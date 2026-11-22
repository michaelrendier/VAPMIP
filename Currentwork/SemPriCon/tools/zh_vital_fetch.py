#!/usr/bin/env python3
"""zh_vital_fetch.py — a small, topic-labelled, Traditional-script Mandarin corpus: English Wikipedia's Level-3 Vital Articles (about 1,000 topics in 11 top-level
categories) mapped to Chinese Wikipedia through interlanguage links, fetched in the zh-tw variant (MediaWiki's own converter), cut to paragraphs.

Politeness: one request at a time, >= GAP seconds apart, honours Retry-After on HTTP 429, backs off, and STOPS after 4 consecutive 429s (a closed door is recorded,
not pushed).  Resumable: pages already cut are skipped.  The user agent is a browser string plus a tool token (Wikimedia rate-limits unidentified browser strings).
Output (corpora/zh/vital/): pages/<n>.txt, index.tsv (en_title, zh_title, topic, subtopic, paragraphs, chars, dropped), paragraphs.tsv (topic, subtopic, zh_title, paragraph)."""
import html.parser, json, os, re, sys, time, unicodedata as ud, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); V = os.path.join(ROOT, "corpora", "zh", "vital")
UA = os.environ.get("CLAUDE_UA", "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0") + " SemPriConFetcher/1.0 (+https://github.com/michaelrendier/VAPMIP)"
GAP = float(os.environ.get("FETCH_GAP", "2.5")); last = [0.0]; strikes = [0]
CANTONESE = set("嘅唔咗喺冇佢哋啲嘢咁嚟咩")        # written Cantonese; any of these in a paragraph drops it from the Mandarin baseline


def get(url):
    while True:
        wait = last[0] + GAP - time.time()
        if wait > 0: time.sleep(wait)
        last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"}), timeout=60) as r:
                strikes[0] = 0; return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                strikes[0] += 1
                if strikes[0] >= 4: print("STOP: 4 consecutive 429s; door closed", url); sys.exit(2)
                ra = int(e.headers.get("Retry-After", "40")); print("429, waiting", ra + 5); time.sleep(ra + 5); continue
            if e.code in (404, 403): return None
            raise


class P(html.parser.HTMLParser):
    """collect the text of <p> inside .mw-parser-output, skipping references, edit links, styles, tables and notes"""
    def __init__(self): super().__init__(convert_charrefs=True); self.paras, self.cur, self.in_p, self.skip, self.depth_skip = [], [], False, 0, []
    def handle_starttag(self, tag, a):
        a = dict(a); cls = a.get("class", "")
        if tag in ("style", "script", "table", "sup") or "mw-editsection" in cls or "reference" in cls or "noprint" in cls or "hatnote" in cls: self.skip += 1; self.depth_skip.append(tag)
        elif self.skip: self.depth_skip.append(tag) if False else None
        if tag == "p" and not self.skip: self.in_p, self.cur = True, []
    def handle_endtag(self, tag):
        if self.skip and self.depth_skip and self.depth_skip[-1] == tag: self.skip -= 1; self.depth_skip.pop()
        if tag == "p" and self.in_p:
            t = re.sub(r"\s+", " ", "".join(self.cur)).strip(); self.in_p = False
            if t: self.paras.append(t)
    def handle_data(self, d):
        if self.in_p and not self.skip: self.cur.append(d)


def main():
    t = json.load(open(os.path.join(V, "en_level3_wikitext.json")))["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
    entries, h2, h3 = [], "", ""
    for line in t.split("\n"):
        m = re.match(r"^(={2,4})\s*([^=]+?)\s*\1\s*$", line)
        if m: (h2 := m.group(2)) if len(m.group(1)) == 2 else None; (h3 := m.group(2)) if len(m.group(1)) == 3 else None; continue
        if line.startswith("*") and "[[" in line:
            m = re.search(r"\[\[([^\]|#]+)", re.sub(r"\{\{[^}]*\}\}", "", line))
            if m: entries.append((h2, h3, m.group(1).strip()))
    entries = [e for e in entries if e[0] not in ("Current total",)]
    print("entries:", len(entries), "topics:", sorted({e[0] for e in entries}))
    # interlanguage links to zh, 50 titles per request
    ll = json.load(open(os.path.join(V, "langlinks_zh.json"))) if os.path.exists(os.path.join(V, "langlinks_zh.json")) else {}
    todo = [e[2] for e in entries if e[2] not in ll]
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        r = get("https://en.wikipedia.org/w/api.php?action=query&prop=langlinks&lllang=zh&lllimit=500&redirects=1&format=json&formatversion=2&titles=" + urllib.parse.quote("|".join(batch)))
        d = json.loads(r); red = {x["from"]: x["to"] for x in d["query"].get("redirects", [])}; norm = {x["from"]: x["to"] for x in d["query"].get("normalized", [])}
        found = {p["title"]: (p.get("langlinks") or [{}])[0].get("title") for p in d["query"]["pages"]}
        for b in batch: ll[b] = found.get(red.get(norm.get(b, b), norm.get(b, b)))
        json.dump(ll, open(os.path.join(V, "langlinks_zh.json"), "w"), ensure_ascii=False); print("langlinks", i + len(batch), "/", len(todo))
    os.makedirs(os.path.join(V, "pages"), exist_ok=True)
    idx = open(os.path.join(V, "index.tsv"), "a", encoding="utf-8"); seen = {l.split("\t")[0] for l in open(os.path.join(V, "index.tsv"), encoding="utf-8")} if os.path.getsize(os.path.join(V, "index.tsv")) else set()
    n = 0
    for h2_, h3_, en in entries:
        zh = ll.get(en)
        if not zh or en in seen: continue
        html_ = get("https://zh.wikipedia.org/zh-tw/" + urllib.parse.quote(zh.replace(" ", "_")))
        if not html_: continue
        body = html_.split('class="mw-parser-output"', 1)[-1]; p = P(); p.feed(body)
        keep, dropped = [], 0
        for para in p.paras:
            para = ud.normalize("NFC", para)
            if len(para) < 12 or sum(c in CANTONESE for c in para): dropped += 1; continue
            keep.append(para)
        open(os.path.join(V, "pages", f"{len(seen) + n:04d}.txt"), "w", encoding="utf-8").write("\n".join(keep) + "\n")
        with open(os.path.join(V, "paragraphs.tsv"), "a", encoding="utf-8") as f:
            for para in keep: f.write(f"{h2_}\t{h3_}\t{zh}\t{para}\n")
        idx.write(f"{en}\t{zh}\t{h2_}\t{h3_}\t{len(keep)}\t{sum(len(x) for x in keep)}\t{dropped}\n"); idx.flush(); n += 1
        if n % 25 == 0: print("pages", n)
    print("done", n)


if __name__ == "__main__":
    open(os.path.join(V, "index.tsv"), "a").close(); main()
