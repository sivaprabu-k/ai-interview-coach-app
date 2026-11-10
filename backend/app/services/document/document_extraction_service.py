from pathlib import Path
import pymupdf
from docx import Document as DocxDocument


class DocumentExtractionService:
    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        extension = path.suffix.lower()

        if extension == ".pdf":
            return self._extract_pdf_text(path)

        if extension == ".docx":
            return self._extract_docx_text(path)

        raise ValueError(
            "Unsupported file format. Only PDF and DOCX are supported."
        )

    def _extract_pdf_text(self, file_path: Path) -> str:
        extracted_pages = []

        with pymupdf.open(file_path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                page_text = page.get_text("text").strip()

                if page_text:
                    extracted_pages.append(
                        f"[Page {page_number}]\n{page_text}"
                    )

        return "\n\n".join(extracted_pages)

    def _extract_docx_text(self, file_path: Path) -> str:
        document = DocxDocument(file_path)

        extracted_content = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                extracted_content.append(text)

        for table_index, table in enumerate(document.tables, start=1):
            extracted_content.append(
                f"\n[Table {table_index}]"
            )

            for row in table.rows:
                row_data = [
                    cell.text.strip().replace("\n", " ")
                    for cell in row.cells
                ]

                extracted_content.append(
                    " | ".join(row_data)
                )

        return "\n\n".join(extracted_content)
