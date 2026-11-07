# Evader variant: result (2026-11-07, 5 seeds per cell, evade.log; smoothing.log)

Keeper share at the end (mean of last 20 generations), recall r across:

| evader | q0 | chooser | r=0.15 | 0.3 | 0.5 | 0.8 | 1.0 |
|---|---|---|---|---|---|---|---|
| mimic (kx=r) | 0 | rep  | 0.03 | 0.03 | 0.06 | 0.13 | 0.58* |
| mimic | 0 | dens | 0.03 | 0.03 | 0.06 | 0.10 | 0.58* |
| mimic | 0.05 | rep  | 0.88 | 0.87 | 0.81 | 0.74 | 0.58* |
| mimic | 0.05 | dens | 0.33 | 0.46 | 0.58 | 0.48 | 0.58* |
| lazy (kx=0.1) | 0 | rep | 0.13 | 0.92 | 0.93 | 0.94 | 0.94 |
| lazy | 0 | dens | 0.24 | 0.92 | 0.95 | 0.95 | 0.95 |
| lazy | 0.05 | rep | 0.91 | 0.93 | 0.94 | 0.95 | 0.95 |
| lazy | 0.05 | dens | 0.87 | 0.92 | 0.93 | 0.95 | 0.95 |

*at r=1 the mimic keeps every promise, so it is a keeper under another name (K+X ≈ 0.97).

Guesses (PREREG-evader.md):
1. Mimic, q0=0, keepers < 0.2 at r<=0.8 under both choosers: RIGHT (0.03-0.13).
2. Lazy: under rep keepers < 0.2 at r<=0.8: WRONG, only at r=0.15 (0.13); from r=0.3 keepers 0.92+.
   Under dens keepers > 0.5 at r>=0.3: right, but dens adds nothing over rep there.
3. q0=0.05 restores keepers > 0.5 vs the mimic under both choosers: right for rep (0.74-0.88),
   WRONG for dens (0.33-0.58; under half at r=0.15, 0.3, 0.8).

Why the lazy evader loses under plain rep: with any positive prior a longer clean record outranks a
shorter clean one, so a keeper with r*n checked records beats an evader with 0.1*n. Prior strength
a0 = 0.1 and 1 give identical runs (same ranking); a0=3 makes r=0.15 worse for keepers (0.06).
The density factor is noisy on small counts and multiplies away the small rep gap that random audits
create against the mimic; that is my reading, not separately tested.

## After the second-model review (review_evader_fable.txt; followup.py, followup.log)
Fable found no result-changing bug; flagged that records reset every generation, that raw d is 0 after
one unchecked promise (value 0, below H and below a failed reneger), and that r=1 is neutral drift.
- Its test of reading (a): prior a0=1e-9 (length no longer ranks). Its prediction "lazy X wins at all r"
  was half right: X wins at r=0.15 (K 0.02), splits at 0.3 (K 0.42±0.13), but K still 0.93-0.94 at
  r>=0.5. Remaining channel: an agent with no checked record this generation scores 0.5; a lazy evader
  often has none. So what protects keepers is "has a clean record at all", then its length.
- Smoothed density (5 pseudo-counts at r) vs mimic, q0=0.05: K 0.65/0.61/0.66/0.47 at r=0.15/0.3/0.5/0.8,
  better than raw dens (0.33-0.58), still below plain rep (0.74-0.88). Density still costs keepers here.
- Untested: false flags e>0 with q0 (would dilute the 5% audit signal), choosers using their own payoff.
