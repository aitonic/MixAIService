"""
Performance test suite for document splitter components.

Created by: ai
Created at: 2025-01-11 14:33:06 UTC
"""

import unittest
import time
import cProfile
import pstats
from io import StringIO
from typing import Any, Callable

from src.app.model_components.doc_split.doc_split_factory import DocSplitterFactory, SplitterType
from src.app.model_components.doc_split.dto import SplitParameter, SplitStrategy


class DocSplitterPerformanceTest(unittest.TestCase):
    """Performance tests for document splitters."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test fixtures for all performance tests."""
        cls.format_splitter = DocSplitterFactory.create_splitter(SplitterType.FORMAT)
        cls.semantic_splitter = DocSplitterFactory.create_splitter(
            SplitterType.SEMANTIC,
            embedding_model=None  # Use mock or lightweight model for performance testing
        )
        
        # Generate test data of different sizes
        cls.small_text = "Short sentence. " * 10
        cls.medium_text = "Medium length sentence for testing. " * 100
        cls.large_text = "Longer sentence for performance testing. " * 1000

    def measure_execution_time(self, func: Callable, *args: Any) -> float:
        """Measure execution time of a function.
        
        Args:
            func: Function to measure
            *args: Arguments to pass to the function
            
        Returns:
            float: Execution time in seconds
        """
        start_time = time.time()
        func(*args)
        end_time = time.time()
        return end_time - start_time

    def profile_function(self, func: Callable, *args: Any) -> str:
        """Profile a function and return statistics.
        
        Args:
            func: Function to profile
            *args: Arguments to pass to the function
            
        Returns:
            str: Profiling statistics
        """
        profiler = cProfile.Profile()
        profiler.enable()
        func(*args)
        profiler.disable()
        
        stats = pstats.Stats(profiler, stream=StringIO())
        stats.sort_stats('cumulative')
        
        output = StringIO()
        stats.stream = output
        stats.print_stats()
        return output.getvalue()

    def test_format_splitter_performance(self) -> None:
        """Test performance of format splitter with different input sizes."""
        parameter = SplitParameter(
            text=self.medium_text,
            strategy=SplitStrategy.FORMAT,
            min_length=5,
            max_length=100
        )
        
        execution_time = self.measure_execution_time(
            self.format_splitter.split,
            parameter
        )
        
        self.assertLess(
            execution_time,
            1.0,  # Expected maximum execution time in seconds
            "Format splitter took too long to process medium text"
        )

    def test_semantic_splitter_performance(self) -> None:
        """Test performance of semantic splitter with different input sizes."""
        parameter = SplitParameter(
            text=self.medium_text,
            strategy=SplitStrategy.SEMANTIC,
            min_length=5,
            max_length=100
        )
        
        execution_time = self.measure_execution_time(
            self.semantic_splitter.split,
            parameter
        )
        
        self.assertLess(
            execution_time,
            2.0,  # Expected maximum execution time in seconds
            "Semantic splitter took too long to process medium text"
        )

    def test_memory_usage(self) -> None:
        """Test memory usage of splitters with large input."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process large text
        parameter = SplitParameter(
            text=self.large_text,
            strategy=SplitStrategy.FORMAT,
            min_length=5,
            max_length=100
        )
        
        self.format_splitter.split(parameter)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        self.assertLess(
            memory_increase,
            100,  # Maximum allowed memory increase in MB
            "Memory usage exceeded threshold"
        )

    def test_profiling(self) -> None:
        """Profile both splitters and compare performance."""
        parameter = SplitParameter(
            text=self.small_text,
            strategy=SplitStrategy.FORMAT,
            min_length=5,
            max_length=100
        )
        
        format_stats = self.profile_function(
            self.format_splitter.split,
            parameter
        )
        
        semantic_stats = self.profile_function(
            self.semantic_splitter.split,
            parameter
        )
        
        # Log profiling results
        print("\nFormat Splitter Profile:")
        print(format_stats)
        print("\nSemantic Splitter Profile:")
        print(semantic_stats)


if __name__ == '__main__':
    unittest.main(verbosity=2)