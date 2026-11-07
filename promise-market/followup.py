"""Fable review follow-ups: (1) a0 ~ 0 removes the record-length channel vs the lazy evader;
(2) dens with pseudo-counts dk=5 (smoothed density) vs the mimic at q0=0.05. 5 seeds."""
import numpy as np, evade
from multiprocessing import Pool
def f(a):
    name, r, kx, q0, ch, extra = a
    p = dict(evade.P, **extra)
    s = np.array([evade.run(r, kx, q0, ch, sd, p) for sd in range(5)])
    return name, r, s.mean(0), s.std(0)[0]
if __name__ == "__main__":
    jobs = [("lazy rep a0=1e-9", r, 0.1, 0.0, "rep", {"a0": 1e-9}) for r in (0.15, 0.3, 0.5, 0.8)]
    jobs += [("mimic q0=.05 dens dk=5", r, r, 0.05, "dens", {"dk": 5}) for r in (0.15, 0.3, 0.5, 0.8)]
    with Pool(8) as pl:
        for n, r, m, sd in pl.map(f, jobs):
            print(f"{n:24} r={r:.2f}: K={m[0]:.2f}±{sd:.2f} X={m[3]:.2f} R={m[1]:.2f} H={m[2]:.2f}")
