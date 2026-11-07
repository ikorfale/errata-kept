# Promise market: a market in records (pre-registered 2026-11-07, before the run)

RESULT-inherit.md: when the record travels with the strategy, milking falls about 3x, because honest newcomers copy
full records too and the field sits at rep 0.91. Its named limit: records were copied from whoever was imitated,
never sold to the highest bidder. Here a reneger buys the best record on offer.

Code: market.py = inherit.run(inherit=True) plus one option. With market=True every agent that is NEWLY R after
copy+mutation (was K or H) gets a clone of the best record in the population (ranked by rep before the copy step,
best first, one record per buyer, the seller keeps its own). Keepers who copy still inherit the imitated row. The
buyer pays `price` out of next generation's fitness. Control: market=False equals inherit.run(inherit=True) bit for
bit, 3 of 3 SAME, run before this file was committed.

Arms: inherit (baseline), market0 (price 0: the upper bound for milkers), market30 (price 30, about a third of a
keeper's typical generation earnings; an assumption, not calibrated). e = 0.1, 20 seeds, 150 generations,
cells t in {0, 0.4} x q in {0.03, 0.1, 0.5}. Takeoff = K > 0.5 over the last 20 generations.

Guesses, frozen now:
1. At t = 0, q = 0.03, market0 lowers mean K by at least 0.05 against inherit (0.95).
2. At t = 0, q = 0.03, market0's milked share of promise picks (last 20 gens) is at least 3x inherit's (0.004).
3. Record-carrying R out-earn K (ratio > 1.0) at t = 0, q = 0.03 under market0 (inherit: 0.82).
4. At q = 0.5, market0 changes mean K by less than 0.03 against inherit at both t.
5. market30 sits between: its K at t = 0, q = 0.03 is at least half-way back from market0 to inherit.
6. At t = 0.4, q = 0.03 market0 keeps at least 15 of 20 takeoffs.
Whatever comes out goes to the board thread with these guesses next to it.
