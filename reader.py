#!/usr/bin/env python3
"""Kept v0.3 front door: a model reader over every sentence of a post (EN+RU).

usage: reader.py OUT.jsonl SEQ [SEQ...]     (posts from archive/posts.jsonl)
Prompt is frozen: its sha256 is written into every output row. Model: claude-sonnet-5, no tools,
no project context, fresh empty cwd. One call per post, 4 workers, resumable (skips seqs in OUT).
"""
import hashlib, json, os, subprocess, sys, tempfile, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPT = open(os.path.join(HERE, 'reader_prompt_v03.txt')).read()
PSHA = hashlib.sha256(PROMPT.encode()).hexdigest()[:12]
CSHA = hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()[:12]  # this code, incl. date parsing
MODEL = 'claude-sonnet-5'
CLI = subprocess.run(['claude', '--version'], capture_output=True, text=True).stdout.strip()  # part of the identity (Fable 04.11)
FROZEN = ['reader.py', 'reader_prompt_v03.txt', 'rows.py', 'RULES.md']
def commit():
    """The commit sha the batch ran from, written into every row: a tag is a name that can be re-pointed, a sha is not
    (gavinagent, Clawk 04.11). Refuses when a frozen file differs from that commit, since the sha would then lie."""
    git = ['git', '-C', HERE]
    if subprocess.run(git + ['diff', '--quiet', 'HEAD', '--'] + FROZEN).returncode != 0:
        sys.exit('reader: ' + ', '.join(FROZEN) + ' must match HEAD (commit first); nothing written')
    return subprocess.run(git + ['rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()

CMD = ['claude', '-p', '--model', MODEL, '--output-format', 'text', '--tools', '',
       '--disallowedTools', 'Bash Read Grep Glob Edit Write NotebookEdit WebFetch WebSearch Agent Skill Task',
       '--exclude-dynamic-system-prompt-sections', '--strict-mcp-config', '--no-session-persistence']

def load(seqs):
    want, got = set(seqs), {}
    for l in open(os.environ.get('KEPT_ARCHIVE', os.path.join(HERE, 'archive/posts.jsonl'))):
        d = json.loads(l)
        if d['seq'] in want: got[d['seq']] = d
    return got

def ask(post, rundir):
    text = PROMPT.replace('{{AUTHOR}}', post['author']).replace('{{BODY}}', post['body'] or '')
    for attempt in (1, 2):
        r = subprocess.run(CMD, input=text, capture_output=True, text=True, cwd=rundir, timeout=600)
        out = r.stdout.strip()
        if 'Not logged in' in out:  # 03.11: an unsourced env wrote INVALID rows that looked like reads
            sys.exit('reader: claude CLI not logged in (source the agent env first); nothing written')
        s, e = out.find('['), out.rfind(']')
        try:
            return json.loads(out[s:e + 1]), out
        except Exception:
            continue
    return None, out

def main():
    out, seqs = sys.argv[1], [int(x) for x in sys.argv[2:]]
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)['seq'] for l in open(out)}
    posts = load([s for s in seqs if s not in done])
    missing = [s for s in seqs if s not in done and s not in posts]
    if missing: print('not in archive:', missing, file=sys.stderr)
    sha = commit()
    rundir = tempfile.mkdtemp(prefix='keptreader-')
    with cf.ThreadPoolExecutor(4) as ex, open(out, 'a') as f:
        futs = {ex.submit(ask, p, rundir): p for p in posts.values()}
        for fu in cf.as_completed(futs):
            p = futs[fu]; found, raw = fu.result()
            f.write(json.dumps({'seq': p['seq'], 'author': p['author'], 'model': MODEL, 'prompt_sha': PSHA, 'code_sha': CSHA, 'cli': CLI, 'commit': sha,
                                'promises': found, 'raw': None if found is not None else raw[:2000]},
                               ensure_ascii=False) + '\n'); f.flush()
            print(p['seq'], 'ok' if found is not None else 'INVALID', len(found or []), flush=True)

if __name__ == '__main__':
    main()
