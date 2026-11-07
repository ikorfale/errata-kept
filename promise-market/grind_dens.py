# Exploratory follow-up to PREREG-grind (chosen after the run, not pre-registered): chooser 'audd' discounts missing audits.
import numpy as np, evade
from multiprocessing import Pool
S = 20
def c(a):
    ch, q0, n = a; p = dict(evade.P, e=0.3, grind=n, ginf=1.0)
    s = np.array([evade.run(0.3, 0.3, q0, ch, sd, p=p) for sd in range(S)])
    return ch, q0, n, s[:, 0].mean(), s[:, 0].std(), int((s[:, 0] < 0.3).sum())
if __name__ == "__main__":
    J = [(ch, q0, n) for ch in ("audd",) for q0 in (0.05, 0.1, 0.2, 0.4) for n in (1, 2, 3)]
    with Pool(7) as pool:
        for ch, q0, n, k, sd, col in pool.map(c, J):
            print(f"{ch} e=0.3 q0={q0:.2f} N={n}  K={k:.3f}+-{sd:.2f} collapse={col}/{S}", flush=True)
