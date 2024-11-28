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
        self._is_vohieuhoadichuyen = False
        #Thiết lập có lưu
        self._is_tudongbattheosaunhom = False
        self._is_tudongtimkiemmuctieu = True
        self._is_tudongsudungkynang = True
        self._is_tudongsudungvatpham = True
        self._is_tudongnhatdo = True
        self._is_chidanhnguoichoi = False
        self._is_tudongtodoi = True
        self._is_tudongphucsinh = True
        self._is_tudongsuado = True
        self._is_tudongdichientruong = False
        self._is_tudongtrieuhoibaothudautien = True

        self._is_uutiennguoichoi = True

        self._khoangcachtoidatruongnhom = 6

        self._tenmuctieutancongs = set()

        self._thoidiembattattheosaunhomgannhat = time.time()
        self._thoidiemkiemtrahieuunggannhat = time.time()
        self._thoidiemdichuyenkhacbandodichuyenxungquanhgannhat = time.time()
        self._thoidiemnhanvatchetgannhat = time.time()
        self._thoidiemthongbaotudongtimduonggannhat = time.time()
        self._thoidiemkiemtranpcsuadogannhat = time.time()
        self._thoidiemnhatdogannhat_map = {}
        self._thoidiemdoimaupkgannhat = time.time()
        self._thoidiemdichuyengiukhoangcachtoithieugannhat = time.time()
        self._thoidiemdichuyendiemdanhxungquanhgannhat = time.time()
        self._thoidiemdichuyentiepcangannhat = time.time()
        self._thoidiemyeucauroikhoichientruonggannhat = time.time()
        self._thoidiemtudongtrieuhoibaothudautien = time.time()
        self._thoidiemthietlapbaothuchodoigannhat = time.time()
        self._thoidiemkiemtradatrieuhoithanthugannhat = time.time()
        self._thoidiemsudungvatphamgannhat = time.time()
        self._thoidiemsudungthucanbaothugannhat = time.time()

        self._diemdanhxungquanhs = []
        self._khoangcachdiemdanhxungquanh = 27.
        self._is_tamngungtancongtheosautruongnhom = False
        self._is_tamngungtancongdichuyenxungquanh = False
        self._is_tamngungdichuyensudungkynang = False
        self._is_tamngungtancongdenhatdo = False
        self._is_tamngungdichuyendenhatdo = False
        self._is_tamngungnhatdodetheosautruongnhom = False
        self._khoangcachtimkiemmuctieu = 18.
        self._is_tudongtrieuhoithanthu = True

        self._idbandohientai = False
        self._phehientai = False

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
            "_is_tudongtodoi": self._is_tudongtodoi,
            # "_diemdanhxungquanhs": self._diemdanhxungquanhs,
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

            if "_is_tudongtodoi" in thietlap:
                self._is_tudongtodoi = thietlap["_is_tudongtodoi"]

            # if "_diemdanhxungquanhs" in thietlap:
            #     self._diemdanhxungquanhs = thietlap["_diemdanhxungquanhs"]

    def action_tudongtheosautruongnhom(self):
        is_tamngungtancongtheosautruongnhom = False
        is_tamngungnhatdodetheosautruongnhom = False
        if self._is_tudongtheosautruongnhom:
            while True:
                if self._is_tamngungdichuyendenhatdo:
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

                if self._is_tudongbattheosaunhom and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THEOSAUNHOM, ), True, is_hieuungcoloi = 1):
                    self.moitruong.action_battheosaunhom(2.)

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
                is_tamngungnhatdodetheosautruongnhom = True

                if self._is_tamngungdichuyensudungkynang:
                    break

                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and time.time() - self.moitruong.get_thoidiemsudungkynangvitrigannhat(*VITRIKYNANG_KHAITHIENTICHDIA, time.time() - 2.0) > 1.0:
                    self.moitruong.action_sudungkynangvitriphudaudiem(*VITRIKYNANG_KHAITHIENTICHDIA, xtruongnhom, ytruongnhom, khoangcachphudau = khoangcachtruongnhom)
                else:
                    self.moitruong.action_dichuyentiepcandiem(xtruongnhom, ytruongnhom)

                break

        self._is_tamngungtancongtheosautruongnhom = is_tamngungtancongtheosautruongnhom
        self._is_tamngungnhatdodetheosautruongnhom = is_tamngungnhatdodetheosautruongnhom

    def action_tudongtimkiemmuctieu(self):
        if self._is_tudongtimkiemmuctieu:
            i = 0

            while True:
                idbandohientai = self.moitruong.get_idbandohientai()
                is_bandokhongtancong = idbandohientai in BANDOKHONGTANCONGs

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if diachicosothongtinnhanvatmuctieudangchon:
                    if is_bandokhongtancong:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif self._tenmuctieutancongs and self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon) not in self._tenmuctieutancongs:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif self._is_chidanhnguoichoi and not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon):
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif idbandohientai == BANDO_CHIENTRUONG:
                        tendoituongmuctieudangchon = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)
                        if self._phehientai == PHEBACHKHOI:
                            if tendoituongmuctieudangchon != LIEMPHA:
                                self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                        elif self._phehientai == PHELIEMPHA:
                            if tendoituongmuctieudangchon != BACHKHOI:
                                self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                        else:
                            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

                if is_bandokhongtancong:
                    break

                diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtinnhanvatmuctieuxemxet:
                    break

                i += 1

                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                if idbandohientai == BANDO_CHIENTRUONG:
                    tendoituongmuctieuxemxet = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet)
                    if self._phehientai == PHEBACHKHOI:
                        if tendoituongmuctieuxemxet != LIEMPHA:
                            continue
                    elif self._phehientai == PHELIEMPHA:
                        if tendoituongmuctieuxemxet != BACHKHOI:
                            continue
                    else:
                        continue

                if self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatmuctieuxemxet) in NHANVATTODOITUDONGs:
                    continue

                if self._tenmuctieutancongs:
                    if self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet) not in self._tenmuctieutancongs:
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

            if time.time() - self._thoidiemkiemtrahieuunggannhat > 2.5:
                self._thoidiemkiemtrahieuunggannhat = time.time()

                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HUYETTHACH,), True, is_hieuungcoloi = 1) or not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHAPLUCTHACH,), True, is_hieuungcoloi = 1):
                    self.moitruong.action_sudungchucnangmorong5()

            if self.moitruong.get_diempk() > 0:
                self.action_sudungvatphamhanhtrang(PHIHANHPHU)

    def action_tudongsudungkynang_vanmongcoc(self):
        is_tamngungdichuyensudungkynang = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongtheosautruongnhom:
                    break
                if self._is_tamngungtancongdenhatdo:
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

                if self.moitruong.get_phantramsinhlucconlai() <= 75. and not self.moitruong.get_is_cohieuungs(HIEUUNGKYNANG_DAUCHUYENTINHDI, True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAMLOTRI):
                    is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_CAMLOTRI)
                        break

                if self.moitruong.get_phantramsinhlucconlai() <= 75. and not self.moitruong.get_is_cohieuungs(HIEUUNGKYNANG_DAUCHUYENTINHDI, True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHIETVANQUYET):
                    is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_KHIETVANQUYET)
                        break

                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANCHAMDOACH,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGANCHAMDOACH):
                    is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_NGANCHAMDOACH)
                        break

                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCHAMDOACH):
                    is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_KIMCHAMDOACH)
                        break

                if not diachicosothongtinnhanvatmuctieudangchon:
                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONGIAPTRAN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_DONGIAPTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - 1)
                            break

                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KYMONTRAN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KYMONTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach + 1)
                            break

                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LIETPHONGQUYET):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LIETPHONGQUYET)
                            break

                if khoangcach <= KHOANGCACHTOIDAHOPLE:
                    if idtuthenhanvat != TUTHENHANVAT_TANCONG:
                        self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon, khoangcachdichuyentoida = khoangcach * 0.8)

                break

        self._is_tamngungdichuyensudungkynang = is_tamngungdichuyensudungkynang

    def action_tudongsudungkynang_duongmon(self):
        is_tamngungdichuyensudungkynang = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongtheosautruongnhom:
                    break
                if self._is_tamngungtancongdenhatdo:
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

                if not diachicosothongtinnhanvatmuctieudangchon:
                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH, ), True, diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_THAUCOTDINH)
                            break

                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MAIHOACHAM):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MAIHOACHAM)
                            break

                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT, ), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_ANTHANTHUAT):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_ANTHANTHUAT)
                            break

                if khoangcach <= KHOANGCACHTOIDAHOPLE:
                    if idtuthenhanvat != TUTHENHANVAT_TANCONG:
                        self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon, khoangcachdichuyentoida = khoangcach * 0.8)

                break

        self._is_tamngungdichuyensudungkynang = is_tamngungdichuyensudungkynang

    def action_tudongsudungkynang_thucson(self):
        is_tamngungdichuyensudungkynang = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongtheosautruongnhom:
                    break
                if self._is_tamngungtancongdenhatdo:
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

                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    if self.moitruong.get_phantramsinhlucconlai() <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                            break

                    if self.moitruong.get_is_cohieuungbatloinhanvat():
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                            is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET, HINHTHUCSUDUNGKYNANG_KHONGCANMUCTIEU)
                                break

                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                            break
                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

                if is_muctieudangchonlanguoichoi:
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH, HINHTHUCSUDUNGKYNANG_KHONGCANMUCTIEU)
                        break

                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, ), macdinh = True, is_hieuungcoloi = 1) and not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH) and (is_muctieudangchonlanguoichoi or self.moitruong.get_phantramsinhlucconlai() < 10.):
                    self.action_sudungvatphamhanhtrang(PHIHANHPHU)

                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG):
                    if is_muctieudangchonlanguoichoi:
                        self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_LUUTINHTRUYMANG)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrikhongtrihoan(*VITRIKYNANG_NGUKIEMPHITIEN)

                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMTHUAT):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_NGUKIEMTHUAT)

                    elif not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LANGKHONGCHIHUYET):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_LANGKHONGCHIHUYET)

                    elif self.moitruong.get_is_cohieuungbatloinhanvat():
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                            is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_TINHTAMQUYET, HINHTHUCSUDUNGKYNANG_KHONGCANMUCTIEU)

                    elif self.moitruong.get_phantramsinhlucconlai() <= 50. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)

                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANKIEMXUYENTAM):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_VANKIEMXUYENTAM)

                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENNHANCHILO):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_TIENNHANCHILO)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    if is_muctieudangchonlanguoichoi:
                        if not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                            self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_LUCPHACHHOASON)
                        elif self.moitruong.get_is_cohieuungcoloinhanvat(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                            self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_PHAMATRAM)
                        elif not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG, ), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                            self.moitruong.action_sudungkynangvitrimuctieukhongtrihoan(*VITRIKYNANG_PHAKHONGKICH)

                if khoangcach <= KHOANGCACHTOIDAHOPLE:
                    if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
                        thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()
                        if thoigiantuthenhanvatdungim > 0.5:
                            if thoigiantuthenhanvatdungim > 8.:
                                self.action_tudongtimduong(self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieudangchon), self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieudangchon), self.moitruong.get_idbandohientai())
                            elif thoigiantuthenhanvatdungim > 4.:
                                self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon)
                            else:

                                self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvatmuctieudangchon, KHOANGCACHSUDUNGKYNANGTAMXA - thoigiantuthenhanvatdungim - (0 if is_muctieudangchonlanguoichoi else 3))

                break
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

    def battat_is_tudongdichientruong(self):
        self._is_tudongdichientruong = not self._is_tudongdichientruong
        if self._is_tudongdichientruong:
            phatam("Bật tự động đi chiến trường")
        else:
            phatam("Tắt tự động đi chiến trường")

    def battat_is_vohieuhoadichuyen(self):

        if not self.moitruong.get_is_vohieuhoadichuyen():
            self.moitruong.set_is_vohieuhoadichuyen(True)
            phatam("Bật vô hiệu hóa di chuyển")
        else:
            self.moitruong.set_is_vohieuhoadichuyen(False)
            phatam("Tắt vô hiệu hóa di chuyển")

    def them_tenmuctieutancong(self, tenmuctieutancong):
        if tenmuctieutancong and tenmuctieutancong not in self._tenmuctieutancongs:
            self._tenmuctieutancongs.add(tenmuctieutancong)

            if self._tenmuctieutancongs:
                phatam("Thêm tên mục tiêu tấn công. Tổng cộng {}".format(len(self._tenmuctieutancongs)))

    def botoanbo_tenmuctieutancong(self):
        self._tenmuctieutancongs.clear()

        phatam("Bỏ thiết lập tên mục tiêu tấn công".format(len(self._tenmuctieutancongs)))

    def action_tudongnhatdo(self):
        is_tamngungdichuyendenhatdo = False
        is_tamngungtancongdenhatdo = False
        if self._is_tudongnhatdo:
            i = 0

            while True:
                if self._is_tamngungnhatdodetheosautruongnhom:
                    break

                diachicosothongtinvatphamxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtinvatphamxemxet:
                    break
                i += 1

                if not self.moitruong.get_is_vatphamtontai(diachicosothongtinvatphamxemxet):
                    continue

                tenvatpham = self.moitruong.get_tendoituong(diachicosothongtinvatphamxemxet)

                if tenvatpham in VATPHAMTUDONGNHATs:
                    khoangcach = self.moitruong.get_khoangcach(diachicosothongtinvatphamxemxet)
                    if khoangcach <= KHOANGCACHNUAMANHINH:
                        is_tamngungdichuyendenhatdo = True
                        is_tamngungtancongdenhatdo = True
                        if khoangcach <= 3:
                            self.moitruong.action_nhatdo(diachicosothongtinvatphamxemxet)
                        else:
                            self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinvatphamxemxet, 3)
                        break
        self._is_tamngungdichuyendenhatdo = is_tamngungdichuyendenhatdo
        self._is_tamngungtancongdenhatdo = is_tamngungtancongdenhatdo

    def action_tudongdichientruong(self):
        idbandohientai = self.moitruong.get_idbandohientai()

        if self._is_tudongdichientruong:
            if idbandohientai == BANDO_CHU:
                if self.moitruong.get_is_daketthucchientruong():
                    self.moitruong.set_is_daketthucchientruong(False)
                self._phehientai = False
                diachicosothongtinnhanvattruongqualao = self.moitruong.action_timkiemnhanvat(tennhanvat = TRUONGQUALAO)

                if not diachicosothongtinnhanvattruongqualao or self.moitruong.get_khoangcach(diachicosothongtinnhanvattruongqualao) > 4.:
                    self.moitruong.action_dichuyentiepcandiem(X_TRUONGQUALAO, Y_TRUONGQUALAO, BANDO_CHU)
                else:
                    iddoituong = self.moitruong.get_iddoituong(diachicosothongtinnhanvattruongqualao)
                    if iddoituong:
                        if self.moitruong.get_is_dangnamtrongnhom() and self.moitruong.get_is_truongnhom():
                            self.moitruong.action_thucthicaulenh("talk {}# welcome.102".format(hex(iddoituong)).replace("0x", ""))
                            time.sleep(0.25)
                            self.moitruong.action_thucthicaulenh("talk {}# welcome.17".format(hex(iddoituong)).replace("0x", ""))
                            time.sleep(0.25)
                        elif self.moitruong.get_idnguoichoi() not in NHANVATTODOITUDONGs:
                            self.moitruong.action_thucthicaulenh("talk {}# welcome.1".format(hex(iddoituong)).replace("0x", ""))
                            time.sleep(0.25)
                            self.moitruong.action_thucthicaulenh("talk {}# welcome.3".format(hex(iddoituong)).replace("0x", ""))
                            time.sleep(0.25)

                        if self.moitruong.get_is_danghiencuasotuychon():
                            self.moitruong.set_is_danghiencuasotuychon(False)

            elif idbandohientai == BANDO_CHIENTRUONG:
                if self._idbandohientai == BANDO_CHU or not self._phehientai:
                    time.sleep(0.5)
                    if self.moitruong.get_khoangcachdiem(X_BACHKHOI, Y_BACHKHOI) <= self.moitruong.get_khoangcachdiem(X_LIEMPHA, Y_LIEMPHA):
                        self._phehientai = PHEBACHKHOI
                    else:
                        self._phehientai = PHELIEMPHA

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if self._phehientai == PHEBACHKHOI:
                    if not diachicosothongtinnhanvatmuctieudangchon or self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon) != LIEMPHA:
                        self.moitruong.action_dichuyentiepcandiem(X_LIEMPHA, Y_LIEMPHA, delay = 2.)

                elif self._phehientai == PHELIEMPHA:
                    if not diachicosothongtinnhanvatmuctieudangchon or self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon) != BACHKHOI:
                        self.moitruong.action_dichuyentiepcandiem(X_BACHKHOI, Y_BACHKHOI, delay = 2.)

                if self.moitruong.get_is_daketthucchientruong():
                    if time.time() - self._thoidiemyeucauroikhoichientruonggannhat > 2.:
                        self._thoidiemyeucauroikhoichientruonggannhat = time.time()
                        self.moitruong.action_thucthicaulenh("desc changping leave", delay = 0.)

        self._idbandohientai = idbandohientai

    def action_tudongtimduong(self, x, y, idbando):
        idbandohientai = self.moitruong.get_idbandohientai()
        if idbandohientai == BANDO_CHU:
            diachicosothongtinnhanvatsugiamonphai = self.moitruong.action_timkiemnhanvat(tennhanvat = SUGIAMONPHAI)

            if not diachicosothongtinnhanvatsugiamonphai or self.moitruong.get_khoangcach(diachicosothongtinnhanvatsugiamonphai) >= 4.:
                self.moitruong.action_tudongtimduong(X_SUGIAMONPHAI_CHU, Y_SUGIAMONPHAI_CHU, BANDO_CHU)
            else:
                iddoituong = self.moitruong.get_iddoituong(diachicosothongtinnhanvatsugiamonphai)
                if iddoituong:
                    self.moitruong.action_thucthicaulenh("talk {}# 1".format(hex(iddoituong)).replace("0x", ""))
                    time.sleep(0.5)

            return
        elif idbandohientai == BANDO_THUCSON:
            diachicosothongtinnhanvattanthutienco = self.moitruong.action_timkiemnhanvat(tennhanvat = TANTHUTIENCO)

            if not diachicosothongtinnhanvattanthutienco or self.moitruong.get_khoangcach(diachicosothongtinnhanvattanthutienco) >= 4.:
                self.moitruong.action_tudongtimduong(X_TANTHUTIENCO_THUCSON, Y_TANTHUTIENCO_THUCSON, BANDO_THUCSON)
                time.sleep(0.5)
            else:
                if idbando in DICHUYENTANTHUTIENCO_MAP:
                    iddoituong = self.moitruong.get_iddoituong(diachicosothongtinnhanvattanthutienco)
                    if iddoituong:
                        for caulenh in DICHUYENTANTHUTIENCO_MAP[idbando]:
                            self.moitruong.action_thucthicaulenh(caulenh.format(hex(iddoituong)).replace("0x", ""))
                            time.sleep(0.25)

                if self.moitruong.get_is_danghiencuasotuychon():
                    self.moitruong.set_is_danghiencuasotuychon(False)

            return
        self.moitruong.action_tudongtimduong(x, y, idbando)

    def action_tudongdichuyenxungquanhdiem(self):
        is_tamngungtancongdichuyenxungquanh = False

        if self._is_tudongsudungkynang and self._diemdanhxungquanhs:
            while True:
                if self._is_tamngungdichuyensudungkynang:
                    break
                if self._is_tamngungdichuyendenhatdo:
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                idbandohientai = self.moitruong.get_idbandohientai()

                diemdanhxungquanhbandos = [diemdanhxungquanh for diemdanhxungquanh in self._diemdanhxungquanhs if diemdanhxungquanh[2] == idbandohientai]

                if diemdanhxungquanhbandos:
                    khoangcachgannhat = KHOANGCACHTOIDAHOPLE
                    khoangcachs = []
                    for iddiemdanhxungquanh, diemdanhxungquanh in enumerate(diemdanhxungquanhbandos):
                        khoangcach = self.moitruong.get_khoangcachdiem(*diemdanhxungquanh[:-1])
                        khoangcachs.append(khoangcach)
                        if khoangcach < khoangcachgannhat:
                            khoangcachgannhat = khoangcach
                            iddiemdanhxungquanhgannhat = iddiemdanhxungquanh
                    iddiemdanhxungquanhtieptheo = (iddiemdanhxungquanhgannhat + 1) % len(diemdanhxungquanhbandos)
                    diemdanhxungquanhtieptheo = diemdanhxungquanhbandos[iddiemdanhxungquanhtieptheo]

                    if not self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon() and time.time() - self.moitruong.get_thoidiemkhongcomuctieugannhat() > 1.:
                        is_tamngungtancongdichuyenxungquanh = True

                        if time.time() - self._thoidiemdichuyendiemdanhxungquanhgannhat < 1.:
                            break

                        if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                            self._thoidiemdichuyendiemdanhxungquanhgannhat = time.time()
                            if idbandohientai != diemdanhxungquanhtieptheo[-1]:
                                self.action_tudongtimduong(*diemdanhxungquanhtieptheo)
                            else:
                                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()
                                if thoigiantuthenhanvatdungim > 6.:
                                    self.action_tudongtimduong(*diemdanhxungquanhtieptheo)
                                elif thoigiantuthenhanvatdungim > 3.:
                                    self.moitruong.action_dichuyentiepcandiem(*diemdanhxungquanhtieptheo[:-1])
                            if time.time() - self._thoidiemthongbaotudongtimduonggannhat > 6.:
                                self._thoidiemthongbaotudongtimduonggannhat = time.time()
                                phatam("Tự động tìm đường về điểm đánh xung quanh")
                else:
                    is_tamngungtancongdichuyenxungquanh = True

                    if time.time() - self._thoidiemdichuyendiemdanhxungquanhgannhat < 1.:
                        break

                    if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                        self._thoidiemdichuyendiemdanhxungquanhgannhat = time.time()

                        diemdanhxungquanhbatky = self._diemdanhxungquanhs[0]
                        self.action_tudongtimduong(*diemdanhxungquanhbatky)

                        if time.time() - self._thoidiemthongbaotudongtimduonggannhat > 6.:
                            self._thoidiemthongbaotudongtimduonggannhat = time.time()
                            phatam("Tự động tìm đường về điểm đánh xung quanh")
                        break
                break

        self._is_tamngungtancongdichuyenxungquanh = is_tamngungtancongdichuyenxungquanh

    def them_diemdanhxungquanh(self, diemdanhxungquanh):
        if diemdanhxungquanh and diemdanhxungquanh not in self._diemdanhxungquanhs:
            self._diemdanhxungquanhs.append(diemdanhxungquanh)
            phatam("Thêm điểm đánh xung quanh. Tổng cộng {}".format(len(self._diemdanhxungquanhs)))

    def botoanbo_diemdanhxungquanh(self):
        self._diemdanhxungquanhs.clear()
        phatam("Bỏ toàn bộ điểm đánh xung quanh")

    def thietlap_chidanhnguoichoi(self, is_chidanhnguoichoi):
        self._is_chidanhnguoichoi = is_chidanhnguoichoi
        if not is_chidanhnguoichoi:
            phatam("Bỏ thiết lập chỉ đánh người chơi")
        else:
            phatam("Thiết lập chỉ đánh người chơi")

    def action_tudongtodoi(self):
        if self._is_tudongtodoi:
            while True:
                if not NHANVATTODOITUDONGs:
                    break

                idnhanvattruongnhom = NHANVATTODOITUDONGs[0]

                idnguoichoi = self.moitruong.get_idnguoichoi()

                if idnguoichoi == idnhanvattruongnhom:
                    if self.moitruong.get_is_dangnamtrongnhom():
                        if len(NHANVATTODOITUDONGs) <= 1:
                            break
                        if not self.moitruong.get_is_truongnhom():
                            break

                        danhsachidthanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
                        danhsachidnguoichoixungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()

                        for idnguoichoithanhvien in NHANVATTODOITUDONGs[1:]:
                            if idnguoichoithanhvien in danhsachidnguoichoixungquanhs and idnguoichoithanhvien not in danhsachidthanhviennhoms:
                                self.moitruong.action_moihoacxinvaonhom(idnguoichoithanhvien)
                                time.sleep(0.25)

                                if self.moitruong.get_is_danghiencuasoyesno():
                                    self.moitruong.set_is_danghiencuasoyesno(False)

                                break
                    else:
                        self.moitruong.action_moihoacxinvaonhom(idnhanvattruongnhom)
                        time.sleep(0.25)

                        if self.moitruong.get_is_danghiencuasoyesno():
                            self.moitruong.set_is_danghiencuasoyesno(False)

                        break
                else:
                    if self.moitruong.get_is_dangnamtrongnhom():
                        idnguoichoitruongnhomhientai = self.moitruong.get_idnguoichoitruongnhom()
                        if idnguoichoitruongnhomhientai != idnhanvattruongnhom and idnguoichoi in NHANVATTODOITUDONGs:
                            danhsachidnguoichoixungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()
                            if idnhanvattruongnhom in danhsachidnguoichoixungquanhs:
                                self.moitruong.action_thoatkhoinhom(idnguoichoitruongnhomhientai)
                                time.sleep(0.25)
                                break
                    else:
                        self.moitruong.action_kiemtravadongyloimoinhom(idnhanvattruongnhom)
                        time.sleep(0.25)
                        break
                break

    def action_tudongphucsinh(self):
        if self._is_tudongphucsinh:
            while True:
                if not self.moitruong.get_is_nhanvatdachet():
                    self._thoidiemnhanvatchetgannhat = time.time()
                elif time.time() - self._thoidiemnhanvatchetgannhat > 2.5:
                    self.moitruong.action_phucsinh()
                break

    def action_tudongdoimaupk(self):
        if self._is_tudongphucsinh:
            while True:
                if time.time() - self._thoidiemdoimaupkgannhat > 30.:
                    self._thoidiemdoimaupkgannhat = time.time()
                    self.moitruong.action_doimaupk(MAUPK_TUDO)
                break

    def action_tudongsuado(self):
        if self._is_tudongsuado:
            if time.time() - self._thoidiemkiemtranpcsuadogannhat < 2.:
                return
            self._thoidiemkiemtranpcsuadogannhat = time.time()

            diachicosothongtinnhanvatchutiemsuachua = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)

            if diachicosothongtinnhanvatchutiemsuachua and self.moitruong.get_khoangcach(diachicosothongtinnhanvatchutiemsuachua) <= 4:
                self.moitruong.action_suado(diachicosothongtinnhanvatchutiemsuachua)

    def action_sudungvatphamhanhtrang(self, tenvatpham, delay = 0.25):
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return

        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(tenvatpham)

        if not iddoituongvatpham:
            return

        self._thoidiemsudungvatphamgannhat = time.time()
        self.moitruong.action_thucthicaulenh("use {}#".format(hex(iddoituongvatpham)).replace("0x", ""), delay = 0.)

    def action_tudongtrieuhoibaothudautien(self):
        if self._is_tudongtrieuhoibaothudautien:
            while True:
                iddoituongbaothudautien = self.moitruong.get_iddoituongbaothudautien()

                if not iddoituongbaothudautien:
                    break

                if self.moitruong.get_is_datrieuhoibaothu():
                    if time.time() - self._thoidiemsudungthucanbaothugannhat > 30.:
                        iddoituongcaocapbaothuthucpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPBAOTHUTHUCPHAM)
                        if iddoituongcaocapbaothuthucpham:
                            self._thoidiemsudungthucanbaothugannhat = time.time()
                            self.moitruong.action_thucthicaulenh("use {}# pet {}#".format(hex(iddoituongcaocapbaothuthucpham), hex(iddoituongbaothudautien)).replace("0x", ""), delay = 0.)

                    diachicosonhanvatbaothudautien = self.moitruong.action_timkiemnhanvat(iddoituong = iddoituongbaothudautien)

                    if diachicosonhanvatbaothudautien and time.time() - self._thoidiemthietlapbaothuchodoigannhat > 2.:
                        self.moitruong.action_thucthicaulenh("pet {}# 3".format(hex(iddoituongbaothudautien)).replace("0x", ""), delay = 0.)
                    break

                if time.time() - self._thoidiemtudongtrieuhoibaothudautien > 1. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                    self._thoidiemtudongtrieuhoibaothudautien = time.time()
                    self.moitruong.action_thucthicaulenh("pet {}# show".format(hex(iddoituongbaothudautien)).replace("0x", ""), delay = 0.)
                    break

    def action_tudongtrieuhoithanthu(self):
        if self._is_tudongtrieuhoithanthu:
            if time.time() - self._thoidiemkiemtradatrieuhoithanthugannhat < 1.:
                return

            self._thoidiemkiemtradatrieuhoithanthugannhat = time.time()

            if not self.moitruong.get_is_dathietlapkynangphimtat(VITRIPHIMTATKYNANG_THANTHU):
                return

            if not self.moitruong.get_is_datrieuhoithanthu():
                self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_THANTHU)
