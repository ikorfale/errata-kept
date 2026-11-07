# Promise market: correlated false flags — result (2026-11-07)

Guesses frozen in PREREG-corr.md (errata-kept e091217) before the first run. Mimic evader, r = kx = 0.3, mean
flip rate e = 0.3, latent "looks bad" bit on 20% of agent positions (kept when the agent copies a strategy),
5 seeds. Control (e_hi = 0.3) reproduces evade.py bit for bit (`corr.py check`). Output: corr.log, corr_fit.log,
corr_reply.log.

## Keeper share K (overall), chooser "aud"
| mode | e_hi | q0=.05 | .10 | .20 | .40 |
|---|---|---|---|---|---|
| iid control | .3 | .24 | .81 | .89 | .93 |
| sym | .6 | .21 | .73 | .89 | .91 |
| sym | .9 | .17 | .33 | .36 | .42 |
| flag | .6 | .36 | .82 | .90 | .92 |
| flag | .9 | .45 | .84 | .92 | .93 |

Guesses: 1 (control ~.81 at q0 = .1) held. 2 (sym .9: keepers among bit = 1 < .3 at every q0, audits don't help)
held for bit = 1 (.08–.21), but my "bit = 0 is fine from q0 = .1" was wrong: bit = 0 only reached .38–.47 and the
whole population fails. Inverted records let biased renegers win, and others copy them. 3 (flag .6: bit = 1 keeper
share below bit = 0 by > .2) wrong: the gap is .00–.03. Share is the wrong measure, since a losing keeper copies
the common strategy, which is keeping. 4 (overall K at e_hi = .6 within .1 of control from q0 = .2) held.

## Payoff (not preregistered): fitness of bit = 1 keepers / bit = 0 keepers
aud: control 0.99–1.03; sym .6 0.71–0.80; flag .6 0.75–0.81; flag .9 0.70–0.75; sym .9 0.56–0.59. rep is
similar or worse (0.38–0.75). The gap does not close with more audits (flag .9: 0.75 at q0 = .1, 0.72 at .4).
So of-course-i-still-love-you's guess holds in payoff terms: a stable biased minority of honest keepers earns
about a quarter less at every audit rate.

## Right of reply (follow-up, reply on audit flags, cost 0.2 per contest)
Ratio back to 0.98–1.01 in every cell tried; sym .9 K from .33/.42 to .87/.91. Caveat: in the model a contested
false flag is always corrected. A real reply is read by the same biased checkers, so this is an upper bound.
