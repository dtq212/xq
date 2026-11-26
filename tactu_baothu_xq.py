# Phần bảo thú giang hồ: triệu hồi, điều khiển.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__

import re
import time
import unicodedata

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
                    iddoituongcaocapbaothuthucpham = next(filter(None, (self.moitruong.action_timkiemvatphamhanhtrang(t) for t in CAOCAPBAOTHUTHUCPHAMs)), False)
                    if iddoituongcaocapbaothuthucpham:
                        if self.moitruong.action_sudungvatphambaothu(iddoituongcaocapbaothuthucpham, iddoituongbaothugiangho, delay = 0.0):
                            self._thoidiemsudungthucanbaothugannhat = time.time()

                # Độ trung thành dưới DOTRUNGTHANHTOITHIEUTRIEUHOI thì không triệu hồi, báo người dùng (người dùng 2026-11-26)
                is_dutrungthanh = True
                if not self.moitruong.get_is_datrieuhoibaothugiangho():
                    dotrungthanh = self.moitruong.get_dotrungthanhbaothugiangho()
                    if dotrungthanh is not False and dotrungthanh is not None and dotrungthanh < DOTRUNGTHANHTOITHIEUTRIEUHOI:
                        is_dutrungthanh = False
                        if time.time() - self._thoidiembaotrungthanhthap > 600.:
                            self._thoidiembaotrungthanhthap = time.time()
                            noidung = f"Bảo thú {self.moitruong.get_tendoituongbaothugiangho()} độ trung thành {dotrungthanh} < {DOTRUNGTHANHTOITHIEUTRIEUHOI}, không triệu hồi"
                            self.moitruong._inlog(f"[BẢO THÚ] {noidung}")
                            canhbao(self.moitruong, noidung)
                            baosuco(self.moitruong, "vatpham", noidung, giancach = 1800.)

                if is_dutrungthanh and not self.moitruong.get_is_datrieuhoibaothugiangho() and not self._is_chotrieuhoilaibaothugiangho() and self.moitruong.get_idbandohientai() in BANDOKHONGPKs and time.time() - self._thoidiemtudongtrieuhoibaothugiangho > 1. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM and time.time() - self._thoidiemtamngungdichuyensudungkynang > 0. and not self.moitruong.get_is_dangvankhi():
                    if self.moitruong.action_trieuhoibaothu(iddoituongbaothugiangho, delay = 0.0):
                        self._thoidiemtudongtrieuhoibaothugiangho = time.time()

                break

    def action_tudongeptinhnguyendon(self):
        # Ép Tinh Nguyên Đơn vào bảo thú giang hồ (người dùng 2026-11-25, acc Thỏ / Ngốc / Gạ mới thu nhận): trong túi có Tinh Nguyên Đơn
        # thì "pet <id bảo thú># fuse_yy <id đơn>#" (lệnh cũ trong loop_xq.py) tới khi bảo thú đủ SOKYNANGBAOTHUEPTINHNGUYENDON kỹ năng
        # bất kỳ, sau này người dùng tự ép Tinh Nguyên Đơn kỹ năng chuẩn. Đủ số kỹ năng thì thôi hẳn, không ép đè.
        # Ép có lúc thêm ô kỹ năng, có lúc THAY một kỹ năng cũ (log 342/347/364 2026-11-25: 2 kỹ năng "Kháng và Nội Công, Độc Nha" ép
        # Miễn Nhiễm Trầm Mặc ra "Kháng và Nội Công, Miễn Nhiễm Trầm Mặc", vẫn 2) => thay cũng là lệnh có tác dụng, ép tiếp.
        # Chỉ khi danh sách kỹ năng không đổi gì EPTINHNGUYENDONTOIDAKHONGTANG lần liền mới ngưng con đó (lệnh sai...) và báo
        if not self._is_tudongeptinhnguyendon:
            # Tắt giữa chừng: bỏ lần ép đang chờ so, khỏi tính nhầm "không đổi" lúc bật lại
            self._eptinhnguyendontruoc = None
            return
        if time.time() - self._thoidiemeptinhnguyendongannhat < THOIGIANEPTINHNGUYENDON:
            return
        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return
        iddoituongbaothu = self.moitruong.get_iddoituongbaothugiangho()
        if not iddoituongbaothu or iddoituongbaothu in self._baothungungeptinhnguyendon:
            return
        # Ô 0 là kỹ năng sẵn có của bảo thú (Quy: "Kháng và Nội Công"), không hiện ở bảng "Kỹ năng chiến đấu" và ép không bao giờ
        # đè (log 342/347/364 2026-11-25) => không đếm. Trước đây đếm cả ô này nên dừng khi bảng mới có 4 kỹ năng (người dùng báo)
        tenkynangs = []
        for i in range(1, 11):
            if self.moitruong.get_idkynangbaothugiangho(i):
                tenkynangs.append(self.moitruong.get_tenkynangbaothugiangho(i) or "?")
        sokynang = len(tenkynangs)

        # Lần ép trước: so danh sách kỹ năng để biết lệnh có tác dụng không (thêm hoặc thay)
        truoc = self._eptinhnguyendontruoc
        if truoc and truoc[0] == iddoituongbaothu:
            # Viên kỹ năng công kích mà bảo thú đã có năng lực công kích: máy chủ không ép ngay mà gửi menu hội thoại "Bảo thú Quy đã có
            # năng lực công kích, năng lực mới sẽ thay thế năng lực cũ, có muốn hợp thành không ?" (1.Xác nhận / 2.Rời khỏi, ảnh acc 359
            # 2026-11-25). Người dùng: không xác nhận, đóng hộp rồi ép viên khác => bỏ qua viên đó cho con này, không tính "không đổi"
            noidung = self.moitruong.get_noidungcuasotuychon()
            if "thay thế năng lực cũ" in unicodedata.normalize("NFC", noidung).lower():
                self.moitruong._inlog(f"[TINH NGUYÊN ĐƠN] viên {truoc[3]:x} sẽ THAY năng lực công kích => bỏ qua, ép viên khác | lệnh menu:"
                                      f" {self.moitruong.get_lenhcuasotuychons()} | nhãn: {self.moitruong.get_nhanluachoncuasotuychons()}")
                self.moitruong.xoa_noidungcuasotuychon()
                self._tinhnguyendonboqua.add((iddoituongbaothu, truoc[3]))
                self._eptinhnguyendontruoc = None
                truoc = None
        if truoc and truoc[0] == iddoituongbaothu:
            if sokynang > truoc[1]:
                self.moitruong._inlog(f"[TINH NGUYÊN ĐƠN] bảo thú {self.moitruong.get_tendoituongbaothugiangho()} lên {sokynang} kỹ năng: {', '.join(tenkynangs)}")
                self._solaneptinhnguyendonkhongtang = 0
            elif tenkynangs != truoc[2]:
                self.moitruong._inlog(f"[TINH NGUYÊN ĐƠN] ép bị THAY kỹ năng, vẫn {sokynang}: {', '.join(truoc[2])} -> {', '.join(tenkynangs)}")
                self._solaneptinhnguyendonkhongtang = 0
            else:
                # Không đổi: thường là viên trùng kỹ năng bảo thú đã có (máy chủ báo "Bảo thú đã có kỹ năng này", không ép, log 354
                # 2026-11-25: Phi Hành Thuật ép lại 3 lần rồi ngưng cả con) => bỏ viên đó cho con này, ép viên khác. Chỉ ngưng cả con khi
                # EPTINHNGUYENDONTOIDAKHONGTANG viên khác nhau liền nhau đều không đổi (lệnh sai...)
                self._tinhnguyendonboqua.add((iddoituongbaothu, truoc[3]))
                self._solaneptinhnguyendonkhongtang += 1
                self.moitruong._inlog(f"[TINH NGUYÊN ĐƠN] ép xong kỹ năng không đổi, vẫn {sokynang} => bỏ qua viên {truoc[3]:x}"
                                      f" (lần {self._solaneptinhnguyendonkhongtang})")
                if self._solaneptinhnguyendonkhongtang >= EPTINHNGUYENDONTOIDAKHONGTANG:
                    self._baothungungeptinhnguyendon.add(iddoituongbaothu)
                    self._eptinhnguyendontruoc = None
                    canhbao(self.moitruong, "Ép Tinh Nguyên Đơn không đổi kỹ năng bảo thú", is_block = False, is_phatam = False)
                    return
            self._eptinhnguyendontruoc = None

        if sokynang >= SOKYNANGBAOTHUEPTINHNGUYENDON:
            return
        tenkynangcos = [t for t in [self.moitruong.get_tenkynangbaothugiangho(0)] + tenkynangs if t]
        iddoituongvatpham = self._timtinhnguyendonduocep(iddoituongbaothu, tenkynangcos)
        if not iddoituongvatpham:
            return
        caulenh = "pet {}# fuse_yy {}#".format(hex(iddoituongbaothu), hex(iddoituongvatpham)).replace("0x", "")
        # Xoá lời thoại menu cũ để lượt sau biết hộp "thay thế năng lực cũ" là trả lời của lần ép này. Đang có menu hội thoại mở (việc
        # khác của bot đang nói chuyện NPC) thì thôi lượt này, khỏi đóng nhầm menu của việc đó
        if self.moitruong.get_is_danghiencuasotuychon():
            return
        self.moitruong.xoa_noidungcuasotuychon()
        if self.moitruong.action_thucthicaulenh2(caulenh, delay = 0.):
            self._thoidiemeptinhnguyendongannhat = time.time()
            self._eptinhnguyendontruoc = (iddoituongbaothu, sokynang, tenkynangs, iddoituongvatpham)
            self.moitruong._inlog(f"[TINH NGUYÊN ĐƠN] ép vào {self.moitruong.get_tendoituongbaothugiangho()} (đang {sokynang} kỹ năng"
                                  f"{': ' + ', '.join(tenkynangs) if tenkynangs else ''}, đã triệu hồi {self.moitruong.get_is_datrieuhoibaothugiangho()}): {caulenh}")

    def _timtinhnguyendonduocep(self, iddoituongbaothu, tenkynangcos = ()):
        # Tinh Nguyên Đơn đầu tiên trong túi được phép ép: chừa lại viên mà mô tả chứa TINHNGUYENDONGIUs (kỹ năng chuẩn, người dùng
        # 2026-11-25). Phân loại theo ID vật phẩm, nhớ trong _phanloaitinhnguyendon_map: lần đầu desc lại (is_napmoi) vì mô tả theo ô,
        # ô vừa đổi đồ có thể còn mô tả món cũ. Chưa đọc được mô tả thì không ép viên đó (thà bỏ lượt còn hơn ép mất viên chuẩn)
        idvatphams = self.moitruong._docdanhsachidvatphamhanhtrang(self.moitruong.get_soluongvatphamhanhtrangtoida() + 1)
        for i, ten in enumerate(self.moitruong.get_danhsachtenvatphamhanhtrang()):
            if ten != TINHNGUYENDON or i >= len(idvatphams) or not idvatphams[i]:
                continue
            iddoituongvatpham = idvatphams[i]
            if (iddoituongbaothu, iddoituongvatpham) in self._tinhnguyendonboqua:
                continue
            is_giu = self._phanloaitinhnguyendon_map.get(iddoituongvatpham)
            if is_giu is None:
                mota = self.moitruong.get_motavatphamhanhtrang(i, is_napmoi = True)
                if not mota:
                    continue
                motachuan = " ".join(unicodedata.normalize("NFC", mota).split()).lower()
                khop = [t for t in TINHNGUYENDONGIUs if unicodedata.normalize("NFC", t).lower() in motachuan]
                # Tên màu vàng: mã màu đầu tiên của mô tả thô là \x1bY (đơn thường tên xanh \x1bC)
                mamau = re.search(r"\x1b(.)", self.moitruong.get_motathovatphamhanhtrangcosan(i) or "")
                if mamau and mamau.group(1) == "Y":
                    khop.append("tên vàng")
                for t in TINHNGUYENDONGIU_KYNANGs:
                    if re.search(r"kỹ năng\s*[:：]\s*" + re.escape(unicodedata.normalize("NFC", t).lower()) + r"(?!\w)", motachuan):
                        khop.append("kỹ năng " + t)
                for t in TINHNGUYENDONGIU_CHISO5s:
                    c = re.escape(unicodedata.normalize("NFC", t).lower())
                    if re.search(c + r"[^,.，。]{0,40}?(?<!\d)5\s*%", motachuan) or re.search(r"(?<!\d)5\s*%\s*" + c, motachuan):
                        khop.append(t + " 5%")
                is_giu = bool(khop)
                self._phanloaitinhnguyendon_map[iddoituongvatpham] = is_giu
                tenkynang = re.search(r"kỹ năng\s*[:：]\s*(.+?)\s+kỹ năng của bảo thú", motachuan)
                if tenkynang:
                    self._kynangtinhnguyendon_map[iddoituongvatpham] = tenkynang.group(1).strip()
                self.moitruong._inlog(f"[TINH NGUYÊN ĐƠN] ô {i} id {iddoituongvatpham:x}: {'GIỮ (' + ', '.join(khop) + ')' if is_giu else 'được ép'}"
                                      f" | màu {mamau.group(1) if mamau else '?'} | mô tả: {motachuan[:200]}")
            if is_giu:
                continue
            # Viên trùng kỹ năng bảo thú đã có: máy chủ không ép ("Bảo thú đã có kỹ năng này", log 354 2026-11-25) => bỏ qua. Tên kỹ năng
            # trong bảo thú bị cắt (~12 ký tự, "Phi Hành Thuật" -> "Phi Hành Thuậ") => so tiền tố
            tenkynangvien = self._kynangtinhnguyendon_map.get(iddoituongvatpham)
            if tenkynangvien and any(tenkynangvien == t or (len(t) >= 6 and tenkynangvien.startswith(t))
                                     for t in (unicodedata.normalize("NFC", x).strip().lower() for x in tenkynangcos)):
                continue
            return iddoituongvatpham
        return False

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
                if is_datrieuhoibaothugiangho:
                    self._thuhoibaothugianghomauthap(iddoituongbaothugiangho)

                for sothutu in range(1, soluongbaothutoida + 1):
                    iddoituongbaothu = self.moitruong.get_iddoituongbaothu(sothutu)

                    if not iddoituongbaothu:
                        continue

                    if self._is_epbaothubidong:
                        self._epbaothubidong(sothutu, iddoituongbaothu)

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

                        is_muctieutancongduoc = bool(diachimuctieu) and self.moitruong.get_is_cothetancong(diachimuctieu) and self.moitruong.get_khoangcach(diachimuctieu) <= KHOANGCACHTOANMANHINH
                        iddoituongnhanvatmuctieu = self.moitruong.get_iddoituong(diachimuctieu) if is_muctieutancongduoc else 0
                        self._keobaothutheo(iddoituongbaothu, idbandohientaidoituongbaothu == idbandohientai, khoangcach, iddoituongnhanvatmuctieu)

                        if idbandohientaidoituongbaothu == idbandohientai:
                            dsbaothutrieuhoi.append((iddoituongbaothu, toadodoituongbaothu, khoangcach))

                    elif is_baothugiangho:
                        if self._is_tudongsudungkynangbaothu:
                            self._hoiphucbaothugiangho(sothutu, iddoituongbaothu)
                        if not self._is_tudongsudungkynangbaothu:
                            # Tắt Tự động kỹ năng bảo thú giang hồ: ở bản đồ không PK cho nó Chờ đợi như cũ
                            if self.moitruong.get_idbandohientai() in BANDOKHONGPKs and self.moitruong.get_trangthaihanhvidoituongbaothu(sothutu) != 3:
                                self.moitruong.action_ralenhbaothudungim(iddoituongbaothu, delay = 0.)
                        else:
                            # Bật Tự động sử dụng kỹ năng bảo thú giang hồ thì luôn kéo nó theo như bảo thú triệu hồi, kể cả bản đồ không PK
                            # (người dùng 2026-11-26): gọi về khi xa / khác bản đồ, theo sau sát cạnh; không ra lệnh tấn công (Bị động,
                            # chỉ dùng Thiên Cân lên người chơi). Trước đây nhánh Chờ đợi ở bản đồ không PK chạy trước nên ở Chu bảo thú
                            # bị đổi qua lại Chờ đợi <-> Theo sau mỗi lượt (Chờ đợi ghi +0x1E0 = 3, lượt sau kéo theo ghi 2, lại Chờ đợi...)
                            self._keobaothutheo(iddoituongbaothu, idbandohientaidoituongbaothu == idbandohientai, khoangcach, 0)
                            if idbandohientaidoituongbaothu == idbandohientai:
                                dsbaothutrieuhoi.append((iddoituongbaothu, toadodoituongbaothu, khoangcach))

                            idkynangbaothu_map = {self.moitruong.get_idkynangbaothugiangho(i): i for i in range(11)}
                            idkynangbaothucothesudungs = {KYNANGBAOTHU_CAOCAPTHIENCAN, }
                            if set(idkynangbaothu_map.keys()) & idkynangbaothucothesudungs:
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

    def _hoiphucbaothugiangho(self, sothutu, iddoituongbaothu):
        # Cho bảo thú giang hồ đang triệu hồi ăn Lão Tửu (nội lực thấp) / Dưa hấu (khí huyết thiếu nhiều) ở mọi bản đồ, không cần kỹ
        # năng Cao Cấp Thiên Cân, khi bật Tự động sử dụng kỹ năng bảo thú giang hồ (người dùng 2026-11-26; trước đây chỉ con có
        # Thiên Cân, bản đồ PK, mỗi 5s).
        # Đang có hiệu ứng hồi (Lão Tửu 9156 "Mỗi 2 giây phục hồi pháp lực.", Dưa hấu 9154 "... khí huyết.") thì thôi. Sau mỗi lần
        # cho ăn chờ CHOHIEUUNGHOIPHUCBAOTHU giây cho hiệu ứng kịp hiện (không thấy bảo thú trong tầm nhìn thì coi như chưa có)
        diachibaothu = self.moitruong._get_diachidoituongbaothu(sothutu)
        bang = (
            (LAOTUU, HIEUUNG_HOIPHAPLUCBAOTHU, "_thoidiemchoanlaotuu",
             lambda: self.moitruong.get_noilucconlaibaothugiangho() <= max(NOILUCBAOTHUCHOANLAOTUU,
                                                                          self.moitruong.get_noiluctoidabaothugiangho() * PHANTRAMNOILUCBAOTHUCHOANLAOTUU / 100.)),
            (DUAHAU, HIEUUNG_HOIKHIHUYETBAOTHU, "_thoidiemchoanduahau",
             lambda: self.moitruong.get_sinhluctoidabaothugiangho() - self.moitruong.get_sinhlucconlaibaothugiangho() >= SINHLUCTHIEUBAOTHUCHOANDUAHAU),
        )
        for tenvatpham, idhieuung, thuoctinh, is_can in bang:
            if time.time() - getattr(self, thuoctinh) < CHOHIEUUNGHOIPHUCBAOTHU or not is_can():
                continue
            if diachibaothu and self.moitruong.get_is_cohieuungs((idhieuung,), macdinh = False, diachicosothongtinnhanvat = diachibaothu):
                continue
            iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(tenvatpham)
            setattr(self, thuoctinh, time.time())
            if not iddoituongvatpham:
                # Hết món thì 60s sau mới tìm lại (khỏi cảnh báo mỗi 1.5s)
                setattr(self, thuoctinh, time.time() + 60.)
                if tenvatpham == LAOTUU:
                    canhbao(self.moitruong, "Hết lão tửu")
                    baosuco(self.moitruong, "vatpham", "Hết Lão Tửu cho bảo thú", giancach = 1800.)
                continue
            if self.moitruong.action_sudungvatphambaothu(iddoituongvatpham, iddoituongbaothu, delay = 0.):
                self.moitruong._inlog(f"[BẢO THÚ] Cho {self.moitruong.get_tendoituongbaothugiangho()} ăn {tenvatpham}: nội lực "
                                      f"{self.moitruong.get_noilucconlaibaothugiangho()}/{self.moitruong.get_noiluctoidabaothugiangho()}, khí huyết "
                                      f"{self.moitruong.get_sinhlucconlaibaothugiangho()}/{self.moitruong.get_sinhluctoidabaothugiangho()}"
                                      f"{'' if diachibaothu else ' (ngoài tầm nhìn, không đọc được hiệu ứng)'}")

    def _thuhoibaothugianghomauthap(self, iddoituongbaothugiangho):
        # Bảo thú giang hồ dưới _phantramsinhlucthuhoibaothugiangho % khí huyết thì cất đi (người dùng 2026-11-26), 0 = tắt
        nguong = self._phantramsinhlucthuhoibaothugiangho
        if nguong <= 0 or time.time() - self._thoidiemthuhoibaothugiangho < 2.:
            return False
        phantram = self.moitruong.get_phantramsinhlucconlaibaothugiangho()
        if not self.moitruong.get_sinhluctoidabaothugiangho() or phantram >= nguong:
            return False
        self._thoidiemthuhoibaothugiangho = time.time()
        if not self.moitruong.action_thuhoibaothu(iddoituongbaothugiangho):
            return False
        self._idbaothudanggoive.discard(iddoituongbaothugiangho)
        self.moitruong._inlog(f"[BẢO THÚ] Thu hồi {self.moitruong.get_tendoituongbaothugiangho()}: khí huyết {phantram:.0f}% < {nguong:.0f}%")
        return True

    def _is_chotrieuhoilaibaothugiangho(self):
        # Vừa thu hồi vì máu thấp: chưa triệu hồi lại tới khi máu đủ ngưỡng hoặc quá THOIGIANCHOTRIEUHOILAIBAOTHU giây
        if not self._thoidiemthuhoibaothugiangho or time.time() - self._thoidiemthuhoibaothugiangho > THOIGIANCHOTRIEUHOILAIBAOTHU:
            return False
        return self.moitruong.get_phantramsinhlucconlaibaothugiangho() < self._phantramsinhlucthuhoibaothugiangho

    def _epbaothubidong(self, sothutu, iddoituongbaothu):
        # Mọi bảo thú (giang hồ, triệu hồi, vật phẩm) giữ hình thức Bị động: Tấn công / Phòng thủ thì bị đánh là tự phản kích,
        # đuổi theo quái đi xa (người dùng 2026-11-26). Bị động vẫn đánh theo lệnh tấn công của bot. Ô +0x1DC khác Bị động
        # (mới gọi ra, người chơi bấm đổi) thì gửi "pet <id># mode 0", mỗi con tối đa mỗi GIANCACHTHIETLAPHINHTHUCBAOTHU giây.
        # Chỉ chạy khi tích ô "Ép bảo thú ... Bị động" (_is_epbaothubidong, mặc định tắt)
        hinhthuc = self.moitruong.get_hinhthucdoituongbaothu(sothutu)
        if hinhthuc is None or hinhthuc is False or hinhthuc == HINHTHUCBAOTHU_BIDONG:
            return
        if time.time() - self._thoidiembaothubidong_map.get(iddoituongbaothu, 0.) < GIANCACHTHIETLAPHINHTHUCBAOTHU:
            return
        if len(self._thoidiembaothubidong_map) > 64:
            self._thoidiembaothubidong_map.clear()
        self._thoidiembaothubidong_map[iddoituongbaothu] = time.time()
        if self.moitruong.action_thietlaphinhthucbaothu(sothutu, iddoituongbaothu, HINHTHUCBAOTHU_BIDONG):
            self.moitruong._inlog(f"[BẢO THÚ] {self.moitruong.get_tendoituongbaothu(sothutu)} hình thức {hinhthuc} -> Bị động")

    def _keobaothutheo(self, iddoituongbaothu, is_cungbando, khoangcach, iddoituongnhanvatmuctieu):
        # Gọi về khi bảo thú khác bản đồ hoặc ra xa quá KHOANGCACHGOIBAOTHUVE; đã gọi thì gọi tới khi về gần
        # KHOANGCACHBAOTHUDAVE mới thôi (không thì vừa về tới mép lại bị lệnh tấn công kéo đi xa tiếp)
        if not is_cungbando or khoangcach > KHOANGCACHGOIBAOTHUVE:
            self._idbaothudanggoive.add(iddoituongbaothu)
        elif khoangcach <= KHOANGCACHBAOTHUDAVE:
            self._idbaothudanggoive.discard(iddoituongbaothu)

        if self._is_danggomquai:
            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu)
        elif iddoituongbaothu in self._idbaothudanggoive:
            # Gọi đều mỗi THOIGIANGOIBAOTHUVE giây tới khi về gần (mỗi lệnh chưa đủ xa để phù về chỉ chạy thêm một đoạn)
            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu, delay = THOIGIANGOIBAOTHUVE)
        elif iddoituongnhanvatmuctieu:
            self.moitruong.action_ralenhbaothutancong(iddoituongbaothu, iddoituongnhanvatmuctieu)
        elif not (self.moitruong.get_is_baothudangtheosau(iddoituongbaothu) and is_cungbando and khoangcach <= KHOANGCACHBAOTHUDANEO):
            # Không có mục tiêu: trước đây không ra lệnh gì nên bảo thú cứ đuổi theo quái cũ/đứng im trong khi nhân vật đi chỗ khác.
            # Kéo về sát cạnh thường xuyên (người dùng 2026-11-19): trước đây theo sau trong 9 ô là thôi gọi, nó tụt lại sau góc
            # vách rồi kẹt. Mỗi lệnh Theo sau nó tìm lại đường một đoạn => gọi lại mỗi 1s tới khi về trong KHOANGCACHBAOTHUDANEO ô
            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu, delay = 1.)

    def _capnhatbaothutheosau(self, dsbaothu):
        # Bỏ quay lại đón bảo thú (người dùng 2026-11-20). Thay bằng: báo cho tầng di chuyển (moitruong) toạ độ bảo thú gần để A* chọn
        # đường thoáng / lùi chỗ còn thấy nó (toadoneobaothu), và con đang Theo sau / bị gọi về gần nhất (baothutheosaugan) để lúc đi
        # vòng góc vách thì dừng ở chỗ nó còn thấy mình, gọi nó theo kịp rồi mới rẽ (moitruong._catduongchobaothu): nó chạy thẳng về
        # mình không vướng vách
        trongtam = [b for b in dsbaothu if b[2] <= KHOANGCACHGOIBAOTHUVE] if not self.moitruong.get_is_nhanvatdachet() else []
        self.moitruong.toadoneobaothu = min(trongtam, key = lambda b: b[2])[1] if trongtam else None
        theosau = [b for b in trongtam if self.moitruong.get_is_baothudangtheosau(b[0]) or b[0] in self._idbaothudanggoive]
        self.moitruong.baothutheosaugan = min(theosau, key = lambda b: b[2]) if theosau else None
