"""
Prompt Factory Module

This module provides a factory for creating various types of prompt components.
It includes functionality to dynamically register new prompt types and manage prompt creation.

Classes:
    PromptFactory: Factory class for creating and managing different types of prompts.

Author: ai
Created: 2025-01-19
"""

from typing import Dict, Type
from ..base_component import (
    BaseComponent, 
    BaseFactory
)
from .prompt import (
    HumanPrompt, 
    SystemPrompt
)


class PromptFactory(BaseFactory):
    """Factory class for creating different types of prompts."""
    
    # Class-level dictionary to store prompt type mappings
    _prompt_types: Dict[str, Type[BaseComponent]] = {
        "system": SystemPrompt,
        "human": HumanPrompt
    }

    def get_bean(self, param: dict) -> BaseComponent:
        """
        Create and return a prompt component based on the given parameters.

        Args:
            param (dict): Dictionary containing component configuration.
                Must include 'component_type' and corresponding prompt parameter.

        Returns:
            BaseComponent: An instance of the requested prompt component.

        Raises:
            KeyError: If `component_type` is not registered.
            ValueError: If required parameters are missing.
        """
        component_type = param["component_type"]
        
        try:
            # Get the appropriate class for the specified component type
            prompt_class = self._prompt_types[component_type]
            
            # Extract the corresponding prompt parameter based on the component type
            prompt_param = param.get(f"{component_type}_prompt") or param.get(f"{component_type}_message")
            
            if prompt_param is None:
                raise ValueError(f"Missing required parameter for {component_type} prompt")
                
            return prompt_class(prompt_param)
            
        except KeyError:
            raise ValueError(f"Unimplemented prompt component_type: {component_type}")

    @classmethod
    def register_prompt_type(cls, type_name: str, prompt_class: Type[BaseComponent]) -> None:
        """
        Register a new prompt type to the factory.

        Args:
            type_name (str): The identifier for the prompt type.
            prompt_class (Type[BaseComponent]): The class to instantiate for this type.
        """
        cls._prompt_types[type_name] = prompt_class