#!/usr/bin/env python3
"""Kept v0.3 rows: the deterministic step after the three-read batch (r3).

usage: rows.py ZONE READ1.jsonl READ2.jsonl READ3.jsonl > rows.jsonl
  ZONE: the agent's self-named zone (UTC, MSK, CET, CEST or +HH:MM); a zone written in the `when` span wins.
Posts come from archive/posts.jsonl (or $KEPT_ARCHIVE), the same file reader.py read.

Per post, candidates are the union of the three reads, matched by quote (case and whitespace folded). For each:
- `when_utc` per read: the `when` span converted by the Verdicts table of RULES.md against the post's created_at;
  None when this code cannot convert the span (then `status: hand-convert`, the hand reader converts it by the same
  table and prints the arithmetic) or when a day word had already passed at posting (`undated`);
- reads are matched by the sentence of the post their quote locates to (a quoting nit is not a new promise); a quote
  that locates nowhere is matched by folded text;
- `status`: `dated` (all three reads found it, all three say dated, all three convert to the same UTC deadline),
  `read-disagreement` (a dated flag or a deadline differs, or a read missed it while another dated it), `hand-convert`
  (a span this code does not convert: weekdays, a bare clock time, a past calendar date, two promises in one sentence),
  or `unscored` with `type` standing / conditional (a trigger and a date) / triggered / undated;
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
FULL_MONTHS = {'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
               'december', 'sept'}


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
    if w in ('май', 'мая', 'мае'):
        return 5
    for stem, n in RU_MONTHS.items():
        if stem != 'ма' and w.startswith(stem) and len(w) <= len(stem) + 3:
            return n
    return None


ZONE_TOK = re.compile(r'(?:UTC|GMT)\s?[+-]\d{1,2}(?::?\d\d)?|\b(?:UTC|GMT|MSK|CEST|CET)\b|\bМСК\b|(?<=\d)\s?Z\b', re.I)
COLON_T = re.compile(r'(?<!\d)(\d{1,2}):(\d\d)(?!\d)')
DOT_T = re.compile(r'(?<![\d.])(\d{1,2})\.(\d\d)(?!\d|\.\d)')  # a sentence's final period is not a date part


def find_time(s):
    """First clock time in s: H:MM, or H.MM when MM cannot be a month (00 or > 12) or follows 'в'/'at'.
    Returns (hour, minute, span) or None."""
    m = COLON_T.search(s)
    if m and int(m.group(1)) < 24 and int(m.group(2)) < 60:
        return int(m.group(1)), int(m.group(2)), m.span()
    for m in DOT_T.finditer(s):
        h, mi = int(m.group(1)), int(m.group(2))
        if h < 24 and mi < 60 and (m.group(2) == '00' or mi > 12 or re.search(r'(?:\bв|\bat)\s+$', s[:m.start()], re.I)):
            return h, mi, m.span()
    return None


def to_utc(when, created, zone):
    """Return (deadline datetime UTC or None, reason). created: aware UTC datetime of the post.
    None with reason unparsed/bad-date/past-date = hand-convert; passed = undated (Verdicts); no-when."""
    if not when:
        return None, 'no-when'
    s = ' '.join(when.split())
    m = re.search(r'\b(20\d\d)-(\d\d)-(\d\d)[T ](\d\d):(\d\d)(?::\d\d)?\s?(Z|[+-]\d\d:?\d\d)?', s, re.I)
    if m:  # ISO date-time; its own offset wins, else the zone rules below
        y, mo, d, h, mi, off = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), m.group(6)
        if off and off.upper() != 'Z':  # '09:00-12:00 UTC' is a range, not an offset: hand-convert anything ambiguous
            oh, omi = int(off[1:3]), int(off[-2:])
            if oh > 14 or omi % 15 or ZONE_TOK.match(s[m.end():].lstrip()) or (off[0] == '-' and (oh, omi) > (h, mi)):
                return None, 'unparsed'
        if off:
            om = 0 if off.upper() == 'Z' else zone_minutes(off)
            try:
                return dt.datetime(y, mo, d, h, mi, tzinfo=dt.timezone(dt.timedelta(minutes=om))).astimezone(dt.timezone.utc), 'iso-dt'
            except ValueError:
                return None, 'bad-date'
    zm = ZONE_TOK.search(s)
    off = zone_minutes(zone)
    if zm:
        tok = zm.group(0).strip()
        off = zone_minutes('Z' if tok.upper() == 'Z' else tok.replace(' ', '').upper().replace('МСК', 'MSK'))
        s = s[:zm.start()] + ' ' + s[zm.end():]
    low = s.lower()
    tz = dt.timezone(dt.timedelta(minutes=off))
    local = created.astimezone(tz)
    day0 = local.replace(hour=0, minute=0, second=0, microsecond=0)
    tm = find_time(s)
    s_nt = s[:tm[2][0]] + ' ' + s[tm[2][1]:] if tm else s  # dates are searched with the time blanked out

    def at(day):
        if tm:
            return (day + dt.timedelta(hours=tm[0], minutes=tm[1])).astimezone(dt.timezone.utc)
        return (day + dt.timedelta(days=1)).astimezone(dt.timezone.utc)  # a date without a time = 24:00 that day

    def dated(y, mon, d, why):
        try:
            c = dt.datetime(y if y else local.year, mon, d, tzinfo=tz)
        except ValueError:
            return None, 'bad-date'
        if not y and c < day0:
            if (day0 - c).days > 183:
                c = c.replace(year=c.year + 1)
            else:
                return None, 'past-date'  # a past calendar date: the hand reader decides
        return at(c), why

    m = re.search(r'(?:within|in|в течение|через)\s+(\d+(?:[.,]\d+)?)\s*(h|hours?|ч|час\w*|d|days?|дн\w*|сут\w*)\b', low)
    if m:
        n = float(m.group(1).replace(',', '.'))
        hours = n if m.group(2)[0] in 'hч' else 24 * n
        return created + dt.timedelta(hours=hours), 'horizon'
    m = re.search(r'\b(20\d\d)-(\d\d)-(\d\d)\b', s_nt)
    if m:
        return dated(int(m.group(1)), int(m.group(2)), int(m.group(3)), 'iso')
    m = re.search(r'(?<![\w.])(\d{1,2})\.(\d\d|\d(?=\.\d\d))(?:\.(20\d\d|\d\d))?(?![\d:])', s_nt)  # 05.11, 5.11, 5.1.27; not v0.3
    if m:
        y = int(m.group(3)) if m.group(3) else None
        if y and y < 100:
            y += 2000
        return dated(y, int(m.group(2)), int(m.group(1)), 'dd.mm')
    for m in re.finditer(r'\b(\d{1,2})\s+([A-Za-z]{3,9})\b|\b([A-Za-z]{3,9})\.?\s+(\d{1,2})\b', s_nt):
        d, word = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(3))
        w = word.lower()
        if w in FULL_MONTHS or (len(w) == 3 and w in MONTHS):  # 'Decision 5' is not 5 December
            return dated(None, MONTHS[w[:3]], int(d), 'month-name')
    for m in re.finditer(r'\b(\d{1,2})\s+([а-яё]+)', s_nt.lower()):
        if ru_month(m.group(2)):
            return dated(None, ru_month(m.group(2)), int(m.group(1)), 'ru-month')
    if re.search(r'\bnext pass\b|\bследующ\w* проход', low):
        return created + dt.timedelta(hours=24), 'next-pass'
    tomorrow = re.search(r'\btomorrow\b|\bзавтра\b', low)
    morning = re.search(r'\bthis morning\b|\bутром\b', low)
    afternoon = re.search(r'\bthis afternoon\b|\bднём\b|\bднем\b', low)
    today = re.search(r'\btoday\b|\btonight\b|\bсегодня\b', low)
    part = re.search(r'\b(?:morning|afternoon|evening|утром|днём|днем|вечером)\b', low)
    if (tomorrow and part) or (part and not (morning or afternoon)):
        return None, 'unparsed'  # 'tomorrow morning', 'this evening': not in the Verdicts table
    if tomorrow or morning or afternoon or today:
        plus = 1 if tomorrow else 0
        if tm:
            d = day0 + dt.timedelta(days=plus, hours=tm[0], minutes=tm[1])
        else:
            d = day0 + dt.timedelta(days=plus, hours=12 if morning else 18 if afternoon else 24)
        if d <= local:
            return None, 'passed'
        return d.astimezone(dt.timezone.utc), 'day-word'
    return None, 'unparsed'  # weekdays, "end of the week", a bare clock time: the hand reader converts


SENT = re.compile(r'(?<=[.!?…])["»”)]?\s+(?=[\"«“(A-ZА-ЯЁ0-9@#*-])|\n+')
QUOTES = str.maketrans({'’': "'", '‘': "'", '`': "'", '“': '"', '”': '"', '«': '"', '»': '"', '–': '-', '—': '-'})


def fold(t):
    """Case, whitespace, curly quotes, dashes and markdown emphasis folded (a quoting nit is not a different sentence)."""
    t = (t or '').translate(QUOTES)
    t = re.sub(r'[*_]{1,3}', '', t)
    return ' '.join(t.split()).lower().strip(' .!?…"\'')


def is_signature(line, author):
    l = line.strip()
    if not l:
        return True
    if re.match(r'^(-|—|–|~)\s*\S', l) and len(l) <= 120:
        return True
    if len(l) <= 120 and (author and author.lower() in l.lower()) and not re.search(r'[.!?]\s', l):
        return True
    return bool(re.fullmatch(r'(\S+://\S+|\S+@\S+|[|·•,\s])+', l))  # a line of links / addresses only


def sentences(body, author=''):
    lines = (body or '').rstrip().split('\n')
    while lines and is_signature(lines[-1], author):
        lines.pop()  # signature lines and trailing blanks sit after the closing sentence
    return [x for x in (y.strip() for y in SENT.split('\n'.join(lines))) if x]


def locate(sents, quote):
    """Index of the sentence the quote comes from, or None. A quote may be a clause of the sentence or span it."""
    q = fold(quote)
    if not q:
        return None
    for i, x in enumerate(sents):
        fx = fold(x)
        if q in fx or (len(fx) > 20 and fx in q):
            return i
    return None


def position(body, quote, author=''):
    sents = sentences(body, author)
    i = locate(sents, quote)
    if i is None:
        return 'unknown'
    return {'index': i, 'count': len(sents), 'closing': i == len(sents) - 1}


def load_posts(seqs):
    got = {}
    for l in open(os.environ.get('KEPT_ARCHIVE', os.path.join(HERE, 'archive/posts.jsonl'))):
        d = json.loads(l)
        if d['seq'] in seqs:
            got[d['seq']] = d
    return got


HAND = ('unparsed', 'bad-date', 'past-date', 'no-when')


def build(zone, reads):
    """reads: three lists of reader.py rows. Yields row dicts.
    Candidates from the three reads are the same promise when they locate to the same sentence of the post (else, when
    a quote cannot be located, the same folded quote)."""
    by = [{r['seq']: r for r in rd} for rd in reads]
    ident = {(r['prompt_sha'], r.get('code_sha'), r['model'], r.get('cli'), r.get('commit')) for rd in reads for r in rd}
    if len(ident) != 1:
        raise SystemExit(f'reads made under different reader identities, never merged: {sorted(map(str, ident))}')
    ident = ident.pop()
    seqs = sorted(set().union(*[set(b) for b in by]))
    posts = load_posts(set(seqs))
    for seq in seqs:
        post = posts.get(seq)
        if post is None:
            raise SystemExit(f'seq {seq} not in archive')
        ca = post['created_at']  # the board archive stores epoch seconds; fixtures use ISO strings
        created = (dt.datetime.fromtimestamp(ca, dt.timezone.utc) if isinstance(ca, (int, float))
                   else dt.datetime.fromisoformat(ca.replace('Z', '+00:00')).astimezone(dt.timezone.utc))
        sents = sentences(post['body'], post['author'])
        cands = {}
        for k, b in enumerate(by):
            row = b.get(seq)
            if row is None or row.get('promises') is None:
                raise SystemExit(f'seq {seq}: read {k + 1} missing or INVALID; the batch is incomplete')
            for p in row['promises']:
                i = locate(sents, p.get('quote'))
                key = ('s', i) if i is not None else ('q', fold(p.get('quote')))
                c = cands.setdefault(key, {'quote': p.get('quote'), 'reads': [None, None, None], 'multi': False})
                if c['reads'][k] is not None:
                    c['multi'] = True  # one read gave two promises in one sentence: the hand reader splits them
                    continue
                c['reads'][k] = p
        for key, c in cands.items():
            per = []
            for p in c['reads']:
                if p is None:
                    per.append(None); continue
                d, why = to_utc(p.get('when'), created, zone)
                per.append({'dated': bool(p.get('dated')), 'when': p.get('when'), 'when_utc': d.isoformat() if d else None,
                            'conv': why, 'trigger': p.get('trigger'), 'standing': bool(p.get('standing'))})
            got = [x for x in per if x]
            flags = [x['dated'] if x else None for x in per]
            if c['multi']:
                status, typ = 'hand-convert', None  # two promises in one sentence: before any flag check (RULES)
            elif any(x['standing'] for x in got):
                status, typ = 'unscored', 'standing'
            elif any(x['trigger'] for x in got):
                status, typ = 'unscored', 'conditional' if any(flags) else 'triggered'  # RULES: dated conditionals are unscored
            elif not any(flags):
                status, typ = 'unscored', 'undated'
            elif flags != [True, True, True]:
                status, typ = 'read-disagreement', None
            elif all(x['conv'] == 'passed' for x in per):
                status, typ = 'unscored', 'undated'  # a day word already past at posting (Verdicts)
            elif any(x['conv'] in HAND for x in per):
                status, typ = 'hand-convert', None
            elif len({x['when_utc'] for x in per}) != 1:
                status, typ = 'read-disagreement', None
            else:
                status, typ = 'dated', None
            yield {'seq': seq, 'author': post['author'], 'created_at': created.isoformat(), 'quote': c['quote'],
                   'status': status, 'type': typ, 'multi': c['multi'], 'reads': per,
                   'position': ({'index': key[1], 'count': len(sents), 'closing': key[1] == len(sents) - 1}
                                if key[0] == 's' else 'unknown'),
                   'zone': zone, 'prompt_sha': ident[0], 'code_sha': ident[1], 'model': ident[2], 'cli': ident[3], 'commit': ident[4],
                   'rows_sha': RSHA}


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    zone_minutes(sys.argv[1])
    reads = [[json.loads(l) for l in open(p) if l.strip()] for p in sys.argv[2:5]]
    for r in build(sys.argv[1], reads):
        print(json.dumps(r, ensure_ascii=False))


if __name__ == '__main__':
    main()
