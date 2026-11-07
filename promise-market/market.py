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
    led = -np.ones((N, W), dtype=np.int8)
    pos = np.zeros(N, dtype=np.int64)
    debt = np.zeros(N)
    for gen in range(p["gens"]):
        fit = -debt if market else np.zeros(N)
        debt = np.zeros(N)
        mk = pp = 0
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
            nbuy.append(int(buyers.size))
        hist.append(np.bincount(typ, minlength=3) / N)
        milk.append((mk, pp))
    h = np.array(hist)
    return h[-20:].mean(0), milk, ratio, nbuy


CELLS = [(t, q) for t in (0.0, 0.4) for q in (0.03, 0.1, 0.5)]
ARMS = [("inherit", False, 0.0), ("market0", True, 0.0), ("market30", True, 30.0)]


def one(a):
    t, q, s, arm = a
    _, mk_, pr = next(x for x in ARMS if x[0] == arm)
    fin, milk, ratio, nb = run(q, 0.1, t, s, mk_, pr)
    m = np.array(milk[-20:]).sum(0)
    rr = [x[0] for x in ratio[50:] if not np.isnan(x[0])]
    return t, q, s, arm, fin.tolist(), (m[0] / m[1] if m[1] else float("nan")), (float(np.mean(rr)) if rr else float("nan")), len(rr), (float(np.mean(nb[-20:])) if nb else 0.0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--seeds", type=int, default=20)
    a = ap.parse_args()
    if a.cmd == "control":
        for q, e, t, s in [(0.5, 0.1, 0.4, 0), (0.03, 0.1, 0.0, 1), (0.1, 0.3, 0.2, 2)]:
            x, y = inherit.run(q, e, t, s, True)[0], run(q, e, t, s, False)[0]
            print(q, e, t, s, x.round(4), y.round(4), "SAME" if np.array_equal(x, y) else "DIFF")
    elif a.cmd == "run":
        jobs = [(t, q, s, arm[0]) for t, q in CELLS for arm in ARMS for s in range(a.seeds)]
        with Pool(6) as pool:
            out = pool.map(one, jobs)
        json.dump(out, open("market.json", "w"))
        for t, q in CELLS:
            for arm in ARMS:
                o = [x for x in out if x[0] == t and x[1] == q and x[3] == arm[0]]
                K_ = np.array([x[4][0] for x in o]); R_ = np.array([x[4][1] for x in o]); mk = np.nanmean([x[5] for x in o])
                rr = np.array([x[6] for x in o]); nb = np.mean([x[8] for x in o])
                print(f"t={t} q={q:<4} {arm[0]:<8} takeoff {int((K_ > .5).sum()):2d}/{len(o)} K={K_.mean():.2f}±{K_.std():.2f} R={R_.mean():.2f} milked/promise(last20)={mk:.3f} carrierR/K={np.nanmean(rr):.2f} buyers/gen={nb:.1f}")
    else:
        sys.exit(__doc__)
