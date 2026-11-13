# Gọi A* bản C (astar_xq.c -> astar_xq.dll) qua ctypes. Không có DLL / DLL lệch phiên bản / lỗi nạp thì is_cosan() = False và
# MoiTruong._timduongkhongcatgoc chạy bản Python như cũ (máy khác chưa build DLL vẫn chạy bình thường).
#
# ctypes là thư viện chuẩn của Python để gọi hàm trong DLL: khai báo kiểu tham số (argtypes) / kiểu trả về (restype) cho đúng với
# chữ ký hàm C, rồi truyền bộ đệm (bytes / mảng ctypes) vào. Không cần biên dịch gì thêm phía Python.
import ctypes
import os
import sys

from dexuatlotrinh_xq import HUONGTIMDUONG_MAP

PHIENBAN = 1  # phải khớp astar_phienban() trong astar_xq.c

# 0 trong lưới client là đi được, khác 0 là vật cản => byte 1 / 0 cho C (bytes.translate chạy trong C, nhanh hơn vòng lặp Python)
_BANGDOI = bytes([1] + [0] * 255)

_dll = None
_loinap = None


def _duongdandll():
    # Bản đóng gói (PyInstaller) để DLL trong thư mục chạy; chạy từ mã nguồn thì DLL nằm cạnh file này
    thumuc = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumuc, "astar_xq.dll")


def _nap():
    global _dll, _loinap
    if _dll is not None or _loinap is not None:
        return _dll
    try:
        dll = ctypes.CDLL(_duongdandll())
        dll.astar_phienban.restype = ctypes.c_int
        if dll.astar_phienban() != PHIENBAN:
            raise RuntimeError(f"DLL phiên bản {dll.astar_phienban()}, cần {PHIENBAN}: chạy lại build_astar.bat")
        dll.astar_timduong.restype = ctypes.c_int
        dll.astar_timduong.argtypes = [
            ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,  # trong, phat, rong, cao
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,  # x1, y1, x2, y2
            ctypes.c_double, ctypes.c_int,  # nguong, chocatgoc
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p,  # dxs, dys, kytus
            ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int),  # ra, tranhtoida, somo
        ]
        _dll = dll
    except Exception as e:
        _loinap = e
    return _dll


def is_cosan():
    return _nap() is not None


def get_loinap():
    # Lý do không dùng được DLL (để log 1 lần), None nếu đang dùng được
    _nap()
    return _loinap


_kytus = "".join(HUONGTIMDUONG_MAP.keys()).encode()
_dxs = (ctypes.c_int * 8)(*[dx for dx, _ in HUONGTIMDUONG_MAP.values()])
_dys = (ctypes.c_int * 8)(*[dy for _, dy in HUONGTIMDUONG_MAP.values()])


def doi_luoi(luoi):
    # luoi[x][y] (list các list, 0 đi được) -> bytes trong[x * cao + y] (1 đi được) cho C
    return b"".join(bytes(cot) for cot in luoi).translate(_BANGDOI)


def timduong(trong, rong, cao, x1, y1, x2, y2, nguong = 0., is_chocatgoc = False, phats = None):
    # trong: bytes / bytearray từ doi_luoi (đã trừ ô vật cản ghi tay). Toạ độ là toạ độ TRONG lưới (đã trừ gốc khung).
    # phats: {(x, y): chi phí cộng thêm khi bước vào ô} hoặc None.
    # -> (chuỗi hướng bytes hoặc None, số ô đã mở)
    dll = _nap()
    phat = None
    if phats:
        phat = (ctypes.c_double * (rong * cao))()
        for (x, y), v in phats.items():
            if 0 <= x < rong and 0 <= y < cao:
                phat[x * cao + y] += v
    ra = ctypes.create_string_buffer(rong * cao + 1)
    somo = ctypes.c_int(0)
    n = dll.astar_timduong(bytes(trong), phat, rong, cao, x1, y1, x2, y2, float(nguong), 1 if is_chocatgoc else 0,
                           _dxs, _dys, _kytus, ra, rong * cao, ctypes.byref(somo))
    if n < 0:
        raise MemoryError(f"astar_timduong lỗi {n}")
    return (ra.raw[:n] if n > 0 else None), somo.value
