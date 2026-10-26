import json
S=lambda n,u,d=None: {"name":n,"url":u,**({"date":d} if d else {})}
CM="https://commons.wikimedia.org/wiki/File:"
PD_US="Public domain (work of the US federal government)"
def ph(): return {"file":None,"placeholder":True,"image_source_url":None,"license":"n/a (neutral placeholder; no clean official or openly licensed photo found)","credit":None}
def img(f,u,lic,credit,note=None):
    d={"file":"img/leaders/"+f,"placeholder":False,"image_source_url":u,"license":lic,"credit":credit}
    if note:d["provenance_note"]=note
    return d
STATE_FTO="https://www.state.gov/inl-rewards-program-narcotics-rewards-program/narcotics-rewards-program-fto-designated-targets"
L=[
dict(id="ivan-guzman",name="Iván Archivaldo Guzmán Salazar",alias="",group_ids=["sinaloa"],faction="Los Chapitos",role="Co-leader of Los Chapitos (sons of El Chapo)",
 status="at_large",status_date="2026-09-09",status_note="Fugitive. A reported surrender negotiation (LA Times, May 2026) has not been confirmed by US or Mexican authorities.",
 status_source=S("Infobae","https://www.infobae.com/mexico/2026/09/09/ivan-archivaldo-guzman/","2026-09-09"),
 reward_usd=10000000,reward_source=S("ICE Most Wanted","https://www.ice.gov/most-wanted/guzman-salazar-ivan"),
 charges=["Charged in N.D. Illinois (warrant 2023-04-06): drug conspiracy, continuing criminal enterprise, money laundering","Sanctioned by OFAC (SDN list)"],
 known_for="Alleged to lead the Chapitos faction that US prosecutors link to industrial fentanyl production; at war with the Mayiza faction since El Mayo's July 2024 abduction to the US.",
 sources=[S("ICE Most Wanted","https://www.ice.gov/most-wanted/guzman-salazar-ivan"),S("InSight Crime: Los Chapitos","https://insightcrime.org/mexico-organized-crime-news/los-chapitos/")],
 photo=img("ivan.jpg",CM+"U.S._Department_of_State_Wanted_Poster,_Iván_Archivaldo_Guzmán_Salazar_(cropped).jpg",PD_US,"US Department of State wanted poster (via Wikimedia Commons)")),
dict(id="alfredo-guzman",name="Jesús Alfredo Guzmán Salazar",alias="",group_ids=["sinaloa"],faction="Los Chapitos",role="Co-leader of Los Chapitos",
 status="at_large",status_date="2026-09-09",status_note="DEA fugitive.",status_source=S("DEA fugitive profile","https://www.dea.gov/fugitives/jesus-alfredo-guzman-salazar"),
 reward_usd=10000000,reward_source=S("DEA fugitive profile","https://www.dea.gov/fugitives/jesus-alfredo-guzman-salazar"),
 charges=["Charged in US federal court with drug trafficking conspiracy (DEA fugitive)","Sanctioned by OFAC (SDN list)"],
 known_for="Brother of Iván Archivaldo; alleged co-leader of the Chapitos' trafficking operations.",
 sources=[S("DEA fugitive profile","https://www.dea.gov/fugitives/jesus-alfredo-guzman-salazar"),S("InSight Crime: Los Chapitos","https://insightcrime.org/mexico-organized-crime-news/los-chapitos/")],
 photo=img("jesus_alfredo.jpg",CM+"Jesus_Alfredo_Guzmán_Salazar.jpg",PD_US,"DEA (via Wikimedia Commons)")),
dict(id="ovidio-guzman",name="Ovidio Guzmán López",alias="El Ratón",group_ids=["sinaloa"],faction="Los Chapitos",role="Former Chapitos leader; cooperating with US prosecutors",
 status="extradited",status_date="2026-10-14",status_note="Extradited Sept 2023; pleaded guilty July 2025 and is cooperating. Sentencing status hearing moved to 2027-04-14.",
 status_source=S("Expansión","https://politica.expansion.mx/mexico/2026/10/14/aplazan-audiencia-sentencia-ovidio-guzman-abril-2027","2026-10-14"),
 reward_usd=None,reward_source=None,charges=["Pleaded guilty (N.D. Illinois), July 2025"],
 known_for="His 2019 capture and release in Culiacán ('Culiacanazo') and 2023 recapture became symbols of the state's struggle with the cartel.",
 sources=[S("Expansión","https://politica.expansion.mx/mexico/2026/10/14/aplazan-audiencia-sentencia-ovidio-guzman-abril-2027","2026-10-14"),S("InSight Crime: Los Chapitos","https://insightcrime.org/mexico-organized-crime-news/los-chapitos/")],
 photo=img("ovidio.jpg",CM+"Wanted_Poster,_Ovidio_Guzmán_López_(cropped).jpg",PD_US,"US government wanted poster (via Wikimedia Commons)")),
dict(id="joaquin-guzman-lopez",name="Joaquín Guzmán López",alias="",group_ids=["sinaloa"],faction="Los Chapitos",role="Former Chapitos leader",
 status="jailed",status_date="2025-12-01",status_note="In US custody since July 2024, when he flew to Texas with El Mayo, whom prosecutors say he kidnapped. Pleaded guilty 2025-12-01; sentencing hearing postponed to 2027-03-01.",
 status_source=S("US DOJ","https://www.justice.gov/opa/pr/joaquin-guzman-lopez-son-el-chapo-and-leader-sinaloa-cartel-pleads-guilty-federal-drug","2025-12-01"),
 reward_usd=None,reward_source=None,charges=["Pleaded guilty to drug trafficking charges (N.D. Illinois), 2025-12-01"],
 known_for="The July 2024 delivery of El Mayo to US agents triggered the Chapitos–Mayiza war in Sinaloa.",
 sources=[S("US DOJ","https://www.justice.gov/opa/pr/joaquin-guzman-lopez-son-el-chapo-and-leader-sinaloa-cartel-pleads-guilty-federal-drug","2025-12-01")],
 photo=img("joaquin.jpg",CM+"Wanted_Poster,_Joaquin_Guzman_Lopez_(cropped).png",PD_US,"US government wanted poster (via Wikimedia Commons)")),
dict(id="el-mayo",name="Ismael Zambada García",alias="El Mayo",group_ids=["sinaloa"],faction="Mayiza",role="Sinaloa Cartel co-founder",
 status="jailed",status_date="2026-07-20",status_note="Pleaded guilty 2025-08-25; sentenced to life in prison and $15 billion forfeiture.",
 status_source=S("US DOJ (EDNY)","https://www.justice.gov/opa/pr/co-founder-sinaloa-cartel-ismael-el-mayo-zambada-garcia-sentenced-life-prison-and-ordered","2026-07-20"),
 reward_usd=None,reward_source=None,charges=["Convicted on guilty plea (EDNY): CCE, racketeering; former US reward $15M"],
 known_for="Ran the cartel for five decades without being captured until July 2024; admitted paying politicians, police and military.",
 sources=[S("US DOJ","https://www.justice.gov/opa/pr/co-founder-sinaloa-cartel-ismael-el-mayo-zambada-garcia-sentenced-life-prison-and-ordered","2026-07-20")],
 photo=img("mayo.jpg",CM+"Mayo_Zambada_(cropped).jpg",PD_US,"DEA (via Wikimedia Commons)")),
dict(id="mayito-flaco",name="Ismael Zambada Sicairos",alias="Mayito Flaco",group_ids=["sinaloa"],faction="Mayiza (Los Mayos)",role="Leader of Los Mayos, per US Treasury",
 status="at_large",status_date="2026-09-29",status_note="Fugitive in Mexico per OFAC.",
 status_source=S("US Treasury sb0636","https://home.treasury.gov/news/press-releases/sb0636","2026-09-29"),
 reward_usd=None,reward_source=None,charges=["Indicted in S.D. California, July 2014 (drug trafficking, money laundering)","OFAC-designated 2026-09-29 (E.O. 14059, E.O. 13224)"],
 known_for="Son of El Mayo; Treasury calls him the 'undisputed head of Los Mayos', fighting the Chapitos and controlling Tijuana and Mexicali plazas through allied cells.",
 sources=[S("US Treasury sb0636","https://home.treasury.gov/news/press-releases/sb0636","2026-09-29")],
 photo=img("mayito.jpg",CM+"IsmaelZambadaS.jpg",PD_US,"DEA (via Wikimedia Commons)")),
dict(id="el-mencho",name="Nemesio Oseguera Cervantes",alias="El Mencho",group_ids=["cjng"],faction="",role="Founder and leader of CJNG",
 status="dead",status_date="2026-02-22",status_note="Killed in a Mexican military operation in Tapalpa, Jalisco, with US intelligence support.",
 status_source=S("Reuters","https://www.reuters.com/world/americas/mexican-drug-lord-el-mencho-killed-military-operation-government-source-2026-02-22/","2026-02-22"),
 reward_usd=None,reward_source=None,charges=["Was charged in US federal court (D.D.C.); former US reward $15M"],
 known_for="Built CJNG into Mexico's most expansive cartel; his death triggered nationwide roadblocks and attacks.",
 sources=[S("Reuters","https://www.reuters.com/world/americas/mexican-drug-lord-el-mencho-killed-military-operation-government-source-2026-02-22/","2026-02-22"),S("Gabinete de Seguridad (Mexico)","https://gabinetedeseguridad.gob.mx/contenido/7937/la-secretaria-de-la-defensa-nacional-informa-sobre-una-operacion-para-la-detencion-de-ruben-n-a-mencho")],
 photo=img("mencho.jpg",CM+"El_Mencho.jpg","Public domain (Commons lists DEA as source)","Wikimedia Commons, credited to DEA","Contested: Commons credits the DEA but its source link points to a news outlet; 1986 booking photo.")),
dict(id="el-pelon",name="Juan Carlos Valencia González",alias="El 03 / El Pelón",group_ids=["cjng"],faction="",role="Named by US and Mexican officials as Mencho's successor (UNCONFIRMED)",
 status="at_large",status_date="2026-09-04",status_note="Mexico's security secretary said 2026-09-04 he is the successor; InSight Crime cautions the succession is unsettled. Mexico has an extradition order.",
 status_source=S("US State Dept","https://www.state.gov/juan-carlos-valencia-gonzalez"),
 reward_usd=25000000,reward_source=S("US State Dept","https://www.state.gov/releases/office-of-the-spokesperson/2026/08/degrading-cjng-announcing-over-100-million-in-reward-offers-and-visa-restrictions","2026-08-05"),
 charges=["Charged in D.D.C. (indictment filed 2020, unsealed 2026-08-05): cocaine and meth conspiracy, firearms"],
 known_for="Stepson of El Mencho; alleged to run CJNG's armed wing. US-born dual national.",
 sources=[S("US DOJ","https://www.justice.gov/opa/pr/new-charges-and-rewards-announced-capture-andor-conviction-senior-leaders-notorious-mexican","2026-08-05"),S("US State Dept","https://www.state.gov/juan-carlos-valencia-gonzalez")],
 flags=["successor_unconfirmed"],
 photo=img("valencia.jpg",CM+"Cartel_de_búsqueda_de_Juan_Carlos_Valencia_González_(25_millones).jpg",PD_US,"US DOJ reward poster (via Wikimedia Commons), cropped")),
dict(id="r-1",name="Juan Reyes Mejía-González",alias="R-1",group_ids=["gulf"],faction="Los Rojos",role="Head of a Gulf Cartel faction (cartel is fragmented)",
 status="at_large",status_date="2026-10-25",status_note="Listed as wanted by State. The Gulf Cartel has no single leader; 2026 arrests included El Meño (Metros) and Nacho Vega (Escorpiones).",
 status_source=S("US State Dept",STATE_FTO),reward_usd=5000000,reward_source=S("US State Dept",STATE_FTO),
 charges=["Charged in D.D.C. (2008) and N.D. Texas (2006): drug trafficking"],
 known_for="Alleged long-time plaza boss in Reynosa and leader of the Los Rojos faction.",
 sources=[S("US State Dept",STATE_FTO)],photo=ph()),
dict(id="z-40",name="Miguel Ángel Treviño Morales",alias="Z-40",group_ids=["cdn"],faction="",role="Founder of Cártel del Noreste (ex-Zetas)",
 status="extradited",status_date="2026-10-21",status_note="Sent to the US Feb 2025; pleaded not guilty (D.D.C.). Government rejected a plea offer; trial proposed for 2028. Current CDN boss reported to be Juan Cisneros Treviño 'El Juanito' (InSight Crime), with no US charges found.",
 status_source=S("Infobae","https://www.infobae.com/mexico/2026/10/21/z-40/","2026-10-21"),
 reward_usd=None,reward_source=None,charges=["Charged in D.D.C.: drug trafficking, firearms; pleaded not guilty"],
 known_for="Led Los Zetas until his 2013 arrest; the group's massacres include San Fernando, 2010.",
 sources=[S("InSight Crime: Cartel del Noreste","https://insightcrime.org/mexico-organized-crime-news/cartel-del-noreste/")],photo=ph()),
dict(id="el-pez",name="Johnny Hurtado Olascoaga",alias="El Pez",group_ids=["lnfm"],faction="",role="Leader of La Nueva Familia Michoacana",
 status="at_large",status_date="2025-04-15",status_note="Wanted by State; LNFM designated FTO 2025-02-20.",
 status_source=S("US State Dept","https://www.state.gov/johnny-hurtado-olascoaga"),reward_usd=5000000,reward_source=S("US State Dept","https://www.state.gov/johnny-hurtado-olascoaga"),
 charges=["Indicted 2024-09-24 with his brother: heroin, meth, cocaine and fentanyl conspiracy","Sanctioned by OFAC"],
 known_for="LNFM is accused of extortion of producers and towns in Guerrero, Mexico state and Michoacán.",
 sources=[S("US State Dept","https://www.state.gov/johnny-hurtado-olascoaga")],
 photo=img("el_pez.jpg","https://www.state.gov/wp-content/uploads/2025/04/Johnny.png",PD_US,"US Department of State")),
dict(id="el-fresa",name="José Alfredo Hurtado Olascoaga",alias="El Fresa",group_ids=["lnfm"],faction="",role="LNFM second in command",
 status="at_large",status_date="2025-04-15",status_note="Wanted by State.",status_source=S("US State Dept",STATE_FTO),
 reward_usd=3000000,reward_source=S("US State Dept",STATE_FTO),charges=["Indicted 2024-09-24 (same case as El Pez)","Sanctioned by OFAC"],
 known_for="Brother of El Pez; State describes him as second in command.",
 sources=[S("US State Dept",STATE_FTO)],photo=img("el_fresa.jpg","https://www.state.gov/wp-content/uploads/2025/04/Jose.png",PD_US,"US Department of State")),
dict(id="el-abuelo",name="Juan José Farías Álvarez",alias="El Abuelo",group_ids=["lnfm"],faction="Cárteles Unidos",role="Leader of Cárteles Unidos",
 status="at_large",status_date="2025-08-14",status_note="Wanted by State; Cárteles Unidos designated FTO 2025-02-20.",
 status_source=S("US State Dept","https://www.state.gov/juan-jose-farias-alvarez"),reward_usd=10000000,reward_source=S("US State Dept","https://www.state.gov/juan-jose-farias-alvarez"),
 charges=["D.D.C. indictment (Jan 2024, unsealed July 2025)","Sanctioned by OFAC"],
 known_for="Emerged from Tepalcatepec 'self-defense' groups in Michoacán; Cárteles Unidos is accused of fighting CJNG with landmines and drones.",
 sources=[S("US State Dept","https://www.state.gov/juan-jose-farias-alvarez")],
 photo=img("farias.jpg","https://www.state.gov/wp-content/uploads/2025/08/Abuelo-Photo-002.jpg",PD_US,"US Department of State")),
dict(id="nino-guerrero",name="Héctor Rusthenford Guerrero Flores",alias="Niño Guerrero",group_ids=["tda"],faction="",role="Leader of Tren de Aragua",
 status="reported_dead",status_date="2026-06-12",status_note="US and Venezuela said he was killed in a joint operation in Bolívar state; no independent forensic confirmation released.",
 status_source=S("BBC","https://www.bbc.com/news/articles/cp36z37knlko","2026-06-12"),
 reward_usd=None,reward_source=None,charges=["Indicted in the US; was under a $5M State reward","OFAC SDN"],
 known_for="Ran the gang from Tocorón prison until escaping a 2023 raid; TdA expanded across South America and into the US.",
 sources=[S("BBC","https://www.bbc.com/news/articles/cp36z37knlko","2026-06-12"),S("RNV (Venezuela state media)","https://rnv.gob.ve/fuerzas-de-seguridad-desarticulan-estructuras-criminales-en-bolivar-y-reportan-deceso-de-alias-nino-guerrero/"),S("InSight Crime","https://insightcrime.org/news/tren-de-aragua-leader-nino-guerrero-killed-in-venezuela-says-trump/")],
 photo=img("nino_guerrero.jpg",CM+"Hectorflores122325.jpg",PD_US,"ICE Most Wanted (via Wikimedia Commons); low resolution")),
dict(id="fito",name="José Adolfo Macías Villamar",alias="Fito",group_ids=["choneros"],faction="",role="Leader of Los Choneros",
 status="extradited",status_date="2025-07-21",status_note="Recaptured June 2025 and extradited to the US; faces 7 charges in EDNY and is reported to be negotiating a plea.",
 status_source=S("DEA","https://www.dea.gov/press-releases/2025/07/21/ecuadorian-gang-leader-extradited-united-states","2025-07-21"),
 reward_usd=None,reward_source=None,charges=["EDNY indictment: cocaine trafficking, firearms (7 counts)"],
 known_for="His Jan 2024 prison escape set off Ecuador's declaration of 'internal armed conflict'.",
 sources=[S("DEA","https://www.dea.gov/press-releases/2025/07/21/ecuadorian-gang-leader-extradited-united-states","2025-07-21")],photo=ph()),
dict(id="pipo",name="Wilmer Geovanny Chavarría Barre",alias="Pipo",group_ids=["lobos"],faction="",role="Leader of Los Lobos",
 status="jailed",status_date="2026-07-01",status_note="Arrested in Málaga, Spain 2025-11-16 after faking his death; Spain's Audiencia Nacional approved transfer to Ecuador (July 2026), under appeal. US has also charged him.",
 status_source=S("BBC Mundo","https://www.bbc.com/mundo/articles/pipo-chavarria"),
 reward_usd=None,reward_source=None,charges=["OFAC-sanctioned 2024","US federal charges (formalized after arrest)"],
 known_for="Los Lobos are linked to illegal gold mining and cocaine routes for Mexican cartels.",
 sources=[S("BBC Mundo","https://www.bbc.com/mundo/articles/pipo-chavarria")],photo=ph()),
dict(id="chiquito-malo",name="Jobanis de Jesús Ávila Villadiego",alias="Chiquito Malo",group_ids=["clan"],faction="",role="Leader of Clan del Golfo (EGC)",
 status="at_large",status_date="2026-09-01",status_note="Colombian arrest warrant reactivated and extradition process reopened; Colombian bounty 5,000M COP.",
 status_source=S("El Tiempo","https://www.eltiempo.com/justicia/conflicto-y-narcotrafico/chiquito-malo"),reward_usd=None,reward_source=None,
 charges=["Colombian arrest warrant; extradition request reopened"],known_for="Succeeded Otoniel in 2021; the group is Colombia's largest armed trafficking organization.",
 sources=[S("El Tiempo","https://www.eltiempo.com/justicia/conflicto-y-narcotrafico/chiquito-malo")],photo=ph()),
dict(id="antonio-garcia",name="Eliécer Erlington Chamorro Acosta",alias="Antonio García",group_ids=["eln"],faction="",role="Top commander of the ELN",
 status="at_large",status_date="2026-10-01",status_note="At large; Colombian bounty 4,378M COP.",status_source=S("El Tiempo","https://www.eltiempo.com/justicia/conflicto-y-narcotrafico/antonio-garcia-eln"),
 reward_usd=None,reward_source=None,charges=["Colombian arrest warrants"],known_for="Led the ELN through failed peace talks; the group operates on both sides of the Colombia–Venezuela border.",
 sources=[S("El Tiempo","https://www.eltiempo.com/justicia/conflicto-y-narcotrafico/antonio-garcia-eln")],
 photo=img("antonio_garcia.jpg",CM+"GarciaELN.jpg","CC BY 3.0","Resumen Latinoamericano (YouTube) via Wikimedia Commons, cropped")),
dict(id="diablito",name="Borromeo Enrique Henríquez Solórzano",alias="Diablito de Hollywood",group_ids=["ms13"],faction="Ranfla Nacional",role="Described by DOJ as MS-13's most powerful member",
 status="jailed",status_date="2026-07-15",status_note="Jailed in El Salvador; mass trial of 485 MS-13 leaders concluded July 2026, verdict pending.",
 status_source=S("LA Times","https://www.latimes.com/world-nation/story/2026-07-15/el-salvador-ms13-mass-trial","2026-07-15"),
 reward_usd=None,reward_source=None,charges=["Charged in US (E.D.N.Y., 2021 'Ranfla' indictment): terrorism conspiracy, narco-terrorism"],
 known_for="Alleged member of MS-13's governing council that directed violence across Central America and the US.",
 sources=[S("US DOJ","https://www.justice.gov/es/espanol/pr/l-deres-de-alto-rango-de-la-ms-13-son-acusados-por-delitos-de-terrorismo-en-los-estados"),S("ICE","https://www.ice.gov/news/releases/ms-13s-highest-ranking-leaders-charged-terrorism-offenses-us")],photo=ph()),
dict(id="marcola",name="Marcos Willians Herbas Camacho",alias="Marcola",group_ids=["pcc"],faction="",role="Leader of PCC",
 status="jailed",status_date="2026-05-21",status_note="Long imprisoned in Brazil's federal system; targeted in a May 2026 money-laundering operation.",
 status_source=S("G1","https://g1.globo.com/sp/sao-paulo/noticia/2026/05/21/operacao-pcc-marcola.ghtml","2026-05-21"),
 reward_usd=None,reward_source=None,charges=["Convicted in Brazil (multiple sentences)","PCC designated by the US as a terrorist organization (2026); OFAC sanctioned a PCC laundering network 2026-07-01"],
 known_for="Built PCC into Brazil's largest criminal organization with cocaine export routes via Paraguay and Bolivia.",
 sources=[S("G1","https://g1.globo.com/sp/sao-paulo/noticia/2026/05/21/operacao-pcc-marcola.ghtml","2026-05-21")],
 photo=img("marcola.jpg",CM+"18-12-2018_Marcos_Willians_Herbas_Camacho.jpg","CC BY 3.0","SBT (YouTube) via Wikimedia Commons","Contested: a separate Commons file claims public domain from police; we use the CC BY 3.0 video still instead.")),
]
IB="https://www.infobae.com/mexico/2026/09/09/ivan-archivaldo-jesus-alfredo-guzman-y-mayito-flaco-siguen-profugos-que-se-sabe-de-ellos-a-2-anos-de-la-guerra-en-sinaloa/"
by={x["id"]:x for x in L}
for k in ("ivan-guzman","alfredo-guzman","ovidio-guzman","joaquin-guzman-lopez"): by[k]["group_ids"]=["sinaloa","chapitos"]
for k in ("el-mayo","mayito-flaco"): by[k]["group_ids"]=["sinaloa","mayiza"]
by["el-abuelo"]["group_ids"]=["unidos"]
for k in ("ivan-guzman","alfredo-guzman"):
    by[k]["sources"]=[s for s in by[k]["sources"] if "insightcrime" not in s["url"]]+[S("Infobae",IB,"2026-09-09")]
by["ivan-guzman"]["status_source"]=S("Infobae",IB,"2026-09-09")
by["alfredo-guzman"]["status_source"]=S("Infobae",IB,"2026-09-09")
by["mayito-flaco"]["sources"].append(S("Infobae",IB,"2026-09-09"))
o=by["ovidio-guzman"];o["sources"]=[o["sources"][0],S("Infobae","https://www.infobae.com/mexico/2026/09/16/a-tres-anos-de-su-extradicion-a-estados-unidos-ovidio-guzman-lopez-no-esta-dentro-de-una-prision-ni-se-conoce-su-paradero/","2026-09-16")]
o["status_note"]+=" Infobae reports he is not held in a listed federal prison."
by["joaquin-guzman-lopez"]["status_source"]["date"]="2025-12-02"
z=by["z-40"];ZU="https://www.infobae.com/mexico/2026/10/21/de-los-zetas-a-los-chapitos-fechas-de-las-proximas-audiencias-de-los-narcos-mexicanos-en-eeuu/"
z["status_source"]=S("Infobae",ZU,"2026-10-21");z["status_note"]="Sent to the US Feb 2025; pleaded not guilty (D.D.C.). Prosecutors ruled out a plea deal; jury trial tentatively 2028-05-19; review hearing 2026-10-30. Current CDN boss is reported by media to be Juan Cisneros Treviño 'El Juanito'; no US charges found for him."
z["sources"]=[S("Infobae",ZU,"2026-10-21"),S("Infobae","https://www.infobae.com/mexico/2026/07/10/fiscalia-de-eeuu-descarta-acuerdo-con-el-z-40-y-el-z-42-los-llevara-a-juicio/","2026-07-10")]
f=by["fito"];FU="https://www.dea.gov/press-releases/2025/07/21/jose-adolfo-fito-macias-villamar-faces-international-drug-and-weapon";f["status_source"]=S("DEA",FU,"2025-07-21");f["sources"]=[S("DEA",FU,"2025-07-21"),S("AP","https://apnews.com/article/ecuador-united-states-extradition-drug-trafficker-e1743a12c2a54117cc12e0de9576774c")]
f["status_note"]="Recaptured 2025-06-25 and extradited to the US; arraigned in Brooklyn on a seven-count superseding indictment."
p=by["pipo"];PU="https://www.eluniverso.com/noticias/politica/espana-aprobo-la-extradicion-a-ecuador-de-alias-pipo-cabecilla-de-los-lobos-nota/"
p.update(status_date="2026-07-31",status_note="Arrested in Málaga, Spain 2025-11-16 after faking his death. Spain's Audiencia Nacional approved extradition to Ecuador (late July 2026) to serve a 16-year homicide sentence and rejected a US extradition request.",
 status_source=S("El Universo",PU),charges=["OFAC-sanctioned (2024)","Convicted in Ecuador (16 years, homicide); US extradition request rejected by Spain"],
 sources=[S("El Universo",PU),S("EFE","https://efe.com/espana/rechazan-entrega-eeuu-presunto-lider-banda-ecuatoriana-lobos/"),S("Heraldo","https://www.heraldo.es/noticias/aragon/2026/07/31/estados-unidos-no-logra-extradicion-preso-mas-peligroso-vigilado-carcel-zaragoza-2041245.html","2026-07-31")])
c=by["chiquito-malo"];CU="https://elpais.com/america-colombia/2026-07-01/petro-reactiva-la-orden-de-extradicion-contra-alias-chiquito-malo-lider-del-clan-del-golfo.html"
c.update(status_date="2026-07-06",status_note="At large. President Petro lifted the suspension of his extradition order on 2026-07-01 (formalized by Resolution 261, 2026-07-06); if captured he is to be sent to the US.",status_source=S("El País",CU,"2026-07-01"),
 charges=["US drug trafficking charges; Colombian extradition order active since 2026-07-01"],sources=[S("El País",CU,"2026-07-01"),S("El Heraldo (CO)","https://www.elheraldo.co/colombia/2026/07/06/presidente-petro-firmo-la-orden-de-extradicion-de-chiquito-malo-maximo-cabecilla-del-clan-del-golfo/","2026-07-06")])
a=by["antonio-garcia"];AU="https://www.infobae.com/colombia/2026/03/02/ofrecen-millonarias-recompensas-por-responsables-de-homicidios-de-lideres-sociales-en-arauca-antonio-garcia-encabeza-la-lista/"
a.update(status_date="2026-03-02",status_note="At large. Colombia's Defense Ministry offers up to about 5,385 million pesos.",status_source=S("Infobae",AU,"2026-03-02"),sources=[S("Infobae",AU,"2026-03-02"),S("El Tiempo","https://www.eltiempo.com/justicia/conflicto-y-narcotrafico/ivan-mordisco-y-antonio-garcia-encabezan-el-listado-de-los-mas-buscados-ofrecen-hasta-5-300-millones-por-ellos-3533578")])
d=by["diablito"];DU="https://apnews.com/article/el-salvador-gang-trial-salvatrucha-ms13-bukele-26a534768c5a624e83500bd764bec3fb"
d.update(status_note="Jailed in El Salvador; the mass trial of 485 alleged MS-13 leaders ended July 2026; the verdict set for Aug 31 was postponed and none is reported yet.",status_source=S("AP",DU,"2026-07"),status_date="2026-08-31")
d["sources"].append(S("AP",DU))
m=by["marcola"];MU="https://g1.globo.com/sp/sao-paulo/noticia/2026/05/21/operacao-prende-influenciadora-deolane-bezerra-e-mira-familia-de-marcola-por-lavagem-de-dinheiro-do-pcc.ghtml"
m.update(status_date="2026-06-16",status_note="Long imprisoned in Brazil's federal system. Made a defendant (réu) on 2026-06-16 for money laundering in Operation Vérnix; not a conviction.",status_source=S("G1",MU,"2026-05-21"),
 sources=[S("G1",MU,"2026-05-21"),S("G1","https://g1.globo.com/sp/presidente-prudente-e-regiao/noticia/2026/06/21/o-que-aconteceu-com-deolane-em-um-mes-veja-os-desdobramentos-que-levaram-a-influenciadora-a-virar-re-por-esquema-ligado-ao-pcc-em-sp.ghtml","2026-06-21")])
by["el-pelon"]["status_source"]=S("US State Dept","https://www.state.gov/juan-carlos-valencia-gonzalez")

# ---------------- CAPTURE ----------------
C=[]
def case(country,person,office,level,group_ids,group_text,status,date,note,sources,in_office=None):
    C.append(dict(id=f"{country.lower()}-{len(C)+1:03d}",country=country,person=person,office=office,level=level,group_ids=group_ids,group_link=group_text,status=status,date=date,note=note,sources=sources))
RM=[S("DEA","https://www.dea.gov/press-releases/2026/04/29/governor-sinaloa-and-nine-current-and-former-mexican-officials-face-drug","2026-04-29"),S("Reuters","https://www.reuters.com/world/americas/us-charges-governor-mexicos-sinaloa-state-ties-cartel-2026-04-29/","2026-04-29")]
case("MEX","Rubén Rocha Moya","Governor of Sinaloa","state",["sinaloa"],"Sinaloa Cartel (Chapitos), alleged","charged","2026-04-29","Charged in SDNY. Denies the charges; Mexico says the US has not provided evidence to justify arrest. On second indefinite leave since 2026-08-23.",RM+[S("El País","https://elpais.com/mexico/2026-08-23/el-congreso-de-sinaloa-acepta-la-segunda-renuncia-de-rocha-al-gobierno-de-sinaloa.html","2026-08-23"),S("La Jornada","https://www.jornada.com.mx/noticia/2026/09/02/politica/sheinbaum-asegura-que-eu-sigue-sin-presentar-pruebas-adicionales-para-detener-a-rocha-y-a-funcionarios-senalados","2026-09-02")])
for n,o,l in [("Enrique Inzunza Cázarez","Senator (Sinaloa)","national"),("Enrique Díaz Vega","Former Sinaloa finance secretary","state"),("Dámaso Castro Zaavedra","Sinaloa deputy attorney general","state"),("Marco Antonio Almanza Avilés","Former head of Sinaloa investigative police","state"),("Alberto Jorge Contreras Núñez","Former head of Sinaloa investigative police","state"),("Gerardo Mérida Sánchez","Former Sinaloa public security secretary","state"),("José Antonio Dionisio Hipólito","Former deputy director, Sinaloa state police","state"),("Juan de Dios Gámez Mendívil","Mayor of Culiacán","municipal"),("Juan Valenzuela Millán","Culiacán police commander","municipal")]:
    case("MEX",n,o,l,["sinaloa"],"Sinaloa Cartel (Chapitos), alleged","charged","2026-04-29","Co-defendant in the SDNY Rocha Moya indictment. Mexico disputes the evidence.",RM)
case("MEX","Genaro García Luna","Secretary of Public Security (federal)","national",["sinaloa"],"Sinaloa Cartel bribes, per jury verdict","convicted","2023-02-21","Convicted by EDNY jury Feb 2023; sentenced to 38+ years (Oct 2024). Appeal argument scheduled for November 2026.",[S("Milenio","https://www.milenio.com/policia/narcotrafico/tribunal-de-nueva-york-fija-audiencia-para-apelacion-de-garcia-luna")])
case("MEX","Gen. Salvador Cienfuegos Zepeda","Secretary of National Defense","national",[],"H-2 cartel (Beltrán Leyva offshoot), alleged","dropped","2020-11-18","Arrested and charged in EDNY Oct 2020; US moved to dismiss for foreign-policy reasons and the judge dismissed on 2020-11-18. Mexico later closed its own probe.",[S("EDNY dismissal order (InSight Crime copy)","https://insightcrime.org/wp-content/uploads/2020/11/20-11-18-Cienfuegos-Dismissal-Order.pdf","2020-11-18")])
case("MEX","Tomás Yarrington Ruvalcaba","Governor of Tamaulipas","state",["gulf"],"Bribes linked to Gulf Cartel / Zetas era","convicted","2023-03-15","Pleaded guilty to money laundering of bribes; sentenced to 9 years.",[S("DEA","https://www.dea.gov/press-releases/2023/03/15/former-mexican-governor-and-presidential-candidate-sentenced-money","2023-03-15")])
case("MEX","Mario Villanueva Madrid","Governor of Quintana Roo","state",["juarez"],"Juárez Cartel bribes","convicted","2013-06-28","Sentenced in SDNY to 131 months for laundering Juárez Cartel bribes.",[S("DEA","https://www.dea.gov/press-releases/2013/06/28/former-governor-mexican-state-sentenced-manhattan-federal-court-131","2013-06-28")])
case("MEX","Édgar Veytia","Attorney General of Nayarit","state",[],"H-2 cartel","convicted","2019-09-26","Pleaded guilty; sentenced in EDNY to 20 years.",[S("US DOJ (EDNY)","https://www.justice.gov/usao-edny/pr/former-mexican-state-attorney-general-sentenced-20-years-prison-participation","2019-09-26")])
case("MEX","Hernán Bermúdez Requena","Tabasco public security secretary","state",[],"Alleged leader of La Barredora","charged","2026-10-22","In custody in Mexico (El Altiplano); Tabasco prosecutors formally accused him of forced disappearance on 2026-10-22, alongside kidnapping and extortion charges.",[S("El Financiero","https://www.elfinanciero.com.mx/estados/2026/10/22/hernan-bermudez-requena-exlider-de-la-barredora-enfrenta-acusacion-por-desaparicion-forzada/","2026-10-22")])
T636=[S("US Treasury sb0636","https://home.treasury.gov/news/press-releases/sb0636","2026-09-29")]
case("MEX","Pedro Ariel Mendívil García","Former Mexicali public security director","municipal",["sinaloa"],"Los Rusos (Sinaloa Cartel, Los Mayos)","sanctioned","2026-09-29","OFAC says he took bribes in exchange for cartel control of Mexicali municipal police.",T636)
case("MEX","Rafael Buenrostro Martín","Former customs official (Chihuahua); legislative adviser, Baja California","state",["sinaloa"],"Sinaloa Cartel (Rivera Zazueta network)","sanctioned","2026-09-29","OFAC says he provided political favors for bribes.",T636)
case("MEX","Carlos Alberto Torres Torres","Political operator; ex-husband of the Baja California governor (not an office holder)","state",["sinaloa"],"Los Rusos (Sinaloa Cartel), alleged","sanctioned","2026-09-29","OFAC alleges he protected the cartel in Baja California; US visa revoked May 2025.",T636)
case("HND","Juan Orlando Hernández","President of Honduras (2014–2022)","national",["sinaloa"],"Cocaine traffickers incl. Sinaloa Cartel, per trial evidence","pardoned","2025-12-01","Convicted March 2024 in SDNY, sentenced to 45 years; granted a full pardon by President Trump on 2025-12-01. Honduras' AG then issued an arrest warrant.",[S("CRS IN12621","https://www.congress.gov/crs-product/IN12621"),S("Reuters","https://www.reuters.com/world/americas/former-honduran-president-released-us-prison-after-trump-pardon-2025-12-02/","2025-12-02"),S("Reuters","https://www.reuters.com/world/americas/honduras-ag-issues-international-arrest-warrant-pardoned-ex-president-hernandez-2025-12-08/","2025-12-08")])
case("HND","Juan Antonio 'Tony' Hernández","Member of Congress","national",["sinaloa"],"Cocaine trafficking (incl. bribes from El Chapo, per prosecutors)","convicted","2021-03-30","Convicted 2019; sentenced to life in SDNY.",[S("DEA","https://www.dea.gov/press-releases/2021/03/30/former-honduran-congressman-tony-hernandez-sentenced-distributing-tons","2021-03-30")])
case("HND","Juan Carlos 'El Tigre' Bonilla","Director of the National Police","national",[],"Cocaine trafficking network tied to JOH case","convicted","2024-08-01","Pleaded guilty; sentenced to 19 years in the US.",[S("AP","https://apnews.com/article/honduras-national-police-valladares-drug-trafficking-1cb7299013ad5d9aab81a4fcd7ebe54b","2024-08-01")])
MD=[S("US DOJ","https://www.justice.gov/opa/pr/nicolas-maduro-moros-and-cilia-adela-flores-de-maduro-charged-torture","2026-10-08"),S("AP","https://apnews.com/article/maduro-venezuela-criminal-case-da82df35aab0f02e344d1c3de0ed31d7")]
case("VEN","Nicolás Maduro Moros","President of Venezuela (until Jan 2026)","national",["soles","eln","exfarc","tda"],"Cartel de los Soles; FARC, per indictment","charged","2026-10-08","In US custody; narco-terrorism, cocaine and weapons charges, plus a torture count added 2026-10-08. Pleaded not guilty.",MD)
case("VEN","Cilia Flores de Maduro","First Lady; former National Assembly president","national",["soles"],"Cartel de los Soles, per indictment","charged","2026-10-08","Co-defendant with Maduro; pleaded not guilty.",MD)
case("VEN","Diosdado Cabello Rondón","Senior PSUV leader and minister","national",["soles"],"Cartel de los Soles, per US charges","charged","2020-03-26","Charged in SDNY in 2020; State reward raised to $25M on 2025-01-10.",[S("US State Dept","https://www.state.gov/diosdado-cabello-rondon")])
case("VEN","Hugo Carvajal Barrios","Director of military intelligence","national",["soles","exfarc"],"FARC cocaine trafficking","convicted","2025-06-25","Pleaded guilty in SDNY to narco-terrorism and drug charges; awaiting sentencing.",[S("Reuters","https://www.reuters.com/legal/litigation/venezuelas-ex-spymaster-pleads-guilty-us-drug-trafficking-charges-2025-06-25/","2025-06-25")])
case("VEN","Cartel de los Soles (state-linked network)","Network the US says is led by senior officials","national",["soles"],"US terrorist designation","sanctioned","2025-11-24","Designated a Foreign Terrorist Organization by the US. Venezuela rejects the existence of the group. Not an individual case.",[S("US State Dept (Venezuelan targets)","https://www.state.gov/wanted-narcotics-reward-program-venezuelan-targets")])
case("ECU","Wilman Terán","President of the Judicature Council","national",["choneros"],"Leandro Norero trafficking network (Caso Metástasis)","convicted","2024-11-25","Sentenced to 9 years 4 months for organized crime; 20 of 21 defendants convicted; written ruling Feb 2025; appeals filed.",[S("Fiscalía de Ecuador","https://www.fiscalia.gob.ec/caso-metastasis-fiscalia-obtiene-sentencia-contra-20-procesados-por-delincuencia-organizada/"),S("Corte Nacional de Justicia","https://www.cortenacional.gob.ec/cnj/index.php/noticias-2024/214-noviembre-2024/551-tribunal-de-la-sala-penal-de-la-cnj-declaro-culpables-a-20-de-los-21-procesados-en-el-caso-metastasis")])
PG=[S("Corte Nacional de Justicia","https://www.cortenacional.gob.ec/cnj/index.php/noticias-2025/204-marzo-2025/619-tribunal-de-la-sala-penal-de-la-cnj-declaro-culpables-a-10-de-los-13-procesados-en-el-caso-purga"),S("Primicias","https://www.primicias.ec/politica/caso-purga-corrupcion-judicial-guayas-sentencia-muentes-gallardo-marfetan-prision-91001/")]
case("ECU","Pablo Muentes","Former National Assembly member","national",[],"Organized-crime network in Guayas courts (Caso Purga)","convicted","2025-03-03","Sentenced to 13 years 4 months for organized crime.",PG)
case("ECU","Fabiola Gallardo","Former president, Guayas Provincial Court","state",[],"Organized-crime network in Guayas courts (Caso Purga)","convicted","2025-03-03","Sentenced to 13 years 4 months for organized crime.",PG)
case("ECU","Fausto Alarcón, Andrea Patiño, Saúl Mero","Defendants in Caso Purga","state",[],"Caso Purga","acquitted","2025-03-03","Court upheld their innocence and ordered immediate release.",PG)
case("GTM","Mauricio López Bonilla","Minister of the Interior","national",[],"Los Zetas and other traffickers, alleged by US","charged","2017-08-30","Charged in the US; Guatemala authorized extradition in 2017 conditioned on local cases; no completed extradition found.",[S("Prensa Libre","https://www.prensalibre.com/guatemala/justicia/guatemala-autoriza-extradicion-de-mauricio-lopez-bonilla-hacia-ee-uu/"),S("AP","https://apnews.com/general-news-dc96b0ddde49423b8fa14f08a17220d2")])
J0519=[S("US Treasury jy0519","https://home.treasury.gov/news/press-releases/jy0519","2021-12-08")]
case("SLV","Osiris Luna Meza","Vice Minister of Justice; prisons director","national",["ms13","b18"],"MS-13 / Barrio 18 truce talks, per US Treasury","sanctioned","2021-12-08","Treasury says he organized secret meetings with jailed gang leaders. The Bukele government denies any pact.",J0519)
case("SLV","Carlos Marroquín Chica","Head of the Reconstruction of the Social Fabric unit","national",["ms13","b18"],"MS-13 / Barrio 18 truce talks, per US Treasury","sanctioned","2021-12-08","Same Treasury action; the government denies.",J0519)
FN=[S("Fiscalía General de El Salvador","https://www.fiscalia.gob.sv/expresidente-funes-y-exministro-munguia-payes-condenados-a-14-y-18-anos-de-carcel-por-tregua/"),S("AP","https://apnews.com/article/513f06d36e9179a17e58c0aa6ec72806")]
case("SLV","Mauricio Funes","President of El Salvador (2009–2014)","national",["ms13","b18"],"2012 gang truce","convicted","2023-05-29","Convicted in absentia (lives in Nicaragua); 14 years for illicit association and breach of duty.",FN)
case("SLV","David Munguía Payés","Minister of Justice and Security","national",["ms13","b18"],"2012 gang truce","convicted","2023-05-29","Sentenced to 18 years.",FN)
case("HTI","Michel Martelly","President of Haiti (2011–2016)","national",["haiti"],"Cocaine trafficking; sponsoring gangs, per US Treasury","sanctioned","2024-08-20","Treasury designation; Martelly denies.",[S("US Treasury jy2542","https://home.treasury.gov/news/press-releases/jy2542","2024-08-20")])
J1080=[S("US Treasury jy1080","https://home.treasury.gov/news/press-releases/jy1080","2022-11-04")]
case("HTI","Joseph Lambert","President of the Senate","national",["haiti"],"Cocaine trafficking, per US Treasury","sanctioned","2022-11-04","Treasury designation.",J1080)
case("HTI","Youri Latortue","Former senator","national",["haiti"],"Cocaine trafficking, per US Treasury","sanctioned","2022-11-04","Treasury designation.",J1080)
J1137=[S("US Treasury jy1137","https://home.treasury.gov/news/press-releases/jy1137","2022-12-02")]
case("HTI","Rony Celestin","Senator","national",["haiti"],"Drug trafficking, per US Treasury","sanctioned","2022-12-02","Treasury designation.",J1137)
case("HTI","Richard Fourcand","Senator","national",["haiti"],"Drug trafficking, per US Treasury","sanctioned","2022-12-02","Treasury designation.",J1137)
case("PRY","Erico Galeano","Senator","national",[],"A Ultranza Py cocaine-laundering network","convicted","2026-03-04","Sentenced to 13 years for money laundering and criminal association; upheld on appeal May 2026.",[S("ABC Color","https://www.abc.com.py/nacionales/2026/03/04/erico-galeano-estara-13-anos-en-la-carcel-por-nexos-con-esquema-narco-de-a-ultranza/","2026-03-04"),S("El Nacional","https://elnacional.com.py/politica/confirman-condena-13-anos-erico-galeano-caso-derivado-ultranza-n105301")])
case("PRY","Horacio Cartes","President of Paraguay (2013–2018)","national",[],"Corruption (US designation did not cite a cartel)","delisted","2025-10-06","Sanctioned by OFAC in 2023 for corruption; removed from the SDN list on 2025-10-06.",[S("OFAC","https://ofac.treasury.gov/recent-actions/20251006","2025-10-06")])
case("BOL","Maximiliano Dávila Pérez","Director of the anti-narcotics force (FELCN)","national",[],"Cocaine trafficking","convicted","2026-03-19","Convicted in SDNY; sentenced to 25 years on 2026-03-19.",[S("AP","https://apnews.com/article/bolivia-eeuu-narcotrafico-davila-condena-ab7eeee1c76a1a50ea013b89623fed77"),S("La Razón","https://larazon.bo/nacional/2026/03/20/condenan-a-maximiliano-davila-a-25-anos-de-carcel-en-estados-unidos/","2026-03-20")])
NAMES={"MEX":"Mexico","HND":"Honduras","VEN":"Venezuela","ECU":"Ecuador","GTM":"Guatemala","SLV":"El Salvador","HTI":"Haiti","PRY":"Paraguay","BOL":"Bolivia"}
summ={}
for c_ in C:
    s=summ.setdefault(c_["country"],{"country":c_["country"],"name":NAMES[c_["country"]],"total":0,"by_level":{},"by_status":{}})
    s["total"]+=1;s["by_level"][c_["level"]]=s["by_level"].get(c_["level"],0)+1;s["by_status"][c_["status"]]=s["by_status"].get(c_["status"],0)+1
cap={"title":"State capture and corruption: documented cases","as_of":"2026-10-25",
 "method":"Only documented cases: convictions, indictments or formal charges, US sanctions or designations, plus acquittals, dismissals, pardons and delistings. Allegations are not findings of guilt. The dashboard counts cases; it does not label any government as compromised. Not exhaustive: Colombia, Peru, Brazil and others are not yet covered.",
 "status_legend":{"alleged":"Named in official reports or testimony only","charged":"Indicted or formally accused; presumed innocent","sanctioned":"US Treasury/State designation (administrative, not a conviction)","convicted":"Found guilty or pleaded guilty","acquitted":"Found not guilty","dropped":"Charges dismissed","pardoned":"Convicted, then pardoned","delisted":"Sanction lifted"},
 "countries":sorted(summ.values(),key=lambda x:-x["total"]),"cases":C}
lead={"title":"Leaders of the main armed groups","as_of":"2026-10-25","method":"Charges are allegations unless the person was convicted or pleaded guilty. Photos are only US government (public domain) or openly licensed images, stored in this repo; others show a neutral placeholder.","leaders":L}
json.dump(lead,open("/workspace/cartel-dashboard/data/leaders.json","w"),ensure_ascii=False,indent=1)
json.dump(cap,open("/workspace/cartel-dashboard/data/capture.json","w"),ensure_ascii=False,indent=1)
print(len(L),len(C),[(s["country"],s["total"]) for s in cap["countries"]])
