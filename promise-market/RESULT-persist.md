# Result: a ledger that persists between generations (PREREG-persist.md, run 2026-11-07)

Pre-registration: 6e98722 (guesses frozen before the run). Code: persist.py; control: persist=False equals trust.run
bit for bit on 3 of 3 cells. e = 0.1, 20 seeds per cell, 150 generations, takeoff = K > 0.5 over the last 20.
Log: persist.log.

| t | q | reset: takeoffs / K | persist: takeoffs / K |
|---|---|---|---|
| 0 | 0.03 | 20/20, 0.83 ± 0.04 | 20/20, 0.92 ± 0.02 |
| 0 | 0.1 | 20/20, 0.93 | 20/20, 0.95 |
| 0 | 0.5 | 20/20, 0.95 | 20/20, 0.95 |
| 0.4 | 0.03 | 0/20, 0.01 | 11/20, 0.61 ± 0.37 |
| 0.4 | 0.1 | 0/20, 0.01 | 20/20, 0.94 |
| 0.4 | 0.5 | 8/20, 0.38 ± 0.45 | 20/20, 0.95 |

## Verdicts on the frozen guesses
1. t = 0.4, q = 0.5: at least 16/20 with persistence. **Held** (20/20).
2. t = 0.4, q = 0.1: at least 5/20. **Held**, but I underestimated the size (20/20).
3. t = 0.4, q = 0.03: nothing starts either way. **Wrong**: 11/20 take off with persistence.
4. Milking at t = 0, q = 0.03: K lower by at least 0.05, and milked share at least 2x. **First half wrong**: K is
   higher by 0.09 (0.83 to 0.92). Second half held but small: 0.013 vs 0.005 of promise picks (2.6x).
5. t = 0, q = 0.5: K changes by less than 0.03. **Held** (0.00).

## What it means (within the model)
The trust cliff in RESULT-trust.md was mostly a product of the ledger being wiped each generation. Once records
outlive the generation, the rare forced trials (choosers whose sample had no safe agent) add up across generations
and the ledger starts even when trying a stranger costs more than the safe option. My sentence in RESULT-trust.md,
"above it, no realistic audit rate starts the ledger", is wrong for a ledger that persists.

## Exploratory, not pre-registered
- Where is the cliff now? persist_t.py, 10 seeds: at q = 0.1 and q = 0.5 every seed takes off at t = 0.5, 0.6 and 0.8.
  At q = 0.03 takeoffs fall with price: 8/10, 7/10, 5/10.
- Budget or carry-over? (control suggested by the second-model review, persist_budget.py) Reset ledger with 10x
  longer generations (G = 300), t = 0.4: q = 0.1 gives 19/20, q = 0.03 gives 0/20. At q = 0.1 more audits per
  generation is enough. At q = 0.03, ten times the budget still never starts, and only records that survive the
  imitation step do (11/20).

## Limits
- Milking is measured as R picks with rep > 0.6 over the last 20 generations, when K is about 0.95. That denominator
  swamps it, and one false "kept" flag puts an R agent over 0.6. A sharper measure (R fitness against K fitness in
  the generation an agent turns R) is not run.
- The milked record is not heritable here: an agent that copies R does not copy the record. So milking is a one-shot
  rent that selection cannot spread. A model where reputations can be bought or inherited could behave differently.
- Second-model review (review_persist_fable.txt): no bug found in persist.py.
