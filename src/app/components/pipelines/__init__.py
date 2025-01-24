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

from src.app.components.pipelines.core.pipeline import Pipeline
from src.app.components.pipelines.core.abstract_pipeline import AbstractPipeline
from src.app.components.pipelines.core.base_logic_unit import BaseLogicUnit
from src.app.components.pipelines.core.pipeline_context import PipelineContext
from src.app.components.pipelines.pipeline_factory import PipelineFactory  # Import PipelineFactory

# Expose components for external usage
__all__ = [
    "Pipeline",
    "AbstractPipeline",
    "BaseLogicUnit",
    "PipelineContext",
    "PipelineFactory",  # Include PipelineFactory in the public API
]