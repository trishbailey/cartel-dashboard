/* Leader cards + state capture layer. Self-contained; hooks: legend chips and Who's-who cards. */
(function(){
const J=p=>fetch(p).then(r=>{if(!r.ok)throw new Error(p);return r.json()});
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const A=s=>s?FN({url:s.url,name:s.name,date:s.date}):"";
const STL={at_large:"At large",jailed:"Jailed",extradited:"In US custody",dead:"Dead",reported_dead:"Reported dead"};
const CST={convicted:["Convicted","#c0504d"],charged:["Charged","#c8a24a"],alleged:["Alleged","#9aa6b8"],sanctioned:["Sanctioned","#8e6cc0"],pardoned:["Pardoned","#4a9a8a"],acquitted:["Acquitted","#4a9a8a"],dropped:["Dropped","#4a9a8a"],delisted:["Delisted","#4a9a8a"]};
const ORDER=["convicted","charged","alleged","sanctioned","pardoned","acquitted","dropped","delisted"];
const usd=n=>"$"+(n>=1e6?(n/1e6)+"M":n.toLocaleString());
Promise.all([J("data/leaders.json"),J("data/capture.json"),J("data/networks.json"),J("data/territory.json"),J("basemap/latam.topo.json")]).then(([ld,cp,net,ter,topo])=>{
 const gname={};net.groups.forEach(g=>gname[g.id]=g.name);ter.groups.forEach(g=>gname[g.id]=gname[g.id]||g.name);
 const anchor=document.querySelector(".row2b")||document.querySelector("main").lastElementChild;
 // ---------- leaders ----------
 const t=document.createElement("section");t.className="tile ldtile";t.id="leaders";
 const gids=[];ld.leaders.forEach(l=>l.group_ids.forEach(g=>{if(!gids.includes(g))gids.push(g)}));
 t.innerHTML=`<div class="tilehead"><h2>Leaders</h2><span class="muted">Click a card for details · charges are allegations unless convicted</span></div>
 <div class="chips" id="ldchips"><span class="chip on" data-lg="">All</span>${gids.map(g=>`<span class="chip" data-lg="${g}">${esc(gname[g]||g)}</span>`).join("")}</div>
 <div id="ldnote" class="muted small"></div><div class="ldgrid" id="ldgrid"></div>
 <details class="more"><summary>About these cards</summary><p class="small">${esc(ld.method)} As of ${esc(ld.as_of)}.</p></details>`;
 anchor.parentNode.insertBefore(t,anchor);
 const grid=t.querySelector("#ldgrid");grid.addEventListener("click",e=>{if(e.target.closest("a"))return;const c=e.target.closest(".ld");if(c)c.classList.toggle("open")});
 grid.innerHTML=ld.leaders.map(l=>{const p=l.photo;const im=p.placeholder?"img/leaders/placeholder.svg":p.file;
  const fl=(l.flags||[]).includes("successor_unconfirmed")?`<span class="st flag">Successor unconfirmed</span>`:"";
  return `<div class="ld" data-g="${l.group_ids.join(" ")}"><div class="ph"><img src="${esc(im)}" alt="${p.placeholder?"No photo available":"Photo of "+esc(l.name)}" loading="lazy">
  <div><h3>${esc(l.name)}</h3>${l.alias?`<div class="al">“${esc(l.alias)}”</div>`:""}<div class="rl">${esc(l.group_ids.map(g=>gname[g]||g).join(" · "))}${l.faction&&!l.group_ids.some(g=>gname[g]===l.faction)?" · "+esc(l.faction):""}</div>
  <div style="margin-top:5px"><span class="st ${l.status}">${{at_large:"🎯",jailed:"⛓",extradited:"⛓",dead:"✝",reported_dead:"✝?"}[l.status]||""} ${STL[l.status]}</span>${l.reward_usd?`<span class="rw" title="US reward offer">💲${usd(l.reward_usd)}</span>`:""}${fl}</div></div></div>
  <div class="bd"><p>${esc(l.status_note)} ${A(l.status_source)}</p>
  ${l.reward_usd?`<p><b>US reward:</b> up to ${usd(l.reward_usd)} <span class="src">(${A(l.reward_source)})</span></p>`:""}
  <ul>${l.charges.map(c=>`<li>${esc(c)}</li>`).join("")}</ul><p>${esc(l.known_for)}</p>
  <p class="src">${FN(l.sources.map(s=>({url:s.url,name:s.name,date:s.date})))}</p></div>
  <div class="lic">${p.placeholder?"Placeholder: no clean official or openly licensed photo found.":`Photo: ${esc(p.credit)}. ${esc(p.license)}. <a href="${esc(p.image_source_url)}" target="_blank" rel="noopener">source</a>${p.provenance_note?` <br>⚠ ${esc(p.provenance_note)}`:""}`}</div></div>`}).join("");
 function setG(g,from){t.querySelectorAll("#ldchips .chip").forEach(c=>c.classList.toggle("on",c.dataset.lg===(g||"")));
  grid.querySelectorAll(".ld").forEach(c=>{const m=!g||c.dataset.g.split(" ").includes(g);c.classList.toggle("hl",!!g&&m);c.classList.toggle("dim",!!g&&!m)});
  const n=g?grid.querySelectorAll(".ld.hl").length:ld.leaders.length;
  t.querySelector("#ldnote").textContent=g?(from?`Highlighted from ${from}: `:"")+`${gname[g]||g}: ${n} leader card${n==1?"":"s"}`+(n?"":" (none profiled yet)"):"";}
 t.querySelector("#ldchips").onclick=e=>{const c=e.target.closest(".chip");if(c)setG(c.dataset.lg)};
 document.addEventListener("click",e=>{const c=e.target.closest("#grouplegend .chip[data-g]");if(c){setG(c.dataset.g,"map");return}
  const k=e.target.closest("#cards [data-map]");if(k)setG(k.dataset.map,"Who's who")},true);
 // ---------- capture ----------
 const s=document.createElement("section");s.className="tile cptile";s.id="capture";
 s.innerHTML=`<div class="tilehead"><h2>State capture and corruption: documented cases</h2><span class="muted">Convictions, charges, US sanctions, and acquittals/dismissals. Counts of cases, not a verdict on any government.</span></div>
 <div class="cplegend">${ORDER.map(k=>`<span title="${esc(cp.status_legend[k])}"><i style="background:${CST[k][1]}"></i>${CST[k][0]}</span>`).join("")}</div>
 <div class="cpwrap"><svg id="cpmap"></svg><div><div class="muted small">Cases by country: <span class="cpramp"></span> light = fewer, dark = more. Click a country.</div><div id="cplist"></div><details class="more"><summary>Case list</summary><div id="cpcases" class="cpcases"></div></details></div></div>
 <details class="more"><summary>Method and gaps</summary><p class="small">${esc(cp.method)} Status meanings: ${ORDER.map(k=>`<b>${CST[k][0]}</b>: ${esc(cp.status_legend[k])}`).join("; ")}.</p></details>`;
 anchor.parentNode.insertBefore(s,anchor);
 const tot={};cp.countries.forEach(c=>tot[c.country]=c);const mx=d3.max(cp.countries,c=>c.total);
 const col=d3.scaleSequentialSqrt([0,mx],d3.interpolateLab("#fde4d8","#7a1712"));
 const svg=d3.select("#cpmap"),W=svg.node().clientWidth||520,H=420;svg.attr("viewBox",`0 0 ${W} ${H}`);
 const fc=topojson.feature(topo,topo.objects.countries);
 const proj=d3.geoConicEqualArea().parallels([-15,20]).rotate([78,0]).fitExtent([[6,6],[W-6,H-6]],{type:"MultiPoint",coordinates:[[-117,32.5],[-35,-7],[-70,-28],[-81.3,-5],[-60,10]]});
 const path=d3.geoPath(proj);
 svg.append("g").selectAll("path").data(fc.features).join("path").attr("class","c").attr("d",path)
  .attr("fill",d=>tot[d.properties.iso]?col(tot[d.properties.iso].total):"#1a2742")
  .on("click",(e,d)=>tot[d.properties.iso]&&pick(d.properties.iso)).append("title").text(d=>tot[d.properties.iso]?`${tot[d.properties.iso].name}: ${tot[d.properties.iso].total} documented cases`:"No cases recorded in this dataset");
 svg.append("g").selectAll("text").data(fc.features.filter(d=>tot[d.properties.iso])).join("text").attr("transform",d=>`translate(${path.centroid(d)})`).attr("text-anchor","middle").attr("fill","#fff").attr("stroke","#0b1526").attr("stroke-width",2.5).attr("paint-order","stroke").attr("font-size",12).attr("font-weight",700).attr("pointer-events","none").text(d=>tot[d.properties.iso].total);
 const list=s.querySelector("#cplist");
 list.innerHTML=cp.countries.map(c=>`<div class="cprow" data-c="${c.country}"><span>${esc(c.name)}</span><span class="cpbar">${ORDER.filter(k=>c.by_status[k]).map(k=>`<span title="${CST[k][0]}: ${c.by_status[k]}" style="background:${CST[k][1]};width:${100*c.by_status[k]/mx}%"></span>`).join("")}</span><b>${c.total}</b></div>`).join("");
 list.onclick=e=>{const r=e.target.closest(".cprow");if(r)pick(r.dataset.c)};
 function pick(iso){const c=tot[iso];list.querySelectorAll(".cprow").forEach(r=>r.classList.toggle("sel",r.dataset.c===iso));svg.selectAll("path.c").classed("sel",d=>d.properties.iso===iso);
  const cs=cp.cases.filter(x=>x.country===iso).sort((a,b)=>ORDER.indexOf(a.status)-ORDER.indexOf(b.status)||b.date.localeCompare(a.date));
  const lv=Object.entries(c.by_level).map(([k,v])=>`${v} ${k}`).join(", ");
  s.querySelector("#cpcases").innerHTML=`<div class="small"><b>${esc(c.name)}</b>: ${c.total} cases (${lv})</div>`+cs.map(x=>`<div class="cp" style="border-left-color:${CST[x.status][1]}"><span class="st" style="background:${CST[x.status][1]}33;color:${CST[x.status][1]}">${CST[x.status][0]}</span> <b>${esc(x.person)}</b> <span class="m">· ${esc(x.office)} · ${esc(x.level)} · ${esc(x.date)}</span><div class="m">Group link: ${esc(x.group_link)}</div><div>${esc(x.note)}</div><div>${x.sources.map(A).join("; ")}</div></div>`).join("");}
 pick(cp.countries[0].country);
}).catch(e=>console.error("leaders/capture:",e));
})();
