# Thử hợp thành Tinh Thạch để đo tỉ lệ / số random máy chủ (chạy tay, người dùng nhờ 2026-11-17).
# Ghép 2 viên cùng tên (loại rác PHAIRAC, cấp <= CAPTOIDA) bằng "mix5 <id1># <id2># 0# 0# 0# 0" (định dạng client "mix5 %x# %x# %x# %x# %x#" ở xq+0x1B26E8;
# thêm " 0" cuối: đúng lệnh client gửi sau khi bấm Xác nhận ở hộp "Bạn có muốn hợp thành?" (bắt bằng --nghe 17/11),
# đọc khung chat: "Số lượng N, tỉ lệ thành công T xác xuất R" rồi dòng kết quả "Hợp thành thất bại, ..." / thành công.
# Mỗi lần ghi 1 dòng JSON vào _internal/hopthanh/<ID>.jsonl (kể cả dòng chat thô) để phân tích hàm random.
# Chạy: python -X utf8 thuhopthanh_xq.py [--id 342] [--solan 0 = tới khi hết cặp] [--thu] (--thu: chỉ liệt kê, không ghép)
import argparse
import itertools
import json
import os
import re
import sys
import time

import win32gui

from tienich_xq import is_tieudecuasogame
from moitruong_xq import MoiTruong

PHAIRAC = ("Phong", "Nguyệt", "Ám", "Ảnh", "Mộc")
CAPTOIDA = 3
MAUTENDA = re.compile(r"^(?P<phai>\S+) Tinh Thạch cấp (?P<cap>\d+)$")
MAUTILE = re.compile(r"Số lượng\s*(?P<n>\d+).*?tỉ lệ thành công\s*(?P<t>\d+).*?xác [xs]uất\s*(?P<r>\d+)", re.I)
# Ghép cần thể lực: hết thể lực thì máy chủ im lặng, không báo lỗi gì (17/11: dừng sau 9 lần, người dùng tắt Foxia)
THOIGIANCHOKETQUA = 8.
GIANCACH = 2.5


def timmoitruong(idnguoichoi):
    ketqua = []

    def callback(hwnd, _):
        if ketqua or not win32gui.IsWindowVisible(hwnd) or not is_tieudecuasogame(win32gui.GetWindowText(hwnd)):
            return
        try:
            mt = MoiTruong(hwnd)
            if mt.get_is_nhanvattontai() and int(mt.get_idnguoichoi() or 0) == idnguoichoi:
                ketqua.append(mt)
        except Exception:
            pass

    win32gui.EnumWindows(callback, None)
    return ketqua[0] if ketqua else None


def timcapda(mt):
    # {tên đá rác cấp <= CAPTOIDA: [id đối tượng...]}, chỉ tên có đúng 2 viên trở lên
    nhoms = {}
    for ten, vatphams in mt.get_danhsachvatphamhanhtrang_map().items():
        m = MAUTENDA.match(ten or "")
        if not m or m.group("phai") not in PHAIRAC or int(m.group("cap")) > CAPTOIDA:
            continue
        ids = [iddoituong for _, iddoituong in vatphams if iddoituong]
        if len(ids) >= 2:
            nhoms[ten] = ids
    return nhoms


def main():
    sys.stdout.reconfigure(encoding = "utf-8")
    ts = argparse.ArgumentParser()
    ts.add_argument("--id", type = int, default = 342)
    ts.add_argument("--solan", type = int, default = 0)
    ts.add_argument("--thu", action = "store_true")
    ts.add_argument("--nghe", type = int, default = 0)
    tham = ts.parse_args()

    mt = timmoitruong(tham.id)
    if not mt:
        print(f"Không thấy cửa sổ nhân vật ID {tham.id}")
        return
    print(f"Nhân vật: {mt.get_tendoituong()} (ID {tham.id})")
    for ten, ids in sorted(timcapda(mt).items()):
        print(f"  {ten}: {len(ids)} viên")
    if tham.thu:
        return
    # Dùng lại bộ đệm hook khung chat bot đã đặt (không có thì tự đặt); bộ đếm đã đọc là của riêng script, không ảnh hưởng bot
    if not mt.action_thietlaphookkhungchat():
        print("Không đặt được hook khung chat, dừng")
        return
    mt._docdongkhungchatmois()
    if tham.nghe:
        # Bắt lệnh client tự gửi ([LỆNH GAME] trong log nhân vật) + dòng khung chat trong tham.nghe giây, để người dùng ghép tay
        # 1 lần xem lệnh thật
        mt.action_thietlaphooklenhgame()
        mt.action_loglenhgame()
        print(f"Đang nghe {tham.nghe}s: ghép tay trong game đi")
        hethan = time.time() + tham.nghe
        while time.time() < hethan:
            mt.action_loglenhgame()
            for dong in mt._docdongkhungchatmois():
                print("[KHUNG CHAT]", dong)
            time.sleep(0.2)
        return

    thumuc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_internal", "hopthanh")
    os.makedirs(thumuc, exist_ok = True)
    duongdan = os.path.join(thumuc, f"{tham.id}.jsonl")
    dem = 0
    khongphanhoi = 0
    capbos = set()
    while not tham.solan or dem < tham.solan:
        nhoms = timcapda(mt)
        if not nhoms:
            print("Hết cặp đá để ghép")
            break
        # Cấp thấp trước, nhóm đông trước; bỏ cặp máy chủ đã không trả lời (17/11: 2 viên Phong cấp 1 gửi 2 lần đều im, đá còn nguyên)
        ten, ids = None, None
        for t in sorted(nhoms, key = lambda t: (int(MAUTENDA.match(t).group("cap")), -len(nhoms[t]), t)):
            cap = next(([a, b] for a, b in itertools.combinations(nhoms[t], 2) if frozenset((a, b)) not in capbos), None)
            if cap:
                ten, ids = t, cap
                break
        if not ids:
            print("Hết cặp đá ghép được")
            break
        caulenh = "mix5 " + " ".join("{:x}#".format(x) for x in (ids + [0, 0, 0, 0, 0])[:5]) + " 0"
        mt._docdongkhungchatmois()
        if not mt.action_thucthicaulenh2(caulenh, delay = 0., is_khancap = True):
            time.sleep(0.5)
            continue
        dongs, tile, ketqua = [], None, None
        hethan = time.time() + THOIGIANCHOKETQUA
        while time.time() < hethan and ketqua is None:
            time.sleep(0.2)
            for dong in mt._docdongkhungchatmois():
                thuong = dong.lower()
                if "đã mở" in thuong:
                    continue
                if "hợp thành" in thuong or "xác" in thuong or "tỉ lệ" in thuong or "tinh thạch" in thuong:
                    dongs.append(dong.strip())
                m = MAUTILE.search(dong)
                if m:
                    tile = {k: int(v) for k, v in m.groupdict().items()}
                elif "hợp thành" in thuong:
                    ketqua = "thatbai" if "thất bại" in thuong else ("thanhcong" if "thành công" in thuong else "khac")
        if ketqua is None and tile is None:
            capbos.add(frozenset(ids))
            khongphanhoi += 1
            print(f"{ten} {['{:x}'.format(x) for x in ids]}: máy chủ không trả lời, bỏ cặp này")
            if khongphanhoi >= 4:
                print("4 lần liền không phản hồi, dừng")
                break
            time.sleep(GIANCACH)
            continue
        khongphanhoi = 0
        banghi = {"thoidiem": time.strftime("%Y-%m-%d %H:%M:%S"), "da": ten, "ids": ["{:x}".format(x) for x in ids],
                  "soluong": tile and tile["n"], "tile": tile and tile["t"], "xacxuat": tile and tile["r"], "ketqua": ketqua, "dongs": dongs}
        with open(duongdan, "a", encoding = "utf-8") as f:
            f.write(json.dumps(banghi, ensure_ascii = False) + "\n")
        dem += 1
        print(f"[{dem}] {ten} x2 -> tỉ lệ {banghi['tile']} xác xuất {banghi['xacxuat']}: {ketqua} | {dongs}")
        time.sleep(GIANCACH)
    print(f"Đã ghép {dem} lần, log ở {duongdan}")


if __name__ == "__main__":
    main()
