from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings


class TextSplitter:
    """Wrapper around LangChain's RecursiveCharacterTextSplitter for splitting
    legal document text into chunks with optional overlap.

    Optimized for legal document structure (sections, articles, numbered paragraphs).
    Allows custom chunk sizes, overlaps, and separators, falling back
    to settings defaults if not provided.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        separators: list[str] | None = None,
    ):
        """Initialize a TextSplitter instance.

        Args:
            chunk_size (int | None): Maximum size of each chunk. Defaults to
                `settings.text_splitter.chunk_size`.
            chunk_overlap (int | None): Number of overlapping characters between chunks.
                Defaults to `settings.text_splitter.chunk_overlap`.
            separators (list[str] | None): List of separators to use when splitting text.
                Defaults to `settings.text_splitter.separators` which is optimized
                for legal document structure.

        """
        config = settings.text_splitter

        self.separators = (
            separators
            or config.separators
            or [
                # Fallback separators if config is empty
                "\n\n",
                "\n",
                ". ",
                "! ",
                "? ",
                " ",
                "",
            ]
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or config.chunk_size,
            chunk_overlap=chunk_overlap or config.chunk_overlap,
            separators=self.separators,
        )

    def split_text(self, text: str) -> list[str]:
        """Split the input text into chunks based on configured size, overlap, and separators.

        Args:
            text (str): The text to split.

        Returns:
            list[str]: List of text chunks.

        """
        return self.splitter.split_text(text)
