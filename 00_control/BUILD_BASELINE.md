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

All five commands pass on the current 2026-08-21 boundary. The lab estimates are
`0.177976805338`, `0.256464342623`, and `0.250381011435` for `n=10`, `1000`,
and `1000000`; the full canonical rows remain in `RUNTIME_LOCK.json` and the
build receipt.

## Exact output boundary

- Reader content: 31 manifested files / 2,173,893 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 2,803 bytes, SHA-256
  `20b8af90f55fb035de538cb6e542fe7d8ce925db022ddca0a156fd5e45f8cbf4`.
- `build/site/BUILD_RECEIPT.json`: 3,096 bytes, SHA-256
  `b9f637a74692c6ee6a16d74411ed77f375264b010d79f300659cb5982c5dfdc5`.
- Backend: 604 entities + 1,625 segments = 2,229 records / 553 relations /
  21 generated files / zero QA failures; manifest SHA-256
  `09941d228f9061ec3f251e54b2a809bb45e61a22afa86740539b2683350631e1`.
- Backend exporter SHA-256
  `647e28ecb2c52d599e80431554f35bb2603fc3f6d84282257270020dc379f978`.
- Backend input-set SHA-256
  `be61f110feb424378c9bc99e183510e2bfd7bb86f9a21b0013a45e7b7eb4031b`.

The reader contains no analytics. Every HTML/CSS local reference and fragment
closes; the executable lab is a copyable code block; all CSS pseudo-icons and
the MathJax autoload extension are local. Browser QA covered all eight theory
pages plus the lab at 1280×720 and 390×844 with no document-level overflow,
broken image, empty image alternative, or console warning/error. Long
code/tables and long mathematical rows scroll only inside bounded containers.
The reader palette now overrides Random's fixed light-gray `div.unit` and table
fills, preventing low-contrast light-on-light blocks in dark mode.
