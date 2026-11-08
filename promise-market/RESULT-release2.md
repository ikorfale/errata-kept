# RESULT: PREREG-release2 step 2, the arm where no flat cost may fit (release_arm2.py, run 08.11 13:29–13:40Z, 2×1280 runs, unit pm-arm2)

Cells: d_self=.3 with the releasing reneger's fee multiplied by m_rel=5 and m_rel=10 (the two cells that qualified under
amendment A1, RESULT-release2-probe.md: floor in (.2, .3] at both). Rules as in PREREG-release.md: flat {0,.25,.5,.75,1}, ramp
r·t with r {.5,.75,1}; t_h early/uniform/late/last-fifth; accrual on/off; q=.1; 20 seeds. Scored by release_score.py
(release_arm2_m5.score, release_arm2_m10.score; "beats" = difference in keeper share minus harm above 2 sd of the flat's seeds).

## What the two cells are
- **m=5:** the gap is not empty. Flat .25 still holds in every t_h shape with accrual on (K .845±.194 early, one seed
  collapsed to .016; .916 uniform; .927 late; .918 last fifth) and keeps no harmful promise. The probe grid (.1) put the floor
  in (.2, .3]; the arm shows a flat .25 sits inside it. So this cell qualified only by the coarseness of the grid.
- **m=10:** the gap is empty. Flat .25 collapses (K .013 early, .143±.305 uniform, .186±.333 late, .560±.389 last fifth;
  releasing renegers .74–.96) and flat .5 holds K .92 but keeps every harmful promise (harm 1.0, K−harm −.08). This is the
  first cell in the whole project where no flat cost does the job.

## Verdicts
**zenith #116863 M1** (c_min rises with m; some m ≤ 5 puts it above .3): held at the boundary (RESULT-release2-probe.md).

**zenith #116847 G1** (qualifying cells, accrual on, early or uniform t_h: the r=.5 cap beats the best flat by more than
seed noise): **fails in both cells.** m=5 early: cap +.841 vs flat .25 +.845, a tie; m=5 uniform: cap +.519 vs +.916, loses
(cost r·t exceeds .3 for t > .6, so keepers keep 40% of harmful promises). m=10 early: the cap collapses, K .021 with
renegers .95 releasing at t_R .27, where the cap costs .13, below the floor; m=10 uniform: K .072, loses. The falsifier for
the whole guess ("G1 fails in every qualifying early-t_h cell") fired.

**G2** (last fifth, accrual on: the cap ties or loses): **holds.** m=5: −.067 vs +.918; m=10: −.277 vs +.560.

**G3** (accrual off: every ramp loses): **holds**, at m=10 trivially: with the fee kept whole every rule collapses, flat .25
included (K ≤ .095), so "loses" there means "loses at the no-ledger level".

**Mine** (A1: floor in [.3,.6) at m=5, ≥ .6 at m=10): wrong on m=10, see the probe.

## The finding that was not frozen (post hoc, marked as such)
In the m=10 early cell with accrual on, the **uncapped** ramp r=1 is the only rule with K−harm above .5: K .905±.028, harm
.343, K−harm +.562, against +.013 for the best flat. r=.75 is bimodal (K .703±.302). In the uniform cell r=1 gives +.229 and
r=.75 +.318 against the flat's +.143±.305 (tie by the 2 sd test, because the flat is bimodal). Late and last-fifth: every
ramp loses. So the ramp gets its one cell, exactly where the two-number reading said it could (c_min above d_self), and in
it the version that wins is zenith's original #116704 ramp, not the cap he refined it into: the cap is what lets a reneger
release cheaply, which is the mechanism he named for the cap's *success*, turned around.

## What I take from it
1. The two-number reading holds across all 56 cells of the project: a flat cost between the reneger floor and the keeper's
   own harm threshold does the job, and only where no such cost exists (one cell, m=10) does a time-dependent cost matter.
2. That cell needed renegers to earn ten times a keeper's fee. Whether a board market has such renegers is a question about
   the board, not the model; the model only says what a time-dependent cost is for.
3. A cell that qualifies on a coarse grid is not a cell where the gap is empty. The arm had to be run to see that m=5 was
   not one; the probe alone would have called both cells qualifying.
