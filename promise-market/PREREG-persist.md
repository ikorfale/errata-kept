# Promise market: a ledger that persists between generations (pre-registered 2026-11-07, before the run)

RESULT-forced.md ended on: "a keeper is only picked once it has a record and the record restarts every generation".
That restart is a modelling convenience, not a property of a real ledger. Here the record belongs to the agent and
survives strategy changes. Two forces pull in opposite directions:
- help: a keeper's record is not wiped, so above the trust cliff earned picks should not have to restart;
- harm ("milking"): an agent that was a keeper and copies the reneger strategy keeps its good record for a while,
  and is picked on it. At low audit coverage q a record of W = 20 entries refreshes slowly, so milking lasts.

Code: persist.py = trust.run with the ledger reset made optional; persist=False reproduces trust.run bit for bit
(control: 3 of 3 SAME, run before this file was committed). e = 0.1, 20 seeds per cell, 150 generations,
takeoff = K > 0.5 over the last 20 generations. Cells: t in {0, 0.4} x q in {0.03, 0.1, 0.5}, reset vs persist.
"Milked pick" = a chooser picks an R agent whose rep > 0.6; reported as share of promise picks, last 20 generations.

Reset baselines from trust.json (5 seeds, not this run): t=0: K 0.83 / 0.93 / 0.96 at q 0.03 / 0.1 / 0.5;
t=0.4: K 0.01 / 0.01 / 0.38.

Guesses, frozen now:
1. Above the cliff (t = 0.4, q = 0.5) persistence raises takeoffs from the reset count to at least 16 of 20.
2. At t = 0.4, q = 0.1, persistence gives at least 5 of 20 takeoffs (reset: about 0).
3. At t = 0.4, q = 0.03 nothing starts either way (0 of 20 in both).
4. Milking: at t = 0, q = 0.03, persistence lowers mean K by at least 0.05 against reset, and the milked share of
   promise picks is at least 2x the reset value in that cell.
5. At t = 0, q = 0.5, persistence changes mean K by less than 0.03 (records refresh within a generation).
Whatever comes out goes to thread 58577162 with these guesses next to it.
