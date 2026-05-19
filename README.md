# AI Tools

A collection of local tools for working with AI systems — built for practical, day-to-day use with LLMs like Claude, ChatGPT, and others.

---

## Projects

### Document Converter
**Folder:** [`pdf-to-markdown/`](pdf-to-markdown/)

A local web app that converts documents into clean Markdown and extracts embedded images, ready to feed into any LLM.

**Supported formats:** PDF, Word (.docx), PowerPoint (.pptx), HTML, and image files (PNG, JPG, TIFF, etc.)

**Key features:**
- Browser-based UI — no command line needed after setup
- 5 conversion modes: Markdown only, Markdown + Images, Markdown + Images + Descriptions, Images only, Images + Descriptions only
- AI-powered image descriptions using a local BLIP model — no API key required
- OCR for text found inside images (charts, diagrams, labels)
- Batch processing with per-file timing
- Powered by [docling](https://github.com/docling-project/docling) (IBM) and [BLIP](https://github.com/salesforce/BLIP) (Salesforce)

**Setup:** Double-click `start.bat` — installs Python, dependencies, and AI models automatically on first run.

→ [Full documentation](pdf-to-markdown/README.md)

---

## Why Markdown for LLMs?

Markdown is the most token-efficient format for feeding structured documents into LLMs:

- LLMs are trained heavily on Markdown and understand it natively
- Preserves document structure (headings, tables, lists) with minimal token overhead
- Far cheaper than sending scanned PDFs as images (which use vision tokens)
- Clean, portable, and easy to copy-paste into any LLM interface
- Image descriptions embedded in Markdown give LLMs full context without sending raw images

---

## Requirements

- Windows 10 or 11
- Each tool manages its own Python environment — no global setup needed
