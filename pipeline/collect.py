"""Free collection: RSS feeds + Brave News (free tier). No model calls.
Writes data/shortlist/YYYY-MM-DD.json for the Grok Bot reasoner routine (see docs/REASONER.md).
.cn hosts are blocked before any request. Secrets are read from env and never printed."""
import os, re, json, html, hashlib, datetime as dt, urllib.parse
import feedparser, requests, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = yaml.safe_load(open(os.path.join(ROOT, "config/sources.yaml"), encoding="utf-8"))
UA = {"User-Agent": "Mozilla/5.0 (compatible; cartel-dashboard/1.0; +https://github.com/trishbailey/cartel-dashboard)"}
TODAY = dt.datetime.now(dt.timezone(dt.timedelta(hours=-5))).date().isoformat()  # America/New_York-ish date

LATAM_TLDS = (".mx", ".co", ".ec", ".pe", ".ve", ".br", ".ar", ".uy", ".cl", ".bo", ".py", ".gt", ".hn", ".sv", ".ni", ".cr", ".pa", ".do", ".ht")
LATAM_HOSTS = {"infobae.com", "insightcrime.org", "elfaro.net", "riodoce.mx", "lasillavacia.com", "elpais.com"}

def blocked(url):
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return host.endswith(".cn") or host == "cn"

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()

def relevant(text):
    t = text.lower()
    return any(k in t for k in CFG["keywords"])

def theatre(text, hint=None):
    t = text.lower()
    scores = {k: sum(t.count(w) for w in ws) for k, ws in CFG["theatres"].items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else (hint or "region")

def rss():
    out = []
    for f in CFG["feeds"]:
        if blocked(f["url"]): continue
        try:
            r = requests.get(f["url"], headers=UA, timeout=20)
            d = feedparser.parse(r.content)
        except Exception as e:
            print(f"rss fail {f['name']}: {type(e).__name__}"); continue
        n = 0
        for e in d.entries[:60]:
            url = e.get("link", "")
            if not url.startswith("http") or blocked(url): continue
            title, summ = clean(e.get("title")), clean(e.get("summary"))[:400]
            if not relevant(title + " " + summ): continue
            pub = e.get("published_parsed") or e.get("updated_parsed")
            date = dt.date(*pub[:3]).isoformat() if pub else TODAY
            out.append({"source": f["name"], "country": f["country"], "local": f["local"], "title": title,
                        "url": url, "snippet": summ, "date": date, "via": "rss"})
            n += 1
        print(f"rss {f['name']}: {n}")
    return out

def brave():
    key = os.environ.get("BRAVE_API_KEY")
    if not key:
        print("no BRAVE_API_KEY; skipping Brave"); return []
    out = []
    for q in CFG["brave_queries"]:
        try:
            r = requests.get("https://api.search.brave.com/res/v1/news/search",
                             params={"q": q["q"], "count": 10, "freshness": "pd"},
                             headers={"X-Subscription-Token": key, "Accept": "application/json"}, timeout=20)
            for x in r.json().get("results", []):
                url = x.get("url", "")
                if not url.startswith("http") or blocked(url): continue
                host = ((x.get("meta_url") or {}).get("hostname", "") or "").removeprefix("www.")
                out.append({"source": host, "country": host.rsplit(".", 1)[-1].upper() if host.endswith(LATAM_TLDS) else "", "local": host.endswith(LATAM_TLDS) or host in LATAM_HOSTS,
                            "title": clean(x.get("title")), "url": url, "snippet": clean(x.get("description"))[:400],
                            "date": TODAY, "via": "brave", "hint": q["theatre"]})
        except Exception as e:
            print(f"brave fail {q['q']}: {type(e).__name__}")
    print(f"brave: {len(out)}")
    return out

def main():
    items, seen = [], set()
    for x in rss() + brave():
        k = re.sub(r"\W+", "", x["title"].lower())[:80]
        if k in seen or x["url"] in seen: continue
        seen.add(k); seen.add(x["url"])
        x["theatre"] = theatre(x["title"] + " " + x["snippet"], x.pop("hint", None))
        items.append(x)
    cutoff = (dt.date.fromisoformat(TODAY) - dt.timedelta(days=3)).isoformat()
    items = [x for x in items if x["date"] >= cutoff]
    items.sort(key=lambda x: (not x["local"], x["date"]), reverse=False)
    items.sort(key=lambda x: x["date"], reverse=True)
    for i, x in enumerate(items, 1): x["id"] = f"E{i}"
    os.makedirs(os.path.join(ROOT, "data/shortlist"), exist_ok=True)
    arcs = {os.path.basename(p)[:-5]: json.load(open(os.path.join(ROOT, "data/arcs", p))) for p in sorted(os.listdir(os.path.join(ROOT, "data/arcs")))}
    out = {"date": TODAY, "events": items[:150],
           "arc_context": {k: a.get("current_phase", "") for k, a in arcs.items()},
           "baseline": json.load(open(os.path.join(ROOT, "data/baseline.json"))) if os.path.exists(os.path.join(ROOT, "data/baseline.json")) else {}}
    json.dump(out, open(os.path.join(ROOT, f"data/shortlist/{TODAY}.json"), "w"), ensure_ascii=False, indent=1)
    print(f"shortlist {TODAY}: {len(out['events'])} events")

if __name__ == "__main__":
    main()
