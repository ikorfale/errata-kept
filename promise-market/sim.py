#!/usr/bin/env python3
"""Promise market: does a public ledger of audited promises make reneging unprofitable?

Types: K keeps promises (pays c to deliver b), R promises and never delivers,
H makes no promise and offers a small sure benefit h.
Each round every agent (as chooser) samples m candidates and picks the one with the
highest expected benefit: b * rep for promisers, h for H. The chosen candidate earns a fee
(f for promisers, fh for H). Each delivered/broken promise is audited with probability q;
an audited record is flipped with probability e (false flag / false clear).
rep = (kept + 1) / (audited + 2) over the candidate's last W audited records.
After each generation of G rounds, every agent compares with a random other and copies it
with probability proportional to the fitness gap (pairwise imitation), plus mutation mu.

Usage: sim.py sweep [--seeds 5] [--out results.json]   |   sim.py one q e seed
"""
import argparse, json, sys
import numpy as np

P = dict(N=200, m=5, b=3.0, c=1.0, f=2.0, h=1.2, fh=1.0, W=20, G=30, gens=150, mu=0.01)
K, R, H = 0, 1, 2


def run(q, e, seed, p=P, trace=False):
    rng = np.random.default_rng(seed)
    N, m, W = p["N"], p["m"], p["W"]
    typ = rng.integers(0, 3, N)
    hist = []
    for gen in range(p["gens"]):
        # ledger: ring buffer of last W audited records per agent (1 kept, 0 broken, -1 empty)
        led = -np.ones((N, W), dtype=np.int8)
        pos = np.zeros(N, dtype=np.int64)
        fit = np.zeros(N)
        for _ in range(p["G"]):
            kept = (led == 1).sum(1)
            aud = (led >= 0).sum(1)
            rep = (kept + 1) / (aud + 2)
            value = np.where(typ == H, p["h"], p["b"] * rep)
            cand = rng.integers(0, N - 1, (N, m))
            cand += cand >= np.arange(N)[:, None]  # no self
            v = value[cand] + rng.random((N, m)) * 1e-6
            pick = cand[np.arange(N), v.argmax(1)]
            pt = typ[pick]
            # chooser payoff
            fit += np.where(pt == K, p["b"], np.where(pt == H, p["h"], 0.0))
            # chosen payoff
            np.add.at(fit, pick, np.where(pt == H, p["fh"], p["f"]))
            np.add.at(fit, pick[pt == K], -p["c"])
            # audits of promises made this round
            prom = pick[pt != H]
            delivered = typ[prom] == K
            a = rng.random(prom.size) < q
            flip = rng.random(prom.size) < e
            rec = (delivered ^ flip).astype(np.int8)
            for who, r in zip(prom[a], rec[a]):
                led[who, pos[who] % W] = r
                pos[who] += 1
        # imitation
        other = rng.integers(0, N, N)
        gap = (fit[other] - fit) / (np.abs(fit).max() + 1e-9)
        copy = rng.random(N) < np.clip(gap, 0, 1)
        typ = np.where(copy, typ[other], typ)
        mut = rng.random(N) < p["mu"]
        typ = np.where(mut, rng.integers(0, 3, N), typ)
        if trace or gen >= p["gens"] - 20:
            hist.append(np.bincount(typ, minlength=3) / N)
    h = np.array(hist)
    return h if trace else h.mean(0)  # mean share over last 20 generations


def sweep(seeds, out, only_e=None):
    qs = [0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0]
    es = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.45]
    res = []
    for e in (es if only_e is None else [only_e]):
        for q in qs:
            shares = np.array([run(q, e, s) for s in range(seeds)])
            mu, sd = shares.mean(0), shares.std(0)
            res.append(dict(q=q, e=e, K=mu[0], R=mu[1], H=mu[2], K_sd=sd[0], seeds=seeds))
            print(f"e={e:.2f} q={q:.2f}  K={mu[0]:.2f}±{sd[0]:.2f} R={mu[1]:.2f} H={mu[2]:.2f}", flush=True)
    json.dump(dict(params=P, rows=res), open(out, "w"), indent=1)


def gsweep(seeds, out, e=0.2):
    """Same expected audits per lifetime (q*G) at different lifetimes G: does K share line up by q*G?"""
    res = []
    for G in (10, 30, 90):
        for qg in (0, 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3):
            q = qg / G
            pp = dict(P, G=G)
            shares = np.array([run(q, e, s, pp) for s in range(seeds)])
            mu = shares.mean(0)
            res.append(dict(G=G, qG=qg, q=q, e=e, K=mu[0], R=mu[1], H=mu[2], K_sd=shares.std(0)[0], seeds=seeds))
            print(f"G={G} qG={qg} q={q:.4f} K={mu[0]:.2f} R={mu[1]:.2f} H={mu[2]:.2f}", flush=True)
    json.dump(dict(params=P, e=e, rows=res), open(out, "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("args", nargs="*")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--e", type=float, default=None)
    a = ap.parse_args()
    if a.cmd == "sweep":
        sweep(a.seeds, a.out, a.e)
    elif a.cmd == "gsweep":
        gsweep(a.seeds, a.out)
    elif a.cmd == "one":
        q, e, s = float(a.args[0]), float(a.args[1]), int(a.args[2])
        print(run(q, e, s).round(3))
    else:
        sys.exit(__doc__)
