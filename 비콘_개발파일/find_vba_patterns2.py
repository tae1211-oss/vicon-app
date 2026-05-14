import zipfile

fname = r'C:\Users\user\Desktop\메가데크 작업지시서 양식_자동화(260506).xlsm'
with zipfile.ZipFile(fname, 'r') as z:
    vba_bin = z.read('xl/vbaProject.bin')

# Search for just b'J1' to find anchor cell string
pattern = b'J1'
positions = [i for i in range(len(vba_bin)) if vba_bin[i:i+2] == pattern]
print(f'b"J1": {len(positions)} occurrences')
for p in positions[:15]:
    ctx = vba_bin[max(0,p-8):p+12]
    print(f'  pos={p}: {repr(ctx)}')
