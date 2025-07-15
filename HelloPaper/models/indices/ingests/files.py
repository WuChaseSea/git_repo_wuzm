from llama_index.core.readers.base import BaseReader
from models.loaders import (
    PDFThumbnailReader,
)


VP_DEFAULT_FILE_EXTRACTORS: dict[str, BaseReader] = {
    ".pdf": PDFThumbnailReader(),
}