#!/usr/bin/env python3
"""Post-save repair pass for PPTX files written by python-pptx.

Two defects are corrected:

1. ``<mc:Fallback xmlns="">``  --  lxml re-serialises the Markup-Compatibility
   fallback of PowerPoint Morph transitions with an empty default namespace.
   That is invalid per the MCE specification (ISO/IEC 29500-3): the children of
   mc:Fallback must stay in the PresentationML namespace. PowerPoint reacts with
   "The file cannot be opened" / a repair prompt. We strip the bogus xmlns="".

2. Notes placeholders written as ``<p:ph type="body" idx="1"/>`` are normalised
   to the ``type="body" sz="quarter" idx="3"`` form used by the notes master in
   this deck, and the sldImg / sldNum placeholders are restored so every notes
   page has the same shape set as the rest of the deck.

The repair is byte-level on the XML parts and rewrites the ZIP container with
the same part order and deflate settings, so nothing else in the package moves.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]

BAD_FALLBACK = re.compile(rb'<mc:Fallback\s+xmlns=""\s*>')

NOTES_PH = re.compile(
    rb'<p:nvPr><p:ph type="body" idx="1"/></p:nvPr>')

SLD_IMG_SP = (
    b'<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image Placeholder 1"/>'
    b'<p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr>'
    b'<p:nvPr><p:ph type="sldImg" idx="2"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp>'
)
SLD_NUM_SP = (
    b'<p:sp><p:nvSpPr><p:cNvPr id="4" name="Slide Number Placeholder 3"/>'
    b'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
    b'<p:nvPr><p:ph type="sldNum" sz="quarter" idx="5"/></p:nvPr></p:nvSpPr>'
    b'<p:spPr/></p:sp>'
)


def fix_fallback(data: bytes) -> tuple[bytes, int]:
    """Remove the invalid empty default namespace on mc:Fallback."""
    data, n = BAD_FALLBACK.subn(b'<mc:Fallback>', data)
    return data, n


def fix_notes(data: bytes) -> tuple[bytes, int]:
    """Bring a synthesised notes page in line with the deck's notes master."""
    if b'<p:ph type="body" idx="1"/>' not in data:
        return data, 0
    data = data.replace(
        b'<p:cNvPr id="2" name="Notes Placeholder 2"/>',
        b'<p:cNvPr id="3" name="Notes Placeholder 2"/>')
    data = NOTES_PH.sub(
        b'<p:nvPr><p:ph type="body" sz="quarter" idx="3"/></p:nvPr>', data)
    # Re-insert the slide-image and slide-number placeholders around the body.
    if b'type="sldImg"' not in data:
        data = data.replace(b'<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/>',
                            SLD_IMG_SP + b'<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/>',
                            1)
    if b'type="sldNum"' not in data:
        data = data.replace(b'</p:spTree>', SLD_NUM_SP + b'</p:spTree>', 1)
    return data, 1


def repair(path: Path) -> dict:
    src = ZipFile(path)
    items = src.infolist()
    payload = {i.filename: src.read(i.filename) for i in items}
    src.close()

    stats = {"fallback": 0, "notes": 0, "parts": 0}
    for name in list(payload):
        if not name.endswith((".xml", ".rels")):
            continue
        data = payload[name]
        original = data
        data, nf = fix_fallback(data)
        stats["fallback"] += nf
        if name.startswith("ppt/notesSlides/notesSlide"):
            data, nn = fix_notes(data)
            stats["notes"] += nn
        if data != original:
            payload[name] = data
            stats["parts"] += 1

    tmp = path.with_suffix(".repaired.pptx")
    with ZipFile(tmp, "w", ZIP_DEFLATED) as out:
        for info in items:
            out.writestr(info, payload[info.filename])
    shutil.move(str(tmp), str(path))
    return stats


def verify(path: Path) -> None:
    z = ZipFile(path)
    assert z.testzip() is None, "corrupt zip"
    import xml.etree.ElementTree as ET
    for name in z.namelist():
        if name.endswith((".xml", ".rels")):
            ET.fromstring(z.read(name))
    leftovers = sum(z.read(n).count(b'<mc:Fallback xmlns="">')
                    for n in z.namelist() if n.endswith(".xml"))
    assert leftovers == 0, f"{leftovers} invalid mc:Fallback remain"
    bad_ph = sum(z.read(n).count(b'<p:ph type="body" idx="1"/>')
                 for n in z.namelist() if n.startswith("ppt/notesSlides/"))
    assert bad_ph == 0, "non-conforming notes placeholder remains"
    print("verify: OK — zip intact, all XML well-formed, no invalid MCE fallback")


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        ROOT / "IITBBS_Impact_Dissipating_Crash_Barrier_Internal_Confidential.pptx")
    s = repair(target)
    print(f"repaired {target.name}: {s['fallback']} mc:Fallback fixes, "
          f"{s['notes']} notes pages normalised, {s['parts']} parts rewritten")
    verify(target)
