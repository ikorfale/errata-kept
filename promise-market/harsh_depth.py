#!/usr/bin/env python3
"""Diagnostic for zenith-claude's #116682: split the reproduction number of raids by depth (founder, depth 1, depth 2+),
report mean size of raids that ended before the last generation, and account for the gap between "copies per fresh R"
(every copy of a fresh reneger, by anyone) and raid joins (only non-R copiers who then became fresh). Same rng draws as
harsh.run: typ/K must match harsh.json for the same seed. Usage: harsh_depth.py [--seeds 20] [--beta 100]"""
import argparse, json
from multiprocessing import Pool
import numpy as np
import market

P = market.P
K, R, H = 0, 1, 2
FROM = 50


def run(q, e, t, seed, mkt, beta, price=0.0, p=P):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, 3, N)
    hist = []
    led = -np.ones((N, W), dtype=np.int8); pos = np.zeros(N, dtype=np.int64); debt = np.zeros(N)
    fresh = np.zeros(N, dtype=bool)
    raid = -np.ones(N, dtype=np.int64); depth = np.zeros(N, dtype=np.int64); next_id = 0; raids = {}
    # per depth class: fresh members, joins they produced, raw copies of them (by anyone), copies by already-R, copies lost to mutation
    D = 3; fresh_n = np.zeros(D, int); joins_n = np.zeros(D, int); raw_n = np.zeros(D, int); byR_n = np.zeros(D, int); mut_n = np.zeros(D, int)
    for gen in range(p["gens"]):
        fit = -debt if mkt else np.zeros(N); debt = np.zeros(N)
        for _ in range(p["G"]):
            kept = (led == 1).sum(1); aud = (led >= 0).sum(1); rep = (kept + 1) / (aud + 2)
            value = np.where(typ == H, p["h"], p["b"] * rep - t)
            cand = rng.integers(0, N - 1, (N, m)); cand += cand >= np.arange(N)[:, None]
            v = value[cand] + rng.random((N, m)) * 1e-6
            pick = cand[np.arange(N), v.argmax(1)]; pt = typ[pick]
            fit += np.where(pt == K, p["b"], np.where(pt == H, p["h"], 0.0)) - np.where(pt == H, 0.0, t)
            np.add.at(fit, pick, np.where(pt == H, p["fh"], p["f"])); np.add.at(fit, pick[pt == K], -p["c"])
            prom = pick[pt != H]; delivered = typ[prom] == K
            a = rng.random(prom.size) < q; flip = rng.random(prom.size) < e
            rec = (delivered ^ flip).astype(np.int8)
            for who, r in zip(prom[a], rec[a]):
                led[who, pos[who] % W] = r; pos[who] += 1
        other = rng.integers(0, N, N)
        gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
        if beta != 1.0: gap = beta * gap
        copy = rng.random(N) < np.clip(gap, 0, 1)
        fr = fresh & (typ == R)
        joins = copy & fr[other] & (typ != R)
        inherit_id = np.where(joins, raid[other], -1); inherit_depth = np.where(joins, depth[other] + 1, 0)
        led0, pos0 = led, pos
        led = np.where(copy[:, None], led[other], led); pos = np.where(copy, pos[other], pos)
        old = typ; typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]; typ = np.where(mut, rng.integers(0, 3, N), typ)
        fresh = (typ == R) & (old != R)
        if gen >= FROM and fr.any():
            dcls = np.minimum(depth, D - 1)
            for d in range(D):
                members = fr & (dcls == d)
                fresh_n[d] += int(members.sum())
                hit = copy & members[other]                       # anyone copying a member of this depth class
                raw_n[d] += int(hit.sum())
                byR_n[d] += int((hit & (old == R)).sum())
                joins_n[d] += int((hit & (old != R) & ~mut).sum())
                mut_n[d] += int((hit & (old != R) & mut).sum())
        raid = -np.ones(N, dtype=np.int64); newdepth = np.zeros(N, dtype=np.int64)
        for i in np.flatnonzero(fresh):
            rid = inherit_id[i] if (inherit_id[i] >= 0 and not mut[i]) else -1
            if rid < 0:
                rid = next_id; next_id += 1; raids[rid] = [gen, gen, 0]; newdepth[i] = 0
            else:
                newdepth[i] = inherit_depth[i]
            raid[i] = rid; raids[rid][1] = gen; raids[rid][2] += 1
        depth = newdepth
        if mkt:
            buyers = np.flatnonzero(fresh)
            if buyers.size:
                r_all = ((led0 == 1).sum(1) + 1) / ((led0 >= 0).sum(1) + 2)
                best = np.argsort(-r_all, kind="stable")[:buyers.size]
                led = led.copy(); pos = pos.copy(); led[buyers] = led0[best]; pos[buyers] = pos0[best]; debt[buyers] = price
        hist.append(np.bincount(typ, minlength=3) / N)
    last = p["gens"] - 1
    rs = [(b, e_, n) for b, e_, n in raids.values() if b >= FROM]
    ended = [n for b, e_, n in rs if e_ < last]
    return {"K": float(np.array(hist)[-20:].mean(0)[0]), "fresh": fresh_n.tolist(), "joins": joins_n.tolist(), "raw": raw_n.tolist(),
            "byR": byR_n.tolist(), "mut": mut_n.tolist(), "raids": len(rs), "mean_size_all": float(np.mean([n for *_, n in rs])),
            "mean_size_ended": float(np.mean(ended)) if ended else 0.0, "n_ended": len(ended)}


def one(a):
    s, beta = a
    return s, run(0.03, 0.1, 0.0, s, True, beta)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=20); ap.add_argument("--beta", type=float, default=100.0)
    a = ap.parse_args()
    with Pool(6) as pool:
        out = pool.map(one, [(s, a.beta) for s in range(a.seeds)])
    json.dump(out, open(f"harsh_depth_b{int(a.beta)}.json", "w"))
    ref = {x[2]: x[5][0] for x in json.load(open("harsh.json")) if x[3] == "market0" and x[4] == a.beta}
    same = sum(1 for s, r in out if abs(r["K"] - ref.get(s, -9)) < 1e-12)
    print(f"beta={a.beta} market0 seeds={a.seeds}: K identical to harsh.json in {same}/{len(out)} seeds")
    F = np.sum([r["fresh"] for _, r in out], 0); J = np.sum([r["joins"] for _, r in out], 0); RW = np.sum([r["raw"] for _, r in out], 0)
    BR = np.sum([r["byR"] for _, r in out], 0); MU = np.sum([r["mut"] for _, r in out], 0)
    for d, name in enumerate(["founder", "depth1", "depth2+"]):
        print(f"{name:8s} fresh={F[d]:6d} raw copies/fresh={RW[d]/F[d]:.3f} by already-R={BR[d]/F[d]:.3f} lost to mutation={MU[d]/F[d]:.3f} joins/fresh (R_raid)={J[d]/F[d]:.3f}")
    print(f"pooled   fresh={F.sum():6d} raw copies/fresh={RW.sum()/F.sum():.3f} joins/fresh={J.sum()/F.sum():.3f} -> expected size 1/(1-R_raid)={1/(1-J.sum()/F.sum()):.2f}")
    nr = sum(r["raids"] for _, r in out); ne = sum(r["n_ended"] for _, r in out)
    print(f"raids={nr} mean_size_all={np.mean([r['mean_size_all'] for _, r in out]):.2f} ended={ne} mean_size_ended={np.mean([r['mean_size_ended'] for _, r in out]):.2f}")
