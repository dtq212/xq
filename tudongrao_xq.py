import json
import os
import random
import sys
import time
import tkinter as tk
from tkinter import ttk

# Tự động rao: mỗi nhân vật (theo ID) rao lặp lại trên 1 kênh chat, mỗi lần bốc ngẫu nhiên 1 câu trong danh sách (không lặp câu vừa rao
# nếu có từ 2 câu), cách nhau ngẫu nhiên [chukytu, chukyden] giây. Gửi "<kênh> <nội dung>" như rao bán ngân lượng (bannganluong_xq).
# Cấu hình _internal/tudongrao.json: {"<ID người chơi>": {"bat", "kenh", "chukytu", "chukyden", "noidung": [câu...]}},
# chỉnh ở cửa sổ "Tự động rao" (tab Khác); bot đọc lại khi file đổi (~2 giây), không cần khởi động lại.
# Rao cả khi tắt bot (ô tích danh sách nhân vật) - nhân vật đứng bán vẫn rao được; chỉ ngừng khi mất kết nối / chưa vào game.

# Kênh nhận (cùng danh sách cuaso_xq cho "raoban:"): tên trong chuỗi "<kênh> %s" của XQ.exe -> nhãn. Đã test: vipchat thế giới
# (2026-11-10 hiện đủ câu ~160 byte), say lân cận; các kênh khác chưa rõ là kênh nào trong game
KENHRAO_MAP = {"vipchat": "vipchat · Thế giới", "say": "say · Lân cận", "chat": "chat", "rumor": "rumor",
               "ct": "ct", "ot": "ot", "ft": "ft", "et": "et", "tt": "tt"}
# Khoảng rao tối thiểu (giây) để khỏi spam khi nhập sai; câu dài hơn chừng này byte (utf-8) có thể bị game cắt
KHOANGRAOTOITHIEU = 5.
DODAICAUTOIDA = 160
CHUKYDOCCAUHINH = 2.
CHUKYVONG = 1.
# Gửi lệnh không được (chưa tới lượt lệnh / đang khoá) thì thử lại sau chừng này giây, không tính là đã rao
THOIGIANTHULAI = 3.
CAUHINHMACDINH = {"bat": False, "kenh": "vipchat", "chukytu": 300, "chukyden": 600, "noidung": []}


def _thumucinternal():
    goc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(goc, "_internal")


def duongdancauhinhrao():
    return os.path.join(_thumucinternal(), "tudongrao.json")


def taicauhinhrao():
    try:
        with open(duongdancauhinhrao(), "r", encoding = "utf-8-sig") as f:
            dulieu = json.load(f)
        return dulieu if isinstance(dulieu, dict) else {}
    except FileNotFoundError:
        return {}
    except Exception as err:
        print(f"[TỰ RAO] Lỗi đọc {duongdancauhinhrao()}: {err}")
        return {}


def luucauhinhrao(cauhinh):
    duongdan = duongdancauhinhrao()
    os.makedirs(os.path.dirname(duongdan), exist_ok = True)
    with open(duongdan + ".tmp", "w", encoding = "utf-8") as f:
        json.dump(cauhinh, f, ensure_ascii = False, indent = 1)
    os.replace(duongdan + ".tmp", duongdan)


def chuanhoa(ch):
    # Cấu hình 1 nhân vật -> đủ khoá, kênh hợp lệ, chu kỳ >= tối thiểu (từ <= đến), bỏ câu trống
    ch = dict(CAUHINHMACDINH, **(ch if isinstance(ch, dict) else {}))
    if ch["kenh"] not in KENHRAO_MAP:
        ch["kenh"] = CAUHINHMACDINH["kenh"]
    try:
        tu, den = max(KHOANGRAOTOITHIEU, float(ch["chukytu"])), max(KHOANGRAOTOITHIEU, float(ch["chukyden"]))
    except (TypeError, ValueError):
        tu, den = CAUHINHMACDINH["chukytu"], CAUHINHMACDINH["chukyden"]
    ch["chukytu"], ch["chukyden"] = min(tu, den), max(tu, den)
    noidung = ch["noidung"] if isinstance(ch["noidung"], list) else [ch["noidung"]]
    ch["noidung"] = [" ".join(str(c).split()) for c in noidung if str(c).strip()]
    ch["bat"] = bool(ch["bat"])
    return ch


class TuDongRao:
    # Phía bot: mỗi cửa sổ một đối tượng, chạy luồng riêng (loop), gửi lệnh thẳng bằng moitruong (không qua command_dict)
    def __init__(self, moitruong):
        self.moitruong = moitruong
        self._cauhinh = chuanhoa({})
        self._idcauhinh = None
        self._mtimecauhinh = None
        self._thoidiemdoccauhinh = 0.
        self._luctieptheo = 0.
        self._caucuoi = None
        self._luccuoi = 0.

    def _doccauhinh(self, idnguoichoi):
        bayh = time.time()
        if bayh - self._thoidiemdoccauhinh < CHUKYDOCCAUHINH and idnguoichoi == self._idcauhinh:
            return
        self._thoidiemdoccauhinh = bayh
        try:
            mtime = os.path.getmtime(duongdancauhinhrao())
        except OSError:
            mtime = None
        if mtime == self._mtimecauhinh and idnguoichoi == self._idcauhinh:
            return
        cu = self._cauhinh
        self._mtimecauhinh, self._idcauhinh = mtime, idnguoichoi
        self._cauhinh = chuanhoa(taicauhinhrao().get(str(idnguoichoi)))
        # Vừa bật / đổi chu kỳ thì rao ngay lượt tới (không bắt chờ hết chu kỳ cũ)
        if self._cauhinh["bat"] and (not cu["bat"] or (cu["chukytu"], cu["chukyden"]) != (self._cauhinh["chukytu"], self._cauhinh["chukyden"])):
            self._luctieptheo = 0.

    def buoc(self):
        mt = self.moitruong
        if mt.get_is_dangmatketnoi():
            return
        idnguoichoi = mt.get_idnguoichoi()
        if not idnguoichoi:
            return
        self._doccauhinh(idnguoichoi)
        ch = self._cauhinh
        if not ch["bat"] or not ch["noidung"] or time.time() < self._luctieptheo:
            return
        cacau = [c for c in ch["noidung"] if c != self._caucuoi] or ch["noidung"]
        cau = random.choice(cacau)
        if not mt.action_thucthicaulenh2(f"{ch['kenh']} {cau}", delay = 0.):
            self._luctieptheo = time.time() + THOIGIANTHULAI
            return
        bayh = time.time()
        self._caucuoi, self._luccuoi = cau, bayh
        self._luctieptheo = bayh + random.uniform(ch["chukytu"], ch["chukyden"])
        print(f"[TỰ RAO] {ch['kenh']}: {cau} (lần sau sau {self._luctieptheo - bayh:.0f}s)")

    def get_share(self):
        # Cho cửa sổ Tự động rao: câu gần nhất + thời điểm, lần tới (0 = chưa hẹn)
        return {"bat": self._cauhinh["bat"], "caucuoi": self._caucuoi, "luccuoi": self._luccuoi,
                "luctieptheo": self._luctieptheo if self._cauhinh["bat"] else 0.}

    def loop(self, stop):
        while not stop.is_set():
            try:
                self.buoc()
            except Exception as err:
                print(f"[TỰ RAO] Lỗi: {err}")
                time.sleep(5)
            time.sleep(CHUKYVONG)


def khoidong_looptudongrao(tudongrao, stop):
    tudongrao.loop(stop)


# ---------------------------------------------------------------------------------------------------------------------------------------
# Phía giao diện: cửa sổ chỉnh câu rao cho nhân vật đang chọn, bấm Lưu thì ghi tudongrao.json

class CuaSoTuDongRao:
    def __init__(self, giaodien):
        self.gd = giaodien
        self.hwnd = None
        self.idnguoichoi = None
        self.top = tk.Toplevel(giaodien.root)
        self.top.title("Tự động rao")
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
        khung.rowconfigure(5, weight = 1)

        ttk.Label(khung, text = "Nhân vật:").grid(row = 0, column = 0, sticky = tk.W)
        self.cbo_nv = ttk.Combobox(khung, state = "readonly", width = 34)
        self.cbo_nv.grid(row = 0, column = 1, sticky = tk.EW, pady = 2)
        self.cbo_nv.bind("<<ComboboxSelected>>", lambda e: self._chonnhanvat(self._hwndtheonhan.get(self.cbo_nv.get())))
        self.cbo_nv.bind("<Button-1>", lambda e: self._napnhanvat())

        self.var_bat = tk.BooleanVar(value = False)
        ttk.Checkbutton(khung, text = "Bật tự động rao", variable = self.var_bat, command = self._luu).grid(
            row = 1, column = 0, columnspan = 2, sticky = tk.W, pady = (4, 4))

        ttk.Label(khung, text = "Kênh:").grid(row = 2, column = 0, sticky = tk.W)
        self._kenhtheonhan = {nhan: kenh for kenh, nhan in KENHRAO_MAP.items()}
        self.cbo_kenh = ttk.Combobox(khung, state = "readonly", width = 20, values = list(self._kenhtheonhan))
        self.cbo_kenh.grid(row = 2, column = 1, sticky = tk.W, pady = 2)

        ttk.Label(khung, text = "Cách nhau (giây):").grid(row = 3, column = 0, sticky = tk.W)
        hangchuky = ttk.Frame(khung)
        hangchuky.grid(row = 3, column = 1, sticky = tk.W, pady = 2)
        self.var_tu = tk.StringVar()
        self.var_den = tk.StringVar()
        ttk.Entry(hangchuky, textvariable = self.var_tu, width = 7).pack(side = tk.LEFT)
        ttk.Label(hangchuky, text = " đến ").pack(side = tk.LEFT)
        ttk.Entry(hangchuky, textvariable = self.var_den, width = 7).pack(side = tk.LEFT)
        ttk.Label(hangchuky, text = f"  (ngẫu nhiên, tối thiểu {KHOANGRAOTOITHIEU:.0f}s)", style = "Phu.TLabel").pack(side = tk.LEFT)

        ttk.Label(khung, text = "Câu rao (mỗi dòng 1 câu, mỗi lần bốc ngẫu nhiên 1 câu):").grid(
            row = 4, column = 0, columnspan = 2, sticky = tk.W, pady = (6, 2))
        self.txt = tk.Text(khung, width = 60, height = 8, wrap = tk.WORD, undo = True,
                           background = giaodien._mau.get("nen_o", "#ffffff"), foreground = giaodien._mau.get("chu", "#000000"),
                           insertbackground = giaodien._mau.get("chu", "#000000"))
        self.txt.grid(row = 5, column = 0, columnspan = 2, sticky = tk.NSEW)

        hangnut = ttk.Frame(khung)
        hangnut.grid(row = 6, column = 0, columnspan = 2, sticky = tk.EW, pady = (6, 0))
        ttk.Button(hangnut, text = "Lưu", command = self._luu).pack(side = tk.LEFT)
        ttk.Button(hangnut, text = "Chép sang mọi nhân vật", command = self._chepsangtatca).pack(side = tk.LEFT, padx = (6, 0))
        self.lbl_trangthai = ttk.Label(khung, text = "", style = "Phu.TLabel", wraplength = 440, justify = tk.LEFT)
        self.lbl_trangthai.grid(row = 7, column = 0, columnspan = 2, sticky = tk.W, pady = (6, 0))
        ttk.Label(khung, text = f"Rao cả khi tắt bot nhân vật đó. Câu dài quá ~{DODAICAUTOIDA} byte có thể bị game cắt. Rao dày trên kênh"
                                " thế giới dễ bị báo cáo, nên để vài phút một lần và viết nhiều câu khác nhau.",
                  style = "Phu.TLabel", wraplength = 440, justify = tk.LEFT).grid(row = 8, column = 0, columnspan = 2, sticky = tk.W, pady = (6, 0))

        self._hwndtheonhan = {}
        self._thongbaoluu = ""
        self._luclu = 0.
        self._napnhanvat()
        self._chonnhanvat(giaodien.get_selected_hwnd())
        self._capnhattrangthai()

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
        self.idnguoichoi = self._layinfo(hwnd).get("idnguoichoi")
        ch = chuanhoa(taicauhinhrao().get(str(self.idnguoichoi)))
        self.var_bat.set(ch["bat"])
        self.cbo_kenh.set(KENHRAO_MAP[ch["kenh"]])
        self.var_tu.set(f"{ch['chukytu']:g}")
        self.var_den.set(f"{ch['chukyden']:g}")
        self.txt.delete("1.0", tk.END)
        self.txt.insert("1.0", "\n".join(ch["noidung"]))

    def _docnhap(self):
        return chuanhoa({"bat": self.var_bat.get(), "kenh": self._kenhtheonhan.get(self.cbo_kenh.get(), "vipchat"),
                         "chukytu": self.var_tu.get(), "chukyden": self.var_den.get(),
                         "noidung": self.txt.get("1.0", tk.END).splitlines()})

    def _luu(self):
        if not self.idnguoichoi:
            self.lbl_trangthai.configure(text = "Chọn nhân vật trước")
            return
        ch = self._docnhap()
        cauhinh = taicauhinhrao()
        cauhinh[str(self.idnguoichoi)] = ch
        try:
            luucauhinhrao(cauhinh)
        except Exception as err:
            self.lbl_trangthai.configure(text = f"Lỗi lưu: {err}")
            return
        # Hiện lại giá trị đã chuẩn hoá (chu kỳ dưới tối thiểu, dòng trống...)
        self.var_tu.set(f"{ch['chukytu']:g}")
        self.var_den.set(f"{ch['chukyden']:g}")
        dai = [c for c in ch["noidung"] if len(f"{ch['kenh']} {c}".encode("utf-8")) > DODAICAUTOIDA]
        self._thongbaoluu = f"Đã lưu {len(ch['noidung'])} câu" + (f", {len(dai)} câu dài, có thể bị cắt" if dai else "") + \
                            ("" if ch["noidung"] or not ch["bat"] else " - chưa có câu nào nên chưa rao")
        self._luclu = time.time()

    def _chepsangtatca(self):
        # Chép kênh / chu kỳ / câu (không chép ô Bật) sang mọi nhân vật đang chạy; ô Bật của nhân vật khác giữ nguyên
        ch = self._docnhap()
        cauhinh = taicauhinhrao()
        so = 0
        for hwnd in self._hwndtheonhan.values():
            idnv = self._layinfo(hwnd).get("idnguoichoi")
            if not idnv:
                continue
            cu = chuanhoa(cauhinh.get(str(idnv)))
            cauhinh[str(idnv)] = dict(ch, bat = ch["bat"] if str(idnv) == str(self.idnguoichoi) else cu["bat"])
            so += 1
        try:
            luucauhinhrao(cauhinh)
        except Exception as err:
            self.lbl_trangthai.configure(text = f"Lỗi lưu: {err}")
            return
        self._thongbaoluu = f"Đã chép sang {so} nhân vật (ô Bật của từng nhân vật giữ nguyên)"
        self._luclu = time.time()

    def _capnhattrangthai(self):
        try:
            if not self.top.winfo_exists():
                return
        except tk.TclError:
            return
        dong = []
        if time.time() - self._luclu < 4:
            dong.append(self._thongbaoluu)
        rao = self._layinfo(self.hwnd).get("_tudongrao") if self.hwnd else None
        if rao is None and self.hwnd:
            dong.append("Chưa có dữ liệu từ bot (khởi động lại bot sau khi cập nhật)")
        elif rao:
            if rao.get("caucuoi"):
                dong.append(f"Rao gần nhất {time.strftime('%H:%M:%S', time.localtime(rao['luccuoi']))}: {rao['caucuoi']}")
            if rao.get("bat") and rao.get("luctieptheo"):
                dong.append(f"Lần tới sau {max(0, rao['luctieptheo'] - time.time()):.0f}s")
            elif not rao.get("bat"):
                dong.append("Đang tắt")
        self.lbl_trangthai.configure(text = "\n".join(dong))
        self.top.after(1000, self._capnhattrangthai)

    def dong(self):
        self.gd._tudongrao = None
        self.top.destroy()

    def hienlen(self):
        self.top.deiconify()
        self.top.lift()


def motudongrao(giaodien):
    if getattr(giaodien, "_tudongrao", None):
        try:
            giaodien._tudongrao.hienlen()
            return
        except tk.TclError:
            pass
    giaodien._tudongrao = CuaSoTuDongRao(giaodien)
