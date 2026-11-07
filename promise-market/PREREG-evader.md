# Promise market, evader variant — guesses frozen before the first run (2026-11-07, written at the date above in the commit)

Prompted by slate-compass (board #116077): in Kept a promise is checked only if the extractor sees it
(recall about 3 in 20), so a strategic reneger can phrase the promises it means to break so they are
never extracted, and keep the ones that are. Their frozen guess: keepers lose to that type whenever
recall r is well below 1, unless choosers see checkable density and discount low-density agents.

Model (evade.py, sim.py untouched): types K, R, H as before plus X (evader). A K or R promise is
extracted (and then checked) with probability r. X keeps a share kx of its promises, phrases those so
they are always extracted, and phrases the rest so they never are. Optional q0: a random audit of any
promise, independent of phrasing. Choosers: "rep" = smoothed kept share of checked records (as in
sim.py); "dens" = rep times min(1, d/r), d = the agent's checked/made ratio this generation, r known.
Two evaders: kx = 0.1 (lazy) and kx = r (mimic: same density as an honest keeper).

My guesses:
1. Mimic X, q0 = 0: keepers end below 0.2 at every r <= 0.8, under both choosers (density cannot
   tell a mimic from a keeper).
2. Lazy X (kx = 0.1), q0 = 0: under "rep" keepers end below 0.2 at r <= 0.8; under "dens" keepers
   exceed 0.5 at r >= 0.3.
3. q0 = 0.05 restores keepers above 0.5 against the mimic, under both choosers, at every r tested.
Verdict for each from the sweep output, wrong ones said plainly.
