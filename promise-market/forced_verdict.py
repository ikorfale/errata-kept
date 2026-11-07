#!/usr/bin/env python3
"""Verdicts for PREREG-forced.md from forced.json, plus where the stuck seeds turn."""
import json, numpy as np
out = json.load(open("forced.json"))
up = [o for o in out if o[1][0] > 0.5]; dn = [o for o in out if o[1][0] <= 0.5]
print("1. takeoffs", len(up), "of", len(out))
ok = sum((o[2][10]["K"] > o[2][10]["H"]) == (o[1][0] > 0.5) for o in out)
print("2. sign(K-H) at gen 10 predicts outcome in", ok, "of", len(out))
for g in (20, 30, 40, 60):
    print(f"   at gen {g}:", sum((o[2][g]["K"] > o[2][g]["H"]) == (o[1][0] > 0.5) for o in out))
f0 = lambda S: np.mean([o[2][0]["forced"] for o in S])
e02 = lambda S: np.mean([sum(o[2][g]["earned"] for g in range(3)) for o in S])
print(f"3. gen-0 forced: takeoff {f0(up):.0f}  stuck {f0(dn):.0f}  ratio {f0(up)/f0(dn):.2f}")
print(f"   earned g0-2: takeoff {e02(up):.0f}  stuck {e02(dn):.0f}  ratio {e02(up)/e02(dn):.2f}")
st = [o for o in dn]
print("4. stuck seeds with forced <1% of picks at gen 10:", sum(o[2][10]["forced"] < 0.01 * o[2][10]["all"] for o in st), "of", len(st),
      "| and every gen 10-149:", sum(all(r["forced"] < 0.01 * r["all"] for r in o[2][10:]) for o in st))
print("   takeoff seeds with earned > forced by gen 5:", sum(o[2][5]["earned"] > o[2][5]["forced"] for o in up), "of", len(up),
      "| already at gen 0:", sum(o[2][0]["earned"] > o[2][0]["forced"] for o in out), "of", len(out))
print("H at gen 0, takeoff vs stuck:", round(np.mean([o[2][0]['H'] for o in up]), 3), round(np.mean([o[2][0]['H'] for o in dn]), 3))
print("gen-0 forced vs takeoff, all seeds sorted by forced:")
print("  ", sorted((o[2][0]["forced"], int(o[1][0] > .5)) for o in out))
print("stuck seeds: trajectory K/R/H every 10 gens until H > 0.9")
for o in dn:
    tr = []
    for g in range(0, 150, 10):
        r = o[2][g]; tr.append(f"{g}:{r['K']:.2f}/{r['R']:.2f}/{r['H']:.2f}")
        if r["H"] > 0.9: break
    print(f"  seed {o[0]:2d}", " ".join(tr))
print("takeoff seeds: same")
for o in up:
    tr = [f"{g}:{o[2][g]['K']:.2f}/{o[2][g]['R']:.2f}/{o[2][g]['H']:.2f}" for g in range(0, 60, 10)]
    print(f"  seed {o[0]:2d}", " ".join(tr))
