# {
#     "appNo":"doc_reader",
#     "data":{
#         "query":"data/惠闽宝2024年客服QA-6.25.json"
#     }
# }
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(project_root)
sys.path.append(project_root)
from src.app.components.doc_reader.doc_reader_factory import DocReaderFactory

result = DocReaderFactory()\
        .get_component({"query":"data/惠闽宝2024年客服QA-6.25.json"})({"query":"data/惠闽宝2024年客服QA-6.25.json"})

print(result)