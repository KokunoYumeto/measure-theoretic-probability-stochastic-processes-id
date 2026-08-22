# QuantEcon CTMC component plan

Status: authority, rights witness, native editable closure, offline Python
environment, and native HTML/PDF baseline admitted. This component is not yet
translated or admitted into the public reader.

## Authority and format

The translation authority is the native MyST/Jupyter Book Markdown at immutable
commit `8b06e0aa5a438692445b2c896f9d238c5a7d5eb7`, not the generated notebooks
or the 100-page PDF. Generated notebooks are executable/download witnesses;
the PDF is a pagination/render witness. Exact archives, expanded snapshots,
manifests, license HTML, and receipts live under `authority/quantecon`.

The component retains the official-reader CC BY-SA 4.0 witness because the
repository has no root license file. The Indonesian QuantEcon adaptation and
any inseparable additions to its pages use CC BY-SA 4.0. Separately reusable
original course bridges may remain CC BY 4.0. Attribution, change notice,
source link, and non-endorsement are mandatory. QuantEcon logos, social cards,
analytics, Colab launch UI, and theme branding are excluded; the sole selected
content asset is
`lectures/_static/lecture_specific/markov_prop/flow_fig.png`, 104,771 bytes,
SHA-256
`54906c3f6f48664960d25ead98af1150014e88367db1d604f6ccc9d01e50564f`.

## Exact chapter map

| Order | Upstream MyST | Stable unit ID | Exercises / solutions / source cells |
|---:|---|---|---:|
| 1 | `memoryless.md` | `unit.o009.quantecon.ctmc.memoryless-distributions` | 2 / 2 / 5 |
| 2 | `poisson.md` | `unit.o009.quantecon.ctmc.poisson-processes` | 2 / 2 / 7 |
| 3 | `markov_prop.md` | `unit.o009.quantecon.ctmc.markov-property` | 4 / 4 / 5 |
| 4 | `kolmogorov_bwd.md` | `unit.o009.quantecon.ctmc.backward-equations` | 3 / 3 / 6 |
| 5 | `kolmogorov_fwd.md` | `unit.o009.quantecon.ctmc.forward-equations` | 3 / 3 / 6 |
| 6 | `generators.md` | `unit.o009.quantecon.ctmc.semigroups-generators` | 3 / 3 / 0 |
| 7 | `uc_mc_semigroups.md` | `unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups` | 5 / 5 / 0 |
| 8 | `ergodicity.md` | `unit.o009.quantecon.ctmc.stationarity-ergodicity` | 3 / 3 / 4 |

The eight chapters contain 25 exercises, 25 paired solutions, and 33 source
code-cell directives. `status.md` contributes two more source cells, for 35
source cells total. The generated notebooks contain 36 cells because the
`kolmogorov_bwd` solution parameter block becomes a separate notebook cell;
all generated execution counts and outputs are empty. Preserve both censuses
and never present them as contradictory.

The first QuantEcon translation boundary, after the four selected Random
discrete pages, is the complete `memoryless.md` chapter with its two
exercises, two solutions, and five cells. No prose-only fragment is a release
boundary.

## Source and backend design

Keep QuantEcon outside the existing Random `THEORY_UNITS` adapter. Add a
separate component builder that understands MyST directives, labels,
exercises/solutions, notebook cell aliases, and CC BY-SA provenance. Preserve
native labels and directive/formula/code order; assign frozen IDs only where
upstream supplies none. Required backend additions are execution entities,
`executes` relations, QuantEcon source-label and notebook-cell alias
namespaces, environment/notebook/result artifact kinds, and component-specific
code/asset/accessibility/PDF QA events. The published `course.o009` namespace
remains stable even though the curriculum packet's semantics are role O009 /
course D30.

## Environment and execution gate

Extend, never replace, the existing R/Pandoc runtime lock with:

- exact Python/base-runtime hashes and ABI;
- a fully pinned, hash-required dependency lock and wheel manifest;
- package/license inventory;
- `PYTHONHASHSEED=0`, `PYTHONNOUSERSITE=1`, UTC, `MPLBACKEND=Agg`, and
  single-thread numerical settings;
- one fresh kernel per chapter, disabled network, removal of all six
  `!pip install quantecon` network operations from the downstream execution
  layer, explicit seeds for stochastic cells, and no undeclared stderr;
- ordered cell source IDs/hashes, outputs, analytic targets, tolerances, and
  output hashes; and
- a second clean offline replay with the same package resolution and admitted
  result identities.

The frozen source is never edited. Network, branding, accessibility, or
mathematical repairs are downstream correction records.

Native execution is also prohibited inside either frozen snapshot. Upstream
`markov_prop.md` writes its flow figure during execution; the first attempted
baseline therefore changed the copied authority asset and was immediately
rejected. The exact asset was restored from the immutable archive and the full
34-file manifest revalidated. Every subsequent build must start from a newly
created disposable copy of the exact active-input closure and must prove the
frozen authority manifest unchanged both before and after execution.

## Build and QA gate

`scripts/build_quantecon_component.py` will validate translated MyST against
authority, execute under the locked environment into a temporary component
stage, produce component HTML/notebooks/manifest/receipt, and reject symlinks,
path escapes, external runtime, analytics, branding, undeclared assets,
unexpected stderr, or unbound output. The existing aggregate builder will only
merge the verified component under `build/site/quantecon`, add common reader
navigation, and bind separate Random/Žitković/QuantEcon/original rights and
runtime receipts.

Per chapter and cumulatively require directive/formula/label/code topology,
25-to-25 `solves` closure, all-cell offline execution, links/fragments/assets,
downloadable notebooks, keyboard/accessibility, meaningful image alternatives,
bounded tables/code at desktop and mobile widths, privacy, mathematical review,
and backend graph completeness. The final PDF uses a pinned native or
normalized print route, removes volatile metadata/IDs, and must match across
two clean builds. The upstream PDF is never an Indonesian build input.

Known downstream source findings already retained: the official PDF is
untagged, the flow figure lacks explicit alternative text, the proof index has
five unresolved `??` entries, and “Asymptotic Stabilitiy” occurs four times.
Do not contact upstream during production.
