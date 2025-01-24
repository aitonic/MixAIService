import json
import os
import re
import uuid

import src.utils.pandas as pd
from src.app.agent.base_security import BaseSecurity
from src.app.components.connectors.base import BaseConnector
from src.app.components.connectors.pandas import PandasConnector
from src.app.components.pipelines.chat.chat_pipeline_input import ChatPipelineInput
from src.app.components.pipelines.chat.code_execution_pipeline_input import (
    CodeExecutionPipelineInput,
)

# from ..llm.langchain import LangchainLLM, is_langchain_llm
from src.app.components.pipelines.core.pipeline_context import PipelineContext
from src.app.components.prompts.base import BasePrompt
from src.app.components.prompts.clarification_questions_prompt import (
    ClarificationQuestionPrompt,
)
from src.app.components.prompts.explain_prompt import ExplainPrompt
from src.app.components.prompts.rephase_query_prompt import RephraseQueryPrompt
from src.app.components.skills import Skill
from src.app.components.vectorstores.vectorstore import VectorStore
from src.config import load_config_from_json
from src.constants import DEFAULT_CACHE_DIRECTORY, DEFAULT_CHART_DIRECTORY
from src.utils.exceptions import (
    InvalidLLMOutputType,
    MaliciousQueryError,
    MissingVectorStoreError,
)
from src.utils.helpers.df_info import df_type
from src.utils.helpers.folder import Folder
from src.utils.helpers.memory import Memory
from src.utils.llm.base import LLM
from src.utils.logger import Logger
from src.utils.schemas.df_config import Config

from .callbacks import Callbacks


class BaseAgent:
    """Base Agent class to improve the conversational experience in PandasAI
    """

    def __init__(
        self,
        dfs: pd.DataFrame | BaseConnector | list[pd.DataFrame | BaseConnector],
        config: Config | dict | None = None,
        memory_size: int | None = 10,
        vectorstore: VectorStore | None = None,
        description: str = None,
        security: BaseSecurity = None,
    ):
        """Args:
        df (Union[pd.DataFrame, List[pd.DataFrame]]): Pandas or Modin dataframe
        Polars or Database connectors
        memory_size (int, optional): Conversation history to use during chat.
        Defaults to 1.

        """
        self.last_prompt = None
        self.last_prompt_id = None
        self.last_result = None
        self.last_code_generated = None
        self.last_code_executed = None
        self.agent_info = description

        self.conversation_id = uuid.uuid4()

        self.dfs = self.get_dfs(dfs)

        # Instantiate the context
        self.config = self.get_config(config)
        self.context = PipelineContext(
            dfs=self.dfs,
            config=self.config,
            memory=Memory(memory_size, agent_info=description),
            vectorstore=vectorstore,
        )

        # Instantiate the logger
        self.logger = Logger()

        # Instantiate the vectorstore
        self._vectorstore = vectorstore

        if self._vectorstore is None and os.environ.get("PANDASAI_API_KEY"):
            try:
                from src.app.components.vectorstores.bamboo_vectorstore import (
                    BambooVectorStore,
                )
            except ImportError as e:
                raise ImportError(
                    "Could not import BambooVectorStore. Please install the required dependencies."
                ) from e

            self._vectorstore = BambooVectorStore(logger=self.logger)
            self.context.vectorstore = self._vectorstore

        self._callbacks = Callbacks(self)

        self.pipeline = None
        self.security = security

    def configure(self):
        # Add project root path if save_charts_path is default
        if (
            self.config.save_charts
            and self.config.save_charts_path == DEFAULT_CHART_DIRECTORY
        ):
            Folder.create(self.config.save_charts_path)

        # Add project root path if cache_path is default
        if self.config.enable_cache:
            Folder.create(DEFAULT_CACHE_DIRECTORY)

    def get_config(self, config: Config | dict):
        """Load a config to be used to run the queries.
        """
        # 如果已经是 Config 实例，直接返回
        if isinstance(config, Config):
            return config

        # 如果是 None，创建一个新的配置
        if config is None:
            config = {}
        
        # 如果是 LLM 实例，转换为配置字典
        if isinstance(config, LLM):
            config = {"llm": config}

        # 确保 config 是一个字典类型
        if not isinstance(config, dict):
            raise TypeError("config 参数必须是一个 dict 类型")

        config = load_config_from_json(config)

        if isinstance(config, dict) and config.get("llm") is not None:
            config["llm"] = self.get_llm(config["llm"])

        return Config(**config)

    def get_llm(self, llm: LLM) -> LLM:
        """Load a LLM to be used to run the queries.
        Check if it is a PandasAI LLM or a Langchain LLM.
        If it is a Langchain LLM, wrap it in a PandasAI LLM.

        Args:
            llm (object): LLMs option to be used for API access

        Raises:
            BadImportError: If the LLM is a Langchain LLM but the langchain package
            is not installed

        """
        # if is_langchain_llm(llm):
        #     llm = LangchainLLM(llm)

        return llm

    def get_dfs(
        self,
        dfs: pd.DataFrame | BaseConnector | list[pd.DataFrame | BaseConnector],
    ):
        """Load all the dataframes to be used in the agent.

        Args:
            dfs (List[Union[pd.DataFrame, Any]]): Pandas dataframe

        """
        # Inline import to avoid circular import
        from src.utils.smart_dataframe import SmartDataframe

        # If only one dataframe is passed, convert it to a list
        if not isinstance(dfs, list):
            dfs = [dfs]

        connectors = []
        for df in dfs:
            if isinstance(df, BaseConnector):
                connectors.append(df)
            elif isinstance(df, (pd.DataFrame, pd.Series, list, dict, str)) or df_type(df) == "modin":
                connectors.append(PandasConnector({
                    "original_df": df,
                    "database": "pandas",  # 添加必需字段
                    "table": "df"          # 添加必需字段
                }))
            elif isinstance(df, SmartDataframe) and isinstance(
                df.dataframe, BaseConnector
            ):
                connectors.append(df.dataframe)
            else:
                try:
                    import polars as pl

                    if isinstance(df, pl.DataFrame):
                        from src.app.components.connectors.polars import PolarsConnector

                        connectors.append(PolarsConnector({"original_df": df}))

                    else:
                        raise ValueError(
                            "Invalid input data. We cannot convert it to a dataframe."
                        )
                except ImportError as e:
                    raise ValueError(
                        "Invalid input data. We cannot convert it to a dataframe."
                    ) from e
        return connectors

    def add_skills(self, *skills: Skill):
        """Add Skills to PandasAI
        """
        self.context.skills_manager.add_skills(*skills)

    def call_llm_with_prompt(self, prompt: BasePrompt):
        """Call LLM with prompt using error handling to retry based on config
        Args:
            prompt (BasePrompt): BasePrompt to pass to LLM's
        """
        retry_count = 0
        while retry_count < self.context.config.max_retries:
            try:
                result: str = self.context.config.llm.call(prompt)
                if prompt.validate(result):
                    return result
                else:
                    raise InvalidLLMOutputType("Response validation failed!")
            except Exception:
                if (
                    not self.context.config.use_error_correction_framework
                    or retry_count >= self.context.config.max_retries - 1
                ):
                    raise
                retry_count += 1

    def check_malicious_keywords_in_query(self, query):
        dangerous_pattern = re.compile(
            r"\b(os|io|chr|b64decode)\b|"
            r"(\.os|\.io|'os'|'io'|\"os\"|\"io\"|chr\(|chr\)|chr |\(chr)"
        )
        return bool(dangerous_pattern.search(query))

    def chat(self, query: str, output_type: str | None = None):
        """Simulate a chat interaction with the assistant on Dataframe.
        """
        if not self.pipeline:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error: No pipeline exists"
            )

        try:

            self.logger.log(
                f"Running Pandas_AI with {self.context.config.llm} LLM..."
            )

            self.assign_prompt_id()

            if self.config.security in [
                "standard",
                "advanced",
            ] and self.check_malicious_keywords_in_query(query):
                raise MaliciousQueryError(
                    "The query contains references to io or os modules or b64decode method which can be used to execute or access system resources in unsafe ways."
                )

            if self.security and self.security.evaluate(query):
                raise MaliciousQueryError("Query can result in a malicious code")

            pipeline_input = ChatPipelineInput(
                query, output_type, self.conversation_id, self.last_prompt_id
            )

            
            return self.pipeline.run(pipeline_input)

        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def generate_code(self, query: str, output_type: str | None = None):
        """Simulate code generation with the assistant on Dataframe.
        """
        if not self.pipeline:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error: No pipeline exists"
            )
        try:
            self.logger.log(f"Question: {query}")
            self.logger.log(
                f"Running PandasAI with {self.context.config.llm.type} LLM..."
            )

            self.assign_prompt_id()

            pipeline_input = ChatPipelineInput(
                query, output_type, self.conversation_id, self.last_prompt_id
            )

            return self.pipeline.run_generate_code(pipeline_input)
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def execute_code(
        self, code: str | None = None, output_type: str | None = None
    ):
        """Execute code Generated with the assistant on Dataframe.
        """
        if not self.pipeline:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error: No pipeline exists to execute try Agent class"
            )
        try:
            if code is None:
                code = self.last_code_generated
            self.logger.log(f"Code: {code}")
            self.logger.log(
                f"Running PandasAI with {self.context.config.llm.type} LLM..."
            )

            self.assign_prompt_id()

            pipeline_input = CodeExecutionPipelineInput(
                code, output_type, self.conversation_id, self.last_prompt_id
            )

            return self.pipeline.run_execute_code(pipeline_input)
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def train(
        self,
        queries: list[str] | None = None,
        codes: list[str] | None = None,
        docs: list[str] | None = None,
    ) -> None:
        """Trains the context to be passed to model
        Args:
            queries (Optional[str], optional): user user
            codes (Optional[str], optional): generated code
            docs (Optional[List[str]], optional): additional docs
        Raises:
            ImportError: if default vector db lib is not installed it raises an error
        """
        if self._vectorstore is None:
            raise MissingVectorStoreError(
                "No vector store provided. Please provide a vector store to train the agent."
            )

        if (queries and not codes) or (not queries and codes):
            raise ValueError(
                "If either queries or codes are provided, both must be provided."
            )

        if docs is not None:
            self._vectorstore.add_docs(docs)

        if queries and codes:
            self._vectorstore.add_question_answer(queries, codes)

        self.logger.log("Agent successfully trained on the data")

    def clear_memory(self):
        """Clears the memory
        """
        self.context.memory.clear()
        self.conversation_id = uuid.uuid4()

    def add_message(self, message, is_user=False):
        """Add message to the memory. This is useful when you want to add a message
        to the memory without calling the chat function (for example, when you
        need to add a message from the agent).
        """
        self.context.memory.add(message, is_user=is_user)

    def assign_prompt_id(self):
        """Assign a prompt ID"""
        self.last_prompt_id = uuid.uuid4()

        if self.logger:
            self.logger.log(f"Prompt ID: {self.last_prompt_id}")

    def clarification_questions(self, query: str) -> list[str]:
        """Generate clarification questions based on the data
        """
        prompt = ClarificationQuestionPrompt(
            context=self.context,
            query=query,
        )

        result = self.call_llm_with_prompt(prompt)
        self.logger.log(
            f"""Clarification Questions:  {result}
            """
        )
        result = result.replace("```json", "").replace("```", "")
        questions: list[str] = json.loads(result)
        return questions[:3]

    def start_new_conversation(self):
        """Clears the previous conversation
        """
        self.clear_memory()

    def explain(self) -> str:
        """Returns the explanation of the code how it reached to the solution
        """
        try:
            prompt = ExplainPrompt(
                context=self.context,
                code=self.last_code_executed,
            )
            response = self.call_llm_with_prompt(prompt)
            self.logger.log(
                f"""Explanation:  {response}
                """
            )
            return response
        except Exception as exception:
            return (
                "Unfortunately, I was not able to explain, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def rephrase_query(self, query: str):
        try:
            prompt = RephraseQueryPrompt(
                context=self.context,
                query=query,
            )
            response = self.call_llm_with_prompt(prompt)
            self.logger.log(
                f"""Rephrased Response:  {response}
                """
            )
            return response
        except Exception as exception:
            return (
                "Unfortunately, I was not able to rephrase query, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    @property
    def logs(self):
        return self.logger.logs

    @property
    def last_error(self):
        raise NotImplementedError

    @property
    def last_query_log_id(self):
        raise NotImplementedError
