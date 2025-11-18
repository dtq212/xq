import random
import time

import pymem

from hangso import *
from moitruong import MoiTruong
from tienich import luuthietlap as util_luuthietlap
from tienich import taithietlap as util_taithietlap, phatam


class TacTu:
    def __init__(self, moitruong: MoiTruong):
        self._is_tudonglamnhiemvulaoquangia = False
        self._is_tudongcatdovaoruong = True
        self._is_thucsondao = False
        self.moitruong = moitruong

        # Thiết lập không lưu
        self._is_tudongtheosautruongnhom = True
        self._is_vohieuhoadichuyen = False
        # Thiết lập có lưu
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
        self._is_phitac = False

        self._is_uutiennguoichoi = True

        self._khoangcachtoidatruongnhom = 12

        self._tenmuctieutancongs = set()
        self._tenmuctieukhongtancongs = set(TENMUCTIEUKHONGTANCONGs)

        self._tenvatphamnhats = set()

        self._thoigiantamngungauto = time.time()

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
        self._thoidiemsudungsinhkhitangannhat = time.time()  # - 300.
        self._thoidiemsudungsotriduocgannhat = time.time()
        self._thoidiemsudungphihanhphugannhat = time.time()
        self._thoidiemsudungkimcuongbathoaidongannhat = time.time()
        self._thoidiemdichuyenlenbandovuachetgannhat = time.time()
        self._thoidiemepdogannhat = time.time()
        self._thoidiemsudunghoithanhphugannhat = time.time()
        self._thoidiemxepchongdogannhat = time.time()
        self._thoidiemvutdogannhat = time.time()
        self._thoidiemsudungtaitaohoangannhat = time.time()

        self._diachicosovatphamkhongnhats = []
        self._diachicosovatphamkhongnhat_map = {}
        self._thoidiemlammoivatphamkhongnhatgannhat = time.time()
        self._thoidiemthaydoivatphamdangnhatgannhat = time.time()
        self._diemdanhxungquanhs = []
        self._iddiemdanhxungquanhhientai = -1
        self._diemdanhxungquanhhientai = False
        self._thoidiemthaydoidiemdanhxungquanhgannhat = time.time()
        self._khoangcachdiemdanhxungquanh = 27.

        self._yeucaunhatdo = None
        self._yeucautheonhom = None
        self._yeucautancong = None
        self._yeucautudo = None

        self._is_tamngungdichuyensudungkynang = False
        self._khoangcachtimkiemmuctieu = 18.
        self._is_tudongtrieuhoithanthu = True
        self._is_tudongdichuyendiemdanhxungquanh = False
        self._is_tudongdoimaupk = True

        self._idbandohientai = False
        self._phehientai = False

        self._idbandovuachet = False

        self._diachicosovatphamdangnhat = False

        self._solansudungkhaithientichdia = 0
        self._solansudungluutinhtruymang = 0

        self._is_chantangcapdo = True

    def __del__(self):
        try:
            self.moitruong.action_bochantangcapdo()
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
            "_is_chantangcapdo": self._is_chantangcapdo,
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

            if "_is_chantangcapdo" in thietlap:
                self._is_chantangcapdo = thietlap["_is_chantangcapdo"]

    def action_xulydichuyenuutien(self):
        if self.moitruong.get_is_nhanvatdachet():
            return
        if self.moitruong.get_is_dangclickchuottrai():
            return
        if self.moitruong.get_is_dangvankhi():
            return
        if self._is_tamngungdichuyensudungkynang:
            # print("self._is_tamngungdichuyensudungkynang")
            return

        yeucauduocchon = None

        if self._yeucaunhatdo:
            yeucauduocchon = self._yeucaunhatdo
            # print(f"yeucauduocchon: self._yeucaunhatdo: {yeucauduocchon}")

        elif self._yeucautheonhom:
            yeucauduocchon = self._yeucautheonhom
            # print(f"yeucauduocchon: self._yeucautheonhom: {yeucauduocchon}")

        elif self._yeucautancong:
            yeucauduocchon = self._yeucautancong
            # print(f"yeucauduocchon: self._yeucautancong: {yeucauduocchon}")

        elif self._yeucautudo:
            yeucauduocchon = self._yeucautudo
            # print(f"yeucauduocchon: self._yeucautudo: {yeucauduocchon}")

        if yeucauduocchon:
            toadodich = yeucauduocchon.get("toadodich")
            diachimuctieu = yeucauduocchon.get("diachimuctieu")

            kieudichuyen = yeucauduocchon.get("kieudichuyen", KIEUDICHUYEN_GIUKHOANGCACHTOIDA)

            if kieudichuyen == KIEUDICHUYEN_GIUKHOANGCACHTOIDA:
                khoangcachtoida = yeucauduocchon.get("khoangcachtoida", 0.0)
                if toadodich:
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(
                        toadodich[0],
                        toadodich[1],
                        khoangcachtoida
                    )
                elif diachimuctieu:
                    self.moitruong.action_dichuyengiukhoangcachtoida(
                        diachimuctieu,
                        khoangcachtoida
                    )

            elif kieudichuyen == KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU:
                khoangcachtoithieu = yeucauduocchon.get("khoangcach", 1.0)
                if toadodich:
                    self.moitruong.action_dichuyengiukhoangcachtoithieudiem(
                        toadodich[0],
                        toadodich[1],
                        khoangcachtoithieu
                    )
                elif diachimuctieu:
                    self.moitruong.action_dichuyengiukhoangcachtoithieu(
                        diachimuctieu,
                        khoangcachtoithieu
                    )

    def _action_theonhom(self):
        self._yeucautheonhom = None

        if not self._is_tudongtheosautruongnhom:
            return

        while True:
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
            if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO):
                break

            if self._is_tudongbattheosaunhom and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THEOSAUNHOM,), True, is_hieuungcoloi = 1):
                self.moitruong.action_battheosaunhom(2.)

            xtruongnhom = self.moitruong.get_toadoxtruongnhom()
            ytruongnhom = self.moitruong.get_toadoytruongnhom()

            if not xtruongnhom and not ytruongnhom:
                break

            khoangcachtruongnhom = self.moitruong.get_khoangcachdiem(xtruongnhom, ytruongnhom)
            khoangcachtoidatruongnhom = self._khoangcachtoidatruongnhom

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon):
                if self.moitruong.get_tenmonphai() != "vanmongcoc":
                    khoangcachtoidatruongnhom -= 6.
                else:
                    khoangcachtoidatruongnhom -= 3

            if khoangcachtruongnhom <= khoangcachtoidatruongnhom:
                break
            if khoangcachtruongnhom >= KHOANGCACHTOIDAHOPLE:
                break

            self._yeucautheonhom = {
                "yeucau": YEUCAUDICHUYENTHEONHOM,
                "toadodich": (xtruongnhom, ytruongnhom),
                "khoangcachtoida": khoangcachtoidatruongnhom - 1.5
            }
            break
        return

    def action_tudongtimkiemmuctieu(self):
        if self._is_tudongtimkiemmuctieu:
            i = 0

            while True:
                idbandohientai = self.moitruong.get_idbandohientai()
                is_bandokhongtancong = idbandohientai in BANDOKHONGTANCONGs

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                if diachicosothongtinnhanvatmuctieudangchon:
                    tendoituongmuctieudangchon = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)
                    if is_bandokhongtancong:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif tendoituongmuctieudangchon in TENNHANVATKHONGTANCONGs:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif self._is_phitac and not is_muctieudangchonlanguoichoi and tendoituongmuctieudangchon not in PHITACs:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif self._tenmuctieutancongs and tendoituongmuctieudangchon not in self._tenmuctieutancongs:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif self._tenmuctieukhongtancongs and tendoituongmuctieudangchon in self._tenmuctieukhongtancongs:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif self._is_chidanhnguoichoi and not is_muctieudangchonlanguoichoi:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                    elif is_muctieudangchonlanguoichoi and self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieudangchon) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

                if is_bandokhongtancong:
                    break

                diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtinnhanvatmuctieuxemxet:
                    break

                i += 1

                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                tendoituongmuctieuxemxet = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet)

                if tendoituongmuctieuxemxet in TENNHANVATKHONGTANCONGs:
                    continue

                if self._is_phitac:
                    if not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieuxemxet) and tendoituongmuctieuxemxet not in PHITACs:
                        continue

                if self._tenmuctieutancongs:
                    if tendoituongmuctieuxemxet not in self._tenmuctieutancongs:
                        continue

                if self._tenmuctieukhongtancongs:
                    if tendoituongmuctieuxemxet in self._tenmuctieukhongtancongs:
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
                is_muctieudangxemxetlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieuxemxet)

                if self._is_uutiennguoichoi:
                    if is_muctieudangxemxetlanguoichoi:
                        if not is_muctieudangchonlanguoichoi:
                            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
                            continue
                    elif is_muctieudangchonlanguoichoi:
                        continue

                if is_muctieudangchonlanguoichoi and self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieudangchon) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                    if is_muctieudangxemxetlanguoichoi:
                        if self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieuxemxet) > 5 or not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)
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

                if self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHAPLUCTHACH,), True, is_hieuungcoloi = 1):
                    self.action_sudungvatphamhanhtrang(TIEUPHAPLUCTHACH)

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
                if diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NHANSAM,), True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(NHANSAM)

            if self.moitruong.get_diempk() > 0:
                self.action_sudungvatphamhanhtrang(ANXAPHU)

            if time.time() - self._thoidiemsudungsinhkhitangannhat > 10.:
                is_ok = self.action_sudungvatphamhanhtrang(SINHKHITAN)
                if is_ok:
                    self._thoidiemsudungsinhkhitangannhat = time.time()

            tenmonphai = self.moitruong.get_tenmonphai()

            if time.time() - self._thoidiemsudungkimcuongbathoaidongannhat >= .5 and self.moitruong.get_phantramsinhlucconlai() <= 25.:
                if tenmonphai != "thucson" or (not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH) and 0 < self.moitruong.get_thoigianconlaihieuungtienthanvodich(macdinh = 2.0) <= 1.5):
                    self._thoidiemsudungkimcuongbathoaidongannhat = time.time()
                    self.action_sudungvatphamhanhtrang(KIMCUONGBATHOAIDON)

            if time.time() - self._thoidiemsudungtaitaohoangannhat >= .5 and self.moitruong.get_phantramsinhlucconlai() <= 5. and 0 < self.moitruong.get_thoigianconlaihieuungkimcuongbathoaidon(macdinh = 2.0) <= 1.5:
                self._thoidiemsudungtaitaohoangannhat = time.time()
                self.action_sudungvatphamhanhtrang(TAITAOHOAN)

            if time.time() - self._thoidiemsudungsotriduocgannhat > 2. and self.moitruong.get_phantramsinhlucconlai() <= 25.:
                self._thoidiemsudungsotriduocgannhat = time.time()
                self.action_sudungvatphamhanhtrang(SOTRIDUOC)

    def _action_sudungkynang(self):
        tenmonphai = self.moitruong.get_tenmonphai()

        self._is_tamngungdichuyensudungkynang = False

        self._yeucautancong = None

        if tenmonphai == "vanmongcoc":
            self._action_sudungkynang_vanmongcoc()
        elif tenmonphai == "thucson":
            self._action_sudungkynang_thucson()
        elif tenmonphai == "daohoanguyen":
            self._action_sudungkynang_daohoanguyen()

    def _action_sudungkynang_vanmongcoc(self):
        if not self._is_tudongsudungkynang:
            return

        while True:
            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self.moitruong.get_is_dangvankhi():
                break

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()

            if phantramsinhlucconlai > 50:
                idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
                i = -1
                diachicosothongtinnhanvatnguoichoithanhviennhoms = []
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
                        diachicosothongtinnhanvatnguoichoithanhviennhoms.append(diachicosothongtinnhanvatxemxet)

                diachicosothongtinnhanvatdachet = False
                diachicosothongtinnhanvatphantramsinhlucthapnhat = False
                phantramsinhlucconlaithapnhat = 100.
                diachicosothongtinnhanvatchuacobuffnoicong = False

                for diachicosothongtinnhanvatnguoichoithanhviennhom in diachicosothongtinnhanvatnguoichoithanhviennhoms:
                    if self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatnguoichoithanhviennhom):
                        diachicosothongtinnhanvatdachet = diachicosothongtinnhanvatnguoichoithanhviennhom
                        break
                    phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatnguoichoithanhviennhom)
                    if phantramsinhlucconlai < phantramsinhlucconlaithapnhat:
                        diachicosothongtinnhanvatphantramsinhlucthapnhat = diachicosothongtinnhanvatnguoichoithanhviennhom
                        phantramsinhlucconlaithapnhat = phantramsinhlucconlai
                    if phantramsinhlucconlai >= 90. or self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs:
                        if not diachicosothongtinnhanvatchuacobuffnoicong and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 1):
                            diachicosothongtinnhanvatchuacobuffnoicong = diachicosothongtinnhanvatnguoichoithanhviennhom

                if diachicosothongtinnhanvatdachet and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAITUHOANSINH, delay = 2.):
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CAITUHOANSINH, diachicosothongtinnhanvatdachet, is_khongkiemtracothetancong = True)
                    break

                if diachicosothongtinnhanvatphantramsinhlucthapnhat and phantramsinhlucconlaithapnhat <= 90.:
                    self._is_tamngungdichuyensudungkynang = True
                    if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAMLOTRI):
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CAMLOTRI, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                            break
                    if phantramsinhlucconlaithapnhat <= 90. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SOTRI):
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_SOTRI, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                            break
                    if phantramsinhlucconlaithapnhat <= 90. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHIETVANQUYET):
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KHIETVANQUYET, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                            break
                    if phantramsinhlucconlaithapnhat <= 90. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VODINHLUUTHUY):
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VODINHLUUTHUY, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                            break

                if diachicosothongtinnhanvatchuacobuffnoicong and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCHAMDOACH):
                    self._is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KIMCHAMDOACH, diachicosothongtinnhanvatchuacobuffnoicong, is_khongkiemtracothetancong = True)
                    break

            if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAMLOTRI):
                self._is_tamngungdichuyensudungkynang = True
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                    self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_CAMLOTRI)
                break
            if phantramsinhlucconlai <= 90. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHIETVANQUYET):
                self._is_tamngungdichuyensudungkynang = True
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                    self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_KHIETVANQUYET)
                break
            if phantramsinhlucconlai <= 90. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SOTRI):
                self._is_tamngungdichuyensudungkynang = True
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                    self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_SOTRI)
                break
            if phantramsinhlucconlai <= 90. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VODINHLUUTHUY):
                self._is_tamngungdichuyensudungkynang = True
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                    self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_VODINHLUUTHUY)
                break

            if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon):
                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, is_hieuungcoloi = 1):
                    self._is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_KIMCHAMDOACH)
                    break

            if diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                if thoigiantuthenhanvatdungim > 0.5 and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA - 3:
                    if thoigiantuthenhanvatdungim > 4.5:
                        # print(f"VMC Phat hien KET CUNG (dung im > 4.5s). Yeu cau di chuyen vao 0. Khoang cach: {khoangcach}")
                        khoangcachgiutoida = 0
                    else:
                        khoangcachgiutoida = (KHOANGCACHSUDUNGKYNANGTAMXA - 3) - (1.5 + thoigiantuthenhanvatdungim)
                        # print(f"VMC Phat hien Desync/Stuck (dung im > 0.5s). Yeu cau di chuyen, khoangcachgiutoida: {khoangcachgiutoida}. Khoang cach: {khoangcach}")

                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": khoangcachgiutoida
                    }
                    break
                else:
                    if is_muctieudangchonlanguoichoi and self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                        if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA - 3:
                            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGANTHUAT):
                                self._is_tamngungdichuyensudungkynang = True
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGANTHUAT)
                                break
                            elif not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYENQUANGTHIEMANH):
                                self._is_tamngungdichuyensudungkynang = True
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HUYENQUANGTHIEMANH)
                                break
                    if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA - 3:
                        phantramnoiluc = int(self.moitruong.get_noilucconlai() * 100 / self.moitruong.get_noiluctoida())
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHAYMAU,), diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, macdinh = True, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGVUKINHTHIEN):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGVUKINHTHIEN)
                            break
                        elif phantramnoiluc > 25 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KYMONTRAN, delay = 1.):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KYMONTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - random.randint(-1, 1))
                            break
                        elif phantramnoiluc > 25 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONGIAPTRAN, delay = 1.):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_DONGIAPTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - random.randint(-1, 1))
                            break
            break
        return

    def _action_sudungkynang_thucson(self):
        if self._is_thucsondao:
            self._action_sudungkynang_thucsondao()
        else:
            self._action_sudungkynang_thucsonkiem()

    def _action_sudungkynang_thucsonkiem(self):
        if not self._is_tudongsudungkynang:
            return

        while True:
            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self.moitruong.get_is_dangvankhi():
                break

            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()

            is_muctieudangchonlanguoichoi = False
            khoangcach = KHOANGCACHTOIDAHOPLE
            is_muctieudangchonbichoang = False
            is_muctieuchaytron = False
            is_cothetancong = False

            if diachicosothongtinnhanvatmuctieudangchon:
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_muctieuchaytron = self.moitruong.get_is_muctieuchaytron(diachicosothongtinnhanvatmuctieudangchon)
                is_cothetancong = self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)

            is_duoitheonguoichoi = is_muctieudangchonlanguoichoi and khoangcach >= 6. and is_muctieuchaytron and not self.moitruong.get_is_vohieuhoadichuyen()

            if not diachicosothongtinnhanvatmuctieudangchon or not is_muctieudangchonlanguoichoi:
                if self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                        break
                if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    self._is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                    break
                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    self._is_tamngungdichuyensudungkynang = True
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                    break
                if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGPHACHNGANTAM):
                        self._is_tamngungdichuyensudungkynang = True
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BANGPHACHNGANTAM)
                        break

            is_bandocuthudao = self.moitruong.get_idbandohientai() == BANDO_CUTHUDAO

            if phantramsinhlucconlai <= 25 or (is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 50) or (is_bandocuthudao and is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 75):
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH)
                    break
            if is_bandocuthudao and is_muctieudangchonlanguoichoi and time.time() - self._thoidiemsudungphihanhphugannhat > 1. and phantramsinhlucconlai <= 25. and not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH) and self.moitruong.get_thoigianconlaihieuungtienthanvodich(macdinh = 2.5) < 2.:
                self._thoidiemsudungphihanhphugannhat = time.time()
                self.action_sudungvatphamhanhtrang(PHIHANHPHU)
                break
                
            if diachicosothongtinnhanvatmuctieudangchon and is_cothetancong:
                if not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA):
                    self._solansudungkhaithientichdia = 0

                if is_duoitheonguoichoi:
                    if idtuthenhanvat == TUTHENHANVAT_DICHUYEN and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG) and not self.moitruong.get_is_vohieuhoadichuyen():
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUUTINHTRUYMANG)
                    # elif idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA) and not self.moitruong.get_is_vohieuhoadichuyen():
                    #     self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach)
                    else:
                        thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                        self._yeucautancong = {
                            "yeucau": YEUCAUDICHUYENTANCONG,
                            "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                            "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                            "khoangcachtoida": khoangcach - thoigiantuthenhanvatdungim - 3.
                        }

                elif is_muctieudangchonlanguoichoi and khoangcach <= 3 and idtuthenhanvat == TUTHENHANVAT_DICHUYEN and not self.moitruong.get_is_vohieuhoadichuyen():
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA, delay = min(1., 0.1 * self._solansudungkhaithientichdia)):
                        is_ok = self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - KHOANGCACHSUDUNGKYNANGTAMXA)
                        if is_ok:
                            self._solansudungkhaithientichdia += 1

                elif not is_duoitheonguoichoi:
                    thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                    if thoigiantuthenhanvatdungim > 0.5 and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA - 3:
                        if thoigiantuthenhanvatdungim > 4.5:
                            # print(f"Phat hien KET CUNG (dung im > 4.5s). Yeu cau di chuyen vao 0. Khoang cach: {khoangcach}")
                            khoangcachgiutoida = 0
                        else:
                            khoangcachgiutoida = KHOANGCACHSUDUNGKYNANGTAMXA - (1.5 + thoigiantuthenhanvatdungim)
                            # print(f"Phat hien Desync/Stuck (dung im > 1s). Yeu cau di chuyen, khoangcachgiutoida: {khoangcachgiutoida}. Khoang cach: {khoangcach}")
                        self._yeucautancong = {
                            "yeucau": YEUCAUDICHUYENTANCONG,
                            "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                            "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                            "khoangcachtoida": khoangcachgiutoida
                        }
                        break
                    else:
                        if is_muctieudangchonlanguoichoi and not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LANGKHONGCHIHUYET):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LANGKHONGCHIHUYET)
                            break
                        elif is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not is_muctieudangchonbichoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUCPHACHHOASON)
                            break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANKIEMXUYENTAM):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANKIEMXUYENTAM)
                            break
                        elif khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and not is_bandocuthudao and not is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN) and self.moitruong.get_noilucconlai() > 70:
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN)
                            break
                        elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMTHUAT):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGUKIEMTHUAT)
                            break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANVUTIEUDIEU):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANVUTIEUDIEU)
                            break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGTAMTHUC):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BANGTAMTHUC)
                            break
                        elif khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN) and self.moitruong.get_noilucconlai() > 70:
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN)
                            break
                        elif self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                                break
                        elif phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                            self._is_tamngungdichuyensudungkynang = True
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                            break
                        elif is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                            if self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAMATRAM)
                                break
                        else:
                            if not diachicosothongtinnhanvatmuctieudangchon or not is_muctieudangchonlanguoichoi:
                                j = -1

                                idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

                                while True:
                                    j += 1
                                    diachicosothongtinnhanvatxemxet = self.moitruong.get_diachicosothongtindoituongx(j)
                                    if not diachicosothongtinnhanvatxemxet:
                                        break
                                    if not self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                                        continue
                                    idnguoichoi = self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
                                    if not idnguoichoi:
                                        continue

                                    if idnguoichoi in idnguoichoithanhviennhoms and self.moitruong.get_khoangcach(diachicosothongtinnhanvatxemxet) <= KHOANGCACHSUDUNGKYNANGTAMXA:
                                        if not self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatxemxet):
                                            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), diachicosothongtinnhanvat = diachicosothongtinnhanvatxemxet, macdinh = True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                                                self._is_tamngungdichuyensudungkynang = True
                                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TIEUCHUTHIEN, diachicosothongtinnhanvatmuctieu = diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                                break
                            if not is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENNHANCHILO):
                                self._is_tamngungdichuyensudungkynang = True
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TIENNHANCHILO)
                                break
            break
        return

    def _action_sudungkynang_thucsondao(self):
        if not self._is_tudongsudungkynang:
            return

        while True:
            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self.moitruong.get_is_dangvankhi():
                break

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
            is_cothetancong = False
            khoangcach = KHOANGCACHTOIDAHOPLE

            if diachicosothongtinnhanvatmuctieudangchon:
                is_cothetancong = self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)
                if is_cothetancong:
                    khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

            if diachicosothongtinnhanvatmuctieudangchon and is_cothetancong:
                if idtuthenhanvat != TUTHENHANVAT_DICHUYEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG):
                    if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                        self._yeucautancong = {
                            "yeucau": YEUCAUDICHUYENTANCONG,
                            "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                            "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                            "khoangcach": khoangcach + 1.5
                        }
                        break

                if khoangcach <= KHOANGCACHTOIDAHOPLE:
                    thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                    if thoigiantuthenhanvatdungim > 0.5:

                        khoangcachtoida_yeucau = KHOANGCACHSUDUNGKYNANGCANCHIEN
                        if (thoigiantuthenhanvatdungim > 2.0 or self._solansudungluutinhtruymang >= 5) and khoangcach >= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                            khoangcachtoida_yeucau = 0
                        elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG) and khoangcach > 1.5:
                            khoangcachtoida_yeucau = khoangcach - 1.5

                        self._yeucautancong = {
                            "yeucau": YEUCAUDICHUYENTANCONG,
                            "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                            "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                            "khoangcachtoida": khoangcachtoida_yeucau
                        }
            break
        return

    def _action_sudungkynang_daohoanguyen(self):
        if not self._is_tudongsudungkynang:
            return

        while True:
            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self.moitruong.get_is_dangvankhi():
                break

            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRANCOTHANUY,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TRANCOTHANUY):
                self._is_tamngungdichuyensudungkynang = True 
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TRANCOTHANUY)
                break

            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMTRUNGCHAO,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMTRUNGCHAO):
                self._is_tamngungdichuyensudungkynang = True 
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KIMTRUNGCHAO)
                break

            if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCUONGTHANPHAP,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCUONGTHANPHAP):
                        self._is_tamngungdichuyensudungkynang = True 
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KIMCUONGTHANPHAP)
                            break
                break

            break

        return

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

    def battat_is_chantangcapdo(self):
        self._is_chantangcapdo = not self._is_chantangcapdo
        if self._is_chantangcapdo:
            phatam("Bật chặn tăng cấp độ")
        else:
            phatam("Tắt chặn tăng cấp độ")

    def battat_is_tudongdichuyendiemdanhxungquanh(self):
        self._is_tudongdichuyendiemdanhxungquanh = not self._is_tudongdichuyendiemdanhxungquanh
        if self._is_tudongdichuyendiemdanhxungquanh:
            phatam("Bật tự động di chuyển điểm đánh xung quanh")
        else:
            phatam("Tắt tự động di chuyển điểm đánh xung quanh")
        self._iddiemdanhxungquanhhientai = False
        self._diemdanhxungquanhhientai = False

    def battat_is_tudongbattheosaunhom(self):
        self._is_tudongbattheosaunhom = not self._is_tudongbattheosaunhom
        if self._is_tudongbattheosaunhom:
            phatam("Bật tự động bật tắt theo sau nhóm")
        else:
            phatam("Tắt tự động bật tắt theo sau nhóm")

    def battat_is_phitac(self):
        self._is_phitac = not self._is_phitac
        if self._is_phitac:
            phatam("Bật phi tặc")
        else:
            phatam("Tắt phi tặc")

    def battat_is_tudongtheosautruongnhom(self):
        self._is_tudongtheosautruongnhom = not self._is_tudongtheosautruongnhom
        if self._is_tudongtheosautruongnhom:
            phatam("Bật tự động theo sau trưởng nhóm")
        else:
            phatam("Tắt tự động theo sau trưởng nhóm")

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

    def them_tenmuctieukhongtancong(self, tenmuctieukhongtancong):
        if tenmuctieukhongtancong and tenmuctieukhongtancong not in self._tenmuctieukhongtancongs:
            self._tenmuctieukhongtancongs.add(tenmuctieukhongtancong)

            if self._tenmuctieukhongtancongs:
                print("Danh sách mục tiêu không tấn công: {}".format(self._tenmuctieukhongtancongs))
                phatam("Thêm tên mục tiêu không tấn công. Tổng cộng {}".format(len(self._tenmuctieukhongtancongs)))

    def them_tenvatphamnhat(self, tenvatphamnhat):
        if tenvatphamnhat and tenvatphamnhat not in self._tenvatphamnhats:
            self._tenvatphamnhats.add(tenvatphamnhat)

            if self._tenvatphamnhats:
                print("Danh sách tên vật phẩm nhặt: {}".format(self._tenvatphamnhats))
                phatam("Thêm tên tên vật phẩm nhặt. Tổng cộng {}".format(len(self._tenvatphamnhats)))

    def botoanbo_tenmuctieutancong(self):
        self._tenmuctieutancongs.clear()
        self._tenvatphamnhats.clear()

        phatam("Bỏ thiết lập tên tên vật phẩm nhặt và vật phẩm nhặt".format(len(self._tenmuctieutancongs)))

    def botoanbo_tenmuctieukhongtancong(self):
        self._tenmuctieukhongtancongs = set(TENMUCTIEUKHONGTANCONGs)
        phatam("Bỏ thiết lập tên mục tiêu không tấn công".format(len(self._tenmuctieukhongtancongs)))

    def action_tudongvutdo(self):
        # if time.time() - self._thoidiemvutdogannhat < 2.:
        #     return
        #
        # if not self.moitruong.get_is_dayhanhtrang():
        #     return
        #
        # is_ok = self.moitruong.action_thucthicaulenh("drop ! {}#1".format(hex(iddoituongvatpham)).replace("0x", ""))
        # if is_ok:
        #     self._thoidiemvutdogannhat = time.time()
        return

    def _action_nhatdo(self):
        self._yeucaunhatdo = None

        if not self._is_tudongnhatdo:
            return

        i = 0
        is_bandocuthudao = self.moitruong.get_idbandohientai() == BANDO_CUTHUDAO
        while True:
            if diachicosomuctieudangchon := self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon():
                if self.moitruong.get_is_nguoichoi(diachicosomuctieudangchon) and self.moitruong.get_is_cothetancong(diachicosomuctieudangchon):
                    break
            if self.moitruong.get_is_dayhanhtrang() and not is_bandocuthudao:
                break
            diachicosothongtinvatphamxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachicosothongtinvatphamxemxet:
                break
            i += 1
            if not self.moitruong.get_is_vatphamtontai(diachicosothongtinvatphamxemxet):
                continue
            if time.time() - self._diachicosovatphamkhongnhat_map.get(diachicosothongtinvatphamxemxet, time.time() - 90) < 60:
                continue
            tenvatpham = self.moitruong.get_tendoituong(diachicosothongtinvatphamxemxet)
            if tenvatpham in VATPHAMTUDONGNHATs or (is_bandocuthudao and any(motphantenvatpham2 in tenvatpham for motphantenvatpham2 in VATPHAMTUDONGNHATCUTHUDAOs)):
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinvatphamxemxet)
                if khoangcach <= KHOANGCACHTOANMANHINH:
                    if not self._diachicosovatphamdangnhat or not self.moitruong.get_is_vatphamtontai(self._diachicosovatphamdangnhat) or khoangcach < self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat):
                        if self._diachicosovatphamdangnhat != diachicosothongtinvatphamxemxet:
                            self._diachicosovatphamdangnhat = diachicosothongtinvatphamxemxet
                            self._thoidiemthaydoivatphamdangnhatgannhat = time.time()
                            break

        if self._diachicosovatphamdangnhat:
            tenvatpham = self.moitruong.get_tendoituong(self._diachicosovatphamdangnhat)
        else:
            tenvatpham = ""

        if self._diachicosovatphamdangnhat and self.moitruong.get_is_vatphamtontai(self._diachicosovatphamdangnhat) and (tenvatpham in VATPHAMTUDONGNHATs or (is_bandocuthudao and any(motphantenvatpham in tenvatpham for motphantenvatpham in VATPHAMTUDONGNHATCUTHUDAOs))) and self._diachicosovatphamdangnhat not in self._diachicosovatphamkhongnhats:
            while True:
                if self.moitruong.get_is_dangclickchuottrai():
                    break
                if self.moitruong.get_is_dangvankhi():
                    break
                if self.moitruong.get_is_nhanvatdachet():
                    break

                khoangcach = self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat)
                if khoangcach <= 2.:
                    self.moitruong.action_nhatdo(self._diachicosovatphamdangnhat)

                if self.moitruong.get_tenmonphai() == "thucson" and \
                        self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA, delay = 1.) and \
                        khoangcach >= 3 and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM and \
                        not self._is_tamngungdichuyensudungkynang and not self.moitruong.get_is_vohieuhoadichuyen():

                    self.moitruong.action_sudungkynangvitriphudaudiem(*VITRIKYNANG_KHAITHIENTICHDIA,
                                                                      self.moitruong.get_toadox(self._diachicosovatphamdangnhat, is_vitrihientai = True),
                                                                      self.moitruong.get_toadoy(self._diachicosovatphamdangnhat, is_vitrihientai = True),
                                                                      khoangcachphudau = khoangcach)

                elif khoangcach > 2.0:
                    self._yeucaunhatdo = {
                        "yeucau": YEUCAUDICHUYENNHATDO,
                        "toadodich": (
                            self.moitruong.get_toadox(self._diachicosovatphamdangnhat, is_vitrihientai = True),
                            self.moitruong.get_toadoy(self._diachicosovatphamdangnhat, is_vitrihientai = True)
                        ),
                        "khoangcachtoida": 0
                    }
                if time.time() - self._thoidiemthaydoivatphamdangnhatgannhat > 3. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM and time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat() > 3.:
                    self._diachicosovatphamkhongnhat_map[self._diachicosovatphamdangnhat] = time.time()
                    self._diachicosovatphamdangnhat = False
                break
        return

    def _action_dichuyentudo(self):
        self._yeucautudo = None

        if not self._is_tudongdichuyendiemdanhxungquanh:
            return

        while True:
            idbandohientai = self.moitruong.get_idbandohientai()
            diemdanhxungquanhs = self._diemdanhxungquanhs
            if not diemdanhxungquanhs:
                diemdanhxungquanhs = DIEMDANHXUNGQUANH_MAP.get(idbandohientai)
            if not diemdanhxungquanhs:
                break

            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_dangvankhi():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self._idbandovuachet and self._is_tudongchaylenbandovuachet:
                break

            if self._is_tamngungdichuyensudungkynang:
                break

            thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()
            if self.moitruong.get_idtuthenhanvat() != TUTHENHANVAT_DUNGIM or thoigiantuthenhanvatdungim < 1.:
                break
            if time.time() - self._thoidiemdichuyendiemdanhxungquanhgannhat < 1.:
                break

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
                    iddiemdanhxungquanhtieptheo = ((self._iddiemdanhxungquanhhientai + 1) % len(diemdanhxungquanhbandos)) if (self.moitruong.get_khoangcachdiem(*self._diemdanhxungquanhhientai[:-1]) <= 6. or time.time() - self._thoidiemthaydoidiemdanhxungquanhgannhat > 6. or (time.time() - self._thoidiemthaydoidiemdanhxungquanhgannhat > 2. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM)) else self._iddiemdanhxungquanhhientai
                    diemdanhxungquanhtieptheo = diemdanhxungquanhbandos[iddiemdanhxungquanhtieptheo]

                if iddiemdanhxungquanhtieptheo != self._iddiemdanhxungquanhhientai or self._diemdanhxungquanhhientai != diemdanhxungquanhtieptheo:
                    self._thoidiemthaydoidiemdanhxungquanhgannhat = time.time()
                    self._iddiemdanhxungquanhhientai = iddiemdanhxungquanhtieptheo
                    self._diemdanhxungquanhhientai = diemdanhxungquanhtieptheo

                self._yeucautudo = {
                    "yeucau": YEUCAUDICHUYENDICHUYENTUDO,
                    "toadodich": diemdanhxungquanhtieptheo[:-1],
                    "khoangcachtoida": 0
                }
            else:
                pass
            break
        return

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
                idnguoichoi = self.moitruong.get_idnguoichoi()

                if idnguoichoi not in NHANVATTODOITUDONGs:
                    break

                idnhanvattruongnhom = NHANVATTODOITUDONGs[0]

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

                                break
                    else:
                        self.moitruong.action_moihoacxinvaonhom(idnhanvattruongnhom)

                        break
                else:
                    if self.moitruong.get_is_dangnamtrongnhom():
                        danhsachidthanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
                        danhsachidnguoichoixungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()

                        if idnhanvattruongnhom in danhsachidnguoichoixungquanhs and idnhanvattruongnhom not in self.moitruong.get_danhsachidnguoichoithanhviennhoms():
                            idnguoichoitruongnhomhientai = self.moitruong.get_idnguoichoitruongnhom()
                            if idnguoichoitruongnhomhientai:
                                self.moitruong.action_thoatkhoinhom(idnguoichoitruongnhomhientai)
                                break
                        else:
                            if len(NHANVATTODOITUDONGs) <= 1:
                                break

                            if not self.moitruong.get_is_truongnhom():
                                break

                            for idnguoichoithanhvien in NHANVATTODOITUDONGs[1:]:
                                if idnguoichoithanhvien in danhsachidnguoichoixungquanhs and idnguoichoithanhvien not in danhsachidthanhviennhoms:
                                    self.moitruong.action_moihoacxinvaonhom(idnguoichoithanhvien)

                                    break

                    else:
                        self.moitruong.action_kiemtravadongyloimoinhom(NHANVATTODOITUDONGs)
                        break
                break

    def action_tudongphucsinh(self):
        if self._is_tudongphucsinh:
            while True:
                if not self.moitruong.get_is_nhanvatdachet():
                    self._thoidiemnhanvatchetgannhat = time.time()
                else:
                    if time.time() - self._thoidiemnhanvatchetgannhat > 0.5:
                        idbandohientai = self.moitruong.get_idbandohientai()
                        if idbandohientai in BANDOTUDONGLENSAUKHICHETs:
                            self._idbandovuachet = idbandohientai
                    if time.time() - self._thoidiemnhanvatchetgannhat > 20. and self.moitruong.get_tenmonphai() != "vanmongcoc":
                        self._thoigiantamngungauto = time.time()
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

    def action_sudungvatphamhanhtrang(self, tenvatpham, is_boquaxacnhan = False, delay = 0.25):
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False

        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(tenvatpham)

        if not iddoituongvatpham:
            return False

        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham, is_boquaxacnhan)
        if is_ok:
            self._thoidiemsudungvatphamgannhat = time.time()

        return is_ok

    def action_tudongxepchongdo(self, delay = 0.5):
        if self._is_tudongxepchongdo and VATPHAMXEPCHONGs:
            while True:
                if time.time() - self._thoidiemxepchongdogannhat < delay:
                    break

                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_dangclickchuottrai():
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

    def action_chantangcapdo(self):
        if self._is_chantangcapdo:
            self.moitruong.action_chantangcapdo()
        else:
            self.moitruong.action_bochantangcapdo()
