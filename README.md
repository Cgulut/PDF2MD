# AI Tools

A collection of local tools for working with AI systems — built for practical, day-to-day use with LLMs like Claude, ChatGPT, and others.

---

## Projects

### PDF to Markdown Converter
**Folder:** [`pdf-to-markdown/`](pdf-to-markdown/)

A local web app that converts PDF files into clean Markdown, ready to feed into any LLM.

**Handles:** digital/text PDFs, scanned documents (OCR), tables, and complex academic paper layouts.

**Key features:**
- Browser-based UI — no command line needed after setup
- Drag-and-drop file upload, side-by-side preview, one-click download
- Batch conversion with per-file timing
- Powered by [docling](https://github.com/docling-project/docling) (IBM)

**Setup:** Double-click `start.bat` — installs Python, dependencies, and AI models automatically on first run.

→ [Full documentation](pdf-to-markdown/README.md)

---

## Why Markdown for LLMs?

Markdown is the most token-efficient format for feeding structured documents into LLMs:

- LLMs are trained heavily on Markdown and understand it natively
- Preserves document structure (headings, tables, lists) with minimal token overhead
- Far cheaper than sending scanned PDFs as images (which use vision tokens)
- Clean, portable, and easy to copy-paste into any LLM interface

---

## Requirements

- Windows 10 or 11
- Each tool manages its own Python environment — no global setup needed
