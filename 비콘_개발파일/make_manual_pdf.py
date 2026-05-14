"""
비콘(주) 관리시스템 사용법 PDF 생성
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os

# ── 한글 폰트 등록 ───────────────────────────────────────────
FONT_PATH  = r'C:\Windows\Fonts\malgun.ttf'
FONTB_PATH = r'C:\Windows\Fonts\malgunbd.ttf'

pdfmetrics.registerFont(TTFont('Malgun', FONT_PATH))
pdfmetrics.registerFont(TTFont('MalgunB', FONTB_PATH))

# ── 색상 ────────────────────────────────────────────────────
ORANGE  = colors.HexColor('#e65100')
ORANGE2 = colors.HexColor('#fff3e0')
GRAY1   = colors.HexColor('#f5f5f5')
GRAY2   = colors.HexColor('#e0e0e0')
DARK    = colors.HexColor('#212121')
MID     = colors.HexColor('#546e7a')
WHITE   = colors.white

# ── 스타일 ───────────────────────────────────────────────────
def S(name, **kw):
    defaults = dict(fontName='Malgun', fontSize=10, leading=16,
                    textColor=DARK, spaceAfter=4)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

sTitle   = S('title',   fontName='MalgunB', fontSize=22, leading=28,
             textColor=WHITE, alignment=TA_CENTER, spaceAfter=0)
sSub     = S('sub',     fontName='Malgun',  fontSize=11, leading=16,
             textColor=WHITE, alignment=TA_CENTER, spaceAfter=0)
sH1      = S('h1',      fontName='MalgunB', fontSize=15, leading=20,
             textColor=WHITE, spaceAfter=4)
sH2      = S('h2',      fontName='MalgunB', fontSize=12, leading=18,
             textColor=ORANGE, spaceAfter=2)
sH3      = S('h3',      fontName='MalgunB', fontSize=10, leading=15,
             textColor=DARK, spaceAfter=2)
sBody    = S('body',    fontSize=9.5, leading=15, spaceAfter=3)
sBullet  = S('bullet',  fontSize=9.5, leading=15, leftIndent=12, spaceAfter=2)
sNote    = S('note',    fontSize=8.5, leading=13, textColor=MID,
             leftIndent=8, spaceAfter=3)
sCenter  = S('center',  fontSize=9,   leading=14, alignment=TA_CENTER)
sSmall   = S('small',   fontSize=8,   leading=12, textColor=MID)

W, H = A4
OUT = r'C:\Users\user\Desktop\비콘㈜_관리시스템_사용설명서.pdf'

# ── 헬퍼 ────────────────────────────────────────────────────
def hr(): return HRFlowable(width='100%', thickness=0.5,
                             color=GRAY2, spaceAfter=6, spaceBefore=4)

def section_title(text):
    """주황 배경 섹션 제목 박스"""
    tbl = Table([[Paragraph(text, sH1)]], colWidths=[W - 40*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ORANGE),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [6]),
    ]))
    return tbl

def info_box(rows, col_widths=None):
    """정보 박스 테이블"""
    cw = col_widths or [35*mm, W - 40*mm - 35*mm]
    data = [[Paragraph(str(k), sH3), Paragraph(str(v), sBody)]
            for k, v in rows]
    tbl = Table(data, colWidths=cw)
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), ORANGE2),
        ('BACKGROUND',    (1,0), (1,-1), WHITE),
        ('GRID',          (0,0), (-1,-1), 0.5, GRAY2),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return tbl

def step_table(steps):
    """순서 테이블 (번호 + 내용)"""
    data = [[Paragraph(f'<b>{i+1}</b>', sCenter),
             Paragraph(s, sBody)] for i, s in enumerate(steps)]
    tbl = Table(data, colWidths=[10*mm, W - 40*mm - 10*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), ORANGE),
        ('TEXTCOLOR',     (0,0), (0,-1), WHITE),
        ('ALIGN',         (0,0), (0,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',          (0,0), (-1,-1), 0.5, GRAY2),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 7),
        ('RIGHTPADDING',  (0,0), (-1,-1), 7),
        ('ROWBACKGROUNDS', (1,0), (1,-1), [WHITE, GRAY1]),
    ]))
    return tbl

def tip_box(text):
    tbl = Table([[Paragraph('💡 ' + text, sNote)]],
                colWidths=[W - 40*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffde7')),
        ('BOX',        (0,0), (-1,-1), 0.5, colors.HexColor('#ffe082')),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ]))
    return tbl

def warn_box(text):
    tbl = Table([[Paragraph('⚠️ ' + text, sNote)]],
                colWidths=[W - 40*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffebee')),
        ('BOX',        (0,0), (-1,-1), 0.5, colors.HexColor('#ef9a9a')),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ]))
    return tbl

def B(text): return f'<b>{text}</b>'
def sp(n=1): return Spacer(1, n*4*mm)

# ════════════════════════════════════════════════════════════
# 콘텐츠 빌드
# ════════════════════════════════════════════════════════════
story = []

# ── 표지 ────────────────────────────────────────────────────
cover = Table(
    [[Paragraph('🏭', S('ic', fontSize=48, alignment=TA_CENTER))],
     [Paragraph('비콘㈜ 관리시스템', sTitle)],
     [Paragraph('사용 설명서', sSub)],
     [Spacer(1, 6*mm)],
     [Paragraph('재고수불 · 생산수불', sSub)],
    ],
    colWidths=[W - 40*mm]
)
cover.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), ORANGE),
    ('TOPPADDING',    (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING',   (0,0), (-1,-1), 15),
    ('RIGHTPADDING',  (0,0), (-1,-1), 15),
    ('ROUNDEDCORNERS', [10]),
]))
story += [sp(8), cover, sp(4)]

story.append(Paragraph(
    '본 문서는 비콘㈜ 관리시스템 웹앱의 사용 방법을 설명합니다.<br/>'
    '재고수불(야적장 입·출고 관리)과 생산수불(생산실적 관리) 두 가지 모듈로 구성됩니다.',
    S('intro', fontSize=10, leading=16, alignment=TA_CENTER, textColor=MID)
))
story.append(PageBreak())

# ── 목차 ────────────────────────────────────────────────────
story.append(section_title('📋  목  차'))
story.append(sp())
toc_items = [
    ('1', '시작하기 — 로그인'),
    ('2', '홈 화면'),
    ('3', '재고수불 — 지도 탭'),
    ('4', '재고수불 — 입고 탭'),
    ('5', '재고수불 — 출고 탭'),
    ('6', '재고수불 — 재고 탭'),
    ('7', '재고수불 — 설정 탭'),
    ('8', '생산수불'),
    ('9', '관리자 기능'),
    ('10', '자주 묻는 질문(FAQ)'),
]
toc_data = [[Paragraph(B(n), sCenter), Paragraph(t, sBody)] for n, t in toc_items]
toc_tbl = Table(toc_data, colWidths=[10*mm, W - 40*mm - 10*mm])
toc_tbl.setStyle(TableStyle([
    ('ROWBACKGROUNDS', (0,0), (-1,-1), [WHITE, GRAY1]),
    ('GRID',          (0,0), (-1,-1), 0.3, GRAY2),
    ('TOPPADDING',    (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND',    (0,0), (0,-1), ORANGE2),
]))
story += [toc_tbl, PageBreak()]

# ════════════════════════════════════════════════════════════
# 1. 로그인
# ════════════════════════════════════════════════════════════
story.append(section_title('1.  시작하기 — 로그인'))
story.append(sp())
story.append(Paragraph(
    '앱에 처음 접속하면 로그인 화면이 나타납니다. '
    'Firebase 인증을 사용하므로 관리자가 발급한 이메일/비밀번호로 로그인합니다.',
    sBody))
story.append(sp())
story.append(step_table([
    '브라우저에서 앱 URL(예: vicon-app.vercel.app)에 접속합니다.',
    '이메일 주소와 비밀번호를 입력합니다.',
    '로그인 유지(자동 로그인)를 원하면 체크박스를 선택합니다.',
    '로그인 버튼을 누릅니다. 인증 성공 시 홈 화면으로 이동합니다.',
]))
story.append(sp())
story.append(tip_box('로그인 정보가 없을 경우 Firebase Console에서 계정을 생성하거나 관리자에게 문의하세요.'))
story.append(warn_box('비밀번호를 잊어버린 경우 Firebase Console → Authentication → 해당 사용자 → 비밀번호 재설정 이메일 발송으로 처리합니다.'))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 2. 홈 화면
# ════════════════════════════════════════════════════════════
story.append(section_title('2.  홈 화면'))
story.append(sp())
story.append(Paragraph(
    '로그인 후 표시되는 메인 화면입니다. 사용할 업무 모듈을 선택합니다.',
    sBody))
story.append(sp())
story.append(info_box([
    ('📦 재고수불', '야적장 입고·출고·구역별 재고 현황을 관리합니다.'),
    ('🏗️ 생산수불', '생산실적, 공정별 생산량을 기록하고 조회합니다.'),
    ('로그아웃',    '우측 상단 로그아웃 버튼을 눌러 계정에서 나갑니다.'),
], col_widths=[35*mm, W - 40*mm - 35*mm]))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 3. 재고수불 — 지도
# ════════════════════════════════════════════════════════════
story.append(section_title('3.  재고수불 — 지도 탭 🗺️'))
story.append(sp())
story.append(Paragraph(
    '야적장 전체 구역(A~K)의 재고 현황을 지도 위에 시각적으로 표시합니다.',
    sBody))
story.append(sp())
story.append(Paragraph(B('구역 구성'), sH2))
zones_data = [
    ['구역', '위치/설명'],
    ['A, B, C', '상단 좌측 구역'],
    ['D', '좌측 중단 구역'],
    ['E, F', '중앙 구역'],
    ['G, H', '중하단 구역'],
    ['I', '우측 상단 구역'],
    ['J, K', '우측 하단 구역'],
]
ztbl = Table(zones_data, colWidths=[30*mm, W - 40*mm - 30*mm])
ztbl.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), ORANGE),
    ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
    ('FONTNAME',      (0,0), (-1,0), 'MalgunB'),
    ('FONTNAME',      (0,1), (-1,-1), 'Malgun'),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, GRAY1]),
    ('GRID',          (0,0), (-1,-1), 0.5, GRAY2),
    ('TOPPADDING',    (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
]))
story += [ztbl, sp()]
story.append(Paragraph(B('구역 상세 조회'), sH2))
story.append(Paragraph(
    '지도에서 구역을 탭(클릭)하면 해당 구역에 적재된 재고 목록이 팝업으로 표시됩니다. '
    '현장명, 패킹 번호, 수량 등을 확인할 수 있습니다.',
    sBody))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 4. 재고수불 — 입고
# ════════════════════════════════════════════════════════════
story.append(section_title('4.  재고수불 — 입고 탭 📥'))
story.append(sp())
story.append(Paragraph(
    '작업지시서 또는 생산계획표 QR을 스캔하여 야적장에 자재를 입고 처리합니다.',
    sBody))
story.append(sp())
story.append(Paragraph(B('QR 입고 절차'), sH2))
story.append(step_table([
    '입고 탭을 선택합니다.',
    '"📷 QR 스캔 시작" 버튼을 누릅니다.',
    '카메라가 활성화되면 작업지시서(job_order) 또는 생산계획표(plan) QR 코드를 카메라에 비춥니다.',
    'QR 인식 성공 시 스캔 결과(업체명, 현장명, 패킹 범위 등)가 표시됩니다.',
    '적재 구역 선택 팝업이 뜨면 야적장 구역(A~K 중 하나)을 선택합니다.',
    '"적재 확정" 버튼을 눌러 입고 완료합니다.',
]))
story.append(sp())
story.append(Paragraph(B('지원 QR 타입'), sH2))
story.append(info_box([
    ('job_order', '작업지시서 QR — 업체명, 현장명, 패킹 번호 범위 포함'),
    ('plan',      '생산계획표 QR — 패킹 번호 목록 포함'),
], col_widths=[28*mm, W - 40*mm - 28*mm]))
story.append(sp())
story.append(tip_box('이미 재고에 존재하는 패킹 번호가 있을 경우 "이미 재고 있음" 경고가 표시됩니다. 중복 입고를 방지합니다.'))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 5. 재고수불 — 출고
# ════════════════════════════════════════════════════════════
story.append(section_title('5.  재고수불 — 출고 탭 📤'))
story.append(sp())
story.append(Paragraph(
    '출고송장 QR을 스캔하거나, QR이 없을 경우 재고에서 직접 패킹을 선택하여 출고 처리합니다.',
    sBody))
story.append(sp())
story.append(Paragraph(B('QR 출고 절차'), sH2))
story.append(step_table([
    '출고 탭을 선택합니다.',
    '"📷 QR 스캔 시작" 버튼을 누릅니다.',
    '출고송장(shipment) QR 코드를 카메라에 비춥니다.',
    '스캔 결과에서 출고 대상 패킹 목록을 확인합니다.',
    '"출고 확정" 버튼을 눌러 완료합니다.',
]))
story.append(sp())
story.append(Paragraph(B('수동 출고 (QR 누락 시)'), sH2))
story.append(step_table([
    '"📋 재고에서 직접 출고" 버튼을 누릅니다.',
    '현장 목록에서 출고할 현장을 선택합니다.',
    '패킹 번호를 체크박스로 선택합니다. "전체선택" 버튼으로 한꺼번에 선택 가능합니다.',
    '"출고 확정" 버튼을 눌러 완료합니다.',
]))
story.append(sp())
story.append(warn_box('출고 처리된 패킹은 재고 목록에서 제거됩니다. 출고 전 대상 패킹을 반드시 확인하세요.'))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 6. 재고수불 — 재고
# ════════════════════════════════════════════════════════════
story.append(section_title('6.  재고수불 — 재고 탭 📋'))
story.append(sp())
story.append(Paragraph(
    '현재 야적장에 보관 중인 모든 자재의 재고 목록을 조회합니다.',
    sBody))
story.append(sp())
story.append(Paragraph(B('주요 기능'), sH2))
story.append(info_box([
    ('검색',        '의뢰번호 또는 현장명으로 빠르게 검색합니다.'),
    ('구역 필터',   '상단 버튼(A~K)을 눌러 특정 구역의 재고만 표시합니다.'),
    ('새로고침',    '🔄 버튼으로 최신 데이터를 다시 불러옵니다.'),
    ('상세 조회',   '목록에서 항목을 탭하면 해당 현장의 상세 패킹 정보(장수, 면적 등)가 팝업으로 표시됩니다.'),
    ('통계',        '상단 통계 카드에서 총 현장 수, 패킹 수, 전체 면적을 한 눈에 확인합니다.'),
], col_widths=[25*mm, W - 40*mm - 25*mm]))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 7. 재고수불 — 설정
# ════════════════════════════════════════════════════════════
story.append(section_title('7.  재고수불 — 설정 탭 ⚙️'))
story.append(sp())
story.append(Paragraph(B('사용자 이름 설정'), sH2))
story.append(Paragraph(
    '입·출고 기록에 남길 담당자 이름을 설정합니다. 이름 입력 후 저장 버튼을 누릅니다.',
    sBody))
story.append(sp())
story.append(Paragraph(B('관리자 모드'), sH2))
story.append(Paragraph('관리자 PIN(초기값: 1234)을 입력하면 관리자 전용 메뉴가 활성화됩니다.', sBody))
story.append(sp())
story.append(Paragraph(B('관리자 전용 기능'), sH2))
story.append(info_box([
    ('Firebase 설정',   'Firebase Console에서 발급받은 firebaseConfig JSON을 입력해 데이터베이스를 연결합니다.'),
    ('QR 코드 생성',    'JSON 형식 데이터를 입력하면 QR 이미지를 즉시 생성합니다. VBA 출력용으로 활용 가능합니다.'),
    ('재고 삭제',       '패킹번호 단위로 삭제할 항목을 체크박스로 선택 후 일괄 삭제합니다. 되돌릴 수 없습니다.'),
    ('데이터 백업',     '전체 재고 데이터를 JSON 파일로 다운로드합니다. 날짜 범위를 지정하여 부분 백업도 가능합니다.'),
    ('PIN 변경',        '관리자 PIN을 새로운 값으로 변경합니다 (4자리 이상).'),
], col_widths=[28*mm, W - 40*mm - 28*mm]))
story.append(sp())
story.append(warn_box('재고 삭제는 복구가 불가능합니다. 삭제 전 반드시 데이터 백업을 수행하세요.'))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 8. 생산수불
# ════════════════════════════════════════════════════════════
story.append(section_title('8.  생산수불 🏗️'))
story.append(sp())
story.append(Paragraph(
    '생산 실적을 입력하고 공정별·일별 생산량을 현황표로 조회합니다. '
    '메가데크, 기가데크, 테라데크 등 제품 유형별로 관리합니다.',
    sBody))
story.append(sp())

story.append(Paragraph(B('생산 실적 입력'), sH2))
story.append(step_table([
    '생산수불 화면에서 제품 유형(메가데크 / 기가데크 / 테라데크 등)을 상단 탭에서 선택합니다.',
    '"입력" 또는 "실적 추가" 탭으로 이동합니다.',
    '생산일자, 호기(설비), 주·야간 구분, 면적(m²) 또는 장수를 입력합니다.',
    '저장 버튼을 눌러 실적을 기록합니다.',
]))
story.append(sp())

story.append(Paragraph(B('현황표 조회'), sH2))
story.append(Paragraph(
    '입력된 실적은 현황표 탭에서 날짜별·호기별·주야별로 정리된 표로 확인합니다. '
    '각 셀은 실선으로 구분되어 가독성이 높습니다.',
    sBody))
story.append(sp())
story.append(info_box([
    ('생산일자',    '생산이 이루어진 날짜'),
    ('호기',        '사용한 생산 설비 번호 (1호기, 2호기 등)'),
    ('주/야간',     '주간 또는 야간 생산 구분'),
    ('면적 (m²)',  '해당 일·호기·시간대의 생산 면적'),
    ('일 합계',     '해당 날짜의 전체 호기 합산 생산량'),
    ('월 합계',     '해당 월의 전체 생산량 합계'),
], col_widths=[25*mm, W - 40*mm - 25*mm]))
story.append(sp())
story.append(Paragraph(B('기록 수정/삭제'), sH2))
story.append(Paragraph(
    '현황표에서 특정 기록을 탭하면 수정 화면으로 이동하거나 삭제할 수 있습니다.',
    sBody))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════
# 9. 관리자 기능
# ════════════════════════════════════════════════════════════
story.append(section_title('9.  관리자 기능 🛡️'))
story.append(sp())
story.append(Paragraph(
    '관리자 PIN을 입력하여 활성화하는 고급 기능입니다.',
    sBody))
story.append(sp())

admin_data = [
    ['기능', '설명', '주의사항'],
    ['Firebase\n재연결',    'firebaseConfig를 새로 입력해 다른 프로젝트로 전환', '기존 데이터가 보이지 않을 수 있음'],
    ['QR 생성',             'JSON 데이터 기반 QR 이미지 즉시 생성, 다운로드',   '—'],
    ['패킹별 삭제',         '현장 단위로 펼쳐서 패킹 번호별 선택 삭제',         '삭제 후 복구 불가'],
    ['데이터 백업',         '전체 또는 기간별 재고 JSON 파일 다운로드',          '정기적으로 수행 권장'],
    ['PIN 변경',            '관리자 접근 PIN을 4자리 이상으로 변경',             '초기값 1234 즉시 변경 권장'],
]
atbl = Table(admin_data, colWidths=[22*mm, W*0.45 - 20*mm, W*0.32 - 20*mm])
atbl.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), ORANGE),
    ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
    ('FONTNAME',      (0,0), (-1,0), 'MalgunB'),
    ('FONTNAME',      (0,1), (-1,-1), 'Malgun'),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, GRAY1]),
    ('GRID',          (0,0), (-1,-1), 0.5, GRAY2),
    ('TOPPADDING',    (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING',   (0,0), (-1,-1), 6),
    ('RIGHTPADDING',  (0,0), (-1,-1), 6),
    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ('FONTSIZE',      (0,0), (-1,-1), 8.5),
]))
story += [atbl, PageBreak()]

# ════════════════════════════════════════════════════════════
# 10. FAQ
# ════════════════════════════════════════════════════════════
story.append(section_title('10.  자주 묻는 질문 (FAQ) ❓'))
story.append(sp())

faqs = [
    ('QR이 인식되지 않아요.',
     '카메라 권한이 허용되어 있는지 확인하세요. 브라우저 설정에서 카메라 접근을 허용한 후 페이지를 새로고침하세요.'),
    ('로그인이 안 됩니다.',
     '이메일/비밀번호를 확인하세요. 오류 메시지가 팝업으로 표시됩니다. 계속 안 되면 관리자에게 계정 확인을 요청하세요.'),
    ('재고가 표시되지 않아요.',
     'Firebase 연결 상태를 확인하세요. 설정 탭 → 관리자 모드 → Firebase 설정에서 연결 상태를 확인합니다.'),
    ('이미 입고한 패킹이 다시 스캔됩니다.',
     '중복 입고 방지 기능이 동작 중입니다. 경고 팝업을 확인하고 필요한 경우 관리자가 해당 재고를 삭제 후 재입고하세요.'),
    ('관리자 PIN을 잊어버렸어요.',
     '브라우저 개발자 도구(F12) → 콘솔에서 localStorage를 확인하거나, '
     '비콘㈜ 관리자에게 문의하세요. 초기값은 1234입니다.'),
    ('데이터가 삭제되지 않아요.',
     '관리자 모드가 활성화되어 있는지 확인하세요. 재고 삭제 기능은 관리자 전용입니다.'),
    ('앱이 느려요 / 로딩이 길어요.',
     '인터넷 연결 상태를 확인하세요. Firebase는 실시간 DB이므로 네트워크 속도에 영향을 받습니다.'),
    ('백업 파일은 어디에 저장되나요?',
     '브라우저의 기본 다운로드 폴더에 JSON 파일로 저장됩니다. '
     '파일명 형식: inventory_backup_YYYYMMDD_HHMMSS.json'),
]

for q, a in faqs:
    q_tbl = Table(
        [[Paragraph('Q. ' + q, S('fq', fontName='MalgunB', fontSize=9.5, textColor=WHITE))],
         [Paragraph('A. ' + a, S('fa', fontName='Malgun',  fontSize=9,   textColor=DARK, leftIndent=4))]],
        colWidths=[W - 40*mm]
    )
    q_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), ORANGE),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#fff8f0')),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, GRAY2),
    ]))
    story += [KeepTogether(q_tbl), sp(0.5)]

story.append(sp(2))

# 하단 메모
footer_tbl = Table([[Paragraph(
    '비콘㈜ 관리시스템  |  문의: 관리자  |  최종 수정: 2026년 5월',
    S('ft', fontSize=8, alignment=TA_CENTER, textColor=MID)
)]], colWidths=[W - 40*mm])
footer_tbl.setStyle(TableStyle([
    ('TOPPADDING',  (0,0), (-1,-1), 4),
    ('BACKGROUND',  (0,0), (-1,-1), GRAY1),
    ('BOX',         (0,0), (-1,-1), 0.3, GRAY2),
]))
story.append(footer_tbl)

# ════════════════════════════════════════════════════════════
# 페이지 번호 콜백
# ════════════════════════════════════════════════════════════
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Malgun', 8)
    canvas.setFillColor(MID)
    canvas.drawRightString(W - 20*mm, 12*mm,
                           f'비콘㈜ 관리시스템 사용설명서  |  {doc.page}')
    canvas.restoreState()

# ── PDF 빌드 ─────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    rightMargin=20*mm, leftMargin=20*mm,
    topMargin=18*mm,   bottomMargin=20*mm,
    title='비콘㈜ 관리시스템 사용설명서',
    author='비콘㈜',
)
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f'PDF 생성 완료: {OUT}')
