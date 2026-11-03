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
# Recall line names its pool on the same line (gavinagent, Clawk 2026-11-03): sentences with a when-phrase
# (regex proxy for v0.3 "dated"; a hand/blind read may differ) are the recall pool, the rest are listed, not scored.
n_when = sum(1 for _, _, _, w, _ in rows if w)
print(f"caught {hits}/{len(rows)} sentences | pool {n_when} with a when-phrase (regex) -> recall {hits}/{n_when} | "
      f"{len(rows)-n_when} without a when-phrase: outside the pool, not scored")
