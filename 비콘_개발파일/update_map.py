import re

with open('yard_b64.txt', 'r') as f:
    b64 = f.read().strip()

with open('beacon_yard.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_zone_rects = """const ZONE_RECTS = {
  C:{x:58,  y:100, w:82,  h:112},
  B:{x:152, y:100, w:86,  h:85},
  A:{x:248, y:100, w:88,  h:85},
  D:{x:58,  y:220, w:82,  h:75},
  E:{x:152, y:193, w:146, h:72},
  F:{x:152, y:270, w:146, h:57},
  G:{x:187, y:335, w:116, h:65},
  H:{x:303, y:335, w:110, h:65},
  I:{x:592, y:250, w:126, h:118},
  J:{x:473, y:367, w:262, h:51},
  K:{x:473, y:420, w:227, h:92},
};"""

new_buildings = """const BUILDINGS = [
  {label:'메가동\\n(TG·조립라인)', x:343, y:102, w:247, h:130, fill:'#cfd8dc', stroke:'#90a4ae'},
  {label:'메가동(신선)',           x:592, y:100, w:105, h:85,  fill:'#b0bec5', stroke:'#78909c'},
  {label:'기가동',                x:197, y:370, w:213, h:70,  fill:'#cfd8dc', stroke:'#90a4ae'},
  {label:'사무동',                x:13,  y:100, w:35,  h:135, fill:'#b0bec5', stroke:'#78909c'},
];"""

new_render = (
"""function renderYardMap(stats) {
  // stats: {zone: {total, sites[]}}
  const W = 840, H = 595;
  const IMG = 'data:image/png;base64,"""
+ b64 +
"""';
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:62vh;display:block">`;
  s += `<image href="${IMG}" x="0" y="0" width="${W}" height="${H}"/>`;

  // zone overlays
  for (const [zone, r] of Object.entries(ZONE_RECTS)) {
    const st = stats[zone] || {total: 0, sites: []};
    const fill = zoneColor(st.total);
    s += `<g class="zone-clickable" onclick="onZoneClick('${zone}')">`;
    s += `<rect x="${r.x}" y="${r.y}" width="${r.w}" height="${r.h}" rx="4" fill="${fill}" fill-opacity="0.55" stroke="#1565c0" stroke-width="1.5"/>`;
    const cx = r.x + r.w/2, cy = r.y + r.h/2;
    const minSide = Math.min(r.w, r.h);
    const fzLetter = minSide < 52 ? 13 : 16;
    const hasData = st.total > 0;
    s += `<text x="${cx}" y="${cy - (hasData ? Math.round(fzLetter*0.45) : 0)}" text-anchor="middle" dominant-baseline="middle" font-size="${fzLetter}" font-weight="800" fill="#0d47a1" stroke="#fff" stroke-width="2.5" paint-order="stroke">${zone}</text>`;
    if (hasData) {
      s += `<text x="${cx}" y="${cy + Math.round(fzLetter*0.7)}" text-anchor="middle" font-size="8" fill="#1a237e" stroke="#fff" stroke-width="2" paint-order="stroke">${st.total}패킹</text>`;
      if (st.sites.length > 0 && r.h >= 60) {
        const lbl = st.sites[0].length > 8 ? st.sites[0].slice(0, 7) + '...' : st.sites[0];
        s += `<text x="${cx}" y="${cy + Math.round(fzLetter*0.7) + 10}" text-anchor="middle" font-size="7" fill="#283593" stroke="#fff" stroke-width="1.5" paint-order="stroke">${lbl}${st.sites.length > 1 ? ' 외'+(st.sites.length-1) : ''}</text>`;
      }
    }
    s += `</g>`;
  }

  s += `</svg>`;
  document.getElementById('map-wrap').innerHTML = s;
}"""
)

html = re.sub(r'const ZONE_RECTS = \{[\s\S]*?\};', new_zone_rects, html)
html = re.sub(r'const BUILDINGS = \[[\s\S]*?\];', new_buildings, html)
html = re.sub(r'function renderYardMap\(stats\) \{[\s\S]*?\n\}', lambda m: new_render, html)

with open('beacon_yard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. File size:', len(html.encode('utf-8')), 'bytes')
