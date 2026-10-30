# Phần di chuyển: giữ khoảng cách với kẻ tấn công, theo sau, đi tới bản đồ / phù, vùng cấm, điểm đánh, lộ trình mẫu, di chuyển tự do, Hồi Thành Phù.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import random
import time

from hangso_xq import *
from moitruong_xq import MoiTruong, DOUUTIEN_THAP, DOUUTIEN_KHANCAP, DOUUTIEN_CAO, SOLUONGDOITUONGXUNGQUANHTOIDA, tinh_is_huongmatvediem
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam
from tienich_xq import tailotrinhmau as util_tailotrinhmau, luulotrinhmau as util_luulotrinhmau
from dexuatlotrinh_xq import taiviquai as util_taiviquai, luuviquai as util_luuviquai, taiviquaibando, ghinhanvitriquai, dexuatlotrinh
from bando_xq import timduongbando, laynpcloidi
from dexuatlotrinh_xq import THOIGIANGHIVITRIQUAI, THOIGIANLUUVITRIQUAI, SOLANTHAYQUAITOITHIEU, TENMAUDEXUAT, TENMAUDO, dexuatlotrinhdo
from nhiemvu_xq import _laydiemcong as nhiemvu_laydiemcong, KHOANGCACHTRANHCONG
from tienich_xq import laynhomtodoitudongs, laynhanvattodoitudongs, donbangthoidiem


class TacTuDiChuyen:
    def _kiemtrathuchienvohieuhoadichuyen(self):
        if self._is_yeucauvohieuhoadichuyen:
            self.moitruong.action_vohieuhoadichuyen()
        else:
            self.moitruong.action_tatvohieuhoadichuyen()

    def _laydanhsachketancong(self, x1, y1):
        # Đối tượng đang tấn công mình: thù địch, ở gần, đang ra đòn (tư thế đánh thường / ra phép / khựng sau đòn) và quay mặt về mình.
        # Tư thế ra đòn nhấp nháy giữa các đòn nên nhớ THOIGIANNHOKETANCONG giây. Trả về [(x, y, khoảng cách)]
        thoidiemhientai = time.time()
        bankinhxet = self._khoangcachgiuketancong + 4.
        tenchunhanphe_map = {}
        ketancongs = []
        idthaytaichos = set()
        for diachi in self.moitruong._get_diachidoituongxungquanhs():
            idthaytaichos.add(self.moitruong.get_iddoituong(diachi))
            x, y = self.moitruong.get_toado(diachi)
            khoangcach = math.dist((x1, y1), (x, y))
            if khoangcach > bankinhxet:
                continue
            # Chỉ mục tiêu PK: người chơi / bảo thú triệu hồi / bảo thú giang hồ (bỏ quái)
            if self._is_giukhoangcachchimuctieupk and not (self.moitruong.get_is_nguoichoi(diachi) or self.moitruong.get_is_baothukynangtrieuhoi(diachi)
                                                           or self.moitruong.get_is_baothugiangho(diachi)):
                continue
            if not self._is_doituongthudich(diachi, tenchunhanphe_map):
                continue
            iddoituong = self.moitruong.get_iddoituong(diachi)
            if self.moitruong.get_idtuthenhanvat(diachi) in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) \
                    and self.moitruong.get_is_huongmatvediem(diachi, x1, y1):
                self._thoidiemketancong_map[iddoituong] = thoidiemhientai
            if thoidiemhientai - self._thoidiemketancong_map.get(iddoituong, 0.) <= THOIGIANNHOKETANCONG:
                ketancongs.append((x, y, khoangcach))

        # Cảnh báo sớm từ tầm nhìn chung: đối tượng thù địch nhân vật khác cùng máy thấy mà mình chưa thấy (ngoài tầm nhìn của mình).
        # Ngoài việc đang ra đòn quay mặt về mình, tính cả đang chạy về phía mình (lao tới) để lùi trước khi nó vào tầm
        for iddoituong, (x, y, tuthe, huong, is_muctieupk, _) in self._laytamnhinchung().items():
            if iddoituong in idthaytaichos:
                continue
            if self._is_giukhoangcachchimuctieupk and not is_muctieupk:
                continue
            khoangcach = math.dist((x1, y1), (x, y))
            if khoangcach > bankinhxet:
                continue
            if tuthe in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG, TUTHENHANVAT_DICHUYEN) \
                    and tinh_is_huongmatvediem(x, y, huong, x1, y1):
                self._thoidiemketancong_map[iddoituong] = thoidiemhientai
            if thoidiemhientai - self._thoidiemketancong_map.get(iddoituong, 0.) <= THOIGIANNHOKETANCONG:
                ketancongs.append((x, y, khoangcach))

        if len(self._thoidiemketancong_map) > 256:
            self._thoidiemketancong_map = donbangthoidiem(self._thoidiemketancong_map, THOIGIANNHOKETANCONG)
        return ketancongs

    def _tinhyeucaugiukhoangcach(self):
        # Kẻ tấn công gần hơn khoảng cách cần giữ thì di chuyển, không đứng yên cho nó đánh: ưu tiên hướng ngược với các kẻ tấn công
        # (kẻ càng gần càng nặng ký), bị vùng cấm / kẹt tường / mép vùng theo sau chặn thì lệch 45°, 90°, 135° (chạy ngang cũng được,
        # miễn không lại gần hơn). Luôn ở trong vùng quanh người theo sau; không còn hướng nào hợp lệ thì thôi không lùi
        x1, y1 = self.moitruong.get_toado()
        ketancongs = self._laydanhsachketancong(x1, y1)
        if not ketancongs:
            return None
        gannhat = min(k[2] for k in ketancongs)
        if gannhat >= self._khoangcachgiuketancong:
            return None
        # Còn kỹ năng quan trọng dùng được thì đứng lại dùng, chỉ lùi khi rảnh
        if not self._is_dangronggiukhoangcach():
            return None

        vx = vy = 0.
        for x, y, khoangcach in ketancongs:
            if khoangcach <= 0.:
                continue
            trongso = 1. / max(khoangcach, 0.5) ** 2
            vx += (x1 - x) / khoangcach * trongso
            vy += (y1 - y) / khoangcach * trongso
        dodai = math.hypot(vx, vy)
        if dodai <= 0.:
            # Đứng trùng chỗ kẻ tấn công / bị vây đều các phía: chọn hướng ngẫu nhiên
            goc = random.uniform(0, 2 * math.pi)
            vx, vy, dodai = math.cos(goc), math.sin(goc), 1.
        ux, uy = vx / dodai, vy / dodai
        buoc = min(6., max(2., self._khoangcachgiuketancong - gannhat + 1.5))

        toadotheosau = self._laytoadomuctieutheosau()
        bankinhtheosau = self._tinhtoanbankinhdungtancongtheosau() if toadotheosau else 0.

        # Hướng vừa lùi mà không nhích được (kẹt tường / vật cản: bot không có dữ liệu ô đi được) thì chặn hướng đó một lúc
        self._kiemtraketluigiukhoangcach(x1, y1)
        thoidiemhientai = time.time()

        for goclech in (0, 45, -45, 90, -90, 135, -135):
            r = math.radians(goclech)
            rx, ry = ux * math.cos(r) - uy * math.sin(r), ux * math.sin(r) + uy * math.cos(r)
            xd, yd = x1 + rx * buoc, y1 + ry * buoc
            # Đang theo trưởng nhóm: điểm lùi kẹp vào vùng quanh trưởng nhóm (không chạy ra rồi lại bị kéo về)
            if toadotheosau:
                khoangcachtheosau = math.dist((xd, yd), toadotheosau)
                if khoangcachtheosau > bankinhtheosau > 0.:
                    xd = toadotheosau[0] + (xd - toadotheosau[0]) * bankinhtheosau / khoangcachtheosau
                    yd = toadotheosau[1] + (yd - toadotheosau[1]) * bankinhtheosau / khoangcachtheosau
            if math.dist((x1, y1), (xd, yd)) < 1.:
                continue
            # Hướng thực tế (sau khi kẹp vào vùng theo sau) theo 8 hướng 45°
            huong = round(math.degrees(math.atan2(yd - y1, xd - x1)) / 45.) % 8
            if thoidiemhientai < self._thoidiemhetchanhuonglui_map.get(huong, 0.):
                continue
            if self._kiemtra_divaovungcam(xd, yd):
                continue
            # Mục đích là không đứng yên cho đối phương đánh: chạy ngang trong vùng cho phép cũng được,
            # chỉ không được lại gần kẻ tấn công hơn chỗ đang đứng (thứ tự thử đã ưu tiên chạy thẳng ra xa trước)
            if min(math.dist((xd, yd), (x, y)) for x, y, _ in ketancongs) < gannhat - 0.5:
                continue
            # Đổi hướng thì đo lại từ đầu xem có nhích được không
            if not self._luigiukhoangcachdangchay or self._luigiukhoangcachdangchay["huong"] != huong:
                self._luigiukhoangcachdangchay = {"huong": huong, "batdau": thoidiemhientai, "toado": (x1, y1)}
            return {
                "yeucau": YEUCAUDICHUYENGIUKHOANGCACH,
                "toadodich": (xd, yd),
                "khoangcachtoida": 0,
            }
        self._luigiukhoangcachdangchay = None
        return None

    def _kiemtraketluigiukhoangcach(self, x1, y1):
        # Đang lùi theo một hướng mà sau THOIGIANKETLUIGIUKHOANGCACH giây vẫn chưa nhích được 0.5 ô => kẹt, chặn hướng đó
        # THOIGIANCHANHUONGLUI giây để lần tính sau thử hướng lệch kế tiếp. Lúc bị giữ đứng yên (vận khí, ra chiêu...) không tính là kẹt
        dangchay = self._luigiukhoangcachdangchay
        if not dangchay:
            return
        thoidiemhientai = time.time()
        if self.moitruong.get_is_dangvankhi() or self.moitruong.get_is_nhanvatbichoang() or self.moitruong.get_is_nhanvatbibatdong() or self.moitruong.get_is_bigiutrongtrando() or thoidiemhientai - self._thoidiemtamngungdichuyensudungkynang < 0. \
                or (thoidiemhientai < self._thoidiemhetgiuchieudangra and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_TANCONGPHEPTHUAT):
            dangchay["batdau"], dangchay["toado"] = thoidiemhientai, (x1, y1)
            return
        if thoidiemhientai - dangchay["batdau"] < THOIGIANKETLUIGIUKHOANGCACH:
            return
        if math.dist((x1, y1), dangchay["toado"]) < 0.5:
            self._thoidiemhetchanhuonglui_map[dangchay["huong"]] = thoidiemhientai + THOIGIANCHANHUONGLUI
            self.moitruong._inlog(f"[GIỮ KHOẢNG CÁCH] kẹt hướng {dangchay['huong']} tại {(x1, y1)}, chặn {THOIGIANCHANHUONGLUI}s")
            self._luigiukhoangcachdangchay = None
        else:
            # Vẫn nhích được: đo tiếp từ chỗ mới
            dangchay["batdau"], dangchay["toado"] = thoidiemhientai, (x1, y1)

    def _capnhatkynangquantrong(self, tenmonphai, danhsachuutien, kynangchopheps = None):
        # Gọi trong danh sách kỹ năng của phái, trước vòng dùng kỹ năng: còn kỹ năng quan trọng (KYNANGQUANTRONGGIUKHOANGCACH_MAP)
        # hết hồi chiêu VÀ đủ điều kiện dùng (có mục tiêu thích hợp, đủ nội lực... đúng điều kiện trong danh sách) thì chưa lùi
        if not self._is_giukhoangcachketancong:
            return
        quantrongs = KYNANGQUANTRONGGIUKHOANGCACH_MAP.get(tenmonphai)
        if not quantrongs:
            return
        is_cokynangquantrong = False
        for item in danhsachuutien:
            vitrikynang, loaikynang, dieukien = item[0], item[1], item[2]
            if vitrikynang not in quantrongs or loaikynang.startswith("dichuyen"):
                continue
            if kynangchopheps is not None and vitrikynang not in kynangchopheps:
                continue
            if not self.moitruong.get_is_kynangsansang(vitrikynang):
                continue
            if callable(dieukien) and not dieukien():
                continue
            is_cokynangquantrong = True
            break
        self._is_cokynangquantrongdungduoc = is_cokynangquantrong
        self._thoidiemxetkynangquantronggannhat = time.time()

    def _laykhoakynangquantrong(self):
        # Thục Sơn Kiếm và Thục Sơn Đao cùng tên môn phái "thucson" nhưng khác ô kỹ năng => tách khoá
        tenmonphai = self.moitruong.get_tenmonphai()
        if tenmonphai == "thucson":
            return "thucsondao" if self._is_thucsondao else "thucsonkiem"
        return tenmonphai

    def _is_dangronggiukhoangcach(self):
        # Rảnh để lùi: phái không có kỹ năng quan trọng, hoặc mọi kỹ năng quan trọng đang hồi chiêu / không có mục tiêu thích hợp.
        # Kết quả xét đã cũ (danh sách kỹ năng không chạy: đang vận khí, tắt tự dùng kỹ năng...) thì coi như rảnh
        if not KYNANGQUANTRONGGIUKHOANGCACH_MAP.get(self._laykhoakynangquantrong()):
            return True
        if time.time() - self._thoidiemxetkynangquantronggannhat > THOIGIANHIEULUCKYNANGQUANTRONG:
            return True
        return not self._is_cokynangquantrongdungduoc

    def _capnhatyeucaugiukhoangcach(self):
        if not self._is_giukhoangcachketancong or self.moitruong.get_is_nhanvatdachet():
            self._yeucaugiukhoangcach = None
            self._luigiukhoangcachdangchay = None
            return
        if time.time() - self._thoidiemtinhgiukhoangcachgannhat < THOIGIANTINHGIUKHOANGCACH:
            return
        self._thoidiemtinhgiukhoangcachgannhat = time.time()
        try:
            self._yeucaugiukhoangcach = self._tinhyeucaugiukhoangcach()
        except Exception as e:
            print(f"[GIỮ KHOẢNG CÁCH] lỗi: {e}")
            self._yeucaugiukhoangcach = None
        # Không lùi nữa thì bỏ mốc đo kẹt: lần lùi sau (có khi cùng hướng, cùng chỗ đứng) đo lại từ đầu, không báo kẹt nhầm
        if not self._yeucaugiukhoangcach:
            self._luigiukhoangcachdangchay = None

    def action_xulyuutiendichuyen(self):
        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        # Đào Hoa Nguyên: máy chủ giữ lệnh "kill" cả khi di chuyển (chỉ đánh khi đã ở gần) nên không coi là đã tắt
        if idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self.moitruong.get_tenmonphai() != "daohoanguyen":
            self._is_battudongtancongvatly = False

        # Lớp chặn vùng cấm cuối cùng ở môi trường theo tùy chọn tránh vùng cấm
        self.moitruong.is_tranhvungcam = self._is_tranhvungcam

        self._kiemtrathuchienvohieuhoadichuyen()

        # Tính trước các lệnh chặn bên dưới để danh sách kỹ năng biết đang lùi (bỏ chiêu đánh, chỉ buff) kể cả lúc đang vận khí / ra chiêu
        self._capnhatyeucaugiukhoangcach()

        is_log = False

        # if time.time() - self._thoidiemlogdebug > 2.0:
        #     is_log = True
        #     self._thoidiemlogdebug = time.time()

        if self.moitruong.get_is_nhanvatdachet():
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Nhân vật đang CHẾT")
            return
        is_khongdiduoc = self.moitruong.get_is_nhanvatbichoang() or self.moitruong.get_is_nhanvatbibatdong()
        if is_khongdiduoc or self.moitruong.get_is_bigiutrongtrando():
            # Bị choáng / Hôn Mê / Bất Động / bị Trận Pháp Lạc Ảnh giữ: đo kẹt lại từ đầu để thời gian đứng im (hoặc bị giữ ở mép trận)
            # không bị tính là kẹt tường
            self._thoidiembatdaukiemtraket = time.time()
            self._toadokiemtraket = self.moitruong.get_toado()
        if is_khongdiduoc:
            # Không đi được: không gửi lệnh di chuyển (Bất Động vẫn ra chiêu với mục tiêu trong tầm)
            return
        if self.moitruong.get_is_dangclickchuottrai():
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang CLICK CHUỘT TRÁI")
            return
        if self.moitruong.get_is_dangvankhi() and not self._is_ngatvankhiloidongcuuthien():
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang VẬN KHÍ")
            return
        # Chiêu kéo dài tới hết tư thế ra chiêu (Ngự Kiếm Phi Tiên...): còn tư thế ra chiêu thì giữ đứng yên.
        # Đã thấy tư thế ra chiêu rồi mà hết (hoặc chờ quá THOIGIANCHONGATDICHUYENXUATCHIEU giây chưa thấy) thì bỏ giữ luôn,
        # kẻo lần ra phép khác sau đó cũng bị giữ
        is_giuchieudangra = False
        if self._thoidiemhetgiuchieudangra:
            if time.time() < self._thoidiemhetgiuchieudangra and idtuthenhanvat == TUTHENHANVAT_TANCONGPHEPTHUAT:
                is_giuchieudangra = True
                self._is_dathaychieudangra = True
            elif self._is_dathaychieudangra or time.time() - self._thoidiembatdaugiuchieudangra > THOIGIANCHONGATDICHUYENXUATCHIEU \
                    or time.time() >= self._thoidiemhetgiuchieudangra:
                self._thoidiemhetgiuchieudangra = 0.
        if time.time() - self._thoidiemtamngungdichuyensudungkynang < 0. or is_giuchieudangra:
            # Ngắt cả khi chưa ở tư thế di chuyển: đích tìm đường còn trong game thì ra chiêu xong game tự đi tiếp
            self.moitruong.action_ngatdichuyen()
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng để dùng SKILL")
            return
        if self._trangthaiveban != 0:
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng để về bán rác")
            return

        is_anhhuongboimuctieutheosau = bool(self._laytoadomuctieutheosau())

        is_yeucaunhatvatpham =self._yeucaunhatvatpham and not is_anhhuongboimuctieutheosau and time.time() - self._thoidiemvohieuquadichuyennhatvatpham > 0.

        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieudangchonlanguoichoi = diachimuctieudangchon and self.moitruong.get_is_nguoichoi(diachimuctieudangchon)
        is_muctieudangchonlabaothukynangtrieuhoi = self.moitruong.get_is_baothukynangtrieuhoi(diachimuctieudangchon)
        is_muctieudangchonlabaothugiangho = self.moitruong.get_is_baothugiangho(diachimuctieudangchon)
        is_muctieupk = is_muctieudangchonlanguoichoi or is_muctieudangchonlabaothukynangtrieuhoi or is_muctieudangchonlabaothugiangho

        yeucauduocchon = None
        lydochon = "KHÔNG CÓ"

        is_yeucaunhatvatphamganhon = False
        if is_yeucaunhatvatpham and not is_muctieupk and self._is_tudongvebanrac:
            khoangcachnhatvatpham = self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat) if self._diachicosovatphamdangnhat else KHOANGCACHTOIDAHOPLE
            khoangcachtancong = KHOANGCACHTOIDAHOPLE
            if self._yeucautancong and self._yeucautancong.get("diachimuctieu"):
                khoangcachtancong = self.moitruong.get_khoangcach(self._yeucautancong.get("diachimuctieu"))
            elif diachimuctieudangchon:
                khoangcachtancong = self.moitruong.get_khoangcach(diachimuctieudangchon)

            if khoangcachnhatvatpham + 0.5 < khoangcachtancong:
                is_yeucaunhatvatphamganhon = True

        # Vật phẩm ưu tiên (VATPHAMUUTIENNHATs) bỏ qua mọi điều kiện: mục tiêu PK, theo nhóm, khóa nhặt sau khi dùng skill
        is_yeucaunhatvatphamuutien = bool(self._yeucaunhatvatpham and self._yeucaunhatvatpham.get("is_uutien"))

        # Đang lùi giữ khoảng cách thì không đi nhặt đồ, nên cũng không chặn buff vì nhặt đồ
        self._is_danguutiennhatdo = (is_yeucaunhatvatphamganhon or is_yeucaunhatvatphamuutien) and not self._yeucaugiukhoangcach

        if self._yeucaugiukhoangcach:
            # Kẻ tấn công lại quá gần: lùi trước mọi việc khác (vẫn sau các khoá vận khí / ra chiêu ở trên)
            yeucauduocchon = self._yeucaugiukhoangcach
            lydochon = "GIỮ KHOẢNG CÁCH"
        elif self._is_dangphutheosau and self._yeucautheosau:
            # Đang sang bản đồ của người được theo sau: đi theo trước tấn công / gom quái / nhặt đồ
            yeucauduocchon = self._yeucautheosau
            lydochon = "THEO SAU SANG BẢN ĐỒ KHÁC"
        elif (self._idbandocandi or self.get_is_danggiaodo() or self.get_is_dangcatkho() or self.get_is_sumondichuyen()
              or self.get_is_langlysondichuyen() or self.get_is_sugiadichuyen()) and self._yeucautudo:
            # Đang Đi tới bản đồ / đi giao đồ / cất kho / đi làm sư môn: đi tiếp trước tấn công / gom quái / nhặt đồ
            yeucauduocchon = self._yeucautudo
            lydochon = "ĐI TỚI BẢN ĐỒ"
        elif is_yeucaunhatvatphamuutien:
            yeucauduocchon = self._yeucaunhatvatpham
            lydochon = "NHẶT ĐỒ ƯU TIÊN"
        elif is_yeucaunhatvatphamganhon:
            yeucauduocchon = self._yeucaunhatvatpham
            lydochon = "NHẶT ĐỒ (GẦN HƠN MỤC TIÊU)"
        elif self._yeucautancong:
            yeucauduocchon = self._yeucautancong
            lydochon = "TẤN CÔNG"
        elif is_yeucaunhatvatpham and not is_muctieupk:
            yeucauduocchon = self._yeucaunhatvatpham
            lydochon = "NHẶT ĐỒ"
        elif self._yeucaukhaikhoang and not is_muctieupk:
            yeucauduocchon = self._yeucaukhaikhoang
            lydochon = "KHAI KHOÁNG"
        elif self._yeucaudaotangbaodo and not is_muctieupk:
            yeucauduocchon = self._yeucaudaotangbaodo
            lydochon = "ĐÀO TÀNG BẢO ĐỒ"
            self._thoidiemdichuyendaotangbaodogannhat = time.time()
        elif self._yeucaugomquai and not is_anhhuongboimuctieutheosau and not is_muctieupk:
            yeucauduocchon = self._yeucaugomquai
            lydochon = "GOM QUÁI"
        elif self._yeucautimmuctieuchung and not is_muctieupk:
            # Không còn mục tiêu quanh mình: đi tới mục tiêu nhân vật khác cùng máy đang thấy (đã kẹp trong vùng quanh người theo sau)
            yeucauduocchon = self._yeucautimmuctieuchung
            lydochon = "TÌM MỤC TIÊU CHUNG"
        elif self._yeucautheosau:
            yeucauduocchon = self._yeucautheosau
            lydochon = "THEO SAU"
        elif self._yeucautudo and not is_anhhuongboimuctieutheosau:
            # Không chờ giữa các lần gửi: tìm đường chỉ ghi bộ nhớ khi đích đổi, gửi lại cùng đích không làm gì
            # (trước đây chờ 2s nên đánh xong / tới điểm đánh là đứng im tới 2s mới đi tiếp)
            yeucauduocchon = self._yeucautudo
            lydochon = "ĐI DẠO (TỰ DO)"

        diachimuctieudanggom = yeucauduocchon.get("diachimuctieu") if yeucauduocchon else False
        if is_log:
            msg_dich = str(yeucauduocchon.get("toadodich")) if yeucauduocchon else "None"
            msg_diachimuctieudanggom = diachimuctieudanggom if yeucauduocchon else "None"
            print(f"[DEBUG-MOVE] Quyết định: {lydochon} | Đích: {msg_dich} | Mục tiêu: {msg_diachimuctieudanggom}")

        if yeucauduocchon and yeucauduocchon.get("yeucau") == YEUCAUDICHUYENTANCONG and is_anhhuongboimuctieutheosau:
            # Sao chép để việc cắt tọa độ theo trưởng nhóm không ghi đè vào self._yeucautancong
            yeucauduocchon = dict(yeucauduocchon)
            x_theosau, y_theosau = self._laytoadomuctieutheosau() or (0, 0)

            if x_theosau and y_theosau and yeucauduocchon.get("kieudichuyen") == KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU:
                # Lùi giữ khoảng cách: điểm lùi tới cũng phải nằm trong vùng quanh trưởng nhóm, nếu không thì kéo về theo nhóm rồi lại lùi ra (chạy đong đưa)
                yeucauduocchon = self._tinhtoanyeucaului_theosau(yeucauduocchon, diachimuctieudanggom, x_theosau, y_theosau)
            elif x_theosau and y_theosau:
                x_muctieu, y_muctieu = None, None
                toadodich_ = yeucauduocchon.get("toadodich")
                diachimuctieu_ = diachimuctieudanggom

                if toadodich_:
                    x_muctieu, y_muctieu = toadodich_
                elif diachimuctieu_:
                    x_muctieu, y_muctieu = self.moitruong.get_toado(diachimuctieu_, )

                if x_muctieu and y_muctieu:
                    khoangcachmuctieuvatheosau = math.dist((x_muctieu, y_muctieu), (x_theosau, y_theosau))
                    khoangcachtoidatheosau = self._tinhtoanbankinhdungtancongtheosau()

                    if khoangcachmuctieuvatheosau > khoangcachtoidatheosau:
                        vec_x = x_muctieu - x_theosau
                        vec_y = y_muctieu - y_theosau

                        # Không làm tròn int(): lệch tới ~1.4 ô đủ làm chỗ đứng ra ngoài tầm đánh
                        x_clipped = x_theosau + (vec_x * khoangcachtoidatheosau / khoangcachmuctieuvatheosau)
                        y_clipped = y_theosau + (vec_y * khoangcachtoidatheosau / khoangcachmuctieuvatheosau)

                        yeucauduocchon["toadodich"] = (x_clipped, y_clipped)
                        yeucauduocchon["diachimuctieu"] = None
                        yeucauduocchon["khoangcachtoida"] = 0

        self._logdichuyen(lydochon, yeucauduocchon)

        iddoituongmuctieudanggom = 0
        if yeucauduocchon:
            loaiyeucau = yeucauduocchon.get("yeucau")
            if loaiyeucau in (YEUCAUDICHUYENTANCONG, YEUCAUDICHUYENGOMQUAI):
                diachimuctieu = diachimuctieudanggom
                if diachimuctieu:
                    iddoituongmuctieudanggom = self.moitruong.get_iddoituong(diachimuctieu)
                else:
                    iddoituongmuctieudanggom = yeucauduocchon.get("idmuctieu", 0)

        # Chỉ coi là kẹt khi thực sự còn phải di chuyển (chưa vào tầm), đứng yên trong tầm để đánh/buff thì không tính
        is_candichuyendendich = False
        if iddoituongmuctieudanggom > 0:
            toadodichkiemtra = yeucauduocchon.get("toadodich")
            diachidichkiemtra = yeucauduocchon.get("diachimuctieu")
            if toadodichkiemtra:
                khoangcachdendich = self.moitruong.get_khoangcachdiem(toadodichkiemtra[0], toadodichkiemtra[1])
            elif diachidichkiemtra:
                khoangcachdendich = self.moitruong.get_khoangcach(diachidichkiemtra)
            else:
                khoangcachdendich = 0.
            if yeucauduocchon.get("kieudichuyen", KIEUDICHUYEN_GIUKHOANGCACHTOIDA) == KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU:
                is_candichuyendendich = khoangcachdendich < yeucauduocchon.get("khoangcach", 1.0) - 1.0
            else:
                is_candichuyendendich = khoangcachdendich > yeucauduocchon.get("khoangcachtoida", 0.0) + 1.0

        if iddoituongmuctieudanggom > 0:
            if iddoituongmuctieudanggom != self._idmuctieudangtheokiemtraket or not is_candichuyendendich or idtuthenhanvat != TUTHENHANVAT_DUNGIM:
                self._idmuctieudangtheokiemtraket = iddoituongmuctieudanggom
                self._thoidiemdungimkiemtraket = time.time()
                self._toadokiemtraket = self.moitruong.get_toado()
                self._thoidiembatdaukiemtraket = time.time()
            else:
                curr_x, curr_y = self.moitruong.get_toado()

                khoangcachdadichuyen = math.dist((curr_x, curr_y), self._toadokiemtraket)

                if time.time() - self._thoidiembatdaukiemtraket > 5.0:
                    if khoangcachdadichuyen < 1.0:
                        is_quai = False
                        if diachimuctieudanggom:
                            if self.moitruong.get_is_nhanvattontai(diachimuctieudanggom) and self.moitruong.get_idloainhanvat(diachimuctieudanggom) == LOAIMUCTIEU_QUAIVATHOACNPC:
                                is_quai = True

                        if is_quai:
                            if not is_anhhuongboimuctieutheosau:
                                print(f"[DEBUG-MOVE] KẸT TƯỜNG/GÓC LAG khi đến QUÁI {hex(iddoituongmuctieudanggom)}. Blacklist 120s.")
                                self._idmuctieubiloi_map[iddoituongmuctieudanggom] = time.time()
                                self._ghimuctieuboqua(iddoituongmuctieudanggom, "Kẹt tường khi tới")
                        else:
                            print(f"[DEBUG-MOVE] KẸT khi di chuyển. Reset hành động.")

                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                        self._idmuctieudangtheokiemtraket = 0
                        self._thoidiemdungimkiemtraket = 0.
                        return
                    else:
                        self._toadokiemtraket = (curr_x, curr_y)
                        self._thoidiembatdaukiemtraket = time.time()
        else:
            self._idmuctieudangtheokiemtraket = 0
            self._thoidiemdungimkiemtraket = 0.

        if yeucauduocchon:
            if yeucauduocchon.get("yeucau") == YEUCAUDICHUYENDICHUYENTUDO:
                toadodich = yeucauduocchon.get("toadodich")
                if toadodich:
                    # Tìm đường tới đích cùng bản đồ: Thục Sơn / Côn Luân dùng chiêu lướt (Khai Thiên Tịch Địa / Đằng Vân Giá Vũ) về phía đích
                    if len(toadodich) < 3 or toadodich[2] == self.moitruong.get_idbandohientai():
                        if self._thusudungkhaithientichdia(idtuthenhanvat, toadodich[0], toadodich[1]):
                            return
                        # Rào chéo chạm góc (Chu Quốc): bot tự tìm đường không lách chéo qua khe góc
                        if yeucauduocchon.get("is_khongcatgoc"):
                            self.moitruong.action_dikhongcatgoc(toadodich[0], toadodich[1], yeucauduocchon.get("khoangcachtoida", 0.))
                            return
                        # Sư môn: đi theo ô (gần thẳng), không để tự động tìm đường của game chạy vòng khi vào thành / môn phái
                        if yeucauduocchon.get("is_dioo"):
                            self.moitruong.action_dioochangtoidich(toadodich[0], toadodich[1], yeucauduocchon.get("khoangcachtoida", 0.))
                            return
                        self.moitruong.action_tudongtimduong(*toadodich)
                    else:
                        self._tudongtimduongtungbando(*toadodich[:3])
                return

            toadodich = yeucauduocchon.get("toadodich")
            diachimuctieu = diachimuctieudanggom

            x_dich, y_dich = None, None
            if toadodich:
                x_dich, y_dich = toadodich[0], toadodich[1]
            elif diachimuctieu:
                x_dich, y_dich = self.moitruong.get_toado(diachimuctieu)
            # Côn Luân đang đánh: chỉ lướt khi mục tiêu đủ xa (lướt xong ~2s không ra chiêu được, gần thì đi bộ nhanh hơn)
            khoangcachtoithieuluot = 3.
            if self.moitruong.get_tenmonphai() == "conluan" and yeucauduocchon.get("yeucau") in (YEUCAUDICHUYENTANCONG, YEUCAUDICHUYENTIMMUCTIEUCHUNG):
                khoangcachtoithieuluot = self._khoangcachsudungkynangtamxa + KHOANGCACHLUOTTHEMKHITANCONG
            if self._thusudungkhaithientichdia(idtuthenhanvat, x_dich, y_dich, khoangcachtoithieu = khoangcachtoithieuluot):
                return

            kieudichuyen = yeucauduocchon.get("kieudichuyen", KIEUDICHUYEN_GIUKHOANGCACHTOIDA)

            if kieudichuyen == KIEUDICHUYEN_GIUKHOANGCACHTOIDA:
                khoangcachtoida = yeucauduocchon.get("khoangcachtoida", 0.0)
                if toadodich and yeucauduocchon.get("yeucau") in (YEUCAUDICHUYENTANCONG, YEUCAUDICHUYENTIMMUCTIEUCHUNG):
                    # Tấn công bị kẹp quanh trưởng nhóm (đích đã cắt thành tọa độ) vẫn là tiếp cận: dùng tìm đường như tiếp cận đối tượng
                    self.moitruong.action_dichuyengiukhoangcachtoidadiembangtimduong(toadodich[0], toadodich[1], khoangcachtoida)
                elif toadodich and yeucauduocchon.get("is_khongcatgoc"):
                    # Theo sau trong thành: bot tự tìm đường theo lưới vật cản, không click thẳng / lách chéo qua khe góc của rào chắn
                    self.moitruong.action_dikhongcatgoc(toadodich[0], toadodich[1], khoangcachtoida)
                elif toadodich:
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(
                        toadodich[0],
                        toadodich[1],
                        khoangcachtoida,
                        is_bokiemtravungcam = yeucauduocchon.get("yeucau") == YEUCAUDICHUYENTHEOSAU,
                    )
                elif diachimuctieu:
                    self.moitruong.action_dichuyengiukhoangcachtoida(
                        diachimuctieu,
                        khoangcachtoida
                    )

            elif kieudichuyen == KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU:
                khoangcachtoithieu = yeucauduocchon.get("khoangcach", 1.0)
                if toadodich:
                    self.moitruong.action_dichuyengiukhoangcachtoithieudiem(
                        toadodich[0],
                        toadodich[1],
                        khoangcachtoithieu
                    )
                elif diachimuctieu:
                    self.moitruong.action_dichuyengiukhoangcachtoithieu(
                        diachimuctieu,
                        khoangcachtoithieu
                    )
            elif kieudichuyen == KIEUDICHUYEN_TOADOCHUAN:
                self.moitruong.action_dichuyenphudau(
                    diachimuctieu,
                    khoangcachphudau = 0
                )

    def action_tudongtheosau(self):
        self._yeucautheosau = None
        self._is_dangphutheosau = False

        if not self._is_tudongtheosau:
            return

        while True:
            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_dangvankhi():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if not self._layidmuctieutheosau():
                break

            # Trưởng nhóm cùng máy đang làm Sư Gia: chọn "Nhận" theo trưởng nhóm, nhiệm vụ của mình xong thì tới Từ Phúc tự trả (tactu_sugia_xq)
            yeucausugia = self._xulysugiathanhvien()
            if yeucausugia is not False:
                self._is_dangphutheosau = True
                self._yeucautheosau = yeucausugia
                break

            # Trưởng nhóm vừa lĩnh thưởng Lăng Ly Sơn: tự tới Đào Vong Khổ Dịch lĩnh phần của mình trước (tactu_langlyson_xq)
            yeucaulanhthuong = self._xulylanhthuongtheosau()
            if yeucaulanhthuong is not False:
                self._is_dangphutheosau = True
                self._yeucautheosau = yeucaulanhthuong
                break

            if self._xulyphutheosau():
                break

            toadomuctieu = self._laytoadomuctieutheosau()
            if not toadomuctieu:
                break
            xtheosau, ytheosau = toadomuctieu

            khoangcachtheosau = self.moitruong.get_khoangcachdiem(xtheosau, ytheosau)
            khoangcachtoidatheosau = self._tinhtoankhoangcachtoidatheosauphuhop()

            if khoangcachtheosau >= KHOANGCACHTOIDAHOPLE:
                break

            # Mỗi thành viên có một chỗ đứng riêng quanh trưởng nhóm (chia đều góc theo thứ tự trong nhóm) thay vì cùng chạy thẳng về phía trưởng nhóm rồi dính vào nhau
            xvitri, yvitri = self._tinhtoanvitritheosau(xtheosau, ytheosau, khoangcachtoidatheosau)
            khoangcachvitri = self.moitruong.get_khoangcachdiem(xvitri, yvitri)

            # Đang có mục tiêu thì đứng trong vùng là đủ: không đi về chỗ đứng riêng (có thể ở phía đối diện mục tiêu),
            # nếu không mỗi lượt không có yêu cầu tấn công (buff bản thân...) sẽ quay đầu chạy về rồi lại chạy ra đánh
            diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            is_comuctieu = bool(diachimuctieudangchon) and not self.moitruong.get_is_nhanvatdachet(diachimuctieudangchon)

            # Chỉ bắt đầu đi khi đã ra quá xa người được theo sau, đã đi thì đi vào hẳn trong vòng chỗ đứng (không dừng ngay mép vùng cho phép).
            # Vào tới vòng chỗ đứng là dừng, không đi tiếp tới đúng chỗ đứng riêng: chỗ đó có thể ở phía bên kia (chạy vòng qua),
            # và khi người được theo sau đang đi thì chỗ đứng dịch theo từng lượt nên sẽ chạy mãi
            if khoangcachtheosau > khoangcachtoidatheosau:
                self._is_dangvevitritheosau = True
            elif is_comuctieu or khoangcachvitri <= 1.0 or khoangcachtheosau <= self._tinhtoanbankinhchodungtheosau(khoangcachtoidatheosau):
                self._is_dangvevitritheosau = False

            if not self._is_dangvevitritheosau:
                break

            # Trong thành / môn phái (Chu Quốc có rào xếp chéo chạm góc cố ý làm kẹt người đi thẳng / tự động tìm đường): bot tự tìm đường
            self._yeucautheosau = {
                "yeucau": YEUCAUDICHUYENTHEOSAU,
                "toadodich": (xvitri, yvitri),
                "khoangcachtoida": 0.5,
                "is_khongcatgoc": self.moitruong.get_idbandohientai() in BANDOKHONGPKs,
            }
            break

        if not self._yeucautheosau:
            self._is_dangvevitritheosau = False
        return

    def _layidmuctieutheosau(self):
        # ID người đang được theo sau, 0 nếu không theo ai (tắt, chọn trưởng nhóm mà không có nhóm / chính mình là trưởng nhóm)
        if not self._is_tudongtheosau:
            return 0
        if self._idmuctieutheosau:
            return self._idmuctieutheosau if self._idmuctieutheosau != self.moitruong.get_idnguoichoi() else 0
        if not self.moitruong.get_is_dangnamtrongnhom() or self.moitruong.get_is_truongnhom():
            return 0
        return self.moitruong.get_idnguoichoitruongnhom() or 0

    def _laytoadomuctieutheosau(self):
        # Tọa độ người đang được theo sau, False nếu không theo ai hoặc không biết họ ở đâu.
        # Gọi nhiều lần mỗi lượt nên nhớ kết quả 0.1s (người chơi bất kỳ phải duyệt danh sách đối tượng xung quanh)
        thoidiem, toado = self._bonhotoadomuctieutheosau
        if time.time() - thoidiem < 0.1:
            return toado
        toado = self._doctoadomuctieutheosau()
        self._bonhotoadomuctieutheosau = (time.time(), toado)
        return toado

    def _doctoadomuctieutheosau(self):
        idmuctieu = self._layidmuctieutheosau()
        if not idmuctieu:
            return False

        if not self._idmuctieutheosau:
            # Trưởng nhóm: đọc từ thông tin nhóm, có cả khi trưởng nhóm ở ngoài tầm nhìn
            toado = self.moitruong.get_toadotruongnhom()
            if not toado or toado == (65535, 65535) or not any(toado):
                return False
            return toado

        # Nhân vật cùng máy: đọc thẳng trong danh sách đối tượng xung quanh cho tọa độ mới nhất. Thử lại địa chỉ lần trước trước khi duyệt cả danh sách
        diachi = self._diachimuctieutheosau
        if not diachi or not self.moitruong.get_is_nhanvattontai(diachi) or self.moitruong.get_idnguoichoi(diachi) != idmuctieu:
            diachi = 0
            i = 0
            while i < SOLUONGDOITUONGXUNGQUANHTOIDA:
                diachixemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachixemxet:
                    break
                i += 1
                if self.moitruong.get_is_nhanvattontai(diachixemxet) and self.moitruong.get_is_nguoichoi(diachixemxet) and self.moitruong.get_idnguoichoi(diachixemxet) == idmuctieu:
                    diachi = diachixemxet
                    break
            self._diachimuctieutheosau = diachi
        if diachi:
            return self.moitruong.get_toado(diachi)

        # Ngoài tầm nhìn nhưng cùng bản đồ => lấy tọa độ cửa sổ đó báo lên (bản đồ khác thì _xulyphutheosau lo phù sang)
        info = self._laythongtinmuctieutheosaucuasokhac()
        if info and info.get("tenbando") == self.moitruong.get_idbandohientai() and (info.get("x") or info.get("y")):
            return info.get("x"), info.get("y")
        return False

    def thietlap_muctieutheosau(self, idnguoichoi, tennguoichoi = ""):
        self._idmuctieutheosau = int(idnguoichoi or 0)
        self._tenmuctieutheosau = tennguoichoi if self._idmuctieutheosau else ""
        self._diachimuctieutheosau = 0
        self._bonhotoadomuctieutheosau = (0., False)
        if self._idmuctieutheosau:
            print(f"[THEO SAU] Theo sau {self._tenmuctieutheosau} (ID {self._idmuctieutheosau})")
        else:
            print("[THEO SAU] Theo sau trưởng nhóm")

    def _laythongtinmuctieutheosaucuasokhac(self):
        # Người đang được theo sau chạy trên cùng máy => thông tin (bản đồ, tọa độ) của cửa sổ đó trong shared_data, không thì None
        if self.shared_data is None:
            return None
        idmuctieu = self._layidmuctieutheosau()
        if not idmuctieu:
            return None
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return None
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict):
                continue
            if info.get("idnguoichoi") != idmuctieu:
                continue
            # Cửa sổ người được theo sau treo/không cập nhật nữa thì không tin bản đồ cũ
            if time.time() - info.get("thoidiemcapnhat", 0.) > 5.:
                return None
            return info
        return None

    def _laymonphainhanvatcungmay(self):
        # {ID người chơi: tên môn phái} của các nhân vật chạy trên cùng máy (shared_data), bỏ cửa sổ treo/không cập nhật
        monphai_map = {}
        if self.shared_data is None:
            return monphai_map
        try:
            danhsach = list(self.shared_data.values())
        except Exception:
            return monphai_map
        for info in danhsach:
            if not isinstance(info, dict) or time.time() - info.get("thoidiemcapnhat", 0.) > 5.:
                continue
            if info.get("idnguoichoi") and info.get("tenmonphai"):
                monphai_map[info["idnguoichoi"]] = info["tenmonphai"]
        return monphai_map

    def _laythongtintodoicungbando(self, idbandohientai, xephang_map):
        # Từ shared_data (các cửa sổ cùng máy) trên cùng bản đồ:
        #   cacnhoms: {idtruongnhom: (hạng tốt nhất trong nhóm, thành viên)}, chỉ tính nhóm có người trong danh sách tổ đội
        #   nguoichoiles: người trong danh sách tổ đội đang không có nhóm
        cacnhoms, nguoichoiles = {}, []
        if self.shared_data is None:
            return cacnhoms, nguoichoiles
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return cacnhoms, nguoichoiles
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict):
                continue
            if info.get("tenbando") != idbandohientai or time.time() - info.get("thoidiemcapnhat", 0.) > 5.:
                continue
            idtruongnhom = info.get("idtruongnhom")
            if not idtruongnhom:
                if info.get("idnguoichoi") in xephang_map:
                    nguoichoiles.append(info.get("idnguoichoi"))
                continue
            thanhviens = set(info.get("thanhviennhoms") or ()) | {info.get("idnguoichoi")}
            if idtruongnhom in cacnhoms:
                thanhviens |= cacnhoms[idtruongnhom][1]
            hangs = [xephang_map[id_] for id_ in thanhviens if id_ in xephang_map]
            if hangs:
                cacnhoms[idtruongnhom] = (min(hangs), thanhviens)
        return cacnhoms, nguoichoiles

    def _xulyphutheosau(self):
        # Người được theo sau ở bản đồ khác (biết được vì cùng máy) và bật _is_tutimduongtheosau => tự tìm đường tới bản đồ đó
        # bằng bộ lập bước của Đi tới bản đồ (phù Tân Thủ Tiên Cô / Chủ Dịch Trạm, Hồi Thành Phù, chạy bộ từng bản đồ).
        # Trả về True khi đang lo việc sang bản đồ khác (bỏ qua theo sau bình thường)
        if self.get_is_danghoithoainpc():
            self._is_dangphutheosau = True
            return True

        if not self._is_tutimduongtheosau or self._trangthaiveban != 0 or self._is_tudongdichientruong or self._is_tudongdaotangbaodo:
            return False

        info = self._laythongtinmuctieutheosaucuasokhac()
        idbandotheosau = info.get("tenbando") if info else None
        if idbandotheosau != self._idbandotheosaugannhat:
            self._idbandotheosaugannhat = idbandotheosau
            self._thoidiemdoibandotheosau = time.time()

        idbandohientai = self.moitruong.get_idbandohientai()
        if not idbandotheosau or idbandotheosau == idbandohientai:
            return False

        # Người được theo sau đã ra khỏi phó bản (xong Lăng Ly Sơn, Hồi Thành Phù về) thì mình cũng Hồi Thành Phù ra theo
        buoc = self._lapbuocditoibando(idbandotheosau, is_hoithanhphu = True, is_roiphoban = True)
        if buoc["loai"] == "khongduong":
            return False

        self._is_dangphutheosau = True

        # Người được theo sau có thể chỉ đi ngang qua bản đồ đó; mình vừa chuyển bản đồ thì chờ tải xong
        if time.time() - self._thoidiemdoibandotheosau < THOIGIANCHOBANDOTHEOSAUONDINH:
            self._capnhatbuocdichuyen(f"Chờ người được theo sau ở yên {laytenbando(idbandotheosau)}, rồi: {buoc['mota']}")
            return True
        if time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return True

        toadotheosau = (info["x"], info["y"]) if info.get("x") and info.get("y") else None
        yeucau = self._thuchienbuocditoibando(buoc, idbandotheosau, toadotheosau, f"[THEO SAU] Người được theo sau ở {laytenbando(idbandotheosau)}")
        if yeucau:
            self._yeucautheosau = yeucau
        return True

    def _lapbuocditoibando(self, idbandodich, is_hoithanhphu = False, toadodich = None, is_roiphoban = False):
        # Quyết định bước tiếp theo để tới bản đồ idbandodich (chưa làm gì), dùng chung cho Đi tới bản đồ, lộ trình, theo sau:
        #   - đang ở Tân Thủ Thôn / Chu: phù (Tân Thủ Tiên Cô / Chủ Dịch Trạm, layphuongandichuyen) nếu chạy bộ tiếp ít cổng hơn chạy bộ từ đây
        #   - is_hoithanhphu: chạy bộ quá SOLANCHUYENBANDOTOIDA cổng mà về Tân Thủ Thôn phù đi gần hơn thì Hồi Thành Phù trước
        #   - còn lại chạy bộ tới cổng sang bản đồ kế tiếp trên đường qua ít bản đồ nhất (không đặt thẳng bản đồ đích cho client)
        # -> {"loai": "toinoi" | "chaybo" | "phu" | "hoithanhphu" | "khongduong", "mota": chuỗi hiển thị, "solan": số cổng chạy bộ, "cong": (x, y)}
        idbandohientai = self.moitruong.get_idbandohientai()
        ten = laytenbando(idbandodich)
        if idbandohientai == idbandodich:
            return {"loai": "toinoi", "mota": f"Đã ở {ten}", "solan": 0}
        # is_roiphoban: đang ở phó bản mà đích ở ngoài, không chạy bộ ra được (Lăng Ly Sơn xong, người được theo sau đã ra) thì Hồi Thành Phù
        # ra luôn (mất phó bản). Nơi khác (cất kho, giao đồ...) không truyền cờ này nên vẫn không bao giờ Hồi Thành Phù trong phó bản
        if is_roiphoban and idbandohientai in BANDOPHOBANs and idbandodich not in BANDOPHOBANs \
                and timduongbando(idbandohientai, idbandodich) is None:
            lydo = self.get_lydokhonghoithanhphu(idbandodich, is_roiphoban = True)
            if lydo:
                return {"loai": "khongduong", "solan": None, "mota": f"Không ra khỏi phó bản được: {lydo}"}
            return {"loai": "hoithanhphu", "solan": 0, "is_roiphoban": True, "mota": f"Hồi Thành Phù ra khỏi phó bản {laytenbando(idbandohientai)} (tới {ten})"}
        # Đường ưu tiên người dùng chỉ (DUONGUUTIENs, theo điểm đích trong bản đồ): ở Tân Thủ Thôn thì phù theo đường đó, đang ở bản đồ
        # phù tới thì chạy tiếp, nơi khác thì Hồi Thành Phù về (không chạy bộ dù ít cổng)
        uutien = layduonguutien(idbandodich, toadodich)
        if uutien and idbandohientai != uutien[2]:
            if idbandohientai == BANDO_TANTHUTHON:
                return {"loai": "phu", "solan": uutien[3], "phuongan": uutien,
                        "mota": f"Phù {uutien[0]} tới {laytenbando(uutien[2])}, chạy tiếp {uutien[3]} cổng tới {ten} (đường ưu tiên)"}
            lydo = self.get_lydokhonghoithanhphu(idbandodich) if is_hoithanhphu else "không dùng Hồi Thành Phù ở đây"
            if not lydo:
                return {"loai": "hoithanhphu", "solan": uutien[3],
                        "mota": f"Hồi Thành Phù về Tân Thủ Thôn rồi phù tới {laytenbando(uutien[2])}, chạy tiếp {uutien[3]} cổng ({ten}, đường ưu tiên)"}
        duongdi = timduongbando(idbandohientai, idbandodich, self.moitruong.get_toado())
        solanbo = len(duongdi) if duongdi is not None else None
        is_xa = solanbo is None or solanbo > SOLANCHUYENBANDOTOIDA
        phuongan = layphuongandichuyen(idbandodich)
        if idbandohientai in (BANDO_TANTHUTHON, BANDO_CHUQUOC):
            if phuongan and (solanbo is None or phuongan[3] < solanbo):
                loainpc, _, idphutoi, solanphu = phuongan
                return {"loai": "phu", "solan": solanphu,
                        "mota": f"Phù {laynpcphu(loainpc, idbandohientai)[0]} tới {laytenbando(idphutoi)}{f', chạy tiếp {solanphu} cổng tới {ten}' if solanphu else ''}"}
        lydokhongphu = ""
        if idbandohientai not in (BANDO_TANTHUTHON, BANDO_CHUQUOC) and is_hoithanhphu and is_xa \
                and (idbandodich == BANDO_TANTHUTHON or (phuongan and (solanbo is None or phuongan[3] + 1 < solanbo))):
            lydo = self.get_lydokhonghoithanhphu(idbandodich)
            if not lydo:
                diphu = f" rồi phù tới {laytenbando(phuongan[2])}" if idbandodich != BANDO_TANTHUTHON else ""
                chaytiep = f", chạy tiếp {phuongan[3]} cổng" if idbandodich != BANDO_TANTHUTHON and phuongan[3] else ""
                return {"loai": "hoithanhphu", "solan": phuongan[3] if phuongan else 0,
                        "mota": f"Hồi Thành Phù về Tân Thủ Thôn{diphu}{chaytiep} ({ten}), thay vì chạy bộ {solanbo} cổng"}
            lydokhongphu = f" (không Hồi Thành Phù: {lydo})"
        if duongdi:
            _, xcong, ycong, idke = duongdi[0]
            # Hiện cả đường đi: "còn 15 cổng" không thì không biết là qua những bản đồ nào
            duong = " → ".join(laytenbando(b[3]) for b in duongdi)
            npc = laynpcloidi(idbandohientai, idke)
            if npc:
                return {"loai": "npc", "solan": solanbo, "npc": npc, "idke": idke,
                        "mota": f"Nói chuyện {npc[2]} ({npc[0]}, {npc[1]}) sang {laytenbando(idke)}, còn {solanbo} bước tới {ten}{lydokhongphu}: {duong}"}
            return {"loai": "chaybo","solan": solanbo, "cong": (xcong, ycong),
                    "mota": f"Chạy tới cổng ({xcong}, {ycong}) sang {laytenbando(idke)}, còn {solanbo} cổng tới {ten}{lydokhongphu}: {duong}"}
        return {"loai": "khongduong", "solan": None, "mota": f"Không có đường chạy bộ / phù tới {ten}: để game tự tìm đường"}

    def _thuchienbuocditoibando(self, buoc, idbandodich, toadodich, nhanlog):
        # Làm bước _lapbuocditoibando trả về; toadodich (x, y) ở bản đồ đích nếu có. -> yêu cầu di chuyển hoặc None (đang phù / Hồi Thành Phù)
        self._capnhatbuocdichuyen(buoc["mota"])
        idbandohientai = self.moitruong.get_idbandohientai()
        loai = buoc["loai"]
        if loai == "chaybo":
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (*buoc["cong"], idbandohientai), "khoangcachtoida": 0}
        if loai == "phu":
            return self._phutoibando(idbandodich, idbandohientai, nhanlog, buoc.get("phuongan"))
        if loai == "npc":
            return self._quanpcsangbando(buoc["npc"], buoc["idke"], idbandohientai, nhanlog)
        if loai == "hoithanhphu":
            if time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() >= 2. and not self.moitruong.get_is_dangvankhi() \
                    and time.time() - self._thoidiemsudunghoithanhphugannhat > 12.:
                print(f"{nhanlog} => {buoc['mota']}")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu(idbandodich, is_roiphoban = buoc.get("is_roiphoban", False))
            return None
        # Đã tới bản đồ đích / không có đường trong dữ liệu cổng: đi thẳng tới điểm đích (client tự tìm đường)
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (*toadodich, idbandodich), "khoangcachtoida": 0} if toadodich else None

    def _capnhatbuocdichuyen(self, mota):
        # Bước di chuyển tiếp theo hiện trên giao diện (get_buocdichuyen), tự hết hạn khi không ai cập nhật nữa
        self._buocdichuyen = (mota, time.time())

    def get_buocdichuyen(self):
        mota, thoidiem = self._buocdichuyen
        return mota if time.time() - thoidiem < 3. else ""

    def thietlap_ditoibando(self, idbando):
        # Đi tới bản đồ idbando (0 = dừng): chạy bộ / phù / Hồi Thành Phù theo _lapbuocditoibando, tới nơi thì dừng
        self._idbandocandi = int(idbando or 0)
        if self._idbandocandi:
            print(f"[ĐI TỚI BẢN ĐỒ] Bắt đầu đi tới {laytenbando(self._idbandocandi)}")
            phatam(f"Đi tới {laytenbando(self._idbandocandi)}")
        else:
            self._yeucautudo = None
            phatam("Dừng đi tới bản đồ")

    def _xulyditoibando(self):
        # Gọi thay lộ trình điểm đánh khi đang Đi tới bản đồ -> yêu cầu di chuyển hoặc None
        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0:
            return None
        buoc = self._lapbuocditoibando(self._idbandocandi, is_hoithanhphu = True)
        if buoc["loai"] == "toinoi":
            print(f"[ĐI TỚI BẢN ĐỒ] Đã tới {laytenbando(self._idbandocandi)}")
            phatam(f"Đã tới {laytenbando(self._idbandocandi)}")
            self._idbandocandi = 0
            return None
        return self._thuchienbuocditoibando(buoc, self._idbandocandi, None, f"[ĐI TỚI BẢN ĐỒ] {laytenbando(self._idbandocandi)}")

    def _tudongtimduongtungbando(self, x, y, idbando):
        # Đích ở bản đồ khác: không đặt thẳng bản đồ đích cho client (nó có thể chọn đường vòng vớ vẩn) mà tìm đường tới cổng sang bản đồ
        # kế tiếp trên đường qua ít bản đồ nhất (bando_xq.timduongbando), sang tới bản đồ đó lượt sau lại tính tiếp.
        # Không có đường đi bộ (dữ liệu cổng thiếu) thì để client tự tìm đường tới bản đồ đích như cũ
        idbandohientai = self.moitruong.get_idbandohientai()
        duongdi = timduongbando(idbandohientai, idbando, self.moitruong.get_toado())
        if duongdi:
            _, xcong, ycong, idke = duongdi[0]
            self._capnhatbuocdichuyen(f"Chạy tới cổng ({xcong}, {ycong}) sang {laytenbando(idke)}, còn {len(duongdi)} cổng tới {laytenbando(idbando)}")
            return self.moitruong.action_tudongtimduong(xcong, ycong, idbandohientai)
        self._capnhatbuocdichuyen(f"Game tự tìm đường tới {laytenbando(idbando)} ({x}, {y})")
        return self.moitruong.action_tudongtimduong(x, y, idbando)

    def _phutoibando(self, idbandodich, idbandohientai, nhanlog, phuongan = None):
        # Đang ở Tân Thủ Thôn / Chu: phù tới idbandodich (hoặc bản đồ gần nhất rồi chạy bộ tiếp) bằng NPC của cách tốt nhất (layphuongandichuyen,
        # hoặc phuongan truyền vào: đường ưu tiên): Tân Thủ Tiên Cô (các bước welcome) hoặc Chủ Dịch Trạm (goto.!, ở Chu tên Trường Hoằng).
        # -> yêu cầu di chuyển tới NPC khi chưa đứng cạnh, None khi đã đứng cạnh (đã / đang gửi lệnh phù) hoặc không phù tới được
        phuongan = phuongan or layphuongandichuyen(idbandodich)
        if not phuongan:
            return None
        loainpc, buoc, idphutoi, _ = phuongan
        tennpc, vitrinpc = laynpcphu(loainpc, idbandohientai)
        diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = tennpc)
        if not diachinpc:
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (vitrinpc[0], vitrinpc[1], idbandohientai), "khoangcachtoida": 0} if vitrinpc else None
        if self.moitruong.get_khoangcach(diachinpc) > 6.:
            x_npc, y_npc = self.moitruong.get_toado(diachinpc)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x_npc, y_npc, idbandohientai), "khoangcachtoida": 0}
        if self.get_is_danghoithoainpc() or time.time() - self._thoidiemphutoibandogannhat < 8.:
            return None
        nganluong = self.moitruong.get_nganluong()
        if loainpc == TANTHUTIENCO and nganluong is not None and nganluong < GIAPHUTANTHUTIENCO:
            self._thoidiemphutoibandogannhat = time.time()
            self._capnhatbuocdichuyen(f"Còn {nganluong} lượng, không đủ {GIAPHUTANTHUTIENCO} lượng phù {tennpc}")
            print(f"{nhanlog} => không phù: còn {nganluong} lượng, {tennpc} lấy {GIAPHUTANTHUTIENCO} lượng")
            return None
        idnpc = self.moitruong.get_iddoituong(diachinpc)
        if not idnpc:
            return None
        self._thoidiemphutoibandogannhat = time.time()
        hex_id = hex(idnpc).replace("0x", "")
        self.moitruong.action_ngatdichuyen()
        print(f"{nhanlog} => dùng {tennpc} phù tới {laytenbando(idphutoi)}{'' if idphutoi == idbandodich else ' rồi chạy bộ tiếp'}")
        if loainpc == TANTHUTIENCO:
            self.action_batdauhoithoainpc([f"tallk {hex_id}# {b}" for b in buoc])
        else:
            self.moitruong.action_thucthicaulenh2(f"tallk {hex_id}# goto.! {buoc} t{int(time.time())}", delay = 0.0)
            self.moitruong.action_ngatdichuyen()
        return None

    def _quanpcsangbando(self, npc, idke, idbandohientai, nhanlog):
        # Sang idke bằng nói chuyện NPC (bando_xq.LOIDINPC_MAP): tới cạnh NPC, "look" mở menu, chọn lựa chọn đầu (trừ CLOSE), đứng yên
        # chờ vận khí xong là được đưa sang. Chưa sang được (vd. tầng trên chưa xong nên NPC không cho qua) thì THOIGIANTHULAILOIDINPC giây
        # sau nói chuyện lại. -> yêu cầu di chuyển tới NPC khi chưa đứng cạnh, None khi đang / đã nói chuyện
        xnpc, ynpc, tennpc = npc
        moitruong = self.moitruong
        now = time.time()
        hoithoai = self._hoithoailoidinpc
        if hoithoai and hoithoai["idbando"] != idbandohientai:
            hoithoai = self._hoithoailoidinpc = None
        if moitruong.get_is_dangvankhi() or now - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = tennpc)
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHNOICHUYENLOIDINPC:
            # Đang dở hội thoại mà bị đẩy ra xa thì chạy lại, tới nơi nói chuyện lại từ đầu
            self._hoithoailoidinpc = None
            xdich, ydich = moitruong.get_toado(diachinpc) if diachinpc else (xnpc, ynpc)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (xdich, ydich, idbandohientai), "khoangcachtoida": 0}
        if not hoithoai or (hoithoai["dachon"] and now - hoithoai["luc"] > THOIGIANTHULAILOIDINPC):
            idnpc = moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                return None
            if hoithoai:
                print(f"{nhanlog} => {THOIGIANTHULAILOIDINPC:.0f}s chưa sang {laytenbando(idke)}, nói chuyện lại {tennpc}")
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            manpc = f"{idnpc:x}#"
            moitruong.action_thucthicaulenh(f"look {manpc}")
            self._hoithoailoidinpc = {"idbando": idbandohientai, "manpc": manpc, "luc": now, "dachon": False}
            return None
        if hoithoai["dachon"]:
            # Đã chọn: đóng menu còn mở (lời NPC từ chối...) rồi đứng chờ vận khí
            if now - hoithoai["luc"] > 1.5 and moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            return None
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung:
            if now - hoithoai["luc"] > THOIGIANCHOMENULOIDINPC:
                # Menu không hiện: lượt sau "look" lại
                self._hoithoailoidinpc = None
            return None
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        moitruong._inlog(f"{nhanlog} Menu {tennpc}: {noidung[:80]!r} {lenhs}")
        if lenhs:
            print(f"{nhanlog} => nói chuyện {tennpc} sang {laytenbando(idke)}: {lenhs[0]}")
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(lenhs[0])
        hoithoai["dachon"] = True
        hoithoai["luc"] = now
        return None

    def _tinhtoanvitritheosau(self, xtheosau, ytheosau, khoangcachtoidatheosau):
        idnguoichoi = self.moitruong.get_idnguoichoi()
        idmuctieu = self._layidmuctieutheosau()
        idthanhviens = [i for i in self.moitruong.get_danhsachidnguoichoithanhviennhoms() if i != idmuctieu] if self.moitruong.get_is_dangnamtrongnhom() else []

        if idnguoichoi in idthanhviens:
            # Thứ tự trong nhóm giống nhau ở mọi máy nên các thành viên tự chia góc không trùng nhau
            goc = 2 * math.pi * idthanhviens.index(idnguoichoi) / len(idthanhviens)
        else:
            # Chưa đọc được danh sách nhóm: rải góc theo ID (góc vàng) để vẫn khác nhau
            goc = (idnguoichoi or 0) * 2.39996

        bankinh = self._tinhtoanbankinhchodungtheosau(khoangcachtoidatheosau)
        return xtheosau + bankinh * math.cos(goc), ytheosau + bankinh * math.sin(goc)

    @staticmethod
    def _tinhtoanbankinhchodungtheosau(khoangcachtoidatheosau):
        # Bán kính vòng các chỗ đứng riêng quanh người được theo sau
        return max(1.5, khoangcachtoidatheosau * 0.6)

    def _tinhtoankhoangcachtoidatheosauphuhop(self):
        khoangcachtoidatheosau = self._khoangcachtoidatheosau
        diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        tendoituongmuctieudangchon = diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)
        is_muctieudangchonlabaothukynangtrieuhoi = tendoituongmuctieudangchon and any(tenbaothu in tendoituongmuctieudangchon for tenbaothu in BAOTHUKYNANGTRIEUHOIs)
        if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon) or is_muctieudangchonlabaothukynangtrieuhoi:
            khoangcachtoidatheosau -= 1.5
        return khoangcachtoidatheosau

    def _tinhtoanbankinhdungtancongtheosau(self):
        # Chỗ đứng đánh xa nhất quanh trưởng nhóm; chừa 0.5 để tọa độ làm tròn không vượt ngưỡng kéo về theo nhóm
        return max(0., self._tinhtoankhoangcachtoidatheosauphuhop() - 0.5)

    def _tinhtoankhoangcachchophepmuctieutheosau(self, is_muctieuhientai = False):
        # Mục tiêu phải đánh được từ chỗ đứng đó, nếu không sẽ chọn quái không bao giờ với tới.
        # Mục tiêu mới chừa thêm 1.0 (sai số khi dừng di chuyển), mục tiêu đang đánh giữ tới đúng tầm để không bỏ/chọn lại liên tục khi trưởng nhóm nhích
        return self._tinhtoanbankinhdungtancongtheosau() + self._khoangcachvoitoimuctieu - (0. if is_muctieuhientai else 1.)

    def _tinhtoanyeucaului_theosau(self, yeucau, diachimuctieu, x_theosau, y_theosau):
        # Trả về yêu cầu lùi tới một điểm cụ thể trong vùng quanh trưởng nhóm, hoặc None nếu không lùi được (đứng đánh tiếp)
        toadodich = yeucau.get("toadodich")
        if toadodich:
            x_muctieu, y_muctieu = toadodich[0], toadodich[1]
        elif diachimuctieu:
            x_muctieu, y_muctieu = self.moitruong.get_toado(diachimuctieu)
        else:
            return None
        x_banthan, y_banthan = self.moitruong.get_toado()
        khoangcachmuctieu = math.dist((x_banthan, y_banthan), (x_muctieu, y_muctieu))
        khoangcachtoithieu = yeucau.get("khoangcach", 1.0)
        if khoangcachmuctieu >= khoangcachtoithieu or khoangcachmuctieu <= 0.:
            return None

        khoangcachlui = khoangcachtoithieu - khoangcachmuctieu + 0.5
        x_lui = x_banthan + (x_banthan - x_muctieu) * khoangcachlui / khoangcachmuctieu
        y_lui = y_banthan + (y_banthan - y_muctieu) * khoangcachlui / khoangcachmuctieu

        bankinh = self._tinhtoanbankinhdungtancongtheosau()
        khoangcachluivatheosau = math.dist((x_lui, y_lui), (x_theosau, y_theosau))
        if khoangcachluivatheosau > bankinh:
            if khoangcachluivatheosau <= 0.:
                return None
            x_lui = x_theosau + (x_lui - x_theosau) * bankinh / khoangcachluivatheosau
            y_lui = y_theosau + (y_lui - y_theosau) * bankinh / khoangcachluivatheosau
            # Điểm trên mép vùng không xa mục tiêu hơn chỗ đang đứng đáng kể => lùi vô ích
            if math.dist((x_lui, y_lui), (x_muctieu, y_muctieu)) < khoangcachmuctieu + 0.5:
                return None

        yeucau = dict(yeucau)
        yeucau["kieudichuyen"] = KIEUDICHUYEN_GIUKHOANGCACHTOIDA
        yeucau["toadodich"] = (x_lui, y_lui)
        yeucau["khoangcachtoida"] = 0
        return yeucau

    def _kiemtra_vungcam(self, x, y):
        # Vùng cấm trên bản đồ (VUNGCAM_MAP): đi vào sẽ bị dịch chuyển sang bản đồ khác
        danhsachvungcam = VUNGCAM_MAP.get(self.moitruong.get_idbandohientai())
        if not danhsachvungcam:
            return False
        for vung in danhsachvungcam:
            if vung["type"] == "circle":
                if math.dist((x, y), (vung["x"], vung["y"])) <= vung["r"]:
                    return True
            elif vung["type"] == "line":
                if self._tinhkhoangcachdendoanthang(x, y, vung["x1"], vung["y1"], vung["x2"], vung["y2"]) <= vung["r"]:
                    return True
        return False

    def _kiemtra_divaovungcam(self, x, y):
        # Nhân vật chạy thẳng tới điểm đích: chặn cả khi điểm đích nằm ngoài vùng cấm nhưng đường chạy cắt qua vùng cấm
        if not self._is_tranhvungcam or not VUNGCAM_MAP.get(self.moitruong.get_idbandohientai()):
            return False
        if self._kiemtra_vungcam(x, y):
            return True
        x1, y1 = self.moitruong.get_toado()
        sobuoc = int(math.dist((x1, y1), (x, y)))
        for i in range(1, sobuoc):
            t = i / sobuoc
            if self._kiemtra_vungcam(x1 + (x - x1) * t, y1 + (y - y1) * t):
                return True
        return False

    def _kiemtra_tamdiemdanh(self, x, y):
        # Đang chạy theo lộ trình điểm đánh: mục tiêu phải nằm trong bán kính _bankinhdiemdanh quanh ít nhất 1 điểm đánh của bản đồ hiện tại.
        # Không có điểm đánh nào trên bản đồ này (hoặc không bật lộ trình) thì không giới hạn.
        if not self._is_tudongdichuyendiemdanhxungquanh or not self._diemdanhxungquanhs or (self._sumon and self._sumon["chedo"] == "danhquai") \
                or self.get_is_langlysondanhquai() or self.get_is_sugiadanhquai():
            return True
        idbandohientai = self.moitruong.get_idbandohientai()
        diemcungbandos = [d for d in self._diemdanhxungquanhs if len(d) >= 3 and d[2] == idbandohientai]
        if not diemcungbandos:
            return True
        return any(math.dist((x, y), (d[0], d[1])) <= self._bankinhdiemdanh for d in diemcungbandos)

    def _nhacbandokhongcodiemdanh(self):
        # Đang bật lộ trình mà bản đồ hiện tại không có điểm đánh nào: mọi mục tiêu bị bỏ qua mà không báo gì thì dễ tưởng đang đánh,
        # nhắc 10s một lần. Chỉ gọi khi mục tiêu đã qua lọc đánh được / tên, nên đi ngang thành không có quái thì không nhắc
        if time.time() - self._thoidiemphatamlotrinhkhacbandogannhat > 10.:
            self._thoidiemphatamlotrinhkhacbandogannhat = time.time()
            phatam("Bản đồ này không có điểm đánh trong lộ trình, bỏ qua mục tiêu")

    def action_tudongdichuyentudo(self):
        yeucautudomoi = None

        # Vừa ra khỏi phó bản mượn ID bản đồ: ngắt di chuyển thêm vài lần trễ (lệnh đi điểm kế gửi lúc vừa ra vẫn lọt sau lần ngắt đầu)
        if self._thoidiemngatdichuyenroiphobans and time.time() >= self._thoidiemngatdichuyenroiphobans[0]:
            self._thoidiemngatdichuyenroiphobans.pop(0)
            self.moitruong.action_ngatdichuyen()

        # Đi tới bản đồ do người dùng chọn: thay hẳn lộ trình điểm đánh tới khi tới nơi / bấm dừng
        if self._idbandocandi:
            self._yeucautudo = self._xulyditoibando()
            return

        # Đang có yêu cầu giao tiền / đồ (tactu_giaodo_xq): về Tân Thủ Thôn tìm người nhận, thay lộ trình điểm đánh tới khi giao xong
        if self.get_is_danggiaodo():
            self._yeucautudo = self._xulygiaodo()
            return

        # Cất kho bấm tay / Telegram (tactu_catkho_xq): như giao đồ, về Tân Thủ Thôn gửi Quản Khố
        self._dondepcatkho()
        if self.get_is_dangcatkho():
            self._yeucautudo = self._xulycatkho()
            return

        # Nhiệm vụ sư môn (tactu_sumon_xq): tự lo đi lại / nói chuyện NPC / bắt yêu quái; Luyện tập, Du lịch thì farm theo lộ trình điểm
        # đánh như thường (kể cả khi chưa bật ô lộ trình)
        # Đang mở cửa hàng đọc hàng (sư môn / mua bù): đứng yên tới khi đọc xong
        self.action_xulymocuahang()
        if self._mocuahang:
            self._yeucautudo = None
            return
        self.action_ghivitridoituong()
        if self.get_is_dangsumon():
            yeucau = self._xulysumon()
            if not self.get_is_sumonfarm():
                self._yeucautudo = yeucau
                return

        # Tự động đi Lăng Ly Sơn (tactu_langlyson_xq): tự lo vào phó bản / đánh boss / nhận thưởng / đổi tổ đội, thay lộ trình điểm đánh
        if self.get_is_danglanglyson():
            self._yeucautudo = self._xulylanglyson()
            return

        # Nhiệm vụ Sư Gia (tactu_sugia_xq): nhận / truy tìm / giết tội phạm / trả ở Từ Phúc, thay lộ trình điểm đánh
        if self.get_is_dangsugia():
            self._yeucautudo = self._xulysugia()
            return

        if not self._is_tudongdichuyendiemdanhxungquanh and not self.get_is_sumonfarm():
            self._yeucautudo = None
            return

        if self._diachicosokhaikhoang:
            self._yeucautudo = None
            return

        # Đang trong quy trình về bán rác: không tự đi/phù lên bãi farm (trước đây vừa Hồi Thành Phù về tới thành,
        # đứng gần Tân Thủ Tiền Cơ là bị nói chuyện NPC phù thẳng lên map farm trước khi kịp bán)
        if self._trangthaiveban != 0:
            self._yeucautudo = None
            return

        # Đang phù sang bản đồ của trưởng nhóm: không tự phù/đi theo lộ trình riêng kẻo giằng co
        if self._is_dangphutheosau:
            self._yeucautudo = None
            return

        # Đang bật Theo sau: đi theo người được theo sau là đủ, không đi lộ trình điểm đánh riêng (cũng không kêu "Chưa có điểm đánh")
        if self._is_tudongtheosau:
            self._yeucautudo = None
            return

        while True:
            if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
                break

            diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            if diachimuctieu:
                if self.moitruong.get_is_nhanvattontai(diachimuctieu) and not self.moitruong.get_is_nhanvatdachet(diachimuctieu) and self.moitruong.get_is_cothetancong(diachimuctieu):
                    if self._yeucautudo is not None:
                        self.moitruong.action_ngatdichuyen()
                    break

            if self.moitruong.get_is_dangclickchuottrai(): break
            if self.moitruong.get_is_dangvankhi(): break
            if self.moitruong.get_is_nhanvatdachet(): break
            if self._idbandovuachet and self._is_tudongchaylenbandovuachet: break

            idbandohientai = self.moitruong.get_idbandohientai()

            # Điểm đánh của phó bản mượn ID bản đồ ngoài (Phong Yêu Kính) mà giờ đã ra ngoài: bỏ hết, kẻo chạy lên bản đồ thật cùng ID
            if self._is_lotrinhphobanmuonbando and self.moitruong.get_is_phobanmuonbando() is False:
                print(f"[LỘ TRÌNH] Đã ra khỏi phó bản ({self.moitruong.get_tenbandogame()}): bỏ {len(self._diemdanhxungquanhs)} điểm đánh của phó bản")
                self.botoanbo_diemdanhxungquanh()
                # Lệnh đi tới điểm kế của lộ trình có thể đã gửi ngay lúc vừa ra (trước khi bỏ điểm): dừng lại kẻo client đi tiếp,
                # ngắt lại sau 0.5s và 1s
                self.moitruong.action_ngatdichuyen()
                self._thoidiemngatdichuyenroiphobans = [time.time() + 0.5, time.time() + 1.]
                self._thoidiemroiphobanmuonbando = time.time()

            # Chưa đặt điểm đánh mà bản đồ có lộ trình mẫu thì tự chọn mẫu chưa ai dùng (trùng với nhân vật khác cũng không chọn lại).
            # Vừa ra khỏi phó bản mượn ID bản đồ thì chờ THOIGIANCHONAPLOTRINHROIPHOBAN: ID bản đồ đọc được còn là ID của phó bản
            # (tên đổi trước), chọn ngay là nạp lại mẫu của phó bản rồi chạy lên bản đồ thật cùng ID
            if not self._diemdanhxungquanhs and idbandohientai != BANDO_CHIENTRUONG and time.time() - self._thoidiemkiemtralotrinhgannhat > 5. \
                    and time.time() - self._thoidiemroiphobanmuonbando > THOIGIANCHONAPLOTRINHROIPHOBAN:
                self._thoidiemkiemtralotrinhgannhat = time.time()
                self.tuchon_lotrinhmau(idbandohientai)

            diemdanhxungquanhs = self._diemdanhxungquanhs

            if not diemdanhxungquanhs:
                key_map = idbandohientai if idbandohientai != BANDO_CHIENTRUONG else "{}_{}".format(idbandohientai, self.moitruong.get_idphechientruong())
                diemdanhxungquanhs = DIEMDANHXUNGQUANH_MAP.get(key_map, [])

            if not diemdanhxungquanhs:
                if time.time() - self._thoidiemphatamlacmapgannhat > 5.0:
                    # Xuyên Không Hành chỉ dùng khi bật tự động farm & về bán rác
                    if self.moitruong.get_tenmonphai() == "maoson" and self._is_tudongvebanrac:
                        print("[AUTO-MOVE] Bản đồ không có trong cấu hình. Mao Sơn dùng Xuyên Không Hành bay lên.")
                        self.moitruong.action_ngatdichuyen()
                        self.moitruong.action_thucthicaulenh("pf 4182.2")
                        self._thoidiemphatamlacmapgannhat = time.time()
                    elif self._is_tudongvebanrac and self._diemdanhxungquanhs:
                        self.moitruong.action_ngatdichuyen()
                        self.action_sudunghoithanhphu()
                        self._thoidiemphatamlacmapgannhat = time.time()
                    else:
                        # Tân Thủ Thôn / Chu Quốc / 7 quốc gia là nơi đứng chờ, mua bán: không cảnh báo
                        if not self._is_tudongdichientruong and idbandohientai not in (BANDO_TANTHUTHON, BANDO_CHUQUOC) and idbandohientai not in BANDO7QUOCGIAs:
                            phatam("Chưa có điểm đánh")
                        self._thoidiemphatamlacmapgannhat = time.time()
                break

            if self._iddiemdanhxungquanhhientai == -1 or not self._diemdanhxungquanhhientai:
                # Vừa mở bot chưa đọc được bản đồ hiện tại (False): chờ, không thì không có điểm nào "cùng bản đồ" và bị chọn điểm 0
                # (vd đang ở bản đồ thứ 2 của lộ trình lại chạy ngược về điểm đầu ở bản đồ 1)
                if not idbandohientai:
                    break
                best_index = 0
                min_dist = 999999.
                found_on_current_map = False

                for idx, point in enumerate(diemdanhxungquanhs):
                    p_map_id = point[2]

                    if p_map_id == idbandohientai:
                        dist = self.moitruong.get_khoangcachdiem(point[0], point[1])
                        if dist < min_dist:
                            min_dist = dist
                            best_index = idx
                            found_on_current_map = True

                if not found_on_current_map:
                    best_index = 0

                self._iddiemdanhxungquanhhientai = best_index
                self._diemdanhxungquanhhientai = diemdanhxungquanhs[best_index]
                self._thoidiembatdaudendiem = time.time()
                print(f"[Move] Bắt đầu lộ trình tại điểm #{best_index} (Map {self._diemdanhxungquanhhientai[2]})")

            canchuyendendiemtieptheo = False
            target_point = self._diemdanhxungquanhhientai
            target_map = target_point[2]

            if idbandohientai == target_map:
                dist_to_target = self.moitruong.get_khoangcachdiem(target_point[0], target_point[1])

                if dist_to_target <= 4.0:
                    canchuyendendiemtieptheo = True
                elif self._is_tudongvebanrac and time.time() - self._thoidiembatdaudendiem > 1.0 and self._is_diemtrongvungdongdoiuutien(target_point[0], target_point[1], self._laytoadodongdoikhacnhom()):
                    # Điểm đánh đang nằm trong vùng của nhân vật ưu tiên hơn => bỏ qua, đi điểm khác cho khỏi sát rạt nhau
                    canchuyendendiemtieptheo = True
                else:
                    if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                        if time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat() > 3.0:
                            if time.time() - self._thoidiembatdaudendiem > 10.0:
                                canchuyendendiemtieptheo = True
            else:
                if time.time() - self._thoidiembatdaudendiem > 90.0:
                    print("[Move] Quá thời gian chuyển map/đến điểm khác map -> Bỏ qua điểm này.")
                    canchuyendendiemtieptheo = True

            if canchuyendendiemtieptheo:
                # Lộ trình dò: đi hết 1 vòng mà đủ vị trí quái thì tự đề xuất lộ trình thật và nạp luôn (lượt sau đi theo lộ trình mới)
                if self._lotrinhmaudangdung.split("|")[1:2] == [TENMAUDO]:
                    self._sodiemdadilotrinhdo += 1
                    if self._sodiemdadilotrinhdo >= len(diemdanhxungquanhs) and self._chuyensanglotrinhdexuat():
                        break
                next_index = (self._iddiemdanhxungquanhhientai + 1) % len(diemdanhxungquanhs)

                self._iddiemdanhxungquanhhientai = next_index
                self._diemdanhxungquanhhientai = diemdanhxungquanhs[next_index]
                self._thoidiembatdaudendiem = time.time()
                target_map = self._diemdanhxungquanhhientai[2]

            is_khacbando = idbandohientai != target_map

            # Tắt "Đi tới điểm đánh ở bản đồ khác" (hoặc đang ở phó bản mượn ID bản đồ ngoài): chỉ đi điểm cùng bản đồ.
            # Đang ở phó bản mà điểm kế ở bản đồ khác không có đường chạy bộ tới (ra khỏi phó bản / sang tầng chưa có cổng): bỏ qua,
            # lấy điểm kế tiếp ở bản đồ này hoặc tới được; không còn điểm nào thì đứng yên
            is_chicungbando = not self._is_dilotrinhkhacbando or self.moitruong.get_is_phobanmuonbando()
            if is_khacbando and (is_chicungbando or (idbandohientai in BANDOPHOBANs and timduongbando(idbandohientai, target_map) is None)):
                sodiem = len(diemdanhxungquanhs)
                for buocnhay in range(1, sodiem + 1):
                    idx = (self._iddiemdanhxungquanhhientai + buocnhay) % sodiem
                    p_map_id = diemdanhxungquanhs[idx][2]
                    if p_map_id == idbandohientai or (not is_chicungbando and timduongbando(idbandohientai, p_map_id) is not None):
                        break
                else:
                    self._capnhatbuocdichuyen(f"Không có điểm đánh nào ở {laytenbando(idbandohientai)}" if is_chicungbando
                                              else f"Ở phó bản {laytenbando(idbandohientai)}: không có điểm đánh nào tới được")
                    break
                self._iddiemdanhxungquanhhientai = idx
                self._diemdanhxungquanhhientai = diemdanhxungquanhs[idx]
                self._thoidiembatdaudendiem = time.time()
                target_map = self._diemdanhxungquanhhientai[2]
                is_khacbando = idbandohientai != target_map

            if is_khacbando:
                # Điểm đánh ở bản đồ khác: phù / chạy bộ từng bản đồ một (không Hồi Thành Phù như trước)
                buoc = self._lapbuocditoibando(target_map)
                yeucautudomoi = self._thuchienbuocditoibando(buoc, target_map, self._diemdanhxungquanhhientai[:2], f"[LỘ TRÌNH] Điểm đánh ở {laytenbando(target_map)}")
                break
            self._capnhatbuocdichuyen(f"Chạy tới điểm đánh #{self._iddiemdanhxungquanhhientai + 1} ({self._diemdanhxungquanhhientai[0]}, {self._diemdanhxungquanhhientai[1]})")
            yeucautudomoi = {
                "yeucau": YEUCAUDICHUYENDICHUYENTUDO,
                "toadodich": self._diemdanhxungquanhhientai,
                "khoangcachtoida": 0
            }
            break

        self._yeucautudo = yeucautudomoi

    def nap_lotrinhmau(self, idbando, tenmau, is_nguocchieu = False, is_tuchon = False, is_bosung = False):
        # is_bosung: nối điểm của mẫu vào cuối lộ trình đang có (bỏ điểm trùng), giữ nguyên điểm đang đi tới; không thì ghi đè
        mau = next((m for m in util_tailotrinhmau().get(str(idbando), []) if m.get("ten") == tenmau), None)
        if not mau or not mau.get("diem"):
            print(f"[LỘ TRÌNH] Không tìm thấy mẫu '{tenmau}' của bản đồ {idbando}")
            return False
        # Mỗi điểm là [x, y] (cùng bản đồ của mẫu) hoặc [x, y, id bản đồ] khi lộ trình đi qua bản đồ khác
        diemdanhs = [(int(d[0]), int(d[1]), int(d[2]) if len(d) >= 3 else int(idbando)) for d in mau["diem"]]
        if is_nguocchieu:
            diemdanhs.reverse()
        if is_bosung and self._diemdanhxungquanhs:
            dacos = {tuple(diem[:3]) for diem in self._diemdanhxungquanhs}
            diemmois = [diem for diem in diemdanhs if diem not in dacos]
            self._diemdanhxungquanhs = list(self._diemdanhxungquanhs) + diemmois
            # Lộ trình giờ ghép từ nhiều mẫu: không còn là đúng 1 mẫu (giao diện tự nhận lại nếu trùng điểm 1 mẫu nào đó)
            self._lotrinhmaudangdung = ""
            self._is_lotrinhtuchon = False
            self._is_lotrinhphobanmuonbando = self._is_lotrinhphobanmuonbando or bool(self.moitruong.get_is_phobanmuonbando())
            print(f"[LỘ TRÌNH] Bổ sung mẫu '{tenmau}' bản đồ {idbando}{' (ngược chiều)' if is_nguocchieu else ''}: "
                  f"thêm {len(diemmois)} điểm (bỏ {len(diemdanhs) - len(diemmois)} điểm trùng), tổng {len(self._diemdanhxungquanhs)} điểm")
            phatam("Bổ sung lộ trình mẫu")
            return True
        self._diemdanhxungquanhs = diemdanhs
        self._iddiemdanhxungquanhhientai = -1
        self._diemdanhxungquanhhientai = None
        self._sodiemdadilotrinhdo = 0
        self._lotrinhmaudangdung = f"{idbando}|{tenmau}|{1 if is_nguocchieu else 0}"
        self._is_lotrinhtuchon = is_tuchon
        self._is_lotrinhphobanmuonbando = bool(self.moitruong.get_is_phobanmuonbando())
        print(f"[LỘ TRÌNH] Nạp mẫu '{tenmau}' bản đồ {idbando}{' (ngược chiều)' if is_nguocchieu else ''}: {len(diemdanhs)} điểm")
        phatam("Nạp lộ trình mẫu")
        return True

    def luu_lotrinhmau(self, tenmau):
        tenmau = (tenmau or "").replace("|", " ").strip()
        if not tenmau or not self._diemdanhxungquanhs:
            return False
        # Lộ trình gắn với bản đồ chiếm đa số điểm trong danh sách
        demtheobando = {}
        for diem in self._diemdanhxungquanhs:
            demtheobando[diem[2]] = demtheobando.get(diem[2], 0) + 1
        idbando = max(demtheobando, key = demtheobando.get)
        lotrinhmau = util_tailotrinhmau()
        dsmau = [m for m in lotrinhmau.get(str(idbando), []) if m.get("ten") != tenmau]
        dsmau.append({"ten": tenmau, "diem": [[d[0], d[1]] if d[2] == idbando else [d[0], d[1], d[2]] for d in self._diemdanhxungquanhs]})
        lotrinhmau[str(idbando)] = dsmau
        util_luulotrinhmau(lotrinhmau)
        self._lotrinhmaudangdung = f"{idbando}|{tenmau}|0"
        self._is_lotrinhtuchon = False
        print(f"[LỘ TRÌNH] Đã lưu mẫu '{tenmau}' cho bản đồ {idbando}")
        phatam("Lưu lộ trình mẫu")
        return True

    def _laylotrinhcuasokhac(self, idbando):
        # {(tên mẫu, ngược chiều): [id cửa sổ, ...]} của các cửa sổ khác đang dùng mẫu trên cùng bản đồ
        dangdung = {}
        if self.shared_data is None:
            return dangdung
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return dangdung
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict):
                continue
            phan = (info.get("_lotrinhmaudangdung") or "").split("|")
            if len(phan) == 3 and phan[0] == str(idbando):
                dangdung.setdefault((phan[1], phan[2] == "1"), []).append(idcuaso)
        return dangdung

    def thietlap_nguocchieulotrinh(self, is_nguocchieu):
        self._is_nguocchieulotrinh = bool(is_nguocchieu)

    def tuchon_lotrinhmau(self, idbando = None):
        # Chọn mẫu ít nhân vật khác dùng nhất trên cùng bản đồ; mẫu nào cũng có người dùng thì đi chiều còn lại để không bám đuôi nhau.
        # Ngang nhau thì đi theo chiều đã chọn ở ô "Đi ngược chiều" (_is_nguocchieulotrinh)
        idbando = idbando or self.moitruong.get_idbandohientai()
        dsmau = [m["ten"] for m in util_tailotrinhmau().get(str(idbando), []) if m.get("diem")]
        if not dsmau:
            return False
        dangdung = self._laylotrinhcuasokhac(idbando)
        def doban(luachon):
            tenmau, is_nguocchieu = luachon
            tong = len(dangdung.get((tenmau, False), [])) + len(dangdung.get((tenmau, True), []))
            return tong, len(dangdung.get(luachon, [])), is_nguocchieu != self._is_nguocchieulotrinh
        luachon = min(((tenmau, is_nguocchieu) for tenmau in dsmau for is_nguocchieu in (False, True)), key = doban)
        return self.nap_lotrinhmau(idbando, *luachon, is_tuchon = True)

    def get_solanthayquaibando(self):
        # Số lần nhân vật này đã thấy quái trên bản đồ hiện tại (hiện trên giao diện cho biết đủ dữ liệu đề xuất chưa)
        return sum(self._bangviquai.get(str(self.moitruong.get_idbandohientai()), {}).values())

    def dexuat_lotrinhmau(self):
        # Tự đề xuất lộ trình cho bản đồ hiện tại từ vị trí quái mọi nhân vật đã thấy, lưu thành mẫu TENMAUDEXUAT (ghi đè mẫu đề xuất cũ)
        idbando = self.moitruong.get_idbandohientai()
        self.luuvitriquai(True)
        demo = taiviquaibando(idbando)
        solanthay = sum(demo.values())
        if solanthay < SOLANTHAYQUAITOITHIEU:
            print(f"[LỘ TRÌNH] Mới thấy quái {solanthay} lần trên bản đồ {idbando}, cần ít nhất {SOLANTHAYQUAITOITHIEU} lần để đề xuất")
            return self.dexuat_lotrinhdo()
        # Client chưa có đối tượng tìm đường (chưa click di chuyển lần nào) thì không kiểm tra được đường đi, vẫn đề xuất
        is_kiemtraduong = self.moitruong.get_is_cotimduongcucbo()
        timduong = self.moitruong._get_chuoihuongtimduongcucbo if is_kiemtraduong else None
        diems, sobo = dexuatlotrinh(demo, timduong = timduong, is_vungcam = self._kiemtra_vungcam)
        if len(diems) < 2:
            print(f"[LỘ TRÌNH] Không đề xuất được lộ trình cho bản đồ {idbando} (chỉ còn {len(diems)} điểm đi được, bỏ {sobo} điểm)")
            phatam("Không đề xuất được lộ trình")
            return False
        lotrinhmau = util_tailotrinhmau()
        # Có lộ trình thật thì bỏ lộ trình dò (kẻo tự chọn mẫu lại chọn trúng nó)
        dsmau = [m for m in lotrinhmau.get(str(idbando), []) if m.get("ten") not in (TENMAUDEXUAT, TENMAUDO)]
        dsmau.append({"ten": TENMAUDEXUAT, "diem": [[x, y] for x, y in diems]})
        lotrinhmau[str(idbando)] = dsmau
        util_luulotrinhmau(lotrinhmau)
        print(f"[LỘ TRÌNH] Đề xuất mẫu '{TENMAUDEXUAT}' bản đồ {idbando} từ {solanthay} lần thấy quái: {diems}"
              f"{f' (bỏ {sobo} điểm không đi được)' if sobo else ''}{'' if is_kiemtraduong else ' (chưa kiểm tra đường đi: client chưa có đối tượng tìm đường)'}")
        phatam(f"Đã đề xuất lộ trình {len(diems)} điểm")
        return True

    def dexuat_lotrinhdo(self):
        # Bản đồ chưa đủ vị trí quái: đề xuất lộ trình dò phủ vùng đi được nối liền với chỗ đứng (lưới vật cản của client), tránh cổng /
        # điểm xuất hiện và vùng cấm, lưu thành mẫu TENMAUDO và nạp luôn. Bot chạy lộ trình này thấy quái thì ghi vị trí, đủ dữ liệu
        # bấm Tự đề xuất lần nữa là ra lộ trình thật (mẫu dò bị bỏ)
        idbando = self.moitruong.get_idbandohientai()
        luoi = self.moitruong.get_luoivatcanbando()
        if not luoi:
            phatam("Chưa đọc được bản đồ")
            return False
        congs = nhiemvu_laydiemcong(idbando)

        def is_tranh(x, y):
            return any(math.dist((x, y), c) < KHOANGCACHTRANHCONG for c in congs) or self._kiemtra_vungcam(x, y)

        batdau = time.time()
        diems = dexuatlotrinhdo(luoi, self.moitruong.get_toado(), is_tranh)
        if len(diems) < 2:
            print(f"[LỘ TRÌNH] Không đề xuất được lộ trình dò cho bản đồ {idbando} ({len(diems)} điểm)")
            phatam("Không đề xuất được lộ trình dò")
            return False
        lotrinhmau = util_tailotrinhmau()
        dsmau = [m for m in lotrinhmau.get(str(idbando), []) if m.get("ten") != TENMAUDO]
        dsmau.append({"ten": TENMAUDO, "diem": [[x, y] for x, y in diems]})
        lotrinhmau[str(idbando)] = dsmau
        util_luulotrinhmau(lotrinhmau)
        print(f"[LỘ TRÌNH] Chưa đủ vị trí quái: đề xuất mẫu '{TENMAUDO}' bản đồ {idbando} {len(diems)} điểm "
              f"({time.time() - batdau:.1f}s): {diems}")
        self.nap_lotrinhmau(idbando, TENMAUDO)
        phatam(f"Chưa có vị trí quái, đã tạo lộ trình dò {len(diems)} điểm")
        return True

    def _chuyensanglotrinhdexuat(self):
        # Hết 1 vòng lộ trình dò: đủ vị trí quái thì đề xuất lộ trình thật (mẫu dò bị bỏ) và nạp, chưa đủ thì đếm lại, đi thêm vòng nữa
        self._sodiemdadilotrinhdo = 0
        idbando = self.moitruong.get_idbandohientai()
        self.luuvitriquai(True)
        solanthay = sum(taiviquaibando(idbando).values())
        if solanthay < SOLANTHAYQUAITOITHIEU:
            print(f"[LỘ TRÌNH] Dò hết 1 vòng bản đồ {idbando} mới thấy quái {solanthay} lần (cần {SOLANTHAYQUAITOITHIEU}): dò thêm vòng nữa")
            return False
        if not self.dexuat_lotrinhmau():
            return False
        print(f"[LỘ TRÌNH] Dò xong bản đồ {idbando}: chuyển sang lộ trình '{TENMAUDEXUAT}'")
        return self.nap_lotrinhmau(idbando, TENMAUDEXUAT)

    def them_diemdanhxungquanh(self, diemdanhxungquanh):
        if diemdanhxungquanh and diemdanhxungquanh not in self._diemdanhxungquanhs:
            self._diemdanhxungquanhs.append(diemdanhxungquanh)
            self._lotrinhmaudangdung = ""
            self._is_lotrinhtuchon = False
            self._is_lotrinhphobanmuonbando = self._is_lotrinhphobanmuonbando or bool(self.moitruong.get_is_phobanmuonbando())
            print(self._diemdanhxungquanhs)
            phatam("Thêm điểm đánh xung quanh. Tổng cộng {}".format(len(self._diemdanhxungquanhs)))

    def botoanbo_diemdanhxungquanh(self):
        self._diemdanhxungquanhs.clear()
        self._iddiemdanhxungquanhhientai = -1
        self._diemdanhxungquanhhientai = None
        self._lotrinhmaudangdung = ""
        self._is_lotrinhtuchon = False
        self._is_lotrinhphobanmuonbando = False
        phatam("Bỏ toàn bộ điểm đánh xung quanh")

    def get_lydokhonghoithanhphu(self, idbandodich = None, is_roiphoban = False):
        # Không được Hồi Thành Phù (mỗi lần GIAHOITHANHPHU lượng) thì trả lý do: thiếu tiền, hoặc đã dùng SOLANHOITHANHPHUTOIDA lần trong
        # THOIGIANDEMHOITHANHPHU giây để tới cùng bản đồ đích idbandodich (đang lặp: về rồi lại không tới được nơi cần tới; sư môn mỗi
        # nhiệm vụ đi một nơi nên dùng nhiều lần tới các nơi khác nhau là bình thường), hoặc đang ở phó bản (về là mất phó bản; trừ khi
        # is_roiphoban: cố ý ra). Được thì None
        if self.moitruong.get_idbandohientai() in BANDOPHOBANs and not is_roiphoban:
            return f"đang ở phó bản {laytenbando(self.moitruong.get_idbandohientai())}"
        if self.moitruong.get_is_phobanmuonbando() and not is_roiphoban:
            return f"đang ở {self.moitruong.get_tenbandogame()}"
        nganluong = self.moitruong.get_nganluong()
        if nganluong is not None and nganluong < GIAHOITHANHPHU:
            return f"còn {nganluong} lượng, không đủ {GIAHOITHANHPHU} lượng Hồi Thành Phù"
        self._thoidiemhoithanhphus = [(t, d) for t, d in self._thoidiemhoithanhphus if time.time() - t < THOIGIANDEMHOITHANHPHU]
        solan = sum(1 for _, d in self._thoidiemhoithanhphus if d == idbandodich)
        if solan >= SOLANHOITHANHPHUTOIDA:
            noi = f" để tới {laytenbando(idbandodich)}" if idbandodich else ""
            return f"đã Hồi Thành Phù {solan} lần{noi} trong {round(THOIGIANDEMHOITHANHPHU / 60)} phút (có thể đang lặp)"
        return None

    def action_sudunghoithanhphu(self, idbandodich = None, is_roiphoban = False):
        if time.time() - self._thoidiemsudunghoithanhphugannhat > 6.:
            self._thoidiemsudunghoithanhphugannhat = time.time()
            lydo = self.get_lydokhonghoithanhphu(idbandodich, is_roiphoban)
            if lydo:
                print(f"[HỒI THÀNH PHÙ] Không dùng: {lydo}")
                phatam("Không dùng Hồi Thành Phù")
                return False
            self._thoidiemhoithanhphus.append((time.time(), idbandodich))
            #self.action_sudungvatphamhanhtrang(HOITHANHPHU)
            self.moitruong.action_thucthicaulenh("dGludmF0 2")
            return True
        return False

    def action_dichuyenlenbandofarm(self):
        # Đang ở Tân Thủ Thôn / Chu: phù tới bản đồ của điểm đánh đầu tiên bằng NPC của cách tốt nhất (_phutoibando), phù tới bản đồ gần
        # thì lộ trình chạy bộ tiếp
        target_map = self._diemdanhxungquanhs[0][2] if self._diemdanhxungquanhs else 0
        if not target_map:
            return
        if not layphuongandichuyen(target_map):
            print(f"[DI-CHUYEN] Không phù tới được {laytenbando(target_map)} (cũng không phù tới bản đồ nào gần đó)")
            return
        yeucau = self._phutoibando(target_map, self.moitruong.get_idbandohientai(), f"[DI-CHUYEN] Lên bãi farm {laytenbando(target_map)}")
        if yeucau:
            x_npc, y_npc, _ = yeucau["toadodich"]
            self.moitruong.action_dichuyengiukhoangcachtoidadiem(x_npc, y_npc, khoangcachtoida = 3.)
            self._thoidiemsudunghoithanhphugannhat = time.time()
