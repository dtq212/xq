import json
import os
import time
import types
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from bando_xq import BANDOCONG_MAP, laycapquaibando
from dexuatlotrinh_xq import SOLANTHAYQUAITOITHIEU
from hangso_xq import laytenbando, KHOANGCACHSUDUNGKYNANGTAMXA, PHANTRAMNOILUCKHAITHIENTICHDIA, KHOANGCACHGIUKETANCONG, BAOTHUTRIEUHOIMAOSONs
import re

from tienich_xq import tailotrinhmau, duongdanlotrinhmau, tainhomtodoitudongs, luunhomtodoitudongs, duongdantodoitudong, laynhomtodoitudongs
from tienich_xq import duongdantaikhoan, phatam, tenmaynay, taicauhinhphongyeu, luucauhinhphongyeu
from dangnhap_xq import duongdangamemaynay, is_batchomaynay, luucauhinhdangnhap, taicauhinhdangnhap, taikhoanbatchomaynay
from thongke_xq import taithongke, gopthongke
from luattuido_xq import tailuat, luuluat, motaluat, TENHANHDONG, DIEUKIENs, TENDIEUKIEN, TRUONGMUABU, TENTRUONGMUABU, TENCHIKHI, CHIKHI_LUON, XEPCHONGMACDINH
from hangso_xq import CHUTIEMTAPHOA, CHUTUULAU, TENMONPHAI, PHAMCHATVATPHAM_MAP
from dieuphoi_xq import taicauhinhdieuphoi, luucauhinhdieuphoi, chuanhoacauhinhdieuphoi, KENH_LENH, KENH_DICHUYEN

# Tạm ẩn các tùy chọn chưa dùng/không còn khả dụng (CN mở rộng, Khai khoáng, Đào tàng bảo đồ, Chiến trường).
# Đổi thành True để hiện lại (tab "Khác"). Phím tắt của chúng vẫn hoạt động.
HIEN_TUYCHON_CHUADUNG = False

FONTCHU = "Calibri"
COCHU = 11

MAUCHU_PHU = "#4d4d4d"
MAUCHU_XANH = "#1a4f9c"
MAUCHU_DO = "#b01020"
MAUCHU_LUC = "#17753f"

TEN_MUCTIEUMACDINH = "(Trưởng nhóm)"
# Máu dưới chừng này % thì dòng nhân vật hiện màu đỏ
NGUONGMAUTHAP = 40


class GiaoDienHienThi:
    def __init__(self, root, shared_data, command_dict, dieuphoi_trangthai = None, dangnhap = None):
        self.root = root
        self.shared_data = shared_data
        self.command_dict = command_dict
        # Dữ liệu chung của bộ chia lượt lệnh (xem dieuphoi_xq.py): giao diện ghi "cauhinh" vào đây, mọi bot đọc
        self.dieuphoi_trangthai = dieuphoi_trangthai
        # Luồng tự động đăng nhập (dangnhap_xq.TuDongDangNhap) chạy cùng tiến trình giao diện, chung cả máy
        self.dangnhap = dangnhap

        self.last_active_hwnd = None
        self._lotrinhmau_cache = ({}, None)
        self._hwndchonmautruocdo = None
        self._diemdanhdanghienthi = None
        # Vừa thêm / xoá mục tiêu: (hwnd, tấn công, bỏ qua, thời điểm) -> chờ bot nhận, trong lúc đó không nạp lại danh sách cũ đè lên
        self._danhsachmuctieudanglu = None
        # Ô chọn người theo sau: chữ hiển thị -> (ID, tên); vừa chọn thì (hwnd, ID, thời điểm) để chờ bot nhận, không bị nạp lại giá trị cũ đè lên
        self._muctieutheosau_map = {TEN_MUCTIEUMACDINH: (0, "")}
        self._muctieutheosauchoxacnhan = None

        self.root.title("Bảng Điều Khiển VIP")
        # Hệ số thu phóng màn hình (100% = 1.0, 125% = 1.25...) để kích thước tính bằng pixel không bị nhỏ đi
        self._heso = max(1.0, self.root.winfo_fpixels("1i") / 96.0)
        # Không cao quá màn hình (chừa chỗ cho thanh taskbar)
        chieucao = min(self._px(900), self.root.winfo_screenheight() - self._px(80))
        # Mở ở giữa màn hình (chừa thanh taskbar ở dưới)
        # Đủ cho hàng 4 tab và nội dung tab kèm thanh cuộn (màn hình thấp) không bị cắt chữ
        chieurong = self._px(700)
        x = max(0, (self.root.winfo_screenwidth() - chieurong) // 2)
        y = max(0, (self.root.winfo_screenheight() - self._px(40) - chieucao) // 2)
        self.root.geometry(f"{chieurong}x{chieucao}+{x}+{y}")
        self.root.minsize(self._px(600), self._px(600))
        self.root.attributes('-topmost', True)

        self._thietlapstyle()

        self.vars = {
            "sudungkynang": tk.BooleanVar(),
            "gomquai": tk.BooleanVar(),
            "vebanrac": tk.BooleanVar(),
            "theosau": tk.BooleanVar(),
            "todoitudong": tk.BooleanVar(),
            "timmuctieu": tk.BooleanVar(),
            "chidanhnguoichoi": tk.BooleanVar(),
            "uutienmaoson": tk.BooleanVar(),
            "bufftoanbang": tk.BooleanVar(),
            "khaikhoang": tk.BooleanVar(),
            "daobaodo": tk.BooleanVar(),
            "chientruong": tk.BooleanVar(),
            "chantangcap": tk.BooleanVar(),
            "khoangcachtheosau": tk.DoubleVar(value = 9.0),
            "bankinhdiemdanh": tk.DoubleVar(value = 18.0),
            "khoangcachtamxa": tk.DoubleVar(value = KHOANGCACHSUDUNGKYNANGTAMXA),
            "phantramnoiluckhaithien": tk.DoubleVar(value = PHANTRAMNOILUCKHAITHIENTICHDIA),
            "diemdanhxungquanh": tk.BooleanVar(),
            "trieuhoibaothu": tk.BooleanVar(),
            "sudungkynangbaothu": tk.BooleanVar(),
            "tranhvungcam": tk.BooleanVar(value = True),
            "dilotrinhkhacbando": tk.BooleanVar(value = True),
            "giukhoangcachketancong": tk.BooleanVar(),
            "giukhoangcachchimuctieupk": tk.BooleanVar(value = True),
            "taphoa": tk.BooleanVar(),
            "timmuctieuchung": tk.BooleanVar(value = True),
            "khoangcachgiuketancong": tk.DoubleVar(value = KHOANGCACHGIUKETANCONG),
            "tutimduongtheosau": tk.BooleanVar(),
            "doidotrieuhoi": tk.BooleanVar(),
        }
        # Phẩm chất (màu tên) vật phẩm dưới đất được nhặt: {mã phẩm chất: biến}
        self.vars_phamchat = {ma: tk.BooleanVar() for ma in PHAMCHATVATPHAM_MAP}

        # Nhịp lệnh dùng chung mọi nhân vật (không theo nhân vật đang chọn nên không đồng bộ trong update_ui)
        cauhinhdieuphoi = taicauhinhdieuphoi()
        # {kênh: {is_xoayvong, nghitoithieu, nghitoida}}, kênh lệnh thêm nhuongkhiranh
        self.vars_dieuphoi = {
            kenh: {k: (tk.BooleanVar if k.startswith("is_") else tk.DoubleVar)(value = v) for k, v in cauhinhdieuphoi[kenh].items()}
            for kenh in (KENH_LENH, KENH_DICHUYEN)
        }

        self._taodanhsachnhanvat()
        self._taothanhtrangthai()

        # (canvas, thanh cuộn, khung nội dung, id khung trong canvas) của từng tab, xem _taotab
        self._tabcuons = []
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill = tk.BOTH, expand = True, padx = 8, pady = (0, 8))

        self._taotabchiendau(self._taotab(notebook, "Chiến đấu"))
        self._taotabfarm(self._taotab(notebook, "Farm & Lộ trình"))
        self._taotabmuctieutodoi(self._taotab(notebook, "Mục tiêu & Tổ đội"))
        self._taotabtuido(self._taotab(notebook, "Túi đồ"))
        self._taotabnhiemvu(self._taotab(notebook, "Nhiệm vụ"))
        if self.dangnhap is not None:
            self._taotabdangnhap(self._taotab(notebook, "Đăng nhập"))
        if HIEN_TUYCHON_CHUADUNG:
            self._taotabkhac(self._taotab(notebook, "Khác"))

        # Bấm ra chỗ khác (không phải ô nhập) thì bỏ focus ô đang sửa -> FocusOut áp dụng số vừa nhập
        self.root.bind_all("<Button-1>", self._bofocusokhibamrangoai, add = "+")
        self.root.bind_all("<MouseWheel>", self._cuonbangconlan, add = "+")

        self.update_ui()

    # ------------------------------------------------------------------ Bố cục

    def _thietlapstyle(self):
        style = ttk.Style(self.root)
        # Đổi font mặc định của cả tk lẫn ttk (ttk dùng các named font, option_add không đổi được)
        for tenfont in ("TkDefaultFont", "TkTextFont", "TkHeadingFont", "TkMenuFont", "TkFixedFont"):
            try:
                tkfont.nametofont(tenfont).configure(family = FONTCHU, size = COCHU)
            except tk.TclError:
                pass
        self.root.option_add("*Font", (FONTCHU, COCHU))
        fontthuong = tkfont.Font(family = FONTCHU, size = COCHU)
        style.configure("Treeview", rowheight = fontthuong.metrics("linespace") + 8)
        style.configure("Treeview.Heading", font = (FONTCHU, COCHU, "bold"))
        # Tk 8.6.9 trên Windows: style mặc định của Treeview ghi đè màu chữ / nền của tag (dòng tô màu không lên). Bỏ các mục
        # ("!disabled", "!selected") trong style.map cho tag được dùng màu của nó, dòng đang chọn vẫn tô màu chọn
        for tuychon in ("foreground", "background"):
            style.map("Treeview", **{tuychon: [m for m in style.map("Treeview", query_opt = tuychon) if m[:2] != ("!disabled", "!selected")]})
        style.configure("TNotebook.Tab", padding = (12, 4))
        style.configure("TLabelframe.Label", font = (FONTCHU, COCHU, "bold"))
        style.configure("Phu.TLabel", foreground = MAUCHU_PHU)
        style.configure("Tieude.TLabel", font = (FONTCHU, COCHU + 1, "bold"))
        # Nhãn phím tắt kiểu "phím bấm": nền xám nhạt, chữ nhỏ
        style.configure("Phim.TLabel", font = (FONTCHU, COCHU - 2), foreground = "#3b3b3b", background = "#e8ebf0", padding = (6, 1))

    def _taodanhsachnhanvat(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill = tk.X, padx = 8, pady = (8, 4))

        # Cột "hwnd" ẩn đi (vẫn dùng làm khoá), chỉ hiện thông tin dễ đọc
        columns = ("hwnd", "name", "hp", "mp", "map", "status", "nganluong", "nganluonggio")
        self.tree = ttk.Treeview(frame, columns = columns, displaycolumns = columns[1:], show = "headings", height = 5, selectmode = "browse")
        for col, text, width, anchor in (
                ("name", "Nhân vật", 100, tk.W),
                ("hp", "Máu", 45, tk.CENTER),
                ("mp", "Nội lực", 55, tk.CENTER),
                ("map", "Bản đồ", 95, tk.W),
                ("status", "Trạng thái", 105, tk.CENTER),
                ("nganluong", "Ngân lượng", 85, tk.E),
                ("nganluonggio", "/giờ", 55, tk.E)):
            self.tree.heading(col, text = text)
            self.tree.column(col, width = self._px(width), anchor = anchor, stretch = col in ("name", "map"))
        # Màu từng dòng: chết xám, tạm ngưng nền vàng, máu dưới NGUONGMAUTHAP đỏ
        self.tree.tag_configure("chet", foreground = "#8a8a8a")
        self.tree.tag_configure("tamngung", background = "#fff4cc")
        self.tree.tag_configure("mauthap", foreground = MAUCHU_DO)

        scrollbar = ttk.Scrollbar(frame, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = scrollbar.set)
        self.tree.pack(side = tk.LEFT, fill = tk.X, expand = True)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._capnhatbangdieukhien())

    def _taothanhtrangthai(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill = tk.X, padx = 10, pady = (0, 6))
        self.lbl_dangdieukhien = ttk.Label(frame, text = "Chưa có nhân vật", style = "Tieude.TLabel")
        self.lbl_dangdieukhien.pack(anchor = tk.W)
        self.lbl_vitri = ttk.Label(frame, text = "", style = "Phu.TLabel")
        self.lbl_vitri.pack(anchor = tk.W)

        # Dòng cảnh báo tạm ngưng (chỉ hiện khi phát hiện người chơi ẩn thân) + nút bật lại
        self.frame_tamngung = tk.Frame(frame, bg = "#fde8e8", highlightbackground = MAUCHU_DO, highlightthickness = 1)
        self.lbl_tamngung = tk.Label(self.frame_tamngung, text = "", fg = MAUCHU_DO, bg = "#fde8e8", justify = tk.LEFT,
                                     anchor = tk.W, wraplength = self._px(300), font = (FONTCHU, COCHU, "bold"))
        self.lbl_tamngung.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = 6, pady = 4)

        def on_tieptuchoatdong():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "tieptuchoatdong"

        ttk.Button(self.frame_tamngung, text = "Bật lại", command = on_tieptuchoatdong).pack(side = tk.RIGHT, padx = 6, pady = 4)

    def _px(self, sopixel):
        return int(sopixel * self._heso)

    def _taotab(self, notebook, tieude):
        # Nội dung tab nằm trong Canvas để cuộn được khi màn hình thấp (vd máy ảo 768px).
        # Khung trong cao ít nhất bằng Canvas để các ô giãn (fill BOTH, expand) vẫn lấp đầy khi đủ chỗ
        vo = ttk.Frame(notebook)
        notebook.add(vo, text = tieude)
        canvas = tk.Canvas(vo, highlightthickness = 0, borderwidth = 0, background = ttk.Style(self.root).lookup("TFrame", "background"))
        thanhcuon = ttk.Scrollbar(vo, orient = tk.VERTICAL, command = canvas.yview)
        canvas.configure(yscrollcommand = thanhcuon.set)
        canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        frame = ttk.Frame(canvas, padding = 8)
        idkhung = canvas.create_window((0, 0), window = frame, anchor = tk.NW)
        self._tabcuons.append((canvas, thanhcuon, frame, idkhung))
        canvas.bind("<Configure>", lambda e: self._capnhatcuontab(canvas, thanhcuon, frame, idkhung))
        return frame

    def _capnhatcuontab(self, canvas, thanhcuon, frame, idkhung):
        chieurong, chieucao = canvas.winfo_width(), canvas.winfo_height()
        if chieurong <= 1:
            return
        cancao = frame.winfo_reqheight()
        is_cancuon = cancao > chieucao
        canvas.itemconfigure(idkhung, width = chieurong, height = max(cancao, chieucao))
        canvas.configure(scrollregion = (0, 0, chieurong, max(cancao, chieucao)))
        if is_cancuon and not thanhcuon.winfo_ismapped():
            thanhcuon.pack(side = tk.RIGHT, fill = tk.Y, before = canvas)
        elif not is_cancuon and thanhcuon.winfo_ismapped():
            thanhcuon.pack_forget()
            canvas.yview_moveto(0)

    def _cuonbangconlan(self, event):
        # Con lăn chuột cuộn tab đang hiện; ô tự cuộn được (ô nhập nhiều dòng, danh sách) thì để nó tự xử lý
        if isinstance(event.widget, str) or isinstance(event.widget, (tk.Text, tk.Listbox, ttk.Treeview)):
            return
        for canvas, thanhcuon, frame, idkhung in self._tabcuons:
            if thanhcuon.winfo_ismapped() and canvas.winfo_ismapped() and str(event.widget).startswith(str(canvas)):
                canvas.yview_scroll(int(-event.delta / 120) or (-1 if event.delta > 0 else 1), "units")
                return

    def _taonhom(self, parent, tieude):
        nhom = ttk.LabelFrame(parent, text = tieude, padding = (8, 4))
        nhom.pack(fill = tk.X, pady = (0, 6))
        nhom.columnconfigure(0, weight = 1)
        return nhom

    def _bofocusokhibamrangoai(self, event):
        # Danh sách thả xuống của Combobox là widget nội bộ của Tk (event.widget là chuỗi): lấy focus khỏi nó thì Tk huỷ luôn lựa chọn
        if isinstance(event.widget, str) or isinstance(event.widget, tk.Listbox):
            return
        if not isinstance(event.widget, (tk.Entry, ttk.Entry, tk.Text, tk.Spinbox)):
            try:
                self.root.focus_set()
            except tk.TclError:
                pass

    def _ganspinboxapdung(self, spin, on_change):
        # Enter: áp dụng rồi bỏ focus (ô hết bị khoá, update_ui đồng bộ lại số thật). Esc: bỏ sửa, lấy lại số cũ
        # Nhớ nhân vật lúc bắt đầu sửa: bấm chọn nhân vật khác làm ô mất focus sau khi đã đổi lựa chọn,
        # nếu lấy nhân vật đang chọn lúc đó thì số vừa nhập bị áp sang nhân vật mới
        boqua = {"focusout": False, "hwnd": None}

        def on_focusin(event):
            boqua["hwnd"] = self.get_selected_hwnd()

        def on_enter(event):
            on_change(boqua["hwnd"])
            boqua["focusout"] = True
            self.root.focus_set()
            return "break"

        def on_escape(event):
            boqua["focusout"] = True
            self.root.focus_set()
            return "break"

        def on_focusout(event):
            if boqua["focusout"]:
                boqua["focusout"] = False
            else:
                on_change(boqua["hwnd"])

        spin.bind("<FocusIn>", on_focusin)
        spin.bind("<Return>", on_enter)
        spin.bind("<KP_Enter>", on_enter)
        spin.bind("<Escape>", on_escape)
        spin.bind("<FocusOut>", on_focusout)

    def _create_check(self, parent, text, variable, cmd_name = None, phimtat = ""):
        def on_click():
            hwnd = self.get_selected_hwnd()
            if hwnd and cmd_name:
                self.command_dict[hwnd] = cmd_name

        dong = parent.grid_size()[1]
        ttk.Checkbutton(parent, text = text, variable = variable, command = on_click).grid(row = dong, column = 0, sticky = tk.W, pady = 1)
        if phimtat:
            ttk.Label(parent, text = phimtat, style = "Phim.TLabel").grid(row = dong, column = 1, sticky = tk.E, padx = (8, 0))

    def _taotabchiendau(self, tab):
        nhom = self._taonhom(tab, "Tự động")
        self._create_check(nhom, "Tự động sử dụng kỹ năng", self.vars["sudungkynang"], "battat_tudongsudungkynang", "Ctrl+F")
        self._create_check(nhom, "Tự tìm mục tiêu", self.vars["timmuctieu"], "battat_tudongtimkiemmuctieu")
        self._create_check(nhom, "Tự động gom quái", self.vars["gomquai"], "battat_tudonggomquai", "Ctrl+Alt+Shift+G")

        nhom = self._taonhom(tab, "Chọn mục tiêu")
        self._create_check(nhom, "Chỉ đánh người chơi", self.vars["chidanhnguoichoi"], "toggle_chidanhnguoichoi", "Ctrl+D / Ctrl+A")
        self._create_check(nhom, "Ưu tiên bảo thú Mao Sơn", self.vars["uutienmaoson"], "battat_uutienbaothukynangtrieuhoi", "Ctrl+Alt+S")
        self._create_check(nhom, "Chế độ buff toàn bang", self.vars["bufftoanbang"], "battat_chedobufftoanbang", "Ctrl+Alt+Shift+N")
        self._create_check(nhom, "Chặn tăng cấp độ", self.vars["chantangcap"], "battat_chantangcapdo", "Ctrl+Alt+Shift+C")
        self._create_check(nhom, "Tập hỏa: đánh mục tiêu của người mình theo sau (cùng máy)", self.vars["taphoa"], "battat_taphoa")
        self._create_check(nhom, "Hết mục tiêu thì tìm tới mục tiêu nhân vật khác cùng máy thấy", self.vars["timmuctieuchung"], "battat_timmuctieuchung")

        # Giữ khoảng cách với đối tượng đang đánh mình (ra đòn và quay mặt về mình): lùi ra, chỉ buff / hồi máu, bỏ chiêu đánh
        nhom = self._taonhom(tab, "Giữ khoảng cách")
        self._create_check(nhom, "Lùi ra khỏi kẻ đang tấn công mình (chỉ buff, không đánh)", self.vars["giukhoangcachketancong"], "battat_giukhoangcachketancong")
        self._create_check(nhom, "Chỉ với mục tiêu PK (bỏ tick để thử với cả quái)", self.vars["giukhoangcachchimuctieupk"], "battat_giukhoangcachchimuctieupk")
        hanggiukhoangcach = ttk.Frame(nhom)
        hanggiukhoangcach.grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.W)
        ttk.Label(hanggiukhoangcach, text = "Giữ cách kẻ tấn công ít nhất:").pack(side = tk.LEFT)

        def on_giukhoangcach_change(hwnd = None):
            hwnd = hwnd or self.get_selected_hwnd()
            if hwnd:
                try:
                    self.command_dict[hwnd] = f"set_khoangcachgiuketancong:{self.vars['khoangcachgiuketancong'].get()}"
                except tk.TclError:
                    pass

        self.spin_khoangcachgiuketancong = ttk.Spinbox(hanggiukhoangcach, from_ = 2.0, to = 15.0, increment = 1.0, width = 5,
                                                       textvariable = self.vars["khoangcachgiuketancong"], command = on_giukhoangcach_change)
        self.spin_khoangcachgiuketancong.pack(side = tk.LEFT, padx = 4)
        self._ganspinboxapdung(self.spin_khoangcachgiuketancong, on_giukhoangcach_change)
        ttk.Label(hanggiukhoangcach, text = "ô", style = "Phu.TLabel").pack(side = tk.LEFT)

        # Nhóm & Bảo thú nằm chung tab Chiến đấu
        self._taotabnhom(tab)

        self._taonhomnhiplenh(tab)

    def _taonhomnhiplenh(self, tab):
        nhom = self._taonhom(tab, "Nhịp lệnh (chung mọi nhân vật)")

        def on_apdung(*args):
            try:
                cauhinh = chuanhoacauhinhdieuphoi({kenh: {k: v.get() for k, v in vars_.items()} for kenh, vars_ in self.vars_dieuphoi.items()})
            except tk.TclError:
                # Ô số đang nhập dở/sai: lấy lại số đang dùng
                cauhinh = taicauhinhdieuphoi()
            # Hiện lại số đã chuẩn hoá (vd. tối thiểu > tối đa thì đổi chỗ)
            for kenh, vars_ in self.vars_dieuphoi.items():
                for k, v in vars_.items():
                    v.set(cauhinh[kenh][k])
            if self.dieuphoi_trangthai is not None:
                self.dieuphoi_trangthai["cauhinh"] = cauhinh
            luucauhinhdieuphoi(cauhinh)

        self._apdungdieuphoi = on_apdung

        for kenh, tieude in ((KENH_LENH, "Xoay vòng chiêu có mục tiêu giữa các nhân vật"), (KENH_DICHUYEN, "Lần lượt bắt đầu di chuyển")):
            vars_ = self.vars_dieuphoi[kenh]
            dong = nhom.grid_size()[1]
            ttk.Checkbutton(nhom, text = tieude, variable = vars_["is_xoayvong"],
                            command = on_apdung).grid(row = dong, column = 0, sticky = tk.W, pady = 1)
            if kenh == KENH_LENH:
                ttk.Label(nhom, text = "Ctrl+Alt+Shift+F", style = "Phu.TLabel").grid(row = dong, column = 1, sticky = tk.E, padx = (8, 0))

            hangnghi = ttk.Frame(nhom)
            hangnghi.grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.W, padx = (22, 0), pady = (0, 2))
            ttk.Label(hangnghi, text = "Mỗi nhân vật giữ lượt từ" if kenh == KENH_LENH else "Cách nhau từ").pack(side = tk.LEFT)
            for khoa, chu in (("nghitoithieu", "đến"), ("nghitoida", "giây")):
                spin = ttk.Spinbox(hangnghi, from_ = 0.0, to = 30.0 if kenh == KENH_LENH else 5.0, increment = 0.01, width = 5, format = "%.2f",
                                   textvariable = vars_[khoa], command = on_apdung)
                spin.pack(side = tk.LEFT, padx = 4)
                self._ganspinboxapdung(spin, on_apdung)
                ttk.Label(hangnghi, text = chu, style = "Phu.TLabel" if chu == "giây" else "TLabel").pack(side = tk.LEFT)

            if "nhuongkhiranh" in vars_:
                hangranh = ttk.Frame(nhom)
                hangranh.grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.W, padx = (22, 0), pady = (0, 2))
                ttk.Label(hangranh, text = "Rảnh quá").pack(side = tk.LEFT)
                spin = ttk.Spinbox(hangranh, from_ = 0.1, to = 5.0, increment = 0.05, width = 5, format = "%.2f",
                                   textvariable = vars_["nhuongkhiranh"], command = on_apdung)
                spin.pack(side = tk.LEFT, padx = 4)
                self._ganspinboxapdung(spin, on_apdung)
                ttk.Label(hangranh, text = "giây thì nhường lượt", style = "Phu.TLabel").pack(side = tk.LEFT)

    def battat_xoayvongchieu(self):
        # Phím tắt Ctrl+Alt+Shift+F (gọi từ luồng phím tắt qua root.after): bật / tắt xoay vòng chiêu chung mọi nhân vật
        bien = self.vars_dieuphoi[KENH_LENH]["is_xoayvong"]
        bien.set(not bien.get())
        self._apdungdieuphoi()
        phatam("Bật xoay vòng chiêu" if bien.get() else "Tắt xoay vòng chiêu", is_block = False)

    def _taotabmuctieutodoi(self, tab):
        # Trên cùng là các ô cấu hình ngắn (tầm đánh), các bảng để dưới; bật / tắt tổ đội nằm ngay trên bảng nhóm tổ đội
        nhom = self._taonhom(tab, "Tầm đánh")
        hangtamxa = ttk.Frame(nhom)
        hangtamxa.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)
        ttk.Label(hangtamxa, text = "Khoảng cách dùng kỹ năng tầm xa:").pack(side = tk.LEFT)

        def on_tamxa_change(hwnd = None):
            hwnd = hwnd or self.get_selected_hwnd()
            if hwnd:
                try:
                    self.command_dict[hwnd] = f"set_khoangcachsudungkynangtamxa:{self.vars['khoangcachtamxa'].get()}"
                except tk.TclError:
                    pass

        self.spin_khoangcachtamxa = ttk.Spinbox(hangtamxa, from_ = 4.0, to = 30.0, increment = 1.0, width = 5,
                                                textvariable = self.vars["khoangcachtamxa"], command = on_tamxa_change)
        self.spin_khoangcachtamxa.pack(side = tk.LEFT, padx = 4)
        self._ganspinboxapdung(self.spin_khoangcachtamxa, on_tamxa_change)
        ttk.Label(hangtamxa, text = "ô", style = "Phu.TLabel").pack(side = tk.LEFT)

        hangkhaithien = ttk.Frame(nhom)
        hangkhaithien.grid(row = 1, column = 0, columnspan = 2, sticky = tk.W)
        ttk.Label(hangkhaithien, text = "Lướt (Khai Thiên Tịch Địa / Đằng Vân Giá Vũ) khi nội lực trên:").pack(side = tk.LEFT)

        def on_khaithien_change(hwnd = None):
            hwnd = hwnd or self.get_selected_hwnd()
            if hwnd:
                try:
                    self.command_dict[hwnd] = f"set_phantramnoiluckhaithientichdia:{self.vars['phantramnoiluckhaithien'].get()}"
                except tk.TclError:
                    pass

        self.spin_phantramnoiluckhaithien = ttk.Spinbox(hangkhaithien, from_ = 0.0, to = 100.0, increment = 5.0, width = 5,
                                                        textvariable = self.vars["phantramnoiluckhaithien"], command = on_khaithien_change)
        self.spin_phantramnoiluckhaithien.pack(side = tk.LEFT, padx = 4)
        self._ganspinboxapdung(self.spin_phantramnoiluckhaithien, on_khaithien_change)
        ttk.Label(hangkhaithien, text = "%", style = "Phu.TLabel").pack(side = tk.LEFT)

        self._taotabtodoi(tab)

        # Danh sách mục tiêu theo từng nhân vật (bot gửi lên shared_data, sửa ở đây là gửi lệnh set_danhsachmuctieu xuống ngay)
        nhom = self._taonhom(tab, "Danh sách mục tiêu (của nhân vật đang chọn)")
        nhom.columnconfigure(0, weight = 1, uniform = "muctieu")
        nhom.columnconfigure(1, weight = 1, uniform = "muctieu")
        self.tree_muctieus = {}
        for cot, (khoa, tieude, mau, phimtat) in enumerate((("tancong", "⚔️ Tấn công (trống = đánh hết)", MAUCHU_XANH, "Ctrl+C thêm · Ctrl+Alt+C xoá"),
                                                            ("boqua", "🚫 Bỏ qua", MAUCHU_LUC, "Ctrl+X thêm · Ctrl+Alt+X xoá · ~tên = tên chứa"))):
            o_ = ttk.Frame(nhom)
            o_.grid(row = 0, column = cot, sticky = tk.NSEW, padx = (0, 8) if cot == 0 else (0, 0))
            khung = ttk.Frame(o_)
            khung.pack(fill = tk.BOTH, expand = True)
            tree = ttk.Treeview(khung, columns = ("ten",), show = "headings", height = 7, selectmode = "extended")
            tree.heading("ten", text = tieude)
            tree.column("ten", width = self._px(250), anchor = tk.W)
            tree.tag_configure("ten", foreground = mau)
            thanhcuon = ttk.Scrollbar(khung, orient = tk.VERTICAL, command = tree.yview)
            tree.configure(yscrollcommand = thanhcuon.set)
            tree.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
            thanhcuon.pack(side = tk.RIGHT, fill = tk.Y)
            tree.bind("<Delete>", lambda e, k = khoa: self._xoamuctieu(k))
            hangnut = ttk.Frame(o_)
            hangnut.pack(fill = tk.X, pady = (4, 0))
            ttk.Button(hangnut, text = "Thêm", command = lambda k = khoa: self._themmuctieu(k)).pack(side = tk.LEFT, padx = (0, 4))
            ttk.Button(hangnut, text = "Xoá", command = lambda k = khoa: self._xoamuctieu(k)).pack(side = tk.LEFT)
            ttk.Label(o_, text = phimtat, style = "Phim.TLabel").pack(anchor = tk.W, pady = (4, 0))
            self.tree_muctieus[khoa] = tree

        hang = ttk.Frame(nhom)
        hang.grid(row = 1, column = 0, columnspan = 2, sticky = tk.EW, pady = (8, 0))
        self.lbl_trangthaimuctieu = tk.Label(hang, text = "", fg = MAUCHU_PHU, anchor = tk.W)
        self.lbl_trangthaimuctieu.pack(side = tk.LEFT, fill = tk.X, expand = True)
        ttk.Button(hang, text = "Áp dụng 2 danh sách này cho tất cả nhân vật", command = lambda: self._guidanhsachmuctieu(is_tatca = True)).pack(side = tk.RIGHT)
        # (hwnd, {"tancong": [...], "boqua": [...]}) đang hiện
        self._muctieudanghien = (None, {"tancong": [], "boqua": []})

        # Mục tiêu bot tự bỏ qua theo id (bị chặn, kẹt tường, đánh không trúng, đi tới mãi không thấy): xoá khi bỏ nhầm để đánh lại ngay
        nhom = self._taonhom(tab, "Đang tự bỏ qua (của nhân vật đang chọn)")
        nhom.columnconfigure(0, weight = 1)
        khung = ttk.Frame(nhom)
        khung.grid(row = 0, column = 0, columnspan = 2, sticky = tk.NSEW)
        self.tree_muctieuboqua = ttk.Treeview(khung, columns = ("ten", "id", "lydo", "conlai"), show = "headings", height = 5, selectmode = "extended")
        for cot, tieude, rong, canh in (("ten", "Tên", 180, tk.W), ("id", "ID", 90, tk.W), ("lydo", "Lý do", 170, tk.W), ("conlai", "Còn lại", 70, tk.E)):
            self.tree_muctieuboqua.heading(cot, text = tieude)
            self.tree_muctieuboqua.column(cot, width = self._px(rong), anchor = canh)
        thanhcuon = ttk.Scrollbar(khung, orient = tk.VERTICAL, command = self.tree_muctieuboqua.yview)
        self.tree_muctieuboqua.configure(yscrollcommand = thanhcuon.set)
        self.tree_muctieuboqua.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        thanhcuon.pack(side = tk.RIGHT, fill = tk.Y)
        self.tree_muctieuboqua.bind("<Delete>", lambda e: self._xoamuctieuboqua())
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 1, column = 0, columnspan = 2, sticky = tk.W, pady = (4, 0))
        ttk.Button(hangnut, text = "Xoá", command = self._xoamuctieuboqua).pack(side = tk.LEFT, padx = (0, 4))
        ttk.Button(hangnut, text = "Xoá hết", command = lambda: self._xoamuctieuboqua(is_tatca = True)).pack(side = tk.LEFT)
        ttk.Label(hangnut, text = "Xoá = bot thôi bỏ qua, đánh lại ngay", style = "Phu.TLabel").pack(side = tk.LEFT, padx = (8, 0))

    def _hiendanhsachmuctieu(self, hwnd, danhsachs):
        for khoa, tree in self.tree_muctieus.items():
            dangchon = set(tree.selection())
            tree.delete(*tree.get_children())
            for ten in danhsachs[khoa]:
                tree.insert("", tk.END, iid = ten, values = (ten,), tags = ("ten",))
            tree.selection_set([t for t in dangchon if tree.exists(t)])
        self._muctieudanghien = (hwnd, {k: list(v) for k, v in danhsachs.items()})

    def _guidanhsachmuctieu(self, danhsachs = None, is_tatca = False):
        # Gửi 2 danh sách cho nhân vật đang chọn (hoặc mọi nhân vật), hiện ngay, chờ bot nhận (_danhsachmuctieudanglu) khỏi bị nạp lại cũ
        hwnd = self.get_selected_hwnd()
        danhsachs = danhsachs or self._muctieudanghien[1]
        hwnds = list(self.shared_data.keys()) if is_tatca else ([hwnd] if hwnd else [])
        if not hwnds:
            self.lbl_trangthaimuctieu.config(text = "Chưa có nhân vật", fg = MAUCHU_DO)
            return
        lenh = "set_danhsachmuctieu:" + json.dumps({"tancong": danhsachs["tancong"], "boqua": danhsachs["boqua"]}, ensure_ascii = False)
        for h in hwnds:
            self.command_dict[h] = lenh
        self._danhsachmuctieudanglu = (hwnd, list(danhsachs["tancong"]), list(danhsachs["boqua"]), time.time())
        self._hiendanhsachmuctieu(hwnd, danhsachs)
        self.lbl_trangthaimuctieu.config(text = f"Đã áp dụng cho {len(hwnds)} nhân vật" if is_tatca else "Đã lưu cho nhân vật đang chọn", fg = MAUCHU_LUC)

    def _themmuctieu(self, khoa):
        # Hộp thoại nhiều dòng: mỗi dòng 1 tên; dán cả tên kèm cấp ("Sói ( Cấp 10)") thì bỏ phần cấp giống khi thêm bằng phím tắt
        kq = self._hopthoaituido("Thêm mục tiêu tấn công" if khoa == "tancong" else "Thêm mục tiêu bỏ qua", [("tens", "Tên mục tiêu", None)], {},
                                 lambda k: None if k["tens"].strip() else "Nhập ít nhất 1 tên", nhieudongs = ("tens",))
        if not kq:
            return
        danhsachs = {k: list(v) for k, v in self._muctieudanghien[1].items()}
        for dong in kq["tens"].splitlines():
            ten = re.split(r"\(\s*[Cc]ấp", dong)[0].strip()
            if ten and ten not in danhsachs[khoa]:
                danhsachs[khoa].append(ten)
        danhsachs[khoa].sort()
        self._guidanhsachmuctieu(danhsachs)

    def _xoamuctieu(self, khoa):
        chon = set(self.tree_muctieus[khoa].selection())
        if not chon:
            return
        danhsachs = {k: list(v) for k, v in self._muctieudanghien[1].items()}
        danhsachs[khoa] = [t for t in danhsachs[khoa] if t not in chon]
        self._guidanhsachmuctieu(danhsachs)

    def _xoamuctieuboqua(self, is_tatca = False):
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            return
        if is_tatca:
            self.command_dict[hwnd] = "xoa_muctieuboqua:all"
            self.tree_muctieuboqua.delete(*self.tree_muctieuboqua.get_children())
            return
        chon = self.tree_muctieuboqua.selection()
        if not chon:
            return
        self.command_dict[hwnd] = "xoa_muctieuboqua:" + json.dumps([int(iid) for iid in chon])
        self.tree_muctieuboqua.delete(*chon)

    def _capnhatmuctieuboqua(self, info):
        # Giữ dòng đang chọn khi làm mới (iid = id đối tượng)
        tree = self.tree_muctieuboqua
        muctieus = info.get("_muctieuboquas") or []
        dangchon = set(tree.selection())
        idmois = {str(muc["id"]) for muc in muctieus}
        for iid in tree.get_children():
            if iid not in idmois:
                tree.delete(iid)
        for muc in muctieus:
            iid = str(muc["id"])
            giatri = (muc["ten"] or "?", hex(muc["id"]), muc["lydo"], f"{muc['conlai']}s")
            if tree.exists(iid):
                tree.item(iid, values = giatri)
            else:
                tree.insert("", tk.END, iid = iid, values = giatri)
        tree.selection_set([t for t in dangchon if tree.exists(t)])

    def _capnhatdanhsachmuctieu(self, hwnd, info):
        tancongs = list(info.get("_tenmuctieutancongs") or [])
        boquas = list(info.get("_tenmuctieukhongtancongs") or [])
        # Bản cũ của bot gửi chuỗi nối bằng ", "
        if isinstance(info.get("_tenmuctieutancongs"), str):
            tancongs = [t.strip() for t in info["_tenmuctieutancongs"].split(",") if t.strip()]
        if isinstance(info.get("_tenmuctieukhongtancongs"), str):
            boquas = [t.strip() for t in info["_tenmuctieukhongtancongs"].split(",") if t.strip()]

        danglu = self._danhsachmuctieudanglu
        if danglu:
            if danglu[0] == hwnd and (danglu[1], danglu[2]) != (tancongs, boquas) and time.time() - danglu[3] < 3.:
                return  # bot chưa nhận lệnh lưu, giữ nguyên nội dung vừa lưu
            self._danhsachmuctieudanglu = None

        dahien = self._muctieudanghien
        if dahien[0] != hwnd:
            self.lbl_trangthaimuctieu.config(text = "")
        elif (dahien[1]["tancong"], dahien[1]["boqua"]) == (tancongs, boquas):
            return
        self._hiendanhsachmuctieu(hwnd, {"tancong": tancongs, "boqua": boquas})

    def _taotabfarm(self, tab):
        nhom = self._taonhom(tab, "Chế độ")
        self._create_check(nhom, "Tự động farm & về bán rác", self.vars["vebanrac"], "battat_tudongvebanrac", "Ctrl+Alt+Shift+H")
        self._create_check(nhom, "Tránh vùng cấm", self.vars["tranhvungcam"], "battat_tranhvungcam")
        self._create_check(nhom, "Di chuyển theo lộ trình điểm đánh", self.vars["diemdanhxungquanh"], "battat_tudongdichuyendiemdanhxungquanh", "Ctrl+Alt+Shift+P")
        # Tắt: chỉ đi các điểm đánh cùng bản đồ đang đứng (vd phó bản Phong Yêu Kính mượn ID bản đồ ngoài)
        self._create_check(nhom, "Đi tới điểm đánh ở bản đồ khác", self.vars["dilotrinhkhacbando"], "battat_dilotrinhkhacbando")

        # Bán kính quanh mỗi điểm đánh: quái xa hơn mọi điểm đánh thì không đánh/gom
        hangbankinh = ttk.Frame(nhom)
        hangbankinh.grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.W, padx = (22, 0), pady = (0, 2))
        ttk.Label(hangbankinh, text = "Chỉ đánh quái cách điểm đánh tối đa:").pack(side = tk.LEFT)

        def on_bankinh_change(hwnd = None):
            hwnd = hwnd or self.get_selected_hwnd()
            if hwnd:
                try:
                    self.command_dict[hwnd] = f"set_bankinhdiemdanh:{self.vars['bankinhdiemdanh'].get()}"
                except tk.TclError:
                    pass

        self.spin_bankinhdiemdanh = ttk.Spinbox(hangbankinh, from_ = 3.0, to = 40.0, increment = 1.0, width = 5,
                                                textvariable = self.vars["bankinhdiemdanh"], command = on_bankinh_change)
        self.spin_bankinhdiemdanh.pack(side = tk.LEFT, padx = 4)
        self._ganspinboxapdung(self.spin_bankinhdiemdanh, on_bankinh_change)
        ttk.Label(hangbankinh, text = "ô", style = "Phu.TLabel").pack(side = tk.LEFT)

        # Nhặt vật phẩm dưới đất có tên màu (xanh lam, vàng...) dù tên không nằm trong danh sách nhặt
        nhom = self._taonhom(tab, "Phẩm chất")
        hangphamchat = ttk.Frame(nhom)
        hangphamchat.grid(row = 0, column = 0, sticky = tk.W)
        ttk.Label(hangphamchat, text = "Nhặt đồ màu:").pack(side = tk.LEFT, padx = (0, 4))

        def on_phamchat():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "set_phamchatnhat:" + ",".join(str(ma) for ma, bien in self.vars_phamchat.items() if bien.get())

        for ma, ten in PHAMCHATVATPHAM_MAP.items():
            ttk.Checkbutton(hangphamchat, text = ten, variable = self.vars_phamchat[ma], command = on_phamchat).pack(side = tk.LEFT, padx = (0, 8))

        # Bấm 1 lần: bot gộp chồng và xếp vật phẩm theo tên trong từng túi; đang xếp thì bấm lại để dừng
        nhom = self._taonhom(tab, "Hành trang")

        def on_sapxephanhtrang():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "battat_sapxephanhtrang"

        self.btn_sapxephanhtrang = ttk.Button(nhom, text = "Sắp xếp hành trang", command = on_sapxephanhtrang)
        self.btn_sapxephanhtrang.grid(row = 0, column = 0, sticky = tk.W)
        ttk.Label(nhom, text = "Gộp chồng, xếp theo tên, dồn lên đầu từng túi", style = "Phu.TLabel").grid(row = 1, column = 0, sticky = tk.W, pady = (2, 0))

        # Đi tới bản đồ: bot tự phù (Chủ Dịch Trạm / Tân Thủ Tiên Cô), Hồi Thành Phù khi xa, chạy bộ từng bản đồ, tới nơi thì dừng.
        # Dòng "Bước tiếp theo" hiện cả bước của lộ trình điểm đánh / theo sau
        nhom = self._taonhom(tab, "Đi tới bản đồ")
        # Tên kèm cấp quái của bản đồ nếu file game có ghi (laycapquaibando), vd. "Tần Trường Thành 1 (51) – cấp 66~74"
        def _tenhienthi(idbando, ten):
            capquai = laycapquaibando(idbando)
            return f"{ten} ({idbando})" + (f" – cấp {capquai[0]}~{capquai[1]}" if capquai else "")
        self._idbandotheohienthi = {_tenhienthi(idbando, ten): idbando for idbando, (ten, _) in sorted(BANDOCONG_MAP.items(), key = lambda m: m[1][0] or "") if ten}
        self.str_bandocandi = tk.StringVar()
        self.cbo_bandocandi = ttk.Combobox(nhom, textvariable = self.str_bandocandi, values = list(self._idbandotheohienthi), state = "readonly", height = 20)
        self.cbo_bandocandi.grid(row = 0, column = 0, sticky = tk.EW)

        def on_ditoibando(idbando):
            hwnd = self.get_selected_hwnd()
            if hwnd and idbando is not None:
                self.command_dict[hwnd] = f"ditoibando:{idbando}"

        ttk.Button(nhom, text = "Đi", width = 5, command = lambda: on_ditoibando(self._idbandotheohienthi.get(self.str_bandocandi.get()))).grid(row = 0, column = 1, padx = (4, 0))
        ttk.Button(nhom, text = "Dừng", width = 6, command = lambda: on_ditoibando(0)).grid(row = 0, column = 2, padx = (4, 0))
        self.lbl_buocdichuyen = tk.Label(nhom, text = "Bước tiếp theo: -", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = 320)
        self.lbl_buocdichuyen.grid(row = 1, column = 0, columnspan = 3, sticky = tk.W, pady = (4, 0))

        # Lộ trình mẫu: chọn mẫu (của bất kỳ bản đồ nào) rồi Nạp, hoặc để bot Tự chọn mẫu chưa nhân vật nào dùng
        nhom = self._taonhom(tab, "Lộ trình mẫu")
        self.lbl_lotrinhmau = tk.Label(nhom, text = "Đang dùng: (tự đặt điểm)", fg = MAUCHU_PHU, anchor = tk.W)
        self.lbl_lotrinhmau.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W, pady = (0, 4))

        # Bảng mẫu: bản đồ đang đứng lên đầu (chữ xanh), "Đang dùng" = nhân vật cùng máy đang chạy mẫu đó,
        # "Ngân lượng/giờ" = thống kê 7 ngày của mọi nhân vật trên máy với mẫu đó (thongke_xq)
        self.tree_lotrinhmau = ttk.Treeview(nhom, columns = ("bando", "ten", "sodiem", "dangdung", "nlgio"), show = "headings", height = 6,
                                            selectmode = "browse")
        for col, text, width, anchor in (
                ("bando", "Bản đồ", 120, tk.W),
                ("ten", "Mẫu", 90, tk.W),
                ("sodiem", "Điểm", 45, tk.CENTER),
                ("dangdung", "Đang dùng", 140, tk.W),
                ("nlgio", "Ngân lượng/giờ", 115, tk.E)):
            self.tree_lotrinhmau.heading(col, text = text)
            self.tree_lotrinhmau.column(col, width = self._px(width), anchor = anchor, stretch = col in ("bando", "dangdung"))
        self.tree_lotrinhmau.tag_configure("bandohientai", foreground = MAUCHU_XANH)
        self.tree_lotrinhmau.grid(row = 1, column = 0, columnspan = 2, sticky = tk.EW)
        self.tree_lotrinhmau.bind("<Double-1>", lambda e: on_nap_lotrinhmau())
        self._lotrinhmaudanghien = None
        self._nlgiolotrinh_cache = (0., {})

        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 2, column = 0, columnspan = 2, sticky = tk.EW, pady = (4, 0))
        self.var_nguocchieu = tk.BooleanVar()
        # Lưu xuống bot (theo nhân vật) để Tự chọn / tự nạp mẫu khi chưa có điểm cũng đi theo chiều này, không chỉ khi bấm Nạp mẫu.
        # Vừa tích: (hwnd, giá trị, thời điểm) chờ bot nhận, update_ui không nạp lại giá trị cũ đè lên
        self._nguocchieuchoxacnhan = None

        def on_nguocchieu():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = f"set_nguocchieulotrinh:{1 if self.var_nguocchieu.get() else 0}"
                self._nguocchieuchoxacnhan = (hwnd, self.var_nguocchieu.get(), time.time())

        ttk.Checkbutton(hangnut, text = "Đi ngược chiều", variable = self.var_nguocchieu, command = on_nguocchieu).pack(side = tk.LEFT)

        def on_tuchon_lotrinhmau():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "tuchon_lotrinhmau"

        def on_nap_lotrinhmau(is_bosung = False):
            # Nạp mẫu: thay lộ trình đang có; Bổ sung: nối điểm của mẫu vào cuối lộ trình đang có (bỏ điểm trùng)
            hwnd = self.get_selected_hwnd()
            chon = self.tree_lotrinhmau.selection()
            if hwnd and chon:
                idbando, tenmau = chon[0].split("|", 1)
                lenh = "bosung_lotrinhmau" if is_bosung else "nap_lotrinhmau"
                self.command_dict[hwnd] = f"{lenh}:{idbando}|{tenmau}|{1 if self.var_nguocchieu.get() else 0}"

        ttk.Button(hangnut, text = "Tự chọn", command = on_tuchon_lotrinhmau).pack(side = tk.RIGHT)
        ttk.Button(hangnut, text = "Bổ sung", command = lambda: on_nap_lotrinhmau(True)).pack(side = tk.RIGHT, padx = (0, 4))
        ttk.Button(hangnut, text = "Nạp mẫu", command = on_nap_lotrinhmau).pack(side = tk.RIGHT, padx = (0, 4))

        hangluu = ttk.Frame(nhom)
        hangluu.grid(row = 3, column = 0, columnspan = 2, sticky = tk.EW, pady = (6, 2))
        ttk.Label(hangluu, text = "Lưu lộ trình hiện tại thành mẫu:").pack(side = tk.LEFT)
        self.str_tenmaumoi = tk.StringVar()

        def on_luu_lotrinhmau():
            hwnd = self.get_selected_hwnd()
            tenmau = self.str_tenmaumoi.get().strip()
            if hwnd and tenmau:
                self.command_dict[hwnd] = f"luu_lotrinhmau:{tenmau}"
                self.str_tenmaumoi.set("")

        ttk.Button(hangluu, text = "Lưu", width = 6, command = on_luu_lotrinhmau).pack(side = tk.RIGHT)
        ttk.Entry(hangluu, textvariable = self.str_tenmaumoi, width = 14).pack(side = tk.RIGHT, padx = 4)

        # Tự đề xuất: gom vị trí quái đã thấy trên bản đồ hiện tại thành vòng điểm đánh, lưu thành mẫu "Tự đề xuất"
        hangdexuat = ttk.Frame(nhom)
        hangdexuat.grid(row = 4, column = 0, columnspan = 2, sticky = tk.EW, pady = (2, 0))
        self.lbl_solanthayquai = ttk.Label(hangdexuat, text = "Đã thấy quái: -", style = "Phu.TLabel")
        self.lbl_solanthayquai.pack(side = tk.LEFT)

        def on_dexuat_lotrinhmau():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "dexuat_lotrinhmau"

        ttk.Button(hangdexuat, text = "Tự đề xuất", command = on_dexuat_lotrinhmau).pack(side = tk.RIGHT)
        ttk.Label(nhom, text = "Nhấp đúp một mẫu để nạp. Bản đồ đang đứng hiện chữ xanh ở đầu bảng.", style = "Phu.TLabel").grid(
            row = 5, column = 0, columnspan = 2, sticky = tk.W, pady = (4, 0))

        # Điểm đánh hiện tại: bảng, điểm đang đi tới tô xanh
        nhom = self._taonhom(tab, "Điểm đánh của nhân vật")
        nhom.pack_configure(fill = tk.BOTH, expand = True)
        nhom.rowconfigure(1, weight = 1)
        self.lbl_sodiem = ttk.Label(nhom, text = "Trống", style = "Phu.TLabel")
        self.lbl_sodiem.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)

        khungds = ttk.Frame(nhom)
        khungds.grid(row = 1, column = 0, columnspan = 2, sticky = tk.NSEW, pady = (2, 4))
        self.tree_diemdanh = ttk.Treeview(khungds, columns = ("stt", "x", "y", "bando"), show = "headings", height = 6, selectmode = "browse")
        for col, text, width, anchor in (("stt", "#", 40, tk.CENTER), ("x", "X", 60, tk.CENTER), ("y", "Y", 60, tk.CENTER), ("bando", "Bản đồ", 250, tk.W)):
            self.tree_diemdanh.heading(col, text = text)
            self.tree_diemdanh.column(col, width = self._px(width), anchor = anchor, stretch = col == "bando")
        self.tree_diemdanh.tag_configure("dangden", foreground = MAUCHU_XANH, font = (FONTCHU, COCHU, "bold"))
        thanhcuon = ttk.Scrollbar(khungds, orient = tk.VERTICAL, command = self.tree_diemdanh.yview)
        self.tree_diemdanh.configure(yscrollcommand = thanhcuon.set)
        self.tree_diemdanh.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        thanhcuon.pack(side = tk.RIGHT, fill = tk.Y)

        hangnhap = ttk.Frame(nhom)
        hangnhap.grid(row = 2, column = 0, columnspan = 2, sticky = tk.EW)
        self.str_nhapdiemdanh = tk.StringVar()

        def on_add_diemdanh():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                val = self.str_nhapdiemdanh.get()
                if val:
                    self.command_dict[hwnd] = f"them_diemdanh_nhaptay:{val}"
                    self.str_nhapdiemdanh.set("")

        def on_clear_diemdanh():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "botoanbo_diemdanhxungquanh"

        ttk.Button(hangnhap, text = "Xoá hết", command = on_clear_diemdanh).pack(side = tk.RIGHT)
        ttk.Button(hangnhap, text = "Thêm", width = 6, command = on_add_diemdanh).pack(side = tk.RIGHT, padx = 4)
        entry_diemdanh = ttk.Entry(hangnhap, textvariable = self.str_nhapdiemdanh)
        entry_diemdanh.pack(side = tk.LEFT, fill = tk.X, expand = True)
        entry_diemdanh.bind("<Return>", lambda e: on_add_diemdanh())

        ttk.Label(nhom, text = "Nhập (x, y, bản đồ) hoặc dán cả danh sách. Ctrl+P / Ctrl+B: thêm vị trí "
                               "đang đứng (hoặc điểm trỏ chuột khi mở bản đồ lớn).",
                  style = "Phu.TLabel", justify = tk.LEFT, wraplength = self._px(560)).grid(row = 3, column = 0, columnspan = 2, sticky = tk.W, pady = (4, 0))


    def _taotabnhom(self, tab):
        nhom = self._taonhom(tab, "Nhóm")

        def on_click_theosau():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "battat_tudongtheosau"

        ttk.Checkbutton(nhom, text = "Tự động theo sau", variable = self.vars["theosau"],
                        command = on_click_theosau).grid(row = 0, column = 0, sticky = tk.W, pady = 1)
        ttk.Label(nhom, text = "Ctrl+Alt+F", style = "Phim.TLabel").grid(row = 0, column = 1, sticky = tk.E, padx = (8, 0))

        # Chọn người theo sau: trưởng nhóm (mặc định) hoặc người chơi đang ở xung quanh, lưu theo ID
        hangmuctieu = ttk.Frame(nhom)
        hangmuctieu.grid(row = 1, column = 0, columnspan = 2, sticky = tk.EW, padx = (22, 0), pady = (0, 2))
        ttk.Label(hangmuctieu, text = "Theo sau:").pack(side = tk.LEFT)
        self.str_muctieutheosau = tk.StringVar(value = TEN_MUCTIEUMACDINH)
        self.cbo_muctieutheosau = ttk.Combobox(hangmuctieu, textvariable = self.str_muctieutheosau, state = "readonly", height = 20,
                                               postcommand = self._napdanhsachmuctieutheosau)
        self.cbo_muctieutheosau.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (4, 0))

        def on_chon_muctieutheosau(event = None):
            hwnd = self.get_selected_hwnd()
            chon = self._muctieutheosau_map.get(self.str_muctieutheosau.get())
            if hwnd and chon is not None:
                idmuctieu, tenmuctieu = chon
                self.command_dict[hwnd] = f"set_muctieutheosau:{idmuctieu}|{tenmuctieu}"
                self._muctieutheosauchoxacnhan = (hwnd, idmuctieu, time.time())
            self.root.focus_set()

        self.cbo_muctieutheosau.bind("<<ComboboxSelected>>", on_chon_muctieutheosau)

        hangkhoangcach = ttk.Frame(nhom)
        hangkhoangcach.grid(row = 2, column = 0, columnspan = 2, sticky = tk.W, padx = (22, 0), pady = (0, 4))
        ttk.Label(hangkhoangcach, text = "Khoảng cách tối đa tới người theo sau:").pack(side = tk.LEFT)

        def on_khoangcach_change(hwnd = None):
            hwnd = hwnd or self.get_selected_hwnd()
            if hwnd:
                try:
                    val = self.vars["khoangcachtheosau"].get()
                    self.command_dict[hwnd] = f"set_khoangcachtheosau:{val}"
                except tk.TclError:
                    pass

        self.spin_khoangcach = ttk.Spinbox(hangkhoangcach, from_ = 1.0, to = 50.0, increment = 1.0, width = 5,
                                           textvariable = self.vars["khoangcachtheosau"], command = on_khoangcach_change)
        self.spin_khoangcach.pack(side = tk.LEFT, padx = 4)
        self._ganspinboxapdung(self.spin_khoangcach, on_khoangcach_change)

        self._create_check(nhom, "Tự tìm đường tới người được theo sau (phù / Hồi Thành Phù / chạy bộ)", self.vars["tutimduongtheosau"], "battat_tutimduongtheosau")

        nhom = self._taonhom(tab, "Bảo thú")
        self._create_check(nhom, "Triệu hồi bảo thú giang hồ", self.vars["trieuhoibaothu"], "battat_tudongtrieuhoibaothugiangho")
        self._create_check(nhom, "Tự động dùng kỹ năng bảo thú giang hồ", self.vars["sudungkynangbaothu"], "battat_tudongsudungkynangbaothu")
        # Triệu hồi bảo thú kỹ năng nào: Tự động (Mao Sơn: Cương Thi nếu có Cương Thi Phù, không thì Thiên Binh; Vân Mộng Cốc: Đậu Binh),
        # đúng 1 loại, hoặc không triệu hồi
        hangbaothu = ttk.Frame(nhom)
        hangbaothu.grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.W, pady = 1)
        ttk.Label(hangbaothu, text = "Triệu hồi bảo thú kỹ năng:").pack(side = tk.LEFT)
        self.str_baothutrieuhoi = tk.StringVar(value = BAOTHUTRIEUHOIMAOSONs[0])
        self.cbo_baothutrieuhoi = ttk.Combobox(hangbaothu, textvariable = self.str_baothutrieuhoi, values = BAOTHUTRIEUHOIMAOSONs,
                                               state = "readonly", width = 15)
        self.cbo_baothutrieuhoi.pack(side = tk.LEFT, padx = 4)
        # Vừa chọn: (hwnd, lựa chọn, thời điểm) để chờ bot nhận, update_ui không nạp lại giá trị cũ đè lên
        self._baothutrieuhoichoxacnhan = None

        def on_chon_baothutrieuhoi(event = None):
            hwnd = self.get_selected_hwnd()
            if hwnd:
                baothu = self.str_baothutrieuhoi.get()
                self.command_dict[hwnd] = f"set_baothutrieuhoimaoson:{baothu}"
                self._baothutrieuhoichoxacnhan = (hwnd, baothu, time.time())

        self.cbo_baothutrieuhoi.bind("<<ComboboxSelected>>", on_chon_baothutrieuhoi)

        self._create_check(nhom, "Mao Sơn: khi triệu hồi đeo bộ đồ đã ghi, xong mặc lại", self.vars["doidotrieuhoi"], "battat_doidokhitrieuhoi")

        # Bộ đồ triệu hồi: mặc bộ đồ muốn dùng khi triệu hồi rồi bấm Ghi (nhận món theo mô tả, đồ để đâu trong hành trang cũng được)
        hangbodo = ttk.Frame(nhom)
        hangbodo.grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.EW, padx = (22, 0), pady = (0, 2))

        def on_ghibodotrieuhoi():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "ghi_bodotrieuhoi"

        ttk.Button(hangbodo, text = "Ghi bộ đồ đang mặc", command = on_ghibodotrieuhoi).pack(side = tk.LEFT)
        self.lbl_bodotrieuhoi = tk.Label(hangbodo, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(300))
        self.lbl_bodotrieuhoi.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (6, 0))

    def _taotabtodoi(self, tab):
        # Danh sách dùng chung cho mọi nhân vật (lưu file todoi.json), bật/tắt thì theo từng nhân vật
        nhom = self._taonhom(tab, "Nhóm tổ đội tự động (dùng chung mọi nhân vật trên máy)")
        self._create_check(nhom, "Bật Tổ đội tự động (theo nhân vật đang chọn)", self.vars["todoitudong"], "battat_tudongtodoi")
        # Tổ đội 1 lần: nhân vật đang chọn giữ nhóm hiện tại (vd. nhóm vừa lập để lấy phó bản), mời đồng đội cùng danh sách vào rồi thôi
        hangmotlan = ttk.Frame(nhom)
        hangmotlan.grid(row = 1, column = 0, sticky = tk.EW, pady = (2, 6))
        self.btn_todoimotlan = ttk.Button(hangmotlan, text = "👥 Tổ đội 1 lần", command = self._todoimotlan)
        self.btn_todoimotlan.pack(side = tk.LEFT)
        ttk.Label(hangmotlan, text = "Ctrl+Alt+T", style = "Phim.TLabel").pack(side = tk.LEFT, padx = (6, 0))
        self.lbl_todoimotlan = tk.Label(hangmotlan, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(420))
        self.lbl_todoimotlan.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (8, 0))
        self.tree_todoi = ttk.Treeview(nhom, columns = ("so", "truongnhom", "thanhvien", "online"), show = "headings", height = 5, selectmode = "browse")
        for col, text, width, anchor in (
                ("so", "Nhóm", 45, tk.CENTER),
                ("truongnhom", "Ưu tiên trưởng nhóm", 130, tk.W),
                ("thanhvien", "Thành viên (theo thứ tự ưu tiên)", 300, tk.W),
                ("online", "Online", 60, tk.CENTER)):
            self.tree_todoi.heading(col, text = text)
            self.tree_todoi.column(col, width = self._px(width), anchor = anchor, stretch = col == "thanhvien")
        self.tree_todoi.grid(row = 2, column = 0, sticky = tk.EW)
        self.tree_todoi.bind("<Double-1>", lambda e: self._suanhomtodoi(is_moi = False))
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 3, column = 0, sticky = tk.W, pady = (4, 0))
        for chu, lenh in (("Thêm nhóm", lambda: self._suanhomtodoi(is_moi = True)), ("Sửa", lambda: self._suanhomtodoi(is_moi = False)),
                          ("Xoá", self._xoanhomtodoi), ("↑ Lên", lambda: self._doichonhomtodoi(-1)), ("↓ Xuống", lambda: self._doichonhomtodoi(1))):
            ttk.Button(hangnut, text = chu, command = lenh).pack(side = tk.LEFT, padx = (0, 4))
        self.lbl_idnhanvatdangchon = tk.Label(nhom, text = "", fg = MAUCHU_XANH, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(560))
        self.lbl_idnhanvatdangchon.grid(row = 4, column = 0, sticky = tk.W, pady = (6, 0))
        ttk.Label(nhom, text = "Người đứng trước trong nhóm được ưu tiên làm trưởng nhóm. Nhân vật trong danh sách cũng được coi là đồng đội "
                               "(buff, không đánh). Nhấp đúp một nhóm để sửa. Tổ đội 1 lần: nhân vật đang chọn giữ nguyên nhóm của mình "
                               "(không rời, không nhường trưởng nhóm), mời đồng đội cùng nhóm đang online vào; đồng đội đang ở nhóm khác "
                               "thì tự rời rồi vào, không cần bật Tổ đội tự động.",
                  style = "Phu.TLabel", justify = tk.LEFT, wraplength = self._px(560)).grid(row = 5, column = 0, sticky = tk.W, pady = (4, 0))
        self._todoidanghien = None
        self._hientodoi(is_batbuoc = True)

    def _todoimotlan(self):
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            from tkinter import messagebox
            messagebox.showwarning("Tổ đội 1 lần", "Chọn nhân vật làm trưởng nhóm trong danh sách trước", parent = self.root)
            return
        # Nút trên giao diện: đang gom thì huỷ việc gom (nhóm giữ nguyên); phím tắt Ctrl+Alt+T thì chỉ bắt đầu
        info = self.shared_data.get(hwnd) or {}
        self.command_dict[int(hwnd)] = "huytodoimotlan" if info.get("_is_dangtodoimotlan") else "todoimotlan"

    def _capnhattodoimotlan(self):
        hwnd = self.get_selected_hwnd()
        info = (self.shared_data.get(hwnd) or {}) if hwnd else {}
        chunut = "⏹ Huỷ tổ đội 1 lần" if info.get("_is_dangtodoimotlan") else "👥 Tổ đội 1 lần"
        if self.btn_todoimotlan.cget("text") != chunut:
            self.btn_todoimotlan.config(text = chunut)
        chu = info.get("_trangthaitodoimotlan") or ""
        if self.lbl_todoimotlan.cget("text") != chu:
            self.lbl_todoimotlan.config(text = chu)

    def _tentheoid(self):
        # {ID người chơi: tên} để hiện tên thay cho ID: nhân vật đang chạy bot (chắc nhất), rồi tới file tài khoản
        ten = {}
        try:
            for tk_ in taicauhinhdangnhap().get("taikhoans", []):
                if tk_.get("idnguoichoi") and tk_.get("tennhanvat"):
                    ten[int(tk_["idnguoichoi"])] = tk_["tennhanvat"]
        except (TypeError, ValueError):
            pass
        for info in dict(self.shared_data.items()).values():
            if isinstance(info, dict) and info.get("idnguoichoi") and info.get("tennhanvat"):
                ten[info["idnguoichoi"]] = info["tennhanvat"]
        return ten

    def _tenvaid(self, idnguoichoi, tentheoid):
        return f"{tentheoid[idnguoichoi]} ({idnguoichoi})" if idnguoichoi in tentheoid else f"ID {idnguoichoi}"

    def _hientodoi(self, is_batbuoc = False, chon = None):
        # Vẽ lại khi file todoi.json, tên hoặc nhân vật online đổi
        nhoms = tainhomtodoitudongs()
        tentheoid = self._tentheoid()
        onlines = {info.get("idnguoichoi") for info in dict(self.shared_data.items()).values() if isinstance(info, dict)}
        khoa = (json.dumps(nhoms), json.dumps(sorted(tentheoid.items())), json.dumps(sorted(i for i in onlines if i)))
        if khoa == self._todoidanghien and not is_batbuoc:
            return
        self._todoidanghien = khoa
        dangchon = chon if chon is not None else (self.tree_todoi.selection() or [None])[0]
        self.tree_todoi.delete(*self.tree_todoi.get_children())
        for i, nhom in enumerate(nhoms):
            self.tree_todoi.insert("", tk.END, iid = str(i), values = (
                i + 1, self._tenvaid(nhom[0], tentheoid) if nhom else "", ", ".join(self._tenvaid(id_, tentheoid) for id_ in nhom),
                f"{sum(1 for id_ in nhom if id_ in onlines)}/{len(nhom)}"))
        if dangchon is not None and self.tree_todoi.exists(str(dangchon)):
            self.tree_todoi.selection_set(str(dangchon))

    def _luutodoi(self, nhoms, chon = None):
        luunhomtodoitudongs(nhoms)
        self._hientodoi(is_batbuoc = True, chon = chon)

    def _xoanhomtodoi(self):
        from tkinter import messagebox
        chon = self.tree_todoi.selection()
        if not chon:
            return
        nhoms = tainhomtodoitudongs()
        if messagebox.askyesno("Xoá nhóm", f"Xoá nhóm {int(chon[0]) + 1}?", parent = self.root):
            nhoms.pop(int(chon[0]))
            self._luutodoi(nhoms)

    def _doichonhomtodoi(self, huong):
        chon = self.tree_todoi.selection()
        if not chon:
            return
        nhoms = tainhomtodoitudongs()
        i, j = int(chon[0]), int(chon[0]) + huong
        if 0 <= j < len(nhoms):
            nhoms[i], nhoms[j] = nhoms[j], nhoms[i]
            self._luutodoi(nhoms, chon = j)

    def _suanhomtodoi(self, is_moi):
        # Hộp thoại sửa 1 nhóm: danh sách thành viên theo thứ tự ưu tiên (lên / xuống / bỏ), thêm từ danh sách nhân vật đã biết
        # (đang chạy bot + file tài khoản) hoặc gõ ID
        from tkinter import messagebox
        chon = self.tree_todoi.selection()
        if not is_moi and not chon:
            return
        nhoms = tainhomtodoitudongs()
        vitri = None if is_moi else int(chon[0])
        thanhviens = [] if is_moi else list(nhoms[vitri])
        tentheoid = self._tentheoid()
        if is_moi:
            hwnd = self.get_selected_hwnd()
            idchon = self.shared_data.get(hwnd, {}).get("idnguoichoi") if hwnd else None
            if idchon:
                thanhviens.append(idchon)

        hop = tk.Toplevel(self.root)
        hop.title("Thêm nhóm tổ đội" if is_moi else f"Sửa nhóm {vitri + 1}")
        hop.transient(self.root)
        hop.attributes("-topmost", True)
        khung = ttk.Frame(hop, padding = 12)
        khung.pack(fill = tk.BOTH, expand = True)
        khung.columnconfigure(0, weight = 1)
        ttk.Label(khung, text = "Thành viên", font = (FONTCHU, COCHU, "bold")).grid(row = 0, column = 0, sticky = tk.W)
        ttk.Label(khung, text = "người đứng trên được ưu tiên làm trưởng nhóm", style = "Phu.TLabel").grid(row = 1, column = 0, sticky = tk.W)
        hangds = ttk.Frame(khung)
        hangds.grid(row = 2, column = 0, sticky = tk.NSEW, pady = (2, 0))
        ds = tk.Listbox(hangds, height = 8, width = 36, activestyle = "none", font = (FONTCHU, COCHU), exportselection = False)
        ds.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        cotnut = ttk.Frame(hangds)
        cotnut.pack(side = tk.LEFT, fill = tk.Y, padx = (6, 0))

        def vechon(j = None):
            ds.delete(0, tk.END)
            for stt, id_ in enumerate(thanhviens, 1):
                ds.insert(tk.END, f"{stt}. {self._tenvaid(id_, tentheoid)}")
            if j is not None and 0 <= j < len(thanhviens):
                ds.selection_set(j)

        def dichuyen(huong):
            sel = ds.curselection()
            if not sel:
                return
            i = sel[0]
            j = i + huong
            if 0 <= j < len(thanhviens):
                thanhviens[i], thanhviens[j] = thanhviens[j], thanhviens[i]
                vechon(j)

        def bo():
            sel = ds.curselection()
            if sel:
                thanhviens.pop(sel[0])
                vechon(min(sel[0], len(thanhviens) - 1))

        for chu, lenh in (("↑ Lên", lambda: dichuyen(-1)), ("↓ Xuống", lambda: dichuyen(1)), ("Bỏ", bo)):
            ttk.Button(cotnut, text = chu, width = 8, command = lenh).pack(pady = (0, 4))

        ttk.Label(khung, text = "Thêm nhân vật", font = (FONTCHU, COCHU, "bold")).grid(row = 3, column = 0, sticky = tk.W, pady = (10, 0))
        ttk.Label(khung, text = "chọn trong danh sách hoặc gõ ID", style = "Phu.TLabel").grid(row = 4, column = 0, sticky = tk.W)
        hangthem = ttk.Frame(khung)
        hangthem.grid(row = 5, column = 0, sticky = tk.EW, pady = (2, 0))
        trongnhomkhac = {id_: i + 1 for i, n in enumerate(nhoms) if i != vitri for id_ in n}
        goiys = [f"{ten} ({id_})" + (f" · đang ở nhóm {trongnhomkhac[id_]}" if id_ in trongnhomkhac else "") for id_, ten in sorted(tentheoid.items(), key = lambda m: m[1])]
        str_them = tk.StringVar()
        ttk.Combobox(hangthem, textvariable = str_them, values = goiys).pack(side = tk.LEFT, fill = tk.X, expand = True)

        def them():
            chu = str_them.get().strip()
            khop = re.search(r"\((\d+)\)", chu) or re.fullmatch(r"(\d+)", chu)
            if not khop:
                messagebox.showwarning("Thêm nhân vật", "Chọn nhân vật trong danh sách hoặc gõ ID (số)", parent = hop)
                return
            id_ = int(khop.group(1))
            if id_ not in thanhviens:
                thanhviens.append(id_)
            str_them.set("")
            vechon(thanhviens.index(id_))

        ttk.Button(hangthem, text = "Thêm", command = them).pack(side = tk.LEFT, padx = (6, 0))
        ketqua = {}

        def on_luu():
            if not thanhviens:
                messagebox.showwarning("Nhóm tổ đội", "Nhóm cần ít nhất 1 nhân vật", parent = hop)
                return
            ketqua["thanhviens"] = list(thanhviens)
            hop.destroy()

        hangnut = ttk.Frame(khung)
        hangnut.grid(row = 6, column = 0, sticky = tk.E, pady = (12, 0))
        ttk.Button(hangnut, text = "Lưu", command = on_luu).pack(side = tk.LEFT, padx = (0, 4))
        ttk.Button(hangnut, text = "Huỷ", command = hop.destroy).pack(side = tk.LEFT)
        vechon(0 if thanhviens else None)
        hop.grab_set()
        self.root.wait_window(hop)
        if not ketqua:
            return
        # 1 nhân vật chỉ ở 1 nhóm: thêm vào nhóm này thì bỏ khỏi nhóm khác (nhóm thành rỗng thì bỏ luôn)
        moi = ketqua["thanhviens"]
        nhoms = [[id_ for id_ in n if id_ not in moi] if i != vitri else n for i, n in enumerate(nhoms)]
        if is_moi:
            nhoms.append(moi)
            vitri = len(nhoms) - 1
        else:
            nhoms[vitri] = moi
        conlai = [(i, n) for i, n in enumerate(nhoms) if n]
        vitri = next(j for j, (i, _) in enumerate(conlai) if i == vitri)
        self._luutodoi([n for _, n in conlai], chon = vitri)

    def _taotabdangnhap(self, tab):
        # Chung mọi máy (không theo nhân vật đang chọn): tài khoản trong _internal/taikhoan_chung.json, mỗi dòng bật cho một máy
        nhom = self._taonhom(tab, f"Tự động đăng nhập (máy này: {tenmaynay()})")
        ttk.Label(nhom, text = "Tự đăng nhập lại nhân vật vắng mặt: tick cột ☑ ở dòng tài khoản để máy này tự đăng nhập tài khoản đó.",
                  justify = tk.LEFT, wraplength = self._px(390)).grid(row = 0, column = 0, sticky = tk.W, pady = 1)
        self.lbl_trangthaidangnhap = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(390))
        self.lbl_trangthaidangnhap.grid(row = 1, column = 0, columnspan = 2, sticky = tk.W, pady = (2, 4))
        # Chỉ hiện khi đang tạm ngưng / tạm hoãn (_capnhatdangnhap)
        self.btn_tieptucdangnhap = ttk.Button(nhom, text = "Tiếp tục đăng nhập ngay", command = self._tieptucdangnhap)
        ttk.Label(nhom, text = "Đang tạm ngưng (ẩn thân / người lạ) hoặc tạm hoãn (bị đá liên tục) thì không đăng nhập cho tới khi hết hạn, "
                               "bấm \"Tiếp tục đăng nhập ngay\" để bỏ chờ.",
                  style = "Phu.TLabel", justify = tk.LEFT, wraplength = self._px(390)).grid(row = 2, column = 0, columnspan = 2, sticky = tk.W)

        # Bảng tài khoản (thứ tự = thứ tự đăng nhập), sửa bằng form; vẫn mở được file JSON để sửa tay
        nhom = self._taonhom(tab, "Tài khoản (đăng nhập lần lượt từ trên xuống)")
        self.tree_taikhoan = ttk.Treeview(nhom, columns = ("bat", "tinhtrang", "ten", "id", "user", "maychu", "nhanvat", "cuaso"), show = "headings",
                                          height = 10, selectmode = "browse")
        for col, text, width, anchor in (
                ("bat", "Bật", 35, tk.CENTER),
                ("tinhtrang", "Trạng thái", 120, tk.W),
                ("ten", "Nhân vật", 110, tk.W),
                ("id", "ID", 45, tk.CENTER),
                ("user", "Tài khoản", 100, tk.W),
                ("maychu", "Cụm·Máy", 70, tk.CENTER),
                ("nhanvat", "Ô NV", 50, tk.CENTER),
                ("cuaso", "Cửa sổ", 55, tk.CENTER)):
            self.tree_taikhoan.heading(col, text = text)
            self.tree_taikhoan.column(col, width = self._px(width), anchor = anchor, stretch = col in ("ten", "user"))
        for tinhtrang, mau in (("online", MAUCHU_LUC), ("đang đăng nhập", MAUCHU_XANH), ("vắng", MAUCHU_PHU), ("thiếu ID/tên", MAUCHU_DO),
                               ("tắt", MAUCHU_PHU)):
            self.tree_taikhoan.tag_configure(tinhtrang, foreground = mau)
        self.tree_taikhoan.grid(row = 0, column = 0, sticky = tk.EW)

        def on_click_taikhoan(event):
            # Bấm vào cột "Bật": bật/tắt tự đăng nhập tài khoản đó cho máy này
            if self.tree_taikhoan.identify_column(event.x) != "#1" or self.tree_taikhoan.identify_region(event.x, event.y) != "cell":
                return None
            dong = self.tree_taikhoan.identify_row(event.y)
            if dong and dong != "loi":
                self._battattaikhoan(int(dong))
            return "break"

        self.tree_taikhoan.bind("<Button-1>", on_click_taikhoan)
        self.tree_taikhoan.bind("<Double-1>", lambda e: None if self.tree_taikhoan.identify_column(e.x) == "#1" else self._suataikhoan(is_moi = False))
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))

        def on_mofiletaikhoan():
            # Chưa có file thì tạo file mẫu để điền
            taicauhinhdangnhap()
            os.startfile(duongdantaikhoan())

        for chu, lenh in (("Thêm", lambda: self._suataikhoan(is_moi = True)), ("Sửa", lambda: self._suataikhoan(is_moi = False)),
                          ("Xoá", self._xoataikhoan), ("↑ Lên", lambda: self._doichotaikhoan(-1)), ("↓ Xuống", lambda: self._doichotaikhoan(1)),
                          ("Mở file", on_mofiletaikhoan)):
            ttk.Button(hangnut, text = chu, command = lenh).pack(side = tk.LEFT, padx = (0, 4))

        hangduongdan = ttk.Frame(nhom)
        hangduongdan.grid(row = 2, column = 0, sticky = tk.EW, pady = (8, 0))
        ttk.Label(hangduongdan, text = "Đường dẫn game:").pack(side = tk.LEFT)
        self.str_duongdangame = tk.StringVar(value = duongdangamemaynay(taicauhinhdangnhap()))
        ttk.Entry(hangduongdan, textvariable = self.str_duongdangame).pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (4, 4))

        def on_luuduongdan():
            # Mỗi máy cài game một chỗ: lưu theo tên máy
            cauhinh = taicauhinhdangnhap()
            if not cauhinh.get("loi"):
                cauhinh.setdefault("duongdangames", {})[tenmaynay()] = self.str_duongdangame.get().strip()
                luucauhinhdangnhap(cauhinh)

        ttk.Button(hangduongdan, text = "Lưu", command = on_luuduongdan).pack(side = tk.LEFT)
        ttk.Label(nhom, text = f"{duongdantaikhoan()} · một file chung mọi máy (đồng bộ qua git), mỗi tài khoản chỉ bật được cho một máy "
                               "nên hai máy không giành nhau. Thêm khi đang chọn nhân vật trong game thì tên và ID tự điền sẵn, bật luôn cho máy này.",
                  style = "Phu.TLabel", justify = tk.LEFT, wraplength = self._px(560)).grid(row = 3, column = 0, sticky = tk.W, pady = (6, 0))
        self._taikhoandanghien = None

    def _capnhatdangnhap(self):
        if self.dangnhap is None:
            return
        trangthai = self.dangnhap.trangthai
        if self.lbl_trangthaidangnhap.cget("text") != trangthai:
            mau = MAUCHU_DO if trangthai.startswith(("Tạm ngưng", "Lỗi", "File tài khoản bị lỗi")) else (MAUCHU_XANH if trangthai.startswith("Đang đăng nhập") else MAUCHU_PHU)
            self.lbl_trangthaidangnhap.config(text = trangthai, fg = mau)
        is_dangtamngung = self.dangnhap.is_dangtamngung()
        if is_dangtamngung != bool(self.btn_tieptucdangnhap.winfo_manager()):
            if is_dangtamngung:
                self.btn_tieptucdangnhap.grid(row = 3, column = 0, sticky = tk.W, pady = (4, 0))
            else:
                self.btn_tieptucdangnhap.grid_remove()
        self._hientaikhoan()

    def _tieptucdangnhap(self):
        self.dangnhap.tieptuc()
        self.btn_tieptucdangnhap.grid_remove()
        self.lbl_trangthaidangnhap.config(text = "Đã bỏ tạm ngưng, đăng nhập lại ở lượt quét kế tiếp...", fg = MAUCHU_XANH)

    def _hientaikhoan(self, is_batbuoc = False, chon = None):
        # Vẽ lại bảng khi file tài khoản hoặc tình trạng (online / vắng...) đổi; tình trạng lấy từ luồng đăng nhập (cùng thứ tự file)
        cauhinh = taicauhinhdangnhap()
        tinhtrangs = [tinhtrang for _, _, tinhtrang in self.dangnhap.danhsach] if self.dangnhap else []
        khoa = (json.dumps(cauhinh.get("taikhoans", []), ensure_ascii = False, sort_keys = True), tuple(tinhtrangs))
        if khoa == self._taikhoandanghien and not is_batbuoc:
            return
        self._taikhoandanghien = khoa
        dangchon = chon if chon is not None else (self.tree_taikhoan.selection() or [None])[0]
        self.tree_taikhoan.delete(*self.tree_taikhoan.get_children())
        bieutuong = {"online": "🟢 online", "vắng": "⚪ vắng", "đang đăng nhập": "⏳ đang vào", "thiếu ID/tên": "⚠ thiếu ID/tên"}
        for i, tk_ in enumerate(cauhinh.get("taikhoans", [])):
            tinhtrang = tinhtrangs[i] if i < len(tinhtrangs) and len(tinhtrangs) == len(cauhinh.get("taikhoans", [])) else ""
            the = "tắt" if tinhtrang.startswith("máy ") else tinhtrang
            self.tree_taikhoan.insert("", tk.END, iid = str(i), tags = (the,), values = (
                "☑" if is_batchomaynay(tk_) else "☐", bieutuong.get(tinhtrang, tinhtrang or "-"), tk_.get("tennhanvat") or "", tk_.get("idnguoichoi") or "", tk_.get("user") or "",
                f"{tk_.get('group', 1)} · {tk_.get('server', 1)}", tk_.get("char_index", 1), tk_.get("vitricuaso", "")))
        if cauhinh.get("loi"):
            self.tree_taikhoan.insert("", tk.END, iid = "loi", tags = ("thiếu ID/tên",), values = ("", "⚠ " + cauhinh["loi"], "", "", "", "", "", ""))
        if dangchon is not None and self.tree_taikhoan.exists(str(dangchon)):
            self.tree_taikhoan.selection_set(str(dangchon))

    def _laycauhinhtaikhoan(self):
        # Cấu hình đọc được để sửa, None (kèm báo lỗi) khi file đang hỏng: lưu đè lúc đó là mất tài khoản
        from tkinter import messagebox
        cauhinh = taicauhinhdangnhap()
        if cauhinh.get("loi"):
            messagebox.showerror("Tài khoản", f"{cauhinh['loi']}\nBấm \"Mở file\" sửa lại trước.", parent = self.root)
            return None
        return cauhinh

    def _luutaikhoan(self, cauhinh, chon = None):
        luucauhinhdangnhap(cauhinh)
        self._hientaikhoan(is_batbuoc = True, chon = chon)

    def _battattaikhoan(self, vitri):
        from tkinter import messagebox
        cauhinh = self._laycauhinhtaikhoan()
        if cauhinh is None or not 0 <= vitri < len(cauhinh.get("taikhoans", [])):
            return
        taikhoan = cauhinh["taikhoans"][vitri]
        is_bat = not is_batchomaynay(taikhoan)
        maykhac = taikhoan.get("maydangnhap")
        if is_bat and maykhac and not messagebox.askyesno(
                "Bật tự đăng nhập", f"{taikhoan.get('tennhanvat') or taikhoan.get('user')} đang bật tự đăng nhập ở máy {maykhac}.\n"
                                    f"Chuyển sang máy này ({tenmaynay()})? Máy {maykhac} sẽ thôi đăng nhập tài khoản này sau khi đồng bộ file.",
                parent = self.root):
            return
        self.dangnhap.set_is_battaikhoan(cauhinh, vitri, is_bat)
        self._hientaikhoan(is_batbuoc = True, chon = vitri)

    def _suataikhoan(self, is_moi):
        cauhinh = self._laycauhinhtaikhoan()
        if cauhinh is None:
            return
        chon = self.tree_taikhoan.selection()
        if not is_moi and (not chon or chon[0] == "loi"):
            return
        taikhoans = list(cauhinh.get("taikhoans", []))
        vitri = None if is_moi else int(chon[0])
        if is_moi:
            # Đang chọn nhân vật nào trên bảng trên cùng thì điền sẵn tên + ID của nó, cửa sổ kế tiếp còn trống
            info = self.shared_data.get(self.get_selected_hwnd()) if self.get_selected_hwnd() else None
            taikhoan = {"tennhanvat": (info or {}).get("tennhanvat") or "", "idnguoichoi": (info or {}).get("idnguoichoi") or "", "group": 1,
                        "server": 1, "char_index": 1, "maydangnhap": tenmaynay(),
                        "vitricuaso": next((v for v in range(1, 5) if v not in {t.get("vitricuaso") for t in taikhoanbatchomaynay(cauhinh)}), 1)}
        else:
            taikhoan = dict(taikhoans[vitri])
        giatris = {k: ("" if taikhoan.get(k) is None else str(taikhoan.get(k))) for k in ("tennhanvat", "idnguoichoi", "user", "pass", "group", "server",
                                                                                          "char_index", "vitricuaso")}
        truongs = [("tennhanvat", "Tên nhân vật", None), ("idnguoichoi", "ID người chơi (cố định, ưu tiên để nhận ra)", None),
                   ("user", "Tài khoản", None), ("pass", "Mật khẩu", None),
                   ("group", "Cụm máy chủ", ["1", "2", "3", "4"]), ("server", "Máy chủ", ["1", "2"]),
                   ("char_index", "Ô nhân vật (1-6)", ["1", "2", "3", "4", "5", "6"]), ("vitricuaso", "Vị trí cửa sổ (1-4)", ["1", "2", "3", "4"])]

        def kiemtra(kq):
            if not kq["user"].strip() or not kq["pass"]:
                return "Cần tài khoản và mật khẩu"
            if not kq["idnguoichoi"].strip() and not kq["tennhanvat"].strip():
                return "Cần ID người chơi hoặc tên nhân vật để biết nhân vật đã online chưa"
            if kq["idnguoichoi"].strip() and not kq["idnguoichoi"].strip().isdigit():
                return "ID người chơi phải là số"
            for t, toida in (("group", 4), ("server", 2), ("char_index", 6), ("vitricuaso", 4)):
                if not kq[t].strip().isdigit() or not 1 <= int(kq[t]) <= toida:
                    return f"Ô \"{dict((k, n) for k, n, _ in truongs)[t]}\" phải từ 1 tới {toida}"
            return None

        kq = self._hopthoaituido("Thêm tài khoản" if is_moi else "Sửa tài khoản", truongs, giatris, kiemtra, matkhaus = ("pass",))
        if not kq:
            return
        moi = dict(taikhoan, tennhanvat = kq["tennhanvat"].strip(), idnguoichoi = int(kq["idnguoichoi"]) if kq["idnguoichoi"].strip() else None,
                   user = kq["user"].strip(), **{"pass": kq["pass"]}, group = int(kq["group"]), server = int(kq["server"]),
                   char_index = int(kq["char_index"]), vitricuaso = int(kq["vitricuaso"]))
        if is_moi:
            taikhoans.append(moi)
            vitri = len(taikhoans) - 1
        else:
            taikhoans[vitri] = moi
        cauhinh["taikhoans"] = taikhoans
        self._luutaikhoan(cauhinh, chon = vitri)

    def _xoataikhoan(self):
        from tkinter import messagebox
        chon = self.tree_taikhoan.selection()
        cauhinh = self._laycauhinhtaikhoan() if chon and chon[0] != "loi" else None
        if cauhinh is None:
            return
        taikhoans = list(cauhinh.get("taikhoans", []))
        taikhoan = taikhoans[int(chon[0])]
        if not messagebox.askyesno("Xoá tài khoản", f"Xoá tài khoản {taikhoan.get('user')} ({taikhoan.get('tennhanvat') or taikhoan.get('idnguoichoi')})?",
                                   parent = self.root):
            return
        taikhoans.pop(int(chon[0]))
        cauhinh["taikhoans"] = taikhoans
        self._luutaikhoan(cauhinh)

    def _doichotaikhoan(self, huong):
        chon = self.tree_taikhoan.selection()
        cauhinh = self._laycauhinhtaikhoan() if chon and chon[0] != "loi" else None
        if cauhinh is None:
            return
        taikhoans = list(cauhinh.get("taikhoans", []))
        i, j = int(chon[0]), int(chon[0]) + huong
        if not 0 <= j < len(taikhoans):
            return
        taikhoans[i], taikhoans[j] = taikhoans[j], taikhoans[i]
        cauhinh["taikhoans"] = taikhoans
        self._luutaikhoan(cauhinh, chon = j)

    def _taotabkhac(self, tab):
        nhom = self._taonhom(tab, "Tạm ẩn (chưa dùng)")
        self._create_check(nhom, "Tự động khai khoáng", self.vars["khaikhoang"], "battat_tudongkhaikhoang", "Ctrl+Alt+Shift+K")
        self._create_check(nhom, "Đào tàng bảo đồ", self.vars["daobaodo"], "battat_tudongdaotangbaodo", "Ctrl+Alt+Shift+I")
        self._create_check(nhom, "Đi chiến trường", self.vars["chientruong"], "battat_tudongdichientruong", "Ctrl+Alt+Shift+Z")

    def _taotabtuido(self, tab):
        # Luật túi đồ (luattuido_xq, file _internal/luattuido.json dùng chung mọi nhân vật trên máy): sửa ở đây là lưu file ngay,
        # các bot tự đọc lại khi file đổi
        nhom = self._taonhom(tab, "Luật túi đồ (xét từ trên xuống, luật đầu tiên khớp quyết định)")
        self.tree_luattuido = ttk.Treeview(nhom, columns = ("bat", "bao", "hanhdong", "dieukien", "ghichu"), show = "headings", height = 8, selectmode = "browse")
        for col, text, width, anchor in (
                ("bat", "Bật", 40, tk.CENTER),
                ("bao", "📣", 35, tk.CENTER),
                ("hanhdong", "Hành động", 105, tk.W),
                ("dieukien", "Điều kiện", 225, tk.W),
                ("ghichu", "Ghi chú", 150, tk.W)):
            self.tree_luattuido.heading(col, text = text)
            self.tree_luattuido.column(col, width = self._px(width), anchor = anchor, stretch = col == "dieukien")
        self.tree_luattuido.grid(row = 0, column = 0, sticky = tk.EW)
        self.tree_luattuido.bind("<Double-1>", lambda e: self._sualuattuido(is_moi = False))
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        for chu, lenh in (("Thêm", lambda: self._sualuattuido(is_moi = True)), ("Sửa", lambda: self._sualuattuido(is_moi = False)),
                          ("Xoá", lambda: self._xoamuctuido("luat", self.tree_luattuido)),
                          ("↑ Lên", lambda: self._doichomuctuido(-1)), ("↓ Xuống", lambda: self._doichomuctuido(1))):
            ttk.Button(hangnut, text = chu, command = lenh).pack(side = tk.LEFT, padx = (0, 4))
        tk.Label(nhom, text = "Về bán rác: món KHÔNG khớp luật nào thì BÁN, muốn giữ thì phải có luật Giữ. Vứt: vứt ngay khi có trong túi. "
                              "📣: nhặt được món khớp bất kỳ luật 📣 nào thì báo Telegram kèm ảnh (xét riêng, luật đứng trên không chặn). "
                              "Món trong bảng Cất kho bên dưới thì không bán, không vứt. Nhấp đúp một dòng để sửa.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 2, column = 0, sticky = tk.W, pady = (4, 0))

        # Cất kho (tactu_catkho_xq): bảng riêng "catkho" trong cùng file luật, xét riêng với luật hành động ở trên
        nhom = self._taonhom(tab, "Cất kho (gửi Quản Khố ở Tân Thủ Thôn)")
        self.tree_catkho = ttk.Treeview(nhom, columns = ("bat", "dieukien", "ruong", "giulai", "ghichu"), show = "headings", height = 4, selectmode = "browse")
        for col, text, width, anchor in (
                ("bat", "Bật", 40, tk.CENTER),
                ("dieukien", "Điều kiện", 250, tk.W),
                ("ruong", "Rương", 70, tk.CENTER),
                ("giulai", "Giữ lại", 55, tk.CENTER),
                ("ghichu", "Ghi chú", 140, tk.W)):
            self.tree_catkho.heading(col, text = text)
            self.tree_catkho.column(col, width = self._px(width), anchor = anchor, stretch = col == "dieukien")
        self.tree_catkho.grid(row = 0, column = 0, sticky = tk.EW)
        self.tree_catkho.bind("<Double-1>", lambda e: self._suacatkho(is_moi = False))
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        for chu, lenh in (("Thêm", lambda: self._suacatkho(is_moi = True)), ("Sửa", lambda: self._suacatkho(is_moi = False)),
                          ("Xoá", lambda: self._xoamuctuido("catkho", self.tree_catkho))):
            ttk.Button(hangnut, text = chu, command = lenh).pack(side = tk.LEFT, padx = (0, 4))
        self.var_catkhosauban = tk.BooleanVar(value = True)
        ttk.Checkbutton(hangnut, text = "Tự cất sau mỗi lần về bán rác", variable = self.var_catkhosauban,
                        command = self._doicatkhosauban).pack(side = tk.LEFT, padx = (8, 4))
        # Cất kho ngay cho nhân vật đang chọn; trạng thái lấy từ shared_data "_trangthaicatkho" (_capnhatgiaodo vẽ lại)
        ttk.Button(hangnut, text = "🗄 Cất kho ngay", command = self._catkhongay).pack(side = tk.LEFT, padx = (8, 4))
        self.lbl_catkho = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W)
        self.lbl_catkho.grid(row = 2, column = 0, sticky = tk.W)
        tk.Label(nhom, text = "Món khớp luật bật nào trong bảng này thì không bán, không vứt, và được cất (thứ tự không quan trọng, luật Giữ ở "
                              "trên không chặn). Rương: \"Tự động\" = rương còn chỗ, hoặc số rương cố định (đầy thì báo, không cất chỗ khác). "
                              "Giữ lại: chừa chừng đó cái trong túi. Trong rương ưu tiên gộp chồng cùng loại, không thì ô trống; cất xong "
                              "tự đóng cửa sổ kho.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 3, column = 0, sticky = tk.W, pady = (4, 0))

        nhom = self._taonhom(tab, "Mua bù ở Tân Thủ Thôn (còn ít hơn \"Mua khi dưới\" thì mua cho đủ)")
        self.tree_muabu = ttk.Treeview(nhom, columns = ("bat", "vatpham", "npc", "xepchong", "duoi", "muatoi", "monphai", "chikhi"),
                                       show = "headings", height = 6, selectmode = "browse")
        for col, text, width, anchor in (
                ("bat", "Bật", 35, tk.CENTER),
                ("vatpham", "Vật phẩm", 105, tk.W),
                ("npc", "NPC", 95, tk.W),
                ("xepchong", "Chồng", 45, tk.E),
                ("duoi", "Khi dưới", 55, tk.E),
                ("muatoi", "Cho đủ", 50, tk.E),
                ("monphai", "Môn phái", 75, tk.W),
                ("chikhi", "Chỉ khi", 70, tk.W)):
            self.tree_muabu.heading(col, text = text)
            self.tree_muabu.column(col, width = self._px(width), anchor = anchor, stretch = col == "vatpham")
        self.tree_muabu.grid(row = 0, column = 0, sticky = tk.EW)
        self.tree_muabu.bind("<Double-1>", lambda e: self._suamuabu(is_moi = False))
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        for chu, lenh in (("Thêm", lambda: self._suamuabu(is_moi = True)), ("Sửa", lambda: self._suamuabu(is_moi = False)),
                          ("Xoá", lambda: self._xoamuctuido("muabu", self.tree_muabu))):
            ttk.Button(hangnut, text = chu, command = lenh).pack(side = tk.LEFT, padx = (0, 4))
        tk.Label(nhom, text = "Ô và giá bot tự tra theo tên món trong cửa hàng (đứng gần NPC thì mở cửa hàng đọc 1 lần rồi đóng, nhớ cho các "
                              "lần sau). Tên trong cửa hàng khác tên trong túi (vd Thức Ăn Bảo Thú Cao Cấp / Cao Cấp Bảo Thú Thực Phẩm) thì "
                              "ghi thêm \"Tên ở cửa hàng\". NPC tìm theo tên hoặc danh hiệu (cửa hàng các nước). Mua lần lượt từ trên xuống "
                              "trong số ngân lượng đang có.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(540)).grid(row = 2, column = 0, sticky = tk.W, pady = (4, 0))
        self._hienluattuido()

        # Giao tiền / đồ (giaodo_xq, tactu_giaodo_xq): hàng chờ của mọi nhân vật trên máy, lấy từ shared_data "_hangchogiaodo"
        nhom = self._taonhom(tab, "Giao tiền / đồ (người giao về Tiệm Tạp Hóa ở Tân Thủ Thôn chờ người nhận)")
        self.tree_giaodo = ttk.Treeview(nhom, columns = ("nguoigiao", "nguoinhan", "noidung", "trangthai"), show = "headings", height = 5,
                                        selectmode = "browse")
        for col, text, width, anchor in (
                ("nguoigiao", "Người giao", 95, tk.W),
                ("nguoinhan", "Người nhận", 95, tk.W),
                ("noidung", "Tiền / đồ", 200, tk.W),
                ("trangthai", "Trạng thái", 150, tk.W)):
            self.tree_giaodo.heading(col, text = text)
            self.tree_giaodo.column(col, width = self._px(width), anchor = anchor, stretch = col in ("noidung", "trangthai"))
        self.tree_giaodo.tag_configure("xong", foreground = MAUCHU_LUC)
        self.tree_giaodo.tag_configure("lỗi", foreground = MAUCHU_DO)
        self.tree_giaodo.tag_configure("dangchay", foreground = MAUCHU_XANH)
        self.tree_giaodo.grid(row = 0, column = 0, sticky = tk.EW)
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        ttk.Button(hangnut, text = "Thêm", command = self._themgiaodo).pack(side = tk.LEFT, padx = (0, 4))
        ttk.Button(hangnut, text = "Huỷ / bỏ dòng", command = self._huygiaodo).pack(side = tk.LEFT)
        ttk.Button(hangnut, text = "🚚 Về giao ngay", command = self._vegiaongay).pack(side = tk.LEFT, padx = (8, 4))
        ttk.Button(hangnut, text = "Cả máy về giao", command = lambda: self._vegiaongay(is_tatca = True)).pack(side = tk.LEFT)
        tk.Label(nhom, text = "Yêu cầu mới được để dành, bot vẫn đánh tiếp. Giao khi: về bán rác mà người nhận đang ở Tân Thủ Thôn (không thấy "
                              "thì bỏ qua, không chờ, để lần sau), hoặc bấm Về giao ngay (nhân vật của dòng đang chọn) / Cả máy về giao: về Tiệm Tạp Hóa chờ người "
                              "nhận tối đa 10 phút. Người giao phải đang chạy bot trên máy này; \"Tất cả nhân vật trên máy\" thì mỗi nhân vật "
                              "(trừ người nhận) 1 yêu cầu. Đồ ghi mỗi dòng 1 món, dạng \"Tên x số lượng\". Đứng cách người nhận tối đa 3 ô "
                              "mới giao; giao xong kiểm tra ngân lượng / túi đồ đã giảm rồi báo Telegram.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 2, column = 0, sticky = tk.W, pady = (4, 0))
        self._giaododanghien = None

    def _taotabnhiemvu(self, tab):
        # Nhiệm vụ sư môn (tactu_sumon_xq) cho nhân vật đang chọn: bấm bắt đầu / dừng, NPC giao nhiệm vụ lưu theo nhân vật
        nhom = self._taonhom(tab, "Nhiệm vụ sư môn (nhân vật đang chọn)")
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 0, column = 0, sticky = tk.W)
        self.btn_sumon = ttk.Button(hangnut, text = "📜 Bắt đầu sư môn", command = self._battatsumon)
        self.btn_sumon.pack(side = tk.LEFT)
        self.lbl_sumon = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(560))
        self.lbl_sumon.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))

        hangnpc = ttk.Frame(nhom)
        hangnpc.grid(row = 2, column = 0, sticky = tk.W, pady = (6, 0))
        ttk.Label(hangnpc, text = "NPC giao nhiệm vụ:").pack(side = tk.LEFT)
        self.str_sumonnpcgiao = tk.StringVar()
        self.ent_sumonnpcgiao = ttk.Entry(hangnpc, textvariable = self.str_sumonnpcgiao, width = 26)
        self.ent_sumonnpcgiao.pack(side = tk.LEFT, padx = 4)

        def on_luunpcgiao(event = None):
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = f"set_sumon_npcgiao:{self.str_sumonnpcgiao.get().strip()}"
            self.root.focus_set()

        self.ent_sumonnpcgiao.bind("<Return>", on_luunpcgiao)
        ttk.Button(hangnpc, text = "Lưu", width = 6, command = on_luunpcgiao).pack(side = tk.LEFT)
        self.lbl_sumonnpcmacdinh = ttk.Label(nhom, text = "", style = "Phu.TLabel")
        self.lbl_sumonnpcmacdinh.grid(row = 3, column = 0, sticky = tk.W)
        tk.Label(nhom, text = "Bot đọc nhiệm vụ trong cửa sổ nhiệm vụ của game rồi tự làm tới khi NPC giao báo hôm nay đã làm đủ 20 lần (làm thêm không có thưởng): nhận / trả ở NPC giao nhiệm vụ, "
                              "Đi tìm Thạch Sư, Thu thập (đánh đúng quái trong mô tả, nhặt đồ, đủ thì Hồi môn phái về giao), Thăm viếng, "
                              "Luyện tập / Du lịch (farm theo lộ trình điểm đánh của nhân vật), Bắt yêu quái (hết Dây Càn Khôn thì tự về "
                              "Chủ Tiệm Tạp Hóa mua), Mua sắm (tự sang nước trong mô tả tìm cửa hàng theo danh hiệu, mua rồi về giao). "
                              "Để trống NPC giao = mặc định theo môn phái (Côn Luân: Văn Xương Chân Quân). Vị trí NPC / quái bot thấy được tự ghi "
                              "lại để lần sau tìm.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 4, column = 0, sticky = tk.W, pady = (6, 0))
        self._hwndsumonhienthi = None

        # Nhiệm vụ Sư Gia (tactu_sugia_xq) cho nhân vật đang chọn
        nhom = self._taonhom(tab, "Nhiệm vụ Sư Gia (nhân vật đang chọn)")
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 0, column = 0, sticky = tk.W)
        self.btn_sugia = ttk.Button(hangnut, text = "🔎 Bắt đầu Sư Gia", command = self._battatsugia)
        self.btn_sugia.pack(side = tk.LEFT)
        self.lbl_sugia = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(560))
        self.lbl_sugia.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        tk.Label(nhom, text = "Bật ở trưởng nhóm (đi một mình cũng được), thành viên bật Theo sau (thành viên ở máy khác thì bật Sư Gia ở thành "
                              "viên: chỉ nhận / trả theo). Mỗi lượt: Chu Quốc (345, 159) Từ Phúc \"1. Hiệp trợ tiêu diệt\" → \"1. Nhận\" (thành "
                              "viên tự chọn \"1. Nhận\") → tới nước trong mô tả, dùng Truy Tìm Thổ Phỉ, đi theo hướng / độ xa game báo → thấy tội "
                              "phạm thì đánh → về Từ Phúc \"1. Tiêu diệt tội phạm...\" → \"1. Hoàn thành nhiệm vụ\" (thành viên cũng tự trả). "
                              "Dừng khi Từ Phúc báo đã đủ số lần trong ngày.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 2, column = 0, sticky = tk.W, pady = (6, 0))

        # Tự động đi Lăng Ly Sơn / Thành Kiều (tactu_langlyson_xq) cho nhân vật đang chọn
        nhom = self._taonhom(tab, "Phó bản Lăng Ly Sơn / Thành Kiều / Phong Yêu Kính (nhân vật đang chọn)")
        hangnut = tk.Frame(nhom)
        hangnut.grid(row = 0, column = 0, sticky = tk.W)
        self.btn_langlyson = ttk.Button(hangnut, text = "🏯 Bắt đầu Lăng Ly Sơn", command = lambda: self._battatlanglyson("langlyson"))
        self.btn_langlyson.pack(side = tk.LEFT)
        self.btn_thanhkieu = ttk.Button(hangnut, text = "⚔ Bắt đầu Thành Kiều", command = lambda: self._battatlanglyson("thanhkieu"))
        self.btn_thanhkieu.pack(side = tk.LEFT, padx = (8, 0))
        self.btn_phongyeukinh = ttk.Button(hangnut, text = "🪞 Bắt đầu Phong Yêu Kính", command = lambda: self._battatlanglyson("phongyeukinh"))
        self.btn_phongyeukinh.pack(side = tk.LEFT, padx = (8, 0))
        self.lbl_langlyson = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(560))
        self.lbl_langlyson.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        tk.Label(nhom, text = "Bật ở nhân vật trưởng nhóm (bật cả ở thành viên cũng được: thành viên chỉ đi theo), các thành viên bật Theo sau "
                              "(tự nói chuyện NPC vào / qua tầng, tự lĩnh thưởng). Mỗi vòng: "
                              "Thuý Hoa Sơn → Đào Vong Khổ Dịch vào Tầng Trên (đánh Tướng Quân Dũng, khởi động Cơ Quan Thạch, Cơ Quan Thạch Sư "
                              "sang tầng) → Tầng Dưới (Đường Truy, Thế Công Minh, Thạch Tướng Quân, Hào Quật, Lăng Mộ Thạch Sư) → Thư Phòng "
                              "(chờ đủ thành viên rồi mới đánh Cơ Quan Tướng Quân) → Hồi Thành Phù ra, Đào Vong Khổ Dịch lĩnh thưởng → tạm tắt "
                              "Tổ đội tự động, mọi người rời nhóm cũ, bật lại cho lập nhóm mới rồi đi vòng sau, tới khi bấm dừng. "
                              "Thành Kiều: trưởng nhóm tới Tần Quốc (220, 65) Thảo Nghịch Tướng Quân \"3. Sử dụng [Hạt Mè Khai Môn] tiến vào\" → "
                              "Xác nhận (cả nhóm được đưa vào) → Mã Quỷ, Lương Hưng, Yến Thập Tam, Tư Tà → chờ đủ thành viên đánh Thủ Lĩnh "
                              "Thành Kiều → Hồi Thành Phù về Tần Quốc \"4. Nhận thưởng\" → \"1. Nhận thưởng\" → đổi tổ đội như trên. Hết Hạt Mè Khai Môn thì dừng. "
                              "Phong Yêu Kính (bật ở mọi nhân vật trong nhóm; thành viên bật Theo sau thì đi theo, không bật thì tự đi lộ trình dò khắp bản đồ đánh quái như trưởng nhóm): người online đứng đầu nhóm Tổ đội tự động lập nhóm 1 người, tới Chu Quốc (252, 160) Tả Khâu Minh, give 1 món đồ theo cấu hình bên dưới (chỉ đồ trong túi, "
                              "chưa Phong Ấn, chọn món cấp thấp nhất) → \"1. Đúng vậy, ta muốn đi\" → mời các thành viên online của nhóm vào → mọi người "
                              "\"1. Đúng vậy, ta muốn vào\" → dò khắp bản đồ đánh hết quái, giết 2 boss (Vương Tàn Phách / Kính Ma) → Thỏ Yêu về Chu Quốc "
                              "→ đổi tổ đội như trên. Hết đồ được phép đốt thì dừng.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 2, column = 0, sticky = tk.W, pady = (6, 0))
        self._taocauhinhphongyeu(nhom)

        # Tập Kích Môn Phái (tactu_tapkich_xq) cho nhân vật đang chọn
        nhom = self._taonhom(tab, "Phó bản Tập Kích Môn Phái (nhân vật đang chọn)")
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 0, column = 0, sticky = tk.W)
        ttk.Label(hangnut, text = "Môn phái:").pack(side = tk.LEFT)
        self._tenphaitapkich = {ten: ma for ma, ten in TENMONPHAI.items()}
        self.str_phaitapkich = tk.StringVar()
        self.cbo_phaitapkich = ttk.Combobox(hangnut, textvariable = self.str_phaitapkich, values = list(self._tenphaitapkich), state = "readonly", width = 16)
        self.cbo_phaitapkich.pack(side = tk.LEFT, padx = 4)
        # Vừa chọn: (hwnd, môn phái, thời điểm) để chờ bot nhận, update_ui không nạp lại giá trị cũ đè lên
        self._phaitapkichchoxacnhan = None

        def on_chon_phaitapkich(event = None):
            hwnd = self.get_selected_hwnd()
            phai = self._tenphaitapkich.get(self.str_phaitapkich.get())
            if hwnd and phai:
                self.command_dict[hwnd] = f"set_tapkich_phai:{phai}"
                self._phaitapkichchoxacnhan = (hwnd, phai, time.time())

        self.cbo_phaitapkich.bind("<<ComboboxSelected>>", on_chon_phaitapkich)
        self.btn_tapkich = ttk.Button(hangnut, text = "🗡 Bắt đầu Tập Kích", command = self._battattapkich)
        self.btn_tapkich.pack(side = tk.LEFT, padx = (8, 0))
        self.lbl_tapkich = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(560))
        self.lbl_tapkich.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        tk.Label(nhom, text = "Bật ở trưởng nhóm (đi một mình cũng được), thành viên bật Theo sau (thành viên ở máy khác thì bật Tập Kích ở "
                              "thành viên: chỉ tự chọn menu vào / mua Lễ Bao). Mỗi vòng: tới bản đồ môn phái đã chọn, dò khắp bản đồ tìm "
                              "Võ Lâm Bại Hoại → \"1. Bớt nói nhảm đi, ta oánh nè !\" → \"1. Dùng 5 Ngân Bảo gia tăng 50% kinh nghiệm\" (thành "
                              "viên cũng tự chọn) → vào phó bản, hỏi mua Võ Lâm Bại Hoại Lễ Bao thì Xác Nhận → dò khắp bản đồ đánh hết quái "
                              "và Thủ Lĩnh Võ Lâm Bại Hoại → hệ thống đưa ra sau 15s → vòng sau, tới khi bấm dừng. Chọn vào 3 lần không "
                              "được đưa vào (hết Ngân Bảo / hết lượt) thì dừng.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 2, column = 0, sticky = tk.W, pady = (6, 0))

        # Đoạt Bảo Mã Tặc (tactu_matac_xq) cho nhân vật đang chọn
        nhom = self._taonhom(tab, "Đoạt Bảo Mã Tặc (nhân vật đang chọn)")
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 0, column = 0, sticky = tk.W)
        ttk.Label(hangnut, text = "Bản đồ:").pack(side = tk.LEFT)
        self.str_bandomatac = tk.StringVar()
        self.ent_bandomatac = ttk.Entry(hangnut, textvariable = self.str_bandomatac, width = 48)
        self.ent_bandomatac.pack(side = tk.LEFT, padx = 4)
        # Vừa sửa: (hwnd, chuỗi, thời điểm) để chờ bot nhận, update_ui không nạp lại giá trị cũ đè lên
        self._bandomatacchoxacnhan = None

        def on_luu_bandomatac(event = None):
            hwnd = self.get_selected_hwnd()
            chuoi = self.str_bandomatac.get().replace(":", " ").strip()
            if hwnd:
                self.command_dict[hwnd] = f"set_matac_bando:{chuoi}"
                self._bandomatacchoxacnhan = (hwnd, chuoi, time.time())

        self.ent_bandomatac.bind("<Return>", on_luu_bandomatac)
        self.ent_bandomatac.bind("<FocusOut>", on_luu_bandomatac)
        self.btn_matac = ttk.Button(hangnut, text = "🐎 Bắt đầu Mã Tặc", command = self._battatmatac)
        self.btn_matac.pack(side = tk.LEFT, padx = (8, 0))
        self.var_tubatmatac = tk.BooleanVar()
        # Vừa bấm: (hwnd, giá trị, thời điểm) để chờ bot nhận, update_ui không nạp lại giá trị cũ đè lên
        self._tubatmatacchoxacnhan = None

        def on_tubatmatac():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                giatri = self.var_tubatmatac.get()
                self.command_dict[hwnd] = f"set_matac_tubat:{int(giatri)}"
                self._tubatmatacchoxacnhan = (hwnd, giatri, time.time())

        ttk.Checkbutton(nhom, text = "Tự bật khi có tin", variable = self.var_tubatmatac, command = on_tubatmatac).grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        self.lbl_matac = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(560))
        self.lbl_matac.grid(row = 2, column = 0, sticky = tk.W, pady = (4, 0))
        tk.Label(nhom, text = "Hoạt động 10h, 14h, 18h, 22h thứ 4, 5, 7, chủ nhật. Mỗi nhân vật đi riêng, nhóm 1 người (tự rời nhóm cũ, lập nhóm 1 người; Tổ đội tự động nghỉ tới khi dừng). Bản đồ cách nhau dấu phẩy (vd \"Bờ Vô "
                              "Định Hà, Vô Định Hà 1\"), Enter để lưu; đang bật mà thấy tin hệ thống \"Đoạt Bảo Mã Tặc đã xuất hiện tại ...\" "
                              "thì tự điền thay (bật \"Tự bật khi có tin\" thì tin đó cũng tự bắt đầu, nếu nhân vật không đang làm sư môn / phó bản / "
                              "giao đồ...). Mỗi con: tới bản đồ, dò khắp bản đồ tìm Đoạt Bảo Mã Tặc → \"1. Khiêu chiến\" → vào phó bản "
                              "đánh tới chết → được đưa về → tìm con khác (dò hết bản đồ không thấy thì sang bản đồ kế). Đi hết danh sách "
                              "2 lượt không thấy con nào thì dừng.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 3, column = 0, sticky = tk.W, pady = (6, 0))

        # Nhiệm vụ Danh Vọng (tactu_danhvong_xq) cho nhân vật đang chọn
        nhom = self._taonhom(tab, "Nhiệm vụ Danh Vọng (nhân vật đang chọn)")
        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 0, column = 0, sticky = tk.W)
        self.btn_danhvong = ttk.Button(hangnut, text = "🏅 Bắt đầu Danh Vọng", command = self._battatdanhvong)
        self.btn_danhvong.pack(side = tk.LEFT)
        self.lbl_danhvong = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(560))
        self.lbl_danhvong.grid(row = 1, column = 0, sticky = tk.W, pady = (4, 0))
        tk.Label(nhom, text = "Nhận / trả ở Tề Tổng Quản, Tề Quốc (89, 168): \"1. Nhiệm vụ Danh vọng\" → \"1. Tiếp nhận\". Trang Bị Quân Đội: "
                              "mua vũ khí môn phái đúng cấp ở Chủ Tiệm Vũ Khí nước có môn phái đó (Vân Mộng Cốc - Nguỵ, Côn Luân - Tần, "
                              "Cấm Vệ Quân - Chu, Đường Môn - Hàn, Mao Sơn - Tề, Thục Sơn - Yên, Đào Hoa Nguyên - Triệu) rồi give Tề Tổng Quản. "
                              "Truy Sát Kẻ Phản Bội / Ám Sát: dùng Công Văn Truy Nã (hết thì mua ở Tạp Hóa Tề Quốc) tìm kẻ phản bội ở Tề Quốc, giết rồi về trả. "
                              "Thăm Hỏi <NPC>: tới NPC → \"1. Thăm Hỏi\" → \"1. Hoàn thành nhiệm vụ\". Làm tới khi bấm dừng / Tề Tổng Quản không giao nữa.",
                 fg = MAUCHU_PHU, justify = tk.LEFT, anchor = tk.W, wraplength = self._px(560)).grid(row = 2, column = 0, sticky = tk.W, pady = (6, 0))

    def _taocauhinhphongyeu(self, nhom):
        # Đồ đem đốt vào Phong Yêu Kính (file _internal/phongyeukinh.json, dùng chung mọi nhân vật trên máy; bot đọc lại khi file đổi):
        # màu tên, chỉ đồ chưa giám định, cấp tối thiểu so với cấp nhân vật, tên không bao giờ đốt / chỉ đốt
        cauhinh = taicauhinhphongyeu()
        khung = ttk.Frame(nhom)
        khung.grid(row = 3, column = 0, sticky = tk.W, pady = (8, 0))
        ttk.Label(khung, text = "Đồ đem đốt vào Phong Yêu Kính (dùng chung mọi nhân vật trên máy):").grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)
        self._var_phongyeu = {k: tk.BooleanVar(value = cauhinh[k]) for k in ("is_lamkim", "is_hoangkim", "is_chichuagiamdinh")}
        hangmau = ttk.Frame(khung)
        hangmau.grid(row = 1, column = 0, columnspan = 2, sticky = tk.W, pady = (2, 0))
        for khoa, chu in (("is_lamkim", "Lam Kim (chữ xanh)"), ("is_hoangkim", "Hoàng Kim (chữ vàng)"), ("is_chichuagiamdinh", "Chỉ đồ Chưa giám định")):
            ttk.Checkbutton(hangmau, text = chu, variable = self._var_phongyeu[khoa], command = self._luucauhinhphongyeu).pack(side = tk.LEFT, padx = (0, 12))
        hangcap = ttk.Frame(khung)
        hangcap.grid(row = 2, column = 0, columnspan = 2, sticky = tk.W, pady = (2, 0))
        ttk.Label(hangcap, text = "Cấp đồ ≥ cấp nhân vật −").pack(side = tk.LEFT)
        self._str_caphonphongyeu = tk.StringVar(value = str(cauhinh["caphonnhanvat"]))
        spin = ttk.Spinbox(hangcap, from_ = 0, to = 200, increment = 1, width = 5, textvariable = self._str_caphonphongyeu, command = self._luucauhinhphongyeu)
        spin.pack(side = tk.LEFT, padx = 4)
        ttk.Label(hangcap, text = "(và ≥ 15; quái trong phó bản = cấp đồ + 20)", foreground = MAUCHU_PHU).pack(side = tk.LEFT)
        self._str_phongyeu = {}
        for dong, (khoa, chu) in enumerate((("khongdot", "Không bao giờ đốt (tên chứa, cách nhau dấu phẩy):"),
                                            ("chidot", "Chỉ đốt (tên chứa; để trống = mọi món đúng điều kiện trên):")), start = 3):
            ttk.Label(khung, text = chu).grid(row = dong, column = 0, sticky = tk.W, pady = (2, 0))
            self._str_phongyeu[khoa] = tk.StringVar(value = ", ".join(cauhinh[khoa]))
            o = ttk.Entry(khung, textvariable = self._str_phongyeu[khoa], width = 40)
            o.grid(row = dong, column = 1, sticky = tk.W, padx = (4, 0), pady = (2, 0))
            o.bind("<FocusOut>", self._luucauhinhphongyeu)
            o.bind("<Return>", self._luucauhinhphongyeu)
        for su_kien in ("<FocusOut>", "<Return>"):
            spin.bind(su_kien, self._luucauhinhphongyeu)

    def _luucauhinhphongyeu(self, event = None):
        try:
            caphon = int(float(self._str_caphonphongyeu.get()))
        except ValueError:
            caphon = taicauhinhphongyeu()["caphonnhanvat"]
            self._str_caphonphongyeu.set(str(caphon))
        cauhinh = {k: v.get() for k, v in self._var_phongyeu.items()}
        cauhinh["caphonnhanvat"] = caphon
        for khoa, bien in self._str_phongyeu.items():
            cauhinh[khoa] = [t.strip() for t in bien.get().split(",") if t.strip()]
        luucauhinhphongyeu(cauhinh)

    def _battatlanglyson(self, phoban):
        # Đang đi phó bản nào thì nút nào cũng là dừng phó bản đó (mỗi nhân vật chỉ đi 1 phó bản 1 lúc)
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            from tkinter import messagebox
            messagebox.showwarning("Phó bản", "Chọn một nhân vật trong danh sách trước", parent = self.root)
            return
        info = self.shared_data.get(hwnd) or {}
        self.command_dict[int(hwnd)] = "huylanglyson" if info.get("_is_danglanglyson") else phoban

    def _capnhatlanglyson(self):
        hwnd = self.get_selected_hwnd()
        info = (self.shared_data.get(hwnd) or {}) if hwnd else {}
        dangdi = info.get("_phobanlanglyson") or ("langlyson" if info.get("_is_danglanglyson") else "")
        for nut, phoban, chubatdau, ten in ((self.btn_langlyson, "langlyson", "🏯 Bắt đầu Lăng Ly Sơn", "Lăng Ly Sơn"),
                                            (self.btn_thanhkieu, "thanhkieu", "⚔ Bắt đầu Thành Kiều", "Thành Kiều"),
                                            (self.btn_phongyeukinh, "phongyeukinh", "🪞 Bắt đầu Phong Yêu Kính", "Phong Yêu Kính")):
            chunut = f"⏹ Dừng {ten}" if dangdi == phoban else chubatdau
            trangthai = tk.DISABLED if dangdi and dangdi != phoban else tk.NORMAL
            if nut.cget("text") != chunut:
                nut.config(text = chunut)
            if str(nut.cget("state")) != trangthai:
                nut.config(state = trangthai)
        chu = info.get("_trangthailanglyson") or ""
        if self.lbl_langlyson.cget("text") != chu:
            self.lbl_langlyson.config(text = chu)

    def _battattapkich(self):
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            from tkinter import messagebox
            messagebox.showwarning("Tập Kích", "Chọn một nhân vật trong danh sách trước", parent = self.root)
            return
        info = self.shared_data.get(hwnd) or {}
        phai = self._tenphaitapkich.get(self.str_phaitapkich.get()) or info.get("_tapkich_phai") or ""
        self.command_dict[int(hwnd)] = "huytapkich" if info.get("_is_dangtapkich") else f"tapkich:{phai}"

    def _capnhattapkich(self):
        hwnd = self.get_selected_hwnd()
        info = (self.shared_data.get(hwnd) or {}) if hwnd else {}
        chunut = "⏹ Dừng Tập Kích" if info.get("_is_dangtapkich") else "🗡 Bắt đầu Tập Kích"
        if self.btn_tapkich.cget("text") != chunut:
            self.btn_tapkich.config(text = chunut)
        chu = info.get("_trangthaitapkich") or ""
        if self.lbl_tapkich.cget("text") != chu:
            self.lbl_tapkich.config(text = chu)
        # Môn phái của nhân vật đang chọn (vừa chọn tay thì chờ bot nhận, tối đa 3s, không nạp đè)
        cho = self._phaitapkichchoxacnhan
        if cho and (cho[0] != hwnd or info.get("_tapkich_phai") == cho[1] or time.time() - cho[2] > 3.):
            self._phaitapkichchoxacnhan = cho = None
        if not cho:
            ten = TENMONPHAI.get(info.get("_tapkich_phai") or "", "")
            if self.str_phaitapkich.get() != ten:
                self.str_phaitapkich.set(ten)

    def _battatdanhvong(self):
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            from tkinter import messagebox
            messagebox.showwarning("Danh Vọng", "Chọn một nhân vật trong danh sách trước", parent = self.root)
            return
        info = self.shared_data.get(hwnd) or {}
        self.command_dict[int(hwnd)] = "huydanhvong" if info.get("_is_dangdanhvong") else "danhvong"

    def _capnhatdanhvong(self):
        hwnd = self.get_selected_hwnd()
        info = (self.shared_data.get(hwnd) or {}) if hwnd else {}
        chunut = "⏹ Dừng Danh Vọng" if info.get("_is_dangdanhvong") else "🏅 Bắt đầu Danh Vọng"
        if self.btn_danhvong.cget("text") != chunut:
            self.btn_danhvong.config(text = chunut)
        chu = info.get("_trangthaidanhvong") or ""
        if self.lbl_danhvong.cget("text") != chu:
            self.lbl_danhvong.config(text = chu)

    def _battatmatac(self):
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            from tkinter import messagebox
            messagebox.showwarning("Mã Tặc", "Chọn một nhân vật trong danh sách trước", parent = self.root)
            return
        info = self.shared_data.get(hwnd) or {}
        self.command_dict[int(hwnd)] = "huymatac" if info.get("_is_dangmatac") else "matac"

    def _capnhatmatac(self):
        hwnd = self.get_selected_hwnd()
        info = (self.shared_data.get(hwnd) or {}) if hwnd else {}
        chunut = "⏹ Dừng Mã Tặc" if info.get("_is_dangmatac") else "🐎 Bắt đầu Mã Tặc"
        if self.btn_matac.cget("text") != chunut:
            self.btn_matac.config(text = chunut)
        chu = info.get("_trangthaimatac") or ""
        if self.lbl_matac.cget("text") != chu:
            self.lbl_matac.config(text = chu)
        # Bản đồ của nhân vật đang chọn (đang gõ thì không nạp đè; vừa lưu thì chờ bot nhận, tối đa 3s)
        cho = self._bandomatacchoxacnhan
        if cho and (cho[0] != hwnd or time.time() - cho[2] > 3.):
            self._bandomatacchoxacnhan = cho = None
        if not cho and self.root.focus_get() is not self.ent_bandomatac:
            chuoi = info.get("_matac_bandos") or ""
            if self.str_bandomatac.get() != chuoi:
                self.str_bandomatac.set(chuoi)
        cho = self._tubatmatacchoxacnhan
        if cho and (cho[0] != hwnd or bool(info.get("_is_tubatmatac")) == cho[1] or time.time() - cho[2] > 3.):
            self._tubatmatacchoxacnhan = cho = None
        if not cho and self.var_tubatmatac.get() != bool(info.get("_is_tubatmatac")):
            self.var_tubatmatac.set(bool(info.get("_is_tubatmatac")))

    def _battatsugia(self):
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            from tkinter import messagebox
            messagebox.showwarning("Sư Gia", "Chọn một nhân vật trong danh sách trước", parent = self.root)
            return
        info = self.shared_data.get(hwnd) or {}
        self.command_dict[int(hwnd)] = "huysugia" if info.get("_is_dangsugia") else "sugia"

    def _capnhatsugia(self):
        hwnd = self.get_selected_hwnd()
        info = (self.shared_data.get(hwnd) or {}) if hwnd else {}
        chunut = "⏹ Dừng Sư Gia" if info.get("_is_dangsugia") else "🔎 Bắt đầu Sư Gia"
        if self.btn_sugia.cget("text") != chunut:
            self.btn_sugia.config(text = chunut)
        chu = info.get("_trangthaisugia") or ""
        if self.lbl_sugia.cget("text") != chu:
            self.lbl_sugia.config(text = chu)

    def _battatsumon(self):
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            from tkinter import messagebox
            messagebox.showwarning("Sư môn", "Chọn một nhân vật trong danh sách trước", parent = self.root)
            return
        info = self.shared_data.get(hwnd) or {}
        self.command_dict[int(hwnd)] = "huysumon" if info.get("_is_dangsumon") else "sumon"

    def _capnhatsumon(self):
        hwnd = self.get_selected_hwnd()
        info = (self.shared_data.get(hwnd) or {}) if hwnd else {}
        chunut = "⏹ Dừng sư môn" if info.get("_is_dangsumon") else "📜 Bắt đầu sư môn"
        if self.btn_sumon.cget("text") != chunut:
            self.btn_sumon.config(text = chunut)
        chu = info.get("_trangthaisumon") or ""
        if self.lbl_sumon.cget("text") != chu:
            self.lbl_sumon.config(text = chu)
        macdinh = f"Đang dùng: {info.get('_npcgiaosumon') or '(chưa biết, nhập tên NPC)'}"
        if self.lbl_sumonnpcmacdinh.cget("text") != macdinh:
            self.lbl_sumonnpcmacdinh.config(text = macdinh)
        # Đổi nhân vật thì nạp lại ô NPC giao (đang gõ thì thôi)
        if info and hwnd != self._hwndsumonhienthi and self.root.focus_get() is not self.ent_sumonnpcgiao:
            self._hwndsumonhienthi = hwnd
            self.str_sumonnpcgiao.set(info.get("_sumon_npcgiao") or "")

    def _catkhongay(self):
        hwnd = self.get_selected_hwnd()
        if not hwnd:
            from tkinter import messagebox
            messagebox.showwarning("Cất kho", "Chọn một nhân vật trong danh sách trước", parent = self.root)
            return
        info = self.shared_data.get(hwnd) or {}
        self.command_dict[int(hwnd)] = "huycatkho" if info.get("_is_dangcatkho") else "catkho"

    def _capnhatgiaodo(self):
        # Vẽ lại khi hàng chờ giao của các nhân vật đổi (iid = "<hwnd>|<id yêu cầu>"); kèm trạng thái cất kho của nhân vật đang chọn
        from giaodo_xq import motayeucau
        hwndchon = self.get_selected_hwnd()
        infochon = (self.shared_data.get(hwndchon) or {}) if hwndchon else {}
        chucatkho = infochon.get("_trangthaicatkho") or ""
        if infochon.get("_is_dangcatkho"):
            chucatkho += " (bấm lại để huỷ)"
        if self.lbl_catkho.cget("text") != chucatkho:
            self.lbl_catkho.config(text = chucatkho)
        hangs = []
        for hwnd, info in dict(self.shared_data.items()).items():
            if not isinstance(info, dict):
                continue
            for y in info.get("_hangchogiaodo") or []:
                trangthai = y["trangthai"] + (f" ({y['ghichu']})" if y.get("ghichu") and y["trangthai"] == "lỗi" else "")
                tag = y["trangthai"] if y["trangthai"] in ("xong", "lỗi") else "dangchay"
                hangs.append((f"{hwnd}|{y['id']}", (info.get("tennhanvat") or "?", y["nguoinhan"], motayeucau(y), trangthai), tag))
        if hangs == self._giaododanghien:
            return
        self._giaododanghien = hangs
        dangchon = self.tree_giaodo.selection()
        self.tree_giaodo.delete(*self.tree_giaodo.get_children())
        for iid, values, tag in hangs:
            self.tree_giaodo.insert("", tk.END, iid = iid, values = values, tags = (tag,))
        if dangchon and self.tree_giaodo.exists(dangchon[0]):
            self.tree_giaodo.selection_set(dangchon[0])

    def _themgiaodo(self):
        from giaodo_xq import taoyeucau, docvatphams, doctien, guiyeucau
        cacnhanvat = {info.get("tennhanvat"): hwnd for hwnd, info in dict(self.shared_data.items()).items() if isinstance(info, dict) and info.get("tennhanvat")}
        if not cacnhanvat:
            from tkinter import messagebox
            messagebox.showwarning("Giao tiền / đồ", "Chưa có nhân vật nào chạy bot trên máy này", parent = self.root)
            return
        hwndchon = self.get_selected_hwnd()
        nguoigiao = (self.shared_data.get(hwndchon) or {}).get("tennhanvat") if hwndchon else None
        tenbiet = sorted(set(self._tentheoid().values()) - {nguoigiao})
        # "Tất cả nhân vật trên máy": mỗi nhân vật (trừ chính người nhận) 1 yêu cầu riêng
        TATCA = "Tất cả nhân vật trên máy"
        truongs = [("nguoigiao", "Người giao (nhân vật trên máy này)", [TATCA] + sorted(cacnhanvat)), ("nguoinhan", "Người nhận", tenbiet),
                   ("tien", "Ngân lượng: giữ 10k = giao hết chừa 10k · hết · 500k", None), ("vatphams", "Vật phẩm", None)]

        def kiemtra(kq):
            if kq["nguoigiao"] not in cacnhanvat and kq["nguoigiao"] != TATCA:
                return "Chọn người giao trong danh sách"
            if not kq["nguoinhan"].strip():
                return "Nhập tên người nhận"
            if kq["nguoinhan"].strip() == kq["nguoigiao"]:
                return "Người nhận trùng người giao"
            tien = doctien(kq["tien"])
            if tien is None:
                return "Không đọc được tiền (vd giữ 10k, hết, 500k, 1.5tr)"
            if not tien[0] and tien[1] is None and not docvatphams(kq["vatphams"]):
                return "Chưa có tiền hay đồ nào để giao"
            return None

        kq = self._hopthoaituido("Giao tiền / đồ", truongs, {"nguoigiao": nguoigiao or "", "tien": "giữ 10k", "vatphams": []}, kiemtra, nhieudongs = {"vatphams": "mỗi dòng 1 món: Tên x 50 / x hết / x giữ 20"})
        if not kq:
            return
        tien, giulai = doctien(kq["tien"])
        nguoigiaos = [ten for ten in cacnhanvat if ten != kq["nguoinhan"].strip()] if kq["nguoigiao"] == TATCA else [kq["nguoigiao"]]
        for ten in nguoigiaos:
            guiyeucau(self.command_dict, cacnhanvat[ten], taoyeucau(kq["nguoinhan"], tien, docvatphams(kq["vatphams"]), giulaitien = giulai))

    def _vegiaongay(self, is_tatca = False):
        # Yêu cầu giao đang chờ của nhân vật (dòng đang chọn trong bảng giao, không thì nhân vật đang chọn ở danh sách trên; is_tatca: mọi
        # nhân vật có yêu cầu đang chờ) về giao ngay
        if is_tatca:
            hwnds = [hwnd for hwnd, info in dict(self.shared_data.items()).items() if isinstance(info, dict)
                     and any(y["trangthai"] not in ("xong", "lỗi") for y in info.get("_hangchogiaodo") or [])]
        else:
            chon = self.tree_giaodo.selection()
            hwnds = [int(chon[0].split("|", 1)[0])] if chon else [self.get_selected_hwnd()] if self.get_selected_hwnd() else []
        if not hwnds:
            from tkinter import messagebox
            messagebox.showwarning("Về giao ngay", "Chọn một dòng trong bảng giao (hoặc một nhân vật) trước", parent = self.root)
            return
        for hwnd in hwnds:
            self.command_dict[int(hwnd)] = "vegiao"

    def _huygiaodo(self):
        chon = self.tree_giaodo.selection()
        if chon:
            hwnd, idyeucau = chon[0].split("|", 1)
            self.command_dict[int(hwnd)] = f"huygiaodo:{idyeucau}"

    def _hienluattuido(self, chonluat = None, chonmuabu = None, choncatkho = None):
        dulieu = tailuat()
        self.tree_luattuido.delete(*self.tree_luattuido.get_children())
        for i, luat in enumerate(dulieu["luat"]):
            self.tree_luattuido.insert("", tk.END, iid = str(i), values = ("✔" if luat["bat"] else "", "📣" if luat["is_bao"] else "", TENHANHDONG[luat["hanhdong"]],
                                                                          motaluat(luat), luat["ghichu"]))
        self.tree_catkho.delete(*self.tree_catkho.get_children())
        for i, luat in enumerate(dulieu["catkho"]):
            self.tree_catkho.insert("", tk.END, iid = str(i), values = ("✔" if luat["bat"] else "", motaluat(luat),
                                                                       f"Rương {luat['ruong']}" if luat["ruong"] else "Tự động",
                                                                       luat["giulai"] or "", luat["ghichu"]))
        self.var_catkhosauban.set(dulieu["is_catkhosauban"])
        if choncatkho is not None and self.tree_catkho.exists(str(choncatkho)):
            self.tree_catkho.selection_set(str(choncatkho))
        self.tree_muabu.delete(*self.tree_muabu.get_children())
        for i, muc in enumerate(dulieu["muabu"]):
            self.tree_muabu.insert("", tk.END, iid = str(i), values = ("✔" if muc["bat"] else "",
                                                                       muc["vatpham"] + (f" ({muc['tencuahang']})" if muc["tencuahang"] else ""), muc["npc"],
                                                                       muc["xepchong"], muc["duoi"], muc["muatoi"], TENMONPHAI.get(muc["monphai"], muc["monphai"]) or "Tất cả",
                                                                       "Luôn" if muc["chikhi"] == CHIKHI_LUON else "Triệu hồi bảo thú"))
        for tree, chon in ((self.tree_luattuido, chonluat), (self.tree_muabu, chonmuabu)):
            if chon is not None and tree.exists(str(chon)):
                tree.selection_set(str(chon))

    def _luutuido(self, dulieu, chonluat = None, chonmuabu = None, choncatkho = None):
        try:
            luuluat(dulieu)
        except OSError as err:
            from tkinter import messagebox
            messagebox.showerror("Luật túi đồ", f"Không lưu được: {err}", parent = self.root)
            return
        self._hienluattuido(chonluat, chonmuabu, choncatkho)

    def _doicatkhosauban(self):
        self._luutuido(dict(tailuat(), is_catkhosauban = bool(self.var_catkhosauban.get())))

    def _suacatkho(self, is_moi):
        dulieu = tailuat()
        chon = self.tree_catkho.selection()
        if not is_moi and not chon:
            return
        vitri = None if is_moi else int(chon[0])
        luat = {"bat": True, "ruong": 0, "giulai": 0} if is_moi else dict(dulieu["catkho"][vitri])
        luat["ruong"] = f"Rương {luat['ruong']}" if luat.get("ruong") else "Tự động"
        luat["giulai"] = str(luat.get("giulai") or 0)
        cacruong = ["Tự động"] + [f"Rương {r}" for r in range(1, 11)]
        # Form 2 cột, xếp theo cặp: Bật | Ghi chú, Rương | Giữ lại, Tên đúng | Tên chứa, Loại chứa | Mô tả chứa
        truongs = [("bat", "Bật", None), ("ghichu", "Ghi chú", None), ("ruong", "Rương", cacruong),
                   ("giulai", "Giữ lại trong túi (cái)", None)] + [(d, TENDIEUKIEN[d], None) for d in DIEUKIENs]

        def docruong(chu):
            chu = chu.strip().lower().replace("rương", "").strip()
            return 0 if chu in ("tự động", "tudong", "", "0") else int(chu) if chu.isdigit() else None

        def kiemtra(kq):
            if docruong(kq["ruong"]) is None:
                return "Rương: chọn Tự động hoặc Rương 1, 2, ..."
            if not kq["giulai"].strip().isdigit():
                return "Giữ lại phải là số (0 = cất hết)"
            if not any(kq[d].strip() for d in DIEUKIENs):
                return "Cần ít nhất 1 điều kiện (tên đúng / tên chứa / loại / mô tả), không thì luật không khớp món nào"
            return None

        kq = self._hopthoaituido("Thêm luật cất kho" if is_moi else "Sửa luật cất kho", truongs, luat, kiemtra, nhieudongs = DIEUKIENs)
        if not kq:
            return
        kq["ruong"], kq["giulai"] = docruong(kq["ruong"]), int(kq["giulai"])
        dulieu = tailuat()
        luats = list(dulieu["catkho"])
        if is_moi:
            luats.append(kq)
            vitri = len(luats) - 1
        else:
            luats[vitri] = kq
        self._luutuido(dict(dulieu, catkho = luats), choncatkho = vitri)

    def _xoamuctuido(self, khoa, tree):
        chon = tree.selection()
        if not chon:
            return
        dulieu = tailuat()
        danhsach = list(dulieu[khoa])
        danhsach.pop(int(chon[0]))
        self._luutuido(dict(dulieu, **{khoa: danhsach}))

    def _doichomuctuido(self, huong):
        chon = self.tree_luattuido.selection()
        if not chon:
            return
        dulieu = tailuat()
        luats = list(dulieu["luat"])
        i, j = int(chon[0]), int(chon[0]) + huong
        if not 0 <= j < len(luats):
            return
        luats[i], luats[j] = luats[j], luats[i]
        self._luutuido(dict(dulieu, luat = luats), chonluat = j)

    def _hopthoaituido(self, tieude, truongs, giatris, kiemtra, nhieudongs = (), matkhaus = ()):
        # Hộp thoại sửa 1 mục: truongs = [(khoá, nhãn, danh sách gợi ý hoặc None)], giatris = {khoá: giá trị}. Bấm Lưu thì gọi
        # kiemtra(kết quả) -> chuỗi lỗi (giữ hộp thoại) hoặc None (đóng, trả kết quả). Trả về dict hoặc None khi huỷ.
        # Khoá trong nhieudongs là ô nhiều dòng (danh sách, mỗi dòng 1 giá trị), kết quả là chuỗi các dòng
        from tkinter import messagebox
        hop = tk.Toplevel(self.root)
        hop.title(tieude)
        hop.transient(self.root)
        hop.attributes("-topmost", True)
        khung = ttk.Frame(hop, padding = 12)
        khung.pack(fill = tk.BOTH, expand = True)
        khung.columnconfigure(0, weight = 1, uniform = "cot")
        khung.columnconfigure(1, weight = 1, uniform = "cot")
        bien = {}
        # Form 2 cột: các ô xếp lần lượt trái rồi phải, mỗi ô có nhãn ở trên, ô nhập ở dưới; ô đánh dấu thì nhãn nằm ngay cạnh ô
        dong = 0
        for thutu, (khoa, nhan, goiy) in enumerate(truongs):
            dong, cot = divmod(thutu, 2)
            o_ = ttk.Frame(khung)
            o_.grid(row = dong, column = cot, sticky = tk.NSEW, padx = (0, 10) if cot == 0 else (0, 0), pady = (0, 8))
            if khoa in ("bat", "is_bao"):
                bien[khoa] = tk.BooleanVar(value = bool(giatris.get(khoa, khoa == "bat")))
                ttk.Checkbutton(o_, text = nhan, variable = bien[khoa]).pack(anchor = tk.W, pady = (2, 0))
                continue
            ttk.Label(o_, text = nhan, font = (FONTCHU, COCHU, "bold")).pack(anchor = tk.W)
            if khoa in nhieudongs:
                ttk.Label(o_, text = nhieudongs.get(khoa) if isinstance(nhieudongs, dict) else "mỗi dòng 1 giá trị, khớp 1 dòng là đủ", style = "Phu.TLabel").pack(anchor = tk.W)
                # Text không có .get() kiểu biến Tk: bọc lại để on_luu đọc chung một kiểu
                khungchu = ttk.Frame(o_)
                khungchu.pack(fill = tk.BOTH, expand = True, pady = (2, 0))
                o = tk.Text(khungchu, width = 30, height = 6, wrap = tk.NONE, font = (FONTCHU, COCHU))
                thanhcuon = ttk.Scrollbar(khungchu, orient = tk.VERTICAL, command = o.yview)
                o.configure(yscrollcommand = thanhcuon.set)
                o.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
                thanhcuon.pack(side = tk.RIGHT, fill = tk.Y)
                giatri = giatris.get(khoa) or []
                o.insert("1.0", "\n".join(giatri) if isinstance(giatri, list) else str(giatri))
                bien[khoa] = types.SimpleNamespace(get = lambda o = o: o.get("1.0", tk.END).strip())
                continue
            bien[khoa] = tk.StringVar(value = str(giatris.get(khoa, "")))
            o = ttk.Combobox(o_, textvariable = bien[khoa], values = goiy) if goiy else ttk.Entry(o_, textvariable = bien[khoa], show = "•" if khoa in matkhaus else "")
            o.pack(fill = tk.X, pady = (2, 0))
        dong += 1
        ketqua = {}

        def on_luu():
            dulieu = {khoa: v.get() for khoa, v in bien.items()}
            loi = kiemtra(dulieu)
            if loi:
                messagebox.showwarning(tieude, loi, parent = hop)
                return
            ketqua.update(dulieu)
            hop.destroy()

        hangnut = ttk.Frame(khung)
        hangnut.grid(row = dong, column = 0, columnspan = 2, sticky = tk.E, pady = (4, 0))
        ttk.Button(hangnut, text = "Lưu", command = on_luu).pack(side = tk.LEFT, padx = (0, 4))
        ttk.Button(hangnut, text = "Huỷ", command = hop.destroy).pack(side = tk.LEFT)
        hop.grab_set()
        self.root.wait_window(hop)
        return ketqua or None

    def _sualuattuido(self, is_moi):
        dulieu = tailuat()
        chon = self.tree_luattuido.selection()
        if not is_moi and not chon:
            return
        vitri = None if is_moi else int(chon[0])
        luat = {"bat": True, "hanhdong": "giu"} if is_moi else dict(dulieu["luat"][vitri])
        tentheohanhdong = {ten: ma for ma, ten in TENHANHDONG.items()}
        luat["hanhdong"] = TENHANHDONG.get(luat.get("hanhdong"), TENHANHDONG["giu"])
        # Form 2 cột, xếp theo cặp: Bật | 📣, Hành động | Ghi chú, Tên đúng | Tên chứa, Loại chứa | Mô tả chứa
        truongs = [("bat", "Bật", None), ("is_bao", "📣 Báo Telegram khi nhặt được", None),
                   ("hanhdong", "Hành động", list(TENHANHDONG.values())), ("ghichu", "Ghi chú", None)]
        truongs += [(d, TENDIEUKIEN[d], None) for d in DIEUKIENs]

        def kiemtra(kq):
            if kq["hanhdong"] not in tentheohanhdong:
                return "Chọn hành động trong danh sách"
            if not any(kq[d].strip() for d in DIEUKIENs):
                return "Cần ít nhất 1 điều kiện (tên đúng / tên chứa / loại / mô tả), không thì luật không khớp món nào"
            return None

        kq = self._hopthoaituido("Thêm luật túi đồ" if is_moi else "Sửa luật túi đồ", truongs, luat, kiemtra, nhieudongs = DIEUKIENs)
        if not kq:
            return
        kq["hanhdong"] = tentheohanhdong[kq["hanhdong"]]
        dulieu = tailuat()
        luats = list(dulieu["luat"])
        if is_moi:
            luats.append(kq)
            vitri = len(luats) - 1
        else:
            luats[vitri] = kq
        self._luutuido(dict(dulieu, luat = luats), chonluat = vitri)

    def _suamuabu(self, is_moi):
        dulieu = tailuat()
        chon = self.tree_muabu.selection()
        if not is_moi and not chon:
            return
        vitri = None if is_moi else int(chon[0])
        muc = {"bat": True, "npc": CHUTIEMTAPHOA, "xepchong": XEPCHONGMACDINH} if is_moi else dict(dulieu["muabu"][vitri])
        machikhi = {ten: ma for ma, ten in TENCHIKHI.items()}
        muc["chikhi"] = TENCHIKHI.get(muc.get("chikhi"), TENCHIKHI[CHIKHI_LUON])
        # Môn phái: hiện tên có dấu, lưu mã ("" = mọi môn phái)
        mamonphai = {"Tất cả": "", **{ten: ma for ma, ten in TENMONPHAI.items()}}
        muc["monphai"] = TENMONPHAI.get(muc.get("monphai"), muc.get("monphai")) or "Tất cả"
        goiys = {"npc": [CHUTIEMTAPHOA, CHUTUULAU], "monphai": list(mamonphai), "chikhi": list(TENCHIKHI.values())}
        # Form 2 cột, xếp theo cặp: Vật phẩm | Tên ở cửa hàng, NPC | Xếp chồng tối đa, Mua khi dưới | Mua cho đủ, Môn phái | Chỉ mua khi, Bật
        truongs = [(t, TENTRUONGMUABU[t], goiys.get(t)) for t in TRUONGMUABU] + [("bat", "Bật", None)]

        def kiemtra(kq):
            if kq["chikhi"] not in machikhi:
                return "Chọn \"Chỉ mua khi\" trong danh sách"
            if kq["monphai"].strip() not in mamonphai and kq["monphai"].strip():
                return "Chọn môn phái trong danh sách (hoặc Tất cả)"
            if not kq["vatpham"].strip() or not kq["npc"].strip():
                return "Cần tên vật phẩm và tên NPC bán"
            for t in ("xepchong", "duoi", "muatoi"):
                if not kq[t].strip().isdigit() or int(kq[t]) <= 0:
                    return f"\"{TENTRUONGMUABU[t]}\" phải là số lớn hơn 0"
            if int(kq["duoi"]) > int(kq["muatoi"]):
                return "\"Mua khi dưới\" không được lớn hơn \"Mua cho đủ\""
            return None

        kq = self._hopthoaituido("Thêm mua bù" if is_moi else "Sửa mua bù", truongs, muc, kiemtra)
        if not kq:
            return
        kq["chikhi"] = machikhi[kq["chikhi"]]
        kq["monphai"] = mamonphai.get(kq["monphai"].strip(), "")
        dulieu = tailuat()
        mucs = list(dulieu["muabu"])
        if is_moi:
            mucs.append(kq)
            vitri = len(mucs) - 1
        else:
            mucs[vitri] = kq
        self._luutuido(dict(dulieu, muabu = mucs), chonmuabu = vitri)

    @staticmethod
    def _sogon(so):
        # Đủ con số, dấu chấm ngăn hàng nghìn: 6.300.000
        return f"{round(so):,}".replace(",", ".")

    def _tyletheogio(self, so, giay):
        return self._sogon(so * 3600. / giay) if giay >= 60 else "-"

    # ------------------------------------------------------------------ Dữ liệu

    def _laylotrinhmau(self):
        # Đọc lại file lộ trình mẫu chỉ khi file thay đổi
        try:
            thoidiemsua = os.path.getmtime(duongdanlotrinhmau())
        except OSError:
            thoidiemsua = None
        dulieu, thoidiemcu = self._lotrinhmau_cache
        if thoidiemsua != thoidiemcu:
            dulieu = tailotrinhmau() if thoidiemsua else {}
            self._lotrinhmau_cache = (dulieu, thoidiemsua)
        return dulieu

    def get_selected_hwnd(self):
        selected = self.tree.selection()
        if selected:
            return int(selected[0])
        elif self.tree.get_children():
            return int(self.tree.get_children()[0])
        return None

    def update_ui(self):
        try:
            self._capnhatdanhsachnhanvat()
            self._capnhatdangnhap()
            self._capnhatbangdieukhien()
            self._capnhatgiaodo()
            self._capnhatsumon()
            self._capnhatlanglyson()
            self._capnhatsugia()
            self._capnhattapkich()
            self._capnhatmatac()
            self._capnhatdanhvong()
            self._capnhattodoimotlan()
            # Nội dung có thể cao lên/thấp xuống (dòng tạm ngưng, danh sách tài khoản...) mà Canvas không tự biết
            for tabcuon in self._tabcuons:
                self._capnhatcuontab(*tabcuon)
        finally:
            self.root.after(500, self.update_ui)

    def _capnhatdanhsachnhanvat(self):
        dulieu = dict(self.shared_data.items())

        # Tự chọn nhân vật của cửa sổ game đang được kích hoạt
        current_active_hwnd = next((str(hwnd) for hwnd, info in dulieu.items() if info.get("is_window_active")), None)
        chonmoi = None
        if current_active_hwnd and current_active_hwnd != self.last_active_hwnd:
            chonmoi = current_active_hwnd
            self.last_active_hwnd = current_active_hwnd

        # Cập nhật tại chỗ (không xoá/vẽ lại cả bảng nên không bị nháy, không mất vị trí cuộn)
        hienco = set(self.tree.get_children())
        for hwnd, info in dulieu.items():
            iid = str(hwnd)
            phien = info.get("_thongkephien") or {}
            giay = phien.get("giay", 0)
            values = (
                hwnd,
                info.get("tennhanvat") or "Đang tải...",
                f"{info.get('phantramsinhluc', 0)}%",
                f"{info.get('phantramnoiluc', 0)}%",
                laytenbando(info.get("tenbando")) if info.get("tenbando") is not None else "-",
                "⏸ Tạm ngưng" if info.get("_thoigiantamngungconlai", 0) > 0 else info.get("status", "-"),
                self._sogon(info["nganluong"]) if info.get("nganluong") is not None else "-",
                self._tyletheogio(phien.get("nganluong", 0), giay),
            )
            if info.get("status") == "Đã chết":
                tags = ("chet",)
            elif info.get("_thoigiantamngungconlai", 0) > 0:
                tags = ("tamngung",)
            elif (info.get("phantramsinhluc") or 100) < NGUONGMAUTHAP:
                tags = ("mauthap",)
            else:
                tags = ()
            if iid in hienco:
                if tuple(str(v) for v in self.tree.item(iid, "values")) != tuple(str(v) for v in values) or tuple(self.tree.item(iid, "tags")) != tags:
                    self.tree.item(iid, values = values, tags = tags)
                hienco.discard(iid)
            else:
                self.tree.insert("", tk.END, iid = iid, values = values, tags = tags)
        for iid in hienco:
            self.tree.delete(iid)

        if chonmoi and self.tree.exists(chonmoi):
            self.tree.selection_set(chonmoi)
        elif not self.tree.selection() and self.tree.get_children():
            self.tree.selection_set(self.tree.get_children()[0])

    def _capnhatbangdieukhien(self):
        hwnd_to_show = self.get_selected_hwnd()
        if not hwnd_to_show or hwnd_to_show not in self.shared_data:
            self.lbl_dangdieukhien.config(text = "Chưa có nhân vật")
            self.lbl_vitri.config(text = "")
            return
        info = self.shared_data[hwnd_to_show]

        idbando = info.get("tenbando")
        tenbando = laytenbando(idbando) if idbando is not None else "-"
        self.lbl_dangdieukhien.config(text = f"Đang điều khiển: {info.get('tennhanvat') or 'Đang tải...'}")
        self.lbl_vitri.config(text = f"{tenbando} ({info.get('x', 0)}, {info.get('y', 0)})  ·  {info.get('status', '-')}")

        conlai = info.get("_thoigiantamngungconlai", 0)
        if conlai > 0:
            self.lbl_tamngung.config(text = f"⏸ TẠM NGƯNG – {info.get('_lydotamngung', '')}\nTự chạy lại sau {int(conlai) // 60}:{int(conlai) % 60:02d}")
            if not self.frame_tamngung.winfo_ismapped():
                self.frame_tamngung.pack(fill = tk.X, pady = (6, 0))
        elif self.frame_tamngung.winfo_ismapped():
            self.frame_tamngung.pack_forget()

        for ten, khoa in (
                ("sudungkynang", "_is_tudongsudungkynang"),
                ("gomquai", "_is_tudonggomquai"),
                ("vebanrac", "_is_tudongvebanrac"),
                ("theosau", "_is_tudongtheosau"),
                ("todoitudong", "_is_tudongtodoi"),
                ("timmuctieu", "_is_tudongtimkiemmuctieu"),
                ("trieuhoibaothu", "_is_tudongtrieuhoibaothugiangho"),
                ("sudungkynangbaothu", "_is_tudongsudungkynangbaothu"),
                ("tranhvungcam", "_is_tranhvungcam"),
                ("dilotrinhkhacbando", "_is_dilotrinhkhacbando"),
                ("giukhoangcachketancong", "_is_giukhoangcachketancong"),
                ("giukhoangcachchimuctieupk", "_is_giukhoangcachchimuctieupk"),
                ("taphoa", "_is_taphoa"),
                ("timmuctieuchung", "_is_timmuctieuchung"),
                ("tutimduongtheosau", "_is_tutimduongtheosau"),
                ("doidotrieuhoi", "_is_doidokhitrieuhoi"),
                ("khaikhoang", "_is_tudongkhaikhoang"),
                ("chientruong", "_is_tudongdichientruong"),
                ("daobaodo", "_is_tudongdaotangbaodo"),
                ("chidanhnguoichoi", "_is_chidanhnguoichoi"),
                ("uutienmaoson", "_is_uutienbaothukynangtrieuhoi"),
                ("bufftoanbang", "_is_chedobufftoanbang"),
                ("chantangcap", "_is_chantangcapdo"),
                ("diemdanhxungquanh", "_is_tudongdichuyendiemdanhxungquanh")):
            self.vars[ten].set(info.get(khoa, False))
        phamchatnhats = info.get("_phamchatnhats") or []
        for ma, bien in self.vars_phamchat.items():
            bien.set(ma in phamchatnhats)

        self.btn_sapxephanhtrang.config(text = "Dừng sắp xếp" if info.get("_is_dangsapxephanhtrang") else "Sắp xếp hành trang")
        choxacnhan = self._baothutrieuhoichoxacnhan
        if choxacnhan and (choxacnhan[0] != hwnd_to_show or info.get("_baothutrieuhoimaoson") == choxacnhan[1] or time.time() - choxacnhan[2] > 5.):
            self._baothutrieuhoichoxacnhan = choxacnhan = None
        if not choxacnhan and info.get("_baothutrieuhoimaoson") in BAOTHUTRIEUHOIMAOSONs and self.str_baothutrieuhoi.get() != info["_baothutrieuhoimaoson"]:
            self.str_baothutrieuhoi.set(info["_baothutrieuhoimaoson"])
        choxacnhan = self._nguocchieuchoxacnhan
        if choxacnhan and (choxacnhan[0] != hwnd_to_show or info.get("_is_nguocchieulotrinh") == choxacnhan[1] or time.time() - choxacnhan[2] > 5.):
            self._nguocchieuchoxacnhan = choxacnhan = None
        if not choxacnhan and "_is_nguocchieulotrinh" in info and self.var_nguocchieu.get() != bool(info["_is_nguocchieulotrinh"]):
            self.var_nguocchieu.set(bool(info["_is_nguocchieulotrinh"]))
        tenbodos = info.get("_tenbodotrieuhoi") or []
        self.lbl_bodotrieuhoi.config(text = ", ".join(tenbodos) if tenbodos else "(chưa ghi bộ đồ)")

        try:
            widgetdangfocus = self.root.focus_get()
        except KeyError:
            # Focus đang ở danh sách thả xuống của ttk.Combobox (widget nội bộ của Tk), tkinter không tra được tên
            widgetdangfocus = None

        if widgetdangfocus != getattr(self, 'spin_khoangcachgiuketancong', None):
            try:
                giukhoangcach_moi = info.get("_khoangcachgiuketancong", KHOANGCACHGIUKETANCONG)
                if abs(self.vars["khoangcachgiuketancong"].get() - giukhoangcach_moi) > 0.01:
                    self.vars["khoangcachgiuketancong"].set(giukhoangcach_moi)
            except tk.TclError:
                pass

        if widgetdangfocus != getattr(self, 'spin_bankinhdiemdanh', None):
            try:
                bankinh_moi = info.get("_bankinhdiemdanh", 18.0)
                if abs(self.vars["bankinhdiemdanh"].get() - bankinh_moi) > 0.01:
                    self.vars["bankinhdiemdanh"].set(bankinh_moi)
            except tk.TclError:
                pass

        if widgetdangfocus != getattr(self, 'spin_khoangcachtamxa', None):
            try:
                tamxa_moi = info.get("_khoangcachsudungkynangtamxa", KHOANGCACHSUDUNGKYNANGTAMXA)
                if abs(self.vars["khoangcachtamxa"].get() - tamxa_moi) > 0.01:
                    self.vars["khoangcachtamxa"].set(tamxa_moi)
            except tk.TclError:
                pass

        if widgetdangfocus != getattr(self, 'spin_phantramnoiluckhaithien', None):
            try:
                khaithien_moi = info.get("_phantramnoiluckhaithientichdia", PHANTRAMNOILUCKHAITHIENTICHDIA)
                if abs(self.vars["phantramnoiluckhaithien"].get() - khaithien_moi) > 0.01:
                    self.vars["phantramnoiluckhaithien"].set(khaithien_moi)
            except tk.TclError:
                pass

        if widgetdangfocus != getattr(self, 'spin_khoangcach', None):
            try:
                kc_moi = info.get("_khoangcachtoidatheosau", 9.0)
                if abs(self.vars["khoangcachtheosau"].get() - kc_moi) > 0.01:
                    self.vars["khoangcachtheosau"].set(kc_moi)
            except tk.TclError:
                pass

        self._capnhatdanhsachmuctieu(hwnd_to_show, info)
        self._capnhatmuctieuboqua(info)
        self._capnhatmuctieutheosau(hwnd_to_show, info)

        self._capnhatlotrinhmau(hwnd_to_show, info, idbando, tenbando)
        self._capnhatdiemdanh(info)
        self._capnhattodoi(info)

    @staticmethod
    def _tenhienthimuctieutheosau(idnguoichoi, ten):
        return f"{idnguoichoi} - {ten}" if idnguoichoi else TEN_MUCTIEUMACDINH

    def _napdanhsachmuctieutheosau(self):
        # Gọi lúc mở ô chọn: trưởng nhóm và các nhân vật khác đang chạy trên cùng máy (cộng người đang theo sau nếu cửa sổ đó đã tắt)
        hwnd = self.get_selected_hwnd()
        info = self.shared_data.get(hwnd) if hwnd else None
        if not isinstance(info, dict):
            return
        danhsach = {0: ""}
        if info.get("_idmuctieutheosau"):
            danhsach[info["_idmuctieutheosau"]] = info.get("_tenmuctieutheosau") or ""
        for idcuaso, infokhac in list(self.shared_data.items()):
            if idcuaso != hwnd and isinstance(infokhac, dict) and infokhac.get("idnguoichoi"):
                danhsach[infokhac["idnguoichoi"]] = infokhac.get("tennhanvat") or ""
        danhsach.pop(info.get("idnguoichoi"), None)

        self._muctieutheosau_map = {self._tenhienthimuctieutheosau(idnguoichoi, ten): (idnguoichoi, ten)
                                    for idnguoichoi, ten in sorted(danhsach.items(), key = lambda x: (x[0] != 0, x[1].lower()))}
        self.cbo_muctieutheosau.config(values = list(self._muctieutheosau_map))

    def _capnhatmuctieutheosau(self, hwnd_to_show, info):
        idmuctieu = info.get("_idmuctieutheosau", 0)
        chonxacnhan = self._muctieutheosauchoxacnhan
        if chonxacnhan:
            hwndchon, idchon, thoidiemchon = chonxacnhan
            if hwndchon == hwnd_to_show and idchon != idmuctieu and time.time() - thoidiemchon < 3.:
                return
            self._muctieutheosauchoxacnhan = None
        tenhienthi = self._tenhienthimuctieutheosau(idmuctieu, info.get("_tenmuctieutheosau") or "")
        if self.str_muctieutheosau.get() != tenhienthi:
            self._muctieutheosau_map.setdefault(tenhienthi, (idmuctieu, info.get("_tenmuctieutheosau") or ""))
            self.str_muctieutheosau.set(tenhienthi)

    def _capnhattodoi(self, info):
        self._hientodoi()
        idnguoichoi = info.get("idnguoichoi")
        nhoms = laynhomtodoitudongs()
        sonhom = next((i for i, nhom in enumerate(nhoms) if idnguoichoi in nhom), None)
        if sonhom is not None:
            text = (f"Đang chọn: {info.get('tennhanvat') or ''} (ID {idnguoichoi}) ở nhóm {sonhom + 1}, "
                    f"thứ {nhoms[sonhom].index(idnguoichoi) + 1} ưu tiên làm trưởng nhóm")
            if self.tree_todoi.exists(str(sonhom)) and not self.tree_todoi.selection():
                self.tree_todoi.selection_set(str(sonhom))
        else:
            text = f"Đang chọn: {info.get('tennhanvat') or ''} (ID {idnguoichoi}) chưa có trong nhóm nào"
        if self.lbl_idnhanvatdangchon.cget("text") != text:
            self.lbl_idnhanvatdangchon.config(text = text)

    def _laynlgiolotrinh(self):
        # {"<id bản đồ>|<tên mẫu>": (giây, ngân lượng nhận)} 7 ngày của mọi nhân vật đang chạy trên máy, tính lại mỗi phút
        thoidiem, ketqua = self._nlgiolotrinh_cache
        if time.time() - thoidiem < 60.:
            return ketqua
        ketqua = {}
        tugio = time.strftime("%Y-%m-%d 00", time.localtime(time.time() - 6 * 86400))
        ids = {info.get("idnguoichoi") for info in dict(self.shared_data.items()).values() if isinstance(info, dict)}
        for idnguoichoi in ids:
            if not idnguoichoi:
                continue
            for khoa, o in gopthongke(taithongke(idnguoichoi), tugio).items():
                giay, nhan = ketqua.get(khoa, (0., 0))
                ketqua[khoa] = (giay + o["giay"], nhan + o["nganluongthu"])
        self._nlgiolotrinh_cache = (time.time(), ketqua)
        return ketqua

    def _capnhatlotrinhmau(self, hwnd_to_show, info, idbando, tenbando):
        idbandocandi = info.get("_idbandocandi")
        buocdichuyen = info.get("_buocdichuyen") or "-"
        if idbandocandi:
            self.lbl_buocdichuyen.config(text = f"Đang đi tới {laytenbando(idbandocandi)}\nBước tiếp theo: {buocdichuyen}", fg = MAUCHU_XANH)
        else:
            self.lbl_buocdichuyen.config(text = f"Bước tiếp theo: {buocdichuyen}", fg = MAUCHU_PHU)
        solanthayquai = info.get("_solanthayquaibando")
        self.lbl_solanthayquai.config(text = f"Đã thấy quái ở {tenbando}: {solanthayquai if solanthayquai is not None else '-'} lần"
                                             f"{f' (cần {SOLANTHAYQUAITOITHIEU})' if solanthayquai is not None and solanthayquai < SOLANTHAYQUAITOITHIEU else ''}")
        tatcamau = self._laylotrinhmau()
        dsmaubando = tatcamau.get(str(idbando), [])
        # Mẫu bản đồ hiện tại lên đầu, sau đó các bản đồ khác theo tên
        thutubando = sorted(tatcamau, key = lambda k: (k != str(idbando), laytenbando(k)))
        dangdung = {}
        for infokhac in dict(self.shared_data.items()).values():
            phankhac = (infokhac.get("_lotrinhmaudangdung") or "").split("|") if isinstance(infokhac, dict) else []
            if len(phankhac) == 3:
                dangdung.setdefault(f"{phankhac[0]}|{phankhac[1]}", []).append(infokhac.get("tennhanvat") or "?")
        nlgio = self._laynlgiolotrinh()
        hangs = []
        for k in thutubando:
            for m in tatcamau[k]:
                khoa = f"{k}|{m.get('ten')}"
                giay, nhan = nlgio.get(khoa, (0., 0))
                hangs.append((khoa, (laytenbando(k), m.get("ten"), len(m.get("diem", [])), ", ".join(dangdung.get(khoa, [])) or "-",
                                     self._sogon(nhan * 3600. / giay) if giay >= 600 else "-"), k == str(idbando)))
        if hangs != self._lotrinhmaudanghien:
            self._lotrinhmaudanghien = hangs
            dangchon = self.tree_lotrinhmau.selection()
            self.tree_lotrinhmau.delete(*self.tree_lotrinhmau.get_children())
            for khoa, values, is_bandohientai in hangs:
                self.tree_lotrinhmau.insert("", tk.END, iid = khoa, values = values, tags = ("bandohientai",) if is_bandohientai else ())
            if dangchon and self.tree_lotrinhmau.exists(dangchon[0]):
                self.tree_lotrinhmau.selection_set(dangchon[0])
        # Đổi nhân vật đang chọn thì nhảy về mẫu đầu tiên của bản đồ nhân vật đó
        if hwnd_to_show != self._hwndchonmautruocdo or not self.tree_lotrinhmau.selection():
            self._hwndchonmautruocdo = hwnd_to_show
            if hangs:
                self.tree_lotrinhmau.selection_set(hangs[0][0])
                self.tree_lotrinhmau.see(hangs[0][0])

        phan = (info.get("_lotrinhmaudangdung") or "").split("|")
        if len(phan) == 3:
            self.lbl_lotrinhmau.config(text = f"Đang dùng: {laytenbando(phan[0])} – {phan[1]}{' (ngược chiều)' if phan[2] == '1' else ''}", fg = MAUCHU_XANH)
            return
        # Lộ trình đặt từ trước khi có mẫu: nếu trùng điểm với một mẫu thì vẫn báo tên mẫu
        diemhientai = [tuple(d[:3]) for d in info.get("_diemdanhxungquanhs", [])]
        tentrung = None
        for m in dsmaubando:
            diemmau = [(d[0], d[1], d[2] if len(d) >= 3 else idbando) for d in m.get("diem", [])]
            if diemhientai and diemhientai == diemmau:
                tentrung = m.get("ten")
            elif diemhientai and diemhientai == diemmau[::-1]:
                tentrung = f"{m.get('ten')} (ngược chiều)"
        if tentrung:
            self.lbl_lotrinhmau.config(text = f"Trùng mẫu: {tenbando} – {tentrung}", fg = MAUCHU_XANH)
        else:
            self.lbl_lotrinhmau.config(text = "Đang dùng: (tự đặt điểm)", fg = MAUCHU_PHU)

    def _capnhatdiemdanh(self, info):
        diemdanhs = [tuple(d) for d in info.get("_diemdanhxungquanhs", [])]
        dangden = (info.get("_diemdanhdangden") or [None] * 4)[3]
        if (diemdanhs, dangden) == self._diemdanhdanghienthi:
            return
        self._diemdanhdanghienthi = (diemdanhs, dangden)
        self.tree_diemdanh.delete(*self.tree_diemdanh.get_children())
        for i, d in enumerate(diemdanhs):
            self.tree_diemdanh.insert("", tk.END, iid = str(i), tags = ("dangden",) if i == dangden else (),
                                      values = (f"▶ {i + 1}" if i == dangden else i + 1, d[0], d[1], laytenbando(d[2]) if len(d) >= 3 else ""))
        if dangden is not None and self.tree_diemdanh.exists(str(dangden)):
            self.tree_diemdanh.see(str(dangden))
        if diemdanhs:
            self.lbl_sodiem.config(text = f"{len(diemdanhs)} điểm" + (f" · đang đi tới điểm {dangden + 1}" if dangden is not None else ""))
        else:
            self.lbl_sodiem.config(text = "Trống – nạp mẫu hoặc thêm điểm bên dưới")
