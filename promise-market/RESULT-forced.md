# Promise market: what decides the split above the trust cliff — result (2026-11-07, after PREREG-forced.md cccc9d2)

forced.py (trust.run + counters; `forced.py control` SAME x3), t = 0.4, q = 0.5, e = 0.1, 20 seeds, 150 generations.
Verdicts from forced_verdict.py (forced_verdict.log):

1. "6-10 of 20 take off": HELD, 8 of 20.
2. "sign(K - H) at generation 10 predicts the outcome in >= 18 of 20": WRONG, 16 of 20. 19 at generation 20, 20 only
   at generation 40. Seed 19 sits at K = 0.59, 0.56, 0.52 at generations 10, 20, 30 with renegers gone (R = 0.01)
   and still ends with the safe type (K = 0.01 by generation 60).
3. "gen-0 forced picks do not separate the outcomes; earned picks in gens 0-2 are >= 2x higher in takeoffs": WRONG
   both ways. Forced picks in generation 0 are 1.43x higher in takeoff seeds (841 vs 588), earned picks only 1.13x.
   Forced picks are just a readout of how few safe agents the seed started with (H at gen 0: 0.34 vs 0.39).
4. "stuck seeds: forced < 1% of picks by gen 10; takeoffs: earned > forced by gen 5": the first half WRONG (4 of 12),
   the second half held in 8 of 8 but is empty: earned picks exceed forced picks already in generation 0 in 20 of 20
   seeds, takeoff or not.

## What this does to my earlier claim
RESULT-trust.md said "the few forced trials must each produce a record". That is not the bottleneck. Within every
generation a handful of forced trials give some keepers an audited record within a few rounds, and from then on most
promise picks are earned ones, in every seed. The split is decided later and more slowly.

## Exploratory, not pre-registered (forced_fh.py, forced_fh.log)
In this parameter set a keeper and a safe agent earn exactly the same fee per pick (f - c = 2 - 1 = fh = 1), so
above the cliff their contest is close to neutral and the outcome drifts. Moving only the safe fee, 20 seeds each:

    fh = 0.8: 13/20 take off (mean K 0.62)
    fh = 0.9: 11/20 (0.52)
    fh = 1.0:  8/20 (0.38)
    fh = 1.1:  3/20 (0.15)

So above the cliff the seeds are a biased coin, and the bias is set by what the safe option pays its provider
compared with keeping a promise, not by how audits are distributed. Even when keepers earn 25% more per pick
(fh = 0.8), 7 of 20 seeds still end with the safe type. A keeper only gets picked once it has a record, and the
record restarts every generation. Model only: uniform prior 0.5, ledgers reset each generation, no data about
real agents.
