import threading
import time
import traceback

import pymem.exception

from hangso import BANDO_CHIENTRUONG, BANDO_CHU, HOITHANHPHU, TANTHUTHON, BANDO_TANTHUTHON, TUTHENHANVAT_DUNGIM
from moitruong import MoiTruong
from tactu import TacTu
from tienich import phatam


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
                print("Loop làm mới trạng thái môi trường: {}".format(err))
                time.sleep(1)
            time.sleep(0.2)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai(): return
        if self.moitruong.get_is_dangmatketnoi(): return
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
                print("Luồng tìm kiếm mục tiêu: {}".format(err))
                time.sleep(1)
            time.sleep(0.15)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai(): return
        if self.moitruong.get_is_dangmatketnoi(): return
        self.tactu.action_tudongtimkiemmuctieu()
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
                print("Luồng điều phối di chuyển: {}".format(err))
                time.sleep(1)
            time.sleep(0.1)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai(): return
        if self.moitruong.get_is_dangmatketnoi(): return
        self.tactu.action_xulydichuyenuutien()


class LoopChinh:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        self.i = 0

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print("Luồng chính: {}, {}".format(err, self.moitruong.get_tendoituong()))
                print(traceback.format_exc())
                time.sleep(1)
            time.sleep(0.1)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai(): return
        if self.moitruong.get_is_dangmatketnoi(): return
        self.tactu._action_theonhom()
        self.tactu.action_xulygomquai()
        self.tactu._action_sudungkynang()

        if self.moitruong.get_idnguoichoi() == 4599 and self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG:
            if not self.moitruong.get_is_dangnamtrongnhom():
                self.moitruong.action_thucthicaulenh("team + 4599", delay = 0)
                time.sleep(0.5)
        #if self.moitruong.get_idnguoichoi() == 4676:
        #    print(str(self.moitruong.get_danhsachvatphamhanhtrang_map()))

class LoopPhu:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        self.thoidiemthongbaochetgannhat = time.time()

    def __del__(self):
        try:
            self.moitruong.action_tatvohieuhoathietlapmuctieu()
            self.moitruong.action_tatvohieuhoatuthedelaysautancong()
            self.moitruong.action_tatvohieuhoalongclick()
            self.moitruong.action_tatvohieuhoatrangthaichuotchonmuctieukynang()
            self.moitruong.action_tatvohieuhoaphimspace()
        except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
            pass
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print("Luồng phụ: {}".format(err))
                time.sleep(1)
            time.sleep(0.5)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai(): return
        if self.moitruong.get_is_dangmatketnoi(): return

        if self.moitruong.get_idbandohientai() == BANDO_CHU and self.moitruong.get_khoangcachdiem(292, 184) < 18 and self.moitruong.get_phantramsinhlucconlai() < 25:
            self.moitruong.action_ngatdichuyen()
            self.tactu.action_sudunghoithanhphu()
            time.sleep(2.5)
            return

        self.tactu.action_tudongsudungvatpham()

        self.moitruong.action_vohieuhoathietlapmuctieu()
        self.moitruong.action_vohieuhoatuthedelaysautancong()
        self.moitruong.action_vohieuhoalongclick()
        self.moitruong.action_vohieuhoatrangthaichuotchonmuctieukynang()
        self.moitruong.action_vohieuhoakhoanhvungkynang()
        self.moitruong.action_vohieuhoaphimspace()

        # self.moitruong.set_idvukhi(13)
        # self.moitruong.set_idcanh((7, 7))

        # self.moitruong.set_mauvukhi((1, 1, 255))
        # self.moitruong.set_mauyphuc((1, 1, 255))
        # self.moitruong.set_mautoc((1, 1, 255))
        # self.moitruong.set_maucanh((1, 1, 255, 1, 1, 255))

        self.tactu.action_chantangcapdo()
        self.tactu.action_tudongxepchongdo()
        self.tactu.action_tudongtodoi()
        self.tactu.action_tudongphucsinh()
        self.tactu.action_tudongdoimaupk()
        self.tactu.action_tudongsuado()

        self.tactu.action_xulyvebanrac()
        self.tactu.action_tudongkhaikhoang()
        self.tactu.action_tudongdaotangbaodo()

        self.tactu.action_tudongtrieuhoibaothudautien()
        self.tactu.action_tudongsudungkynangbaothu()
        self.tactu.action_tudongdichientruong()
        self.tactu.action_dichuyentudo()
        self.tactu.action_nhatdo()

        if self.moitruong.get_is_nhanvatdachet() and self.moitruong.get_idbandohientai() != BANDO_CHIENTRUONG:
            if time.time() - self.thoidiemthongbaochetgannhat > 5.:
                self.thoidiemthongbaochetgannhat = time.time()
                phatam("Nhân vật đã chết")

        if not self.moitruong.get_is_bathanhtrang():
            self.moitruong.set_is_batalt(True)

        if self.moitruong.get_idnguoichoi() in (1904, 4676, 2303) and self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
            diachi = self.moitruong.action_timkiemnhanvat("Thiên Sứ Trao Đổi")
            if diachi and self.moitruong.get_khoangcach(diachi) <= 3.:
             self.moitruong.action_thucthicaulenh("tallk {}# bonus.1".format(hex(self.moitruong.get_iddoituong(diachi))).replace("0x", ""))
             time.sleep(0.25)
             self.moitruong.action_thucthicaulenh("tallk {}# bonus.22".format(hex(self.moitruong.get_iddoituong(diachi))).replace("0x", ""))
             time.sleep(0.25)
             self.moitruong.action_thucthicaulenh("tallk {}# bonus.23".format(hex(self.moitruong.get_iddoituong(diachi))).replace("0x", ""))
             time.sleep(0.25)

        