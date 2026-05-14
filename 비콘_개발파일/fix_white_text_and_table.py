"""
1. 주황 배경 위 흰 글자 → 검정으로 변경
2. prod-stat-table 칸 구분선 추가
"""

fpath = r'C:\Users\user\Desktop\클로드\index.html'
with open(fpath, 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# ══════════════════════════════════════════════════════════════
# 1) 주황/오렌지 배경 위 흰 글자 → 검정
# ══════════════════════════════════════════════════════════════
replacements = [
    # 헤더
    ('header{background:#e65100;color:#fff;', 'header{background:#e65100;color:#000;'),
    # 버튼
    ('.btn-primary{background:#e65100;color:#fff}', '.btn-primary{background:#e65100;color:#000}'),
    ('.btn-warning{background:#e65100;color:#fff}', '.btn-warning{background:#e65100;color:#000}'),
    # zone pill 배지
    ('background:#e65100;color:#fff;border-radius:4px', 'background:#e65100;color:#000;border-radius:4px'),
    # zone 선택 버튼
    ('.zone-btn-pick.selected{background:#e65100;color:#fff;', '.zone-btn-pick.selected{background:#e65100;color:#000;'),
    # 로그인 버튼
    ('.btn-login{width:100%;padding:14px;background:#f57c00;color:#fff;', '.btn-login{width:100%;padding:14px;background:#f57c00;color:#000;'),
    # 일보 다운로드 버튼
    ('.dr-btn-dl{background:#f57c00;color:#fff;', '.dr-btn-dl{background:#f57c00;color:#000;'),
    # 홈화면 텍스트 (주황 그라디언트 위)
    ('.home-header{padding:40px 24px 20px;color:#fff;', '.home-header{padding:40px 24px 20px;color:#000;'),
    ('.home-back{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.18);border:none;color:#fff;',
     '.home-back{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.18);border:none;color:#000;'),
    # 홈 유저 정보/로그아웃
    ('.home-user-info{color:rgba(255,255,255,.85);', '.home-user-info{color:rgba(0,0,0,.75);'),
    ('.btn-logout{background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.35);color:#fff;',
     '.btn-logout{background:rgba(255,255,255,.2);border:1px solid rgba(0,0,0,.2);color:#000;'),
    # 인라인 스타일 (JS에서 생성되는 버튼들)
    ('background:#f57c00;color:#fff;font-weight:700', 'background:#f57c00;color:#000;font-weight:700'),
    ('background:#f57c00;color:#fff;border:none', 'background:#f57c00;color:#000;border:none'),
]

for old, new in replacements:
    n = html.count(old)
    if n:
        html = html.replace(old, new)
        print(f'  [흰글자→검정] {n}개: {old[:50]}...')
    else:
        print(f'  [미발견] {old[:50]}...')

# ══════════════════════════════════════════════════════════════
# 2) prod-stat-table 칸 구분 실선 추가
# ══════════════════════════════════════════════════════════════
# th: border 추가
old_th = '.prod-stat-table th{background:#fff3e0;color:#37474f;font-weight:700;padding:6px 7px;text-align:center;white-space:nowrap;position:sticky;top:0}'
new_th = '.prod-stat-table th{background:#fff3e0;color:#37474f;font-weight:700;padding:6px 7px;text-align:center;white-space:nowrap;position:sticky;top:0;border:1px solid #bdbdbd}'

# td: border-bottom만 있던 것을 4면 실선으로
old_td = '.prod-stat-table td{padding:5px 7px;border-bottom:1px solid #f0f0f0;text-align:center;white-space:nowrap}'
new_td = '.prod-stat-table td{padding:5px 7px;border:1px solid #bdbdbd;text-align:center;white-space:nowrap}'

for old, new, label in [(old_th, new_th, 'th 테두리'), (old_td, new_td, 'td 테두리')]:
    n = html.count(old)
    if n:
        html = html.replace(old, new)
        print(f'  [테이블 {label}] {n}개 수정')
    else:
        print(f'  [미발견] {label}: {old[:60]}')

# ══════════════════════════════════════════════════════════════
# 저장
# ══════════════════════════════════════════════════════════════
if html != original:
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)
    print('\n저장 완료.')
else:
    print('\n변경 없음.')
