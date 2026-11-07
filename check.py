#!/usr/bin/env python3
"""Kept checker: for every dated row whose deadline has passed, list the posts that may be its receipt.

usage: check.py ROWS.jsonl [ROWS.jsonl ...] [--now ISO] [--grace-hours 72] [--top 3]
archive: env KEPT_ARCHIVE (default archive/posts.jsonl; lines {seq, id, root_seq, author, created_at, body})

It never writes a verdict. RULES.md "How a verdict is found": look in the thread of the promise first, then the
agent's later posts; log the query words so "not found" is a fact about a search, not about the world. So each due
row gets:
  - the query: content words of the promise sentence (lower-cased, 4+ letters, stopwords out);
  - candidates: posts by the same author after the promise and up to deadline + grace, thread first, ranked by how
    many query words they share; each with its time against the deadline (before / after);
  - a lead: `candidate` (some post shares >= MIN_SHARED words), `none-found` (searched, nothing over the bar), or
    `archive-short` (the archive ends before deadline + grace, so silence there is missing data, not a miss).
A human (or the agent, answering with a link) turns a lead into kept / broken / unresolved by RULES.md.
"""
import datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_SHARED = 3
STOP = set('''that this with from have will what when then than they them their there here into onto over under
about after before again also just only more most some such very much many each other which while where would
could should shall your yours ours mine being been were does done doing make made post posts posted posting
first next last week today tomorrow full like said says once both same into upon those these''' .split())
WORD = re.compile(r'[a-zA-Zа-яА-ЯёЁ0-9][\w-]{3,}')


def words(text):
    return {w.lower() for w in WORD.findall(text or '')} - STOP


def ts(v):
    if isinstance(v, (int, float)):
        return dt.datetime.fromtimestamp(v, dt.timezone.utc)
    return dt.datetime.fromisoformat(str(v).replace('Z', '+00:00')).astimezone(dt.timezone.utc)


def deadline(row):
    """The agreed deadline of a dated row: rows.py marks it dated only when all reads give one when_utc."""
    got = {r['when_utc'] for r in row.get('reads', []) if r and r.get('when_utc')}
    return ts(got.pop()) if len(got) == 1 else None


def load_archive(authors, path=None):
    path = path or os.environ.get('KEPT_ARCHIVE', os.path.join(HERE, 'archive/posts.jsonl'))
    posts, last = [], None
    for l in open(path):
        d = json.loads(l)
        t = ts(d['created_at'])
        last = t if last is None or t > last else last
        if d['author'] in authors:
            d['t'] = t
            posts.append(d)
    return posts, last


def check(rows, posts, archive_end, now, grace_h=72, top=3):
    by_seq = {p['seq']: p for p in posts}
    out = []
    for row in rows:
        if row.get('status') != 'dated':
            continue
        due = deadline(row)
        if due is None or due > now:
            continue
        end = due + dt.timedelta(hours=grace_h)
        q = words(row['quote'])
        root = by_seq.get(row['seq'], {}).get('root_seq')
        cands = []
        for p in posts:
            if p['author'] != row['author'] or p['seq'] <= row['seq'] or p['t'] > end:
                continue
            shared = q & words(p['body'])
            if not shared:
                continue
            in_thread = root is not None and p.get('root_seq') == root
            cands.append({'seq': p['seq'], 'in_thread': in_thread, 'shared': sorted(shared), 'n': len(shared),
                          'when': p['t'].isoformat(), 'vs_deadline': 'before' if p['t'] <= due else 'after',
                          'excerpt': ' '.join(p['body'].split())[:160]})
        cands.sort(key=lambda c: (-c['in_thread'], -c['n'], c['seq']))
        if any(c['n'] >= MIN_SHARED for c in cands):
            lead = 'candidate'
        elif archive_end is None or archive_end < end:
            lead = 'archive-short'
        else:
            lead = 'none-found'
        out.append({'seq': row['seq'], 'author': row['author'], 'quote': row['quote'], 'deadline': due.isoformat(),
                    'searched_until': end.isoformat(), 'archive_end': archive_end.isoformat() if archive_end else None,
                    'query': sorted(q), 'lead': lead, 'candidates': cands[:top]})
    return out


def main(argv):
    opts = {'--now': None, '--grace-hours': '72', '--top': '3'}
    files, i = [], 0
    while i < len(argv):
        if argv[i] in opts:
            opts[argv[i]] = argv[i + 1]; i += 2
        else:
            files.append(argv[i]); i += 1
    if not files:
        sys.exit(__doc__)
    rows = [json.loads(l) for f in files for l in open(f) if l.strip()]
    now = ts(opts['--now']) if opts['--now'] else dt.datetime.now(dt.timezone.utc)
    posts, end = load_archive({r['author'] for r in rows})
    for r in check(rows, posts, end, now, int(opts['--grace-hours']), int(opts['--top'])):
        print(json.dumps(r, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1:])
