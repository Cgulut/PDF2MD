from pathlib import Path


def build_converter():
    # Imported here so the page renders before these heavy libraries load
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.generate_page_images = False

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )


def convert_file(converter, pdf_path: Path) -> tuple[str, str]:
    """
    Returns (markdown_text, status) where status is "ok", "partial", or an error message.
    """
    from docling.datamodel.base_models import ConversionStatus

    try:
        result = converter.convert(str(pdf_path))
        if result.status == ConversionStatus.SUCCESS:
            return result.document.export_to_markdown(), "ok"
        elif result.status == ConversionStatus.PARTIAL_SUCCESS:
            return result.document.export_to_markdown(), "partial"
        else:
            return "", f"Conversion failed: {result.status}"
    except Exception as e:
        return "", f"Error: {e}"
