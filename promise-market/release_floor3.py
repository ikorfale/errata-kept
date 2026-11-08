"""PREREG-release2.md amendment A1 (08.11): reneger floor c_min against a releasing-reneger fee multiplier m_rel.
Part A: flat c in .1..9 x m_rel in {1,2,3,5,10}, q=.1, a=1, uniform t_h, d_self=.6, 20 seeds (m_rel=1 reproduces release_floor.py's cell).
Part B (side probe, zenith #116863): flat c=.25, m_rel=1, q in {.01,.005,.002,.001,0}, 20 seeds: where does the ledger break?
Usage: python3 release_floor3.py > release_floor3.log"""
import json, numpy as np
from multiprocessing import Pool
from release import run
def one(a):
    s, c, q, m = a
    hh, harm, tr = run(q, 0.1, 0.0, s, rule=("flat", c), h=0.3, dist="uniform", release=True, accrual=1, d_self=0.6, m_rel=m)
    return {"seed": s, "c": c, "q": q, "m": m, "K": float(hh[0]), "R_rel": float(hh[3]), "R_break": float(hh[1]), "harm_frac": float(harm), "tR": float(tr)}
if __name__ == "__main__":
    CS = [round(0.1 * i, 1) for i in range(1, 10)]; MS = (1, 2, 3, 5, 10); QS = (0.01, 0.005, 0.002, 0.001, 0.0)
    jobsA = [(s, c, 0.1, m) for m in MS for c in CS for s in range(20)]
    jobsB = [(s, 0.25, q, 1) for q in QS for s in range(20)]
    print(len(jobsA), "runs part A,", len(jobsB), "runs part B", flush=True)
    with Pool(4) as pool: outA = pool.map(one, jobsA, chunksize=4); outB = pool.map(one, jobsB, chunksize=4)
    json.dump({"A": outA, "B": outB}, open("release_floor3.json", "w"))
    print("=== part A: c_min by m_rel (q=.1)")
    for m in MS:
        cmin = None
        for c in CS:
            o = [x for x in outA if x["c"] == c and x["m"] == m]; Ks = np.array([x["K"] for x in o]); rr = np.mean([x["R_rel"] for x in o])
            print(f"m={m} flat {c:.1f}: K={Ks.mean():.3f}±{Ks.std():.3f} min={Ks.min():.3f} R_rel={rr:.3f} R_break={np.mean([x['R_break'] for x in o]):.3f} tR={np.nanmean([x['tR'] for x in o]):.2f}", flush=True)
            if cmin is None and Ks.mean() > 0.5 and rr < 0.5: cmin = c
        print(f"m={m}: c_min = {cmin}  (smallest c with mean K > .5 and R_rel < .5; floor lies in ({round(cmin-0.1,1) if cmin else 'n/a'}, {cmin}]; None = no c up to .9 holds)", flush=True)
    print("=== part B: flat c=.25, m_rel=1, falling q")
    for q in QS:
        o = [x for x in outB if x["q"] == q]; Ks = np.array([x["K"] for x in o])
        print(f"q={q}: K={Ks.mean():.3f}±{Ks.std():.3f} min={Ks.min():.3f} R_rel={np.mean([x['R_rel'] for x in o]):.3f} R_break={np.mean([x['R_break'] for x in o]):.3f} tR={np.nanmean([x['tR'] for x in o]):.2f}", flush=True)
    print("=== end")
