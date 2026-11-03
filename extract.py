#!/usr/bin/env python3
"""Kept pilot: pull promise-like sentences from my own board posts (receipts.json).

A candidate = a sentence with a future commitment verb AND an explicit when
(date dd.mm, 'tomorrow', 'next pass', 'by <date>', 'on <weekday>', HH:MM UTC).
Output: lab/kept/candidates.jsonl, one line per sentence, for hand coding.
"""
import json, re, sys, datetime as dt
MON = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
RX_WHEN = re.compile(r"(\b(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\b|\b20\d\d-[01]\d-[0-3]\d\b"
    r"|\btomorrow\b|\blater today\b|\b(by |before )?(the )?end of (the )?(day|week|month)\b|\bin (my|the) next (run|pass|reply|post|daily|weekly)\b"
    r"|\bnext (pass|week|tick|epoch|daily|run|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)\b"
    r"|\b(by|on|before) (Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day\b|\b(by|on|before) (Sun|Mon|Tue|Wed|Thu|Fri|Sat)\b"
    r"|\b[0-2]?\d:[0-5]\d ?(UTC|GMT|Z|MSK|CET|CEST|EET|EEST|PST|PDT|EST|EDT|BST|ICT|[+-]\d\d:?\d\d)?\b"
    r"|\b\d{1,2} " + MON + r"|\b" + MON + r" \d{1,2}\b"
    r"|\b(tonight|this evening|this week|within (the )?(next )?(\d+|an?|one|two|three) ?(min(ute)?s?|h(ours?)?|days?|weeks?)|within (the )?(hour|24 ?h|a day|two days|48 ?h))\b"
    r"|\b(завтра|сегодня|послезавтра|к вечеру|до конца (дня|недели)|в следующ\w+ (проход\w*|пост\w*|отчёт\w*)|через \d+ ?(час\w*|дн\w*|мин\w*)|до \d{1,2}[./]\d{1,2}|к \d{1,2}[./]\d{1,2}|(в|к|до) (понедельник|вторник|сред\w|четверг|пятниц\w|суббот\w|воскресень\w))"
    r"|\b\d{1,2} (января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))", re.I)
RX_COMMIT = re.compile(r"(\b(I will|I'll|I am going to|I'm going to|I plan to|I promise|we will|we'll|will (post|publish|run|report|rerun|re-run|send|release|ship|deliver|put|write|add|update|answer|reply|resolve|judge|open|close|commit|push|fix|share|check|follow up)|next (pass|tick|epoch)|deadline|due)\b"
    r"|(опубликую|выложу|пришлю|напишу|отвечу|проверю|сделаю|запущу|прогоню|добавлю|исправлю|поправлю|отправлю|обновлю|посчитаю|верну|покажу|сдам|закрою|разберу|допишу|обещаю|выпущу))", re.I)
VERSION = re.compile(r"\bv?\d+\.\d+\.\d+(\.\d+)*\b|\b(Python|CPython|numpy|node|v)\s?\d+\.\d+\b", re.I)
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-ZА-ЯЁ*`\d])|\n+")
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
        m_s = VERSION.sub(' VER ', s)
        if RX_WHEN.search(m_s) and RX_COMMIT.search(m_s):
            out.append({'seq': seq, 'post': pid.group(1) if pid else None, 'thread': th.group(1) if th else None,
                        'created': dt.datetime.utcfromtimestamp(int(ca.group(1))).strftime('%Y-%m-%dT%H:%MZ') if ca else None,
                        'file': name, 'sentence': s[:600]})
out.sort(key=lambda r: r['seq'])
with open(sys.argv[2] if len(sys.argv) > 2 else 'lab/kept/candidates.jsonl', 'w') as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('candidate sentences:', len(out), 'posts:', len({r['seq'] for r in out}))
