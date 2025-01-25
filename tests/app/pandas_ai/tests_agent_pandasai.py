import unittest
from unittest.mock import Mock, patch
import pandas as pd
import os
import sys



project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)
env_path = os.path.join(project_root, "config", ".env")

from src.app.agent.agent import Agent
# from src.app.agent.base import BaseAgent
# from src.app.components.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
# from src.utils.schemas.df_config import Config

class TestAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.sample_df = pd.DataFrame({
            "country": ["United States", "United Kingdom", "France"],
            "revenue": [5000, 3200, 2900]
        })
        
        # Mock environment variable
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test_key',
            'PANDASAI_API_KEY': 'test_key'
        })
        self.env_patcher.start()
        
        # Create config with OpenAI LLM
        from src.utils.llm import OpenAI
        config = {"llm": OpenAI()}
        
        # Create agent instance
        self.agent = Agent(self.sample_df, config=config)

    # def tearDown(self):
    #     """Clean up after each test method"""
    #     self.env_patcher.stop()

    # def test_agent_initialization(self):
    #     """Test if Agent initializes correctly"""
    #     self.assertIsInstance(self.agent, BaseAgent)
    #     self.assertIsInstance(self.agent.pipeline, GenerateChatPipeline)
    #     self.assertEqual(len(self.agent.dfs), 1)

    # def test_agent_with_multiple_dataframes(self):
    #     """Test if Agent handles multiple dataframes correctly"""
    #     df2 = pd.DataFrame({"test": [1, 2, 3]})
    #     agent = Agent([self.sample_df, df2])
    #     self.assertEqual(len(agent.dfs), 2)

    # @patch('src.app.agent.agent.GenerateChatPipeline')
    # def test_chat_method(self, mock_pipeline):
    #     """Test the chat method of Agent"""
    #     # Setup mock
    #     mock_pipeline.return_value.run.return_value = "Test response"
        
    #     # Create agent with mocked pipeline
    #     agent = Agent(self.sample_df, pipeline=mock_pipeline)
        
    #     # Test chat method
    #     response = agent.chat("Which country has highest revenue?")
    #     self.assertEqual(response, "Test response")

    # def test_agent_with_custom_config(self):
    #     """Test Agent initialization with custom config"""
    #     custom_config = Config(
    #         save_logs=True,
    #         verbose=True
    #     )
    #     agent = Agent(self.sample_df, config=custom_config)
    #     self.assertEqual(agent.config.save_logs, True)
    #     self.assertEqual(agent.config.verbose, True)

    # def test_last_error_property(self):
    #     """Test last_error property"""
    #     mock_error = "Test error"
    #     self.agent.pipeline.last_error = mock_error
    #     self.assertEqual(self.agent.last_error, mock_error)

    # def test_generate_code(self):
    #     """Test generate_code method"""
    #     with patch.object(self.agent.pipeline, 'run_generate_code') as mock_generate:
    #         mock_generate.return_value = "test_code"
    #         result = self.agent.generate_code("Generate code to show top revenue")
    #         self.assertEqual(result, "test_code")

    # def test_execute_code(self):
    #     """Test execute_code method"""
    #     test_code = "print('test')"
    #     with patch.object(self.agent.pipeline, 'run_execute_code') as mock_execute:
    #         mock_execute.return_value = "test output"
    #         result = self.agent.execute_code(test_code)
    #         self.assertEqual(result, "test output")

    # def test_start_new_conversation(self):
    #     """Test conversation reset"""
    #     initial_memory = self.agent.context.memory
    #     self.agent.start_new_conversation()
    #     self.assertNotEqual(id(initial_memory), id(self.agent.context.memory))

    def test_real_sales_analysis(self):
        """Test actual sales analysis with a real dataframe"""
        # Create sample sales data
        sales_df = pd.DataFrame({
            "country": ["United States", "United Kingdom", "France", "Germany", "Italy", 
                       "Spain", "Canada", "Australia", "Japan", "China"],
            "revenue": [5000, 3200, 2900, 4100, 2300, 2100, 2500, 2600, 4500, 7000]
        })

        # Initialize agent with real data
        # agent = Agent(sales_df, self.config)
        self.agent.dsf = sales_df
        agent = self.agent

        # Test different analysis queries
        top_countries = agent.chat('Which are the top 5 countries by revenue?')
        self.assertIsNotNone(top_countries)
        self.assertIn("China", top_countries)  # China should be mentioned as it has highest revenue

        # Test average revenue calculation
        avg_revenue = agent.chat('What is the average revenue across all countries?')
        self.assertIsNotNone(avg_revenue)
        # Average should be around 3620
        self.assertIn("3620", avg_revenue)

        # Test revenue range analysis
        revenue_range = agent.chat('What is the difference between highest and lowest revenue?')
        self.assertIsNotNone(revenue_range)
        # Difference should be 7000 - 2100 = 4900
        self.assertIn("4900", revenue_range)

    # def test_real_data_visualization(self):
    #     """Test data visualization capabilities with real data"""
    #     # Create sample data with clear patterns
    #     data = pd.DataFrame({
    #         "month": ["Jan", "Feb", "Mar", "Apr", "May"],
    #         "sales": [100, 150, 200, 180, 250],
    #         "expenses": [80, 90, 120, 110, 140]
    #     })

    #     agent = Agent(data)

    #     # Test plotting capabilities
    #     plot_response = agent.chat('Create a line plot showing sales and expenses trends')
    #     self.assertIsNotNone(plot_response)
    #     # Verify that a plot was generated
    #     self.assertTrue(any(keyword in plot_response.lower() 
    #                       for keyword in ['plot', 'graph', 'figure', 'visualization']))


if __name__ == '__main__':
    unittest.main() 