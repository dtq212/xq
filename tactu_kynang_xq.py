# Phần kỹ năng: ưu tiên dùng kỹ năng, dùng kỹ năng từng môn phái, tâm pháp, Đào Hoa Nguyên, đổi đồ khi triệu hồi.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import random
import time

from hangso_xq import *
from moitruong_xq import MoiTruong, DOUUTIEN_THAP, DOUUTIEN_KHANCAP, DOUUTIEN_CAO, SOLUONGDOITUONGXUNGQUANHTOIDA, tinh_is_huongmatvediem
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam
from tienich_xq import laynhomtodoitudongs, laynhanvattodoitudongs, donbangthoidiem


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
                if TENKYNANG_TUDONGCONGKICH in noidung:
                    if "ngừng" in noidung:
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
                    if info.get("tenbando") != idbandohientai or info.get("x") is None:
                        continue
                    if self.moitruong.get_khoangcachdiem(info["x"], info["y"]) > self._khoangcachsudungkynangtamxa:
                        continue
                    is_nhuong = True
                    break

        self._bonhonhuongbuffdaohoanguyen = (time.time(), is_nhuong)
        return is_nhuong

    def _thusudungkhaithientichdia(self, idtuthenhanvat, x_dich, y_dich):
        # Đang di chuyển xa đích > 3 ô và nội lực trên mức % đặt ở giao diện thì dùng chiêu lướt về phía đích: Thục Sơn Khai Thiên Tịch
        # Địa (nhắm thẳng đích), Côn Luân Đằng Vân Giá Vũ (dịch chuyển tới điểm chọn trong tầm đánh xa: đích xa hơn thì nhắm điểm trên
        # đường thẳng tới đích, cách bản thân tầm xa - 0.5 ô). Trả về True khi đã dùng
        tenmonphai = self.moitruong.get_tenmonphai()
        chieuluot = {"thucson": VITRIKYNANG_KHAITHIENTICHDIA, "conluan": VITRIKYNANG_DANGVANGIAVU}.get(tenmonphai)
        if idtuthenhanvat != TUTHENHANVAT_DICHUYEN or not chieuluot or self.moitruong.get_phantramnoilucconlai() <= self._phantramnoiluckhaithientichdia:
            return False
        if not x_dich or not y_dich:
            return False
        toado = self.moitruong.get_toado()
        khoangcach = math.dist(toado, (x_dich, y_dich))
        if khoangcach <= 3.:
            return False
        if tenmonphai == "conluan" and khoangcach > self._khoangcachsudungkynangtamxa - 0.5:
            tile = (self._khoangcachsudungkynangtamxa - 0.5) / khoangcach
            x_dich, y_dich = toado[0] + (x_dich - toado[0]) * tile, toado[1] + (y_dich - toado[1]) * tile

        is_khaithiensansang = self.moitruong.get_is_kynangsansang(chieuluot) and self._is_dutieuhao(chieuluot)
        if self._is_khaithientichdiasansang and not is_khaithiensansang:
            # Vừa ra chiêu: tạm ngưng di chuyển 0.5s như bản cũ, vào tư thế xuất chiêu thì ngắt tiếp (action_ngatdichuyenkhixuatchieu)
            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
            self._thoidiemhetchongatdichuyen = time.time() + THOIGIANCHONGATDICHUYENXUATCHIEU

        self._is_khaithientichdiasansang = is_khaithiensansang

        if not is_khaithiensansang:
            return False

        if self._solanthatbaikhaithien >= self._solanthatbaikhaithientoida and time.time() - self._thoidiembiphatkhaithien > 3.0:
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
                return True
        return False

    def action_xulyuutiensudungkynang(self, loaikynang, vitrikynang, diachimuctieu, khoangcachyeucau = 0, is_yeucaukhongdichuyen = False, is_ngatdichuyen = False):
        thoidiemhientai = time.time()
        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        thoigiandungim = 0.
        if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
            thoigiandungim = thoidiemhientai - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0.

        # Đang lùi giữ khoảng cách với kẻ tấn công: bỏ chiêu đánh, phủ đầu, mọi bước tiếp cận và Lôi Động Cửu Thiên (vận khí đứng yên 6s),
        # chỉ còn buff / hồi máu / triệu hồi... để "buff xong chạy". Trả về (False, False) để thử kỹ năng tiếp theo trong danh sách
        if self._yeucaugiukhoangcach and (loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynangphudau")
                                          or loaikynang.startswith("dichuyen") or vitrikynang == VITRIKYNANG_LOIDONGCUUTHIEN):
            return False, False

        if loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynanglendongdoi"):
            if khoangcach <= khoangcachyeucau:
                khoangcachthucteyeucau = khoangcachyeucau
                # Buff lên đồng đội (Tiểu Chu Thiên, Hộ Thể Kim Cang...) không cần bù khoảng cách: trong tầm là buff, không chạy lại gần
                if loaikynang != "sudungkynanglendongdoi" and (thoigiandungim > 0.5 or (idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self._is_dangchaybukhoangcach)):
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
                        "khoangcachtoida": max(0, khoangcachthucteyeucau - 1.)
                    }
                    return False, True
                else:
                    self._is_dangchaybukhoangcach = False
            else:
                self._is_dangchaybukhoangcach = False
                return False, False

        if thoidiemhientai - self.moitruong.thoidiembatchucnangmoronggannhat < 0.5 or thoidiemhientai - self.moitruong.thoidiemtatchucnangmoronggannhat < 0.5:
            return False, True

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
                    "khoangcachtoida": max(0, khoangcachyeucau - 1.),
                }
            else:
                # Ghi nhớ tầm thực sự đánh được (tầm xa trừ hao TRUHAOTAMXACHONMUCTIEU, xem hangso) để lọc mục tiêu quanh trưởng nhóm
                self._khoangcachvoitoimuctieu = KHOANGCACHSUDUNGKYNANGCANCHIEN if loaikynang == "dichuyentiepcancanchien" else max(KHOANGCACHSUDUNGKYNANGCANCHIEN, khoangcachyeucau - TRUHAOTAMXACHONMUCTIEU)
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    # Tầm xa chỉ cần chạy vào trong tầm đã bù (BUKHOANGCACHTAMXA) và dư 1 ô, không chạy sát mục tiêu
                    "khoangcachtoida": max(0, KHOANGCACHSUDUNGKYNANGCANCHIEN - 1.) if loaikynang == "dichuyentiepcancanchien" else max(0, khoangcachyeucau - BUKHOANGCACHTAMXA - 1.),
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
                is_dasudung = self.moitruong.action_sudungkynangvitrimuctieu(vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu)
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
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    "khoangcachtoida": khoangcachyeucau
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
        # Người chơi đang giữ chuột kéo nhân vật đi: không chặn / xoá lệnh đi của người chơi, bỏ luôn các hạn chờ ngắt đang treo
        if self.moitruong.get_is_dangclickchuottrai():
            self._thoidiemhetchantudichuyentruocxuatchieu = 0.
            self._thoidiemhetchongatdichuyen = 0.
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

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0

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

        danhsachuutien = [
            (VITRIKYNANG_ANTHANTHUAT, "sudungkynangkhongmuctieu", lambda: not is_anthan and diachimuctieu and is_muctieutienthanvodich and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(VITRIKYNANG_BISAT), 0, None, False),
            (VITRIKYNANG_BISAT, "sudungkynangmuctieu", lambda: is_anthan and diachimuctieu and is_muctieutienthanvodich and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: not is_anthan and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5 and time.time() - self._thoidiemsudungnhiephonchamgannhat < 1., 0, None, False),
            (None, "dichuyengiukhoangcach", lambda: not is_bidaohoalacanh and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5 and (time.time() - self._thoidiemsudungmatamthuatgannhat < 0.5 or time.time() - self._thoidiemsudungamkichgannhat < 0.5 or time.time() - self._thoidiemsudungthichsatgannhat < 0.5), khoangcach + 3., None, False),
            (VITRIKYNANG_LACTUYETVONGAN, "sudungkynangkhongmuctieu", lambda: not is_anthan and diachimuctieu and is_muctieupk and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACTUYETVONGAN,), True, is_hieuungcoloi = 1), 0, None, False),
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: not is_anthan and diachimuctieu and khoangcach > self._khoangcachsudungkynangtamxa, 0, None, False),
            (VITRIKYNANG_NHIEPHONCHAM, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and is_muctieupk and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvat = diachimuctieu), self._khoangcachsudungkynangtamxa, None, True),
            (None, "tancongvatly", lambda: diachimuctieu and not self._is_battudongtancongvatly, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and self._is_nhieumuctieugan5 and not is_muctieupk, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_SONGLONGDOATCHAU, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and (is_muctieupk or is_bandochientruong or self._is_tudongdichuyendiemdanhxungquanh) and not is_muctieucomatamthuat, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and self._is_nhieumuctieugan5 and is_muctieupk, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and is_muctieulanguoichoi and is_muctieusudungphapluc and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HAPTINHMACHAM,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_MAIHOACHAM, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_AMKICH, "sudungkynangmuctieu", lambda: not is_bidaohoalacanh and diachimuctieu and not is_muctieucomatamthuat and (is_muctieugiukhoangcach or is_bituocvukhi), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() != BANDO_TIVO and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 30. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), self._khoangcachsudungkynangtamxa, None, False),
            (VITRIKYNANG_THICHSAT, "sudungkynangmuctieu", lambda: not is_bidaohoalacanh and diachimuctieu and not is_muctieucomatamthuat and (is_muctieugiukhoangcach or is_bituocvukhi), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "dichuyengiukhoangcach", lambda: not is_bidaohoalacanh and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5, khoangcach + 3., None, False),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: not is_bituocvukhi and diachimuctieu, self._khoangcachsudungkynangtamxa, None, True),
            (None, "tancongvatly", lambda: diachimuctieu, self._khoangcachsudungkynangtamxa, None, True),
            (None, "dichuyentiepcantamxa", lambda: not is_bidaohoalacanh and diachimuctieu and khoangcach > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, False),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen = item

            if callable(dieukien) and not dieukien():
                continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang):
                continue

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

    def action_sudungkynangmonphaidaohoanguyen(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = self.moitruong.get_is_nguoichoi(diachimuctieu)
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0

        diachidongdoicanbuff = None
        if not diachimuctieu and self.moitruong.get_is_dangnamtrongnhom():
            diachidongdoicanbuff = self._diachidoituongcanbuffhothekimcangdaohoanguyen

        is_anhhuongboimuctieutheosau = bool(self._laytoadomuctieutheosau())
        is_nhuongbuff = self._is_nhuongbuffdaohoanguyen()
        is_cancanchien = bool(diachimuctieu) and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN
        idloaivukhimuctieu = self.moitruong.get_idloaivukhi(diachimuctieu) if diachimuctieu and is_muctieulanguoichoi else None
        nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai() or 0
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
            # Kim Chung Tráo: game không cho dùng khi đang Dã Tính nên bỏ qua lúc đó
            (VITRIKYNANG_KIMTRUNGCHAO, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), True, is_hieuungcoloi = 1) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMTRUNGCHAO,), True, is_hieuungcoloi = 1), 0, None, False, False),
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglenbanthan", lambda: not is_nhuongbuff and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), True, is_hieuungcoloi = 1), 0, None, False, False),
            # Nguyên Khí Quy Nguyên: bật / làm mới theo tin server ở _lammoinguyenkhiquynguyen (gọi trước danh sách)
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglendongdoi", lambda: diachidongdoicanbuff and not is_nhuongbuff, self._khoangcachsudungkynangtamxa, diachidongdoicanbuff, False, False),
            # "kill" chỉ bật Tự Động Công Kích lên mục tiêu (không phải kỹ năng): gửi được từ xa, máy chủ giữ lệnh cả khi di chuyển và chỉ
            # đánh khi đã ở gần. Đánh thường làm chiêu ra chậm hẳn nên chỉ bật khi gần hết nguyên khí (NGUYENKHITANCONGVATLYDAOHOA), còn
            # nguyên khí thì spam chiêu. Gửi 1 lần mỗi mục tiêu, THOIGIANGUILAITANCONGVATLY giây gửi lại cho chắc
            (None, "tancongvatly", lambda: diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa and nguyenkhiconlai <= NGUYENKHITANCONGVATLYDAOHOA, self._khoangcachsudungkynangtamxa + BUKHOANGCACHTAMXA, None, False, False),
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
        if nguyenkhiconlai >= NGUYENKHINGATTANCONGVATLYDAOHOA:
            self._ngattancongvatlydaohoa(diachimuctieu)

        for i, item in enumerate(danhsachuutien):
            # Phần tử thứ 8 (nếu có): hiệu ứng khống chế chiêu này gây ra, giữ chỗ giữa các bot để không cùng gửi lên 1 mục tiêu
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen, is_ngatdichuyen, *phu = item
            hieuunggiucho = phu[0] if phu else None

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang): continue

            # Trấn Cổ Thần Uy chỉ ra chiêu khi đang di chuyển: đứng im thì nhích rồi kết thúc lượt
            # (các kỹ năng cận chiến phía sau có ngắt di chuyển, sẽ huỷ cú nhích), lượt sau đang di chuyển mới gửi
            # Điều kiện của Trấn Cổ Thần Uy đã đòi có mục tiêu (không buff khi đứng chờ, theo sau, trong thành)
            if vitrikynang in VITRIKYNANGCANNHICHDAOHOANGUYENs and self.moitruong.get_idtuthenhanvat() != TUTHENHANVAT_DICHUYEN:
                if self._nhichdedungkynang(vitrikynang, diachimuctieu):
                    return
                continue

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
        return (hieuung, idmuctieu), True

    def _bogiuchokynangphai(self, giucho):
        if giucho:
            self._bogiukynangmuctieu(*giucho)

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

    def _nhichdedungkynang(self, vitrikynang, diachimuctieu):
        # Đang đứng im mà cần dùng kỹ năng chỉ ra chiêu khi di chuyển => nhích một chút: đứng trùng ô quái (hoặc không có mục tiêu)
        # thì ra 1 ô bên cạnh, đứng cạnh quái thì xuyên qua sang ô đối diện (vẫn sát quái để đánh cận chiến)
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemnhichgannhat < THOIGIANGIUAHAILANNHICH:
            return False
        if self.moitruong.get_idtuthenhanvat() != TUTHENHANVAT_DUNGIM:
            return False
        # Kỹ năng đang bị khoá (chống spam / khoá kỹ năng lúc triệu hồi bảo thú) thì lượt sau cũng không gửi được, nhích vô ích
        idkynang = self.moitruong.get_idkynang(vitrikynang)
        if not idkynang or self.moitruong.get_is_kynangdangbikhoa(idkynang):
            return False

        x, y = self.moitruong.get_toado()
        xquai, yquai = self.moitruong.get_toado(diachimuctieu) if diachimuctieu else (x, y)
        if (x, y) == (xquai, yquai):
            dx, dy = random.choice(((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)))
            xdich, ydich = x + dx, y + dy
        else:
            xdich, ydich = 2 * xquai - x, 2 * yquai - y
        if self._kiemtra_divaovungcam(xdich, ydich):
            return False

        self._thoidiemnhichgannhat = thoidiemhientai
        is_ok = self.moitruong.action_dichuyengiukhoangcachtoidadiem(xdich, ydich, 0, delay = 0.)
        if IS_LOGCAULENH:
            self.moitruong._inlog(f"[NHÍCH] để dùng kỹ năng ô {vitrikynang}: ({x}, {y}) -> ({xdich}, {ydich}){'' if is_ok else ' (không đi được)'}")
        return is_ok

    def action_sudungkynangmonphaicamvequan(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai()
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        is_bandochientruong = self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG

        danhsachuutien = [
            (VITRIKYNANG_MANHHOBOPHAP, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MANHHOBOPHAP,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_KIMSUBOGIAP, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMSUBOPHAP,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_SINHTUTHANLUC, "sudungkynangkhongmuctieu", lambda: diachimuctieu and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_SINHTUTHANLUC,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_LUANHOIVANCHUYEN, "sudungkynangkhongmuctieu", lambda: diachimuctieu and nguyenkhiconlai < 4 and self.moitruong.get_phantramsinhlucconlai() <= 65, 0, None, True),
            (VITRIKYNANG_PHILONGTAMCHAU, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self._khoangcachsudungkynangtamxa / 2 <= khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, False),
            (VITRIKYNANG_THIENLYTATSAT, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self._khoangcachsudungkynangtamxa / 2 <= khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, False),

            (VITRIKYNANG_HOANHTAOTHIENQUAN, "sudungkynangkhongmuctieu", lambda: not is_bandochientruong and diachimuctieu and not is_muctieulanguoichoi and self._is_nhieumuctieugan3, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_CHANTHIENNOHONG, "sudungkynangkhongmuctieu", lambda: not is_bandochientruong and diachimuctieu and is_muctieulanguoichoi and self._is_nhieumuctieugan3, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "tancongvatly", lambda: diachimuctieu and not self._is_battudongtancongvatly, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_NGULOIAPDINH, "sudungkynangmuctieu", lambda: is_bandochientruong and diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_TRUCDAOHOANGLONG, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_THIENBONGNHATKICH, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu and is_muctieulanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_LOIDINHKICH, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_BADAONOLANG, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_GIAOLONGNHAPHAI, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False),
            (None, "tancongvatly", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
        ]

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
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        tamxa = self._khoangcachsudungkynangtamxa

        # Không đánh thường: Côn Luân đánh thường chỉ 1-2 máu (người dùng bỏ 2026-10-29), hết pháp lực / chiêu đang hồi thì đứng chờ
        danhsachuutien = [
            # Tâm pháp bật / tắt: chỉ bấm khi chưa có hiệu ứng, gửi 1 lần rồi chờ hiệu ứng hiện (_is_duocguitamphapbattat gọi cuối)
            (VITRIKYNANG_CANKHONNADI, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CANKHONNADI,), macdinh = True, is_hieuungcoloi = 1)
                and self._is_duocguitamphapbattat(VITRIKYNANG_CANKHONNADI), 0, None, False),
            # Hỏa Long Quyết (3 Bùa Giấy): gây Thiêu Đốt 12s, mục tiêu đang bị Thiêu Đốt thì để chiêu khác
            (VITRIKYNANG_HOALONGQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and (self.moitruong.get_soluongvatphamhanhtrangtheoten() or {}).get(BUAGIAY, 0) >= 3
                and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), tamxa, None, True),
            (VITRIKYNANG_NGULOITHUAT, "sudungkynangmuctieu", lambda: diachimuctieu and self.moitruong.action_timkiemvatphamhanhtrang(BUAGIAY), tamxa, None, True),
            (VITRIKYNANG_PHONGHOAQUYET, "sudungkynangmuctieu", lambda: diachimuctieu, tamxa, None, True),
            (None, "dichuyentiepcantamxa", lambda: diachimuctieu and khoangcach > tamxa, tamxa, None, False),
        ]

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

    def _get_tenbaothukynangtrieuhois(self):
        return [ten for ten, _ in self._get_baothukynangtrieuhois()]

    def _get_phantramsinhlucthapnhatthanhviennhomgan(self, khoangcachtoida):
        # % sinh lực thấp nhất của thành viên nhóm (không tính bản thân) còn sống trong khoangcachtoida ô; không có ai thì None
        if not self.moitruong.get_is_dangnamtrongnhom():
            return None
        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
        idnguoichoi = self.moitruong.get_idnguoichoi()
        phantramthapnhat = None
        j = -1
        while True:
            j += 1
            addr = self.moitruong.get_diachicosothongtindoituongx(j)
            if not addr:
                return phantramthapnhat
            if not self.moitruong.get_is_nhanvattontai(addr) or self.moitruong.get_is_nhanvatdachet(addr):
                continue
            id_nd = self.moitruong.get_idnguoichoi(addr)
            if id_nd in idnguoichoithanhviennhoms and id_nd != idnguoichoi and self.moitruong.get_khoangcach(addr) <= khoangcachtoida:
                phantram = self.moitruong.get_phantramsinhlucconlai(addr)
                if phantramthapnhat is None or phantram < phantramthapnhat:
                    phantramthapnhat = phantram

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
        if self.moitruong.get_is_khoavankhitrieuhoi():
            if self._bodotruoctrieuhoi is None:
                if self.moitruong.get_tenmonphai() != "maoson" or not self._is_doidokhitrieuhoi or not self._bodotrieuhoi:
                    return
                self._bodotruoctrieuhoi = self._laybotrangbi()
                self._solanmaclaitrieuhoi = 0
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
        if time.time() - self._thoidiemdoidotrieuhoigannhat < giancachmaclai:
            return
        self._hangdoideodotrieuhoi = []
        hientai = self._laybotrangbi()
        # Ô trang bị đang mặc món khác lúc trước triệu hồi (trước đó trống thì không tháo được, bỏ qua)
        khacs = [(vitri, idcu, tencu) for vitri, (idcu, tencu) in self._bodotruoctrieuhoi.items() if idcu and hientai[vitri][0] != idcu]
        if not khacs or self._solanmaclaitrieuhoi >= solanmaclaitoida:
            if khacs:
                print("{}: không mặc lại được sau triệu hồi: {}".format(self.moitruong.get_tendoituong(), ", ".join(ten for _, _, ten in khacs)))
                phatam("Không mặc lại được đồ sau triệu hồi")
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
        self.moitruong.action_khoavankhitrieuhoi(caulenhduocpheps = ("pf {}".format(idkynang),) if idkynang else ())
        self._yeucautancong = None

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
        # Đang vận khí Lôi Động Cửu Thiên (vào vận khí 0-1s sau khi ra chiêu, kéo dài 6s) mà mục tiêu đã ra ngoài phạm vi 7x7
        # và quanh bản thân không còn cụm quái nào thì ngắt luôn (cho di chuyển / dùng chiêu khác), không chờ hết vận khí.
        # Gọi khi game đang báo vận khí; trả về True thì coi như không vận khí
        if self.moitruong.get_tenmonphai() != "maoson":
            return False
        # Đang vận khí triệu hồi bảo thú thì tuyệt đối không ngắt
        if self.moitruong.get_is_khoavankhitrieuhoi():
            return False
        if time.time() - self._thoidiemsudungloidongcuuthiengannhat > THOIGIANVANKHILOIDONGCUUTHIEN + 1.5:
            return False
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachimuctieu or self.moitruong.get_khoangcach(diachimuctieu) <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN + 0.5:
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
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0

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
        # Mệnh Tế / Huyết Tế: người cần hồi dưới 25% máu thì tế mọi bảo thú triệu hồi,
        # dưới 50% máu thì chỉ tế khi bảo thú triệu hồi không phải Cương Thi / Thần Tướng
        is_khongphaicuongthithantuong = is_cobaothukynangtrieuhoi and all(
            not ten.startswith((CUONGTHI.lower(), THANTUONG.lower())) for ten, _ in baothukynangtrieuhois)
        is_cantebaothu = lambda phantram: is_cobaothukynangtrieuhoi and (phantram < 25 or (phantram < 50 and is_khongphaicuongthithantuong))
        # Thành viên nhóm thấp máu nhất trong 21x21 ô (None: không có ai): Mệnh Tế hồi cả nhóm nên xét cả máu của họ
        phantramthanhviennhomgan = self._get_phantramsinhlucthapnhatthanhviennhomgan(KHOANGCACHHIEUQUAMENHTE) if is_cobaothukynangtrieuhoi else None
        is_cothanhviennhomgan = phantramthanhviennhomgan is not None
        kynangchopheps = self._get_kynangchophep()
        # Bật xoay vòng chiêu có mục tiêu, mục tiêu là quái: bỏ Phục Ma Quyết (phải chờ lượt), đánh bằng Lôi Động Cửu Thiên (không mục tiêu,
        # không chờ lượt) dù chỉ 1 mục tiêu, xa quá thì chạy lại gần. Mục tiêu là người chơi (PK) thì không chạy vào sát, vẫn dùng Phục Ma Quyết
        is_xoayvongchieu = self.moitruong.get_is_batxoayvongchieu() and not is_muctieulanguoichoi

        danhsachuutien = [
            # Bảo thú triệu hồi sắp chết (dưới PHANTRAMSINHLUCTETHANTUONG% sinh lực) thì Tế Thần Tướng (120 pháp lực, hồi 180s): hy sinh nó để gọi Thần Tướng
            # Tế Thần Tướng chỉ có từ cấp CAPDOTOITHIEUTETHANTUONG: cấp thấp chưa học mà game vẫn báo ô kỹ năng sẵn sàng nên bị spam liên tục
            (VITRIKYNANG_TETHANTUONG, "sudungkynangkhongmuctieu", lambda: is_cobaothusaphet and self.moitruong.get_capdonhanvat() >= CAPDOTOITHIEUTETHANTUONG, 0, None, True, True),
            # Máu thấp (xem is_cantebaothu) thì tế khí huyết bảo thú:
            #   có thành viên nhóm trong 21x21 ô thì Mệnh Tế (150 pháp lực: 25% khí huyết bảo thú hồi cho cả nhóm), xét bản thân hoặc thành viên đó thấp máu
            #   không thì Huyết Tế (100 pháp lực: hy sinh 50% khí huyết bảo thú hồi cho bản thân)
            (VITRIKYNANG_MENHTE, "sudungkynangkhongmuctieu", lambda: is_cothanhviennhomgan and is_cantebaothu(min(phantramsinhlucconlai, phantramthanhviennhomgan)), 0, None, True, True),
            (VITRIKYNANG_HUYETTE, "sudungkynangkhongmuctieu", lambda: not is_cothanhviennhomgan and is_cantebaothu(phantramsinhlucconlai), 0, None, True, True),
            # Chưa có bảo thú triệu hồi thì gọi bảo thú theo lựa chọn _baothutrieuhoimaoson; chờ 3s sau mỗi lần gọi để bảo thú kịp xuất hiện
            #   Tự động: có Cương Thi Phù trong hành trang thì ưu tiên gọi Cương Thi,
            #   không thì gọi Thiên Binh (3 Bùa Giấy). Pháp lực / khí huyết / nguyên khí đủ hay chưa thì _is_kynangdungduoc xét theo mô tả trong game
            (VITRIKYNANG_TRIEUHOICUONGTHI, "sudungkynangkhongmuctieu", lambda: self._baothutrieuhoimaoson in (BAOTHUTRIEUHOI_TUDONG, CUONGTHI) and not is_cobaothukynangtrieuhoi and time.time() - self._thoidiemtrieuhoibaothugannhat > 3. and self.moitruong.action_timkiemvatphamhanhtrang(CUONGTHIPHU), 0, None, True, True),
            (VITRIKYNANG_TRIEUHOITHIENBINH, "sudungkynangkhongmuctieu", lambda: self._baothutrieuhoimaoson in (BAOTHUTRIEUHOI_TUDONG, THIENBINH) and not is_cobaothukynangtrieuhoi and time.time() - self._thoidiemtrieuhoibaothugannhat > 3. and self.moitruong.action_timkiemvatphamhanhtrang(BUAGIAY), 0, None, True, True),
            # Quỷ Tốt cũng chỉ cần Bùa Giấy
            (VITRIKYNANG_TRIEUHOIQUYTOT, "sudungkynangkhongmuctieu", lambda: self._baothutrieuhoimaoson == QUYTOT and not is_cobaothukynangtrieuhoi and time.time() - self._thoidiemtrieuhoibaothugannhat > 3. and self.moitruong.action_timkiemvatphamhanhtrang(BUAGIAY), 0, None, True, True),
            (VITRIKYNANG_HUYETMACHU, "sudungkynangkhongmuctieu", lambda: phantramsinhlucconlai > 25 and phantramnoilucconlai <= 50, 0, None, True, False),
            (VITRIKYNANG_THANTUEPHAPCHU, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THANTUEPHAPCHU,), macdinh = True, is_hieuungcoloi = 1), 0, None, True, False),

            (VITRIKYNANG_AMMANHAPTHE, "sudungkynangmuctieu", lambda: diachiammanhapthe, self._khoangcachsudungkynangtamxa, diachiammanhapthe, True, True),
            (VITRIKYNANG_THUCCOT, "sudungkynangmuctieu", lambda: diachithuccot, self._khoangcachsudungkynangtamxa, diachithuccot, True, True),
            (VITRIKYNANG_THUCGIAP, "sudungkynangmuctieu", lambda: diachithucgiap, self._khoangcachsudungkynangtamxa, diachithucgiap, True, True),
            (VITRIKYNANG_THUCTAM, "sudungkynangmuctieu", lambda: diachithuctam, self._khoangcachsudungkynangtamxa, diachithuctam, True, True),

            # Di Tinh Đại Pháp hồi nội lực bảo thú triệu hồi: nghỉ GIANCACHHOIBAOTHUTRIEUHOI giây cho nội lực bảo thú kịp cập nhật, còn lại theo hồi chiêu game.
            # Lưu Huyết Thuật hồi máu dần trong 8 giây: chỉ dùng lại sau GIANCACHLUUHUYETTHUAT giây (lần trước đã hồi xong), không phí pháp lực
            (VITRIKYNANG_DITINHDAIPHAP, "sudungkynangkhongmuctieu", lambda: time.time() - self._thoidiemsudungditinhdaiphapgannhat > GIANCACHHOIBAOTHUTRIEUHOI and self._is_baothukynangtrieuhoihetnoiluc, 0, None, True, True),
            (VITRIKYNANG_LUUHUYETTHUAT, "sudungkynangkhongmuctieu", lambda: time.time() - self._thoidiemsudungluuhuyetthuatgannhat > GIANCACHLUUHUYETTHUAT and self._is_baothukynangtrieuhoihetsinhluc, 0, None, True, True),

            (VITRIKYNANG_LOIDONGCUUTHIEN, "sudungkynangkhongmuctieu", lambda: diachimuctieu and self._is_nhieumuctieuganbanthan3 and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, None, True, True),
            (VITRIKYNANG_LOIDONGCUUTHIEN, "sudungkynangkhongmuctieu", lambda: is_xoayvongchieu and diachimuctieu and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, None, True, True),
            (VITRIKYNANG_LOIDONGCUUTHIEN, "dichuyentiepcandenkhoangcach", lambda: is_xoayvongchieu and diachimuctieu and khoangcach > KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHTIEPCANLOIDONGCUUTHIEN, None, False, False),
            # Lôi Động Cửu Thiên đánh quanh bản thân 3 ô: có cụm quái quanh mục tiêu (đánh quái, không PK)
            # thì chạy vào sát mục tiêu (giữa cụm) để lượt sau ra chiêu trúng cả cụm
            (VITRIKYNANG_LOIDONGCUUTHIEN, "dichuyentiepcandenkhoangcach", lambda: diachimuctieu and not is_muctieulanguoichoi and self._is_nhieumuctieugan3 and khoangcach > KHOANGCACHTIEPCANLOIDONGCUUTHIEN, KHOANGCACHTIEPCANLOIDONGCUUTHIEN, None, False, False),
            (VITRIKYNANG_PHUCMAQUYET, "sudungkynangmuctieu", lambda: not is_xoayvongchieu and diachimuctieu and khoangcach <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True, True),

            (None, "dichuyentiepcantamxa", lambda: diachimuctieu and khoangcach > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, False, False),
        ]

        self._capnhatkynangquantrong("maoson", danhsachuutien, kynangchopheps)

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen, is_ngatdichuyen = item
            if vitrikynang and kynangchopheps is not None and vitrikynang not in kynangchopheps:
                continue
            if callable(dieukien) and not dieukien():
                continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang):
                continue
            target_use = target if target else diachimuctieu
            # Bot khác cùng máy vừa gửi cùng chiêu (Thực Cốt / Thực Giáp / Thực Tâm) lên mục tiêu này thì dùng chiêu tiếp theo
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
                self.moitruong.action_chovankhi(THOIGIANCHOVAOVANKHI)
                self._thoidiemsudungloidongcuuthiengannhat = time.time()
            if vitrikynang in (VITRIKYNANG_TRIEUHOICUONGTHI, VITRIKYNANG_TRIEUHOITHIENBINH, VITRIKYNANG_TRIEUHOIQUYTOT) and is_ok:
                self._thoidiemtrieuhoibaothugannhat = time.time()
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
        khoangcachmuctieutancong = self.moitruong.get_khoangcach(diachimuctieu)
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
            (VITRIKYNANG_PHONGANTHUAT, "sudungkynangmuctieu", lambda: diachidoituongcanbuffphonganthuat and self.moitruong.get_khoangcach(diachidoituongcanbuffphonganthuat) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffphonganthuat, True),
            (VITRIKYNANG_HUYENQUANGTHIEMANH, "sudungkynangmuctieu", lambda: diachidoituongcanbuffhuyenquangthiemanh and self.moitruong.get_khoangcach(diachidoituongcanbuffhuyenquangthiemanh) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffhuyenquangthiemanh, True),

            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() not in (BANDO_TIVO, BANDO_CHIENTRUONG) and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 5. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), self._khoangcachsudungkynangtamxa, None, False),
            (VITRIKYNANG_TOANPHONGQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa and self.moitruong.get_phantramsinhlucconlai(diachimuctieu) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 1), self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_CAITUHOANSINH, "sudungkynanglendongdoi", lambda: diachidoituongcanhoisinh and self.moitruong.get_khoangcach(diachidoituongcanhoisinh) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanhoisinh, True),
            (VITRIKYNANG_TAYTRANQUYET, "sudungkynanglendongdoi", lambda: diachidoituongcanbufftaytranquyet and self.moitruong.get_khoangcach(diachidoituongcanbufftaytranquyet) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbufftaytranquyet, True),
            (VITRIKYNANG_CAMLOTRI, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcach(diachidoituongcanbommau) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbommau, True),
            (VITRIKYNANG_KHIETVANQUYET, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongkhietvanquyet and self.moitruong.get_khoangcach(diachidoituongkhietvanquyet) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongkhietvanquyet, True),
            (VITRIKYNANG_SOTRI, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcach(diachidoituongcanbommau) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbommau, True),
            (VITRIKYNANG_VODINHLUUTHUY, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcach(diachidoituongcanbommau) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbommau, True),
            (VITRIKYNANG_TAYTRANQUYET, "sudungkynanglendongdoi", lambda: diachidoituongcanbufftaytranquyet2 and self.moitruong.get_khoangcach(diachidoituongcanbufftaytranquyet2) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbufftaytranquyet2, True),
            (VITRIKYNANG_NGANCHAMDOACH, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffngancham and self.moitruong.get_khoangcach(diachidoituongcanbuffngancham) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffngancham, True),
            (VITRIKYNANG_KIMCHAMDOACH, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffkimcham and self.moitruong.get_khoangcach(diachidoituongcanbuffkimcham) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffkimcham, True),
            (VITRIKYNANG_CUONGTHETHUAT, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffcuongthethuat and self.moitruong.get_khoangcach(diachidoituongcanbuffcuongthethuat) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbuffcuongthethuat, True),

            (None, loaitiepcan, lambda: diachicantiepcan and self.moitruong.get_khoangcach(diachicantiepcan) > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachicantiepcan, False),

            (VITRIKYNANG_DONGIAPTRAN, "sudungkynangphudau", lambda: diachimuctieu and is_contranky and phantramnoiluc > 25 and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa, khoangcachmuctieutancong + random.choice([-1, 1]), None, True),
            (VITRIKYNANG_KYMONTRAN, "sudungkynangphudau", lambda: diachimuctieu and is_contranky and phantramnoiluc > 25 and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa, khoangcachmuctieutancong + random.randint(0, 0), None, True),
            (VITRIKYNANG_LIETPHONGQUYET, "sudungkynangmuctieu", lambda: not is_xoayvongchieu and not is_dangbatpk and diachimuctieu and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, None, True),
            (VITRIKYNANG_PHONGVUKINHTHIEN, "sudungkynangmuctieu", lambda: is_xoayvongchieu and not is_dangbatpk and diachimuctieu and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa
                and time.time() - self._thoidiemphongvukinhthien_map.get(idmuctieu, 0.) >= THOIGIANPHONGVUKINHTHIEN, self._khoangcachsudungkynangtamxa, None, True),
            # (None, "tancongvatly", lambda: diachimuctieu and khoangcachmuctieutancong <= self._khoangcachsudungkynangtamxa and (not self._is_battudongtancongvatly or time.time() - self.moitruong._thoidiemsudungtancongvatlygannhat > 5.), self._khoangcachsudungkynangtamxa, None, True),

            (VITRIKYNANG_LINHKHIHOTHE, "sudungkynanglendongdoi", lambda: diachidoituongcanbufflinhkhihothe and self.moitruong.get_khoangcach(diachidoituongcanbufflinhkhihothe) <= self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachidoituongcanbufflinhkhihothe, True),
            (None, "dichuyengiukhoangcach", lambda: diachimuctieu and is_muctieugiukhoangcach and khoangcachmuctieutancong <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5, khoangcachmuctieutancong + 3., None, False),

            (None, loaitiepcan, lambda: diachicantiepcan and self.moitruong.get_khoangcach(diachicantiepcan) > self._khoangcachsudungkynangtamxa, self._khoangcachsudungkynangtamxa, diachicantiepcan, False),
        ]

        self._capnhatkynangquantrong("vanmongcoc", danhsachuutien)

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
        self._yeucautancong = None

        if self._is_battudongtancongvatly and self.moitruong.get_is_nhanvatbichoang():
            self._is_battudongtancongvatly = False

        if self._trangthaiveban != 0:
            return

        if self._is_danggomquai:
            return

        if self._is_danguutiennhatdo:
            return

        if self.moitruong.get_is_nhanvatchuasansang(self.moitruong.get_diachicosothongtinnhanvat1()):
            return
        if time.time() - self._thoidiemtamngungsudungkynang < 0.:
            return

        tenmonphai = self.moitruong.get_tenmonphai()

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

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu)
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

    def action_sudungkynangmonphaithucson(self):
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
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
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
                if self.moitruong.get_khoangcach(addr) > self._khoangcachsudungkynangtamxa:
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
        self._is_khongcongidebuff = not diachidongdoicanbuff
        is_tieuchuthiensansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_TIEUCHUTHIEN)
        if self._is_tieuchuthiensansang and not is_tieuchuthiensansang and self._idnguoichoibuffnoikhanggannhat:
            self._thoidiembuffnoikhanggannhat_map[self._idnguoichoibuffnoikhanggannhat] = time.time()
            self._thoidiembuffnoikhanggannhat_map = donbangthoidiem(self._thoidiembuffnoikhanggannhat_map, 120.)
        self._is_tieuchuthiensansang = is_tieuchuthiensansang

        capdonhanvat = self.moitruong.get_capdonhanvat()

        noilucconlai = self.moitruong.get_noilucconlai()
        is_bituocvukhi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, is_hieuungcoloi = 0)
        is_ngukiemdudieukien = capdonhanvat > 35 and diachimuctieu and self._is_nhieumuctieugan9
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
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
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
                if self.moitruong.get_khoangcach(addr) > self._khoangcachsudungkynangtamxa: continue
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

        self._is_khongcongidebuff = not diachidongdoicanbuff
        is_tieuchuthiensansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_TIEUCHUTHIEN)
        if self._is_tieuchuthiensansang and not is_tieuchuthiensansang and self._idnguoichoibuffnoikhanggannhat:
            self._thoidiembuffnoikhanggannhat_map[self._idnguoichoibuffnoikhanggannhat] = time.time()
            self._thoidiembuffnoikhanggannhat_map = donbangthoidiem(self._thoidiembuffnoikhanggannhat_map, 120.)
        self._is_tieuchuthiensansang = is_tieuchuthiensansang

        if diachimuctieu and self.moitruong.get_is_cothetancong(diachimuctieu):
            if self._idmuctieuluutinhtruymang != diachimuctieu:
                self._idmuctieuluutinhtruymang = diachimuctieu
                self._solanthatbailuutinhtruymang = 0

            is_luutinhtruymangsansang = self.moitruong.get_is_kynangsansang(VITRIKYNANG_LUUTINHTRUYMANG)

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
            is_bimatamthuat = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MATAMTHUAT,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu)

            if khoangcach <= self._khoangcachsudungkynangtamxa and is_duocphepsudungluutinhtruymang and not is_bimatamthuat:
                self._yeucautancong = None
                if self.moitruong.action_sudungkynangvitrimuctieu(VITRIKYNANG_LUUTINHTRUYMANG):
                    # Gửi thẳng, không qua action_xulyuutiensudungkynang: tự đánh dấu chiêu cần đứng yên và chặn client tự bước từ lúc gửi
                    self.moitruong.set_is_chieucanngatdichuyen(True, diachimuctieu)
                    self._ghinhanchieuguivaomuctieu(diachimuctieu)
                    self._thoidiemhetchantudichuyentruocxuatchieu = time.time() + THOIGIANCHANTUDICHUYENTRUOCXUATCHIEU
                    self.moitruong.action_chandichuyen()
                    self._thoidiemtamngungluutinhtruymang = time.time()
                    self._solansudungluutinhtruymang += 1
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

        for vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngat in danhsachuutien:
            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self._is_kynangdungduoc(vitrikynang): continue

            is_ok, is_break = self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, target if target else diachimuctieu, khoangcachyeucau, is_ngat)
            if is_ok and vitrikynang == VITRIKYNANG_TIEUCHUTHIEN and target:
                self._idnguoichoibuffnoikhanggannhat = self.moitruong.get_idnguoichoi(target)
            if is_break:
                return
