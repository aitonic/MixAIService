"""AI Exception Handling Module

This module provides custom exception classes for AI-related error scenarios.
The exceptions are designed to handle specific errors such as timeouts, unauthorized
access, model loading issues, and resource exhaustion, among others. These exceptions
provide a structured and descriptive approach to error handling in AI systems.

Author: ai
Created: 2025-01-19
"""

class AIBaseError(Exception):
    """Base exception class for all AI-related errors."""
    
    def __init__(self, message:str="An AI-related error occurred.") -> None:
        """Initialize the base exception class.

        Args:
            message (str): A description of the error. Defaults to a generic message.

        """
        self.message = message
        super().__init__(self.message)

class DocumentNotFoundError(AIBaseError):
    """Exception for Document Not Found errors."""
    
    def __init__(self, message:str="Document not found.") -> None:
        """Initialize the DocumentNotFoundError exception.

        Args:
            message (str): A description of document not found error. Defaults to a generic error message.

        """
        super().__init__(message)
        
class LLMTimeoutError(AIBaseError):
    """Exception for LLM timeout errors."""
    
    def __init__(self, message:str="LLM API call timed out.") -> None:
        """Initialize the LLMTimeoutError exception.

        Args:
            message (str): A description of the timeout error. Defaults to a generic timeout message.

        """
        super().__init__(message)


class LLMAuthorizationError(AIBaseError):
    """Exception for unauthorized access to LLM API."""
    
    def __init__(self, message:str="Unauthorized access to LLM API.") -> None:
        """Initialize the LLMAuthorizationError exception.

        Args:
            message (str): A description of the authorization error. Defaults to a generic unauthorized access message.

        """
        super().__init__(message)


class LLMAPIError(AIBaseError):
    """Exception for generic LLM API errors."""
    
    def __init__(self, message:str="An error occurred during the LLM API request.") -> None:
        """Initialize the LLMAPIError exception.

        Args:
            message (str): A description of the API error. Defaults to a generic API error message.

        """
        super().__init__(message)


class ModelLoadError(AIBaseError):
    """Exception for errors during model loading."""
    
    def __init__(self, message:str="Failed to load the AI model.") -> None:
        """Initialize the ModelLoadError exception.

        Args:
            message (str): A description of the model loading error. Defaults to a generic loading error message.

        """
        super().__init__(message)


class InvalidInputError(AIBaseError):
    """Exception for invalid input data format or content."""
    
    def __init__(self, message:str="Invalid input data provided.") -> None:
        """Initialize the InvalidInputError exception.

        Args:
            message (str): A description of the invalid input error. Defaults to a generic invalid input message.

        """
        super().__init__(message)


class TokenLimitError(AIBaseError):
    """Exception for token limit exceeded scenarios."""
    
    def __init__(self, message:str="Token limit exceeded for the model.") -> None:
        """Initialize the TokenLimitError exception.

        Args:
            message (str): A description of the token limit exceeded error. Defaults to a generic limit exceeded message.

        """
        super().__init__(message)


class InferenceError(AIBaseError):
    """Exception for errors during model inference."""
    
    def __init__(self, message:str="Error occurred during model inference.") -> None:
        """Initialize the InferenceError exception.

        Args:
            message (str): A description of the inference error. Defaults to a generic inference error message.

        """
        super().__init__(message)


class ResourceExhaustionError(AIBaseError):
    """Exception for resource (GPU/CPU/Memory) exhaustion."""
    
    def __init__(self, message:str="System resources exhausted.") -> None:
        """Initialize the ResourceExhaustionError exception.

        Args:
            message (str): A description of the resource exhaustion error. Defaults to a generic exhaustion message.

        """
        super().__init__(message)


class DataPreprocessingError(AIBaseError):
    """Exception for errors during data preprocessing."""
    
    def __init__(self, message:str="Error in data preprocessing step.") -> None:
        """Initialize the DataPreprocessingError exception.

        Args:
            message (str): A description of the preprocessing error. Defaults to a generic preprocessing error message.

        """
        super().__init__(message)


class ModelConfigError(AIBaseError):
    """Exception for model configuration errors."""
    
    def __init__(self, message:str="Invalid model configuration.") -> None:
        """Initialize the ModelConfigError exception.

        Args:
            message (str): A description of the configuration error. Defaults to a generic configuration error message.

        """
        super().__init__(message)


class CacheError(AIBaseError):
    """Exception for caching-related errors."""
    
    def __init__(self, message:str="Error in caching operation.") -> None:
        """Initialize the CacheError exception.

        Args:
            message (str): A description of the caching error. Defaults to a generic caching error message.

        """
        super().__init__(message)
