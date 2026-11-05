import base64
import math
import struct
import zlib
import tkinter as tk
from tkinter import ttk

# Chủ đề giao diện phẳng kiểu Material/Bootstrap dựng trên theme "clam" có sẵn của Tk (không cần thư viện ngoài).
# Nút, ô tích, tab là ảnh PNG tự vẽ (bo góc, khử răng cưa) nên đổi sáng/tối chỉ cần vẽ lại ảnh và đổi màu style.

# Mỗi khoá một mã màu riêng trong cùng bảng: đổi chế độ thì dò màu cũ của widget tk thuần -> khoá -> màu mới
BANGMAU_SANG = {
    "nen": "#f5f7fa",           # nền cửa sổ, khung, nhãn
    "nen_o": "#ffffff",         # ô nhập, bảng
    "vien": "#d5dbe5",
    "chu": "#1f2733",
    "chu_phu": "#5b6575",
    "chu_mo": "#8b94a3",        # nhân vật chết / tắt bot, chữ bị khoá
    "chinh": "#2563eb",         # màu nhấn: nút chính, ô tích, tab đang chọn
    "chinh_dam": "#1d4fd0",
    "chon": "#dbe6fd",          # dòng đang chọn
    "nut": "#e9edf3",
    "nut_re": "#dde3ec",        # rê chuột
    "nut_bam": "#cdd5e1",
    "xanh": "#1a56c4",
    "do": "#c4262e",
    "luc": "#15803d",
    "nen_tamngung": "#fff4cc",
    "nen_tat": "#eceff3",
    "nen_canhbao": "#fde8e8",
    "nen_thongbao": "#e8f0fe",  # khối hành động hiện tại kiểu alert-info
    "nen_goiy": "#fffbe6",
    "chu_goiy": "#262626",
    "nen_phim": "#e6eaf0",
    "chu_phim": "#3a4250",
    "vang": "#c27c0e",          # biểu tượng hộp cảnh báo
    # Nút màu kiểu Bootstrap (btn-danger / btn-warning / btn-success / btn-secondary), mỗi loại một màu rê chuột
    "nut_nguyhiem": "#dc3545",
    "nut_nguyhiem_re": "#bb2d3b",
    "nut_canhbao": "#ffc107",
    "nut_canhbao_re": "#e6ac00",
    "nut_thanhcong": "#198754",
    "nut_thanhcong_re": "#146c43",
    "nut_phu": "#6c757d",
    "nut_phu_re": "#5c636a",
}

BANGMAU_TOI = {
    "nen": "#1c1f26",
    "nen_o": "#151820",
    "vien": "#353b47",
    "chu": "#e4e8ef",
    "chu_phu": "#a2abba",
    "chu_mo": "#6f7889",
    "chinh": "#4c8dff",
    "chinh_dam": "#3a78ea",
    "chon": "#27375a",
    "nut": "#2b303a",
    "nut_re": "#363c48",
    "nut_bam": "#414857",
    "xanh": "#79acff",
    "do": "#ff6b70",
    "luc": "#4fd07f",
    "nen_tamngung": "#45391a",
    "nen_tat": "#262a31",
    "nen_canhbao": "#4a2024",
    "nen_thongbao": "#1b2944",
    "nen_goiy": "#2c313c",
    "chu_goiy": "#eef1f6",
    "nen_phim": "#30353f",
    "chu_phim": "#c5ccd8",
    "vang": "#f0b54a",
    "nut_nguyhiem": "#d9434c",
    "nut_nguyhiem_re": "#e85d65",
    "nut_canhbao": "#e8ad1e",
    "nut_canhbao_re": "#f5c03c",
    "nut_thanhcong": "#22955a",
    "nut_thanhcong_re": "#2fae6c",
    "nut_phu": "#5a6270",
    "nut_phu_re": "#6a7383",
}

for _bang in (BANGMAU_SANG, BANGMAU_TOI):
    assert len({m.lower() for m in _bang.values()}) == len(_bang), "Bảng màu có hai khoá trùng mã màu"


# Loại nút màu -> style "<Loai>.TButton" (Nguyhiem.TButton = btn-danger...); Chinh.TButton là btn-primary
LOAINUTMAU = ("nguyhiem", "canhbao", "thanhcong", "phu")


# Màu nút theo chữ đầu (khớp tiền tố, thứ tự quan trọng): như class btn-success / btn-danger / btn-warning / btn-primary bên web
_MAUNUTTHEOCHU = (
    (("Huỷ / bỏ", "Xoá", "Giải tán", "Bỏ", "⏹", "Dừng"), "Nguyhiem.TButton"),
    (("Thêm", "Ghi bộ đồ"), "Thanhcong.TButton"),
    (("Sửa", "Đổi tên", "Số vòng", "↺", "⚙", "Bổ sung"), "Canhbao.TButton"),
    (("Lưu", "▶", "Áp dụng", "Đi", "Tiếp tục", "Nạp mẫu", "Tự đề xuất", "Tự chọn", "🗄", "🚚", "Cả máy", "👥", "🐣", "🤝", "🐥", "🐎",
      "Sắp xếp"), "Chinh.TButton"),
    (("Huỷ", "Mở file"), "Phu.TButton"),
)


def _stylenuttheochu(chu):
    # "" = nút xám mặc định (↑ ↓...)
    chu = str(chu).strip()
    return next((tenstyle for tiengtos, tenstyle in _MAUNUTTHEOCHU if chu.startswith(tiengtos)), "")


def tomaunut(widget):
    # Gán style màu cho mọi nút thường (chưa có style riêng) bên trong widget theo chữ trên nút
    for con in widget.winfo_children():
        tomaunut(con)
    if isinstance(widget, ttk.Button) and not str(widget.cget("style")):
        tenstyle = _stylenuttheochu(widget.cget("text"))
        if tenstyle:
            widget.configure(style = tenstyle)


def doichunut(nut, chu):
    # Nút bật/tắt đổi chữ (▶ Chạy ↔ ⏹ Dừng) thì đổi màu theo chữ mới (xanh ↔ đỏ)
    if str(nut.cget("text")) != chu:
        nut.configure(text = chu, style = _stylenuttheochu(chu))


def laybangmau(is_toi):
    return BANGMAU_TOI if is_toi else BANGMAU_SANG


def _rgb(mau):
    return tuple(int(mau[i:i + 2], 16) for i in (1, 3, 5))


def _png(rong, cao, hammau, somau = 3):
    # Ảnh PNG RGBA (base64): hammau(x, y) -> (r, g, b) hoặc None (trong suốt), lấy mẫu somau x somau mỗi pixel để khử răng cưa
    dong = []
    for y in range(cao):
        hang = bytearray([0])
        for x in range(rong):
            tong, so = [0, 0, 0], 0
            for sy in range(somau):
                for sx in range(somau):
                    c = hammau(x + (sx + 0.5) / somau, y + (sy + 0.5) / somau)
                    if c:
                        tong[0] += c[0]
                        tong[1] += c[1]
                        tong[2] += c[2]
                        so += 1
            hang += bytes([t // so for t in tong] + [255 * so // somau ** 2]) if so else bytes(4)
        dong.append(bytes(hang))

    def khoi(loai, dulieu):
        return struct.pack(">I", len(dulieu)) + loai + dulieu + struct.pack(">I", zlib.crc32(loai + dulieu) & 0xffffffff)

    png = b"\x89PNG\r\n\x1a\n" + khoi(b"IHDR", struct.pack(">IIBBBBB", rong, cao, 8, 6, 0, 0, 0)) + \
        khoi(b"IDAT", zlib.compress(b"".join(dong))) + khoi(b"IEND", b"")
    return base64.b64encode(png).decode("ascii")


def _khoangcachhop(x, y, x0, y0, x1, y1, r):
    # Khoảng cách có dấu từ điểm tới hình chữ nhật bo góc bán kính r (âm = bên trong)
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    qx = abs(x - x0 - hx) - hx + r
    qy = abs(y - y0 - hy) - hy + r
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r


def _khoangcachdoan(x, y, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0., min(1., ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - ax - t * dx, y - ay - t * dy)


def _anhhop(rong, cao, hop, r, nen, vien = None, dayvien = 1., phu = None):
    # Hình chữ nhật bo góc nền "nen", viền "vien" dày dayvien; phu(x, y) -> màu vẽ đè (dấu tích...) hoặc None
    nen, vien = _rgb(nen), (_rgb(vien) if vien else None)

    def hammau(x, y):
        d = _khoangcachhop(x, y, *hop, r)
        if d > 0:
            return None
        c = phu(x, y) if phu else None
        if c:
            return c
        return vien if vien and d > -dayvien else nen

    return _png(rong, cao, hammau)


def _veanh(mau, heso):
    # {tên ảnh: dữ liệu PNG} theo bảng màu và hệ số thu phóng màn hình
    anh = {}
    # Nút: hình bo góc co giãn được (element dùng border = r + 1 giữ nguyên 4 góc)
    canh = round(20 * heso)
    r = 4 * heso
    hopnut = (0.5, 0.5, canh - 0.5, canh - 0.5)
    for ten, nen, vien in (("nut", mau["nut"], mau["vien"]), ("nut_re", mau["nut_re"], mau["vien"]),
                           ("nut_bam", mau["nut_bam"], mau["nut_bam"]), ("nut_tat", mau["nen"], mau["vien"]),
                           ("nutchinh", mau["chinh"], mau["chinh"]), ("nutchinh_re", mau["chinh_dam"], mau["chinh_dam"])):
        anh[ten] = _anhhop(canh, canh, hopnut, r, nen, vien, heso)
    for loai in LOAINUTMAU:
        for duoi in ("", "_re"):
            khoa = f"nut_{loai}{duoi}"
            anh[khoa] = _anhhop(canh, canh, hopnut, r, mau[khoa], mau[khoa], heso)

    # Ô tích: hộp vuông bo góc, chừa trong suốt bên phải làm khoảng cách tới chữ
    o = round(16 * heso)
    hopo = (0.5, 0.5, o - 0.5, o - 0.5)
    rong = o + round(6 * heso)
    trang = _rgb("#ffffff")
    diemtich = ((0.26 * o, 0.52 * o), (0.43 * o, 0.69 * o), (0.75 * o, 0.33 * o))
    daytich = 1.0 * heso

    def tich(x, y):
        return trang if min(_khoangcachdoan(x, y, *diemtich[0], *diemtich[1]),
                            _khoangcachdoan(x, y, *diemtich[1], *diemtich[2])) <= daytich else None

    for ten, nen, vien, phu in (("tich", mau["nen_o"], mau["chu_mo"], None), ("tich_re", mau["nen_o"], mau["chinh"], None),
                                ("tich_tat", mau["nen"], mau["vien"], None), ("tich_co", mau["chinh"], mau["chinh"], tich),
                                ("tich_co_re", mau["chinh_dam"], mau["chinh_dam"], tich),
                                ("tich_co_tat", mau["chu_mo"], mau["chu_mo"], tich)):
        anh[ten] = _anhhop(rong, o, hopo, 3 * heso, nen, vien, 1.2 * heso, phu)

    # Tab: nền trơn, tab đang chọn có vạch màu nhấn dày 3px ở đáy (kiểu Material)
    vach = max(2, round(3 * heso))
    cao = vach + 8
    for ten, nen, mauvach in (("tab", mau["nen"], None), ("tab_re", mau["nut"], None), ("tab_chon", mau["nen"], mau["chinh"])):
        nen_, vach_ = _rgb(nen), (_rgb(mauvach) if mauvach else None)
        anh[ten] = _png(8, cao, lambda x, y, n = nen_, v = vach_: v if v and y >= cao - vach else n, somau = 1)
    return anh, {"nut": round(r) + 1, "vach": vach}


def _doilayout(layout, doiten):
    # Đổi tên element trong layout theo doiten {tên cũ: tên mới}; tên mới None = bỏ element đó, giữ các element con
    kq = []
    for ten, tuychon in layout:
        con = _doilayout(tuychon["children"], doiten) if "children" in tuychon else None
        if ten in doiten and doiten[ten] is None:
            kq.extend(con or [])
            continue
        tuychon = dict(tuychon)
        if con is not None:
            tuychon["children"] = con
        if ten in doiten:
            # Element ảnh thay vào mà giữ "border" của layout cũ thì các element con (chữ trên nút) không hiện
            tuychon.pop("border", None)
        kq.append((doiten.get(ten, ten), tuychon))
    return kq


# Ảnh của element (giữ suốt đời giao diện: element ttk trỏ tới tên ảnh, đổi chế độ chỉ vẽ lại nội dung ảnh)
_anh = {}
# Bảng màu, hệ số thu phóng, font đang dùng (cho hộp thoại thông báo)
_hientai = {"mau": BANGMAU_SANG, "heso": 1.0, "font": ("Segoe UI", 10)}


def apdungchude(root, mau, heso, font):
    _hientai.update(mau = mau, heso = heso, font = font)
    style = ttk.Style(root)
    if style.theme_use() != "clam":
        style.theme_use("clam")
    dulieuanh, kichthuoc = _veanh(mau, heso)
    is_lantao = not _anh
    for ten, dulieu in dulieuanh.items():
        if ten in _anh:
            _anh[ten].configure(data = dulieu, format = "png")
        else:
            _anh[ten] = tk.PhotoImage(master = root, data = dulieu, format = "png")

    def px(sopixel):
        return int(sopixel * heso)

    if is_lantao:
        a = _anh
        style.element_create("XQ.Nut.nen", "image", a["nut"], ("disabled", a["nut_tat"]), ("pressed", a["nut_bam"]),
                             ("active", a["nut_re"]), border = kichthuoc["nut"], sticky = "nsew")
        style.element_create("XQ.NutChinh.nen", "image", a["nutchinh"], ("disabled", a["nut_tat"]), ("pressed", a["nutchinh_re"]),
                             ("active", a["nutchinh_re"]), border = kichthuoc["nut"], sticky = "nsew")
        style.element_create("XQ.Tich.chi", "image", a["tich"], ("disabled", "selected", a["tich_co_tat"]), ("disabled", a["tich_tat"]),
                             ("selected", "active", a["tich_co_re"]), ("selected", a["tich_co"]), ("active", a["tich_re"]), sticky = "w")
        style.element_create("XQ.Tab.nen", "image", a["tab"], ("selected", a["tab_chon"]), ("active", a["tab_re"]),
                             border = (2, 2, 2, kichthuoc["vach"] + 1), sticky = "nsew")
        layoutnut = style.layout("TButton")
        style.layout("TButton", _doilayout(layoutnut, {"Button.border": "XQ.Nut.nen", "Button.focus": None}))
        style.layout("Chinh.TButton", _doilayout(layoutnut, {"Button.border": "XQ.NutChinh.nen", "Button.focus": None}))
        for loai in LOAINUTMAU:
            style.element_create(f"XQ.Nut{loai}.nen", "image", a[f"nut_{loai}"], ("disabled", a["nut_tat"]),
                                 ("pressed", a[f"nut_{loai}_re"]), ("active", a[f"nut_{loai}_re"]), border = kichthuoc["nut"], sticky = "nsew")
            style.layout(f"{loai.capitalize()}.TButton", _doilayout(layoutnut, {"Button.border": f"XQ.Nut{loai}.nen", "Button.focus": None}))
        style.layout("TCheckbutton", _doilayout(style.layout("TCheckbutton"), {"Checkbutton.indicator": "XQ.Tich.chi",
                                                                                "Checkbutton.focus": None}))
        style.layout("TNotebook.Tab", _doilayout(style.layout("TNotebook.Tab"), {"Notebook.tab": "XQ.Tab.nen", "Notebook.focus": None}))
        # Thanh cuộn mảnh, bỏ hai nút mũi tên
        for huong, dinh in (("Vertical", "ns"), ("Horizontal", "ew")):
            style.layout(f"{huong}.TScrollbar", [(f"{huong}.Scrollbar.trough", {"sticky": dinh, "children": [
                (f"{huong}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])

    nen, nen_o, vien, chu = mau["nen"], mau["nen_o"], mau["vien"], mau["chu"]
    style.configure(".", background = nen, foreground = chu, bordercolor = vien, lightcolor = nen, darkcolor = nen, troughcolor = nen,
                    fieldbackground = nen_o, selectbackground = mau["chinh"], selectforeground = "#ffffff", insertcolor = chu,
                    focuscolor = mau["chinh"], arrowcolor = mau["chu_phu"], font = font)
    style.map(".", background = [], foreground = [("disabled", mau["chu_mo"])])

    # clam ép nút rộng tối thiểu 11 ký tự (-11) làm nút "Thêm"/"Xoá" to bè: chỉ giữ tối thiểu 4 ký tự, padding gọn
    # clam ép nút rộng tối thiểu 11 ký tự (-11) làm nút "Thêm"/"Xoá" to bè: chỉ giữ tối thiểu 3 ký tự, chữ nhỏ 1 cỡ, padding gọn (kiểu btn-sm)
    style.configure("TButton", padding = (px(8), px(1)), width = -3, foreground = chu, anchor = tk.CENTER, font = (font[0], font[1] - 1))
    style.map("TButton", foreground = [("disabled", mau["chu_mo"])], background = [])
    # Nút màu: chữ trắng, riêng nút vàng (btn-warning) chữ tối cho dễ đọc
    for tenstyle, mauchu in (("Chinh.TButton", "#ffffff"), ("Nguyhiem.TButton", "#ffffff"), ("Canhbao.TButton", "#212529"),
                             ("Thanhcong.TButton", "#ffffff"), ("Phu.TButton", "#ffffff")):
        style.configure(tenstyle, foreground = mauchu)
        style.map(tenstyle, foreground = [("disabled", mau["chu_mo"])])
    style.configure("TCheckbutton", padding = (0, px(1)))
    style.map("TCheckbutton", background = [], indicatorbackground = [])

    style.configure("TLabelframe", bordercolor = vien, lightcolor = nen, darkcolor = nen)
    style.configure("TLabelframe.Label", foreground = chu)

    style.configure("TNotebook", bordercolor = vien, tabmargins = (0, 0, 0, 0))
    style.configure("TNotebook.Tab", padding = (px(12), px(5)), foreground = mau["chu_phu"])
    style.map("TNotebook.Tab", foreground = [("selected", mau["chinh"]), ("active", chu)], background = [], lightcolor = [],
              bordercolor = [], padding = [], expand = [])

    style.configure("Treeview", background = nen_o, fieldbackground = nen_o, foreground = chu, bordercolor = vien,
                    lightcolor = nen_o, darkcolor = nen_o)
    style.map("Treeview", background = [("selected", mau["chon"])], foreground = [("selected", chu)])
    style.configure("Treeview.Heading", background = nen, foreground = mau["chu_phu"], bordercolor = vien, lightcolor = nen,
                    darkcolor = vien, relief = tk.FLAT, padding = (px(6), px(3)))
    style.map("Treeview.Heading", background = [("active", mau["nut_re"])], foreground = [("active", chu)])

    for lop in ("TEntry", "TSpinbox", "TCombobox"):
        style.configure(lop, fieldbackground = nen_o, foreground = chu, bordercolor = vien, lightcolor = nen_o, darkcolor = nen_o,
                        background = nen_o, arrowcolor = mau["chu_phu"], padding = (px(4), px(2)))
        style.map(lop, bordercolor = [("focus", mau["chinh"])], lightcolor = [("focus", mau["chinh"])],
                  fieldbackground = [("disabled", nen), ("readonly", nen_o)], background = [("pressed", mau["nut_bam"]), ("active", mau["nut_re"])],
                  arrowcolor = [("disabled", mau["chu_mo"])], foreground = [("disabled", mau["chu_mo"])])
    style.configure("TSpinbox", arrowsize = px(11))
    style.configure("TCombobox", arrowsize = px(13))
    # Ô chọn chỉ đọc đang focus: tô nhạt thay vì nền xanh đậm cả ô
    style.map("TCombobox", selectbackground = [("readonly", "focus", mau["chon"])], selectforeground = [("readonly", "focus", chu)])

    style.configure("TScrollbar", background = mau["nut_bam"], troughcolor = nen, bordercolor = nen, lightcolor = mau["nut_bam"],
                    darkcolor = mau["nut_bam"], gripcount = 0, arrowsize = px(10))
    style.map("TScrollbar", background = [("pressed", mau["chu_mo"]), ("active", mau["chu_mo"])],
              lightcolor = [("pressed", mau["chu_mo"]), ("active", mau["chu_mo"])],
              darkcolor = [("pressed", mau["chu_mo"]), ("active", mau["chu_mo"])])
    style.configure("TSeparator", background = vien)

    # Widget tk thuần (Label, Frame, Listbox, Text, hộp thoại...) tạo sau này lấy màu từ option database
    for lop in ("Frame", "Label", "Toplevel", "Canvas"):
        root.option_add(f"*{lop}.background", nen)
    root.option_add("*Label.foreground", chu)
    for lop in ("Listbox", "Text"):
        for tuychon, giatri in (("background", nen_o), ("foreground", chu), ("selectBackground", mau["chon"]), ("selectForeground", chu),
                                ("insertBackground", chu), ("relief", tk.FLAT), ("borderWidth", 0), ("highlightThickness", 1),
                                ("highlightBackground", vien), ("highlightColor", mau["chinh"])):
            root.option_add(f"*{lop}.{tuychon}", giatri)
    root.configure(background = nen)


def doithanhtieude(cuaso, is_toi):
    # Windows 10 (20H1+)/11: thanh tiêu đề tối theo chế độ (DWMWA_USE_IMMERSIVE_DARK_MODE = 20); máy cũ không có thì bỏ qua
    try:
        import ctypes
        cuaso.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(cuaso.winfo_id())
        giatri = ctypes.c_int(1 if is_toi else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(giatri), ctypes.sizeof(giatri))
        # Vẽ lại khung cửa sổ ngay (SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED)
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x1 | 0x2 | 0x4 | 0x10 | 0x20)
    except Exception:
        pass


# ------------------------------------------------------------------ Hộp thoại thông báo
# Thay tkinter.messagebox / simpledialog (hộp gốc của Windows, không theo màu giao diện): cùng tên hàm và tham số chính

# Loại hộp -> (khoá màu biểu tượng, chữ trong biểu tượng)
_BIEUTUONG = {"info": ("chinh", "i"), "warning": ("vang", "!"), "error": ("do", "×"), "question": ("chinh", "?")}


def _vungmanhinh(cuaso):
    # Vùng làm việc (trừ taskbar) của màn hình chứa cửa sổ -> (trái, trên, phải, dưới). Cửa sổ đang thu nhỏ thì Windows lấy chỗ trước khi
    # thu nhỏ; nhiều màn hình thì toạ độ có thể âm. Lỗi thì lấy màn hình chính
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        user32.GetParent.restype = ctypes.c_void_p
        user32.GetParent.argtypes = [ctypes.c_void_p]
        user32.MonitorFromWindow.restype = ctypes.c_void_p
        user32.MonitorFromWindow.argtypes = [ctypes.c_void_p, wintypes.DWORD]
        user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        class MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

        hwnd = user32.GetParent(cuaso.winfo_id()) or cuaso.winfo_id()
        thongtin = MONITORINFO(cbSize = ctypes.sizeof(MONITORINFO))
        # MONITOR_DEFAULTTONEAREST = 2
        if user32.GetMonitorInfoW(user32.MonitorFromWindow(hwnd, 2), ctypes.byref(thongtin)):
            vung = thongtin.rcWork
            return vung.left, vung.top, vung.right, vung.bottom
    except Exception:
        pass
    return 0, 0, cuaso.winfo_screenwidth(), cuaso.winfo_screenheight() - int(40 * _hientai["heso"])


def is_chahien(cha):
    # Cửa sổ cha đang hiện trên màn hình (không thu nhỏ / ẩn): thu nhỏ thì toạ độ -32000, hộp transient theo nó cũng bị ẩn theo
    try:
        return cha.state() not in ("iconic", "withdrawn") and cha.winfo_rootx() > -30000
    except tk.TclError:
        return False


def canhgiua(hop, cha):
    # Đặt hộp thoại giữa cửa sổ cha (1/3 chiều cao); cha thu nhỏ / ẩn thì giữa màn hình chứa cha. Không tràn ra ngoài màn hình
    hop.update_idletasks()
    rong, cao = hop.winfo_reqwidth(), hop.winfo_reqheight()
    trai, tren, phai, duoi = _vungmanhinh(cha)
    if is_chahien(cha):
        x = cha.winfo_rootx() + (cha.winfo_width() - rong) // 2
        y = cha.winfo_rooty() + (cha.winfo_height() - cao) // 3
    else:
        x = trai + (phai - trai - rong) // 2
        y = tren + (duoi - tren - cao) // 3
    x = max(trai, min(x, phai - rong))
    y = max(tren, min(y, duoi - cao))
    hop.geometry(f"+{x}+{y}")
    # Áp toạ độ ngay: để chờ lúc rảnh thì đổi -topmost / lift sau đó (dualentren) kéo cửa sổ về chỗ cũ (góc trái trên)
    hop.update_idletasks()


def dualentren(hop, is_giunoi = True):
    # Đưa hộp lên trên mọi cửa sổ và lấy focus bàn phím (không phải click vào). is_giunoi = False: chỉ nổi lúc mở, sau đó thôi topmost
    # (để App không ghim thì cửa sổ khác vẫn đè lên được)
    hop.lift()
    hop.attributes("-topmost", True)
    hop.focus_force()
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.GetParent.restype = ctypes.c_void_p
        user32.GetParent.argtypes = [ctypes.c_void_p]
        user32.SetForegroundWindow.argtypes = [ctypes.c_void_p]
        user32.SetForegroundWindow(user32.GetParent(hop.winfo_id()) or hop.winfo_id())
    except Exception:
        pass
    if not is_giunoi:
        def thoinoi():
            try:
                hop.attributes("-topmost", False)
            except tk.TclError:
                pass
        hop.after(300, thoinoi)


def _hopthoai(tieude, noidung, parent, loai, nuts, o_nhap = None):
    # nuts = [(chữ, giá trị)], nút đầu là nút chính (Enter); Esc / đóng cửa sổ trả giá trị của nút cuối.
    # o_nhap = (giá trị đầu, hàm kiểm tra chuỗi -> (giá trị, lỗi)) thì có ô nhập, nút chính trả giá trị đã kiểm tra
    mau, heso, font = _hientai["mau"], _hientai["heso"], _hientai["font"]

    def px(sopixel):
        return int(sopixel * heso)

    cha = parent.winfo_toplevel() if parent else tk._default_root
    hop = tk.Toplevel(cha)
    # Ẩn tới khi đặt xong chỗ (không loé ở góc trái trên)
    hop.withdraw()
    hop.title(tieude)
    hop.resizable(False, False)
    # Cha đang thu nhỏ thì không transient: hộp transient bị ẩn theo cha, bot báo lúc App thu nhỏ sẽ không thấy
    if is_chahien(cha):
        hop.transient(cha)
    ketqua = {"giatri": nuts[-1][1]}

    khung = ttk.Frame(hop, padding = (px(18), px(16), px(18), px(12)))
    khung.pack(fill = tk.BOTH, expand = True)
    khoamau, kytu = _BIEUTUONG[loai]
    co = px(30)
    bieutuong = tk.Canvas(khung, width = co, height = co, highlightthickness = 0, borderwidth = 0, background = mau["nen"])
    bieutuong.create_oval(1, 1, co - 1, co - 1, fill = mau[khoamau], outline = mau[khoamau])
    bieutuong.create_text(co / 2, co / 2, text = kytu, fill = mau["nen"] if mau is BANGMAU_TOI else "#ffffff", font = (font[0], font[1] + 3, "bold"))
    bieutuong.grid(row = 0, column = 0, rowspan = 2, sticky = tk.N, padx = (0, px(14)))
    ttk.Label(khung, text = noidung, justify = tk.LEFT, wraplength = px(400)).grid(row = 0, column = 1, sticky = tk.W)

    bien, lbl_loi = None, None
    if o_nhap:
        bien = tk.StringVar(value = "" if o_nhap[0] is None else str(o_nhap[0]))
        o = ttk.Entry(khung, textvariable = bien, width = 16)
        o.grid(row = 1, column = 1, sticky = tk.W, pady = (px(10), 0))
        o.select_range(0, tk.END)
        lbl_loi = ttk.Label(khung, text = "", foreground = mau["do"])
        lbl_loi.grid(row = 2, column = 1, sticky = tk.W)

    hangnut = ttk.Frame(khung)
    hangnut.grid(row = 3, column = 0, columnspan = 2, sticky = tk.E, pady = (px(16), 0))

    def bam(giatri, is_chinh):
        if o_nhap and is_chinh:
            giatri, loi = o_nhap[1](bien.get().strip())
            if loi:
                lbl_loi.configure(text = loi)
                return
        ketqua["giatri"] = giatri
        hop.destroy()

    for thutu, (chu, giatri) in enumerate(nuts):
        nut = ttk.Button(hangnut, text = chu, style = "Chinh.TButton" if thutu == 0 else "TButton",
                         command = lambda g = giatri, c = thutu == 0: bam(g, c))
        nut.pack(side = tk.LEFT, padx = (px(8), 0))
        if thutu == 0 and not o_nhap:
            nut.focus_set()
    if o_nhap:
        o.focus_set()
    hop.bind("<Return>", lambda e: bam(nuts[0][1], True))
    hop.bind("<KP_Enter>", lambda e: bam(nuts[0][1], True))
    hop.bind("<Escape>", lambda e: bam(nuts[-1][1], False))
    hop.protocol("WM_DELETE_WINDOW", lambda: bam(nuts[-1][1], False))

    canhgiua(hop, cha)
    hop.deiconify()
    doithanhtieude(hop, mau is BANGMAU_TOI)
    # Hộp thông báo / hỏi luôn nổi trên cùng tới khi đóng
    dualentren(hop)
    if loai in ("warning", "error"):
        hop.bell()
    hop.grab_set()
    hop.wait_window()
    return ketqua["giatri"]


def _thongbao(loai):
    def ham(tieude, noidung, parent = None, **kw):
        _hopthoai(tieude, noidung, parent, loai, [("OK", "ok")])
        return "ok"
    return ham


def _askyesno(tieude, noidung, parent = None, **kw):
    return _hopthoai(tieude, noidung, parent, "question", [("Có", True), ("Không", False)])


def _askinteger(tieude, noidung, parent = None, initialvalue = None, minvalue = None, maxvalue = None, **kw):
    def kiemtra(chuoi):
        try:
            so = int(chuoi)
        except ValueError:
            return None, "Phải là số nguyên"
        if (minvalue is not None and so < minvalue) or (maxvalue is not None and so > maxvalue):
            return None, f"Phải từ {minvalue if minvalue is not None else '...'} tới {maxvalue if maxvalue is not None else '...'}"
        return so, None
    return _hopthoai(tieude, noidung, parent, "question", [("OK", None), ("Huỷ", None)], o_nhap = (initialvalue, kiemtra))


def _askstring(tieude, noidung, parent = None, initialvalue = None, **kw):
    # Ô nhập chữ, bỏ khoảng trắng 2 đầu, không cho để trống. -> chuỗi hoặc None khi huỷ
    def kiemtra(chuoi):
        chuoi = chuoi.strip()
        return (chuoi, None) if chuoi else (None, "Không được để trống")
    return _hopthoai(tieude, noidung, parent, "question", [("OK", None), ("Huỷ", None)], o_nhap = (initialvalue, kiemtra))


class hopthoai:
    showinfo = staticmethod(_thongbao("info"))
    showwarning = staticmethod(_thongbao("warning"))
    showerror = staticmethod(_thongbao("error"))
    askyesno = staticmethod(_askyesno)
    askinteger = staticmethod(_askinteger)
    askstring = staticmethod(_askstring)
