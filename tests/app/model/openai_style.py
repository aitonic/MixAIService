from collections.abc import Iterator

from src.app.model_components.model.openai_style import (
    BaseCompletionParameter,
    OpenAiStyleLLMParameter,
    OpenAiStyleModel,
)

result = OpenAiStyleModel(OpenAiStyleLLMParameter(api_key = "123", full_url = "http://127.0.0.1:1234/v1/chat/completions")).chat.completions.create(BaseCompletionParameter(messages=[{"role":"system", "content":"你是一个数学家"}, {"role":"user","content":"10的20倍是多少"}]))

if isinstance(result, Iterator):
    for r in result:
        print(r)
else:
    print(result)
