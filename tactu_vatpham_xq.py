# Phần vật phẩm: dùng thuốc / vật phẩm, nhặt, vứt, mua, sửa, sắp xếp / xếp chồng hành trang, bán rác, về bán rác.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import json
import math
import os
import random
import re
import threading
import time
import unicodedata

from hangso_xq import *
from luattuido_xq import tailuat, timluat, timluatbao, timluatcatkho, timhanhdongnhat, HANHDONG_GIU, HANHDONG_BAN, HANHDONG_VUT, CHIKHI_TRIEUHOIBAOTHU, \
    NHAT_NHAT, NHAT_UUTIEN, NHAT_KHONGNHAT, NOI_BANDOPK, NOI_DANGPK, NOI_KHAIKHOANG, NOI_PHOBAN, NOI_KHAC
from thongbao_xq import baosuco, LYDOTAMNGUNGTUXA
from moitruong_xq import MoiTruong, DOUUTIEN_THAP, DOUUTIEN_KHANCAP, DOUUTIEN_CAO, SOLUONGDOITUONGXUNGQUANHTOIDA, tinh_is_huongmatvediem
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam, canhbao
from tienich_xq import laynhomtodoitudongs, laynhanvattodoitudongs, donbangthoidiem

# Bán rác: máy chủ thỉnh thoảng bỏ lệnh sell (chắc do giới hạn tốc độ gửi lệnh) => gửi hết hàng đợi xong, chờ thêm chừng này giây cho
# túi cập nhật rồi bán lại các món còn trong túi, tối đa chừng này lần
THOIGIANCHOKIEMTRABANRAC = 1.
SOLANTHULAIBANRAC = 2
# Điều kiện hiệu ứng của bảng Tự động sử dụng vật phẩm (luattuido_xq TENHIEUUNGDUNG): khoá -> (mã hiệu ứng, True = cần đang CÓ hiệu
# ứng / False = cần CHƯA có, đọc lỗi thì coi như có hay không, is_hieuungcoloi, có giãn nhịp kiểm tra không).
# - Buff ("thieu_" món): đọc lỗi coi như đang có (khỏi dùng phí); giãn nhịp: lần kiểm tra cũng tính vào "giancach" của luật (đọc bảng
#   hiệu ứng tối đa mỗi giancach giây, như mốc 2,5s viết cứng trước đây)
# - Dã Tính Cuồng Lực (tâm pháp Đào Hoa Nguyên, mã 3191, có lợi): dùng theo cặp luật thuốc "chưa có" / "đang có" => đọc lỗi coi như
#   KHÔNG có để luật thường vẫn chạy (cả 2 cùng bỏ là không uống thuốc); không giãn nhịp (thuốc phải kịp ngay khi hết hồi)
# - Hiệu ứng xấu: đọc lỗi coi như không (như mã cũ), không giãn nhịp
HIEUUNGLUATDUNG = {
    "thieu_huyetthach": ((HIEUUNGKYNANG_HUYETTHACH,), False, True, 1, True),
    "thieu_phapluc": ((HIEUUNGKYNANG_PHAPLUCTHACH,), False, True, 1, True),
    "thieu_thiennguyen": ((HIEUUNGKYNANG_THIENNGUYENDON,), False, True, 1, True),
    "thieu_nganhanh": ((HIEUUNGKYNANG_NGANHANHTU,), False, True, 1, True),
    "thieu_xaloi": ((HIEUUNGKYNANG_XALOITU,), False, True, 1, True),
    "co_datinh": ((HIEUUNGKYNANG_DATINCUONGLUC,), True, False, 1, False),
    "thieu_datinh": ((HIEUUNGKYNANG_DATINCUONGLUC,), False, False, 1, False),
    "bikhongche": ((HIEUUNGKYNANG_THUCCOT, HIEUUNGKYNANG_THUCGIAP, HIEUUNGKYNANG_THIEUDOT, HIEUUNGKYNANG_THAUCOTDINH,
                    HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN), True, False, 0, False),
}
# Mua bù: cửa hàng chưa biết hàng thì mở để đọc (tactu_sumon_xq.batdau_mocuahang), mở hỏng thì chừng này giây sau mới thử lại
GIANCACHMOCUAHANGMUABU = 120.
# Về mua bù (món còn <= "thapnhat"): vừa về vì món nào thì chừng này giây sau mới xét lại món đó (NPC không bán / hết tiền thì khỏi chạy
# về liên tục); tới NPC rồi chờ mua tối đa chừng này giây; xét món thiếu cách nhau chừng này giây
THOIGIANCHOVEMUABULAI = 300.
THOIGIANCHOMUABU = 60.
GIANCACHKIEMTRAVEMUABU = 2.
# Về sửa đồ (độ bền món sửa được < _phantramvesuado %): desc lại đồ đang mặc cách nhau chừng này giây (độ bền giảm chậm), chờ mô tả
# tối đa chừng này giây; vừa về sửa thì chừng này giây sau mới xét lại (thiếu tiền / không tới được NPC thì khỏi chạy về liên tục)
GIANCACHKIEMTRAVESUADO = 60.
THOIGIANCHODOBENVESUADO = 3.
THOIGIANCHOVESUADOLAI = 300.
# Bảo thú vật phẩm: dùng vật phẩm là công tắc (đang có thì thu hồi, chưa có thì gọi ra), con gọi ra cộng chỉ số cho chủ, chỉ số nào ghi
# trong mô tả ("tăng 7% Ngoại Công cho chủ nhân", "gia tăng cho chủ nhân 7% Bạo Kích") => tra CHISONHANVAT_MAP ra ô cần theo dõi.
# Game không lưu chủ của đối tượng bảo thú nên không nhận theo đối tượng (dễ nhầm con cùng tên của người khác): dùng vật phẩm rồi xem
# chỉ số đó => tăng là vừa gọi ra, giảm là vừa thu hồi (Thìn: Ngoại Công ±180, Dần: Bạo Kích ±700, đo 2026-11-02). Nhớ mức nhảy ("dấu
# vân tay"); sau đó đúng các ô đó tụt cùng lúc (lệch tối đa SAISODAUVANTAYBAOTHU) là con đã mất. Chỉ theo dõi ô của chỉ số trong mô tả
# vì chỉ số khác tự đổi liên tục (Đào Hoa: Ngoại / Nội Kháng chớp ±77, Ngoại Công đổi theo nguyên khí)
THOIGIANCHOCHISOBAOTHUVATPHAM = 3.
SAISODAUVANTAYBAOTHU = 0.05
# Phòng dấu vân tay lệch (đổi đồ / lên cấp làm mức cộng khác): nghĩ đang có mà chừng này giây không thấy con nào cùng tên trong bảng
# đối tượng thì không chắc nữa, dùng vật phẩm để xét lại (công tắc: tụt thì dùng thêm lần nữa).
# Trước đây 15s và chỉ xét trong 18 ô (toàn màn hình) => cứ vài phút lại thu hồi rồi gọi lại con đang có (log 347 / 364, 2026-11-13):
# đo bảng đối tượng thấy bảo thú hay tụt sau chủ 17-21 ô khi chạy, có lúc còn bị client đánh id -1 vài giây. Giờ xét cả bảng
# (không giới hạn khoảng cách) và chờ lâu hơn; mất thật (hết giờ / đổi bản đồ) thì đã có nhánh chỉ số tụt đúng dấu vân tay
THOIGIANKHONGTHAYBAOTHUVATPHAM = 60.
# Cần dùng vật phẩm (chưa biết có / không, bảo thú vừa mất) thì chờ ngẫu nhiên trong khoảng này (giây) rồi mới dùng
THOIGIANCHONGAUNHIENBAOTHUVATPHAM = (3., 20.)

class TacTuVatPham:
    def _get_baothuvatphamocuoi(self):
        # Chỉ triệu hồi bảo thú vật phẩm đặt ở ô mở cuối cùng của hành trang (người chơi tự chọn con nào bằng cách đặt vào ô đó):
        # (vị trí, tên) nếu ô đó là bảo thú vật phẩm còn hạn, không thì None
        vitri = self.moitruong.get_soluongvatphamhanhtrangtoida()
        tenvatpham = self.moitruong.get_tenvatphamhanhtrang(vitri)
        if tenvatpham not in BAOTHUVATPHAMs or not self.moitruong.get_iddoituongvatphamhanhtrang(vitri):
            return None
        if "Hết hạn sử dụng" in (self.moitruong.get_motavatphamhanhtrang(vitri) or ""):
            if time.time() - self._thoidiemphatambaothuhethan > 60.:
                self._thoidiemphatambaothuhethan = time.time()
                canhbao(self.moitruong, "{} đã hết hạn sử dụng".format(tenvatpham), is_block = False)
                baosuco(self.moitruong, "vatpham", f"{tenvatpham} đã hết hạn sử dụng", giancach = 3600.)
            return None
        return vitri, tenvatpham

    def _get_dichchisobaothuvatpham(self, vitri, ten):
        # Các ô chỉ số bảo thú vật phẩm ten cộng cho chủ, đọc từ mô tả (chỉ số nhắc tới đầu tiên sau "triệu hồi"); None nếu chưa có mô
        # tả / chỉ số chưa biết ô (báo 1 lần, không dùng vật phẩm mù vì dùng là bật / tắt)
        if ten in self._dichchisobaothuvatpham_map:
            return self._dichchisobaothuvatpham_map[ten]
        if ten in CHISOBAOTHUVATPHAM_MAP:
            # Mô tả không ghi chỉ số (12 con Giáp - Chuột bản Niết Bàn): dùng chỉ số khai tay
            dichs = tuple(dich for tenchiso in CHISOBAOTHUVATPHAM_MAP[ten] for dich in CHISONHANVAT_MAP[tenchiso])
            if IS_LOGCAULENH: self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] {ten} cộng {CHISOBAOTHUVATPHAM_MAP[ten]} cho chủ (khai tay), theo dõi ô {[hex(dich) for dich in dichs]}")
            self._dichchisobaothuvatpham_map[ten] = dichs
            return dichs
        mota = unicodedata.normalize("NFC", self.moitruong.get_motavatphamhanhtrang(vitri) or "")
        if not mota:
            return None
        doan = mota.split("triệu hồi", 1)[-1]
        vitris = {tenchiso: doan.find(tenchiso) for tenchiso in CHISONHANVAT_MAP if tenchiso in doan}
        dichs = CHISONHANVAT_MAP[min(vitris, key = vitris.get)] if vitris else None
        if not dichs:
            canhbao(self.moitruong, f"{ten}: chưa biết chỉ số cộng cho chủ, không tự triệu hồi", is_block = False)
            self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] {ten}: mô tả không có chỉ số trong CHISONHANVAT_MAP, không tự triệu hồi. Mô tả: {mota!r}")
        elif IS_LOGCAULENH:
            self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] {ten} cộng {min(vitris, key = vitris.get)} cho chủ, theo dõi ô {[hex(dich) for dich in dichs]}")
        self._dichchisobaothuvatpham_map[ten] = dichs
        return dichs

    def get_baothuvatphamluu(self):
        # Lưu vào thiết lập (mỗi giây): chỉ khi đã chắc có / không và đang không chờ chỉ số nhảy; chưa chắc thì giữ bản đã nạp (chưa
        # dùng tới) để không ghi đè mất
        if self._is_cobaothuvatpham is not None and self._dauvantaybaothuvatpham and self._chisobaothuvatphamtruoc \
                and self._trangthaitrieuhoibaothuvatpham == 0:
            self._baothuvatphamluucuoi = {"ten": self._tendauvantaybaothuvatpham, "co": self._is_cobaothuvatpham,
                                          "dauvantay": list(self._dauvantaybaothuvatpham), "chisos": list(self._chisobaothuvatphamtruoc)}
        return self._baothuvatphamluucuoi or self._baothuvatphamluu

    def _is_khopdauvantaybaothu(self, chenhlechs, dau):
        # Chênh lệch chỉ số khớp dấu vân tay bảo thú vật phẩm: dau +1 vừa gọi ra, -1 vừa mất
        dauvantay = self._dauvantaybaothuvatpham
        return bool(dauvantay) and all(abs(c - dau * muc) <= max(2, muc * SAISODAUVANTAYBAOTHU) for c, muc in zip(chenhlechs, dauvantay))

    def _action_trieuhoibaothuvatpham(self):
        # Triệu hồi bảo thú vật phẩm ở ô cuối hành trang, nhận biết có / mất bằng chỉ số của chính mình (xem SAISODAUVANTAYBAOTHU).
        # Không gửi pf 4131.@ ("Đợi lệnh" / "Hành động"): câu trả lời không kèm tên thú, dính cả bảo thú kỹ năng Mao Sơn / Vân Mộng Cốc
        thoidiemhientai = time.time()
        baothuvatphamocuoi = self._get_baothuvatphamocuoi()
        if not baothuvatphamocuoi:
            return
        vitri, ten = baothuvatphamocuoi
        dichs = self._get_dichchisobaothuvatpham(vitri, ten)
        if not dichs:
            return
        if ten != self._tendauvantaybaothuvatpham:
            # Mới bật bot / người chơi đổi con khác vào ô cuối: chưa biết gì về con này
            self._tendauvantaybaothuvatpham = ten
            self._dauvantaybaothuvatpham = None
            self._is_cobaothuvatpham = None
            self._chisobaothuvatphamtruoc = None
            self._trangthaitrieuhoibaothuvatpham = 0
        chisos = self.moitruong.get_chisonhanvats(dichs)
        if not chisos:
            return
        chisotruoc = self._chisobaothuvatphamtruoc
        self._chisobaothuvatphamtruoc = chisos

        if self._trangthaitrieuhoibaothuvatpham == 1:
            chenhlechs = [a - b for a, b in zip(chisos, self._chisobaothuvatphamkhidung)]
            if all(c > 0 for c in chenhlechs) or all(c < 0 for c in chenhlechs):
                is_goira = chenhlechs[0] > 0
                self._dauvantaybaothuvatpham = [abs(c) for c in chenhlechs]
                self._is_cobaothuvatpham = is_goira
                self._thoidiemthaybaothuvatpham = thoidiemhientai
                self._trangthaitrieuhoibaothuvatpham = 0
                if IS_LOGCAULENH: self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] {ten} {'đã gọi ra' if is_goira else 'đang có nên vừa bị thu hồi'}, chỉ số nhảy {chenhlechs}")
                if is_goira:
                    self.action_lammoitrangthai()
                else:
                    # Vật phẩm là công tắc: vừa thu hồi con đang có thì chốc lát sau dùng lại để gọi ra
                    self._thoidiemsudungbaothuvatphamgannhat = thoidiemhientai - 3.
                    self._thoidiemduocdungbaothuvatpham = thoidiemhientai + random.uniform(1.5, 4.)
            elif thoidiemhientai - self._thoidiemsudungbaothuvatphamgannhat > THOIGIANCHOCHISOBAOTHUVATPHAM:
                # Chỉ số không nhảy (game không nhận lệnh dùng) hoặc nhảy lẫn lộn: 30s sau thử lại
                if IS_LOGCAULENH: self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] dùng {ten} {THOIGIANCHOCHISOBAOTHUVATPHAM}s chỉ số không nhảy rõ ({chenhlechs}), 30s sau thử lại")
                self._trangthaitrieuhoibaothuvatpham = 0
                self._thoidiemsudungbaothuvatphamgannhat = thoidiemhientai + 27.
            return

        if chisotruoc:
            chenhlechs = [a - b for a, b in zip(chisos, chisotruoc)]
            if self._is_cobaothuvatpham and self._is_khopdauvantaybaothu(chenhlechs, -1):
                # Hết giờ / đổi bản đồ / người chơi tự thu hồi
                if IS_LOGCAULENH: self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] chỉ số tụt đúng dấu vân tay {ten} {chenhlechs}: đã mất bảo thú")
                self._is_cobaothuvatpham = False
            elif not self._is_cobaothuvatpham and self._is_khopdauvantaybaothu(chenhlechs, 1):
                if IS_LOGCAULENH: self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] chỉ số tăng đúng dấu vân tay {ten} {chenhlechs}: bảo thú đã ra (người chơi tự gọi)")
                self._is_cobaothuvatpham = True
                self._thoidiemthaybaothuvatpham = thoidiemhientai

        if self._is_cobaothuvatpham:
            if thoidiemhientai - self._thoidiemkiemtrabaothuvatphamxungquanh > 2.:
                self._thoidiemkiemtrabaothuvatphamxungquanh = thoidiemhientai
                # Tên trong hành trang có thể bị cắt ("Thần Thú - Dần (Giới h"), đối tượng thì đủ tên => so phần đầu
                if any((self.moitruong.get_tendoituong(diachi) or "").startswith(ten) and self.moitruong.get_phantramsinhlucconlai(diachi) > 100
                       for diachi in self.moitruong.get_diachinhanvattontais()):
                    self._thoidiemthaybaothuvatpham = thoidiemhientai
                elif thoidiemhientai - self._thoidiemthaybaothuvatpham > THOIGIANKHONGTHAYBAOTHUVATPHAM:
                    if IS_LOGCAULENH: self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] {THOIGIANKHONGTHAYBAOTHUVATPHAM}s không thấy {ten} trong bảng đối tượng, dùng vật phẩm xét lại")
                    self._is_cobaothuvatpham = None
            if self._is_cobaothuvatpham:
                return

        if self._is_cobaothuvatpham is None and self._baothuvatphamluu:
            # Mới mở lại bot: so chỉ số với lúc lưu, khớp thì biết có / không mà khỏi dùng vật phẩm (dùng là bật / tắt, mọi nhân vật mở
            # cùng lúc thì bảo thú tắt bật cùng lúc, lộ)
            luu, self._baothuvatphamluu = self._baothuvatphamluu, None
            if luu.get("ten") == ten and luu.get("dauvantay") and len(luu.get("chisos") or ()) == len(chisos):
                self._dauvantaybaothuvatpham = list(luu["dauvantay"])
                chenhlechs = [a - b for a, b in zip(chisos, luu["chisos"])]
                if not any(chenhlechs):
                    self._is_cobaothuvatpham = luu["co"]
                elif luu["co"] and self._is_khopdauvantaybaothu(chenhlechs, -1):
                    self._is_cobaothuvatpham = False
                elif not luu["co"] and self._is_khopdauvantaybaothu(chenhlechs, 1):
                    self._is_cobaothuvatpham = True
                if IS_LOGCAULENH: self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] {ten} lúc lưu {'có' if luu['co'] else 'không có'}, chỉ số lệch {chenhlechs} => "
                                        f"{'chưa chắc, dùng vật phẩm xét lại' if self._is_cobaothuvatpham is None else ('đang có' if self._is_cobaothuvatpham else 'đang không có')}")
                self._thoidiemthaybaothuvatpham = thoidiemhientai
                if self._is_cobaothuvatpham:
                    return

        if thoidiemhientai - self._thoidiemsudungbaothuvatphamgannhat <= 3.:
            return
        if self._thoidiemduocdungbaothuvatpham is None:
            # Chờ ngẫu nhiên: nhiều nhân vật cùng mở bot / cùng mất bảo thú (đổi bản đồ) thì không bật / tắt cùng giây
            self._thoidiemduocdungbaothuvatpham = thoidiemhientai + random.uniform(*THOIGIANCHONGAUNHIENBAOTHUVATPHAM)
        if thoidiemhientai < self._thoidiemduocdungbaothuvatpham:
            return
        self._thoidiemduocdungbaothuvatpham = None
        self._chisobaothuvatphamkhidung = chisos
        self._thoidiemsudungbaothuvatphamgannhat = thoidiemhientai
        if self.action_sudungvatphamhanhtrangtaivitri(vitri, ten, delay = 0.):
            if IS_LOGCAULENH: self.moitruong._inlog(f"[TRIỆU HỒI BẢO THÚ] dùng {ten} ({'chưa biết có hay không' if self._is_cobaothuvatpham is None else 'chưa có'}), chờ chỉ số nhảy")
            self._thoidiemtamngungsudungkynang = max(self._thoidiemtamngungsudungkynang, thoidiemhientai + 0.5)
            self._tenbaothuvatphamdangtrieuhoi = ten
            self._trangthaitrieuhoibaothuvatpham = 1

    def _laybophapbaotheomau(self, tenmonphai):
        # Bộ 3 mức pháp bảo (cao, vừa, thấp) của phái trong PHAPBAOTHEOMAU_MAP; None = tắt tuỳ chọn hoặc phái không có bộ.
        # Thục Sơn Kiếm / Đao cùng tên môn phái "thucson", tách bằng _is_thucsondao như _laykhoakynangquantrong
        if not self._is_doiphapbaotheomau:
            return None
        if tenmonphai == "thucson":
            tenmonphai = "thucsondao" if self._is_thucsondao else "thucsonkiem"
        return PHAPBAOTHEOMAU_MAP.get(tenmonphai)

    def _laymucphapbaotheomau(self, phantramsinhluc, muchientai):
        # Mức 0 cao / 1 vừa / 2 thấp. Tụt máu: < _mauphapbaovua% xuống vừa, <= _mauphapbaothap% xuống thấp.
        # Đang đeo món mức thấp hơn thì chỉ đổi lên khi máu vượt ngưỡng + _dotrephapbao%, tránh đổi qua lại liên tục khi máu
        # dao động quanh ngưỡng (người dùng báo 2026-11-12). Ngưỡng thấp nhập >= ngưỡng vừa thì ép xuống dưới ngưỡng vừa 1%
        nguongvua = self._mauphapbaovua
        nguongthap = min(self._mauphapbaothap, nguongvua - 1)
        if phantramsinhluc >= nguongvua:
            muc = 0
        elif phantramsinhluc > nguongthap:
            muc = 1
        else:
            muc = 2
        if muchientai is not None and muc < muchientai:
            if phantramsinhluc >= nguongvua + self._dotrephapbao:
                muc = 0
            elif phantramsinhluc >= nguongthap + self._dotrephapbao:
                muc = min(1, muchientai)
            else:
                muc = muchientai
        return muc

    def _laydobenphapbaotui(self, vitri, iddoituong, ten):
        # Độ bền món trong túi ở ô vitri: (bền, tối đa), None = món không có độ bền (vd Thượng Phương Bảo Kiếm), False = chưa đọc được.
        # Mỗi món desc 1 lần (chờ tối đa 1s), lưu theo id; desc không ra thì THOIGIANTHULAIDOBENPHAPBAOTUI giây sau mới thử lại
        daluu = self._dobenphapbaotui_map.get(iddoituong)
        if daluu and (daluu[1] is not False or time.time() - daluu[0] < THOIGIANTHULAIDOBENPHAPBAOTUI):
            return daluu[1]
        mota = self.moitruong.get_motavatphamhanhtrang(vitri, thoigianchotoida = 1., is_napmoi = True) or ""
        mota = re.sub(r'\x1b[a-zA-Z0-9]', '', mota)
        # Mô tả theo ô: dòng đầu phải là tên món này, không thì là mô tả cũ của món khác từng ở ô đó
        if not mota.strip() or ten not in mota.strip().split("\n")[0]:
            doben = False
        else:
            doben = self.moitruong.get_dobenmota(mota)
            if doben is None and ten not in PHAPBAOKHONGHUHONGs:
                # Có tên mà chưa có dòng độ bền: có thể game chưa ghi xong mô tả, đọc lại 1 lần; vẫn không có thì coi như
                # món không có độ bền
                time.sleep(0.3)
                mota = re.sub(r'\x1b[a-zA-Z0-9]', '', self.moitruong.get_motavatphamhanhtrangcosan(vitri) or "")
                doben = self.moitruong.get_dobenmota(mota)
            # Khí huyết pháp bảo (Cửu Long Thần Hỏa Trảo) đọc cùng mô tả: không hồi khi nằm trong túi nên lưu như độ bền
            khihuyet = self.moitruong.get_khihuyetphapbaomota(mota)
            if khihuyet:
                self._khihuyetphapbaotui_map[iddoituong] = khihuyet
            else:
                self._khihuyetphapbaotui_map.pop(iddoituong, None)
        self._dobenphapbaotui_map[iddoituong] = (time.time(), doben)
        khihuyet = self._khihuyetphapbaotui_map.get(iddoituong)
        self.moitruong._inlog("[PHÁP BẢO] độ bền {} (id {:x}, ô {}): {}{}".format(
            ten, iddoituong, vitri, "chưa đọc được" if doben is False else "không có" if doben is None else "{}/{}".format(*doben),
            ", khí huyết {}/{}".format(*khihuyet) if khihuyet and doben is not False else ""))
        return doben

    def _timphapbaoconbentrongtui(self, tens, chuchua = None, is_uutienkhihuyet = False):
        # (ô, id, tên) của món đầu tiên trong túi tên thuộc tens (theo thứ tự tens), rồi tới món tên chứa chuchua; bỏ món hỏng
        # (độ bền 0/x) và món chưa đọc được độ bền. None = không có.
        # is_uutienkhihuyet: trong các món dùng được chọn món còn khí huyết pháp bảo nhiều nhất (Trảo), món không có dòng khí huyết xếp cuối
        hanhtrang_map = self.moitruong.get_danhsachvatphamhanhtrang_map()
        tenxets = [ten for ten in tens if ten in hanhtrang_map]
        if chuchua:
            tenxets += sorted(ten for ten in hanhtrang_map if ten and chuchua in ten and ten not in tenxets)
        totnhat = None
        for ten in tenxets:
            for vitri, iddoituong in hanhtrang_map[ten]:
                if not iddoituong or vitri >= VITRITRANGBIDAUTIEN:
                    continue
                doben = self._laydobenphapbaotui(vitri, iddoituong, ten)
                if doben is None or (doben and doben[0] > 0):
                    if not is_uutienkhihuyet:
                        return vitri, iddoituong, ten
                    khihuyet = self._khihuyetphapbaotui_map.get(iddoituong)
                    diem = khihuyet[0] if khihuyet else -1
                    if totnhat is None or diem > totnhat[0]:
                        totnhat = (diem, (vitri, iddoituong, ten))
        return totnhat[1] if totnhat else None

    def _timtraotrongtui(self, dieukien, khoa):
        # Trảo trong túi còn độ bền, đã đọc được khí huyết, thoả dieukien((hiện tại, tối đa)); chọn món có khoa(khí huyết) nhỏ nhất.
        # Trả (ô, id, tên, (hiện tại, tối đa)) hoặc None
        hanhtrang_map = self.moitruong.get_danhsachvatphamhanhtrang_map()
        totnhat = None
        for ten in PHAPBAOTHEOMAU_TRAO:
            for vitri, iddoituong in hanhtrang_map.get(ten, ()):
                if not iddoituong or vitri >= VITRITRANGBIDAUTIEN:
                    continue
                doben = self._laydobenphapbaotui(vitri, iddoituong, ten)
                if doben is False or (doben and doben[0] <= 0):
                    continue
                khihuyet = self._khihuyetphapbaotui_map.get(iddoituong)
                if not khihuyet or not dieukien(khihuyet):
                    continue
                if totnhat is None or khoa(khihuyet) < khoa(totnhat[3]):
                    totnhat = (vitri, iddoituong, ten, khihuyet)
        return totnhat

    def _xoayvongtraotheokhihuyet(self, tenphapbaohientai, mucphapbaos, idbandohientai, phantramsinhlucconlai):
        # Xoay vòng Cửu Long Thần Hỏa Trảo theo khí huyết pháp bảo (người dùng dặn 2026-11-14). Trả (is_giu, is_daralenh):
        # is_giu = đang giữ / vừa đeo Trảo để hồi, đổi theo sinh lực lượt này bỏ qua (không thì nó đổi lại Nhiếp Hồn Linh / Chuông).
        # - Nghỉ (bản đồ không PK, không có mục tiêu quá THOIGIANNGHIXOAYTRAO giây): Trảo chỉ hồi khi đeo nên đeo Trảo chưa đầy;
        #   đang đeo Trảo chưa đầy (hoặc chưa đọc được) thì giữ, đầy rồi thì đổi sang Trảo chưa đầy ít khí huyết nhất trong túi.
        #   Đang đeo món khác thì chỉ thay khi bật đổi theo sinh lực cho phái này (dù sao bot cũng tự chọn pháp bảo), không thì để yên
        # - Đang đánh: Trảo đang đeo hết khí huyết (0/x) thì đeo Trảo khác còn khí huyết nhiều nhất; máu đã xuống mức tháo pháp bảo thì thôi
        if not self._is_xoayvongtrao or self._tenphapbaocu is not None:
            return False, False
        if tenphapbaohientai and (PHAPBAOKHAIKHOANG in tenphapbaohientai or PHAPBAOHAIDUOC in tenphapbaohientai):
            return False, False
        iddeo = self.moitruong.get_iddoituongvatphamhanhtrang(VITRITRANGBI_PHAPBAO)
        is_deotrao = bool(iddeo) and tenphapbaohientai in PHAPBAOTHEOMAU_TRAO
        khihuyetdeo = None
        if is_deotrao and self._khihuyetphapbaodeo and self._khihuyetphapbaodeo[0] == iddeo:
            khihuyetdeo = self._khihuyetphapbaodeo[1:]
        is_nghi = idbandohientai in BANDOKHONGPKs and time.time() - self._thoidiemcomuctieugannhat > THOIGIANNGHIXOAYTRAO
        if is_nghi:
            if is_deotrao and (khihuyetdeo is None or khihuyetdeo[0] < khihuyetdeo[1]):
                return True, False
            if not is_deotrao and not mucphapbaos:
                return False, False
            if time.time() - self._thoidiemxetxoaytrao < 3.:
                return False, False
            self._thoidiemxetxoaytrao = time.time()
            trao = self._timtraotrongtui(lambda kh: kh[0] < kh[1], lambda kh: kh[0] / max(1, kh[1]))
            if not trao:
                return False, False
            if self._deophapbaotaivitri(trao[0], trao[1]):
                self.moitruong._inlog("[PHÁP BẢO] {}: nghỉ, {} -> {} (id {:x}, khí huyết {}/{}) để hồi khí huyết".format(
                    self.moitruong.get_tendoituong(), "{} đầy {}/{}".format(tenphapbaohientai, *khihuyetdeo) if khihuyetdeo
                    else (tenphapbaohientai or "(không)"), trao[2], trao[1], *trao[3]))
                return True, True
            return False, False
        if not is_deotrao or not khihuyetdeo or khihuyetdeo[0] > 0:
            return False, False
        if phantramsinhlucconlai <= (min(self._mauphapbaothap, self._mauphapbaovua - 1) if mucphapbaos else 25):
            return False, False
        if time.time() - self._thoidiemxetxoaytrao < 2.:
            return False, False
        self._thoidiemxetxoaytrao = time.time()
        trao = self._timtraotrongtui(lambda kh: kh[0] > 0, lambda kh: -kh[0])
        if not trao:
            return False, False
        if self._deophapbaotaivitri(trao[0], trao[1]):
            self.moitruong._inlog("[PHÁP BẢO] {}: {} hết khí huyết (0/{}), đổi sang {} (id {:x}, khí huyết {}/{})".format(
                self.moitruong.get_tendoituong(), tenphapbaohientai, khihuyetdeo[1], trao[2], trao[1], *trao[3]))
            return False, True
        return False, False

    def _deophapbaotaivitri(self, vitri, iddoituong):
        # "use <id>#" như chuột phải (đổi được cả khi Dã Tính Cuồng Lực, "use2" thì không); ô đã đổi món thì thôi
        if self.moitruong.get_iddoituongvatphamhanhtrang(vitri) != iddoituong:
            return False
        if self.moitruong.action_sudungvatpham(iddoituong, False, delay = 0., is_use2 = False):
            self._thoidiemsudungvatphamgannhat = time.time()
            self._thoidiemhoandoiphapbao = time.time()
            # Món vừa đeo: kiểm tra độ bền ngay
            self._thoidiemtruyvandobenphapbao = 0.
            return True
        return False

    def _doiphapbaotheomau(self, tenphapbaohientai, phapbaomoi, phantramsinhlucconlai):
        vitri, iddoituong, ten = phapbaomoi
        if self._deophapbaotaivitri(vitri, iddoituong):
            self.moitruong._inlog("[PHÁP BẢO] {}: máu {}%, đổi pháp bảo {} -> {}".format(
                self.moitruong.get_tendoituong(), int(phantramsinhlucconlai), tenphapbaohientai or "(không)", ten))
            return True
        return False

    def _kiemtraphapbaodangdeohong(self, tenphapbaohientai, mucphapbaos):
        # Pháp bảo đang đeo hỏng (độ bền 0/x) thì đeo món tương tự còn bền trong túi: cùng tên, cùng mức trong PHAPBAOTHEOMAU_MAP
        # của phái (các cách viết tên), món có "Cuốc" / "Liềm" thì món nào cũng chứa chữ đó. True = vừa gửi lệnh đổi.
        # Độ bền đọc từ mô tả: "desc 7" lại mỗi THOIGIANKIEMTRADOBENPHAPBAO giây (hoặc khi đổi món), lượt sau đọc kết quả
        iddeo = self.moitruong.get_iddoituongvatphamhanhtrang(VITRITRANGBI_PHAPBAO)
        if not iddeo or not tenphapbaohientai:
            return False
        # Món đang đeo thì mòn (Trảo thì khí huyết đổi): lần sau nằm trong túi phải đọc lại
        self._dobenphapbaotui_map.pop(iddeo, None)
        self._khihuyetphapbaotui_map.pop(iddeo, None)
        # Đang đeo Trảo (xoay vòng theo khí huyết bật) thì desc dày hơn để biết sớm lúc hết khí huyết / đã đầy
        giancach = THOIGIANKIEMTRAKHIHUYETTRAO if self._is_xoayvongtrao and tenphapbaohientai in PHAPBAOTHEOMAU_TRAO \
            else THOIGIANKIEMTRADOBENPHAPBAO
        if iddeo != self._idtruyvandobenphapbao or time.time() - self._thoidiemtruyvandobenphapbao > giancach:
            if self.moitruong.action_truyvanmotatrangbi(VITRITRANGBI_PHAPBAO):
                self._idtruyvandobenphapbao = iddeo
                self._thoidiemtruyvandobenphapbao = time.time()
            return False
        mota = re.sub(r'\x1b[a-zA-Z0-9]', '', self.moitruong.get_motavatphamhanhtrangcosan(VITRITRANGBI_PHAPBAO) or "")
        if not mota.strip() or tenphapbaohientai not in mota.strip().split("\n")[0]:
            return False
        khihuyet = self.moitruong.get_khihuyetphapbaomota(mota)
        if khihuyet:
            self._khihuyetphapbaodeo = (iddeo, khihuyet[0], khihuyet[1])
        doben = self.moitruong.get_dobenmota(mota)
        if not doben or doben[0] > 0:
            return False
        tens = [tenphapbaohientai]
        for ds in (mucphapbaos or ()):
            if tenphapbaohientai in ds:
                tens += [ten for ten in ds if ten not in tens]
        chuchua = next((chu for chu in (PHAPBAOKHAIKHOANG, PHAPBAOHAIDUOC) if chu in tenphapbaohientai), None)
        phapbaomoi = self._timphapbaoconbentrongtui(tens, chuchua)
        if phapbaomoi and self._deophapbaotaivitri(phapbaomoi[0], phapbaomoi[1]):
            self.moitruong._inlog("[PHÁP BẢO] {}: pháp bảo {} hỏng ({}/{}), đổi sang {} (id {:x})".format(
                self.moitruong.get_tendoituong(), tenphapbaohientai, doben[0], doben[1], phapbaomoi[2], phapbaomoi[1]))
            return True
        if not phapbaomoi and time.time() - self._thoidiemcanhbaophapbaohong > 300.:
            self._thoidiemcanhbaophapbaohong = time.time()
            self.moitruong._inlog("[PHÁP BẢO] {}: pháp bảo {} hỏng ({}/{}), trong túi không có món tương tự còn độ bền".format(
                self.moitruong.get_tendoituong(), tenphapbaohientai, doben[0], doben[1]))
        return False

    def _thaophapbao(self, tenphapbaohientai, phantramsinhlucconlai, is_luutencu = True):
        # Tháo pháp bảo đang đeo: "remove <vị trí>" đếm ô trang bị từ 1 như desc đồ đang mặc (pháp bảo = 7), cần túi còn ô trống.
        # is_luutencu: lưu tên để máu hồi lại thì đeo lại (đổi theo sinh lực thì không cần, tự đeo theo mức). False = túi đầy
        if not self.moitruong.get_iddoituongvatphamhanhtrang(VITRITRANGBI_PHAPBAO):
            return False
        if all(self.moitruong.get_iddoituongvatphamhanhtrang(vitri) for vitri in self.moitruong.get_danhsachvitrimohanhtrang()):
            return False
        if self.moitruong.action_thucthicaulenh("remove {}".format(VITRITRANGBI_PHAPBAO - VITRITRANGBIDAUTIEN + 1), douutien = DOUUTIEN_CAO):
            self._thoidiemhoandoiphapbao = time.time()
            if not is_luutencu:
                self.moitruong._inlog("[PHÁP BẢO] {}: máu {}%, tháo pháp bảo {}".format(self.moitruong.get_tendoituong(), int(phantramsinhlucconlai), tenphapbaohientai))
            elif self._tenphapbaocu is None:
                self._tenphapbaocu = tenphapbaohientai
                self._mucsinhluckhihoandoi = phantramsinhlucconlai
                self.moitruong._inlog("[PHÁP BẢO] {}: máu {}%, không có {} -> tháo pháp bảo {}".format(
                    self.moitruong.get_tendoituong(), phantramsinhlucconlai, PHAPBAOKHONGHUHONGs[0], tenphapbaohientai))
        return True

    def _action_dunganxaphu(self):
        # Ân Xá Phù: mỗi lá giảm 100 điểm Ác Danh PK (KDK_DIEMPK). Trước đây gửi "use ! <id>#" mỗi lượt (~0.5s): 2026-11-13 Ngốc PK 400,
        # Kng PK 100 spam 7 phút mà số lá trong túi và PK không đổi => "use !" không ăn với món này (giống đồ tân thủ trong
        # VATPHAMDUNGUSE2s, dùng có hộp hỏi xác nhận). Nay gửi 3s/lần, thử "use2 <id>#" trước; PK không giảm thì đổi qua "use !",
        # cách nào làm PK giảm thì giữ cách đó
        diempk = self.moitruong.get_diempk()
        s = self._anxaphu
        if not diempk or diempk <= 0:
            s["pk"] = None
            s["hut"] = 0
            return
        if time.time() - s["luc"] < 3.:
            return
        tencach = ("use2", "use !")
        if s["pk"] is not None:
            if diempk < s["pk"]:
                self.moitruong._inlog("[ÂN XÁ PHÙ] {}: PK {} -> {} bằng \"{}\"".format(
                    self.moitruong.get_tendoituong(), s["pk"], diempk, tencach[s["cach"]]))
                s["hut"] = 0
            else:
                s["hut"] += 1
                s["cach"] ^= 1
                if s["hut"] in (2, 10) or s["hut"] % 100 == 0:
                    self.moitruong._inlog("[ÂN XÁ PHÙ] {}: gửi {} lần mà PK vẫn {} (cả use2 lẫn use !), thử tiếp \"{}\"".format(
                        self.moitruong.get_tendoituong(), s["hut"], diempk, tencach[s["cach"]]))
        if self.action_sudungvatphamhanhtrang(ANXAPHU, is_boquaxacnhan = True, delay = 0., is_use2 = s["cach"] == 0):
            s["luc"] = time.time()
            s["pk"] = diempk

    def action_tudongsudungvatpham(self):
        if self._is_tudongsudungvatpham:
            if self.moitruong.get_is_nhanvatdachet():
                return

            # Đọc tên hành trang 1 lần mỗi lượt để kiểm tra có vật phẩm hay không (trước đây mỗi vật phẩm quét lại cả hành trang,
            # vật phẩm không có thì lượt nào cũng quét vì mốc thời gian chỉ cập nhật khi dùng được). Dùng thì vẫn tìm lại id mới nhất
            tenvatphamhanhtrangs = set(self.moitruong.get_danhsachtenvatphamhanhtrang())
            co = tenvatphamhanhtrangs.__contains__

            self._action_trieuhoibaothuvatpham()

            idbandohientai = self.moitruong.get_idbandohientai()
            is_bandokhongpk = idbandohientai in BANDOKHONGPKs
            is_bandopk = not is_bandokhongpk
            is_dangbatpk = self.moitruong.get_idmaupk() != MAUPK_HOABINH
            tenmonphai = self.moitruong.get_tenmonphai()

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()

            # Thuốc, Huyết Thạch, Pháp Lực Thạch, buff, Khu Ma Tán, Bát Tiên Đơn: theo bảng "Tự động sử dụng vật phẩm" (tab Hành trang)
            self._dungvatphamtheoluat(co, idbandohientai, is_bandopk, is_dangbatpk, tenmonphai, phantramsinhlucconlai)

            if co(ANXAPHU):
                self._action_dunganxaphu()

            # Máu thấp: lưu tên pháp bảo đang đeo (đọc ô trang bị, không dò hành trang) rồi đổi sang pháp bảo không hư hỏng;
            # máu hồi lại (cao hơn lúc đổi 15%) thì tìm pháp bảo cũ trong hành trang đeo lại, xác nhận bằng cách đọc lại ô trang bị
            tenphapbaohientai = self.moitruong.get_tenphapbaohientai()
            # Vừa ra lệnh đổi: game chưa kịp cập nhật ô trang bị thì chưa xét, tránh tưởng đã đeo lại / người chơi tự đổi
            is_dangchodoiphapbao = time.time() - self._thoidiemhoandoiphapbao < 2.

            # Đổi pháp bảo theo sinh lực (tuỳ chọn tab Chiến đấu, PHAPBAOTHEOMAU_MAP: Đào Hoa, Thục Sơn Kiếm, Vân Mộng Cốc), thay cho cách
            # lưu / đeo lại pháp bảo cũ ở dưới.
            # Đổi bằng "use <id>#" như chuột phải: "use2" (lệnh nút Xác Nhận, dùng cho Trảo tân thủ) bị máy chủ chặn khi đang
            # Dã Tính Cuồng Lực - "Trạng thái Cuồng Bạo không thể đổi trang bị" (người dùng báo 2026-11-12), chuột phải thì đổi được.
            # Mức cao / vừa: món cần đeo không có trong túi thì giữ nguyên.
            # Mức thấp (người dùng dặn 2026-11-12):
            # - Không Dã Tính Cuồng Lực: đang đeo Thượng Phương Bảo Kiếm / món có "Cuốc" / "Liềm" / không đeo gì thì giữ nguyên,
            #   món khác thì tháo ("remove 7"); túi đầy không tháo được thì để cách cũ bên dưới (đổi Kiếm / cảnh báo)
            # - Đào Hoa Nguyên đang Dã Tính Cuồng Lực: máy chủ không cho tháo đồ => phải đổi sang Thượng Phương Bảo Kiếm; không có
            #   Kiếm thì để cách cũ cảnh báo. Đọc hiệu ứng lỗi thì coi như đang Dã Tính (đổi Kiếm chứ không tháo).
            #   Phái khác không bao giờ đổi sang Kiếm, chỉ tháo (người dùng dặn 2026-11-13)
            # Đang đeo Cuốc / Liềm (khai khoáng / hái dược) mà máu chưa xuống mức thấp thì không đụng tới
            # Chạy ở mọi bản đồ, cả thành / quốc gia không PK (người dùng dặn 2026-11-12: làm Sư Môn ở Tề Quốc máu < 50% mà không đổi)
            is_vuadoiphapbao = is_dangchodoiphapbao
            is_daralenhdoi = False

            def is_daohoadatinh():
                # Chỉ Đào Hoa Nguyên đang Dã Tính Cuồng Lực (không tháo đồ được) mới đổi sang Thượng Phương Bảo Kiếm khi máu thấp
                return tenmonphai == "daohoanguyen" and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), macdinh = True, is_hieuungcoloi = 1)

            mucphapbaos = self._laybophapbaotheomau(tenmonphai)

            # Xoay vòng Trảo theo khí huyết chạy trước: đang nghỉ mà giữ / vừa đeo Trảo để hồi thì bỏ qua đổi theo sinh lực lượt này
            is_giutrao = False
            if not is_dangchodoiphapbao:
                is_giutrao, is_lenhtrao = self._xoayvongtraotheokhihuyet(tenphapbaohientai, mucphapbaos, idbandohientai, phantramsinhlucconlai)
                if is_lenhtrao:
                    is_daralenhdoi = is_dangchodoiphapbao = True

            if mucphapbaos and is_giutrao:
                self._tenphapbaocu = None
                is_dangchodoiphapbao = True
            elif mucphapbaos:
                is_cuocliem = bool(tenphapbaohientai) and (PHAPBAOKHAIKHOANG in tenphapbaohientai or PHAPBAOHAIDUOC in tenphapbaohientai)
                # Không đeo gì coi như mức thấp (vừa tháo ở mức thấp): phải hồi qua ngưỡng + độ trễ mới đeo lại, không thì đổi liên tục
                if not tenphapbaohientai or is_cuocliem:
                    muchientai = 2
                else:
                    muchientai = next((i for i, ds in enumerate(mucphapbaos) if tenphapbaohientai in ds), None)
                muc = self._laymucphapbaotheomau(phantramsinhlucconlai, muchientai)
                tenphapbaocans = mucphapbaos[muc]
                is_cotrongtui = any(co(ten) for ten in tenphapbaocans)

                def doi():
                    # Chỉ đeo món còn độ bền (_timphapbaoconbentrongtui bỏ món 0/x); món cần đều hỏng thì giữ nguyên
                    # Trảo: chọn cái còn khí huyết nhiều nhất (_xoayvongtraotheokhihuyet)
                    phapbaomoi = self._timphapbaoconbentrongtui(tenphapbaocans, is_uutienkhihuyet = self._is_xoayvongtrao) if is_cotrongtui else None
                    return bool(phapbaomoi) and self._doiphapbaotheomau(tenphapbaohientai, phapbaomoi, phantramsinhlucconlai)

                is_daxuly = False
                if (is_cuocliem and muc < 2) or tenphapbaohientai in tenphapbaocans:
                    is_daxuly = True
                elif muc < 2:
                    is_daxuly = True
                    if not is_dangchodoiphapbao:
                        is_daralenhdoi = doi()
                elif is_daohoadatinh():
                    if is_cotrongtui:
                        is_daxuly = True
                        if not is_dangchodoiphapbao:
                            is_daralenhdoi = doi()
                elif not tenphapbaohientai or is_cuocliem or is_dangchodoiphapbao:
                    is_daxuly = True
                elif self._thaophapbao(tenphapbaohientai, phantramsinhlucconlai, is_luutencu = False):
                    is_daxuly = is_daralenhdoi = True
                if is_daxuly:
                    self._tenphapbaocu = None
                    # Đã xử lý: bỏ qua đổi pháp bảo kiểu cũ bên dưới
                    is_dangchodoiphapbao = True

            # Pháp bảo đang đeo hỏng (0/x): đổi món tương tự còn bền, mọi phái, có bật tuỳ chọn theo sinh lực hay không
            # (người dùng dặn 2026-11-12). Lượt này vừa gửi lệnh đổi / tháo thì để lượt sau
            if not is_vuadoiphapbao and not is_daralenhdoi and self._kiemtraphapbaodangdeohong(tenphapbaohientai, mucphapbaos):
                is_dangchodoiphapbao = True

            if self._tenphapbaocu is not None and not is_dangchodoiphapbao:
                if self._tenphapbaocu and tenphapbaohientai == self._tenphapbaocu:
                    self.moitruong._inlog("[PHÁP BẢO] {}: đã đeo lại pháp bảo {}".format(self.moitruong.get_tendoituong(), self._tenphapbaocu))
                    self._tenphapbaocu = None
                elif tenphapbaohientai not in (*PHAPBAOKHONGHUHONGs, ""):
                    # Không còn đeo pháp bảo không hư hỏng / đã tháo (người chơi tự đổi): thôi không đeo lại
                    self.moitruong._inlog("[PHÁP BẢO] {}: pháp bảo đang đeo là {}, bỏ đeo lại {}".format(self.moitruong.get_tendoituong(), tenphapbaohientai or "(không)", self._tenphapbaocu))
                    self._tenphapbaocu = None
                elif phantramsinhlucconlai >= self._mucsinhluckhihoandoi + 15 and time.time() - self._thoidiemthumaclaiphapbao > 2.:
                    if not self._tenphapbaocu:
                        # Trước đó không đeo pháp bảo nào: không có gì để đeo lại
                        self._tenphapbaocu = None
                    else:
                        # Chỉ đeo lại món cùng tên còn độ bền (món đã hỏng 0/x thì thôi)
                        phapbaocu = self._timphapbaoconbentrongtui([self._tenphapbaocu])
                        self._thoidiemthumaclaiphapbao = time.time()
                        if phapbaocu is None:
                            self.moitruong._inlog("[PHÁP BẢO] {}: không còn {} còn độ bền để đeo lại".format(self.moitruong.get_tendoituong(), self._tenphapbaocu))
                            self._tenphapbaocu = None
                        else:
                            self._deophapbaotaivitri(phapbaocu[0], phapbaocu[1])

            if ((phantramsinhlucconlai <= 25 and idbandohientai not in (BANDO_CHIENTRUONG, BANDO_COMO, BANDO_TIVO, *BANDOKHONGPKs)) or (phantramsinhlucconlai < 15 and idbandohientai == BANDO_COMO)) \
                    and not is_dangchodoiphapbao and tenphapbaohientai not in PHAPBAOKHONGHUHONGs:
                # Chỉ Đào Hoa đang Dã Tính Cuồng Lực mới đổi sang Kiếm; còn lại tháo thẳng (người dùng dặn 2026-11-13)
                is_doikiem = is_daohoadatinh()
                for phapbaokhonghuhong in (PHAPBAOKHONGHUHONGs if is_doikiem else ()):
                    if not co(phapbaokhonghuhong):
                        continue
                    if self.action_sudungvatphamhanhtrang(phapbaokhonghuhong, delay = 0.):
                        self._thoidiemhoandoiphapbao = time.time()
                        # Đổi lại lần nữa khi chưa kịp đeo lại pháp bảo cũ: vẫn giữ tên pháp bảo cũ ban đầu
                        if self._tenphapbaocu is None:
                            self._tenphapbaocu = tenphapbaohientai
                            self._mucsinhluckhihoandoi = phantramsinhlucconlai
                            self.moitruong._inlog("[PHÁP BẢO] {}: máu {}%, lưu pháp bảo đang đeo: {} -> đổi sang {}".format(
                                self.moitruong.get_tendoituong(), phantramsinhlucconlai, tenphapbaohientai or "(không)", phapbaokhonghuhong))
                    break
                else:
                    # Không có pháp bảo không hư hỏng: tháo thẳng pháp bảo đang đeo ("remove 7").
                    # Thượng Phương Bảo Kiếm chỉ cần cho Đào Hoa đang Dã Tính Cường Lực / Kim Cường (không tháo đồ được)
                    if tenphapbaohientai and self._thaophapbao(tenphapbaohientai, phantramsinhlucconlai):
                        pass
                    # Máu thấp mà không đổi / tháo được pháp bảo (túi đầy): nhắc 60s một lần, Telegram 30 phút một lần
                    elif tenphapbaohientai and time.time() - self._thoidiemcanhbaokhongphapbao > 60.:
                        self._thoidiemcanhbaokhongphapbao = time.time()
                        lydo = f"không có {PHAPBAOKHONGHUHONGs[0]} để đổi (Dã Tính), " if is_doikiem else ""
                        canhbao(self.moitruong, f"Máu thấp: {lydo}túi đầy không tháo được pháp bảo", is_block = False)
                        baosuco(self.moitruong, "vatpham", f"Máu {int(phantramsinhlucconlai)}%: {lydo}"
                                f"túi đầy không tháo được pháp bảo", khoa = "khongphapbaokhonghuhong", giancach = 1800.)

            if self.moitruong.get_idnguoichoi() == 59844:
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Luyện Đơn",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if co(sachcanhoc) and self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

    def _dungvatphamtheoluat(self, co, idbandohientai, is_bandopk, is_dangbatpk, tenmonphai, phantramsinhlucconlai):
        # Bảng "dung" trong luattuido.json (sửa ở tab Hành trang): xét MỌI luật bật, luật đủ điều kiện thì dùng món đầu tiên còn trong túi
        # và đã hết thời gian hồi (_sudungvatphamhoi). Mỗi luật có mốc riêng trong _thoidiemluatdung: dùng được thì chờ "giancach" giây
        # mới xét lại; luật có điều kiện hiệu ứng thì cả lần kiểm tra hiệu ứng cũng tính (đọc bảng hiệu ứng tối đa mỗi "giancach" giây,
        # như mốc 2,5s viết cứng trước đây)
        luats = tailuat()["dung"]
        if not luats:
            return
        bayh = time.time()
        is_dangpk = is_dangbatpk and is_bandopk
        is_phoban = not is_dangpk and idbandohientai in BANDOPHOBANs
        # Đọc lười: chỉ đọc khi có luật cần
        docs = {}

        def doc(khoa):
            if khoa not in docs:
                mt = self.moitruong
                if khoa == "noiluc":
                    docs[khoa] = mt.get_phantramnoilucconlai()
                elif khoa == "matsinhluc":
                    docs[khoa] = mt.get_sinhluctoida() - mt.get_sinhlucconlai()
                elif khoa == "matnoiluc":
                    docs[khoa] = mt.get_noiluctoida() - mt.get_noilucconlai()
                elif khoa == "theluc":
                    docs[khoa] = mt.get_thelucconlai()
                elif khoa == "khongphobanrieng":
                    # Phong Yêu Kính, Lăng Ly Sơn (3 tầng), Tập Kích Môn Phái: người chơi không muốn tốn thuốc ở đây
                    docs[khoa] = idbandohientai in (BANDO_LANGLYSON1, BANDO_LANGLYSON2, BANDO_LANGLYSON3) \
                        or self._is_trongphongyeu() or mt.get_is_bandotapkichmonphai()
            return docs[khoa]

        for luat in luats:
            # Món vừa được 1 luật khác dùng thì chờ hết giãn cách của luật đó (vd 3 luật Huyết Thạch: luật đầu dùng xong, hiệu ứng chưa
            # kịp hiện thì luật sau tưởng chưa có mà dùng thêm lần nữa; mã cũ gộp 1 lần kiểm tra mỗi 2,5s nên không bị)
            if not luat["bat"]:
                continue
            vatphams = [ten for ten in luat["vatpham"] if co(ten) and bayh >= self._thoidiemluatdung.get(("cho", ten), 0.)]
            if not vatphams:
                continue
            khoa = (tuple(luat["vatpham"]), luat["noi"], luat["hieuung"], luat["monphai"], luat["sinhluc"], luat["noiluc"])
            if bayh - self._thoidiemluatdung.get(khoa, 0.) < luat["giancach"]:
                continue
            noi = luat["noi"]
            if noi == NOI_BANDOPK and not is_bandopk or noi == NOI_DANGPK and not is_dangpk \
                    or noi == NOI_KHAIKHOANG and not (is_bandopk and (is_dangbatpk or self._is_tudongkhaikhoang)) \
                    or noi == NOI_PHOBAN and not is_phoban or noi == NOI_KHAC and (is_dangpk or is_phoban):
                continue
            if luat["monphai"] and luat["monphai"] != tenmonphai:
                continue
            if luat["chikhidanh"] and not self._is_tudongsudungkynang:
                continue
            if luat["sinhluc"] and not phantramsinhlucconlai < luat["sinhluc"]:
                continue
            if luat["noiluc"] and not doc("noiluc") < luat["noiluc"]:
                continue
            if luat["matsinhluc"] and not doc("matsinhluc") >= luat["matsinhluc"]:
                continue
            if luat["matnoiluc"] and not doc("matnoiluc") >= luat["matnoiluc"]:
                continue
            if luat["theluc"] >= 0 and not doc("theluc") <= luat["theluc"]:
                continue
            if luat["khongphobanrieng"] and doc("khongphobanrieng"):
                continue
            if luat["hieuung"]:
                idhieuungs, is_canco, macdinhdocloi, is_hieuungcoloi, is_giannhip = HIEUUNGLUATDUNG[luat["hieuung"]]
                if is_giannhip:
                    self._thoidiemluatdung[khoa] = bayh
                if bool(self.moitruong.get_is_cohieuungs(idhieuungs, macdinhdocloi, is_hieuungcoloi = is_hieuungcoloi)) != is_canco:
                    continue
            tendadung = self._sudungvatphamhoi(vatphams, co)
            if tendadung:
                self._thoidiemluatdung[khoa] = time.time()
                self._thoidiemluatdung[("cho", tendadung)] = time.time() + luat["giancach"]

    def _sudungvatphamhoi(self, tenvatphams, co):
        # Dùng món đầu tiên còn trong hành trang mà client báo đã hết thời gian hồi; trả về tên món đã gửi được lệnh dùng, None nếu không
        tenvatphams = [ten for ten in tenvatphams if co(ten)]
        if not tenvatphams:
            return None
        thoigianhois = self.moitruong.get_thoigianhoiconlaivatphams(tenvatphams)
        for ten in tenvatphams:
            if thoigianhois[ten] <= 0 and self.action_sudungvatphamhanhtrang(ten, delay = 0.):
                return ten
        # Tất cả đang hồi nhưng sẽ xong trước vòng lặp kế tiếp: chờ tới đúng lúc hồi xong rồi dùng ngay, không trễ thêm 1 vòng
        conlai = min(thoigianhois.values())
        if 0 < conlai <= THOIGIANCHOHOIXONGTOIDA:
            time.sleep(conlai + 0.02)
            ten = next(ten for ten in tenvatphams if thoigianhois[ten] <= conlai)
            return ten if self.action_sudungvatphamhanhtrang(ten, delay = 0.) else None
        return None

    def action_tudongvutvatpham(self):
        if time.time() - self._thoidiemvutvatphamgannhat < 1.:
            return

        if not self._is_tudongkhaikhoang:
            return

        # Đang khai khoáng (đeo Cuốc) thì không vứt dược
        if self.moitruong.get_idbandohientai() in BANDOHAIDUOCs and self._loaikhaikhoang != "khaikhoang":
            # Mỗi giây xét 1 lần kể cả khi không vứt: đọc mô tả có thể phải hỏi game (desc + chờ 0.2 giây)
            self._thoidiemvutvatphamgannhat = time.time()
            soluongo = self.moitruong.get_soluongvatphamhanhtrangtoida() + 1
            for i, tenvatphamhanhtrang in enumerate(self.moitruong._docdanhsachtenvatphamhanhtrang(soluongo)):
                if tenvatphamhanhtrang not in VATPHAMVUTKHIHAIDUOCs:
                    continue
                iddoituongvatpham = self.moitruong.get_iddoituongvatphamhanhtrang(i)
                if not iddoituongvatpham:
                    continue
                # Vật phẩm khác trùng tên (không phải nguyên liệu Luyện Đơn) thì giữ; chưa đọc được mô tả thì để lượt sau
                if "Luyện Đơn" not in (self.moitruong.get_motavatphamhanhtrang(i) or ""):
                    continue
                print("{}: vứt dược {} tại vị trí {}".format(self.moitruong.get_tendoituong(), tenvatphamhanhtrang, i))
                soluong = max(1, self.moitruong.get_soluongvatphamhanhtrang(i) or 1)
                if self.moitruong.action_thucthicaulenh2("drop ! {}#{}".format(hex(iddoituongvatpham), soluong).replace("0x", "")):
                    self._thoidiemvutvatphamgannhat = time.time()
                return

    def action_tudongnhatvatpham(self):
        yeucaunhatvatphammoi = None

        if not self._is_tudongnhatvatpham:
            self._yeucaunhatvatpham = None
            return

        # Đang theo sau trưởng nhóm / người chơi được chọn thì chỉ nhặt vật phẩm ưu tiên
        is_chinhatvatphamuutien = bool(self._layidmuctieutheosau())

        if self.moitruong.get_is_dayhanhtrang():
            if time.time() - self._thoidiemphatamdayhanhtrang > 5.0:
                if not self._is_tudongvebanrac:
                    pass
                self._thoidiemphatamdayhanhtrang = time.time()

            self._diachicosovatphamdangnhat = False
            self._yeucaunhatvatpham = None
            return

        # Luật nhặt ở tab Hành trang (luattuido_xq "nhat"), đọc 1 lần mỗi lượt; luật "chỉ khi về bán rác" chỉ xét khi bật Tự động về bán rác
        # (ngoài Phong Yêu Kính) hoặc đang đi Phong Yêu Kính có bật Bán rác ở cấu hình Phong Yêu Kính (xong vòng bán ở Chu Quốc,
        # tactu_langlyson_xq._banracphongyeu). Trong Phong Yêu Kính ô Tự động về bán rác không tính: hai luồng bán tách riêng
        dulieuluat = tailuat()
        is_banrac = self.get_is_nhatbanracphongyeu() if self.get_is_dangphongyeukinh() else self._is_tudongvebanrac

        def hanhdongnhat(tenvatphamkiemtra):
            return timhanhdongnhat(tenvatphamkiemtra, is_banrac, dulieuluat)

        def kiemtradieukiennhat(tenvatphamkiemtra, diachikiemtra):
            hanhdong = hanhdongnhat(tenvatphamkiemtra)
            if hanhdong == NHAT_KHONGNHAT:
                return False
            if hanhdong == NHAT_UUTIEN:
                return True
            # Vật phẩm nhiệm vụ Thu thập của sư môn
            if tenvatphamkiemtra in self._layvatphamnhatsumon():
                return True
            if is_chinhatvatphamuutien:
                return False
            if hanhdong == NHAT_NHAT:
                return True
            if self._tenvatphamnhats and tenvatphamkiemtra in self._tenvatphamnhats:
                return True
            # Món có màu (xanh lam, vàng...) theo cài đặt Phẩm chất
            if self._phamchatnhats and self.moitruong.get_phamchatvatpham(diachikiemtra) in self._phamchatnhats:
                return True
            return False

        is_vatphamdangnhathople = True

        if self._diachicosovatphamdangnhat:
            tenvatphamhientai = self.moitruong.get_tendoituong(self._diachicosovatphamdangnhat)

            if not self.moitruong.get_is_vatphamtontai(self._diachicosovatphamdangnhat):
                is_vatphamdangnhathople = False
            elif self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat) >= KHOANGCACHNHATDO:
                is_vatphamdangnhathople = False
            elif not kiemtradieukiennhat(tenvatphamhientai, self._diachicosovatphamdangnhat):
                is_vatphamdangnhathople = False
            elif self._kiemtra_divaovungcam(*self.moitruong.get_toado(self._diachicosovatphamdangnhat)):
                is_vatphamdangnhathople = False
            elif time.time() - self._thoidiemthaydoivatphamdangnhatgannhat > 10:
                self._diachicosovatphamkhongnhat_map[self._diachicosovatphamdangnhat] = time.time()
                self._diachicosovatphamkhongnhat_map = donbangthoidiem(self._diachicosovatphamkhongnhat_map, 120.)
                is_vatphamdangnhathople = False
        else:
            is_vatphamdangnhathople = False

        if not is_vatphamdangnhathople:
            self._diachicosovatphamdangnhat = False

            diachiduphong = self._diachicosovatphamnhatduphong
            if diachiduphong:
                if self.moitruong.get_is_vatphamtontai(diachiduphong):
                    tenvatphamduphong = self.moitruong.get_tendoituong(diachiduphong)
                    if self.moitruong.get_khoangcach(diachiduphong) < KHOANGCACHNHATDO and kiemtradieukiennhat(tenvatphamduphong, diachiduphong) and not self._kiemtra_divaovungcam(*self.moitruong.get_toado(diachiduphong)):
                        self._diachicosovatphamdangnhat = diachiduphong
                        self._thoidiemthaydoivatphamdangnhatgannhat = time.time()
                self._diachicosovatphamnhatduphong = False

        danhsachvatpham = []
        # Lệnh nhặt xung quanh của game tự đi tới vật phẩm gần đó (không chọn được món nào), nên có món nằm trong vùng cấm ở gần thì không dùng lệnh này
        # Bản đồ có vùng cấm khác cổng (vùng rộng / đường dài) thì không dùng lệnh nhặt xung quanh, chỉ nhặt đích danh từng món;
        # cổng chuyển bản đồ thì bản đồ nào cũng có nên chỉ chặn khi đang đứng gần cổng
        idbandohientai = self.moitruong.get_idbandohientai()
        xnhanvat, ynhanvat = self.moitruong.get_toado()
        is_covatphamvungcamgan = bool(KHUVUCCAM_MAP.get(idbandohientai)) or any(
            math.dist((xnhanvat, ynhanvat), (x, y)) <= KHOANGCACHGANCONGKHONGNHATXUNGQUANH for _, x, y, _, _ in BANDOCONG_MAP.get(idbandohientai, ("", ()))[1])
        # Phá Thiên Tháp (ID 894) đang có mục tiêu: không dùng lệnh nhặt xung quanh (game tự chạy tới vật phẩm), chỉ nhặt đích danh món
        # trong tầm tại chỗ; di chuyển nhặt đồ chặn ở tactu_dichuyen (người dùng 2026-11-13)
        if idbandohientai == BANDO_BATQUAITRAN and self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon():
            is_covatphamvungcamgan = True
        i = -1
        while True:
            i += 1
            diachivatpham = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachivatpham:
                break

            if not self.moitruong.get_is_vatphamtontai(diachivatpham):
                continue

            if time.time() - self._diachicosovatphamkhongnhat_map.get(diachivatpham, 0) < 60:
                continue

            tenvatpham = self.moitruong.get_tendoituong(diachivatpham)
            khoangcach = self.moitruong.get_khoangcach(diachivatpham)

            # Vật phẩm nằm trong vùng cấm (đi vào sẽ bị dịch chuyển sang bản đồ khác) thì bỏ qua, kể cả vật phẩm ưu tiên
            if self._kiemtra_divaovungcam(*self.moitruong.get_toado(diachivatpham)):
                if khoangcach <= 6.:
                    is_covatphamvungcamgan = True
                continue

            if kiemtradieukiennhat(tenvatpham, diachivatpham) and khoangcach < KHOANGCACHNHATDO:
                danhsachvatpham.append((hanhdongnhat(tenvatpham) != NHAT_UUTIEN, khoangcach, diachivatpham))

        if danhsachvatpham:
            # Vật phẩm ưu tiên lên đầu, sau đó mới xét gần nhất
            danhsachvatpham.sort(key = lambda x: (x[0], x[1]))
            diachigannhat = danhsachvatpham[0][2]

            if diachigannhat != self._diachicosovatphamdangnhat:
                self._diachicosovatphamdangnhat = diachigannhat
                self._thoidiemthaydoivatphamdangnhatgannhat = time.time()

            if len(danhsachvatpham) > 1:
                self._diachicosovatphamnhatduphong = danhsachvatpham[1][2]
            else:
                self._diachicosovatphamnhatduphong = False
        else:
            self._diachicosovatphamdangnhat = False
            self._diachicosovatphamnhatduphong = False

        if self._diachicosovatphamdangnhat:
            khoangcach = self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat)
            # Món Thu thập của sư môn cũng ưu tiên: không thì còn quái quanh đó là cứ đánh tiếp (tấn công xếp trước nhặt đồ), không nhặt
            tenvatphamdangnhat = self.moitruong.get_tendoituong(self._diachicosovatphamdangnhat)
            is_vatphamuutien = hanhdongnhat(tenvatphamdangnhat) == NHAT_UUTIEN or tenvatphamdangnhat in self._layvatphamnhatsumon()
            if khoangcach > 1.5:
                yeucaunhatvatphammoi = {
                    "yeucau": YEUCAUDICHUYENNHATDO,
                    "toadodich": (
                        *self.moitruong.get_toado(self._diachicosovatphamdangnhat, ),
                    ),
                    "khoangcachtoida": 0,
                    "is_uutien": is_vatphamuutien,
                }
            if khoangcach <= 3.:
                if self._is_tudongvebanrac and not is_vatphamuutien and not is_covatphamvungcamgan:
                    self.moitruong.action_nhatvatphamxungquanh(delay = 0.2)
                elif time.time() - self._thoidiemnhatvatphamgannhat_map.get(self._diachicosovatphamdangnhat, 0) > 0.2:
                    self.moitruong.action_nhatvatpham(self._diachicosovatphamdangnhat)
                    self._thoidiemnhatvatphamgannhat_map[self._diachicosovatphamdangnhat] = time.time()
                    self._thoidiemnhatvatphamgannhat_map = donbangthoidiem(self._thoidiemnhatvatphamgannhat_map, 120.)

        elif self._is_tudongvebanrac and not is_chinhatvatphamuutien and not is_covatphamvungcamgan and not self._is_vuamatmuctieu:
            # Lệnh nhặt xung quanh tự chạy tới vật phẩm => vừa mất mục tiêu thì cũng chờ chọn con kế như di chuyển nhặt đồ
            self.moitruong.action_nhatvatphamxungquanh(delay = 0.5)

        self._yeucaunhatvatpham = yeucaunhatvatphammoi

    def action_tudongmuavatpham(self, delay = 3.):
        if self._is_tudongmuavatpham:
            # Dòng Mua bù TRANBAOKHO: mua bằng KNB ở bất kỳ đâu
            self._muabutranbaokho()
            if time.time() - self._thoidiemkiemtranpcmuavatphamgannhat < delay:
                return
            if self.moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                return

            self._thoidiemkiemtranpcmuavatphamgannhat = time.time()

            # Chỉ mua trong số ngân lượng đang có, chừa lại NGANLUONGGIULAI (Hồi Thành Phù / phù); chưa đọc được ngân lượng thì không mua
            nganluong = self.moitruong.get_nganluong()
            if nganluong is None:
                return
            nganquy = nganluong - NGANLUONGGIULAI

            # Món cần mua, NPC, số lượng: luật mua bù (luattuido_xq, tab Hành trang)
            self._muabutheoluat(nganquy)

    def _muabutheoluat(self, nganquy):
        # Mua bù theo luật túi đồ (luattuido_xq "muabu", lần lượt từ trên xuống): còn ít hơn "duoi" món thì mua cho đủ "muatoi", ở NPC cách
        # không quá 12 ô (NPC tìm theo tên riêng hoặc danh hiệu).
        # Ô / giá tra theo tên món ("tencuahang" nếu có) trong hàng đã đọc của cửa hàng đó (nhiemvu_xq.SoVitri); chưa đọc thì đứng gần
        # mở cửa hàng đọc 1 lần (đóng ngay).
        # Đếm cả các chồng của món đó; vừa mua món nào thì 10s sau mới xét lại món đó (chờ hành trang cập nhật, khỏi mua trùng)
        mucs = self._laymucmuabus()
        if not mucs:
            return
        soluongtheoten = self.moitruong.get_soluongvatphamhanhtrangtheoten()
        if soluongtheoten is None:
            return
        for muc in mucs:
            if time.time() - self._thoidiemmuabu_map.get(muc["vatpham"], 0.) < 10.:
                continue
            soluong = soluongtheoten.get(muc["vatpham"], 0)
            if soluong >= muc["duoi"] or soluong >= muc["muatoi"]:
                continue
            diachinpc = self._timdoituongxungquanh(muc["npc"])
            if not diachinpc or self.moitruong.get_khoangcach(diachinpc) > 12.0:
                continue
            idnpc = self.moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                continue
            ogia = self._layogiamuabu(muc, diachinpc)
            if not ogia:
                continue
            # Mỗi lệnh buy không quá 1 chồng (game không mua quá số xếp chồng của món trong 1 lệnh): thiếu nhiều thì chia nhiều lệnh,
            # mỗi lượt tối đa 10 lệnh (xếp chồng đặt nhỏ thì khỏi gửi cả trăm lệnh 1 lúc), còn thiếu thì lượt sau (10s) mua tiếp
            conthieu, damua = muc["muatoi"] - soluong, 0
            for _ in range(10):
                if conthieu <= 0:
                    break
                lan = min(conthieu, muc["xepchong"])
                dadung = self._muavatpham(idnpc, ogia[0], lan, ogia[1], muc["vatpham"], nganquy)
                if not dadung:
                    break
                nganquy -= dadung
                damua += dadung // ogia[1]
                conthieu -= lan
                if dadung < lan * ogia[1]:
                    break
            if damua:
                self._thoidiemmuabu_map[muc["vatpham"]] = time.time()
                print(f"[MUA BÙ] {self.moitruong.get_tendoituong()}: mua {damua} {muc['vatpham']} (còn {soluong}, chồng {muc['xepchong']}/ô)")

    def _laymucmuabus(self, is_tranbaokho = False):
        # Các mục mua bù đang dùng được cho nhân vật này (bật, đủ thông tin, đúng môn phái / điều kiện). is_tranbaokho: chỉ lấy dòng TRANBAOKHO
        # (mua bằng KNB), không thì chỉ lấy dòng NPC ở Tân Thủ Thôn
        tenmonphai = self.moitruong.get_tenmonphai()
        return [m for m in tailuat()["muabu"] if m["bat"] and m["vatpham"] and m["npc"] and m["muatoi"]
                and (m["npc"] == TRANBAOKHO) == is_tranbaokho
                and (not m["monphai"] or m["monphai"] == tenmonphai)
                and (m["chikhi"] != CHIKHI_TRIEUHOIBAOTHU or self._is_tudongtrieuhoibaothugiangho)]

    def _muabutranbaokho(self):
        # Mua bù ở Trân Bảo Khố (dòng Mua bù có NPC = TRANBAOKHO): còn ít hơn "duoi" thì mua cho đủ "muatoi" bằng Kim Nguyên Bảo, ở đâu cũng mua.
        # Mua chạy ở luồng riêng (moitruong.action_muavatphamtranbaokho chờ menu + giãn cách lệnh vài giây, không chặn vòng chính), mỗi lần 1 món.
        # Chỉ xét mỗi GIANCACHKIEMTRAMUATRANBAOKHO giây; đang có menu hội thoại hiện (việc khác đang nói chuyện NPC) thì để lượt sau, vì đọc KNB
        # phải mở menu "buyitem" đè lên. KNB không đủ / không mua được thì THOIGIANCHOKHONGDUKNB giây sau mới thử lại món đó
        luong = self._luongmuatranbaokho
        if luong is not None and luong.is_alive():
            return
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemkiemtramuatranbaokho < GIANCACHKIEMTRAMUATRANBAOKHO:
            return
        self._thoidiemkiemtramuatranbaokho = thoidiemhientai
        moitruong = self.moitruong
        mucs = self._laymucmuabus(is_tranbaokho = True)
        # Niết Bàn chưa hỗ trợ (không quét bộ nhớ tìm gói tin hàng được)
        if not mucs or moitruong.is_nietban or moitruong.get_is_nhanvatdachet() or moitruong.get_is_danghiencuasotuychon():
            return
        soluongtheoten = moitruong.get_soluongvatphamhanhtrangtheoten()
        if soluongtheoten is None:
            return
        for muc in mucs:
            # Ô của món đọc mới ở Trân Bảo Khố mỗi lần mua (moitruong.action_muavatphamtranbaokho), không bán thì chờ lâu rồi thử lại
            tenmon = muc["tencuahang"] or muc["vatpham"]
            if thoidiemhientai < self._thoidiemchomuatranbaokho_map.get(tenmon, 0.):
                continue
            soluong = soluongtheoten.get(muc["vatpham"], 0)
            if soluong >= muc["duoi"] or soluong >= muc["muatoi"]:
                continue
            canmua = muc["muatoi"] - soluong
            tennhanvat = moitruong.get_tendoituong()

            def mua(tenmon = tenmon, canmua = canmua, soluong = soluong):
                try:
                    damua, knb = moitruong.action_muavatphamtranbaokho(tenmon, canmua)
                except Exception as loi:
                    damua, knb = None, None
                    print(f"[MUA TRÂN BẢO KHỐ] {tennhanvat}: lỗi mua {tenmon}: {loi!r}")
                # Mua thiếu (hết KNB / lệnh không ăn) thì chờ lâu, khỏi bật menu "buyitem" liên tục; đủ thì 10s sau xét lại
                self._thoidiemchomuatranbaokho_map[tenmon] = time.time() + (10. if damua and damua >= canmua else THOIGIANCHOKHONGDUKNB)
                print(f"[MUA TRÂN BẢO KHỐ] {tennhanvat}: còn {soluong} {tenmon}, cần {canmua}, mua được "
                      f"{damua if damua is not None else '?'}, KNB còn {knb if knb is not None else '?'}")

            self._luongmuatranbaokho = threading.Thread(target = mua, daemon = True)
            self._luongmuatranbaokho.start()
            return

    def _is_canvemuabu(self):
        # Đang farm mà có món mua bù còn <= "thapnhat": phát âm, trả về True để luồng về bán rác chạy về Tân Thủ Thôn (mua ở
        # action_tudongmuavatpham, chờ mua ở _xulychomuabu). Đang ở Tân Thủ Thôn thì action_tudongmuavatpham tự mua, khỏi về
        if not self._is_tudongmuavatpham or self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
            return False
        if time.time() - self._thoidiemkiemtravemuabu < GIANCACHKIEMTRAVEMUABU:
            return False
        self._thoidiemkiemtravemuabu = time.time()
        soluongtheoten = self.moitruong.get_soluongvatphamhanhtrangtheoten()
        if soluongtheoten is None:
            return False
        for muc in self._laymucmuabus():
            if time.time() - self._thoidiemvemuabu_map.get(muc["vatpham"], 0.) < THOIGIANCHOVEMUABULAI:
                continue
            soluong = soluongtheoten.get(muc["vatpham"], 0)
            if soluong <= muc["thapnhat"] and soluong < muc["muatoi"]:
                self._thoidiemvemuabu_map[muc["vatpham"]] = time.time()
                print(f"[MUA BÙ] {self.moitruong.get_tendoituong()}: còn {soluong} {muc['vatpham']} (<= {muc['thapnhat']}), về Tân Thủ Thôn mua")
                canhbao(self.moitruong, f"Còn {soluong} {muc['vatpham']}, về mua bù", is_block = False)
                return True
        return False

    def _is_canvesuado(self):
        # Bật tự về sửa đồ mà có món sửa được dưới _phantramvesuado % độ bền: True để luồng về bán rác chạy về thành sửa ở Chủ Tiệm Sửa
        # Chữa (bước sửa đồ của _xulybanracvamuabu). Ở phó bản (kể cả phó bản mượn bản đồ ngoài, chưa đọc được tên bản đồ thì coi như
        # đang ở phó bản) thì không bao giờ về: về là mất phó bản. Không chặn luồng: lần đầu desc đồ đang mặc, lượt sau mới đọc độ bền
        moitruong = self.moitruong
        if not self._is_tudongvesuado or moitruong.get_is_nhanvatdachet() or moitruong.get_idbandohientai() in BANDOPHOBANs \
                or moitruong.get_is_phobanmuonbando() is not False:
            self._thoidiemtruyvandobenvesua = 0.
            return False
        thoidiemhientai = time.time()
        if not self._thoidiemtruyvandobenvesua:
            if thoidiemhientai - self._thoidiemkiemtravesuado < GIANCACHKIEMTRAVESUADO:
                return False
            self._thoidiemkiemtravesuado = thoidiemhientai
            if moitruong.action_truyvandobentrangbi():
                self._thoidiemtruyvandobenvesua = thoidiemhientai
            return False
        dobens = moitruong.get_dobentrangbisuaduocs()
        if None in dobens.values() and thoidiemhientai - self._thoidiemtruyvandobenvesua < THOIGIANCHODOBENVESUADO:
            return False
        self._thoidiemtruyvandobenvesua = 0.
        thaps = [vitri for vitri, doben in dobens.items() if doben and doben[1] > 0 and doben[0] * 100 < doben[1] * self._phantramvesuado]
        if not thaps:
            return False
        # Vừa về sửa thì THOIGIANCHOVESUADOLAI giây sau mới xét lại (sửa hỏng vì thiếu tiền / không thấy NPC thì khỏi chạy về liên tục)
        self._thoidiemkiemtravesuado = thoidiemhientai + THOIGIANCHOVESUADOLAI
        mota = ", ".join("{} ({}/{})".format(moitruong.get_tentrangbi(vitri), *dobens[vitri]) for vitri in thaps)
        print(f"[VỀ SỬA ĐỒ] {moitruong.get_tendoituong()}: độ bền dưới {self._phantramvesuado}%: {mota}, về sửa")
        canhbao(moitruong, "Độ bền thấp, về sửa đồ", is_block = False)
        return True

    def _is_canve(self):
        # Luồng về bán rác có cần về không: túi đầy / thiếu đồ mua bù (khi bật về bán rác) hoặc độ bền thấp (khi bật về sửa đồ)
        if self._is_tudongvebanrac and (self.moitruong.get_is_dayhanhtrang() or self._is_canvemuabu()):
            return True
        return self._is_canvesuado()

    def _xulychomuabu(self):
        # Đã về tới tiệm (bán rác xong): còn món mua bù dưới "Mua khi dưới" mà thấy NPC bán thì đi tới đứng chờ action_tudongmuavatpham
        # mua (mỗi 3s), quá THOIGIANCHOMUABU giây thì thôi. True = xong, quay lại bãi
        if not self._thoidiembatdauchomuabu:
            self._thoidiembatdauchomuabu = time.time()
        soluongtheoten = self.moitruong.get_soluongvatphamhanhtrangtheoten()
        if time.time() - self._thoidiembatdauchomuabu < THOIGIANCHOMUABU and soluongtheoten is not None:
            for muc in self._laymucmuabus():
                soluong = soluongtheoten.get(muc["vatpham"], 0)
                if soluong >= muc["duoi"] or soluong >= muc["muatoi"]:
                    continue
                diachinpc = self._timdoituongxungquanh(muc["npc"])
                if not diachinpc:
                    continue
                if self.moitruong.get_khoangcach(diachinpc) > 3. and time.time() - self._thoidiemdichuyenchomuabu > 1.:
                    self._thoidiemdichuyenchomuabu = time.time()
                    self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 0.)
                return False
        self._thoidiembatdauchomuabu = 0.
        return True

    def _xulybanracvamuabu(self):
        # Bước 3 của về bán rác: bán rác + sửa đồ (nếu bật về bán rác; chỉ bật về sửa đồ thì chỉ sửa) rồi chờ mua bù
        if self._thoidiembatdauchomuabu == 0.:
            if self._is_tudongvebanrac:
                if not self._xulydangbanrac():
                    return False
            elif not self._xulysuadokhongbanrac():
                return False
        return self._xulychomuabu()

    def _xulysuadokhongbanrac(self):
        # Chỉ bật về sửa đồ (không về bán rác): bắt đầu sửa đồ rồi chờ action_xulybanracvasuado sửa xong. True = xong
        if self._buocbanrac == 0:
            self.action_suavatpham()
            self._buocbanrac = 2
            return False
        if self.get_is_dangsuavatpham():
            return False
        self._buocbanrac = 0
        return True

    def _layogiamuabu(self, muc, diachinpc):
        # (ô, giá) để mua món của luật mua bù ở NPC này, None khi chưa biết (đã cho mở cửa hàng đọc nếu được)
        moitruong = self.moitruong
        idbando = moitruong.get_idbandohientai()
        tenmon = muc["tencuahang"] or muc["vatpham"]
        tra = self._sovitri.timhang(idbando, muc["npc"], tenmon)
        ketqua = self.get_ketquamocuahang(idbando, muc["npc"])
        khoa = (idbando, muc["npc"])
        if tra:
            # Hàng nhớ có thể của nhân vật khác / bản khác (Niết Bàn xếp hàng khác Aegis): desc ô trước khi mua. Mình vừa đọc cửa hàng
            # (sau lần mở để kiểm) thì tin luôn; desc ra món khác thì đứng gần mở cửa hàng đọc lại
            lucdoc = self._lucmocuahangmuabu_map.get(khoa, 0.)
            if lucdoc and ketqua and ketqua[0] and ketqua[1] >= lucdoc:
                return tra
            dung = self._kiemhangcuahang(self._kiemcuahangmuabu, diachinpc, tra[0], tenmon)
            if dung:
                return tra
            if dung is False and moitruong.get_khoangcach(diachinpc) <= 3. and not self._mocuahang \
                    and time.time() - lucdoc > GIANCACHMOCUAHANGMUABU:
                self._lucmocuahangmuabu_map[khoa] = time.time()
                self.batdau_mocuahang(diachinpc)
            return None
        if ketqua and ketqua[0]:
            khoa = (idbando, muc["npc"], tenmon)
            if khoa not in self._lechmuabudabao:
                self._lechmuabudabao.add(khoa)
                print(f"[MUA BÙ] {muc['npc']} không bán \"{tenmon}\": sửa tên món / \"Tên ở cửa hàng\" trong luật mua bù")
            return None
        # Chưa đọc cửa hàng này: đứng gần thì mở đọc (mở hỏng thì GIANCACHMOCUAHANGMUABU giây sau mới thử lại)
        if moitruong.get_khoangcach(diachinpc) <= 3. and not self._mocuahang \
                and time.time() - self._lucmocuahangmuabu_map.get(khoa, 0.) > GIANCACHMOCUAHANGMUABU:
            self._lucmocuahangmuabu_map[khoa] = time.time()
            self.batdau_mocuahang(diachinpc)
        return None

    def _layhanhdongluat(self, ten, vitri):
        # Hành động theo luật túi đồ của người dùng (luattuido_xq) cho món ở ô vitri: None = không luật nào khớp (làm như cũ),
        # "chuabiet" = luật cần loại / mô tả mà chưa đọc được (lượt này đừng bán / vứt món đó).
        # Kỵ thú quý (KYTHUGIUs) luôn Giữ, không theo luật người dùng (luật có thể bị sửa / tắt / đặt dưới luật Vứt)
        if self._is_kythugiu(ten):
            return HANHDONG_GIU
        luat = self._layluatvatpham(ten, vitri)
        return luat["hanhdong"] if isinstance(luat, dict) else luat

    def _laymotaluat(self, ten, vitri):
        # (loại, mô tả) của món ở ô vitri cho luật túi đồ, None khi chưa đọc được. Đọc hỏng thì 60s sau mới hỏi game lại (vòng vứt chạy
        # mỗi giây, desc mỗi lần chờ tới 1s)
        if ten not in self._motavatpham_map:
            if time.time() < self._thoidiemdoclaimota_map.get(ten, 0.):
                return None
            if not self._docloaivatpham(ten, vitri):
                self._loaivatpham_map.pop(ten, None)
                self._thoidiemdoclaimota_map[ten] = time.time() + 60.
                return None
        return self._loaivatpham_map.get(ten, ""), self._motavatpham_map.get(ten, "")

    def _layluatvatpham(self, ten, vitri):
        # Luật túi đồ đầu tiên khớp món ở ô vitri (dict), None / "chuabiet" như luattuido_xq.timluat
        return timluat(self._chuanhoatenvatpham(ten), lambda: self._laymotaluat(ten, vitri))

    def _layluatbaovatpham(self, ten, vitri):
        # Luật 📣 đầu tiên khớp món ở ô vitri, xét riêng với hành động (luật khác đứng trên quyết định bán / giữ cũng không chặn báo)
        return timluatbao(self._chuanhoatenvatpham(ten), lambda: self._laymotaluat(ten, vitri))

    def _layluatcatkho(self, ten, vitri):
        # Luật bảng Cất kho khớp món ở ô vitri (dict có "ruong" / "giulai") hoặc None; xét riêng với luật hành động
        return timluatcatkho(self._chuanhoatenvatpham(ten), lambda: self._laymotaluat(ten, vitri))

    def _is_catkhovatpham(self, ten, vitri):
        # Món khớp bảng Cất kho: không bán, không vứt (kể cả phần "giữ lại trong túi"). Kỵ thú quý thì để trong túi để đeo, không cất
        if self._is_kythugiu(ten):
            return False
        return bool(self._layluatcatkho(ten, vitri))

    def _is_kythugiu(self, ten):
        return self._chuanhoatenvatpham(ten) in KYTHUGIUs

    @staticmethod
    def _get_okythu(vitrimos):
        # Ô đặt kỵ thú quý khi sắp xếp hành trang: ô mở áp chót (ô mở cuối dành cho bảo thú vật phẩm), None nếu chưa tới 2 ô mở
        return vitrimos[-2] if len(vitrimos) >= 2 else None

    def action_tudongdeokythu(self):
        # Có kỵ thú quý (KYTHUGIUs) trong túi mà chưa đeo (nhân vật +0x1198 = 0) thì "use <id>#" để đeo, mỗi giây xét 1 lần.
        # Gửi xong chờ THOIGIANCHODEOKYTHU giây xem cờ lên chưa; hỏng SOLANDEOKYTHUTOIDA lần liền thì nghỉ THOIGIANNGHIDEOKYTHU giây
        now = time.time()
        if now < self._thoidiemxetdeokythu:
            return
        self._thoidiemxetdeokythu = now + 1.
        moitruong = self.moitruong
        if moitruong.get_is_nhanvatdachet() or self.get_is_dangbanrac() or self._is_dangsapxephanhtrang:
            return
        if moitruong._get_idthucuoi():
            if self._lucguideokythu:
                print(f"[KỴ THÚ] {moitruong.get_tendoituong()}: đã đeo kỵ thú sau {now - self._lucguideokythu:.1f} giây")
            self._lucguideokythu = 0.
            self._solandeokythuthatbai = 0
            return
        if self._lucguideokythu:
            if now - self._lucguideokythu < THOIGIANCHODEOKYTHU:
                return
            self._lucguideokythu = 0.
            self._solandeokythuthatbai += 1
            if self._solandeokythuthatbai >= SOLANDEOKYTHUTOIDA:
                print(f"[KỴ THÚ] {moitruong.get_tendoituong()}: dùng kỵ thú {self._solandeokythuthatbai} lần vẫn chưa thấy đeo "
                      f"(+0x1198 = 0), nghỉ {THOIGIANNGHIDEOKYTHU:.0f} giây")
                self._solandeokythuthatbai = 0
                self._thoidiemxetdeokythu = now + THOIGIANNGHIDEOKYTHU
                return
        soluongo = moitruong.get_soluongvatphamhanhtrangtoida() + 1
        tens = moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        vitri = next((i for i, ten in enumerate(tens) if ten and self._is_kythugiu(ten)), None)
        iddoituong = moitruong.get_iddoituongvatphamhanhtrang(vitri) if vitri is not None else 0
        if not iddoituong:
            # Không có kỵ thú trong túi (acc khác): 30 giây xét lại
            self._thoidiemxetdeokythu = now + 30.
            return
        if moitruong.action_sudungvatpham(iddoituong):
            print(f"[KỴ THÚ] {moitruong.get_tendoituong()}: chưa đeo kỵ thú, dùng {tens[vitri]} ở ô {vitri} (lần {self._solandeokythuthatbai + 1})")
            self._lucguideokythu = now

    def action_tudongvutvatphamtheoluat(self):
        # Vứt món khớp luật "vứt" (luattuido_xq), mỗi giây xét 1 lượt và vứt tối đa 1 món. Món đã gửi lệnh vứt mà vẫn còn (game không
        # cho vứt: khoá...) thì 60s sau mới thử lại. Đang bán rác / sắp xếp hành trang thì thôi (vị trí các ô đang đổi)
        if time.time() - self._thoidiemvuttheoluatgannhat < 1.:
            return
        self._thoidiemvuttheoluatgannhat = time.time()
        if not any(luat["bat"] and luat["hanhdong"] == HANHDONG_VUT for luat in tailuat()["luat"]):
            return
        if self.get_is_dangbanrac() or self._is_dangsapxephanhtrang or self.moitruong.get_is_nhanvatdachet():
            return
        soluongvatphamhanhtrangtoida = self.moitruong.get_soluongvatphamhanhtrangtoida()
        tens = self.moitruong._docdanhsachtenvatphamhanhtrang(soluongvatphamhanhtrangtoida + 1)
        for i in range(6, min(soluongvatphamhanhtrangtoida, len(tens))):
            if not tens[i]:
                continue
            iddoituongvatpham = self.moitruong.get_iddoituongvatphamhanhtrang(i)
            if not iddoituongvatpham or time.time() < self._thoidiemthulaivut_map.get(iddoituongvatpham, 0.):
                continue
            # Món trong bảng Cất kho thì để dành đi cất, không vứt
            if self._layhanhdongluat(tens[i], i) != HANHDONG_VUT or self._is_catkhovatpham(tens[i], i):
                continue
            # Đồ đã ép sao thì không vứt dù khớp luật Vứt (chỉ xem mô tả có sẵn, chưa có thì gửi desc, lượt sau xét lại)
            if self._is_dosaokhongban(i, tens[i], is_docmoi = False):
                if not self.moitruong.get_motathovatphamhanhtrangcosan(i):
                    self.moitruong.get_motavatphamhanhtrang(i, thoigianchotoida = 0.)
                continue
            soluong = max(1, self.moitruong.get_soluongvatphamhanhtrang(i) or 1)
            print(f"[VỨT THEO LUẬT] {self.moitruong.get_tendoituong()}: vứt {soluong} {tens[i]} ở ô {i}")
            self.moitruong.action_thucthicaulenh2("drop ! {}#{}".format(hex(iddoituongvatpham), soluong).replace("0x", ""))
            self._thoidiemthulaivut_map[iddoituongvatpham] = time.time() + 60.
            return

    def _muavatpham(self, idnpc, ovatpham, soluong, dongia, tenvatpham, nganquy):
        # Mua tối đa soluong món ở ô ovatpham của NPC (đơn giá dongia), bớt số lượng cho vừa nganquy. -> số ngân lượng đã dùng
        soluongmua = min(soluong, max(0, nganquy) // dongia)
        if soluongmua <= 0:
            if time.time() - self._thoidiembaothieutienmuagannhat_map.get(tenvatpham, 0.) > 300.:
                self._thoidiembaothieutienmuagannhat_map[tenvatpham] = time.time()
                print(f"[MUA] Không đủ ngân lượng mua {tenvatpham} ({dongia} lượng/món, còn dùng được {max(0, nganquy)} lượng sau khi chừa {NGANLUONGGIULAI})")
            return 0
        if soluongmua < soluong:
            print(f"[MUA] Chỉ đủ tiền mua {soluongmua}/{soluong} {tenvatpham}")
        caulenh = "buy {}# {} {} {}".format(hex(idnpc).replace("0x", ""), ovatpham, soluongmua, dongia)
        self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)
        return soluongmua * dongia

    def action_tudongsuavatpham(self, delay = 3.):
        if self._is_tudongsuavatpham:
            if time.time() - self._thoidiemkiemtranpcsuavatphamgannhat < delay:
                return
            self._thoidiemkiemtranpcsuavatphamgannhat = time.time()

            if time.time() < self._thoidiemkhongcansuavatphamden:
                return

            diachicosothongtinnhanvatchutiemsuachua = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)

            if diachicosothongtinnhanvatchutiemsuachua and self.moitruong.get_khoangcach(diachicosothongtinnhanvatchutiemsuachua) <= 12.0:
                is_cansua = self._get_is_cansuavatpham()
                if is_cansua:
                    self.moitruong.action_suavatpham(diachicosothongtinnhanvatchutiemsuachua)
                elif is_cansua is False:
                    # Độ bền giảm chậm: khỏi desc lại liên tục mỗi lần đứng gần NPC
                    self._thoidiemkhongcansuavatphamden = time.time() + 60.

    def _get_is_cansuavatpham(self, thoigianchotoida = 3.):
        # Có món sửa được (nón, hạng liên, vũ khí, áo, yêu đới, giày) bị giảm độ bền không, để khỏi gửi repair khi đồ còn nguyên.
        # Không chặn luồng: lần đầu desc các món rồi trả None (đang chờ mô tả), gọi lại sau đó mới có True/False.
        # Món nào hết giờ chờ vẫn không đọc được độ bền thì coi như cần sửa (như trước đây luôn sửa)
        thoidiemhientai = time.time()
        if not self._thoidiemtruyvandobengannhat or thoidiemhientai - self._thoidiemtruyvandobengannhat > thoigianchotoida * 2:
            if not self.moitruong.action_truyvandobentrangbi():
                self._thoidiemtruyvandobengannhat = 0.
                return False
            self._thoidiemtruyvandobengannhat = thoidiemhientai
            return None
        dobens = self.moitruong.get_dobentrangbisuaduocs()
        if None in dobens.values() and thoidiemhientai - self._thoidiemtruyvandobengannhat < thoigianchotoida:
            return None
        self._thoidiemtruyvandobengannhat = 0.
        cansuas = [vitri for vitri, doben in dobens.items() if doben is None or doben[0] < doben[1]]
        if cansuas:
            print("[Auto-SuaDo] Cần sửa {}".format(", ".join(
                "{} ({})".format(self.moitruong.get_tentrangbi(vitri), "{}/{}".format(*dobens[vitri]) if dobens[vitri] else "?") for vitri in cansuas)))
        return bool(cansuas)

    def action_suavatpham(self):
        # Chỉ bắt đầu việc sửa đồ (tối đa 30s); action_xulybanracvasuado làm dần mỗi giây (trước đây vòng while chặn luồng tới 30s)
        # Nói chuyện NPC sửa đồ không ngắt vận khí => không chặn khi đang vận khí
        if self.moitruong.get_is_nhanvatdachet():
            return
        self._thoidiemhetsuavatpham = time.time() + 30.
        self._thoidiemkiemtrasuavatpham = 0.

    def action_sudungvatphamhanhtrang(self, tenvatpham, is_boquaxacnhan = False, delay = 0.25, is_use2 = None):
        # is_use2: None = theo VATPHAMDUNGUSE2s; False = ép "use <id>#" như chuột phải (vd đổi pháp bảo Đào Hoa)
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False

        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(tenvatpham)

        if not iddoituongvatpham:
            return False

        print("{}: sử dụng vật phẩm: {}".format(self.moitruong.get_tendoituong(), tenvatpham))

        if is_use2 is None:
            is_use2 = tenvatpham in VATPHAMDUNGUSE2s
        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham, is_boquaxacnhan, delay = delay, is_use2 = is_use2)
        if is_ok:
            self._thoidiemsudungvatphamgannhat = time.time()

        return is_ok

    # Ctrl+U (người dùng 2026-11-13; nút trên giao diện đã gỡ): dùng 1 lượt mỗi loại thuốc buff 1 giờ đang có trong
    # hành trang. Tên trong game là "Kim Tang Tán" (người chơi hay gọi Kim Cang Tán)
    THUOC1GIOs = (TIEUDAOTAN, TUTAMDON, QUYNGUYENDON, KIMTANGTAN, KHIMACHDON, NHANSAM)
    # Chỉ số trong thông báo buff đang còn ("Gia tăng Ngoại Công còn 3560 giây", "Gia tăng Ngoại kháng còn lại 3548 giây"; người dùng
    # 2026-11-13), so không phân biệt hoa thường. Món không có ở đây (Nhân Sâm) thì nhận mọi thông báo "còn ... giây"
    CHISOTHUOC1GIO_MAP = {TIEUDAOTAN: "ngoại công", QUYNGUYENDON: "nội kháng", KIMTANGTAN: "ngoại kháng", KHIMACHDON: "khí huyết",
                          TUTAMDON: "nội công"}

    def _demvatphamhanhtrang(self, ten):
        # Tổng số lượng các ô tên ten trong túi (không tính ô trang bị)
        tens = self.moitruong._docdanhsachtenvatphamhanhtrang(VITRITRANGBIDAUTIEN)
        return sum(self.moitruong.get_soluongvatphamhanhtrang(i) or 0 for i, t in enumerate(tens) if t == ten)

    def _docthongbaogiuamanhinh(self):
        return self._chuanhoatenvatpham(self.moitruong.get_noidungthongbaogannhat() or "")

    def action_dungvongthuoc1gio(self, solanthutoida = 8, thoigianchoketqua = 1.2, thoigianchohoitoida = 3.):
        # Chạy ở vòng xử lý lệnh (LoopXuLyLenh) nên chờ được. Tiêu Dao / Tử Tâm / Quy Nguyên / Kim Tang / Khí Mạch chung nhóm hồi 2
        # (đo 13/11, HT_NHOMHOI): trước gửi cách 0.35s thì viên ngay sau 1 viên vừa dùng bị bỏ (3 lần bấm đều hụt Quy Nguyên Đơn).
        # Mỗi viên gửi "use" tới khi chắc buff đã lên, nhận biết 1 trong 2: số lượng trong túi giảm (vừa dùng được) hoặc game báo buff
        # đang còn (thông báo giữa màn hình "Gia tăng Ngoại Công còn 3560 giây", get_noidungthongbaogannhat).
        # Mỗi lần gửi: chờ hết hồi nhóm, gửi, chờ tới thoigianchoketqua xem có 1 trong 2 dấu hiệu đó không, không có thì gửi lại
        mauconlai = re.compile(r"còn(?: lại)?\s*\d+\s*giây")
        xongs, khongxacnhans, khongcos = [], [], []
        for ten in self.THUOC1GIOs:
            if not self.moitruong.action_timkiemvatphamhanhtrang(ten):
                khongcos.append(ten)
                continue
            is_xong = False
            for _ in range(solanthutoida):
                thoidiemhet = time.time() + thoigianchohoitoida
                while self.moitruong.get_thoigianhoiconlaivatphams([ten]).get(ten, 0.) > 0 and time.time() < thoidiemhet:
                    time.sleep(0.1)
                iddoituong = self.moitruong.action_timkiemvatphamhanhtrang(ten)
                if not iddoituong:
                    break
                soluongtruoc = self._demvatphamhanhtrang(ten)
                thongbaotruoc = self._docthongbaogiuamanhinh()
                if not self.moitruong.action_sudungvatpham(iddoituong, delay = 0., is_use2 = ten in VATPHAMDUNGUSE2s):
                    time.sleep(0.3)
                    continue
                self._thoidiemsudungvatphamgannhat = time.time()
                thoidiemhet = time.time() + thoigianchoketqua
                while time.time() < thoidiemhet:
                    time.sleep(0.1)
                    thongbao = self._docthongbaogiuamanhinh()
                    # Thông báo phải đúng chỉ số của viên này (thông báo của viên trước / việc khác không tính)
                    if thongbao != thongbaotruoc and mauconlai.search(thongbao) \
                            and self.CHISOTHUOC1GIO_MAP.get(ten, "") in thongbao.lower():
                        print("{}: {}: {}".format(self.moitruong.get_tendoituong(), ten, thongbao))
                        is_xong = True
                        break
                    if self._demvatphamhanhtrang(ten) < soluongtruoc:
                        # Số lượng giảm = đã dùng được, chắc như thông báo => xong, khỏi gửi thêm
                        print("{}: {}: đã dùng (số lượng giảm)".format(self.moitruong.get_tendoituong(), ten))
                        is_xong = True
                        break
                if is_xong:
                    break
            (xongs if is_xong else khongxacnhans).append(ten)
        thongbao = "Đã có buff {} loại thuốc 1 giờ".format(len(xongs))
        if khongxacnhans:
            thongbao += ", {} loại chưa xác nhận".format(len(khongxacnhans))
        print("{}: {}: {}{}{}".format(self.moitruong.get_tendoituong(), thongbao, ", ".join(xongs),
                                      " | chưa thấy báo còn giây: {}".format(", ".join(khongxacnhans)) if khongxacnhans else "",
                                      " | không có: {}".format(", ".join(khongcos)) if khongcos else ""))
        phatam(thongbao)

    def action_sudungvatphamhanhtrangtaivitri(self, vitri, tenvatpham, is_boquaxacnhan = False, delay = 0.25):
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False

        if vitri is None or vitri < 0 or self.moitruong.get_tenvatphamhanhtrang(vitri) != tenvatpham:
            return False

        iddoituongvatpham = self.moitruong.get_iddoituongvatphamhanhtrang(vitri)

        if not iddoituongvatpham:
            return False

        print("{}: sử dụng vật phẩm: {} tại vị trí {}".format(self.moitruong.get_tendoituong(), tenvatpham, vitri))

        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham, is_boquaxacnhan, delay = delay, is_use2 = tenvatpham in VATPHAMDUNGUSE2s)
        if is_ok:
            self._thoidiemsudungvatphamgannhat = time.time()

        return is_ok

    def _timbuocsapxephanhtrang(self, soogiu = 2):
        # Bước tiếp theo để hành trang ngăn nắp: ("o", id vật phẩm, ô đích) / ("tui", id vật phẩm, túi đích 1-4),
        # chuỗi = dừng với thông báo đó, None = chưa đọc được hành trang / chờ kết quả lần trước.
        # Xếp chung cả 4 túi như 1 dãy ô mở (túi phụ có thể chỉ mở 4/6/12 ô, ô khoá bỏ qua): gộp chồng trước, rồi xếp: đồ khác
        # (theo loại ［Vũ Khí］［Nón］... rồi tên) dồn từ đầu túi 1, đồ ［Có thể sử dụng］ rồi thuốc (THUOCSAPXEPs) dồn về cuối túi cuối.
        # Game chỉ có 2 lệnh: "move <id># <ô>" trong CÙNG túi (ô đích có món khác thì đổi chỗ 2 món) và
        # "move <id># to <túi>" sang túi khác (rơi vào ô trống của túi đó, túi đầy thì không được), không có lệnh đổi 2 món khác túi. Nên:
        # 1. Giữa các túi: so theo tên, túi nào thừa món tên X (nhiều hơn số ô tên X của túi đó trong bố cục đích) chuyển sang túi đang
        #    thiếu X mà còn ô trống. Các túi thiếu đều đầy (vòng tròn A cần món ở B, B cần món ở A...) thì dời tạm 1 món thừa của túi
        #    thiếu đó sang túi còn trống bất kỳ, lượt sau túi vừa trống nhận món nó cần => tối đa 2 lệnh là bớt 1 món sai túi.
        #    Cả hành trang không còn ô trống nào thì không chuyển giữa túi được: chỉ xếp trong từng túi rồi báo.
        # 2. Trong từng túi: mỗi lệnh đổi chỗ đặt ít nhất 1 món vào đúng ô cuối cùng.
        # soogiu ô mở cuối túi 1 xếp sau cùng (chỉ dùng khi các túi khác đầy) để chế đồ không phải chuyển đi (action_giuotrongcuoihanhtrang)
        vitrimos = self.moitruong.get_danhsachvitrimohanhtrang()
        soluongo = vitrimos[-1] + 1
        tens = self.moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        ids = self.moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        if len(tens) < soluongo or len(ids) < soluongo:
            return None

        vitrimotui1s = [vitri for vitri in vitrimos if vitri < SOLUONGOMOITUI]
        ogius = vitrimotui1s[-soogiu:] if len(vitrimotui1s) < len(vitrimos) else []
        cacvitri = [vitri for vitri in vitrimos if vitri not in ogius] + ogius
        # Bảo thú vật phẩm ở ô mở cuối cùng là con được chọn để triệu hồi (_get_baothuvatphamocuoi): giữ nguyên chỗ
        if ids[vitrimos[-1]] and tens[vitrimos[-1]] in BAOTHUVATPHAMs:
            cacvitri.remove(vitrimos[-1])

        # Kỵ thú quý (KYTHUGIUs) đặt ở ô mở áp chót (_get_okythu), làm trước mọi việc khác; đã đúng chỗ thì giữ nguyên ô đó
        okythu = self._get_okythu(vitrimos)
        vitrikythus = [i for i in vitrimos if ids[i] and self._is_kythugiu(tens[i])] if okythu is not None else []
        if vitrikythus:
            if okythu not in vitrikythus:
                nguon = vitrikythus[0]
                tuinguon, tuidich = nguon // SOLUONGOMOITUI, okythu // SOLUONGOMOITUI
                if tuinguon == tuidich:
                    return "o", ids[nguon], okythu
                # Khác túi: "to túi" rơi vào ô trống của túi đích, lượt sau mới đổi vào đúng ô. Túi đích đầy thì đưa món đang chiếm
                # ô kỵ thú sang túi đang chứa kỵ thú (nếu còn chỗ); cả 2 túi đều đầy thì thôi, xếp như thường
                if any(not ids[i] for i in vitrimos if i // SOLUONGOMOITUI == tuidich):
                    return "tui", ids[nguon], tuidich + 1
                if any(not ids[i] for i in vitrimos if i // SOLUONGOMOITUI == tuinguon):
                    return "tui", ids[okythu], tuinguon + 1
            else:
                for danhsach in (cacvitri, ogius):
                    if okythu in danhsach:
                        danhsach.remove(okythu)

        # Gộp chồng trước: chồng sau chuyển vào chồng trước cùng tên (bỏ qua cặp đã biết không gộp được)
        chongchuaday_map = self._laychongchuaday_map(cacvitri, tens, ids)
        buoc = self._chonbuocxepchong(chongchuaday_map)
        if buoc:
            onguon, idnguon, odich = buoc
            if onguon // SOLUONGOMOITUI != odich // SOLUONGOMOITUI:
                return "tui", idnguon, odich // SOLUONGOMOITUI + 1
            return "o", idnguon, odich
        if self._langopgannhat:
            # Đang chờ kết quả lần gộp trước
            return None

        # Loại vật phẩm (_docloaivatpham) của mọi tên đang có. Trước đây mỗi lượt desc 1 tên rồi chờ tới 1s => lần sắp xếp đầu sau khi
        # mở bot mất cả chục giây. Giờ: đọc mô tả game đã nạp sẵn cho mọi tên, tên còn thiếu thì gửi desc tất cả cùng lúc (không chờ),
        # các lượt sau đọc lại; gửi 2 lần quá 0.5s vẫn chưa có thì đọc kiểu cũ (desc + chờ, hỏng thì coi là không có loại).
        # Tên đã đọc được lưu cache theo tên (_ghicachemotavatpham) nên lần mở bot sau không desc lại
        chuabiet_map = {}
        for i in cacvitri:
            if ids[i] and tens[i] not in self._loaivatpham_map:
                chuabiet_map.setdefault(tens[i], i)
        if chuabiet_map:
            now = time.time()
            for ten, vitri in chuabiet_map.items():
                if self._docloaivatpham(ten, vitri, is_chicosan = True):
                    continue
                solan, thoidiem = self._descsapxep_map.get(ten, (0, 0.))
                if now - thoidiem < 0.5:
                    continue
                if solan < 2:
                    if self.moitruong.truyvan_motavatphamhanhtrang(vitri, is_cho = False):
                        self._descsapxep_map[ten] = (solan + 1, now)
                else:
                    self._docloaivatpham(ten, vitri)
                    break
            return None

        # Bố cục đích: đồ khác dồn từ đầu túi 1, đồ dùng được rồi thuốc dồn về cuối túi cuối, ô trống ở giữa. Các ô giữ cuối túi 1
        # chỉ nhận đồ khác khi hết chỗ
        tensapxeps = sorted((tens[i] for i in cacvitri if ids[i]), key = self._khoasapxepvatpham)
        vitrichinhs = [vitri for vitri in cacvitri if vitri not in ogius]
        sokhac = sum(1 for ten in tensapxeps if self._khoasapxepvatpham(ten)[0] == 0)
        socuoi = len(tensapxeps) - sokhac
        if socuoi <= len(vitrichinhs):
            sokhacchinh = min(sokhac, len(vitrichinhs) - socuoi)
            vitridichs = vitrichinhs[:sokhacchinh] + ogius[:sokhac - sokhacchinh] + vitrichinhs[len(vitrichinhs) - socuoi:]
        else:
            vitridichs = cacvitri[:len(tensapxeps)]
        tencan_map = dict.fromkeys(cacvitri)
        tencan_map.update(zip(vitridichs, tensapxeps))

        def tui(vitri):
            return vitri // SOLUONGOMOITUI

        def is_dungcho(vitri):
            return (tens[vitri] if ids[vitri] else None) == tencan_map[vitri]

        # Bước 2 của lần đổi chỗ 2 viên đá (xem cuối hàm) làm trước mọi việc khác, kẻo bị xếp lại mất ô vừa dọn:
        # ô okiemtra đã có idkiemtra (0 = trống) thì chuyển idchuyen tới ô của idmuctieu (None = chính okiemtra)
        if self._xoayvongsapxep:
            okiemtra, idkiemtra, idchuyen, idmuctieu, thoidiem = self._xoayvongsapxep
            if ids[okiemtra] == idkiemtra and idchuyen in ids and (idmuctieu is None or idmuctieu in ids):
                self._xoayvongsapxep = None
                odich = okiemtra if idmuctieu is None else ids.index(idmuctieu)
                if tui(ids.index(idchuyen)) == tui(odich):
                    return "o", idchuyen, odich
            elif time.time() - thoidiem < 3.:
                # Chờ game cập nhật bước 1
                return None
            self._xoayvongsapxep = None

        # 1. Giữa các túi. thua_map[túi][tên] > 0: túi thừa bấy nhiêu món tên đó, < 0: còn thiếu
        thua_map = {}
        for vitri in cacvitri:
            demtui = thua_map.setdefault(tui(vitri), {})
            if ids[vitri]:
                demtui[tens[vitri]] = demtui.get(tens[vitri], 0) + 1
            if tencan_map[vitri] is not None:
                demtui[tencan_map[vitri]] = demtui.get(tencan_map[vitri], 0) - 1
        sootrong_map = {}
        for vitri in vitrimos:
            sootrong_map[tui(vitri)] = sootrong_map.get(tui(vitri), 0) + (0 if ids[vitri] else 1)

        def chonmonthua(tuinguon, ten = None):
            # Món thừa trong tuinguon (tên ten, hoặc tên bất kỳ đang thừa) cần chuyển đi, ưu tiên món đang nằm sai ô
            ungviens = [i for i in cacvitri if tui(i) == tuinguon and ids[i] and thua_map[tuinguon].get(tens[i], 0) > 0
                        and (ten is None or tens[i] == ten)]
            return min(ungviens, key = is_dungcho, default = None)

        cachuyengiuatui = any(sl > 0 for demtui in thua_map.values() for sl in demtui.values())
        if cachuyengiuatui:
            # Chuyển thẳng: món thừa sang túi đang thiếu tên đó mà còn ô trống
            for tuidich, demtui in thua_map.items():
                if not sootrong_map.get(tuidich):
                    continue
                for ten, sl in demtui.items():
                    if sl >= 0:
                        continue
                    for tuinguon in thua_map:
                        if tuinguon != tuidich and thua_map[tuinguon].get(ten, 0) > 0:
                            return "tui", ids[chonmonthua(tuinguon, ten)], tuidich + 1
            # Các túi đang thiếu đều đầy: dời tạm 1 món thừa của túi thiếu sang túi còn nhiều ô trống nhất
            tuitrongs = sorted((t for t, so in sootrong_map.items() if so), key = lambda t: -sootrong_map[t])
            for tuinguon, demtui in thua_map.items():
                if not any(sl < 0 for sl in demtui.values()):
                    continue
                nguon = chonmonthua(tuinguon)
                tuidich = next((t for t in tuitrongs if t != tuinguon), None)
                if nguon is not None and tuidich is not None:
                    return "tui", ids[nguon], tuidich + 1
            # Hết ô trống: không chuyển giữa túi được, vẫn xếp trong từng túi

        # 2. Trong từng túi: nguồn là món tên tencan cùng túi đang nằm sai chỗ; ưu tiên món mà sau khi đổi chỗ, món ở dich
        # rơi đúng vào chỗ của nó. Túi chưa đủ món (chưa chuyển giữa túi xong) thì ô thiếu bỏ qua.
        # Đá (DAKHONGDEDOs) không được đè lên ô có món: chuyển món ở dich sang ô của đá (vẫn là đổi chỗ 2 món); 2 bên đều là đá thì
        # dời đá ở dich ra ô trống cùng túi, không có thì xoay vòng qua món thường cùng túi, túi toàn đá thì tạm gửi sang túi khác
        sokhongxepduoc = 0
        for dich in cacvitri:
            tencan = tencan_map[dich]
            if tencan is None or is_dungcho(dich):
                continue
            nguons = [i for i in cacvitri if tui(i) == tui(dich) and ids[i] and tens[i] == tencan and not is_dungcho(i)]
            if not nguons:
                continue
            tendich = tens[dich] if ids[dich] else None
            nguon = next((i for i in nguons if tencan_map[i] == tendich), nguons[0])
            if not ids[dich] or not self._is_dakhongdedo(tencan):
                return "o", ids[nguon], dich
            if not self._is_dakhongdedo(tendich):
                return "o", ids[dich], nguon
            otrongs = [i for i in cacvitri if tui(i) == tui(dich) and not ids[i]]
            if otrongs:
                # Ưu tiên ô trống không cần món nào, khỏi phải dời lần nữa
                return "o", ids[dich], min(otrongs, key = lambda i: tencan_map[i] is not None)
            # Túi đầy: xoay vòng qua 1 món thường Z cùng túi (ưu tiên món đang sai chỗ): Z đè lên dich (đá ở dich sang ô của Z),
            # lượt sau Z đè lên ô đá cần đặt (đá đó vào dich, xem _xoayvongsapxep) => đá không bao giờ là món đi đè
            trunggians = [i for i in cacvitri if tui(i) == tui(dich) and ids[i] and i not in (dich, nguon)
                          and not self._is_dakhongdedo(tens[i])]
            if trunggians:
                trunggian = min(trunggians, key = is_dungcho)
                self._xoayvongsapxep = (dich, ids[trunggian], ids[trunggian], ids[nguon], time.time())
                return "o", ids[trunggian], dich
            # Túi toàn đá: tạm đưa đá ở dich sang túi khác còn trống ("to túi" chỉ vào ô trống), lượt sau đặt đá cần vào dich,
            # viên đưa đi được bước 1 chuyển về sau
            tuitam = max((t for t, so in sootrong_map.items() if so and t != tui(dich)), key = sootrong_map.get, default = None)
            if tuitam is not None:
                self._xoayvongsapxep = (dich, 0, ids[nguon], None, time.time())
                return "tui", ids[dich], tuitam + 1
            sokhongxepduoc += 1
        if cachuyengiuatui:
            return "Hành trang hết ô trống, không chuyển được vật phẩm giữa các hành trang"
        if sokhongxepduoc:
            return f"Còn {sokhongxepduoc} ô đá chưa xếp được (túi không còn ô trống để đổi chỗ 2 viên đá)"
        if not all(is_dungcho(vitri) for vitri in cacvitri):
            # Hành trang vừa đổi giữa lúc đọc: lượt sau đọc lại
            return None
        return "Đã sắp xếp xong hành trang"

    @staticmethod
    def _chuanhoatenvatpham(ten):
        return unicodedata.normalize("NFC", re.sub(r'\x1b[a-zA-Z0-9]', '', ten or "")).strip()

    def _is_thuocsapxep(self, ten):
        ten = self._chuanhoatenvatpham(ten)
        return any(ten.startswith(thuoc) for thuoc in THUOCSAPXEPs)

    def _khoasapxepvatpham(self, ten):
        # Thứ tự khi sắp xếp hành trang (tên đã có trong _loaivatpham_map): nhóm 0 đồ khác, 1 đồ ［Có thể sử dụng］, 2 thuốc;
        # trong nhóm theo loại (Vũ Khí, Nón, Tinh luyện...) rồi tên, món không ghi loại (nguyên liệu...) để sau.
        # Thiên Lý Hữu Tình (người chơi hay dùng) xếp đầu nhóm 0 => luôn nằm ô đầu hành trang 1, dù là đồ ［Có thể sử dụng］
        # Trong nhóm 1, món có mô tả gần giống nhau ("Trong 1 giờ gia tăng ...", "Lập tức hồi phục ...") nằm cạnh nhau: xếp theo
        # dòng mô tả đầu (_khoamotavatpham) trước tên
        loai = self._loaivatpham_map.get(ten, "")
        is_dautui1 = self._chuanhoatenvatpham(ten) == THIENLYHUUTINH
        nhom = 0 if is_dautui1 else 2 if self._is_thuocsapxep(ten) else 1 if loai == LOAIVATPHAM_COTHESUDUNG else 0
        # Nhóm thuốc (THUOCSAPXEPs: Tiêu Dao Tán, Thí Luyện Quả...) cũng theo công dụng, không thì chỉ còn theo tên => hồi máu nằm giữa buff
        motakhoa = self._khoamotavatpham(ten) if nhom in (1, 2) else (0, "")
        return nhom, not is_dautui1, not loai, loai.lower(), motakhoa, ten.lower()

    # Nhóm công dụng đồ ［Có thể sử dụng］ khi sắp xếp, xét theo thứ tự, mẫu khớp trên mô tả đã thường hoá (chữ thường, số -> "#", bỏ từ
    # "Giá bán ra" trở đi). Không xếp theo dòng mô tả đầu được: dòng sau ［Có thể sử dụng］ thường là câu giới thiệu ("Một loại tinh
    # thạch kỳ dị màu đỏ..."), công dụng nằm ở dòng sau. Mô tả thật (đo 13/11):
    #   Thí Luyện Quả "Lập tức hồi phục 1850 điểm Khí Huyết", Cấp Cứu Đơn "lập tức khôi phục 1400 điểm khí huyết",
    #   Trị Dược "ngay lập tức khôi phục trực tiếp 2000 điểm khí huyết", Phục Dược "ngay lập tức khôi phục 2000 điểm lực pháp lực",
    #   Tiểu Huyết Thạch "liên tục hồi phục 40 điểm Khí Huyết sau mỗi 2 giây", Đại Huyết Thạch "cứ 2 giây có thể khôi phục 90 điểm khí huyết",
    #   Tiêu Dao Tán "Trong 1 giờ gia tăng lên 8％ Ngoại Công", Quy Nguyên Đơn "Trong 1 giờ gia tăng 10％ Nội kháng",
    #   Xá Lợi Tử "Nâng cao 5％ Ngoại Kháng, hiệu quả trong 10 phút", Chiến Quốc Lệnh / Tù Và "điểm Kinh nghiệm ... trong suốt 1 tiếng",
    #   Cửu Chuyển Đơn / Tử Sâm Đơn "tiềm năng", Túi Linh Thạch "Sau khi sử dụng có thể nhận được một Linh Thạch"
    NHOMCONGDUNGs = (
        r"lập tức.*(?:hồi|khôi) phục.*khí huyết",
        r"lập tức.*(?:hồi|khôi) phục.*pháp lực",
        r"(?:mỗi|cứ) # giây.*khí huyết|khí huyết.*(?:mỗi|cứ) # giây",
        r"(?:mỗi|cứ) # giây.*pháp lực|pháp lực.*(?:mỗi|cứ) # giây",
        r"thể lực",
        # Thiên Nguyên Đơn "Mỗi 2 giây khôi phục cho người chơi 1 điểm Nguyên Khí"
        r"nguyên khí",
        # Thanh Tâm Đơn "khôi phục trạng thái bất thường... loại bỏ hiệu quả biến thân", Tịch Độc Tán "Giải độc..."
        r"trạng thái bất thường|giải độc|biến thân",
        r"trong # giờ gia tăng",
        r"(?:nâng cao|tăng) #％.*trong # phút",
        r"kinh nghiệm",
        r"tiềm năng",
        r"sống lại|hồi sinh",
        r"học làm",
        r"nhận được (?:một|#)",
    )

    def _khoamotavatpham(self, ten):
        # (thứ tự nhóm công dụng trong NHOMCONGDUNGs, chỉ số tăng): "Trong 1 giờ gia tăng ..." / "Lập tức hồi phục ..." nằm cạnh nhau.
        # Không khớp nhóm nào thì (len, câu có số đầu tiên) để món mô tả giống nhau vẫn gần nhau; chưa có mô tả thì xếp cuối
        mota = self._motavatpham_map.get(ten, "")
        if not mota:
            return len(self.NHOMCONGDUNGs) + 1, ""
        mota = re.split(r"Giá bán ra", mota)[0]
        mota = re.sub(r"[\[［][^\]］]*[\]］]", " ", mota).replace("%", "％")
        mota = re.sub(r"\d+(?:[.,]\d+)?", "#", mota)
        mota = re.sub(r"\s+", " ", mota).lower()
        for thutu, mau in enumerate(self.NHOMCONGDUNGs):
            if re.search(mau, mota):
                # Cùng nhóm thì theo chỉ số được tăng ("#％ ngoại công" -> "ngoại công"), giữ các buff cùng chỉ số cạnh nhau
                chiso = re.search(r"#％ ([^,.，。|]+)", mota)
                return thutu, chiso.group(1).strip() if chiso else ""
        cau = next((c.strip() for c in re.split(r"[.,，。\n]", mota) if "#" in c), "")
        return len(self.NHOMCONGDUNGs), cau

    def _is_dakhongdedo(self, ten):
        # Đá (xem DAKHONGDEDOs): loại ［Tinh luyện］, tên có Đoạn / Linh / Tinh Thạch, hoặc tên có "Thạch" mà chưa biết / không có loại
        tenchuan = self._chuanhoatenvatpham(ten)
        loai = self._loaivatpham_map.get(ten)
        return bool(tenchuan) and (loai in LOAIVATPHAMDAs or any(da in tenchuan for da in DAKHONGDEDOs)
                                   or (not loai and "Thạch" in tenchuan))

    def _docloaivatpham(self, ten, vitri, is_chicosan = False):
        # is_chicosan: chỉ đọc mô tả game đã nạp sẵn, không khớp thì trả False và không ghi gì (không desc)
        # Ghi _loaivatpham_map[ten] = loại vật phẩm: chữ trong cặp [] / ［］ đầu tiên của mô tả, bỏ qua dòng tên (dòng tên có thể có
        # "(Vật phẩm hiệu ứng [Khoá])"), "" nếu không có (nguyên liệu...). Mô tả lưu theo ô nên chỉ tin khi dòng đầu khớp ten, không
        # thì desc lại; desc không ra thì coi là không có loại (khỏi hỏi lại mãi)
        tenchuan = self._chuanhoatenvatpham(ten)

        def laydongs(mota):
            return [dong.strip() for dong in self._chuanhoatenvatpham(mota).split("\n") if dong.strip()]

        dongs = laydongs(self.moitruong.get_motavatphamhanhtrangcosan(vitri))
        if is_chicosan and (not dongs or tenchuan not in dongs[0]):
            return False
        if not dongs or tenchuan not in dongs[0]:
            # Chờ ngắn (0.2s sau desc + tối đa 0.25s): máy chủ trả mô tả sau ~0.25-0.5s, mô tả đã nhớ theo tên vào cache nên hiếm khi tới đây
            dongs = laydongs(self.moitruong.get_motavatphamhanhtrang(vitri, thoigianchotoida = 0.25, is_napmoi = True) or "")
        if not dongs or tenchuan not in dongs[0]:
            print("{}: không đọc được mô tả {}, coi là không có loại khi sắp xếp".format(self.moitruong.get_tendoituong(), tenchuan))
            self._loaivatpham_map[ten] = ""
            return False
        khop = re.search(r"[\[［]\s*([^\]］\n]*?)\s*[\]］]", "\n".join(dongs[1:]))
        self._loaivatpham_map[ten] = khop.group(1) if khop else ""
        # Mô tả (bỏ dòng tên) cho luật túi đồ "mô tả chứa"
        self._motavatpham_map[ten] = "\n".join(dongs[1:])
        self._ghicachemotavatpham(ten)
        return True

    def _duongdancachemotavatpham(self):
        # Aegis và Niết Bàn khác bảng vật phẩm / mô tả nên mỗi bản 1 file
        tenfile = "motavatpham_nietban.json" if getattr(self.moitruong, "is_nietban", False) else "motavatpham.json"
        return os.path.join(os.getcwd(), "_internal", tenfile)

    def _taicachemotavatpham(self):
        # {tên: [loại, mô tả]} đã đọc ở các lần chạy trước (mọi cửa sổ dùng chung): cùng tên thì cùng mô tả nên khỏi desc lại
        try:
            with open(self._duongdancachemotavatpham(), encoding = "utf-8") as file:
                dulieu = json.load(file)
        except (OSError, ValueError):
            return
        for ten, giatri in dulieu.items():
            if isinstance(giatri, list) and len(giatri) == 2:
                self._loaivatpham_map.setdefault(ten, giatri[0])
                self._motavatpham_map.setdefault(ten, giatri[1])

    def _ghicachemotavatpham(self, ten):
        # Chỉ ghi món mà mô tả không đổi theo từng món: trang bị (độ bền, chỉ số ngẫu nhiên) và đồ có hạn (ngày hết hạn) thì không.
        # Gộp với file đang có (cửa sổ khác có thể vừa ghi) rồi thay file một lần
        mota = self._motavatpham_map.get(ten, "")
        if "Độ bền" in mota or "Sử dụng đến" in mota:
            return
        duongdan = self._duongdancachemotavatpham()
        try:
            try:
                with open(duongdan, encoding = "utf-8") as file:
                    dulieu = json.load(file)
            except (OSError, ValueError):
                dulieu = {}
            if dulieu.get(ten) == [self._loaivatpham_map.get(ten, ""), mota]:
                return
            dulieu[ten] = [self._loaivatpham_map.get(ten, ""), mota]
            filetam = "{}.{}.tmp".format(duongdan, os.getpid())
            with open(filetam, "w", encoding = "utf-8") as file:
                json.dump(dulieu, file, ensure_ascii = False, indent = 1)
            os.replace(filetam, duongdan)
        except OSError as e:
            print("Không ghi được cache mô tả vật phẩm: {}".format(e))

    def _docanhhanhtrangsapxep(self):
        # Ảnh (id, tên) mọi ô mở để biết lệnh move vừa gửi đã có kết quả chưa; None nếu chưa đọc được
        vitrimos = self.moitruong.get_danhsachvitrimohanhtrang()
        if not vitrimos:
            return None
        soluongo = vitrimos[-1] + 1
        ids = self.moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        tens = self.moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        if len(ids) < soluongo or len(tens) < soluongo:
            return None
        return tuple(ids), tuple(tens)

    def action_sapxephanhtrang(self, delaytoithieu = 0.08, thoigianchotoida = 1.0, thoigiantoida = 180., solandichuyentoida = 300):
        # Không chờ cố định giữa 2 lệnh move (trước 0.6s + vòng LoopPhu 0.5s => ~1s/lệnh): gửi lệnh kế ngay khi hành trang đã đổi
        # so với lúc gửi lệnh trước (game đã xử lý xong, đọc lại không bị cũ), cách tối thiểu delaytoithieu. Hành trang chưa đổi thì
        # chờ tối đa thoigianchotoida (gộp chồng một phần chỉ đổi số lượng, không đổi id/tên) rồi tính lại. LoopPhu gọi hàm này
        # mỗi ~0.05s khi đang sắp xếp (xem LoopPhu.loop)
        if not self._is_dangsapxephanhtrang:
            return

        if time.time() - self._thoidiembatdausapxephanhtrang > thoigiantoida or self._solandichuyensapxep >= solandichuyentoida:
            self._ketthucsapxephanhtrang("Sắp xếp hành trang quá lâu, dừng lại")
            return

        thoigiantulenhtruoc = time.time() - self._thoidiemsapxephanhtranggannhat
        if thoigiantulenhtruoc < delaytoithieu:
            return
        if self._anhhanhtrangsapxep is not None and thoigiantulenhtruoc < thoigianchotoida:
            if self._docanhhanhtrangsapxep() == self._anhhanhtrangsapxep:
                return

        # Đang vận khí (chế đồ) vẫn xếp được: "move" không ngắt vận khí, ô giữ cuối túi 1 xếp sau cùng nên chế đồ vẫn có chỗ
        if self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_nhanvatdachet():
            return

        if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
            return

        buoc = self._timbuocsapxephanhtrang()
        if buoc is None:
            return
        if isinstance(buoc, str):
            self._ketthucsapxephanhtrang(buoc)
            return

        # Cùng một lệnh lặp lại mãi (game không cho chuyển) thì dừng, tránh kẹt
        if buoc == self._lenhsapxepgannhat:
            self._solanlaplenhsapxep += 1
            if self._solanlaplenhsapxep >= 3:
                self._ketthucsapxephanhtrang("Không di chuyển được vật phẩm, dừng sắp xếp hành trang")
                return
        else:
            self._lenhsapxepgannhat = buoc
            self._solanlaplenhsapxep = 0

        kieu, iddoituong, dich = buoc
        anhtruoclenh = self._docanhhanhtrangsapxep()
        if kieu == "tui":
            is_ok = self.moitruong.action_dichuyenvatphamsanghanhtrangkhac(iddoituong, dich, delay = 0.)
        else:
            is_ok = self.moitruong.action_dichuyenvatphamhanhtrang(iddoituong, dich + 1, delay = 0.)
        if is_ok:
            self._thoidiemsapxephanhtranggannhat = time.time()
            self._anhhanhtrangsapxep = anhtruoclenh
            self._solandichuyensapxep += 1

    def _ghitenvatphamdat(self, thoigiangiu = 15.):
        # Ghi tên các vật phẩm đang nằm dưới đất quanh nhân vật, món mới vào túi trùng tên 1 món vừa thấy dưới đất mới tính là nhặt
        thoidiemhientai = time.time()
        i = -1
        while True:
            i += 1
            diachivatpham = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachivatpham:
                break
            if not self.moitruong.get_is_vatphamtontai(diachivatpham):
                continue
            tenvatpham = (self.moitruong.get_tendoituong(diachivatpham) or "").strip()
            if tenvatpham:
                self._tenvatphamdat_map[tenvatpham] = thoidiemhientai
        self._tenvatphamdat_map = {k: v for k, v in self._tenvatphamdat_map.items() if thoidiemhientai - v <= thoigiangiu}

    def _is_vatphamnhattudat(self, ten):
        # Tên ô túi chỉ 31 byte (bị cắt) nên so theo đầu tên
        ten = (ten or "").strip()
        return bool(ten) and any(tendat == ten or tendat.startswith(ten) for tendat in self._tenvatphamdat_map)

    def action_tudongdatvatphammoi(self, thoigiancho = 3., delay = 0.6, solanchuyentoida = 3, soogiu = 2):
        # Tự động nhẹ (khác nút Sắp xếp hành trang): so danh sách id mỗi lượt, món MỚI NHẶT TỪ ĐẤT vào hành trang nằm yên thoigiancho
        # giây thì chèn vào đúng thứ tự với 2 món kề bên (_khoasapxepvatpham), chỗ đang nằm đã đúng thì thôi. Đồ người khác cho, mở
        # túi, lấy kho, mua, chế... (tên không trùng món vừa thấy dưới đất) thì để nguyên chỗ. Mỗi món chỉ vài lệnh (xem 4 cách bên
        # dưới), không dồn cả hành trang; món bị rút ra thì để trống, không dồn lại.
        # Xử lý quá solanchuyentoida lần vẫn chưa đúng chỗ thì bỏ qua món đó
        if not self._is_tudongdatvatphammoi or self._is_dangsapxephanhtrang:
            self._idhanhtrangtruoc = None
            self._vatphammoi_map = {}
            self._tenvatphamdat_map = {}
            return
        self._ghitenvatphamdat()
        vitrimos = self.moitruong.get_danhsachvitrimohanhtrang()
        soluongo = vitrimos[-1] + 1
        ids = self.moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        if len(ids) < soluongo:
            return
        idhientais = {ids[vitri] for vitri in vitrimos if ids[vitri]}
        idmois = idhientais - self._idhanhtrangtruoc if self._idhanhtrangtruoc is not None else set()
        if idmois:
            tens = self.moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
            if len(tens) < soluongo:
                return
            for idvatpham in idmois:
                if self._is_vatphamnhattudat(tens[ids.index(idvatpham)]):
                    # [lúc thấy, số lần đã xử lý, ô đang chờ trống để đưa vào]
                    self._vatphammoi_map[idvatpham] = [time.time(), 0, None]
        self._idhanhtrangtruoc = idhientais
        self._vatphammoi_map = {k: v for k, v in self._vatphammoi_map.items() if k in idhientais}
        if not self._vatphammoi_map or time.time() - self._thoidiemdatvatphammoigannhat < delay:
            return
        if self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_nhanvatdachet() \
                or self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
            return
        idvatpham = next((k for k, mon in self._vatphammoi_map.items() if time.time() - mon[0] >= thoigiancho), None)
        if idvatpham is None:
            return

        tens = self.moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        if len(tens) < soluongo:
            return
        vitri = ids.index(idvatpham)
        ten = tens[vitri]
        if ten not in self._loaivatpham_map:
            self._docloaivatpham(ten, vitri)
            return
        # Thứ tự ô như Sắp xếp hành trang, bỏ các ô giữ cuối túi 1 (chế đồ) và ô bảo thú cuối cùng (giữ nguyên chỗ)
        vitrimotui1s = [v for v in vitrimos if v < SOLUONGOMOITUI]
        ogius = vitrimotui1s[-soogiu:] if len(vitrimotui1s) < len(vitrimos) else []
        cacvitri = [v for v in vitrimos if v not in ogius]
        if ids[vitrimos[-1]] and tens[vitrimos[-1]] in BAOTHUVATPHAMs:
            if vitrimos[-1] == vitri:
                del self._vatphammoi_map[idvatpham]
                return
            cacvitri.remove(vitrimos[-1])
        # Ô kỵ thú quý đang có kỵ thú thì không đụng (Sắp xếp hành trang đặt nó ở đó)
        okythu = self._get_okythu(vitrimos)
        if okythu in cacvitri and ids[okythu] and self._is_kythugiu(tens[okythu]):
            if okythu == vitri:
                del self._vatphammoi_map[idvatpham]
                return
            cacvitri.remove(okythu)

        khoa = self._khoasapxepvatpham(ten)
        khoatheoo = {v: self._khoasapxepvatpham(tens[v]) for v in cacvitri if ids[v] and v != vitri}
        thutu = {v: k for k, v in enumerate(cacvitri)}

        def tui(o):
            return o // SOLUONGOMOITUI

        def is_hople(o, k, khoatheoo, muc = 4):
            # Đặt món khoá k ở ô o: món kề trước (bỏ qua ô trống) không đứng sau nó, món kề sau không đứng trước. So muc phần đầu
            # của khoá: 4 = tới tên, 3 = chỉ nhóm + loại (tự động nhẹ: chèn đúng tên không được thì đúng nhóm, đúng loại là đủ)
            truoc = next((khoatheoo[v] for v in reversed(cacvitri[:thutu[o]]) if v in khoatheoo), None)
            sau = next((khoatheoo[v] for v in cacvitri[thutu[o] + 1:] if v in khoatheoo), None)
            return (truoc is None or truoc[:muc] <= k[:muc]) and (sau is None or k[:muc] <= sau[:muc])

        def is_otrongdau(o, otrongcons):
            # "to túi" thả vào ô trống đầu tiên của túi (tính cả ô giữ): o phải là ô đó thì mới rơi đúng chỗ
            return next((v for v in vitrimos if tui(v) == tui(o) and v in otrongcons), None) == o

        mon = self._vatphammoi_map[idvatpham]
        # Lượt trước đã dời món chắn ở ô mon[2] đi (cách 3 dưới đây): ô đã trống thì đưa món mới vào
        if mon[2] is not None:
            ocho, mon[2] = mon[2], None
            if not ids[ocho] and (tui(ocho) == tui(vitri) or is_otrongdau(ocho, {v for v in vitrimos if not ids[v]})):
                self._chuyenvatphammoi(idvatpham, ten, vitri, ocho)
                return
        mon[1] += 1
        if mon[1] > solanchuyentoida:
            print("{}: không đặt được {} vào chỗ hợp lý, bỏ qua".format(self.moitruong.get_tendoituong(), ten))
            del self._vatphammoi_map[idvatpham]
            return
        otrongs = [v for v in cacvitri if not ids[v]]
        otrongtatcas = {v for v in vitrimos if not ids[v]}
        if vitri in thutu and is_hople(vitri, khoa, khoatheoo):
            # Đã đúng thứ tự nhưng còn lạc giữa khúc trống thì vẫn dồn sát về nhóm của nó (đồ khác ô hợp lệ sớm nhất, đồ dùng / thuốc
            # ô hợp lệ muộn nhất), kẻo chắn đường các món chèn sau
            ohoples = [v for v in otrongs if is_hople(v, khoa, khoatheoo)
                       and (thutu[v] < thutu[vitri] if khoa[0] == 0 else thutu[v] > thutu[vitri])]
            if ohoples:
                self._chuyenvatphammoi(idvatpham, ten, vitri, ohoples[0] if khoa[0] == 0 else ohoples[-1])
            else:
                del self._vatphammoi_map[idvatpham]
            return

        # Thử chèn đúng tới tên (muc 4) trước, không được thì đúng nhóm + loại (muc 3); món Y bị dời đi chỉ cần đúng nhóm + loại
        for muc in (4, 3):
            if muc == 3 and vitri in thutu and is_hople(vitri, khoa, khoatheoo, 3):
                del self._vatphammoi_map[idvatpham]
                return

            # 1. Ô trống đúng thứ tự: đồ khác lấy ô sớm nhất, đồ dùng được / thuốc ô muộn nhất
            ohoples = [v for v in otrongs if is_hople(v, khoa, khoatheoo, muc)]
            if ohoples:
                self._chuyenvatphammoi(idvatpham, ten, vitri, ohoples[0] if khoa[0] == 0 else ohoples[-1])
                return

            # 2. Khúc đó đã kín: đổi chỗ với 1 món Y cùng túi mà sau khi đổi cả 2 đều đúng thứ tự (vd thuốc mới ở khúc trống giữa đổi
            # với món dùng được cuối cùng ngay trước khúc thuốc). Đá không đè lên đồ: món mới là đá thì cho Y đè sang ô món mới
            if vitri in thutu:
                for o in sorted((v for v in khoatheoo if tui(v) == tui(vitri)), key = lambda v: abs(thutu[v] - thutu[vitri])):
                    khoay = khoatheoo[o]
                    khoasaudoi = {**{v: k for v, k in khoatheoo.items() if v != o}, vitri: khoay}
                    if not is_hople(o, khoa, khoasaudoi, muc) or not is_hople(vitri, khoay, khoasaudoi, 3):
                        continue
                    if not self._is_dakhongdedo(ten):
                        self.moitruong.action_dichuyenvatphamhanhtrang(idvatpham, o + 1, delay = 0.)
                    elif not self._is_dakhongdedo(tens[o]):
                        self.moitruong.action_dichuyenvatphamhanhtrang(ids[o], vitri + 1, delay = 0.)
                    else:
                        continue
                    self._thoidiemdatvatphammoigannhat = time.time()
                    del self._vatphammoi_map[idvatpham]
                    print("{}: đặt vật phẩm mới {} vào ô {} (đổi chỗ với {})".format(self.moitruong.get_tendoituong(), ten, o, tens[o]))
                    return

            # 3. Khác túi: dời 1 món Y đang chắn chỗ đúng của món mới sang 1 ô trống mà Y vẫn đúng thứ tự, lượt sau đưa món mới vào ô
            # của Y (mon[2]). Chuyển sang túi khác ("to túi" thả vào ô trống đầu túi) thì ô đích phải là ô trống đầu túi đó
            for o in sorted(khoatheoo, key = lambda v: (tui(v) != tui(vitri), abs(thutu[v] - thutu.get(vitri, thutu[v])))):
                conlai = {v: k for v, k in khoatheoo.items() if v != o}
                if not is_hople(o, khoa, conlai, muc) or (tui(o) != tui(vitri) and not is_otrongdau(o, otrongtatcas | {o})):
                    continue
                khoay = khoatheoo[o]
                e = next((e for e in otrongs if is_hople(e, khoay, {**conlai, o: khoa}, 3)
                          and (tui(e) == tui(o) or is_otrongdau(e, otrongtatcas))), None)
                if e is not None:
                    self._chuyenvatphammoi(ids[o], tens[o], o, e)
                    mon[2] = o
                    return

        # 4. Không chèn được: chỉ chuyển 1 lần về phía nhóm của nó (đồ khác ô trống đầu, đồ dùng / thuốc ô trống cuối) nếu thế là gần
        # hơn. Sang túi khác thì còn theo dõi: tới túi đó rồi lượt sau có thể đổi chỗ trong túi (cách 2); cùng túi thì thôi, không
        # chuyển qua lại
        odich = (otrongs[0] if khoa[0] == 0 else otrongs[-1]) if otrongs else None
        if odich is None or (vitri in thutu and (thutu[odich] > thutu[vitri]) == (khoa[0] == 0)):
            del self._vatphammoi_map[idvatpham]
            return
        if tui(odich) == tui(vitri):
            del self._vatphammoi_map[idvatpham]
        self._chuyenvatphammoi(idvatpham, ten, vitri, odich)

    def _chuyenvatphammoi(self, idvatpham, ten, vitri, odich):
        # Ô trống cùng túi thì chuyển thẳng vào ô, khác túi thì "to túi" (rơi vào ô trống đầu túi đó, lượt sau chỉnh trong túi)
        if odich // SOLUONGOMOITUI == vitri // SOLUONGOMOITUI:
            is_ok = self.moitruong.action_dichuyenvatphamhanhtrang(idvatpham, odich + 1, delay = 0.)
        else:
            is_ok = self.moitruong.action_dichuyenvatphamsanghanhtrangkhac(idvatpham, odich // SOLUONGOMOITUI + 1, delay = 0.)
        if is_ok:
            self._thoidiemdatvatphammoigannhat = time.time()
            print("{}: đặt vật phẩm mới {} từ ô {} vào ô {}".format(self.moitruong.get_tendoituong(), ten, vitri, odich))

    def action_giuotrongcuoihanhtrang(self, soogiu = 2, thoigianchoketqua = 0.5, solanthatbaitoida = 3, thoigianboqua = 60.):
        # Đang vận khí (chế đồ) thì soogiu ô mở cuối của hành trang 1 luôn phải trống (giữ 2 ô cho thong thả, 1 ô dễ không kịp),
        # không thì chế thất bại báo hành trang đầy dù hành trang 2-4 còn chỗ: có vật phẩm thì chuyển sang hành trang khác còn chỗ.
        # Chạy trong luồng riêng chu kỳ ngắn (LoopGiuOTrongHanhTrang), lệnh gửi thẳng không qua hàng đợi, mỗi lần chuyển 1 vật phẩm.
        # Vật phẩm vừa chuyển rời các ô giữ là thành công, canh tiếp ngay (ô có thể bị vật phẩm mới chiếm liền sau đó);
        # quá thoigianchoketqua giây vẫn còn là thất bại, gửi lại; thất bại solanthatbaitoida lần thì báo và bỏ qua vật phẩm đó thoigianboqua giây
        # Đang bật di chuyển tự do (lộ trình điểm đánh) thì không làm: chỉ dùng khi đứng chế đồ
        if self._is_dangsapxephanhtrang or not self.moitruong.get_is_dangvankhi() or self._is_tudongdichuyendiemdanhxungquanh:
            self._idvatphamotrongdangchuyen = 0
            self._solanchuyenotrongthatbai = 0
            return

        # Ô đang mở (túi phụ có thể chỉ mở 4/6/12 ô): ô giữ = soogiu ô mở cuối của túi 1, túi đích phải còn ô MỞ trống
        vitrimos = self.moitruong.get_danhsachvitrimohanhtrang()
        vitrimotui1s = [vitri for vitri in vitrimos if vitri < SOLUONGOMOITUI]
        if not vitrimotui1s or len(vitrimos) == len(vitrimotui1s):
            return
        soluongo = vitrimos[-1] + 1
        # Đọc riêng các ô giữ trước (4 byte mỗi ô), trống hết thì xong luôn; chỉ đọc cả hành trang khi cần tìm túi đích
        idtaios = {vitri: self.moitruong.get_iddoituongvatphamhanhtrang(vitri) for vitri in vitrimotui1s[-soogiu:]}

        # Lần chuyển trước: vật phẩm đã rời các ô giữ là thành công, quá thoigianchoketqua giây vẫn còn là thất bại
        if self._idvatphamotrongdangchuyen:
            if self._idvatphamotrongdangchuyen not in idtaios.values():
                print("{}: đã chuyển vật phẩm khỏi ô cuối hành trang 1 sau {:.2f} giây".format(
                    self.moitruong.get_tendoituong(), time.time() - self._thoidiemchuyenotronggannhat))
                self._idvatphamotrongdangchuyen = 0
                self._solanchuyenotrongthatbai = 0
            elif time.time() - self._thoidiemchuyenotronggannhat < thoigianchoketqua:
                return
            else:
                self._solanchuyenotrongthatbai += 1
                if self._solanchuyenotrongthatbai >= solanthatbaitoida:
                    vitrithatbai = next(vitri for vitri, idtaio in idtaios.items() if idtaio == self._idvatphamotrongdangchuyen)
                    print("{}: chuyển {} khỏi ô cuối hành trang 1 thất bại {} lần, bỏ qua {:.0f} giây".format(
                        self.moitruong.get_tendoituong(), self.moitruong.get_tenvatphamhanhtrang(vitrithatbai), self._solanchuyenotrongthatbai, thoigianboqua))
                    canhbao(self.moitruong, "Không chuyển được vật phẩm ở ô cuối hành trang 1")
                    self._thoidiemhetboquaotrong_map[self._idvatphamotrongdangchuyen] = time.time() + thoigianboqua
                    self._idvatphamotrongdangchuyen = 0
                    self._solanchuyenotrongthatbai = 0
                    return

        self._thoidiemhetboquaotrong_map = {k: v for k, v in self._thoidiemhetboquaotrong_map.items() if v > time.time()}
        # Vật phẩm cần chuyển: đang chuyển dở (gửi lại) thì giữ nguyên, không thì ô giữ đầu tiên có vật phẩm chưa bị bỏ qua
        vitricuoi = next((vitri for vitri, idtaio in idtaios.items() if idtaio and idtaio == self._idvatphamotrongdangchuyen), None)
        if vitricuoi is None:
            vitricuoi = next((vitri for vitri, idtaio in idtaios.items() if idtaio and idtaio not in self._thoidiemhetboquaotrong_map), None)
        if vitricuoi is None:
            return
        idvatpham = idtaios[vitricuoi]

        # Hành trang đích: túi đầu tiên (từ túi 2) còn ô trống
        ids = self.moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        if len(ids) < soluongo:
            return
        tuidich = next((vitri // 24 + 1 for vitri in vitrimos if vitri >= 24 and not ids[vitri]), None)
        if tuidich is None:
            if self._solanchuyenotrongthatbai == 0 and not self._idvatphamotrongdangchuyen:
                canhbao(self.moitruong, "Các hành trang khác đã đầy, không chuyển được ô cuối hành trang 1")
                baosuco(self.moitruong, "vatpham", "Hành trang đã đầy", giancach = 1800.)
            self._thoidiemhetboquaotrong_map[idvatpham] = time.time() + thoigianboqua
            return

        if self.moitruong.action_dichuyenvatphamsanghanhtrangkhac(idvatpham, tuidich, delay = 0., is_guingay = True):
            if self._idvatphamotrongdangchuyen != idvatpham:
                print("{}: chuyển {} từ ô cuối hành trang 1 sang hành trang {}".format(
                    self.moitruong.get_tendoituong(), self.moitruong.get_tenvatphamhanhtrang(vitricuoi), tuidich))
                # Chế đồ liên tục thì món nào cũng rơi vào ô này: chỉ đọc thông báo tối đa 10 giây 1 lần
                if time.time() - self._thoidiemphatamchuyenotronggannhat > 10.:
                    self._thoidiemphatamchuyenotronggannhat = time.time()
                    phatam("Chuyển vật phẩm ô cuối sang hành trang {}".format(tuidich))
            self._idvatphamotrongdangchuyen = idvatpham
            self._thoidiemchuyenotronggannhat = time.time()

    def _get_soluongneuxepchongduoc(self, idvitri, tenvatpham):
        # Số lượng ở ô idvitri nếu món này xếp chồng được, không thì None. Tự nhận biết, không cần danh sách tên: game ghi số lượng >= 1
        # cho món xếp chồng (thuốc, nguyên liệu...), trang bị / bí kíp / pháp bảo luôn 0
        soluong = self.moitruong.get_soluongvatphamhanhtrang(idvitri)
        if not soluong or soluong < 1:
            return None
        if soluong > self._soluongchonglonnhat_map.get(tenvatpham, 0):
            self._soluongchonglonnhat_map[tenvatpham] = soluong
        return soluong

    def _get_soluongxepchongtoida(self, tenvatpham):
        # 1 ô chồng tối đa bao nhiêu: ghi trong SOLUONGXEPCHONGTOIDA_MAP (món khác mức chung), không thì SOLUONGXEPCHONGMACDINH
        # (game nâng lên 100), từng thấy chồng lớn hơn thì lấy số đó
        return SOLUONGXEPCHONGTOIDA_MAP.get(tenvatpham) or max(SOLUONGXEPCHONGMACDINH, self._soluongchonglonnhat_map.get(tenvatpham, 0))

    def _chonbuocxepchong(self, chongchuaday_map):
        # chongchuaday_map: {tên: [(ô, id vật phẩm, số lượng), ...]} các chồng chưa đầy theo thứ tự ô. -> (ô nguồn, id nguồn, ô đích) hoặc None.
        # Cùng tên cùng mô tả mà khác trạng thái khoá (khoá / giao dịch được) thì game không gộp, client không có cờ khoá để biết trước:
        # chuyển thử, quá 3s số lượng 2 món không đổi thì nhớ cặp id này không gộp được, lần sau ghép món đó với chồng khác cùng tên
        soluongtheoid = {idvp: soluong for chongs in chongchuaday_map.values() for _, idvp, soluong in chongs}
        if self._langopgannhat:
            idnguon, iddich, slnguon, sldich, thoidiem, ten = self._langopgannhat
            if soluongtheoid.get(idnguon) != slnguon or soluongtheoid.get(iddich) != sldich:
                self._langopgannhat = None
            elif time.time() - thoidiem > 3.:
                if len(self._capkhonggopduocs) > 500:
                    self._capkhonggopduocs.clear()
                self._capkhonggopduocs.add(frozenset((idnguon, iddich)))
                print(f"[XẾP CHỒNG] 2 chồng {ten} không gộp được (khác trạng thái khoá?), ghép với chồng khác")
                self._langopgannhat = None
            else:
                # Chờ game cập nhật kết quả lần gộp trước
                return None
        for ten, chongs in chongchuaday_map.items():
            for k, (odich, iddich, sldich) in enumerate(chongs):
                for onguon, idnguon, slnguon in chongs[k + 1:]:
                    if frozenset((idnguon, iddich)) in self._capkhonggopduocs:
                        continue
                    self._langopgannhat = (idnguon, iddich, slnguon, sldich, time.time(), ten)
                    return onguon, idnguon, odich
        return None

    def _laychongchuaday_map(self, cacvitri, tens, ids):
        # {tên: [(ô, id vật phẩm, số lượng), ...]} các chồng chưa đầy của món xếp chồng được (tự nhận biết), chỉ tên có từ 2 chồng
        chongchuaday_map = {}
        for i in cacvitri:
            if not ids[i] or not tens[i]:
                continue
            soluong = self._get_soluongneuxepchongduoc(i, tens[i])
            if soluong is not None and soluong < self._get_soluongxepchongtoida(tens[i]):
                chongchuaday_map.setdefault(tens[i], []).append((i, ids[i], soluong))
        return {ten: chongs for ten, chongs in chongchuaday_map.items() if len(chongs) >= 2}

    def action_tudongxepchongvatpham(self, delay = 0.5):
        # Đang sắp xếp hành trang thì việc gộp chồng do action_sapxephanhtrang làm, không chuyển chen vào
        if self._is_tudongxepchongvatpham and not self._is_dangsapxephanhtrang:
            while True:
                if time.time() - self._thoidiemxepchongvatphamgannhat < delay:
                    break

                # Chuyển đồ trong hành trang không ngắt vận khí => vẫn xếp chồng lúc đang vận khí

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
                    break

                vatphamhanhtrang_map = self.moitruong.get_danhsachvatphamhanhtrang_map()
                tens, ids = {}, {}
                for tenvatpham, vitrivatphams in vatphamhanhtrang_map.items():
                    for vitri, idvatpham in vitrivatphams:
                        tens[vitri], ids[vitri] = tenvatpham, idvatpham

                # Mỗi lượt chuyển 1 chồng vào chồng cùng tên trước nó (bỏ qua cặp đã biết không gộp được: khác trạng thái khoá)
                buoc = self._chonbuocxepchong(self._laychongchuaday_map(sorted(ids), tens, ids))
                if buoc:
                    onguon, idnguon, odich = buoc
                    if onguon // 24 != odich // 24:
                        is_ok = self.moitruong.action_dichuyenvatphamsanghanhtrangkhac(idnguon, odich // 24 + 1, delay = delay)
                    else:
                        is_ok = self.moitruong.action_dichuyenvatphamhanhtrang(idnguon, odich + 1, delay = delay)
                    if is_ok:
                        self._thoidiemxepchongvatphamgannhat = time.time()
                break

    def _is_dosaokhongban(self, vitri, ten, is_docmoi = True):
        # Món đã ép sao (mô tả có ★, vd Ngọc Thần Bảo Kiếm 6★ bị bán rác ở PYK 2026-11-04) thì không bao giờ bán / vứt, kể cả không khớp
        # luật nào. Mô tả giữ theo ô (có thể còn của món trước): dòng tên phải khớp tên ô, không thì desc lại (is_docmoi). Chưa đọc được
        # mô tả thì coi như cần giữ (thà sót rác còn hơn bán nhầm đồ quý). -> True = không được bán / vứt
        tenchuan = unicodedata.normalize("NFC", re.sub(r"\x1b.", "", ten or "")).strip()

        def khoptheoten(mota):
            sach = unicodedata.normalize("NFC", re.sub(r"\x1b.", "", mota or ""))
            dongs = [d.strip() for d in sach.split("\n") if d.strip()]
            return sach if dongs and tenchuan and dongs[0].startswith(tenchuan) else None

        sach = khoptheoten(self.moitruong.get_motathovatphamhanhtrangcosan(vitri))
        if sach is None and is_docmoi:
            sach = khoptheoten(self.moitruong.get_motavatphamhanhtrang(vitri, thoigianchotoida = 1., is_napmoi = True) or "")
        if sach is None:
            return True
        return "★" in sach

    def action_tudongbanrac(self):
        diachi_npc = self.moitruong.action_timkiemnhanvat(CHUTIEMTAPHOA)
        if not diachi_npc:
            diachi_npc = self.moitruong.action_timkiemnhanvat(CHUTIEMTAPHOA)
            if not diachi_npc:
                return

        khoangcach = self.moitruong.get_khoangcach(diachi_npc)
        if khoangcach > 3.0:
            return

        idnpc = self.moitruong.get_iddoituong(diachi_npc)
        if not idnpc or idnpc <= 0:
            return

        # Chỉ xếp lệnh bán vào hàng đợi; action_xulybanracvasuado gửi dần 1 lệnh/giây ở mỗi lượt loop phụ
        hangdoi = []
        soluongvatphamhanhtrangtoida = self.moitruong.get_soluongvatphamhanhtrangtoida()
        for i in range(soluongvatphamhanhtrangtoida + 1):
            iddoituongvatphamhanhtrang = self.moitruong.get_iddoituongvatphamhanhtrang(i)
            if not iddoituongvatphamhanhtrang or iddoituongvatphamhanhtrang <= 0:
                continue

            tenvatphamhanhtrang = self.moitruong.get_tenvatphamhanhtrang(i)
            # Tên chưa đọc được (đang tải...) thì không khớp luật Giữ nào, đừng bán nhầm
            if not tenvatphamhanhtrang:
                continue
            # Theo luật túi đồ (luattuido_xq, tab Hành trang): không khớp luật nào hoặc luật Bán thì bán; Giữ / Vứt / Cất kho / chưa đọc được
            # mô tả (luật có điều kiện loại / mô tả) thì không bán
            hanhdong = self._layhanhdongluat(tenvatphamhanhtrang, i)
            # Món khớp luật Cất kho (dù luật đứng dưới luật Bán) thì để dành đi cất, không bán
            if hanhdong in (None, HANHDONG_BAN) and not self._is_catkhovatpham(tenvatphamhanhtrang, i):
                if self._is_dosaokhongban(i, tenvatphamhanhtrang):
                    print(f"[BÁN RÁC] {self.moitruong.get_tendoituong()}: chừa {tenvatphamhanhtrang} ở ô {i} (đồ có sao / chưa đọc được mô tả)")
                    continue
                hangdoi.append("sell ! {}# {}# 255".format(hex(idnpc).replace("0x", ""), hex(iddoituongvatphamhanhtrang).replace("0x", "")))
        self._datnhangdoibanrac(hangdoi)

    def _datnhangdoibanrac(self, lenhs):
        # Bắt đầu một đợt bán: hàng đợi lệnh mới, xoá lệnh đã gửi và số lần bán lại của đợt trước
        self._hangdoibanrac = list(lenhs)
        self._lenhbanracdagui = []
        self._solanthulaibanrac = 0
        self._thoidiemguibanractieptheo = 0.

    def get_is_dangbanrac(self):
        # Còn lệnh chờ gửi, hoặc đã gửi xong nhưng chưa kiểm tra lại túi (có thể còn phải bán lại)
        return bool(self._hangdoibanrac) or bool(self._lenhbanracdagui)

    def _kiemtrabanlairac(self):
        # Máy chủ thỉnh thoảng bỏ lệnh sell (chắc do giới hạn tốc độ gửi lệnh) => sau khi gửi hết, món nào (theo id) còn trong túi thì
        # xếp lại lệnh bán, tối đa SOLANTHULAIBANRAC lần. Gọi khi hàng đợi trống và đã qua lúc gửi lệnh kế tiếp.
        dagui, self._lenhbanracdagui = self._lenhbanracdagui, []
        if self._solanthulaibanrac >= SOLANTHULAIBANRAC:
            return
        idsconlai = set()
        for i in range(self.moitruong.get_soluongvatphamhanhtrangtoida() + 1):
            iddoituong = self.moitruong.get_iddoituongvatphamhanhtrang(i)
            if iddoituong and iddoituong > 0:
                idsconlai.add(iddoituong)
        conlai = []
        for lenh in dagui:
            try:
                iddoituong = int(lenh.split()[3].rstrip("#"), 16)
            except (IndexError, ValueError):
                continue
            if iddoituong in idsconlai:
                conlai.append(lenh)
        if not conlai:
            return
        self._solanthulaibanrac += 1
        print(f"[BÁN RÁC] {self.moitruong.get_tendoituong()}: còn {len(conlai)}/{len(dagui)} món chưa bán được, bán lại lần "
              f"{self._solanthulaibanrac}/{SOLANTHULAIBANRAC}")
        self._hangdoibanrac = conlai

    def get_is_dangsuavatpham(self):
        return bool(self._thoidiemhetsuavatpham)

    def action_xulybanracvasuado(self):
        # Gọi mỗi lượt loop phụ: gửi lệnh bán kế tiếp (cách nhau 1s), và đi tìm/sửa đồ nếu đang có việc sửa
        thoidiemhientai = time.time()
        if self._hangdoibanrac and thoidiemhientai >= self._thoidiemguibanractieptheo:
            lenh = self._hangdoibanrac.pop(0)
            self.moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_THAP)
            self._lenhbanracdagui.append(lenh)
            self._thoidiemguibanractieptheo = thoidiemhientai + 1.
            # Lệnh cuối: chờ thêm cho túi cập nhật rồi mới kiểm tra món nào chưa bán được
            if not self._hangdoibanrac:
                self._thoidiemguibanractieptheo += THOIGIANCHOKIEMTRABANRAC
        elif not self._hangdoibanrac and self._lenhbanracdagui and thoidiemhientai >= self._thoidiemguibanractieptheo:
            self._kiemtrabanlairac()

        if not self._thoidiemhetsuavatpham:
            return
        if thoidiemhientai > self._thoidiemhetsuavatpham:
            print("[Auto-SuaDo] Quá 30s không tìm thấy Chủ Tiệm Sửa Chữa. Hủy bỏ.")
            self._thoidiemhetsuavatpham = 0.
            return
        if thoidiemhientai - self._thoidiemkiemtrasuavatpham < 1.:
            return
        self._thoidiemkiemtrasuavatpham = thoidiemhientai

        diachinpc = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)
        if diachinpc and self.moitruong.get_khoangcach(diachinpc) <= 9.0:
            is_cansua = self._get_is_cansuavatpham()
            if is_cansua is None:
                return
            if is_cansua:
                print("[Auto-SuaDo] Đã tìm thấy NPC, đang sửa đồ...")
                self.moitruong.action_suavatpham(diachinpc)
            else:
                print("[Auto-SuaDo] Đồ còn nguyên độ bền, không cần sửa.")
            self._thoidiemhetsuavatpham = 0.
            return
        # Chủ Tiệm Sửa Chữa ở bản đồ nào cũng sửa được: thấy là đi tới; Tân Thủ Thôn chưa thấy thì đi về chỗ tiệm
        if diachinpc:
            self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 3.)
        elif self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
            self.moitruong.action_dichuyengiukhoangcachtoidadiem(111, 157, khoangcachtoida = 3.)
        self._thoidiemsudunghoithanhphugannhat = time.time()

    def _xulydangbanrac(self):
        # Bước 3 của về bán rác (dùng chung cho mọi phái): bán hết -> sửa đồ -> cất kho (tactu_catkho_xq) -> giao đồ nếu gặp người nhận
        # (tactu_giaodo_xq) -> trả về True khi xong (túi hết đầy)
        if time.time() < self._thoidiemthulaibanrac:
            return False
        if self._buocbanrac == 0:
            self.action_tudongbanrac()
            self._buocbanrac = 1
            return False
        if self._buocbanrac == 1:
            # Bán xong vẫn chờ 1s sau lệnh cuối như trước rồi mới sửa đồ
            if self.get_is_dangbanrac() or time.time() < self._thoidiemguibanractieptheo:
                return False
            self.action_suavatpham()
            self._buocbanrac = 2
            return False
        if self._buocbanrac == 2:
            if self.get_is_dangsuavatpham():
                return False
            # Sửa đồ xong: cất các món khớp luật Cất kho (không có món nào thì bước sau xong ngay)
            self.batdau_catkho_sauban()
            self._buocbanrac = 3
            return False
        if self._buocbanrac == 3:
            if not self._xulycatkhobanrac():
                return False
            # Cất kho xong: yêu cầu giao đang chờ mà người nhận đang ở đây thì giao luôn (tactu_giaodo_xq)
            self.batdau_giaodo_sauban()
            self._buocbanrac = 4
            return False
        if self._buocbanrac == 4 and not self._xulygiaodobanrac():
            return False
        self._buocbanrac = 0
        if not self.moitruong.get_is_dayhanhtrang():
            return True
        # Vẫn đầy (còn đồ không bán được): nghỉ 1s rồi bán lại, tránh lặp liên tục
        self._thoidiemthulaibanrac = time.time() + 1.
        return False

    def action_tudongxulyvebanrac(self):
        # Đang tự đi Phong Yêu Kính: bán rác ở Chu Quốc giữa các vòng (tactu_langlyson_xq._banracphongyeu), không Hồi Thành Phù về
        if (not self._is_tudongvebanrac and not self._is_tudongvesuado) or self.get_is_dangphongyeukinh():
            self._trangthaiveban = 0
            return

        # Chỉ chốt luồng khi đang rảnh; Mao Sơn chưa học Xuyên Không Hành thì đi Hồi Thành Phù + chạy bộ như phái khác
        if self._trangthaiveban == 0:
            self._is_vebanxuyenkhonghanh = self._is_coxuyenkhonghanh()

        if self._is_vebanxuyenkhonghanh:
            self._action_xulyvebanrac_maoson()
        else:
            self._action_xulyvebanrac_phaikhac()

    def _ghibandolucveban(self):
        # Gọi lúc bắt đầu về (trạng thái 0 -> 1): nhớ bản đồ đang đánh để quay lại. Đang ở thành / phó bản thì giữ bản đồ đã ghi trước đó
        idbando = self.moitruong.get_idbandohientai()
        if idbando and idbando not in (BANDO_TANTHUTHON, BANDO_CHUQUOC) and idbando not in BANDOPHOBANs:
            self._idbandolucveban = idbando

    def _get_idbandoquaylaibanrac(self):
        # Bản đồ quay lại sau khi bán theo ô "Quay lại" (tab Hành trang) -> id bản đồ, 0 = không biết đi đâu
        if self._idbandoquaylaibanrac > 0:
            return self._idbandoquaylaibanrac
        if self._idbandoquaylaibanrac == BANDOQUAYLAI_THEOLOTRINH and self._diemdanhxungquanhs and len(self._diemdanhxungquanhs[0]) >= 3:
            return self._diemdanhxungquanhs[0][2]
        # "Bản đồ lúc về", hoặc theo lộ trình mà chưa có lộ trình (bot đang dò bản đồ): về bản đồ đang đứng lúc bắt đầu về
        return self._idbandolucveban

    def _is_quaylaitheolotrinh(self):
        return self._idbandoquaylaibanrac == BANDOQUAYLAI_THEOLOTRINH and bool(self._diemdanhxungquanhs)

    def _batdauquaylaibando(self, idbando):
        # Quay lại bản đồ không theo lộ trình: giao cho "Đi tới bản đồ" (phù / chạy bộ / Hồi Thành Phù từng bản đồ, tới nơi thì dừng),
        # tới nơi mà không có lộ trình thì bot tự dò bản đồ (_dobandokhonglotrinh)
        print(f"[AUTO-SELL] Quay lại {laytenbando(idbando)}")
        self._idbandocandi = int(idbando)
        self._trangthaiveban = 0
        self._yeucautudo = None

    def _is_coxuyenkhonghanh(self):
        # Mao Sơn đã học Xuyên Không Hành (pf 4182) mới về bán / quay lại bãi bằng chiêu
        return self.moitruong.get_tenmonphai() == "maoson" and self.moitruong.get_is_kynangdahoc(VITRIKYNANG_XUYENKHONGHANH)

    def _action_xulyvebanrac_maoson(self):
        if not self._is_tudongvebanrac and not self._is_tudongvesuado:
            self._trangthaiveban = 0
            return

        if self.moitruong.get_tenmonphai() != "maoson":
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        chutiemtaphoa = "Chủ Tiệm Tạp Hóa"

        if self._trangthaiveban == 0:
            is_dayhanhtrang = self.moitruong.get_is_dayhanhtrang()

            diachi_npc = self.moitruong.action_timkiemnhanvat(chutiemtaphoa)
            is_dangganchutiemtaphoa = False
            # Chỉ bật về sửa đồ thì không tự bán / quay lại bãi khi đứng cạnh tiệm; đang Đi tới bản đồ (vừa bán xong, quay lại bản đồ
            # chọn sẵn) thì không xét lại
            if diachi_npc and self._is_tudongvebanrac and not self._idbandocandi:
                if self.moitruong.get_khoangcach(diachi_npc) <= 3.0:
                    is_dangganchutiemtaphoa = True

            if is_dangganchutiemtaphoa:
                if is_dayhanhtrang:
                    print("[AUTO-RECOVERY] Phát hiện đang ở cạnh NPC và túi đầy -> Tiếp tục bán.")
                    self._trangthaiveban = 2
                    self._thoidiemchuyentrangthai = time.time()
                else:
                    print("[AUTO-RECOVERY] Đang ở cạnh NPC và túi đã gọn -> Quay lại bãi train.")
                    self._trangthaiveban = 4
                    self._thoidiemchuyentrangthai = time.time()

            elif self._is_canve():
                self._ghibandolucveban()
                self._trangthaiveban = 1
                self._thoidiemchuyentrangthai = time.time()

        elif self._trangthaiveban == 1:
            if not self.moitruong.get_is_kynangsansang(VITRIKYNANG_XUYENKHONGHANH):
                print("[AUTO-SELL] Xuyên không hành thành công (đang hồi chiêu). Chuyển bước.")
                self._trangthaiveban = 2
                self._thoidiemchuyentrangthai = time.time()
                return

            if time.time() - self._thoidiemchuyentrangthai > 1.5:
                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                    print("[AUTO-SELL] Đã đứng yên. Sử dụng Xuyên không hành (Về thành)")
                    self.moitruong.action_ngatdichuyen()
                    self.moitruong.action_thucthicaulenh("pf 4182.1")
                    self._thoidiemchuyentrangthai = time.time()

        elif self._trangthaiveban == 2:
            if time.time() - self._thoidiemchuyentrangthai > 3.0:
                diachi_npc = self.moitruong.action_timkiemnhanvat(chutiemtaphoa)
                if diachi_npc:
                    khoangcach = self.moitruong.get_khoangcach(diachi_npc)
                    if khoangcach <= 3.0:
                        print("[AUTO-SELL] Đã gặp NPC, bắt đầu bán")
                        self._trangthaiveban = 3
                    else:
                        self.moitruong.action_dichuyengiukhoangcachtoida(diachi_npc, 3.)
                else:
                    print("[AUTO-SELL] Đang tìm NPC Tạp Hóa...")
                    if time.time() - self._thoidiemchuyentrangthai > 6.0:
                        print("[AUTO-SELL] Lỗi: Không tìm thấy NPC quá lâu -> Reset.")
                        self._trangthaiveban = 0

        elif self._trangthaiveban == 3:
            if self._xulybanracvamuabu():
                print("[AUTO-SELL] Đã bán xong, chuẩn bị quay lại")
                self._trangthaiveban = 4
                self._thoidiemchuyentrangthai = time.time()

        elif self._trangthaiveban == 4:
            # Chọn sẵn bản đồ quay lại khác bản đồ lúc về: Xuyên Không Hành (Quay lại) chỉ về chỗ cũ, nên đi bằng phù / chạy bộ
            if self._idbandoquaylaibanrac > 0 and self._idbandoquaylaibanrac != self._idbandolucveban:
                self._diachicosokhaikhoang = 0
                self._thoidiemphatamlacmapgannhat = time.time()
                self._batdauquaylaibando(self._idbandoquaylaibanrac)
                return
            if not self.moitruong.get_is_kynangsansang(VITRIKYNANG_XUYENKHONGHANH):
                print("[AUTO-SELL] Xuyên không hành (Quay lại) thành công. Kết thúc quy trình.")
                self._trangthaiveban = 0
                self._yeucautudo = None
                self._diachicosokhaikhoang = 0
                self._thoidiemphatamlacmapgannhat = time.time()
                return

            if time.time() - self._thoidiemchuyentrangthai > 1.0:
                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                    print("[AUTO-SELL] Đã đứng yên. Sử dụng Xuyên không hành (Quay lại)")
                    self.moitruong.action_ngatdichuyen()
                    self.moitruong.action_thucthicaulenh("pf 4182.2")
                    self._thoidiemchuyentrangthai = time.time()

    def _action_xulyvebanrac_phaikhac(self):
        if self._trangthaiveban == 0:
            diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = CHUTIEMTAPHOA)

            # Chỉ bật về sửa đồ thì không tự bán / quay lại bãi khi đứng cạnh tiệm; đang Đi tới bản đồ (vừa bán xong, quay lại bản đồ
            # chọn sẵn / lúc về) thì không xét lại, không thì lượt nào cũng đặt lại việc đi
            if self._is_tudongvebanrac and not self._idbandocandi and diachinpc and self.moitruong.get_khoangcach(diachinpc) <= 3.0:
                if not self.moitruong.get_is_dayhanhtrang():
                    if self._get_idbandoquaylaibanrac():
                        print("[AUTO-SELL] Đứng cạnh NPC và túi đã gọn. Tiếp tục quay lại bãi farm.")
                        self._trangthaiveban = 4
                        return
                else:
                    print("[AUTO-SELL] Đứng cạnh NPC nhưng túi đầy. Tiếp tục bán.")
                    self._trangthaiveban = 2
                    return
            if self._is_canve():
                print("[AUTO-SELL] Hành trang đầy / cần mua bù / cần sửa đồ. Bắt đầu quy trình về bán.")
                self._ghibandolucveban()
                self._trangthaiveban = 1
                self._thoidiemhoithanhphu = 0

        elif self._trangthaiveban == 1:
            if self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
                print("[AUTO-SELL] Đã về thành công. Chuyển sang di chuyển.")
                self._trangthaiveban = 2
                return

            if time.time() - self._thoidiemhoithanhphu > 12.0 and not self.moitruong.get_is_dangvankhi():
                print("[AUTO-SELL] Đang dùng Hồi Thành Phù...")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu()
                self._thoidiemhoithanhphu = time.time()

        elif self._trangthaiveban == 2:
            # Trước đây là vòng while chặn loop phụ tới 45s; giờ mỗi lượt (cách nhau >= 1s) làm 1 bước, quá 45s thì thử lại từ đầu
            thoigiantoida = 45.0
            if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
                return
            if not self._thoidiembatdautimnpcbanrac:
                self._thoidiembatdautimnpcbanrac = time.time()
            if time.time() - self._thoidiembatdautimnpcbanrac > thoigiantoida:
                print(f"[AUTO-SELL] Quá {thoigiantoida}s không tới được Tiệm Tạp Hóa. Thử lại.")
                self._thoidiembatdautimnpcbanrac = 0.
                self._trangthaiveban = 1
                return
            if time.time() - self._thoidiemkiemtranpcbanrac < 1.:
                return
            self._thoidiemkiemtranpcbanrac = time.time()
            diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = CHUTIEMTAPHOA)
            if self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
                if not diachinpc:
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(X_CHUTIEMTAPHOA_TANTHUTHON, Y_CHUTIEMTAPHOA_TANTHUTHON, khoangcachtoida = 0.)
                else:
                    khoangcach = self.moitruong.get_khoangcach(diachinpc)
                    if khoangcach <= 3.0:
                        print("[AUTO-SELL] Đã tìm thấy NPC, chuẩn bị bán đồ...")
                        self._thoidiembatdautimnpcbanrac = 0.
                        self._trangthaiveban = 3
                        return
                    else:
                        self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 0.)
            else:
                if not diachinpc:
                    print("[AUTO-SELL] Đang chờ load map hoặc chưa về thành...")

        elif self._trangthaiveban == 3:
            if self._xulybanracvamuabu():
                print("[AUTO-SELL] Đã bán xong.")
                self._trangthaiveban = 4

        elif self._trangthaiveban == 4:
            idbandodich = self._get_idbandoquaylaibanrac()
            if not idbandodich:
                print("[AUTO-SELL] Lỗi: Không biết quay lại bản đồ nào (chưa có lộ trình, chưa chọn bản đồ quay lại)!")
                self._trangthaiveban = 0
                return
            if not self._is_quaylaitheolotrinh():
                # Bản đồ chọn sẵn / bản đồ lúc về: đi tới bản đồ đó, tới nơi thì đánh theo lộ trình nếu có, không thì tự dò bản đồ
                self._batdauquaylaibando(idbandodich)
                return
            self.action_dichuyenlenbandofarm()
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if self.moitruong.get_idbandohientai() in danhsachbandohople:
                print("[AUTO-SELL] Đã tới bãi farm hợp lệ.")
                self._trangthaiveban = 0
            elif self.moitruong.get_idbandohientai() not in (BANDO_TANTHUTHON, BANDO_CHUQUOC):
                # Đã phù tới bản đồ gần bãi farm: để lộ trình điểm đánh chạy bộ tiếp
                print(f"[AUTO-SELL] Đã phù tới {laytenbando(self.moitruong.get_idbandohientai())}, chạy bộ tiếp tới bãi farm.")
                self._trangthaiveban = 0
