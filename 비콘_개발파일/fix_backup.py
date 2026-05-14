with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. 백업 카드 HTML 추가 (일괄삭제 카드 바로 뒤) ──────────
old_admin_end = """        <button id="batch-del-btn" class="btn btn-danger btn-full" onclick="executeBatchDelete()" style="display:none">🗑️ 일괄 삭제 실행</button>
      </div>
    </div>"""

new_admin_end = """        <button id="batch-del-btn" class="btn btn-danger btn-full" onclick="executeBatchDelete()" style="display:none">🗑️ 일괄 삭제 실행</button>
      </div>
      <!-- 데이터 백업 카드 -->
      <div class="card" style="margin-top:12px;border:1.5px solid #1565c0">
        <div class="card-title" style="color:#1565c0">💾 데이터 백업</div>
        <div style="font-size:.78rem;color:#546e7a;margin-bottom:10px">전체 생산기록을 JSON 파일로 저장합니다.<br>삭제 전이나 월말에 정기적으로 백업하세요.</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
          <div>
            <label style="font-size:.75rem;font-weight:700;color:#546e7a;display:block;margin-bottom:3px">시작 날짜 (선택)</label>
            <input type="date" id="backup-from" style="width:100%;padding:8px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;box-sizing:border-box"/>
          </div>
          <div>
            <label style="font-size:.75rem;font-weight:700;color:#546e7a;display:block;margin-bottom:3px">끝 날짜 (선택)</label>
            <input type="date" id="backup-to" style="width:100%;padding:8px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;box-sizing:border-box"/>
          </div>
        </div>
        <div style="font-size:.72rem;color:#90a4ae;margin-bottom:10px">※ 날짜를 비우면 전체 데이터를 백업합니다.</div>
        <button id="backup-btn" class="btn btn-full" onclick="backupData()"
          style="background:#1565c0;color:#fff;font-weight:700">💾 데이터 백업 다운로드</button>
        <div id="backup-status" style="font-size:.8rem;margin-top:8px;min-height:16px;color:#1565c0"></div>
      </div>
    </div>"""

cnt = html.count(old_admin_end)
print(f'admin_end: {cnt}')
html = html.replace(old_admin_end, new_admin_end)

# ── 2. backupData JS 함수 추가 (executeBatchDelete 바로 뒤) ──
old_after_batch = """// ── 생산기록 수정 (체크박스 방식) ───────────────────────"""

new_after_batch = """// ── 데이터 백업 ─────────────────────────────────────────
async function backupData() {
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
    const blob = new Blob(['﻿'+json], { type: 'application/json;charset=utf-8' });
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
}

// ── 생산기록 수정 (체크박스 방식) ───────────────────────"""

cnt = html.count(old_after_batch)
print(f'after_batch: {cnt}')
html = html.replace(old_after_batch, new_after_batch, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('backupData:', 'backupData' in html)
print('백업 카드:', '데이터 백업 다운로드' in html)
