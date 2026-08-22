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

The first four commands pass on the locally complete tenth boundary. The
publication verifier is run against local bytes before push and again against
the anonymously served Pages bytes after deployment.

## Exact tenth-boundary output

- Reader content: 43 manifested files / 2,661,986 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 3,985 bytes, SHA-256
  `c82e526a39a952f439ed11034ce8bbdcccb5deb853fef931a4336453780bf527`.
- `build/site/BUILD_RECEIPT.json`: 7,015 bytes, SHA-256
  `682a76f74952286f39bf1aafa1ff2939a8b0c0ea8602ee559efdb396d4175ac8`.
- Backend: 1,058 entities + 2,737 segments = 3,795 records / 988 relations /
  21 generated files / eight QA passes / zero QA failures.
- `backend/BACKEND_MANIFEST.json`: 3,995 bytes, SHA-256
  `6f14a2e733baa821f264c8964fa8e4bcd64ab17bbfae21626832803abe6a3e73`.
- Backend input-set SHA-256:
  `0581b6e3068816ec48833486a8c077c0ee3056441fa575f46fef724021c86ab1`.
- Reader builder: 187,036 bytes, SHA-256
  `7a8d426450d9e12ff9fb408912b342eb9dae566c44de0debb2193578b5d69310`.
- Backend exporter: 162,937 bytes, SHA-256
  `98f0267f30fe5fc71f5236e28e8046eea6a176ea93feca675f04529a313dc3ac`.

The build receipt binds the ordered 15 theory sources, two lab sources, exact
golden rows, current runtime hashes/versions, manifest count/bytes, and legacy
first-lab compatibility fields. The reader contains no analytics. Every local
HTML/CSS reference and fragment closes; every generated lab has a copyable
stable-ID code block, stable-ID result table, complete edition navigation, and
exact source/result binding. Symbolic links are rejected from inputs and site
inventory.

Browser QA covered all 18 pages at 1280×720 and 390×844. Each sweep rendered
9,996 MathJax containers and found 279 disclosures, with zero document
overflow, broken image, empty alternative, unresolved visible reference,
external runtime, navigation mismatch, or browser warning/error. Long code,
tables, and displays scroll only inside bounded containers. The exact evidence
is in `qa/TENTH_BOUNDARY_CHECKPOINT_20260822.md`.
