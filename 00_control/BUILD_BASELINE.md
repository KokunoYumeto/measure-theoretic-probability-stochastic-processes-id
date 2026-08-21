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

## Deterministic first-boundary commands

```text
python scripts/build_first_boundary.py
python scripts/build_first_boundary.py --check
python scripts/build_backend.py
python scripts/build_backend.py --validate-only
python scripts/verify_published_site.py build/site
```

All five commands pass on the 2026-08-21 boundary. The lab estimates are
`0.177976805338`, `0.256464342623`, and `0.250381011435` for `n=10`, `1000`,
and `1000000`; the full canonical rows remain in `RUNTIME_LOCK.json` and the
build receipt.

## Exact output boundary

- Reader content: 22 manifested files / 1,807,932 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 1,996 bytes, SHA-256
  `c7dcaf31439066f3a2191937bcad7dce18dba5d4044bdaa25c7b434dcf369c3d`.
- `build/site/BUILD_RECEIPT.json`: 1,392 bytes, SHA-256
  `4764287c8a64a1b566074dfe95a2a786532044a35e9318fe266cd1fc4468b0d1`.
- Backend: 340 records / 103 relations / 21 generated files; manifest SHA-256
  `2bd9008f16aca2f80222e4f19ca7885c57e1cc706136da7133902847039cf638`.
- Backend exporter SHA-256
  `457a059db310a180e82f704c9284c8ac9f210958325e66d88f8700e3183b5575`.
- Backend input-set SHA-256
  `1a70b701cf6dcdb60b379ab9fffe9720506d2a0e408ef0a0da528467b3ad710d`.

The reader contains no analytics. Every HTML/CSS local reference and fragment
closes; the executable lab is a copyable code block; all CSS pseudo-icons and
the MathJax autoload extension are local. Visual QA passed at 1280×720 and
390×844 with no document-level overflow. Long code/tables and long mathematical
rows scroll only inside their bounded containers.
