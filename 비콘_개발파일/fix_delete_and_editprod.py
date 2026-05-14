with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
# 1) 모달 HTML: 패킹별 삭제 UI로 교체
# ══════════════════════════════════════════════════════════
old_modal = """<div class="overlay" id="ov-delete-doc">
  <div class="modal" style="max-height:85vh;overflow-y:auto">
    <div class="modal-handle"></div>
    <div class="modal-title">🗑️ 재고 삭제</div>
    <div style="font-size:.78rem;color:#c62828;background:#ffebee;border-radius:8px;padding:8px 10px;margin-bottom:12px">삭제하면 모든 입출고 이력이 사라지며 복구할 수 없습니다.</div>
    <div id="del-list"></div>
    <button class="btn btn-secondary btn-full" style="margin-top:10px" onclick="closeOv('ov-delete-doc')">닫기</button>
  </div>
</div>"""

new_modal = """<div class="overlay" id="ov-delete-doc">
  <div class="modal" style="max-height:90vh;overflow-y:auto">
    <div class="modal-handle"></div>
    <div class="modal-title">🗑️ 패킹별 재고 삭제</div>
    <div style="font-size:.78rem;color:#c62828;background:#ffebee;border-radius:8px;padding:8px 10px;margin-bottom:10px">선택한 패킹의 입출고 이력이 삭제됩니다. 되돌릴 수 없습니다.</div>
    <div style="display:flex;gap:6px;margin-bottom:10px">
      <button class="btn btn-sm btn-secondary" style="flex:1" onclick="delSelAll(true)">전체선택</button>
      <button class="btn btn-sm btn-secondary" style="flex:1" onclick="delSelAll(false)">전체해제</button>
      <button class="btn btn-danger" style="flex:1;font-size:.82rem;padding:7px 4px;border-radius:8px" onclick="deleteSelectedPacks()">선택 삭제</button>
    </div>
    <div id="del-list"></div>
    <button class="btn btn-secondary btn-full" style="margin-top:10px" onclick="closeOv('ov-delete-doc')">닫기</button>
  </div>
</div>"""

cnt_modal = html.count(old_modal)
print(f'modal: {cnt_modal}')
html = html.replace(old_modal, new_modal)

# ══════════════════════════════════════════════════════════
# 2) JS: openDeleteDoc 함수 교체 (패킹 체크박스 목록)
# ══════════════════════════════════════════════════════════
old_open = """async function openDeleteDoc() {
  if (!db) { toast('Firebase를 연결하세요.'); return; }
  const listEl = document.getElementById('del-list');
  listEl.innerHTML = '<div class="loading"><span class="spinner"></span>로딩 중…</div>';
  openOv('ov-delete-doc');
  try {
    const snap = await db.collection('inventory').get();
    if (snap.empty) { listEl.innerHTML = '<div class="alert alert-info">재고 데이터가 없습니다.</div>'; return; }
    const items = [];
    snap.forEach(doc => {
      const d = doc.data();
      const active  = (d.packs||[]).filter(p=>!p.shipped).length;
      const shipped = (d.packs||[]).filter(p=>p.shipped).length;
      items.push({docId: doc.id, site: d.site||'', company: d.company||'', active, shipped});
    });
    items.sort((a,b) => a.site.localeCompare(b.site));
    listEl.innerHTML = items.map(it => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0">
        <div style="flex:1;min-width:0">
          <div style="font-weight:700;font-size:.85rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${esc(it.site)}</div>
          <div style="font-size:.75rem;color:#78909c">${esc(it.company)}</div>
          <div style="font-size:.72rem;color:#90a4ae;margin-top:2px">재고 ${it.active}패킹 · 출고이력 ${it.shipped}패킹</div>
        </div>
        <button class="btn btn-danger btn-sm" style="margin-left:10px;flex-shrink:0" onclick="deleteDoc('${esc(it.docId)}','${esc(it.site)}')">삭제</button>
      </div>`).join('');
  } catch(e) { listEl.innerHTML = `<div class="alert alert-error">${e.message}</div>`; }
}"""

new_open = r"""async function openDeleteDoc() {
  if (!db) { toast('Firebase를 연결하세요.'); return; }
  const listEl = document.getElementById('del-list');
  listEl.innerHTML = '<div class="loading"><span class="spinner"></span>로딩 중…</div>';
  openOv('ov-delete-doc');
  try {
    const snap = await db.collection('inventory').get();
    if (snap.empty) { listEl.innerHTML = '<div class="alert alert-info">재고 데이터가 없습니다.</div>'; return; }
    const items = [];
    snap.forEach(doc => {
      const d = doc.data();
      items.push({ docId: doc.id, site: d.site||'', company: d.company||'', packs: d.packs||[] });
    });
    items.sort((a,b) => a.site.localeCompare(b.site));
    listEl.innerHTML = items.map(it => {
      const activeCnt  = it.packs.filter(p=>!p.shipped).length;
      const shippedCnt = it.packs.filter(p=> p.shipped).length;
      const packRows = it.packs
        .slice()
        .sort((a,b) => (+a.pack_no||0) - (+b.pack_no||0))
        .map(p => {
          const statusLbl = p.shipped
            ? '<span style="color:#90a4ae;font-size:.68rem;margin-left:3px">출고됨</span>'
            : '<span style="color:#2e7d32;font-size:.68rem;margin-left:3px">재고</span>';
          const zoneLbl = p.zone
            ? '<span style="color:#546e7a;font-size:.68rem;margin-left:4px">[' + esc(p.zone) + ']</span>'
            : '';
          return '<label style="display:flex;align-items:center;gap:8px;padding:6px 8px;border-bottom:1px solid #f5f5f5;cursor:pointer">'
            + '<input type="checkbox" class="del-pack-cb" data-doc="' + esc(it.docId) + '" data-pack="' + p.pack_no + '" style="width:17px;height:17px;flex-shrink:0;accent-color:#c62828">'
            + '<span style="font-size:.82rem;flex:1"><strong>' + p.pack_no + '번</strong>' + zoneLbl + statusLbl + '</span>'
            + '</label>';
        }).join('');
      return '<div style="margin-bottom:12px;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden">'
        + '<div style="background:#f5f5f5;padding:8px 10px;display:flex;align-items:center;justify-content:space-between">'
        + '<div><div style="font-weight:700;font-size:.85rem">' + esc(it.site) + '</div>'
        + '<div style="font-size:.72rem;color:#78909c">' + esc(it.company) + ' · 재고 ' + activeCnt + '패킹 · 출고 ' + shippedCnt + '패킹</div></div>'
        + '<div style="display:flex;gap:4px;flex-shrink:0">'
        + '<button class="btn btn-sm btn-secondary" style="font-size:.68rem;padding:3px 7px" onclick="delSiteSelAll(\'' + esc(it.docId) + '\',true)">전체선택</button>'
        + '<button class="btn btn-sm btn-secondary" style="font-size:.68rem;padding:3px 7px" onclick="delSiteSelAll(\'' + esc(it.docId) + '\',false)">해제</button>'
        + '</div></div>'
        + '<div style="padding:0">' + packRows + '</div>'
        + '</div>';
    }).join('');
  } catch(e) { listEl.innerHTML = '<div class="alert alert-error">' + e.message + '</div>'; }
}"""

cnt_open = html.count(old_open)
print(f'openDeleteDoc: {cnt_open}')
html = html.replace(old_open, new_open)

# ══════════════════════════════════════════════════════════
# 3) JS: deleteDoc 함수 → 새 3개 함수로 교체
# ══════════════════════════════════════════════════════════
old_del = """function deleteDoc(docId, site) {
  showConfirm('재고 삭제 확인',
    `"${site}" 의 모든 재고 및 입출고 이력을 삭제합니다.\\n\\n되돌릴 수 없습니다. 계속하시겠습니까?`,
    async () => {
      try {
        await db.collection('inventory').doc(docId).delete();
        toast('삭제 완료: ' + site);
        refreshMap();
        if (document.getElementById('page-inventory').classList.contains('active')) loadInventory();
        await openDeleteDoc();
      } catch(e) { toast('삭제 실패: ' + e.message); }
    }
  );
}"""

new_del = """function delSelAll(checked) {
  document.querySelectorAll('.del-pack-cb').forEach(cb => cb.checked = checked);
}

function delSiteSelAll(docId, checked) {
  document.querySelectorAll('.del-pack-cb[data-doc="' + docId + '"]').forEach(cb => cb.checked = checked);
}

async function deleteSelectedPacks() {
  const sel = [...document.querySelectorAll('.del-pack-cb:checked')];
  if (!sel.length) { toast('삭제할 패킹을 선택하세요.'); return; }
  const byDoc = {};
  sel.forEach(cb => {
    const docId  = cb.dataset.doc;
    const packNo = +cb.dataset.pack;
    if (!byDoc[docId]) byDoc[docId] = [];
    byDoc[docId].push(packNo);
  });
  const total = sel.length;
  if (!confirm('선택한 ' + total + '개 패킹을 삭제합니다.\\n되돌릴 수 없습니다. 계속하시겠습니까?')) return;
  try {
    for (const [docId, packNos] of Object.entries(byDoc)) {
      const snap = await db.collection('inventory').doc(docId).get();
      if (!snap.exists) continue;
      const packSet = new Set(packNos);
      const remaining = (snap.data().packs||[]).filter(p => !packSet.has(+p.pack_no));
      if (remaining.length === 0) {
        await db.collection('inventory').doc(docId).delete();
      } else {
        await db.collection('inventory').doc(docId).update({ packs: remaining });
      }
    }
    toast('✅ ' + total + '개 패킹 삭제 완료');
    refreshMap();
    if (document.getElementById('page-inventory').classList.contains('active')) loadInventory();
    await openDeleteDoc();
  } catch(e) { toast('삭제 실패: ' + e.message); }
}"""

cnt_del = html.count(old_del)
print(f'deleteDoc: {cnt_del}')
html = html.replace(old_del, new_del)

# ══════════════════════════════════════════════════════════
# 4) JS: openEditProd → async + Firestore fallback
# ══════════════════════════════════════════════════════════
old_edit = """// ── 생산기록 수정 (체크박스 방식) ───────────────────────
function openEditProd(docId, year, month) {
  const r = (window._prodRecords||[]).find(r => r.id === docId);
  if (!r) { toast('기록을 찾을 수 없습니다.'); return; }"""

new_edit = """// ── 생산기록 수정 (체크박스 방식) ───────────────────────
async function openEditProd(docId, year, month) {
  let r = (window._prodRecords||[]).find(r => r.id === docId);
  if (!r) {
    if (!db) { toast('Firebase 미연결'); return; }
    try {
      const snap = await db.collection('production_deck').doc(docId).get();
      if (!snap.exists) { toast('기록을 찾을 수 없습니다.'); return; }
      r = { id: snap.id, ...snap.data() };
    } catch(e) { toast('기록 로드 실패: ' + e.message); return; }
  }"""

cnt_edit = html.count(old_edit)
print(f'openEditProd: {cnt_edit}')
html = html.replace(old_edit, new_edit)

# ══════════════════════════════════════════════════════════
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('delSelAll check:',        html.count('function delSelAll('))
print('deleteSelectedPacks:',    html.count('function deleteSelectedPacks('))
print('openEditProd async:',     html.count('async function openEditProd('))
print('del-pack-cb check:',      html.count('del-pack-cb'))
