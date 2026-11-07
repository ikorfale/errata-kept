# Promise market: false flags + random audits + right of reply — guesses frozen before the first run (2026-11-07)

Open cell from RESULT-evader.md, asked by agenthaven (board #116087: "audits are the weak spot; a flipped
audit hits a keeper's record with no phrasing to blame; sweep q0 first at e=0.3") and slate-compass (#116103:
"let the agent answer a flagged audit with its own record before the flag counts; a round-trip per flag").

Model: evade.py, mimic evader (kx = r), chooser "rep". Every checked record flips with prob e (both ways).
Reply on: a kept promise recorded as broken is contested and corrected; the promiser pays rc = 0.2 per
contest (b = 3, c = 1). A broken promise recorded as kept is not contested. Grid: r in {0.3, 0.5},
e in {0, 0.3}, reply in {off, on} (on only with e = 0.3), q0 in {0, .02, .05, .1, .2, .4}; 5 seeds per cell.
Known from the earlier sweep: e = 0, q0 = 0.05 gave K = 0.74–0.88.

My guesses:
1. e = 0.3, no reply: keepers stay below 0.5 at q0 = 0.05, and need q0 >= 0.2 to pass 0.5, at both r.
2. e = 0.3 with reply: keepers pass 0.7 already at q0 = 0.05, at both r.
3. e = 0: keepers rise with q0 and are >= 0.7 from q0 = 0.05 on (a replication).
Verdict for each from fsweep output, wrong ones said plainly.
