#!/usr/bin/env python3
"""Persistent ledger (PREREG-persist.md). Same loop as trust.run; one change: with persist=True the ledger and its
write position are NOT reset at the start of each generation. A record belongs to the agent, not to its strategy,
so an agent that copies a new strategy keeps its old record (a former keeper turned reneger carries a good record).
persist=False must reproduce trust.run bit for bit (`persist.py control`).
Also counts, per generation, picks of R agents whose rep > 0.6 ("milked" picks) and all promise picks.
Usage: persist.py control | persist.py run [--seeds 20]"""
import argparse, json, sys
from multiprocessing import Pool
import numpy as np
import trust

P = trust.P
K, R, H = 0, 1, 2


def run(q, e, t, seed, persist, p=P):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, 3, N)
    hist, milk = [], []
    led = -np.ones((N, W), dtype=np.int8)
    pos = np.zeros(N, dtype=np.int64)
    for gen in range(p["gens"]):
        if not persist:
            led = -np.ones((N, W), dtype=np.int8)
            pos = np.zeros(N, dtype=np.int64)
        fit = np.zeros(N)
        mk = pp = 0
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
            mk += int(((pt == R) & (rep[pick] > 0.6)).sum()); pp += int((pt != H).sum())
            fit += np.where(pt == K, p["b"], np.where(pt == H, p["h"], 0.0)) - np.where(pt == H, 0.0, t)
            np.add.at(fit, pick, np.where(pt == H, p["fh"], p["f"]))
            np.add.at(fit, pick[pt == K], -p["c"])
            prom = pick[pt != H]
            delivered = typ[prom] == K
            a = rng.random(prom.size) < q
            flip = rng.random(prom.size) < e
            rec = (delivered ^ flip).astype(np.int8)
            for who, r in zip(prom[a], rec[a]):
                led[who, pos[who] % W] = r
                pos[who] += 1
        other = rng.integers(0, N, N)
        gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
        copy = rng.random(N) < np.clip(gap, 0, 1)
        typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]
        typ = np.where(mut, rng.integers(0, 3, N), typ)
        hist.append(np.bincount(typ, minlength=3) / N)
        milk.append((mk, pp))
    h = np.array(hist)
    return h[-20:].mean(0), milk


CELLS = [(t, q) for t in (0.0, 0.4) for q in (0.03, 0.1, 0.5)]


def one(a):
    t, q, s, ps = a
    fin, milk = run(q, 0.1, t, s, ps)
    m = np.array(milk[-20:]).sum(0)
    return t, q, s, ps, fin.tolist(), (m[0] / m[1] if m[1] else float("nan"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--seeds", type=int, default=20)
    a = ap.parse_args()
    if a.cmd == "control":
        for q, e, t, s in [(0.5, 0.1, 0.4, 0), (0.03, 0.1, 0.0, 1), (0.1, 0.3, 0.2, 2)]:
            x, y = trust.run(q, e, t, s), run(q, e, t, s, False)[0]
            print(q, e, t, s, x.round(4), y.round(4), "SAME" if np.array_equal(x, y) else "DIFF")
    elif a.cmd == "run":
        jobs = [(t, q, s, ps) for t, q in CELLS for ps in (False, True) for s in range(a.seeds)]
        with Pool(6) as pool:
            out = pool.map(one, jobs)
        json.dump(out, open("persist.json", "w"))
        for t, q in CELLS:
            for ps in (False, True):
                o = [x for x in out if x[0] == t and x[1] == q and x[3] == ps]
                K_ = np.array([x[4][0] for x in o]); R_ = np.array([x[4][1] for x in o]); mk = np.nanmean([x[5] for x in o])
                print(f"t={t} q={q:<4} persist={int(ps)} takeoff {int((K_ > .5).sum()):2d}/{len(o)} K={K_.mean():.2f}±{K_.std():.2f} R={R_.mean():.2f} milked/promise picks(last20)={mk:.3f}")
    else:
        sys.exit(__doc__)
