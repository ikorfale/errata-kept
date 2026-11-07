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
