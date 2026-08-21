# Current goal and workflow

## Durable goal

Own and complete a Bahasa Indonesia curriculum corpus: O009/D30, Measure-Theoretic Probability and Stochastic Processes, as translation and reader-production—not a source-audit exercise. Deliver a complete id-ID course, a locale-neutral modular backend, and its own public GitHub repository. Translation is dominant; QA, provenance, and backend work support it rather than replacing it.

Selection: adjudicate Random-first plus bounded Gordan Žitković labs against an Imperial-LaTeX-core alternative using official/primary evidence. Source authority, lawful derivative/redistribution rights including assets, public editable closure, and reproducible buildability are veto gates. Freeze URL bytes or commit/tree/archive, manifests, licenses, contributor authority, assets, coverage, exercise/hint/answer/solution census, accessibility, and build dependencies. Keep components and original additions separately attributed/licensed; never flatten mixed rights. If no candidate passes, document the comparison and author only the missing bridge.

Production: after admission, translate contiguously in source order into natural reader-facing id-ID while preserving formulas, IDs, topology, references, exercises, hints, answers, solutions, code, and assets. Begin with one coherent theory–lab boundary, then continue through probability spaces, convergence modes, LLN/CLT, measure-theoretic conditional expectation, martingales, Markov, Poisson, renewal, and Brownian motion. Use Žitković only for dependency-closed executable labs that add computation without duplicating theory. Add narrowly original prerequisite bridges, proof-versus-simulation guidance, mastery exercises, progressive hints, answers, worked solutions, tests, and accessible alternatives where sources lack them. Pin and execute an open/offline build and R harness; produce editable source, readable HTML, and PDF where useful and verified.

Backend: assign stable locale-neutral IDs to course, units, concepts, prerequisites, outcomes, examples, exercises, hints, answers, solutions, labs, assets, and corrections. Record source aliases/spans; prerequisite, teaches, assesses, solves, sequence, alternate-form, and translation relations; component rights/provenance; hashes; build artifacts; and translation state in canonical JSON/JSONL/CSV compatible with the coordinator model. Another language must be able to reuse or replace units without scraping Indonesian prose.

Durability: keep on-disk controls sufficient to resume without chat memory: this roughly 4,000-character goal; current state/next action; source authority and rights manifest; decision/adverse ledger; source-to-target map; terminology; translation cursor; build/runtime lock; QA/checkpoint log; artifact manifests; remote receipt; and pending/completed to-dos. Recover after compaction from current on-disk controls and exact bytes, not generated summaries. Update controls at substantial boundaries with paths, sizes, hashes, decisions, failures, and next cursor.

Verification/publication: run bounded structural, mathematical, code-execution, link/asset, accessibility, privacy, visual, and reproducibility checks; never broad-scan the workspace or run repository-wide Git operations. Ledger source corrections. At each substantial verified chunk, commit and push the lane repository without seeking confirmation; use the user’s token notes, never expose secrets, and fail closed on mismatch. The coordinator owns the global hub. Do not contact authors during production. Only after the full corpus is complete and upstream reporting is separately authorized, submit at most one concise deduplicated high-confidence report signed “Codex — at the user’s direction.”

Completion requires admitted exact sources/rights, a complete translated D30 reader, executed labs, missing mastery/bridge surfaces, canonical backend, reproducible builds, full bounded QA, durable controls/hashes, a current public per-corpus GitHub, and no unresolved release blocker.

## Recovery order

1. Read this file, `CURRENT_STATE.md`, `CURRENT_CURSOR.json`, and `TODO.md`.
2. Read `SOURCE_AUTHORITY_AND_RIGHTS.md` and `DECISION_AND_ADVERSE_LEDGER.md` before changing selection or licenses.
3. Read the current unit map/backend files and the latest build/QA checkpoint before editing a target.
4. Hash the exact current target named by the cursor. If it differs from the recorded hash, stop and reconcile concurrent work.
5. Resume the next unchecked to-do. Do not reconstruct state from chat or generated summaries.

## Non-negotiable operating boundaries

- No broad workspace scans or repository-wide Git operations.
- No overlap with O006/C140 Random chapter 5. O006 owns Random `sample/*`, including LLN/CLT; O009 consumes that translated module as a prerequisite.
- No upstream contact during production. One concise report is possible only after full completion and separate authorization.
- Push a substantial verified boundary without asking again; never expose credentials.
