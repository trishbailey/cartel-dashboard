"""Colour audit (Trish 2026-10-27): every colour must be clearly distinct, no greys, no two shades of one hue family.
Rules enforced: the plain group colours (public/palette.js TERR_FILL) differ pairwise by CIEDE2000 >= PLAIN_MIN_DE and each sits in its own hue family; small distant groups may repeat a
plain hex only with a texture unique to that hex; timeline-only and network-only groups (CARTEL_FALL + CARTEL_TEX) follow the same (hex, texture) rule; territory.json colours equal TERR_FILL;
presence levels change lightness (paler = less) within the group hue, never the hue or opacity; routes and overlays stand out from every fill. Sources: data/territory.json, public/palette.js, public/routes3.js, public/app.js (overlay colours)."""
import json, os, re, math, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_DE = 20
def rd(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def lab(h):
    h = h.lstrip("#"); c = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    c = [((v+0.055)/1.055)**2.4 if v > 0.04045 else v/12.92 for v in c]
    x = (c[0]*.4124+c[1]*.3576+c[2]*.1805)/.95047; y = c[0]*.2126+c[1]*.7152+c[2]*.0722; z = (c[0]*.0193+c[1]*.1192+c[2]*.9505)/1.08883
    f = lambda t: t**(1/3) if t > 216/24389 else (24389/27*t+16)/116
    fx, fy, fz = f(x), f(y), f(z); return 116*fy-16, 500*(fx-fy), 200*(fy-fz)
def sat(h):
    import colorsys; h = h.lstrip("#"); return colorsys.rgb_to_hls(*[int(h[i:i+2], 16)/255 for i in (0, 2, 4)])[2]
def de2000(a, b):
    L1, a1, b1 = a; L2, a2, b2 = b
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cm = (C1+C2)/2
    G = .5*(1-math.sqrt(Cm**7/(Cm**7+25**7))); a1p, a2p = a1*(1+G), a2*(1+G)
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1 = math.degrees(math.atan2(b1, a1p)) % 360; h2 = math.degrees(math.atan2(b2, a2p)) % 360
    dL, dC = L2-L1, C2p-C1p
    dh = 0 if C1p*C2p == 0 else (h2-h1 if abs(h2-h1) <= 180 else h2-h1-360 if h2 > h1 else h2-h1+360)
    dH = 2*math.sqrt(C1p*C2p)*math.sin(math.radians(dh/2))
    Lm, Cpm = (L1+L2)/2, (C1p+C2p)/2
    hm = h1+h2 if C1p*C2p == 0 else ((h1+h2)/2 if abs(h1-h2) <= 180 else (h1+h2+360)/2 if h1+h2 < 360 else (h1+h2-360)/2)
    T = 1-.17*math.cos(math.radians(hm-30))+.24*math.cos(math.radians(2*hm))+.32*math.cos(math.radians(3*hm+6))-.2*math.cos(math.radians(4*hm-63))
    SL = 1+.015*(Lm-50)**2/math.sqrt(20+(Lm-50)**2); SC = 1+.045*Cpm; SH = 1+.015*Cpm*T
    RT = -2*math.sqrt(Cpm**7/(Cpm**7+25**7))*math.sin(math.radians(60*math.exp(-((hm-275)/25)**2)))
    return math.sqrt((dL/SL)**2+(dC/SC)**2+(dH/SH)**2+RT*(dC/SC)*(dH/SH))
def collect():
    cols = {}
    for g in json.load(open(os.path.join(ROOT, "data/territory.json"), encoding="utf-8"))["groups"]:
        if g.get("color"): cols["group:"+g["id"]] = g["color"].lower()
    for k, v in re.findall(r'(\w+):"(#[0-9a-fA-F]{6})"', re.search(r"CARTEL_FALL=\{(.*?)\}", rd("public/palette.js")).group(1)):
        cols.setdefault("group:"+k, v.lower())
    for k, v in re.findall(r'(\w+):"(#[0-9a-fA-F]{6})"', (re.search(r"GCOL=\{(.*?)\}", rd("public/leaders.js")) or re.match("()","")).group(1)):  # bar charts removed; GCOL optional
        if cols.get("group:"+k, v.lower()) != v.lower(): cols["leaders:"+k] = v.lower()
    for k, v in re.findall(r'k:"(\w+)".*?color:"(#[0-9a-fA-F]{6})"', rd("public/routes3.js")): cols["layer:"+k] = v.lower()
    app = rd("public/app.js")
    for k, v in re.findall(r'(?<!&)mk\("(\w+)",.*?,"(#[0-9a-fA-F]{6})"', app): cols["layer:"+k] = v.lower()
    m = re.search(r'PVC=\{official:"(#\w{6})",journalist:"(#\w{6})"\}', app)
    if m: cols["layer:pvm"], cols["layer:pvj"] = m.group(1).lower(), m.group(2).lower()
    return cols
CHARTS = {  # colours drawn together in one graphic, enforced at MIN_DE
    "map: overlay layers (routes, crossings, sites, killings)": lambda c: {k: v for k, v in c.items() if k.startswith("layer:")},
}
WARN = {}  # superseded by check_lineage(): group colours are no longer one-per-id, they are (hex, texture) identities
TERR = {g["id"] for g in json.load(open(os.path.join(ROOT, "data/territory.json"), encoding="utf-8"))["groups"]}
def pairs(cols, lim):
    L = {k: lab(v) for k, v in cols.items()}; out = []
    for x, y in itertools.combinations(cols, 2):
        if cols[x] == cols[y] and (x.split(":")[1] == y.split(":")[1] or {x[6:], y[6:]} == {"haiti", "viv_ansanm"}): continue
        d = de2000(L[x], L[y])
        if d < lim: out.append(f"{x} {cols[x]} vs {y} {cols[y]}: dE2000 {d:.1f}")
    return out
def check(cols=None):
    cols = cols or collect(); errs = []
    for k, v in cols.items():
        l, a, b = lab(v)
        if math.hypot(a, b) < 15 and 10 < l < 97: errs.append(f"colour {k} {v} is grey-ish (chroma {math.hypot(a,b):.0f})")
    for name, f in CHARTS.items(): errs += [f"[{name}] {p} < {MIN_DE}" for p in pairs(f(cols), MIN_DE)]
    return errs
def warnings(cols=None):
    cols = cols or collect(); out = []
    for name, f in WARN.items():
        sub = f(cols); ps = pairs(sub, MIN_DE)
        if ps: out.append(f"[{name}] {len(sub)} colours, {len(ps)} pairs below {MIN_DE} (min shown): " + min(ps, key=lambda s: float(s.rsplit(" ", 1)[1])))
    return out
# --- mid-tone area fills (Trish 2026-10-26): L* 45-65, HSL sat 0.4-0.7, never grey, pinks/purples allowed if not neon ---
FILL_PALE = {"dominant": 0, "significant": .18, "present": .4}  # presence level = share of white mixed into the group hue (lighter = less, full hue = more), mirrors PALE in public/app.js
LAND = "#1b2c4a"
FILL_L = (36, 76); FILL_SAT = (.35, .9); FILL_C_MIN = 20; FILL_MIN_DE = 22; PLAIN_MIN_DE = 22  # relaxed from the 2026-10-26 mid-tone limits: dE >= 22 across 13 plain hue families is unreachable inside L* 40-68 / sat .4-.7
# named hue families on CIELCh hue (plus a dark low-chroma "brown"). Every plain fill needs its OWN family (Trish 2026-10-26).
# The only allowed repeat: a non-Mexican group in a distant country that carries a texture (window.TERR_PAT dots/grid) differing from every other group in that family.
HUE_BUCKETS = [(350, 15, "rose"), (15, 40, "red"), (40, 62, "orange"), (62, 88, "gold"), (88, 115, "olive"), (115, 150, "green"), (150, 180, "emerald"), (180, 220, "teal"), (220, 265, "sky blue"), (265, 288, "blue"), (288, 305, "periwinkle"), (305, 325, "violet"), (325, 350, "magenta")]
ADJ = {frozenset(p) for p in [("MEX","GTM"),("MEX","BLZ"),("MEX","USA"),("GTM","SLV"),("GTM","HND"),("GTM","BLZ"),("HND","SLV"),("HND","NIC"),("COL","VEN"),("COL","ECU"),("COL","BRA"),("COL","PAN"),("COL","PER"),("VEN","BRA"),("VEN","GUY"),("BRA","PRY"),("BRA","PER"),("BRA","BOL"),("ECU","PER"),("PRY","BOL"),("PRY","ARG"),("HTI","DOM")]}
def hue_bucket(h):
    L, a, b = lab(h); C = math.hypot(a, b); hh = math.degrees(math.atan2(b, a)) % 360
    if 20 <= hh < 95 and L < 52 and C < 40: return "brown"
    for lo, hi, n in HUE_BUCKETS:
        if (lo <= hh < hi) if lo < hi else (hh >= lo or hh < hi): return n
def group_countries():
    t = json.load(open(os.path.join(ROOT, "data/territory.json"), encoding="utf-8")); c = {g["id"]: set() for g in t["groups"]}
    for r in t["regions"]:
        for x in r["groups"]: c.setdefault(x["group"], set()).add(r["iso"])
    return c
def near(cx, cy): return any(a == b or frozenset((a, b)) in ADJ for a in cx for b in cy)
ARROW_MIN_DE = 24; ARROW_MIN_DE_PALE = 12; ARROW_MIN_CR = 2.5  # paler presence tints (lighter = less) sit closer to the bright route colours; every route line keeps its dark #0b1526 halo (routes3.js), so they only need ARROW_MIN_DE_PALE
def pats():
    m = re.search(r"TERR_PAT=\{(.*?)\}", rd("public/palette.js"))
    return dict(re.findall(r'(\w+):"(\w+)"', m.group(1))) if m else {}
def fills():
    m = re.search(r"TERR_FILL=\{(.*?)\}", rd("public/palette.js"))
    return {k: v.lower() for k, v in re.findall(r'(\w+):"(#[0-9a-fA-F]{6})"', m.group(1))} if m else {}
def shade(c, lv):  # what the eye sees: the group colour mixed with white by its presence level
    w = FILL_PALE[lv]; f = [int(c[i:i+2], 16)*(1-w)+255*w for i in (1, 3, 5)]
    return lab("#%02x%02x%02x" % tuple(round(v) for v in f))
def lum(h):
    h = h.lstrip("#"); c = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    c = [((v+0.055)/1.055)**2.4 if v > 0.04045 else v/12.92 for v in c]; return .2126*c[0]+.7152*c[1]+.0722*c[2]
def lab_lum(L): y = ((L+16)/116)**3 if L > 8 else L/903.3; return y
def check_fills(cols=None):
    cols = cols or collect(); F = fills(); errs, warns = [], []
    for g in TERR:
        if g not in F: errs.append(f"fill: group {g} has no muted TERR_FILL colour")
    for k, v in F.items():
        L, a, b = lab(v); C = math.hypot(a, b); h = math.degrees(math.atan2(b, a)) % 360
        if not FILL_L[0] <= L <= FILL_L[1]: errs.append(f"fill {k} {v}: lightness L*{L:.0f} outside {FILL_L}")
        if not FILL_SAT[0] <= sat(v) <= FILL_SAT[1]: errs.append(f"fill {k} {v}: HSL saturation {sat(v):.2f} outside {FILL_SAT}")
        if C < FILL_C_MIN: errs.append(f"fill {k} {v}: chroma {C:.0f} < {FILL_C_MIN} (grey)")
        for lv in FILL_PALE:
            Ls, as_, bs = shade(v, lv)
            if math.hypot(as_, bs) < 15: errs.append(f"fill {k} {v} at {lv}: grey (chroma {math.hypot(as_, bs):.0f})")
    ids = sorted(F); low = []; GCN = group_countries(); PT = pats(); plain, nearp = [], []
    for k, v in PT.items():
        if k not in F: errs.append(f"TERR_PAT {k}: not a fill")
        if v not in ("dots", "grid", "stripes"): errs.append(f"TERR_PAT {k}: unknown texture {v}")
        if "MEX" in GCN.get(k, set()): errs.append(f"TERR_PAT {k}: Mexican groups keep a plain fill")
    for x, y in itertools.combinations(ids, 2):
        if F[x] == F[y] and {x, y} == {"haiti", "viv_ansanm"}: continue
        d = de2000(lab(F[x]), lab(F[y]))
        cx, cy = GCN.get(x, set()), GCN.get(y, set()); mex = "MEX" in cx or "MEX" in cy; close = near(cx, cy) or ("MEX" in cx and "MEX" in cy)
        if hue_bucket(F[x]) == hue_bucket(F[y]):
            px, py = PT.get(x, "plain"), PT.get(y, "plain")
            if mex or close or px == py: errs.append(f"fill {x} {F[x]} vs {y} {F[y]}: same hue family '{hue_bucket(F[x])}' " + ("(Mexican group)" if mex else "(same or neighbouring country)" if close else "(no distinguishing texture)"))
        elif PT.get(x, "plain") == "plain" and PT.get(y, "plain") == "plain": plain.append((d, x, y))
        if close: nearp.append((d, x, y))
        if d < PLAIN_MIN_DE and F[x] != F[y]: errs.append(f"fill {x} {F[x]} vs {y} {F[y]}: dE2000 {d:.1f} < {PLAIN_MIN_DE} (indistinct)")
        if close and F[x] != F[y] and d < FILL_MIN_DE: errs.append(f"fill {x} {F[x]} vs {y} {F[y]}: dE2000 {d:.1f} < {FILL_MIN_DE} (indistinct, can sit together)")
    if plain: d, x, y = min(plain); warns.append(f"[map: fills] closest pair of plain fills (different hue families): {x} {F[x]} vs {y} {F[y]} dE2000 {d:.1f}")
    if nearp: d, x, y = min(nearp); warns.append(f"[map: fills] closest pair that can sit together: {x} {F[x]} vs {y} {F[y]} dE2000 {d:.1f} (floor {FILL_MIN_DE})")
    # route arrows / lines must stand out from every fill shade they cross
    routes = {"route:"+k: v.lower() for k, v in re.findall(r'k:"(\w+)".*?color:"(#[0-9a-fA-F]{6})"', rd("public/routes3.js"))}
    worst = None
    for rk, rc in routes.items():
        for k, v in F.items():
            for lv in FILL_PALE:
                fl = shade(v, lv); d = de2000(lab(rc), fl)
                y1, y2 = lum(rc), lab_lum(fl[0]); cr = (max(y1, y2)+.05)/(min(y1, y2)+.05)
                floor = ARROW_MIN_DE if lv == "dominant" else ARROW_MIN_DE_PALE
                if d < floor: errs.append(f"arrow {rk} {rc} vs fill {k}@{lv}: dE2000 {d:.1f} < {floor}")
                if worst is None or cr < worst[0]: worst = (cr, rk, rc, k, lv)
    if worst and worst[0] < ARROW_MIN_CR: warns.append("[map: route arrows on fills] lowest luminance contrast %.2f (%s %s on %s@%s); arrows/lines keep a dark #0b1526 outline" % worst)
    return errs, warns
_check, _warnings = check, warnings
def texs():
    out = {}
    for name in ("CARTEL_TEX",):
        m = re.search(name + r"=\{(.*?)\}", rd("public/palette.js")); out.update(re.findall(r'(\w+):"(\w+)"', m.group(1)) if m else [])
    return out
def check_lineage():
    """every group in the map, network graph and timeline resolves to one (hex, texture) identity; identities are unique; textures only on a hex owned by a plain group"""
    errs = []; F = fills(); PT = pats(); TX = texs(); js = rd("public/palette.js")
    FALL = {k: v.lower() for k, v in re.findall(r'(\w+):"(#[0-9a-fA-F]{6})"', re.search(r"CARTEL_FALL=\{(.*?)\}", js).group(1))}
    alias = dict(re.findall(r'(\w+):"(\w+)"', re.search(r"CARTEL_ALIAS=\{(.*?)\}", js).group(1)))
    t = json.load(open(os.path.join(ROOT, "data/territory.json"), encoding="utf-8"))
    for g in t["groups"]:
        if g["color"].lower() != F.get(g["id"]): errs.append(f"territory.json colour of {g['id']} ({g['color']}) differs from TERR_FILL ({F.get(g['id'])})")
    ids = set(F) | set(FALL) | {g["id"] for g in json.load(open(os.path.join(ROOT, "data/networks.json"), encoding="utf-8"))["groups"]} | {l["id"] for l in json.load(open(os.path.join(ROOT, "data/timeline.json"), encoding="utf-8"))["lanes"]}
    ident = {}
    for i in sorted(ids):
        k = alias.get(i, i); hx = F.get(k) or FALL.get(i); tx = PT.get(k) or TX.get(i) or "plain"
        if not hx: errs.append(f"group {i} has no colour in palette.js (TERR_FILL or CARTEL_FALL)"); continue
        if tx != "plain" and tx not in ("dots", "grid", "stripes"): errs.append(f"group {i}: unknown texture {tx}")
        ident.setdefault((hx, tx), []).append(k)
    for (hx, tx), v in ident.items():
        if len(set(v)) > 1: errs.append(f"groups {sorted(set(v))} share both colour {hx} and texture {tx}: indistinguishable")
    plain = {hx: v for (hx, tx), v in ident.items() if tx == "plain"}
    for (hx, tx), v in ident.items():
        if tx != "plain" and hx not in plain: errs.append(f"textured group {v} uses {hx}, which no plain group owns (a texture only separates groups that share a colour)")
    hs = sorted({hx for hx, tx in ident}); fam = {}
    for h in hs: fam.setdefault(hue_bucket(h), []).append(h)
    for b, v in fam.items():
        if len(v) > 1: errs.append(f"hue family '{b}' holds {len(v)} different colours {v}: two shades of one family")
    for x, y in itertools.combinations(hs, 2):
        d = de2000(lab(x), lab(y))
        if d < PLAIN_MIN_DE: errs.append(f"colours {x} vs {y}: dE2000 {d:.1f} < {PLAIN_MIN_DE}")
    return errs
def check(cols=None): cols = cols or collect(); return _check(cols) + check_fills(cols)[0] + check_lineage()
def warnings(cols=None): cols = cols or collect(); return _warnings(cols) + check_fills(cols)[1]
if __name__ == "__main__":
    c = collect(); e = check(c); print(len(c), "colours;", len(e), "problems"); print("\n".join(e)); print("\n".join(warnings(c)))
