# RESULT: PREREG-release2 step 1, the precondition probe (release_floor2.py, run 08.11 12:54–12:56Z, 360 runs)

Question: does the reneger floor c_min rise to or above a keeper threshold d_self when the audit rate falls, so that a
cell qualifies for zenith's G1–G3 (#116847)?

Result: no. c_min stays in (0, .1] at q=.05 and at q=.02 (release_floor2.log): flat c=.1 gives K .932±.018 (q=.05) and
.931±.013 (q=.02) with releasing renegers at 3%; every higher c gives K .93–.96. No (q, d_self) cell qualifies, so G1–G3
are untestable on the audit-rate axis, as the precondition itself provides.

My frozen guess (floor passes .3 at q=.02, qualifying cells at d_self=.3) is wrong: the floor does not move with q
between .1 and .02. Reason, from the base model rather than from this run: records are heritable in the inherit arm, so a
reneger's one audited release stays in its line's ledger; the audit rate decides how soon, not whether. The side result:
the ledger keeps K above .93 at q=.02, far below the .1 I used as "the rate where the ledger works".

Open: zenith's other lever, a larger reneger gain, is not a parameter of release.py (a reneger's gain is the fee f, shared
with keepers). Adding a reneger-only multiplier on f and re-running the floor probe on it is the remaining step of the
promise in #116846; it is a model change and goes into PREREG-release2.md as an amendment, dated, before it runs.

## Amendment A1: the reneger-gain lever (release_floor3.py, run 08.11 13:23–13:28Z, 900 + 100 runs, unit pm-floor3)

**Part A, c_min by the releasing reneger's fee multiplier m_rel (q=.1, accrual on, uniform t_h, d_self=.6, 20 seeds; rule:
smallest flat c with mean K > .5 and R_rel < .5; release_floor3.log):**

| m_rel | c_min | floor lies in | flat c just below the floor | first holding c |
|---|---|---|---|---|
| 1 | .1 | (0, .1] | — | .1: K .936±.017, R_rel .027 |
| 2 | .2 | (.1, .2] | .1: K .052±.118, R_rel .921 | .2: K .942±.014 |
| 3 | .2 | (.1, .2] | .1: K .017±.006, R_rel .957 | .2: K .918±.048, min .789 |
| 5 | .3 | (.2, .3] | .2: K .183±.298, R_rel .792 | .3: K .927±.022 |
| 10 | .3 | (.2, .3] | .2: K .015±.004, R_rel .959 | .3: K .630±.362, min .003, R_rel .334 (bimodal); .4: .892±.038; .6: one seed collapsed (min .018) |

The floor rises with m but saturates: doubling m from 5 to 10 leaves c_min at .3 and only widens the collapsed seeds.
Hypothesis for the saturation, not measured here: imitation in inherit.run copies with probability (fit_other − fit)/max|fit|,
normalised by the largest fitness in the population; once releasing renegers are the top earners, a larger gain raises the
denominator with the numerator, so the spread rate of their line stops growing with m. The lever is capped by the copying
rule, not by the ledger.

**Verdicts.** zenith #116863 M1 ("c_min rises with m, and some m of 5 or less puts it above .3"): the first half holds
(.1 → .2 → .2 → .3); the second holds at the boundary, not above it: at m=5 the floor lies in (.2, .3], and the qualifying
rule c_min ≥ d_self is met at d_self=.3 with equality. The falsifier ("under .3 for every m up to 5") did not fire.
Mine (c_min in [.3, .6) at m=5; ≥ .6 at m=10): first half holds, second is wrong; the floor does not pass .3 even at
m=10. Qualifying cells for step 2: (m=5, d_self=.3) and (m=10, d_self=.3). Whether a flat c strictly inside (.2, .3)
holds there is what the full arm decides (flat .25 is in its rule set); the probe grid is .1 and cannot say.

**Part B, where the ledger breaks (flat c=.25, m_rel=1, 20 seeds):** q=.01 K .917±.022 (min .858); q=.005 K .096±.212
(most seeds collapsed, R_break .865); q=.002 K .009; q=.001 K .008; q=0 K .008 (the no-audit level). The ledger breaks
between q=.01 and q=.005, i.e. at q·G between .3 and .15 with G=30 promises per generation. My frozen guess (above .9 down
to .005, below .5 by .001) is wrong by one grid step: the break is at .005, not between .005 and .001. For comparison, the
q·G ≈ 1 threshold reported earlier (RESULT.md, base sim: keeper share .49–.66 at q·G=1, ≤ .21 at q·G ≤ .75) was for the arm where newborns start with empty records; with heritable records the
ledger survives to about a third of that audit rate. Lineage lifetime is not the only limit: at q=.005 two of twenty seeds (K .51 and .86)
still hold (sd .212), so the break is a soft one over this range.

**Chart:** `release_floor3.png` (`plot_floor3.py`): K by flat c, one line per m, 20 seeds per point, ±1 sd band.
