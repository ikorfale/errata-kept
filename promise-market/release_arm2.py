"""PREREG-release2.md step 2 in the cells that qualified under amendment A1: d_self=.3 with m_rel in {5,10} (release_floor3:
c_min in (.2,.3] at both). Same rules as PREREG-release.md: flat {0,.25,.5,.75,1}, ramp {.5,.75,1}; four t_h shapes; accrual
on/off; q=.1; 20 seeds. One log per m in release.py's line format, so release_score.py reads it unchanged.
Usage: python3 release_arm2.py M > release_arm2_mM.log"""
import json, sys, numpy as np
from multiprocessing import Pool
from release import run, RULES, DISTS
M = float(sys.argv[1])
def one(a):
    s, rule, dist, acc = a
    hh, harm, tr = run(0.1, 0.1, 0.0, s, rule=rule, h=0.3, dist=dist, release=True, accrual=acc, d_self=0.3, m_rel=M)
    return {"seed": s, "rule": list(rule), "dist": dist, "accrual": acc, "d_self": 0.3, "m": M, "K": hh[0], "R_break": hh[1], "H": hh[2], "R_rel": hh[3], "harm_frac": harm, "tR": tr}
if __name__ == "__main__":
    jobs = [(s, rule, dist, acc) for dist in DISTS for acc in (1, 0) for rule in RULES for s in range(20)]
    print(f"{len(jobs)} runs, m_rel={M}, d_self=.3", flush=True)
    with Pool(4) as pool: out = pool.map(one, jobs, chunksize=8)
    json.dump(out, open(f"release_arm2_m{int(M)}.json", "w"))
    for dist in DISTS:
        for acc in (1, 0):
            for rule in RULES:
                o = [x for x in out if x["dist"] == dist and x["accrual"] == acc and tuple(x["rule"]) == rule]
                Ks = np.array([x["K"] for x in o]); hf = np.array([x["harm_frac"] for x in o]); tr = np.array([x["tR"] for x in o])
                print(f"rel q=0.1 {dist:7s} a={acc} ds=0.3 {rule[0]} {rule[1]:.2f}  K={Ks.mean():.3f}±{Ks.std():.3f} min={Ks.min():.3f} "
                      f"R_break={np.mean([x['R_break'] for x in o]):.3f} R_rel={np.mean([x['R_rel'] for x in o]):.3f} tR={np.nanmean(tr):.2f} "
                      f"harm_frac={np.nanmean(hf):.3f} K-harm={(Ks - hf).mean():.3f}", flush=True)
    print("=== end")
