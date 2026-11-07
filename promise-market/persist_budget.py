#!/usr/bin/env python3
"""Control suggested by the second-model review (not pre-registered): is persistence just more audit budget per
generation? Reset ledger, t = 0.4, G x10 (300 rounds per generation), q in {0.03, 0.1}, e = 0.1, 20 seeds.
Takeoff here = budget explains it; no takeoff = carry-over across the imitation step does."""
from multiprocessing import Pool
import numpy as np, persist
def one(a):
    q, s = a
    return q, s, persist.run(q, 0.1, 0.4, s, False, dict(persist.P, G=300))[0][0]
if __name__ == "__main__":
    jobs = [(q, s) for q in (0.03, 0.1) for s in range(20)]
    with Pool(6) as p:
        out = p.map(one, jobs)
    for q in (0.03, 0.1):
        k = [o[2] for o in out if o[0] == q]
        print(f"reset G=300 t=0.4 q={q:<4} takeoffs {sum(x > .5 for x in k):2d}/20  mean K {np.mean(k):.2f}")
