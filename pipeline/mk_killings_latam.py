"""Merge sourced killings of sitting mayors and journalists outside Mexico into data/political_violence.json.
Idempotent: re-running replaces all non-Mexico events and LatAm source entries. Window: 2024-10-06 onward (same as the Mexico lists)."""
import json, os
D = os.path.join(os.path.dirname(__file__), "..", "data")
CPJ = "https://cpj.org/data/people/"
UN = "https://www.unesco.org/en/safety-journalists/observatory/"
S = [  # id, title, publisher, url, date
 ("CPJ_KILLED_DB", "Killed journalists database (Americas, 2024-2026)", "Committee to Protect Journalists", "https://cpj.org/data/killed/americas/?status=Killed&start_year=2024&end_year=2026", "2026-10-25"),
 ("UNESCO_OBS", "Observatory of Killed Journalists", "UNESCO", "https://www.unesco.org/en/safety-journalists/observatory/table", "2026-10-25"),
 ("IFJ_KILLED_2025", "Killed List 2025", "International Federation of Journalists", "https://www.ifj.org/fileadmin/user_upload/Killed_List_2025_28_December_final.xlsx.pdf", "2025-12-28"),
 ("G1_ABAETETUBA", "Quem era o radialista morto a tiros durante programa ao vivo no Pará", "g1", "https://g1.globo.com/pa/para/noticia/2025/05/28/quem-era-o-radialista-morto-a-tiros-durante-programa-ao-vivo-no-para.ghtml", "2025-05-28"),
 ("EU_RAMOS", "Prisión preventiva para sospechoso implicado en el asesinato del periodista Xavier Ramos", "El Universo", "https://www.eluniverso.com/noticias/prision-preventiva-para-sospechoso-implicado-en-el-asesinato-del-periodista-xavier-ramos-nota/", "2026-01-05"),
 ("RSF_ALVAREZ", "Ecuador: RSF condemns murder of journalist Álex Fernando Álvarez Vera", "RSF", "https://rsf.org/en/ecuador-rsf-condemns-murder-journalist-%C3%A1lex-fernando-%C3%A1lvarez-vera-calls-rigorous-independent", "2025-10-30"),
 ("FUNDAMEDIOS_COBOS", "Asesinan a René Cobos, fixer de medios internacionales, en Yaguachi", "Fundamedios", "https://fundamedios.org.ec/alertas/asesinan-a-rene-cobos-fixer-de-medios-internacionales-en-yaguachi/", "2026-08-24"),
 ("TELEAMAZONAS_ALCALDES", "Cinco alcaldes asesinados desde las elecciones seccionales 2023", "Teleamazonas", "https://www.teleamazonas.com/actualidad/noticias/politica/alcaldes-asesinados-detenidos-ecuador-radiografia-122562/", "2026-10-01"),
 ("EXPRESO_ARENILLAS", "Asesinato del alcalde de Arenillas", "Expreso", "https://www.expreso.ec/actualidad/asesinato-alcalde-arenilla-reacciones-e-investigaciones-227698.html", "2025-01-12"),
 ("LAHORA_CHUARRANCHO", "Alcalde de Chuarrancho fallece en ataque armado en ruta al Atlántico", "La Hora (Guatemala)", "https://lahora.gt/nacionales/ypena/2025/02/26/alcalde-de-chuarrancho-fallece-en-ataque-armado-en-ruta-al-atlantico/", "2025-02-26"),
 ("PC_CHUARRANCHO", "Concejal I asumirá como alcalde de Chuarrancho", "Prensa Comunitaria", "https://prensacomunitaria.org/2025/02/concejal-i-asumira-como-alcalde-de-chuarrancho/", "2025-02-28"),
 ("DW_SANISIDRO", "Descartan móvil político en asesinato de alcalde en Honduras", "DW", "https://www.dw.com/es/descartan-m%C3%B3vil-pol%C3%ADtico-en-asesinato-de-alcalde-en-honduras/a-73235261", "2025-07-11"),
 ("DW_MASAGUA", "Asesinan a tiros a alcalde en el sur de Guatemala", "DW", "https://www.dw.com/es/asesinan-a-tiros-a-alcalde-en-el-sur-de-guatemala/a-75052356", "2025-12-07"),
 ("AP_COVIRIALI", "Fallece alcalde peruano tras ataque armado, el 2do en morir en una semana", "AP", "https://apnews.com/article/peru-ataque-alcalde-motocicleta-amazonia-homicidio-495c63ae19ed7a7e2abe5b39ed16bf7e", "2026-02-26"),
 ("RPP_COVIRIALI", "Falleció alcalde de Coviriali tras ser trasladado de emergencia a Lima", "RPP", "https://rpp.pe/peru/actualidad/fallecio-alcalde-de-coviriali-tras-ser-trasladado-de-emergencia-a-lima-por-heridas-de-bala-noticia-1677685", "2026-02-26"),
 ("AP_PIURA", "Asesinan a alcalde de municipio en región azotada por la delincuencia en Perú", "AP", "https://apnews.com/article/peru-asesinato-alcalde-piura-costa-sicarios-motocicletas-delincuencia-7ce74b9da9803b8854acf8c5346e5755", "2026-05-21"),
 ("ANDINA_PIURA", "Piura: asesinan al alcalde de Veintiséis de Octubre en ataque armado atribuido a sicarios", "Andina", "https://andina.pe/agencia/noticia-piura-asesinan-al-alcalde-veintiseis-octubre-ataque-armado-atribuido-a-sicarios-1076124.aspx", "2026-05-21"),
]
UIU = "motive under investigation"
J = lambda date, name, outlet, place, country, ll, url, cites, motive, perp=None, prec="municipality (approximate)": dict(
    date=date, name=name, role="Journalist or media worker", kind="journalist", outlet=outlet, place=place, country=country,
    lonlat=ll, precision=prec, url=url, cites=cites, motive=motive, **({"perpetrator": perp} if perp else {}))
M = lambda date, name, place, country, ll, url, cites, motive=UIU, perp=None, prec="municipality (approximate seat)": dict(
    date=date, name=name, role="Sitting mayor", kind="official", place=place, country=country, lonlat=ll, precision=prec,
    url=url, cites=cites, motive=motive, **({"perpetrator": perp} if perp else {}))
C, U = "CPJ: work-related motive confirmed", "CPJ: motive unconfirmed (" + UIU + ")"
EV = [
 J("2024-12-24", "Jimmy Jean", "Moun Afe Bon", "Port-au-Prince", "Haiti", [-72.34, 18.54], CPJ+"jimmy-jean/", ["CPJ_KILLED_DB"], C, "Criminal group (CPJ); gang gunfire on a press conference at a hospital reopening (IFJ)"),
 J("2024-12-24", "Marckendy Natoux", "Freelance", "Port-au-Prince", "Haiti", [-72.33, 18.55], CPJ+"marckendy-natoux/", ["CPJ_KILLED_DB"], C, "Criminal group (CPJ)"),
 J("2025-01-20", "Gastón Medina", "Cadena Sur", "Ica", "Peru", [-75.73, -14.07], CPJ+"gaston-medina/", ["CPJ_KILLED_DB", "IFJ_KILLED_2025"], C),
 J("2025-01-24", "Óscar Gómez Agudelo", "Rumba del Café", "Armenia, Quindío", "Colombia", [-75.68, 4.53], CPJ+"oscar-gomez-agudelo/", ["CPJ_KILLED_DB", "IFJ_KILLED_2025"], U),
 J("2025-03-04", "Patricio Aguilar", "El Libertador", "Quinindé, Esmeraldas", "Ecuador", [-79.47, 0.33], CPJ+"patricio-aguilar/", ["CPJ_KILLED_DB", "UNESCO_OBS"], U),
 J("2025-03-21", "Ismael Alonzo González", "Freelance", "Quetzaltenango", "Guatemala", [-91.52, 14.83], CPJ+"ismael-alonzo-gonzalez/", ["CPJ_KILLED_DB", "UNESCO_OBS"], U),
 J("2025-05-07", "Raúl Celis López", "Hora Cero", "Iquitos, Loreto", "Peru", [-73.25, -3.75], CPJ+"raul-celis-lopez/", ["CPJ_KILLED_DB", "IFJ_KILLED_2025"], U),
 J("2025-05-27", "Luís Augusto Carneiro da Costa", "Rádio Guarany FM", "Abaetetuba, Pará", "Brazil", [-48.88, -1.72], UN+"e3589c40-ae73-4bbc-b682-967ef82aa662", ["UNESCO_OBS", "G1_ABAETETUBA"], "Not in CPJ database; " + UIU),
 J("2025-05-31", "Javier Hércules (Javier Antonio Salinas)", "ATN Noticias (A Todo Noticias, Canal 32)", "Copán department", "Honduras", [-88.78, 14.77], CPJ+"javier-hercules/", ["CPJ_KILLED_DB", "UNESCO_OBS"], C, "Criminal group (CPJ)", "department (approximate)"),
 J("2025-08-21", "Xavier Ramos", "El Universo", "Guayaquil", "Ecuador", [-79.92, -2.17], UN+"0215b1f4-bfcb-4918-9d94-3086c0965ee4", ["UNESCO_OBS", "EU_RAMOS"], "Not in CPJ database; suspect charged with robbery resulting in death"),
 J("2025-10-28", "Fernando Álvarez Vera", "Fernando TV (digital)", "Salitre, Guayas", "Ecuador", [-79.82, -1.83], UN+"b8180dae-22eb-461b-ba94-9c2c60dc272e", ["UNESCO_OBS", "RSF_ALVAREZ"], "Not in CPJ database; " + UIU),
 J("2025-12-06", "Juan Fernando Núñez Guevara", "Kamila TV", "Chepén, La Libertad", "Peru", [-79.43, -7.22], CPJ+"juan-fernando-nunez-guevara/", ["CPJ_KILLED_DB", "IFJ_KILLED_2025"], U),
 J("2025-12-16", "Jorge Zapeta Aguilar", "Libertad de Expresión", "San Pablo Jocopilas, Suchitepéquez", "Guatemala", [-91.45, 14.58], CPJ+"jorge-zapeta-aguilar/", ["CPJ_KILLED_DB", "IFJ_KILLED_2025"], U),
 J("2025-12-26", "Mitzar Bato Castillejos Tenazoa", "Radio Latin Plus", "Aguaytía, Ucayali", "Peru", [-75.51, -9.04], CPJ+"mitzar-bato-castillejos-tenazoa/", ["CPJ_KILLED_DB", "UNESCO_OBS"], U),
 J("2026-04-26", "Carlos Humberto Cal Ical", "Freelance", "San Cristóbal Verapaz, Alta Verapaz", "Guatemala", [-90.48, 15.37], CPJ+"carlos-humberto-cal-ical/", ["CPJ_KILLED_DB", "UNESCO_OBS"], U),
 J("2026-05-05", "Mateo Pérez Rueda", "El Confidente", "Briceño, Antioquia", "Colombia", [-75.55, 7.11], CPJ+"mateo-perez-rueda/", ["CPJ_KILLED_DB", "UNESCO_OBS"], C, "Criminal group (CPJ)"),
 J("2026-06-06", "Cristian Herrera Niño", "Cúcuta al Rojo Vivo", "Cúcuta, Norte de Santander", "Colombia", [-72.50, 7.89], CPJ+"cristian-herrera-nino/", ["CPJ_KILLED_DB", "UNESCO_OBS"], U),
 J("2026-08-23", "René Manuel Cobos Merchán", "Fixer for national and foreign media", "Yaguachi, Guayas", "Ecuador", [-79.69, -2.12], UN+"fd919364-70e5-4e8c-8e49-569cc5fd26f3", ["UNESCO_OBS", "FUNDAMEDIOS_COBOS"], "Not in CPJ database; " + UIU),
 J("2026-09-10", "Joseph Willard Vancol", "Ti-Boukan FM", "Petit-Boucan (Grand-Goâve area)", "Haiti", [-72.77, 18.43], CPJ+"joseph-willard-vancol/", ["CPJ_KILLED_DB", "UNESCO_OBS"], C, "Criminal group (CPJ)", "locality (approximate)"),
 J("2026-10-02", "Evelio Lisandro López Sánchez", "Huehue es Noticias", "San Pedro Necta, Huehuetenango", "Guatemala", [-91.77, 15.49], CPJ+"evelio-lisandro-lopez-sanchez/", ["CPJ_KILLED_DB", "UNESCO_OBS"], U),
 M("2025-01-11", "Eber Rigoberto Ponce Rosero", "Arenillas, El Oro", "Ecuador", [-80.06, -3.55], "https://www.teleamazonas.com/actualidad/noticias/politica/alcaldes-asesinados-detenidos-ecuador-radiografia-122562/", ["TELEAMAZONAS_ALCALDES", "EXPRESO_ARENILLAS"]),
 M("2025-02-26", "Gerson Saúl Ajcúc Xot", "Chuarrancho (killed on the Ruta al Atlántico, Guatemala City)", "Guatemala", [-90.47, 14.65], "https://lahora.gt/nacionales/ypena/2025/02/26/alcalde-de-chuarrancho-fallece-en-ataque-armado-en-ruta-al-atlantico/", ["LAHORA_CHUARRANCHO", "PC_CHUARRANCHO"], prec="attack site (approximate)"),
 M("2025-07-09", "Francisco Martínez", "San Isidro, Intibucá (killed in Siguatepeque)", "Honduras", [-87.83, 14.60], "https://www.dw.com/es/descartan-m%C3%B3vil-pol%C3%ADtico-en-asesinato-de-alcalde-en-honduras/a-73235261", ["DW_SANISIDRO"], "Police rule out political motive and cite possible personal revenge; " + UIU, prec="attack site (approximate)"),
 M("2025-12-06", "Nelson Luciano Marroquín", "Masagua, Escuintla", "Guatemala", [-90.86, 14.20], "https://www.dw.com/es/asesinan-a-tiros-a-alcalde-en-el-sur-de-guatemala/a-75052356", ["DW_MASAGUA"]),
 M("2026-02-22", "Edward Amoroto", "Los Aquijes, Ica (died in Lima hospital)", "Peru", [-75.69, -14.10], "https://apnews.com/article/peru-ataque-alcalde-motocicleta-amazonia-homicidio-495c63ae19ed7a7e2abe5b39ed16bf7e", ["AP_COVIRIALI"]),
 M("2026-02-26", "Iroshi Erik Ureta Campos", "Coviriali, Junín", "Peru", [-74.64, -11.29], "https://rpp.pe/peru/actualidad/fallecio-alcalde-de-coviriali-tras-ser-trasladado-de-emergencia-a-lima-por-heridas-de-bala-noticia-1677685", ["RPP_COVIRIALI", "AP_COVIRIALI"]),
 M("2026-05-21", "Víctor Hugo Febre Calle", "Veintiséis de Octubre, Piura", "Peru", [-80.67, -5.18], "https://apnews.com/article/peru-asesinato-alcalde-piura-costa-sicarios-motocicletas-delincuencia-7ce74b9da9803b8854acf8c5346e5755", ["AP_PIURA", "ANDINA_PIURA"]),
]
EV = [e for e in EV if e]
def main():
    p = os.path.join(D, "political_violence.json"); o = json.load(open(p))
    mx = [dict(e, country="Mexico") for e in o["events"] if e.get("country", "Mexico") == "Mexico"]
    o["events"] = sorted(mx + EV, key=lambda e: (e["date"], e["name"]))
    o["title"] = "Killings of sitting mayors and journalists in Latin America and the Caribbean since October 2024"
    o["last"] = max(e["date"] for e in o["events"])
    for c in ("CPJ_KILLED_DB", "UNESCO_OBS"):
        if c not in o["cites"]: o["cites"].append(c)
    o["note_latam"] = ("Outside Mexico: journalists from CPJ's killed database (confirmed and unconfirmed motive) cross-checked with UNESCO's "
        "observatory and IFJ, plus UNESCO cases CPJ does not list; sitting mayors (alcaldes, prefeitos) from national media. "
        "Ex-mayors and candidates are excluded. No sitting mayor or prefeito killing in Brazil or Colombia was found for the window.")
    json.dump(o, open(p, "w"), ensure_ascii=False, indent=1)
    sp = os.path.join(D, "sources.json"); s = json.load(open(sp)); have = {x["id"] for x in s["sources"]}
    for i, t, pub, u, d in S:
        if i not in have: s["sources"].append(dict(id=i, title=t, publisher=pub, url=u, date=d, type="media" if pub not in ("UNESCO",) else "official"))
    json.dump(s, open(sp, "w"), ensure_ascii=False, indent=1)
    print(len(mx), "Mexico +", len(EV), "elsewhere")
if __name__ == "__main__": main()
