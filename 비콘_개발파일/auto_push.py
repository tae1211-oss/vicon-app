"""
index.html 수정 시 자동으로 git commit & push
Claude Code PostToolUse 훅에서 호출됨 (stdin으로 JSON 입력)
"""
import sys, json, subprocess, os

def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8')

try:
    data = json.load(sys.stdin)
except:
    sys.exit(0)

file_path = data.get('tool_input', {}).get('file_path', '')

# index.html 수정 시에만 동작
if 'index.html' not in file_path:
    sys.exit(0)

repo = r'C:\Users\user\Desktop\클로드'

# git add
r = run(['git', 'add', 'index.html'], repo)
if r.returncode != 0:
    sys.exit(0)

# git commit (변경 없으면 종료)
r = run(['git', 'commit', '-m', 'auto: index.html 업데이트'], repo)
if r.returncode != 0:
    sys.exit(0)  # 변경 없음 또는 오류

# git push
r = run(['git', 'push', 'origin', 'master'], repo)
run(['git', 'push', 'origin', 'master:main', '--force'], repo)  # Vercel 배포용 main 동기화
if r.returncode == 0:
    print(json.dumps({"systemMessage": "GitHub 업로드 완료"}))
else:
    print(json.dumps({"systemMessage": f"GitHub push 실패: {r.stderr[:100]}"}))
