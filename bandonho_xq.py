import ctypes
import ctypes.wintypes
import math
import time
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from hangso_xq import (LOAIMUCTIEU_NGUOICHOICUNGNHOM, TRANPHAPVANMONGCOCs, NUACANHTRANVANMONGCOCs, MAHIEUUNGDATLACANHs, laytenbando)
from chude_xq import doithanhtieude
from tienich_xq import taivatcanhoc

# Bản đồ nhỏ (người dùng muốn 2026-11-14): cửa sổ Tk riêng ngoài game vẽ quanh nhân vật đang chọn: lưới vật cản, quái / người chơi / NPC,
# mục tiêu, trận pháp trên đất (cả Kỳ Môn / Độn Giáp đã bỏ vẽ trong game), đường A* bot đang đi, điểm lộ trình sắp tới.
# Không đụng phần vẽ của game nên không thêm rủi ro văng client.
# Bot chỉ gom dữ liệu khi giao diện bật (lệnh "set_bandonho:1"), gửi qua shared_data[hwnd]["_bandonho"] mỗi lượt cập nhật giao diện (0,25s).

# Nửa cạnh vùng lưới vật cản gửi lên (ô). Tầm thấy đối tượng ~18 ô (KHOANGCACHTOANMANHINH) => ±30 ô dư để thấy địa hình quanh đó.
# 61 x 61 ô = 3,7 KB mỗi lượt
BANKINHLUOIBANDONHO = 30
# Lưới đọc lại khi nhân vật đi xa tâm vùng đã đọc quá chừng này ô, hoặc sau THOIGIANDOCLAILUOI giây (mỗi lần đọc 61 lần đọc bộ nhớ)
NGUONGDOCLAILUOI = 10
THOIGIANDOCLAILUOI = 15.


class ThuThapBanDoNho:
    # Phía bot (tiến trình cửa sổ game): gom dữ liệu cho cửa sổ bản đồ nhỏ
    def __init__(self, moitruong, tactu):
        self.moitruong = moitruong
        self.tactu = tactu
        self.is_bat = False
        # (id bản đồ, ox, oy, rộng, cao, bytes theo cột x: luoi[(x-ox)*cao + (y-oy)] = 1 vật cản, lúc đọc)
        self._luoi = None

    def _layluoi(self, idbando, x, y):
        nho = self._luoi
        bayh = time.time()
        if nho and nho[0] == idbando and bayh - nho[6] < THOIGIANDOCLAILUOI \
                and abs(x - (nho[1] + BANKINHLUOIBANDONHO)) <= NGUONGDOCLAILUOI and abs(y - (nho[2] + BANKINHLUOIBANDONHO)) <= NGUONGDOCLAILUOI:
            return nho[:6]
        ox, oy = x - BANKINHLUOIBANDONHO, y - BANKINHLUOIBANDONHO
        luoi = self.moitruong.get_luoivatcanvung(ox, oy, x + BANKINHLUOIBANDONHO, y + BANKINHLUOIBANDONHO)
        if not luoi:
            return nho[:6] if nho and nho[0] == idbando else None
        rong, cao = len(luoi), len(luoi[0])
        self._luoi = (idbando, ox, oy, rong, cao, bytes(1 if o else 0 for cot in luoi for o in cot), bayh)
        return self._luoi[:6]

    def _laydoituongs(self, x, y):
        # [(x, y, loại, tên, id)], loại: quai / thudich (người chơi, bảo thú có thể đánh mình) / nguoichoi / dongdoi / npc / baothu
        mt = self.moitruong
        idbanthan = mt.get_iddoituong()
        tenchunhanphe_map = {}
        ketqua = []
        _, banchup = mt._get_banchupdoituongxungquanh()
        for diachi, dx, dy in banchup:
            if abs(dx - x) > BANKINHLUOIBANDONHO or abs(dy - y) > BANKINHLUOIBANDONHO:
                continue
            try:
                iddoituong = mt.get_iddoituong(diachi)
                if iddoituong == idbanthan or mt.get_is_nhanvatdachet(diachi):
                    continue
                if mt.get_is_npc(diachi):
                    loai = "npc"
                elif mt.get_is_quai(diachi):
                    loai = "quai"
                elif mt.get_is_nguoichoi(diachi):
                    if mt.get_idloainhanvat(diachi) == LOAIMUCTIEU_NGUOICHOICUNGNHOM:
                        loai = "dongdoi"
                    elif self.tactu._is_doituongthudich(diachi, tenchunhanphe_map):
                        loai = "thudich"
                    else:
                        loai = "nguoichoi"
                else:
                    loai = "thudich" if self.tactu._is_doituongthudich(diachi, tenchunhanphe_map) else "baothu"
                ketqua.append((dx, dy, loai, mt.get_tendoituong(diachi) or "", iddoituong))
            except Exception:
                continue
        return ketqua

    def _laytrans(self):
        # Trận trên mặt đất [(x, y, tên, nửa cạnh ô vuông)]: Vân Mộng Cốc (cả nút chưa tra được mã) + Lạc Ảnh Đào Hoa
        trans = []
        try:
            nuts = [nut for nut in self.moitruong.get_danhsachhieuungdat() if nut["co"] != 1]
        except Exception:
            return trans
        dalacanh = set()
        for nut in nuts:
            ma = nut["ma"]
            if ma is None or ma in TRANPHAPVANMONGCOCs:
                trans.append((nut["x"], nut["y"], TRANPHAPVANMONGCOCs.get(ma, "Trận chưa rõ"), NUACANHTRANVANMONGCOCs.get(ma, 2)))
            elif ma in MAHIEUUNGDATLACANHs and (nut["x"], nut["y"]) not in dalacanh:
                dalacanh.add((nut["x"], nut["y"]))
                trans.append((nut["x"], nut["y"], "Lạc Ảnh", 2))
        return trans

    def _layduong(self, x, y):
        # Đường A* bot đang cho client đi (action_dikhongcatgoc), bỏ phần đã đi qua. Đi bằng tìm đường của game thì không có
        mt = self.moitruong
        diem = mt._duongkhongcatgoc
        if not diem or not mt.get_idlenhdichuyen():
            return [], None
        i = min(range(len(diem)), key = lambda k: max(abs(diem[k][0] - x), abs(diem[k][1] - y)))
        return [tuple(d) for d in diem[i:]], mt._dichkhongcatgoc

    def lay(self, diemden = None):
        # -> dict cho shared_data, None khi chưa bật / chưa có nhân vật. diemden: [x, y, id bản đồ, ...] điểm lộ trình đang tới
        if not self.is_bat:
            return None
        mt = self.moitruong
        if not mt.get_is_nhanvattontai():
            return None
        idbando = mt.get_idbandohientai()
        fx, fy = mt.get_toado()
        x, y = round(fx), round(fy)
        luoi = self._layluoi(idbando, x, y)
        duong, dich = self._layduong(x, y)
        hocs = []
        if luoi:
            _, ox, oy, rong, cao, _ = luoi
            hocs = [o for o in taivatcanhoc(idbando) if ox <= o[0] < ox + rong and oy <= o[1] < oy + cao]
        return {
            "thoidiem": time.time(),
            "bando": idbando,
            "x": fx,
            "y": fy,
            "luoi": luoi,
            "hoc": hocs,
            "doituongs": self._laydoituongs(x, y),
            "muctieu": mt.get_iddoituongmuctieudangchon() or 0,
            "trans": self._laytrans(),
            "duong": duong,
            "dich": tuple(dich) if dich else None,
            "diemden": tuple(diemden[:2]) if diemden and len(diemden) >= 3 and diemden[2] == idbando else None,
        }


# ---------------------------------------------------------------------------------------------------------------------------------------
# Phía giao diện

# Khung bản đồ dùng bảng màu tối riêng kiểu radar (người dùng chê bản nền trắng "phèn" 2026-11-14), không theo sáng / tối của giao diện:
# nền tối thì chấm màu và chữ nổi hơn. Thanh công cụ, chú thích bên ngoài vẫn theo chủ đề.
MAUBANDO = {
    "vatcan": "#0b1118",       # ô vật cản bên trong
    "vatcanmep": "#2c3d50",    # ô vật cản giáp đất đi được: viền địa hình
    "dat": "#223245",          # đất đi được
    "datmep": "#1b2838",      # đất sát vật cản: tối hơn chút cho có chiều sâu
    "hoc": "#5a3d22",          # vật cản ghi tay (vatcanhoc.json)
    "luoike": "#26364a",       # kẻ ô mỗi 10 ô
    "chu": "#e2e8f0",
    "chuphu": "#94a3b8",
    "vienchu": "#05080c",
    "hop": "#0f172a",
    "hopvien": "#334155",
    "banthan": "#f8fafc",
    "banthanvong": "#22d3ee",
    "muctieu": "#ff4d5e",
    "duong": "#22d3ee",
    "diemden": "#fbbf24",
    "tamnhin": "#3b5068",
}
MAUDOITUONG = {"quai": "#f59e0b", "thudich": "#ff4d5e", "nguoichoi": "#cbd5e1", "dongdoi": "#4ade80", "npc": "#60a5fa", "baothu": "#8b9bb0"}
TENLOAIDOITUONG = {"quai": "Quái", "thudich": "Thù địch", "nguoichoi": "Người chơi", "dongdoi": "Đồng đội", "npc": "NPC", "baothu": "Bảo thú"}
MAUTRAN = {"Kỳ Môn Trận": "#facc15", "Độn Giáp Trận": "#a78bfa", "Lạc Ảnh": "#f472b6"}
# Thứ tự ưu tiên giữ tên khi chồng nhau (nhỏ giữ trước); quái không ghi tên
UUTIENTEN = {"thudich": 0, "dongdoi": 1, "nguoichoi": 2, "npc": 3, "baothu": 4, "quai": 5}
# Tên quái chỉ giữ chừng này ký tự (người dùng muốn 2026-11-14): quái đông, tên dài thì rối; tên chồng nhau vẫn bị bỏ như tên khác
DODAITENQUAI = 10
# Số điểm ảnh mỗi ô: mặc định / nhỏ nhất / lớn nhất
COOMACDINH, COOTOITHIEU, COOTOIDA = 8, 4, 16
KICHTHUOCKHUNG = 488
CHUKYVE = 250
# Mặc định mép dưới cửa sổ bản đồ cao hơn mép dưới game chừng này điểm ảnh (người dùng muốn thấp hơn game "chút xíu xiu")
BOTCAOBANDONHO = 12
# Vòng tầm nhìn (ô vuông như tầm đánh): đối tượng xa hơn chừng này bot không thấy
TAMNHINBANDONHO = 18
PHONGCHU = ("Segoe UI", 8)
PHONGCHUDAM = ("Segoe UI Semibold", 9)


class CuaSoBanDoNho:
    # Một cửa sổ cho cả giao diện: chọn nhân vật trong ô chọn, đổi nhân vật thì tắt gom dữ liệu ở bot cũ, bật ở bot mới
    def __init__(self, giaodien):
        self.gd = giaodien
        self.hwnd = None
        self.coo = COOMACDINH
        # Ảnh lưới vật cản dựng lại khi lưới / cỡ ô đổi: (khoá, PhotoImage)
        self._anhluoi = (None, None)
        self._dulieu = None
        self._henve = None
        self._lenhcho = {}
        # Chỉ đặt cỡ / vị trí theo cửa sổ game lần đầu có nhân vật; sau đó người dùng kéo cỡ thì giữ
        self._dadatco = False

        self.top = tk.Toplevel(giaodien.root)
        self.top.title("Bản đồ nhỏ")
        self.top.configure(background = self._mau("nen"))
        self.top.protocol("WM_DELETE_WINDOW", self.dong)
        self.top.after(0, lambda: doithanhtieude(self.top, getattr(giaodien, "is_chedotoi", False)))
        self._maunen = None
        self._phongchu = tkfont.Font(family = PHONGCHU[0], size = PHONGCHU[1])
        self._phongchudam = tkfont.Font(family = PHONGCHUDAM[0], size = PHONGCHUDAM[1])

        # Hai hàng: cửa sổ hẹp thì các ô tích không bị cắt mất
        thanh = ttk.Frame(self.top, padding = (8, 6, 8, 2))
        thanh.pack(side = tk.TOP, fill = tk.X)
        ttk.Label(thanh, text = "Nhân vật:").pack(side = tk.LEFT)
        self.cbo = ttk.Combobox(thanh, state = "readonly", width = 22)
        self.cbo.pack(side = tk.LEFT, padx = (4, 8), fill = tk.X, expand = True)
        self.cbo.bind("<<ComboboxSelected>>", lambda e: self._chonnhanvat(self._hwndtheonhan.get(self.cbo.get())))
        self.cbo.bind("<Button-1>", lambda e: self._napdanhsach())
        ttk.Button(thanh, text = "+", width = 3, command = lambda: self._doico(2)).pack(side = tk.RIGHT)
        ttk.Button(thanh, text = "−", width = 3, command = lambda: self._doico(-2)).pack(side = tk.RIGHT, padx = (0, 2))
        thanh2 = ttk.Frame(self.top, padding = (8, 0, 8, 6))
        thanh2.pack(side = tk.TOP, fill = tk.X)
        self.var_ten = tk.BooleanVar(value = True)
        self.var_duong = tk.BooleanVar(value = True)
        ttk.Checkbutton(thanh2, text = "Tên", variable = self.var_ten, command = self._ve).pack(side = tk.LEFT)
        ttk.Checkbutton(thanh2, text = "Đường đi", variable = self.var_duong, command = self._ve).pack(side = tk.LEFT, padx = (10, 0))
        # Tự đổi sang nhân vật của cửa sổ game đang mở (người dùng muốn 2026-11-14); chọn tay trong ô Nhân vật vẫn được khi tắt ô này
        self.var_theoactive = tk.BooleanVar(value = True)
        ttk.Checkbutton(thanh2, text = "Theo cửa sổ game", variable = self.var_theoactive).pack(side = tk.LEFT, padx = (10, 0))

        self.canvas = tk.Canvas(self.top, width = KICHTHUOCKHUNG, height = KICHTHUOCKHUNG, highlightthickness = 1,
                                highlightbackground = MAUBANDO["hopvien"], background = MAUBANDO["vatcan"])
        self.canvas.bind("<Configure>", lambda e: (self._ve(), self._vechuthich()))
        self.canvas.bind("<Motion>", self._rechuot)
        self.canvas.bind("<Leave>", lambda e: self.lbl_chuot.configure(text = ""))
        self.canvas.bind("<MouseWheel>", lambda e: self._doico(1 if e.delta > 0 else -1))

        duoi = ttk.Frame(self.top, padding = (8, 4, 8, 2))
        duoi.pack(side = tk.BOTTOM, fill = tk.X)
        self.lbl_trangthai = ttk.Label(duoi, text = "", style = "Phu.TLabel")
        self.lbl_trangthai.pack(side = tk.LEFT)
        self.lbl_chuot = ttk.Label(duoi, text = "", style = "Phu.TLabel")
        self.lbl_chuot.pack(side = tk.RIGHT)
        self.chuthich = tk.Canvas(self.top, height = 22, highlightthickness = 0, background = self._mau("nen"))
        self.chuthich.pack(side = tk.BOTTOM, fill = tk.X, padx = 8, pady = (0, 8), before = duoi)
        # Khung vẽ xếp sau cùng: cửa sổ thấp thì khung co lại, dòng trạng thái và chú thích bên dưới không bị cắt
        self.canvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True, padx = 8)

        self._hwndtheonhan = {}
        self._napdanhsach()
        self._chonnhanvat(giaodien.get_selected_hwnd())
        self._capnhat()

    # --- tiện ích -----------------------------------------------------------------------------------------------------------------
    def _mau(self, khoa):
        return khoa if khoa.startswith("#") else self.gd._mau.get(khoa, "#888888")

    def _layinfo(self, hwnd):
        try:
            return self.gd.shared_data.get(hwnd) or {}
        except Exception:
            return {}

    def _guilenh(self, hwnd, lenh, solan = 0):
        # Ô lệnh mỗi cửa sổ chỉ chứa 1 lệnh: còn lệnh khác chưa xử lý thì chờ rồi gửi, khỏi đè mất lệnh của giao diện
        if not hwnd:
            return
        try:
            if self.gd.command_dict.get(hwnd) and solan < 10:
                self.top.after(150, lambda: self._guilenh(hwnd, lenh, solan + 1))
                return
            self.gd.command_dict[hwnd] = lenh
        except Exception:
            pass

    def _napdanhsach(self):
        self._hwndtheonhan = {}
        try:
            danhsach = list(self.gd.shared_data.items())
        except Exception:
            danhsach = []
        for hwnd, info in danhsach:
            if isinstance(info, dict) and info.get("tennhanvat"):
                self._hwndtheonhan[f"{info['tennhanvat']} ({info.get('idnguoichoi', '?')})"] = hwnd
        self.cbo.configure(values = list(self._hwndtheonhan))

    def _chonnhanvat(self, hwnd):
        if hwnd == self.hwnd or not hwnd:
            return
        if self.hwnd:
            self._guilenh(self.hwnd, "set_bandonho:0")
        self.hwnd = hwnd
        self._datcotheogame(hwnd)
        self._dulieu = None
        self._guilenh(hwnd, "set_bandonho:1")
        for nhan, h in self._hwndtheonhan.items():
            if h == hwnd:
                self.cbo.set(nhan)
        self._ve()

    def _datcotheogame(self, hwnd):
        # Mặc định cao bằng cửa sổ game (người dùng muốn 2026-11-14), mép trên ngang mép trên game,
        # đặt sát bên phải game nếu màn hình còn chỗ, không thì giữ chỗ Tk tự chọn. Hwnd khoá shared_data chính là hwnd cửa sổ game
        if self._dadatco or not hwnd:
            return
        try:
            khung, trong = ctypes.wintypes.RECT(), ctypes.wintypes.RECT()
            if not ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(khung)) \
                    or not ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(trong)) or trong.bottom < 200:
                return
        except Exception:
            return
        self._dadatco = True
        self.top.update_idletasks()
        # Chiều cao Tk là phần trong (không gồm thanh tiêu đề) nên lấy phần trong của game: hai cửa sổ cùng kiểu khung thì mép ngoài bằng nhau
        cao = trong.bottom
        rong = self.top.winfo_reqwidth()
        vitri = ""
        if khung.right + rong + 16 <= self.top.winfo_screenwidth():
            vitri = f"+{khung.right}+{max(0, khung.top)}"
        # Đặt ngay khi cửa sổ chưa hiện thì Windows tự xếp chồng lại (đo: ra +52+52): đặt thêm lần nữa sau khi cửa sổ đã hiện
        hinh = f"{rong}x{max(300, cao)}{vitri}"
        self.top.geometry(hinh)
        self.top.after(150, lambda: (self.top.geometry(hinh), self.top.after(100, lambda: self._canhmeptheogame(hwnd))))

    @staticmethod
    def _khungnhinthay(hwnd):
        # Mép cửa sổ nhìn thấy (DWMWA_EXTENDED_FRAME_BOUNDS = 9): GetWindowRect gồm cả viền kéo cỡ vô hình ~7px của cửa sổ kéo được cỡ
        k = ctypes.wintypes.RECT()
        if ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(k), ctypes.sizeof(k)) != 0:
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(k))
        return k

    def _canhmeptheogame(self, hwnd):
        # Cửa sổ game không kéo cỡ được, khung khác cửa sổ Tk nên lấy chiều cao phần trong thì mép dưới vẫn lệch (người dùng thấy cao hơn,
        # 2026-11-14): canh mép trên / dưới nhìn thấy cho khớp game, rồi bớt thêm BOTCAOBANDONHO điểm ảnh cho thấp hơn chút
        try:
            game = self._khungnhinthay(hwnd)
            minh = self._khungnhinthay(ctypes.windll.user32.GetParent(self.top.winfo_id()))
            lechtren = game.top - minh.top
            lechduoi = (game.bottom - BOTCAOBANDONHO) - minh.bottom
            if lechtren == 0 and lechduoi == 0:
                return
            cao = max(300, self.top.winfo_height() + lechduoi - lechtren)
            self.top.geometry(f"{self.top.winfo_width()}x{cao}+{self.top.winfo_x()}+{self.top.winfo_y() + lechtren}")
        except Exception:
            pass

    def _doico(self, buoc):
        self.coo = max(COOTOITHIEU, min(COOTOIDA, self.coo + buoc))
        self._ve()

    def dong(self):
        if self._henve:
            self.top.after_cancel(self._henve)
        if self.hwnd:
            try:
                self.gd.command_dict[self.hwnd] = "set_bandonho:0"
            except Exception:
                pass
        self.gd._bandonho = None
        self.top.destroy()

    def hienlen(self):
        self.top.deiconify()
        self.top.lift()

    # --- vòng cập nhật ---------------------------------------------------------------------------------------------------------------
    def _theocuasoactive(self):
        # Cửa sổ game đang ở trên cùng (cùng cách bot nhận biết: get_is_cuasogamekichhoat) là nhân vật có bot thì vẽ nhân vật đó.
        # Đang ở cửa sổ khác (bản đồ nhỏ, giao diện, trình duyệt...) thì giữ nhân vật đang vẽ. Chỉ lấy danh sách khoá (hwnd), không chép info
        if not self.var_theoactive.get():
            return
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd or hwnd == self.hwnd or hwnd not in self.gd.shared_data.keys():
                return
        except Exception:
            return
        if hwnd not in self._hwndtheonhan.values():
            self._napdanhsach()
        self._chonnhanvat(hwnd)

    def _capnhat(self):
        self._theocuasoactive()
        info = self._layinfo(self.hwnd)
        self._dulieu = info.get("_bandonho")
        # Đổi sáng / tối ở giao diện chính: vẽ lại chú thích, nền
        if self._maunen != self._mau("nen"):
            self._maunen = self._mau("nen")
            self.top.configure(background = self._maunen)
            self.chuthich.configure(background = self._maunen)
            self._vechuthich()
        if not self.cbo.get() and info.get("tennhanvat"):
            self._napdanhsach()
            self._chonnhanvat_nhan()
        self._ve()
        self._henve = self.top.after(CHUKYVE, self._capnhat)

    def _chonnhanvat_nhan(self):
        for nhan, h in self._hwndtheonhan.items():
            if h == self.hwnd:
                self.cbo.set(nhan)

    # --- vẽ --------------------------------------------------------------------------------------------------------------------------------
    def _toado(self, x, y):
        # Ô game -> điểm ảnh trên khung. Bắc (y+) lên trên, Đông (x+) sang phải; nhân vật ở giữa khung
        d = self._dulieu
        rong, cao = self.canvas.winfo_width(), self.canvas.winfo_height()
        return rong / 2 + (x - d["x"]) * self.coo, cao / 2 - (y - d["y"]) * self.coo

    def _oduoichuot(self, px, py):
        d = self._dulieu
        rong, cao = self.canvas.winfo_width(), self.canvas.winfo_height()
        return round(d["x"] + (px - rong / 2) / self.coo), round(d["y"] - (py - cao / 2) / self.coo)

    def _dunganhluoi(self, luoi, hocs):
        # PhotoImage 1 điểm ảnh / ô rồi phóng lên self.coo: ~4.000 ô vẽ bằng hình chữ nhật thì khung ì.
        # Ô vật cản giáp đất tô sáng làm viền, đất giáp vật cản tô tối: địa hình có khối thay vì ô xám phẳng
        idbando, ox, oy, rong, cao, dulieu = luoi
        khoa = (idbando, ox, oy, rong, cao, dulieu, tuple(hocs), self.coo)
        if self._anhluoi[0] == khoa:
            return self._anhluoi[1]
        m = MAUBANDO
        tapphoc = set(hocs)

        def is_chan(x, y):
            # Ngoài vùng đã đọc coi như vật cản
            if x < ox or y < oy or x >= ox + rong or y >= oy + cao:
                return True
            return bool(dulieu[(x - ox) * cao + (y - oy)])

        hangs = []
        for y in range(oy + cao - 1, oy - 1, -1):
            hang = []
            for x in range(ox, ox + rong):
                if (x, y) in tapphoc:
                    hang.append(m["hoc"])
                    continue
                chan = is_chan(x, y)
                giap = any(is_chan(x + a, y + b) != chan for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if chan:
                    hang.append(m["vatcanmep"] if giap else m["vatcan"])
                else:
                    hang.append(m["datmep"] if giap else m["dat"])
            hangs.append("{" + " ".join(hang) + "}")
        anh = tk.PhotoImage(width = rong, height = cao)
        anh.put(" ".join(hangs))
        anh = anh.zoom(self.coo)
        self._anhluoi = (khoa, anh)
        return anh

    def _hopbo(self, x1, y1, x2, y2, r = 6, **kw):
        # Hình chữ nhật bo góc (polygon smooth)
        c = self.canvas
        diem = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return c.create_polygon(diem, smooth = True, **kw)

    def _chuvien(self, x, y, chu, mau, anchor = tk.CENTER, font = PHONGCHU):
        # Chữ có viền tối 1 điểm ảnh: đọc được trên cả đất lẫn vật cản
        c = self.canvas
        for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            c.create_text(x + a, y + b, text = chu, anchor = anchor, fill = MAUBANDO["vienchu"], font = font)
        c.create_text(x, y, text = chu, anchor = anchor, fill = mau, font = font)

    def _ve(self):
        c = self.canvas
        c.delete("all")
        m = MAUBANDO
        d = self._dulieu
        rong, cao = c.winfo_width(), c.winfo_height()
        if not d:
            c.create_text(rong / 2, cao / 2, text = "Đang chờ dữ liệu từ bot…" if self.hwnd else "Chọn nhân vật",
                          fill = m["chuphu"], font = PHONGCHUDAM)
            self.lbl_trangthai.configure(text = "")
            return
        s = self.coo

        # Lưới vật cản
        if d.get("luoi"):
            _, ox, oy, rongl, caol, _ = d["luoi"]
            anh = self._dunganhluoi(d["luoi"], d.get("hoc") or ())
            trai, tren = self._toado(ox, oy + caol - 1)
            c.create_image(trai - s / 2, tren - s / 2, image = anh, anchor = tk.NW)

        # Kẻ ô mỗi 10 ô theo toạ độ game (dễ ước khoảng cách), mờ
        x0, y0 = self._oduoichuot(0, 0)
        x1, y1 = self._oduoichuot(rong, cao)
        for gx in range((x0 // 10) * 10, x1 + 1, 10):
            px = self._toado(gx, 0)[0] - s / 2
            c.create_line(px, 0, px, cao, fill = m["luoike"], dash = (1, 3))
        for gy in range((y1 // 10) * 10, y0 + 1, 10):
            py = self._toado(0, gy)[1] + s / 2
            c.create_line(0, py, rong, py, fill = m["luoike"], dash = (1, 3))

        # Vùng tầm nhìn: ô vuông đứt nét quanh nhân vật
        mx, my = rong / 2, cao / 2
        t = TAMNHINBANDONHO * s + s / 2
        c.create_rectangle(mx - t, my - t, mx + t, my + t, outline = m["tamnhin"], dash = (6, 4))

        # Trận pháp: ô vuông (tầm trận tính theo ô vuông như tầm đánh)
        for tx, ty, ten, nuacanh in d.get("trans") or ():
            mau = MAUTRAN.get(ten, m["chuphu"])
            xa, ya = self._toado(tx - nuacanh, ty + nuacanh)
            xb, yb = self._toado(tx + nuacanh, ty - nuacanh)
            c.create_rectangle(xa - s / 2, ya - s / 2, xb + s / 2, yb + s / 2, outline = mau, width = 2, fill = mau, stipple = "gray12")
            cx, cy = self._toado(tx, ty)
            c.create_line(cx - s / 2, cy, cx + s / 2, cy, fill = mau)
            c.create_line(cx, cy - s / 2, cx, cy + s / 2, fill = mau)

        # Đường đi bot đang chạy + đích + điểm lộ trình đang tới
        if self.var_duong.get():
            duong = d.get("duong") or ()
            if len(duong) >= 2:
                diem = [v for o in duong for v in self._toado(*o)]
                c.create_line(*diem, fill = m["duong"], width = 2, dash = (5, 3), capstyle = tk.ROUND, joinstyle = tk.ROUND)
            if d.get("dich"):
                dx, dy = self._toado(*d["dich"])
                r = max(4, s * 0.6)
                c.create_oval(dx - r, dy - r, dx + r, dy + r, outline = m["duong"], width = 2)
                c.create_oval(dx - 1.5, dy - 1.5, dx + 1.5, dy + 1.5, fill = m["duong"], outline = "")
            if d.get("diemden"):
                ex, ey = self._toado(*d["diemden"])
                r = max(5, s * 0.8)
                c.create_polygon(ex, ey - r, ex + r, ey, ex, ey + r, ex - r, ey, outline = m["diemden"], fill = "", width = 2)

        # Đối tượng: chấm có viền tối; tên gom lại vẽ sau cùng để nằm trên mọi chấm
        idmuctieu = d.get("muctieu") or 0
        r = max(2.5, s * 0.42)
        dems = {}
        tens = []
        for ox_, oy_, loai, ten, iddoituong in d.get("doituongs") or ():
            dems[loai] = dems.get(loai, 0) + 1
            px, py = self._toado(ox_, oy_)
            if px < -s or py < -s or px > rong + s or py > cao + s:
                continue
            mau = MAUDOITUONG.get(loai, m["chuphu"])
            rr = r * 1.25 if loai in ("thudich", "nguoichoi", "dongdoi") else r
            c.create_oval(px - rr, py - rr, px + rr, py + rr, fill = mau, outline = m["vienchu"], width = 1)
            if iddoituong == idmuctieu:
                # Khung ngắm 4 góc quanh mục tiêu
                k, l = rr + 4, max(3, rr * 0.8)
                for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    c.create_line(px + sx * k, py + sy * (k - l), px + sx * k, py + sy * k, px + sx * (k - l), py + sy * k,
                                  fill = m["muctieu"], width = 2)
            if self.var_ten.get() and loai in UUTIENTEN and ten and s >= 6:
                ten = ten.split("(")[0].strip()
                if loai == "quai" and len(ten) > DODAITENQUAI:
                    ten = ten[:DODAITENQUAI].rstrip() + "…"
                tens.append((UUTIENTEN[loai], px, py, rr, ten[:16], mau))

        # Tên: trên chấm, chồng tên đã vẽ thì thử dưới chấm, vẫn chồng thì bỏ (ưu tiên thù địch > đồng đội > người chơi > NPC)
        dave = []
        caochu = self._phongchu.metrics("linespace")
        tenquai = []
        for uutien, px, py, rr, ten, mau in sorted(tens, key = lambda t: t[0]):
            # Quái cùng tên đứng gần (≤ 5 ô) chỉ ghi tên một lần: bầy quái cùng loại khỏi lặp chữ
            if uutien == UUTIENTEN["quai"]:
                if any(t == ten and abs(qx - px) <= 5 * s and abs(qy - py) <= 5 * s for t, qx, qy in tenquai):
                    continue
                tenquai.append((ten, px, py))
            w = self._phongchu.measure(ten)
            for day in (py - rr - 2, py + rr + 2 + caochu):
                hop = (px - w / 2 - 2, day - caochu, px + w / 2 + 2, day)
                if not any(hop[0] < b[2] and b[0] < hop[2] and hop[1] < b[3] and b[1] < hop[3] for b in dave):
                    dave.append(hop)
                    self._chuvien(px, day, ten, mau, anchor = tk.S)
                    break

        # Bản thân: chấm trắng có vòng xanh ở giữa (không có hướng mặt nên không vẽ mũi tên)
        rb = max(4, s * 0.55)
        c.create_oval(mx - rb - 4, my - rb - 4, mx + rb + 4, my + rb + 4, outline = m["banthanvong"], width = 1, dash = (2, 2))
        c.create_oval(mx - rb, my - rb, mx + rb, my + rb, fill = m["banthan"], outline = m["banthanvong"], width = 2)

        # Nhãn bản đồ + toạ độ góc trên trái
        tuoi = time.time() - d.get("thoidiem", 0)
        nhan = f"{laytenbando(d['bando'])}   {round(d['x'])}, {round(d['y'])}"
        w = self._phongchudam.measure(nhan) + 20
        self._hopbo(8, 8, 8 + w, 30, r = 8, fill = m["hop"], outline = m["hopvien"])
        c.create_text(18, 19, text = nhan, anchor = tk.W, fill = m["chu"], font = PHONGCHUDAM)
        if tuoi > 3:
            self._hopbo(8, 34, 150, 54, r = 8, fill = m["hop"], outline = m["muctieu"])
            c.create_text(18, 44, text = f"Dữ liệu cũ {tuoi:.0f}s", anchor = tk.W, fill = m["muctieu"], font = PHONGCHU)

        # La bàn góc trên phải: Bắc lên trên
        lx, ly = rong - 22, 22
        c.create_oval(lx - 13, ly - 13, lx + 13, ly + 13, fill = m["hop"], outline = m["hopvien"])
        c.create_polygon(lx, ly - 10, lx + 4, ly, lx - 4, ly, fill = m["muctieu"], outline = "")
        c.create_polygon(lx, ly + 10, lx + 4, ly, lx - 4, ly, fill = m["chuphu"], outline = "")
        c.create_text(lx, ly + 22, text = "B", fill = m["chuphu"], font = PHONGCHU)

        # Thước đo góc dưới trái: 10 ô
        dai = 10 * s
        bx, by = 12, cao - 14
        c.create_line(bx, by, bx + dai, by, fill = m["chuphu"], width = 2)
        c.create_line(bx, by - 4, bx, by + 1, fill = m["chuphu"], width = 2)
        c.create_line(bx + dai, by - 4, bx + dai, by + 1, fill = m["chuphu"], width = 2)
        self._chuvien(bx + dai + 6, by - 1, "10 ô", m["chuphu"], anchor = tk.W)

        tom = " · ".join(f"{TENLOAIDOITUONG[k]} {v}" for k, v in dems.items() if k in TENLOAIDOITUONG)
        self.lbl_trangthai.configure(text = tom)

    def _vechuthich(self):
        # Chú thích tự xuống dòng theo bề rộng khung
        c = self.chuthich
        c.delete("all")
        rongtoida = max(200, self.canvas.winfo_width() or KICHTHUOCKHUNG)
        muc = [("cham", MAUDOITUONG[loai], TENLOAIDOITUONG[loai]) for loai in ("quai", "thudich", "nguoichoi", "dongdoi", "npc")]
        muc += [("tran", MAUTRAN[ten], ten.replace(" Trận", "")) for ten in ("Kỳ Môn Trận", "Độn Giáp Trận")]
        muc += [("duong", MAUBANDO["duong"], "Đường bot đi"), ("diem", MAUBANDO["diemden"], "Điểm lộ trình")]
        x, y = 4, 11
        for kieu, mau, chu in muc:
            idchu = c.create_text(0, 0, text = chu, anchor = tk.W, fill = self._mau("chu_phu"), font = PHONGCHU)
            rongchu = c.bbox(idchu)[2] - c.bbox(idchu)[0]
            if x + 18 + rongchu > rongtoida:
                x, y = 4, y + 18
            if kieu == "cham":
                c.create_oval(x, y - 4, x + 9, y + 5, fill = mau, outline = "")
            elif kieu == "tran":
                c.create_rectangle(x, y - 5, x + 10, y + 5, outline = mau, fill = mau, stipple = "gray25")
            elif kieu == "duong":
                c.create_line(x, y, x + 12, y, fill = mau, width = 2, dash = (4, 2))
            else:
                c.create_polygon(x + 5, y - 5, x + 10, y, x + 5, y + 5, x, y, outline = mau, fill = "", width = 2)
            c.coords(idchu, x + 15, y)
            x += 15 + rongchu + 12
        c.configure(height = y + 9)

    def _rechuot(self, e):
        d = self._dulieu
        if not d:
            return
        ox, oy = self._oduoichuot(e.x, e.y)
        chu = f"Ô ({ox},{oy})"
        gannhat = None
        for x, y, loai, ten, _ in d.get("doituongs") or ():
            kc = max(abs(x - ox), abs(y - oy))
            if kc <= 1 and (gannhat is None or kc < gannhat[0]):
                gannhat = (kc, f"{TENLOAIDOITUONG.get(loai, loai)}: {ten}")
        if gannhat:
            chu += " · " + gannhat[1]
        else:
            for tx, ty, ten, nuacanh in d.get("trans") or ():
                if max(abs(tx - ox), abs(ty - oy)) <= nuacanh:
                    chu += f" · trong {ten} tâm ({tx},{ty})"
                    break
        self.lbl_chuot.configure(text = chu)


def mobandonho(giaodien):
    # Nút ở tab Khác: chỉ 1 cửa sổ, bấm lại thì đưa lên trên
    if getattr(giaodien, "_bandonho", None):
        try:
            giaodien._bandonho.hienlen()
            return
        except tk.TclError:
            pass
    giaodien._bandonho = CuaSoBanDoNho(giaodien)
