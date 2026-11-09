# G/H training expansion provenance

| Added resource | Permitted source | Use |
|---|---|---|
| example-10.png | PDF3 “Cerebras & NYU Weekly Speculative Decoding 2026 Spring .pdf”, page492 (1-based), former development G | Wide-ablation family image |
| example-11.png | PDF2 “Cerebras & NYU Weekly Quantization.pdf”, page662 (1-based), former development H | Summary-plus-inset family image |
| example-11-workflow-detail.png | The embedded296×595 workflow image on the same H page | Inspect local figure grammar, source sharpness and palette |
| measurements-gh.json | The same two pages only | Exact native spans/fonts/baseline origins and geometry; separately labeled raster estimates |
| author-family-layouts.json | Derived from the same measurements | Layout-stage starting records without experiment copy |
| author-family-copy.json | Derived from the same measurements | Copy-stage functional paragraph grammar |

These pages are training/development evidence from this point onward. Do not count them as unseen cases. No additional PDF pages were inspected for this expansion; supporting examples01 and07 were already in the authorized training archive. New held-out target pages and their excluded neighboring experiment pages were not accessed. Source PDF facts/numbers and complete slide rasters are inspection evidence only; never insert a reference slide as a newly authored slide or borrow its experimental result.

Native spans are exact PDF measurements. Table rules/fills are extracted native drawing properties. H diagram dimensions are exact image placement; its font-size range and colors are raster estimates. Area fractions use bounding envelopes/frames, not pixel ink. `author-family-layouts.json` records clipping envelopes explicitly so authoring engines do not confuse glyph bounds, clip frames and text-box padding.
