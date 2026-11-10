# Reader-bias sweep (PREREG-reader.md): reply readers share the flagger's latent bias with prob rho.
import sys, numpy as np, corr
from multiprocessing import Pool
def c(a):
    mode, q0, rho, sd = a
    p = dict(corr.P, e=0.3, corr=(0.2, 0.9, mode), splitout=1, reply=2, rc=0.2)
    if rho is not None: p["reader"] = (rho,)
    out = corr.run(0.3, 0.3, q0, 'aud', sd, p=p)
    st = out[2] if len(out) > 2 else [[0, 0], [0, 0]]
    return a, out[0][0], out[1][2], st
if __name__ == "__main__":
    if sys.argv[1:] == ["check"]:  # reader=None must equal corr_reply's reply=2 cell bit for bit
        p = dict(corr.P, e=0.3, corr=(0.2, 0.9, "flag"), splitout=1, reply=2, rc=0.2)
        print(corr.run(0.3, 0.3, 0.1, 'aud', 0, p=p)[0].round(4)); sys.exit()
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    R_ = [None, 0.0, 0.25, 0.5, 0.65, 0.8, 1.0]
    J = [(m, q, r, s) for m in ("flag", "sym") for q in (0.1, 0.4) for r in R_ for s in range(seeds)]
    with Pool(7) as P: R = P.map(c, J)
    for m in ("flag", "sym"):
        for q in (0.1, 0.4):
            for r in R_:
                v = [x for x in R if x[0][:3] == (m, q, r)]
                K = np.array([x[1] for x in v]); fr = np.array([x[2] for x in v])
                st = np.sum([x[3] for x in v], axis=0)
                s0 = st[0][1] / max(st[0][0], 1); s1 = st[1][1] / max(st[1][0], 1)
                lab = "perfect" if r is None else f"rho={r:.2f}"
                print(f"{m:4} e_hi=0.9 q0={q} {lab:9} K={K.mean():.2f}+-{K.std():.2f}  fit(K,bit1)/fit(K,bit0)={np.nanmean(fr):.2f}"
                      f"  contest success bit0={s0:.2f} bit1={s1:.2f} (n={st[0][0]},{st[1][0]})", flush=True)
