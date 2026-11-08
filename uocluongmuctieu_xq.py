"""Ước lượng Khí Huyết tối đa và Kháng của mục tiêu đang chọn từ sát thương mình gây ra (chạy trong bot, luồng riêng mỗi cửa sổ).
Giao diện gộp kết quả mọi cửa sổ cùng đánh 1 mục tiêu (nhân vật hệ Ngoại ra Ngoại Kháng, hệ Nội ra Nội Kháng) để hiện ở đầu tab
Chiến đấu. Công thức: congthucsatthuong_xq.

- Mỗi đòn: số bay mới trên mục tiêu trong client của mình (MoiTruong.get_sobaydoituong; client chỉ hiện số của chính mình) + Công
  trên bảng lúc đó => Kháng suy ra (khangtusatthuong) nếu coi là đòn thường không bạo.
- Gán chiêu cho đòn: chiêu "pf <id>" bot gửi gần nhất trong THOIGIANGANCHIEU giây trước đòn (MoiTruong._lenhbotganday), không có thì
  coi là đánh thường. Phần cộng của chiêu đọc từ mô tả ô kỹ năng (cấp hiện tại): "tăng thêm X điểm Ngoại/Nội Công" cộng vào Công,
  "bỏ qua X% phòng thủ" nhân Kháng (1 - X); chiêu tính theo nguyên khí / % Công (Khí Tráng Sơn Hà, Lôi Động) bỏ đòn đó.
- Đòn gán sai (đánh thường tự động xen giữa chiêu), bạo kích, bị đỡ cho Kháng lệch hẳn, còn đòn gán đúng cho cùng 1 Kháng => lấy
  cụm (±BEROCUM) đông đòn nhất, ít nhất SODONTOITHIEUCUM đòn, hoà thì cụm Kháng cao hơn (bạo kích luôn kéo xuống). Kiểm 882 đòn
  đo 2026-11-05: khi có đòn thường xen vào thì lệch Kháng thật dưới 1%. Chỉ dùng toàn 1 chiêu cộng Công mà gán không ra chiêu
  (chiêu có độ trễ hơn THOIGIANGANCHIEU) thì Kháng ra thấp hơn thật.
- Khí Huyết tối đa: client chỉ có % máu mục tiêu (bước 2%) => tổng sát thương / phần % tụt. Giao diện cộng sát thương của mọi cửa
  sổ cùng đánh; người ngoài cùng đánh => ra thấp hơn thật. Máu mục tiêu hồi lên (> 2%) thì đo lại đoạn mới.
"""
import collections
import re
import threading
import time
import unicodedata

from congthucsatthuong_xq import HE_NGOAI, HE_NOI, HEMONPHAI_MAP, chonhe, congtusatthuong, khangtusatthuong, satthuong
from tienich_xq import PHIENBANSODO
from hangso_xq import (CHISONHANVAT_MAP, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG,
                       LOAIMUCTIEU_NGUOICHOIKHACNHOM)

CHUKYDOC = 0.03
# Nhớ bấy nhiêu mục tiêu gần nhất (đổi qua lại vẫn giữ số đã đo), bỏ mục tiêu không đánh quá THOIGIANNHOMUCTIEU giây
SOMUCTIEUNHO = 8
THOIGIANNHOMUCTIEU = 600.
# Mỗi mục tiêu giữ bấy nhiêu đòn gần nhất (Kháng đổi theo buff / phá giáp nên không giữ mãi)
SODONGIU = 120
SODONTOITHIEUCUM = 3
BEROCUM = 0.03
# Máu mục tiêu phải tụt ít nhất chừng này % mới ước Khí Huyết tối đa (bước % máu 2 => sai mỗi đầu ±1%)
MAUTUTTOITHIEU = 6.
# Máu hồi lên quá chừng này % so với lần đọc trước: bắt đầu đoạn đo máu mới
MAUHOIBATLAI = 2.
# % máu tụt mà cửa sổ này không có số bay nào trong ±chừng này giây = người khác / bảo thú đánh => Khí Huyết của đoạn đó ra thấp
# (kho quái cũ 2026-11-07 có Kiến Đen 10, Xích Hậu 2, Độc Nhãn Thú 3 Khí Huyết). Đếm vào "sobackhac" của đoạn, kho không lưu
THOIGIANGANBAC = 1.
DICHCONG = (CHISONHANVAT_MAP["Ngoại Công"][0], CHISONHANVAT_MAP["Nội Công"][0])
# Đòn tới sau lệnh chiêu trong chừng này giây thì coi là của chiêu đó (chiêu có delay Đào Hoa ra số bay sau 0.28-0.53s, đo 2026-10-28)
THOIGIANGANCHIEU = 0.8
# Đọc lại mô tả chiêu sau chừng này giây (lên cấp chiêu thì phần cộng đổi)
THOIGIANNHOMOTACHIEU = 120.
# Xét hỏi môn phái / bang phái mục tiêu người chơi mỗi chừng này giây
CHUKYHOITHONGTIN = 1.

# Đo Công đối thủ từ máu mình tụt: kẻ đang đánh mình = đối tượng trong BANKINHKETANCONG ô, tư thế ra đòn và quay mặt về mình
# (moitruong.get_is_huongmatvediem, cùng cách tactu._laydanhsachketancong / thongbao báo bị PK), quét mỗi CHUKYDOKETANCONG giây và nhớ
# THOIGIANNHODANH giây (tư thế nhấp nháy giữa các đòn). Máu tụt mà đúng 1 kẻ đang đánh và đó là người chơi khác nhóm thì gán đòn cho
# người đó; nhiều kẻ cùng đánh / có quái đánh thì bỏ (không biết của ai)
BANKINHKETANCONG = 12.
CHUKYDOKETANCONG = 0.1
THOIGIANNHODANH = 1.5
TUTHERADONs = (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG)
DICHKHANG = (CHISONHANVAT_MAP["Ngoại Kháng"][0], CHISONHANVAT_MAP["Nội Kháng"][0])
SODOITHUNHO = 8
# Số loại quái (tên + cấp) gom đòn Kháng / Công cùng lúc (xem UocLuongMucTieu._donsquai)
SOLOAIQUAINHO = 24


# Đòn đã gán cho chiêu vẫn thử thêm giả thuyết "đánh thường" (đánh thường tự động rơi trúng lúc vừa gửi chiêu) với trọng số thấp
# hơn: đòn thường khớp cụm đúng qua giả thuyết này, còn toàn chiêu thì cụm theo chiêu vẫn thắng. Kiểm phát lại 2026-11-05: Hắc Hổ /
# Đại Hải / Nhất Quyền xen đánh thường, Tiên Nhân Chỉ Lộ toàn chiêu đều ra Kháng lệch dưới 1%
TRONGSODANHTHUONGKHIGANCHIEU = 0.9

# Nhịp đánh / DPS: chỉ tính khoảng giữa 2 đòn liền nhau cách nhau không quá chừng này giây (lâu hơn là đã ngừng đánh, chạy, đổi mục tiêu)
KHOANGDONLIENTOIDA = 5.
# Cần ít nhất chừng này khoảng liền nhau mới ra nhịp / DPS
SOKHOANGTOITHIEU = 3
# Mục tiêu có đòn của mình trong chừng này giây gần nhất = đang đánh (DPS đo trực tiếp dùng được cho kết luận)
THOIGIANDANGDANH = 6.


def nhiptheoluc(cacluc):
    # Các lúc ra đòn (tăng dần) -> (số đòn / giây khi đang đánh, số khoảng liền nhau); nhiều số bay cùng 1 lúc đọc tính là 1 đòn
    khoangs = [b - a for a, b in zip(cacluc, cacluc[1:]) if 0 < b - a <= KHOANGDONLIENTOIDA]
    if len(khoangs) < SOKHOANGTOITHIEU:
        return None, len(khoangs)
    return len(khoangs) / sum(khoangs), len(khoangs)


def dpstheodon(cacdon):
    # [(lúc, sát thương)] tăng dần theo lúc -> (sát thương / giây khi đang đánh, số khoảng): cộng sát thương các lúc nối tiếp 1 khoảng
    # liền nhau, chia tổng các khoảng đó (đòn mở đầu sau lúc nghỉ không tính vì không biết bắt đầu đánh lúc nào)
    tong, thoigian, sokhoang = 0., 0., 0
    for (a, _), (b, st) in zip(cacdon, cacdon[1:]):
        if b == a:
            tong += st
        elif b - a <= KHOANGDONLIENTOIDA:
            tong += st
            thoigian += b - a
            sokhoang += 1
    if sokhoang < SOKHOANGTOITHIEU or thoigian <= 0:
        return None, sokhoang
    return tong / thoigian, sokhoang


def khoaquaitheoten(tenday):
    # Tên đầy đủ trong game "Thủ Lĩnh Thích Khách ( 29 ) ( Cấp 102)" -> "Thủ Lĩnh Thích Khách|102" (khoá lưu chỉ số quái cùng tên và
    # cấp, _internal/thongtinquai.json); bỏ mọi cụm "( ... )" (ID chủ quái nhiệm vụ). Không có cấp -> ""
    tenday = unicodedata.normalize("NFC", re.sub(r"\x1b.", "", tenday or ""))
    cap = re.search(r"\(\s*[Cc]ấp\s*(\d+)\s*\)", tenday)
    if not cap:
        return ""
    ten = re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", "", tenday)).strip()
    return f"{ten}|{cap.group(1)}" if ten else ""


def khangtheocum(dons):
    # dons: mỗi đòn là [(Kháng suy ra, trọng số)] theo các giả thuyết. Cụm rộng ±BEROCUM có tổng trọng số lớn nhất (mỗi đòn tính 1 lần,
    # lấy giả thuyết trọng số cao nhất trong cụm), cần >= SODONTOITHIEUCUM đòn -> (trung vị cụm, số đòn), không có -> (None, 0)
    diems = sorted((k, w, i) for i, gts in enumerate(dons) for k, w in gts if k)
    tot = (0., 0, None)
    for j, (k, _, _) in enumerate(diems):
        theodon = {}
        for x, w, i in diems[j:]:
            if x > k * (1. + 2 * BEROCUM):
                break
            if w > theodon.get(i, (0, 0))[0]:
                theodon[i] = (w, x)
        diem = sum(w for w, _ in theodon.values())
        if diem > tot[0] + 1e-9:
            giatris = sorted(x for _, x in theodon.values())
            tot = (diem, len(theodon), giatris[len(giatris) // 2])
    return (tot[2], tot[1]) if tot[1] >= SODONTOITHIEUCUM else (None, 0)


def congtheocum(congs):
    # Công đối thủ: cụm (±BEROCUM) đông nhất, hoà thì cụm THẤP hơn (bạo kích / chiêu cộng Công của họ đều đẩy Công suy ra lên cao,
    # đòn bị pháp bảo mình đỡ thì thấp nhưng lẻ tẻ) -> (trung vị cụm, số đòn) hoặc (None, 0)
    giatris = sorted(c for c in congs if c)
    tot = (0, None)
    for i, c in enumerate(giatris):
        cum = [x for x in giatris[i:] if x <= c * (1. + 2 * BEROCUM)]
        if len(cum) > tot[0]:
            tot = (len(cum), cum[len(cum) // 2])
    return (tot[1], tot[0]) if tot[0] >= SODONTOITHIEUCUM else (None, 0)


def phancongchieu(mota):
    # Mô tả ô kỹ năng -> (Công cộng thêm, phần phòng thủ bỏ qua) của cấp hiện tại; None nếu chiêu tính theo cách không suy ra được
    mota = unicodedata.normalize("NFC", mota or "").split("Cấp tiếp theo")[0]
    if re.search(r"mỗi (?:lần|điểm) tiêu hao|％ Nội Công của|% Nội Công của|％ Ngoại Công của|% Ngoại Công của", mota):
        return None
    congthem = re.search(r"tăng thêm (\d+) điểm (?:Ngoại|Nội) Công|(?:Ngoại|Nội) Công tăng thêm (\d+)", mota)
    boqua = re.search(r"bỏ qua (\d+)\s*[％%] phòng thủ", mota)
    return (int(next(g for g in congthem.groups() if g)) if congthem else 0, int(boqua.group(1)) / 100. if boqua else 0.)


class UocLuongMucTieu:
    def __init__(self, moitruong):
        self.moitruong = moitruong
        self._khoa = threading.Lock()
        # id đối tượng -> {ten, lucdanh, dons [(Kháng suy ra hoặc None)], tongst, doan [tổng ST đầu đoạn, % đầu đoạn], maucuoi}
        self._muctieus = collections.OrderedDict()
        self._diachi = None
        self._id = 0
        self._sobay = None
        # % máu mục tiêu đang chọn lần đọc trước (biết mục tiêu còn đầy máu ngay trước đòn đầu của mình)
        self._mautruoc = None
        # id chiêu -> (lúc đọc, (Công cộng thêm, phần bỏ qua phòng thủ) hoặc None)
        self._phancongchieu_map = {}
        self._luchoithongtin = 0.
        # Đo Công đối thủ: {id đối tượng: (lúc thấy ra đòn về mình, ID người chơi hoặc 0 nếu quái / bảo thú, tên)}, máu mình lần trước,
        # {ID người chơi: {ten, dons [(sát thương, Ngoại Kháng mình, Nội Kháng mình)], lucdanh}}
        self._kedanh = {}
        self._lucquetkedanh = 0.
        self._mauminh = None
        self._doithus = collections.OrderedDict()
        # {id đối tượng: {ten, khoaquai, idnguoichoi, dons [(sát thương, Ngoại Kháng mình, Nội Kháng mình, lúc)], lucdanh}} mọi kẻ đã
        # đánh mình (quái + người chơi)
        self._bidanhs = collections.OrderedDict()
        # Sát thương / giây thật của mình chia cho sát thương 1 đòn thường theo công thức (mục tiêu đã biết Kháng) - "số đòn thường quy
        # đổi mỗi giây", để ước DPS lên mục tiêu chưa đánh: DPS ≈ hệ số * satthuong(Công mình, Kháng nó)
        self._hesodps = None
        # Đòn gom theo loại quái (khoaquai = tên + cấp), không theo từng con: quái thường chết sau 2-4 đòn nên 1 con không bao giờ đủ
        # SODONCHACCHAN đòn khớp => kho quái 2026-11-09 có 151 loại, 46 có Khí Huyết mà Nội Kháng 17, Ngoại Kháng 2. Cùng tên + cấp thì
        # cùng Kháng / Công, nên cộng đòn của mọi con cùng loại. {khoaquai: {"dons": [gts], "he": hệ}} và {khoaquai: [(st, NK, NộiK)]}
        self._donsquai = collections.OrderedDict()
        self._bidanhquai = collections.OrderedDict()

    def _ghiquai(self, kho, khoaquai, phantu, he = None):
        # Thêm 1 đòn vào kho gom theo loại quái (giữ SODONGIU đòn mới nhất, SOLOAIQUAINHO loại gần nhất); đổi hệ thì đo lại
        muc = kho.get(khoaquai)
        if muc is None or muc["he"] != he:
            muc = kho[khoaquai] = {"dons": collections.deque(maxlen = SODONGIU), "he": he}
        kho.move_to_end(khoaquai)
        muc["dons"].append(phantu)
        while len(kho) > SOLOAIQUAINHO:
            kho.popitem(last = False)

    def get_sharequai(self):
        # {khoaquai: {"khang": {hệ: (Kháng, số đòn cụm, số đòn)}, "cong": {hệ: (Công, số đòn cụm, số đòn)}}} gom mọi con cùng loại
        ketqua = {}
        with self._khoa:
            for khoaquai, muc in self._donsquai.items():
                khang, socum = khangtheocum(muc["dons"])
                if khang and muc["he"]:
                    ketqua.setdefault(khoaquai, {"khang": {}, "cong": {}})["khang"][muc["he"]] = (round(khang), socum, len(muc["dons"]))
            for khoaquai, muc in self._bidanhquai.items():
                for he, chiso in ((HE_NGOAI, 1), (HE_NOI, 2)):
                    giatri, socum = congtheocum([congtusatthuong(d[0], d[chiso], he) for d in muc["dons"]])
                    if giatri:
                        ketqua.setdefault(khoaquai, {"khang": {}, "cong": {}})["cong"][he] = (round(giatri), socum, len(muc["dons"]))
        return ketqua

    def _quetkedanh(self):
        # Ghi lúc từng đối tượng đang ra đòn quay mặt về mình (xem BANKINHKETANCONG)
        mt = self.moitruong
        x1, y1 = mt.get_toado()
        banthan = mt.get_diachicosothongtinnhanvat1()
        luc = time.time()
        for diachi in mt._get_diachidoituongxungquanhs():
            if diachi == banthan:
                continue
            x, y = mt.get_toado(diachi)
            if max(abs(x - x1), abs(y - y1)) > BANKINHKETANCONG or mt.get_idtuthenhanvat(diachi) not in TUTHERADONs \
                    or not mt.get_is_huongmatvediem(diachi, x1, y1):
                continue
            idnguoichoi = mt.get_idnguoichoi(diachi) if mt.get_idloainhanvat(diachi) == LOAIMUCTIEU_NGUOICHOIKHACNHOM else 0
            iddoituong = mt.get_iddoituong(diachi)
            cu = self._kedanh.get(iddoituong)
            # Khoá quái (tên + cấp) chỉ đọc lần đầu thấy
            khoaquai = cu[3] if cu else (khoaquaitheoten(mt._get_tenthucte(diachi)) if mt.get_is_quai(diachi) else "")
            self._kedanh[iddoituong] = (luc, idnguoichoi or 0, mt.get_tendoituong(diachi), khoaquai)
        self._kedanh = {k: v for k, v in self._kedanh.items() if luc - v[0] <= THOIGIANNHODANH}

    def _ghibidanh(self):
        # Máu mình tụt (máu tối đa không đổi) -> gán cho kẻ đang đánh nếu chỉ có 1: người chơi vào _doithus (Công theo ID), mọi kẻ
        # (cả quái) vào _bidanhs theo id đối tượng (Công + nhịp đánh, cho kết luận Nguy hiểm / An toàn và lưu chỉ số quái)
        mt = self.moitruong
        if time.time() - self._lucquetkedanh >= CHUKYDOKETANCONG:
            self._lucquetkedanh = time.time()
            self._quetkedanh()
        mau = (mt.get_sinhlucconlai(), mt.get_sinhluctoida())
        truoc, self._mauminh = self._mauminh, mau
        if not truoc or mau[0] is False or mau[1] != truoc[1] or mau[0] >= truoc[0]:
            return
        luc = time.time()
        kedanhs = [(k, v) for k, v in self._kedanh.items() if luc - v[0] <= THOIGIANNHODANH]
        if len(kedanhs) != 1:
            return
        iddoituong, (_, idnguoichoi, ten, khoaquai) = kedanhs[0]
        khang = mt.get_chisonhanvats(DICHKHANG)
        if not khang:
            return
        with self._khoa:
            bidanh = self._bidanhs.get(iddoituong)
            if bidanh is None:
                bidanh = self._bidanhs[iddoituong] = {"ten": ten, "khoaquai": khoaquai, "idnguoichoi": idnguoichoi,
                                                      "dons": collections.deque(maxlen = SODONGIU), "lucdanh": 0.}
            self._bidanhs.move_to_end(iddoituong)
            bidanh["dons"].append((truoc[0] - mau[0], khang[0], khang[1], luc))
            bidanh["lucdanh"] = luc
            if khoaquai:
                self._ghiquai(self._bidanhquai, khoaquai, (truoc[0] - mau[0], khang[0], khang[1]))
            while len(self._bidanhs) > SOMUCTIEUNHO:
                self._bidanhs.popitem(last = False)
        if not idnguoichoi:
            return
        with self._khoa:
            doithu = self._doithus.get(idnguoichoi)
            if doithu is None:
                doithu = self._doithus[idnguoichoi] = {"ten": ten, "dons": collections.deque(maxlen = SODONGIU), "lucdanh": 0.}
            self._doithus.move_to_end(idnguoichoi)
            doithu["dons"].append((truoc[0] - mau[0], khang[0], khang[1]))
            doithu["lucdanh"] = time.time()
            while len(self._doithus) > SODOITHUNHO:
                self._doithus.popitem(last = False)

    def get_sharecongdoithu(self):
        # {ID người chơi: {ten, monphai (mã), cong: {hệ: (Công, số đòn cụm, số đòn)}}} các người chơi đã đánh mình gần đây. Tính cả 2 hệ:
        # hệ thật theo môn phái (giao diện chọn), môn phái chưa rõ hệ (Thục Sơn đao / kiếm...) thì hiện cả 2
        ketqua = {}
        with self._khoa:
            for idnguoichoi, doithu in self._doithus.items():
                if time.time() - doithu["lucdanh"] > THOIGIANNHOMUCTIEU:
                    continue
                cong = {}
                for he, chiso in ((HE_NGOAI, 1), (HE_NOI, 2)):
                    giatri, socum = congtheocum([congtusatthuong(d[0], d[chiso], he) for d in doithu["dons"]])
                    if giatri:
                        cong[he] = (round(giatri), socum, len(doithu["dons"]))
                ketqua[idnguoichoi] = {"ten": doithu["ten"], "monphai": self.moitruong._monphainguoichoi_map.get(idnguoichoi), "cong": cong}
        return ketqua

    def _chieuvuagui(self, luc):
        # (Công cộng thêm, phần bỏ qua phòng thủ) của chiêu "pf <id>" bot gửi gần nhất trong THOIGIANGANCHIEU giây trước luc; không có
        # chiêu nào thì (0, 0.) = đánh thường; None = chiêu không suy ra được (bỏ đòn)
        try:
            lenhs = list(self.moitruong._lenhbotganday.items())
        except Exception:
            return 0, 0.
        gannhat = None
        for caulenh, lucgui in lenhs:
            if caulenh.startswith("pf ") and 0 <= luc - lucgui <= THOIGIANGANCHIEU and (not gannhat or lucgui > gannhat[1]):
                gannhat = (caulenh, lucgui)
        if not gannhat:
            return 0, 0.
        try:
            idchieu = int(gannhat[0].split()[1])
        except (IndexError, ValueError):
            return 0, 0.
        dadoc = self._phancongchieu_map.get(idchieu)
        if not dadoc or luc - dadoc[0] > THOIGIANNHOMOTACHIEU:
            dulieu = self.moitruong._docokynangtheoid(idchieu)
            mota = dulieu.replace(b"\x00", b"\n").decode("utf-8", "ignore") if dulieu else ""
            # Mô tả chưa nạp thì chưa biết: coi như không cộng, lần sau đọc lại
            dadoc = (luc if "(Cấp" in mota or "Tái sử dụng" in mota else 0., phancongchieu(re.sub(r"\x1b.", "", mota)))
            self._phancongchieu_map[idchieu] = dadoc
        return dadoc[1]

    def step(self):
        mt = self.moitruong
        self._ghibidanh()
        diachi = mt._get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachi or not mt.get_is_nhanvattontai(diachi):
            self._diachi, self._id, self._sobay = None, 0, None
            return
        iddoituong = mt.get_iddoituong(diachi)
        # Người chơi: hỏi "desc user" lấy môn phái / bang phái (moitruong tự giãn cách, chỉ hỏi lại sau 10 phút)
        if time.time() - self._luchoithongtin >= CHUKYHOITHONGTIN:
            self._luchoithongtin = time.time()
            if mt.get_is_nguoichoi(diachi):
                mt.action_hoithongtinnguoichoimuctieu(diachi)
        if diachi != self._diachi or iddoituong != self._id:
            self._diachi, self._id, self._sobay = diachi, iddoituong, mt.get_sobaydoituong(diachi)
            self._mautruoc = float(mt.get_phantramsinhlucconlai(diachi))
            return
        moi = mt.get_sobaydoituong(diachi)
        cu, self._sobay = self._sobay, moi or self._sobay
        mau = float(mt.get_phantramsinhlucconlai(diachi))
        mautruoc, self._mautruoc = self._mautruoc, mau
        if not moi or not cu:
            return
        sts = [moi[0][i] for i in range(10) if moi[0][i] > 0 and (moi[0][i] != cu[0][i] or moi[1][i] < cu[1][i])]
        with self._khoa:
            muctieu = self._muctieus.get(iddoituong)
            if muctieu is None:
                if not sts:
                    return
                # moc / mocsau: (tổng sát thương, % máu, tổng số đòn) ở lần % máu nhảy bậc đầu tiên / gần nhất của đoạn đo;
                # sobackhac: số bậc tụt trong đoạn không có đòn của mình gần đó (THOIGIANGANBAC), bacchogan: lúc bậc đang chờ đòn tới
                # idnguoichoi: ID người chơi cố định (tên đổi được), 0 nếu là quái / NPC -> giao diện lưu lâu dài theo ID này
                idnguoichoi = mt.get_idnguoichoi(diachi) if mt.get_is_nguoichoi(diachi) else 0
                # cacdon: (lúc, tổng số bay lần đọc đó) cho DPS; khoaquai: tên + cấp nếu là quái (lưu chỉ số quái)
                # Ngay trước đòn đầu mục tiêu còn 100% => mốc đầu đoạn đo là (0, 100%): đo được cả đoạn từ đầy máu (trước đây mốc đầu
                # là lần nhảy bậc sau đòn đầu, bot đánh 3-4 đòn chết thì đoạn chỉ 60-70% => quái hầu như không lưu được Khí Huyết)
                is_daymau = mautruoc is not None and mautruoc >= 100
                muctieu = self._muctieus[iddoituong] = {"ten": mt.get_tendoituong(diachi), "dons": collections.deque(maxlen = SODONGIU),
                                                        "tongst": 0, "moc": (0, 100., 0) if is_daymau else None, "mocsau": None,
                                                        "maucuoi": 100. if is_daymau else mau, "he": None,
                                                        "sodontong": 0, "lucdoncuoi": 0., "sobackhac": 0, "bacchogan": None,
                                                        "idnguoichoi": idnguoichoi or 0, "cacdon": collections.deque(maxlen = SODONGIU),
                                                        "khoaquai": khoaquaitheoten(mt._get_tenthucte(diachi)) if mt.get_is_quai(diachi) else ""}
            self._muctieus.move_to_end(iddoituong)
            luc = time.time()
            if sts:
                muctieu["sodontong"] += len(sts)
                muctieu["lucdoncuoi"] = luc
                # Số bay tới sau % máu (máy chủ gửi riêng): bậc đang chờ là của mình
                if muctieu["bacchogan"] and luc - muctieu["bacchogan"] <= THOIGIANGANBAC:
                    muctieu["bacchogan"] = None
                muctieu["cacdon"].append((time.time(), sum(sts)))
                cong = mt.get_chisonhanvats(DICHCONG)
                he = chonhe(mt.get_tenmonphai(), {"ngoaicong": cong[0], "noicong": cong[1]}) if cong else None
                phan = self._chieuvuagui(time.time())
                for st in sts:
                    muctieu["tongst"] += st
                    if not he or phan is None:
                        continue
                    muctieu["he"] = he
                    c = cong[0] if he == HE_NGOAI else cong[1]
                    gts = [(khangtusatthuong(st, c, he, phan[0], phan[1]), 1.)]
                    if phan != (0, 0.):
                        gts.append((khangtusatthuong(st, c, he), TRONGSODANHTHUONGKHIGANCHIEU))
                    muctieu["dons"].append(gts)
                    if muctieu["khoaquai"]:
                        self._ghiquai(self._donsquai, muctieu["khoaquai"], gts, he)
                muctieu["lucdanh"] = time.time()
            # Khí Huyết: chỉ tính giữa các lần % máu nhảy bậc (lúc đó máu vừa đi qua đúng mốc, sai số còn cỡ 1 đòn); hồi lên thì đo lại
            if muctieu["bacchogan"] and luc - muctieu["bacchogan"] > THOIGIANGANBAC:
                muctieu["sobackhac"] += 1
                muctieu["bacchogan"] = None
            if mau > muctieu["maucuoi"] + MAUHOIBATLAI:
                muctieu["moc"] = muctieu["mocsau"] = muctieu["bacchogan"] = None
                muctieu["sobackhac"] = 0
            elif 0 < mau < muctieu["maucuoi"]:
                # Về 0% thì bỏ: đòn kết liễu hiện đủ số dù máu còn ít hơn (Khí Huyết ra cao hơn thật)
                muctieu["mocsau"] = (muctieu["tongst"], mau, muctieu["sodontong"])
                if muctieu["moc"] is None:
                    muctieu["moc"] = muctieu["mocsau"]
                elif luc - muctieu["lucdoncuoi"] > THOIGIANGANBAC:
                    if muctieu["bacchogan"]:
                        muctieu["sobackhac"] += 1
                    muctieu["bacchogan"] = luc
            muctieu["maucuoi"] = mau
            while len(self._muctieus) > SOMUCTIEUNHO:
                self._muctieus.popitem(last = False)

    def get_share(self):
        # {id mục tiêu: tóm tắt} các mục tiêu mình đã đánh gần đây, cho giao diện gộp giữa các cửa sổ
        ketqua = {}
        cong = self.moitruong.get_chisonhanvats(DICHCONG)
        hesomoi = None
        with self._khoa:
            for iddoituong, muctieu in self._muctieus.items():
                if time.time() - muctieu.get("lucdanh", 0) > THOIGIANNHOMUCTIEU:
                    continue
                khang, socum = khangtheocum(muctieu["dons"])
                moc, mocsau = muctieu["moc"], muctieu["mocsau"]
                # Mốc đầu 100% có sẵn trước khi máu nhảy bậc lần đầu: chưa có đoạn
                if not mocsau:
                    moc = None
                dps, sokhoang = dpstheodon(list(muctieu["cacdon"]))
                # Hệ số DPS theo mục tiêu đánh gần nhất đã biết Kháng (đủ đòn)
                if dps and khang and cong and muctieu["he"] and sokhoang >= SODONLUUTOITHIEU:
                    c = cong[0] if muctieu["he"] == HE_NGOAI else cong[1]
                    hesomoi = dps / max(satthuong(c, khang, muctieu["he"]), 1.)
                ketqua[iddoituong] = {
                    "khoaquai": muctieu.get("khoaquai", ""), "dps": round(dps) if dps else None, "sokhoangdps": sokhoang,
                    "ten": muctieu["ten"], "idnguoichoi": muctieu["idnguoichoi"],
                    # (môn phái, bang phái) theo "desc user": None chưa biết, bang "" = không có bang
                    "thongtin": self.moitruong.get_thongtinnguoichoi(muctieu["idnguoichoi"]) if muctieu["idnguoichoi"] else (None, None),
                    "he": muctieu["he"], "khang": round(khang) if khang else None, "socum": socum,
                    "sodon": len(muctieu["dons"]), "stdoan": (mocsau[0] - moc[0]) if moc else 0,
                    "maudau": moc[1] if moc else None, "maucuoi": mocsau[1] if mocsau else None, "lucdanh": muctieu["lucdanh"],
                    # Số đòn của mình trong đoạn đo máu, số bậc máu tụt không phải do mình (xem THOIGIANGANBAC)
                    "sodondoan": (mocsau[2] - moc[2]) if moc else 0, "sobackhac": muctieu["sobackhac"] + (1 if muctieu["bacchogan"] else 0),
                }
            if hesomoi:
                self._hesodps = hesomoi
        return ketqua

    def get_hesodps(self):
        return self._hesodps

    def get_sharebidanh(self):
        # {id đối tượng: {ten, khoaquai, idnguoichoi, cong: {hệ: (Công, số đòn cụm, số đòn)}, nhip (đòn / giây), sokhoang, lucdanh}} mọi
        # kẻ đã đánh mình gần đây. Quái không biết hệ => tính cả 2 hệ (cùng Kháng mình thì ra cùng sát thương)
        ketqua = {}
        with self._khoa:
            for iddoituong, bidanh in self._bidanhs.items():
                if time.time() - bidanh["lucdanh"] > THOIGIANNHOMUCTIEU:
                    continue
                cong = {}
                for he, chiso in ((HE_NGOAI, 1), (HE_NOI, 2)):
                    giatri, socum = congtheocum([congtusatthuong(d[0], d[chiso], he) for d in bidanh["dons"]])
                    if giatri:
                        cong[he] = (round(giatri), socum, len(bidanh["dons"]))
                nhip, sokhoang = nhiptheoluc([d[3] for d in bidanh["dons"]])
                ketqua[iddoituong] = {"ten": bidanh["ten"], "khoaquai": bidanh["khoaquai"], "idnguoichoi": bidanh["idnguoichoi"],
                                      "cong": cong, "nhip": round(nhip, 3) if nhip else None, "sokhoang": sokhoang,
                                      "lucdanh": bidanh["lucdanh"]}
        return ketqua


def gopuocluong(tomtats):
    # Gộp tóm tắt của nhiều cửa sổ cho cùng 1 mục tiêu -> {"khang": {hệ: (Kháng, số đòn cụm, số đòn)}, "khihuyet": số hoặc None,
    # "mautut": % đã tụt trong đoạn đo}. Khí Huyết: các cửa sổ cùng đoạn đo (cùng mốc % đầu / cuối) thì cộng sát thương; khác đoạn thì
    # lấy đoạn dài nhất (sát thương cửa sổ khác trong đoạn đó bị thiếu => số ra thấp hơn thật)
    # "sodondoan": số đòn của mình trong đoạn, "sobackhac": số bậc tụt không phải do các cửa sổ cùng đoạn (lấy ít nhất: bậc cửa sổ A
    # không đánh có thể là của cửa sổ B cùng đoạn) - > 0 thì Khí Huyết ra thấp hơn thật, kho không lưu
    khangs = {}
    doans = {}
    for tt in tomtats:
        if tt.get("he") and tt.get("khang") and tt["socum"] > khangs.get(tt["he"], (0, 0, 0))[1]:
            khangs[tt["he"]] = (tt["khang"], tt["socum"], tt["sodon"])
        if tt.get("maudau") is not None:
            khoa = (tt["maudau"], tt["maucuoi"])
            st, sodon, sobac = doans.get(khoa, (0, 0, None))
            sobackhac = tt.get("sobackhac", 0)
            doans[khoa] = (st + tt.get("stdoan", 0), sodon + tt.get("sodondoan", 0), sobackhac if sobac is None else min(sobac, sobackhac))
    mautut, khihuyet, sodondoan, sobackhac = 0, None, 0, 0
    if doans:
        (maudau, maucuoi), (tongst, sodondoan, sobackhac) = max(doans.items(), key = lambda d: (d[0][0] - d[0][1], d[1][0]))
        mautut = maudau - maucuoi
        if mautut >= MAUTUTTOITHIEU and tongst > 0:
            khihuyet = round(tongst * 100. / mautut)
    return {"khang": khangs, "khihuyet": khihuyet, "mautut": mautut, "sodondoan": sodondoan, "sobackhac": sobackhac}


# Lưu lâu dài theo ID người chơi (giao diện gọi, file tienich_xq.duongdanthongtinnguoichoi). Kháng cần ít nhất chừng này đòn khớp
# nhau mới ghi (3 đòn để hiện tạm trên giao diện, ghi file thì chắc hơn)
SODONLUUTOITHIEU = 5
# Số đã lưu cũ hơn chừng này giây (lần giao lưu khác, có thể đã đổi đồ) thì số mới thay luôn dù ít đòn hơn; trong cùng lần giao lưu thì
# chỉ thay khi đo được nhiều đòn hơn / máu tụt nhiều hơn
THOIGIANPHIENGIAOLUU = 1800.
TENCHISOKHANG_MAP = {"ngoai": "ngoaikhang", "noi": "noikhang"}


def capnhatkhonguoichoi(kho, tomtatstheomuctieu, luc = None):
    # kho: dict đọc từ file; tomtatstheomuctieu: {id đối tượng: [tóm tắt của các cửa sổ]}. Ghi vào kho các chỉ số đo được của mục tiêu
    # là người chơi -> True nếu kho đổi
    luc = luc or time.time()
    is_doi = False
    for tomtats in tomtatstheomuctieu.values():
        idnguoichoi = next((tt.get("idnguoichoi") for tt in tomtats if tt.get("idnguoichoi")), 0)
        if not idnguoichoi:
            continue
        gop = gopuocluong(tomtats)
        muc = kho.setdefault(str(idnguoichoi), {})
        ten = next((tt.get("ten") for tt in tomtats if tt.get("ten")), None)
        if ten and muc.get("ten") != ten:
            muc["ten"] = ten
            is_doi = True
        for he, (khang, socum, _) in gop["khang"].items():
            if socum < SODONLUUTOITHIEU:
                continue
            cu = muc.get(TENCHISOKHANG_MAP[he])
            if not cu or luc - cu.get("luc", 0) > THOIGIANPHIENGIAOLUU or socum >= cu.get("sodon", 0):
                if not cu or cu.get("giatri") != khang or cu.get("sodon") != socum:
                    muc[TENCHISOKHANG_MAP[he]] = {"giatri": khang, "sodon": socum, "luc": round(luc), "pb": PHIENBANSODO}
                    is_doi = True
        # Khí Huyết: đoạn có bậc máu tụt không phải do mình (người khác / bảo thú cùng đánh) thì không lưu
        if gop["khihuyet"] and not gop["sobackhac"] and gop["sodondoan"] >= SODONTOITHIEUCUM:
            cu = muc.get("khihuyet")
            if not cu or luc - cu.get("luc", 0) > THOIGIANPHIENGIAOLUU or gop["mautut"] >= cu.get("mautut", 0):
                if not cu or cu.get("giatri") != gop["khihuyet"]:
                    muc["khihuyet"] = {"giatri": gop["khihuyet"], "mautut": gop["mautut"], "luc": round(luc), "pb": PHIENBANSODO}
                    is_doi = True
        for tt in tomtats:
            monphai, bangphai = tt.get("thongtin") or (None, None)
            is_doi = ghithongtinnguoichoi(kho, idnguoichoi, None, monphai, bangphai, luc) or is_doi
        if not any(k in muc for k in KHOATHONGTINs):
            del kho[str(idnguoichoi)]
    return is_doi


KHOATHONGTINs = ("khihuyet", "ngoaikhang", "noikhang", "ngoaicong", "noicong", "monphai", "bangphai")


def ghithongtinnguoichoi(kho, idnguoichoi, ten, monphai, bangphai, luc = None):
    # Môn phái / bang phái (theo "desc user") của người chơi vào kho; None = chưa biết thì giữ số cũ, bang "" = không có bang.
    # Gọi cả cho mục tiêu mới chọn chưa đánh -> True nếu kho đổi
    if not idnguoichoi or (monphai is None and bangphai is None and not ten):
        return False
    luc = luc or time.time()
    muc = kho.setdefault(str(idnguoichoi), {})
    is_doi = False
    for khoa, giatri in (("ten", ten), ("monphai", monphai), ("bangphai", bangphai)):
        if giatri is not None and (khoa != "ten" or giatri) and muc.get(khoa) != giatri:
            muc[khoa] = giatri
            is_doi = True
    if is_doi and (monphai is not None or bangphai is not None):
        muc["lucthongtin"] = round(luc)
    if not any(k in muc for k in KHOATHONGTINs):
        del kho[str(idnguoichoi)]
    return is_doi


TENCHISOCONG_MAP = {HE_NGOAI: "ngoaicong", HE_NOI: "noicong"}


def gopcongdoithu(tomtats, mamonphai = None):
    # tomtats: các tóm tắt get_sharecongdoithu của 1 người chơi từ nhiều cửa sổ -> ({hệ: (Công, số đòn cụm, số đòn)}, is_rohe).
    # Môn phái biết hệ (HEMONPHAI_MAP) thì chỉ giữ hệ đó; chưa rõ hệ thì giữ cả 2 (giao diện ghi "nếu đánh Ngoại / Nội")
    mamonphai = mamonphai or next((tt.get("monphai") for tt in tomtats if tt.get("monphai")), None)
    he = HEMONPHAI_MAP.get(mamonphai)
    congs = {}
    for tt in tomtats:
        for h, (cong, socum, sodon) in (tt.get("cong") or {}).items():
            if (he is None or h == he) and socum > congs.get(h, (0, 0, 0))[1]:
                congs[h] = (cong, socum, sodon)
    return congs, he is not None


def ghicongnguoichoi(kho, idnguoichoi, tomtats, luc = None):
    # Ghi Công đối thủ đo được vào kho (chỉ khi biết hệ theo môn phái), cùng quy tắc thay số với Kháng -> True nếu kho đổi
    congs, is_rohe = gopcongdoithu(tomtats)
    if not is_rohe or not idnguoichoi:
        return False
    luc = luc or time.time()
    muc = kho.setdefault(str(idnguoichoi), {})
    is_doi = False
    for he, (cong, socum, _) in congs.items():
        if socum < SODONLUUTOITHIEU:
            continue
        cu = muc.get(TENCHISOCONG_MAP[he])
        if not cu or luc - cu.get("luc", 0) > THOIGIANPHIENGIAOLUU or socum >= cu.get("sodon", 0):
            if not cu or cu.get("giatri") != cong or cu.get("sodon") != socum:
                muc[TENCHISOCONG_MAP[he]] = {"giatri": cong, "sodon": socum, "luc": round(luc), "pb": PHIENBANSODO}
                is_doi = True
    if not muc:
        del kho[str(idnguoichoi)]
    return is_doi


# Chỉ số quái theo tên + cấp (khoaquaitheoten), giao diện ghi _internal/thongtinquai.json (tienich_xq.luuthongtinquai), bot đọc để
# hiện / kết luận ngay khi chọn quái cùng loại mà không phải đo lại. Chỉ ghi số đã CHẮC (người dùng yêu cầu biết chính xác mới lưu), đã
# ghi thì giữ, chỉ thay khi đo được chắc hơn hẳn (Khí Huyết tụt thêm >= MAUTUTTHAYTHE %, Kháng / Công gấp đôi số đòn):
# - Khí Huyết: máu tụt liền 1 đoạn ≥ MAUTUTCHACCHAN % (đoạn thường bắt đầu từ 100% đúng đầy máu, đầu cuối bước 2% => tụt 50% lệch
#   ≤ ~4%; 0% không tính vì đòn kết liễu dư), trong đoạn có ≥ SODONKHIHUYETCHACCHAN đòn của mình và mọi bậc tụt đều có đòn của
#   mình gần đó (không ai khác cùng đánh). Trước 2026-11-08 cần 90% từ lần nhảy bậc sau đòn đầu => 103 quái chỉ 9 con có Khí Huyết
# - Kháng / Công: cụm khớp nhau ≥ SODONCHACCHAN đòn (Kháng cụm khớp lệch dưới 1%)
# - Nhịp đánh của quái: ≥ SOKHOANGNHIPCHACCHAN khoảng giữa 2 đòn liền nhau
MAUTUTCHACCHAN = 50.
MAUTUTTHAYTHE = 10.
SODONKHIHUYETCHACCHAN = 2
SODONCHACCHAN = 5
SOKHOANGNHIPCHACCHAN = 8


def capnhatkhoquai(kho, infos, luc = None):
    # kho: dict đọc từ thongtinquai.json {"<tên>|<cấp>": {ten, cap, khihuyet / ngoaikhang / noikhang / ngoaicong / noicong / nhip:
    # {giatri, sodon | mautut, luc}}}; infos: info mọi cửa sổ -> True nếu kho đổi
    luc = luc or time.time()
    theomuctieu, theokhoa = {}, {}
    for i in infos:
        for iddoituong, tt in (i.get("_uocluongmuctieu") or {}).items():
            if tt.get("khoaquai"):
                theomuctieu.setdefault((tt["khoaquai"], iddoituong), []).append(tt)
        for tt in (i.get("_bidanh") or {}).values():
            if tt.get("khoaquai"):
                theokhoa.setdefault(tt["khoaquai"], []).append(tt)
    is_doi = False

    def ghi(khoaquai, truong, giatri):
        nonlocal is_doi
        ten, cap = khoaquai.rsplit("|", 1)
        muc = kho.setdefault(khoaquai, {"ten": ten, "cap": int(cap)})
        cu = muc.get(truong)
        if cu and "mautut" in giatri:
            is_thay = giatri["mautut"] >= cu.get("mautut", 0) + MAUTUTTHAYTHE
        elif cu:
            is_thay = giatri["sodon"] >= 2 * cu.get("sodon", 0) and giatri["giatri"] != cu.get("giatri")
        else:
            is_thay = True
        if is_thay:
            giatri["luc"] = round(luc)
            giatri["pb"] = PHIENBANSODO
            muc[truong] = giatri
            is_doi = True

    for (khoaquai, _), tomtats in theomuctieu.items():
        gop = gopuocluong(tomtats)
        if gop["khihuyet"] and gop["mautut"] >= MAUTUTCHACCHAN and not gop["sobackhac"] and gop["sodondoan"] >= SODONKHIHUYETCHACCHAN:
            ghi(khoaquai, "khihuyet", {"giatri": gop["khihuyet"], "mautut": gop["mautut"]})
        for he, (khang, socum, _) in gop["khang"].items():
            if socum >= SODONCHACCHAN:
                ghi(khoaquai, TENCHISOKHANG_MAP[he], {"giatri": khang, "sodon": socum})
    for khoaquai, tomtats in theokhoa.items():
        for he in (HE_NGOAI, HE_NOI):
            tot = max((tt["cong"][he] for tt in tomtats if he in (tt.get("cong") or {})), key = lambda v: v[1], default = None)
            if tot and tot[1] >= SODONCHACCHAN:
                ghi(khoaquai, TENCHISOCONG_MAP[he], {"giatri": tot[0], "sodon": tot[1]})
        tot = max(((tt["nhip"], tt["sokhoang"]) for tt in tomtats if tt.get("nhip")), key = lambda v: v[1], default = None)
        if tot and tot[1] >= SOKHOANGNHIPCHACCHAN:
            ghi(khoaquai, "nhip", {"giatri": tot[0], "sodon": tot[1]})
    # Kháng / Công gom theo loại quái (mọi con cùng tên + cấp, xem UocLuongMucTieu._donsquai): mỗi cửa sổ 1 tóm tắt, lấy cụm đông nhất
    theoloai = {}
    for i in infos:
        for khoaquai, tt in (i.get("_chisoquai") or {}).items():
            for loai, tenmap in (("khang", TENCHISOKHANG_MAP), ("cong", TENCHISOCONG_MAP)):
                for he, v in (tt.get(loai) or {}).items():
                    truong = tenmap[he]
                    if v[1] > theoloai.get((khoaquai, truong), (0, 0, 0))[1]:
                        theoloai[(khoaquai, truong)] = v
    for (khoaquai, truong), (giatri, socum, _) in theoloai.items():
        if socum >= SODONCHACCHAN:
            ghi(khoaquai, truong, {"giatri": giatri, "sodon": socum})
    return is_doi
