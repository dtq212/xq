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

        self._is_tudongbattheosaunhom = True
        self._is_tudongtimkiemmuctieu = True
        self._is_tudongsudungkynang = True
        self._is_tudonggiukhoangcachtruongnhom = True

        self._khoangcachtoidatruongnhom = 6

        self._is_uutiennguoichoi = True

        self._tenmuctieutancong = False

        self.thoidiemsudungkynangphimtatgannhat_map = {}
        self.thoidiembattattheosaunhomgannhat = time.time() - 0.5

    def __del__(self):
        try:
            pass
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass

    def luuthietlap(self, tennhanvat):
        thietlap = {
            "_is_tudongbattheosaunhom": self._is_tudongbattheosaunhom,
            "_is_tudongtimkiemmuctieu": self._is_tudongtimkiemmuctieu,
            "_is_tudongsudungkynang": self._is_tudongsudungkynang,
            "_is_uutiennguoichoi": self._is_uutiennguoichoi,
        }

        util_luuthietlap(tennhanvat, thietlap)

    def taithietlap(self, tennhanvat):
        thietlap = util_taithietlap(tennhanvat)
        if thietlap:
            if "_is_tudongbattheosaunhom" in thietlap:
                self._is_tudongbattheosaunhom = thietlap["_is_tudongbattheosaunhom"]

            if "_is_tudongtimkiemmuctieu" in thietlap:
                self._is_tudongtimkiemmuctieu = thietlap["_is_tudongtimkiemmuctieu"]

            if "_is_tudongsudungkynang" in thietlap:
                self._is_tudongsudungkynang = thietlap["_is_tudongsudungkynang"]

            if "_is_uutiennguoichoi" in thietlap:
                self._is_uutiennguoichoi = thietlap["_is_uutiennguoichoi"]

    def action_tudongbattheosaunhom(self):
        if self._is_tudongbattheosaunhom:
            if time.time() - self.thoidiembattattheosaunhomgannhat < 1:
                return

            if self.moitruong.get_is_dangtheosaunhom():
                return

            if not self.moitruong.get_is_dangotrongnhom():
                return

            if self.moitruong.get_is_truongnhom():
                return

            self.thoidiembattattheosaunhomgannhat = time.time()

            self.moitruong.action_battattheosaunhom(delay = 1)

    def action_tudonggiukhoangcachtruongnhom(self):
        is_tamngungtancong = False
        if self._is_tudonggiukhoangcachtruongnhom:
            while True:
                if not self.moitruong.get_is_dangtheosaunhom():
                    break

                if not self.moitruong.get_is_dangotrongnhom():
                    break

                if self.moitruong.get_is_truongnhom():
                    break

                diachicosothongtintruongnhom = self.moitruong.get_diachicosothongtintruongnhom()
                if not diachicosothongtintruongnhom:
                    break

                idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

                khoangcachtoidatruongnhom = self._khoangcachtoidatruongnhom

                khoangcachtruongnhom = self.moitruong.get_khoangcach(diachicosothongtintruongnhom)
                if khoangcachtruongnhom <= khoangcachtoidatruongnhom:
                    break

                if khoangcachtruongnhom >= 20:
                    break

                is_tamngungtancong = True

                if idtuthenhanvat == 6:
                    self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_0)
                else:
                    self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_1)

                self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtintruongnhom, khoangcachtoidatruongnhom)

                break
        self.moitruong.set_is_tamngungtancong(is_tamngungtancong)


    def action_tudongtimkiemmuctieu(self):
        if self._is_tudongtimkiemmuctieu:
            i = 0

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

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
                    if idloainhanvatmuctieuxemxet == LOAIMUCTIEU_NGUOICHOICOTHETANCONG:
                        if idloainhanvatmuctieudangchon != LOAIMUCTIEU_NGUOICHOICOTHETANCONG:
                            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                            continue
                    elif idloainhanvatmuctieudangchon == LOAIMUCTIEU_NGUOICHOICOTHETANCONG:
                        continue

                khoangcachmuctieuxemxet = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet)
                if khoangcachmuctieuxemxet >= 15:
                    continue

                if khoangcachmuctieuxemxet < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                    continue

    def action_tudongsudungkynang(self):
        if self._is_tudongsudungkynang:
            if self.moitruong.get_is_batenter():
                return
            if self.moitruong.get_idtrangthaichuot() == TRANGTHAICHUOT_KHOANHVUNGKYNANG:
                return
            if self.moitruong.get_is_dangclickchuottrai():
                return
            if self.moitruong.get_is_tamngungtancong():
                return

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            if not diachicosothongtinnhanvatmuctieudangchon:
                return
            if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                return

            khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

            if khoangcach <= 8 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN) and self.moitruong.get_idloainhanvat(diachicosothongtinnhanvatmuctieudangchon) == LOAIMUCTIEU_QUAIVATHOACNPC and self.moitruong.get_idtuthenhanvat() != TUTHENHANVAT_DICHUYEN:
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN, is_khongcanmuctieu = True)
            elif khoangcach <= 8 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG):
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LUUTINHTRUYMANG)
            elif khoangcach <= 1:
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LUCPHACHHOASON)
                elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONDAOTRUCNHAP):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DONDAOTRUCNHAP)
                elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_PHAMATRAM)
                elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_PHAKHONGKICH)
            elif khoangcach <= 8:
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LANGKHONGCHIHUYET):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LANGKHONGCHIHUYET)
                elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGTAMTHUC):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BANGTAMTHUC)
                elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANKIEMXUYENTAM):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_VANKIEMXUYENTAM)
                elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANVUTIEUDIEU):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_VANVUTIEUDIEU)
                elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMTHUAT):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMTHUAT)
            elif khoangcach <= 15:
                self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon)

            # if self.moitruong.get_idloainhanvat(diachicosothongtinnhanvatmuctieudangchon) == LOAIMUCTIEU_NGUOICHOICOTHETANCONG and self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon) >= 5:
            #     for vitrikynang in (VITRIPHIMTATKYNANG_A, VITRIPHIMTATKYNANG_S, VITRIPHIMTATKYNANG_D, VITRIPHIMTATKYNANG_Q):
            #         if vitrikynang in self.thoidiemsudungkynangphimtatgannhat_map and time.time() - self.thoidiemsudungkynangphimtatgannhat_map[vitrikynang] < 0.5:
            #             continue
            #         self.thoidiemsudungkynangphimtatgannhat_map[vitrikynang] = time.time()
            #         self.moitruong.action_sudungkynangphimtat(vitrikynang)
            #         break
            # else:
            #     for vitrikynang in (VITRIPHIMTATKYNANG_Q, VITRIPHIMTATKYNANG_W, VITRIPHIMTATKYNANG_E, VITRIPHIMTATKYNANG_R):
            #         if vitrikynang in self.thoidiemsudungkynangphimtatgannhat_map and time.time() - self.thoidiemsudungkynangphimtatgannhat_map[vitrikynang] < 0.5:
            #             continue
            #         self.thoidiemsudungkynangphimtatgannhat_map[vitrikynang] = time.time()
            #         self.moitruong.action_sudungkynangphimtat(vitrikynang)
            #         break

    def battat_is_tudongsudungkynang(self):
        self._is_tudongsudungkynang = not self._is_tudongsudungkynang
        if self._is_tudongsudungkynang:
            phatam("Bật tự động sử dụng kỹ năng")
        else:
            phatam("Tắt tự động sử dụng kỹ năng")

    def battat_is_tudongbattheosaunhom(self):
        self._is_tudongbattheosaunhom = not self._is_tudongbattheosaunhom
        if self._is_tudongbattheosaunhom:
            phatam("Bật tự động theo sau nhóm")
        else:
            phatam("Tắt tự động theo sau nhóm")

    def set_tenmuctieutancong(self, tenmuctieutancong):
        if self._tenmuctieutancong != tenmuctieutancong:
            self._tenmuctieutancong = tenmuctieutancong
