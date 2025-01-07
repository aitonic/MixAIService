from openai import OpenAI

client = OpenAI()
client.chat.completions.create
# client.embeddings.create
# client.completions.create
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.app.model_components.model.openai_style import OpenAiStyleModel, OpenAiStyleLLMParameter,BaseCompletionParameter

result = OpenAiStyleModel(OpenAiStyleLLMParameter(api_key = "123", full_url = "http:127.0.0.1:1234/chat/v1/completions")).chat.completions.create(BaseCompletionParameter(messages=[{"role":"system", "content":"你是一个数学家"}, {"role":"user","content":"10的20倍是多少"}]))

for r in result:
    print(r)