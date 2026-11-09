# Build and QA

## Select a supported backend

Apply current host routing and use its preferred presentation capability. For standalone PPTX authoring only when the environment permits it, inspect available libraries such as PptxGenJS or Artifact Tool rather than assuming installation. For Google Slides use supported native APIs and the current connector workflow. Do not embed machine-specific paths or request credentials preemptively.

Keep a dedicated task directory containing sources, the slide plan, design tokens, authoring input, and output. Record which source version generated the deck. Resolve reusable tools from their installed packages. This skill does not bundle the upstream renderers, validators, OMML tools, or converters.

## Handle Data report conversion

Use the existing reviewed Data app state and its verified data. Preserve active filters, signed values, population, units, caveats, timestamps, and provenance. Prefer supported native PNG exports of individual charts/cards, with editable surrounding slide structure. Do not use a whole-dashboard screenshot or invent recommendations absent from the source. Rebuild a chart only under the Data workflow's verified fallback rules.

## Check content before rendering

- Verify slide count, order, backup status, titles, notes, evidence mappings, and cited numbers.
- Check formulas and dimensions, chart signs, axes, metric definitions, numerical precision, and sources.
- Remove unresolved placeholders and stale template content. Keep legitimate research TODOs only when explicitly part of the requested progress report and clearly labeled.
- Check object bounds, font availability, native bullet formatting, media paths, and expected editability through supported readback tools.
- For PPTX, use the chosen tool's package/relationship and chart validation. For template-derived files, baseline against the source when supported. Report checks that could not run.

## Inspect actual output

Render the final saved deck through an available presentation renderer or native export, then inspect every slide at readable resolution. Use a contact sheet for consistency and individual renders for text, figures, and equations. A contact sheet or overflow estimator alone is insufficient.

Check text clipping, unintended overlap, crowding, excessive empty regions, inconsistent alignment, faint text, tiny labels, distorted images, missing marks, cropped scientific content, font substitutions, equation rendering, and footer collisions. Check appendix slides too. Preserve intentional overlapping shapes and template-specific exceptions.

Collect concrete defects and repair them in one consolidated pass where practical. Re-render changed slides and verify fixes. After changes to masters, themes, slide order, or structure, inspect a fresh complete render. Stop when supported checks pass and no concrete defect remains. Never invent defects merely to force an edit cycle.

For native equations or renderer substitutions, state when preview fidelity is approximate. Prefer native PowerPoint validation when available without requiring new installation or paid services. If rendering is unavailable, deliver only with an explicit statement that visual QA remains incomplete.

## Deliver

Return the verified file or native deck link through the host's required delivery format. Include visible and backup counts, a brief description, and material limitations. Preserve reproducible inputs and the original. Do not claim file creation, editability, native import, hidden status, validation, installation, or export unless observed.
