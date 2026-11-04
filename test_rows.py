"""Synthetic tests for rows.py (no model call). Run: python3 test_rows.py"""
import datetime as dt, json, os, tempfile
import rows

U = dt.timezone.utc
C = dt.datetime(2026, 11, 4, 9, 30, tzinfo=U)  # 12:30 MSK, a Wednesday


def t(when, zone='UTC'):
    d, why = rows.to_utc(when, C, zone)
    return (d.isoformat() if d else None), why

assert t('by 05.11') == ('2026-11-06T00:00:00+00:00', 'dd.mm')
assert t('by 05.11', 'MSK') == ('2026-11-05T21:00:00+00:00', 'dd.mm')
assert t('5.11 12:00 MSK') == ('2026-11-05T09:00:00+00:00', 'dd.mm')
assert t('2026-11-07 18:00 UTC') == ('2026-11-07T18:00:00+00:00', 'iso')
assert t('UTC+03:00 6 Nov') == ('2026-11-06T21:00:00+00:00', 'month-name'), t('UTC+03:00 6 Nov')
assert t('Nov 6') == ('2026-11-07T00:00:00+00:00', 'month-name')
assert t('к 6 ноября', 'MSK') == ('2026-11-06T21:00:00+00:00', 'ru-month')
assert t('до 2 мая')[0].startswith('2027-05-03T00'), t('до 2 мая')  # >180 days back -> next year
assert t('15.03') [0].startswith('2027-03-16T00')
assert t('within 1.5 h') == ('2026-11-04T11:00:00+00:00', 'horizon')
assert t('в течение 24 ч') == ('2026-11-05T09:30:00+00:00', 'horizon')
assert t('next pass') == ('2026-11-05T09:30:00+00:00', 'next-pass')
assert t('today') == ('2026-11-05T00:00:00+00:00', 'day-word')
assert t('tomorrow', 'MSK') == ('2026-11-05T21:00:00+00:00', 'day-word')
assert t('this morning', 'MSK') == (None, 'passed')      # 12:30 MSK, morning ended 12:00
assert t('this morning') == ('2026-11-04T12:00:00+00:00', 'day-word')
assert t('сегодня в 10:00', 'MSK') == (None, 'passed')
assert t('by Friday') == ('2026-11-07T00:00:00+00:00', 'weekday')
assert t('soon') == (None, 'unparsed') and t(None) == (None, 'no-when')
assert t('v0.3 next week') == (None, 'unparsed')
assert t('31.02') == (None, 'bad-date')

P = rows.position
body = 'First line. I will post the table by 05.11. Questions welcome?\n\n— errata (errata.page)'
assert P(body, 'I will post the table by 05.11.') == {'index': 1, 'count': 3, 'closing': False}
assert P(body, 'Questions welcome?')['closing'] is True
assert P(body, 'Not in the post') == 'unknown'
assert P('Ответ ниже. Я выложу таблицу к 6 ноября.', 'я выложу таблицу к 6 ноября') == {'index': 1, 'count': 2, 'closing': True}

# build(): three reads, statuses, identity check
d = tempfile.mkdtemp()
arch = os.path.join(d, 'posts.jsonl')
open(arch, 'w').write(json.dumps({'seq': 1, 'author': 'x', 'created_at': '2026-11-04T09:30:00Z', 'body': body}) + '\n')
os.environ['KEPT_ARCHIVE'] = arch
idn = {'author': 'x', 'model': 'm', 'prompt_sha': 'p', 'code_sha': 'c'}
pr = lambda when, dated: {'quote': 'I will post the table by 05.11.', 'when': when, 'dated': dated}
def run(a, b, c, zone='UTC'):
    rs = [[dict(idn, seq=1, promises=x)] for x in (a, b, c)]
    return [r['status'] for r in rows.build(zone, rs)]
assert run([pr('by 05.11', True)], [pr('05.11', True)], [pr('by 05.11', True)]) == ['dated']
assert run([pr('by 05.11', True)], [pr('06.11', True)], [pr('by 05.11', True)]) == ['read-disagreement']
assert run([pr('by 05.11', True)], [], [pr('by 05.11', True)]) == ['read-disagreement']
assert run([pr('by 05.11', True)], [pr('05.11', False)], [pr('by 05.11', True)]) == ['read-disagreement']
assert run([pr(None, False)], [pr(None, False)], []) == ['unscored']
assert run([pr('end of the week', True)] * 1, [pr('end of the week', True)], [pr('end of the week', True)]) == ['hand-convert']
rs = [[dict(idn, seq=1, promises=[])], [dict(idn, seq=1, promises=[], code_sha='other')], [dict(idn, seq=1, promises=[])]]
try:
    list(rows.build('UTC', rs)); raise AssertionError('mixed identities merged')
except SystemExit as e:
    assert 'different reader identities' in str(e)
rs = [[dict(idn, seq=1, promises=[])], [dict(idn, seq=1, promises=None)], [dict(idn, seq=1, promises=[])]]
try:
    list(rows.build('UTC', rs)); raise AssertionError('INVALID read accepted')
except SystemExit as e:
    assert 'INVALID' in str(e)
print('test_rows: all passed')
