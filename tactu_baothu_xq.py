# Phần bảo thú giang hồ: triệu hồi, điều khiển.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__

import time

from hangso_xq import *
from thongbao_xq import baosuco, LYDOTAMNGUNGTUXA
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam, canhbao


class TacTuBaoThu:
    def action_tudongtrieuhoibaothugiangho(self):
        if self._is_tudongtrieuhoibaothugiangho:
            while True:
                # Cho bảo thú ăn không ngắt vận khí => vẫn cho ăn lúc đang vận khí; triệu hồi bảo thú giang hồ cũng phải vận khí nên
                # đang vận khí (chế đồ...) thì không triệu hồi
                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                iddoituongbaothugiangho = self.moitruong.get_iddoituongbaothugiangho()

                if not iddoituongbaothugiangho:
                    break

                if time.time() - self._thoidiemsudungthucanbaothugannhat > 2. and self.moitruong.get_dotrungthanhbaothugiangho() <= 80:
                    iddoituongcaocapbaothuthucpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPBAOTHUTHUCPHAM)
                    if iddoituongcaocapbaothuthucpham:
                        if self.moitruong.action_sudungvatphambaothu(iddoituongcaocapbaothuthucpham, iddoituongbaothugiangho, delay = 0.0):
                            self._thoidiemsudungthucanbaothugannhat = time.time()

                if not self.moitruong.get_is_datrieuhoibaothugiangho() and self.moitruong.get_idbandohientai() in BANDOKHONGPKs and time.time() - self._thoidiemtudongtrieuhoibaothugiangho > 1. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM and time.time() - self._thoidiemtamngungdichuyensudungkynang > 0. and not self.moitruong.get_is_dangvankhi():
                    if self.moitruong.action_trieuhoibaothu(iddoituongbaothugiangho, delay = 0.0):
                        self._thoidiemtudongtrieuhoibaothugiangho = time.time()

                break

    def action_tudongdieukhienbaothu(self):
        is_baothukynangtrieuhoihetnoiluc = False
        is_baothukynangtrieuhoihetsinhluc = False
        dsbaothutrieuhoi = []  # (id, toạ độ, khoảng cách) bảo thú kỹ năng triệu hồi cùng bản đồ
        if self._is_tudongdieukhienbaothu:
            while True:
                if self.moitruong.get_is_nhanvatdachet():
                    break

                idbandohientai = self.moitruong.get_idbandohientai()
                soluongbaothutoida = 3
                iddoituongbaothugiangho = self.moitruong.get_iddoituongbaothugiangho()
                # ID ở cấu trúc giang hồ vẫn còn khi đã cất bảo thú, có thể trùng ID bảo thú triệu hồi mới => chỉ tin khi đang triệu hồi giang hồ
                is_datrieuhoibaothugiangho = bool(iddoituongbaothugiangho) and self.moitruong.get_is_datrieuhoibaothugiangho()

                for sothutu in range(1, soluongbaothutoida + 1):
                    iddoituongbaothu = self.moitruong.get_iddoituongbaothu(sothutu)

                    if not iddoituongbaothu:
                        continue

                    # Nhận bảo thú giang hồ theo ID, không đoán theo tên: trước đây tên có "(...)" là triệu hồi, còn lại là giang hồ,
                    # lượt nào đọc tên hụt (rỗng/chưa tải) thì bảo thú triệu hồi bị coi là giang hồ và bị ra lệnh Chờ đợi ("pet ...# 3")
                    # Tên ô bảo thú triệu hồi luôn có dạng "Cương Thi ( ... )": có "(" thì chắc chắn không phải giang hồ
                    tenbaothu = self.moitruong.get_tendoituongbaothu(sothutu) or ""
                    is_baothugiangho = is_datrieuhoibaothugiangho and iddoituongbaothu == iddoituongbaothugiangho and "(" not in tenbaothu

                    # Bảo thú gọi bằng vật phẩm (Thần Thú - Chuột, Song Tử, Thuỷ Bình...) cũng nằm ở các ô này nhưng không có % sinh lực / nội lực
                    # (+0x1D4 / +0x1D8 luôn 0, đo 2026-11-05 trên Thần Thú - Chuột) => trước đây bị coi là bảo thú triệu hồi "hết máu, hết nội lực"
                    # nên Mao Sơn buff Lưu Huyết Thuật / Di Tinh Đại Pháp liên tục dù đệ chưa mất giọt máu nào. Bỏ qua hẳn: không buff, không ra lệnh
                    # (bảo thú triệu hồi còn sống không bao giờ 0% cả máu lẫn nội lực; tên triệu hồi luôn có "(")
                    if not is_baothugiangho and "(" not in tenbaothu and (
                            tenbaothu in BAOTHUVATPHAMs
                            or (not self.moitruong.get_phantramsinhlucconlaidoituongbaothukynangtrieuhoi(sothutu)
                                and not self.moitruong.get_phantramnoilucconlaidoituongbaothukynangtrieuhoi(sothutu))):
                        continue
                    is_baothukynangtrieuhoi = not is_baothugiangho

                    toadodoituongbaothu = self.moitruong.get_toadodoituongbaothu(sothutu)
                    idbandohientaidoituongbaothu = self.moitruong.get_idbandohientaidoituongbaothu(sothutu)

                    khoangcach = self.moitruong.get_khoangcachdiem(*toadodoituongbaothu)

                    is_baothudangogan = idbandohientaidoituongbaothu == idbandohientai and khoangcach <= KHOANGCACHTOANMANHINH

                    if is_baothukynangtrieuhoi:
                        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                        # Chỉ cần 1 con yếu là bật cờ (trước đây gán thẳng nên con duyệt sau cùng ghi đè kết quả các con trước)
                        if self.moitruong.get_phantramnoilucconlaidoituongbaothukynangtrieuhoi(sothutu) < 50:
                            is_baothukynangtrieuhoihetnoiluc = True
                        if self.moitruong.get_phantramsinhlucconlaidoituongbaothukynangtrieuhoi(sothutu) < PHANTRAMSINHLUCLUUHUYETTHUAT:
                            is_baothukynangtrieuhoihetsinhluc = True

                        # Gọi về khi bảo thú khác bản đồ hoặc ra xa quá KHOANGCACHGOIBAOTHUVE; đã gọi thì gọi tới khi về gần
                        # KHOANGCACHBAOTHUDAVE mới thôi (không thì vừa về tới mép lại bị lệnh tấn công kéo đi xa tiếp)
                        if idbandohientaidoituongbaothu != idbandohientai or khoangcach > KHOANGCACHGOIBAOTHUVE:
                            self._idbaothudanggoive.add(iddoituongbaothu)
                        elif khoangcach <= KHOANGCACHBAOTHUDAVE:
                            self._idbaothudanggoive.discard(iddoituongbaothu)

                        is_muctieutancongduoc = bool(diachimuctieu) and self.moitruong.get_is_cothetancong(diachimuctieu) and self.moitruong.get_khoangcach(diachimuctieu) <= KHOANGCACHTOANMANHINH
                        iddoituongnhanvatmuctieu = self.moitruong.get_iddoituong(diachimuctieu) if is_muctieutancongduoc else 0

                        if self._is_danggomquai:
                            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu)
                        elif iddoituongbaothu in self._idbaothudanggoive:
                            # Gọi đều mỗi THOIGIANGOIBAOTHUVE giây tới khi về gần (mỗi lệnh chưa đủ xa để phù về chỉ chạy thêm một đoạn)
                            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu, delay = THOIGIANGOIBAOTHUVE)
                        elif iddoituongnhanvatmuctieu:
                            self.moitruong.action_ralenhbaothutancong(iddoituongbaothu, iddoituongnhanvatmuctieu)
                        elif not (self.moitruong.get_is_baothudangtheosau(iddoituongbaothu) and idbandohientaidoituongbaothu == idbandohientai
                                  and khoangcach <= KHOANGCACHBAOTHUDANEO):
                            # Không có mục tiêu: trước đây không ra lệnh gì nên bảo thú cứ đuổi theo quái cũ/đứng im trong khi nhân vật đi chỗ khác.
                            # Kéo về sát cạnh thường xuyên (người dùng 2026-11-19): trước đây theo sau trong 9 ô là thôi gọi, nó tụt lại sau góc
                            # vách rồi kẹt. Mỗi lệnh Theo sau nó tìm lại đường một đoạn => gọi lại mỗi 1s tới khi về trong KHOANGCACHBAOTHUDANEO ô
                            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu, delay = 1.)

                        if idbandohientaidoituongbaothu == idbandohientai:
                            dsbaothutrieuhoi.append((iddoituongbaothu, toadodoituongbaothu, khoangcach))

                    elif is_baothugiangho:
                        if self.moitruong.get_idbandohientai() in BANDOKHONGPKs and self.moitruong.get_trangthaihanhvidoituongbaothu(sothutu) != 3:
                            self.moitruong.action_ralenhbaothudungim(iddoituongbaothu, delay = 0.)
                        elif self._is_tudongsudungkynangbaothu:
                            idkynangbaothu_map = {self.moitruong.get_idkynangbaothugiangho(i): i for i in range(11)}
                            idkynangbaothucothesudungs = {KYNANGBAOTHU_CAOCAPTHIENCAN, }
                            if set(idkynangbaothu_map.keys()) & idkynangbaothucothesudungs:
                                if time.time() - self._thoidiemhoiphucbaothugannhat > 5.:
                                    if self.moitruong.get_noilucconlaibaothugiangho() <= 120:
                                        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(LAOTUU)
                                        if iddoituongvatpham:
                                            if self.moitruong.action_sudungvatphambaothu(iddoituongvatpham, iddoituongbaothu):
                                                self._thoidiemhoiphucbaothugannhat = time.time()
                                        else:
                                            canhbao(self.moitruong, "Hết lão tửu")
                                            baosuco(self.moitruong, "vatpham", "Hết Lão Tửu cho bảo thú", giancach = 1800.)
                                            self._thoidiemhoiphucbaothugannhat = time.time()

                                    if self.moitruong.get_sinhluctoidabaothugiangho() - self.moitruong.get_sinhlucconlaibaothugiangho() >= 1200:
                                        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(DUAHAU)
                                        if iddoituongvatpham:
                                            if self.moitruong.action_sudungvatphambaothu(iddoituongvatpham, iddoituongbaothu):
                                                self._thoidiemhoiphucbaothugannhat = time.time()

                                diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                                if diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu) and self.moitruong.get_noilucconlaibaothugiangho() >= 60:
                                    if KYNANGBAOTHU_CAOCAPTHIENCAN in idkynangbaothu_map and self.moitruong.get_is_kynangbaothugianghosansang(idkynangbaothu_map[KYNANGBAOTHU_CAOCAPTHIENCAN]) and self.moitruong.get_is_cothegaychoang(diachimuctieu):
                                        if not is_baothudangogan and time.time() - self._thoidiemsudungthaotacbaothugannhat > 0.25:
                                            self._thoidiemsudungthaotacbaothugannhat = time.time()
                                            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu, delay = 0.)
                                        elif is_baothudangogan:
                                            self.moitruong.action_sudungkynangbaothu(KYNANGBAOTHU_CAOCAPTHIENCAN, diachimuctieu)
                break
        self._is_baothukynangtrieuhoihetnoiluc = is_baothukynangtrieuhoihetnoiluc
        self._is_baothukynangtrieuhoihetsinhluc = is_baothukynangtrieuhoihetsinhluc
        try:
            self._capnhatbaothutheosau(dsbaothutrieuhoi)
        except Exception as e:
            print(f"[BẢO THÚ THEO SAU] Lỗi: {e}")
            self.moitruong.toadoneobaothu = None
            self.moitruong.baothutheosaugan = None

    def _capnhatbaothutheosau(self, dsbaothu):
        # Bỏ quay lại đón bảo thú (người dùng 2026-11-20). Thay bằng: báo cho tầng di chuyển (moitruong) toạ độ bảo thú gần để A* chọn
        # đường thoáng / lùi chỗ còn thấy nó (toadoneobaothu), và con đang Theo sau / bị gọi về gần nhất (baothutheosaugan) để lúc đi
        # vòng góc vách thì dừng ở chỗ nó còn thấy mình, gọi nó theo kịp rồi mới rẽ (moitruong._catduongchobaothu): nó chạy thẳng về
        # mình không vướng vách
        trongtam = [b for b in dsbaothu if b[2] <= KHOANGCACHGOIBAOTHUVE] if not self.moitruong.get_is_nhanvatdachet() else []
        self.moitruong.toadoneobaothu = min(trongtam, key = lambda b: b[2])[1] if trongtam else None
        theosau = [b for b in trongtam if self.moitruong.get_is_baothudangtheosau(b[0]) or b[0] in self._idbaothudanggoive]
        self.moitruong.baothutheosaugan = min(theosau, key = lambda b: b[2]) if theosau else None
