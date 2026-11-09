# Follow the local record, including what it does not add

Use the selected functional example, not a uniform “research style.” Read its image and [measured spans](author-examples/measurements-summary.json). ArialMT maps to Arial; FrankRuhlLibre-Bold maps to Frank Ruhl Libre bold. Span bounds are glyph bounds, not recovered textbox bounds; confirm the render.

## Prepare a faithful input record

Keep the actual lab method name, experiment type, model/precision, and preceding-page context when those are available. A method's proper name is scientific information; removing it merely because it appeared in a title can force a generic replacement. A follow-up definition after a format was already introduced need not restart the chapter. Preserve the researcher's working phrases and the relationship between observations and qualifiers. Do not rewrite the raw notes into a polished abstract before authoring.

Source notes can contain figure facts, discussion points and maker instructions. Keep figure facts recoverable in the figure; do not automatically repeat an axis definition or legend entry as another body bullet. Maker guardrails constrain claims rather than becoming visible footnotes. A supplied interpretation remains scoped to its trial.

## Choose the actual paragraph grammar

The archive contains **different** local styles:

- Quantization experiment examples 01/09 use standalone bold role headings such as Idea, Goal, Experiment and Results, followed by ordinary bullets and nested clarifications. This is different from putting a bold prefix inside every bullet.
- Runtime ablation example07 uses ordinary, non-bold body text and normal/nested bullets. Do not add a bold Question/Observation/TLDR label merely to regularize it. A question can simply be a question; a short existing TLDR can remain plain.
- Untitled mechanism example08 lets objects and mathematical labels carry the hierarchy. A definition does not need invented category headers such as Weights/Block scale/Global scale in every prose paragraph. Describe the object directly and subordinate its shade, scope or exception in the ordinary bullet flow.
- Other pages can use inline bold lead-ins. Use them when the matched reference actually does; the presence of a role word in raw notes is not a universal bolding command.

Native `addAuthorBullets` supplies editable levels and run styles; it does not decide which paragraphs should be bold. Use `authorText` for a standalone role heading, and native bullet items below it when appropriate. Keep each selected reference's absence of an extra title, grouping layer, intro paragraph or label. Do not mechanically apply all available components.

## Use exact local sizes

| Example | Title pt | Relevant body/evidence | Task |
|---|---:|---|---|
| 01 |22|prose17; small figure labels|idea/mechanism|
| 02 |27|table10|dense result|
| 03 |25|body13; table10|experimental comparison|
| 04 |36|labels12–16|matrix mechanism|
| 05 |30|labels10–16|positional transformation|
| 06 |24|body14; table10|long runtime diagnostic|
| 07 |36|plain body14; table10|runtime ablation|
| 08 |none|object/math8–11|untitled working mechanism|
| 09 |28|body14|goal/experiment/results and curves|

An ablation in the 07 family should not silently inherit a 28pt deck-wide title. Use the author's compact lab terms and experiment type when choosing a topic title; a descriptive “Ablation study for …” is appropriate to that family, not an obligatory claim headline. Do not shrink 10pt result numerals to fit an extra introduction. Worked vectors are a different evidence level from a dense result table and may need14–16pt digits.

## Scientific abstraction and evidence scale

An untitled page has no freestanding headline, rather than a new black sans-serif substitute. Put small object labels at their objects. If full matrix dimensions are unspecified, use generic matrix corners/ellipsis or a symbolic dimension, and demonstrate one correspondence. The known count of members **within a block** does not specify the number of blocks **in the matrix**. Avoid inventing a complete 3×4 indexed matrix merely to demonstrate a generic storage format. Counting all members is useful only when that counting or bit-field operation is the scientific task.

For a small one-condition runtime comparison, a simple one-row table header may be the author's structure. Grouped tables are appropriate when a sweep or distinct metric families genuinely require them. Do not introduce a new “Share of complete step” header tier solely because a helper can merge cells. Likewise, do not automatically append arrows to familiar metric labels, bold every header/value or add an explanatory label the reference leaves implicit. Preserve the required values and scope with the fewest added layers consistent with the selected example. Emphasize the endpoints of the comparison actually being discussed; do not automatically bold a whole unquantized baseline or every numerical maximum when the research claim compares two other configurations.

## Brand and defects

For new pages in this personal family, use `addAuthorChrome` with the matching explicit SAI/NYU family and reserve its footer regions. Existing chrome remains as actually used. A documented dense-page exception is different from forgetting a footer.

Set evidence size from the functional reference and necessary labels. Do not automatically turn every plot into a larger hero while detaching its working notes into caption-like paragraphs. Keep the record's bullet relationships; avoid repeating information already readable in the figure.

Repair actual lost text, clipped scientific content and footer collisions. Do not manufacture grammar errors or damage to hide authorship. Natural source-style density and line wrapping are allowed when the entire scientific identifier remains readable; a different word break alone is not a reason to redesign a table. Review positive author cues separately from roughness heuristics.

## Measured paragraph geometry is part of the style

Read [paragraph tokens](author-examples/paragraph-tokens.json) before composing lists. Every measured ordinary bullet in the prose examples is a large `●` (U+25CF); nested runtime bullets are `○` (U+25CB). Substituting `•/◦` materially changes the silhouette. Use native bullet metadata with these glyphs, not hand-typed symbols. In example07 a 14pt first-level text start is x71.51pt and its marker starts x45.06pt; the next level advances36pt. The native helper's 36pt left margin/27pt hanging/36pt level increment reproduces this relationship when the textbox starts near x35.5pt. Wrapped text starts at the same x as its first line.

Example07 has continuous19.32pt baseline pitch at14pt (115% over the normal16.8pt pitch), no extra gap after each bullet; example09 has16.8pt pitch at14pt (100%). A sibling item and a wrapped line belong to the same connected flow. Select the actual family instead of making every item an isolated statement. Keep a supplied Observation role as an ordinary top-level item and the recorded observations as its sub-items when that is the matched grammar; do not remove that role merely to shorten the page.

Distinguish prose font from object labels: example08's8–11pt mathematical labels do not prescribe11pt for a neighboring multi-sentence explanation. Use the nearest prose reference's14pt level for sustained notes, adapting width and diagram allocation instead of inheriting tiny object typography.
