# Hàng việc (bảng ở tab Nhiệm vụ): các nhiệm vụ tích chọn được làm lần lượt theo thứ tự, việc này dừng (xong / lỗi / hết vật phẩm) thì
# tự sang việc kế. Kết quả từng việc ghi theo ngày: việc đã có kết quả hôm nay thì bỏ qua, qua ngày thì làm lại từ đầu (hàng việc đang
# chạy mà hết việc thì vẫn bật, chờ sang ngày). Bấm tay dừng việc đang làm thì hàng việc cũng dừng (không ghi kết quả, chạy lại thì làm
# tiếp chính việc đó). Thứ tự / tích chọn / giới hạn vòng / đang chạy / kết quả lưu theo nhân vật (luuthietlap)
import time

from hangso_xq import *
from tienich_xq import phatam

# Bắt đầu việc rồi chờ chừng này giây mới xét lại (việc chưa kịp bật thì coi là không bắt đầu được)
THOIGIANCHOBATDAUVIEC = 3.


def ngayhomnay():
    return time.strftime("%Y-%m-%d")


class TacTuHangViec:
    # --- Thiết lập từ giao diện ------------------------------------------------------------------------------------------------------
    def thietlap_hangviec(self, cauhinh):
        # cauhinh: {"thutu": [mã việc], "chon": [mã việc], "vong": {mã việc: số vòng, 0 = không giới hạn}} (thiếu khoá nào thì giữ cũ)
        if "thutu" in cauhinh:
            thutu = [k for k in cauhinh["thutu"] if k in VIECHANG_MAP]
            self._hangviec_thutu = thutu + [k for k in VIECHANG_MAP if k not in thutu]
        if "chon" in cauhinh:
            self._hangviec_chon = [k for k in cauhinh["chon"] if k in VIECHANG_MAP]
        if "vong" in cauhinh:
            self._hangviec_vong = {k: int(v) for k, v in cauhinh["vong"].items() if k in VIECCOVONGs and int(v or 0) > 0}

    def batdau_hangviec(self):
        if not self._is_chayhangviec:
            self._is_chayhangviec = True
            self._luchangviec = 0.
            self._loghv("Bắt đầu chạy hàng việc: " + (", ".join(VIECHANG_MAP[k] for k in self._hangviec_thutu if k in self._hangviec_chon)
                                                        or "(chưa tích việc nào)"))

    def huy_hangviec(self):
        # Dừng hàng việc, việc hàng việc đang làm cũng dừng luôn
        if not self._is_chayhangviec:
            return
        self._is_chayhangviec = False
        self._loghv("Đã dừng hàng việc (bấm tay)")
        viec = self._viechangdangchay
        if viec and viec == self.get_viecdanglam():
            self._dungviec(viec)
        self._viechangdangchay = ""

    def lamlai_hangviec(self, viecs):
        # Xoá kết quả hôm nay của các việc này để hàng việc làm lại
        for viec in viecs:
            self._ketquahangviec["viec"].pop(viec, None)

    # --- Trạng thái ------------------------------------------------------------------------------------------------------------------
    def get_viecdanglam(self):
        # Việc (nhiệm vụ / phó bản) đang chạy: mã trong VIECHANG_MAP, "matac" / "keocap", hoặc ""
        if self._sumon:
            return "sumon"
        if self._sugia:
            return "sugia"
        if self._danhvong:
            return "danhvong"
        if self._tapkich:
            return "tapkich"
        if self._langlyson:
            return self._langlyson["phoban"]
        if self._matac:
            return "matac"
        if self._keocap:
            return "keocap"
        return ""

    def get_viechangtieptheo(self, boqua = ""):
        # Việc tích chọn đầu tiên chưa có kết quả hôm nay (trừ việc boqua: việc đang làm, để bảng hiện việc sau nó)
        self._lamtuoingayhangviec()
        daxong = self._ketquahangviec["viec"]
        return next((k for k in self._hangviec_thutu if k in self._hangviec_chon and k not in daxong and k != boqua), "")

    def get_hangviecshare(self):
        # Cho bảng Hàng việc trên giao diện
        self._lamtuoingayhangviec()
        return {"chay": self._is_chayhangviec, "thutu": list(self._hangviec_thutu), "chon": list(self._hangviec_chon),
                "vong": dict(self._hangviec_vong), "ketqua": dict(self._ketquahangviec["viec"]), "danglam": self.get_viecdanglam(),
                "tieptheo": self.get_viechangtieptheo(boqua = self.get_viecdanglam()), "danglamtheohang": self._viechangdangchay, "trangthai": self._trangthaiviecdanglam()}

    def _trangthaiviecdanglam(self):
        # Một dòng "nhân vật đang làm gì" cho bảng
        if self._is_tatbot:
            return "Bot đang tắt"
        viec = self.get_viecdanglam()
        if viec == "sumon":
            return self.get_trangthaisumon()
        if viec == "sugia":
            return self.get_trangthaisugia()
        if viec == "danhvong":
            return self.get_trangthaidanhvong()
        if viec == "tapkich":
            return self.get_trangthaitapkich()
        if viec in ("langlyson", "thanhkieu", "phongyeukinh"):
            return self.get_trangthailanglyson()
        if viec == "matac":
            return self.get_trangthaimatac()
        if viec == "keocap":
            return self.get_trangthaikeocap()
        if self.get_is_danggiaodo():
            return "Giao tiền / đồ"
        if self.get_is_dangcatkho():
            return "Cất kho"
        if self._idbandocandi:
            return "Đi tới bản đồ chọn tay"
        if self._is_tudongtheosau:
            return f"Theo sau {self._tenmuctieutheosau or 'trưởng nhóm'}"
        if self._is_tudongdichuyendiemdanhxungquanh:
            return "Farm theo lộ trình điểm đánh"
        return "Không làm nhiệm vụ"

    # --- Ghi kết quả (gọi từ _ketthuc... của từng việc) ---------------------------------------------------------------------------------
    def _ghiketthucviec(self, viec, thongbao):
        if viec not in VIECHANG_MAP:
            return
        if "(bấm tay)" in thongbao:
            # Người dùng tự dừng: hàng việc đang chạy chính việc này thì dừng theo, không ghi kết quả
            if self._is_chayhangviec and viec == self._viechangdangchay:
                self._is_chayhangviec = False
                self._viechangdangchay = ""
                self._loghv(f"Dừng tay {VIECHANG_MAP[viec]}: dừng luôn hàng việc (bấm Chạy để làm tiếp)")
            return
        self._lamtuoingayhangviec()
        self._ketquahangviec["viec"][viec] = {"kq": "xong" if thongbao.startswith("✅") else "loi", "luc": time.strftime("%H:%M"),
                                              "thongbao": thongbao}
        if viec == self._viechangdangchay:
            self._viechangdangchay = ""

    def _is_dugioihanvong(self, viec, sovong):
        # Việc có vòng (phó bản, Tập Kích) do hàng việc bật: đủ số vòng đặt trong bảng thì dừng ở chỗ an toàn (gọi từ module việc đó)
        gioihan = self._hangviec_vong.get(viec, 0)
        return bool(gioihan) and self._is_chayhangviec and self._viechangdangchay == viec and sovong >= gioihan

    # --- Vòng chính -------------------------------------------------------------------------------------------------------------------
    def action_hangviec(self):
        if not self._is_chayhangviec or time.time() < self._luchangviec:
            return
        dang = self.get_viecdanglam()
        if dang:
            # Việc khác (bật tay, Mã Tặc tự bật...) đang chạy: chờ nó xong
            return
        viec = self._viechangdangchay
        if viec and viec not in self._ketquahangviec["viec"]:
            # Vừa bật mà không chạy (hoặc dừng không qua _ketthuc...): ghi lỗi để không bật lại mãi
            self._ghiketthucviec(viec, "❌ Không bắt đầu được (thiếu thiết lập? xem log)")
        self._viechangdangchay = ""
        # Đang có việc ưu tiên của người dùng: để xong rồi mới bật việc kế
        if self._idbandocandi or self.get_is_danggiaodo() or self.get_is_dangcatkho() or self._mocuahang:
            return
        viec = self.get_viechangtieptheo()
        if not viec:
            if not self._ketquahangviec.get("dabaoxong"):
                self._ketquahangviec["dabaoxong"] = True
                self._loghv("Hết việc trong hàng hôm nay, chờ sang ngày mới làm lại")
                phatam("Xong hàng việc hôm nay")
            return
        self._loghv(f"Bắt đầu {VIECHANG_MAP[viec]}")
        self._viechangdangchay = viec
        self._luchangviec = time.time() + THOIGIANCHOBATDAUVIEC
        if viec == "sumon":
            self.batdau_sumon()
        elif viec == "sugia":
            self.batdau_sugia()
        elif viec == "danhvong":
            self.batdau_danhvong()
        elif viec == "tapkich":
            self.batdau_tapkich()
        else:
            self.batdau_langlyson(viec)

    def _dungviec(self, viec):
        if viec == "sumon":
            self.huy_sumon()
        elif viec == "sugia":
            self.huy_sugia()
        elif viec == "danhvong":
            self.huy_danhvong()
        elif viec == "tapkich":
            self.huy_tapkich()
        elif viec in ("langlyson", "thanhkieu", "phongyeukinh"):
            self.huy_langlyson()

    def _lamtuoingayhangviec(self):
        if self._ketquahangviec.get("ngay") != ngayhomnay():
            self._ketquahangviec = {"ngay": ngayhomnay(), "viec": {}}

    def _loghv(self, noidung):
        self.moitruong._inlog(f"[HÀNG VIỆC] {noidung}")
