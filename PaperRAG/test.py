
from langchain_community.document_loaders import UnstructuredPDFLoader

# 加载结构化元素
loader = UnstructuredPDFLoader(
    "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/papar_QA_dataset/papers/0/2024.acl-long.820.pdf",
    mode="elements"
)
elements = loader.load()

# 过滤函数：排除页码/页眉/页脚等疑似内容
def is_valid_content(element):
    text = element.page_content.strip()
    
    # 去除很短的行（比如单独的页码、标题序号等）
    if len(text) < 10:
        return False

    # 去除全数字（可能是页码）
    if text.isdigit():
        return False

    # 去除常见页码格式，比如 "Page 1", "1 of 10"
    import re
    if re.match(r"^page\s*\d+.*$", text.lower()):
        return False
    if re.match(r"^\d+\s*/\s*\d+$", text):
        return False

    # 根据类别保留正文
    category = element.metadata.get("category", "")
    if category in ["NarrativeText", "Title", "ListItem", "BulletedText"]:
        return True
    
    return False

# 应用过滤
filtered_docs = [el for el in elements if is_valid_content(el)]

# 输出正文
for doc in filtered_docs:
    print(doc.page_content)

