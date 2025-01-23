import unittest

from src.app.components.model.openai_style import (
    BaseCompletionParameter,
    OpenAiStyleLLMParameter,
    OpenAiStyleModel,
)
from src.app.components.model.dto import EmbedParameter

result = OpenAiStyleModel(OpenAiStyleLLMParameter(api_key = "123", base_url = "http://192.168.11.11:8070")).embeddings.create(EmbedParameter(query="测试文本"))

print(result)

if __name__ == '__main__':
    unittest.main()