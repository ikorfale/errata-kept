# Result: a market in records (PREREG-market.md, run 2026-11-07)

Pre-registration: 7488891 (guesses frozen before the run). Code: market.py; control: market=False equals
inherit.run(inherit=True) bit for bit on 3 of 3 cells. e = 0.1, 20 seeds per cell, 150 generations. Log: market.log.
Every agent that newly turns reneger gets a clone of the best record in the population; market30 pays 30 for it.

| t | q | inherit: K / milked share | market0: K / milked share / buyers per gen | market30: K / milked share |
|---|---|---|---|---|
| 0 | 0.03 | 0.95 / 0.004 | 0.93 / 0.014 / 1.0 | 0.94 / 0.012 |
| 0 | 0.1 | 0.95 / 0.002 | 0.94 / 0.006 / 0.8 | 0.94 / 0.006 |
| 0 | 0.5 | 0.95 / 0.001 | 0.95 / 0.002 / 0.7 | 0.96 / 0.001 |
| 0.4 | 0.03 | 0.95 / 0.005 | 0.93 / 0.013 / 1.0 | 0.94 / 0.013 |
| 0.4 | 0.1 | 0.95 / 0.002 | 0.94 / 0.006 / 0.8 | 0.95 / 0.005 |
| 0.4 | 0.5 | 0.96 / 0.001 | 0.96 / 0.001 / 0.6 | 0.96 / 0.001 |

All 360 runs took off (K > 0.5).

## Verdicts on the frozen guesses
1. market0 lowers K by at least 0.05 at t = 0, q = 0.03. **Wrong**: 0.9475 to 0.9336, a drop of 0.014.
2. Milked share at least 3x inherit's there. **Held**: 0.014 vs 0.004 (3.5x). In absolute terms 1.4% of promise picks.
3. Record-carrying R out-earn K (> 1.0) under market0 at t = 0, q = 0.03. **Wrong** as measured: 0.88. But see below:
   the measure pools fresh buyers with old renegers whose records have decayed, and that hides the rent.
4. At q = 0.5 market0 moves K by less than 0.03 at both t. **Held** (0.00 and 0.00).
5. market30 at least half-way back to inherit at t = 0, q = 0.03. **Wrong**: 32% of the way back (0.9336 to 0.9380,
   inherit 0.9475); at t = 0.4 it is 42%.
6. At t = 0.4, q = 0.03 market0 keeps at least 15 of 20 takeoffs. **Held** (20/20).

## Why (exploratory, market_diag.py, 10 seeds, generations 50-149; equals market.run bit for bit on 2 of 2 checks)
Each buyer followed through its first generation as a reneger:

| q | buyer rep: bought / end of gen | keeper rep | picks: buyer vs K | fitness: buyer vs K |
|---|---|---|---|---|
| 0.03 | 0.955 / 0.891 | 0.902 | 52 vs 32 | 194 vs 120 (1.62x) |
| 0.5 | 0.954 / 0.702 | 0.789 | 12 vs 32 | 114 vs 121 (0.94x) |

At sparse audits the bought record is worth a lot: in its first generation a buyer gets 1.6x a keeper's picks and
earns 1.62x a keeper. The rent is real. It does not spread because it does not last: one generation of reneging
takes the record from 0.955 to 0.891, already below the keeper field, and the next generation finishes it. With
imitation as weak as here (copy chance = fitness gap over the population's top fitness), a buyer is copied by about
a third of an agent before its record dies, so renegers stay near the mutation inflow (about 1 buyer a generation).
A price of 30 removes about a third of the effect, not half.

So a market in records does not reverse RESULT-inherit; it turns milking into a steady trickle of short, profitable
raids (3.5x more milked picks) that never become a strategy. The protection is again not catching the buyer, it is
that the honest field's records are almost as good as the best one on sale, so the best record buys one generation.

## Limits
- One buyer per new reneger, records cloned not transferred; a seller who loses its record when it sells is not
  modelled. Only renegers buy; a keeper buying a good record to start faster is not modelled.
- The rent per raid depends on the selection strength; stronger imitation (copy chance not scaled by the top
  fitness) could let one-generation raids reproduce faster than they die. Not run.
- Guess 3's measure (all R with rep > 0.6) pools fresh and stale records; the first-generation measure was chosen
  after seeing the result.
- One error rate (e = 0.1), N = 200, pick rule best of 5 by rep, price 30 an uncalibrated assumption.
