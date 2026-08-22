# Build and execution baseline

## Frozen host/runtime inputs

- Pandoc `3.9.0.2`
- Python with Beautiful Soup/lxml as used by the builder
- lane-local official R `4.6.1`, `LC_ALL=C`, `--vanilla`, temporary `R_USER`
- R RNG: Mersenne-Twister / Inversion / Rejection
- Random MathJax `tex-svg.js`: 1,704,911 bytes, SHA-256
  `dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a`
- MathJax `boldsymbol.js`: 4,709 bytes, SHA-256
  `716cf8735d00abfb1627f8adbbf4aeb915ac9b5c55d47aeaf276e73dac6a2aa1`

The exact R installer/runtime/RNG evidence is in `RUNTIME_LOCK.json`; the
installer and runtime are not publication payloads.

## Deterministic reader commands

```text
python scripts/build_first_boundary.py
python scripts/build_first_boundary.py --check
python scripts/build_backend.py
python scripts/build_backend.py --validate-only
python scripts/verify_published_site.py build/site
```

All five commands pass on the current 2026-08-22 boundary. The lab estimates are
`0.177976805338`, `0.256464342623`, and `0.250381011435` for `n=10`, `1000`,
and `1000000`; the full canonical rows remain in `RUNTIME_LOCK.json` and the
build receipt.

## Exact output boundary

- Reader content: 33 manifested files / 2,306,486 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 3,002 bytes, SHA-256
  `9cc2ed7d7867a63082285338cf9727b1aeb90d8ae884bc55cb2f6934566b7284`.
- `build/site/BUILD_RECEIPT.json`: 3,340 bytes, SHA-256
  `fc5faf5656514f6c09ecee3b08260dad129a7524893109f397a38311822e85a0`.
- Backend: 688 entities + 1,835 segments = 2,523 records / 629 relations /
  21 generated files / zero QA failures; manifest SHA-256
  `db70ebe0880e31a607c57bc7282476f2d2f2fd386a1ed937946bf35e1e7eefe7`.
- Backend exporter SHA-256
  `6171235e0d7c80c0f6fbef8ca469f9b6fd6d4688b8d6e583a56e9d8b2298172f`.
- Backend input-set SHA-256
  `4afe8a4fa42b973c78d964331c0824ece7a66a51730570d064e7de3b835b81e3`.

The reader contains no analytics. Every HTML/CSS local reference and fragment
closes; the executable lab is a copyable code block; all CSS pseudo-icons and
the MathJax autoload extension are local. Browser QA covered all nine theory
pages plus the lab at 1280×720 and 390×844 with no document-level overflow,
broken image, empty image alternative, or console warning/error. Long
code/tables and long mathematical rows scroll only inside bounded containers.
The reader palette now overrides Random's fixed light-gray `div.unit` and table
fills, preventing low-contrast light-on-light blocks in dark mode.
