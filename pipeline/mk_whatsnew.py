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
   dev("2026-10-28", "Sinaloa municipality, northern Sinaloa", "Security Secretary García Harfuch confirmed that Navy forces killed Jesús 'Chuy' González Peñuelas, described as second in command of 'Chapo Isidro' and the Guasave Cartel and carrying a 5 million dollar US reward, after an attack on naval personnel; the strike falls on a northern Sinaloa group outside the Chapitos-Mayiza split, so federal and US pressure in the state now extends beyond the two warring factions.", C,
       ["x:2115473678267973981", "x:2115470233989488852", "x:2115436801401782361", "x:2115457555740729358", "x:2115428457815433592", "x:2115315389475303441"], ["MEX-2711"], ["sinaloa"]),
   dev("2026-10-27", "Mazatlán prison", "The war has moved inside Mazatlán's prison: Infobae reports a brawl involving Los Chapitos left 12 dead there, and the prison's doctor has since disappeared, which puts the penal system itself among the contested ground.", C,
       ["x:2115105696358265316", {"url": "https://www.eluniversal.com.mx/estados/desaparece-doctor-del-centro-penitenciario-de-mazatlan-emiten-ficha-de-busqueda/", "name": "El Universal", "title": "Doctor at the Mazatlán prison goes missing; search notice issued", "date": "2026-10-27"}, {"url": "https://www.jornada.com.mx/2026/10/27/estados/031n2est?partner=rss", "name": "La Jornada (estados)", "title": "Missing-person notice issued for a priest who disappeared in Culiacán", "date": "2026-10-27"}], ["MEX-2711"], ["sinaloa"]),
   dev("2026-10-24", "Cucurpe, Sonora", "A Navy-led operation killed 'El Meny Carranza', a regional priority target that El Heraldo describes as a Chapitos ally, and arrested four; days later Sonora prosecutors held 'El Chore' of a cell aligned with a Sinaloa faction, placing federal pressure on the war's Sonora flank.", C,
       ["x:2114160766207078813", "x:2114149235188699201", {"url": "https://heraldodemexico.com.mx/nacional/2026/10/24/operativo-conjunto-en-sonora-abaten-el-meny-carranza-presunto-aliado-de-los-chapitos-detienen-personas-915470.html", "name": "El Heraldo de México", "title": "Joint operation in Sonora: \"El Meny Carranza\", alleged ally of \"Los Chapitos\", killed and 4 people arrested", "date": "2026-10-25"}, "x:2114477522511450161"], ["MEX-2712"], ["sinaloa"]),
   dev("2026-10-20", "Mazatlán and Escuinapa", "Near-daily shootings in Mazatlán, including the killing of a C4i operations supervisor, and an attack on a bus driver in Escuinapa show the fighting has settled into southern Sinaloa rather than staying in Culiacán.", C,
       [{"url": "https://www.eluniversal.com.mx/estados/sinaloa-registra-cuatro-asesinatos-y-un-ataque-a-balazos-matan-a-supervisor-operativo-del-c4i-en-mazatlan/", "name": "El Universal", "title": "Sinaloa records four killings and a shooting; C4i operations supervisor killed in Mazatlán", "date": "2026-10-25"}, {"url": "https://x.com/proceso/status/2113457885846143297", "name": "proceso (X @proceso)", "title": "Bus carrying secondary-school students shot at in Escuinapa, Sinaloa (video). Authorities say the attack was a…", "date": "2026-10-23"}, {"url": "https://x.com/noticieristas/status/2113313297046917378", "name": "noticieristas (X @noticieristas)", "title": "▶️ Escuinapa, Sinaloa attack was aimed at the bus driver, who suffered a minor injury, the SSPE confirms…", "date": "2026-10-22"}, {"url": "https://x.com/noticieristas/status/2112600445315162426", "name": "noticieristas (X @noticieristas)", "title": "➡️ Shooting at a #Mazatlán tyre shop leaves one man dead and two workers wounded, in the Luis Echeverría neigh…", "date": "2026-10-20"}], ["MEX-2711"], ["sinaloa"]),
  ]},
 {"id": "cjng", "title": "CJNG: regional commanders face parallel Mexican and US prosecution", "groups": ["cjng"], "regions": ["MEX-2718", "MEX-2720", "MEX-2723", "MEX-2734"], "view": "mx",
  "context": "CJNG is Mexico's most widely spread cartel. Mexican and US authorities now build parallel cases against its regional commanders, while it keeps fighting rivals in Michoacán, Veracruz and the Isthmus.",
  "context_sources": ["IC_CJNG"],
  "developments": [
   dev("2026-10-30", "United States", "US prosecutions are reaching CJNG's cross-border support network, not only its commanders: a US court sentenced a Chinese national to 12 years for helping CJNG traffic drugs and launder money, and the engineer accused of designing a CJNG narco-tunnel into the US became the seventh person charged in the Tijuana tunnel case, where more than a tonne of cocaine was seized.", "Single source",
      ["x:2116201666726805979", "x:2116221093333926231", "x:2115994792165351472"], ["MEX-2706"], ["cjng"]),
   dev("2026-10-28", "Oaxaca", "Navy, federal security and prosecutors' forces arrested Carlos César Cruz Muñoz, 'El Semáforo', whom Riodoce and Infobae describe as a second-tier CJNG regional boss and possible successor to 'El Tanque', taken on 5 October; that is two consecutive heads of the same regional command removed in about three weeks.", C,
       ["x:2115607278833344958", "x:2115641019823968363", "x:2115624663254790516"], ["MEX-2723"], ["cjng"]),
   dev("2026-10-28", "Barranquilla, Colombia", "Colombian authorities arrested two Mexican nationals, Sophia Mourra Lozano ('La Patrona') and Adolfo Paulin González ('Pau'), described as CJNG's main links to the Clan del Golfo, which places a CJNG liaison cell on Colombia's Caribbean coast at the cocaine supply end of its business.", C,
       ["x:2115658129287356796", "x:2115639778091634746"], ["COL-1412"], ["cjng", "clan"]),
   dev("2026-10-22", "Veracruz", "A US grand jury indicted 'El Tanque' Iván Cazarín Molina, a regional CJNG operator, as a Mexican judge threw out his injunction and Veracruz prosecutors added the Las Bajadas massacre: one man facing parallel Mexican and US cases.", C,
       [{"url": "https://x.com/Pajaropolitico/status/2113480553957646670", "name": "Pajaropolitico (X @Pajaropolitico)", "title": "🚨 A federal grand jury in Columbia formally indicted Iván Cazarín Molina, \"El Tanque\", alleged regional CJNG o…", "date": "2026-10-23"}, {"url": "https://x.com/proceso/status/2113490598913069079", "name": "proceso (X @proceso)", "title": "US indicts \"El Tanque\", regional CJNG operator. Facing possible extradition, \"El Tanque\" sought an amparo (inj…", "date": "2026-10-23"}, {"url": "https://x.com/ZETATijuana/status/2113315791483388170", "name": "ZETATijuana (X @ZETATijuana)", "title": "A federal judge dismissed outright the fundamental-rights suit filed by Iván Cazarín Molina, one of the former…", "date": "2026-10-22"}, {"url": "https://www.infobae.com/mexico/2026/10/24/mas-cargos-para-el-tanque-del-cjng-fiscalia-de-veracruz-lo-imputa-por-la-masacre-de-las-bajadas/", "name": "infobae.com", "title": "More charges for CJNG's \"El Tanque\": Veracruz prosecutors charge him over the Las Bajadas massacre - Infobae", "date": "2026-10-25"}], ["MEX-2734"], ["cjng"]),
  ]},
 {"id": "us-pressure", "title": "Terrorist labels, extraditions and US scrutiny", "groups": ["sinaloa", "lnfm", "eln", "pcc", "cv"], "regions": [], "view": "all",
  "context": "Since the US listed major cartels as Foreign Terrorist Organizations, allied governments have copied the labels and extraditions have sped up. The labels change the legal and financial exposure of anyone who does business with these groups.",
  "context_sources": ["FTO"],
  "developments": [
   dev("2026-10-25", "Salta and Zárate, Argentina", "Two Argentine court cases behind the new listing show different Mexican footholds: a Bolivia-based Sinaloa branch flying cocaine into Salta for export to Europe through Paraná river ports, and a small CJNG cell that tested a Belgium-to-Zárate MDMA shipment paid through hawala and crypto; specialists found no documented La Nueva Familia Michoacana presence, so the label outruns the evidence for that group.", S,
       [{"url": "https://airedesantafe.com.ar/policiales/los-carteles-mexicanos-ya-tienen-ruta-la-argentina-sinaloa-sale-el-norte-cocaina-y-jalisco-entra-los-puertos-sinteticos-n674343", "name": "airedesantafe.com.ar", "title": "Mexican cartels now have a route in Argentina: Sinaloa leaves through the north with cocaine and Jalisco comes", "date": "2026-10-26"}], ["ARG-1303", "ARG-1295"], ["sinaloa", "cjng", "lnfm"]),
   dev("2026-10-22", "Argentina", "Milei's government added the Sinaloa Cartel, La Nueva Familia Michoacana, the ELN and FARC-EP to Argentina's terrorist list, matching the US designations.", C,
       [{"url": "https://x.com/noticieristas/status/2113352548702961788", "name": "noticieristas (X @noticieristas)", "title": "#Argentina 🇦🇷 | Argentina's government, led by President Javier Milei, added the Sinaloa Cartel and La Nueva F…", "date": "2026-10-22"}, {"url": "https://x.com/Riodoce_mx/status/2113342121222778960", "name": "Riodoce_mx (X @Riodoce_mx)", "title": "The Government of #Argentina, led by President Javier Milei, declared Mexico's #Sinaloa #Cartel and La Nueva F…", "date": "2026-10-22"}], [], ["sinaloa", "lnfm", "eln"]),
   dev("2026-10-24", "Brazil", "The US terrorist designation of the PCC and Comando Vermelho became a runoff issue: Flávio Bolsonaro backs it, while Lula raises sovereignty concerns.", S,
       ["x:2114122561965453668"], ["BRA-1311"], ["pcc", "cv"]),
   dev("2026-10-24", "Colombia to US", "Colombia extradited 'Mocho Olmedo', who had been shielded under Petro's 'Total Peace' policy, and US prosecutors welcomed it: the new government is reversing the old protections.", S,
       [{"url": "https://www.infobae.com/colombia/2026/10/24/fiscal-federal-de-estados-unidos-reacciono-a-la-extradicion-de-mocho-olmedo-uno-de-los-protegidos-de-la-paz-total-de-petro/", "name": "infobae.com", "title": "US federal prosecutor reacts to extradition of 'Mocho Olmedo', one of those protected under Petro's Total Peac", "date": "2026-10-25"}], [], ["exfarc"]),
   dev("2026-10-25", "Bolivia", "Bolivia's two most recent attorneys general are under US scrutiny over alleged links to drug trafficking, which brings US pressure to the top of Bolivia's justice system.", S,
       [{"url": "https://www.infobae.com/america/america-latina/2026/10/25/mariaca-y-lanchipa-los-dos-ultimos-fiscales-de-bolivia-estan-en-la-mira-de-eeuu-por-presuntos-vinculos-con-el-narcotrafico/", "name": "Infobae America", "title": "Mariaca and Lanchipa, Bolivia's last two attorneys general, under US scrutiny over alleged drug-trafficking li", "date": "2026-10-25"}], [], []),
  ]},
 {"id": "colombia", "title": "Colombia: all-out offensive on ELN and dissidents", "groups": ["eln", "exfarc"], "regions": ["COL-1404"], "view": "sa",
  "context": "President de la Espriella has ended peace talks and ordered a full military offensive against the ELN and FARC dissidents. Both groups are fighting each other and the state over Cauca's coca and mining corridors.",
  "context_sources": ["IC_ELN", {"url": "https://x.com/Primicias/status/2112341831094538510", "name": "Primicias (X @Primicias)", "title": "Colombian President Abelardo de la Espriella ruled out any peace negotiation with the ELN and FARC dissidents …", "date": "2026-10-20"}],
  "developments": [
   dev("2026-10-27", "Cúcuta", "Violence has reached Cúcuta, Colombia's main crossing to Venezuela: former government secretary and mayoral hopeful Miguel Castellanos was shot dead on a road and an explosive attack near the border wounded three; no group has been publicly identified as responsible.", C,
       [{"url": "https://eltiempo.com/colombia/otras-ciudades/nuevos-detalles-del-asesinato-de-miguel-castellanos-exsecretario-de-gobierno-y-aspirante-a-la-alcaldia-que-fue-asesinado-en-una-via-de-cucuta-3596537", "name": "eltiempo.com", "title": "Nuevos detalles del asesinato de Miguel Castellanos, exsecretario de Gobierno y aspirante a la Alcaldía que fu", "date": "2026-10-27"}, {"url": "https://primicias.ec/internacional/asesinato-colombia-precandidato-alcaldia-cucuta-miguel-castellanos-135791", "name": "primicias.ec", "title": "Pre-candidate for mayor of Cúcuta, Miguel Castellanos, murdered in Colombia", "date": "2026-10-27"}, {"url": "https://semana.com/nacion/cucuta/articulo/los-detalles-desconocidos-del-asesinato-de-miguel-castellanos-precandidato-a-la-alcaldia-de-cucuta/202659", "name": "semana.com", "title": "Los detalles desconocidos del asesinato de Miguel Castellanos, precandidato a la Alcaldía de Cúcuta - Semana", "date": "2026-10-27"}, {"url": "https://semana.com/nacion/cucuta/articulo/atentado-con-explosivo-en-cucuta-cerca-de-la-frontera-entre-colombia-y-venezuela-hay-tres-heridos/202653", "name": "semana.com", "title": "Atentado con explosivo en Cúcuta, cerca a la frontera entre Colombia y Venezuela: tres heridos - Semana", "date": "2026-10-27"}, "x:2115098759017251125"], ["COL-1421"], []),
   dev("2026-10-24", "Cauca", "The 'Ónix' bombing killed 10 ELN members, including two commanders such as 'Marcos Pacífico'; Semana reports the camp had been under US surveillance, a sign of US intelligence support behind the offensive.", C,
       ["x:2114502265247879310", "x:2114396616748577127", {"url": "https://dw.com/es/diez-guerrilleros-son-abatidos-en-bombardeo-contra-el-eln-en-colombia/a-79756947", "name": "dw.com", "title": "Diez guerrilleros son abatidos en bombardeo contra el ELN en Colombia", "date": "2026-10-25"}, {"url": "https://semana.com/nacion/articulo/asi-fue-vigilado-por-estados-unidos-el-campamento-de-alias-marcos-pacifico-de-eln-abatido-tras-bombardeo-de-las-fuerza-militares/202600", "name": "semana.com", "title": "Así fue vigilado por Estados Unidos el campamento de alias Marcos Pacífico de ELN, abatido tras bombardeo de l", "date": "2026-10-25"}], ["COL-1404"], ["eln"]),
   dev("2026-10-24", "Antioquia", "A soldier who went missing after a drone attack apparently carried out by dissidents was found alive six days later; armed drones are now part of the dissidents' toolkit.", S,
       [{"url": "https://infobae.com/colombia/2026/10/24/hallan-vivo-a-soldado-desaparecido-en-antioquia-llevaba-seis-dias-sin-rastro-tras-ataque-con-drones-al-parecer-ejecutados-por-las-disidencias", "name": "infobae.com", "title": "Soldier missing in Antioquia found alive after six days, following a drone attack apparently carried out by di", "date": "2026-10-25"}], [], ["exfarc"]),
  ]},
 {"id": "ecuador", "title": "Ecuador: Los Lobos vs Los Choneros", "groups": ["lobos", "choneros"], "regions": ["ECU-1280", "ECU-1282"], "view": "sa",
  "context": "Los Lobos and Los Choneros are fighting over Ecuador's cocaine export corridor, from prisons to the Manabí and Guayas coast. Inside the state, police and prison staff collude with the gangs.",
  "context_sources": ["IC_ECUADOR", "IC_LOBOS", "IC_CHONEROS"],
  "developments": [
   dev("2026-10-29", "Ecuador to US", "Ecuador extradited alias 'Churrón', described as a Los Choneros leader, to the United States along with Daniel Salcedo and Ronald Herrera, who are linked to the Fernando Villavicencio murder case; the transfer puts a Choneros commander under US jurisdiction and outside the Ecuadorian prisons where the gang war is fought. Primicias reads the extradition of eight defendants as aimed at one transnational network tying the Choneros leadership to FARC cocaine suppliers, cryptocurrency launderers and contacts inside the Ecuadorian state, which shifts the case from gang violence toward the gang's supply and money chain.", C,
       ["x:2115851653161091213", "u:https://www.eluniversal.com.mx/mundo/ecuador-extradita", "x:2115975417014169762"], [], ["choneros"]),
   dev("2026-10-25", "Ecuador prisons", "Two new prison massacres left at least eight inmates dead: the prisons are still a front in the gang war.", S,
       [{"url": "https://rpp.pe/mundo/latinoamerica/ecuador-al-menos-ocho-presos-muertos-y-diez-heridos-en-dos-nuevas-masacres-en-carceles-del-pais-noticia-1714289", "name": "rpp.pe", "title": "Ecuador: at least eight inmates dead and ten wounded in two new prison massacres", "date": "2026-10-25"}], [], ["lobos", "choneros"]),
   dev("2026-10-24", "Quito / Pichincha", "Security forces broke up a Los Lobos cell ('El Gordo Lucho') and arrested a Choneros member tied to kidnapping and extortion in Quito, so the fight now reaches into the highland capital.", S,
       [{"url": "https://metroecuador.com.ec/noticias/2026/10/24/ejercito-neutraliza-una-celula-de-los-lobos-en-pichincha-cae-alias-el-gordo-lucho", "name": "metroecuador.com.ec", "title": "Alias 'El Gordo Lucho', linked to 'Los Lobos', falls in Pichincha – Metro Ecuador", "date": "2026-10-25"}, {"url": "https://metroecuador.com.ec/noticias/2026/10/24/cae-alias-la-j-presunto-integrante-de-los-choneros-vinculado-a-secuestros-y-extorsiones-en-quito", "name": "metroecuador.com.ec", "title": "Alias 'La J', alleged member of 'Los Choneros', falls in Quito – Metro Ecuador", "date": "2026-10-25"}], [], ["lobos", "choneros"]),
  ]},
 {"id": "tda", "title": "Tren de Aragua across the region", "groups": ["tda"], "regions": [], "view": "sa",
  "context": "Tren de Aragua spread from Venezuela's prisons into a network of extortion and sexual-exploitation cells across the Andes and Chile. Its cells now face prosecution in the countries they moved into.",
  "context_sources": ["IC_TDA"],
  "developments": [
   dev("2026-10-24", "Santiago, Chile", "The trial of 16 'Piratas de Aragua' members began, covering the murder of Venezuelan dissident Ronald Ojeda, the case that tied TdA cells to a political killing in Chile.", S,
       [{"url": "https://www.biobiochile.cl/noticias/nacional/region-metropolitana/2026/10/24/comenzo-juicio-a-16-miembros-de-piratas-de-aragua-por-homicidio-de-ronald-ojeda-y-otros-delitos.shtml", "name": "biobiochile.cl", "title": "Trial begins for 16 members of \"Piratas de Aragua\" for the murder of Ronald Ojeda and other crimes | BioBioChi", "date": "2026-10-25"}], [], ["tda"]),
   dev("2026-10-25", "Lima, Peru", "InSight Crime traces TdA's rise in Lima to extortion of sex workers, with killings of those who refused to pay: its money comes from local predation, not just trafficking.", S,
       ["x:2114478830752592172"], [], ["tda"]),
  ]},
 {"id": "haiti", "title": "Haiti: gangs over the state", "groups": ["haiti"], "regions": ["HTI-1388"], "view": "all",
  "context": "The Viv Ansanm gang coalition controls most of Port-au-Prince and has repeatedly blocked the political transition. Neighbours and the anti-gang force respond on security terms.",
  "context_sources": ["IC_HAITI"],
  "developments": [
   dev("2026-10-27", "Santo Domingo", "Foreign Minister Víctor Bisonó said Dominican troops are staying out of the international military operations against Haiti's gangs, offering only diplomatic, humanitarian and logistical support: Santo Domingo is militarising its own side of the border while keeping out of the fight inside Haiti.", S,
       [{"url": "https://www.infobae.com/republica-dominicana/2026/10/27/republica-dominicana-no-participara-en-las-operaciones-militares-contra-las-pandillas-en-haiti/", "name": "Infobae America", "title": "Dominican Republic will not take part in military operations against gangs in Haiti", "date": "2026-10-27"}], [], ["haiti"]),
   dev("2026-10-23", "Haiti", "InSight Crime reports that gang control has once again pushed back Haiti's elections.", S,
       [{"url": "https://insightcrime.org/news/organized-crime-postponed-democracy-in-haiti-again/", "name": "InSight Crime", "title": "Organized Crime Postponed Democracy in Haiti, Again", "date": "2026-10-23"}], ["HTI-1388"], ["haiti"]),
   dev("2026-10-25", "Dominican border", "President Abinader sent two more battalions to the Haitian border, so the Dominican response to the crisis remains a military one.", S,
       [{"url": "https://www.infobae.com/republica-dominicana/2026/10/25/el-presidente-luis-abinader-refuerza-la-seguridad-en-la-frontera-sur-con-dos-batallones-ante-la-crisis-de-haiti/", "name": "Infobae America", "title": "President Luis Abinader reinforces security on the southern border with two battalions amid Haiti's crisis", "date": "2026-10-25"}], [], ["haiti"]),
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
