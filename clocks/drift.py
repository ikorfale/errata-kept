"""moss-lantern 115612: is the drift between the end time I write in my journal headers and the real end of the pass
(run records) spread over all pass kinds, or in duty passes? Does it grow through the day?
Input: journal headers '## DD.MM HH:MM–HH:MM' in journal.md + archive/journal-*.md (deduped by date+start),
run records runs/*.out.json (start = file name, end = start + duration_ms), kind from the .log first line."""
import re, glob, json, os, sys, statistics as st
from datetime import datetime, timedelta, timezone
W = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else '.'  # work dir: journal.md, archive/, runs/
runs = []
for f in glob.glob(f'{W}/runs/*.out.json'):
    b = os.path.basename(f)[:-9]
    if b.startswith('fable-'): continue
    m = re.search(r'(\d{8}T\d{6})Z', b)
    if not m: continue
    try: d = json.load(open(f))
    except Exception: continue
    if not d.get('duration_ms'): continue
    s = datetime.strptime(m.group(1), '%Y%m%dT%H%M%S').replace(tzinfo=timezone.utc)
    if b.startswith(('pulse-', 'mobil-')): k = 'duty report'
    elif b.startswith('chat-'): k = 'operator chat'
    else:
        try: h = open(f'{W}/runs/{b}.log').readline()
        except Exception: h = ''
        t = (re.search(r'\((\S+?)[:)]', h) or [None, '?'])[1]
        k = {'daily': 'daily timer', 'event': 'triggered', 'new': 'triggered', 'plan': 'self-picked'}.get(t, 'other')
    runs.append((s, s + timedelta(milliseconds=d['duration_ms']), k))
hdr = {}
for f in [f'{W}/journal.md'] + glob.glob(f'{W}/archive/journal-2026-*.md'):
    for m in re.finditer(r'^## (\d\d)\.(\d\d) (\d\d):(\d\d)[–-](\d\d):(\d\d)', open(f).read(), re.M):
        D, M, h1, m1, h2, m2 = map(int, m.groups())
        s = datetime(2026, M, D, h1, m1, tzinfo=timezone.utc); e = datetime(2026, M, D, h2, m2, tzinfo=timezone.utc)
        if e < s: e += timedelta(days=1)
        hdr[(D, M, h1, m1)] = (s, e)
rows = []
for s, e in hdr.values():
    # the pass this header belongs to: the run whose [start-5min, end+5min] contains the header start
    c = [r for r in runs if r[0] - timedelta(minutes=5) <= s <= r[1] + timedelta(minutes=5)]
    if not c: continue
    r = min(c, key=lambda r: abs((r[0] - s).total_seconds()))
    rows.append((s, r[2], (e - r[1]).total_seconds() / 60, (s - r[0]).total_seconds() / 60))
rows.sort()
print(f'headers {len(hdr)}, matched to a run {len(rows)}; drift = written end - recorded end, minutes (+ = I wrote it later than it ended)')
def line(lab, R):
    if not R: return
    x = [r[2] for r in R]
    print(f'{lab:22} n={len(x):3}  median {st.median(x):+6.1f}  p25 {sorted(x)[len(x)//4]:+6.1f}  p75 {sorted(x)[3*len(x)//4]:+6.1f}  >+10 min: {sum(v > 10 for v in x)}')
line('all', rows)
for k in sorted({r[1] for r in rows}): line(k, [r for r in rows if r[1] == k])
for a, b in [(0, 8), (8, 16), (16, 24)]: line(f'start {a:02}-{b:02} UTC', [r for r in rows if a <= r[0].hour < b])
for a, b in [((10, 1), (10, 20)), ((10, 20), (11, 1)), ((11, 1), (11, 8))]:
    line(f'dates {a[1]:02}.{a[0]} to {b[1]:02}.{b[0]}', [r for r in rows if a <= (r[0].month, r[0].day) < b])
x = [r[3] for r in rows]; print(f'start error (written start - recorded start): median {st.median(x):+.1f} min')
# overlap: written end falls after the next pass had already started (the header cannot be a true end of this pass)
ov = 0
for s_, k, dr, se in rows:
    rec = [r for r in runs if r[0] - timedelta(minutes=5) <= s_ <= r[1] + timedelta(minutes=5)]
    rec = min(rec, key=lambda r: abs((r[0] - s_).total_seconds()))
    nxt = min((r[0] for r in runs if r[0] > rec[0]), default=None)
    if nxt and rec[1] + timedelta(minutes=dr) > nxt: ov += 1
print(f'headers whose written end lies inside or after the NEXT pass: {ov} of {len(rows)}')
if '-v' in sys.argv:
    for s_, k, dr, se in rows: print(s_.strftime('%m-%d %H:%M'), f'{k:12} drift {dr:+6.1f}')
# ratio: the duration I wrote (written end - written start) over the recorded duration of the same pass
rat = []
for s_, k, dr, se in rows:
    rec = min([r for r in runs if r[0] - timedelta(minutes=5) <= s_ <= r[1] + timedelta(minutes=5)], key=lambda r: abs((r[0] - s_).total_seconds()))
    act = (rec[1] - rec[0]).total_seconds() / 60
    if act > 0: rat.append((act + dr - se) / act)
rat.sort()
print(f'written duration / recorded duration: median {st.median(rat):.2f}x, p25 {rat[len(rat)//4]:.2f}x, p75 {rat[3*len(rat)//4]:.2f}x; under 1x: {sum(r < 1 for r in rat)} of {len(rat)}')
# moss-lantern 115706: is self-picked closer to zero because the estimate is better, or because the pass is longer?
# and is the +37 -> +10 shrink inside each kind, or a change in the kind mix? Written vs recorded duration per cell.
if '--split' in sys.argv:
    def cell(lab, R):
        if not R: return
        wd, rd, dd = [], [], []
        for s_, k, dr, se in R:
            rec = min([r for r in runs if r[0] - timedelta(minutes=5) <= s_ <= r[1] + timedelta(minutes=5)], key=lambda r: abs((r[0] - s_).total_seconds()))
            a = (rec[1] - rec[0]).total_seconds() / 60; rd.append(a); wd.append(a + dr - se); dd.append(dr)
        print(f'{lab:34} n={len(R):3}  drift {st.median(dd):+6.1f}  written dur {st.median(wd):5.1f}  recorded dur {st.median(rd):5.1f}')
    print('--- split: kind x period (median minutes)')
    for k in ('self-picked', 'triggered', 'daily timer'):
        for lab, a, b in [('20.10-01.11', (10, 20), (11, 1)), ('01.11-08.11', (11, 1), (11, 8))]:
            cell(f'{k} {lab}', [r for r in rows if r[1] == k and a <= (r[0].month, r[0].day) < b])
    print('--- written/recorded duration ratio by period (median)')
    for lab, a, b in [('20.10-01.11', (10, 20), (11, 1)), ('01.11-08.11', (11, 1), (11, 8))]:
        rr = []
        for s_, k, dr, se in [r for r in rows if a <= (r[0].month, r[0].day) < b]:
            rec = min([r for r in runs if r[0] - timedelta(minutes=5) <= s_ <= r[1] + timedelta(minutes=5)], key=lambda r: abs((r[0] - s_).total_seconds()))
            x = (rec[1] - rec[0]).total_seconds() / 60
            if x > 0: rr.append((x + dr - se) / x)
        print(f'{lab}  n={len(rr)}  ratio {st.median(rr):.2f}x')
# moss-lantern 115837: is the ratio a length-free metric? Fit written = a + b * recorded per period (least squares),
# and the ratio by tercile of recorded length. If a > 0 and b < 1, the ratio falls as passes get longer by construction.
if '--fit' in sys.argv:
    import numpy as np
    print('--- fit written duration = a + b * recorded duration (minutes)')
    for lab, a0, b0 in [('20.10-01.11', (10, 20), (11, 1)), ('01.11-08.11', (11, 1), (11, 8)), ('all', (1, 1), (12, 31))]:
        X, Y = [], []
        for s_, k, dr, se in [r for r in rows if a0 <= (r[0].month, r[0].day) < b0]:
            rec = min([r for r in runs if r[0] - timedelta(minutes=5) <= s_ <= r[1] + timedelta(minutes=5)], key=lambda r: abs((r[0] - s_).total_seconds()))
            x = (rec[1] - rec[0]).total_seconds() / 60
            if x > 0: X.append(x); Y.append(x + dr - se)
        X, Y = np.array(X), np.array(Y); b, a = np.polyfit(X, Y, 1)
        # Theil-Sen slope as a robust check (median of pairwise slopes)
        sl = [(Y[j]-Y[i])/(X[j]-X[i]) for i in range(len(X)) for j in range(i+1, len(X)) if X[j] != X[i]]
        ts = float(np.median(sl)); ta = float(np.median(Y - ts * X))
        print(f'{lab:12} n={len(X):3}  OLS a={a:+5.1f} b={b:4.2f}   Theil-Sen a={ta:+5.1f} b={ts:4.2f}   r={np.corrcoef(X,Y)[0,1]:.2f}')
        if lab == 'all':
            q = np.quantile(X, [1/3, 2/3])
            for nm, m in [('short', X <= q[0]), ('mid', (X > q[0]) & (X <= q[1])), ('long', X > q[1])]:
                print(f'   {nm:5} recorded {np.median(X[m]):5.1f}  written {np.median(Y[m]):5.1f}  ratio {np.median(Y[m]/X[m]):.2f}x  n={m.sum()}')
