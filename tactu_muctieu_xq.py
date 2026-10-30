# Phần mục tiêu: lọc / chọn mục tiêu (chung và theo môn phái), tầm nhìn chia sẻ giữa các cửa sổ, gom quái.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import time

from hangso_xq import *
from dexuatlotrinh_xq import taiviquai as util_taiviquai, luuviquai as util_luuviquai, taiviquaibando, ghinhanvitriquai, dexuatlotrinh
from dexuatlotrinh_xq import THOIGIANGHIVITRIQUAI, THOIGIANLUUVITRIQUAI, SOLANTHAYQUAITOITHIEU, TENMAUDEXUAT
from tienich_xq import laynhomtodoitudongs, laynhanvattodoitudongs, donbangthoidiem


class TacTuMucTieu:
    def _is_doituongthudich(self, diachidoituong, tenchunhanphe_map):
        # Đối tượng có thể đang đánh mình: quái hoặc người chơi / bảo thú không cùng phe.
        # Khác get_is_cothetancong (mình đánh được nó không): đang hoà bình thì người chơi PK vẫn đánh được mình
        if self.moitruong.get_is_nhanvatdachet(diachidoituong) or self.moitruong.get_is_npc(diachidoituong)                 or self.moitruong.get_is_baothuvatpham(diachidoituong):
            return False
        if self.moitruong.get_idloainhanvat(diachidoituong) == LOAIMUCTIEU_NGUOICHOICUNGNHOM:
            return False
        if self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG and self.moitruong.get_idphechientruong() == self.moitruong.get_idphechientruong(diachidoituong):
            return False
        if self.moitruong.get_is_baothukynangtrieuhoi(diachidoituong) or self.moitruong.get_is_baothugiangho(diachidoituong):
            tenchunhan = self.moitruong.get_tenchunhan(diachidoituong)
            if tenchunhan:
                if tenchunhan not in tenchunhanphe_map:
                    # Bảo thú của mình / đồng đội thì cùng phe; chủ nhân không ở gần thì coi như thù địch
                    diachichunhan = None if tenchunhan == self.moitruong.get_tendoituong() else self.moitruong.action_timkiemnhanvat(tennhanvat = tenchunhan)
                    tenchunhanphe_map[tenchunhan] = tenchunhan == self.moitruong.get_tendoituong() or bool(
                        diachichunhan and self.moitruong.get_idloainhanvat(diachichunhan) == LOAIMUCTIEU_NGUOICHOICUNGNHOM)
                if tenchunhanphe_map[tenchunhan]:
                    return False
        return True

    def get_tamnhinchiase(self):
        # Tầm nhìn của cửa sổ này để chia sẻ cho nhân vật khác cùng máy (ghi vào shared_data mỗi lượt cập nhật giao diện):
        # các đối tượng thù địch nó thấy, gần nhất trước. Mỗi phần tử: (id đối tượng, x, y, tư thế, hướng mặt, là mục tiêu PK, tên)
        # ID đối tượng do máy chủ cấp nên mọi cửa sổ thấy giống nhau (đã đo); tọa độ là tọa độ ô tuyệt đối trên bản đồ
        x1, y1 = self.moitruong.get_toado()
        tenchunhanphe_map = {}
        doituongs = []
        for diachi in self.moitruong._get_diachidoituongxungquanhs():
            if not self._is_doituongthudich(diachi, tenchunhanphe_map):
                continue
            x, y = self.moitruong.get_toado(diachi)
            is_muctieupk = self.moitruong.get_is_nguoichoi(diachi) or self.moitruong.get_is_baothukynangtrieuhoi(diachi) or self.moitruong.get_is_baothugiangho(diachi)
            doituongs.append((math.dist((x1, y1), (x, y)), (self.moitruong.get_iddoituong(diachi), x, y, self.moitruong.get_idtuthenhanvat(diachi),
                                                             self.moitruong.get_huongmat(diachi), bool(is_muctieupk), self.moitruong.get_tendoituong(diachi))))
        doituongs.sort(key = lambda d: d[0])
        # Ghi vị trí quái (không phải người chơi / bảo thú, không nằm trong danh sách không tấn công) để tự đề xuất lộ trình
        if self._idnguoichoiviquai and time.time() - self._thoidiemghiviquaigannhat >= THOIGIANGHIVITRIQUAI:
            self._thoidiemghiviquaigannhat = time.time()
            ghinhanvitriquai(self._bangviquai, self.moitruong.get_idbandohientai(),
                             [(d[1], d[2]) for _, d in doituongs if not d[5] and not self._is_tenbiboqua(d[6])])
        return {
            "thoidiem": time.time(),
            "bando": self.moitruong.get_idbandohientai(),
            "doituongs": [d[1] for d in doituongs[:SOLUONGTAMNHINTOIDA]],
        }

    def _laytamnhinchung(self):
        # Đối tượng thù địch mà nhân vật khác cùng máy, cùng bản đồ đang thấy (tầm nhìn còn mới): {id đối tượng: (x, y, tư thế, hướng, là PK, tên)}.
        # Đọc shared_data tốn 1 lần gọi qua Manager nên nhớ THOIGIANDOCTAMNHIN giây
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemdoctamnhinchunggannhat < THOIGIANDOCTAMNHIN:
            return self._tamnhinchung
        self._thoidiemdoctamnhinchunggannhat = thoidiemhientai
        tamnhinchung = {}
        if self.shared_data is not None:
            try:
                danhsach = list(self.shared_data.items())
            except Exception:
                danhsach = []
            idbandohientai = self.moitruong.get_idbandohientai()
            for idcuaso, info in danhsach:
                if idcuaso == self.idcuaso or not isinstance(info, dict):
                    continue
                tamnhin = info.get("tamnhin")
                if not tamnhin or tamnhin.get("bando") != idbandohientai or thoidiemhientai - tamnhin.get("thoidiem", 0.) > THOIGIANHIEULUCTAMNHIN:
                    continue
                for doituong in tamnhin.get("doituongs", ()):
                    # Cửa sổ chưa khởi động lại sau khi cập nhật chỉ có 6 trường (chưa có tên)
                    iddoituong, x, y, tuthe, huong, is_muctieupk = doituong[:6]
                    tamnhinchung[iddoituong] = (x, y, tuthe, huong, is_muctieupk, doituong[6] if len(doituong) > 6 else "")
        self._tamnhinchung = tamnhinchung
        return tamnhinchung

    def _is_doituongmoixuathien(self, diachidoituong):
        # Đối tượng vừa xuất hiện / mới nhìn thấy (chưa đủ THOIGIANCHOCHONMUCTIEUMOI giây) thì chưa được chọn làm mục tiêu,
        # cả mục tiêu tấn công lẫn đồng đội cần buff / hồi máu / hồi sinh, cho giống người chơi thật phản ứng.
        # Đồng thời ghi nhận lần thấy: mất dấu quá THOIGIANMATDAUMUCTIEU thì lần thấy lại tính là mới. Bản thân không bao giờ "mới"
        if not diachidoituong or diachidoituong == self.moitruong.get_diachicosothongtinnhanvat1():
            return False
        thoidiemhientai = time.time()
        iddoituong = self.moitruong.get_iddoituong(diachidoituong)
        thoidiemthaylandau, thoidiemthaygannhat = self._thoidiemthaymuctieu_map.get(iddoituong, (thoidiemhientai, thoidiemhientai))
        if thoidiemhientai - thoidiemthaygannhat > THOIGIANMATDAUMUCTIEU:
            thoidiemthaylandau = thoidiemhientai
        self._thoidiemthaymuctieu_map[iddoituong] = (thoidiemthaylandau, thoidiemhientai)
        return thoidiemhientai - thoidiemthaylandau < THOIGIANCHOCHONMUCTIEUMOI

    def _is_tenbiboqua(self, ten):
        # Danh sách bỏ qua: tên thường khớp đúng, tên bắt đầu bằng "~" là "tên chứa" (vd "~Hổ" bỏ mọi con có chữ Hổ).
        # Quái cùng loại trùng tên nhiều nên nhớ kết quả theo tên; danh sách bị thay set hoặc thêm tên thì tính lại
        danhsach = self._tenmuctieukhongtancongs
        khoa = (id(danhsach), len(danhsach))
        if getattr(self, "_khoatenbiboqua", None) != khoa:
            self._khoatenbiboqua = khoa
            self._mautenchuaboquas = [t[1:].strip() for t in danhsach if t.startswith("~") and t[1:].strip()]
            self._tenbiboqua_map = {}
        ketqua = self._tenbiboqua_map.get(ten)
        if ketqua is None:
            ketqua = ten in danhsach or any(mau in ten for mau in self._mautenchuaboquas)
            self._tenbiboqua_map[ten] = ketqua
        return ketqua

    def _kiemtramuctieuhople(self, diachidoituong, is_dongdoi = False):
        # Trả về False nếu không hợp lệ, ngược lại trả về dict thông tin mục tiêu để tái sử dụng
        # Ghi nhận lần thấy trước mọi kiểm tra khác (kể cả đồng đội) để đếm đúng thời gian đã nhìn thấy
        is_moixuathien = self._is_doituongmoixuathien(diachidoituong)

        if is_dongdoi:
            return not is_moixuathien

        if not self.moitruong.get_is_cothetancong(diachidoituong):
            return False

        if is_moixuathien:
            return False

        tendoituong = self.moitruong.get_tendoituong(diachidoituong)
        if tendoituong in TENMUCTIEUKHONGTANCONGs or self.moitruong.get_is_quairiengnguoikhac(tendoituong):
            return False
        if self._laytenmuctieutancongs() and tendoituong not in self._laytenmuctieutancongs():
            return False
        if self._is_tenbiboqua(tendoituong):
            return False

        is_nguoichoi = self.moitruong.get_is_nguoichoi(diachidoituong)
        is_baothukynangtrieuhoi = self.moitruong.get_is_baothukynangtrieuhoi(diachidoituong)
        is_baothugiangho = self.moitruong.get_is_baothugiangho(diachidoituong)
        is_muctieupk = is_nguoichoi or is_baothukynangtrieuhoi or is_baothugiangho

        if self._is_chidanhnguoichoi and not is_muctieupk:
            return False

        idbandohientai = self.moitruong.get_idbandohientai()
        if (idbandohientai in BANDOKHONGPKs) and is_muctieupk:
            return False

        # Sư môn / phó bản / Sư Gia đang đánh quái của việc đó thì không giới hạn theo bản đồ của lộ trình
        if self._diemdanhxungquanhs and self._is_tudongdichuyendiemdanhxungquanh and not self._is_bolotrinhdiemdanh():
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if danhsachbandohople and idbandohientai not in danhsachbandohople:
                self._nhacbandokhongcodiemdanh()
                return False

        if self.moitruong.get_is_nhanvatanthan(diachidoituong):
            return False

        toadodoituong = self.moitruong.get_toado(diachidoituong)

        # Tránh vùng cấm (theo tùy chọn tránh vùng cấm)
        if self._kiemtra_divaovungcam(*toadodoituong):
            return False

        # Quái phải nằm trong tầm của một điểm đánh (người chơi/bảo thú PK thì không giới hạn để còn phản công)
        if not is_muctieupk and not self._kiemtra_tamdiemdanh(*toadodoituong):
            return False

        if is_nguoichoi:
            idnguoichoixemxet = self.moitruong.get_idnguoichoi(diachidoituong)
            if time.time() - self.moitruong.thoidiemmuctieuanthangannhat_map.get(idnguoichoixemxet, 0) < 1.5:
                return False
            if time.time() - self.moitruong.thoidiemmuctieuxuathiengannhat_map.get(idnguoichoixemxet, 0) < 1.5:
                return False

        if is_baothukynangtrieuhoi:
            tenchunhanxemxet = self.moitruong.get_tenchunhan(diachidoituong)
            if tenchunhanxemxet and time.time() - self.moitruong.thoidiembaothuxuathiengannhat_map.get(tenchunhanxemxet, 0) < 1.5:
                return False

        return {
            "diachi": diachidoituong,
            "ten": tendoituong,
            "is_nguoichoi": is_nguoichoi,
            "is_baothukynangtrieuhoi": is_baothukynangtrieuhoi,
            "is_baothugiangho": is_baothugiangho,
            "is_muctieupk": is_muctieupk,
        }

    def _timmuctieuchung(self, toadobanthan, toadotheosau, khoangcachchophepmuctieutheosau, toadodongdois):
        # Mình không còn mục tiêu hợp lệ nào: lấy đối tượng thù địch nhân vật khác cùng máy đang thấy (mình chưa thấy), lọc như khi chọn
        # mục tiêu (tên, PK, vùng cấm, điểm đánh, vùng quanh người theo sau, nhường quái), chọn con gần mình nhất => yêu cầu tìm đường tới đó.
        # Tắt tự động sử dụng kỹ năng thì tới nơi cũng không đánh: không đi
        if not self._is_timmuctieuchung or not self._is_tudongsudungkynang:
            return None
        # Sư môn / phó bản / Sư Gia đang đánh quái của việc đó thì không giới hạn theo bản đồ của lộ trình
        if self._diemdanhxungquanhs and self._is_tudongdichuyendiemdanhxungquanh and not self._is_bolotrinhdiemdanh():
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if danhsachbandohople and self.moitruong.get_idbandohientai() not in danhsachbandohople:
                return None
        thoidiemhientai = time.time()
        idthaytaichos = {self.moitruong.get_iddoituong(diachi) for diachi in self.moitruong._get_diachidoituongxungquanhs()}
        is_hoabinh = self.moitruong.get_idmaupk() == MAUPK_HOABINH or self.moitruong.get_idbandohientai() in BANDOKHONGPKs
        tot = None
        for iddoituong, (x, y, _, _, is_muctieupk, ten) in self._laytamnhinchung().items():
            if iddoituong in idthaytaichos or iddoituong in self._idmuctieubiloi_map:
                continue
            if thoidiemhientai < self._thoidiemhetboquamuctieuchung_map.get(iddoituong, 0.):
                continue
            if ten in TENMUCTIEUKHONGTANCONGs or self.moitruong.get_is_quairiengnguoikhac(ten) \
                    or (self._laytenmuctieutancongs() and ten not in self._laytenmuctieutancongs()) \
                    or self._is_tenbiboqua(ten):
                continue
            if (self._is_chidanhnguoichoi and not is_muctieupk) or (is_muctieupk and is_hoabinh):
                continue
            khoangcach = math.dist(toadobanthan, (x, y))
            if khoangcach > KHOANGCACHTIMMUCTIEUCHUNGTOIDA:
                continue
            if toadotheosau and math.dist(toadotheosau, (x, y)) > khoangcachchophepmuctieutheosau:
                continue
            if self._kiemtra_divaovungcam(x, y):
                continue
            if not is_muctieupk and (not self._kiemtra_tamdiemdanh(x, y) or (toadodongdois and self._is_nhuongquaichodongdoi((x, y), khoangcach, toadodongdois))):
                continue
            if not tot or khoangcach < tot[0]:
                tot = (khoangcach, iddoituong, x, y)
        if not tot:
            self._muctieuchungdangtim = None
            return None

        _, iddoituong, x, y = tot
        # Đi tới 1 mục tiêu quá lâu mà vẫn chưa tự thấy (bị chặn đường, nó chạy mất...) thì bỏ qua nó một lúc
        if not self._muctieuchungdangtim or self._muctieuchungdangtim[0] != iddoituong:
            self._muctieuchungdangtim = (iddoituong, thoidiemhientai)
        elif thoidiemhientai - self._muctieuchungdangtim[1] > THOIGIANTOIDATIMMUCTIEUCHUNG:
            self._thoidiemhetboquamuctieuchung_map[iddoituong] = thoidiemhientai + THOIGIANBOQUAMUCTIEUCHUNG
            self._ghimuctieuboqua(iddoituong, "Đi tới mãi không thấy", self._laytamnhinchung().get(iddoituong, ("",) * 6)[5])
            self._thoidiemhetboquamuctieuchung_map = {k: v for k, v in self._thoidiemhetboquamuctieuchung_map.items() if v > thoidiemhientai}
            self._muctieuchungdangtim = None
            return None
        # Đang theo sau: điểm đến kẹp vào vùng quanh người theo sau (mục tiêu trong tầm đánh từ mép vùng là được)
        if toadotheosau:
            bankinh = self._tinhtoanbankinhdungtancongtheosau()
            khoangcachtheosau = math.dist(toadotheosau, (x, y))
            if khoangcachtheosau > bankinh > 0.:
                x = toadotheosau[0] + (x - toadotheosau[0]) * bankinh / khoangcachtheosau
                y = toadotheosau[1] + (y - toadotheosau[1]) * bankinh / khoangcachtheosau
                return {"yeucau": YEUCAUDICHUYENTIMMUCTIEUCHUNG, "toadodich": (x, y), "khoangcachtoida": 0.}
        return {"yeucau": YEUCAUDICHUYENTIMMUCTIEUCHUNG, "toadodich": (x, y), "khoangcachtoida": KHOANGCACHDUNGTIMMUCTIEUCHUNG}

    def _laymuctieutaphoa(self):
        # Địa chỉ (trong cửa sổ này) của mục tiêu mà người mình theo sau đang chọn, 0 nếu không biết.
        # Chỉ biết khi người đó chạy trên cùng máy (đọc iddoituongmuctieu cửa sổ đó công bố), cùng bản đồ và thông tin còn mới
        info = self._laythongtinmuctieutheosaucuasokhac()
        if not info or time.time() - info.get("thoidiemcapnhat", 0.) > THOIGIANHIEULUCTAPHOA:
            return 0
        if info.get("tenbando") != self.moitruong.get_idbandohientai():
            return 0
        iddoituongmuctieu = info.get("iddoituongmuctieu")
        if not iddoituongmuctieu or iddoituongmuctieu <= 0:
            return 0
        for diachi in self.moitruong._get_diachidoituongxungquanhs():
            if self.moitruong.get_iddoituong(diachi) == iddoituongmuctieu:
                return diachi
        return 0

    def _ghinhanchieuguivaomuctieu(self, diachimuctieu):
        # Đếm chiêu gửi vào mục tiêu đang theo dõi trúng chiêu; chiêu đầu tiên sau lần trúng gần nhất là mốc bắt đầu tính giờ
        theodoi = self._theodoitrungchieu
        if not diachimuctieu or not theodoi or theodoi["id"] != self.moitruong.get_iddoituong(diachimuctieu):
            return
        if not theodoi["sochieu"]:
            theodoi["thoidiembatdau"] = time.time()
        theodoi["sochieu"] += 1

    def _kiemtramuctieukhongtrungchieu(self, diachimuctieu):
        # Mục tiêu hiện tại đã đánh mãi mà không trúng (không hiện số bay mất máu mới, xem THOIGIANKHONGTRUNGCHIEUTOIDA) thì bỏ qua nó
        # THOIGIANBOQUAMUCTIEUKHONGTRUNG giây, trả về True. Số bay do người khác đánh cũng tính là trúng: quái vẫn đang mất máu
        thoidiemhientai = time.time()
        iddoituong = self.moitruong.get_iddoituong(diachimuctieu)
        sobay = self.moitruong._docsobaydoituong(diachimuctieu)
        theodoi = self._theodoitrungchieu
        if not theodoi or theodoi["id"] != iddoituong:
            self._theodoitrungchieu = {"id": iddoituong, "sobay": sobay, "sochieu": 0, "thoidiembatdau": 0.}
            return False
        if sobay and theodoi["sobay"]:
            (giatricu, demcu), (giatri, dem) = theodoi["sobay"], sobay
            if any(giatri[i] > 0 and (giatri[i] != giatricu[i] or dem[i] < demcu[i]) for i in range(10)):
                theodoi["sochieu"] = 0
                theodoi["thoidiembatdau"] = 0.
        theodoi["sobay"] = sobay
        if theodoi["sochieu"] < SOCHIEUKHONGTRUNGTOIDA or thoidiemhientai - theodoi["thoidiembatdau"] <= THOIGIANKHONGTRUNGCHIEUTOIDA:
            return False
        print(f"[KHÔNG TRÚNG] Gửi {theodoi['sochieu']} chiêu trong {round(thoidiemhientai - theodoi['thoidiembatdau'], 1)}s vào "
              f"{self.moitruong.get_tendoituong(diachimuctieu)} ({hex(iddoituong)}) mà không thấy số bay -> bỏ qua {THOIGIANBOQUAMUCTIEUKHONGTRUNG:.0f}s")
        # _idmuctieubiloi_map tự xoá sau 120s: lùi mốc để hết bỏ qua sau đúng THOIGIANBOQUAMUCTIEUKHONGTRUNG giây
        self._idmuctieubiloi_map[iddoituong] = thoidiemhientai - (120. - THOIGIANBOQUAMUCTIEUKHONGTRUNG)
        self._ghimuctieuboqua(iddoituong, "Đánh không trúng", self.moitruong.get_tendoituong(diachimuctieu))
        self._theodoitrungchieu = None
        return True

    def _ghimuctieuboqua(self, iddoituong, lydo, ten = None):
        # Ghi tên / lý do mục tiêu vừa bị bỏ qua cho giao diện; không biết tên thì tìm trong đối tượng xung quanh
        if ten is None:
            ten = next((self.moitruong.get_tendoituong(diachi) for diachi in self.moitruong._get_diachidoituongxungquanhs()
                        if self.moitruong.get_iddoituong(diachi) == iddoituong), "")
        self._thongtinmuctieuboqua_map[iddoituong] = (ten or "", lydo)

    def get_danhsachmuctieuboqua(self):
        # [{id, ten, lydo, conlai}] mục tiêu bot đang tự bỏ qua theo id (_idmuctieubiloi_map hết sau 120s, _thoidiemhetboquamuctieuchung_map theo mốc hết).
        # Chép dict trước khi duyệt: luồng khác đang thêm / xoá
        thoidiemhientai = time.time()
        conlais = {}
        for iddoituong, thoidiem in self._idmuctieubiloi_map.copy().items():
            if 120. - (thoidiemhientai - thoidiem) > 0:
                conlais[iddoituong] = 120. - (thoidiemhientai - thoidiem)
        for iddoituong, thoidiemhet in self._thoidiemhetboquamuctieuchung_map.copy().items():
            if thoidiemhet > thoidiemhientai:
                conlais[iddoituong] = max(conlais.get(iddoituong, 0.), thoidiemhet - thoidiemhientai)
        thongtins = self._thongtinmuctieuboqua_map.copy()
        self._thongtinmuctieuboqua_map = {k: v for k, v in thongtins.items() if k in conlais}
        danhsach = []
        for iddoituong, conlai in conlais.items():
            ten, lydo = thongtins.get(iddoituong, ("", "Bị chặn / kẹt"))
            danhsach.append({"id": iddoituong, "ten": ten, "lydo": lydo, "conlai": round(conlai)})
        return sorted(danhsach, key = lambda muc: (muc["ten"], muc["id"]))

    def xoa_muctieuboqua(self, iddoituongs = None):
        # Giao diện bấm Xoá: thôi bỏ qua các id này (None: xoá hết) để bot đánh lại ngay
        idxoas = set(self._idmuctieubiloi_map) | set(self._thoidiemhetboquamuctieuchung_map) if iddoituongs is None else set(iddoituongs)
        for iddoituong in idxoas:
            self._idmuctieubiloi_map.pop(iddoituong, None)
            self._thoidiemhetboquamuctieuchung_map.pop(iddoituong, None)
            self._thongtinmuctieuboqua_map.pop(iddoituong, None)
        print("Thôi bỏ qua mục tiêu: {}".format(", ".join(hex(i) for i in idxoas) or "không có"))

    def action_tudongtimkiemmuctieu(self):
        # Yêu cầu đi tới mục tiêu nhân vật khác thấy chỉ tạo lại ở cuối hàm khi mình không có mục tiêu nào
        self._yeucautimmuctieuchung = None
        if not self._is_tudongtimkiemmuctieu:
            return

        idbandohientai = self.moitruong.get_idbandohientai()
        if idbandohientai in BANDOKHONGTANCONGs:
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            return

        # Người được theo sau đã sang bản đồ khác và đang tự tìm đường theo (_xulyphutheosau): bỏ mục tiêu, đi theo trước, không đứng lại đánh quái
        if self._is_dangphutheosau:
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            return

        # Lăng Ly Sơn: trưởng nhóm đang chờ đủ thành viên trước boss cuối (người vắng lúc boss chết không được thưởng): không đánh
        if self.get_is_camdanhlanglyson():
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            return

        # Sư Gia: trưởng nhóm thấy tội phạm mà chưa đủ thành viên (mình hoặc trưởng nhóm cùng máy đang chờ): không đánh
        if self.get_is_camdanhsugia():
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            return

        # Đang Đi tới bản đồ người dùng chọn / đi giao đồ / cất kho / đi làm sư môn: không chọn quái dọc đường (trước đây gặp quái là đứng
        # lại đánh), tới nơi mới đánh
        if self._idbandocandi or self.get_is_danggiaodo() or self.get_is_dangcatkho() or self.get_is_sumondichuyen() or self.get_is_langlysondichuyen() \
                or self.get_is_sugiadichuyen() or self.get_is_tapkichdichuyen():
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            return

        def _thaydoimuctieu(diachimuctieu):
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachimuctieu)
            self.moitruong._thoidiemtuthenhanvatdungimcomuctieugannhat = time.time()
            self._is_battudongtancongvatly = False
            self._thoidiemdoimuctieugannhat = time.time()

        if idbandohientai != self._idbandomuctieudangchon:
            self._idbandomuctieudangchon = idbandohientai
            self._diachicosomuctieuduphong = 0
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

        thoidiemhientai = time.time()
        idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if thoidiemhientai - v > 120]
        for k in idcanxoas:
            del self._idmuctieubiloi_map[k]
        self._thoidiemthaymuctieu_map = {k: v for k, v in self._thoidiemthaymuctieu_map.items() if thoidiemhientai - v[1] <= THOIGIANMATDAUMUCTIEU}

        diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

        toadotheosau = self._laytoadomuctieutheosau()
        is_anhhuongboimuctieutheosau = bool(toadotheosau)
        khoangcachtoidatheosau = self._tinhtoankhoangcachtoidatheosauphuhop()

        khoangcachchophepmuctieutheosau = self._tinhtoankhoangcachchophepmuctieutheosau()
        khoangcachchophepmuctieuhientaitheosau = self._tinhtoankhoangcachchophepmuctieutheosau(is_muctieuhientai = True)

        # Đọc tọa độ bản thân 1 lần, tính khoảng cách bằng math.dist thay vì đọc lại bộ nhớ cho mỗi đối tượng
        toadobanthan = self.moitruong.get_toado()

        def _bosungvitri(thongtin, toado = None):
            toado = toado or self.moitruong.get_toado(thongtin["diachi"])
            thongtin["toado"] = toado
            thongtin["khoangcach"] = math.dist(toado, toadobanthan)
            thongtin["khoangcachtheosau"] = math.dist(toado, toadotheosau) if is_anhhuongboimuctieutheosau else 0.
            return thongtin

        # Đang farm & bán rác: nhường quái đang ở gần nhân vật khác của mình cho nhân vật đó,
        # tránh các nhân vật đánh chung một chỗ, đi sát rạt vào nhau (giống logic nhường quái khi gom)
        toadodongdois = self._laytoadodongdoikhacnhom() if self._is_tudongvebanrac else []

        def _is_nhuongdongdoi(thongtin):
            if thongtin["is_muctieupk"] or not toadodongdois:
                return False
            return self._is_nhuongquaichodongdoi(thongtin["toado"], thongtin["khoangcach"], toadodongdois)

        muctieuhientai = None

        if diachicosothongtinnhanvatmuctieudangchon:
            thongtin = self._kiemtramuctieuhople(diachicosothongtinnhanvatmuctieudangchon, is_dongdoi = False)
            if thongtin:
                _bosungvitri(thongtin)
                if is_anhhuongboimuctieutheosau and thongtin["khoangcachtheosau"] > khoangcachchophepmuctieuhientaitheosau:
                    thongtin = False
                elif self.moitruong.get_idmaupk() == MAUPK_HOABINH and thongtin["is_muctieupk"]:
                    thongtin = False
                elif _is_nhuongdongdoi(thongtin):
                    thongtin = False
                elif not thongtin["is_muctieupk"] and self._kiemtramuctieukhongtrungchieu(diachicosothongtinnhanvatmuctieudangchon):
                    thongtin = False

            if thongtin:
                muctieuhientai = thongtin
            else:
                # Không xoá mục tiêu dự phòng ở đây: mục tiêu hiện tại chết / hết hợp lệ chính là lúc cần quay lại dự phòng
                if self._diachicosomuctieuduphong == diachicosothongtinnhanvatmuctieudangchon:
                    self._diachicosomuctieuduphong = 0
                _thaydoimuctieu(0)
                diachicosothongtinnhanvatmuctieudangchon = 0

        if not diachicosothongtinnhanvatmuctieudangchon and self._diachicosomuctieuduphong:
            diachiduphong = self._diachicosomuctieuduphong
            self._diachicosomuctieuduphong = 0

            thongtin = self.moitruong.get_is_nhanvattontai(diachiduphong) and self._kiemtramuctieuhople(diachiduphong, is_dongdoi = False)
            if thongtin:
                _bosungvitri(thongtin)
                is_duphonghople = thongtin["khoangcach"] < KHOANGCACHTOANMANHINH and not _is_nhuongdongdoi(thongtin)
                if is_anhhuongboimuctieutheosau and thongtin["khoangcachtheosau"] > khoangcachchophepmuctieuhientaitheosau:
                    is_duphonghople = False

                if is_duphonghople:
                    _thaydoimuctieu(diachiduphong)
                    diachicosothongtinnhanvatmuctieudangchon = diachiduphong
                    muctieuhientai = thongtin

        if is_anhhuongboimuctieutheosau:
            khoangcachtoibanthanvatheosau = math.dist(toadobanthan, toadotheosau)
            # Chừa thêm một khoảng: ngưỡng này trùng chỗ dừng khi theo nhóm nên lệch chút xíu (trưởng nhóm đang đi) là không chọn được mục tiêu
            if khoangcachtoibanthanvatheosau > khoangcachtoidatheosau + KHOANGCACHSUDUNGKYNANGCANCHIEN:
                # Không đếm lượt này: xoá kết quả đếm cũ để không dùng chiêu diện rộng theo số quái của lượt trước khi đang chạy về
                self._is_nhieumuctieugan3 = self._is_nhieumuctieugan5 = self._is_nhieumuctieugan7 = self._is_nhieumuctieugan9 = False
                self._is_nhieumuctieuganbanthan3 = self._is_nhieumuctieuganbanthan5 = self._is_nhieumuctieuganbanthan7 = self._is_nhieumuctieuganbanthan9 = False
                return

        # Tập hỏa: người mình theo sau chạy cùng máy thì đánh đúng mục tiêu họ đang chọn (dữ liệu chia sẻ). Khác máy, hoặc mục tiêu đó
        # không hợp lệ với mình (chưa thấy, mới xuất hiện chưa đủ 1s, ngoài vùng quanh người theo sau, đang hoà bình mà là mục tiêu PK...)
        # thì chọn mục tiêu gần người theo sau nhất (xem _is_uutienhon)
        if self._is_taphoa and is_anhhuongboimuctieutheosau:
            diachitaphoa = self._laymuctieutaphoa()
            thongtin = diachitaphoa and self._kiemtramuctieuhople(diachitaphoa, is_dongdoi = False)
            if thongtin:
                _bosungvitri(thongtin)
                if thongtin["khoangcachtheosau"] <= khoangcachchophepmuctieuhientaitheosau \
                        and not (self.moitruong.get_idmaupk() == MAUPK_HOABINH and thongtin["is_muctieupk"]):
                    if diachitaphoa != diachicosothongtinnhanvatmuctieudangchon:
                        if diachicosothongtinnhanvatmuctieudangchon:
                            self._diachicosomuctieuduphong = diachicosothongtinnhanvatmuctieudangchon
                        _thaydoimuctieu(diachitaphoa)
                    return

        is_nhanvatbichoang = self.moitruong.get_is_nhanvatbichoang()
        is_vanmongcoc = self.moitruong.get_tenmonphai() == "vanmongcoc"

        def _is_codieukienbattu(diachi):
            if self.moitruong.get_phantramsinhlucconlai(diachi) > 5:
                return False, False
            return True, self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachi, is_hieuungcoloi = 1)

        def _is_uutienhon(xemxet, hientai):
            is_baothuxemxettrongtam = xemxet["is_baothukynangtrieuhoi"] and xemxet["khoangcach"] < self._khoangcachsudungkynangtamxa
            is_baothuhientaitrongtam = hientai["is_baothukynangtrieuhoi"] and hientai["khoangcach"] < self._khoangcachsudungkynangtamxa

            if self._is_uutienbaothukynangtrieuhoi and (is_baothuxemxettrongtam or is_baothuhientaitrongtam):
                if is_baothuxemxettrongtam != is_baothuhientaitrongtam:
                    return is_baothuxemxettrongtam
            elif xemxet["is_nguoichoi"] != hientai["is_nguoichoi"]:
                return xemxet["is_nguoichoi"]

            if self._is_khonguutienbaothugiangho and not is_nhanvatbichoang:
                if (xemxet["is_nguoichoi"] or xemxet["is_baothukynangtrieuhoi"]) and hientai["is_baothugiangho"]:
                    return True
                if (hientai["is_nguoichoi"] or hientai["is_baothukynangtrieuhoi"]) and xemxet["is_baothugiangho"]:
                    return False

            if self._is_uutienmuctieupk and xemxet["is_muctieupk"] != hientai["is_muctieupk"]:
                return xemxet["is_muctieupk"]

            if xemxet["is_muctieupk"] and hientai["is_muctieupk"]:
                is_hientaibikhongthu = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, diachicosothongtinnhanvat = hientai["diachi"], is_hieuungcoloi = 0)
                if is_hientaibikhongthu and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, diachicosothongtinnhanvat = xemxet["diachi"], is_hieuungcoloi = 0):
                    return True

                if not is_vanmongcoc:
                    _, is_hientaibattu = _is_codieukienbattu(hientai["diachi"])
                    if is_hientaibattu:
                        is_xemxetmauthap, is_xemxetbattu = _is_codieukienbattu(xemxet["diachi"])
                        if not is_xemxetmauthap or not is_xemxetbattu:
                            return True

            # Chỉ hơn nhau về khoảng cách: muốn thay mục tiêu đang đánh thì phải gần hơn hẳn (xem CHENHLECHKHOANGCACHDOIMUCTIEU)
            chenhlech = CHENHLECHKHOANGCACHDOIMUCTIEU if hientai is muctieuhientai else 0.5
            # Tập hỏa mà người theo sau ở máy khác (không biết họ chọn ai): ưu tiên mục tiêu gần người theo sau nhất cho sát mục tiêu của họ.
            # Không tập hỏa: ưu tiên mục tiêu gần bản thân (vẫn lọc bỏ mục tiêu ngoài vùng quanh người theo sau ở chỗ khác)
            if is_anhhuongboimuctieutheosau and self._is_taphoa:
                return xemxet["khoangcachtheosau"] + chenhlech < hientai["khoangcachtheosau"]
            return _khoangcachsosanh(xemxet) + chenhlech < _khoangcachsosanh(hientai)

        # Đang chạy thì mục tiêu sau lưng (ngược hướng đang chạy) bị tính xa thêm PHATMUCTIEUSAULUNG ô khi so: chỉ theo khoảng cách
        # thì cứ có con sau lưng gần hơn 0.5 ô là quay đầu, chạy vài bước con phía trước lại gần hơn => đổi qua lại, chạy tới chạy lui
        huongdichuyen = None
        if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
            xsap, ysap = self.moitruong.get_toado(is_toadosaptoi = True)
            if (xsap, ysap) != tuple(toadobanthan):
                huongdichuyen = (xsap - toadobanthan[0], ysap - toadobanthan[1])

        def _khoangcachsosanh(thongtin):
            khoangcach = thongtin["khoangcach"]
            toado = thongtin.get("toado")
            if huongdichuyen and toado and (toado[0] - toadobanthan[0]) * huongdichuyen[0] + (toado[1] - toadobanthan[1]) * huongdichuyen[1] < 0:
                khoangcach += PHATMUCTIEUSAULUNG
            return khoangcach

        demmuctieuganbanthan3 = 0
        demmuctieuganbanthan5 = 0
        demmuctieuganbanthan7 = 0
        demmuctieuganbanthan9 = 0

        khoangcachtimkiem = self._khoangcachtimkiemmuctieu
        muctieutotnhat = muctieuhientai
        # Ứng viên tốt nhì: làm mục tiêu dự phòng khi trước đó không có mục tiêu hiện tại
        muctieutotnhi = None
        toadomuctieuhoples = []

        iii = 0
        while True:
            diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(iii)
            if not diachicosothongtinnhanvatmuctieuxemxet:
                break
            iii += 1

            toadomuctieuxemxet = self.moitruong.get_toado(diachicosothongtinnhanvatmuctieuxemxet)
            khoangcachmuctieuxemxettoibanthan = math.dist(toadomuctieuxemxet, toadobanthan)
            if khoangcachmuctieuxemxettoibanthan >= khoangcachtimkiem:
                continue

            if self.moitruong.get_iddoituong(diachicosothongtinnhanvatmuctieuxemxet) in self._idmuctieubiloi_map:
                continue

            thongtinmuctieuxemxet = self._kiemtramuctieuhople(diachicosothongtinnhanvatmuctieuxemxet, is_dongdoi = False)
            if not thongtinmuctieuxemxet:
                continue

            # Đếm trước khi lọc theo vùng quanh người theo sau / nhường đồng đội: chiêu diện rộng (Đại Hải Vô Lượng...)
            # trúng mọi con đứng quanh mình, kể cả con không được chọn làm mục tiêu. Lọc trước thì người theo sau
            # khoảng cách ngắn chỉ đếm được con trong ~1.5 ô quanh trưởng nhóm nên gần như không bao giờ đủ số lượng
            toadomuctieuhoples.append(toadomuctieuxemxet)

            if khoangcachmuctieuxemxettoibanthan <= 9.0:
                if khoangcachmuctieuxemxettoibanthan <= 3.0:
                    demmuctieuganbanthan3 += 1
                if khoangcachmuctieuxemxettoibanthan <= 5.0:
                    demmuctieuganbanthan5 += 1
                if khoangcachmuctieuxemxettoibanthan <= 7.0:
                    demmuctieuganbanthan7 += 1
                demmuctieuganbanthan9 += 1

            _bosungvitri(thongtinmuctieuxemxet, toadomuctieuxemxet)
            if is_anhhuongboimuctieutheosau and thongtinmuctieuxemxet["khoangcachtheosau"] > khoangcachchophepmuctieutheosau:
                continue
            if _is_nhuongdongdoi(thongtinmuctieuxemxet):
                continue

            # Mục tiêu hiện tại đã là điểm xuất phát của muctieutotnhat, không so lại với chính nó
            if muctieuhientai and diachicosothongtinnhanvatmuctieuxemxet == muctieuhientai["diachi"]:
                continue

            if not muctieutotnhat or _is_uutienhon(thongtinmuctieuxemxet, muctieutotnhat):
                muctieutotnhi = muctieutotnhat
                muctieutotnhat = thongtinmuctieuxemxet
            elif not muctieutotnhi or _is_uutienhon(thongtinmuctieuxemxet, muctieutotnhi):
                muctieutotnhi = thongtinmuctieuxemxet

        # Chỉ ghi mục tiêu vào game 1 lần sau khi đã chọn xong
        diachimuctieumoi = muctieutotnhat["diachi"] if muctieutotnhat else 0
        if diachimuctieumoi != diachicosothongtinnhanvatmuctieudangchon:
            # Dự phòng: mục tiêu đang đánh bị thay (quay lại nó khi mục tiêu mới chết), không có thì ứng viên tốt nhì
            diachiduphong = diachicosothongtinnhanvatmuctieudangchon or (muctieutotnhi["diachi"] if muctieutotnhi else 0)
            if diachiduphong:
                self._diachicosomuctieuduphong = diachiduphong
            _thaydoimuctieu(diachimuctieumoi)

        # Quanh mình không còn mục tiêu nào: xem tầm nhìn của nhân vật khác cùng máy, có thì tìm đường tới đó
        if not muctieutotnhat:
            self._yeucautimmuctieuchung = self._timmuctieuchung(toadobanthan, toadotheosau if is_anhhuongboimuctieutheosau else None,
                                                                khoangcachchophepmuctieutheosau, toadodongdois)
        else:
            self._muctieuchungdangtim = None

        # Đếm quanh mục tiêu cuối cùng (trước đây đếm theo mục tiêu tạm thời trong vòng lặp nên bị sai)
        demmuctieugan3 = 0
        demmuctieugan5 = 0
        demmuctieugan7 = 0
        demmuctieugan9 = 0

        toadotamdem = muctieutotnhat["toado"] if muctieutotnhat else toadobanthan
        for toadomuctieuhople in toadomuctieuhoples:
            khoangcachtoitamdem = math.dist(toadomuctieuhople, toadotamdem)
            if khoangcachtoitamdem <= 9.0:
                if khoangcachtoitamdem <= 3.0:
                    demmuctieugan3 += 1
                if khoangcachtoitamdem <= 5.0:
                    demmuctieugan5 += 1
                if khoangcachtoitamdem <= 7.0:
                    demmuctieugan7 += 1
                demmuctieugan9 += 1

        self._is_nhieumuctieugan3 = demmuctieugan3 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan5 = demmuctieugan5 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan7 = demmuctieugan7 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan9 = demmuctieugan9 >= self._soluongnhieumuctieu

        self._is_nhieumuctieuganbanthan3 = demmuctieuganbanthan3 >= self._soluongnhieumuctieu
        self._is_nhieumuctieuganbanthan5 = demmuctieuganbanthan5 >= self._soluongnhieumuctieu
        self._is_nhieumuctieuganbanthan7 = demmuctieuganbanthan7 >= self._soluongnhieumuctieu
        self._is_nhieumuctieuganbanthan9 = demmuctieuganbanthan9 >= self._soluongnhieumuctieu

    def _is_baothudongdoi(self, diachibaothu, idnguoichoi, idnguoichoithanhviennhoms):
        # Bảo thú (tên có chủ nhân trong ngoặc) của mình, thành viên nhóm hoặc nhân vật tổ đội tự động; chủ không ở gần thì không biết => False
        if not (self.moitruong.get_is_baothukynangtrieuhoi(diachibaothu) or self.moitruong.get_is_baothugiangho(diachibaothu)):
            return False
        tenchunhan = self.moitruong.get_tenchunhan(diachibaothu)
        if not tenchunhan:
            return False
        if tenchunhan == self.moitruong.get_tendoituong():
            return True
        diachichunhan = self.moitruong.action_timkiemnhanvat(tennhanvat = tenchunhan)
        if not diachichunhan:
            return False
        idchunhan = self.moitruong.get_idnguoichoi(diachichunhan)
        return idchunhan == idnguoichoi or bool(idnguoichoithanhviennhoms and idchunhan in idnguoichoithanhviennhoms) \
            or idchunhan in laynhanvattodoitudongs()

    def _kiemtramuctieuhoplemonphai(self, diachidoituong, is_dongdoi = False):
        # Vừa xuất hiện thì chờ đủ THOIGIANCHOCHONMUCTIEUMOI, kể cả đồng đội (buff / hồi máu / hồi sinh)
        if self._is_doituongmoixuathien(diachidoituong):
            return False
        if is_dongdoi:
            return True
        iddoituong = self.moitruong.get_iddoituong(diachidoituong)
        if iddoituong in self._idmuctieubiloi_map:
            return False
        tendoituong = self.moitruong.get_tendoituong(diachidoituong)
        if tendoituong in TENMUCTIEUKHONGTANCONGs or self.moitruong.get_is_quairiengnguoikhac(tendoituong):
            return False
        if self._laytenmuctieutancongs() and tendoituong not in self._laytenmuctieutancongs():
            return False
        if self._is_tenbiboqua(tendoituong):
            return False
        is_nguoichoi = self.moitruong.get_is_nguoichoi(diachidoituong)
        is_baothu = self.moitruong.get_is_baothukynangtrieuhoi(diachidoituong) or self.moitruong.get_is_baothugiangho(diachidoituong)
        is_muctieupk = is_nguoichoi or is_baothu

        if self._is_chidanhnguoichoi and not is_muctieupk:
            return False
        if self.moitruong.get_is_nhanvatanthan(diachidoituong):
            return False
        idbandohientai = self.moitruong.get_idbandohientai()
        is_bandokhongpk = idbandohientai in BANDOKHONGPKs
        if is_bandokhongpk and is_muctieupk:
            return False
        # Sư môn / phó bản / Sư Gia đang đánh quái của việc đó thì không giới hạn theo bản đồ của lộ trình
        if self._diemdanhxungquanhs and self._is_tudongdichuyendiemdanhxungquanh and not self._is_bolotrinhdiemdanh():
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if danhsachbandohople and idbandohientai not in danhsachbandohople:
                return False

        return True

    def action_test(self):
        vitrivatpham = 0
        iddoituong = self.moitruong.get_iddoituongvatphamhanhtrang(vitrivatpham)
        if iddoituong:
            while True:
                self.moitruong.truyvan_motavatphamhanhtrang(vitrivatpham)
                motavatpham = self.moitruong.get_motavatphamhanhtrang(vitrivatpham)
                if not motavatpham:
                    break
                if "★★★★★★" in motavatpham:
                    break
                if "★★★★★" in motavatpham or "★★★★" in motavatpham:
                    iddoituongdoanthach = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPDOANTHACH)
                elif "★★★" in motavatpham or "★★" in motavatpham:
                    iddoituongdoanthach = self.moitruong.action_timkiemvatphamhanhtrang(TRUNGCAPDOANTHACH)
                else:
                    iddoituongdoanthach = self.moitruong.action_timkiemvatphamhanhtrang(SOCAPDOANTHACH)
                if iddoituongdoanthach:
                    self.moitruong.action_thucthicaulenh("mix3 0# {}# {}#".format(hex(iddoituong), hex(iddoituongdoanthach)).replace("0x", ""))
                    time.sleep(0.25)
                else:
                    break
    def action_tudongtimkiemmuctieumonphai(self):
        tenmonphai = self.moitruong.get_tenmonphai()

        toadotheosau = self._laytoadomuctieutheosau()
        is_anhhuongboimuctieutheosau = bool(toadotheosau)
        # Cùng ngưỡng với chọn mục tiêu: đối tượng phải với tới được (tầm xa đã trừ hao phần bù khi đứng im) từ chỗ đứng quanh trưởng nhóm,
        # nếu không kỹ năng buff cứ xin chạy bù mà bị cắt về mép vùng, chặn luôn các kỹ năng tấn công phía sau
        khoangcachchophepmuctieutheosau = self._tinhtoanbankinhdungtancongtheosau() + self._khoangcachsudungkynangtamxa - TRUHAOTAMXACHONMUCTIEU

        idbandohientai = self.moitruong.get_idbandohientai()
        if tenmonphai == "daohoanguyen":
            idnguoichoi = self.moitruong.get_idnguoichoi()
            idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

            diachidoituongcanbuff = None

            if self.moitruong.get_is_dangnamtrongnhom():
                i = -1
                while True:
                    i += 1
                    diachicosothongtindoituongmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)

                    if not diachicosothongtindoituongmuctieuxemxet:
                        break

                    if not self.moitruong.get_is_nhanvattontai(diachicosothongtindoituongmuctieuxemxet):
                        continue
                    if self.moitruong.get_is_nhanvatdachet(diachicosothongtindoituongmuctieuxemxet):
                        continue

                    if is_anhhuongboimuctieutheosau:
                        if self.moitruong.get_khoangcachdiem(*toadotheosau, diachicosothongtindoituongmuctieuxemxet) > khoangcachchophepmuctieutheosau:
                            continue

                    if self.moitruong.get_khoangcach(diachicosothongtindoituongmuctieuxemxet) > self._khoangcachsudungkynangtamxa:
                        continue

                    if self.moitruong.get_is_nguoichoi(diachicosothongtindoituongmuctieuxemxet):
                        idnguoichoixemxet = self.moitruong.get_idnguoichoi(diachicosothongtindoituongmuctieuxemxet)

                        # Đồng đội vừa xuất hiện thì chờ đủ THOIGIANCHOCHONMUCTIEUMOI mới buff
                        if idnguoichoixemxet != idnguoichoi and idnguoichoithanhviennhoms and idnguoichoixemxet in idnguoichoithanhviennhoms \
                                and not self._is_doituongmoixuathien(diachicosothongtindoituongmuctieuxemxet):
                            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, macdinh = True, is_hieuungcoloi = 1):
                                diachidoituongcanbuff = diachicosothongtindoituongmuctieuxemxet
                                break

            self._diachidoituongcanbuffhothekimcangdaohoanguyen = diachidoituongcanbuff

        elif tenmonphai == "maoson":
            diachidoituongcanbuffthuccot = None
            khoangcachthuccotgannhat = 9999.

            diachidoituongcanbuffthucgiap = None
            khoangcachthucgiapgannhat = 9999.

            diachidoituongcanbuffthuctam = None
            khoangcachthuctamgannhat = 9999.

            diachidoituongcanbuffammanhapthe = None
            khoangcachammanhapthegannhat = 9999.

            # Bản đồ không PK (thành Ngụy Quốc...) vẫn xét nhưng chỉ dùng lên boss trong TENBOSSBUFFMAOSONs (Trộm Bảo / Bảo Hộp Phi Tặc xuất hiện trong thành)
            is_bandokhongpk = idbandohientai in BANDOKHONGPKs
            diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            i = -1
            while True:
                i += 1
                diachicosothongtindoituongmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtindoituongmuctieuxemxet:
                    break

                if not self.moitruong.get_is_nhanvattontai(diachicosothongtindoituongmuctieuxemxet): continue
                if self.moitruong.get_is_nhanvatdachet(diachicosothongtindoituongmuctieuxemxet): continue
                if not self.moitruong.get_is_cothetancong(diachicosothongtindoituongmuctieuxemxet): continue

                if not self._kiemtramuctieuhoplemonphai(diachicosothongtindoituongmuctieuxemxet, is_dongdoi = False):
                    continue

                if is_anhhuongboimuctieutheosau:
                    if self.moitruong.get_khoangcachdiem(*toadotheosau, diachicosothongtindoituongmuctieuxemxet) > khoangcachchophepmuctieutheosau:
                        continue

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtindoituongmuctieuxemxet)
                if khoangcach > self._khoangcachsudungkynangtamxa:
                    continue

                is_nguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtindoituongmuctieuxemxet)
                is_baothu = self.moitruong.get_is_baothukynangtrieuhoi(diachicosothongtindoituongmuctieuxemxet) or self.moitruong.get_is_baothugiangho(diachicosothongtindoituongmuctieuxemxet)
                tendoituong = self.moitruong.get_tendoituong(diachicosothongtindoituongmuctieuxemxet)
                is_boss = not is_nguoichoi and not is_baothu and tendoituong in TENBOSSBUFFMAOSONs
                if not is_nguoichoi and not is_baothu and not is_boss and idbandohientai not in (BANDO_COMO, BANDO_BATQUAITRAN):
                    continue
                if is_bandokhongpk and not is_boss:
                    continue
                # Phá Thiên Yêu: Thực Giáp / Thực Tâm chỉ dùng khi nó là mục tiêu đang chọn, con khác chỉ buff Thực Cốt
                is_chibuffthuccot = not is_nguoichoi and not is_baothu and tendoituong == "Phá Thiên Yêu" \
                    and diachicosothongtindoituongmuctieuxemxet != diachimuctieudangchon

                if khoangcach < khoangcachthuccotgannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCCOT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, is_hieuungcoloi = 0):
                    diachidoituongcanbuffthuccot = diachicosothongtindoituongmuctieuxemxet
                    khoangcachthuccotgannhat = khoangcach

                if not is_chibuffthuccot and khoangcach < khoangcachthucgiapgannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCGIAP,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, is_hieuungcoloi = 0):
                    diachidoituongcanbuffthucgiap = diachicosothongtindoituongmuctieuxemxet
                    khoangcachthucgiapgannhat = khoangcach

                if not is_chibuffthuccot and khoangcach < khoangcachthuctamgannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCTAM,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, is_hieuungcoloi = 0):
                    diachidoituongcanbuffthuctam = diachicosothongtindoituongmuctieuxemxet
                    khoangcachthuctamgannhat = khoangcach

                idloaivukhi = self.moitruong.get_idloaivukhi(diachicosothongtindoituongmuctieuxemxet)
                if is_nguoichoi and idloaivukhi in (IDLOAIVUKHI_THUONG, IDLOAIVUKHI_CON, ):
                    if khoangcach < khoangcachammanhapthegannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_AMMANHAPTHE,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, is_hieuungcoloi = 0):
                        diachidoituongcanbuffammanhapthe = diachicosothongtindoituongmuctieuxemxet
                        khoangcachammanhapthegannhat = khoangcach

            self._diachidoituongcanbuffthuccotmaoson = diachidoituongcanbuffthuccot
            self._diachidoituongcanbuffthucgiapmaoson = diachidoituongcanbuffthucgiap
            self._diachidoituongcanbuffthuctammaoson = diachidoituongcanbuffthuctam
            self._diachidoituongcanbuffammanhapthemaoson = diachidoituongcanbuffammanhapthe

        elif tenmonphai == "vanmongcoc":
            idnguoichoi = self.moitruong.get_idnguoichoi()
            idbandohientai = idbandohientai
            idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

            diachidoituongcanhoisinh = None
            diachidoituongcanbufftaytranquyet = None
            diachidoituongcanbufftaytranquyet2 = None
            diachidoituongcanbufflinhkhihothe = None
            diachidoituongcanbommau = None
            phantramsinhlucthapnhat = 100.

            diachidoituongcanhoisinhduphong = None
            diachidoituongcanbufftaytranquyetduphong = None
            diachidoituongcanbufftaytranquyet2duphong = None
            diachidoituongcanbommauduphong = None
            phantramsinhlucthapnhatduphong = 100.

            # Đối tượng cần bơm máu (kể cả dự phòng) kèm toạ độ, để chọn tâm Khiết Vân Quyết (hồi máu 3x3 ô)
            danhsachcanbommau = []

            diachidoituongcanbuffkimcham = None
            diachidoituongcanbuffngancham = None
            diachidoituongcanbuffcuongthethuat = None

            diachidoituongcanbuffphonganthuat = None
            khoangcachphonganthuatgannhat = 9999.

            diachidoituongcanbuffhuyenquangthiemanh = None
            khoangcachhuyenquanggannhat = 9999.

            danhsachungviens = [(0, self.moitruong.get_diachicosothongtinnhanvat1())]

            # Môn phái nhân vật cùng máy (kể cả bản thân) để chỉ buff loại châm phù hợp
            monphaicungmay_map = self._laymonphainhanvatcungmay()
            monphaicungmay_map[idnguoichoi] = tenmonphai

            diachicosodoituongnguoichoi_map = {}
            danhsachdoituonghoples = []

            diachicosobanthan = self.moitruong.get_diachicosothongtinnhanvat1()
            if diachicosobanthan:
                tenbanthan = self.moitruong.get_tendoituong(diachicosobanthan)
                if tenbanthan:
                    diachicosodoituongnguoichoi_map[tenbanthan] = diachicosobanthan

            i = -1
            while True:
                i += 1
                diachidoituongdangxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachidoituongdangxemxet:
                    break
                if not self.moitruong.get_is_nhanvattontai(diachidoituongdangxemxet):
                    continue
                if self.moitruong.get_is_nhanvatchuasansang(diachidoituongdangxemxet):
                    continue

                is_muctieudangxemxetlanguoichoi = self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet)
                is_dongdoi = False
                if is_muctieudangxemxetlanguoichoi:
                    idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
                    is_dongdoi = (idnguoichoi == idnguoichoidangxemxet) or (idnguoichoithanhviennhoms and idnguoichoidangxemxet in idnguoichoithanhviennhoms) or (idnguoichoidangxemxet in laynhanvattodoitudongs())
                else:
                    # Bảo thú của mình / đồng đội xét theo chủ nhân: không thì bị lọc như quái (ngoài danh sách tấn công, bản đồ không PK...)
                    is_dongdoi = self._is_baothudongdoi(diachidoituongdangxemxet, idnguoichoi, idnguoichoithanhviennhoms)

                if not self._kiemtramuctieuhoplemonphai(diachidoituongdangxemxet, is_dongdoi = is_dongdoi):
                    continue

                if is_anhhuongboimuctieutheosau:
                    if self.moitruong.get_khoangcachdiem(*toadotheosau, diachidoituongdangxemxet) > khoangcachchophepmuctieutheosau:
                        continue

                khoangcachhientai = self.moitruong.get_khoangcach(diachidoituongdangxemxet)
                if khoangcachhientai >= KHOANGCACHTOANMANHINH:
                    continue
                if idbandohientai == BANDO_CHIENTRUONG and self.moitruong.get_idphechientruong() != self.moitruong.get_idphechientruong(diachidoituongdangxemxet):
                    continue

                is_nguoichoi = self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet)
                is_baothu = self.moitruong.get_is_baothukynangtrieuhoi(diachidoituongdangxemxet) or self.moitruong.get_is_baothugiangho(diachidoituongdangxemxet)
                tendoituong = self.moitruong.get_tendoituong(diachidoituongdangxemxet)

                if is_nguoichoi:
                    diachicosodoituongnguoichoi_map[tendoituong] = diachidoituongdangxemxet

                    idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
                    is_dongdoi = (idnguoichoi == idnguoichoidangxemxet) or (idnguoichoithanhviennhoms and idnguoichoidangxemxet in idnguoichoithanhviennhoms) or (idnguoichoidangxemxet in laynhanvattodoitudongs())

                    if not is_dongdoi and self.moitruong.get_is_cothetancong(diachidoituongdangxemxet):
                        idloaivukhi = self.moitruong.get_idloaivukhi(diachidoituongdangxemxet)

                        if idloaivukhi in (IDLOAIVUKHI_DAO, IDLOAIVUKHI_KIEM):
                            if khoangcachhientai < khoangcachphonganthuatgannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0):
                                diachidoituongcanbuffphonganthuat = diachidoituongdangxemxet
                                khoangcachphonganthuatgannhat = khoangcachhientai

                        if idloaivukhi != IDLOAIVUKHI_KIEM:
                            if khoangcachhientai < khoangcachhuyenquanggannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0):
                                diachidoituongcanbuffhuyenquangthiemanh = diachidoituongdangxemxet
                                khoangcachhuyenquanggannhat = khoangcachhientai

                if is_nguoichoi or is_baothu:
                    danhsachdoituonghoples.append({
                        "diachi": diachidoituongdangxemxet,
                        "is_nguoichoi": is_nguoichoi,
                        "is_baothu": is_baothu
                    })

            for doituong in danhsachdoituonghoples:
                diachicosodoituongxemxet = doituong["diachi"]
                priority = -1

                if doituong["is_nguoichoi"]:
                    idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachicosodoituongxemxet)
                    if idnguoichoidangxemxet == idnguoichoi:
                        continue
                    if idnguoichoithanhviennhoms and idnguoichoidangxemxet in idnguoichoithanhviennhoms:
                        priority = 1
                    elif idnguoichoidangxemxet in laynhanvattodoitudongs():
                        priority = 2

                elif doituong["is_baothu"]:
                    tendoituongchunhan = self.moitruong.get_tenchunhan(diachicosodoituongxemxet)
                    if tendoituongchunhan and tendoituongchunhan in diachicosodoituongnguoichoi_map:
                        diachicosodoituongchunhan = diachicosodoituongnguoichoi_map[tendoituongchunhan]
                        idnguoichoichunhan = self.moitruong.get_idnguoichoi(diachicosodoituongchunhan)

                        if idnguoichoichunhan == idnguoichoi:
                            priority = 1
                        elif idnguoichoithanhviennhoms and idnguoichoichunhan in idnguoichoithanhviennhoms:
                            priority = 1
                        elif idnguoichoichunhan in laynhanvattodoitudongs():
                            priority = 2

                if priority != -1:
                    danhsachungviens.append((priority, diachicosodoituongxemxet))

            danhsachungviens.sort(key = lambda x: x[0])

            for item in danhsachungviens:
                priority, diachidoituongdangxemxet = item
                is_uutiennhom = priority <= 1
                is_uutienbang = priority == 2

                is_nguoichoi_hientai = self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet)

                if self.moitruong.get_is_nhanvatdachet(diachidoituongdangxemxet):
                    if idbandohientai == BANDO_CHIENTRUONG:
                        continue
                    if is_nguoichoi_hientai:
                        idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
                        if time.time() - self._thoidiemcaituhoansinh_map.get(idnguoichoidangxemxet, 0) > 5.0:
                            if is_uutiennhom and not diachidoituongcanhoisinh:
                                diachidoituongcanhoisinh = diachidoituongdangxemxet
                            elif is_uutienbang and not diachidoituongcanhoisinhduphong:
                                diachidoituongcanhoisinhduphong = diachidoituongdangxemxet
                    continue

                is_cantaytran = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCCOT, HIEUUNGKYNANG_THUCGIAP, HIEUUNGKYNANG_THIEUDOT, HIEUUNGKYNANG_THAUCOTDINH, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0)

                if is_cantaytran:
                    if is_uutiennhom and not diachidoituongcanbufftaytranquyet:
                        diachidoituongcanbufftaytranquyet = diachidoituongdangxemxet
                    elif is_uutienbang and not diachidoituongcanbufftaytranquyetduphong:
                        diachidoituongcanbufftaytranquyetduphong = diachidoituongdangxemxet

                is_cantaytran2 = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCTAM, HIEUUNGKYNANG_LACKICH, HIEUUNGKYNANG_DONGBANG), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0)

                if is_cantaytran2:
                    if is_uutiennhom and not diachidoituongcanbufftaytranquyet2:
                        diachidoituongcanbufftaytranquyet2 = diachidoituongdangxemxet
                    elif is_uutienbang and not diachidoituongcanbufftaytranquyet2duphong:
                        diachidoituongcanbufftaytranquyet2duphong = diachidoituongdangxemxet

                is_dangbithieudot = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0)

                if is_uutiennhom and is_dangbithieudot:
                    if not diachidoituongcanbufflinhkhihothe and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LINHKHIHOTHE,), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1):
                        diachidoituongcanbufflinhkhihothe = diachidoituongdangxemxet

                phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai(diachidoituongdangxemxet)
                is_khongbithieudot = not is_dangbithieudot
                is_datinhcuongluc = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                is_dangbatpk = self.moitruong.get_idmaupk() != MAUPK_HOABINH

                if is_khongbithieudot and (phantramsinhlucconlai <= 35 or ((not is_datinhcuongluc or is_dangbatpk) and phantramsinhlucconlai <= 75)):
                    danhsachcanbommau.append((diachidoituongdangxemxet, self.moitruong.get_toado(diachidoituongdangxemxet)))
                    if is_uutiennhom:
                        if phantramsinhlucconlai < phantramsinhlucthapnhat:
                            phantramsinhlucthapnhat = phantramsinhlucconlai
                            diachidoituongcanbommau = diachidoituongdangxemxet
                    elif is_uutienbang:
                        if phantramsinhlucconlai < phantramsinhlucthapnhatduphong:
                            phantramsinhlucthapnhatduphong = phantramsinhlucconlai
                            diachidoituongcanbommauduphong = diachidoituongdangxemxet

                if is_uutienbang:
                    continue

                if phantramsinhlucconlai >= 25. or idbandohientai in BANDOKHONGPKs:
                    monphaidangxemxet = monphaicungmay_map.get(self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)) if is_nguoichoi_hientai else None
                    tenbaothu = "" if is_nguoichoi_hientai else (self.moitruong.get_tendoituong(diachidoituongdangxemxet) or "")
                    if not diachidoituongcanbuffngancham and monphaidangxemxet not in MONPHAICHIBUFFKIMCHAMs \
                            and not tenbaothu.startswith(BAOTHUCHIBUFFKIMCHAMs):
                        is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                        if is_thieuhieuung:
                            diachidoituongcanbuffngancham = diachidoituongdangxemxet

                    if not diachidoituongcanbuffkimcham and monphaidangxemxet not in MONPHAICHIBUFFNGANCHAMs \
                            and not tenbaothu.startswith(BAOTHUCHIBUFFNGANCHAMs):
                        is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                        if is_thieuhieuung:
                            diachidoituongcanbuffkimcham = diachidoituongdangxemxet

                    if not diachidoituongcanbuffcuongthethuat:
                        is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CUONGTHETHUAT,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                        if is_thieuhieuung:
                            diachidoituongcanbuffcuongthethuat = diachidoituongdangxemxet

            if not diachidoituongcanhoisinh:
                diachidoituongcanhoisinh = diachidoituongcanhoisinhduphong
            if not diachidoituongcanbufftaytranquyet:
                diachidoituongcanbufftaytranquyet = diachidoituongcanbufftaytranquyetduphong
            if not diachidoituongcanbommau:
                diachidoituongcanbommau = diachidoituongcanbommauduphong

            # Khiết Vân Quyết hồi máu 3x3 ô quanh mục tiêu: chỉ dùng khi tâm phủ được ít nhất 2 đối tượng cần bơm máu, không thì để Sơ Trị
            diachidoituongkhietvanquyet = None
            soluongphutotnhat = 1
            for diachitam, (xtam, ytam) in danhsachcanbommau:
                soluongphu = sum(1 for _, (x, y) in danhsachcanbommau if abs(x - xtam) <= 1 and abs(y - ytam) <= 1)
                if soluongphu > soluongphutotnhat:
                    soluongphutotnhat = soluongphu
                    diachidoituongkhietvanquyet = diachitam

            if not diachidoituongcanbufftaytranquyet2:
                diachidoituongcanbufftaytranquyet2 = diachidoituongcanbufftaytranquyet2duphong

            self._diachidoituongcanhoisinhvanmongcoc = diachidoituongcanhoisinh
            self._diachidoituongcanbufftaytranquyetvanmongcoc = diachidoituongcanbufftaytranquyet
            self._diachidoituongcanbufftaytranquyet2vanmongcoc = diachidoituongcanbufftaytranquyet2
            self._diachidoituongcanbufflinhkhihothevanmongcoc = diachidoituongcanbufflinhkhihothe
            self._diachidoituongcanbommauvanmongcoc = diachidoituongcanbommau
            self._diachidoituongkhietvanquyetvanmongcoc = diachidoituongkhietvanquyet
            self._diachidoituongcanbuffkimchamvanmongcoc = diachidoituongcanbuffkimcham
            self._diachidoituongcanbuffnganchamvanmongcoc = diachidoituongcanbuffngancham
            self._diachidoituongcanbuffcuongthethuatvanmongcoc = diachidoituongcanbuffcuongthethuat

            self._diachidoituongcanbuffphonganthuatvanmongcoc = diachidoituongcanbuffphonganthuat
            self._diachidoituongcanbuffhuyenquangthiemanhvanmongcoc = diachidoituongcanbuffhuyenquangthiemanh

            self._is_khongcongidebuff = not any([
                self._diachidoituongcanhoisinhvanmongcoc,
                self._diachidoituongcanbufftaytranquyetvanmongcoc,
                self._diachidoituongcanbommauvanmongcoc,
                self._diachidoituongcanbufftaytranquyet2vanmongcoc,
                self._diachidoituongcanbuffkimchamvanmongcoc,
                self._diachidoituongcanbuffnganchamvanmongcoc,
                self._diachidoituongcanbuffcuongthethuatvanmongcoc,
                self._diachidoituongcanbuffphonganthuatvanmongcoc,
                self._diachidoituongcanbuffhuyenquangthiemanhvanmongcoc
            ])

    def _tinhkhoangcachdendoanthang(self, px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.dist((px, py), (x1, y1))

        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)

        t = max(0, min(1, t))

        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy

        return math.dist((px, py), (nearest_x, nearest_y))

    def _kiemtraketgomquai(self, idmuctieu, khoangcach):
        # Quái sau tường: đường chim bay thì gần nhưng chạy mãi không lại gần hơn. Trả về True nếu bị kẹt.
        thoidiemhientai = time.time()
        # Đang bận việc khác (nhặt đồ ưu tiên, đứng im dùng skill) thì không tính là kẹt
        is_dangbanviec = self._is_danguutiennhatdo or self.moitruong.get_is_nhanvatbichoang() or self.moitruong.get_is_nhanvatbibatdong() or self.moitruong.get_is_bigiutrongtrando() or thoidiemhientai - self._thoidiemtamngungdichuyensudungkynang < 0.
        if idmuctieu != self._idgomtheodoiket or is_dangbanviec or khoangcach < self._khoangcachgomtotnhat - 0.5:
            self._idgomtheodoiket = idmuctieu
            self._khoangcachgomtotnhat = khoangcach
            self._thoidiemgomcaithiengannhat = thoidiemhientai
            return False
        return thoidiemhientai - self._thoidiemgomcaithiengannhat > 2.5

    def _boquaquaibichan(self, idquai):
        print(f"[GOM] Quái {hex(idquai)} bị chặn (tường/vật cản) -> Bỏ qua 120s")
        self._idmuctieubiloi_map[idquai] = time.time()
        self._ghimuctieuboqua(idquai, "Gom: bị chặn")
        self._danhsachidquaidagom.discard(idquai)
        if self._idquaidautien == idquai:
            self._idquaidautien = 0
        if self._idquaidangkeo == idquai:
            self._idquaidangkeo = 0
        self._idgomtheodoiket = 0
        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if diachimuctieudangchon and self.moitruong.get_iddoituong(diachimuctieudangchon) == idquai:
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

    def _is_nhuongquaichodongdoi(self, toadoquai, khoangcachtoiquai, dongdois):
        # dongdois: [(tọa độ, id người chơi)] từ _laytoadodongdoikhacnhom
        # - Đồng đội ID nhỏ hơn được ưu tiên: mình tránh hẳn mọi quái trong vùng BANKINHVUNGNHUONGQUAIDONGDOI quanh nó
        #   (chỉ một bên nhường nên không có chuyện cả hai cùng nhường rồi cùng đứng im)
        # - Còn lại: quái ở sát đồng đội (<= 9) và gần nó hơn mình thì để cho nó
        idbanthan = self.moitruong.get_idnguoichoi()
        for toadodongdoi, iddongdoi in dongdois:
            khoangcachdongdoi = math.dist(toadoquai, toadodongdoi)
            if iddongdoi < idbanthan and khoangcachdongdoi <= BANKINHVUNGNHUONGQUAIDONGDOI:
                return True
            if khoangcachdongdoi <= 9.0 and khoangcachdongdoi < khoangcachtoiquai:
                return True
        return False

    def _is_diemtrongvungdongdoiuutien(self, x, y, dongdois):
        idbanthan = self.moitruong.get_idnguoichoi()
        return any(iddongdoi < idbanthan and math.dist((x, y), toadodongdoi) <= BANKINHVUNGNHUONGQUAIDONGDOI for toadodongdoi, iddongdoi in dongdois)

    def _layidthanhviendangtheosau(self, idthanhviennhoms):
        # Thành viên cùng nhóm (trừ trưởng nhóm) chạy cùng máy và đang bật tự động theo sau; máy khác thì không biết nên coi như không theo
        idtruongnhom = self.moitruong.get_idnguoichoitruongnhom()
        if self.shared_data is None:
            return set()
        try:
            danhsach = list(self.shared_data.values())
        except Exception:
            return set()
        return {info.get("idnguoichoi") for info in danhsach
                if isinstance(info, dict) and info.get("_is_tudongtheosau")
                and info.get("idnguoichoi") in idthanhviennhoms and info.get("idnguoichoi") != idtruongnhom}

    def _laytoadodongdoikhacnhom(self):
        # Nhân vật của mình (danh sách tổ đội tự động) đang ở gần => tránh giành quái của nhau, cùng nhóm hay khác nhóm đều vậy.
        # Riêng việc theo sau thì phải đứng gần nhau: mình đang theo sau thì không nhường ai, và không nhường cho thành viên đang theo sau
        # Trả về [(tọa độ, id người chơi)]
        is_dangnamtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        if self._layidmuctieutheosau():
            return []
        idnhanvathientai = self.moitruong.get_idnguoichoi()
        idthanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms() if is_dangnamtrongnhom else []
        idbotheosaus = self._layidthanhviendangtheosau(idthanhviennhoms) if idthanhviennhoms else set()
        toadodongdois = []
        i = -1
        while True:
            i += 1
            diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituong:
                break
            if not self.moitruong.get_is_nhanvattontai(diachidoituong) or not self.moitruong.get_is_nguoichoi(diachidoituong):
                continue
            idnguoichoi = self.moitruong.get_idnguoichoi(diachidoituong)
            if idnguoichoi in laynhanvattodoitudongs() and idnguoichoi != idnhanvathientai and idnguoichoi not in idbotheosaus:
                toadodongdois.append((self.moitruong.get_toado(diachidoituong), idnguoichoi))
        return toadodongdois

    def action_tudongxulygomquai(self):
        yeucaugomquaimoi = None

        # Chỉ đánh người chơi thì quái không phải mục tiêu, gom về cũng không đánh
        if not self._is_tudonggomquai or not self._is_tudongsudungkynang or self._is_chidanhnguoichoi:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            self._danhsachidquaidagom.clear()
            self._idquaidautien = 0
            return

        idbandohientai = self.moitruong.get_idbandohientai()

        # Sư môn / phó bản / Sư Gia: bản đồ đang đánh không nằm trong lộ trình điểm đánh của nhân vật mà vẫn phải gom
        if self._is_tudongvebanrac and self._diemdanhxungquanhs and not self._is_bolotrinhdiemdanh():
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if danhsachbandohople and idbandohientai not in danhsachbandohople:
                self._is_danggomquai = False
                self._yeucaugomquai = None
                self._idquaidangkeo = 0
                self._danhsachidquaidagom.clear()
                self._idquaidautien = 0
                return

        if idbandohientai in BANDOKHONGPKs:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            return

        if time.time() - self._thoidiemloggomquai > 1.5:
            self._thoidiemloggomquai = time.time()
        is_canghilog = False
        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_dangvankhi() or idbandohientai in BANDOKHONGPKs:
            self._yeucaugomquai = None
            return

        if len(self._danhsachidquaidagom) == 0:
            self._idquaidautien = 0
            # Đánh xong đám (hoặc chưa gom gì) thì lượt gom sau đánh dấu lại từ đầu
            if not self._is_danggomquai:
                self._danhsachidquaidagommotlan.clear()

        # Tập Kích Môn Phái: không theo số tối thiểu, gom tới khi mọi quái thấy được đều đã gom 1 lần (con rớt lại không kéo lại)
        is_gomhetquaithay = self.moitruong.get_is_bandotapkichmonphai()

        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if diachimuctieudangchon:
            if self.moitruong.get_is_nguoichoi(diachimuctieudangchon) or self.moitruong.get_is_baothukynangtrieuhoi(diachimuctieudangchon) or self.moitruong.get_is_baothugiangho(diachimuctieudangchon):
                self._is_danggomquai = False
                self._yeucaugomquai = None
                self._idquaidangkeo = 0
                self._danhsachidquaidagom.clear()
                self._idquaidautien = 0
                return

        diachiquaidautien = 0
        khoangcachneohientai = 0.0

        if self._idquaidautien > 0:
            diachiquaidautien = self.moitruong.action_timkiemnhanvat(iddoituong = self._idquaidautien)

            if not diachiquaidautien or self.moitruong.get_is_nhanvatdachet(diachiquaidautien):
                if is_canghilog: print(f"[GOM] Neo {hex(self._idquaidautien)} chết/mất -> Xóa")
                if self._idquaidautien in self._danhsachidquaidagom:
                    self._danhsachidquaidagom.remove(self._idquaidautien)
                self._idquaidautien = 0
                diachiquaidautien = 0
            else:
                khoangcachneohientai = self.moitruong.get_khoangcach(diachiquaidautien)
                if khoangcachneohientai > 18.0:
                    if is_canghilog: print(f"[GOM] Neo rớt quá xa (>18m) -> Reset Neo")
                    self._idquaidautien = 0
                    diachiquaidautien = 0
                    khoangcachneohientai = 0.0

        if self._idquaidautien == 0 and len(self._danhsachidquaidagom) > 0:
            idungvien = 0
            khoangcachungviennhonhat = 9999.
            diachiungvien = 0

            for id_mob in list(self._danhsachidquaidagom):
                addr_mob = self.moitruong.action_timkiemnhanvat(iddoituong = id_mob)
                if addr_mob and not self.moitruong.get_is_nhanvatdachet(addr_mob):
                    kc = self.moitruong.get_khoangcach(addr_mob)
                    if kc < khoangcachungviennhonhat:
                        khoangcachungviennhonhat = kc
                        idungvien = id_mob
                        diachiungvien = addr_mob
                else:
                    self._danhsachidquaidagom.remove(id_mob)

            if idungvien != 0:
                self._idquaidautien = idungvien
                diachiquaidautien = diachiungvien
                khoangcachneohientai = khoangcachungviennhonhat
                if is_canghilog: print(f"[GOM] Bầu Neo mới: {hex(idungvien)} (KC: {round(khoangcachungviennhonhat, 1)}m)")

        i = -1
        soluongquaigan = 0

        idquaicankeogannhat = 0
        khoangcachquaicankeo = 9999.
        diachicosoquaicankeo = 0

        is_coquaixungquanh = False

        # Quái chưa kéo gần neo nhất (dùng khi đủ số mà vẫn kéo thêm), và quái đang kéo nếu còn trong danh sách xét: (id, địa chỉ, khoảng cách tới mình, tới neo)
        quaikeothemgannhat = None
        quaidangkeo = None

        idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if time.time() - v > 120.0]
        for k in idcanxoas:
            del self._idmuctieubiloi_map[k]

        # Tập Kích: neo rớt lại cũng không quay về đón, kéo tiếp cho đỡ chạy qua chạy lại (xong mới tụ về neo)
        is_neobirotlai = (diachiquaidautien and khoangcachneohientai > 12.0 and not is_gomhetquaithay)

        # Chỉ khi bật farm & bán rác: quái gần nhân vật khác trong danh sách tổ đội tự động hơn mình thì nhường.
        # Không bật farm & bán rác thì không nhường gì cả.
        toadobanthan = self.moitruong.get_toado()
        toadodongdois = self._laytoadodongdoikhacnhom() if self._is_tudongvebanrac else []

        while True:
            i += 1
            diachidoituongxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituongxemxet: break

            if not self.moitruong.get_is_cothetancong(diachidoituongxemxet): continue
            if self.moitruong.get_idloainhanvat(diachidoituongxemxet) != LOAIMUCTIEU_QUAIVATHOACNPC: continue

            tendoituongxemxet = self.moitruong.get_tendoituong(diachidoituongxemxet)
            if self._is_tenbiboqua(tendoituongxemxet) or self.moitruong.get_is_quairiengnguoikhac(tendoituongxemxet):
                continue
            if self._laytenmuctieutancongs() and tendoituongxemxet not in self._laytenmuctieutancongs():
                continue

            toadoquai = self.moitruong.get_toado(diachidoituongxemxet)
            if self._kiemtra_divaovungcam(*toadoquai):
                continue
            if not self._kiemtra_tamdiemdanh(*toadoquai):
                continue

            iddoituongquai = self.moitruong.get_iddoituong(diachidoituongxemxet)

            if toadodongdois:
                khoangcachtoiquai = math.dist(toadoquai, toadobanthan)
                if self._is_nhuongquaichodongdoi(toadoquai, khoangcachtoiquai, toadodongdois):
                    self._danhsachidquaidagom.discard(iddoituongquai)
                    if self._idquaidautien == iddoituongquai:
                        self._idquaidautien = 0
                        diachiquaidautien = 0
                    continue

            if iddoituongquai in self._idmuctieubiloi_map:
                continue

            khoangcach = self.moitruong.get_khoangcach(diachidoituongxemxet)

            if khoangcach < KHOANGCACHTOANMANHINH:
                is_coquaixungquanh = True

            if iddoituongquai in self._danhsachidquaidagom:
                if khoangcach > 12.0:
                    if is_canghilog: print(f"[GOM] Quái {hex(iddoituongquai)} rớt lại (>12m) -> Xóa để đón")
                    self._danhsachidquaidagom.remove(iddoituongquai)
                    if iddoituongquai == self._idquaidautien:
                        self._idquaidautien = 0
                        diachiquaidautien = 0
                else:
                    if khoangcach <= 6.0: soluongquaigan += 1
                continue

            if khoangcach <= 4.5:
                self._danhsachidquaidagom.add(iddoituongquai)
                self._danhsachidquaidagommotlan.add(iddoituongquai)
                if self._idquaidautien == 0:
                    self._idquaidautien = iddoituongquai
                    diachiquaidautien = diachidoituongxemxet
                    khoangcachneohientai = khoangcach
                soluongquaigan += 1
                continue

            if is_gomhetquaithay and iddoituongquai in self._danhsachidquaidagommotlan:
                continue

            # Tập Kích: mọi con thấy được (chưa gom lần nào) đều phải kéo, không giới hạn 15m / cách neo 18m
            if not is_neobirotlai and (khoangcach <= 15.0 or (is_gomhetquaithay and khoangcach < KHOANGCACHTOANMANHINH)) and iddoituongquai not in self._danhsachidquaidagom:
                is_thoamandieukienneo = True
                khoangcachneo = khoangcach
                if diachiquaidautien:
                    khoangcachneo = self.moitruong.get_khoangcach(diachidoituongxemxet, diachiquaidautien)
                    if khoangcachneo > 18.0 and not is_gomhetquaithay: is_thoamandieukienneo = False

                if is_thoamandieukienneo:
                    if khoangcach < khoangcachquaicankeo:
                        khoangcachquaicankeo = khoangcach
                        idquaicankeogannhat = iddoituongquai
                        diachicosoquaicankeo = diachidoituongxemxet
                    if not quaikeothemgannhat or khoangcachneo < quaikeothemgannhat[3]:
                        quaikeothemgannhat = (iddoituongquai, diachidoituongxemxet, khoangcach, khoangcachneo)
                    if iddoituongquai == self._idquaidangkeo:
                        quaidangkeo = (iddoituongquai, diachidoituongxemxet, khoangcach, khoangcachneo)

        # Giữ con đang kéo nếu nó không xa hơn con gần nhất quá 2m, khỏi đổi đích qua lại giữa các con gần ngang nhau
        if quaidangkeo and quaidangkeo[2] <= khoangcachquaicankeo + 2.0:
            idquaicankeogannhat, diachicosoquaicankeo, khoangcachquaicankeo = quaidangkeo[:3]

        soluongquaidagom = len(self._danhsachidquaidagom)

        if idquaicankeogannhat == 0 and not is_neobirotlai:
            diachinhanvatmuctieudangchon = diachimuctieudangchon
            if diachinhanvatmuctieudangchon and self.moitruong.get_is_nhanvattontai(diachinhanvatmuctieudangchon) and self.moitruong.get_is_cothetancong(diachinhanvatmuctieudangchon):
                if self.moitruong.get_idloainhanvat(diachinhanvatmuctieudangchon) == LOAIMUCTIEU_QUAIVATHOACNPC:
                    id_target = self.moitruong.get_iddoituong(diachinhanvatmuctieudangchon)
                    kc_target = self.moitruong.get_khoangcach(diachinhanvatmuctieudangchon)
                    toadotarget = self.moitruong.get_toado(diachinhanvatmuctieudangchon)
                    is_dongdoigannhuong = self._is_nhuongquaichodongdoi(toadotarget, kc_target, toadodongdois)
                    is_dagommotlan = is_gomhetquaithay and id_target in self._danhsachidquaidagommotlan
                    if id_target not in self._danhsachidquaidagom and not is_dagommotlan and id_target not in self._idmuctieubiloi_map and 12.0 < kc_target < KHOANGCACHTOANMANHINH and not is_dongdoigannhuong:
                        idquaicankeogannhat = id_target
                        diachicosoquaicankeo = diachinhanvatmuctieudangchon
                        khoangcachquaicankeo = kc_target
                        if is_canghilog: print(f"[GOM] dự phòng mục tiêu: {hex(idquaicankeogannhat)}")

        if not is_coquaixungquanh:
            self._danhsachidquaidagom.clear()
            self._danhsachidquaidagommotlan.clear()
            self._idquaidautien = 0

        if is_canghilog:
            neo_str = f"{hex(self._idquaidautien)}" if self._idquaidautien else "None"
            neo_kc = f"({round(khoangcachneohientai, 1)}m)" if self._idquaidautien else ""
            print(f"[GOM] Neo: {neo_str}{neo_kc} | List: {soluongquaidagom} | Gần: {soluongquaigan}/{self._soluongquaigomtoithieu} | Target: {hex(idquaicankeogannhat) if idquaicankeogannhat else 'None'}")

        if soluongquaidagom == 0 and idquaicankeogannhat == 0:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            return

        if is_gomhetquaithay:
            # Còn con thấy được chưa gom lần nào (idquaicankeogannhat) thì kéo tiếp, không dừng vì đủ số; quá tải nâng lên 50
            is_dusoluongquaigan = idquaicankeogannhat == 0
            is_quatai = soluongquaidagom >= 20
        else:
            is_dusoluongquaigan = soluongquaigan >= self._soluongquaigomtoithieu
            is_quatai = soluongquaidagom >= 20

        # Số tối thiểu chỉ là ngưỡng dưới: đang chạy gom, đủ số mà sát đám đang gom vẫn còn quái chưa kéo thì kéo nốt, chưa dừng lại đánh.
        # Đã dừng lại đánh thì giữ như cũ (quái tự lại gần <= 4.5m vẫn được tính vào đám)
        # Chọn theo khoảng cách tới neo (không phải tới mình), ưu tiên giữ con đang kéo, để không nhảy qua lại giữa kéo thêm và tụ về neo
        if self._is_danggomquai and is_dusoluongquaigan and not is_quatai and not is_neobirotlai:
            quaikeothem = quaidangkeo if quaidangkeo and quaidangkeo[3] <= BANKINHKEOTHEMGOMQUAI else quaikeothemgannhat
            if quaikeothem and quaikeothem[3] <= BANKINHKEOTHEMGOMQUAI:
                idquaicankeogannhat, diachicosoquaicankeo, khoangcachquaicankeo = quaikeothem[:3]
                is_dusoluongquaigan = False
                if is_canghilog: print(f"[GOM] Đủ {soluongquaigan} gần nhưng còn {hex(idquaicankeogannhat)} cách đám {round(quaikeothem[3], 1)}m -> Kéo thêm")
        is_khongkeoduocnua = (idquaicankeogannhat == 0 and soluongquaidagom > 0)
        is_dangdanh = (not self._is_danggomquai and soluongquaidagom > 0)

        if is_dusoluongquaigan or is_quatai or is_khongkeoduocnua or is_dangdanh or is_neobirotlai:
            is_canluive = False
            lydolui = ""

            if diachiquaidautien:
                if (is_dusoluongquaigan or is_quatai) and khoangcachneohientai > 4.5:
                    is_canluive = True
                    lydolui = "Tụ quái"
                elif is_neobirotlai:
                    is_canluive = True
                    lydolui = "Đón Neo"

            if is_canluive:
                if is_canghilog: print(f"[GOM] {lydolui}: Quay lại Neo ({round(khoangcachneohientai, 1)}m)")

                if self._kiemtraketgomquai(self._idquaidautien, khoangcachneohientai):
                    self._boquaquaibichan(self._idquaidautien)
                    self._yeucaugomquai = None
                    return

                x_neo, y_neo = self.moitruong.get_toado(diachiquaidautien, )

                yeucaugomquaimoi = {
                    "yeucau": YEUCAUDICHUYENGOMQUAI,
                    "toadodich": (x_neo, y_neo),
                    "khoangcachtoida": 3.0,
                    "idmuctieu": self._idquaidautien,
                    "diachimuctieu": diachiquaidautien
                }
            else:
                if not is_neobirotlai:
                    if self._is_danggomquai and is_canghilog:
                        print(f"[GOM] >>> ĐỦ ({soluongquaigan} gần) & TỤ XONG -> ĐÁNH <<<")
                    self._is_danggomquai = False
                    self._yeucaugomquai = None
                    self._idquaidangkeo = 0
                    if soluongquaidagom == 0: self._danhsachidquaidagom.clear()
                    return

        if not self._is_danggomquai and is_canghilog:
            print("[GOM] >>> BẮT ĐẦU CHẠY GOM")
        self._is_danggomquai = True

        if yeucaugomquaimoi:
            self._yeucaugomquai = yeucaugomquaimoi
            return

        if idquaicankeogannhat > 0:
            if diachicosoquaicankeo == 0:
                self._yeucaugomquai = None
                return

            if idquaicankeogannhat != self._idquaidangkeo:
                self._idquaidangkeo = idquaicankeogannhat
                self._thoidiembatdaukeo = time.time()

            # Trước đây hết 5s vẫn coi quái là đã gom (kể cả khi bị tường chặn) nên lại bầu nó làm neo và kẹt tiếp
            if khoangcachquaicankeo > 1.5 and (self._kiemtraketgomquai(idquaicankeogannhat, khoangcachquaicankeo) or time.time() - self._thoidiembatdaukeo > 8.0):
                self._boquaquaibichan(idquaicankeogannhat)
                self._yeucaugomquai = None
                return

            if khoangcachquaicankeo <= 1.5:
                self._danhsachidquaidagom.add(idquaicankeogannhat)
                self._danhsachidquaidagommotlan.add(idquaicankeogannhat)
                if self._idquaidautien == 0:
                    self._idquaidautien = idquaicankeogannhat
                yeucaugomquaimoi = None
                self._idquaidangkeo = 0
                if is_canghilog: print(f"[GOM] Đã tiếp cận {hex(idquaicankeogannhat)}")
            else:
                x_quai, y_quai = self.moitruong.get_toado(diachicosoquaicankeo, )

                if x_quai > 0 and y_quai > 0:
                    if is_canghilog: print(f"[GOM] SET MOVE -> {hex(idquaicankeogannhat)}")
                    yeucaugomquaimoi = {
                        "yeucau": YEUCAUDICHUYENGOMQUAI,
                        "toadodich": (x_quai, y_quai),
                        "khoangcachtoida": 0.,
                        "idmuctieu": idquaicankeogannhat,
                        "diachimuctieu": diachicosoquaicankeo
                    }
        else:
            yeucaugomquaimoi = None
            self._idquaidangkeo = 0

        self._yeucaugomquai = yeucaugomquaimoi
