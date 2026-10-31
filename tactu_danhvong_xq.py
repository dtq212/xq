# Nhiệm vụ Danh Vọng (bật tay trên giao diện, chạy tới khi bấm dừng / Tề Tổng Quản không giao nữa). Nhận / trả ở Tề Tổng Quản, Tề Quốc
# (89, 168): "look" -> "1. Nhiệm vụ Danh vọng" -> "1. Tiếp nhận". Mỗi lượt đọc nhiệm vụ trong cửa sổ nhiệm vụ (mục "Nhiệm vụ Danh Vọng",
# như sư môn: không nhớ quy trình riêng, tắt / bật lại giữa chừng vẫn làm tiếp được) rồi làm bước kế:
#   Trang Bị Quân Đội    : "Tìm kiếm một trang bị môn phái <Phái> cấp <N> giao cho Tề Tổng Quản" -> mua vũ khí môn phái đó ở Chủ Tiệm Vũ
#                          Khí nước có môn phái (BANDOVUKHIMONPHAI), đúng cấp (cấp đọc ở "Cấp độ sử dụng" trong mô tả món; chưa biết món
#                          nào cấp mấy thì đoán ô thứ N/10 trong cửa hàng, mua sai thì học cấp món đó rồi đoán lại), về give Tề Tổng Quản
#   Truy Sát Kẻ Phản Bội : "Tiêu diệt kẻ phản bội <Tên> sau đó quay về gặp Tề Tổng Quản" -> kẻ phản bội ("<Tên> (ID mình)") luôn ở Tề Quốc:
#                          dùng Công Văn Truy Nã (hết thì mua ở Chủ Tiệm Tạp Hóa Tề Quốc) tới chấm vàng, đánh tới chết, về trả
#   Thăm Hỏi <NPC>       : tới NPC (bản đồ trong mô tả) -> "1. Thăm Hỏi <NPC>" -> "1. Hoàn thành nhiệm vụ"
# Dùng chung phần đi đường / tìm NPC / cửa hàng / Công Văn Truy Nã của sư môn (tactu_sumon_xq): các hàm đó nhận dict trạng thái s nên
# self._danhvong có đủ các khoá chúng cần (khampha, dabao, trangthai, lucmonphai, solanmonphai, truyna).
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import json
import math
import os
import re
import time
import unicodedata

from hangso_xq import *
from giaodo_xq import taolenhgiao
from nhiemvu_xq import chuanhoaten, boma, timbandotheoten, laydiemluoi, _thumucgoc
from thongbao_xq import baosuco
from tienich_xq import phatam, thaythefile
from tactu_sumon_xq import THOIGIANCHOTRUYNA, KHOANGCACHTOICHAMTRUYNA

MUCDANHVONG = "Nhiệm vụ Danh Vọng"
TETONGQUAN = "Tề Tổng Quản"
CHUTIEMVUKHI = "Chủ Tiệm Vũ Khí"
CONGVANTRUYNA = "Công Văn Truy Nã"
SOLUONGMUACONGVANTRUYNA = 5
# Vũ khí môn phái bán ở Chủ Tiệm Vũ Khí của nước này
BANDOVUKHIMONPHAI = {"vanmongcoc": BANDO_NGUYQUOC, "conluan": BANDO_TANQUOC, "camvequan": BANDO_CHUQUOC, "duongmon": BANDO_HANQUOC,
                     "maoson": BANDO_TEQUOC, "thucson": BANDO_YENQUOC, "daohoanguyen": BANDO_TRIEUQUOC}
# Mua sai cấp (đoán ô) tối đa chừng này món mỗi lượt rồi dừng báo
SOLANMUAVUKHITOIDA = 3
# Hội thoại / mua: gửi xong chờ chừng này giây cho nhiệm vụ / túi đổi, quá SOLANTHUDANHVONG lần không đổi thì dừng
SOLANTHUDANHVONG = 3
THOIGIANCHODOI = 4.
THOIGIANCHONHAN = 12.
GIANCACHBUOCHOITHOAI = 0.8
THOIGIANCHOMENU = 2.
KHOANGCACHNOICHUYEN = 3.
KHOANGCACHNOICHUYENKET = 6.
THOIGIANKHONGNHICH = 10.
GIANCACHXINNHIEMVU = 10.
THOIGIANCHOMOTANHIEMVU = 30.
GIANCACHDESC = 1.5
# Desc món trong cửa hàng chừng này lần mà không ra mô tả thì mua thử như cũ
SOLANDESCCUAHANG = 3
# Nhiệm vụ Danh Vọng mỗi ngày tối đa chừng này lượt
SOLUOTDANHVONGMOINGAY = 30
# Kẻ phản bội khuất tầm nhìn chưa tới chừng này giây sau lần thấy cuối, lúc đó còn dưới chừng này % máu và ở gần: coi như đã chết
THOIGIANMATDOITHU = 5.
MAUMATDOITHU = 25
KHOANGCACHMATDOITHU = 10.
THOIGIANDANHVONGTOIDA = 4 * 3600.
# Dùng Công Văn Truy Nã khi con cần giết đã chết: thông báo giữa màn hình "Không tìm thấy mục tiêu đang tồn tại. Hãy kiểm tra ..."
LOIKHONGCONMUCTIEU = "Không tìm thấy mục tiêu đang tồn tại"
THOIGIANCHODOITHUXUATHIEN = 15.
# Kẹt (TacTuDanhVong._chongketdv): chừng này giây không gần đích thêm thì đi theo ô đã đi, nhắm ô cách chừng này bước trên lộ trình,
# đi theo lộ trình tối đa chừng này giây
THOIGIANKETDV = 12.
DIEMTRUOCDV = 6
THOIGIANLOTRINHDADI = 90.

# Cấp các món đã đọc được từ mô tả (tên chuẩn hoá -> cấp), dùng chung cả phiên để đoán ô cửa hàng
_CAPVUKHI = {}
# Cấp đã đo được (log 2026-10-31), để khỏi mua sai lần đầu; món mới học thêm ghi vào _internal/capvukhi.json (dùng chung mọi nhân vật)
CAPVUKHIDABIET = {
    "Xích Kim Giản": 80,          # Nguỵ Quốc (Vân Mộng Cốc), ô 8
    "Huyền Minh Giản": 80,        # Tần Quốc (Côn Luân), ô 8
    "Toả Hầu Thương": 80,         # Chu Quốc (Cấm Vệ Quân), ô 7 (Chu bắt đầu từ cấp 20)
    "Kim Hoàn Thương": 90,        # Chu Quốc, ô 8
    "Tích Lịch Đạn": 80,          # Hàn Quốc (Đường Môn), ô 8
    "Tịch Tà Kiếm": 80,           # Tề Quốc (Mao Sơn), ô 8
    "Tử Huyết Hộ Thủ": 80,        # Triệu Quốc (Đào Hoa Nguyên), ô 8 (Triệu không có ô 1)
    "Huyền Thiết Quyền Thủ": 90,  # Triệu Quốc, ô 9
}


def _duongdancapvukhi():
    return os.path.join(_thumucgoc(), "_internal", "capvukhi.json")


def _laycapvukhi():
    # Tên chuẩn hoá -> cấp: bảng biết sẵn + file đã học, nạp 1 lần mỗi phiên
    if not _CAPVUKHI:
        _CAPVUKHI.update({chuanhoaten(t): c for t, c in CAPVUKHIDABIET.items()})
        try:
            with open(_duongdancapvukhi(), encoding = "utf-8") as file:
                _CAPVUKHI.update({chuanhoaten(t): int(c) for t, c in json.load(file).items()})
        except (OSError, ValueError):
            pass
    return _CAPVUKHI


def _ghicapvukhi(ten, cap):
    capbiet = _laycapvukhi()
    if not cap or capbiet.get(chuanhoaten(ten)) == cap:
        return
    capbiet[chuanhoaten(ten)] = cap
    try:
        with open(_duongdancapvukhi(), encoding = "utf-8") as file:
            dulieu = json.load(file)
    except (OSError, ValueError):
        dulieu = {}
    dulieu[ten] = cap
    try:
        with open(_duongdancapvukhi() + ".tmp", "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False, indent = 1)
        thaythefile(_duongdancapvukhi() + ".tmp", _duongdancapvukhi())
    except OSError as err:
        print(f"[DANH VỌNG] Lỗi lưu cấp vũ khí: {err}")


def laynhiemvudanhvong(mucs):
    # mucs: [(tên mục, mô tả), ...] của cửa sổ nhiệm vụ -> nhiệm vụ Danh Vọng đang nhận (dict) hoặc None
    is_trongmuc = False
    for ten, mota in mucs:
        if not ten.startswith(" "):
            is_trongmuc = chuanhoaten(ten) == chuanhoaten(MUCDANHVONG)
            continue
        if is_trongmuc:
            return phantichdanhvong(ten.strip(), mota)
    return None


def phantichdanhvong(tenmuc, mota):
    # -> {"ten", "is_xong", "luot", "conlai", "loai" (trangbi / truysat / thamhoi / None), "mota", "khoa", ...thông tin theo loại}
    is_xong = bool(re.search(r"\(\s*Xong\s*\)\s*$", tenmuc))
    ten = unicodedata.normalize("NFC", re.sub(r"\(\s*Xong\s*\)\s*$", "", tenmuc).strip())
    vanban = re.sub(r"\s+", " ", unicodedata.normalize("NFC", boma(mota))).strip()
    luot = re.search(r"lượt thứ\s*(\d+)", vanban, re.IGNORECASE)
    conlai = re.search(r"còn lại\s*(\d+)\s*phút", vanban, re.IGNORECASE)
    nv = {"ten": ten, "is_xong": is_xong, "luot": int(luot.group(1)) if luot else 0, "conlai": int(conlai.group(1)) if conlai else None,
          "loai": None, "mota": vanban}
    nv["khoa"] = f"{nv['luot']}|{ten}"
    m = re.search(r"trang bị môn phái\s+(.+?)\s+cấp\s*(\d+)", vanban, re.IGNORECASE)
    if m:
        tenphai = m.group(1).strip()
        nv.update(loai = "trangbi", tenphai = tenphai, cap = int(m.group(2)),
                  phai = next((ma for ma, t in TENMONPHAI.items() if chuanhoaten(t) == chuanhoaten(tenphai)), None))
        return nv
    # (tên mục "Truy Sát Kẻ Phản Bội ( Tề Quốc )" cũng có chữ "kẻ phản bội": tìm sau "diệt")
    m = re.search(r"diệt kẻ phản bội\s+(.+?)\s+(?:sau đó|rồi|,|\.|\()", vanban, re.IGNORECASE) \
        or re.search(r"diệt kẻ phản bội\s+([^,.(]+)", vanban, re.IGNORECASE)
    if m or chuanhoaten(ten).startswith(chuanhoaten("Truy Sát")):
        doithu = m.group(1).strip() if m else ""
        nv.update(loai = "truysat", doithu = doithu, doithus = [doithu] if doithu else [])
        return nv
    # Nhiệm Vụ Ám Sát: "Truy sát và tiêu diệt Thủ Lĩnh Thích Khách và Thích Khách Bịt Mặt (lượt thứ 2, ...)" -> làm y như Truy Sát:
    # chỉ có 1 con NPC là tên đầu (Thủ Lĩnh Thích Khách ( ID )), Công Văn Truy Nã chỉ chỗ con đó
    if chuanhoaten(ten).startswith(chuanhoaten("Nhiệm Vụ Ám Sát")) or chuanhoaten(ten).startswith(chuanhoaten("Ám Sát")):
        m = re.search(r"tiêu diệt\s+(.+?)\s*(?:\(\s*lượt|sau đó|rồi quay|\.|$)", vanban, re.IGNORECASE)
        doithus = [t.strip() for t in re.split(r"\s+và\s+|,", m.group(1)) if t.strip()][:1] if m else []
        nv.update(loai = "truysat", doithu = doithus[0] if doithus else "Thủ Lĩnh Thích Khách", doithus = doithus or ["Thủ Lĩnh Thích Khách"])
        return nv
    if chuanhoaten(ten).startswith(chuanhoaten("Thăm Hỏi")):
        npc = ten[len("Thăm Hỏi"):].strip()
        if not npc:
            m = re.search(r"thăm hỏi\s+(.+?)\s+(?<!\w)(?:tại|ở)\s", vanban, re.IGNORECASE)
            npc = m.group(1).strip() if m else ""
        # "... đến nhà <NPC> tại <bản đồ> chơi nhiều ngày": thử bỏ dần chữ cuối cho tới khi khớp tên bản đồ. "tại" / "ở" phải là 1 chữ riêng
        # (trước đây "ở" khớp vào chữ "Sở" trong "Sở Tổng Quản" nên không ra bản đồ)
        idbando = None
        for m in re.finditer(r"(?<!\w)(?:tại|ở)\s+([^,.;:!?()]+)", vanban, re.IGNORECASE):
            tus = m.group(1).split()
            for k in range(min(len(tus), 5), 0, -1):
                idbando = timbandotheoten(" ".join(tus[:k]))
                if idbando:
                    break
            if idbando:
                break
        nv.update(loai = "thamhoi", npc = npc, bando = idbando)
    return nv


def motadanhvong(nv):
    if not nv:
        return "không có nhiệm vụ"
    chu = f"{nv['ten']}{' (Xong)' if nv['is_xong'] else ''} lượt {nv['luot']}"
    if nv["conlai"] is not None:
        chu += f", còn {nv['conlai']} phút"
    if nv["loai"] == "trangbi":
        chu += f": vũ khí {nv['tenphai']} cấp {nv['cap']}"
    elif nv["loai"] == "truysat":
        chu += f": giết {nv['doithu'] or '?'}"
    elif nv["loai"] == "thamhoi":
        chu += f": {nv['npc'] or '?'} ({laytenbando(nv['bando']) if nv['bando'] else 'chưa rõ bản đồ'})"
    return chu


class TacTuDanhVong:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_danhvong(self):
        if self._danhvong:
            return
        self._danhvong = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "thu": {}, "hoithoai": None, "dabao": set(),
                          "khampha": None, "lucmonphai": 0., "solanmonphai": 0, "soluotxong": 0, "khoadangnhan": None, "tenquai": set(),
                          "dagiet": set(), "doithu": None, "capmon": {}, "lucdesc": 0., "solanmua": {}}
        self._logdv("Bắt đầu làm nhiệm vụ Danh Vọng")
        # Đi một mình: Theo sau đang bật thì bot bị kéo về phía người được theo sau; tạm tắt, dừng thì trả lại
        self._doituychondv(self._danhvong, "_is_tudongtheosau", False, "Theo sau")
        phatam("Bắt đầu nhiệm vụ Danh Vọng")

    def huy_danhvong(self):
        if self._danhvong:
            self._ketthucdanhvong(thongbao = "Đã dừng nhiệm vụ Danh Vọng (bấm tay)")

    def get_is_dangdanhvong(self):
        return bool(self._danhvong)

    def get_is_danhvongdichuyen(self):
        # Đang tự lo đi lại / nói chuyện NPC / mua đồ: không chọn quái dọc đường
        return bool(self._danhvong) and self._danhvong["chedo"] == "dichuyen"

    def get_is_danhvongdanhquai(self):
        # Truy Sát ở Tề Quốc: chỉ đánh kẻ phản bội (self._danhvong["tenquai"])
        return bool(self._danhvong) and self._danhvong["chedo"] == "danhquai"

    def get_trangthaidanhvong(self):
        if self._danhvong:
            return f"Danh Vọng (phiên này trả {self._danhvong['soluotxong']} lượt): {self._danhvong['trangthai']}"
        return self._ketquadanhvong or ""

    def _logdv(self, noidung):
        self.moitruong._inlog(f"[DANH VỌNG] {noidung}")

    def _doituychondv(self, s, thuoctinh, giatri, ten):
        # Đổi 1 ô thiết lập, nhớ giá trị cũ (s["tuychoncu"]) để trả lại khi dừng; luuthietlap lưu giá trị cũ này
        if getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self._logdv(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng Danh Vọng thì trả lại)")

    def _ketthucdanhvong(self, loi = None, thongbao = None):
        s = self._danhvong
        self._danhvong = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        noidung = thongbao or (f"❌ Danh Vọng dừng: {loi}" if loi else "✅ Xong nhiệm vụ Danh Vọng")
        if s and s["soluotxong"]:
            noidung += f" (phiên này trả {s['soluotxong']} lượt)"
        self._logdv(noidung)
        self._ketquadanhvong = f"{time.strftime('%H:%M')} {noidung}"
        baosuco(self.moitruong, "sumon", noidung, khoa = f"danhvong|{s['batdau']}" if s else None, giancach = 0.)
        phatam("Lỗi nhiệm vụ Danh Vọng" if loi else "Kết thúc nhiệm vụ Danh Vọng")

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulydanhvong(self):
        # Gọi thay lộ trình điểm đánh khi đang làm Danh Vọng -> yêu cầu di chuyển hoặc None (kẹt thì đổi sang đi theo ô đã đi)
        yeucau = self._xulydanhvongchinh()
        return self._chongketdv(self._danhvong, yeucau) if self._danhvong else yeucau

    def _chongketdv(self, s, yeucau):
        # Đi trong cùng bản đồ mà THOIGIANKETDV giây không gần đích thêm (Sở Quốc: từ phía đông không vào được Vương Phủ, tìm đường cục
        # bộ báo đoạn cụt, tự động tìm đường của game đứng im) thì đi theo các ô nhân vật từng đứng (SoVitri.laydadi, gộp mọi nhân vật: đường
        # chắc chắn đi được) tới ô gần đích nhất, mỗi lần nhắm ô cách DIEMTRUOCDV ô trên lộ trình; tới cuối lộ trình thì đi thẳng như cũ
        moitruong = self.moitruong
        idbando = moitruong.get_idbandohientai()
        dich = (yeucau or {}).get("toadodich")
        if not dich or (yeucau or {}).get("yeucau") != YEUCAUDICHUYENDICHUYENTUDO or (len(dich) >= 3 and dich[2] != idbando):
            s["ket"] = None
            return yeucau
        now = time.time()
        toado = moitruong.get_toado()
        khoangcach = math.dist(toado, dich[:2])
        k = s.get("ket")
        if not k or k["idbando"] != idbando or math.dist(k["dich"], dich[:2]) > 5:
            k = s["ket"] = {"idbando": idbando, "dich": tuple(dich[:2]), "ganhat": khoangcach, "luc": now, "lotrinh": None}
        if khoangcach < k["ganhat"] - 1:
            k["ganhat"], k["luc"] = khoangcach, now
        if not k["lotrinh"]:
            if now - k["luc"] < THOIGIANKETDV or khoangcach <= 6:
                return yeucau
            k["lotrinh"] = self._timlotrinhdadi(idbando, toado, dich[:2])
            k["luc"] = now
            if not k["lotrinh"]:
                self._logdv(f"Kẹt {THOIGIANKETDV:.0f}s ở {tuple(toado)} khi tới {tuple(dich[:2])}, không có lộ trình ô đã đi")
                return yeucau
            self._logdv(f"Kẹt ở {tuple(toado)} khi tới {tuple(dich[:2])}: đi theo {len(k['lotrinh'])} ô đã đi "
                        f"{k['lotrinh'][::max(1, len(k['lotrinh']) // 6)]}")
        lotrinh = k["lotrinh"]
        i = min(range(len(lotrinh)), key = lambda j: math.dist(lotrinh[j], toado))
        if math.dist(lotrinh[-1], toado) <= 3 or now - k["luc"] > THOIGIANLOTRINHDADI:
            # Hết lộ trình (hoặc đi mãi chưa hết): đi thẳng như cũ, kẹt nữa thì tính lại
            k.update(lotrinh = None, luc = now, ganhat = khoangcach)
            return yeucau
        x, y = lotrinh[min(i + DIEMTRUOCDV, len(lotrinh) - 1)]
        return dict(yeucau, toadodich = (x, y, idbando), khoangcachtoida = 1., is_dioo = True)

    def _timlotrinhdadi(self, idbando, tu, den):
        # BFS trên các ô đã đi (nối 2 ô cách nhau tối đa 3 ô) từ ô gần mình nhất tới ô gần đích nhất -> [(x, y), ...] hoặc None
        os_ = self._sovitri.laydadi(idbando)
        if not os_:
            return None
        dau = min(os_, key = lambda o: math.dist(o, tu))
        cuoi = min(os_, key = lambda o: math.dist(o, den))
        if math.dist(dau, tu) > 6 or math.dist(cuoi, den) >= math.dist(tu, den):
            return None
        lechs = [(dx, dy) for dx in range(-3, 4) for dy in range(-3, 4) if (dx or dy) and dx * dx + dy * dy <= 9]
        truoc = {dau: None}
        hang = [dau]
        for o in hang:
            if o == cuoi:
                break
            for dx, dy in lechs:
                ke = (o[0] + dx, o[1] + dy)
                if ke in os_ and ke not in truoc:
                    truoc[ke] = o
                    hang.append(ke)
        if cuoi not in truoc:
            return None
        lotrinh, o = [], cuoi
        while o:
            lotrinh.append(o)
            o = truoc[o]
        return lotrinh[::-1]

    def _xulydanhvongchinh(self):
        s = self._danhvong
        moitruong = self.moitruong
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logdv(f"Trạng thái: {s['trangthai']}")
        chan = next((ly for ly, co in (("nhân vật chết", moitruong.get_is_nhanvatdachet()), ("đang vận khí", moitruong.get_is_dangvankhi()),
                                       ("đang hội thoại NPC", self.get_is_danghoithoainpc()),
                                       (f"đang về bán (bước {self._trangthaiveban})", self._trangthaiveban != 0)) if co), None)
        if chan:
            if chan != s.get("chan"):
                s["chan"] = chan
                self._logdv(f"Tạm chờ: {chan}")
            return None
        s["chan"] = None
        if time.time() - s["batdau"] > THOIGIANDANHVONGTOIDA:
            self._ketthucdanhvong(f"quá {int(THOIGIANDANHVONGTOIDA // 3600)} giờ")
            return None
        if s["hoithoai"]:
            s["chedo"] = "dichuyen"
            self._xulyhoithoaidv(s)
            return None
        if self._mocuahang:
            s["trangthai"] = "đọc hàng cửa hàng"
            return None

        mucs = moitruong.get_danhsachmucnhiemvu()
        if mucs is None:
            s["trangthai"] = "chưa đọc được nhiệm vụ: mở bảng nhiệm vụ trong game 1 lần"
            if time.time() - s.get("lucxinnhiemvu", 0.) > GIANCACHXINNHIEMVU:
                s["lucxinnhiemvu"] = time.time()
                self._logdv("Chưa đọc được cửa sổ nhiệm vụ: gửi \"quest list\"")
                moitruong.action_thucthicaulenh("quest list")
            return None
        nv = laynhiemvudanhvong(mucs)
        # Có tên mà mô tả còn trống: xin mô tả ("quest intro <mã>", như bấm vào dòng đó), chờ tối đa THOIGIANCHOMOTANHIEMVU giây
        if nv and not nv["mota"] and not nv["is_xong"]:
            s.setdefault("luctrongmota", time.time())
            ma = moitruong.get_manhiemvu(MUCDANHVONG)
            if ma and time.time() - s.get("lucxinmota", 0.) > GIANCACHXINNHIEMVU:
                s["lucxinmota"] = time.time()
                self._logdv(f"Mô tả {nv['ten']} còn trống: gửi \"quest intro {ma[0]} {ma[1]} {ma[2]}\"")
                moitruong.action_thucthicaulenh(f"quest intro {ma[0]} {ma[1]} {ma[2]}")
            if time.time() - s["luctrongmota"] < THOIGIANCHOMOTANHIEMVU:
                s["trangthai"] = f"chờ mô tả nhiệm vụ {nv['ten']}"
                return None
        else:
            s.pop("luctrongmota", None)
        # Nhiệm vụ đang nhận đổi / mất: đã trả xong lượt trước
        if s["khoadangnhan"] and (not nv or nv["khoa"] != s["khoadangnhan"]):
            s["soluotxong"] += 1
            self._logdv(f"Đã trả {s['khoadangnhan']}")
            # Mỗi ngày chỉ SOLUOTDANHVONGMOINGAY lượt (người dùng): trả xong lượt cuối thì thôi, không quay về nhận nữa
            luotvuatra = int(s["khoadangnhan"].split("|", 1)[0] or 0)
            if not nv and luotvuatra >= SOLUOTDANHVONGMOINGAY:
                self._ketthucdanhvong(thongbao = f"✅ Đã đủ {SOLUOTDANHVONGMOINGAY} lượt Danh Vọng hôm nay")
                return None
        s["khoadangnhan"] = nv["khoa"] if nv else None
        motanv = motadanhvong(nv)
        if motanv != s.get("motanv"):
            s["motanv"] = motanv
            self._logdv(f"Nhiệm vụ: {motanv}" + (f" | {nv['mota'][:200]!r}" if nv else ""))
        s["chedo"], s["tenquai"] = "dichuyen", set()

        if not nv:
            s["trangthai"] = "nhận nhiệm vụ ở Tề Tổng Quản"
            return self._noichuyendv(s, nv, TETONGQUAN, ["look", "chon1", "chon1"], "nhận nhiệm vụ", BANDO_TEQUOC)
        if nv["is_xong"]:
            return self._tradanhvong(s, nv)
        if nv["loai"] == "trangbi":
            return self._buoctrangbi(s, nv)
        is_trachuaxong = s.pop("trachuaxong", False)
        if nv["loai"] == "truysat":
            if nv["khoa"] in s["dagiet"] and is_trachuaxong:
                self._logdv(f"Tề Tổng Quản bảo chưa xong ({nv['doithu']} còn sống): quay lại truy")
                s["dagiet"].discard(nv["khoa"])
                s.get("dadanh", set()).discard(nv["khoa"])
                s["thu"].pop(f"{s['soluotxong']}|{nv['khoa']}|trả nhiệm vụ", None)
                if s.get("truyna"):
                    s["truyna"]["khongmenu"] = 0
            if nv["khoa"] in s["dagiet"]:
                return self._tradanhvong(s, nv, khiloi = lambda: self._trasaitruysat(s, nv))
            return self._buoctruysat(s, nv)
        if nv["loai"] == "thamhoi":
            if not nv["npc"]:
                self._ketthucdanhvong(f"không đọc được NPC cần thăm hỏi: {nv['ten']} – {nv['mota'][:120]}")
                return None
            return self._noichuyendv(s, nv, nv["npc"], ["look", "chon1", "chon1"], f"thăm hỏi {nv['npc']}", nv["bando"])
        self._ketthucdanhvong(f"chưa biết làm nhiệm vụ này: {nv['ten']} – {nv['mota'][:150]}")
        return None

    def _tradanhvong(self, s, nv, khiloi = None):
        # Về Tề Tổng Quản: "1. Nhiệm vụ Danh vọng" -> lựa chọn có task_info (không có thì lựa chọn đầu)
        s["trangthai"] = f"trả {nv['ten']} ở Tề Tổng Quản"
        return self._noichuyendv(s, nv, TETONGQUAN, ["look", "chon1", "hoanthanh"], "trả nhiệm vụ", BANDO_TEQUOC, khiloi = khiloi)

    # --- Hội thoại NPC -----------------------------------------------------------------------------------------------------------
    def _noichuyendv(self, s, nv, tennpc, buocs, viec, idbandogoiy = None, is_chibandogoiy = False, khiloi = None):
        # Tới gần NPC rồi nói chuyện theo các bước (_xulyhoithoaidv). Mỗi việc thử tối đa SOLANTHUDANHVONG lần, mỗi lần chờ nhiệm vụ đổi;
        # quá số lần thì gọi khiloi (Truy Sát: trả không được thì đi giết lại) hoặc dừng. -> yêu cầu di chuyển hoặc None
        moitruong = self.moitruong
        diachi, yeucau = self._tinpc(s, tennpc, idbandogoiy, is_chibandogoiy)
        if not diachi:
            # Yêu cầu None có thể chỉ là đang chờ (dùng phù, vừa chuyển bản đồ): chỉ dừng khi thật sự không tra được vị trí NPC
            if yeucau is None and not idbandogoiy and not self._sovitri.timnpc(tennpc, self._thumucgame()):
                self._ketthucdanhvong(f"không biết {tennpc} ở đâu ({viec}): đứng gần NPC đó 1 lần cho bot ghi lại vị trí")
            return yeucau
        khoangcach = moitruong.get_khoangcach(diachi)
        if khoangcach > KHOANGCACHNOICHUYEN:
            gan = s.get("gannpc")
            if not gan or gan[0] != tennpc or khoangcach < gan[1] - 0.5:
                gan = s["gannpc"] = (tennpc, khoangcach, time.time())
            if khoangcach > KHOANGCACHNOICHUYENKET or time.time() - gan[2] < THOIGIANKHONGNHICH:
                x, y = moitruong.get_toado(diachi)
                return self._dentoi(s, moitruong.get_idbandohientai(), x, y, tennpc)
        khoa = f"{s['soluotxong']}|{nv['khoa'] if nv else ''}|{viec}"
        solan, luc = s["thu"].get(khoa, (0, 0.))
        if time.time() - luc < (THOIGIANCHODOI if nv else THOIGIANCHONHAN):
            s["trangthai"] = f"chờ {tennpc} ({viec})"
            return None
        if solan >= SOLANTHUDANHVONG:
            if khiloi:
                self._logdv(f"{viec} ở {tennpc} {solan} lần mà nhiệm vụ không đổi, làm lại bước trước")
                s["thu"].pop(khoa, None)
                khiloi()
                return None
            self._ketthucdanhvong(f"{viec} ở {tennpc} {solan} lần mà nhiệm vụ không đổi ({motadanhvong(nv)})"
                                  + (" – hết lượt trong ngày?" if not nv else ""))
            return None
        moitruong.action_ngatdichuyen()
        idnpc = moitruong.get_iddoituong(diachi)
        s["thu"][khoa] = (solan + 1, time.time() + 10.)
        s["hoithoai"] = {"manpc": f"{idnpc:x}#", "buocs": list(buocs), "luc": 0., "khoa": khoa}
        s["trangthai"] = f"{viec} ở {tennpc} (lần {solan + 1})"
        self._logdv(f"{viec} ở {tennpc} (lần {solan + 1}): {[b if not b.startswith('give:') else 'give' for b in buocs]}")
        return None

    def _xulyhoithoaidv(self, s):
        # Mỗi lượt gửi tối đa 1 bước: "look" mở menu gốc, "chon1" lựa chọn đầu (trừ CLOSE), "hoanthanh" lựa chọn có task_info (không có thì
        # lựa chọn đầu), "give:<lệnh>" gửi nguyên lệnh. Ghi lời NPC + các lệnh trong menu để xem log biết menu thật
        h = s["hoithoai"]
        moitruong = self.moitruong
        now = time.time()
        if now - h["luc"] < GIANCACHBUOCHOITHOAI:
            return
        if not h["buocs"]:
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            s["thu"][h["khoa"]] = (s["thu"][h["khoa"]][0], now)
            s["hoithoai"] = None
            return
        buoc = h["buocs"][0]
        if buoc == "look":
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {h['manpc']}")
        elif buoc in ("chon1", "hoanthanh"):
            noidung = moitruong.get_noidungcuasotuychon()
            if not noidung and now - h["luc"] < THOIGIANCHOMENU:
                return
            lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"] if noidung else []
            lenh = (next((l for l in lenhs if l.split("# ", 1)[-1].strip() == "task_info"), None) if buoc == "hoanthanh" else None) \
                or (lenhs[0] if lenhs else None)
            self._logdv(f"Menu {h['manpc']}: {(noidung or '')[:100]!r} {lenhs} -> {lenh or 'không có lựa chọn'}")
            if lenh:
                moitruong.xoa_noidungcuasotuychon()
                moitruong.action_thucthicaulenh(lenh)
            else:
                h["buocs"] = [buoc]
                if buoc == "hoanthanh" and noidung:
                    # Chưa xong thì Tề Tổng Quản hỏi "Mọi chuyện thế nào rồi? Tên ... đang ẩn nấu ở Tề Quốc..." và không có lựa chọn
                    # nào: báo cho vòng chính quay lại làm tiếp ngay, không thử trả thêm
                    s["trachuaxong"] = True
        elif buoc.startswith("give:"):
            moitruong.action_thucthicaulenh(buoc[5:])
        h["buocs"].pop(0)
        h["luc"] = now

    # --- Trang Bị Quân Đội ---------------------------------------------------------------------------------------------------------
    def _docapmon(self, s, vitri, iddoituong, ten):
        # Cấp ("Cấp độ sử dụng: cấp N") của món ở ô vitri: đọc mô tả game đã nạp, chưa có thì desc (cách nhau GIANCACHDESC giây).
        # -> cấp, hoặc None khi đang chờ mô tả
        if iddoituong in s["capmon"]:
            return s["capmon"][iddoituong]
        moitruong = self.moitruong
        mota = unicodedata.normalize("NFC", moitruong.get_motavatphamhanhtrangcosan(vitri) or "")
        dongs = [d.strip() for d in mota.split("\n") if d.strip()]
        # Mô tả giữ theo ô: dòng tên phải khớp tên món (tên ô tối đa 31 byte nên chỉ so đầu), không thì mô tả cũ của món khác
        if dongs and chuanhoaten(dongs[0]).startswith(chuanhoaten(ten)):
            khop = re.search(r"Cấp độ sử dụng\s*[:：]\s*cấp\s*(\d+)", mota, re.IGNORECASE)
            cap = int(khop.group(1)) if khop else 0
            s["capmon"][iddoituong] = cap
            _ghicapvukhi(ten, cap)
            self._logdv(f"{ten}: cấp {cap or '? (mô tả không ghi)'}")
            return cap
        if time.time() - s["lucdesc"] > GIANCACHDESC:
            s["lucdesc"] = time.time()
            moitruong.truyvan_motavatphamhanhtrang(vitri)
        return None

    def _docaphangcuahang(self, s, diachi, o, ten):
        # Cấp món ở ô o cửa hàng của NPC diachi: đọc mô tả game đã nạp (dòng tên phải khớp), chưa có thì "desc <id NPC># <ô>" (cách nhau
        # GIANCACHDESC giây), SOLANDESCCUAHANG lần không có thì thôi (mua thử như cũ). -> cấp (đã ghi vào capvukhi.json), 0 khi không đọc
        # được, None khi đang chờ mô tả
        moitruong = self.moitruong
        mota = unicodedata.normalize("NFC", moitruong.get_motahangcuahang(o) or "")
        dongs = [d.strip() for d in mota.split("\n") if d.strip()]
        if dongs and chuanhoaten(dongs[0]).startswith(chuanhoaten(ten)):
            khop = re.search(r"Cấp độ sử dụng\s*[:：]\s*cấp\s*(\d+)", mota, re.IGNORECASE)
            cap = int(khop.group(1)) if khop else 0
            _ghicapvukhi(ten, cap)
            self._logdv(f"{ten} (ô {o} cửa hàng): cấp {cap or '? (mô tả không ghi)'}")
            return cap
        khoa = f"{ten}|desccuahang"
        solan = s["thu"].get(khoa, (0, 0.))[0]
        if solan >= SOLANDESCCUAHANG:
            return 0
        if time.time() - s["lucdesc"] > GIANCACHDESC:
            s["lucdesc"] = time.time()
            s["thu"][khoa] = (solan + 1, time.time())
            moitruong.action_thucthicaulenh(f"desc {moitruong.get_iddoituong(diachi):x}# {o}")
        return None

    def _chonovukhi(self, hang, cap):
        # Ô cửa hàng bán vũ khí đúng cấp: món đã biết cấp đúng thì lấy; chưa thì đoán theo món đã biết cấp gần nhất (mỗi ô hơn 10 cấp),
        # không biết món nào thì ô thứ cap / 10. Đoán ra món đã biết sai cấp -> None. -> (ô, giá, tên) hoặc None
        if not hang:
            return None
        capbiet = _laycapvukhi()
        biets = [(i, capbiet[chuanhoaten(t)]) for i, (o, g, t) in enumerate(hang) if capbiet.get(chuanhoaten(t))]
        dung = next((i for i, c in biets if c == cap), None)
        if dung is not None:
            return tuple(hang[dung])
        # Giá theo cấp, mọi dòng vũ khí như nhau (đọc bộ nhớ 4 cửa hàng 2026-10-31: Chu Thương / Côn, Thục Sơn Đao / Kiếm, Triệu Đào Hoa:
        # 3000 cấp 20, 7000 cấp 30, rồi mỗi 10 cấp +5000 => 32000 cấp 80, 37000 cấp 90). Không phụ thuộc nước bắt đầu ô 1 từ cấp mấy
        giadung = 7000 + 5000 * (cap // 10 - 3) if cap >= 30 else 3000
        theogia = next((i for i, (o, g, t) in enumerate(hang) if g == giadung and not capbiet.get(chuanhoaten(t))), None)
        if theogia is not None:
            return tuple(hang[theogia])
        if biets:
            i, c = min(biets, key = lambda b: abs(b[1] - cap))
            d = round((cap - c) / 10) or (1 if cap > c else -1)
            k = i + d
        else:
            # Theo số ô (đa số nước ô N = cấp N x 10), không theo thứ tự trong danh sách: Triệu Quốc không có ô 1 nên món thứ 8 là ô 9
            # (cấp 90). Nước bắt đầu từ cấp 20 (Chu Quốc) vẫn có thể sai 1 lần, học xong ghi file
            k = next((i for i, (o, g, t) in enumerate(hang) if o == cap // 10), cap // 10 - 1)
        k = max(0, min(len(hang) - 1, k))
        if capbiet.get(chuanhoaten(hang[k][2])):
            return None
        return tuple(hang[k])

    def _buoctrangbi(self, s, nv):
        moitruong = self.moitruong
        if not nv["phai"]:
            self._ketthucdanhvong(f"không nhận ra môn phái \"{nv['tenphai']}\" trong nhiệm vụ")
            return None
        idbando = BANDOVUKHIMONPHAI[nv["phai"]]
        hang = self._sovitri.layhang(idbando, CHUTIEMVUKHI)
        nhan = f"vũ khí {nv['tenphai']} cấp {nv['cap']}"
        # Món trong túi thuộc hàng Chủ Tiệm Vũ Khí nước đó, đúng cấp
        tenhangs = {chuanhoaten(t) for _, _, t in hang}
        dung, dangdoc = None, False
        for ten, mons in moitruong.get_danhsachvatphamhanhtrang_map().items():
            if not ten or not any(t == chuanhoaten(ten) or t.startswith(chuanhoaten(ten)) for t in tenhangs):
                continue
            for vitri, iddoituong in mons:
                # Chỉ đồ trong túi, không lấy đồ đang mặc
                if not iddoituong or vitri >= VITRITRANGBIDAUTIEN:
                    continue
                cap = self._docapmon(s, vitri, iddoituong, ten)
                if cap is None:
                    dangdoc = True
                elif cap == nv["cap"] and (not dung or dung[0] >= 24 > vitri):
                    dung = (vitri, iddoituong, ten)
        if dung:
            return self._giaovukhi(s, nv, *dung)
        if dangdoc:
            s["trangthai"] = f"{nhan}: đọc cấp đồ trong túi"
            return None
        # Chưa có: tới Chủ Tiệm Vũ Khí nước đó mua
        diachi, yeucau = self._toicuahangdv(s, CHUTIEMVUKHI, idbando, nhan)
        if not diachi:
            return yeucau
        if not hang:
            return self._mocuahangdv(s, nv, diachi, CHUTIEMVUKHI)
        chon = self._chonovukhi(hang, nv["cap"])
        if not chon:
            self._ketthucdanhvong(f"không đoán được ô {nhan} ở {CHUTIEMVUKHI} {laytenbando(idbando)} (cấp đã biết: "
                                  f"{', '.join(f'{t} {_laycapvukhi()[chuanhoaten(t)]}' for _, _, t in hang if chuanhoaten(t) in _laycapvukhi())})")
            return None
        o, gia, ten = chon
        # Desc món trong cửa hàng xem đúng cấp chưa rồi mới mua (khỏi mua nhầm rồi mới biết); sai thì học cấp, lượt sau chọn món khác
        cap = self._docaphangcuahang(s, diachi, o, ten)
        if cap is None:
            s["trangthai"] = f"{nhan}: đọc mô tả {ten} (ô {o}) trong cửa hàng"
            return None
        if cap and cap != nv["cap"]:
            return None
        solanmua = s["solanmua"].get(nv["khoa"], 0)
        if solanmua >= SOLANMUAVUKHITOIDA:
            self._ketthucdanhvong(f"đã mua {solanmua} món mà chưa ra {nhan}")
            return None
        if not self._muadv(s, nv, diachi, o, gia, ten, 1, f"{nhan}: mua {ten} (ô {o}, đoán đúng cấp)"):
            return None
        s["solanmua"][nv["khoa"]] = solanmua + 1
        return None

    def _giaovukhi(self, s, nv, vitri, iddoituong, ten):
        # Đồ giao NPC phải ở hành trang 1 (24 ô đầu): chuyển lên rồi give Tề Tổng Quản
        moitruong = self.moitruong
        if vitri >= 24:
            if time.time() - s.get("lucchuyentui", 0.) > 3.:
                s["lucchuyentui"] = time.time()
                self._logdv(f"Chuyển {ten} lên hành trang 1 để giao")
                moitruong.action_thucthicaulenh(f"move {iddoituong:x}# to 1")
            s["trangthai"] = f"chuyển {ten} lên hành trang 1"
            return None
        diachi = self._timdoituongxungquanh(TETONGQUAN)
        manpc = f"{moitruong.get_iddoituong(diachi):x}#" if diachi else ""
        lenhgive = taolenhgiao(manpc, [(iddoituong, 1)], 0)[0]
        s["trangthai"] = f"giao {ten} cho Tề Tổng Quản"
        return self._noichuyendv(s, nv, TETONGQUAN, [f"give:{lenhgive}"], f"giao {ten}", BANDO_TEQUOC)

    # --- Cửa hàng ------------------------------------------------------------------------------------------------------------------
    def _toicuahangdv(self, s, loaicuahang, idbando, nhan):
        # -> (địa chỉ NPC cửa hàng khi đã đứng cạnh, None) hoặc (None, yêu cầu di chuyển)
        moitruong = self.moitruong
        s["trangthai"] = f"{nhan}: tới {loaicuahang} ({laytenbando(idbando)})"
        diachi = self._timdoituongxungquanh(loaicuahang) if moitruong.get_idbandohientai() == idbando else None
        if not diachi:
            return None, self._tinpc(s, loaicuahang, idbando, is_chibandogoiy = True)[1]
        if moitruong.get_khoangcach(diachi) > KHOANGCACHNOICHUYEN:
            x, y = moitruong.get_toado(diachi)
            return None, self._dentoi(s, idbando, x, y, loaicuahang)
        return diachi, None

    def _mocuahangdv(self, s, nv, diachi, loaicuahang):
        # Chưa biết hàng: mở cửa hàng đọc 1 lần (batdau_mocuahang của sư môn), tối đa SOLANTHUDANHVONG lần
        khoa = f"{nv['khoa'] if nv else ''}|{loaicuahang}|mocuahang"
        solan = s["thu"].get(khoa, (0, 0.))[0]
        if solan >= SOLANTHUDANHVONG:
            self._ketthucdanhvong(f"mở cửa hàng {loaicuahang} {solan} lần không được (xem menu trong log [CỬA HÀNG])")
            return None
        s["thu"][khoa] = (solan + 1, time.time())
        s["trangthai"] = f"đọc hàng của {loaicuahang}"
        self.batdau_mocuahang(diachi)
        return None

    def _muadv(self, s, nv, diachi, o, gia, ten, soluong, nhan):
        # Mua bằng lệnh buy, chờ THOIGIANCHODOI giây cho túi đổi rồi mới mua lại; quá SOLANTHUDANHVONG lần thì dừng. -> True khi vừa gửi lệnh
        moitruong = self.moitruong
        khoa = f"{nv['khoa'] if nv else ''}|{ten}|mua"
        solan, luc = s["thu"].get(khoa, (0, 0.))
        if time.time() - luc < THOIGIANCHODOI:
            s["trangthai"] = f"chờ mua {ten}"
            return False
        if solan >= SOLANTHUDANHVONG:
            self._ketthucdanhvong(f"mua {ten} (ô {o}, giá {gia}) {solan} lần không được")
            return False
        moitruong.action_ngatdichuyen()
        nganquy = (moitruong.get_nganluong() or 0) - NGANLUONGGIULAI
        if not self._muavatpham(moitruong.get_iddoituong(diachi), o, soluong, gia, ten, nganquy):
            self._ketthucdanhvong(f"không đủ ngân lượng mua {ten} ({gia} lượng, chừa {NGANLUONGGIULAI})")
            return False
        s["thu"][khoa] = (solan + 1, time.time())
        s["trangthai"] = nhan
        self._logdv(f"{nhan}: buy ô {o}, {soluong} món, giá {gia}")
        return True

    def _muacongvandv(self, s, nv):
        # Mua ở Chủ Tiệm Tạp Hóa Tề Quốc (gần Tề Tổng Quản, người dùng xác nhận có bán); đọc hàng rồi mà không có thì về Tân Thủ Thôn
        loaicuahang = CHUTIEMTAPHOA
        idbando = BANDO_TEQUOC
        if self._sovitri.layhang(idbando, loaicuahang) and not self._sovitri.timhang(idbando, loaicuahang, CONGVANTRUYNA):
            idbando = BANDO_TANTHUTHON
        diachi, yeucau = self._toicuahangdv(s, loaicuahang, idbando, f"mua {CONGVANTRUYNA}")
        if not diachi:
            return yeucau
        tra = self._sovitri.timhang(idbando, loaicuahang, CONGVANTRUYNA)
        if not tra:
            return self._mocuahangdv(s, nv, diachi, loaicuahang)
        self._muadv(s, nv, diachi, tra[0], tra[1], CONGVANTRUYNA, SOLUONGMUACONGVANTRUYNA, f"mua {CONGVANTRUYNA}")
        return None

    # --- Truy Sát Kẻ Phản Bội ------------------------------------------------------------------------------------------------------
    def _buoctruysat(self, s, nv):
        moitruong = self.moitruong
        idbando = BANDO_TEQUOC
        nhan = f"truy sát {nv['doithu'] or 'kẻ phản bội'}"
        # Hết Công Văn Truy Nã thì về Tân Thủ Thôn mua trước, kể cả khi đang đứng ở Tề Quốc (nhận nhiệm vụ xong là ở đây sẵn; trước đây chỉ
        # mua khi ở ngoài Tề Quốc nên đứng đó là đi dò khắp bản đồ luôn). Đang đánh / vừa thấy đối thủ thì thôi
        dt = s["doithu"]
        if not self._demvatpham(CONGVANTRUYNA) and not (dt and dt["khoa"] == nv["khoa"] and time.time() - dt["luc"] < 30.):
            return self._muacongvandv(s, nv)
        if moitruong.get_idbandohientai() != idbando:
            return self._dentoi(s, idbando, None, None, nhan)
        s["chedo"] = "danhquai"
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            self._doituychondv(s, thuoctinh, giatri, ten)
        # Kẻ phản bội mang ID mình ("Quan Đào Tấu ( 29 )"), con mang ID người khác bỏ qua
        # (danh sách tên rỗng là đánh mọi quái: luôn giữ tên trong nhiệm vụ)
        tens, gannhat = self._layquairieng(nv["doithus"])
        s["tenquai"] = tens | set(nv["doithus"] or ["Kẻ Phản Bội"])
        s["trangthai"] = nhan
        now = time.time()
        dt = s["doithu"]
        if gannhat and moitruong.get_is_nhanvatdachet(gannhat):
            return self._dagietdv(s, nv, "thấy kẻ phản bội đã chết")
        if gannhat:
            if s.get("truyna"):
                s["truyna"]["solanloi"] = 0
            s["doithu"] = {"khoa": nv["khoa"], "luc": now, "mau": moitruong.get_phantramsinhlucconlai(gannhat),
                           "kc": moitruong.get_khoangcach(gannhat)}
            # Đã tới sát đánh con này (giết xong tên nhiệm vụ không đổi, không có "(Xong)": tự nhận biết theo Công Văn ở dưới)
            if s["doithu"]["kc"] <= KHOANGCACHMATDOITHU:
                s.setdefault("dadanh", set()).add(nv["khoa"])
            x, y = moitruong.get_toado(gannhat)
            return self._dentoi(s, idbando, x, y, f"{nhan}: đánh {moitruong.get_tendoituong(gannhat)}",
                                khoangcach = self._khoangcachsudungkynangtamxa, is_dioo = self._is_dioo(idbando))
        if dt and dt["khoa"] == nv["khoa"] and now - dt["luc"] < THOIGIANMATDOITHU \
                and (100 if dt["mau"] is None else dt["mau"]) <= MAUMATDOITHU and dt["kc"] <= KHOANGCACHMATDOITHU:
            return self._dagietdv(s, nv, f"kẻ phản bội mất khỏi tầm nhìn lúc còn {dt['mau']}% máu")
        if dt and dt["khoa"] == nv["khoa"] and now - dt["luc"] < THOIGIANMATDOITHU:
            # Vừa còn thấy (khuất chốc lát / đang ra chiêu): đứng đánh tiếp, chưa dùng Công Văn
            return None
        s["doithu"] = None
        if self._is_dagietquacongvan(s, nv):
            return None
        is_dangtruyna, yeucau = self._buoctruyna(s, {"luot": nv["khoa"]}, idbando, nhan)
        if is_dangtruyna:
            return yeucau
        # Hết công văn / dùng mãi không ra: dò khắp Tề Quốc
        diems = list(DIEMNGOAITHANH_MAP.get(idbando) or self._taodiemdo(idbando) or laydiemluoi(idbando))
        return self._diquadiem(s, f"truysat|{nv['khoa']}", idbando, diems, nhan)

    def _is_dagietquacongvan(self, s, nv):
        # Giết xong nhiệm vụ không báo gì (tên không thêm "(Xong)"), tự nhận biết qua Công Văn Truy Nã (_buoctruyna của sư môn, trạng thái
        # s["truyna"]); kẻ phản bội đứng yên đúng chỗ chấm vàng:
        #   - menu "Bạn muốn tìm vị trí của ai ?" hiện mà không còn ai (menu chỉ liệt kê con còn sống)
        #   - đã đánh con này rồi mà dùng công văn không ra menu, hoặc tới sát chấm vàng không thấy nó
        # Nhận nhầm thì trả ở Tề Tổng Quản không được, sau SOLANTHUDANHVONG lần quay lại truy tiếp (khiloi). -> True khi coi như đã giết
        moitruong = self.moitruong
        t = s.get("truyna")
        thongbao = unicodedata.normalize("NFC", moitruong.get_noidungthongbaogannhat() or "")
        if not t or t["luot"] != nv["khoa"] or t["buoc"] != "menu":
            # Thông báo giữa màn hình giữ tới lần sau: nhớ cái đang có trước khi dùng công văn để không nhận nhầm thông báo cũ (lưu theo
            # phiên, không theo lượt: lượt mới dùng công văn ngay lần đầu thì vẫn có bản nhớ; trước đây thông báo "Không tìm thấy" của lượt
            # trước bị tưởng là mới, vừa nhận đã đi trả)
            s["thongbaotruoc"] = thongbao
        if not t or t["luot"] != nv["khoa"]:
            return False
        is_dadanh = nv["khoa"] in s.get("dadanh", ())
        # Vừa nhận nhiệm vụ đối thủ có thể chưa xuất hiện (công văn cũng báo "Không tìm thấy... NPC đã xuất hiện chưa"): chưa đủ
        # THOIGIANCHODOITHUXUATHIEN giây từ lúc thấy lượt này thì không kết luận đã chết
        is_dulau = time.time() - s.setdefault("lucthaynv", {}).setdefault(nv["khoa"], time.time()) > THOIGIANCHODOITHUXUATHIEN
        if t["buoc"] == "menu":
            # Con cần giết đã chết thì dùng công văn hiện "Không tìm thấy mục tiêu đang tồn tại. Hãy kiểm tra nhiệm vụ và NPC đã xuất
            # hiện chưa." giữa màn hình (không có menu); xem cả dòng chat phòng khi nó vào khung chat
            is_moi = LOIKHONGCONMUCTIEU in thongbao and LOIKHONGCONMUCTIEU not in s.get("thongbaotruoc", "")
            is_chat = any(luc >= t["luc"] and LOIKHONGCONMUCTIEU in unicodedata.normalize("NFC", nd or "")
                          for luc, nd in moitruong.get_lichsutrochuyen5s())
            if (is_moi or is_chat) and not (is_dulau or is_dadanh):
                if not t.get("dabaochuaxuathien"):
                    t["dabaochuaxuathien"] = True
                    self._logdv("Công Văn báo không tìm thấy mục tiêu nhưng vừa nhận nhiệm vụ: chờ đối thủ xuất hiện rồi dùng lại")
            elif is_moi or is_chat:
                t["buoc"] = None
                self._dagietdv(s, nv, f"Công Văn Truy Nã báo \"{LOIKHONGCONMUCTIEU}\" ({'giữa màn hình' if is_moi else 'khung chat'})")
                return True
            noidung = moitruong.get_noidungcuasotuychon()
            if noidung and time.time() - t["luc"] > GIANCACHBUOCHOITHOAI \
                    and not any("# target." in l for l in moitruong.get_lenhcuasotuychons()):
                self._logdv(f"Menu Công Văn Truy Nã không còn ai: {noidung[:80]!r} {moitruong.get_lenhcuasotuychons()}")
                moitruong.xoa_noidungcuasotuychon()
                if moitruong.get_is_danghiencuasotuychon():
                    moitruong.set_is_danghiencuasotuychon(False)
                t["buoc"] = None
                self._dagietdv(s, nv, "Công Văn Truy Nã không còn tên kẻ phản bội")
                return True
            if noidung:
                t["khongmenu"] = 0
            elif time.time() - t["luc"] > THOIGIANCHOTRUYNA:
                # Đối thủ còn sống thì công văn luôn ra menu: không ra menu (đã đánh rồi, hoặc 2 lần liền kể cả khi chưa thấy nó: bot vừa
                # mở lại thì quên đã đánh) là nó đã chết. Ghi thông báo giữa màn hình / chat lúc đó để xem game báo gì
                t["khongmenu"] = t.get("khongmenu", 0) + 1
                self._logdv(f"Dùng Công Văn {THOIGIANCHOTRUYNA:.0f}s không ra menu (lần {t['khongmenu']}): thông báo {thongbao[:80]!r} "
                            f"(trước khi dùng {s.get('thongbaotruoc', '')[:40]!r}), chat {[nd[:60] for _, nd in moitruong.get_lichsutrochuyen5s()][-3:]}")
                if is_dadanh or (is_dulau and t["khongmenu"] >= 2):
                    t["buoc"] = None
                    self._dagietdv(s, nv, f"dùng Công Văn Truy Nã {t['khongmenu']} lần không ra menu" + (" (đã đánh)" if is_dadanh else ""))
                    return True
        if is_dadanh and t["dich"] and moitruong.get_khoangcachdiem(*t["dich"][1:]) <= KHOANGCACHTOICHAMTRUYNA:
            self._dagietdv(s, nv, f"đã đánh, tới chấm vàng {tuple(t['dich'][1:])} không còn thấy")
            t["dich"] = None
            return True
        return False

    def _trasaitruysat(self, s, nv):
        # Tưởng đã giết mà trả không được: quay lại truy (bỏ dấu đã đánh để không nhận ngay là đã giết); lần thứ 2 thì dừng báo (giết thật
        # rồi mà trả không được thì là menu trả sai, xem log)
        s["dagiet"].discard(nv["khoa"])
        s.get("dadanh", set()).discard(nv["khoa"])
        s.setdefault("solantrasai", {})[nv["khoa"]] = solan = s.get("solantrasai", {}).get(nv["khoa"], 0) + 1
        if solan >= 2:
            self._ketthucdanhvong(f"tưởng đã giết {nv['doithu']} nhưng trả ở Tề Tổng Quản {solan} lần không được (xem menu trong log)")

    def _dagietdv(self, s, nv, lydo):
        s["dagiet"].add(nv["khoa"])
        s["doithu"] = None
        s["chedo"], s["tenquai"] = "dichuyen", set()
        self._logdv(f"Đã giết kẻ phản bội ({lydo}), về Tề Tổng Quản trả")
        return None
