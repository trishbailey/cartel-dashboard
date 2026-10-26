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

# data modules: every value carries an https source URL (not .cn), every file cites registered sources
def _url(u, where):
    if not str(u).startswith("https://"): err(f"{where}: value without https source url")
    elif is_cn(u): err(f"{where}: .cn url")
def _pts(pts, where, key):
    if not pts: err(f"{where}: empty series")
    for x in pts:
        if not isinstance(x.get(key), (int, float)): err(f"{where} {x.get('m')}: bad value")
        _url(x.get("url"), f"{where} {x.get('m')}")
for fn in ("violence.json", "seizures.json", "overdoses.json", "disappearances.json", "extortion.json", "mx_states.json", "political_violence.json"):
    if not os.path.exists(os.path.join(D, fn)): err(f"missing data module {fn}"); continue
    o = load(fn); cites(o, fn)
    if fn == "violence.json":
        for k, v in o["states"].items(): _pts(v, f"violence state {k}", "v")
    elif fn == "seizures.json":
        for d, v in o["national"].items(): _pts(v, f"seizures {d}", "lb")
        for a, dd in o["aor"].items():
            for d, v in dd.items(): _pts(v, f"seizures {a}/{d}", "lb")
    elif fn == "overdoses.json":
        for st, v in o["series"].items(): _pts(v, f"overdoses {st}", "v")
    elif fn in ("disappearances.json", "extortion.json"):
        if len(o["states"]) != 32: err(f"{fn}: expected 32 states")
        for x in o["states"]:
            if _ids is not None and x["region"] not in _ids: err(f"{fn} {x['name']}: region not in basemap")
            _url(x.get("url"), f"{fn} {x['name']}")
    elif fn == "mx_states.json":
        for x in o["states"]: _url(x.get("url"), f"mx_states {x['name']}")
    elif fn == "political_violence.json":
        for x in o["events"]:
            w = f"political_violence {x.get('name')}"
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", x.get("date", "")) or not x.get("lonlat"): err(f"{w}: date/lonlat")
            _url(x.get("url"), w); cites(x, w)

# storyline cards (data/arcs/*.json "storyline") and the situation overview: every sentence sourced, no predictive words
def _sentences(lst, where):
    if not lst: err(f"{where}: no sentences")
    for i, t in enumerate(lst):
        cites(t, f"{where}[{i}]")
        if BANNED.search(t.get("text", "")): err(f"{where}[{i}] uses predictive/prescriptive word: {BANNED.search(t['text']).group(0)}")
_orders = []
for p in glob.glob(os.path.join(D, "arcs/*.json")):
    a = json.load(open(p)); sl = a.get("storyline")
    if not sl: continue
    _orders.append(sl.get("order"))
    for k in ("title", "what", "view", "trend"):
        if not sl.get(k): err(f"storyline {a['id']}: missing {k}")
    _sentences(sl.get("what"), f"storyline {a['id']}")
    for g in sl.get("groups", []):
        if g not in _gids: err(f"storyline {a['id']}: unknown group {g}")
    for l in a.get("log", []):
        for x in l.get("links", []): _url(x.get("url"), f"arc {a['id']} log {l.get('date')}")
if not 5 <= len(_orders) <= 7: err(f"expected 5-7 storylines, found {len(_orders)}")
_sentences(load("overview.json")["sentences"], "overview")
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
        if BANNED.search(u.get("text", "")): err(f"arc_update {u.get('arc')} uses predictive/prescriptive word")
        if u.get("what_happening"): _sentences(u["what_happening"], f"arc_update {u.get('arc')} what_happening")

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
        if p.get("lang") != "en" and not (p.get("text_en") or "").strip(): err(f"{w}: non-English post needs text_en (run pipeline/tr.py todo, translate, tr.py add)")

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
        if e.get("lang", "es") != "en" and not (e.get("title_en") or "").strip(): err(f"{w}: non-English title needs title_en (run pipeline/tr.py todo, translate, tr.py add)")

# ---- leaders.json and capture.json (leader cards, state capture layer) ----
_okstat = {"at_large","jailed","extradited","dead","reported_dead"}
def _srcok(s, w):
    if not s or not s.get("name") or not str(s.get("url","")).startswith("https://"): err(f"{w}: source needs name and https url"); return
    if is_cn(s["url"]): err(f"{w}: .cn source")
if os.path.exists(os.path.join(D, "leaders.json")):
    _ld = load("leaders.json"); _seen = set()
    for l in _ld.get("leaders", []):
        w = f"leader {l.get('id')}"
        if l.get("id") in _seen: err(f"{w}: duplicate id")
        _seen.add(l.get("id"))
        for k in ("name","role","status","status_date","known_for"):
            if not l.get(k): err(f"{w}: missing {k}")
        if l.get("status") not in _okstat: err(f"{w}: bad status {l.get('status')}")
        _srcok(l.get("status_source"), w + " status_source")
        if not l.get("sources"): err(f"{w}: no sources")
        for s in l.get("sources", []): _srcok(s, w)
        if l.get("reward_usd"): _srcok(l.get("reward_source"), w + " reward_source")
        for g in l.get("group_ids", []):
            if g not in (_gids | gids): err(f"{w}: unknown group {g}")
        ph = l.get("photo") or {}
        if not ph.get("license"): err(f"{w}: photo needs a license")
        if not ph.get("placeholder"):
            if not str(ph.get("image_source_url","")).startswith("https://") or is_cn(ph.get("image_source_url","")): err(f"{w}: photo needs https image_source_url")
            if not ph.get("credit"): err(f"{w}: photo needs credit")
            if not ph.get("file") or not os.path.exists(os.path.join(ROOT, "public", ph["file"])): err(f"{w}: image file missing (no hotlinking)")
if os.path.exists(os.path.join(D, "capture.json")):
    _cp = load("capture.json"); _okc = set(_cp.get("status_legend", {}))
    if not {"alleged","charged","convicted","sanctioned","acquitted","pardoned","dropped"} <= _okc: err("capture: status_legend incomplete")
    _cc = {}
    for c in _cp.get("cases", []):
        w = f"capture {c.get('id')}"
        for k in ("country","person","office","level","status","date","note"):
            if not c.get(k): err(f"{w}: missing {k}")
        if not re.fullmatch(r"[A-Z]{3}", str(c.get("country"))): err(f"{w}: bad country")
        if c.get("level") not in ("national","state","municipal"): err(f"{w}: bad level")
        if c.get("status") not in _okc: err(f"{w}: bad status")
        if re.search(r"compromised", json.dumps(c), re.I): err(f"{w}: do not label as compromised")
        if not c.get("sources"): err(f"{w}: no sources")
        for s in c.get("sources", []): _srcok(s, w)
        for g in c.get("group_ids", []):
            if g not in (_gids | gids): err(f"{w}: unknown group {g}")
        _cc[c.get("country")] = _cc.get(c.get("country"), 0) + 1
    for s in _cp.get("countries", []):
        if _cc.get(s["country"]) != s.get("total"): err(f"capture summary {s['country']}: total mismatch")

# ---- who's in charge: roles, confidence, coverage per group ----
_ROLES={"current_leader","faction_leader","former_leader","reported_successor"}
_CONF={"confirmed by officials","reported by multiple outlets","reported, contested"}
if os.path.exists(os.path.join(D, "leaders.json")):
    _gk={g.get("id"):g for g in _ld.get("groups",[])}
    if len(_gk)!=14: err(f"leaders: expected 14 groups, got {len(_gk)}")
    for l in _ld.get("leaders",[]):
        w=f"leader {l.get('id')}"
        if l.get("role") not in _ROLES: err(f"{w}: role must be one of {sorted(_ROLES)}")
        if l.get("group_key") not in _gk: err(f"{w}: group_key not in groups")
        if l.get("role")!="former_leader":
            if l.get("confidence") not in _CONF: err(f"{w}: needs confidence label")
            if l.get("status") in ("dead","reported_dead","extradited"): err(f"{w}: dead/extradited cannot be in charge")
        if re.search(r"in charge", json.dumps(l), re.I) and l.get("role")=="former_leader": err(f"{w}: former leader text says 'in charge'")
    for gid,g in _gk.items():
        live=[l for l in _ld["leaders"] if l.get("group_key")==gid and l.get("role")!="former_leader"]
        if not live and not g.get("leadership_unknown"): err(f"group {gid}: needs a current/faction leader, reported successor, or leadership_unknown note")
        for s in g.get("sources",[]): _srcok(s, f"group {gid}")
        if not g.get("sources"): err(f"group {gid}: leadership note needs a source")
if os.path.exists(os.path.join(D, "groups_size.json")):
    for gid,g in load("groups_size.json")["groups"].items():
        for k in ("members","revenue"):
            if not g.get(k): err(f"size {gid}: missing {k} (use no_credible_estimate)")
            for e in g.get(k,[]):
                if e.get("no_credible_estimate"): continue
                if not e.get("unit"): err(f"size {gid} {k}: missing unit")
                if not str(e.get("source_url","")).startswith("https://") or is_cn(e.get("source_url","")): err(f"size {gid} {k}: needs https source_url")
                if e.get("low") is None and e.get("high") is None: err(f"size {gid} {k}: no figure")
                if not e.get("year"): err(f"size {gid} {k}: missing year")
if os.path.exists(os.path.join(D, "groups_business.json")):
    _bz=load("groups_business.json"); _ln={x["id"] for x in _bz["lines"]}
    for gid,row in _bz["groups"].items():
        for line,c in row.items():
            if line not in _ln: err(f"business {gid}: unknown line {line}")
            if c.get("level") not in ("primary","secondary","minor"): err(f"business {gid}.{line}: bad level")
            if not str(c.get("source_url","")).startswith("https://") or is_cn(c.get("source_url","")): err(f"business {gid}.{line}: needs source")

# ---- group_countries.json: every country needs a known source ----
if os.path.exists(os.path.join(D, "group_countries.json")):
    for gid, g in load("group_countries.json")["groups"].items():
        if not g.get("countries") or g["countries"][0]["iso"] != g.get("home"): err(f"group_countries {gid}: home country must be first")
        for c in g["countries"]:
            if not c.get("cites") or any(x not in src for x in c["cites"]): err(f"group_countries {gid}.{c.get('iso')}: needs known cite ids")
# timeline: every lane/event needs a known group, a year and a registered source
if os.path.exists(os.path.join(D, "timeline.json")):
    _tl = load("timeline.json"); _tg = gids | {g["id"] for g in load("territory.json")["groups"]}
    _lanes = set()
    for l in _tl["lanes"]:
        if l["id"] not in _tg and not (l.get("historic") and l.get("name")): err(f"timeline lane {l['id']}: unknown group")
        if not isinstance(l.get("founded"), int): err(f"timeline lane {l['id']}: no founded year")
        cites(l, f"timeline lane {l['id']}"); _lanes.add(l["id"])
        if l.get("split"): cites(l["split"], f"timeline lane {l['id']} split")
    for l in _tl["lanes"]:
        if l.get("parent") and l["parent"] not in _lanes: err(f"timeline lane {l['id']}: parent has no lane")
    for i, e in enumerate(_tl["events"]):
        if not isinstance(e.get("year"), int) or not 1900 <= e["year"] <= 2100: err(f"timeline event {i}: bad year")
        if e.get("group") not in _lanes: err(f"timeline event {i}: group {e.get('group')} has no lane")
        if not e.get("text"): err(f"timeline event {i}: no text")
        cites(e, f"timeline event {i} ({e.get('group')})")

# ---- whatsnew.json (digest; see docs/DIGEST.md) ----
if os.path.exists(os.path.join(D, "whatsnew.json")):
    import re as _re
    _wn = load("whatsnew.json"); _BAN = _re.compile(r"\b(will|likely to|expected to|should|must|forecast\w*|predict\w*|recommend\w*)\b", _re.I)
    _VER = {"Confirmed", "Single source", "Official claim only"}
    if not _wn.get("as_of"): err("whatsnew: no as_of")
    def _wsrc(s, w):
        if isinstance(s, str):
            if s not in src: err(f"{w}: unknown source id {s}")
        elif not (isinstance(s, dict) and s.get("url") and (s.get("name") or s.get("publisher"))): err(f"{w}: source needs url and name")
        elif is_cn(s["url"]): err(f"{w}: .cn source")
    def _wdev(d, w):
        if not d.get("text"): err(f"{w}: no text")
        if _BAN.search(d.get("text", "")): err(f"{w}: banned word: {_BAN.search(d['text']).group(0)}")
        if d.get("verification") not in _VER: err(f"{w}: bad verification {d.get('verification')}")
        if not _re.match(r"^\d{4}-\d{2}-\d{2}$", str(d.get("date", ""))): err(f"{w}: bad date")
        if not d.get("sources"): err(f"{w}: no sources")
        for s in d.get("sources", []): _wsrc(s, w)
        if d.get("verification") == "Confirmed" and len({(s if isinstance(s, str) else s["name"].split(" (X")[0]).lower() for s in d["sources"]}) < 2: err(f"{w}: Confirmed needs 2+ sources")
    _tr = _wn.get("trends", [])
    if not 4 <= len(_tr) <= 7: err(f"whatsnew: {len(_tr)} trends (want 4-7)")
    for t in _tr:
        w = f"whatsnew trend {t.get('id')}"
        if not t.get("title") or not t.get("context"): err(f"{w}: needs title and context")
        if _BAN.search(t.get("context", "")): err(f"{w}: banned word in context")
        if not t.get("context_sources"): err(f"{w}: context unsourced")
        for s in t.get("context_sources", []): _wsrc(s, w)
        if t.get("status") and t["status"] not in ("escalating", "steady", "easing"): err(f"{w}: bad status")
        if t.get("status") and not t.get("status_sources"): err(f"{w}: status needs sourced counts (status_sources)")
        if not 1 <= len(t.get("developments", [])) <= 5: err(f"{w}: 1-5 developments")
        for i, d in enumerate(t.get("developments", [])): _wdev(d, f"{w} dev {i}")
    if len(_wn.get("other", [])) > 3: err("whatsnew: max 3 'other' items")
    for i, d in enumerate(_wn.get("other", [])): _wdev(d, f"whatsnew other {i}")

# ---- physical route layers (pipeline/mk_routes3.py) ----
for _fn, _ch, _subs in [("routes_drugs.geojson", "drugs", {"cocaine", "precursor", "synthetic"}),
                        ("routes_migrants.geojson", "migrants", {"northbound land", "rail (La Bestia)", "sea", "southbound (reverse) 2025"}),
                        ("routes_firearms.geojson", "firearms", {"land", "sea", "air"})]:
    if not os.path.exists(os.path.join(D, _fn)): err(f"{_fn} missing"); continue
    _g = load(_fn)
    if not _g.get("features"): err(f"{_fn}: no features")
    for i, f in enumerate(_g["features"]):
        pr, w = f.get("properties", {}), f"{_fn} feature {i}"
        if pr.get("channel") != _ch: err(f"{w}: channel {pr.get('channel')}")
        if pr.get("subtype") not in _subs: err(f"{w}: unknown subtype {pr.get('subtype')}")
        for k in ("from", "to", "description", "year"):
            if not pr.get(k): err(f"{w}: no {k}")
        if not pr.get("sources"): err(f"{w}: unsourced")
        for s in pr.get("sources", []):
            if isinstance(s, str):
                if s not in src: err(f"{w}: unknown source {s}")
            elif not (s.get("url") and s.get("name")) or is_cn(s["url"]): err(f"{w}: bad source")
        c = f.get("geometry", {}).get("coordinates", [])
        if f.get("geometry", {}).get("type") != "LineString" or len(c) < 2 or not all(-180 <= x <= 180 and -90 <= y <= 90 for x, y in c): err(f"{w}: bad geometry")

# ---- profiles.json (group profile cards) ----
if os.path.exists(os.path.join(D, "profiles.json")):
    _pr = load("profiles.json"); _BANP = re.compile(r"\b(will|likely to|expected to|should|must|forecast\w*|predict\w*|recommend\w*)\b", re.I)
    for p in _pr["profiles"]:
        w = f"profile {p.get('id')}"
        for k in ("id", "name", "what", "founded"):
            if not p.get(k): err(f"{w}: missing {k}")
        for k in ("what_c", "founded_c"): cites({"cites": p.get(k)}, f"{w} {k}")
        if p.get("lines"): cites({"cites": p.get("lines_c")}, f"{w} lines")
        for i, (t, c) in enumerate(p.get("more", [])):
            cites({"cites": c}, f"{w} more {i}")
            if _BANP.search(t): err(f"{w}: banned word in more {i}")
        if _BANP.search(p["what"]): err(f"{w}: banned word in what")
        for i, s in enumerate(p.get("membership_series", [])):
            if not isinstance(s.get("year"), int) or not isinstance(s.get("low"), (int, float)): err(f"{w} series {i}: year/low")
            if s.get("high") is not None and s["high"] < s["low"]: err(f"{w} series {i}: high<low")
            cites({"cites": [s.get("source")]}, f"{w} series {i}")
        im = p.get("image")
        if im:
            if not os.path.exists(os.path.join(os.path.dirname(D), "public", im["src"])): err(f"{w}: image file missing")
            if not im.get("license") or not im.get("page", "").startswith("https://commons.wikimedia.org/"): err(f"{w}: image needs Commons page + licence")

if errs:
    print("\n".join("ERROR " + e for e in errs)); sys.exit(1)
print(f"valid: {len(src)} sources, {len(net['groups'])} groups, {len(net['edges'])} edges, {len(ev['events'])} events")
