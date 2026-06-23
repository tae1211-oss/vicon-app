# -*- coding: utf-8 -*-
"""
production_deck 컬렉션에서 total_sheets=0 (또는 None) 인 탈형 레코드를
job_orders 데이터 기준으로 장수를 재계산해 업데이트합니다.

실행:
  py _fix_prod_sheets.py --dry-run   # 변경 내용만 출력 (실제 수정 안 함)
  py _fix_prod_sheets.py             # 실제 Firestore 업데이트
"""
import sys, os
import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_KEY = r"C:\Users\user\Desktop\클로드\vicon-service-account.json"

def init_db():
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(SERVICE_ACCOUNT_KEY))
    return firestore.client()

def main():
    dry = "--dry-run" in sys.argv
    db = init_db()

    # 1) job_orders 전부 로드 → (company, site, req_code) → {pack_no: sheets}
    print("[1/3] job_orders 로드 중...")
    jo_map = {}  # (company, site) -> {pack_no: sheets}  (req_code 도 같이)
    jo_req_map = {}  # req_code -> {pack_no: sheets}
    for doc in db.collection("job_orders").stream():
        d = doc.to_dict()
        pf = d.get("pack_from", 1)
        packs_data = d.get("d") or []
        pack_sheets = {}
        for i, item in enumerate(packs_data):
            pno = pf + i
            if isinstance(item, dict):
                pack_sheets[pno] = int(item.get("s", 0) or 0)
            elif isinstance(item, list) and len(item) >= 1:
                pack_sheets[pno] = int(item[0] or 0)
        key = (d.get("company",""), d.get("site",""))
        jo_map[key] = pack_sheets
        rc = d.get("req_code","")
        if rc:
            jo_req_map[rc] = pack_sheets
    print(f"   -> {len(jo_map)}건 로드")

    # 2) production_deck 에서 total_sheets=0 또는 None 인 레코드 조회
    print("[2/3] production_deck 스캔 중...")
    to_fix = []
    for doc in db.collection("production_deck").stream():
        d = doc.to_dict()
        ts = d.get("total_sheets")
        if ts is not None and ts != 0:
            continue  # 이미 정상
        # 장수 정보가 없는 레코드만 처리
        packs = d.get("packs") or []
        if not packs:
            continue
        # job_orders 에서 장수 찾기
        key = (d.get("company",""), d.get("site",""))
        rc  = d.get("req_code","")
        pack_sheets = jo_map.get(key) or jo_req_map.get(rc) or {}
        if not pack_sheets:
            continue

        new_packs = []
        changed = False
        for p in packs:
            pno = p.get("pack_no")
            old_s = p.get("sheets") or 0
            new_s = pack_sheets.get(pno, old_s)
            old_a = p.get("area") or 0
            new_packs.append({**p, "sheets": new_s})
            if new_s != old_s:
                changed = True

        if not changed:
            continue

        new_total = sum(p.get("sheets",0) or 0 for p in new_packs)
        to_fix.append({
            "doc_id": doc.id,
            "ref": doc.reference,
            "old_total": ts,
            "new_total": new_total,
            "new_packs": new_packs,
            "site": d.get("site",""),
            "date": d.get("date",""),
            "machine": d.get("machine",""),
        })

    print(f"   -> 수정 대상: {len(to_fix)}건")

    if not to_fix:
        print("수정할 레코드 없음.")
        return

    for r in to_fix:
        print(f"   [{r['date']}] {r['site']} / {r['machine']}  "
              f"total_sheets: {r['old_total']} -> {r['new_total']}")

    if dry:
        print("\n(--dry-run: 실제 수정 안 함)")
        return

    # 3) 업데이트
    print(f"\n[3/3] {len(to_fix)}건 업데이트 중...")
    batch = db.batch()
    for i, r in enumerate(to_fix):
        batch.update(r["ref"], {
            "packs": r["new_packs"],
            "total_sheets": r["new_total"],
        })
        if (i+1) % 400 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f"완료: {len(to_fix)}건 업데이트")

if __name__ == "__main__":
    main()
