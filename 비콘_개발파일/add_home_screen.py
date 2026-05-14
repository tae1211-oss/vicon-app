with open('beacon_yard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. title 변경
html = html.replace(
    '<title>비콘㈜ 야적장 재고관리</title>',
    '<title>비콘㈜ 관리시스템</title>'
)

# 2. 홈 화면 CSS 추가 (</style> 직전)
home_css = """
/* ─── HOME SCREEN ─── */
.screen{display:none}
.screen.active{display:block}
#screen-home{min-height:100vh;background:linear-gradient(160deg,#0d47a1 0%,#1565c0 40%,#1976d2 100%)}
.home-header{padding:40px 24px 20px;color:#fff;text-align:center}
.home-logo{font-size:2.2rem;margin-bottom:6px}
.home-title{font-size:1.4rem;font-weight:800;letter-spacing:-.5px}
.home-sub{font-size:.82rem;opacity:.75;margin-top:4px}
.home-cards{padding:16px}
.app-card{background:#fff;border-radius:20px;padding:24px 20px;margin-bottom:14px;display:flex;align-items:center;gap:18px;box-shadow:0 4px 20px rgba(0,0,0,.15);cursor:pointer;transition:transform .15s,box-shadow .15s;-webkit-tap-highlight-color:transparent}
.app-card:active{transform:scale(.97);box-shadow:0 2px 10px rgba(0,0,0,.12)}
.app-card-icon{font-size:2.4rem;flex-shrink:0}
.app-card-info{}
.app-card-name{font-size:1.05rem;font-weight:800;color:#0d47a1}
.app-card-desc{font-size:.78rem;color:#78909c;margin-top:3px;line-height:1.4}
.home-back{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.18);border:none;color:#fff;font-size:.82rem;padding:6px 12px;border-radius:20px;cursor:pointer;font-family:inherit}
"""
html = html.replace('</style>', home_css + '</style>')

# 3. <body> 직후에 홈 화면 삽입
home_screen = """
<!-- ════════════════════ HOME ════════════════════ -->
<div id="screen-home" class="screen active">
  <div id="screen-home">
    <div class="home-header">
      <div class="home-logo">🏭</div>
      <div class="home-title">비콘㈜ 관리시스템</div>
      <div class="home-sub">업무 영역을 선택하세요</div>
    </div>
    <div class="home-cards">
      <div class="app-card" onclick="goApp('inventory')">
        <div class="app-card-icon">📦</div>
        <div class="app-card-info">
          <div class="app-card-name">재고수불</div>
          <div class="app-card-desc">야적장 입고·출고·구역별 재고 현황 관리</div>
        </div>
      </div>
      <div class="app-card" onclick="goApp('production')">
        <div class="app-card-icon">🏗️</div>
        <div class="app-card-info">
          <div class="app-card-name">생산수불</div>
          <div class="app-card-desc">생산 실적·공정별 수량·불량 현황 관리</div>
        </div>
      </div>
    </div>
  </div>
</div>

"""

# 4. 기존 header ~ toast를 screen-inventory로 감싸기
# 기존 header 앞에 screen-inventory 시작 태그 추가
inventory_open = '<!-- ════════════════════ INVENTORY APP ════════════════════ -->\n<div id="screen-inventory" class="screen">\n\n'

# 5. header 수정: 홈 버튼 + 타이틀
old_header = """<header>
  <h1>🏭 비콘㈜ 야적장 재고관리</h1>
  <div class="user-pill" id="user-pill" onclick="showTab('settings')">
    <span id="user-name-disp">이름 설정</span>
  </div>
</header>"""

new_header = """<header>
  <button class="home-back" onclick="goHome()">⬅ 홈</button>
  <h1 style="font-size:.88rem">📦 재고수불</h1>
  <div class="user-pill" id="user-pill" onclick="showTab('settings')">
    <span id="user-name-disp">이름 설정</span>
  </div>
</header>"""

html = html.replace(old_header, inventory_open + new_header)

# 6. toast div 뒤에 screen-inventory 닫기 + screen-production 추가
production_screen = """

</div><!-- /screen-inventory -->

<!-- ════════════════════ PRODUCTION APP ════════════════════ -->
<div id="screen-production" class="screen">
  <header>
    <button class="home-back" onclick="goHome()">⬅ 홈</button>
    <h1 style="font-size:.88rem">🏗️ 생산수불</h1>
    <div style="width:60px"></div>
  </header>
  <div class="tabs">
    <div class="tab active" id="ptab-dashboard" onclick="showPTab('dashboard')"><span class="tab-icon">📊</span>현황</div>
    <div class="tab" id="ptab-input" onclick="showPTab('input')"><span class="tab-icon">✏️</span>생산입력</div>
    <div class="tab" id="ptab-ledger" onclick="showPTab('ledger')"><span class="tab-icon">📒</span>수불장</div>
    <div class="tab" id="ptab-settings" onclick="showPTab('psettings')"><span class="tab-icon">⚙️</span>설정</div>
  </div>

  <!-- 현황 -->
  <div class="page active" id="ppage-dashboard">
    <div class="card">
      <div class="card-title">📊 생산 현황</div>
      <div class="alert alert-info" style="text-align:center;padding:30px 16px">
        <div style="font-size:2rem;margin-bottom:8px">🚧</div>
        <div style="font-weight:700;margin-bottom:4px">준비 중입니다</div>
        <div style="font-size:.78rem;color:#546e7a">생산수불 기능을 구성 중입니다.<br>필요한 항목을 관리자에게 문의하세요.</div>
      </div>
    </div>
  </div>

  <!-- 생산입력 -->
  <div class="page" id="ppage-input">
    <div class="card">
      <div class="card-title">✏️ 생산 입력</div>
      <div class="alert alert-info" style="text-align:center;padding:30px 16px">
        <div style="font-size:2rem;margin-bottom:8px">🚧</div>
        <div style="font-weight:700">준비 중</div>
      </div>
    </div>
  </div>

  <!-- 수불장 -->
  <div class="page" id="ppage-ledger">
    <div class="card">
      <div class="card-title">📒 수불장</div>
      <div class="alert alert-info" style="text-align:center;padding:30px 16px">
        <div style="font-size:2rem;margin-bottom:8px">🚧</div>
        <div style="font-weight:700">준비 중</div>
      </div>
    </div>
  </div>

  <!-- 설정 -->
  <div class="page" id="ppage-psettings">
    <div class="card">
      <div class="card-title">⚙️ 생산 설정</div>
      <div class="alert alert-info" style="text-align:center;padding:30px 16px">
        <div style="font-size:2rem;margin-bottom:8px">🚧</div>
        <div style="font-weight:700">준비 중</div>
      </div>
    </div>
  </div>
</div><!-- /screen-production -->
"""

html = html.replace('<div id="toast"></div>', '<div id="toast"></div>' + production_screen)

# 7. body 태그 직후에 홈 화면 삽입
html = html.replace('<body>\n', '<body>\n' + home_screen)

# 8. JS: goApp, goHome, showPTab 함수 추가 (</script> 직전)
nav_js = """
// ─────────────────────────────────────────────────────────
//  APP NAVIGATION
// ─────────────────────────────────────────────────────────
function goApp(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-' + name).classList.add('active');
  window.scrollTo(0,0);
  if (name === 'inventory') refreshMap();
}
function goHome() {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-home').classList.add('active');
  window.scrollTo(0,0);
}
function showPTab(name) {
  document.querySelectorAll('[id^="ppage-"]').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('[id^="ptab-"]').forEach(t => t.classList.remove('active'));
  document.getElementById('ppage-' + name).classList.add('active');
  document.getElementById('ptab-' + name).classList.add('active');
}
"""
html = html.replace('</script>', nav_js + '\n</script>')

with open('beacon_yard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')), 'bytes')
