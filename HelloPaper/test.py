import gradio as gr

def on_upload(files):
    print("Upload called:", files)
    return "Uploading..."

# with gr.Blocks() as demo:
#     upload = gr.File(file_types=[".pdf"], file_count="multiple")
#     status = gr.Textbox(label="Status")
#     upload.upload(fn=on_upload, outputs=status)

with gr.Blocks() as demo:
    with gr.Column(scale=1, elem_id="conv-settings-panel") as conv_column:

        quick_upload_label = ("Quick Upload")
        with gr.Accordion(label=quick_upload_label) as _:
            quick_file_upload_status = gr.Markdown("none")
            quick_file_upload = gr.File(
                    file_types=['.pdf'],
                    file_count="multiple",
                    container=True,
                    show_label=False,
                    elem_id="quick-file",
                )
            status = gr.Textbox(label="Status")
            quick_file_upload.upload(fn=on_upload, outputs=status)
            

demo.launch()