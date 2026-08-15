#!/usr/bin/env python3
"""Build the revised deck by SURGICAL ZIP EDITING of the user's original file.

Why this approach
-----------------
Re-serialising the whole presentation with python-pptx rewrites every XML part,
including PowerPoint-specific Markup-Compatibility blocks (Morph transitions),
p14/p159 extension lists and other round-trip-fragile constructs. That is what
made PowerPoint refuse the file.

Here we instead keep the user's original package byte-for-byte and replace only
what actually has to change:

  * ppt/slides/slide1.xml      -- swap the feature photo relationship target
  * ppt/slides/slide6.xml      -- methods slide, rebuilt
  * ppt/slides/slide20.xml     -- new Background slide (added)
  * page-number text on the shifted slides (a one-token string substitution)
  * presentation.xml / rels / [Content_Types].xml -- register the new slide

The new slide-6 and slide-20 bodies are produced in an isolated scratch
presentation, then their <p:spTree> payloads are transplanted into a copy of a
known-good slide part from the user's own file. Every slide therefore keeps the
original root element, namespace declarations and MCE transition block exactly
as PowerPoint wrote them.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".build" / "original_user_deck.pptx"
OUT = ROOT / "IITBBS_Impact_Dissipating_Crash_Barrier_Internal_Confidential.pptx"
SCRATCH = ROOT / ".build" / "scratch_content.pptx"

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
P, A, R = (f"{{{NS[k]}}}" for k in ("p", "a", "r"))

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

SLIDE_CT = ("application/vnd.openxmlformats-officedocument"
            ".presentationml.slide+xml")
CHART_CT = "application/vnd.openxmlformats-officedocument.drawingml.chart+xml"
XLSX_CT = ("application/vnd.openxmlformats-officedocument"
           ".spreadsheetml.sheet")
NOTES_CT = ("application/vnd.openxmlformats-officedocument"
            ".presentationml.notesSlide+xml")


# --------------------------------------------------------------------------
def qn(tag: str) -> str:
    pfx, local = tag.split(":")
    return f"{{{NS[pfx]}}}{local}"


def spTree_of(xml_bytes: bytes):
    root = etree.fromstring(xml_bytes)
    return root.find(f"{P}cSld/{P}spTree")


def transplant(donor_slide_xml: bytes, new_spTree) -> bytes:
    """Put `new_spTree` into a copy of `donor_slide_xml`, keeping its shell."""
    root = etree.fromstring(donor_slide_xml)
    cSld = root.find(f"{P}cSld")
    old = cSld.find(f"{P}spTree")
    cSld.replace(old, new_spTree)
    return etree.tostring(root, xml_declaration=True,
                          encoding="UTF-8", standalone=True)


def remap_media_rels(spTree, id_map: dict[str, str]) -> None:
    """Rewrite r:embed / r:id references according to id_map."""
    for el in spTree.iter():
        for attr in (f"{R}embed", f"{R}id", f"{R}link"):
            val = el.get(attr)
            if val is not None and val in id_map:
                el.set(attr, id_map[val])


def strip_ids(spTree) -> None:
    """Renumber cNvPr ids so they are unique and non-zero within the tree."""
    next_id = 2
    for el in spTree.iter():
        if el.tag.endswith("}cNvPr"):
            if el.get("id") == "1":
                continue
            el.set("id", str(next_id))
            next_id += 1


# --------------------------------------------------------------------------
def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing pristine source: {SRC}")
    if not SCRATCH.exists():
        raise SystemExit(f"missing scratch content deck: {SCRATCH}")

    src = ZipFile(SRC)
    scratch = ZipFile(SCRATCH)

    # ---- pull the generated content out of the scratch deck ---------------
    # scratch slide 1 = Background, scratch slide 2 = Methods
    bg_tree = spTree_of(scratch.read("ppt/slides/slide1.xml"))
    methods_tree = spTree_of(scratch.read("ppt/slides/slide2.xml"))

    # ---- collect scratch media that must travel with them -----------------
    def rels_of(zf, part):
        name = re.sub(r"([^/]+)$", r"_rels/\1.rels", part)
        if name not in zf.namelist():
            return {}
        root = etree.fromstring(zf.read(name))
        return {r.get("Id"): (r.get("Type"), r.get("Target"))
                for r in root.findall(f"{{{REL_NS}}}Relationship")}

    scratch_s1 = rels_of(scratch, "ppt/slides/slide1.xml")
    scratch_s2 = rels_of(scratch, "ppt/slides/slide2.xml")

    out_parts: dict[str, bytes] = {}
    added_media: dict[str, str] = {}   # scratch target -> new media filename

    existing_media = [n for n in src.namelist() if n.startswith("ppt/media/")]
    media_idx = max(
        [int(m.group(1))
         for n in existing_media
         if (m := re.search(r"image(\d+)\.", n))] or [0])

    def import_media(scratch_target: str) -> str:
        """Copy a media part out of the scratch deck; return new filename."""
        nonlocal media_idx
        key = scratch_target
        if key in added_media:
            return added_media[key]
        data = scratch.read("ppt/" + scratch_target.replace("../", ""))
        media_idx += 1
        ext = Path(scratch_target).suffix
        new_name = f"image{media_idx}{ext}"
        out_parts[f"ppt/media/{new_name}"] = data
        added_media[key] = new_name
        return new_name

    # =====================================================================
    # 1. SLIDE 1 -- replace the feature photograph binary in place.
    #    The relationship and the <p:pic> stay exactly as PowerPoint wrote
    #    them; only the JPEG bytes behind the existing rel are swapped.
    # =====================================================================
    s1_rels = rels_of(src, "ppt/slides/slide1.xml")
    # the big picture on slide 1 is image2.jpg (the logo is image1.png)
    hero_rel = None
    for rid, (typ, tgt) in s1_rels.items():
        if "image" in typ and "image1.png" not in tgt:
            hero_rel = tgt
    if hero_rel is None:
        raise SystemExit("could not identify slide-1 hero image relationship")
    hero_part = "ppt/media/" + Path(hero_rel).name

    hero_jpg = (ROOT / ".build" / "fit" / "hero_ai.jpg")
    if not hero_jpg.exists():
        raise SystemExit(f"missing rendered hero image: {hero_jpg}")
    out_parts[hero_part] = hero_jpg.read_bytes()

    # caption text under the picture
    s1 = src.read("ppt/slides/slide1.xml").decode("utf-8")
    s1 = s1.replace(
        "One-third-scale barrier pendulum-impact apparatus",
        "Concept visualisation: instrumented energy-dissipating barrier "
        "(AI-generated illustration)")
    out_parts["ppt/slides/slide1.xml"] = s1.encode("utf-8")

    # =====================================================================
    # 2. SLIDE 6 -- methods overview, rebuilt.
    # =====================================================================
    id_map = {}
    for rid, (typ, tgt) in scratch_s2.items():
        if "image" in typ:
            new_media = import_media(tgt)
            id_map[rid] = f"__NEW__{new_media}"

    # slide6 keeps its own rels file; build a fresh one
    s6_rels_existing = rels_of(src, "ppt/slides/slide6.xml")
    keep = {rid: v for rid, v in s6_rels_existing.items()
            if "slideLayout" in v[0] or "notesSlide" in v[0]
            or ("image" in v[0] and "image1.png" in v[1])}

    rel_xml = [f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               f'<Relationships xmlns="{REL_NS}">']
    n = 0
    keep_new = {}     # original slide-6 rId -> new rId
    final_map = {}    # scratch rId          -> new rId
    for rid, (typ, tgt) in keep.items():
        n += 1
        new_rid = f"rId{n}"
        keep_new[rid] = (new_rid, typ, tgt)
        rel_xml.append(f'<Relationship Id="{new_rid}" Type="{typ}" Target="{tgt}"/>')
    for rid, placeholder in id_map.items():
        n += 1
        new_rid = f"rId{n}"
        media = placeholder.replace("__NEW__", "")
        final_map[rid] = new_rid
        rel_xml.append(
            f'<Relationship Id="{new_rid}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="../media/{media}"/>')
    rel_xml.append("</Relationships>")
    out_parts["ppt/slides/_rels/slide6.xml.rels"] = "".join(rel_xml).encode()

    remap_media_rels(methods_tree, final_map)

    # The kept furniture (logo picture) still references the ORIGINAL rel ids,
    # so remap those too, using the same old->new mapping.
    keep_map = {rid: final_map[rid] for rid in keep if rid in final_map}

    # Keep the user's own header/footer furniture on slide 6 (including the
    # yellow "Arrow: Pentagon" marker they added) and replace only the body.
    donor = etree.fromstring(src.read("ppt/slides/slide6.xml"))
    donor_tree = donor.find(f"{P}cSld/{P}spTree")
    KEEP = ("Rectangle 1", "Rectangle 4", "Picture 5", "Connector 6",
            "Connector 7", "TextBox 2", "TextBox 3", "TextBox 8", "TextBox 9")
    for sp in list(donor_tree):
        if sp.tag in (f"{P}nvGrpSpPr", f"{P}grpSpPr"):
            continue
        nv = sp.find(f".//{P}cNvPr")
        name = nv.get("name") if nv is not None else ""
        if name in KEEP or "Pentagon" in name:
            continue
        donor_tree.remove(sp)

    # Fix the kept furniture's own image reference: the logo must point at the
    # relationship that still targets image1.png in the NEW rels file.
    logo_rid = next(new_rid for (new_rid, typ, tgt) in keep_new.values()
                    if "image" in typ and "image1.png" in tgt)
    # donor_tree currently holds ONLY the kept furniture (body not yet added),
    # so every picture here is the logo.
    for pic in donor_tree.iter(f"{P}pic"):
        blip = pic.find(f".//{A}blip")
        if blip is not None:
            blip.set(f"{R}embed", logo_rid)

    # append the freshly drawn body shapes (skip the scratch slide's own
    # header furniture, which duplicates what we just kept)
    SKIP = {"Rectangle 1", "Rectangle 4", "Picture 5", "Connector 6",
            "Connector 7", "TextBox 2", "TextBox 3", "TextBox 8", "TextBox 9"}
    body_shapes = []
    for sp in list(methods_tree):
        if sp.tag in (f"{P}nvGrpSpPr", f"{P}grpSpPr"):
            continue
        nv = sp.find(f".//{P}cNvPr")
        if nv is not None and nv.get("name") in SKIP:
            continue
        body_shapes.append(sp)

    for sp in body_shapes:
        donor_tree.append(sp)

    strip_ids(donor_tree)
    out_parts["ppt/slides/slide6.xml"] = etree.tostring(
        donor, xml_declaration=True, encoding="UTF-8", standalone=True)

    # =====================================================================
    # 3. NEW BACKGROUND SLIDE  -> ppt/slides/slide20.xml, shown at position 2
    # =====================================================================
    bg_map = {}
    bg_rel_lines = []
    n = 0

    # layout + the logo image, taken from an existing slide
    s2_rels = rels_of(src, "ppt/slides/slide2.xml")
    for rid, (typ, tgt) in s2_rels.items():
        if "slideLayout" in typ or ("image" in typ and "image1.png" in tgt):
            n += 1
            bg_rel_lines.append(
                f'<Relationship Id="rId{n}" Type="{typ}" Target="{tgt}"/>')
            for srid, (st, stg) in scratch_s1.items():
                if "image" in st and "image1" in stg and "image" in typ:
                    bg_map[srid] = f"rId{n}"

    # chart part from the scratch deck
    chart_rid = None
    for srid, (typ, tgt) in scratch_s1.items():
        if "chart" in typ:
            chart_src = "ppt/" + tgt.replace("../", "")
            chart_xml = scratch.read(chart_src)
            # embedded workbook for the chart
            crels = rels_of(scratch, chart_src)
            wb_target = None
            for _, (ct, ctg) in crels.items():
                if "package" in ct:
                    wb_target = ctg
            out_parts["ppt/charts/chart12.xml"] = chart_xml
            if wb_target:
                wb_src = "ppt/" + wb_target.replace("../", "")
                out_parts["ppt/embeddings/Microsoft_Excel_Sheet1.xlsx"] = \
                    scratch.read(wb_src)
                out_parts["ppt/charts/_rels/chart12.xml.rels"] = (
                    f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    f'<Relationships xmlns="{REL_NS}">'
                    f'<Relationship Id="rId1" '
                    f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/package" '
                    f'Target="../embeddings/Microsoft_Excel_Sheet1.xlsx"/>'
                    f'</Relationships>').encode()
            n += 1
            chart_rid = f"rId{n}"
            bg_map[srid] = chart_rid
            bg_rel_lines.append(
                f'<Relationship Id="{chart_rid}" '
                f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart" '
                f'Target="../charts/chart12.xml"/>')

    out_parts["ppt/slides/_rels/slide20.xml.rels"] = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{REL_NS}">' + "".join(bg_rel_lines) +
        "</Relationships>").encode()

    remap_media_rels(bg_tree, bg_map)
    strip_ids(bg_tree)
    # donor shell = slide2 of the original (same layout, has the MCE block)
    bg_slide = transplant(src.read("ppt/slides/slide2.xml"), bg_tree)
    out_parts["ppt/slides/slide20.xml"] = bg_slide

    # =====================================================================
    # 4. Page numbers: slides 2..19 shift up by one.
    # =====================================================================
    for i in range(2, 20):
        part = f"ppt/slides/slide{i}.xml"
        data = out_parts.get(part, src.read(part)).decode("utf-8")
        old, new = f"<a:t>{i:02d}</a:t>", f"<a:t>{i + 1:02d}</a:t>"
        data = data.replace(old, new, 1)
        out_parts[part] = data.encode("utf-8")

    # =====================================================================
    # 5. Register the new slide in presentation.xml + rels + content types
    # =====================================================================
    pres_rels = etree.fromstring(src.read("ppt/_rels/presentation.xml.rels"))
    used = [int(m.group(1))
            for r in pres_rels.findall(f"{{{REL_NS}}}Relationship")
            if (m := re.match(r"rId(\d+)$", r.get("Id")))]
    new_rid = f"rId{max(used) + 1}"
    el = etree.SubElement(pres_rels, f"{{{REL_NS}}}Relationship")
    el.set("Id", new_rid)
    el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/"
                   "relationships/slide")
    el.set("Target", "slides/slide20.xml")
    out_parts["ppt/_rels/presentation.xml.rels"] = etree.tostring(
        pres_rels, xml_declaration=True, encoding="UTF-8", standalone=True)

    pres = etree.fromstring(src.read("ppt/presentation.xml"))
    lst = pres.find(f"{P}sldIdLst")
    ids = [int(s.get("id")) for s in lst]
    node = etree.SubElement(lst, f"{P}sldId")
    node.set("id", str(max(ids) + 1))
    node.set(f"{R}id", new_rid)
    lst.remove(node)
    lst.insert(1, node)            # show it as slide 2
    out_parts["ppt/presentation.xml"] = etree.tostring(
        pres, xml_declaration=True, encoding="UTF-8", standalone=True)

    ct = etree.fromstring(src.read("[Content_Types].xml"))
    have = {o.get("PartName") for o in ct.findall(f"{{{CT_NS}}}Override")}
    for part, cty in [("/ppt/slides/slide20.xml", SLIDE_CT),
                      ("/ppt/charts/chart12.xml", CHART_CT)]:
        if part in have or f"/ppt{part}" in have:
            continue
        o = etree.SubElement(ct, f"{{{CT_NS}}}Override")
        o.set("PartName", part)
        o.set("ContentType", cty)
    exts = {d.get("Extension").lower() for d in ct.findall(f"{{{CT_NS}}}Default")}
    if "xlsx" not in exts:
        d = etree.SubElement(ct, f"{{{CT_NS}}}Default")
        d.set("Extension", "xlsx")
        d.set("ContentType", XLSX_CT)
    out_parts["[Content_Types].xml"] = etree.tostring(
        ct, xml_declaration=True, encoding="UTF-8", standalone=True)

    # =====================================================================
    # 6. Write the package, preserving original entry order.
    # =====================================================================
    tmp = OUT.with_suffix(".tmp.pptx")
    with ZipFile(tmp, "w", ZIP_DEFLATED) as out:
        for info in src.infolist():
            data = out_parts.pop(info.filename, None)
            out.writestr(info, src.read(info.filename) if data is None else data)
        for name, data in out_parts.items():
            out.writestr(name, data)
    shutil.move(tmp, OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
