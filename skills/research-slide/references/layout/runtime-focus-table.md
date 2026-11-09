# Layout — runtime focus table

Use for a bounded runtime-cost report whose evidence compares configurations and may select an operating configuration. Run the [purpose-first selector](family-selector.md). Inspect example12 and its `runtime-focus-table` record in [focused starters](../author-examples/focused-layout-starters.json).

The local source uses a36pt purple Frank Ruhl Libre Bold experiment-series title, a compact14pt Arial question/summary with ordinary nested observations, then a low broad table. Its table frame is x12.74–674.24,y234.03–333.03pt,91.9% of page width and22.5% of page area. Ten-point Arial table text and16.5pt rows are readable local density. Preserve the deliberate≈65.92pt last-note-to-table gap when the current content fits; do not enlarge the table font or compact the whole page solely for preference.

The source table has white cells, navy bold headers, pale blue.75pt rules, and one gray-filled navy-bold focus row. These are a coherent local variant. Existing black-grid/green-focus and plain black tables remain legitimate siblings. Do not import this palette into every runtime report or replace it automatically with another authentic variant.

Specify independent controls:

- `focusRowIds`: current selected configuration(s), with semantic reason. A focus row may contain nonwinning values.
- `winnerCellIds`: current cells justified by the declared comparison, independently of focus. Empty is valid; this local source has no separately marked winners.
- `focusStyle`, `winnerStyle`, `headerStyle`: separately chosen local visual treatments. A header color does not imply a metric maximum, and row position never establishes focus.

Use the current table's actual columns, row count, precise values and comparison scope. Reference geometry guides scale; its experiment schema and values are not defaults. Keep established current-series title cadence and compact question/summary rhythm when supported. Copy can scope the claim within that rhythm without adding a universal Question/Observation taxonomy, acronym key or conclusion band.
