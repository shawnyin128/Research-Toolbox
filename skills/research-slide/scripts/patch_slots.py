"""Compile native Slides text edits without rebuilding the surrounding objects.

python patch_slots.py page.json edits.json > requests.json
Each edit has objectId, before, after and optionally cellLocation.
The caller supplies a fresh page resource and applies the result to a working copy.
"""

import json
import sys
from pathlib import Path


def utf16_length(value):
    return len(value.encode("utf-16-le")) // 2


def collect(elements):
    for element in elements:
        yield element
        yield from collect(element.get("elementGroup", {}).get("children", []))


def compile_requests(page, edits):
    objects = {obj["objectId"]: obj for obj in collect(page["pageElements"])}
    requests = []
    used = set()
    for edit in edits:
        object_id = edit["objectId"]
        obj = objects[object_id]
        target = {"objectId": object_id}
        location = edit.get("cellLocation")
        if location is None:
            text = obj["shape"]["text"]
        else:
            row, col = location["rowIndex"], location["columnIndex"]
            if row < 0 or col < 0:
                raise ValueError("Negative cell index")
            # Merged cells can omit covered columns from tableCells.
            cells = obj["table"]["tableRows"][row]["tableCells"]
            cell = next((c for j, c in enumerate(cells)
                         if c.get("location", {}).get("columnIndex", j) == col), None)
            if cell is None:
                raise ValueError("Address the upper-left anchor of a merged cell")
            text = cell["text"]
            target["cellLocation"] = location
        key = (object_id, tuple(sorted((location or {}).items())))
        if key in used:
            raise ValueError("Submit each shape or cell once per readback")
        used.add(key)
        runs = text["textElements"]
        if any("autoText" in run for run in runs):
            raise ValueError("Leave automatic fields intact")
        content = "".join(run.get("textRun", {}).get("content", "") for run in runs)
        before, after = edit["before"], edit["after"]
        if any(c in before + after for c in "\r\n"):
            raise ValueError("Edit one paragraph at a time, preserving its native break")
        if not before or content.count(before) != 1:
            raise ValueError(f"Expected one exact match in {object_id}")
        start = utf16_length(content[:content.index(before)])
        end = start + utf16_length(before)
        if before == after:
            continue
        offset = 0
        styles = []
        for run in runs:
            token = run.get("textRun", {})
            limit = offset + utf16_length(token.get("content", ""))
            if offset < end and limit > start:
                styles.append(token.get("style", {}))
            offset = limit
        if any(style != styles[0] for style in styles[1:]):
            raise ValueError("Split an edit that crosses native text styles")
        # Keep the first original character as a style anchor during insertion.
        # For mixed-style paragraphs submit a single contiguous, uniform-style span.
        anchor_len = utf16_length(before[0])
        if after:
            requests.append({"insertText": {**target, "insertionIndex": start + anchor_len, "text": after}})
        shift = utf16_length(after)
        if end > start + anchor_len:
            requests.append({"deleteText": {**target, "textRange": {
                "type": "FIXED_RANGE", "startIndex": start + anchor_len + shift, "endIndex": end + shift}}})
        requests.append({"deleteText": {**target, "textRange": {
            "type": "FIXED_RANGE", "startIndex": start, "endIndex": start + anchor_len}}})
    return requests


if __name__ == "__main__":
    page, edits = [json.loads(Path(path).read_text(encoding="utf-8-sig")) for path in sys.argv[1:]]
    print(json.dumps(compile_requests(page, edits), ensure_ascii=True))
