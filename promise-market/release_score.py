"""Score the five frozen guesses of PREREG-release.md from release.log (no re-simulation).
Usage: python3 release_score.py release.log"""
import re, sys, collections
pat = re.compile(r'^(OFF|rel) q=([\d.]+) (\w+)\s+a=(\d) ds=([\d.]+) (flat|ramp) ([\d.]+)\s+K=([\d.]+)±([\d.]+) min=([\d.]+) R_break=([\d.]+) R_rel=([\d.]+) tR=(\S+) harm_frac=([\d.]+) K-harm=(-?[\d.]+)')
rows = []
for line in open(sys.argv[1]):
    m = pat.match(line.strip())
    if not m: continue
    arm,q,th,a,ds,kind,p,K,sd,mn,rb,rr,tR,hf,kh = m.groups()
    rows.append(dict(arm=arm,q=float(q),th=th,a=int(a),ds=float(ds),kind=kind,p=float(p),K=float(K),sd=float(sd),
                     rb=float(rb),rr=float(rr),tR=tR,hf=float(hf),kh=float(kh)))
print(f"rows parsed: {len(rows)}")
rel = [r for r in rows if r['arm']=='rel']
cells = collections.defaultdict(list)
for r in rel: cells[(r['th'],r['a'],r['ds'])].append(r)
print("\n# Per cell: best flat (by K-harm), ramps, verdicts. 'beats' = difference > 2*sd of the flat's seeds")
print(f"{'t_h':8}{'a':3}{'ds':5}| best flat c  K-harm (K, harm) | ramp .5 | ramp .75 | ramp 1.0 | ramp1>bestflat? capped(.5)~bestflat?")
summary = collections.defaultdict(list)
for key in sorted(cells):
    rs = cells[key]
    flats = [r for r in rs if r['kind']=='flat']
    ramps = {r['p']: r for r in rs if r['kind']=='ramp'}
    bf = max(flats, key=lambda r: r['kh'])
    # middle flats = .25,.5,.75
    bmid = max([r for r in flats if r['p'] in (.25,.5,.75)], key=lambda r: r['kh'])
    def cmp(r):  # +1 beats, 0 within noise, -1 loses, vs best flat
        d = r['kh'] - bf['kh']; tol = 2*max(bf['sd'], r['sd'])
        return '+' if d > tol else ('-' if d < -tol else '=')
    line = f"{key[0]:8}{key[1]:<3}{key[2]:<5}| c={bf['p']:.2f} {bf['kh']:+.3f} ({bf['K']:.3f},{bf['hf']:.2f}) |"
    for p in (.5,.75,1.0):
        r = ramps[p]; line += f" {r['kh']:+.3f}{cmp(r)}|"
    line += f"  r1 vs best flat: {cmp(ramps[1.0])}   r.5 vs best mid c={bmid['p']:.2f}: {cmp(ramps[.5])}  r.75: {cmp(ramps[.75])}"
    print(line)
    summary[key[0]].append((key, cmp(ramps[1.0]), cmp(ramps[.5]), cmp(ramps[.75]), bf, ramps))
print("\n# Guess 1 (slate): flat c sweep, pooled over t_h at a=1 (K, harm_frac) by c and ds")
for ds in (.3,.6,.9):
    for c in (0,.25,.5,.75,1.0):
        xs=[r for r in rel if r['a']==1 and r['ds']==ds and r['kind']=='flat' and r['p']==c]
        if not xs: continue
        print(f"  a=1 ds={ds} c={c:.2f}: K={sum(r['K'] for r in xs)/len(xs):.3f} harm={sum(r['hf'] for r in xs)/len(xs):.2f} R_rel={sum(r['rr'] for r in xs)/len(xs):.3f}")
print("\n# Guess 2 falsifier: a=0 (release keeps full fee = early release costless to reneger): ramp arms")
for r in rel:
    if r['a']==0 and r['kind']=='ramp' and r['ds']==.6: print(f"  {r['th']:8} ramp r={r['p']}: K={r['K']:.3f}±{r['sd']:.3f} R_rel={r['rr']:.3f} tR={r['tR']} K-harm={r['kh']:+.3f}")
print("\n# Reneger release time tR by arm (a=1): do renegers sit at the ramp crossing?")
for r in rel:
    if r['a']==1 and r['ds']==.6 and r['th']=='uniform': print(f"  {r['kind']} {r['p']:.2f}: tR={r['tR']} R_rel={r['rr']:.3f} R_break={r['rb']:.3f}")
