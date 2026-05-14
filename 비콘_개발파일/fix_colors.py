"""
index.html 파란색 → 주황색 변경 + 생산수불 설명 수정
"""
import re

fpath = r'C:\Users\user\Desktop\클로드\index.html'

with open(fpath, 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# ── 색상 교체 맵 (파란색 → 주황색) ──────────────────────────────────────
COLOR_MAP = [
    # 진한 파란색
    ('#0d47a1', '#e65100'),
    ('#1565c0', '#f57c00'),
    ('#1976d2', '#fb8c00'),
    # 연한 파란색 배경
    ('#e3f2fd', '#fff3e0'),
    ('#dce8fb', '#ffe0b2'),
    ('#e8edf5', '#fff3e0'),
    ('#f8f9ff', '#fff8f0'),
    ('#e8eaf6', '#fbe9e7'),
    # 파란색 보더/강조
    ('#90caf9', '#ffcc80'),
    # 인디고 계열
    ('#5c6bc0', '#ef6c00'),
    ('#3949ab', '#f4511e'),
    ('#283593', '#bf360c'),
    # 기타 파란색
    ('#1e88e5', '#fb8c00'),
    ('#42a5f5', '#ffa726'),
    ('#64b5f6', '#ffb74d'),
    ('#bbdefb', '#ffe0b2'),
    ('#2196f3', '#ff9800'),
    ('#1a237e', '#bf360c'),
    ('#0288d1', '#f57c00'),
    ('#01579b', '#e65100'),
    ('#039be5', '#fb8c00'),
    ('#29b6f6', '#ffa726'),
    ('#4fc3f7', '#ffb74d'),
    ('#b3e5fc', '#ffe0b2'),
    ('#e1f5fe', '#fff3e0'),
    # rgba 파란색 → 주황색
]

count_total = 0
for old, new in COLOR_MAP:
    # case-insensitive 교체
    old_upper = old.upper()
    old_lower = old.lower()
    n1 = html.count(old_lower)
    n2 = html.count(old_upper)
    n = n1 + n2
    if n:
        html = html.replace(old_lower, new)
        html = html.replace(old_upper, new.upper())
        count_total += n
        print(f'  {old} → {new}: {n}개')

# rgba 파란색 패턴도 처리 (rgba(13,71,161,...) 등)
rgba_patterns = [
    (r'rgba\(\s*13\s*,\s*71\s*,\s*161\s*,', 'rgba(230,81,0,'),
    (r'rgba\(\s*21\s*,\s*101\s*,\s*192\s*,', 'rgba(245,124,0,'),
    (r'rgba\(\s*25\s*,\s*118\s*,\s*210\s*,', 'rgba(251,140,0,'),
    (r'rgba\(\s*33\s*,\s*150\s*,\s*243\s*,', 'rgba(255,152,0,'),
]
for pattern, replacement in rgba_patterns:
    new_html, n = re.subn(pattern, replacement, html, flags=re.IGNORECASE)
    if n:
        html = new_html
        count_total += n
        print(f'  rgba 패턴 교체: {n}개')

# ── 생산수불 설명 수정 ─────────────────────────────────────────────────────
old_desc = '생산 실적·공정별 수량·불량 현황 관리'
new_desc = '생산실적, 공정별 생산량 관리'
n = html.count(old_desc)
if n:
    html = html.replace(old_desc, new_desc)
    print(f'  생산수불 설명 수정: {n}개')
else:
    # 혹시 다른 형태일 경우 탐색
    alt_patterns = [
        '생산 실적',
        '공정별 수량',
    ]
    print(f'  생산수불 설명 원문 미발견. 검색 결과:')
    for ap in alt_patterns:
        idx = html.find(ap)
        if idx >= 0:
            print(f'    "{ap}" @ {idx}: ...{html[max(0,idx-30):idx+60]}...')

# ── 저장 ──────────────────────────────────────────────────────────────────
if html != original:
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'\n총 {count_total}개 색상 교체 완료. 저장됨.')
else:
    print('\n변경 없음.')
