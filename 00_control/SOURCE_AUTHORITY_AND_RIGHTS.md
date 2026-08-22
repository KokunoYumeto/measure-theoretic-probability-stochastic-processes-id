# Source authority, closure, and rights

## Coordinator controls

These are inputs, not lane authority. Current hashes at lane startup:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/00_CURRENT_GOAL_AND_WORKFLOW.md` | 13,290 | `ba09f5eeacef5c62f17fc8565c2b5e619b924eb8315757cf67416479aef503f1` |
| `outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/09_CANDIDATE_SEARCH_CURRENT.md` | 48,507 | `4f66e3594aefc7bca490799595e6c17025143e27c80b37068e37ce8e6c9bfc6d` |
| `outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/05_MODULAR_BACKEND_INTEROPERABILITY_V0.md` | 5,204 | `fdb6c8fa87ea88d8fcb6ddf40415d8a6a6da315025b9b18eb917190f508b1c5f` |

## Random theory candidate

- Official authority: Kyle Siegrist, <https://www.randomservices.org/random/>.
- Upstream form: deployed semantic HTML containing TeX source, local CSS/JavaScript and image assets. No official public authoring repository, edition, tag, commit, archive, or build recipe has been found. Authority must therefore be expressed as exact URL bytes, response metadata, and hashes, not a fictional commit.
- Current O009 selection: 47 disjoint theory pages plus 3 authority pages and 44 direct assets = 94 files / 1,997,915 bytes.
- Canonical manifest: `authority/random/RANDOM_AUTHORITY_MANIFEST.csv`, SHA-256 `2ee154a38b57201457538db8c0e7df592a052eade8dcfda217605810f04f21e4`.
- Receipt: `authority/random/RANDOM_AUTHORITY_RECEIPT.json`, schema `o009.random-authority-freeze.v2`.
- First page: `prob/Convergence.html`, 39,189 bytes, SHA-256 `749de69aba8c7b54e5944ddbe4b342fec8695b32ff46e34409f7b6040241e34f`, Last-Modified `Fri, 13 Mar 2026 16:39:13 GMT`.
- Shared MathJax: `authority/random/shared/MathJax/tex-svg.js`, 1,704,911 bytes, SHA-256 `dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a`; MathJax 3.1.2 / Apache-2.0 license at `shared/MathJax/LICENSE`, 11,358 bytes, SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
- Excluded runtime: Google Analytics. The reader must be offline-capable and must not ship it.
- Cross-lane exclusion: Random `sample/LLN.html` and `sample/CLT.html`, and the rest of chapter 5, belong to O006/C140. O009 links that translated module as a prerequisite and does not fork/translate it.

### Random rights conflict

Two current official pages conflict:

| Witness | Bytes | SHA-256 | Statement |
|---|---:|---|---|
| `authority/random/static/index.html` | 22,462 | `a26f07b700c9de8c7ce83e5a2f38e1e676ed5b085fec8c4a52bb44abefaa8ba8` | links CC BY 2.0 |
| `authority/random/static/Credits.html` | 6,467 | `2d28d0293b41b71d08a531d37399205f657fbed77592c8f7acd54bf2a54113bf` | links CC BY 1.0 |

Both statements expressly permit copying, derivative works, distribution/display, and commercial use with attribution and a home-site link. Translation is permitted. The edition must preserve both witnesses and describe the version conflict; it must not state one unqualified version. Separately credited or unclear ancillary media must be excluded, replaced, linked, or licensed component-by-component.

### Current kernels component closure

`expect/Kernels.html` is admitted from the frozen Random selection at 53,030
bytes / SHA-256
`9dd2a5474f284fcb11c9e9f9e81099a1c4fe1708094bfcd64b08ccb9f82c5b8d`.
It introduces no substantive page-specific image, audio, data, or executable
asset. Its runtime references only the already frozen shared favicon, control
icons, `Screen.css`, `Basic.js`, MathJax, and `boldsymbol` closure. The
Random-derived translation retains `rights.random.dual-witness`; 34 explicit
downstream source repairs remain identified as repairs rather than relicensed
source. The original regular-conditional-distribution qualification and reader
palette changes remain separately identified as CC BY 4.0 edition additions.

### Current martingale-introduction component closure

`martingales/Introduction.html` is admitted from the same frozen Random
selection at 59,687 bytes / SHA-256
`ff102fd4f54926d89c47b92885176e587f342378e442f1f38e4a69199a02375a`.
Its page-specific image `martingales/Martingale.png` is also frozen at 67,648
bytes / SHA-256
`c7b5939b84f2a18776fc684f9b413a26fec315a684e35c7986c73a0efbb6cf4b`.
The source figure explicitly credits Danielle M., links the Wikimedia Commons
source record (`curid=13264705`), and identifies the image as CC BY 3.0. The
reader must preserve that visible credit and license link, copy the exact
frozen image, and bind it to a separate component-rights record rather than
placing it under Random's dual page-level witnesses. Other runtime references
are the already frozen shared favicon, controls, CSS, JavaScript, and MathJax.

## Žitković laboratory donor

- Official author route: Gordan Žitković’s UT Austin lecture-notes page linking the hosted book and public repository.
- Repository: <https://github.com/gordanz/stochastic-book>.
- Exact authority: `master@e2b35ad91a3689454ae6455e8ffc510a90760c0d`; parent `d5451c1330657b913a0aee58d56c8951d7040f3f`; tree `9947483e0cafa8dae52b2f6b0592860cf2e59c3d`; no tag/release.
- Exact codeload archive: 76,045,979 bytes, SHA-256 `25151c274360ce8228df138de3d2f9fa9895fa47112422c369d455725c53569e`.
- Archive census: 730 files / 97,549,488 expanded bytes.
- License: root CC0-1.0, 6,556 bytes, SHA-256 `6a1ee543e5282cd9061881edf462e6fdab181f328da71fc2c9a6950a80e94d01`. Adaptation and redistribution are permitted; attribution is retained as scholarly provenance. CC0 does not erase third-party rights.
- Whole-book build veto: 166 configured child sources are absent or home-local; `source/linkproblems` points into `~/teaching/problems`; no dependency lock/container/CI/session record exists; Chapters 9/10 are draft/stub. Do not represent the whole book as reproducibly buildable.
- Admitted donor policy: only exact, dependency-closed inline slices with no missing children/assets/packages.
- First proposed slice: `source/02-simulation.Rmd` lines 758–832, full file 57,963 bytes / SHA-256 `ce93a06c41bf6c6093c1cb7ca3d9dcde60fa52b317f7681ec30097d8e6117351`; raw slice 2,710 bytes / SHA-256 `e95fec79fc93f1239951864901c570b8aaa44e77c6a02be64d48bda4aa5c265f`. It uses base R only and has one exercise with a worked solution.
- Later Markov donor candidate: `source/05-Markov-chains.Rmd` lines 601–666, full file 34,298 bytes / SHA-256 `b350e2283aaeaf65b6bc29819bee5f7f41cdcefc6248f8356ce9d56b39e7354a`; slice SHA-256 `dcabe361eaaacaa537966f2bf8809dd8eac52e28392edc78d8e289c8c9be2bd8`.

## Imperial comparator — rejected as core

The bounded audit rejects `Samuel-CHLam/Imperial-Probability-Theory@48ace211871db3d57d5b5585f41c49f72abca81c` as the O009 core. Exact tree: `f766c30c287d8f31f6a1082228b0a3270d45135b`; archive: 15,304,794 bytes / SHA-256 `78b0db479a3f6b0fa7e0684f531b8ce82e4ff522ed8502dce02889c20fccf779`, 46 entries / 44 files.

The README/preface call the work unofficial student notes by Ivan Kirev and Samuel Lam based mainly on Igor Krasovsky’s lectures and other references, explicitly not checked by Krasovsky. The repository does not prove that its grantors controlled all incorporated expression. CC BY 4.0 appears in README/preface and is described as currently applicable; that temporariness is not itself fatal because a valid CC BY 4.0 grant is irrevocable, but licensor authority remains unproved. `includes.tex` retains a CC BY-NC-SA 3.0 template notice; nine of eleven active raster assets lack package-level rights evidence. There is no locked build/CI; the committed 125-page PDF is stale v0.1.3 while source is v0.1.7. Census: 58 exercises, 40 hints, one partial solution, zero answers; no adequate Markov, Poisson, renewal, or Brownian closure. Imperial remains an unincorporated comparator only.

## Final selection

Random’s 47 disjoint theory pages are the theory spine; O006/C140 supplies shared sampling/LLN/CLT prerequisites; Žitković supplies only exact dependency-closed CC0 lab slices; original bridge/mastery material is CC BY 4.0. Random’s downstream offline build and asset closure must pass at every boundary. If it fails, do not silently fall back to Imperial.

## Original additions

New bridge, mastery, accessibility, and execution-harness material authored in this lane is CC BY 4.0 unless a future file states otherwise. It must be visibly separated from Random-derived material and Žitković-derived lab material. There is no blanket license for the combined corpus.
