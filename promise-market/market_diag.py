#!/usr/bin/env python3
"""Record market (task #692, PREREG-market.md). inherit.run plus one option: with market=True, every agent that is
NEWLY a reneger after the copy+mutation step (was K or H, is now R) does not take the imitated agent's record; it gets
a clone of the best record in the population at that moment (ranked by rep, best first, one record per buyer; the
seller keeps its row). Keepers and honest-abstainers who copy still inherit the imitated agent's row (as in inherit).
The buyer pays `price` out of the next generation's fitness.
market=False must reproduce inherit.run(inherit=True) bit for bit (`market.py control`).
Usage: market.py control | market.py run [--seeds 20]"""
import argparse, json, sys
from multiprocessing import Pool
import numpy as np
import inherit

P = inherit.P
K, R, H = 0, 1, 2


def run(q, e, t, seed, market, price=0.0, p=P):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, 3, N)
    hist, milk, ratio, nbuy = [], [], [], []
    newb = np.zeros(N, bool); D = []
    led = -np.ones((N, W), dtype=np.int8)
    pos = np.zeros(N, dtype=np.int64)
    debt = np.zeros(N)
    for gen in range(p["gens"]):
        fit = -debt if market else np.zeros(N)
        debt = np.zeros(N)
        mk = pp = 0
        picks = np.zeros(N)
        repb = ((led == 1).sum(1) + 1) / ((led >= 0).sum(1) + 2)
        r0 = ((led == 1).sum(1) + 1) / ((led >= 0).sum(1) + 2)
        carr = (typ == R) & (r0 > 0.6)
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
            np.add.at(picks, pick, 1)
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
        isK = typ == K
        if newb.any() and gen >= 50:
            rend = ((led == 1).sum(1) + 1) / ((led >= 0).sum(1) + 2)
            D.append((repb[newb].mean(), rend[newb].mean(), picks[newb].mean(), picks[isK].mean(), fit[newb].mean(), fit[isK].mean(), repb[isK].mean()))
        newb = np.zeros(N, bool)
        ratio.append((fit[carr].mean() / fit[isK].mean()) if carr.any() and isK.any() and fit[isK].mean() > 0 else np.nan)
        ratio[-1] = (ratio[-1], int(carr.sum()))
        other = rng.integers(0, N, N)
        gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
        copy = rng.random(N) < np.clip(gap, 0, 1)
        led0, pos0 = led, pos
        led = np.where(copy[:, None], led[other], led)
        pos = np.where(copy, pos[other], pos)
        old = typ
        typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]
        typ = np.where(mut, rng.integers(0, 3, N), typ)
        if market:
            buyers = np.flatnonzero((typ == R) & (old != R))
            if buyers.size:
                r_all = ((led0 == 1).sum(1) + 1) / ((led0 >= 0).sum(1) + 2)
                best = np.argsort(-r_all, kind="stable")[:buyers.size]
                led = led.copy(); pos = pos.copy()
                led[buyers] = led0[best]; pos[buyers] = pos0[best]
                debt[buyers] = price
                newb[buyers] = True
            nbuy.append(int(buyers.size))
        hist.append(np.bincount(typ, minlength=3) / N)
        milk.append((mk, pp))
    h = np.array(hist)
    return h[-20:].mean(0), milk, ratio, nbuy, D


if __name__ == "__main__":
    import sys
    t, q = float(sys.argv[1]), float(sys.argv[2])
    D = []
    for s in range(10):
        D += run(q, 0.1, t, s, True, 0.0)[4]
    D = np.array(D)
    print(f"t={t} q={q} buyer-gens {len(D)}: buyer rep start {D[:,0].mean():.3f} end {D[:,1].mean():.3f}; keeper rep {D[:,6].mean():.3f}; picks buyer {D[:,2].mean():.1f} vs K {D[:,3].mean():.1f}; fitness buyer {D[:,4].mean():.1f} vs K {D[:,5].mean():.1f} (ratio {D[:,4].mean()/D[:,5].mean():.2f})")

