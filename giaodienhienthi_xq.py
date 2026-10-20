import os
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from hangso_xq import laytenbando
from tienich_xq import tailotrinhmau, duongdanlotrinhmau

# Tạm ẩn các tùy chọn chưa dùng/không còn khả dụng (CN mở rộng, Khai khoáng, Đào tàng bảo đồ, Chiến trường).
# Đổi thành True để hiện lại (tab "Khác"). Phím tắt của chúng vẫn hoạt động.
HIEN_TUYCHON_CHUADUNG = False

FONTCHU = "Calibri"
COCHU = 11

MAUCHU_PHU = "#7a7a7a"
MAUCHU_XANH = "#1a5fb4"
MAUCHU_DO = "#c01c28"
MAUCHU_LUC = "#26a269"


class GiaoDienHienThi:
    def __init__(self, root, shared_data, command_dict):
        self.root = root
        self.shared_data = shared_data
        self.command_dict = command_dict

        self.last_active_hwnd = None
        self._lotrinhmau_cache = ({}, None)
        # Tên hiển thị "Tương Lăng – Vòng A" -> (id bản đồ, tên mẫu thật "Vòng A"); có mẫu của mọi bản đồ
        self._tenmautheohienthi = {}
        self._hwndchonmautruocdo = None
        self._diemdanhdanghienthi = None

        self.root.title("Bảng Điều Khiển VIP")
        # Hệ số thu phóng màn hình (100% = 1.0, 125% = 1.25...) để kích thước tính bằng pixel không bị nhỏ đi
        self._heso = max(1.0, self.root.winfo_fpixels("1i") / 96.0)
        # Không cao quá màn hình (chừa chỗ cho thanh taskbar)
        chieucao = min(self._px(900), self.root.winfo_screenheight() - self._px(80))
        self.root.geometry(f"{self._px(450)}x{chieucao}")
        self.root.minsize(self._px(420), self._px(600))
        self.root.attributes('-topmost', True)

        self._thietlapstyle()

        self.vars = {
            "sudungkynang": tk.BooleanVar(),
            "gomquai": tk.BooleanVar(),
            "vebanrac": tk.BooleanVar(),
            "theotruongnhom": tk.BooleanVar(),
            "battheosaunhom": tk.BooleanVar(),
            "timmuctieu": tk.BooleanVar(),
            "chidanhnguoichoi": tk.BooleanVar(),
            "uutienmaoson": tk.BooleanVar(),
            "bufftoanbang": tk.BooleanVar(),
            "khaikhoang": tk.BooleanVar(),
            "daobaodo": tk.BooleanVar(),
            "chientruong": tk.BooleanVar(),
            "chantangcap": tk.BooleanVar(),
            "khoangcachtheosau": tk.DoubleVar(value = 9.0),
            "diemdanhxungquanh": tk.BooleanVar(),
            "trieuhoibaothu": tk.BooleanVar(),
            "tudongbattatchucnangmorong": tk.BooleanVar(),
            "sudungkynangbaothu": tk.BooleanVar(),
        }

        self._taodanhsachnhanvat()
        self._taothanhtrangthai()

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill = tk.BOTH, expand = True, padx = 8, pady = (0, 8))

        self._taotabchiendau(self._taotab(notebook, "Chiến đấu"))
        self._taotabfarm(self._taotab(notebook, "Farm & Lộ trình"))
        if HIEN_TUYCHON_CHUADUNG:
            self._taotabkhac(self._taotab(notebook, "Khác"))

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

    def _px(self, sopixel):
        return int(sopixel * self._heso)

    def _taotab(self, notebook, tieude):
        frame = ttk.Frame(notebook, padding = 8)
        notebook.add(frame, text = tieude)
        return frame

    def _taonhom(self, parent, tieude):
        nhom = ttk.LabelFrame(parent, text = tieude, padding = (8, 4))
        nhom.pack(fill = tk.X, pady = (0, 6))
        nhom.columnconfigure(0, weight = 1)
        return nhom

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

        # Nhóm & Bảo thú nằm chung tab Chiến đấu
        self._taotabnhom(tab)

        # Gộp 2 danh sách vào 1 khung cho gọn: dòng tiêu đề nhỏ (kèm phím tắt) + nội dung
        nhom = self._taonhom(tab, "Danh sách mục tiêu")
        ttk.Label(nhom, text = "Tấn công   Ctrl+C thêm · Ctrl+Alt+C xoá", style = "Phu.TLabel").grid(row = 0, column = 0, sticky = tk.W)
        self.lbl_tancong = tk.Label(nhom, text = "Trống", fg = MAUCHU_PHU, justify = tk.LEFT, wraplength = self._px(390), anchor = tk.W)
        self.lbl_tancong.grid(row = 1, column = 0, sticky = tk.W, pady = (0, 4))
        ttk.Label(nhom, text = "Bỏ qua   Ctrl+X thêm · Ctrl+Alt+X xoá", style = "Phu.TLabel").grid(row = 2, column = 0, sticky = tk.W)
        self.lbl_boqua = tk.Label(nhom, text = "Trống", fg = MAUCHU_PHU, justify = tk.LEFT, wraplength = self._px(390), anchor = tk.W)
        self.lbl_boqua.grid(row = 3, column = 0, sticky = tk.W)

    def _taotabfarm(self, tab):
        nhom = self._taonhom(tab, "Chế độ")
        self._create_check(nhom, "Tự động farm & về bán rác", self.vars["vebanrac"], "battat_tudongvebanrac", "Ctrl+Alt+Shift+H")
        self._create_check(nhom, "Di chuyển theo lộ trình điểm đánh", self.vars["diemdanhxungquanh"], "battat_tudongdichuyendiemdanhxungquanh", "Ctrl+Alt+Shift+P")

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
        ttk.Checkbutton(hangnut, text = "Đi ngược chiều", variable = self.var_nguocchieu).pack(side = tk.LEFT)

        def on_tuchon_lotrinhmau():
            hwnd = self.get_selected_hwnd()
            if hwnd:
                self.command_dict[hwnd] = "tuchon_lotrinhmau"

        def on_nap_lotrinhmau():
            hwnd = self.get_selected_hwnd()
            mau = self._tenmautheohienthi.get(self.str_lotrinhmau.get())
            if hwnd and mau:
                idbando, tenmau = mau
                self.command_dict[hwnd] = f"nap_lotrinhmau:{idbando}|{tenmau}|{1 if self.var_nguocchieu.get() else 0}"

        ttk.Button(hangnut, text = "Tự chọn", command = on_tuchon_lotrinhmau).pack(side = tk.RIGHT)
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
                self.command_dict[hwnd] = "battat_tudongtheosautruongnhom"

        ttk.Checkbutton(nhom, text = "Theo sau trưởng nhóm", variable = self.vars["theotruongnhom"],
                        command = on_click_theosau).grid(row = 0, column = 0, sticky = tk.W, pady = 1)
        ttk.Label(nhom, text = "Ctrl+Alt+F", style = "Phu.TLabel").grid(row = 0, column = 1, sticky = tk.E, padx = (8, 0))

        hangkhoangcach = ttk.Frame(nhom)
        hangkhoangcach.grid(row = 1, column = 0, columnspan = 2, sticky = tk.W, padx = (22, 0), pady = (0, 4))
        ttk.Label(hangkhoangcach, text = "Khoảng cách tối đa tới trưởng nhóm:").pack(side = tk.LEFT)

        def on_khoangcach_change(*args):
            hwnd = self.get_selected_hwnd()
            if hwnd:
                try:
                    val = self.vars["khoangcachtheosau"].get()
                    self.command_dict[hwnd] = f"set_khoangcachtheosau:{val}"
                except tk.TclError:
                    pass

        self.spin_khoangcach = ttk.Spinbox(hangkhoangcach, from_ = 1.0, to = 50.0, increment = 1.0, width = 5,
                                           textvariable = self.vars["khoangcachtheosau"], command = on_khoangcach_change)
        self.spin_khoangcach.pack(side = tk.LEFT, padx = 4)
        self.spin_khoangcach.bind("<Return>", on_khoangcach_change)
        self.spin_khoangcach.bind("<FocusOut>", on_khoangcach_change)

        self._create_check(nhom, "Bật/Tắt theo sau nhóm", self.vars["battheosaunhom"], "battat_tudongbattheosaunhom", "Ctrl+Alt+T")

        nhom = self._taonhom(tab, "Bảo thú")
        self._create_check(nhom, "Tự động gọi bảo thú", self.vars["trieuhoibaothu"], "battat_tudongtrieuhoibaothugiangho")
        self._create_check(nhom, "Tự động dùng kỹ năng bảo thú", self.vars["sudungkynangbaothu"], "battat_tudongsudungkynangbaothu")

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
            self._capnhatbangdieukhien()
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
                info.get("status", "-"),
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

        for ten, khoa in (
                ("sudungkynang", "_is_tudongsudungkynang"),
                ("gomquai", "_is_tudonggomquai"),
                ("vebanrac", "_is_tudongvebanrac"),
                ("tudongbattatchucnangmorong", "_is_tudongbattatchucnangmorong"),
                ("theotruongnhom", "_is_tudongtheosautruongnhom"),
                ("battheosaunhom", "_is_tudongbattheosaunhom"),
                ("timmuctieu", "_is_tudongtimkiemmuctieu"),
                ("trieuhoibaothu", "_is_tudongtrieuhoibaothugiangho"),
                ("sudungkynangbaothu", "_is_tudongsudungkynangbaothu"),
                ("khaikhoang", "_is_tudongkhaikhoang"),
                ("chientruong", "_is_tudongdichientruong"),
                ("daobaodo", "_is_tudongdaotangbaodo"),
                ("chidanhnguoichoi", "_is_chidanhnguoichoi"),
                ("uutienmaoson", "_is_uutienbaothukynangtrieuhoi"),
                ("bufftoanbang", "_is_chedobufftoanbang"),
                ("chantangcap", "_is_chantangcapdo"),
                ("diemdanhxungquanh", "_is_tudongdichuyendiemdanhxungquanh")):
            self.vars[ten].set(info.get(khoa, False))

        if self.root.focus_get() != getattr(self, 'spin_khoangcach', None):
            try:
                kc_moi = info.get("_khoangcachtoidatruongnhom", 9.0)
                if abs(self.vars["khoangcachtheosau"].get() - kc_moi) > 0.01:
                    self.vars["khoangcachtheosau"].set(kc_moi)
            except tk.TclError:
                pass

        tancong = info.get("_tenmuctieutancongs", "")
        boqua = info.get("_tenmuctieukhongtancongs", "")
        self.lbl_tancong.config(text = tancong or "Trống (đánh mọi mục tiêu hợp lệ)", fg = MAUCHU_XANH if tancong else MAUCHU_PHU)
        self.lbl_boqua.config(text = boqua or "Trống", fg = MAUCHU_LUC if boqua else MAUCHU_PHU)

        self._capnhatlotrinhmau(hwnd_to_show, info, idbando, tenbando)
        self._capnhatdiemdanh(info)

    def _capnhatlotrinhmau(self, hwnd_to_show, info, idbando, tenbando):
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
