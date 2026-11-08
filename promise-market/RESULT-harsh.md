# Promise market: harsher imitation, do raids breed? Result (2026-11-08, PREREG-harsh.md)

Cell t = 0, q = 0.03, e = 0.1; arms inherit and market0; beta 10, 30, 100; 20 seeds; raids traced from generation
50 (harsh.py, control SAME on 3 of 3 against strong.run). Output: harsh.log, harsh.json.

| beta | arm | K mean (min) | copies per fresh R | buyers/gen | raids | mean length | longest | >= 5 gens | >= 20 gens |
|---|---|---|---|---|---|---|---|---|---|
| 10 | inherit | 0.974 (0.938) | 0.43 | 0 | 2626 | 1.44 | 7 | 30 | 0 |
| 10 | market0 | 0.927 (0.851) | 0.60 | 5.7 | 5642 | 1.71 | 16 | 239 | 0 |
| 30 | inherit | 0.976 (0.910) | 0.45 | 0 | 2985 | 1.46 | 13 | 24 | 0 |
| 30 | market0 | 0.897 (0.797) | 0.63 | 8.6 | 7734 | 1.73 | 13 | 344 | 0 |
| 100 | inherit | 0.974 (0.933) | 0.46 | 0 | 2950 | 1.48 | 8 | 35 | 0 |
| 100 | market0 | 0.868 (0.780) | 0.65 | 10.9 | 9321 | 1.76 | 16 | 472 | 0 |

Market cost (K inherit - K market0): 0.047 at beta 10, 0.079 at 30, 0.106 at 100.

## Guesses
1. Copies per fresh R at beta 100 below 1: **held**, 0.65 (0.60, 0.63, 0.65 at 10, 30, 100: saturating).
2. At least one raid of 5+ generations at beta 100: **held**, 472 of 9321 (5.1%); longest 16.
3. No raid of 20+ generations anywhere: **held**, 0 in all six cells.
4. K market0 at beta 100 >= 0.85 and 20/20 take off: **held**, 0.868 and 20/20; the worst seed is 0.780.
5. Market cost larger at beta 100 than at 10: **held**, 0.106 vs 0.047.
6. Inherit K at beta 100 >= beta 10: **held by 0.0002** (0.9738 vs 0.9736), which is no difference.

## Reading
Raids never become self-sustaining: the reproduction number flattens at about 0.65 and the longest chain in 120
runs is 16 generations. What grows with beta is the number of raids, not their length: buyers per generation go
5.7 -> 8.6 -> 10.9, raids 5642 -> 9321, and that is where the market's cost comes from (0.047 -> 0.106 of K).
Why the ceiling (exploratory, from the model's structure, not a separate run): each agent compares itself with one
random other per generation, so a fresh buyer is met by Poisson(1) agents, and at beta 100 the copy chance is
already clipped at 1 whenever the buyer is fitter. The reproduction number is then about P(a random agent earns
less than the buyer), and 0.65 is that share. A broadcast imitation rule (copy the best of m sampled agents) would
lift the ceiling; not run.
Limit: "alive at the last generation" is censoring, not survival (mean length 1.8 generations), so it is not reported
as a result.
