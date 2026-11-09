# Select composition by purpose and local series

Use the science-free [family inventory](../author-examples/family-inventory.json) to shortlist two functional candidates without loading every module. Then inspect their images and selected measured records. A chart, a table or token symbols identify an evidence form. They do not identify the page's report intent, prose hierarchy or author period. Select an executable family in this order:

1. **Report intent and object role.** From frozen facts identify what the audience must inspect: a brief experimental readout, a bounded runtime cost, a trend/ablation observation, an intended objective and motivation, one mechanism, a staged progress report, a dense result comparison, or an experimental setup/results account. Identify what each object does in that argument: primary evidence, supporting example, or mechanism to trace. A schematic illustrating a motivation does not become the main teaching task merely because it contains tokens. Retain separate intents only when each has a distinct required scientific object.
2. **Current series and identity.** Use current supplied series cues, established title grammar, deck identity and authorized local analogues. A reference's footer records its provenance. It cannot override the current deck's institution, lab, footer or page numbering. Do not invent an adjacent-page context or inspect unauthorized pages to establish it. When current series is unknown, record that uncertainty and select the closest functional analogue without asserting historical continuity.
3. **Evidence form.** Determine whether the required evidence is a table, plot, operation sequence, mathematical object or independent figure. Check which information is already inside it. Plot conditions and diagram labels do not require a second prose account by default.
4. **Composition.** Compare compatible candidates before freezing the single-family layout packet. A fresh selection packet supplies frozen facts and two candidate images/science-free records; its owner records `caseId`, `selectedExample`, `candidateExamples`, `reportIntent`, `objectRole`, `reason` and `alternativeRejection`. Reject both and request a better pair when neither matches the task. The final layout packet carries that decision; do not silently substitute its preselected analogue. Choose title scale/absence, body scale, scientific-object footprint, note placement, local figure typography and emphasis controls together. A table's internal font does not determine deck-note font. Record the selected starter and why its coupled hierarchy fits. Other author families remain legitimate when supported by purpose and series.
5. **Copy grammar, separately.** Within that composition reserve only justified roles: purpose plus ordinary nested observation, question plus compact summary, short operational bullets, or fuller setup/results sections. Pass these role constraints to copy. Do not import an example's subtitle, Goal/Experiment/Results sections, acronym key, caveat or conclusion solely because its evidence has the same form.

| Current scientific task | Candidate composition | Discriminating question |
|---|---|---|
| Brief experimental readout with one complete scientific figure | [Evidence-led short readout](evidence-led-readout.md), example15; dense-result02 when evidence supplies nearly the entire account | Are the notes only context and a scoped observation? Keep a shallow large-type report band and dominant evidence rather than creating explanatory sidebar capacity. |
| Intended objective and rationale with a supporting example | [Prose-led overview with inset](prose-led-overview.md), example16; report-plus-inset01/11 when their distinct roles fit | Is the schematic subordinate to a nested motivation example, or must the audience trace its mechanism? Preserve the narrative hierarchy and small inset for the former. |
| Brief observation about a trend/repeated operation | [Plot-led runtime observation](plot-led-observation.md), example13 | Does the plot carry the conditions while notes supply only purpose and scoped observations? Reserve the plot first. |
| Fuller experimental account with curves | Existing example09 | Do current facts and series actually require Goal/Experiment/Results roles? A plot alone is insufficient. |
| Bounded runtime cost plus selected configuration | [Runtime focus table](runtime-focus-table.md), example12; plain/green siblings07/10 | Is selection a configuration focus, a metric winner, or both? Choose footprint and emphasis independently from those semantics. |
| One mechanism and concise operational notes | [Compact object plus notes](compact-object.md), example14; examples01/08 where appropriate | Does one self-contained object carry every required relation? Keep its independent local typography and avoid a duplicate abstraction. |
| Staged progress/implementation report | Existing example11 and [workflow](workflow.md) | Does the main report concern completed/pending stages, with an inset that supports those notes? |
| Positional transformation or aligned mathematical objects | Existing examples05/04/08 | Is the task to trace correspondences, rather than report a mechanism beside notes? Token presence cannot decide. |
| Ordered implementation procedure | [Method reports](method-report.md), example22 | Does the actual order plus subordinate implementation detail carry the procedure? Preserve decimal/lettered hierarchy without inventing a flowchart. |
| Paper-reading conceptual method outline | [Method reports](method-report.md), example18 | Are the primary objects a numbered concept outline and independent equations rather than operators to trace? |
| Algorithm premise and operational narrative | [Method reports](method-report.md), example17 | Are plots/local illustration supporting the algorithm report? Keep narrative/inset hierarchy instead of replacing it with a dependency board. |
| Compact scientific method/model/conditions heading with implementation/pending notes | [Scientific status caption](scientific-table.md), example23 | Does one black/sans scientific caption introduce a neutral table and internal status account? Preserve that compact hierarchy without adding a purple topic-title layer. |
| Self-contained scientific table with context caption | [Scientific tables](scientific-table.md), example19;02/15 for their distinct roles | Do grouped headers, condition stubs and a small caption already supply the account? Keep scientific object identity and only current meaningful emphasis. |
| Empirical design notes plus plot and mathematical justification | [Independent plot setup](independent-plot-setup.md), example20;13 for brief runtime observations | Must the audience inspect independent plots and a separate equation object? Retain those objects rather than normalizing them into deck prose. |
| Operator, branch and update dependencies | [Operator graph](operator-graph.md), example21 | Are actual graph relations the scientific task? Preserve topology/path semantics and compact graph/report balance. |
| Dense results or setup/result comparison | Existing examples02/03/06, [experiment](experiment.md) | Is the table the main explanation, or does a distinct setup/diagnosis report need surrounding space? |

The compact object family does not make every mechanism compact; the plot-led family does not make every plotted experiment sparse. Preserve the author's measured readable density and genuine variation. If current facts need another object or more space, adapt minimally and record the reason. Do not average the archive into a uniform slide theme.

Selection output in `layout.json`:

```json
{
  "selection": {
    "reportIntent": "<current scientific task>",
    "seriesEvidence": "<supplied current cues or unknown>",
    "identitySource": "<current deck/user instruction>",
    "evidenceForm": "<required scientific objects>",
    "objectRole": "<primary evidence, supporting illustration, or mechanism to trace>",
    "family": "<selected functional family>",
    "starter": "<one applicable measured record>",
    "reason": "<purpose/series/footprint fit>",
    "copyGrammarConstraints": ["<justified roles and emphasis, no drafted prose>"],
    "excludedAdditions": ["<unneeded duplicate account or inherited section>"]
  }
}
```

A concise note count constrains report load, not merely the number of bullet markers. Two slots can still become an explanatory essay. Plan capacity for required context and scoped observation; retain scientific qualifications and attribution status while avoiding repeated topic, caption and label accounts. If essential facts genuinely exceed that capacity, report the conflict upstream rather than shrink body text or promote an inset without a new scientific task.

Example numbers are inspection addresses, never routing conditions. New facts choose a family by function and current context. No reference experiment values, method list or scientific token counts become defaults.
