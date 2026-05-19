import io
from pathlib import Path


def build_converter():
    # Imported here so the page renders before these heavy libraries load
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import (
        DocumentConverter, PdfFormatOption,
        WordFormatOption, PowerpointFormatOption, ImageFormatOption,
    )

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.generate_page_images = False
    pipeline_options.generate_picture_images = True

    return DocumentConverter(
        allowed_formats=[
            InputFormat.PDF, InputFormat.DOCX, InputFormat.PPTX,
            InputFormat.HTML, InputFormat.IMAGE,
        ],
        format_options={
            InputFormat.PDF:   PdfFormatOption(pipeline_options=pipeline_options),
            InputFormat.DOCX:  WordFormatOption(),
            InputFormat.PPTX:  PowerpointFormatOption(),
            InputFormat.IMAGE: ImageFormatOption(),
        }
    )


def build_image_captioner():
    # Downloads ~990 MB on first call; cached in ~/.cache/huggingface/
    from transformers import BlipProcessor, BlipForConditionalGeneration
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    model.eval()
    return processor, model


def describe_image(captioner, pil_image) -> str:
    import torch
    processor, model = captioner
    inputs = processor(pil_image.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=150)
    return processor.decode(out[0], skip_special_tokens=True)


def ocr_image(pil_image) -> str:
    try:
        import easyocr
        import numpy as np
        reader = easyocr.Reader(["en"], verbose=False)
        results = reader.readtext(np.array(pil_image.convert("RGB")))
        return " ".join([item[1] for item in results if item[2] > 0.3])
    except Exception:
        return ""


def extract_images(result, captioner=None) -> list[dict]:
    images = []
    for i, picture in enumerate(result.document.pictures):
        try:
            pil_img = picture.get_image(result.document)
        except Exception:
            pil_img = None
        if pil_img is None:
            continue

        caption = ""
        try:
            caption = picture.caption_text(doc=result.document) or ""
        except Exception:
            pass

        description = ""
        ocr_text = ""
        if captioner is not None:
            description = describe_image(captioner, pil_img)
            ocr_text = ocr_image(pil_img)

        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")

        images.append({
            "ref_id":      f"image_{i + 1}",
            "filename":    f"image_{i + 1}.png",
            "bytes":       buf.getvalue(),
            "caption":     caption,
            "description": description,
            "ocr_text":    ocr_text,
        })
    return images


def _image_markdown_section(images: list[dict]) -> str:
    lines = ["\n\n## Extracted Images\n"]
    for img in images:
        lines.append(f"\n### {img['ref_id'].replace('_', ' ').title()}\n")
        if img["caption"]:
            lines.append(f"**Caption:** {img['caption']}\n\n")
        if img["description"]:
            lines.append(f"**Description:** {img['description']}\n\n")
        if img["ocr_text"]:
            lines.append(f"**Text found in image:** {img['ocr_text']}\n\n")
        lines.append(f"![{img['ref_id']}](images/{img['filename']})\n")
    return "".join(lines)


def convert_file(
    converter,
    file_path: Path,
    mode: str = "md_only",
    captioner=None,
) -> tuple[str, str, list]:
    """
    Returns (markdown, status, images).
    mode: "md_only" | "md_images" | "md_images_desc" | "images_only" | "images_desc_only"
    """
    from docling.datamodel.base_models import ConversionStatus

    needs_text  = mode in ("md_only", "md_images", "md_images_desc")
    needs_imgs  = mode in ("md_images", "md_images_desc", "images_only", "images_desc_only")
    needs_desc  = mode in ("md_images_desc", "images_desc_only")

    try:
        result = converter.convert(str(file_path))

        if result.status not in (ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS):
            return "", f"Conversion failed: {result.status}", []

        status   = "ok" if result.status == ConversionStatus.SUCCESS else "partial"
        markdown = result.document.export_to_markdown() if needs_text else ""
        images   = extract_images(result, captioner if needs_desc else None) if needs_imgs else []

        if images:
            if mode in ("md_images", "md_images_desc"):
                markdown += _image_markdown_section(images)
            elif mode == "images_desc_only":
                # descriptions-only markdown — no document body text
                markdown = _image_markdown_section(images).strip()

        return markdown, status, images

    except Exception as e:
        return "", f"Error: {e}", []
