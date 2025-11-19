import os
import threading
import time
import keyboard
import win32gui
from infi.systray import SysTrayIcon

# Import các module nội bộ (Đảm bảo loop.py đã sửa lỗi Circular Import)
from loop import (
    LoopLamMoiTrangThaiMoiTruong,
    LoopTimKiemMucTieu,
    LoopSuDungVatPham,
    LoopChinh,
    LoopPhu,
    LoopDieuPhoiDiChuyen
)
from moitruong import MoiTruong
from tactu import TacTu
from hangso import *

def khoidong_looplammoitrangthaimoitruong(moitruong, tactu, stop):
    LoopLamMoiTrangThaiMoiTruong(moitruong, tactu, stop).loop()


def khoidong_looptimkiemmuctieu(moitruong, tactu, stop):
    LoopTimKiemMucTieu(moitruong, tactu, stop).loop()


def khoidong_loopsudungvatpham(moitruong, tactu, stop):
    LoopSuDungVatPham(moitruong, tactu, stop).loop()


def khoidong_loopchinh(moitruong, tactu, stop):
    LoopChinh(moitruong, tactu, stop).loop()


def khoidong_loopphu(moitruong, tactu, stop):
    LoopPhu(moitruong, tactu, stop).loop()


def khoidong_loopdieuphoidichuyen(moitruong, tactu, stop):
    LoopDieuPhoiDiChuyen(moitruong, tactu, stop).loop()


class CuaSo:
    def __init__(self, idcuaso):
        self.moitruong = MoiTruong(idcuaso)
        self.tactu = TacTu(self.moitruong)
        self.tennhanvat = False
        self.main_stop = threading.Event()
        self.hotkeys = []

        self.luongs = (
            threading.Thread(target = khoidong_looplammoitrangthaimoitruong, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_looptimkiemmuctieu, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopsudungvatpham, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopchinh, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopphu, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopdieuphoidichuyen, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
        )

        for luong in self.luongs:
            luong.start()

        icon_path = os.path.join("_internal", "icon", "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = None

        title_ban_dau = f"{CHUACHONHANVAT} ({idcuaso})"
        self.systray = SysTrayIcon(icon_path, title_ban_dau, on_quit = self.tatauto)
        self.systray.start()

        self.dang_ky_hotkey("ctrl + f", self.battat_tudongsudungkynang)
        self.dang_ky_hotkey("ctrl + c", self.themtenmuctieutancong)
        self.dang_ky_hotkey("ctrl + alt + c", self.botoanbotenmuctieutancong)
        self.dang_ky_hotkey("ctrl + x", self.themtenmuctieukhongtancong)
        self.dang_ky_hotkey("ctrl + alt + x", self.botoanbotenmuctieukhongtancong)
        self.dang_ky_hotkey("ctrl + alt + f", self.battat_tudongtheosautruongnhom)
        self.dang_ky_hotkey("ctrl + d", self.thietlapchidanhnguoichoi)
        self.dang_ky_hotkey("ctrl + a", self.bothietlapchidanhnguoichoi)
        self.dang_ky_hotkey("ctrl + e", self.batpk)
        self.dang_ky_hotkey("ctrl + q", self.tatpk)
        self.dang_ky_hotkey("ctrl + p", self.themdiemdanhxungquanh)
        self.dang_ky_hotkey("ctrl + alt + shift + p", self.battat_tudongdichuyendiemdanhxungquanh)
        self.dang_ky_hotkey("ctrl + alt + p", self.botoanbodiemdanhxungquanh)
        self.dang_ky_hotkey("ctrl + m", self.battat_vohieuhoadichuyen)
        self.dang_ky_hotkey("ctrl + alt + t", self.battat_tudongbattheosaunhom)
        self.dang_ky_hotkey("ctrl + alt + d", self.battat_thucsondao)
        self.dang_ky_hotkey("ctrl + alt + v", self.battat_is_phitac)
        self.dang_ky_hotkey("ctrl + alt + shift + c", self.battat_chantangcapdo)

        self.thoidiemluuthietlapgannhat = time.time()

    def dang_ky_hotkey(self, phim, ham):
        hook = keyboard.add_hotkey(phim, ham)
        self.hotkeys.append(hook)

    def __del__(self):
        self.tatauto()

    def _chotoanbocacluongdunghan(self):
        for luong in self.luongs:
            if luong.is_alive():
                luong.join(timeout = 0.2)

    def tatauto(self, *args, **kwargs):
        self.main_stop.set()

        for hook in self.hotkeys:
            try:
                keyboard.remove_hotkey(hook)
            except:
                pass
        self.hotkeys.clear()

        self._chotoanbocacluongdunghan()

        try:
            self.systray.shutdown()
        except:
            pass

    def loop(self):
        last_hover_text = None
        while not self.main_stop.is_set() and self.moitruong.get_is_cuasogametontai():
            if not self.moitruong.get_is_dangmatketnoi():
                tennhanvat = self.moitruong.get_tendoituong()

                if tennhanvat != self.tennhanvat:
                    if tennhanvat:
                        if self.tennhanvat:
                            self.tactu.luuthietlap(self.tennhanvat)
                        self.tactu.taithietlap(tennhanvat)

                        if tennhanvat != last_hover_text:
                            self.systray.update(hover_text = tennhanvat)
                            last_hover_text = tennhanvat
                    elif self.tennhanvat:
                        self.tactu.luuthietlap(self.tennhanvat)
                        if CHUACHONHANVAT != last_hover_text:
                            self.systray.update(hover_text = CHUACHONHANVAT)
                            last_hover_text = CHUACHONHANVAT

                    self.tennhanvat = tennhanvat

                elif tennhanvat and time.time() - self.thoidiemluuthietlapgannhat > 1.:
                    self.thoidiemluuthietlapgannhat = time.time()
                    self.tactu.luuthietlap(tennhanvat)
            else:
                # Mất kết nối
                self.tennhanvat = False
                if CHUACHONHANVAT != last_hover_text:
                    self.systray.update(hover_text = CHUACHONHANVAT)
                    last_hover_text = CHUACHONHANVAT

            time.sleep(1)

        self.tatauto()

    def battat_tudongsudungkynang(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.battat_is_tudongsudungkynang()

    def battat_tudongtheosautruongnhom(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.battat_is_tudongtheosautruongnhom()

    def battat_vohieuhoadichuyen(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.battat_is_vohieuhoadichuyen()

    def battat_tudongbattheosaunhom(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.battat_is_tudongbattheosaunhom()

    def battat_is_phitac(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.battat_is_phitac()

    def battat_thucsondao(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.battat_is_thucsondao()

    def battat_tudongdichuyendiemdanhxungquanh(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.battat_is_tudongdichuyendiemdanhxungquanh()

    def battat_chantangcapdo(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.battat_is_chantangcapdo()

    def themtenmuctieutancong(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.them_tenmuctieutancong(self.moitruong.get_tennhanvatchichuot())

    def themtenmuctieukhongtancong(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            self.tactu.them_tenmuctieukhongtancong(self.moitruong.get_tennhanvatchichuot())

    def botoanbotenmuctieutancong(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.botoanbo_tenmuctieutancong()

    def botoanbotenmuctieukhongtancong(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.botoanbo_tenmuctieukhongtancong()

    def themdiemdanhxungquanh(self):
        if self.moitruong.get_is_cuasogamekichhoat():
            if self.moitruong.get_is_dangmobando():
                self.tactu.them_diemdanhxungquanh((self.moitruong.get_toadoxbandochichuot(), self.moitruong.get_toadoybandochichuot(), self.moitruong.get_idbandochichuot()))
            else:
                self.tactu.them_diemdanhxungquanh((self.moitruong.get_toadox(is_vitrihientai = True), self.moitruong.get_toadoy(is_vitrihientai = True), self.moitruong.get_idbandohientai()))

    def botoanbodiemdanhxungquanh(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.botoanbo_diemdanhxungquanh()

    def thietlapchidanhnguoichoi(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.thietlap_chidanhnguoichoi(True)

    def bothietlapchidanhnguoichoi(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.thietlap_chidanhnguoichoi(False)

    def batpk(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.action_batpk()

    def tatpk(self):
        if self.moitruong.get_is_cuasogamekichhoat(): self.tactu.action_tatpk()