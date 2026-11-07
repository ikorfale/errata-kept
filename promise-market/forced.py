#!/usr/bin/env python3
"""Forced vs earned promise picks above the trust cliff (task #688, PREREG-forced.md).
Same loop as trust.run, same RNG calls in the same order; only counters added.
Usage: forced.py control | forced.py run [--seeds 20]"""
import argparse, json, sys
from multiprocessing import Pool
import numpy as np
import trust

P = trust.P
K, R, H = 0, 1, 2


def run(q, e, t, seed, p=P):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, 3, N)
    hist, rows = [], []
    for gen in range(p["gens"]):
        led = -np.ones((N, W), dtype=np.int8)
        pos = np.zeros(N, dtype=np.int64)
        fit = np.zeros(N)
        c = dict(forced=0, earned=0, forced_K=0, all=0)
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
            hasH = (typ[cand] == H).any(1)
            pr = pt != H
            c["forced"] += int((pr & ~hasH).sum()); c["earned"] += int((pr & hasH).sum())
            c["forced_K"] += int(((pt == K) & ~hasH).sum()); c["all"] += N
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
        sh = np.bincount(typ, minlength=3) / N
        hist.append(sh)
        rows.append(dict(c, K=sh[0], R=sh[1], H=sh[2]))
    return np.array(hist)[-20:].mean(0), rows


def one(s):
    fin, rows = run(0.5, 0.1, 0.4, s)
    return s, fin.tolist(), rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--seeds", type=int, default=20)
    a = ap.parse_args()
    if a.cmd == "control":
        for q, e, t, s in [(0.5, 0.1, 0.4, 0), (0.5, 0.1, 0.4, 3), (0.03, 0.1, 0.0, 1)]:
            x, y = trust.run(q, e, t, s), run(q, e, t, s)[0]
            print(q, e, t, s, x.round(4), y.round(4), "SAME" if np.array_equal(x, y) else "DIFF")
    elif a.cmd == "run":
        with Pool(6) as pool:
            out = pool.map(one, range(a.seeds))
        json.dump(out, open("forced.json", "w"))
        for s, fin, rows in out:
            print(f"seed {s:2d} final K={fin[0]:.2f} H={fin[2]:.2f} | " + " ".join(
                f"g{g}:F{rows[g]['forced']}/E{rows[g]['earned']}/K{rows[g]['K']:.2f}/H{rows[g]['H']:.2f}" for g in (0, 2, 5, 10)))
    else:
        sys.exit(__doc__)
