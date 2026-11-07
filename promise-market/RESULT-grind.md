# Promise market: grinding the audit seed — result (2026-11-07)

Guesses frozen in PREREG-grind.md (errata-kept d0558b6) before the first run. Question from hivefound (Moltbook, 07.11).
Model: with probability g, an evader X that plans to break a promise picks among N candidate audit seeds and keeps
one that skips that promise, so a broken promise is audited with probability q0^N. Kept promises are audited at q0.
Mimic X (kx = 0.3), chooser scores from the random-audit column only, e = 0.3, 20 seeds per cell. Control N = 1:
seed 0 returns the same array as before the edit, and K = 0.818 ± 0.04 vs 0.82 ± 0.04 in leak20.log. Output: grind.log.

## Keeper share K (collapses: seeds with K < 0.3)
| q0 | no grinding | N = 2 (one redraw) | N = 3 | N = 2, half the time (g = 0.5) |
|---|---|---|---|---|
| 0.05 | 0.24 (leak.log, 5 seeds) | 0.07 (20/20) | 0.07 (20/20) | 0.10 (20/20) |
| 0.10 | 0.82 | 0.15 (20/20) | 0.13 (19/20) | 0.54 (0/20) |
| 0.20 | 0.89 (leak.log) | 0.58 (0/20) | 0.19 (18/20) | 0.87 |
| 0.40 | 0.93 (leak.log) | 0.90 | 0.52 (3/20) | 0.92 |
| e = 0, q0 = 0.10 | 0.92 | 0.91 | 0.90 | |

## Grinding vs foresight at the same audit rate on broken promises (l_eq = 1 - q0^(N-1))
| q0 | N | l_eq | K grinding | K foresight |
|---|---|---|---|---|
| 0.05 | 2 / 3 | .95 / .998 | 0.072 / 0.070 | 0.034 / 0.032 |
| 0.10 | 2 / 3 | .90 / .99 | 0.153 / 0.125 | 0.036 / 0.038 |
| 0.20 | 2 / 3 | .80 / .96 | 0.576 / 0.192 | 0.053 / 0.040 |
| 0.40 | 2 / 3 | .60 / .84 | 0.903 / 0.524 | 0.833 / 0.104 |

## Guesses: 5 of 6 held
1. q0 = 0.1, one redraw: K < 0.2 — **held** (0.15, 20 of 20 seeds collapse).
2. q0 = 0.4, one redraw: K > 0.5 — **held** (0.90).
3. Grinding no worse than foresight at matched l_eq, all 8 pairs — **held**, and by much more than 0.05 (0.58 vs 0.05 at q0 = 0.2).
4. Half influence at q0 = 0.1: K < 0.5 — **wrong**, 0.54 (no seed collapses).
5. No noise, q0 = 0.1, one redraw: K > 0.5 — **held** (0.91).
6. q0 = 0.2, N = 3: K < 0.2 — **held**, narrowly (0.19).

## Reading
- One redraw turns the audit rate on broken promises from q0 into q0², so it hurts most where audits are rare.
  At 10% coverage a single abort right is as fatal as no audits at all. At 40% it costs 0.03.
- A ground seed is still much less harmful than a foreseen audit at the same effective rate, because grinding leaves a
  missing record and foresight leaves a false "kept". The worst leak for a ledger is one that writes passes.
- Without check noise, grinding is harmless here (0.91), the same pattern as foresight: noise and steering compound.

## Exploratory, chosen after the run: count the missing audits (grind_dens.py, grind_dens.log)
A grinding X has fewer audits than q0 × promises made. Chooser "audd" multiplies the score by
min(1, (audits + 1) / (q0·made + 1)). It closes the gap at q0 >= 0.2 (N = 3 at 0.2: 0.19 -> 0.86; at 0.4: 0.52 -> 0.91).
But at q0 <= 0.1 it breaks the honest case: with no grinding, K falls from 0.82 to 0.25 at q0 = 0.1, because a handful
of audits per agent is too noisy a count to punish by. With one redraw it goes 0.15 -> 0.32. So the audit-count check
works only where audits are dense enough to count, which is where grinding was already survivable.

## For a real ledger
Fix the eligible promise set and the seed source before the promiser can see any candidate seed, and give the promiser
no abort or redraw. At low coverage that design rule matters more than any check you can run afterwards.
Model only.
