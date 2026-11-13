# Reproduce of-course-i-still-love-you #120765: corr_reader with e_hi in {0.9,0.5,0.3}, R_=[None,0,0.5], 5 seeds.
import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np, corr_elo as corr
from multiprocessing import Pool
def c(a):
    mode, q0, eh, rho, sd = a
    p = dict(corr.P, e=0.3, corr=(0.2, eh, mode), splitout=1, reply=2, rc=0.2, e_lo=0.15)
    if rho is not None: p["reader"] = (rho,)
    out = corr.run(0.3, 0.3, q0, 'aud', sd, p=p)
    st = out[2] if len(out) > 2 else [[0, 0], [0, 0]]
    return a, out[0][0], out[1][2], st
if __name__ == "__main__":
    R_ = [None, 0.0, 0.5]; E = (0.9, 0.5, 0.3)
    J = [(m, q, eh, r, s) for m in ("flag", "sym") for q in (0.1, 0.4) for eh in E for r in R_ for s in range(5)]
    with Pool(7) as P: R = P.map(c, J)
    for m in ("flag", "sym"):
      for q in (0.1, 0.4):
        for eh in E:
          for r in R_:
            v = [x for x in R if x[0][:4] == (m, q, eh, r)]
            K = np.array([x[1] for x in v]); fr = np.array([x[2] for x in v]); st = np.sum([x[3] for x in v], axis=0)
            s0 = st[0][1]/max(st[0][0],1); s1 = st[1][1]/max(st[1][0],1)
            lab = "perfect" if r is None else f"rho={r:.2f}"
            print(f"{m:4} e_hi={eh} q0={q} {lab:9} K={K.mean():.2f}+-{K.std():.2f} ratio={np.nanmean(fr):.3f} cs0={s0:.2f} cs1={s1:.2f} (n={st[0][0]},{st[1][0]})", flush=True)
