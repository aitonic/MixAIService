from src.app.model_components.model.openai_style import OpenAiStyleModel, OpenAiStyleLLMParameter,BaseCompletionParameter

result = OpenAiStyleModel(OpenAiStyleLLMParameter(api_key = "123", base_url = "http://192.168.11.11:8070")).embeddings.create(text="这是一个测试")

print(result)