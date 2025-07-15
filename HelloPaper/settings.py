import os
from importlib.metadata import version
from inspect import currentframe, getframeinfo
from pathlib import Path

from decouple import config

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

VP_APP_DATA_DIR = this_dir / "viewpaper_app_data"
VP_APP_DATA_EXISTS = VP_APP_DATA_DIR.exists()
VP_APP_DATA_DIR.mkdir(parents=True, exist_ok=True)


