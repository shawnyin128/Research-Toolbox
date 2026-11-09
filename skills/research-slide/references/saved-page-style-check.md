# Fresh check of saved-page style fidelity

Use a new critic after saving and rendering the actual delivery file. Give only this guide, that file's PNG, the selected author's full-page reference and its geometry measurements, and minimal intended `argumentRole`/`audience`. Exclude old reviews, other families, approved copy drafts and full facts/provenance. The critic judges the actual page, not the plan or a memory of an earlier preview.

Compare hierarchy and coupled type scales; prose/object footprint and placement; ordinary notes, nested clauses and emphasis cadence; and independence of the scientific object's own labels, typography and topology. Check whether explanatory sentences, glossary tiers, repeated framing, or resized objects changed the selected author's rhythm. Keep legitimate current scientific differences separate from style mismatches. No preference question and no cleaner/larger-is-better score.

Return only genuine mismatches with a visible location, selected-reference evidence, and owner (`layout` or `copy`). If none are supported, return an empty mismatch list. Do not rewrite the page or invent scientific corrections from the author reference. Owning stages repair their artifacts; then save and render again.

A separate fresh science reader next receives the repaired actual render and raw authorized scientific record. That reader checks recoverability, scope, uncertainty, exact data/assets and newly introduced mappings. The style critic's narrow packet cannot perform this check. Both are internal QA; neither substitutes for the final frozen blind attribution test.

Build the isolated packet with `make_stage_packet.py style-check --saved-page saved.png --intent intent.json --family selected-family --out empty-directory`. `intent.json` contains only `argumentRole` and `audience`; extra fields are discarded. The script records saved/reference file hashes but cannot establish that a caller's PNG came from the final saved artifact. The caller must supply that render.
