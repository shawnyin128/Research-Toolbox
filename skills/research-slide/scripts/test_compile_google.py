#!/usr/bin/env python3
"""Offline behavior tests; they do not establish Google render fidelity."""
import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from compile_google import compile_scene, SceneError


def scene(*elements):
    return {"slideSizePt":[720,405],"slides":[{"id":"test-slide","elements":list(elements)}]}


def find(body, key):
    return [r[key] for r in body["requests"] if key in r]


def textbox(**kwargs):
    return {"type":"text","x":20,"y":20,"w":300,"h":60,"text":"Hello",**kwargs}


def table(**kwargs):
    return {"type":"table","x":20,"y":90,"w":300,"h":60,"values":[["Name","Value"],["A",0]],**kwargs}


class CompilerTests(unittest.TestCase):
    def test_utf16_ranges_do_not_split_surrogate_pair(self):
        body,_=compile_scene(scene(textbox(text="A🧪中B",runs=[{"text":"A"},{"text":"🧪","bold":True},{"text":"中B","color":"FF0000"}])))
        ranges=[r["textRange"] for r in find(body,"updateTextStyle") if r["textRange"]["type"]=="FIXED_RANGE"]
        self.assertEqual(ranges,[{"type":"FIXED_RANGE","startIndex":1,"endIndex":3},{"type":"FIXED_RANGE","startIndex":3,"endIndex":5}])
        self.assertEqual(find(body,"insertText")[0]["text"],"A🧪中B")

    def test_native_table_cell_order_geometry_and_style(self):
        body,manifest=compile_scene(scene(table(colWidths=[180,120],rowHeights=[20,40],headerRows=1,
            fills=[[None,"EEEEEE"],["FFFFFF",None]],cellStyles=[[None,None],[None,{"bold":True,"align":"right"}]])))
        self.assertEqual(len(find(body,"createTable")),1)
        self.assertEqual(find(body,"createTable")[0]["rows"],2)
        self.assertEqual(find(body,"createShape"),[])
        self.assertEqual([x["text"] for x in find(body,"insertText")],["Name","Value","A","0"])
        self.assertEqual([x["tableColumnProperties"]["columnWidth"]["magnitude"] for x in find(body,"updateTableColumnProperties")],[180,120])
        styles=find(body,"updateTextStyle")
        self.assertEqual([x["style"]["bold"] for x in styles],[True,True,False,True])
        self.assertEqual(find(body,"updatePageElementTransform")[0]["transform"]["translateY"],90)
        self.assertTrue(any("minimums" in x for x in manifest["warnings"]))

    def test_empty_fills_and_no_border_are_not_rendered(self):
        body,_=compile_scene(scene({"type":"rect","x":2,"y":2,"w":10,"h":10,"fill":"","lineColor":None},table(fill=None,lineColor="none")))
        self.assertEqual(find(body,"updateShapeProperties")[0]["shapeProperties"]["shapeBackgroundFill"],{"propertyState":"NOT_RENDERED"})
        border=find(body,"updateTableBorderProperties")[0]["tableBorderProperties"]
        self.assertNotIn("propertyState",border)
        self.assertEqual(border["tableBorderFill"]["solidFill"]["alpha"],0)
        self.assertTrue(all(x["tableCellProperties"]["tableCellBackgroundFill"]=={"propertyState":"NOT_RENDERED"} for x in find(body,"updateTableCellProperties")))

    def test_line_transform_maps_both_endpoints_nonsingular(self):
        lines=[]
        for endpoints in [(10,10,100,10),(20,20,20,200),(200,100,10,20),(10,100,200,20)]:
            lines.append({"type":"line",**dict(zip(("x1","y1","x2","y2"),endpoints))})
        body,_=compile_scene(scene(*lines))
        for el,request in zip(lines,find(body,"createLine")):
            tf=request["elementProperties"]["transform"]
            self.assertAlmostEqual(tf["translateX"],el["x1"])
            self.assertAlmostEqual(tf["translateY"],el["y1"])
            self.assertAlmostEqual(tf["translateX"]+tf["scaleX"]+tf["shearX"],el["x2"])
            self.assertAlmostEqual(tf["translateY"]+tf["shearY"]+tf["scaleY"],el["y2"])
            self.assertNotEqual(tf["scaleX"]*tf["scaleY"]-tf["shearX"]*tf["shearY"],0)

    def test_url_is_preserved_without_network_or_upload(self):
        url="https://example.org/authorized-image.png"
        body,manifest=compile_scene(scene({"type":"image","x":1,"y":1,"w":50,"h":50,"url":url}))
        self.assertEqual(find(body,"createImage")[0]["url"],url)
        self.assertEqual(manifest["status"],"compiled-offline-not-rendered")
        self.assertEqual(len(manifest["warnings"]),1)

    def test_missing_and_nonhttps_urls_rejected(self):
        for url in [None,"","data:image/png;base64,AAA","file:///private/source.png","/tmp/image.png","http://example.org/a.png","https://user:secret@example.org/a.png"]:
            el={"type":"image","x":1,"y":1,"w":50,"h":50}
            if url is not None:el["url"]=url
            with self.subTest(url=url),self.assertRaises(SceneError):compile_scene(scene(el))

    def test_bad_numbers_and_bounds_rejected(self):
        for kwargs in [{"x":-1},{"y":-1},{"w":0},{"h":-1},{"x":float("nan")},{"w":float("inf")},{"fontSize":True},{"fontSize":0},{"x":700,"w":50},{"y":400,"h":10}]:
            with self.subTest(kwargs=kwargs),self.assertRaises(SceneError):compile_scene(scene(textbox(**kwargs)))

    def test_bad_color_font_and_style_rejected(self):
        for kwargs in [{"color":"red"},{"bold":"true"},{"fontFamily":""},{"align":"diagonal"},{"baselineOffset":"RAISED"}]:
            with self.subTest(kwargs=kwargs),self.assertRaises(SceneError):compile_scene(scene(textbox(**kwargs)))

    def test_merged_and_ragged_tables_explicitly_rejected(self):
        for kwargs in [{"mergeCells":[[0,0,1,2]]},{"merged":True},{"values":[[{"text":"A","colSpan":2},"B"]]},{"values":[["A","B"],["C"]]}]:
            with self.subTest(kwargs=kwargs),self.assertRaises(SceneError):compile_scene(scene(table(**kwargs)))

    def test_invalid_table_sizes_fills_and_overrides_rejected(self):
        for kwargs in [{"colWidths":[20,280]},{"colWidths":[100,100]},{"rowHeights":[20,20]},{"headerRows":3},{"headerRows":True},{"fills":[[None]]},{"cellStyles":[[{},{}],[{}, {"rowSpan":2}]]},{"values":[[True,"B"]]}]:
            with self.subTest(kwargs=kwargs),self.assertRaises(SceneError):compile_scene(scene(table(**kwargs)))

    def test_controls_pua_mismatched_runs_rejected(self):
        for kwargs in [{"text":"A\x00B"},{"text":"A\ue000B"},{"text":"A\rB"},{"text":"A","runs":[{"text":"B"}]}]:
            with self.subTest(kwargs=kwargs),self.assertRaises(SceneError):compile_scene(scene(textbox(**kwargs)))

    def test_empty_table_cell_no_insert_but_styles_remain(self):
        body,_=compile_scene(scene(table(values=[[None,""],["A",0]])))
        self.assertEqual(len(find(body,"insertText")),2)
        self.assertEqual(len(find(body,"updateTextStyle")),4)

    def test_revision_namespaced_ids_and_nonmutation(self):
        original=scene(textbox(),table());saved=copy.deepcopy(original)
        body,manifest=compile_scene(original,"private_2","freshRevision")
        self.assertEqual(original,saved)
        self.assertEqual(body["writeControl"],{"requiredRevisionId":"freshRevision"})
        creates=[x[key]["objectId"] for x in body["requests"] for key in ("createSlide","createShape","createTable") if key in x]
        self.assertEqual(len(set(creates)),3)
        self.assertTrue(all(x.startswith("private_2_") for x in creates))
        self.assertNotIn("deleteObject",json.dumps(body))
        self.assertEqual(manifest["expectedSlideSizePt"],[720,405])

    def test_duplicate_logical_ids_rejected(self):
        s=scene(textbox(id="same"),textbox(id="same"))
        with self.assertRaises(SceneError):compile_scene(s)
        s=scene();s["slides"].append(copy.deepcopy(s["slides"][0]))
        with self.assertRaises(SceneError):compile_scene(s)

    def test_shared_style_defaults_are_stable(self):
        body,_=compile_scene(scene(textbox(),table(),{"type":"line","x1":1,"y1":2,"x2":20,"y2":2}))
        ts=find(body,"updateTextStyle")
        self.assertEqual(ts[0]["style"]["fontSize"]["magnitude"],14)
        self.assertEqual(ts[1]["style"]["fontSize"]["magnitude"],10)
        self.assertEqual(find(body,"updateParagraphStyle")[1]["style"]["alignment"],"CENTER")
        self.assertEqual(find(body,"updateTableBorderProperties")[0]["tableBorderProperties"]["weight"]["magnitude"],0.5)
        self.assertEqual(find(body,"updateLineProperties")[0]["lineProperties"]["weight"]["magnitude"],0.6)

    def test_cli_writes_api_body_and_separate_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root);(p/"scene.json").write_text(json.dumps(scene(textbox())),encoding="utf-8")
            cp=subprocess.run([sys.executable,str(Path(__file__).with_name("compile_google.py")),str(p/"scene.json"),str(p/"out.json"),"--manifest",str(p/"manifest.json")],capture_output=True,text=True)
            self.assertEqual(cp.returncode,0,cp.stderr)
            self.assertEqual(set(json.loads((p/"out.json").read_text())),{"requests"})
            self.assertEqual(json.loads((p/"manifest.json").read_text())["status"],"compiled-offline-not-rendered")

    def test_cli_invalid_input_writes_no_batch(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root);(p/"scene.json").write_text(json.dumps(scene(textbox(w=-1))),encoding="utf-8")
            cp=subprocess.run([sys.executable,str(Path(__file__).with_name("compile_google.py")),str(p/"scene.json"),str(p/"out.json")],capture_output=True,text=True)
            self.assertEqual(cp.returncode,2)
            self.assertFalse((p/"out.json").exists())


if __name__=="__main__":unittest.main(verbosity=2)
