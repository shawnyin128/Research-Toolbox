# Recovery contract — v2 extension

FACT freezes scientific truth; LAYOUT chooses where a reader recovers it; COPY writes only assigned wording. Atomic scientific completeness does not imply one sentence per fact. Public facts normally use `delivery: recoverable`. Retain explicit `visible_text`/`visible_label` only for an actual user requirement; do not infer them from source paragraphs. Keep existing exact data strings and asset hashes. Scientific scope and uncertainty remain obligations.

A same-case `stage: layout` contract has stable `slots` (list of `{id, ...}` or object keyed by id), plus:

```json
{
  "objects": [
    {"id":"topic", "kind":"title", "locator":"page/title", "slotId":"title"},
    {"id":"results", "kind":"table", "locator":"page/lower-table", "evidenceRef":"values"}
  ],
  "recovery": [
    {"factId":"comparison", "witnesses":[
      {"objectId":"topic", "locator":"page/title", "slotId":"title"},
      {"objectId":"results", "locator":"page/lower-table", "evidenceLocator":"columns[2]"}
    ]}
  ]
}
```

Object kinds: `title`, `header`, `table`, `math`, `diagram`, `asset`, `prose`, `label`. `locator` identifies its planned page location and must match in each witness. An object either assigns a `slotId` to COPY, references exact frozen `evidenceRef`, or freezes visible `text` (e.g. a formal equation or diagram label). Do not freeze text in a copy-owned object. A table's `evidenceLocator` is `whole`, `columns[N]`, or `rows[R][C]`, zero-based; an asset uses a precise readable region description. Metadata alone is not audience-visible evidence. Layout must ensure the chosen headers/labels/math or joint surfaces actually deliver that meaning.

Map every public fact, including `evidence_only`, exactly once in `recovery`; several facts may share an object, and one fact may need several objects. Private/context records have no recovery entry. Explicit `visible_label` uses an actual label/header/math/diagram surface; explicit text obligations cannot be discharged only by an unquoted asset. Existing v2 explicit-delivery contracts without this extension remain readable, but any `recoverable` fact requires the map.

COPY supplies `coverage: [{factId, witnesses:[...]}]`, repeating every planned witness identity (`objectId`, `locator`, optional `slotId`, optional `evidenceLocator`). Text witnesses add a `quote` occurring in actual slot text or the layout object's frozen `text`. Each copy slot names its assigned `factIds`. Evidence witnesses repeat the planned locator without inventing a quote. Joint coverage is intentional: a method title plus metric headers plus exact table rows can establish a comparison without an English inventory of columns. No copy outside approved slots; no new prose assignment to private/context/evidence-only records.

For an introduced symbol without an authorized prior definition, add a coverage-level `mapping`:

```json
{"symbolWitness":0,"symbolSpan":[5,6],"meaningWitness":0,"meaningSpan":[0,4]}
```

Offsets are zero-based/end-exclusive within witness quotes; this example locates `S` and `Sink` in `Sink(S)`. Symbol and meaning must be distinct visible spans; a letter hidden inside a word is invalid. Canonical upstream meaning may be “sink window”: semantic review decides whether the actual local label is equivalent in context. A formal definition such as `z := x + y` can define a quantity through mathematical syntax; no full English paraphrase is required. For an existing mapping legible inside a frozen asset, `mapping: {evidenceWitness: N}` points to a precise planned definition region; do not invent an asset quote or duplicate its labels. Table header/cell mapping spans index their exact source string when the witness has no copy quote. These forms still require independent visible semantic review. The reviewer checks actual definitional meaning, dimensional consistency and whether genuinely new local notation is recoverable. Familiar domain abbreviations and established conventions need no manufactured glossary.

Run `python scripts/validate_contracts.py facts.json --layout layout.json --copy copy.json`. It checks planned surfaces, witnesses, table locator bounds and separation; it cannot prove entailment, absence of unsupported prose, or legibility. A fresh reader must inspect the actual saved render against raw science after repairs. Do not treat a pass, an ID, a heading, or two related nouns as scientific verification.
