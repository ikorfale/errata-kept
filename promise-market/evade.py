#!/usr/bin/env python3
"""Promise market with an evader (see PREREG-evader.md). sim.py stays as frozen.

Types: K keep, R renege, H safe, X evader. K/R promises are extracted (checked) with prob r.
X keeps a share kx of its promises and makes exactly those extractable; the rest are never extracted.
q0: random audit of any promise, independent of phrasing. Checked records flip with prob e.
Chooser 'rep': b*rep; 'dens': b*rep*min(1, d/r) with d = checked/made this generation.
Usage: evade.py sweep [--seeds 5] [--out evade.json] | evade.py one r kx q0 chooser seed
"""
import argparse, json, sys
import numpy as np

P = dict(N=200, m=5, b=3.0, c=1.0, f=2.0, h=1.2, fh=1.0, W=20, G=30, gens=150, mu=0.01, e=0.0)
K, R, H, X = 0, 1, 2, 3
NT = 4


def run(r, kx, q0, chooser, seed, p=P, types=NT):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, types, N)
    hist = []
    for gen in range(p["gens"]):
        led = -np.ones((N, W), dtype=np.int8)
        pos = np.zeros(N, dtype=np.int64)
        ledA = -np.ones((N, W), dtype=np.int8); posA = np.zeros(N, dtype=np.int64)  # audit-only records
        made = np.zeros(N); chk = np.zeros(N)
        fit = np.zeros(N)
        for _ in range(p["G"]):
            L = ledA if chooser == "aud" else led  # 'aud': score only from random-audit records
            kept = (L == 1).sum(1); aud = (L >= 0).sum(1)
            rep = (kept + p.get("a0", 1)) / (aud + 2 * p.get("a0", 1))
            if chooser == "dens":
                dk = p.get("dk", 0)  # pseudo-counts at the norm r (Fable review: raw d hits 0 after one unchecked promise)
                d = (chk + dk * r) / (made + dk) if dk > 0 else np.where(made > 0, chk / np.maximum(made, 1), r)
                rep = rep * np.minimum(1.0, d / r)
            value = np.where(typ == H, p["h"], p["b"] * rep)
            cand = rng.integers(0, N - 1, (N, m))
            cand += cand >= np.arange(N)[:, None]
            v = value[cand] + rng.random((N, m)) * 1e-6
            pick = cand[np.arange(N), v.argmax(1)]
            pt = typ[pick]
            prom_mask = pt != H
            prom = pick[prom_mask]; ptp = pt[prom_mask]
            u = rng.random(prom.size)
            rx = rng.random(prom.size)  # same draw order as before the leak edit: u, extraction, audit
            audited = rng.random(prom.size) < q0
            # leak (agenthaven #116109): X foresees an audit with prob p['leak'] and keeps that promise
            lk = p.get("leak", 0.0)
            foresee = audited & (rng.random(prom.size) < lk) if lk > 0 else np.zeros(prom.size, bool)
            # grind (hivefound, Moltbook 07.11): the audit seed is a future event, but the promiser may influence it.
            # With prob p['ginf'] an X that plans to break a promise picks among p['grind'] candidate seeds and takes one
            # that skips that promise: it is audited only if every candidate selects it (q0**N). Extra draws only if grind > 1.
            gn = p.get("grind", 1)
            if gn > 1:
                infl = (ptp == X) & (u >= kx) & (rng.random(prom.size) < p.get("ginf", 1.0))
                every = (rng.random((prom.size, gn - 1)) < q0).all(1)
                audited = audited & ~(infl & ~every)
            delivered = (ptp == K) | ((ptp == X) & ((u < kx) | foresee))
            # chooser payoff
            pay = np.zeros(N)
            pay[prom_mask] = np.where(delivered, p["b"], 0.0)
            pay[pt == H] = p["h"]
            fit += pay
            np.add.at(fit, pick, np.where(pt == H, p["fh"], p["f"]))
            np.add.at(fit, prom[delivered], -p["c"])
            extract = np.where(ptp == X, u < kx, rx < r)  # X makes only its planned keeps extractable
            checked = extract | audited
            np.add.at(made, prom, 1); np.add.at(chk, prom[checked], 1)
            flip = rng.random(prom.size) < p["e"]
            rec = (delivered ^ flip).astype(np.int8)
            if p.get("reply", 0):  # slate-compass #116103: a promiser answers a false flag with its own record
                ff = (audited if p["reply"] == 2 else checked) & delivered & flip  # reply=2: audit flags only (Fable review)          # kept, recorded as broken: contested and corrected
                rec[ff] = 1
                np.add.at(fit, prom[ff], -p.get("rc", 0.2))
            for who, x in zip(prom[checked], rec[checked]):
                led[who, pos[who] % W] = x
                pos[who] += 1
            for who, x in zip(prom[audited], rec[audited]):
                ledA[who, posA[who] % W] = x
                posA[who] += 1
        other = rng.integers(0, N, N)
        gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
        copy = rng.random(N) < np.clip(gap, 0, 1)
        typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]
        typ = np.where(mut, rng.integers(0, types, N), typ)
        if gen >= p["gens"] - 20:
            hist.append(np.bincount(typ, minlength=NT) / N)
    return np.array(hist).mean(0)


def fcell(args):
    r, e, q0, reply, seeds = args
    p = dict(P, e=e, reply=reply, rc=0.2)
    s = np.array([run(r, r, q0, "rep", sd, p=p) for sd in range(seeds)])
    mu, sd = s.mean(0), s.std(0)
    return dict(r=r, e=e, q0=q0, reply=reply, K=mu[0], R=mu[1], H=mu[2], X=mu[3], K_sd=sd[0], seeds=seeds)


def fsweep(seeds, out):  # PREREG-flags.md: mimic evader, chooser rep
    from multiprocessing import Pool
    jobs = [(r, e, q0, rp, seeds) for r in (0.3, 0.5) for e in (0.0, 0.3) for rp in (0, 1)
            for q0 in (0.0, 0.02, 0.05, 0.1, 0.2, 0.4) if not (e == 0.0 and rp == 1)]
    with Pool(6) as pool:
        rows = pool.map(fcell, jobs)
    for x in rows:
        print(f"r={x['r']:.1f} e={x['e']:.1f} reply={x['reply']} q0={x['q0']:.2f}  K={x['K']:.2f}+-{x['K_sd']:.2f} "
              f"R={x['R']:.2f} H={x['H']:.2f} X={x['X']:.2f}", flush=True)
    json.dump(dict(params=P, rc=0.2, rows=rows), open(out, "w"), indent=1)


def cell(args):
    r, kxname, q0, ch, seeds = args
    kx = r if kxname == "mimic" else float(kxname)
    s = np.array([run(r, kx, q0, ch, sd) for sd in range(seeds)])
    mu, sd = s.mean(0), s.std(0)
    return dict(r=r, evader=kxname, kx=kx, q0=q0, chooser=ch, K=mu[0], R=mu[1], H=mu[2], X=mu[3],
                K_sd=sd[0], seeds=seeds)


def sweep(seeds, out):
    from multiprocessing import Pool
    jobs = [(r, ev, q0, ch, seeds) for ev in ("mimic", "0.1") for q0 in (0.0, 0.05) for ch in ("rep", "dens")
            for r in (0.15, 0.3, 0.5, 0.8, 1.0)]
    with Pool(6) as pool:
        rows = pool.map(cell, jobs)
    for x in rows:
        print(f"{x['evader']:>5} q0={x['q0']:.2f} {x['chooser']:4} r={x['r']:.2f}  K={x['K']:.2f}±{x['K_sd']:.2f} "
              f"R={x['R']:.2f} H={x['H']:.2f} X={x['X']:.2f}", flush=True)
    json.dump(dict(params=P, rows=rows), open(out, "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd"); ap.add_argument("args", nargs="*")
    ap.add_argument("--seeds", type=int, default=5); ap.add_argument("--out", default="evade.json")
    a = ap.parse_args()
    if a.cmd == "fsweep":
        fsweep(a.seeds, a.out)
    elif a.cmd == "sweep":
        sweep(a.seeds, a.out)
    elif a.cmd == "one":
        r, kx, q0, ch, s = float(a.args[0]), float(a.args[1]), float(a.args[2]), a.args[3], int(a.args[4])
        print(run(r, kx, q0, ch, s).round(3))
    elif a.cmd == "check":  # without X, r plays q: should match sim.py one q 0 seed in distribution
        import sim
        for q in (0.01, 0.05):
            print(q, "sim", sim.run(q, 0.0, 0).round(2), "evade3", run(q, 1, 0, "rep", 0, types=3).round(2))
    else:
        sys.exit(__doc__)
