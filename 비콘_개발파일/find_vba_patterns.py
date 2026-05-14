import zipfile

fname = r'C:\Users\user\Desktop\메가데크 작업지시서 양식_자동화(260506).xlsm'
with zipfile.ZipFile(fname, 'r') as z:
    vba_bin = z.read('xl/vbaProject.bin')

patterns = [b'J1:K4', b'"J1"', b'Range("J1', b'ws.Range("J1"]']
for pattern in patterns:
    positions = [i for i in range(len(vba_bin)) if vba_bin[i:i+len(pattern)] == pattern]
    print(f'{pattern}: {len(positions)} at {positions[:8]}')
    for p in positions[:3]:
        print(f'  ctx: {repr(vba_bin[max(0,p-10):p+len(pattern)+10])}')
