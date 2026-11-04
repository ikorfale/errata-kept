#!/usr/bin/env python3
"""Check that every verdict row can still be re-scored from the commit it names.

usage: verify.py ROWS.jsonl [ROWS.jsonl ...]

For each row: the commit must exist and be on origin/main, and the sha256 of reader_prompt_v03.txt, reader.py and
rows.py read back from that commit must equal the row's prompt_sha, code_sha and rows_sha. rows.py merges the three reads
later than reader.py takes them, so round-1 rows name the reader's commit only; when rows.py at that commit differs,
the rows.py that made the row is searched for in main's history by its hash and named (a gap: rows.py should write its
own commit; due at the next freeze, since rows.py is frozen for round 1). Any miss is reported and the exit code is 1.
There is no fallback to the newest files: a row whose commit cannot be read back is unverifiable, not re-scored
under other rules (gavinagent, Clawk 04.11). main refuses force-pushes and deletion, so a commit that
was on main when the row was written stays readable.
"""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GIT = ['git', '-C', HERE]
FILES = {'prompt_sha': 'reader_prompt_v03.txt', 'code_sha': 'reader.py', 'rows_sha': 'rows.py'}

def at(commit, path):
    r = subprocess.run(GIT + ['show', f'{commit}:{path}'], capture_output=True)
    return hashlib.sha256(r.stdout).hexdigest()[:12] if r.returncode == 0 else None

def rows_commit(sha, cache):
    key = ('rows', sha)
    if key not in cache:
        log = subprocess.run(GIT + ['log', '--format=%H', 'origin/main', '--', 'rows.py'], capture_output=True, text=True)
        cache[key] = next((c for c in log.stdout.split() if at(c, 'rows.py') == sha), None)
    return cache[key]

def check(row, cache, notes):
    c = row.get('commit')
    if not c:
        return ['no commit in row']
    if c not in cache:
        ok = subprocess.run(GIT + ['cat-file', '-e', c + '^{commit}'], capture_output=True).returncode == 0
        on_main = ok and subprocess.run(GIT + ['merge-base', '--is-ancestor', c, 'origin/main']).returncode == 0
        cache[c] = (ok, on_main, {k: at(c, f) for k, f in FILES.items()} if ok else {})
    ok, on_main, shas = cache[c]
    if not ok:
        return [f'commit {c[:12]} not found: unverifiable, no fallback']
    errs = [] if on_main else [f'commit {c[:12]} is not on origin/main']
    for k, f in FILES.items():
        if row.get(k) is not None and shas.get(k) != row[k]:
            if k == 'rows_sha' and rows_commit(row[k], cache):
                notes.add(f'rows.py {row[k]} is at {rows_commit(row[k], cache)[:12]} on main, not at the read commit {c[:12]}')
                continue
            errs.append(f'{k} {row[k]} != {f}@{c[:12]} {shas.get(k)}')
    return errs

def main(paths):
    subprocess.run(GIT + ['fetch', '-q', 'origin', 'main'])
    cache, notes, n, bad = {}, set(), 0, 0
    for p in paths:
        for i, l in enumerate(open(p), 1):
            if not l.strip():
                continue
            n += 1
            errs = check(json.loads(l), cache, notes)
            if errs:
                bad += 1
                print(f'{p}:{i}: ' + '; '.join(errs))
    for x in sorted(notes):
        print('note: ' + x)
    print(f'{n} rows, {n - bad} verified, {bad} failed')
    return 1 if bad else 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
