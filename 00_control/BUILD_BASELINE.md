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

All five commands pass on the current 2026-08-22 fifth boundary. The lab estimates are
`0.177976805338`, `0.256464342623`, and `0.250381011435` for `n=10`, `1000`,
and `1000000`; the full canonical rows remain in `RUNTIME_LOCK.json` and the
build receipt.

## Exact output boundary

- Reader content: 37 manifested files / 2,372,365 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 3,395 bytes, SHA-256
  `eca262b01a8bdf87ba4a7dfc23db99e06e11ee18d098e2b702636aa6261fbb38`.
- `build/site/BUILD_RECEIPT.json`: 3,582 bytes, SHA-256
  `16608283683eb30fca0f0922b642b69ecb03604180e10cf2aa97f0bc29b7467c`.
- Backend: 748 entities + 1,990 segments = 2,738 records / 683 relations /
  21 generated files / zero QA failures; manifest SHA-256
  `c8a654be6cc87f3349110422ed09ecad68becceecbd487a3e897261ba596b32b`.
- Backend exporter SHA-256
  `5909e41ae032b00d74a08084e4cf0e88401ef85ab5beef7c79d883cc119485fb`.
- Backend input-set SHA-256
  `06330bd48713053c60ea18680d8ba5ce1aa527ada729386c2a120818e3b515af`.

The reader contains no analytics. Every HTML/CSS local reference and fragment
closes; the executable lab is a copyable code block; all CSS pseudo-icons and
the MathJax autoload extension are local. Browser QA covered all ten theory
pages, the index, and the lab at 1280×720 and 390×844 with no document-level
overflow, broken image, empty image alternative, unresolved visible reference,
external runtime, or palette mismatch. Long
code/tables and long mathematical rows scroll only inside bounded containers.
The reader palette now overrides Random's fixed light-gray `div.unit` and table
fills, preventing low-contrast light-on-light blocks in dark mode.
