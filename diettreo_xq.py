# Diệt nhân vật treo trên máy chủ sau khi bị dis (thử nghiệm 2026-11-10, chưa test trong game lúc viết).
#
# Vấn đề: lag làm kết nối TCP chết (cq_stability.log "recv_error wsa=10060"), máy chủ không nhận được FIN/RST nên vẫn giữ nhân vật
# trong game. Nhân vật treo chiếm chỗ: đủ 5 nhân vật thì đăng nhập lại báo "Game đã full", phải thoát oan một acc khác.
#
# Cách làm (cơ chế phát hiện kết nối nửa mở của TCP): mở kết nối mới tới máy chủ TỪ ĐÚNG CỔNG CỤC BỘ của kết nối đã chết. Máy chủ nhận
# SYN trên cặp (IP, cổng) nó tưởng vẫn đang mở thì trả ACK "hỏi lại" (challenge ACK, ack = số thứ tự nó đang chờ); Windows bên mình
# không còn kết nối đó nên đáp RST với seq = đúng số đó -> máy chủ chấp nhận RST, huỷ kết nối cũ, xoá nhân vật treo. Windows gửi lại
# SYN sau ~1-3s, lúc này máy chủ không còn kết nối cũ nên bắt tay bình thường -> connect thành công, đóng ngay (không gửi gì).
# Điều kiện: router giữ nguyên cổng NAT cho kết nối mới từ cùng cổng cục bộ (đa số router gia đình làm vậy khi cổng còn trống) và IP
# công cộng không đổi sau lag.
#
# Cổng của từng nhân vật ghi lúc còn online (TuDongDangNhap._mot_luot gọi capnhatketnoi mỗi lượt 5s), khoá theo ID người chơi, lưu
# _internal/ketnoigame.json để bot khởi động lại vẫn còn. Chạy tay: python -X utf8 diettreo_xq.py [ID] (không ID: in danh sách cổng)

import ctypes
import ctypes.wintypes
import json
import os
import socket
import sys
import threading
import time

# Kết nối game: mọi client nối tới máy chủ cổng này (đăng nhập lẫn trong game, đo 2026-11-10: 103.92.26.138:8888). Lọc theo cổng để
# không lấy nhầm kết nối HTTPS xác thực của chienquoc2d.dll
CONGMAYCHUGAME = 8888
# Chờ connect tối đa: RST diệt kết nối cũ đi ngay, SYN gửi lại sau 1-3s mới bắt tay được
THOIGIANCHOKETNOI = 6.
# Cổng ghi quá lâu (nhân vật không online lại) thì bỏ: cổng có thể đã thuộc kết nối khác, máy chủ cũng đã tự xoá nhân vật
THOIGIANGIUCONG = 6 * 3600

_MIB_TCP_STATE_ESTAB = 5
_TCP_TABLE_OWNER_PID_ALL = 5
_AF_INET = 2

_khoa = threading.Lock()
_ketnois = None  # {str(ID): {"ip": ..., "cong": ..., "ipmaychu": ..., "congmaychu": ..., "luc": ...}}


class _MIB_TCPROW_OWNER_PID(ctypes.Structure):
    _fields_ = [("dwState", ctypes.wintypes.DWORD), ("dwLocalAddr", ctypes.wintypes.DWORD), ("dwLocalPort", ctypes.wintypes.DWORD),
                ("dwRemoteAddr", ctypes.wintypes.DWORD), ("dwRemotePort", ctypes.wintypes.DWORD), ("dwOwningPid", ctypes.wintypes.DWORD)]


def _duongdan():
    # Không dùng os.getcwd(): bot mở từ chỗ khác thì thư mục làm việc là System32 (2026-11-10 file bị ghi vào đó)
    from tienich_xq import _thumucthietlap
    return os.path.join(os.path.dirname(_thumucthietlap()), "ketnoigame.json")


def _tai():
    global _ketnois
    if _ketnois is None:
        try:
            with open(_duongdan(), "r", encoding = "utf-8") as file:
                _ketnois = json.load(file)
        except Exception:
            _ketnois = {}
    return _ketnois


def _luu():
    try:
        filetam = _duongdan() + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(_ketnois, file, ensure_ascii = False, indent = 1)
        os.replace(filetam, _duongdan())
    except Exception as e:
        print(f"[DIỆT TREO] Không lưu được {_duongdan()}: {e}")


def _ip(dword):
    return socket.inet_ntoa(dword.to_bytes(4, "little"))


def _cong(dword):
    return socket.ntohs(dword & 0xFFFF)


def laybangtcp():
    # Mọi kết nối TCP IPv4: [(trạng thái, ip, cổng, ip xa, cổng xa, pid)] (GetExtendedTcpTable, không cần psutil)
    iphlpapi = ctypes.windll.iphlpapi
    kichthuoc = ctypes.wintypes.DWORD(0)
    iphlpapi.GetExtendedTcpTable(None, ctypes.byref(kichthuoc), False, _AF_INET, _TCP_TABLE_OWNER_PID_ALL, 0)
    for _ in range(3):
        bodem = ctypes.create_string_buffer(kichthuoc.value + 4096)
        kichthuoc = ctypes.wintypes.DWORD(len(bodem))
        if iphlpapi.GetExtendedTcpTable(bodem, ctypes.byref(kichthuoc), False, _AF_INET, _TCP_TABLE_OWNER_PID_ALL, 0) == 0:
            break
    else:
        return []
    soluong = ctypes.cast(bodem, ctypes.POINTER(ctypes.wintypes.DWORD))[0]
    hangs = ctypes.cast(ctypes.addressof(bodem) + 4, ctypes.POINTER(_MIB_TCPROW_OWNER_PID * soluong)).contents
    return [(h.dwState, _ip(h.dwLocalAddr), _cong(h.dwLocalPort), _ip(h.dwRemoteAddr), _cong(h.dwRemotePort), h.dwOwningPid) for h in hangs]


def capnhatketnoi(cuasos):
    # cuasos: {hwnd: ID người chơi} các cửa sổ đang có nhân vật. Ghi cổng cục bộ kết nối game của từng nhân vật; chỉ lưu file khi đổi
    import win32process
    try:
        bang = laybangtcp()
    except Exception as e:
        print(f"[DIỆT TREO] Không đọc được bảng TCP: {e}")
        return
    ketnoitheopid = {}
    for trangthai, ip, cong, ipxa, congxa, pid in bang:
        if trangthai == _MIB_TCP_STATE_ESTAB and congxa == CONGMAYCHUGAME:
            ketnoitheopid[pid] = (ip, cong, ipxa, congxa)
    with _khoa:
        ketnois = _tai()
        is_doi = False
        bayGio = time.time()
        for hwnd, idnguoichoi in cuasos.items():
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
            except Exception:
                continue
            ketnoi = ketnoitheopid.get(pid)
            if not ketnoi:
                continue
            khoa = str(int(idnguoichoi))
            cu = ketnois.get(khoa)
            moi = {"ip": ketnoi[0], "cong": ketnoi[1], "ipmaychu": ketnoi[2], "congmaychu": ketnoi[3], "luc": bayGio}
            if not cu or (cu["ip"], cu["cong"], cu["ipmaychu"], cu["congmaychu"]) != ketnoi or bayGio - cu.get("luc", 0) > 600:
                ketnois[khoa] = moi
                is_doi = True
        for khoa in [k for k, v in ketnois.items() if bayGio - v.get("luc", 0) > THOIGIANGIUCONG]:
            ketnois.pop(khoa)
            is_doi = True
        if is_doi:
            _luu()


def diettreo(idnguoichoi, inlog = print):
    # Gọi trước khi đăng nhập lại nhân vật vừa vắng. Trả về chuỗi kết quả (để log), None nếu không có cổng ghi trước / cổng đang dùng.
    # Cổng đã thử thì xoá khỏi danh sách: thử lại lần sau vô ích (máy chủ đã nhận RST, hoặc NAT đã đổi cổng)
    if not idnguoichoi:
        return None
    khoa = str(int(idnguoichoi))
    with _khoa:
        ketnoi = _tai().pop(khoa, None)
        if ketnoi:
            _luu()
    if not ketnoi:
        return None
    try:
        dangdung = any(cong == ketnoi["cong"] and trangthai == _MIB_TCP_STATE_ESTAB for trangthai, ip, cong, _, _, _ in laybangtcp())
    except Exception:
        dangdung = False
    if dangdung:
        inlog(f"[DIỆT TREO] ID {khoa}: cổng {ketnoi['cong']} đang có kết nối khác dùng, bỏ qua")
        return None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    batdau = time.time()
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ketnoi["ip"], ketnoi["cong"]))
        s.settimeout(THOIGIANCHOKETNOI)
        maloi = s.connect_ex((ketnoi["ipmaychu"], ketnoi["congmaychu"]))
        # Đóng kiểu abort (RST) để máy chủ không giữ kết nối thừa chờ LOGIN
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, (1).to_bytes(2, "little") + (0).to_bytes(2, "little"))
    except OSError as e:
        maloi = e.errno or e.winerror
    finally:
        try:
            s.close()
        except Exception:
            pass
    ketqua = (f"ID {khoa}: gửi SYN từ {ketnoi['ip']}:{ketnoi['cong']} tới {ketnoi['ipmaychu']}:{ketnoi['congmaychu']} -> "
              f"{'bắt tay được' if maloi == 0 else f'mã {maloi}'} sau {time.time() - batdau:.1f}s "
              f"(cổng ghi lúc {time.strftime('%H:%M:%S', time.localtime(ketnoi['luc']))})")
    inlog(f"[DIỆT TREO] {ketqua}")
    return ketqua


def diettreokhongcho(idnguoichoi):
    # Chạy diettreo ở luồng riêng, không chặn người gọi
    threading.Thread(target = diettreo, args = (idnguoichoi,), daemon = True).start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(diettreo(sys.argv[1]) or "Không có cổng ghi trước cho ID này (hoặc cổng đang được dùng)")
    else:
        for khoa, v in _tai().items():
            print(f"ID {khoa}: {v['ip']}:{v['cong']} -> {v['ipmaychu']}:{v['congmaychu']} lúc {time.strftime('%d/%m %H:%M:%S', time.localtime(v['luc']))}")
