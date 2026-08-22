# Build and execution baseline

## Frozen host/runtime inputs

- Pandoc `3.9.0.2`, executable SHA-256
  `24f1593d7ba9f511bc428be3d7177d2a8ddc4bf60457c9f24a888a4790748c5d`.
- Python with Beautiful Soup/lxml as used by the builder.
- Lane-local official R `4.6.1`, `Rscript.exe` SHA-256
  `d829bcf7e9fa1d7e3e828c565c3cdbb1ed416f551f4fa6fd4dfcdf231e33e5e8`,
  `LC_ALL=C`, `--vanilla`, and a fresh temporary `R_USER`.
- R RNG: Mersenne-Twister / Inversion / Rejection.
- Random MathJax `tex-svg.js`: 1,704,911 bytes, SHA-256
  `dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a`.
- MathJax `boldsymbol.js`: 4,709 bytes, SHA-256
  `716cf8735d00abfb1627f8adbbf4aeb915ac9b5c55d47aeaf276e73dac6a2aa1`.

The exact installer/runtime/RNG/Pandoc and both golden lab results are in
`RUNTIME_LOCK.json`. The R installer and installed runtime are not publication
payloads.

## Deterministic reader commands

```text
python scripts/build_first_boundary.py
python scripts/build_first_boundary.py --check
python scripts/build_backend.py
python scripts/build_backend.py --validate-only
python scripts/verify_published_site.py build/site
```

All five commands pass on the locally complete eleventh boundary. The
publication verifier is run against local bytes before push and again against
the anonymously served Pages bytes after deployment.

## Exact eleventh-boundary output

- Reader content: 44 manifested files / 2,762,106 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 4,077 bytes, SHA-256
  `f2315be8b9d3a9f9a7a64b65ae67766ca9d467078056ce85e385cde69aad8b45`.
- `build/site/BUILD_RECEIPT.json`: 7,250 bytes, SHA-256
  `867d2594620907c5e1cc1d4fefc8187bc9dbc45914a2b319c52f776decc5d5a8`.
- Backend: 1,160 entities + 3,016 segments = 4,176 records / 1,100 relations /
  21 generated files / eight QA passes / zero QA failures.
- `backend/BACKEND_MANIFEST.json`: 3,998 bytes, SHA-256
  `d999141322b17356ad924d5d1dcb02d06d2b675d7708be8a66252bcb905713ca`.
- Backend input-set SHA-256:
  `793ef366551e25f0eb9ee501869433ae2ebbe734e3ae57809b650b4f3eec2429`.
- Reader builder: 222,359 bytes, SHA-256
  `0046acda50b3e46006c836e133f4e2ac2d8f1efd7db599dc15922d716801e034`.
- Backend exporter: 176,740 bytes, SHA-256
  `8b15e23f2f65adcb0fed23403b586b035638323664e848e3eea9457984311fc9`.

The build receipt binds the ordered 16 theory sources, two lab sources, exact
golden rows, current runtime hashes/versions, manifest count/bytes, and legacy
first-lab compatibility fields. The reader contains no analytics. Every local
HTML/CSS reference and fragment closes; every generated lab has a copyable
stable-ID code block, stable-ID result table, complete edition navigation, and
exact source/result binding. Symbolic links are rejected from inputs and site
inventory.

Browser QA covered all 19 pages at 1280×720 and 390×844. Each sweep rendered
10,656 MathJax containers, 309 disclosures, and 73 images, with zero document
overflow, broken image, empty alternative, unresolved visible reference,
external runtime, navigation/heading/landmark/label mismatch, or browser
warning/error. Long code, tables, and displays scroll only inside bounded
containers. The exact evidence is in
`qa/ELEVENTH_BOUNDARY_CHECKPOINT_20260822.md`.
