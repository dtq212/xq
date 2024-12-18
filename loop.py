import threading
import time
import pymem.exception
from hangso import *
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

            time.sleep(0.02)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return
        if self.moitruong.get_is_dangmatketnoi():
            return

        self.moitruong.action_lammoitrangthaimoitruong()


class LoopTimKiemMucTieu:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        try:
            pass
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass

        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print("Luồng tìm kiếm mục tiêu: {}".format(err))
                # raise Exception(err)
                time.sleep(1)

            time.sleep(0.02)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.moitruong.get_is_dangmatketnoi():
            return

        self.tactu.action_tudongtimkiemmuctieu()

class LoopChinh:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        self.i = 0

    def __del__(self):
        try:
            pass
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass

        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print("Luồng chính: {}".format(err))
                time.sleep(1)

            time.sleep(0.02)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.moitruong.get_is_dangmatketnoi():
            return

        if time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() < 0.5:
            return

        self.tactu.action_tudongtheosautruongnhom()

        tenmonphai = MONPHAI_MAP.get(self.moitruong.get_idkynang(0, 0))
        if hasattr(self.tactu, "action_tudongsudungkynang_{}".format(tenmonphai)):
            getattr(self.tactu, "action_tudongsudungkynang_{}".format(tenmonphai))()

        # while True:
        #     self.tactu.action_sudungvatphamhanhtrang(TUILINHTHACHCAP1)
        #     time.sleep(0.25)
        #     self.tactu.action_sudungvatphamhanhtrang(TUILINHTHACHCAP2)
        #     time.sleep(0.25)
        #     self.tactu.action_tudonghopthanhlinhthach()
        #     time.sleep(0.25)

        # while True:
        #     self.moitruong.action_thucthicaulenh("noichuyen 21d# gift.30", delay = 0.25)
        #     time.sleep(0.25)
        #     self.tactu.action_tudongxepchongdo()
        #     time.sleep(0.25)

        # while True:
        #     self.moitruong.action_thucthicaulenh("talk 61201# info.10050")
        #     time.sleep(0.1)
        #     self.moitruong.action_thucthicaulenh("talk 61201# info.11")
        #     time.sleep(0.1)
        #     self.moitruong.action_thucthicaulenh("talk 61201# info.200")
        #     time.sleep(0.1)
        #     self.moitruong.action_thucthicaulenh("talk 61201# info.210")
        #     time.sleep(0.1)

        # i = 0
        #
        # while True:
        #     #noi cong 143
        #     #bao kich 146
        #     self.moitruong.action_thucthicaulenh("talk 6365e# info.143")
        #     time.sleep(0.05)
        #     i += 1
        #     if i % 10 == 0:
        #         self.tactu.action_sudungvatphamhanhtrang(TUSAMDONTRUNG)
        #         time.sleep(0.5)

        # while True:
        #     iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(DOANTHACHDACBIETSOCAP)
        #
        #     if not iddoituongvatpham:
        #         print("khong tim thay")
        #         break
        #
        #     caulenh = "move ! {}# 1".format(hex(iddoituongvatpham)).replace("0x", "")
        #
        #     self.moitruong.action_thucthicaulenh(caulenh)
        #
        #     time.sleep(0.25)

        # solan = 100
        #
        # for i in range(1, solan + 1):
        #     self.moitruong.action_thucthicaulenh("talk 227# giaotrangbi.411b5#")
        #     time.sleep(0.05)
        #     if not i % 10:
        #         time.sleep(2)

        # time.sleep(5555)
        # time.sleep(1)
        # self.tactu.action_sudungvatphamhanhtrang(PHIHANHPHU)
        # time.sleep(555)

        # muctieu = self.moitruong.get_diachicosothongtinnhanvatdangchichuot()
        # if muctieu:
        #     print(self.moitruong.get_tendoituong(muctieu))

        # if not self.i:
        #     pass
            # self.i = 1
            # self.tactu.action_tudongtimduong(BANDO_KHONMATRAN1)

        # print(self.moitruong.get_danhsachhieuungnhanvats())

class LoopPhu:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

        self.thoidiemthongbaochetgannhat = time.time()

    def __del__(self):
        try:
            self.moitruong.action_tatvohieuhoatuthedelaysautancong()
            self.moitruong.action_tatvohieuhoathietlapmuctieu()
            self.moitruong.action_tatvohieuhoaxoamuctieu()
            self.moitruong.action_tatvohieuhoalongclick()
            self.moitruong.action_tatvohieuhoatrangthaichuotchonmuctieukynang()
            self.moitruong.action_tatvohieuhoakhoanhvungkynang()
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
                print("Luồng phụ: {}".format(err))
                time.sleep(1)

            time.sleep(0.02)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.moitruong.get_is_dangmatketnoi():
            return

        if time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() < 0.5:
            return

        self.moitruong.action_vohieuhoatuthedelaysautancong()
        self.moitruong.action_vohieuhoathietlapmuctieu()

        if self.moitruong.get_is_bathanhtrang():
            self.moitruong.set_is_batalt(False)
        else:
            self.moitruong.set_is_batalt(True)

        self.moitruong.action_vohieuhoaxoamuctieu()
        self.moitruong.action_vohieuhoalongclick()

        self.moitruong.action_vohieuhoatrangthaichuotchonmuctieukynang()
        self.moitruong.action_vohieuhoakhoanhvungkynang()
        self.moitruong.action_vohieuhoaphimspace()

        self.tactu.action_tudongdichuyenxungquanhdiem()
        self.tactu.action_tudongdichientruong()
        self.tactu.action_tudongdibatquaitran()

        self.tactu.action_tudongxepchongdo()

        self.tactu.action_tudongtodoi()

        if self.moitruong.get_is_nhanvatdachet():
            if time.time() - self.thoidiemthongbaochetgannhat > 5.:
                self.thoidiemthongbaochetgannhat = time.time()
                phatam("Nhân vật đã chết")

        self.tactu.action_tudongphucsinh()
        self.tactu.action_tudongdichuyenlenbandovuachet()
        self.tactu.action_tudongdoimaupk()
        self.tactu.action_tudongsuado()

        self.tactu.action_tudongtrieuhoibaothudautien()
        self.tactu.action_tudongcuoithu()

        self.tactu.action_tudongnhatdo()
        self.tactu.action_tudongvutdo()

class LoopSuDungVatPham:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        try:
            pass
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass

        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print("Luồng sử dụng vật phẩm: {}".format(err))
                time.sleep(1)

            time.sleep(0.02)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.moitruong.get_is_dangmatketnoi():
            return

        if time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() < 0.5:
            return

        self.tactu.action_tudongsudungvatpham()
