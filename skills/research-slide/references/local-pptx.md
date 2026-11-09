# Editable PPTX authoring

Use the current host presentation workflow and runtime. In Codex, read the installed Presentations skill's implementation, API quick start and finalization instructions. Do not install a competing backend when a bundled one is required. Keep a local build directory and final artifacts separate.

## Optional scene adapter

`scripts/compile_pptx.mjs` uses `@oai/artifact-tool` and `skia-canvas` from the host's runtime modules. Link that runtime's node_modules beside the script in an installed working copy (or use the host-supported module resolution). Never bundle a machine-specific node_modules symlink into a distributed skill.

```
node scripts/compile_pptx.mjs scene.json work/build
```

It renders previews and an editable **draft.pptx**, not an already finalized deliverable. Finalize using the host's checks. Its points-to-pixels conversion is centralized. It registers the complete reference title font locally; verify the title's actual rendering and exported typeface. Do not replace an editable title with a bitmap to mask a missing font. The script is an optional low-level adapter, not an automatic slide designer.

The scene is `{slideSizePt:[720,405], slides:[{id, elements:[...], notes?}]}`. Coordinates and font sizes are **pt**; not inches or CSS px. Elements:

- `text`: x,y,w,h,text; fontFamily,fontSize,color,bold,italic,align,verticalAlign,lineSpacing; optional `runs:[{text,bold?,italic?,fontFamily?,fontSize?,color?}]`. When both text and runs appear their text must agree. Keep mathematical expressions legible; for native math, scripts, rich paragraphs or bullet metadata use direct host authoring rather than flattening semantics into underscores.
- `rect`: x,y,w,h,fill,lineColor,lineWidth. For editable scientific diagrams explicitly requested by the user; never use this adapter to decorate slides with invented component panels.
- `line`: x1,y1,x2,y2,color,width. This subset has no arrowheads; use direct host connectors for attached arrows and complex mechanisms.
- `table`: x,y,w,h,values (rectangular matrix), fontFamily,fontSize,color,lineColor,lineWidth,padding; optional colWidths,rowHeights in pt (must sum to frame), headerRows, fills and cellStyles as rectangular matrices. cellStyles may override fontSize/fontFamily/color/bold/italic/align/fill. There is no automatic “winning” cell selection. Merges are intentionally rejected; use direct native table API for grouped headers, merged model cells or complex spans.
- `image`: x,y,w,h,path,alt. Path resolves relative to scene.json. Keep aspect ratio; use only the actual supplied asset/figure. This adapter embeds local file bytes. It never publishes local/private images to make a Google URL.

The shared subset also compiles to Google requests through `compile_google.py`, whose documented backend limits still apply. Direct host authoring is appropriate when scene limitations would lose important evidence. Do not simplify a required table, equation or diagram just to fit the adapter.

## Two actual export/style failure modes

- Direct Artifact Tool whole-shape text styling uses `typeface`; do not rely on an ignored `fontFamily` key. Apply base style before assigning rich runs so a later `bold:false` whole-shape style does not erase the intended inline emphasis. The bundled helpers handle this order.
- A JSON/proto freeze may retain image references but lose byte payloads. Preserve source assets/payloads across cloning and verify the saved PPTX package has nonempty media and that its reimport render still shows the actual brand/figure. Repairing an export defect does not justify changing scientific content after a blind freeze.

## Render and handoff

Inspect every PNG at readable resolution and check persisted PPTX structure and native editability. Use the host finalizer with the actual slide count, native table/chart owner slides, slide size (720×405pt corresponds to 9144000×5143500 EMU), and reference font policy. After finalization, re-import/render the saved PPTX when supported; a pre-export preview alone is not final-file QA. Differences in unsupported font metrics or math require explicit reporting. Do not claim PowerPoint-native or Google-native validation unless those apps were actually used.
