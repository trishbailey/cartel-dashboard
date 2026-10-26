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
 "San Diego": (-117.16, 32.72), "El Centro / Calexico": (-115.50, 32.70), "Yuma": (-114.62, 32.69), "Altar": (-111.82, 30.71), "Sásabe": (-111.54, 31.48),
 "Tucson": (-110.97, 32.22), "Sonoyta": (-112.86, 31.86), "Lukeville / Ajo": (-112.82, 32.05), "Caborca": (-112.16, 30.72), "El Paso": (-106.49, 31.76),
 "Puerto Palomas": (-107.63, 31.77), "Columbus (NM)": (-107.64, 31.83), "Hidalgo del Parral": (-105.67, 26.93), "Aldama (Chih.)": (-105.91, 28.84),
 "Ojinaga": (-104.41, 29.56), "Presidio (Big Bend)": (-104.37, 29.56), "Piedras Negras": (-100.52, 28.70), "Eagle Pass (Del Rio sector)": (-100.50, 28.71),
 "Laredo": (-99.51, 27.53), "McAllen": (-98.23, 26.20), "Brownsville": (-97.50, 25.90), "San Luis Potosí": (-100.98, 22.15), "Torreón": (-103.41, 25.54),
 "Nuevo Casas Grandes": (-107.91, 30.42), "El Ceibo": (-91.50, 17.25), "Tenosique": (-91.42, 17.47), "Chihuahua": (-106.09, 28.63),
 "Antwerp": (4.40, 51.22), "Rotterdam": (4.48, 51.92), "Hamburg": (9.99, 53.55), "Algeciras": (-5.45, 36.13), "Valencia": (-0.32, 39.45),
 "Galicia (Vigo)": (-8.72, 42.24), "Tanger-Med (Morocco)": (-5.50, 35.89), "Praia (Cabo Verde)": (-23.51, 14.92), "Cotonou (Benin)": (2.42, 6.36), "Banjul (Gambia)": (-16.58, 13.45),
 "Santa Marta": (-74.20, 11.24), "Moín (Costa Rica)": (-83.08, 10.00), "Colón (Panama)": (-79.90, 9.36), "Amazon mouth (Pará)": (-48.5, -1.4),
 "China (east-coast ports)": (121.5, 31.2), "India (west-coast ports)": (72.85, 18.95),
 "~a1": (-45.0, 24.0), "~a2": (-28.0, 37.5), "~a3": (-12.0, 45.0), "~a4": (-5.5, 48.6), "~a5": (1.2, 50.6), "~a6": (3.3, 51.6), "~a7": (6.5, 54.2), "~a8": (8.4, 54.0),
 "~g1": (-12.0, 36.8), "~g2": (-6.3, 35.95), "~g3": (-2.0, 36.4), "~g4": (0.4, 38.6), "~v1": (-10.5, 42.5),
 "~s1": (-44.5, -25.6), "~s2": (-36.0, -12.0), "~s3": (-29.0, 0.0), "~s4": (-24.0, 12.0), "~s5": (-17.5, 22.0), "~s6": (-11.0, 32.5), "~s7": (-4.0, 1.5), "~s8": (-18.5, 13.2),
 "~n1": (-45.0, 3.0), "~n2": (-30.0, 20.0), "~c1": (-72.0, 14.0), "~c2": (-64.0, 19.3), "~pr": (-60.0, 21.0), "~m1": (-80.5, 12.0),
 "~p1": (135.0, 30.0), "~p2": (160.0, 28.0), "~p3": (-170.0, 25.0), "~p4": (-145.0, 22.0), "~p5": (-120.0, 18.5), "~p6": (-108.0, 17.6),
 "~i0": (72.3, 10.0), "~i1": (80.0, 5.3), "~i2": (94.0, 6.6), "~i3": (101.6, 2.6), "~i4": (104.4, 1.15), "~i5": (110.0, 8.0), "~i6": (121.0, 20.6),
 "Lima": (-77.04, -12.05), "Tumbes (Peru-Ecuador border)": (-80.45, -3.57), "Colombia–Ecuador border": (-77.7, 0.85),
 "~gyeS": (-80.1, -2.9), "~gyeW": (-81.2, -2.3), "~ecMan": (-81.1, -0.9), "~ecN": (-80.5, 1.0), "~colP": (-79.3, 3.2), "~colP2": (-79.6, 6.5), "~gPan": (-79.45, 8.6), "~canal": (-79.7, 9.2), "~colon": (-79.9, 9.45), "~peN1": (-79.3, -10.5), "~peN2": (-81.7, -6.0), "~peN3": (-81.6, -3.6), "~prS": (-65.3, 17.8), "~prE": (-65.3, 18.6), "~prN": (-66.1, 18.6), "~hisN": (-68.5, 19.8), "~hisN2": (-72.0, 20.3), "~cubE": (-74.0, 20.6), "~obc1": (-75.3, 21.6), "~obc2": (-77.3, 22.75), "~obc3": (-78.8, 23.3), "~fs1": (-79.7, 24.3), "~fs2": (-80.0, 25.4), "~wind": (-73.8, 19.95), "~gon1": (-73.1, 19.0), "~gon2": (-72.6, 18.7), "~bhN1": (-79.6, 27.1), "~bhN2": (-77.6, 27.1), "~bhE1": (-76.0, 26.4), "~bhE2": (-74.8, 24.8), "~bhE3": (-73.8, 23.2), "~tci": (-72.3, 22.4), "~hisN3": (-72.4, 20.3), "~nic1": (-82.5, 14.8), "~nic2": (-83.6, 15.65), "~azS": (-79.9, 6.9), "~cho1": (-78.0, 5.5), "~cho2": (-77.6, 4.3), "Tumbes (Peru-Ecuador border)": (-80.45, -3.57), "Colombia–Ecuador border": (-77.7, 0.85),
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
CBP24 = S("https://www.cbp.gov/newsroom/stats/migrant-protection-protocols-fy2024", "CBP", "USBP apprehensions by Southwest Border sector, FY2024 (Oct 2023-Sep 2024)", "FY2024")
CBP25 = S("https://www.cbp.gov/newsroom/national-media-release/lowest-fiscal-year-border-patrol-apprehensions-1970", "CBP", "Lowest fiscal year for Border Patrol apprehensions since 1970 (FY2025: 237,565)", "2025-10-07")
BR24 = S("https://www.borderreport.com/border-report-tour/immigration/south-texas-border-patrol-sectors-saw-big-drops-in-migrant-encounters-in-fiscal-2024/", "Border Report", "South Texas Border Patrol sectors saw big drops in migrant encounters in Fiscal 2024", "2024-10")
IC_SON = S("https://insightcrime.org/news/sonora-mexico-under-siege-amid-sinaloa-cartel-battle-over-migrant-smuggling/", "InSight Crime", "Sinaloa Cartel battle over migrant smuggling in Sonora, Mexico")
IC_DES = S("https://insightcrime.org/news/desperation-desert-migrant-smuggling-us-mexico-border/", "InSight Crime", "Desperation in the desert: the industrialization of migrant smuggling on the US-Mexico border")
AP_LUKE = S("https://apnews.com/article/lukeville-arizona-border-crossing-closed-ae04e8c861a95e98dbfc8d49244cf092", "AP", "Smugglers bring migrants to Arizona border crossing, overwhelming US agents", "2023-12")
JBC_SON = S("https://jornadabc.com.mx/region/entrada-de-frente-frio-complica-situacion-de-migrantes/", "La Jornada Baja California", "Entrada de frente frío complica situación de migrantes (Sonoyta, San Luis Río Colorado)", "2023-12-08")
UNI_TJ = S("https://www.uniradiobaja.com/gobierno/crimen-organizado-controla-trafico-personas-pagos-traslado-o-cobro-piso-dejar-pasar-migrantes-dmam-tijuana-n729721", "Uniradio Informa", "Crimen organizado controla tráfico de personas con pagos por traslado o cobro de piso (Tijuana)", "2024")
ZETA_SY = S("https://zetatijuana.com/2024/02/las-mafias-en-garita-de-san-ysidro/", "Semanario ZETA", "Las mafias en Garita de San Ysidro", "2024-02")
IC_LINEA = S("https://insightcrime.org/mexico-organized-crime-news/la-linea/", "InSight Crime", "La Línea: profile")
USAT_JZ = S("https://www.usatoday.com/story/news/investigations/2024/06/20/mexican-drug-cartels-migrant-vip-package/74154061007/", "USA Today", "Mexican drug cartels offer migrants VIP package for passage into US", "2024-06-20")
DIA_JZ = S("https://diario.mx/juarez/2025/jun/03/al-dia-70-detenciones-de-migrantes-1069206.html", "El Diario de Juárez", "Al día, 70 detenciones de migrantes", "2025-06-03")
JOR_JZ = S("https://www.jornada.com.mx/2022/07/01/politica/008n2pol", "La Jornada", "El cruce de personas de Juárez a El Paso, en control de La Línea", "2022-07-01")
REU_TRAIN = S("https://www.reuters.com/world/americas/migrants-aboard-mexico-cargo-trains-stranded-miles-us-border-2023-09-30/", "Reuters", "Migrants aboard Mexico cargo trains stranded miles from U.S. border", "2023-09-30")
SIG_PN = S("https://www.elsiglodetorreon.com.mx/noticia/2023/miles-de-migrantes-arriban-a-piedras-negras-cruzan-el-rio-bravo-y-llegan-a-eua.html", "El Siglo de Torreón", "Miles de migrantes arriban a Piedras Negras, cruzan el río Bravo y llegan a EUA", "2023-09")
OFAC_CDN = S("https://home.treasury.gov/news/press-releases/sb0219", "US Treasury (OFAC)", "Treasury sanctions additional members and associate of Cartel del Noreste", "2025")
DOJ_CDN = S("https://www.justice.gov/usao-sdtx/pr/two-sent-prison-roles-cartel-linked-human-smuggling-scheme", "US Attorney SDTX", "Two sent to prison for roles in cartel-linked (CDN) human smuggling scheme", "2024-10-30")
IC_CDG = S("https://insightcrime.org/mexico-organized-crime-news/gulf-cartel-profile/", "InSight Crime", "Gulf Cartel: profile and current status")
MND_TAB = S("https://mexiconewsdaily.com/news/migrants-find-new-route-into-mexico-via-tabasco-but-also-dangers/", "Mexico News Daily", "Migrants find new route into Mexico via Tabasco but also dangers")
MSF_MAP = S("https://www.msf.org.co/wp-content/uploads/2023/07/Mapa-MSF-en-ruta-contigo.pdf", "MSF", "Mapa MSF en ruta contigo (migrant route assistance points)", "2023-07")
SEC = {"San Diego": 324260, "El Centro": 17484, "Yuma": 53877, "Tucson": 463567, "El Paso": 256102, "Big Bend": 4921, "Del Rio": 244105, "Laredo": 31108, "Rio Grande Valley": 135099}

def F(channel, subtype, pts, desc, src, year, width=None, sector=None, control=None, csrc=None):
    p = {"channel": channel, "subtype": subtype, "from": pts[0], "to": pts[-1], "description": desc, "sources": src, "year": year}
    if width: p["volume"] = width
    if sector:
        p.update(sector=sector, encounters=SEC[sector], encounters_year="FY2024", volume=SEC[sector])
        if CBP24 not in src: src.append(CBP24)
    if control: p["control"], p["control_sources"] = control, csrc
    pts = [x for x in pts if x != "~SEAM"]  # world map seam now at 45E (Saudi Arabia), so Indian Ocean to Pacific is continuous
    geo = {"type": "LineString", "coordinates": [list(P[x]) for x in pts]}
    return {"type": "Feature", "properties": p, "geometry": geo}

drugs = [
 F("drugs", "cocaine", ["Tumaco", "Central America Pacific (offshore)", "Guatemala Pacific coast"], "Cocaine leaves Colombia's southern Pacific coast by go-fast boat and semi-submersible for Central America's Pacific coast.", ["UNODC_WDR25", "IC_URABENOS", "JS_STRIKES"], "2025"),
 F("drugs", "cocaine", ["Buenaventura", "Central America Pacific (offshore)", "Chiapas coast"], "Shipments from Buenaventura run north along the Pacific to southern Mexico.", ["UNODC_WDR25", "IC_URABENOS"], "2025"),
 F("drugs", "cocaine", ["Guayaquil", "~gyeS", "~gyeW", "Galápagos (offshore)", "Central America Pacific (offshore)", "Guerrero coast"], "Ecuadorian ports feed a long Pacific route, sometimes skirting the Galápagos, to Mexico's Pacific coast.", ["IC_ECUADOR", "IC_CHONEROS", "UNODC_WDR25"], "2025"),
 F("drugs", "cocaine", ["Manta", "Galápagos (offshore)", "Central America Pacific (offshore)"], "Manta and Esmeraldas launch boats that hand loads to Mexican buyers offshore.", ["IC_LOBOS", "IC_ECUADOR"], "2025"),
 F("drugs", "cocaine", ["Guerrero coast", "Tierra Caliente (Michoacán)", "Guadalajara", "Culiacán", "Nogales"], "Cocaine landed on Mexico's Pacific coast moves overland under Sinaloa and CJNG control to the Arizona and California crossings.", ["DEA25", "IC_SINALOA", "IC_CJNG"], "2025"),
 F("drugs", "cocaine", ["Guajira/Falcón coast", "Santo Domingo"], "Cocaine moves by boat and light aircraft from Venezuela's and Colombia's Caribbean coast to the Dominican Republic.", ["IC_SOLES", "UNODC_WDR25", "JS_STRIKES"], "2025"),
 F("drugs", "cocaine", ["Venezuela east coast", "~prS", "~prE", "~prN", "San Juan", "~prN", "~hisN", "~hisN2", "~cubE", "~obc1", "~obc2", "~obc3", "~fs1", "~fs2", "Miami"], "Puerto Rico is a Caribbean entry point for US-bound cocaine.", ["DEA25", "UNODC_WDR25"], "2025"),
 F("drugs", "cocaine", ["Cartagena", "Haiti south coast"], "Haiti's south coast is a transshipment point on the Caribbean route.", ["IC_HAITI", "UNODC_WDR25"], "2025"),
 F("drugs", "cocaine", ["Cartagena", "~nic1", "~nic2", "Honduras Mosquitia"], "Air and sea loads land in Honduras' Mosquitia and start the Central American land bridge.", ["UNODC_WDR25", "IC_HONDURAS"], "2025"),
 F("drugs", "cocaine", ["Honduras Mosquitia", "San Pedro Sula", "Petén", "Villahermosa", "Veracruz", "Reynosa"], "The land corridor runs through Honduras and Guatemala's Petén into Tabasco, then up the Gulf side to the Tamaulipas border.", ["UNODC_WDR25", "IC_GUATEMALA", "IC_GULF"], "2025"),
 F("drugs", "cocaine", ["Petén", "Tapachula"], "A western branch enters Mexico through Chiapas.", ["UNODC_WDR25", "IC_GUATEMALA", IC_TAP], "2025"),
 F("drugs", "cocaine", ["Guayaquil", "~gyeS", "~gyeW", "~ecMan", "~ecN", "~colP", "~colP2", "~gPan", "~canal", "~colon", "~c1", "~c2", "~pr", "~a1", "~a2", "~a3", "~a4", "~a5", "~a6", "Antwerp"], "Containers from Guayaquil carry cocaine through the Panama Canal to Antwerp, the EU's main cocaine entry port; EUDA counts Antwerp seizures from Guayaquil rising from 6 t (2018) to 55.6 t (2021).", [EUDA_C, "IC_ECUADOR"], "2021"),
 F("drugs", "cocaine", ["VRAEM", "Chapare", "Santa Cruz", "Santos", "~s1", "~s2", "~s3", "~s4", "~s5", "~s6", "~a3", "~a4", "~a5", "~a6", "Antwerp"], "Peruvian and Bolivian cocaine crosses Bolivia to Brazil's Santos port, where the PCC organises container exports; Santos was the second source port for cocaine bound for Belgian ports in 2018-21 (about 49 t seized).", [EUDA_N, "IC_PCC", "UNODC_WDR25"], "2025"),
 F("drugs", "cocaine", ["Santa Cruz", "Paranaguá", "~s1", "~s2", "~s3", "~s4", "~s5", "~s6", "~a3", "~a4", "~a5", "~a6", "Antwerp"], "Paranaguá is the second major Brazilian export port that EUDA names; about 25 t bound for Belgian ports was seized in 2018-21.", [EUDA_N, EUDA_C], "2025"),
 F("drugs", "cocaine", ["Santa Cruz", "Villeta", "~s1", "~s2", "~s3", "~s4", "~s5", "~s6", "~a3", "~a4", "~a5", "~a6", "Antwerp"], "Paraguay's river port of Villeta ships Bolivian cocaine downriver and across the Atlantic; 13.5 t bound for Belgian ports was seized in 2018-21.", [EUDA_C, "IC_PARAGUAY"], "2025"),
 F("drugs", "cocaine", ["Callao", "~peN1", "~peN2", "~peN3", "~ecMan", "~ecN", "~colP", "~colP2", "~gPan", "~canal", "Colón (Panama)"], "Peru's Callao container port is an export point to Europe; the sources do not name a European arrival port, so the line stops where it joins the Atlantic container lanes at Colón.", ["UNODC_WDR25"], "2025"),
 F("drugs", "precursor", ["China (east-coast ports)", "~p1", "~p2", "~p3", "~p4", "~p5", "Manzanillo"], "Precursor chemicals from China arrive by ship at Manzanillo, per DEA and US Treasury; sources name the country, not the Chinese port, so the start dot is placed at the east-coast port belt.", ["DEA25", "OFAC_JY1413", "OFAC_SB0468"], "2025"),
 F("drugs", "precursor", ["China (east-coast ports)", "~p1", "~p2", "~p3", "~p4", "~p6", "Lázaro Cárdenas"], "Lázaro Cárdenas is the second main Pacific entry port for Asian precursors.", ["DEA25", "OFAC_JY1413"], "2025"),
 F("drugs", "precursor", ["India (west-coast ports)", "~i0", "~i1", "~i2", "~i3", "~SEAM", "~i4", "~i5", "~i6", "~p2", "~p3", "~p4", "~p5", "Manzanillo"], "DEA names India, with China, as a main source of fentanyl precursors shipped to Mexican Pacific ports; sources name the country, not the Indian port.", ["DEA25"], "2025"),
 F("drugs", "cocaine", ["Necoclí / Turbo", "~c1", "~c2", "~pr", "~a1", "~a2", "~a3", "~a4", "~a5", "~a6", "Antwerp"], "Turbo on Colombia's Urabá coast was the fourth source port for cocaine bound for Belgian ports in 2018-21 (about 25 t seized).", [EUDA_C, "IC_URABENOS"], "2021"),
 F("drugs", "cocaine", ["Santa Marta", "~c2", "~pr", "~a1", "~a2", "~a3", "~a4", "~a5", "~a6", "Antwerp"], "Santa Marta shipped about 33 t of cocaine seized en route to Belgian ports in 2018-21, mostly hidden in legitimate cargo.", [EUDA_C], "2021"),
 F("drugs", "cocaine", ["Moín (Costa Rica)", "~m1", "~c1", "~c2", "~pr", "~a1", "~a2", "~a3", "~a4", "~a5", "~a6", "Rotterdam"], "Costa Rica's Moín terminal is a top source port for Belgian- and Dutch-bound cocaine; Antwerp and Rotterdam took almost 65% of EU port seizures in 2020.", [EUDA_C], "2021"),
 F("drugs", "cocaine", ["Colón (Panama)", "~c1", "~c2", "~pr", "~a1", "~a2", "~a3", "~a4", "~a5", "~a6", "~a7", "~a8", "Hamburg"], "Hamburg is a rising cocaine entry point that German police tie to Balkan and Albanian-speaking networks; Colón is one of the top source ports for Europe-bound loads.", [EUDA_C], "2021"),
 F("drugs", "cocaine", ["Colón (Panama)", "~c1", "~c2", "~pr", "~a1", "~a2", "~g1", "~g2", "Algeciras"], "Spain's Algeciras is one of the EU's largest container entry points for cocaine (5.3 t seized in 2020).", [EUDA_C], "2021"),
 F("drugs", "cocaine", ["Colón (Panama)", "~c1", "~c2", "~pr", "~a1", "~a2", "~g1", "~g2", "~g3", "~g4", "Valencia"], "Valencia is the third EU port for cocaine seizures (7.7 t in 2020).", [EUDA_C], "2021"),
 F("drugs", "cocaine", ["Amazon mouth (Pará)", "~n1", "~n2", "~a2", "~v1", "Galicia (Vigo)"], "In 2019 a semi-submersible carrying 3 t of cocaine crossed from the Amazon to Galicia, the first caught in Europe.", [EUDA_C], "2019"),
 F("drugs", "cocaine", ["Santos", "~s1", "~s2", "~s3", "~s4", "Praia (Cabo Verde)", "~s5", "~s6", "~g2", "Tanger-Med (Morocco)"], "Via West Africa's islands: 11 t was seized in Cabo Verde in 2019 from a ship bound for Tangier, and Tanger-Med intercepted Brazil-to-Antwerp loads in 2021.", [EUDA_C], "2021"),
 F("drugs", "cocaine", ["Santos", "~s1", "~s2", "~s3", "~s7", "Cotonou (Benin)"], "The Gulf of Guinea is a transit area: Benin, Côte d'Ivoire and Senegal reported large cocaine seizures in 2020, including 0.5 t bound for Europe seized in Cotonou.", [EUDA_C, "IC_PCC"], "2020"),
 F("drugs", "cocaine", ["Santos", "~s1", "~s2", "~s3", "~s4", "~s8", "Banjul (Gambia)"], "In January 2021 Gambia seized 2.9 t of cocaine in a container of industrial salt at Banjul port.", [EUDA_C], "2021"),
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
 # ---- southern entry, interior trunks and staging cities feeding the nine USBP southwest sectors ----
 F("migrants", "northbound land", ["Petén", "El Ceibo", "Tenosique", "Villahermosa"], "The El Ceibo–Tenosique crossing into Tabasco is the main eastern entry, about 60 km by road; MSF runs assistance points in Tenosique and coyotes charge thousands of dollars.", [MND_TAB, MSF_MAP], "2023"),
 F("migrants", "northbound land", ["Mexico City", "San Luis Potosí", "Monterrey"], "The central route runs from Mexico City through San Luis Potosí to Monterrey, the staging hub for the Coahuila and Tamaulipas crossings.", [GI_MX, IC_DES], "2018"),
 F("migrants", "rail (La Bestia)", ["Monterrey", "Torreón", "Chihuahua", "Ciudad Juárez"], "In 2023 thousands of migrants rode freight trains north through Torreón toward Ciudad Juárez and Piedras Negras until Ferromex halted trains.", [REU_TRAIN], "2023"),
 F("migrants", "northbound land", ["Tijuana", "San Diego"], "Tijuana feeds the San Diego sector, the second busiest in FY2024; Tijuana officials say organised crime now controls smuggling through transport payments or piso charged to let migrants pass.", [UNI_TJ, ZETA_SY], "2024", sector="San Diego",
   control="Organised crime charges piso per migrant (Tijuana migrant affairs office); ZETA reports Sinaloa Cartel-linked and Arellano Félix-linked cells competing around the San Ysidro crossing.", csrc=[UNI_TJ, ZETA_SY]),
 F("migrants", "northbound land", ["Mexicali", "El Centro / Calexico"], "Mexicali feeds the El Centro sector; Tijuana officials report migrants being moved from Tijuana toward Mexicali crossings.", [UNI_TJ], "2024", sector="El Centro"),
 F("migrants", "northbound land", ["San Luis Río Colorado", "Yuma"], "San Luis Río Colorado feeds the Yuma sector; in December 2023 CBP warned it might close the San Luis crossings as crossings surged.", [JBC_SON], "2023", sector="Yuma"),
 F("migrants", "northbound land", ["Hermosillo", "Altar", "Sásabe", "Tucson"], "Altar is the staging town for the desert crossing near Sásabe into the Tucson sector, the busiest in FY2024.", [IC_SON, IC_DES], "2023", sector="Tucson",
   control="Sinaloa Cartel factions control the Altar–Sásabe corridor and collect at least $100 per migrant, plus about $1,000 for unguided 'permission' to cross (InSight Crime).", csrc=[IC_DES, IC_SON]),
 F("migrants", "northbound land", ["Hermosillo", "Caborca", "Sonoyta", "Lukeville / Ajo"], "In December 2023 smugglers delivered thousands of migrants a day near Sonoyta–Lukeville, forcing CBP to close the Lukeville port (Tucson sector, Ajo station).", [AP_LUKE, JBC_SON], "2023", sector="Tucson"),
 F("migrants", "northbound land", ["Chihuahua", "Ciudad Juárez", "El Paso"], "Ciudad Juárez feeds the El Paso sector; smugglers even use the storm-drain tunnels into El Paso, charging $6,000 or more.", [USAT_JZ, DIA_JZ], "2024", sector="El Paso",
   control="La Línea controls the Juárez–El Paso polleros (La Jornada 2022) and moved 1,000+ migrants a month through drain tunnels (USA Today); La Empresa and Los Cabrera also operate in Juárez and the Valle (El Diario 2025).", csrc=[JOR_JZ, USAT_JZ, DIA_JZ, IC_LINEA]),
 F("migrants", "northbound land", ["Nuevo Casas Grandes", "Puerto Palomas", "Columbus (NM)"], "Puerto Palomas, west of Juárez, is a main irregular crossing in the El Paso sector's New Mexico stretch.", [DIA_JZ], "2025", sector="El Paso",
   control="La Línea runs the main irregular crossing at Puerto Palomas, per Chihuahua authorities (El Diario 2025).", csrc=[DIA_JZ]),
 F("migrants", "northbound land", ["Hidalgo del Parral", "Aldama (Chih.)", "Ojinaga", "Presidio (Big Bend)"], "Chihuahua state police describe a Parral–Aldama–Ojinaga smuggling route into the Big Bend sector, the quietest of the nine.", [DIA_JZ], "2025", sector="Big Bend",
   control="Los Cabrera are moving into the Parral–Aldama–Ojinaga route (Chihuahua state police via El Diario).", csrc=[DIA_JZ]),
 F("migrants", "northbound land", ["Monterrey", "Piedras Negras", "Eagle Pass (Del Rio sector)"], "In September 2023 thousands, mostly Venezuelans, travelled from Monterrey by train and bus to Piedras Negras and waded the Rio Grande into Eagle Pass (Del Rio sector).", [REU_TRAIN, SIG_PN, BR24], "2023", sector="Del Rio",
   control="Cartel del Noreste holds influence in Piedras Negras and runs human smuggling into the US (US Treasury, 2025).", csrc=[OFAC_CDN]),
 F("migrants", "northbound land", ["Monterrey", "Nuevo Laredo", "Laredo"], "Nuevo Laredo feeds the Laredo sector; US prosecutors describe CDN-recruited smugglers moving migrants in tractor trailers past the I-35 checkpoint.", [DOJ_CDN, BR24], "2024", sector="Laredo",
   control="Cartel del Noreste: US court case (SDTX 2024) says CDN recruited smugglers; Treasury says CDN dominates the Laredo crossing.", csrc=[DOJ_CDN, OFAC_CDN]),
 F("migrants", "northbound land", ["Monterrey", "Reynosa", "McAllen"], "Reynosa feeds the Rio Grande Valley sector, which once led the border and fell 60% in FY2024.", [BR24, IC_CDG], "2024", sector="Rio Grande Valley",
   control="Gulf Cartel factions, chiefly the Scorpions and Cyclones, control Reynosa and Matamoros and smuggle migrants (InSight Crime).", csrc=[IC_CDG]),
 F("migrants", "northbound land", ["Matamoros", "Brownsville"], "Matamoros is the Gulf route's last stop, crossing into Brownsville in the Rio Grande Valley sector.", [BR24, IC_CDG], "2024", sector="Rio Grande Valley",
   control="Gulf Cartel factions control Matamoros and smuggle migrants from the border (InSight Crime).", csrc=[IC_CDG]),
 F("migrants", "southbound (reverse) 2025", ["Peñas Blancas", "Paso Canoas", "Panama City"], "In 2025 Costa Rica and Panama bused southbound migrants along the old northbound route.", [AP_REV, MPI], "2025"),
 F("migrants", "southbound (reverse) 2025", ["Panama City", "Colón (Miramar/Palenque)", "Capurganá", "Necoclí / Turbo"], "Panama recorded 22,300+ people heading south to Colombia in 2025, mostly Venezuelans, many taking boats from Colón to Capurganá.", [HIAS, TNH], "2025", 22300),
 F("migrants", "southbound (reverse) 2025", ["Panama City", "Jaque (Darién)", "~cho1", "~cho2", "Buenaventura"], "A Pacific boat route from Panama City via Jaque also returns migrants to Colombia.", [HIAS], "2025"),
]
guns = [
 F("firearms", "land", ["Phoenix", "Nogales", "Hermosillo", "Culiacán"], "Arizona to Sonora is the single largest US–Mexico gun pipeline in ATF trace data; Arizona dealers sourced about 22% of traced Mexican crime guns in 2022-23.", [ATF], "2023", 3969),
 F("firearms", "land", ["Houston", "Matamoros"], "Texas to Tamaulipas is the second-largest pipeline; Texas dealers sourced 43% of traced Mexican crime guns (7,825 of 18,205).", [ATF], "2023", 7825),
 F("firearms", "land", ["Dallas", "Nuevo Laredo", "Monterrey"], "Texas to Nuevo León is the third of ATF's top five pipelines.", [ATF], "2023"),
 F("firearms", "land", ["Albuquerque", "Ciudad Juárez"], "Guns from Texas and New Mexico go south through Ciudad Juárez into Chihuahua (Texas–Chihuahua is a top-five pipeline).", [ATF], "2023"),
 F("firearms", "land", ["Houston", "Monterrey", "Guadalajara"], "Texas to Guanajuato completes ATF's top five pipelines, which carry 32% of traced guns.", [ATF], "2023"),
 F("firearms", "land", ["Los Angeles", "Tijuana"], "California dealers were the third US source (2,734 traced guns, 2022-23), mostly through Baja California.", [ATF, "GAO_FIREARMS"], "2023", 2734),
 F("firearms", "sea", ["Miami", "~fs2", "~fs1", "~obc3", "~obc2", "~obc1", "~wind", "~gon1", "~gon2", "Port-au-Prince"], "UNODC's primary Haiti route: guns shipped from Florida in containers to public and private ports in Port-au-Prince.", [UNODC_H1, UNODC_H3], "2024"),
 F("firearms", "sea", ["Fort Lauderdale", "~bhN1", "~bhN2", "~bhE1", "~bhE2", "~bhE3", "~tci", "~hisN3", "Port-de-Paix"], "Indirect shipments from Florida, sometimes via the Bahamas and Turks and Caicos, land in Port-de-Paix, Saint-Marc and Gonaïves.", [UNODC_H1], "2023"),
 F("firearms", "sea", ["Fort Lauderdale", "~bhN1", "~bhN2", "~bhE1", "~bhE2", "~bhE3", "~tci", "Cap-Haïtien"], "In April 2024 Haitian police seized guns in a container shipped from Port Everglades to Cap-Haïtien for Artibonite gangs.", [UNODC_H3], "2024"),
 F("firearms", "land", ["Santo Domingo", "Dominican border (Dajabón)", "Gonaïves"], "Arms and ammunition also cross Haiti's land border from the Dominican Republic.", [UNODC_H1, UNODC_H3], "2024"),
 F("firearms", "air", ["Miami", "Manta"], "Ecuadorian police name a Miami–Manta air route among three US-origin gun routes into Ecuador.", [REU_EC, IC_ECG], "2024"),
 F("firearms", "land", ["Lima", "Tumbes (Peru-Ecuador border)", "Guayaquil"], "Three overland gun routes enter Ecuador from Peru, including US guns that arrive via Lima.", [REU_EC, IC_ECG], "2024"),
 F("firearms", "sea", ["Panama Canal", "~canal", "~gPan", "~azS", "Galápagos (offshore)", "~gyeW", "~gyeS", "Guayaquil"], "Police also describe a sea route via the Galápagos, and guns hidden in containers have been seized at Guayaquil.", [REU_EC, IC_ECA], "2024"),
 F("firearms", "land", ["Colombia–Ecuador border", "Esmeraldas"], "A further route enters northern Ecuador from the Colombian border.", [REU_EC], "2024"),
]
NOTES = {
 "drugs": {"note": "Covers cocaine, precursor chemicals and synthetics (fentanyl, meth). Lines are schematic corridors between places named in sources, drawn along sea lanes, not tracks. Use the World view to see Europe, West Africa and Asia endpoints.", "sources": ["DEA25", "UNODC_WDR25", EUDA_C]},
 "migrants": {"note": " Lines ending at the border are widened by US Border Patrol apprehensions in that sector in FY2024 (Oct 2023-Sep 2024; 1.53 million across nine sectors, Tucson highest at 463,567). That was the last full year before the collapse: FY2025 fell to 237,565, the lowest since 1970, with only about 65,500 after 20 January 2025, so these corridors now carry a small fraction of FY2024 traffic. Two lines into one sector share its total. Darién width is the 2023 crossing count.", "sources": [CBP24, CBP25, MPI, HIAS]},
 "firearms": {"note": "ATF: 74% of international crime guns traced to a purchaser in 2017-21 were recovered in Mexico; in 2022-23 Texas, Arizona and California dealers sourced 73% of traced Mexican crime guns, and 82% were recovered in states with a dominant Sinaloa or CJNG presence. Width scaled by traced guns where sourced.", "sources": [ATF, ATF_MX, "GAO_FIREARMS"]},
}
for name, feats, ch in [("routes_drugs", drugs, "drugs"), ("routes_migrants", migr, "migrants"), ("routes_firearms", guns, "firearms")]:
    json.dump({"type": "FeatureCollection", "channel": ch, "notes": NOTES[ch], "features": feats}, open(os.path.join(D, name + ".geojson"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(name, len(feats))
