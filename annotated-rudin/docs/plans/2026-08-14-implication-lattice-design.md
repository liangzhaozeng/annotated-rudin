# The Implication Lattice — companion document design (validated 2026-08-14)

## Decisions (user-approved, one question at a time)
- **Form:** standalone companion PDF, not an in-book interlude — frees it from
  Rudin's chapter order (Ch. 5–6 are unwritten in the annotated edition).
- **Universe:** two tiers. Tier 1 = one real function on an interval.
  Tier 2 = a sequence `f_n -> f`, convergence split pointwise vs uniform.
- **Coverage:** complete lattice. Every ordered pair settled — implication
  with proof, or non-implication with a named counterexample.
- **Integrability:** include the Lebesgue criterion (bounded `f` on `[a,b]`
  is Riemann integrable iff its discontinuity set has measure zero).
- **Integration:** cite into the annotated edition throughout; this is its
  synthesis chapter, not a free-standing essay.

## Architecture — three blocks
Four of the five properties are pointwise; integrability is not. A single
5x5 matrix would equivocate, so:

- **Block A (local, at p):** has-limit <- continuous <- differentiable.
- **Block B (global, on [a,b]):** those promoted to "everywhere", plus
  integrability. Continuity => integrability lives here; so does Volterra.
- **Block C (sequences):** which of A and B survive a limit. Pointwise
  preserves nothing; uniform preserves continuity and integrability, not
  differentiability.

Spine: Block C is Blocks A and B asked again with a limit in front.

## Cells
**A:** D=>C (quotient times (x-p)); C=>limit. Failures: removable spike;
|x| at 0. Plus x^2 sin(1/x) — differentiable, derivative discontinuous — and
its counterweight, Darboux (a derivative has the IVT property, so no jumps).

**B:** C on [a,b] => I, via uniform continuity making oscillation small on a
fine partition. Failures in rising sharpness: step fn; Thomae (dense
discontinuities, still integrable); Dirichlet (bounded, not integrable).
Lebesgue criterion re-derives all three in one line. Deepest cell: Volterra
— differentiable everywhere, bounded derivative, derivative not integrable;
the reason FTC carries a hypothesis and the two halves are independent.

**C:** pointwise breaks continuity (x^n on [0,1]), integrability (indicators
of finite rational sets -> Dirichlet), and lim-integral exchange (tall
spikes). Uniform rescues continuity + integrability; fails for
differentiability (sin(nx)/sqrt n -> 0 uniformly, derivatives diverge). The
repair is Rudin 7.17: hypothesise uniform convergence of the derivatives.

~16 arrows, ~12 counterexamples.

## Cast (12 dossiers)
removable spike · |x| · x^2 sin(1/x) · sin(1/x) · step · Thomae · Dirichlet ·
Weierstrass · x^n on [0,1] · sin(nx)/sqrt n · tall spikes · Volterra.

## Integration with the annotated edition
The Lebesgue criterion's machinery is **already in the book**: oscillation
`omega_f` is developed at ch2 appendix S2.4–S2.5 and ch4 appendix S4.4–S4.5,
including that `Omega_eps` is closed and disc(f) = union of `Omega_{1/n}` —
exactly the set the criterion measures. Also cite: Baire (ch2 S2.13) making
Weierstrass typical and Dirichlet not a pointwise limit of continuous
functions; Thomae (Rudin Ex 4.18, ch4 S4.5 no-mirror-image); uniform
continuity (ch4 Supplement E).

## Build
`companion/` sibling directory, own driver, reuses `annotated.sty`. Results
numbered T1–T16, examples E1–E12. Deliverable
`annotated-rudin-companion.pdf`.

## Figures (three-gate test applies to each)
1. The lattice — three blocks, solid arrows for implications, struck-through
   arrows labelled by the killing function. Centrepiece.
2. Measure zero — discontinuity set covered by intervals of total length < e.
3. Uniform vs pointwise — the e-tube, x^n escaping near 1.
4. sin(nx)/sqrt n — two panels: amplitude collapsing, slope steepening.
5. Tall spikes — area pinned at 1 while the function goes to 0.

## Verification
Standard battery (clean build; zero overfull >5pt, missing chars, lost
floats, undefined controls; no sparse pages; greyscale render of every figure
inspected). **Plus a new gate:** a script that resolves every cross-reference
into the annotated edition — each cited `S2.x`, `S4.x`, Rudin item number
must exist in `ch0*/` or `appendix/`. No fidelity checker (no verbatim Rudin).

## Revision (2026-08-14, same day)
User: "actually I would like to consider as a separate paper." Chose
**paper format, still citing the book** over full self-containment.

Rebuilt as `paper.tex` -> `implication-lattice.pdf` (10 pp): article class,
title/abstract/numbered theorems/bibliography, own `paper/preamble.tex`
(normal margins, no margin-note column, no house boxes; TikZ vocabulary
carried over so the five figures are unchanged). House-style boxes became
prose and `remark` environments; margin notes became running text. The two
oscillation lemmas are cited to the annotated edition rather than reproved.
Author line is a placeholder.

The earlier `companion/` build (13 pp, house style) is retained, not deleted.
