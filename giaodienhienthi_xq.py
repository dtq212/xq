import tkinter as tk
from tkinter import ttk


class GiaoDienHienThi:
    def __init__(self, root, shared_data, command_dict):
        self.root = root
        self.shared_data = shared_data
        self.command_dict = command_dict

        self.root.title("Trò Chơi - Bảng Điều Khiển VIP")
        self.root.geometry("650x850")
        self.root.attributes('-topmost', True)

        frame_top = tk.Frame(self.root)
        frame_top.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)

        columns = ("hwnd", "name", "hp", "mp", "map", "pos", "status")
        self.tree = ttk.Treeview(frame_top, columns = columns, show = "headings", height = 8)

        self.tree.heading("hwnd", text = "HWND")
        self.tree.column("hwnd", width = 70, anchor = tk.CENTER)
        self.tree.heading("name", text = "Nhân vật")
        self.tree.column("name", width = 100, anchor = tk.W)
        self.tree.heading("hp", text = "%SL")
        self.tree.column("hp", width = 50, anchor = tk.CENTER)
        self.tree.heading("mp", text = "%NL")
        self.tree.column("mp", width = 50, anchor = tk.CENTER)
        self.tree.heading("map", text = "Bản đồ")
        self.tree.column("map", width = 60, anchor = tk.CENTER)
        self.tree.heading("pos", text = "Tọa độ")
        self.tree.column("pos", width = 80, anchor = tk.CENTER)
        self.tree.heading("status", text = "Trạng thái")
        self.tree.column("status", width = 120, anchor = tk.W)

        self.tree.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

        scrollbar = ttk.Scrollbar(frame_top, orient = tk.VERTICAL, command = self.tree.yview)
        self.tree.configure(yscroll = scrollbar.set)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        # --- Khung chứa Trạng thái & Phím tắt (Phần dưới) ---
        frame_bottom = tk.LabelFrame(self.root, text = "Trạng Thái & Phím Tắt (Chọn nhân vật ở trên để điều khiển)", padx = 10, pady = 10)
        frame_bottom.pack(fill = tk.BOTH, expand = False, padx = 5, pady = 5)

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
            "chantangcap": tk.BooleanVar()
        }

        # --- Group 1: Cơ bản & Farm ---
        self._create_check(frame_bottom, "Tự động sử dụng kỹ năng  [Ctrl + F]", self.vars["sudungkynang"], "battat_tudongsudungkynang")
        self._create_check(frame_bottom, "Tự động gom quái  [Ctrl+Alt+Shift+G]", self.vars["gomquai"], "battat_tudonggomquai")
        self._create_check(frame_bottom, "Tự động Farm & Bán rác  [Ctrl+Alt+Shift+H]", self.vars["vebanrac"], "battat_tudongvebanrac")
        self._create_check(frame_bottom, "Theo sau trưởng nhóm  [Ctrl+Alt+F]", self.vars["theotruongnhom"], "battat_tudongtheosautruongnhom")
        self._create_check(frame_bottom, "Bật/Tắt theo sau nhóm  [Ctrl+Alt+T]", self.vars["battheosaunhom"], "battat_tudongbattheosaunhom")
        self._create_check(frame_bottom, "Chặn tăng cấp độ  [Ctrl+Alt+Shift+C]", self.vars["chantangcap"], "battat_chantangcapdo")

        ttk.Separator(frame_bottom, orient = 'horizontal').pack(fill = 'x', pady = 5)

        # --- Group 2: PK & Tùy chọn ---
        # Riêng phần "Chỉ đánh Người chơi", chúng ta gửi lệnh chung là "toggle_chidanhnguoichoi"
        self._create_check(frame_bottom, "Chỉ đánh Người chơi  [Ctrl+D/Ctrl+A]", self.vars["chidanhnguoichoi"], "toggle_chidanhnguoichoi")
        self._create_check(frame_bottom, "Ưu tiên Bảo thú Mao Sơn  [Ctrl+Alt+S]", self.vars["uutienmaoson"], "battat_uutienbaothumaoson")
        self._create_check(frame_bottom, "Chế độ Buff toàn bang  [Ctrl+Alt+Shift+N]", self.vars["bufftoanbang"], "battat_chedobufftoanbang")

        ttk.Separator(frame_bottom, orient = 'horizontal').pack(fill = 'x', pady = 5)

        # --- Group 3: Hoạt động ---
        self._create_check(frame_bottom, "Tự động Khai khoáng  [Ctrl+Alt+Shift+K]", self.vars["khaikhoang"], "battat_tudongkhaikhoang")
        self._create_check(frame_bottom, "Đào Tàng bảo đồ  [Ctrl+Alt+Shift+I]", self.vars["daobaodo"], "battat_tudongdaotangbaodo")
        self._create_check(frame_bottom, "Đi Chiến trường  [Ctrl+Alt+Shift+Z]", self.vars["chientruong"], "battat_tudongdichientruong")

        ttk.Separator(frame_bottom, orient = 'horizontal').pack(fill = 'x', pady = 5)

        # --- Group 4: Danh sách Tấn công / Bỏ qua ---
        tk.Label(frame_bottom, text = "[Ctrl+C] Thêm | [Ctrl+Alt+C] Xóa danh sách Tấn công", font = ("Arial", 9, "bold")).pack(anchor = tk.W)
        self.lbl_tancong = tk.Label(frame_bottom, text = "→ Trống", fg = "red", justify = tk.LEFT, wraplength = 600)
        self.lbl_tancong.pack(anchor = tk.W, pady = (0, 10))

        tk.Label(frame_bottom, text = "[Ctrl+X] Thêm | [Ctrl+Alt+X] Xóa danh sách Bỏ qua", font = ("Arial", 9, "bold")).pack(anchor = tk.W)
        self.lbl_boqua = tk.Label(frame_bottom, text = "→ Trống", fg = "green", justify = tk.LEFT, wraplength = 600)
        self.lbl_boqua.pack(anchor = tk.W)

        self.update_ui()

    def _create_check(self, parent, text, variable, cmd_name = None):
        """Tạo Checkbox có khả năng gửi lệnh trực tiếp vào command_dict khi click"""

        def on_click():
            hwnd = self.get_selected_hwnd()
            if hwnd and cmd_name:
                self.command_dict[hwnd] = cmd_name

        cb = tk.Checkbutton(parent, text = text, variable = variable, command = on_click)
        cb.pack(anchor = tk.W)

    def get_selected_hwnd(self):
        selected = self.tree.selection()
        if selected:
            return int(self.tree.item(selected[0], 'values')[0])
        elif self.tree.get_children():
            return int(self.tree.item(self.tree.get_children()[0], 'values')[0])
        return None

    def update_ui(self):
        selected_item = self.tree.selection()
        selected_hwnd = self.tree.item(selected_item[0], 'values')[0] if selected_item else None

        for item in self.tree.get_children():
            self.tree.delete(item)

        for hwnd, info in self.shared_data.items():
            name = info.get("tennhanvat") or "Đang tải..."
            hp = info.get("phantramsinhluc", 0)
            mp = info.get("phantramnoiluc", 0)
            map_id = info.get("tenbando", "N/A")
            x, y = info.get("x", 0), info.get("y", 0)
            pos = f"{x}, {y}"
            status = info.get("status", "N/A")

            item_id = self.tree.insert("", tk.END, values = (hwnd, name, f"{hp}%", f"{mp}%", map_id, pos, status))

            if str(hwnd) == str(selected_hwnd):
                self.tree.selection_set(item_id)

        hwnd_to_show = self.get_selected_hwnd()
        if hwnd_to_show and hwnd_to_show in self.shared_data:
            info = self.shared_data[hwnd_to_show]

            self.vars["sudungkynang"].set(info.get("_is_tudongsudungkynang", False))
            self.vars["gomquai"].set(info.get("_is_tudonggomquai", False))
            self.vars["vebanrac"].set(info.get("_is_tudongvebanrac", False))
            self.vars["theotruongnhom"].set(info.get("_is_tudongtheosautruongnhom", False))
            self.vars["battheosaunhom"].set(info.get("_is_tudongbattheosaunhom", False))
            self.vars["timmuctieu"].set(info.get("_is_tudongtimkiemmuctieu", False))
            self.vars["khaikhoang"].set(info.get("_is_tudongkhaikhoang", False))
            self.vars["chientruong"].set(info.get("_is_tudongdichientruong", False))
            self.vars["daobaodo"].set(info.get("_is_tudongdaotangbaodo", False))

            self.vars["chidanhnguoichoi"].set(info.get("_is_chidanhnguoichoi", False))
            self.vars["uutienmaoson"].set(info.get("_is_uutienbaothumaoson", False))
            self.vars["bufftoanbang"].set(info.get("_is_chedobufftoanbang", False))
            self.vars["chantangcap"].set(info.get("_is_chantangcapdo", False))

            tancong = info.get("_tenmuctieutancongs", "")
            boqua = info.get("_tenmuctieukhongtancongs", "")

            self.lbl_tancong.config(
                text = f"→ {tancong}" if tancong else "→ Trống",
                fg = "blue" if tancong else "red"
            )
            self.lbl_boqua.config(
                text = f"→ {boqua}" if boqua else "→ Trống",
                fg = "green" if boqua else "red"
            )

        self.root.after(500, self.update_ui)