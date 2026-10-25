"""Validator: every route, edge and claim must cite a registered source with a URL. No .cn. Sankey must balance.
Also validates data/reasoner/*.json written by the Grok Bot routine. Exit 1 on any error."""
import json, os, sys, glob, re, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
errs = []
def err(m): errs.append(m)
def load(p): return json.load(open(os.path.join(D, p), encoding="utf-8"))
def is_cn(u): return (urllib.parse.urlparse(u).hostname or "").lower().endswith(".cn")

src = {s["id"]: s for s in load("sources.json")["sources"]}
for s in src.values():
    for k in ("title", "publisher", "url", "date"):
        if not s.get(k): err(f"source {s.get('id')} missing {k}")
    if not s.get("url", "").startswith("https://"): err(f"source {s['id']} url not https")
    if is_cn(s.get("url", "")): err(f"source {s['id']} is .cn")

def cites(obj, where):
    c = obj.get("cites")
    if not c: err(f"{where}: no cites"); return
    for x in c:
        if x not in src: err(f"{where}: unknown cite {x}")

for f in load("routes.geojson")["features"]: cites(f["properties"], f"route {f['properties']['id']}")
cr = load("crossings.geojson")
for f in cr["features"]: cites(f["properties"], f"crossing {f['properties']['id']}")
cites(cr["stats"], "crossing stats")

m = load("money_flows.json")
for k in ("slug", "title", "takeaway", "summary", "data_date", "unit", "kind", "notes"):
    if not m.get(k): err(f"money_flows missing {k}")
if "unknown" not in m["notes"].lower(): err("money_flows notes must state unknowns")
ids = {n["id"]: n for n in m["nodes"]}
for n in m["nodes"]:
    if n["group"] not in ("source", "channel", "use"): err(f"node {n['id']} bad group")
inflow, outflow = {}, {}
for l in m["links"]:
    if l["source"] not in ids or l["target"] not in ids: err(f"link {l} bad node")
    if not (isinstance(l["value"], (int, float)) and l["value"] > 0): err(f"link {l['source']}->{l['target']} value")
    if not l.get("period") or not l.get("status"): err(f"link {l['source']}->{l['target']} period/status")
    cites(l, f"link {l['source']}->{l['target']}")
    outflow[l["source"]] = outflow.get(l["source"], 0) + l["value"]
    inflow[l["target"]] = inflow.get(l["target"], 0) + l["value"]
for n in m["nodes"]:
    if n["group"] == "channel" and abs(inflow.get(n["id"], 0) - outflow.get(n["id"], 0)) > 1e-6:
        err(f"channel {n['id']} unbalanced")
for t in m["typologies"] + m["related"]: cites(t, f"money item {t['name']}")
sch = m.get("schematic")
if sch:
    if sch.get("kind") != "schematic" or "not amounts" not in sch["title"]: err("schematic must be labelled 'not amounts'")
    for l in sch["links"]: cites(l, "schematic link")

net = load("networks.json")
gids = {g["id"] for g in net["groups"]}
for g in net["groups"]:
    cites(g, f"group {g['id']}")
    if g.get("fto"): cites(g["fto"], f"group {g['id']} fto")
    for p in g.get("leaders", []): cites(p, f"leader {p['name']}")
for e in net["edges"]:
    if e["source"] not in gids or e["target"] not in gids: err(f"edge {e['source']}-{e['target']} unknown group")
    cites(e, f"edge {e['source']}-{e['target']}")

# territory: every region-group pairing and contested note must cite; region ids must exist in basemap
_t = load("territory.json")
_gids = {g["id"] for g in _t["groups"]}
_bm = os.path.join(os.path.dirname(D), "public", "basemap", "latam.topo.json")
_ids = {g["properties"]["id"] for g in json.load(open(_bm))["objects"]["admin1"]["geometries"]} if os.path.exists(_bm) else None
for r in _t["regions"]:
    if _ids is not None and r["id"] not in _ids: err(f"territory {r['id']}: not in admin1 basemap")
    if not r["groups"]: err(f"territory {r['id']}: no groups")
    for g in r["groups"]:
        if g["group"] not in _gids: err(f"territory {r['id']}: unknown group {g['group']}")
        if g["level"] not in _t["levels"]: err(f"territory {r['id']}: bad level")
        cites(g, f"territory {r['id']}/{g['group']}")
    if r.get("contested"): cites(r["contested"], f"territory {r['id']} contested")
for i in load("china.json")["items"]: cites(i, f"china {i['id']}")
for p in glob.glob(os.path.join(D, "arcs/*.json")):
    a = json.load(open(p))
    cites(a, f"arc {a['id']}")
    for h in a["history"] + a["turning_points"]: cites(h, f"arc {a['id']} item")

BANNED = re.compile(r"\b(will|likely to|expected to|should|must|forecast|predict|recommend|ought)\b", re.I)
ev = load("events.json")
for e in ev["events"]:
    if not e.get("url", "").startswith("http"): err(f"event {e.get('title')} no url")
    if is_cn(e.get("url", "")): err(f"event .cn {e['url']}")

def check_reasoner(path):
    r = json.load(open(path, encoding="utf-8"))
    sl_path = os.path.join(D, "shortlist", r.get("date", "") + ".json")
    sl = {x["id"]: x for x in json.load(open(sl_path))["events"]} if os.path.exists(sl_path) else {}
    if not sl: err(f"{path}: no shortlist for {r.get('date')}")
    for i, a in enumerate(r.get("analysis", [])):
        w = f"{os.path.basename(path)} analysis[{i}]"
        for k in ("theatre", "headline", "what_happened", "says_vs_does", "follow_the_money", "at_stake", "cites"):
            if not a.get(k): err(f"{w} missing {k}")
        for c in a.get("cites", []):
            if c not in sl and c not in src: err(f"{w} cite {c} not in shortlist or sources")
        for k in ("headline", "what_happened", "says_vs_does", "follow_the_money", "at_stake", "tensions"):
            t = a.get(k) or ""
            if isinstance(t, list): t = " ".join(t)
            if BANNED.search(t): err(f"{w} {k} uses predictive/prescriptive word: {BANNED.search(t).group(0)}")
    for u in r.get("arc_updates", []):
        if u.get("arc") not in [os.path.basename(p)[:-5] for p in glob.glob(os.path.join(D, "arcs/*.json"))]: err(f"arc_update unknown arc {u.get('arc')}")
        if not u.get("cites"): err("arc_update without cites")

for p in sorted(glob.glob(os.path.join(D, "reasoner/*.json")))[-3:]: check_reasoner(p)

# xfeed (X posts, written by the Grok Bot routine): verified accounts only, valid region/group ids, a post URL each
_xf = os.path.join(D, "xfeed.json")
if os.path.exists(_xf):
    _x = json.load(open(_xf, encoding="utf-8"))
    _gz = load("gazetteer.json")
    _ok_handles = {k.lower() for k, v in _gz["accounts"].items() if v.get("tier") == "verified"}
    _bad_handles = {h.lower() for h in _gz.get("excluded_accounts", [])}
    _xg = _gids | gids
    _seen = set()
    for p in _x.get("posts", []):
        w = f"xfeed {p.get('id')}"
        if p.get("id") in _seen: err(f"{w}: duplicate id")
        _seen.add(p.get("id"))
        for k in ("id", "handle", "url", "created_at", "text", "lang", "tier", "source_type"):
            if not p.get(k): err(f"{w}: missing {k}")
        if p.get("tier") != "verified": err(f"{w}: tier must be 'verified' (unverified sources are not allowed)")
        h = (p.get("handle") or "").lower()
        if h in _bad_handles or h not in _ok_handles: err(f"{w}: handle @{p.get('handle')} is not on the verified account list")
        if not re.match(r"^https://x\.com/[A-Za-z0-9_]{1,15}/status/\d+$", p.get("url", "")): err(f"{w}: bad url")
        if not (p.get("region_ids") or p.get("group_ids")): err(f"{w}: no region or group tag")
        for r in p.get("region_ids", []):
            if _ids is not None and r not in _ids: err(f"{w}: unknown region {r}")
        for g in p.get("group_ids", []):
            if g not in _xg: err(f"{w}: unknown group {g}")
        if p.get("source_type") == "official" and p.get("label") != "Official statement": err(f"{w}: official post must be labelled 'Official statement'")

# breaking (pipeline/breaking.py): professional outlets/officials only, status must follow the rules, every source has a URL
_bk = os.path.join(D, "breaking.json")
_ok_handles = {k.lower() for k, v in load("gazetteer.json")["accounts"].items() if v.get("tier") == "verified"}
if os.path.exists(_bk):
    _b = json.load(open(_bk, encoding="utf-8"))
    _ol = {o["id"]: o for o in load("outlets.json")["outlets"]}
    for e in _b.get("events", []):
        w = f"breaking {e.get('id')}"
        if not e.get("sources"): err(f"{w}: no sources"); continue
        for s in e["sources"]:
            if s.get("outlet") not in _ol: err(f"{w}: source outlet {s.get('outlet')} not in outlets.json")
            elif s.get("kind") != _ol[s["outlet"]]["kind"]: err(f"{w}: source kind mismatch")
            if not str(s.get("url", "")).startswith("https://"): err(f"{w}: source without https url")
            if is_cn(s.get("url", "")): err(f"{w}: .cn source")
            h = re.match(r"^https://x\.com/([^/]+)/", s.get("url", ""))
            if h and h.group(1).lower() not in _ok_handles: err(f"{w}: X source @{h.group(1)} not verified")
        outs = {s["outlet"] for s in e["sources"] if s.get("kind") == "outlet"}
        offs = {s["outlet"] for s in e["sources"] if s.get("kind") == "official"}
        want = "confirmed" if (len(outs) >= 2 or (offs and outs)) else ("single_source" if outs else "official_claim_only")
        if e.get("status") != want: err(f"{w}: status {e.get('status')} should be {want}")
        for r in e.get("region_ids", []):
            if _ids is not None and r not in _ids: err(f"{w}: unknown region {r}")
        for g in e.get("group_ids", []):
            if g not in (_gids | gids): err(f"{w}: unknown group {g}")
        if not e.get("first_report"): err(f"{w}: no first_report")

if errs:
    print("\n".join("ERROR " + e for e in errs)); sys.exit(1)
print(f"valid: {len(src)} sources, {len(net['groups'])} groups, {len(net['edges'])} edges, {len(ev['events'])} events")
