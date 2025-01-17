# {
#     "appNo":"doc_reader",
#     "data":{
#         "query":"data/unstructured_text.txt"
#     }
# }

import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(project_root)
sys.path.append(project_root)
from src.app.model_components.doc_reader.doc_reader_factory import DocReaderFactory

result = DocReaderFactory()\
        .get_component({"query":"data/unstructured_text.txt"})({"query":"data/unstructured_text.txt"})

print(result)