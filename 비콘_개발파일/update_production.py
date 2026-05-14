import re

with open('beacon_yard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS 추가 ──────────────────────────────────────────────
prod_css = """
/* ─── PRODUCTION ─── */
.prod-type-bar{display:flex;background:#fff;border-bottom:1px solid #e0e0e0;overflow-x:auto;scrollbar-width:none;position:sticky;top:44px;z-index:98}
.prod-type-bar::-webkit-scrollbar{display:none}
.prod-type-btn{flex:1;min-width:68px;padding:7px 4px 5px;text-align:center;font-size:.7rem;color:#888;cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap}
.prod-type-btn.active{color:#0d47a1;border-bottom-color:#0d47a1;font-weight:700}
.prod-tabs-sticky{top:88px}
.prod-stat-table{width:100%;border-collapse:collapse;font-size:.74rem}
.prod-stat-table th{background:#e8edf5;color:#37474f;font-weight:700;padding:6px 7px;text-align:center;white-space:nowrap;position:sticky;top:0}
.prod-stat-table td{padding:5px 7px;border-bottom:1px solid #f0f0f0;text-align:center;white-space:nowrap}
.prod-stat-table tr.day-total td{background:#f5f7fa;font-weight:700;color:#0d47a1}
.prod-stat-table tr.month-total td{background:#dce8fb;font-weight:800;color:#0d47a1;font-size:.8rem}
.stat-back-btn{background:#fff;border:1.5px solid #cfd8dc;border-radius:8px;padding:5px 14px;font-size:.78rem;color:#546e7a;cursor:pointer;margin-bottom:10px;font-family:inherit}
.pack-detail-row{display:flex;align-items:center;padding:7px 12px;border-bottom:1px solid #f5f5f5}
.pack-detail-badge{display:inline-flex;gap:10px;font-size:.73rem;color:#546e7a;margin-left:auto}
.prod-summary-bar{background:#e8f5e9;border-radius:10px;padding:10px 12px;margin-top:8px;display:flex;justify-content:space-around;text-align:center}
.prod-summary-item .pval{font-size:1.1rem;font-weight:800;color:#2e7d32}
.prod-summary-item .plbl{font-size:.68rem;color:#78909c;margin-top:1px}
.year-summary{display:flex;justify-content:space-around;padding:16px 0}
.year-summary .num{font-size:1.5rem;font-weight:800}
.year-summary .lbl{font-size:.7rem;color:#78909c;margin-top:2px}
"""
html = html.replace('</style>', prod_css + '</style>')

# ── 2. scanners에 production 추가 ────────────────────────────
html = html.replace(
    "let scanners = {inbound: null, outbound: null};",
    "let scanners = {inbound: null, outbound: null, production: null};"
)

# ── 3. 생산 화면 교체 ─────────────────────────────────────────
prod_screen = """<!-- ════════════════════ PRODUCTION APP ════════════════════ -->
<div id="screen-production" class="screen">
  <header>
    <button class="home-back" onclick="goHome()">⬅ 홈</button>
    <h1 style="font-size:.88rem">🏗️ 생산수불</h1>
    <div style="width:60px"></div>
  </header>

  <!-- 공정 선택 -->
  <div class="prod-type-bar">
    <div class="prod-type-btn active" id="ptype-deck"    onclick="setProdType('deck')">📐 데크</div>
    <div class="prod-type-btn"        id="ptype-fresh"   onclick="setProdType('fresh')">❄️ 신선</div>
    <div class="prod-type-btn"        id="ptype-tg"      onclick="setProdType('tg')">⚙️ TG</div>
    <div class="prod-type-btn"        id="ptype-forming" onclick="setProdType('forming')">🔧 포밍</div>
  </div>

  <!-- 탭 -->
  <div class="tabs prod-tabs-sticky">
    <div class="tab active" id="ptab-stat"      onclick="showPTab('stat')"><span class="tab-icon">📊</span>현황</div>
    <div class="tab"        id="ptab-entry"     onclick="showPTab('entry')"><span class="tab-icon">✏️</span>생산입력</div>
    <div class="tab"        id="ptab-psettings" onclick="showPTab('psettings')"><span class="tab-icon">⚙️</span>설정</div>
  </div>

  <!-- ── 현황 ── -->
  <div class="page active" id="ppage-stat">
    <div class="card">
      <div class="card-title" id="prod-stat-title">📊 데크 생산 현황</div>
      <div id="prod-stat-nav" style="margin-bottom:8px"></div>
      <div id="prod-stat-body">
        <div style="text-align:center;color:#90a4ae;padding:30px 0;font-size:.82rem">연도를 선택하세요</div>
      </div>
    </div>
  </div>

  <!-- ── 생산입력 ── -->
  <div class="page" id="ppage-entry">
    <!-- 데크 -->
    <div id="pdeck-entry">
      <div class="card">
        <div class="card-title">📐 데크 QR 스캔</div>
        <div class="alert alert-info" style="font-size:.78rem">작업지시서(job_order) QR을 스캔하세요.</div>
        <button class="btn btn-primary btn-full" id="btn-prod-scan" onclick="startProdScan()">📷 QR 스캔 시작</button>
        <div id="prod-scan-wrap" style="display:none;margin-top:12px">
          <div id="prod-qr-reader"></div>
          <button class="btn btn-secondary btn-full" style="margin-top:8px" onclick="stopProdScan()">■ 스캔 중지</button>
        </div>
      </div>
      <div id="prod-entry-card" style="display:none">
        <div class="card">
          <div class="card-title" id="prod-entry-title">✏️ 생산 내역 입력</div>
          <div id="prod-entry-body"></div>
        </div>
      </div>
    </div>
    <!-- 준비중 (신선/TG/포밍) -->
    <div id="pother-entry" style="display:none">
      <div class="card" style="text-align:center;padding:36px 16px">
        <div style="font-size:2.5rem;margin-bottom:10px">🚧</div>
        <div style="font-weight:700;font-size:1rem;margin-bottom:6px">준비 중</div>
        <div style="font-size:.78rem;color:#78909c">추후 지원 예정입니다.</div>
      </div>
    </div>
  </div>

  <!-- ── 설정 ── -->
  <div class="page" id="ppage-psettings">
    <div id="prod-admin-sec">
      <div class="card">
        <div class="card-title">⚠️ 생산 데이터 관리</div>
        <div style="font-size:.78rem;color:#78909c;margin-bottom:10px">최근 생산 기록을 삭제합니다.</div>
        <button class="btn btn-danger btn-full" onclick="openDeleteProd()">🗑️ 생산 기록 삭제</button>
      </div>
    </div>
    <div id="prod-noadmin-sec" class="card" style="display:none">
      <div class="card-title">🔐 관리자 전용</div>
      <div style="font-size:.78rem;color:#546e7a">재고수불 설정 탭에서 관리자 로그인 후 이용하세요.</div>
    </div>
  </div>
</div><!-- /screen-production -->"""

# 기존 production screen 교체
html = re.sub(
    r'<!-- ════+\s*PRODUCTION APP\s*════+ -->\s*<div id="screen-production"[\s\S]*?</div><!-- /screen-production -->',
    prod_screen,
    html
)

# ── 4. JS 추가 ───────────────────────────────────────────────
prod_js = r"""
// ─────────────────────────────────────────────────────────
//  PRODUCTION MODULE
// ─────────────────────────────────────────────────────────
let currentProdType = 'deck';
let pendingProd     = null;
let prodStatView    = {year: null, month: null};
window._prodRecords = [];

// 공정 선택
function setProdType(type) {
  currentProdType = type;
  document.querySelectorAll('.prod-type-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('ptype-' + type).classList.add('active');
  const isDeck = type === 'deck';
  document.getElementById('pdeck-entry').style.display  = isDeck ? 'block' : 'none';
  document.getElementById('pother-entry').style.display = isDeck ? 'none'  : 'block';
  const title = {deck:'데크',fresh:'신선',tg:'TG',forming:'포밍'}[type] || type;
  document.getElementById('prod-stat-title').textContent = '📊 ' + title + ' 생산 현황';
  if (document.getElementById('ppage-stat').classList.contains('active')) loadProdStat();
}

// 탭 전환
function showPTab(name) {
  document.querySelectorAll('[id^="ppage-"]').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('[id^="ptab-"]').forEach(t => t.classList.remove('active'));
  document.getElementById('ppage-' + name).classList.add('active');
  document.getElementById('ptab-' + name).classList.add('active');
  if (name === 'stat') loadProdStat();
  if (name === 'psettings') {
    document.getElementById('prod-admin-sec').style.display  = isAdmin ? 'block' : 'none';
    document.getElementById('prod-noadmin-sec').style.display = isAdmin ? 'none'  : 'block';
  }
}

// 날짜 기본값: 오전 8시 기준 (8시 이전이면 전날)
function getProductionDate() {
  const now = new Date();
  if (now.getHours() < 8) now.setDate(now.getDate() - 1);
  return now.toISOString().split('T')[0];
}
// 주간/야간 기본값: 8~20시 = 주간
function getDefaultShift() {
  const h = new Date().getHours();
  return (h >= 8 && h < 20) ? '주간' : '야간';
}

// ── QR 스캔 ──────────────────────────────────────────────
function startProdScan() {
  document.getElementById('prod-scan-wrap').style.display = 'block';
  document.getElementById('btn-prod-scan').style.display  = 'none';
  if (scanners.production) return;
  scanners.production = new Html5Qrcode('prod-qr-reader');
  scanners.production.start(
    {facingMode: 'environment'},
    {fps: 10, qrbox: {width: 250, height: 250}},
    raw => {
      try {
        const data = JSON.parse(raw);
        stopProdScan();
        handleProdQR(data);
      } catch(_) {}
    }, () => {}
  ).catch(e => toast('카메라 오류: ' + e));
}

function stopProdScan() {
  if (scanners.production) {
    scanners.production.stop().catch(() => {});
    scanners.production = null;
  }
  const wrap = document.getElementById('prod-scan-wrap');
  const btn  = document.getElementById('btn-prod-scan');
  if (wrap) wrap.style.display = 'none';
  if (btn)  btn.style.display  = 'block';
}

function handleProdQR(data) {
  if (data.type !== 'job_order') { toast('작업지시서 QR이 아닙니다.'); return; }
  pendingProd = data;
  document.getElementById('prod-entry-card').style.display = 'block';
  document.getElementById('prod-entry-title').textContent =
    (data.site || '') + (data.company ? ' (' + data.company + ')' : '');
  renderDeckForm(data);
}

// ── 입력 폼 ──────────────────────────────────────────────
function renderDeckForm(data) {
  const packFrom = data.pack_from ?? data.pf ?? 0;
  const packTo   = data.pack_to   ?? data.pt ?? 0;
  const details  = data.d || [];          // [[sheets, area], …]
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

  const defDate  = getProductionDate();
  const defShift = getDefaultShift();
  const hasDetail = packs.some(p => p.s !== null);

  let html = `
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">
    <div class="form-group" style="margin:0">
      <label>생산 일자</label>
      <input type="date" id="prod-date" value="${defDate}"
        style="width:100%;border:1.5px solid #cfd8dc;border-radius:8px;padding:8px;font-size:.85rem;font-family:inherit">
    </div>
    <div class="form-group" style="margin:0">
      <label>호기</label>
      <select id="prod-machine"
        style="width:100%;border:1.5px solid #cfd8dc;border-radius:8px;padding:8px;font-size:.85rem;background:#fff;font-family:inherit">
        <option>1호기</option><option>2호기</option><option>3호기</option><option>4호기</option><option>탈형</option>
      </select>
    </div>
  </div>
  <div class="form-group" style="margin-bottom:12px">
    <label>주간 / 야간</label>
    <div style="display:flex;gap:8px">
      <label id="lbl-shift-day"
        style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:10px;border:2px solid #cfd8dc;border-radius:10px;cursor:pointer;font-size:.9rem;transition:border-color .15s">
        <input type="radio" name="prod-shift" value="주간" ${defShift==='주간'?'checked':''} onchange="updateShiftUI()"> 🌤️ 주간
      </label>
      <label id="lbl-shift-night"
        style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:10px;border:2px solid #cfd8dc;border-radius:10px;cursor:pointer;font-size:.9rem;transition:border-color .15s">
        <input type="radio" name="prod-shift" value="야간" ${defShift==='야간'?'checked':''} onchange="updateShiftUI()"> 🌙 야간
      </label>
    </div>
  </div>
  <div style="font-size:.78rem;color:#546e7a;margin-bottom:8px">
    <strong>의뢰번호:</strong> ${esc(data.req_code || '-')}
    &nbsp;|&nbsp; 총 ${packs.length}패킹
    ${hasDetail ? '' : '<span style="color:#f57f17"> (장수·면적 정보 없음)</span>'}
  </div>
  <div class="pack-controls">
    <button class="btn btn-sm btn-secondary" onclick="prodPackSelAll(true)">전체선택</button>
    <button class="btn btn-sm btn-secondary" onclick="prodPackSelAll(false)">전체해제</button>
  </div>
  <div style="border:1px solid #e0e0e0;border-radius:10px;margin:6px 0;max-height:280px;overflow-y:auto">`;

  packs.forEach(p => {
    html += `<div class="pack-detail-row">
      <label style="display:flex;align-items:center;gap:8px;flex:1;cursor:pointer">
        <input type="checkbox" class="prod-cb" value="${p.n}" checked onchange="updateProdTotals()">
        <span style="font-weight:600;min-width:38px">${p.n}</span>
        ${p.s !== null
          ? `<span class="pack-detail-badge"><span>${p.s}장</span><span>${p.a}㎡</span></span>`
          : '<span style="font-size:.72rem;color:#ccc">-</span>'}
      </label>
    </div>`;
  });

  html += `</div>
  <div class="prod-summary-bar" id="prod-summary">
    <div class="prod-summary-item"><div class="pval" id="sum-packs">0</div><div class="plbl">선택 패킹</div></div>
    <div class="prod-summary-item"><div class="pval" id="sum-sheets">-</div><div class="plbl">총 장수</div></div>
    <div class="prod-summary-item"><div class="pval" id="sum-area">-</div><div class="plbl">총 면적(㎡)</div></div>
  </div>
  <button class="btn btn-success btn-full" style="margin-top:12px" onclick="submitProdEntry()">✅ 생산 등록</button>`;

  document.getElementById('prod-entry-body').innerHTML = html;
  updateShiftUI();
  updateProdTotals();
}

function updateShiftUI() {
  const isDay = document.querySelector('input[name="prod-shift"][value="주간"]')?.checked;
  document.getElementById('lbl-shift-day').style.borderColor   = isDay  ? '#0d47a1' : '#cfd8dc';
  document.getElementById('lbl-shift-night').style.borderColor = !isDay ? '#0d47a1' : '#cfd8dc';
}

function prodPackSelAll(val) {
  document.querySelectorAll('.prod-cb').forEach(c => { c.checked = val; });
  updateProdTotals();
}

function updateProdTotals() {
  const packs = pendingProd?._packs || [];
  const sel   = [...document.querySelectorAll('.prod-cb:checked')].map(c => +c.value);
  let tSheets = 0, tArea = 0, hasDetail = false;
  sel.forEach(n => {
    const p = packs.find(x => x.n === n);
    if (p && p.s !== null) { tSheets += p.s; tArea += p.a; hasDetail = true; }
  });
  document.getElementById('sum-packs').textContent  = sel.length;
  document.getElementById('sum-sheets').textContent = hasDetail ? tSheets : '-';
  document.getElementById('sum-area').textContent   = hasDetail ? tArea.toFixed(1) : '-';
}

async function submitProdEntry() {
  if (!db) { toast('Firebase 미연결'); return; }
  if (!currentUser) { toast('먼저 이름을 설정하세요.'); return; }
  const sel = [...document.querySelectorAll('.prod-cb:checked')].map(c => +c.value);
  if (!sel.length) { toast('패킹을 선택하세요.'); return; }

  const date    = document.getElementById('prod-date').value;
  const machine = document.getElementById('prod-machine').value;
  const shift   = document.querySelector('input[name="prod-shift"]:checked')?.value || '주간';
  const packs   = pendingProd._packs || [];
  const selPacks = sel.map(n => {
    const p = packs.find(x => x.n === n) || {n, s: null, a: null};
    return {pack_no: p.n, sheets: p.s, area: p.a};
  });
  const hasDetail  = selPacks.some(p => p.sheets !== null);
  const totSheets  = hasDetail ? selPacks.reduce((s,p) => s + (p.sheets||0), 0) : null;
  const totArea    = hasDetail ? +selPacks.reduce((s,p) => s + (p.area||0), 0).toFixed(2) : null;

  const rec = {
    type: 'deck', date, shift, machine,
    company:      pendingProd.company  || '',
    site:         pendingProd.site     || '',
    req_code:     pendingProd.req_code || '',
    packs:        selPacks,
    pack_count:   selPacks.length,
    total_sheets: totSheets,
    total_area:   totArea,
    recorded_at:  firebase.firestore.Timestamp.now(),
    recorded_by:  currentUser
  };

  try {
    await db.collection('production_deck').add(rec);
    document.getElementById('prod-entry-card').style.display = 'none';
    pendingProd = null;
    toast('✅ 생산 등록 완료!');
    if (window._prodRecords) window._prodRecords.push({...rec, id: 'new'});
  } catch(e) { toast('저장 실패: ' + e.message); }
}

// ── 현황 ─────────────────────────────────────────────────
async function loadProdStat() {
  if (!db) return;
  const bodyEl = document.getElementById('prod-stat-body');
  const navEl  = document.getElementById('prod-stat-nav');
  if (!bodyEl) return;
  bodyEl.innerHTML = '<div class="loading"><span class="spinner"></span>로딩 중…</div>';
  navEl.innerHTML  = '';
  try {
    const snap = await db.collection('production_deck').get();
    const records = [];
    snap.forEach(doc => records.push({id: doc.id, ...doc.data()}));
    window._prodRecords = records;

    if (!records.length) {
      bodyEl.innerHTML = '<div class="alert alert-info">생산 기록이 없습니다.</div>'; return;
    }

    const years = [...new Set(records.map(r => r.date?.slice(0,4)).filter(Boolean))].sort().reverse();
    navEl.innerHTML = years.map(y =>
      `<button class="btn btn-sm btn-secondary" style="min-width:66px;margin:2px"
        onclick="showProdYear('${y}')">${y}년</button>`
    ).join('');
    bodyEl.innerHTML = '<div style="text-align:center;color:#90a4ae;padding:20px 0;font-size:.82rem">연도를 탭하세요</div>';
  } catch(e) {
    bodyEl.innerHTML = `<div class="alert alert-error">${e.message}</div>`;
  }
}

function showProdYear(year) {
  const records = (window._prodRecords||[]).filter(r => r.date?.startsWith(year));
  const navEl  = document.getElementById('prod-stat-nav');
  const bodyEl = document.getElementById('prod-stat-body');

  const months = [...new Set(records.map(r => r.date?.slice(5,7)).filter(Boolean))].sort();
  navEl.innerHTML = `<button class="stat-back-btn" onclick="loadProdStat()">← 전체</button>
    <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px">${
      months.map(m => `<button class="btn btn-sm btn-secondary" style="min-width:52px"
        onclick="showProdMonth('${year}','${m}')">${+m}월</button>`).join('')
    }</div>`;

  const totPacks  = records.reduce((s,r) => s + (r.pack_count||0), 0);
  const totSheets = records.reduce((s,r) => s + (r.total_sheets||0), 0);
  const totArea   = records.reduce((s,r) => s + (r.total_area||0), 0);
  const hasDetail = records.some(r => r.total_sheets);

  bodyEl.innerHTML = `<div style="text-align:center;padding:12px 0 6px">
    <div style="font-size:.9rem;font-weight:800;color:#0d47a1;margin-bottom:10px">${year}년 합계</div>
    <div class="year-summary">
      <div><div class="num" style="color:#2e7d32">${totPacks}</div><div class="lbl">패킹</div></div>
      <div><div class="num" style="color:#1565c0">${hasDetail ? totSheets : '-'}</div><div class="lbl">장</div></div>
      <div><div class="num" style="color:#6a1b9a">${hasDetail ? totArea.toFixed(1) : '-'}</div><div class="lbl">㎡</div></div>
    </div>
    <div style="font-size:.75rem;color:#90a4ae">월을 탭하면 상세 현황을 볼 수 있습니다</div>
  </div>`;
}

function showProdMonth(year, month) {
  const records = (window._prodRecords||[])
    .filter(r => r.date?.startsWith(year + '-' + month))
    .sort((a,b) => {
      if (a.date !== b.date) return a.date.localeCompare(b.date);
      if (a.shift !== b.shift) return a.shift === '주간' ? -1 : 1;
      return (a.machine||'').localeCompare(b.machine||'');
    });

  const navEl  = document.getElementById('prod-stat-nav');
  const bodyEl = document.getElementById('prod-stat-body');

  navEl.innerHTML = `<button class="stat-back-btn" onclick="showProdYear('${year}')">← ${year}년</button>`;

  if (!records.length) {
    bodyEl.innerHTML = '<div class="alert alert-info">해당 월 기록 없습니다.</div>'; return;
  }

  const hasDetail = records.some(r => r.total_sheets);

  let html = `<div style="overflow-x:auto"><table class="prod-stat-table"><thead><tr>
    <th>날짜</th><th>주/야</th><th>호기</th><th>현장</th><th>패킹</th>
    ${hasDetail ? '<th>장수</th><th>㎡</th>' : ''}
  </tr></thead><tbody>`;

  // 날짜별 그룹
  const byDay = {};
  records.forEach(r => { (byDay[r.date] = byDay[r.date]||[]).push(r); });

  let mPacks = 0, mSheets = 0, mArea = 0;
  Object.entries(byDay).sort().forEach(([date, recs]) => {
    const dPacks  = recs.reduce((s,r) => s+(r.pack_count||0), 0);
    const dSheets = recs.reduce((s,r) => s+(r.total_sheets||0), 0);
    const dArea   = recs.reduce((s,r) => s+(r.total_area||0), 0);
    mPacks += dPacks; mSheets += dSheets; mArea += dArea;

    const d = new Date(date + 'T12:00:00');
    const dayLbl = (d.getMonth()+1) + '/' + d.getDate() + '(' + '일월화수목금토'[d.getDay()] + ')';

    recs.forEach((r, idx) => {
      const siteShort = (r.site||'').length > 8 ? (r.site||'').slice(0,7)+'…' : (r.site||'-');
      html += `<tr>
        <td>${idx===0 ? dayLbl : ''}</td>
        <td>${r.shift||''}</td>
        <td>${r.machine||''}</td>
        <td style="text-align:left">${esc(siteShort)}</td>
        <td>${r.pack_count||0}</td>
        ${hasDetail ? `<td>${r.total_sheets??'-'}</td><td>${r.total_area!=null?r.total_area.toFixed(1):'-'}</td>` : ''}
      </tr>`;
    });
    html += `<tr class="day-total">
      <td colspan="4" style="text-align:right;font-size:.72rem">${dayLbl} 계</td>
      <td>${dPacks}</td>
      ${hasDetail ? `<td>${dSheets||'-'}</td><td>${dArea?dArea.toFixed(1):'-'}</td>` : ''}
    </tr>`;
  });

  html += `<tr class="month-total">
    <td colspan="4" style="text-align:right">${+month}월 합계</td>
    <td>${mPacks}</td>
    ${hasDetail ? `<td>${mSheets||'-'}</td><td>${mArea?mArea.toFixed(1):'-'}</td>` : ''}
  </tr></tbody></table></div>`;

  bodyEl.innerHTML = html;
}

// ── 생산기록 삭제 ─────────────────────────────────────────
async function openDeleteProd() {
  if (!db) { toast('Firebase 미연결'); return; }
  let snap;
  try { snap = await db.collection('production_deck').orderBy('date','desc').limit(60).get(); }
  catch(e) { toast(e.message); return; }
  if (snap.empty) { toast('삭제할 기록이 없습니다.'); return; }

  let html = '<div style="max-height:50vh;overflow-y:auto">';
  snap.forEach(doc => {
    const r = doc.data();
    html += `<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f0f0f0">
      <div style="flex:1;font-size:.8rem">
        <div style="font-weight:700">${r.date||''} ${r.shift||''} ${r.machine||''}</div>
        <div style="color:#78909c">${esc(r.site||'')} · ${r.pack_count||0}패킹 · ${esc(r.recorded_by||'')}</div>
      </div>
      <button class="btn btn-danger btn-sm" onclick="deleteProdRecord('${doc.id}',this)">삭제</button>
    </div>`;
  });
  html += '</div>';

  document.getElementById('conf-title').textContent  = '🗑️ 생산 기록 삭제';
  document.getElementById('conf-body').innerHTML     = html;
  document.getElementById('conf-ok').style.display   = 'none';
  openOv('ov-confirm');
}

async function deleteProdRecord(docId, btn) {
  if (btn) btn.disabled = true;
  try {
    await db.collection('production_deck').doc(docId).delete();
    window._prodRecords = (window._prodRecords||[]).filter(r => r.id !== docId);
    toast('삭제 완료');
    if (btn) btn.closest('div').style.opacity = '.3';
  } catch(e) { toast('삭제 실패: ' + e.message); if (btn) btn.disabled = false; }
}
"""
html = html.replace('</script>', prod_js + '\n</script>')

with open('beacon_yard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. File size:', len(html.encode('utf-8')), 'bytes')
