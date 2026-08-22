# Eleventh reader boundary — discrete-time Markov chains

Verified locally on 2026-08-22. This checkpoint is a complete, locally
release-ready boundary; public GitHub status is recorded separately after the
single bounded push/readback attempt.

## Exact source and translation

- Frozen Random authority: `authority/random/static/markov/Discrete.html`,
  55,099 bytes, SHA-256
  `808118b103e17cd5e31115b953663b0d8ff94da21f432e6fe7c104e9300380f0`.
- Indonesian source: `source/theory/markov/Discrete.html`, 57,545 bytes,
  SHA-256
  `176d4f9284ee16353142d6c2612b46a32a93c416471621997c89e72308b785ea`.
- Built reader: `build/site/markov/Discrete.html`, 65,408 bytes, SHA-256
  `9b21e65c3da1c7989c99adee09da517634ca186d31c2a3886f51d65c9686a2b8`.
- The authority/translation pair preserves 530 parsed elements, 56 unique
  identifiers, 44 units, 30 disclosures, and all 649 ordered TeX surfaces.
  Seven explicit exercises and their seven worked disclosures are represented
  as exercise/solution roles in the backend.

The built page applies 44 exact-once actions: 34 source-content repairs, six
source-link repairs, and four deterministic-output reflows. They cover the
all-state Markov-family convention, strong Markov law, stopping/entrance/last-
visit domains, transition/tower laws, potential and resolvent identities,
sampling/restriction conventions, four resolvent examples, broken links,
media type, and mobile display layout. Frozen authority and faithful
translation remain unchanged by this downstream correction layer.

## Deterministic reader and backend

- Reader: 44 manifested files / 2,762,106 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 4,077 bytes, SHA-256
  `f2315be8b9d3a9f9a7a64b65ae67766ca9d467078056ce85e385cde69aad8b45`.
- `build/site/BUILD_RECEIPT.json`: 7,250 bytes, SHA-256
  `867d2594620907c5e1cc1d4fefc8187bc9dbc45914a2b319c52f776decc5d5a8`.
- Reader builder: 222,359 bytes, SHA-256
  `0046acda50b3e46006c836e133f4e2ac2d8f1efd7db599dc15922d716801e034`.
- Backend: 1,160 entities + 3,016 segments = 4,176 semantic records;
  1,100 typed relations; 21 files; zero QA failures.
- `backend/BACKEND_MANIFEST.json`: 3,998 bytes, SHA-256
  `d999141322b17356ad924d5d1dcb02d06d2b675d7708be8a66252bcb905713ca`.
- Backend input-set SHA-256:
  `793ef366551e25f0eb9ee501869433ae2ebbe734e3ae57809b650b4f3eec2429`.

All seven exercise/solution pairs have exactly one `solves` relation and one
`assesses` relation. The page depends on the general Markov, kernel, process,
and stopping-time units and records O006/C140 as the external sampling
prerequisite without importing any O006 chapter-5 byte.

The following commands pass:

```text
python -B scripts/build_first_boundary.py
python -B scripts/build_first_boundary.py --check
python -B scripts/build_backend.py
python -B scripts/build_backend.py --validate-only
python -B scripts/verify_published_site.py build/site
```

## Independent and browser QA

Independent language, mathematical, and static/backend audits found no
remaining content, translation, topology, link, asset, accessibility,
privacy, or semantic-graph veto. The mathematical audit explicitly rechecked
the strong-Markov all-state extension, hitting/last-visit conventions,
Chapman–Kolmogorov and tower derivations, potential identities, and all four
displayed resolvents.

Whole-reader browser QA covered all 19 HTML pages at 1280×720 and 390×844.
Each sweep rendered 10,656 MathJax containers, 309 disclosures, and 73 images,
with zero bad rows: no document overflow, broken/missing image, external
runtime, empty visible reference, heading-level jump, missing/duplicate
disclosure label, missing navigation label, or missing `h1`/`main` landmark.
The Discrete bulk controls reach 30/30 and return to 0/30; a native disclosure
opens to 1/30 and closes to 0/30 on phone width. Browser warning/error logs are
empty.

The whole-reader sweep exposed and resolved three inherited shell defects:
the index's duplicate H1 and missing main landmark, both labs' missing main
landmarks, and `prob/Processes.html`'s H1-to-H3 jump. The builder now enforces
one H1, one main landmark, no skipped heading level, and unique nonempty
disclosure labels for every generated HTML page.

Seven source lines and six generated-reader lines retain blank-at-EOL from the
exact Random HTML witness. They are deliberate source-fidelity bytes (including
one TeX line), not accidental new prose whitespace; all other staged diff
checks remain enabled.

## Rights, scope, and next cursor

The page remains bound to `rights.random.dual-witness`. It adds no new local
asset, package, dataset, or runtime. Random's external `TwoState.html`
simulation remains a labeled ancillary; the existing gambler's-ruin lab is not
misrepresented as its replacement. No excluded Random CTMC, ordinary-Poisson,
renewal, or O006-owned source byte entered this boundary. No upstream contact
occurred.

Next selected source: `authority/random/static/markov/Recurrence.html`, 51,381
bytes, SHA-256
`24edb8bd0237b0e3abd7beeae48596f35421c9aa35653c6845cfaebb223c5535`.
Translate it contiguously into `source/theory/markov/Recurrence.html`, preserve
its topology and mathematics, then extend the correction layer, backend,
reader, QA, and publication boundary. Do not divert to the Random pages
replaced by QuantEcon or to renewal.

## Publication attempt

The complete verified boundary, including its terminology controls, is
committed locally as `31fd97d5a7f29ea8937a7f3dc69912ce5fa840a6`
(tree `6673c3fd8e4bebd6bc4f468eb545784c18c96079`). The single bounded push
attempted the substantive boundary head
`993233df46a963e3ed580de48844b5f28042ae56` at
2026-08-22T15:53:39.9113931Z and failed with GitHub HTTP 403 and the explicit
message that the account is suspended. The subsequent commits only add this
sanitized receipt and the already-validated terminology entries; they were not
pushed again. Anonymous reads of the exact repository and Pages URLs both
returned 404. No credential value was printed, persisted, or placed in a URL.
Do not loop or create a substitute account; the complete local head is queued
for one retry only after the external account state changes.
