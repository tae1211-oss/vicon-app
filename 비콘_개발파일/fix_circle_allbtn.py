with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. 작업일보 shift 동그라미 표시 ─────────────────────
old_shift = """    const shiftHtml = curShift==='주간'
      ? '<span style="color:#c0392b;font-weight:bold">주</span>&nbsp;야'
      : '주&nbsp;<span style="color:#c0392b;font-weight:bold">야</span>';"""

new_shift = """    const circleStyle = 'display:inline-block;border:2px solid #c0392b;border-radius:50%;width:1.5em;height:1.5em;line-height:1.4em;text-align:center;color:#c0392b;font-weight:bold;vertical-align:middle';
    const shiftHtml = curShift==='주간'
      ? '<span style="'+circleStyle+'">주</span>&nbsp;야'
      : '주&nbsp;<span style="'+circleStyle+'">야</span>';"""

cnt = html.count(old_shift)
print(f'shiftHtml: {cnt}')
html = html.replace(old_shift, new_shift)

# ── 2. 수정 모달 일괄선택/일괄취소 버튼 추가 ─────────────
old_modal_label = """    <div style="font-size:.78rem;font-weight:700;color:#546e7a;margin-bottom:6px">취소할 패킹번호 체크 해제</div>
    <div id="edit-prod-packs" style="border:1px solid #e0e0e0;border-radius:8px;padding:4px 8px;max-height:300px;overflow-y:auto"></div>"""

new_modal_label = """    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
      <div style="font-size:.78rem;font-weight:700;color:#546e7a">취소할 패킹번호 체크 해제</div>
      <div style="display:flex;gap:6px">
        <button onclick="setAllPackCb(true)"  style="font-size:.72rem;padding:3px 8px;background:#e3f2fd;color:#1565c0;border:1px solid #90caf9;border-radius:6px;cursor:pointer;font-family:inherit">일괄선택</button>
        <button onclick="setAllPackCb(false)" style="font-size:.72rem;padding:3px 8px;background:#fce4ec;color:#c62828;border:1px solid #ef9a9a;border-radius:6px;cursor:pointer;font-family:inherit">일괄취소</button>
      </div>
    </div>
    <div id="edit-prod-packs" style="border:1px solid #e0e0e0;border-radius:8px;padding:4px 8px;max-height:300px;overflow-y:auto"></div>"""

cnt = html.count(old_modal_label)
print(f'modal_label: {cnt}')
html = html.replace(old_modal_label, new_modal_label)

# ── 3. setAllPackCb 함수 추가 (closeEditProd 바로 앞) ────
old_close = """function closeEditProd() {
  document.getElementById('edit-prod-modal').style.display = 'none';
}"""

new_close = """function setAllPackCb(checked) {
  document.querySelectorAll('input[name="edit-pack-cb"]').forEach(cb => cb.checked = checked);
}

function closeEditProd() {
  document.getElementById('edit-prod-modal').style.display = 'none';
}"""

cnt = html.count(old_close)
print(f'closeEditProd: {cnt}')
html = html.replace(old_close, new_close, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('circle style:', 'border-radius:50%' in html)
print('setAllPackCb:', 'setAllPackCb' in html)
print('일괄선택:', '일괄선택' in html)
