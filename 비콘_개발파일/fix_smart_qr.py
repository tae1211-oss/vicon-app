with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
# 1. handleProdQR → async + 로딩 표시 후 await renderDeckForm
# ══════════════════════════════════════════════════════════
old_handleProdQR = """function handleProdQR(data) {
  if (data.type !== 'job_order') { toast('작업지시서 QR이 아닙니다.'); return; }
  pendingProd = data;
  document.getElementById('prod-entry-card').style.display = 'block';
  document.getElementById('prod-entry-title').textContent =
    (data.site || '') + (data.company ? ' (' + data.company + ')' : '');
  renderDeckForm(data);
}"""

new_handleProdQR = """async function handleProdQR(data) {
  if (data.type !== 'job_order') { toast('작업지시서 QR이 아닙니다.'); return; }
  pendingProd = data;
  document.getElementById('prod-entry-card').style.display = 'block';
  document.getElementById('prod-entry-title').textContent =
    (data.site || '') + (data.company ? ' (' + data.company + ')' : '');
  document.getElementById('prod-entry-body').innerHTML =
    '<div class="loading"><span class="spinner"></span>기존 생산 확인 중…</div>';
  await renderDeckForm(data);
}"""

cnt1 = html.count(old_handleProdQR)
print(f'handleProdQR: {cnt1}')
html = html.replace(old_handleProdQR, new_handleProdQR)

# ══════════════════════════════════════════════════════════
# 2. renderDeckForm → async + 이미 생산된 팩 자동 해제
# ══════════════════════════════════════════════════════════
old_render_start = "function renderDeckForm(data) {"
old_render_end   = "  document.getElementById('prod-entry-body').innerHTML = html;\n  updateShiftUI();\n  updateProdTotals();\n}"

new_render = r"""async function renderDeckForm(data) {
  const packFrom = data.pack_from ?? data.pf ?? 0;
  const packTo   = data.pack_to   ?? data.pt ?? 0;
  const details  = data.d || [];
  const packs = [];
  for (let i = packFrom; i <= packTo; i++) {
    const idx = i - packFrom;
    packs.push({
      n: i,
      s: details[idx] != null ? details[idx][0] : null,
      a: details[idx] != null ? details[idx][1] : null
    });
  }
  pendingProd._packs = packs;

  // ── 이미 생산된 팩 조회 ──────────────────────────────────
  const donePacks = new Set();
  const doneInfo  = {};   // pack_no -> {date, shift, machine}
  if (db && (data.company || data.site)) {
    try {
      const snap = await db.collection('production_deck')
        .where('company',  '==', data.company  || '')
        .where('site',     '==', data.site      || '')
        .where('req_code', '==', data.req_code  || '')
        .get();
      const cutoff = new Date();
      cutoff.setMonth(cutoff.getMonth() - 4);
      const cutoffStr = cutoff.toISOString().slice(0, 10);
      snap.forEach(doc => {
        const d = doc.data();
        if ((d.date || '9999') >= cutoffStr) {
          (d.packs || []).forEach(p => {
            donePacks.add(p.pack_no);
            if (!doneInfo[p.pack_no]) {
              doneInfo[p.pack_no] = { date: d.date||'', shift: d.shift||'', machine: d.machine||'' };
            }
          });
        }
      });
    } catch(e) { /* 조회 실패 시 무시 */ }
  }

  const defDate   = getProductionDate();
  const defShift  = getDefaultShift();
  const hasDetail = packs.some(p => p.s !== null);
  const doneCount = packs.filter(p => donePacks.has(p.n)).length;

  let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">'
    + '<div class="form-group" style="margin:0"><label>생산 일자</label>'
    + '<input type="date" id="prod-date" value="' + defDate + '" style="width:100%;border:1.5px solid #cfd8dc;border-radius:8px;padding:8px;font-size:.85rem;font-family:inherit"></div>'
    + '<div class="form-group" style="margin:0"><label>호기</label>'
    + '<select id="prod-machine" style="width:100%;border:1.5px solid #cfd8dc;border-radius:8px;padding:8px;font-size:.85rem;background:#fff;font-family:inherit">'
    + '<option>1호기</option><option>2호기</option><option>3호기</option><option>4호기</option><option>탈형</option>'
    + '</select></div></div>'
    + '<div class="form-group" style="margin-bottom:12px"><label>주간 / 야간</label>'
    + '<div style="display:flex;gap:8px">'
    + '<label id="lbl-shift-day" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:10px;border:2px solid #cfd8dc;border-radius:10px;cursor:pointer;font-size:.9rem;transition:border-color .15s">'
    + '<input type="radio" name="prod-shift" value="주간" ' + (defShift==='주간'?'checked':'') + ' onchange="updateShiftUI()"> 🌤️ 주간</label>'
    + '<label id="lbl-shift-night" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:10px;border:2px solid #cfd8dc;border-radius:10px;cursor:pointer;font-size:.9rem;transition:border-color .15s">'
    + '<input type="radio" name="prod-shift" value="야간" ' + (defShift==='야간'?'checked':'') + ' onchange="updateShiftUI()"> 🌙 야간</label>'
    + '</div></div>'
    + '<div style="font-size:.78rem;color:#546e7a;margin-bottom:8px">'
    + '<strong>의뢰번호:</strong> ' + esc(data.req_code || '-')
    + ' &nbsp;|  총 ' + packs.length + '패킹'
    + (hasDetail ? '' : '<span style="color:#f57f17"> (장수·면적 정보 없음)</span>')
    + '</div>';

  if (doneCount > 0) {
    html += '<div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:8px;padding:8px 12px;margin-bottom:8px;font-size:.78rem;color:#2e7d32">'
      + '✅ 이미 생산 완료 ' + doneCount + '패킹은 자동 해제되었습니다 ('
      + packs.filter(p=>donePacks.has(p.n)).map(p=>p.n).join(', ') + '번)'
      + '</div>';
  }

  html += '<div class="pack-controls">'
    + '<button class="btn btn-sm btn-secondary" onclick="prodPackSelAll(true)">전체선택</button>'
    + '<button class="btn btn-sm btn-secondary" onclick="prodPackSelAll(false)">전체해제</button>'
    + '</div>'
    + '<div style="border:1px solid #e0e0e0;border-radius:10px;margin:6px 0;max-height:280px;overflow-y:auto">';

  packs.forEach(p => {
    const done = donePacks.has(p.n);
    const info = doneInfo[p.n];
    const infoTxt = done && info ? (info.date + ' ' + info.shift + ' ' + info.machine) : '';
    html += '<div class="pack-detail-row" style="' + (done ? 'opacity:.55;background:#f1f8e9' : '') + '">'
      + '<label style="display:flex;align-items:center;gap:8px;flex:1;cursor:' + (done ? 'default' : 'pointer') + '">'
      + '<input type="checkbox" class="prod-cb" value="' + p.n + '" '
      + (done ? '' : 'checked ') + 'onchange="updateProdTotals()">'
      + '<span style="font-weight:600;min-width:38px">' + p.n + '</span>';
    if (done) {
      html += '<span style="font-size:.7rem;color:#388e3c">✅ ' + esc(infoTxt) + '</span>';
    } else if (p.s !== null) {
      html += '<span class="pack-detail-badge"><span>' + p.s + '장</span><span>' + p.a + '㎡</span></span>';
    } else {
      html += '<span style="font-size:.72rem;color:#ccc">-</span>';
    }
    html += '</label></div>';
  });

  html += '</div>'
    + '<div class="prod-summary-bar" id="prod-summary">'
    + '<div class="prod-summary-item"><div class="pval" id="sum-packs">0</div><div class="plbl">선택 패킹</div></div>'
    + '<div class="prod-summary-item"><div class="pval" id="sum-sheets">-</div><div class="plbl">총 장수</div></div>'
    + '<div class="prod-summary-item"><div class="pval" id="sum-area">-</div><div class="plbl">총 면적(㎡)</div></div>'
    + '</div>'
    + '<button class="btn btn-success btn-full" style="margin-top:12px" onclick="submitProdEntry()">✅ 생산 등록</button>';

  document.getElementById('prod-entry-body').innerHTML = html;
  updateShiftUI();
  updateProdTotals();
}"""

count2 = 0
pos = 0
while True:
    idx_start = html.find(old_render_start, pos)
    if idx_start == -1:
        break
    idx_end = html.find(old_render_end, idx_start)
    if idx_end == -1:
        break
    idx_end += len(old_render_end)
    html = html[:idx_start] + new_render + html[idx_end:]
    pos = idx_start + len(new_render)
    count2 += 1

print(f'renderDeckForm: {count2}')

# ══════════════════════════════════════════════════════════
# 3. handleInbound (job_order) → 재고 중복 체크 추가
# ══════════════════════════════════════════════════════════
old_inbound = """  // ── job_order QR ──
  if (data.type === 'job_order') {
    titleEl.textContent = `📥 입고: ${data.site}`;
    const packs = [];
    for (let i = data.pack_from; i <= data.pack_to; i++) packs.push(i);
    pendingIB = {...data, selPacks: [...packs]};

    let html = `<div style="font-size:.83rem;margin-bottom:10px;line-height:1.6">
      <strong>${esc(data.site)}</strong><br>
      <span style="color:#546e7a">${esc(data.company)}</span><br>
      <span style="color:#0d47a1">패킹 ${data.pack_from}~${data.pack_to} (${packs.length}개)</span>
    </div>
    <div class="pack-controls">
      <button class="btn btn-sm btn-secondary" onclick="packSelAll('ib',true)">전체선택</button>
      <button class="btn btn-sm btn-secondary" onclick="packSelAll('ib',false)">전체해제</button>
    </div>
    <div class="pack-grid" id="ib-pack-grid">`;
    packs.forEach(p => {
      html += `<label class="pack-item checked">
        <input type="checkbox" class="ib-cb" value="${p}" checked onchange="syncSel('ib')">
        <span>${p}</span>
      </label>`;
    });
    html += `</div>
    <button class="btn btn-success btn-full" style="margin-top:12px" onclick="openZonePicker()">
      📍 구역 선택 후 적재
    </button>`;
    bodyEl.innerHTML = html;
    return;
  }"""

new_inbound = """  // ── job_order QR ──
  if (data.type === 'job_order') {
    titleEl.textContent = '📥 입고: ' + data.site;
    const packs = [];
    for (let i = data.pack_from; i <= data.pack_to; i++) packs.push(i);

    // ── 현재 재고에서 이미 입고된 팩 조회 ──────────────────
    bodyEl.innerHTML = '<div class="loading"><span class="spinner"></span>재고 확인 중…</div>';
    const stockSet = new Set();
    const stockZone = {};
    if (db) {
      try {
        const docId = makeDocId(data.company, data.site);
        const doc = await db.collection('inventory').doc(docId).get();
        if (doc.exists) {
          (doc.data().packs || []).filter(p => !p.shipped).forEach(p => {
            stockSet.add(p.pack_no);
            stockZone[p.pack_no] = p.zone || '';
          });
        }
      } catch(e) {}
    }

    const alreadyIn = packs.filter(p => stockSet.has(p));
    const newPacks  = packs.filter(p => !stockSet.has(p));
    pendingIB = {...data, selPacks: [...newPacks]};

    let html = '<div style="font-size:.83rem;margin-bottom:10px;line-height:1.6">'
      + '<strong>' + esc(data.site) + '</strong><br>'
      + '<span style="color:#546e7a">' + esc(data.company) + '</span><br>'
      + '<span style="color:#0d47a1">패킹 ' + data.pack_from + '~' + data.pack_to + ' (' + packs.length + '개)</span>'
      + '</div>';

    if (alreadyIn.length > 0) {
      html += '<div style="background:#fff3e0;border:1px solid #ffb74d;border-radius:8px;padding:10px 12px;margin-bottom:10px;font-size:.78rem">'
        + '<div style="font-weight:700;color:#e65100;margin-bottom:4px">⚠️ 이미 재고 있음 (' + alreadyIn.length + '개)</div>'
        + '<div style="color:#555;line-height:1.7">';
      const byZoneWarn = {};
      alreadyIn.forEach(p => { const z = stockZone[p]||'?'; (byZoneWarn[z]=byZoneWarn[z]||[]).push(p); });
      Object.entries(byZoneWarn).forEach(([z,ps]) => {
        html += z + '구역: ' + ps.join(', ') + '번<br>';
      });
      html += '</div>'
        + '<div style="margin-top:6px;color:#bf360c">이미 입고된 패킹은 자동 해제되었습니다. 필요 시 직접 체크하세요.</div>'
        + '</div>';
    }

    html += '<div class="pack-controls">'
      + '<button class="btn btn-sm btn-secondary" onclick="packSelAll(\'ib\',true)">전체선택</button>'
      + '<button class="btn btn-sm btn-secondary" onclick="packSelAll(\'ib\',false)">전체해제</button>'
      + '</div>'
      + '<div class="pack-grid" id="ib-pack-grid">';

    packs.forEach(p => {
      const inStock = stockSet.has(p);
      const zone = stockZone[p];
      html += '<label class="pack-item' + (inStock ? '' : ' checked') + '" style="' + (inStock ? 'opacity:.5' : '') + '">'
        + '<input type="checkbox" class="ib-cb" value="' + p + '" '
        + (inStock ? '' : 'checked ') + 'onchange="syncSel(\'ib\')">'
        + '<span>' + p + (inStock && zone ? '<small style="opacity:.7;font-size:.65em;display:block">' + zone + '</small>' : '') + (inStock ? '📦' : '') + '</span>'
        + '</label>';
    });

    html += '</div>'
      + '<button class="btn btn-success btn-full" style="margin-top:12px" onclick="openZonePicker()">'
      + '📍 구역 선택 후 적재'
      + '</button>';
    bodyEl.innerHTML = html;
    return;
  }"""

cnt3 = html.count(old_inbound)
print(f'handleInbound: {cnt3}')
html = html.replace(old_inbound, new_inbound)

# handleInbound 를 async 로 변경
old_inbound_sig  = 'async function handleInbound(data) {'
# already async, check:
print(f'already async: {html.count(old_inbound_sig)}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('async renderDeckForm:', html.count('async function renderDeckForm'))
print('async handleProdQR:', html.count('async function handleProdQR'))
