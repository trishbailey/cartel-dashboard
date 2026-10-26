import json
P="/workspace/cartel-dashboard/data/"
NC=lambda g:"https://www.dni.gov/nctc/terrorist_groups/"+g+".html"
PC="https://www.science.org/doi/10.1126/science.adh2888"
CAR="https://caracol.com.co/2026/08/26/cerca-de-30000-integrantes-conforman-grupos-armados-y-delincuenciales-en-colombia/"
ECU="https://www.comunicacion.gob.ec/ecuador-y-ee-uu-coinciden-en-declarar-que-las-organizaciones-criminales-son-terroristas-2/"
def m(lo,hi,yr,unit,note,url,src):return {"low":lo,"high":hi,"year":yr,"unit":unit,"note":note,"source_url":url,"source_name":src}
NO=lambda why:{"no_credible_estimate":True,"note":why}
SZ={
"sinaloa":{"label":"Sinaloa Cartel (both factions)","applies_to":["chapitos","mayiza"],
 "members":[m(26000,None,2023,"members","DEA: 'more than 26,000 members, associates, facilitators and brokers' worldwide; lower bound only.","https://www.justice.gov/sites/default/files/2023-07/2023.7.12_dea_papadopoulos_sfr_for_a_house_homeland_hearing_on_protecting_the_homeland.pdf","DEA testimony"),
  m(17825,17825,2022,"members","Model-based point estimate (Prieto-Curiel et al., Science 2023) from homicide and incarceration data.",PC,"Science")],
 "revenue":[m(None,3e9,2019,"annual_revenue_usd","'Up to $3 billion' a year; dated estimate quoted by Congressional Research Service.","https://www.congress.gov/crs-product/R41576","CRS")]},
"cjng":{"label":"CJNG","members":[m(15000,20000,2026,"members","US counterterrorism center estimate.",NC("cjng"),"NCTC"),m(28764,28764,2022,"members","Model-based point estimate (Science 2023).",PC,"Science")],"revenue":[NO("No official or academic annual figure found.")]},
"gulf":{"label":"Gulf Cartel","members":[NO("NCTC: 'thousands', no number.")],"revenue":[NO("None found.")]},
"cdn":{"label":"Cártel del Noreste","members":[m(1000,None,2025,"members","'More than 1,000'; lower bound only.",NC("cdn"),"NCTC")],"revenue":[NO("None found.")]},
"lnfm":{"label":"La Nueva Familia Michoacana","members":[m(5000,5000,2026,"members","Approximate.",NC("lnfm"),"NCTC")],"revenue":[NO("None found.")]},
"unidos":{"label":"Cárteles Unidos","members":[NO("NCTC: 'thousands', no number.")],"revenue":[NO("None found.")]},
"tda":{"label":"Tren de Aragua","members":[m(2500,5000,2026,"members","US counterterrorism center range.",NC("tren_de_aragua"),"NCTC")],"revenue":[NO("Figures circulate in media but none traced to an official or academic estimate.")]},
"choneros":{"label":"Los Choneros","members":[m(12000,12000,2026,"members","Approximate.",NC("los_choneros"),"NCTC"),m(30000,30000,2024,"armed members","Ecuadorian government figure; much higher than US estimate (contested).",ECU,"Ecuador government")],"revenue":[NO("None found.")]},
"lobos":{"label":"Los Lobos","members":[m(8000,8000,2026,"members","Approximate.",NC("los_lobos"),"NCTC"),m(50000,50000,2024,"members","Ecuadorian government figure; much higher than US estimate (contested).",ECU,"Ecuador government")],
 "revenue":[m(43.2e6,43.2e6,2024,"annual_revenue_usd","PARTIAL: illegal gold mining in one area only (Ecuadorian intelligence report via Código Vidrio). Not total revenue.","https://news.mongabay.com/2024/05/ecuadors-los-lobos-narcotrafficking-gang-muscles-in-on-illegal-gold-mining/","Mongabay",)]},
"clan":{"label":"Clan del Golfo","members":[m(9915,9915,2026,"members","Defence Ministry: 9,915 total including support networks.",CAR,"Colombia MinDefensa"),m(3364,3364,2026,"armed members","Defence Ministry: armed combatants.",CAR,"Colombia MinDefensa"),m(10268,10268,2026,"members","Interior Ministry figure.","https://www.portafolio.co/economia/gobierno/grupos-armados-casi-duplicaron-sus-integrantes-durante-la-paz-total-del-gobierno-petro-segun-mininterior-502594","Colombia MinInterior")],
 "revenue":[m(4.4e9,4.4e9,2025,"annual_revenue_usd","International Crisis Group estimate.","https://www.crisisgroup.org/es/rpt/latin-america-caribbean/andes/colombia/105-unsolved-crime-total-peace-dealing-colombias-gaitanistas","Crisis Group")]},
"eln":{"label":"ELN","members":[m(6877,6877,2026,"members","Defence Ministry: total including support networks.",CAR,"Colombia MinDefensa"),m(3442,3442,2026,"armed members","Defence Ministry: armed combatants.",CAR,"Colombia MinDefensa")],
 "revenue":[m(250e9,250e9,2023,"annual_revenue_cop","COP 250,000 million a year (Colombian pesos, not converted). Not shown on the USD chart.","https://caracol.com.co/2023/11/15/eln-percibiria-250-mil-millones-al-ano-por-finanzas-criminales/","Caracol")]},
"ms13":{"label":"MS-13","members":[m(10000,10000,2018,"members","US only (CRS). NCTC says 'probably tens of thousands' worldwide, no number.","https://www.congress.gov/crs-product/R45292","CRS")],"revenue":[NO("None found.")]},
"pcc":{"label":"PCC","members":[m(40000,40000,2025,"members","São Paulo state prosecutors (Lincoln Gakiya).","https://g1.globo.com/sp/sao-paulo/noticia/2025/09/22/como-em-20-anos-o-pcc-saltou-de-faccao-com-5-mil-criminosos-para-virar-mafia-com-40-mil-membros.ghtml","MP-SP via G1")],
 "revenue":[m(2e9,None,2025,"annual_revenue_usd","'At least US$2 billion' (R$10bn+) a year; São Paulo prosecutors. Lower bound.","https://www.estadao.com.br/sao-paulo/pcc-ja-fatura-r-10-bilhoes-ao-ano-crescimento-foi-assustador-diz-promotor-em-cpi/","MP-SP via Estadão")]},
}
json.dump({"note":"Ranges as published; nothing averaged or converted. low=high means a single published figure; a null high means 'more than'.","groups":SZ},open(P+"groups_size.json","w"),ensure_ascii=False,indent=1)
LINES=[("fentanyl","Fentanyl"),("meth","Meth"),("cocaine","Cocaine"),("heroin","Heroin"),("marijuana","Marijuana"),("drugs_unspecified","Drugs (type not specified)"),("precursors","Precursor chemicals"),("migrant_smuggling","Migrant smuggling"),("human_trafficking","Human / sex trafficking"),("extortion","Extortion"),("kidnapping","Kidnapping"),("fuel_theft","Fuel theft"),("illegal_mining","Illegal mining"),("logging_fishing","Illegal logging / fishing"),("arms","Arms trafficking"),("money_laundering","Money laundering"),("legit_economies","Control of legal economies")]
U={"ndta":"https://www.dea.gov/sites/default/files/2025-05/2025%20National%20Drug%20Threat%20Assessment_Web%205-12-2025.pdf","fto":"https://www.state.gov/designation-of-international-cartels","deac":"https://www.dea.gov/cartels","t636":"https://home.treasury.gov/news/press-releases/sb0636",
"abuelo":"https://www.state.gov/juan-jose-farias-alvarez","tda":NC("tren_de_aragua"),"t2459":"https://home.treasury.gov/news/press-releases/jy2459","cho":NC("los_choneros"),"gold":"https://insightcrime.org/es/noticias/mientras-aumenta-presion-gobierno-las-pandillas-ecuatorianas-buscan-oro/",
"lobos":"https://insightcrime.org/es/noticias-crimen-organizado-ecuador/lobos/","mong":"https://news.mongabay.com/2024/05/ecuadors-los-lobos-narcotrafficking-gang-muscles-in-on-illegal-gold-mining/","icg":"https://www.crisisgroup.org/es/rpt/latin-america-caribbean/andes/colombia/105-unsolved-crime-total-peace-dealing-colombias-gaitanistas",
"sem":"https://www.semana.com/nacion/barranquilla/articulo/la-millonaria-fortuna-de-los-grupos-armados-en-colombia-semana-revela-detalles-de-los-negocios-del-eln-disidencias-y-clan-del-golfo/202608/","eln":"https://insightcrime.org/es/noticias-crimen-organizado-colombia/eln-colombia/",
"ms":NC("ms13"),"crs":"https://www.congress.gov/crs-product/R45292","pccg":"https://g1.globo.com/sp/sao-paulo/noticia/2025/09/22/como-em-20-anos-o-pcc-saltou-de-faccao-com-5-mil-criminosos-para-virar-mafia-com-40-mil-membros.ghtml","fin":"https://g1.globo.com/economia/noticia/2025/08/28/como-o-pcc-usa-fintechs-para-lavar-dinheiro.ghtml","mpsp":"https://mpsp.mp.br/w/megaoperacao-com-1-400-agentes-mira-setor-de-combustiveis"}
def row(**k):return {l:{"level":v[0],"source_url":U[v[1]]} for l,v in k.items()}
SIN=dict(fentanyl=("primary","ndta"),meth=("primary","ndta"),cocaine=("primary","ndta"),heroin=("secondary","ndta"),marijuana=("minor","ndta"),fuel_theft=("minor","ndta"))
B={"chapitos":row(**SIN),
"mayiza":row(**SIN,extortion=("secondary","t636"),kidnapping=("secondary","t636"),money_laundering=("secondary","t636")),
"cjng":row(fentanyl=("primary","ndta"),meth=("primary","ndta"),cocaine=("primary","ndta"),precursors=("secondary","ndta"),money_laundering=("secondary","ndta"),fuel_theft=("secondary","deac"),extortion=("secondary","deac"),migrant_smuggling=("secondary","deac"),illegal_mining=("minor","fto"),arms=("minor","fto")),
"gulf":row(cocaine=("primary","ndta"),fentanyl=("secondary","ndta"),meth=("secondary","ndta"),heroin=("secondary","ndta"),migrant_smuggling=("primary","ndta"),money_laundering=("secondary","ndta"),fuel_theft=("minor","ndta"),kidnapping=("secondary","fto"),extortion=("secondary","fto")),
"cdn":row(drugs_unspecified=("primary","fto"),extortion=("secondary","fto"),kidnapping=("secondary","fto"),migrant_smuggling=("secondary","fto")),
"lnfm":row(meth=("primary","ndta"),extortion=("primary","fto"),kidnapping=("secondary","fto"),fuel_theft=("minor","ndta")),
"unidos":row(meth=("primary","abuelo"),fentanyl=("secondary","abuelo"),cocaine=("secondary","abuelo"),heroin=("minor","abuelo")),
"tda":row(extortion=("primary","tda"),human_trafficking=("primary","tda"),kidnapping=("secondary","tda"),migrant_smuggling=("secondary","tda"),illegal_mining=("secondary","t2459"),cocaine=("minor","t2459"),money_laundering=("minor","t2459")),
"choneros":row(cocaine=("primary","cho"),kidnapping=("secondary","cho"),arms=("secondary","cho"),extortion=("secondary","gold"),illegal_mining=("secondary","gold")),
"lobos":row(illegal_mining=("primary","gold"),extortion=("primary","lobos"),cocaine=("primary","lobos"),kidnapping=("secondary","lobos"),arms=("minor","mong")),
"clan":row(cocaine=("primary","icg"),illegal_mining=("secondary","sem"),migrant_smuggling=("secondary","icg"),extortion=("secondary","icg"),arms=("minor","icg")),
"eln":row(cocaine=("primary","eln"),extortion=("primary","eln"),kidnapping=("secondary","eln"),illegal_mining=("secondary","sem")),
"ms13":row(extortion=("primary","ms"),drugs_unspecified=("secondary","ms"),migrant_smuggling=("minor","ms"),human_trafficking=("minor","crs"),legit_economies=("minor","ms")),
"pcc":row(cocaine=("primary","pccg"),money_laundering=("primary","fin"),legit_economies=("secondary","mpsp")),
}
json.dump({"note":"Levels (primary/secondary/minor) are an editorial reading of how prominently the cited source describes each activity. Empty = no source found, not 'not involved'.","lines":[{"id":a,"label":b} for a,b in LINES],"levels":["primary","secondary","minor"],"groups":B},open(P+"groups_business.json","w"),ensure_ascii=False,indent=1)
