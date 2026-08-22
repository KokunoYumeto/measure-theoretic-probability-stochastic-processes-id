# Fifth reader-boundary checkpoint — 2026-08-22

Status: **release-ready locally; publication transaction pending**.

## Added unit and component closure

- Frozen authority: `authority/random/static/martingales/Properties.html`,
  37,473 bytes, SHA-256
  `0f8bc07eb5eda38e8d4f78e94ba71a7dae8e9b788278f9b6ed250b0f66dc3850`.
- Indonesian source: `source/theory/martingales/Properties.html`, 38,315
  bytes, SHA-256
  `7420e69d72f16ab55ba0f9c3c8f6e0476de8b3516aff5613210620824bee21f9`.
- Built reader: `build/site/martingales/Properties.html`, 40,809 bytes,
  SHA-256
  `cd9797175f9b119db56058b6be2185568fdeb427fde986d583c5c6327515ffe6`.

The translation preserves the authority page's 430 LF-terminated lines, 322
parsed start tags, 30 unique IDs, 60 links, 9 source references, 16 detail
panels, and all 520 ordered TeX surfaces. The built reader has 536 mathematical
surfaces after explicit downstream qualifications and repairs.

The three same-origin mathematical plots are copied byte-for-byte and remain
under Random's dual official license witnesses rather than the edition's
original-work license:

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `martingales/ConvexFunction.png` | 2,861 | `0849bd7b68a2e0f3c34a990b568eb9f778d39e5293798ebbe9327c1b464ee84d` |
| `martingales/Powers.png` | 14,675 | `67ec6db3d3a459d051b4c24d1d2fbd9122086c6b8c58eddb0063a655786431fc` |
| `martingales/PositivePart.png` | 6,483 | `44f6d78041b2d1959a9887395c84bdd1064097894145bfa7225c50776ad56b14` |

## Reader repairs and backend representation

Frozen authority and translation-source mathematics remain unchanged. The
built reader applies 13 exact-once repairs for the SVG media type, filtration
macro, visible heading references, Doob normalization, the Doob–Meyer
hypotheses, the every-start scope of the harmonic converse, the martingale
transform reference and integrability condition, the De Moivre equality,
the branching-process space–time representation, and the truncated identity
sentence.

The whole-reader sweep also exposed ten pre-existing empty visible references:
one in `dist/Convergence.html` and nine in
`martingales/Introduction.html`. The builder now supplies exact-once Indonesian
labels while preserving the frozen authority and translation sources. All ten
are exported as source-link repairs. The Pandoc index and lab now declare the
local SVG favicon explicitly, eliminating the browser's implicit missing-root
favicon request.

The backend contains 748 entities and 1,990 segments (2,738 records), 683
typed relations, 21 generated files, and zero QA failures. Its 74 correction
records comprise 60 source-content repairs, 11 source-link repairs, two
original additions, and one deterministic-output record.

## Deterministic artifact gate

- Site: 37 manifested files / 2,372,365 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 3,395 bytes, SHA-256
  `eca262b01a8bdf87ba4a7dfc23db99e06e11ee18d098e2b702636aa6261fbb38`.
- `build/site/BUILD_RECEIPT.json`: 3,582 bytes, SHA-256
  `16608283683eb30fca0f0922b642b69ecb03604180e10cf2aa97f0bc29b7467c`.
- `backend/BACKEND_MANIFEST.json`: 3,993 bytes, SHA-256
  `c8a654be6cc87f3349110422ed09ecad68becceecbd487a3e897261ba596b32b`.
- Backend input-set SHA-256:
  `06330bd48713053c60ea18680d8ba5ce1aa527ada729386c2a120818e3b515af`.

The bounded Python compile, authority-freeze check, deterministic reader
build/check, strict backend build/validation, and publication-structure
verifier all pass.

## Browser, reflow, interaction, and privacy gate

The in-app browser inspected all ten theory pages, the index, and the lab at
1280×720 and 390×844. At each size all 12 pages use `lang=id-ID`, have
`scrollWidth == clientWidth`, and have no broken image, empty image
alternative, unresolved visible `.ref` anchor, external runtime, or palette
mismatch. Each sweep rendered 6,702 MathJax containers and found 202 detail
panels. The new page alone renders 536 MathJax containers; its visible controls
open and close all 16 detail panels at both sizes.

On mobile the three figures occupy a centered 350-pixel content width. The
325×250 convexity plot remains intrinsic size; the two 360×228 plots reflow to
350×221. The document stays 375 pixels wide with no mathematical or figure
overflow. Desktop and mobile screenshots show the edition filling and centering
the available reader column.

This checkpoint is not the complete edition. The next source-order unit is
`authority/random/static/martingales/Stop.html`, 43,887 bytes, SHA-256
`8d4c674bec0d19a253405dfe8c06e4b4062d6ef82330f945d50e2c494955a5af`.

