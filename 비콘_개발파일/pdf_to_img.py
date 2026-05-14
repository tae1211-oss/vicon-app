from pdf2image import convert_from_path

images = convert_from_path(r'C:\Users\user\Desktop\S25C-1i26042917510.pdf', dpi=150)
for i, img in enumerate(images):
    path = rf'C:\Users\user\Desktop\클로드\yard_page_{i+1}.png'
    img.save(path)
    print(f'Saved: {path} ({img.size})')
