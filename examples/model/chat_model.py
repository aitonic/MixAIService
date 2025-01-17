# {
#     "appNo":"chat_model",
#     "data":{
#         "query":"小马撒了一些花种，第一天开出花朵的数量是总数量的一半多一个，第二天，在剩下的种子中，又开出了一半多一个。还剩下3个种子没有开花。告诉我，小马一共撒下了多少个花种？",
#         "system_prompt":"你是一个数学家，可以通过严禁的思考和推理解决所有的数学问题。记住，对于数学问题，你需要逐步推理。",
#         "max_length": 50
#     }
# }
from collections.abc import Iterator
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(project_root)
sys.path.append(project_root)

from src.app.model_components.model.openai_style import (
    BaseCompletionParameter,
    OpenAiStyleLLMParameter,
    OpenAiStyleModel,
)

result = OpenAiStyleModel(OpenAiStyleLLMParameter(api_key = "123", full_url = "http://127.0.0.1:1234/v1/chat/completions")).chat.completions.create(BaseCompletionParameter(messages=[{"role":"system", "content":"你是一个数学家"}, {"role":"user","content":"10的20倍是多少"}]))

if isinstance(result, Iterator):
    print("--------------------")
    for r in result:
        print(r)
else:
    print(result)