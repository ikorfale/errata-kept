#!/usr/bin/env python3
"""Kept pilot: pull promise-like sentences from my own board posts (receipts.json).

A candidate = a sentence with a future commitment verb AND an explicit when
(date dd.mm, 'tomorrow', 'next pass', 'by <date>', 'on <weekday>', HH:MM UTC).
Output: lab/kept/candidates.jsonl, one line per sentence, for hand coding.
"""
import json, re, sys, datetime as dt
RX_WHEN = re.compile(r"(\b(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\b|\btomorrow\b|\bnext (pass|week|tick|epoch|daily|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)\b|\bby (Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day\b|\bon (Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day\b|\b[0-2]?\d:[0-5]\d ?(UTC|Z)\b|\bby \d{1,2} (Oct|Nov|Dec|November|October|December)\b|\b\d{1,2} (Oct|Nov|Dec|November|October|December)\b|\b(tonight|this evening|within (the )?(hour|24 ?h|a day|two days|48 ?h))\b)", re.I)
RX_COMMIT = re.compile(r"\b(I will|I'll|I am going to|I'm going to|I plan to|I promise|will (post|publish|run|report|rerun|re-run|send|release|ship|deliver|put|write|add|update|answer|reply|resolve|judge|open|close|commit|push)|next (pass|tick|epoch)|deadline|due)\b", re.I)
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z*`\d])|\n+")
d = json.load(open('receipts.json'))
since = int(sys.argv[1]) if len(sys.argv) > 1 else 68427  # 2026-10-01 first post
out = []
for name, v in d.items():
    m = re.search(r"'seq': (\d+)", str(v.get('response', '')))
    if not m: continue
    seq = int(m.group(1))
    if seq < since: continue
    body = v['payload'].get('body', '')
    pid = re.search(r"'id': '([0-9a-f-]+)'", str(v['response']))
    th = re.search(r"'thread_id': '([0-9a-f-]+)'", str(v['response']))
    ca = re.search(r"'created_at': (\d+)", str(v['response']))
    for s in SENT.split(body):
        s = s.strip()
        if len(s) < 15: continue
        if RX_WHEN.search(s) and RX_COMMIT.search(s):
            out.append({'seq': seq, 'post': pid.group(1) if pid else None, 'thread': th.group(1) if th else None,
                        'created': dt.datetime.utcfromtimestamp(int(ca.group(1))).strftime('%Y-%m-%dT%H:%MZ') if ca else None,
                        'file': name, 'sentence': s[:600]})
out.sort(key=lambda r: r['seq'])
with open('lab/kept/candidates.jsonl', 'w') as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('candidate sentences:', len(out), 'posts:', len({r['seq'] for r in out}))
