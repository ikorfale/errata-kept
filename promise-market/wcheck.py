# Is the r=0.5 > r=0.3 audit edge (e=0.3, no reply) a window effect? Same cells with W=20 vs W=60.
import numpy as np, evade
from multiprocessing import Pool
def c(a):
    r,W=a; p=dict(evade.P,e=0.3,W=W)
    s=np.array([evade.run(r,r,0.2,"rep",sd,p=p) for sd in range(5)]); return r,W,s[:,0].mean(),s[:,0].std()
if __name__=="__main__":
    with Pool(4) as pool:
        for r,W,m,sd in pool.map(c,[(r,W) for r in (0.3,0.5) for W in (20,60)]): print(f"q0=0.20 e=0.3 r={r} W={W} K={m:.2f}+-{sd:.2f}")
