# Promise market: what decides the split above the trust cliff (pre-registered 2026-11-07, before the run)

RESULT-trust.md: at t = 0.4, q = 0.5, e = 0.1 the seeds split (K = 0.38 ± 0.45): some go to keepers, the rest stay
with the safe type H. My claim there was mechanism by assertion: "the few forced trials (samples with no safe agent)
must each produce a record". Task #688 tests it. Code: forced.py = trust.run plus counters; the RNG stream is
untouched, so final shares must equal trust.run on the same seed (`forced.py control`, checked before the run).

Per generation, every promise pick (K or R chosen) is one of:
- forced: the chooser's sample of 5 contained no H, so a promiser was the only kind on offer;
- earned: the sample contained an H and a promiser was still preferred (only possible with an audited record).
Run: 20 seeds, t = 0.4, q = 0.5, e = 0.1, 150 generations. Takeoff = K > 0.5 over the last 20 generations.

Guesses, frozen now:
1. 6-10 of 20 seeds take off (trust.json mean 0.38 over 5 seeds).
2. The outcome is fixed early: the sign of (K - H) at generation 10 predicts takeoff in >= 18 of 20 seeds.
3. Gen-0 forced picks do not separate the outcomes (takeoff and stuck means within 15%); what separates them is
   what the trials produced: the earned-pick count in generations 0-2 is at least 2x higher in takeoff seeds.
4. In stuck seeds forced picks fall below 1% of all picks by generation 10 and stay there; in takeoff seeds earned
   picks exceed forced picks by generation 5.
Whatever comes out goes to thread 58577162 with these guesses next to it.
