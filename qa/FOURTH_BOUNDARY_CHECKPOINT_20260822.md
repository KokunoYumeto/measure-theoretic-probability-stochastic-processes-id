# Fourth reader-boundary checkpoint — 2026-08-22

Status: **release-ready; public deployment and anonymous byte readback pending**.

## Added unit and component asset

- Frozen authority: `authority/random/static/martingales/Introduction.html`,
  59,687 bytes, SHA-256
  `ff102fd4f54926d89c47b92885176e587f342378e442f1f38e4a69199a02375a`.
- Indonesian source: `source/theory/martingales/Introduction.html`, 61,528
  bytes, SHA-256
  `38702482ef4563bd29c050d1dfaec7d280ea1bee0bf6b55ff272d0ee5d2346e7`.
- Built reader: `build/site/martingales/Introduction.html`, 64,294 bytes,
  SHA-256
  `4318a2f8cfde41d3f3d633ef1abd7181bd7800f72675128ba3b4630401b51fc9`.
- Page-specific image: `martingales/Martingale.png`, 67,648 bytes,
  SHA-256
  `c7b5939b84f2a18776fc684f9b413a26fec315a684e35c7986c73a0efbb6cf4b`.
  The exact source bytes are copied to the reader. The visible figure credit
  retains Danielle M., the Wikimedia Commons source link, and CC BY 3.0; the
  backend records this as a component right distinct from Random's page-level
  license witnesses.

The topology-preserving translation retains all 604 LF-terminated source
lines, 449 parsed tag events, immutable attributes, 49 IDs, 90 links, 7 source
references, 22 disclosure panels, and 741 ordered TeX surfaces. The built
reader has 742 TeX surfaces because one separately recorded correction adds
the missing `s\le t` condition. No reader-facing English residue remains apart
from the source-preserved `\text{ for some }` inside TeX.

## Repairs and backend representation

Frozen authority and translation-source mathematics are unchanged. The reader
builder applies 13 exact-once, high-confidence source-content repairs: six
expectation-macro repairs; the partial-product input sequence; the
stationary-increment time order and variance rate; the second-moment variance
identity; two branching-process notation/index repairs; and the density index
domain. Every repair has a stable backend correction record and exact source,
reader, and evidence bindings. `UPSTREAM_FINDINGS.md` preserves the bounded
evidence; no upstream contact occurred.

The backend now contains 688 entities and 1,835 segments (2,523 records), 629
typed relations, 21 manifest-bound files, and zero QA failures. It includes the
martingale concepts, page/translation/provenance relations, separate CC BY 3.0
image right, the image artifact, and the 13 correction records. The builder
and backend now hard-fail if their theory sequences differ, if any admitted
unit or lab is missing from the index, or if any backend QA event fails.

## Deterministic artifacts and command gate

- Site: 33 manifested files / 2,306,486 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 3,002 bytes, SHA-256
  `9cc2ed7d7867a63082285338cf9727b1aeb90d8ae884bc55cb2f6934566b7284`.
- `build/site/BUILD_RECEIPT.json`: 3,340 bytes, SHA-256
  `fc5faf5656514f6c09ecee3b08260dad129a7524893109f397a38311822e85a0`.
- `backend/BACKEND_MANIFEST.json`: 3,992 bytes, SHA-256
  `db70ebe0880e31a607c57bc7282476f2d2f2fd386a1ed937946bf35e1e7eefe7`.
- Backend input-set SHA-256:
  `4afe8a4fa42b973c78d964331c0824ece7a66a51730570d064e7de3b835b81e3`.

The following bounded commands pass:

```text
python -m py_compile scripts/build_first_boundary.py scripts/build_backend.py
python scripts/freeze_random_authority.py --root authority/random --check
python scripts/build_first_boundary.py --check
python scripts/build_backend.py --validate-only
python scripts/verify_published_site.py build/site
```

## Browser, reflow, interaction, and privacy gate

The in-app browser inspected all nine theory pages and the laboratory at
1280×720 and 390×844. Every page had `scrollWidth == clientWidth`, `lang=id-ID`,
no broken image, no empty image alternative, no external runtime, and no
console warning/error. The sweep rendered 6,132 MathJax containers across the
theory pages and 34 in the laboratory. Every current `div.unit` uses the same
dark high-contrast palette (`rgb(24,39,51)` with `rgb(238,244,248)` text).

On the new page, all 742 formulas and all 22 detail panels render. The visible
open-all and close-all controls reach 22/22 and 0/22 panels at both viewport
sizes. The horse-harness image loads at its intrinsic 167×250 pixels with the
Indonesian alternative text `Kekang martingal`; its figure reflows from 1,152
pixels wide on desktop to 350 pixels on mobile. One long variance display is
340 pixels wide inside a 333-pixel `overflow-x:auto` MathJax container; the
375-pixel mobile document itself does not overflow. This is the intended
bounded formula scroll, not a non-centered page layout.

## Publication evidence

The source commit, tree, Pages run/job/deployment, and anonymous manifest
readback will be appended immediately after the authorized push succeeds. This
checkpoint is not the complete edition; the next exact source-order unit is
`authority/random/static/martingales/Properties.html`.
