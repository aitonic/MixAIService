"""AI Exception Handling and Pandas_AI Custom Exceptions

This module provides a unified implementation of custom exceptions for AI-related and PandasAI scenarios.
The exceptions are designed to handle specific errors such as timeouts, unauthorized
access, model loading issues, resource exhaustion, and more.

Author: ai
Created: 2025-01-19
"""

class AIBaseError(Exception):
    """Base exception class for all AI-related errors."""
    
    def __init__(self, message: str = "An AI-related error occurred.", status_code: int = 500) -> None:
        """Initialize the base exception class.
        
        Args:
            message (str): A description of the error. Defaults to a generic message.
            status_code (int): HTTP status code. Defaults to 500 (Internal Server Error).

        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# ------------------------------------------------------------------------------
# 以下为「代码一」原有的 AI 相关异常
# ------------------------------------------------------------------------------

class DocumentNotFoundError(AIBaseError):
    """Exception for Document Not Found errors."""
    
    def __init__(self, message: str = "Document not found.") -> None:
        super().__init__(message, 404)


class LLMTimeoutError(AIBaseError):
    """Exception for LLM timeout errors."""
    
    def __init__(self, message: str = "LLM API call timed out.") -> None:
        super().__init__(message, 504)


class LLMAuthorizationError(AIBaseError):
    """Exception for unauthorized access to LLM API."""
    
    def __init__(self, message: str = "Unauthorized access to LLM API.") -> None:
        super().__init__(message, 401)


class LLMAPIError(AIBaseError):
    """Exception for generic LLM API errors."""
    
    def __init__(self, message: str = "An error occurred during the LLM API request.") -> None:
        super().__init__(message, 502)


class ModelLoadError(AIBaseError):
    """Exception for errors during model loading."""
    
    def __init__(self, message: str = "Failed to load the AI model.") -> None:
        super().__init__(message, 503)


class InvalidInputError(AIBaseError):
    """Exception for invalid input data format or content."""
    
    def __init__(self, message: str = "Invalid input data provided.") -> None:
        super().__init__(message, 400)


class TokenLimitError(AIBaseError):
    """Exception for token limit exceeded scenarios."""
    
    def __init__(self, message: str = "Token limit exceeded for the model.") -> None:
        super().__init__(message, 429)


class InferenceError(AIBaseError):
    """Exception for errors during model inference."""
    
    def __init__(self, message: str = "Error occurred during model inference.") -> None:
        super().__init__(message, 500)


class ResourceExhaustionError(AIBaseError):
    """Exception for resource (GPU/CPU/Memory) exhaustion."""
    
    def __init__(self, message: str = "System resources exhausted.") -> None:
        super().__init__(message, 507)


class DataPreprocessingError(AIBaseError):
    """Exception for errors during data preprocessing."""
    
    def __init__(self, message: str = "Error in data preprocessing step.") -> None:
        super().__init__(message, 500)


class ModelConfigError(AIBaseError):
    """Exception for model configuration errors."""
    
    def __init__(self, message: str = "Invalid model configuration.") -> None:
        super().__init__(message, 500)


class CacheError(AIBaseError):
    """Exception for caching-related errors."""
    
    def __init__(self, message: str = "Error in caching operation.") -> None:
        super().__init__(message, 500)


class TooManyRequestError(AIBaseError):
    """Exception for too many requests error."""
    
    def __init__(self, message: str = "Too many requests to the server.") -> None:
        super().__init__(message, 429)

# ------------------------------------------------------------------------------
# 以下为从「代码二」合并过来的、原本不在代码一中的异常
# 全部继承自 AIBaseError，并保留各自原有的文档说明
# ------------------------------------------------------------------------------

class InvalidRequestError(AIBaseError):
    """Raised when the request is not successful.
    """

    def __init__(self, message: str = "The request was invalid or not successful.") -> None:
        super().__init__(message, 400)


class APIKeyNotFoundError(AIBaseError):
    """Raised when the API key is not defined/declared.
    """

    def __init__(self, message: str = "API key is missing or not declared.") -> None:
        super().__init__(message, 401)


class LLMNotFoundError(AIBaseError):
    """Raised when the LLM is not provided.
    """

    def __init__(self, message: str = "No LLM provided.") -> None:
        super().__init__(message, 400)


class NoCodeFoundError(AIBaseError):
    """Raised when no code is found in the response.
    """

    def __init__(self, message: str = "No code found in the LLM response.") -> None:
        super().__init__(message, 500)


class NoResultFoundError(AIBaseError):
    """Raised when no result is found in the response.
    """

    def __init__(self, message: str = "No result found in the LLM response.") -> None:
        super().__init__(message, 500)


class MethodNotImplementedError(AIBaseError):
    """Raised when a method is not implemented.
    """

    def __init__(self, message: str = "This method is not yet implemented.") -> None:
        super().__init__(message, 501)


class UnsupportedModelError(AIBaseError):
    """Raised when an unsupported model is used.
    
    Args:
        model_name (str): The name of the unsupported model.

    """

    def __init__(self, model_name: str):
        self.model = model_name
        message = (
            f"Unsupported model: The model '{model_name}' doesn't exist or is not supported yet."
        )
        super().__init__(message, 400)


class MissingModelError(AIBaseError):
    """Raised when deployment name is not passed to azure as it's a required parameter.
    """

    def __init__(self, message: str = "Missing deployment name for Azure model.") -> None:
        super().__init__(message, 400)


class LLMResponseHTTPError(AIBaseError):
    """Raised when a remote LLM service responds with an error HTTP code.
    
    Args:
        status_code (int): The HTTP status code.
        error_msg (str): Additional error message from the remote service.

    """

    def __init__(self, status_code: int, error_msg: str = None):
        self.remote_status_code = status_code
        msg = f"The remote server responded with error HTTP code: {status_code}; {error_msg or ''}"
        super().__init__(msg, status_code)


class BadImportError(AIBaseError):
    """Raised when a library not in the whitelist is imported.
    
    Args:
        library_name (str): Name of the library that is not in the whitelist.

    """

    def __init__(self, library_name: str):
        self.library_name = library_name
        message = (
            f"Generated code includes import of '{library_name}', which is not in the whitelist."
        )
        super().__init__(message, 403)


class TemplateFileNotFoundError(AIBaseError):
    """Raised when a template file cannot be found.
    
    Args:
        template_path (str): Path for template file.
        prompt_name (str): Prompt name. Defaults to "Unknown".

    """

    def __init__(self, template_path: str, prompt_name: str = "Unknown"):
        self.template_path = template_path
        message = (
            f"Unable to find a file with template at '{template_path}' for '{prompt_name}' prompt."
        )
        super().__init__(message, 404)


class UnSupportedLogicUnit(AIBaseError):
    """Raised when an unsupported logic unit is added in the pipeline.
    """

    def __init__(self, message: str = "Unsupported logic unit used in the pipeline.") -> None:
        super().__init__(message, 400)


class InvalidWorkspacePathError(AIBaseError):
    """Raised when the environment variable of workspace exists but the path is invalid.
    """

    def __init__(self, message: str = "Invalid workspace path.") -> None:
        super().__init__(message, 400)


class InvalidConfigError(AIBaseError):
    """Raised when a config value is not applicable.
    """

    def __init__(self, message: str = "Invalid configuration value.") -> None:
        super().__init__(message, 400)


class MaliciousQueryError(AIBaseError):
    """Raised if a malicious query is generated.
    """

    def __init__(self, message: str = "A malicious query has been detected.") -> None:
        super().__init__(message, 403)


class InvalidLLMOutputType(AIBaseError):
    """Raised if the output type from the LLM is invalid.
    """

    def __init__(self, message: str = "Invalid LLM output type.") -> None:
        super().__init__(message, 400)


class InvalidOutputValueMismatch(AIBaseError):
    """Raised if the output value doesn't match the expected type.
    """

    def __init__(self, message: str = "Mismatch between expected and actual output value type.") -> None:
        super().__init__(message, 400)


class ExecuteSQLQueryNotUsed(AIBaseError):
    """Raised if Execute SQL Query is not used where it is required.
    """

    def __init__(self, message: str = "ExecuteSQLQuery not called but is required in this context.") -> None:
        super().__init__(message, 500)


class PipelineConcatenationError(AIBaseError):
    """Raised if concatenating incompatible pipelines.
    """

    def __init__(self, message: str = "Error concatenating pipelines: incompatible pipeline steps.") -> None:
        super().__init__(message, 500)


class MissingVectorStoreError(AIBaseError):
    """Raised if vector store is not found.
    """

    def __init__(self, message: str = "Missing vector store in pipeline.") -> None:
        super().__init__(message, 500)


# 如果用到了 PANDASBI_SETUP_MESSAGE，请取消注释并导入
# class PandasAIApiKeyError(AIBaseError):
#     """
#     Raised if api key is not found for remote vector store or LLM.
#     """
#     def __init__(self):
#         message = PANDASBI_SETUP_MESSAGE
#         super().__init__(message, 401)

class PandasAIApiKeyError(AIBaseError):
    """Raised if api key is not found for remote vector store and LLM.
    """

    def __init__(self, message: str = "API key not found for remote vector store or LLM.") -> None:
        super().__init__(message, 401)


class PandasAIApiCallError(AIBaseError):
    """Raised if there's an exception in an API request.
    """

    def __init__(self, message: str = "PandasAI API call failed.") -> None:
        super().__init__(message, 500)


class PandasConnectorTableNotFound(AIBaseError):
    """Raised if a requested table is not found.
    """

    def __init__(self, message: str = "Pandas Connector table not found.") -> None:
        super().__init__(message, 404)


class InvalidTrainJson(AIBaseError):
    """Raised if the training JSON is malformed or invalid.
    """

    def __init__(self, message: str = "Invalid train JSON.") -> None:
        super().__init__(message, 400)


class InvalidSchemaJson(AIBaseError):
    """Raised if the schema JSON is not correct.
    """

    def __init__(self, message: str = "Invalid schema JSON.") -> None:
        super().__init__(message, 400)
