# Săn Tinh Anh: người dùng chọn các bản đồ có quái Tinh Anh (tên vàng, QUAITINHANH_MAP), bot lần lượt tới từng bản đồ (đường đi + phù như
# Mã Tặc), dò khắp bản đồ theo lưới vật cản và chỉ đánh quái Tinh Anh (lấy đồ Lam Kim đốt Phong Yêu Kính). Người chơi / bảo thú PK đánh
# mình thì vẫn phản công như thường. Nhặt đồ, về bán, sửa đồ, phục sinh theo thiết lập sẵn có của nhân vật.
# Mỗi bản đồ:
#   - đi qua các chỗ đã từng thấy Tinh Anh (mọi nhân vật ghi, _internal/vitritinhanh/<ID>.json) trước, rồi các điểm dò phủ vùng đi được
#   - thấy Tinh Anh thì đi tới (chọn mục tiêu / tấn công của bot lo phần đánh, ưu tiên hơn đi dò)
#   - đi hết 1 lượt điểm thì sang bản đồ kế, hết danh sách thì quay lại bản đồ đầu (Tinh Anh hồi sinh lâu nên xoay vòng các bản đồ)
# Chạy tới khi bấm dừng. Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import json
import math
import os
import re
import sys
import time

from hangso_xq import *
from luattuido_xq import MAUTEN
from tienich_xq import phatam

# Đi dò: tới cách điểm chừng này ô là tới, quá THOIGIANMOIDIEMTINHANH giây chưa tới (kẹt / điểm bên kia vách) thì sang điểm kế
KHOANGCACHTOIDIEMTINHANH = 3.
THOIGIANMOIDIEMTINHANH = 25.
# Chỗ thấy Tinh Anh: cách chỗ đã ghi dưới chừng này ô thì coi là cùng chỗ (Tinh Anh đi lang thang quanh điểm xuất hiện)
KHOANGCACHGOPVITRITINHANH = 15.
GIANCACHGHIVITRITINHANH = 3.
# Thấy Tinh Anh mà chừng này giây chưa đánh được (bị chắn, chọn mục tiêu bỏ qua...) thì thôi đi tới con đó, dò tiếp
THOIGIANDUOITINHANHTOIDA = 40.
# Tinh Anh đang đuổi ra khỏi tầm nhìn (_get_diachidoituongxungquanhs chỉ lấy trong KHOANGCACHTOANMANHINH = 18 ô) thì vẫn nhớ chỗ thấy cuối
# chừng này giây và đi tiếp tới đó. 18/11 Hầm Vạn Nhân 1: Tinh Binh Oan Linh cách 17~18.6 ô bên kia vách (đường đi 36 ô), mình lùi 1 bước
# là nó ra ngoài 18 ô -> quên ngay, quay về điểm dò hướng ngược lại; bước lại vào 18 ô thì đuổi tiếp. Hai lệnh "dò" / "tới Tinh Anh" (cộng
# chọn mục tiêu "Tiếp cận để tấn công") thay nhau mỗi giây, nhân vật kẹt tại chỗ, giờ đuổi 40s cũng bị xoá theo nên không bao giờ hết
THOIGIANNHOTINHANHKHUAT = 10.
# Túi đầy lúc săn: về Tân Thủ Thôn cất kho CHỈ đồ Lam Kim rơi từ Tinh Anh (không theo bảng Cất kho), không bán rác; cất xong săn tiếp. Cất xong
# chưa tới chừng này giây mà túi vẫn đầy (không có món nào cất được) thì dừng săn, kẻo đi về Tân Thủ Thôn mãi.
# Đồ Lam Kim khớp luật Bán có "Màu tên" ở tab Hành trang thì bán ở Chủ Tiệm Tạp Hóa cùng đồ trắng (_lydokhongbanmautinhanh, 22/11)
MAUCATTINHANHs = (MAUTEN["lam kim"],)
THOIGIANCATLAITINHANH = 300.
# Giết được con Tinh Anh của bản đồ (mỗi bản đồ 1 con) mà quanh đó không còn con nào sống: sang bản đồ kế luôn, khỏi dò hết các
# điểm. Trước khi đi chờ nhặt đồ rơi: ít nhất chừng này giây (đồ mới hiện dưới đất), còn đồ đang nhặt thì chờ tới tối đa
THOIGIANCHONHATSAUTINHANH = 3.
THOIGIANCHONHATSAUTINHANHTOIDA = 20.
# Bản đồ không có đường / không đọc được lưới chừng này lần liền thì bỏ bản đồ đó khỏi lượt này
SOLANLOIBANDOTINHANH = 3


# Tinh Anh chết LUÔN rơi ít nhất 1 món Lam Kim (người dùng 16/11; phẩm chất đồ dưới đất 1 = xanh lam). Con chỉ nhận theo CẤP (tên không có
# trong bảng) mà chết xong chừng này giây không có món Lam Kim MỚI nào hiện trong BANKINHDOROITINHANH ô quanh chỗ chết => không phải Tinh
# Anh (16/11 Yên Trường Thành: Tam Đao Quỷ / Tâm Chi Ma cấp 61~63 chết không rơi gì). Có Lam Kim => học là Tinh Anh. Học theo bản đồ + tên,
# chung mọi nhân vật: _internal/tinhanhhoc.json {"co"/"khong": {"<id bản đồ>": [tên, ...]}}
PHAMCHATLAMKIM = 1
# Đang săn thì nhặt cả đồ trắng (phẩm chất 0) lẫn Lam Kim, không cần ô Phẩm chất ở tab Hành trang: Tinh Anh rơi cả đồ trắng, nhặt về bán
# gỡ vốn (người dùng 16/11). Luật nhặt "Không nhặt" vẫn thắng
PHAMCHATNHATTINHANHs = (0, PHAMCHATLAMKIM)
THOIGIANCHODOROITINHANH = 5.
BANKINHDOROITINHANH = 5.
# Chết không rơi Lam Kim chừng này lần (cộng dồn mọi nhân vật, đếm ở "nghi") mới ghi "khong" (bỏ hẳn). 16/11 Tướng Quân Cổ Mộ 1-3:
# Thủ Mộ Thạch Sư / Thạch Hổ là Tinh Anh thật (cấp 93, quái thường 85~88) mà bị ghi "khong" sau 1 lần do lỗi ảnh chụp đồ cũ (đồ rơi
# cùng lúc thấy chết bị tính là đồ cũ, bot nhặt luôn) -> bỏ lỡ Tinh Anh cả buổi. Đếm 2 lần cho chắc
SOLANKHONGROITINHANH = 2
# Ảnh chụp đồ Lam Kim dưới đất ở lượt trước (lúc con còn sống) cũ hơn chừng này giây thì không dùng làm "đồ cũ"
THOIGIANANHCHUPLAMKIM = 3.
# Nhận Tinh Anh theo chênh cấp với quái THƯỜNG đang thấy trên bản đồ (mọi bản đồ có Tinh Anh, đoán hay đã biết tên). Khoảng đoán cũ =
# cấp cao nhất đã ghi +1~+15, mà cấp ghi gồm luôn con Tinh Anh => 24/11 Tru Tiên Trận 1: quái thường 110~113, Tinh Anh Thương Quỷ 119,
# đã ghi 110~120 nên đoán 121~135, bot dò hết bản đồ bỏ qua con bò. Cấp quái thường = cấp cao nhất có >= SOQUAICAPTHUONG con khác
# nhau thấy trong THOIGIANNHOCAPQUAI giây (Tinh Anh mỗi bản đồ 1 con, ~30 phút mới mọc lại nên không đủ số con). Quái cao hơn quái
# thường >= CHENHCAPTINHANH cấp là Tinh Anh (đo: Lang Yêu 33~34 / Thủ Lĩnh 37, Yên Trường Thành 56~58 / Tinh Vệ 61~63, Hầm Vạn Nhân 1
# 80~83 / 93, Tru Tiên Trận 1 110~113 / 119). Đoán nhầm thì giết xong không rơi Lam Kim -> tinhanhhoc.json học "khong" như cũ
SOQUAICAPTHUONG = 3
THOIGIANNHOCAPQUAI = 600.
CHENHCAPTINHANH = 3
SOQUAINHOCAPTOIDA = 500
_tinhanhhoc = {"luc": 0., "mtime": None, "bang": {"co": {}, "khong": {}, "nghi": {}}}


def _duongdantinhanhhoc():
    return os.path.join(os.path.dirname(_thumucvitritinhanh()), "tinhanhhoc.json")


def taitinhanhhoc():
    # Đọc lại file tối đa 5 giây 1 lần (các cửa sổ khác cũng ghi), chỉ khi file đổi
    if time.time() - _tinhanhhoc["luc"] > 5.:
        _tinhanhhoc["luc"] = time.time()
        try:
            mtime = os.path.getmtime(_duongdantinhanhhoc())
            if mtime != _tinhanhhoc["mtime"]:
                with open(_duongdantinhanhhoc(), "r", encoding = "utf-8") as file:
                    bang = json.load(file)
                _tinhanhhoc["bang"] = {"co": bang.get("co") or {}, "khong": bang.get("khong") or {}, "nghi": bang.get("nghi") or {}}
                _tinhanhhoc["mtime"] = mtime
        except Exception:
            pass
    return _tinhanhhoc["bang"]


def tentinhanhhoc(ten):
    return " ".join((ten or "").split("(")[0].split())


def ghitinhanhhoc(loai, idbando, ten):
    # loai "co" / "khong"; ghi vào loại này thì bỏ khỏi loại kia. "khong" chỉ ghi thật khi đủ SOLANKHONGROITINHANH lần (đếm ở "nghi")
    # -> trả về True khi đã ghi "khong" (bỏ hẳn), False khi mới đếm
    _tinhanhhoc["luc"] = 0.
    bang = taitinhanhhoc()
    ten, khoa = tentinhanhhoc(ten), str(idbando)
    khac = "khong" if loai == "co" else "co"
    if ten in bang[khac].get(khoa, []):
        bang[khac][khoa].remove(ten)
    nghi = bang["nghi"].get(khoa) or {}
    if loai == "co":
        nghi.pop(ten, None)
    else:
        nghi[ten] = nghi.get(ten, 0) + 1
        bang["nghi"][khoa] = nghi
        if nghi[ten] < SOLANKHONGROITINHANH:
            _luutinhanhhoc(bang)
            return False
        nghi.pop(ten, None)
    if not nghi:
        bang["nghi"].pop(khoa, None)
    if ten not in bang[loai].setdefault(khoa, []):
        bang[loai][khoa].append(ten)
    _luutinhanhhoc(bang)
    return True


def _luutinhanhhoc(bang):
    try:
        from tienich_xq import thaythefile
        duongdan = _duongdantinhanhhoc()
        with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
            json.dump(bang, file, ensure_ascii = False, indent = 1)
        thaythefile(duongdan + ".tmp", duongdan)
    except Exception:
        pass


def _thumucvitritinhanh():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "vitritinhanh")


def taivitritinhanh(idbando):
    # Gộp chỗ từng thấy Tinh Anh trên bản đồ của mọi nhân vật -> [(x, y), ...] (bỏ chỗ trùng)
    diems = []
    try:
        tenfiles = os.listdir(_thumucvitritinhanh())
    except FileNotFoundError:
        return diems
    for tenfile in tenfiles:
        if not tenfile.endswith(".json"):
            continue
        try:
            with open(os.path.join(_thumucvitritinhanh(), tenfile), "r", encoding = "utf-8") as file:
                bang = json.load(file)
        except Exception:
            continue
        for x, y in bang.get(str(idbando), []):
            if all(math.dist((x, y), d) >= KHOANGCACHGOPVITRITINHANH for d in diems):
                diems.append((int(x), int(y)))
    return diems


def tachbandotinhanh(chuoi, is_thaplencao = True):
    # "71, 528, 263" -> [71, 528, 263] (chỉ bản đồ có trong QUAITINHANH_MAP, bỏ trùng). Thứ tự đi theo tuỳ chọn "Đi từ cấp thấp lên cao"
    # (is_thaplencao, mặc định bật: người dùng 16/11 các bản đồ nối nhau chạy 1 mạch từ thấp lên cao, vd Cầu Cửu Khúc -> Thiên Môn Trận);
    # tắt thì cấp CAO trước như trước (đi từ dưới lên danh sách chọn xếp cấp tăng dần); cùng cấp thì id NHỎ trước = chiều thuận của các bản đồ nối nhau
    # (Yên Trường Thành 1 -> 2 -> 3, Chân Núi Đại Biệt 261 -> Đại Biệt Sơn 262 -> Vu Sơn 263), vào bản đồ ở đầu lộ trình dò chứ không
    # phải ở cuối (16/11 đi ngược Vu Sơn -> Đại Biệt Sơn, đứng cuối bản đồ)
    ids = []
    for so in re.findall(r"\d+", str(chuoi or "")):
        idbando = int(so)
        if idbando in QUAITINHANH_MAP and idbando not in ids:
            ids.append(idbando)
    return sorted(ids, key = lambda i: thutubandotinhanh(i, is_thaplencao))


def thutubandotinhanh(idbando, is_thaplencao = True):
    # Khoá xếp thứ tự đi: cấp Tinh Anh tăng dần (is_thaplencao) / giảm dần, cùng cấp thì id bản đồ tăng dần (giao diện chọn bản đồ dùng chung)
    capthap, capcao = CAPTINHANH_MAP.get(idbando, (0, 0))
    return (capthap, capcao, idbando) if is_thaplencao else (-capthap, -capcao, idbando)


class TacTuTinhAnh:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_tinhanh(self):
        if self._tinhanh:
            return
        self._tinhanh = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "ibando": 0, "do": None, "sovong": 0,
                         "sogiet": 0, "idsong": set(), "iddachet": set(), "lucghi": 0., "duoi": None, "dabatdanh": False}
        self._logta(f"Bắt đầu săn Tinh Anh ở: {self._motabandotinhanh() or '(chưa chọn bản đồ)'}")
        # Tự đi một mình: Theo sau đang bật thì bot bị kéo về người được theo sau; tạm tắt, dừng thì trả lại
        self._doituychontinhanh("_is_tudongtheosau", False, "Theo sau")
        # Nhặt đồ trắng / Lam Kim rơi từ Tinh Anh (PHAMCHATNHATTINHANHs)
        self._doituychontinhanh("_is_tudongnhatvatpham", True, "Tự động nhặt vật phẩm")
        phatam("Bắt đầu săn tinh anh")

    def huy_tinhanh(self):
        if self._tinhanh:
            self._ketthuctinhanh("Đã dừng săn Tinh Anh (bấm tay)")

    def thietlap_bandotinhanh(self, chuoi):
        self._tinhanh_bandos = tachbandotinhanh(chuoi, self._is_tinhanhthaplencao)
        self._logta(f"Bản đồ: {self._motabandotinhanh() or '(trống)'}")
        if self._tinhanh:
            self._tinhanh.update(ibando = 0, do = None, duoi = None)

    def thietlap_tinhanhthaplencao(self, is_thaplencao):
        # Đổi thứ tự đi giữa chừng: xếp lại, đang săn thì giữ bản đồ đang tới (ibando tìm lại theo bản đồ hiện tại khi tới nơi)
        self._is_tinhanhthaplencao = bool(is_thaplencao)
        dangtoi = None
        if self._tinhanh and self._tinhanh_bandos:
            dangtoi = self._tinhanh_bandos[self._tinhanh["ibando"] % len(self._tinhanh_bandos)]
        self._tinhanh_bandos = tachbandotinhanh(self._tinhanh_bandos, self._is_tinhanhthaplencao)
        if dangtoi in self._tinhanh_bandos:
            self._tinhanh["ibando"] = self._tinhanh_bandos.index(dangtoi)
        self._logta(f"Thứ tự đi: {'cấp thấp lên cao' if self._is_tinhanhthaplencao else 'cấp cao xuống thấp'}: {self._motabandotinhanh() or '(trống)'}")

    def get_is_dangtinhanh(self):
        return bool(self._tinhanh)

    def _is_tinhanhdangchay(self):
        # Săn Tinh Anh đứng sau Lăng Ly Sơn / Sư Gia / Mã Tặc... trong vòng di chuyển: việc đó đang chạy thì _xulytinhanh không được gọi,
        # "chedo" đứng yên ở giá trị cũ. 16/11 Ngốc đang đi Lăng Ly Sơn lỡ bật Săn Tinh Anh -> chedo kẹt "dichuyen" -> không chọn mục
        # tiêu suốt 15 phút. Chỉ tính khi _xulytinhanh mới được gọi gần đây
        return bool(self._tinhanh) and time.time() - self._tinhanh.get("lucxuly", 0.) < 2.

    def get_is_tinhanhdichuyen(self):
        # Đang đi tới bản đồ chọn: không chọn quái dọc đường
        return self._is_tinhanhdangchay() and self._tinhanh["chedo"] == "dichuyen"

    def get_is_tinhanhdanhquai(self):
        # Đang ở bản đồ chọn đi dò: chỉ đánh Tinh Anh, không giới hạn theo lộ trình điểm đánh của nhân vật
        return self._is_tinhanhdangchay() and self._tinhanh["chedo"] == "danhquai"

    def _is_loctinhanh(self):
        # Chỉ chọn quái Tinh Anh: ô "Chỉ đánh mục tiêu tên màu vàng" hoặc đang săn Tinh Anh ở bản đồ chọn
        return self._is_chidanhtinhanh or self.get_is_tinhanhdanhquai()

    def _is_doituongtinhanh(self, diachi, ten = None):
        # Quái Tinh Anh theo tên hoặc theo cấp so với bản đồ đang đứng (hangso is_quaitinhanh). Phó bản mượn ID bản đồ (Phong Yêu Kính)
        # thì không xét cấp: quái trong đó cấp không theo bản đồ thật
        moitruong = self.moitruong
        ten = ten or moitruong.get_tendoituong(diachi)
        idbando = moitruong.get_idbandohientai() if moitruong.get_is_phobanmuonbando() is False else None
        cap = laycaptrongten(moitruong._get_tenthucte(diachi))
        if idbando is not None and cap is not None:
            self._ghicapquaithay(idbando, moitruong.get_iddoituong(diachi), ten, cap)
        if idbando is not None:
            # Đã học (theo đồ rơi): có Lam Kim => Tinh Anh, không => bỏ hẳn, khỏi xét cấp
            bang, khoa, tenhoc = taitinhanhhoc(), str(idbando), tentinhanhhoc(ten)
            if tenhoc in bang["co"].get(khoa, ()):
                return True
            if tenhoc in bang["khong"].get(khoa, ()):
                return False
        return is_quaitinhanh(ten, idbando, cap) or self._is_tinhanhtheocapthay(idbando, ten, cap)

    def _ghicapquaithay(self, idbando, iddoituong, ten, cap):
        # Ghi cấp từng con quái thấy (theo id, kẻo 1 con đứng lâu được đếm nhiều lần) cho _capquaithuongthay
        if is_tenkhongthetinhanh(ten):
            return
        bang = self._capquaithay.setdefault(idbando, {})
        bang[iddoituong] = (cap, time.time())
        if len(bang) > SOQUAINHOCAPTOIDA:
            hethan = time.time() - THOIGIANNHOCAPQUAI
            for i in [i for i, (_, luc) in bang.items() if luc < hethan]:
                del bang[i]
            if len(bang) > SOQUAINHOCAPTOIDA:
                for i in sorted(bang, key = lambda i: bang[i][1])[:len(bang) - SOQUAINHOCAPTOIDA]:
                    del bang[i]

    def _capquaithuongthay(self, idbando):
        # Cấp cao nhất có >= SOQUAICAPTHUONG con khác nhau thấy gần đây trên bản đồ = cấp quái thường; chưa đủ số con thì None
        hethan = time.time() - THOIGIANNHOCAPQUAI
        dem = {}
        for cap, luc in self._capquaithay.get(idbando, {}).values():
            if luc >= hethan:
                dem[cap] = dem.get(cap, 0) + 1
        caps = [cap for cap, so in dem.items() if so >= SOQUAICAPTHUONG]
        return max(caps) if caps else None

    def _is_tinhanhtheocapthay(self, idbando, ten, cap):
        # Chỉ ở bản đồ có Tinh Anh (QUAITINHANH_MAP) và bản đồ thật (idbando None = phó bản mượn ID)
        if idbando is None or cap is None or idbando not in QUAITINHANH_MAP or is_tenkhongthetinhanh(ten):
            return False
        capthuong = self._capquaithuongthay(idbando)
        return capthuong is not None and cap >= capthuong + CHENHCAPTINHANH

    def _is_tinhanhchacchan(self, idbando, ten):
        # Nhận theo TÊN ghi cho chính bản đồ này hoặc đã học là Tinh Anh nhờ rơi Lam Kim: giết xong là xong bản đồ. Tên Tinh Anh của bản
        # đồ khác (vd Võng Lượng Quỷ ở Linh Cốc Động 2) / đuôi "Thủ Lĩnh" thì chờ xem rơi Lam Kim như con nhận theo cấp
        return is_tentinhanhcuabando(ten, idbando) or tentinhanhhoc(ten) in taitinhanhhoc()["co"].get(str(idbando), ())

    def _diachilamkimquanh(self, x, y):
        # Địa chỉ đồ Lam Kim dưới đất trong BANKINHDOROITINHANH ô quanh (x, y)
        moitruong = self.moitruong
        kq = set()
        i = -1
        while True:
            i += 1
            diachi = moitruong.get_diachicosothongtindoituongx(i)
            if not diachi:
                break
            if (moitruong.get_is_vatphamtontai(diachi) and moitruong.get_phamchatvatpham(diachi) == PHAMCHATLAMKIM
                    and math.dist(moitruong.get_toado(diachi), (x, y)) <= BANKINHDOROITINHANH):
                kq.add(diachi)
        return kq

    def _tatcalamkimduoidat(self):
        moitruong = self.moitruong
        kq = set()
        i = -1
        while True:
            i += 1
            diachi = moitruong.get_diachicosothongtindoituongx(i)
            if not diachi:
                break
            if moitruong.get_is_vatphamtontai(diachi) and moitruong.get_phamchatvatpham(diachi) == PHAMCHATLAMKIM:
                kq.add(diachi)
        return kq

    def _kiemdoroitinhanh(self, s, idbando):
        # Con nhận theo cấp vừa chết: chờ đồ rơi. Có món Lam Kim mới => học là Tinh Anh (tính như giết Tinh Anh của bản đồ), hết giờ không
        # có => học là không phải (đủ SOLANKHONGROITINHANH lần mới bỏ hẳn). Đổi bản đồ thì bỏ dở
        conlai = []
        for cho in s.get("chodoroi") or ():
            if cho["idbando"] != idbando:
                continue
            ten, x, y = cho["ten"], cho["x"], cho["y"]
            if self._diachilamkimquanh(x, y) - cho["cu"]:
                ghitinhanhhoc("co", idbando, ten)
                self._logta(f"{ten} ở {laytenbando(idbando)} rơi Lam Kim: là Tinh Anh (ghi tinhanhhoc.json)")
                if s.get("bandogiet") != idbando:
                    s["bandogiet"], s["loaidagiet"] = idbando, set()
                s["loaidagiet"].add(tentinhanhhoc(ten))
                s["lucgiet"] = time.time()
            elif time.time() - cho["luc"] > THOIGIANCHODOROITINHANH:
                if ghitinhanhhoc("khong", idbando, ten):
                    self._logta(f"{ten} ở {laytenbando(idbando)} chết không rơi Lam Kim lần thứ {SOLANKHONGROITINHANH}: không phải Tinh Anh, "
                                f"lần sau bỏ qua (ghi tinhanhhoc.json)")
                else:
                    self._logta(f"{ten} ở {laytenbando(idbando)} chết không thấy rơi Lam Kim: nghi không phải Tinh Anh, lần sau vẫn đánh "
                                f"(đủ {SOLANKHONGROITINHANH} lần mới bỏ)")
            else:
                conlai.append(cho)
        s["chodoroi"] = conlai

    def get_trangthaitinhanh(self):
        if self._tinhanh:
            return f"Săn Tinh Anh (giết {self._tinhanh['sogiet']} con, {self._tinhanh['sovong']} vòng): {self._tinhanh['trangthai']}"
        return self._ketquatinhanh or ""

    def _motabandotinhanh(self):
        return ", ".join(f"{laytenbando(i) or i}" for i in self._tinhanh_bandos)

    def _logta(self, noidung):
        self.moitruong._inlog(f"[TINH ANH] {noidung}")

    def _doituychontinhanh(self, thuoctinh, giatri, ten):
        # Đổi 1 ô thiết lập trong lúc săn, nhớ giá trị cũ để trả lại khi dừng (luuthietlap lưu giá trị cũ này)
        s = self._tinhanh
        if s is not None and getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self._logta(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng săn thì trả lại)")

    def _ketthuctinhanh(self, thongbao):
        s = self._tinhanh
        self._tinhanh = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if s and s["sogiet"]:
            thongbao += f" (giết {s['sogiet']} con)"
        self._logta(thongbao)
        self._ketquatinhanh = f"{time.strftime('%H:%M')} {thongbao}"
        phatam("Kết thúc săn tinh anh")

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulytinhanh(self):
        # Gọi thay lộ trình điểm đánh khi đang săn Tinh Anh -> yêu cầu di chuyển hoặc None
        s = self._tinhanh
        moitruong = self.moitruong
        s["lucxuly"] = time.time()
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logta(s["trangthai"])
        bandos = [b for b in self._tinhanh_bandos if b in QUAITINHANH_MAP]
        if not bandos:
            s["chedo"] = "dichuyen"
            s["trangthai"] = "chưa chọn bản đồ: bấm \"Chọn bản đồ\" ở tab Chiến đấu"
            return None
        if moitruong.get_is_nhanvatdachet() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0 or moitruong.get_is_dangvankhi():
            return None
        if time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        if moitruong.get_is_dayhanhtrang():
            if self._catkho:
                return None
            if time.time() - s.get("luccatkho", 0.) < THOIGIANCATLAITINHANH:
                self._ketthuctinhanh("Túi đầy mà về không có đồ trắng để bán / đồ Lam Kim để cất (dọn túi)")
                return None
            s["luccatkho"] = time.time()
            s["trangthai"] = "túi đầy: về Tân Thủ Thôn bán đồ trắng, cất kho Lam Kim"
            self._logta("Túi đầy: về Tân Thủ Thôn bán đồ trắng, cất kho đồ Lam Kim, xong săn tiếp")
            # Việc "Cất kho ngay" (tactu_catkho_xq): vòng di chuyển xét nó trước Săn Tinh Anh, cất xong thì đây tự đi lại bản đồ đang săn.
            # "banrac": bán trang bị trắng ở Chủ Tiệm Tạp Hóa trước (_buocbantrangtinhanh)
            self.yeucau_catkho()
            if self._catkho:
                self._catkho["mamaus"] = MAUCATTINHANHs
                self._catkho["banrac"] = "cho"
            return None
        idbando = moitruong.get_idbandohientai()
        # Lúc bắt đầu (bấm Bắt đầu / mở lại bot) mà đang đứng ở 1 bản đồ trong danh sách: dò luôn bản đồ đó trước. Chỉ xét 1 lần, kẻo dò
        # xong bản đồ này chuyển sang bản đồ kế lại bị kéo về đây mãi
        if not s.get("daxetbatdau"):
            s["daxetbatdau"] = True
            if idbando in bandos:
                s["ibando"] = bandos.index(idbando)
        s["ibando"] %= len(bandos)
        bandodich = bandos[s["ibando"]]
        # Đang đi ngang 1 bản đồ trong danh sách (vd. Yên Trường Thành 2 -> 1) mà thấy Tinh Anh nhận theo TÊN còn sống: đánh luôn, coi bản
        # đồ này là bản đồ đang săn (giết xong thì sang bản đồ kế của nó như thường). Con đã đuổi quá giờ / bị đánh dấu lỗi thì thôi
        if idbando != bandodich and idbando in bandos:
            duoi = s["duoi"] or {}
            for _, iddoituong, x, y, ten in self._timtinhanhxungquanh(s, idbando):
                if (self._is_tinhanhchacchan(idbando, ten) and iddoituong not in self._idmuctieubiloi_map
                        and time.time() - duoi.get(iddoituong, {}).get("luc", time.time()) <= THOIGIANDUOITINHANHTOIDA):
                    self._logta(f"Thấy {ten} ở {laytenbando(idbando)} ({x}, {y}) trên đường đi: đánh luôn")
                    s["ibando"] = bandos.index(idbando)
                    s["do"] = None
                    bandodich = idbando
                    break
        if idbando != bandodich:
            s["chedo"] = "dichuyen"
            s["trangthai"] = f"tới {laytenbando(bandodich)} săn {self._tentinhanhbando(bandodich)}"
            buoc = self._lapbuocditoibando(bandodich, is_hoithanhphu = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                self._logta(f"Không có đường tới {laytenbando(bandodich)}: {buoc['mota']}, sang bản đồ kế")
                self._sangbandoketinhanh(s, bandos)
                return None
            return self._thuchienbuocditoibando(buoc, bandodich, None, f"[TINH ANH] Tới {laytenbando(bandodich)}")

        s["chedo"] = "danhquai"
        self._batdanhquaitinhanh(s)
        tinhanhs = self._timtinhanhxungquanh(s, idbando)
        # Thấy Tinh Anh còn sống (chưa bị bot đánh dấu lỗi): đi tới nó, chọn mục tiêu / tấn công của bot lo phần đánh (ưu tiên hơn đi dò)
        # s["duoi"]: id -> {"luc": lúc bắt đầu đi tới con đó, "thay": lúc thấy cuối, x, y, ten} (mỗi con tính riêng, kẻo 2 con không tới
        # được thay nhau đặt lại giờ). Con ra khỏi tầm nhìn vẫn nhớ THOIGIANNHOTINHANHKHUAT giây, đi tới chỗ thấy cuối; tới gần (nửa màn
        # hình) mà không thấy (đã chết / đi xa) hoặc đã thấy chết thì bỏ
        bayh = time.time()
        duoi = s["duoi"] = s["duoi"] or {}
        thays = {t[1] for t in tinhanhs}
        for iddoituong, d in list(duoi.items()):
            if iddoituong not in thays and (bayh - d["thay"] > THOIGIANNHOTINHANHKHUAT or iddoituong in s["iddachet"]
                                            or moitruong.get_khoangcachdiem(d["x"], d["y"]) <= KHOANGCACHNUAMANHINH):
                del duoi[iddoituong]
        for _, iddoituong, x, y, ten in tinhanhs:
            duoi.setdefault(iddoituong, {"luc": bayh}).update(thay = bayh, x = x, y = y, ten = ten)
        dangduois = sorted(tinhanhs + [(moitruong.get_khoangcachdiem(d["x"], d["y"]), i, d["x"], d["y"], d["ten"])
                                       for i, d in duoi.items() if i not in thays])
        for khoangcach, iddoituong, x, y, ten in dangduois:
            if iddoituong in self._idmuctieubiloi_map:
                continue
            if bayh - duoi[iddoituong]["luc"] > THOIGIANDUOITINHANHTOIDA:
                continue
            khuat = "" if iddoituong in thays else ", chỗ thấy cuối"
            s["trangthai"] = f"đánh {ten} ở {laytenbando(idbando)} ({x}, {y}{khuat})"
            self._capnhatbuocdichuyen(f"Săn Tinh Anh: tới {ten} ({x}, {y}{khuat})")
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 2.}
        # Mỗi bản đồ chỉ có 1 con Tinh Anh (người dùng 16/11, ~30 phút mới mọc lại): giết được 1 con là sang bản đồ kế, cứ quay vòng
        if not tinhanhs and s.get("bandogiet") == idbando and s.get("loaidagiet"):
            chuagiet = time.time() - s["lucgiet"]
            # Còn món đang nhặt thì chờ tiếp. Trước chỉ xét _yeucaunhatvatpham, mà yêu cầu này chỉ có khi món cách > 1.5 ô: đứng ngay trên
            # đống đồ nhặt món đầu thì nó là None -> quá 3s bỏ đi, sót món Lam Kim thứ 2 (người dùng 18/11, Hầm Vạn Nhân 4 bỏ lại Hỗn
            # Thiên Cân Mạo). _diachicosovatphamdangnhat còn khi đứng sát món
            is_conde = bool(self._yeucaunhatvatpham or self._diachicosovatphamdangnhat)
            if chuagiet < THOIGIANCHONHATSAUTINHANH or (is_conde and chuagiet < THOIGIANCHONHATSAUTINHANHTOIDA):
                s["trangthai"] = f"đã giết hết {self._tentinhanhbando(idbando)} ở {laytenbando(idbando)}: chờ nhặt đồ"
                return None
            conlai = self._tatcalamkimduoidat()
            if conlai:
                self._logta("Bỏ lại Lam Kim dưới đất: " + ", ".join(
                    f"{self.moitruong.get_tendoituong(d)} {tuple(self.moitruong.get_toado(d))}" for d in conlai))
            self._logta(f"Đã giết hết {self._tentinhanhbando(idbando)} ở {laytenbando(idbando)}, sang bản đồ kế")
            self._sangbandoketinhanh(s, bandos)
            return None
        yeucau, is_hetluot = self._ditheodiemtinhanh(s, idbando, f"dò {laytenbando(idbando)} tìm {self._tentinhanhbando(idbando)}")
        if is_hetluot:
            self._logta(f"Dò hết {laytenbando(idbando)}, sang bản đồ kế")
            self._sangbandoketinhanh(s, bandos)
            return None
        return yeucau

    def _sangbandoketinhanh(self, s, bandos):
        s["ibando"] = (s["ibando"] + 1) % len(bandos)
        s["do"] = None
        s["duoi"] = None
        s["bandogiet"] = None
        if s["ibando"] == 0:
            s["sovong"] += 1

    def _tentinhanhbando(self, idbando):
        # Tên trong bảng chỉ là 1 biến thể (quái nào của bản đồ cũng có thể ra Tinh Anh): hiện theo cấp
        cap = CAPTINHANH_MAP.get(idbando)
        return f"Tinh Anh (cấp {cap[0]}~{cap[1]})" if cap else "Tinh Anh"

    def _batdanhquaitinhanh(self, s):
        # Ô cần cho đánh quái người dùng quên bật (hoặc đang "Chỉ đánh người chơi") thì đổi giúp, dừng thì trả lại
        if s["dabatdanh"]:
            return
        s["dabatdanh"] = True
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            self._doituychontinhanh(thuoctinh, giatri, ten)

    def _timtinhanhxungquanh(self, s, idbando):
        # Tinh Anh trong tầm nhìn -> [(khoảng cách, id, x, y, tên), ...] con còn sống, gần trước. Đồng thời: đếm con đã chết (từng thấy
        # sống), ghi chỗ thấy Tinh Anh cho lần sau
        moitruong = self.moitruong
        toado = moitruong.get_toado()
        self._kiemdoroitinhanh(s, idbando)
        songs, vitris = [], []
        cokiem = False
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi) or moitruong.get_is_npc(diachi):
                continue
            ten = moitruong.get_tendoituong(diachi)
            if not self._is_doituongtinhanh(diachi, ten):
                self._ghinghitinhanh(s, idbando, diachi, ten)
                continue
            iddoituong = moitruong.get_iddoituong(diachi)
            x, y = moitruong.get_toado(diachi)
            if moitruong.get_is_nhanvatdachet(diachi):
                if iddoituong in s["idsong"] and iddoituong not in s["iddachet"]:
                    s["iddachet"].add(iddoituong)
                    s["sogiet"] += 1
                    # Chỉ con nhận ra theo TÊN mới tính "đã giết Tinh Anh của bản đồ" -> sang bản đồ kế. Con chỉ khớp theo cấp có thể là
                    # quái nhiệm vụ / sự kiện lạc vào (16/11 Yên Trường Thành 2-3: Tam Đao Quỷ, Tâm Chi Ma cấp 61~63 chết sau 1-2 giây, bot
                    # tưởng xong bản đồ, bỏ đi sót Yên Quốc Tinh Vệ to lù lù) -> giết xong vẫn dò tiếp
                    if not self._is_tinhanhchacchan(idbando, ten):
                        self._logta(f"Đã giết {ten} ở {laytenbando(idbando)} ({x}, {y}) (nhận theo cấp, chờ xem rơi Lam Kim): tổng {s['sogiet']} con")
                        # Đồ cũ = ảnh chụp lượt trước lúc con còn sống: đồ rơi ra cùng lúc thấy chết mà chụp bây giờ thì bị tính là đồ cũ,
                        # bot lại nhặt ngay (get sau 3ms) -> tưởng không rơi (16/11 Thủ Mộ Thạch Sư). Kiểm ngay lượt này, kẻo bị nhặt mất
                        anhchup = s.get("lamkimtruoc")
                        cu = anhchup[1] if anhchup and time.time() - anhchup[0] < THOIGIANANHCHUPLAMKIM else self._diachilamkimquanh(x, y)
                        s.setdefault("chodoroi", []).append({"idbando": idbando, "ten": ten, "x": x, "y": y, "luc": time.time(), "cu": cu})
                        cokiem = True
                        continue
                    # Loại đã giết ở bản đồ đang dò (đổi bản đồ thì tính lại) -> đủ loại thì sang bản đồ kế (_xulytinhanh)
                    if s.get("bandogiet") != idbando:
                        s["bandogiet"], s["loaidagiet"] = idbando, set()
                    s["loaidagiet"].add(ten.split("(")[0].strip().replace("Thuỷ", "Thủy"))
                    s["lucgiet"] = time.time()
                    self._logta(f"Đã giết {ten} ở {laytenbando(idbando)} ({x}, {y}): tổng {s['sogiet']} con")
                continue
            if not moitruong.get_is_cothetancong(diachi):
                continue
            s["idsong"].add(iddoituong)
            vitris.append((int(x), int(y)))
            songs.append((math.dist(toado, (x, y)), iddoituong, int(x), int(y), ten))
        if cokiem:
            self._kiemdoroitinhanh(s, idbando)
        # Còn con sống (có thể sắp chết): chụp đồ Lam Kim dưới đất để lượt sau so đồ mới rơi
        s["lamkimtruoc"] = (time.time(), self._tatcalamkimduoidat()) if songs else None
        # Id cũ chất đống cả phiên: giữ gọn
        if len(s["idsong"]) > 2000:
            s["idsong"] = set(i for _, i, _, _, _ in songs)
            s["iddachet"].clear()
        if vitris and time.time() - s["lucghi"] > GIANCACHGHIVITRITINHANH:
            s["lucghi"] = time.time()
            self._ghivitritinhanh(idbando, vitris)
        return sorted(songs)

    def _ghinghitinhanh(self, s, idbando, diachi, ten):
        # Sợ bỏ sót Tinh Anh khi mô tả bản đồ (tips) ghi sai khoảng cấp (Bành Thành tips sai tên): quái ở bản đồ đang săn cấp CAO hơn khoảng
        # Tinh Anh thì không đánh (người dùng: cấp Tinh Anh đúng như mô tả) nhưng ghi log "Nghi Tinh Anh" mỗi tên + cấp 1 lần để đối chiếu
        khoang = CAPTINHANH_MAP.get(idbando)
        if not khoang or not ten or ten in TENKHONGPHAITINHANHs or "Bảo Bảo" in ten or "Quốc Kính" in ten or "Tàn Phách" in ten:
            return
        cap = laycaptrongten(self.moitruong._get_tenthucte(diachi))
        if cap is None or cap <= khoang[1]:
            return
        danghi = s.setdefault("danghi", set())
        if (idbando, ten, cap) in danghi:
            return
        danghi.add((idbando, ten, cap))
        x, y = self.moitruong.get_toado(diachi)
        self._logta(f"Nghi Tinh Anh: {ten} cấp {cap} ở {laytenbando(idbando)} ({x}, {y}), cao hơn khoảng cấp mô tả {khoang[0]}~{khoang[1]} "
                    f"nên không đánh. Đúng là tên vàng thì sửa QUAITINHANH_MAP")

    def _ghivitritinhanh(self, idbando, vitris):
        idnguoichoi = self.moitruong.get_idnguoichoi()
        if not idnguoichoi:
            return
        # Phó bản mượn ID bản đồ ngoài (Phong Yêu Kính...): quái trong đó không có ở bản đồ thật, không ghi
        if self.moitruong.get_is_phobanmuonbando() is not False:
            return
        duongdan = os.path.join(_thumucvitritinhanh(), f"{idnguoichoi}.json")
        try:
            with open(duongdan, "r", encoding = "utf-8") as file:
                bang = json.load(file)
        except Exception:
            bang = {}
        diems = bang.setdefault(str(idbando), [])
        is_doi = False
        for x, y in vitris:
            if all(math.dist((x, y), d) >= KHOANGCACHGOPVITRITINHANH for d in diems):
                diems.append([x, y])
                is_doi = True
                self._logta(f"Ghi chỗ thấy Tinh Anh {laytenbando(idbando)} ({x}, {y})")
        if not is_doi:
            return
        try:
            from tienich_xq import thaythefile
            os.makedirs(os.path.dirname(duongdan), exist_ok = True)
            with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
                json.dump(bang, file, separators = (",", ":"))
            thaythefile(duongdan + ".tmp", duongdan)
        except Exception as err:
            self._logta(f"Lỗi ghi chỗ Tinh Anh: {err}")
        # Điểm dò đang đi của bản đồ này chưa có chỗ mới: thêm vào cuối lượt
        do = self._tinhanh and self._tinhanh["do"]
        if do and do["idbando"] == idbando:
            for x, y in vitris:
                if all(math.dist((x, y), d) >= KHOANGCACHGOPVITRITINHANH for d in do["diems"]):
                    do["diems"].append((x, y))

    def _ditheodiemtinhanh(self, s, idbando, nhan):
        # Đi lần lượt chỗ từng thấy Tinh Anh rồi các điểm dò phủ vùng đi được (lưới vật cản, _taodiemdo).
        # -> (yêu cầu di chuyển, đã đi hết 1 lượt các điểm)
        moitruong = self.moitruong
        do = s["do"]
        if not do or do["idbando"] != idbando:
            toado = moitruong.get_toado()
            vitris = taivitritinhanh(idbando)
            dos = list(self._taodiemdo(idbando))
            if not dos and not vitris:
                s["trangthai"] = f"{nhan}: chưa đọc được bản đồ"
                s["solanloi"] = s.get("solanloi", 0) + 1
                if s["solanloi"] >= SOLANLOIBANDOTINHANH:
                    s["solanloi"] = 0
                    return None, True
                return None, False
            s["solanloi"] = 0
            # Chỗ từng thấy: gần mình trước rồi lần lượt điểm gần điểm trước; điểm dò giữ thứ tự vòng của dexuatlotrinhdo, bắt đầu từ
            # điểm gần chỗ kết thúc phần chỗ từng thấy
            diems = []
            con = list(vitris)
            vitrihientai = toado
            while con:
                gan = min(con, key = lambda d: math.dist(d, vitrihientai))
                con.remove(gan)
                diems.append(gan)
                vitrihientai = gan
            dos = [d for d in dos if all(math.dist(d, v) >= KHOANGCACHGOPVITRITINHANH for v in vitris)]
            if dos:
                i = min(range(len(dos)), key = lambda k: math.dist(dos[k], vitrihientai))
                diems += dos[i:] + dos[:i]
            do = s["do"] = {"idbando": idbando, "diems": diems, "i": 0, "luc": time.time()}
            self._logta(f"{laytenbando(idbando)}: {len(vitris)} chỗ từng thấy Tinh Anh + {len(dos)} điểm dò")
        x, y = do["diems"][do["i"]]
        if moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIDIEMTINHANH or time.time() - do["luc"] > THOIGIANMOIDIEMTINHANH:
            do["i"] += 1
            do["luc"] = time.time()
            if do["i"] >= len(do["diems"]):
                return None, True
            x, y = do["diems"][do["i"]]
        s["trangthai"] = f"{nhan} (điểm {do['i'] + 1}/{len(do['diems'])})"
        self._capnhatbuocdichuyen(f"Săn Tinh Anh: {nhan} (điểm {do['i'] + 1}/{len(do['diems'])})")
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1., "is_dioo": False}, False
