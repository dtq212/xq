import json
import re
import threading
import time
import tkinter as tk
import unicodedata
from tkinter import ttk

# Tẩy (tái tạo) thuộc tính đồ ở NPC Lương Phan Tiên: lấy món ở ô đầu tiên hành trang (ô 0), desc đọc các dòng chỉ số "Tên: +x",
# chưa đạt mọi điều kiện (thuộc tính >= giá trị mong muốn) thì gửi lệnh tái tạo rồi desc lại, lặp tới khi đạt / hết số lần / bấm Dừng.
# Lệnh tái tạo: "talk <ID NPC># giaotrangbi.<ID món># 0" như client gửi khi bấm tay (xem _taitao; NPC tìm theo tên).
# Chạy luồng riêng trong tiến trình bot, không qua LoopChinh / LoopPhu.
# Giao diện: nút "Tẩy thuộc tính đồ" ở tab Khác -> hộp thoại CuaSoTayThuocTinh, gửi lệnh qua command_dict:
#   "taythuoctinh:<json {dieukiens: [[tên, giá trị]...], solantoida, giancach}>"  bắt đầu
#   "huytaythuoctinh"                                                              dừng
#   "docthuoctinh"                                                                 chỉ đọc món ô đầu (để chọn thuộc tính)
# Trạng thái trả về giao diện ở info["_taythuoctinh"] (get_share).

NPCTAYTHUOCTINH = "Lương Phan Tiên"
VITRITAYTHUOCTINH = 0
# NPC xa hơn chừng này ô thì máy chủ bỏ qua lệnh (give tới NPC được 6-9 ô), dừng và báo đứng gần lại
KHOANGCACHNPCTOIDA = 8.
# Giãn cách mặc định giữa 2 lần tái tạo (giây) và tối thiểu cho phép nhập
GIANCACHMACDINH = 0.3
GIANCACHTOITHIEU = 0.15
# Mô tả không đổi sau chừng này lần tái tạo liên tiếp: máy chủ không làm (hết tiền / nguyên liệu, món không tẩy được) -> dừng
SOLANKHONGDOITOIDA = 5
# Chờ mô tả mới sau lệnh desc (giây)
THOIGIANCHOMOTA = 1.5
SOLICHSU = 8
# Số lần desc lại khi mô tả về là dòng rác (xem _docmon)
SOLANDOCLAI = 4


def chuanhoaten(ten):
    # Bỏ dấu, gộp khoảng trắng, chữ thường: "Ngoại  Kháng" / "ngoai khang" đều khớp
    ten = "".join(c for c in unicodedata.normalize("NFD", ten or "") if not unicodedata.combining(c))
    return " ".join(ten.replace("đ", "d").replace("Đ", "D").split()).lower()


def phantichthuoctinh(mota):
    # Mô tả -> (tên món, [(tên thuộc tính, giá trị)...]) theo thứ tự xuất hiện. Chỉ lấy dòng "Tên: +x" (Ngoại Kháng: +452);
    # tên trùng thì giữ lần đầu (dòng chỉ số chính nằm trước các dòng hiệu ứng bộ)
    dongs = [d.strip() for d in re.sub(r"\x1b[a-zA-Z0-9]", "", unicodedata.normalize("NFC", mota or "")).split("\n") if d.strip()]
    if not dongs:
        return "", []
    tenmon = re.sub(r"\s*[（(].*$", "", dongs[0]).strip()
    thuoctinhs, dacos = [], set()
    for dong in dongs[1:]:
        khop = re.match(r"^(.+?)\s*[:：]\s*\+\s*(\d+)", dong)
        if not khop:
            continue
        ten = khop.group(1).strip()
        if chuanhoaten(ten) in dacos:
            continue
        dacos.add(chuanhoaten(ten))
        thuoctinhs.append((ten, int(khop.group(2))))
    return tenmon, thuoctinhs


def kiemtradieukien(thuoctinhs, dieukiens):
    # -> (đạt hết?, [(tên điều kiện, giá trị hiện có hoặc None, giá trị cần, đạt?)])
    theoten = {chuanhoaten(ten): giatri for ten, giatri in thuoctinhs}
    ketqua = []
    for ten, can in dieukiens:
        co = theoten.get(chuanhoaten(ten))
        ketqua.append((ten, co, can, co is not None and co >= can))
    return all(k[3] for k in ketqua) and bool(ketqua), ketqua


class TayThuocTinh:
    # Phía bot: mỗi cửa sổ một đối tượng, luồng riêng (loop)
    def __init__(self, moitruong):
        self.moitruong = moitruong
        self._khoa = threading.Lock()
        self._is_chay = False
        self._is_yeucaudoc = False
        self._dieukiens = []
        self._solantoida = 0
        self._giancach = GIANCACHMACDINH
        self._solan = 0
        self._tenmon = ""
        self._thuoctinhs = []
        self._ketqua = []
        self._trangthai = ""
        self._motatruoc = None
        self._solankhongdoi = 0
        self._lichsu = []

    # --- lệnh từ giao diện ---
    def batdau(self, cauhinh):
        dieukiens = []
        for muc in cauhinh.get("dieukiens") or []:
            try:
                ten, giatri = str(muc[0]).strip(), int(float(muc[1]))
            except (TypeError, ValueError, IndexError):
                continue
            if ten:
                dieukiens.append((ten, giatri))
        if not dieukiens:
            self._trangthai = "Chưa có điều kiện nào"
            return
        with self._khoa:
            self._dieukiens = dieukiens
            try:
                self._solantoida = max(0, int(float(cauhinh.get("solantoida") or 0)))
            except (TypeError, ValueError):
                self._solantoida = 0
            try:
                self._giancach = max(GIANCACHTOITHIEU, float(cauhinh.get("giancach") or GIANCACHMACDINH))
            except (TypeError, ValueError):
                self._giancach = GIANCACHMACDINH
            self._solan = 0
            self._tenmon = ""
            self._motatruoc = None
            self._solankhongdoi = 0
            self._lichsu = []
            self._trangthai = "Đang bắt đầu..."
            self._is_chay = True
        self.moitruong._inlog(f"[TẨY THUỘC TÍNH] Bắt đầu: {', '.join(f'{t} >= {g}' for t, g in dieukiens)}"
                              f"{f', tối đa {self._solantoida} lần' if self._solantoida else ''}")

    def huy(self, lydo = "Đã dừng"):
        if self._is_chay:
            self.moitruong._inlog(f"[TẨY THUỘC TÍNH] {lydo} (sau {self._solan} lần tái tạo)")
        self._is_chay = False
        self._trangthai = lydo

    def yeucaudoc(self):
        self._is_yeucaudoc = True

    def get_share(self):
        return {"chay": self._is_chay, "solan": self._solan, "solantoida": self._solantoida, "tenmon": self._tenmon,
                "thuoctinhs": list(self._thuoctinhs), "ketqua": list(self._ketqua), "trangthai": self._trangthai,
                "lichsu": list(self._lichsu)}

    # --- phía bot ---
    def _docmon(self):
        # Desc lại món ô đầu (xoá mô tả cũ: sau tái tạo mô tả trong ô không tự cập nhật) -> mô tả, "" nếu ô trống / không về
        # Ngay sau tái tạo ô mô tả có thể bị ghi 1 dòng rác kiểu "X1794699097" (thấy 2026-11-15 trên 1039, bot tưởng món ô đầu đổi
        # tên và dừng): mô tả thật luôn nhiều dòng, gặp mô tả 1 dòng thì chờ rồi desc lại, tối đa SOLANDOCLAI lần
        mt = self.moitruong
        for lan in range(SOLANDOCLAI):
            if not mt.get_iddoituongvatphamhanhtrang(VITRITAYTHUOCTINH):
                return ""
            mota = mt.get_motavatphamhanhtrang(VITRITAYTHUOCTINH, thoigianchotoida = THOIGIANCHOMOTA, is_napmoi = True) or ""
            if len([d for d in mota.split("\n") if d.strip()]) >= 2:
                return mota
            time.sleep(0.3)
        return ""

    def _capnhatmon(self, mota):
        self._tenmon, self._thuoctinhs = phantichthuoctinh(mota)
        _, self._ketqua = kiemtradieukien(self._thuoctinhs, self._dieukiens)

    def _taitao(self, idnpc, idmon):
        # 1 lần tái tạo = 1 lệnh "talk <NPC># giaotrangbi.<món># 0", đúng lệnh client gửi khi bấm tay (log [LỆNH GAME] 1039,
        # 2026-11-15 06:22, hex 74 61 6c 6b = "talk"). Gửi "tallk" như đoạn thử cũ trong loop_xq thì máy chủ bỏ qua (06:29 / 06:33: 5 lần
        # Ngoại Kháng đứng yên 419)
        return bool(self.moitruong.action_thucthicaulenh2("talk {:x}# giaotrangbi.{:x}# 0".format(idnpc, idmon)))

    def buoc(self):
        mt = self.moitruong
        if mt.get_is_dangmatketnoi():
            if self._is_chay:
                self.huy("Dừng: mất kết nối")
            return
        if self._is_yeucaudoc and not self._is_chay:
            self._is_yeucaudoc = False
            mota = self._docmon()
            if not mota:
                self._tenmon, self._thuoctinhs, self._ketqua = "", [], []
                self._trangthai = "Ô đầu tiên hành trang trống hoặc chưa đọc được mô tả"
            else:
                self._capnhatmon(mota)
                self._trangthai = f"Đã đọc: {self._tenmon} ({len(self._thuoctinhs)} thuộc tính)"
            return
        if not self._is_chay:
            return

        mota = self._docmon()
        if not mota:
            self.huy("Dừng: ô đầu tiên hành trang trống hoặc không đọc được mô tả")
            return
        tenmontruoc = self._tenmon
        self._capnhatmon(mota)
        # Món ở ô đầu bị đổi (sắp xếp hành trang / tay người chơi) thì dừng, kẻo tẩy nhầm món khác
        if tenmontruoc and self._tenmon != tenmontruoc:
            self.huy(f"Dừng: món ô đầu đổi từ {tenmontruoc} sang {self._tenmon}")
            return
        is_dat, ketqua = kiemtradieukien(self._thuoctinhs, self._dieukiens)
        if self._motatruoc is not None:
            phan = ", ".join(f"{ten} {co if co is not None else '-'}" for ten, co, can, _ in ketqua)
            self._lichsu = ([f"Lần {self._solan}: {phan}"] + self._lichsu)[:SOLICHSU]
        if is_dat:
            self.huy(f"ĐẠT sau {self._solan} lần: " + ", ".join(f"{ten} {co}" for ten, co, can, _ in ketqua))
            return
        # Mô tả đứng yên nhiều lần liền: máy chủ không tái tạo (hết tiền / nguyên liệu, món không tẩy được ở NPC này)
        if self._motatruoc is not None and mota == self._motatruoc:
            self._solankhongdoi += 1
            if self._solankhongdoi >= SOLANKHONGDOITOIDA:
                self.huy(f"Dừng: {SOLANKHONGDOITOIDA} lần tái tạo liền mà thuộc tính không đổi (hết tiền / nguyên liệu? món không tẩy được?)")
                return
        else:
            self._solankhongdoi = 0
        self._motatruoc = mota
        if self._solantoida and self._solan >= self._solantoida:
            self.huy(f"Dừng: hết {self._solantoida} lần mà chưa đạt")
            return

        diachinpc = mt.action_timkiemnhanvat(tennhanvat = NPCTAYTHUOCTINH)
        idnpc = mt.get_iddoituong(diachinpc) if diachinpc else 0
        if not idnpc:
            self.huy(f"Dừng: không thấy NPC {NPCTAYTHUOCTINH} quanh nhân vật")
            return
        khoangcach = mt.get_khoangcach(diachinpc)
        if khoangcach > KHOANGCACHNPCTOIDA:
            self.huy(f"Dừng: đứng cách {NPCTAYTHUOCTINH} {khoangcach:.0f} ô, cần trong {KHOANGCACHNPCTOIDA:.0f} ô")
            return
        idmon = mt.get_iddoituongvatphamhanhtrang(VITRITAYTHUOCTINH)
        if not self._taitao(idnpc, idmon):
            # Hàng đợi lệnh đầy / đang khoá: thử lại lượt sau, không tính lần
            time.sleep(0.3)
            return
        self._solan += 1
        self._trangthai = f"Đang tẩy {self._tenmon}: lần {self._solan}" + (f"/{self._solantoida}" if self._solantoida else "")
        time.sleep(self._giancach)

    def loop(self, stop):
        while not stop.is_set():
            try:
                self.buoc()
            except Exception as err:
                print(f"[TẨY THUỘC TÍNH] Lỗi: {err}")
                if self._is_chay:
                    self.huy(f"Dừng do lỗi: {err}")
                time.sleep(1)
            time.sleep(0.1)


def khoidong_looptaythuoctinh(taythuoctinh, stop):
    taythuoctinh.loop(stop)


# ---------------------------------------------------------------------------------------------------------------------------------------
# Phía giao diện: nút ở tab Khác mở hộp thoại CuaSoTayThuocTinh (luôn nổi trên giao diện chính), áp cho nhân vật đang chọn ở ô
# Nhân vật của giao diện chính

SODIEUKIEN = 3
THUOCTINHGOIY = ["Ngoại Kháng", "Nội Kháng", "Khí Huyết", "Nội Lực", "Ngoại Công", "Nội Công", "Chính Xác", "Né Tránh"]


class NhomTayThuocTinh:
    def __init__(self, giaodien, nhom):
        self.gd = giaodien
        self.nhom = nhom

        hangdoc = ttk.Frame(nhom)
        hangdoc.grid(row = 0, column = 0, sticky = tk.W)
        ttk.Button(hangdoc, text = "Đọc đồ ô đầu hành trang", command = lambda: self._guilenh("docthuoctinh")).pack(side = tk.LEFT)
        self.lbl_mon = ttk.Label(hangdoc, text = "")
        self.lbl_mon.pack(side = tk.LEFT, padx = (8, 0))
        giaodien._taohuongdan(hangdoc, f"Đặt món cần tẩy vào Ô ĐẦU TIÊN hành trang, đứng cạnh NPC {NPCTAYTHUOCTINH}"
                                       f" (trong {KHOANGCACHNPCTOIDA:.0f} ô). Áp cho nhân vật đang chọn ở ô Nhân vật.\n"
                                       "• Mỗi lần: desc món, chưa đạt TẤT CẢ điều kiện (thuộc tính ≥ giá trị) thì gửi lệnh tái tạo.\n"
                                       "• Tự dừng khi đạt, hết số lần, không thấy NPC, món ô đầu bị đổi, hoặc "
                                       f"{SOLANKHONGDOITOIDA} lần liền thuộc tính không đổi (hết tiền / nguyên liệu).\n"
                                       "• Nên tắt Sắp xếp hành trang trong lúc tẩy.")
        self.lbl_thuoctinh = ttk.Label(nhom, text = "", style = "Phu.TLabel")
        self.lbl_thuoctinh.grid(row = 1, column = 0, sticky = tk.W)

        hangdk = ttk.Frame(nhom)
        hangdk.grid(row = 2, column = 0, sticky = tk.W, pady = (4, 0))
        self.cbo_tts, self.var_gts = [], []
        for i in range(SODIEUKIEN):
            cbo = ttk.Combobox(hangdk, width = 14, values = THUOCTINHGOIY)
            cbo.grid(row = 0, column = i * 3, sticky = tk.W)
            ttk.Label(hangdk, text = " ≥ ").grid(row = 0, column = i * 3 + 1)
            var = tk.StringVar()
            ttk.Entry(hangdk, textvariable = var, width = 6).grid(row = 0, column = i * 3 + 2, sticky = tk.W, padx = (0, 10))
            self.cbo_tts.append(cbo)
            self.var_gts.append(var)

        hangnut = ttk.Frame(nhom)
        hangnut.grid(row = 3, column = 0, sticky = tk.W, pady = (4, 0))
        ttk.Label(hangnut, text = "Tối đa").pack(side = tk.LEFT)
        self.var_solan = tk.StringVar(value = "0")
        ttk.Entry(hangnut, textvariable = self.var_solan, width = 6).pack(side = tk.LEFT, padx = 4)
        ttk.Label(hangnut, text = "lần (0 = mãi)  Cách").pack(side = tk.LEFT)
        self.var_giancach = tk.StringVar(value = f"{GIANCACHMACDINH:g}")
        ttk.Entry(hangnut, textvariable = self.var_giancach, width = 5).pack(side = tk.LEFT, padx = 4)
        ttk.Label(hangnut, text = "giây").pack(side = tk.LEFT)
        ttk.Button(hangnut, text = "Bắt đầu tẩy", command = self._batdau).pack(side = tk.LEFT, padx = (12, 0))
        ttk.Button(hangnut, text = "Dừng", command = lambda: self._guilenh("huytaythuoctinh")).pack(side = tk.LEFT, padx = (6, 0))

        self.lbl_trangthai = ttk.Label(nhom, text = "", justify = tk.LEFT)
        self.lbl_trangthai.grid(row = 4, column = 0, sticky = tk.W, pady = (4, 0))
        self.lbl_lichsu = ttk.Label(nhom, text = "", style = "Phu.TLabel", justify = tk.LEFT)
        self.lbl_lichsu.grid(row = 5, column = 0, sticky = tk.W)

        self._thongbao = ""
        self._lucthongbao = 0.
        self._capnhattrangthai()

    def _hwnd(self):
        try:
            return self.gd.get_selected_hwnd()
        except Exception:
            return None

    def _guilenh(self, lenh):
        hwnd = self._hwnd()
        if not hwnd:
            self._bao("Chọn nhân vật ở ô Nhân vật trước")
            return False
        self.gd.command_dict[hwnd] = lenh
        return True

    def _bao(self, chu):
        self._thongbao, self._lucthongbao = chu, time.time()

    def _batdau(self):
        dieukiens = []
        for cbo, var in zip(self.cbo_tts, self.var_gts):
            ten = cbo.get().strip()
            if not ten:
                continue
            try:
                dieukiens.append([ten, int(float(var.get().strip()))])
            except ValueError:
                self._bao(f"Giá trị của {ten} không phải số")
                return
        if not dieukiens:
            self._bao("Nhập ít nhất 1 thuộc tính và giá trị mong muốn")
            return
        cauhinh = {"dieukiens": dieukiens, "solantoida": self.var_solan.get().strip() or "0",
                   "giancach": self.var_giancach.get().strip() or str(GIANCACHMACDINH)}
        if self._guilenh("taythuoctinh:" + json.dumps(cauhinh, ensure_ascii = False)):
            self._bao("Đã gửi lệnh bắt đầu")

    def _capnhattrangthai(self):
        try:
            if not self.nhom.winfo_exists():
                return
        except tk.TclError:
            return
        try:
            hwnd = self._hwnd()
            try:
                tt = (self.gd.shared_data.get(hwnd) or {}).get("_taythuoctinh") if hwnd else None
            except Exception:
                tt = None
            info = {}
            try:
                info = (self.gd.shared_data.get(hwnd) or {}) if hwnd else {}
            except Exception:
                pass
            dong = [f"Nhân vật: {info.get('tennhanvat')} ({info.get('idnguoichoi')})" if info.get("tennhanvat")
                    else "Chưa chọn nhân vật ở ô Nhân vật của giao diện chính"]
            if time.time() - self._lucthongbao < 4 and self._thongbao:
                dong.append(self._thongbao)
            if not tt:
                if hwnd and tt is None:
                    dong.append("Chưa có dữ liệu từ bot (khởi động lại bot sau khi cập nhật)")
                self.lbl_mon.configure(text = "")
                self.lbl_thuoctinh.configure(text = "")
                self.lbl_lichsu.configure(text = "")
            else:
                self.lbl_mon.configure(text = tt.get("tenmon") or "")
                thuoctinhs = tt.get("thuoctinhs") or []
                self.lbl_thuoctinh.configure(text = "  ·  ".join(f"{ten} +{gt}" for ten, gt in thuoctinhs))
                # Gợi ý tên thuộc tính theo món vừa đọc (giữ cả danh sách gợi ý sẵn)
                tens = [ten for ten, _ in thuoctinhs]
                datens = {chuanhoaten(x) for x in tens}
                goiy = tens + [t for t in THUOCTINHGOIY if chuanhoaten(t) not in datens]
                for cbo in self.cbo_tts:
                    if list(cbo.cget("values")) != goiy:
                        cbo.configure(values = goiy)
                if tt.get("trangthai"):
                    dong.append(("▶ " if tt.get("chay") else "") + tt["trangthai"])
                if tt.get("ketqua"):
                    dong.append("Điều kiện: " + "  ·  ".join(f"{ten} {co if co is not None else 'không có'} / {can} {'✓' if dat else '✗'}"
                                                              for ten, co, can, dat in tt["ketqua"]))
                # Chỉ 3 lần gần nhất cho đỡ dài tab
                self.lbl_lichsu.configure(text = "\n".join((tt.get("lichsu") or [])[:3]))
            self.lbl_trangthai.configure(text = "\n".join(dong))
        except Exception as err:
            print(f"[TẨY THUỘC TÍNH] Lỗi cập nhật giao diện: {err}")
        self.nhom.after(500, self._capnhattrangthai)


class CuaSoTayThuocTinh:
    # Hộp thoại riêng (gọn tab Khác) chứa NhomTayThuocTinh. Luôn nổi trên giao diện chính: transient theo cửa sổ chính + -topmost
    # (giao diện chính bật Ghim là topmost, hộp thường bị nó che mất)
    def __init__(self, giaodien):
        self.gd = giaodien
        self.top = tk.Toplevel(giaodien.root)
        self.top.title("Tẩy thuộc tính đồ")
        self.top.configure(background = giaodien._mau.get("nen", "#ffffff"))
        self.top.protocol("WM_DELETE_WINDOW", self.dong)
        try:
            self.top.transient(giaodien.root)
        except tk.TclError:
            pass
        khung = ttk.Frame(self.top, padding = 10)
        khung.pack(fill = tk.BOTH, expand = True)
        khung.columnconfigure(0, weight = 1)
        self.nhom = NhomTayThuocTinh(giaodien, khung)
        try:
            from chude_xq import doithanhtieude, canhgiua
            canhgiua(self.top, giaodien.root)
            self.top.after(0, lambda: doithanhtieude(self.top, getattr(giaodien, "is_chedotoi", False)))
        except Exception:
            pass
        self.hienlen()

    def dong(self):
        self.gd._taythuoctinh = None
        self.top.destroy()

    def hienlen(self):
        self.top.deiconify()
        self.top.lift()
        self.top.attributes("-topmost", True)


def motaythuoctinh(giaodien):
    if getattr(giaodien, "_taythuoctinh", None):
        try:
            giaodien._taythuoctinh.hienlen()
            return
        except tk.TclError:
            pass
    giaodien._taythuoctinh = CuaSoTayThuocTinh(giaodien)
