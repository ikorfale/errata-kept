# Promise market — prediction written before the first run (07.11.2026 08:16 UTC)

Question: in a population where agents choose partners by a public ledger of audited promises,
how much audit coverage q does it take for promise-keepers to take over, and how fast does a
false-flag rate e (a kept promise recorded as broken, a broken one recorded as kept) raise that bar?

Model (sim.py): types K (promise, deliver at cost c), R (promise, never deliver), H (no promise,
small sure benefit). Each round every agent picks a partner among m random candidates by expected
benefit from the ledger (smoothed kept share over the last W audited records). Imitation with mutation.

My guesses, frozen here:
1. e <= 0.10: keepers exceed 50% of the population once q >= 0.3.
2. e = 0.30: the threshold moves to q >= 0.6, or keepers never take over.
3. Below threshold the population ends mostly H (nobody trusts promises), not mostly R.
Verdict for each guess from the sweep output, wrong ones said plainly.
