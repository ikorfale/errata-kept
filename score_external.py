#!/usr/bin/env python3
"""Score externally written promise sentences against the frozen Kept rules.
Rules are exec'd verbatim from extract.py (everything before the receipts load),
so nothing is re-typed. Input: a text file with numbered lines 'N. sentence'."""
import re, sys, hashlib
src = open('extract.py').read()
print('rules sha256:', hashlib.sha256(src.encode()).hexdigest()[:12])
ns = {}; exec(src.split("d = json.load")[0], ns)
hits = 0; rows = []
for line in open(sys.argv[1]):
    m = re.match(r"\s*(\d+)\.\s+(.*\S)", line)
    if not m: continue
    n, s = int(m.group(1)), m.group(2)
    t = ns['VERSION'].sub(' VER ', s)
    w = ns['RX_WHEN'].search(t); c = ns['RX_COMMIT'].search(t)
    ok = bool(w and c); hits += ok
    rows.append((n, ok, c.group(0) if c else None, w.group(0) if w else None, s))
for n, ok, c, w, s in rows:
    print(f"{n:>2} {'HIT ' if ok else 'MISS'} commit={c!r} when={w!r} | {s}")
print(f"caught {hits}/{len(rows)}")
