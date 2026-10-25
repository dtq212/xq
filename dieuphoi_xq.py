import json
import os
import random
import threading
import time

from hangso_xq import IS_XOAYVONGLENHGIUACACBOT, KHOANGNGHIGIUALENH, IS_XOAYVONGBATDAUDICHUYEN, KHOANGNGHIBATDAUDICHUYEN, THOIGIANCHOLUOTTOIDA, THOIGIANGIUKYNANGMUCTIEU
from tienich_xq import _thumucthietlap

# Bot đăng ký chờ lượt mà quá lâu không làm mới (process đã chết) thì bỏ qua
THOIGIANCHOHETHAN = 0.5
# Cấu hình (giao diện sửa) đọc lại sau mỗi khoảng này, khỏi tốn 1 lần gọi qua Manager cho mỗi lệnh
THOIGIANDOCLAICAUHINH = 1.0

# Các kênh chia lượt độc lập: gửi lệnh vào game, và bắt đầu di chuyển (nhân vật đang đứng mà bắt đầu chạy)
KENH_LENH = "lenh"
KENH_DICHUYEN = "dichuyen"


def _cauhinhmacdinh():
    return {
        KENH_LENH: {"is_xoayvong": IS_XOAYVONGLENHGIUACACBOT, "nghitoithieu": KHOANGNGHIGIUALENH[0], "nghitoida": KHOANGNGHIGIUALENH[1]},
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

    Dùng chung qua Manager: khoa (Lock), trangthai (dict: theo từng kênh bot gửi gần nhất, thời điểm, khoảng nghỉ kế tiếp;
    "cauhinh" do giao diện sửa), dangchos (dict: (kênh, hwnd) -> thời điểm làm mới gần nhất của bot đang chờ lượt).
    Lượt kế tiếp thuộc về bot đang chờ có hwnd đứng ngay sau bot vừa được lượt (xoay vòng theo thứ tự hwnd).
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
        # Trong cùng 1 bot có nhiều luồng gửi lệnh (hàng đợi + gửi trực tiếp): chỉ 1 luồng đi xin lượt 1 lúc
        self._khoanoibo = threading.Lock()
        self._cauhinh = _cauhinhmacdinh()[kenh]
        self._thoidiemdoccauhinh = 0.
        # thuxinluot: lúc bắt đầu xin (chưa được) để tính quá lâu, và lần gọi gần nhất
        self._thoidiembatdauthuxin = 0.
        self._thoidiemthuxingannhat = 0.

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

    def xinluot(self):
        # Chờ (chặn luồng gọi) tới khi được lượt. Dùng cho gửi lệnh: lệnh đã nằm trong hàng đợi, phải gửi
        if not self.get_is_batxoayvong():
            return
        with self._khoanoibo:
            thoidiembatdau = time.time()
            while True:
                thoidiemhientai = time.time()
                with self.khoa:
                    if self._thulaylanluot(thoidiemhientai, thoidiemhientai - thoidiembatdau >= THOIGIANCHOLUOTTOIDA):
                        return
                time.sleep(0.01)

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

    def ghinhanguingay(self):
        # Lệnh khẩn cấp đi thẳng, nhưng vẫn tính là 1 lượt để bot khác nghỉ sau nó
        if not self.get_is_batxoayvong():
            return
        with self.khoa:
            self._ghinhanluot(time.time())


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
