with open('beacon_yard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Firebase Auth SDK 추가 (firestore-compat 뒤에) ─────────────────────────
old_fs_script = '<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore-compat.js">'
new_fs_script = (
    '<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore-compat.js">\n'
    '</script>\n'
    '<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js">'
)
html = html.replace(old_fs_script, new_fs_script, 1)

# ── 2. 로그인 화면 CSS 추가 ───────────────────────────────────────────────────
login_css = """
/* ─── LOGIN SCREEN ─── */
#screen-login{min-height:100vh;background:linear-gradient(160deg,#0d47a1 0%,#1565c0 40%,#1976d2 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px;box-sizing:border-box}
.login-box{background:#fff;border-radius:24px;padding:32px 24px;width:100%;max-width:360px;box-shadow:0 8px 40px rgba(0,0,0,.25)}
.login-logo{text-align:center;margin-bottom:28px}
.login-logo-icon{font-size:2.8rem}
.login-logo-title{font-size:1.2rem;font-weight:800;color:#0d47a1;margin-top:8px}
.login-logo-sub{font-size:.75rem;color:#90a4ae;margin-top:4px}
.login-field{margin-bottom:14px}
.login-field label{font-size:.78rem;font-weight:700;color:#546e7a;display:block;margin-bottom:5px}
.login-field input{width:100%;padding:13px 14px;border:1.5px solid #e0e0e0;border-radius:10px;font-size:.95rem;font-family:inherit;box-sizing:border-box;outline:none;transition:border-color .2s}
.login-field input:focus{border-color:#1565c0}
.login-remember{display:flex;align-items:center;gap:8px;margin-bottom:20px;font-size:.82rem;color:#546e7a;cursor:pointer}
.login-remember input[type=checkbox]{width:17px;height:17px;accent-color:#1565c0;cursor:pointer}
.btn-login{width:100%;padding:14px;background:#1565c0;color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:700;cursor:pointer;font-family:inherit;transition:background .2s}
.btn-login:active{background:#0d47a1}
.login-error{color:#c62828;font-size:.8rem;text-align:center;margin-top:12px;min-height:18px;line-height:1.4}
.home-user-bar{display:flex;align-items:center;justify-content:space-between;padding:10px 16px 0}
.home-user-info{color:rgba(255,255,255,.85);font-size:.8rem}
.btn-logout{background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.35);color:#fff;font-size:.75rem;padding:5px 12px;border-radius:20px;cursor:pointer;font-family:inherit}
"""
html = html.replace('</style>', login_css + '</style>', 1)

# ── 3. screen-home을 처음엔 숨김 (auth가 제어) ──────────────────────────────
html = html.replace(
    '<div id="screen-home" class="screen active">',
    '<div id="screen-home" class="screen">',
    1
)

# ── 4. 로그인 화면 HTML 삽입 (HOME 앞에) ────────────────────────────────────
login_screen = """<!-- ════════════════════ LOGIN ════════════════════ -->
<div id="screen-login" class="screen active">
  <div class="login-box">
    <div class="login-logo">
      <div class="login-logo-icon">🏭</div>
      <div class="login-logo-title">비콘㈜ 관리시스템</div>
      <div class="login-logo-sub">로그인이 필요합니다</div>
    </div>
    <div class="login-field">
      <label>아이디 (이메일)</label>
      <input type="email" id="inp-login-email" placeholder="user@beacon.kr"
             autocomplete="email" inputmode="email"/>
    </div>
    <div class="login-field">
      <label>비밀번호</label>
      <input type="password" id="inp-login-pw" placeholder="••••••••"
             autocomplete="current-password"
             onkeydown="if(event.key==='Enter')doLogin()"/>
    </div>
    <label class="login-remember">
      <input type="checkbox" id="chk-remember"/>
      아이디·비밀번호 저장
    </label>
    <button class="btn-login" onclick="doLogin()">로그인</button>
    <div class="login-error" id="login-error"></div>
  </div>
</div>

"""

html = html.replace('<!-- ════════════════════ HOME ════════════════════ -->', login_screen + '<!-- ════════════════════ HOME ════════════════════ -->', 1)

# ── 5. 홈 화면에 사용자 정보 + 로그아웃 버튼 추가 ──────────────────────────
old_home_header = """    <div class="home-header">
      <div class="home-logo">🏭</div>
      <div class="home-title">비콘㈜ 관리시스템</div>
      <div class="home-sub">업무 영역을 선택하세요</div>
    </div>"""

new_home_header = """    <div class="home-user-bar">
      <div class="home-user-info">👤 <span id="home-user-name">-</span></div>
      <button class="btn-logout" onclick="doLogout()">로그아웃</button>
    </div>
    <div class="home-header">
      <div class="home-logo">🏭</div>
      <div class="home-title">비콘㈜ 관리시스템</div>
      <div class="home-sub">업무 영역을 선택하세요</div>
    </div>"""

html = html.replace(old_home_header, new_home_header, 1)

# ── 6. initFirebase에 Auth 초기화 추가 ──────────────────────────────────────
old_init = """async function initFirebase(cfg) {
  try {
    if (firebase.apps.length) {
      await Promise.all(firebase.apps.map(a => a.delete()));
    }
    firebase.initializeApp(cfg);
    db = firebase.firestore();
    db.settings({experimentalAutoDetectLongPolling: true, merge: true});
    setFbStatus('success', '✅ 연결됨 — ' + cfg.projectId);
    loadInventory();
    refreshMap();
  } catch(e) {
    setFbStatus('error', '❌ 오류: ' + e.message);
  }
}"""

new_init = """async function initFirebase(cfg) {
  try {
    if (firebase.apps.length) {
      await Promise.all(firebase.apps.map(a => a.delete()));
    }
    firebase.initializeApp(cfg);
    db = firebase.firestore();
    db.settings({experimentalAutoDetectLongPolling: true, merge: true});
    setFbStatus('success', '✅ 연결됨 — ' + cfg.projectId);
    initAuth();
  } catch(e) {
    setFbStatus('error', '❌ 오류: ' + e.message);
  }
}"""

html = html.replace(old_init, new_init, 1)

# ── 7. Auth JS 함수 추가 ─────────────────────────────────────────────────────
auth_js = """
// ─────────────────────────────────────────────────────────
//  FIREBASE AUTH
// ─────────────────────────────────────────────────────────
function initAuth() {
  const auth = firebase.auth();

  // 저장된 아이디/비밀번호 자동 입력
  const savedEmail = localStorage.getItem('bvy_login_email');
  const savedPw    = localStorage.getItem('bvy_login_pw');
  const remember   = localStorage.getItem('bvy_remember') === '1';
  if (savedEmail) document.getElementById('inp-login-email').value = savedEmail;
  if (savedPw)    document.getElementById('inp-login-pw').value    = savedPw;
  if (remember)   document.getElementById('chk-remember').checked  = true;

  auth.onAuthStateChanged(user => {
    if (user) {
      // 로그인됨 → 홈 화면
      const name = user.displayName || user.email?.split('@')[0] || '사용자';
      currentUser = name;
      updateUserDisp();
      const el = document.getElementById('home-user-name');
      if (el) el.textContent = name;
      document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
      document.getElementById('screen-home').classList.add('active');
      loadInventory();
      refreshMap();
    } else {
      // 로그아웃됨 → 로그인 화면
      document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
      document.getElementById('screen-login').classList.add('active');
    }
  });
}

async function doLogin() {
  const email  = document.getElementById('inp-login-email').value.trim();
  const pw     = document.getElementById('inp-login-pw').value;
  const remember = document.getElementById('chk-remember').checked;
  const errEl  = document.getElementById('login-error');
  errEl.textContent = '';

  if (!email || !pw) {
    errEl.textContent = '아이디와 비밀번호를 입력하세요.';
    return;
  }

  // 저장 여부 처리
  if (remember) {
    localStorage.setItem('bvy_login_email', email);
    localStorage.setItem('bvy_login_pw', pw);
    localStorage.setItem('bvy_remember', '1');
  } else {
    localStorage.removeItem('bvy_login_email');
    localStorage.removeItem('bvy_login_pw');
    localStorage.removeItem('bvy_remember');
  }

  try {
    const persistence = remember
      ? firebase.auth.Auth.Persistence.LOCAL
      : firebase.auth.Auth.Persistence.SESSION;
    await firebase.auth().setPersistence(persistence);
    await firebase.auth().signInWithEmailAndPassword(email, pw);
    // onAuthStateChanged가 화면 전환 처리
  } catch(e) {
    const msgs = {
      'auth/user-not-found':    '등록되지 않은 아이디입니다.',
      'auth/wrong-password':    '비밀번호가 틀렸습니다.',
      'auth/invalid-email':     '이메일 형식이 올바르지 않습니다.',
      'auth/too-many-requests': '시도 횟수 초과. 잠시 후 다시 시도하세요.',
      'auth/invalid-credential':'아이디 또는 비밀번호가 올바르지 않습니다.',
    };
    errEl.textContent = msgs[e.code] || '로그인 오류: ' + e.message;
  }
}

function doLogout() {
  if (!confirm('로그아웃 하시겠습니까?')) return;
  firebase.auth().signOut();
}
"""

html = html.replace('</script>\n</body>', auth_js + '\n</script>\n</body>', 1)

with open('beacon_yard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')), 'bytes')
