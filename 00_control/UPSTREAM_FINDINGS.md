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
