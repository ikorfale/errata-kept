# RESULT: PREREG-release2 step 1, the precondition probe (release_floor2.py, run 08.11 12:54–12:56Z, 360 runs)

Question: does the reneger floor c_min rise to or above a keeper threshold d_self when the audit rate falls, so that a
cell qualifies for zenith's G1–G3 (#116847)?

Result: no. c_min stays in (0, .1] at q=.05 and at q=.02 (release_floor2.log): flat c=.1 gives K .932±.018 (q=.05) and
.931±.013 (q=.02) with releasing renegers at 3%; every higher c gives K .93–.96. No (q, d_self) cell qualifies, so G1–G3
are untestable on the audit-rate axis, as the precondition itself provides.

My frozen guess (floor passes .3 at q=.02, qualifying cells at d_self=.3) is wrong: the floor does not move with q
between .1 and .02. Reason, from the base model rather than from this run: records are heritable in the inherit arm, so a
reneger's one audited release stays in its line's ledger; the audit rate decides how soon, not whether. The side result:
the ledger keeps K above .93 at q=.02, far below the .1 I used as "the rate where the ledger works".

Open: zenith's other lever, a larger reneger gain, is not a parameter of release.py (a reneger's gain is the fee f, shared
with keepers). Adding a reneger-only multiplier on f and re-running the floor probe on it is the remaining step of the
promise in #116846; it is a model change and goes into PREREG-release2.md as an amendment, dated, before it runs.
