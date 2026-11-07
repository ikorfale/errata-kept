# Result: stronger selection (PREREG-strong.md, run 2026-11-07)

Pre-registration: b2deb7a (guesses frozen before the run). Code: strong.py; control: beta = 1 equals market.run bit
for bit on 3 of 3 cells. e = 0.1, 20 seeds per cell, 150 generations. Log: strong.log, data strong.json.
Copy chance = clip(beta x fitness gap / top |fitness|, 0, 1). "Copies per fresh R" = agents that copy a reneger in
its first generation as one, generations 50-149: the raid's reproduction number (a raid breeds at >= 1).

t = 0, q = 0.03 (sparse audits), K / R / milked share / buyers per gen / copies per fresh R:

| beta | inherit | market0 | market's cost in K |
|---|---|---|---|
| 1 | 0.948 / 0.029 / 0.004 / - / 0.08 | 0.934 / 0.047 / 0.014 / 1.0 / 0.32 | 0.014 |
| 3 | 0.978 / 0.017 / 0.006 / - / 0.32 | 0.971 / 0.023 / 0.010 / 1.5 / 0.40 | 0.007 |
| 10 | 0.974 / 0.023 / 0.011 / - / 0.43 | 0.927 / 0.070 / 0.037 / 5.7 / 0.60 | 0.047 |

t = 0.4 looks the same (beta 10: inherit 0.977, market0 0.928, copies per fresh R 0.59). All 720 runs took off.

## Verdicts on the frozen guesses
1. Copies per fresh R at beta 10 >= 0.9. **Wrong**: 0.60. Raids chain (a copier of a buyer buys too) but each chain
   dies out; mean chain length about 1 / (1 - 0.6) = 2.5 raiders.
2. R share at beta 10 >= 2x beta 1. **Wrong**: 0.070 vs 0.047 (1.5x).
3. K at beta 10 at least 0.05 below beta 1. **Wrong**: 0.927 vs 0.934 (0.007). The median seed did not move
   (0.936 to 0.932); the lower tail did: worst seeds 0.889 at beta 1, 0.851 and 0.861 at beta 10 (t = 0.4: 0.871 vs
   0.824 and 0.825).
4. The market's cost is larger at beta 10 than at beta 1. **Held**: 0.047 vs 0.014.
5. At q = 0.5, |K market0 - K inherit| < 0.03 at every beta and both t. **Held** (largest 0.006).
6. Every cell keeps at least 15 of 20 takeoffs. **Held** (20/20 everywhere).

## What it says
Stronger imitation is good for honesty when records only travel by copying: keepers climb from 0.95 to 0.97-0.99
in every cell. The record market takes that gain away exactly where audits are sparse (q = 0.03): at beta 10 the
market costs 0.047 of K instead of 0.014, milked picks are 3.7% instead of 1.4%, and 5.7 agents a generation buy a
record instead of 1. The guess that raids would become self-sustaining was wrong; the number that matters stayed
below 1 (0.60), so the damage is a larger trickle and a fatter bad tail, not a takeover. With audits at q = 0.1 or
more the market's cost stays under 0.01 at any beta: frequent audits, not slow imitation, are what keep a record
market harmless.

## Limits
- beta only up to 10; 0.60 rose with beta (0.32, 0.40, 0.60), so a still stronger rule could cross 1. Not run.
- Chain length 2.5 is computed from the mean, not traced chain by chain.
- One buyer per new reneger, records cloned not transferred, price 0 only; e = 0.1, N = 200, pick best of 5.
