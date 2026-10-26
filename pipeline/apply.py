"""Merge the latest shortlist (raw local-media headlines) and, if present, the day's reasoner file into data/events.json,
append arc log entries, and refresh data/baseline.json. Deterministic; no model calls."""
import json, os, glob, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
def load(p, default=None):
    p = os.path.join(D, p)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default
def save(p, o): json.dump(o, open(os.path.join(D, p), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

ev = load("events.json", {"events": [], "analysis": []})
seen = {e["url"] for e in ev["events"]}
for p in sorted(glob.glob(os.path.join(D, "shortlist/*.json")))[-2:]:
    for e in json.load(open(p))["events"]:
        if e["url"] in seen: continue
        seen.add(e["url"]); ev["events"].append({k: e[k] for k in ("title", "url", "source", "country", "local", "date", "theatre", "snippet")})
cut = (dt.date.today() - dt.timedelta(days=10)).isoformat()
ev["events"] = sorted([e for e in ev["events"] if e["date"] >= cut], key=lambda e: e["date"], reverse=True)[:250]

rfiles = sorted(glob.glob(os.path.join(D, "reasoner/*.json")))
if rfiles:
    r = json.load(open(rfiles[-1], encoding="utf-8"))
    sl = {x["id"]: x for x in json.load(open(os.path.join(D, "shortlist", r["date"] + ".json")))["events"]}
    src = {s["id"]: s for s in load("sources.json")["sources"]}
    def resolve(c):
        if c in sl: return {"title": sl[c]["title"], "url": sl[c]["url"], "source": sl[c]["source"], "date": sl[c]["date"]}
        s = src[c]; return {"title": s["title"], "url": s["url"], "source": s["publisher"], "date": s["date"]}
    an = [dict(a, date=r["date"], links=[resolve(c) for c in a["cites"]]) for a in r.get("analysis", [])]
    ev["analysis"] = an + [a for a in ev.get("analysis", []) if a["date"] != r["date"]][:40]
    for u in r.get("arc_updates", []):
        a = load(f"arcs/{u['arc']}.json")
        a["log"] = [x for x in a["log"] if x["date"] != r["date"]] + [{"date": r["date"], "text": u["text"], "links": [resolve(c) for c in u["cites"]]}]
        if u.get("current_phase"): a["current_phase"] = u["current_phase"]
        if u.get("what_happening") and a.get("storyline"): a["storyline"]["what"] = u["what_happening"][:2]; a["storyline"]["updated"] = r["date"]
        save(f"arcs/{u['arc']}.json", a)
ev["as_of"] = dt.date.today().isoformat()
try:
    import tr; tr.fill_events(ev, tr.load()["map"])
except Exception as e: print("translation fill skipped:", e)
save("events.json", ev)

base = {"as_of": ev["as_of"], "arcs": {}}
for p in sorted(glob.glob(os.path.join(D, "arcs/*.json"))):
    a = json.load(open(p)); base["arcs"][a["id"]] = {"phase": a["current_phase"], "actors": a["actors"], "turning_points": [t["date"] + " " + t["text"] for t in a["turning_points"]], "recent_log": a["log"][-5:]}
net = load("networks.json")
base["fto"] = {g["name"]: g["fto"]["date"] for g in net["groups"] if g.get("fto")}
save("baseline.json", base)
print(f"applied: {len(ev['events'])} events, {len(ev.get('analysis', []))} analyses")
