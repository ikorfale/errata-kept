# Dated-flag stability, looktwin-feedback blind30 (task #629, 04.11)

Question: how often does the reader's `dated` flag change between reads of the same post, and does the
three-read rule (RULES r3: dated only if all three reads say dated with the same UTC deadline) matter?

Setup: the 30 seqs of `data/looktwin-feedback_blind30_seqs.txt`. Reads 2, 3, 4 made 04.11 13:25-13:40Z with the
frozen reader (prompt 10226431ff68, code eeebd8ed352b, claude-sonnet-5, CLI 2.1.280, commit eccc414). Read 1 is the
03.11 run (same prompt and model, older reader code, no commit field); rows.py refused to merge it with the
others ("different reader identities"), as it should, so it enters only the post-level check.
Rows: `rows.py MSK read2 read3 read4` -> `data/flip629/rows234.jsonl`; numbers by `data/flip629/flip.py`.

Results:
- 62 candidates: 55 unscored, 3 dated, 2 hand-convert, 2 read-disagreement.
- 9 candidates were dated in at least one read; 5 in all three; **4 of 9 flipped**:
  - 80500 dated / not / dated (an explicit "by 10.10 12:00 MSK" fallback) -> lands as unscored (conditional);
  - 96667 not / dated / not;
  - 82612 and 96666: one read did not output the sentence at all -> `read-disagreement`, goes to the hand reader.
- Post level, four reads: 30 posts, 5 with a dated promise in every read, 21 in none, **4 flip** (13%).

What it means: a single read would have counted up to 9 dated candidates where the unanimity rule keeps 5, and the
4 that move are exactly the borderline ones (fallback clauses, a "within 30 minutes" service promise, a missed
sentence). Two of the four flips are misses, not wrong flags, so "all three reads" also catches reader recall
gaps, and routes them to a hand read instead of losing them. RULES.md is not edited (it is frozen at round1-freeze);
its line "flipped in 1 of 5 reads on one post" is superseded by this measurement: 4 of 9 candidates, n=30 posts,
one agent. Small sample: the rate could be quite different for other writers.
