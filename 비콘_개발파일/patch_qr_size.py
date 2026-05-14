"""
작업지시서 xlsm 파일의 QR 이미지 범위를 J1:K4 → I1:K5 로 패치
"""
import zipfile, shutil, os, re
from io import BytesIO

FILES = [
    r'C:\Users\user\Desktop\메가데크 작업지시서 양식_자동화(260506).xlsm',
    r'C:\Users\user\Desktop\기가데크 작업지시서 양식_자동화(260318).xlsm',
    r'C:\Users\user\Desktop\테라데크 작업지시서 양식(신).xlsm',
]

def patch_vba_bin(data: bytes) -> tuple[bytes, int]:
    """vbaProject.bin 바이너리에서 J1:K4 → I1:K5 패치"""
    count = 0

    # 1) Range("J1:K4")  →  Range("I1:K5")
    #    P-code string literal: b9 00 05 00 "J1:K4" 00
    old1 = b'\xb9\x00\x05\x00J1:K4\x00'
    new1 = b'\xb9\x00\x05\x00I1:K5\x00'
    n = data.count(old1)
    if n:
        data = data.replace(old1, new1)
        count += n
        print(f'  [P-code] Range("J1:K4") → Range("I1:K5"): {n}개')

    # 2) ws.Range("J1") anchor → ws.Range("I1")
    #    P-code string literal: b9 00 02 00 "J1"
    old2 = b'\xb9\x00\x02\x00J1'
    new2 = b'\xb9\x00\x02\x00I1'
    n = data.count(old2)
    if n:
        data = data.replace(old2, new2)
        count += n
        print(f'  [P-code] Range("J1") → Range("I1"): {n}개')

    # 3) 메시지 텍스트 / 주석 중 남은 "J1:K4" 평문
    old3 = b'J1:K4'
    n = data.count(old3)
    if n:
        data = data.replace(old3, b'I1:K5')
        count += n
        print(f'  [text]  J1:K4 → I1:K5: {n}개')

    return data, count


for fpath in FILES:
    if not os.path.exists(fpath):
        print(f'파일 없음: {fpath}')
        continue

    fname = os.path.basename(fpath)
    print(f'\n=== {fname} ===')

    # 원본 읽기
    with open(fpath, 'rb') as f:
        raw = f.read()

    zin = zipfile.ZipFile(BytesIO(raw), 'r')

    # vbaProject.bin 확인
    try:
        vba_data = zin.read('xl/vbaProject.bin')
    except KeyError:
        print('  vbaProject.bin 없음 - 스킵')
        zin.close()
        continue

    # J1:K4 존재 여부 확인
    if b'J1:K4' not in vba_data and b'\xb9\x00\x02\x00J1' not in vba_data:
        print('  J1:K4 패턴 없음 - 스킵')
        zin.close()
        continue

    # 패치
    new_vba, total = patch_vba_bin(vba_data)
    if total == 0:
        print('  패치 없음')
        zin.close()
        continue

    # 백업
    bak = fpath.replace('.xlsm', '_backup.xlsm')
    if not os.path.exists(bak):
        shutil.copy2(fpath, bak)
        print(f'  백업: {os.path.basename(bak)}')

    # 새 ZIP 생성
    out_buf = BytesIO()
    with zipfile.ZipFile(out_buf, 'w', compression=zipfile.ZIP_DEFLATED) as dst:
        for item in zin.infolist():
            if item.filename == 'xl/vbaProject.bin':
                dst.writestr(item, new_vba)
            else:
                dst.writestr(item, zin.read(item.filename))

    zin.close()

    # 저장
    with open(fpath, 'wb') as f:
        f.write(out_buf.getvalue())

    print(f'  ✅ 완료 (총 {total}개 패치)')

print('\nDone.')
