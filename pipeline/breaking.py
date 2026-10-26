"""Build data/breaking.json: cluster verified X posts (data/xfeed.json) and RSS/Brave headlines (data/events.json)
from professional outlets (data/outlets.json) into events, and give each a status:
  confirmed           two or more independent outlets, or an official body plus at least one outlet
  single_source       one outlet so far
  official_claim_only only a government account or site
Deterministic: same inputs give the same output. No model calls. Events are kept for 48 hours; an event's status is
recomputed on every run, so it upgrades as more sources arrive.
Usage: python3 pipeline/breaking.py
"""
import json, os, re, hashlib, datetime as dt, urllib.parse, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tag_x
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
KEEP_H = 48
JOIN_H = 12
CC = {"MX": "MEX", "CO": "COL", "EC": "ECU", "VE": "VEN", "PE": "PER", "BR": "BRA", "GT": "GTM", "HN": "HND", "SV": "SLV",
      "HT": "HTI", "CR": "CRI", "PA": "PAN", "BO": "BOL", "CL": "CHL", "AR": "ARG", "UY": "URY", "PY": "PRY", "US": None}
STOP = set(tag_x.norm(w) for w in """de la el los las en y a que del se por un una con para al su sus es fue son como mas más tras sobre entre
 este esta estos estas lo le les ya no si o u ha han hay ser sin desde hasta durante contra the of and in to a for on by with from at is are was
 were be has have this that it its after over into new nuevo nueva dos tres cuatro cinco seis hoy ayer este semana mexico méxico colombia ecuador
 venezuela según dijo informa informó reporta reportan presunto presuntos presunta http https co""".split())

def toks(s):
    s = tag_x.URL.sub(" ", s)
    return {w for w in re.findall(r"[a-z0-9ñ]{4,}", tag_x.norm(s)) if w not in STOP}

def outlet_index():
    o = json.load(open(os.path.join(D, "outlets.json"), encoding="utf-8"))["outlets"]
    by_x = {h.lower(): x for x in o for h in x["x"]}
    return o, by_x

def match_outlet(outlets, source, url):
    s = (source or "").strip().lower()
    host = (urllib.parse.urlparse(url or "").hostname or "").lower()
    if host.endswith(".cn"): return None
    for x in outlets:
        for m in x["match"]:
            if "." in m:
                if host == m or host.endswith("." + m) or s == m: return x
            elif s == m: return x
    return None

def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))

def items(now):
    outlets, by_x = outlet_index()
    out = []
    xf = json.load(open(os.path.join(D, "xfeed.json"), encoding="utf-8"))
    for p in xf["posts"]:
        o = by_x.get(p["handle"].lower())
        if not o or p.get("tier") != "verified": continue
        out.append({"t": ts(p["created_at"]), "precise": True, "outlet": o, "url": p["url"], "title": p["text"], "title_en": p.get("text_en"), "lang": p.get("lang", "es"),
                    "via": "X @" + p["handle"], "regions": p["region_ids"], "groups": p["group_ids"], "country": p.get("country")})
    ev = json.load(open(os.path.join(D, "events.json"), encoding="utf-8"))
    acct = {"country": None}
    for e in ev["events"]:
        o = match_outlet(outlets, e.get("source"), e.get("url"))
        if not o or not e.get("date"): continue
        text = (e.get("title") or "") + ". " + (e.get("snippet") or "")
        acct["country"] = CC.get(e.get("country"))
        r, g, c, crime = tag_x.tag(text, acct)
        if not (r or g): continue
        t = dt.datetime.fromisoformat(e["date"]).replace(hour=12, tzinfo=dt.timezone.utc)
        out.append({"t": t, "precise": False, "outlet": o, "url": e["url"], "title": e.get("title") or "", "title_en": e.get("title_en"), "lang": "es" if e.get("local") else "en", "via": "headline",
                    "regions": r, "groups": g, "country": c})
    cut = now - dt.timedelta(hours=KEEP_H)
    out = [i for i in out if i["t"] >= cut and i["t"] <= now + dt.timedelta(hours=1)]
    for i in out: i["tok"] = toks(i["title"])
    out.sort(key=lambda i: (i["t"], i["url"]))
    return out

def similar(a, b):
    gap = abs((a["t"] - b["t"]).total_seconds()) / 3600
    if gap > (36 if not (a["precise"] and b["precise"]) else JOIN_H): return False
    sr = set(a["regions"]) & set(b["regions"]); sg = set(a["groups"]) & set(b["groups"])
    if a["regions"] and b["regions"] and not sr: return False
    if not sr and not sg: return False
    shared = a["tok"] & b["tok"]
    jac = len(shared) / max(1, len(a["tok"] | b["tok"]))
    need = 4 if (a["precise"] and b["precise"]) else 5
    return jac >= 0.18 or len(shared) >= need or (sr and sg and len(shared) >= 3)

def cluster(its):
    events = []
    for i in its:
        best = None
        for e in events:
            if any(similar(i, m) for m in e):
                best = e; break
        if best is None: events.append([i])
        else: best.append(i)
    return events

def status(members):
    outs = {m["outlet"]["id"] for m in members if m["outlet"]["kind"] == "outlet"}
    offs = {m["outlet"]["id"] for m in members if m["outlet"]["kind"] == "official"}
    if len(outs) >= 2 or (offs and outs): return "confirmed"
    if outs: return "single_source"
    return "official_claim_only"

def main():
    now = dt.datetime.now(dt.timezone.utc)
    evs = []
    for ms in cluster(items(now)):
        ms.sort(key=lambda m: (m["t"], not m["precise"]))
        first = ms[0]
        lead = next((m for m in ms if m["outlet"]["kind"] == "outlet"), first)
        regions = sorted({r for m in ms for r in m["regions"]}, key=lambda r: -sum(r in m["regions"] for m in ms))[:4]
        groups = sorted({g for m in ms for g in m["groups"]}, key=lambda g: -sum(g in m["groups"] for m in ms))[:4]
        seen, sources = set(), []
        for m in ms:
            if m["url"] in seen: continue
            seen.add(m["url"])
            sources.append({"outlet": m["outlet"]["id"], "name": m["outlet"]["name"], "kind": m["outlet"]["kind"], "via": m["via"],
                            "url": m["url"], "time": m["t"].strftime("%Y-%m-%dT%H:%M:%SZ"), "time_precision": "minute" if m["precise"] else "day"})
        st = status(ms)
        eid = hashlib.sha1(first["url"].encode()).hexdigest()[:10]
        evs.append({"id": eid, "status": st, "title": re.sub(r"\s+", " ", tag_x.URL.sub("", lead["title"])).strip()[:200], "lang": "en" if lead.get("lang") == "en" else "es", "title_en": re.sub(r"\s+", " ", tag_x.URL.sub("", lead.get("title_en") or "")).strip()[:220] or None,
                    "first_report": first["t"].strftime("%Y-%m-%dT%H:%M:%SZ"), "first_report_precision": "minute" if first["precise"] else "day",
                    "first_source": first["outlet"]["name"], "region_ids": regions, "country": first["country"], "group_ids": groups,
                    "outlets": sorted({s["name"] for s in sources}), "sources": sources})
    rank = {"confirmed": 0, "single_source": 1, "official_claim_only": 2}
    evs.sort(key=lambda e: (max(s["time"] for s in e["sources"])), reverse=True)
    try:
        import tr; tr.fill_breaking({"events": evs}, tr.load()["map"])
    except Exception as e: print("translation fill skipped:", e)
    json.dump({"as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "keep_hours": KEEP_H,
               "rules": {"confirmed": "two or more independent professional outlets, or an official body plus at least one outlet",
                         "single_source": "one professional outlet so far", "official_claim_only": "only a government account or site says it"},
               "note": "Built by pipeline/breaking.py from verified X accounts and professional-outlet headlines only (data/outlets.json). Grouping is by place, group, time and shared keywords and can be wrong; open the sources.",
               "events": evs}, open(os.path.join(D, "breaking.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    c = {k: sum(e["status"] == k for e in evs) for k in rank}
    print(f"breaking: {len(evs)} events ({c['confirmed']} confirmed, {c['single_source']} single source, {c['official_claim_only']} official claim only)")

if __name__ == "__main__":
    main()
