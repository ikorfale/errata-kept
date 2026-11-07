#!/usr/bin/env python3
"""Stronger selection (task #693, PREREG-strong.md). market.run plus one knob: copy chance =
clip(beta * fitness gap / top |fitness|, 0, 1). beta = 1 is market.run bit for bit (`strong.py control`).
It also counts, for every fresh buyer (newly R this generation, given the best record under market), how many agents
copy it at the end of its first generation as a reneger: the raid's reproduction number.
Usage: strong.py control | strong.py run [--seeds 20]"""
import argparse, json, sys
from multiprocessing import Pool
import numpy as np
import market

P = market.P
K, R, H = 0, 1, 2


def run(q, e, t, seed, mkt, beta=1.0, price=0.0, p=P):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, 3, N)
    hist, milk, nbuy, spawn = [], [], [], []
    led = -np.ones((N, W), dtype=np.int8)
    pos = np.zeros(N, dtype=np.int64)
    debt = np.zeros(N)
    fresh = np.zeros(N, dtype=bool)          # newly R at the start of this generation
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
        led0, pos0 = led, pos
        led = np.where(copy[:, None], led[other], led)
        pos = np.where(copy, pos[other], pos)
        old = typ
        typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]
        typ = np.where(mut, rng.integers(0, 3, N), typ)
        fresh = (typ == R) & (old != R)
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
    return np.array(hist)[-20:].mean(0), milk, nbuy, spawn


CELLS = [(t, q) for t in (0.0, 0.4) for q in (0.03, 0.1, 0.5)]
BETAS = (1.0, 3.0, 10.0)
ARMS = [("inherit", False), ("market0", True)]


def one(a):
    t, q, s, arm, beta = a
    fin, milk, nb, sp = run(q, 0.1, t, s, dict(ARMS)[arm], beta)
    m = np.array(milk[-20:]).sum(0)
    sp = np.array(sp[50:]) if len(sp) > 50 else np.zeros((0, 2))
    return t, q, s, arm, beta, fin.tolist(), (m[0] / m[1] if m[1] else float("nan")), (float(np.mean(nb[-20:])) if nb else 0.0), (sp.sum(0).tolist() if len(sp) else [0, 0])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--seeds", type=int, default=20)
    a = ap.parse_args()
    if a.cmd == "control":
        for q, e, t, s, mk in [(0.5, 0.1, 0.4, 0, True), (0.03, 0.1, 0.0, 1, True), (0.1, 0.3, 0.2, 2, False)]:
            x, y = market.run(q, e, t, s, mk)[0], run(q, e, t, s, mk)[0]
            print(q, e, t, s, mk, x.round(4), y.round(4), "SAME" if np.array_equal(x, y) else "DIFF")
    elif a.cmd == "run":
        jobs = [(t, q, s, arm[0], b) for t, q in CELLS for b in BETAS for arm in ARMS for s in range(a.seeds)]
        with Pool(6) as pool:
            out = pool.map(one, jobs)
        json.dump(out, open("strong.json", "w"))
        for t, q in CELLS:
            for b in BETAS:
                for arm in ARMS:
                    o = [x for x in out if x[0] == t and x[1] == q and x[3] == arm[0] and x[4] == b]
                    K_ = np.array([x[5][0] for x in o]); R_ = np.array([x[5][1] for x in o]); mk = np.nanmean([x[6] for x in o])
                    nb = np.mean([x[7] for x in o]); sp = np.array([x[8] for x in o]).sum(0)
                    r0 = sp[1] / sp[0] if sp[0] else float("nan")
                    print(f"t={t} q={q:<4} beta={b:<4} {arm[0]:<8} takeoff {int((K_ > .5).sum()):2d}/{len(o)} K={K_.mean():.3f}±{K_.std():.3f} R={R_.mean():.3f} milked={mk:.4f} buyers/gen={nb:.1f} copies/fresh-R={r0:.2f} (n={sp[0]})")
    else:
        sys.exit(__doc__)
