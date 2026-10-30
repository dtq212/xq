# Nhiệm vụ Sư Gia (bật tay trên giao diện, làm tới khi đủ số lần trong ngày NPC báo hoặc bấm dừng). Nhân vật bật là trưởng nhóm (đi một
# mình cũng được), thành viên bật Theo sau (hoặc bật Sư Gia ở thành viên: chỉ làm phần của thành viên). Mỗi lượt:
#   nhận    : Chu Quốc (345, 159) Từ Phúc (danh hiệu Sư Gia) "1. Hiệp trợ tiêu diệt" -> "1. Nhận". Lời NPC có "Số lần làm nhiệm vụ trong
#             ngày 30 là: 1/10 lần": đủ thì dừng. Trưởng nhóm nhận xong thì thành viên hiện menu "<trưởng nhóm> đã nhận nhiệm vụ rồi...
#             1. Nhận" -> thành viên tự chọn "1. Nhận" (_nhanmoisugia)
#   tìm     : cửa sổ nhiệm vụ "Nhiệm vụ Sư Gia" / "Tiêu diệt Tội Phạm  Thích Đại Hắc", mô tả "...Tội Phạm Thích Đại Hắc ở Nguy làm..." ->
#             tới nước đó, dùng kỹ năng Truy Tìm Thổ Phỉ (thẻ Cơ Bản, "pf2 41"), game báo vào khung trò chuyện "Bạn bám sát Tội Phạm
#             Thích Đại Hắc đến tại Cách bạn cực xa Phía đông bắc." -> đi theo hướng đó một quãng theo độ xa rồi truy tìm lại
#   giết    : thấy tội phạm thì đánh (chỉ con đó), tiến độ "Tiêu diệt ...: 1/1" là xong
#   trả     : về Từ Phúc "1. Tiêu diệt tội phạm<tên>" -> "1. Hoàn thành nhiệm vụ"; thành viên cũng tự trả (_xulysugiathanhvien)
# Hướng của tin Truy Tìm đổi ra toạ độ bản đồ thế nào chưa đo: thử lần lượt các cách đổi (HUONGs), đi mà xa thêm thì đổi cách khác; thấy tội
# phạm thì so mọi lần đọc tin với chỗ tội phạm, lưu cách khớp nhất (_internal/sugia_huong.json) cho lần sau.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import json
import math
import os
import re
import time
import unicodedata

from hangso_xq import *
from dexuatlotrinh_xq import layvungtoiduoc
from nhiemvu_xq import boma, chuanhoaten, laydiemkhampha, timbandotheoten, _thumucgoc
from thongbao_xq import baosuco
from tienich_xq import phatam

NPCSUGIA = ("Từ Phúc", 345, 159)
BANDONPCSUGIA = BANDO_CHUQUOC
# Truy Tìm Thổ Phỉ: kỹ năng thẻ Cơ Bản (Truy Tìm, id 41), gửi bằng pf2 như các kỹ năng Cơ Bản khác
LENHTRUYTIM = "pf2 41"
# Truy tìm xong chờ tin trong khung trò chuyện tối đa chừng này giây; quá SOLANTRUYTIMLOI lần liền không có tin thì đi dò khắp bản đồ
THOIGIANCHOTINTRUYTIM = 4.
GIANCACHTRUYTIM = 3.
SOLANTRUYTIMLOI = 3
# Đang đi theo hướng thì truy tìm lại khi: tới nơi, THOIGIANKHONGGANHON giây không gần đích thêm (kẹt), hoặc quá THOIGIANMOIHUONG giây.
# Không cắt ngang khi vẫn đang gần lại: đích bên kia sông thì tìm đường vòng xa, từng truy tìm lại giữa đường (15s) ra đích mới mà đường
# vòng tới đó chạy ngược về chỗ cũ => chạy lên chạy xuống mãi ở Ngụy Quốc
THOIGIANMOIHUONG = 120.
THOIGIANKHONGGANHON = 10.
# Độ xa trong tin (theo thứ tự gần -> xa) -> số ô đi mỗi lần
# Chọn điểm tới (_chondiemtruytim): ô trong quạt ±GOCQUATTRUYTIM độ theo hướng, cách [số ô x TYLEGANTRUYTIM, số ô x TYLEXATRUYTIM]
GOCQUATTRUYTIM = 35.
TYLEGANTRUYTIM = 0.6
TYLEXATRUYTIM = 1.6
DOXAs = (("xung quanh", 6), ("rất gần", 10), ("gần", 15), ("không xa", 25), ("rất xa", 40), ("cực xa", 60))
# Hướng trong tin -> (đông, bắc)
HUONG_MAP = {"đông bắc": (1, 1), "đông nam": (1, -1), "tây bắc": (-1, 1), "tây nam": (-1, -1), "đông": (1, 0), "tây": (-1, 0),
             "nam": (0, -1), "bắc": (0, 1)}
# Cách đổi (đông, bắc) ra (dx, dy) trên bản đồ: ((a, b), (c, d)) -> dx = a * đông + b * bắc, dy = c * đông + d * bắc. Đo ở Tề Quốc
# (10 lần đọc tin so với chỗ tội phạm, khớp 0.98): Đông = x tăng, Bắc = y tăng. Các cách sau dự phòng
HUONGs = (((1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, -1)), ((-1, 0), (0, 1)),
          ((1, 1), (-1, 1)), ((1, -1), (1, 1)), ((-1, 1), (-1, -1)), ((-1, -1), (1, -1)))
# Đi theo 1 cách đổi mà chừng này lần liền tin báo xa thêm thì đổi cách khác
SOLANXATHEM = 2
# Nước trong mô tả ("ở Nguy") -> bản đồ, so không dấu
NUOC_MAP = {"te": BANDO_TEQUOC, "han": BANDO_HANQUOC, "trieu": BANDO_TRIEUQUOC, "nguy": BANDO_NGUYQUOC, "tan": BANDO_TANQUOC,
            "so": BANDO_SOQUOC, "yen": BANDO_YENQUOC, "chu": BANDO_CHUQUOC}
# Thấy tội phạm cách xa hơn chừng này ô thì đi lại gần (bot chỉ đánh mục tiêu trong tầm)
KHOANGCACHTOITOIPHAM = 8.
# Nói chuyện Từ Phúc xong mà chừng này giây cửa sổ nhiệm vụ chưa đổi thì nói lại, quá SOLANTHUSUGIA lần thì dừng
THOIGIANCHONHIEMVUDOISUGIA = 10.
SOLANTHUSUGIA = 3
# Trưởng nhóm chờ thành viên cùng máy trả nhiệm vụ trước khi nhận lượt mới / nhận theo sau khi mình nhận, tối đa chừng này giây
THOIGIANCHOTHANHVIENTRA = 90.
THOIGIANCHOTHANHVIENNHAN = 20.
THOIGIANSUGIATOIDA = 6 * 3600.
GIANCACHGHIHUONG = 5.
THOIGIANCHOMOTASUGIA = 30.
# Thấy tội phạm: thành viên lượt này phải còn trong nhóm, còn sống, đứng trong chừng này ô mới đánh; người rời nhóm thì GIANCACHMOILAISUGIA
# giây mời lại 1 lần; chờ quá THOIGIANBAOCHOTHANHVIENSUGIA giây thì báo (vẫn chờ)
KHOANGCACHTHANHVIENSUGIA = 10.
GIANCACHMOILAISUGIA = 10.
THOIGIANBAOCHOTHANHVIENSUGIA = 180.


def _khongdau(chuoi):
    chuoi = unicodedata.normalize("NFD", str(chuoi or "")).replace("đ", "d").replace("Đ", "D")
    return " ".join("".join(c for c in chuoi if not unicodedata.combining(c)).lower().split())


def _duongdanhuong():
    return os.path.join(_thumucgoc(), "_internal", "sugia_huong.json")


def _taihuong():
    # Lưu theo cách đổi (không theo số thứ tự: danh sách HUONGs đổi thì số cũ trỏ nhầm)
    try:
        with open(_duongdanhuong(), encoding = "utf-8") as f:
            cachdoi = json.load(f).get("cachdoi")
        cachdoi = tuple(tuple(hang) for hang in cachdoi)
        return HUONGs.index(cachdoi) if cachdoi in HUONGs else None
    except Exception:
        return None


def _luuhuong(i):
    try:
        with open(_duongdanhuong(), "w", encoding = "utf-8") as f:
            json.dump({"cachdoi": HUONGs[i]}, f)
    except Exception:
        pass


def doihuong(dong, bac, i):
    (a, b), (c, d) = HUONGs[i]
    return a * dong + b * bac, c * dong + d * bac


def laybandonuoc(nuoc):
    ten = re.sub(r"\s+quoc$", "", _khongdau(nuoc))
    return NUOC_MAP.get(ten) or timbandotheoten(f"{nuoc} Quốc") or timbandotheoten(nuoc)


def laynhiemvusugia(mucs):
    # mucs: [(tên mục, mô tả)] của cửa sổ nhiệm vụ -> {"ten", "toipham", "loi", "is_xong", "tiendo", "nuoc", "bando", "phutconlai"} hoặc None.
    # Mục cha "Nhiệm vụ Sư Gia", mục con "Tiêu diệt Tội Phạm  Thích Đại Hắc"; mô tả:
    #   "Tiêu diệt Tội Phạm Thích Đại Hắc (Lượt thứ 2)\nMục đích nhiệm vụ:\n Giúp Sư Gia tiêu diệt Tội Phạm Thích Đại Hắc.\n Tiêu diệt Tội
    #    Phạm Thích Đại Hắc: 0/1 (Thời gian còn 59 phút)\nMiêu tả nhiệm vụ:\n Gần đây có tên tội phạm Tội Phạm Thích Đại Hắc ở Nguy làm..."
    muccha = None
    for ten, mota in mucs or ():
        if not ten.startswith(" "):
            muccha = ten if "su gia" in _khongdau(ten) else None
            continue
        if muccha:
            nv = _phantichsugia(ten.strip(), mota)
            nv["muccha"] = muccha
            return nv
    return None


def _phantichsugia(tenmuc, mota):
    is_xong = bool(re.search(r"\(\s*Xong\s*\)\s*$", tenmuc))
    ten = " ".join(re.sub(r"\(\s*Xong\s*\)\s*$", "", tenmuc).split())
    vanban = boma(mota).replace("\r", "")
    toipham = re.sub(r"^Tiêu diệt\s*", "", ten, flags = re.IGNORECASE).strip()
    tiendo = re.search(r"(\d+)\s*/\s*(\d+)\s*\(?\s*Thời gian", vanban) or re.search(r"[:：]\s*(\d+)\s*/\s*(\d+)", vanban)
    phut = re.search(r"Thời gian còn\s*(\d+)\s*phút", vanban)
    nuoc = re.search(r"\bở\s+(\S+(?:\s+Quốc)?)\s+làm", vanban)
    nuoc = nuoc.group(1) if nuoc else ""
    return {"ten": ten, "toipham": toipham, "loi": re.sub(r"^Tội Phạm\s*", "", toipham, flags = re.IGNORECASE).strip(), "is_xong": is_xong,
            "tiendo": (int(tiendo.group(1)), int(tiendo.group(2))) if tiendo else None, "nuoc": nuoc,
            "bando": laybandonuoc(nuoc) if nuoc else None, "phutconlai": int(phut.group(1)) if phut else None, "is_comota": bool(vanban.strip())}


def is_xongsugia(nv):
    return bool(nv) and (nv["is_xong"] or bool(nv["tiendo"] and nv["tiendo"][1] and nv["tiendo"][0] >= nv["tiendo"][1]))


def doctintruytim(noidung):
    # "Bạn bám sát Tội Phạm  Thích Đại Hắc đến tại Cách bạn cực xa Phía đông bắc." (tin có thể bị cắt làm 2 dòng, nơi gọi nối lại)
    # -> (thứ hạng độ xa 0 gần nhất, tên độ xa, hướng) hoặc None
    i = noidung.lower().rfind("bám sát")
    if i < 0:
        return None
    phan = " ".join(noidung[i:].lower().split())
    phan = phan[phan.find("đến tại"):] if "đến tại" in phan else phan
    hang = next(((k, ten) for k, (ten, _) in enumerate(DOXAs) if ten in phan and not (ten == "gần" and "rất gần" in phan)), None)
    huong = re.search(r"phía\s+(đông bắc|đông nam|tây bắc|tây nam|đông|tây|nam|bắc)", phan)
    if not hang or not huong:
        return None
    return hang[0], hang[1], huong.group(1)


class TacTuSuGia:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_sugia(self):
        if self._sugia:
            return
        huong = _taihuong()
        self._sugia = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "hoithoai": None, "dabao": set(), "solan": 0,
                       "tenquai": set(), "huong": huong if huong is not None else 0, "is_dadohuong": huong is not None, "truytim": None,
                       "mau": [], "nvtruoc": None, "thu": {}, "khampha": None, "solanmonphai": 0, "lucmonphai": 0.,
                       "thanhviens": {}, "dudoi": False, "lucchodoi": 0., "lucmoi": {}}
        self.moitruong._inlog("[SƯ GIA] Bắt đầu làm nhiệm vụ Sư Gia" + (f" (cách đổi hướng đã đo: {HUONGs[huong]})" if huong is not None else ""))
        phatam("Bắt đầu nhiệm vụ sư gia")

    def huy_sugia(self):
        if self._sugia:
            self._ketthucsugia("Đã dừng nhiệm vụ Sư Gia (bấm tay)")

    def get_is_dangsugia(self):
        return bool(self._sugia)

    def get_is_sugiadichuyen(self):
        # Đang tự lo đi lại / nói chuyện NPC / truy tìm: không chọn quái dọc đường, đi trước đánh / nhặt. Bật ở thành viên thì chỉ khi đang
        # tự đi trả nhiệm vụ (còn lại theo sau và đánh như thường)
        s = self._sugia
        return bool(s) and (s["chedo"] in ("dichuyen", "cho") or (s["chedo"] == "thanhvien" and bool(self._yeucautudo)))

    def get_is_sugiadanhquai(self):
        return bool(self._sugia) and self._sugia["chedo"] == "danhquai"

    def get_trangthaisugia(self):
        if self._sugia:
            s = self._sugia
            solan = f", hôm nay {s['homnay'][0]}/{s['homnay'][1]}" if s.get("homnay") else ""
            return f"Sư Gia (xong {s['solan']} lượt{solan}): {s['trangthai']}"
        return self._ketquasugia or ""

    def get_nhiemvusugiashare(self):
        # Nhiệm vụ Sư Gia của mình cho trưởng nhóm cùng máy biết (shared_data): "" không có, "dang" đang làm, "xong" chờ trả. Nhớ 1s
        luc, kq = self._bonhonhiemvusugia
        if time.time() - luc > 1.:
            nv = laynhiemvusugia(self.moitruong.get_danhsachmucnhiemvu())
            kq = ("xong" if is_xongsugia(nv) else "dang") if nv else ""
            self._bonhonhiemvusugia = (time.time(), kq)
        return kq

    def _logsg(self, noidung):
        self.moitruong._inlog(f"[SƯ GIA] {noidung}")

    def _ketthucsugia(self, thongbao, is_loi = False):
        s = self._sugia
        self._sugia = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if s and s["solan"]:
            thongbao += f" (phiên này trả {s['solan']} lượt)"
        self._logsg(thongbao)
        self._ketquasugia = f"{time.strftime('%H:%M')} {thongbao}"
        baosuco(self.moitruong, "sumon", thongbao, khoa = f"sugia|{s['batdau'] if s else 0}", giancach = 0.)
        phatam("Lỗi nhiệm vụ sư gia" if is_loi else "Kết thúc nhiệm vụ sư gia")

    def _baosugia(self, s, khoa, noidung):
        # Báo Telegram 1 lần cho mỗi việc cần người dùng để ý, bot vẫn chạy tiếp
        if khoa not in s["dabao"]:
            s["dabao"].add(khoa)
            self._logsg(noidung)
            baosuco(self.moitruong, "sumon", noidung, khoa = f"sugia|{s['batdau']}|{khoa}", giancach = 0.)

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulysugia(self):
        # Gọi thay lộ trình điểm đánh khi đang làm Sư Gia -> yêu cầu di chuyển hoặc None
        s = self._sugia
        moitruong = self.moitruong
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logsg(s["trangthai"])
        s["chedo"] = "dichuyen"
        if moitruong.get_is_nhanvatdachet() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0 or moitruong.get_is_dangvankhi():
            return None
        if time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        if time.time() - s["batdau"] > THOIGIANSUGIATOIDA:
            self._ketthucsugia(f"❌ Sư Gia dừng: quá {int(THOIGIANSUGIATOIDA // 3600)} giờ", is_loi = True)
            return None
        if moitruong.get_is_dangnamtrongnhom() and not moitruong.get_is_truongnhom():
            # Bật ở thành viên: chỉ nhận theo trưởng nhóm, đi theo (Theo sau) và tự trả
            s["chedo"] = "thanhvien"
            s["trangthai"] = "thành viên: nhận / trả theo trưởng nhóm" + ("" if self._is_tudongtheosau else ", tự về Từ Phúc trả")
            yeucau = self._xulysugiathanhvien(is_tubat = True)
            return yeucau if yeucau is not False else None
        mucs = moitruong.get_danhsachmucnhiemvu()
        if mucs is None:
            s["trangthai"] = "chưa đọc được nhiệm vụ: mở bảng nhiệm vụ trong game 1 lần"
            if time.time() - s.get("lucxinnhiemvu", 0.) > 10.:
                s["lucxinnhiemvu"] = time.time()
                moitruong.action_thucthicaulenh("quest list")
            return None
        nv = laynhiemvusugia(mucs)
        # Vừa nhận / sau "quest list" máy chủ chỉ gửi tên, mô tả (nước, tiến độ) gửi khi bấm vào dòng đó = "quest intro <mã>": xin mô tả,
        # cách nhau 10s, chờ tối đa THOIGIANCHOMOTASUGIA giây (như sư môn)
        if nv and not nv["is_comota"] and not nv["is_xong"]:
            s.setdefault("luctrongmota", time.time())
            self._xinmotasugia(nv)
            if time.time() - s["luctrongmota"] < THOIGIANCHOMOTASUGIA:
                s["trangthai"] = f"chờ mô tả nhiệm vụ {nv['ten']}"
                return None
        else:
            s.pop("luctrongmota", None)
        truoc = s["nvtruoc"]
        if truoc and not nv and is_xongsugia(truoc):
            s["solan"] += 1
            self._logsg(f"Đã trả lượt {s['solan']} ({truoc['ten']})")
            s["hoithoai"] = None
        elif truoc and not nv:
            self._logsg(f"Nhiệm vụ {truoc['ten']} biến mất khi chưa xong (hết giờ?), nhận lại")
        if nv and (not truoc or truoc["ten"] != nv["ten"] or truoc["bando"] != nv["bando"]):
            self._logsg(f"Nhiệm vụ: {nv['ten']} ở {nv['nuoc'] or '?'} ({laytenbando(nv['bando']) if nv['bando'] else 'chưa biết bản đồ'}), "
                        f"tiến độ {nv['tiendo']}, còn {nv['phutconlai']} phút")
            s.update(truytim = None, mau = [], hoithoai = None, thanhviens = {}, dudoi = False, lucchodoi = 0., lucmoi = {})
            s.pop("lucconhiemvu", None)
        s["nvtruoc"] = nv
        s["tenquai"] = set()
        if not nv:
            return self._nhansugia(s)
        s.pop("lucnhan", None)
        if is_xongsugia(nv):
            return self._trasugia(s, nv)
        # Vừa nhận: chờ thành viên cùng máy nhận theo (menu "đã nhận nhiệm vụ rồi") rồi mới đi
        chuanhans = self._laythanhviencungmay(("",))
        if chuanhans and time.time() - s.get("lucconhiemvu", time.time()) < THOIGIANCHOTHANHVIENNHAN:
            s.setdefault("lucconhiemvu", time.time())
            s["trangthai"] = f"chờ {', '.join(chuanhans)} nhận nhiệm vụ theo"
            return None
        s["lucconhiemvu"] = 0.
        self._ghithanhviensugia(s)
        return self._timtoipham(s, nv)

    def _xinmotasugia(self, nv):
        # Gửi "quest intro <mã>" xin mô tả nhiệm vụ Sư Gia (như bấm vào dòng đó trong cửa sổ nhiệm vụ), cách nhau 10s
        if time.time() - self._lucxinmotasugia <= 10.:
            return
        ma = self.moitruong.get_manhiemvu(nv["muccha"])
        if ma:
            self._lucxinmotasugia = time.time()
            self._logsg(f"Mô tả {nv['ten']} còn trống: gửi \"quest intro {ma[0]} {ma[1]} {ma[2]}\"")
            self.moitruong.action_thucthicaulenh(f"quest intro {ma[0]} {ma[1]} {ma[2]}")

    def _laythanhviencungmay(self, trangthais):
        # Tên thành viên trong nhóm chạy cùng máy (shared_data) có nhiệm vụ Sư Gia ở trạng thái trangthais ("" / "dang" / "xong")
        if self.shared_data is None or not self.moitruong.get_is_dangnamtrongnhom():
            return []
        thanhviens = set(self.moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) - {self.moitruong.get_idnguoichoi()}
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return []
        return [info.get("tennhanvat") or str(info.get("idnguoichoi")) for idcuaso, info in danhsach
                if idcuaso != self.idcuaso and isinstance(info, dict) and info.get("idnguoichoi") in thanhviens
                and time.time() - info.get("thoidiemcapnhat", 0.) <= 5. and info.get("_sugianhiemvu", "") in trangthais]

    def _toitusugia(self, s, nhan):
        # Tới Chu Quốc chỗ Từ Phúc -> yêu cầu di chuyển, hoặc False khi đã ở Chu Quốc
        if self.moitruong.get_idbandohientai() == BANDONPCSUGIA:
            return False
        tennpc, x, y = NPCSUGIA
        s["trangthai"] = f"{nhan}: về {laytenbando(BANDONPCSUGIA)} ({tennpc})"
        buoc = self._lapbuocditoibando(BANDONPCSUGIA, is_hoithanhphu = True, toadodich = (x, y))
        if buoc["loai"] in ("toinoi", "khongduong"):
            s["trangthai"] = f"không có đường tới {laytenbando(BANDONPCSUGIA)}: {buoc['mota']}"
            return None
        return self._thuchienbuocditoibando(buoc, BANDONPCSUGIA, (x, y), "[SƯ GIA] " + nhan)

    def _khongcatgocchu(self, yeucau):
        # Ở Chu Quốc (rào xếp chéo chạm góc quanh Từ Phúc, tìm đường của game / client lách qua khe góc là húc rào giật giật): đi bằng
        # đường bot tự tìm không cắt góc (moitruong.action_dikhongcatgoc)
        if yeucau and yeucau.get("yeucau") == YEUCAUDICHUYENDICHUYENTUDO and self.moitruong.get_idbandohientai() == BANDONPCSUGIA:
            yeucau["is_khongcatgoc"] = True
        return yeucau

    def _noichuyensugia(self, s, *thamso, **thamsoten):
        ketqua, yeucau = self._noichuyenlls(s, *thamso, **thamsoten)
        return ketqua, self._khongcatgocchu(yeucau)

    def _kiemtramenusugia(self, noidung):
        # Lời Từ Phúc lúc nhận: "Số lần làm nhiệm vụ trong ngày 30 là: 1/10 lần" -> nhớ để hiện, đủ thì không nhận
        m = re.search(r"trong ngày.*?(\d+)\s*/\s*(\d+)\s*lần", noidung or "")
        if m:
            self._sugia["homnay"] = (int(m.group(1)), int(m.group(2)))
            return int(m.group(1)) < int(m.group(2))
        return True

    def _nhansugia(self, s):
        tennpc, x, y = NPCSUGIA
        # Thành viên cùng máy còn nhiệm vụ đã xong chưa trả: chờ họ trả (nhận lượt mới họ sẽ không theo được)
        chuatras = self._laythanhviencungmay(("xong",))
        if chuatras:
            s.setdefault("lucchotra", time.time())
            if time.time() - s["lucchotra"] < THOIGIANCHOTHANHVIENTRA:
                s["trangthai"] = f"chờ {', '.join(chuatras)} trả nhiệm vụ"
                return None
            self._baosugia(s, f"chuatra|{s['solan']}", f"⚠️ Sư Gia: {', '.join(chuatras)} chưa trả nhiệm vụ sau "
                                                        f"{int(THOIGIANCHOTHANHVIENTRA)}s, vẫn nhận lượt mới")
        else:
            s.pop("lucchotra", None)
        yeucau = self._toitusugia(s, "nhận nhiệm vụ")
        if yeucau is not False:
            return yeucau
        if s.get("lucnhan") and time.time() - s["lucnhan"] < THOIGIANCHONHIEMVUDOISUGIA:
            s["trangthai"] = "đã nhận, chờ cửa sổ nhiệm vụ"
            return None
        if s.get("lucnhan"):
            s.pop("lucnhan")
            s["thu"]["nhan"] = s["thu"].get("nhan", 0) + 1
            if s["thu"]["nhan"] >= SOLANTHUSUGIA:
                self._ketthucsugia(f"❌ Sư Gia dừng: nhận {SOLANTHUSUGIA} lần mà không có nhiệm vụ (xem log [PHÓ BẢN] Menu {tennpc})", is_loi = True)
                return None
            self._logsg(f"Nhận xong {THOIGIANCHONHIEMVUDOISUGIA:.0f}s chưa thấy nhiệm vụ, nói chuyện lại")
        s["trangthai"] = f"nhận nhiệm vụ ở {tennpc}"
        ketqua, yeucau = self._noichuyensugia(s, tennpc, x, y, is_chovankhi = False, luachon = (0, 0), kiemtramenu = self._kiemtramenusugia)
        if ketqua == "tuchoi":
            homnay = s.get("homnay") or ("?", "?")
            self._ketthucsugia(f"✅ Xong Sư Gia: hôm nay đã làm {homnay[0]}/{homnay[1]} lần")
            return None
        if ketqua == "xong":
            s["lucnhan"] = time.time()
            s["hoithoai"] = None
        return yeucau

    def _trasugia(self, s, nv):
        tennpc, x, y = NPCSUGIA
        s.update(truytim = None)
        yeucau = self._toitusugia(s, "trả nhiệm vụ")
        if yeucau is not False:
            return yeucau
        khoa = f"tra|{s['solan']}"
        if s.get("luctra") and time.time() - s["luctra"] < THOIGIANCHONHIEMVUDOISUGIA:
            s["trangthai"] = "đã trả, chờ cửa sổ nhiệm vụ"
            return None
        if s.get("luctra"):
            s.pop("luctra")
            s["thu"][khoa] = s["thu"].get(khoa, 0) + 1
            if s["thu"][khoa] >= SOLANTHUSUGIA:
                self._ketthucsugia(f"❌ Sư Gia dừng: trả {nv['ten']} {SOLANTHUSUGIA} lần mà nhiệm vụ không mất (xem log [PHÓ BẢN] Menu {tennpc})",
                                   is_loi = True)
                return None
        s["trangthai"] = f"trả {nv['ten']} ở {tennpc}"
        ketqua, yeucau = self._noichuyensugia(s, tennpc, x, y, is_chovankhi = False, luachon = (0, 0))
        if ketqua == "xong":
            s["luctra"] = time.time()
            s["hoithoai"] = None
        return yeucau

    # --- Tìm và giết tội phạm --------------------------------------------------------------------------------------------------------
    def _timdoituongtoipham(self, nv):
        # Tội phạm đang thấy (sống): tên đối tượng khớp "Tội Phạm Thích Đại Hắc" hoặc "Thích Đại Hắc" (bỏ phần ID trong ngoặc)
        moitruong = self.moitruong
        tens = {chuanhoaten(nv["toipham"]), chuanhoaten(nv["loi"])} - {""}
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi) or moitruong.get_is_nhanvatdachet(diachi):
                continue
            ten = moitruong.get_tendoituong(diachi) or ""
            if chuanhoaten(re.sub(r"\s*\(\d+\)\s*$", "", ten)) in tens and not moitruong.get_is_quairiengnguoikhac(ten):
                return diachi, ten
        return None, ""

    def _timtoipham(self, s, nv):
        moitruong = self.moitruong
        idbando = nv["bando"]
        if not idbando:
            self._ketthucsugia(f"❌ Sư Gia dừng: không biết nước \"{nv['nuoc']}\" trong mô tả nhiệm vụ là bản đồ nào", is_loi = True)
            return None
        tiendo = f" ({nv['tiendo'][0]}/{nv['tiendo'][1]})" if nv["tiendo"] else ""
        if moitruong.get_idbandohientai() != idbando:
            s["truytim"] = None
            s["trangthai"] = f"tới {laytenbando(idbando)} tìm {nv['toipham']}{tiendo}"
            buoc = self._lapbuocditoibando(idbando, is_hoithanhphu = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                return None
            return self._khongcatgocchu(self._thuchienbuocditoibando(buoc, idbando, None, "[SƯ GIA] Tìm tội phạm"))
        diachi, ten = self._timdoituongtoipham(nv)
        if diachi:
            toado = moitruong.get_toado(diachi)
            if not s.get("dathay"):
                s["dathay"] = True
                self._logsg(f"Thấy {ten} ở {toado}")
                self._dohuongtruytim(s, toado)
            # Chờ đông đủ thành viên rồi mới đánh
            vangs = self._laythanhvienvangsugia(s)
            if vangs:
                s["dudoi"] = False
                return self._chothanhviensugia(s, ten, vangs)
            if not s["dudoi"]:
                if s["lucchodoi"]:
                    self._logsg(f"Đủ thành viên sau {int(time.time() - s['lucchodoi'])}s, đánh {ten}")
                s.update(dudoi = True, lucchodoi = 0.)
            s["truytim"] = None
            s["chedo"] = "danhquai"
            s["tenquai"] = {ten}
            self._batdanhquaisugia(s)
            s["trangthai"] = f"đánh {ten}{tiendo}"
            if moitruong.get_khoangcach(diachi) > KHOANGCACHTOITOIPHAM:
                return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (*toado, idbando), "khoangcachtoida": 3.}
            return None
        s["dathay"] = False
        return self._buoctruytim(s, nv, idbando, tiendo)

    def _ghithanhviensugia(self, s):
        # Mọi người từng ở trong nhóm trong lượt này (id -> tên): rớt khỏi nhóm vẫn nhớ để chờ trước khi đánh tội phạm
        moitruong = self.moitruong
        idtoi = moitruong.get_idnguoichoi()
        for idtv in moitruong.get_danhsachidnguoichoithanhviennhoms() or () if moitruong.get_is_dangnamtrongnhom() else ():
            if idtv and idtv != idtoi and not s["thanhviens"].get(idtv):
                diachi = moitruong.action_timkiemnhanvat(idnguoichoi = idtv)
                s["thanhviens"][idtv] = (moitruong.get_tendoituong(diachi) if diachi else "") or self._laytencungmay(idtv)

    def _laythanhvienvangsugia(self, s):
        # Thành viên lượt này chưa có mặt: [(id, tên, lý do)]. Chưa đủ lần nào (dudoi False) thì phải đứng trong KHOANGCACHTHANHVIENSUGIA ô;
        # đủ rồi (đang đánh) chỉ tính người rời nhóm / không thấy / đã chết
        moitruong = self.moitruong
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if moitruong.get_is_dangnamtrongnhom() else set()
        vangs = []
        for idtv, ten in s["thanhviens"].items():
            ten = ten or self._laytencungmay(idtv) or f"ID {idtv}"
            if idtv not in trongnhoms:
                vangs.append((idtv, ten, "không còn trong nhóm"))
                continue
            diachi = moitruong.action_timkiemnhanvat(idnguoichoi = idtv)
            if not diachi:
                vangs.append((idtv, ten, "chưa tới"))
            elif moitruong.get_is_nhanvatdachet(diachi):
                vangs.append((idtv, ten, "đã chết"))
            elif not s["dudoi"] and moitruong.get_khoangcach(diachi) > KHOANGCACHTHANHVIENSUGIA:
                vangs.append((idtv, ten, f"chưa tới gần (cần trong {KHOANGCACHTHANHVIENSUGIA:.0f} ô)"))
        return vangs

    def _chothanhviensugia(self, s, ten, vangs):
        # Đứng yên, không đánh (cả thành viên theo sau cùng máy: get_is_camdanhsugia), mời lại người rời nhóm
        moitruong = self.moitruong
        now = time.time()
        s["chedo"] = "cho"
        if not s["lucchodoi"]:
            s["lucchodoi"] = now
            self._logsg(f"Thấy {ten}, chờ đủ thành viên mới đánh: {', '.join(f'{t} ({l})' for _, t, l in vangs)}")
        self.get_is_camdanhsugia()
        moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
        for idtv, _, lydo in vangs:
            if lydo == "không còn trong nhóm" and now - s["lucmoi"].get(idtv, 0.) > GIANCACHMOILAISUGIA:
                s["lucmoi"][idtv] = now
                moitruong.action_moihoacxinvaonhom(idtv)
        s["trangthai"] = f"thấy {ten}, chờ đủ người mới đánh: " + ", ".join(f"{t} {l}" for _, t, l in vangs)
        if now - s["lucchodoi"] > THOIGIANBAOCHOTHANHVIENSUGIA:
            self._baosugia(s, f"chodoi|{s['solan']}|{int(s['lucchodoi'])}",
                           f"⚠️ Sư Gia: chờ {int(THOIGIANBAOCHOTHANHVIENSUGIA // 60)} phút chưa đủ người để đánh {ten}: "
                           + ", ".join(f"{t} ({l})" for _, t, l in vangs))
        return None

    def get_is_sugiachothanhvien(self):
        # Theo mốc bắt đầu chờ chứ không theo chedo (chedo mỗi lượt đặt lại từ đầu, thành viên đọc qua shared_data giữa chừng bị chập chờn)
        return bool(self._sugia) and bool(self._sugia["lucchodoi"]) and not self._sugia["dudoi"]

    def get_is_camdanhsugia(self):
        # Không được đánh: mình đang chờ đủ thành viên, hoặc người mình theo sau (cùng máy) đang chờ và mình cũng ở bản đồ đó. Đang đánh
        # thường ("kill") thì ngắt luôn
        is_cam = self.get_is_sugiachothanhvien()
        if not is_cam and self._is_tudongtheosau:
            info = self._laythongtinmuctieutheosaucuasokhac()
            is_cam = bool(info and info.get("_sugiachothanhvien") and info.get("tenbando") == self.moitruong.get_idbandohientai())
        if is_cam and self._is_battudongtancongvatly and self._diachimuctieutancongvatly:
            self._ngattancongvatlydaohoa(self._diachimuctieutancongvatly)
        return is_cam

    def _batdanhquaisugia(self, s):
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            if getattr(self, thuoctinh) != giatri:
                s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
                setattr(self, thuoctinh, giatri)
                self._logsg(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" để đánh tội phạm (dừng thì trả lại)")

    def _buoctruytim(self, s, nv, idbando, tiendo):
        # Truy Tìm Thổ Phỉ -> đọc tin -> đi theo hướng một quãng -> truy tìm lại. Không đọc được tin thì đi dò khắp bản đồ
        moitruong = self.moitruong
        now = time.time()
        t = s["truytim"]
        if not t:
            t = s["truytim"] = {"luc": 0., "dich": None, "lucdich": 0., "solanloi": 0, "hangtruoc": None, "xathem": 0, "chodoc": False}
        if t["solanloi"] >= SOLANTRUYTIMLOI:
            self._baosugia(s, "khongtin", f"⚠️ Sư Gia: dùng Truy Tìm Thổ Phỉ (\"{LENHTRUYTIM}\") {SOLANTRUYTIMLOI} lần không thấy tin "
                                          f"\"Bạn bám sát...\": đi dò khắp {laytenbando(idbando)}")
            s["trangthai"] = f"dò khắp {laytenbando(idbando)} tìm {nv['toipham']}{tiendo} (Truy Tìm không có tin)"
            if now - t["luc"] > 60.:
                # Thỉnh thoảng vẫn thử lại Truy Tìm
                t["solanloi"] = SOLANTRUYTIMLOI - 1
            return self._diquadiem(s, f"sugia|{idbando}", idbando, laydiemkhampha(idbando), f"tìm {nv['toipham']}")
        if t["chodoc"]:
            ketqua = self._doctintruytimmoi(t["luc"])
            if ketqua:
                t["chodoc"] = False
                t["solanloi"] = 0
                self._nhantintruytim(s, t, ketqua, nv)
            elif now - t["luc"] > THOIGIANCHOTINTRUYTIM:
                t["chodoc"] = False
                t["solanloi"] += 1
                self._logsg(f"Truy Tìm lần {t['solanloi']}: {THOIGIANCHOTINTRUYTIM:.0f}s không thấy tin")
            else:
                s["trangthai"] = f"Truy Tìm {nv['toipham']}: chờ tin{tiendo}"
                return None
        dich = t["dich"]
        is_toi = is_ket = False
        if dich:
            # Quãng đi bộ thật tới đích (loang trên lưới từ đích, tính 1 lần mỗi đích): đi vòng qua sông lúc đầu xa thêm theo đường chim bay
            # vẫn là đang gần lại
            if t.get("truong") is None:
                luoi = moitruong.get_luoivatcanbando()
                t["truong"] = (layvungtoiduoc(luoi, dich) if luoi else None) or {}
            khoangcach = moitruong.get_khoangcachdiem(*dich)
            is_toi = khoangcach <= 3.
            o = moitruong.get_oditduocganhat(*moitruong.get_toado())
            khoangcach = t["truong"].get(tuple(o), khoangcach)
            if khoangcach < t.get("ganhat", float("inf")) - 2:
                t.update(ganhat = khoangcach, lucgan = now)
            is_ket = now - t.get("lucgan", now) > THOIGIANKHONGGANHON
        if (not dich or is_toi or is_ket or now - t["lucdich"] > THOIGIANMOIHUONG) and now - t["luc"] >= GIANCACHTRUYTIM:
            if dich and not is_toi:
                self._logsg(f"Chưa tới {dich} ({'kẹt, không gần thêm' if is_ket else 'đi quá lâu'}), truy tìm lại")
            moitruong.action_ngatdichuyen()
            moitruong.action_thucthicaulenh(LENHTRUYTIM)
            t.update(luc = now, chodoc = True, dich = None)
            s["trangthai"] = f"Truy Tìm {nv['toipham']}{tiendo}"
            return None
        if not dich:
            return None
        s["trangthai"] = f"đi theo Truy Tìm ({t.get('mota', '')}) tới {dich}{tiendo}"
        self._capnhatbuocdichuyen(f"Sư Gia: truy tìm {nv['toipham']} -> {dich}")
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (*dich, idbando), "khoangcachtoida": 1.,
                "is_dioo": self._is_dioo(idbando)}

    def _doctintruytimmoi(self, tu):
        # Tin Truy Tìm vào khung trò chuyện từ lúc tu (nối các dòng lại: tin dài bị cắt làm 2 dòng)
        dongs = [noidung for luc, noidung in list(self.moitruong.get_lichsutrochuyen5s()) if luc >= tu - 0.2 and noidung]
        return doctintruytim(" ".join(dongs)) if dongs else None

    def _nhantintruytim(self, s, t, ketqua, nv):
        moitruong = self.moitruong
        hang, tendoxa, huong = ketqua
        toado = moitruong.get_toado()
        s["mau"].append((toado, huong))
        s["mau"] = s["mau"][-40:]
        # Chưa đo được cách đổi hướng: đi theo cách đang thử mà tin báo xa thêm SOLANXATHEM lần liền thì đổi cách khác
        if not s["is_dadohuong"] and t["hangtruoc"] is not None:
            if hang > t["hangtruoc"]:
                t["xathem"] += 1
                if t["xathem"] >= SOLANXATHEM:
                    s["huong"] = (s["huong"] + 1) % len(HUONGs)
                    t["xathem"] = 0
                    self._logsg(f"Đi theo hướng mà xa thêm {SOLANXATHEM} lần: thử cách đổi hướng khác {HUONGs[s['huong']]}")
            elif hang < t["hangtruoc"]:
                t["xathem"] = 0
        t["hangtruoc"] = hang
        buoc = DOXAs[hang][1]
        dong, bac = HUONG_MAP[huong]
        dx, dy = doihuong(dong, bac, s["huong"])
        dodai = math.hypot(dx, dy) or 1.
        dich = self._chondiemtruytim(toado, dx / dodai, dy / dodai, buoc) \
               or self._laydiemditoi(toado[0] + dx / dodai * buoc, toado[1] + dy / dodai * buoc)
        if math.dist(dich, toado) < max(3., buoc / 3):
            # Không đi được về phía đó (mép bản đồ / vật cản): cách đổi hướng có thể sai (từng đứng ở mép trên truy tìm mãi). Chưa đo được thì
            # đổi cách khác; đã đo được thì đi dò quanh một quãng
            t["ketmep"] = t.get("ketmep", 0) + 1
            if not s["is_dadohuong"] and t["ketmep"] >= SOLANXATHEM:
                s["huong"] = (s["huong"] + 1) % len(HUONGs)
                t.update(ketmep = 0, xathem = 0)
                self._logsg(f"Không đi được về phía {huong} từ {tuple(round(v) for v in toado)}: thử cách đổi hướng khác {HUONGs[s['huong']]}")
            goc = (t["ketmep"] * 2.4) % (2 * math.pi)
            dich = self._laydiemditoi(toado[0] + math.cos(goc) * buoc, toado[1] + math.sin(goc) * buoc)
        else:
            t["ketmep"] = 0
        t.update(dich = dich, lucdich = time.time(), lucgan = time.time(), ganhat = float("inf"), truong = None,
                 mota = f"{tendoxa}, phía {huong}")
        self._logsg(f"Truy Tìm {nv['toipham']}: {tendoxa}, phía {huong} (đứng {tuple(round(v) for v in toado)}) -> đi {buoc} ô tới {dich}")

    def _chondiemtruytim(self, toado, ux, uy, buoc):
        # Ô tới được nằm trong hình quạt ±GOCQUATTRUYTIM độ theo hướng (ux, uy), cách chỗ đứng [buoc x TYLEGANTRUYTIM, buoc x TYLEXATRUYTIM]
        # ô, chọn ô ít bước đi bộ nhất. Tội phạm bên kia sông / tường: ô gần điểm ước tính theo đường chim bay là mép bờ bên này (từng
        # đứng mãi ở bờ sông Tần Quốc "rất gần, phía nam"), còn ô trong quạt ít bước nhất thì ở bờ bên kia, đi vòng qua cầu.
        # -> (x, y) hoặc None (không đọc được lưới / quạt không có ô nào)
        # Số bước tính từ chỗ đứng bây giờ (_layvungtoiduoc nhớ số bước từ chỗ đứng lúc tính, chỉ tính lại khi ra khỏi vùng)
        luoi = self.moitruong.get_luoivatcanbando()
        vung = layvungtoiduoc(luoi, self.moitruong.get_oditduocganhat(*toado)) if luoi else None
        if not vung:
            return None
        # Quạt không có ô đi được (dải sông / kè đá dày hơn tầm: Tần Quốc "rất gần, phía nam" mà phía nam là dải đá ~24 ô) thì nới tầm xa
        # dần, ô ở bờ bên kia đi vòng tới được
        cosgoc = math.cos(math.radians(GOCQUATTRUYTIM))
        gan = buoc * TYLEGANTRUYTIM
        for tyle in (1, 2, 3, 5):
            xa = buoc * TYLEXATRUYTIM * tyle
            tot = None
            for (x, y), sobuoc in vung.items():
                vx, vy = x - toado[0], y - toado[1]
                d = math.hypot(vx, vy)
                if not gan <= d <= xa or (vx * ux + vy * uy) < cosgoc * d:
                    continue
                khoa = (sobuoc, -(vx * ux + vy * uy) / d)
                if tot is None or khoa < tot[0]:
                    tot = (khoa, (x, y))
            if tot:
                if tyle > 1:
                    self._logsg(f"Hướng truy tìm gần không có ô đi được, nới tầm x{tyle}: tới {tot[1]} ({tot[0][0]} bước)")
                return tot[1]
        return None

    def _laydiemditoi(self, x, y):
        # Ô đi tới được (cùng vùng với chỗ đứng) gần (x, y) nhất; không đọc được lưới thì ô đi được gần nhất
        vung = self._layvungtoiduoc(self.moitruong.get_idbandohientai())
        if not vung:
            return self.moitruong.get_oditduocganhat(x, y)
        return min(vung, key = lambda o: (o[0] - x) ** 2 + (o[1] - y) ** 2)

    def _dohuongtruytim(self, s, toadotoipham):
        # Thấy tội phạm: so mọi lần đọc tin (chỗ đứng, hướng) với chỗ tội phạm, chọn cách đổi hướng khớp nhiều nhất, lưu cho lần sau
        maus = [(tdo, h) for tdo, h in s["mau"] if math.dist(tdo, toadotoipham) > 8]
        if len(maus) < 2:
            return
        def diem(i):
            tong = 0.
            for (x, y), h in maus:
                dx, dy = doihuong(*HUONG_MAP[h], i)
                vx, vy = toadotoipham[0] - x, toadotoipham[1] - y
                tong += (dx * vx + dy * vy) / ((math.hypot(dx, dy) or 1.) * (math.hypot(vx, vy) or 1.))
            return tong / len(maus)
        diems = [diem(i) for i in range(len(HUONGs))]
        tot = max(range(len(HUONGs)), key = lambda i: diems[i])
        self._logsg(f"Đo hướng Truy Tìm từ {len(maus)} lần đọc: cách {HUONGs[tot]} khớp {diems[tot]:.2f} (1 = khớp hẳn); mẫu: "
                    f"{[(tuple(round(v) for v in tdo), h) for tdo, h in maus[-6:]]}, tội phạm {tuple(round(v) for v in toadotoipham)}")
        if diems[tot] >= 0.7:
            s["huong"], s["is_dadohuong"] = tot, True
            _luuhuong(tot)

    # --- Thành viên --------------------------------------------------------------------------------------------------------------------
    def _nhanmoisugia(self):
        # Trưởng nhóm vừa nhận: menu "<tên> đã nhận nhiệm vụ rồi, ngươi muốn làm gì đây? 1. Nhận 2. Rời khỏi" -> chọn "1. Nhận".
        # -> True khi đang có menu đó (vừa chọn / chờ)
        moitruong = self.moitruong
        if not moitruong.get_is_danghiencuasotuychon():
            return False
        noidung = moitruong.get_noidungcuasotuychon() or ""
        if "đã nhận nhiệm vụ rồi" not in noidung.lower():
            return False
        if time.time() - self._lucnhanmoisugia < 2.:
            return True
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        if not lenhs:
            return False
        self._lucnhanmoisugia = time.time()
        moitruong.xoa_noidungcuasotuychon()
        moitruong.action_thucthicaulenh(lenhs[0])
        self._logsg(f"Trưởng nhóm đã nhận nhiệm vụ: chọn Nhận ({lenhs[0]!r})")
        return True

    def _xulysugiathanhvien(self, is_tubat = False):
        # Thành viên: nhận theo trưởng nhóm, nhiệm vụ của mình xong thì ở Chu Quốc tới Từ Phúc tự trả. Chạy khi mình bật Sư Gia (is_tubat)
        # hoặc người mình theo sau (cùng máy) đang làm Sư Gia. -> False: không có gì phải làm (theo sau như thường); None / yêu cầu di
        # chuyển: đang làm
        moitruong = self.moitruong
        if not is_tubat:
            info = self._laythongtinmuctieutheosaucuasokhac()
            if not (info and info.get("_is_dangsugia")):
                self._sugiathanhvien = None
                return False
        if moitruong.get_is_nhanvatdachet():
            return False
        if self._nhanmoisugia():
            return None
        if moitruong.get_is_dangvankhi() or time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return False
        nv = laynhiemvusugia(moitruong.get_danhsachmucnhiemvu())
        s = self._sugiathanhvien
        if nv and not nv["is_comota"] and not nv["is_xong"]:
            # Mô tả trống thì không biết tiến độ (đã giết chưa): xin mô tả
            self._xinmotasugia(nv)
        if not is_xongsugia(nv):
            if s and s.get("luctra"):
                self._logsg("Thành viên: đã trả nhiệm vụ")
            self._sugiathanhvien = None
            return False
        if not s or s["ten"] != nv["ten"]:
            s = self._sugiathanhvien = {"ten": nv["ten"], "hoithoai": None, "luctra": 0., "solan": 0, "trangthai": ""}
        if moitruong.get_idbandohientai() != BANDONPCSUGIA:
            # Theo sau thì trưởng nhóm dẫn về; tự bật mà không theo sau thì tự về
            return self._toitusugia(s, "trả nhiệm vụ") if is_tubat and not self._is_tudongtheosau else False
        if s["luctra"] and time.time() - s["luctra"] < THOIGIANCHONHIEMVUDOISUGIA:
            return None
        if s["solan"] >= SOLANTHUSUGIA:
            if s["solan"] == SOLANTHUSUGIA:
                s["solan"] += 1
                baosuco(moitruong, "sumon", f"⚠️ Sư Gia: thành viên trả {nv['ten']} {SOLANTHUSUGIA} lần mà nhiệm vụ không mất (trả tay giúp)",
                        khoa = f"sugiatv|{nv['ten']}", giancach = 0.)
            return False
        tennpc, x, y = NPCSUGIA
        self._capnhatbuocdichuyen(f"Sư Gia: tới {tennpc} trả nhiệm vụ")
        ketqua, yeucau = self._noichuyensugia(s, tennpc, x, y, is_chovankhi = False, luachon = (0, 0))
        if ketqua == "xong":
            s.update(luctra = time.time(), hoithoai = None, solan = s["solan"] + 1)
            self._logsg(f"Thành viên: trả {nv['ten']} ở {tennpc} (lần {s['solan']})")
        return yeucau
