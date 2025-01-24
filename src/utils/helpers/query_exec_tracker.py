import base64
import json
import os
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Any, TypedDict, Union

import requests

from src.__version__ import __version__
from src.app.components.connectors import BaseConnector
from src.app.components.pipelines.core.pipeline_context import PipelineContext
from src.utils.helpers.encoder import CustomEncoder

if TYPE_CHECKING:
    from src.app.components.pipelines.chat.chat_pipeline_input import (
        ChatPipelineInput,
        CodeExecutionPipelineInput,
    )


class ResponseType(TypedDict):
    type: str
    value: Any


exec_steps = {
    "cache_hit": "Cache Hit",
    "get_prompt": "Generate Prompt",
    "generate_code": "Generate Code",
    "execute_code": "Code Execution",
    "retry_run_code": "Retry Code Generation",
    "parse": "Parse Output",
}


class QueryExecTracker:
    _query_info: dict
    _dataframes: list
    _skills: list
    _response: ResponseType
    _steps: list
    _func_exec_count: dict
    _success: bool
    _server_config: dict
    _last_log_id: int

    def __init__(
        self,
        server_config: dict | None = None,
    ) -> None:
        self._success = False
        self._start_time = None
        self._last_log_id = None
        self._server_config = server_config
        self._query_info = {}

    def start_new_track(self, input: 'ChatPipelineInput'):
        """Resets tracking variables to start new track
        """
        self._last_log_id = None
        self._start_time = time.time()
        self._dataframes: list = []
        self._skills: list = []
        self._response: ResponseType = {}
        self._steps: list = []
        self._query_info = {}
        self._func_exec_count: dict = defaultdict(int)

        self._query_info = {
            "conversation_id": str(input.conversation_id),
            "instance": "Agent",
            "query": input.query,
            "output_type": input.output_type,
            "pandasai_version": __version__,
        }

    def convert_dataframe_to_dict(self, df):
        json_data = json.loads(
            df.to_json(
                orient="split",
                date_format="iso",
                default_handler=str,
                force_ascii=False,
            )
        )
        return {"headers": json_data["columns"], "rows": json_data["data"]}

    def add_dataframes(self, dfs: list[BaseConnector]) -> None:
        """Add used dataframes for the query to query exec tracker
        Args:
            dfs (List[BaseConnector]): List of dataframes
        """
        for df in dfs:
            head = df.get_schema()
            self._dataframes.append(self.convert_dataframe_to_dict(head))

    def add_skills(self, context: PipelineContext):
        self._skills = context.skills_manager.to_object()

    def add_step(self, step: dict) -> None:
        """Add Custom Step that is performed for additional information
        Args:
            step (dict): dictionary containing information
        """
        if "_steps" not in self.__dict__:
            self._steps = []

        self._steps.append(step)

    def set_final_response(self, response: Any):
        self._response = response

    def execute_func(self, function, *args, **kwargs) -> Any:
        """Tracks function executions, calculates execution time and prepare data
        Args:
            function (function): Function that is to be executed

        Returns:
            Any: Response return after function execution

        """
        start_time = time.time()

        # Get the tag from kwargs if provided, or use the function name as the default
        tag = kwargs.pop("tag", function.__name__)

        try:
            result = function(*args, **kwargs)

            execution_time = time.time() - start_time
            if tag not in exec_steps:
                return result

            step_data = self._generate_exec_step(tag, result)

            step_data["success"] = True
            step_data["execution_time"] = execution_time

            self._steps.append(step_data)

            return result

        except Exception:
            execution_time = time.time() - start_time
            self._steps.append(
                {
                    "type": exec_steps[tag],
                    "success": False,
                    "execution_time": execution_time,
                }
            )
            raise

    def _generate_exec_step(self, func_name: str, result: Any) -> dict:
        """Extracts and Generates result
        Args:
            func_name (str): function name that is executed
            result (Any): function output response

        Returns:
            dict: dictionary with information about the function execution

        """
        step = {"type": exec_steps[func_name]}

        if func_name == "get_prompt":
            step["prompt_class"] = result.__class__.__name__
            step["generated_prompt"] = result.to_string()

        elif func_name == "retry_run_code":
            self._func_exec_count["retry_run_code"] += 1

            step[
                "type"
            ] = f"{exec_steps[func_name]} ({self._func_exec_count['retry_run_code']})"
            step["code_generated"] = result

        elif func_name in {"cache_hit", "generate_code"}:
            step["code_generated"] = result

        elif func_name == "execute_code":
            self._response = self._format_response(result)
            step["result"] = self._response

        return step

    def _format_response(self, result: ResponseType) -> ResponseType:
        """Format output response
        Args:
            result (ResponseType): response returned after execution

        Returns:
            ResponseType: formatted response output

        """
        if result["type"] == "dataframe":
            df_dict = self.convert_dataframe_to_dict(result["value"])
            return {"type": result["type"], "value": df_dict}

        elif result["type"] == "plot":
            with open(result["value"], "rb") as image_file:
                image_data = image_file.read()
            # Encode the image data to Base64
            base64_image = (
                f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
            )
            return {
                "type": result["type"],
                "value": base64_image,
            }
        else:
            return result

    def get_summary(self) -> dict:
        """Returns the summary in json to steps involved in execution of track
        Returns:
            dict: summary json
        """
        if self._start_time is None:
            raise RuntimeError("[QueryExecTracker]: Tracking not started")

        execution_time = time.time() - self._start_time
        return {
            "query_info": self._query_info,
            "skills": self._skills,
            "dataframes": self._dataframes,
            "steps": self._steps,
            "response": self._response,
            "execution_time": execution_time,
            "success": self._success,
        }

    def get_execution_time(self) -> float:
        return time.time() - self._start_time

    def publish(self) -> None:
        """Publish Query Summary to remote logging server
        """
        api_key = None
        server_url = None

        if self._server_config is None:
            server_url = os.environ.get("PANDASAI_API_URL", "https://api.domer.ai")
            api_key = os.environ.get("PANDASAI_API_KEY") or None
        else:
            server_url = self._server_config.get(
                "server_url", os.environ.get("PANDASAI_API_URL", "https://api.domer.ai")
            )
            api_key = self._server_config.get(
                "api_key", os.environ.get("PANDASAI_API_KEY")
            )

        if api_key is None:
            return

        try:
            log_data = {
                "json_log": self.get_summary(),
            }

            encoder = CustomEncoder()
            ecoded_json_str = encoder.encode(log_data)

            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.post(
                f"{server_url}/api/log/add",
                json=json.loads(ecoded_json_str),
                headers=headers,
            )
            if response.status_code != 200:
                raise Exception(response.text)

            json_data = json.loads(response.text)

            if "data" in json_data and json_data["data"] is not None:
                self._last_log_id = json_data["data"]["log_id"]

        except Exception as e:
            print(f"Exception in APILogger: {e}")

    @property
    def success(self) -> bool:
        return self._success

    @success.setter
    def success(self, value: bool):
        self._success = value

    @property
    def last_log_id(self) -> int:
        return self._last_log_id

    def track_execution(
        self,
        input_data: Union['ChatPipelineInput', 'CodeExecutionPipelineInput'],
    ):
        # implementation
        pass
