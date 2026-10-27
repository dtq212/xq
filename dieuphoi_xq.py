import json
import os
import random
import threading
import time

from hangso_xq import IS_XOAYVONGLENHGIUACACBOT, KHOANGGIULUOTLENH, THOIGIANNHUONGLUOTKHIRANH, IS_XOAYVONGBATDAUDICHUYEN, KHOANGNGHIBATDAUDICHUYEN, THOIGIANCHOLUOTTOIDA, THOIGIANGIUKYNANGMUCTIEU
from tienich_xq import _thumucthietlap

# Bot đăng ký chờ lượt mà quá lâu không làm mới (process đã chết) thì bỏ qua
THOIGIANCHOHETHAN = 0.5
# Cấu hình (giao diện sửa) đọc lại sau mỗi khoảng này, khỏi tốn 1 lần gọi qua Manager cho mỗi lệnh
THOIGIANDOCLAICAUHINH = 1.0
# Đang giữ lượt thì báo còn hoạt động sau mỗi khoảng này; chưa tới lượt thì trong khoảng này trả lời luôn là chưa (khỏi gọi qua Manager liên tục)
THOIGIANBAOHOATDONG = 0.1
THOIGIANNHOTUCHOI = 0.05

# Các kênh chia lượt độc lập: gửi lệnh chiêu / đánh vào game (mỗi bot giữ lượt [nghitoithieu, nghitoida] giây rồi nhường bot khác),
# và bắt đầu di chuyển (nhân vật đang đứng mà bắt đầu chạy, mỗi lần nhấc chân 1 lượt, giữa 2 lượt nghỉ [nghitoithieu, nghitoida] giây)
KENH_LENH = "lenh"
KENH_DICHUYEN = "dichuyen"


def is_lenhxoayvong(caulenh):
    # Chiêu có mục tiêu của nhân vật: "pf <id> <mục tiêu>" (pf2 cũng vậy). "pf <id>" (không mục tiêu: diện rộng quanh mình, buff, vận khí),
    # kỹ năng bảo thú "pf5" và đánh thường "kill" không xoay vòng
    return caulenh.startswith("pf") and not caulenh.startswith("pf5") and len(caulenh.split()) >= 3


def _cauhinhmacdinh():
    return {
        KENH_LENH: {"is_xoayvong": IS_XOAYVONGLENHGIUACACBOT, "nghitoithieu": KHOANGGIULUOTLENH[0], "nghitoida": KHOANGGIULUOTLENH[1],
                    "nhuongkhiranh": THOIGIANNHUONGLUOTKHIRANH},
        KENH_DICHUYEN: {"is_xoayvong": IS_XOAYVONGBATDAUDICHUYEN, "nghitoithieu": KHOANGNGHIBATDAUDICHUYEN[0], "nghitoida": KHOANGNGHIBATDAUDICHUYEN[1]},
    }


def _chuanhoakenh(cauhinhkenh, macdinh):
    # Thiếu khoá / sai kiểu thì lấy mặc định; khoảng nghỉ không âm, tối thiểu <= tối đa
    ketqua = dict(macdinh)
    try:
        ketqua["is_xoayvong"] = bool(cauhinhkenh.get("is_xoayvong", ketqua["is_xoayvong"]))
        nghitoithieu = max(0., float(cauhinhkenh.get("nghitoithieu", ketqua["nghitoithieu"])))
        nghitoida = max(0., float(cauhinhkenh.get("nghitoida", ketqua["nghitoida"])))
        ketqua["nghitoithieu"], ketqua["nghitoida"] = min(nghitoithieu, nghitoida), max(nghitoithieu, nghitoida)
        if "nhuongkhiranh" in ketqua:
            # Quá nhỏ thì bot đang đánh dở cũng bị coi là rảnh
            ketqua["nhuongkhiranh"] = max(0.1, float(cauhinhkenh.get("nhuongkhiranh", ketqua["nhuongkhiranh"])))
    except (AttributeError, TypeError, ValueError):
        pass
    return ketqua


def chuanhoacauhinhdieuphoi(cauhinh):
    # {kênh: {is_xoayvong, nghitoithieu, nghitoida}}. File bản đầu chỉ có 1 kênh (lệnh) để phẳng: coi là kênh lệnh
    macdinh = _cauhinhmacdinh()
    if not isinstance(cauhinh, dict):
        return macdinh
    if "is_xoayvong" in cauhinh:
        cauhinh = {KENH_LENH: cauhinh}
    return {kenh: _chuanhoakenh(cauhinh.get(kenh) or {}, macdinh[kenh]) for kenh in macdinh}


def duongdancauhinhdieuphoi():
    return os.path.join(os.path.dirname(_thumucthietlap()), "dieuphoi.json")


def taicauhinhdieuphoi():
    try:
        with open(duongdancauhinhdieuphoi(), "r", encoding = "utf-8") as file:
            return chuanhoacauhinhdieuphoi(json.load(file))
    except FileNotFoundError:
        return _cauhinhmacdinh()
    except Exception as err:
        print(f"Lỗi đọc cấu hình điều phối: {err}")
        return _cauhinhmacdinh()


def luucauhinhdieuphoi(cauhinh):
    filepath = duongdancauhinhdieuphoi()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(chuanhoacauhinhdieuphoi(cauhinh), file, ensure_ascii = False, indent = 2)
        os.replace(filetam, filepath)
    except Exception as err:
        print(f"Lỗi lưu cấu hình điều phối: {err}")


class DieuPhoiLuot:
    """Chia lượt giữa các process bot (mỗi cửa sổ game 1 process) trên 1 kênh (KENH_LENH / KENH_DICHUYEN).

    Dùng chung qua Manager: khoa (Lock), trangthai (dict: theo từng kênh bot gửi gần nhất, thời điểm, khoảng nghỉ kế tiếp / lúc hết lượt;
    "cauhinh" do giao diện sửa), dangchos (dict: (kênh, hwnd) -> thời điểm làm mới gần nhất của bot đang chờ lượt).
    Lượt kế tiếp thuộc về bot đang chờ có hwnd đứng ngay sau bot vừa được lượt (xoay vòng theo thứ tự hwnd).
    Kênh lệnh dùng thugiuluot (giữ lượt theo thời gian), kênh di chuyển dùng thuxinluot (mỗi lần 1 lượt).
    """

    def __init__(self, idcuaso, khoa, trangthai, dangchos, kenh = KENH_LENH):
        self.idcuaso = idcuaso
        self.khoa = khoa
        self.trangthai = trangthai
        self.dangchos = dangchos
        self.kenh = kenh
        self._khoacho = (kenh, idcuaso)
        self._khoabotguigannhat = kenh + "_botguigannhat"
        self._khoathoidiemgui = kenh + "_thoidiemgui"
        self._khoakhoangnghi = kenh + "_khoangnghi"
        self._khoahetluot = kenh + "_hetluot"
        # Trong cùng 1 bot có nhiều luồng gửi lệnh (hàng đợi + gửi trực tiếp): chỉ 1 luồng đi xin lượt 1 lúc
        self._khoanoibo = threading.Lock()
        self._cauhinh = _cauhinhmacdinh()[kenh]
        self._thoidiemdoccauhinh = 0.
        # thuxinluot: lúc bắt đầu xin (chưa được) để tính quá lâu, và lần gọi gần nhất
        self._thoidiembatdauthuxin = 0.
        self._thoidiemthuxingannhat = 0.
        # thugiuluot: lượt mình đang giữ hết lúc nào, lần được gần nhất / báo hoạt động gần nhất / bị từ chối gần nhất
        self._hetluotcucbo = 0.
        self._thoidiemduocgannhat = 0.
        self._thoidiembaohoatdong = 0.
        self._thoidiemtuchoi = 0.

    def _laycauhinh(self):
        if time.time() - self._thoidiemdoccauhinh >= THOIGIANDOCLAICAUHINH:
            self._thoidiemdoccauhinh = time.time()
            try:
                self._cauhinh = chuanhoacauhinhdieuphoi(self.trangthai.get("cauhinh") or {})[self.kenh]
            except Exception:
                pass
        return self._cauhinh

    def get_is_batxoayvong(self):
        return self._laycauhinh()["is_xoayvong"]

    def _get_nhuongkhiranh(self):
        return self._laycauhinh().get("nhuongkhiranh", THOIGIANNHUONGLUOTKHIRANH)

    def _khoangnghingaunhien(self):
        cauhinh = self._laycauhinh()
        return random.uniform(cauhinh["nghitoithieu"], cauhinh["nghitoida"])

    def _botduocluot(self, thoidiemhientai):
        dangchos = sorted(h for (k, h), t in self.dangchos.items() if k == self.kenh and thoidiemhientai - t < THOIGIANCHOHETHAN)
        if not dangchos:
            return self.idcuaso
        botguigannhat = self.trangthai.get(self._khoabotguigannhat, 0)
        for h in dangchos:
            if h > botguigannhat:
                return h
        return dangchos[0]

    def _thulaylanluot(self, thoidiemhientai, is_qualau):
        # Phải gọi trong self.khoa. Đăng ký đang chờ; tới lượt (hoặc chờ quá lâu) thì nhận lượt và trả về True
        self.dangchos[self._khoacho] = thoidiemhientai
        khoangnghi = self.trangthai.get(self._khoakhoangnghi, 0.)
        is_hetnghi = thoidiemhientai - self.trangthai.get(self._khoathoidiemgui, 0.) >= khoangnghi
        if not ((is_hetnghi and self._botduocluot(thoidiemhientai) == self.idcuaso) or is_qualau):
            return False
        self._ghinhanluot(thoidiemhientai)
        self.dangchos.pop(self._khoacho, None)
        return True

    def _ghinhanluot(self, thoidiemhientai):
        self.trangthai.update({
            self._khoabotguigannhat: self.idcuaso,
            self._khoathoidiemgui: thoidiemhientai,
            self._khoakhoangnghi: self._khoangnghingaunhien(),
        })

    def thuxinluot(self):
        # Không chờ: được lượt thì True, chưa thì False (vẫn giữ chỗ trong hàng chờ; gọi lại trong THOIGIANCHOHETHAN giây để không mất chỗ).
        # Dùng cho di chuyển: chưa tới lượt thì bỏ lần click này, loop di chuyển tự thử lại sau 0.05-0.1s
        if not self.get_is_batxoayvong():
            return True
        thoidiemhientai = time.time()
        if not self._thoidiembatdauthuxin or thoidiemhientai - self._thoidiemthuxingannhat > THOIGIANCHOHETHAN:
            # Lần xin mới (lần trước đã được, hoặc đã thôi xin: chỗ trong hàng chờ cũng đã hết hạn)
            self._thoidiembatdauthuxin = thoidiemhientai
        self._thoidiemthuxingannhat = thoidiemhientai
        with self.khoa:
            is_duoc = self._thulaylanluot(thoidiemhientai, thoidiemhientai - self._thoidiembatdauthuxin >= THOIGIANCHOLUOTTOIDA)
        if is_duoc:
            self._thoidiembatdauthuxin = 0.
        return is_duoc

    def thugiuluot(self):
        # Kênh lệnh, không chờ: đang giữ lượt / vừa nhận lượt thì True, chưa tới lượt thì False (vẫn giữ chỗ trong hàng chờ, gọi lại trong
        # THOIGIANCHOHETHAN giây để không mất chỗ). Bot nhận lượt giữ ngẫu nhiên [nghitoithieu, nghitoida] giây, gửi bao nhiêu chiêu / đánh
        # cũng được; hết giờ thì nhường bot đang chờ kế tiếp (không ai chờ thì giữ tiếp). Chưa tới lượt thì bot bỏ lần gửi này, vòng lặp tự gửi lại
        if not self.get_is_batxoayvong():
            return True
        with self._khoanoibo:
            thoidiemhientai = time.time()
            if thoidiemhientai < self._hetluotcucbo and thoidiemhientai - self._thoidiemduocgannhat < self._get_nhuongkhiranh() / 2:
                self._thoidiemduocgannhat = thoidiemhientai
                if thoidiemhientai - self._thoidiembaohoatdong >= THOIGIANBAOHOATDONG:
                    self._thoidiembaohoatdong = thoidiemhientai
                    self.trangthai[self._khoathoidiemgui] = thoidiemhientai
                return True
            if thoidiemhientai - self._thoidiemtuchoi < THOIGIANNHOTUCHOI:
                return False
            with self.khoa:
                hetluot = self._thunhanluottheothoigian(thoidiemhientai)
            if not hetluot:
                self._hetluotcucbo = 0.
                self._thoidiemtuchoi = thoidiemhientai
                return False
            self._hetluotcucbo = hetluot
            self._thoidiemduocgannhat = self._thoidiembaohoatdong = thoidiemhientai
            return True

    def baogiuluot(self):
        # Luồng nhanh gọi liên tục lúc đang xuất chiêu: đang giữ lượt thì báo còn hoạt động để không bị coi là rảnh mà mất lượt giữa 2 chiêu
        thoidiemhientai = time.time()
        if thoidiemhientai >= self._hetluotcucbo or thoidiemhientai - self._thoidiemduocgannhat >= self._get_nhuongkhiranh() / 2:
            return
        self._thoidiemduocgannhat = thoidiemhientai
        if thoidiemhientai - self._thoidiembaohoatdong >= THOIGIANBAOHOATDONG:
            self._thoidiembaohoatdong = thoidiemhientai
            self.trangthai[self._khoathoidiemgui] = thoidiemhientai

    def _thunhanluottheothoigian(self, thoidiemhientai):
        # Phải gọi trong self.khoa. Trả về lúc hết lượt nếu mình đang giữ / vừa nhận lượt, 0 nếu chưa tới lượt (đã đăng ký đang chờ)
        botgiuluot = self.trangthai.get(self._khoabotguigannhat, 0)
        hetluot = self.trangthai.get(self._khoahetluot, 0.)
        is_ranh = thoidiemhientai - self.trangthai.get(self._khoathoidiemgui, 0.) >= self._get_nhuongkhiranh()
        if botgiuluot == self.idcuaso and thoidiemhientai < hetluot and not is_ranh:
            self.trangthai[self._khoathoidiemgui] = thoidiemhientai
            self.dangchos.pop(self._khoacho, None)
            return hetluot
        self.dangchos[self._khoacho] = thoidiemhientai
        if (thoidiemhientai < hetluot and not is_ranh) or self._botduocluot(thoidiemhientai) != self.idcuaso:
            return 0.
        hetluot = thoidiemhientai + self._khoangnghingaunhien()
        self.trangthai.update({
            self._khoabotguigannhat: self.idcuaso,
            self._khoathoidiemgui: thoidiemhientai,
            self._khoahetluot: hetluot,
        })
        self.dangchos.pop(self._khoacho, None)
        return hetluot


class GiuKyNangMucTieu:
    """Giữ chỗ chiêu khống chế trên 1 mục tiêu giữa các process bot, để 2 nhân vật không cùng gửi 1 hiệu ứng lên 1 mục tiêu.

    giukynangs (dict qua Manager): (hiệu ứng, ID mục tiêu) -> (hwnd bot giữ, thời điểm hết hạn).
    ID mục tiêu là ID máy chủ (ID người chơi / ID đối tượng) nên mọi cửa sổ game thấy giống nhau.
    """

    # Dọn các chỗ đã hết hạn khi dict lớn quá mức này
    SOLUONGTOIDA = 200

    def __init__(self, idcuaso, khoa, giukynangs):
        self.idcuaso = idcuaso
        self.khoa = khoa
        self.giukynangs = giukynangs

    def thugiu(self, hieuung, idmuctieu, thoigian = THOIGIANGIUKYNANGMUCTIEU):
        # True: được gửi (chưa ai giữ, chỗ cũ hết hạn, hoặc chính bot này giữ) và đã giữ chỗ. False: bot khác đang giữ
        khoa = (hieuung, idmuctieu)
        thoidiemhientai = time.time()
        with self.khoa:
            dangiu = self.giukynangs.get(khoa)
            if dangiu and dangiu[0] != self.idcuaso and dangiu[1] > thoidiemhientai:
                return False
            if len(self.giukynangs) > self.SOLUONGTOIDA:
                for k, (_, hethan) in list(self.giukynangs.items()):
                    if hethan <= thoidiemhientai:
                        self.giukynangs.pop(k, None)
            self.giukynangs[khoa] = (self.idcuaso, thoidiemhientai + thoigian)
        return True

    def bogiu(self, hieuung, idmuctieu):
        # Giữ chỗ mà rốt cuộc không gửi được chiêu (còn xa phải chạy lại, kỹ năng bị khoá...) thì trả lại cho bot khác
        khoa = (hieuung, idmuctieu)
        with self.khoa:
            dangiu = self.giukynangs.get(khoa)
            if dangiu and dangiu[0] == self.idcuaso:
                self.giukynangs.pop(khoa, None)
