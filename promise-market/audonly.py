# Follow-up (not in PREREG-flags): score only from random-audit records ('aud') vs all records ('rep'), mimic, e=0.3, no reply.
import numpy as np, evade
from multiprocessing import Pool
def c(a):
    r,q0,ch=a; p=dict(evade.P,e=0.3)
    s=np.array([evade.run(r,r,q0,ch,sd,p=p) for sd in range(5)]); return r,q0,ch,s[:,0].mean(),s[:,0].std()
if __name__=="__main__":
    with Pool(6) as pool:
        for r,q0,ch,m,sd in pool.map(c,[(r,q0,ch) for r in (0.3,0.5) for q0 in (0.05,0.1,0.2) for ch in ("rep","aud")]):
            print(f"e=0.3 r={r} q0={q0:.2f} {ch:3} K={m:.2f}+-{sd:.2f}")
