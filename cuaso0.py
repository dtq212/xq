import os
import threading
import time

import keyboard
from infi.systray import SysTrayIcon

from hangso import *
from loop import (
    LoopLamMoiTrangThaiMoiTruong,
    LoopTimKiemMucTieu,
    LoopChinh,
    LoopPhu,
    LoopDieuPhoiDiChuyen
)
from moitruong import MoiTruong
from tactu import TacTu


def khoidong_looplammoitrangthaimoitruong(moitruong, tactu, stop):
    LoopLamMoiTrangThaiMoiTruong(moitruong, tactu, stop).loop()


def khoidong_looptimkiemmuctieu(moitruong, tactu, stop):
    LoopTimKiemMucTieu(moitruong, tactu, stop).loop()

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

        self.luongs = (
            threading.Thread(target = khoidong_looplammoitrangthaimoitruong, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_looptimkiemmuctieu, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopchinh, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopphu, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopdieuphoidichuyen, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
        )

        for luong in self.luongs:
            luong.start()

        threading.Thread(target = self.loop_xulyphimtat, daemon = True).start()

        icon_path = os.path.join("_internal", "icon", "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = None

        title_ban_dau = f"{CHUACHONHANVAT} ({idcuaso})"
        self.systray = SysTrayIcon(icon_path, title_ban_dau, on_quit = self.tatauto)
        self.systray.start()

        self.thoidiemluuthietlapgannhat = time.time()

    def __del__(self):
        self.tatauto()

    def _chotoanbocacluongdunghan(self):
        for luong in self.luongs:
            if luong.is_alive():
                luong.join(timeout = 0.2)

    def tatauto(self, *args, **kwargs):
        self.main_stop.set()

        self._chotoanbocacluongdunghan()

        try:
            self.systray.shutdown()
        except:
            pass

    def loop(self):
        last_hover_text = None
        thoi_gian_mat_ket_noi = 0

        while not self.main_stop.is_set() and self.moitruong.get_is_cuasogametontai():
            if not self.moitruong.get_is_dangmatketnoi():
                thoi_gian_mat_ket_noi = 0
                tennhanvat = self.moitruong.get_tendoituong()

                if tennhanvat != self.tennhanvat:
                    if tennhanvat:
                        # if self.tennhanvat:
                        #     self.tactu.luuthietlap(self.tennhanvat)
                        self.tactu.taithietlap(tennhanvat)

                        if tennhanvat != last_hover_text:
                            self.systray.update(hover_text = tennhanvat)
                            last_hover_text = tennhanvat
                    elif self.tennhanvat:
                        # self.tactu.luuthietlap(self.tennhanvat)
                        if CHUACHONHANVAT != last_hover_text:
                            self.systray.update(hover_text = CHUACHONHANVAT)
                            last_hover_text = CHUACHONHANVAT

                    self.tennhanvat = tennhanvat

                elif tennhanvat and time.time() - self.thoidiemluuthietlapgannhat > 1.:
                    self.thoidiemluuthietlapgannhat = time.time()
                    # self.tactu.luuthietlap(tennhanvat)
            else:
                self.tennhanvat = False
                if CHUACHONHANVAT != last_hover_text:
                    self.systray.update(hover_text = CHUACHONHANVAT)
                    last_hover_text = CHUACHONHANVAT

                if thoi_gian_mat_ket_noi == 0:
                    thoi_gian_mat_ket_noi = time.time()
                elif time.time() - thoi_gian_mat_ket_noi > 1.:
                    break

            time.sleep(1)

        self.tatauto()

    def loop_xulyphimtat(self):
        while not self.main_stop.is_set():
            if self.moitruong.get_is_cuasogamekichhoat():

                if keyboard.is_pressed("ctrl+alt+shift+p"):
                    self.battat_tudongdichuyendiemdanhxungquanh()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+shift+c"):
                    self.battat_chantangcapdo()
                    time.sleep(0.3)
                elif keyboard.is_pressed("ctrl+alt+shift+k"):
                    self.battat_tudongkhaikhoang()
                    time.sleep(0.3)
                elif keyboard.is_pressed("ctrl+alt+shift+b"):
                    self.thuchien_tudongbanrac()
                    time.sleep(0.3)
                elif keyboard.is_pressed("ctrl+alt+c"):
                    self.botoanbotenmuctieutancong()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+x"):
                    self.botoanbotenmuctieukhongtancong()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+f"):
                    self.battat_tudongtheosautruongnhom()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+p"):
                    self.botoanbodiemdanhxungquanh()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+t"):
                    self.battat_tudongbattheosaunhom()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+d"):
                    self.battat_thucsondao()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+f"):
                    self.battat_tudongsudungkynang()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+c"):
                    self.themtenmuctieutancong()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+x"):
                    self.themtenmuctieukhongtancong()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+d"):
                    self.thietlapchidanhnguoichoi()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+a"):
                    self.bothietlapchidanhnguoichoi()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+e"):
                    self.batpk()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+q"):
                    self.tatpk()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+p"):
                    self.themdiemdanhxungquanh()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+shift+g"):
                    self.battat_tudonggomquai()
                    time.sleep(0.3)
                elif keyboard.is_pressed("ctrl+alt+shift+h"):
                    self.battat_tudongvebanrac()
                    time.sleep(0.3)
                elif keyboard.is_pressed("ctrl+alt+shift+z"):
                    self.battat_tudongdichientruong()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+s"):
                    self.battat_uutienbaothumaoson()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+shift+r"):
                    self.action_suado()
                    time.sleep(0.3)

                elif keyboard.is_pressed("ctrl+alt+shift+n"):
                    self.tactu.battat_chedobufftoanbang()
                    time.sleep(0.3)

            time.sleep(0.05)

    def battat_uutienbaothumaoson(self):
        self.tactu.battat_is_uutienbaothumaoson()

    def battat_tudongsudungkynang(self):
        self.tactu.battat_is_tudongsudungkynang()

    def battat_tudongtheosautruongnhom(self):
        self.tactu.battat_is_tudongtheosautruongnhom()

    def battat_tudongbattheosaunhom(self):
        self.tactu.battat_is_tudongbattheosaunhom()

    def battat_thucsondao(self):
        self.tactu.battat_is_thucsondao()

    def battat_tudongdichuyendiemdanhxungquanh(self):
        self.tactu.battat_is_tudongdichuyendiemdanhxungquanh()

    def battat_chantangcapdo(self):
        self.tactu.battat_is_chantangcapdo()

    def battat_tudongkhaikhoang(self):
        self.tactu.battat_is_tudongkhaikhoang()

    def thuchien_tudongbanrac(self):
        self.tactu.action_tudongbanrac()

    def themtenmuctieutancong(self):
        self.tactu.them_tenmuctieutancong(self.moitruong.get_tennhanvatchichuot())

    def themtenmuctieukhongtancong(self):
        self.tactu.them_tenmuctieukhongtancong(self.moitruong.get_tennhanvatchichuot())

    def botoanbotenmuctieutancong(self):
        self.tactu.botoanbo_tenmuctieutancong()

    def botoanbotenmuctieukhongtancong(self):
        self.tactu.botoanbo_tenmuctieukhongtancong()

    def themdiemdanhxungquanh(self):
        if self.moitruong.get_is_dangmobando():
            self.tactu.them_diemdanhxungquanh((self.moitruong.get_toadoxbandochichuot(), self.moitruong.get_toadoybandochichuot(), self.moitruong.get_idbandochichuot()))
        else:
            self.tactu.them_diemdanhxungquanh((self.moitruong.get_toadox(is_vitrihientai = True), self.moitruong.get_toadoy(is_vitrihientai = True), self.moitruong.get_idbandohientai()))

    def botoanbodiemdanhxungquanh(self):
        self.tactu.botoanbo_diemdanhxungquanh()

    def thietlapchidanhnguoichoi(self):
        self.tactu.thietlap_chidanhnguoichoi(True)

    def bothietlapchidanhnguoichoi(self):
        self.tactu.thietlap_chidanhnguoichoi(False)

    def batpk(self):
        self.tactu.action_batpk()

    def tatpk(self):
        self.tactu.action_tatpk()

    def battat_tudonggomquai(self):
        self.tactu.battat_tudonggomquai()

    def battat_tudongvebanrac(self):
        self.tactu.battat_tudongvebanrac()

    def battat_tudongdichientruong(self):
        self.tactu.battat_is_tudongdichientruong()

    def battat_tudonglamnhiemvusugia(self):
        self.tactu.battat_is_tudonglamnhiemvusugia()

    def action_suado(self):
        self.tactu.action_suado()