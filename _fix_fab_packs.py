# -*- coding: utf-8 -*-
import firebase_admin
from firebase_admin import credentials, firestore

firebase_admin.initialize_app(credentials.Certificate(
    r"C:\Users\user\Desktop\클로드\vicon-service-account.json"))
db = firestore.client()

def get_job_packs(req_code):
    docs = list(db.collection("job_orders").where("req_code", "==", req_code).stream())
    if not docs:
        return None
    d = docs[0].to_dict()
    pf = d.get("pack_from", 1)
    result = {}
    for i, item in enumerate(d.get("d") or []):
        pno = pf + i
        if isinstance(item, dict):
            result[pno] = {"sheets": int(item.get("s", 0) or 0),
                           "area":   round(float(item.get("a", 0) or 0), 2)}
    return result

targets = {
    "eaABtJLfLsCLfszFnQsI": "0611-31-SMS",
    "6VWKdAfK3fZLQVtFCFKd": "0612-32-SMS",
}

for doc_id, req_code in targets.items():
    pack_map = get_job_packs(req_code)
    if not pack_map:
        print("job_order not found:", req_code)
        continue
    ref = db.collection("production_deck").document(doc_id)
    old = ref.get().to_dict()
    new_packs = []
    for p in (old.get("packs") or []):
        pno = p.get("pack_no")
        correct = pack_map.get(pno, {})
        new_packs.append({
            "pack_no": pno,
            "sheets":  correct.get("sheets", 0),
            "area":    correct.get("area", 0),
        })
    new_total_sheets = sum(p["sheets"] for p in new_packs)
    new_total_area   = round(sum(p["area"] for p in new_packs), 2)
    ref.update({
        "packs":        new_packs,
        "total_sheets": new_total_sheets,
        "total_area":   new_total_area,
    })
    print(req_code, "-> sheets:", new_total_sheets, "area:", new_total_area)
    for p in new_packs:
        print(" ", p)
