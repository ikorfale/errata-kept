# Follow-ups after the Fable review of 2026-11-07 (not preregistered): e=0.3, 5 seeds each.
import numpy as np, evade
from multiprocessing import Pool
def c(a):
    tag,r,kx,q0,ch,extra=a; p=dict(evade.P,e=0.3,**extra)
    s=np.array([evade.run(r,kx,q0,ch,sd,p=p) for sd in range(5)]); return tag,r,kx,q0,ch,extra,s[:,0].mean(),s[:,0].std()
J=[("reply-audits-only",r,r,q0,"rep",dict(reply=2,rc=0.2)) for r in (0.3,0.5) for q0 in (0.05,0.1,0.2)]
J+=[("kx-decoupled",r,kx,0.2,"rep",{}) for r,kx in ((0.5,0.3),(0.3,0.5),(0.3,0.3),(0.5,0.5))]
J+=[("W200",r,r,0.1,ch,dict(W=200)) for r in (0.3,0.5) for ch in ("rep","aud")]
if __name__=="__main__":
    with Pool(6) as pool:
        for tag,r,kx,q0,ch,extra,m,sd in pool.map(c,J):
            print(f"{tag:18} r={r} kx={kx} q0={q0:.2f} {ch:3} K={m:.2f}+-{sd:.2f}",flush=True)
