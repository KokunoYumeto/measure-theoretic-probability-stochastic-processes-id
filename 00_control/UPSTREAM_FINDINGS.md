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

## `markov/General.html`

The frozen page is 74,595 bytes at SHA-256
`69b4f54fd8c976d8a7093b3bfb9e0b3e836aa60794d1ad262e55c9b4b27f043c`.
The Indonesian source is 76,342 bytes at SHA-256
`fb3026464841179c1480001ecda1e2ab28448a26ba6840f2f9571d6645831194`
and preserves all 925 ordered TeX surfaces. The final built reader applies 53
exact-once source-content repairs.

- Pointwise conditioning on possibly null states is replaced downstream by a
  consistent Markov family/all-state kernel formulation; standard-Borel and
  regular-conditional-version scope is made explicit.
- The Feller definition, infinite-discrete-state qualification, càdlàg
  realization, and strong-Markov filtration/path hypotheses are corrected.
- Chapman–Kolmogorov uses the correct time variables, kernel proof, density
  side, almost-everywhere scope, and absolute-continuity/time-zero conditions.
- The finite-dimensional construction receives standard-Borel scope; random
  time change, product-state enlargement, finite-memory, and two-step kernels
  receive their missing domains and measurability conditions.
- The deterministic recurrence, ODE flow, and random-walk examples receive
  the correct function/state domains and operator notation.
- Additive-state/increment support, continuous-time Lévy convention,
  stochastic continuity, moment regularity, and zero-variance cases are
  stated explicitly.
- Poisson support/time zero and Gaussian identity-kernel/time-zero density are
  separated correctly; the density convolution identity is asserted only
  when the relevant densities exist.
- Filtration, stopping-time, stopped-state, dimension/index, product-space,
  link-label, and embedded-language defects are normalized downstream.

No exercise or solution block occurs on the Random page. Its matched lab adds
a separately licensed mastery sequence and deterministic diagnostic; those
edition additions are not upstream findings. No upstream contact has occurred;
retain only a concise deduplicated subset for the one possible post-corpus
report if separately authorized.

## `markov/Discrete.html`

The frozen page is 55,099 bytes at SHA-256
`808118b103e17cd5e31115b953663b0d8ff94da21f432e6fe7c104e9300380f0`.
The Indonesian source is 57,545 bytes at SHA-256
`176d4f9284ee16353142d6c2612b46a32a93c416471621997c89e72308b785ea`
and preserves all 530 parsed elements, 649 ordered TeX surfaces, 56 unique
identifiers, 30 disclosures, and four image alternatives. The built reader
is 65,408 bytes at SHA-256
`9b21e65c3da1c7989c99adee09da517634ca186d31c2a3886f51d65c9686a2b8`
and applies 44 exact-once actions: 34 source-content repairs, six source-link
repairs, and four deterministic mobile reflows.

- The elementary history-conditioned Markov formula is restricted to
  positive-probability histories, and time homogeneity is expressed through
  a consistent all-state transition family. The strong Markov statement is
  correspondingly restricted to homogeneous chains, written with the
  stopped-state transition kernel, and its future-law prose distinguishes an
  almost-sure conditional identity from the all-state extension under
  `(P_x)_{x in S}`.
- Enlarging a countable discrete-time state space by the time coordinate gives
  `S × N`, which remains countable; the source incorrectly calls it
  uncountable. Entrance/positive-hitting-time index domains and the possibly
  absent or infinite last-visit time are made explicit.
- The stochastic row-sum uses `P_n`, not `P`; an `(n+1)`-state path belongs to
  `S^{n+1}`; and two transition-law references point to the wrong result or
  omit the fragment marker. The n-step expectations and finite-dimensional
  law are consistently stated under the all-state family; the latter is
  proved by tower recursion rather than a chain rule through null histories.
- The potential-matrix definition is made entrywise, the expected visit count
  is conditioned on its stated starting state, a probability is corrected
  from an expectation symbol, the geometric support is `N`, and the economic
  multiplier is called a discount factor. An undefined `q^k` becomes
  `beta^k`, and the shift identity cites the defining series.
- General sampling now defines `n_0`; the restricted-matrix path formula is
  stated for positive time with `P_A^0=I_A` separately.
- The published two-state resolvent is false even at discount zero. The
  downstream spectral decomposition was symbolically checked against
  `(I-alpha P)^{-1}`. A second three-state potential matrix uses an undefined
  scalar `a`; all occurrences are corrected to `alpha` and the resulting
  formula was independently checked.
- The integer-state and doubly-stochastic symbols are normalized. The broken
  `trn5` fragment and lowercase `limiting.html` URL are repaired, and the SVG
  media type is corrected. Four long equality chains are reflowed without
  changing their mathematics.

The source has 115 opening paragraph tags but 113 closing tags, including an
ordered list nested in the `pot8` paragraph. The deterministic HTML parser
normalizes those two markup defects in the reader; the frozen and translated
source topology remains unchanged. The page contains seven explicit exercise
units with seven worked disclosures. Its TwoState simulation is an external
Random ancillary, not a frozen offline app; the existing gambler's-ruin lab is
not misrepresented as a replacement. No upstream contact has occurred; retain
only a concise deduplicated subset for the one possible post-corpus report if
separately authorized.

## `markov/Recurrence.html` — pre-build correction audit

The frozen selected page is 51,381 bytes at SHA-256
`24edb8bd0237b0e3abd7beeae48596f35421c9aa35653c6845cfaebb223c5535`.
It has 519 parsed elements, 48 unique identifiers, 35 unit blocks, 27
disclosures, six content figures, ten images, and 698 ordered TeX surfaces.
The authority and all six content PNGs are complete; the shared Random/MathJax
closure supplies the remaining offline runtime.

- The first finite-chain example prints the first transition row as
  `(1/2, 2/3, 0, 0)`, which sums to `7/6`. A July 16, 2009 print capture of
  Kyle Siegrist's former official UAH `Recurrence.xhtml` page shows the same
  row as `(1/3, 2/3, 0, 0)` on PDF page 9. That historical source-lineage
  witness resolves the otherwise ambiguous correction to `1/3`; the current
  Random page and its LibreTexts derivative both retain the later `1/2`
  regression. Witness URL:
  `https://www.dipmat.univpm.it/~demeio/Alabama_PDF/16.%20Markov_Chains/Recurrence.pdf`.
- The first-hit convolution statement is correct, but its proof sums over an
  impossible/infinite range and substitutes `P^k(x,y)` where
  `P^{n-k}(y,y)` is required. The first-step proof for `H_{n+1}` similarly
  substitutes `H_n(x,A)` where `H_n(y,A)` is required.
- The recurrent-visit proof contradicts its correct statement by concluding
  `P_x(N_y=infinity)=1-H(x,y)` rather than `H(x,y)`, and its final item cites
  the transient theorem instead of the visit-count distribution.
- The page conditions repeatedly on possibly null initial-state events. The
  reader must bind these expressions to the all-state family `(P_x)_{x in S}`
  established in the preceding unit. First-positive hitting and restricted-
  path formulas also need their `n=1` empty-intersection and `n=0` identity
  cases stated explicitly.
- The transitivity proof uses undeclared `N` instead of `\N`; singleton
  closures are written ambiguously as `cl(y)` and `cl(x)`; thirteen generated
  internal references lack static fallback labels. Deterministic grammar,
  spelling, favicon-media-type, image-alternative, and long-matrix reflow
  repairs are also required.

No authority byte is changed and no upstream contact has occurred. The exact
downstream correction count, target/build hashes, and final disposition will
be frozen after the Indonesian reader boundary passes independent review.

## `markov/Limiting.html` — checkpoint 16 correction audit

The frozen authority is 50,069 bytes at SHA-256
`d4719c5e1cb9ad3be4fbf84c8dd849390f7d1ad15ced112f6312be83e5545680`.
The Indonesian source is 51,577 bytes at SHA-256
`9ab9164c51069883a19cc2da591afd1019d214a497c743a8ef42491fd16e9c42` and
preserves 581 TeX surfaces, 38 identifiers, 22 disclosure panels, five
exercise/solution pairs, and all five source figures. Corrections are
downstream-only; the frozen authority and source translation remain intact.

- The renewal/counting theorem mixed `N_{n,y}` and `N_{y,n}` and asserted a
  probability equal to `H` without the finite-mean/null-recurrent qualification.
  The reader states the robust almost-sure limit and the conditional/finite-
  mean scope explicitly.
- Delayed-renewal and first-delay arguments were missing the hit conditioning
  or strong-Markov qualification; these hypotheses are now visible.
- The averaged-index identity uses the shifted increment
  `G_{n+i+j}-G_{i+j}`; the invariant-limit citation and the zero-​probability
  branch in the invariant-vector exercise are repaired.
- The finite examples contain arithmetic/normalization defects: the fifth
  return is `19/9` (not `19/8`), the limiting row has `1/10,1/10`, and the
  final normalizers are `1/595` rather than `1/585`; punctuation and the
  missing comma are restored.
- The seven-state graph omitted the `d→d` self-loop. Its visible edge prose,
  exact matrix, and image alternatives now agree. Empty references, malformed
  paragraph/list topology, and the missing `</ol>` are repaired in the built
  reader, while the source topology remains evidence-bound.
- The authority's JavaScript-only TwoState app is not an offline reader
  surface. An original deterministic two-state simulator is supplied as a
  separately attributed CC BY 4.0 addition and is clearly not presented as
  upstream or endorsed.

No upstream contact has occurred. These findings are retained for one possible
future deduplicated report only after the full corpus is complete and separately
authorized.

## Checkpoint 16 preservation finding

The 193-page reader and 56-file HTML/backend boundary passed structural, math,
link, asset, privacy, accessibility qualification, and representative visual
QA. Zenodo record 22070728 / DOI `10.5281/zenodo.22070728` is public and every
one of its six files was anonymously SHA-256 verified. Figshare's exact
metadata-only package is locally valid, but its authorized publish attempt
returned HTTP 403 `InactiveAccount` before mutation; see
`00_control/FIGSHARE_PUBLICATION_BLOCKED_CHECKPOINT_16.json`. No upstream
message or GitHub retry was made.

## QuantEcon `memoryless.md` — checkpoint 17 finding

The frozen authority is the QuantEcon `continuous_time_mcs` source at commit
`8b06e0aa5a438692445b2c896f9d238c5a7d5eb7`, tree
`f0f11e3bbc6bd23d6e4a447a7e05c0aaf0f7209e`, with the official CC BY-SA 4.0
witness naming Thomas J. Sargent and John Stachurski. The bounded first unit
contains two exercises, two solutions, and five executable cells. The
downstream target preserves the source formulas/topology and uses a local
offline build; no upstream authority bytes were changed.

The donor solution for the first exercise had an invalid `s−t` branch. The
reader corrects it with the mathematically valid cases `t≤s` and `t>s`; the
correction is explicit in the component receipt and backend. The downstream
adapter also removes only the package-install directive for offline replay,
adds figure alternatives, and removes remote theme/analytics runtime. These
are bounded reader-layer changes, not claims about upstream intent. No upstream
contact has occurred; retain only a deduplicated subset for the single
post-corpus report if separately authorized.

## Checkpoint 17 publication finding

The complete local checkpoint package passed metadata, ZIP integrity, reader,
source/backend, PDF, and QA gates. The authorized Zenodo API preflight timed out
after 30 seconds, and one bounded anonymous public API request timed out with
zero response bytes after 20 seconds. No upload or publication mutation was
observed. Checkpoint 16 remains the public lineage head. See the sanitized
blocker `00_control/ZENODO_PUBLICATION_BLOCKED_CHECKPOINT_17.json`; do not loop
or create a duplicate record.

## QuantEcon `poisson.md` — checkpoint 18 findings

The frozen authority is
`authority/quantecon/source_snapshot/continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7/lectures/poisson.md`,
13,453 bytes at SHA-256
`d9bb4268d30179d48598dd63066f938da895110511fb6f54aaf915200353e102`.
The Indonesian target is 14,614 bytes at SHA-256
`8d0f457f3cad1b306e6fede93f390a514da5ec18a544bd22a9a4fdeccdcdea10`
and preserves every formula, stable label, directive, seven executable cells,
two exercises, and two solutions.

- In the Bernoulli-grid construction, the authority describes the first-visit
  waiting time as exponential with rate `t lambda`; its rate is `lambda`, with
  `t` the observation horizon. The downstream reader states the corrected
  rate.
- The authority writes `J_k := W_1 + \\cdots W_k` and repeats the same omission
  in the first exercise. The downstream reader inserts the missing `+` before
  the final summand.
- The proof typo `indepenence` is rendered as `independensi`.
- Several authority prose passages loosely call fixed-time Poisson laws
  rate-parameterized. The terminology gate preserves `laju` for the process or
  exponential waiting-time distribution and uses `parameter` for a fixed-time
  Poisson count distribution. Formulas and executable code are unchanged.

The frozen authority bytes remain unchanged. These bounded corrections are
recorded in the component receipt and backend; no upstream contact has
occurred. Retain only a concise deduplicated subset for the single possible
post-corpus report after separate authorization.

## Checkpoint 18 terminology and reader finding

No representative same-field Indonesian arXiv TeX source was found in the
bounded official search. The official Universitas Ahmad Dahlan module
*Pengantar Proses Stokastik* (2021) was therefore inspected only as a
nonredistributed PDF terminology witness. The resulting glossary decisions
were propagated before the final build. The 78-file HTML reader, 5,300-record
backend, and 209-page PDF pass their strict and visual QA gates. The rejected
first PDF candidate was never published; the admitted PDF has SHA-256
`0e833c56460522b981511b2a2b7293f1e4dd3184fbb6755e53064e99d2fbbad9`.

## QuantEcon `markov_prop.md` — checkpoint 20 findings

The frozen authority is
`authority/quantecon/source_snapshot/continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7/lectures/markov_prop.md`,
31,134 bytes at SHA-256
`0380ca588468e4185391e8bf5d2d207978a958a6c954029f41399473d9d6f545`.
The Indonesian target is 34,796 bytes at SHA-256
`95819eeb048f4fc792bd7d8b1a85dfbaecca962c440bd87b54424a6fa8b96a45`
and preserves the 27-heading sequence, 32 display surfaces, 12 equation
labels, five standalone labels, five executable cells, four exercises, four
solutions, and the frozen source figure.

- The inventory-process prose states that the simulation starts from
  `X_0=0`, while the function signature, docstring, and call initialize it at
  `b`. The downstream reader states `X_0=b`, matching the executable model.
- The displayed empirical distribution averages indicators of `X_t` without
  the replication index. The downstream reader writes `X_t^m`, making the
  Monte Carlo sample explicit without changing the computation.
- Exercise 4 defines states `0,...,b` but evaluates a binomial PMF with
  `n=b+1`, which assigns positive mass to the omitted state `b+1`. The
  downstream solution uses `Binomial(b,0.25)` on `0,...,b`; the admitted PMF
  sums to one up to floating-point error, whereas the source expression omits
  mass `2.3841857965667401e-07` for the supplied parameters.

The downstream renderer also required two local implementation repairs that
are not upstream content findings: an unlabeled display was initially allowed
to consume later parenthetical prose as an HTML equation ID, and the official
QuantEcon macro `dD = \\mathcal{D}` was absent from the local MathJax map.
Both are now regression-guarded. Generated and source figures now have stable
resolving DOM fragments and backend asset paths. No upstream contact has
occurred; retain only a concise deduplicated subset for the single possible
post-corpus report after separate authorization.
