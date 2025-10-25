from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pymupdf4llm
from pathlib import Path


class PDFParserToolInput(BaseModel):
    """Input schema for PDFParserTool."""
    pdf_path: str = Field(..., description="Path to the PDF file to parse")


class PDFParserTool(BaseTool):
    name: str = "PDF to Markdown Parser"
    description: str = (
        "Converts PDF documents to markdown format using direct text extraction. "
        "Preserves document structure, formatting, and returns clean markdown text. "
        "Input: path to PDF file. Output: markdown text content."
    )
    args_schema: Type[BaseModel] = PDFParserToolInput

    def _run(self, pdf_path: str) -> str:
        """
        Convert a PDF document to markdown format.

        Args:
            pdf_path: Path to the input PDF file

        Returns:
            str: The markdown text content extracted from the PDF

        Raises:
            FileNotFoundError: If input PDF doesn't exist
            Exception: If PDF parsing fails
        """
        input_path = Path(pdf_path)

        if not input_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            # Convert PDF to markdown using direct text extraction
            md_text = pymupdf4llm.to_markdown(str(input_path))
            return md_text
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")
