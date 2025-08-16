def replace_think_tag_with_details(text):
    text = text.replace(
        "<think>",
        '<details><summary><span style="color:grey">Thought</span></summary><blockquote>',  # noqa
    )
    text = text.replace("</think>", "</blockquote></details>")
    return text