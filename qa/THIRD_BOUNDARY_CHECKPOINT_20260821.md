# Third reader-boundary checkpoint — 2026-08-21

Status: **release-ready locally; public deployment/readback pending**.

## Added unit

- Frozen authority: `authority/random/static/expect/Kernels.html`, 53,030
  bytes, SHA-256
  `9dd2a5474f284fcb11c9e9f9e81099a1c4fe1708094bfcd64b08ccb9f82c5b8d`.
- Indonesian source: `source/theory/expect/Kernels.html`, 54,612 bytes,
  SHA-256
  `5eb002c6749c46f90468ca78f62b57d88f068c5ec4b9dcd465aa90814f274b8b`.
- Built page: `build/site/expect/Kernels.html`, 57,311 bytes, SHA-256
  `f52bfb7994749b55f30b7b67286fb7a21fddb606f4ec19cae66452bc25683fd2`.

The source-preserving translation matches all 979 ordered tag events, all
immutable attributes, 5 IDs, 54 links, 22 disclosure panels, and 858 ordered
TeX surfaces (811 inline, 42 display, 5 standalone environments). No
reader-facing English residue remains. The built page applies 34 exact-once,
high-confidence source-content repairs and adds one separately licensed CC BY
4.0 qualification on existence and almost-everywhere uniqueness of regular
conditional distributions. Frozen authority and translation-source formulas
remain unchanged. Repairs are enumerated in `backend/corrections.csv` and
`00_control/UPSTREAM_FINDINGS.md`.

## Deterministic artifacts

- Site: 31 manifested files / 2,173,893 bytes.
- `PACKAGE_MANIFEST.csv`: 2,803 bytes, SHA-256
  `20b8af90f55fb035de538cb6e542fe7d8ce925db022ddca0a156fd5e45f8cbf4`.
- `BUILD_RECEIPT.json`: 3,096 bytes, SHA-256
  `b9f637a74692c6ee6a16d74411ed77f375264b010d79f300659cb5982c5dfdc5`.
- Backend: 604 entities + 1,625 segments = 2,229 records; 553 typed
  relations; 21 manifest-bound backend files; zero QA failures.
- `BACKEND_MANIFEST.json`: 3,992 bytes, SHA-256
  `09941d228f9061ec3f251e54b2a809bb45e61a22afa86740539b2683350631e1`.
- Backend input-set SHA-256:
  `be61f110feb424378c9bc99e183510e2bfd7bb86f9a21b0013a45e7b7eb4031b`.

The original edition note is independently represented in the backend as
`segment.o009.original.expect.kernels.regular-conditional-note`, with its own
CC BY 4.0 rights ID and a `contains` relation from the kernels unit. Kernel,
probability-kernel, density, invariant-measure, composition, operator, and
regular-conditional-distribution concepts are locale-neutral records.

## Structural, mathematical, link, and privacy gate

The following bounded checks pass:

```text
python -m py_compile scripts/build_first_boundary.py scripts/build_backend.py
python scripts/freeze_random_authority.py --root authority/random --check
python scripts/build_first_boundary.py --check
python scripts/build_backend.py --validate-only
python scripts/verify_published_site.py build/site
```

The builder asserts every rendered repair has one and only one source match;
the backend validates all correction, provenance, rights, graph, schema, and
manifest bindings. The site verifier closes local links/fragments/assets/CSS,
local MathJax plus `boldsymbol`, stable R execution, locale declarations,
duplicate IDs, and private-path/analytics exclusions.

## Browser, reflow, interaction, and contrast gate

The in-app browser inspected all eight theory pages and the laboratory at
1280×720 and 390×844. Every page had `scrollWidth == clientWidth`, no broken
image, no empty image alternative, and `lang=id-ID`. All 5,390 theory MathJax
containers rendered (including 862 on `Kernels.html` after explicit repairs
and the edition note); the lab rendered 34. Runtime warning/error logs were
empty.

`Kernels.html` opened all 22 proof/detail panels through the visible control
and returned to 0 open panels through the close control at both reflow states.
The edition note was visible and centered: about 1,188 px wide at desktop and
350 px wide at mobile. Long mathematics scrolls within its own bounded
container; the document itself never overflows horizontally.

Visual QA exposed and resolved an inherited dark-mode defect: Random's
`div.unit` rule forced a light-gray fill while the reader supplied light text.
`reader.css` now overrides unit and striped-table surfaces with the reader
palette. All 35 mathematical units on the kernels page, and all units across
the existing reader, use one consistent dark panel (`rgb(24,39,51)`) with
light text (`rgb(238,244,248)`) in the inspected dark scheme. This directly
removes the previously confusing filled/unfilled and low-contrast behavior.

## Release gate

Commit/push, Pages workflow evidence, deployed commit identity, and anonymous
31-file byte readback remain required. This checkpoint is not the complete
edition; after publication the cursor advances to the martingale sequence.
