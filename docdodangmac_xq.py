"""Ghi mô tả đồ đang mặc (nón, hạng liên, vũ khí, áo, yêu đới, giày, pháp bảo) + bảng chỉ số của mọi nhân vật đang mở.
Chạy tay, cần quyền Admin như bot:  python -X utf8 docdodangmac_xq.py
Kết quả: _internal/chisotrangbi/dodangmac.json {tên: {"id", "chiso", "do": {ô: mô tả}}} để so với đồ cấp 100
(tracuutrangbi_xq.py). Đồ đang mặc desc theo vị trí "desc <ô - 95>" (docmota trong sosanhbuild_xq).
"""
import json
import os
import sys
import time

from hangso_xq import VITRITRANGBIDAUTIEN
from sosanhbuild_xq import TENOTRANGBIs, docchiso, docmota, timnhanvats

SOOCANDOC = 7
FILEKETQUA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_internal", "chisotrangbi", "dodangmac.json")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding = "utf-8", line_buffering = True)
    nhanvats = timnhanvats()
    if not nhanvats:
        print("Không thấy cửa sổ game nào có nhân vật (chạy bằng quyền Admin?)")
        return
    ketqua = {}
    for ten, mt in nhanvats.items():
        dos = {}
        for i in range(SOOCANDOC):
            vitri = VITRITRANGBIDAUTIEN + i
            if not mt.get_iddoituongvatphamhanhtrang(vitri):
                continue
            mota = docmota(mt, vitri)
            if not mota:   # lần đầu có lúc chưa kịp nạp
                time.sleep(0.3)
                mota = docmota(mt, vitri)
            dos[TENOTRANGBIs[i]] = mota
        ketqua[ten] = {"id": mt.get_idnguoichoi(), "chiso": docchiso(mt), "do": dos}
        print(f"{ten}: {len(dos)} món")
    os.makedirs(os.path.dirname(FILEKETQUA), exist_ok = True)
    with open(FILEKETQUA, "w", encoding = "utf-8") as f:
        json.dump(ketqua, f, ensure_ascii = False, indent = 1)
    print("Đã ghi", FILEKETQUA)


if __name__ == "__main__":
    main()
