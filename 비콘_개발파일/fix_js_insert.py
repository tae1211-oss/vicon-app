with open('index.html.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 이미 삽입됐는지 확인
if 'function openDailyReport' in html:
    print('openDailyReport already exists')
else:
    print('Need to insert openDailyReport')

if 'function openEditProd' in html:
    print('openEditProd already exists')
else:
    print('Need to insert openEditProd')

if 'function executeBatchDelete' in html:
    print('executeBatchDelete already exists')
else:
    print('Need to insert executeBatchDelete')

# </script> 바로 앞에 넣을 앵커 찾기 (doLogout 함수 끝 부분)
anchor = """function doLogout() {
  if (!confirm('로그아웃 하시겠습니까?')) return;
  firebase.auth().signOut();
}

</script>"""

print('anchor found:', anchor in html)
