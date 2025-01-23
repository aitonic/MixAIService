"""
Pipeline Module

This module defines the main components and structures for creating and managing
pipelines. It provides abstractions for pipelines, logic units, and pipeline contexts,
as well as a factory for creating pipeline instances.

Classes:
    Pipeline: Represents the core pipeline structure.
    AbstractPipeline: Abstract base class for pipelines.
    BaseLogicUnit: Base class for individual logic units within a pipeline.
    PipelineContext: Represents the context in which a pipeline operates.
    PipelineFactory: Factory class for creating pipeline instances.

Author: ai
Created: 2025-01-19
"""

from .core.pipeline import Pipeline
from .core.abstract_pipeline import AbstractPipeline
from .core.base_logic_unit import BaseLogicUnit
from .core.pipeline_context import PipelineContext
from .pipeline_factory import PipelineFactory  # Import PipelineFactory

# Expose components for external usage
__all__ = [
    "Pipeline",
    "AbstractPipeline",
    "BaseLogicUnit",
    "PipelineContext",
    "PipelineFactory",  # Include PipelineFactory in the public API
]