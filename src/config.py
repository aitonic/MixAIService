import json

from src.utils.helpers.path import find_closest
from src.utils.llm import LLM, OpenAI
from src.utils.logger import Logger
from src.utils.schemas.df_config import Config


def load_config_from_json(
    override_config: Config | dict | None = None,
):
    """Load the configuration from the pandas_ai.json file.

    Args:
        override_config (Optional[Union[Config, dict]], optional): The configuration to
        override the one in the file. Defaults to None.

    Returns:
        dict: The configuration.

    """
    config = {}

    if override_config is None:
        override_config = {"llm": OpenAI()}

    Logger.log(f"override_config: {override_config}")
    
    
    if isinstance(override_config, Config):
        override_config = override_config.model_dump()
        

    try:
        with open(find_closest("pandas_ai.json")) as f:
            config = json.load(f)

            if not config.get("llm") and not override_config.get("llm"):
                config["llm"] = LLM()

    except FileNotFoundError:
        # Ignore the error if the file does not exist, will use the default config
        pass

    if override_config:
        config.update(override_config)

    return config
