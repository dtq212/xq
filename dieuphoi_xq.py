import random
import threading
import time

from hangso_xq import IS_XOAYVONGLENHGIUACACBOT, KHOANGNGHIGIUALENH, THOIGIANCHOLUOTTOIDA

# Bot đăng ký chờ lượt mà quá lâu không làm mới (process đã chết) thì bỏ qua
THOIGIANCHOHETHAN = 0.5


class DieuPhoiLuot:
    """Chia lượt gửi lệnh giữa các process bot (mỗi cửa sổ game 1 process).

    Dùng chung qua Manager: khoa (Lock), trangthai (dict: bot gửi gần nhất, thời điểm, khoảng nghỉ kế tiếp),
    dangchos (dict: hwnd -> thời điểm làm mới gần nhất của bot đang chờ lượt).
    Lượt kế tiếp thuộc về bot đang chờ có hwnd đứng ngay sau bot vừa gửi (xoay vòng theo thứ tự hwnd).
    """

    def __init__(self, idcuaso, khoa, trangthai, dangchos):
        self.idcuaso = idcuaso
        self.khoa = khoa
        self.trangthai = trangthai
        self.dangchos = dangchos
        # Trong cùng 1 bot có nhiều luồng gửi lệnh (hàng đợi + gửi trực tiếp): chỉ 1 luồng đi xin lượt 1 lúc
        self._khoanoibo = threading.Lock()

    def _botduocluot(self, thoidiemhientai):
        dangchos = sorted(h for h, t in self.dangchos.items() if thoidiemhientai - t < THOIGIANCHOHETHAN)
        if not dangchos:
            return self.idcuaso
        botguigannhat = self.trangthai.get("botguigannhat", 0)
        for h in dangchos:
            if h > botguigannhat:
                return h
        return dangchos[0]

    def xinluot(self):
        if not IS_XOAYVONGLENHGIUACACBOT:
            return
        with self._khoanoibo:
            thoidiembatdau = time.time()
            while True:
                thoidiemhientai = time.time()
                with self.khoa:
                    self.dangchos[self.idcuaso] = thoidiemhientai
                    khoangnghi = self.trangthai.get("khoangnghi", 0.)
                    is_hetnghi = thoidiemhientai - self.trangthai.get("thoidiemgui", 0.) >= khoangnghi
                    is_qualau = thoidiemhientai - thoidiembatdau >= THOIGIANCHOLUOTTOIDA
                    if (is_hetnghi and self._botduocluot(thoidiemhientai) == self.idcuaso) or is_qualau:
                        self.trangthai.update({
                            "botguigannhat": self.idcuaso,
                            "thoidiemgui": thoidiemhientai,
                            "khoangnghi": random.uniform(*KHOANGNGHIGIUALENH),
                        })
                        self.dangchos.pop(self.idcuaso, None)
                        return
                time.sleep(0.01)

    def ghinhanguingay(self):
        # Lệnh khẩn cấp đi thẳng, nhưng vẫn tính là 1 lượt để bot khác nghỉ sau nó
        if not IS_XOAYVONGLENHGIUACACBOT:
            return
        with self.khoa:
            self.trangthai.update({
                "botguigannhat": self.idcuaso,
                "thoidiemgui": time.time(),
                "khoangnghi": random.uniform(*KHOANGNGHIGIUALENH),
            })
