# First theory–lab boundary checkpoint — 2026-08-21

## Verdict

The Convergence + Monte Carlo boundary is admissible for initial repository and
Pages publication. Structural, mathematical, execution, link/asset,
accessibility, privacy, responsive visual, modular-backend, and deterministic
replay gates pass. This is a substantial checkpoint, not completion of the
Indonesian edition or proof of curriculum admission.

## Reader evidence

- Source theory: 40,997 bytes / SHA-256
  `185888375673550452d1d2428cd0b4203fecd31f0f338fc6c703849642a7809a`.
- Source lab: 6,499 bytes / SHA-256
  `c95bb36c66684b3fdc1b02de5233fe748aa11805205ef8f831f24d7bec9df085`.
- Site payload: 22 files / 1,807,932 bytes / manifest SHA-256
  `c7dcaf31439066f3a2191937bcad7dce18dba5d4044bdaa25c7b434dcf369c3d`.
- Build receipt SHA-256
  `4764287c8a64a1b566074dfe95a2a786532044a35e9318fe266cd1fc4468b0d1`.
- Fresh R execution matches all three receipt rows.
- The standard-library publication verifier independently passes the payload.

## Browser evidence

The reader was served only on `127.0.0.1` for QA, then the server was stopped.

- Desktop viewport: 1280×720; document scroll width 1,265, no horizontal
  overflow; all three pages display centered readable content.
- Mobile viewport: 390×844; document/body scroll width 375 after correction,
  no document-level overflow. Wide R code, result tables, and long mathematics
  remain usable through bounded internal scrolling.
- Theory: 408/408 MathJax containers, 24 disclosure panels, no missing images;
  localized Perluas/Ciutkan controls open 24/24 and close 24/24 panels.
- Lab: 34 MathJax containers, one stable-ID copyable R code block, three result
  rows, no duplicate IDs.
- Browser error/warning log: empty.
- Local requests for all figures/icons and
  `MathJax/input/tex/extensions/boldsymbol.js` returned HTTP 200.

## Backend evidence

- 340 records: program/course/resource/edition/unit/concept/outcome/segment/
  asset/rights plus artifact/QA/correction/translation projections.
- 103 typed relations with all endpoints valid, including O006 prerequisite,
  teaches, assesses, precedes, translates, hints, answers, and solves.
- 21 generated backend files; strict validation and two-build byte comparison
  pass; zero QA failures.
- Backend manifest SHA-256
  `2bd9008f16aca2f80222e4f19ca7885c57e1cc706136da7133902847039cf638`.

## Next cursor

`source/theory/prob/Probability2.html` is already translated and structurally
verified (51,686 bytes; SHA-256
`4cd3a1eb9edca1c3dc81eba39b97c018b339136241d8a668063e3bf62c1a4c32`).
It is the next reader/backend integration boundary, followed by translation of
`authority/random/static/prob/Processes.html`.

## Public closure

- Repository: `https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id`
- Deployed source commit: `f07ffbee0fa8309a9e39ae602a6fe1bfda9da2d8`
- Successful Pages run: `32505068598`; deployment `6025603605`.
- Reader: `https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/`
- Anonymous readback: every one of the 22 manifested files, totaling 1,807,932
  bytes, is exactly equal to the local verified payload.
