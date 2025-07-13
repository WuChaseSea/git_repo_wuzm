import os
from importlib.metadata import version
from inspect import currentframe, getframeinfo
from pathlib import Path

from decouple import config
from apps.utils.lang import SUPPORTED_LANGUAGE_MAP

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

VP_DEMO_MODE = config("VP_DEMO_MODE", default=False, cast=bool)
VP_OLLAMA_URL = config("VP_OLLAMA_URL", default="http://localhost:11434/v1/")

VP_APP_DATA_DIR = this_dir / "viewpaper_app_data"
VP_APP_DATA_EXISTS = VP_APP_DATA_DIR.exists()
VP_APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# User data directory
VP_USER_DATA_DIR = VP_APP_DATA_DIR / "user_data"
VP_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# markdown output directory
VP_MARKDOWN_OUTPUT_DIR = VP_APP_DATA_DIR / "markdown_cache_dir"
VP_MARKDOWN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# chunks output directory
VP_CHUNKS_OUTPUT_DIR = VP_APP_DATA_DIR / "chunks_cache_dir"
VP_CHUNKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# zip output directory
VP_ZIP_OUTPUT_DIR = VP_APP_DATA_DIR / "zip_cache_dir"
VP_ZIP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# zip input directory
VP_ZIP_INPUT_DIR = VP_APP_DATA_DIR / "zip_cache_dir_in"
VP_ZIP_INPUT_DIR.mkdir(parents=True, exist_ok=True)

VP_FEATURE_CHAT_SUGGESTION = config(
    "VP_FEATURE_CHAT_SUGGESTION", default=False, cast=bool
)

VP_SSO_ENABLED = config("VP_SSO_ENABLED", default=False, cast=bool)
VP_USER_CAN_SEE_PUBLIC = None

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
    "apps.reasoning.simple.FullQAPipeline",
]

VP_INDEX_TYPES = [
    "apps.index.file.FileIndex",
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
        "index_type": "apps.index.file.FileIndex",
    },
]

VP_FEATURE_CHAT_SUGGESTION = config(
    "VP_FEATURE_CHAT_SUGGESTION", default=False, cast=bool
)

### 数据库配置
VP_DATABASE = f"sqlite:///{VP_USER_DATA_DIR / 'sql.db'}"
VP_ENABLE_ALEMBIC = False
