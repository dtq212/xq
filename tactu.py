import random
import time

import pymem

from hangso import LOAIMUCTIEU_NGUOICHOICOTHETANCONG
from moitruong import MoiTruong
from tienich import taithietlap as util_taithietlap
from tienich import luuthietlap as util_luuthietlap

class TacTu:
    def __init__(self, moitruong: MoiTruong):
        self.moitruong = moitruong

        self._is_tudongtheosaunhom = True
        self._is_tudongtimkiemmuctieu = True

        self._is_uutiennguoichoi = True

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

            if self.moitruong.get_is_doitruong():
                return

            self.thoidiembattattheosaunhomgannhat = time.time()

            self.moitruong.action_battattheosaunhom(delay = 2)

    def action_tudongtimkiemmuctieu(self):
        if self._is_tudongtimkiemmuctieu:
            for diachicosothongtinnhanvatmuctieuxemxet in self.moitruong.get_danhsachdiachicosothongtinnhanvats():
                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if diachicosothongtinnhanvatmuctieuxemxet == diachicosothongtinnhanvatmuctieudangchon:
                    continue

                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                    continue

                idloainhanvatmuctieudangchon = self.moitruong.get_idloainhanvat(diachicosothongtinnhanvatmuctieudangchon)

                if self._is_uutiennguoichoi and idloainhanvatmuctieudangchon != LOAIMUCTIEU_NGUOICHOICOTHETANCONG:
                    idloainhanvatmuctieuxemxet = self.moitruong.get_idloainhanvat(diachicosothongtinnhanvatmuctieuxemxet)
                    if idloainhanvatmuctieuxemxet == LOAIMUCTIEU_NGUOICHOICOTHETANCONG:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                        continue

                if self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet) < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                    continue