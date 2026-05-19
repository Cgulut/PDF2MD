import io
import tempfile
import time
import zipfile
from pathlib import Path

import streamlit as st

from converter import build_converter, convert_file

st.set_page_config(
    page_title="PDF to Markdown",
    page_icon="📄",
    layout="wide",
)

st.title("PDF to Markdown Converter")
st.caption("Powered by docling · Handles text PDFs, scanned docs, tables, and academic papers")

# ── Session state init ────────────────────────────────────────────────────────
# The converter holds ~500 MB of loaded AI models — must be cached across reruns.
if "converter" not in st.session_state:
    with st.spinner("Loading AI models — this takes ~30 s on first run ever, ~5 s after that..."):
        st.session_state.converter = build_converter()

if "results" not in st.session_state:
    st.session_state.results = {}  # filename -> {"markdown": str, "status": str}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Upload PDFs")
    uploaded_files = st.file_uploader(
        "Choose one or more PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) selected")
        for f in uploaded_files:
            st.write(f"- {f.name} ({f.size / 1024:.0f} KB)")

        st.divider()
        convert_btn = st.button("Convert All", type="primary", use_container_width=True)
    else:
        convert_btn = False
        st.info("Upload one or more PDF files to get started.")

    st.divider()
    st.caption("Scanned PDFs use EasyOCR and may take 60–90 s per 10 pages on CPU.")

# ── Conversion ────────────────────────────────────────────────────────────────
if convert_btn and uploaded_files:
    st.session_state.results = {}
    total = len(uploaded_files)
    progress = st.progress(0, text="Starting...")
    status_msg = st.empty()
    timer_display = st.empty()

    batch_start = time.time()
    seen: dict[str, int] = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, uploaded_file in enumerate(uploaded_files):
            # Strip directory components to prevent path traversal
            safe_name = Path(uploaded_file.name).name
            # De-duplicate: "report.pdf", "report (1).pdf", ...
            if safe_name in seen:
                seen[safe_name] += 1
                stem, suffix = Path(safe_name).stem, Path(safe_name).suffix
                safe_name = f"{stem} ({seen[safe_name]}){suffix}"
            else:
                seen[safe_name] = 0

            status_msg.info(f"Converting {i + 1}/{total}: **{safe_name}**")
            progress.progress(i / total, text=f"File {i + 1} of {total}")

            tmp_path = Path(tmpdir) / safe_name
            tmp_path.write_bytes(uploaded_file.getvalue())

            file_start = time.time()
            markdown, status = convert_file(st.session_state.converter, tmp_path)
            file_secs = round(time.time() - file_start, 1)

            st.session_state.results[safe_name] = {
                "markdown": markdown,
                "status": status,
                "duration": file_secs,
            }

            total_elapsed = round(time.time() - batch_start, 1)
            timer_display.caption(f"Last file: {file_secs}s · Total elapsed: {total_elapsed}s")

    total_elapsed = round(time.time() - batch_start, 1)
    progress.progress(1.0, text="Done")
    status_msg.success(f"Converted {total} file(s) in {total_elapsed}s.")
    timer_display.empty()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.results:
    st.divider()
    st.header("Results")

    # Download all as ZIP (only shown when 2+ files)
    if len(st.session_state.results) > 1:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname, data in st.session_state.results.items():
                if data["markdown"]:
                    zf.writestr(Path(fname).stem + ".md", data["markdown"])
        zip_buf.seek(0)
        st.download_button(
            label="Download All as ZIP",
            data=zip_buf,
            file_name="converted_markdown.zip",
            mime="application/zip",
        )

    st.divider()

    # Per-file tabs
    filenames = list(st.session_state.results.keys())
    tabs = st.tabs(filenames)

    for tab, fname in zip(tabs, filenames):
        data = st.session_state.results[fname]
        with tab:
            duration_note = f" · {data['duration']}s" if "duration" in data else ""
            if data["status"] == "ok":
                st.success(f"Converted successfully{duration_note}")
            elif data["status"] == "partial":
                st.warning(f"Partial conversion — some pages may be missing{duration_note}")
            else:
                st.error(data["status"])

            if data["markdown"]:
                st.download_button(
                    label=f"Download {Path(fname).stem}.md",
                    data=data["markdown"].encode("utf-8"),
                    file_name=Path(fname).stem + ".md",
                    mime="text/markdown",
                    key=f"dl_{fname}",
                )

                col_preview, col_raw = st.columns(2)
                with col_preview:
                    st.subheader("Rendered Preview")
                    st.markdown(data["markdown"])
                with col_raw:
                    st.subheader("Raw Markdown")
                    st.code(data["markdown"], language="markdown")
            else:
                st.error("No output produced for this file.")
