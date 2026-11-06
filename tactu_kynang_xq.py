# Phần kỹ năng: ưu tiên dùng kỹ năng, dùng kỹ năng từng môn phái, tâm pháp, Đào Hoa Nguyên, đổi đồ khi triệu hồi.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import json
import math
import os
import random
import sys
import time
import unicodedata

from hangso_xq import *
from moitruong_xq import MoiTruong, DOUUTIEN_THAP, DOUUTIEN_KHANCAP, DOUUTIEN_CAO, SOLUONGDOITUONGXUNGQUANHTOIDA, tinh_is_huongmatvediem
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam, canhbao
from tienich_xq import laynhomtodoitudongs, laynhanvattodoitudongs, donbangthoidiem


# Phái có "tancongvatly" ("kill") trong danh sách ưu tiên riêng (dùng khi bật Chỉ dùng Tự động tấn công)
PHAICOTANCONGVATLYRIENG = ("duongmon", "daohoanguyen", "camvequan")


class TacTuKyNang:
    def _is_duocguitamphapbattat(self, vitrikynang):
        # Tâm pháp bật / tắt: bấm lần nữa là tắt, nên chỉ gửi 1 lần rồi chờ THOIGIANCHOTAMPHAPBATTAT giây cho hiệu ứng hiện
        # (trước đây vòng lặp gửi 3 lần trong ~0.4s trước khi hiệu ứng kịp lên: bật - tắt - bật). Gọi cuối điều kiện, trả True thì ghi mốc
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemguitamphapbattat_map.get(vitrikynang, 0.) < THOIGIANCHOTAMPHAPBATTAT:
            return False
        self._thoidiemguitamphapbattat_map[vitrikynang] = thoidiemhientai
        return True

    def _lammoinguyenkhiquynguyen(self):
        # Quá ~30 phút server cho Nguyên Khí Quy Nguyên hết hạn mà client vẫn hiện hiệu ứng (người dùng phát hiện 2026-10-28: thiếu nguyên
        # khí mà không biết). Server báo "Tập trung vận khí “Nguyên Khí Quy Nguyên”." khi bật, "Bạn thu hồi …" khi tắt. Người dùng chốt:
        # client CÓ hiệu ứng thì chưa chắc server có, client KHÔNG có thì chắc chắn server không có. Nên:
        #  - không có hiệu ứng: chắc chắn tắt => bấm bật, bị từ chối (đang ra chiêu...) thì THOIGIANCHOTAMPHAPBATTAT giây sau bấm lại
        #  - có hiệu ứng, tin "Tập trung" chưa quá THOIGIANLAMMOINGUYENKHIQUYNGUYEN: đang bật
        #  - có hiệu ứng mà chưa có tin / quá hạn: bấm làm mới 1 lần rồi chờ tin (server bật thì thành thu hồi, hiệu ứng mất => nhánh đầu
        #    bật lại; server đã hết hạn thì thành bật). Chưa có tin thì không bấm tiếp trong THOIGIANCHOTINLAMMOINGUYENKHIQUYNGUYEN
        thoidiemhientai = time.time()
        for thoidiem, noidung in self.moitruong.get_lichsutrochuyen5s():
            if thoidiem <= self._thoidiemxettinnguyenkhiquynguyen or TENKYNANG_NGUYENKHIQUYNGUYEN not in noidung:
                continue
            self._thoidiemxettinnguyenkhiquynguyen = thoidiem
            if "Tập trung vận khí" in noidung:
                self._thoidiembatnguyenkhiquynguyen = thoidiem
            elif "thu hồi" in noidung:
                self._thoidiembatnguyenkhiquynguyen = None
        # Đọc bảng hiệu ứng chưa chắc (đang tải lại) thì coi như có: chỉ khi chắc chắn không có mới bấm ngay
        is_cohieuung = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGUYENKHIQUYNGUYEN,), True, is_hieuungcoloi = 1)
        dabat = self._thoidiembatnguyenkhiquynguyen
        if is_cohieuung:
            if dabat is not None and thoidiemhientai - dabat < THOIGIANLAMMOINGUYENKHIQUYNGUYEN:
                return
            # Chưa chắc trạng thái: đã bấm mà server chưa trả tin thì chờ, không bấm dồn (lỡ đang bật thì bấm thêm là tắt)
            thoidiemgui = self._thoidiemguitamphapbattat_map.get(VIRIKYNANG_NGUYENKHIQUYNGUYEN, 0.)
            if thoidiemgui > self._thoidiemxettinnguyenkhiquynguyen and thoidiemhientai - thoidiemgui < THOIGIANCHOTINLAMMOINGUYENKHIQUYNGUYEN:
                return
        elif dabat is not None and thoidiemhientai - dabat < THOIGIANCHOTAMPHAPBATTAT:
            # Vừa có tin bật mà hiệu ứng chưa kịp hiện trên client: chờ, đừng bấm thành tắt
            return
        if not self._is_kynangdungduoc(VIRIKYNANG_NGUYENKHIQUYNGUYEN) or not self._is_duocguitamphapbattat(VIRIKYNANG_NGUYENKHIQUYNGUYEN):
            return
        if self.moitruong.action_sudungkynangvitri(VIRIKYNANG_NGUYENKHIQUYNGUYEN) and IS_LOGCAULENH:
            lydo = "không có hiệu ứng" if not is_cohieuung else ("có hiệu ứng, chưa có tin bật" if dabat is None
                                                                else f"đã bật {(thoidiemhientai - dabat) / 60:.0f} phút, làm mới")
            self.moitruong._inlog(f"[NGUYÊN KHÍ QUY NGUYÊN] bấm: {lydo}")

    def _get_thoigianconlaihoichieunhatquyen(self, is_sansang):
        # Thời gian hồi chiêu còn lại của Nhất Quyền: ghi mốc lúc nó chuyển từ sẵn sàng sang đang hồi, lấy thời gian tái sử dụng trên mô tả
        # (không có thì THOIGIANHOICHIEUNHATQUYEN) trừ đi. Sẵn sàng thì 0
        thoidiemhientai = time.time()
        if self._is_nhatquyensansangtruoc and not is_sansang:
            self._thoidiemnhatquyenvaohoichieu = thoidiemhientai
        self._is_nhatquyensansangtruoc = is_sansang
        if is_sansang:
            return 0.
        tieuhao = self.moitruong.get_tieuhaokynang(VITRIKYNANG_NHATQUYENBATSON, is_truyvan = False) or {}
        thoigianhoichieu = tieuhao.get("tái sử dụng", THOIGIANHOICHIEUNHATQUYEN)
        return max(0., thoigianhoichieu - (thoidiemhientai - self._thoidiemnhatquyenvaohoichieu))

    def _ngattancongvatlydaohoa(self, diachimuctieu):
        # Đang đánh thường ("kill") mục tiêu này thì gửi "pf2 14" lên nó tới khi máy chủ báo "Bạn đã ngừng “Tự Động Công Kích”"
        # (pf2 14 bật / tắt qua lại: lỡ đang tắt thì lần gửi bật lại, báo "Sử dụng", lần sau gửi tiếp là tắt)
        if not self._is_battudongtancongvatly or not diachimuctieu or self._diachimuctieutancongvatly != diachimuctieu:
            return
        thoidiemhientai = time.time()
        if self._thoidiemguingattancongvatly > self.moitruong._thoidiemsudungtancongvatlygannhat:
            for thoidiem, noidung in reversed(self.moitruong.get_lichsutrochuyen5s()):
                if thoidiem < self._thoidiemguingattancongvatly:
                    break
                # Niết Bàn viết thường: "Bạn đã ngừng " Tự động công kích "lại." -> so không phân biệt hoa thường
                thuong = unicodedata.normalize("NFC", noidung).lower()
                if TENKYNANG_TUDONGCONGKICH.lower() in thuong:
                    if "ngừng" in thuong:
                        self._is_battudongtancongvatly = False
                        if IS_LOGCAULENH:
                            self.moitruong._inlog("[NGẮT ĐÁNH THƯỜNG] máy chủ báo đã ngừng")
                        return
                    break
        if thoidiemhientai - self._thoidiemguingattancongvatly < THOIGIANCHONGATTANCONGVATLY:
            return
        if self.moitruong.get_is_nguoichoi(diachimuctieu):
            caulenh = "pf2 {} {}".format(IDKYNANG_TUDONGCONGKICH, self.moitruong.get_idnguoichoi(diachimuctieu))
        else:
            caulenh = "pf2 {} {}#".format(IDKYNANG_TUDONGCONGKICH, hex(self.moitruong.get_iddoituong(diachimuctieu)).replace("0x", ""))
        if self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO):
            self._thoidiemguingattancongvatly = thoidiemhientai
            if IS_LOGCAULENH:
                self.moitruong._inlog(f"[NGẮT ĐÁNH THƯỜNG] nguyên khí {self.moitruong.get_nguyenkhiconlai()}: {caulenh}")

    def _is_nhuongbuffdaohoanguyen(self):
        # Có nhân vật Đào Hoa Nguyên khác chạy cùng máy, cùng nhóm, đứng trước mình trong danh sách tổ đội tự động,
        # đang bật tự dùng kỹ năng, còn sống và ở gần (cùng bản đồ, trong tầm buff) thì để nhân vật đó dùng Trấn Cổ Thần Uy / Hộ Thể Kim Cang
        thoidiemxet, is_nhuong = self._bonhonhuongbuffdaohoanguyen
        if time.time() - thoidiemxet < THOIGIANNHOSHAREDDATA:
            return is_nhuong

        is_nhuong = False
        if self.shared_data is not None and self.moitruong.get_is_dangnamtrongnhom():
            idnguoichoi = self.moitruong.get_idnguoichoi()
            danhsachuutien = next((list(nhom) for nhom in laynhomtodoitudongs() if idnguoichoi in nhom), [])
            if idnguoichoi in danhsachuutien:
                iduutiencaohons = set(danhsachuutien[:danhsachuutien.index(idnguoichoi)]) & set(self.moitruong.get_danhsachidnguoichoithanhviennhoms() or ())
                try:
                    danhsach = list(self.shared_data.items()) if iduutiencaohons else []
                except Exception:
                    danhsach = []
                idbandohientai = self.moitruong.get_idbandohientai()
                for idcuaso, info in danhsach:
                    if idcuaso == self.idcuaso or not isinstance(info, dict):
                        continue
                    if info.get("idnguoichoi") not in iduutiencaohons or info.get("tenmonphai") != "daohoanguyen":
                        continue
                    if time.time() - info.get("thoidiemcapnhat", 0.) > 5. or not info.get("_is_tudongsudungkynang") or info.get("status") == "Đã chết":
                        continue
                    if not self.moitruong.get_is_cungbando(info, idbandohientai) or info.get("x") is None:
                        continue
                    if self.moitruong.get_khoangcachtamdanhdiem(info["x"], info["y"]) > self._khoangcachsudungkynangtamxa:
                        continue
                    is_nhuong = True
                    break

        self._bonhonhuongbuffdaohoanguyen = (time.time(), is_nhuong)
        return is_nhuong

    def _thusudungkhaithientichdia(self, idtuthenhanvat, x_dich, y_dich, khoangcachtoithieu = 3.):
        # Đang di chuyển xa đích > 3 ô và nội lực trên mức % đặt ở giao diện thì dùng chiêu lướt về phía đích: Thục Sơn Khai Thiên Tịch
        # Địa (nhắm thẳng đích), Côn Luân Đằng Vân Giá Vũ (dịch chuyển tới điểm chọn trong tầm đánh xa: đích xa hơn thì nhắm điểm trên
        # đường thẳng tới đích, cách bản thân tầm xa - 0.5 ô). Trả về True khi đã dùng
        if self._is_chidungtudongtancong:
            return False
        tenmonphai = self.moitruong.get_tenmonphai()
        chieuluot = {"thucson": VITRIKYNANG_KHAITHIENTICHDIA, "conluan": VITRIKYNANG_DANGVANGIAVU}.get(tenmonphai)
        if idtuthenhanvat != TUTHENHANVAT_DICHUYEN or not chieuluot or self.moitruong.get_phantramnoilucconlai() <= self._phantramnoiluckhaithientichdia:
            return False
        if not x_dich or not y_dich:
            return False
        # Đang đi lấy góc cho Khai Thiên Tịch Địa đánh: giữ chiêu để ra ở chỗ mới, không lướt đi đường
        if tenmonphai == "thucson" and self._chodoikhaithien:
            return False
        toado = self.moitruong.get_toado()
        khoangcach = math.dist(toado, (x_dich, y_dich))
        if khoangcach <= khoangcachtoithieu:
            return False
        if tenmonphai == "conluan" and khoangcach > self._khoangcachsudungkynangtamxa - 0.5:
            tile = (self._khoangcachsudungkynangtamxa - 0.5) / khoangcach
            x_dich, y_dich = toado[0] + (x_dich - toado[0]) * tile, toado[1] + (y_dich - toado[1]) * tile

        if not self._capnhatchieuluotsansang(chieuluot):
            return False

        if tenmonphai == "thucson":
            # Khai Thiên Tịch Địa không lướt qua vật cản: xét đoạn thẳng tới đích (đích xa thì chỉ xét trong tầm đánh xa, quãng lướt thật)
            # và điểm rơi cũng phải đi được
            quangxet = min(khoangcach, self._khoangcachsudungkynangtamxa) / khoangcach
            x_roi, y_roi = toado[0] + (x_dich - toado[0]) * quangxet, toado[1] + (y_dich - toado[1]) * quangxet
            if self.moitruong.get_is_vatcan(x_roi, y_roi) or self.moitruong.get_is_doanthangcovatcan(*toado, x_roi, y_roi):
                return False

        return self._guichieuluot(chieuluot, x_dich, y_dich, tenmonphai)

    def _capnhatchieuluotsansang(self, chieuluot):
        # Chiêu lướt (Khai Thiên Tịch Địa / Đằng Vân Giá Vũ) dùng được chưa; vừa chuyển từ dùng được sang đang hồi (vừa ra chiêu) thì
        # tạm ngưng di chuyển 0.5s như bản cũ, vào tư thế xuất chiêu thì ngắt tiếp (action_ngatdichuyenkhixuatchieu)
        is_sansang = self.moitruong.get_is_kynangsansang(chieuluot) and self._is_dutieuhao(chieuluot)
        if self._is_khaithientichdiasansang and not is_sansang:
            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
            self._thoidiemhetchongatdichuyen = time.time() + THOIGIANCHONGATDICHUYENXUATCHIEU
        self._is_khaithientichdiasansang = is_sansang
        return is_sansang

    def _guichieuluot(self, chieuluot, x_dich, y_dich, tenmonphai):
        # Gửi chiêu lướt chọn toạ độ, gửi lại trong 0.8s mà chiêu vẫn sẵn sàng thì tính 1 lần thất bại, đủ số lần thì nghỉ 3s
        if self._solanthatbaikhaithien >=self._solanthatbaikhaithientoida and time.time() - self._thoidiembiphatkhaithien > 3.0:
            self._solanthatbaikhaithien = 0
            self._thoidiembiphatkhaithien = 0

        is_bicam = time.time() - self._thoidiemtamngungkhaithientichdia < 0.8
        if is_bicam and self._solanthatbaikhaithien < self._solanthatbaikhaithientoida:
            self._solanthatbaikhaithien += 1
            if self._solanthatbaikhaithien == self._solanthatbaikhaithientoida:
                self._thoidiembiphatkhaithien = time.time()

        if self._solanthatbaikhaithien < self._solanthatbaikhaithientoida:
            idkynang = self.moitruong.get_idkynang(chieuluot)
            if idkynang and self.moitruong.action_sudungkynangtoado(idkynang, int(round(x_dich)), int(round(y_dich)), delay = 0.05):
                # Chiêu lướt để đi đường: giữ trọn hoạt ảnh xuất chiêu (chặn client tự gửi "go" từ lúc gửi tới hết tư thế xuất chiêu,
                # đo: không chặn thì client gửi "go" ngay trong lúc xuất chiêu) nhưng không khựng thêm sau đó
                self.moitruong.set_is_chieucanngatdichuyen(True, is_khungsauxuatchieu = False)
                self._thoidiemhetchantudichuyentruocxuatchieu = time.time() + THOIGIANCHANTUDICHUYENTRUOCXUATCHIEU
                self.moitruong.action_chandichuyen()
                self._thoidiemtamngungkhaithientichdia = time.time()
                self._solansudungkhaithientichdia += 1
                if tenmonphai == "conluan":
                    self._thoidiemhetkhoachieusauluot = time.time() + THOIGIANKHOACHIEUSAULUOT
                return True
        return False

    def _diemkhaithientu(self, x0, y0, tx, ty, quais, r, luoi, ox, oy, is_rong = False):
        # Khai Thiên Tịch Địa (Thục Sơn, mô tả: "tấn công tất cả mục tiêu trong phạm vi tùy ý trước mặt", 40 pháp lực, hồi 6s) lướt từ
        # chỗ đứng (x0, y0) tới 1 toạ độ, sát thương mọi mục tiêu trong hình chữ nhật có 2 góc đối là chỗ đứng và điểm rơi (cạnh =
        # |delta X| x |delta Y|). Xét mọi ô trong tầm r (tầm ô vuông max(|dx|, |dy|)), điểm rơi phải đi được và đường lướt thẳng không qua
        # vật cản; hình luôn phải chứa mục tiêu đang chọn (tx, ty). Hai cách chọn (người dùng 2026-11-04):
        # - Bám mục tiêu (mặc định): dễ trúng mục tiêu đang đánh nhất, rơi kề nó để đánh tiếp không phải chạy bộ lại: điểm rơi kề mục tiêu,
        #   rồi mục tiêu nằm sâu trong hình (cách mép >= 1 ô, nó nhúc nhích vẫn trúng), rồi trúng thêm nhiều con, rồi lướt ngắn
        # - Rộng (is_rong, khi Lưu Tinh Truy Mạng dùng được ngay sau đó để lướt về mục tiêu): trúng nhiều con nhất, rồi diện tích lớn nhất;
        #   điểm rơi phải còn trong tầm tới mục tiêu và đường thẳng điểm rơi -> mục tiêu không vật cản (để Lưu Tinh lướt về được)
        # luoi[x - ox][y - oy] phải phủ đủ (x0 +- r, y0 +- r). -> (x, y, số mục tiêu trúng) hoặc None
        def is_vatcan(x, y):
            return luoi[x - ox][y - oy]

        def is_tronghinh(q, px, py):
            return min(x0, px) - 0.5 <= q[0] <= max(x0, px) + 0.5 and min(y0, py) - 0.5 <= q[1] <= max(y0, py) + 0.5

        def is_doanthong(xa, ya, xb, yb):
            # Lấy mẫu mỗi 0.5 ô trên đoạn (xa, ya) -> (xb, yb) như get_is_doanthangcovatcan (bỏ 2 đầu mút, xét riêng)
            sobuoc = max(1, math.ceil(math.hypot(xb - xa, yb - ya) * 2))
            for i in range(1, sobuoc):
                bx, by = round(xa + (xb - xa) * i / sobuoc), round(ya + (yb - ya) * i / sobuoc)
                if (bx, by) not in ((xa, ya), (xb, yb)) and is_vatcan(bx, by):
                    return False
            return True

        ungviens = []
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                px, py = x0 + dx, y0 + dy
                # Người dùng 2026-11-04: điểm rơi lệch cả X lẫn Y so với chỗ đứng (hình ít nhất 1 x 1, không lướt thẳng hàng)
                if not dx or not dy or max(abs(dx), abs(dy)) < 2 or is_vatcan(px, py) or not is_tronghinh((tx, ty), px, py):
                    continue
                cachmuctieu = max(abs(px - tx), abs(py - ty))
                if is_rong and cachmuctieu > r:
                    continue
                sotrung = sum(1 for q in quais if is_tronghinh(q, px, py))
                if is_rong:
                    khoa = (sotrung, (abs(dx) + 1) * (abs(dy) + 1), -cachmuctieu)
                else:
                    bien = min(tx - min(x0, px), max(x0, px) - tx, ty - min(y0, py), max(y0, py) - ty)
                    khoa = (-max(0, cachmuctieu - 1), min(1., bien), sotrung, -max(abs(dx), abs(dy)))
                ungviens.append((khoa, sotrung, px, py))
        ungviens.sort(key = lambda u: u[0], reverse = True)
        for _, sotrung, px, py in ungviens:
            if not is_doanthong(x0, y0, px, py):
                continue
            if is_rong and not is_doanthong(px, py, round(tx), round(ty)):
                continue
            return px, py, sotrung
        return None

    def _chondiemkhaithientichdia(self, diachimuctieu, quangdoicho = 0, is_rong = False):
        # Điểm rơi Khai Thiên Tịch Địa tốt nhất từ chỗ đang đứng, và (quangdoicho > 0) chỗ đứng lấy góc tốt nhất. Chỗ đứng lấy góc chỉ là
        # 8 ô quanh mục tiêu (|dx|, |dy| <= 1 so với mục tiêu, người dùng 2026-11-04: không chạy ra xa lấy đà rồi chiêu chưa dùng được lại
        # phải chạy về đánh), đi được, cách mình <= quangdoicho ô.
        # -> (điểm rơi từ chỗ hiện tại hoặc None, (chỗ đứng x, y, điểm rơi) tốt nhất hoặc None)
        toado = self.moitruong.get_toado()
        toadomuctieu = self.moitruong.get_toado(diachimuctieu) if diachimuctieu else None
        if not toado or not toadomuctieu:
            return None, None
        x0, y0 = round(toado[0]), round(toado[1])
        tx, ty = toadomuctieu
        r = int(self._khoangcachsudungkynangtamxa)
        if r < 2:
            return None, None
        rr = r + quangdoicho
        luoi = self.moitruong.get_luoivatcanvung(x0 - rr, y0 - rr, x0 + rr, y0 + rr)
        if not luoi:
            return None, None
        ox, oy = x0 - rr, y0 - rr
        quais = list(self._toadomuctieuhoples or ())
        if not any(abs(q[0] - tx) < 0.5 and abs(q[1] - ty) < 0.5 for q in quais):
            quais.append((tx, ty))
        # Chỉ tính mục tiêu với tới được: ngoài (r + quangdoicho) ô thì không hình nào chứa được
        quais = [q for q in quais if max(abs(q[0] - x0), abs(q[1] - y0)) <= rr + 1]

        hientai = self._diemkhaithientu(x0, y0, tx, ty, quais, r, luoi, ox, oy, is_rong)
        tot = None
        if quangdoicho > 0:
            mx, my = round(tx), round(ty)
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    sx, sy = mx + ex, my + ey
                    dx, dy = sx - x0, sy - y0
                    if (ex, ey) == (0, 0) or (dx, dy) == (0, 0) or max(abs(dx), abs(dy)) > quangdoicho or luoi[sx - ox][sy - oy]:
                        continue
                    diem = self._diemkhaithientu(sx, sy, tx, ty, quais, r, luoi, ox, oy, is_rong)
                    if not diem:
                        continue
                    khoa = (diem[2], -max(abs(dx), abs(dy)))
                    if tot is None or khoa > tot[0]:
                        tot = (khoa, (sx, sy, diem))
        return hientai, (tot[1] if tot else None)

    def _is_luutinhnoitiepkhaithien(self, noiluc):
        # Lưu Tinh Truy Mạng dùng được ngay sau Khai Thiên Tịch Địa (sẵn sàng, không bị phạt gửi hỏng, đủ pháp lực cho cả 2 chiêu theo
        # mô tả): khi đó Khai Thiên được chọn hình rộng nhất, rơi xa mục tiêu thì Lưu Tinh lướt về
        if not self.moitruong.get_is_kynangsansang(VITRIKYNANG_LUUTINHTRUYMANG) or not self._is_dutieuhao(VITRIKYNANG_LUUTINHTRUYMANG):
            return False
        if self._solanthatbailuutinhtruymang >= self._solanthatbailuutinhtruymangtoida:
            return False
        tieuhao = self._laytieuhao(VITRIKYNANG_KHAITHIENTICHDIA, "pháp lực") + self._laytieuhao(VITRIKYNANG_LUUTINHTRUYMANG, "pháp lực")
        return noiluc > max(150, tieuhao)

    def _thudungkhaithientichdiadanh(self, diachimuctieu, idtuthenhanvat, noiluc):
        # Thục Sơn đánh, ưu tiên số 1: Khai Thiên Tịch Địa dùng được thì ra chiêu (hình luôn chứa mục tiêu đang chọn). Lưu Tinh Truy Mạng
        # không nối được thì chọn điểm rơi bám mục tiêu (dễ trúng, rơi kề nó), không đi lấy góc. Lưu Tinh nối được thì chọn hình rộng
        # nhất; góc xấu (chỗ đứng trong QUANGDOICHOKHAITHIEN ô quanh mình trúng thêm từ SOMUCTIEUTANGDOICHOKHAITHIEN con) thì đi tới đó
        # trước. Chỗ đứng chốt theo mục tiêu đang đánh (tactu_muctieu khoá mục tiêu lúc đi; đổi mục tiêu / tới nơi / quá
        # THOIGIANGIUCHODOIKHAITHIEN giây / Lưu Tinh hết dùng được thì bỏ). Trả về True khi đã gửi chiêu hoặc đang đi lấy góc
        # Cập nhật trạng thái sẵn sàng trước mọi điều kiện khác: bỏ lượt nào là lỡ mốc vừa ra chiêu
        if not self._capnhatchieuluotsansang(VITRIKYNANG_KHAITHIENTICHDIA):
            self._ketthuclaygockhaithien("hetsansang", tuple(round(v) for v in self.moitruong.get_toado()))
            return False
        if idtuthenhanvat in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT) or noiluc <= 150:
            return False
        if not self._is_kynangdungduoc(VITRIKYNANG_KHAITHIENTICHDIA):
            return False

        is_rong = self._is_luutinhnoitiepkhaithien(noiluc)
        toado = tuple(round(v) for v in self.moitruong.get_toado())
        cho = self._chodoikhaithien
        if cho:
            lydo = "doimuctieu" if cho["diachimuctieu"] != diachimuctieu else "hetluutinh" if cho["is_rong"] and not is_rong \
                else "toinoi" if toado == cho["toado"] else "hethan" if time.time() > cho["hethan"] \
                else "muctieudichuyen" if max(abs(cho["toado"][0] - self.moitruong.get_toado(diachimuctieu)[0]),
                                              abs(cho["toado"][1] - self.moitruong.get_toado(diachimuctieu)[1])) > 1 else None
            if lydo:
                self._ketthuclaygockhaithien(lydo, toado)
                cho = None

        # Đi lấy góc (chỉ tới 8 ô quanh mục tiêu): Lưu Tinh nối được thì khi chỗ mới trúng thêm từ SOMUCTIEUTANGDOICHOKHAITHIEN con;
        # bám mục tiêu thì chỉ khi từ chỗ đang đứng không có điểm rơi nào (thẳng hàng, vật cản). Đang lùi giữ khoảng cách thì không đi
        quangdoicho = 0 if self._yeucaugiukhoangcach else QUANGDOICHOKHAITHIEN
        hientai, tot = self._chondiemkhaithientichdia(diachimuctieu, quangdoicho, is_rong)
        sohientai = hientai[2] if hientai else 0
        if cho and hientai and sohientai >= cho["sotrung"]:
            # Quái dồn lại: chỗ hiện tại đã tốt bằng chỗ chốt thì thôi đi, ra chiêu luôn
            self._ketthuclaygockhaithien("dutot", toado)
            cho = None
        is_dangdi = tot and ((is_rong and tot[2][2] >= sohientai + SOMUCTIEUTANGDOICHOKHAITHIEN) or not hientai)
        if is_dangdi and (not cho or tot[2][2] > cho["sotrung"]):
            # Đang đi tới chỗ đã chốt thì chỉ đổi khi chỗ mới trúng nhiều hơn (không đổi đích liên tục khi quái nhúc nhích)
            cu = cho or {}
            cho = self._chodoikhaithien = {"diachimuctieu": diachimuctieu, "toado": (tot[0], tot[1]), "sotrung": tot[2][2],
                                           "hethan": time.time() + THOIGIANGIUCHODOIKHAITHIEN,
                                           "batdau": cu.get("batdau", time.time()), "tu": cu.get("tu", toado),
                                           "sotruoc": cu.get("sotruoc", sohientai), "sodoidich": cu.get("sodoidich", -1) + 1,
                                           "is_rong": is_rong}
            if IS_LOGCAULENH:
                self.moitruong._inlog(f"[KHAI THIÊN] góc xấu (trúng {sohientai}): đi tới {cho['toado']} để trúng {cho['sotrung']}")
        if cho:
            self._yeucautancong = {
                "yeucau": YEUCAUDICHUYENTANCONG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                "diachimuctieu": diachimuctieu,
                "toadodich": cho["toado"],
                "khoangcachtoida": 0.,
            }
            self._is_giuyeucautancongcu = False
            return True

        if not hientai:
            return False
        self._yeucautancong = None
        self._is_giuyeucautancongcu = False
        if self._guichieuluot(VITRIKYNANG_KHAITHIENTICHDIA, hientai[0], hientai[1], "thucson"):
            if IS_LOGCAULENH:
                self.moitruong._inlog(f"[KHAI THIÊN] rơi ({hientai[0]}, {hientai[1]}) trúng {hientai[2]} mục tiêu")
            self._batdaudokhaithien(toado, hientai, diachimuctieu, "rong" if is_rong else "bammuctieu")
            if is_rong:
                # Khai Thiên rộng rơi xa: giữ mục tiêu này tới khi Lưu Tinh Truy Mạng lướt về đúng nó (tactu_muctieu không đổi sang con
                # gần chỗ rơi hơn, người dùng 2026-11-04); Lưu Tinh gửi xong / hết dùng được / quá THOIGIANKHOAMUCTIEULUUTINH giây thì thôi
                self._khoamuctieuluutinh = {"diachimuctieu": diachimuctieu, "hethan": time.time() + THOIGIANKHOAMUCTIEULUUTINH}
            return True
        return False

    # ---- Đo hiệu quả Khai Thiên Tịch Địa: mỗi lần ra chiêu 1 dòng jsonl ở _internal/khaithien/<id người chơi>.jsonl ----
    # Ghi: chỗ đứng, điểm rơi, số dự đoán trúng; máu (%) mọi mục tiêu quanh mình lúc gửi và THOIGIANDOKHAITHIEN giây sau khi game nhận
    # chiêu (chiêu chuyển sang hồi) => số con trong hình mất máu thật, số con ngoài hình mất máu (người khác đánh / hình sai); lần lấy
    # góc ngay trước đó (đi từ đâu tới đâu, mất bao lâu, trúng trước / sau). Phân tích: py _internal/phantich_khaithien.py

    def _ghilogkhaithien(self, banghi):
        try:
            thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
            thumuc = os.path.join(thumucgoc, "_internal", "khaithien")
            os.makedirs(thumuc, exist_ok = True)
            with open(os.path.join(thumuc, f"{self.moitruong.get_idnguoichoi()}.jsonl"), "a", encoding = "utf-8") as f:
                f.write(json.dumps(banghi, ensure_ascii = False) + "\n")
        except Exception as err:
            print(f"[Khai Thiên] Lỗi ghi log: {err}")

    def _ketthuclaygockhaithien(self, lydo, toado):
        # Bỏ chỗ đứng đang đi tới (lydo: toinoi / dutot / hethan / doimuctieu / hetsansang); nhớ lại để gắn vào lần ra chiêu ngay sau
        cho = self._chodoikhaithien
        self._chodoikhaithien = None
        if not cho:
            return
        laygoc = {"lydo": lydo, "tu": list(cho["tu"]), "dich": list(cho["toado"]), "toi": list(toado), "sotruoc": cho["sotruoc"],
                  "sodudoan": cho["sotrung"], "sodoidich": cho["sodoidich"], "thoigiandi": round(time.time() - cho["batdau"], 2),
                  "ketthuc": time.time()}
        if lydo in ("hethan", "doimuctieu", "hetsansang", "hetluutinh", "muctieudichuyen"):
            # Không ra chiêu sau lần đi này: ghi riêng 1 dòng
            self._ghilogkhaithien({"loai": "laygoc_huy", "thoidiem": time.strftime("%Y-%m-%d %H:%M:%S"), **laygoc})
            self._laygockhaithien = None
        else:
            self._laygockhaithien = laygoc

    def _batdaudokhaithien(self, toado, diem, diachimuctieu, chedo):
        # Gửi chiêu lần đầu thì chụp máu + số bay các mục tiêu quanh mình; gửi lại (spam tới khi game nhận) thì giữ bản chụp cũ
        if self._dokhaithien and time.time() - self._dokhaithien["thoidiemgui"] < 2.:
            return
        x0, y0 = toado
        px, py = diem[0], diem[1]

        def is_tronghinh(q):
            return min(x0, px) - 0.5 <= q[0] <= max(x0, px) + 0.5 and min(y0, py) - 0.5 <= q[1] <= max(y0, py) + 0.5

        doituongs = []
        for diachi in list(self._diachimuctieuhoples or ()):
            try:
                if not self.moitruong.get_is_nhanvattontai(diachi):
                    continue
                q = self.moitruong.get_toado(diachi)
                if max(abs(q[0] - x0), abs(q[1] - y0)) > int(self._khoangcachsudungkynangtamxa) + 2:
                    continue
                doituongs.append({"diachi": diachi, "id": self.moitruong.get_iddoituong(diachi), "toado": list(q),
                                  "mau": self.moitruong.get_phantramsinhlucconlai(diachi), "tronghinh": is_tronghinh(q),
                                  "lamuctieu": diachi == diachimuctieu, "sobay": self.moitruong.get_sobaydoituong(diachi), "satthuong": []})
            except Exception:
                continue
        laygoc = self._laygockhaithien if self._laygockhaithien and time.time() - self._laygockhaithien["ketthuc"] < 1.5 else None
        self._laygockhaithien = None
        # Tư thế lúc gửi + đang đánh thường không: tìm lý do game không nhận chiêu (đo 2026-11-04: bám mục tiêu hỏng ~50%, rộng ~8%)
        self._dokhaithien = {"thoidiemgui": time.time(), "thoidiemnhan": 0., "toado": [x0, y0], "diemroi": [px, py], "chedo": chedo,
                             "tuthe": self.moitruong.get_idtuthenhanvat(), "is_danhthuong": bool(self._is_battudongtancongvatly),
                             "sodudoan": diem[2], "doituongs": doituongs, "laygoc": laygoc, "thoidiemdungdem": 0.}

    def _demsobaykhaithien(self, do, is_tinh):
        # Số bay mới trên từng mục tiêu so với lần đọc trước (ô đổi giá trị / bộ đếm chạy lại). Số bay chỉ là sát thương của chính mình
        # (đánh nhóm vẫn đúng). is_tinh: đang trong cửa sổ đo (sau khi game nhận Khai Thiên, trước khi gửi chiêu khác) thì ghi lại
        for d in do["doituongs"]:
            if not d["sobay"]:
                continue
            try:
                if self.moitruong.get_iddoituong(d["diachi"]) != d["id"]:
                    continue
                moi = self.moitruong.get_sobaydoituong(d["diachi"])
            except Exception:
                continue
            if not moi:
                continue
            (giatricu, demcu), (giatri, dem) = d["sobay"], moi
            if is_tinh:
                for i in range(10):
                    if giatri[i] > 0 and (giatri[i] != giatricu[i] or dem[i] < demcu[i]):
                        d["satthuong"].append(giatri[i])
            d["sobay"] = moi

    def _capnhatdokhaithien(self):
        # Gọi mỗi lượt kỹ năng Thục Sơn: chờ game nhận chiêu (chiêu chuyển sang hồi), đếm số bay mới trên các mục tiêu trong
        # THOIGIANDOKHAITHIEN giây sau đó (dừng sớm khi gửi Lưu Tinh Truy Mạng / chiêu khác để không lẫn), rồi đọc lại máu và ghi log
        do = self._dokhaithien
        if not do:
            return
        bayg = time.time()
        if not do["thoidiemnhan"]:
            if not self.moitruong.get_is_kynangsansang(VITRIKYNANG_KHAITHIENTICHDIA):
                do["thoidiemnhan"] = bayg
            elif bayg - do["thoidiemgui"] > 2.:
                self._dokhaithien = None
                self._ghilogkhaithien({"loai": "khongnhan", "thoidiem": time.strftime("%Y-%m-%d %H:%M:%S"), "chedo": do["chedo"],
                                       "toado": do["toado"], "diemroi": do["diemroi"], "sodudoan": do["sodudoan"], "laygoc": do["laygoc"],
                                       "tuthe": do["tuthe"], "is_danhthuong": do["is_danhthuong"]})
                return
            # Chưa thấy chiêu vào hồi vẫn đếm: đo 2026-11-04 số bay hiện trước khi client báo chiêu hồi (~0.23s sau khi gửi), bỏ qua
            # đoạn này thì hụt gần hết số bay (mốc số bay đã chụp lúc gửi nên đòn trước đó không bị tính)
            self._demsobaykhaithien(do, True)
            return
        if not do["thoidiemdungdem"] and self._thoidiemtamngungluutinhtruymang > do["thoidiemnhan"]:
            do["thoidiemdungdem"] = self._thoidiemtamngungluutinhtruymang
        self._demsobaykhaithien(do, not do["thoidiemdungdem"])
        if bayg - do["thoidiemnhan"] < THOIGIANDOKHAITHIEN:
            return
        self._dokhaithien = None
        trungtrong = trungngoai = matmautrong = matmaungoai = chet = 0
        chitiet = []
        for d in do["doituongs"]:
            try:
                is_conguyen = self.moitruong.get_is_nhanvattontai(d["diachi"]) and self.moitruong.get_iddoituong(d["diachi"]) == d["id"]
                mausau = self.moitruong.get_phantramsinhlucconlai(d["diachi"]) if is_conguyen else None
                is_chet = not is_conguyen or self.moitruong.get_is_nhanvatdachet(d["diachi"])
            except Exception:
                mausau, is_chet = None, True
            is_matmau = is_chet or (mausau is not None and mausau < d["mau"])
            # Trúng = có số bay của mình, hoặc chết trong lúc đo (quái chết là mất đối tượng, không đọc được số bay nữa)
            is_trung = bool(d["satthuong"]) or is_chet
            chet += is_chet
            if d["tronghinh"]:
                trungtrong += is_trung
                matmautrong += is_matmau
            else:
                trungngoai += is_trung
                matmaungoai += is_matmau
            chitiet.append({"id": d["id"], "toado": d["toado"], "tronghinh": d["tronghinh"], "lamuctieu": d["lamuctieu"],
                            "mautruoc": d["mau"], "mausau": mausau, "chet": is_chet, "satthuong": d["satthuong"]})
        sotronghinh = sum(1 for d in do["doituongs"] if d["tronghinh"])
        self._ghilogkhaithien({
            "loai": "rachieu", "thoidiem": time.strftime("%Y-%m-%d %H:%M:%S"), "chedo": do["chedo"], "toado": do["toado"], "diemroi": do["diemroi"],
            "dx": do["diemroi"][0] - do["toado"][0], "dy": do["diemroi"][1] - do["toado"][1], "sodudoan": do["sodudoan"],
            # trungtrong / trungngoai: có số bay mới của mình (đo chính); matmau*: máu giảm (lẫn cả người khác đánh)
            "sotronghinh": sotronghinh, "trungtrong": trungtrong, "trungngoai": trungngoai, "matmautrong": matmautrong,
            "matmaungoai": matmaungoai, "chet": chet, "dodem": "sobay2", "tuthe": do["tuthe"], "is_danhthuong": do["is_danhthuong"],
            "thoigiandem": round((do["thoidiemdungdem"] or bayg) - do["thoidiemnhan"], 2),
            "tregui": round(do["thoidiemnhan"] - do["thoidiemgui"], 2), "laygoc": do["laygoc"], "doituongs": chitiet,
            # Chế độ rộng: Lưu Tinh Truy Mạng có được gửi nối ngay sau không (giây sau khi game nhận Khai Thiên, None = chưa gửi)
            "luutinhnoi": round(self._thoidiemtamngungluutinhtruymang - do["thoidiemnhan"], 2)
            if self._thoidiemtamngungluutinhtruymang >= do["thoidiemgui"] else None,
            # Lưu Tinh nối có lướt về đúng mục tiêu của Khai Thiên không (None = chưa gửi Lưu Tinh)
            "luutinhdungmuctieu": (getattr(self, "_idmuctieuluutinhgannhat", None) in [d["id"] for d in do["doituongs"] if d["lamuctieu"]])
            if self._thoidiemtamngungluutinhtruymang >= do["thoidiemgui"] else None,
        })

    def _chontamxa(self, thoidiemhientai):
        # Chọn tầm dùng cho lượt này. Mình không di chuyển >= THOIGIANDUNGYENTAMXA giây (hoặc đang nhích / tiếp cận ở chế độ đứng yên
        # trong THOIGIANNHICHTAMXA giây) và mục tiêu không di chuyển: toạ độ client khớp server nên dùng tầm học khi đứng yên (chưa có mẫu
        # thì thử tới tầm tối đa), chiêu trượt thì nhích vào NHICHTAMXA ô với mục tiêu đó. Ngược lại dùng tầm học khi di chuyển
        self._dolechlammoitoado(thoidiemhientai)
        moitruong = self.moitruong
        diachimuctieu = moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        idmuctieu = moitruong.get_iddoituong(diachimuctieu) if diachimuctieu else 0
        is_dangnhich = idmuctieu == self._tamxanhich[0] and thoidiemhientai - self._thoidiemnhichtamxa < THOIGIANNHICHTAMXA
        self._is_tamxadungyen = bool(idmuctieu) and moitruong.get_idtuthenhanvat(diachimuctieu) != TUTHENHANVAT_DICHUYEN \
            and (is_dangnhich or thoidiemhientai - moitruong.get_thoidiemtuthenhanvatkhongdichuyen() >= THOIGIANDUNGYENTAMXA)
        if not self._is_tamxadungyen:
            self._khoangcachsudungkynangtamxa = self._tamxadichuyen
            return
        tam = self._tinhtamxahoc(self._tileratamxadungyen)
        if idmuctieu == self._tamxanhich[0]:
            tam = min(tam, self._tamxanhich[1])
        self._khoangcachsudungkynangtamxa = max(min(TAMXATOITHIEU, self._tamxatoida), tam)

    def _is_cholammoitoado(self, thoidiemhientai):
        # Chiêu tầm xa vừa trượt (lệch toạ độ client - server): gửi lệnh danh hiệu để máy chủ gửi lại trạng thái nhân vật (client lấy toạ
        # độ thật) rồi chờ THOIGIANCHOLAMMOITOADO giây mới bắn. Làm mới tốn tài nguyên game nên cách lần trước tối thiểu
        # THOIGIANGIANCACHLAMMOITOADO giây, chưa đủ thì chỉ nhích vào (xem _capnhattamxa). True = chưa bắn lượt này
        thoigian = thoidiemhientai - self._thoidiemlammoitoado
        if thoigian < THOIGIANCHOLAMMOITOADO:
            return True
        if not self._is_lammoisautruot or thoigian < THOIGIANGIANCACHLAMMOITOADO:
            return False
        if not self.action_lammoitrangthai():
            return False
        self._is_lammoisautruot = False
        self._thoidiemlammoitoado = thoidiemhientai
        # Toạ độ đã chuẩn: bỏ tầm nhích còn sót, trong tầm học khi đứng yên là bắn
        self._tamxanhich = (0, 0.)
        self._toadotruoclammoi = self.moitruong.get_toado()
        return True

    def _dolechlammoitoado(self, thoidiemhientai):
        # Sau khi làm mới toạ độ: toạ độ client nhảy (lúc mình không di chuyển) là đã lấy lại toạ độ máy chủ, log độ lệch và sau bao lâu
        if not self._toadotruoclammoi:
            return
        moitruong = self.moitruong
        thoigian = thoidiemhientai - self._thoidiemlammoitoado
        if moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
            self._toadotruoclammoi = None
            return
        dolech = math.dist(self._toadotruoclammoi, moitruong.get_toado())
        if dolech > 0.1:
            moitruong._inlog(f"[LÀM MỚI TOẠ ĐỘ] client lệch {dolech:.1f} ô, nhận sau {thoigian:.2f}s")
            self._toadotruoclammoi = None
        elif thoigian >= THOIGIANDOLECHLAMMOI:
            moitruong._inlog(f"[LÀM MỚI TOẠ ĐỘ] không lệch ({thoigian:.1f}s)")
            self._toadotruoclammoi = None

    def _doikhoangcachtiepcan(self, diachimuctieu, khoangcachtamdanh):
        # Tầm đánh đo theo ô max(|dx|, |dy|) (get_khoangcachtamdanh) nhưng hàm đi giữ khoảng cách dừng theo đường thẳng: đi thẳng về
        # mục tiêu thì max(|dx|, |dy|) giảm cùng tỉ lệ với đường thẳng => quy đổi theo tỉ lệ hiện tại (chéo dừng xa hơn, thẳng hàng như cũ)
        moitruong = self.moitruong
        x1, y1 = moitruong.get_toado()
        x2, y2 = moitruong.get_toado(diachimuctieu)
        o = max(abs(x2 - x1), abs(y2 - y1))
        if o <= 0:
            return khoangcachtamdanh
        return khoangcachtamdanh * math.dist((x1, y1), (x2, y2)) / o

    def _ghinhichtamxa(self, diachimuctieu, tam, thoidiemhientai):
        # Đang tiếp cận / nhích ở chế độ đứng yên: giữ chế độ đứng yên trong lúc đi (xem _chontamxa), tầm với mục tiêu này không vượt tam
        idmuctieu = self.moitruong.get_iddoituong(diachimuctieu)
        if idmuctieu != self._tamxanhich[0]:
            self._tamxanhich = (idmuctieu, tam)
        self._thoidiemnhichtamxa = thoidiemhientai

    def _capnhattamxa(self, thoidiemhientai):
        # Xem chiêu tầm xa vừa gửi có ra không (xem THOIGIANCHOCHIEUNHAN trong hangso_xq.py): vào hồi chiêu / tư thế xuất chiêu là ra,
        # hết giờ chờ mà chưa thấy (mục tiêu vẫn còn, mình còn sống) là không ra. Ghi vào thống kê theo khoảng cách và chế độ (đứng yên /
        # di chuyển) lúc gửi rồi tính lại tầm; đứng yên mà không ra thì nhích vào NHICHTAMXA ô với mục tiêu đó
        self._logthongketamxa(thoidiemhientai)
        chieu = self._chieuchonhantamxa
        if not chieu:
            return
        moitruong = self.moitruong
        if not moitruong.get_is_kynangsansang(chieu["vitri"]) \
                or moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT):
            is_ra = True
        elif thoidiemhientai - chieu["thoidiem"] < THOIGIANCHOCHIEUNHAN:
            return
        elif moitruong.get_is_nhanvatdachet() or moitruong.get_iddoituong(chieu["diachimuctieu"]) != chieu["idmuctieu"]:
            self._chieuchonhantamxa = None
            return
        else:
            is_ra = False
        self._chieuchonhantamxa = None
        self._logchitiettamxa(chieu, is_ra)
        if not is_ra:
            # Trượt (đứng yên hay di chuyển): lần bắn kế tiếp làm mới toạ độ (nếu đã cách lần trước đủ lâu, xem _is_cholammoitoado)
            self._is_lammoisautruot = True
        o = int(chieu["khoangcach"])
        is_dungyen = chieu["is_dungyen"]
        self._thongketamxa.setdefault((is_dungyen, o), [0, 0])[0 if is_ra else 1] += 1
        self._ghitilera(self._tileratamxadungyen if is_dungyen else self._tileratamxa, o, is_ra, thoidiemhientai)
        if is_dungyen:
            if not is_ra and self._danhhieulammoi != DANHHIEULAMMOI_KHONG \
                    and thoidiemhientai - self._thoidiemlammoitoado >= THOIGIANGIANCACHLAMMOITOADO:
                # Lần bắn kế tiếp làm mới toạ độ được (_is_cholammoitoado): làm mới xong toạ độ client khớp server, đang trong tầm thì
                # bắn luôn, không nhích. Chưa đặt danh hiệu làm mới / vừa làm mới chưa đủ lâu thì nhích như cũ
                moitruong._inlog(f"[TẦM XA] đứng yên không ra ở {chieu['khoangcach']:.1f} ô => làm mới toạ độ, không nhích"
                                 f" | đứng yên: {self._motatilera(self._tileratamxadungyen)}")
            elif not is_ra:
                self._tamxanhich = (chieu["idmuctieu"], max(min(TAMXATOITHIEU, self._tamxatoida), chieu["khoangcach"] - NHICHTAMXA))
                self._thoidiemnhichtamxa = thoidiemhientai
                moitruong._inlog(f"[TẦM XA] đứng yên không ra ở {chieu['khoangcach']:.1f} ô => nhích còn {self._tamxanhich[1]:.1f}"
                                 f" | đứng yên: {self._motatilera(self._tileratamxadungyen)}")
            return
        tamcu = self._tamxadichuyen
        self._tamxadichuyen = self._tinhtamxahoc(self._tileratamxa)
        self._khoangcachvoitoimuctieu = min(self._khoangcachvoitoimuctieu, self._tamxadichuyen - TRUHAOTAMXACHONMUCTIEU)
        if self._tamxadichuyen != tamcu:
            moitruong._inlog(f"[TẦM XA] di chuyển {'ra' if is_ra else 'không ra'} ở {chieu['khoangcach']:.1f} ô, tầm {tamcu:.1f} -> {self._tamxadichuyen:.1f}"
                             f" (tối đa {self._tamxatoida:.0f}) | {self._motatilera(self._tileratamxa)}")

    def _logchitiettamxa(self, chieu, is_ra):
        # Tìm nguyên nhân trượt ở 9-11 ô dù toạ độ mình đã làm mới: toạ độ mình / mục tiêu lúc gửi (vẽ và ô bước tới +0x18), dx dy,
        # khoảng cách theo ô (max) và Manhattan (máy chủ đo khác?), mục tiêu có đang đi không, và mục tiêu đã dịch bao nhiêu tới lúc biết kết quả
        moitruong = self.moitruong
        xm, ym = chieu["toadominh"]
        xt, yt = chieu["toadomuctieu"]
        dx, dy = xt - xm, yt - ym
        dich = ""
        if moitruong.get_iddoituong(chieu["diachimuctieu"]) == chieu["idmuctieu"]:
            dich = f", mục tiêu dịch {math.dist((xt, yt), moitruong.get_toado(chieu['diachimuctieu'])):.1f} ô"
        moitruong._inlog(f"[TẦM XA CHI TIẾT] {'ra' if is_ra else 'TRƯỢT'} {'đứng yên' if chieu['is_dungyen'] else 'di chuyển'}"
                         f" | mình {(xm, ym)} bước {chieu['buocminh']} | mục tiêu {(xt, yt)} bước {chieu['buocmuctieu']}"
                         f"{' đang đi' if chieu['is_muctieudi'] else ''} | dx {dx} dy {dy}: thẳng {math.hypot(dx, dy):.1f},"
                         f" ô {max(abs(dx), abs(dy))}, Manhattan {abs(dx) + abs(dy)}{dich}")

    def _ghitilera(self, bang, o, is_ra, thoidiemhientai):
        # Thống kê lâu dài {ô: [ra, gửi]} (số thực) của cả hai bảng: giảm một nửa sau mỗi BANRATAMXA giây, mỗi ô giữ tối đa SOMAUTOIDATAMXA
        # lần gửi. Giảm không xuống dưới SOMAUTOITHIEUTAMXA lần gửi: ô đã biết là hay trượt không bị coi là "chưa đủ mẫu" rồi nhảy tầm lên tối đa
        heso = 0.5 ** ((thoidiemhientai - self._thoidiemcapnhattilera) / BANRATAMXA) if self._thoidiemcapnhattilera else 1.
        self._thoidiemcapnhattilera = thoidiemhientai
        for dem in (*self._tileratamxa.values(), *self._tileratamxadungyen.values()):
            if dem[1] > 0.:
                tile = max(heso, min(1., SOMAUTOITHIEUTAMXA / dem[1]))
                dem[0] *= tile
                dem[1] *= tile
        dem = bang.setdefault(o, [0., 0.])
        dem[0] += 1. if is_ra else 0.
        dem[1] += 1.
        if dem[1] > SOMAUTOIDATAMXA:
            tile = SOMAUTOIDATAMXA / dem[1]
            dem[0] *= tile
            dem[1] *= tile

    def _tinhtamxahoc(self, bang):
        # Ô xa nhất (khoảng cách tầm đánh max(|dx|, |dy|) là số nguyên, bắn khi <= tầm) mà mọi ô trên sàn TAMXATOITHIEU tới đó đạt
        # NGUONGTILERATAMXA (ô chưa đủ mẫu coi như đạt), trong [sàn, tối đa]
        san = min(TAMXATOITHIEU, self._tamxatoida)
        tam = san
        o = int(san) + 1
        while o <= self._tamxatoida:
            ra, gui = bang.get(o, (0., 0.))
            if gui >= SOMAUTOITHIEUTAMXA and ra / gui < NGUONGTILERATAMXA:
                break
            tam = float(o)
            o += 1
        return min(self._tamxatoida, max(san, tam))

    def _motatilera(self, bang):
        return ", ".join(f"{o} ô {100 * ra / gui:.0f}% ({gui:.0f})" for o, (ra, gui) in sorted(bang.items()) if gui >= 1) or "chưa có"

    def _logthongketamxa(self, thoidiemhientai):
        # Mỗi THOIGIANLOGTHONGKETAMXA giây: số chiêu tầm xa ra / không ra theo chế độ và khoảng cách lúc gửi (làm tròn xuống) rồi xoá để đếm lại
        if thoidiemhientai - self._thoidiemlogthongketamxa < THOIGIANLOGTHONGKETAMXA:
            return
        self._thoidiemlogthongketamxa = thoidiemhientai
        if not self._thongketamxa:
            return
        chitiet = " | ".join(
            f"{'đứng yên' if is_dungyen else 'di chuyển'}: " + ", ".join(f"{kc} ô {ra}/{ra + khong}" for (dy, kc), (ra, khong) in sorted(self._thongketamxa.items()) if dy == is_dungyen)
            for is_dungyen in (True, False) if any(dy == is_dungyen for dy, _ in self._thongketamxa))
        self.moitruong._inlog(f"[TẦM XA] thống kê {THOIGIANLOGTHONGKETAMXA:.0f}s (ra/gửi) {chitiet} | tầm di chuyển {self._tamxadichuyen:.1f},"
                              f" đứng yên {self._tinhtamxahoc(self._tileratamxadungyen):.1f} (tối đa {self._tamxatoida:.0f})")
        self._thongketamxa = {}

    def action_xulyuutiensudungkynang(self, loaikynang, vitrikynang, diachimuctieu, khoangcachyeucau = 0, is_yeucaukhongdichuyen = False, is_ngatdichuyen = False):
        thoidiemhientai = time.time()
        self._capnhattamxa(thoidiemhientai)
        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        thoigiandungim = 0.
        if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
            thoigiandungim = thoidiemhientai - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu) if diachimuctieu else 0.

        # Đang lùi giữ khoảng cách với kẻ tấn công: bỏ chiêu đánh, phủ đầu, mọi bước tiếp cận và Lôi Động Cửu Thiên (vận khí đứng yên 6s),
        # chỉ còn buff / hồi máu / triệu hồi... để "buff xong chạy". Trả về (False, False) để thử kỹ năng tiếp theo trong danh sách
        # Chỉ dùng Tự động tấn công: bỏ mọi kỹ năng thật (có vị trí kỹ năng: chiêu đánh, buff, triệu hồi...), chỉ còn "kill" và các bước
        # di chuyển / tiếp cận của phái (giữ cách đánh thường riêng từng phái, vd Đường Môn đi vòng vật cản). Thử mục kế tiếp trong danh sách
        if self._is_chidungtudongtancong and vitrikynang is not None and loaikynang.startswith("sudungkynang"):
            return False, False

        if self._yeucaugiukhoangcach and (loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynangphudau")
                                          or loaikynang.startswith("dichuyen") or vitrikynang in (VITRIKYNANG_LOIDONGCUUTHIEN, VITRIKYNANG_LOILONGQUYET)):
            return False, False

        if loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynanglendongdoi"):
            if khoangcach <= khoangcachyeucau:
                khoangcachthucteyeucau = khoangcachyeucau
                # Buff lên đồng đội (Tiểu Chu Thiên, Hộ Thể Kim Cang...) không cần bù khoảng cách: trong tầm là buff, không chạy lại gần
                # Chế độ đứng yên (_chontamxa) không bù: tầm đã học riêng khi đứng yên và tự nhích khi trượt
                if loaikynang != "sudungkynanglendongdoi" and not self._is_tamxadungyen \
                        and (thoigiandungim > 0.5 or (idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self._is_dangchaybukhoangcach)):
                    # Đứng im lâu / đang chạy bù thì tầm xa yêu cầu giảm BUKHOANGCACHTAMXA ô (cố định, không giảm mãi theo thời gian đứng).
                    # Tầm xa 9 ô đã trừ hao lệch tọa độ client - server (tầm thật ~12 ô) nên chỉ bù nhẹ, trước đây trừ 2-3 ô là trừ hao 2 lần
                    if khoangcachyeucau >= self._khoangcachsudungkynangtamxa:
                        khoangcachthucteyeucau = khoangcachthucteyeucau - BUKHOANGCACHTAMXA

                if khoangcach > khoangcachthucteyeucau:
                    self._is_dangchaybukhoangcach = True
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachimuctieu,
                        "khoangcachtoida": self._doikhoangcachtiepcan(diachimuctieu, max(0, khoangcachthucteyeucau - 1.))
                    }
                    return False, True
                else:
                    self._is_dangchaybukhoangcach = False
            else:
                self._is_dangchaybukhoangcach = False
                return False, False

        if thoidiemhientai - self.moitruong.thoidiembatchucnangmoronggannhat < 0.5 or thoidiemhientai - self.moitruong.thoidiemtatchucnangmoronggannhat < 0.5:
            return False, True

        if loaikynang == "dichuyendiembanthong":
            # Đường bắn bị vật cản chắn: đi tới ô gần nhất bắn thông được mà không lại gần mục tiêu (xem get_diembanthong); không có
            # ô nào thì (False, False) để mục kế (tiếp cận vòng qua vật cản) chạy
            if not diachimuctieu:
                return False, False
            diem = self.moitruong.get_diembanthong(*self.moitruong.get_toado(diachimuctieu), khoangcachyeucau)
            if not diem:
                return False, False
            self._yeucautancong = {
                "yeucau": YEUCAUDICHUYENTANCONG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                "diachimuctieu": diachimuctieu,
                "toadodich": diem,
                "khoangcachtoida": 0.,
            }
            return True, True

        if loaikynang in ("dichuyentiepcancanchien", "dichuyengiukhoangcach", "dichuyentiepcantamxa", "dichuyentiepcanbuff", "dichuyentiepcandenkhoangcach"):
            if loaikynang == "dichuyengiukhoangcach":
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                    "diachimuctieu": diachimuctieu,
                    "khoangcach": khoangcachyeucau
                }
            elif loaikynang in ("dichuyentiepcanbuff", "dichuyentiepcandenkhoangcach"):
                # Tiếp cận đồng đội để buff: buff không bù khoảng cách nên chỉ cần vào vừa trong tầm, không chạy sát.
                # Tiếp cận đến khoảng cách: chạy vào trong khoangcachyeucau (dư 1 ô) rồi dừng (vd Ngự Kiếm Phi Tiên vào giữa cụm quái)
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    "khoangcachtoida": self._doikhoangcachtiepcan(diachimuctieu, max(0, khoangcachyeucau - 1.)),
                }
            elif loaikynang == "dichuyentiepcantamxa" and self._is_tamxadungyen and diachimuctieu:
                # Chế độ đứng yên: chỉ đi vào vừa trong tầm (dư VUNGTIEPCANTAMXADUNGYEN ô) rồi bắn, không chạy sâu vào; giữ chế độ đứng yên lúc đi
                self._ghinhichtamxa(diachimuctieu, khoangcachyeucau, thoidiemhientai)
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    "khoangcachtoida": self._doikhoangcachtiepcan(diachimuctieu, max(0, khoangcachyeucau - VUNGTIEPCANTAMXADUNGYEN)),
                }
            else:
                # Ghi nhớ tầm thực sự đánh được (tầm xa trừ hao TRUHAOTAMXACHONMUCTIEU, xem hangso) để lọc mục tiêu quanh trưởng nhóm
                self._khoangcachvoitoimuctieu = KHOANGCACHSUDUNGKYNANGCANCHIEN if loaikynang == "dichuyentiepcancanchien" else max(KHOANGCACHSUDUNGKYNANGCANCHIEN, khoangcachyeucau - TRUHAOTAMXACHONMUCTIEU)
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    # Tầm xa chỉ cần chạy vào trong tầm đã bù (BUKHOANGCACHTAMXA) và dư 1 ô, không chạy sát mục tiêu
                    "khoangcachtoida": max(0, KHOANGCACHSUDUNGKYNANGCANCHIEN - 1.) if loaikynang == "dichuyentiepcancanchien" else self._doikhoangcachtiepcan(diachimuctieu, max(0, khoangcachyeucau - BUKHOANGCACHTAMXA - 1.)),
                }
            return True, True

        elif loaikynang == "battathieuungphapbao":
            self.moitruong.action_thucthicaulenh("pf2 908.6", douutien = DOUUTIEN_CAO)
            self._thoidiembattathieuungphapbaogannhat = thoidiemhientai

        elif loaikynang == "sudungcaoboctacdan":
            if diachimuctieu:
                iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN)
                if iddoituongvatpham:
                    if self.moitruong.get_is_nguoichoi(diachimuctieu):
                        caulenh = "use {}# for {}".format(hex(iddoituongvatpham).replace("0x", ""), self.moitruong.get_idnguoichoi(diachimuctieu))
                    else:
                        caulenh = "use {}# for {}#".format(hex(iddoituongvatpham).replace("0x", ""), hex(self.moitruong.get_iddoituong(diachimuctieu)).replace("0x", ""))
                    if self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO):
                        self._thoidiemsudungcaoboctacdangannhat = thoidiemhientai
        else:
            # "kill" chỉ bật tự động đánh thường: đã bật với đúng mục tiêu này thì THOIGIANGUILAITANCONGVATLY giây mới gửi lại.
            # Cờ tắt khi di chuyển (trừ Đào Hoa Nguyên) / bị choáng / đổi mục tiêu (xem các chỗ gán _is_battudongtancongvatly = False)
            if loaikynang == "tancongvatly" and self._is_battudongtancongvatly and self._diachimuctieutancongvatly == diachimuctieu \
                    and time.time() - self.moitruong._thoidiemsudungtancongvatlygannhat < THOIGIANGUILAITANCONGVATLY:
                return False, False

            # Đang xuất chiêu / khựng sau chiêu: không gửi chiêu nhắm mục tiêu ở ngoài KHOANGCACHCHIEUKHIXUATCHIEU. Mục tiêu ngoài tầm thật
            # của chiêu thì hết chiêu game tự chạy lại gần để ra chiêu (đo: bước về phía mục tiêu ngay khi hết chiêu) => mất tác dụng chiêu
            # đang khựng. Thử kỹ năng tiếp theo (chiêu không mục tiêu / lên bản thân vẫn dùng được)
            if loaikynang in ("tancongvatly", "sudungkynangmuctieu", "sudungkynanglendongdoi", "sudungkynangphudau") and diachimuctieu \
                    and khoangcach > KHOANGCACHCHIEUKHIXUATCHIEU and self.moitruong.get_is_dangxuatchieu():
                return False, False

            # Game đang bận với kỹ năng vừa gửi thì chờ, không gửi kỹ năng nào, kể cả chiêu khác: game cập nhật cờ sẵn sàng chậm, nếu mỗi
            # lượt lại gửi chiêu khác thì cắt ngang chiêu đang chuẩn bị ra. "kill" không xét: nó chỉ là lệnh nền bật đánh thường
            if loaikynang in ("sudungkynangkhongmuctieu", "sudungkynanglenbanthan", "sudungkynangmuctieu", "sudungkynanglendongdoi") \
                    and self._is_dangcholenhdanhtruoc(thoidiemhientai):
                return False, True

            # Chiêu tầm xa vừa trượt: làm mới toạ độ trước, chờ client nhận toạ độ thật rồi mới bắn
            if loaikynang == "sudungkynangmuctieu" and diachimuctieu and khoangcachyeucau >= self._khoangcachsudungkynangtamxa \
                    and self.moitruong.get_is_kynangsansang(vitrikynang) and self._is_cholammoitoado(thoidiemhientai):
                return False, True

            is_dasudung = True
            if loaikynang == "sudungkynangkhongmuctieu":
                is_dasudung = self.moitruong.action_sudungkynangvitri(vitrikynang)
            elif loaikynang == "sudungkynanglenbanthan":
                is_dasudung = self.moitruong.action_sudungkynangvitrilenbanthan(vitrikynang)
            elif loaikynang == "tancongvatly":
                is_dasudung = self.moitruong.action_sudungtancongvatly(diachimuctieu)
                if is_dasudung:
                    self._is_battudongtancongvatly = True
                    self._diachimuctieutancongvatly = diachimuctieu
            elif loaikynang == "sudungkynangmuctieu":
                # Sẵn sàng đọc trước khi gửi (sau khi gửi cờ có thể đã chuyển sang hồi): chiêu gửi lúc còn hồi thì máy chủ không nhận
                is_sansanglucgui = self.moitruong.get_is_kynangsansang(vitrikynang)
                is_dasudung = self.moitruong.action_sudungkynangvitrimuctieu(vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu)
                # Đo sát thương chiêu bằng số bay cho chế độ Tự học (đo ở cả chế độ Luật cố định)
                if is_dasudung:
                    self._ghichieututhoc(vitrikynang, diachimuctieu, is_sansanglucgui)
                # Chiêu dùng tầm xa gửi từ đủ xa: theo dõi xem có ra không để học tầm (_capnhattamxa)
                if is_dasudung and not self._chieuchonhantamxa and khoangcachyeucau >= self._khoangcachsudungkynangtamxa \
                        and khoangcach >= min(TAMXATOITHIEU, self._tamxatoida) - VUNGMEPTAMXA and self.moitruong.get_is_kynangsansang(vitrikynang):
                    self._chieuchonhantamxa = {"vitri": vitrikynang, "diachimuctieu": diachimuctieu, "idmuctieu": self.moitruong.get_iddoituong(diachimuctieu),
                                               "khoangcach": khoangcach, "thoidiem": thoidiemhientai, "is_dungyen": self._is_tamxadungyen,
                                               "toadominh": self.moitruong.get_toado(), "toadomuctieu": self.moitruong.get_toado(diachimuctieu),
                                               "buocminh": self.moitruong.get_toadobuoc(), "buocmuctieu": self.moitruong.get_toadobuoc(diachimuctieu),
                                               "is_muctieudi": self.moitruong.get_idtuthenhanvat(diachimuctieu) == TUTHENHANVAT_DICHUYEN}
            elif loaikynang == "sudungkynanglendongdoi":
                is_dasudung = self.moitruong.action_sudungkynangvitrimuctieu(vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu, is_khongkiemtracothetancong = True)
            elif loaikynang == "sudungkynangphudau":
                self.moitruong.action_sudungkynangvitriphudau(vitrikynang, None, diachimuctieu, khoangcachphudau = khoangcachyeucau)
            else:
                is_dasudung = False

            # Kỹ năng không gửi được (đang bị khoá chống spam / khoá kỹ năng, mục tiêu không đánh được...) thì để lượt này
            # thử kỹ năng tiếp theo trong danh sách. Trước đây vẫn dừng lượt: kỹ năng ưu tiên đầu bị khoá chống spam 3s
            # (vd Đại Hải Vô Lượng khi nhiều quái) làm nhân vật đứng cạnh quái 3s không đánh gì
            if not is_dasudung and loaikynang in ("sudungkynangkhongmuctieu", "sudungkynanglenbanthan", "sudungkynangmuctieu", "sudungkynanglendongdoi"):
                return False, False

            # "kill" là lệnh nền (không ra đòn ngay): không giữ hoạt ảnh / ghi nhận chiêu như kỹ năng
            if is_dasudung and loaikynang != "tancongvatly":
                self._thoidiemvohieuquadichuyennhatvatpham = max(self._thoidiemvohieuquadichuyennhatvatpham, thoidiemhientai + 0.5)
                # Giữ trọn hoạt ảnh xuất chiêu + khựng cho chiêu có một trong hai cờ (danh sách 6 phần tử như Thục Sơn chỉ có
                # is_yeucaukhongdichuyen); chiêu ra sát thương ngay (Đại Hải Vô Lượng, Ba Động Quyền) để cả hai False
                self.moitruong.set_is_chieucanngatdichuyen(is_ngatdichuyen or is_yeucaukhongdichuyen, diachimuctieu)
                self._ghinhanchieuguivaomuctieu(diachimuctieu)

            # Kỹ năng không mục tiêu thì không tạo yêu cầu di chuyển rỗng (chặn nhặt đồ/theo nhóm mà không đi đâu cả)
            if diachimuctieu:
                # Chiêu không mục tiêu / lên bản thân vẫn được gắn mục tiêu đang đánh (danh sách để None thì lấy diachimuctieu) nhưng không
                # cần lại gần nó: giữ nguyên khoảng cách đang đứng, đi lại gần hay không để chiêu đánh / bước tiếp cận phía sau quyết định.
                # Trước đây khoảng cách yêu cầu 0 => tiếp cận sát kiểu cận chiến, phái tầm xa buff xong lao vào quái (Đường Môn Mê Tâm Thuật)
                khoangcachtiepcan = max(khoangcachyeucau, khoangcach) if loaikynang in ("sudungkynangkhongmuctieu", "sudungkynanglenbanthan") \
                    else khoangcachyeucau
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    "khoangcachtoida": self._doikhoangcachtiepcan(diachimuctieu, khoangcachtiepcan)
                }

        # Luôn ngắt di chuyển rồi mới đánh: đánh lúc đang chạy thì máy chủ xử lý ở vị trí nó biết (client chạy trước ~1 ô) => client bị
        # kéo giật lùi, đòn hụt. action_ngatdichuyen nay chặn luôn client tự gửi "go" (đo: client có thể gửi thêm 1 bước đúng khung hình chiêu
        # bắt đầu -> hết chiêu bước 1 ô, chiêu mất tác dụng); vào tư thế xuất chiêu thì luồng nhanh ngắt tiếp (action_ngatdichuyenkhixuatchieu)
        if khoangcach <= khoangcachyeucau:
            if is_ngatdichuyen:
                self.moitruong.action_ngatdichuyen()
                self._thoidiemhetchongatdichuyen = thoidiemhientai + THOIGIANCHONGATDICHUYENXUATCHIEU
                self._thoidiemhetchantudichuyentruocxuatchieu = thoidiemhientai + THOIGIANCHANTUDICHUYENTRUOCXUATCHIEU

            if is_yeucaukhongdichuyen:
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, thoidiemhientai + 0.5)

        # "kill" không chiếm lượt: gửi xong vẫn thử kỹ năng tiếp theo trong danh sách ngay lượt này
        return True, loaikynang != "tancongvatly"

    def action_ngatdichuyenkhixuatchieu(self):
        # Đang xuất chiêu / khựng sau chiêu (moitruong.get_is_dangxuatchieu) mà nhân vật vẫn ở tư thế di chuyển thì ngắt ngay:
        # đích tìm đường đặt từ trước (tiếp cận, đi dạo) vẫn nằm trong game, hết tư thế xuất chiêu là game tự đi tiếp (đo: chuyển sang
        # tư thế 2 ngay 0.00s sau khi hết chiêu) dù bot đã chặn mọi lệnh di chuyển mới => mất tác dụng chiêu
        # Phải xoá NGAY TỪ LÚC ĐANG XUẤT CHIÊU, không chờ thấy tư thế di chuyển: đo được game bước đi đúng lúc hết tư thế xuất chiêu
        # (+0.00s, trước lượt kiểm tra đầu tiên của bot), dùng đích tìm đường / lệnh di chuyển đặt từ lúc tiếp cận còn nằm lại.
        # Game còn giữ "ô sắp tới" (bước dở, có khi đặt ngay trong lúc ra chiêu) thì cũng kéo về vị trí hiện tại
        # Người chơi đang giữ chuột kéo nhân vật đi: không chặn / xoá lệnh đi của người chơi, bỏ luôn các hạn chờ ngắt đang treo.
        # Đang đánh thường thì gửi "pf2 14" ngắt. Đào Hoa Nguyên máy chủ giữ "kill" cả khi chạy nên gửi tới khi máy chủ báo ngừng;
        # phái khác máy chủ tự tắt khi đi, chỉ gửi lúc còn tư thế xuất chiêu (pf2 14 bật / tắt qua lại: tới sau lệnh đi là bật lại)
        if self.moitruong.get_is_dangclickchuottrai():
            self._thoidiemhetchantudichuyentruocxuatchieu = 0.
            self._thoidiemhetchongatdichuyen = 0.
            if self._is_battudongtancongvatly and self._diachimuctieutancongvatly and (self.moitruong.get_tenmonphai() == "daohoanguyen"
                    or self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT)):
                self._ngattancongvatlydaohoa(self._diachimuctieutancongvatly)
            return
        if self.moitruong.get_is_dangxuatchieu():
            self._thoidiemhetchantudichuyentruocxuatchieu = 0.
            self.moitruong.action_chandichuyen()
            self.moitruong.action_ngatdichuyen()
            self.moitruong.action_huybuocdichuyen()
        elif self._thoidiemhetchantudichuyentruocxuatchieu:
            if time.time() > self._thoidiemhetchantudichuyentruocxuatchieu:
                self._thoidiemhetchantudichuyentruocxuatchieu = 0.
            else:
                self.moitruong.action_chandichuyen()
        # Đang tạm ngưng di chuyển cho kỹ năng is_yeucaukhongdichuyen: luồng nhanh ngắt liên tục (bộ di chuyển chỉ ngắt mỗi lượt loop chính)
        if time.time() < self._thoidiemtamngungdichuyensudungkynang:
            self.moitruong.action_ngatdichuyen()
        # Đang chờ ngắt di chuyển cho kỹ năng vừa gửi (action_xulyuutiensudungkynang): nhân vật đã vào tư thế xuất chiêu thì ngắt di chuyển
        if not self._thoidiemhetchongatdichuyen:
            return
        if time.time() > self._thoidiemhetchongatdichuyen:
            self._thoidiemhetchongatdichuyen = 0.
            return
        if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT):
            self._thoidiemhetchongatdichuyen = 0.
            self.moitruong.action_ngatdichuyen()

    def _logdichuyen(self, lydochon, yeucau):
        # Log nhẹ: chỉ ghi khi lý do hoặc điểm đích (làm tròn 1 ô) thay đổi
        if not IS_LOGDICHUYEN:
            return
        try:
            dich, muctieu = None, "-"
            if yeucau:
                if yeucau.get("toadodich"):
                    dich = tuple(round(v) for v in yeucau["toadodich"][:2])
                diachi = yeucau.get("diachimuctieu")
                if diachi:
                    toadomuctieu = self.moitruong.get_toado(diachi)
                    muctieu = f"{self.moitruong.get_tendoituong(diachi)} {toadomuctieu}"
                    dich = dich or toadomuctieu
            khoa = (lydochon, dich)
            if khoa == self._khoalogdichuyencuoi:
                return
            self._khoalogdichuyencuoi = khoa
            khoangcachtoida = yeucau.get("khoangcachtoida", yeucau.get("khoangcach")) if yeucau else None
            self.moitruong._inlog(f"[DI CHUYỂN] {lydochon} | mình {self.moitruong.get_toado()} tư thế {self.moitruong.get_idtuthenhanvat()} | "
                                  f"mục tiêu {muctieu} | đích {dich} giữ ≤{khoangcachtoida}")
        except Exception:
            pass

    def _is_dangcholenhdanhtruoc(self, thoidiemhientai):
        # Xem THOIGIANCHOPHANUNGLENH trong hangso_xq.py. Không chờ tư thế 6 / 9 (chỉ là hoạt ảnh): test lôi đài 2026-10-28 gửi chiêu kế
        # ngay trong tư thế 6 thì chiêu trước vẫn ra dame đủ, còn chờ hết tư thế làm chuỗi chậm (game nhận chiêu kế đúng lúc dame chiêu trước hiện)
        return thoidiemhientai - self.moitruong.get_thoidiemlenhdanhgannhat() < THOIGIANCHOPHANUNGLENH

    def action_sudungkynangmonphaiduongmon(self):
        if not self._is_tudongsudungkynang: return

        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        is_kynangamkichsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_AMKICH)
        if self._is_kynangamkichsansang and not is_kynangamkichsansang:
            self._thoidiemsudungamkichgannhat = time.time()
        self._is_kynangamkichsansang = is_kynangamkichsansang

        is_kynangthichsatsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_THICHSAT)
        if self._is_kynangthichsatsansang and not is_kynangthichsatsansang:
            self._thoidiemsudungthichsatgannhat = time.time()
        self._is_kynangthichsatsansang = is_kynangthichsatsansang

        is_kynangbisatsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_BISAT)
        if self._is_kynangbisatsansang and not is_kynangbisatsansang:
            self._thoidiemsudungbisatgannhat = time.time()
        self._is_kynangbisatsansang = is_kynangbisatsansang

        is_kynangmatamthuatsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_MATAMTHUAT)
        if self._is_kynangmatamthuatsansang and not is_kynangmatamthuatsansang:
            self._thoidiemsudungmatamthuatgannhat = time.time()
        self._is_kynangmatamthuatsansang = is_kynangmatamthuatsansang

        is_kynangnhiephonchamsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_NHIEPHONCHAM)
        if self._is_kynangnhiephonchamsansang and not is_kynangnhiephonchamsansang:
            self._thoidiemsudungnhiephonchamgannhat = time.time()
        self._is_kynangnhiephonchamsansang = is_kynangnhiephonchamsansang
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

        is_muctieusudungphapluc = diachimuctieu and self.moitruong.get_idloaivukhi(diachimuctieu) in (IDLOAIVUKHI_KIEM, IDLOAIVUKHI_AMKHI)
        is_muctieulabaothukynangtrieuhoi = self.moitruong.get_is_baothukynangtrieuhoi(diachimuctieu)
        is_muctieulabaothugiangho = self.moitruong.get_is_baothugiangho(diachimuctieu)
        is_muctieulanguoichoi = self.moitruong.get_is_nguoichoi(diachimuctieu)
        is_muctieugiukhoangcach = (is_muctieulanguoichoi and self.moitruong.get_idloaivukhi(diachimuctieu) not in (IDLOAIVUKHI_KIEM, IDLOAIVUKHI_AMKHI))  # or self._is_tudongdichuyendiemdanhxungquanh
        is_muctieupk = is_muctieulanguoichoi or is_muctieulabaothukynangtrieuhoi or is_muctieulabaothugiangho

        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu) if diachimuctieu else 0

        is_anthan = self.moitruong.get_is_nhanvatanthan()
        is_bituocvukhi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, is_hieuungcoloi = 0)
        is_bidaohoalacanh = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DAOHOALACANH,), macdinh = False, is_hieuungcoloi = 0)

        is_muctieucomatamthuat = False
        is_muctieutienthanvodich = False
        if diachimuctieu:
            is_muctieucomatamthuat = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MATAMTHUAT,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu)
            is_muctieutienthanvodich = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu)

        is_bandochientruong = self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG

        noilucconlai = self.moitruong.get_noilucconlai()
        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

        # Ám khí không bay qua vật cản: đoạn thẳng mình -> mục tiêu có ô vật cản thì không đánh thường / dùng chiêu / ném Tạc Đạn lên mục tiêu
        # được, phải đi vòng lại gần (tìm đường đi quanh vật cản, tới chỗ thông thì chiêu gửi và ngắt di chuyển). Chỉ xét khi trong tầm
        is_duongbanbichan = bool(diachimuctieu) and khoangcach <= self._khoangcachsudungkynangtamxa + BUKHOANGCACHTAMXA \
            and self.moitruong.get_is_doanthangcovatcan(*self.moitruong.get_toado(), *self.moitruong.get_toado(diachimuctieu))

        danhsachuutien = [
            (VITRIKYNANG_ANTHANTHUAT, "sudungkynangkhongmuctieu", lambda: not is_anthan and diachimuctieu and is_muctieutienthanvodich and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(VITRIKYNANG_BISAT), 0, None, False),
            (VITRIKYNANG_BISAT, "sudungkynangmuctieu", lambda: is_anthan and diachimuctieu and is_muctieutienthanvodich and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            # Chiêu không mục tiêu vẫn gắn mục tiêu đang đánh nên dùng xong tạo yêu cầu đi tới khoảng cách yêu cầu: để 0 là chạy sát quái
            # đánh cận chiến (Mê Tâm Thuật 3642 khi quái ngoài tầm => mọi lần "TIẾP CẬN CẬN CHIẾN ... giữ ≤0.0", 2026-11-03) => để tầm xa
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: not is_anthan and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHLUIGIUKHOANGCACH and time.time() - self._thoidiemsudungnhiephonchamgannhat < 1., self._khoangcachsudungkynangtamxa, None, False),
            (None, "dichuyengiukhoangcach", lambda: not is_bidaohoalacanh and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHLUIGIUKHOANGCACH and (time.time() - self._thoidiemsudungmatamthuatgannhat < 0.5 or time.time() - self._thoidiemsudungamkichgannhat < 0.5 or time.time() - self._thoidiemsudungthichsatgannhat < 0.5), khoangcach + 3., None, False),
            (VITRIKYNANG_LACTUYETVONGAN, "sudungkynangkhongmuctieu", lambda: not is_anthan and diachimuctieu and is_muctieupk and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACTUYETVONGAN,), True, is_hieuungcoloi = 1), self._khoangcachsudungkynangtamxa, None, False),
            # "kill" bật Tự Động Công Kích (đánh thường tầm xa) như Đào Hoa: gửi khi mục tiêu trong tầm xa, không chiếm lượt (chiêu vẫn gửi
            # ngay lượt này), không chặn di chuyển / chạy lại gần (tầm yêu cầu + BUKHOANGCACHTAMXA). Đang ẩn thân thì để Bí Sát mở đòn.
            # Đang chạy (lùi giữ khoảng cách) thì không gửi: máy chủ tắt đánh thường khi đi, dừng lại là cờ đã reset nên gửi lại ngay
            (None, "tancongvatly", lambda: not is_anthan and diachimuctieu and idtuthenhanvat != TUTHENHANVAT_DICHUYEN and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa + BUKHOANGCACHTAMXA, None, False),
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: not is_anthan and diachimuctieu and khoangcach > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, False),
            (VITRIKYNANG_NHIEPHONCHAM, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and is_muctieupk and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvat = diachimuctieu), self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and self._is_nhieumuctieugan5 and not is_muctieupk, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_SONGLONGDOATCHAU, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and (is_muctieupk or is_bandochientruong or self._is_tudongdichuyendiemdanhxungquanh) and not is_muctieucomatamthuat, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and self._is_nhieumuctieugan5 and is_muctieupk, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and is_muctieulanguoichoi and is_muctieusudungphapluc and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HAPTINHMACHAM,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_MAIHOACHAM, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_AMKICH, "sudungkynangmuctieu", lambda: not is_bidaohoalacanh and diachimuctieu and not is_muctieucomatamthuat and (is_muctieugiukhoangcach or is_bituocvukhi), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() != BANDO_TIVO and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 30. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), self._khoangcachsudungkynangtamxa, None, False),
            (VITRIKYNANG_THICHSAT, "sudungkynangmuctieu", lambda: not is_bidaohoalacanh and diachimuctieu and not is_muctieucomatamthuat and (is_muctieugiukhoangcach or is_bituocvukhi), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "dichuyengiukhoangcach", lambda: not is_bidaohoalacanh and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHLUIGIUKHOANGCACH, khoangcach + 3., None, False),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu, self._khoangcachsudungkynangtamxa, None, True),
            # Đường bắn bị vật cản chắn: đi ngang / lùi tới ô bắn thông gần nhất trong tầm (đã trừ bù tầm khi đứng im), không lao vào
            # giữa mình và mục tiêu (máu yếu). Không có ô nào thì mới đi lại gần mục tiêu (tìm đường vòng qua vật cản), đường thông thì
            # các chiêu phía trên dùng được (không dùng "dichuyentiepcancanchien": nó ghi tầm đánh cận chiến vào _khoangcachvoitoimuctieu)
            (None, "dichuyendiembanthong", lambda: not is_bidaohoalacanh and is_duongbanbichan, self._khoangcachsudungkynangtamxa - BUKHOANGCACHTAMXA, None, False),
            (None, "dichuyentiepcandenkhoangcach", lambda: not is_bidaohoalacanh and is_duongbanbichan, KHOANGCACHSUDUNGKYNANGCANCHIEN + 1., None, False),
            (None, "dichuyentiepcantamxa", lambda: not is_bidaohoalacanh and diachimuctieu and khoangcach > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, False),
        ]

        danhsachuutien = self._sapxepuutientuhoc(danhsachuutien, diachimuctieu)
        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen = item

            if callable(dieukien) and not dieukien():
                continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang):
                continue

            target = target if target else diachimuctieu
            if is_duongbanbichan and target == diachimuctieu and loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungcaoboctacdan"):
                continue

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen
            )
            if is_break:
                return

    def action_sudungkynangmonphaidaohoanguyen(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = self.moitruong.get_is_nguoichoi(diachimuctieu)
        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu) if diachimuctieu else 0

        diachidongdoicanbuff = None
        if not diachimuctieu and self.moitruong.get_is_dangnamtrongnhom():
            diachidongdoicanbuff = self._diachidoituongcanbuffhothekimcangdaohoanguyen

        is_anhhuongboimuctieutheosau = bool(self._laytoadomuctieutheosau())
        is_nhuongbuff = self._is_nhuongbuffdaohoanguyen()
        is_nietban = self.moitruong.is_nietban
        is_cancanchien = bool(diachimuctieu) and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN
        idloaivukhimuctieu = self.moitruong.get_idloaivukhi(diachimuctieu) if diachimuctieu and is_muctieulanguoichoi else None
        nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai() or 0
        if self._is_tudongbatnguyenkhiquynguyen:
            self._lammoinguyenkhiquynguyen()
        # Nhất Quyền (dame chính) đã hồi chiêu mà nguyên khí còn thấp: để dành cho nó, không lót chiêu delay 0 (delay 0 -> Nhất Quyền là
        # bước chậm nhất, 0.8-1.7s). Lạc Kích lặp lại / Ba Động cận chiến đã cần NGUYENKHITOITHIEUCHIEULOT nên luật này chặn Đại Hải
        is_nhatquyensansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_NHATQUYENBATSON)
        is_giunguyenkhinhatquyen = is_nhatquyensansang and nguyenkhiconlai <= NGUYENKHIGIUCHONHATQUYEN
        # Chiêu lót delay 0 (Lạc Kích lặp lại, Ba Động cận chiến): nguyên khí dư (NGUYENKHITOITHIEUCHIEULOT) thì dùng; hoặc Nhất Quyền còn
        # hồi lâu (THOIGIANHOICHIEUCONLAICHIEULOT) thì bước chờ delay 0 -> Nhất Quyền (0.8-1.7s) bị hồi chiêu che mất, dùng khi còn đủ
        # NGUYENKHITOITHIEUCHIEULOTKHIHOICHIEU
        thoigianconlaihoichieunhatquyen = self._get_thoigianconlaihoichieunhatquyen(is_nhatquyensansang)
        is_duoclotdelay0 = nguyenkhiconlai >= NGUYENKHITOITHIEUCHIEULOT or (
            thoigianconlaihoichieunhatquyen >= THOIGIANHOICHIEUCONLAICHIEULOT and nguyenkhiconlai >= NGUYENKHITOITHIEUCHIEULOTKHIHOICHIEU)

        def is_muctieucohieuung(*hieuungs):
            return self.moitruong.get_is_cohieuungs(hieuungs, macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu)

        # Thứ tự theo test lôi đài 2026-10-28: chiêu có delay (dame ra sau ~0.4s) đi trước, game nhận chiêu kế ngay lúc dame chiêu
        # trước hiện; chiêu delay 0 (Lạc Kích, Ba Động, Đại Hải, Đào Hoa Lạc Ảnh) để sau vì sau nó game khoá chiêu kế ~0.6-1s.
        # Chiêu kế bị game từ chối thì lượt sau gửi lại ngay (các chiêu đánh nằm trong IDKYNANGKHONGCHANSPAMs)
        # Mở chuỗi: Thốn Kình -> Phong Ma (đao / kiếm: Vân Mộng, phép) hoặc Không Thủ (vũ khí khác) -> Nhất Quyền -> Lạc Kích
        # (mục tiêu đã có Lạc Kích thì Ba Động: chậm + 40% rối loạn) -> Mê Tung -> Đào Hoa Lạc Ảnh; xoay vòng Nhất Quyền -> Thốn Kình
        # -> Lạc Kích / Ba Động. Đại Hải chỉ dùng khi nhiều mục tiêu (choáng 1s với 1 người không đáng 4 nguyên khí)
        danhsachuutien = [
            (VITRIKYNANG_TRANCOTHANUY, "sudungkynangkhongmuctieu", lambda: diachimuctieu and not is_nhuongbuff and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRANCOTHANUY,), True, is_hieuungcoloi = 1), 0, None, False, False),
            # Không tự bật tâm pháp (Dã Tính / Kim Cương): người chơi tự chọn (bỏ tự bật Dã Tính 2026-10-28).
            # Kim Chung Tráo: như Trấn Cổ, chỉ dùng khi có mục tiêu; game không cho dùng khi đang Dã Tính nên bỏ qua lúc đó
            (VITRIKYNANG_KIMTRUNGCHAO, "sudungkynangkhongmuctieu", lambda: diachimuctieu and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), True, is_hieuungcoloi = 1) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMTRUNGCHAO,), True, is_hieuungcoloi = 1), 0, None, False, False),
            # Hộ Thể Kim Cang: Niết Bàn sửa chỉ còn tác dụng 15s mà hồi 30s, không đáng dùng (người dùng dặn 2026-11-04) => chỉ dùng ở Aegis
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglenbanthan", lambda: not is_nietban and not is_nhuongbuff and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), True, is_hieuungcoloi = 1), 0, None, False, False),
            # Nguyên Khí Quy Nguyên: bật / làm mới theo tin server ở _lammoinguyenkhiquynguyen (gọi trước danh sách)
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglendongdoi", lambda: not is_nietban and diachidongdoicanbuff and not is_nhuongbuff, self._khoangcachsudungkynangtamxa, diachidongdoicanbuff, False, False),
            # "kill" chỉ bật Tự Động Công Kích lên mục tiêu (không phải kỹ năng): gửi được từ xa, máy chủ giữ lệnh cả khi di chuyển và chỉ
            # đánh khi đã ở gần. Đánh thường làm chiêu ra chậm hẳn nên chỉ bật khi gần hết nguyên khí (NGUYENKHITANCONGVATLYDAOHOA), còn
            # nguyên khí thì spam chiêu. Gửi 1 lần mỗi mục tiêu, THOIGIANGUILAITANCONGVATLY giây gửi lại cho chắc
            (None, "tancongvatly", lambda: diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa and (self._is_chidungtudongtancong or nguyenkhiconlai <= NGUYENKHITANCONGVATLYDAOHOA), self._khoangcachsudungkynangtamxa + BUKHOANGCACHTAMXA, None, False, False),
            (VITRIKYNANG_DAIHAIVOLUONG, "sudungkynangkhongmuctieu", lambda: is_cancanchien and self._is_nhieumuctieuganbanthan3 and not is_giunguyenkhinhatquyen, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, False),
            # Ba Động đánh tầm xa, dame ra ngay: mở đầu / đuổi khi mục tiêu còn ngoài tầm cận chiến
            (VITRIKYNANG_BADONGQUYEN, "sudungkynangmuctieu", lambda: diachimuctieu and not is_anhhuongboimuctieutheosau and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN and idtuthenhanvat == TUTHENHANVAT_DICHUYEN, self._khoangcachsudungkynangtamxa, None, False, False),
            (VITRIKYNANG_BADONGQUYEN, "sudungkynangmuctieu", lambda: diachimuctieu and is_anhhuongboimuctieutheosau and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN and idtuthenhanvat == TUTHENHANVAT_DICHUYEN and khoangcach < self._khoangcachsudungkynangtamxa - 3, self._khoangcachsudungkynangtamxa, None, False, False),
            (VITRIKYNANG_THONKINH, "sudungkynangmuctieu", lambda: is_cancanchien and not is_muctieucohieuung(HIEUUNGKYNANG_TRONGTHUONG), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True, HIEUUNGKYNANG_TRONGTHUONG),
            (VITRIKYNANG_PHONGMAQUYET, "sudungkynangmuctieu", lambda: is_cancanchien and is_muctieulanguoichoi and idloaivukhimuctieu in (IDLOAIVUKHI_DAO, IDLOAIVUKHI_KIEM) and not is_muctieucohieuung(HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True, HIEUUNGKYNANG_TRAMMAC),
            (VITRIKYNANG_KHONGTHUNHAPBACHNHAN, "sudungkynangmuctieu", lambda: is_cancanchien and is_muctieulanguoichoi and idloaivukhimuctieu not in (IDLOAIVUKHI_DAO, IDLOAIVUKHI_KIEM, IDLOAIVUKHI_TAYKHONG) and not is_muctieucohieuung(HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN, HIEUUNGKYNANG_CHOANG), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN),
            (VITRIKYNANG_NHATQUYENBATSON, "sudungkynangmuctieu", lambda: is_cancanchien, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            # Chiêu có delay còn lại trước (Thốn Kình lấp chỗ hồi chiêu 2s của Nhất Quyền khi mục tiêu đã có Trọng Thương, Mê Tung),
            # chiêu delay 0 sau cùng. Thốn Kình lấp chỗ chỉ khi nguyên khí dư (NGUYENKHITOITHIEUTHONKINHLAPCHO): nguyên khí thấp mà cứ đủ 2 là
            # Thốn Kình ăn mất thì không bao giờ tích đủ 4 cho Nhất Quyền
            (VITRIKYNANG_THONKINH, "sudungkynangmuctieu", lambda: is_cancanchien and nguyenkhiconlai >= NGUYENKHITOITHIEUTHONKINHLAPCHO, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_METUNGQUYEN, "sudungkynangmuctieu", lambda: is_cancanchien and is_muctieulanguoichoi and not is_muctieucohieuung(HIEUUNGKYNANG_ROILOAN, HIEUUNGKYNANG_CHOANG), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True, HIEUUNGKYNANG_ROILOAN),
            (VITRIKYNANG_LACKICH, "sudungkynangmuctieu", lambda: is_cancanchien and not is_muctieucohieuung(HIEUUNGKYNANG_LACKICH), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, False, HIEUUNGKYNANG_LACKICH),
            # Ba Động cận chiến / Lạc Kích lặp lại là chiêu lót: chỉ dùng khi không làm thiếu nguyên khí / chậm Nhất Quyền (is_duoclotdelay0)
            (VITRIKYNANG_BADONGQUYEN, "sudungkynangmuctieu", lambda: is_cancanchien and is_duoclotdelay0, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, False),
            (VITRIKYNANG_DAOHOALACANH, "sudungkynangkhongmuctieu", lambda: is_cancanchien and is_muctieulanguoichoi, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            # Lạc Kích đã có hiệu ứng vẫn ra dame ngay (chiêu lót, như Ba Động cận chiến)
            (VITRIKYNANG_LACKICH, "sudungkynangmuctieu", lambda: is_cancanchien and is_duoclotdelay0, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, False),
            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() not in (BANDO_TIVO, BANDO_CHIENTRUONG) and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 5. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), self._khoangcachsudungkynangtamxa, None, False, False),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False, False),
        ]

        # Nguyên khí đã hồi đủ (NGUYENKHINGATTANCONGVATLYDAOHOA) thì ngắt đánh thường để spam chiêu (không chặn lượt, chiêu vẫn gửi)
        # Chỉ dùng Tự động tấn công thì không ngắt (không còn chiêu nào để spam)
        if nguyenkhiconlai >= NGUYENKHINGATTANCONGVATLYDAOHOA and not self._is_chidungtudongtancong:
            self._ngattancongvatlydaohoa(diachimuctieu)

        danhsachuutien = self._sapxepuutientuhoc(danhsachuutien, diachimuctieu)
        for i, item in enumerate(danhsachuutien):
            # Phần tử thứ 8 (nếu có): hiệu ứng khống chế chiêu này gây ra, giữ chỗ giữa các bot để không cùng gửi lên 1 mục tiêu
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen, is_ngatdichuyen, *phu = item
            hieuunggiucho = phu[0] if phu else None

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang): continue

            target = target if target else diachimuctieu

            # Bot khác vừa gửi chiêu gây cùng hiệu ứng lên mục tiêu này (hiệu ứng chưa kịp hiện) thì dùng chiêu tiếp theo
            idmuctieugiucho = self._get_idmuctieugiucho(target) if hieuunggiucho and target else None
            if idmuctieugiucho and not self._thugiukynangmuctieu(hieuunggiucho, idmuctieugiucho): continue

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen,
                is_ngatdichuyen = is_ngatdichuyen
            )

            if idmuctieugiucho and not is_ok:
                self._bogiukynangmuctieu(hieuunggiucho, idmuctieugiucho)

            if is_break:
                return

    def _thugiuchokynangphai(self, khoaphai, vitrikynang, loaikynang, target):
        # Giữ chỗ chiêu lên mục tiêu giữa các bot cùng máy theo HIEUUNGGIUCHOKYNANG_MAP. Trả về (chỗ đã giữ hoặc None, có được gửi không):
        # bot khác vừa gửi cùng chiêu lên mục tiêu này thì không gửi (dùng chiêu tiếp theo). Gửi không thành thì gọi _bogiuchokynangphai
        hieuung = HIEUUNGGIUCHOKYNANG_MAP.get(khoaphai, {}).get(vitrikynang)
        if not hieuung or not target or loaikynang.startswith("dichuyen"):
            return None, True
        idmuctieu = self._get_idmuctieugiucho(target)
        if not idmuctieu:
            return None, True
        if not self._thugiukynangmuctieu(hieuung, idmuctieu):
            return None, False
        return [(hieuung, idmuctieu)], True

    def _bogiuchokynangphai(self, giucho):
        # giucho: danh sách (hiệu ứng, ID mục tiêu) đã giữ
        for hieuung, idmuctieu in giucho or ():
            self._bogiukynangmuctieu(hieuung, idmuctieu)

    def _thugiumenhte(self, idcanhois):
        # Mệnh Tế: giữ chỗ cho từng người cần hồi (bản thân / đồng đội, theo ID _get_idmuctieugiucho) quanh mình. Mọi người này đều
        # vừa được bot khác Mệnh Tế (THOIGIANGIUMENHTE giây) thì không dùng. Trả về (chỗ đã giữ, có được dùng không)
        giukynang = self.moitruong.giukynang
        idmuctieus = [i for i in idcanhois if i and i[1]]
        if not giukynang or not idmuctieus:
            return None, True
        try:
            trongs = giukynang.thugiumotphan([(KHOAGIUCHO_MENHTE, i) for i in idmuctieus], THOIGIANGIUMENHTE)
        except Exception:
            return None, True
        return trongs, bool(trongs)

    def _get_khoagiuchobichan(self):
        # Tập (hiệu ứng, ID mục tiêu) bot khác đang giữ / còn hiệu lực, cộng dấu hiệu lực bot này nhớ (khi chạy không có Manager)
        thoidiemhientai = time.time()
        khoas = {k for k, hethan in self._dauhieulucbuffs.items() if hethan > thoidiemhientai}
        giukynang = self.moitruong.giukynang
        if giukynang:
            try:
                khoas |= giukynang.laykhoabichan()
            except Exception:
                pass
        return khoas

    def _is_canbuffmaoson(self, diachi, hieuung, idmuctieu, khoabichan):
        # Mục tiêu nên buff hiệu ứng này: chưa dính (đang dính thì đánh dấu hiệu lực cho mọi bot), không bị bot khác giữ / còn hiệu lực
        if self.moitruong.get_is_cohieuungs((hieuung,), macdinh = False, diachicosothongtinnhanvat = diachi, is_hieuungcoloi = 0):
            self._danhdauhieulucbuff(hieuung, idmuctieu)
            return False
        return not idmuctieu or (hieuung, idmuctieu) not in khoabichan

    def _danhdauhieulucbuff(self, hieuung, idmuctieu):
        # Thấy hiệu ứng (THOIGIANHIEULUCBUFFMAOSON_MAP) đã dính trên mục tiêu: đánh dấu cho mọi bot không buff lại tới hết hiệu lực.
        # Nhớ thời điểm hết hạn ở _dauhieulucbuffs để khỏi hỏi Manager mỗi lượt quét
        thoigian = THOIGIANHIEULUCBUFFMAOSON_MAP.get(hieuung)
        if not thoigian or not idmuctieu:
            return
        khoa = (hieuung, idmuctieu)
        thoidiemhientai = time.time()
        if self._dauhieulucbuffs.get(khoa, 0) > thoidiemhientai:
            return
        hethan = thoidiemhientai + thoigian
        giukynang = self.moitruong.giukynang
        if giukynang:
            try:
                hethan = giukynang.danhdauhieuluc(hieuung, idmuctieu, thoigian)
            except Exception:
                pass
        if len(self._dauhieulucbuffs) > 200:
            self._dauhieulucbuffs = {k: v for k, v in self._dauhieulucbuffs.items() if v > thoidiemhientai}
        self._dauhieulucbuffs[khoa] = hethan
        if hethan > thoidiemhientai + 1.:
            print("{}: hiệu ứng {} đã dính trên {}, không buff lại trong {:.0f}s".format(
                self.moitruong.get_tendoituong(), hieuung, idmuctieu, hethan - thoidiemhientai))

    def _get_idmuctieugiucho(self, diachimuctieu):
        # ID máy chủ của mục tiêu (mọi cửa sổ game thấy giống nhau, khác địa chỉ bộ nhớ): người chơi theo ID người chơi, còn lại theo ID đối tượng
        if self.moitruong.get_is_nguoichoi(diachimuctieu):
            idnguoichoi = self.moitruong.get_idnguoichoi(diachimuctieu)
            return ("nguoichoi", idnguoichoi) if idnguoichoi else None
        iddoituong = self.moitruong.get_iddoituong(diachimuctieu)
        return ("doituong", iddoituong) if iddoituong else None

    def _thugiukynangmuctieu(self, hieuung, idmuctieu):
        giukynang = self.moitruong.giukynang
        if not giukynang:
            return True
        try:
            return giukynang.thugiu(hieuung, idmuctieu)
        except Exception:
            # Mất kết nối Manager (đang tắt chương trình) thì cứ gửi như khi chạy 1 bot
            return True

    def _bogiukynangmuctieu(self, hieuung, idmuctieu):
        giukynang = self.moitruong.giukynang
        if not giukynang:
            return
        try:
            giukynang.bogiu(hieuung, idmuctieu)
        except Exception:
            pass


    def _guikillcamvequan(self, diachimuctieu, khoangcach):
        # "kill" gửi riêng như Đào Hoa (không phải kỹ năng, không chiếm lượt): mục tiêu trong tầm xa là bật Tự Động Công Kích để đòn
        # đánh thường hồi nguyên khí (đo 2026-11-03: chỉ dùng chiêu thì nguyên khí luôn 0-3, đứng im 2-3s chờ hồi). Máy chủ tắt đánh
        # thường khi đi / sau chiêu nên đứng im quá THOIGIANDUNGIMGUILAIKILLCAMVEQUAN giây là gửi lại, tối đa 1 lần / THOIGIANCHOGUILAIKILLCAMVEQUAN giây
        if not diachimuctieu or khoangcach > self._khoangcachsudungkynangtamxa:
            return
        thoidiemhientai = time.time()
        if thoidiemhientai - self.moitruong._thoidiemsudungtancongvatlygannhat < THOIGIANCHOGUILAIKILLCAMVEQUAN:
            return
        if self._is_battudongtancongvatly and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM \
                and thoidiemhientai - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat() >= THOIGIANDUNGIMGUILAIKILLCAMVEQUAN:
            self._is_battudongtancongvatly = False
        self.action_xulyuutiensudungkynang(loaikynang = "tancongvatly", vitrikynang = None, diachimuctieu = diachimuctieu,
                                           khoangcachyeucau = self._khoangcachsudungkynangtamxa + BUKHOANGCACHTAMXA)

    def action_sudungkynangmonphaicamvequan(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai() or 0
        phantramsinhluc = self.moitruong.get_phantramsinhlucconlai()
        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu) if diachimuctieu else 0
        is_cancanchien = bool(diachimuctieu) and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN
        is_bandochientruong = self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG
        is_nguyenkhidu = nguyenkhiconlai >= NGUYENKHIDUCAMVEQUAN

        def is_muctieucohieuung(*hieuungs):
            return self.moitruong.get_is_cohieuungs(hieuungs, macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0)

        def is_duongthangthong():
            # Hai chiêu đánh từ xa (cùng gây choáng 2s): Phi Long Tầm Châu ném đạn (như Ba Động Quyền), Thiên Lý Tất Sát lướt vào.
            # Đường thẳng tới mục tiêu có vật cản thì không dùng, để bước tiếp cận đi vòng
            if not diachimuctieu or not KHOANGCACHSUDUNGKYNANGCANCHIEN < khoangcach <= self._khoangcachsudungkynangtamxa:
                return False
            return not self.moitruong.get_is_doanthangcovatcan(*self.moitruong.get_toado(), *self.moitruong.get_toado(diachimuctieu))

        def is_dangluanhoi():
            # Luân Hồi Vạn Chuyển hồi đầy nguyên khí và xoá hồi chiêu mọi kỹ năng: dùng khi cạn nguyên khí hoặc >= 2 chiêu hồi lâu đang hồi
            if not diachimuctieu or phantramsinhluc > PHANTRAMSINHLUCLUANHOIVANCHUYEN:
                return False
            if nguyenkhiconlai <= 3:
                return True
            chieuhoilau = (VITRIKYNANG_BADAONOLANG, VITRIKYNANG_LOIDINHKICH, VITRIKYNANG_THIENLYTATSAT, VITRIKYNANG_DAIHAICUONGDAO, VITRIKYNANG_SINHTUTHANLUC)
            return sum(1 for vitri in chieuhoilau if not self.moitruong.get_is_kynangsansang(vitri)) >= 2

        # Mô tả đọc 2026-11-03 (cấp 54, vũ khí thương, nguyên khí tối đa 12), thứ tự theo người dùng chốt:
        #  Mạnh nhất: Ba Đào Nộ Lãng (+25 bạo kích 100%, 4 NK hồi 20s) và Lôi Đình Kích (+30 đánh 2 lần)
        #  Ngũ Lôi Áp Đỉnh (+25, quái -40 Ngoại Kháng = phá giáp, 4 NK hồi 2s): luôn spam lên quái; người chơi thì tước vũ khí 5s
        #  Đánh từ xa chỉ có Phi Long Tầm Châu (ném đạn) và Thiên Lý Tất Sát (lướt vào), cả hai choáng 2s
        #  Sinh Tử Thần Lực (+30 Ngoại Công +60 Ngoại Kháng 9s, 4 NK hồi 70s) có độ trễ: bật trước rồi mới lướt vào
        #  Thiên Bồng Nhất Kích chỉ dùng với người chơi (tước vũ khí 8s); Chấn Thiên Nộ Hống không có sát thương: chỉ khi đông người chơi
        #  Giao Long Nhập Hải (+12% chính xác, 1 NK hồi 2s) là chiêu spam duy trì; Mãng Xà Xuất Động (+105, 1 NK hồi 1s) lót khi dư nguyên khí
        # Không dùng: Thiền Trị (phải vận khí), Ngạo Thiên Côn, Trường Giang Nộ Thủy, Mê Hồn Thức (hôn mê không sát thương).
        # Chiến trường giữ như cũ: Ngũ Lôi tước vũ khí, không dùng chiêu đánh khác
        danhsachuutien = [
            (VITRIKYNANG_MANHHOBOPHAP, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MANHHOBOPHAP,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_KIMSUBOGIAP, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMSUBOPHAP,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_LUANHOIVANCHUYEN, "sudungkynangkhongmuctieu", is_dangluanhoi, 0, None, True),
            (VITRIKYNANG_SINHTUTHANLUC, "sudungkynangkhongmuctieu", lambda: diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_SINHTUTHANLUC,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_THIENLYTATSAT, "sudungkynangmuctieu", is_duongthangthong, self._khoangcachsudungkynangtamxa, None, False),
            (VITRIKYNANG_PHILONGTAMCHAU, "sudungkynangmuctieu", is_duongthangthong, self._khoangcachsudungkynangtamxa, None, False),
            (VITRIKYNANG_CHANTHIENNOHONG, "sudungkynangkhongmuctieu", lambda: not is_bandochientruong and is_cancanchien and is_muctieulanguoichoi and self._is_nhieumuctieuganbanthan3, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_HOANHTAOTHIENQUAN, "sudungkynangkhongmuctieu", lambda: not is_bandochientruong and is_cancanchien and self._is_nhieumuctieuganbanthan3, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_NGULOIAPDINH, "sudungkynangmuctieu", lambda: is_bandochientruong and diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            # Quái chưa bị phá giáp thì Ngũ Lôi trước, rồi hai chiêu mạnh nhất, rồi spam Ngũ Lôi tiếp
            (VITRIKYNANG_NGULOIAPDINH, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien and not is_muctieulanguoichoi and not is_muctieucohieuung(HIEUUNGKYNANG_NGULOIAPDINH), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_BADAONOLANG, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_LOIDINHKICH, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_NGULOIAPDINH, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien and not is_muctieulanguoichoi, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_THIENLYTATSAT, "sudungkynangmuctieu", lambda: is_cancanchien, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_PHILONGTAMCHAU, "sudungkynangmuctieu", lambda: is_cancanchien, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_DAIHAICUONGDAO, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien and not is_muctieucohieuung(HIEUUNGKYNANG_CHOANG), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_TRUCDAOHOANGLONG, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien and not is_muctieucohieuung(HIEUUNGKYNANG_TRONGTHUONG), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_THIENBONGNHATKICH, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien and is_muctieulanguoichoi and not is_muctieucohieuung(HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_NGULOIAPDINH, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien and is_muctieulanguoichoi and not is_muctieucohieuung(HIEUUNGKYNANG_NGULOIAPDINH, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_GIAOLONGNHAPHAI, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_MANGXAXUATDONG, "sudungkynangmuctieu", lambda: not is_bandochientruong and is_cancanchien and is_nguyenkhidu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False),
        ]

        self._guikillcamvequan(diachimuctieu, khoangcach)

        danhsachuutien = self._sapxepuutientuhoc(danhsachuutien, diachimuctieu)
        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang): continue

            target = target if target else diachimuctieu

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen
            )
            if is_break:
                return

    def action_sudungkynangmonphaiconluan(self):
        # Côn Luân (phái phép, đánh tầm xa). Chiêu chưa học / chưa hồi / thiếu pháp lực thì _is_kynangdungduoc bỏ qua, danh sách đi tiếp
        # tới chiêu sau. Học thêm chiêu thì thêm dòng vào danh sách (id ở hangso_xq VITRIKYNANG_* Côn Luân)
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        # Đang vận khí Lôi Long Quyết: chờ hết, trừ khi mục tiêu đã ra khỏi tầm và quanh mình hết cụm quái (ngắt sớm, như Lôi Động Cửu Thiên)
        if self.moitruong.get_is_dangvankhi() and not self._is_ngatvankhiloidongcuuthien(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu) if diachimuctieu else 0
        tamxa = self._khoangcachsudungkynangtamxa
        is_muctieulanguoichoi = bool(diachimuctieu) and self.moitruong.get_is_nguoichoi(diachimuctieu)
        # Vừa lướt Đằng Vân Giá Vũ: máy chủ chưa nhận chiêu, không gửi (gửi là bị khoá chống spam 3s), đi bộ vào gần hơn để hết chờ là
        # mục tiêu chắc chắn trong tầm (kể cả khi nó chạy). Đang lùi giữ khoảng cách thì action_xulyuutiensudungkynang bỏ qua bước tiếp cận
        if time.time() < self._thoidiemhetkhoachieusauluot:
            if diachimuctieu and khoangcach > tamxa - KHOANGCACHGANTHEMSAULUOT:
                self.action_xulyuutiensudungkynang("dichuyentiepcandenkhoangcach", None, diachimuctieu, tamxa - KHOANGCACHGANTHEMSAULUOT + 1.)
            return
        # Bùa Giấy: đọc túi 1 lần mỗi lượt, chỉ khi có mục tiêu (chiêu đánh nào cũng tốn bùa trừ Phong Hỏa Quyết / Phong Ma Chú)
        sobuagiay = (self.moitruong.get_soluongvatphamhanhtrangtheoten() or {}).get(BUAGIAY, 0) if diachimuctieu else 0

        def muctieuco(hieuung):
            return self.moitruong.get_is_cohieuungs((hieuung,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0)

        # Không đánh thường: Côn Luân đánh thường chỉ 1-2 máu (người dùng bỏ 2026-10-29), hết pháp lực / chiêu đang hồi thì đứng chờ.
        # Chưa dùng: Biến Thân Thuật, Khốn Ma Thuật / Khốn Ma Trận (không tác dụng lên người chơi), Phá Chú (giải bùa cho đồng đội),
        # Long Du Tứ Hải (dịch chuyển theo ID người chơi)
        danhsachuutien = [
            # Tâm pháp bật / tắt: chỉ bấm khi chưa có hiệu ứng, gửi 1 lần rồi chờ hiệu ứng hiện (_is_duocguitamphapbattat gọi cuối).
            # Pháp lực dưới mức chuyển hóa ghi trong mô tả (cấp 4: 700) thì không bật (người dùng 2026-10-30)
            (VITRIKYNANG_CANKHONNADI, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CANKHONNADI,), macdinh = True, is_hieuungcoloi = 1)
                and self.moitruong.get_noilucconlai() >= self._laytieuhao(VITRIKYNANG_CANKHONNADI, "chuyển hóa")
                and self._is_duocguitamphapbattat(VITRIKYNANG_CANKHONNADI), 0, None, False),
            # Lôi Long Quyết (6 bùa, 9x9 ô quanh bản thân liên tục 6s, vận khí) như Lôi Động Cửu Thiên của Mao Sơn: cụm quái quanh mình và
            # mục tiêu trong 3 ô thì ra chiêu đứng yên; cụm quái quanh mục tiêu (đánh quái, không PK) thì chạy vào giữa cụm (cách ~2 ô) để
            # lượt sau trúng cả cụm (chỉ chạy khi chiêu đang dùng được)
            (VITRIKYNANG_LOILONGQUYET, "sudungkynangkhongmuctieu", lambda: diachimuctieu and sobuagiay >= 6 and self._somuctieuganbanthan3 >= SOLUONGQUAITOITHIEUCHIEUVANKHI
                and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, None, True),
            (VITRIKYNANG_LOILONGQUYET, "dichuyentiepcandenkhoangcach", lambda: diachimuctieu and sobuagiay >= 6 and not is_muctieulanguoichoi and self._somuctieugan3 >= SOLUONGQUAITOITHIEUCHIEUVANKHI
                and khoangcach > KHOANGCACHTIEPCANLOIDONGCUUTHIEN, KHOANGCACHTIEPCANLOIDONGCUUTHIEN, None, False),
            # Hàn Băng Trận (5 bùa, 7x7 ô quanh bản thân, Đóng Băng 6s): cụm quái quanh mình mà Lôi Long Quyết chưa dùng được
            (VITRIKYNANG_HANBANGTRAN, "sudungkynangkhongmuctieu", lambda: diachimuctieu and sobuagiay >= 5 and self._is_nhieumuctieuganbanthan3
                and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, None, True),
            # Kim Quang Trận (3 bùa, 5x5 ô quanh mục tiêu, +250 nội công): cụm quái quanh mục tiêu
            (VITRIKYNANG_KIMQUANGTRAN, "sudungkynangmuctieu", lambda: diachimuctieu and sobuagiay >= 3 and self._is_nhieumuctieugan3, tamxa, None, True),
            # PK: Phong Ma Chú (Trầm Mặc 6s, không tốn bùa) lên người chơi chưa bị Trầm Mặc
            (VITRIKYNANG_PHONGMACHU, "sudungkynangmuctieu", lambda: is_muctieulanguoichoi and not muctieuco(HIEUUNGKYNANG_TRAMMAC), tamxa, None, True),
            # Đánh 1 mục tiêu: Huyền Long Chân Khí (4 bùa, +100 nội công) mạnh nhất, rồi các chiêu gây hiệu ứng khi mục tiêu chưa dính
            (VITRIKYNANG_HUYENLONGCHANKHI, "sudungkynangmuctieu", lambda: diachimuctieu and sobuagiay >= 4, tamxa, None, True),
            # Hỏa Long Quyết (3 Bùa Giấy): gây Thiêu Đốt 12s, mục tiêu đang bị Thiêu Đốt thì để chiêu khác
            (VITRIKYNANG_HOALONGQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and sobuagiay >= 3 and not muctieuco(HIEUUNGKYNANG_THIEUDOT), tamxa, None, True),
            # Thương Long Quyết (3 bùa, Đóng Băng 6s) khi mục tiêu chưa bị Đóng Băng
            (VITRIKYNANG_THUONGLONGQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and sobuagiay >= 3 and not muctieuco(HIEUUNGKYNANG_DONGBANG), tamxa, None, True),
            # Combo duy trì: đánh qua lại Ngự Lôi Thuật / Hỏa Long Quyết (không xét Thiêu Đốt), chiêu dùng lâu hơn đi trước.
            # Bỏ Hàn Băng Thuật (người dùng 2026-10-30)
            *sorted([
                (VITRIKYNANG_NGULOITHUAT, "sudungkynangmuctieu", lambda: diachimuctieu and sobuagiay >= 1, tamxa, None, True),
                (VITRIKYNANG_HOALONGQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and sobuagiay >= 3, tamxa, None, True),
            ], key = lambda item: self.moitruong.get_thoidiemsudungkynangvitrigannhat(item[0], macdinh = 0.)),
            # Hết bùa / cả hai đang hồi: Phong Hỏa Quyết (không tốn bùa)
            (VITRIKYNANG_PHONGHOAQUYET, "sudungkynangmuctieu", lambda: diachimuctieu, tamxa, None, True),
            (None, "dichuyentiepcantamxa", lambda: diachimuctieu and khoangcach > tamxa, tamxa, None, False),
        ]

        danhsachuutien = self._sapxepuutientuhoc(danhsachuutien, diachimuctieu)
        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang): continue

            target = target if target else diachimuctieu

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen
            )
            if vitrikynang == VITRIKYNANG_LOILONGQUYET and loaikynang == "sudungkynangkhongmuctieu" and is_ok:
                # Như Lôi Động Cửu Thiên: chờ game vào vận khí, ghi mốc để biết lúc nào được ngắt sớm
                self.moitruong.action_chovankhi(vitrikynang)
                self._thoidiemsudungloidongcuuthiengannhat = time.time()
            if is_break:
                return

    def _get_kynangchophep(self):
        # None = không giới hạn; ngược lại là tập vị trí kỹ năng được phép dùng (xem KYNANGCHOPHEPTHEONHANVAT_MAP)
        kynangchopheps = KYNANGCHOPHEPTHEONHANVAT_MAP.get(self.moitruong.get_idnguoichoi())
        if kynangchopheps is None:
            tennhanvat = " ".join((self.moitruong.get_tendoituong() or "").split()).lower()
            kynangchopheps = KYNANGCHOPHEPTHEONHANVAT_MAP.get(tennhanvat)
        return set(kynangchopheps) if kynangchopheps is not None else None

    def _get_baothukynangtrieuhois(self):
        # [(tên viết thường, % sinh lực còn lại)] của bảo thú kỹ năng triệu hồi
        # Tên dạng "Thiên Binh ( chủ nhân ) (cấp 65)", bảo thú giang hồ thì không có ngoặc
        baothus = []
        for sothutu in range(1, 4):
            if not self.moitruong.get_iddoituongbaothu(sothutu):
                continue
            tendoituongbaothu = self.moitruong.get_tendoituongbaothu(sothutu) or ""
            if "(" in tendoituongbaothu and ")" in tendoituongbaothu:
                # Đọc hụt (False) thì coi như đầy máu, không tế nhầm
                phantramsinhluc = self.moitruong.get_phantramsinhlucconlaidoituongbaothukynangtrieuhoi(sothutu)
                baothus.append((tendoituongbaothu.lower(), phantramsinhluc if phantramsinhluc is not False else 100))
        return baothus

    def _get_idbaothukynangtrieuhois(self):
        # {số thứ tự ô bảo thú: id đối tượng} của bảo thú kỹ năng triệu hồi (tên có ngoặc như _get_baothukynangtrieuhois)
        idbaothus = {}
        for sothutu in range(1, 4):
            idbaothu = self.moitruong.get_iddoituongbaothu(sothutu)
            if idbaothu and "(" in (self.moitruong.get_tendoituongbaothu(sothutu) or ""):
                idbaothus[sothutu] = idbaothu
        return idbaothus

    def _get_tenbaothukynangtrieuhois(self):
        return [ten for ten, _ in self._get_baothukynangtrieuhois()]

    def _get_thanhviennhomgans(self, khoangcachtoida):
        # [(% sinh lực, khoảng cách, địa chỉ)] của thành viên nhóm (không tính bản thân) còn sống trong khoangcachtoida ô
        # Đào Hoa đang bật Dã Tính Cuồng Lực (tự đốt máu) chỉ tính khi dưới 25%, không thì coi như đầy máu
        if not self.moitruong.get_is_dangnamtrongnhom():
            return []
        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
        idnguoichoi = self.moitruong.get_idnguoichoi()
        thanhviens = []
        j = -1
        while True:
            j += 1
            addr = self.moitruong.get_diachicosothongtindoituongx(j)
            if not addr:
                return thanhviens
            if not self.moitruong.get_is_nhanvattontai(addr) or self.moitruong.get_is_nhanvatdachet(addr):
                continue
            id_nd = self.moitruong.get_idnguoichoi(addr)
            if id_nd not in idnguoichoithanhviennhoms or id_nd == idnguoichoi:
                continue
            khoangcach = self.moitruong.get_khoangcachtamdanh(addr)
            if khoangcach > khoangcachtoida:
                continue
            phantram = self.moitruong.get_phantramsinhlucconlai(addr)
            if phantram >= 25 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), macdinh = False, diachicosothongtinnhanvat = addr, is_hieuungcoloi = 1):
                phantram = 100
            thanhviens.append((phantram, khoangcach, addr))

    def _get_is_cobaothukynangtrieuhoi(self, tenbaothu = None):
        # tenbaothu: chỉ tính bảo thú triệu hồi có tên này (vd: THIENBINH)
        return any(tenbaothu is None or ten.startswith(tenbaothu.lower()) for ten in self._get_tenbaothukynangtrieuhois())

    def _laybotrangbi(self):
        # Bộ đồ đang mặc: {ô trang bị: (id vật phẩm, tên)} cho SOLUONGOTRANGBI ô từ VITRITRANGBIDAUTIEN
        ids = self.moitruong._docdanhsachidvatphamhanhtrang(VITRITRANGBIDAUTIEN + SOLUONGOTRANGBI)
        return {vitri: (ids[vitri], self.moitruong.get_tentrangbi(vitri) if ids[vitri] else "")
                for vitri in range(VITRITRANGBIDAUTIEN, VITRITRANGBIDAUTIEN + SOLUONGOTRANGBI)}

    def thietlap_baothutrieuhoimaoson(self, baothu):
        if baothu not in BAOTHUTRIEUHOIMAOSONs or baothu == self._baothutrieuhoimaoson:
            return
        self._baothutrieuhoimaoson = baothu
        print("{}: Mao Sơn gọi bảo thú triệu hồi: {}".format(self.moitruong.get_tendoituong(), baothu))
        phatam("Gọi bảo thú {}".format(baothu))

    def battat_doidokhitrieuhoi(self):
        self._is_doidokhitrieuhoi = not self._is_doidokhitrieuhoi
        if self._is_doidokhitrieuhoi:
            phatam("Bật đổi đồ khi triệu hồi bảo thú")
        else:
            phatam("Tắt đổi đồ khi triệu hồi bảo thú")

    def ghi_bodotrieuhoi(self):
        # Ghi đồ đang mặc ở VITRITRANGBIDOITRIEUHOIs làm bộ đồ triệu hồi: [{"vitri": ô trang bị, "ten", "id", "vantay"}].
        # Nhận lại món bằng id (mã máy chủ cấp, riêng từng món, cùng tên vẫn khác id); dấu vân tay mô tả để dự phòng khi id đổi.
        # Món chưa có mô tả (game xoá mô tả đồ đang mặc khi đổi đồ / đăng nhập lại) thì desc lần lượt từng món theo vị trí ô trang bị
        # (moitruong.truyvan_motavatphamhanhtrang), chờ tối đa 1s mỗi món; ghi log món nào có / không có mô tả
        ids = self.moitruong._docdanhsachidvatphamhanhtrang(VITRITRANGBIDAUTIEN + SOLUONGOTRANGBI)
        bodo = []
        for vitri in VITRITRANGBIDOITRIEUHOIs:
            if not ids[vitri]:
                continue
            is_cosan = bool(self.moitruong.get_motavatphamhanhtrangcosan(vitri))
            thoidiembatdau = time.time()
            mota = self.moitruong.get_motavatphamhanhtrang(vitri)
            ten = self.moitruong.get_tentrangbi(vitri)
            self.moitruong._inlog("[GHI BỘ ĐỒ] ô {} {}: {}".format(vitri, ten, "mô tả có sẵn" if is_cosan else (
                "desc -> có mô tả sau {:.2f}s".format(time.time() - thoidiembatdau) if mota else "desc -> KHÔNG có mô tả sau 1s")))
            bodo.append({"vitri": vitri, "ten": ten, "id": ids[vitri], "vantay": self.moitruong.get_vantayvatpham(mota)})
        self._bodotrieuhoi = bodo
        print("{}: ghi bộ đồ triệu hồi: {}".format(self.moitruong.get_tendoituong(), ", ".join(mon["ten"] for mon in bodo) or "(trống)"))
        phatam("Đã ghi bộ đồ triệu hồi {} món".format(len(bodo)))

    def _timvatphambodotrieuhoi(self, mon, is_chonapsan = False):
        # id món của bộ đồ triệu hồi đang nằm trong hành trang (ô đang mở), không có thì 0: đúng id đã ghi trước,
        # không thấy id (id đổi) thì món cùng tên có dấu vân tay mô tả khớp. is_chonapsan: chỉ dùng mô tả có sẵn, không hỏi desc
        vitrimos = self.moitruong.get_danhsachvitrimohanhtrang()
        tens = self.moitruong._docdanhsachtenvatphamhanhtrang(vitrimos[-1] + 1)
        ids = self.moitruong._docdanhsachidvatphamhanhtrang(vitrimos[-1] + 1)
        if mon.get("id") and any(ids[vitri] == mon["id"] for vitri in vitrimos):
            return mon["id"]
        if not mon.get("vantay"):
            return 0
        for vitri in vitrimos:
            if not ids[vitri] or tens[vitri] != mon["ten"]:
                continue
            mota = self.moitruong.get_motavatphamhanhtrangcosan(vitri) if is_chonapsan else self.moitruong.get_motavatphamhanhtrang(vitri)
            if mota and self.moitruong.get_vantayvatpham(mota) == mon["vantay"]:
                return ids[vitri]
        return 0

    def action_doidokhitrieuhoi(self, giancachdeo = 0.15, giancachmaclai = 0.4, solanmaclaitoida = 15):
        # Mao Sơn bật _is_doidokhitrieuhoi: trong lúc vận khí gọi bảo thú triệu hồi (khoá vận khí triệu hồi) ghi lại bộ đồ đang mặc,
        # rồi đeo bộ đồ triệu hồi đã ghi (ghi_bodotrieuhoi, thường là đồ tấn công), tìm từng món trong hành trang theo dấu vân tay mô tả.
        # Dùng / đeo vật phẩm không ngắt vận khí. Vận khí xong thì ô trang bị nào khác lúc ghi lại sẽ mặc lại đúng món cũ (theo id)
        if self.moitruong.get_is_khoavankhitrieuhoibaothu():
            if self._bodotruoctrieuhoi is None:
                if self.moitruong.get_tenmonphai() != "maoson" or not self._is_doidokhitrieuhoi or not self._bodotrieuhoi:
                    return
                self._bodotruoctrieuhoi = self._laybotrangbi()
                self._solanmaclaitrieuhoi = 0
                self._idbaothutruoctrieuhoi = set(self._get_idbaothukynangtrieuhois().values())
                self._thoidiemhetvankhitrieuhoi = 0.
                self._is_dathaybaothutrieuhoi = False
                hangdoi = []
                for mon in self._bodotrieuhoi:
                    # Đang mặc đúng món đó rồi (cùng id, hoặc cùng dấu vân tay nếu có mô tả) thì thôi
                    idmac = self._bodotruoctrieuhoi.get(mon["vitri"], (0, ""))[0]
                    if idmac and (idmac == mon.get("id") or (mon.get("vantay") and self.moitruong.get_vantayvatpham(
                            self.moitruong.get_motavatphamhanhtrangcosan(mon["vitri"])) == mon["vantay"])):
                        continue
                    idvatpham = self._timvatphambodotrieuhoi(mon)
                    if idvatpham:
                        hangdoi.append((idvatpham, mon["ten"]))
                    else:
                        print("{}: không thấy {} (đúng mô tả đã ghi) trong hành trang".format(self.moitruong.get_tendoituong(), mon["ten"]))
                self._hangdoideodotrieuhoi = hangdoi
                if hangdoi:
                    print("{}: vận khí triệu hồi, đeo: {}".format(self.moitruong.get_tendoituong(), ", ".join(ten for _, ten in hangdoi)))
            if self._hangdoideodotrieuhoi and time.time() - self._thoidiemdoidotrieuhoigannhat >= giancachdeo:
                idvatpham, _ = self._hangdoideodotrieuhoi.pop(0)
                self.moitruong.action_sudungvatpham(idvatpham, delay = 0.)
                self._thoidiemdoidotrieuhoigannhat = time.time()
            return

        if self._bodotruoctrieuhoi is None:
            self._napmotadotrieuhoi()
            return
        if self.moitruong.get_is_dangvankhi() or self.moitruong.get_is_nhanvatdachet():
            return
        # Chỉ mặc lại khi đã thấy bảo thú triệu hồi mới (id chưa có lúc bắt đầu vận khí, đang trong tầm nhìn): đồ triệu hồi
        # ảnh hưởng chỉ số bảo thú lúc gọi ra. Quá THOIGIANCHOBAOTHUSAUTRIEUHOI giây không thấy (hỏng / bị ngắt) thì vẫn mặc lại
        if not self._is_dathaybaothutrieuhoi:
            if not self._thoidiemhetvankhitrieuhoi:
                self._thoidiemhetvankhitrieuhoi = time.time()
            idmois = [(sothutu, idbaothu) for sothutu, idbaothu in self._get_idbaothukynangtrieuhois().items()
                      if idbaothu not in self._idbaothutruoctrieuhoi]
            if any(self.moitruong._get_diachidoituongbaothu(sothutu) for sothutu, _ in idmois):
                self._is_dathaybaothutrieuhoi = True
                self.moitruong._inlog("[ĐỔI ĐỒ TRIỆU HỒI] thấy bảo thú mới sau {:.2f}s, mặc lại".format(time.time() - self._thoidiemhetvankhitrieuhoi))
            elif time.time() - self._thoidiemhetvankhitrieuhoi < THOIGIANCHOBAOTHUSAUTRIEUHOI:
                return
            else:
                self._is_dathaybaothutrieuhoi = True
                print("{}: không thấy bảo thú triệu hồi ra sau {:.0f}s, vẫn mặc lại".format(self.moitruong.get_tendoituong(), THOIGIANCHOBAOTHUSAUTRIEUHOI))
        if time.time() - self._thoidiemdoidotrieuhoigannhat < giancachmaclai:
            return
        self._hangdoideodotrieuhoi = []
        hientai = self._laybotrangbi()
        # Ô trang bị đang mặc món khác lúc trước triệu hồi (trước đó trống thì không tháo được, bỏ qua)
        khacs = [(vitri, idcu, tencu) for vitri, (idcu, tencu) in self._bodotruoctrieuhoi.items() if idcu and hientai[vitri][0] != idcu]
        if not khacs or self._solanmaclaitrieuhoi >= solanmaclaitoida:
            if khacs:
                print("{}: không mặc lại được sau triệu hồi: {}".format(self.moitruong.get_tendoituong(), ", ".join(ten for _, _, ten in khacs)))
                canhbao(self.moitruong, "Không mặc lại được đồ sau triệu hồi")
            elif self._solanmaclaitrieuhoi:
                print("{}: đã mặc lại bộ đồ trước triệu hồi".format(self.moitruong.get_tendoituong()))
            self._bodotruoctrieuhoi = None
            return
        vitri, idcu, tencu = khacs[0]
        self.moitruong.action_sudungvatpham(idcu, delay = 0.)
        self._thoidiemdoidotrieuhoigannhat = time.time()
        self._solanmaclaitrieuhoi += 1

    def _napmotadotrieuhoi(self, giancach = 2.):
        # Lúc rảnh (tối đa 1 lệnh desc mỗi giancach giây, mỗi lệnh chờ 0.2s):
        #   - món của bộ đồ chưa có dấu vân tay: lấy từ mô tả có sẵn, chưa có thì desc (đồ đang mặc desc theo vị trí ô trang bị)
        #   - món không còn thấy id ở đâu (id đổi): nạp mô tả các món cùng tên trong hành trang để lúc vận khí dò bằng dấu vân tay ngay
        if self.moitruong.get_tenmonphai() != "maoson" or not self._is_doidokhitrieuhoi or not self._bodotrieuhoi:
            return
        # desc không ngắt vận khí: vẫn nạp được lúc đang vận khí
        if time.time() - self._thoidiemnapmotadotrieuhoi < giancach:
            return
        self._thoidiemnapmotadotrieuhoi = time.time()
        vitrimos = self.moitruong.get_danhsachvitrimohanhtrang()
        tens = self.moitruong._docdanhsachtenvatphamhanhtrang(VITRITRANGBIDAUTIEN + SOLUONGOTRANGBI)
        ids = self.moitruong._docdanhsachidvatphamhanhtrang(VITRITRANGBIDAUTIEN + SOLUONGOTRANGBI)
        vitritheoid = {ids[vitri]: vitri for vitri in vitrimos + list(VITRITRANGBIDOITRIEUHOIs) if ids[vitri]}
        for mon in self._bodotrieuhoi:
            vitri = vitritheoid.get(mon.get("id"))
            if vitri is None:
                for vitricungten in vitrimos:
                    if mon.get("vantay") and ids[vitricungten] and tens[vitricungten] == mon["ten"] \
                            and ids[vitricungten] not in self._idnapmotathatbais and not self.moitruong.get_motavatphamhanhtrangcosan(vitricungten):
                        if not self.moitruong.get_motavatphamhanhtrang(vitricungten):
                            self._idnapmotathatbais.add(ids[vitricungten])
                        return
                continue
            if mon.get("vantay") or mon["id"] in self._idnapmotathatbais:
                continue
            mota = self.moitruong.get_motavatphamhanhtrangcosan(vitri)
            if not mota:
                mota = self.moitruong.get_motavatphamhanhtrang(vitri)
                if mota:
                    mon["vantay"] = self.moitruong.get_vantayvatpham(mota)
                else:
                    # desc 1 lần không ra mô tả thì thôi không hỏi lại món này (tránh gửi desc lặp mãi)
                    self._idnapmotathatbais.add(mon["id"])
                return
            mon["vantay"] = self.moitruong.get_vantayvatpham(mota)

    def _khoavankhitrieuhoi(self, vitrikynang):
        # Lệnh triệu hồi vừa vào hàng đợi là "pf <id kỹ năng>" (action_sudungkynang): vẫn cho gửi, các lệnh chiêu / đánh khác
        # và di chuyển bị chặn tới khi vận khí xong (xem moitruong._is_lenhbichankhoavankhi)
        idkynang = self.moitruong.get_idkynang(vitrikynang)
        self.moitruong.action_khoavankhitrieuhoi(caulenhduocpheps = ("pf {}".format(idkynang),) if idkynang else (), vitrikynang = vitrikynang)
        self._yeucautancong = None
        self._is_giuyeucautancongcu = False

    def _laytieuhao(self, makynang, loai):
        # Tiêu hao loai ("pháp lực", "khí huyết", "nguyên khí") của kỹ năng theo mô tả trong game; mã vị trí (x, y) hoặc chưa đọc được mô tả thì 0
        if not isinstance(makynang, int):
            return 0
        tieuhao = self.moitruong.get_tieuhaokynang(makynang)
        return tieuhao.get(loai, 0) if tieuhao else 0

    def _is_dutieuhao(self, makynang):
        # Đủ pháp lực / khí huyết / nguyên khí cho kỹ năng theo mô tả trong game. Khí huyết phải còn hơn tiêu hao (đổi hết máu là chết).
        # Chưa đọc được mô tả thì cho dùng (get_tieuhaokynang đã gửi "desc pf" để lần sau có), game không đủ thì tự từ chối
        if not isinstance(makynang, int):
            return True
        tieuhao = self.moitruong.get_tieuhaokynang(makynang)
        if not tieuhao:
            return True
        if tieuhao.get("pháp lực", 0) > self.moitruong.get_noilucconlai():
            return False
        if tieuhao.get("khí huyết", 0) and tieuhao["khí huyết"] >= self.moitruong.get_sinhlucconlai():
            return False
        if tieuhao.get("nguyên khí", 0) > self.moitruong.get_nguyenkhiconlai():
            return False
        return True

    def _is_kynangdungduoc(self, makynang):
        # Bị choáng / Trầm Mặc (phái phép thuật) thì bỏ qua chiêu, danh sách ưu tiên đi tiếp tới đánh thường / di chuyển
        return not self.moitruong.get_is_khongthedungkynang() and self.moitruong.get_is_kynangsansang(makynang) and self._is_dutieuhao(makynang)

    def _is_ngatvankhiloidongcuuthien(self):
        # Đang vận khí Lôi Động Cửu Thiên (Mao Sơn) / Lôi Long Quyết (Côn Luân, cùng cơ chế) (vào vận khí 0-1s sau khi ra chiêu, kéo dài
        # 6s) mà mục tiêu đã ra ngoài phạm vi và quanh bản thân không còn cụm quái nào thì ngắt luôn (cho di chuyển / dùng chiêu khác),
        # không chờ hết vận khí. Gọi khi game đang báo vận khí; trả về True thì coi như không vận khí
        if self.moitruong.get_tenmonphai() not in ("maoson", "conluan"):
            return False
        # Đang vận khí triệu hồi bảo thú thì tuyệt đối không ngắt
        if self.moitruong.get_is_khoavankhitrieuhoi():
            return False
        if time.time() - self._thoidiemsudungloidongcuuthiengannhat > THOIGIANVANKHILOIDONGCUUTHIEN + 1.5:
            return False
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachimuctieu or self.moitruong.get_khoangcachtamdanh(diachimuctieu) <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN + 0.5:
            return False
        if self._is_nhieumuctieuganbanthan3:
            return False
        self.moitruong.action_huychovankhi()
        return True

    def action_sudungkynangmonphaimaoson(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi() and not self._is_ngatvankhiloidongcuuthien(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu) if diachimuctieu else 0

        noilucconlai = self.moitruong.get_noilucconlai()
        phantramnoilucconlai = self.moitruong.get_phantramnoilucconlai()
        phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()

        diachithuccot = self._diachidoituongcanbuffthuccotmaoson
        diachithucgiap = self._diachidoituongcanbuffthucgiapmaoson
        diachithuctam = self._diachidoituongcanbuffthuctammaoson
        diachiammanhapthe = self._diachidoituongcanbuffammanhapthemaoson

        idbandohientai = self.moitruong.get_idbandohientai()

        baothukynangtrieuhois = self._get_baothukynangtrieuhois()
        is_cobaothukynangtrieuhoi = bool(baothukynangtrieuhois)
        is_cobaothusaphet = any(phantram < PHANTRAMSINHLUCTETHANTUONG for _, phantram in baothukynangtrieuhois)
        # Mệnh Tế / Huyết Tế: người cần hồi dưới nguongmoi% máu thì tế mọi bảo thú triệu hồi,
        # dưới nguongthuong% máu thì chỉ tế khi bảo thú triệu hồi không phải Cương Thi / Thần Tướng
        # (Lăng Ly Sơn / Thành Kiều tế sớm hơn, xem PHANTRAMSINHLUCTEBAOTHU_LANGLYSON)
        is_khongphaicuongthithantuong = is_cobaothukynangtrieuhoi and all(
            not ten.startswith((CUONGTHI.lower(), THANTUONG.lower())) for ten, _ in baothukynangtrieuhois)
        nguongmoi, nguongthuong = PHANTRAMSINHLUCTEBAOTHU_LANGLYSON if idbandohientai in BANDOTEBAOTHUSOMs else PHANTRAMSINHLUCTEBAOTHU
        is_cantebaothu = lambda phantram: is_cobaothukynangtrieuhoi and (phantram < nguongmoi or (phantram < nguongthuong and is_khongphaicuongthithantuong))
        # Mệnh Tế hồi cả nhóm nên xét cả máu đồng đội: chỉ dùng khi đồng đội trong KHOANGCACHSUDUNGMENHTE ô (xa hơn thì thực tế không được hồi),
        # đồng đội cần hồi ở xa hơn (tới KHOANGCACHTIMTHANHVIENMENHTE ô) thì tiếp cận người thấp máu nhất trong số đó trước
        thanhviennhoms = self._get_thanhviennhomgans(KHOANGCACHTIMTHANHVIENMENHTE) if is_cobaothukynangtrieuhoi else []
        thanhviennhomgans = [tv for tv in thanhviennhoms if tv[1] <= KHOANGCACHSUDUNGMENHTE]
        is_cothanhviennhomgan = bool(thanhviennhomgans)
        phantramthanhviennhomgan = min(tv[0] for tv in thanhviennhomgans) if thanhviennhomgans else 100
        thanhviennhomxacantes = [tv for tv in thanhviennhoms if tv[1] > KHOANGCACHSUDUNGMENHTE and is_cantebaothu(tv[0])]
        diachithanhviennhomxacante = min(thanhviennhomxacantes, key = lambda tv: tv[0])[2] if thanhviennhomxacantes else None
        kynangchopheps = self._get_kynangchophep()
        # Bật xoay vòng chiêu có mục tiêu, mục tiêu là quái: bỏ Phục Ma Quyết (phải chờ lượt), đánh bằng Lôi Động Cửu Thiên (không mục tiêu,
        # không chờ lượt) dù chỉ 1 mục tiêu, xa quá thì chạy lại gần (không xét ngưỡng SOLUONGQUAITOITHIEUCHIEUVANKHI, người dùng 2026-11-04).
        # Mục tiêu là người chơi (PK) thì không chạy vào sát, vẫn dùng Phục Ma Quyết
        is_xoayvongchieu = self.moitruong.get_is_batxoayvongchieu() and not is_muctieulanguoichoi

        danhsachuutien = [
            (VITRIKYNANG_THUCCOT, "sudungkynangmuctieu", lambda: diachithuccot, self._khoangcachsudungkynangtamxa, diachithuccot, True, True),
            # Bảo thú triệu hồi sắp chết (dưới PHANTRAMSINHLUCTETHANTUONG% sinh lực) thì Tế Thần Tướng (120 pháp lực, hồi 180s): hy sinh nó để gọi Thần Tướng
            # Tế Thần Tướng chỉ có từ cấp CAPDOTOITHIEUTETHANTUONG: cấp thấp chưa học mà game vẫn báo ô kỹ năng sẵn sàng nên bị spam liên tục
            (VITRIKYNANG_TETHANTUONG, "sudungkynangkhongmuctieu", lambda: is_cobaothusaphet and self.moitruong.get_capdonhanvat() >= CAPDOTOITHIEUTETHANTUONG, 0, None, True, True),
            # Máu thấp (xem is_cantebaothu) thì tế khí huyết bảo thú:
            #   có thành viên nhóm trong KHOANGCACHSUDUNGMENHTE ô thì Mệnh Tế (150 pháp lực: 25% khí huyết bảo thú hồi cho cả nhóm), xét bản thân hoặc thành viên đó thấp máu
            #   đồng đội cần hồi ở xa hơn thì tiếp cận tới KHOANGCACHSUDUNGMENHTE ô (Mệnh Tế sẵn sàng mới đi)
            #   không thì Huyết Tế (100 pháp lực: hy sinh 50% khí huyết bảo thú hồi cho bản thân)
            (VITRIKYNANG_MENHTE, "sudungkynangkhongmuctieu", lambda: is_cothanhviennhomgan and is_cantebaothu(min(phantramsinhlucconlai, phantramthanhviennhomgan)), 0, None, True, True),
            (VITRIKYNANG_MENHTE, "dichuyentiepcandenkhoangcach", lambda: diachithanhviennhomxacante, KHOANGCACHSUDUNGMENHTE, diachithanhviennhomxacante, False, False),
            (VITRIKYNANG_HUYETTE, "sudungkynangkhongmuctieu", lambda: not is_cothanhviennhomgan and is_cantebaothu(phantramsinhlucconlai), 0, None, True, True),
            # Chưa có bảo thú triệu hồi thì gọi bảo thú theo lựa chọn _baothutrieuhoimaoson (khoá vận khí triệu hồi đã chặn gọi lại tới khi vận khí xong)
            #   Tự động: có Cương Thi Phù trong hành trang thì ưu tiên gọi Cương Thi,
            #   không thì gọi Thiên Binh (3 Bùa Giấy). Pháp lực / khí huyết / nguyên khí đủ hay chưa thì _is_kynangdungduoc xét theo mô tả trong game
            (VITRIKYNANG_TRIEUHOICUONGTHI, "sudungkynangkhongmuctieu", lambda: self._baothutrieuhoimaoson in (BAOTHUTRIEUHOI_TUDONG, CUONGTHI) and not is_cobaothukynangtrieuhoi and self.moitruong.action_timkiemvatphamhanhtrang(CUONGTHIPHU), 0, None, True, True),
            (VITRIKYNANG_TRIEUHOITHIENBINH, "sudungkynangkhongmuctieu", lambda: self._baothutrieuhoimaoson in (BAOTHUTRIEUHOI_TUDONG, THIENBINH) and not is_cobaothukynangtrieuhoi and self.moitruong.action_timkiemvatphamhanhtrang(BUAGIAY), 0, None, True, True),
            # Quỷ Tốt cũng chỉ cần Bùa Giấy
            (VITRIKYNANG_TRIEUHOIQUYTOT, "sudungkynangkhongmuctieu", lambda: self._baothutrieuhoimaoson == QUYTOT and not is_cobaothukynangtrieuhoi and self.moitruong.action_timkiemvatphamhanhtrang(BUAGIAY), 0, None, True, True),
            (VITRIKYNANG_HUYETMACHU, "sudungkynangkhongmuctieu", lambda: phantramsinhlucconlai > 25 and phantramnoilucconlai <= 50, 0, None, True, False),
            (VITRIKYNANG_LUUHUYETTHUAT, "sudungkynangkhongmuctieu", lambda: time.time() - self._thoidiemsudungluuhuyetthuatgannhat > GIANCACHLUUHUYETTHUAT and self._is_baothukynangtrieuhoihetsinhluc, 0, None, True, True),

            (VITRIKYNANG_THANTUEPHAPCHU, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THANTUEPHAPCHU,), macdinh = True, is_hieuungcoloi = 1), 0, None, True, False),

            (VITRIKYNANG_AMMANHAPTHE, "sudungkynangmuctieu", lambda: diachiammanhapthe, self._khoangcachsudungkynangtamxa, diachiammanhapthe, True, True),
            (VITRIKYNANG_THUCGIAP, "sudungkynangmuctieu", lambda: diachithucgiap, self._khoangcachsudungkynangtamxa, diachithucgiap, True, True),
            (VITRIKYNANG_THUCTAM, "sudungkynangmuctieu", lambda: diachithuctam, self._khoangcachsudungkynangtamxa, diachithuctam, True, True),

            # Di Tinh Đại Pháp hồi nội lực bảo thú triệu hồi: nghỉ GIANCACHHOIBAOTHUTRIEUHOI giây cho nội lực bảo thú kịp cập nhật, còn lại theo hồi chiêu game.
            # Lưu Huyết Thuật hồi máu dần trong 8 giây: chỉ dùng lại sau GIANCACHLUUHUYETTHUAT giây (lần trước đã hồi xong), không phí pháp lực
            (VITRIKYNANG_DITINHDAIPHAP, "sudungkynangkhongmuctieu", lambda: time.time() - self._thoidiemsudungditinhdaiphapgannhat > GIANCACHHOIBAOTHUTRIEUHOI and self._is_baothukynangtrieuhoihetnoiluc, 0, None, True, True),

            (VITRIKYNANG_LOIDONGCUUTHIEN, "sudungkynangkhongmuctieu", lambda: diachimuctieu and self._somuctieuganbanthan3 >= SOLUONGQUAITOITHIEULOIDONGCUUTHIEN and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, None, True, True),
            (VITRIKYNANG_LOIDONGCUUTHIEN, "sudungkynangkhongmuctieu", lambda: is_xoayvongchieu and diachimuctieu and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, None, True, True),
            (VITRIKYNANG_LOIDONGCUUTHIEN, "dichuyentiepcandenkhoangcach", lambda: is_xoayvongchieu and diachimuctieu and khoangcach > KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHTIEPCANLOIDONGCUUTHIEN, None, False, False),
            # Lôi Động Cửu Thiên đánh quanh bản thân 3 ô: có cụm quái quanh mục tiêu (đánh quái, không PK)
            # thì chạy vào sát mục tiêu (giữa cụm) để lượt sau ra chiêu trúng cả cụm
            (VITRIKYNANG_LOIDONGCUUTHIEN, "dichuyentiepcandenkhoangcach", lambda: diachimuctieu and not is_muctieulanguoichoi and self._somuctieugan3 >= SOLUONGQUAITOITHIEULOIDONGCUUTHIEN and khoangcach > KHOANGCACHTIEPCANLOIDONGCUUTHIEN, KHOANGCACHTIEPCANLOIDONGCUUTHIEN, None, False, False),
            (VITRIKYNANG_PHUCMAQUYET, "sudungkynangmuctieu", lambda: not is_xoayvongchieu and diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True, True),

            (None, "dichuyentiepcantamxa", lambda: diachimuctieu and khoangcach > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, False, False),
        ]

        self._capnhatkynangquantrong("maoson", danhsachuutien, kynangchopheps)

        danhsachuutien = self._sapxepuutientuhoc(danhsachuutien, diachimuctieu)
        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen, is_ngatdichuyen = item
            if vitrikynang and kynangchopheps is not None and vitrikynang not in kynangchopheps:
                continue
            if callable(dieukien) and not dieukien():
                continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang):
                continue
            target_use = target if target else diachimuctieu
            # Bot khác (cùng máy / LAN) vừa gửi cùng chiêu (Thực Cốt / Thực Giáp / Thực Tâm) lên mục tiêu này, hoặc hiệu ứng còn hiệu lực
            # 120s (THOIGIANHIEULUCBUFFMAOSON_MAP), thì dùng chiêu tiếp theo
            if vitrikynang == VITRIKYNANG_MENHTE and loaikynang == "sudungkynangkhongmuctieu":
                # Mệnh Tế: chỉ dùng khi còn người thấp máu quanh mình chưa được bot Mao Sơn khác vừa Mệnh Tế (6 acc cùng tế 1 lúc rất phí)
                idcanhois = [self._get_idmuctieugiucho(tv[2]) for tv in thanhviennhomgans if is_cantebaothu(tv[0])]
                if is_cantebaothu(phantramsinhlucconlai):
                    # Bản thân: khoá theo ID người chơi như bot khác thấy mình (thành viên nhóm)
                    idcanhois.append(("nguoichoi", self.moitruong.get_idnguoichoi()))
                giucho, is_duocgui = self._thugiumenhte(idcanhois)
            else:
                giucho, is_duocgui = self._thugiuchokynangphai("maoson", vitrikynang, loaikynang, target_use)
            if not is_duocgui:
                continue
            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target_use,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen,
                is_ngatdichuyen = is_ngatdichuyen
            )
            if not is_ok:
                self._bogiuchokynangphai(giucho)

            if vitrikynang == VITRIKYNANG_LOIDONGCUUTHIEN and loaikynang == "sudungkynangkhongmuctieu" and is_ok:
                self.moitruong.action_chovankhi(vitrikynang)
                self._thoidiemsudungloidongcuuthiengannhat = time.time()
            if vitrikynang in (VITRIKYNANG_TRIEUHOICUONGTHI, VITRIKYNANG_TRIEUHOITHIENBINH, VITRIKYNANG_TRIEUHOIQUYTOT) and is_ok:
                # Triệu hồi tốn bùa, vận khí bị ngắt là mất bùa: khoá mọi thao tác tới khi vận khí xong
                self._khoavankhitrieuhoi(vitrikynang)
            if vitrikynang == VITRIKYNANG_DITINHDAIPHAP and is_ok:
                self._thoidiemsudungditinhdaiphapgannhat = time.time()
            if vitrikynang == VITRIKYNANG_LUUHUYETTHUAT and is_ok:
                self._thoidiemsudungluuhuyetthuatgannhat = time.time()
            if is_break:
                return

    def action_sudungkynangmonphaivanmongcoc(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)

        diachidoituongcanhoisinh = self._diachidoituongcanhoisinhvanmongcoc
        diachidoituongcanbufftaytranquyet = self._diachidoituongcanbufftaytranquyetvanmongcoc
        diachidoituongcanbufftaytranquyet2 = self._diachidoituongcanbufftaytranquyet2vanmongcoc
        diachidoituongcanbufflinhkhihothe = self._diachidoituongcanbufflinhkhihothevanmongcoc
        diachidoituongcanbommau = self._diachidoituongcanbommauvanmongcoc
        diachidoituongkhietvanquyet = self._diachidoituongkhietvanquyetvanmongcoc
        diachidoituongcanbuffkimcham = self._diachidoituongcanbuffkimchamvanmongcoc
        diachidoituongcanbuffngancham = self._diachidoituongcanbuffnganchamvanmongcoc
        diachidoituongcanbuffcuongthethuat = self._diachidoituongcanbuffcuongthethuatvanmongcoc

        diachidoituongcanbuffphonganthuat = self._diachidoituongcanbuffphonganthuatvanmongcoc
        diachidoituongcanbuffhuyenquangthiemanh = self._diachidoituongcanbuffhuyenquangthiemanhvanmongcoc

        is_cohieuungdauchuyentinhdi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DAUCHUYENTINHDI,), macdinh = False, is_hieuungcoloi = 1)

        diachicantiepcan = None

        if diachidoituongcanbuffphonganthuat and self.moitruong.get_is_kynangsansang(VITRIKYNANG_PHONGANTHUAT):
            diachicantiepcan = diachidoituongcanbuffphonganthuat
        elif diachidoituongcanbuffhuyenquangthiemanh and self.moitruong.get_is_kynangsansang(VITRIKYNANG_HUYENQUANGTHIEMANH):
            diachicantiepcan = diachidoituongcanbuffhuyenquangthiemanh
        # Chỉ tiếp cận đối tượng cần buff khi kỹ năng tương ứng đã học và sẵn sàng, tránh đứng yên cạnh đồng đội/bản thân mà không đánh quái
        elif diachidoituongcanhoisinh and self.moitruong.get_is_kynangsansang(VITRIKYNANG_CAITUHOANSINH):
            diachicantiepcan = diachidoituongcanhoisinh
        elif diachidoituongcanbufftaytranquyet and self.moitruong.get_is_kynangsansang(VITRIKYNANG_TAYTRANQUYET):
            diachicantiepcan = diachidoituongcanbufftaytranquyet
        elif diachidoituongcanbommau and any(self.moitruong.get_is_kynangsansang(vitri) for vitri in (VITRIKYNANG_CAMLOTRI, VITRIKYNANG_KHIETVANQUYET, VITRIKYNANG_SOTRI, VITRIKYNANG_VODINHLUUTHUY)):
            diachicantiepcan = diachidoituongcanbommau
        elif diachidoituongcanbufftaytranquyet2 and self.moitruong.get_is_kynangsansang(VITRIKYNANG_TAYTRANQUYET):
            diachicantiepcan = diachidoituongcanbufftaytranquyet2
        elif diachidoituongcanbuffkimcham and self.moitruong.get_is_kynangsansang(VITRIKYNANG_KIMCHAMDOACH):
            diachicantiepcan = diachidoituongcanbuffkimcham
        elif diachidoituongcanbuffngancham and self.moitruong.get_is_kynangsansang(VITRIKYNANG_NGANCHAMDOACH):
            diachicantiepcan = diachidoituongcanbuffngancham
        elif diachidoituongcanbuffcuongthethuat and self.moitruong.get_is_kynangsansang(VITRIKYNANG_CUONGTHETHUAT):
            diachicantiepcan = diachidoituongcanbuffcuongthethuat
        elif diachimuctieu and not is_muctieulanguoichoi:
            diachicantiepcan = diachimuctieu
        elif diachidoituongcanbufflinhkhihothe and self.moitruong.get_is_kynangsansang(VITRIKYNANG_LINHKHIHOTHE):
            diachicantiepcan = diachidoituongcanbufflinhkhihothe
        # Đối tượng cần tiếp cận là đồng đội cần buff (không phải quái/đối thủ) thì chỉ chạy vừa vào tầm
        loaitiepcan = "dichuyentiepcanbuff" if diachicantiepcan and diachicantiepcan in (diachidoituongcanhoisinh, diachidoituongcanbufftaytranquyet, diachidoituongcanbommau, diachidoituongcanbufftaytranquyet2, diachidoituongcanbuffkimcham, diachidoituongcanbuffngancham, diachidoituongcanbuffcuongthethuat, diachidoituongcanbufflinhkhihothe) else "dichuyentiepcantamxa"

        is_nganchamdoachsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_NGANCHAMDOACH)
        if self._is_nganchamdoachsansang and not is_nganchamdoachsansang and self._idnguoichoibuffnganchamgannhat:
            self._thoidiembuffnganchamgannhat_map[self._idnguoichoibuffnganchamgannhat] = time.time()
            self._thoidiembuffnganchamgannhat_map = donbangthoidiem(self._thoidiembuffnganchamgannhat_map, 120.)
        self._is_nganchamdoachsansang = is_nganchamdoachsansang

        is_kimchamdoachsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_KIMCHAMDOACH)
        if self._is_kimchamdoachsansang and not is_kimchamdoachsansang and self._idnguoichoibuffkimchamgannhat:
            self._thoidiembuffkimchamgannhat_map[self._idnguoichoibuffkimchamgannhat] = time.time()
            self._thoidiembuffkimchamgannhat_map = donbangthoidiem(self._thoidiembuffkimchamgannhat_map, 120.)
        self._is_kimchamdoachsansang = is_kimchamdoachsansang

        is_cuongthethuatsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_CUONGTHETHUAT)
        if self._is_cuongthethuatsansang and not is_cuongthethuatsansang and self._idnguoichoibuffcuongthethuatgannhat:
            self._thoidiembuffcuongthethuatgannhat_map[self._idnguoichoibuffcuongthethuatgannhat] = time.time()
            self._thoidiembuffcuongthethuatgannhat_map = donbangthoidiem(self._thoidiembuffcuongthethuatgannhat_map, 120.)
        self._is_cuongthethuatsansang = is_cuongthethuatsansang

        noilucconlai = self.moitruong.get_noilucconlai()
        noiluctoida = self.moitruong.get_noiluctoida()
        phantramnoiluc = int(noilucconlai * 100 / noiluctoida) if noiluctoida else 0
        khoangcachmuctieutancong = self.moitruong.get_khoangcachtamdanh(diachimuctieu)
        # Acc gà chưa học chiêu đánh nào (QuanSuMuMuu 9286 chỉ có buff / hồi máu, 2026-11-03): quái trong tầm mà không có gì để gửi nên không có
        # yêu cầu tấn công, "đi dạo" thắng => chạy qua chạy lại cạnh quái. Đánh thường như nhân vật chưa vào phái (ám khí tầm xa, còn lại cận chiến)
        is_chuahocchieudanh = not any(self.moitruong.get_is_kynangdahoc(vitri) for vitri in (VITRIKYNANG_LIETPHONGQUYET, VITRIKYNANG_PHONGVUKINHTHIEN))
        khoangcachdanhthuong = self._khoangcachsudungkynangtamxa if self.moitruong.get_idloaivukhi() == IDLOAIVUKHI_AMKHI else KHOANGCACHSUDUNGKYNANGCANCHIEN
        is_contranky = self.moitruong.action_timkiemvatphamhanhtrang(TRANKY)
        is_dangbatpk = self.moitruong.get_idmaupk() != MAUPK_HOABINH

        idloaivukhimuctieu = self.moitruong.get_idloaivukhi(diachimuctieu)
        is_muctieugiukhoangcach = (is_muctieulanguoichoi and idloaivukhimuctieu not in (IDLOAIVUKHI_KIEM, IDLOAIVUKHI_AMKHI))

        is_cobaothukynangtrieuhoi = self._get_is_cobaothukynangtrieuhoi()
        # Bật xoay vòng chiêu có mục tiêu: thay Liệt Phong Quyết (gửi liên tục) bằng Phong Vũ Kinh Thiên (đánh liên tục 8s chỉ với 1 lệnh,
        # không dùng lại lên cùng mục tiêu trong THOIGIANPHONGVUKINHTHIEN giây) => ít lệnh, hết việc thì nhường lượt cho nhân vật khác
        is_xoayvongchieu = self.moitruong.get_is_batxoayvongchieu()
        idmuctieu = self.moitruong.get_iddoituong(diachimuctieu) if diachimuctieu else None

        danhsachuutien = [
            # Chưa có bảo thú triệu hồi thì Rải Đậu Thành Binh (tốn 60 pháp lực + Đậu Nành); chờ 3s sau mỗi lần gọi để Đậu Binh kịp xuất hiện
            (VITRIKYNANG_RAIDAUTHANHBINH, "sudungkynangkhongmuctieu", lambda: self._baothutrieuhoimaoson in (BAOTHUTRIEUHOI_TUDONG, DAUBINH) and not is_cobaothukynangtrieuhoi and time.time() - self._thoidiemraidauthanhbinhgannhat > 3. and self.moitruong.action_timkiemvatphamhanhtrang(DAUNANH), 0, None, True),
            (VITRIKYNANG_PHONGANTHUAT, "sudungkynangmuctieu", lambda: diachidoituongcanbuffphonganthuat and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbuffphonganthuat) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffphonganthuat, True),
            (VITRIKYNANG_HUYENQUANGTHIEMANH, "sudungkynangmuctieu", lambda: diachidoituongcanbuffhuyenquangthiemanh and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbuffhuyenquangthiemanh) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffhuyenquangthiemanh, True),

            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() not in (BANDO_TIVO, BANDO_CHIENTRUONG) and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 5. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), self._khoangcachsudungkynangtamxa, None, False),
            (VITRIKYNANG_TOANPHONGQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa and self.moitruong.get_phantramsinhlucconlai(diachimuctieu) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 1), self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_CAITUHOANSINH, "sudungkynanglendongdoi", lambda: diachidoituongcanhoisinh and self.moitruong.get_khoangcachtamdanh(diachidoituongcanhoisinh) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanhoisinh, True),
            (VITRIKYNANG_TAYTRANQUYET, "sudungkynanglendongdoi", lambda: diachidoituongcanbufftaytranquyet and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbufftaytranquyet) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbufftaytranquyet, True),
            (VITRIKYNANG_CAMLOTRI, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbommau) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbommau, True),
            (VITRIKYNANG_KHIETVANQUYET, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongkhietvanquyet and self.moitruong.get_khoangcachtamdanh(diachidoituongkhietvanquyet) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongkhietvanquyet, True),
            (VITRIKYNANG_SOTRI, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbommau) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbommau, True),
            (VITRIKYNANG_VODINHLUUTHUY, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbommau) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbommau, True),
            (VITRIKYNANG_TAYTRANQUYET, "sudungkynanglendongdoi", lambda: diachidoituongcanbufftaytranquyet2 and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbufftaytranquyet2) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbufftaytranquyet2, True),
            (VITRIKYNANG_NGANCHAMDOACH, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffngancham and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbuffngancham) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffngancham, True),
            (VITRIKYNANG_KIMCHAMDOACH, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffkimcham and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbuffkimcham) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffkimcham, True),
            (VITRIKYNANG_CUONGTHETHUAT, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffcuongthethuat and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbuffcuongthethuat) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffcuongthethuat, True),

            (None, loaitiepcan, lambda: diachicantiepcan and self.moitruong.get_khoangcachtamdanh(diachicantiepcan) > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachicantiepcan, False),

            (VITRIKYNANG_DONGIAPTRAN, "sudungkynangphudau", lambda: diachimuctieu and is_contranky and phantramnoiluc > 25 and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa, khoangcachmuctieutancong + random.choice([-1, 1]), None, True),
            (VITRIKYNANG_KYMONTRAN, "sudungkynangphudau", lambda: diachimuctieu and is_contranky and phantramnoiluc > 25 and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa, khoangcachmuctieutancong + random.randint(0, 0), None, True),
            (VITRIKYNANG_LIETPHONGQUYET, "sudungkynangmuctieu", lambda: not is_xoayvongchieu and not is_dangbatpk and diachimuctieu and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_PHONGVUKINHTHIEN, "sudungkynangmuctieu", lambda: is_xoayvongchieu and not is_dangbatpk and diachimuctieu and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa
                and time.time() - self._thoidiemphongvukinhthien_map.get(idmuctieu, 0.) >= THOIGIANPHONGVUKINHTHIEN, self._khoangcachsudungkynangtamxa, None, True),
            (None, "tancongvatly", lambda: is_chuahocchieudanh and diachimuctieu and khoangcachmuctieutancong <= khoangcachdanhthuong
                and (not self._is_battudongtancongvatly or time.time() - self.moitruong._thoidiemsudungtancongvatlygannhat > 5.), khoangcachdanhthuong, None, False),
            (None, "dichuyentiepcancanchien", lambda: is_chuahocchieudanh and diachimuctieu and not is_muctieulanguoichoi and khoangcachdanhthuong == KHOANGCACHSUDUNGKYNANGCANCHIEN
                and khoangcachmuctieutancong > khoangcachdanhthuong, 0, None, False),
            # (None, "tancongvatly", lambda: diachimuctieu and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa and (not self._is_battudongtancongvatly or time.time() - self.moitruong._thoidiemsudungtancongvatlygannhat > 5.), self._khoangcachsudungkynangtamxa, None, True),

            (VITRIKYNANG_LINHKHIHOTHE, "sudungkynanglendongdoi", lambda: diachidoituongcanbufflinhkhihothe and self.moitruong.get_khoangcachtamdanh(diachidoituongcanbufflinhkhihothe) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbufflinhkhihothe, True),
            (None, "dichuyengiukhoangcach", lambda: diachimuctieu and is_muctieugiukhoangcach and khoangcachmuctieutancong <= KHOANGCACHLUIGIUKHOANGCACH, khoangcachmuctieutancong + 3., None, False),

            (None, loaitiepcan, lambda: diachicantiepcan and self.moitruong.get_khoangcachtamdanh(diachicantiepcan) > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachicantiepcan, False),
        ]

        self._capnhatkynangquantrong("vanmongcoc", danhsachuutien)

        danhsachuutien = self._sapxepuutientuhoc(danhsachuutien, diachimuctieu)
        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang): continue

            target = target if target else diachimuctieu

            # Bot khác cùng máy vừa gửi cùng chiêu (Phong Ấn Thuật, Huyền Quang Thiểm Ảnh, Cải Tử Hoàn Sinh) lên mục tiêu này thì dùng chiêu tiếp theo:
            # 2 Vân Mộng Cốc không cùng hồi sinh 1 người, không cùng khống chế 1 kẻ địch
            giucho, is_duocgui = self._thugiuchokynangphai("vanmongcoc", vitrikynang, loaikynang, target)
            if not is_duocgui:
                continue

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen
            )
            if not is_ok:
                self._bogiuchokynangphai(giucho)

            if vitrikynang == VITRIKYNANG_RAIDAUTHANHBINH and is_ok:
                self._thoidiemraidauthanhbinhgannhat = time.time()
                # Danh sách ưu tiên Vân Mộng Cốc không có tham số ngắt di chuyển nên ngắt thủ công: đang chạy sẽ làm hỏng vận khí
                self.moitruong.action_ngatdichuyen()
                # Tốn Đậu Nành, vận khí bị ngắt là mất: khoá mọi thao tác tới khi vận khí xong
                self._khoavankhitrieuhoi(vitrikynang)

            if vitrikynang == VITRIKYNANG_PHONGVUKINHTHIEN and is_ok and idmuctieu:
                self._thoidiemphongvukinhthien_map[idmuctieu] = time.time()
                self._thoidiemphongvukinhthien_map = donbangthoidiem(self._thoidiemphongvukinhthien_map, 120.)

            if is_ok and target:
                if self.moitruong.get_is_nguoichoi(target):
                    idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(target)
                    if idnguoichoidangxemxet:
                        if vitrikynang == VITRIKYNANG_CAITUHOANSINH:
                            self._thoidiemcaituhoansinh_map[idnguoichoidangxemxet] = time.time()
                            self._thoidiemcaituhoansinh_map = donbangthoidiem(self._thoidiemcaituhoansinh_map, 120.)
                        if vitrikynang == VITRIKYNANG_NGANCHAMDOACH:
                            self._idnguoichoibuffnganchamgannhat = idnguoichoidangxemxet
                        if vitrikynang == VITRIKYNANG_KIMCHAMDOACH:
                            self._idnguoichoibuffkimchamgannhat = idnguoichoidangxemxet
                        if vitrikynang == VITRIKYNANG_CUONGTHETHUAT:
                            self._idnguoichoibuffcuongthethuatgannhat = idnguoichoidangxemxet

            if is_break:
                return

    def action_tudongsudungkynang(self):
        # self._yeucautancong là bản nháp của lượt này; luồng di chuyển (chạy song song mỗi 0.05s) chỉ đọc bản đã xuất
        # self._yeucautancongxuat, gán sau khi tính xong. Trước đây luồng di chuyển đọc thẳng bản nháp: đầu lượt vừa xoá về None
        # (lượt kỹ năng có khi mất cả trăm ms) là nó tưởng hết mục tiêu, chuyển sang Đi dạo tìm đường tới điểm dò quái ở xa, lượt
        # sau lại Tấn công => đang đánh dở chạy đi rồi quay lại
        self._yeucautancong = None
        self._is_giuyeucautancongcu = False
        try:
            self._tudongsudungkynang()
        finally:
            self._xuatyeucautancong()

    def _xuatyeucautancong(self):
        thoidiemhientai = time.time()
        if self._yeucautancong:
            self._yeucautancongxuat = self._yeucautancong
            self._thoidiemxuatyeucautancong = thoidiemhientai
            return
        # Lượt này không ra yêu cầu (đang chờ lệnh đánh trước, chờ làm mới toạ độ, kill đã bật, chiêu đang hồi...) mà vẫn còn
        # đang chọn đúng con vừa đánh, nó chưa chết: giữ yêu cầu cũ tối đa THOIGIANGIUYEUCAUTANCONG giây thay vì bỏ trống để
        # Đi dạo / Tìm mục tiêu chung kéo đi chỗ khác. Về bán, gom quái, nhặt đồ ưu tiên thì bỏ luôn như cũ
        cu = self._yeucautancongxuat
        diachicu = cu.get("diachimuctieu") if cu else None
        if self._is_giuyeucautancongcu and diachicu \
                and thoidiemhientai - self._thoidiemxuatyeucautancong < THOIGIANGIUYEUCAUTANCONG \
                and diachicu == self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon() \
                and self.moitruong.get_is_nhanvattontai(diachicu) and not self.moitruong.get_is_nhanvatdachet(diachicu):
            return
        self._yeucautancongxuat = None

    def _tudongsudungkynang(self):
        self._capnhattuhockynang()

        if self._is_battudongtancongvatly and self.moitruong.get_is_nhanvatbichoang():
            self._is_battudongtancongvatly = False

        if self._trangthaiveban != 0:
            return

        if self._is_danggomquai:
            return

        if self._is_danguutiennhatdo:
            return

        self._is_giuyeucautancongcu = True

        if self.moitruong.get_is_nhanvatchuasansang(self.moitruong.get_diachicosothongtinnhanvat1()):
            return
        if time.time() - self._thoidiemtamngungsudungkynang < 0.:
            return

        self._chontamxa(time.time())
        tenmonphai = self.moitruong.get_tenmonphai()

        # Chỉ dùng Tự động tấn công: phái có cách gửi "kill" riêng không phụ thuộc chiêu (Đường Môn vòng vật cản, Đào Hoa, Cấm Vệ Quân) vẫn
        # chạy danh sách phái (kỹ năng bị bỏ ở action_xulyuutiensudungkynang); phái khác (kill chỉ khi chưa học chiêu / hết nội lực, hoặc
        # không có kill) thì đánh như chưa môn phái: kill + tiếp cận theo vũ khí
        if self._is_chidungtudongtancong and tenmonphai not in PHAICOTANCONGVATLYRIENG:
            tenmonphai = None

        if tenmonphai is None:
            self.action_sudungkynangvomonphai()
        elif hasattr(self, f"action_sudungkynangmonphai{tenmonphai}"):
            getattr(self, f"action_sudungkynangmonphai{tenmonphai}")()
        elif hasattr(self, f"_action_sudungkynang_{tenmonphai}"):
            getattr(self, f"_action_sudungkynang_{tenmonphai}")()

    def action_sudungkynangvomonphai(self):
        # Nhân vật chưa có môn phái: chỉ dùng tấn công vật lý
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachimuctieu: return

        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu)
        # Cầm ám khí thì đánh tầm xa, còn lại đánh cận chiến
        khoangcachtancong = self._khoangcachsudungkynangtamxa if self.moitruong.get_idloaivukhi() == IDLOAIVUKHI_AMKHI else KHOANGCACHSUDUNGKYNANGCANCHIEN

        danhsachuutien = [
            (None, "tancongvatly", lambda: khoangcach <= khoangcachtancong and (not self._is_battudongtancongvatly or time.time() - self.moitruong._thoidiemsudungtancongvatlygannhat > 5.), khoangcachtancong, None, False, True),
            (None, "dichuyentiepcancanchien", lambda: khoangcachtancong == KHOANGCACHSUDUNGKYNANGCANCHIEN and khoangcach > khoangcachtancong, 0, None, False, False),
            (None, "dichuyentiepcantamxa", lambda: khoangcachtancong == self._khoangcachsudungkynangtamxa and khoangcach > khoangcachtancong, khoangcachtancong, None, False, False),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen, is_ngatdichuyen = item

            if callable(dieukien) and not dieukien(): continue

            target = target if target else diachimuctieu

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen,
                is_ngatdichuyen = is_ngatdichuyen
            )

            if is_break:
                return

    def _capnhatthucsondao(self):
        # Thục Sơn Đao / Kiếm theo vũ khí đang cầm: loại vũ khí của nhân vật (+0x1180, 61 đao / 62 kiếm). Chưa rõ thì đọc tên + mô tả
        # vũ khí đang mặc ("desc 3") tìm chữ Đao / Kiếm, mỗi món chỉ đọc 1 lần; vẫn không ra (tay không...) thì giữ như lần trước
        idloaivukhi = self.moitruong.get_idloaivukhi()
        if idloaivukhi in (IDLOAIVUKHI_DAO, IDLOAIVUKHI_KIEM):
            self._is_thucsondao = idloaivukhi == IDLOAIVUKHI_DAO
            return
        vitrivukhi = VITRITRANGBIDAUTIEN + 2
        iddoituongvukhi = self.moitruong.get_iddoituongvatphamhanhtrang(vitrivukhi)
        if not iddoituongvukhi or iddoituongvukhi == self._iddoituongvukhidadoc:
            return
        self._iddoituongvukhidadoc = iddoituongvukhi
        for chu in (self.moitruong.get_tenvatphamhanhtrang(vitrivukhi) or "", self.moitruong.get_motavatphamhanhtrang(vitrivukhi) or ""):
            is_dao, is_kiem = "Đao" in chu, "Kiếm" in chu
            if is_dao != is_kiem:
                self._is_thucsondao = is_dao
                return

    def action_sudungkynangmonphaithucson(self):
        self._capnhatthucsondao()
        if self._is_thucsondao:
            self.action_sudungkynangmonphaithucsondao()
        else:
            self.action_sudungkynangmonphaithucsonkiem()

    def action_sudungkynangmonphaithucsonkiem(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieupk = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu) if diachimuctieu else 0
        phantramsinhluc = self.moitruong.get_phantramsinhlucconlai()

        diachidongdoicanbuff = None
        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

        danhsachungviens = [self.moitruong.get_diachicosothongtinnhanvat1()]
        if self.moitruong.get_is_dangnamtrongnhom():
            j = -1
            while True:
                j += 1
                addr = self.moitruong.get_diachicosothongtindoituongx(j)
                if not addr:
                    break
                if not self.moitruong.get_is_nhanvattontai(addr) or self.moitruong.get_is_nhanvatdachet(addr):
                    continue
                if self.moitruong.get_khoangcachtamdanh(addr) > self._khoangcachsudungkynangtamxa:
                    continue
                # Đồng đội vừa xuất hiện thì chờ đủ THOIGIANCHOCHONMUCTIEUMOI mới buff / hồi máu
                if self._is_doituongmoixuathien(addr):
                    continue
                id_nd = self.moitruong.get_idnguoichoi(addr)
                if id_nd in idnguoichoithanhviennhoms and id_nd != self.moitruong.get_idnguoichoi():
                    danhsachungviens.append(addr)

        for addr in danhsachungviens:
            is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), diachicosothongtinnhanvat = addr, macdinh = True, is_hieuungcoloi = 1)
            is_quathoigian = False

            if is_thieuhieuung or is_quathoigian:
                diachidongdoicanbuff = addr
                break

        # Đồng đội (không tính bản thân) máu thấp nhất dưới 75% để buff Tiên Khí
        diachidongdoimauthap = None
        phantramsinhlucdongdoithapnhat = 75
        for addr in danhsachungviens[1:]:
            phantramsinhlucdongdoi = self.moitruong.get_phantramsinhlucconlai(addr)
            if phantramsinhlucdongdoi < phantramsinhlucdongdoithapnhat:
                phantramsinhlucdongdoithapnhat = phantramsinhlucdongdoi
                diachidongdoimauthap = addr
        is_tieuchuthiensansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_TIEUCHUTHIEN)
        if self._is_tieuchuthiensansang and not is_tieuchuthiensansang and self._idnguoichoibuffnoikhanggannhat:
            self._thoidiembuffnoikhanggannhat_map[self._idnguoichoibuffnoikhanggannhat] = time.time()
            self._thoidiembuffnoikhanggannhat_map = donbangthoidiem(self._thoidiembuffnoikhanggannhat_map, 120.)
        self._is_tieuchuthiensansang = is_tieuchuthiensansang

        noilucconlai = self.moitruong.get_noilucconlai()
        is_bituocvukhi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, is_hieuungcoloi = 0)
        # Chưa học thì _is_kynangdungduoc tự bỏ qua, không cần xét cấp
        is_ngukiemdudieukien = diachimuctieu and self._is_nhieumuctieugan8
        # Chỉ chạy vào khi đánh quái lúc di chuyển tự do, PK thì giữ khoảng cách như cũ
        is_ngukiemtiepcan = is_ngukiemdudieukien and self._is_tudongdichuyendiemdanhxungquanh and not is_muctieupk
        danhsachuutien = [
            # Bị tước vũ khí: dùng Định Tâm Quyết ngay để giải, không chờ đủ nội lực ngưỡng
            (VITRIKYNANG_TINHTAMQUYET, "sudungkynangkhongmuctieu", lambda: is_bituocvukhi or self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0), 0, None, True),
            # (VITRIKYNANG_TIENKHI, "sudungkynanglenbanthan", lambda: phantramsinhluc <= 75 and noilucconlai > 100, 0, None, True),
            (VITRIKYNANG_TIENTHANVODICH, "sudungkynangkhongmuctieu", lambda: (phantramsinhluc <= 25 or (is_muctieupk and phantramsinhluc <= 50)), 0, None, True),
            (VITRIKYNANG_TIEUCHUTHIEN, "sudungkynanglendongdoi", lambda: diachidongdoicanbuff, self._khoangcachsudungkynangtamxa, diachidongdoicanbuff, False),
            (VITRIKYNANG_BANGPHACHNGANTAM, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_LANGKHONGCHIHUYET, "sudungkynangmuctieu", lambda: is_muctieupk and self.moitruong.get_is_cothegaychoang(diachimuctieu) and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_VANKIEMXUYENTAM, "sudungkynangmuctieu", lambda: is_muctieupk and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True),
            # Đang di chuyển tự do (farm): cụm quái đếm quanh mục tiêu, còn Ngự Kiếm Phi Tiên đánh quanh bản thân
            # => chạy vào sát mục tiêu (giữa cụm) rồi mới ra chiêu để trúng nhiều mục tiêu nhất
            (VITRIKYNANG_NGUKIEMPHITIEN, "dichuyentiepcandenkhoangcach", lambda: is_ngukiemtiepcan and khoangcach > KHOANGCACHTIEPCANNGUKIEMPHITIEN, KHOANGCACHTIEPCANNGUKIEMPHITIEN, None, False),
            (VITRIKYNANG_NGUKIEMPHITIEN, "sudungkynangkhongmuctieu", lambda: is_ngukiemdudieukien and khoangcach <= (KHOANGCACHTIEPCANNGUKIEMPHITIEN if is_ngukiemtiepcan else KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN), 0, None, True),
            # Không có mục tiêu hoặc đang đánh quái (không PK) thì buff Tiên Khí cho đồng đội máu dưới 75%
            # (VITRIKYNANG_TIENKHI, "sudungkynanglendongdoi", lambda: noilucconlai > 100 and not is_muctieupk and diachidongdoimauthap, self._khoangcachsudungkynangtamxa, diachidongdoimauthap, False),
            (VITRIKYNANG_NGUKIEMTHUAT, "sudungkynangmuctieu", lambda: diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_BANGTAMTHUC, "sudungkynangmuctieu", lambda: diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_VANVUTIEUDIEU, "sudungkynangmuctieu", lambda: diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_TIENNHANCHILO, "sudungkynangmuctieu", lambda: diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True),
            (None, "dichuyentiepcantamxa", lambda: diachimuctieu and khoangcach > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, False),
        ]
        # Bị tước vũ khí chỉ còn dùng được Tiên Khí, Định Tâm Quyết, Tiên Thân Vô Địch, Tiểu Chu Thiên
        if is_bituocvukhi:
            danhsachuutien = [x for x in danhsachuutien if x[0] in (VITRIKYNANG_TIENKHI, VITRIKYNANG_TINHTAMQUYET, VITRIKYNANG_TIENTHANVODICH, VITRIKYNANG_TIEUCHUTHIEN)]

        self._capnhatkynangquantrong("thucsonkiem", danhsachuutien)

        danhsachuutien = self._sapxepuutientuhoc(danhsachuutien, diachimuctieu)
        for vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen in danhsachuutien:
            if callable(dieukien) and not dieukien():
                continue

            if vitrikynang and not self._is_kynangdungduoc(vitrikynang):
                continue

            # Bot khác cùng máy vừa gây choáng (Lăng Không Chỉ Huyệt...) lên mục tiêu này thì dùng chiêu tiếp theo
            giucho, is_duocgui = self._thugiuchokynangphai("thucsonkiem", vitrikynang, loaikynang, target if target else diachimuctieu)
            if not is_duocgui:
                continue
            is_ok, is_break = self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, target if target else diachimuctieu, khoangcachyeucau, is_yeucaukhongdichuyen)
            if not is_ok:
                self._bogiuchokynangphai(giucho)
            if is_ok and vitrikynang == VITRIKYNANG_TIEUCHUTHIEN and target:
                self._idnguoichoibuffnoikhanggannhat = self.moitruong.get_idnguoichoi(target)
            # Ngự Kiếm Phi Tiên, Tiểu Chu Thiên kéo dài tới hết tư thế ra chiêu: không đứng lại trước khi ra chiêu, vào tư thế ra chiêu thì
            # ngắt di chuyển (action_ngatdichuyenkhixuatchieu) rồi giữ đứng yên tới khi hết tư thế ra chiêu (giới hạn 10s phòng đọc tư thế sai);
            # chờ tối đa THOIGIANCHONGATDICHUYENXUATCHIEU giây để thấy tư thế ra chiêu, không thấy thì thôi giữ
            if is_ok and vitrikynang in (VITRIKYNANG_NGUKIEMPHITIEN, VITRIKYNANG_TIEUCHUTHIEN) and not loaikynang.startswith("dichuyen"):
                # Như bản cũ: ngắt di chuyển ngay và đứng yên ít nhất 1s (chờ game chuyển sang tư thế ra chiêu)
                self.moitruong.action_ngatdichuyen()
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                self._thoidiemhetchongatdichuyen = time.time() + THOIGIANCHONGATDICHUYENXUATCHIEU
                self._thoidiemhetgiuchieudangra = max(self._thoidiemhetgiuchieudangra, time.time() + 10.)
                self._thoidiembatdaugiuchieudangra = time.time()
                self._is_dathaychieudangra = False
            if is_break:
                return

    def action_sudungkynangmonphaithucsondao(self):
        if not self._is_tudongsudungkynang: return
        self._capnhatdokhaithien()
        khoa = self._khoamuctieuluutinh
        if khoa and (time.time() > khoa["hethan"] or not self.moitruong.get_is_kynangsansang(VITRIKYNANG_LUUTINHTRUYMANG)):
            # Hết hạn, hoặc Lưu Tinh đã vào hồi (đã ra chiêu): thôi giữ mục tiêu
            self._khoamuctieuluutinh = None
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        khoangcach = self.moitruong.get_khoangcachtamdanh(diachimuctieu) if diachimuctieu else 0
        phantramsinhluc = self.moitruong.get_phantramsinhlucconlai()
        noiluc = self.moitruong.get_noilucconlai()

        diachidongdoicanbuff = None
        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
        danhsachungviens = [self.moitruong.get_diachicosothongtinnhanvat1()]

        if self.moitruong.get_is_dangnamtrongnhom():
            j = -1
            while True:
                j += 1
                addr = self.moitruong.get_diachicosothongtindoituongx(j)
                if not addr: break
                if not self.moitruong.get_is_nhanvattontai(addr) or self.moitruong.get_is_nhanvatdachet(addr): continue
                if self.moitruong.get_khoangcachtamdanh(addr) > self._khoangcachsudungkynangtamxa: continue
                # Đồng đội vừa xuất hiện thì chờ đủ THOIGIANCHOCHONMUCTIEUMOI mới buff
                if self._is_doituongmoixuathien(addr): continue
                id_nd = self.moitruong.get_idnguoichoi(addr)
                if id_nd in idnguoichoithanhviennhoms and id_nd != self.moitruong.get_idnguoichoi():
                    danhsachungviens.append(addr)

        for addr in danhsachungviens:
            id_nd = self.moitruong.get_idnguoichoi(addr)
            is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), diachicosothongtinnhanvat = addr, macdinh = True, is_hieuungcoloi = 1)
            is_quathoigian = self.moitruong.get_diachicosothongtinnhanvat1() != addr and self.moitruong.get_is_nguoichoi(addr) and time.time() - self._thoidiembuffnoikhanggannhat_map.get(id_nd, 0) > 60
            if is_thieuhieuung or is_quathoigian:
                diachidongdoicanbuff = addr
                break

        is_tieuchuthiensansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_TIEUCHUTHIEN)
        if self._is_tieuchuthiensansang and not is_tieuchuthiensansang and self._idnguoichoibuffnoikhanggannhat:
            self._thoidiembuffnoikhanggannhat_map[self._idnguoichoibuffnoikhanggannhat] = time.time()
            self._thoidiembuffnoikhanggannhat_map = donbangthoidiem(self._thoidiembuffnoikhanggannhat_map, 120.)
        self._is_tieuchuthiensansang = is_tieuchuthiensansang

        # Chỉ dùng Tự động tấn công: Khai Thiên Tịch Địa / Lưu Tinh Truy Mạng gửi thẳng (không qua action_xulyuutiensudungkynang) nên bỏ ở đây
        if diachimuctieu and not self._is_chidungtudongtancong and self.moitruong.get_is_cothetancong(diachimuctieu):
            is_bimatamthuat = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MATAMTHUAT,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu)
            # Người dùng 2026-11-04: Khai Thiên Tịch Địa dùng được là ưu tiên số 1 (chọn toạ độ, trúng cả hình chữ nhật chỗ đứng - điểm
            # rơi, góc xấu thì đi lấy góc rộng hơn), rồi Lưu Tinh Truy Mạng (chọn mục tiêu, lướt tới nó), rồi mới tới các chiêu khác
            if not is_bimatamthuat and self._thudungkhaithientichdiadanh(diachimuctieu, idtuthenhanvat, noiluc):
                return
            if self._idmuctieuluutinhtruymang != diachimuctieu:
                self._idmuctieuluutinhtruymang = diachimuctieu
                self._solanthatbailuutinhtruymang = 0

            is_luutinhtruymangsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_LUUTINHTRUYMANG) and self._is_dutieuhao(VITRIKYNANG_LUUTINHTRUYMANG)

            if self._is_luutinhtruymangsansang and not is_luutinhtruymangsansang:
                if khoangcach <= 1.5:
                    # Vừa ra chiêu sát mục tiêu: tạm ngưng di chuyển 0.5s như bản cũ, vào tư thế xuất chiêu thì ngắt tiếp
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self._thoidiemhetchongatdichuyen = time.time() + THOIGIANCHONGATDICHUYENXUATCHIEU

            self._is_luutinhtruymangsansang = is_luutinhtruymangsansang

            if self._solanthatbailuutinhtruymang >= self._solanthatbailuutinhtruymangtoida and time.time() - self._thoidiembiphatluutinhtruymang > 3.0:
                self._solanthatbailuutinhtruymang = 0
                self._thoidiembiphatluutinhtruymang = 0.

            if not is_luutinhtruymangsansang:
                self._solanthatbailuutinhtruymang = 0
                self._thoidiembiphatluutinhtruymang = 0.

            is_luutinhtruymangbicam = time.time() - self._thoidiemtamngungluutinhtruymang < 0.8
            is_sudungluutinhtruymangthatbai = is_luutinhtruymangbicam and is_luutinhtruymangsansang
            if is_sudungluutinhtruymangthatbai and self._solanthatbailuutinhtruymang < self._solanthatbailuutinhtruymangtoida:
                self._solanthatbailuutinhtruymang += 1
                if self._solanthatbailuutinhtruymang == self._solanthatbailuutinhtruymangtoida:
                    self._thoidiembiphatluutinhtruymang = time.time()

            is_duocphepsudungluutinhtruymang = is_luutinhtruymangsansang and noiluc > 50 and self._solanthatbailuutinhtruymang < self._solanthatbailuutinhtruymangtoida and idtuthenhanvat not in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT)

            if khoangcach <= self._khoangcachsudungkynangtamxa and is_duocphepsudungluutinhtruymang and not is_bimatamthuat \
                    and not self.moitruong.get_is_khongthedungkynang() \
                    and not self.moitruong.get_is_doanthangcovatcan(*self.moitruong.get_toado(), *self.moitruong.get_toado(diachimuctieu)):
                # Lưu Tinh Truy Mạng chọn mục tiêu, lướt tới nó: mô tả ghi "di chuyển đến sau lưng mục tiêu" nhưng thực tế chỉ cần đoạn thẳng
                # mình - mục tiêu không có vật cản (người dùng xác nhận 2026-11-04, không xét ô sau lưng). Bị chắn thì để Khai Thiên Tịch
                # Địa / đánh cận chiến / tiếp cận như thường
                self._yeucautancong = None
                self._is_giuyeucautancongcu = False
                if self.moitruong.action_sudungkynangvitrimuctieu(VITRIKYNANG_LUUTINHTRUYMANG):
                    # Gửi thẳng, không qua action_xulyuutiensudungkynang: tự đánh dấu chiêu cần đứng yên và chặn client tự bước từ lúc gửi
                    self.moitruong.set_is_chieucanngatdichuyen(True, diachimuctieu)
                    self._ghinhanchieuguivaomuctieu(diachimuctieu)
                    self._thoidiemhetchantudichuyentruocxuatchieu = time.time() + THOIGIANCHANTUDICHUYENTRUOCXUATCHIEU
                    self.moitruong.action_chandichuyen()
                    self._thoidiemtamngungluutinhtruymang = time.time()
                    self._solansudungluutinhtruymang += 1
                    self._idmuctieuluutinhgannhat = self.moitruong.get_iddoituong(diachimuctieu)
                    if IS_LOGCAULENH and self._khoamuctieuluutinh:
                        self.moitruong._inlog(f"[LƯU TINH] nối Khai Thiên, lướt về mục tiêu cũ {self.moitruong.get_tendoituong(diachimuctieu)}")
                    return

        danhsachuutien = [
            (VITRIKYNANG_TINHTAMQUYET, "sudungkynangkhongmuctieu", lambda: noiluc > 150 and self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0), 0, None, True),
            (VITRIKYNANG_TIENKHI, "sudungkynanglenbanthan", lambda: noiluc > 150 and phantramsinhluc <= 75, 0, None, True),
            (VITRIKYNANG_TIEUCHUTHIEN, "sudungkynanglendongdoi", lambda: noiluc > 150 and diachidongdoicanbuff, self._khoangcachsudungkynangtamxa, diachidongdoicanbuff, True),
            (VITRIKYNANG_BANGPHACHNGANTAM, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1), 0, None, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False),
            (VITRIKYNANG_NGHENHPHONGTRAM, "sudungkynangmuctieu", lambda: diachimuctieu and noiluc > 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_PHAKHONGKICH, "sudungkynangmuctieu", lambda: diachimuctieu and noiluc > 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_PHAMATRAM, "sudungkynangmuctieu", lambda: diachimuctieu and noiluc > 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_DONDAOTRUCNHAP, "sudungkynangmuctieu", lambda: diachimuctieu and noiluc > 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (None, "tancongvatly", lambda: diachimuctieu and noiluc < 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
        ]

        danhsachuutien = self._sapxepuutientuhoc(danhsachuutien, diachimuctieu)
        for vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngat in danhsachuutien:
            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang): continue

            is_ok, is_break = self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, target if target else diachimuctieu, khoangcachyeucau, is_ngat)
            if is_ok and vitrikynang == VITRIKYNANG_TIEUCHUTHIEN and target:
                self._idnguoichoibuffnoikhanggannhat = self.moitruong.get_idnguoichoi(target)
            if is_break:
                return
