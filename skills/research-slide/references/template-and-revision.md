# Template following and revision

1. Inspect the current editable deck and its rendered slides. Treat the latest user-edited deck as the source of truth. Do not assume a prior build script includes manual edits.
2. Preserve the original. Create a versioned working copy unless the user explicitly requests editing the existing cloud deck in place. For template-based creation, copy the template before authoring.
3. Extract a design inventory: canvas, master/layout families, fonts, colors, text hierarchy, margins, object geometry, media slots, tables, notes, links, and protected regions. Use the destination's template parser when available.
4. Map each output slide to an exemplar by narrative role, evidence type, density, and meaningful slots. Record every exemplar image, chart, portrait, or mockup as keep, replace, or delete. Remove unused groups and stale captions together.
5. Prefer duplicating an appropriate rich exemplar over rebuilding its native objects. Preserve paragraph and run formatting, object types, grouping, notes, links, and intrinsic media proportions. Edit native tables and charts in place where supported.
6. Finalize structural operations in the sequence required by the backend. Verify every intended slide ID occurs exactly once in the final order. Avoid editing shared chart parts accidentally when duplicating slides.
7. Preserve manual font, position, wording, and sizing changes. For a major rebuild, compare the current deck with the generated one and explicitly carry forward user changes. Never regenerate from a stale script and silently discard them.
8. Use a tested native or OOXML-aware editing tool when needed. Preserve relationships, content types, namespaces, notes, media, and chart dependencies. Do not copy slide XML alone or assume loading with one library proves PowerPoint compatibility.
9. Fit complete scientific figures, charts, and screenshots inside their frame. Crop only when meaning is preserved. Shorten flexible wording or select a better exemplar before reducing type size.
10. Re-render and inspect final output. Check for stale template content, mixed formatting lost during replacement, orphaned visuals, stretched figures, missing links/notes, and unwanted template-library slides.

Creating an installable visual template from a particular reference is a separate operation. Invoke the current Template Creator workflow only when the user asks for that reusable artifact template and supplies or selects a concrete reference. Do not label this workflow skill as a reference-backed gallery template.
