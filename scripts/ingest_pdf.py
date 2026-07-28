#!/usr/bin/env python3
"""
ULTRON — reference ingestion utility.

Files a PDF supplied by the Master into the repository knowledge base:
  1. copies it to  docs/references/<slugified-name>.pdf
  2. extracts text to  docs/notes/<slug>.txt        (if pypdf is installed)
  3. creates a note stub  docs/notes/<slug>.md      (for the distilled summary)
  4. registers it in  docs/references/INDEX.md

Usage
-----
    python3 scripts/ingest_pdf.py paper.pdf
    python3 scripts/ingest_pdf.py paper.pdf --tag geopolymer --tag SLWA
    python3 scripts/ingest_pdf.py *.pdf --tag literature

Dependency-light: works without pypdf (skips text extraction and says so).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REF_DIR = REPO / "docs" / "references"
NOTE_DIR = REPO / "docs" / "notes"
INDEX = REF_DIR / "INDEX.md"

INDEX_HEADER = """# Reference Index

All source documents supplied by **MASTER AARKASON** or gathered by ULTRON.
Maintained automatically by `scripts/ingest_pdf.py`.

| # | Document | Added | Pages | Tags | Notes | SHA-256 (short) |
|---|---|---|---|---|---|---|
"""


def slugify(name: str) -> str:
    s = re.sub(r"[^\w\s-]", "", Path(name).stem).strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s) or "document"


def sha256_short(path: Path, n: int = 10) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def extract_text(pdf: Path, out_txt: Path) -> int | None:
    """Extract text -> out_txt. Returns page count, or None if pypdf is unavailable."""
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None
    reader = PdfReader(str(pdf))
    parts = []
    for i, page in enumerate(reader.pages, 1):
        try:
            body = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001 - never abort ingestion on one bad page
            body = f"[extraction failed: {exc}]"
        parts.append(f"\n\n===== PAGE {i} =====\n{body}")
    out_txt.write_text("".join(parts), encoding="utf-8")
    return len(reader.pages)


NOTE_TEMPLATE = """# {title}

- **Source file:** `docs/references/{pdf_name}`
- **Raw text:** `docs/notes/{slug}.txt`
- **Ingested:** {date}
- **Tags:** {tags}

> ULTRON distillation. Terse & technical; reasoning only where mandatory.

## 1. Objective of the work
_TBD_

## 2. Materials / mix design
_TBD_

## 3. Methodology (experimental / numerical)
_TBD_

## 4. Key quantitative results
| Quantity | Value | Unit | Note |
|---|---|---|---|
| | | | |

## 5. Modelling parameters extractable for our FEM
| Parameter | Symbol | Value | Unit | Source (page/table) |
|---|---|---|---|---|
| | | | | |

## 6. Limitations / gaps
_TBD_

## 7. Relevance to this project
_TBD_
"""


def ingest(pdf_path: Path, tags: list[str], force: bool) -> None:
    if not pdf_path.is_file():
        sys.exit(f"[ULTRON] ERROR: not a file -> {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        print(f"[ULTRON] WARNING: {pdf_path.name} is not a .pdf — filing anyway.")

    REF_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)

    slug = slugify(pdf_path.name)
    dest = REF_DIR / f"{slug}{pdf_path.suffix.lower()}"
    if dest.exists() and not force:
        print(f"[ULTRON] Already filed: {dest.relative_to(REPO)} (use --force to overwrite)")
    else:
        shutil.copy2(pdf_path, dest)
        print(f"[ULTRON] Filed  -> {dest.relative_to(REPO)}")

    digest = sha256_short(dest)
    pages = extract_text(dest, NOTE_DIR / f"{slug}.txt")
    if pages is None:
        print("[ULTRON] pypdf not installed -> text extraction skipped "
              "(`pip install pypdf` to enable).")
        pages_str = "?"
    else:
        print(f"[ULTRON] Text   -> docs/notes/{slug}.txt  ({pages} pages)")
        pages_str = str(pages)

    note_md = NOTE_DIR / f"{slug}.md"
    if not note_md.exists():
        note_md.write_text(
            NOTE_TEMPLATE.format(
                title=pdf_path.stem,
                pdf_name=dest.name,
                slug=slug,
                date=_dt.date.today().isoformat(),
                tags=", ".join(f"`{t}`" for t in tags) or "_untagged_",
            ),
            encoding="utf-8",
        )
        print(f"[ULTRON] Note   -> docs/notes/{slug}.md (stub)")

    # --- update index -------------------------------------------------------
    if not INDEX.exists():
        INDEX.write_text(INDEX_HEADER, encoding="utf-8")
    text = INDEX.read_text(encoding="utf-8")
    if f"`{dest.name}`" in text:
        print("[ULTRON] Index already contains this document.")
        return
    n = sum(1 for ln in text.splitlines() if ln.startswith("| ") and ln[2:3].isdigit()) + 1
    row = (f"| {n} | [`{dest.name}`](./{dest.name}) | {_dt.date.today().isoformat()} "
           f"| {pages_str} | {', '.join(tags) or '—'} "
           f"| [note](../notes/{slug}.md) | `{digest}` |\n")
    INDEX.write_text(text.rstrip("\n") + "\n" + row, encoding="utf-8")
    print(f"[ULTRON] Index  -> {INDEX.relative_to(REPO)} (entry #{n})")


def main() -> None:
    ap = argparse.ArgumentParser(description="ULTRON PDF ingestion into the knowledge base.")
    ap.add_argument("pdfs", nargs="+", type=Path, help="PDF file(s) to ingest")
    ap.add_argument("--tag", action="append", default=[], help="tag (repeatable)")
    ap.add_argument("--force", action="store_true", help="overwrite if already filed")
    args = ap.parse_args()

    print("=" * 60)
    print(" ULTRON — REFERENCE INGESTION")
    print("=" * 60)
    for p in args.pdfs:
        ingest(p, args.tag, args.force)
        print("-" * 60)
    print("[ULTRON] Done, MASTER AARKASON.")


if __name__ == "__main__":
    main()
