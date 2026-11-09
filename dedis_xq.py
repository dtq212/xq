# Đăng nhập ĐÈ lên nhân vật treo nhờ máy ảo (thử nghiệm 2026-11-10).
#
# Vấn đề: lag làm kết nối chết mà máy chủ không biết (cq_stability.log wsa=10060) -> nhân vật treo vẫn ở trên máy chủ. Máy chủ giới
# hạn 5 nhân vật MỖI MÁY nên đăng nhập lại báo "Full tài khoản", phải thoát oan một acc.
#
# Đo 2026-11-10 (Kng 359, tạo treo bằng luật firewall chặn 2 chiều cổng cục bộ):
#   - Còn nhân vật treo thì client mới trên máy chính cũng không vào được; client máy chính đi vòng qua IP máy ảo (relay TCP, kết nối
#     tới máy chủ đúng là từ IP máy ảo) VẪN không vào được => giới hạn không theo IP mà theo máy (chienquoc2d.dll xác thực máy qua
#     HTTPS lúc mở client, hook cả winsock). Đã bỏ cách relay.
#   - Máy chủ tự xoá nhân vật treo sau ~50-80s (thử ở giây 0/30/50 hỏng, giây 83 vào được).
#   - Người dùng làm tay: đăng nhập acc đó Ở MÁY ẢO thì vào được (đè lên nhân vật treo), rồi đăng nhập lại ở máy chính (đè lên máy ảo)
#     là xong, nhân vật không bị logout nên giữ chỗ.
#
# Cách làm (tự động hoá đúng thao tác tay đó):
#   1. Máy chính (cửa sổ bị dis, lần đăng nhập lại đầu không vào được) gửi "dangnhaptam" kèm tài khoản sang máy ảo qua card Host-only.
#   2. Máy ảo đủ 5 nhân vật thì đóng 1 acc của nó (ưu tiên "nhuongcho": true, không thì acc cuối danh sách) và tạm hoãn tự đăng nhập
#      acc đó; mở client mới đăng nhập acc của máy chính (đè lên nhân vật treo), trả lời khi đã vào game.
#   3. Máy chính đăng nhập lại trong cửa sổ cũ (máy chính giờ còn 4) -> đè lên phiên ở máy ảo.
#   4. Máy chính gửi "ketthuctam": máy ảo đóng client tạm đó, bỏ tạm hoãn acc vừa nhường để tự đăng nhập lại.
#
# Cấu hình trong _internal/lan.json (chung mọi máy): "nhuongcho": {"may": tên máy ảo, "diachi": IP Host-only dự phòng, "cong": cổng}.
# Máy có tên = "may" mở cổng điều khiển trên IP của nó cùng mạng /24 với máy chủ LAN (không mở ra mạng điện thoại). Kênh xác thực
# bằng "matkhau" của lan.json (multiprocessing.connection, HMAC; nội dung — có cả mật khẩu acc — không mã hoá, chỉ đi trên Host-only).
import json
import os
import socket
import subprocess
import threading
import time
from multiprocessing.connection import Client, Listener

from tienich_xq import _thumucthietlap, tenmaynay

# Máy ảo tạm hoãn tự đăng nhập acc vừa nhường chỗ tối đa chừng này giây (máy chính báo "ketthuctam" thì bỏ ngay)
THOIGIANTAMHOANNHUONGCHO = 600
# Đóng client acc nhường xong chờ chừng này giây cho máy chủ xoá nhân vật (đóng tiến trình -> Windows gửi FIN/RST, máy chủ biết ngay)
THOIGIANCHOMAYCHUXOA = 5.
# Máy ảo mở client + đăng nhập + chờ nhân vật vào game tối đa chừng này giây
THOIGIANDANGNHAPTAM = 120.
SONHANVATTOIDA = 5


def taicauhinhnhuongcho():
    # -> (cấu hình lan.json, mục "nhuongcho") hoặc (None, None) khi chưa cấu hình
    duongdan = os.path.join(os.path.dirname(_thumucthietlap()), "lan.json")
    try:
        with open(duongdan, encoding = "utf-8-sig") as file:
            cauhinh = json.load(file)
    except Exception:
        return None, None
    nhuongcho = cauhinh.get("nhuongcho")
    if not cauhinh.get("matkhau") or not cauhinh.get("diachi") or not isinstance(nhuongcho, dict) \
            or not all(nhuongcho.get(k) for k in ("may", "diachi", "cong")):
        return None, None
    return cauhinh, nhuongcho


def _diachicungmang(diachimaychu):
    # IP của máy này cùng mạng /24 với máy chủ LAN (card Host-only): VMware cấp IP động nên không ghi cứng (2026-11-10 máy ảo
    # Windows7Game nhận .131 trong khi lan.json ghi .128 của máy ảo khác)
    tiento = diachimaychu.rsplit(".", 1)[0] + "."
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip.startswith(tiento) and ip != diachimaychu:
                return ip
    except OSError:
        pass
    return None


def _kill(pid):
    # Đóng client bất kể đang tắt tự đăng nhập (dangnhap_xq._killtientrinh chặn khi tắt)
    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output = True)


# ------------------------------------------------------------------ Máy ảo

class MayNhuongCho:
    # Chạy ở máy ảo trong tiến trình chính (trochoi_xq), cần TuDongDangNhap của máy đó để tạm hoãn / bỏ tạm hoãn acc nhường chỗ
    def __init__(self, tudongdangnhap):
        self.tudongdangnhap = tudongdangnhap
        self.cauhinh, self.nhuongcho = taicauhinhnhuongcho()
        self._khoa = threading.Lock()

    def batdau(self):
        if not self.nhuongcho or self.nhuongcho["may"] != tenmaynay():
            return False
        diachi, cong = _diachicungmang(self.cauhinh["diachi"]) or self.nhuongcho["diachi"], int(self.nhuongcho["cong"])
        try:
            listener = Listener((diachi, cong), authkey = self.cauhinh["matkhau"].encode())
        except Exception as e:
            print(f"[ĐÈ DIS] Không mở được cổng nhường chỗ {diachi}:{cong}: {e}")
            return False
        threading.Thread(target = self._nhan, args = (listener,), daemon = True).start()
        print(f"[ĐÈ DIS] Nhận yêu cầu đăng nhập tạm ở {diachi}:{cong}")
        return True

    def _nhan(self, listener):
        while True:
            try:
                ketnoi = listener.accept()
            except Exception as e:
                # Sai mật khẩu (AuthenticationError) / kết nối hỏng: bỏ qua
                print(f"[ĐÈ DIS] Từ chối kết nối điều khiển: {e}")
                continue
            threading.Thread(target = self._phucvu, args = (ketnoi,), daemon = True).start()

    def _phucvu(self, ketnoi):
        try:
            yeucau = ketnoi.recv()
            with self._khoa:
                lenh = yeucau.get("lenh")
                if lenh == "dangnhaptam":
                    traloi = self._dangnhaptam(yeucau)
                elif lenh == "ketthuctam":
                    traloi = self._ketthuctam(yeucau)
                elif lenh == "thu":
                    traloi = {"ok": True}
                else:
                    traloi = {"ok": False, "loi": f"lệnh lạ {lenh}"}
            ketnoi.send(traloi)
        except Exception as e:
            print(f"[ĐÈ DIS] Lỗi xử lý yêu cầu: {e}")
        finally:
            ketnoi.close()

    def _nhuongcho(self, online, idcanvao):
        # Đóng 1 acc của máy này để còn chỗ. -> "user" acc đã đóng, None nếu không cần / không có acc nào đóng được
        import dangnhap_xq
        import win32process
        cauhinh = dangnhap_xq.taicauhinhdangnhap()
        # Lấy acc nào ở máy ảo cũng được (người dùng 2026-11-10): ưu tiên "nhuongcho": true, còn lại acc cuối danh sách (thứ tự trong
        # file = thứ tự ưu tiên đăng nhập)
        tks = sorted(reversed(dangnhap_xq.taikhoanbatchomaynay(cauhinh)), key = lambda tk: not tk.get("nhuongcho"))
        for tk in tks:
            hwnd = next((h for h, i in online["cuaso"].items()
                         if dangnhap_xq._is_cuasocuataikhoan(tk, i, online["tentheocuaso"].get(h))), None)
            if not hwnd or online["cuaso"][hwnd] == idcanvao or not tk.get("user"):
                continue
            ten = tk.get("tennhanvat") or tk.get("user")
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            # Tạm hoãn trước khi đóng: không thì lượt quét tự đăng nhập kế tiếp thấy vắng là đăng nhập lại chiếm chỗ ngay
            self.tudongdangnhap._tamhoanden[tk["user"]] = time.time() + THOIGIANTAMHOANNHUONGCHO
            print(f"[ĐÈ DIS] Nhường chỗ: đóng {ten} (PID {pid}), tạm hoãn tự đăng nhập tối đa {THOIGIANTAMHOANNHUONGCHO // 60} phút")
            _kill(pid)
            time.sleep(THOIGIANCHOMAYCHUXOA)
            return tk["user"]
        return None

    def _dangnhaptam(self, yeucau):
        import dangnhap_xq
        tk = yeucau["taikhoan"]
        idcanvao = int(tk["idnguoichoi"])
        ten = tk.get("tennhanvat") or str(idcanvao)
        online = dangnhap_xq.laydanhsachnhanvatonlines()
        if idcanvao in online["id"]:
            return {"ok": False, "loi": f"{ten} đang online ở máy này rồi"}
        usernhuong = None
        if len(online["cuaso"]) >= SONHANVATTOIDA:
            usernhuong = self._nhuongcho(online, idcanvao)
            if not usernhuong:
                return {"ok": False, "loi": f"máy {tenmaynay()} đủ {len(online['cuaso'])} nhân vật mà không đóng được acc nào"}
        print(f"\n[ĐÈ DIS] Máy chính nhờ đăng nhập tạm {ten} (ID {idcanvao}) để đè lên nhân vật treo")
        cauhinh = dangnhap_xq.taicauhinhdangnhap()
        hwnd, is_vao = None, False
        try:
            hwnd = dangnhap_xq.mogamevadangnhap(f"{ten} (tạm)", dict(tk, vitricuaso = 6), dangnhap_xq.duongdangamemaynay(cauhinh))
            hethan = time.time() + THOIGIANDANGNHAPTAM
            while hwnd and time.time() < hethan and not is_vao:
                time.sleep(2)
                is_vao = dangnhap_xq.laydanhsachnhanvatonlines()["cuaso"].get(hwnd) == idcanvao
        except Exception as e:
            print(f"❌ [ĐÈ DIS] Lỗi đăng nhập tạm {ten}: {e}")
        print(f"[ĐÈ DIS] Đăng nhập tạm {ten}: {'đã vào game' if is_vao else 'KHÔNG vào được'}")
        if not is_vao:
            self._dondep(hwnd, usernhuong)
            return {"ok": False, "loi": f"máy {tenmaynay()} đăng nhập {ten} không vào được"}
        return {"ok": True, "hwnd": hwnd, "usernhuong": usernhuong}

    def _dondep(self, hwnd, usernhuong):
        import win32gui
        import win32process
        if hwnd and win32gui.IsWindow(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            _kill(pid)
        if usernhuong:
            self.tudongdangnhap._tamhoanden.pop(usernhuong, None)

    def _ketthuctam(self, yeucau):
        # Máy chính đã đăng nhập lại (đè lên phiên ở đây) hoặc bỏ cuộc: đóng client tạm, trả chỗ cho acc vừa nhường
        self._dondep(yeucau.get("hwnd"), yeucau.get("usernhuong"))
        print(f"[ĐÈ DIS] Kết thúc đăng nhập tạm: đóng client tạm, "
              f"{'bỏ tạm hoãn ' + yeucau['usernhuong'] + ' để đăng nhập lại' if yeucau.get('usernhuong') else 'không có acc nhường'}")
        return {"ok": True}


# ------------------------------------------------------------------ Máy chính

def _diachimayaos(cauhinh, nhuongcho):
    # Các IP có thể là máy ảo: IP đang nối vào LAN hub (máy chính là máy chủ LAN, cổng lan.json "cong") rồi tới IP ghi trong "nhuongcho"
    ips = []
    try:
        import diettreo_xq
        for trangthai, ip, cong, ipxa, _, _ in diettreo_xq.laybangtcp():
            if trangthai == 5 and cong == int(cauhinh["cong"]) and ipxa not in ips:
                ips.append(ipxa)
    except Exception:
        pass
    if nhuongcho["diachi"] not in ips:
        ips.append(nhuongcho["diachi"])
    return ips


def _guiyeucau(yeucau, thoigianchotraloi = 30.):
    cauhinh, nhuongcho = taicauhinhnhuongcho()
    if not nhuongcho:
        return None
    ketnoi, lois = None, []
    for ip in _diachimayaos(cauhinh, nhuongcho):
        try:
            # Client không có timeout: thử cổng trước cho nhanh, IP sai thì bỏ sau 3s
            socket.create_connection((ip, int(nhuongcho["cong"])), timeout = 3).close()
            ketnoi = Client((ip, int(nhuongcho["cong"])), authkey = cauhinh["matkhau"].encode())
            break
        except Exception as e:
            lois.append(f"{ip}: {e}")
    if not ketnoi:
        return {"ok": False, "loi": f"không nối được máy {nhuongcho['may']} ({'; '.join(lois)})"}
    try:
        ketnoi.send(yeucau)
        if not ketnoi.poll(thoigianchotraloi):
            return {"ok": False, "loi": f"máy {nhuongcho['may']} không trả lời sau {thoigianchotraloi:.0f}s"}
        return ketnoi.recv()
    except Exception as e:
        return {"ok": False, "loi": f"lỗi kênh điều khiển: {e}"}
    finally:
        ketnoi.close()


def is_codedis():
    # Máy này có thể nhờ máy khác đăng nhập tạm (đã cấu hình và máy này không phải máy ảo đó)
    _, nhuongcho = taicauhinhnhuongcho()
    return bool(nhuongcho) and nhuongcho["may"] != tenmaynay()


def dangnhaptam(taikhoan):
    # Nhờ máy ảo đăng nhập tài khoản này (đè lên nhân vật treo). -> {"ok", "hwnd", "usernhuong"} / {"ok": False, "loi"}, None nếu chưa
    # cấu hình. Chỉ gửi các trường cần để đăng nhập
    tk = {k: taikhoan.get(k) for k in ("tennhanvat", "idnguoichoi", "user", "pass", "group", "server", "char_index")}
    return _guiyeucau({"lenh": "dangnhaptam", "taikhoan": tk}, thoigianchotraloi = 60 + THOIGIANDANGNHAPTAM)


def ketthuctam(traloi):
    return _guiyeucau({"lenh": "ketthuctam", "hwnd": traloi.get("hwnd"), "usernhuong": traloi.get("usernhuong")})
