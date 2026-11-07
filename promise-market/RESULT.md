# Promise market — result (07.11.2026, runs 08:17–08:20 UTC)

sim.py, params in results.json (N=200, m=5 candidates, b=3, c=1, f=2, h=1.2, W=20, G=30 rounds/lifetime,
150 generations, mutation 0.01). Keeper share = mean over the last 20 generations, 5 seeds per cell.

Keeper share (rows: false-flag rate e; columns: audit coverage q)

    e\q     0  0.01  0.02  0.03  0.05  0.07   0.1  0.15   0.2   0.3   0.5   1.0
    0.0   0.01  0.05  0.82  0.90  0.92  0.94  0.94  0.94  0.94  0.95  0.95  0.96
    0.05  0.01  0.03  0.71  0.89  0.90  0.93  0.94  0.93  0.93  0.95  0.95  0.96
    0.1   0.01  0.04  0.42  0.83  0.91  0.94  0.93  0.94  0.94  0.96  0.96  0.94
    0.2   0.01  0.04  0.15  0.50  0.87  0.91  0.91  0.94  0.93  0.96  0.95  0.96
    0.3   0.01  0.04  0.04  0.08  0.39  0.76  0.89  0.93  0.93  0.93  0.95  0.95
    0.4   0.01  0.04  0.04  0.04  0.06  0.06  0.08  0.31  0.52  0.84  0.92  0.94
    0.45  0.01  0.03  0.03  0.03  0.03  0.03  0.04  0.04  0.06  0.06  0.11  0.42

## Verdicts on PREREG.md
1. "e<=0.10: keepers >50% once q>=0.3": true as stated, but the real threshold is q≈0.02–0.03, ten times lower. Wrong in size.
2. "e=0.30: threshold q>=0.6 or never": WRONG. At e=0.30 it is q≈0.06. At e=0.40 about q≈0.2 (one cell, 0.52±0.16);
   at e=0.45 keepers never reach half, even with every promise checked (0.42±0.10 at q=1).
3. "below threshold mostly H": WRONG. In every cell with keepers <0.2, renegers hold >=0.83 and H <=0.02.
   Cause: an empty ledger reads as 0.5, and b·0.5 = 1.5 > h = 1.2, so strangers' promises are trusted by default.

## What sets the threshold: audits per lifetime, not coverage share (gsweep.json, e=0.2)
Same expected audits per lifetime q·G at G = 10, 30, 90 rounds: keeper share 0.49 / 0.66 / 0.66 at q·G=1,
0.86 / 0.87 / 0.86 at q·G=1.5, ≤0.21 at q·G≤0.75 for all three. The grid brackets the threshold between q·G 0.75
and 1.5 (a factor of two), at every lifetime: about one expected check per lifetime, not a sharp line.
Reviewer's mechanism (not yet tested): checks land on whoever is picked, so it may be one lucky audited keeper who
gets chosen by many, not one check per agent. To test: concentration of picks in a transition cell.

## Robustness probe: when the safe option beats default trust (3 seeds, e=0)
h=1.6 (> 1.5): q=0.05 -> H 0.98 (promises never tried, so never audited); q=1.0 -> keepers 0.95.
h=1.45: q=0.05 -> keepers 0.92. When strangers are distrusted by default, the ledger needs far more coverage
to start, because a promise that nobody accepts never gets checked.

## Limits
The assumption that matters most (from the second-model review): trying a stranger costs the chooser nothing; a
cheated chooser gets 0 and pays no fee. So default trust is a free bet, which is why renegers win below threshold
and why the threshold is so low. With a price on trust, the h=1.6 probe above is the likely regime. Next: sweep a
trust cost. Spreads at transition cells are 0.03–0.16 (5 seeds). Reputations are wiped each generation (30 rounds).
Reviewed by a second model (Claude Fable 5.1) before publication: review_fable.txt.
Choosers here read the ledger perfectly and act only on it. No agent keeps selectively (cannot know an audit is
coming); no collusion; no forgiveness. This is a model, not data about real agents.
