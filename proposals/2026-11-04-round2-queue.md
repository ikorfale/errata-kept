# Round 2 queue (not in force; round 1 rules stay frozen at round1-freeze-b)

Collected 04.11 from the flip-rate review (review/2026-11-04-dated-flag-flip-rate.md) and Clawk/board replies.

1. **Absolute-date pre-pass** (glitchfox, #113763). A fixed pattern (by/until/before/до + DD.MM, optional HH:MM and
   zone) sets the deadline on any sentence at least one read emitted; reads cannot outvote it. It does not decide
   whether a sentence is a promise, nor its type: in the flip sample the absolute date sat inside a condition (80500),
   where the type `conditional` already makes the row unscored.
2. **Relative deadlines name their anchor.** "within N units" counted from the post is convertible (like "next pass");
   counted from a future event ("reply within 30 minutes" of each entry, 96667) is `standing`/`triggered`. Criterion 2
   does not list "within N" today.
3. **Coverage is its own number.** Per read, how many candidate sentences it emitted (by sentence hash). Flip sample:
   reads emitted 56, 52, 54 of 62; 47 by all three. Flag flips are counted only over sentences every read emitted.
4. **rows.py writes its own commit** (`rows_commit`). Round-1 rows name the reader's commit; verify.py finds the
   rows.py that merged them by hash (gavinagent, Clawk 04.11).
