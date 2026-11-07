#!/usr/bin/env python3
"""Exploratory, NOT pre-registered (after PREREG-persist verdicts): where is the cliff with a persistent ledger?
t in {0.5, 0.6, 0.8}, q in {0.03, 0.1, 0.5}, e = 0.1, 10 seeds, persist only."""
from multiprocessing import Pool
import numpy as np, persist
def one(a):
    t, q, s = a
    return t, q, s, persist.run(q, 0.1, t, s, True)[0][0]
if __name__ == "__main__":
    jobs = [(t, q, s) for t in (0.5, 0.6, 0.8) for q in (0.03, 0.1, 0.5) for s in range(10)]
    with Pool(6) as p:
        out = p.map(one, jobs)
    for t in (0.5, 0.6, 0.8):
        for q in (0.03, 0.1, 0.5):
            k = [o[3] for o in out if o[0] == t and o[1] == q]
            print(f"t={t} q={q:<4} takeoffs {sum(x > .5 for x in k):2d}/10  mean K {np.mean(k):.2f}")
