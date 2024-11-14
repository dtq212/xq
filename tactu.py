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

        #Thiết lập không lưu
        self._is_tudongtheosautruongnhom = True
        #Thiết lập có lưu
        self._is_tudongbattheosaunhom = True
        self._is_tudongtimkiemmuctieu = True
        self._is_tudongsudungkynang = True
        self._is_tudongsudungvatpham = True
        self._is_tudongnhatdo = True
        self._is_chidanhnguoichoi = False


        self._is_uutiennguoichoi = True

        self._khoangcachtoidatruongnhom = 6

        self._tenmuctieutancong = False

        self.thoidiembattattheosaunhomgannhat = time.time()
        self.thoidiemkiemtrahieuunggannhat = time.time()

        self._is_sudungkynanglenbanthan = False
        self._diemdanhxungquanh = False
        self._khoangcachdiemdanhxungquanh = 27.
        self._is_vuotquakhoangcachdiemdanhxungquanh = False
        self._is_tamngungtancongtheosautruongnhom = False
        self._is_tamngungtancongdichuyenxungquanh = False
        self._is_tamngungdichuyensudungkynang = False
        self._khoangcachtimkiemmuctieu = 18.

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
            "_is_tudongsudungvatpham": self._is_tudongsudungvatpham,
            "_is_tudongnhatdo": self._is_tudongnhatdo,
            "_is_chidanhnguoichoi": self._is_chidanhnguoichoi,
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

            if "_is_tudongsudungvatpham" in thietlap:
                self._is_tudongsudungvatpham = thietlap["_is_tudongsudungvatpham"]

            if "_is_tudongnhatdo" in thietlap:
                self._is_tudongnhatdo = thietlap["_is_tudongnhatdo"]

            if "_is_chidanhnguoichoi" in thietlap:
                self._is_chidanhnguoichoi = thietlap["_is_chidanhnguoichoi"]

    def action_tudongtheosautruongnhom(self):
        is_tamngungtancongtheosautruongnhom = False
        if self._is_tudongtheosautruongnhom:
            while True:
                if self._is_tamngungdichuyensudungkynang:
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                if not self.moitruong.get_is_dangnamtrongnhom():
                    break

                if self.moitruong.get_is_truongnhom():
                    break

                xtruongnhom = self.moitruong.get_toadoxtruongnhom()
                ytruongnhom = self.moitruong.get_toadoytruongnhom()

                if not xtruongnhom and not ytruongnhom:
                    break

                idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

                khoangcachtruongnhom = self.moitruong.get_khoangcachdiem(xtruongnhom, ytruongnhom)
                if khoangcachtruongnhom <= self._khoangcachtoidatruongnhom:
                    break

                if khoangcachtruongnhom >= KHOANGCACHTOIDAHOPLE:
                    break

                is_tamngungtancongtheosautruongnhom = True

                if idtuthenhanvat == TUTHENHANVAT_TANCONG and self.moitruong.get_is_thietlapkynangphimtat(VITRIPHIMTATKYNANG_THUCUOI):
                    self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_THUCUOI, delay = 2)
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and time.time() - self.moitruong.get_thoidiemsudungkynangvitrigannhat(*VITRIKYNANG_KHAITHIENTICHDIA, time.time() - 2.0) > 1.0:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KHAITHIENTICHDIA, HINHTHUCSUDUNGKYNANG_CANKHOANHVUNG)
                    self.moitruong.action_chonvungsudungkynangphudaudiem(xtruongnhom, ytruongnhom, khoangcachphudau = 0)
                else:
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(xtruongnhom, ytruongnhom, self._khoangcachtoidatruongnhom)

                break
        self._is_tamngungtancongtheosautruongnhom = is_tamngungtancongtheosautruongnhom


    def action_tudongtimkiemmuctieu(self):
        if self._is_tudongtimkiemmuctieu:
            i = 0

            while True:
                if self._is_sudungkynanglenbanthan:
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(self.moitruong.get_diachicosothongtinnhanvat1())
                    break

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                elif self._tenmuctieutancong and self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon) != self._tenmuctieutancong:
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                elif self._is_chidanhnguoichoi and not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon):
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
                if self._is_chidanhnguoichoi and not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                khoangcachmuctieuxemxet = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet)
                if khoangcachmuctieuxemxet >= self._khoangcachtimkiemmuctieu:
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

            if time.time() - self.thoidiemkiemtrahieuunggannhat < 2.5:
                return

            self.thoidiemkiemtrahieuunggannhat = time.time()

            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIEUHUYETTHACH, ), True, is_hieuungcoloi = 1) and self.moitruong.get_is_thietlapkynangphimtat(VITRIPHIMTATKYNANG_HUYETTHACH):
                    self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_HUYETTHACH)
                    return

            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIEUPHAPLUCTHACH, ), True, is_hieuungcoloi = 1) and self.moitruong.get_is_thietlapkynangphimtat(VITRIPHIMTATKYNANG_PHAPLUCTHACH):
                self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_PHAPLUCTHACH)
                return


    def action_tudongsudungkynang(self):
        is_sudungkynanglenbanthan = False
        is_tamngungdichuyensudungkynang = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongtheosautruongnhom:
                    break
                if self._is_tamngungtancongdichuyenxungquanh:
                    break
                if self.moitruong.get_is_dangclickchuottrai():
                    break
                if self.moitruong.get_is_nhanvatdachet():
                    break
                if self.moitruong.get_is_dangvankhi():
                    break

                idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, ), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    is_sudungkynanglenbanthan = True
                    is_tamngungdichuyensudungkynang = True
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(self.moitruong.get_diachicosothongtinnhanvat1())
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIEUCHUTHIEN)
                    break
                elif self.moitruong.get_phantramsinhlucconlai() <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    is_sudungkynanglenbanthan = True
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(self.moitruong.get_diachicosothongtinnhanvat1())
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENKHI)
                    break

                if not diachicosothongtinnhanvatmuctieudangchon:
                    break
                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

                if is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH, HINHTHUCSUDUNGKYNANG_KHONGCANMUCTIEU)
                    break

                is_muctieudangchonbichoang = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG) and time.time() - self.moitruong.get_thoidiemsudungkynangvitrigannhat(*VITRIKYNANG_LUUTINHTRUYMANG, time.time() - 2.0) > 1.0:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LUUTINHTRUYMANG)
                    break

                if KHOANGCACHSUDUNGKYNANGCANCHIEN < khoangcach <= KHOANGCACHHIEUQUAKYNANGKHAITHIENTICHDIA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and time.time() - self.moitruong.get_thoidiemsudungkynangvitrigannhat(*VITRIKYNANG_KHAITHIENTICHDIA, time.time() - 2.0) > 1.0:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KHAITHIENTICHDIA, HINHTHUCSUDUNGKYNANG_CANKHOANHVUNG)
                    self.moitruong.action_chonvungsudungkynangphudau(diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = 2)
                    break

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    if is_muctieudangchonlanguoichoi:
                        if not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LUCPHACHHOASON)
                            break
                        if self.moitruong.get_is_cohieuungcoloinhanvat(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_PHAMATRAM)
                            break
                    else:
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONDAOTRUCNHAP):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DONDAOTRUCNHAP)
                            break
                        if self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG, ), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_PHAKHONGKICH)
                            break

                    if self.moitruong.get_is_cohieuungbatloinhanvat():
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                            is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG):
                                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                            break

                    if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
                        self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon)
                    break

                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LANGKHONGCHIHUYET):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LANGKHONGCHIHUYET)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANKIEMXUYENTAM):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_VANKIEMXUYENTAM)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGTAMTHUC):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BANGTAMTHUC)
                        break

                    if self.moitruong.get_is_cohieuungbatloinhanvat():
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                            is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG):
                                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                            break

                    if khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN and idtuthenhanvat == TUTHENHANVAT_DUNGIM:
                        self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon) #Tiếp cận luôn thay vì chỉ chạy đến khoảng cách sử dụng kỹ năng cận chiến vì nhiều khi nó bị treo lắm
                    break

                if khoangcach <= KHOANGCACHTOIDAHOPLE:
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and time.time() - self.moitruong.get_thoidiemsudungkynangvitrigannhat(*VITRIKYNANG_KHAITHIENTICHDIA, time.time() - 2.0) > 1.0:
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KHAITHIENTICHDIA, HINHTHUCSUDUNGKYNANG_CANKHOANHVUNG)
                        self.moitruong.action_chonvungsudungkynangphudau(diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = 2)
                        break
                    if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
                        self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon) #Tiếp cận luôn thay vì chỉ chạy đến khoảng cách sử dụng kỹ năng tầm xa vì nhiều khi nó bị treo lắm
                    break

                break

        self._is_sudungkynanglenbanthan = is_sudungkynanglenbanthan
        self._is_tamngungdichuyensudungkynang = is_tamngungdichuyensudungkynang

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
        is_vuotquakhoangcachdiemdanhxungquanh = False
        is_tamngungtancongdichuyenxungquanh = False

        if self._diemdanhxungquanh:
            while True:
                khoangcach = self.moitruong.get_khoangcachdiem(*self._diemdanhxungquanh)
                if khoangcach > self._khoangcachdiemdanhxungquanh:
                    is_vuotquakhoangcachdiemdanhxungquanh = True

                if self._is_tamngungdichuyensudungkynang:
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                if not self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon() and time.time() - self.moitruong.get_thoidiemkhongcomuctieugannhat() > 2.5:
                    is_tamngungtancongdichuyenxungquanh = True
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(*self._diemdanhxungquanh, khoangcachtoida = 0)

                break

        self._is_vuotquakhoangcachdiemdanhxungquanh = is_vuotquakhoangcachdiemdanhxungquanh
        self._is_tamngungtancongdichuyenxungquanh = is_tamngungtancongdichuyenxungquanh

    def thietlap_diemdanhxungquanh(self, diemdanhxungquanh):
        if not diemdanhxungquanh:
            self._diemdanhxungquanh = False
            phatam("Bỏ thiết lập điểm đánh xung quanh")
        else:
            self._diemdanhxungquanh = diemdanhxungquanh
            phatam("Thiết lập điểm đánh xung quanh")

    def thietlap_chidanhnguoichoi(self, is_chidanhnguoichoi):
        self._is_chidanhnguoichoi = is_chidanhnguoichoi
        if not is_chidanhnguoichoi:
            phatam("Bỏ thiết lập chỉ đánh người chơi")
        else:
            phatam("Thiết lập chỉ đánh người chơi")
