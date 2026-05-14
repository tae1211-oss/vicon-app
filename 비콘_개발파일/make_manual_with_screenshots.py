"""
비콘㈜ 관리시스템 사용설명서 PDF - 실제 스크린샷 포함
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PIL import Image as PILImage
import os

# ── 폰트 등록 ─────────────────────────────────────────────
pdfmetrics.registerFont(TTFont('Malgun',  r'C:\Windows\Fonts\malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunB', r'C:\Windows\Fonts\malgunbd.ttf'))

ORANGE  = colors.HexColor('#e65100')
ORANGE2 = colors.HexColor('#fff3e0')
GRAY1   = colors.HexColor('#f8f8f8')
GRAY2   = colors.HexColor('#e0e0e0')
DARK    = colors.HexColor('#212121')
MID     = colors.HexColor('#546e7a')
WHITE   = colors.white
BLUE    = colors.HexColor('#1565c0')

W, H = A4
MARGIN = 18*mm
CONTENT_W = W - 2*MARGIN
SHOT_DIR = r'C:\Users\user\Desktop\클로드\screenshots'
OUT = r'C:\Users\user\Desktop\비콘㈜_관리시스템_사용설명서_v2.pdf'

def S(name, **kw):
    d = dict(fontName='Malgun', fontSize=10, leading=16, textColor=DARK, spaceAfter=3)
    d.update(kw)
    return ParagraphStyle(name, **d)

sTitleW = S('tw', fontName='MalgunB', fontSize=20, textColor=WHITE, alignment=TA_CENTER, leading=26)
sSubW   = S('sw', fontName='Malgun',  fontSize=10, textColor=WHITE, alignment=TA_CENTER, leading=15)
sH1     = S('h1', fontName='MalgunB', fontSize=14, textColor=WHITE, leading=20)
sH2     = S('h2', fontName='MalgunB', fontSize=11, textColor=ORANGE, leading=16, spaceBefore=6)
sH3     = S('h3', fontName='MalgunB', fontSize=9.5, textColor=DARK, leading=14, spaceBefore=4)
sBody   = S('body', fontSize=9.5, leading=15)
sBullet = S('bul', fontSize=9.5, leading=15, leftIndent=10)
sNote   = S('note', fontSize=8.5, leading=13, textColor=MID)
sSmall  = S('sm',   fontSize=8,   leading=12, textColor=MID, alignment=TA_CENTER)
sCaption= S('cap',  fontSize=8.5, leading=13, textColor=MID, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)
sStep   = S('step', fontSize=9,   leading=14, textColor=DARK)

def sp(n=1): return Spacer(1, n*3.5*mm)

def sec_title(text):
    t = Table([[Paragraph(text, sH1)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), ORANGE),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
        ('LEFTPADDING',   (0,0),(-1,-1), 12),
        ('RIGHTPADDING',  (0,0),(-1,-1), 12),
    ]))
    return t

def tip(text, warn=False):
    bg = colors.HexColor('#ffebee') if warn else colors.HexColor('#fffde7')
    bc = colors.HexColor('#ef9a9a') if warn else colors.HexColor('#ffe082')
    icon = 'red' if warn else 'yellow'
    prefix = '⚠️ ' if warn else '💡 '
    t = Table([[Paragraph(prefix + text, sNote)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), bg),
        ('BOX',        (0,0),(-1,-1), 0.5, bc),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
        ('RIGHTPADDING',  (0,0),(-1,-1), 10),
    ]))
    return t

def info_row(rows, w1=32*mm):
    w2 = CONTENT_W - w1
    data = [[Paragraph(str(k), sH3), Paragraph(str(v), sBody)] for k,v in rows]
    t = Table(data, colWidths=[w1, w2])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(0,-1), ORANGE2),
        ('GRID',          (0,0),(-1,-1), 0.5, GRAY2),
        ('TOPPADDING',    (0,0),(-1,-1), 5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 5),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
    ]))
    return t

def steps(items):
    data = [[Paragraph(f'<b>{i+1}</b>', S('sn', fontName='MalgunB', fontSize=9, textColor=WHITE, alignment=TA_CENTER)),
             Paragraph(s, sStep)] for i,s in enumerate(items)]
    t = Table(data, colWidths=[9*mm, CONTENT_W-9*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(0,-1), ORANGE),
        ('ROWBACKGROUNDS',(1,0),(1,-1), [WHITE, GRAY1]),
        ('GRID',          (0,0),(-1,-1), 0.4, GRAY2),
        ('TOPPADDING',    (0,0),(-1,-1), 5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 5),
        ('LEFTPADDING',   (0,0),(-1,-1), 7),
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
        ('ALIGN',         (0,0),(0,-1), 'CENTER'),
    ]))
    return t

def screenshot(fname, caption='', max_h=110*mm):
    path = f'{SHOT_DIR}/{fname}'
    if not os.path.exists(path):
        return Paragraph(f'[이미지 없음: {fname}]', sNote)
    img = PILImage.open(path)
    iw, ih = img.size
    # 핸드폰 비율 유지하며 콘텐츠 폭에 맞춤
    phone_w = min(CONTENT_W * 0.55, 90*mm)
    scale   = phone_w / iw
    ph      = ih * scale
    if ph > max_h:
        scale  = max_h / ih
        phone_w = iw * scale
        ph      = max_h
    elems = []
    img_obj = Image(path, width=phone_w, height=ph)
    # 중앙 정렬을 위해 테이블로 감쌈
    t = Table([[img_obj]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('ALIGN',    (0,0),(-1,-1), 'CENTER'),
        ('VALIGN',   (0,0),(-1,-1), 'MIDDLE'),
        ('BOX',      (0,0),(-1,-1), 1, GRAY2),
        ('TOPPADDING',    (0,0),(-1,-1), 4),
        ('BOTTOMPADDING', (0,0),(-1,-1), 4),
        ('BACKGROUND',    (0,0),(-1,-1), GRAY1),
    ]))
    elems.append(t)
    if caption:
        elems.append(Paragraph(caption, sCaption))
    return elems

def two_shots(f1, cap1, f2, cap2, max_h=100*mm):
    """두 화면을 나란히"""
    def make_img(fname, cap, w):
        path = f'{SHOT_DIR}/{fname}'
        if not os.path.exists(path):
            return [Paragraph(f'[없음:{fname}]', sNote)]
        img = PILImage.open(path)
        iw, ih = img.size
        scale = w / iw
        ph = ih * scale
        if ph > max_h:
            scale = max_h / ih
            w = iw * scale
            ph = max_h
        return [Image(path, width=w, height=ph), Paragraph(cap, sCaption)]
    col_w = (CONTENT_W - 6*mm) / 2
    left  = make_img(f1, cap1, col_w)
    right = make_img(f2, cap2, col_w)
    # pad to same length
    while len(left) < len(right): left.append(Spacer(1,1))
    while len(right) < len(left): right.append(Spacer(1,1))
    rows = list(zip(left, right))
    t = Table(rows, colWidths=[col_w, col_w], hAlign='CENTER')
    t.setStyle(TableStyle([
        ('ALIGN',    (0,0),(-1,-1), 'CENTER'),
        ('VALIGN',   (0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING',  (0,0),(-1,-1), 3),
        ('RIGHTPADDING', (0,0),(-1,-1), 3),
    ]))
    return t

def add_page_num(canvas, doc):
    canvas.saveState()
    canvas.setFont('Malgun', 8)
    canvas.setFillColor(MID)
    canvas.drawRightString(W-MARGIN, 12*mm, f'비콘(주) 관리시스템 사용설명서  |  {doc.page}')
    canvas.restoreState()

# ════════════════════════════════════════════════════════════
story = []

# ── 표지 ─────────────────────────────────────────────────
cover = Table([
    [Paragraph('🏭', S('ic', fontSize=44, alignment=TA_CENTER))],
    [Paragraph('비콘㈜ 관리시스템', sTitleW)],
    [Spacer(1, 3*mm)],
    [Paragraph('사용 설명서', sSubW)],
    [Spacer(1, 2*mm)],
    [Paragraph('재고수불 · 생산수불', sSubW)],
], colWidths=[CONTENT_W])
cover.setStyle(TableStyle([
    ('BACKGROUND',    (0,0),(-1,-1), ORANGE),
    ('TOPPADDING',    (0,0),(-1,-1), 10),
    ('BOTTOMPADDING', (0,0),(-1,-1), 10),
    ('LEFTPADDING',   (0,0),(-1,-1), 15),
    ('RIGHTPADDING',  (0,0),(-1,-1), 15),
]))
story += [sp(6), cover, sp(3)]
story.append(Paragraph('본 문서는 비콘㈜ 관리시스템 웹앱의 전체 사용 방법을 실제 화면 이미지와 함께 설명합니다.',
    S('intro', fontSize=9.5, leading=15, alignment=TA_CENTER, textColor=MID)))
story.append(PageBreak())

# ── 목차 ─────────────────────────────────────────────────
story.append(sec_title('📋  목  차'))
story.append(sp())
toc = [
    ('1', '로그인'),
    ('2', '홈 화면'),
    ('3', '재고수불 — 지도 탭'),
    ('4', '재고수불 — 입고 탭 (QR 스캔)'),
    ('5', '재고수불 — 출고 탭'),
    ('6', '재고수불 — 재고 탭'),
    ('7', '재고수불 — 설정 탭'),
    ('8', '생산수불'),
    ('9', '관리자 전용 기능'),
    ('10', '자주 묻는 질문 (FAQ)'),
]
td = [[Paragraph(f'<b>{n}</b>', S('tn', fontName='MalgunB', fontSize=9, alignment=TA_CENTER)), Paragraph(t, sBody)] for n,t in toc]
tt = Table(td, colWidths=[10*mm, CONTENT_W-10*mm])
tt.setStyle(TableStyle([
    ('ROWBACKGROUNDS', (0,0),(-1,-1), [WHITE, GRAY1]),
    ('GRID',          (0,0),(-1,-1), 0.3, GRAY2),
    ('TOPPADDING',    (0,0),(-1,-1), 6),
    ('BOTTOMPADDING', (0,0),(-1,-1), 6),
    ('LEFTPADDING',   (0,0),(-1,-1), 8),
    ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
    ('BACKGROUND',    (0,0),(0,-1), ORANGE2),
]))
story += [tt, PageBreak()]

# ════════════════════════════════════════════════════════════
# 1. 로그인
# ════════════════════════════════════════════════════════════
story.append(sec_title('1.  로그인'))
story.append(sp())
story.append(Paragraph('앱에 처음 접속하면 로그인 화면이 표시됩니다. Firebase 인증을 사용하므로 관리자가 발급한 이메일과 비밀번호로 로그인합니다.', sBody))
story.append(sp())

for e in screenshot('01_login.png', '▲ 로그인 화면'):
    story.append(e)
story.append(sp())

story.append(Paragraph('로그인 방법', sH2))
story.append(steps([
    '앱 URL에 접속합니다.',
    '이메일 주소와 비밀번호를 입력합니다.',
    '"로그인 유지" 체크박스를 선택하면 다음 접속 시 자동 로그인됩니다.',
    '로그인 버튼을 누릅니다. 성공하면 홈 화면으로 이동합니다.',
    '오류 발생 시 화면 하단에 오류 내용이 표시되고 팝업 알림이 뜹니다.',
]))
story.append(sp())
story.append(tip('계정이 없는 경우 Firebase Console → Authentication → 사용자 추가에서 이메일/비밀번호 계정을 생성하세요.'))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 2. 홈 화면
# ════════════════════════════════════════════════════════════
story.append(sec_title('2.  홈 화면'))
story.append(sp())
story.append(Paragraph('로그인 성공 후 표시되는 메인 메뉴 화면입니다. 사용할 업무 모듈을 선택합니다.', sBody))
story.append(sp())

for e in screenshot('02_home.png', '▲ 홈 화면 — 업무 모듈 선택'):
    story.append(e)
story.append(sp())

story.append(info_row([
    ('📦 재고수불', '야적장 입고·출고·구역별 재고 현황을 관리합니다. 탭하면 재고수불 화면으로 이동합니다.'),
    ('🏗️ 생산수불', '생산실적, 공정별 생산량을 기록하고 조회합니다. 탭하면 생산수불 화면으로 이동합니다.'),
    ('로그아웃',    '우측 상단 "로그아웃" 버튼을 눌러 계정에서 나갑니다.'),
]))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 3. 지도 탭
# ════════════════════════════════════════════════════════════
story.append(sec_title('3.  재고수불 — 지도 탭 🗺️'))
story.append(sp())
story.append(Paragraph('재고수불 화면의 첫 번째 탭입니다. 야적장 전체 구역(A~K)의 재고 현황을 지도 위에 시각적으로 표시합니다.', sBody))
story.append(sp())

for e in screenshot('03_map.png', '▲ 지도 탭 — 야적장 구역별 현황'):
    story.append(e)
story.append(sp())

story.append(Paragraph('구역 탭 조회 방법', sH2))
story.append(steps([
    '지도에서 조회할 구역(A~K 중 하나)을 탭(클릭)합니다.',
    '해당 구역에 적재된 현장 목록과 패킹 정보가 팝업으로 표시됩니다.',
    '"닫기" 버튼을 눌러 팝업을 닫습니다.',
]))
story.append(sp())
story.append(info_row([
    ('구역 A~C', '야적장 상단 좌측 구역'),
    ('구역 D~F', '야적장 중앙 구역'),
    ('구역 G~H', '야적장 중하단 구역'),
    ('구역 I',   '야적장 우측 상단 구역'),
    ('구역 J~K', '야적장 우측 하단 구역'),
], w1=22*mm))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 4. 입고 탭
# ════════════════════════════════════════════════════════════
story.append(sec_title('4.  재고수불 — 입고 탭 📥'))
story.append(sp())
story.append(Paragraph('작업지시서 또는 생산계획표 QR을 스캔하여 야적장에 자재를 입고 처리합니다.', sBody))
story.append(sp())

for e in screenshot('04_inbound.png', '▲ 입고 탭 — QR 스캔 입고'):
    story.append(e)
story.append(sp())

story.append(Paragraph('QR 입고 절차', sH2))
story.append(steps([
    '상단 탭에서 "📥 입고"를 선택합니다.',
    '"📷 QR 스캔 시작" 버튼을 누릅니다.',
    '카메라가 켜지면 작업지시서(job_order) 또는 생산계획표(plan) QR을 비춥니다.',
    'QR 인식 성공 시 업체명·현장명·패킹 번호 범위 등 스캔 결과가 표시됩니다.',
    '적재 구역 선택 팝업에서 적재할 구역(A~K)을 선택합니다.',
    '"✅ 적재 확정" 버튼을 눌러 입고를 완료합니다.',
]))
story.append(sp())
story.append(tip('이미 재고에 존재하는 패킹이 있으면 "이미 재고 있음" 경고가 표시됩니다. 중복 입고를 방지하는 기능입니다.'))
story.append(tip('스캔을 중단하려면 "■ 스캔 중지" 버튼을 누르세요.', warn=False))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 5. 출고 탭
# ════════════════════════════════════════════════════════════
story.append(sec_title('5.  재고수불 — 출고 탭 📤'))
story.append(sp())
story.append(Paragraph('출고송장 QR을 스캔하거나, QR이 없을 경우 재고 목록에서 직접 패킹을 선택해 출고 처리합니다.', sBody))
story.append(sp())

for e in screenshot('05_outbound.png', '▲ 출고 탭 — QR 스캔 출고'):
    story.append(e)
story.append(sp())

story.append(Paragraph('QR 출고 절차', sH2))
story.append(steps([
    '상단 탭에서 "📤 출고"를 선택합니다.',
    '"📷 QR 스캔 시작" 버튼을 누릅니다.',
    '출고송장(shipment) QR 코드를 카메라에 비춥니다.',
    '출고 대상 현장명과 패킹 목록을 확인합니다.',
    '"출고 확정" 버튼을 눌러 완료합니다.',
]))
story.append(sp())
story.append(Paragraph('수동 출고 (QR 없을 때)', sH2))
story.append(steps([
    '"📋 재고에서 직접 출고" 버튼을 누릅니다.',
    '현장 목록에서 출고할 현장을 선택합니다.',
    '패킹 번호 체크박스로 출고할 패킹을 선택합니다. "전체선택" 버튼 사용 가능.',
    '"출고 확정"을 눌러 완료합니다.',
]))
story.append(sp())
story.append(tip('출고 처리된 패킹은 재고 목록에서 자동으로 제거됩니다.', warn=True))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 6. 재고 탭
# ════════════════════════════════════════════════════════════
story.append(sec_title('6.  재고수불 — 재고 탭 📋'))
story.append(sp())
story.append(Paragraph('현재 야적장에 보관 중인 전체 재고를 조회합니다.', sBody))
story.append(sp())

for e in screenshot('06_inventory.png', '▲ 재고 탭 — 재고 목록'):
    story.append(e)
story.append(sp())

story.append(info_row([
    ('검색',      '상단 검색창에 의뢰번호 또는 현장명을 입력하면 실시간으로 필터링됩니다.'),
    ('구역 필터', '상단 구역 버튼(A~K, 전체)을 눌러 특정 구역 재고만 표시합니다.'),
    ('새로고침',  '🔄 버튼을 눌러 최신 데이터를 다시 불러옵니다.'),
    ('상세 조회', '목록 항목을 탭하면 해당 현장의 패킹별 세부 정보(장수, 면적 등)가 팝업으로 표시됩니다.'),
    ('통계',      '상단 카드에서 총 현장 수, 패킹 수, 전체 면적(m²)을 한눈에 확인합니다.'),
]))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 7. 설정 탭
# ════════════════════════════════════════════════════════════
story.append(sec_title('7.  재고수불 — 설정 탭 ⚙️'))
story.append(sp())
story.append(Paragraph('사용자 이름 설정 및 관리자 기능에 접근합니다.', sBody))
story.append(sp())

for e in screenshot('07_settings.png', '▲ 설정 탭'):
    story.append(e)
story.append(sp())

story.append(Paragraph('사용자 이름 설정', sH2))
story.append(steps([
    '"이름 (적재/출고 기록용)" 입력란에 담당자 이름을 입력합니다.',
    '"저장" 버튼을 누릅니다.',
    '입력한 이름이 입·출고 기록에 자동으로 표시됩니다.',
]))
story.append(sp())
story.append(Paragraph('관리자 로그인', sH2))
story.append(steps([
    '"관리자 PIN" 입력란에 PIN 번호를 입력합니다 (초기값: 1234).',
    '"로그인" 버튼을 누르면 관리자 전용 메뉴가 활성화됩니다.',
]))
story.append(sp())
story.append(tip('초기 관리자 PIN(1234)은 처음 사용 시 반드시 변경하세요.', warn=True))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 8. 생산수불
# ════════════════════════════════════════════════════════════
story.append(sec_title('8.  생산수불 🏗️'))
story.append(sp())
story.append(Paragraph('생산 실적을 입력하고 공정별·일별·월별 생산량을 현황표로 조회합니다.', sBody))
story.append(sp())

for e in screenshot('08_production.png', '▲ 생산수불 화면'):
    story.append(e)
story.append(sp())

story.append(Paragraph('생산 실적 입력', sH2))
story.append(steps([
    '상단 탭에서 제품 유형(메가데크 / 기가데크 / 테라데크 등)을 선택합니다.',
    '"실적 입력" 탭을 선택합니다.',
    '생산일자, 호기(설비), 주·야간 구분, 생산량(면적/장수)을 입력합니다.',
    '"저장" 버튼을 눌러 실적을 기록합니다.',
]))
story.append(sp())
story.append(Paragraph('현황표 조회', sH2))
story.append(steps([
    '"현황" 탭을 선택합니다.',
    '조회할 연도와 월을 선택합니다.',
    '생산일자·호기·주야간별로 정리된 표가 표시됩니다.',
    '표의 각 셀은 실선으로 구분되어 있습니다.',
    '특정 행을 탭하면 해당 기록을 수정하거나 삭제할 수 있습니다.',
]))
story.append(sp())
story.append(info_row([
    ('생산일자', '생산이 이루어진 날짜'),
    ('호기',     '생산 설비 번호 (1호기, 2호기 등)'),
    ('주/야간',  '주간 또는 야간 생산 구분'),
    ('면적(m²)', '해당 조건의 생산 면적'),
    ('일 합계',  '해당 날짜 전체 호기 합계'),
    ('월 합계',  '해당 월의 전체 생산량 합계'),
], w1=22*mm))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 9. 관리자 기능
# ════════════════════════════════════════════════════════════
story.append(sec_title('9.  관리자 전용 기능 🛡️'))
story.append(sp())
story.append(Paragraph('관리자 PIN으로 로그인하면 설정 탭에서 아래 기능들이 활성화됩니다.', sBody))
story.append(sp())

for e in screenshot('09_admin.png', '▲ 관리자 모드 활성화 시 설정 탭'):
    story.append(e)
story.append(sp())

story.append(info_row([
    ('Firebase 설정',   'Firebase Console에서 발급한 firebaseConfig JSON을 입력해 데이터베이스에 연결합니다.'),
    ('QR 코드 생성',    'JSON 데이터를 입력하면 QR 이미지를 즉시 생성합니다. Excel VBA 작업지시서 출력에 활용됩니다.'),
    ('패킹별 재고 삭제','현장별로 펼쳐서 패킹 번호 단위로 체크박스 선택 후 일괄 삭제합니다. 복구 불가.'),
    ('데이터 백업',     '전체 또는 기간별 재고를 JSON 파일로 다운로드합니다. 삭제 전 반드시 백업하세요.'),
    ('PIN 변경',        '관리자 PIN을 새 값으로 변경합니다 (4자리 이상 권장).'),
    ('관리자 로그아웃', '관리자 모드를 해제합니다. 일반 사용자 모드로 전환됩니다.'),
]))
story.append(sp())
story.append(tip('재고 삭제는 복구가 불가능합니다. 반드시 데이터 백업 후 진행하세요.', warn=True))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 10. FAQ
# ════════════════════════════════════════════════════════════
story.append(sec_title('10.  자주 묻는 질문 (FAQ) ❓'))
story.append(sp())

faqs = [
    ('QR이 인식되지 않습니다.',
     '① 브라우저 카메라 권한을 허용했는지 확인하세요.\n② 주소창 좌측 자물쇠 아이콘 → 카메라 권한 허용.\n③ QR 코드와 카메라 거리를 10~30cm로 유지하고 초점이 맞도록 하세요.'),
    ('로그인이 되지 않습니다.',
     '① 이메일/비밀번호가 올바른지 확인하세요.\n② 오류 메시지가 화면 하단에 표시됩니다.\n③ 계속 실패하면 Firebase Console에서 계정 상태를 확인하세요.'),
    ('재고 목록이 표시되지 않습니다.',
     '① Firebase 연결 여부를 확인하세요.\n② 설정 탭 → 관리자 모드 → Firebase 설정에서 연결 상태를 확인합니다.\n③ 인터넷 연결 상태를 확인하세요.'),
    ('이미 입고한 패킹이 또 스캔됩니다.',
     '중복 입고 방지 기능이 작동 중입니다. 팝업 경고를 확인하고, 필요하면 관리자가 해당 재고를 삭제 후 재입고하세요.'),
    ('관리자 PIN을 잊어버렸습니다.',
     '초기값은 1234입니다. 변경했다면 비콘㈜ 시스템 관리자에게 문의하세요.'),
    ('백업 파일은 어디에 저장됩니까?',
     '브라우저 기본 다운로드 폴더에 JSON 파일로 저장됩니다.\n파일명: inventory_backup_YYYYMMDD_HHMMSS.json'),
    ('앱이 느리거나 데이터가 늦게 로딩됩니다.',
     'Firebase는 실시간 DB로 인터넷 속도에 영향을 받습니다. Wi-Fi 또는 LTE 환경에서 사용을 권장합니다.'),
    ('생산 실적을 잘못 입력했습니다.',
     '현황 탭에서 해당 행을 탭하면 수정 화면으로 이동합니다. 수정 후 저장하거나 삭제할 수 있습니다.'),
]

for q, a in faqs:
    q_tbl = Table([
        [Paragraph('Q.  ' + q, S('fq', fontName='MalgunB', fontSize=9.5, textColor=WHITE))],
        [Paragraph(a.replace('\n', '<br/>'), S('fa', fontSize=9, leading=15, leftIndent=4))],
    ], colWidths=[CONTENT_W])
    q_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(0,0), ORANGE),
        ('BACKGROUND',    (0,1),(0,1), colors.HexColor('#fff8f0')),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
        ('RIGHTPADDING',  (0,0),(-1,-1), 10),
        ('BOX',           (0,0),(-1,-1), 0.5, GRAY2),
    ]))
    story.append(KeepTogether(q_tbl))
    story.append(sp(0.5))

story.append(sp(2))
ft = Table([[Paragraph('비콘㈜ 관리시스템  |  문의: 관리자  |  2026년 5월',
    S('ft', fontSize=8, alignment=TA_CENTER, textColor=MID))]], colWidths=[CONTENT_W])
ft.setStyle(TableStyle([
    ('BACKGROUND', (0,0),(-1,-1), GRAY1),
    ('BOX',        (0,0),(-1,-1), 0.3, GRAY2),
    ('TOPPADDING',    (0,0),(-1,-1), 5),
    ('BOTTOMPADDING', (0,0),(-1,-1), 5),
]))
story.append(ft)

# ── 빌드 ─────────────────────────────────────────────────
doc = SimpleDocTemplate(OUT, pagesize=A4,
    rightMargin=MARGIN, leftMargin=MARGIN,
    topMargin=16*mm, bottomMargin=20*mm,
    title='비콘㈜ 관리시스템 사용설명서')
doc.build(story, onFirstPage=add_page_num, onLaterPages=add_page_num)
print('PDF saved:', OUT)
