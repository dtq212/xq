# Tự động đăng nhập lại nhân vật vắng mặt (trước đây là các kịch bản tudongdangnhap*.py chạy riêng).
# Tài khoản của mọi máy nằm chung trong _internal/taikhoan_chung.json (mỗi dòng ghi máy nào được tự đăng nhập), luồng chạy trong trochoi_xq.py

import csv
import ctypes
import json
import os
import random
import re
import struct
import subprocess
import threading
import time

import pymem
import pymem.process
import pywintypes
import win32api
import win32con
import win32gui
import win32process

import diachi_xq
from diachi_xq import DC
from moitruong_xq import MoiTruong
from tienich_xq import read_bytes, read_chuoi, read_int, write_bytes, write_int
from tienich_xq import duongdantaikhoan, duongdantaikhoantheomay, is_tieudecuasogame, laytamngungdanghieuluc, tenmaynay, xoatamngung

# Mẫu regex, không ghi cứng số phiên bản: game cập nhật (2.01.07 -> 2.01.08...) hay đổi năm (ooo2026ooo) vẫn nhận ra cửa sổ
LAUNCHER_TITLE = r"client \d+(\.\d+)+$"
# Màn hình đăng nhập Aegis / Niết Bàn (trong game tiêu đề có thêm "(ID)" nên không khớp)
# Niết Bàn 1.01.93: màn đăng nhập "Chien Quoc Niet Ban.1.01.93" (bản cũ "Chien Quoc Niet Ban -- version: ...")
GAME_TITLE_LOGIN_SCREEN = r"Chien Quoc 2D --\S*-- v\.\d+(\.\d+)+|Chien Quoc Niet Ban( -- version: |\.)\d+(\.\d+)+"

# Hộp lỗi do chienquoc2d.dll hiện lúc mở client: xác thực client qua HTTPS (auth_http, chỉ thử 1 lần) mà mạng chậm / đứt thì hiện
# "Loi Ket Noi HTTPS" ("Loi Mang (5): WinINet 12002, buoc HttpSendRequest, lan 1/1. Ket noi qua cham / timeout"), máy chủ xác thực
# trả lỗi thì "Bao Mat Client"; hộp đứng chờ bấm OK, client treo không vào được (gặp 2026-11-06 lúc lag mạng)
CUA_SO_LOI_MANG = ["loi ket noi https", "bao mat client"]
DANH_SACH_CUA_SO_LOI = ["warning", "play"] + CUA_SO_LOI_MANG
# Gặp hộp lỗi mạng khi mở client: chờ bấy nhiêu giây cho mạng ổn rồi mới mở lại (mở lại ngay cũng lỗi y vậy)
THOIGIANCHOMANGLOI = 30.

# Cửa sổ bị dis về màn hình đăng nhập: thử đăng nhập lại ngay trong nó tối đa bấy nhiêu lần (vào lại tại chỗ, không mất chỗ phó bản),
# vẫn không vào được thì thôi giữ chỗ, xử lý như client không đăng nhập (đóng, mở game mới)
SOLANDANGNHAPLAICUASODIS = 2

# Số client tối đa cùng lúc. Lúc mở, xq.exe đếm mọi tiến trình tên đúng "xq.exe" (so từng byte, cả bản khác như Niết Bàn, cùng mã),
# quá 4 thì báo "You can not run more client program!" và treo cả quy trình đăng nhập. Niết Bàn được DLL của nó nâng lên 7, Aegis vẫn 4:
# client bot mở được vá lên số này (mogame), client mở tay qua play.exe vẫn bị giới hạn 4. Đổi file exe Aegis thành "XQ.exe" thì không
# bản nào đếm client Aegis nữa
SOCLIENTTOIDA = 7
# Niết Bàn không vá mã được (client không hợp lệ): giới hạn do DLL của nó đặt
GIOIHANCLIENTNIETBAN = 7

# Rớt khỏi game chừng này lần trong THOIGIANDEMBIDA giây thì coi như đang giành tài khoản với máy khác: tạm hoãn tự đăng nhập
# tài khoản đó THOIGIANTAMHOAN giây (xem TuDongDangNhap._theodoiroigame)
SOLANBIDALIENTUC = 3
THOIGIANDEMBIDA = 1800
THOIGIANTAMHOAN = 1800
# Nhân vật vắng chừng này giây mà tự đăng nhập vẫn chưa đưa vào lại được thì báo Telegram (kẹt quy trình đăng nhập...)
THOIGIANBAOVANG = 600
# Cửa sổ không trả lời tin nhắn liên tục chừng này giây mới coi là đơ mà kill. Vừa chọn nhân vật xong game load bản đồ, luồng giao
# diện bận vài giây không trả lời: trước đây chỉ chờ 1s là kill luôn => vừa vào game đã bị kill
THOIGIANTREOTOIDA = 60.
# Vừa bấm vào game xong, chừng này giây chưa thấy nhân vật thì vẫn coi là đang load: không đóng / kill cửa sổ đó, không đăng nhập ai khác
THOIGIANCHOVAOGAME = 90.
# xq.exe không có cửa sổ game: chỉ kill khi đã chạy chừng này giây (lúc chuyển từ màn chọn nhân vật vào game có thể thoáng không có cửa sổ)
TUOIXQAOTOITHIEU = 60.

TOADO_LAUNCHER = {
    "BTN_VAO_GAME": (530, 495)
}

TOADO_GAME = {
    "BTN_XACNHAN_SERVER": (760, 465),
}

TOADO_CUMMAYCHU = {
    1: (190, 185),
    2: (190, 221),
    3: (190, 234),
    4: (190, 259),
}

TOADO_MAYCHU = {
    1: (377, 182),
    2: (372, 206),
}

TOADO_CHONNHANVAT = {
    2: (369, 146),
    3: (560, 146),
    4: (188, 352),
    5: (369, 352),
    6: (560, 352),
}

DUONGDANGAMEMACDINH = r"E:\Games\ChienQuoc2D_Aegis\xq.exe"

# Đăng nhập bằng cách gọi hàm nút trong game (_DangNhapBangHam) thay cho click / gõ phím; False = dùng lại cách cũ
IS_DANGNHAPBANGHAM = True
# Địa chỉ trong diachi_xq mà đăng nhập bằng hàm cần (thiếu cái nào thì dùng cách bấm phím)
TENDIACHIDANGNHAP = ("MENUMAYCHU", "MENUDANGNHAP", "MENUCHONNHANVAT", "HAMXACNHANMAYCHU", "HAMNUTDANGNHAP", "HAMDATCHUOTONHAP",
                     "HAMCHONNHANVAT", "HAMVAOGAME", "THONGTINGAME", "TG_GIAODIEN", "NV_TEN")
# Địa chỉ riêng của tạo nhân vật (kéo gà A-Z): thiếu thì vẫn đăng nhập được, chỉ không tạo nhân vật
TENDIACHITAONHANVAT = ("MENUTAONHANVAT", "HAMMOTAONHANVAT", "HAMNUTTAONHANVAT")
# Byte "đang hiện" của từng menu (hàm ảo đầu tiên của menu đọc byte này)
DANGHIEN_MENU = {"MENUMAYCHU": 0x5C, "MENUDANGNHAP": 0x760, "MENUCHONNHANVAT": 0x34, "MENUTAONHANVAT": 0x238}
# Menu máy chủ: dữ liệu server.lst (+0x34, mỗi cụm CUM_KICHTHUOC byte), số cụm +0x38, cụm đang chọn +0x54, máy chủ đang chọn +0x58
# (-1 = chưa chọn), dòng chọn trong danh sách "gần đây" +0x808, cờ đã chọn máy chủ +0x80D, cờ vẽ lại +0x2C. Click hàng thứ n của
# danh sách (chưa cuộn) = chỉ số n - 1: cụm (y - 181) / 24, máy chủ (y - 174) / 22 (đúng TOADO_CUMMAYCHU / TOADO_MAYCHU cũ)
MMC_DULIEU = 0x34
MMC_SOCUM = 0x38
MMC_CUM = 0x54
MMC_MAYCHU = 0x58
MMC_GANDAY = 0x808
MMC_COCHON = 0x80D
MMC_VELAI = 0x2C
# Trong 1 cụm: tên cụm +0, tên máy chủ +0x2C (mỗi máy 20 byte), số máy chủ +0x284, trạng thái máy chủ +0x288 (mỗi máy 4 byte, <= 0 thì
# client không cho chọn), IP +0x378 (mỗi máy 20 byte), cổng +0x5D0 (mỗi máy 4 byte)
CUM_KICHTHUOC = 0x6C0
CUM_TENMAYCHU = 0x2C
CUM_SOMAYCHU = 0x284
CUM_TRANGTHAIMAYCHU = 0x288
# Menu nhập tài khoản: con trỏ ô nhập tài khoản / mật khẩu (chữ ở ô +0x24)
MDN_OTAIKHOAN = 0x34
MDN_OMATKHAU = 0x38
# Menu chọn nhân vật: 6 con trỏ ô nhân vật từ +0x54 (cùng cấu trúc đối tượng nhân vật: id +0x20, -1 = ô trống; tên NV_TEN),
# ô đang chọn +0x2C4 (-1 = chưa). Ô 0..2 hàng trên trái -> phải, 3..5 hàng dưới (char_index 1..6)
SOONHANVAT = 6
MCN_ONHANVAT = 0x54
MCN_DANGCHON = 0x2C4
ONV_ID = 0x20
# Cấp nhân vật trong ô (menu chọn nhân vật vẽ "%d" từ đây, dịch ngược hàm vẽ xq+0x14F2C0 2026-11-08)
ONV_CAPDO = 0x2EEC
# Menu tạo nhân vật [xq+0x380B4C] (dịch ngược 2026-11-08, chưa test trong game lúc viết). Nút Tạo ở menu chọn nhân vật (HAMMOTAONHANVAT)
# tạo / hiện menu, ghi ô trống (đếm từ 1, -1 = hết ô) vào +0x23C rồi ẩn menu chọn. Ô nhập tên +0x34 (chữ +0x24, tối đa 12 byte, không dấu
# cách), giới tính +0x38 (1 nam, 2 nữ), mặt +0x240 / tóc +0x244 (đếm từ 0, số kiểu +0x24C = 5 / +0x248 = 8), +0x44 = đang chờ máy chủ
# (nút Tạo bỏ qua khi khác 0). Nút Tạo (HAMNUTTAONHANVAT) kiểm tên rồi kết nối lại máy chủ; máy chủ chào thì client gửi
# "LOGIN <tài khoản> <md5> <tên> <giới tính> <mặt + 1> <tóc + 1> <ô>", tạo xong máy chủ gửi lại danh sách nhân vật => menu chọn hiện lại
MTN_OTEN = 0x34
MTN_GIOITINH = 0x38
MTN_DANGCHO = 0x44
MTN_O = 0x23C
MTN_MAT = 0x240
MTN_TOC = 0x244
MTN_SOTOC = 0x248
MTN_SOMAT = 0x24C
# Tên nhân vật tạo mới: tối đa 12 byte (client chặn dài hơn), chỉ chữ / số không dấu cho chắc qua bộ lọc tên; tiền tố + số ngẫu nhiên
SOBYTETENTOIDA = 12
SOCHUSOTEN = 4
# Tạo nhân vật: chờ máy chủ trả danh sách nhân vật tối đa chừng này giây mỗi tên; tên bị từ chối (trùng) thì thử tên khác, tối đa SOLANTHUTEN tên
THOIGIANCHOTAONHANVAT = 20.
SOLANTHUTEN = 3
# [TG + TG_GIAODIEN] + 0x1A4: trạng thái kết nối; 0xF / 0x31 / 0x32 = đang kết nối dở, nút Đăng nhập bỏ qua
GD_TRANGTHAIKETNOI = 0x1A4
TRANGTHAIDANGKETNOIs = (0xF, 0x31, 0x32)
# Bấm Đăng nhập xong chờ tối đa chừng này giây cho máy chủ trả danh sách nhân vật
THOIGIANCHODANHSACHNHANVAT = 20.


# Mẫu file cấu hình khi chưa có. Mỗi tài khoản nhận diện online theo "idnguoichoi" (cố định); chưa điền ID thì tạm so theo "tennhanvat".
# "maydangnhap": tên máy tự đăng nhập tài khoản này, rỗng = tắt. "duongdangames": {tên máy: đường dẫn xq.exe}
CAUHINHMAU = {
    "duongdangames": {},
    "taikhoans": [
        {
            "tennhanvat": "Tên nhân vật",
            "idnguoichoi": None,
            "user": "taikhoan",
            "pass": "matkhau",
            "group": 1,
            "server": 1,
            "char_index": 1,
            "vitricuaso": 1,
            "maydangnhap": "",
        },
    ],
}


def _gopfiletheomay():
    # Lần đầu chạy bản file chung: gộp các file riêng taikhoan_<tên máy>.json (máy nào đang bật tự đăng nhập thì các dòng của nó bật
    # cho máy đó, đang tắt thì để tắt). File cũ để nguyên cho bot bản cũ ở máy khác còn dùng
    cauhinh = {"duongdangames": {}, "taikhoans": []}
    for tenmay, duongdan in duongdantaikhoantheomay().items():
        try:
            with open(duongdan, encoding = "utf-8-sig") as file:
                cu = json.load(file)
        except Exception as err:
            print(f"[ĐĂNG NHẬP] Bỏ qua {duongdan} khi gộp: {err}")
            continue
        if cu.get("duongdangame"):
            cauhinh["duongdangames"][tenmay] = cu["duongdangame"]
        dacos = {taikhoan.get("user") for taikhoan in cauhinh["taikhoans"]}
        for taikhoan in cu.get("taikhoans", []):
            if taikhoan.get("user") and taikhoan.get("user") not in dacos and taikhoan.get("user") != CAUHINHMAU["taikhoans"][0]["user"]:
                cauhinh["taikhoans"].append(dict(taikhoan, maydangnhap = tenmay if cu.get("is_tudongdangnhap") else ""))
        print(f"[ĐĂNG NHẬP] Gộp {os.path.basename(duongdan)} vào {os.path.basename(duongdantaikhoan())}")
    return cauhinh if cauhinh["taikhoans"] else CAUHINHMAU


def taicauhinhdangnhap():
    # Đọc lỗi (sai cú pháp JSON...) thì trả về cấu hình rỗng có khoá "loi" để báo lên giao diện, và không được lưu đè lên file
    duongdan = duongdantaikhoan()
    if not os.path.exists(duongdan):
        luucauhinhdangnhap(_gopfiletheomay())
    try:
        # utf-8-sig: Notepad (nhất là Windows 7) lưu "UTF-8" kèm BOM ở đầu file
        with open(duongdan, encoding = "utf-8-sig") as file:
            cauhinh = json.load(file)
        if not isinstance(cauhinh, dict):
            raise ValueError("nội dung phải là một đối tượng JSON { ... }")
    except Exception as err:
        print(f"[ĐĂNG NHẬP] Lỗi đọc {duongdan}: {err}")
        return dict(CAUHINHMAU, duongdangames = {}, taikhoans = [], loi = f"File tài khoản bị lỗi: {err}")
    cauhinh.setdefault("duongdangames", {})
    cauhinh.setdefault("taikhoans", [])
    return cauhinh


def is_batchomaynay(taikhoan):
    return bool(taikhoan.get("maydangnhap")) and taikhoan.get("maydangnhap") == tenmaynay()


def taikhoanbatchomaynay(cauhinh):
    # Các tài khoản máy này được tự đăng nhập (thứ tự trong file = thứ tự đăng nhập)
    return [taikhoan for taikhoan in cauhinh.get("taikhoans", []) if is_batchomaynay(taikhoan)]


def _duongdanxq(duongdan):
    # Đường dẫn ghi là play.exe thì đổi về xq.exe cùng thư mục: so cửa sổ / tiến trình theo đường dẫn xq.exe
    if os.path.basename(duongdan).lower() == "play.exe":
        return os.path.join(os.path.dirname(duongdan), "xq.exe")
    return duongdan


def duongdangamemaynay(cauhinh):
    return _duongdanxq(cauhinh.get("duongdangames", {}).get(tenmaynay()) or cauhinh.get("duongdangame") or DUONGDANGAMEMACDINH)


def duongdangamecua(taikhoan, cauhinh):
    # Tài khoản có đường dẫn riêng (vd nhân vật bản Niết Bàn) thì dùng, trống thì dùng đường dẫn chung của máy
    return _duongdanxq((taikhoan.get("duongdangame") or "").strip() or duongdangamemaynay(cauhinh))


def _chuanhoaduongdan(duongdan):
    return os.path.normcase(os.path.abspath(duongdan))


def _duongdangamequanlys():
    # Các xq.exe tự đăng nhập của máy này quản lý (đường dẫn chung + đường dẫn riêng của tài khoản bật cho máy này): chỉ đóng / kill
    # client của các bản này, bản khác (mở tay) để nguyên
    cauhinh = taicauhinhdangnhap()
    return {_chuanhoaduongdan(duongdangamemaynay(cauhinh))} | {_chuanhoaduongdan(duongdangamecua(taikhoan, cauhinh))
                                                              for taikhoan in taikhoanbatchomaynay(cauhinh)}


def is_nietban(duongdangame):
    return os.path.exists(os.path.join(os.path.dirname(duongdangame), "ChienQuocNietBan.dll"))


def luucauhinhdangnhap(cauhinh):
    duongdan = duongdantaikhoan()
    if cauhinh.get("loi"):
        # Cấu hình rỗng do đọc lỗi: lưu vào sẽ xoá mất tài khoản người dùng vừa nhập
        print(f"[ĐĂNG NHẬP] Không lưu vì file đang lỗi, sửa lại {duongdan} trước")
        return False
    try:
        os.makedirs(os.path.dirname(duongdan), exist_ok = True)
        filetam = duongdan + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(cauhinh, file, ensure_ascii = False, indent = 4)
        os.replace(filetam, duongdan)
    except Exception as err:
        print(f"[ĐĂNG NHẬP] Lỗi lưu {duongdan}: {err}")


# Tắt tự động đăng nhập thì tuyệt đối không kill tiến trình / đóng cửa sổ nào, kể cả cửa sổ bị đơ (tắt giữa lúc đang đăng nhập dở
# thì các bước dọn dẹp còn lại cũng bỏ qua). TuDongDangNhap cập nhật cờ này theo nút bật/tắt
is_chophepdong = False


def _killtientrinh(pid):
    if not is_chophepdong:
        print(f"   -> Đang tắt tự động đăng nhập, không kill tiến trình (PID: {pid})")
        return False
    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output = True)
    return True


_diachigioihanclients = {}


def _diachigioihanclient(duongdangame):
    # Địa chỉ byte N trong "cmp edi, N / jle" (83 FF N 7E ..) ngay trước "push <thông báo>" của kiểm tra số client, dò trên file xq.exe
    # theo section PE (lưu đệm theo đường dẫn + thời điểm sửa file). None khi không thấy
    khoa = (duongdangame, os.path.getmtime(duongdangame))
    if khoa not in _diachigioihanclients:
        diachi = None
        with open(duongdangame, "rb") as f:
            d = f.read()
        pe = struct.unpack_from("<I", d, 0x3C)[0]
        sosection, kichthuocoptional = struct.unpack_from("<H", d, pe + 6)[0], struct.unpack_from("<H", d, pe + 20)[0]
        imagebase = struct.unpack_from("<I", d, pe + 24 + 28)[0]
        sections = [struct.unpack_from("<IIII", d, pe + 24 + kichthuocoptional + i * 40 + 8) for i in range(sosection)]

        def file2va(vitri):
            for _, va, rsize, raw in sections:
                if raw <= vitri < raw + rsize:
                    return imagebase + va + vitri - raw

        vitrithongbao = d.find(b"You can not run more client program!\0")
        if vitrithongbao >= 0:
            pushthongbao = b"\x68" + struct.pack("<I", file2va(vitrithongbao))
            vitri = d.find(pushthongbao)
            while vitri >= 0:
                # 83 FF N | 7E xx | 50 | 68 <"warning"> | 68 <thông báo>
                if d[vitri - 11:vitri - 9] == b"\x83\xff" and d[vitri - 8] == 0x7E and d[vitri - 6] == 0x50 and d[vitri - 5] == 0x68:
                    diachi = file2va(vitri - 9)
                    break
                vitri = d.find(pushthongbao, vitri + 1)
        _diachigioihanclients[khoa] = diachi
    return _diachigioihanclients[khoa]


def mogame(duongdangame, thumuc, is_vagioihan = True):
    # Mở thẳng "xq.exe ran" (lệnh play.exe dùng để vào game, bỏ qua launcher) ở trạng thái tạm dừng, vá giới hạn số client lên
    # SOCLIENTTOIDA rồi mới cho chạy (is_vagioihan, Niết Bàn thì không vá). Bỏ qua play.exe nên game có bản cập nhật thì phải tự mở
    # play.exe một lần.
    # Tiến trình bot nằm trong Job "đóng là kill hết" (trochoi_xq._gantientrinhvaojob): game mở từ đây phải tách khỏi Job, không thì
    # tắt bot là game cũng tắt theo. Đang chạy trong Job khác không cho tách (vd Job của IDE) thì mở bình thường
    lenh = f'"{duongdangame}" ran'
    try:
        hp, ht, pid, _ = win32process.CreateProcess(None, lenh, None, None, False,
                                                    win32con.CREATE_SUSPENDED | subprocess.CREATE_BREAKAWAY_FROM_JOB, None, thumuc,
                                                    win32process.STARTUPINFO())
    except pywintypes.error:
        hp, ht, pid, _ = win32process.CreateProcess(None, lenh, None, None, False, win32con.CREATE_SUSPENDED, None, thumuc,
                                                    win32process.STARTUPINFO())
    try:
        diachi = _diachigioihanclient(duongdangame) if is_vagioihan else None
        if is_vagioihan and (diachi is None or not ctypes.windll.kernel32.WriteProcessMemory(int(hp), ctypes.c_void_p(diachi), bytes([SOCLIENTTOIDA]), 1,
                                                                           None)):
            print("      ⚠️ Không vá được giới hạn số client: game vẫn chỉ cho chạy 4 xq.exe cùng lúc")
    finally:
        win32process.ResumeThread(ht)
        ht.Close()
        hp.Close()
    return pid


class _STARTUPINFOEXW(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong), ("lpReserved", ctypes.c_wchar_p), ("lpDesktop", ctypes.c_wchar_p), ("lpTitle", ctypes.c_wchar_p),
                ("dwX", ctypes.c_ulong), ("dwY", ctypes.c_ulong), ("dwXSize", ctypes.c_ulong), ("dwYSize", ctypes.c_ulong),
                ("dwXCountChars", ctypes.c_ulong), ("dwYCountChars", ctypes.c_ulong), ("dwFillAttribute", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong), ("wShowWindow", ctypes.c_ushort), ("cbReserved2", ctypes.c_ushort),
                ("lpReserved2", ctypes.c_void_p), ("hStdInput", ctypes.c_void_p), ("hStdOutput", ctypes.c_void_p),
                ("hStdError", ctypes.c_void_p), ("lpAttributeList", ctypes.c_void_p)]


class _PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", ctypes.c_void_p), ("hThread", ctypes.c_void_p), ("dwProcessId", ctypes.c_ulong), ("dwThreadId", ctypes.c_ulong)]


def _mocon_explorer(duongdanexe, thumuc):
    # Mở duongdanexe với tiến trình cha là explorer.exe của phiên này. False khi không làm được
    kernel32 = ctypes.WinDLL("kernel32", use_last_error = True)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    pid_explorer = win32process.GetWindowThreadProcessId(ctypes.windll.user32.GetShellWindow())[1]
    if not pid_explorer:
        return False
    hcha = kernel32.OpenProcess(0x0080, False, pid_explorer)  # PROCESS_CREATE_PROCESS
    if not hcha:
        return False
    try:
        kichthuoc = ctypes.c_size_t()
        kernel32.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(kichthuoc))
        danhsach = ctypes.create_string_buffer(kichthuoc.value)
        if not kernel32.InitializeProcThreadAttributeList(danhsach, 1, 0, ctypes.byref(kichthuoc)):
            return False
        try:
            giatricha = ctypes.c_void_p(hcha)
            # PROC_THREAD_ATTRIBUTE_PARENT_PROCESS
            if not kernel32.UpdateProcThreadAttribute(danhsach, 0, ctypes.c_size_t(0x00020000), ctypes.byref(giatricha),
                                                      ctypes.sizeof(giatricha), None, None):
                return False
            si = _STARTUPINFOEXW()
            si.cb = ctypes.sizeof(si)
            si.lpAttributeList = ctypes.cast(danhsach, ctypes.c_void_p)
            pi = _PROCESS_INFORMATION()
            lenh = ctypes.create_unicode_buffer(f'"{duongdanexe}"')
            # EXTENDED_STARTUPINFO_PRESENT
            if not kernel32.CreateProcessW(None, lenh, None, None, False, 0x00080000, None, thumuc, ctypes.byref(si), ctypes.byref(pi)):
                return False
            kernel32.CloseHandle(ctypes.c_void_p(pi.hThread))
            kernel32.CloseHandle(ctypes.c_void_p(pi.hProcess))
            return True
        finally:
            kernel32.DeleteProcThreadAttributeList(danhsach)
    finally:
        kernel32.CloseHandle(ctypes.c_void_p(hcha))


def molauncher(thumuc):
    # Niết Bàn từ 1.01.93 (ChienQuocNietBan.dll R4): xq.exe không do play.exe mở thì báo "launcher bắt buộc" và không vào được,
    # nên mở play.exe rồi bấm Đăng nhập như launcher mở tay. play.exe do bot mở (cha là python) thì game vẫn tự thoát sau ~2s,
    # do explorer mở (như bấm đúp) thì được: tạo tiến trình với cha là explorer (PROC_THREAD_ATTRIBUTE_PARENT_PROCESS), thư mục làm việc
    # là thư mục game (chạy "explorer.exe play.exe" thì sai thư mục, play.exe không đọc được play.ini, hiện "client 0").
    # Không còn explorer thì mở thẳng. Trả về cửa sổ launcher, 0 khi sau 20s chưa thấy
    if not _mocon_explorer(os.path.join(thumuc, "play.exe"), thumuc):
        subprocess.Popen([os.path.join(thumuc, "play.exe")], cwd = thumuc)
    for _ in range(40):
        time.sleep(0.5)
        hwnd = timlauncherdangmo(thumuc)
        if hwnd:
            return hwnd
    return 0


def _dongcuaso(hwnd):
    if not is_chophepdong:
        print(f"   -> Đang tắt tự động đăng nhập, không đóng cửa sổ (HWND: {hwnd})")
        return False
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    return True


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


def _safe_post_message(hwnd, msg, wparam, lparam):
    try:
        win32gui.PostMessage(hwnd, msg, wparam, lparam)
    except pywintypes.error as e:
        if e.winerror == 1400:
            return
        raise e


PHIMDIEUKHIENs = (win32con.VK_SHIFT, win32con.VK_CONTROL, win32con.VK_MENU, win32con.VK_LWIN, win32con.VK_RWIN)


def chonhaphimdieukhien(thoigiantoida = 5.):
    # Chỉ đọc trạng thái phím thật (không gửi gì ra bàn phím): nếu người dùng đang giữ Ctrl/Shift/Alt/Win
    # thì chờ nhả ra rồi mới gửi click/phím, tránh game hiểu thành tổ hợp phím (vd Shift+Tab, Alt+Enter)
    hethan = time.time() + thoigiantoida
    while time.time() < hethan:
        if not any(win32api.GetAsyncKeyState(phim) & 0x8000 for phim in PHIMDIEUKHIENs):
            return True
        time.sleep(0.05)
    return False


def click(hwnd, x, y, delay = 0.1):
    chonhaphimdieukhien()
    lparam = make_lparam(x, y)
    _safe_post_message(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
    time.sleep(delay)


def press_key(hwnd, key_code, delay = 0.1):
    chonhaphimdieukhien()
    _safe_post_message(hwnd, win32con.WM_KEYDOWN, key_code, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYUP, key_code, 0)
    time.sleep(delay)


def type_text(hwnd, text, delay = 0.05):
    for char in text:
        _safe_post_message(hwnd, win32con.WM_CHAR, ord(char), 0)
        time.sleep(delay)


# hwnd -> lúc bắt đầu không trả lời tin nhắn (đang đơ / đang load)
_thoidiembatdautreo = {}
# hwnd -> lúc vừa bấm vào game (dangnhaptrongcuaso), xem THOIGIANCHOVAOGAME
_thoidiemvaogame = {}


def laycuasodangvaogame():
    now = time.time()
    for hwnd in [h for h, t in _thoidiemvaogame.items() if now - t >= THOIGIANCHOVAOGAME or not win32gui.IsWindow(h) or _is_cuasodadangnhap(h)]:
        _thoidiemvaogame.pop(hwnd, None)
    return set(_thoidiemvaogame)


# Cửa sổ đơ ở phó bản đã báo "không kill" (chỉ in 1 lần mỗi đợt đơ)
_cuasophobandaobao = set()


def _is_cuasodangophoban(hwnd):
    # Đọc bộ nhớ vẫn được khi cửa sổ đơ (tiến trình còn sống). Không đọc được thì coi như không ở phó bản (giữ cách cũ: kill)
    try:
        mt = MoiTruong(hwnd)
        return bool(mt.get_is_nhanvattontai() and mt.get_is_dangophobandocbonho())
    except Exception:
        return False


def kiemtravadongcuasotreo(hwnd):
    # Chỉ trả về True (đã kill) khi cửa sổ không trả lời liên tục THOIGIANTREOTOIDA giây; đơ ngắn (load bản đồ) thì bỏ qua
    try:
        win32gui.PostMessage(hwnd, win32con.WM_NCMOUSEMOVE, 0, 0)
        time.sleep(0.2)

        win32gui.SendMessageTimeout(
            hwnd,
            win32con.WM_GETTEXTLENGTH,
            0,
            0,
            win32con.SMTO_NORMAL | win32con.SMTO_ABORTIFHUNG,
            3000
        )
        _thoidiembatdautreo.pop(hwnd, None)
        _cuasophobandaobao.discard(hwnd)
        return False

    except Exception:
        thoigiantreo = time.time() - _thoidiembatdautreo.setdefault(hwnd, time.time())
        if thoigiantreo < THOIGIANTREOTOIDA or hwnd in laycuasodangvaogame():
            print(f"   -> Cửa sổ không trả lời {int(thoigiantreo)}s (HWND: {hwnd}), có thể đang load, chờ thêm")
            return False
        if _is_cuasodangophoban(hwnd):
            # Kill giữa phó bản là nhân vật bị out, phải chạy lại 1-2 tầng mới lên được chỗ cũ (người dùng 2026-11-08): chờ tới khi hết đơ
            if hwnd not in _cuasophobandaobao:
                _cuasophobandaobao.add(hwnd)
                print(f"   -> Cửa sổ đơ {int(thoigiantreo)}s (HWND: {hwnd}) nhưng đang ở phó bản: không kill, chờ hết đơ")
            return False
        _thoidiembatdautreo.pop(hwnd, None)
        print(f"⚠️ Phát hiện cửa sổ bị đơ ngầm {int(thoigiantreo)}s (HWND: {hwnd}). Đang thực hiện dọn dẹp...")
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if _killtientrinh(pid):
                print(f"✅ Đã đóng thành công cửa sổ lỗi (PID: {pid}).")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi cố gắng dọn dẹp cửa sổ: {e}")
            return False


def chuanhoatennhanvat(tennhanvat):
    # Gộp mọi loại khoảng trắng (kể cả Alt+255 / U+00A0 trong tên nhân vật) thành dấu cách thường trước khi so
    return " ".join((tennhanvat or "").split()).lower()


def laydanhsachnhanvatonlines():
    # "cuaso": {hwnd: ID người chơi} của các cửa sổ đang có nhân vật (để nhận ra cửa sổ đó khi bị dis về màn hình đăng nhập),
    # "tentheocuaso": {hwnd: tên đã chuẩn hoá} (nhận ra cửa sổ của tài khoản chưa điền ID / tự điền ID)
    online_chars = {"ten": set(), "id": set(), "cuaso": {}, "tentheocuaso": {}}
    duongdans = _duongdangamequanlys()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if is_tieudecuasogame(title):
                # Chỉ kill cửa sổ đơ của bản tự đăng nhập quản lý
                if _is_cuasoquanly(hwnd, duongdans) and kiemtravadongcuasotreo(hwnd):
                    return

                try:
                    mt = MoiTruong(hwnd)
                    if mt.get_is_nhanvattontai():
                        idnguoichoi = mt.get_idnguoichoi()
                        if idnguoichoi:
                            online_chars["id"].add(int(idnguoichoi))
                            online_chars["cuaso"][hwnd] = int(idnguoichoi)
                        tennhanvat = chuanhoatennhanvat(mt.get_tendoituong())
                        if tennhanvat:
                            online_chars["ten"].add(tennhanvat)
                            online_chars["tentheocuaso"][hwnd] = tennhanvat
                except:
                    pass

    win32gui.EnumWindows(callback, None)
    return online_chars


def _is_cuasoquanly(hwnd, duongdans):
    # Cửa sổ của xq.exe nằm trong duongdans (_duongdangamequanlys)
    try:
        return _layduongdantientrinh(win32process.GetWindowThreadProcessId(hwnd)[1]) in duongdans
    except pywintypes.error:
        return False


def timlauncherdangmo(thumucgame = None):
    # thumucgame: chỉ nhận launcher (play.exe) của bản game trong thư mục này
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if re.match(LAUNCHER_TITLE, title):
                if thumucgame:
                    duongdan = _layduongdantientrinh(win32process.GetWindowThreadProcessId(hwnd)[1])
                    if not duongdan or os.path.dirname(duongdan) != _chuanhoaduongdan(thumucgame):
                        return
                hwnd_found = hwnd

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def timcuanhbaoloi():
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            title_thuong = title.lower()
            for loi_title in DANH_SACH_CUA_SO_LOI:
                # Bản 2.01.06 tiêu đề có hậu tố, vd "warning -- Ping: N/A"
                if title_thuong == loi_title or title_thuong.startswith(loi_title + " "):
                    hwnd_found = hwnd
                    break

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def _is_cuasodadangnhap(hwnd):
    # Bản 2.01.06 tiêu đề màn hình đăng nhập và trong game có thể trùng tiền tố, kiểm tra bộ nhớ để không đóng nhầm cửa sổ đang chơi
    try:
        mt = MoiTruong(hwnd)
        return bool(mt.get_is_nhanvattontai() and mt.get_idnguoichoi())
    except:
        return False


def _is_cuasomanhinhdangnhap(hwnd):
    # Cửa sổ game đang ở màn hình đăng nhập (mới mở, hoặc bị dis về), chưa có nhân vật. Chỉ so tiền tố tiêu đề: trong game tiêu đề
    # là "Chien Quoc 2D (ID) -oo2026oo- ...", bị dis về màn chọn máy chủ có thể vẫn giữ tiêu đề đó chứ không đổi về tiêu đề đăng nhập
    if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd) or not is_tieudecuasogame(win32gui.GetWindowText(hwnd)):
        return False
    r = win32gui.GetWindowRect(hwnd)
    w, h = r[2] - r[0], r[3] - r[1]
    return 790 < w < 830 and 590 < h < 660 and not _is_cuasodadangnhap(hwnd)


def timcuasogamedangbiket(boquas = (), duongdans = None, pid = None):
    # boquas: cửa sổ bị dis đang giữ chỗ cho nhân vật khác (đăng nhập lại ngay trong đó thì vào lại tại chỗ, đóng là mất chỗ phó bản)
    # duongdans: chỉ cửa sổ của các xq.exe này; pid: chỉ cửa sổ của tiến trình này
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if hwnd in boquas:
            return
        if pid is not None and win32process.GetWindowThreadProcessId(hwnd)[1] != pid:
            return
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if re.search(GAME_TITLE_LOGIN_SCREEN, title) and (duongdans is None or _is_cuasoquanly(hwnd, duongdans)):
                r = win32gui.GetWindowRect(hwnd)
                w, h = r[2] - r[0], r[3] - r[1]
                if 790 < w < 830 and 590 < h < 660 and not _is_cuasodadangnhap(hwnd):
                    hwnd_found = hwnd

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def mogamevadangnhap(char_name, config, duongdangame, cuasogiuchos = ()):
    # cuasogiuchos: cửa sổ bị dis của nhân vật khác, không đóng / không nhận nhầm là cửa sổ mới mở
    print(f"\n[ĐĂNG NHẬP] >>> BẮT ĐẦU QUY TRÌNH CHO: {char_name}")
    # Cửa sổ vừa bấm vào game, đang load: cũng không đóng / kill
    cuasogiuchos = set(cuasogiuchos) | laycuasodangvaogame()
    is_nietbanmo = is_nietban(duongdangame)
    gioihan = GIOIHANCLIENTNIETBAN if is_nietbanmo else SOCLIENTTOIDA
    try:
        hwnd_game_stuck = timcuasogamedangbiket(cuasogiuchos, duongdans = _duongdangamequanlys())
        if hwnd_game_stuck:
            print(f"   -> Phát hiện cửa sổ chờ (HWND: {hwnd_game_stuck}). Đang đóng...")
            try:
                if _dongcuaso(hwnd_game_stuck):
                    time.sleep(5)
            except Exception as e:
                print(f"   -> Lỗi khi đóng cửa sổ cũ: {e}")

        if not giaiphongchoclient(cuasogiuchos, gioihan):
            print(f"   -> Đã đủ {gioihan} client mà không có client nào đóng được (đều đang chơi / giữ chỗ). Không mở thêm.")
            return False

        hwnd_game = 0
        hwnd_launcher = timlauncherdangmo(os.path.dirname(duongdangame))
        if hwnd_launcher:
            print(f"   -> Tìm thấy Launcher (HWND: {hwnd_launcher}).")
            if win32gui.IsIconic(hwnd_launcher):
                win32gui.ShowWindow(hwnd_launcher, win32con.SW_SHOWNOACTIVATE)
        else:
            if not os.path.exists(duongdangame):
                print(f"❌ Không tìm thấy file game: {duongdangame} (sửa \"Đường dẫn game\" ở thẻ Đăng nhập)")
                return
            game_dir = os.path.dirname(duongdangame)

            dondepclientkhongdangnhap(cuasogiuchos = cuasogiuchos)

            max_retries = 3
            success_open = False

            if is_nietbanmo:
                print("   -> Mở launcher play.exe (Niết Bàn bắt buộc vào game qua launcher)...")
                hwnd_launcher = molauncher(game_dir)
                if not hwnd_launcher:
                    print("❌ Lỗi: Launcher play.exe không hiện lên sau 20s!")
                    return
                print(f"   -> Launcher đã lên (HWND: {hwnd_launcher}).")
            else:
                print("   -> Mở file exe mới...")

            for attempt in range(0 if is_nietbanmo else max_retries):
                print(f"      [Lần thử {attempt + 1}/{max_retries}] Đang chạy lệnh mở game...")
                pid = mogame(duongdangame, game_dir, is_vagioihan = not is_nietbanmo)

                # Mở thẳng vào game (không qua launcher): chờ cửa sổ đăng nhập của chính tiến trình vừa mở tối đa 20s, kiểm tra mỗi 0.5s
                for i in range(40):
                    hwnd_game = timcuasogamedangbiket(cuasogiuchos, pid = pid)
                    if hwnd_game:
                        success_open = True
                        break

                    hwnd_error = timcuanhbaoloi()
                    if hwnd_error:
                        title_error = win32gui.GetWindowText(hwnd_error)
                        print(f"\n      ⚠️ CẢNH BÁO: Phát hiện cửa sổ '{title_error}' (HWND: {hwnd_error}).")
                        print("      -> Đang gửi lệnh ĐÓNG cửa sổ lỗi...")
                        try:
                            _dongcuaso(hwnd_error)
                        except Exception as e:
                            print(f"      -> Lỗi khi đóng: {e}")

                        dondeptientrinhaovuabithoatgame(tuoitoithieu = 0.)
                        dondepclientkhongdangnhap(tuoitoithieu = 0., cuasogiuchos = cuasogiuchos)

                        if title_error.strip().lower() in CUA_SO_LOI_MANG:
                            print(f"      -> Lỗi mạng khi xác thực client: chờ {THOIGIANCHOMANGLOI:.0f}s cho mạng ổn rồi mới mở lại")
                            time.sleep(THOIGIANCHOMANGLOI)
                        break

                    time.sleep(0.5)

                if success_open:
                    break
                else:
                    print("      -> Hết thời gian chờ. Thử lại quy trình...")
                    time.sleep(5)

        if hwnd_launcher:
            # Launcher có sẵn (mở tay): bấm "Vào game" như cũ
            time.sleep(2)
            lx, ly = TOADO_LAUNCHER["BTN_VAO_GAME"]
            click(hwnd_launcher, lx, ly)
            time.sleep(1)
            click(hwnd_launcher, lx, ly)

            for i in range(60):
                time.sleep(1)
                hwnd_game = timcuasogamedangbiket(cuasogiuchos, duongdans = {_chuanhoaduongdan(duongdangame)})
                if hwnd_game: break
                # Click có thể bị launcher nuốt mất: bấm lại "Vào game" mỗi 15s
                if (i + 1) % 15 == 0 and win32gui.IsWindow(hwnd_launcher):
                    print(f"   -> Chưa thấy cửa sổ game sau {i + 1}s, bấm lại Vào game...")
                    click(hwnd_launcher, lx, ly)

            if not hwnd_game:
                print("❌ Lỗi: Cửa sổ Game không hiện lên! Launcher có thể bị đơ -> Đóng launcher để lần sau mở lại từ đầu.")
                donglauncher(hwnd_launcher)
                return
        elif not hwnd_game:
            print("❌ Lỗi: Không mở được cửa sổ game sau nhiều lần thử!")
            return

        print(f"[5] Game đã lên (HWND: {hwnd_game}). Đợi load Login (2s)...")
        dangnhaptrongcuaso(hwnd_game, char_name, config)

    except Exception as e:
        print(f"❌ Exception: {e}")


class _DangNhapBangHam:
    # Đăng nhập bằng cách gọi thẳng hàm của các nút trên màn hình đăng nhập trong xq.exe (luồng từ xa, như HAMGUILENH của MoiTruong),
    # không click / gõ phím: không phụ thuộc toạ độ, cửa sổ ẩn / thu nhỏ, phím Ctrl/Shift người dùng đang giữ. Dịch ngược 2026-11-08,
    # Aegis và Niết Bàn cùng mã. Thứ tự màn hình: chọn máy chủ (MENUMAYCHU) -> nhập tài khoản (MENUDANGNHAP) -> chọn nhân vật
    # (MENUCHONNHANVAT) -> vào game. Mỗi menu có cờ "đang hiện" (hàm ảo đầu tiên của menu đọc đúng byte này)

    def __init__(self, hwnd):
        self.hwnd = hwnd
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        self.tientrinh = pymem.Pymem()
        self.tientrinh.open_process_from_id(pid)
        xqmodule = pymem.process.module_from_name(self.tientrinh.process_handle, "xq.exe")
        if not xqmodule:
            raise Exception("không thấy module xq.exe")
        self.diachixq = xqmodule.lpBaseOfDll
        diachi_xq.khoitao(xqmodule.filename)
        thieu = [ten for ten in TENDIACHIDANGNHAP if ten in " ".join(DC.loi)]
        if thieu:
            raise Exception(f"chữ ký không dò được: {', '.join(thieu)}")

    def dong(self):
        try:
            self.tientrinh.close_process()
        except Exception:
            pass

    def _doc(self, diachi):
        return read_int(self.tientrinh, diachi)

    def menu(self, ten):
        # Con trỏ menu (0 = chưa tạo)
        return self._doc(self.diachixq + getattr(DC, ten))

    def is_menudanghien(self, ten):
        diachi = self.menu(ten)
        return bool(diachi) and read_bytes(self.tientrinh, diachi + DANGHIEN_MENU[ten], 1) != b"\0"

    def menudanghien(self):
        for ten in (("MENUTAONHANVAT",) if self.is_taonhanvatduoc() else ()) + ("MENUCHONNHANVAT", "MENUDANGNHAP", "MENUMAYCHU"):
            if self.is_menudanghien(ten):
                return ten
        return None

    def chomenu(self, tens, thoigiantoida):
        # Chờ tới khi 1 trong các menu tens hiện, trả về tên menu đó (None: hết giờ)
        hethan = time.time() + thoigiantoida
        while True:
            ten = self.menudanghien()
            if ten in tens:
                return ten
            if time.time() >= hethan or not win32gui.IsWindow(self.hwnd):
                return None
            time.sleep(0.2)

    def goiham(self, tenham, this = None, thamsos = (), chuois = ()):
        # Chạy hàm trong game bằng luồng từ xa: [push tham số] [mov ecx, this] call hàm; ret 4. chuois: các chuỗi chép vào vùng nhớ cấp
        # tạm, thamsos ghi "chuoi<i>" thì thay bằng địa chỉ chuỗi thứ i. Vùng nhớ xoá trắng rồi giải phóng sau khi chạy (có mật khẩu)
        kichthuoc = 64 + sum(len(c) + 1 for c in chuois)
        vung = self.tientrinh.allocate(kichthuoc)
        try:
            diachichuois, vitri = [], vung + 64
            for chuoi in chuois:
                write_bytes(self.tientrinh, vitri, chuoi + b"\0", len(chuoi) + 1)
                diachichuois.append(vitri)
                vitri += len(chuoi) + 1
            ma = b""
            for t in reversed(thamsos):
                t = diachichuois[int(t[5:])] if isinstance(t, str) else t
                ma += b"\x68" + struct.pack("<I", t & 0xFFFFFFFF)
            if this is not None:
                ma += b"\xB9" + struct.pack("<I", this)
            ma += b"\xB8" + struct.pack("<I", self.diachixq + getattr(DC, tenham)) + b"\xFF\xD0" + b"\x33\xC0\xC2\x04\x00"
            write_bytes(self.tientrinh, vung, ma, len(ma))
            # pymem chờ luồng chạy xong nhưng không đóng handle
            ctypes.windll.kernel32.CloseHandle(self.tientrinh.start_thread(vung))
        finally:
            try:
                write_bytes(self.tientrinh, vung, bytes(kichthuoc), kichthuoc)
                self.tientrinh.free(vung)
            except Exception:
                pass

    def chonmaychu(self, cum, maychu):
        # cum, maychu đếm từ 1 như cấu hình ("group", "server"): đúng hàng thứ mấy trên danh sách lúc chưa cuộn
        menumaychu = self.menu("MENUMAYCHU")
        socum = self._doc(menumaychu + MMC_SOCUM)
        dulieu = self._doc(menumaychu + MMC_DULIEU)
        icum, imaychu = cum - 1, maychu - 1
        if not dulieu or not 0 <= icum < socum:
            print(f"   -> [Hàm] Không có cụm {cum} (có {socum} cụm)")
            return False
        cumdulieu = dulieu + icum * CUM_KICHTHUOC
        somaychu = self._doc(cumdulieu + CUM_SOMAYCHU)
        if not 0 <= imaychu < somaychu:
            print(f"   -> [Hàm] Cụm {cum} không có máy chủ {maychu} (có {somaychu} máy)")
            return False
        tencum = read_chuoi(self.tientrinh, cumdulieu, 0x2C).decode("latin1", "ignore")
        tenmaychu = read_chuoi(self.tientrinh, cumdulieu + CUM_TENMAYCHU + imaychu * 20, 20).decode("latin1", "ignore")
        if self._doc(cumdulieu + CUM_TRANGTHAIMAYCHU + imaychu * 4) <= 0:
            # Client cũng không cho chọn máy chủ trạng thái <= 0 (bảo trì / chưa mở)
            print(f"   -> [Hàm] Máy chủ {tenmaychu} ({tencum}) đang đóng, không chọn được")
            return False
        print(f"   -> [Hàm] Chọn cụm {cum} \"{tencum}\", máy chủ {maychu} \"{tenmaychu}\"")
        # Y như click: click cụm ghi +0x54 và cờ vẽ lại +0x2C, click máy chủ ghi +0x58, bỏ chọn danh sách "gần đây" +0x808, bật cờ +0x80D
        write_int(self.tientrinh, menumaychu + MMC_CUM, icum)
        write_int(self.tientrinh, menumaychu + MMC_VELAI, 1)
        write_int(self.tientrinh, menumaychu + MMC_MAYCHU, imaychu)
        write_int(self.tientrinh, menumaychu + MMC_GANDAY, -1)
        write_bytes(self.tientrinh, menumaychu + MMC_COCHON, b"\x01", 1)
        self.goiham("HAMXACNHANMAYCHU")
        return True

    def nhaptaikhoan(self, taikhoan, matkhau):
        menudangnhap = self.menu("MENUDANGNHAP")
        trangthai = self._doc(self._doc(self._doc(self.diachixq + DC.THONGTINGAME) + DC.TG_GIAODIEN) + GD_TRANGTHAIKETNOI)
        if trangthai in TRANGTHAIDANGKETNOIs:
            # Nút Đăng nhập không làm gì khi client đang kết nối dở (lần bấm trước chưa xong)
            print(f"   -> [Hàm] Client đang kết nối dở (trạng thái {hex(trangthai)}), bấm Đăng nhập sẽ không có tác dụng")
        self.goiham("HAMDATCHUOTONHAP", this = self._doc(menudangnhap + MDN_OTAIKHOAN), thamsos = ("chuoi0",), chuois = (taikhoan.encode("latin1"),))
        self.goiham("HAMDATCHUOTONHAP", this = self._doc(menudangnhap + MDN_OMATKHAU), thamsos = ("chuoi0",), chuois = (matkhau.encode("latin1"),))
        print("   -> [Hàm] Đã điền tài khoản & mật khẩu, bấm Đăng nhập")
        self.goiham("HAMNUTDANGNHAP")

    def danhsachnhanvat(self):
        # [(ô 0..5, id, tên, cấp)] các ô có nhân vật (id -1 = ô trống)
        menuchon = self.menu("MENUCHONNHANVAT")
        ketqua = []
        for o in range(SOONHANVAT):
            nhanvat = self._doc(menuchon + MCN_ONHANVAT + 4 * o)
            if not nhanvat:
                continue
            idnhanvat = self._doc(nhanvat + ONV_ID)
            if idnhanvat == -1:
                continue
            ten = read_chuoi(self.tientrinh, nhanvat + DC.NV_TEN, 32).decode("utf-8", "ignore")
            ketqua.append((o, idnhanvat, ten, self._doc(nhanvat + ONV_CAPDO)))
        return ketqua

    def _chodanhsachnhanvat(self, thoigiantoida = 3.):
        hethan = time.time() + thoigiantoida
        nhanvats = self.danhsachnhanvat()
        while not nhanvats and time.time() < hethan:
            time.sleep(0.2)
            nhanvats = self.danhsachnhanvat()
        return nhanvats

    def chonvavaogame(self, config):
        # Chọn ô theo ID / tên nhân vật nếu khớp (đổi thứ tự ô vẫn đúng người), không thì theo "char_index" (1..6)
        nhanvats = self._chodanhsachnhanvat()
        print("   -> [Hàm] Các ô nhân vật: " + ", ".join(f"ô {o + 1}: {ten} (ID {idnv}, cấp {cap})" for o, idnv, ten, cap in nhanvats))
        idnguoichoi, tennhanvat = config.get("idnguoichoi"), chuanhoatennhanvat(config.get("tennhanvat"))
        o = next((o for o, idnv, ten, _ in nhanvats if idnguoichoi and idnv == idnguoichoi), None)
        if o is None:
            o = next((o for o, idnv, ten, _ in nhanvats if tennhanvat and chuanhoatennhanvat(ten) == tennhanvat), None)
        if o is None:
            o = int(config.get("char_index", 1)) - 1
            if not any(oo == o for oo, _, _, _ in nhanvats):
                print(f"   -> [Hàm] Ô nhân vật {o + 1} trống / không có")
                return False
        elif o != int(config.get("char_index", 1)) - 1:
            print(f"   -> [Hàm] Nhân vật đang ở ô {o + 1} (cấu hình ghi ô {config.get('char_index', 1)}), chọn ô {o + 1}")
        menuchon = self.menu("MENUCHONNHANVAT")
        self.goiham("HAMCHONNHANVAT", this = menuchon, thamsos = (o,))
        if self._doc(menuchon + MCN_DANGCHON) != o:
            print(f"   -> [Hàm] Chọn ô nhân vật {o + 1} không được")
            return False
        print(f"   -> [Hàm] Chọn ô nhân vật {o + 1}, bấm Vào game")
        self.goiham("HAMVAOGAME")
        return True

    def is_taonhanvatduoc(self):
        return not [ten for ten in TENDIACHITAONHANVAT if ten in " ".join(DC.loi)]

    def taonhanvat(self, tiento, gioitinh = 0):
        # Tạo 1 nhân vật ở ô trống (đang ở menu chọn nhân vật hoặc menu tạo nhân vật). -> (id, tên) nhân vật mới / None.
        # gioitinh 1 nam, 2 nữ, 0 ngẫu nhiên; mặt / tóc ngẫu nhiên
        if not self.is_taonhanvatduoc():
            print("   -> [Hàm] Chữ ký tạo nhân vật không dò được, không tạo được nhân vật")
            return None
        if not self.is_menudanghien("MENUTAONHANVAT"):
            self.goiham("HAMMOTAONHANVAT")
            if self.chomenu(("MENUTAONHANVAT",), 5.) is None:
                print("   -> [Hàm] Bấm Tạo mà không thấy menu tạo nhân vật")
                return None
        menutao = self.menu("MENUTAONHANVAT")
        o = self._doc(menutao + MTN_O)
        if o <= 0:
            print("   -> [Hàm] Hết ô trống để tạo nhân vật")
            return None
        gioitinh = gioitinh if gioitinh in (1, 2) else random.choice((1, 2))
        write_int(self.tientrinh, menutao + MTN_GIOITINH, gioitinh)
        somat, sotoc = self._doc(menutao + MTN_SOMAT), self._doc(menutao + MTN_SOTOC)
        if somat > 0:
            write_int(self.tientrinh, menutao + MTN_MAT, random.randrange(somat))
        if sotoc > 0:
            write_int(self.tientrinh, menutao + MTN_TOC, random.randrange(sotoc))
        tiento = re.sub(r"[^A-Za-z0-9]", "", tiento or "")[:SOBYTETENTOIDA - SOCHUSOTEN] or "ga"
        for lan in range(SOLANTHUTEN):
            ten = tiento + "".join(random.choice("0123456789") for _ in range(SOCHUSOTEN))
            print(f"   -> [Hàm] Tạo nhân vật \"{ten}\" ({'nam' if gioitinh == 1 else 'nữ'}) ở ô {o} (lần {lan + 1}/{SOLANTHUTEN})")
            # Lần bấm trước bị từ chối có thể còn cờ đang chờ máy chủ: bỏ cờ, không thì nút Tạo không làm gì
            write_bytes(self.tientrinh, menutao + MTN_DANGCHO, b"\0", 1)
            self.goiham("HAMDATCHUOTONHAP", this = self._doc(menutao + MTN_OTEN), thamsos = ("chuoi0",), chuois = (ten.encode("latin1"),))
            self.goiham("HAMNUTTAONHANVAT")
            if self.chomenu(("MENUCHONNHANVAT",), THOIGIANCHOTAONHANVAT) is None:
                if not win32gui.IsWindow(self.hwnd) or not self.is_menudanghien("MENUTAONHANVAT"):
                    print(f"   -> [Hàm] {THOIGIANCHOTAONHANVAT:.0f}s không quay lại menu chọn nhân vật, cũng không còn ở menu tạo")
                    return None
                print(f"   -> [Hàm] {THOIGIANCHOTAONHANVAT:.0f}s chưa quay lại menu chọn nhân vật (tên trùng / bị từ chối?), thử tên khác")
                continue
            time.sleep(1.)
            moi = next(((idnv, tennv) for _, idnv, tennv, _ in self._chodanhsachnhanvat() if chuanhoatennhanvat(tennv) == ten.lower()), None)
            if moi:
                print(f"   -> [Hàm] Đã tạo nhân vật {moi[1]} (ID {moi[0]})")
                return moi
            print(f"   -> [Hàm] Quay lại menu chọn nhân vật mà không thấy \"{ten}\" (máy chủ từ chối?)")
            return None
        return None

    def chonhoactaoga(self, config):
        # Kéo gà A-Z (config["taoga"]): chọn nhân vật cấp < capketthuc chưa kéo xong (cấp cao nhất trước, đỡ kéo lại từ đầu), không có thì
        # tạo nhân vật mới ở ô trống; hết ô thì báo "het". Kết quả ghi vào taoga["ketqua"]: id, ten, cap, tao (mới tạo), het, loitao, caps
        taoga = config["taoga"]
        ketqua = taoga.setdefault("ketqua", {})
        capketthuc = int(taoga.get("capketthuc") or 0)
        daxongs = {int(i) for i in taoga.get("idsdaxong") or ()}
        nhanvats = self._chodanhsachnhanvat()
        print("   -> [Hàm] Các ô nhân vật: " + (", ".join(f"ô {o + 1}: {ten} (ID {idnv}, cấp {cap})" for o, idnv, ten, cap in nhanvats) or "trống"))
        ketqua["caps"] = {idnv: cap for _, idnv, _, cap in nhanvats}
        chons = [(cap, o, idnv, ten) for o, idnv, ten, cap in nhanvats if cap < capketthuc and idnv not in daxongs]
        if chons:
            # Vào lại acc gà đang trong lượt (bị dis) thì đúng nhân vật đó
            cap, o, idnv, ten = next((c for c in chons if c[2] == taoga.get("idchon")), max(chons))
            print(f"   -> [Hàm] Kéo gà: chọn nhân vật cấp {cap} < {capketthuc}: {ten} (ID {idnv})")
            ketqua.update(id = idnv, ten = ten, cap = cap, tao = False)
        elif len(nhanvats) < SOONHANVAT:
            moi = self.taonhanvat(taoga.get("tiento"), int(taoga.get("gioitinh") or 0))
            if not moi:
                ketqua["loitao"] = True
                return False
            idnv, ten = moi
            ketqua.update(id = idnv, ten = ten, cap = 0, tao = True)
        else:
            print(f"   -> [Hàm] Kéo gà: cả {SOONHANVAT} ô đều là nhân vật đã kéo xong (cấp >= {capketthuc}), tài khoản hết chỗ")
            ketqua["het"] = True
            return False
        return self.chonvavaogame(dict(config, idnguoichoi = ketqua["id"], tennhanvat = ketqua["ten"]))


def _dangnhapbangham(hwnd_game, char_name, config):
    # True: đã bấm Vào game. False: lỗi giữa chừng (để lượt sau thử lại). None: chưa dùng được (không mở được tiến trình, thiếu địa chỉ,
    # chưa thấy menu nào) => dùng cách click / gõ phím cũ
    try:
        dn = _DangNhapBangHam(hwnd_game)
    except Exception as e:
        print(f"   -> [Hàm] Không đăng nhập bằng hàm được ({e}), dùng cách bấm phím")
        return None
    try:
        menu = dn.chomenu(("MENUMAYCHU", "MENUDANGNHAP", "MENUCHONNHANVAT", "MENUTAONHANVAT"), 15.)
        if menu == "MENUTAONHANVAT":
            # Kẹt ở màn tạo nhân vật (lần trước tạo dở): kéo gà thì tạo tiếp, không thì không biết đường về
            if not config.get("taoga"):
                print("   -> [Hàm] Đang ở màn tạo nhân vật, không đăng nhập tiếp được")
                return False
            if not dn.taonhanvat(config["taoga"].get("tiento"), int(config["taoga"].get("gioitinh") or 0)):
                config["taoga"].setdefault("ketqua", {})["loitao"] = True
                return False
            menu = "MENUCHONNHANVAT"
        if menu is None:
            print("   -> [Hàm] Chưa thấy màn hình chọn máy chủ / đăng nhập / chọn nhân vật, dùng cách bấm phím")
            return None
        if menu == "MENUMAYCHU":
            try:
                cum, maychu = int(config.get("group", 1)), int(config.get("server", 1))
            except (TypeError, ValueError):
                print(f"❌ Lỗi: cụm / máy chủ '{config.get('group')}' / '{config.get('server')}' không hợp lệ!")
                return False
            if not dn.chonmaychu(cum, maychu):
                return False
            # Client mở bằng mã từ launcher (chế độ đăng nhập khác 0) thì nút xác nhận máy chủ tự kết nối, không qua màn nhập tài khoản
            menu = dn.chomenu(("MENUDANGNHAP", "MENUCHONNHANVAT"), 5.)
            if menu is None:
                print("   -> [Hàm] Bấm xác nhận máy chủ mà không sang màn nhập tài khoản")
                return False
        if menu == "MENUDANGNHAP":
            dn.nhaptaikhoan(config["user"], config["pass"])
            print("   -> [Hàm] Chờ danh sách nhân vật...")
            if dn.chomenu(("MENUCHONNHANVAT",), THOIGIANCHODANHSACHNHANVAT) is None:
                print(f"   -> [Hàm] {THOIGIANCHODANHSACHNHANVAT:.0f}s chưa sang màn chọn nhân vật (sai mật khẩu / tài khoản đang online / mất mạng?)")
                return False
        return dn.chonhoactaoga(config) if config.get("taoga") else dn.chonvavaogame(config)
    except Exception as e:
        print(f"❌ [Hàm] Lỗi đăng nhập bằng hàm: {e}")
        return False
    finally:
        dn.dong()


def dangnhaptrongcuaso(hwnd_game, char_name, config):
    # Từ màn hình chọn cụm / máy chủ (cửa sổ mới mở, hoặc cửa sổ bị dis quay về) tới khi vào game
    try:
        vitri = config.get("vitricuaso", 1)
        dichuyencuasotheovitri(hwnd_game, vitri)

        if IS_DANGNHAPBANGHAM:
            ketqua = _dangnhapbangham(hwnd_game, char_name, config)
            if config.get("taoga"):
                # Kéo gà A-Z: chọn / tạo nhân vật chỉ làm được bằng hàm, không lùi về cách bấm phím (sẽ vào nhầm ô 1)
                config["taoga"].setdefault("ketqua", {})["hwnd"] = hwnd_game
                if ketqua is None:
                    config["taoga"]["ketqua"]["loitao"] = True
                    return
            if ketqua is not None:
                if ketqua:
                    _thoidiemvaogame[hwnd_game] = time.time()
                    print(f"✅ Hoàn tất cho {char_name}. Nghỉ 15s...")
                    time.sleep(15)
                return

        time.sleep(2)

        group_name = config.get("group")
        server_index = config.get("server", 1)

        if group_name in TOADO_CUMMAYCHU:
            print(f"   -> Chọn cụm {group_name}")
            gx, gy = TOADO_CUMMAYCHU[group_name]
            click(hwnd_game, gx, gy)
            time.sleep(0.2)

        try:
            idx = int(server_index)
            if idx in TOADO_MAYCHU:
                print(f"   -> Chọn server thứ {idx}")
                sx, sy = TOADO_MAYCHU[idx]
                click(hwnd_game, sx, sy)
                time.sleep(0.2)
                bx, by = TOADO_GAME["BTN_XACNHAN_SERVER"]
                click(hwnd_game, bx, by)
                # Chuyển sang màn nhập tài khoản gần như tức thì, chỉ chờ ngắn để ô nhập kịp hiện
                time.sleep(0.5)
            else:
                print(f"⚠️ Không có tọa độ cho server index {idx}")
        except ValueError:
            print(f"❌ Lỗi: Server index '{server_index}' không hợp lệ!")
            return

        print("   -> Nhập Tài khoản & Mật khẩu...")
        press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)
        for _ in range(30):
            press_key(hwnd_game, win32con.VK_BACK, delay = 0.01)
        time.sleep(0.5)

        type_text(hwnd_game, config["user"])
        time.sleep(0.5)
        press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)
        type_text(hwnd_game, config["pass"])
        time.sleep(0.5)
        press_key(hwnd_game, win32con.VK_RETURN)

        print("   -> Chờ load nhân vật (2.5s)...")
        time.sleep(2.5)

        char_idx = config.get("char_index", 1)

        if char_idx >= 2:
            cx, cy = TOADO_CHONNHANVAT.get(char_idx)
            click(hwnd_game, cx, cy)
            time.sleep(1)
        else:
            print("   -> Chọn nhân vật số 1 (Mặc định)")

        press_key(hwnd_game, win32con.VK_RETURN)
        time.sleep(1)
        press_key(hwnd_game, win32con.VK_RETURN)
        _thoidiemvaogame[hwnd_game] = time.time()

        print(f"✅ Hoàn tất cho {char_name}. Nghỉ 15s...")

        time.sleep(15)

    except Exception as e:
        print(f"❌ Exception: {e}")


def dondeptientrinhaovuabithoatgame(tuoitoithieu = TUOIXQAOTOITHIEU):
    valid_pids = set()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if is_tieudecuasogame(title):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                valid_pids.add(pid)

    win32gui.EnumWindows(callback, None)

    # Chỉ dọn xq.exe của bản game tự đăng nhập quản lý: bản khác (mở tay) cũng tên xq.exe, có thể đang ở màn hình có tiêu đề
    # lạ (đăng nhập, chọn máy chủ...) mà không phải tiến trình ảo
    duongdans = _duongdangamequanlys()
    ghost_pids = {pid for pid in _laypidxq() - valid_pids
                  if _laytuoitientrinh(pid) >= tuoitoithieu and _layduongdantientrinh(pid) in duongdans}

    if ghost_pids:
        print(f"[CLEANUP] Đang kiểm tra các tiến trình xq.exe bị treo ngầm...")

        pid_dakills = []
        for pid in ghost_pids:
            print(f"   ⚠️ Phát hiện xq.exe ảo (PID: {pid}). Đang tiến hành kill...")
            try:
                if _killtientrinh(pid):
                    pid_dakills.append(pid)
                    print(f"   ✅ Đã đóng thành công xq.exe ảo (PID: {pid}).")
            except Exception as e:
                print(f"   ❌ Lỗi khi kill PID {pid}: {e}")

        if pid_dakills:
            chotientrinhthoat(pid_dakills)


def donglauncher(hwnd_launcher):
    # Launcher bị đơ không vào được game: đóng nhẹ trước, không được thì kill tiến trình rồi chờ thoát hẳn
    if not hwnd_launcher or not win32gui.IsWindow(hwnd_launcher):
        return
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd_launcher)
    except pywintypes.error:
        return
    try:
        if not _dongcuaso(hwnd_launcher):
            return
    except pywintypes.error:
        pass
    for _ in range(10):
        time.sleep(0.5)
        if not win32gui.IsWindow(hwnd_launcher):
            break
    else:
        print(f"   ⚠️ Launcher không tự đóng (PID: {pid}). Đang kill...")
        if not _killtientrinh(pid):
            return
    chotientrinhthoat([pid])
    print(f"   ✅ Đã đóng launcher (PID: {pid}).")


def _laypidxq(is_dunghoathuong = False):
    # is_dunghoathuong: chỉ tiến trình tên đúng "xq.exe" chữ thường, đúng như kiểm tra số client của game (so từng byte). File exe
    # Aegis đổi thành "XQ.exe" thì client Aegis không bị Niết Bàn (và chính Aegis) đếm
    xq_pids = set()
    try:
        output = subprocess.check_output(
            ['tasklist', '/FI', 'IMAGENAME eq xq.exe', '/FO', 'CSV', '/NH']
        ).decode('utf-8', errors = 'ignore')
        for row in csv.reader(output.splitlines()):
            if len(row) > 1 and (row[0] == 'xq.exe' if is_dunghoathuong else 'xq.exe' in row[0].lower()):
                xq_pids.add(int(row[1]))
    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách tiến trình: {e}")
    return xq_pids


def _layduongdantientrinh(pid):
    # Đường dẫn exe của tiến trình (đã chuẩn hoá để so sánh), None khi không đọc được
    try:
        handle = win32api.OpenProcess(0x0410, False, pid)  # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
        try:
            return os.path.normcase(os.path.abspath(win32process.GetModuleFileNameEx(handle, 0)))
        finally:
            win32api.CloseHandle(handle)
    except Exception:
        return None


def _laytuoitientrinh(pid):
    try:
        handle = win32api.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        try:
            return time.time() - win32process.GetProcessTimes(handle)["CreationTime"].timestamp()
        finally:
            win32api.CloseHandle(handle)
    except Exception:
        return 0.


def dondepclientkhongdangnhap(tuoitoithieu = 120., cuasogiuchos = ()):
    # Client vừa bị dis vẫn còn cửa sổ "Chien Quoc 2D..." nên không bị coi là tiến trình ảo, nhưng vẫn chiếm suất
    # => game báo "You can not run more client program!". Kill các client không có nhân vật đang đăng nhập.
    # Bỏ qua client mới mở (< tuoitoithieu giây) vì có thể đang đăng nhập dở.
    pid_dangnhaps = set()
    pid_cuasogames = set()
    duongdans = _duongdangamequanlys()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and is_tieudecuasogame(win32gui.GetWindowText(hwnd)) and _is_cuasoquanly(hwnd, duongdans):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pid_cuasogames.add(pid)
            # Cửa sổ bị dis đang giữ chỗ: coi như đang đăng nhập, không kill
            if hwnd in cuasogiuchos or _is_cuasodadangnhap(hwnd):
                pid_dangnhaps.add(pid)

    win32gui.EnumWindows(callback, None)

    pid_cankills = [pid for pid in pid_cuasogames - pid_dangnhaps if _laytuoitientrinh(pid) >= tuoitoithieu]
    pid_dakills = []
    for pid in pid_cankills:
        print(f"   ⚠️ Client không còn nhân vật đăng nhập (bị dis?) (PID: {pid}). Đang kill...")
        if _killtientrinh(pid):
            pid_dakills.append(pid)
    if pid_dakills:
        chotientrinhthoat(pid_dakills)


def giaiphongchoclient(cuasogiuchos = (), gioihan = SOCLIENTTOIDA):
    # Trước khi mở client mới: đã đủ gioihan tiến trình game đếm (tên đúng "xq.exe", mọi bản) thì kill client không có nhân vật
    # (cửa sổ chờ, cửa sổ bị dis đã hết lượt thử...), trừ cửa sổ bị dis đang giữ chỗ. Chỉ kill cửa sổ của bản tự đăng nhập quản lý
    # mà game có đếm, bản khác chỉ chiếm suất. Không cần tuổi tối thiểu như dondepclientkhongdangnhap vì đằng nào cũng phải mở mới.
    # Trả về False khi không giải phóng được chỗ (mở thêm sẽ thành client thứ gioihan + 1)
    pidtheocuasos = {}
    duongdans = _duongdangamequanlys()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and is_tieudecuasogame(win32gui.GetWindowText(hwnd)) and _is_cuasoquanly(hwnd, duongdans):
            pidtheocuasos[hwnd] = win32process.GetWindowThreadProcessId(hwnd)[1]

    win32gui.EnumWindows(callback, None)

    pid_demduocs = _laypidxq(is_dunghoathuong = True)
    pids = set(pidtheocuasos.values()) & pid_demduocs
    socanbot = len(pid_demduocs) - gioihan + 1
    if socanbot <= 0:
        return True
    pid_dangnhaps = {pid for hwnd, pid in pidtheocuasos.items() if hwnd in cuasogiuchos or _is_cuasodadangnhap(hwnd)}
    pid_cankills = sorted(pids - pid_dangnhaps)[:socanbot]
    pid_dakills = []
    for pid in pid_cankills:
        print(f"   ⚠️ Đã đủ {gioihan} client, kill client không có nhân vật (PID: {pid}) để lấy chỗ...")
        if _killtientrinh(pid):
            pid_dakills.append(pid)
    if pid_dakills:
        chotientrinhthoat(pid_dakills)
    return len(pid_dakills) >= socanbot


def chotientrinhthoat(pids, thoigiantoida = 15.):
    # taskkill trả về ngay nhưng tiến trình cần một lúc mới thoát hẳn; mở xq.exe mới quá sớm vẫn bị tính quá số client
    pids = set(pids)
    hethan = time.time() + thoigiantoida
    while pids and time.time() < hethan:
        pids &= _laypidxq()
        if pids:
            time.sleep(0.5)
    time.sleep(1.)


def dichuyencuasotheovitri(hwnd, vitricuaso):
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    window_width = 810
    window_height = 630
    taskbar_height = 40

    index_goc = (vitricuaso - 1) % 5

    toa_do_4_goc = [
        (0, 0),                                                                       # 1: Trái Trên
        (screen_width - window_width, 0),                                             # 2: Phải Trên
        (0, screen_height - window_height - taskbar_height),                          # 3: Trái Dưới
        (screen_width - window_width, screen_height - window_height - taskbar_height),  # 4: Phải Dưới
        ((screen_width - window_width) // 2, (screen_height - window_height - taskbar_height) // 2)  # 5: Giữa màn hình
    ]

    toado_x, toado_y = toa_do_4_goc[index_goc]

    _bokieuan(hwnd)
    try:
        win32gui.SetWindowPos(
            hwnd,
            0,
            toado_x,
            toado_y,
            0,
            0,
            win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
        )
        print(f"   -> [GIAO DIỆN] Đã ghim cửa sổ vào vị trí số {vitricuaso}.")
    except Exception as e:
        print(f"   ❌ Lỗi khi di chuyển cửa sổ: {e}")


# Ẩn cửa sổ game: dời ra ngoài mọi màn hình + bỏ khỏi thanh taskbar / Alt+Tab (WS_EX_TOOLWINDOW). Không dùng SW_HIDE / thu nhỏ: bot
# tìm cửa sổ game bằng IsWindowVisible, PrintWindow không chụp được cửa sổ thu nhỏ. {hwnd: (x, y)} chỗ cũ để hiện lại
_vitritruockhian = {}


def _xbenngoaimanhinh():
    # Mép trái màn hình ảo (nhiều màn hình có thể âm) lùi thêm 1 khoảng xa hơn cả bề rộng cửa sổ game
    return win32api.GetSystemMetrics(76) - 4000


def is_cuasogamedaan(hwnd):
    try:
        return win32gui.GetWindowRect(hwnd)[2] <= _xbenngoaimanhinh() + 2000
    except Exception:
        return False


def _doikieutaskbar(hwnd, is_an, x, y):
    # Đổi WS_EX_TOOLWINDOW lúc cửa sổ đang hiện thì taskbar không cập nhật: ẩn thoáng qua, đổi kiểu + chỗ, hiện lại không kích hoạt
    kieu = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    kieu = (kieu | win32con.WS_EX_TOOLWINDOW) & ~win32con.WS_EX_APPWINDOW if is_an else kieu & ~win32con.WS_EX_TOOLWINDOW
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    try:
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, kieu)
        win32gui.SetWindowPos(hwnd, 0, x, y, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_FRAMECHANGED)
    finally:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)


def ancuasogame(hwnd):
    try:
        if not win32gui.IsWindow(hwnd) or is_cuasogamedaan(hwnd):
            return
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
        r = win32gui.GetWindowRect(hwnd)
        _vitritruockhian[hwnd] = r[0], r[1]
        _doikieutaskbar(hwnd, True, _xbenngoaimanhinh(), 0)
    except Exception as e:
        print(f"   ❌ Lỗi khi ẩn cửa sổ game: {e}")


def hiencuasogame(hwnd):
    # Không nhớ chỗ cũ (bot mở lại lúc game còn đang ẩn) thì đặt giữa màn hình
    try:
        if not win32gui.IsWindow(hwnd):
            _vitritruockhian.pop(hwnd, None)
            return
        vitri = _vitritruockhian.pop(hwnd, None)
        if vitri is None:
            if not is_cuasogamedaan(hwnd):
                return
            r = win32gui.GetWindowRect(hwnd)
            vitri = (win32api.GetSystemMetrics(0) - (r[2] - r[0])) // 2, (win32api.GetSystemMetrics(1) - 40 - (r[3] - r[1])) // 2
        _doikieutaskbar(hwnd, False, *vitri)
    except Exception as e:
        print(f"   ❌ Lỗi khi hiện cửa sổ game: {e}")


def focuscuasogame(hwnd):
    # Đưa cửa sổ game lên trước (bấm đúp trên danh sách nhân vật): thu nhỏ thì phục hồi. Giao diện đang là cửa sổ trước nên Windows
    # cho SetForegroundWindow; vẫn bị chặn thì nhấn Alt giả để mở khoá
    try:
        if not win32gui.IsWindow(hwnd):
            return
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"   ❌ Lỗi khi đưa cửa sổ game lên trước: {e}")


def _bokieuan(hwnd):
    # Đăng nhập (lại) cần cửa sổ trên màn hình và có lại nút taskbar; xong thì giao diện tự ẩn lại nếu đang bật Ẩn game
    _vitritruockhian.pop(hwnd, None)
    try:
        if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOOLWINDOW:
            _doikieutaskbar(hwnd, False, *win32gui.GetWindowRect(hwnd)[:2])
    except Exception:
        pass


def _is_cuasocuataikhoan(taikhoan, idnguoichoi, tennhanvat):
    # Cửa sổ (đã biết ID / tên nhân vật lúc còn online) có phải của tài khoản này: so ID, chưa điền ID thì so tên
    if taikhoan.get("idnguoichoi"):
        return idnguoichoi is not None and int(taikhoan["idnguoichoi"]) == idnguoichoi
    return bool(tennhanvat) and chuanhoatennhanvat(taikhoan.get("tennhanvat")) == tennhanvat


def _is_taikhoanonline(taikhoan, online):
    # Ưu tiên ID (cố định); chưa điền ID thì tạm so theo tên (tên có thể đổi). None = cấu hình thiếu cả hai
    idnguoichoi = taikhoan.get("idnguoichoi")
    tennhanvat = taikhoan.get("tennhanvat")
    if idnguoichoi:
        return int(idnguoichoi) in online["id"]
    if tennhanvat:
        return chuanhoatennhanvat(tennhanvat) in online["ten"]
    return None


class TuDongDangNhap:
    # Luồng nền trong tiến trình giao diện: bật/tắt từng tài khoản lưu vào file cấu hình ("maydangnhap"), giao diện đọc "trangthai"
    # để hiển thị. Máy này có ít nhất một tài khoản bật thì coi như đang bật tự đăng nhập
    def __init__(self):
        global is_chophepdong
        self.is_bat = bool(taikhoanbatchomaynay(taicauhinhdangnhap()))
        is_chophepdong = self.is_bat
        self.trangthai = "Đang tắt" if not self.is_bat else "Đang khởi động..."
        # [(tên, ID, "online"/"vắng"/"đang đăng nhập"/"tắt"...)] lần quét gần nhất, cùng thứ tự với mọi tài khoản trong file
        self.danhsach = []
        # hwnd -> ID nhân vật lần cuối thấy trong cửa sổ đó: cửa sổ bị dis về màn hình đăng nhập vẫn giữ chỗ (phó bản), đăng nhập lại
        # ngay trong nó thì vào lại tại chỗ, đóng cửa sổ là mất chỗ. hwnd -> số lần đã thử đăng nhập lại trong cửa sổ bị dis
        self._idtheocuaso = {}
        self._solandangnhaplaicuaso = {}
        # hwnd -> tên nhân vật (đã chuẩn hoá) lần cuối thấy trong cửa sổ đó: nhận ra cửa sổ bị dis của tài khoản chưa có ID
        self._tentheocuaso = {}
        # Tài khoản ("user") -> lúc bắt đầu vắng mà chưa đăng nhập lại được (báo Telegram khi vắng quá THOIGIANBAOVANG giây)
        self._batdauvang = {}
        # Theo dõi rớt game theo tài khoản ("user"): online lượt quét trước, [các lần rớt trong THOIGIANDEMBIDA giây], tạm hoãn tự
        # đăng nhập tới thời điểm này
        self._onlinetruoc = {}
        self._lanroigames = {}
        self._tamhoanden = {}
        # Kéo gà A-Z (keogatudong_xq.KeoGaTuDong, trochoi_xq gắn vào): chạy cùng luồng này sau mỗi lượt đăng nhập lại để hai bên không
        # cùng mở client; đang bật thì cũng được đóng / kill client (is_chophepdong)
        self.keoga = None
        self._luong = threading.Thread(target = self.loop, daemon = True)

    def batdau(self):
        self._luong.start()

    def _is_dangtamhoan(self, taikhoan):
        return time.time() < self._tamhoanden.get(taikhoan.get("user"), 0.)

    def _theodoiroigame(self, taikhoans, online):
        # Nhân vật đang online (lượt quét trước) mà giờ vắng: rớt mạng / bị đá (tài khoản đăng nhập ở máy khác) / game đóng -> báo
        # Telegram. Rớt SOLANBIDALIENTUC lần trong THOIGIANDEMBIDA giây thì gần như chắc có máy khác đang đăng nhập cùng tài khoản (vd chép
        # nhầm file tài khoản sang máy ảo, 2026-10-29 hai máy đá nhau cả buổi sáng): tạm hoãn tự đăng nhập tài khoản đó THOIGIANTAMHOAN
        # giây và báo, để hai máy thôi giành nhau
        import html
        from thongbao_xq import guitinmay
        now = time.time()
        for taikhoan in taikhoans:
            khoa = taikhoan.get("user")
            is_online = _is_taikhoanonline(taikhoan, online)
            if not khoa or is_online is None:
                continue
            if self._onlinetruoc.get(khoa) and not is_online:
                ten = html.escape(taikhoan.get("tennhanvat") or str(taikhoan.get("idnguoichoi") or khoa))
                lans =[t for t in self._lanroigames.get(khoa, []) if now - t < THOIGIANDEMBIDA] + [now]
                self._lanroigames[khoa] = lans
                if len(lans) >= SOLANBIDALIENTUC:
                    self._tamhoanden[khoa] = now + THOIGIANTAMHOAN
                    self._lanroigames[khoa] = []
                    print(f"[ĐĂNG NHẬP] {ten} rớt {len(lans)} lần trong {THOIGIANDEMBIDA // 60} phút: tạm hoãn tự đăng nhập {THOIGIANTAMHOAN // 60} phút")
                    guitinmay("dangnhap", f"🚫 <b>{ten}</b> bị đá khỏi game {len(lans)} lần trong {THOIGIANDEMBIDA // 60} phút\n"
                                          f"Có thể máy khác đang đăng nhập cùng tài khoản <b>{html.escape(khoa)}</b>. "
                                          f"Tạm hoãn tự đăng nhập tài khoản này {THOIGIANTAMHOAN // 60} phút.", khoa = ("bida", khoa), giancach = 600.)
                else:
                    guitinmay("dangnhap", f"⚠️ <b>{ten}</b> rớt khỏi game (mất kết nối, game đóng hoặc tài khoản bị đăng nhập ở nơi khác)"
                                          f"{(', đang tạm hoãn tự đăng nhập' if self._is_dangtamhoan(taikhoan) else ', đang tự đăng nhập lại') if self.is_bat else ''}",
                             khoa = ("roigame", khoa), giancach = 120.)
            self._onlinetruoc[khoa] = is_online

    def is_dangtamngung(self):
        # Đang tạm ngưng chung (ẩn thân / người lạ) hoặc có tài khoản đang tạm hoãn (bị đá liên tục): giao diện hiện nút "Tiếp tục"
        return bool(laytamngungdanghieuluc()) or any(t > time.time() for t in self._tamhoanden.values())

    def tieptuc(self):
        # Người dùng bấm "Tiếp tục": bỏ mọi tạm ngưng / tạm hoãn, đăng nhập lại ngay ở lượt quét sau. Đếm rớt game cũng tính lại từ đầu,
        # không thì rớt thêm một lần là tạm hoãn lại ngay
        for idnguoichoi, _, _ in laytamngungdanghieuluc():
            xoatamngung(idnguoichoi)
        self._tamhoanden.clear()
        self._lanroigames.clear()
        print("[ĐĂNG NHẬP] Người dùng bấm Tiếp tục: bỏ tạm ngưng / tạm hoãn, đăng nhập lại ngay")

    def _capnhatisbat(self, cauhinh):
        global is_chophepdong
        self.is_bat = bool(taikhoanbatchomaynay(cauhinh))
        is_chophepdong = self.is_bat or bool(self.keoga and self.keoga.is_bat)

    def set_is_battaikhoan(self, cauhinh, vitri, is_bat):
        # Bật cho máy này (dòng đang bật ở máy khác thì chuyển sang máy này) / tắt; lưu ngay vào file chung
        taikhoan = cauhinh["taikhoans"][vitri]
        taikhoan["maydangnhap"] = tenmaynay() if is_bat else ""
        luucauhinhdangnhap(cauhinh)
        self._capnhatisbat(cauhinh)
        print(f"[ĐĂNG NHẬP] {'Bật' if is_bat else 'Tắt'} tự đăng nhập {taikhoan.get('tennhanvat') or taikhoan.get('user')} trên máy {tenmaynay()}")

    def loop(self):
        while True:
            try:
                self._mot_luot()
            except Exception as e:
                self.trangthai = f"Lỗi: {e}"
                print(f"[ĐĂNG NHẬP] Lỗi vòng lặp: {e}")
            if self.keoga:
                global is_chophepdong
                is_chophepdong = self.is_bat or self.keoga.is_bat
                self.keoga.mot_luot()
            time.sleep(5)

    def _mot_luot(self):
        # Đọc file cả khi đang tắt để giao diện thấy danh sách tài khoản / lỗi file ngay sau khi sửa
        cauhinh = taicauhinhdangnhap()
        if cauhinh.get("loi"):
            self.trangthai = cauhinh["loi"]
            self.danhsach = []
            return
        self._capnhatisbat(cauhinh)

        def tinhtrangtat(taikhoan):
            return f"máy {taikhoan['maydangnhap']}" if taikhoan.get("maydangnhap") else "tắt"

        if not self.is_bat:
            self.trangthai = f"Đang tắt (chưa bật tài khoản nào cho máy {tenmaynay()})"
            self.danhsach = [(taikhoan.get("tennhanvat") or str(taikhoan.get("user")), taikhoan.get("idnguoichoi"), tinhtrangtat(taikhoan))
                             for taikhoan in cauhinh["taikhoans"]]
            return

        # Nhân vật nào đang tạm ngưng (ẩn thân / người lạ) thì không đăng nhập ai cả cho tới khi hết hạn
        tamngungs = laytamngungdanghieuluc()
        if tamngungs:
            idnguoichoi, thoidiemhet, lydo = tamngungs[0]
            conlai = int(thoidiemhet - time.time())
            self.trangthai = f"Tạm ngưng (ID {idnguoichoi}: {lydo}) – còn {conlai // 60}:{conlai % 60:02d}"
            return

        taikhoans = taikhoanbatchomaynay(cauhinh)

        dondeptientrinhaovuabithoatgame()
        online = laydanhsachnhanvatonlines()

        self._tudienid(cauhinh, online)

        # Cửa sổ đang có nhân vật: nhớ là của ai. Cửa sổ đã đóng thì quên
        for hwnd, idnguoichoi in online["cuaso"].items():
            self._idtheocuaso[hwnd] = idnguoichoi
            if online["tentheocuaso"].get(hwnd):
                self._tentheocuaso[hwnd] = online["tentheocuaso"][hwnd]
            self._solandangnhaplaicuaso.pop(hwnd, None)
        for hwnd in [h for h in self._idtheocuaso if not win32gui.IsWindow(h)]:
            self._idtheocuaso.pop(hwnd, None)
            self._tentheocuaso.pop(hwnd, None)
            self._solandangnhaplaicuaso.pop(hwnd, None)
        # Cửa sổ bị dis: đang ở màn hình đăng nhập, nhân vật của nó chưa online ở cửa sổ khác, chưa thử đăng nhập lại quá
        # SOLANDANGNHAPLAICUASODIS lần. Không đóng / kill, không nhận nhầm là cửa sổ mới mở
        cuasodis = {hwnd: idnguoichoi for hwnd, idnguoichoi in self._idtheocuaso.items()
                    if hwnd not in online["cuaso"] and idnguoichoi not in online["id"]
                    and self._solandangnhaplaicuaso.get(hwnd, 0) < SOLANDANGNHAPLAICUASODIS and _is_cuasomanhinhdangnhap(hwnd)}

        # Nhân vật vắng có cửa sổ bị dis được đăng nhập trước: dis cùng lúc nhiều acc mà lấy nhân vật đầu danh sách (cửa sổ của nó đã
        # hết lượt thử) thì phải mở client mới trong khi các cửa sổ bị dis khác vẫn chiếm đủ chỗ. Khớp cửa sổ theo ID, tài khoản chưa có
        # ID thì theo tên (trước đây chỉ theo ID: 4 tài khoản chưa điền ID bị dis cùng lúc thì không cửa sổ nào khớp, mở client mới
        # cũng không được vì cả 4 cửa sổ đang giữ chỗ -> kẹt mãi, 2026-10-29)
        def cuasodiscua(taikhoan):
            return next((hwnd for hwnd, idnguoichoi in cuasodis.items()
                         if _is_cuasocuataikhoan(taikhoan, idnguoichoi, self._tentheocuaso.get(hwnd))), None)

        self._theodoiroigame(taikhoans, online)
        # Tài khoản đang tạm hoãn (bị đá liên tục: máy khác đang đăng nhập cùng tài khoản) thì không đăng nhập lại, kẻo hai máy đá nhau mãi
        vangs = [taikhoan for taikhoan in taikhoans if _is_taikhoanonline(taikhoan, online) is False and not self._is_dangtamhoan(taikhoan)]
        self._baovanglau(taikhoans, online, vangs)
        canhdangnhap = next((taikhoan for taikhoan in vangs if cuasodiscua(taikhoan)), vangs[0] if vangs else None)
        danhsach = []
        for taikhoan in cauhinh["taikhoans"]:
            is_online = _is_taikhoanonline(taikhoan, online)
            ten = taikhoan.get("tennhanvat") or str(taikhoan.get("idnguoichoi") or taikhoan.get("user"))
            if not is_batchomaynay(taikhoan):
                # Tài khoản máy này không đăng nhập: vẫn báo online nếu đang có trên máy này (vd đăng nhập tay)
                danhsach.append((ten, taikhoan.get("idnguoichoi"), "online" if is_online else tinhtrangtat(taikhoan)))
            elif is_online is None:
                danhsach.append((ten, None, "thiếu ID/tên"))
            elif is_online is False and self._is_dangtamhoan(taikhoan):
                conlai = int(self._tamhoanden[taikhoan.get("user")] - time.time()) // 60 + 1
                danhsach.append((ten, taikhoan.get("idnguoichoi"), f"tạm hoãn {conlai} phút (bị đá liên tục)"))
            elif taikhoan is canhdangnhap:
                danhsach.append((ten, taikhoan.get("idnguoichoi"), "đang đăng nhập"))
            else:
                danhsach.append((ten, taikhoan.get("idnguoichoi"), "online" if is_online else "vắng"))
        self.danhsach = danhsach

        if canhdangnhap is None:
            self.trangthai = f"Đủ {sum(1 for taikhoan in taikhoans if _is_taikhoanonline(taikhoan, online))}/{len(taikhoans)} nhân vật online"
            return
        if laycuasodangvaogame():
            # Vừa bấm vào game, nhân vật chưa hiện (đang load bản đồ): chờ, không thì tưởng vắng mà đóng chính cửa sổ đó để đăng nhập lại
            self.trangthai = "Đang chờ nhân vật vừa đăng nhập vào game..."
            return

        ten = canhdangnhap.get("tennhanvat") or str(canhdangnhap.get("idnguoichoi"))
        hwnd_dis = cuasodiscua(canhdangnhap)
        if hwnd_dis:
            # Đăng nhập lại ngay trong cửa sổ bị dis: vào lại tại chỗ (phó bản), không về thành
            self._solandangnhaplaicuaso[hwnd_dis] = self._solandangnhaplaicuaso.get(hwnd_dis, 0) + 1
            self.trangthai = f"Đang đăng nhập lại {ten} trong cửa sổ bị dis..."
            print(f"\n[ĐĂNG NHẬP] {ten} bị dis, đăng nhập lại ngay trong cửa sổ cũ (HWND: {hwnd_dis}, lần {self._solandangnhaplaicuaso[hwnd_dis]})")
            dangnhaptrongcuaso(hwnd_dis, ten, canhdangnhap)
            return
        self.trangthai = f"Đang đăng nhập {ten}..."
        if mogamevadangnhap(ten, canhdangnhap, duongdangamecua(canhdangnhap, cauhinh), cuasogiuchos = set(cuasodis)) is False and cuasodis:
            # Đủ client mà chỗ nào cũng bị cửa sổ dis giữ (của nhân vật khác / không nhận ra của ai): bỏ giữ chỗ để lượt sau đóng được
            # một cửa sổ mà mở client mới, không thì kẹt mãi
            import html
            from thongbao_xq import guitinmay
            print(f"   -> Bỏ giữ chỗ {len(cuasodis)} cửa sổ bị dis để mở được client mới cho {ten}")
            for hwnd in cuasodis:
                self._solandangnhaplaicuaso[hwnd] = SOLANDANGNHAPLAICUASODIS
            guitinmay("dangnhap", f"⚠️ Đủ client đều là cửa sổ bị dis đang giữ chỗ, không mở thêm được để đăng nhập "
                                  f"<b>{html.escape(ten)}</b>: bỏ giữ chỗ, đóng bớt cửa sổ dis rồi mở client mới", khoa = "kethetcho", giancach = 600.)

    def _tudienid(self, cauhinh, online):
        # Tài khoản chưa điền ID mà nhân vật cùng tên đang online: ghi ID vào file tài khoản (ID cố định, tên có thể đổi; nhận cửa sổ bị
        # dis theo ID chắc hơn theo tên)
        tentheoid = {}
        for hwnd, idnguoichoi in online["cuaso"].items():
            if online["tentheocuaso"].get(hwnd):
                tentheoid[online["tentheocuaso"][hwnd]] = idnguoichoi
        dadien = []
        for taikhoan in cauhinh["taikhoans"]:
            ten = chuanhoatennhanvat(taikhoan.get("tennhanvat"))
            if not taikhoan.get("idnguoichoi") and ten in tentheoid:
                taikhoan["idnguoichoi"] = tentheoid[ten]
                dadien.append(f"{taikhoan.get('tennhanvat')} = {tentheoid[ten]}")
        if dadien:
            print(f"[ĐĂNG NHẬP] Tự điền ID vào {os.path.basename(duongdantaikhoan())}: {', '.join(dadien)}")
            luucauhinhdangnhap(cauhinh)

    def _baovanglau(self, taikhoans, online, vangs):
        # Nhân vật vắng quá THOIGIANBAOVANG giây mà vẫn chưa vào lại được: báo Telegram (30 phút nhắc lại 1 lần)
        import html
        from thongbao_xq import guitinmay
        now = time.time()
        khoavangs = {taikhoan.get("user") for taikhoan in vangs}
        for khoa in [k for k in self._batdauvang if k not in khoavangs]:
            self._batdauvang.pop(khoa)
        for taikhoan in vangs:
            khoa = taikhoan.get("user")
            batdau = self._batdauvang.setdefault(khoa, now)
            if now - batdau >= THOIGIANBAOVANG:
                ten = html.escape(taikhoan.get("tennhanvat") or str(taikhoan.get("idnguoichoi") or khoa))
                guitinmay("dangnhap", f"❗ <b>{ten}</b> vắng {int(now - batdau) // 60} phút mà tự đăng nhập chưa đưa vào lại được "
                                      f"({self.trangthai})", khoa = ("vanglau", khoa), giancach = 1800.)
