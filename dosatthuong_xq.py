"""Đo sát thương: ghi từng đòn trúng nhân vật đang mở trên máy này để tìm công thức (phân tích bằng phantichsatthuong_xq.py).

Máy chủ tính sát thương, client chỉ có kết quả: máu quái chỉ đọc được theo % (0.5%) nên đo trên NHÂN VẬT (máu chính xác ở KDK). Cách đo:
mở 2 nhân vật trên máy này (người đánh, người bị đánh) ở lôi đài, người đánh dùng 1 chiêu, công cụ đọc máu người bị đánh mỗi 10ms,
máu tụt là 1 đòn: ghi lượng tụt + chỉ số cả 2 bên (đọc ở lượt trước đòn). Đổi 1 chỉ số mỗi đợt (bật / tắt bảo thú Thìn ±180 Ngoại Công,
Dần ±7% Bạo Kích, tháo / mặc 1 món) để biết chỉ số đó ảnh hưởng thế nào. Đứng cho quái đánh thì chỉ có chỉ số người bị đánh (đo Kháng).

    python dosatthuong_xq.py --nhan "Nhất Quyền" [--danh <tên người đánh>] [--bi <tên người bị đánh>]

--nhan: tên chiêu đang đo (mỗi chiêu hệ số riêng); đổi chiêu thì chạy lại với nhãn khác. Không có --danh mà mở đúng 2 nhân vật thì người
kia là người đánh. Ghi vào _internal/dosatthuong/<lúc chạy>.csv, Ctrl+C để dừng.
Chỉ đọc bộ nhớ, không gắn hook (chạy được cùng lúc với bot).
"""
import argparse
import csv
import os
import sys
import time

import win32gui

from dangnhap_xq import GAME_TITLE_PREFIX, chuanhoatennhanvat
from hangso_xq import CHISONHANVAT_MAP
from moitruong_xq import MoiTruong

THUMUCDOSATTHUONG = os.path.join("_internal", "dosatthuong")
CHUKYDOC = 0.01

# Tên cột ngắn cho từng ô chỉ số (cặp thấp / cao đánh số 1, 2), cùng thứ tự với DICHCHISOs
TENCOTCHISO_MAP = {
    "Khí Huyết": "khihuyet", "Ngoại Công": "ngoaicong", "Ngoại Kháng": "ngoaikhang", "Thân Thủ": "thanthu",
    "Nội Công": "noicong", "Nội Kháng": "noikhang", "Bạo Kích": "baokich",
}
COTCHISOs, DICHCHISOs = [], []
for _ten, _dichs in CHISONHANVAT_MAP.items():
    for _i, _dich in enumerate(_dichs):
        COTCHISOs.append(TENCOTCHISO_MAP[_ten] + (str(_i + 1) if len(_dichs) > 1 else ""))
        DICHCHISOs.append(_dich)


def timnhanvats():
    # {tên đã chuẩn hoá: MoiTruong} của các cửa sổ game đang có nhân vật
    nhanvats = {}

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd) or GAME_TITLE_PREFIX not in win32gui.GetWindowText(hwnd):
            return
        try:
            mt = MoiTruong(hwnd)
            if mt.get_is_nhanvattontai():
                nhanvats[chuanhoatennhanvat(mt.get_tendoituong())] = mt
        except Exception:
            pass

    win32gui.EnumWindows(callback, None)
    return nhanvats


def docnhanvat(mt):
    # (máu, máu tối đa, {cột chỉ số: giá trị}) hoặc None khi đang dis / chưa đọc được
    try:
        if not mt.get_is_nhanvattontai():
            return None
        chisos = mt.get_chisonhanvats(DICHCHISOs)
        mau, mautoida = mt.get_sinhlucconlai(), mt.get_sinhluctoida()
    except Exception:
        return None
    if not chisos or mau is False or not mautoida:
        return None
    return mau, mautoida, dict(zip(COTCHISOs, chisos))


def main():
    sys.stdout.reconfigure(encoding = "utf-8")
    thamso = argparse.ArgumentParser(description = "Ghi sát thương từng đòn để tìm công thức")
    thamso.add_argument("--nhan", required = True, help = "tên chiêu đang đo")
    thamso.add_argument("--danh", help = "tên người đánh (bỏ trống: người còn lại khi mở đúng 2 nhân vật)")
    thamso.add_argument("--bi", help = "chỉ ghi đòn trúng nhân vật này")
    thamso = thamso.parse_args()

    nhanvats = timnhanvats()
    if not nhanvats:
        print("Không thấy cửa sổ game nào có nhân vật")
        return
    print("Nhân vật:", ", ".join(nhanvats))
    tendanh = chuanhoatennhanvat(thamso.danh) if thamso.danh else None
    tenbi = chuanhoatennhanvat(thamso.bi) if thamso.bi else None
    for ten in (tendanh, tenbi):
        if ten and ten not in nhanvats:
            print(f"Không thấy nhân vật '{ten}'")
            return

    os.makedirs(THUMUCDOSATTHUONG, exist_ok = True)
    duongdan = os.path.join(THUMUCDOSATTHUONG, time.strftime("%Y%m%d-%H%M%S") + ".csv")
    cots = (["thoidiem", "nhan", "nguoibidanh", "satthuong", "mautruoc", "mautoida"] + ["bi_" + c for c in COTCHISOs]
            + ["nguoidanh"] + ["danh_" + c for c in COTCHISOs])
    print(f"Ghi vào {duongdan}, Ctrl+C để dừng")

    truoc = {ten: docnhanvat(mt) for ten, mt in nhanvats.items()}
    sodon = 0
    with open(duongdan, "w", newline = "", encoding = "utf-8-sig") as f:
        ghi = csv.writer(f)
        ghi.writerow(cots)
        try:
            while True:
                time.sleep(CHUKYDOC)
                hientai = {ten: docnhanvat(mt) for ten, mt in nhanvats.items()}
                for ten, sau in hientai.items():
                    dau = truoc.get(ten)
                    if not sau or not dau or (tenbi and ten != tenbi):
                        continue
                    # Đổi máu tối đa (mặc / tháo đồ, lên cấp) thì máu đổi theo, không phải đòn đánh
                    satthuong = dau[0] - sau[0]
                    if satthuong <= 0 or dau[1] != sau[1]:
                        continue
                    nguoidanh = tendanh
                    if not nguoidanh:
                        cons = [t for t in nhanvats if t != ten]
                        nguoidanh = cons[0] if len(cons) == 1 else None
                    # Chỉ số người đánh lấy ở lượt trước đòn (Ngoại Công Đào Hoa đổi theo nguyên khí ngay khi trúng)
                    chisodanh = truoc.get(nguoidanh) if nguoidanh and nguoidanh != ten else None
                    ghi.writerow([round(time.time(), 3), thamso.nhan, ten, satthuong, dau[0], dau[1]]
                                 + [dau[2][c] for c in COTCHISOs]
                                 + [nguoidanh if chisodanh else ""] + [chisodanh[2][c] if chisodanh else "" for c in COTCHISOs])
                    f.flush()
                    sodon += 1
                    print(f"#{sodon} {ten} -{satthuong} ({dau[0]} -> {sau[0]})"
                          + (f" | {nguoidanh}: NC {chisodanh[2]['ngoaicong1']}-{chisodanh[2]['ngoaicong2']}"
                             f" NộiC {chisodanh[2]['noicong1']}-{chisodanh[2]['noicong2']} BK {chisodanh[2]['baokich'] / 100:.2f}%"
                             if chisodanh else ""))
                truoc = {ten: hientai[ten] or truoc.get(ten) for ten in nhanvats}
        except KeyboardInterrupt:
            pass
    print(f"Đã ghi {sodon} đòn vào {duongdan}")


if __name__ == "__main__":
    main()
