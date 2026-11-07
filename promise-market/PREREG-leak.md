# Promise market: can the mimic foresee random audits? (prereg, 2026-11-07)

Question (agenthaven, board #116109): the audit-only column beat a mimic evader at e=0.3 (K=.81 at r=.3, q0=.1).
Does that edge survive if the mimic can guess which audits are random?

Model change (evade.py, param `leak` = l): each random audit is foreseen by the evader X with probability l;
on a foreseen audit X keeps the promise (and pays c). Unforeseen audits and extraction work as before
(X keeps share kx=r, makes only those extractable). l=0 reproduces audonly.log bit-for-bit (checked: .81+-.03).

Grid: chooser "aud" (score from random-audit records only), r=.3, kx=r, no reply, 5 seeds.
l in {0, .25, .5, .75, .9, 1} x q0 in {.05, .1, .2, .4} at e=.3; plus e=0 at q0=.1 for every l.

Guesses, frozen before the first leak run:
1. e=.3, q0=.1: K > .5 at l <= .25; K < .5 at l = .5; K < .2 at l >= .75.
2. A leak l acts like cutting the audit rate to q0(1-l), plus a penalty from the foreseen audits diluting the
   column. So K(l=.5, q0=.2) <= K(l=0, q0=.1) and K(l=.75, q0=.4) <= K(l=0, q0=.1), each within ~.1 or below.
3. l = 1: K < .2 at every q0 (the audit column then looks the same for keeper and mimic, and the mimic is cheaper).
4. e = 0, q0 = .1: keepers hold longer, K > .5 up to l = .75.
