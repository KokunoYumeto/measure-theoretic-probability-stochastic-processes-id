# Current state

As of 2026-08-21, this is an active O009/D30 production lane. Its first
theory–lab reader boundary is verified and ready for its initial GitHub
publication. The complete Indonesian edition is not yet finished, and no
upstream contact has occurred. Completion of this edition is independent of
the coordinator's later curriculum-admission decision.

## Source disposition

- Random is admitted as an exact URL-byte theory source, with the current home
  CC BY 2.0 and Credits CC BY 1.0 witnesses both retained.
- Random chapter 5 sampling/LLN/CLT belongs to O006/C140 and is a shared
  prerequisite, not duplicated source.
- Only dependency-closed Žitković CC0 slices are admitted as computational
  donors. The translated adaptation and original additions are separately CC
  BY 4.0.
- Imperial is rejected as a core because contributor authority, component
  rights, deterministic build, mastery, and D30 coverage do not close.
- MathJax 3.1.2 plus its required `boldsymbol` extension are frozen under
  Apache-2.0; Google Analytics is excluded.

The Random selection remains 94 files / 1,997,915 bytes with manifest SHA-256
`2ee154a38b57201457538db8c0e7df592a052eade8dcfda217605810f04f21e4`.
The authority receipt is schema v3 and binds the 4,709-byte `boldsymbol.js`
dependency at SHA-256
`716cf8735d00abfb1627f8adbbf4aeb915ac9b5c55d47aeaf276e73dac6a2aa1`.

## Completed production boundaries

### First reader boundary

- `source/theory/prob/Convergence.html`: 40,997 bytes, SHA-256
  `185888375673550452d1d2428cd0b4203fecd31f0f338fc6c703849642a7809a`;
  834 ordered HTML events and 408 TeX spans preserve authority.
- `source/labs/01-konvergensi-monte-carlo.Rmd`: 6,499 bytes, SHA-256
  `c95bb36c66684b3fdc1b02de5233fe748aa11805205ef8f831f24d7bec9df085`;
  the base-R chunk executes under pinned R 4.6.1 and includes original mastery,
  three progressive hints, an answer, and a worked solution.
- `build/site`: 22 manifested files / 1,807,932 bytes; manifest SHA-256
  `c7dcaf31439066f3a2191937bcad7dce18dba5d4044bdaa25c7b434dcf369c3d`;
  build receipt SHA-256
  `4764287c8a64a1b566074dfe95a2a786532044a35e9318fe266cd1fc4468b0d1`.
- Backend: 340 records, 103 typed relations, 21 manifest-bound files, zero QA
  failures; manifest SHA-256
  `2bd9008f16aca2f80222e4f19ca7885c57e1cc706136da7133902847039cf638`.

The build and independent publication verifier both pass. Desktop QA at
1280×720 and mobile QA at 390×844 show no document-level horizontal overflow.
The theory renders all 408 math expressions and 24 disclosure panels; expand
and collapse controls reach 24/24 and 0/24 open panels. The lab renders one
copyable R block, 34 math expressions, and the three-row executed result table.
All local images load, the `boldsymbol` extension is requested locally with
HTTP 200, and browser error/warning logs are empty.

### Next translated source unit

`source/theory/prob/Probability2.html` is fully translated but intentionally
not yet included in the first reader/backend boundary: 51,686 bytes, SHA-256
`4cd3a1eb9edca1c3dc81eba39b97c018b339136241d8a668063e3bf62c1a4c32`;
841/841 topology events, 697/697 TeX spans, 16 details panels, and 5 images
match authority.

## Next exact action

1. Create and push the initial verified repository and deploy `build/site`.
2. Record the remote commit, Pages run/deployment, and anonymous byte checks.
3. Integrate `Probability2.html` into the next reader/backend boundary.
4. Continue with `prob/Processes.html` in source order.

The durable goal remains active. No PDF has yet been admitted because HTML is
the additive and accessible publication surface at this boundary.
