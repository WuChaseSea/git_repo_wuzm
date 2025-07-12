import os
from importlib.metadata import version
from inspect import currentframe, getframeinfo
from pathlib import Path

from decouple import config
from app.utils.lang import SUPPORTED_LANGUAGE_MAP

cur_frame = currentframe()
if cur_frame is None:
    raise ValueError("Cannot get the current frame.")
this_file = getframeinfo(cur_frame).filename
this_dir = Path(this_file).parent

VP_PACKAGE_NAME = "viewpaper_app"
VP_APP_VERSION = config("VP_APP_VERSION", None)
if not VP_APP_VERSION:
    try:
        # Caution: This might produce the wrong version
        # https://stackoverflow.com/a/59533071
        VP_APP_VERSION = version(VP_PACKAGE_NAME)
    except Exception:
        VP_APP_VERSION = "local"
VP_ENABLE_FIRST_SETUP = config("KH_ENABLE_FIRST_SETUP", default=True, cast=bool)

VP_APP_DATA_DIR = this_dir / "viewpaper_app_data"
VP_APP_DATA_EXISTS = VP_APP_DATA_DIR.exists()
VP_APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_APP: dict[str, dict] = {}
SETTINGS_REASONING = {
    "use": {
        "name": "Reasoning options",
        "value": None,
        "choices": [],
        "component": "radio",
    },
    "lang": {
        "name": "Language",
        "value": "en",
        "choices": [(lang, code) for code, lang in SUPPORTED_LANGUAGE_MAP.items()],
        "component": "dropdown",
    },
    "max_context_length": {
        "name": "Max context length (LLM)",
        "value": 32000,
        "component": "number",
    },
}

VP_REASONINGS = [
    "app.reasoning.simple.FullQAPipeline",
]

VP_INDEX_TYPES = [
    "app.index.file.FileIndex",
]
VP_INDICES = [
    {
        "name": "File Collection",
        "config": {
            "supported_file_types": (
                ".png, .jpeg, .jpg, .tiff, .tif, .pdf, .xls, .xlsx, .doc, .docx, "
                ".pptx, .csv, .html, .mhtml, .txt, .md, .zip"
            ),
            "private": True,
        },
        "index_type": "app.index.file.FileIndex",
    },
]

