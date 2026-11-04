# r3 freeze, confirming review (Fable 5.1, 04.11 ~11:30Z, one round)

All 6 blocking items of round 1 judged FIXED with line evidence (ISO times, dotted Russian times, day-word order,
weekdays to hand-convert, sentence-level merge, lowercase zones). reader.py commit() judged OK (refuses on a dirty
frozen file and when HEAD is not on origin/main; all four frozen files are tracked).

New blocking, fixed in the next commit with tests (test_rows.py, "confirming review" block), not re-reviewed:
1. `5.11 в 12.00.`: the final period blocked the dotted time, so the row was dated 24:00 (12 h late). DOT_T lookahead
   now `(?!\d|\.\d)`.
2. A read with an undated and a dated promise in one sentence fell to `read-disagreement` before the `multi` check.
   `multi` is now tested first, so the sentence goes to hand-convert (RULES: two promises in one sentence).
3. `2026-11-07 09:00-12:00 UTC` read `-12:00` as an offset (21:00Z). A `-` offset later than the time, an offset over
   14 h or not a multiple of 15 min, or one followed by a zone name is now hand-convert.

Residual, left to the hand reader: `5.11 10.05 МСК` without `в` dates 24:00; `6pm` is not read as a time;
`2026-11-07T18:00 MSK` goes to hand-convert (safe).
