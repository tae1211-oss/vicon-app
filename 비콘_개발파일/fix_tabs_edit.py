with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
# 1. 현황탭 행 버튼에서 🗑 삭제버튼 제거 (✏️만 남김, 모든 유저 사용)
#    → 5곳 동일하게 적용
# ══════════════════════════════════════════════════════════
old_row_btns = """        <td style="white-space:nowrap">
          <button onclick="openEditProd('${r.id}','${year}','${month}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#2e7d32;padding:2px 4px;line-height:1"
            title="수정">✏️</button>
          <button onclick="openDailyReport('${r.date}','${r.machine}','${r.shift||''}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#1565c0;padding:2px 4px;line-height:1"
            title="작업일보">📋</button>
          <button onclick="deleteProdRow('${r.id}','${year}','${month}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#e53935;padding:2px 4px;line-height:1"
            title="삭제">🗑</button>
        </td>"""

new_row_btns = """        <td style="white-space:nowrap">
          <button onclick="openEditProd('${r.id}','${year}','${month}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#2e7d32;padding:2px 4px;line-height:1"
            title="수정/취소">✏️</button>
          <button onclick="openDailyReport('${r.date}','${r.machine}','${r.shift||''}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#1565c0;padding:2px 4px;line-height:1"
            title="작업일보">📋</button>
        </td>"""

cnt = html.count(old_row_btns)
print(f'row_btns: {cnt}')
html = html.replace(old_row_btns, new_row_btns)

# ══════════════════════════════════════════════════════════
# 2. 공정 탭 CSS → 2배 크기
# ══════════════════════════════════════════════════════════
old_type_css = """.prod-type-btn{flex:1;min-width:68px;padding:7px 4px 5px;text-align:center;font-size:.7rem;color:#888;cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap}
.prod-type-btn.active{color:#0d47a1;border-bottom-color:#0d47a1;font-weight:700}"""

new_type_css = """.prod-type-btn{flex:1;min-width:88px;padding:14px 6px 11px;text-align:center;font-size:1rem;color:#888;cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap}
.prod-type-btn.active{color:#0d47a1;border-bottom-color:#0d47a1;font-weight:700}"""

cnt = html.count(old_type_css)
print(f'type_css: {cnt}')
html = html.replace(old_type_css, new_type_css)

# ══════════════════════════════════════════════════════════
# 3. 공정 탭 순서 변경: 신선 제거, TG-포밍-데크 순서
# ══════════════════════════════════════════════════════════
old_type_bar = """  <div class="prod-type-bar">
    <div class="prod-type-btn active" id="ptype-deck"    onclick="setProdType('deck')">📐 데크</div>
    <div class="prod-type-btn"        id="ptype-fresh"   onclick="setProdType('fresh')">❄️ 신선</div>
    <div class="prod-type-btn"        id="ptype-tg"      onclick="setProdType('tg')">⚙️ TG</div>
    <div class="prod-type-btn"        id="ptype-forming" onclick="setProdType('forming')">🔧 포밍</div>
  </div>"""

new_type_bar = """  <div class="prod-type-bar">
    <div class="prod-type-btn"        id="ptype-tg"      onclick="setProdType('tg')">⚙️ TG</div>
    <div class="prod-type-btn"        id="ptype-forming" onclick="setProdType('forming')">🔧 포밍</div>
    <div class="prod-type-btn active" id="ptype-deck"    onclick="setProdType('deck')">📐 데크</div>
  </div>"""

cnt = html.count(old_type_bar)
print(f'type_bar: {cnt}')
html = html.replace(old_type_bar, new_type_bar)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('row_btns(no delete):', 'title="수정/취소"' in html)
print('bigger tabs:', 'font-size:1rem' in html)
print('TG first:', html.find('ptype-tg') < html.find('ptype-deck'))
print('신선 탭 없음:', 'ptype-fresh' not in html)
