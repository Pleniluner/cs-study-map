"""Bounded, non-executing text extraction; full text stays in ignored storage."""

import io
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import PurePosixPath
from xml.etree import ElementTree

from .storage import StudyError

EXTRACTOR_VERSION = "1"


def redact(text):
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[邮箱已省略]", text)
    text = re.sub(r"(?<!\d)(?:20\d{8}|1[3-9]\d{9})(?!\d)", "[个人编号已省略]", text)
    text = re.sub(r"(?i)(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}", "[凭据已省略]", text)
    return text.replace("\x00", "")


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def decode_text(data):
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise StudyError("text-encoding-unsupported")


def extract(path, data, max_chars=10000, max_pages=8):
    ext = PurePosixPath(path).suffix.lower()
    raw = []
    partial = False
    if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise StudyError("git-lfs-pointer-not-content")
    if ext == ".pdf":
        from pypdf import PdfReader
        try:
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                raise StudyError("encrypted-pdf")
            partial = len(reader.pages) > max_pages
            for i, page in enumerate(reader.pages[:max_pages]):
                raw.append((f"p{i + 1}", f"PDF 第 {i + 1} 页", page.extract_text() or ""))
        except StudyError:
            raise
        except Exception:
            raise StudyError("pdf-extraction-failed") from None
    elif ext in {".docx", ".pptx"}:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                entries = archive.infolist()
                if len(entries) > 5000 or sum(i.file_size for i in entries) > 64_000_000:
                    raise StudyError("office-archive-size-limit")
                if ext == ".docx":
                    names = ["word/document.xml"]
                else:
                    names = sorted((n for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)), key=lambda n: int(re.search(r"(\d+)\.xml", n).group(1)))
                for i, name in enumerate(names[:max_pages]):
                    node = ElementTree.fromstring(archive.read(name))
                    text = "\n".join(e.text for e in node.iter() if e.tag.endswith("}t") and e.text)
                    locator = "Word 正文" if ext == ".docx" else f"幻灯片 {i + 1}"
                    raw.append((f"section{i + 1}", locator, text))
                partial = len(names) > max_pages
        except StudyError:
            raise
        except Exception:
            raise StudyError("office-extraction-failed") from None
    elif ext == ".ipynb":
        try:
            notebook = json.loads(decode_text(data))
            for i, cell in enumerate(notebook.get("cells", [])):
                if cell.get("cell_type") in {"markdown", "code"}:
                    source = cell.get("source", [])
                    raw.append((f"cell{i + 1}", f"Notebook 单元 {i + 1}", "".join(source) if isinstance(source, list) else source))
        except Exception:
            raise StudyError("notebook-extraction-failed") from None
    else:
        text = decode_text(data)
        if ext in {".html", ".htm"}:
            parser = VisibleHTML()
            parser.feed(text)
            raw = [("html", "HTML 可见文本", "\n".join(parser.parts))]
        else:
            lines = text.splitlines()
            for i in range(0, len(lines), 40):
                raw.append((f"L{i + 1}-L{min(i + 40, len(lines))}", f"第 {i + 1}–{min(i + 40, len(lines))} 行", "\n".join(lines[i:i + 40])))
    segments = []
    remaining = max_chars
    for identifier, locator, text in raw:
        text = redact(text).strip()
        if not text:
            continue
        if remaining <= 0:
            partial = True
            break
        if len(text) > remaining:
            text = text[:remaining]
            partial = True
        segments.append({"id": identifier, "locator": locator, "text": text})
        remaining -= len(text)
    if sum(len(s["text"].strip()) for s in segments) < 30:
        raise StudyError("insufficient-readable-text-or-scanned-document")
    return {"extractor_version": EXTRACTOR_VERSION, "coverage": "partial" if partial else "extracted-text", "segments": segments}
