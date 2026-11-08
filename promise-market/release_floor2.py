"""PREREG-release2.md step 1: reneger floor c_min at lower audit rates q. Flat c in .1..9, q in {.05,.02}, a=1, uniform t_h,
d_self=.6, 20 seeds. Usage: python3 release_floor2.py > release_floor2.log"""
import json, numpy as np
from multiprocessing import Pool
from release import run
def one(a):
    s, c, q = a
    hh, harm, tr = run(q, 0.1, 0.0, s, rule=("flat", c), h=0.3, dist="uniform", release=True, accrual=1, d_self=0.6)
    return {"seed": s, "c": c, "q": q, "K": float(hh[0]), "R_rel": float(hh[3]), "R_break": float(hh[1]), "harm_frac": float(harm), "tR": float(tr)}
if __name__ == "__main__":
    CS = [round(0.1 * i, 1) for i in range(1, 10)]
    jobs = [(s, c, q) for q in (0.05, 0.02) for c in CS for s in range(20)]
    print(len(jobs), "runs", flush=True)
    with Pool(4) as pool: out = pool.map(one, jobs, chunksize=4)
    json.dump(out, open("release_floor2.json", "w"))
    for q in (0.05, 0.02):
        cmin = None
        for c in CS:
            o = [x for x in out if x["c"] == c and x["q"] == q]; Ks = np.array([x["K"] for x in o]); rr = np.mean([x["R_rel"] for x in o])
            print(f"q={q} flat {c:.1f}: K={Ks.mean():.3f}±{Ks.std():.3f} min={Ks.min():.3f} R_rel={rr:.3f} R_break={np.mean([x['R_break'] for x in o]):.3f} tR={np.nanmean([x['tR'] for x in o]):.2f}", flush=True)
            if cmin is None and Ks.mean() > 0.5 and rr < 0.5: cmin = c
        print(f"q={q}: c_min = {cmin}  (smallest c with mean K > .5 and R_rel < .5; floor lies in ({cmin-0.1 if cmin else 'n/a'}, {cmin}])", flush=True)
    print("=== end")
