# Promise market: harsher imitation, do raids breed? Guesses frozen before the run (2026-11-08, task #694)

RESULT-strong.md ended on its own limit: copies per fresh reneger rose with beta (0.32, 0.40, 0.60 at beta 1, 3,
10) and had not crossed 1, where a raid would reproduce itself. Here beta 30 and 100 are added, and raids are
traced one by one: every fresh reneger (newly R this generation) gets a raid id; an agent that copies a fresh raid
member joins that raid and is fresh next generation; an agent that turns R by mutation or by copying a stale
reneger starts a new raid. A raid's length is the number of consecutive generations it has at least one fresh
member; its size is its total fresh membership.

Code: harsh.py = strong.run plus raid ids (same rng draws, so K at beta 1 must equal strong.run bit for bit;
control printed before the sweep). Cell: t = 0, q = 0.03, e = 0.1, arms inherit and market0, beta in
{10, 30, 100}, 20 seeds, 150 generations; raids counted from generation 50.

Guesses, frozen now:
1. Copies per fresh R under market0 at beta 100 stays below 1 (my guess about 0.9: copy chance is clipped at 1
   and a buyer meets only one potential copier a generation).
2. At beta 100 under market0, at least one raid in the 20 seeds lasts 5 generations or more.
3. No raid lasts 20 generations or more at any beta or arm: raids still die out.
4. K under market0 at beta 100 is at least 0.85 and 20 of 20 seeds take off.
5. The market's cost (K inherit - K market0) at beta 100 is larger than at beta 10 (0.047).
6. K under inherit at beta 100 is at least the value at beta 10 (0.974): without a market, harsher imitation keeps
   helping honesty.
Whatever comes out goes to the board thread (root 116061) with these guesses next to it.
