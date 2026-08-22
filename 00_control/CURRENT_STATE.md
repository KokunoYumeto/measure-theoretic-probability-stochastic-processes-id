# Current state

As of 2026-08-22, this is an active O009/D30 production lane. Its first nine
reader boundaries are public and anonymously byte-verified on GitHub Pages.
The complete Indonesian edition is not yet finished, and no upstream contact has occurred.
Completion of this edition is independent of the coordinator's later
curriculum-admission decision.

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

### Third reader boundary (public and anonymously verified)

`expect/Kernels.html` is now complete, structurally verified, integrated, and
visually inspected:

- frozen authority: 53,030 bytes / SHA-256
  `9dd2a5474f284fcb11c9e9f9e81099a1c4fe1708094bfcd64b08ccb9f82c5b8d`;
- Indonesian source: 54,612 bytes / SHA-256
  `5eb002c6749c46f90468ca78f62b57d88f068c5ec4b9dcd465aa90814f274b8b`;
- built reader page: 57,311 bytes / SHA-256
  `f52bfb7994749b55f30b7b67286fb7a21fddb606f4ec19cae66452bc25683fd2`.

All 979 tag events, 858 source TeX surfaces, 5 IDs, 54 links, and 22 detail
panels are preserved. The built reader applies 34 exact-once source repairs
and one separately licensed CC BY 4.0 regular-conditional-distribution note;
all 35 actions have backend correction/provenance records.

The deterministic site contains 31 files / 2,173,893 bytes, manifest SHA-256
`20b8af90f55fb035de538cb6e542fe7d8ce925db022ddca0a156fd5e45f8cbf4`,
and build-receipt SHA-256
`b9f637a74692c6ee6a16d74411ed77f375264b010d79f300659cb5982c5dfdc5`.
The backend contains 604 entities, 1,625 segments, and 553 relations (2,229
records total), with zero QA failures; manifest SHA-256
`09941d228f9061ec3f251e54b2a809bb45e61a22afa86740539b2683350631e1`.

Browser QA covered all eight theory pages and the lab at 1280×720 and 390×844:
no document overflow, broken image, empty image alternative, or console
warning/error. It exposed and resolved Random's low-contrast light-gray unit
fill under the reader dark palette. All current theory units now use one
consistent legible palette. See `qa/THIRD_BOUNDARY_CHECKPOINT_20260821.md`.

Commit `347517ed1bd8252bd5735677cbe680145d302802` (tree
`a109b42cce366b7a81ec25e7fd90daa43c33fb36`) is public. Pages run
`32527548058`, job `96912701798`, and deployment `6029386935` succeeded. An
anonymous readback matched all 31 manifested files and 2,173,893 bytes at
2026-08-21T21:20:22.3315139Z. See `PUBLICATION_RECEIPT.json`.

### Fourth reader boundary (public and anonymously verified)

`martingales/Introduction.html` is completely translated, structurally
verified, integrated, and visually inspected:

- frozen authority: 59,687 bytes / SHA-256
  `ff102fd4f54926d89c47b92885176e587f342378e442f1f38e4a69199a02375a`;
- Indonesian source: 61,528 bytes / SHA-256
  `38702482ef4563bd29c050d1dfaec7d280ea1bee0bf6b55ff272d0ee5d2346e7`;
- built reader page: 64,294 bytes / SHA-256
  `4318a2f8cfde41d3f3d633ef1abd7181bd7800f72675128ba3b4630401b51fc9`;
- separately credited CC BY 3.0 figure: 67,648 bytes / SHA-256
  `c7b5939b84f2a18776fc684f9b413a26fec315a684e35c7986c73a0efbb6cf4b`.

All 449 tag events, 49 IDs, 90 links, 7 source references, 22 detail panels,
and 741 authority/translation TeX surfaces are preserved. The built reader
applies 13 exact-once source-content repairs and records each in the backend.
The deterministic site contains 33 files / 2,306,486 bytes, manifest SHA-256
`9cc2ed7d7867a63082285338cf9727b1aeb90d8ae884bc55cb2f6934566b7284`,
and build-receipt SHA-256
`fc5faf5656514f6c09ecee3b08260dad129a7524893109f397a38311822e85a0`.
The backend contains 688 entities, 1,835 segments, and 629 relations (2,523
records total), with zero QA failures; manifest SHA-256
`db70ebe0880e31a607c57bc7282476f2d2f2fd386a1ed937946bf35e1e7eefe7`.

Browser QA covered all nine theory pages and the lab at 1280×720 and 390×844.
No page has document-level overflow, a broken image, an empty image
alternative, an external runtime, or a console warning/error. The new page
renders 742 MathJax containers and its visible controls open and close all 22
detail panels at both sizes. One long display scrolls only within its own
bounded container. See `qa/FOURTH_BOUNDARY_CHECKPOINT_20260822.md`.

Commit `5a77276ea7a6dcaee2d25f5e4518877f820b0db8` (tree
`dd1a0d56f4fc34c08edaa54889bf1ff95f719d0a`) is public. Pages run
`32540431719`, job `96949257411`, and deployment `6031439023` succeeded. An
anonymous readback matched all 33 manifested files and 2,306,486 bytes at
2026-08-22T00:29:31.5580754Z. See `PUBLICATION_RECEIPT.json`.

### Fifth reader boundary (public and anonymously verified)

`martingales/Properties.html` is completely translated, structurally
verified, integrated, and visually inspected:

- frozen authority: 37,473 bytes / SHA-256
  `0f8bc07eb5eda38e8d4f78e94ba71a7dae8e9b788278f9b6ed250b0f66dc3850`;
- Indonesian source: 38,315 bytes / SHA-256
  `7420e69d72f16ab55ba0f9c3c8f6e0476de8b3516aff5613210620824bee21f9`;
- built reader page: 40,809 bytes / SHA-256
  `cd9797175f9b119db56058b6be2185568fdeb427fde986d583c5c6327515ffe6`.

The exact topology, identifiers, and all 520 translation-source TeX surfaces
are preserved. Three same-origin mathematical plots are copied byte-for-byte
under Random's dual official license witnesses. Thirteen exact-once reader
repairs are recorded in the backend. A whole-reader sweep also found and
resolved ten previously empty visible heading references without changing
their authority or translation-source bytes.

The deterministic site contains 37 files / 2,372,365 bytes, manifest SHA-256
`eca262b01a8bdf87ba4a7dfc23db99e06e11ee18d098e2b702636aa6261fbb38`,
and build-receipt SHA-256
`16608283683eb30fca0f0922b642b69ecb03604180e10cf2aa97f0bc29b7467c`.
The backend contains 748 entities, 1,990 segments, and 683 relations (2,738
records), with zero QA failures; manifest SHA-256
`c8a654be6cc87f3349110422ed09ecad68becceecbd487a3e897261ba596b32b`.

Browser QA covered all ten theory pages, the index, and the lab at 1280×720
and 390×844. Both sweeps rendered 6,702 MathJax containers and found no
document overflow, broken image, empty image alternative, unresolved visible
reference, external runtime, or palette mismatch. The new page's controls
open and close all 16 detail panels at both sizes. See
`qa/FIFTH_BOUNDARY_CHECKPOINT_20260822.md`.

Commit `ff0931a39df6d0ce59c557c6950851e835e935ab` (tree
`dafd6524004a57272f0d1771bc0fbd0a396253d6`) is public. Pages run
`32541961706`, job `96953550545`, and deployment `6031664444` succeeded. An
anonymous readback matched all 37 manifested files and 2,372,365 bytes at
2026-08-22T00:58:29.7321943Z. See `PUBLICATION_RECEIPT.json`.

### Sixth reader boundary (public and anonymously verified)

`martingales/Stop.html` is fully translated, repaired downstream, integrated,
and visually inspected:

- frozen authority: 43,887 bytes / SHA-256
  `8d4c674bec0d19a253405dfe8c06e4b4062d6ef82330f945d50e2c494955a5af`;
- Indonesian source: 45,979 bytes / SHA-256
  `7b2d717eb0c5e04a0fe1d46cd9cadb2e5d295fd4a43cab863cf6d3835bef23b2`;
- built reader: 48,094 bytes / SHA-256
  `621a18ee8468e3112d2233843693a3ceb9075833dc8ec0f27467df686a5818d5`.

All 580 translation-source TeX surfaces and exact source topology are
preserved. Twenty exact-once built-reader actions repair the source's theorem,
notation, proof, accounting, initialization, markup, and bounded localization
defects; all are exported in the backend. The deterministic site contains 38
files / 2,420,936 bytes at manifest SHA-256
`210398e53aba6ea35748cf8d09d21a9a89e0820c3fff899d0b786e0b926de7a6`.
The backend contains 809 entities, 2,169 segments, and 743 relations (2,978
records), with zero QA failures; manifest SHA-256
`2788f5a50e364fa1794b6281941ae9e4c8190a947c58dda7c59b3a5a330be940`.

Browser QA covered all 13 reader pages at 1280×720 and 390×844. Each sweep
rendered 7,300 math containers and 220 details with zero bad rows. The new
page's visible controls open and close all 18 panels at both sizes, and its
corrected Wald proof is reflowed into readable mobile lines. See
`qa/SIXTH_BOUNDARY_CHECKPOINT_20260822.md`.

Commit `e53b2c4fcd8251f520c39a0a9eac9d477e764527` (tree
`1493889d4475df6dcea4dfbdb6fdb4bce047dbe4`) is public. Pages run
`32543990253`, job `96959134483`, and deployment `6031962276` succeeded. An
anonymous readback matched all 38 manifested files and 2,420,936 bytes at
2026-08-22T01:39:44.8137221Z. See `PUBLICATION_RECEIPT.json`.

### Seventh reader boundary (public and anonymously verified)

`martingales/Inequalities.html` is fully translated, repaired downstream,
integrated, and visually inspected:

- frozen authority: 38,731 bytes / SHA-256
  `9e03259e83a9e8ac67c9a43a2df1aa8a85d65944f86b82653e46869f4ab451f3`;
- Indonesian source: 40,512 bytes / SHA-256
  `f7327659431ab0f8a7b6f696474e4b0e57e7dd138ba0374c5f722a31781161b6`;
- built reader: 43,713 bytes / SHA-256
  `1469c38f26ff99f74dbb4e3633f1bef0927846d022d4db8e39d91a8f8862e144`.

All 550 translation-source TeX surfaces and exact source topology are
preserved. Twenty-two exact-once source-content repairs correct the maximal,
upcrossing, and red-and-black arguments; four deterministic display reflows
make the long upcrossing chains readable on phones. All 26 actions are
exported in the backend. The Kolmogorov application records O006/C140 as an
external sampling prerequisite and duplicates none of its chapter-5 bytes.

The deterministic site contains 39 files / 2,465,207 bytes at manifest
SHA-256
`10fcbf5114f7a914a8d924c254c33e77a27456b3a89fca7eb76845a26ba67d95`;
build-receipt SHA-256
`b57a48023545e448749293d2ab1b9a468cb39c5215dbf485ba47c0299b971778`.
The backend contains 861 entities, 2,298 segments, and 793 relations (3,159
records), with zero QA failures; manifest SHA-256
`bd260d9ad30832a48ded45160a4efb620db50a0048079a61bfbba4e263ee348b`.

Browser QA covered all 14 reader pages at 1280×720 and 390×844. Each sweep
rendered 7,853 math containers and 235 details with zero bad rows, browser
warnings/errors, broken assets, empty visible references, external runtime, or
document overflow. The new page's controls open and close all 15 panels at
both sizes. See `qa/SEVENTH_BOUNDARY_CHECKPOINT_20260822.md`.

Commit `bf8761e7b57f32738e41a6bf449de22a923185da` (tree
`10bfd2133a379bc64b4ac6ed85f6d2b0b16bcdea`) is public. Pages run
`32546297240`, job `96965238838`, and deployment `6032323338` succeeded. An
anonymous readback matched all 39 manifested files and 2,465,207 bytes at
2026-08-22T02:29:21.6560745Z. See `PUBLICATION_RECEIPT.json`.

### Eighth reader boundary (public and anonymously verified)

`martingales/Convergence.html` is completely translated, repaired downstream,
integrated, and visually inspected:

- frozen authority: 44,951 bytes / SHA-256
  `c5ef4134737d39992647bc1bf7ab4c9b16814f11450e53e7f54642ec64bdea0f`;
- Indonesian source: 47,368 bytes / SHA-256
  `da3c58c6260e21b9c04a67bdb18656bfcaabea4d7f8ee83b8f9538d0668a5747`;
- built reader: 50,294 bytes / SHA-256
  `0df044a093006920698ab95354c6c5cf3ebde8b4dc0f56be563f67764362ffa4`.

The authority/source pair preserves the exact 275-element topology, 22 IDs,
12 disclosures, 13 units, and all 722 ordered TeX surfaces. Thirty exact-once
reader actions repair convergence proofs and links, random-walk, branching,
beta–Bernoulli, Pólya, likelihood-ratio, partial-product, and signed-density
arguments; two displays are reflowed for mobile. An independent re-audit found
no remaining mathematical veto.

The site contains 40 manifested files / 2,515,782 bytes at manifest SHA-256
`f930653432a727a7941bfb1af77185d46635801e62aaabcd7891b67077b446ff`.
The backend contains 914 entities, 2,405 segments, and 844 relations (3,319
semantic records), with zero QA failures; manifest SHA-256
`038d71c967415bbe1d6613e83d4a9cb7518ac7fa84c377aa90087cd2d1d99a1c`.
Whole-reader
browser QA covered all 15 pages at 1280×720 and 390×844. Each sweep rendered
8,580 math containers and 247 details with zero bad rows, reader-origin browser
warnings/errors, broken assets, empty visible references, external runtime, or
document overflow. See `qa/EIGHTH_BOUNDARY_CHECKPOINT_20260822.md`.

Commit `39e0a31a2a2ec1172d3670fa30ea7c5a12388c78` (tree
`016d83022898c81f5f6c50196b7f32ff745f59cf`) is public. Pages run
`32548461973`, job `96971081076`, and deployment `6032660668` succeeded. An
anonymous readback matched all 40 manifested files and 2,515,782 bytes at
2026-08-22T03:17:02.5016359Z. See `PUBLICATION_RECEIPT.json`.

### Ninth reader boundary (public and anonymously verified)

`martingales/Backwards.html` is completely translated, repaired downstream,
integrated, and visually inspected:

- frozen authority: 31,248 bytes / SHA-256
  `adae3d5409d9f698129b8b21dfe9f1cd8d3045e2bd3f79e42cbc70751b7b28ba`;
- Indonesian source: 32,504 bytes / SHA-256
  `cfc8490994e139e7c4c869fd1c431b1c0f3872af9247279bf0885472dfaa50c2`;
- built reader: 35,188 bytes / SHA-256
  `2a77650d3debb9dcce0218b58c2098d851c02fd1f482c08f31682c13d609c293`.

All 393 raw tag events, 202 opening tags, 13 legacy identifiers, nine
disclosures, ten units, and 426 ordered translation-source TeX surfaces are
preserved. The built page renders 445 MathJax containers and applies 26
exact-once reader actions: 25 source-content repairs and one deterministic
localization. Independent language, mathematical, and structural re-audits
found no publication veto. The SLLN proof records O006/C140 as an external
sampling prerequisite and duplicates none of its chapter-5 bytes.

The deterministic site contains 41 files / 2,551,660 bytes at manifest
SHA-256
`ad9e50cf0c063f9dac3aa68d9d0111820d2665ee0bb9d7b2c005ab9b6ce89108`;
build-receipt SHA-256
`bbc51c18a5498ff8820520f7dbb0913d0c56b6442b0ce109ec8dfe4b3266be29`.
The backend contains 957 entities, 2,482 segments, and 881 relations (3,439
semantic records), with zero QA failures; manifest SHA-256
`d6f0c4fe0bed616d29c77b33522cc7d27727cb317b78cda90bbb08647c7a623b`.

Whole-reader browser QA covered all 16 pages at 1280×720 and 390×844. Each
sweep rendered 9,025 MathJax containers and found 256 disclosures, with no
uncontained/document overflow, broken asset, empty alternative, unresolved
visible or fragment reference, external runtime, or reader-origin browser
warning/error. The mobile lab's wide R source remains inside its intentional
horizontal scroll container. The new page's desktop controls open 9/9 panels
and return to 0/9; its native mobile disclosure opens and closes through the
visible summary. See `qa/NINTH_BOUNDARY_CHECKPOINT_20260822.md`.

Commit `e8f7bedbd45ee8ad8a8463cbc76432c349bab973` (tree
`581b7589cb0e69cb2295bb14147d3d43b0e3b28f`) is public. Pages run
`32551382020`, job `96978596938`, and deployment `6033127490` succeeded. An
anonymous readback matched all 41 manifested files and 2,551,660 bytes at
2026-08-22T04:20:31.6178906Z. See `PUBLICATION_RECEIPT.json`.

## Next exact action

1. Continue in source order with
   `authority/random/static/markov/General.html` (74,595 bytes,
   SHA-256
   `69b4f54fd8c976d8a7093b3bfb9e0b3e836aa60794d1ad262e55c9b4b27f043c`).
   The Markov landing page is 9,248 bytes at SHA-256
   `18dfcf15b97a2af7d90404e879376234865bfb40985deb4d6e50b9778f5f7660`;
   its explicit unit order starts `General.html`, then `Potentials.html`.

The durable goal remains active. No PDF has yet been admitted because HTML is
the additive and accessible publication surface at this boundary.
