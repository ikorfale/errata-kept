# PREREG-grind.md sweep: X grinds the audit seed (N candidates, influence prob g); matched foresight cells at l = 1 - q0**(N-1).
import numpy as np, evade, json, sys
from multiprocessing import Pool
S = 20
def c(a):
    e, q0, n, g, lk = a; p = dict(evade.P, e=e, grind=n, ginf=g, leak=lk)
    s = np.array([evade.run(0.3, 0.3, q0, 'aud', sd, p=p) for sd in range(S)])
    return dict(e=e, q0=q0, N=n, g=g, leak=lk, K=s[:, 0].mean(), Ksd=s[:, 0].std(), R=s[:, 1].mean(), H=s[:, 2].mean(),
                X=s[:, 3].mean(), collapse=int((s[:, 0] < 0.3).sum()))
if __name__ == "__main__":
    J = [(0.3, 0.1, 1, 1.0, 0.0)]  # control: must equal the l = 0 leak model
    for q0 in (0.05, 0.1, 0.2, 0.4):
        for n, g in ((2, 1.0), (3, 1.0), (2, 0.5)):
            J.append((0.3, q0, n, g, 0.0))
        for n in (2, 3):
            J.append((0.3, q0, 1, 1.0, round(1 - q0 ** (n - 1), 4)))  # matched foresight
    J += [(0.0, 0.1, 2, 1.0, 0.0), (0.0, 0.1, 3, 1.0, 0.0)]
    with Pool(7) as pool:
        out = pool.map(c, J)
    for x in out:
        print(f"e={x['e']} q0={x['q0']:.2f} N={x['N']} g={x['g']:.1f} leak={x['leak']:.3f}  K={x['K']:.3f}+-{x['Ksd']:.2f} "
              f"R={x['R']:.2f} H={x['H']:.2f} X={x['X']:.2f} collapse={x['collapse']}/{S}", flush=True)
    json.dump(out, open('grind.json', 'w'), indent=1)
