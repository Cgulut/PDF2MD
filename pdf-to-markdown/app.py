import io
import tempfile
import time
import zipfile
from pathlib import Path

import streamlit as st

from converter import build_converter, build_image_captioner, convert_file

ACCEPTED_TYPES = ["pdf", "docx", "pptx", "html", "htm",
                  "png", "jpg", "jpeg", "tiff", "bmp", "webp"]

MODE_OPTIONS = {
    "Markdown only":                    "md_only",
    "Markdown + Images":                "md_images",
    "Markdown + Images + Descriptions": "md_images_desc",
    "Images only":                      "images_only",
    "Images + Descriptions only":       "images_desc_only",
}

NEEDS_TEXT   = {"md_only", "md_images", "md_images_desc"}
NEEDS_IMAGES = {"md_images", "md_images_desc", "images_only", "images_desc_only"}
NEEDS_BLIP   = {"md_images_desc", "images_desc_only"}

st.set_page_config(
    page_title="Document Converter",
    page_icon="📄",
    layout="wide",
)

st.title("Document Converter")
st.caption("Convert documents to Markdown and extract images · Powered by docling")

# ── Session state init ─────────────────────────────────────────────────────────
# Converter holds ~500 MB of AI models — cached to avoid reload on every rerun.
if "converter" not in st.session_state:
    with st.spinner("Loading AI models — ~30 s on first ever run, ~5 s after that..."):
        st.session_state.converter = build_converter()

if "results" not in st.session_state:
    st.session_state.results = {}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("1. Upload Files")
    uploaded_files = st.file_uploader(
        "PDF, Word, PowerPoint, HTML, or images",
        type=ACCEPTED_TYPES,
        accept_multiple_files=True,
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) selected")
        for f in uploaded_files:
            st.write(f"- {f.name} ({f.size / 1024:.0f} KB)")

    st.divider()
    st.header("2. Choose Mode")
    mode_label = st.radio(
        "What do you want to extract?",
        list(MODE_OPTIONS.keys()),
        label_visibility="collapsed",
    )
    mode = MODE_OPTIONS[mode_label]

    # Load BLIP only when a descriptions mode is selected — avoids 990 MB download otherwise
    if mode in NEEDS_BLIP and "captioner" not in st.session_state:
        with st.spinner("Loading image description model — first run downloads ~990 MB..."):
            st.session_state.captioner = build_image_captioner()
    captioner = st.session_state.get("captioner") if mode in NEEDS_BLIP else None

    st.divider()
    if uploaded_files:
        convert_btn = st.button("Convert All", type="primary", use_container_width=True)
    else:
        convert_btn = False
        st.info("Upload files to get started.")

    st.divider()
    st.caption("Scanned docs use EasyOCR · GPU used automatically if available")

# ── Conversion ─────────────────────────────────────────────────────────────────
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
            # De-duplicate filenames
            if safe_name in seen:
                seen[safe_name] += 1
                stem, suffix = Path(safe_name).stem, Path(safe_name).suffix
                safe_name = f"{stem} ({seen[safe_name]}){suffix}"
            else:
                seen[safe_name] = 0

            status_msg.info(f"Processing {i + 1}/{total}: **{safe_name}**")
            progress.progress(i / total, text=f"File {i + 1} of {total}")

            tmp_path = Path(tmpdir) / safe_name
            tmp_path.write_bytes(uploaded_file.getvalue())

            file_start = time.time()
            markdown, status, images = convert_file(
                st.session_state.converter, tmp_path,
                mode=mode, captioner=captioner,
            )
            file_secs = round(time.time() - file_start, 1)

            st.session_state.results[safe_name] = {
                "markdown": markdown,
                "status":   status,
                "images":   images,
                "duration": file_secs,
                "mode":     mode,
            }

            total_elapsed = round(time.time() - batch_start, 1)
            timer_display.caption(f"Last file: {file_secs}s · Total elapsed: {total_elapsed}s")

    total_elapsed = round(time.time() - batch_start, 1)
    progress.progress(1.0, text="Done")
    status_msg.success(f"Processed {total} file(s) in {total_elapsed}s.")
    timer_display.empty()


# ── Helper: build per-file ZIP ─────────────────────────────────────────────────
def _build_zip(fname: str, data: dict) -> bytes:
    stem = Path(fname).stem
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if data["markdown"]:
            zf.writestr(f"{stem}.md", data["markdown"])
        for img in data.get("images", []):
            zf.writestr(f"images/{img['filename']}", img["bytes"])
    buf.seek(0)
    return buf.getvalue()


# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.results:
    st.divider()
    st.header("Results")

    # "Download All" ZIP for 2+ files — each file in its own subfolder
    if len(st.session_state.results) > 1:
        all_buf = io.BytesIO()
        with zipfile.ZipFile(all_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname, data in st.session_state.results.items():
                stem = Path(fname).stem
                if data["markdown"]:
                    zf.writestr(f"{stem}/{stem}.md", data["markdown"])
                for img in data.get("images", []):
                    zf.writestr(f"{stem}/images/{img['filename']}", img["bytes"])
        all_buf.seek(0)
        st.download_button(
            label="Download All as ZIP",
            data=all_buf,
            file_name="converted_files.zip",
            mime="application/zip",
        )
        st.divider()

    # Per-file tabs
    filenames = list(st.session_state.results.keys())
    tabs = st.tabs(filenames)

    for tab, fname in zip(tabs, filenames):
        data = st.session_state.results[fname]
        file_mode = data.get("mode", "md_only")
        stem = Path(fname).stem
        has_images = bool(data.get("images"))

        with tab:
            # Status badge
            duration_note = f" · {data['duration']}s" if "duration" in data else ""
            if data["status"] == "ok":
                st.success(f"Done{duration_note}")
            elif data["status"] == "partial":
                st.warning(f"Partial — some content may be missing{duration_note}")
            else:
                st.error(data["status"])

            # Download button
            if file_mode == "md_only" and data["markdown"]:
                st.download_button(
                    label=f"Download {stem}.md",
                    data=data["markdown"].encode("utf-8"),
                    file_name=f"{stem}.md",
                    mime="text/markdown",
                    key=f"dl_{fname}",
                )
            elif file_mode in NEEDS_IMAGES:
                st.download_button(
                    label=f"Download {stem}.zip",
                    data=_build_zip(fname, data),
                    file_name=f"{stem}.zip",
                    mime="application/zip",
                    key=f"dl_{fname}",
                )

            # Markdown preview
            if data["markdown"] and file_mode in NEEDS_TEXT:
                col_preview, col_raw = st.columns(2)
                with col_preview:
                    st.subheader("Rendered Preview")
                    st.markdown(data["markdown"])
                with col_raw:
                    st.subheader("Raw Markdown")
                    st.code(data["markdown"], language="markdown")
            elif file_mode in NEEDS_TEXT and not data["markdown"]:
                st.error("No text output produced for this file.")

            # Extracted images
            if has_images:
                st.divider()
                with st.expander(f"Extracted Images ({len(data['images'])})", expanded=True):
                    for img in data["images"]:
                        col_img, col_info = st.columns([1, 2])
                        with col_img:
                            st.image(img["bytes"], caption=img["caption"] or img["ref_id"])
                        with col_info:
                            if img["description"]:
                                st.markdown(f"**Description:** {img['description']}")
                            if img["ocr_text"]:
                                st.markdown(f"**Text in image:** {img['ocr_text']}")
                            if not img["description"] and not img["ocr_text"]:
                                st.caption(
                                    "No description — choose a Descriptions mode for AI analysis"
                                )
            elif file_mode in NEEDS_IMAGES:
                st.info("No embedded images found in this file.")
