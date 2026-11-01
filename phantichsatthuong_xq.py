"""Phân tích log của dosatthuong_xq.py ra công thức sát thương, theo từng chiêu (cột nhan).

    python phantichsatthuong_xq.py [file.csv ...]      (bỏ trống: mọi file trong _internal/dosatthuong)

Mỗi chiêu:
1. Tách đòn Bạo Kích: lặp khớp sát thương thường ~ chỉ số, đòn cao hơn dự đoán quá NGUONGBAOKICH lần là bạo; báo hệ số bạo
   (sát thương bạo / dự đoán thường) và tỉ lệ ra bạo so với Bạo Kích trên bảng.
2. Khớp tuyến tính sát thương thường = a*Công + b*Kháng + c trên các chỉ số có thay đổi trong log. b ~ -a là kiểu trừ thẳng
   (Công - Kháng); kiểu chia tỉ lệ thì khớp tỉ lệ (sát thương / Công theo Kháng) tốt hơn.
3. Bảng theo mức Công: sát thương thường thấp nhất / cao nhất so với cặp Công 1 / 2 (cặp này có phải khoảng random không).
"""
import csv
import glob
import os
import sys
from collections import defaultdict

import numpy as np

from dosatthuong_xq import THUMUCDOSATTHUONG

NGUONGBAOKICH = 1.3
# Chỉ số dùng khớp: Công người đánh lấy trung bình cặp thấp / cao
BIENs = {
    "Ngoại Công": lambda d: (d["danh_ngoaicong1"] + d["danh_ngoaicong2"]) / 2,
    "Nội Công": lambda d: (d["danh_noicong1"] + d["danh_noicong2"]) / 2,
    "Ngoại Kháng (bị đánh)": lambda d: (d["bi_ngoaikhang1"] + d["bi_ngoaikhang2"]) / 2,
    "Nội Kháng (bị đánh)": lambda d: (d["bi_noikhang1"] + d["bi_noikhang2"]) / 2,
    "Thân Thủ (đánh)": lambda d: d["danh_thanthu"],
    "Thân Thủ (bị đánh)": lambda d: d["bi_thanthu"],
}


def docdons(duongdans):
    dons = []
    for duongdan in duongdans:
        with open(duongdan, encoding = "utf-8-sig") as f:
            for dong in csv.DictReader(f):
                # Đòn không biết người đánh (quái đánh) vẫn giữ: chỉ dùng được biến của người bị đánh
                don = {k: (float(v) if v not in ("", None) and k not in ("nhan", "nguoibidanh", "nguoidanh") else v)
                       for k, v in dong.items()}
                dons.append(don)
    return dons


def khop(dons, tenbiens):
    # Bình phương tối thiểu sát thương ~ biến (chỉ biến có thay đổi) + hằng số -> ({tên: hệ số}, hằng số, R², dự đoán)
    y = np.array([d["satthuong"] for d in dons])
    cots, tens = [], []
    for ten in tenbiens:
        cot = np.array([BIENs[ten](d) for d in dons])
        if np.ptp(cot) > 0:
            cots.append(cot)
            tens.append(ten)
    X = np.column_stack(cots + [np.ones(len(y))])
    heso = np.linalg.lstsq(X, y, rcond = None)[0]
    dudoan = X @ heso
    r2 = 1 - ((y - dudoan) ** 2).sum() / max(((y - y.mean()) ** 2).sum(), 1e-9)
    return dict(zip(tens, heso[:-1])), heso[-1], r2, dudoan


def phantichchieu(nhan, dons):
    print(f"\n=== {nhan}: {len(dons)} đòn ===")
    if len(dons) < 3:
        print("Quá ít đòn để phân tích")
        return
    codanh = all(d.get("nguoidanh") for d in dons)
    tenbiens = [t for t in BIENs if codanh or "(bị đánh)" in t]

    # Lặp: khớp trên đòn thường, đòn vượt dự đoán quá NGUONGBAOKICH lần coi là bạo, khớp lại tới khi tập đòn bạo không đổi
    baokich = np.zeros(len(dons), bool)
    for _ in range(10):
        thuong = [d for d, b in zip(dons, baokich) if not b]
        if len(thuong) < 3:
            break
        heso, hang, r2, _ = khop(thuong, tenbiens)
        dudoan = np.array([hang + sum(h * BIENs[t](d) for t, h in heso.items()) for d in dons])
        moi = np.array([d["satthuong"] for d in dons]) > NGUONGBAOKICH * np.maximum(dudoan, 1)
        if (moi == baokich).all():
            break
        baokich = moi

    thuong = [d for d, b in zip(dons, baokich) if not b]
    bao = [(d, p) for d, p, b in zip(dons, dudoan, baokich) if b]
    print(f"Đòn thường {len(thuong)}, đòn bạo {len(bao)} ({len(bao) / len(dons) * 100:.1f}%)")
    if codanh:
        print(f"  Bạo Kích trên bảng (trung bình): {np.mean([d['danh_baokich'] for d in dons]) / 100:.2f}%")
    if bao:
        tile = [d["satthuong"] / max(p, 1) for d, p in bao]
        print(f"  Hệ số bạo ~ x{np.mean(tile):.2f} (từ x{min(tile):.2f} tới x{max(tile):.2f})")

    print(f"Khớp tuyến tính (R² = {r2:.3f}): sát thương thường = " + " ".join(f"{h:+.3f}*{t}" for t, h in heso.items())
          + f" {hang:+.1f}")
    if not heso:
        print("  Không chỉ số nào thay đổi trong log: đổi 1 chỉ số (bật / tắt bảo thú, tháo đồ) rồi đo thêm để tách hệ số")

    # Kiểu chia tỉ lệ: sát thương / Công theo Kháng tương ứng (cùng hệ Ngoại hoặc Nội, chọn hệ có Công lớn hơn)
    if codanh and thuong:
        he = "Ngoại" if np.mean([BIENs["Ngoại Công"](d) for d in thuong]) >= np.mean([BIENs["Nội Công"](d) for d in thuong]) else "Nội"
        cong = np.array([BIENs[f"{he} Công"](d) for d in thuong])
        khang = np.array([BIENs[f"{he} Kháng (bị đánh)"](d) for d in thuong])
        y = np.array([d["satthuong"] for d in thuong])
        if np.ptp(khang) > 0 and cong.min() > 0:
            tl = y / cong
            a, b = np.polyfit(khang, tl, 1)
            dudoantl = cong * (a * khang + b)
            r2tl = 1 - ((y - dudoantl) ** 2).sum() / max(((y - y.mean()) ** 2).sum(), 1e-9)
            print(f"  Kiểu tỉ lệ ({he}, R² = {r2tl:.3f}): sát thương = Công * ({a:.6f}*Kháng {b:+.4f})"
                  f"  -> R² cao hơn kiểu trừ thẳng ở trên thì Kháng giảm theo tỉ lệ")

        # Bảng theo mức Công (làm tròn 10): khoảng sát thương thường so với cặp Công thấp / cao
        print(f"  Theo {he} Công (cặp thấp-cao) | Kháng | số đòn | sát thương thường thấp nhất - cao nhất (trung bình)")
        nhom = defaultdict(list)
        for d in thuong:
            nhom[(d[f"danh_{'ngoai' if he == 'Ngoại' else 'noi'}cong1"] // 10 * 10,
                  d[f"danh_{'ngoai' if he == 'Ngoại' else 'noi'}cong2"] // 10 * 10,
                  round(BIENs[f"{he} Kháng (bị đánh)"](d), -1))].append(d["satthuong"])
        for (c1, c2, k), ys in sorted(nhom.items()):
            print(f"    {c1:.0f}-{c2:.0f} | {k:.0f} | {len(ys)} | {min(ys):.0f} - {max(ys):.0f} ({np.mean(ys):.0f})")


def main():
    sys.stdout.reconfigure(encoding = "utf-8")
    duongdans = sys.argv[1:] or sorted(glob.glob(os.path.join(THUMUCDOSATTHUONG, "*.csv")))
    dons = docdons(duongdans)
    if not dons:
        print("Chưa có đòn nào (chạy dosatthuong_xq.py để ghi)")
        return
    theochieu = defaultdict(list)
    for d in dons:
        theochieu[d["nhan"]].append(d)
    for nhan, ds in theochieu.items():
        phantichchieu(nhan, ds)


if __name__ == "__main__":
    main()
