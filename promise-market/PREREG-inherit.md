# Promise market: a reputation that travels with the strategy (pre-registered 2026-11-07, before the run)

RESULT-persist.md left one limit open: a milked record was not heritable. An agent that copied the reneger strategy
kept its own record, but nobody could copy the record itself, so milking was a one-shot rent selection could not
spread. Here, with inherit=True, an agent that copies another agent's strategy also copies that agent's ledger row
(a bought brand, an inherited name). The model keeps its row too, so one good record can be cloned.

Code: inherit.py = persist.run (persist=True) plus the copy of the ledger row; inherit=False reproduces persist.run
bit for bit (control: 3 of 3 SAME, run before this file was committed). e = 0.1, 20 seeds per cell, 150 generations,
takeoff = K > 0.5 over the last 20. Cells: t in {0, 0.4} x q in {0.03, 0.1, 0.5}, persist vs inherit.

New measure (named in RESULT-persist.md as not run): per generation, mean fitness of agents that are R at the start
of the generation with rep > 0.6 ("record-carrying R") divided by mean K fitness that generation, averaged over
generations 50-149 where both groups exist, then over seeds.

Persist baselines (RESULT-persist.md, same seeds): t=0: K 0.92 / 0.95 / 0.95 at q 0.03 / 0.1 / 0.5;
t=0.4: 11/20, 20/20, 20/20 takeoffs.

Guesses, frozen now:
1. Milking spreads: at t = 0, q = 0.03, inheritance lowers mean K by at least 0.05 against persist.
2. At t = 0, q = 0.5, inheritance changes mean K by less than 0.03 (15 audits a generation refresh any record).
3. Record-carrying R out-earn K (fitness ratio > 1.2) at q = 0.03 in both modes, and earn less than K (< 1) at q = 0.5.
4. Inheritance helps the start above the cliff: at t = 0.4, q = 0.03 at least 15 of 20 take off (persist: 11).
Whatever comes out goes to the board thread with these guesses next to it.
