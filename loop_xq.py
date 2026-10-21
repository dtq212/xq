import queue
import random
import re
import threading
import time
import traceback
import unicodedata

import pymem.exception

from hangso_xq import BANDO_CHIENTRUONG, BANDO_TANTHUTHON, TUTHENHANVAT_DUNGIM, VATPHAMKHONGBANs, BANDO_YENTRUONGTHANH3, BANDO_YENTRUONGTHANH2, BANDO_YENTRUONGTHANH1, TANGBAODO, LAMCAU, HACCAU, HIEUUNGKYNANG_TRONGTHUONG
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
        self.tactu.action_tudongtheosautruongnhom()
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
                time.sleep(1)
            time.sleep(0.1)

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

        # if self.moitruong.get_idnguoichoi() in (29, 30, 31, 32):
        #     if not self.moitruong.action_timkiemvatphamhanhtrang("Rương Dự Trữ"):
        #         time.sleep(0.25)
        #     self.moitruong.action_thucthicaulenh("tallk 4cdfa# info.10")
        #     time.sleep(0.25)
        #     self.moitruong.action_thucthicaulenh("tallk 4cdfa# info.11")
        #     time.sleep(0.25)
        #     self.moitruong.action_thucthicaulenh("tallk 4cdfa# info.20")
        #     time.sleep(0.25)
        #     self.moitruong.action_thucthicaulenh("tallk 4cdfa# info.21")
        #     time.sleep(0.25)

        # Nộp Rương dự trữ (khôi phục từ main2/loop.py, commit cae781b) — id NPC (810a) đổi mỗi lần, cần sửa trước khi bật
        # self.moitruong.action_thucthicaulenh("tallk 810a# info.58", delay = 0.)
        # time.sleep(0.25)
        # self.moitruong.action_thucthicaulenh("tallk 810a# info.18", delay = 0.)
        # time.sleep(0.25)
        # self.moitruong.action_thucthicaulenh("tallk 810a# info.20", delay = 0.)
        # time.sleep(0.25)
        # self.moitruong.action_thucthicaulenh("tallk 810a# info.21", delay = 0.)
        # time.sleep(0.25)

        if self.moitruong.get_idnguoichoi() in (29, 30, 31, 32, ):
            if self.moitruong.action_timkiemvatphamhanhtrang("Túi Ngân Lượng"):
                self.tactu.action_sudungvatphamhanhtrang("Túi Ngân Lượng")
                time.sleep(0.25)
            if self.moitruong.action_timkiemvatphamhanhtrang("Chén Bạc"):
                self.tactu.action_sudungvatphamhanhtrang("Chén Bạc")
                time.sleep(0.25)
            if self.moitruong.action_timkiemvatphamhanhtrang("Túi Kim Bảo"):
                self.tactu.action_sudungvatphamhanhtrang("Túi Kim Bảo")
                time.sleep(0.25)
            if self.moitruong.action_timkiemvatphamhanhtrang("Túi Quà Vô Song"):
                self.tactu.action_sudungvatphamhanhtrang("Túi Quà Vô Song")
                time.sleep(0.25)
            if self.moitruong.action_timkiemvatphamhanhtrang("Túi Pháp Bảo"):
                self.tactu.action_sudungvatphamhanhtrang("Túi Pháp Bảo")
                time.sleep(0.25)
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
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
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
            time.sleep(0.5)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai() or self.moitruong.get_is_dangmatketnoi():
            return

        self.moitruong.action_vohieuhoathietlapmuctieu()
        self.moitruong.action_vohieuhoatuthedelaysautancong()
        self.moitruong.action_vohieuhoalongclick()
        self.moitruong.action_vohieuhoatrangthaichuotchonmuctieukynang()
        self.moitruong.action_vohieuhoakhoanhvungkynang()
        self.moitruong.action_vohieuhoaphimspace()
        self.moitruong.action_vohieuhieuungmuloa()

        # Thấy người chơi ẩn thân, hoặc người lạ ở map train, khi đang di chuyển theo lộ trình điểm đánh: ngưng mọi hoạt động (có nút Bật lại trên bảng điều khiển)
        self.tactu.action_kiemtraanthan()
        if self.tactu.get_is_dangtamngung():
            return

        self.tactu.action_tudongsudungvatpham()
        self.tactu.action_chantangcapdo()
        self.tactu.action_tudongxepchongvatpham()
        self.tactu.action_tudongtodoi()
        self.tactu.action_tudongphucsinh()
        self.tactu.action_tudongdoimaupk()
        self.tactu.action_tudongmuavatpham()
        self.tactu.action_tudongsuavatpham()

        self.tactu.action_tudongxulyvebanrac()
        self.tactu.action_tudongkhaikhoang()
        self.tactu.action_tudongdaotangbaodo()

        self.tactu.action_tudongtrieuhoibaothugiangho()

        self.tactu.action_tudongdichientruong()
        self.tactu.action_tudongdichuyentudo()
        self.tactu.action_tudongnhatvatpham()
        self.tactu.action_tudongvutvatpham()

        if self.moitruong.get_is_nhanvatdachet() and self.moitruong.get_idbandohientai() != BANDO_CHIENTRUONG:
            if time.time() - self.thoidiemthongbaochetgannhat > 5.0:
                self.thoidiemthongbaochetgannhat = time.time()
                phatam("Nhân vật đã chết", is_block = False)

        if not self.moitruong.get_is_bathanhtrang():
            self.moitruong.set_is_batalt(True)

        self.tactu.action_tudongbatautoingame()

        self.moitruong.action_vohieuhoahookchienquoc2()
        self.tactu.action_tudongmuaauto()

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
