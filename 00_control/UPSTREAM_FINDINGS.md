# Deferred upstream findings

This is the internal, deduplicated evidence queue for the complete O009/D30
edition. No upstream contact occurs during production. After the entire corpus
is complete, and only with separate authorization, collapse high-confidence
items into at most one concise report signed `Codex — at the user’s direction.`

## `prob/Probability2.html`

- Authority line 486 links `href="#tai1"`, but no such ID exists. The sentence
  invokes the immediately relevant result that `limsup` is a tail event, whose
  authority ID is `tai12` at line 441. The downstream reader rewrites only this
  rendered link to `#tai12`; the frozen authority and topology-preserving
  translation retain the original bytes.

## `prob/Processes.html`

Mechanical/prose candidates retained for later deduplication:

- Lines 115, 118, and 119: malformed phrases including “versions of”, “is ia
  version,” and an omitted “version” in the transitive clause.
- Line 146: mismatched TeX delimiter in `\P(...\}`.
- Line 149: bare `P` where the surrounding notation uses `\P`.
- Line 194: `I` is undefined in context.
- Line 201: `N` versus `N_+` domain mismatch.
- Line 225: misspelling “consistence.”
- Lines 246, 261, and 271: grammatical defects.
- Navigation title at lines 41 and 296: “Revisted.”

Substantive candidates requiring a tightly scoped mathematical formulation:

- Around line 82, the claim that statements involving countably many indexed
  variables are measurable needs assumptions on the index sigma-algebra (for
  example measurable singletons/discreteness), not merely countability.
- Around line 168, the projection of an arbitrary measurable subset of a
  product measurable space need not be measurable in general.
- The Kolmogorov existence statement, as phrased for an arbitrary measurable
  state space, omits regularity/standard-Borel-type hypotheses normally needed
  for that generality.

All source formulas and claims remain unchanged in the translation. Any
pedagogical qualification belongs in separately licensed connective material,
not in an unmarked silent alteration.

## `prob/Stop.html`

- `id="dnf2"` appears to be a transposition of `dfn2`.
- The display `\( \mf H = \ms H_t: t \in T\} \)` lacks the opening `\{`.
- The second `dfn3` list item and first `alg4` detail item lack closing
  `</li>` tags; `alg8` lacks `</p>` before `</details>`.
- The introduction says `\P` is a measure on `(S, \ms S)` rather than on the
  stated probability space.
- `prc6` uses `\subseteq` where membership of an event in a sigma-algebra calls
  for `\in`.
- Footer navigation labels `Processes` as item 9 although the header gives it
  item 8; both also contain the source spelling `Probability Spaces Revisted`.

The topology-preserving translation retains these source structures and
formula bytes. Indonesian reader-facing tooltip text is translated separately,
which the structural validator expressly permits.

## `expect/Conditional2.html`

- Jensen-related displays around authority lines 204 and 223 are malformed.
- Several formulas inconsistently use bare `E`/`P` instead of the established
  `\E`/`\P`; an obsolete or undefined `\scr G` also appears.
- Bracket/parenthesis defects occur around lines 378, 505, and 512.
- Three list items are not closed.
- Around line 502, the prose says “conditioning on X” while the displayed
  formula conditions on `\mathscr G`.
- Mechanical candidates include `repsect`, `coonditions`, `witl`, and
  `subsituting`.

These bytes remain preserved pending exact deduplication at corpus completion.

## `dist/Convergence.html`

- In the geometric-limit proof, malformed inline math beginning
  `\(x \in [0, \infty)` absorbs the intervening English clause through the
  later `\(r\)` delimiter. The translation preserves the malformed authority
  math span byte-for-byte so the defect remains auditable rather than silently
  changing source mathematics.

## `expect/Uniform.html`

- The stated `\mathscr L_k` norm omits an absolute value.
- A threshold changes between `\ge` and `>` without accounting for the boundary.
- One passage uses undefined `X` where the indexed `X_i` is intended.
- A scaling expression has `ca` where `|c|a` is needed.
- `\mathbb N` and `\mathbb N_+` are used inconsistently.
- An expectation/colon expression is malformed, and Fatou limits indexed by
  `n` do not match the displayed subsequence `X_{n_k}`.
- The final conditional-expectation example has a strict-inequality gap.

All are preserved as authority findings pending final deduplication.

## `expect/Kernels.html`

The frozen authority and the topology-preserving translation retain the exact
source formulas. The built reader applies only the following high-confidence,
machine-recorded repairs; every replacement is asserted to match exactly once.

- Lines 91, 116, 122, 132, and 133: one omitted `</li>`; `{A_j: i \in J}`
  should use `j`; the kernel-measurability proof needs `A \in \mathscr T`;
  the norm assertion is an inequality, not equality for arbitrary `f`; and
  `Kf` belongs to `\mathscr B(S)`, not `\mathscr B(T)`.
- Lines 196, 228, and 246: use `L(y,A)` in the composition integral, integrate
  the right action over `T`, and quantify the composed function at `x \in R`.
- Lines 273–283: the last two distributive identities need separate functions
  on `S`; positive measures form a cone, so their action is additive and
  positively homogeneous rather than linear over all real scalars.
- Lines 296–299, 317, and 319: invariant measures/functions require an
  endokernel on `S`; write `(PQ)(x,T)`; remove one stray parenthesis.
- Lines 348, 352, 383, and 410: two kernel-function integrals are over `T`, the
  second doubly stochastic condition ranges over `y \in T`, and the composed
  density concludes with the target reference measure `\rho(dz)`.
- Lines 422 and 426: the discrete right action sums over `T`; composition uses
  `L(y,z)` and has output domain `S \times U`.
- Lines 486–491: a regular conditional distribution need not exist on arbitrary
  measurable spaces and is determined only almost everywhere. The reader adds
  a separately licensed note giving the standard-Borel sufficient condition
  and the version/zero-set qualification.
- Lines 509 and 534: integrate the conditional distribution over `T`, and
  restore the missing equality sign in the normal-mixture calculation.
- Lines 586, 597, and 606: delete a duplicated empty integral; for `g(r)=r`,
  the Poisson left action is `gP=f+1` and the value is `n+1`, not `n`.
- Lines 619 and 629–630: density powers use `n \in \mathbb N_+`, and the
  squared-normal-kernel formula must use one output variable consistently.
- Lines 649, 652, and 654–655: the general normal exponent needs the factor
  `1/2`; the beta density needs `(1-x)^{b-1}`; and the negative-binomial
  parameter space/order is `\mathbb N_+ \times (0,1)` with
  `p[(k,\alpha),n]`.

Minor source prose/markup candidates include the misspelling `kerneal`, the
duplicated “If If,” and the omitted list close noted above. Natural Indonesian
calques were repaired in translation prose without changing source formulas.

## `martingales/Introduction.html`

The frozen page is 59,687 bytes at SHA-256
`ff102fd4f54926d89c47b92885176e587f342378e442f1f38e4a69199a02375a`.
Its translation source preserves all 741 ordered TeX surfaces. The built reader
repairs only exact, separately recorded defects; it does not alter the frozen
authority.

- Lines 177, 206, 222, 277, 412, and 433 use bare `E` where the page's defined
  expectation macro is `\E`.
- Line 436 incorrectly squares `\var(X_t-X_s)` and omits the closing bracket
  in `\E[(X_t-X_s)^2]`.
- Line 460 defines `b^2` from the level `X_1`; the claimed stationary-increment
  variance formula requires the unit increment `X_1-X_0`.
- Lines 535 and 539 disagree on whether the offspring sum starts at 1 or 0;
  starting at 0 introduces an extra term. Line 536 calls the already defined
  offspring mean `\mu` instead of `m`.
- Line 263 says the partial-product process is associated with `\bs X` rather
  than its input sequence `\bs V`.
- Line 396 defines stationary increments for every pair `s,t` without the
  required order `s\le t`, so `X_{t-s}` need not be defined on the stated time
  domains.
- Line 567 restricts the density construction to `n\in\mathbb N_+` even though
  the process, hypotheses, and proof all include `X_0` and `n\in\mathbb N`.
- Lines 140–141 leave substantive prose outside a paragraph; lines 473–477
  omit a paragraph close before an ordered list. The downstream HTML parser
  closes the latter implicitly, but both remain source-markup findings.
- Line 306 truncates the visible phrase “simple symmetric random walk” before
  “walk.”

Mechanical prose candidates include `process\(`, `attachement`, `Them`, a
missing possessive in “gamblers net fortune,” duplicated `that that` and `and
and`, `number of success`, `number of red ball selected`, `martinagle`, a
missing sentence break before “So,” and missing “of” in “the children a
particle.” These are translated naturally rather than imitated as Indonesian
typos. No upstream contact occurs during production.

## Cross-page empty heading references

The source leaves `.ref` anchors empty while targeting headings rather than
numbered `.unit` elements. `Basic.js` populates only the latter, so these links
render with no visible text. The downstream reader supplies explicit Indonesian
labels without changing the frozen authority or translation sources:

- `dist/Convergence.html`: one `#sko` reference;
- `martingales/Introduction.html`: two `#asm`, one `#inc`, three `#sum`, two
  `#wlk`, and one `#prd` references.

All ten are backend-recorded source-link repairs. The browser gate now requires
zero empty `.ref` anchors across the whole reader.

## `martingales/Properties.html`

The frozen page is 37,473 bytes at SHA-256
`0f8bc07eb5eda38e8d4f78e94ba71a7dae8e9b788278f9b6ed250b0f66dc3850`.
Its translation source preserves all 520 ordered TeX surfaces. The built reader
applies only exact, separately recorded repairs:

- The page's relative MathJax path does not resolve inside the official static
  tree; the reader maps it to the frozen local MathJax closure. The favicon
  declares `image/svg` instead of `image/svg+xml`.
- Three expectation relations use undefined `\frak` where the page otherwise
  uses `\mathfrak`.
- Four references to heading IDs (`#pre` and `#wlk`) are empty and remain blank
  under `Basic.js`; the reader supplies visible labels.
- Doob decomposition uniqueness needs the normalization `Z_0=0`.
- The Doob–Meyer paragraph is false for an arbitrary adapted integrable class-D
  process; the reader states the càdlàg sub/supermartingale hypotheses,
  predictable monotone compensator, and zero normalization.
- The harmonic-function converse is global on the state space only when the
  martingale assertion holds under every initial-state law `P_x`.
- The simple-walk gambling paragraph cites `#wlk1` rather than the martingale
  transform and omits the integrability argument for unbounded bets.
- The De Moivre alignment omits an equality sign.
- The claim that `X_n/m^n` cannot be a state-only function has the exception
  `m=1`; the general representation is the space–time function `H(n,x)=x/m^n`.
- The final identity-function introduction is truncated.

Minor source prose and markup defects remain queued for final deduplication. No
upstream contact occurs during production.

## `martingales/Stop.html`

The frozen page is 43,887 bytes at SHA-256
`8d4c674bec0d19a253405dfe8c06e4b4062d6ef82330f945d50e2c494955a5af`.
Its Indonesian translation preserves the exact source topology, all 30 IDs,
all 69 ordered `href`/`src` references, 18 detail panels, and all 580 ordered
TeX surfaces. The built reader makes only exact-once, backend-recorded repairs.

- The first optional-stopping theorem omits both stopping-time variables from
  its premise, and one restricted-expectation formula uses a colon instead of
  the page's semicolon convention.
- The stated unbounded-time counterexample points to `#srw2`; `#srw3` is the
  example that actually violates the conditional optional-stopping identity.
- The stopped-process definition hard-codes `[0,∞)` despite the page also
  covering discrete time. Its transform conclusion writes `X_τ` instead of
  the stopped process `X^τ`, and three ensuing relations use bare `E` rather
  than the defined `\E` macro.
- A second empty `<summary>` occurs inside one detail panel. The favicon uses
  the nonstandard media type `image/svg` rather than `image/svg+xml`.
- The two-sided exit-time calculation cites the bounded-stopping-time theorem
  `#ost1`, although the exit time is unbounded; its established finite mean and
  bounded increments support the discrete theorem `#dis2` instead.
- The proof of Wald's equation bounds only the *expected* increment magnitude
  and then invokes `#dis2`, whose hypothesis is an almost-sure uniform bound.
  The reader replaces this with bounded stopping followed by an explicit
  `L¹` convergence argument and states integrability explicitly.
- The pattern-waiting proof calls total gambler wealth a mean-zero martingale
  even though one unit of new capital enters at every trial. It also uses a
  false strict bound, an undefined `N`, an inadequate increment bound, and
  inconsistent bold-word subscripts. The reader uses net gain `W_n-n`, proves
  finite mean and bounded increments, and identifies deterministic terminal
  wealth through prefix–suffix overlaps.
- The 001 worked example repeats gambler `N-2`; the second gambler is `N-1`.
  The secretary sequence displays `a_0` through `a_10`—eleven terms—not ten.
- The secretary proof omits time zero from the filtration and sets `Y_0=0`
  while later requiring `E(Y_0)=a_n`. The reader includes the trivial
  time-zero sigma-algebra, sets `Y_0=a_n`, and repairs the expectation macro.

The reader also completes two Indonesian phrases embedded in source TeX and
normalizes one Indonesian optional-stopping term. Those localization actions
are not upstream findings. No upstream contact occurs during production.

## `martingales/Inequalities.html`

The frozen page is 38,731 bytes at SHA-256
`9e03259e83a9e8ac67c9a43a2df1aa8a85d65944f86b82653e46869f4ab451f3`.
The Indonesian source is 40,512 bytes at SHA-256
`f7327659431ab0f8a7b6f696474e4b0e57e7dd138ba0374c5f722a31781161b6`
and preserves all 550 ordered TeX surfaces. The built reader applies 22
exact-once source-content repairs and four deterministic mobile reflows:

- the discrete maximal proof uses the unbound `U_t` three times where its
  fixed horizon requires `U_n`;
- the continuous maximal proof asserts a false closed-threshold identity on
  finite dyadic grids, invokes monotone convergence on a signed integrand, and
  contains `P`/`X` notation slips; the reader uses relaxed thresholds,
  continuity of probability, and dominated convergence;
- the integral maximal inequality drops a factor `1/x`;
- the nonnegative-supermartingale proof sets `Y=-X` but falsely claims
  `Y^+=X`; the reader uses stopped processes and finite dyadic grids;
- three occurrences use an undefined total-upcrossing symbol, while a fourth
  counts failed stopping indices by writing `t_k <= infinity`;
- the discrete upcrossing theorem states both supermartingale and
  submartingale bounds but proves only the first; the reader supplies the
  complementary predictable-transform proof and corrects the transform's
  initial-value/index convention;
- the continuous upcrossing criterion permits two fixed repeated times, and
  its proof chooses an unjustified path-dependent cofinal family; the reader
  requires alternating times and uses measurable entrance times with
  deterministic inward-relaxed dyadic grids;
- the red-and-black application omits nonnegative-stake admissibility, uses an
  inconsistent transform convention, cites `#max5` instead of `#max7`, and
  overstates what the displayed estimate proves for `p<1/2`; the reader proves
  the fortune supermartingale directly and confines the displayed optimality
  conclusion to the fair case while retaining the separate subfair theorem
  link;
- the favicon media type and three short TeX prose remnants are normalized in
  the built reader; and
- four long upcrossing displays are split into aligned lines without changing
  their mathematics so they remain readable at phone width.

No exercise or solution block occurs on this page. No upstream contact has
occurred; retain only deduplicated high-confidence items for the one possible
post-corpus report, if separately authorized.

## `martingales/Convergence.html`

The frozen page is 44,951 bytes at SHA-256
`c5ef4134737d39992647bc1bf7ab4c9b16814f11450e53e7f54642ec64bdea0f`.
The Indonesian source is 47,368 bytes at SHA-256
`da3c58c6260e21b9c04a67bdb18656bfcaabea4d7f8ee83b8f9538d0668a5747`
and preserves all 722 ordered TeX surfaces. The final built reader applies 30
exact-once actions: 27 source-content repairs, two deterministic mobile
reflows, and one source-link repair.

- The first convergence proof mixes discrete and continuous upcrossing
  references, uses an undefined total-upcrossing index, states a strict bound
  where only a non-strict limit bound follows, and names `X` rather than
  `X_infinity` in the terminal measurability claim.
- The uniform-integrability proof has a broken theorem URL, uses `X` instead
  of `X_infinity` in mean convergence, and does not justify passage of
  conditional expectations to the limit. The Lp theorem is false as stated
  for arbitrary sub/supermartingales and one maximal estimate drops its norm
  subscript.
- The simple-walk application defines increments at an undefined time zero,
  starts the partial sum at that undefined increment, gives the wrong state
  space, and diagnoses the failed convergence hypothesis only through the
  mean—missing the symmetric case.
- The branching paragraph overstates an exponential divergence rate and what
  the normalized martingale proves on nonextinction. The beta–Bernoulli page
  omits the argument transferring convergence to the sample mean; the Pólya
  prose confuses draw counts, sample proportions, and urn composition and
  leaves `M_0=Y_0/0` if the time domain is not restricted.
- The likelihood-ratio proof applies a strong law without handling an
  infinite negative log mean and invokes continuity of the logarithm at zero.
  The partial-product discussion indexes an undefined normalized term and
  typesets the normalizer outside the product, leaving its index free.
- The density proof uses inconsistent expectation notation and undefined
  terminal-measure symbols. For a signed measure it falsely assumes that
  ambient Jordan parts remain absolutely continuous after restriction to a
  coarse sigma-algebra; cancellation makes this false. It also equates the
  total variation of every restriction with ambient total variation. The
  reader instead uses the restricted-variation bound, Fatou's lemma, and a
  monotone-class argument against a full-probability total-variation-null set.
- The dyadic measure example omits parentheses around the interval argument.
  Two long displays are reflowed for phone width while retaining the exact
  integer domain. One empty reference to the Doob heading receives visible
  Indonesian link text.

The first candidate reader build was vetoed because its own dyadic reflow
dropped the integer domain and its first signed-measure repair still relied on
ambient Jordan parts. Both defects were corrected before publication; they are
edition-process findings, not additional upstream defects. No exercise or
solution block occurs on this page. No upstream contact has occurred.

## `martingales/Backwards.html`

The frozen page is 31,248 bytes at SHA-256
`adae3d5409d9f698129b8b21dfe9f1cd8d3045e2bd3f79e42cbc70751b7b28ba`.
The Indonesian source is 32,504 bytes at SHA-256
`cfc8490994e139e7c4c869fd1c431b1c0f3872af9247279bf0885472dfaa50c2`
and preserves all 426 ordered source TeX surfaces. The built reader applies 26
exact-once actions: 25 source-content repairs and one deterministic
localization.

- The continuous-time convergence statement needs path regularity; the reader
  uses a left-continuous/right-limit version so finite time reversal supplies
  the regularity required by the ordinary martingale theorem.
- The finite-horizon upcrossing bound names `X_t` rather than the defined
  `X_t^t`, and the expanding positive horizon is sent to negative instead of
  positive infinity. Two expectation/conditional-expectation displays also
  contain macro or parenthesis defects.
- The terminal-identification proof neither proves
  `G_infinity`-measurability nor supplies a dominator. The reader defines the
  integer-time limit, proves terminal measurability, and uses the established
  L1 convergence to identify the conditional expectation.
- The SLLN reverse filtration is defined on inconsistent integer domains and
  invokes a theorem stated from time zero without shifting its positive-index
  process. The reader aligns the domains and records the explicit shift. It
  links, rather than duplicates, the O006/C140 sampling chapter.
- The elementary de Finetti argument starts a bit-string sum at an undefined
  coordinate, starts its tail intersection before the fields are defined,
  conditions on possibly null totals, conditions the indicator on the wrong
  sigma-algebra, cites the wrong construction result, and omits explicit
  integrability.
- The second de Finetti martingale uses `Y_m` instead of the conditional mean
  `(n/m)Y_m`, does not shift its positive index, and its last conditioning step
  omits the tower property. The general statement also needs standard-Borel
  scope and must restrict arithmetic sample means to integrable real-valued
  variables. A final product-space pair omits its comma.

No exercise or solution block occurs on this page. No upstream contact has
occurred; retain only a concise deduplicated subset for the one possible
post-corpus report if separately authorized.
