"""Does the rep prior (kept+a0)/(aud+2a0) act as a density penalty against the lazy evader?"""
import numpy as np, evade
from multiprocessing import Pool
def f(a):
    a0, r = a
    p = dict(evade.P, a0=a0)
    s = np.array([evade.run(r, 0.1, 0.0, "rep", sd, p) for sd in range(5)])
    return a0, r, s.mean(0)
if __name__ == "__main__":
    with Pool(6) as pl:
        for a0, r, m in pl.map(f, [(a0, r) for a0 in (0.1, 1, 3) for r in (0.15, 0.3, 0.5)]):
            print(f"lazy X, rep chooser, prior a0={a0} r={r}: K={m[0]:.2f} X={m[3]:.2f} R={m[1]:.2f} H={m[2]:.2f}")
