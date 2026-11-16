"""內容交叉比對：在 repo 根目錄執行 `python3 tools/xcheck.py`（需要 `pip install opencc-python-reimplemented`）。
檢查 RAW 詞表與 L?.txt／LP.txt 是否一一對應、格式、簡體字、例句是否用到該字、例句重複、相關字互相矛盾、字根格式。
結果印在螢幕，明細寫到目前資料夾的 xcheck_report.json。
注意：「簡體字」會有誤報（台、游、里、干、后、征、杰、据、虱⋯是正確的繁體用法）；「例句沒用到該字」多為複合字或不規則變化，需人工判斷。"""
import re, json, sys
from collections import Counter, defaultdict
from opencc import OpenCC
import os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
s2t = OpenCC('s2tw')

s = open(R + 'index.html').read()
raw = re.search(r'RAW = "(.*?)";', s, re.S).group(1)
raw = json.loads('"' + raw + '"')
rows = [l.split('|') for l in raw.strip().split('\n')]
want = Counter((r[0], r[1]) for r in rows)
heads = {r[0] for r in rows}

POS = re.compile(r'^(n|v|adj|adv|prep|conj|pron|aux|art|interj|num)\.(/(n|v|adj|adv|prep|conj|pron|aux|art|interj|num)\.)*\s')
REL = re.compile(r'^([^()]+)\((衍生字|同義字|反義字|易混淆字|片語|相關字),([^()]+)\)$')
P = defaultdict(list)
def prob(cat, w, msg): P[cat].append(f'{w}: {msg}')

E = {}   # (w,lvl) -> dict
got = Counter()
for lv in ['1', '2', '3', '4', '5', '6', 'P']:
    txt = open(R + f'L{lv}.txt', encoding='utf-8').read()
    for b in re.split(r'\n\s*\n', txt.strip()):
        ls = [x.rstrip() for x in b.split('\n') if x.strip()]
        m = re.match(r'^(.+?) \| (?:L(\d)|(P))$', ls[0])
        if not m: prob('格式', f'L{lv}', f'字頭行錯誤 {ls[0]!r}'); continue
        w = m.group(1); l = m.group(2) or 'P'
        if l != lv: prob('格式', w, f'檔案 L{lv} 裡寫成 {l}')
        got[(w, l)] += 1
        e = {'w': w, 'l': l, 'senses': [], 'ex': None, 'rel': [], 'root': None}
        for x in ls[1:]:
            if x.startswith('例:'):
                if e['ex']: prob('格式', w, '例句不只一行')
                parts = x[2:].split(' | ')
                if len(parts) != 2: prob('格式', w, f'例句行格式 {x!r}'); continue
                e['ex'] = (parts[0].strip(), parts[1].strip())
            elif x.startswith('相關:'):
                for it in x[3:].split(' / '):
                    it = it.strip(); mm = REL.match(it)
                    if not mm: prob('格式', w, f'相關字格式 {it!r}')
                    else: e['rel'].append((mm.group(1).strip(), mm.group(2), mm.group(3)))
            elif x.startswith('字根:'):
                if lv == 'P': prob('格式', w, '片語不應有字根')
                if x.count('|') != 2: prob('格式', w, f'字根行要剛好兩個 | ：{x!r}')
                else: e['root'] = [y.strip() for y in x[3:].split('|')]
            elif POS.match(x + ' '):
                if '|' not in x: prob('格式', w, f'詞義行缺 | ：{x!r}')
                e['senses'].append(x)
            else: prob('格式', w, f'無法辨識的行 {x!r}')
        if not e['senses']: prob('格式', w, '沒有詞義行')
        if not e['ex']: prob('格式', w, '沒有例句')
        if not e['rel']: prob('格式', w, '沒有相關字')
        E[(w, l)] = e
        # simplified chars
        for c in set(b):
            if '一' <= c <= '鿿' and s2t.convert(c) != c:
                prob('簡體字', w, f'{c}→{s2t.convert(c)}')

for k, n in want.items():
    if got[k] == 0: prob('對不上', k[0], f'詞表有、L{k[1]} 內容沒有')
for k, n in got.items():
    if k not in want: prob('對不上', k[0], f'L{k[1]} 有內容、詞表沒有')
    elif n > 1: prob('對不上', k[0], f'L{k[1]} 內容重複 {n} 次')

# ---------- example contains headword ----------
IRR = {}
for line in '''be am is are was were been being|have has had having|do does did done doing|go goes went gone going
see saw seen|take took taken|give gave given|come came|get got gotten|make made|know knew known|think thought
find found|tell told|become became|leave left|feel felt|bring brought|begin began begun|keep kept|hold held
write wrote written|stand stood|hear heard|let|mean meant|set|meet met|run ran|pay paid|sit sat|speak spoke spoken
lie lay lain lying|lead led|read|grow grew grown|lose lost|fall fell fallen|send sent|build built|understand understood
draw drew drawn|break broke broken|spend spent|cut|rise rose risen|drive drove driven|buy bought|wear wore worn
choose chose chosen|seek sought|throw threw thrown|catch caught|deal dealt|win won|forget forgot forgotten|sell sold
fight fought|teach taught|eat ate eaten|sing sang sung|swim swam swum|fly flew flown|drink drank drunk|ring rang rung
shoot shot|hide hid hidden|bite bit bitten|shake shook shaken|steal stole stolen|freeze froze frozen|forgive forgave forgiven
hang hung|feed fed|bleed bled|flee fled|bind bound|grind ground|wind wound|sting stung|swing swung|cling clung
dig dug|stick stuck|strike struck|spin spun|weep wept|sweep swept|sleep slept|creep crept|kneel knelt|lend lent
bend bent|beat beaten|blow blew blown|tear tore torn|swear swore sworn|bear bore born borne|ride rode ridden|arise arose arisen
sink sank sunk|shrink shrank shrunk|stink stank|spring sprang sprung|undertake undertook undertaken|withdraw withdrew withdrawn
overcome overcame|forbid forbade forbidden|mistake mistook mistaken|weave wove woven|tread trod trodden|slide slid
light lit|leap leapt|dream dreamt|burn burnt|spell spelt|spill spilt|spoil spoilt|smell smelt|learn learnt|dwell dwelt
child children|man men|woman women|foot feet|tooth teeth|mouse mice|goose geese|person people|ox oxen|leaf leaves
knife knives|wife wives|life lives|half halves|wolf wolves|shelf shelves|thief thieves|loaf loaves|crisis crises
good better best|bad worse worst|well better best|many more most|much more most|little less least|far farther further farthest furthest
analysis analyses|phenomenon phenomena|criterion criteria|medium media|bacterium bacteria|thesis theses|hypothesis hypotheses
I me my mine myself|he him his himself|she her hers herself|we us our ours ourselves|they them their theirs themselves
you your yours yourself yourselves|it its itself|who whom whose|this these|that those|a an'''.split('|'):
    ws = line.split()
    for x in ws: IRR.setdefault(x, set()).update(ws)

def forms(w):
    w = w.lower()
    out = {w} | IRR.get(w, set())
    for x in list(out):
        out |= {x + 's', x + 'es', x + 'ed', x + 'd', x + 'ing', x + 'er', x + 'est', x + 'ly', x + "'s"}
        if x.endswith('y'): out |= {x[:-1] + 'ies', x[:-1] + 'ied', x[:-1] + 'ier', x[:-1] + 'iest', x[:-1] + 'ily'}
        if x.endswith('e'): out |= {x[:-1] + 'ing', x[:-1] + 'ed', x[:-1] + 'er', x[:-1] + 'est'}
        if x.endswith('ie'): out.add(x[:-2] + 'ying')
        if re.search(r'[^aeiou][aeiou][bdgklmnprt]$', x): out |= {x + x[-1] + 'ed', x + x[-1] + 'ing', x + x[-1] + 'er', x + x[-1] + 'est'}
        if x.endswith('f'): out.add(x[:-1] + 'ves')
        if x.endswith('fe'): out.add(x[:-2] + 'ves')
        if x.endswith('ic'): out |= {x + 'ked', x + 'king'}
        if x.endswith('le'): out.add(x[:-1] + 'y')
    return out

def variants(h):
    # 'achieve(ment)' -> achieve, achievement ; 'a/an' ; 'grown-up'
    vs = set()
    for part in re.split(r'/', h):
        part = part.strip()
        m = re.match(r'^(.*?)\((.*?)\)(.*)$', part)
        if m: vs |= {m.group(1) + m.group(3), m.group(1) + m.group(2) + m.group(3)}
        else: vs.add(part)
    return {v.strip() for v in vs if v.strip()}

def toks(sent): return re.findall(r"[a-z]+(?:[-'][a-z]+)*", sent.lower())

GAP = {'sb', 'sth', "one's", 'oneself', 'be'}
def phrase_in(ph, sent):
    low = sent.lower()
    words = [x for x in ph.lower().split() if x not in GAP]
    tk = toks(sent); tset = set(tk)
    for x in words:
        if not (forms(x) & tset) and x not in low: return False
    return True

for (w, l), e in E.items():
    if not e['ex']: continue
    en, zh = e['ex']
    tset = set(toks(en)); low = en.lower()
    if l == 'P':
        if not phrase_in(w, en): prob('例句沒用到該字', w, en)
    else:
        ok = False
        for v in variants(w):
            if ' ' in v or '-' in v:
                if v.lower() in low or phrase_in(v.replace('-', ' '), en.replace('-', ' ')): ok = True
            elif forms(v) & tset or any(t.startswith(v.lower()) and len(v) >= 5 for t in tset): ok = True
        if not ok: prob('例句沒用到該字', w, en)
    if re.search(r'[一-鿿]', en): prob('例句', w, f'英文句裡有中文：{en}')
    if not re.search(r'[一-鿿]', zh): prob('例句', w, f'中文翻譯沒有中文：{zh}')
    n = len(toks(en))
    if n < 6 or n > 28: prob('例句長度', w, f'{n} 字：{en}')

ex_c = Counter(e['ex'][0] for e in E.values() if e['ex'])
for (w, l), e in E.items():
    if e['ex'] and ex_c[e['ex'][0]] > 1: prob('例句重複', w, e['ex'][0])

# ---------- related cross-consistency ----------
bykey = defaultdict(list)
for e in E.values():
    for v in variants(e['w']): bykey[v.lower()].append(e)
CONTRA = {frozenset(['同義字', '反義字'])}
for e in E.values():
    seen = set()
    for (rw, typ, zh) in e['rel']:
        if rw.lower() in {v.lower() for v in variants(e['w'])}: prob('相關字', e['w'], f'把自己列為相關字 {rw}')
        if rw.lower() in seen: prob('相關字', e['w'], f'相關字重複 {rw}')
        seen.add(rw.lower())
        if re.search(r'[一-鿿]', rw): prob('相關字', e['w'], f'相關字欄位有中文 {rw}')
        if typ == '片語' and ' ' not in rw: prob('相關字類型', e['w'], f'{rw} 標成片語但只有一個字')
        for o in bykey.get(rw.lower(), []):
            for (rw2, typ2, _) in o['rel']:
                if rw2.lower() in {v.lower() for v in variants(e['w'])} and frozenset([typ, typ2]) in CONTRA:
                    prob('相關字互相矛盾', e['w'], f'{e["w"]}→{rw} 是{typ}，但 {o["w"]}→{rw2} 是{typ2}')

# ---------- root ----------
partmean = defaultdict(Counter)
for e in E.values():
    if not e['root']: continue
    comp, expl, fam = e['root']
    parts = [x.strip() for x in comp.split(' + ')]
    for p in parts:
        mm = re.match(r'^(.+?)\((.+)\)$', p)
        if not mm: prob('字根格式', e['w'], f'部件格式 {p!r}'); continue
        partmean[mm.group(1).strip().lower()][mm.group(2)] += 1
    for f in [x.strip() for x in fam.split(',') if x.strip()]:
        if f.lower() in {v.lower() for v in variants(e['w'])}: prob('字根', e['w'], f'同字根字列了自己 {f}')
    if not fam.strip(): prob('字根', e['w'], '同字根字是空的')

json.dump({k: v for k, v in P.items()}, open('xcheck_report.json', 'w'), ensure_ascii=False, indent=1)
json.dump({k: dict(v) for k, v in partmean.items() if len(v) > 1}, open('xcheck_roots.json', 'w'), ensure_ascii=False, indent=1)
print('entries', len(E))
for k, v in P.items():
    print(f'== {k}: {len(v)}')
    for x in v[:12]: print('   ', x)

# ---------- extra: pair type mismatch, derivation sanity, zh overlap ----------
import os
X = defaultdict(list)
def norm(w): return w.lower()
for e in E.values():
    vs = {v.lower() for v in variants(e['w'])}
    for (rw, typ, zh) in e['rel']:
        tg = bykey.get(rw.lower(), [])
        for o in tg:
            for (rw2, typ2, _) in o['rel']:
                if rw2.lower() in vs and typ != typ2 and e['w'] < o['w']:
                    X['類型不一致'].append(f"{e['w']}→{rw}:{typ} / {o['w']}→{rw2}:{typ2}")
        if typ == '衍生字' and ' ' not in rw:
            a = rw.lower(); b = min(vs, key=len)
            k = 0
            while k < min(len(a), len(b)) and a[k] == b[k]: k += 1
            if k < 3 and not (b in a or a in b): X['衍生字不像衍生'].append(f"{e['w']}→{rw}({zh})")
        if typ in ('同義字', '衍生字') and tg and len(tg) == 1:
            o = tg[0]
            zhs = ''.join(s.split('|')[0] for s in o['senses'])
            cz = set(re.findall(r'[一-鿿]', zh)); oz = set(re.findall(r'[一-鿿]', zhs))
            if typ == '同義字' and cz and not (cz & oz): X['相關字中文與該字詞義無交集'].append(f"{e['w']}→{rw}({zh}) vs {zhs[:40]}")
json.dump(X, open('xcheck_extra.json', 'w'), ensure_ascii=False, indent=1)
for k, v in X.items(): print('==', k, len(v))
