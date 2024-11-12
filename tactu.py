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
        self._is_tudongtheosautruongnhom = True
        self._is_tudongsudungvatpham = True
        self._is_tudongnhatdo = True

        self._khoangcachtoidatruongnhom = 4

        self._is_uutiennguoichoi = True

        self._tenmuctieutancong = False

        self.thoidiemsudungkynangphimtatgannhat_map = {}
        self.thoidiembattattheosaunhomgannhat = time.time()
        self.thoidiemsudungkynangkhaithientichdiagannhat = time.time()
        self.thoidiemsudungkynangluutinhtruymanggannhat = time.time()
        self._is_sudungkynangtieuchuthien = False
        self.thoidiemkiemtrahieuunggannhat = time.time()

        self.thoidiemtudongsudungvatphamgannhat = time.time()
        self.thoidiemtudongsudungvatphamgannhat_map = {}

        self._diemdanhxungquanh = False
        self._khoangcachdiemdanhxungquanh = 27.
        self._is_vuotquadiemdanhxungquanh = False

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

    def action_tudongtheosautruongnhom(self):
        is_tamngungtancongtheosautruongnhom = False
        if self._is_tudongtheosautruongnhom:
            while True:
                if self.moitruong.get_is_batenter():
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if not self.moitruong.get_is_dangotrongnhom():
                    break

                if self.moitruong.get_is_truongnhom():
                    break

                diachicosothongtintruongnhom = self.moitruong.get_diachicosothongtintruongnhom()
                if not diachicosothongtintruongnhom:
                    break

                idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

                khoangcachtruongnhom = self.moitruong.get_khoangcach(diachicosothongtintruongnhom)
                if khoangcachtruongnhom <= self._khoangcachtoidatruongnhom:
                    break

                if khoangcachtruongnhom >= KHOANGCACHTOIDAHOPLE:
                    break

                is_tamngungtancongtheosautruongnhom = True

                if idtuthenhanvat == TUTHENHANVAT_TANCONG and self.moitruong.get_is_thietlapkynangphimtat(VITRIPHIMTATKYNANG_THUCUOI):
                    self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_THUCUOI, delay = 2)
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and time.time() - self.thoidiemsudungkynangkhaithientichdiagannhat > 1.0:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KHAITHIENTICHDIA, HINHTHUCSUDUNGKYNANG_CANKHOANHVUNG)
                    self.moitruong.action_chonvungsudungkynangphudau(diachicosothongtintruongnhom, khoangcachphudau = 0)
                    self.thoidiemsudungkynangkhaithientichdiagannhat = time.time()
                else:
                    self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtintruongnhom, self._khoangcachtoidatruongnhom)

                break
        self._is_tamngungtancongtheosautruongnhom = is_tamngungtancongtheosautruongnhom


    def action_tudongtimkiemmuctieu(self):
        if self._is_tudongtimkiemmuctieu:
            i = 0

            while True:
                if self._is_sudungkynangtieuchuthien:
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(self.moitruong.get_diachicosothongtinnhanvat1())
                    break

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

                diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtinnhanvatmuctieuxemxet:
                    break

                i += 1

                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                if self._tenmuctieutancong:
                    if self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet) != self._tenmuctieutancong:
                        continue

                khoangcachmuctieuxemxet = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet)
                if khoangcachmuctieuxemxet >= KHOANGCACHTOIDAHOPLE:
                    continue

                if diachicosothongtinnhanvatmuctieuxemxet == diachicosothongtinnhanvatmuctieudangchon:
                    continue

                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                    continue

                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

                if self._is_uutiennguoichoi:
                    is_muctieudangxemxetlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieuxemxet)
                    if is_muctieudangxemxetlanguoichoi:
                        if not is_muctieudangchonlanguoichoi:
                            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                            continue
                    elif is_muctieudangchonlanguoichoi:
                        continue

                if khoangcachmuctieuxemxet < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                    continue

    def action_tudongsudungvatpham(self):
        if self._is_tudongsudungvatpham:
            if self.moitruong.get_is_nhanvatdachet():
                return

            if time.time() - self.thoidiemkiemtrahieuunggannhat < 5.:
                return

            self.thoidiemkiemtrahieuunggannhat = time.time()

            if not self.moitruong.get_is_cohieuung(HIEUUNGKYNANG_TIEUHUYETTHACH, True) and self.moitruong.get_is_thietlapkynangphimtat(VITRIPHIMTATKYNANG_HUYETTHACH):
                self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_HUYETTHACH)
                return

            if not self.moitruong.get_is_cohieuung(HIEUUNGKYNANG_TIEUPHAPLUCTHACH, True) and self.moitruong.get_is_thietlapkynangphimtat(VITRIPHIMTATKYNANG_PHAPLUCTHACH):
                self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_PHAPLUCTHACH)
                return


    def action_tudongsudungkynang(self):
        is_sudungkynangtieuchuthien = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongtheosautruongnhom:
                    break
                if self._is_vuotquadiemdanhxungquanh:
                    break
                if self.moitruong.get_is_batenter():
                    break
                if self.moitruong.get_is_dangclickchuottrai():
                    break
                if self.moitruong.get_is_nhanvatdachet():
                    break

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if not self.moitruong.get_is_cohieuung(HIEUUNGKYNANG_NGOAIKHANG, True) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    is_sudungkynangtieuchuthien = True
                    if diachicosothongtinnhanvatmuctieudangchon and diachicosothongtinnhanvatmuctieudangchon == self.moitruong.get_diachicosothongtinnhanvat1():
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIEUCHUTHIEN)
                    break

                if not diachicosothongtinnhanvatmuctieudangchon:
                    break
                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

                if is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH, HINHTHUCSUDUNGKYNANG_KHONGCANMUCTIEU)
                elif khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG) and time.time() - self.thoidiemsudungkynangluutinhtruymanggannhat > 1.0:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LUUTINHTRUYMANG)
                    self.thoidiemsudungkynangluutinhtruymanggannhat = time.time()
                elif KHOANGCACHSUDUNGKYNANGCANCHIEN < khoangcach <= KHOANGCACHHIEUQUAKYNANGKHAITHIENTICHDIA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and time.time() - self.thoidiemsudungkynangkhaithientichdiagannhat > 1.0:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KHAITHIENTICHDIA, HINHTHUCSUDUNGKYNANG_CANKHOANHVUNG)
                    self.moitruong.action_chonvungsudungkynangphudau(diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = 2)
                    self.thoidiemsudungkynangkhaithientichdiagannhat = time.time()
                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    if not is_muctieudangchonlanguoichoi:
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONDAOTRUCNHAP):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DONDAOTRUCNHAP)
                        elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_PHAKHONGKICH)
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONDAOTRUCNHAP):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DONDAOTRUCNHAP)
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LUCPHACHHOASON)
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_PHAMATRAM)
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_PHAKHONGKICH)
                elif khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LANGKHONGCHIHUYET):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LANGKHONGCHIHUYET)
                elif khoangcach <= KHOANGCACHTOIDAHOPLE:
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and time.time() - self.thoidiemsudungkynangkhaithientichdiagannhat > 1.0:
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KHAITHIENTICHDIA, HINHTHUCSUDUNGKYNANG_CANKHOANHVUNG)
                        self.moitruong.action_chonvungsudungkynangphudau(diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = 2)
                        self.thoidiemsudungkynangkhaithientichdiagannhat = time.time()
                    elif self.moitruong.get_idtuthenhanvat() != TUTHENHANVAT_TANCONG:
                        self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvatmuctieudangchon, KHOANGCACHSUDUNGKYNANGCANCHIEN)
                break

        self._is_sudungkynangtieuchuthien = is_sudungkynangtieuchuthien

    def battat_is_tudongsudungkynang(self):
        self._is_tudongsudungkynang = not self._is_tudongsudungkynang
        if self._is_tudongsudungkynang:
            phatam("Bật tự động sử dụng kỹ năng")
        else:
            phatam("Tắt tự động sử dụng kỹ năng")

    def battat_is_tudongbattheosaunhom(self):
        self._is_tudongbattheosaunhom = not self._is_tudongbattheosaunhom
        if self._is_tudongbattheosaunhom:
            phatam("Bật tự động bật tắt theo sau nhóm")
        else:
            phatam("Tắt tự động bật tắt theo sau nhóm")

    def battat_is_tudongtheosautruongnhom(self):
        self._is_tudongtheosautruongnhom = not self._is_tudongtheosautruongnhom
        if self._is_tudongtheosautruongnhom:
            phatam("Bật tự động theo sau trưởng nhóm")
        else:
            phatam("Tắt tự động theo sau trưởng nhóm")

    def set_tenmuctieutancong(self, tenmuctieutancong):
        if self._tenmuctieutancong != tenmuctieutancong:
            self._tenmuctieutancong = tenmuctieutancong

            if self._tenmuctieutancong:
                phatam("Thiết lập tên mục tiêu tấn công")
            else:
                phatam("Bỏ thiết lập tên mục tiêu tấn công")

    def action_tudongnhatdo(self):
        if self._is_tudongnhatdo:
            self.moitruong.action_nhatdo()

    def action_tudongdichuyenxungquanhdiem(self):
        is_vuotquadiemdanhxungquanh = False
        if self._diemdanhxungquanh:
            while True:
                khoangcach = self.moitruong.get_khoangcachdiem(self._diemdanhxungquanh)
                if khoangcach <= self._khoangcachdiemdanhxungquanh:
                    break

                is_vuotquadiemdanhxungquanh = True

                break
        self._is_vuotquadiemdanhxungquanh = is_vuotquadiemdanhxungquanh

    def thietlap_diemdanhxungquanh(self, diemdanhxungquanh):
        if not diemdanhxungquanh:
            self._diemdanhxungquanh = False
            phatam("Bỏ thiết lập thành công điểm đánh xung quanh")
        else:
            self._diemdanhxungquanh = diemdanhxungquanh
            phatam("Thiết lập thành công điểm đánh xung quanh")
