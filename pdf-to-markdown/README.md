# PDF to Markdown Converter

A local web app that converts PDF files into clean Markdown — ready to paste into Claude, ChatGPT, or any other LLM.

Built with [Streamlit](https://streamlit.io) and [docling](https://github.com/docling-project/docling).

---

## What it does

- Converts PDFs to well-structured Markdown in your browser
- Handles digital/text PDFs, scanned documents (OCR), tables, and complex academic paper layouts
- Shows a side-by-side rendered preview and raw Markdown for each file
- Lets you download individual `.md` files or all files as a ZIP
- Shows conversion time per file

---

## Requirements

- Windows 10 or 11
- Internet connection for first-time setup (~3 GB download)
- ~4 GB free disk space
- ~4 GB RAM (for scanned PDFs with OCR)

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

1. **Upload** one or more PDF files using the sidebar on the left
2. Click **Convert All**
3. Wait for conversion to finish — time is shown on screen
4. **Preview** the Markdown output (rendered and raw, side by side)
5. **Download** individual `.md` files using the button in each tab, or download all files at once as a ZIP

---

## First-run setup details

`start.bat` handles everything automatically in this order:

| Step | What happens | Time |
|---|---|---|
| Python check | Installs Python 3.13 via winget if not found | 1–3 min |
| Dependencies | Installs docling, streamlit, torch (~3 GB) | 5–15 min |
| AI models | docling downloads layout and OCR models (~500 MB) on first conversion | 2–5 min |

All subsequent runs skip these steps and start immediately.

AI models are cached at:
```
C:\Users\<your-username>\.cache\docling\models\
```

---

## Performance

| PDF type | Typical speed (CPU) |
|---|---|
| Digital / text PDF | 5–15 s |
| PDF with tables | 10–30 s |
| Academic paper (complex layout) | 15–45 s |
| Scanned document (OCR) | 60–90 s per 10 pages |

GPU (CUDA) is used automatically if available, significantly reducing conversion time for scanned documents.

---

## Conversion quality

| PDF type | Expected accuracy |
|---|---|
| Clean digital PDF | ~95% |
| PDF with tables | ~85–90% |
| Academic paper (multi-column) | ~80–90% |
| Scanned doc (good quality scan) | ~80–85% |
| Scanned doc (poor quality) | ~50–70% |

---

## Troubleshooting

**The app opens but conversion fails for all files**
The virtual environment may be installed in a folder path that contains non-ASCII characters (e.g. Turkish, Arabic, Chinese). `start.bat` avoids this by installing the venv to `C:\Users\<username>\pdf2md_venv\`. If you moved the venv manually, delete it and run `start.bat` again.

**The terminal gets stuck on startup**
Streamlit may be asking for an email address. Press Enter to skip it. This only happens once — the `.streamlit\config.toml` file in the project disables the prompt for future runs.

**"Python was installed — please close and run again"**
This is normal. Windows requires a new terminal session to pick up newly installed programs. Close the window and double-click `start.bat` again.

**The page is blank with a spinning icon**
On first use after setup, docling loads its AI models into memory (~30 seconds). Leave the browser tab open and wait — the UI will appear once loading is complete.

**Scanned PDFs are very slow**
OCR on CPU takes ~60–90 seconds per 10 pages. This is expected. If speed is important, a machine with an NVIDIA GPU will process the same document in ~10–20 seconds.

---

## Project files

```
pdf-to-markdown/
├── app.py              — Streamlit web UI
├── converter.py        — docling PDF conversion logic
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
| docling | ≥ 2.94.0 | PDF parsing, OCR, table extraction, markdown export |
| streamlit | ≥ 1.57.0 | Web UI |
| torch | auto | Required by docling's AI models |
