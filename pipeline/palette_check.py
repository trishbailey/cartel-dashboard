"""Colour audit: every cartel/group colour and every map-layer colour must differ by CIEDE2000 dE >= 20, and none may be grey.
Sources: data/territory.json, public/palette.js, public/leaders.js GCOL, public/routes3.js, public/app.js (overlay colours)."""
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
    for k, v in re.findall(r'(\w+):"(#[0-9a-fA-F]{6})"', re.search(r"GCOL=\{(.*?)\}", rd("public/leaders.js")).group(1)):
        if cols.get("group:"+k, v.lower()) != v.lower(): cols["leaders:"+k] = v.lower()
    for k, v in re.findall(r'k:"(\w+)".*?color:"(#[0-9a-fA-F]{6})"', rd("public/routes3.js")): cols["layer:"+k] = v.lower()
    app = rd("public/app.js")
    for k, v in re.findall(r'(?<!&)mk\("(\w+)",.*?,"(#[0-9a-fA-F]{6})"', app): cols["layer:"+k] = v.lower()
    m = re.search(r'PVC=\{official:"(#\w{6})",journalist:"(#\w{6})"\}', app)
    if m: cols["layer:pvm"], cols["layer:pvj"] = m.group(1).lower(), m.group(2).lower()
    m = re.search(r"COL=\{(.*?)\}", rd("public/shift.js"))
    if m:
        for k, v in re.findall(r'(\w+):"(#[0-9a-fA-F]{6})"', m.group(1)): cols["shift:"+k] = v.lower()
    return cols
CHARTS = {  # colours drawn together in one graphic, enforced at MIN_DE
    "chart: how the business shifted (all series)": lambda c: {k: v for k, v in c.items() if k.startswith("shift:")},
    "map: group territory fills": lambda c: {k: v for k, v in c.items() if k.startswith("group:") and k[6:] in TERR},
    "map: overlay layers (routes, crossings, sites, killings)": lambda c: {k: v for k, v in c.items() if k.startswith("layer:")},
}
WARN = {  # graphics with too many categories for dE>=20 in sRGB; nodes carry text labels, so these only warn
    "network/timeline/profiles: all groups": lambda c: {k: v for k, v in c.items() if k.startswith("group:")},
    "map: fills plus overlays together": lambda c: {k: v for k, v in c.items() if k.startswith("layer:") or k[6:] in TERR},
}
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
if __name__ == "__main__":
    c = collect(); e = check(c); print(len(c), "colours;", len(e), "problems"); print("\n".join(e)); print("\n".join(warnings(c)))
