#!/usr/bin/env python3
"""Kept: renegotiation lead time (adopted in board thread 5c0c2dd8, 04.11; schema promised by 08.11).

For every verdict row with verdict `announced_revision` or `renegotiated`:
  lead      = original deadline - time of the public notice (hours; negative = notice came after the deadline)
  horizon   = original deadline - time the promise was posted (hours)
  share     = lead / horizon (share of the horizon still left when the notice came)
  late_notice = share < 0.10  (a change one minute before the deadline shows up as what it is)
A notice after the deadline is not a revision under RULES.md (it is judged as broken or kept-late); lead.py
prints it as `after-deadline` so a mislabelled row is visible instead of silently counted.

This sits at the verdict stage, after rows.py. rows.py and the round-1 freeze are untouched.
Usage: lead.py VERDICTS.jsonl   (fields: promised, deadline, notice_at as ISO-8601 UTC; verdict)"""
import json, sys, datetime as dt

KINDS = ('announced_revision', 'renegotiated')
LATE = 0.10


def t(s):
    d = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    if d.tzinfo is None:
        raise ValueError(f'naive time {s!r}: every time in a verdict row is UTC with an offset')
    return d.astimezone(dt.timezone.utc)


def lead(row):
    """Return dict(lead_h, horizon_h, share, label) for one revision row."""
    p, d, n = t(row['promised']), t(row['deadline']), t(row['notice_at'])
    if not p < d:
        raise ValueError(f"deadline {row['deadline']} is not after the promise {row['promised']}")
    if n < p:
        raise ValueError(f"notice {row['notice_at']} predates the promise {row['promised']}")
    lead_h = (d - n).total_seconds() / 3600
    hor_h = (d - p).total_seconds() / 3600
    share = lead_h / hor_h
    label = 'after-deadline' if lead_h < 0 else ('late-notice' if share < LATE else 'in-time')
    return {'lead_h': round(lead_h, 2), 'horizon_h': round(hor_h, 2), 'share': round(share, 3), 'label': label}


def table(rows):
    out = {k: {'n': 0, 'late-notice': 0, 'after-deadline': 0, 'leads_h': []} for k in KINDS}
    for r in rows:
        if r.get('verdict') not in KINDS:
            continue
        x = lead(r); o = out[r['verdict']]
        o['n'] += 1; o['leads_h'].append(x['lead_h'])
        if x['label'] != 'in-time':
            o[x['label']] += 1
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    for r in rows:
        if r.get('verdict') in KINDS:
            print(json.dumps({'seq': r.get('promise_seq'), 'verdict': r['verdict'], **lead(r)}))
    for k, o in table(rows).items():
        med = sorted(o['leads_h'])[len(o['leads_h']) // 2] if o['leads_h'] else None
        print(f"{k}: n={o['n']} | notice with <10% of horizon left: {o['late-notice']} of {o['n']} | "
              f"after the deadline (mislabelled?): {o['after-deadline']} | median lead {med} h")


if __name__ == '__main__':
    main()
