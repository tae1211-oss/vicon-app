"""
Playwright로 비콘㈜ 관리시스템 각 화면 자동 캡처
"""
import asyncio
from playwright.async_api import async_playwright
import os

HTML_PATH = r'C:\Users\user\Desktop\클로드\index.html'
OUT_DIR   = r'C:\Users\user\Desktop\클로드\screenshots'
os.makedirs(OUT_DIR, exist_ok=True)

FILE_URL = 'file:///' + HTML_PATH.replace('\\', '/')

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={'width': 390, 'height': 844},   # iPhone 14 크기
            device_scale_factor=2,
        )
        page = await ctx.new_page()

        print('앱 로드 중...')
        await page.goto(FILE_URL)
        await page.wait_for_timeout(1500)

        # ── 1. 로그인 화면 ──────────────────────────────────
        print('1. 로그인 화면 캡처')
        await page.screenshot(path=f'{OUT_DIR}/01_login.png', full_page=False)

        # ── 로그인 (Firebase 없이 테스트용 — 화면만 캡처) ──
        # 로그인 버튼 클릭 없이 홈 화면으로 JS로 직접 이동
        await page.evaluate("""
            // 로그인 화면 숨기고 홈 화면 표시
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            const home = document.getElementById('screen-home');
            if (home) home.classList.add('active');
            // 사용자 이름 설정
            const nameEl = document.getElementById('home-user-name');
            if (nameEl) nameEl.textContent = '홍길동';
        """)
        await page.wait_for_timeout(800)

        # ── 2. 홈 화면 ───────────────────────────────────────
        print('2. 홈 화면 캡처')
        await page.screenshot(path=f'{OUT_DIR}/02_home.png', full_page=False)

        # ── 재고수불 화면으로 이동 ────────────────────────────
        await page.evaluate("""
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            const inv = document.getElementById('screen-inventory');
            if (inv) inv.classList.add('active');
            // 지도 탭 활성화
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            const mapPage = document.getElementById('page-map');
            if (mapPage) mapPage.classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            const mapTab = document.getElementById('tab-map');
            if (mapTab) mapTab.classList.add('active');
        """)
        await page.wait_for_timeout(1200)

        # ── 3. 지도 탭 ──────────────────────────────────────
        print('3. 지도 탭 캡처')
        await page.screenshot(path=f'{OUT_DIR}/03_map.png', full_page=False)

        # ── 4. 입고 탭 ──────────────────────────────────────
        await page.evaluate("""
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-inbound').classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('tab-inbound').classList.add('active');
        """)
        await page.wait_for_timeout(500)
        print('4. 입고 탭 캡처')
        await page.screenshot(path=f'{OUT_DIR}/04_inbound.png', full_page=False)

        # ── 5. 출고 탭 ──────────────────────────────────────
        await page.evaluate("""
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-outbound').classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('tab-outbound').classList.add('active');
        """)
        await page.wait_for_timeout(500)
        print('5. 출고 탭 캡처')
        await page.screenshot(path=f'{OUT_DIR}/05_outbound.png', full_page=False)

        # ── 6. 재고 탭 ──────────────────────────────────────
        await page.evaluate("""
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-inventory').classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('tab-inventory').classList.add('active');
            // 로딩 메시지 대신 샘플 텍스트
            const invList = document.getElementById('inv-list');
            if (invList) invList.innerHTML = '<div style="text-align:center;padding:20px;color:#90a4ae;font-size:.85rem">재고 데이터를 불러오려면 Firebase 연결이 필요합니다.</div>';
        """)
        await page.wait_for_timeout(500)
        print('6. 재고 탭 캡처')
        await page.screenshot(path=f'{OUT_DIR}/06_inventory.png', full_page=False)

        # ── 7. 설정 탭 ──────────────────────────────────────
        await page.evaluate("""
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-settings').classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('tab-settings').classList.add('active');
        """)
        await page.wait_for_timeout(500)
        print('7. 설정 탭 캡처')
        await page.screenshot(path=f'{OUT_DIR}/07_settings.png', full_page=True)

        # ── 8. 생산수불 화면 ─────────────────────────────────
        await page.evaluate("""
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            const prod = document.getElementById('screen-production');
            if (prod) prod.classList.add('active');
        """)
        await page.wait_for_timeout(800)
        print('8. 생산수불 화면 캡처')
        await page.screenshot(path=f'{OUT_DIR}/08_production.png', full_page=False)

        # ── 9. 관리자 모드 (설정 탭에서 admin-only 표시) ─────
        await page.evaluate("""
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            const inv = document.getElementById('screen-inventory');
            if (inv) inv.classList.add('active');
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-settings').classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('tab-settings').classList.add('active');
            // 관리자 영역 표시
            const adminOnly = document.getElementById('admin-only');
            if (adminOnly) adminOnly.style.display = 'block';
            const cardLogin = document.getElementById('card-admin-login');
            if (cardLogin) cardLogin.style.display = 'none';
        """)
        await page.wait_for_timeout(500)
        print('9. 관리자 설정 캡처')
        await page.screenshot(path=f'{OUT_DIR}/09_admin.png', full_page=True)

        await browser.close()
        print(f'\n✅ 캡처 완료! 저장 위치: {OUT_DIR}')
        files = os.listdir(OUT_DIR)
        for f in sorted(files):
            size = os.path.getsize(f'{OUT_DIR}/{f}')
            print(f'  {f}: {size//1024}KB')

asyncio.run(capture())
