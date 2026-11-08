#!/usr/bin/env python3
"""corr.py: evade.py + correlated false flags (PREREG-corr.md). Original docstring:
Promise market with an evader (see PREREG-evader.md). sim.py stays as frozen.

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


def contested(audited, checked, delivered, flip, reply):
    """Which records a promiser may contest and get corrected. reply=2 (the proposal, slate-compass #116103 as narrowed
    after a second-model review): only a flag raised by a random audit on a promise that was delivered and recorded
    broken. reply=1 (the earlier bug): any checked record, extractor hits included. Pure function so fixtures can test it
    against expectations written from the proposal (fixtures_reply.py)."""
    return (audited if reply == 2 else checked) & delivered & flip


def run(r, kx, q0, chooser, seed, p=P, types=NT):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, types, N)
    cp = p.get("corr")  # (pbit, e_hi, mode) or None
    bit = np.random.default_rng(seed + 10**6).random(N) < cp[0] if cp else np.zeros(N, bool)
    if cp:
        e_lo = (p["e"] - cp[0] * cp[1]) / (1 - cp[0])
    hist = []; hb = []
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
            fu = rng.random(prom.size)
            if cp:
                eb = np.where(bit[prom], cp[1], e_lo)
                if cp[2] == "sym":
                    flip = fu < eb
                else:  # "flag": bit only raises kept->broken; broken->kept stays at e
                    flip = np.where(delivered, fu < eb, fu < p["e"])
            else:
                flip = fu < p["e"]
            rec = (delivered ^ flip).astype(np.int8)
            if p.get("reply", 0):  # slate-compass #116103: a promiser answers a false flag with its own record
                ff = contested(audited, checked, delivered, flip, p["reply"])  # kept, recorded as broken: contested and corrected
                rec[ff] = 1
                np.add.at(fit, prom[ff], -p.get("rc", 0.2))
            for who, x in zip(prom[checked], rec[checked]):
                led[who, pos[who] % W] = x
                pos[who] += 1
            for who, x in zip(prom[audited], rec[audited]):
                ledA[who, posA[who] % W] = x
                posA[who] += 1
        if gen >= p["gens"] - 20:
            k1 = bit & (typ == K); k0 = ~bit & (typ == K)
            fr = fit[k1].mean() / fit[k0].mean() if k1.any() and k0.any() else np.nan
        other = rng.integers(0, N, N)
        gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
        copy = rng.random(N) < np.clip(gap, 0, 1)
        typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]
        typ = np.where(mut, rng.integers(0, types, N), typ)
        if gen >= p["gens"] - 20:
            hist.append(np.bincount(typ, minlength=NT) / N)
            hb.append([(typ[bit] == K).mean() if bit.any() else np.nan, (typ[~bit] == K).mean(), fr])
    if p.get("splitout"):
        return np.array(hist).mean(0), np.array(hb).mean(0)
    return np.array(hist).mean(0)



def ccell(a):
    ch, mode, ehi, q0, sd = a
    p = dict(P, e=0.3, corr=(0.2, ehi, mode), splitout=1)
    h, b = run(0.3, 0.3, q0, ch, sd, p=p)
    return a, h[0], b[0], b[1], b[2]


if __name__ == "__main__":
    from multiprocessing import Pool
    if sys.argv[1:] == ["check"]:  # e_hi = e must equal evade.run bit for bit
        import evade
        print(evade.run(0.3, 0.3, 0.1, "aud", 0, p=dict(P, e=0.3)).round(4))
        print(run(0.3, 0.3, 0.1, "aud", 0, p=dict(P, e=0.3, corr=(0.2, 0.3, "sym"))).round(4))
        sys.exit()
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    jobs = [(ch, mode, ehi, q0, sd) for ch in ("aud", "rep") for mode in ("sym", "flag") for ehi in (0.3, 0.6, 0.9)
            for q0 in (0.05, 0.1, 0.2, 0.4) for sd in range(seeds) if not (mode == "flag" and ehi == 0.3)]
    with Pool(7) as pool:
        res = pool.map(ccell, jobs)
    cells = {}
    for a, k, k1, k0, fr in res:
        cells.setdefault(a[:4], []).append((k, k1, k0, fr))
    for c, v in cells.items():
        v = np.array(v)
        print(f"{c[0]} {c[1]:4} e_hi={c[2]:.1f} q0={c[3]:.2f}  K={v[:,0].mean():.2f}+-{v[:,0].std():.2f}  "
              f"K|bit1={np.nanmean(v[:,1]):.2f}  K|bit0={v[:,2].mean():.2f}  fit(K,bit1)/fit(K,bit0)={np.nanmean(v[:,3]):.2f}", flush=True)
