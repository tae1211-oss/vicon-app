with open('index.html.html', 'r', encoding='utf-8') as f:
    html = f.read()

all_js = r"""
// ── 생산기록 일괄 삭제 (관리자) ─────────────────────────
function previewBatchDelete() {
  const ym   = document.getElementById('batch-del-month').value;
  const date = document.getElementById('batch-del-date').value;
  const mach = document.getElementById('batch-del-machine').value.trim();
  const shift= document.getElementById('batch-del-shift').value;
  const prev = document.getElementById('batch-del-preview');
  const btn  = document.getElementById('batch-del-btn');
  if (!ym && !date && !mach && !shift) {
    prev.textContent = '⚠️ 조건을 하나 이상 입력하세요.';
    btn.style.display = 'none'; return;
  }
  const matched = (window._prodRecords||[]).filter(r => {
    if (ym   && !(r.date||'').startsWith(ym))       return false;
    if (date && r.date !== date)                     return false;
    if (mach && String(r.machine||'') !== mach)      return false;
    if (shift && r.shift !== shift)                  return false;
    return true;
  });
  window._batchDeleteTargets = matched;
  if (!matched.length) {
    prev.innerHTML = '<span style="color:#e53935">조건에 맞는 기록이 없습니다.</span>';
    btn.style.display = 'none';
  } else {
    prev.innerHTML = `<span style="color:#1565c0;font-weight:700">${matched.length}건</span> 이 검색되었습니다.`;
    btn.style.display = 'block';
  }
}

async function executeBatchDelete() {
  if (!db) { toast('Firebase 미연결'); return; }
  const targets = window._batchDeleteTargets || [];
  if (!targets.length) { toast('삭제할 기록 없음'); return; }
  if (!confirm(`⚠️ 일괄 삭제 확인\n\n${targets.length}건을 삭제합니다.\n삭제 후에는 복구할 수 없습니다.\n\n계속하시겠습니까?`)) return;
  const btn = document.getElementById('batch-del-btn');
  btn.disabled = true; btn.textContent = '삭제 중...';
  try {
    const CHUNK = 400;
    for (let i = 0; i < targets.length; i += CHUNK) {
      const batch = db.batch();
      targets.slice(i, i+CHUNK).forEach(r => batch.delete(db.collection('production_deck').doc(r.id)));
      await batch.commit();
    }
    const ids = new Set(targets.map(r => r.id));
    window._prodRecords = (window._prodRecords||[]).filter(r => !ids.has(r.id));
    window._batchDeleteTargets = [];
    document.getElementById('batch-del-preview').innerHTML = '<span style="color:#2e7d32">✅ 삭제 완료</span>';
    btn.style.display = 'none';
    toast(`✅ ${targets.length}건 삭제 완료`);
    loadProdStat();
  } catch(e) {
    toast('삭제 실패: ' + e.message);
  } finally {
    btn.disabled = false; btn.textContent = '🗑️ 일괄 삭제 실행';
  }
}

// ── 생산기록 수정 ─────────────────────────────────────────
function openEditProd(docId, year, month) {
  const r = (window._prodRecords||[]).find(r => r.id === docId);
  if (!r) { toast('기록을 찾을 수 없습니다.'); return; }
  document.getElementById('edit-prod-id').value      = docId;
  document.getElementById('edit-prod-year').value    = year;
  document.getElementById('edit-prod-month').value   = month;
  document.getElementById('edit-prod-date').value    = r.date    || '';
  document.getElementById('edit-prod-shift').value   = r.shift   || '주간';
  document.getElementById('edit-prod-machine').value = r.machine || '';
  document.getElementById('edit-prod-site').value    = r.site    || '';
  document.getElementById('edit-prod-reqcode').value = r.req_code|| '';
  document.getElementById('edit-prod-modal').style.display = 'flex';
}
function closeEditProd() {
  document.getElementById('edit-prod-modal').style.display = 'none';
}
async function saveEditProd() {
  if (!db) { toast('Firebase 미연결'); return; }
  const docId  = document.getElementById('edit-prod-id').value;
  const year   = document.getElementById('edit-prod-year').value;
  const month  = document.getElementById('edit-prod-month').value;
  const date   = document.getElementById('edit-prod-date').value;
  const shift  = document.getElementById('edit-prod-shift').value;
  const machine= document.getElementById('edit-prod-machine').value.trim();
  const site   = document.getElementById('edit-prod-site').value.trim();
  const reqCode= document.getElementById('edit-prod-reqcode').value.trim();
  if (!date) { toast('날짜를 입력하세요.'); return; }
  try {
    await db.collection('production_deck').doc(docId).update({date, shift, machine, site, req_code: reqCode});
    if (window._prodRecords) {
      const idx = window._prodRecords.findIndex(r => r.id === docId);
      if (idx >= 0) Object.assign(window._prodRecords[idx], {date, shift, machine, site, req_code: reqCode});
    }
    closeEditProd();
    toast('✅ 수정되었습니다.');
    showProdMonth(year, month);
  } catch(e) { toast('수정 실패: ' + e.message); }
}

// ── 작업일보 ─────────────────────────────────────────────
function openDailyReport(date, machine) {
  const allRecs = (window._prodRecords||[])
    .filter(r => r.date === date && String(r.machine||'') === String(machine||''))
    .sort((a,b) => a.shift === '주간' ? -1 : 1);
  if (!allRecs.length) { toast('해당 일자/호기 기록 없음'); return; }

  const d  = new Date(date + 'T12:00:00');
  const y  = d.getFullYear(), mo = d.getMonth()+1, dy = d.getDate();
  const dw = '일월화수목금토'[d.getDay()];
  const shift = allRecs[0].shift || '';
  const ROWS = 13;
  const pages = [];
  for (let i = 0; i < Math.max(1, Math.ceil(allRecs.length / ROWS)); i++)
    pages.push(allRecs.slice(i*ROWS, (i+1)*ROWS));

  let pagesHtml = '';
  pages.forEach((recs, pi) => {
    let rowsHtml = '', tArea = 0, tSheets = 0;
    recs.forEach(r => {
      const packs = r.packs || [];
      const nos = packs.map(p => Number(p.pack_no)).filter(n => !isNaN(n)).sort((a,b)=>a-b);
      const packStr = nos.length
        ? (nos[0]===nos[nos.length-1] ? String(nos[0]) : nos[0]+'-'+nos[nos.length-1])
        : (r.pack_count ? '('+r.pack_count+'건)' : '');
      const site = r.site||'', req = r.req_code||'';
      const area = r.total_area!=null ? (+r.total_area).toFixed(2) : '';
      const qty  = r.total_sheets!=null ? r.total_sheets : (r.pack_count||'');
      tArea += r.total_area||0;
      tSheets += r.total_sheets||r.pack_count||0;
      const combined = site+(packStr?' '+packStr:'');
      const inner = combined.length>22
        ? esc(site)+'<br><span style="font-size:8pt;color:#333">'+esc(packStr)+'</span>'
        : esc(combined);
      rowsHtml += `<tr style="height:22px">
        <td class="dr-site-td">${inner}</td>
        <td>${esc(req)}</td><td>${area}</td><td>${qty}</td>
        <td><span class="dr-chk"></span></td><td><span class="dr-chk"></span></td>
        <td style="letter-spacing:2px">&thinsp;:&thinsp;</td><td>합 / 불</td>
      </tr>`;
    });
    for (let i=recs.length; i<ROWS; i++)
      rowsHtml += `<tr style="height:22px"><td class="dr-site-td"></td><td></td><td></td><td></td>
        <td><span class="dr-chk"></span></td><td><span class="dr-chk"></span></td>
        <td style="letter-spacing:2px">&thinsp;:&thinsp;</td><td>합 / 불</td></tr>`;

    const shiftHtml = shift==='주간'
      ? '<span style="color:#c0392b;font-weight:bold">주</span>&nbsp;야'
      : '주&nbsp;<span style="color:#c0392b;font-weight:bold">야</span>';

    pagesHtml += `
    ${pi>0?'<div class="dr-page-gap"></div>':''}
    <div class="dr-page">
      <div class="dr-hrow">
        <div class="dr-title">(${esc(String(machine))})호기 데크반 작업일보</div>
        <table class="dr-stbl"><tr><th>작&nbsp;성</th><th>조 / 반장</th><th>확&nbsp;인</th></tr>
          <tr><td style="height:30px"></td><td></td><td></td></tr></table>
      </div>
      <div class="dr-dateline">${y}년 ${mo}월 ${dy}일 &nbsp;${dw}요일 &nbsp;&nbsp;(${shiftHtml}) &nbsp;&nbsp; OP :&nbsp;&nbsp;&nbsp;&nbsp; TI</div>
      <div class="dr-note">※ 라벨에 날자 기록 / 자주검사 및 박리검사 명확하게 할 것</div>
      <div class="dr-winfo">■ 작업시간 : 시작&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;~&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;종료 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ■ 작업자 이름 (&nbsp;&nbsp;&nbsp;&nbsp;명) :</div>
      <table class="dr-tbl">
        <thead><tr>
          <th rowspan="2" style="width:215px">현 장 명</th>
          <th rowspan="2" style="width:95px">의뢰번호</th>
          <th rowspan="2" style="width:58px">면 적</th>
          <th rowspan="2" style="width:48px">수 량</th>
          <th colspan="2">포장방식</th><th colspan="2">자 주 검 사</th>
        </tr><tr>
          <th style="width:42px">롤 재</th><th style="width:42px">슬리퍼</th>
          <th style="width:72px">시 간</th><th style="width:62px">합 / 불</th>
        </tr></thead>
        <tbody>${rowsHtml}
          <tr class="dr-total-row">
            <td colspan="2" style="text-align:right;padding-right:8px">합&nbsp;&nbsp;&nbsp;계</td>
            <td>${(+tArea).toFixed(2)}</td><td>${tSheets||''}</td><td colspan="4"></td>
          </tr>
        </tbody>
      </table>
      ${pages.length>1?`<div class="dr-pgnum">${pi+1} / ${pages.length}</div>`:''}
    </div>`;
  });

  document.getElementById('dr-body').innerHTML = pagesHtml;
  document.getElementById('dr-modal').style.display = 'flex';
  window._drDate = date; window._drMachine = machine;
}

function closeDailyReport() {
  document.getElementById('dr-modal').style.display = 'none';
}

async function downloadDailyReport() {
  const body = document.getElementById('dr-body');
  try {
    toast('이미지 생성 중...');
    const canvas = await html2canvas(body, {scale:2, useCORS:true, backgroundColor:'#ffffff', logging:false});
    const a = document.createElement('a');
    a.download = `작업일보_${window._drMachine}호기_${window._drDate}.png`;
    a.href = canvas.toDataURL('image/png');
    a.click();
  } catch(e) { toast('이미지 저장 실패: '+e.message); }
}

"""

anchor = """function doLogout() {
  if (!confirm('로그아웃 하시겠습니까?')) return;
  firebase.auth().signOut();
}

</script>"""

new_anchor = """function doLogout() {
  if (!confirm('로그아웃 하시겠습니까?')) return;
  firebase.auth().signOut();
}
""" + all_js + """
</script>"""

cnt = html.count(anchor)
print(f'anchor occurrences: {cnt}')
html = html.replace(anchor, new_anchor, 1)

with open('index.html.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('openDailyReport:', 'openDailyReport' in html)
print('openEditProd:', 'openEditProd' in html)
print('executeBatchDelete:', 'executeBatchDelete' in html)
