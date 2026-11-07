# Promise market: a price on trust — result (2026-11-07, run 13:39 UTC, after PREREG-trust.md a8e78b1)

trust.py, e = 0.1, 5 seeds per cell, mean of the last 20 of 150 generations. Control: t = 0 equals sim.py (SAME x3).
Keeper share K (H = the safe no-promise type):

    t \ q    0   .01   .02   .03   .05   .1    .2    .3    .5    1.0
    0      .01   .04   .42   .83   .91   .93   .94   .96   .96   .94
    0.2    .01   .04   .43   .86   .93   .94   .94   .94   .95   .95
    0.3    .01   .06   .49   .81   .91   .91   .94   .94   .95   .95
    0.35   .01   .01   .01   .01   .01   .01   .01   .01   .38   .95    (H = .98 for q <= .3)
    0.4    .01   .01   .01   .01   .01   .01   .01   .01   .38   .95
    0.6    .01   .01   .01   .01   .01   .01   .01   .01   .58   .95

At q = 0.5 above the cliff the seeds split (sd 0.45): some runs go to keepers, the rest stay safe. Rows t = .1, .25, .5
in trust.json; same pattern.

## Verdicts
1. "t <= 0.2: within 0.10 of t = 0": HELD (and t = 0.25, 0.3 too: largest gap 0.08).
2. "t >= 0.4: keepers pass 0.5 only at q >= 0.3; below, H > 0.8": the H half HELD (0.97-0.98). The threshold was
   WRONG in size: q = 0.3 gives 0.01, q = 0.5 is a coin flip between seeds, only q = 1 is reliable. The threshold
   moves from q ~ 0.03 to q ~ 0.5-1, about twenty times higher.
3. "a cliff at t = 0.3, not a slope": HELD. Between t = 0.30 and 0.35 the whole grid flips from renegers-or-keepers to
   safe. At t = 0.3 an untried stranger ties with the safe option (1.5 - 0.3 = 1.2) and ties break at random, which is
   enough trials for the ledger to start.
4. "top 5% take > 25% of promise picks while keepers rise (transition cell q*G = 1)": WRONG. They take 0.18-0.23 in
   every generation of 5 seeds, flat from generation 0, with no spike during the rise. That is 3x the no-audit
   baseline (0.07 at q = 0, where picks are a lottery), so picks do pile onto agents with a good audited record,
   but the pile is the same size whether or not the ledger is taking off. At q = 1 it is highest at the start (0.26)
   and falls as keepers become common (0.15 by generation 10).

## What it means (in the model)
The low threshold in RESULT.md was bought by free default trust. Once trying a stranger costs more than the gap
between a stranger's prior value and the safe option, nobody tries strangers, nobody gets audited, and the ledger
never starts unless audits are nearly certain: the few forced trials (samples with no safe agent in them) must each
produce a record. What a ledger needs is not only coverage but someone willing to make the first unrecorded bet.
Below the cliff the cost changes nothing. This is a model with a uniform prior of 0.5, perfect ledger readers and
no forgiveness; not data about real agents.
