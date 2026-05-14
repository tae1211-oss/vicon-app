with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── Fix 1: handleInbound unescaped single quotes ──────────────────────────
# Python reads the broken JS literally; replace with escaped versions

old1 = """    html += '<div class="pack-controls">'\n      + '<button class="btn btn-sm btn-secondary" onclick="packSelAll('ib',true)">전체선택</button>'\n      + '<button class="btn btn-sm btn-secondary" onclick="packSelAll('ib',false)">전체해제</button>'"""
new1 = """    html += '<div class="pack-controls">'\n      + '<button class="btn btn-sm btn-secondary" onclick="packSelAll(\\'ib\\',true)">전체선택</button>'\n      + '<button class="btn btn-sm btn-secondary" onclick="packSelAll(\\'ib\\',false)">전체해제</button>'"""

cnt1 = html.count(old1)
print(f'fix1 (packSelAll): {cnt1}')
html = html.replace(old1, new1)

old2 = """        + (inStock ? '' : 'checked ') + 'onchange="syncSel('ib')">'"""
new2 = """        + (inStock ? '' : 'checked ') + 'onchange="syncSel(\\'ib\\')">'"""

cnt2 = html.count(old2)
print(f'fix2 (syncSel): {cnt2}')
html = html.replace(old2, new2)

# ── Fix 3: doLogin error — also show alert popup ──────────────────────────
old3 = "    errEl.textContent = msgs[e.code] || '로그인 오류: ' + e.message;"
new3 = """    const loginMsg = msgs[e.code] || '로그인 오류: ' + e.message;
    errEl.textContent = loginMsg;
    alert(loginMsg);"""

cnt3 = html.count(old3)
print(f'fix3 (doLogin alert): {cnt3}')
html = html.replace(old3, new3)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print("packSelAll\\'ib\\' check:", html.count("packSelAll(\\'ib\\'"))
print("syncSel\\'ib\\' check:", html.count("syncSel(\\'ib\\'"))
print('loginMsg alert check:', html.count('alert(loginMsg)'))
