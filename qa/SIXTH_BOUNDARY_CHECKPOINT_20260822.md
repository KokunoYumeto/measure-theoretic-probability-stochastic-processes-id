# Sixth reader-boundary checkpoint — 2026-08-22

Status: **public and anonymously byte-verified**.

## Added unit and authority closure

- Frozen authority: `authority/random/static/martingales/Stop.html`, 43,887
  bytes, SHA-256
  `8d4c674bec0d19a253405dfe8c06e4b4062d6ef82330f945d50e2c494955a5af`.
- Indonesian source: `source/theory/martingales/Stop.html`, 45,979 bytes,
  SHA-256
  `7b2d717eb0c5e04a0fe1d46cd9cadb2e5d295fd4a43cab863cf6d3835bef23b2`.
- Built reader: `build/site/martingales/Stop.html`, 48,094 bytes,
  SHA-256
  `621a18ee8468e3112d2233843693a3ceb9075833dc8ec0f27467df686a5818d5`.

The translation preserves the exact authority topology, 30 unique IDs, all
69 ordered `href`/`src` references, 18 detail panels, and all 580 ordered TeX
surfaces. It introduces no page-specific asset or executable dependency; all
runtime files belong to the already frozen Random/MathJax closure.

## Reader corrections and modular backend

Frozen authority and translation-source mathematics remain unchanged. Twenty
exact-once reader actions repair the omitted optional-stopping variables,
restricted-expectation punctuation, two wrong theorem/example references, the
stopped-process domain and notation, an empty summary, expectation macros, an
invalid Wald proof, incorrect pattern-waiting martingale accounting, a repeated
gambler index, the secretary term count and initialization, SVG media type,
and three bounded localization inconsistencies. The long Wald argument is
split into aligned lines for phone readability. Every action is exported in
`backend/corrections.csv` and described in `00_control/UPSTREAM_FINDINGS.md`.

The backend reuses the existing stopping-time, stopped-process, and random-walk
concepts; adds optional stopping, hitting time, Wald's equation, finite-pattern
waiting time, and optimal stopping; and records explicit dependencies on
`prob/Stop.html` and `martingales/Properties.html`. Four Indonesian outcomes
and eight required teaching/assessment/dependency relations close the unit
without importing O006-owned chapter-5 bytes.

The backend contains 809 entities and 2,169 segments (2,978 records), 743
typed relations, 21 generated files, and zero QA failures. Its 94 correction
records comprise 78 source-content repairs, 13 source-link repairs, two
original additions, and one deterministic-output record.

## Deterministic artifact gate

- Site: 38 manifested files / 2,420,936 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 3,488 bytes, SHA-256
  `210398e53aba6ea35748cf8d09d21a9a89e0820c3fff899d0b786e0b926de7a6`.
- `build/site/BUILD_RECEIPT.json`: 3,818 bytes, SHA-256
  `76d312d58eff8add50e88a5647e12f6cbb3cbb929c1eadc6abad52cb36071359`.
- `backend/BACKEND_MANIFEST.json`: 3,994 bytes, SHA-256
  `2788f5a50e364fa1794b6281941ae9e4c8190a947c58dda7c59b3a5a330be940`.
- Backend input-set SHA-256:
  `bee0f38b4be42ba7e796e076f9e64c1de8fbfeeada9ef1ff9433a973bb53ddcb`.

The bounded Python syntax parse, 94-file authority-freeze check, reader
build/check, strict backend build/validation, local-reference and CSS-closure
verifier, privacy scan, and reproducibility gates all pass.

## Browser, reflow, interaction, and privacy gate

The in-app browser inspected the index, all 11 theory pages, and the lab at
1280×720 and 390×844. Each 13-page sweep rendered 7,300 MathJax containers and
found 220 detail panels. All pages use `lang=id-ID`; no page has document-level
horizontal overflow, a broken image, an empty image alternative, an unresolved
visible `.ref`, an external runtime, or unit contrast below 13.75:1.

The new page renders 598 MathJax containers and exposes exactly 18 summaries
for 18 details. Its visible controls open 18/18 and close to 0/18 at both
viewports. The reflowed Wald displays occupy at most the 323-pixel mobile
content width without shrinking their 16-pixel math context or widening the
375-pixel document. Desktop and phone screenshots show a centered reader that
fills the usable page column.

## Source-choice rationale, separate from curriculum admission

Random-first plus dependency-closed Žitković labs remains the strongest
edition design on primary evidence: Random supplies the exact 47-page D30
theory progression in a frozen 94-file/1,997,915-byte URL-byte closure;
Žitković supplies only exact CC0 computational slices from commit
`e2b35ad91a3689454ae6455e8ffc510a90760c0d` because its whole-book build has
166 missing or home-local children. Imperial remains unsuitable as the core
because contributor authority, component rights, deterministic build,
mastery, and Markov/Poisson/Brownian coverage do not close. O006/C140 owns all
Random chapter-5 sampling/LLN/CLT bytes; O009 links that prerequisite and owns
only the disjoint advanced theory, process units, labs, and original bridges.
This rationale does not claim that edition completion determines later
40-course curriculum admission.

The next source-order unit is
`authority/random/static/martingales/Inequalities.html`, 38,731 bytes,
SHA-256
`9e03259e83a9e8ac67c9a43a2df1aa8a85d65944f86b82653e46869f4ab451f3`.

## Publication evidence

- Deployed commit: `e53b2c4fcd8251f520c39a0a9eac9d477e764527`.
- Deployed tree: `1493889d4475df6dcea4dfbdb6fdb4bce047dbe4`.
- Pages run/job/deployment: `32543990253` / `96959134483` / `6031962276`;
  workflow conclusion and deployment state both `success`.
- Deployment status: `17148971521`.
- Anonymous verification at 2026-08-22T01:39:44.8137221Z matched all 38
  manifested files and 2,420,936 bytes; manifest SHA-256
  `210398e53aba6ea35748cf8d09d21a9a89e0820c3fff899d0b786e0b926de7a6`.
- Public reader:
  `https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/`.
