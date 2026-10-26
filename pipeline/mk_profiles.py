"""Build data/profiles.json (group profile cards) and register any new sources in data/sources.json.
Facts are hand-curated from cited outlets; membership_series holds only published figures (never interpolated)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = os.path.join(ROOT, "data")
NEW = [
 ("ELPAIS_PCC","PCC, la hermandad de los criminales","El País","https://elpais.com/especiales/2020/pcc-la-hermandad-de-los-criminales-en-brasil/","2020"),
 ("G1_PCC40K","Como em 20 anos o PCC saltou de facção com 5 mil criminosos para máfia com 40 mil membros","G1","https://g1.globo.com/sp/sao-paulo/noticia/2025/09/22/como-em-20-anos-o-pcc-saltou-de-faccao-com-5-mil-criminosos-para-virar-mafia-com-40-mil-membros.ghtml","2025-09-22"),
 ("EXPRESO_EC","Crisis en Ecuador: el pasado y presente de los grupos terroristas","Expreso (Ecuador)","https://www.expreso.ec/actualidad/crisis-ecuador-pasado-presente-grupos-terrorista-rivales-daniel-noboa-tiguerones-lagartos-choneros-185939.html","2024-01"),
 ("ELUNIVERSO_LOBOS","Los Lobos: origen, cabecillas y poder de la banda","El Universo","https://www.eluniverso.com/noticias/los-lobos-origen-cabecillas-y-poder-de-la-banda-que-ee-uu-catalogo-como-terrorista-nota/","2025"),
 ("PRIMICIAS_BANDAS","En casi 40 años el crimen en Ecuador pasó de tener una banda a más de 22","Primicias","https://www.primicias.ec/noticias/seguridad/crimen-organizado-ecuador-bandas-narcotrafico/","2024"),
 ("JORNADA_CJNG","Reconoce la PGR que el CJNG tiene la mayor presencia en varias entidades","La Jornada","https://www.jornada.com.mx/2017/05/04/politica/005n1pol","2017-05-04"),
 ("NARCODATA_CJNG","Cártel de Jalisco opera en 27 estados del país","Animal Político (NarcoData)","https://narcodata.animalpolitico.com/cartel-jalisco-27-estados/","2020"),
 ("IC_GULF_ES","Cartel del Golfo: historia, líderes y facciones criminales","InSight Crime","https://insightcrime.org/es/noticias-crimen-organizado-mexico/cartel-del-golfo-perfil/","2024"),
 ("ELPAIS_TOCORON","Venezuela despliega 11.000 efectivos para tomar la cárcel desde la que gobierna el Tren de Aragua","El País","https://elpais.com/internacional/2023-09-21/venezuela-despliega-11000-efectivos-para-tomar-la-carcel-desde-la-que-gobierna-el-tren-de-aragua.html","2023-09-21"),
 ("BBC_TDA","El Tren de Aragua: así opera la megabanda de Venezuela","BBC News Mundo","https://www.bbc.com/mundo/articles/crg4yl8g3n0o","2023-09"),
 ("ELTIEMPO_CLAN","Cómo está operando hoy el Clan del Golfo","El Tiempo","https://www.eltiempo.com/politica/proceso-de-paz/como-esta-operando-hoy-el-clan-del-golfo-el-grupo-ilegal-con-mas-presencia-en-el-pais-y-al-que-el-gobierno-le-abrio-las-puertas-de-la-paz-total-3388098","2024"),
 ("SILLA_GAO23","Cifras secretas del Gobierno confirman que todos los grupos armados crecieron","La Silla Vacía","https://www.lasillavacia.com/silla-nacional/cifras-secretas-del-gobierno-confirman-que-todos-los-grupos-armados-crecieron/","2024"),
 ("INFOBAE_GAO25","Se disparó el número de miembros de grupos criminales en Colombia entre 2024 y 2025","Infobae","https://www.infobae.com/colombia/2026/01/30/indepaz-revelo-cifras-de-crecimiento-de-grupos-criminales-en-colombia-entre-2024-y-2025/","2026-01-30"),
 ("CARACOL_GAO26","Cerca de 30.000 integrantes conforman grupos armados y delincuenciales en Colombia","Caracol Radio","https://caracol.com.co/2026/08/26/cerca-de-30000-integrantes-conforman-grupos-armados-y-delincuenciales-en-colombia/","2026-08-26"),
 ("FIP_GAO25","Lo que dicen las nuevas cifras sobre el aumento de integrantes de grupos armados","Fundación Ideas para la Paz","https://ideaspaz.org/publicaciones/investigaciones-analisis/2025-11/lo-que-dicen-las-nuevas-cifras-sobre-el-aumento-de-integrantes-de-grupos-armados-en-colombia","2025-11"),
 ("ELMUNDO_SV_70K","Gobierno oficializa 70 mil pandilleros en las calles","Diario El Mundo (El Salvador)","https://diario.elmundo.sv/nacionales/gobierno-oficializa-70-mil-pandilleros-en-las-calles-y-advierte-no-revertira-medidas","2022-04"),
 ("UK_CPIN_SV","Country policy and information note: fear of gangs, El Salvador","UK Home Office","https://www.gov.uk/government/publications/el-salvador-country-policy-and-information-notes/country-policy-and-information-note-fear-of-gangs-el-salvador-december-2025-accessible","2025-12"),
 ("CRS_SV_EXC","El Salvador's State of Exception and U.S. Interests","Congressional Research Service","https://www.congress.gov/crs_external_products/IN/PDF/IN12510/IN12510.2.pdf","2025-02"),
]
S = lambda y,lo,hi,src,note="": {"year":y,"low":lo,"high":hi,"source":src,**({"note":note} if note else {})}
P = [
 {"id":"sinaloa","name":"Sinaloa Cartel","abbr":None,"aka":"Cártel de Sinaloa; split into Chapitos and Mayiza factions","what":"Mexico's oldest major trafficking organisation, now split into two warring factions.","what_c":["IC_SINALOA"],
  "founded":"Late 1980s, Sinaloa (Mexico)","founded_c":["IC_SINALOA"],"biz":["chapitos","mayiza"],
  "more":[["Grew out of the Guadalajara-era networks and was long run as a federation of semi-autonomous bosses (Guzmán, Zambada and others).",["IC_SINALOA"]],
          ["Since September 2024 the Chapitos (sons of Joaquín Guzmán) and the Mayiza (Zambada loyalists) have fought each other in Sinaloa after Ismael Zambada was taken to the US.",["ELPAIS_SIN","ACLED_SIN"]],
          ["US agencies name it a main supplier of fentanyl and other drugs to the US; revenue figures are not reliably known.",["DEA25"]]]},
 {"id":"cjng","name":"Jalisco New Generation Cartel","abbr":"CJNG = Cártel de Jalisco Nueva Generación","what":"Fast-expanding Mexican cartel, reported in most Mexican states.","what_c":["NARCODATA_CJNG"],
  "founded":"2010–11, Jalisco (Mexico), from the remnants of the Milenio Cartel and Nacho Coronel's network","founded_c":["JORNADA_CJNG","IC_CJNG"],"biz":["cjng"],
  "more":[["Began as an armed wing (\u2018Matazetas\u2019) after Ignacio Coronel's death in 2010; led for years by Nemesio Oseguera, \u2018El Mencho\u2019.",["JORNADA_CJNG"]],
          ["Mexico's financial intelligence unit reported operations in 27 states in 2020; its main rival is the Sinaloa Cartel.",["NARCODATA_CJNG","IC_CJNG"]],
          ["Leadership after El Mencho is contested in reporting.",["IC_CJNG_BOSS"]]],
  "series_note":"Published estimates (2022 model-based 28,764; 2026 NCTC 15,000–20,000) use different methods, so they are not plotted as a trend."},
 {"id":"gulf","name":"Gulf Cartel","abbr":"CDG = Cártel del Golfo","what":"Historic Tamaulipas border cartel, now split into rival factions.","what_c":["IC_GULF_ES"],
  "founded":"1980s (roots earlier), Tamaulipas (Mexico)","founded_c":["IC_GULF_ES"],"biz":["gulf"],
  "more":[["Juan García Ábrego built it in the 1980s by moving Cali Cartel cocaine across the border; Osiel Cárdenas later created the armed wing that became Los Zetas.",["IC_GULF_ES"]],
          ["Today it is fragmented into factions (Escorpiones, Ciclones, Metros and others) that fight over border crossings, drugs, arms and migrant smuggling.",["IC_GULF_ES"]]],
  "series_note":"No numeric membership estimate found (US NCTC says only \u2018thousands\u2019)."},
 {"id":"cdn","name":"Northeast Cartel","abbr":"CDN = Cártel del Noreste","what":"Zetas successor group based in Nuevo Laredo.","what_c":["IC_ZETAS"],
  "founded":"Mid-2010s, Tamaulipas (Mexico), splinter of Los Zetas","founded_c":["IC_ZETAS"],"biz":["cdn"],
  "more":[["Emerged as Los Zetas broke apart; controls key crossings around Nuevo Laredo.",["IC_ZETAS"]],["Detailed independent reporting on its structure is limited.",["IC_ZETAS"]]]},
 {"id":"lnfm","name":"La Nueva Familia Michoacana","abbr":"LNFM","what":"Michoacán-rooted group now strongest in Guerrero, Mexico State and Michoacán.","what_c":["IC_FAMILIA"],
  "founded":"2000s, Michoacán (Mexico); current form after La Familia's 2010–11 break-up","founded_c":["IC_FAMILIA"],"biz":["lnfm"],
  "more":[["Successor to La Familia Michoacana, whose split also produced the Knights Templar.",["IC_FAMILIA","IC_TEMPLARIOS"]],["Known for extortion of farmers and businesses alongside drug production; it fights CJNG in the region.",["IC_FAMILIA"]]]},
 {"id":"juarez","name":"Juárez Cartel / La Línea","abbr":None,"what":"Chihuahua border cartel whose armed wing La Línea now carries the name.","what_c":["IC_JUAREZ"],
  "founded":"1980s–90s, Ciudad Juárez (Mexico)","founded_c":["IC_JUAREZ"],"biz":[],"lines":["cocaine","marijuana","extortion"],"lines_c":["IC_JUAREZ"],
  "more":[["Rose under Amado Carrillo Fuentes in the 1990s; weakened by its 2008–12 war with Sinaloa in Ciudad Juárez.",["IC_JUAREZ"]],["Membership and revenue are not reliably estimated.",["IC_JUAREZ"]]]},
 {"id":"clan","name":"Clan del Golfo","abbr":"also EGC = Ejército Gaitanista de Colombia (self-name)","what":"Colombia's largest armed criminal group, a successor to right-wing paramilitaries.","what_c":["IC_URABENOS","FIP_GAO25"],
  "founded":"2006, Urabá region (Colombia), after paramilitary demobilisation","founded_c":["IC_URABENOS"],"biz":["clan"],
  "more":[["Formed from demobilised AUC paramilitaries; also known as the Urabeños or AGC.",["IC_URABENOS"]],
          ["Run as a franchise-like network that subcontracts local gangs; Colombian forces count it in more than 200 municipalities.",["ELTIEMPO_CLAN","SILLA_GAO23"]],
          ["It controls major Caribbean cocaine departure points and is in on-off talks with the government.",["IC_URABENOS"]]],
  "series":[S(2018,3632,3632,"ELTIEMPO_CLAN"),S(2023,5000,None,"SILLA_GAO23","at least, first half"),S(2024,7551,7551,"INFOBAE_GAO25","December"),S(2025,9840,9840,"INFOBAE_GAO25","December"),S(2026,9915,9915,"CARACOL_GAO26")],
  "series_note":"Colombian security-force counts (armed members plus support networks). Other claims (e.g. 13,500\u201314,000) are not plotted."},
 {"id":"eln","name":"National Liberation Army","abbr":"ELN = Ejército de Liberación Nacional","what":"Colombia's last major leftist guerrilla, heavily involved in illicit economies.","what_c":["IC_ELN"],
  "founded":"1964, Santander (Colombia)","founded_c":["IC_ELN"],"biz":["eln"],
  "more":[["Founded by students and priests inspired by the Cuban revolution.",["IC_ELN"]],["Operates on both sides of the Colombia–Venezuela border, taxing cocaine, mining and contraband; it has fought FARC dissidents in Catatumbo.",["IC_ELN","IC_SOLES"]]],
  "series":[S(2022,5851,5851,"SILLA_GAO23"),S(2023,6158,6158,"SILLA_GAO23","first half"),S(2025,6810,6810,"INFOBAE_GAO25","December"),S(2026,6877,6877,"CARACOL_GAO26")],
  "series_note":"Colombian security-force counts (armed members plus support networks)."},
 {"id":"exfarc","name":"FARC dissidents","abbr":"EMC = Estado Mayor Central; Segunda Marquetalia and other splinters","what":"Factions of the former FARC guerrilla that rejected the 2016 peace deal.","what_c":["IC_EXFARC"],
  "founded":"2016–19, Colombia","founded_c":["IC_EXFARC","IC_SEGMAR"],"biz":[],"lines":["cocaine","illegal_mining","extortion"],"lines_c":["IC_EXFARC"],
  "more":[["Not one group: the EMC, its offshoots and the Segunda Marquetalia compete as well as cooperate.",["IC_EXFARC","IC_SEGMAR"]],["Security forces counted 3,919 in Iván Mordisco's EMC and 2,802 in Calarcá's EMBF as of July 2025.",["FIP_GAO25"]]],
  "series_note":"Faction counts change as groups split, so no consistent series."},
 {"id":"tda","name":"Tren de Aragua","abbr":None,"what":"Venezuelan prison-born gang that spread with the Venezuelan migration.","what_c":["ELPAIS_TOCORON"],
  "founded":"About 2013–14, Tocorón prison, Aragua (Venezuela)","founded_c":["ELPAIS_TOCORON","BBC_TDA"],"biz":["tda"],
  "more":[["The name comes from a construction union on an unfinished railway in Aragua; Héctor \u2018Niño Guerrero\u2019 Guerrero built the group from Tocorón prison.",["BBC_TDA"]],
          ["Venezuela retook Tocorón in September 2023; cells abroad act with much autonomy.",["ELPAIS_TOCORON","IC_TDA_EMPIRE"]],["Its size and US reach are disputed.",["IC_TDA"]]],
  "series_note":"Only one numeric range (NCTC 2,500\u20135,000, 2026)."},
 {"id":"choneros","name":"Los Choneros","abbr":None,"what":"Ecuador's oldest major gang, long dominant in prisons and coastal routes.","what_c":["IC_CHONEROS"],
  "founded":"1998, Manta, Manabí (Ecuador)","founded_c":["EXPRESO_EC"],"biz":["choneros"],
  "more":[["Named after founder Jorge Véliz, \u2018El Chonero\u2019; grew under \u2018Rasquiña\u2019, killed in 2020, then \u2018Fito\u2019, who escaped prison in January 2024.",["EXPRESO_EC","PRIMICIAS_BANDAS"]],
          ["Ecuadorian police link its alliance to the Sinaloa Cartel.",["PRIMICIAS_BANDAS"]]],
  "series_note":"US (12,000) and Ecuadorian government (30,000) figures conflict and count different things."},
 {"id":"lobos","name":"Los Lobos","abbr":None,"what":"Ecuador's largest gang by most estimates, a Choneros splinter.","what_c":["IC_LOBOS"],
  "founded":"About 2019, Cuenca (Ecuador), from a Choneros cell","founded_c":["EXPRESO_EC","ELUNIVERSO_LOBOS"],"biz":["lobos"],
  "more":[["Led a breakaway coalition (\u2018Nueva Generación\u2019) against the Choneros after Rasquiña's 2020 killing.",["ELUNIVERSO_LOBOS"]],
          ["Ecuadorian police tie it to CJNG; it is also linked to illegal gold mining.",["PRIMICIAS_BANDAS","IC_LOBOS"]]],
  "series_note":"US (8,000) and Ecuadorian government (50,000) figures conflict."},
 {"id":"pcc","name":"First Capital Command","abbr":"PCC = Primeiro Comando da Capital","what":"Brazil's largest criminal faction, a prison gang turned transnational cocaine network.","what_c":["IC_PCC"],
  "founded":"31 Aug 1993, Taubaté prison, São Paulo (Brazil)","founded_c":["ELPAIS_PCC"],"biz":["pcc"],
  "more":[["Founded by eight inmates after the 1992 Carandiru massacre, presented as a prisoners' \u2018union\u2019; led for decades by Marcos Camacho, \u2018Marcola\u2019.",["ELPAIS_PCC"]],
          ["Controls cocaine routes through Paraguay and Brazilian ports to Europe and Africa; rival of Comando Vermelho.",["IC_PCC","IC_PARAGUAY"]],
          ["São Paulo operations have targeted PCC money-laundering schemes and fuel adulteration.",["G1_PCC40K"]]],
  "series":[S(2005,5000,5000,"G1_PCC40K","approx."),S(2025,40000,40000,"G1_PCC40K")],
  "series_note":"São Paulo prosecutors' figures as reported by G1; only two points."},
 {"id":"cv","name":"Red Command","abbr":"CV = Comando Vermelho","what":"Rio de Janeiro faction, Brazil's oldest, expanding into the Amazon.","what_c":["IC_CV"],
  "founded":"Late 1970s, Ilha Grande prison, Rio de Janeiro (Brazil)","founded_c":["IC_CV"],"biz":[],"lines":["cocaine","marijuana","arms","extortion"],"lines_c":["IC_CV"],
  "more":[["Formed in a prison where common prisoners mixed with political prisoners.",["IC_CV"]],["Main PCC rival; controls favelas in Rio and Amazon river routes.",["IC_CV"]],["No reliable membership figure found.",["IC_CV"]]]},
 {"id":"ms13","name":"Mara Salvatrucha","abbr":"MS-13","what":"Street gang born in Los Angeles, rooted in El Salvador, Honduras and Guatemala.","what_c":["IC_MS13"],
  "founded":"1980s, Los Angeles (US), by Salvadoran migrants","founded_c":["IC_MS13"],"biz":["ms13"],
  "more":[["In 2022 El Salvador's government cited about 70,000 gang members on the streets (all gangs); UK officials summarise MS-13 at about 78,000 members before the crackdown.",["ELMUNDO_SV_70K","UK_CPIN_SV"]],
          ["Since the March 2022 state of exception more than 84,000 people have been detained; by late 2023 over 52,000 alleged MS-13 members were in custody.",["CRS_SV_EXC","UK_CPIN_SV"]],
          ["It remains active in Honduras, Guatemala and US cities; main rival is Barrio 18.",["IC_MS13","DOJ_MS13_HOU","IC_HONDURAS"]]],
  "series_note":"Pre-2022 estimates count members; post-2022 figures count detentions, so they are not plotted together."},
 {"id":"b18","name":"Barrio 18","abbr":"also 18th Street gang; Sureños and Revolucionarios factions","what":"Los Angeles–born street gang, MS-13's main rival in Central America.","what_c":["IC_B18"],
  "founded":"1960s–70s, Los Angeles (US)","founded_c":["IC_B18"],"biz":[],"lines":["extortion","drugs_unspecified"],"lines_c":["IC_B18"],
  "more":[["Split in El Salvador in 2005 into Sureños and Revolucionarios.",["UK_CPIN_SV"]],["Strong in Guatemala and Honduras; heavily hit by El Salvador's state of exception.",["IC_B18","UK_CPIN_SV"]]]},
 {"id":"haiti","name":"Viv Ansanm / Gran Grif","abbr":"Viv Ansanm = \u2018Living Together\u2019 gang coalition","what":"Coalitions of armed gangs controlling most of Port-au-Prince and parts of Artibonite.","what_c":["IC_HAITI"],
  "founded":"2023–24, Haiti","founded_c":["IC_HAITI"],"biz":[],"lines":["kidnapping","extortion","arms"],"lines_c":["IC_HAITI"],
  "more":[["Viv Ansanm joined the previously rival G9 and G-Pèp alliances in 2024; Gran Grif operates in Artibonite.",["IC_HAITI"]],["Membership estimates are not reliable.",["IC_HAITI"]]]},
]
src = json.load(open(os.path.join(D,"sources.json")))
have = {s["id"] for s in src["sources"]}
for i,t,p,u,d in NEW:
    if i not in have: src["sources"].append({"id":i,"title":t,"publisher":p,"url":u,"date":d,"type":"media" if "gov" not in u and "congress" not in u and "dni" not in u else "official"})
json.dump(src, open(os.path.join(D,"sources.json"),"w"), ensure_ascii=False, indent=1)
imgs = json.load(open(os.path.join(ROOT,"pipeline","profile_images.json")))
out = []
for p in P:
    q = {k:v for k,v in p.items() if k not in ("series",)}
    q["membership_series"] = p.get("series", [])
    if p["id"] in imgs: q["image"] = imgs[p["id"]]
    out.append(q)
json.dump({"as_of":"2026-10-25","note":"Descriptive profiles; each claim cites data/sources.json ids. membership_series: published figures only, nothing interpolated; high=null means 'at least'. Countries come from group_countries.json, crime lines from groups_business.json (or 'lines' where that file has no entry).","profiles":out}, open(os.path.join(D,"profiles.json"),"w"), ensure_ascii=False, indent=1)
print("profiles:", len(out))
