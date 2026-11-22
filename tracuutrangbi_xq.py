# -*- coding: utf-8 -*-
"""Tra cứu chỉ số trang bị và trần tái tạo (chạy tay, không cần game).

Dữ liệu tải 2026-11-20 từ tool chienquoc2d.com/tinh-chi-so.php (cần đăng nhập):
- _internal/chisotrangbi/itemdb.json : ITEM_DB của trang (chỉ số gốc từng món, đồ chế "crafted" / đồ phái "default").
- _internal/chisotrangbi/taitao.json  : bảng kết quả máy chủ tính cho từng (phái, ô, loại vũ khí, cấp, phẩm chất) với
  chỉ số gốc = 0, dạng {"phái|ô|loại|cấp|màu": [[tên dòng, hệ số, tái tạo max], ...]}.
Đã kiểm: số tái tạo KHÔNG phụ thuộc chỉ số gốc (Đào Hoa vũ khí gốc NgK 80 hay 0 đều +316), nên
Tổng max = gốc + tái tạo, Khuyên dùng = gốc + floor(0.85 × tái tạo) (khớp mọi mẫu đã xem).
Mỗi số là mức tối đa TỪNG DÒNG, không lên hết cùng lúc.

Cách dùng:
  python -X utf8 tracuutrangbi_xq.py --phai 1 --o vukhi --cap 100
  python -X utf8 tracuutrangbi_xq.py --phai thucson --o all --cap 100 --mau lamkim
  python -X utf8 tracuutrangbi_xq.py --ten "Long Lân"        (tìm theo tên, mọi phái)
"""
import argparse
import json
import math
import os
import sys

THUMUC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_internal", "chisotrangbi")

PHAI = {0: "Vô Môn Phái", 1: "Đào Hoa Nguyên", 2: "Thục Sơn", 3: "Cấm Vệ Quân", 4: "Đường Môn",
        5: "Mao Sơn", 6: "Côn Luân", 7: "Vân Mộng Cốc"}
PHAI_TAT = {"vomon": 0, "daohoa": 1, "thucson": 2, "camve": 3, "camvequan": 3, "duongmon": 4,
            "maoson": 5, "conluan": 6, "vanmong": 7}
# Ô trang bị: tên khoá trong ITEM_DB và mã equip_type của form trên trang.
O = {"vukhi": ("weapon", 4), "ao": ("armor", 3), "non": ("head", 1), "hanglien": ("neck", 2),
     "yeudoi": ("waist", 5), "giay": ("boots", 6)}
TEN_O = {"weapon": "Vũ Khí", "armor": "Áo", "head": "Nón", "neck": "Hạng Liên", "waist": "Yêu Đới", "boots": "Giày"}
TEN_LOAIVK = {"sword": "Kiếm", "blade": "Đao", "spear": "Thương", "stick": "Côn", "unarmed": "Quyền", "throwing": "Ám Khí"}
# Loại vũ khí mỗi phái dùng được (giống getWeaponSubKey của trang).
LOAIVK_PHAI = {0: ["sword", "blade"], 1: ["unarmed"], 2: ["sword", "blade"], 3: ["spear", "stick"], 4: ["throwing"],
               5: ["sword"], 6: ["sword"], 7: ["sword"]}
DONG = [("hp", "Khí Huyết"), ("mp", "Pháp Lực"), ("ap", "Ngoại Công"), ("cp", "Nội Công"),
        ("dp", "Ngoại Kháng"), ("pp", "Nội Kháng"), ("sp", "Thân Thủ")]
TEN_DONG = dict(DONG)
MAU = {"hoangkim": 2, "hk": 2, "2": 2, "lamkim": 1, "lk": 1, "1": 1}
TEN_MAU = {2: "Hoàng Kim", 1: "Lam Kim"}


def docdulieu():
    with open(os.path.join(THUMUC, "itemdb.json"), encoding="utf-8") as f:
        itemdb = json.load(f)
    with open(os.path.join(THUMUC, "taitao.json"), encoding="utf-8") as f:
        taitao = json.load(f)
    return itemdb, taitao


def _nhom(db, khoa):
    # Nhóm theo phái: PHP json_encode ra mảng khi khoá là 0..n liền nhau, ra object khi không liền
    if isinstance(db, list):
        k = int(khoa)
        return db[k] if 0 <= k < len(db) else None
    return db.get(khoa)


def danhsachmon(itemdb, nguon, khoa_o, phai, loaivk=None):
    """Danh sách món giống trang: lấy theo phái, không có thì lấy nhóm 0; kiếm chế nằm ở nhóm 9 (mọi phái kiếm)."""
    db = itemdb.get(nguon, {}).get(khoa_o)
    if not db:
        return []
    if khoa_o == "weapon":
        db = db.get(loaivk) or {}
        for k in (str(phai), "9", "0"):
            if _nhom(db, k):
                return _nhom(db, k)
        return []
    return _nhom(db, str(phai)) or _nhom(db, "0") or []


def bangtaitao(taitao, phai, ma_o, loaivk, cap, mau):
    return taitao.get("|".join([str(phai), str(ma_o), loaivk or "", str(cap), str(mau)]))


def inmon(mon, bang, mau):
    gt = {1: " [Nam]", 2: " [Nữ]"}.get(mon.get("gender", 0), "")
    print("  Lv%d %s%s  (%s)" % (mon["level"], mon["name"], gt, TEN_MAU[mau]))
    if bang is None:
        print("    (không có dữ liệu tái tạo cho tổ hợp này)")
        return
    goc = mon["stats"]
    dongtaitao = {ten: (heso, tt) for ten, heso, tt in bang}
    for khoa, ten in DONG:
        g = int(goc.get(khoa) or 0)
        heso, tt = dongtaitao.get(ten, ("-", 0))
        if not g and not tt:
            continue
        print("    %-12s gốc %5d  hệ số %5s  tái tạo +%-5d tổng max %5d  khuyên dùng %5d"
              % (ten, g, heso, tt, g + tt, g + int(math.floor(0.85 * tt))))


def main():
    ap = argparse.ArgumentParser(description="Tra chỉ số trang bị + trần tái tạo (dữ liệu chienquoc2d)")
    ap.add_argument("--phai", help="số 0-7 hoặc tên không dấu: daohoa thucson camve duongmon maoson conluan vanmong vomon")
    ap.add_argument("--o", default="all", help="vukhi ao non hanglien yeudoi giay | all")
    ap.add_argument("--cap", type=int, help="cấp món (mặc định: mọi cấp)")
    ap.add_argument("--mau", default="hoangkim", help="hoangkim | lamkim")
    ap.add_argument("--nguon", default="all", help="che | phai | all")
    ap.add_argument("--ten", help="tìm món theo tên (chứa chuỗi), mọi phái")
    a = ap.parse_args()

    itemdb, taitao = docdulieu()
    mau = MAU.get(str(a.mau).lower().replace(" ", ""), 2)
    nguons = {"che": ["crafted"], "phai": ["default"]}.get(a.nguon, ["crafted", "default"])
    ten_nguon = {"crafted": "Đồ Chế", "default": "Đồ Phái"}

    if a.ten:
        tim = a.ten.lower()
        for phai in PHAI:
            for nguon in nguons:
                for ten_o, (khoa_o, ma_o) in O.items():
                    for loaivk in (LOAIVK_PHAI[phai] if khoa_o == "weapon" else [None]):
                        for mon in danhsachmon(itemdb, nguon, khoa_o, phai, loaivk):
                            if tim in mon["name"].lower() and (a.cap is None or mon["level"] == a.cap):
                                print("%s · %s · %s%s" % (PHAI[phai], ten_nguon[nguon], TEN_O[khoa_o],
                                                         " " + TEN_LOAIVK[loaivk] if loaivk else ""))
                                inmon(mon, bangtaitao(taitao, phai, ma_o, loaivk, mon["level"], mau), mau)
        return

    if a.phai is None:
        ap.error("cần --phai hoặc --ten")
    phai = int(a.phai) if str(a.phai).isdigit() else PHAI_TAT.get(str(a.phai).lower())
    if phai not in PHAI:
        ap.error("phái không hợp lệ: %s" % a.phai)
    cac_o = list(O.items()) if a.o == "all" else [(a.o, O[a.o])]
    for ten_o, (khoa_o, ma_o) in cac_o:
        for loaivk in (LOAIVK_PHAI[phai] if khoa_o == "weapon" else [None]):
            for nguon in nguons:
                mons = [m for m in danhsachmon(itemdb, nguon, khoa_o, phai, loaivk)
                        if a.cap is None or m["level"] == a.cap]
                if not mons:
                    continue
                print("== %s · %s%s · %s ==" % (PHAI[phai], TEN_O[khoa_o],
                                               " " + TEN_LOAIVK[loaivk] if loaivk else "", ten_nguon[nguon]))
                for mon in mons:
                    inmon(mon, bangtaitao(taitao, phai, ma_o, loaivk, mon["level"], mau), mau)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
