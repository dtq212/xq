import threading
import time
import traceback

import pymem.exception

from hangso_xq import BANDO_CHIENTRUONG, BANDO_CHU, BANDO_TANTHUTHON, TUTHENHANVAT_DUNGIM, BANDOFARMs, BANDOKHONGPKs
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
                print(f"[Loop DI CHUYỂN] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                print(f"[Loop DI CHUYỂN] Lỗi không xác định: {e}")
            time.sleep(0.1)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai() or self.moitruong.get_is_dangmatketnoi():
            return
        self.tactu.action_xulydichuyenuutien()


class LoopChinh:
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

        if self.moitruong.get_is_dangmocuasoxacnhan():
            phatam("Mã xác nhận", is_block = False)
            time.sleep(2.0)
            noidungcuasoxacnhan = self.moitruong.get_noidungcuasomaxacnhan()
            try:
                maxacnhan = noidungcuasoxacnhan.split(":")[1].strip()
                if maxacnhan.isnumeric():
                    caulenh = f"captcha2 {maxacnhan}"
                    self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                    self.moitruong.set_is_dangmocuasoxacnhan(False)
                    time.sleep(1.0)
            except IndexError:
                print("Không tìm thấy mã xác nhận đúng định dạng")
            return

        self.tactu._action_theonhom()
        self.tactu.action_xulygomquai()
        self.tactu._action_sudungkynang()
        self.tactu.action_tudongsudungkynangbaothu()

        # if self.moitruong.get_idnguoichoi() == 4599 and self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG:
        #     if not self.moitruong.get_is_dangnamtrongnhom():
        #         self.moitruong.action_thucthicaulenh("team + 4599", delay = 0)
        #         time.sleep(0.5)


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
                print(f"[Loop PHỤ] Lỗi không xác định: {e}")
            time.sleep(0.5)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai() or self.moitruong.get_is_dangmatketnoi():
            return

        if self.moitruong.get_idbandohientai() == BANDO_CHU and self.moitruong.get_khoangcachdiem(292, 184) < 18 and self.moitruong.get_phantramsinhlucconlai() < 25:
            self.moitruong.action_ngatdichuyen()
            self.tactu.action_sudunghoithanhphu()
            time.sleep(2.5)
            return

        self.moitruong.action_vohieuhoathietlapmuctieu()
        self.moitruong.action_vohieuhoatuthedelaysautancong()
        self.moitruong.action_vohieuhoalongclick()
        self.moitruong.action_vohieuhoatrangthaichuotchonmuctieukynang()
        self.moitruong.action_vohieuhoakhoanhvungkynang()
        self.moitruong.action_vohieuhoaphimspace()
        self.moitruong.action_vohieuhieuungmuloa()

        self.tactu.action_tudongsudungvatpham()
        self.tactu.action_chantangcapdo()
        self.tactu.action_tudongxepchongdo()
        self.tactu.action_tudongtodoi()
        self.tactu.action_tudongphucsinh()
        self.tactu.action_tudongdoimaupk()
        self.tactu.action_tudongsuado()

        self.tactu.action_xulyvebanrac()
        self.tactu.action_tudongkhaikhoang()
        self.tactu.action_tudongdaotangbaodo()

        # if self.moitruong.get_idnguoichoi() != 4676:
        #     self.tactu.action_tudongtrieuhoibaothudautien()

        self.tactu.action_tudongdichientruong()
        self.tactu.action_dichuyentudo()
        self.tactu.action_nhatdo()

        if self.moitruong.get_is_nhanvatdachet() and self.moitruong.get_idbandohientai() != BANDO_CHIENTRUONG:
            if time.time() - self.thoidiemthongbaochetgannhat > 5.0:
                self.thoidiemthongbaochetgannhat = time.time()
                phatam("Nhân vật đã chết", is_block = False)

        if not self.moitruong.get_is_bathanhtrang():
            self.moitruong.set_is_batalt(True)

        self.moitruong.set_is_batautoingame(False)
        if self.moitruong.get_idbandohientai() not in BANDOKHONGPKs and self.tactu._is_tudongsudungkynang:
            self.moitruong.action_batchucnangmorong()
            if time.time() - self.moitruong._thoidiemsudungkynanggannhat > 2.5 and time.time() - self.thoidiempfgannhat > 2.5:
                self.moitruong.action_thucthicaulenh("kill {}".format(self.moitruong.get_idnguoichoi()))

        self.moitruong.action_vohieuhoahookchienquoc2()
        self.tactu.action_muauto()