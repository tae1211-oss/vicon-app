with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
# 1. 재고수불 백업 카드 HTML 추가 (데이터 관리 카드 바로 뒤)
# ══════════════════════════════════════════════════════════
old_inv_admin_end = """      <button class="btn btn-danger btn-full" onclick="openDeleteDoc()">🗑️ 재고 삭제</button>
    </div>
  </div>
</div>

<!-- ════════════════════ MODALS ════════════════════ -->"""

new_inv_admin_end = """      <button class="btn btn-danger btn-full" onclick="openDeleteDoc()">🗑️ 재고 삭제</button>
    </div>
    <!-- 재고수불 백업 카드 -->
    <div class="card" style="margin-top:12px;border:1.5px solid #1565c0">
      <div class="card-title" style="color:#1565c0">💾 재고 데이터 백업</div>
      <div style="font-size:.78rem;color:#546e7a;margin-bottom:10px">전체 재고기록을 JSON 파일로 저장합니다.<br>삭제 전이나 정기적으로 백업하세요.</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
        <div>
          <label style="font-size:.75rem;font-weight:700;color:#546e7a;display:block;margin-bottom:3px">시작 날짜 (선택)</label>
          <input type="date" id="inv-backup-from" style="width:100%;padding:8px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;box-sizing:border-box"/>
        </div>
        <div>
          <label style="font-size:.75rem;font-weight:700;color:#546e7a;display:block;margin-bottom:3px">끝 날짜 (선택)</label>
          <input type="date" id="inv-backup-to" style="width:100%;padding:8px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;box-sizing:border-box"/>
        </div>
      </div>
      <div style="font-size:.72rem;color:#90a4ae;margin-bottom:10px">※ 날짜를 비우면 전체 데이터를 백업합니다.</div>
      <button id="inv-backup-btn" class="btn btn-full" onclick="backupInventory()"
        style="background:#1565c0;color:#fff;font-weight:700">💾 재고 데이터 백업 다운로드</button>
      <div id="inv-backup-status" style="font-size:.8rem;margin-top:8px;min-height:16px;color:#1565c0"></div>
    </div>
  </div>
</div>

<!-- ════════════════════ MODALS ════════════════════ -->"""

cnt = html.count(old_inv_admin_end)
print(f'inv_admin_end: {cnt}')
html = html.replace(old_inv_admin_end, new_inv_admin_end)

# ══════════════════════════════════════════════════════════
# 2. 기존 backupData() → 공통 함수 + 개별 래퍼로 교체
# ══════════════════════════════════════════════════════════
old_backup_fn = """async function backupData() {
  if (!db) { toast('Firebase 미연결'); return; }
  const btn    = document.getElementById('backup-btn');
  const status = document.getElementById('backup-status');
  btn.disabled = true; btn.textContent = '백업 중...';
  status.textContent = '데이터 불러오는 중...';
  try {
    let query = db.collection('production_deck');
    const from = document.getElementById('backup-from').value;
    const to   = document.getElementById('backup-to').value;
    if (from) query = query.where('date', '>=', from);
    if (to)   query = query.where('date', '<=', to);
    const snap = await query.get();
    const records = [];
    snap.forEach(doc => records.push({ id: doc.id, ...doc.data() }));

    const today = new Date().toISOString().slice(0,10);
    const suffix = (from||to) ? `_${from||''}~${to||''}` : '_전체';
    const filename = `생산기록_백업_${today}${suffix}.json`;

    const json = JSON.stringify({ exported_at: new Date().toISOString(), count: records.length, records }, null, 2);
    const blob = new Blob(['\\uFEFF'+json], { type: 'application/json;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);

    status.innerHTML = `<span style="color:#2e7d32">✅ ${records.length}건 백업 완료</span>`;
    toast(`✅ ${records.length}건 백업 완료`);
  } catch(e) {
    status.textContent = '백업 실패: ' + e.message;
    toast('백업 실패: ' + e.message);
  } finally {
    btn.disabled = false; btn.textContent = '💾 데이터 백업 다운로드';
  }
}"""

new_backup_fn = """// ── 공통 백업 엔진 ──────────────────────────────────────
// cfg: { collection, label, dateField, fromId, toId, btnId, statusId, btnLabel }
async function _backupEngine(cfg) {
  if (!db) { toast('Firebase 미연결'); return; }
  const btn    = document.getElementById(cfg.btnId);
  const status = document.getElementById(cfg.statusId);
  const origLabel = btn.textContent;
  btn.disabled = true; btn.textContent = '백업 중...';
  status.textContent = '데이터 불러오는 중...';
  try {
    let query = db.collection(cfg.collection);
    const from = cfg.fromId ? document.getElementById(cfg.fromId).value : '';
    const to   = cfg.toId   ? document.getElementById(cfg.toId).value   : '';
    if (from && cfg.dateField) query = query.where(cfg.dateField, '>=', from);
    if (to   && cfg.dateField) query = query.where(cfg.dateField, '<=', to);
    const snap = await query.get();
    const records = [];
    snap.forEach(doc => records.push({ id: doc.id, ...doc.data() }));

    const today  = new Date().toISOString().slice(0,10);
    const suffix = (from||to) ? `_${from||''}~${to||''}` : '_전체';
    const filename = `${cfg.label}_백업_${today}${suffix}.json`;

    const json = JSON.stringify({ exported_at: new Date().toISOString(), collection: cfg.collection, count: records.length, records }, null, 2);
    const blob = new Blob([json], { type: 'application/json;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);

    status.innerHTML = `<span style="color:#2e7d32">✅ ${records.length}건 백업 완료</span>`;
    toast(`✅ [${cfg.label}] ${records.length}건 백업 완료`);
  } catch(e) {
    status.textContent = '백업 실패: ' + e.message;
    toast('백업 실패: ' + e.message);
  } finally {
    btn.disabled = false; btn.textContent = origLabel;
  }
}

// ── 생산수불 백업 ─────────────────────────────────────────
function backupData() {
  _backupEngine({ collection:'production_deck', label:'생산기록', dateField:'date',
    fromId:'backup-from', toId:'backup-to', btnId:'backup-btn', statusId:'backup-status' });
}

// ── 재고수불 백업 ─────────────────────────────────────────
function backupInventory() {
  _backupEngine({ collection:'inventory', label:'재고기록', dateField:'in_date',
    fromId:'inv-backup-from', toId:'inv-backup-to', btnId:'inv-backup-btn', statusId:'inv-backup-status' });
}"""

# BOM 문자가 파이썬 raw string에서 문제가 될 수 있으므로 직접 찾기
cnt = html.count('async function backupData()')
print(f'backupData fn: {cnt}')

if cnt > 0:
    start = html.find('async function backupData()')
    end   = html.find('\n}', start) + 2  # closing brace
    html  = html[:start] + new_backup_fn + html[end:]
    print('backupData replaced')
else:
    print('WARNING: backupData not found')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('_backupEngine:', '_backupEngine' in html)
print('backupInventory:', 'backupInventory' in html)
print('inv-backup-btn:', 'inv-backup-btn' in html)
print('재고 데이터 백업:', '재고 데이터 백업' in html)
