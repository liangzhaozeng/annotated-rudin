# Geometrizing Algebra — design (validated 2026-08-11)

## Decisions (user-approved)
- **Scope:** retrofit Chapters 1–4 and apply forward from Chapter 5.
- **Bar:** faithful + load-bearing only. Three gates, all must pass:
  1. *Faithful* — the picture IS the statement under an explicit dictionary
     (numbers=lengths, products=areas, ℂ=plane, …); every hypothesis visible.
  2. *Load-bearing* — the picture shows why it's true or where a hypothesis
     is spent; spatially restating symbols fails.
  3. *Honest about generality* — special-case pictures (n=2, positive reals)
     say so in the caption and say what changes in general.
  Fail any gate → no figure. Tempting-but-misleading picture → `pitfall` box.
- **Home:** new sub-skill `rudin-geometrizing-algebra` (test + catalogue);
  `rudin-drawing-figures` keeps TikZ craft; orchestrator Stage 5 references both.

## Catalogue of standard dictionaries
products=areas (distributive, (a+b)²); telescoping=stacked segments
(bⁿ−aⁿ, geometric series); order=position on the line; ℂ=plane
(multiplication rotate-and-scale, conjugation reflection, triangle
inequality as triangle); inner product=projection (Schwarz, parallelogram);
dissection (Tennenbaum); summation-by-parts=staircase regrouping (3.41).

## Retrofit candidates
- **Ch1:** bⁿ−aⁿ identity at 1.21; distributive law at 1.12; complex
  multiplication/conjugation/triangle-inequality at 1.25–1.33.
  (Already done: Tennenbaum, sup pictures, Schwarz projection.)
- **Ch2:** expect zero — sweep confirms.
- **Ch3:** geometric series 3.26; summation by parts 3.41; Cauchy product
  grid 3.48 if it passes the gates.
- **Ch4:** expect zero to one.

## Placement
Statement pictures: figure + `\figcap` naming the dictionary.
Alternative geometric proofs: `deeper` box. Figures are additive — Rudin's
text untouched; normal battery applies (build, greyscale render, fidelity).

## Process
Sub-skill written under writing-skills TDD (baseline → skill → verify);
then retrofit lands chapter by chapter.
