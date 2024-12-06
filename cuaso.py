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

def khoidong_loopsudungvatpham(moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
    luong = LoopSuDungVatPham(moitruong, tactu, stop)
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
            threading.Thread(target = khoidong_loopsudungvatpham, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopchinh, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopphu, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),

        )

        for luong in self.luongs:
            luong.start()

        self.systray = SysTrayIcon(os.path.join("_internal", "icon", "icon.ico"), CHUACHONHANVAT, on_quit = self.tatauto)
        self.systray.start()

        keyboard.add_hotkey("ctrl + f", self.battat_tudongsudungkynang)
        keyboard.add_hotkey("ctrl + c", self.themtenmuctieutancong)
        keyboard.add_hotkey("ctrl + alt+ c", self.botoanbotenmuctieutancong)
        keyboard.add_hotkey("ctrl + alt + f", self.battat_tudongtheosautruongnhom)

        keyboard.add_hotkey("ctrl + d", self.thietlapchidanhnguoichoi)
        keyboard.add_hotkey("ctrl + a", self.bothietlapchidanhnguoichoi)

        keyboard.add_hotkey("ctrl + p", self.themdiemdanhxungquanh)
        keyboard.add_hotkey("ctrl + alt + shift + p", self.battat_tudongdichuyendiemdanhxungquanh)
        keyboard.add_hotkey("ctrl + alt + p", self.botoanbodiemdanhxungquanh)

        keyboard.add_hotkey("ctrl + m", self.battat_vohieuhoadichuyen)
        keyboard.add_hotkey("ctrl + alt + y", self.battat_tudongdichientruong)
        keyboard.add_hotkey("ctrl + alt + b", self.battat_tudongdibatquaitran)
        keyboard.add_hotkey("ctrl + alt + t", self.battat_tudongbattheosaunhom)

        keyboard.add_hotkey("ctrl + alt + e", self.action_tudongepdo)
        keyboard.add_hotkey("ctrl + e", self.action_tudongepdomotlan)

        self.thoidiemluuthietlapgannhat = time.time()

    def __del__(self):
        self.main_stop.set()


        keyboard.remove_hotkey("ctrl + f")
        keyboard.remove_hotkey("ctrl + c")
        keyboard.remove_hotkey("ctrl + alt+ c")
        keyboard.remove_hotkey("ctrl + alt + f")

        keyboard.remove_hotkey("ctrl + d")
        keyboard.remove_hotkey("ctrl + a")

        keyboard.remove_hotkey("ctrl + p")
        keyboard.remove_hotkey("ctrl + alt + p")

        keyboard.remove_hotkey("ctrl + m")
        keyboard.remove_hotkey("ctrl + alt + y")
        keyboard.remove_hotkey("ctrl + alt + b")
        keyboard.remove_hotkey("ctrl + alt + t")

        keyboard.remove_hotkey("ctrl + alt + e")
        keyboard.remove_hotkey("ctrl + e")


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

    def battat_vohieuhoadichuyen(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.battat_is_vohieuhoadichuyen()

    def battat_tudongdichientruong(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.battat_is_tudongdichientruong()

    def battat_tudongdibatquaitran(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.battat_is_tudongdibatquaitran()

    def battat_tudongbattheosaunhom(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.battat_is_tudongbattheosaunhom()

    def battat_tudongdichuyendiemdanhxungquanh(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.battat_is_tudongdichuyendiemdanhxungquanh()

    def action_tudongepdo(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.action_tudongepdo()

    def action_tudongepdomotlan(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.action_tudongepdomotlan()

    def themtenmuctieutancong(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            tenmuctieutancong = self.moitruong.get_tennhanvatchichuot()
            self.tactu.them_tenmuctieutancong(tenmuctieutancong)

    def botoanbotenmuctieutancong(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.botoanbo_tenmuctieutancong()

    def themdiemdanhxungquanh(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            if self.moitruong.get_is_dangmobando():
                self.tactu.them_diemdanhxungquanh((self.moitruong.get_toadoxbandochichuot(), self.moitruong.get_toadoybandochichuot(), self.moitruong.get_idbandochichuot()))
            else:
                self.tactu.them_diemdanhxungquanh((self.moitruong.get_toadox(is_vitrihientai = True), self.moitruong.get_toadoy(is_vitrihientai = True), self.moitruong.get_idbandohientai()))

    def botoanbodiemdanhxungquanh(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.botoanbo_diemdanhxungquanh()

    def thietlapchidanhnguoichoi(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.thietlap_chidanhnguoichoi(True)

    def bothietlapchidanhnguoichoi(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.thietlap_chidanhnguoichoi(False)