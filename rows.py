#!/usr/bin/env python3
"""Kept v0.3 rows: the deterministic step after the three-read batch (r3).

usage: rows.py ZONE READ1.jsonl READ2.jsonl READ3.jsonl > rows.jsonl
  ZONE: the agent's self-named zone (UTC, MSK, CET, CEST or +HH:MM); a zone written in the `when` span wins.
Posts come from archive/posts.jsonl (or $KEPT_ARCHIVE), the same file reader.py read.

Per post, candidates are the union of the three reads, matched by quote (case and whitespace folded). For each:
- `when_utc` per read: the `when` span converted by the Verdicts table of RULES.md against the post's created_at;
  None when this code cannot convert the span (then `status: hand-convert`, the hand reader converts it by the same
  table and prints the arithmetic) or when a day word had already passed at posting (`undated`);
- `status`: `dated` (all three reads found it, all three say dated, all three convert to the same UTC deadline),
  `read-disagreement` (a dated flag or a deadline differs, or a read missed it while another dated it), `hand-convert`,
  or `unscored` (no read dated it);
- `position`: sentence index (0-based), sentence count, `closing` (last sentence before a signature line), or
  `unknown` when the quote cannot be located in the body. Never a guess.
Every row carries rows_sha (sha256 of this file, 12 hex), next to reader.py's prompt_sha, code_sha and model.
"""
import datetime as dt, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RSHA = hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()[:12]
ZONES = {'UTC': 0, 'GMT': 0, 'Z': 0, 'MSK': 180, 'МСК': 180, 'CET': 60, 'CEST': 120}
MONTHS = {m: i + 1 for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])}
RU_MONTHS = {s: i + 1 for i, s in enumerate(['январ', 'феврал', 'март', 'апрел', 'ма', 'июн', 'июл', 'август', 'сентябр',
                                            'октябр', 'ноябр', 'декабр'])}
WEEKDAYS = {w: i for i, w in enumerate(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])}


def zone_minutes(z):
    z = (z or 'UTC').strip()
    if z.upper() in ZONES or z in ZONES:
        return ZONES.get(z.upper(), ZONES.get(z))
    m = re.fullmatch(r'(?:UTC|GMT)?([+-])(\d{1,2})(?::?(\d\d))?', z)
    if m:
        return (1 if m.group(1) == '+' else -1) * (int(m.group(2)) * 60 + int(m.group(3) or 0))
    raise ValueError(f'unknown zone {z!r}')


def ru_month(word):
    w = word.lower()
    if w.startswith('ма') and not w.startswith('мар'):
        return 5
    for stem, n in RU_MONTHS.items():
        if stem != 'ма' and w.startswith(stem):
            return n
    return None


def to_utc(when, created, zone):
    """Return (deadline datetime UTC or None, reason). created: aware UTC datetime of the post."""
    if not when:
        return None, 'no-when'
    s = ' '.join(when.split())
    low = s.lower()
    zm = re.search(r'(?:UTC|GMT)\s?[+-]\d{1,2}(?::?\d\d)?|\b(UTC|GMT|MSK|CEST|CET)\b|МСК|\b\d{1,2}:\d\d\s?Z\b', s)
    off = zone_minutes(zone)
    if zm:
        tok = zm.group(0)
        tok = 'Z' if re.search(r'\d\s?Z$', tok) else tok.replace(' ', '')
        off = zone_minutes(tok)
    tz = dt.timezone(dt.timedelta(minutes=off))
    local = created.astimezone(tz)
    day0 = local.replace(hour=0, minute=0, second=0, microsecond=0)
    tm = re.search(r'\b(\d{1,2}):(\d\d)\b', s[:zm.start()] + ' ' + s[zm.end():] if zm else s)

    def at(day, default_end=True):
        if tm:
            return (day + dt.timedelta(hours=int(tm.group(1)), minutes=int(tm.group(2)))).astimezone(dt.timezone.utc)
        return (day + dt.timedelta(days=1)).astimezone(dt.timezone.utc)  # a date without a time = 24:00 that day

    def year_for(mon, d):
        y = local.year
        try:
            c = dt.datetime(y, mon, d, tzinfo=tz)
        except ValueError:
            return None
        return y + 1 if (day0 - c).days > 180 else y

    m = re.search(r'(?:within|in|в течение|через)\s+(\d+(?:[.,]\d+)?)\s*(h|hours?|ч|час\w*|d|days?|дн\w*|сут\w*)\b', low)
    if m:
        n = float(m.group(1).replace(',', '.'))
        hours = n if m.group(2)[0] in 'hч' else 24 * n
        return created + dt.timedelta(hours=hours), 'horizon'
    m = re.search(r'\b(20\d\d)-(\d\d)-(\d\d)', s)
    if m:
        return at(dt.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=tz)), 'iso'
    m = re.search(r'\b(\d{1,2})\.(\d{1,2})(?:\.(20\d\d|\d\d))?\b(?!:)', s)
    if m and not (tm and m.start() == tm.start()):
        d, mon = int(m.group(1)), int(m.group(2))
        y = int(m.group(3)) if m.group(3) else year_for(mon, d)
        if y and y < 100:
            y += 2000
        try:
            return at(dt.datetime(y, mon, d, tzinfo=tz)), 'dd.mm'
        except (ValueError, TypeError):
            return None, 'bad-date'
    m = re.search(r'\b(\d{1,2})\s+([A-Za-z]{3,9})\b|\b([A-Za-z]{3,9})\.?\s+(\d{1,2})\b', s)
    if m:
        d, word = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(3))
        mon = MONTHS.get(word[:3].lower())
        if mon:
            y = year_for(mon, int(d))
            if y:
                return at(dt.datetime(y, mon, int(d), tzinfo=tz)), 'month-name'
    m = re.search(r'\b(\d{1,2})\s+([а-яё]+)', low)
    if m and ru_month(m.group(2)):
        mon, d = ru_month(m.group(2)), int(m.group(1))
        y = year_for(mon, d)
        if y:
            return at(dt.datetime(y, mon, d, tzinfo=tz)), 'ru-month'
    if re.search(r'\bnext pass\b|следующ\w* проход', low):
        return created + dt.timedelta(hours=24), 'next-pass'
    for words, hour, plus in ((r'\btomorrow\b|завтра', 24, 1), (r'\btonight\b|\btoday\b|сегодня', 24, 0),
                              (r'\bthis morning\b|утром', 12, 0), (r'\bthis afternoon\b|днём|днем', 18, 0)):
        if re.search(words, low):
            if tm:
                d = (day0 + dt.timedelta(days=plus, hours=int(tm.group(1)), minutes=int(tm.group(2))))
            else:
                d = day0 + dt.timedelta(days=plus, hours=hour)
            if d <= local:
                return None, 'passed'
            return d.astimezone(dt.timezone.utc), 'day-word'
    for w, i in WEEKDAYS.items():
        if re.search(r'\b' + w + r'\b', low):
            return at(day0 + dt.timedelta(days=(i - local.weekday()) % 7)), 'weekday'
    return None, 'unparsed'


SENT = re.compile(r'(?<=[.!?…])["»”)]?\s+(?=[\"«“(A-ZА-ЯЁ0-9@#*-])|\n+')
SIG = re.compile(r'^\s*(—|--|~)\s*\S|^\s*(errata|fable-terminal)\b.{0,60}$', re.I)


def fold(t):
    return ' '.join((t or '').split()).lower().strip(' .!?…"«»“”')


def position(body, quote):
    lines = (body or '').rstrip().split('\n')
    while lines and (not lines[-1].strip() or SIG.match(lines[-1])):
        lines.pop()  # signature lines and trailing blanks sit after the closing sentence
    sents = [x for x in (y.strip() for y in SENT.split('\n'.join(lines))) if x]
    q = fold(quote)
    if not q:
        return 'unknown'
    hits = [i for i, x in enumerate(sents) if q in fold(x) or (len(fold(x)) > 20 and fold(x) in q)]
    if not hits:
        return 'unknown'
    i = hits[0]
    return {'index': i, 'count': len(sents), 'closing': i == len(sents) - 1}


def load_posts(seqs):
    got = {}
    for l in open(os.environ.get('KEPT_ARCHIVE', os.path.join(HERE, 'archive/posts.jsonl'))):
        d = json.loads(l)
        if d['seq'] in seqs:
            got[d['seq']] = d
    return got


def build(zone, reads):
    """reads: three lists of reader.py rows. Yields row dicts."""
    by = [{r['seq']: r for r in rd} for rd in reads]
    ident = {(r['prompt_sha'], r.get('code_sha'), r['model']) for rd in reads for r in rd}
    if len(ident) != 1:
        raise SystemExit(f'reads made under different reader identities, never merged: {sorted(map(str, ident))}')
    ident = ident.pop()
    seqs = sorted(set().union(*[set(b) for b in by]))
    posts = load_posts(set(seqs))
    for seq in seqs:
        post = posts.get(seq)
        if post is None:
            raise SystemExit(f'seq {seq} not in archive')
        created = dt.datetime.fromisoformat(post['created_at'].replace('Z', '+00:00')).astimezone(dt.timezone.utc)
        cands = {}
        for k, b in enumerate(by):
            row = b.get(seq)
            if row is None or row.get('promises') is None:
                raise SystemExit(f'seq {seq}: read {k + 1} missing or INVALID; the batch is incomplete')
            for p in row['promises']:
                c = cands.setdefault(fold(p.get('quote')), {'quote': p.get('quote'), 'reads': [None, None, None]})
                c['reads'][k] = p
        for c in cands.values():
            per = []
            for p in c['reads']:
                if p is None:
                    per.append(None); continue
                d, why = to_utc(p.get('when'), created, zone)
                per.append({'dated': bool(p.get('dated')), 'when': p.get('when'), 'when_utc': d.isoformat() if d else None,
                            'conv': why, 'trigger': p.get('trigger'), 'standing': bool(p.get('standing'))})
            flags = [x['dated'] if x else None for x in per]
            if not any(flags):
                status = 'unscored'
            elif flags != [True, True, True]:
                status = 'read-disagreement'
            elif all(x['conv'] == 'passed' for x in per):
                status = 'unscored'  # a day word already past at posting = undated (Verdicts)
            elif any(x['conv'] == 'unparsed' for x in per):
                status = 'hand-convert'
            elif len({x['when_utc'] for x in per}) != 1 or per[0]['when_utc'] is None:
                status = 'read-disagreement'
            else:
                status = 'dated'
            yield {'seq': seq, 'author': post['author'], 'created_at': created.isoformat(), 'quote': c['quote'],
                   'status': status, 'reads': per, 'position': position(post['body'], c['quote']), 'zone': zone,
                   'prompt_sha': ident[0], 'code_sha': ident[1], 'model': ident[2], 'rows_sha': RSHA}


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    zone_minutes(sys.argv[1])
    reads = [[json.loads(l) for l in open(p) if l.strip()] for p in sys.argv[2:5]]
    for r in build(sys.argv[1], reads):
        print(json.dumps(r, ensure_ascii=False))


if __name__ == '__main__':
    main()
