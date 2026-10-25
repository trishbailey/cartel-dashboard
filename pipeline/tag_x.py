"""Tag X posts from the verified account list to dashboard regions and groups, and merge them into data/xfeed.json.

Usage: python3 pipeline/tag_x.py RAW.json [RAW.json ...]
RAW files are X search results as written by the Grok Bot routine (each has "data" posts and optional "includes.users").
Only accounts listed in data/gazetteer.json "accounts" (all tier "verified") are kept. Retweets, replies to others,
and bare reshared viral clips with no reporting are dropped. The feed keeps a rolling 7-day window, deduplicated by id.
"""
import json, os, re, sys, unicodedata, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
GAZ = json.load(open(os.path.join(D, "gazetteer.json"), encoding="utf-8"))
OUT = os.path.join(D, "xfeed.json")
WINDOW_DAYS = 7
MAXLEN = 280

def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()

def rx(alias, case=False):
    a = alias if case else norm(alias)
    return re.compile(r"(?<![\w])" + re.escape(a) + r"(?![\w])")

COUNTRY_RX = {iso: [rx(a) for a in al] for iso, al in GAZ["countries"].items()}
REG = []
for r in GAZ["regions"]:
    REG.append((r, [rx(a) for a in r["aliases"]], [re.compile(r"(?<![\w])(?:en|de|del estado de|estado de|sierra de|por|desde|hacia|a)\s+" + re.escape(norm(a)) + r"(?![\w])") for a in r["ambiguous_aliases"]]))
CASE = set(GAZ.get("case_sensitive", []))
# group aliases that are also ordinary words or nicknames need a crime word in the same post
AMBIG_G = {"Noreste", "Metros", "Ciclones", "Mencho", "Fito", "Pipo", "Barbecue", "Zetas", "Los Zetas", "El 03", "Delta 1",
           "Los Cabrera", "El Pez", "El Fresa", "Marcola", "Calarcá", "Lobos, Ecuador", "El Mayito", "El Rosarito", "El Jando",
           "Los Ninis", "El Jardinero", "Grupo Élite", "Los Aztecas", "Los Mexicles", "La Línea", "La Linea", "Los Rojos, Tamaulipas",
           "Los Escorpiones", "Los Hurtado", "Los Reyes Magos", "Templarios", "Los Fatales", "G9", "4 letras", "cuatro letras", "El Mayo",
           "El Chapo", "CDN", "CDS", "CDG", "AGC", "EGC", "EMC", "PCC", "TdA"}
CRIME = re.compile(r"(cartel|narco|sicari|crimen|criminal|banda|pandilla|grupo armado|grupo delictivo|gang|traficant|trafficking|drug|droga|fentanil|fentanyl|cocain|extorsi|secuestr|detien|captur|abati|muert|violen|desaparec|fosa|homicid|asesin|ataque|enfrentamiento|balacera|detenid|capturad|arrest|dissiden|disidencia|guerrilla|terroris|sanction|sancion|ofac|operativo|decomis|asegur|seiz)")
GRP = []
for g in GAZ["groups"]:
    for a in g["aliases"]:
        GRP.append((g["ids"], a, rx(a, a in CASE), a in AMBIG_G))
URL = re.compile(r"https?://\S+")
VIRAL = re.compile(r"(\bvideo\b|\bvideos\b|viral|captan|graban|momento (exacto )?en que|asi fue|mira |impactante|imagenes fuertes|🎥|📹|▶)")

def substance(text):
    t = URL.sub(" ", text)
    t = re.sub(r"[#@]\w+", " ", t)
    return re.findall(r"[^\W\d_]{2,}", t)

def is_bare_viral(text):
    words = substance(text)
    if len(words) < 8: return True
    return bool(VIRAL.search(norm(text))) and len(words) < 25

def tag(text, acct):
    n = norm(text)
    countries = {iso for iso, rs in COUNTRY_RX.items() if any(r.search(n) for r in rs)}
    ctx = set(countries)
    if acct.get("country"): ctx.add(acct["country"])
    regions = []
    for r, al, amb in REG:
        if any(x.search(n) for x in al) or (r["country"] in ctx and any(x.search(n) for x in amb)):
            regions.append(r)
    crime = bool(CRIME.search(n))
    groups = []
    for ids, a, r, amb in GRP:
        hit = r.search(text) if a in CASE else r.search(n)
        if hit and (not amb or crime):
            for i in ids:
                if i not in groups: groups.append(i)
    if not regions and acct.get("default_region") and (crime or groups):
        regions = [r for r, _, _ in REG if r["id"] == acct["default_region"]]
    country = regions[0]["country"] if regions else (sorted(countries)[0] if len(countries) == 1 else acct.get("country"))
    return [r["id"] for r in regions], groups, country, crime

def handle_of(p, users):
    m = re.search(r"x\.com/([^/]+)/status", p.get("url", ""))
    if m: return m.group(1)
    return users.get(p.get("author_id"), {}).get("username")

def load_raw(f):
    """Accept a plain JSON search result, or a tool-output file with the JSON embedded after a header."""
    s = open(f, encoding="utf-8").read()
    try: return json.loads(s)
    except ValueError: pass
    i = s.find('{"data"')
    if i < 0: i = s.find('{"meta"')
    return json.JSONDecoder().raw_decode(s[i:])[0] if i >= 0 else {}

def main(files):
    accts = {k.lower(): (k, v) for k, v in GAZ["accounts"].items() if v.get("tier") == "verified"}
    feed = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"posts": []}
    byid = {p["id"]: p for p in feed["posts"]}
    users_ids = {}
    added = skipped = 0
    for f in files:
        raw = load_raw(f)
        if isinstance(raw, dict) and "result" in raw and isinstance(raw["result"], (dict, str)):
            raw = raw["result"] if isinstance(raw["result"], dict) else json.loads(raw["result"])
        users = {u["id"]: u for u in raw.get("includes", {}).get("users", [])}
        for p in raw.get("data", []) or []:
            h = handle_of(p, users)
            if not h or h.lower() not in accts: skipped += 1; continue
            h, acct = accts[h.lower()]
            users_ids[p.get("author_id")] = h
            text = p.get("text", "")
            refs = {r["type"] for r in p.get("referenced_tweets", []) or []}
            if text.startswith("RT @") or "retweeted" in refs: skipped += 1; continue
            if p.get("in_reply_to_user_id") and p.get("in_reply_to_user_id") != p.get("author_id"): skipped += 1; continue
            if is_bare_viral(text): skipped += 1; continue
            regions, groups, country, crime = tag(text, acct)
            if not (regions or groups): skipped += 1; continue
            if acct["source_type"] in ("national outlet", "regional outlet", "official") and not (crime or groups): skipped += 1; continue
            t = re.sub(r"\s+", " ", text).strip()
            if len(t) > MAXLEN: t = t[:MAXLEN - 1].rstrip() + "…"
            post = {"id": p["id"], "handle": h, "url": f"https://x.com/{h}/status/{p['id']}",
                    "created_at": p["created_at"], "text": t, "lang": p.get("lang") or "und",
                    "region_ids": regions, "country": country, "group_ids": groups,
                    "tier": "verified", "source_type": acct["source_type"],
                    "label": "Official statement" if acct["source_type"] == "official" else None}
            if p["id"] not in byid: added += 1
            byid[p["id"]] = post
    now = dt.datetime.now(dt.timezone.utc)
    cut = now - dt.timedelta(days=WINDOW_DAYS)
    posts = [p for p in byid.values() if dt.datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) >= cut
             and p["handle"].lower() in accts]
    posts.sort(key=lambda p: p["created_at"], reverse=True)
    out = {"as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "window_days": WINDOW_DAYS,
           "note": "Posts from verified professional, researcher and official X accounts only, tagged to regions and groups by pipeline/tag_x.py. Official accounts are labelled 'Official statement'. Tags are keyword matches and can be wrong; open the post.",
           "accounts": sorted(k for k, v in GAZ["accounts"].items() if v.get("tier") == "verified"), "posts": posts}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"xfeed: {len(posts)} posts in window ({added} new, {skipped} skipped), {len({r for p in posts for r in p['region_ids']})} regions")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1:])
