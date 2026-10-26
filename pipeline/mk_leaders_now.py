import json
P="/workspace/cartel-dashboard/data/"
d=json.load(open(P+"leaders.json"));L=d["leaders"];by={l["id"]:l for l in L}
S=lambda n,u,dt=None:{"name":n,"url":u,**({"date":dt} if dt else {})}
CO,RM,RC="confirmed by officials","reported by multiple outlets","reported, contested"
ph={"file":None,"placeholder":True,"image_source_url":None,"license":"n/a (neutral placeholder; no clean official or openly licensed photo found)","credit":None}
for l in L: l["title"]=l.pop("role")
def setr(i,g,r,c=None,note=None):
    l=by[i];l["group_key"]=g;l["role"]=r
    if c:l["confidence"]=c
    if note:l["leadership_note"]=note
setr("ivan-guzman","chapitos","current_leader",CO);setr("alfredo-guzman","chapitos","current_leader",CO)
setr("ovidio-guzman","chapitos","former_leader");setr("joaquin-guzman-lopez","chapitos","former_leader")
setr("el-mayo","mayiza","former_leader");setr("mayito-flaco","mayiza","current_leader",CO)
setr("el-mencho","cjng","former_leader");setr("el-pelon","cjng","reported_successor",RC)
setr("r-1","gulf","faction_leader",RC,"State's reward dates from 2017; no recent professional reporting confirms he still runs Los Rojos.")
setr("z-40","cdn","former_leader");setr("el-pez","lnfm","current_leader",CO);setr("el-fresa","lnfm","current_leader",CO)
setr("el-abuelo","unidos","current_leader",CO);setr("nino-guerrero","tda","former_leader");setr("fito","choneros","former_leader")
setr("pipo","lobos","former_leader");setr("chiquito-malo","clan","current_leader",CO);setr("antonio-garcia","eln","current_leader",CO)
setr("diablito","ms13","former_leader");setr("marcola","pcc","current_leader",RM,"Leads from prison: São Paulo police's 2026 organogram places him at the head of the Sintonia Final.")
by["marcola"]["sources"].append(S("G1","https://g1.globo.com/sp/sao-paulo/noticia/2026/02/24/novo-organograma-feito-pela-policia-civil-revela-estrutura-empresarial-do-pcc-com-setores-de-compliance-e-rede-social.ghtml","2026-02-24"))
by["antonio-garcia"]["status_note"]+=" Convicted in absentia (first instance, under appeal) with the rest of the Central Command on 2026-09-28."
by["antonio-garcia"]["sources"].append(S("Infobae","https://www.infobae.com/colombia/2026/09/28/gabino-antonio-garcia-pablo-beltran-y-otros-11-maximos-cabecillas-del-eln-fueron-condenados-a-20-anos-de-prision-por-el-reclutamiento-forzado-de-60-menores-de-edad/","2026-09-28"))
def new(**k):
    k.setdefault("faction","");k.setdefault("reward_usd",None);k.setdefault("reward_source",None);k.setdefault("photo",dict(ph));L.append(k);by[k["id"]]=k
IBG="https://www.infobae.com/mexico/2026/10/20/el-primito-pide-amparo-para-evitar-su-extradicion-a-eeuu-el-lider-del-cjng-sigue-profugo/"
new(id="primito",name="César Morfín Morfín",alias="Primito / Metro 300",group_ids=["gulf"],group_key="gulf",faction="Los Metros",title="Head of Los Metros, the Gulf faction allied with CJNG",role="faction_leader",confidence=RM,
 status="at_large",status_date="2026-10-20",status_note="Fugitive; filed an injunction against extradition to the US (Oct 2026).",status_source=S("Infobae",IBG,"2026-10-20"),
 charges=["Sought by the US for extradition"],known_for="DEA says Los Metros act as CJNG's enforcement arm in northeastern Mexico.",sources=[S("Infobae",IBG,"2026-10-20"),S("El Universal","https://www.eluniversal.com.mx/nacion/el-primito-lider-del-cjng-en-tamaulipas-se-ampara-contra-extradicion-a-eu-sigue-profugo/")])
new(id="escorpion-7",name="Armando López Garcés",alias="Escorpión 7 / El Pajarito",group_ids=["gulf"],group_key="gulf",faction="Los Escorpiones",title="Reported head of Los Escorpiones faction",role="faction_leader",confidence=RC,
 status="at_large",status_date="2026-07-16",status_note="Named as Gulf Cartel leader by MVS; InSight Crime describes him only as a possible successor in the Escorpiones faction.",status_source=S("MVS Noticias","https://mvsnoticias.com/nacional/2026/7/16/los-ocho-carteles-mexicanos-declarados-organizaciones-terroristas-por-eu-738636.html","2026-07-16"),
 charges=[],known_for="Los Escorpiones fight Los Metros and CDN for Reynosa and Matamoros.",sources=[S("MVS Noticias","https://mvsnoticias.com/nacional/2026/7/16/los-ocho-carteles-mexicanos-declarados-organizaciones-terroristas-por-eu-738636.html","2026-07-16"),S("InSight Crime","https://insightcrime.org/es/noticias-crimen-organizado-mexico/cartel-del-golfo-perfil/")])
ICN="https://insightcrime.org/mexico-organized-crime-news/northeast-cartel/"
new(id="juanito",name="Juan Cisneros Treviño",alias="El Juanito / La Sombra",group_ids=["cdn"],group_key="cdn",title="Leader of Cártel del Noreste",role="current_leader",confidence=RM,
 status="at_large",status_date="2026-07-16",status_note="Took over CDN and its Tropa del Infierno after El Huevo's March 2022 arrest.",status_source=S("InSight Crime",ICN),
 charges=[],known_for="Described as the last of the Treviño family line; Treasury names Abdón Rodríguez 'Cucho' as second in command.",sources=[S("InSight Crime",ICN),S("MVS Noticias","https://mvsnoticias.com/nacional/2026/7/16/los-ocho-carteles-mexicanos-declarados-organizaciones-terroristas-por-eu-738636.html","2026-07-16")])
TG="https://www.infobae.com/colombia/2026/06/16/quien-es-giovanny-el-nuevo-lider-del-tren-de-aragua-en-colombia-tras-el-bombardeo-ordenado-por-ee-uu-que-dio-de-baja-a-nino-guerrero/"
CNN="https://cnnespanol.cnn.com/2026/06/16/latinoamerica/muerte-nino-guerrero-sucesion-tren-aragua-orix"
new(id="giovanny",name="Giovanni Vicente Mosquera Serrano",alias="Giovanny / El Viejo",group_ids=["tda"],group_key="tda",title="Reported new operational head of Tren de Aragua",role="reported_successor",confidence=RC,
 status="at_large",status_date="2026-06-16",status_note="Colombian police and prosecutors (per El Tiempo) say power passed to him after Niño Guerrero's death; on the FBI Ten Most Wanted list.",status_source=S("Infobae",TG,"2026-06-16"),
 charges=["On FBI Ten Most Wanted list"],known_for="Credited with TdA's extortion and kidnapping rackets in Bogotá and other Colombian cities.",
 sources=[S("El Tiempo","https://www.eltiempo.com/justicia/conflicto-y-narcotrafico/giovanni-vicente-mosquera-alias-el-viejo-el-capo-que-hereda-el-poder-del-tren-de-aragua-en-colombia-tras-la-muerte-de-nino-guerrero-3564483"),S("Infobae",TG,"2026-06-16"),S("CNN en Español",CNN,"2026-06-16")],
 photo={"file":"img/leaders/giovanny.jpg","placeholder":False,"image_source_url":"https://commons.wikimedia.org/wiki/File:Picture_of_Giovanni_Vicente_Mosquera_Serrano.webp","license":"Public domain (work of the US federal government)","credit":"FBI (via Wikimedia Commons)"})
IP="https://insightcrime.org/es/noticias-crimen-organizado-venezuela/yohan-jose-romero-alias-johan-petrica/"
new(id="petrica",name="Yohan José Romero",alias="Johan Petrica",group_ids=["tda"],group_key="tda",title="TdA co-founder; Las Claritas mining boss",role="reported_successor",confidence=RC,
 status="at_large",status_date="2026-06-16",status_note="InSight Crime says he may be the highest-ranking TdA leader still free, but the group is fragmented.",status_source=S("InSight Crime",IP),
 reward_usd=4000000,reward_source=S("CNN en Español",CNN,"2026-06-16"),charges=["Sanctioned by the US (2025)"],known_for="Runs the Sindicato de Las Claritas gold-mining enclave in Bolívar.",sources=[S("InSight Crime",IP),S("CNN en Español",CNN,"2026-06-16")])
CH="https://www.infobae.com/america/america-latina/2026/07/03/detuvieron-en-ecuador-a-churron-el-lider-criminal-de-los-choneros-por-el-que-eeuu-ofrecia-usd-5-millones/"
new(id="churron",name="Francisco Manuel Bermúdez Cagua",alias="Churrón",group_ids=["choneros"],group_key="choneros",title="Led Los Choneros after Fito",role="former_leader",
 status="jailed",status_date="2026-07-02",status_note="Captured in Guayaquil 2026-07-02; held in La Cárcel del Encuentro pending extradition to the US.",status_source=S("Infobae",CH,"2026-07-03"),
 charges=["EDNY indictment (June 2025): cocaine conspiracy, firearms; former $5M reward"],known_for="High-ranking lieutenant of Fito, per the US indictment.",sources=[S("Infobae",CH,"2026-07-03"),S("El Universo","https://www.eluniverso.com/noticias/seguridad/cae-alias-churron-el-ultimo-cabecilla-de-los-choneros-requerido-por-estados-unidos-nota/")])
LM="https://www.primicias.ec/politica/daniel-noboa-extraditado-alias-lobo-menor-lobos-asesinato-fernando-villavicencio-118529/"
new(id="lobo-menor",name="Ángel Esteban Aguilar Morales",alias="Lobo Menor",group_ids=["lobos"],group_key="lobos",title="Ran Los Lobos after Pipo's arrest",role="former_leader",
 status="jailed",status_date="2026-03-20",status_note="Arrested in Mexico City 2026-03-18 and sent to Ecuador; held in La Cárcel del Encuentro.",status_source=S("Primicias",LM,"2026-03-20"),
 charges=["Charged in Ecuador over the 2023 killing of Fernando Villavicencio"],known_for="Pipo's stepson; President Noboa called him the group's operational head.",sources=[S("Primicias",LM),S("El País","https://elpais.com/mexico/2026-03-19/el-mundo-criminal-de-mexico-colombia-y-ecuador-converge-en-el-asesinato-de-fernando-villavicencio.html","2026-03-19")])
for k in ("ivan-guzman","alfredo-guzman","ovidio-guzman","joaquin-guzman-lopez","el-mayo","mayito-flaco"): pass
G=[
("chapitos","Los Chapitos (Sinaloa)","single","Iván Archivaldo and Jesús Alfredo Guzmán Salazar jointly; both fugitives."),
("mayiza","La Mayiza / Los Mayos (Sinaloa)","single","Mayito Flaco, per US Treasury (Sept 2026)."),
("cjng","CJNG","contested","Leadership contested: US and Mexico name El 03/El Pelón; InSight Crime and the State Dept's OSAC say CJNG may be run by semi-autonomous regional commanders with no single head."),
("gulf","Gulf Cartel","split","Split into rival factions (DEA): Los Metros (Primito), Los Escorpiones (reportedly Escorpión 7), Los Ciclones, Los Rojos. No overall leader."),
("cdn","Cártel del Noreste","single","El Juanito, per InSight Crime and Mexican media."),
("lnfm","La Nueva Familia Michoacana","single","Hurtado Olascoaga brothers; both fugitives with US rewards."),
("unidos","Cárteles Unidos","single","El Abuelo, per HSI/State; 'El Gordo' Sierra Santana (Viagras) also a fugitive."),
("tda","Tren de Aragua","contested","Leadership contested since Niño Guerrero's reported death: Giovanny (Colombian authorities) vs Johan Petrica (InSight Crime); the network is fragmented."),
("choneros","Los Choneros","unknown","Leadership unknown: Fito extradited (2025) and successor Churrón captured (July 2026); no confirmed head reported since."),
("lobos","Los Lobos","unknown","Leadership unknown: Pipo detained in Spain and Lobo Menor jailed (March 2026). InSight lists other senior figures (Palanqueta, Capitán Pico) without naming a head."),
("clan","Clan del Golfo (EGC)","single","Chiquito Malo; extradition order reactivated July 2026."),
("eln","ELN","collective","Collective Central Command (COCE); Antonio García is top commander."),
("ms13","MS-13","unknown","Leadership unknown: historic ranfla jailed in El Salvador; NCTC says cliques and regional 'programs' operate with varying central control."),
("pcc","PCC","single","Marcola heads the Sintonia Final from prison (São Paulo police); one member, 'Maranhão', reported free."),
]
GS={"chapitos":[S("Infobae","https://www.infobae.com/mexico/2026/09/09/ivan-archivaldo-jesus-alfredo-guzman-y-mayito-flaco-siguen-profugos-que-se-sabe-de-ellos-a-2-anos-de-la-guerra-en-sinaloa/")],
"mayiza":[S("US Treasury","https://home.treasury.gov/news/press-releases/sb0636")],
"cjng":[S("InSight Crime","https://insightcrime.org/es/noticias/the-insight-take-nuevo-lider-del-cjng/"),S("El Economista (OSAC report)","https://www.eleconomista.com.mx/politica/muerte-mencho-afecto-operacion-regional-cjng-20261012-838103.html")],
"gulf":[S("DEA NDTA 2025","https://www.dea.gov/sites/default/files/2025-05/2025%20National%20Drug%20Threat%20Assessment_Web%205-12-2025.pdf")],
"cdn":[S("InSight Crime",ICN)],"lnfm":[S("Infobae","https://www.infobae.com/mexico/2026/06/19/quien-es-quien-en-la-nueva-familia-michoacana-los-cuatro-hermanos-que-dirigen-uno-de-los-carteles-mas-buscados/")],
"unidos":[S("Infobae","https://www.infobae.com/mexico/2026/09/28/la-caceria-contra-lideres-de-carteles-unidos-se-reduce-a-dos-profugos-eeuu-ofrece-15-mdd-por-el-abuelo-farias-y-el-gordo/")],
"tda":[S("CNN en Español",CNN),S("InSight Crime",IP)],"choneros":[S("Diálogo Américas","https://dialogo-americas.com/es/articles/ecuador-lleva-la-presion-contra-los-choneros-del-liderazgo-a-sus-redes-logisticas/")],
"lobos":[S("InSight Crime","https://insightcrime.org/es/noticias-crimen-organizado-ecuador/lobos/"),S("La Hora","https://www.lahora.com.ec/seguridad/los-lobos-siguen-operando-pese-a-la-captura-de-sus-cabecillas-y-el-reto-es-golpear-su-patrimonio-20260319-0043.html")],
"clan":[S("El País","https://elpais.com/america-colombia/2026-07-01/petro-reactiva-la-orden-de-extradicion-contra-alias-chiquito-malo-lider-del-clan-del-golfo.html")],
"eln":[S("Infobae","https://www.infobae.com/colombia/2026/09/28/gabino-antonio-garcia-pablo-beltran-y-otros-11-maximos-cabecillas-del-eln-fueron-condenados-a-20-anos-de-prision-por-el-reclutamiento-forzado-de-60-menores-de-edad/")],
"ms13":[S("NCTC","https://www.dni.gov/nctc/terrorist_groups/ms13.html"),S("InSight Crime","https://insightcrime.org/el-salvador-organized-crime-news/mara-salvatrucha-ms-13-profile/")],
"pcc":[S("Folha","https://www1.folha.uol.com.br/cotidiano/2026/02/novo-organograma-do-pcc-tem-14-sintonias-e-35-lideres-soltos-aponta-policia-civil-de-sp.shtml")]}
d["groups"]=[{"id":g,"name":n,"leadership":st,"leadership_note":nt,"sources":GS[g],**({"leadership_unknown":nt} if st=="unknown" else {})} for g,n,st,nt in G]
d["role_legend"]={"current_leader":"Reported to be running the group now","faction_leader":"Runs one faction of a split group","reported_successor":"Named as successor; not settled","former_leader":"Jailed, extradited, dead or cooperating"}
d["confidence_legend"]=[CO,RM,RC]
json.dump(d,open(P+"leaders.json","w"),ensure_ascii=False,indent=1)
print(len(L))
