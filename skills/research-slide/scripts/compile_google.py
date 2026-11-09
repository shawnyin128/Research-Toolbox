#!/usr/bin/env python3
"""Compile a point-coordinate slide scene to an OFFLINE Google Slides batch body.

No network, credentials, uploads, or account mutation. See references/google-slides.md.
Run: python compile_google.py scene.json requests.json --manifest manifest.json
"""
import argparse
import json
import math
import re
from pathlib import Path
from urllib.parse import urlparse


class SceneError(ValueError):
    """An unsupported or invalid scene; nothing should be sent to Google."""


def fail(where, message):
    raise SceneError(f"{where}: {message}")


def fields(obj, allowed, where):
    if not isinstance(obj, dict):
        fail(where, "expected an object")
    unknown = set(obj) - set(allowed)
    if unknown:
        fail(where, "unsupported field(s): " + ", ".join(sorted(unknown)))


def number(v, where, positive=False, nonnegative=False):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        fail(where, "expected a finite number")
    if positive and v <= 0:
        fail(where, "must be > 0")
    if nonnegative and v < 0:
        fail(where, "must be >= 0")
    return v


def integer(v, where, minimum=0):
    if isinstance(v, bool) or not isinstance(v, int) or v < minimum:
        fail(where, f"expected an integer >= {minimum}")
    return v


def text(v, where):
    if not isinstance(v, str):
        fail(where, "expected a string")
    if re.search(r"[\x00-\x08\x0c-\x1f\ue000-\uf8ff\ud800-\udfff]", v):
        fail(where, "text contains a character Google strips or an unpaired surrogate")
    return v


def utf16_len(s):
    return len(s.encode("utf-16-le")) // 2


def color(v, where, allow_none=False):
    if allow_none and (v is None or v == "" or v == "none"):
        return None
    if not isinstance(v, str) or not re.fullmatch(r"#?[0-9a-fA-F]{6}", v):
        fail(where, "expected six-digit RGB hex" + (" or null/''/'none'" if allow_none else ""))
    v = v.lstrip("#")
    return {k: int(v[i:i+2], 16) / 255 for k, i in (("red", 0), ("green", 2), ("blue", 4))}


def fill(v, where):
    rgb = color(v, where, allow_none=True)
    if rgb is None:
        return {"propertyState": "NOT_RENDERED"}
    return {"propertyState": "RENDERED", "solidFill": {"color": {"rgbColor": rgb}, "alpha": 1}}


def dim(n):
    return {"magnitude": n, "unit": "PT"}


def transform(x, y):
    return {"scaleX": 1, "scaleY": 1, "shearX": 0, "shearY": 0,
            "translateX": x, "translateY": y, "unit": "PT"}


def element_properties(page_id, x, y, w, h):
    return {"pageObjectId": page_id, "size": {"width": dim(w), "height": dim(h)},
            "transform": transform(x, y)}


def rect_geometry(el, size, where):
    x, y = (number(el.get(k), f"{where}.{k}", nonnegative=True) for k in ("x", "y"))
    w, h = (number(el.get(k), f"{where}.{k}", positive=True) for k in ("w", "h"))
    if x + w > size[0] + 1e-6 or y + h > size[1] + 1e-6:
        fail(where, "element bounding box is outside slideSizePt")
    return x, y, w, h


TEXT_STYLE_KEYS = {"fontSize", "fontFamily", "color", "bold", "italic", "underline", "baselineOffset"}
PARA_KEYS = {"align", "lineSpacing", "spaceAbove", "spaceBelow"}
BASE_STYLE = {"fontSize": 14, "fontFamily": "Arial", "color": "333333", "bold": False,
              "italic": False, "underline": False, "baselineOffset": "NONE"}


def google_text_style(style, where):
    out = {}
    if "fontSize" in style:
        out["fontSize"] = dim(number(style["fontSize"], where + ".fontSize", positive=True))
    if "fontFamily" in style:
        family = text(style["fontFamily"], where + ".fontFamily")
        if not family.strip():
            fail(where, "fontFamily must not be empty")
        out["fontFamily"] = family
    if "color" in style:
        out["foregroundColor"] = {"opaqueColor": {"rgbColor": color(style["color"], where + ".color")}}
    for k in ("bold", "italic", "underline"):
        if k in style:
            if not isinstance(style[k], bool):
                fail(where + "." + k, "expected a boolean")
            out[k] = style[k]
    if "baselineOffset" in style:
        if style["baselineOffset"] not in ("NONE", "SUPERSCRIPT", "SUBSCRIPT"):
            fail(where + ".baselineOffset", "expected NONE, SUPERSCRIPT or SUBSCRIPT")
        out["baselineOffset"] = style["baselineOffset"]
    return out


def google_para_style(style, where):
    align = style.get("align", "left")
    if align not in ("left", "center", "right", "justify"):
        fail(where + ".align", "expected left, center, right or justify")
    return {"alignment": {"left": "START", "center": "CENTER", "right": "END", "justify": "JUSTIFIED"}[align],
            "lineSpacing": number(style.get("lineSpacing", 100), where + ".lineSpacing", positive=True),
            "spaceAbove": dim(number(style.get("spaceAbove", 0), where + ".spaceAbove", nonnegative=True)),
            "spaceBelow": dim(number(style.get("spaceBelow", 0), where + ".spaceBelow", nonnegative=True))}


def emit_text(requests, object_id, content, style, where, cell=None, runs=None):
    """One insertion followed by ranges in UTF-16; cell text uses its own indices."""
    target = {"objectId": object_id}
    if cell is not None:
        target["cellLocation"] = cell
    if content:
        requests.append({"insertText": {**target, "insertionIndex": 0, "text": content}})
    ts = google_text_style({**BASE_STYLE, **{k: v for k, v in style.items() if k in TEXT_STYLE_KEYS}}, where)
    requests.append({"updateTextStyle": {**target, "textRange": {"type": "ALL"}, "style": ts,
                                          "fields": ",".join(ts)}})
    ps = google_para_style(style, where)
    requests.append({"updateParagraphStyle": {**target, "textRange": {"type": "ALL"}, "style": ps,
                                               "fields": ",".join(ps)}})
    offset = 0
    for i, run in enumerate(runs or []):
        # All strings have already been validated before any range is calculated.
        end = offset + utf16_len(run["text"])
        rs = google_text_style({k: v for k, v in run.items() if k in TEXT_STYLE_KEYS}, f"{where}.runs[{i}]")
        if end > offset and rs:
            requests.append({"updateTextStyle": {**target,
                "textRange": {"type": "FIXED_RANGE", "startIndex": offset, "endIndex": end},
                "style": rs, "fields": ",".join(rs)}})
        offset = end


def content_and_runs(el, where):
    runs = el.get("runs")
    if runs is None:
        return text(el.get("text", ""), where + ".text"), None
    if not isinstance(runs, list):
        fail(where + ".runs", "expected a list of text/style objects")
    for i, run in enumerate(runs):
        fields(run, {"text"} | TEXT_STYLE_KEYS, f"{where}.runs[{i}]")
        text(run.get("text"), f"{where}.runs[{i}].text")
        google_text_style(run, f"{where}.runs[{i}]")
    joined = "".join(r["text"] for r in runs)
    if "text" in el and text(el["text"], where + ".text") != joined:
        fail(where, "text must equal concatenated runs when both are provided")
    return joined, runs


def scalar(v, where):
    if v is None:
        return ""
    if isinstance(v, str):
        return text(v, where)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        number(v, where)
        return str(v)
    fail(where, "table values must be string, finite number or null; no cell objects/merges")


def matrix(v, rows, cols, where):
    if not isinstance(v, list) or len(v) != rows or any(not isinstance(r, list) or len(r) != cols for r in v):
        fail(where, f"expected a rectangular {rows} x {cols} matrix")
    return v


def compile_scene(scene, prefix="rslides", required_revision_id=None):
    """Return an API batchUpdate body plus a local-only manifest; never sends it."""
    fields(scene, {"slideSizePt", "slides", "title"}, "scene")
    if not re.fullmatch(r"[a-zA-Z0-9_][a-zA-Z0-9_:-]{0,19}", prefix):
        fail("prefix", "use 1–20 characters: alphanumerics/_ first, then alphanumerics/_/:-")
    size = scene.get("slideSizePt", [720, 405])
    if not isinstance(size, list) or len(size) != 2:
        fail("slideSizePt", "expected [width,height] in points")
    for i, n in enumerate(size):
        number(n, f"slideSizePt[{i}]", positive=True)
    slides = scene.get("slides")
    if not isinstance(slides, list) or not slides:
        fail("slides", "expected a nonempty list")
    requests, mapping, warnings, logical_ids = [], [], [], set()
    for si, slide in enumerate(slides):
        where = f"slides[{si}]"
        fields(slide, {"id", "elements", "background"}, where)
        sid = text(slide.get("id"), where + ".id")
        if not sid or sid in logical_ids:
            fail(where + ".id", "must be a nonempty, unique logical ID")
        logical_ids.add(sid)
        page_id = f"{prefix}_s{si+1:04d}"
        requests.append({"createSlide": {"objectId": page_id}})  # omitted layout means BLANK
        bg = color(slide.get("background", "FFFFFF"), where + ".background")
        requests.append({"updatePageProperties": {"objectId": page_id,
            "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": bg}, "alpha": 1}}},
            "fields": "pageBackgroundFill"}})
        mapping.append({"sceneId": sid, "objectId": page_id, "elements": []})
        elements = slide.get("elements")
        if not isinstance(elements, list):
            fail(where + ".elements", "expected a list")
        element_ids = set()
        for ei, el in enumerate(elements):
            ew = f"{where}.elements[{ei}]"
            if not isinstance(el, dict):
                fail(ew, "expected an element object")
            kind = el.get("type")
            if kind not in ("text", "rect", "line", "table", "image"):
                fail(ew + ".type", "supported types: text, rect, line, table, image")
            logical_id = text(el.get("id", f"element-{ei+1}"), ew + ".id")
            if not logical_id or logical_id in element_ids:
                fail(ew + ".id", "must be nonempty and unique within slide")
            element_ids.add(logical_id)
            obj_id = f"{page_id}_e{ei+1:04d}"
            mapping[-1]["elements"].append({"sceneId": logical_id, "objectId": obj_id, "type": kind})
            common = {"type", "id", "x", "y", "w", "h"}
            if kind == "line":
                fields(el, {"type", "id", "x1", "y1", "x2", "y2", "color", "width"}, ew)
                x1,y1,x2,y2 = [number(el.get(k), ew + "." + k, nonnegative=True) for k in ("x1","y1","x2","y2")]
                if max(x1,x2) > size[0] or max(y1,y2) > size[1]:
                    fail(ew, "line endpoint outside slideSizePt")
                dx,dy=x2-x1,y2-y1
                if math.hypot(dx,dy) < 1e-8:
                    fail(ew, "line must have distinct endpoints")
                # A non-singular transform of unit-square diagonal (0,0)->(1,1).
                # No zero dimensions or singular matrix for horizontal/vertical lines.
                tf={"scaleX":(dx-dy)/2,"shearX":(dx+dy)/2,
                    "shearY":(dy+dx)/2,"scaleY":(dy-dx)/2,
                    "translateX":x1,"translateY":y1,"unit":"PT"}
                requests.append({"createLine": {"objectId":obj_id,"category":"STRAIGHT",
                    "elementProperties":{"pageObjectId":page_id,"size":{"width":dim(1),"height":dim(1)},"transform":tf}}})
                lp={"lineFill":{"solidFill":{"color":{"rgbColor":color(el.get("color","555555"),ew+".color")},"alpha":1}},
                    "weight":dim(number(el.get("width",0.6),ew+".width",positive=True)),
                    "dashStyle":"SOLID","startArrow":"NONE","endArrow":"NONE"}
                requests.append({"updateLineProperties":{"objectId":obj_id,"lineProperties":lp,"fields":",".join(lp)}})
                continue
            x,y,w,h=rect_geometry(el,size,ew)
            ep=element_properties(page_id,x,y,w,h)
            if kind in ("text","rect"):
                allowed=common | ({"text","runs","verticalAlign"} | TEXT_STYLE_KEYS | PARA_KEYS if kind=="text" else {"fill","lineColor","lineWidth"})
                fields(el,allowed,ew)
                requests.append({"createShape":{"objectId":obj_id,"shapeType":"TEXT_BOX" if kind=="text" else "RECTANGLE","elementProperties":ep}})
                props={"shapeBackgroundFill":fill(el.get("fill"),ew+".fill"),"outline":{"propertyState":"NOT_RENDERED"}}
                if kind=="rect":
                    lc=color(el.get("lineColor"),ew+".lineColor",allow_none=True)
                    lw=number(el.get("lineWidth",0),ew+".lineWidth",nonnegative=True)
                    if lc is not None and lw>0:
                        props["outline"]={"propertyState":"RENDERED","outlineFill":{"solidFill":{"color":{"rgbColor":lc},"alpha":1}},"weight":dim(lw),"dashStyle":"SOLID"}
                else:
                    va=el.get("verticalAlign","top")
                    if va not in ("top","middle","bottom"):
                        fail(ew+".verticalAlign","expected top, middle or bottom")
                    props["contentAlignment"]={"top":"TOP","middle":"MIDDLE","bottom":"BOTTOM"}[va]
                    props["autofit"]={"autofitType":"NONE"}
                requests.append({"updateShapeProperties":{"objectId":obj_id,"shapeProperties":props,"fields":",".join(props)}})
                if kind=="text":
                    content,runs=content_and_runs(el,ew)
                    emit_text(requests,obj_id,content,el,ew,runs=runs)
            elif kind=="image":
                fields(el,common | {"url"},ew)
                url=el.get("url")
                if not isinstance(url,str) or not url:
                    fail(ew+".url","Google image needs an explicitly supplied public HTTPS URL; no local path upload is performed")
                parsed=urlparse(url)
                if parsed.scheme!="https" or not parsed.netloc or parsed.username or parsed.password or len(url.encode("utf-8"))>2048:
                    fail(ew+".url","expected HTTPS URL <= 2048 bytes without embedded credentials; local/data/file URLs are unsupported")
                requests.append({"createImage":{"objectId":obj_id,"url":url,"elementProperties":ep}})
                warnings.append(f"{ew}: URL reachability, permissions, file format/size and aspect fit require authorized Google insertion/readback.")
            else:
                fields(el,common | {"values","fontSize","fontFamily","color","bold","italic","underline","baselineOffset","align","lineSpacing","spaceAbove","spaceBelow","colWidths","rowHeights","headerRows","fills","cellStyles","fill","lineColor","lineWidth"},ew)
                vals=el.get("values")
                if not isinstance(vals,list) or not vals or not isinstance(vals[0],list) or not vals[0]:
                    fail(ew+".values","expected a nonempty rectangular matrix")
                nr,nc=len(vals),len(vals[0]);matrix(vals,nr,nc,ew+".values")
                values=[[scalar(v,f"{ew}.values[{r}][{c}]") for c,v in enumerate(row)] for r,row in enumerate(vals)]
                cw=el.get("colWidths",[w/nc]*nc);rh=el.get("rowHeights",[h/nr]*nr)
                for arr,length,total,key in ((cw,nc,w,"colWidths"),(rh,nr,h,"rowHeights")):
                    if not isinstance(arr,list) or len(arr)!=length:
                        fail(ew+"."+key,f"expected {length} point sizes")
                    for k,n in enumerate(arr):number(n,f"{ew}.{key}[{k}]",positive=True)
                    if not math.isclose(sum(arr),total,abs_tol=1e-4,rel_tol=0):
                        fail(ew+"."+key,f"sum must equal {'w' if key=='colWidths' else 'h'}")
                if min(cw)<32:
                    fail(ew+".colWidths","Google native table columns must be >=32pt; choose another layout or retain native import path")
                headers=integer(el.get("headerRows",0),ew+".headerRows")
                if headers>nr:fail(ew+".headerRows","cannot exceed row count")
                fills=matrix(el["fills"],nr,nc,ew+".fills") if "fills" in el else None
                cells=matrix(el["cellStyles"],nr,nc,ew+".cellStyles") if "cellStyles" in el else None
                requests.append({"createTable":{"objectId":obj_id,"rows":nr,"columns":nc,"elementProperties":ep}})
                # Explicit final translation avoids relying on initial centering behavior.
                requests.append({"updatePageElementTransform":{"objectId":obj_id,"applyMode":"ABSOLUTE","transform":transform(x,y)}})
                for c,n in enumerate(cw):
                    requests.append({"updateTableColumnProperties":{"objectId":obj_id,"columnIndices":[c],"tableColumnProperties":{"columnWidth":dim(n)},"fields":"columnWidth"}})
                for r,n in enumerate(rh):
                    requests.append({"updateTableRowProperties":{"objectId":obj_id,"rowIndices":[r],"tableRowProperties":{"minRowHeight":dim(n)},"fields":"minRowHeight"}})
                border_color=color(el.get("lineColor","999999"),ew+".lineColor",allow_none=True)
                border_width=number(el.get("lineWidth",0.5),ew+".lineWidth",nonnegative=True)
                # TableBorderProperties has no propertyState (unlike cell/shape fills).
                # Explicit transparent SolidFill removes borders without an invalid field.
                bp={"tableBorderFill":{"solidFill":{"color":{"rgbColor":{"red":0,"green":0,"blue":0}},"alpha":0}},"weight":dim(0.5),"dashStyle":"SOLID"}
                if border_color is not None and border_width>0:
                    bp={"tableBorderFill":{"solidFill":{"color":{"rgbColor":border_color},"alpha":1}},"weight":dim(border_width),"dashStyle":"SOLID"}
                requests.append({"updateTableBorderProperties":{"objectId":obj_id,"borderPosition":"ALL","tableBorderProperties":bp,"fields":",".join(bp)}})
                for r in range(nr):
                    for c in range(nc):
                        loc={"rowIndex":r,"columnIndex":c}
                        cs={} if cells is None or cells[r][c] is None else cells[r][c]
                        fields(cs,TEXT_STYLE_KEYS | PARA_KEYS | {"fill"},f"{ew}.cellStyles[{r}][{c}]")
                        style={"fontSize":10,"color":"000000","align":"center",**{k:v for k,v in el.items() if k in TEXT_STYLE_KEYS | PARA_KEYS}}
                        if r<headers:style["bold"]=True
                        style.update(cs)
                        emit_text(requests,obj_id,values[r][c],style,f"{ew}.cell[{r},{c}]",cell=loc)
                        fv=el.get("fill","FFFFFF")
                        if fills is not None:fv=fills[r][c]
                        if "fill" in cs:fv=cs["fill"]
                        requests.append({"updateTableCellProperties":{"objectId":obj_id,
                            "tableRange":{"location":loc,"rowSpan":1,"columnSpan":1},
                            "tableCellProperties":{"tableCellBackgroundFill":fill(fv,f"{ew}.fill[{r},{c}]"),"contentAlignment":"MIDDLE"},
                            "fields":"tableCellBackgroundFill,contentAlignment"}})
                warnings.append(f"{ew}: rowHeights are Google minimums; native rows can grow for text. Verify rendered bounds and fit online.")
    body={"requests":requests}
    if required_revision_id is not None:
        if not isinstance(required_revision_id,str) or not required_revision_id:
            fail("required_revision_id","expected a nonempty revision ID from a fresh native read")
        body["writeControl"]={"requiredRevisionId":required_revision_id}
    manifest={"schema":"research-slides-scene-v1","status":"compiled-offline-not-rendered",
              "expectedSlideSizePt":size,"objectIdPrefix":prefix,"objects":mapping,
              "requestCount":len(requests),"warnings":warnings,
              "preconditions":["Read destination pageSize and confirm it matches expectedSlideSizePt; no request here changes page size.",
                               "Use only an authorized host route; compilation grants no online write or public upload permission.",
                               "Check generated object IDs do not exist; repeated submission is not idempotent.",
                               "Preserve unrelated pages. This batch only appends new slides and their objects."]}
    return body,manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path);parser.add_argument("output",type=Path)
    parser.add_argument("--manifest",type=Path);parser.add_argument("--prefix",default="rslides")
    parser.add_argument("--revision-id",help="Fresh requiredRevisionId; no credentials/network used")
    args=parser.parse_args()
    try:
        scene=json.loads(args.input.read_text(encoding="utf-8-sig"))
        body,manifest=compile_scene(scene,args.prefix,args.revision_id)
        if args.output.resolve()==args.input.resolve():fail("output","must not overwrite input scene")
        if args.manifest and args.manifest.resolve() in (args.input.resolve(),args.output.resolve()):
            fail("manifest","must differ from input and output")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(body,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
        if args.manifest:
            args.manifest.parent.mkdir(parents=True,exist_ok=True)
            args.manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
        print(json.dumps({"status":manifest["status"],"slides":len(scene["slides"]),"requests":len(body["requests"]),"warnings":len(manifest["warnings"])},ensure_ascii=False))
    except (SceneError,ValueError,OSError) as exc:
        parser.exit(2,f"compile_google: {exc}\n")


if __name__=="__main__":
    main()
