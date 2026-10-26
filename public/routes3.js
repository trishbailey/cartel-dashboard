/* Three physical-goods route overlays: drugs & precursors, migrants, firearms (data/routes_*.geojson, pipeline/mk_routes3.py).
   Uses the map's own overlay helper (window.MAPX.mk from app.js) so toggles live in the Overlay box. Click a line: side panel with footnotes. */
(function(){
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const L=[{k:"drug",f:"data/routes_drugs.geojson",label:"Drug and precursor routes",color:"#ff00ff",dash:{cocaine:null,precursor:"1 5",synthetic:"9 5"}},
 {k:"migr",f:"data/routes_migrants.geojson",label:"Migrant routes",color:"#e6ff00",dash:{"northbound land":null,"rail (La Bestia)":"14 6","sea":"1 5","southbound (reverse) 2025":"9 4 1 4"}},
 {k:"guns",f:"data/routes_firearms.geojson",label:"Firearm routes (southbound)",color:"#7b61ff",dash:{land:null,sea:"1 5",air:"9 5"}}];
const FN=r=>(window.FN?window.FN(r):"");
function show(p,l){if(typeof drawer!=="function")return;drawer(`<h2>${esc(p.from)} → ${esc(p.to)}</h2><span class="tag" style="border-color:${l.color}">${esc(l.label)}</span><span class="tag">${esc(p.subtype)}</span><span class="tag">${esc(p.year)}</span><p>${esc(p.description)}${FN(p.sources)}</p>${p.volume?`<p class="muted small">Sourced volume: ${(+p.volume).toLocaleString()}</p>`:""}<p class="muted small">Schematic corridor between places named in the sources.</p>`)}
function start(){const M=window.MAPX;if(!M||!document.getElementById("layers")){return setTimeout(start,200)}
 Promise.all(L.map(l=>fetch(l.f).then(r=>r.json()))).then(gs=>{
  const notes=document.createElement("div");notes.id="routenotes";notes.className="rnotes muted small";
  gs.forEach((g,i)=>{const l=L[i],vs=g.features.map(f=>+f.properties.volume||0),mx=Math.max(...vs,1);
   const sw=d=>d.properties.volume?1.8+3.2*Math.sqrt(d.properties.volume/mx):2.2;
   M.mk(l.k,l.label,l.color,s=>{s.append("g").selectAll("path").data(g.features).join("path").attr("d",M.path).attr("fill","none").attr("stroke","#0b1526").attr("stroke-opacity",.85).attr("stroke-width",d=>sw(d)+2.5).attr("stroke-linecap","round").attr("vector-effect","non-scaling-stroke").style("pointer-events","none");
    s.append("g").selectAll("path").data(g.features).join("path").attr("class","ovl rt-"+l.k).attr("d",M.path).attr("fill","none").attr("stroke",l.color).attr("stroke-width",sw).attr("stroke-linecap","round").attr("stroke-dasharray",d=>l.dash[d.properties.subtype]||null).attr("vector-effect","non-scaling-stroke").style("cursor","pointer").on("click",(e,d)=>show(d.properties,l)).append("title").text(d=>`${d.properties.from} → ${d.properties.to} (${d.properties.subtype})`)});
   if(M.layers&&M.layers[l.k])M.layers[l.k].lower();
   const box=document.getElementById("layers"),lab=box.querySelector(`label[data-k="${l.k}"]`),hd=box.querySelector("b");
   if(lab){const ref=[...box.querySelectorAll("label")].find(x=>!L.some(y=>y.k===x.dataset.k));box.insertBefore(lab,ref||null);
    lab.querySelector(".dot").outerHTML=`<svg width="22" height="8" style="vertical-align:middle"><line x1="1" y1="4" x2="21" y2="4" stroke="${l.color}" stroke-width="3" stroke-linecap="round"/></svg>`}
   const subs=Object.keys(l.dash).filter(k=>g.features.some(f=>f.properties.subtype===k));
   notes.insertAdjacentHTML("beforeend",`<div data-k="${l.k}"><b style="color:${l.color}">${esc(l.label)}</b> (${g.features.length}): ${subs.map(k=>`<svg width="26" height="6"><line x1="1" y1="3" x2="25" y2="3" stroke="${l.color}" stroke-width="2.5" stroke-dasharray="${l.dash[k]||""}"/></svg> ${esc(k)}`).join(" · ")}. ${esc(g.notes.note)}${FN(g.notes.sources)}</div>`)});
  const mw=document.querySelector(".maptile .mapwrap");if(mw)mw.after(notes);
 }).catch(e=>console.warn("routes3:",e))}
start();})();
