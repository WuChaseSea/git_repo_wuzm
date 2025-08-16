from llama_index.core.schema import NodeWithScore, TextNode, NodeRelationship


def merge_strings(A, B):
    # 找到A的结尾和B的开头最长的匹配子串
    max_overlap = 0
    min_length = min(len(A), len(B))

    for i in range(1, min_length + 1):
        if A[-i:] == B[:i]:
            max_overlap = i

    # 合并A和B，去除重复部分
    merged_string = A + B[max_overlap:]
    return merged_string


def get_node_content(node: NodeWithScore, embed_type=0, nodes: list[TextNode] = None, nodeid2idx: dict = None) -> str:
    text: str = node.get_content()
    if embed_type == 6:
        cur_text = text
        if cur_text.count("|") >= 5 and cur_text.count("---") == 0:
            cnt = 0
            flag = False
            while True:
                pre_node_id = node.node.relationships[NodeRelationship.PREVIOUS].node_id
                pre_node = nodes[nodeid2idx[pre_node_id]]
                pre_text = pre_node.text
                cur_text = merge_strings(pre_text, cur_text)
                cnt += 1
                if pre_text.count("---") >= 2:
                    flag = True
                    break
                if cnt >= 3:
                    break
            if flag:
                idx = cur_text.index("---")
                text = cur_text[:idx].strip().split("\n")[-1] + cur_text[idx:]
            # print(flag, cnt)
    if embed_type == 1:
        if 'file_path' in node.metadata:
            text = '###\n' + node.metadata['file_path'] + "\n\n" + text
    elif embed_type == 2:
        if 'know_path' in node.metadata:
            text = '###\n' + node.metadata['know_path'] + "\n\n" + text
    elif embed_type == 3 or embed_type == 6:
        if "imgobjs" in node.metadata and len(node.metadata['imgobjs']) > 0:
            for imgobj in node.metadata['imgobjs']:
                text = text.replace(f"{imgobj['cap']} {imgobj['title']}\n",
                                    f"{imgobj['cap']}.{imgobj['title']}:{imgobj['content']}\n")
    elif embed_type == 4:
        if 'file_path' in node.metadata:
            text = node.metadata['file_path']
        else:
            text = ""
    elif embed_type == 5:
        if 'know_path' in node.metadata:
            text = node.metadata['know_path']
        else:
            text = ""
    return text