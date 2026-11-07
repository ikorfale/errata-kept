#!/usr/bin/env python3
"""Exploratory (not pre-registered): why does inheritance lower milking? Per generation 50-149 at t=0, q=0.03,
10 seeds: mean start-of-generation rep and audited entries of K agents and of record-carrying R, and carriers count."""
import numpy as np, persist, inherit
P = inherit.P; K, R = 0, 1
orig = np.random.default_rng
def stats(ih, seeds=10, q=0.03, t=0.0):
    out = []
    for s in range(seeds):
        snaps = []
        # re-run with a hook: copy of inherit.run's loop is avoided by sampling state via monkeypatched np.where? simpler: replicate
        rng = np.random.default_rng(s); p = P; N, m, W = p["N"], p["m"], p["W"]
        typ = rng.integers(0, 3, N); led = -np.ones((N, W), dtype=np.int8); pos = np.zeros(N, dtype=np.int64)
        for gen in range(p["gens"]):
            aud0 = (led >= 0).sum(1); r0 = ((led == 1).sum(1) + 1) / (aud0 + 2); carr = (typ == R) & (r0 > 0.6)
            if gen >= 50: snaps.append((r0[typ == K].mean(), aud0[typ == K].mean(), r0[carr].mean() if carr.any() else np.nan, aud0[carr].mean() if carr.any() else np.nan, carr.sum()))
            fit = np.zeros(N)
            for _ in range(p["G"]):
                kept = (led == 1).sum(1); aud = (led >= 0).sum(1); rep = (kept + 1) / (aud + 2)
                value = np.where(typ == 2, p["h"], p["b"] * rep - t)
                cand = rng.integers(0, N - 1, (N, m)); cand += cand >= np.arange(N)[:, None]
                v = value[cand] + rng.random((N, m)) * 1e-6; pick = cand[np.arange(N), v.argmax(1)]; pt = typ[pick]
                fit += np.where(pt == K, p["b"], np.where(pt == 2, p["h"], 0.0)) - np.where(pt == 2, 0.0, t)
                np.add.at(fit, pick, np.where(pt == 2, p["fh"], p["f"])); np.add.at(fit, pick[pt == K], -p["c"])
                prom = pick[pt != 2]; delivered = typ[prom] == K
                a = rng.random(prom.size) < q; flip = rng.random(prom.size) < 0.1; rec = (delivered ^ flip).astype(np.int8)
                for who, r in zip(prom[a], rec[a]): led[who, pos[who] % W] = r; pos[who] += 1
            other = rng.integers(0, N, N); gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
            copy = rng.random(N) < np.clip(gap, 0, 1)
            if ih: led = np.where(copy[:, None], led[other], led); pos = np.where(copy, pos[other], pos)
            typ = np.where(copy, typ[other], typ); mut = rng.random(N) < p["mu"]; typ = np.where(mut, rng.integers(0, 3, N), typ)
        out.append(np.nanmean(np.array(snaps, dtype=float), 0))
    return np.mean(out, 0)
# note: this loop re-implements inherit.run with the same rng order; not checked against it bit for bit
for ih in (False, True):
    kr, ka, cr, ca, nc = stats(ih)
    print(f"inherit={int(ih)} K: rep {kr:.3f}, audited entries {ka:.1f} | carrier R: rep {cr:.3f}, entries {ca:.1f}, count/gen {nc:.1f}")
