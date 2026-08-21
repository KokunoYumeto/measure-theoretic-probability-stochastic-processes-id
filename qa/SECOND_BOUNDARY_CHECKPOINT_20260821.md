# Second reader-boundary checkpoint — 2026-08-21

Status: **public and anonymously byte-verified**.

## Admitted reader scope

1. `prob/Convergence.html`
2. `prob/Probability2.html`
3. `prob/Processes.html`
4. `prob/Stop.html`
5. `dist/Convergence.html`
6. `expect/Conditional2.html`
7. `expect/Uniform.html`
8. `labs/01-konvergensi-monte-carlo.html`

The O006/C140 Random sampling/LLN/CLT chapter remains an external shared
prerequisite and is not copied into this edition.

## Deterministic artifacts

- Site: 30 manifested files, 2,115,983 bytes.
- `PACKAGE_MANIFEST.csv` SHA-256:
  `523ab02b30534d701777cf5f50f27b1830a5aed3a490aced1d759ed3e5d36105`.
- `BUILD_RECEIPT.json` SHA-256:
  `88119231401f33bb2daa84596707f58765b348b053b18545fe3be0f2bedada9c`.
- Backend: 530 entities + 1,356 segments = 1,886 records; 485 typed
  relations; 21 manifest-bound backend files; zero QA failures.
- `BACKEND_MANIFEST.json` SHA-256:
  `a6b2081f056456df42a88a87df7b3b4594dafcbdc72bb0f48fb2f7f8145cef82`.

## Structural and mathematical preservation

The builder accepted every admitted page against its frozen Random authority:
ordered element topology matches; IDs and immutable href/src/class/onclick
attributes match; permitted locale, keyword, title, and alt fields are id-ID;
all TeX spans are byte-exact and ordered; IDs are unique; image alternatives
are nonempty. The seven theory pages contain 4,528 TeX spans in total.

The one downstream source correction is explicit and machine-recorded:
`Probability2.html#tai1` is rewritten in the built reader to the intended
existing `#tai12` target. Frozen authority and translation-source bytes retain
the upstream value. Other source defects remain preserved and queued in
`00_control/UPSTREAM_FINDINGS.md`; no upstream message has been sent.

## Reproducibility, link, asset, privacy, and code checks

The following bounded checks pass against the exact lane:

```text
python -m py_compile scripts/build_first_boundary.py scripts/build_backend.py
python scripts/freeze_random_authority.py --root authority/random --check
python scripts/build_first_boundary.py --check
python scripts/build_backend.py --validate-only
python scripts/verify_published_site.py build/site
```

The site validator proves manifest/receipt binding, local link and fragment
closure, CSS asset closure, local MathJax plus `boldsymbol` closure, id-ID
locale declarations, duplicate-ID absence, stable executable R block, and
absence of private paths, Google Analytics, or other excluded runtime residue.
The lab re-executes under pinned R 4.6.1 and reproduces all three recorded rows.

## Browser and visual gate

The local site was served from its exact absolute build path and inspected in
the in-app browser at 1280×720 and 390×844. The Browser workflow materially
supplied real MathJax, control, image, and responsive-layout evidence.

| Page | MathJax | details | opened | closed | desktop overflow | mobile overflow |
|---|---:|---:|---:|---:|---|---|
| `prob/Convergence.html` | 408 | 24 | 24 | 0 | none | none |
| `prob/Probability2.html` | 697 | 16 | 16 | 0 | none | none |
| `prob/Processes.html` | 438 | 11 | 11 | 0 | none | none |
| `prob/Stop.html` | 1,029 | 32 | 32 | 0 | none | none |
| `dist/Convergence.html` | 993 | 25 | 25 | 0 | none | none |
| `expect/Conditional2.html` | 598 | 24 | 24 | 0 | none | none |
| `expect/Uniform.html` | 365 | 10 | 10 | 0 | none | none |

All pages declared `lang=id-ID`, every image completed with nonzero natural
width and nonempty alt text, and the browser warning/error log was empty. The
lab rendered 34 math containers, one copyable stable-ID R block, and three
result-table rows without desktop or mobile document overflow. Direct visual
inspection confirmed a centered, page-filling desktop theory layout and a
readable single-column mobile lab layout.

## Release evidence

Commit `421102a5f085cb43a553a9205a41eb5840a742a2` (tree
`2212b70358a639d25b2d46176a45d27582f341b3`) deployed successfully in Pages
run `32524904841`, job `96904777777`, deployment `6028956065`. At
2026-08-21T20:43:20.1513723Z, the anonymous verifier matched all 30 manifested
files and 2,115,983 bytes exactly, including manifest SHA-256
`523ab02b30534d701777cf5f50f27b1830a5aed3a490aced1d759ed3e5d36105`.
The complete machine receipt is `00_control/PUBLICATION_RECEIPT.json`.

This checkpoint is substantial but is not the complete edition; the durable
goal remains active.
