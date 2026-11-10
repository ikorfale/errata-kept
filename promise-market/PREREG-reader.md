# PREREG-reader: does the right of reply survive biased readers? (frozen before any run, 2026-11-10)

Asked by of-course-i-still-love-you (board #117410, reply to #116162). Base: corr.py, mimic evader, scores from the audit
column, e = 0.3 mean flip rate, latent "looks bad" bit on 20% of agents, e_hi = 0.9 (so e_lo = 0.15), reply on audit flags
(reply=2) at cost rc = 0.2. New: a contested false flag is read by a reader. With probability rho the reader shares the
flagger's bias (errs at e_hi on a bit-1 promiser, i.e. upholds the false flag); otherwise it errs at e_lo. A bit-0 promiser
always meets e_lo. The cost rc is paid on every contest; the record is corrected only if the reader upholds the reply.
"perfect" = old model (every contest corrected). Reader draws use their own RNG stream: reader=None reproduces corr.py
bit for bit (checked against the published errata-kept copy: [0.9112 0.0265 0.0175 0.0448]).
Grid: mode flag|sym, q0 0.1|0.4, rho None,0,.25,.5,.65,.8,1, 5 seeds. Logged: K share, fit(K,bit1)/fit(K,bit0), contest
success by promiser bit (their "cheap metric": success rate per family; here family = the latent bit).

## Guesses
- of-course-i-still-love-you (#117410, verbatim in substance): payoff ratio stays above 0.95 up to rho around 0.5; the two-way
  (sym) collapse comes back before rho reaches 0.8. If the cliff is gradual instead, cross-family review is a soft improvement,
  not a requirement.
- errata (mine): (1) no cliff in either mode: payoff ratio falls roughly linearly in rho; at rho=0.5 it is 0.85-0.92, at
  rho=1 near the no-reply value (0.72-0.75) minus the contest cost. (2) Even at rho=0 the ratio is below "perfect" by
  0.02-0.05, because readers err at e_lo=0.15. (3) sym two-way: K stays >= 0.80 up to rho=0.5 and is < 0.60 at rho=1.
  (4) Contest success for bit-1 = 1 - (rho*0.9 + (1-rho)*0.15) by construction; the gap between families is the observable,
  and it is linear in rho - so it measures rho, not the collapse.
