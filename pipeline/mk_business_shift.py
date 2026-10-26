"""Build data/business_shift.json: annual regional series showing how criminal lines of business rose and fell.
Fetched live: CBP Southwest border drug seizures (FY2019+) and USBP Southwest border encounters (FY2019+) from CBP CSVs;
SESNSP extortion victims (2015+) from the elcri.men mirror of the SESNSP victims file (SESNSP's host returns 403 to scripts).
Transcribed (with source URL): USBP SW apprehensions FY2015-FY2018 (CBP PDF FY1960-FY2020), Pemex illegal taps on
refined-fuel pipelines 2015-2025 (IGAVIM, from Pemex transparency answers), UNODC/SIMCI alluvial gold (EVOA) Colombia 2020-2023.
Only complete years are kept. Run: python3 pipeline/mk_business_shift.py"""
import csv, io, gzip, json, os, urllib.request, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=240).read()
CBP = "https://www.cbp.gov/sites/default/files/"
DRUG = [(CBP+"assets/documents/2022-Oct/nationwide-drugs-fy19-fy22.csv", 2019, 2022), (CBP+"2025-11/nationwide-drugs-fy22-fy25.csv", 2023, 2025)]
ENC = [(CBP+"assets/documents/2022-Oct/sbo-encounters-fy19-fy22.csv", 2019, 2022), (CBP+"2026-09/sbo-encounters-fy23-fy26-aug.csv", 2023, 2025)]
BP_PDF = "https://www.cbp.gov/sites/default/files/assets/documents/2021-Aug/US59B8~1.PDF"
BP_PAGE = "https://www.cbp.gov/document/stats/us-border-patrol-fiscal-year-southwest-border-sector-apprehensions-fy-1960-fy-2020"
ELC = "https://data.diegovalle.net/elcrimen/nm-estatal-victimas.csv.gz"
IGAVIM = "https://www.igavim.org/Documentos%20Generados/Reportes/2026%20TomasCland2025.pdf"
def rows(u): return csv.DictReader(io.StringIO(get(u).decode("utf-8-sig")))
def drugs():
    t = collections.defaultdict(float); names = {"Fentanyl": "fentanyl", "Methamphetamine": "meth", "Cocaine": "cocaine", "Marijuana": "marijuana"}
    for u, lo, hi in DRUG:
        for x in rows(u):
            fy = int(x["FY"][:4])
            if lo <= fy <= hi and x["Region"] == "Southwest Border" and x["Drug Type"] in names: t[(names[x["Drug Type"]], fy)] += float(x["Sum Qty (lbs)"] or 0)
    return {k: [{"y": y, "v": round(t[(k, y)]), "url": DRUG[0][0] if y <= 2022 else DRUG[1][0]} for y in range(2019, 2026)] for k in names.values()}
def encounters():
    t = collections.Counter()
    for u, lo, hi in ENC:
        for x in rows(u):
            fy = int(x["Fiscal Year"][:4])
            if lo <= fy <= hi and x["Component"] == "U.S. Border Patrol": t[fy] += float(x["Encounter Count"] or 0)
    old = {2015: 331333, 2016: 408870, 2017: 303916, 2018: 396579}
    return [{"y": y, "v": v, "url": BP_PDF} for y, v in old.items()] + [{"y": y, "v": int(t[y]), "url": ENC[0][0] if y <= 2022 else ENC[1][0]} for y in range(2019, 2026)]
def extortion():
    t = collections.Counter()
    for r in csv.DictReader(io.StringIO(gzip.decompress(get(ELC)).decode("utf-8"))):
        if r["subtipo"] == "EXTORSIÓN": t[int(r["date"][:4])] += float(r["count"] or 0)
    return [{"y": y, "v": int(round(t[y])), "url": ELC} for y in range(2015, 2026)]
TAPS = dict(zip(range(2015, 2026), [5252, 6969, 10363, 14956, 13053, 9132, 10251, 11295, 12005, 10396, 9366]))
GOLD = [(2020, 100752, "https://www.unodc.org/colombia/es/100-752-hectareas-con-evidencias-de-explotacion-de-oro-de-aluvion-evoa.html"),
        (2021, 98567, "https://www.unodc.org/colombia/es/informe-de-explotacion-de-oro-de-aluvion-2021-encontr-98-567-hectareas-con-evidencia-de-esta-practica-en-colombia.html"),
        (2022, 94733, "https://www.unodc.org/colombia/es/informe-de-explotacion-de-oro-de-aluvion-2022.html"),
        (2023, 105060, "https://acmineria.com.co/wp-content/uploads/2026/04/evidencias_de_explotacion_de_oro_de_aluvion_2023_compressed.pdf")]
def main():
    d = drugs()
    S = lambda name, title, url: {"name": name, "title": title, "url": url}
    out = {"title": "How the business shifted", "note": "Annual counts for the region, not per-cartel figures; seizures and arrests also reflect enforcement effort. Describes the record only, no prediction.",
      "panels": [
        {"id": "drugs", "title": "US southwest border drug seizures", "unit": "index, FY2019 = 100 (pounds seized)", "years": "US fiscal years (Oct to Sep)", "indexed": True,
         "series": [{"id": k, "label": l, "points": d[k]} for k, l in [("fentanyl", "Fentanyl"), ("meth", "Methamphetamine"), ("cocaine", "Cocaine"), ("marijuana", "Marijuana")]],
         "sources": [S("US Customs and Border Protection", "Drug seizure statistics FY2019-FY2022 (CSV)", DRUG[0][0]), S("US Customs and Border Protection", "Drug seizure statistics FY2022-FY2025 (CSV)", DRUG[1][0])]},
        {"id": "extortion", "title": "Extortion victims, Mexico", "unit": "victims in prosecutors' case files per year", "years": "calendar years",
         "series": [{"id": "extortion", "label": "Extortion", "points": extortion()}],
         "sources": [S("SESNSP via elcri.men mirror", "Victims of crime, fuero común (state-level file)", ELC)]},
        {"id": "fuel", "title": "Illegal taps on Pemex fuel pipelines", "unit": "taps found per year (refined-fuel pipelines, excluding LP gas)", "years": "calendar years",
         "series": [{"id": "fuel", "label": "Fuel theft (huachicol)", "points": [{"y": y, "v": v, "url": IGAVIM} for y, v in TAPS.items()]}],
         "sources": [S("IGAVIM, from Pemex transparency answers", "Tomas clandestinas 2025 report", IGAVIM)]},
        {"id": "migrants", "title": "Border Patrol southwest border encounters", "unit": "people encountered per year, a proxy for demand for migrant smuggling", "years": "US fiscal years (Oct to Sep); from March 2020 includes Title 42 expulsions", "proxy": True,
         "series": [{"id": "migrants", "label": "Migrant smuggling (proxy)", "points": encounters()}],
         "sources": [S("US Customs and Border Protection", "USBP Southwest Border Sector Apprehensions FY1960-FY2020", BP_PAGE), S("US Customs and Border Protection", "Southwest land border encounters FY2019-FY2022 (CSV)", ENC[0][0]), S("US Customs and Border Protection", "Southwest land border encounters FY2023-FY2026 (CSV)", ENC[1][0])]},
        {"id": "gold", "title": "Alluvial gold mining, Colombia", "unit": "hectares with evidence of alluvial gold exploitation (EVOA, on land)", "years": "calendar years; earlier UNODC years used a different method",
         "series": [{"id": "gold", "label": "Illegal gold mining", "points": [{"y": y, "v": v, "url": u} for y, v, u in GOLD]}],
         "sources": [S("UNODC / SIMCI", f"Alluvial gold exploitation (EVOA) {y}", u) for y, _, u in GOLD]}]}
    json.dump(out, open(os.path.join(ROOT, "data/business_shift.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for p in out["panels"]:
        for s in p["series"]: print(s["id"], [(x["y"], x["v"]) for x in s["points"]])
if __name__ == "__main__": main()
