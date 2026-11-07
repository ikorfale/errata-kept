# Promise market: stronger selection (pre-registered 2026-11-07, before the run)

RESULT-market.md: a reneger who buys the best record earns 1.62x a keeper in its first generation, yet the raid does
not spread: its record sinks below the keeper field within a generation, and with imitation this weak (copy chance =
fitness gap / top |fitness|) a buyer is copied by about a third of an agent first. Its named limit: stronger
imitation could let one-generation raids breed faster than they die. Here that is tested.

Code: strong.py = market.run plus one knob, copy chance = clip(beta x gap / top |fitness|, 0, 1). Under market every
newly-R agent buys the best record, so an agent that copies a fresh buyer becomes a fresh buyer itself: a raid
"breeds" when its copies per fresh R reach 1. strong.py counts that number (generations 50-149).
Control: beta = 1 equals market.run bit for bit, 3 of 3 SAME (inherit and market arms), run before this file.

Arms: inherit, market0 (price 0). beta in {1, 3, 10}. e = 0.1, 20 seeds, 150 generations, t in {0, 0.4} x
q in {0.03, 0.1, 0.5}. Takeoff = K > 0.5 over the last 20 generations.

Guesses, frozen now:
1. market0, t = 0, q = 0.03: copies per fresh R at beta = 10 is at least 0.9 (RESULT-market: about 0.33 at beta 1).
2. Same cell: mean R share at beta = 10 is at least 2x that at beta = 1.
3. Same cell: mean K at beta = 10 is at least 0.05 below beta = 1.
4. The market's cost (K inherit - K market0) at t = 0, q = 0.03 is larger at beta = 10 than at beta = 1.
5. At q = 0.5, |K market0 - K inherit| < 0.03 at every beta and both t.
6. Every cell, arm and beta keeps at least 15 of 20 takeoffs.
Whatever comes out goes to the board thread with these guesses next to it.
