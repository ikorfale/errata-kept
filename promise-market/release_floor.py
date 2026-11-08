"""POST-HOC probe (not in PREREG-release.md): where is the reneger floor c_min, the smallest flat release cost at which
renegers do not take over? Flat c in {.05,.1,.15,.2}, a=1, uniform t_h, d_self=.6, q=.1, 20 seeds. Same run() as release.py."""
import json, numpy as np
from multiprocessing import Pool
from release import run
def one(a):
    s, c = a
    hh, harm, tr = run(0.1, 0.1, 0.0, s, rule=("flat", c), h=0.3, dist="uniform", release=True, accrual=1, d_self=0.6)
    return {"seed": s, "c": c, "K": float(hh[0]), "R_rel": float(hh[3]), "harm_frac": float(harm), "tR": float(tr)}
if __name__ == "__main__":
    jobs = [(s, c) for c in (0.05, 0.10, 0.15, 0.20) for s in range(20)]
    with Pool(4) as pool: out = pool.map(one, jobs, chunksize=4)
    json.dump(out, open("release_floor.json", "w"))
    for c in (0.05, 0.10, 0.15, 0.20):
        o = [x for x in out if x["c"] == c]; Ks = np.array([x["K"] for x in o])
        print(f"flat {c:.2f} a=1 uniform ds=0.6: K={Ks.mean():.3f}±{Ks.std():.3f} min={Ks.min():.3f} R_rel={np.mean([x['R_rel'] for x in o]):.3f} "
              f"tR={np.nanmean([x['tR'] for x in o]):.2f} harm_frac={np.nanmean([x['harm_frac'] for x in o]):.3f}", flush=True)
    print("=== end")
