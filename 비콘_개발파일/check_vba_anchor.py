import zipfile

fname = r'C:\Users\user\Desktop\메가데크 작업지시서 양식_자동화(260506).xlsm'
with zipfile.ZipFile(fname, 'r') as z:
    vba_bin = z.read('xl/vbaProject.bin')

# Show broader context around position 78915 (the standalone J1)
pos = 78915
print("Bytes around pos 78915:")
print(repr(vba_bin[pos-30:pos+30]))
print()

# Also show as hex
chunk = vba_bin[pos-30:pos+30]
print("Hex:", ' '.join(f'{b:02x}' for b in chunk))
print()

# Show all 8 J1 occurrences with 30-byte context
pattern = b'J1'
positions = [i for i in range(len(vba_bin)) if vba_bin[i:i+2] == pattern]
for p in positions:
    ctx = vba_bin[max(0,p-15):p+20]
    print(f'pos={p}: {repr(ctx)}')
