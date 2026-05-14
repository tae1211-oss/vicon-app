import fitz  # PyMuPDF

doc = fitz.open(r'C:\Users\user\Desktop\S25C-1i26042917510.pdf')
print(f'Pages: {len(doc)}')
for i, page in enumerate(doc):
    mat = fitz.Matrix(2, 2)  # 2x zoom = ~150dpi
    pix = page.get_pixmap(matrix=mat)
    path = rf'C:\Users\user\Desktop\클로드\yard_page_{i+1}.png'
    pix.save(path)
    print(f'Saved: {path} ({pix.width}x{pix.height})')
doc.close()
