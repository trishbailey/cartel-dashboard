"""Monthly free-data refresh (no keys, no model calls, no .cn). Each fetcher is independent:
on failure the existing data file is kept unchanged and the failure is recorded in data/monthly_status.json.
Outputs: data/seizures.json (CBP), data/overdoses.json (CDC VSRR), data/violence.json (SESNSP victims)."""
import csv, io, json, os, re, sys, datetime as dt, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept": "text/html,application/json,text/csv,*/*", "Accept-Language": "en-US,en;q=0.9"}
MON = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
def get(u, t=90):
    if (urllib.parse.urlparse(u).hostname or "").endswith(".cn"): raise RuntimeError("cn blocked")
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
import urllib.parse
def save(n, o): json.dump(o, open(os.path.join(D, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
status = {"run": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "sources": {}}

# ---- CBP nationwide drug seizures (Southwest border, by month and AOR) ----
CBP_PAGE = "https://www.cbp.gov/document/stats/nationwide-drug-seizures"
def cbp():
    html = get(CBP_PAGE).decode("utf-8", "ignore")
    links = re.findall(r'href="([^"]*nationwide-drugs[^"]*\.csv)"', html)
    if not links: raise RuntimeError("no CSV link on CBP page")
    url = urllib.parse.urljoin(CBP_PAGE, links[0])
    rows = list(csv.DictReader(io.StringIO(get(url).decode("utf-8-sig", "ignore"))))
    keep = {"Fentanyl": "fentanyl", "Methamphetamine": "methamphetamine", "Cocaine": "cocaine"}
    series, aor = {}, {}
    for r in rows:
        if r.get("Region") != "Southwest Border" or r.get("Drug Type") not in keep: continue
        fy = int(r["FY"][:4]); m = MON.index(r["Month (abbv)"].upper()[:3]) + 1
        y = fy - 1 if m >= 10 else fy; ym = f"{y}-{m:02d}"; d = keep[r["Drug Type"]]
        lb = float(r["Sum Qty (lbs)"] or 0)
        series.setdefault(d, {}).setdefault(ym, 0); series[d][ym] += lb
        a = r["Area of Responsibility"].title()
        aor.setdefault(a, {}).setdefault(d, {}).setdefault(ym, 0); aor[a][d][ym] += lb
    months = sorted({m for s in series.values() for m in s})
    out = {"title": "CBP drug seizures at the Southwest border", "unit": "pounds seized per month (Border Patrol + Field Operations)",
           "source_url": url, "landing_url": CBP_PAGE, "cites": ["CBP_SEIZ_CSV"], "first": months[0], "last": months[-1],
           "note": "Seizure weights measure enforcement activity as well as trafficking. They are not a measure of drug flow, and they do not show any link to overdose deaths.",
           "national": {d: [{"m": k, "lb": round(v, 1), "url": url} for k, v in sorted(s.items())] for d, s in series.items()},
           "aor": {a: {d: [{"m": k, "lb": round(v, 1), "url": url} for k, v in sorted(s.items())] for d, s in v.items()} for a, v in sorted(aor.items())}}
    save("seizures.json", out); return f"{months[0]}..{months[-1]}"

# ---- CDC VSRR provisional overdose deaths (12-month ending) ----
CDC = "https://data.cdc.gov/resource/xkb8-kh2a.json"
def cdc():
    out = {"title": "Provisional drug overdose deaths, 12 months ending", "unit": "deaths in the 12 months ending each month (predicted value where CDC gives one)",
           "landing_url": "https://www.cdc.gov/nchs/nvss/vsrr/drug-overdose-data.htm", "cites": ["CDC_VSRR"], "series": {},
           "note": "Provisional counts are revised as death records are completed. Shown beside seizures for context only; no causal link is implied."}
    for st in ["US", "AZ", "CA", "NM", "TX"]:
        q = CDC + "?" + urllib.parse.urlencode({"state": st, "indicator": "Number of Drug Overdose Deaths", "$limit": 5000})
        rows = json.loads(get(q))
        pts = []
        for r in rows:
            m = MON.index(r["month"][:3].upper()) + 1 if not r["month"].isdigit() else int(r["month"])
            v = r.get("predicted_value") or r.get("data_value")
            if v: pts.append({"m": f"{r['year']}-{m:02d}", "v": round(float(str(v).replace(",", ""))), "url": q})
        out["series"][st] = sorted([p for p in pts if p["m"] >= "2019-01"], key=lambda p: p["m"])
    allm = [p["m"] for p in out["series"]["US"]]; out["first"], out["last"] = allm[0], allm[-1]
    save("overdoses.json", out); return f"{allm[0]}..{allm[-1]}"

# ---- SESNSP victims of intentional homicide by state and month ----
SES_BASE = "https://repodatos.atdt.gob.mx/api_update/sesnsp/incidencia_delictiva/"
ESM = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
def sesnsp():
    t = dt.date.today(); last = None
    for k in range(0, 14):
        y, m = t.year, t.month - k
        while m <= 0: m += 12; y -= 1
        u = f"{SES_BASE}IDVFC_NM_{ESM[m-1]}{str(y)[2:]}.csv"
        try: raw = get(u, 180)
        except Exception: continue
        if raw[:200].lstrip().startswith(b"<"): continue
        last = (u, raw); break
    if not last: raise RuntimeError("SESNSP files not reachable (Akamai 403 or not published)")
    u, raw = last
    txt = raw.decode("latin-1") if b"\xf1" in raw[:20000] or b"\xe9" in raw[:20000] else raw.decode("utf-8-sig", "ignore")
    rd = csv.DictReader(io.StringIO(txt)); cols = rd.fieldnames
    sub = next(c for c in cols if "ubtipo" in c); ent = next(c for c in cols if c.lower().startswith("clave_ent") or c.lower() == "clave_ent")
    yr = next(c for c in cols if c.lower() in ("año", "ano", "aÃ±o") or c.lower().startswith("a"))
    agg = {}
    for r in rd:
        if r[sub].strip().lower() != "homicidio doloso": continue
        e = int(r[ent])
        for i, mm in enumerate(MESES):
            v = r.get(mm, "")
            if v.strip() == "": continue
            key = (e, f"{int(r[yr])}-{i+1:02d}"); agg[key] = agg.get(key, 0) + int(float(v))
    st = {}
    for (e, ym), v in agg.items(): st.setdefault(str(e), []).append({"m": ym, "v": v, "url": u})
    for v in st.values(): v.sort(key=lambda p: p["m"])
    months = sorted({ym for _, ym in agg})
    while months and sum(agg.get((e, months[-1]), 0) for e in range(1, 33)) == 0: months.pop()
    for k in st: st[k] = [p for p in st[k] if p["m"] <= months[-1]]
    save("violence.json", {"title": "Victims of intentional homicide (homicidio doloso), by state and month", "source_url": u,
        "landing_url": "https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva", "cites": ["SESNSP_VIC"],
        "unit": "victims per month, from state prosecutors' preliminary investigation files", "first": months[0], "last": months[-1], "states": st,
        "note": "Counts are open investigation files reported by state prosecutors. Under-recording varies by state, and disappearances are counted separately."})
    return f"{months[0]}..{months[-1]}"

# Fallback: elcri.men's public mirror of the same SESNSP victims file (Diego Valle-Jones), when SESNSP blocks automated access.
ELC = "https://data.diegovalle.net/elcrimen/nm-estatal-victimas.csv.gz"
def elcrimen():
    import gzip
    rd = csv.DictReader(io.StringIO(gzip.decompress(get(ELC, 240)).decode("utf-8")))
    agg, pop = {}, {}
    for r in rd:
        if r["subtipo"] != "HOMICIDIO DOLOSO": continue
        k = (r["state_code"], r["date"]); agg[k] = agg.get(k, 0) + float(r["count"] or 0)
        if r["population"] and r["modalidad"] == "CON ARMA DE FUEGO":
            pk = (r["state_code"], r["date"][:4]); pop.setdefault(pk, {})[(r["sex"], r["age_group"])] = int(float(r["population"]))
    months = sorted({m for _, m in agg})
    while months and sum(v for (e, m), v in agg.items() if m == months[-1]) == 0: months.pop()
    months = [m for m in months if m >= "2019-01"]
    st = {}
    for (e, m), v in agg.items():
        if m in months: st.setdefault(e, []).append({"m": m, "v": int(round(v)), "url": ELC})
    for v in st.values(): v.sort(key=lambda p: p["m"])
    popy = {f"{e}|{y}": sum(d.values()) for (e, y), d in pop.items() if y >= "2019"}
    save("violence.json", {"title": "Victims of intentional homicide (homicidio doloso), by state and month", "source_url": ELC,
        "landing_url": "https://elcri.men/datos.html", "official_url": "https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva",
        "cites": ["SESNSP_VIC", "ELCRIMEN"], "substitute": True,
        "unit": "victims per month, from state prosecutors' investigation files", "first": months[0], "last": months[-1], "states": st,
        "population": popy, "population_note": "Population by state and year as carried in the elcri.men file (CONAPO projections), used for rates per 100,000.",
        "note": "SESNSP's own open-data host returns HTTP 403 to automated requests (tested from this server and from GitHub Actions), so the same SESNSP victims data is read from elcri.men's public mirror. Counts are prosecutors' open files; under-recording varies by state, and disappearances are counted separately."})
    return f"{months[0]}..{months[-1]} (elcri.men mirror)"
def sesnsp_any():
    try: return sesnsp()
    except Exception as e1:
        return elcrimen() + f"; direct SESNSP failed: {str(e1)[:80]}"

for name, fn in [("cbp", cbp), ("cdc_vsrr", cdc), ("sesnsp", sesnsp_any)]:
    try: status["sources"][name] = {"ok": True, "range": fn()}
    except Exception as e: status["sources"][name] = {"ok": False, "error": str(e)[:200]}
    print(name, status["sources"][name])
save("monthly_status.json", status)
