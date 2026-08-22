# Tenth reader-boundary checkpoint — 2026-08-22

Status: **public and anonymously byte-verified**.

## Added theory and laboratory closure

- Frozen Random authority: `authority/random/static/markov/General.html`,
  74,595 bytes, SHA-256
  `69b4f54fd8c976d8a7093b3bfb9e0b3e836aa60794d1ad262e55c9b4b27f043c`.
- Topology-preserving Indonesian source:
  `source/theory/markov/General.html`, 76,342 bytes, SHA-256
  `fb3026464841179c1480001ecda1e2ab28448a26ba6840f2f9571d6645831194`.
- Built theory reader: `build/site/markov/General.html`, 80,114 bytes,
  SHA-256
  `8adb839f1b7c7f41103dd24edb7cd5171ed305ca5c7160378cbc52da30fa542c`.
- Indonesian Markov-chain lab:
  `source/labs/02-simulasi-rantai-markov.Rmd`, 6,910 bytes, SHA-256
  `28e9b1c731082f9e590d74cf0b44922f5d45759851a7739bf1af1ad50bf09727`.
- Built lab: `build/site/labs/02-simulasi-rantai-markov.html`, 27,106
  bytes, SHA-256
  `d695b3ad98bb476690947211ccd2dd87374e14a48a442759ee3c88d19f7743c4`.

The theory translation preserves the authority's ordered element topology,
attributes, 44 identifiers, 102 links, six source references, four `onclick`
values, 23 disclosures, and all 925 ordered TeX surfaces. It is UTF-8,
NFC, LF-only, and has no BOM. The page introduces no new content asset; its
runtime closure is the already frozen Random UI plus local MathJax and
`boldsymbol` payloads.

The lab is a dependency-closed adaptation of Žitković
`source/05-Markov-chains.Rmd` lines 601–666 at frozen commit
`e2b35ad91a3689454ae6455e8ffc510a90760c0d`, slice SHA-256
`dcabe361eaaacaa537966f2bf8809dd8eac52e28392edc78d8e289c8c9be2bd8`.
The CC0 donor, CC BY 4.0 Indonesian adaptation, and CC BY 4.0 original
mastery material remain separate. No O006 chapter-5 byte is copied.

## Mathematical and execution gates

The frozen authority and faithful translation source remain unchanged. The
built reader applies 53 exact-once source-content repairs. These close
all-state kernel/conditional-version scope, Feller and strong-Markov
hypotheses, Chapman–Kolmogorov and density-at-zero domains, Kolmogorov
construction scope, product/random-clock measurability, recurrence/ODE and
random-walk domains, additive/Lévy regularity, Poisson/Gaussian time-zero
support, stopping-time notation, and localized display prose. Every old anchor
is absent and every new anchor occurs exactly once. The backend exports the
same 53 correction IDs. Independent mathematical and static re-audits found no
remaining high-confidence veto.

The lab executes under the pinned R 4.6.1/RNG harness and emits the exact row
`20260822,1000,100,1,3,592,0.592000000000,0.571428571429,0.571428571429,1.248349703776e-33,0.020571428571`.
The analytic tail gap `(4/7)(2/9)^50` remains visible even though it disappears
at 12 decimal places; the reader explicitly distinguishes that exact gap from
floating-point roundoff. The generated table, code ID, metadata, full edition
navigation, source hash, golden result, R executable/version/RNG, and Pandoc
executable/version are all bound and rechecked by `--check`.

## Deterministic artifact and backend gate

- Site: 43 manifested files / 2,661,986 bytes.
- `build/site/PACKAGE_MANIFEST.csv`: 3,985 bytes, SHA-256
  `c82e526a39a952f439ed11034ce8bbdcccb5deb853fef931a4336453780bf527`.
- `build/site/BUILD_RECEIPT.json`: 7,015 bytes, SHA-256
  `682a76f74952286f39bf1aafa1ff2939a8b0c0ea8602ee559efdb396d4175ac8`.
- Backend: 1,058 entities, 2,737 segments, 988 relations, 3,795 semantic
  records, eight recorded QA passes, and zero QA failures.
- `backend/BACKEND_MANIFEST.json`: 3,995 bytes, SHA-256
  `6f14a2e733baa821f264c8964fa8e4bcd64ab17bbfae21626832803abe6a3e73`.
- Backend input-set SHA-256:
  `0581b6e3068816ec48833486a8c077c0ee3056441fa575f46fef724021c86ab1`.

The deterministic build, check-only rebuild, strict backend validation,
source topology/TeX preservation, link/fragment/asset closure, privacy scan,
runtime probes, source/result receipt binding, stable-ID graph, and symlink
rejection all pass. The builder is 187,036 bytes at SHA-256
`7a8d426450d9e12ff9fb408912b342eb9dae566c44de0debb2193578b5d69310`;
the backend exporter is 162,937 bytes at SHA-256
`98f0267f30fe5fc71f5236e28e8046eea6a176ea93feca675f04529a313dc3ac`.

## Browser, interaction, accessibility, and reflow gate

The in-app browser inspected the index, all 15 theory pages, and both labs at
1280×720 and 390×844. Each 18-page sweep rendered 9,996 MathJax containers and
found 279 disclosures. Both sweeps had zero document overflow, broken image,
empty image alternative, empty visible reference, external executable
runtime, bad navigation count, or browser warning/error.

The new theory page rendered 918 MathJax containers and 23 disclosures at both
sizes. Its bulk controls opened 23/23 panels and returned to 0/23; a native
mobile summary opened and closed. The new lab rendered 53 MathJax containers,
one copyable stable-ID R block, the exact 11-column result row, and complete
reader navigation. The wide result table and R source scroll only inside
bounded containers. A discovered 22-pixel desktop table overflow was repaired
before this checkpoint; the final full-reader sweeps show zero overflow.

## Publication and next-cursor gate

Commit `2ef87fed687a7b2c8bc909d8e8993c6a4f136f4f` (tree
`6aae30c4cec3340bc2f0e6ee580c3c8143119538`) is public. Pages run
`32555221669`, job `96988207571`, deployment `6033729818`, and deployment
status `17153722812` all succeeded. At
2026-08-22T05:47:39.9902666Z, an anonymous readback matched all 43 manifested
files, all 2,661,986 bytes, manifest SHA-256
`c82e526a39a952f439ed11034ce8bbdcccb5deb853fef931a4336453780bf527`,
and build-receipt SHA-256
`682a76f74952286f39bf1aafa1ff2939a8b0c0ea8602ee559efdb396d4175ac8`.
The next action is to read and adopt the controlling material-root selection
packet before setting another translation cursor; `markov/Potentials.html` is
not inferred as the successor.
