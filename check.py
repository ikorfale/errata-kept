#!/usr/bin/env python3
"""Kept checker: for every dated row whose deadline has passed, list the posts that may be its receipt.

usage: check.py ROWS.jsonl [ROWS.jsonl ...] [--now ISO] [--grace-hours 72] [--top 3] [--fetch-threads]
archive: env KEPT_ARCHIVE (default archive/posts.jsonl; lines {seq, id, root_seq, author, created_at, body})
--fetch-threads: re-read each due promise's own thread from the board (env KEPT_GET, a script that GETs an API
path and prints JSON) before searching. The archive grows by new threads only, so later replies inside an old
thread are missing from it; the thread is where receipts most often are. The printed `thread_fetched` says
whether that happened.

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


def load_archive(authors, seqs=(), path=None):
    """Posts by these authors; also root seq -> root id, and root_seq for the promise seqs."""
    path = path or os.environ.get('KEPT_ARCHIVE', os.path.join(HERE, 'archive/posts.jsonl'))
    posts, last, root_ids, root_of = [], None, {}, {}
    for l in open(path):
        d = json.loads(l)
        t = ts(d['created_at'])
        last = t if last is None or t > last else last
        if d['seq'] == d.get('root_seq'):
            root_ids[d['seq']] = d['id']
        if d['seq'] in seqs:
            root_of[d['seq']] = d.get('root_seq')
        if d['author'] in authors:
            d['t'] = t
            posts.append(d)
    return posts, last, root_ids, root_of


def fetch_thread(root_id, root_seq, get):
    """All posts of one thread, paged until next_after is null. get(path) -> dict or None."""
    out, a = [], 1
    while True:
        t = get(f'/v1/posts/{root_id}?after={a}&limit=30')
        if not t or 'post' not in t:
            return None
        if a == 1:
            p = t['post']
            out.append(dict(seq=p['seq'], id=p['id'], root_seq=p['seq'], author=p.get('author'),
                            created_at=p.get('created_at'), body=p.get('body') or ''))
        for x in t['replies']['items']:
            out.append(dict(seq=x['seq'], id=x['id'], root_seq=root_seq, author=x.get('author'),
                            created_at=x.get('created_at'), body=x.get('body') or ''))
        a = t['replies'].get('next_after')
        if not a:
            return out


def refresh_threads(rows, posts, root_ids, get):
    """Merge fresh copies of the due rows' threads into posts (by seq). Returns the set of root seqs fetched."""
    have, done = {p['seq'] for p in posts}, set()
    for root in {r.get('root_seq') for r in rows if r.get('root_seq')}:
        got = fetch_thread(root_ids[root], root, get) if root in root_ids else None
        if got is None:
            continue
        done.add(root)
        for p in got:
            if p['seq'] not in have:
                p['t'] = ts(p['created_at']); posts.append(p); have.add(p['seq'])
    return done


def check(rows, posts, archive_end, now, grace_h=72, top=3, fetched=()):
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
                    'thread_fetched': root in fetched, 'query': sorted(q), 'lead': lead, 'candidates': cands[:top]})
    return out


def main(argv):
    opts = {'--now': None, '--grace-hours': '72', '--top': '3'}
    files, i, fetch = [], 0, False
    while i < len(argv):
        if argv[i] == '--fetch-threads':
            fetch = True; i += 1
        elif argv[i] in opts:
            opts[argv[i]] = argv[i + 1]; i += 2
        else:
            files.append(argv[i]); i += 1
    if not files:
        sys.exit(__doc__)
    rows = [json.loads(l) for f in files for l in open(f) if l.strip()]
    now = ts(opts['--now']) if opts['--now'] else dt.datetime.now(dt.timezone.utc)
    posts, end, root_ids, root_of = load_archive({r['author'] for r in rows}, {r['seq'] for r in rows})
    fetched = set()
    if fetch:
        import subprocess, time
        def get(path):
            time.sleep(1.2)
            r = subprocess.run([os.environ.get('KEPT_GET', 'get.sh'), path], capture_output=True, text=True)
            try:
                d = json.loads(r.stdout)
            except ValueError:
                return None
            return None if 'error' in d else d
        due = [dict(r, root_seq=root_of.get(r['seq'])) for r in rows if r.get('status') == 'dated'
               and deadline(r) and deadline(r) <= now]
        fetched = refresh_threads(due, posts, root_ids, get)
    for r in check(rows, posts, end, now, int(opts['--grace-hours']), int(opts['--top']), fetched):
        print(json.dumps(r, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1:])
