# QuantEcon authority-admission checkpoint — 2026-08-22

Status: **exact source, rights witness, offline environment, and native build
baseline admitted; Indonesian component translation remains pending**.

## Authority and rights

The authoritative editable component is Thomas J. Sargent and John
Stachurski, *Continuous Time Markov Chains*, tag `publish-2026jul14`, immutable
commit `8b06e0aa5a438692445b2c896f9d238c5a7d5eb7`, tree
`f0f11e3bbc6bd23d6e4a447a7e05c0aaf0f7209e`. The commit ZIP is 240,751 bytes
at SHA-256
`ae12b4e7724b92c16d1caa3d42c82180fd67723212fe641b22594a1bbd5a4346`.
The expanded source has 34 files / 384,053 bytes and normalized manifest
SHA-256
`6b9c5ae0a04281259360124f0d432dea19ff03d10cb00ced0ae3499ded58d27c`.
The 17 active native-build inputs total 260,561 bytes at manifest SHA-256
`6caf088583fba12eab445490f8ef3cfbece2c23b0e47a715a5da7f2ed412beb6`.

The generated-notebook witness is commit
`1e17c25c937f369544380f769eb9c1bc45d12d1a`, 13 files / 501,361 bytes,
manifest SHA-256
`d0934f364b8655d114dc9f5e8469214909b8b7af20a9d69febf5bee1d12603ca`.
The official reader's 32,586-byte CC BY-SA 4.0 witness has SHA-256
`ff0dd3b21c95d225b2555710bdb6217d2963954cb95e34655711529d93209e46`;
the source repository has no root license file, so this witness remains bound.
QuantEcon branding and analytics are excluded from the Indonesian component.

`authority/quantecon/AUTHORITY_RECEIPT.json` is 10,953 bytes at SHA-256
`4c9694b57b46c3fb2173e3aea259c5641d409920add6484b77594d25a661863b`.
Its strict verifier passes 34 source files, 13 notebooks, all archive-safety
checks, the complete eight-chapter MyST topology, 25 exercises paired with 25
solutions, 35 source cells (33 chapter cells plus two status cells), 36 empty
generated-notebook cells, and the exact selected/excluded asset partition.

## Offline environment

The clean replay resolves 160 distributions to 160 exact wheels totaling
180,231,134 bytes. The byte-exact resolver/replay freeze SHA-256 is
`d830e291a14fc4012cd54b53d8700f9f16fb01c4e0f6cfa91018fd38bba7708f`;
the hash-required lock SHA-256 is
`9c4464dc9e5705a095ec07cdf943331bd84025460eff3bc202f1ebab29cdb577`;
the wheel manifest SHA-256 is
`b967b4d80e739d0b59020acdce19f524d3b3f4e2ae63af5d7c654dc6ec84248b`.
The 31,851-file / 763,434,580-byte replay tree has SHA-256
`6ee8d8ca56a76cb6ec364f71552e89f122f314d8439bb1e427422d906def2335`.
Both `pip check` probes pass; NumPy, SciPy, Matplotlib/Agg, Numba, QuantEcon,
Jupyter Book, Sphinx, and every configured extension import and execute.

The strict `--check` mode proves the receipt, frozen outputs, and replay tree
unchanged. `ENVIRONMENT_RECEIPT.json` is 9,857 bytes at SHA-256
`07f5a093e11c7405b9529e7620037f8a2695180843ade6dc4ebc9c40a53b2755`.
Wheel binaries and virtual environments remain local and Git-ignored; the
public source retains the exact hash lock and per-wheel manifest.

## Disposable-copy native baseline

Frozen snapshots are never build workspaces. An initial attempt exposed that
upstream `markov_prop.md` rewrites its source `flow_fig.png`; the verifier
caught the mutation before admission, and the immutable archive restored the
104,771-byte asset at SHA-256
`54906c3f6f48664960d25ead98af1150014e88367db1d604f6ccc9d01e50564f`.
The full authority manifest then passed again. Both admitted builds use fresh
17-file disposable copies, and authority checks pass before and after.

The locked offline native HTML command succeeds with 98 files / 6,349,351
bytes and manifest SHA-256
`b40177b0b9f176ae5e130a490963ac1acbbafbde8c1a8a58a6a29842e6ee09ab`.
It is not byte-identical to the hazard-only first build: 73 paths match and 25
differ, so no upstream byte-determinism claim is made.

The native PDF wrapper produces the complete LaTeX tree, then Jupyter Book
1.0.4.post1 on Windows fails to locate its own bare `make.bat`. Executing the
generated batch explicitly with package installation disabled succeeds and
produces an untagged 92-page / 451,761-byte PDF at SHA-256
`bda190957516c405c75505af5a05df3a7bd83159226c8ce1f2577de611c2d24f`.
The official 100-page PDF remains an independent witness, not a build input.

`NATIVE_BUILD_BASELINE.json` is 6,674 bytes at SHA-256
`56cfa007c532a73d49518d11e8ce83fb5f6a80801b727e416d1aa8c9d43bc949`;
`python -B scripts/verify_quantecon_native_build.py --check` passes.

## Admission limits and next cursor

The native output is not publishable reader output. It contains remote
runtime/resource links, Google Analytics, QuantEcon theme branding, Colab UI,
local Windows paths, notebook warnings, missing image alternatives, unresolved
references/proof-index locators, and an untagged PDF. The downstream component
adapter must remove or repair each item, preserve CC BY-SA attribution and
source topology, execute from the locked environment with explicit seeds and
targets, and separately prove deterministic accessible HTML/PDF.

These hazards do not veto the editable source: authority, rights, source
closure, mastery closure, environment, and native buildability are now proven.
The exact next production cursor is the complete id-ID translation of selected
Random `markov/Discrete.html`. QuantEcon translation begins only after the four
selected Random discrete-Markov pages.
