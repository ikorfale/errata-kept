# Follow-up (not in prereg): 20 seeds at the tipping cell vs a plain rate cut q0*(1-leak).
import numpy as np, evade
from multiprocessing import Pool
def c(a):
    q0,lk,sd=a; return q0,lk,evade.run(0.3,0.3,q0,'aud',sd,p=dict(evade.P,e=0.3,leak=lk))[0]
if __name__=="__main__":
    cells=[(0.1,0.25),(0.075,0.0),(0.2,0.5),(0.1,0.0),(0.4,0.75)]
    with Pool(6) as pool: r=pool.map(c,[(q,l,s) for q,l in cells for s in range(20)])
    for q,l in cells:
        k=np.array([x[2] for x in r if x[0]==q and x[1]==l]); print(f"q0={q:.3f} leak={l:.2f} eff={q*(1-l):.3f}  K={k.mean():.2f}+-{k.std():.2f}  collapsed(K<.3)={int((k<.3).sum())}/20")
