**BLOCKING**

1. **ISO time lost** (`rows.py:56-70`). `2026-11-07T18:00Z`: the `T` kills the `\b` before `18:00`, so neither the Z zone nor the time is seen; result is 24:00 of 07.11 in the agent's zone (MSK agent: 21:00Z, 3 h late). `2026-11-07 18:00Z` is also wrong: the Z alternative swallows the time, `tm` then searches the span minus that token and finds nothing, giving 2026-11-08T00:00Z. All three reads agree, so the row is `dated` with the wrong deadline.
2. **Russian dotted times** (`rows.py:88-97`). `5.11 в 12.00 МСК` converts to 24:00 of 5.11 (12 h late, silently dated). `к 12.00 МСК` alone hits `bad-date` and is labelled `read-disagreement`, which the text does not allow (should be `hand-convert`).
3. **Day-word order and Cyrillic boundaries** (`rows.py:114-123`). `сегодня утром` matches `сегодня` first and becomes 24:00 today instead of 12:00; posted at 14:00 it should be `undated` but is dated. `послезавтра` contains `завтра` and is read as tomorrow (one day early). Same for `сегодня днём`. Fix: test morning/afternoon before today, use `\b` on the Russian words.
4. **Weekdays are not in the Verdicts table** (`rows.py:124-126`, `RULES.md:79-86`). The prompt calls a weekday dated and rows.py converts it, resolving "by Wednesday" posted on a Wednesday to 24:00 today. RULES.md never defines a weekday, so the code decides what the text does not. Add a table line or make weekdays `hand-convert`.
5. **Merge by exact folded quote loses rows** (`rows.py:134-135,182`). Reads that quote the same sentence with a different apostrophe (`I’ll` vs `I'll`), dropped markdown `**`, or a trailing clause omitted become two candidates, each `read-disagreement`. RULES.md:18 only allows that mark for a flag or deadline disagreement, so a promise all three reads dated is lost on a quoting nit.
6. **Lowercase zone tokens ignored** (`rows.py:56`). `by 18:00 utc` or `msk` falls through to the agent's self-named zone; for an MSK agent writing `utc` that is a 3 h error, silently dated.

**Non-blocking**

- `bad-date` and `no-when` with `dated: true` end as `read-disagreement`; RULES.md:31-32 says `hand-convert` for anything rows.py cannot convert.
- rows.py only sees the `when` span, so a zone named elsewhere in the post ("all times MSK") never wins, contrary to RULES.md:80. The hand reader has to catch it; printing the local-time reading with the row would help.
- 180-day rollover: `by 11.05` posted 04.11 stays 2026 (177 days in the past). A past calendar date is still `dated`.
- False positives in short spans: `Decision 5` reads as 5 Dec, `step 3.2` as 3 Feb. Unlikely in a `when` span.
- Unscored rows carry no `type` (triggered/conditional/standing/undated) though RULES.md:66-68 requires it; only `trigger`/`standing` per read.
- Signature detection hardcodes `errata` and `fable-terminal`, so `closing` is wrong for other agents' signatures.
- Reader identity omits the CLI version and any user-level CLAUDE.md that `claude -p` still loads; the four hashes do not pin the full input.
- test_rows.py covers none of the inputs above; add them before the tag.