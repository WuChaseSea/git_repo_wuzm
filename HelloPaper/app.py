import os

import settings

VP_APP_DATA_DIR = getattr(settings, "VP_APP_DATA_DIR", ".")
VP_GRADIO_SHARE = getattr(settings, "VP_GRADIO_SHARE", False)
GRADIO_TEMP_DIR = os.getenv("GRADIO_TEMP_DIR", None)
# override GRADIO_TEMP_DIR if it's not set
if GRADIO_TEMP_DIR is None:
    GRADIO_TEMP_DIR = os.path.join(VP_APP_DATA_DIR, "gradio_tmp")
    os.environ["GRADIO_TEMP_DIR"] = GRADIO_TEMP_DIR

from apps.main import App

app = App()
demo = app.make()
demo.queue().launch(
    favicon_path=app._favicon,
    inbrowser=True,
    allowed_paths=[
        "assets",
        GRADIO_TEMP_DIR,
    ],
    share=VP_GRADIO_SHARE,
)
