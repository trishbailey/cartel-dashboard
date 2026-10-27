"""Build data/whatsnew.json: a digested 'What's new' section grouped under ongoing trends.
The analytic text below is written by the reasoner (Grok Bot routine; see docs/DIGEST.md). This script only
resolves source references into {url,name,title,date} so the UI can footnote them:
  "x:<post id>"   -> post in data/xfeed.json (X posts are sourcing only, never pasted as content)
  "u:<url>"       -> article in data/events.json or data/breaking.json
  "<ID>"          -> id in data/sources.json (kept as-is)
Run: python3 pipeline/mk_whatsnew.py  (then python3 pipeline/validate.py)"""
import json, os, datetime
D = os.path.join(os.path.dirname(__file__), "..", "data")
L = lambda p: json.load(open(os.path.join(D, p), encoding="utf-8"))
XF = {p["id"]: p for p in L("xfeed.json")["posts"]}
EV = {e["url"]: e for e in L("events.json")["events"]}
SRC = {s["id"] for s in L("sources.json")["sources"]}
ACC = {a.get("handle"): a.get("name") for a in L("xfeed.json").get("accounts", []) if isinstance(a, dict)}

def ref(r):
    if isinstance(r, dict):  # pinned source whose X post has aged out of xfeed.json
        return r
    if r.startswith("x:"):
        p = XF[r[2:]]; t = (p.get("text_en") or p["text"]).split("http")[0].strip()
        return {"url": p["url"], "name": f"{ACC.get(p['handle']) or p['handle']} (X @{p['handle']})", "title": t[:110] + ("…" if len(t) > 110 else ""), "date": p["created_at"][:10]}
    if r.startswith("u:"):
        u = r[2:]; m = [k for k in EV if k.startswith(u)]; assert len(m) == 1, u; u = m[0]; e = EV[u]
        return {"url": u, "name": e.get("source", "").split(" - ")[0] or u.split("/")[2], "title": (e.get("title_en") or e.get("title") or "")[:110], "date": e.get("date", "")}
    assert r in SRC, r
    return r

def dev(date, place, text, ver, srcs, regions=(), groups=()):
    return {"date": date, "place": place, "text": text, "verification": ver, "regions": list(regions), "groups": list(groups), "sources": [ref(s) for s in srcs]}

C, S, O = "Confirmed", "Single source", "Official claim only"
trends = [
 {"id": "sinaloa-war", "title": "Sinaloa civil war: Chapitos vs Mayiza", "groups": ["sinaloa"], "regions": ["MEX-2711", "MEX-2712"], "view": "mx",
  "context": "The split between El Chapo's sons (Chapitos) and the Zambada faction (Mayiza), now in its second year, has spread from Culiacán to Mazatlán, southern Sinaloa and neighbouring states. It drives the highest sustained violence in Mexico and shapes who controls Pacific fentanyl and cocaine routes.",
  "context_sources": ["ACLED_SIN", "ELPAIS_SIN"],
  "developments": [
   dev("2026-10-24", "Cucurpe, Sonora", "A Navy-led operation killed 'El Meny Carranza', a regional priority target that El Heraldo describes as a Chapitos ally, and arrested four; days later Sonora prosecutors held 'El Chore' of a cell aligned with a Sinaloa faction, placing federal pressure on the war's Sonora flank.", C,
       ["x:2114160766207078813", "x:2114149235188699201", "u:https://heraldodemexico.com.mx/nacional/2026/10/24/operativo-conjunto-en-sonora-abaten-el-meny-carranza-presunto-aliado-de-los-chapitos-detienen-personas-915470.html", "x:2114477522511450161"], ["MEX-2712"], ["sinaloa"]),
   dev("2026-10-20", "Mazatlán and Escuinapa", "Near-daily shootings in Mazatlán, including the killing of a C4i operations supervisor, and an attack on a bus driver in Escuinapa show the fighting has settled into southern Sinaloa rather than staying in Culiacán.", C,
       ["u:https://www.eluniversal.com.mx/estados/sinaloa-registra-cuatro-asesinatos-y-un-ataque-a-balazos-mata", "x:2113457885846143297", "x:2113313297046917378", "x:2112600445315162426"], ["MEX-2711"], ["sinaloa"]),
  ]},
 {"id": "cjng", "title": "CJNG: regional commanders face parallel Mexican and US prosecution", "groups": ["cjng"], "regions": ["MEX-2718", "MEX-2720", "MEX-2734"], "view": "mx",
  "context": "CJNG is Mexico's most widely spread cartel. Mexican and US authorities now build parallel cases against its regional commanders, while it keeps fighting rivals in Michoacán, Veracruz and the Isthmus.",
  "context_sources": ["IC_CJNG"],
  "developments": [
   dev("2026-10-22", "Veracruz", "A US grand jury indicted 'El Tanque' Iván Cazarín Molina, a regional CJNG operator, as a Mexican judge threw out his injunction and Veracruz prosecutors added the Las Bajadas massacre: one man facing parallel Mexican and US cases.", C,
       ["x:2113480553957646670", "x:2113490598913069079", "x:2113315791483388170", "u:https://www.infobae.com/mexico/2026/10/24/mas-cargos-para-el-tanque-del-cjng-fiscalia-de-veracruz-lo-imputa-por-la-masacre-de-las-bajadas/"], ["MEX-2734"], ["cjng"]),
  ]},
 {"id": "us-pressure", "title": "Terrorist labels, extraditions and US scrutiny", "groups": ["sinaloa", "lnfm", "eln", "pcc", "cv"], "regions": [], "view": "all",
  "context": "Since the US listed major cartels as Foreign Terrorist Organizations, allied governments have copied the labels and extraditions have sped up. The labels change the legal and financial exposure of anyone who does business with these groups.",
  "context_sources": ["FTO"],
  "developments": [
   dev("2026-10-25", "Salta and Zárate, Argentina", "Two Argentine court cases behind the new listing show different Mexican footholds: a Bolivia-based Sinaloa branch flying cocaine into Salta for export to Europe through Paraná river ports, and a small CJNG cell that tested a Belgium-to-Zárate MDMA shipment paid through hawala and crypto; specialists found no documented La Nueva Familia Michoacana presence, so the label outruns the evidence for that group.", S,
       ["u:https://airedesantafe.com.ar/policiales/los-carteles-mexicanos-ya-tienen-ruta-la-argentina"], ["ARG-1303", "ARG-1295"], ["sinaloa", "cjng", "lnfm"]),
   dev("2026-10-22", "Argentina", "Milei's government added the Sinaloa Cartel, La Nueva Familia Michoacana, the ELN and FARC-EP to Argentina's terrorist list, matching the US designations.", C,
       ["x:2113352548702961788", "x:2113342121222778960"], [], ["sinaloa", "lnfm", "eln"]),
   dev("2026-10-24", "Brazil", "The US terrorist designation of the PCC and Comando Vermelho became a runoff issue: Flávio Bolsonaro backs it, while Lula raises sovereignty concerns.", S,
       ["x:2114122561965453668"], ["BRA-1311"], ["pcc", "cv"]),
   dev("2026-10-24", "Colombia to US", "Colombia extradited 'Mocho Olmedo', who had been shielded under Petro's 'Total Peace' policy, and US prosecutors welcomed it: the new government is reversing the old protections.", S,
       ["u:https://www.infobae.com/colombia/2026/10/24/fiscal-federal-de-estados-unidos-reacciono-a-la-extradicion-de-mocho-olmedo-uno-de-los-protegidos-de-la-paz-total-de-petro/"], [], ["exfarc"]),
   dev("2026-10-25", "Bolivia", "Bolivia's two most recent attorneys general are under US scrutiny over alleged links to drug trafficking, which brings US pressure to the top of Bolivia's justice system.", S,
       ["u:https://www.infobae.com/america/america-latina/2026/10/25/mariaca-y-lanchipa"], [], []),
  ]},
 {"id": "colombia", "title": "Colombia: all-out offensive on ELN and dissidents", "groups": ["eln", "exfarc"], "regions": ["COL-1404"], "view": "sa",
  "context": "President de la Espriella has ended peace talks and ordered a full military offensive against the ELN and FARC dissidents. Both groups are fighting each other and the state over Cauca's coca and mining corridors.",
  "context_sources": ["IC_ELN", {"url": "https://x.com/Primicias/status/2112341831094538510", "name": "Primicias (X @Primicias)", "title": "Colombian President Abelardo de la Espriella ruled out any peace negotiation with the ELN and FARC dissidents …", "date": "2026-10-20"}],
  "developments": [
   dev("2026-10-24", "Cauca", "The 'Ónix' bombing killed 10 ELN members, including two commanders such as 'Marcos Pacífico'; Semana reports the camp had been under US surveillance, a sign of US intelligence support behind the offensive.", C,
       ["x:2114502265247879310", "x:2114396616748577127", "u:https://dw.com/es/diez-guerrilleros-son-abatidos-en-bombardeo-contra-el-eln-en-colombia/a-79756947", "u:https://semana.com/nacion/articulo/asi-fue-vigilado-por-estados-unidos-el-campamento-de-alias-marcos-pacifico-de-eln-abatido-tras-bombardeo-de-las-fuerza-militares/202600"], ["COL-1404"], ["eln"]),
   dev("2026-10-24", "Antioquia", "A soldier who went missing after a drone attack apparently carried out by dissidents was found alive six days later; armed drones are now part of the dissidents' toolkit.", S,
       ["u:https://infobae.com/colombia/2026/10/24/hallan-vivo-a-soldado-desaparecido-en-antioquia-llevaba-seis-dias-sin-rastro-tras-ataque-con-drones-al-parecer-ejecutados-por-las-disidencias"], [], ["exfarc"]),
  ]},
 {"id": "ecuador", "title": "Ecuador: Los Lobos vs Los Choneros", "groups": ["lobos", "choneros"], "regions": ["ECU-1280", "ECU-1282"], "view": "sa",
  "context": "Los Lobos and Los Choneros are fighting over Ecuador's cocaine export corridor, from prisons to the Manabí and Guayas coast. Inside the state, police and prison staff collude with the gangs.",
  "context_sources": ["IC_ECUADOR", "IC_LOBOS", "IC_CHONEROS"],
  "developments": [
   dev("2026-10-25", "Ecuador prisons", "Two new prison massacres left at least eight inmates dead: the prisons are still a front in the gang war.", S,
       ["u:https://rpp.pe/mundo/latinoamerica/ecuador-al-menos-ocho-presos-muertos-y-diez-heridos-en-dos-nuevas-masacres-en-carceles-del-pais-noticia-1714289"], [], ["lobos", "choneros"]),
   dev("2026-10-24", "Quito / Pichincha", "Security forces broke up a Los Lobos cell ('El Gordo Lucho') and arrested a Choneros member tied to kidnapping and extortion in Quito, so the fight now reaches into the highland capital.", S,
       ["u:https://metroecuador.com.ec/noticias/2026/10/24/ejercito-neutraliza-una-celula-de-los-lobos-en-pichincha-cae-alias-el-gordo-lucho", "u:https://metroecuador.com.ec/noticias/2026/10/24/cae-alias-la-j-presunto-integrante-de-los-choneros-vinculado-a-secuestros-y-extorsiones-en-quito"], [], ["lobos", "choneros"]),
  ]},
 {"id": "tda", "title": "Tren de Aragua across the region", "groups": ["tda"], "regions": [], "view": "sa",
  "context": "Tren de Aragua spread from Venezuela's prisons into a network of extortion and sexual-exploitation cells across the Andes and Chile. Its cells now face prosecution in the countries they moved into.",
  "context_sources": ["IC_TDA"],
  "developments": [
   dev("2026-10-24", "Santiago, Chile", "The trial of 16 'Piratas de Aragua' members began, covering the murder of Venezuelan dissident Ronald Ojeda, the case that tied TdA cells to a political killing in Chile.", S,
       ["u:https://www.biobiochile.cl/noticias/nacional/region-metropolitana/2026/10/24/comenzo-juicio-a-16-miembros-de-piratas-de-aragua-por-homicidio-de-ronald-ojeda-y-otros-delitos.shtml"], [], ["tda"]),
   dev("2026-10-25", "Lima, Peru", "InSight Crime traces TdA's rise in Lima to extortion of sex workers, with killings of those who refused to pay: its money comes from local predation, not just trafficking.", S,
       ["x:2114478830752592172"], [], ["tda"]),
  ]},
 {"id": "haiti", "title": "Haiti: gangs over the state", "groups": ["haiti"], "regions": ["HTI-1388"], "view": "all",
  "context": "The Viv Ansanm gang coalition controls most of Port-au-Prince and has repeatedly blocked the political transition. Neighbours and the anti-gang force respond on security terms.",
  "context_sources": ["IC_HAITI"],
  "developments": [
   dev("2026-10-27", "Santo Domingo", "Foreign Minister Víctor Bisonó said Dominican troops are staying out of the international military operations against Haiti's gangs, offering only diplomatic, humanitarian and logistical support: Santo Domingo is militarising its own side of the border while keeping out of the fight inside Haiti.", S,
       ["u:https://www.infobae.com/republica-dominicana/2026/10/27/republica-dominicana-no-participara"], [], ["haiti"]),
   dev("2026-10-23", "Haiti", "InSight Crime reports that gang control has once again pushed back Haiti's elections.", S,
       [{"url": "https://insightcrime.org/news/organized-crime-postponed-democracy-in-haiti-again/", "name": "InSight Crime", "title": "Organized Crime Postponed Democracy in Haiti, Again", "date": "2026-10-23"}], ["HTI-1388"], ["haiti"]),
   dev("2026-10-25", "Dominican border", "President Abinader sent two more battalions to the Haitian border, so the Dominican response to the crisis remains a military one.", S,
       ["u:https://www.infobae.com/republica-dominicana/2026/10/25/el-presidente-luis-abinader-refuerza-la-seguridad-en-la-frontera-sur-con-dos-batallones-ante-la-crisis-de-haiti/"], [], ["haiti"]),
  ]},
]
other = [
  dev("2026-10-24", "El Salvador", "El Salvador indicted more than 560 alleged Barrio 18 leaders for about 14,500 crimes since 2012, one of the largest cases under the state of emergency.", S,
      ["x:2113813301628944715"], [], ["b18"]),
]
for t in trends:
    t["context_sources"] = [ref(s) for s in t["context_sources"]]
    t["developments"].sort(key=lambda d: d["date"], reverse=True)
out = {"as_of": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
       "note": "Strategic digest of the last ~7 days, grouped by ongoing trend: leadership, splits and alliances, territory and routes, policy and designations, violence patterns, money. Routine seizures and minor arrests are left out. X posts are used only as sources. Verification: Confirmed = 2+ independent reliable sources; Single source; Official claim only. Status is shown only when sourced counts support it.",
       "trends": trends, "other": other}
json.dump(out, open(os.path.join(D, "whatsnew.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("whatsnew:", [(t["id"], len(t["developments"])) for t in trends], "other", len(other))
