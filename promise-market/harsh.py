#!/usr/bin/env python3
"""Harsher imitation and raid chains (task #694, PREREG-harsh.md). strong.run plus raid ids, with the same rng draws:
every fresh reneger gets a raid id; a non-R agent that copies a fresh raid member joins that raid and is fresh next
generation; an agent that turns R by mutation or by copying a stale reneger starts a new raid. Raid length = consecutive
generations with at least one fresh member; size = total fresh membership. Raids counted from generation 50.
Usage: harsh.py control | harsh.py run [--seeds 20]"""
import argparse, json, sys
from multiprocessing import Pool
import numpy as np
import market, strong

P = market.P
K, R, H = 0, 1, 2
FROM = 50


def run(q, e, t, seed, mkt, beta=1.0, price=0.0, p=P):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, 3, N)
    hist, milk, nbuy, spawn = [], [], [], []
    led = -np.ones((N, W), dtype=np.int8)
    pos = np.zeros(N, dtype=np.int64)
    debt = np.zeros(N)
    fresh = np.zeros(N, dtype=bool)
    raid = -np.ones(N, dtype=np.int64); next_id = 0; raids = {}
    for gen in range(p["gens"]):
        fit = -debt if mkt else np.zeros(N)
        debt = np.zeros(N)
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
        if beta != 1.0:
            gap = beta * gap
        copy = rng.random(N) < np.clip(gap, 0, 1)
        fr = fresh & (typ == R)
        if fr.any():
            spawn.append((int(fr.sum()), int((copy & fr[other]).sum())))
        joins = copy & fr[other] & (typ != R)                 # non-R agents copying a fresh raid member
        inherit_id = np.where(joins, raid[other], -1)
        led0, pos0 = led, pos
        led = np.where(copy[:, None], led[other], led)
        pos = np.where(copy, pos[other], pos)
        old = typ
        typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]
        typ = np.where(mut, rng.integers(0, 3, N), typ)
        fresh = (typ == R) & (old != R)
        raid = -np.ones(N, dtype=np.int64)
        for i in np.flatnonzero(fresh):
            rid = inherit_id[i] if (inherit_id[i] >= 0 and not mut[i]) else -1
            if rid < 0:
                rid = next_id; next_id += 1
                raids[rid] = [gen, gen, 0]
            raid[i] = rid; raids[rid][1] = gen; raids[rid][2] += 1
        if mkt:
            buyers = np.flatnonzero(fresh)
            if buyers.size:
                r_all = ((led0 == 1).sum(1) + 1) / ((led0 >= 0).sum(1) + 2)
                best = np.argsort(-r_all, kind="stable")[:buyers.size]
                led = led.copy(); pos = pos.copy()
                led[buyers] = led0[best]; pos[buyers] = pos0[best]
                debt[buyers] = price
            nbuy.append(int(buyers.size))
        hist.append(np.bincount(typ, minlength=3) / N)
        milk.append((mk, pp))
    last = p["gens"] - 1
    rs = [(b, e_, n) for b, e_, n in raids.values() if b >= FROM]
    lens = np.array([e_ - b + 1 for b, e_, n in rs]) if rs else np.zeros(0, int)
    stats = {"raids": len(rs), "max_len": int(lens.max()) if len(lens) else 0, "ge5": int((lens >= 5).sum()), "ge20": int((lens >= 20).sum()),
             "alive_end": int(sum(1 for b, e_, n in rs if e_ == last)), "mean_size": float(np.mean([n for b, e_, n in rs])) if rs else 0.0,
             "mean_len": float(lens.mean()) if len(lens) else 0.0}
    return np.array(hist)[-20:].mean(0), milk, nbuy, spawn, stats


BETAS = (10.0, 30.0, 100.0)
ARMS = [("inherit", False), ("market0", True)]
CELL = (0.0, 0.03)


def one(a):
    t, q, s, arm, beta = a
    fin, milk, nb, sp, st = run(q, 0.1, t, s, dict(ARMS)[arm], beta)
    sp = np.array(sp[FROM:]) if len(sp) > FROM else np.zeros((0, 2))
    return t, q, s, arm, beta, fin.tolist(), (float(np.mean(nb[-20:])) if nb else 0.0), (sp.sum(0).tolist() if len(sp) else [0, 0]), st


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--seeds", type=int, default=20)
    a = ap.parse_args()
    if a.cmd == "control":
        for s, mk, b in [(0, True, 1.0), (1, False, 1.0), (2, True, 10.0)]:
            x, y = strong.run(0.03, 0.1, 0.0, s, mk, b)[0], run(0.03, 0.1, 0.0, s, mk, b)[0]
            print("seed", s, "market" if mk else "inherit", "beta", b, x.round(4), y.round(4), "SAME" if np.array_equal(x, y) else "DIFF")
    elif a.cmd == "run":
        t, q = CELL
        jobs = [(t, q, s, arm[0], b) for b in BETAS for arm in ARMS for s in range(a.seeds)]
        with Pool(6) as pool:
            out = pool.map(one, jobs)
        json.dump(out, open("harsh.json", "w"))
        for b in BETAS:
            for arm in ARMS:
                o = [x for x in out if x[3] == arm[0] and x[4] == b]
                K_ = np.array([x[5][0] for x in o]); R_ = np.array([x[5][1] for x in o]); nb = np.mean([x[6] for x in o]); sp = np.array([x[7] for x in o]).sum(0)
                r0 = sp[1] / sp[0] if sp[0] else float("nan")
                st = [x[8] for x in o]
                print(f"t={t} q={q} beta={b:<5} {arm[0]:<8} takeoff {int((K_ > .5).sum()):2d}/{len(o)} K={K_.mean():.3f}±{K_.std():.3f} min={K_.min():.3f} R={R_.mean():.3f} buyers/gen={nb:.1f} copies/fresh-R={r0:.2f} (n={sp[0]}) "
                      f"raids={sum(s['raids'] for s in st)} mean_len={np.mean([s['mean_len'] for s in st]):.2f} max_len={max(s['max_len'] for s in st)} ge5={sum(s['ge5'] for s in st)} ge20={sum(s['ge20'] for s in st)} alive_end={sum(s['alive_end'] for s in st)} mean_size={np.mean([s['mean_size'] for s in st]):.2f}")
    else:
        sys.exit(__doc__)
