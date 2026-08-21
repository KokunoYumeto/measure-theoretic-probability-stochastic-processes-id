# Current state

As of 2026-08-21, this is an active O009/D30 production lane. Its first
theory–lab reader boundary is public and anonymously byte-verified on GitHub
Pages. The complete Indonesian edition is not yet finished, and no upstream
contact has occurred. Completion of this edition is independent of the
coordinator's later curriculum-admission decision.

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

The public repository is
`https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id`
and the reader is
`https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/`.
Pages run `32505068598` deployed source commit `f07ffbee0fa8309a9e39ae602a6fe1bfda9da2d8`;
all 22 manifested files matched anonymously. See `PUBLICATION_RECEIPT.json`.

### Second reader boundary (public and anonymously verified)

The reader now contains seven structurally verified theory units plus the
executed Monte Carlo lab:

- `prob/Convergence.html`: 40,997 bytes / SHA-256 `185888375673550452d1d2428cd0b4203fecd31f0f338fc6c703849642a7809a`.
- `prob/Probability2.html`: 51,686 bytes / SHA-256 `4cd3a1eb9edca1c3dc81eba39b97c018b339136241d8a668063e3bf62c1a4c32`.
- `prob/Processes.html`: 34,337 bytes / SHA-256 `8f31864d8cd4e4a5e9a5dba1181fb2ceac86817bc2eda49a7bd50a6b96385074`.
- `prob/Stop.html`: 62,596 bytes / SHA-256 `0fe72b687b42af41a6756545f25a5582d6d9f4aba4f0c88bbd3f30b79624366e`.
- `dist/Convergence.html`: 65,986 bytes / SHA-256 `948e294db3cfe1daefbd5bfd1e50f9d7a8b942dadfc0cefc63ca171be974dccc`.
- `expect/Conditional2.html`: 48,721 bytes / SHA-256 `ddd6260bfafc60a7de3e2b78220c0b793349abcf01afa8cf35420cb16f4e55b7`.
- `expect/Uniform.html`: 25,643 bytes / SHA-256 `63fc5afefa354f1f5db2530860089d5810284a185fba28713d315c5cd30ac895`.

The deterministic site contains 30 manifested files / 2,115,983 bytes;
manifest SHA-256
`523ab02b30534d701777cf5f50f27b1830a5aed3a490aced1d759ed3e5d36105`
and build-receipt SHA-256
`88119231401f33bb2daa84596707f58765b348b053b18545fe3be0f2bedada9c`.
The backend contains 530 entities, 1,356 segments, and 485 typed relations
(1,886 records total), with zero QA failures; manifest SHA-256
`a6b2081f056456df42a88a87df7b3b4594dafcbdc72bb0f48fb2f7f8145cef82`.

Whole-boundary browser QA at 1280×720 and 390×844 found no horizontal
overflow, broken images, empty image alternatives, or console warnings/errors.
All 142 disclosure panels opened and closed through their visible controls;
4,528 MathJax containers rendered across theory pages. The lab rendered 34
math containers, one copyable stable-ID R block, and three result rows. See
`qa/SECOND_BOUNDARY_CHECKPOINT_20260821.md`.

Commit `421102a5f085cb43a553a9205a41eb5840a742a2` (tree
`2212b70358a639d25b2d46176a45d27582f341b3`) is public. Pages run
`32524904841`, job `96904777777`, and deployment `6028956065` all succeeded.
An anonymous readback matched all 30 manifested files and 2,115,983 bytes
exactly at 2026-08-21T20:43:20.1513723Z. See `PUBLICATION_RECEIPT.json`.

## Next exact action

1. Reconcile and finish the existing `expect/Kernels.html` draft against its
   exact frozen authority. The current draft is 54,426 bytes at SHA-256
   `c9c1275b4226d6d761cedcf3b153d0cfc2574ff2b06fb0aa239a05962ccbf84b`;
   it is not yet admitted or release-ready.
2. Run structure/math/language QA, integrate the completed kernels unit into
   the deterministic reader and backend, and then continue the martingale
   sequence in source order.
3. Keep publishing substantial verified boundaries without treating any
   intermediate checkpoint as full completion.

The durable goal remains active. No PDF has yet been admitted because HTML is
the additive and accessible publication surface at this boundary.
