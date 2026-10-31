# Phần vật phẩm: dùng thuốc / vật phẩm, nhặt, vứt, mua, sửa, sắp xếp / xếp chồng hành trang, bán rác, về bán rác.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import re
import time
import unicodedata

from hangso_xq import *
from luattuido_xq import tailuat, timluat, timluatbao, timluatcatkho, HANHDONG_BAN, HANHDONG_VUT, CHIKHI_TRIEUHOIBAOTHU
from thongbao_xq import baosuco, LYDOTAMNGUNGTUXA
from moitruong_xq import MoiTruong, DOUUTIEN_THAP, DOUUTIEN_KHANCAP, DOUUTIEN_CAO, SOLUONGDOITUONGXUNGQUANHTOIDA, tinh_is_huongmatvediem
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam
from tienich_xq import laynhomtodoitudongs, laynhanvattodoitudongs, donbangthoidiem

# Mua bù: cửa hàng chưa biết hàng thì mở để đọc (tactu_sumon_xq.batdau_mocuahang), mở hỏng thì chừng này giây sau mới thử lại
GIANCACHMOCUAHANGMUABU = 120.


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
                phatam("{} đã hết hạn sử dụng".format(tenvatpham), is_block = False)
                baosuco(self.moitruong, "vatpham", f"{tenvatpham} đã hết hạn sử dụng", giancach = 3600.)
            return None
        return vitri, tenvatpham

    def action_tudongsudungvatpham(self):
        if self._is_tudongsudungvatpham:
            if self.moitruong.get_is_nhanvatdachet():
                return

            # Đọc tên hành trang 1 lần mỗi lượt để kiểm tra có vật phẩm hay không (trước đây mỗi vật phẩm quét lại cả hành trang,
            # vật phẩm không có thì lượt nào cũng quét vì mốc thời gian chỉ cập nhật khi dùng được). Dùng thì vẫn tìm lại id mới nhất
            tenvatphamhanhtrangs = set(self.moitruong.get_danhsachtenvatphamhanhtrang())
            co = tenvatphamhanhtrangs.__contains__

            lichsutrochuyen5s = self.moitruong.get_lichsutrochuyen5s()

            if self._trangthaitrieuhoibaothuvatpham != 3:
                is_doilenh = False
                is_hanhdong = False
                for _, noidungtrochuyen in lichsutrochuyen5s:
                    if "Đợi lệnh" in noidungtrochuyen:
                        is_doilenh = True
                    if "Hành động" in noidungtrochuyen:
                        is_hanhdong = True

                    # Đang kiểm tra (gửi pf 4131.@ đúng 1 lần) thì chỉ cần thấy 1 trong 2 dòng là đã có bảo thú
                    is_datrieuhoi = (is_doilenh or is_hanhdong) if self._trangthaitrieuhoibaothuvatpham == 4 else (is_doilenh and is_hanhdong)
                    if is_datrieuhoi:
                        if IS_LOGCAULENH: print(f"[TRIỆU HỒI BẢO THÚ] trạng thái {self._trangthaitrieuhoibaothuvatpham} -> 3: đã triệu hồi xong, mở khoá kỹ năng")
                        self._trangthaitrieuhoibaothuvatpham = 3
                        self.moitruong.action_mokhoakynang()

                        danhhieu = DANHHIEU_MAP[self.moitruong.get_idnguoichoi()]
                        if danhhieu:
                            self.moitruong.action_thucthicaulenh("title show {}".format(danhhieu), douutien = DOUUTIEN_KHANCAP)

                        break

            if self._trangthaitrieuhoibaothuvatpham == 0:
                # Trước khi dùng vật phẩm: gửi pf 4131.@ xem bảo thú vật phẩm đã triệu hồi chưa (có thì hiện "Đợi lệnh"/"Hành động")
                if time.time() - self._thoidiemsudungbaothuvatphamgannhat > 3.0 and self._get_baothuvatphamocuoi():
                    if IS_LOGCAULENH: print("[TRIỆU HỒI BẢO THÚ] trạng thái 0 -> 4: gửi pf 4131.@ kiểm tra đã triệu hồi chưa")
                    self.moitruong.xoalichsutrochuyen()
                    self.moitruong.action_khoakynang(1.5)
                    self.moitruong.action_thucthicaulenh("pf 4131.@", douutien = DOUUTIEN_KHANCAP)
                    self._trangthaitrieuhoibaothuvatpham = 4
                    self._thoidiemchuyentrangthaitrieuhoibaothuvatpham = time.time()

            elif self._trangthaitrieuhoibaothuvatpham == 4:
                if time.time() - self._thoidiemchuyentrangthaitrieuhoibaothuvatpham > 1.5:
                    # Không thấy "Đợi lệnh"/"Hành động" => chưa có bảo thú, giờ mới dùng vật phẩm
                    if IS_LOGCAULENH: print("[TRIỆU HỒI BẢO THÚ] trạng thái 4 -> dùng vật phẩm: chưa có bảo thú")
                    self.moitruong.action_mokhoakynang()
                    # Dùng không được vật phẩm nào thì về trạng thái 0, 3s sau kiểm tra lại
                    self._trangthaitrieuhoibaothuvatpham = 0
                    self._thoidiemsudungbaothuvatphamgannhat = time.time()
                    baothuvatphamocuoi = self._get_baothuvatphamocuoi()
                    if baothuvatphamocuoi and self.action_sudungvatphamhanhtrangtaivitri(*baothuvatphamocuoi, delay = 0.):
                        if IS_LOGCAULENH: print(f"[TRIỆU HỒI BẢO THÚ] trạng thái 4 -> 1: đã dùng {baothuvatphamocuoi[1]}, chờ 1s rồi spam pf 4131.@")
                        self._thoidiemtamngungsudungkynang = max(self._thoidiemtamngungsudungkynang, time.time() + 0.5)
                        self._thoidiemsudungbaothuvatphamgannhat = time.time()

                        self._trangthaitrieuhoibaothuvatpham = 1
                        self._thoidiemchuyentrangthaitrieuhoibaothuvatpham = time.time()
                        self.moitruong.xoalichsutrochuyen()

            elif self._trangthaitrieuhoibaothuvatpham == 1:
                if time.time() - self._thoidiemchuyentrangthaitrieuhoibaothuvatpham > 1.0:
                    # Lệnh triệu hồi cũng là spam kỹ năng: khoá mọi kỹ năng khác suốt lúc spam (mở lại khi xong hoặc hết 3s)
                    if IS_LOGCAULENH: print("[TRIỆU HỒI BẢO THÚ] trạng thái 1 -> 2: bắt đầu spam pf 4131.@, khoá kỹ năng")
                    self.moitruong.action_khoakynang(1.5)
                    self.moitruong.action_thucthicaulenh("pf 4131.@", douutien = DOUUTIEN_KHANCAP)

                    self._trangthaitrieuhoibaothuvatpham = 2
                    self._thoidiemchuyentrangthaitrieuhoibaothuvatpham = time.time()
                    self._thoidiemyeucaubaothuvatphamdoilenh = time.time()

            elif self._trangthaitrieuhoibaothuvatpham == 2:
                thoigianchochuyentrangthaitrieuhoibaothuvatpham = time.time() - self._thoidiemchuyentrangthaitrieuhoibaothuvatpham
                self.moitruong.action_khoakynang(1.5)

                if time.time() - self._thoidiemyeucaubaothuvatphamdoilenh > 0.25:
                    self.moitruong.action_thucthicaulenh("pf 4131.@", douutien = DOUUTIEN_KHANCAP)
                    self._thoidiemyeucaubaothuvatphamdoilenh = time.time()

                if thoigianchochuyentrangthaitrieuhoibaothuvatpham > 3.:
                    # Không thấy "Đợi lệnh"/"Hành động" => coi như thất bại. Trước đây 3s sau là dùng vật phẩm + spam lại,
                    # quay vòng mãi nên kỹ năng bị khoá gần như liên tục; giờ chờ 30s mới thử lại
                    if IS_LOGCAULENH: print("[TRIỆU HỒI BẢO THÚ] trạng thái 2 -> 0: spam 3s không thấy 'Đợi lệnh'/'Hành động', mở khoá kỹ năng, 30s sau thử lại")
                    self._trangthaitrieuhoibaothuvatpham = 0
                    self._thoidiemsudungbaothuvatphamgannhat = time.time() + 27.
                    self.moitruong.action_mokhoakynang()

            idbandohientai = self.moitruong.get_idbandohientai()
            is_bandokhongpk = idbandohientai in BANDOKHONGPKs
            is_bandopk = not is_bandokhongpk
            is_dangbatpk = self.moitruong.get_idmaupk() != MAUPK_HOABINH
            tenmonphai = self.moitruong.get_tenmonphai()

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
            phantramnoilucconlai = self.moitruong.get_phantramnoilucconlai()
            noilucmatdi = self.moitruong.get_noiluctoida() - self.moitruong.get_noilucconlai()
            if time.time() - self._thoidiemkiemtrahieuunggannhat > 2.5:
                self._thoidiemkiemtrahieuunggannhat = time.time()

                if is_bandopk and phantramnoilucconlai < 50. and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHAPLUCTHACH,), True, is_hieuungcoloi = 1):
                    if co(TIEUPHAPLUCTHACH):
                        self.action_sudungvatphamhanhtrang(TIEUPHAPLUCTHACH)

                # Máu dưới 25% (Mao Sơn 50%) thì dùng Tiểu Huyết Thạch ở mọi bản đồ, mọi môn phái, không cần bật PK hay tự động khai khoáng
                nguongmauhuyetthach = 50. if tenmonphai == "maoson" else 25.
                if ((is_bandopk and (is_dangbatpk or self._is_tudongkhaikhoang) and phantramsinhlucconlai < 75.) or phantramsinhlucconlai < nguongmauhuyetthach) \
                        and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HUYETTHACH,), True, is_hieuungcoloi = 1):
                    # Khai khoáng ở Hư Lăng Động: Đại Huyết Thạch trước, hết mới Tiểu Huyết Thạch
                    huyetthachs = [DAIHUYETTHACH, TIEUHUYETTHACH] if self._is_tudongkhaikhoang and idbandohientai == BANDO_HULANGDONG else [TIEUHUYETTHACH]
                    for huyetthach in huyetthachs:
                        if co(huyetthach):
                            self.action_sudungvatphamhanhtrang(huyetthach)
                            break

                if is_dangbatpk and is_bandopk:
                    if tenmonphai == "daohoanguyen" and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIENNGUYENDON,), macdinh = True, is_hieuungcoloi = 1):
                        if co(THIENNGUYENDON):
                            self.action_sudungvatphamhanhtrang(THIENNGUYENDON, delay = 0.)
                    if co(NGANHANHTU) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANHANHTU,), macdinh = True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(NGANHANHTU, delay = 0.)
                    if co(XALOITU) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_XALOITU,), macdinh = True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(XALOITU, delay = 0.)

            if self.moitruong.get_diempk() > 0:
                if co(ANXAPHU):
                    self.action_sudungvatphamhanhtrang(ANXAPHU, is_boquaxacnhan = True, delay = 0.)

            # Máu thấp: lưu tên pháp bảo đang đeo (đọc ô trang bị, không dò hành trang) rồi đổi sang pháp bảo không hư hỏng;
            # máu hồi lại (cao hơn lúc đổi 15%) thì tìm pháp bảo cũ trong hành trang đeo lại, xác nhận bằng cách đọc lại ô trang bị
            tenphapbaohientai = self.moitruong.get_tenphapbaohientai()
            # Vừa ra lệnh đổi: game chưa kịp cập nhật ô trang bị thì chưa xét, tránh tưởng đã đeo lại / người chơi tự đổi
            is_dangchodoiphapbao = time.time() - self._thoidiemhoandoiphapbao < 2.

            if self._tenphapbaocu is not None and not is_dangchodoiphapbao:
                if self._tenphapbaocu and tenphapbaohientai == self._tenphapbaocu:
                    print("{}: đã đeo lại pháp bảo {}".format(self.moitruong.get_tendoituong(), self._tenphapbaocu))
                    self._tenphapbaocu = None
                elif tenphapbaohientai not in PHAPBAOKHONGHUHONGs:
                    # Không còn đeo pháp bảo không hư hỏng (người chơi tự đổi / tháo): thôi không đeo lại
                    print("{}: pháp bảo đang đeo là {}, bỏ đeo lại {}".format(self.moitruong.get_tendoituong(), tenphapbaohientai or "(không)", self._tenphapbaocu))
                    self._tenphapbaocu = None
                elif phantramsinhlucconlai >= self._mucsinhluckhihoandoi + 15 and time.time() - self._thoidiemthumaclaiphapbao > 2.:
                    if not self._tenphapbaocu:
                        # Trước đó không đeo pháp bảo nào: không có gì để đeo lại
                        self._tenphapbaocu = None
                    else:
                        vitriphapbaocu = self.moitruong.action_timkiemvitrivatphamhanhtrang(self._tenphapbaocu)
                        if vitriphapbaocu is not False and self.action_sudungvatphamhanhtrangtaivitri(vitriphapbaocu, self._tenphapbaocu, delay = 0.):
                            self._thoidiemthumaclaiphapbao = time.time()
                            self._thoidiemhoandoiphapbao = time.time()

            if ((phantramsinhlucconlai <= 25 and idbandohientai not in (BANDO_CHIENTRUONG, BANDO_COMO, BANDO_TIVO, *BANDOKHONGPKs)) or (phantramsinhlucconlai < 15 and idbandohientai == BANDO_COMO)) \
                    and not is_dangchodoiphapbao and tenphapbaohientai not in PHAPBAOKHONGHUHONGs:
                for phapbaokhonghuhong in PHAPBAOKHONGHUHONGs:
                    if not co(phapbaokhonghuhong):
                        continue
                    if self.action_sudungvatphamhanhtrang(phapbaokhonghuhong, delay = 0.):
                        self._thoidiemhoandoiphapbao = time.time()
                        # Đổi lại lần nữa khi chưa kịp đeo lại pháp bảo cũ: vẫn giữ tên pháp bảo cũ ban đầu
                        if self._tenphapbaocu is None:
                            self._tenphapbaocu = tenphapbaohientai
                            self._mucsinhluckhihoandoi = phantramsinhlucconlai
                            print("{}: máu {}%, lưu pháp bảo đang đeo: {} -> đổi sang {}".format(
                                self.moitruong.get_tendoituong(), phantramsinhlucconlai, tenphapbaohientai or "(không)", phapbaokhonghuhong))
                    break

            # Hồi sinh lực/nội lực: chưa mất đủ nhiều mà dùng thuốc thì phí => ngoài phần trăm còn phải mất quá 2500 sinh lực / 3000 nội lực.
            # Đang PK ở bản đồ PK: dưới 75%; ở phó bản (không PK): dưới 25%
            is_hoiphucpk = is_dangbatpk and is_bandopk
            is_hoiphucphoban = not is_hoiphucpk and idbandohientai in BANDOPHOBANs
            nguongphantramhoiphuc = 75 if is_hoiphucpk else 35
            sinhlucmatdi = self.moitruong.get_sinhluctoida() - self.moitruong.get_sinhlucconlai()

            # Vật phẩm hồi ngay dùng chung thời gian hồi theo nhóm: chỉ gửi lệnh khi client báo đã hồi xong (_sudungvatphamhoi).
            # Lệnh không phải lúc nào cũng thành công: gửi rồi mà vẫn chưa vào hồi thì THOIGIANCHOXACNHANHOIVATPHAM giây sau gửi lại
            if time.time() - self._thoidiemsudungvatphamhoisinhlucgannhat > THOIGIANCHOXACNHANHOIVATPHAM:
                hoisinhlucs = []
                # Phó bản thì không cần bật tự động kỹ năng
                if (is_hoiphucpk and self._is_tudongsudungkynang) or is_hoiphucphoban:
                    if phantramsinhlucconlai < nguongphantramhoiphuc and sinhlucmatdi > 2500:
                        hoisinhlucs = [TRIDUOC, THILUYENQUA, THILUYENDON, CAPCUUDON, HOATLACHOAN, ]
                        # Phó bản không PK: dùng theo thứ tự ngược lại (cả sinh lực và nội lực)
                        if is_hoiphucphoban:
                            hoisinhlucs.reverse()
                elif self._is_tudongsudungkynang and phantramsinhlucconlai <= 75:
                    hoisinhlucs = [HOATLACHOAN, ]
                if self._sudungvatphamhoi(hoisinhlucs, co):
                    self._thoidiemsudungvatphamhoisinhlucgannhat = time.time()

            if self._is_tudongsudungkynang and time.time() - self._thoidiemsudungvatphamhoinoilucgannhat > THOIGIANCHOXACNHANHOIVATPHAM:
                hoinoilucs = []
                if is_hoiphucpk or is_hoiphucphoban:
                    if phantramnoilucconlai < nguongphantramhoiphuc and noilucmatdi > 3000:
                        hoinoilucs = [PHUCDUOC, LONGTIENTHAO, THILUYENDON, HOATTAMDON, ANTHANHOAN, ]
                        if is_hoiphucphoban:
                            hoinoilucs.reverse()
                elif phantramnoilucconlai <= 75:
                    hoinoilucs = [ANTHANHOAN, ]
                if self._sudungvatphamhoi(hoinoilucs, co):
                    self._thoidiemsudungvatphamhoinoilucgannhat = time.time()

            if is_dangbatpk and is_bandopk and self._is_tudongsudungkynang and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCCOT, HIEUUNGKYNANG_THUCGIAP, HIEUUNGKYNANG_THIEUDOT, HIEUUNGKYNANG_THAUCOTDINH, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN), macdinh = False, is_hieuungcoloi = 0) and time.time() - self._thoidiemsudungthanhtamdangannhat > THOIGIANCHOXACNHANHOIVATPHAM:
                # Khu Ma Tán trước, hết (hoặc đang hồi) thì Thanh Tâm Đơn (tác dụng tương tự)
                if self._sudungvatphamhoi([KHUMATAN, THANHTAMDON, ], co):
                    self._thoidiemsudungthanhtamdangannhat = time.time()

            if self.moitruong.get_idnguoichoi() == 59844:
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Luyện Đơn",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if co(sachcanhoc) and self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

            if self.moitruong.get_idnguoichoi() in (59844, 59845):
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Thái Cổ Thần Quy",
                        "Nhập môn Quyền Cước Chi",
                        "Nhập môn Kim Cương Bất H",
                        "Nhập môn Chu Thiên Vận Ch",
                        "Nhập môn Thái Cổ Thần Q",
                        "Nhập môn Hộ Thể Kim Cang",
                        "Nhập môn Kinh Lạc Học Th",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if co(sachcanhoc) and self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

                # if time.time() - self._thoidiemsudungtusamdongannhat > 30.:
                #     if self.action_sudungvatphamhanhtrang(TUSAMDON, delay = 0.0):
                #         self._thoidiemsudungtusamdongannhat = time.time()

            if self.moitruong.get_idnguoichoi() == 59996:
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Y Thuật",
                        "Nhập môn Trung Y Dược Lý",
                        "Nhập môn Tu Tâm",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if co(sachcanhoc) and self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

            if self.moitruong.get_idnguoichoi() == 60055:
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Tụng Kinh",
                        "Nhập môn Nghịch Thiên Ph",
                        "Nhập môn Cơ Quan",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if co(sachcanhoc) and self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

            if self.moitruong.get_thelucconlai() <= 5:
                if time.time() - self._thoidiemsudungbattiendongannhat > 30.:
                    if co(BATTIENDON) and self.action_sudungvatphamhanhtrang(BATTIENDON):
                        self._thoidiemsudungbattiendongannhat = time.time()

    def _sudungvatphamhoi(self, tenvatphams, co):
        # Dùng món đầu tiên còn trong hành trang mà client báo đã hết thời gian hồi; True nếu đã gửi được lệnh dùng
        tenvatphams = [ten for ten in tenvatphams if co(ten)]
        if not tenvatphams:
            return False
        thoigianhois = self.moitruong.get_thoigianhoiconlaivatphams(tenvatphams)
        for ten in tenvatphams:
            if thoigianhois[ten] <= 0 and self.action_sudungvatphamhanhtrang(ten, delay = 0.):
                return True
        # Tất cả đang hồi nhưng sẽ xong trước vòng lặp kế tiếp: chờ tới đúng lúc hồi xong rồi dùng ngay, không trễ thêm 1 vòng
        conlai = min(thoigianhois.values())
        if 0 < conlai <= THOIGIANCHOHOIXONGTOIDA:
            time.sleep(conlai + 0.02)
            ten = next(ten for ten in tenvatphams if thoigianhois[ten] <= conlai)
            return self.action_sudungvatphamhanhtrang(ten, delay = 0.)
        return False

    def action_tudongmuaauto(self):
        # Mua auto trong game (phím tắt Ctrl+Alt+Shift+Y)
        if time.time() - self._thoidiemmuaautogannhat < 5.:
            return
        self._thoidiemmuaautogannhat = time.time()
        self.moitruong.action_thucthicaulenh("auto buy 5 10")

    def action_tudongvutvatpham(self):
        if time.time() - self._thoidiemvutvatphamgannhat < 1.:
            return

        if not self._is_tudongkhaikhoang:
            return

        if self.moitruong.get_idbandohientai() in BANDOHAIDUOCs:
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

        vatphamtudongnhats = VATPHAMTUDONGNHATs
        if self._is_tudongvebanrac:
            vatphamtudongnhats = (*vatphamtudongnhats,
                                  TIENTE, "Tơ Nhện", "Kịch Độc Châm", "Đuôi Bọ Cạp", "Ly Hồn", "Ly Phách", "Ma Tinh thạch", "Trái Táo", "Trái lê", "Phá Bố Y", "Toái Lăng", "Tơ Tằm", "Da Rắn", "Ống Tên", "Bao Kiếm", "Cán Đao", "Toái Sa", "Hồng Sắc Tiểu Thạch", "Mạng Nhện", "Tử Giả Di Vật", "Phi Hành Phiến", "Núm Vú", "Hành Quân Tán"
                                  )

        def kiemtradieukiennhat(tenvatphamkiemtra, diachikiemtra):
            if tenvatphamkiemtra in VATPHAMKHONGNHATs:
                return False
            if tenvatphamkiemtra in VATPHAMUUTIENNHATs:
                return True
            # Vật phẩm nhiệm vụ Thu thập của sư môn
            if tenvatphamkiemtra in self._layvatphamnhatsumon():
                return True
            if is_chinhatvatphamuutien:
                return False
            if tenvatphamkiemtra in vatphamtudongnhats:
                return True
            if VATPHAMTUDONGNHATFARMs and self._is_tudongvebanrac and any(x in tenvatphamkiemtra for x in VATPHAMTUDONGNHATFARMs):
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
                danhsachvatpham.append((tenvatpham not in VATPHAMUUTIENNHATs, khoangcach, diachivatpham))

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
            is_vatphamuutien = tenvatphamdangnhat in VATPHAMUUTIENNHATs or tenvatphamdangnhat in self._layvatphamnhatsumon()
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

        elif self._is_tudongvebanrac and not is_chinhatvatphamuutien and not is_covatphamvungcamgan:
            self.moitruong.action_nhatvatphamxungquanh(delay = 0.5)

        self._yeucaunhatvatpham = yeucaunhatvatphammoi

    def action_tudongmuavatpham(self, delay = 3.):
        if self._is_tudongmuavatpham:
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

            # Món cần mua, NPC, số lượng: luật mua bù (luattuido_xq, tab Túi đồ)
            self._muabutheoluat(nganquy)

    def _muabutheoluat(self, nganquy):
        # Mua bù theo luật túi đồ (luattuido_xq "muabu", lần lượt từ trên xuống): còn ít hơn "duoi" món thì mua cho đủ "muatoi", ở NPC cách
        # không quá 12 ô (NPC tìm theo tên riêng hoặc danh hiệu).
        # Ô / giá tra theo tên món ("tencuahang" nếu có) trong hàng đã đọc của cửa hàng đó (nhiemvu_xq.SoVitri); chưa đọc thì đứng gần
        # mở cửa hàng đọc 1 lần (đóng ngay).
        # Đếm cả các chồng của món đó; vừa mua món nào thì 10s sau mới xét lại món đó (chờ hành trang cập nhật, khỏi mua trùng)
        mucs = [m for m in tailuat()["muabu"] if m["bat"] and m["vatpham"] and m["npc"] and m["muatoi"]]
        if not mucs:
            return
        soluongtheoten = self.moitruong.get_soluongvatphamhanhtrangtheoten()
        if soluongtheoten is None:
            return
        tenmonphai = self.moitruong.get_tenmonphai()
        for muc in mucs:
            if muc["monphai"] and muc["monphai"] != tenmonphai:
                continue
            if muc["chikhi"] == CHIKHI_TRIEUHOIBAOTHU and not self._is_tudongtrieuhoibaothugiangho:
                continue
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

    def _layogiamuabu(self, muc, diachinpc):
        # (ô, giá) để mua món của luật mua bù ở NPC này, None khi chưa biết (đã cho mở cửa hàng đọc nếu được)
        moitruong = self.moitruong
        idbando = moitruong.get_idbandohientai()
        tenmon = muc["tencuahang"] or muc["vatpham"]
        tra = self._sovitri.timhang(idbando, muc["npc"], tenmon)
        if tra:
            return tra
        ketqua = self.get_ketquamocuahang(idbando, muc["npc"])
        if ketqua and ketqua[0]:
            khoa = (idbando, muc["npc"], tenmon)
            if khoa not in self._lechmuabudabao:
                self._lechmuabudabao.add(khoa)
                print(f"[MUA BÙ] {muc['npc']} không bán \"{tenmon}\": sửa tên món / \"Tên ở cửa hàng\" trong luật mua bù")
            return None
        # Chưa đọc cửa hàng này: đứng gần thì mở đọc (mở hỏng thì GIANCACHMOCUAHANGMUABU giây sau mới thử lại)
        khoa = (idbando, muc["npc"])
        if moitruong.get_khoangcach(diachinpc) <= 3. and not self._mocuahang \
                and time.time() - self._lucmocuahangmuabu_map.get(khoa, 0.) > GIANCACHMOCUAHANGMUABU:
            self._lucmocuahangmuabu_map[khoa] = time.time()
            self.batdau_mocuahang(diachinpc)
        return None

    def _layhanhdongluat(self, ten, vitri):
        # Hành động theo luật túi đồ của người dùng (luattuido_xq) cho món ở ô vitri: None = không luật nào khớp (làm như cũ),
        # "chuabiet" = luật cần loại / mô tả mà chưa đọc được (lượt này đừng bán / vứt món đó)
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
        # Món khớp bảng Cất kho: không bán, không vứt (kể cả phần "giữ lại trong túi")
        return bool(self._layluatcatkho(ten, vitri))

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

    def action_sudungvatphamhanhtrang(self, tenvatpham, is_boquaxacnhan = False, delay = 0.25):
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False

        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(tenvatpham)

        if not iddoituongvatpham:
            return False

        print("{}: sử dụng vật phẩm: {}".format(self.moitruong.get_tendoituong(), tenvatpham))

        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham, is_boquaxacnhan, delay = delay)
        if is_ok:
            self._thoidiemsudungvatphamgannhat = time.time()

        return is_ok

    def action_sudungvatphamhanhtrangtaivitri(self, vitri, tenvatpham, is_boquaxacnhan = False, delay = 0.25):
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False

        if vitri is None or vitri < 0 or self.moitruong.get_tenvatphamhanhtrang(vitri) != tenvatpham:
            return False

        iddoituongvatpham = self.moitruong.get_iddoituongvatphamhanhtrang(vitri)

        if not iddoituongvatpham:
            return False

        print("{}: sử dụng vật phẩm: {} tại vị trí {}".format(self.moitruong.get_tendoituong(), tenvatpham, vitri))

        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham, is_boquaxacnhan, delay = delay)
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

        # Loại vật phẩm (_docloaivatpham) của mọi tên đang có: tên chưa biết thì đọc mô tả / desc (mỗi lượt 1 tên)
        tenchuabiet = next((tens[i] for i in cacvitri if ids[i] and tens[i] not in self._loaivatpham_map), None)
        if tenchuabiet is not None:
            self._docloaivatpham(tenchuabiet, next(i for i in cacvitri if ids[i] and tens[i] == tenchuabiet))
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
        # trong nhóm theo loại (Vũ Khí, Nón, Tinh luyện...) rồi tên, món không ghi loại (nguyên liệu...) để sau
        loai = self._loaivatpham_map.get(ten, "")
        nhom = 2 if self._is_thuocsapxep(ten) else 1 if loai == LOAIVATPHAM_COTHESUDUNG else 0
        return nhom, not loai, loai.lower(), ten.lower()

    def _is_dakhongdedo(self, ten):
        # Đá (xem DAKHONGDEDOs): loại ［Tinh luyện］, tên có Đoạn / Linh / Tinh Thạch, hoặc tên có "Thạch" mà chưa biết / không có loại
        tenchuan = self._chuanhoatenvatpham(ten)
        loai = self._loaivatpham_map.get(ten)
        return bool(tenchuan) and (loai in LOAIVATPHAMDAs or any(da in tenchuan for da in DAKHONGDEDOs)
                                   or (not loai and "Thạch" in tenchuan))

    def _docloaivatpham(self, ten, vitri):
        # Ghi _loaivatpham_map[ten] = loại vật phẩm: chữ trong cặp [] / ［］ đầu tiên của mô tả, bỏ qua dòng tên (dòng tên có thể có
        # "(Vật phẩm hiệu ứng [Khoá])"), "" nếu không có (nguyên liệu...). Mô tả lưu theo ô nên chỉ tin khi dòng đầu khớp ten, không
        # thì desc lại; desc không ra thì coi là không có loại (khỏi hỏi lại mãi)
        tenchuan = self._chuanhoatenvatpham(ten)

        def laydongs(mota):
            return [dong.strip() for dong in self._chuanhoatenvatpham(mota).split("\n") if dong.strip()]

        dongs = laydongs(self.moitruong.get_motavatphamhanhtrangcosan(vitri))
        if not dongs or tenchuan not in dongs[0]:
            dongs = laydongs(self.moitruong.get_motavatphamhanhtrang(vitri, is_napmoi = True) or "")
        if not dongs or tenchuan not in dongs[0]:
            print("{}: không đọc được mô tả {}, coi là không có loại khi sắp xếp".format(self.moitruong.get_tendoituong(), tenchuan))
            self._loaivatpham_map[ten] = ""
            return False
        khop = re.search(r"[\[［]\s*([^\]］\n]*?)\s*[\]］]", "\n".join(dongs[1:]))
        self._loaivatpham_map[ten] = khop.group(1) if khop else ""
        # Mô tả (bỏ dòng tên) cho luật túi đồ "mô tả chứa"
        self._motavatpham_map[ten] = "\n".join(dongs[1:])
        return True

    def action_sapxephanhtrang(self, delay = 0.6, thoigiantoida = 180., solandichuyentoida = 300):
        if not self._is_dangsapxephanhtrang:
            return

        if time.time() - self._thoidiembatdausapxephanhtrang > thoigiantoida or self._solandichuyensapxep >= solandichuyentoida:
            self._ketthucsapxephanhtrang("Sắp xếp hành trang quá lâu, dừng lại")
            return

        if time.time() - self._thoidiemsapxephanhtranggannhat < delay:
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
        if kieu == "tui":
            is_ok = self.moitruong.action_dichuyenvatphamsanghanhtrangkhac(iddoituong, dich, delay = 0.)
        else:
            is_ok = self.moitruong.action_dichuyenvatphamhanhtrang(iddoituong, dich + 1, delay = 0.)
        if is_ok:
            self._thoidiemsapxephanhtranggannhat = time.time()
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
                    phatam("Không chuyển được vật phẩm ở ô cuối hành trang 1")
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
                phatam("Các hành trang khác đã đầy, không chuyển được ô cuối hành trang 1")
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
        for i in range(6, soluongvatphamhanhtrangtoida):
            iddoituongvatphamhanhtrang = self.moitruong.get_iddoituongvatphamhanhtrang(i)
            if not iddoituongvatphamhanhtrang or iddoituongvatphamhanhtrang <= 0:
                continue

            tenvatphamhanhtrang = self.moitruong.get_tenvatphamhanhtrang(i)
            # Tên chưa đọc được (đang tải...) thì không khớp luật Giữ nào, đừng bán nhầm
            if not tenvatphamhanhtrang:
                continue
            # Theo luật túi đồ (luattuido_xq, tab Túi đồ): không khớp luật nào hoặc luật Bán thì bán; Giữ / Vứt / Cất kho / chưa đọc được
            # mô tả (luật có điều kiện loại / mô tả) thì không bán
            hanhdong = self._layhanhdongluat(tenvatphamhanhtrang, i)
            # Món khớp luật Cất kho (dù luật đứng dưới luật Bán) thì để dành đi cất, không bán
            if hanhdong in (None, HANHDONG_BAN) and not self._is_catkhovatpham(tenvatphamhanhtrang, i):
                hangdoi.append("sell ! {}# {}# 30".format(hex(idnpc).replace("0x", ""), hex(iddoituongvatphamhanhtrang).replace("0x", "")))
        self._hangdoibanrac = hangdoi
        self._thoidiemguibanractieptheo = 0.

    def get_is_dangbanrac(self):
        return bool(self._hangdoibanrac)

    def get_is_dangsuavatpham(self):
        return bool(self._thoidiemhetsuavatpham)

    def action_xulybanracvasuado(self):
        # Gọi mỗi lượt loop phụ: gửi lệnh bán kế tiếp (cách nhau 1s), và đi tìm/sửa đồ nếu đang có việc sửa
        thoidiemhientai = time.time()
        if self._hangdoibanrac and thoidiemhientai >= self._thoidiemguibanractieptheo:
            self.moitruong.action_thucthicaulenh(self._hangdoibanrac.pop(0), douutien = DOUUTIEN_THAP)
            self._thoidiemguibanractieptheo = thoidiemhientai + 1.

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
        if self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
            if not diachinpc:
                self.moitruong.action_dichuyengiukhoangcachtoidadiem(111, 157, khoangcachtoida = 3.)
            else:
                self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 3.)
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
        if not self._is_tudongvebanrac:
            return

        tenmonphai = self.moitruong.get_tenmonphai()

        if tenmonphai == "maoson":
            self._action_xulyvebanrac_maoson()
        else:
            self._action_xulyvebanrac_phaikhac()

    def _action_xulyvebanrac_maoson(self):
        if not self._is_tudongvebanrac:
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
            if diachi_npc:
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

            elif is_dayhanhtrang:
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
            if self._xulydangbanrac():
                print("[AUTO-SELL] Đã bán xong, chuẩn bị quay lại")
                self._trangthaiveban = 4
                self._thoidiemchuyentrangthai = time.time()

        elif self._trangthaiveban == 4:
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

            if diachinpc and self.moitruong.get_khoangcach(diachinpc) <= 3.0:
                if not self.moitruong.get_is_dayhanhtrang():
                    if self._diemdanhxungquanhs:
                        print("[AUTO-SELL] Đứng cạnh NPC và túi đã gọn. Tiếp tục quay lại bãi farm.")
                        self._trangthaiveban = 4
                        return
                else:
                    print("[AUTO-SELL] Đứng cạnh NPC nhưng túi đầy. Tiếp tục bán.")
                    self._trangthaiveban = 2
                    return
            if self.moitruong.get_is_dayhanhtrang():
                print("[AUTO-SELL] Hành trang đầy. Bắt đầu quy trình về bán.")
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
            if self._xulydangbanrac():
                print("[AUTO-SELL] Đã bán xong.")
                self._trangthaiveban = 4

        elif self._trangthaiveban == 4:
            if not self._diemdanhxungquanhs:
                print("[AUTO-SELL] Lỗi: Không có danh sách điểm đánh!")
                self._trangthaiveban = 0
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
