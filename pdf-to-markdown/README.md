# Document Converter

A local web app that converts documents into clean Markdown and extracts embedded images — ready to use with Claude, ChatGPT, or any other LLM.

Built with [Streamlit](https://streamlit.io) and [docling](https://github.com/docling-project/docling).

---

## What it does

- Converts documents to well-structured Markdown in your browser
- Extracts embedded images from documents as PNG files
- Describes image content using a local AI model (BLIP) — no API key needed
- OCRs text found inside images (charts, diagrams, labels)
- Handles PDF, Word (.docx), PowerPoint (.pptx), HTML, and image files
- Shows a side-by-side rendered preview and raw Markdown for each file
- Shows conversion time per file

---

## Supported input formats

| Format | Extension(s) | Notes |
|---|---|---|
| PDF | .pdf | Text, scanned, tables, academic papers |
| Word | .docx | Full text and embedded images |
| PowerPoint | .pptx | Slides converted to markdown |
| HTML | .html, .htm | Web pages |
| Images | .png .jpg .jpeg .tiff .bmp .webp | OCR and description applied |

---

## Conversion modes

Choose what you want to extract before clicking Convert:

| Mode | Output | Download |
|---|---|---|
| Markdown only | Document text as `.md` | `.md` file |
| Markdown + Images | Text + extracted image PNGs | ZIP |
| Markdown + Images + Descriptions | Text + images + AI descriptions + OCR | ZIP |
| Images only | Extracted image PNGs, no text | ZIP |
| Images + Descriptions only | Images + AI descriptions + OCR, no document text | ZIP |

**Image descriptions** use a local BLIP model (~990 MB, downloaded once on first use). No internet connection or API key required after download.

---

## Requirements

- Windows 10 or 11
- Internet connection for first-time setup (~4 GB total download)
- ~5 GB free disk space
- ~4 GB RAM (more if using image descriptions)

Python is installed automatically if not already present.

---

## Getting started

1. Download or clone this project folder to your computer
2. Double-click **`start.bat`**
3. Wait for setup to complete (first run only — downloads Python, dependencies, and AI models)
4. Your browser will open automatically at **http://localhost:8501**

That's it. From the second run onwards, the app starts in about 10 seconds.

---

## How to use

1. **Upload** one or more files using the sidebar on the left
2. **Choose a mode** — select what you want to extract
3. Click **Convert All**
4. Wait for conversion to finish — time is shown on screen
5. **Preview** the output in the results tabs
6. **Download** the output using the button in each tab, or download all files at once as a ZIP

---

## First-run setup details

`start.bat` handles everything automatically in this order:

| Step | What happens | Time |
|---|---|---|
| Python check | Installs Python 3.13 via winget if not found | 1–3 min |
| Dependencies | Installs docling, streamlit, torch (~3 GB) | 5–15 min |
| AI models (docling) | Layout and OCR models downloaded on first conversion (~500 MB) | 2–5 min |
| AI model (BLIP) | Downloaded on first use of a Descriptions mode (~990 MB) | 3–8 min |

All subsequent runs skip these steps and start immediately.

Cached model locations:
```
C:\Users\<your-username>\.cache\docling\models\     ← docling layout/OCR models
C:\Users\<your-username>\.cache\huggingface\        ← BLIP image description model
```

---

## Performance

| File type | Typical speed (CPU) |
|---|---|
| Digital / text PDF | 5–15 s |
| PDF with tables | 10–30 s |
| Academic paper (complex layout) | 15–45 s |
| Scanned document (OCR) | 60–90 s per 10 pages |
| Image description (BLIP, per image) | 1–3 s per image |

GPU (CUDA) is used automatically if available, significantly reducing conversion time for scanned documents and image descriptions.

---

## Conversion quality

| Content type | Expected accuracy |
|---|---|
| Clean digital PDF (text) | ~95% |
| PDF with tables | ~85–90% |
| Academic paper (multi-column) | ~80–90% |
| Scanned doc (good quality) | ~80–85% |
| Scanned doc (poor quality) | ~50–70% |
| Image description (photos) | Good |
| Image description (charts/diagrams) | Moderate — use Descriptions mode for best results |

---

## Troubleshooting

**Conversion fails for all files**
The virtual environment may be installed in a path containing non-ASCII characters (e.g. Turkish, Arabic, Chinese). `start.bat` avoids this by installing the venv to `C:\Users\<username>\pdf2md_venv\`. If you moved the venv manually, delete it and run `start.bat` again.

**The terminal gets stuck on first run**
Streamlit may be asking for an email address. Press Enter to skip it. This only happens once — the `.streamlit\config.toml` file disables the prompt for future runs.

**"Python was installed — please close and run again"**
Normal behaviour. Windows requires a new terminal session to pick up a newly installed program. Close the window and double-click `start.bat` again.

**The browser shows a blank page with a spinning icon**
On first use, docling loads its AI models into memory (~30 seconds). Leave the browser tab open and wait.

**Scanned PDFs are slow**
OCR on CPU takes ~60–90 seconds per 10 pages. A machine with an NVIDIA GPU processes the same document in ~10–20 seconds.

**No images extracted from my document**
HTML files reference images as external URLs and cannot be extracted. DOCX and PPTX image extraction depends on how the document was created. PDFs with embedded vector graphics (not raster images) will not produce extractable pictures.

---

## Project files

```
pdf-to-markdown/
├── app.py              — Streamlit web UI
├── converter.py        — docling conversion + BLIP image description logic
├── requirements.txt    — Python dependencies
├── start.bat           — One-click launcher (installs Python if needed)
├── .streamlit/
│   └── config.toml     — Disables Streamlit email prompt
└── README.md           — This file
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| docling | ≥ 2.94.0 | Document parsing, OCR, table extraction, markdown export |
| streamlit | ≥ 1.57.0 | Web UI |
| torch | auto | Required by docling and BLIP models |
| transformers | auto | BLIP image captioning model |
