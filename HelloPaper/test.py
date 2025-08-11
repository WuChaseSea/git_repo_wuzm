import gradio as gr

def on_upload(files):
    print("Upload called:", files)
    return "Uploading..."

# with gr.Blocks() as demo:
#     upload = gr.File(file_types=[".pdf"], file_count="multiple")
#     status = gr.Textbox(label="Status")
#     upload.upload(fn=on_upload, outputs=status)


with gr.Blocks() as demo:
    with gr.Row():
        state_retrieval_history = gr.State([])
        with gr.Column(scale=1, elem_id="conv-settings-panel") as conv_column:

            quick_upload_label = ("Quick Upload")
            with gr.Accordion(label=quick_upload_label) as _:
                quick_file_upload_status = gr.Markdown("none")
                quick_file_upload = gr.File(
                        file_types=[".pdf"],
                        file_count="multiple",
                        container=True,
                        show_label=False,
                        elem_id="quick-file",
                    )
                print("*************** quick_file_upload id:", id(quick_file_upload))
                def on_upload():
                    print("Upload called:")
                    return "Uploading..."
                status = gr.Textbox(label="Status")
                quick_file_upload.upload(fn=on_upload, outputs=quick_file_upload_status)
                
                quick_urls = gr.Textbox(
                    placeholder=(
                        "Or paste URLs"
                    ),
                    lines=1,
                    container=False,
                    show_label=False,
                    elem_id=(
                        "quick-url"
                    ),
                )


demo.launch()