import json
import os
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from bando_xq import BANDOCONG_MAP
from dexuatlotrinh_xq import SOLANTHAYQUAITOITHIEU
from hangso_xq import laytenbando, KHOANGCACHSUDUNGKYNANGTAMXA, PHANTRAMNOILUCKHAITHIENTICHDIA, KHOANGCACHGIUKETANCONG, BAOTHUTRIEUHOIMAOSONs
import re

from tienich_xq import tailotrinhmau, duongdanlotrinhmau, tainhomtodoitudongs, luunhomtodoitudongs, duongdantodoitudong, laynhomtodoitudongs
from tienich_xq import duongdantaikhoan
from dangnhap_xq import taicauhinhdangnhap
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
        # Tên hiển thị "Tương Lăng – Vòng A" -> (id bản đồ, tên mẫu thật "Vòng A"); có mẫu của mọi bản đồ
        self._tenmautheohienthi = {}
        self._hwndchonmautruocdo = None
        self._diemdanhdanghienthi = None
        self._thoidiemsuatodoi = None
        # Danh sách mục tiêu đang hiện trong ô sửa: (hwnd, tấn công, bỏ qua) để biết khi nào nạp lại từ nhân vật
        self._danhsachmuctieudanghien = None
        # Vừa bấm Lưu: (hwnd, tấn công, bỏ qua, thời điểm) -> chờ bot nhận, trong lúc đó không nạp lại danh sách cũ đè lên
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
        chieurong = self._px(500)
        x = max(0, (self.root.winfo_screenwidth() - chieurong) // 2)
        y = max(0, (self.root.winfo_screenheight() - self._px(40) - chieucao) // 2)
        self.root.geometry(f"{chieurong}x{chieucao}+{x}+{y}")
        self.root.minsize(self._px(480), self._px(600))
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
            "tudongbattatchucnangmorong": tk.BooleanVar(),
            "sudungkynangbaothu": tk.BooleanVar(),
            "tranhvungcam": tk.BooleanVar(value = True),
            "giukhoangcachketancong": tk.BooleanVar(),
            "giukhoangcachchimuctieupk": tk.BooleanVar(value = True),
            "taphoa": tk.BooleanVar(),
            "timmuctieuchung": tk.BooleanVar(value = True),
            "khoangcachgiuketancong": tk.DoubleVar(value = KHOANGCACHGIUKETANCONG),
            "hoithanhphutheosau": tk.BooleanVar(),
            "doidotrieuhoi": tk.BooleanVar(),
        }

        # Nhịp lệnh dùng chung mọi nhân vật (không theo nhân vật đang chọn nên không đồng bộ trong update_ui)
        cauhinhdieuphoi = taicauhinhdieuphoi()
        # {kênh: {is_xoayvong, nghitoithieu, nghitoida}}
        self.vars_dieuphoi = {
            kenh: {
                "is_xoayvong": tk.BooleanVar(value = cauhinhdieuphoi[kenh]["is_xoayvong"]),
                "nghitoithieu": tk.DoubleVar(value = cauhinhdieuphoi[kenh]["nghitoithieu"]),
                "nghitoida": tk.DoubleVar(value = cauhinhdieuphoi[kenh]["nghitoida"]),
            }
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
        style.configure("TNotebook.Tab", padding = (12, 4))
        style.configure("TLabelframe.Label", font = (FONTCHU, COCHU, "bold"))
        style.configure("Phu.TLabel", foreground = MAUCHU_PHU)
        style.configure("Tieude.TLabel", font = (FONTCHU, COCHU + 1, "bold"))

    def _taodanhsachnhanvat(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill = tk.X, padx = 8, pady = (8, 4))

        # Cột "hwnd" ẩn đi (vẫn dùng làm khoá), chỉ hiện thông tin dễ đọc
        columns = ("hwnd", "name", "hp", "mp", "map", "status")
        self.tree = ttk.Treeview(frame, columns = columns, displaycolumns = ("name", "hp", "mp", "map", "status"),
                                 show = "headings", height = 5, selectmode = "browse")
        for col, text, width, anchor in (
                ("name", "Nhân vật", 110, tk.W),
                ("hp", "SL", 45, tk.CENTER),
                ("mp", "NL", 45, tk.CENTER),
                ("map", "Bản đồ", 115, tk.W),
                ("status", "Trạng thái", 75, tk.CENTER)):
            self.tree.heading(col, text = text)
            self.tree.column(col, width = self._px(width), anchor = anchor, stretch = col in ("name", "map"))

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
            ttk.Label(parent, text = phimtat, style = "Phu.TLabel").grid(row = dong, column = 1, sticky = tk.E, padx = (8, 0))

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

        for kenh, tieude in ((KENH_LENH, "Xoay vòng lệnh giữa các nhân vật"), (KENH_DICHUYEN, "Lần lượt bắt đầu di chuyển")):
            vars_ = self.vars_dieuphoi[kenh]
            ttk.Checkbutton(nhom, text = tieude, variable = vars_["is_xoayvong"],
                            command = on_apdung).grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.W, pady = 1)

            hangnghi = ttk.Frame(nhom)
            hangnghi.grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.W, padx = (22, 0), pady = (0, 2))
            ttk.Label(hangnghi, text = "Cách nhau từ").pack(side = tk.LEFT)
            for khoa, chu in (("nghitoithieu", "đến"), ("nghitoida", "giây")):
                spin = ttk.Spinbox(hangnghi, from_ = 0.0, to = 2.0, increment = 0.01, width = 5, format = "%.2f",
                                   textvariable = vars_[khoa], command = on_apdung)
                spin.pack(side = tk.LEFT, padx = 4)
                self._ganspinboxapdung(spin, on_apdung)
                ttk.Label(hangnghi, text = chu, style = "Phu.TLabel" if chu == "giây" else "TLabel").pack(side = tk.LEFT)

    def _taotabmuctieutodoi(self, tab):
        # Gộp 2 danh sách vào 1 khung cho gọn: dòng tiêu đề nhỏ (kèm phím tắt) + nội dung
        nhom = self._taonhom(tab, "Danh sách mục tiêu (mỗi dòng một tên)")

        def taoosua(dong, tieude, mau):
            ttk.Label(nhom, text = tieude, style = "Phu.TLabel").grid(row = dong, column = 0, columnspan = 2, sticky = tk.W)
            khung = ttk.Frame(nhom)
            khung.grid(row = dong + 1, column = 0, columnspan = 2, sticky = tk.EW, pady = (0, 4))
            txt = tk.Text(khung, height = 3, wrap = tk.NONE, undo = True, fg = mau, highlightthickness = 0, borderwidth = 1, relief = tk.SOLID)
            thanhcuon = ttk.Scrollbar(khung, orient = tk.VERTICAL, command = txt.yview)
            txt.configure(yscrollcommand = thanhcuon.set)
            txt.pack(side = tk.LEFT, fill = tk.X, expand = True)
            thanhcuon.pack(side = tk.RIGHT, fill = tk.Y)
            return txt

        self.txt_tancong = taoosua(0, "Tấn công (trống = đánh hết)   Ctrl+C thêm · Ctrl+Alt+C xoá", MAUCHU_XANH)
        self.txt_boqua = taoosua(2, "Bỏ qua   Ctrl+X thêm · Ctrl+Alt+X xoá", MAUCHU_LUC)

        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 4, column = 0, columnspan = 2, sticky = tk.EW)
        self.lbl_trangthaimuctieu = tk.Label(hangnut, text = "", fg = MAUCHU_PHU, anchor = tk.W)
        self.lbl_trangthaimuctieu.pack(side = tk.LEFT, fill = tk.X, expand = True)

        def on_luu(is_tatca):
            tancongs, boquas = self._docdanhsachmuctieutugiaodien()
            lenh = "set_danhsachmuctieu:" + json.dumps({"tancong": tancongs, "boqua": boquas}, ensure_ascii = False)
            hwnd = self.get_selected_hwnd()
            hwnds = list(self.shared_data.keys()) if is_tatca else ([hwnd] if hwnd else [])
            if not hwnds:
                self.lbl_trangthaimuctieu.config(text = "Chưa có nhân vật", fg = MAUCHU_DO)
                return
            for h in hwnds:
                self.command_dict[h] = lenh
            self._danhsachmuctieudanglu = (hwnd, tancongs, boquas, time.time())
            self._hiendanhsachmuctieu(hwnd, tancongs, boquas)
            self.lbl_trangthaimuctieu.config(text = f"Đã lưu cho {len(hwnds)} nhân vật" if is_tatca else "Đã lưu", fg = MAUCHU_LUC)

        def on_hoantac():
            self._danhsachmuctieudanghien = None
            self._danhsachmuctieudanglu = None
            self.lbl_trangthaimuctieu.config(text = "")

        ttk.Button(hangnut, text = "Lưu", width = 6, command = lambda: on_luu(False)).pack(side = tk.RIGHT)
        ttk.Button(hangnut, text = "Lưu cho tất cả", command = lambda: on_luu(True)).pack(side = tk.RIGHT, padx = 4)
        ttk.Button(hangnut, text = "Hoàn tác", command = on_hoantac).pack(side = tk.RIGHT)

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
        ttk.Label(hangkhaithien, text = "Thục Sơn lướt Khai Thiên Tịch Địa khi nội lực trên:").pack(side = tk.LEFT)

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

    def _docdanhsachmuctieutugiaodien(self):
        def doc(txt):
            tens = []
            for dong in txt.get("1.0", tk.END).splitlines():
                # Dán cả tên kèm cấp ("Sói ( Cấp 10)") thì bỏ phần cấp giống khi thêm bằng phím tắt
                ten = re.split(r"\(\s*[Cc]ấp", dong)[0].strip()
                if ten and ten not in tens:
                    tens.append(ten)
            return sorted(tens)
        return doc(self.txt_tancong), doc(self.txt_boqua)

    def _hiendanhsachmuctieu(self, hwnd, tancongs, boquas):
        for txt, tens in ((self.txt_tancong, tancongs), (self.txt_boqua, boquas)):
            txt.delete("1.0", tk.END)
            txt.insert("1.0", "\n".join(tens))
            txt.edit_modified(False)
            txt.edit_reset()
        self._danhsachmuctieudanghien = (hwnd, list(tancongs), list(boquas))

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

        dahien = self._danhsachmuctieudanghien
        is_dangsua = self.txt_tancong.edit_modified() or self.txt_boqua.edit_modified()
        if dahien and dahien[0] == hwnd:
            if is_dangsua:
                self.lbl_trangthaimuctieu.config(text = "Chưa lưu", fg = MAUCHU_DO)
                return
            if (dahien[1], dahien[2]) == (tancongs, boquas):
                return
        elif dahien:
            self.lbl_trangthaimuctieu.config(text = "")
        self._hiendanhsachmuctieu(hwnd, tancongs, boquas)

    def _taotabfarm(self, tab):
        nhom = self._taonhom(tab, "Chế độ")
        self._create_check(nhom, "Tự động farm & về bán rác", self.vars["vebanrac"], "battat_tudongvebanrac", "Ctrl+Alt+Shift+H")
        self._create_check(nhom, "Tránh vùng cấm", self.vars["tranhvungcam"], "battat_tranhvungcam")
        self._create_check(nhom, "Di chuyển theo lộ trình điểm đánh", self.vars["diemdanhxungquanh"], "battat_tudongdichuyendiemdanhxungquanh", "Ctrl+Alt+Shift+P")

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
        self._idbandotheohienthi = {f"{ten} ({idbando})": idbando for idbando, (ten, _) in sorted(BANDOCONG_MAP.items(), key = lambda m: m[1][0] or "") if ten}
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

        self.str_lotrinhmau = tk.StringVar()
        self.cbo_lotrinhmau = ttk.Combobox(nhom, textvariable = self.str_lotrinhmau, state = "readonly", height = 20)
        self.cbo_lotrinhmau.grid(row = 1, column = 0, columnspan = 2, sticky = tk.EW)

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
            mau = self._tenmautheohienthi.get(self.str_lotrinhmau.get())
            if hwnd and mau:
                idbando, tenmau = mau
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
        ttk.Entry(hangluu, textvariable = self.str_tenmaumoi, width = 12).pack(side = tk.RIGHT, padx = 4)

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

        # Điểm đánh hiện tại: mỗi điểm một dòng
        nhom = self._taonhom(tab, "Điểm đánh của nhân vật")
        nhom.pack_configure(fill = tk.BOTH, expand = True)
        nhom.rowconfigure(1, weight = 1)
        self.lbl_sodiem = ttk.Label(nhom, text = "Trống", style = "Phu.TLabel")
        self.lbl_sodiem.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)

        khungds = ttk.Frame(nhom)
        khungds.grid(row = 1, column = 0, columnspan = 2, sticky = tk.NSEW, pady = (2, 4))
        self.lst_diemdanh = tk.Listbox(khungds, height = 6, activestyle = "none", highlightthickness = 0, borderwidth = 1, relief = tk.SOLID)
        thanhcuon = ttk.Scrollbar(khungds, orient = tk.VERTICAL, command = self.lst_diemdanh.yview)
        self.lst_diemdanh.configure(yscrollcommand = thanhcuon.set)
        self.lst_diemdanh.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
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
                  style = "Phu.TLabel", justify = tk.LEFT, wraplength = self._px(390)).grid(row = 3, column = 0, columnspan = 2, sticky = tk.W, pady = (4, 0))

    def _taotabnhom(self, tab):
        nhom = self._taonhom(tab, "Nhóm")

        def on_click_theosau():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "battat_tudongtheosau"

        ttk.Checkbutton(nhom, text = "Tự động theo sau", variable = self.vars["theosau"],
                        command = on_click_theosau).grid(row = 0, column = 0, sticky = tk.W, pady = 1)
        ttk.Label(nhom, text = "Ctrl+Alt+F", style = "Phu.TLabel").grid(row = 0, column = 1, sticky = tk.E, padx = (8, 0))

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

        self._create_check(nhom, "Hồi Thành Phù về để phù sang chỗ người theo sau", self.vars["hoithanhphutheosau"], "battat_hoithanhphutheosau")
        self._create_check(nhom, "Tổ đội tự động (danh sách ở tab Mục tiêu & Tổ đội)", self.vars["todoitudong"], "battat_tudongtodoi")

        nhom = self._taonhom(tab, "Bảo thú")
        self._create_check(nhom, "Tự động gọi bảo thú", self.vars["trieuhoibaothu"], "battat_tudongtrieuhoibaothugiangho")
        self._create_check(nhom, "Tự động dùng kỹ năng bảo thú", self.vars["sudungkynangbaothu"], "battat_tudongsudungkynangbaothu")
        # Mao Sơn tự gọi bảo thú triệu hồi nào: Tự động (Cương Thi nếu có Cương Thi Phù, không thì Thiên Binh) hoặc đúng 1 loại
        hangbaothu = ttk.Frame(nhom)
        hangbaothu.grid(row = nhom.grid_size()[1], column = 0, columnspan = 2, sticky = tk.W, pady = 1)
        ttk.Label(hangbaothu, text = "Mao Sơn gọi bảo thú:").pack(side = tk.LEFT)
        self.str_baothutrieuhoi = tk.StringVar(value = BAOTHUTRIEUHOIMAOSONs[0])
        self.cbo_baothutrieuhoi = ttk.Combobox(hangbaothu, textvariable = self.str_baothutrieuhoi, values = BAOTHUTRIEUHOIMAOSONs,
                                               state = "readonly", width = 12)
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
        # Danh sách dùng chung cho mọi nhân vật (lưu file todoi.json), bật/tắt thì theo từng nhân vật ở tab Chiến đấu
        nhom = self._taonhom(tab, "Danh sách tổ đội tự động")
        nhom.pack_configure(fill = tk.BOTH, expand = True)
        nhom.rowconfigure(1, weight = 1)

        ttk.Label(nhom, text = "Mỗi dòng là một nhóm, các ID cách nhau bằng dấu phẩy. ID đứng trước được ưu tiên "
                               "làm trưởng nhóm. Nhân vật trong danh sách cũng được coi là đồng đội (buff, không đánh).",
                  style = "Phu.TLabel", justify = tk.LEFT, wraplength = self._px(390)).grid(row = 0, column = 0, columnspan = 2, sticky = tk.W, pady = (0, 4))

        khung = ttk.Frame(nhom)
        khung.grid(row = 1, column = 0, columnspan = 2, sticky = tk.NSEW)
        self.txt_todoi = tk.Text(khung, height = 6, wrap = tk.NONE, undo = True, highlightthickness = 0, borderwidth = 1, relief = tk.SOLID)
        thanhcuon = ttk.Scrollbar(khung, orient = tk.VERTICAL, command = self.txt_todoi.yview)
        self.txt_todoi.configure(yscrollcommand = thanhcuon.set)
        self.txt_todoi.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        thanhcuon.pack(side = tk.RIGHT, fill = tk.Y)

        self.lbl_idnhanvatdangchon = ttk.Label(nhom, text = "", style = "Phu.TLabel", wraplength = self._px(390))
        self.lbl_idnhanvatdangchon.grid(row = 2, column = 0, columnspan = 2, sticky = tk.W, pady = (4, 0))

        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 3, column = 0, columnspan = 2, sticky = tk.EW, pady = (4, 0))
        self.lbl_trangthaitodoi = tk.Label(hangnut, text = "", fg = MAUCHU_PHU, anchor = tk.W)
        self.lbl_trangthaitodoi.pack(side = tk.LEFT, fill = tk.X, expand = True)

        def on_them_iddangchon():
            # Thêm ID nhân vật đang chọn vào cuối dòng đang đặt con trỏ
            hwnd = self.get_selected_hwnd()
            idnguoichoi = self.shared_data.get(hwnd, {}).get("idnguoichoi") if hwnd else None
            if not idnguoichoi:
                return
            dong = self.txt_todoi.index(tk.INSERT).split(".")[0]
            noidungdong = self.txt_todoi.get(f"{dong}.0", f"{dong}.end").rstrip(" ,")
            self.txt_todoi.delete(f"{dong}.0", f"{dong}.end")
            self.txt_todoi.insert(f"{dong}.0", f"{noidungdong}, {idnguoichoi}" if noidungdong.strip() else str(idnguoichoi))

        def on_luu_todoi():
            nhoms, loi = self._doctodoitugiaodien()
            if loi:
                self.lbl_trangthaitodoi.config(text = f"Không phải ID: {', '.join(loi)}", fg = MAUCHU_DO)
                return
            trungs = sorted({id_ for nhom_ in nhoms for id_ in nhom_ if sum(n.count(id_) for n in nhoms) > 1})
            luunhomtodoitudongs(nhoms)
            self._taitodoilengiaodien(is_batbuoc = True)
            if trungs:
                self.lbl_trangthaitodoi.config(text = f"Đã lưu. Lưu ý ID nằm ở nhiều nhóm: {', '.join(map(str, trungs))}", fg = MAUCHU_DO)
            else:
                self.lbl_trangthaitodoi.config(text = f"Đã lưu {len(nhoms)} nhóm", fg = MAUCHU_LUC)

        ttk.Button(hangnut, text = "Lưu", width = 6, command = on_luu_todoi).pack(side = tk.RIGHT)
        ttk.Button(hangnut, text = "Thêm ID đang chọn", command = on_them_iddangchon).pack(side = tk.RIGHT, padx = 4)

        self._taitodoilengiaodien(is_batbuoc = True)

    def _doctodoitugiaodien(self):
        nhoms, loi = [], []
        for dong in self.txt_todoi.get("1.0", tk.END).splitlines():
            ids = []
            for phan in re.split(r"[,;\s]+", dong.strip()):
                if not phan:
                    continue
                if phan.isdigit() and int(phan) > 0:
                    if int(phan) not in ids:
                        ids.append(int(phan))
                else:
                    loi.append(phan)
            if ids:
                nhoms.append(ids)
        return nhoms, loi

    def _taitodoilengiaodien(self, is_batbuoc = False):
        # Đọc lại file khi nó đổi (vd. sửa tay), nhưng không đè lên chỗ đang gõ dở chưa lưu
        try:
            thoidiemsua = os.path.getmtime(duongdantodoitudong())
        except OSError:
            thoidiemsua = None
        if not is_batbuoc and (thoidiemsua == self._thoidiemsuatodoi or self.txt_todoi.edit_modified()):
            return
        self._thoidiemsuatodoi = thoidiemsua
        self.txt_todoi.delete("1.0", tk.END)
        self.txt_todoi.insert("1.0", "\n".join(", ".join(map(str, nhom)) for nhom in tainhomtodoitudongs()))
        self.txt_todoi.edit_modified(False)
        self.txt_todoi.edit_reset()

    def _taotabdangnhap(self, tab):
        # Chung cả máy (không theo nhân vật đang chọn): tài khoản trong _internal/taikhoan.json
        nhom = self._taonhom(tab, "Tự động đăng nhập (chung cả máy)")
        self.var_tudongdangnhap = tk.BooleanVar(value = self.dangnhap.is_bat)

        def on_click_dangnhap():
            self.dangnhap.set_is_bat(self.var_tudongdangnhap.get())

        ttk.Checkbutton(nhom, text = "Tự đăng nhập lại nhân vật vắng mặt", variable = self.var_tudongdangnhap,
                        command = on_click_dangnhap).grid(row = 0, column = 0, sticky = tk.W, pady = 1)
        self.lbl_trangthaidangnhap = tk.Label(nhom, text = "", fg = MAUCHU_PHU, anchor = tk.W, justify = tk.LEFT, wraplength = self._px(390))
        self.lbl_trangthaidangnhap.grid(row = 1, column = 0, columnspan = 2, sticky = tk.W, pady = (2, 4))
        ttk.Label(nhom, text = "Đang tạm ngưng (ẩn thân / người lạ) thì không đăng nhập ai cho tới khi hết hạn.",
                  style = "Phu.TLabel", justify = tk.LEFT, wraplength = self._px(390)).grid(row = 2, column = 0, columnspan = 2, sticky = tk.W)

        nhom = self._taonhom(tab, "Tài khoản")
        self.lbl_taikhoandangnhap = tk.Label(nhom, text = "", anchor = tk.W, justify = tk.LEFT)
        self.lbl_taikhoandangnhap.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)

        def on_mofiletaikhoan():
            # Chưa có file thì tạo file mẫu để điền
            taicauhinhdangnhap()
            os.startfile(duongdantaikhoan())

        ttk.Button(nhom, text = "Mở file tài khoản", command = on_mofiletaikhoan).grid(row = 1, column = 0, sticky = tk.W, pady = (6, 0))
        ttk.Label(nhom, text = f"{duongdantaikhoan()}\nMỗi máy một file riêng (có mật khẩu, không đưa lên git). Sửa xong lưu lại là "
                               "lượt quét sau tự dùng, không cần mở lại tool.",
                  style = "Phu.TLabel", justify = tk.LEFT, wraplength = self._px(390)).grid(row = 2, column = 0, columnspan = 2, sticky = tk.W, pady = (4, 0))

    def _capnhatdangnhap(self):
        if self.dangnhap is None:
            return
        trangthai = self.dangnhap.trangthai
        if self.lbl_trangthaidangnhap.cget("text") != trangthai:
            mau = MAUCHU_DO if trangthai.startswith(("Tạm ngưng", "Lỗi", "File tài khoản bị lỗi")) else (MAUCHU_XANH if trangthai.startswith("Đang đăng nhập") else MAUCHU_PHU)
            self.lbl_trangthaidangnhap.config(text = trangthai, fg = mau)
        dong = [f"{ten}{f' (ID {idnc})' if idnc else ''} – {tinhtrang}" for ten, idnc, tinhtrang in self.dangnhap.danhsach]
        text = "\n".join(dong) if dong else "(chưa có tài khoản nào)"
        if self.lbl_taikhoandangnhap.cget("text") != text:
            self.lbl_taikhoandangnhap.config(text = text)

    def _taotabkhac(self, tab):
        nhom = self._taonhom(tab, "Tạm ẩn (chưa dùng)")
        self._create_check(nhom, "Tự động bật/tắt CN mở rộng", self.vars["tudongbattatchucnangmorong"], "battat_tudongbattatchucnangmorong", "Ctrl+Alt+Shift+F")
        self._create_check(nhom, "Tự động khai khoáng", self.vars["khaikhoang"], "battat_tudongkhaikhoang", "Ctrl+Alt+Shift+K")
        self._create_check(nhom, "Đào tàng bảo đồ", self.vars["daobaodo"], "battat_tudongdaotangbaodo", "Ctrl+Alt+Shift+I")
        self._create_check(nhom, "Đi chiến trường", self.vars["chientruong"], "battat_tudongdichientruong", "Ctrl+Alt+Shift+Z")

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
            values = (
                hwnd,
                info.get("tennhanvat") or "Đang tải...",
                f"{info.get('phantramsinhluc', 0)}%",
                f"{info.get('phantramnoiluc', 0)}%",
                laytenbando(info.get("tenbando")) if info.get("tenbando") is not None else "-",
                "⏸ Tạm ngưng" if info.get("_thoigiantamngungconlai", 0) > 0 else info.get("status", "-"),
            )
            if iid in hienco:
                if tuple(str(v) for v in self.tree.item(iid, "values")) != tuple(str(v) for v in values):
                    self.tree.item(iid, values = values)
                hienco.discard(iid)
            else:
                self.tree.insert("", tk.END, iid = iid, values = values)
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
                ("tudongbattatchucnangmorong", "_is_tudongbattatchucnangmorong"),
                ("theosau", "_is_tudongtheosau"),
                ("todoitudong", "_is_tudongtodoi"),
                ("timmuctieu", "_is_tudongtimkiemmuctieu"),
                ("trieuhoibaothu", "_is_tudongtrieuhoibaothugiangho"),
                ("sudungkynangbaothu", "_is_tudongsudungkynangbaothu"),
                ("tranhvungcam", "_is_tranhvungcam"),
                ("giukhoangcachketancong", "_is_giukhoangcachketancong"),
                ("giukhoangcachchimuctieupk", "_is_giukhoangcachchimuctieupk"),
                ("taphoa", "_is_taphoa"),
                ("timmuctieuchung", "_is_timmuctieuchung"),
                ("hoithanhphutheosau", "_is_hoithanhphutheosau"),
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
        self._taitodoilengiaodien()
        idnguoichoi = info.get("idnguoichoi")
        nhomcuatoi = next((nhom for nhom in laynhomtodoitudongs() if idnguoichoi in nhom), None)
        if nhomcuatoi:
            vitri = nhomcuatoi.index(idnguoichoi) + 1
            text = f"{info.get('tennhanvat') or ''} (ID {idnguoichoi}) – nhóm {', '.join(map(str, nhomcuatoi))}, thứ {vitri} ưu tiên làm trưởng nhóm"
        else:
            text = f"{info.get('tennhanvat') or ''} (ID {idnguoichoi}) – chưa có trong danh sách"
        self.lbl_idnhanvatdangchon.config(text = text)

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
        self._tenmautheohienthi = {f"{laytenbando(k)} – {m.get('ten')}": (k, m.get("ten")) for k in thutubando for m in tatcamau[k]}
        dshienthi = list(self._tenmautheohienthi)
        if list(self.cbo_lotrinhmau.cget("values") or ()) != dshienthi:
            self.cbo_lotrinhmau.config(values = dshienthi)
        # Đổi nhân vật đang chọn thì nhảy về mẫu đầu tiên của bản đồ nhân vật đó
        if hwnd_to_show != self._hwndchonmautruocdo or self.str_lotrinhmau.get() not in dshienthi:
            self._hwndchonmautruocdo = hwnd_to_show
            self.str_lotrinhmau.set(dshienthi[0] if dshienthi else "")

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
        if diemdanhs == self._diemdanhdanghienthi:
            return
        self._diemdanhdanghienthi = diemdanhs
        self.lst_diemdanh.delete(0, tk.END)
        for i, d in enumerate(diemdanhs, 1):
            tenbandodiem = laytenbando(d[2]) if len(d) >= 3 else ""
            self.lst_diemdanh.insert(tk.END, f"{i:>2}.  ({d[0]}, {d[1]})   {tenbandodiem}")
        if diemdanhs:
            self.lbl_sodiem.config(text = f"{len(diemdanhs)} điểm")
        else:
            self.lbl_sodiem.config(text = "Trống – nạp mẫu hoặc thêm điểm bên dưới")
