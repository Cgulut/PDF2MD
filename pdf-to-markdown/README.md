# PDF to Markdown Converter

A local web app that converts PDFs to clean Markdown using [docling](https://github.com/docling-project/docling).

Handles: digital/text PDFs, scanned documents (OCR), tables, and complex academic paper layouts.

## Setup

Requires Python 3.10 or higher.

```
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies (~2-3 GB download including torch)
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## First-Run Model Download

On the very first run, docling downloads layout and OCR models (~500 MB) to:

```
%USERPROFILE%\.cache\docling\models\
```

This happens automatically and only once. After that, the app loads in 5–10 seconds.

To pre-download models without starting the app (e.g. on a machine with internet before going offline):

```
docling-tools models download
```

## Usage

1. Upload one or more PDF files using the sidebar
2. Click **Convert All**
3. Preview rendered markdown and raw markdown side-by-side per file
4. Download individual `.md` files or all files as a ZIP

## Performance Notes

| PDF type | Speed (CPU) | Speed (GPU) |
|---|---|---|
| Digital/text PDF | Fast (2–10 s) | Fast |
| Scanned doc (OCR) | ~60–90 s per 10 pages | ~10–20 s per 10 pages |
| Academic paper | 10–30 s | 5–15 s |

GPU (CUDA) is used automatically if available — no configuration needed.

## Memory Usage

- Text PDFs: ~2 GB RAM
- Scanned PDFs with EasyOCR: ~4 GB RAM

## Streamlit Upload Size Limit

By default Streamlit limits uploads to 200 MB. To increase it, create `~/.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 500
```
