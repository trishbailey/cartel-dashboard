"""English translations without a paid API. data/translations.json maps original text (whitespace-normalised)
to an English rendering written by the Grok Bot routine itself. Usage for the routine:
  python3 pipeline/tr.py todo   > /tmp/todo.json   # untranslated non-English strings
  (translate them yourself: faithful, plain English, keep names, aliases and place names)
  python3 pipeline/tr.py add /tmp/done.json        # {"original": "english", ...}; then re-applies to all files
"""
import json, os, re, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
P = os.path.join(D, "translations.json")
N = lambda s: re.sub(r"\s+", " ", s or "").strip()
URL = re.compile(r"https?://\S+")

def load():
    return json.load(open(P, encoding="utf-8")) if os.path.exists(P) else {"note": "", "map": {}}

def lookup(text, m=None):
    m = m if m is not None else load()["map"]
    t = N(text)
    if t in m: return m[t]
    for k, v in m.items():  # breaking titles are truncated / URL-stripped originals
        if len(t) > 40 and N(URL.sub("", k)).startswith(t[:60]): return v
    return None

def fill_xfeed(x, m):
    for p in x.get("posts", []):
        if p.get("lang") != "en" and not p.get("text_en"):
            v = lookup(p["text"], m)
            if v: p["text_en"] = v
    return x

def fill_events(e, m):
    for v in e.get("events", []):
        if v.get("local") and not v.get("title_en"):
            t = lookup(v.get("title"), m)
            if t: v["title_en"] = t
    return e

def fill_breaking(b, m):
    for v in b.get("events", []):
        if v.get("lang", "es") != "en" and not v.get("title_en"):
            t = lookup(v.get("title"), m)
            if t: v["title_en"] = N(URL.sub("", t))[:220]
    return b

def apply_all():
    m = load()["map"]
    for f, fn in (("xfeed.json", fill_xfeed), ("events.json", fill_events), ("breaking.json", fill_breaking)):
        p = os.path.join(D, f)
        if os.path.exists(p):
            d = fn(json.load(open(p, encoding="utf-8")), m)
            json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def todo():
    m = load()["map"]; out = []
    x = json.load(open(os.path.join(D, "xfeed.json"), encoding="utf-8"))
    out += [N(p["text"]) for p in x["posts"] if p.get("lang") != "en" and not p.get("text_en") and not lookup(p["text"], m)]
    e = json.load(open(os.path.join(D, "events.json"), encoding="utf-8"))
    out += [N(v["title"]) for v in e["events"] if v.get("local") and not v.get("title_en") and not lookup(v["title"], m)]
    b = json.load(open(os.path.join(D, "breaking.json"), encoding="utf-8"))
    out += [N(v["title"]) for v in b["events"] if v.get("lang", "es") != "en" and not v.get("title_en") and not lookup(v["title"], m)]
    return sorted(set(out))

if __name__ == "__main__":
    if sys.argv[1:2] == ["todo"]: print(json.dumps(todo(), ensure_ascii=False, indent=1))
    elif sys.argv[1:2] == ["add"]:
        t = load(); t["map"].update({N(k): v for k, v in json.load(open(sys.argv[2], encoding="utf-8")).items()})
        json.dump(t, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1); apply_all(); print(len(todo()), "left")
    else: apply_all()
