import pdfplumber

with pdfplumber.open(r'C:\Users\user\Desktop\S25C-1i26042917510.pdf') as pdf:
    print(f'Pages: {len(pdf.pages)}')
    for i, page in enumerate(pdf.pages):
        print(f'--- Page {i+1} | Size: {int(page.width)} x {int(page.height)} ---')
        text = page.extract_text()
        if text:
            print(text[:5000])
        print(f'Rects: {len(page.rects)}, Lines: {len(page.lines)}, Chars: {len(page.chars)}')
        for r in page.rects[:30]:
            print(f'  rect: x0={r["x0"]:.0f} y0={r["y0"]:.0f} x1={r["x1"]:.0f} y1={r["y1"]:.0f} w={r["x1"]-r["x0"]:.0f} h={r["y1"]-r["y0"]:.0f}')
        # Also print word positions
        words = page.extract_words()
        print(f'Words ({len(words)}):')
        for w in words:
            print(f'  "{w["text"]}" x0={w["x0"]:.0f} y0={w["y0"]:.0f} x1={w["x1"]:.0f} y1={w["y1"]:.0f}')
