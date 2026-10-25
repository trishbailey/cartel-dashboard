const COL={precursors:"#c8a24a",cocaine:"#e6e9ef","fentanyl / methamphetamine":"#ff6b6b",migrants:"#6aa684",firearms:"#b39ddb",cash:"#5b8fd1"};
const KCOL={rivalry:"#c0504d",alliance:"#6aa684",faction:"#9aa6b8","alleged link":"#c8a24a",service:"#5b8fd1"};
const LV={dominant:.95,significant:.75,present:.35};
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const $=id=>document.getElementById(id);
let SRC={};
const cite=ids=>`<div class="cite">Sources: ${(ids||[]).map(i=>{const s=SRC[i];return s?`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.publisher)}: ${esc(s.title)}</a> (${esc(s.date)})`:esc(i)}).join("; ")}</div>`;
const srcLink=ids=>ids.map(i=>SRC[i]?`<a href="${esc(SRC[i].url)}" target="_blank" rel="noopener">${esc(SRC[i].publisher)}</a>`:esc(i)).join(", ");
const links=ls=>`<div class="cite">Sources: ${ls.map(l=>`<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.source)}: ${esc(l.title)}</a>`).join("; ")}</div>`;
const first=s=>{s=String(s||"");const m=s.match(/^.*?[.!?](\s|$)/);return m?m[0]:s};
function drawer(html){$("dbody").innerHTML=html;$("drawer").classList.add("on")}
$("dclose").onclick=()=>$("drawer").classList.remove("on");
document.addEventListener("keydown",e=>{if(e.key==="Escape")$("drawer").classList.remove("on")});
const J=p=>fetch(p).then(r=>{if(!r.ok)throw new Error(p);return r.json()});
Promise.all([J("data/sources.json"),J("data/routes.geojson"),J("data/crossings.geojson"),J("data/money_flows.json"),J("data/networks.json"),J("data/china.json"),J("data/events.json"),J("data/territory.json"),J("basemap/latam.topo.json"),
 ...["mexico","venezuela-caribbean","andes","brazil","money"].map(a=>J(`data/arcs/${a}.json`))]).then(([src,routes,cross,money,net,china,events,terr,topo,...arcs])=>{
  const adm=topojson.feature(topo,topo.objects.admin1);
  src.sources.forEach(s=>SRC[s.id]=s);
  $("asof").textContent=`Reference data as of ${src.as_of} · headlines updated ${events.as_of}`;
  const GC=Object.fromEntries(terr.groups.map(g=>[g.id,g]));
  kpis(net,cross,money,events,terr);
  const M=mapView(topo,adm,terr,routes,cross,china,GC);
  moneyTile(money);netTile(net,terr);chinaTile(china);cards(net,terr,M);ticker(events);background(arcs);sources(src);
});
function kpis(net,cross,money,events,terr){
  const fto=net.groups.filter(g=>g.fto).length, s=cross.stats;
  const cm=money.links.filter(l=>l.source==="cmln").reduce((a,l)=>a+l.value,0);
  const today=events.events.filter(e=>e.date===events.as_of).length;
  const K=[[fto,"groups tracked here are US-designated FTOs",srcLink(["FTO"])],
   [s.fy2025_border_fentanyl_lb.toLocaleString()+" lb",`fentanyl seized at the US border, FY2025 (${s.change_vs_fy2024_pct}% vs FY2024)`,srcLink(s.cites)],
   ["$"+cm+"bn","suspicious activity linked to Chinese money laundering networks, 2020-24",srcLink(["FINCEN_CMLN_FTA"])],
   [terr.regions.length,"states and departments with a sourced group footprint",srcLink(["DEA_MAP_SILLA","ACLED_RIFT"])+", InSight Crime"],
   [today,`headlines in today's feed (${events.as_of})`,`<a href="https://github.com/trishbailey/cartel-dashboard/blob/main/config/sources.yaml" target="_blank" rel="noopener">feed list</a>`]];
  $("kpis").innerHTML=K.map(k=>`<div class="kpi"><div class="v">${k[0]}</div><div class="l">${k[1]}</div><div class="s">Source: ${k[2]}</div></div>`).join("");
}
function mapView(topo,adm,terr,routes,cross,china,GC){
  const svg=d3.select("#mapsvg"),W=svg.node().parentNode.clientWidth||1200,H=Math.round(Math.max(460,Math.min(W*0.62,window.innerHeight-150)));svg.attr("width",W).attr("height",H).style("height",H+"px");
  const view=document.createElement("div");view.className="overlay viewbtns";view.innerHTML='<button class="chip on" data-v="mx">Mexico</button><button class="chip" data-v="all">All Latin America</button><button class="chip" data-v="sa">South America</button>';svg.node().parentNode.appendChild(view);
  const proj=d3.geoConicEqualArea().parallels([-15,20]).rotate([78,0]).center([0,-2]).fitExtent([[10,10],[W-10,H-10]],{type:"MultiPoint",coordinates:[[-118,32.7],[-34.8,-7],[-70,-40],[-55,-34],[-81.3,-5]]});
  const path=d3.geoPath(proj),defs=svg.append("defs"),g=svg.append("g");
  adm.features.forEach(f=>{if(d3.geoArea(f)>2*Math.PI){const rv=p=>p.map(r=>r.slice().reverse());const g=f.geometry;g.coordinates=g.type==='Polygon'?rv(g.coordinates):g.coordinates.map(rv)}});
  const RB=Object.fromEntries(terr.regions.map(r=>[r.id,r]));
  const zoom=d3.zoom().scaleExtent([1,14]).translateExtent([[-W*.2,-H*.2],[W*1.2,H*1.2]]).on("zoom",e=>{g.attr("transform",e.transform);g.selectAll(".ovl").attr("stroke-width",2/e.transform.k);g.selectAll(".pt").attr("transform",function(){return `${this.dataset.t} scale(${1/e.transform.k})`})});svg.call(zoom).on("dblclick.zoom",null);
  const fitBox=(lo0,la0,lo1,la1)=>{const pts=[[lo0,la0],[lo1,la0],[lo0,la1],[lo1,la1],[(lo0+lo1)/2,la0],[(lo0+lo1)/2,la1]].map(proj);const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);const k=Math.min(14,0.92/Math.max((x1-x0)/W,(y1-y0)/H));return d3.zoomIdentity.translate(W/2,H/2).scale(k).translate(-(x0+x1)/2,-(y0+y1)/2)};
  const VIEWS={mx:fitBox(-117.5,14,-86.5,32.8),all:d3.zoomIdentity,sa:fitBox(-82,-40,-34,13)};
  view.querySelectorAll("button").forEach(b=>b.onclick=()=>{view.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));svg.transition().duration(700).call(zoom.transform,VIEWS[b.dataset.v])});
  g.append("g").selectAll("path").data(topojson.feature(topo,topo.objects.countries).features).join("path").attr("d",path).attr("fill",d=>d.properties.iso==="USA"?"#16243f":"#1b2c4a");
  const pats={};
  const pattern=cols=>{const k=cols.join("-").replace(/#/g,"");if(pats[k])return pats[k];const w=4*cols.length;
    const p=defs.append("pattern").attr("id","p"+k).attr("patternUnits","userSpaceOnUse").attr("width",w).attr("height",w).attr("patternTransform","rotate(45)");
    cols.forEach((c,i)=>p.append("rect").attr("x",i*4).attr("y",0).attr("width",4).attr("height",w).attr("fill",c));return pats[k]=`url(#p${k})`};
  let filt=null;
  const style=d=>{const r=RB[d.properties.id];if(!r)return{f:"#1b2c4a",o:1};
    if(filt){const e=r.groups.find(x=>x.group===filt);return e?{f:GC[filt].color,o:LV[e.level]}:{f:"#1b2c4a",o:1}}
    let heavy=r.groups.filter(x=>x.level!=="present");
    if(r.contested&&r.contested.groups.length>1)heavy=r.contested.groups.map(x=>({group:x}));
    const dom=r.groups.filter(x=>x.level==="dominant");if(dom.length===1&&!(r.contested&&r.contested.groups.length>1))heavy=dom;
    if(!heavy.length)return{f:GC[r.groups[0].group].color,o:.35};
    if(heavy.length===1){const c=GC[heavy[0].group].color;return r.contested?{f:pattern([c,"#0b1526"]),o:.95}:{f:c,o:.85}}
    return{f:pattern(heavy.slice(0,3).map(x=>GC[x.group].color)),o:.9}};
  const ad=g.append("g").selectAll("path").data(adm.features).join("path").attr("class","adm").attr("d",path).attr("stroke","none").attr("vector-effect","non-scaling-stroke").attr("stroke-width",1.5).style("cursor",d=>RB[d.properties.id]?"pointer":"default")
    .on("click",(e,d)=>regionShow(d)).on("mouseover",function(){d3.select(this).attr("stroke","#fff").raise()}).on("mouseout",function(){d3.select(this).attr("stroke","none")});
  ad.append("title").text(d=>{const r=RB[d.properties.id];return (d.properties.name||"")+(r?": "+r.groups.map(x=>GC[x.group].name).join(", "):"")});
  const paint=()=>ad.each(function(d){const s=style(d);d3.select(this).attr("fill",s.f).attr("fill-opacity",s.o)});paint();
  g.append("path").datum(topojson.mesh(topo,topo.objects.admin1,(a,b)=>a!==b&&a.properties.iso===b.properties.iso&&a.properties.iso!=="USA")).attr("d",path).attr("fill","none").attr("stroke","#0b1526").attr("stroke-width",.6).attr("vector-effect","non-scaling-stroke").style("pointer-events","none");
  g.append("path").datum(topojson.mesh(topo,topo.objects.countries)).attr("d",path).attr("fill","none").attr("stroke","#8fa3c4").attr("stroke-width",1).attr("vector-effect","non-scaling-stroke").style("pointer-events","none");
  function regionShow(d){const r=RB[d.properties.id];if(!r){drawer(`<h2>${esc(d.properties.name||"")}</h2><p class="muted">No sourced group footprint is mapped here. That reflects data coverage, not an absence of organized crime.</p>`);return}
    drawer(`<h2>${esc(r.name)}</h2><div class="muted">${esc(r.iso)}</div>`+(r.contested?`<h3>Contested</h3><div class="rg">${r.contested.groups.map(x=>`<span class="dot" style="background:${GC[x].color}"></span> ${esc(GC[x].name)}`).join(" vs ")}<div>${esc(r.contested.note)}</div>${cite(r.contested.cites)}</div>`:"")+
    "<h3>Groups active</h3>"+r.groups.slice().sort((a,b)=>LV[b.level]-LV[a.level]).map(x=>`<div class="rg"><span class="dot" style="background:${GC[x.group].color}"></span> <b>${esc(GC[x.group].name)}</b> <span class="lvl">${esc(terr.levels[x.level])}${r.contested&&r.contested.groups.includes(x.group)?" · contests":""}</span>${x.note?`<div>${esc(x.note)}</div>`:""}${cite(x.cites)}</div>`).join(""))}
  // legend chips = filter
  const used=new Set(terr.regions.flatMap(r=>r.groups.map(x=>x.group)));
  const L=$("grouplegend");L.innerHTML=`<button class="chip on" data-g="">All groups</button>`+terr.groups.filter(x=>used.has(x.id)).map(x=>`<button class="chip" data-g="${x.id}"><span class="dot" style="background:${x.color}"></span>${esc(x.name)}</button>`).join("");
  const setF=id=>{filt=id||null;L.querySelectorAll(".chip").forEach(b=>b.classList.toggle("on",b.dataset.g===(id||"")));paint();key()};
  L.querySelectorAll(".chip").forEach(b=>b.onclick=()=>setF(b.dataset.g));
  const key=()=>$("keybox").innerHTML=filt?`<b>${esc(GC[filt].name)}</b><br>`+Object.entries(terr.levels).map(([k,v])=>`<span class="dot" style="background:${GC[filt].color};opacity:${LV[k]}"></span> ${esc(v)}`).join("<br>")
    :`<b>Shading</b><br><span class="dot" style="background:#e4572e"></span> one group dominant or significant<br><span class="dot hatch"></span> stripes: contested or shared by 2-3 groups<br><span class="dot" style="background:#e4572e;opacity:.35"></span> lighter: lesser presence only<br><span class="dot" style="background:#1b2c4a;border:1px solid #3a5583"></span> no sourced footprint`;key();
  $("mapnotes").innerHTML=`<p>${esc(terr.note)}</p><h3>Where footprint data is thin</h3><ul>${terr.thin.map(t=>`<li>${esc(t)}</li>`).join("")}</ul>`;
  // overlays
  const proj2=c=>proj(c);
  const layers={};const og=g.append("g");
  const mk=(k,label,color,draw)=>{layers[k]=og.append("g").style("display","none");draw(layers[k]);
    const lab=document.createElement("label");lab.innerHTML=`<input type="checkbox"> <span class="dot" style="background:${color}"></span> ${label}`;lab.querySelector("input").onchange=e=>layers[k].style("display",e.target.checked?null:"none");$("layers").appendChild(lab)};
  const rshow=p=>drawer(`<h2>${esc(p.name)}</h2><span class="tag">${esc(p.kind||p.category||"")}</span>${p.commodity?`<span class="tag">${esc(p.commodity)}</span>`:""}<p>${esc(p.text)}</p>${p.says_vs_does?`<p class="says">Says vs does: ${esc(p.says_vs_does)}</p>`:""}${cite(p.cites)}`);
  const lines=(sel,feat)=>sel.selectAll("path").data(feat).join("path").attr("class","ovl").attr("d",path).attr("fill","none").attr("stroke",d=>COL[d.properties.commodity]||"#ccc").attr("stroke-width",2).attr("stroke-dasharray",d=>d.properties.confidence==="reported"?null:"5 4").style("cursor","pointer").on("click",(e,d)=>rshow(d.properties)).append("title").text(d=>d.properties.name);
  const drug=routes.features.filter(f=>["cocaine","fentanyl / methamphetamine","precursors"].includes(f.properties.commodity));
  mk("drug","Drug and precursor routes","#ff6b6b",s=>lines(s,drug));
  mk("other","Migrant and firearm routes","#6aa684",s=>lines(s,routes.features.filter(f=>["migrants","firearms"].includes(f.properties.commodity))));
  mk("money","Cash and money routes","#5b8fd1",s=>lines(s,routes.features.filter(f=>f.properties.commodity==="cash")));
  mk("cross","Border crossings and hubs","#ffffff",s=>{const n=s.selectAll("g").data(cross.features).join("g").attr("class","pt").attr("data-t",d=>`translate(${proj2(d.geometry.coordinates)})`).attr("transform",d=>`translate(${proj2(d.geometry.coordinates)})`).style("cursor","pointer").on("click",(e,d)=>rshow(d.properties));n.append("circle").attr("r",4).attr("fill","#fff").attr("stroke","#0b1526");n.append("title").text(d=>d.properties.name)});
  mk("china","China-linked sites","#c8a24a",s=>{const n=s.selectAll("g").data(china.items.filter(i=>i.lonlat)).join("g").attr("class","pt").attr("data-t",d=>`translate(${proj2(d.lonlat)})`).attr("transform",d=>`translate(${proj2(d.lonlat)})`).style("cursor","pointer").on("click",(e,d)=>rshow({...d,name:d.title}));n.append("rect").attr("x",-5).attr("y",-5).attr("width",10).attr("height",10).attr("fill","#c8a24a").attr("transform","rotate(45)");n.append("text").attr("class","lbl").attr("x",9).attr("y",4).text(d=>d.title)});
  svg.call(zoom.transform,VIEWS.mx);
  return {setF:id=>{setF(id);document.querySelector(".maptile").scrollIntoView({behavior:"smooth"})}};
}
function moneyTile(m){
  $("moneyunit").textContent=m.unit;
  const el=$("sankey"),W=el.parentNode.clientWidth-28,H=300;const svg=d3.select(el).attr("width",W).attr("height",H);
  const {nodes,links}=d3.sankey().nodeId(d=>d.id).nodeWidth(14).nodePadding(26).extent([[8,22],[W-200,H-8]])({nodes:m.nodes.map(d=>({...d})),links:m.links.map(d=>({...d}))});
  const gc={source:"#c8a24a",channel:"#5b8fd1",use:"#6aa684"};
  svg.append("g").selectAll("path").data(links).join("path").attr("d",d3.sankeyLinkHorizontal()).attr("fill","none").attr("stroke","#5b8fd1").attr("stroke-opacity",.4).attr("stroke-width",d=>Math.max(2,d.width)).style("cursor","pointer")
   .on("click",(e,d)=>drawer(`<h2>${esc(d.source.name)} → ${esc(d.target.name)}</h2><p><b>$${d.value}bn</b> (${esc(d.period||"")}, ${esc(d.status||"")})</p><p class="note">${esc(m.unit)}</p>${cite(d.cites)}`)).append("title").text(d=>`${d.source.name} → ${d.target.name}: $${d.value}bn`);
  const n=svg.append("g").selectAll("g").data(nodes).join("g");
  n.append("rect").attr("x",d=>d.x0).attr("y",d=>d.y0).attr("width",d=>d.x1-d.x0).attr("height",d=>Math.max(2,d.y1-d.y0)).attr("fill",d=>gc[d.group]);
  n.append("text").attr("class","lbl").attr("x",d=>d.group==="source"?d.x1+6:d.group==="use"?d.x1+6:d.x0).attr("y",d=>d.group==="channel"?d.y0-5:(d.y0+d.y1)/2+4).text(d=>{const nm=d.name.length>34?d.name.slice(0,32)+"…":d.name;return d.group==="source"?`$${d.value}bn total`:`${nm} $${d.value}bn`});
  $("moneymore").innerHTML=`<p><b>${esc(m.takeaway)}</b></p><p>${esc(m.summary)}</p><h3>Typologies flagged (overlapping)</h3>${m.typologies.map(t=>`<div>${esc(t.name)}: $${t.value}bn</div>`).join("")}${cite(["FINCEN_CMLN_FTA"])}<h3>Related</h3>${m.related.map(r=>`<div><b>${esc(r.name)}</b>${r.value?` ($${r.value}bn)`:""}: ${esc(r.text||"")}${cite(r.cites)}</div>`).join("")}<p class="note">${esc(m.notes)}</p>`;
}
function netTile(net,terr){
  const el=$("netsvg"),W=el.parentNode.clientWidth-28,H=330;const svg=d3.select(el).attr("width",W).attr("height",H);
  const tc=Object.fromEntries(terr.groups.filter(g=>g.network_id).map(g=>[g.network_id,g.color]));
  const ids=new Set(net.edges.flatMap(e=>[e.source,e.target]));
  const nodes=net.groups.filter(g=>ids.has(g.id)).map(d=>({...d})),by=Object.fromEntries(nodes.map(n=>[n.id,n]));
  const edges=net.edges.map(e=>({...e,source:by[e.source],target:by[e.target]}));
  $("netlegend").innerHTML=Object.entries(KCOL).map(([k,c])=>`<span><span class="dot" style="background:${c};height:4px"></span> ${k}</span>`).join("");
  const sim=d3.forceSimulation(nodes).force("link",d3.forceLink(edges).distance(70)).force("charge",d3.forceManyBody().strength(-260)).force("collide",d3.forceCollide(30)).force("center",d3.forceCenter(W/2,H/2)).force("x",d3.forceX(W/2).strength(.08)).force("y",d3.forceY(H/2).strength(.12)).stop();
  for(let i=0;i<300;i++)sim.tick();nodes.forEach(d=>{d.x=Math.max(12,Math.min(W-90,d.x));d.y=Math.max(14,Math.min(H-12,d.y))});
  svg.append("g").selectAll("line").data(edges).join("line").attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y).attr("stroke",d=>KCOL[d.kind]).attr("stroke-width",2.5).attr("stroke-dasharray",d=>d.kind==="alleged link"?"4 3":null).style("cursor","pointer")
   .on("click",(e,d)=>drawer(`<h2>${esc(d.source.name)} and ${esc(d.target.name)}</h2><span class="tag">${esc(d.kind)}</span><p>${esc(d.text)}</p>${cite(d.cites)}`));
  const n=svg.append("g").selectAll("g").data(nodes).join("g").attr("transform",d=>`translate(${d.x},${d.y})`).style("cursor","pointer").on("click",(e,d)=>drawer(groupHtml(d,net)));
  n.append("circle").attr("r",7).attr("fill",d=>tc[d.id]||"#9aa6b8").attr("stroke","#e6e9ef").attr("stroke-width",d=>d.fto?1.5:0);
  n.append("text").attr("class","lbl").attr("x",9).attr("y",4).text(d=>d.name.split(" (")[0].replace(/^Cartel (de |del )?/,"").slice(0,18));
}
function chinaTile(c){
  const ab={precursors:"PRE",ports:"PRT",money:"$",finance:"$",laundering:"$",infrastructure:"INF"};
  const cc={precursors:"#c8a24a",ports:"#5b8fd1",money:"#6aa684",finance:"#6aa684",laundering:"#6aa684"};
  $("china").innerHTML=c.items.map((i,k)=>`<div class="ch" data-k="${k}"><div class="ico" style="background:${cc[i.category]||"#9aa6b8"}">${esc(ab[i.category]||i.category.slice(0,3).toUpperCase())}</div><div class="t"><b>${esc(i.title)}</b><div class="muted">${esc(i.category)}</div></div></div>`).join("");
  $("china").querySelectorAll(".ch").forEach(el=>el.onclick=()=>{const i=c.items[+el.dataset.k];drawer(`<h2>${esc(i.title)}</h2><span class="tag">${esc(i.category)}</span><p>${esc(i.text)}</p>${i.says_vs_does?`<p class="says">Says vs does: ${esc(i.says_vs_does)}</p>`:""}${cite(i.cites)}`)});
}
function groupHtml(x,net){const nm=Object.fromEntries(net.groups.map(g=>[g.id,g.name]));const es=net.edges.filter(e=>e.source===x.id||e.target===x.id);
  return `<h2>${esc(x.name)}</h2><span class="tag">${esc(x.kind)}</span><span class="tag">${esc(x.country)}</span>${x.fto?`<span class="tag fto">FTO ${x.fto.date}</span>`:""}<p>${esc(x.summary)}</p>${x.says_vs_does?`<p class="says">Says vs does: ${esc(x.says_vs_does)}</p>`:""}
  ${(x.leaders||[]).map(p=>`<div class="rg"><b>${esc(p.name)}</b> (${esc(p.role)}): ${esc(p.status)}${cite(p.cites)}</div>`).join("")}${cite(x.cites)}
  ${es.length?"<h3>Relationships</h3>"+es.map(e=>`<div class="rg"><span class="tag">${esc(e.kind)}</span>${esc(nm[e.source===x.id?e.target:e.source])}: ${esc(e.text)}${cite(e.cites)}</div>`).join(""):""}`}
let NET;
function cards(net,terr,M){NET=net;
  const tc=Object.fromEntries(terr.groups.filter(g=>g.network_id).map(g=>[g.network_id,g]));
  $("cards").innerHTML=net.groups.map((x,k)=>{const L=(x.leaders||[])[0];const t=tc[x.id];
   return `<div class="gc" data-k="${k}" style="border-left-color:${t?t.color:"#56657f"}"><h4>${esc(x.name)}</h4>${x.fto?`<span class="tag fto">FTO</span>`:""}<span class="tag">${esc(x.country)}</span>
   ${L?`<div class="st">${esc(L.name)}: ${esc(L.status)}</div>`:""}<div class="one">${esc(first(x.summary))}</div>
   <div class="full">${groupHtml(x,net).replace(/<h2>.*?<\/h2>/,"")}${t?`<button class="chip" data-map="${t.id}">Show footprint on map</button>`:""}</div></div>`}).join("");
  $("cards").querySelectorAll(".gc").forEach(el=>el.onclick=e=>{if(e.target.closest("a"))return;const b=e.target.closest("[data-map]");if(b){e.stopPropagation();M.setF(b.dataset.map);return}el.classList.toggle("open")});
}
function ticker(ev){
  const th=["all",...new Set(ev.events.map(e=>e.theatre))],F=$("evfilters");let cur="all";
  F.innerHTML=th.map(t=>`<button class="chip ${t==="all"?"on":""}" data-t="${esc(t)}">${esc(t)}</button>`).join("");
  const draw=()=>$("events").innerHTML=ev.events.filter(e=>cur==="all"||e.theatre===cur).map(e=>`<div class="ev"><a href="${esc(e.url)}" target="_blank" rel="noopener" title="${esc(e.title)}">${esc(e.title.length>110?e.title.slice(0,108)+"…":e.title)}</a><div class="m">${esc(e.source)} · ${esc(e.date)} · ${esc(e.theatre)}</div></div>`).join("")||"<p class='muted'>No items.</p>";
  F.querySelectorAll(".chip").forEach(b=>b.onclick=()=>{cur=b.dataset.t;F.querySelectorAll(".chip").forEach(x=>x.classList.toggle("on",x===b));draw()});draw();
}
function background(arcs){$("arcs").innerHTML=arcs.map(a=>`<div class="arc"><h3>${esc(a.title)}</h3><p>${esc(a.current_phase)}</p><details class="more"><summary>History and turning points</summary>${a.history.map(h=>`<div><b>${esc(h.period)}</b>: ${esc(h.text)}</div>`).join("")}${a.turning_points.map(t=>`<div>${esc(t.date)}: ${esc(t.text)}</div>`).join("")}${a.log.length?"<h3>Recent</h3>"+a.log.slice(-4).reverse().map(l=>`<div>${esc(l.date)}: ${esc(l.text)}${links(l.links)}</div>`).join(""):""}${cite(a.cites)}</details></div>`).join("")}
function sources(s){$("srclist").innerHTML=`<p class="muted">${esc(s.note)}</p><table>${s.sources.map(x=>`<tr><td>${esc(x.id)}</td><td><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.title)}</a></td><td>${esc(x.publisher)}</td><td>${esc(x.date)}</td></tr>`).join("")}</table>`}
