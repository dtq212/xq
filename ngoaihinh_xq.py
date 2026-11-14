import json
import os
import struct
import sys
import time
import tkinter as tk
from tkinter import ttk, colorchooser

from diachi_xq import DC
from hangso_xq import COHIENTHI_MACDINH
from tienich_xq import read_int, write_int, read_bytes, write_bytes

# Ngoại hình chỉ mình thấy (người dùng muốn 2026-11-14): ghi đè ngoại trang / cánh / vũ khí / màu hào quang của nhân vật mình trong bộ
# nhớ client. Máy chủ và người khác không thấy gì. Đo trên 364 ("Gạ") 2026-11-14:
#  - Màu hào quang 3 byte theo thứ tự B, G, R (ghi FF0000 ra xanh lam đậm): vũ khí +0xA4, cánh +0xA8 và +0xB4, y phục +0xB0.
#    Lên / xuống thú cưỡi là game nạp lại từ bản gốc ở chỗ khác (30s bị đè 18 lần) => phải ghi đè liên tục, ghi mỗi CHUKYGHIDE giây.
#  - Ngoại trang +0x1174 (DC.NV_NGOAITRANG): 10003 đồ môn phái Thục Sơn -> 10001 đồ vô môn phái, đổi được ngay, 45s không văng.
#  - Cánh +0x119C 2 số (DC.NV_CANH), id vũ khí +0x1184 (DC.NV_VUKHI). KHÔNG ghi loại vũ khí +0x1180: bot đọc ô đó để quyết định
#    (ám khí đánh xa, Vân Mộng Cốc buff theo loại vũ khí...), nên chỉ cho chọn vũ khí cùng loại đang cầm.
# Chỉ cho chọn mã đã thấy trên người chơi thật (ghi vào ngoaihinh_dathay.json khi gặp): mã game không có ảnh dễ làm văng client.
# Giới tính đoán theo số đã thấy (chưa kiểm chứng hết): ngoại trang 10xxx nam / 11xxx nữ, cánh nữ >= 1000 (11001 đi với 1005/1000,
# 11008 với 1008; nam 10001 với 5, 10003 với 7). Lệch giới tính có thể thiếu ảnh nên giao diện lọc theo giới tính đang mặc.

CHUKYGHIDE = 0.2
CHUKYDOCCAUHINH = 2.
CHUKYGHINHAN = 10.
# Màu: tên trong cấu hình -> các offset (3 byte B, G, R)
OFFSETMAUs = {"mauvukhi": (0xA4,), "maucanh": (0xA8, 0xB4), "mauyphuc": (0xB0,)}
OFFSET_LOAIVUKHI = 0x1180


def _thumucinternal():
    goc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(goc, "_internal")


def duongdancauhinhngoaihinh():
    # {"<ID người chơi>": {"bat", "ngoaitrang", "canh": [a, b], "vukhi", "mauvukhi" / "maucanh" / "mauyphuc": "rrggbb" (RGB thường)}}
    return os.path.join(_thumucinternal(), "ngoaihinh.json")


def duongdanngoaihinhdathay():
    # {"ngoaitrang": {"10001": {"ten", "luc"}}, "canh": {"5,0": ...}, "vukhi": {"62:14": ...}} mã đã thấy trên người chơi thật
    return os.path.join(_thumucinternal(), "ngoaihinh_dathay.json")


def _docjson(duongdan):
    try:
        with open(duongdan, "r", encoding = "utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as err:
        print(f"Lỗi đọc {duongdan}: {err}")
        return {}


def _ghijson(duongdan, dulieu):
    tam = duongdan + ".tmp"
    with open(tam, "w", encoding = "utf-8") as f:
        json.dump(dulieu, f, ensure_ascii = False, indent = 1)
    os.replace(tam, duongdan)


def taicauhinhngoaihinh():
    return _docjson(duongdancauhinhngoaihinh())


def luucauhinhngoaihinh(cauhinh):
    _ghijson(duongdancauhinhngoaihinh(), cauhinh)


def taingoaihinhdathay():
    return _docjson(duongdanngoaihinhdathay())


def duongdanhienthi():
    # Cờ ẩn hiển thị chung mọi cửa sổ (ô tích tab Khác): {"hieuungnhanvat": bool, "tranphap": bool}, xem hangso COHIENTHI_VITRI
    return os.path.join(_thumucinternal(), "hienthi.json")


def taihienthi():
    hienthi = dict(COHIENTHI_MACDINH)
    hienthi.update({k: bool(v) for k, v in _docjson(duongdanhienthi()).items() if k in COHIENTHI_MACDINH})
    return hienthi


def luuhienthi(hienthi):
    _ghijson(duongdanhienthi(), hienthi)


def rgbsangbgr(mau):
    return bytes.fromhex(mau)[::-1]


class NgoaiHinh:
    # Phía bot: mỗi cửa sổ một đối tượng, chạy trong luồng riêng (loop)
    def __init__(self, moitruong):
        self.moitruong = moitruong
        self._cauhinh = {}
        self._mtimecauhinh = None
        # Cờ ẩn hiển thị (hienthi.json): mtime lần áp gần nhất; "chua" = chưa áp lần nào (áp ngay cả khi chưa có file)
        self._mtimehienthi = "chua"
        self._thoidiemdoccauhinh = 0.
        self._thoidiemghinhan = 0.
        # Giá trị thật trước khi đè: {khoá ô: bytes}, theo con trỏ nhân vật (đổi bản đồ / đăng nhập lại thì đọc lại)
        self._goc = {}
        self._contrognoc = None
        # Ngoại hình thật đang mặc (cho giao diện): cập nhật mỗi vòng ở những ô không đè
        self._that = {}

    # --- cấu hình -----------------------------------------------------------------------------------------------------------------------
    def _doccauhinh(self, idnguoichoi):
        bayh = time.time()
        if bayh - self._thoidiemdoccauhinh < CHUKYDOCCAUHINH:
            return
        self._thoidiemdoccauhinh = bayh
        self._dochienthi()
        try:
            mtime = os.path.getmtime(duongdancauhinhngoaihinh())
        except OSError:
            mtime = None
        if mtime == self._mtimecauhinh:
            return
        self._mtimecauhinh = mtime
        self._cauhinh = taicauhinhngoaihinh().get(str(idnguoichoi)) or {}

    def _dochienthi(self):
        # Ô tích ẩn hiển thị ở tab Khác đổi thì ghi cờ vào game (hook vẽ đọc mỗi khung hình)
        try:
            mtime = os.path.getmtime(duongdanhienthi())
        except OSError:
            mtime = None
        if mtime == self._mtimehienthi:
            return
        self._mtimehienthi = mtime
        for ten, is_an in taihienthi().items():
            self.moitruong.set_cohienthi(ten, is_an)

    def _danhsachghide(self):
        # [(khoá ô, offset, bytes muốn ghi)] theo cấu hình đang bật
        ch = self._cauhinh
        if not ch.get("bat"):
            return []
        ds = []
        if isinstance(ch.get("ngoaitrang"), int):
            ds.append(("ngoaitrang", DC.NV_NGOAITRANG, struct.pack("<i", ch["ngoaitrang"])))
        if isinstance(ch.get("canh"), list) and len(ch["canh"]) == 2:
            ds.append(("canh", DC.NV_CANH, struct.pack("<ii", *ch["canh"])))
        if isinstance(ch.get("vukhi"), int):
            ds.append(("vukhi", DC.NV_VUKHI, struct.pack("<i", ch["vukhi"])))
        for ten, offsets in OFFSETMAUs.items():
            mau = ch.get(ten)
            if isinstance(mau, str) and len(mau) == 6:
                for i, o in enumerate(offsets):
                    ds.append((f"{ten}{i}", o, rgbsangbgr(mau)))
        return ds

    # --- một vòng ----------------------------------------------------------------------------------------------------------------------
    def buoc(self):
        mt = self.moitruong
        nv = mt._doccontronhanvat()
        if not nv:
            return
        if nv != self._contrognoc:
            self._goc, self._contrognoc = {}, nv
        self._doccauhinh(mt.get_idnguoichoi())
        ghide = self._danhsachghide()
        khoaghide = {k for k, _, _ in ghide}
        for khoa, o, dulieu in ghide:
            hientai = read_bytes(mt.tientrinh, nv + o, len(dulieu))
            if hientai == dulieu:
                continue
            # Game vừa nạp lại (thú cưỡi, thay đồ...): giá trị lúc này là đồ thật mới nhất
            self._goc[khoa] = (o, hientai)
            write_bytes(mt.tientrinh, nv + o, dulieu, len(dulieu))
        # Ô thôi đè (tắt / bỏ chọn): trả giá trị thật đã nhớ
        for khoa in [k for k in self._goc if k not in khoaghide]:
            o, goc = self._goc.pop(khoa)
            write_bytes(mt.tientrinh, nv + o, goc, len(goc))
        self._capnhatthat(nv, khoaghide)
        if time.time() - self._thoidiemghinhan >= CHUKYGHINHAN:
            self._thoidiemghinhan = time.time()
            self._ghinhandathay(nv, khoaghide)

    def _docngoaihinh(self, diachi):
        tt = self.moitruong.tientrinh
        return {
            "ngoaitrang": read_int(tt, diachi + DC.NV_NGOAITRANG),
            "canh": list(struct.unpack("<ii", read_bytes(tt, diachi + DC.NV_CANH, 8))),
            "vukhi": read_int(tt, diachi + DC.NV_VUKHI),
            "loaivukhi": read_int(tt, diachi + OFFSET_LOAIVUKHI),
        }

    def _capnhatthat(self, nv, khoaghide):
        that = self._docngoaihinh(nv)
        for khoa in ("ngoaitrang", "canh", "vukhi"):
            if khoa in khoaghide and khoa in self._goc:
                o, goc = self._goc[khoa]
                that[khoa] = list(struct.unpack("<ii", goc)) if khoa == "canh" else struct.unpack("<i", goc)[0]
        self._that = that

    def get_share(self):
        # Cho giao diện: ngoại hình thật đang mặc (không tính phần đang đè)
        return dict(self._that)

    def _ghinhandathay(self, nv, khoaghide):
        # Mã ngoại hình của người chơi xung quanh (và của mình khi không đè) vào ngoaihinh_dathay.json; chỉ ghi file khi có mã mới
        mt = self.moitruong
        thay = []
        try:
            _, banchup = mt._get_banchupdoituongxungquanh()
            for diachi, _, _ in banchup:
                # Chỉ người chơi thật (+0x28 loại 1 / 2): lớp +0x29 < 0x80 còn lọt bóng / phân thân ("Yêu Bài", "Càng Lớn" chép ngoại hình chủ)
                if not mt.get_is_nguoichoi(diachi):
                    continue
                thay.append((mt.get_tendoituong(diachi) or "", self._docngoaihinh(diachi)))
        except Exception:
            pass
        if self._that:
            thay.append((mt.get_tendoituong() or "", self._that))
        kho = taingoaihinhdathay()
        is_moi = False
        for ten, nh in thay:
            for loai, khoa in (("ngoaitrang", str(nh["ngoaitrang"])), ("canh", f"{nh['canh'][0]},{nh['canh'][1]}"),
                               ("vukhi", f"{nh['loaivukhi']}:{nh['vukhi']}")):
                if loai == "ngoaitrang" and nh["ngoaitrang"] < 10000:
                    continue  # 99 = bóng / phân thân, không phải trang phục
                if loai == "vukhi" and nh["vukhi"] <= 0:
                    continue
                if loai == "canh" and nh["canh"][0] <= 0:
                    continue
                muc = kho.setdefault(loai, {})
                if khoa not in muc:
                    muc[khoa] = {"ten": ten, "luc": int(time.time())}
                    is_moi = True
        if is_moi:
            try:
                _ghijson(duongdanngoaihinhdathay(), kho)
            except Exception as err:
                print(f"Lỗi ghi ngoại hình đã thấy: {err}")

    def loop(self, stop):
        while not stop.is_set():
            try:
                self.buoc()
            except Exception as err:
                print(f"[NGOẠI HÌNH] Lỗi: {err}")
                time.sleep(1)
            time.sleep(CHUKYGHIDE)


def khoidong_loopngoaihinh(ngoaihinh, stop):
    ngoaihinh.loop(stop)


# ---------------------------------------------------------------------------------------------------------------------------------------
# Phía giao diện: cửa sổ chỉnh ngoại hình cho nhân vật đang chọn, lưu vào ngoaihinh.json (bot tự đọc lại khi file đổi)

GIUNGUYEN = "(giữ nguyên)"


def _gioitinh(ngoaitrang):
    # 10 nam / 11 nữ theo nghìn của mã ngoại trang (xem chú thích đầu file); None = chưa biết
    return ngoaitrang // 1000 if isinstance(ngoaitrang, int) and ngoaitrang >= 10000 else None


class CuaSoNgoaiHinh:
    def __init__(self, giaodien):
        self.gd = giaodien
        self.hwnd = None
        self.top = tk.Toplevel(giaodien.root)
        self.top.title("Ngoại hình chỉ mình thấy")
        self.top.configure(background = giaodien._mau.get("nen", "#ffffff"))
        self.top.protocol("WM_DELETE_WINDOW", self.dong)
        try:
            from chude_xq import doithanhtieude
            self.top.after(0, lambda: doithanhtieude(self.top, getattr(giaodien, "is_chedotoi", False)))
        except Exception:
            pass

        khung = ttk.Frame(self.top, padding = 10)
        khung.pack(fill = tk.BOTH, expand = True)
        khung.columnconfigure(1, weight = 1)

        ttk.Label(khung, text = "Nhân vật:").grid(row = 0, column = 0, sticky = tk.W)
        self.cbo_nv = ttk.Combobox(khung, state = "readonly", width = 30)
        self.cbo_nv.grid(row = 0, column = 1, columnspan = 2, sticky = tk.EW, pady = 2)
        self.cbo_nv.bind("<<ComboboxSelected>>", lambda e: self._chonnhanvat(self._hwndtheonhan.get(self.cbo_nv.get())))
        self.cbo_nv.bind("<Button-1>", lambda e: self._napnhanvat())

        self.lbl_that = ttk.Label(khung, text = "", style = "Phu.TLabel")
        self.lbl_that.grid(row = 1, column = 0, columnspan = 3, sticky = tk.W, pady = (0, 6))

        self.var_bat = tk.BooleanVar(value = False)
        ttk.Checkbutton(khung, text = "Bật ngoại hình chỉ mình thấy", variable = self.var_bat, command = self._luu).grid(
            row = 2, column = 0, columnspan = 3, sticky = tk.W, pady = (0, 6))

        self.cbos = {}
        for hang, (khoa, nhan) in enumerate((("ngoaitrang", "Ngoại trang"), ("canh", "Cánh"), ("vukhi", "Vũ khí")), start = 3):
            ttk.Label(khung, text = nhan + ":").grid(row = hang, column = 0, sticky = tk.W)
            cbo = ttk.Combobox(khung, state = "readonly", width = 30)
            cbo.grid(row = hang, column = 1, columnspan = 2, sticky = tk.EW, pady = 2)
            cbo.bind("<<ComboboxSelected>>", lambda e: self._luu())
            self.cbos[khoa] = cbo

        self.mau = {}
        self.nutmau = {}
        for hang, (khoa, nhan) in enumerate((("mauvukhi", "Màu vũ khí"), ("maucanh", "Màu cánh"), ("mauyphuc", "Màu y phục")), start = 6):
            ttk.Label(khung, text = nhan + ":").grid(row = hang, column = 0, sticky = tk.W)
            nut = tk.Label(khung, text = GIUNGUYEN, width = 18, relief = tk.GROOVE, cursor = "hand2")
            nut.grid(row = hang, column = 1, sticky = tk.W, pady = 2)
            nut.bind("<Button-1>", lambda e, k = khoa: self._chonmau(k))
            ttk.Button(khung, text = "Bỏ", width = 4, command = lambda k = khoa: self._datmau(k, None)).grid(row = hang, column = 2, sticky = tk.W)
            self.nutmau[khoa] = nut
            self.mau[khoa] = None

        ttk.Label(khung, text = "Chỉ client này thấy. Danh sách trang phục / cánh / vũ khí lấy từ người chơi thật bot đã gặp (cùng giới tính,"
                                " vũ khí cùng loại đang cầm), gặp thêm người thì có thêm lựa chọn. Màu là hào quang cường hoá.",
                  style = "Phu.TLabel", wraplength = 330, justify = tk.LEFT).grid(row = 9, column = 0, columnspan = 3, sticky = tk.W, pady = (8, 0))

        self._hwndtheonhan = {}
        self._giatritheonhan = {}
        self._napnhanvat()
        self._chonnhanvat(giaodien.get_selected_hwnd())

    def _layinfo(self, hwnd):
        try:
            return self.gd.shared_data.get(hwnd) or {}
        except Exception:
            return {}

    def _napnhanvat(self):
        self._hwndtheonhan = {}
        try:
            danhsach = list(self.gd.shared_data.items())
        except Exception:
            danhsach = []
        for hwnd, info in danhsach:
            if isinstance(info, dict) and info.get("tennhanvat") and info.get("idnguoichoi"):
                self._hwndtheonhan[f"{info['tennhanvat']} ({info['idnguoichoi']})"] = hwnd
        self.cbo_nv.configure(values = list(self._hwndtheonhan))

    def _chonnhanvat(self, hwnd):
        if not hwnd:
            return
        self.hwnd = hwnd
        for nhan, h in self._hwndtheonhan.items():
            if h == hwnd:
                self.cbo_nv.set(nhan)
        info = self._layinfo(hwnd)
        self.idnguoichoi = info.get("idnguoichoi")
        that = info.get("_ngoaihinh") or {}
        self.lbl_that.configure(text = f"Đang mặc thật: ngoại trang {that.get('ngoaitrang', '?')}, cánh {that.get('canh', '?')}, "
                                       f"vũ khí {that.get('vukhi', '?')} (loại {that.get('loaivukhi', '?')})" if that else
                                "Chưa có dữ liệu từ bot (khởi động lại bot sau khi cập nhật)")
        self._naplualchon(that)
        ch = taicauhinhngoaihinh().get(str(self.idnguoichoi)) or {}
        self.var_bat.set(bool(ch.get("bat")))
        for khoa, cbo in self.cbos.items():
            giatri = ch.get(khoa)
            nhan = next((n for n, v in self._giatritheonhan[khoa].items() if v == giatri), GIUNGUYEN) if giatri is not None else GIUNGUYEN
            cbo.set(nhan)
        for khoa in self.mau:
            self._datmau(khoa, ch.get(khoa), is_luu = False)

    def _naplualchon(self, that):
        kho = taingoaihinhdathay()
        gioi = _gioitinh(that.get("ngoaitrang"))
        loaivk = that.get("loaivukhi")
        self._giatritheonhan = {}
        for khoa in self.cbos:
            nhans = {GIUNGUYEN: None}
            for ma, muc in sorted((kho.get(khoa) or {}).items()):
                try:
                    if khoa == "ngoaitrang":
                        giatri = int(ma)
                        if gioi is not None and _gioitinh(giatri) != gioi:
                            continue
                    elif khoa == "canh":
                        giatri = [int(v) for v in ma.split(",")]
                        if gioi is not None and (giatri[0] >= 1000) != (gioi == 11):
                            continue
                    else:
                        loai, idvk = (int(v) for v in ma.split(":"))
                        if loaivk is not None and loai != loaivk:
                            continue
                        giatri = idvk
                except ValueError:
                    continue
                nhans[f"{ma} · thấy trên {muc.get('ten') or '?'}"] = giatri
            self._giatritheonhan[khoa] = nhans
            self.cbos[khoa].configure(values = list(nhans))

    def _chonmau(self, khoa):
        hientai = self.mau.get(khoa)
        ketqua = colorchooser.askcolor(color = f"#{hientai}" if hientai else None, parent = self.top, title = "Chọn màu")
        if ketqua and ketqua[1]:
            self._datmau(khoa, ketqua[1].lstrip("#").lower())

    def _datmau(self, khoa, mau, is_luu = True):
        self.mau[khoa] = mau
        nut = self.nutmau[khoa]
        if mau:
            r, g, b = (int(mau[i:i + 2], 16) for i in (0, 2, 4))
            nut.configure(text = f"#{mau.upper()}", background = f"#{mau}", foreground = "#000000" if r * 0.3 + g * 0.59 + b * 0.11 > 140 else "#ffffff")
        else:
            nut.configure(text = GIUNGUYEN, background = self.gd._mau.get("nen_o", "#ffffff"), foreground = self.gd._mau.get("chu", "#000000"))
        if is_luu:
            self._luu()

    def _luu(self):
        if not getattr(self, "idnguoichoi", None):
            return
        cauhinh = taicauhinhngoaihinh()
        ch = {"bat": self.var_bat.get()}
        for khoa, cbo in self.cbos.items():
            giatri = self._giatritheonhan.get(khoa, {}).get(cbo.get())
            if giatri is not None:
                ch[khoa] = giatri
        for khoa, mau in self.mau.items():
            if mau:
                ch[khoa] = mau
        cauhinh[str(self.idnguoichoi)] = ch
        try:
            luucauhinhngoaihinh(cauhinh)
        except Exception as err:
            print(f"Lỗi lưu ngoại hình: {err}")

    def dong(self):
        self.gd._ngoaihinh = None
        self.top.destroy()

    def hienlen(self):
        self.top.deiconify()
        self.top.lift()


def mongoaihinh(giaodien):
    if getattr(giaodien, "_ngoaihinh", None):
        try:
            giaodien._ngoaihinh.hienlen()
            return
        except tk.TclError:
            pass
    giaodien._ngoaihinh = CuaSoNgoaiHinh(giaodien)
