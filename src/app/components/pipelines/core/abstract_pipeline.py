# app/model_components/pipelines/core/abstract_pipeline.py
from abc import ABC, abstractmethod


class AbstractPipeline(ABC):
    """Abstract base class for all pipelines"""
    
    @abstractmethod
    def run(self, input_data):
        """Run the pipeline with given input"""
        pass
