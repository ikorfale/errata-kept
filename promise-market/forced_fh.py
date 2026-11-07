#!/usr/bin/env python3
"""Exploratory, NOT pre-registered (after PREREG-forced verdicts): above the cliff K and H earn the same fee per pick
(f - c = fh = 1). Does the split move when the safe fee fh is 0.9 or 1.1? t = 0.4, q = 0.5, e = 0.1, 20 seeds."""
from multiprocessing import Pool
import numpy as np, forced
def one(a):
    fh, s = a
    fin, rows = forced.run(0.5, 0.1, 0.4, s, dict(forced.P, fh=fh))
    return fh, s, fin[0]
if __name__ == "__main__":
    jobs = [(fh, s) for fh in (0.8, 0.9, 1.0, 1.1) for s in range(20)]
    with Pool(6) as p:
        out = p.map(one, jobs)
    for fh in (0.8, 0.9, 1.0, 1.1):
        k = [o[2] for o in out if o[0] == fh]
        print(f"fh={fh}: takeoffs {sum(x > .5 for x in k)}/20, mean K {np.mean(k):.2f}")
