import queue
import random
import re
import threading
import time
import traceback
import unicodedata

import pymem.exception

from hangso_xq import IS_BOKHUNGSAUTANCONG, CHUKYBOKHUNGSAUTANCONG, THOIGIANCHOBOKHUNGSAUTANCONG, TUTHENHANVAT_DELAYSAUTANCONG, CHUKYGIUOTRONGHANHTRANG
from hangso_xq import BANDO_BANGPHAI, TRUONGPHONGTIENSINH, RUONGDUTRU
from hangso_xq import BANDO_CHIENTRUONG, BANDO_TANTHUTHON, TUTHENHANVAT_DUNGIM, BANDO_YENTRUONGTHANH3, BANDO_YENTRUONGTHANH2, BANDO_YENTRUONGTHANH1, TANGBAODO, LAMCAU, HACCAU, HIEUUNGKYNANG_TRONGTHUONG
from moitruong_xq import MoiTruong
from tactu_xq import TacTu
from tienich_xq import phatam


class LoopLamMoiTrangThaiMoiTruong:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop LÀM MỚI] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                print(f"[Loop LÀM MỚI] Lỗi không xác định: {e}")
            time.sleep(0.2)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai() or self.moitruong.get_is_dangmatketnoi():
            return
        self.moitruong.action_lammoitrangthaimoitruong()


class LoopTimKiemMucTieu:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop TÌM MỤC TIÊU] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                print(f"[Loop TÌM MỤC TIÊU] Lỗi không xác định: {e}")
            time.sleep(0.15)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai() or self.moitruong.get_is_dangmatketnoi():
            return
        if self.tactu.get_is_dangtamngung():
            return
        self.tactu.action_tudongtimkiemmuctieu()
        self.tactu.action_tudongtimkiemmuctieumonphai()
        self.moitruong.action_phananhdiachicosothongtinnhanvatmuctieudangchoningame()


class LoopDieuPhoiDiChuyen:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop DI CHUYỂN] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                print(f"[Loop DI CHUYỂN] Lỗi không xác định: {e}")
            time.sleep(0.05)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai() or self.moitruong.get_is_dangmatketnoi():
            return
        if self.tactu.get_is_dangtamngung():
            return
        # Tính đích theo nhóm ngay trước khi di chuyển (để ở loop chính thì phải chờ cả lượt dùng kỹ năng, đích bị cũ nên chạy theo vị trí trưởng nhóm từ lâu)
        self.tactu.action_tudongtheosau()
        self.tactu.action_xulyuutiendichuyen()


class LoopChinh:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        self.thoidiemhopthanhtinhthach_map = {}
        self.thoidiemlogtinhthachgannhat = 0.

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop CHÍNH] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                print(f"[Loop CHÍNH] Lỗi không xác định: {e}")
                traceback.print_exc()
                # Ghi cả vào file log nhân vật: lỗi lặp lại mỗi lượt làm nhân vật đứng im không dùng kỹ năng mà log không thấy gì
                try:
                    self.moitruong._inlog(f"[Loop CHÍNH] Lỗi: {e}\n{traceback.format_exc()}")
                except Exception:
                    pass
                time.sleep(1)
            time.sleep(0.1)

    def _guilenhchomenu(self, caulenh, thoigianchotoida = 2.):
        # Gửi lệnh hội thoại NPC rồi chờ menu trả lời về (lời thoại cửa sổ tuỳ chọn có lại), tối đa thoigianchotoida giây.
        # -> True khi có menu về (không về thì lệnh trong cửa sổ là của menu cũ, đừng dùng)
        self.moitruong.xoa_noidungcuasotuychon()
        self.moitruong.action_thucthicaulenh(caulenh)
        hethan = time.time() + thoigianchotoida
        while time.time() < hethan and not self.moitruong.get_noidungcuasotuychon():
            time.sleep(0.1)
        time.sleep(0.25)
        return bool(self.moitruong.get_noidungcuasotuychon())

    def step(self):
        if not self.moitruong.get_is_nhanvattontai() or self.moitruong.get_is_dangmatketnoi():
            return

        if self.tactu.get_is_dangtamngung():
            return

        self.tactu.action_tudongxulygomquai()
        self.tactu.action_tudongsudungkynang()
        self.tactu.action_tudongdieukhienbaothu()

        # if self.moitruong.get_idnguoichoi() == 59844:
        #     print("{}".format(self.moitruong.get_danhsachhieuungnhanvats()))

        if self.moitruong.get_idbandohientai() == BANDO_BANGPHAI:
            # Nộp Rương Dự Trữ qua Trưởng Phòng Tiên Sinh, 4 bước như bấm tay: Hỗ trợ nhiệm vụ trù bị, Nhận nhiệm vụ,
            # (bấm lại NPC) Hoàn thành nhiệm vụ trù bị, Xác nhận. Số lệnh info.xx máy chủ đổi (info.55 / 58, info.11 / 18...)
            # nên mỗi bước lấy lệnh của lựa chọn đầu tiên trong menu vừa hiện thay vì ghi cứng số
            diachitruongphong = self.moitruong.action_timkiemnhanvat(tennhanvat = TRUONGPHONGTIENSINH)
            idtruongphong = self.moitruong.get_iddoituong(diachitruongphong) if diachitruongphong else 0
            if idtruongphong and self.moitruong.action_timkiemvatphamhanhtrang(RUONGDUTRU):
                # Bấm NPC = "look <id>#" (mở menu gốc), mỗi bước chọn lựa chọn đầu tiên; menu không về thì thôi lượt này.
                # Nhận nhiệm vụ và Xác nhận không có menu trả lời: gửi xong làm tiếp luôn, không chờ (trước chờ hết 2s mỗi lần)
                for is_bamnpc, is_comenutraloi in ((True, True), (False, False), (True, True), (False, False)):
                    if is_bamnpc and not self._guilenhchomenu("look {:x}#".format(idtruongphong)):
                        break
                    lenhs = [lenh for lenh in self.moitruong.get_lenhcuasotuychons() if lenh.startswith("talk {:x}# info.".format(idtruongphong))]
                    if not lenhs:
                        break
                    if not is_comenutraloi:
                        self.moitruong.action_thucthicaulenh(lenhs[0])
                        time.sleep(0.3)
                    elif not self._guilenhchomenu(lenhs[0]):
                        break

        if self.moitruong.get_idnguoichoi() in (29, 30, 31, 32, 273):
            for tenvatpham in ("Túi Ngân Lượng", "Túi Kim Bảo", "Túi Quà Vô Song", "Túi Pháp Bảo", "Lễ Bao Khai Quốc", "Túi Linh Thạch cấp 1"):
                if self.tactu.action_sudungvatphamhanhtrang(tenvatpham):
                    break

            def chuanhoaten(ten):
                # Bỏ dấu, gộp khoảng trắng thừa và bỏ phân biệt hoa thường để "Thủy"/"Thuỷ", "Tinh  Thạch" đều khớp
                if not ten:
                    return ""
                ten = "".join(c for c in unicodedata.normalize("NFD", ten) if not unicodedata.combining(c))
                return " ".join(ten.replace("đ", "d").replace("Đ", "D").split()).lower()

            # Hợp thành Tinh Thạch khi có >= 5 viên cùng tên
            for tenvatphamhanhtrang, vatphams in self.moitruong.get_danhsachvatphamhanhtrang_map().items():
                tenchuanhoa = chuanhoaten(tenvatphamhanhtrang)
                if "tinh thach" not in tenchuanhoa:
                    continue
                capdo = re.search(r"cap\s*(\d+)", tenchuanhoa)
                # Chỉ hợp thành Tinh Thạch dưới cấp 3
                if capdo and int(capdo.group(1)) >= 3:
                    continue
                # Nhóm vừa gửi lệnh hợp thành thì nhường lượt cho nhóm khác, tránh một nhóm lỗi chặn cả các cấp sau
                if time.time() - self.thoidiemhopthanhtinhthach_map.get(tenvatphamhanhtrang, 0) < 2.:
                    continue
                iddoituongs = [iddoituong for vitri, iddoituong in vatphams if iddoituong]
                if len(iddoituongs) >= 5:
                    self.moitruong.action_thucthicaulenh2("mix5 {} 0".format(" ".join("{}#".format(hex(x).replace("0x", "")) for x in iddoituongs[:5])))
                    self.thoidiemhopthanhtinhthach_map[tenvatphamhanhtrang] = time.time()
                    time.sleep(0.25)
                    break

        # vitrivatphams = [0, ]
        # if self.moitruong.get_idnguoichoi() == 102:
        #     for vitrivatpham in vitrivatphams:
        #         while True:
        #             iddoituong = self.moitruong.get_iddoituongvatphamhanhtrang(vitrivatpham)
        #             if not iddoituong:
        #                 break
        #             self.moitruong.truyvan_motavatphamhanhtrang(vitrivatpham)
        #             motavatpham = self.moitruong.get_motavatphamhanhtrang(vitrivatpham)
        #             #print("Mô tả vật phẩm: {}".format(motavatpham))
        #
        #             match = re.search(r"Nội Kháng:\s*\+(\d+)", motavatpham)
        #
        #             if match:
        #                 chisohientai = int(match.group(1))
        #                 print(f"Đã tìm thấy Nội Kháng: {chisohientai}")
        #
        #                 if chisohientai >= 85:
        #                     print("Nội Kháng >= 85. Dừng tiến trình!")
        #                     break
        #                 else:
        #                     self.moitruong.action_thucthicaulenh2("tallk 165a# giaotrangbi.{}# 0".format(hex(iddoituong)).replace("0x", ""))
        #                     time.sleep(0.2)
        #             else:
        #                 print("Không tìm thấy dòng Nội Kháng trong mô tả vật phẩm này.")
        #                 self.moitruong.action_thucthicaulenh2("tallk 165a# giaotrangbi.{}# 0".format(hex(iddoituong)).replace("0x", ""))
        #                 time.sleep(0.2)

        # if self.moitruong.get_idnguoichoi() == 60055:
        #     if not self.moitruong.action_timkiemvatphamhanhtrang("Túi Pháp Bảo"):
        #         self.moitruong.action_thucthicaulenh("buyitem ! 5 4 1")
        #         time.sleep(0.25)

        # if self.moitruong.get_idnguoichoi() in (59844, 59845):
        #     diachithiensutraodoi = self.moitruong.action_timkiemnhanvat("Thiên Sứ Trao Đổi")
        #     if not diachithiensutraodoi:
        #         return
        #     idthiensutraodoi = self.moitruong.get_iddoituong(diachithiensutraodoi)
        #     if not idthiensutraodoi:
        #         return
        #     if self.moitruong.get_khoangcach(diachithiensutraodoi) > 6:
        #         return
        #     if not self.moitruong.action_timkiemvatphamhanhtrang(LAMCAU) or not self.moitruong.action_timkiemvatphamhanhtrang(HACCAU):
        #         return
        #     self.moitruong.action_thucthicaulenh("tallk {}# bonus.29".format(hex(idthiensutraodoi).replace("0x", "")))
        #     time.sleep(0.25)
        #
        #     iddoituongtuivaibaobo = self.moitruong.action_timkiemvatphamhanhtrang("Bao Vải Ma Bố")
        #
        #     if iddoituongtuivaibaobo:
        #         self.moitruong.action_thucthicaulenh("drop ! {}#1".format(hex(iddoituongtuivaibaobo)).replace("0x", ""))
        #         time.sleep(0.25)
        #

        # if self.moitruong.get_idnguoichoi() == 59996:
        #     idtinhnguyendon = self.moitruong.action_timkiemvatphamhanhtrang("Tinh Nguyên Đơn")
        #     iddoituongbaothugiangho = self.moitruong.get_iddoituongbaothugiangho()
        #     if idtinhnguyendon and iddoituongbaothugiangho:
        #         idtinhnguyendon = hex(idtinhnguyendon).replace("0x", "")
        #         iddoituongbaothugiangho = hex(iddoituongbaothugiangho).replace("0x", "")
        #
        #         caulenh = "pet {}# fuse_yy {}#".format(iddoituongbaothugiangho, idtinhnguyendon)
        #         print()
        #         self.moitruong.action_thucthicaulenh(caulenh)
        #         time.sleep(0.25)


class LoopPhu:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event, giamsat = None):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        # Watchdog (giamsat_xq): mỗi lượt đánh dấu nhịp, lâu không có là luồng treo
        self.giamsat = giamsat
        self.thoidiemthongbaochetgannhat = time.time()
        self.thoidiempfgannhat = time.time()

    def __del__(self):
        try:
            self.moitruong.action_tatvohieuhoathietlapmuctieu()
            self.moitruong.action_tatvohieuhoatuthedelaysautancong()
            self.moitruong.action_tatvohieuhoalongclick()
            self.moitruong.action_tatvohieuhoatrangthaichuotchonmuctieukynang()
            self.moitruong.action_tatvohieuhoaphimspace()
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass
        if not self.stop.is_set():
            self.stop.set()

    def _thongbaochet(self):
        if self.moitruong.get_is_nhanvatdachet() and self.moitruong.get_idbandohientai() != BANDO_CHIENTRUONG:
            if time.time() - self.thoidiemthongbaochetgannhat > 5.0:
                self.thoidiemthongbaochetgannhat = time.time()
                phatam("Nhân vật đã chết", is_block = False)

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop PHỤ] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                traceback.print_exc()
                print(f"[Loop PHỤ] Lỗi không xác định: {e}")
            if self.giamsat:
                self.giamsat.danhdau("phụ")
            time.sleep(0.5)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai() or self.moitruong.get_is_dangmatketnoi():
            return

        self.moitruong.action_vohieuhoathietlapmuctieu()
        self.moitruong.action_vohieuhoatuthedelaysautancong()
        if self.tactu._is_tudongsudungkynang:
            self.moitruong.action_vohieuhoalongclick()
        else:
            self.moitruong.action_tatvohieuhoalongclick()
        self.moitruong.action_vohieuhoatrangthaichuotchonmuctieukynang()
        self.moitruong.action_vohieuhoakhoanhvungkynang()
        self.moitruong.action_vohieuhoaphimspace()
        self.moitruong.action_vohieuhieuungmuloa()

        # Thấy người chơi ẩn thân, hoặc người lạ ở map train, khi đang di chuyển theo lộ trình điểm đánh: ngưng mọi hoạt động (có nút Bật lại trên bảng điều khiển)
        self.tactu.action_kiemtraanthan()
        if self.tactu.get_is_dangtamngung():
            return

        # Đang nằm chết chờ phục sinh: không làm gì khác (trước đây luồng này bị sleep chặn trong lúc chờ nên cũng không làm gì)
        self.tactu.action_tudongphucsinh()
        if self.tactu.get_is_dangchophucsinh():
            self._thongbaochet()
            return

        self.tactu.action_tudongsudungvatpham()
        self.tactu.action_chantangcapdo()
        self.tactu.action_tudongxepchongvatpham()
        self.tactu.action_sapxephanhtrang()
        self.tactu.action_tudongdatvatphammoi()
        self.tactu.action_tudongtodoi()
        self.tactu.action_tudongdoimaupk()
        self.tactu.action_tudonghoibangphai()
        self.tactu.action_tudongmuavatpham()
        self.tactu.action_tudongsuavatpham()

        self.tactu.action_xulyhoithoainpc()
        self.tactu.action_xulybanracvasuado()
        self.tactu.action_tudongxulyvebanrac()
        self.tactu.action_tudongkhaikhoang()
        self.tactu.action_tudongdaotangbaodo()

        self.tactu.action_tudongtrieuhoibaothugiangho()

        self.tactu.action_tudongdichientruong()
        self.tactu.action_tudongdichuyentudo()
        self.tactu.action_tudongnhatvatpham()
        self.tactu.action_tudongvutvatpham()
        self.tactu.action_tudongvutvatphamtheoluat()

        self._thongbaochet()

        if not self.moitruong.get_is_bathanhtrang():
            self.moitruong.set_is_batalt(True)

        self.tactu.action_tudongbatautoingame()

        self.moitruong.action_vohieuhoahookchienquoc2()

        if self.moitruong.get_idnguoichoi() in (59996, ) and self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
            diachi = self.moitruong.action_timkiemnhanvat("Thiên Sứ Trao Đổi")
            if diachi and self.moitruong.get_khoangcach(diachi) <= 3.:
                lamcau = self.moitruong.action_timkiemvatphamhanhtrang(LAMCAU)
                haccau = self.moitruong.action_timkiemvatphamhanhtrang(HACCAU)
                if lamcau and haccau:
                    self.moitruong.action_thucthicaulenh("tallk {}# bonus.23".format(hex(self.moitruong.get_iddoituong(diachi))).replace("0x", ""))
                    time.sleep(0.25)
                elif lamcau:
                    self.moitruong.action_thucthicaulenh("tallk {}# bonus.9".format(hex(self.moitruong.get_iddoituong(diachi))).replace("0x", ""))

                for _ in range(2):
                    iddoituongtangbaodo = self.moitruong.action_timkiemvatphamhanhtrang(TANGBAODO, is_ruongdautien = True)
                    if iddoituongtangbaodo:
                        self.moitruong.action_thucthicaulenh("move {}# to {}".format(hex(iddoituongtangbaodo), random.randint(2, 4)).replace("0x", ""))


class LoopBoKhungSauTanCong:
    # Luồng riêng, chu kỳ ngắn (CHUKYBOKHUNGSAUTANCONG): tư thế khựng sau đòn kéo dài quá THOIGIANCHOBOKHUNGSAUTANCONG giây
    # thì ghi về đứng im (các luồng khác chạy 0.1-0.5s/lượt nên không bắt kịp)
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        # Lúc nhân vật bắt đầu vào tư thế khựng sau đòn (0 = không đang khựng)
        self.thoidiembatdaukhung = 0.

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                if IS_BOKHUNGSAUTANCONG and self.moitruong.get_is_nhanvattontai() and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DELAYSAUTANCONG:
                    if not self.thoidiembatdaukhung:
                        self.thoidiembatdaukhung = time.time()
                    elif time.time() - self.thoidiembatdaukhung >= THOIGIANCHOBOKHUNGSAUTANCONG:
                        self.moitruong.set_idtuthenhanvat(TUTHENHANVAT_DUNGIM)
                        self.thoidiembatdaukhung = 0.
                else:
                    self.thoidiembatdaukhung = 0.
            except (pymem.exception.PymemError, pymem.exception.WinAPIError):
                time.sleep(1)
            except Exception as e:
                print(f"[Loop BỎ KHỰNG] Lỗi không xác định: {e}")
                time.sleep(1)
            time.sleep(CHUKYBOKHUNGSAUTANCONG)


class LoopGiuOTrongHanhTrang:
    # Luồng riêng, chu kỳ ngắn (CHUKYGIUOTRONGHANHTRANG) cho việc hành trang / trang bị cần nhanh trong lúc vận khí
    # (LoopPhu 0.5s/lượt không kịp): đang chế đồ thì vật phẩm vừa vào ô cuối hành trang 1 phải được chuyển đi ngay trước lần chế
    # kế tiếp; đang vận khí gọi bảo thú triệu hồi thì đổi đồ, xong mặc lại; kỹ năng vừa gửi cần đứng lại thì ngắt di chuyển
    # ngay khi nhân vật vào tư thế xuất chiêu
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                if self.moitruong.get_is_nhanvattontai() and not self.moitruong.get_is_dangmatketnoi():
                    # Cập nhật mốc xuất chiêu đủ dày để biết chính xác lúc hết tư thế xuất chiêu (khựng tính từ mốc này)
                    self.moitruong.get_is_dangxuatchieu()
                    self.moitruong.action_baogiuluotkhixuatchieu()
                    self.tactu.action_giuotrongcuoihanhtrang()
                    self.tactu.action_doidokhitrieuhoi()
                    self.tactu.action_ngatdichuyenkhixuatchieu()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError):
                time.sleep(1)
            except Exception as e:
                print(f"[Loop GIỮ Ô TRỐNG] Lỗi không xác định: {e}")
                traceback.print_exc()
                time.sleep(1)
            time.sleep(CHUKYGIUOTRONGHANHTRANG)


class LoopXuLyLenh:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                lenhthucthi = self.moitruong.hangdoicaulenh.get(timeout = 0.05)
                if lenhthucthi.caulenh in self.moitruong.caulenhdangchos:
                    self.moitruong.caulenhdangchos.remove(lenhthucthi.caulenh)
                self.moitruong._ghilenhvaobonho(lenhthucthi)
                self.moitruong.hangdoicaulenh.task_done()
            except queue.Empty:
                continue
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop XỬ LÝ LỆNH] Lỗi bộ nhớ: {err}")
                time.sleep(0.1)
            except Exception as e:
                print(f"[Loop XỬ LÝ LỆNH] Lỗi không xác định: {e}")
                time.sleep(0.1)
