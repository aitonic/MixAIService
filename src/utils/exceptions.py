"""AI Exception Handling and PandasAI Custom Exceptions

This module provides a unified implementation of custom exceptions for AI-related and PandasAI scenarios. 
The exceptions are designed to handle specific errors such as timeouts, unauthorized
access, model loading issues, resource exhaustion, and more.

Author: ai
Created: 2025-01-19
"""

class AIBaseError(Exception):
    """Base exception class for all AI-related errors."""
    
    def __init__(self, message: str = "An AI-related error occurred.") -> None:
        self.message = message
        super().__init__(self.message)

# AI-specific exceptions
class DocumentNotFoundError(AIBaseError):
    def __init__(self, message: str = "Document not found.") -> None:
        super().__init__(message)

class LLMTimeoutError(AIBaseError):
    def __init__(self, message: str = "LLM API call timed out.") -> None:
        super().__init__(message)

class LLMAuthorizationError(AIBaseError):
    def __init__(self, message: str = "Unauthorized access to LLM API.") -> None:
        super().__init__(message)

class LLMAPIError(AIBaseError):
    def __init__(self, message: str = "An error occurred during the LLM API request.") -> None:
        super().__init__(message)

class ModelLoadError(AIBaseError):
    def __init__(self, message: str = "Failed to load the AI model.") -> None:
        super().__init__(message)

class InvalidInputError(AIBaseError):
    def __init__(self, message: str = "Invalid input data provided.") -> None:
        super().__init__(message)

class TokenLimitError(AIBaseError):
    def __init__(self, message: str = "Token limit exceeded for the model.") -> None:
        super().__init__(message)

class InferenceError(AIBaseError):
    def __init__(self, message: str = "Error occurred during model inference.") -> None:
        super().__init__(message)

class ResourceExhaustionError(AIBaseError):
    def __init__(self, message: str = "System resources exhausted.") -> None:
        super().__init__(message)

class DataPreprocessingError(AIBaseError):
    def __init__(self, message: str = "Error in data preprocessing step.") -> None:
        super().__init__(message)

class ModelConfigError(AIBaseError):
    def __init__(self, message: str = "Invalid model configuration.") -> None:
        super().__init__(message)

class CacheError(AIBaseError):
    def __init__(self, message: str = "Error in caching operation.") -> None:
        super().__init__(message)

# Pandas-specific exceptions
class InvalidRequestError(Exception):
    """Raised when the request is not successful."""
    pass

class APIKeyNotFoundError(Exception):
    """Raised when the API key is not defined/declared."""
    pass

class LLMNotFoundError(Exception):
    """Raised when the LLM is not provided."""
    pass

class NoCodeFoundError(Exception):
    """Raised when no code is found in the response."""
    pass

class NoResultFoundError(Exception):
    """Raised when no result is found in the response."""
    pass

class MethodNotImplementedError(Exception):
    """Raised when a method is not implemented."""
    pass

class UnsupportedModelError(Exception):
    """Raised when an unsupported model is used."""
    
    def __init__(self, model_name):
        self.model = model_name
        super().__init__(
            f"Unsupported model: The model '{model_name}' doesn't exist or is not supported yet."
        )

class MissingModelError(Exception):
    """Raised when deployment name is not passed to azure as it's a required parameter."""
    pass

class LLMResponseHTTPError(Exception):
    """Raised when a remote LLM service responses with error HTTP code."""
    
    def __init__(self, status_code, error_msg=None):
        self.status_code = status_code
        self.error_msg = error_msg
        super().__init__(
            f"The remote server has responded with an error HTTP code: {status_code}; {error_msg or ''}"
        )

class BadImportError(Exception):
    """Raised when a library not in the whitelist is imported."""
    
    def __init__(self, library_name):
        self.library_name = library_name
        super().__init__(
            f"Generated code includes import of {library_name} which is not in whitelist."
        )

class TemplateFileNotFoundError(FileNotFoundError):
    """Raised when a template file cannot be found."""
    
    def __init__(self, template_path, prompt_name="Unknown"):
        self.template_path = template_path
        super().__init__(
            f"Unable to find a file with template at '{template_path}' for '{prompt_name}' prompt."
        )

class UnSupportedLogicUnit(Exception):
    """Raised when unsupported logic unit is added in the pipeline."""
    pass

class InvalidWorkspacePathError(Exception):
    """Raised when the environment variable of workspace exists but path is invalid."""
    pass

class InvalidConfigError(Exception):
    """Raised when config value is not applicable."""
    pass

class MaliciousQueryError(Exception):
    """Raise error if malicious query is generated."""
    pass

class InvalidLLMOutputType(Exception):
    """Raise error if the output type is invalid."""
    pass

class InvalidOutputValueMismatch(Exception):
    """Raise error if the output value doesn't match with type."""
    pass

class ExecuteSQLQueryNotUsed(Exception):
    """Raise error if Execute SQL Query is not used."""
    pass

class PipelineConcatenationError(Exception):
    """Raise error if concatenating wrong pipelines."""
    pass

class MissingVectorStoreError(Exception):
    """Raise error if vector store is not found."""
    pass

class PandasAIApiKeyError(Exception):
    """Raise error if API key is not found for remote vector store and LLM."""
    pass

class PandasAIApiCallError(Exception):
    """Raise error if exception in API request fails."""
    pass

class PandasConnectorTableNotFound(Exception):
    """Raise error if the table is not found in the connector."""
    pass

class InvalidTrainJson(Exception):
    """Raise error if the train JSON is not correct."""
    pass

class InvalidSchemaJson(Exception):
    """Raise error if the schema JSON is not correct."""
    pass
