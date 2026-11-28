# Nhiệm vụ Thiên Xu Viện (nhiệm vụ bang phái, mục "Nhiệm Vụ Bang Phái" trong cửa sổ nhiệm vụ, nhóm "quest intro 1 103 <loại>").
# Bật tay / hàng việc, chạy tới khi đủ lượt trong ngày (cửa sổ ghi "Số lượt hiện tại: N/10") / Tổng Quản không giao nữa / bấm dừng.
# Nhận ở "<Tên bang> Tổng Quản" trên bản đồ bang (bang Nghề: Nghề Tổng Quản, bản đồ 886 (79, 141), log 2026-11-15):
#   look -> "5. Lãnh nhiệm vụ Thiên Xu Viện" (talk <id># quest.10) -> "1. Nhận" (talk <id># quest.11)
# Tới bản đồ bang bằng Hồi Bang Phù: Aegis "dGludmF0 3" (Hồi Môn Phái 1, Hồi Thành 2; người dùng dặn), Niết Bàn dùng phù trong túi.
# Các loại (người dùng 2026-11-15, chưa đủ, phát sinh thì bổ sung):
#   Cứu Nguy Giải Nạn (loại 1): "Đem thuốc trị thương tới Người Đưa Tin <Bang>" ... "Người Đưa Tin <Bang> tại <Nước> (x, y)"
#                               -> tới toạ độ, NPC tên game "<Bang> Người Đưa Tin" -> look -> "1. Hoàn thành nhiệm vụ"
#   Gửi Thư Nhà (loại 4?)     : "Gửi thư nhà cho <NPC>" ... "người ấy sống tại <Nước>, ở ..." -> tới NPC -> look -> lựa chọn hoàn thành
#                               (Vương Thợ Rèn ghi "Không biết tên chỗ", không có trong dữ liệu game: huỷ, NPCHUYGUITHU; người khác
#                               không rõ chỗ cũng huỷ luôn cho khỏi đứt chuỗi - người dùng dặn 2026-11-22, trước đó dừng báo lỗi)
#   Thu Thập (Cơm No Áo Ấm)   : "Thu thập 1 cái Súp Bắp" -> hành trang có đủ thì về Tổng Quản trả (quest.20 -> quest.21);
#                               không đủ: VATPHAMHUYTHUTHAP huỷ, món khác dừng báo lỗi để người dùng xem
#   Trừ Ác Giúp Yếu           : "Diệt trừ <Ác Nhân ...>" ... "xuất hiện tại <Nước> (x, y)" -> tới toạ độ, chỉ đánh con đó tới chết,
#                               về Tổng Quản trả (nhiệm vụ chưa "(Xong)" cũng về trả). Vd Ác Nhân Phương Tiểu Tam Tần (193, 31),
#                               Ác Nhân Trữ Tiểu Ngũ Nguỵ (240, 229)
#   Bảo Vật Di Thất (loại 3)  : "Truy Tìm Bảo Vật", "báu vật ... thất lạc tại <Nước> (x, y)" -> tới toạ độ, look NPC "<Bang> Bảo Rương",
#                               vận khí một lúc là túi có món "Truy Tìm Bảo Vật" -> về Tổng Quản trả.
#                               Không thấy rương thì ghi log đối tượng quanh đó, look NPC lạ, nhặt đồ đất
# Trả ở Tổng Quản: look -> "5. Hoàn thành nhiệm vụ Thiên Xu Viện" (quest.20) -> "1. Hoàn thành nhiệm vụ" (quest.21). Cứu Nguy / Gửi Thư
# xong ngay ở NPC (nhiệm vụ biến mất). Vừa huỷ thì phải chờ ~3 phút mới nhận lại (LOICHONHANLAI).
# Dùng chung đi đường / tìm NPC của sư môn (tactu_sumon_xq: _tinpc, _dentoi, _diquadiem, _laydiemdoquanh) nên self._thienxu có đủ
# khoá chúng cần (khampha, dabao, trangthai, lucmonphai, solanmonphai).
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import re
import time
import unicodedata

from hangso_xq import *
from nhiemvu_xq import chuanhoaten, boma, timbandotheoten, is_nhiemvuthatbai
from thongbao_xq import baosuco
from tienich_xq import phatam, canhbao

MUCTHIENXU = "Nhiệm Vụ Bang Phái"
NGUOIDUATIN = "Người Đưa Tin"
# Hồi Bang Phù (Aegis): như Hồi Thành Phù "dGludmF0 2", Hồi Môn Phái "dGludmF0 1"
LENHHOIBANGPHU = "dGludmF0 3"
# Lệnh menu Tổng Quản (log 5 acc 2026-11-15): "5. Lãnh nhiệm vụ Thiên Xu Viện" rồi "1. Nhận"
LENHLANHTHIENXU = "quest.10"
LENHNHANTHIENXU = "quest.11"
# Trả (Thu Thập, Bảo Vật; người dùng + log acc 342 2026-11-15): đang có nhiệm vụ thì lựa chọn 5 thành "5. Hoàn thành nhiệm vụ Thiên Xu
# Viện" (quest.20) rồi "1. Hoàn thành nhiệm vụ" (quest.21)
LENHTRATHIENXU = "quest.20"
LENHHOANTHANHTHIENXU = "quest.21"
# Vừa huỷ nhiệm vụ mà nhận lại ngay thì Tổng Quản bảo "Làm việc phải cẩn thận, đừng nóng vội!..." (chỉ có "Rời khỏi"): chờ chừng này giây
# rồi nhận lại (người dùng đoán ~3 phút), không tính là lần nhận hỏng
LOICHONHANLAI = "đừng nóng vội"
THOIGIANCHONHANLAI = 180.
SOLUOTTHIENXUMOINGAY = 10
# Hồi Bang Phù: dùng xong chờ chừng này giây cho chuyển bản đồ, quá SOLANHOIBANG lần không về được bang thì dừng
GIANCACHHOIBANG = 15.
# Bắt đầu mà chưa biết tên bang: chờ trả lời "desc user" chừng này giây rồi mới Hồi Bang Phù
THOIGIANCHOTENBANG = 6.
SOLANHOIBANG = 3
# Hội thoại: mỗi việc thử tối đa SOLANTHUTHIENXU lần, gửi xong chờ nhiệm vụ đổi
SOLANTHUTHIENXU = 3
THOIGIANCHODOI = 4.
THOIGIANCHONHAN = 12.
GIANCACHBUOCHOITHOAI = 0.8
THOIGIANCHOMENU = 2.
KHOANGCACHNOICHUYEN = KHOANGCACHNOICHUYENNPC
KHOANGCACHNOICHUYENKET = 8.
THOIGIANKHONGNHICH = 10.
GIANCACHXINNHIEMVU = 10.
THOIGIANCHOMOTANHIEMVU = 30.
# Tới toạ độ Người Đưa Tin mà chưa thấy: đứng chờ chừng này giây rồi mới đi dò quanh
THOIGIANCHONGUOIDUATIN = 8.
KHOANGCACHTOITOADO = 4.
THOIGIANTHIENXUTOIDA = 3 * 3600.
# Trừ Ác Giúp Yếu: ác nhân khuất tầm nhìn chưa tới chừng này giây sau lần thấy cuối, lúc đó dưới chừng này % máu và ở gần: coi như đã chết
THOIGIANMATACNHAN = 5.
MAUMATACNHAN = 25
KHOANGCACHMATACNHAN = 10.
# Thấy ác nhân mà chừng này giây chưa thành mục tiêu đang chọn thì tự gán
THOIGIANTUGANMUCTIEU = 3.
# Người dùng dặn huỷ luôn (2026-11-15), loại khác cùng nhóm thì dừng báo lỗi để người dùng xem: Thu Thập các món này, Gửi Thư Nhà cho
# các NPC này
VATPHAMHUYTHUTHAP = ("Súp Bắp", "Bột Bắp Hấp")
NPCHUYGUITHU = ("Vương Thợ Rèn",)
# Bảo Vật Di Thất: đối tượng cách toạ độ trong nhiệm vụ tối đa chừng này ô mới xét; đứng ở toạ độ chừng này giây không ra thì dò quanh,
# dò hết 1 vòng (hoặc quá THOIGIANTIMBAOVAT giây) mà nhiệm vụ không đổi thì dừng báo
BANKINHBAOVAT = 10.
# Báu vật là NPC "<Tên bang> Bảo Rương" đứng đúng toạ độ trong nhiệm vụ (Nghề Bảo Rương, Nguỵ (116, 142), log 347 2026-11-15)
TENBAORUONG = "Bảo Rương"
# Look rương, vận khí xong thì túi có món này (vật phẩm nhiệm vụ "Truy Tìm Bảo Vật"), nhiệm vụ không tự đổi: về Tổng Quản trả
TENVATPHAMBAOVAT = "Truy Tìm Bảo Vật"
THOIGIANCHOBAOVAT = 6.
THOIGIANTIMBAOVAT = 240.
# NPC cố định hay đứng quanh thành (không phải bảo vật): bỏ qua khi tìm vật để look
TUBOQUABAOVAT = ("Chủ Tiệm", "Tổng Quản", "Người Đưa Tin", "Vệ Binh", "Thủ Vệ", "Xa Phu", "Tiên Cô", "Truyền Tống")


def _tachchu(ten):
    # Chữ màu dính nhau khi bỏ mã màu ("Ác Nhân PhươngTiểu Tam"): chèn dấu cách giữa chữ thường và chữ hoa liền sau
    kq = ""
    for i, c in enumerate(ten or ""):
        if i and c.isupper() and ten[i - 1].islower():
            kq += " "
        kq += c
    return re.sub(r"\s+", " ", kq).strip()


def _timnuoc(tennuoc):
    # Tên nước gọi tắt trong mô tả ("Nguỵ (240,229)", "Tần (193,31)") -> id bản đồ hoặc None; so cả không dấu để dự phòng
    tennuoc = (tennuoc or "").strip()
    if not tennuoc:
        return None
    idbando = timbandotheoten(tennuoc) or timbandotheoten(tennuoc + " Quốc")
    if idbando:
        return idbando
    khongdau = lambda t: "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn").replace("đ", "d")
    return next((b for t, b in (("Tề", BANDO_TEQUOC), ("Hàn", BANDO_HANQUOC), ("Triệu", BANDO_TRIEUQUOC), ("Nguỵ", BANDO_NGUYQUOC),
                                ("Tần", BANDO_TANQUOC), ("Sở", BANDO_SOQUOC), ("Yên", BANDO_YENQUOC), ("Chu", BANDO_CHUQUOC))
                 if khongdau(tennuoc) in (khongdau(t), khongdau(t + " Quốc"))), None)


def _khongcach(ten):
    # So tên bỏ hẳn dấu và dấu cách. Không dùng chuanhoaten: nó dời dấu thanh về cuối TỪNG chữ, mô tả dính "TrữTiểu" (1 chữ) còn tên
    # game "Ác Nhân  Trữ Tiểu Ngũ (cấp 95)" (2 chữ) thì lệch thứ tự dấu, không khớp (log 354 2026-11-15)
    chu = unicodedata.normalize("NFD", (ten or "").lower()).replace("đ", "d")
    return "".join(c for c in chu if not unicodedata.combining(c) and not c.isspace())


def laynhiemvuthienxu(mucs):
    # mucs: [(tên mục, mô tả), ...] của cửa sổ nhiệm vụ -> nhiệm vụ Thiên Xu Viện đang nhận (dict) hoặc None
    is_trongmuc = False
    for ten, mota in mucs:
        if not ten.startswith(" "):
            is_trongmuc = chuanhoaten(ten) == chuanhoaten(MUCTHIENXU)
            continue
        if is_trongmuc:
            return phantichthienxu(ten.strip(), mota)
    return None


def _timbandotrongcau(vanban, tus = ("tại", "ở")):
    # Bản đồ sau "tại" / "ở" (1 chữ riêng): bỏ dần chữ cuối tới khi khớp tên bản đồ ("tại Sở Quốc, ở Bách Việt thôn" -> Sở Quốc)
    for m in re.finditer(r"(?<!\w)(?:%s)\s+([^,.;:!?()]+)" % "|".join(tus), vanban, re.IGNORECASE):
        chu = m.group(1).split()
        for k in range(min(len(chu), 5), 0, -1):
            idbando = timbandotheoten(" ".join(chu[:k])) or (timbandotheoten(" ".join(chu[:k]) + " Quốc") if k == 1 else None)
            if idbando:
                return idbando
    return None


def phantichthienxu(tenmuc, mota):
    # -> {"ten", "is_xong", "luot", "tong", "loai" (cuunguy / guithu / None), "mota", "khoa", ...thông tin theo loại}
    is_xong = bool(re.search(r"\(\s*Xong\s*\)\s*$", tenmuc))
    ten = unicodedata.normalize("NFC", re.sub(r"\(\s*Xong\s*\)\s*$", "", tenmuc).strip())
    vanban = re.sub(r"\s+", " ", unicodedata.normalize("NFC", boma(mota))).strip()
    luot = re.search(r"Số lượt hiện tại\s*[:：]\s*(\d+)\s*/\s*(\d+)", vanban, re.IGNORECASE)
    nv = {"ten": ten, "is_xong": is_xong, "luot": int(luot.group(1)) if luot else 0,
          "tong": int(luot.group(2)) if luot else SOLUOTTHIENXUMOINGAY, "loai": None, "mota": vanban,
          "is_thatbai": not is_xong and is_nhiemvuthatbai(vanban)}
    # "Người Đưa Tin Nghề tại Nguỵ (213, 189)"
    m = re.search(r"Người Đưa Tin\s+(\S+)\s+tại\s+([^()]+?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", vanban, re.IGNORECASE)
    if m or chuanhoaten(ten).startswith(chuanhoaten("Cứu Nguy")):
        tenbang = m.group(1) if m else (re.search(r"Người Đưa Tin\s+(\S+)", vanban) or [None, None])[1]
        tennuoc = m.group(2).strip() if m else ""
        idbando = _timnuoc(tennuoc)
        nv.update(loai = "cuunguy", tenbang = tenbang, bando = idbando, toado = (int(m.group(3)), int(m.group(4))) if m else None)
    elif chuanhoaten(ten).startswith(chuanhoaten("Trừ Ác")) or re.search(r"Diệt trừ\s", vanban, re.IGNORECASE):
        m = re.search(r"Diệt trừ\s+(.+?)\s+Nhiệm vụ miêu tả", vanban, re.IGNORECASE)
        tenquai = _tachchu(m.group(1)) if m else ""
        m = re.search(r"xuất hiện\s+(?:tại|ở)\s+([^()]+?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", vanban, re.IGNORECASE)
        tennuoc = m.group(1).strip() if m else ""
        idbando = _timnuoc(tennuoc)
        nv.update(loai = "truac", tenquai = tenquai, bando = idbando, toado = (int(m.group(2)), int(m.group(3))) if m else None)
    elif chuanhoaten(ten).startswith(chuanhoaten("Bảo Vật")) or re.search(r"Truy Tìm Bảo Vật|báu vật", vanban, re.IGNORECASE):
        m = re.search(r"thất lạc\s+(?:tại|ở)\s+([^()]+?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", vanban, re.IGNORECASE) \
            or re.search(r"(?:tại|ở)\s+([^()]+?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", vanban, re.IGNORECASE)
        nv.update(loai = "baovat", bando = _timnuoc(m.group(1)) if m else None, toado = (int(m.group(2)), int(m.group(3))) if m else None)
    elif re.search(r"Mục đích nhiệm vụ\s*[:：]?\s*Thu thập\s", vanban, re.IGNORECASE) or chuanhoaten(ten) == chuanhoaten("Cơm No Áo Ấm"):
        m = re.search(r"Thu thập\s+(.+?)\s+Nhiệm vụ miêu tả", vanban, re.IGNORECASE)
        vatpham = _tachchu(m.group(1)) if m else ""
        # "1 cái Súp Bắp" -> số lượng 1, tên "Súp Bắp" (không ghi số thì 1)
        m = re.match(r"(\d+)\s*(?:cái|chiếc|bình|phần|viên|miếng|bộ|quyển|cuốn|con|bó|túi|bát|chén|tấm|khối)?\s+(.+)$", vatpham, re.IGNORECASE)
        nv.update(loai = "thuthap", vatpham = vatpham, soluong = int(m.group(1)) if m else 1,
                  tenvatpham = (m.group(2) if m else vatpham).strip(" .,"))
    elif chuanhoaten(ten).startswith(chuanhoaten("Gửi Thư")) or re.search(r"thư nhà cho", vanban, re.IGNORECASE):
        m = re.search(r"thư nhà cho\s+(.+?)\s+Nhiệm vụ miêu tả", vanban, re.IGNORECASE) \
            or re.search(r"người thân\s+(.+?)\s*,", vanban, re.IGNORECASE)
        npc = _tachchu(m.group(1)) if m else ""
        m = re.search(r"sống\s+(?:tại|ở)\s+(.*)", vanban, re.IGNORECASE)
        idbando = _timbandotrongcau("tại " + m.group(1)) if m else None
        nv.update(loai = "guithu", npc = npc, bando = idbando or _timbandotrongcau(vanban))
    nv["khoa"] = f"{nv['luot']}|{ten}|{nv.get('npc') or nv.get('tenquai') or ''}|{nv.get('toado') or ''}"
    return nv


def motathienxu(nv):
    if not nv:
        return "không có nhiệm vụ"
    chu = f"{nv['ten']}{' (Xong)' if nv['is_xong'] else ''} lượt {nv['luot']}/{nv['tong']}"
    if nv["loai"] == "cuunguy":
        chu += f": Người Đưa Tin {nv['tenbang'] or '?'} ở {laytenbando(nv['bando']) if nv['bando'] else '?'} {nv['toado'] or ''}"
    elif nv["loai"] == "guithu":
        chu += f": thư cho {nv['npc'] or '?'} ({laytenbando(nv['bando']) if nv['bando'] else 'chưa rõ bản đồ'})"
    elif nv["loai"] == "thuthap":
        chu += f": thu thập {nv['vatpham'] or '?'}"
    elif nv["loai"] == "baovat":
        chu += f": tìm báu vật ở {laytenbando(nv['bando']) if nv['bando'] else '?'} {nv['toado'] or ''}"
    elif nv["loai"] == "truac":
        chu += f": diệt {nv['tenquai'] or '?'} ở {laytenbando(nv['bando']) if nv['bando'] else '?'} {nv['toado'] or ''}"
    return chu


class TacTuThienXu:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_thienxu(self):
        if self._thienxu:
            return
        self._thienxu = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "thu": {}, "hoithoai": None, "dabao": set(),
                         "khampha": None, "lucmonphai": 0., "solanmonphai": 0, "soluotxong": 0, "khoadangnhan": None,
                         "tenbang": None, "bandobang": None, "solanhoibang": 0, "luchoibang": 0., "bandotruochoibang": None,
                         "tenquai": set(), "doithu": None, "dagiet": set()}
        self._logtx("Bắt đầu làm nhiệm vụ Thiên Xu Viện")
        # Tên bang của mình (Tổng Quản là "<Tên bang> Tổng Quản"): hỏi qua "desc user", trả lời vào get_bangphai
        self.moitruong.action_hoibangphaicuaminh()
        self._doituychontx(self._thienxu, "_is_tudongtheosau", False, "Theo sau")
        phatam("Bắt đầu nhiệm vụ Thiên Xu Viện")

    def huy_thienxu(self):
        if self._thienxu:
            self._ketthucthienxu(thongbao = "Đã dừng nhiệm vụ Thiên Xu Viện (bấm tay)")

    def get_is_dangthienxu(self):
        return bool(self._thienxu)

    def get_is_thienxudichuyen(self):
        # Chỉ đi lại / nói chuyện NPC: không chọn quái dọc đường
        return bool(self._thienxu) and self._thienxu["chedo"] == "dichuyen"

    def get_is_thienxudanhquai(self):
        # Trừ Ác Giúp Yếu: chỉ đánh ác nhân của nhiệm vụ (self._thienxu["tenquai"])
        return bool(self._thienxu) and self._thienxu["chedo"] == "danhquai"

    def get_trangthaithienxu(self):
        if self._thienxu:
            return f"Thiên Xu Viện (phiên này trả {self._thienxu['soluotxong']} lượt): {self._thienxu['trangthai']}"
        return self._ketquathienxu or ""

    def _logtx(self, noidung):
        self.moitruong._inlog(f"[THIÊN XU] {noidung}")

    def _doituychontx(self, s, thuoctinh, giatri, ten):
        # Đổi 1 ô thiết lập, nhớ giá trị cũ (s["tuychoncu"]) để trả lại khi dừng; luuthietlap lưu giá trị cũ này
        if getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self._logtx(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng Thiên Xu Viện thì trả lại)")

    def _ketthucthienxu(self, loi = None, thongbao = None):
        s = self._thienxu
        self._thienxu = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        noidung = thongbao or (f"❌ Thiên Xu Viện dừng: {loi}" if loi else "✅ Xong nhiệm vụ Thiên Xu Viện")
        if s and s["soluotxong"]:
            noidung += f" (phiên này trả {s['soluotxong']} lượt)"
        self._logtx(noidung)
        self._ketquathienxu = f"{time.strftime('%H:%M')} {noidung}"
        self._ghiketthucviec("thienxu", noidung)
        baosuco(self.moitruong, "sumon", noidung, khoa = f"thienxu|{s['batdau']}" if s else None, giancach = 0.)
        canhbao(self.moitruong, "Lỗi nhiệm vụ Thiên Xu Viện") if loi else phatam("Kết thúc nhiệm vụ Thiên Xu Viện")

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulythienxu(self):
        # Gọi thay lộ trình điểm đánh khi đang làm Thiên Xu Viện -> yêu cầu di chuyển hoặc None
        yeucau = self._xulythienxuchinh()
        # Kẹt trong cùng bản đồ: đi theo ô đã đi (dùng chung của Danh Vọng)
        return self._chongketdv(self._thienxu, yeucau) if self._thienxu else yeucau

    def _xulythienxuchinh(self):
        s = self._thienxu
        moitruong = self.moitruong
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logtx(f"Trạng thái: {s['trangthai']}")
        chan = next((ly for ly, co in (("nhân vật chết", moitruong.get_is_nhanvatdachet()), ("đang vận khí", moitruong.get_is_dangvankhi()),
                                       ("đang hội thoại NPC", self.get_is_danghoithoainpc()),
                                       (f"đang về bán (bước {self._trangthaiveban})", self._trangthaiveban != 0)) if co), None)
        if chan:
            if chan != s.get("chan"):
                s["chan"] = chan
                self._logtx(f"Tạm chờ: {chan}")
            return None
        s["chan"] = None
        if time.time() - s["batdau"] > THOIGIANTHIENXUTOIDA:
            self._ketthucthienxu(f"quá {int(THOIGIANTHIENXUTOIDA // 3600)} giờ")
            return None
        self._kiemtrahoibang(s)
        if s["hoithoai"]:
            self._xulyhoithoaitx(s)
            return None

        mucs = moitruong.get_danhsachmucnhiemvu()
        if mucs is None:
            s["trangthai"] = "chưa đọc được nhiệm vụ: mở bảng nhiệm vụ trong game 1 lần"
            if time.time() - s.get("lucxinnhiemvu", 0.) > GIANCACHXINNHIEMVU:
                s["lucxinnhiemvu"] = time.time()
                self._logtx("Chưa đọc được cửa sổ nhiệm vụ: gửi \"quest list\"")
                moitruong.action_thucthicaulenh("quest list")
            return None
        nv = laynhiemvuthienxu(mucs)
        # Có tên mà mô tả còn trống: xin mô tả ("quest intro 1 103 <loại>")
        if nv and not nv["mota"] and not nv["is_xong"]:
            s.setdefault("luctrongmota", time.time())
            ma = moitruong.get_manhiemvu(MUCTHIENXU)
            if ma and time.time() - s.get("lucxinmota", 0.) > GIANCACHXINNHIEMVU:
                s["lucxinmota"] = time.time()
                self._logtx(f"Mô tả {nv['ten']} còn trống: gửi \"quest intro {ma[0]} {ma[1]} {ma[2]}\"")
                moitruong.action_thucthicaulenh(f"quest intro {ma[0]} {ma[1]} {ma[2]}")
            if time.time() - s["luctrongmota"] < THOIGIANCHOMOTANHIEMVU:
                s["trangthai"] = f"chờ mô tả nhiệm vụ {nv['ten']}"
                return None
        else:
            s.pop("luctrongmota", None)
        if nv and nv["is_thatbai"]:
            s["khoadangnhan"] = None
            s["trangthai"] = f"huỷ {nv['ten']} (thất bại / quá thời gian)"
            self.action_huynhiemvuthatbai(s, MUCTHIENXU, nv, self._logtx)
            return None
        if nv and nv["loai"] == "cuunguy" and nv["tenbang"] and not s["tenbang"]:
            s["tenbang"] = nv["tenbang"]
        # Nhiệm vụ đang nhận đổi / mất: đã xong lượt trước
        if s["khoadangnhan"] and (not nv or nv["khoa"] != s["khoadangnhan"]):
            s["soluotxong"] += 1
            self._logtx(f"Đã xong {s['khoadangnhan']}")
            luot, tong = s.get("luottong") or (0, SOLUOTTHIENXUMOINGAY)
            if not nv and luot >= tong:
                self._ketthucthienxu(thongbao = f"✅ Đã đủ {tong} lượt Thiên Xu Viện hôm nay")
                return None
        s["khoadangnhan"] = nv["khoa"] if nv else None
        if nv:
            s["luottong"] = (nv["luot"], nv["tong"])
        motanv = motathienxu(nv)
        if motanv != s.get("motanv"):
            s["motanv"] = motanv
            self._logtx(f"Nhiệm vụ: {motanv}" + (f" | {nv['mota'][:220]!r}" if nv else ""))
        # Trừ Ác tự lo chế độ (_buoctruac): không đặt lại mỗi lượt, kẻo luồng chọn mục tiêu đọc đúng lúc thấy "dichuyen" thì xoá mục tiêu
        if not nv or nv["loai"] != "truac" or nv["khoa"] in s["dagiet"]:
            s["chedo"], s["tenquai"] = "dichuyen", set()
        if not nv and self.get_is_nhuongdoiphoban():
            self._ketthucthienxu(thongbao = "Tạm dừng Thiên Xu Viện (nhường đội)")
            return None

        if not nv:
            conlai = s.get("lucchonhan", 0.) - time.time()
            if conlai > 0:
                s["trangthai"] = f"chờ {int(conlai)}s rồi nhận lại (vừa huỷ nhiệm vụ)"
                return None
            s["trangthai"] = "nhận nhiệm vụ ở Tổng Quản bang"
            return self._toitongquan(s, nv, ["look", f"kw:{LENHLANHTHIENXU}", f"kw:{LENHNHANTHIENXU}"], "nhận nhiệm vụ")
        if nv["is_xong"] or nv["khoa"] in s["dagiet"]:
            s["trangthai"] = f"trả {nv['ten']} ở Tổng Quản bang"
            return self._toitongquan(s, nv, ["look", f"kw:{LENHTRATHIENXU}", f"kw:{LENHHOANTHANHTHIENXU}"], "trả nhiệm vụ")
        if nv["loai"] == "cuunguy":
            return self._buoccuunguy(s, nv)
        # Thu Thập (người dùng dặn 2026-11-15): hành trang có đủ thì về Tổng Quản trả; không đủ thì món VATPHAMHUYTHUTHAP huỷ luôn,
        # món khác dừng báo lỗi. Gửi Thư Nhà cho NPCHUYGUITHU huỷ luôn
        lydohuy = None
        if nv["loai"] == "thuthap":
            co = self._demvatpham(nv["tenvatpham"]) if nv["tenvatpham"] else 0
            if nv["tenvatpham"] and co >= nv["soluong"]:
                if f"cothuthap|{nv['khoa']}" not in s["dabao"]:
                    s["dabao"].add(f"cothuthap|{nv['khoa']}")
                    self._logtx(f"Hành trang có {co} {nv['tenvatpham']} (cần {nv['soluong']}): về Tổng Quản trả")
                s["trangthai"] = f"trả {nv['ten']} ({nv['vatpham']}) ở Tổng Quản bang"
                return self._toitongquan(s, nv, ["look", f"kw:{LENHTRATHIENXU}", f"kw:{LENHHOANTHANHTHIENXU}"], "trả thu thập")
            if not any(chuanhoaten(t) in chuanhoaten(nv["vatpham"]) for t in VATPHAMHUYTHUTHAP):
                self._ketthucthienxu(f"Thu Thập {nv['vatpham'] or '?'} ({nv['ten']}): hành trang có {co}/{nv['soluong']}, "
                                     "kiếm đủ rồi bật lại / huỷ tay")
                return None
            lydohuy = f"Thu Thập {nv['vatpham']} (hành trang có {co}/{nv['soluong']})"
        elif nv["loai"] == "guithu" and any(chuanhoaten(t) == chuanhoaten(nv["npc"]) for t in NPCHUYGUITHU):
            lydohuy = f"Gửi Thư Nhà cho {nv['npc']} (không rõ chỗ)"
        if lydohuy:
            s["khoadangnhan"] = None
            s["trangthai"] = f"huỷ {nv['ten']}: {lydohuy}"
            self.action_huynhiemvuthatbai(s, MUCTHIENXU, nv, lambda chu: self._logtx(f"Huỷ ({lydohuy}): {chu}"))
            return None
        if nv["loai"] == "truac":
            return self._buoctruac(s, nv)
        if nv["loai"] == "baovat":
            return self._buocbaovat(s, nv)
        if nv["loai"] == "guithu":
            if not nv["npc"]:
                self._ketthucthienxu(f"không đọc được NPC nhận thư: {nv['mota'][:150]}")
                return None
            npc = nv["npc"]
            return self._noichuyentx(s, nv, npc, ["look", "hoanthanh"], f"gửi thư {npc}", nv["bando"])
        self._ketthucthienxu(f"chưa biết làm nhiệm vụ này: {nv['ten']} – {nv['mota'][:150]}")
        return None

    # --- Bang: Tổng Quản, Hồi Bang Phù -------------------------------------------------------------------------------------------------
    def _laytenbang(self, s):
        tenbang = self.moitruong.get_bangphai(self.moitruong.get_idnguoichoi())
        if tenbang:
            s["tenbang"] = tenbang
        return s["tenbang"]

    def _toitongquan(self, s, nv, buocs, viec):
        moitruong = self.moitruong
        idbandohientai = moitruong.get_idbandohientai()
        tenbang = self._laytenbang(s)
        ten = f"{tenbang} Tổng Quản" if tenbang else None
        if ten and not s["bandobang"]:
            vitri = self._sovitri.timnpc(ten, self._thumucgame())
            if vitri:
                s["bandobang"] = vitri[0]
        diachi = self._timdoituongxungquanh(ten) if ten else None
        if not diachi and not tenbang and idbandohientai == s["bandobang"]:
            # Chưa biết tên bang mà đã ở bản đồ bang: NPC "<...> Tổng Quản" đứng gần là của bang mình
            for dc in moitruong._get_diachidoituongxungquanhs():
                tendc = moitruong.get_tendoituong(dc) or ""
                if moitruong.get_is_nhanvattontai(dc) and not moitruong.get_is_nguoichoi(dc) and tendc.endswith(" Tổng Quản"):
                    s["tenbang"] = tendc[:-len(" Tổng Quản")].strip()
                    self._logtx(f"Tên bang theo NPC ở bản đồ bang: {s['tenbang']}")
                    return None
        if not diachi and (not s["bandobang"] or idbandohientai != s["bandobang"]):
            # Vừa bắt đầu chưa có trả lời tên bang ("desc user"): chờ chút, kẻo đang đứng ở bản đồ bang vẫn dùng phù (acc 342 2026-11-15)
            if not tenbang and time.time() - s["batdau"] < THOIGIANCHOTENBANG:
                s["trangthai"] = "chờ biết tên bang"
                return None
            return self._hoibang(s)
        if not ten:
            self._ketthucthienxu("chưa biết tên bang (đứng gần <Tên bang> Tổng Quản 1 lần cho Foxia ghi lại)")
            return None
        return self._noichuyentx(s, nv, ten, buocs, viec, s["bandobang"] or idbandohientai, diachi = diachi)

    def _kiemtrahoibang(self, s):
        # Vừa dùng Hồi Bang Phù mà bản đồ đổi: bản đồ mới là bản đồ bang
        truoc = s["bandotruochoibang"]
        if truoc is None:
            return
        idbando = self.moitruong.get_idbandohientai()
        if idbando != truoc and idbando:
            s["bandobang"], s["bandotruochoibang"], s["solanhoibang"] = idbando, None, 0
            self._logtx(f"Đã về bản đồ bang ({laytenbando(idbando)}, {idbando})")
        elif time.time() - s["luchoibang"] > 60.:
            s["bandotruochoibang"] = None

    def _hoibang(self, s):
        moitruong = self.moitruong
        now = time.time()
        s["trangthai"] = "Hồi Bang Phù về bang"
        if now - s["luchoibang"] < GIANCACHHOIBANG or now - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        if s["solanhoibang"] >= SOLANHOIBANG:
            self._ketthucthienxu(f"dùng Hồi Bang Phù {s['solanhoibang']} lần không về được bang (hết phù / chưa vào bang?)")
            return None
        if moitruong.is_nietban:
            idphu = moitruong.action_timkiemvatphamhanhtrang(HOIBANGPHU)
            if not idphu:
                self._ketthucthienxu(f"Niết Bàn: không có {HOIBANGPHU} trong túi để về bang")
                return None
            lenh = f"use {idphu:x}#"
        else:
            lenh = LENHHOIBANGPHU
        if not self.action_thugiuhoithanh(lenh):
            return None
        moitruong.action_ngatdichuyen()
        moitruong.action_khoavankhitrieuhoi((lenh,), ten = "HỒI BANG PHÙ")
        moitruong.action_thucthicaulenh(lenh)
        s["luchoibang"] = now
        s["solanhoibang"] += 1
        s["bandotruochoibang"] = moitruong.get_idbandohientai()
        self.ghi_hanhdong(f"Hồi Bang Phù ('{lenh}') về bang", "[THIÊN XU] nhận / trả ở Tổng Quản bang")
        self._logtx(f"Hồi Bang Phù ('{lenh}') lần {s['solanhoibang']} từ {laytenbando(s['bandotruochoibang'])}")
        return None

    # --- Cứu Nguy Giải Nạn -----------------------------------------------------------------------------------------------------------
    def _timnguoiduatin(self, tenbang):
        # NPC "<Bang> Người Đưa Tin" gần nhất (biết tên bang thì phải đúng bang: bang khác cũng có Người Đưa Tin, vd "MaGiáo Người Đưa Tin")
        moitruong = self.moitruong
        tot, khoangcachtot = None, None
        for dc in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(dc) or moitruong.get_is_nguoichoi(dc):
                continue
            ten = chuanhoaten(moitruong.get_tendoituong(dc) or "")
            if chuanhoaten(NGUOIDUATIN) not in ten or (tenbang and chuanhoaten(tenbang) not in ten):
                continue
            khoangcach = moitruong.get_khoangcach(dc)
            if khoangcachtot is None or khoangcach < khoangcachtot:
                tot, khoangcachtot = dc, khoangcach
        return tot

    def _buoccuunguy(self, s, nv):
        moitruong = self.moitruong
        tenbang = nv["tenbang"] or self._laytenbang(s)
        tennpc = f"{tenbang} {NGUOIDUATIN}" if tenbang else NGUOIDUATIN
        diachi = self._timnguoiduatin(tenbang)
        if diachi:
            return self._noichuyentx(s, nv, tennpc, ["look", "hoanthanh"], "đưa thuốc", moitruong.get_idbandohientai(), diachi = diachi)
        if not nv["bando"] or not nv["toado"]:
            self._ketthucthienxu(f"không đọc được chỗ Người Đưa Tin: {nv['mota'][:150]}")
            return None
        x, y = nv["toado"]
        if moitruong.get_idbandohientai() != nv["bando"] or (moitruong.get_khoangcachdiem(x, y) > KHOANGCACHTOITOADO and not s.get("luctoitoado")):
            s["trangthai"] = f"tới {tennpc} {laytenbando(nv['bando'])} ({x}, {y})"
            return self._dentoi(s, nv["bando"], x, y, tennpc)
        # Tới toạ độ mà chưa thấy: đứng chờ chút rồi dò quanh
        s.setdefault("luctoitoado", time.time())
        if time.time() - s["luctoitoado"] < THOIGIANCHONGUOIDUATIN:
            s["trangthai"] = f"chờ {tennpc} ở ({x}, {y})"
            return None
        diems = self._laydiemdoquanh(nv["bando"], (x, y)) or [(x, y)]
        return self._diquadiem(s, f"npc|{tennpc}", nv["bando"], diems, f"tìm {tennpc}")

    # --- Bảo Vật Di Thất ---------------------------------------------------------------------------------------------------------------
    def _doituongquanhbaovat(self, x, y):
        # Mọi đối tượng (trừ người chơi) cách (x, y) tối đa BANKINHBAOVAT ô -> [(địa chỉ, tên, danh hiệu, loại, (x, y), cách toạ độ)]
        moitruong = self.moitruong
        kq = []
        for dc in moitruong._get_diachidoituongxungquanhs():
            try:
                if moitruong.get_is_nguoichoi(dc):
                    continue
                xd, yd = moitruong.get_toado(dc)
                cach = max(abs(xd - x), abs(yd - y))
                if cach > BANKINHBAOVAT:
                    continue
                loai = "đồ đất" if moitruong.get_is_vatphamtontai(dc) else "NPC" if moitruong.get_is_npc(dc) else \
                    "chết" if moitruong.get_is_nhanvatdachet(dc) else "quái"
                kq.append((dc, moitruong.get_tendoituong(dc) or "", moitruong.get_danhhieudoituong(dc), loai, (xd, yd), cach))
            except Exception:
                continue
        return sorted(kq, key = lambda d: d[5])

    def _buocbaovat(self, s, nv):
        moitruong = self.moitruong
        if not nv["bando"] or not nv["toado"]:
            self._ketthucthienxu(f"không đọc được chỗ báu vật: {nv['mota'][:150]}")
            return None
        # Đã nhặt được (món TENVATPHAMBAOVAT trong túi; nhiệm vụ không tự đổi, acc 359 2026-11-15): về Tổng Quản trả
        if self._demvatpham(TENVATPHAMBAOVAT):
            if f"cobaovat|{nv['khoa']}" not in s["dabao"]:
                s["dabao"].add(f"cobaovat|{nv['khoa']}")
                self._logtx(f"Hành trang có {TENVATPHAMBAOVAT}: về Tổng Quản trả")
            s["trangthai"] = f"trả {nv['ten']} ở Tổng Quản bang"
            return self._toitongquan(s, nv, ["look", f"kw:{LENHTRATHIENXU}", f"kw:{LENHHOANTHANHTHIENXU}"], "trả báu vật")
        idbando = nv["bando"]
        x, y = nv["toado"]
        nhan = "tìm báu vật"
        if moitruong.get_idbandohientai() != idbando or (moitruong.get_khoangcachdiem(x, y) > KHOANGCACHTOITOADO and not s.get("luctoitoado")):
            s["trangthai"] = f"{nhan}: tới {laytenbando(idbando)} ({x}, {y})"
            return self._dentoi(s, idbando, x, y, nhan, khoangcach = 1.)
        now = time.time()
        s.setdefault("luctoitoado", now)
        bv = s.get("baovat")
        if not bv or bv["khoa"] != nv["khoa"]:
            bv = s["baovat"] = {"khoa": nv["khoa"], "luc": now, "dathu": set(), "ghi": set()}
        doituongs = self._doituongquanhbaovat(x, y)
        # Ghi log mọi đối tượng mới thấy quanh toạ độ (học xem báu vật là gì)
        moi = [d for d in doituongs if d[0] not in bv["ghi"]]
        if moi:
            bv["ghi"].update(d[0] for d in moi)
            self._logtx("Quanh báu vật " + str((x, y)) + ": " + "; ".join(
                f"{ten}{f' [{dh}]' if dh else ''} ({loai}, {toado}, id {moitruong.get_iddoituong(dc):x})" for dc, ten, dh, loai, toado, _ in moi))
        if now - bv["luc"] > THOIGIANTIMBAOVAT:
            self._ketthucthienxu(f"tìm báu vật ở {laytenbando(idbando)} {(x, y)} {int(THOIGIANTIMBAOVAT)}s không được: làm tay 1 lần "
                                 "rồi gửi log [THIÊN XU] để bổ sung")
            return None
        # 0. "<Tên bang> Bảo Rương" (NPC, đúng toạ độ; người dùng 2026-11-15): tới look, game cho vận khí một lúc rồi nhặt được. Vòng chính
        # tạm chờ khi đang vận khí (đứng yên, không bị ngắt); look tới khi nhiệm vụ đổi, tối đa SOLANTHUTHIENXU lần. Bang khác cũng có rương
        # thì ưu tiên rương của bang mình
        tenbang = self._laytenbang(s)
        ruongs = [d for d in doituongs if chuanhoaten(TENBAORUONG) in chuanhoaten(d[1]) and d[3] != "đồ đất"]
        ruongs.sort(key = lambda d: (not (tenbang and chuanhoaten(tenbang) in chuanhoaten(d[1])), d[5]))
        if ruongs:
            dc, ten = ruongs[0][0], ruongs[0][1]
            if f"ruong|{nv['khoa']}" not in s["dabao"]:
                s["dabao"].add(f"ruong|{nv['khoa']}")
                self._logtx(f"Thấy {ten} ở {ruongs[0][4]}: look rồi chờ vận khí nhặt")
            s["trangthai"] = f"{nhan}: mở {ten}"
            return self._noichuyentx(s, nv, ten, ["look"], f"mở {ten}", idbando, diachi = dc)
        # 1. Đồ dưới đất gần toạ độ: tới sát rồi nhặt
        for dc, ten, dh, loai, toado, _ in doituongs:
            if loai != "đồ đất" or (dc, "nhat") in bv["dathu"] and now - bv.get("lucnhat", 0.) > 20.:
                continue
            if moitruong.get_khoangcach(dc) > 1.5:
                s["trangthai"] = f"{nhan}: tới nhặt {ten} {toado}"
                return self._dentoi(s, idbando, toado[0], toado[1], f"nhặt {ten}", khoangcach = 1.)
            if (dc, "nhat") not in bv["dathu"]:
                bv["dathu"].add((dc, "nhat"))
                bv["lucnhat"] = now
                self._logtx(f"Nhặt {ten} ở {toado}")
            moitruong.action_ngatdichuyen()
            moitruong.action_nhatvatpham(dc)
            s["trangthai"] = f"{nhan}: nhặt {ten}"
            return None
        # 2. NPC / vật lạ gần toạ độ (không phải NPC cố định quanh thành): look -> lựa chọn hoàn thành, mỗi cái 1 lần
        for dc, ten, dh, loai, toado, _ in doituongs:
            if loai not in ("NPC", "quái") or dc in bv["dathu"] or any(chuanhoaten(t) in chuanhoaten(ten + " " + dh) for t in TUBOQUABAOVAT):
                continue
            if loai == "quái" and not re.search(r"bảo|báu|rương|hộp|bao|tráp", ten, re.IGNORECASE):
                continue
            yeucau = self._noichuyentx(s, nv, ten, ["look", "hoanthanh"], f"look {ten}", idbando, diachi = dc)
            # Chỉ tính là đã thử khi đã thật sự look (đang đi tới thì chưa: trước đây đánh dấu ngay lúc đi nên tới nơi bỏ qua, log 347)
            if s["hoithoai"]:
                bv["dathu"].add(dc)
                self._logtx(f"Thử look {ten} ({loai}) ở {toado}")
            return yeucau
        # 3. Không thấy gì: tự nhặt quanh chỗ đứng (đồ có thể không nằm trong bảng đối tượng), chờ chút rồi dò quanh
        if now - bv.get("lucnhatquanh", 0.) > 3.:
            bv["lucnhatquanh"] = now
            moitruong.action_nhatvatphamxungquanh()
        if now - s["luctoitoado"] < THOIGIANCHOBAOVAT:
            s["trangthai"] = f"{nhan}: chờ ở ({x}, {y})"
            return None
        diems = self._laydiemdoquanh(idbando, (x, y)) or [(x, y)]
        s["trangthai"] = f"{nhan}: dò quanh ({x}, {y})"
        return self._diquadiem(s, f"baovat|{nv['khoa']}", idbando, diems, nhan)

    # --- Trừ Ác Giúp Yếu --------------------------------------------------------------------------------------------------------------
    def _timacnhan(self, tenquai):
        # Ác nhân gần nhất: tên game so bỏ dấu cách (mô tả có chữ dính "PhươngTiểu"), có thể kèm "( ID )"; con mang ID người khác bỏ qua.
        # -> (tên game, địa chỉ) hoặc (None, None)
        moitruong = self.moitruong
        can = _khongcach(tenquai)
        tot, khoangcachtot = (None, None), None
        for dc in moitruong._get_diachidoituongxungquanhs():
            if moitruong.get_is_nguoichoi(dc):
                continue
            ten = moitruong.get_tendoituong(dc) or ""
            if can not in _khongcach(re.sub(r"\(\s*\d+\s*\)", "", ten)) or moitruong.get_is_quairiengnguoikhac(ten):
                continue
            khoangcach = moitruong.get_khoangcach(dc)
            if khoangcachtot is None or khoangcach < khoangcachtot:
                tot, khoangcachtot = (ten, dc), khoangcach
        return tot

    def _buoctruac(self, s, nv):
        moitruong = self.moitruong
        if not nv["tenquai"] or not nv["bando"] or not nv["toado"]:
            self._ketthucthienxu(f"không đọc được ác nhân / chỗ xuất hiện: {nv['mota'][:150]}")
            return None
        idbando = nv["bando"]
        x, y = nv["toado"]
        nhan = f"diệt {nv['tenquai']}"
        if moitruong.get_idbandohientai() != idbando:
            s["trangthai"] = f"{nhan}: tới {laytenbando(idbando)} ({x}, {y})"
            return self._dentoi(s, idbando, x, y, nhan)
        tengame, gannhat = self._timacnhan(nv["tenquai"])
        now = time.time()
        dt = s["doithu"]
        if gannhat and (not moitruong.get_is_nhanvattontai(gannhat) or moitruong.get_is_nhanvatdachet(gannhat)):
            return self._dagiettx(s, nv, "thấy ác nhân đã chết")
        s["trangthai"] = nhan
        if gannhat:
            s["chedo"] = "danhquai"
            for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
                self._doituychontx(s, thuoctinh, giatri, ten)
            # Danh sách rỗng là đánh mọi quái: luôn giữ tên trong nhiệm vụ, thêm tên game thật (có "( ID )")
            s["tenquai"] = {nv["tenquai"], tengame}
            if f"thay|{nv['khoa']}" not in s["dabao"]:
                s["dabao"].add(f"thay|{nv['khoa']}")
                self._logtx(f"Thấy ác nhân: {tengame!r}")
            s["doithu"] = {"khoa": nv["khoa"], "luc": now, "mau": moitruong.get_phantramsinhlucconlai(gannhat),
                           "kc": moitruong.get_khoangcach(gannhat)}
            # Phần chọn mục tiêu chung có lúc không chọn con này (acc 354 Ác Nhân  SầmThỏ Nhân 2026-11-15, chưa rõ lý do): thấy mà
            # THOIGIANTUGANMUCTIEU giây chưa có mục tiêu thì tự gán, ghi log lý do lọc 1 lần để xem
            if moitruong.get_diachicosothongtinnhanvatmuctieudangchon() == gannhat:
                s.pop("lucchuacomuctieu", None)
            elif now - s.setdefault("lucchuacomuctieu", now) > THOIGIANTUGANMUCTIEU:
                if f"tugan|{nv['khoa']}" not in s["dabao"]:
                    s["dabao"].add(f"tugan|{nv['khoa']}")
                    xq, yq = moitruong.get_toado(gannhat)
                    self._logtx(f"{THOIGIANTUGANMUCTIEU:.0f}s chưa chọn được {tengame!r} làm mục tiêu, tự gán. Chẩn đoán: "
                                f"cothetancong={moitruong.get_is_cothetancong(gannhat)}, loai={moitruong.get_idloainhanvat(gannhat)}, "
                                f"npc={moitruong.get_is_npc(gannhat)}, boqua={self._is_tenbiboqua(tengame)}, "
                                f"trongds={tengame in self._laytenmuctieutancongs()}, vungcam={self._kiemtra_divaovungcam(xq, yq)}, "
                                f"tamdiem={self._kiemtra_tamdiemdanh(xq, yq)}, "
                                f"biloi={moitruong.get_iddoituong(gannhat) in self._idmuctieubiloi_map}, "
                                f"timmuctieu={self._is_tudongtimkiemmuctieu}, kynang={self._is_tudongsudungkynang}, "
                                f"kc={moitruong.get_khoangcach(gannhat):.1f}, tamxa={self._khoangcachsudungkynangtamxa}")
                moitruong.set_diachicosothongtinnhanvatmuctieudangchon(gannhat)
            xq, yq = moitruong.get_toado(gannhat)
            return self._dentoi(s, idbando, xq, yq, f"{nhan}: đánh {tengame}",
                                khoangcach = self._khoangcachsudungkynangtamxa, is_dioo = self._is_dioo(idbando))
        if dt and dt["khoa"] == nv["khoa"] and now - dt["luc"] < THOIGIANMATACNHAN:
            if (100 if dt["mau"] is None else dt["mau"]) <= MAUMATACNHAN and dt["kc"] <= KHOANGCACHMATACNHAN:
                return self._dagiettx(s, nv, f"ác nhân mất khỏi tầm nhìn lúc còn {dt['mau']}% máu")
            # Vừa còn thấy (khuất chốc lát): đứng đánh tiếp
            return None
        s["doithu"] = None
        s["chedo"] = "dichuyen"
        # Chưa thấy: tới toạ độ, chờ chút rồi dò quanh
        if moitruong.get_khoangcachdiem(x, y) > KHOANGCACHTOITOADO and not s.get("luctoitoado"):
            return self._dentoi(s, idbando, x, y, nhan)
        s.setdefault("luctoitoado", now)
        if now - s["luctoitoado"] < THOIGIANCHONGUOIDUATIN:
            s["trangthai"] = f"{nhan}: chờ ở ({x}, {y})"
            return None
        diems = self._laydiemdoquanh(idbando, (x, y)) or [(x, y)]
        return self._diquadiem(s, f"truac|{nv['khoa']}", idbando, diems, f"tìm {nv['tenquai']}")

    def _dagiettx(self, s, nv, lydo):
        s["dagiet"].add(nv["khoa"])
        s["doithu"] = None
        s.pop("luctoitoado", None)
        s["chedo"], s["tenquai"] = "dichuyen", set()
        self._logtx(f"Đã diệt {nv['tenquai']} ({lydo}), về Tổng Quản trả")
        return None

    # --- Hội thoại NPC -----------------------------------------------------------------------------------------------------------
    def _noichuyentx(self, s, nv, tennpc, buocs, viec, idbandogoiy = None, diachi = None):
        # Tới gần NPC rồi nói chuyện theo các bước (_xulyhoithoaitx). Mỗi việc thử tối đa SOLANTHUTHIENXU lần. -> yêu cầu di chuyển / None
        moitruong = self.moitruong
        if not diachi:
            diachi, yeucau = self._tinpc(s, tennpc, idbandogoiy)
            if not diachi:
                if yeucau is None and not idbandogoiy and not self._sovitri.timnpc(tennpc, self._thumucgame()):
                    # Gửi Thư Nhà cho NPC không rõ chỗ: huỷ luôn cho khỏi đứt chuỗi lượt (người dùng dặn 2026-11-22, vd Bạch Dễ
                    # bản đồ 886); việc khác (Tổng Quản, Người Đưa Tin...) vẫn dừng báo lỗi
                    if nv and nv["loai"] == "guithu":
                        lydohuy = f"Gửi Thư Nhà cho {tennpc} (không biết ở đâu)"
                        s["khoadangnhan"] = None
                        s["trangthai"] = f"huỷ {nv['ten']}: {lydohuy}"
                        self.action_huynhiemvuthatbai(s, MUCTHIENXU, nv, lambda chu: self._logtx(f"Huỷ ({lydohuy}): {chu}"))
                        return None
                    self._ketthucthienxu(f"không biết {tennpc} ở đâu ({viec}): đứng gần NPC đó 1 lần cho Foxia ghi lại vị trí")
                return yeucau
        s.pop("luctoitoado", None)
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
        if solan >= SOLANTHUTHIENXU:
            if not nv:
                luot, tong = s.get("luottong") or (0, SOLUOTTHIENXUMOINGAY)
                if luot >= tong:
                    self._ketthucthienxu(thongbao = f"✅ Đã đủ {tong} lượt Thiên Xu Viện hôm nay")
                else:
                    self._ketthucthienxu(f"nhận ở {tennpc} {solan} lần không được nhiệm vụ – hết lượt trong ngày? (xem menu trong log)")
                return None
            self._ketthucthienxu(f"{viec} ở {tennpc} {solan} lần mà nhiệm vụ không đổi ({motathienxu(nv)})")
            return None
        moitruong.action_ngatdichuyen()
        idnpc = moitruong.get_iddoituong(diachi)
        s["thu"][khoa] = (solan + 1, time.time() + 10.)
        s["hoithoai"] = {"manpc": f"{idnpc:x}#", "buocs": list(buocs), "luc": 0., "khoa": khoa}
        s["trangthai"] = f"{viec} ở {tennpc} (lần {solan + 1})"
        self._logtx(f"{viec} ở {tennpc} (lần {solan + 1}): {buocs}")
        return None

    def _xulyhoithoaitx(self, s):
        # Mỗi lượt gửi tối đa 1 bước: "look" mở menu gốc; "kw:<từ khoá>" chọn lựa chọn có lệnh kết thúc bằng từ khoá (không có trong menu
        # thì gửi thẳng "talk <id># <từ khoá>" như game); "hoanthanh" lựa chọn có task_info, không có thì lựa chọn đầu (trừ CLOSE).
        # Ghi lời NPC + các lệnh trong menu để xem log biết menu thật
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
        else:
            noidung = moitruong.get_noidungcuasotuychon()
            if not noidung and now - h["luc"] < THOIGIANCHOMENU:
                return
            lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"] if noidung else []
            # Bỏ dấu câu trước khi so: chuanhoaten dồn dấu thanh về cuối từ nên "vội!" không chứa "vội" (21/11 acc 359 chờ hụt 3 lần rồi dừng)
            if noidung and chuanhoaten(LOICHONHANLAI) in chuanhoaten(re.sub(r"[^\w\s]", " ", unicodedata.normalize("NFC", noidung))):
                # Vừa huỷ: chờ THOIGIANCHONHANLAI giây rồi nhận lại, không tính lần thử
                self._logtx(f"Tổng Quản bảo chờ ({(noidung or '')[:80]!r}): {int(THOIGIANCHONHANLAI)}s nữa nhận lại")
                s["lucchonhan"] = now + THOIGIANCHONHANLAI
                s["thu"].pop(h["khoa"], None)
                s["hoithoai"] = None
                if moitruong.get_is_danghiencuasotuychon():
                    moitruong.set_is_danghiencuasotuychon(False)
                return
            if buoc.startswith("kw:"):
                tukhoa = buoc[3:]
                lenh = next((l for l in lenhs if l.split("# ", 1)[-1].strip() == tukhoa), None) or f"talk {h['manpc']} {tukhoa}"
            else:
                lenh = next((l for l in lenhs if l.split("# ", 1)[-1].strip() == "task_info"), None) or (lenhs[0] if lenhs else None)
            self._logtx(f"Menu {h['manpc']}: {(noidung or '')[:120]!r} {lenhs} -> {lenh or 'không có lựa chọn'}")
            if lenh:
                moitruong.xoa_noidungcuasotuychon()
                moitruong.action_thucthicaulenh(lenh)
            else:
                h["buocs"] = [buoc]
        h["buocs"].pop(0)
        h["luc"] = now
