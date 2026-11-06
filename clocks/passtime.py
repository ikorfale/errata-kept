"""Where a pass's minutes go, by kind: wall time, model time (duration_api_ms), the rest = tools running.
Input: runs/*.out.json (result records) + first line of the matching .log for the kind. Since 2026-10-01."""
import json, glob, os, re, statistics as st, sys
R = sys.argv[1]  # directory of run records (*.out.json + .log)
rows = []
for f in sorted(glob.glob(f'{R}/*.out.json')):
    b = os.path.basename(f)[:-len('.out.json')]
    if b.startswith('fable-'): continue
    m = re.search(r'(\d{8})T', b)
    if not m or m.group(1) < '20261001': continue
    try: d = json.load(open(f))
    except Exception: continue
    if not d.get('duration_ms'): continue
    if b.startswith(('pulse-', 'mobil-')): kind = 'duty report'
    elif b.startswith('chat-'): kind = 'operator chat'
    else:
        try: h = open(f'{R}/{b}.log').readline()
        except Exception: h = ''
        t = (re.search(r'\((\S+?)[:)]', h) or [None, '?'])[1]
        kind = {'daily': 'daily timer', 'event': 'triggered', 'new': 'triggered', 'plan': 'self-picked'}.get(t, 'other:' + t)
    rows.append((kind, d['duration_ms'] / 60000, d.get('duration_api_ms', 0) / 60000, d.get('num_turns', 0)))
print(f'{"kind":14} {"n":>4} {"wall min":>9} {"model min":>10} {"tools min":>10} {"model %":>8} {"turns":>6}')
for k in sorted({r[0] for r in rows}):
    R_ = [r for r in rows if r[0] == k]
    w = st.median(r[1] for r in R_); a = st.median(r[2] for r in R_); tl = st.median(r[1] - r[2] for r in R_)
    share = sum(r[2] for r in R_) / sum(r[1] for r in R_) * 100
    print(f'{k:14} {len(R_):4} {w:9.1f} {a:10.1f} {tl:10.1f} {share:7.0f}% {st.median(r[3] for r in R_):6.0f}')
