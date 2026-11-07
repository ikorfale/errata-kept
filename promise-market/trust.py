#!/usr/bin/env python3
"""Promise market with a price on trust (task #684, PREREG-trust.md). sim.py stays frozen.

Only change from sim.py: a chooser who picks a promiser (K or R) pays t, whether or not the
promise is kept. Choosers know this, so a promiser's value is b*rep - t against h for H.
t=0 must reproduce sim.py exactly (checked by `trust.py control`).
Also records pick concentration: share of all promise picks in a generation that go to the
top 5% most-picked agents (10 of 200), and the H share inside sampled candidate sets.
Usage: trust.py sweep [--seeds 5] | trust.py control | trust.py conc q e t seed
"""
import argparse, json, sys
from multiprocessing import Pool
import numpy as np
import sim

P = sim.P
K, R, H = 0, 1, 2


def run(q, e, t, seed, p=P, trace=False):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, 3, N)
    hist, conc = [], []
    for gen in range(p["gens"]):
        led = -np.ones((N, W), dtype=np.int8)
        pos = np.zeros(N, dtype=np.int64)
        fit = np.zeros(N)
        picks = np.zeros(N)
        for _ in range(p["G"]):
            kept = (led == 1).sum(1)
            aud = (led >= 0).sum(1)
            rep = (kept + 1) / (aud + 2)
            value = np.where(typ == H, p["h"], p["b"] * rep - t)
            cand = rng.integers(0, N - 1, (N, m))
            cand += cand >= np.arange(N)[:, None]
            v = value[cand] + rng.random((N, m)) * 1e-6
            pick = cand[np.arange(N), v.argmax(1)]
            pt = typ[pick]
            fit += np.where(pt == K, p["b"], np.where(pt == H, p["h"], 0.0)) - np.where(pt == H, 0.0, t)
            np.add.at(fit, pick, np.where(pt == H, p["fh"], p["f"]))
            np.add.at(fit, pick[pt == K], -p["c"])
            prom = pick[pt != H]
            np.add.at(picks, prom, 1)
            delivered = typ[prom] == K
            a = rng.random(prom.size) < q
            flip = rng.random(prom.size) < e
            rec = (delivered ^ flip).astype(np.int8)
            for who, r in zip(prom[a], rec[a]):
                led[who, pos[who] % W] = r
                pos[who] += 1
        tot = picks.sum()
        conc.append(np.sort(picks)[-N // 20:].sum() / tot if tot > 0 else np.nan)
        other = rng.integers(0, N, N)
        gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
        copy = rng.random(N) < np.clip(gap, 0, 1)
        typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]
        typ = np.where(mut, rng.integers(0, 3, N), typ)
        hist.append(np.bincount(typ, minlength=3) / N)
    h = np.array(hist)
    if trace:
        return h, np.array(conc)
    return h[-20:].mean(0)


def cell(args):
    q, e, t, s = args
    return (q, e, t, s, run(q, e, t, s).tolist())


QS = [0, 0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
TS = [0, 0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd"); ap.add_argument("args", nargs="*")
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "control":
        for q, e, s in [(0.02, 0.1, 0), (0.1, 0.3, 1), (0.03, 0.2, 2)]:
            x, y = sim.run(q, e, s), run(q, e, 0.0, s)
            print(q, e, s, x.round(4), y.round(4), "SAME" if np.array_equal(x, y) else "DIFF")
    elif a.cmd == "sweep":
        e = 0.1
        jobs = [(q, e, t, s) for t in TS for q in QS for s in range(a.seeds)]
        with Pool(6) as pool:
            out = pool.map(cell, jobs)
        rows = []
        for t in TS:
            for q in QS:
                sh = np.array([o[4] for o in out if o[2] == t and o[0] == q])
                mu, sd = sh.mean(0), sh.std(0)
                rows.append(dict(t=t, q=q, e=e, K=mu[0], R=mu[1], H=mu[2], K_sd=sd[0]))
                print(f"t={t:.2f} q={q:.2f} K={mu[0]:.2f}±{sd[0]:.2f} R={mu[1]:.2f} H={mu[2]:.2f}", flush=True)
        json.dump(dict(params=P, e=e, rows=rows), open("trust.json", "w"), indent=1)
    elif a.cmd == "conc":
        q, e, t, s = float(a.args[0]), float(a.args[1]), float(a.args[2]), int(a.args[3])
        h, c = run(q, e, t, s, trace=True)
        for g in [0, 5, 10, 20, 30, 50, 80, 149]:
            print(f"gen {g:3d} K={h[g][0]:.2f} R={h[g][1]:.2f} H={h[g][2]:.2f} top5%picks={c[g]:.2f}")
    else:
        sys.exit(__doc__)
