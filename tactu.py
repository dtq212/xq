import random
import time

import pymem

from hangso import *
from moitruong import MoiTruong
from tienich import taithietlap as util_taithietlap, phatam
from tienich import luuthietlap as util_luuthietlap

class TacTu:
    def __init__(self, moitruong: MoiTruong):
        self._is_thucsondao = False
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
        self._is_tudongchaylenbandovuachet = True
        self._is_tudongxepchongdo = True

        self._is_tudongdibatquaitran = False

        self._is_uutiennguoichoi = True

        self._khoangcachtoidatruongnhom = 9

        self._tenmuctieutancongs = set()
        self._tenvatphamnhats = set()

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
        self._thoidiemkiemtracuoithugannhat = time.time()
        self._thoidiemsudungvatphamgannhat = time.time()
        self._thoidiemsudungthucanbaothugannhat = time.time()
        self._thoidiemmochangiabaoruonggannhat = time.time()
        self._thoidiemsudungsinhkhitangannhat = time.time() # - 300.
        self._thoidiemsudungsotriduocgannhat = time.time()
        self._thoidiemsudungkimcuongbathoaidongannhat = time.time()
        self._thoidiemdichuyenlenbandovuachetgannhat = time.time()
        self._thoidiemepdogannhat = time.time()
        self._thoidiemsudunghoithanhphugannhat = time.time()
        self._thoidiemxepchongdogannhat = time.time()
        self._thoidiemvutdogannhat = time.time()

        self._diachicosovatphamkhongnhats = []
        self._diachicosovatphamkhongnhat_map = {}
        self._thoidiemlammoivatphamkhongnhatgannhat = time.time()
        self._thoidiemthaydoivatphamdangnhatgannhat = time.time()
        self._diemdanhxungquanhs = []
        self._iddiemdanhxungquanhhientai = -1
        self._diemdanhxungquanhhientai = False
        self._thoidiemthaydoidiemdanhxungquanhgannhat = time.time()
        self._khoangcachdiemdanhxungquanh = 27.
        self._is_tamngungtancongtheosautruongnhom = False
        self._is_tamngungtancongdichuyenxungquanh = False
        self._is_tamngungdichuyensudungkynang = False
        self._is_tamngungtancongdenhatdo = False
        self._is_tamngungdichuyendenhatdo = False
        self._is_tamngungnhatdodetheosautruongnhom = False
        self._khoangcachtimkiemmuctieu = 18.
        self._is_tudongtrieuhoithanthu = True
        self._is_tamngungtancongdebuffchothanhviennhom = False
        self._is_tamngungtancongdichuyenlenbandovuachet = False
        self._is_tudongdichuyendiemdanhxungquanh = False
        self._is_tudongdoimaupk = True

        self._idbandohientai = False
        self._phehientai = False

        self._idbandovuachet = False
        self._tenmuctieubatquaitranhientai = False

        self._tenmuctieubatquaitranhientai = False
        self._tenmuctieubatquaitrantruocdo = False

        self._diachicosovatphamdangnhat = False

        self._solansudungkhaithientichdia = 0
        self._solansudungluutinhtruymang = 0

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
            "_is_thucsondao": self._is_thucsondao,
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

            if "_is_thucsondao" in thietlap:
                self._is_thucsondao = thietlap["_is_thucsondao"]

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

                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_TANCONG:
                    break

                if self._is_tudongbattheosaunhom and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THEOSAUNHOM, ), True, is_hieuungcoloi = 1):
                    self.moitruong.action_battheosaunhom(2.)

                xtruongnhom = self.moitruong.get_toadoxtruongnhom()
                ytruongnhom = self.moitruong.get_toadoytruongnhom()

                if not xtruongnhom and not ytruongnhom:
                    break

                khoangcachtruongnhom = self.moitruong.get_khoangcachdiem(xtruongnhom, ytruongnhom)

                khoangcachtoidatruongnhom = self._khoangcachtoidatruongnhom

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon):
                    khoangcachtoidatruongnhom -= 6.

                if khoangcachtruongnhom <= khoangcachtoidatruongnhom:
                    break

                if khoangcachtruongnhom >= KHOANGCACHTOIDAHOPLE:
                    break

                is_tamngungtancongtheosautruongnhom = True
                is_tamngungnhatdodetheosautruongnhom = True

                if self._is_tamngungdichuyensudungkynang:
                    break

                if self.moitruong.get_tenmonphai() == "thucson" and khoangcachtruongnhom >= KHOANGCACHNUAMANHINH and not self.moitruong.get_is_vohieuhoadichuyen() and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA, delay = 1.):
                    self.moitruong.action_sudungkynangvitriphudaudiem(*VITRIKYNANG_KHAITHIENTICHDIA, xtruongnhom, ytruongnhom, khoangcachphudau = khoangcachtruongnhom - khoangcachtoidatruongnhom + 3.)
                else:
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(xtruongnhom, ytruongnhom, max(0, khoangcachtoidatruongnhom - 1.5 - time.time() + self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat()))

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
                    elif idbandohientai == BANDO_BATQUAITRAN:
                        tendoituongmuctieudangchon = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)
                        if tendoituongmuctieudangchon and tendoituongmuctieudangchon != self._tenmuctieubatquaitranhientai:
                            self._tenmuctieubatquaitrantruocdo = self._tenmuctieubatquaitranhientai
                            self._tenmuctieubatquaitranhientai = tendoituongmuctieudangchon
                if idbandohientai != BANDO_BATQUAITRAN: #Tức là bản đồ không phải bát quái trận
                    self._tenmuctieubatquaitranhientai = False
                    self._tenmuctieubatquaitrantruocdo = False
                    
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

                # if self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatmuctieuxemxet) in NHANVATTODOITUDONGs:
                #     continue

                if self._tenmuctieutancongs:
                    if self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet) not in self._tenmuctieutancongs:
                        continue

                if self._is_chidanhnguoichoi and not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                diachicosothongtinnhanvattruongnhom = self.moitruong.get_diachicosothongtinnhanvattruongnhom()
                if not diachicosothongtinnhanvattruongnhom:
                    diachicosothongtinnhanvattruongnhom = self.moitruong.get_diachicosothongtinnhanvat1()

                khoangcachmuctieuxemxet = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet, diachicosothongtinnhanvattruongnhom)
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

                if khoangcachmuctieuxemxet < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon, diachicosothongtinnhanvattruongnhom):
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


                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
                if diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NHANSAMVUONG, ), True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(NHANSAMVUONG)

            if self.moitruong.get_diempk() > 0:
                self.action_sudungvatphamhanhtrang(ANXAPHU)

            if time.time() - self._thoidiemsudungsinhkhitangannhat > 10.:
                is_ok = self.action_sudungvatphamhanhtrang(SINHKHITAN)
                if is_ok:
                    self._thoidiemsudungsinhkhitangannhat = time.time()

            if time.time() - self._thoidiemsudungsotriduocgannhat > 1. and self.moitruong.get_phantramsinhlucconlai() <= 25.:
                self._thoidiemsudungsotriduocgannhat = time.time()
                self.action_sudungvatphamhanhtrang(SOTRIDUOC)

    def action_tudongsudungkynang_vanmongcoc(self):
        is_tamngungdichuyensudungkynang = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongdebuffchothanhviennhom:
                    break
                if self._is_tamngungtancongdichuyenlenbandovuachet:
                    break
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
                idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

                i = -1

                while True:
                    i += 1
                    diachicosothongtinnhanvatxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                    if not diachicosothongtinnhanvatxemxet:
                        break
                    if not self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                        continue
                    idnguoichoi = self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
                    if not idnguoichoi:
                        continue

                    if idnguoichoi in idnguoichoithanhviennhoms and self.moitruong.get_khoangcach(diachicosothongtinnhanvatxemxet) <= KHOANGCACHSUDUNGKYNANGTAMXA:
                        if self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatxemxet):
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAITUHOANSINH):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CAITUHOANSINH, diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                            break
                        else:
                            if self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatxemxet) <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHIETVANQUYET):
                                is_tamngungdichuyensudungkynang = True
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KHIETVANQUYET, diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                    break
                            if self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatxemxet) <= 50. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SOTRI):
                                is_tamngungdichuyensudungkynang = True
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_SOTRI, diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                    break

                            if self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatxemxet) <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VODINHLUUTHUY):
                                is_tamngungdichuyensudungkynang = True
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VODINHLUUTHUY, diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                    break

                            if self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatxemxet) >= 75:
                                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatxemxet, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGANCHAMDOACH):
                                    is_tamngungdichuyensudungkynang = True
                                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGANCHAMDOACH, diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                        break

                                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatxemxet, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCHAMDOACH):
                                    is_tamngungdichuyensudungkynang = True
                                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KIMCHAMDOACH, diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                        break

                if self.moitruong.get_phantramsinhlucconlai() <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHIETVANQUYET):
                    is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_KHIETVANQUYET)
                        break

                if self.moitruong.get_phantramsinhlucconlai() <= 50. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SOTRI):
                    is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_SOTRI)
                        break

                if self.moitruong.get_phantramsinhlucconlai() <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VODINHLUUTHUY):
                    is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_VODINHLUUTHUY)
                        break

                if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs:
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

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if not diachicosothongtinnhanvatmuctieudangchon:
                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGANTHUAT):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGANTHUAT)

                    elif not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYENQUANGTHIEMANH):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HUYENQUANGTHIEMANH)

                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONGIAPTRAN, delay = 1.):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_DONGIAPTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - random.randint(0, 1))

                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KYMONTRAN, delay = 1.):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KYMONTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - random.randint(0, 1))
                            break

                    elif not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHONGVUKINHTHIEN, diachicosothongtinnhanvatmuctieudangchon), macdinh = True, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGVUKINHTHIEN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGVUKINHTHIEN)

                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LIETPHONGQUYET):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LIETPHONGQUYET)

                if khoangcach <= KHOANGCACHTOIDAHOPLE:
                    thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                    if thoigiantuthenhanvatdungim > 0.5:
                        if thoigiantuthenhanvatdungim > 4.5:
                            self.moitruong.action_dichuyentiepcandiem(self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieudangchon), self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieudangchon))
                        else:
                            self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvatmuctieudangchon, KHOANGCACHSUDUNGKYNANGTAMXA - thoigiantuthenhanvatdungim - (0. if is_muctieudangchonlanguoichoi else 3.))

                break

        self._is_tamngungdichuyensudungkynang = is_tamngungdichuyensudungkynang

    def action_tudongsudungkynang_thucsondao(self):
        is_tamngungdichuyensudungkynang = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongtheosautruongnhom:
                    break
                if self._is_tamngungtancongdenhatdo:
                    break
                if self._is_tamngungtancongdichuyenxungquanh:
                    break
                if self._is_tamngungtancongdichuyenlenbandovuachet:
                    break
                if self.moitruong.get_is_dangclickchuottrai():
                    break
                if self.moitruong.get_is_nhanvatdachet():
                    break
                if self.moitruong.get_is_dangvankhi():
                    break

                idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    if self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                            break

                    if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                        break

                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                        break

                    if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGPHACHNGANTAM):
                            is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BANGPHACHNGANTAM)
                                break

                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

                if phantramsinhlucconlai <= 25 or (is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 75):
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH)
                        break

                if time.time() - self._thoidiemsudungkimcuongbathoaidongannhat > 1. and phantramsinhlucconlai <= 25. and not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH) and self.moitruong.get_thoigianconlaihieuungtienthanvodich(macdinh = 2.5) <= 1.5:
                    self._thoidiemsudungkimcuongbathoaidongannhat = time.time()
                    self.action_sudungvatphamhanhtrang(KIMCUONGBATHOAIDON)

                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)

                if not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG):
                    self._solansudungluutinhtruymang = 0

                if not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA):
                    self._solansudungkhaithientichdia = 0

                if idtuthenhanvat == TUTHENHANVAT_DICHUYEN and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG) and not self.moitruong.get_is_vohieuhoadichuyen():
                    is_ok = self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUUTINHTRUYMANG)
                    if is_ok:
                        self._solansudungluutinhtruymang += 1

                elif idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and not self.moitruong.get_is_vohieuhoadichuyen():
                    is_ok = self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach)
                    if is_ok:
                        self._solansudungkhaithientichdia += 1

                if not is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN, HIEUUNGKYNANG_MULOA), macdinh = False, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)

                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONDAOTRUCNHAP):
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_DONDAOTRUCNHAP)

                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG, ), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAKHONGKICH)

                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUCPHACHHOASON)

                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, ), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAMATRAM)

                elif self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)

                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and idtuthenhanvat != TUTHENHANVAT_DICHUYEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG):
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA):
                        self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach + 1.5)
                    else:
                        self.moitruong.action_dichuyengiukhoangcachtoithieu(diachicosothongtinnhanvatmuctieudangchon, khoangcachtoithieu = khoangcach + 1.5)

                if khoangcach <= KHOANGCACHTOIDAHOPLE:
                    thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                    if thoigiantuthenhanvatdungim > 0.5:
                        if (thoigiantuthenhanvatdungim > 2.0 or self._solansudungluutinhtruymang >= 5) and khoangcach >= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                            self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon)
                        elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG) and khoangcach > 1.5:
                            self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvatmuctieudangchon, khoangcachtoida = khoangcach - 1.5)
                        else:
                            self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvatmuctieudangchon, KHOANGCACHSUDUNGKYNANGCANCHIEN)
                    else:
                        self.moitruong.action_dichuyentiepcan(diachicosothongtinnhanvatmuctieudangchon)
                break
        self._is_tamngungdichuyensudungkynang = is_tamngungdichuyensudungkynang

    def action_tudongsudungkynang_thucson(self):
        if self._is_thucsondao:
            return self.action_tudongsudungkynang_thucsondao()

        is_tamngungdichuyensudungkynang = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongtheosautruongnhom:
                    break
                if self._is_tamngungtancongdenhatdo:
                    break
                if self._is_tamngungtancongdichuyenxungquanh:
                    break
                if self._is_tamngungtancongdichuyenlenbandovuachet:
                    break
                if self.moitruong.get_is_dangclickchuottrai():
                    break
                if self.moitruong.get_is_nhanvatdachet():
                    break
                if self.moitruong.get_is_dangvankhi():
                    break

                idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    if self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                            break

                    if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                        break

                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                        break

                    if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGPHACHNGANTAM):
                            is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BANGPHACHNGANTAM)
                                break

                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

                if phantramsinhlucconlai <= 25 or (is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 75):
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH)
                        break

                if time.time() - self._thoidiemsudungkimcuongbathoaidongannhat > 1. and phantramsinhlucconlai <= 25. and not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH) and self.moitruong.get_thoigianconlaihieuungtienthanvodich(macdinh = 2.5) <= 1.5:
                    self._thoidiemsudungkimcuongbathoaidongannhat = time.time()
                    self.action_sudungvatphamhanhtrang(KIMCUONGBATHOAIDON)

                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_muctieuchaytron = self.moitruong.get_is_muctieuchaytron(diachicosothongtinnhanvatmuctieudangchon)

                is_duoitheo = khoangcach >= 6. and is_muctieuchaytron and not self.moitruong.get_is_vohieuhoadichuyen()

                if not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA):
                    self._solansudungkhaithientichdia = 0

                if is_duoitheo:
                    if idtuthenhanvat == TUTHENHANVAT_DICHUYEN and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG) and not self.moitruong.get_is_vohieuhoadichuyen():
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUUTINHTRUYMANG)
                    elif idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and not self.moitruong.get_is_vohieuhoadichuyen():
                        self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach)
                    else:
                        thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                        self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvatmuctieudangchon, khoangcach - thoigiantuthenhanvatdungim - 3.)

                elif khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if not is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN, HIEUUNGKYNANG_MULOA), macdinh = False, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)

                    elif not is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN)

                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMTHUAT):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGUKIEMTHUAT)

                    elif is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN)

                    elif not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LANGKHONGCHIHUYET):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LANGKHONGCHIHUYET)

                    elif self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)

                    elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and is_muctieudangchonlanguoichoi and not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUCPHACHHOASON)

                    elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, ), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAMATRAM)

                    elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANKIEMXUYENTAM):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANKIEMXUYENTAM)

                    elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGTAMTHUC):
                        is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BANGTAMTHUC)

                if khoangcach <= KHOANGCACHTOIDAHOPLE:
                    if not is_duoitheo:
                        thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                        if thoigiantuthenhanvatdungim > 1.:
                            if thoigiantuthenhanvatdungim > 4.5:
                                self.moitruong.action_dichuyentiepcandiem(self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieudangchon), self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieudangchon))
                            else:
                                self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvatmuctieudangchon, KHOANGCACHSUDUNGKYNANGTAMXA - min(1. + thoigiantuthenhanvatdungim + (3 if not is_muctieudangchonlanguoichoi else 0), 3.))

                        elif is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA - 6 and not self.moitruong.get_is_vohieuhoadichuyen():
                            if idtuthenhanvat == TUTHENHANVAT_TANCONG and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA, delay = min(1., 0.1 * self._solansudungkhaithientichdia)):
                                is_ok = self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - KHOANGCACHSUDUNGKYNANGTAMXA)
                                if is_ok:
                                    self._solansudungkhaithientichdia += 1
                break
        self._is_tamngungdichuyensudungkynang = is_tamngungdichuyensudungkynang

    def action_tudongsudungkynang_daohoanguyen(self):
        is_tamngungdichuyensudungkynang = False
        if self._is_tudongsudungkynang:
            while True:
                if self._is_tamngungtancongtheosautruongnhom:
                    break
                if self._is_tamngungtancongdenhatdo:
                    break
                if self._is_tamngungtancongdichuyenxungquanh:
                    break
                if self._is_tamngungtancongdichuyenlenbandovuachet:
                    break
                if self.moitruong.get_is_dangclickchuottrai():
                    break
                if self.moitruong.get_is_nhanvatdachet():
                    break
                if self.moitruong.get_is_dangvankhi():
                    break

                idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRANCOTHANUY,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TRANCOTHANUY):
                    is_tamngungdichuyensudungkynang = True
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TRANCOTHANUY)
                    break

                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMTRUNGCHAO,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMTRUNGCHAO):
                    is_tamngungdichuyensudungkynang = True
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KIMTRUNGCHAO)
                    break

                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCUONGTHANPHAP,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCUONGTHANPHAP):
                            is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KIMCUONGTHANPHAP)
                                break
                    break

                break
        self._is_tamngungdichuyensudungkynang = is_tamngungdichuyensudungkynang

    def battat_is_tudongsudungkynang(self):
        self._is_tudongsudungkynang = not self._is_tudongsudungkynang
        if self._is_tudongsudungkynang:
            phatam("Bật tự động sử dụng kỹ năng")
        else:
            phatam("Tắt tự động sử dụng kỹ năng")

    def battat_is_thucsondao(self):
        self._is_thucsondao = not self._is_thucsondao
        if self._is_thucsondao:
            phatam("Bật thục sơn đao")
        else:
            phatam("Tắt thục sơn đao")

    def battat_is_tudongdichuyendiemdanhxungquanh(self):
        self._is_tudongdichuyendiemdanhxungquanh = not self._is_tudongdichuyendiemdanhxungquanh
        if self._is_tudongdichuyendiemdanhxungquanh:
            phatam("Bật tự động di chuyển điểm đánh xung quanh")
        else:
            phatam("Tắt tự động di chuyển điểm đánh xung quanh")



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

    def battat_is_tudongdibatquaitran(self):
        self._is_tudongdibatquaitran = not self._is_tudongdibatquaitran
        if self._is_tudongdibatquaitran:
            phatam("Bật tự động đi bát quái trận")
        else:
            phatam("Tắt tự động đi bát quái trận")

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
                print("Danh sách mục tiêu tấn công: {}".format(self._tenmuctieutancongs))
                phatam("Thêm tên mục tiêu tấn công. Tổng cộng {}".format(len(self._tenmuctieutancongs)))

    def them_tenvatphamnhat(self, tenvatphamnhat):
        if tenvatphamnhat and tenvatphamnhat not in self._tenvatphamnhats:
            self._tenvatphamnhats.add(tenvatphamnhat)

            if self._tenvatphamnhats:
                print("Danh sách mục tiêu tấn công: {}".format(self._tenvatphamnhats))
                phatam("Thêm tên mục tiêu tấn công. Tổng cộng {}".format(len(self._tenvatphamnhats)))

    def botoanbo_tenmuctieutancong(self):
        self._tenmuctieutancongs.clear()
        self._tenvatphamnhats.clear()

        phatam("Bỏ thiết lập tên mục tiêu tấn công và vật phẩm nhặt".format(len(self._tenmuctieutancongs)))


    def action_tudongvutdo(self):
        if time.time() - self._thoidiemvutdogannhat < 2.:
            return

        if not self.moitruong.get_idbandohientai() != BATQUAITRAN:
            return

        if not self.moitruong.get_is_dayhanhtrang():
            return

        # iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(DOANTHACHDACBIETCAOCAPHANHTRANG)
        #
        # if not iddoituongvatpham:
        #     return

        # iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(DOANTHACHCAOCAP)
        #
        # if not iddoituongvatpham:
        #     return

        # is_ok = self.moitruong.action_thucthicaulenh("drop ! {}#1".format(hex(iddoituongvatpham)).replace("0x", ""))
        # if is_ok:
        #     self._thoidiemvutdogannhat = time.time()


    def action_tudongnhatdo(self):
        is_tamngungdichuyendenhatdo = False
        is_tamngungtancongdenhatdo = False
        if self._is_tudongnhatdo:
            i = 0

            while True:
                diachicosothongtinvatphamxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtinvatphamxemxet:
                    break
                i += 1

                if not self.moitruong.get_is_vatphamtontai(diachicosothongtinvatphamxemxet):
                    continue

                if time.time() - self._diachicosovatphamkhongnhat_map.get(diachicosothongtinvatphamxemxet, time.time() - 90) < 60:
                    continue

                tenvatpham = self.moitruong.get_tendoituong(diachicosothongtinvatphamxemxet)

                if tenvatpham in VATPHAMTUDONGNHATs:
                    khoangcach = self.moitruong.get_khoangcach(diachicosothongtinvatphamxemxet)
                    if khoangcach <= KHOANGCACHTOANMANHINH * 2:
                        if not self._diachicosovatphamdangnhat or not self.moitruong.get_is_vatphamtontai(self._diachicosovatphamdangnhat) or khoangcach < self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat):
                            if self._diachicosovatphamdangnhat != diachicosothongtinvatphamxemxet:
                                self._diachicosovatphamdangnhat = diachicosothongtinvatphamxemxet
                                self._thoidiemthaydoivatphamdangnhatgannhat = time.time()

            if self._diachicosovatphamdangnhat and self.moitruong.get_is_vatphamtontai(self._diachicosovatphamdangnhat) and self.moitruong.get_tendoituong(self._diachicosovatphamdangnhat) in VATPHAMTUDONGNHATs and self._diachicosovatphamdangnhat not in self._diachicosovatphamkhongnhats:
                while True:
                    if self._is_tamngungnhatdodetheosautruongnhom:
                        break

                    if self.moitruong.get_is_dangclickchuottrai():
                        break

                    if self.moitruong.get_is_dangvankhi():
                        break

                    if self.moitruong.get_is_nhanvatdachet():
                        break

                    is_tamngungdichuyendenhatdo = True
                    is_tamngungtancongdenhatdo = True

                    khoangcach = self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat)
                    if self.moitruong.get_tendoituong(self._diachicosovatphamdangnhat) == GATAYNOEL:
                        self.moitruong.action_nhatdoxungquanh()
                    elif khoangcach <= 3.:
                        self.moitruong.action_nhatdo(self._diachicosovatphamdangnhat)

                    if not self._is_tamngungdichuyensudungkynang:
                        if self.moitruong.get_tenmonphai() == "thucson" and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA, delay = 1.) and khoangcach >= 3:
                            self.moitruong.action_sudungkynangvitriphudaudiem(*VITRIKYNANG_KHAITHIENTICHDIA, self.moitruong.get_toadox(self._diachicosovatphamdangnhat, is_vitrihientai = True), self.moitruong.get_toadoy(self._diachicosovatphamdangnhat, is_vitrihientai = True), khoangcachphudau = khoangcach)
                        else:
                            self.moitruong.action_dichuyentiepcandiem(self.moitruong.get_toadox(self._diachicosovatphamdangnhat, is_vitrihientai = True), self.moitruong.get_toadoy(self._diachicosovatphamdangnhat, is_vitrihientai = True))

                    if time.time() - self._thoidiemthaydoivatphamdangnhatgannhat > 3. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM and time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat() > 3.:
                        self._diachicosovatphamkhongnhat_map[self._diachicosovatphamdangnhat] = time.time()
                        self._diachicosovatphamdangnhat = False

                    break
            else:
                if self.moitruong.get_idbandohientai() == BANDO_BATQUAITRAN:
                    i = 0

                    while True:
                        if self._is_tamngungnhatdodetheosautruongnhom:
                            break

                        if self.moitruong.get_is_dangclickchuottrai():
                            break

                        if self.moitruong.get_is_dangvankhi():
                            break

                        if self.moitruong.get_is_nhanvatdachet():
                            break

                        diachicosothongtinvatphamxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                        if not diachicosothongtinvatphamxemxet:
                            break
                        i += 1

                        if not self.moitruong.get_is_nhanvattontai(diachicosothongtinvatphamxemxet):
                            continue

                        if self.moitruong.get_tendoituong(diachicosothongtinvatphamxemxet) != CHANGIABAORUONG:
                            continue

                        if self._tenmuctieubatquaitrantruocdo != "S9" or self._tenmuctieubatquaitranhientai != AOANHMADAO:
                            khoangcach = self.moitruong.get_khoangcach(diachicosothongtinvatphamxemxet)
                            if khoangcach <= 6.:
                                if time.time() - self._thoidiemmochangiabaoruonggannhat >= 1.5 and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                                    is_ok = self.moitruong.action_nhatruong(self.moitruong.get_iddoituong(diachicosothongtinvatphamxemxet), delay = 1.)
                                    if is_ok:
                                        self._thoidiemmochangiabaoruonggannhat = time.time()
                            elif not self._is_tamngungdichuyensudungkynang:
                                self.moitruong.action_dichuyengiukhoangcachtoida(diachicosothongtinvatphamxemxet, khoangcachtoida = 1.5)
                        elif time.time() - self.moitruong.get_thoidiemkhongcomuctieugannhat() > 6. and self.moitruong.get_idtuthenhanvat() != TUTHENHANVAT_DICHUYEN:
                            self.action_sudungvatphamhanhtrang(HOITHANHPHU)

                        break

        self._is_tamngungdichuyendenhatdo = is_tamngungdichuyendenhatdo
        self._is_tamngungtancongdenhatdo = is_tamngungtancongdenhatdo

    def action_tudongdibatquaitran(self):
        if self._is_tudongdibatquaitran:
            if self.moitruong.get_idbandohientai() == BANDO_CHU:
                diachicosothongtinnhanvatbatquaitran = self.moitruong.action_timkiemnhanvat(tennhanvat = BATQUAITRAN)

                if not diachicosothongtinnhanvatbatquaitran or self.moitruong.get_khoangcach(diachicosothongtinnhanvatbatquaitran) > 4.:
                    self.moitruong.action_dichuyentiepcandiem(X_BATQUAITRAN, Y_BATQUAITRAN, BANDO_CHU)
                else:
                    iddoituong = self.moitruong.get_iddoituong(diachicosothongtinnhanvatbatquaitran)
                    if iddoituong:
                        if self.moitruong.get_is_dangnamtrongnhom() and self.moitruong.get_is_truongnhom():
                            is_ok = self.moitruong.action_trochuyenvoinpc(iddoituong, "welcome.1")
                            if is_ok:
                                time.sleep(1.)

                                if self.moitruong.get_is_danghiencuasotuychon():
                                    self.moitruong.set_is_danghiencuasotuychon(False)

                                time.sleep(1.)

                                is_ok = self.moitruong.action_trochuyenvoinpc(iddoituong, "welcome.11")
                                if is_ok:
                                    time.sleep(0.25)

    def action_tudongdichientruong(self):
        pass

    def action_tudongtimduong(self, x = False, y = False, idbando = False):
        if not x and not y and not idbando:
            return

        idbandohientai = self.moitruong.get_idbandohientai()
        if idbandohientai == BANDO_CHU:
            if self.moitruong.get_khoangcachdiem(X_SUGIAMONPHAI_CHU, Y_SUGIAMONPHAI_CHU) < self.moitruong.get_khoangcachdiem(X_PHITACDOATNGANTRUYENTONG_CHU, Y_PHITACDOATNGANTRUYENTONG_CHU):
                diachicosothongtinnhanvatsugiamonphai = self.moitruong.action_timkiemnhanvat(tennhanvat = SUGIAMONPHAI)

                if not diachicosothongtinnhanvatsugiamonphai or self.moitruong.get_khoangcach(diachicosothongtinnhanvatsugiamonphai) > 6.:
                    self.moitruong.action_dichuyentiepcandiem(X_SUGIAMONPHAI_CHU, Y_SUGIAMONPHAI_CHU)
                else:
                    iddoituong = self.moitruong.get_iddoituong(diachicosothongtinnhanvatsugiamonphai)
                    if iddoituong:
                        is_ok = self.moitruong.action_trochuyenvoinpc(iddoituong, "1")
                        if is_ok:
                            time.sleep(0.25)

                            if self.moitruong.get_is_danghiencuasotuychon():
                                self.moitruong.set_is_danghiencuasotuychon(False)
                return
            else:
                diachicosothongtinnhanvatphitacdoatngantruyentong = self.moitruong.action_timkiemnhanvat(tennhanvat = PHITACDOATNGANTRUYENTONG)

                if not diachicosothongtinnhanvatphitacdoatngantruyentong or self.moitruong.get_khoangcach(diachicosothongtinnhanvatphitacdoatngantruyentong) > 6.:
                    self.moitruong.action_dichuyentiepcandiem(X_PHITACDOATNGANTRUYENTONG_CHU, Y_PHITACDOATNGANTRUYENTONG_CHU)
                elif idbando in DICHUYENPHITACDOATNGUYENTRUYENTONG_MAP:
                    iddoituong = self.moitruong.get_iddoituong(diachicosothongtinnhanvatphitacdoatngantruyentong)
                    if iddoituong:
                        self._idbandovuachet = False
                        for noidungtrochuyen in DICHUYENPHITACDOATNGUYENTRUYENTONG_MAP[idbando]:
                            is_ok = self.moitruong.action_trochuyenvoinpc(iddoituong, noidungtrochuyen)
                            if is_ok:
                                time.sleep(0.25)
                            else:
                                break

                        if self.moitruong.get_is_danghiencuasotuychon():
                            self.moitruong.set_is_danghiencuasotuychon(False)

                return
        elif idbandohientai == BANDO_TANTHUTHON:
            diachicosothongtinnhanvatphitacdoatngantruyentong = self.moitruong.action_timkiemnhanvat(tennhanvat = PHITACDOATNGANTRUYENTONG)

            if not diachicosothongtinnhanvatphitacdoatngantruyentong or self.moitruong.get_khoangcach(diachicosothongtinnhanvatphitacdoatngantruyentong) > 6.:
                self.moitruong.action_dichuyentiepcandiem(X_PHITACDOATNGANTRUYENTONG_TANTHUTHON, Y_PHITACDOATNGANTRUYENTONG_TANTHUTHON)
            elif idbando in DICHUYENPHITACDOATNGUYENTRUYENTONG_MAP:
                iddoituong = self.moitruong.get_iddoituong(diachicosothongtinnhanvatphitacdoatngantruyentong)
                if iddoituong:
                    self._idbandovuachet = False
                    for noidungtrochuyen in DICHUYENPHITACDOATNGUYENTRUYENTONG_MAP[idbando]:
                        self.moitruong.action_trochuyenvoinpc(iddoituong, noidungtrochuyen)
                        time.sleep(0.25)

                    if self.moitruong.get_is_danghiencuasotuychon():
                        self.moitruong.set_is_danghiencuasotuychon(False)

            return
        elif idbandohientai == BANDO_THUCSON:
            diachicosothongtinnhanvatxaphu = self.moitruong.action_timkiemnhanvat(tennhanvat = XAPHU)

            if not diachicosothongtinnhanvatxaphu or self.moitruong.get_khoangcach(diachicosothongtinnhanvatxaphu) > 6.:
                self.moitruong.action_dichuyentiepcandiem(X_XAPHU_THUCSON, Y_XAPHU_THUCSON)
            else:
                iddoituong = self.moitruong.get_iddoituong(diachicosothongtinnhanvatxaphu)
                if iddoituong:
                    self.moitruong.action_trochuyenvoinpc(iddoituong, "go")
                    time.sleep(0.25)

                    if self.moitruong.get_is_danghiencuasotuychon():
                        self.moitruong.set_is_danghiencuasotuychon(False)

            return

        if x and y:
            self.moitruong.action_tudongtimduong(x, y, idbando)

    def action_tudongdichuyenlenbandovuachet(self):
        is_tamngungtancongdichuyenlenbandovuachet = False

        if self._is_tudongchaylenbandovuachet and self._is_tudongdichuyendiemdanhxungquanh and self._idbandovuachet:
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

                if not self._idbandovuachet:
                    break

                idbandohientai = self.moitruong.get_idbandohientai()

                if idbandohientai == self._idbandovuachet:
                    self._idbandovuachet = False
                else:
                    is_tamngungtancongdichuyenlenbandovuachet = True

                    if time.time() - self._thoidiemdichuyenlenbandovuachetgannhat < 1.:
                        break

                    if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                        self._thoidiemdichuyenlenbandovuachetgannhat = time.time()

                        self.action_tudongtimduong(idbando = self._idbandovuachet)

                        if time.time() - self._thoidiemthongbaotudongtimduonggannhat > 5.:
                            self._thoidiemthongbaotudongtimduonggannhat = time.time()
                            phatam("Di chuyển lên bản đồ vừa chết")
                        break

                break
        self._is_tamngungtancongdichuyenlenbandovuachet = is_tamngungtancongdichuyenlenbandovuachet

    def action_tudongdichuyenxungquanhdiem(self):
        is_tamngungtancongdichuyenxungquanh = False

        if self._is_tudongdichuyendiemdanhxungquanh:
            while True:
                idbandohientai = self.moitruong.get_idbandohientai()
                diemdanhxungquanhs = self._diemdanhxungquanhs
                if not diemdanhxungquanhs:
                    diemdanhxungquanhs = DIEMDANHXUNGQUANH_MAP.get(idbandohientai)

                if not diemdanhxungquanhs:
                    break

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

                if self._idbandovuachet and self._is_tudongchaylenbandovuachet:
                    break

                if self._diachicosovatphamdangnhat and self.moitruong.get_is_vatphamtontai(self._diachicosovatphamdangnhat):
                    break

                if self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon() and self.moitruong.get_is_cothetancong(self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()):
                    break

                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

                if self.moitruong.get_idtuthenhanvat() != TUTHENHANVAT_DUNGIM or thoigiantuthenhanvatdungim < 1.:
                    break

                if time.time() - self._thoidiemdichuyendiemdanhxungquanhgannhat < 1.:
                    break

                is_tamngungtancongdichuyenxungquanh = True
                self._thoidiemdichuyendiemdanhxungquanhgannhat = time.time()

                diemdanhxungquanhbandos = [diemdanhxungquanh for diemdanhxungquanh in diemdanhxungquanhs if diemdanhxungquanh[2] == idbandohientai]

                if diemdanhxungquanhbandos:
                    if self._diemdanhxungquanhhientai == -1 or not self._diemdanhxungquanhhientai:
                        khoangcachgannhat = KHOANGCACHTOIDAHOPLE
                        iddiemdanhxungquanhgannhat = False
                        for iddiemdanhxungquanh, diemdanhxungquanh in enumerate(diemdanhxungquanhbandos):
                            khoangcach = self.moitruong.get_khoangcachdiem(*diemdanhxungquanh[:-1])
                            if khoangcach < khoangcachgannhat:
                                khoangcachgannhat = khoangcach
                                iddiemdanhxungquanhgannhat = iddiemdanhxungquanh
                        iddiemdanhxungquanhtieptheo = iddiemdanhxungquanhgannhat
                        diemdanhxungquanhtieptheo = diemdanhxungquanhbandos[iddiemdanhxungquanhgannhat]
                    else:
                        iddiemdanhxungquanhtieptheo = ((self._iddiemdanhxungquanhhientai + 1) % len(diemdanhxungquanhbandos)) if (self.moitruong.get_khoangcachdiem(*self._diemdanhxungquanhhientai[:-1]) <= 6. or time.time() - self._thoidiemthaydoidiemdanhxungquanhgannhat > 6.) else self._iddiemdanhxungquanhhientai
                        diemdanhxungquanhtieptheo = diemdanhxungquanhbandos[iddiemdanhxungquanhtieptheo]

                    if iddiemdanhxungquanhtieptheo != self._iddiemdanhxungquanhhientai or self._diemdanhxungquanhhientai != diemdanhxungquanhtieptheo:
                        self._thoidiemthaydoidiemdanhxungquanhgannhat = time.time()
                        self._iddiemdanhxungquanhhientai = iddiemdanhxungquanhtieptheo
                        self._diemdanhxungquanhhientai = diemdanhxungquanhtieptheo

                    print("{}: Di chuyển tiếp cận điểm: ".format(self.moitruong.get_tendoituong()), iddiemdanhxungquanhtieptheo, diemdanhxungquanhtieptheo)
                    self.moitruong.action_dichuyentiepcandiem(*diemdanhxungquanhtieptheo[:-1])

                else:
                    diemdanhxungquanhbatky = diemdanhxungquanhs[0]
                    self.action_tudongtimduong(*diemdanhxungquanhbatky)

                break

        self._is_tamngungtancongdichuyenxungquanh = is_tamngungtancongdichuyenxungquanh

    def them_diemdanhxungquanh(self, diemdanhxungquanh):
        if diemdanhxungquanh and diemdanhxungquanh not in self._diemdanhxungquanhs:
            self._diemdanhxungquanhs.append(diemdanhxungquanh)
            print(self._diemdanhxungquanhs)
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

                                # if self.moitruong.get_is_danghiencuasoyesno():
                                #     self.moitruong.set_is_danghiencuasoyesno(False)

                                break
                    else:
                        self.moitruong.action_moihoacxinvaonhom(idnhanvattruongnhom)
                        time.sleep(0.25)

                        # if self.moitruong.get_is_danghiencuasoyesno():
                        #     self.moitruong.set_is_danghiencuasoyesno(False)

                        break
                else:
                    if self.moitruong.get_is_dangnamtrongnhom():
                        idnguoichoitruongnhomhientai = self.moitruong.get_idnguoichoitruongnhom()
                        if idnguoichoitruongnhomhientai != idnhanvattruongnhom and idnguoichoi in NHANVATTODOITUDONGs:
                            danhsachidnguoichoixungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()
                            if idnhanvattruongnhom in danhsachidnguoichoixungquanhs and idnhanvattruongnhom not in self.moitruong.get_danhsachidnguoichoithanhviennhoms():
                                self.moitruong.action_thoatkhoinhom(idnguoichoitruongnhomhientai)
                                break
                    else:
                        self.moitruong.action_kiemtravadongyloimoinhom(idnhanvattruongnhom)
                        break
                break

    def action_tudongphucsinh(self):
        if self._is_tudongphucsinh:
            while True:
                if not self.moitruong.get_is_nhanvatdachet():
                    self._thoidiemnhanvatchetgannhat = time.time()
                else:
                    if time.time() - self._thoidiemnhanvatchetgannhat > 0.5:
                        self._idbandovuachet = self.moitruong.get_idbandohientai()
                    if time.time() - self._thoidiemnhanvatchetgannhat > 4.:
                        self.moitruong.action_phucsinh(is_duoccuu = True)
                    elif time.time() - self._thoidiemnhanvatchetgannhat > 8.:
                        self.moitruong.action_phucsinh()
                break

    def action_tudongdoimaupk(self):
        if self._is_tudongdoimaupk:
            if time.time() - self._thoidiemdoimaupkgannhat > 5.:
                self._thoidiemdoimaupkgannhat = time.time()
                self.action_batpk()

    def action_batpk(self):
        self.moitruong.action_doimaupk(MAUPK_BANG)

    def action_tatpk(self):
        self.moitruong.action_doimaupk(MAUPK_HOABINH)

    def action_tudongsuado(self):
        if self._is_tudongsuado:
            if time.time() - self._thoidiemkiemtranpcsuadogannhat < 2.:
                return
            self._thoidiemkiemtranpcsuadogannhat = time.time()

            diachicosothongtinnhanvatchutiemsuachua = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)

            if diachicosothongtinnhanvatchutiemsuachua and self.moitruong.get_khoangcach(diachicosothongtinnhanvatchutiemsuachua) <= 6:
                self.moitruong.action_suado(diachicosothongtinnhanvatchutiemsuachua)

    def action_sudungvatphamhanhtrang(self, tenvatpham, delay = 0.25):
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False

        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(tenvatpham)

        if not iddoituongvatpham:
            return False

        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham)
        if is_ok:
            self._thoidiemsudungvatphamgannhat = time.time()

        return is_ok

    def action_tudongkhamdenkhithatbai(self):
        noidungthongbaotruocdo = False

        while True:
            noidungthongbaogannhat = self.moitruong.get_noidungthongbaogannhat()
            if noidungthongbaotruocdo:
                if noidungthongbaogannhat == noidungthongbaotruocdo:
                    time.sleep(0.05)
                    continue

                # if "Tháº¥t Báº¡i" in noidungthongbaogannhat:
                #     break

                if "ThÃ nh CÃ´ng [18/20]" in noidungthongbaogannhat:
                    break

            self.action_tudongepdomotlan(delay = 0.)
            time.sleep(0.05)

            noidungthongbaotruocdo = noidungthongbaogannhat

    def action_tudongepdomotlan(self, delay = 0.05):
        if time.time() - self._thoidiemepdogannhat < delay:
            return

        iddoituongvatphamhanhtrang2 = self.moitruong.get_iddoituongvatphamhanhtrang(1)
        if not iddoituongvatphamhanhtrang2:
            return

        iddoituongvatphamhanhtrang1 = self.moitruong.get_iddoituongvatphamhanhtrang(0)
        if not iddoituongvatphamhanhtrang1:
            return

        self._thoidiemepdogannhat = time.time()

        self.moitruong.action_thucthicaulenh("move ! {}# 1".format(hex(iddoituongvatphamhanhtrang2)).replace("0x", ""), delay = 0.)

    def action_tudongepdo78910(self, delay = 0.25):
        if time.time() - self._thoidiemepdogannhat < delay:
            return

        tenvatpham2 = self.moitruong.get_tenvatphamhanhtrang(1)

        if not tenvatpham2:
            return

        iddoituongvatphamhanhtrang2 = self.moitruong.get_iddoituongvatphamhanhtrang(1)
        if not iddoituongvatphamhanhtrang2:
            return

        self._thoidiemepdogannhat = time.time()

        sdfjhsdfsdf = 0

        while sdfjhsdfsdf <= 10:
            sdfjhsdfsdf += 1
            iddoituongvatphamhanhtrang1 = self.moitruong.get_iddoituongvatphamhanhtrang(0)
            if not iddoituongvatphamhanhtrang1:
                break

            iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(tenvatpham2)

            if not iddoituongvatpham:
                break

            self.moitruong.action_dichuyenvatphamhanhtrang(iddoituongvatpham, 1)
            time.sleep(0.25)

            caulenh = "mix40262 0# {}# {}#".format(hex(iddoituongvatphamhanhtrang1), hex(iddoituongvatpham)).replace("0x", "")

            self.moitruong.action_thucthicaulenh(caulenh)

            time.sleep(0.25)

        if self.moitruong.get_is_danghiencuasotuychon():
            self.moitruong.set_is_danghiencuasotuychon(False)

    def action_tudongepdo1112(self, delay = 0.25):
        if time.time() - self._thoidiemepdogannhat < delay:
            return

        iddoituongvatphamhanhtrang2 = self.moitruong.get_iddoituongvatphamhanhtrang(1)
        if not iddoituongvatphamhanhtrang2:
            return

        self._thoidiemepdogannhat = time.time()

        iddoituongvatphamhanhtrang1 = self.moitruong.get_iddoituongvatphamhanhtrang(0)
        if not iddoituongvatphamhanhtrang1:
            return

        self.moitruong.action_dichuyenvatphamhanhtrang(iddoituongvatphamhanhtrang2, 1)
        time.sleep(0.25)

        caulenh = "mix111255 0# {}# {}#".format(hex(iddoituongvatphamhanhtrang1), hex(iddoituongvatphamhanhtrang2)).replace("0x", "")

        if random.randint(0, 10) < 10:
            time.sleep(0.01)

        self.moitruong.action_thucthicaulenh(caulenh, delay = 0)

        time.sleep(0.25)

        if self.moitruong.get_is_danghiencuasotuychon():
            self.moitruong.set_is_danghiencuasotuychon(False)

    def action_tudonghopthanhlinhthach(self, delay = 0.5):
        while True:
            vatphamhanhtrang_map = self.moitruong.get_danhsachvatphamhanhtrang_map()

            for tenvatpham, vitrivatphams in vatphamhanhtrang_map.items():
                if len(vitrivatphams) < 5:
                    continue

                if not tenvatpham:
                    continue

                if tenvatpham in ("TÃºi Linh Tháº¡ch cáº¥p 1", ):
                    continue


                caulenh = "mix5 {}".format(" ".join(["{}#".format(hex(vitrivatpham[1])) for vitrivatpham in vitrivatphams[:5]])).replace("0x", "")

                self.moitruong.action_thucthicaulenh(caulenh, delay = delay)
                time.sleep(0.5)

            break

    def action_tudongxepchongdo(self, delay = 0.5):
        if self._is_tudongxepchongdo and VATPHAMXEPCHONGs:
            while True:
                if time.time() - self._thoidiemxepchongdogannhat < delay:
                    break

                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
                    break

                vatphamhanhtrang_map = self.moitruong.get_danhsachvatphamhanhtrang_map()

                for tenvatpham, vitrivatphams in vatphamhanhtrang_map.items():
                    if tenvatpham not in VATPHAMXEPCHONGs:
                        continue

                    if len(vitrivatphams) <= 1:
                        continue

                    for vitrivatpham in vitrivatphams[1:]:
                        is_ok = self.moitruong.action_dichuyenvatphamhanhtrang(vitrivatpham[1], vitrivatphams[0][0] + 1, delay = delay)
                        if is_ok:
                            self._thoidiemxepchongdogannhat = time.time()
                break

    def action_tudongtrieuhoibaothudautien(self):
        if self._is_tudongtrieuhoibaothudautien:
            while True:
                if self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs or time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() < 1.:
                    break

                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
                    break

                if self._is_tamngungdichuyensudungkynang:
                    break

                iddoituongbaothudautien = self.moitruong.get_iddoituongbaothudautien()

                if not iddoituongbaothudautien:
                    break

                if self.moitruong.get_is_datrieuhoibaothu():
                    if time.time() - self._thoidiemsudungthucanbaothugannhat > 120.:
                        iddoituongcaocapbaothuthucpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPBAOTHUTHUCPHAM)
                        if iddoituongcaocapbaothuthucpham:
                            is_ok = self.moitruong.action_sudungvatphambaothu(iddoituongcaocapbaothuthucpham, iddoituongbaothudautien, delay = 0.5)
                            if is_ok:
                                self._thoidiemsudungthucanbaothugannhat = time.time()
                    diachicosonhanvatbaothudautien = self.moitruong.action_timkiemnhanvat(iddoituong = iddoituongbaothudautien)

                    if diachicosonhanvatbaothudautien and time.time() - self._thoidiemthietlapbaothuchodoigannhat > 2.:
                        is_ok = self.moitruong.action_sudungkynangbaothu(iddoituongbaothudautien, 3, delay = 0.5)
                        if is_ok:
                            self._thoidiemthietlapbaothuchodoigannhat = time.time()
                    break

                if time.time() - self._thoidiemtudongtrieuhoibaothudautien > 1. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                    is_ok = self.moitruong.action_trieuhoibaothu(iddoituongbaothudautien, delay = 0.5)
                    if is_ok:
                        self._thoidiemtudongtrieuhoibaothudautien = time.time()
                    break

                break

    def action_tudongcuoithu(self):
        if self._is_tudongtrieuhoithanthu:
            if time.time() - self._thoidiemkiemtracuoithugannhat < 2.:
                return

            if self.moitruong.get_is_dangvankhi():
                return

            if self.moitruong.get_is_dangclickchuottrai():
                return

            if self.moitruong.get_is_nhanvatdachet():
                return
            
            if self.moitruong.get_idthucuoi() or time.time() - self.moitruong._thoidiemkhongcuoithugannhat < 2.:
                return

            if not self.moitruong.get_is_dathietlapkynangphimtat(VITRIPHIMTATKYNANG_THUCANTHUCUOI):
                return

            self._thoidiemkiemtracuoithugannhat = time.time()

            self.moitruong.action_sudungkynangphimtat(VITRIPHIMTATKYNANG_THUCANTHUCUOI)
