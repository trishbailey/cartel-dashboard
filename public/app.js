const COL={precursors:"#c8a24a",cocaine:"#e6e9ef","fentanyl / methamphetamine":"#c0504d",migrants:"#6aa684",firearms:"#9b7fc6",cash:"#5b8fd1"};
const KCOL={rivalry:"#c0504d",alliance:"#6aa684",faction:"#9aa6b8","alleged link":"#c8a24a",service:"#5b8fd1"};
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let SRC={};
const cite=ids=>`<div class="cite">Sources: ${(ids||[]).map(i=>{const s=SRC[i];return s?`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.publisher)}: ${esc(s.title)}</a> (${esc(s.date)})`:esc(i)}).join("; ")}</div>`;
const links=ls=>`<div class="cite">Sources: ${ls.map(l=>`<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.source)}: ${esc(l.title)}</a>`).join("; ")}</div>`;
const R={},done={};
const openTab=t=>{document.querySelectorAll("#tabs button,.tab").forEach(x=>x.classList.toggle("on",x.dataset.t===t||x.id===t));if(R[t]&&!done[t]){done[t]=1;R[t]()}};
document.querySelectorAll("#tabs button").forEach(b=>b.onclick=()=>openTab(b.dataset.t));
const J=p=>fetch("data/"+p).then(r=>r.json());
Promise.all([J("sources.json"),J("routes.geojson"),J("crossings.geojson"),J("money_flows.json"),J("networks.json"),J("china.json"),J("events.json"),fetch("basemap/americas.geojson").then(r=>r.json()),
 ...["mexico","venezuela-caribbean","andes","brazil","money"].map(a=>J(`arcs/${a}.json`))]).then(([src,routes,cross,money,net,china,events,base,...arcs])=>{
  src.sources.forEach(s=>SRC[s.id]=s);
  document.getElementById("asof").textContent=`Reference data as of ${src.as_of}. Latest events updated ${events.as_of}.`;
  R.overview=()=>overview(arcs,net);R.map=()=>mapView(base,routes,cross,china);R.money=()=>moneyView(money);R.network=()=>netView(net);R.china=()=>chinaView(china);R.latest=()=>latest(events);R.sources=()=>sources(src);openTab("overview");
});
function overview(arcs,net){
  document.getElementById("arcs").innerHTML="<h2>Context</h2>"+arcs.map(a=>`<div class="arc"><h3>${esc(a.title)}</h3><p>${esc(a.current_phase)}</p>
   ${a.history.map(h=>`<div><b>${esc(h.period)}</b>: ${esc(h.text)}</div>`).join("")}
   <h3>Turning points</h3>${a.turning_points.map(t=>`<div>${esc(t.date)}: ${esc(t.text)}</div>`).join("")}
   ${a.log.length?`<h3>Recent</h3>`+a.log.slice(-4).reverse().map(l=>`<div>${esc(l.date)}: ${esc(l.text)}${links(l.links)}</div>`).join(""):""}${cite(a.cites)}</div>`).join("");
  const g=net.groups;
  document.getElementById("whoswho").innerHTML="<h2>Who's who</h2><div class='who'>"+g.filter(x=>x.summary&&!x.summary.startsWith("Designated as an FTO. This")).map(card).join("")+
   `<div class="card"><h4>Also designated FTOs</h4>${g.filter(x=>x.summary.startsWith("Designated as an FTO. This")).map(x=>`${esc(x.name)} (${x.fto.date})`).join(", ")}${cite(["FTO"])}</div></div>`;
}
function card(x){return `<div class="card"><h4>${esc(x.name)}</h4><span class="tag">${esc(x.kind)}</span><span class="tag">${esc(x.country)}</span>${x.fto?`<span class="tag fto">FTO ${x.fto.date}</span>`:""}
 <p>${esc(x.summary)}</p>${x.says_vs_does?`<p class="says">Says vs does: ${esc(x.says_vs_does)}</p>`:""}
 ${x.leaders.map(p=>`<div><b>${esc(p.name)}</b> (${esc(p.role)}): ${esc(p.status)}${cite(p.cites)}</div>`).join("")}${cite(x.cites)}</div>`}
function mapView(base,routes,cross,china){
  const svg=d3.select("#mapsvg"),W=svg.node().clientWidth||900,H=720;svg.attr("viewBox",`0 0 ${W} ${H}`);
  const proj=d3.geoConicEqualArea().parallels([-10,30]).rotate([88,0]).fitExtent([[10,10],[W-10,H-10]],{type:"MultiPoint",coordinates:[[-140,34],[-30,34],[-75,-35],[-118,-5]]});
  const path=d3.geoPath(proj),g=svg.append("g");
  svg.call(d3.zoom().scaleExtent([1,8]).on("zoom",e=>g.attr("transform",e.transform)));
  g.selectAll(".c").data(base.features).join("path").attr("d",path).attr("fill",d=>d.properties.iso==="USA"?"#1a2a47":"#1d3050").attr("stroke","#2e4670").attr("stroke-width",.6);
  g.append("text").attr("x",proj([-139,32])[0]).attr("y",proj([-139,32])[1]+40).attr("class","lbl").text("From China and India (precursors)");
  const det=document.getElementById("mapdetail");
  const show=p=>{det.innerHTML=`<h2>${esc(p.name||p.title)}</h2>${p.commodity?`<span class="tag">${esc(p.commodity)}</span><span class="tag">${esc(p.kind)}</span>`:`<span class="tag">${esc(p.kind||p.category)}</span>`}<p>${esc(p.text)}</p>${p.says_vs_does?`<p class="says">${esc(p.says_vs_does)}</p>`:""}${cite(p.cites)}`};
  const layers={};
  const rl=g.append("g");routes.features.forEach(f=>{const c=f.properties.commodity;(layers[c]=layers[c]||[]).push(
    rl.append("path").datum(f).attr("d",d3.line().curve(d3.curveCatmullRom)(f.geometry.coordinates.map(proj))).attr("fill","none").attr("stroke",COL[c]||"#ccc").attr("stroke-width",3).attr("stroke-opacity",.85)
     .attr("stroke-dasharray",f.properties.kind.includes("maritime")?"7 4":null).style("cursor","pointer").on("click",()=>show(f.properties)).append("title").text(f.properties.name).node().parentNode)});
  const sym={"port of entry":"#e6e9ef",maritime:"#5b8fd1","precursor port":"#c8a24a","departure port":"#9aa6b8","China-linked port":"#c0504d"};
  const pl=g.append("g");cross.features.forEach(f=>{const [x,y]=proj(f.geometry.coordinates),k=f.properties.kind;(layers["pts:"+k]=layers["pts:"+k]||[]).push(
    pl.append("circle").attr("cx",x).attr("cy",y).attr("r",6).attr("fill",sym[k]).attr("stroke","#0b1526").attr("stroke-width",1.5).style("cursor","pointer").on("click",()=>show(f.properties)).node());
    if(k!=="port of entry"||["C1","C5","C6"].includes(f.properties.id))layers["pts:"+k].push(pl.append("text").attr("x",x+8).attr("y",y+4).attr("class","lbl").text(f.properties.name.split(" (")[0]).node());});
  const L=document.getElementById("layers");
  L.innerHTML="<b>Layers</b>"+Object.keys(layers).map(k=>`<label><input type="checkbox" checked data-k="${esc(k)}"> <span class="sw" style="background:${k.startsWith("pts:")?sym[k.slice(4)]:COL[k]}"></span>${esc(k.replace("pts:",""))}</label>`).join("")+`<div class="muted">Dashed = maritime. Scroll to zoom.</div>`;
  L.querySelectorAll("input").forEach(i=>i.onchange=()=>layers[i.dataset.k].forEach(n=>n.style.display=i.checked?null:"none"));
  const s=cross.stats;document.getElementById("borderstats").innerHTML=`<h3>Border fentanyl seizures</h3><p>FY2025: ${s.fy2025_border_fentanyl_lb.toLocaleString()} lb, ${s.change_vs_fy2024_pct}% vs FY2024 and ${s.change_vs_fy2023_pct}% vs FY2023. ${s.share_hard_drugs_at_ports_pct}% of drugs other than marijuana are seized at ports of entry.</p><p class="note">${esc(s.note)}</p>${cite(s.cites)}`;
}
function sankeyDraw(sel,data,W,H,showVal){
  const el=document.querySelector(sel);W=el.parentNode.clientWidth||W;const svg=d3.select(sel).attr("viewBox",`0 0 ${W} ${H}`).attr("width",W).style("height",H+"px");
  const {nodes,links}=d3.sankey().nodeId(d=>d.id).nodeWidth(16).nodePadding(34).extent([[240,24],[W-200,H-10]])({nodes:data.nodes.map(d=>({...d})),links:data.links.map(d=>({...d}))});
  const gc={source:"#c8a24a",channel:"#5b8fd1",use:"#6aa684"};
  svg.append("g").selectAll("path").data(links).join("path").attr("d",d3.sankeyLinkHorizontal()).attr("fill","none").attr("stroke","#5b8fd1").attr("stroke-opacity",.35).attr("stroke-width",d=>Math.max(2,d.width))
   .append("title").text(d=>`${d.source.name} → ${d.target.name}${showVal?": $"+d.value+"bn":""}\nSources: ${d.cites.map(c=>SRC[c]?.publisher).join(", ")}`);
  const n=svg.append("g").selectAll("g").data(nodes).join("g"),tl=svg.append("g");
  n.append("rect").attr("x",d=>d.x0).attr("y",d=>d.y0).attr("width",d=>d.x1-d.x0).attr("height",d=>Math.max(2,d.y1-d.y0)).attr("fill",d=>gc[d.group]);
  tl.selectAll("text").data(nodes).join("text").attr("class","lbl").attr("x",d=>d.group==="source"?d.x0-6:d.group==="use"?d.x1+6:d.x0).attr("text-anchor",d=>d.group==="source"?"end":"start").attr("y",d=>d.group==="channel"?d.y0-6:(d.y0+d.y1)/2+4).text(d=>d.name+(showVal?` ($${d.value}bn)`:""));
}
function moneyView(m){
  document.getElementById("moneyhead").innerHTML=`<h2>${esc(m.title)}</h2><p><b>${esc(m.takeaway)}</b></p><p>${esc(m.summary)}</p><div class="muted">Unit: ${esc(m.unit)}</div>`;
  sankeyDraw("#sankey",m,780,340,true);
  const svg=d3.select("#bars"),W=document.getElementById("bars").parentNode.clientWidth||560,bh=30,H=m.typologies.length*bh+10;svg.attr("viewBox",`0 0 ${W} ${H}`).attr("width",W).style("height",H+"px");
  const x=d3.scaleLinear().domain([0,d3.max(m.typologies,d=>d.value)]).range([0,W-260]);
  m.typologies.forEach((t,i)=>{svg.append("text").attr("class","lbl").attr("x",0).attr("y",i*bh+19).text(t.name);svg.append("rect").attr("x",200).attr("y",i*bh+6).attr("height",18).attr("width",x(t.value)).attr("fill","#c8a24a");
   svg.append("text").attr("class","lbl").attr("x",206+x(t.value)).attr("y",i*bh+19).text("$"+t.value+"bn")});
  document.getElementById("related").innerHTML=cite(["FINCEN_CMLN_FTA"])+"<h3>Related</h3>"+m.related.map(r=>`<div class="card"><b>${esc(r.name)}</b>${r.value?` ($${r.value}bn)`:""}<div>${esc(r.text||"")}</div>${cite(r.cites)}</div>`).join("");
  document.getElementById("schtitle").textContent=m.schematic.title;sankeyDraw("#schematic",m.schematic,1100,300,false);
  document.getElementById("moneynotes").innerHTML=esc(m.notes)+cite(m.schematic.links[0].cites);
}
function netView(net){
  const svg=d3.select("#netsvg"),W=svg.node().clientWidth||900,H=680;svg.attr("viewBox",`0 0 ${W} ${H}`);
  const nodes=net.groups.map(d=>({...d})),byId=Object.fromEntries(nodes.map(n=>[n.id,n]));
  const edges=net.edges.map(e=>({...e,source:byId[e.source],target:byId[e.target]}));
  const kc={cartel:"#c0504d",faction:"#e08a6a",gang:"#9b7fc6","armed group":"#6aa684",guerrilla:"#6aa684","state-linked network":"#c8a24a",facilitator:"#5b8fd1"};
  document.getElementById("netlegend").innerHTML="<b>Links</b><br>"+Object.entries(KCOL).map(([k,c])=>`<span class="sw" style="background:${c}"></span>${k}`).join("<br>")+"<br><b>Groups</b><br>"+Object.entries(kc).map(([k,c])=>`<span class="sw" style="background:${c};height:10px;width:10px;border-radius:5px"></span>${k}`).join("<br>");
  const sim=d3.forceSimulation(nodes).force("link",d3.forceLink(edges).distance(110)).force("charge",d3.forceManyBody().strength(-420)).force("center",d3.forceCenter(W/2+60,H/2)).force("x",d3.forceX(W/2+60).strength(.05)).force("y",d3.forceY(H/2).strength(.07));
  const l=svg.append("g").selectAll("line").data(edges).join("line").attr("stroke",d=>KCOL[d.kind]).attr("stroke-width",2.5).attr("stroke-dasharray",d=>d.kind==="alleged link"?"5 4":null).style("cursor","pointer").on("click",(e,d)=>edgeShow(d));
  l.append("title").text(d=>`${d.source.name} - ${d.target.name}: ${d.kind}`);
  const n=svg.append("g").selectAll("g").data(nodes).join("g").style("cursor","pointer").on("click",(e,d)=>{document.getElementById("netdetail").innerHTML=card(d)+netEdges(d,net)})
    .call(d3.drag().on("start",(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y}).on("drag",(e,d)=>{d.fx=e.x;d.fy=e.y}).on("end",(e,d)=>{if(!e.active)sim.alphaTarget(0)}));
  n.append("circle").attr("r",d=>d.leaders.length?12:8).attr("fill",d=>kc[d.kind]||"#999").attr("stroke",d=>d.fto?"#e6e9ef":"none").attr("stroke-width",1.5);
  n.append("text").attr("class","lbl").attr("x",14).attr("y",4).text(d=>d.name.split(" (")[0]);
  sim.on("tick",()=>{nodes.forEach(d=>{d.x=Math.max(20,Math.min(W-150,d.x));d.y=Math.max(20,Math.min(H-20,d.y))});l.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);n.attr("transform",d=>`translate(${d.x},${d.y})`)});
  function edgeShow(d){document.getElementById("netdetail").innerHTML=`<h2>${esc(d.source.name)} and ${esc(d.target.name)}</h2><span class="tag">${esc(d.kind)}</span><p>${esc(d.text)}</p>${cite(d.cites)}`}
}
function netEdges(d,net){const es=net.edges.filter(e=>e.source===d.id||e.target===d.id);const nm=Object.fromEntries(net.groups.map(g=>[g.id,g.name]));
  return es.length?"<h3>Relationships</h3>"+es.map(e=>`<div><span class="tag">${esc(e.kind)}</span>${esc(nm[e.source===d.id?e.target:e.source])}: ${esc(e.text)}${cite(e.cites)}</div>`).join(""):""}
function chinaView(c){document.getElementById("chinalist").innerHTML=c.items.map(i=>`<div class="card"><span class="tag">${esc(i.category)}</span><h3>${esc(i.title)}</h3><p>${esc(i.text)}</p>${i.says_vs_does?`<p class="says">Says vs does: ${esc(i.says_vs_does)}</p>`:""}${cite(i.cites)}</div>`).join("")}
function latest(ev){
  document.getElementById("analysis").innerHTML=ev.analysis.length?"<h2>Analysis</h2>"+ev.analysis.slice(0,12).map(a=>`<div class="card"><span class="tag">${esc(a.theatre)}</span><span class="tag">${esc(a.date)}</span><h3>${esc(a.headline)}</h3><p>${esc(a.what_happened)}</p><p class="says">Says vs does: ${esc(a.says_vs_does)}</p><p><b>Follow the money:</b> ${esc(a.follow_the_money)}</p><p><b>At stake:</b> ${esc(a.at_stake)}</p>${a.tensions?`<p><b>Tensions:</b> ${esc([].concat(a.tensions).join("; "))}</p>`:""}${links(a.links)}</div>`).join(""):"";
  const th=["all",...new Set(ev.events.map(e=>e.theatre))],F=document.getElementById("evfilters");let cur="all",loc=false;
  F.innerHTML="<h2>Latest reporting</h2>"+th.map(t=>`<button data-t="${esc(t)}" class="${t==="all"?"on":""}">${esc(t)}</button>`).join("")+`<button data-l="1">Local media only</button>`;
  const draw=()=>document.getElementById("events").innerHTML=ev.events.filter(e=>(cur==="all"||e.theatre===cur)&&(!loc||e.local)).map(e=>`<div class="ev"><a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.title)}</a><div class="muted">${esc(e.source)} · ${esc(e.date)} · ${esc(e.theatre)}${e.local?" · local":""}</div></div>`).join("")||"<p class='muted'>No items.</p>";
  F.querySelectorAll("button").forEach(b=>b.onclick=()=>{if(b.dataset.l){loc=!loc;b.classList.toggle("on")}else{cur=b.dataset.t;F.querySelectorAll("button[data-t]").forEach(x=>x.classList.toggle("on",x===b))}draw()});draw();
}
function sources(s){document.getElementById("srclist").innerHTML=`<h2>Source registry</h2><p class="muted">${esc(s.note)}</p><table>${s.sources.map(x=>`<tr><td>${esc(x.id)}</td><td><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.title)}</a></td><td>${esc(x.publisher)}</td><td>${esc(x.date)}</td><td>${esc(x.type)}</td></tr>`).join("")}</table>`}
