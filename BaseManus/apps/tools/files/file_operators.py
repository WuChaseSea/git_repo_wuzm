"""File operation interfaces and implementations for local environments."""

import asyncio
from pathlib import Path
from typing import Optional, Union

from apps.exceptions import ToolError

PathLike = Union[str, Path]
