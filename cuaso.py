import os

import keyboard
from infi.systray import SysTrayIcon

from loop import *
from moitruong import MoiTruong
from tactu import TacTu
from hangso import *

def khoidong_looplammoitrangthaimoitruong(moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
    luong = LoopLamMoiTrangThaiMoiTruong(moitruong, tactu, stop)
    luong.loop()

def khoidong_looptimkiemmuctieu(moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
    luong = LoopTimKiemMucTieu(moitruong, tactu, stop)
    luong.loop()

def khoidong_loopchinh(moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
    luong = LoopChinh(moitruong, tactu, stop)
    luong.loop()

def khoidong_loopphu(moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
    luong = LoopPhu(moitruong, tactu, stop)
    luong.loop()


class CuaSo:
    def __init__(self, idcuaso):
        self.moitruong = MoiTruong(idcuaso)
        self.tactu = TacTu(self.moitruong)
        self.tennhanvat = False

        self.main_stop = threading.Event()

        self.luongs = (
            threading.Thread(target = khoidong_looplammoitrangthaimoitruong, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_looptimkiemmuctieu, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopchinh, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopphu, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
        )

        for luong in self.luongs:
            luong.start()

        self.systray = SysTrayIcon(os.path.join("_internal", "icon", "icon.ico"), CHUACHONHANVAT, on_quit = self.tatauto)
        self.systray.start()

        keyboard.add_hotkey("ctrl + f", self.battat_tudongsudungkynang)
        keyboard.add_hotkey("ctrl + c", self.thietlaptenmuctieutancong)
        keyboard.add_hotkey("ctrl + alt + f", self.battat_tudongtheosautruongnhom)

        keyboard.add_hotkey("ctrl + d", self.thietlapchidanhnguoichoi)
        keyboard.add_hotkey("ctrl + a", self.bothietlapchidanhnguoichoi)

        keyboard.add_hotkey("ctrl + p", self.themdiemdanhxungquanh)
        keyboard.add_hotkey("ctrl + alt + p", self.xoatoanbodiemdanhxungquanh)

        self.thoidiemluuthietlapgannhat = time.time()

    def tatauto(self, *args, **kwargs):
        self.main_stop.set()
        try:
            self.systray.shutdown()
        except:
            pass

    def loop(self):
        while not self.main_stop.is_set() and self.moitruong.get_is_cuasogametontai():
            if not self.moitruong.get_is_dangmatketnoi():
                tennhanvat = self.moitruong.get_tendoituong()
                if tennhanvat:
                    self.systray.update(hover_text = tennhanvat)

                if tennhanvat != self.tennhanvat:
                    if tennhanvat:
                        self.tactu.taithietlap(tennhanvat)

                elif tennhanvat and time.time() - self.thoidiemluuthietlapgannhat > 2.:
                    self.thoidiemluuthietlapgannhat = time.time()
                    self.tactu.luuthietlap(tennhanvat)

                self.tennhanvat = tennhanvat
            else:
                self.systray.update(hover_text = CHUACHONHANVAT)

            time.sleep(1)
        try:
            self.systray.shutdown()
        except:
            pass

    def battat_tudongsudungkynang(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.battat_is_tudongsudungkynang()

    def battat_tudongtheosautruongnhom(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.battat_is_tudongtheosautruongnhom()

    def thietlaptenmuctieutancong(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            tenmuctieutancong = self.moitruong.get_tennhanvatchichuot()
            self.tactu.set_tenmuctieutancong(tenmuctieutancong)

    def themdiemdanhxungquanh(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.thietlap_diemdanhxungquanh((self.moitruong.get_toadox(), self.moitruong.get_toadoy()))

    def xoatoanbodiemdanhxungquanh(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.thietlap_diemdanhxungquanh(False)

    def thietlapchidanhnguoichoi(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.thietlap_chidanhnguoichoi(True)

    def bothietlapchidanhnguoichoi(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.thietlap_chidanhnguoichoi(False)