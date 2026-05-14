with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_dup = """      const registeredPacks = [];
      const fourMonthsAgo = new Date();
      fourMonthsAgo.setMonth(fourMonthsAgo.getMonth() - 4);
      const cutoff = fourMonthsAgo.toISOString().slice(0, 10);
      dupSnap.forEach(doc => {
        const d = doc.data();
        if ((d.date || '9999') >= cutoff) {
          (d.packs || []).forEach(p => registeredPacks.push(p.pack_no));
        }
      });
      const dupPacks = sel.filter(n => registeredPacks.includes(n));
      if (dupPacks.length > 0) {
        alert('⚠️ 중복 등록 차단\n\n이미 등록된 패킹번호가 있습니다:\n' +
              dupPacks.join(', ') + '번\n\n' +
              '(주간/야간 구분 없이 4개월 내 동일 패킹 재등록 불가)\n\n' +
              '업체: ' + (pendingProd.company || '') + '\n' +
              '현장: ' + (pendingProd.site    || '') + '\n' +
              '의뢰번호: ' + (pendingProd.req_code || ''));
        return;
      }"""

new_dup = """      const registeredPacks = [];
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
      });
      const dupPacks = sel.filter(n => registeredPacks.includes(n));
      if (dupPacks.length > 0) {
        showDupWarning(dupPacks, dupRecordMap);
        return;
      }"""

cnt = html.count(old_dup)
print(f'dup_check occurrences: {cnt}')
html = html.replace(old_dup, new_dup)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('showDupWarning calls:', html.count('showDupWarning(dupPacks'))
print('dupRecordMap:', 'dupRecordMap' in html)
