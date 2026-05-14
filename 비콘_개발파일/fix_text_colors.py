"""
텍스트 색상(color:)만 검정으로 변경, 배경색(background-color:)은 주황색 유지
규칙: 'color:' 앞에 '-'나 알파벳이 없을 때만 교체 (background-color, border-color 등 제외)
"""
import re

fpath = r'C:\Users\user\Desktop\클로드\index.html'
with open(fpath, 'r', encoding='utf-8') as f:
    html = f.read()

original = html
count = 0

# ── 주황색 텍스트 → 검정 (단, background-color/border-color 등은 제외) ──────
# (?<![a-z\-]) : 앞에 소문자 알파벳이나 하이픈이 없을 때만 매칭
text_color_map = [
    (r'(?<![a-z\-])color\s*:\s*#e65100', 'color:#222222'),
    (r'(?<![a-z\-])color\s*:\s*#ef6c00', 'color:#555555'),
    (r'(?<![a-z\-])color\s*:\s*#f57c00', 'color:#222222'),
    (r'(?<![a-z\-])color\s*:\s*#fb8c00', 'color:#222222'),
    (r'(?<![a-z\-])color\s*:\s*#bf360c', 'color:#222222'),
]

for pattern, replacement in text_color_map:
    new_html, n = re.subn(pattern, replacement, html, flags=re.IGNORECASE)
    if n:
        html = new_html
        count += n
        print(f'  {pattern[-7:]} → {replacement[-7:]}: {n}개')

# ── 단, 버튼/배지처럼 주황 배경 위에 흰색 글자는 건드리지 않음 (이미 #fff 이므로 무관) ──

# ── 확인: border-color, background-color 주황색은 유지됐는지 체크 ──────────
bg_count = html.count('background:#e65100') + html.count('background-color:#e65100')
border_count = html.count('border-color:#e65100') + html.count('border-top-color:#e65100') + html.count('border-bottom-color:#e65100')
print(f'\n  [확인] background:#e65100 = {bg_count}개 유지')
print(f'  [확인] border-color:#e65100 = {border_count}개 유지')

if html != original:
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'\n총 {count}개 텍스트 색상 검정으로 변경 완료.')
else:
    print('\n변경 없음.')
