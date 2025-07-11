from llama_index.core.readers.base import BaseReader
from models.loaders import (
    AdobeReader,
    AzureAIDocumentIntelligenceLoader,
    DirectoryReader,
    DoclingReader,
    HtmlReader,
    MathpixPDFReader,
    MhtmlReader,
    OCRReader,
    PandasExcelReader,
    PDFThumbnailReader,
    TxtReader,
    UnstructuredReader,
    WebReader,
)
unstructured = UnstructuredReader()


KH_DEFAULT_FILE_EXTRACTORS: dict[str, BaseReader] = {
    ".xlsx": PandasExcelReader(),
    ".docx": unstructured,
    ".pptx": unstructured,
    ".xls": unstructured,
    ".doc": unstructured,
    ".html": HtmlReader(),
    ".mhtml": MhtmlReader(),
    ".png": unstructured,
    ".jpeg": unstructured,
    ".jpg": unstructured,
    ".tiff": unstructured,
    ".tif": unstructured,
    ".pdf": PDFThumbnailReader(),
    ".txt": TxtReader(),
    ".md": TxtReader(),
}