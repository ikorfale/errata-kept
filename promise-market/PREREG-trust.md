# Promise market: a price on trust (pre-registered 2026-11-07, before the sweep)

Open question from RESULT.md: trying a stranger is free in sim.py, so default trust (b x 0.5 = 1.5 > h = 1.2)
is a free bet. Here a chooser who picks a promiser pays t, kept or not; choosers price it in (value b*rep - t).
Code: trust.py (t = 0 reproduces sim.py exactly on 3 cells: `trust.py control`, SAME x3).
Sweep: e = 0.1, t in {0, .1, .2, .25, .3, .35, .4, .5, .6}, q in {0, .01, .02, .03, .05, .1, .2, .3, .5, 1}, 5 seeds.
Pick concentration: `trust.py conc 0.0333 0.2 0 S` (transition cell q*G = 1), share of promise picks taken by
the top 5% most-picked agents per generation (uniform = 0.05).

Guesses, frozen now:
1. t <= 0.2 (a stranger still beats the safe option, 1.5 - t > 1.2): keeper share within 0.10 of t = 0 at every q.
2. t >= 0.4: keepers pass 0.5 only at q >= 0.3; below that the safe type H dominates (> 0.8), not renegers.
3. The change between is a cliff at t = 0.3 (where an untried stranger is worth exactly h), not a slope:
   t = 0.25 looks like t = 0, t = 0.35 looks like t = 0.4.
4. Concentration: in the transition cell, while keepers are rising, the top 5% of agents take > 25% of promise picks
   (the reviewer's "one lucky audited keeper chosen by many" mechanism).
Whatever comes out is posted in thread 58577162 with these guesses next to it.
