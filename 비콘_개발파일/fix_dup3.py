with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 직접 인덱스 기반으로 교체 (한글+이스케이프 문자 문제 우회)
# 찾을 패턴: dupPacks 정의 + alert 호출 + return
search_start = "      const dupPacks = sel.filter(n => registeredPacks.includes(n));\n      if (dupPacks.length > 0) {\n        alert("
search_end   = "        return;\n      }"

new_block = """      const dupPacks = sel.filter(n => registeredPacks.includes(n));
      if (dupPacks.length > 0) {
        showDupWarning(dupPacks, dupRecordMap);
        return;
      }"""

count = 0
pos = 0
while True:
    idx_start = html.find(search_start, pos)
    if idx_start == -1:
        break
    idx_end = html.find(search_end, idx_start)
    if idx_end == -1:
        break
    idx_end += len(search_end)
    html = html[:idx_start] + new_block + html[idx_end:]
    pos = idx_start + len(new_block)
    count += 1

print(f'replaced: {count}')

# registeredPacks 수집 부분도 교체 (dupRecordMap 추가)
old_reg = """      const registeredPacks = [];
      const fourMonthsAgo = new Date();
      fourMonthsAgo.setMonth(fourMonthsAgo.getMonth() - 4);
      const cutoff = fourMonthsAgo.toISOString().slice(0, 10);
      dupSnap.forEach(doc => {
        const d = doc.data();
        if ((d.date || '9999') >= cutoff) {
          (d.packs || []).forEach(p => registeredPacks.push(p.pack_no));
        }
      });"""

new_reg = """      const registeredPacks = [];
      const dupRecordMap = {};
      const fourMonthsAgo = new Date();
      fourMonthsAgo.setMonth(fourMonthsAgo.getMonth() - 4);
      const cutoff = fourMonthsAgo.toISOString().slice(0, 10);
      dupSnap.forEach(doc => {
        const d = doc.data();
        if ((d.date || '9999') >= cutoff) {
          (d.packs || []).forEach(p => {
            registeredPacks.push(p.pack_no);
            if (!dupRecordMap[p.pack_no]) {
              dupRecordMap[p.pack_no] = {
                docId: doc.id, date: d.date||'', shift: d.shift||'', machine: d.machine||''
              };
            }
          });
        }
      });"""

cnt2 = html.count(old_reg)
print(f'registeredPacks: {cnt2}')
html = html.replace(old_reg, new_reg)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('showDupWarning calls:', html.count('showDupWarning(dupPacks'))
print('dupRecordMap defined:', html.count('const dupRecordMap'))
