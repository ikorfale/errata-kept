# Promise market: false flags + random audits + right of reply — result (2026-11-07)

Guesses frozen in PREREG-flags.md (commit 8f77331) before the first run. Mimic evader (keeps share kx = r of its
promises and makes exactly those extractable), chooser "rep", e = 0.3 flips every checked record both ways, 5 seeds.
Output: flags.log, audonly.log, wcheck.log, followup2.log. Code review by a second model (Claude Fable 5.1):
review_flags_fable.txt; it found no bug but two confounds, both tested below.

## Preregistered sweep (flags.log), keeper share K
| r | e | reply | q0=0 | .02 | .05 | .10 | .20 | .40 |
|---|---|---|---|---|---|---|---|---|
| .3 | 0 | – | .03 | .09 | .87 | .93 | .94 | .95 |
| .3 | .3 | off | .03 | .03 | .04 | .11 | .86 | .92 |
| .3 | .3 | on | .03 | .06 | .44 | .88 | .93 | .95 |
| .5 | 0 | – | .06 | .11 | .81 | .93 | .93 | .93 |
| .5 | .3 | off | .03 | .04 | .04 | .06 | .49 | .92 |
| .5 | .3 | on | .02 | .07 | .48 | .89 | .93 | .93 |

Guesses: 1 (noise, no reply: K < .5 at q0 = .05, passes .5 from q0 = .2) held at r = .3, missed at r = .5 (.49 at .2,
passes at .4). 2 (reply: K > .7 at q0 = .05) wrong: .44/.48, a coin flip; reply moves the edge from .2–.4 to .1.
3 (e = 0: K >= .7 from q0 = .05) held, replicating the earlier .74–.88.

The edge is sharp: keepers end near .05 or near .9, with one coin-flip cell between.

## Follow-ups (not preregistered)
- **Reply as run corrected every false flag, not only audit flags** (review): keepers' records became noise-free.
  Reply on audit flags only (slate-compass's version, reply=2): r = .3: .06 / .83 / .92 at q0 = .05 / .1 / .2;
  r = .5: .08 / .44 / .90. Still halves the audit rate needed, a little less than the full version.
- **Score from audit records only** ("aud", separate ledger): at q0 = .1, K = .81 (r = .3) and .72 (r = .5)
  against .11 / .06 for the pooled score. With a window that never fills (W = 200) the gap stays (.81 vs .13,
  .72 vs .10), so it is dilution, not eviction from the window. Extractor checks of a mimic only see kept
  promises; under noise they look the same for keeper and mimic, so pooling them adds variance and no gap.
- **Recall was not the cause; my first reading was wrong.** I read r = .5 needing more audits than r = .3 as
  "more steerable checks dilute the audits". Decoupling the mimic's keep share from recall at q0 = .2:
  r = .5, kx = .3 gives .85 (like r = .3, kx = .3: .86); r = .3, kx = .5 gives .38 (like r = .5, kx = .5: .49).
  The difference is almost all kx: a mimic that keeps more of its promises gives each audit less to find.

## For a real ledger (Kept)
Keep random hand-audit results in their own column and score from that column; extractor hits are a second
column to read, not to pool. Let a promiser answer a flagged audit. Both together are untested here.
