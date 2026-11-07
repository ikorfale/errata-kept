"""Tests for check.py: python3 test_check.py"""
import datetime as dt
from check import check, ts

U = dt.timezone.utc
def row(seq, quote, when):
    r = {'dated': True, 'when_utc': when}
    return {'seq': seq, 'author': 'a', 'quote': quote, 'status': 'dated', 'reads': [r, r, dict(r)]}
def post(seq, root, author, t, body):
    return {'seq': seq, 'root_seq': root, 'author': author, 't': ts(t), 'body': body}

Q = 'I will publish the recovery drill table with latency numbers by 29.10'
P = [post(10, 10, 'a', '2026-10-24T00:00Z', Q),
     post(20, 99, 'a', '2026-10-28T00:00Z', 'drill latency table numbers, elsewhere'),
     post(21, 10, 'a', '2026-10-30T00:00Z', 'recovery drill table here, late'),
     post(22, 10, 'b', '2026-10-28T00:00Z', 'recovery drill table latency numbers by someone else'),
     post(23, 10, 'a', '2026-11-20T00:00Z', 'recovery drill table latency numbers, far too late')]
END_OK, NOW = ts('2026-11-10T00:00Z'), ts('2026-11-10T00:00Z')

def test_thread_first_and_bounds():
    r, = check([row(10, Q, '2026-10-29T21:00:00+00:00')], P, END_OK, NOW)
    seqs = [c['seq'] for c in r['candidates']]
    assert seqs == [21, 20], seqs                       # thread before other posts; other author and post-grace out
    assert r['candidates'][0]['vs_deadline'] == 'after' and r['candidates'][1]['vs_deadline'] == 'before'
    assert r['lead'] == 'candidate'

def test_not_due_yet():
    assert check([row(10, Q, '2026-11-20T00:00:00+00:00')], P, END_OK, NOW) == []

def test_archive_short_vs_none_found():
    q = 'I will ship the quantum ledger widget by 29.10'
    short, = check([row(10, q, '2026-10-29T21:00:00+00:00')], P, ts('2026-10-30T00:00Z'), NOW)
    full, = check([row(10, q, '2026-10-29T21:00:00+00:00')], P, END_OK, NOW)
    assert short['lead'] == 'archive-short' and full['lead'] == 'none-found'
    assert 'quantum' in full['query']                  # the search is logged

def test_undated_and_disagreeing_skipped():
    r = row(10, Q, '2026-10-29T21:00:00+00:00'); r['status'] = 'unscored'
    d = row(10, Q, '2026-10-29T21:00:00+00:00'); d['reads'][2] = {'dated': True, 'when_utc': '2026-10-30T00:00:00+00:00'}
    assert check([r], P, END_OK, NOW) == [] and check([d], P, END_OK, NOW) == []

if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
