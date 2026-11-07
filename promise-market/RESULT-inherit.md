# Result: a reputation that travels with the strategy (PREREG-inherit.md, run 2026-11-07)

Pre-registration: 3fbb533 (guesses frozen before the run). Code: inherit.py; control: inherit=False equals
persist.run (persist=True) bit for bit on 3 of 3 cells. e = 0.1, 20 seeds per cell, 150 generations. Log: inherit.log.

| t | q | persist: takeoffs / K / carrier-R÷K fitness | inherit: takeoffs / K / carrier-R÷K fitness |
|---|---|---|---|
| 0 | 0.03 | 20/20, 0.92, 0.96 | 20/20, 0.95, 0.82 |
| 0 | 0.1 | 20/20, 0.95, 0.87 | 20/20, 0.95, 0.78 |
| 0 | 0.5 | 20/20, 0.95, 0.80 | 20/20, 0.95, 0.75 |
| 0.4 | 0.03 | 11/20, 0.61, 2.36 | 20/20, 0.95, 0.80 |
| 0.4 | 0.1 | 20/20, 0.94, 0.86 | 20/20, 0.95, 0.75 |
| 0.4 | 0.5 | 20/20, 0.95, 0.78 | 20/20, 0.96, 0.73 |

Milked share of promise picks (last 20 generations) at t = 0, q = 0.03: persist 0.013, inherit 0.004.

## Verdicts on the frozen guesses
1. Inheritance lowers K by at least 0.05 at t = 0, q = 0.03. **Wrong, opposite sign**: K rises 0.92 to 0.95, and the
   milked share falls about 3x.
2. At t = 0, q = 0.5, K changes by less than 0.03. **Held** (0.00).
3. Record-carrying R out-earn K (> 1.2) at q = 0.03 in both modes; below 1 at q = 0.5. **Wrong for the first half**:
   carriers earn 0.96 and 0.82 of K at t = 0. The only cell where they out-earn K (2.36) is t = 0.4, q = 0.03 without
   inheritance, where 9 of 20 seeds never take off and K agents earn little. Second half held (0.80, 0.75).
4. At t = 0.4, q = 0.03, at least 15 of 20 take off with inheritance. **Held** (20/20; persist 11/20).

## Why (exploratory, inherit_diag.py, 10 seeds, t = 0, q = 0.03, generations 50-149)
| | K: mean rep, audited entries | carrier R: mean rep, entries, count per generation |
|---|---|---|
| persist | 0.64, 13.9 | 0.70, 19.3, 5.1 |
| inherit | 0.91, 20.0 | 0.87, 20.0, 6.0 |

Without inheritance a new keeper starts with an empty record (rep 0.5) and the average keeper sits at 0.64, so a
former keeper turned reneger with a full old record (0.70) looks better than the honest field. With inheritance a
new keeper copies a full record from the keeper it imitated, the field sits at 0.91, and a milker's record (0.87) is
no longer the best on offer. Heritable records help milkers a little and honest newcomers much more, because most
copying is of keepers. What protects choosers here is not catching the milker but the honest competition having
records too.

## Limits
- Copying is payoff-biased imitation of a random other; records are copied, never sold to the highest bidder. A
  market in records (a reneger buys the best record available) is not modelled and could reverse this.
- The diagnostic re-implements the loop and was not checked bit for bit against inherit.run.
- One error rate (e = 0.1), one population size, one pick rule (best of 5 by rep).
