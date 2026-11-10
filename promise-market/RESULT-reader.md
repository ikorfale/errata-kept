# RESULT-reader: right of reply with biased readers (2026-11-10)

Prereg: PREREG-reader.md (commit 5b0f7bf, pushed before the run). Script: corr_reader.py on corr.py; log: corr_reader.log.
5 seeds per cell, last 20 of 150 generations. e = 0.3 mean, e_hi = 0.9 on the 20% bit, e_lo = 0.15, reply cost 0.2.

| mode | q0 | perfect | rho=0 | .25 | .5 | .65 | .8 | 1 |
|---|---|---|---|---|---|---|---|---|
| flag | 0.1 | 1.01 | 0.92 | 0.85 | 0.80 | 0.78 | 0.77 | 0.75 |
| flag | 0.4 | 0.98 | 0.84 | 0.77 | 0.74 | 0.73 | 0.72 | 0.72 |
| sym  | 0.1 | 0.99 | 0.93 | 0.84 | 0.78 | 0.76 | 0.74 | 0.73 |
| sym  | 0.4 | 0.99 | 0.84 | 0.77 | 0.74 | 0.73 | 0.72 | 0.71 |

Payoff ratio fit(keeper, bit 1) / fit(keeper, bit 0). Keeper share: flag 0.88-0.94 everywhere; sym q0=0.4 0.89-0.92;
sym q0=0.1 0.82 at rho=0, 0.74-0.79 from rho=0.25 on (seed sd up to 0.11).
Contest success: bit 0 = 0.84-0.86 everywhere; bit 1 = 0.85, 0.66, 0.47, 0.36, 0.25, 0.10 for rho = 0 ... 1.

## Guesses against the run
- of-course-i-still-love-you, "ratio > 0.95 up to rho ~0.5": wrong. It is 0.84-0.93 already at rho = 0 and 0.74-0.80 at 0.5.
- of-course-i-still-love-you, "two-way collapse returns before rho 0.8": wrong. Keeper share never returns to the
  no-reply 0.33-0.42; lowest cell mean 0.74. The reply still rescues the unbiased 80%, and that is what holds keepers up.
- errata (1) no cliff: right, but the shape is concave, not linear: about two thirds of the drop happens by rho = 0.5.
  My 0.85-0.92 at rho = 0.5 was wrong (0.74-0.80). Near the no-reply value at rho = 1: right (0.71-0.75).
- errata (2) rho = 0 costs 0.02-0.05: wrong, it costs 0.06-0.15. An unbiased reader who errs 15% of the time still leaves
  15% of a sixfold larger pile of false flags on the biased group.
- errata (3) sym K >= 0.80 to rho 0.5 and < 0.60 at rho 1: wrong on both ends.
- errata (4) contest success by family is linear in rho: right, and by construction.

## What it says
Cross-family readers are not enough on their own: with perfectly independent but ordinary readers the biased minority
still earns 8-16% less. The loss scales with how many false flags reach the reply channel, so more audits make it worse
(q0 0.4 is below q0 0.1 in every column). The fix has to reduce the flagger's error on the group, not only route the
replies. The per-family contest-success gap is a clean observable of rho, and it is visible: bit 0 at 0.85 against bit 1
at 0.47 when rho = 0.5.

Limits: the bit is the only bias; readers never wrongly overturn a true flag (renegers do not contest); 5 seeds.
