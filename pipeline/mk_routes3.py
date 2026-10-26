"""Build the three physical-goods route layers: data/routes_drugs.geojson, routes_migrants.geojson, routes_firearms.geojson.
Each feature: channel, subtype, from, to, description (one sentence), sources[] (sources.json id or {url,name,title,date}), year.
Coordinates are schematic corridors between named places in the cited sources, not GPS tracks."""
import json, os
D = os.path.join(os.path.dirname(__file__), "..", "data")
P = {  # lon, lat
 "Tumaco": (-78.79, 1.80), "Buenaventura": (-77.07, 3.88), "Esmeraldas": (-79.65, 0.97), "Manta": (-80.72, -0.95), "Guayaquil": (-79.90, -2.19),
 "Callao": (-77.15, -12.05), "VRAEM": (-74.0, -12.5), "Chapare": (-65.5, -17.0), "Santa Cruz": (-63.18, -17.78), "Villeta": (-57.56, -25.50),
 "Santos": (-46.33, -23.96), "Paranaguá": (-48.51, -25.52), "Galápagos (offshore)": (-91.0, 0.5), "Central America Pacific (offshore)": (-90.0, 11.0),
 "Guatemala Pacific coast": (-91.9, 14.0), "Chiapas coast": (-93.2, 15.4), "Guerrero coast": (-99.9, 16.8), "Lázaro Cárdenas": (-102.2, 17.96),
 "Manzanillo": (-104.32, 19.05), "Culiacán": (-107.39, 24.80), "Guadalajara": (-103.35, 20.67), "Tierra Caliente (Michoacán)": (-101.6, 18.9),
 "Tijuana": (-117.03, 32.53), "Mexicali": (-115.45, 32.62), "Nogales": (-110.94, 31.33), "San Luis Río Colorado": (-114.77, 32.46),
 "Ciudad Juárez": (-106.45, 31.73), "Nuevo Laredo": (-99.51, 27.48), "Reynosa": (-98.28, 26.08), "Matamoros": (-97.50, 25.87),
 "Los Angeles": (-118.24, 34.05), "Phoenix": (-112.07, 33.45), "Houston": (-95.37, 29.76), "Dallas": (-96.80, 32.78), "Albuquerque": (-106.65, 35.08),
 "Miami": (-80.19, 25.76), "Fort Lauderdale": (-80.12, 26.09), "Guajira/Falcón coast": (-70.5, 11.9), "Venezuela east coast": (-63.0, 10.7),
 "Cartagena": (-75.51, 10.40), "Santo Domingo": (-69.90, 18.47), "San Juan": (-66.10, 18.47), "Haiti south coast": (-72.53, 18.23),
 "Port-au-Prince": (-72.34, 18.54), "Port-de-Paix": (-72.83, 19.94), "Cap-Haïtien": (-72.20, 19.76), "Gonaïves": (-72.69, 19.45),
 "Saint-Marc": (-72.69, 19.11), "Turks and Caicos": (-71.8, 21.8), "Bahamas": (-77.3, 25.0), "Dominican border (Dajabón)": (-71.71, 19.55),
 "Honduras Mosquitia": (-84.5, 15.3), "San Pedro Sula": (-88.03, 15.50), "Petén": (-90.0, 16.9), "Tecún Umán / Ciudad Hidalgo": (-92.15, 14.68),
 "Tapachula": (-92.26, 14.90), "Villahermosa": (-92.93, 17.99), "Veracruz": (-96.13, 19.17), "Monterrey": (-100.31, 25.67),
 "Panama Canal": (-79.9, 9.1), "Caribbean (east)": (-62.0, 17.5), "Atlantic, to Europe (map edge)": (-28.0, 28.0), "Atlantic, to Europe/W. Africa (map edge)": (-30.0, 5.0),
 "Asia (via Pacific, map edge)": (-128.0, 18.0), "Necoclí / Turbo": (-76.73, 8.40), "Darién Gap": (-77.6, 8.0), "Lajas Blancas (Panama)": (-77.9, 8.5),
 "Paso Canoas": (-82.84, 8.53), "Peñas Blancas": (-85.62, 11.21), "Trojes / Danlí (Honduras)": (-86.6, 14.0), "Guatemala City": (-90.51, 14.63),
 "Arriaga / Tonalá": (-93.8, 16.1), "Mexico City": (-99.13, 19.43), "Ocós (Guatemala)": (-92.19, 14.51), "Salina Cruz / Huatulco": (-95.6, 15.9),
 "Hermosillo": (-110.96, 29.07), "Colón (Miramar/Palenque)": (-79.3, 9.55), "Capurganá": (-77.35, 8.63), "Panama City": (-79.52, 8.98), "Jaque (Darién)": (-78.17, 7.52),
 "Lima": (-77.04, -12.05), "Tumbes (Peru-Ecuador border)": (-80.45, -3.57), "Colombia–Ecuador border": (-77.7, 0.85),
}
S = lambda url, name, title, date="": {"url": url, "name": name, "title": title, "date": date}
EUDA_C = S("https://www.euda.europa.eu/publications/eu-drug-markets/cocaine/europe-and-global-cocaine-trade_en", "EUDA", "Europe and the global cocaine trade (EU Drug Markets)")
EUDA_N = S("https://www.euda.europa.eu/publications/eu-drug-markets/cocaine/criminal-networks_en", "EUDA", "Cocaine: criminal networks (EU Drug Markets)")
MPI = S("https://www.migrationpolicy.org/journal/feature/how-immigration-crackdowns-and-aid-cuts-are-reshaping-migration-across-central", "Migration Policy Institute", "How immigration crackdowns and aid cuts are reshaping migration across Central America", "2025")
IC_TAP = S("https://insightcrime.org/news/vortex-evil-gangs-narcos-tapachula-mexico/", "InSight Crime", "Vortex of Evil: Gangs and Narcos in Tapachula, Mexico")
IC_SEA = S("https://insightcrime.org/news/human-smugglers-take-to-the-waves-along-mexicos-pacific-coast/", "InSight Crime", "Human smugglers take to the waves along Mexico's Pacific coast")
GI_MX = S("https://globalinitiative.net/wp-content/uploads/2018/07/Organized-Crime-and-Central-American-Migration-in-Mexico-The-University-of-Texas-at-Austin-2018.pdf", "UT Austin / Global Initiative", "Organized crime and Central American migration in Mexico", "2018")
HIAS = S("https://hias.org/wp-content/uploads/Panama-Reverse-Flow-Monitoring-Factsheet_2025.pdf", "UNHCR / HIAS", "Panama reverse flow monitoring factsheet", "2025")
TNH = S("https://www.thenewhumanitarian.org/news-feature/2025/06/19/challenges-invisible-reverse-flow-migrantion-panama-americas", "The New Humanitarian", "The challenges facing 'invisible' reverse flow migrants in Panama", "2025-06-19")
AP_REV = S("https://apnews.com/article/costa-rica-panama-immigration-darien-27c86f83c2288b9519ddf71fc23726c0", "AP", "Costa Rica and Panama coordinate to move southbound migrants", "2025-03-03")
ATF = S("https://www.atf.gov/media/18621/download", "ATF", "NFCTA Vol. IV Part VII: Firearm commerce, crime guns and the Southwest border", "2025")
ATF_MX = S("https://www.atf.gov/firearms/report/firearms-trace-data/firearms-trace-data-mexico-2018-2023", "ATF", "Firearms trace data: Mexico 2018-2023", "2024")
UNODC_H1 = S("https://documents.un.org/doc/undoc/gen/n23/414/49/pdf/n2341449.pdf", "UNODC (S/2023/780)", "Report to the Security Council on illicit arms flows into Haiti", "2023")
UNODC_H3 = S("https://docs.haitidocs.org/unodc-reports-to-sc-2024-07.pdf", "UNODC", "Report to the Security Council on illicit arms flows into Haiti, July 2024", "2024-07")
REU_EC = S("https://www.reuters.com/world/americas/one-gun-34-dead-inside-ecuadors-war-black-market-weapons-2024-06-29/", "Reuters", "One gun, 34 dead: Inside Ecuador's war on black-market weapons", "2024-06-29")
IC_ECG = S("https://insightcrime.org/news/indictment-ecuador-most-wanted-criminal-is-shift-security-policy/", "InSight Crime", "The US just indicted Ecuadorian gang boss 'Fito'")
IC_ECA = S("https://insightcrime.org/news/illegal-arms-trafficking-is-ecuador-security-blind-spot/", "InSight Crime", "Illegal arms trafficking is Ecuador's security blind spot")

def F(channel, subtype, pts, desc, src, year, width=None):
    p = {"channel": channel, "subtype": subtype, "from": pts[0], "to": pts[-1], "description": desc, "sources": src, "year": year}
    if width: p["volume"] = width
    return {"type": "Feature", "properties": p, "geometry": {"type": "LineString", "coordinates": [list(P[x]) for x in pts]}}

drugs = [
 F("drugs", "cocaine", ["Tumaco", "Central America Pacific (offshore)", "Guatemala Pacific coast"], "Cocaine leaves Colombia's southern Pacific coast by go-fast boat and semi-submersible for Central America's Pacific coast.", ["UNODC_WDR25", "IC_URABENOS", "JS_STRIKES"], "2025"),
 F("drugs", "cocaine", ["Buenaventura", "Central America Pacific (offshore)", "Chiapas coast"], "Shipments from Buenaventura run north along the Pacific to southern Mexico.", ["UNODC_WDR25", "IC_URABENOS"], "2025"),
 F("drugs", "cocaine", ["Guayaquil", "Galápagos (offshore)", "Central America Pacific (offshore)", "Guerrero coast"], "Ecuadorian ports feed a long Pacific route, sometimes skirting the Galápagos, to Mexico's Pacific coast.", ["IC_ECUADOR", "IC_CHONEROS", "UNODC_WDR25"], "2025"),
 F("drugs", "cocaine", ["Manta", "Galápagos (offshore)", "Central America Pacific (offshore)"], "Manta and Esmeraldas launch boats that hand loads to Mexican buyers offshore.", ["IC_LOBOS", "IC_ECUADOR"], "2025"),
 F("drugs", "cocaine", ["Guerrero coast", "Tierra Caliente (Michoacán)", "Guadalajara", "Culiacán", "Nogales"], "Cocaine landed on Mexico's Pacific coast moves overland under Sinaloa and CJNG control to the Arizona and California crossings.", ["DEA25", "IC_SINALOA", "IC_CJNG"], "2025"),
 F("drugs", "cocaine", ["Guajira/Falcón coast", "Santo Domingo"], "Cocaine moves by boat and light aircraft from Venezuela's and Colombia's Caribbean coast to the Dominican Republic.", ["IC_SOLES", "UNODC_WDR25", "JS_STRIKES"], "2025"),
 F("drugs", "cocaine", ["Venezuela east coast", "San Juan", "Miami"], "Puerto Rico is a Caribbean entry point for US-bound cocaine.", ["DEA25", "UNODC_WDR25"], "2025"),
 F("drugs", "cocaine", ["Cartagena", "Haiti south coast"], "Haiti's south coast is a transshipment point on the Caribbean route.", ["IC_HAITI", "UNODC_WDR25"], "2025"),
 F("drugs", "cocaine", ["Cartagena", "Honduras Mosquitia"], "Air and sea loads land in Honduras' Mosquitia and start the Central American land bridge.", ["UNODC_WDR25", "IC_HONDURAS"], "2025"),
 F("drugs", "cocaine", ["Honduras Mosquitia", "San Pedro Sula", "Petén", "Villahermosa", "Veracruz", "Reynosa"], "The land corridor runs through Honduras and Guatemala's Petén into Tabasco, then up the Gulf side to the Tamaulipas border.", ["UNODC_WDR25", "IC_GUATEMALA", "IC_GULF"], "2025"),
 F("drugs", "cocaine", ["Petén", "Tapachula"], "A western branch enters Mexico through Chiapas.", ["UNODC_WDR25", "IC_GUATEMALA", IC_TAP], "2025"),
 F("drugs", "cocaine", ["Guayaquil", "Panama Canal", "Caribbean (east)", "Atlantic, to Europe (map edge)"], "Containers from Guayaquil carry cocaine to Antwerp and Rotterdam; EUDA counts Antwerp seizures from Guayaquil rising from 6 t (2018) to 55.6 t (2021).", [EUDA_C, "IC_ECUADOR"], "2021"),
 F("drugs", "cocaine", ["VRAEM", "Chapare", "Santa Cruz", "Santos", "Atlantic, to Europe/W. Africa (map edge)"], "Peruvian and Bolivian cocaine crosses Bolivia to Brazil's Santos port, where the PCC organises container exports to Europe and West Africa.", [EUDA_N, "IC_PCC", "UNODC_WDR25"], "2025"),
 F("drugs", "cocaine", ["Santa Cruz", "Paranaguá", "Atlantic, to Europe/W. Africa (map edge)"], "Paranaguá is the second major Brazilian export port that EUDA names.", [EUDA_N, EUDA_C], "2025"),
 F("drugs", "cocaine", ["Santa Cruz", "Villeta", "Atlantic, to Europe (map edge)"], "Paraguay's river port of Villeta ships Bolivian cocaine downriver toward the Atlantic and Europe.", [EUDA_C, "IC_PARAGUAY"], "2025"),
 F("drugs", "cocaine", ["Callao", "Panama Canal", "Atlantic, to Europe (map edge)"], "Peru's Callao container port is an export point to Europe.", ["UNODC_WDR25"], "2025"),
 F("drugs", "precursor", ["Asia (via Pacific, map edge)", "Manzanillo"], "Precursor chemicals from China and India arrive by ship at Manzanillo; the Asia leg runs off the map.", ["DEA25", "OFAC_JY1413", "OFAC_SB0468"], "2025"),
 F("drugs", "precursor", ["Asia (via Pacific, map edge)", "Lázaro Cárdenas"], "Lázaro Cárdenas is the second main Pacific entry port for Asian precursors.", ["DEA25", "OFAC_JY1413"], "2025"),
 F("drugs", "precursor", ["Manzanillo", "Guadalajara"], "Chemicals move inland from Manzanillo to CJNG labs in Jalisco.", ["DEA25", "IC_CJNG"], "2025"),
 F("drugs", "precursor", ["Manzanillo", "Culiacán"], "Chemicals also go north to Sinaloa Cartel fentanyl and meth labs in Sinaloa.", ["DEA25", "IC_SINALOA"], "2025"),
 F("drugs", "precursor", ["Lázaro Cárdenas", "Tierra Caliente (Michoacán)"], "Michoacán's Tierra Caliente labs draw chemicals from Lázaro Cárdenas.", ["DEA25", "IC_FAMILIA"], "2025"),
 F("drugs", "synthetic", ["Culiacán", "Hermosillo", "Nogales", "Phoenix"], "Fentanyl and meth from Sinaloa labs go north through Sonora to the Nogales crossing and Phoenix.", ["DEA25", "WOLA_FENT", "IC_SINALOA"], "2025"),
 F("drugs", "synthetic", ["Culiacán", "San Luis Río Colorado", "Mexicali"], "A Sonora–Baja branch reaches the San Luis and Calexico crossings.", ["DEA25", "WOLA_FENT"], "2025"),
 F("drugs", "synthetic", ["Guadalajara", "Culiacán", "Tijuana", "Los Angeles"], "CJNG and Sinaloa product goes to Tijuana and San Diego; most US fentanyl seizures are made at California and Arizona ports of entry.", ["DEA25", "IC_CJNG", "WOLA_FENT"], "2025"),
 F("drugs", "synthetic", ["Culiacán", "Ciudad Juárez", "Albuquerque"], "A Chihuahua corridor crosses at Ciudad Juárez–El Paso.", ["DEA25", "IC_JUAREZ"], "2025"),
 F("drugs", "synthetic", ["Tierra Caliente (Michoacán)", "Monterrey", "Nuevo Laredo", "Dallas"], "Meth from Michoacán and Jalisco also moves to the Texas crossings.", ["DEA25", "IC_CJNG"], "2025"),
]
migr = [
 F("migrants", "northbound land", ["Necoclí / Turbo", "Darién Gap", "Lajas Blancas (Panama)"], "The Darién crossing from Colombia to Panama carried a record 520,000+ people north in 2023, then collapsed to a trickle by 2025.", [MPI, TNH], "2023", 520000),
 F("migrants", "northbound land", ["Lajas Blancas (Panama)", "Panama City", "Paso Canoas", "Peñas Blancas", "Trojes / Danlí (Honduras)", "Guatemala City", "Tecún Umán / Ciudad Hidalgo"], "From Panama the route crosses Costa Rica (Paso Canoas to Peñas Blancas), Nicaragua, Honduras and Guatemala to the Mexican border.", [MPI, AP_REV], "2024"),
 F("migrants", "northbound land", ["Tecún Umán / Ciudad Hidalgo", "Tapachula", "Arriaga / Tonalá"], "Tapachula is the bottleneck where about 60% of Mexico's 2021-23 asylum requests were filed; the coastal highway leads north.", [IC_TAP], "2023"),
 F("migrants", "rail (La Bestia)", ["Arriaga / Tonalá", "Veracruz", "Mexico City"], "The freight train known as La Bestia starts in Chiapas and runs to central Mexico.", [IC_TAP, GI_MX], "2023"),
 F("migrants", "northbound land", ["Villahermosa", "Veracruz", "Reynosa", "Matamoros"], "The Gulf route through Veracruz to Tamaulipas is the most used and most violent, taxed by Gulf Cartel and Zetas splinters.", [GI_MX], "2018"),
 F("migrants", "northbound land", ["Mexico City", "Guadalajara", "Hermosillo", "Nogales"], "The Pacific route runs through Sinaloa Cartel territory to the Sonora crossings.", [GI_MX], "2018"),
 F("migrants", "northbound land", ["Hermosillo", "Mexicali", "Tijuana"], "The Pacific route continues on to Baja California.", [GI_MX], "2018"),
 F("migrants", "sea", ["Ocós (Guatemala)", "Salina Cruz / Huatulco"], "Smugglers take people by fishing boat about 450 km along the Pacific coast, from Ocós to Oaxaca, to avoid checkpoints in Chiapas.", [IC_SEA], "2022"),
 F("migrants", "southbound (reverse) 2025", ["Peñas Blancas", "Paso Canoas", "Panama City"], "In 2025 Costa Rica and Panama bused southbound migrants along the old northbound route.", [AP_REV, MPI], "2025"),
 F("migrants", "southbound (reverse) 2025", ["Panama City", "Colón (Miramar/Palenque)", "Capurganá", "Necoclí / Turbo"], "Panama recorded 22,300+ people heading south to Colombia in 2025, mostly Venezuelans, many taking boats from Colón to Capurganá.", [HIAS, TNH], "2025", 22300),
 F("migrants", "southbound (reverse) 2025", ["Panama City", "Jaque (Darién)", "Buenaventura"], "A Pacific boat route from Panama City via Jaque also returns migrants to Colombia.", [HIAS], "2025"),
]
guns = [
 F("firearms", "land", ["Phoenix", "Nogales", "Hermosillo", "Culiacán"], "Arizona to Sonora is the single largest US–Mexico gun pipeline in ATF trace data; Arizona dealers sourced about 22% of traced Mexican crime guns in 2022-23.", [ATF], "2023", 3969),
 F("firearms", "land", ["Houston", "Matamoros"], "Texas to Tamaulipas is the second-largest pipeline; Texas dealers sourced 43% of traced Mexican crime guns (7,825 of 18,205).", [ATF], "2023", 7825),
 F("firearms", "land", ["Dallas", "Nuevo Laredo", "Monterrey"], "Texas to Nuevo León is the third of ATF's top five pipelines.", [ATF], "2023"),
 F("firearms", "land", ["Albuquerque", "Ciudad Juárez"], "Guns from Texas and New Mexico go south through Ciudad Juárez into Chihuahua (Texas–Chihuahua is a top-five pipeline).", [ATF], "2023"),
 F("firearms", "land", ["Houston", "Monterrey", "Guadalajara"], "Texas to Guanajuato completes ATF's top five pipelines, which carry 32% of traced guns.", [ATF], "2023"),
 F("firearms", "land", ["Los Angeles", "Tijuana"], "California dealers were the third US source (2,734 traced guns, 2022-23), mostly through Baja California.", [ATF, "GAO_FIREARMS"], "2023", 2734),
 F("firearms", "sea", ["Miami", "Port-au-Prince"], "UNODC's primary Haiti route: guns shipped from Florida in containers to public and private ports in Port-au-Prince.", [UNODC_H1, UNODC_H3], "2024"),
 F("firearms", "sea", ["Fort Lauderdale", "Bahamas", "Turks and Caicos", "Port-de-Paix"], "Indirect shipments from Florida, sometimes via the Bahamas and Turks and Caicos, land in Port-de-Paix, Saint-Marc and Gonaïves.", [UNODC_H1], "2023"),
 F("firearms", "sea", ["Fort Lauderdale", "Cap-Haïtien"], "In April 2024 Haitian police seized guns in a container shipped from Port Everglades to Cap-Haïtien for Artibonite gangs.", [UNODC_H3], "2024"),
 F("firearms", "land", ["Santo Domingo", "Dominican border (Dajabón)", "Gonaïves"], "Arms and ammunition also cross Haiti's land border from the Dominican Republic.", [UNODC_H1, UNODC_H3], "2024"),
 F("firearms", "air", ["Miami", "Manta"], "Ecuadorian police name a Miami–Manta air route among three US-origin gun routes into Ecuador.", [REU_EC, IC_ECG], "2024"),
 F("firearms", "land", ["Lima", "Tumbes (Peru-Ecuador border)", "Guayaquil"], "Three overland gun routes enter Ecuador from Peru, including US guns that arrive via Lima.", [REU_EC, IC_ECG], "2024"),
 F("firearms", "sea", ["Panama Canal", "Galápagos (offshore)", "Guayaquil"], "Police also describe a sea route via the Galápagos, and guns hidden in containers have been seized at Guayaquil.", [REU_EC, IC_ECA], "2024"),
 F("firearms", "land", ["Colombia–Ecuador border", "Esmeraldas"], "A further route enters northern Ecuador from the Colombian border.", [REU_EC], "2024"),
]
NOTES = {
 "drugs": {"note": "Cocaine (solid), precursors (dotted; Asia leg off-map), synthetics: fentanyl/meth (dashed). Lines are schematic corridors between places named in sources, not tracks. Atlantic legs end at the map edge.", "sources": ["DEA25", "UNODC_WDR25", EUDA_C]},
 "migrants": {"note": "Northbound land (solid), rail (long dash), sea (dotted), 2025 southbound reverse flow (dash-dot). Line width only where a sourced count exists.", "sources": [MPI, HIAS]},
 "firearms": {"note": "ATF: 74% of international crime guns traced to a purchaser in 2017-21 were recovered in Mexico; in 2022-23 Texas, Arizona and California dealers sourced 73% of traced Mexican crime guns, and 82% were recovered in states with a dominant Sinaloa or CJNG presence. Land (solid), sea (dotted), air (dashed). Width scaled by traced guns where sourced.", "sources": [ATF, ATF_MX, "GAO_FIREARMS"]},
}
for name, feats, ch in [("routes_drugs", drugs, "drugs"), ("routes_migrants", migr, "migrants"), ("routes_firearms", guns, "firearms")]:
    json.dump({"type": "FeatureCollection", "channel": ch, "notes": NOTES[ch], "features": feats}, open(os.path.join(D, name + ".geojson"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(name, len(feats))
