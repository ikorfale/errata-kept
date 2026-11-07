# PREREG-leak.md sweep: mimic foresees random audits with prob leak; chooser 'aud'.
import numpy as np, evade
from multiprocessing import Pool
def c(a):
    e,q0,lk=a; p=dict(evade.P,e=e,leak=lk)
    s=np.array([evade.run(0.3,0.3,q0,'aud',sd,p=p) for sd in range(5)])
    return e,q0,lk,s.mean(0),s[:,0].std()
if __name__=="__main__":
    jobs=[(0.3,q0,lk) for q0 in (0.05,0.1,0.2,0.4) for lk in (0,.25,.5,.75,.9,1)]+[(0.0,0.1,lk) for lk in (0,.25,.5,.75,.9,1)]
    with Pool(6) as pool:
        for e,q0,lk,m,sd in pool.map(c,jobs):
            print(f"e={e} q0={q0:.2f} leak={lk:.2f}  K={m[0]:.2f}+-{sd:.2f} R={m[1]:.2f} H={m[2]:.2f} X={m[3]:.2f}",flush=True)
