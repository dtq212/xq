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

            time.sleep(0.05)

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
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print("Luồng tìm kiếm mục tiêu: {}".format(err))
                time.sleep(1)

            time.sleep(0.05)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.moitruong.get_is_dangmatketnoi():
            return

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
            time.sleep(0.05)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return
        if self.moitruong.get_is_dangmatketnoi():
            return
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
                time.sleep(1)

            time.sleep(0.05)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.moitruong.get_is_dangmatketnoi():
            return

        self.tactu._action_theonhom()
        self.tactu.action_xulygomquai()
        self.tactu._action_sudungkynang()

        #if self.moitruong.get_idnguoichoi() == 4642:
        #    # self.tactu.action_sudungvatphamhanhtrang(TUSAMDON, delay = 5.)
        #    self.moitruong.action_thucthicaulenh("tallk 29d# bonus.1")
        #    time.sleep(0.25)
        #    self.moitruong.action_thucthicaulenh("tallk 29d# bonus.28")
        #    time.sleep(0.25)
        #    self.moitruong.action_thucthicaulenh("tallk 29d# bonus.29")
        #    time.sleep(0.25)

        # if diachidoituong := self.moitruong.get_diachicosothongtinnhanvatdangchichuot():
        #     print(self.moitruong.get_tendoituong(diachidoituong))
            # print(self.moitruong.get_danhsachhieuungnhanvats(diachidoituong))
            # print(self.moitruong.get_tendoituong(diachidoituong))
        # print(self.moitruong.get_danhsachhieuungnhanvats())
        # print(self.moitruong.get_danhsachvatphamhanhtrang_map().keys())

        # print(self.moitruong.get_idkynang(0, 0))

        # if self.moitruong.get_tendoituong() == "ThoLuuManh1":
        #     self.moitruong.action_thucthicaulenh("noichuyen 1ed# gift.30", delay = 0)
        #     time.sleep(0.5)
            # if diachi := self.moitruong.action_timkiemnhanvat(iddoituong = self.moitruong.get_iddoituongbaothumaoson()):
            #     print(hex(diachi))

        # if self.moitruong.get_tendoituong() == "ThoLuuManh2":
        #     print(self.moitruong.get_danhsachhieuungnhanvats())
        #     if diachidoituong := self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon():
        #         print(self.moitruong.get_danhsachhieuungnhanvats(diachidoituong))
        #         print(self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG, ), macdinh = True, is_hieuungcoloi = 0))

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
            time.sleep(0.05)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.moitruong.get_is_dangmatketnoi():
            return

        self.moitruong.action_vohieuhoathietlapmuctieu()
        self.moitruong.action_vohieuhoatuthedelaysautancong()
        self.moitruong.action_vohieuhoalongclick()
        self.moitruong.action_vohieuhoatrangthaichuotchonmuctieukynang()
        self.moitruong.action_vohieuhoakhoanhvungkynang()
        self.moitruong.action_vohieuhoaphimspace()
        self.tactu.action_chantangcapdo()
        self.tactu.action_tudongxepchongdo()
        self.tactu.action_tudongtodoi()
        self.tactu.action_tudongphucsinh()
        self.tactu.action_tudongdoimaupk()
        self.tactu.action_tudongsuado()
        self.tactu.action_tudongvutdo()
        self.tactu.action_xulyvebanrac()
        self.tactu.action_tudongkhaikhoang()

        self.tactu.action_tudongtrieuhoibaothudautien()
        self.tactu.action_tudongdieukhienbaothumaoson()
        self.tactu.action_tudongdichientruong()
        self.tactu.action_tudonglamnhiemvusugia()
        self.tactu.action_dichuyentudo()
        self.tactu.action_nhatdo()

        if self.moitruong.get_is_nhanvatdachet():
            if time.time() - self.thoidiemthongbaochetgannhat > 5.:
                self.thoidiemthongbaochetgannhat = time.time()
                phatam("Nhân vật đã chết")

        if not self.moitruong.get_is_bathanhtrang():
            self.moitruong.set_is_batalt(True)

class LoopSuDungVatPham:
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
                print("Luồng sử dụng vật phẩm: {}".format(err))
                time.sleep(1)

            time.sleep(0.05)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.moitruong.get_is_dangmatketnoi():
            return

        self.tactu.action_tudongsudungvatpham()