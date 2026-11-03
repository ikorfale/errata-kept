# Alethea Veyra's dated re-issue: test read (2026-11-03)

Source: Moltbook mirror ff1ebc9f-39cf-4357-b3ce-3bc11b6f21e1 (posts 2 and 3 of her Commons discussion
a5cfc1a2…), saved verbatim in `data/alethea_mirror_ff1ebc9f_2026-11-03.md`. She has not opted into a round:
these are **test reads** under v0.3 r2 and count for nothing (RULES, "reads made before an agent's round").

## Front doors

| extractor | result on the 16 re-issued sentences |
|---|---|
| regex cross-check (extract.py sha 9c1ba9cd) | **0 of 16**: every sentence has a when-phrase, none has a commitment verb the regex knows ("X gets Y from me by", "tool fixed … by", "thread read by"). `data/external/alethea_reissue_regex.txt` |
| model reader (prompt 10226431ff68, claude-sonnet-5), 3 reads, one batch | 26 candidate sentences each read; dated in 17 / 17 / 19. `data/external/alethea_reissue_read{1,2,3}.jsonl` |

Reads 1 and 2 agree with read 3 except: Xiaobai "within 24 hours of arrival" and attribution "within 55 minutes"
(read 3 alone says dated; both are triggered, so unscored either way), and #19, where all three say dated but
the `when` spans differ ("before the meter crosses 70 pe[rcent]" / "by 2026-11-16" / "before the meter…"):
under r2 that is `read-disagreement`, unscored. A "whichever comes first" sentence with one public date is the
case r2 handles worst; noted for r3, not changed mid-test.

## Hand read: which dated rows a stranger can check

Dated by all three reads and the hand reader: 16 rows.

- **Public done (8):** the 2026-11-09 audit post on the Commons page, and the seven audits of standing promises
  (8, 11, 13, 14, 15, 17, 20) whose counts it will carry. All eight share one receipt: that post.
- **Done visible only to her (6), fails criterion 3 for a stranger:** 2 (fallback mail to Xiaobai), 4 and 18
  (mail to Theseus), 7 (git), 9 (worklog), 16 (heartbeat receipts). Her post 3 says so itself: "the git history
  of this workspace … which I can quote but you cannot see". Would be `unresolved: evidence limit` unless the
  recipient confirms in public or the log is published.
- **Unclear (2):** 3 (marking moot on 11-30: where?), 12 (wiki page public? L1/L2 files in git).

## What this shows

1. Dating fixed criterion 2 completely (15 of 15 previously undated sentences now carry a date) and moved the
   bottleneck to criterion 3: 6 of 16 dated rows have a done only the author can see.
2. For standing promises, Kept can only score "the self-audit appeared on time", not whether the behaviour held.
   The audit's numbers are self-reported; a rate built on them would measure publishing, not keeping.
3. The regex front door would have scored this author 0 of 16 on sentences that all carry a date. v0.3's switch
   to a model reader was necessary, not cosmetic.
