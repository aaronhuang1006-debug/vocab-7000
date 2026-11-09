"""Build exams.json: which vocabulary headword appears in which past 學測 exam, which section, which sentence.
Usage: python3 exam_index.py <exam_txt_dir> <out_json>
Each exam file is named <year>.txt (pdftotext reading-order output)."""
import json, re, sys, glob, os

WORK = os.path.dirname(os.path.abspath(__file__))
recs = json.load(open(os.path.join(WORK, 'words.json')))

def keys_of(w):
    ks = set()
    for f in w.split('/'):
        f = f.strip()
        if not f: continue
        m = re.match(r'^(.+?)\(([a-z]+)\)(.*)$', f, re.I)
        if m: ks |= {(m[1] + m[3]).lower().strip(), (m[1] + m[2] + m[3]).lower().strip()}
        else: ks.add(re.sub(r'[()]', '', f).lower().strip())
    return ks

def norm(s): return re.sub(r'\s+', ' ', s.lower().replace('’', "'").replace('‘', "'")).strip()
KEYS = set()
for r in recs:
    for k in keys_of(r['w']): KEYS.add(norm(k))
MULTI = {k for k in KEYS if ' ' in k}
MAXN = max(len(k.split()) for k in MULTI)

IRREG = """arise arose arisen|awake awoke awoken|be was were been am is are|bear bore borne born|beat beaten|become became|begin began begun|bend bent|bet|bind bound|bite bit bitten|bleed bled|blow blew blown|break broke broken|breed bred|bring brought|broadcast|build built|burn burnt|burst|buy bought|catch caught|choose chose chosen|cling clung|come came|cost|creep crept|cut|deal dealt|dig dug|do did done does|draw drew drawn|dream dreamt|drink drank drunk|drive drove driven|eat ate eaten|fall fell fallen|feed fed|feel felt|fight fought|find found|flee fled|fling flung|fly flew flown flies|forbid forbade forbidden|forecast|forget forgot forgotten|forgive forgave forgiven|freeze froze frozen|get got gotten|give gave given|go went gone goes|grind ground|grow grew grown|hang hung|have had has|hear heard|hide hid hidden|hit|hold held|hurt|keep kept|kneel knelt|know knew known|lay laid|lead led|lean leant|leap leapt|learn learnt|leave left|lend lent|let|lie lay lain|light lit|lose lost|make made|mean meant|meet met|mislead misled|mistake mistook mistaken|overcome overcame|overtake overtook overtaken|pay paid|prove proven|put|quit|read|rid|ride rode ridden|ring rang rung|rise rose risen|run ran|say said|see saw seen|seek sought|sell sold|send sent|set|sew sewn|shake shook shaken|shed|shine shone|shoot shot|show shown|shrink shrank shrunk|shut|sing sang sung|sink sank sunk|sit sat|sleep slept|slide slid|sling slung|speak spoke spoken|speed sped|spell spelt|spend spent|spin spun|spit spat|split|spoil spoilt|spread|spring sprang sprung|stand stood|steal stole stolen|stick stuck|sting stung|stink stank stunk|strike struck stricken|string strung|strive strove striven|swear swore sworn|sweep swept|swell swollen|swim swam swum|swing swung|take took taken|teach taught|tear tore torn|tell told|think thought|throw threw thrown|thrust|understand understood|undertake undertook undertaken|upset|wake woke woken|wear wore worn|weave wove woven|weep wept|wet|win won|wind wound|withdraw withdrew withdrawn|withstand withstood|write wrote written|
child children|man men|woman women|person people|foot feet|tooth teeth|goose geese|mouse mice|ox oxen|knife knives|life lives|wife wives|leaf leaves|half halves|wolf wolves|shelf shelves|thief thieves|loaf loaves|calf calves|self selves|crisis crises|analysis analyses|basis bases|thesis theses|phenomenon phenomena|criterion criteria|medium media|datum data|bacterium bacteria|alumnus alumni|cactus cacti|fungus fungi|nucleus nuclei|stimulus stimuli|curriculum curricula|
good better best|bad worse worst|well better best|far farther further farthest furthest|little less least|many more most|much more most|
i me my mine myself|he him his himself|she her hers herself|it its itself|we us our ours ourselves|you your yours yourself yourselves|they them their theirs themselves"""
IRR = {}
for grp in IRREG.replace('\n', '').split('|'):
    ws = grp.split()
    if not ws: continue
    base = ws[0]
    for f in ws[1:]: IRR.setdefault(f, set()).add(base)

def lemmas(t):
    """Candidate headword keys for a lowercase token (the token itself first)."""
    out = []
    def add(x):
        if x and x in KEYS and x not in out: out.append(x)
    add(t)
    for b in IRR.get(t, ()): add(b)
    if t.endswith("'s"): add(t[:-2])
    if t.endswith('ies'): add(t[:-3] + 'y')
    if t.endswith('es'): add(t[:-2])
    if t.endswith('s') and not t.endswith('ss'): add(t[:-1])
    if t.endswith('ied'): add(t[:-3] + 'y')
    if t.endswith('ed'):
        add(t[:-2]); add(t[:-1])
        if re.search(r'(.)\1ed$', t): add(t[:-3])
    if t.endswith('ing'):
        add(t[:-3]); add(t[:-3] + 'e')
        if re.search(r'(.)\1ing$', t): add(t[:-4])
        if t.endswith('ying'): add(t[:-4] + 'ie')
    if t.endswith('ier'): add(t[:-3] + 'y')
    if t.endswith('iest'): add(t[:-4] + 'y')
    if t.endswith('er'):
        add(t[:-2]); add(t[:-1])
        if re.search(r'(.)\1er$', t): add(t[:-3])
    if t.endswith('est'):
        add(t[:-3]); add(t[:-2])
        if re.search(r'(.)\1est$', t): add(t[:-4])
    if t.endswith('ily'): add(t[:-3] + 'y')
    if t.endswith('ly') and len(t) > 4: add(t[:-2])
    return out

FUNCTION_WORDS = set('''a an the
i me my mine myself you your yours yourself yourselves he him his himself she her hers herself it its itself
we us our ours ourselves they them their theirs themselves this that these those
who whom whose which what whatever whoever someone somebody something anyone anybody anything
everyone everybody everything nobody nothing none no one each every either neither both all some any other another
be am is are was were been being do does did done have has had can could may might must shall should will would ought to used to
about above across after against along among around at before behind below beneath beside besides between beyond by
down during except for from in inside into like near of off on onto out outside over since through throughout
till until to toward towards under underneath up upon with within without
and but or nor so yet because although though if unless while whether than as once when where why how
not yes very too also there here then now just only even still more most much many few little less least
o'clock oh ok okay hello hi bye goodbye mr mrs ms miss sir'''.replace('ought to', 'ought_to').replace('used to', 'used_to').replace('no one', 'no_one').split())
FUNCTION_WORDS = {w.replace('_', ' ') for w in FUNCTION_WORDS}

SECTIONS = ['詞彙題', '綜合測驗', '文意選填', '篇章結構', '閱讀測驗', '混合題']
STOP_SECTIONS = ['中譯英', '英文作文', '非選擇題']
CJK = re.compile(r'[　-〿㐀-鿿＀-￯]')

def is_heading(line):
    s = re.sub(r'\s+', '', line)
    for name in SECTIONS + STOP_SECTIONS:
        if name in s and (re.match(r'^[一二三四五六七八九]、', s) or re.match(r'^第[壹貳參肆]部分', s)) and len(s) < 40:
            return name
    return None

def english_units(lines):
    """Join passage lines; keep question stems and grouped options as their own units."""
    units, cur = [], ''
    def flush():
        nonlocal cur
        if cur.strip(): units.append(re.sub(r'\s+', ' ', cur).strip())
        cur = ''
    for raw in lines:
        line = raw.strip().replace('\u0002', '-')
        if not line: continue
        cjk = len(CJK.findall(line)); latin = len(re.findall(r'[A-Za-z]', line))
        if cjk and cjk * 2 >= latin: continue           # instructions, headers, Chinese prompts
        if re.fullmatch(r'[-–\d\s]+', line): continue    # page numbers
        line = CJK.sub(' ', line)
        is_opt = re.match(r'^\(\s*[A-J]\s*\)', line)
        is_q = re.match(r'^\d{1,2}\s*[.-]', line) or re.match(r'^\d{1,2}-\d{1,2}\b', line)
        if is_opt:
            if not cur.strip().startswith('('): flush()
            cur += ' ' + line
            continue
        if is_q: flush()
        elif cur.strip().startswith('('): flush()
        if cur.endswith('-') and re.match(r'^[a-z]', line): cur = cur[:-1] + line
        else: cur += ' ' + line
    flush()
    sents = []
    for u in units:
        if u.startswith('('): sents.append(u); continue
        for s in re.split(r'(?<=[.?!])\s+(?=["“(]?[A-Z0-9])', u):
            s = s.strip()
            if len(re.findall(r'[A-Za-z]+', s)) >= 1: sents.append(s)
    return sents

def parse_exam(txt):
    sec, buckets = None, {}
    for line in txt.replace('\r', '').split('\n'):
        h = is_heading(line)
        if h: sec = h; continue
        if sec in SECTIONS: buckets.setdefault(sec, []).append(line)
    return {s: english_units(ls) for s, ls in buckets.items()}

def tokens(s):
    return [norm(t) for t in re.findall(r"[A-Za-z]+(?:[-'’][A-Za-z]+)*", s)]

def match_sentence(s):
    toks = tokens(s); hits = set()
    for i, t in enumerate(toks):
        for k in lemmas(t): hits.add(k)
        if '-' in t:
            for part in t.split('-'):
                for k in lemmas(part): hits.add(k)
        for n in range(2, MAXN + 1):
            if i + n > len(toks): break
            first = lemmas(toks[i]) or [toks[i]]
            rest = ' '.join(toks[i + 1:i + n])
            for f in first + [toks[i]]:
                cand = f + ' ' + rest
                if cand in MULTI: hits.add(cand)
    return hits

def build(exam_dir, out_path):
    years = sorted(int(os.path.basename(p)[:-4]) for p in glob.glob(os.path.join(exam_dir, '*.txt')) if os.path.basename(p)[:-4].isdigit())
    sentences, index = [], {}
    report = {}
    for yi, y in enumerate(years):
        parsed = parse_exam(open(os.path.join(exam_dir, f'{y}.txt'), encoding='utf-8').read())
        report[y] = {s: len(v) for s, v in parsed.items()}
        for sec, sents in parsed.items():
            si = SECTIONS.index(sec)
            for s in sents:
                sid = len(sentences); sentences.append([yi, si, s])
                for k in match_sentence(s):
                    if k not in FUNCTION_WORDS: index.setdefault(k, []).append(sid)
    used = set(i for ids in index.values() for i in ids)
    remap = {old: new for new, old in enumerate(sorted(used))}
    sentences = [sentences[i] for i in sorted(used)]
    index = {k: [remap[i] for i in ids] for k, ids in index.items()}
    skip = sorted(k for k in FUNCTION_WORDS if k in KEYS)
    data = {'years': years, 'sections': SECTIONS, 'sentences': sentences, 'index': index, 'skip': skip}
    json.dump(data, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    return data, report

if __name__ == '__main__':
    d, rep = build(sys.argv[1], sys.argv[2])
    print('years', d['years']); print(json.dumps(rep, ensure_ascii=False))
    print('sentences', len(d['sentences']), 'headwords hit', len(d['index']), 'of', len(KEYS), 'bytes', os.path.getsize(sys.argv[2]))
