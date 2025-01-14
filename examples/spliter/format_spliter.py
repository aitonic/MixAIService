# from langchain_text_splitters import SpacyTextSplitter
# splitter = SpacyTextSplitter(chunk_size = 100, chunk_overlap  = 2)

text = '''
# Programming
Programming is a fundamental skill in software development.
Python is one of the most popular programming languages.
It's widely used in AI and web development.

# Cooking
Cooking is both an art and a science.
Baking bread requires precise measurements and timing.
Understanding temperature control is crucial.

# Gardening
Gardening helps connect with nature.
Growing vegetables requires patience and care.
Different plants need different soil conditions.
'''
# splits = splitter.split_text(text.replace('-',''))

# print(len(splits))
# for s in splits:
#     print(f'====={s}=======')

import requests
result = requests.post(url="http://127.0.0.1:8899/simple-ai/run", json={
    "appNo":"format_split",
    "data":{
        "query":text,
        "max_length": 50
    }
}).json()

print(result)