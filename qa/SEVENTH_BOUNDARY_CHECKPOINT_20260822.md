# Seventh reader-boundary checkpoint — 2026-08-22

Status: **locally complete and verified; publication pending**.

## Added unit and authority closure

- Frozen authority: `authority/random/static/martingales/Inequalities.html`,
  38,731 bytes, SHA-256
  `9e03259e83a9e8ac67c9a43a2df1aa8a85d65944f86b82653e46869f4ab451f3`.
- Indonesian source: `source/theory/martingales/Inequalities.html`, 40,512
  bytes, SHA-256
  `f7327659431ab0f8a7b6f696474e4b0e57e7dd138ba0374c5f722a31781161b6`.
- Built reader: `build/site/martingales/Inequalities.html`, 43,713 bytes,
  SHA-256
  `1469c38f26ff99f74dbb4e3633f1bef0927846d022d4db8e39d91a8f8862e144`.

The translation preserves the exact 557-event tag topology, 21 unique IDs,
63 ordered `href`/`src` occurrences, four `onclick` values, 15 disclosure
panels, 18 units, and all 550 ordered source TeX surfaces. It introduces no
page-specific content asset or executable dependency. Existing Random UI
assets retain the dual official rights witnesses; MathJax and its now-explicit
`boldsymbol.js` backend asset remain Apache-2.0. Ancillary applications remain
external links rather than claimed offline functionality.

## Reader corrections and modular backend

Frozen authority and translation-source mathematics remain unchanged. The
built reader applies 26 exact-once actions: 22 source-content repairs and four
deterministic display reflows. They correct the discrete maximal-process
index, the continuous closed-threshold/dyadic-limit proof, a missing `1/x`,
the invalid sign-reversal proof for nonnegative supermartingales, total
upcrossing notation and finite-index scope, the omitted submartingale
upcrossing proof, transform convention, alternating continuous-time crossings,
measurability and deterministic-grid justification, and the red-and-black
admissibility/reference/fair-case argument. Four long upcrossing chains are
reflowed into aligned lines for phone readability. Every action is exported in
`backend/corrections.csv` and described in
`00_control/UPSTREAM_FINDINGS.md`.

The backend records the maximal process, Doob maximal bounds, upcrossings,
Kolmogorov's inequality, and the bold-play application; adds three outcomes;
and binds explicit dependencies on martingale properties, optional stopping,
and convergence. The Kolmogorov application depends on the external O006/C140
sampling module, so no chapter-5 sampling/LLN/CLT source byte is duplicated.

The backend contains 861 entities and 2,298 segments (3,159 records), 793
typed relations, 21 generated files, and zero QA failures. Its 120 correction
records comprise 100 source-content repairs, 13 source-link repairs, two
original additions, and five deterministic-output records.

## Deterministic artifact gate

- Site: 39 manifested files / 2,465,207 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 3,589 bytes, SHA-256
  `10fcbf5114f7a914a8d924c254c33e77a27456b3a89fca7eb76845a26ba67d95`.
- `build/site/BUILD_RECEIPT.json`: 4,062 bytes, SHA-256
  `b57a48023545e448749293d2ab1b9a468cb39c5215dbf485ba47c0299b971778`.
- `backend/BACKEND_MANIFEST.json`: 3,994 bytes, SHA-256
  `bd260d9ad30832a48ded45160a4efb620db50a0048079a61bfbba4e263ee348b`.
- Backend input-set SHA-256:
  `a9dfd380084a2929887d1c016918ed7b124caca128395e26969e92e84a995ae4`.

The bounded Python syntax parse, reader build/check, strict backend
build/validation, source topology/math checks, local-reference and asset
closure, privacy checks, and deterministic output gates all pass.

## Browser, reflow, interaction, and privacy gate

The in-app browser inspected the index, all 12 theory pages, and the lab at
1280×720 and 390×844. Each 14-page sweep rendered 7,853 MathJax containers and
found 235 detail panels. There was no document-level horizontal overflow,
broken image, empty image alternative, unresolved visible reference, external
runtime, MathJax error, or browser warning/error.

The new page renders 553 MathJax containers and has 15 details. Its two visible
open controls open 15/15 panels and its two close controls return the count to
0/15 at both viewports. The first mobile inspection exposed four long displays;
after deterministic reflow, the repeated inspection showed normal-size,
readable aligned mathematics in the centered full-width reader.

## Source-choice rationale, separate from curriculum admission

The disjoint Random theory plus dependency-closed Žitković lab composite
remains the strongest design for this edition. Random supplies the coherent
47-page advanced theory/process progression from a frozen 94-file URL-byte
closure. Žitković contributes only exact CC0 computational slices from commit
`e2b35ad91a3689454ae6455e8ffc510a90760c0d`, because its whole-book build has
166 missing or home-local children. Imperial remains inadmissible as a core:
contributor authority, component rights, deterministic build, mastery closure,
and Markov/Poisson/Brownian coverage do not all close. O006/C140 owns every
Random chapter-5 sampling/LLN/CLT byte; O009 links that prerequisite and owns
only disjoint advanced theory, processes, labs, and original bridges. This
edition judgment does not imply later admission to the 40-course curriculum,
and completed work is not used as selection evidence.

The next source-order unit is
`authority/random/static/martingales/Convergence.html`, 44,951 bytes,
SHA-256
`c5ef4134737d39992647bc1bf7ab4c9b16814f11450e53e7f54642ec64bdea0f`.

## Publication evidence

Pending publication to the existing GitHub Pages lineage. This section will be
replaced with commit/tree, Pages run/job/deployment, and anonymous manifested
byte-readback evidence immediately after deployment.
