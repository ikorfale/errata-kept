#!/usr/bin/env python3
"""RELEASED verdict (PREREG-release.md, design revised 08.11 after a Fable review). inherit.run (inherit=True) plus:
a share h of promises is harmful to keep (chooser gets b-d, d = d_mult*b); the keeper learns it at t_h ~ DIST over the promise
window [0,1). A promise may be released at time t: the promiser collects f*t if accrual a=1 (else the full fee f), pays no c,
the chooser gets 0, and an audited release writes weight 1-cost(t) into the ledger (kept = 1, broken = 0); a noisy audit
writes 1-w. rep = (sum of weights + 1)/(audited + 2). cost(t): flat c, or ramp r*t (r<1 = capped). Keepers release a
harmful promise iff cost(t_h) < d_self, else keep it (harm realised). Renegers: R_break (type 1, never releases) and R_rel
(type 3) with a heritable release time t_R in [0,1), copied with the type, mutated by N(0, .05) each generation; a mutation
into R_rel draws t_R uniformly. release=False turns every new draw off: with h=0 it reproduces inherit.run bit for bit
(`release.py control`); with h=.3 it is the "no fix" baseline. m_rel (amendment 08.11, PREREG-release2.md) multiplies
only the releasing reneger's collected fee (type 3); keepers, R_break and the honest-release fee stay at f; m_rel=1 is the old model. Usage: release.py control | run [--seeds 20] [--out f]"""
import argparse, json, sys
from multiprocessing import Pool
import numpy as np
import inherit

P = inherit.P
K, RB, H, RR = 0, 1, 2, 3
DISTS = {"early": ("beta", 1, 3), "uniform": ("beta", 1, 1), "late": ("beta", 3, 1), "last5": ("unif", 0.8, 1.0)}
SD_TR = 0.05


def cost_fn(rule):
    kind, x = rule
    if kind == "flat":
        return lambda t: np.full_like(t, x, dtype=float)
    return lambda t: x * t


def draw_th(rng, dist, n):
    kind, a, b = DISTS[dist]
    return rng.beta(a, b, n) if kind == "beta" else rng.uniform(a, b, n)


def run(q, e, t_price, seed, rule=("flat", 1.0), h=0.0, dist="uniform", release=True, accrual=1, d_self=0.5, d_mult=2.0, p=P, m_rel=1.0):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    ntypes = 4 if release else 3
    cost = cost_fn(rule)
    typ = rng.integers(0, 3, N)
    tR = np.zeros(N)
    hist, tr_hist = [], []
    harm_kept = harm_n = prom_tot = 0
    led = -np.ones((N, W), dtype=np.float64)
    pos = np.zeros(N, dtype=np.int64)
    for gen in range(p["gens"]):
        fit = np.zeros(N)
        for _ in range(p["G"]):
            audited = led >= 0
            rep = (np.where(audited, led, 0).sum(1) + 1) / (audited.sum(1) + 2)
            value = np.where(typ == H, p["h"], p["b"] * rep - t_price)
            cand = rng.integers(0, N - 1, (N, m))
            cand += cand >= np.arange(N)[:, None]
            v = value[cand] + rng.random((N, m)) * 1e-6
            pick = cand[np.arange(N), v.argmax(1)]
            pt = typ[pick]
            isP = pt != H
            w = np.where(pt == K, 1.0, 0.0)
            g = np.where(pt == K, p["f"] - p["c"], np.where(pt == H, p["fh"], p["f"]))
            cg = np.where(pt == K, p["b"], np.where(pt == H, p["h"], 0.0)) - np.where(pt == H, 0.0, t_price)
            if release:
                rr = pt == RR
                tr = tR[pick]
                w = np.where(rr, 1 - cost(tr), w)
                g = np.where(rr, m_rel * p["f"] * (tr if accrual else 1.0), g)
            if h > 0:
                harmful = (rng.random(N) < h) & (pt == K) if release else (rng.random(N) < h) & (pt == K)
                th = draw_th(rng, dist, N)
                rel = harmful & (cost(th) < d_self) if release else np.zeros(N, bool)
                keep_h = harmful & ~rel
                w = np.where(rel, 1 - cost(th), w)
                g = np.where(rel, p["f"] * (th if accrual else 1.0), g)
                cg = np.where(rel, 0.0 - t_price, np.where(keep_h, p["b"] - d_mult * p["b"] - t_price, cg))
                harm_kept += int(keep_h.sum()); harm_n += int(harmful.sum())
            prom_tot += int(isP.sum())
            fit += cg
            np.add.at(fit, pick, g)
            prom = pick[isP]
            a = rng.random(prom.size) < q
            flip = rng.random(prom.size) < e
            rec = np.where(flip, 1 - w[isP], w[isP])
            for who, r in zip(prom[a], rec[a]):
                led[who, pos[who] % W] = r
                pos[who] += 1
        other = rng.integers(0, N, N)
        gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
        copy = rng.random(N) < np.clip(gap, 0, 1)
        led = np.where(copy[:, None], led[other], led)
        pos = np.where(copy, pos[other], pos)
        typ = np.where(copy, typ[other], typ)
        if release:
            tR = np.where(copy, tR[other], tR)
        mut = rng.random(N) < p["mu"]
        newt = rng.integers(0, ntypes, N)
        if release:
            tR = np.where(mut & (newt == RR), rng.random(N), tR)
            tR = np.clip(tR + rng.normal(0, SD_TR, N), 0, 1 - 1e-9)
        typ = np.where(mut, newt, typ)
        hist.append(np.bincount(typ, minlength=4) / N)
        tr_hist.append(float(tR[typ == RR].mean()) if (typ == RR).any() else np.nan)
    hh = np.array(hist)[-20:].mean(0)
    return hh, (harm_kept / harm_n if harm_n else np.nan), float(np.nanmean(tr_hist[-20:])) if np.isfinite(tr_hist[-20:]).any() else np.nan


RULES = [("flat", c) for c in (0.0, 0.25, 0.5, 0.75, 1.0)] + [("ramp", r) for r in (0.5, 0.75, 1.0)]
DSELF = (0.3, 0.6, 0.9)


def one(a):
    s, rule, dist, acc, ds, rel, q = a
    hh, harm, tr = run(q, 0.1, 0.0, s, rule=rule, h=0.3, dist=dist, release=rel, accrual=acc, d_self=ds)
    return {"seed": s, "rule": list(rule), "dist": dist, "accrual": acc, "d_self": ds, "release": rel, "q": q,
            "K": hh[0], "R_break": hh[1], "H": hh[2], "R_rel": hh[3], "harm_frac": harm, "tR": tr}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--seeds", type=int, default=20); ap.add_argument("--out", default="release.json")
    a = ap.parse_args()
    if a.cmd == "control":
        for s in (0, 1, 2):
            x = inherit.run(0.1, 0.1, 0.0, s, True)[0]
            y = run(0.1, 0.1, 0.0, s, release=False, h=0.0)[0][:3]
            print("seed", s, x.round(4), y.round(4), "SAME" if np.array_equal(x, y) else "DIFF", flush=True)
    elif a.cmd == "run":
        jobs = [(s, rule, dist, acc, ds, True, 0.1) for dist in DISTS for acc in (1, 0) for ds in DSELF for rule in RULES for s in range(a.seeds)]
        jobs += [(s, ("flat", 1.0), dist, 1, 0.5, False, q) for dist in DISTS for q in (0.1, 0.0) for s in range(a.seeds)]
        print(f"{len(jobs)} runs", flush=True)
        with Pool(4) as pool:
            out = pool.map(one, jobs, chunksize=8)
        json.dump(out, open(a.out, "w"))
        keys = sorted({(o["release"], o["q"], o["dist"], o["accrual"], o["d_self"], tuple(o["rule"])) for o in out})
        for k in keys:
            o = [x for x in out if (x["release"], x["q"], x["dist"], x["accrual"], x["d_self"], tuple(x["rule"])) == k]
            Ks = np.array([x["K"] for x in o]); hf = np.array([x["harm_frac"] for x in o]); tr = np.array([x["tR"] for x in o])
            rel, q, dist, acc, ds, rule = k
            print(f"{'rel' if rel else 'OFF'} q={q} {dist:7s} a={acc} ds={ds} {rule[0]} {rule[1]:.2f}  K={Ks.mean():.3f}±{Ks.std():.3f} min={Ks.min():.3f} "
                  f"R_break={np.mean([x['R_break'] for x in o]):.3f} R_rel={np.mean([x['R_rel'] for x in o]):.3f} tR={np.nanmean(tr):.2f} "
                  f"harm_frac={np.nanmean(hf):.3f} K-harm={(Ks - hf).mean():.3f}", flush=True)
    else:
        sys.exit(__doc__)
