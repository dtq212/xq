import random
import time

import pymem

from hangso import *
from moitruong import MoiTruong
from tienich import taithietlap as util_taithietlap, phatam
from tienich import luuthietlap as util_luuthietlap

class TacTu:
    def __init__(self, moitruong: MoiTruong):
        self.moitruong = moitruong

        self._is_tudongtheosaunhom = True
        self._is_tudongtimkiemmuctieu = True
        self._is_tudongsudungkynang = True

        self._is_uutiennguoichoi = True

        self._tenmuctieutancong = False

        self.thoidiembattattheosaunhomgannhat = time.time() - 0.5

    def __del__(self):
        try:
            pass
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass
    
    def luuthietlap(self, tennhanvat):
        thietlap = {
            "_is_tudongtheosaunhom": self._is_tudongtheosaunhom,
            "_is_tudongtimkiemmuctieu": self._is_tudongtimkiemmuctieu,
            "_is_tudongsudungkynang": self._is_tudongsudungkynang,
            "_is_uutiennguoichoi": self._is_uutiennguoichoi,
        }

        util_luuthietlap(tennhanvat, thietlap)
    def taithietlap(self, tennhanvat):
        thietlap = util_taithietlap(tennhanvat)
        if thietlap:
            if "_is_tudongtheosaunhom" in thietlap:
                self._is_tudongtheosaunhom = thietlap["_is_tudongtheosaunhom"]

            if "_is_tudongtimkiemmuctieu" in thietlap:
                self._is_tudongtimkiemmuctieu = thietlap["_is_tudongtimkiemmuctieu"]

            if "_is_tudongsudungkynang" in thietlap:
                self._is_tudongsudungkynang = thietlap["_is_tudongsudungkynang"]

            if "_is_uutiennguoichoi" in thietlap:
                self._is_uutiennguoichoi = thietlap["_is_uutiennguoichoi"]

    def action_tudongtheosaunhom(self):
        if self._is_tudongtheosaunhom:
            if time.time() - self.thoidiembattattheosaunhomgannhat < 2:
                return

            if self.moitruong.get_is_dangtheosaunhom():
                return

            if not self.moitruong.get_is_dangotrongnhom():
                return

            if self.moitruong.get_is_truongnhom():
                return

            self.thoidiembattattheosaunhomgannhat = time.time()

            self.moitruong.action_battattheosaunhom(delay = 2)

    def action_tudongtimkiemmuctieu(self):
        if self._is_tudongtimkiemmuctieu:
            i = 0
            while True:
                diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtinnhanvatx(i)
                if not diachicosothongtinnhanvatmuctieuxemxet:
                    break

                i += 1

                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                if self._tenmuctieutancong:
                    if self.moitruong.get_tennhanvat(diachicosothongtinnhanvatmuctieuxemxet) != self._tenmuctieutancong:
                        continue

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if diachicosothongtinnhanvatmuctieuxemxet == diachicosothongtinnhanvatmuctieudangchon:
                    continue

                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                    continue

                idloainhanvatmuctieudangchon = self.moitruong.get_idloainhanvat(diachicosothongtinnhanvatmuctieudangchon)

                if self._is_uutiennguoichoi:
                    idloainhanvatmuctieuxemxet = self.moitruong.get_idloainhanvat(diachicosothongtinnhanvatmuctieuxemxet)
                    if idloainhanvatmuctieuxemxet == LOAIMUCTIEU_NGUOICHOICOTHETANCONG and idloainhanvatmuctieudangchon != LOAIMUCTIEU_NGUOICHOICOTHETANCONG:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                        continue

                if self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet) < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                    continue

    def action_tudongsudungkynang(self):
        if self._is_tudongsudungkynang:
            if self.moitruong.get_is_batspace():
                return
            if self.moitruong.get_idtrangthaichuot() == TRANGTHAICHUOT_KHOANHVUNGKYNANG:
                return
            if self.moitruong.get_is_dangclickchuottrai():
                return

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            if not diachicosothongtinnhanvatmuctieudangchon:
                return
            if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                return

            # khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
            # if khoangcach <= 2:
            for vitrikynang in (VITRIKYNANG_Q, VITRIKYNANG_W, VITRIKYNANG_E, VITRIKYNANG_R):
                self.moitruong.action_sudungkynangphimtat(vitrikynang)
                time.sleep(0.05)
            # else:
            #     for vitrikynang in (VITRIKYNANG_Q, VITRIKYNANG_A, VITRIKYNANG_S, VITRIKYNANG_D, VITRIKYNANG_F):
            #         self.moitruong.action_sudungkynangphimtat(vitrikynang)
            #         time.sleep(0.05)

    def battat_is_tudongsudungkynang(self):
        self._is_tudongsudungkynang = not self._is_tudongsudungkynang
        if self._is_tudongsudungkynang:
            phatam("Bật tự động sử dụng kỹ năng")
        else:
            phatam("Tắt tự động sử dụng kỹ năng")

    def battat_is_tudongtheosaunhom(self):
        self._is_tudongtheosaunhom = not self._is_tudongtheosaunhom
        if self._is_tudongtheosaunhom:
            phatam("Bật tự động theo sau nhóm")
        else:
            phatam("Tắt tự động theo sau nhóm")

    def set_tenmuctieutancong(self, tenmuctieutancong):
        if self._tenmuctieutancong != tenmuctieutancong:
            self._tenmuctieutancong = tenmuctieutancong