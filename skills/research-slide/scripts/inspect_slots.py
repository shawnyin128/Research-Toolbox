"""Describe the scientific content slots on a native Google Slides page.

Pass two page JSON files for a before/after comparison. Duplicate-page edits
may preserve roles but change object IDs; use the sorted output to match them.
Nested groups are reported as groups, so their local coordinates are never
misreported as page coordinates.
"""

import json
import sys
from pathlib import Path


def pt(value, unit):
    return value / 12700 if unit == "EMU" else value


def length(d):
    return pt(d.get("magnitude", 0), d.get("unit", "PT"))


def describe(el):
    transform = el.get("transform", {})
    unit = transform.get("unit", "PT")
    size = el.get("size", {})
    w, h = (length(size.get(k, {})) for k in ("width", "height"))
    if "table" in el:
        cols = [length(k.get("columnWidth", {})) for k in el["table"].get("tableColumns", [])]
        rows = [length(k.get("rowHeight", {})) for k in el["table"].get("tableRows", [])]
        if cols and all(cols):
            w = sum(cols)
        if rows and all(rows):
            h = sum(rows)
    a, b = transform.get("scaleX", 1), transform.get("shearX", 0)
    c, d = transform.get("shearY", 0), transform.get("scaleY", 1)
    x, y = (pt(transform.get(k, 0), unit) for k in ("translateX","translateY"))
    corners = [(x + a*u + b*v, y + c*u + d*v) for u,v in ((0,0),(w,0),(0,h),(w,h))]
    xs, ys = zip(*corners)
    kind = next((k for k in ("table","shape","image","sheetsChart","line","elementGroup","wordArt") if k in el), "other")
    item = {"id":el["objectId"], "kind":kind,
            "bounds_pt":[round(z,1) for z in (min(xs),min(ys),max(xs),max(ys))]}
    if kind == "table":
        item["grid"] = [el[kind]["rows"],el[kind]["columns"]]
    if kind == "shape":
        elems = el[kind].get("text",{}).get("textElements",[])
        item["text"] = "".join(e.get("textRun",{}).get("content","") for e in elems).strip()[:90]
        item["paragraphs"] = sum("paragraphMarker" in e for e in elems)
    if kind == "elementGroup":
        item["child_count"] = len(el[kind]["children"])
    return item


if __name__ == "__main__":
    for name in sys.argv[1:]:
        page = json.loads(Path(name).read_text(encoding="utf-8-sig"))
        slots = sorted(map(describe,page["pageElements"]),key=lambda s:(s["bounds_pt"][1],s["bounds_pt"][0]))
        print(json.dumps({"file":name,"slots":slots},ensure_ascii=True))
