import ctypes
import datetime
import math
import random
import time

import pymem
import win32gui

from hangso import *
from tienich import *

OFFSET_DIACHICOSOTHONGTINGAME = 0x37FA34

OFFSET_DIACHICOSOTHONGTINNHANVAT1 = 0x37F9E8
OFFSET_DIACHICOSOHIEUUNGNHANVAT = 0x1638
OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT = 0x13C


OFFSET_DIACHICOSOMOIKYNANG = 0x224

OFFSET_DIACHICOSOTHONGTINNHANVATX = 0x1BC950

class MoiTruong:
    def __init__(self, idcuaso):
        self.idcuaso = idcuaso
        idtientrinh = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(self.idcuaso, ctypes.byref(idtientrinh))
        idtientrinh = idtientrinh.value

        self.tientrinh = pymem.Pymem()
        self.tientrinh.open_process_from_id(idtientrinh)

        xqmodule = pymem.process.module_from_name(self.tientrinh.process_handle, "xq.exe")
        if not xqmodule:
            raise Exception("Tìm không thấy module xq.exe. Có vẻ cửa sổ Game không phải cửa sổ Game Chiến Quốc. Vui lòng thử lại")
        self.diachixq = xqmodule.lpBaseOfDll

        kichthuoccuaso = win32gui.GetWindowRect(self.idcuaso)
        if not kichthuoccuaso:
            raise Exception("Lấy kích thước cửa sổ game không thành công")

        #self.kichthuoccuasogame = kichthuoccuaso[2] - kichthuoccuaso[0], kichthuoccuaso[3] - kichthuoccuaso[1]
        self._kichthuoccuasogame = 800., 600.
        self._centerx, self._centery = 430., 300.

        self._is_dasetupautoassemblemocuasotuychonnhanvatchinh = False
        self._is_dasetupautoassemblesudungkynangphimtat = False
        self._is_dasetupautoassembledichuyen = False
        self._is_dasetupautoassemblesudungkynangvitri = False
        self._is_dasetupautoassemblenhatdo = False
        self._is_dasetupautoassemblekhoitaothongtinbando = False
        self._is_dasetupautoassemblethucthicaulenh = False
        self._is_dasetupautoassembletudongtimduong = False

        self._thoidiembattattheosaunhomgannhat = time.time() - 0.5
        self._thoidiemdichuyengannhat = time.time() - 0.5
        self._thoidiemsudungkynangphimtatgannhat_map = {}
        self._thoidiemsudungkynangvitrigannhat_map = {}
        self._thoidiemnhatdogannhat = time.time() - 2.
        self._thoidiemnhatdogannhat_map = {}
        self._thoidiemthucthicaulenhgannhat = time.time() - 0.5
        self._thoidiemthaotacnhomgannhat = time.time() - 1.
        self._thoidiemkhoitaothongtinbandogannhat = time.time() - 0.5
        self._thoidiemtudongtimduonggannhat = time.time() - 1.
        self._thoidiemphucsinhgannhat = time.time() - 1.
        self._thoidiemmaupkgannhat = time.time() - 1.
        self._thoidiemsuadogannhat = time.time() - 1.
        self._thoidiemsudungchucnangmorong5 = time.time() - 2.5
        self._thoidiemtuthenhanvatdungimgannhat = time.time()
        self._thoidiemngungdichuyengannhat = time.time() - 0.25
        self.thoidiemdichuyen1buocgannhat = time.time() - 0.25

        self._is_tamngungtancong = False

        self._is_vohieuhoadichuyen = False

        self._thoidiemkhongcomuctieugannhat = time.time()

        self._soluonghieuungnhanvattruocdo_map = {}
        self._thoidiemsoluonghieuungbangkhonggannhat_map = {}

        self._diachicosothongtinnhanvatmuctieudangchon = False

    def __del__(self):
        if self._is_dasetupautoassemblemocuasotuychonnhanvatchinh:
            self.tientrinh.free(self._diachiautoassemblemocuasotuychonnhanvatchinh)

        if self._is_dasetupautoassemblesudungkynangphimtat:
            self.tientrinh.free(self._diachiautoassemblesudungkynangphimtat)

        if self._is_dasetupautoassembledichuyen:
            self.tientrinh.free(self._diachiautoassembledichuyen)

        if self._is_dasetupautoassemblesudungkynangvitri:
            self.tientrinh.free(self._diachiautoassemblesudungkynangvitri)

        if self._is_dasetupautoassemblenhatdo:
            self.tientrinh.free(self._diachiautoassemblenhatdo)

        if self._is_dasetupautoassemblekhoitaothongtinbando:
            self.tientrinh.free(self._diachiautoassemblekhoitaothongtinbando)

        if self._is_dasetupautoassembletudongtimduong:
            self.tientrinh.free(self._diachiautoassembletudongtimduong)

        if self._is_dasetupautoassemblethucthicaulenh:
            self.tientrinh.free(self._diachiautoassemblethucthicaulenh)

    def get_diachicosothongtinnhanvat1(self):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVAT1)

    def get_diachicosothongtindoituongx(self, x):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVATX + x * 0x4)


    def get_diachicosothongtinvatphamhanhtrang(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFD78)

        return x

    def get_iddoituongvatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return False
        return read_int(self.tientrinh, x + idvitri * 0x4)

    def get_tenvatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return False
        return read_string(self.tientrinh, x + idvitri * 0x4 + 0x1A8)

    def get_diachicosothongtinkynang(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0xADFE18)

    def get_danhsachidnguoichoixungquanhs(self):
        i = -1
        danhsachidnguoichoixungquanhs = []
        while True:
            i += 1
            diachicosothongtinnhanvatxemxet = self.get_diachicosothongtindoituongx(i)
            if not diachicosothongtinnhanvatxemxet:
                break
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                continue
            idnguoichoi = self.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
            if not idnguoichoi:
                continue
            danhsachidnguoichoixungquanhs.append(idnguoichoi)

        return danhsachidnguoichoixungquanhs

    def get_thoidiemtuthenhanvatdungimgannhat(self):
        return self._thoidiemtuthenhanvatdungimgannhat

    def action_lammoitrangthaimoitruong(self):
        diachicosothongtinnhanvatmuctieuhientai = self.get_diachicosothongtinnhanvatmuctieudangchon()

        if diachicosothongtinnhanvatmuctieuhientai:
            self._thoidiemkhongcomuctieugannhat = time.time()

        if self.get_idtuthenhanvat() != TUTHENHANVAT_DUNGIM:
            self._thoidiemtuthenhanvatdungimgannhat = time.time()

    def get_is_cuasogametontai(self):
        tencuaso = str(win32gui.GetWindowText(self.idcuaso))
        return "(" in tencuaso

    def get_is_cuasogamekichhoat(self):
        return win32gui.GetForegroundWindow() == self.idcuaso

    def get_diachicosothongtinnhanvatdangchichuot(self):
        return read_int(self.tientrinh, self.diachixq + 0x37FA54)

    def get_idnguoichoi(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x24)

    def get_is_dangmatketnoi(self):
        return not self.get_is_nhanvattontai()

    def get_iddoituong(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x20)

    def get_idloaidoituong(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0xF0)

    #Gọi là không tồn tại nó không đúng. Mà là nó ngoài tầm mà nhân vật thấy được nên không có thông tin về nó nữa
    def get_is_nhanvattontai(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return self.get_iddoituong(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) in (LOAIDOITUONG_NHANVAT1, LOAIDOITUONG_NHANVATKHAC1)

    def get_is_vatphamtontai(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return self.get_iddoituong(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) == LOAIDOITUONG_VATPHAMDUOIDAT

    def get_is_nhanvatdachet(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        return read_boolean(self.tientrinh, diachicosothongtinnhanvat + 0x1424)

    def get_tendoituong(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_string(self.tientrinh, diachicosothongtinnhanvat + 0x10AC)

    def get_tennhanvatchichuot(self):
        diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvatdangchichuot()
        if not diachicosothongtinnhanvat:
            return False
        return self.get_tendoituong(diachicosothongtinnhanvat)

    def get_sinhlucconlai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x371754)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x152C)

    def get_sinhluctoida(self):
        x = read_int(self.tientrinh, self.diachixq + 0x371754)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1530)

    def get_noilucconlai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x371754)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1534)

    def get_noiluctoida(self):
        x = read_int(self.tientrinh, self.diachixq + 0x371754)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1538)

    def get_idbandohientai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x371754)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x15F4)

    def get_phantramsinhlucconlai(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1410) * 2

    def get_toadox(self, diachicosothongtinnhanvat = None, is_vitrihientai = False):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        toadox = read_int(self.tientrinh, diachicosothongtinnhanvat)

        if is_vitrihientai:
            return toadox

        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN:
            toadoxsaptoi = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x18)
            deltax = toadoxsaptoi - toadox
            if deltax > 0:
                toadox += deltax / abs(deltax)

        return round(toadox)

    def get_toadoy(self, diachicosothongtinnhanvat = None, is_vitrihientai = False):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        toadoy = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x4)

        if is_vitrihientai:
            return toadoy

        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN:
            toadoysaptoi = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1C)
            deltay = toadoysaptoi - toadoy
            if deltay > 0:
                toadoy += deltay / abs(deltay)

        return round(toadoy)

    def get_toadoxbandochichuot(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x371C80)

    def get_toadoybandochichuot(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x371C84)

    def get_idbandochichuot(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)
        if not x:
            return False

        y = read_int(self.tientrinh, x + 0x11F10)

        if not y:
            return False

        return read_int(self.tientrinh, x + 0x23C + 0x16C * y)

    def get_idmaupk(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0xAED6CC)

    def set_idmaupk(self, idmaupk):
        if self.get_idmaupk() == idmaupk:
            return

        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        write_int(self.tientrinh, x + 0xAED6CC, idmaupk)

    def get_tenbang(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        return read_string(self.tientrinh, diachicosothongtinnhanvat + 0x1136)

    def get_is_cungbang(self, diachicosothongtinnhanvat):
        return False

    def get_idtrangthaichuot(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDA8)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1A4)

    def set_idtrangthaichuot(self, idtrangthaichuot):
        if idtrangthaichuot == self.get_idtrangthaichuot():
            return
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return
        x = read_int(self.tientrinh, x + 0xADFDA8)
        if not x:
            return
        write_int(self.tientrinh, x + 0x1A4, idtrangthaichuot)

    def get_khoangcach(self, diachicosothongtinnhanvat2, diachicosothongtinnhanvat1 = False):
        if not diachicosothongtinnhanvat1:
            diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)
        x2, y2 = self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2)

        return round(math.dist((x1, y1), (x2, y2)), 2)

    def get_khoangcachdiem(self, x2, y2, diachicosothongtinnhanvat1 = False):
        if not diachicosothongtinnhanvat1:
            diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)

        return round(math.dist((x1, y1), (x2, y2)), 2)

    def get_idtuthenhanvat(self, diachicosothongtinnhanvat = None):
        """
            1: đứng yên, 2: di chuyển, 6: tấn công, 11: delay sau tấn công
        """
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1178)

    def set_idtuthenhanvat(self, idtuthenhanvat, diachicosothongtinnhanvat = None):
        """
            1: đứng yên, 2: di chuyển, 6: tấn công, 11: delay sau tấn công
        """
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == idtuthenhanvat:
            return

        write_int(self.tientrinh, diachicosothongtinnhanvat + 0x1178, idtuthenhanvat)

    def get_is_dangdelaysautancong(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x11B8) == 11

    def get_soluonghieuungnhanvat(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        soluonghieuungnhanvat = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x2EE8)

        soluonghieuungnhanvattruocdo = self._soluonghieuungnhanvattruocdo_map.get(diachicosothongtinnhanvat, -1)

        if soluonghieuungnhanvattruocdo > 0 and soluonghieuungnhanvat == 0:
            self._thoidiemsoluonghieuungbangkhonggannhat_map[diachicosothongtinnhanvat] = time.time()

        self._soluonghieuungnhanvattruocdo_map[diachicosothongtinnhanvat] = soluonghieuungnhanvat

        return soluonghieuungnhanvat

    def get_danhsachhieuungnhanvats(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        hieuungs = []

        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
            return hieuungs

        diachicosohieuungnhanvat = diachicosothongtinnhanvat + OFFSET_DIACHICOSOHIEUUNGNHANVAT
        soluonghieuungnhanvat = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
        soluonghieuungdemduoc = 0
        i = -1

        while True:
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
                return hieuungs

            soluonghieuungnhanvatmoinhat = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
            if soluonghieuungnhanvat != soluonghieuungnhanvatmoinhat:
                soluonghieuungnhanvat = soluonghieuungnhanvatmoinhat
                soluonghieuungdemduoc = 0
                i = -1

            i += 1
            if i >= SOLUONGHIEUUNGNHANVATTOIDA:
                return hieuungs

            idvitrihieuungxemxet = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT)
            is_hieuungcoloi = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x4) #1 là có lợi, 0 là có hại
            thoigianhieuluctoida = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x8)

            if idvitrihieuungxemxet < 0:
                continue
            if is_hieuungcoloi < 0:
                continue
            if not idvitrihieuungxemxet and not is_hieuungcoloi and not thoigianhieuluctoida:
                continue

            idhieuungxemxet = read_int(self.tientrinh, self.diachixq + 0x1BF4D0 + idvitrihieuungxemxet * 4)  # Dò bằng cách tắt bật hiệu ứng theo sau nhóm và check xem ai write vào idvitrihieuung ở 0x1638

            hieuungs.append((idhieuungxemxet, is_hieuungcoloi, thoigianhieuluctoida))

            soluonghieuungdemduoc += 1

            if soluonghieuungdemduoc >= soluonghieuungnhanvatmoinhat:
                break

        return hieuungs

    def get_is_cohieuungcoloinhanvat(self, diachicosothongtinnhanvat = None):
        return self.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, ), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvat, is_hieuungcoloi = 1)

    def get_is_cohieuungbatloinhanvat(self, diachicosothongtinnhanvat = None):
        return self.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG, HIEUUNGKYNANG_CHOANG, ), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvat, is_hieuungcoloi = 0)

    def get_is_cohieuungs(self, idhieuungs, macdinh, diachicosothongtinnhanvat = None, is_hieuungcoloi: int = None): #is_loihai: Kiểm tra lợi hại nữa
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
            return macdinh

        diachicosohieuungnhanvat = diachicosothongtinnhanvat + OFFSET_DIACHICOSOHIEUUNGNHANVAT

        soluonghieuungnhanvat = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
        soluonghieuungdemduoc = 0
        i = -1

        if time.time() - self._thoidiemsoluonghieuungbangkhonggannhat_map.get(diachicosothongtinnhanvat, time.time() - 2.) < 1:
            return macdinh

        if soluonghieuungdemduoc >= soluonghieuungnhanvat:
            return False

        while True:
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
                return macdinh

            if time.time() - self._thoidiemsoluonghieuungbangkhonggannhat_map.get(diachicosothongtinnhanvat, time.time() - 2.) < 1:
                return macdinh

            soluonghieuungnhanvatmoinhat = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
            if soluonghieuungnhanvat != soluonghieuungnhanvatmoinhat:
                soluonghieuungnhanvat = soluonghieuungnhanvatmoinhat
                soluonghieuungdemduoc = 0
                i = -1

            if time.time() - self._thoidiemsoluonghieuungbangkhonggannhat_map.get(diachicosothongtinnhanvat, time.time() - 2.) < 1:
                return macdinh

            if soluonghieuungdemduoc >= soluonghieuungnhanvat:
                return False

            i += 1
            if i >= SOLUONGHIEUUNGNHANVATTOIDA:
                return macdinh

            idvitrihieuungxemxet = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT)
            is_hieuungcoloixemxet = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x4) #1 là có lợi, 0 là có hại
            thoigianhieuluctoida = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x8)


            if idvitrihieuungxemxet < 0:
                continue
            if is_hieuungcoloixemxet < 0:
                continue
            if not idvitrihieuungxemxet and not is_hieuungcoloixemxet and not thoigianhieuluctoida:
                continue

            idhieuungxemxet = read_int(self.tientrinh, self.diachixq + 0x1BF4D0 + idvitrihieuungxemxet * 4)  # Dò bằng cách tắt bật hiệu ứng theo sau nhóm và check xem ai write vào idvitrihieuung ở 0x1638

            if idhieuungxemxet in idhieuungs:
                if is_hieuungcoloi is not None:
                    return is_hieuungcoloixemxet == is_hieuungcoloi
                return True

            soluonghieuungdemduoc += 1

        return macdinh

    def get_is_dangtheosaunhom(self):
        return self.get_is_cohieuungs(HIEUUNGKYNANG_THEOSAUNHOM, False)

    def get_diachicosoidthanhviennhom(self):
        #Trong nhóm còn nhìn thấy máu của nhau nữa nhé
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDA4)
        if not x:
            return False
        return x

    def get_toadoxtruongnhom(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return False

        return read_int(self.tientrinh, diachicosothanhviennhom + 0xBD0)

    def get_toadoytruongnhom(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return False

        return read_int(self.tientrinh, diachicosothanhviennhom + 0xC00)

    def get_idnguoichoitruongnhom(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return False
        return read_int(self.tientrinh, diachicosothanhviennhom)

    def get_is_truongnhom(self):
        return self.get_idnguoichoi(self.get_diachicosothongtinnhanvat1()) == self.get_idnguoichoitruongnhom()

    def get_danhsachidnguoichoithanhviennhoms(self):
        idthanhviens = []
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return idthanhviens
        for i in range(SOLUONGTHANHVIENNHOMTOIDA):
            idthanhvien = read_int(self.tientrinh, diachicosothanhviennhom + i * 0x4)
            if idthanhvien:
                idthanhviens.append(idthanhvien)

        return idthanhviens
    def get_is_dangnamtrongnhom(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return False

        idthanhviendautien = read_int(self.tientrinh, diachicosothanhviennhom)

        return idthanhviendautien > 0

    def get_is_tamngungtancong(self):
        return self._is_tamngungtancong

    def set_is_tamngungtancong(self, is_tamngungtancong):
        if self._is_tamngungtancong != is_tamngungtancong:
            self._is_tamngungtancong = is_tamngungtancong

    def get_idloainhanvat(self, diachicosothongtinnhanvat):
        if not diachicosothongtinnhanvat:
            return False
        """
        0:  Quái vật hoặc NPC
        1: Người chơi có thể tấn công
        2: Người chơi không thể tấn công
        """
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x28)

    def get_is_nguoichoi(self, diachicosothongtinnhanvat):
        return self.get_idloainhanvat(diachicosothongtinnhanvat) in (LOAIMUCTIEU_NGUOICHOIKHACNHOM, LOAIMUCTIEU_NGUOICHOICUNGNHOM)

    def get_is_npc(self, diachicosothongtinnhanvat):
        phantramsinhlucconlai = self.get_phantramsinhlucconlai(diachicosothongtinnhanvat)
        if phantramsinhlucconlai > 100:
            return True

        # return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1414) in (1, 7, 12) and not phantramsinhlucconlai #1 hình như là nguyên liệu, 7 nó là con thỏ của PYK, 60 là mấy con thú cưng
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x155C) in (25, 40) #25 có vẻ như là ở xa tít chưa thấy gì hay còn gọi là Chưa xác định, còn 40 là thấy rồi

    def get_idkynang(self, idvitriX, idvitriY):
        """
        :param idvitriX: Số thứ tự cuốn sách bắt đầu từ 0
        :param idvitriY: Số thứ tự kỹ năng ở trong cuốn sách ấy bắt đầu từ 0
        """
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang:
            return False

        idvitrikynang = 14 * idvitriY + idvitriX #Vì mỗi cuốn nó chỉ có tối đa 12 kỹ năng cho nên nó nhích lên 14 để không bao giờ trùng nhau

        return read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830)

    def get_tenkynang(self, idvitriX, idvitriY):
        """
        :param idvitriX: Số thứ tự cuốn sách bắt đầu từ 0
        :param idvitriY: Số thứ tự kỹ năng ở trong cuốn sách ấy bắt đầu từ 0
        """
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang:
            return False

        idvitrikynang = 14 * idvitriY + idvitriX #Vì mỗi cuốn nó chỉ có tối đa 12 kỹ năng cho nên nó nhích lên 14 để không bao giờ trùng nhau

        return read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830)

    def get_is_kynangsansang(self, idvitriX, idvitriY):
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang:
            return False
        idvitrikynang = 14 * idvitriY + idvitriX #Vì mỗi cuốn nó chỉ có tối đa 12 kỹ năng cho nên nó nhích lên 14 để không bao giờ trùng nhau

        idkynang = read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830)
        is_dahockynang = True
        thoigiangiancach = read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6A4C) == 0

        return idkynang and is_dahockynang and thoigiangiancach and self._thoidiemsudungkynangvitrigannhat_map.get((idvitriX, idvitriY), time.time() - 2) > 1.0

    def get_is_cothetancong(self, diachicosothongtinnhanvat):
        if not diachicosothongtinnhanvat:
            return False

        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
            return False

        if self.get_is_nhanvatdachet(diachicosothongtinnhanvat):
            return False

        idloainhanvat = self.get_idloainhanvat(diachicosothongtinnhanvat)

        if idloainhanvat == LOAIMUCTIEU_NGUOICHOICUNGNHOM:
            return False

        if self.get_is_npc(diachicosothongtinnhanvat):
            return False

        idmaupk = self.get_idmaupk()

        if idmaupk == MAUPK_HOABINH:
            if idloainhanvat in (LOAIMUCTIEU_NGUOICHOIKHACNHOM, LOAIMUCTIEU_NGUOICHOICUNGNHOM):
                return False
        elif idmaupk == MAUPK_NHOM:
            if idloainhanvat == LOAIMUCTIEU_NGUOICHOICUNGNHOM:
                return False
        elif idmaupk == MAUPK_BANG:
            if idloainhanvat == LOAIMUCTIEU_NGUOICHOIKHACNHOM and self.get_is_cungbang(diachicosothongtinnhanvat):
                return False
        elif idmaupk == MAUPK_TUDO:
            if idloainhanvat == LOAIMUCTIEU_NGUOICHOIKHACNHOM and self.get_is_cungbang(diachicosothongtinnhanvat):
                return False

        return True

    def get_is_batalt(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA28)
        if not x:
            return False
        return read_boolean(self.tientrinh, x)

    def set_is_batalt(self, is_batalt):
        if self.get_is_batalt() == is_batalt:
            return

        x = read_int(self.tientrinh, self.diachixq + 0x37FA28)
        if not x:
            return

        write_boolean(self.tientrinh, x, is_batalt)

    def get_is_bathanhtrang(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFE0C)

        if not x:
            return False

        return read_boolean(self.tientrinh, x + 0x34)


    def get_is_dangbatenter(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFD60)
        if not x:
            return False
        return read_boolean(self.tientrinh, x + 0x8140)

    def get_thoidiemkhongcomuctieugannhat(self):
        return self._thoidiemkhongcomuctieugannhat

    def get_iddoituongmuctieudangchon(self):
        diachicosothongtinnhanvatmuctieudangchon = self.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachicosothongtinnhanvatmuctieudangchon:
            return False

        return self.get_iddoituong(diachicosothongtinnhanvatmuctieudangchon)

    def get_is_dangclickchuottrai(self):
        return read_boolean(self.tientrinh, self.diachixq + 0x37FA6D)

    def get_diachicosothongtinnhanvatmuctieudangchon(self):
        return self._diachicosothongtinnhanvatmuctieudangchon

    def set_diachicosothongtinnhanvatmuctieudangchon(self, diachicosothongtinnhanvat):
        if self.get_diachicosothongtinnhanvatmuctieudangchon() == diachicosothongtinnhanvat:
            return

        # print("set_diachicosothongtinnhanvatmuctieudangchon: ", hex(diachicosothongtinnhanvat), self.get_tendoituong(self._diachicosothongtinnhanvatmuctieudangchon) if self._diachicosothongtinnhanvatmuctieudangchon and not diachicosothongtinnhanvat else "")

        self._diachicosothongtinnhanvatmuctieudangchon = diachicosothongtinnhanvat

        if diachicosothongtinnhanvat:
            iddoituong = self.get_iddoituong(diachicosothongtinnhanvat)
            if iddoituong > 0:
                write_int(self.tientrinh, self.diachixq + 0x1BC3E0, diachicosothongtinnhanvat)
                write_int(self.tientrinh, self.diachixq + 0x37173C, iddoituong)
                write_int(self.tientrinh, self.diachixq + 0x1BC440, diachicosothongtinnhanvat)
                write_int(self.tientrinh, self.diachixq + 0x1BC444, iddoituong)

    def action_vohieuhoatuthedelaysautancong(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x1AF43, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x1AF43, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

    def action_tatvohieuhoatuthedelaysautancong(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x1AF43, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x1AF43, bytes.fromhex("C7 86 B8 11 00 00 0B 00 00 00"), 10)

    def action_vohieuhoathietlapmuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0xA1E30, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA1E30, bytes.fromhex("90 90 90 90 90"), 5)

        if read_bytes(self.tientrinh, self.diachixq + 0xA1E38, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA1E38, bytes.fromhex("90 90 90 90 90 90"), 6)

        if read_bytes(self.tientrinh, self.diachixq + 0xA1E3E, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA1E3E, bytes.fromhex("90 90 90 90 90"), 5)

        if read_bytes(self.tientrinh, self.diachixq + 0xA1E46, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA1E46, bytes.fromhex("90 90 90 90 90 90"), 6)

    def action_tatvohieuhoathietlapmuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0xA1E30, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA1E30, bytes.fromhex("A3 40 C4 5B 00"), 5)

        if read_bytes(self.tientrinh, self.diachixq + 0xA1E38, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA1E38, bytes.fromhex("89 0D 44 C4 5B 00"), 6)

        if read_bytes(self.tientrinh, self.diachixq + 0xA1E3E, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA1E3E, bytes.fromhex("A3 E0 C3 5B 00"), 5)

        if read_bytes(self.tientrinh, self.diachixq + 0xA1E46, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA1E46, bytes.fromhex("89 15 3C 17 77 00"), 6)


    def action_vohieuhoaxoamuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x951A5, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x951A5, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)
        if read_bytes(self.tientrinh, self.diachixq + 0x9519B, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x9519B, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

        if read_bytes(self.tientrinh, self.diachixq + 0x497DF, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x497DF, bytes.fromhex("90 90 90 90 90 90"), 6)
        if read_bytes(self.tientrinh, self.diachixq + 0x497E5, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x497E5, bytes.fromhex("90 90 90 90 90 90"), 6)

    def action_tatvohieuhoaxoamuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x951A5, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x951A5, bytes.fromhex("C7 05"), 2)
            write_int(self.tientrinh, self.diachixq + 0x951A5 + 2, self.diachixq + 0x1BC3E0)
            write_int(self.tientrinh, self.diachixq + 0x951A5 + 6, 0)
        if read_bytes(self.tientrinh, self.diachixq + 0x9519B, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x9519B, bytes.fromhex("C7 05"), 2)
            write_int(self.tientrinh, self.diachixq + 0x9519B + 2, self.diachixq + 0x37173C)
            write_int(self.tientrinh, self.diachixq + 0x9519B + 6, 0)

        if read_bytes(self.tientrinh, self.diachixq + 0x497DF, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x497DF, bytes.fromhex("89 35"), 2)
            write_int(self.tientrinh, self.diachixq + 0x497DF + 2, self.diachixq + 0x1BC440)
        if read_bytes(self.tientrinh, self.diachixq + 0x497E5, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x497E5, bytes.fromhex("89 35"), 2)
            write_int(self.tientrinh, self.diachixq + 0x497E5 + 2, self.diachixq + 0x1BC444)

    def action_vohieuhoalongclick(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x4984C, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x4984C, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

    def action_tatvohieuhoalongclick(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x4984C, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x4984C, bytes.fromhex("C7 82 10 16 00 00 01 00 00 00"), 10)

    def action_vohieuhoalongclick2(self):
        #Dưới đây là long click thực hiện được khi vừa dí chuột vừa đưa chuột ra khỏi màn hình cần disable nó thì hàm di chuyển mới dùng được, nếu không mỗi lần gọi nó đều bị dính long click này
        # if read_bytes(self.tientrinh, self.diachixq + 0x41721, 1) != bytes.fromhex("90"):
        #     write_bytes(self.tientrinh, self.diachixq + 0x41721, bytes.fromhex("90 90 90 90 90 90 90"), 7)
        if read_bytes(self.tientrinh, self.diachixq + 0x41721 + 6, 1) != bytes.fromhex("00"):
            write_bytes(self.tientrinh, self.diachixq + 0x41721 + 6, bytes.fromhex("00"), 1)
    def action_tatvohieuhoalongclick2(self):
        #Dưới đây là long click thực hiện được khi vừa dí chuột vừa đưa chuột ra khỏi màn hình cần disable nó thì hàm di chuyển mới dùng được, nếu không mỗi lần gọi nó đều bị dính long click này
        # if read_bytes(self.tientrinh, self.diachixq + 0x41721, 1) == bytes.fromhex("90"):
        #     write_bytes(self.tientrinh, self.diachixq + 0x41721, bytes.fromhex("C6 05 01"), 2)
        #     write_int(self.tientrinh, self.diachixq + 0x41721 + 2, self.diachixq + 0x37FA6D)
        #     write_bytes(self.tientrinh, self.diachixq + 0x41721 + 6, bytes.fromhex("01"), 1)
        if read_bytes(self.tientrinh, self.diachixq + 0x41721 + 6, 1) == bytes.fromhex("00"):
            write_bytes(self.tientrinh, self.diachixq + 0x41721 + 6, bytes.fromhex("01"), 1)

    def action_vohieuhoatrangthaichuotchonmuctieukynang(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x5405C, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x5405C, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

    def action_tatvohieuhoatrangthaichuotchonmuctieukynang(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x5405C, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x5405C, bytes.fromhex("C7 86 A4 01 00 00 02 00 00 00"), 10)

    def action_vohieuhoakhoanhvungkynang(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x76148, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x76148, bytes.fromhex("90 90"), 2)

    def action_tatvohieuhoakhoanhvungkynang(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x76148, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x76148, bytes.fromhex("88 01"), 2)

    def action_vohieuhoaphimspace(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x3D8CB, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x3D8CB, bytes.fromhex("90 90 90 90 90 90 90"), 7)

    def action_tatvohieuhoaphimspace(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x3D8CB, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x3D8CB, bytes.fromhex("C6 80 40 81 00 00 01"), 7)

    def get_is_danghiencuasoyesno(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFE10)
        if not x:
            return False

        return read_boolean(self.tientrinh, x + 0x34)

    def set_is_danghiencuasoyesno(self, is_danghiencuasoyesno):
        if self.get_is_danghiencuasoyesno() == is_danghiencuasoyesno:
            return

        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return

        x = read_int(self.tientrinh, x + 0xADFE10)
        if not x:
            return

        return write_boolean(self.tientrinh, x + 0x34, is_danghiencuasoyesno)

    def get_is_danghiencuasotuychon(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFD74)
        if not x:
            return False

        return read_boolean(self.tientrinh, x + 0x1E38)

    def set_is_danghiencuasotuychon(self, is_danghiencuasotuychon):
        if self.get_is_danghiencuasotuychon() == is_danghiencuasotuychon:
            return

        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return

        x = read_int(self.tientrinh, x + 0xADFD74)
        if not x:
            return

        return write_boolean(self.tientrinh, x + 0x1E38, is_danghiencuasotuychon)

    def get_caulenhthucthihientai(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFE10)
        if not x:
            return False

        return read_string(self.tientrinh, x + 0x7C).strip()

    def set_caulenhthucthihientai(self, caulenh):
        if self.get_caulenhthucthihientai() == caulenh:
            return
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return

        x = read_int(self.tientrinh, x + 0xADFE10)
        if not x:
            return

        return write_string(self.tientrinh, x + 0x7C, caulenh)

    def action_thucthicaulenhhientai(self, delay = 1.):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return

        self._thoidiemthucthicaulenhgannhat = time.time()

        if not self.get_caulenhthucthihientai():
            return

        self.tientrinh.start_thread(self.diachixq + 0x131560)

    def action_thucthicaulenh(self, caulenh, delay = 0.05):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_thucthicaulenh(caulenh)

    def action_moihoacxinvaonhom(self, idnguoichoi, delay = 1.):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return
        if not idnguoichoi:
            return

        self._thoidiemthaotacnhomgannhat = time.time()

        self.action_thucthicaulenh("team + {}".format(idnguoichoi))

    def action_thoatkhoinhom(self, idnguoichoitruongnhom, delay = 1.):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return
        if not idnguoichoitruongnhom:
            return

        self._thoidiemthaotacnhomgannhat = time.time()

        self.action_thucthicaulenh("team x {}".format(idnguoichoitruongnhom))

    def action_kiemtravadongyloimoinhom(self, idnguoichoitruongnhom, delay = 1.):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return
        if not idnguoichoitruongnhom:
            return

        if "team + {}".format(idnguoichoitruongnhom) == self.get_caulenhthucthihientai():
            self._thoidiemthaotacnhomgannhat = time.time()

            if self.get_is_danghiencuasoyesno():
                self.set_is_danghiencuasoyesno(False)

            self.action_thucthicaulenhhientai()

    def auto_assemble_thucthicaulenh(self, caulenh):
        if not self._is_dasetupautoassemblethucthicaulenh:
            self._diachiautoassemblethucthicaulenh = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh, bytes.fromhex("B9"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 5, bytes.fromhex("BA"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 6, self._diachiautoassemblethucthicaulenh + 21)

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 10, bytes.fromhex("51"), 1)
            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 11, bytes.fromhex("52"), 1)

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 12, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 13, self.diachixq + 0x951C0 - (self._diachiautoassemblethucthicaulenh + 12) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 17, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 20, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblethucthicaulenh + 21, caulenh)

            self._is_dasetupautoassemblethucthicaulenh = True
        else:
            write_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 1, len(caulenh))
            write_string(self.tientrinh, self._diachiautoassemblethucthicaulenh + 21, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblethucthicaulenh)

    def auto_assemble_mocuasotuychonnhanvatchinh(self):
        if not self._is_dasetupautoassemblemocuasotuychonnhanvatchinh:
            self._diachiautoassemblemocuasotuychonnhanvatchinh = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh, bytes.fromhex("BA 3F000000"), 5)

            write_bytes(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh + 5, bytes.fromhex("8B 3D"), 2)
            write_int(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh + 7, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh + 11, bytes.fromhex("8D 77 14"), 3)

            write_bytes(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh + 14, bytes.fromhex("8B CF"), 2)

            write_bytes(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh + 16, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh + 17, self.diachixq + 0x70B20 - (self._diachiautoassemblemocuasotuychonnhanvatchinh + 16) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh + 21, bytes.fromhex("C3"), 1)

            self._is_dasetupautoassemblemocuasotuychonnhanvatchinh = True

        self.tientrinh.start_thread(self._diachiautoassemblemocuasotuychonnhanvatchinh)

    def auto_assemble_sudungkynangphimtat(self, idvitriphimtat):
        if not self._is_dasetupautoassemblesudungkynangphimtat:
            self._diachiautoassemblesudungkynangphimtat = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangphimtat, bytes.fromhex("B8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 1, idvitriphimtat)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 5, bytes.fromhex("8B 15"), 2)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 7, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 11, bytes.fromhex("50"), 1)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 12, bytes.fromhex("8D 8A"), 2)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 14, 0xADFEA0)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 18, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 19, self.diachixq + 0x72E70 - (self._diachiautoassemblesudungkynangphimtat + 18) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 23, bytes.fromhex("C3"), 1)

            self._is_dasetupautoassemblesudungkynangphimtat = True
        else:
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 1, idvitriphimtat)

        self.tientrinh.start_thread(self._diachiautoassemblesudungkynangphimtat)


    def auto_assemble_sudungkynangvitri(self, idvitriX, idvitriY, hinhthucsudungkynang = HINHTHUCSUDUNGKYNANG_CANMUCTIEU):
        idkynang = self.get_idkynang(idvitriX, idvitriY)
        if not idkynang:
            return

        if not self._is_dasetupautoassemblesudungkynangvitri:
            self._diachiautoassemblesudungkynangvitri = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangvitri, bytes.fromhex("B8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 1, idkynang)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 5, bytes.fromhex("8B 0D"), 2)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 7, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 11, bytes.fromhex("BA"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 12, hinhthucsudungkynang)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 16, bytes.fromhex("52"), 1)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 17, bytes.fromhex("50"), 1)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 18, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 19, self.diachixq + 0x53D60 - (self._diachiautoassemblesudungkynangvitri + 18) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 23, bytes.fromhex("C3"), 1)

            self._is_dasetupautoassemblesudungkynangvitri = True
        else:
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 12, hinhthucsudungkynang)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 1, idkynang)

        self.tientrinh.start_thread(self._diachiautoassemblesudungkynangvitri)

    def auto_assemble_dichuyen(self, x, y):
        if not self._is_dasetupautoassembledichuyen:
            self._diachiautoassembledichuyen = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen, bytes.fromhex("8B 35"), 2)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 2, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 6, bytes.fromhex("BB"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 7, x)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 11, bytes.fromhex("BF"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 12, y)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 16, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 17, 0)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 21, bytes.fromhex("57"), 1)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 22, bytes.fromhex("53"), 1)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 23, bytes.fromhex("8B CE"), 2)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 25, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 26, self.diachixq + 0x476A0 - (self._diachiautoassembledichuyen + 25) - 5)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 30, bytes.fromhex("C3"), 1)
            self._is_dasetupautoassembledichuyen = True
        else:
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 7, x)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 12, y)

        self.tientrinh.start_thread(self._diachiautoassembledichuyen)

    def auto_assemble_nhatdo(self):
        if not self._is_dasetupautoassemblenhatdo:
            self._diachiautoassemblenhatdo = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatdo, bytes.fromhex("8B 0D"), 2)
            write_int(self.tientrinh, self._diachiautoassemblenhatdo + 2, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatdo + 6, bytes.fromhex("8D 59 14"), 3)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatdo + 9, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatdo + 10, self.diachixq + 0xB3F0 - (self._diachiautoassemblenhatdo + 9) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatdo + 14, bytes.fromhex("C3"), 1)
            self._is_dasetupautoassemblenhatdo = True

        self.tientrinh.start_thread(self._diachiautoassemblenhatdo)

    def auto_assemble_khoitaothongtinbando(self):
        if not self._is_dasetupautoassemblekhoitaothongtinbando:
            self._diachiautoassemblekhoitaothongtinbando = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando, bytes.fromhex("8B 0D"), 2)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 2, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 6, bytes.fromhex("BF"), 1)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 7, 100)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 11, bytes.fromhex("BE 01002020"), 5)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 16, bytes.fromhex("56"), 1)
            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 17, bytes.fromhex("57"), 1)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 18, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 19, self.diachixq + 0x3C020 - (self._diachiautoassemblekhoitaothongtinbando + 18) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 23, bytes.fromhex("8B 35"), 2)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 25, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 29, bytes.fromhex("8B B6"), 2)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 31, 0xADFDEC)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 35, bytes.fromhex("B0 00 88 06"), 4)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 39, bytes.fromhex("C3"), 1)
            self._is_dasetupautoassemblekhoitaothongtinbando = True

        self.tientrinh.start_thread(self._diachiautoassemblekhoitaothongtinbando)

    def auto_assemble_tudongtimduong(self, x, y, idbando):
        if not self._is_dasetupautoassembletudongtimduong:
            self._diachiautoassembletudongtimduong = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong, bytes.fromhex("8B 35"), 2)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 2, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 6, bytes.fromhex("8B B6"), 2)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 8, 0xADFDEC)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 12, bytes.fromhex("B9"), 1)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 13, y)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 17, bytes.fromhex("BA"), 1)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 18, x)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 22, bytes.fromhex("B8"), 1)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 23, idbando)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 27, bytes.fromhex("51"), 1)
            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 28, bytes.fromhex("52"), 1)
            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 29, bytes.fromhex("50"), 1)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 30, bytes.fromhex("8B CE"), 2)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 32, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 33, self.diachixq + 0xD6120 - (self._diachiautoassembletudongtimduong + 32) - 5)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 37, bytes.fromhex("C3"), 1)

            self._is_dasetupautoassembletudongtimduong = True
        else:
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 13, y)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 18, x)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 23, idbando)

        self.tientrinh.start_thread(self._diachiautoassembletudongtimduong)

    def action_nhatdo(self, diachicosothongtinvatpham, delay = 0.05):
        if time.time() - self._thoidiemnhatdogannhat < delay:
            return

        if time.time() - self._thoidiemnhatdogannhat_map.get(diachicosothongtinvatpham, time.time() - 2.) < 1.:
            return

        x = self.get_toadox(diachicosothongtinvatpham, is_vitrihientai = True)
        y = self.get_toadoy(diachicosothongtinvatpham, is_vitrihientai = True)

        if not x and not y:
            return

        self._thoidiemnhatdogannhat = time.time()
        self._thoidiemnhatdogannhat_map[diachicosothongtinvatpham] = time.time()

        self.action_thucthicaulenh("get {} {}".format(x, y), delay = 0)

    def action_battheosaunhom(self, delay = 2.):
        if time.time() - self._thoidiembattattheosaunhomgannhat < delay:
            return

        idnguoichoitruongnhom = self.get_idnguoichoitruongnhom()
        if not idnguoichoitruongnhom:
            return

        self._thoidiembattattheosaunhomgannhat = time.time()

        self.action_thucthicaulenh("team follow {}".format(idnguoichoitruongnhom))
    
    def action_sudungkynangphimtat(self, idvitriphimtat, delay = 0.5):
        if idvitriphimtat in self._thoidiemsudungkynangphimtatgannhat_map and time.time() - self._thoidiemsudungkynangphimtatgannhat_map[idvitriphimtat] < delay:
            return

        self._thoidiemsudungkynangphimtatgannhat_map[idvitriphimtat] = time.time()
        self.auto_assemble_sudungkynangphimtat(idvitriphimtat)

    def get_thoidiemsudungkynangvitrigannhat(self, idvitriX, idvitriY, macdinh = None):
        return self._thoidiemsudungkynangvitrigannhat_map.get((idvitriX, idvitriY), macdinh)

    def action_sudungkynangvitri(self, idvitriX, idvitriY, hinhthucsudungkynang = HINHTHUCSUDUNGKYNANG_CANMUCTIEU, delay = 0.25):
        idvitri = (idvitriX, idvitriY)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        self.auto_assemble_sudungkynangvitri(idvitriX, idvitriY, hinhthucsudungkynang)

    def action_sudungkynangvitrimuctieukhongtrihoan(self, idvitriX, idvitriY, delay = 0.25):
        idvitri = (idvitriX, idvitriY)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        idkynang = self.get_idkynang(idvitriX, idvitriY)
        if not idkynang:
            return

        diachicosomuctieudangchon = self.get_diachicosothongtinnhanvatmuctieudangchon()

        if not diachicosomuctieudangchon or not self.get_is_cothetancong(diachicosomuctieudangchon):
            return

        if self.get_is_nguoichoi(diachicosomuctieudangchon):
            idnguoichoi = self.get_idnguoichoi(diachicosomuctieudangchon)
            caulenh = "pf {} {}".format(idkynang, idnguoichoi)
        else:
            iddoituong = self.get_iddoituongmuctieudangchon()
            if not iddoituong:
                return
            caulenh = "pf {} {}#".format(idkynang, hex(iddoituong)).replace("0x", "")

        self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        self.action_thucthicaulenh(caulenh, delay = 0)

    def action_sudungkynangvitrikhongtrihoan(self, idvitriX, idvitriY, delay = 0.25):
        idvitri = (idvitriX, idvitriY)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        idkynang = self.get_idkynang(idvitriX, idvitriY)
        if not idkynang:
            return

        caulenh = "pf {}".format(idkynang)

        self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        self.action_thucthicaulenh(caulenh, delay = 0)

    def action_sudungkynangvitrilenbanthan(self, idvitriX, idvitriY, delay = 0.25):
        idvitri = (idvitriX, idvitriY)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        idkynang = self.get_idkynang(idvitriX, idvitriY)
        if not idkynang:
            return

        self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()

        self.action_thucthicaulenh("pf {} {}".format(idkynang, self.get_idnguoichoi()), delay = 0)

    def action_dichuyen(self, x, y, delay = 0.25):
        if self._is_vohieuhoadichuyen:
            return

        if time.time() - self._thoidiemdichuyengannhat < delay:
            return

        self._thoidiemdichuyengannhat = time.time()

        self.auto_assemble_dichuyen(x, y)

    def action_dichuyengiukhoangcachtoithieu(self, diachicosothongtinnhanvat2, khoangcachtoithieu, khoangcachdichuyentoida = 0, delay = 0.25):
        if not diachicosothongtinnhanvat2:
            return

        if not self.get_iddoituong(diachicosothongtinnhanvat2):
            return

        return self.action_dichuyengiukhoangcachtoithieudiem(self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2), khoangcachtoithieu = khoangcachtoithieu, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyengiukhoangcachtoida(self, diachicosothongtinnhanvat2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.25):
        if not diachicosothongtinnhanvat2:
            return

        if not self.get_iddoituong(diachicosothongtinnhanvat2):
            return

        return self.action_dichuyengiukhoangcachtoidadiem(self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2), khoangcachtoida = khoangcachtoida, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyenngaunhien(self, delay = 0.25):
        deltax = random.randint(-1, 1)
        deltay = random.randint(-1, 1)

        xmax = self._kichthuoccuasogame[0]
        ymax = self._kichthuoccuasogame[1]

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = int(self._centerx + deltax * toadomoidonvikhoangcachx)
        yclick = int(self._centery + deltay * toadomoidonvikhoangcachy)

        self.action_dichuyen(xclick, yclick, delay = delay)

    def action_dichuyenphudau(self, diachicosothongtinnhanvat2, khoangcachphudau = 1, delay = 0.25):
        if not diachicosothongtinnhanvat2:
            return
        if not self.get_iddoituong(diachicosothongtinnhanvat2):
            return

        diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x2, y2 = self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2)
        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)

        deltax = x2 - x1
        deltay = y1 - y2

        khoangcach = round(math.dist((x1, y1), (x2, y2)), 2)

        khoangcachdichuyen = khoangcach + khoangcachphudau

        if not khoangcachdichuyen:
            return

        if khoangcach > 0.:
            deltax = round(khoangcachdichuyen * deltax / khoangcach, 2)
            deltay = round(khoangcachdichuyen * deltay / khoangcach, 2)
        else:
            deltax = khoangcachdichuyen
            deltay = khoangcachdichuyen

        if not deltax and not deltay:
            return

        xmax = self._kichthuoccuasogame[0]
        ymax = self._kichthuoccuasogame[1]

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = round(self._centerx + deltax * toadomoidonvikhoangcachx)
        yclick = round(self._centery + deltay * toadomoidonvikhoangcachy)

        self.action_dichuyen(xclick, yclick, delay = delay)

    def action_dichuyengiukhoangcachtoidadiem(self, x2, y2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.25):
        diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)

        khoangcach = round(math.dist((x1, y1), (x2, y2)), 2)

        if khoangcach <= khoangcachtoida:
            return

        khoangcachtoida = max(0., khoangcachtoida - 1.) #Đi gần vào hơn khoảng cách tối đa 1 chút

        deltax = x2 - x1
        deltay = y1 - y2

        khoangcachdichuyen = khoangcach - khoangcachtoida

        if not round(khoangcachdichuyen):
            return

        if khoangcachdichuyentoida:
            khoangcachdichuyen = min(khoangcachdichuyentoida * 1., khoangcachdichuyen)

        if khoangcach > 0.:
            deltax = int(khoangcachdichuyen * deltax / khoangcach)
            deltay = int(khoangcachdichuyen * deltay / khoangcach)

        if not deltax and not deltay:
            return

        xmax = self._kichthuoccuasogame[0]
        ymax = self._kichthuoccuasogame[1]

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = int(self._centerx + deltax * toadomoidonvikhoangcachx)
        yclick = int(self._centery + deltay * toadomoidonvikhoangcachy)

        self.action_dichuyen(xclick, yclick, delay = delay)

    def action_dichuyengiukhoangcachtoithieudiem(self, x2, y2, khoangcachtoithieu, khoangcachdichuyentoida = 0, delay = 0.25):
        diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)

        khoangcach = round(math.dist((x1, y1), (x2, y2)), 2)

        if khoangcach >= khoangcachtoithieu:
            return

        deltax = x2 - x1
        deltay = y1 - y2

        khoangcachdichuyen = khoangcachtoithieu

        if not round(khoangcachdichuyen):
            return

        if khoangcachdichuyentoida:
            khoangcachdichuyen = min(khoangcachdichuyentoida * 1., khoangcachdichuyen)

        if khoangcach > 0.:
            deltax = int(-1 * khoangcachdichuyen * deltax / khoangcach)
            deltay = int(-1 * khoangcachdichuyen * deltay / khoangcach)

        if not deltax and not deltay:
            deltax = random.randint(-1, 1) * khoangcachdichuyentoida
            deltay = random.randint(-1, 1) * khoangcachdichuyentoida

        xmax = self._kichthuoccuasogame[0]
        ymax = self._kichthuoccuasogame[1]

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = int(self._centerx + deltax * toadomoidonvikhoangcachx)
        yclick = int(self._centery + deltay * toadomoidonvikhoangcachy)

        self.action_dichuyen(xclick, yclick, delay = delay)

    def action_dichuyentiepcan(self, diachicosothongtinnhanvat2, khoangcachdichuyentoida = 0):
        self.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvat2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida)

    def action_dichuyen1buoc(self, diachicosothongtinnhanvat2, delay = 0.25):
        if time.time() - self.thoidiemdichuyen1buocgannhat < delay:
            return

        if not diachicosothongtinnhanvat2:
            return
        if not self.get_iddoituong(diachicosothongtinnhanvat2):
            return

        x1, y1 = self.get_toadox(is_vitrihientai = True), self.get_toadoy(is_vitrihientai = True)
        x2, y2 = self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2)

        deltax = x2 - x1
        deltay = y1 - y2

        deltax = int(deltax / abs(deltax or 1))
        deltay = int(deltay / abs(deltay or 1))

        go = GOs.get((deltax, deltay), False)
        if not go:
            return

        self.thoidiemdichuyen1buocgannhat = time.time()

        self.action_thucthicaulenh("go {},{} {} {}".format(x1, y1, go, int(time.time())), delay = 0)

        self.set_idtuthenhanvat(TUTHENHANVAT_DICHUYEN)

    def action_ngungdichuyen(self, delay = 0.25):
        if time.time() - self._thoidiemngungdichuyengannhat < delay:
            return

        x1, y1 = self.get_toadox(), self.get_toadoy()

        self._thoidiemngungdichuyengannhat = time.time()

        self.action_thucthicaulenh("go {},{} 0 {}".format(x1, y1, int(time.time())), delay = 0)

    def action_dichuyentiepcandiem(self, x2, y2, khoangcachdichuyentoida = 0):
        self.action_dichuyengiukhoangcachtoidadiem(x2, y2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida)

    def action_sudungkynangvitriphudau(self, idvitriX, idvitriY, diachicosothongtinnhanvat2, khoangcachphudau, delay = 0.25):
        if not diachicosothongtinnhanvat2:
            return
        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat2):
            return
        return self.action_sudungkynangvitriphudaudiem(idvitriX, idvitriY, self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2), khoangcachphudau = khoangcachphudau, delay = delay)

    def action_sudungkynangvitriphudaudiem(self, idvitriX, idvitriY, x2, y2, khoangcachphudau, delay = 0.25):
        idvitri = (idvitriX, idvitriY)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        idkynang = self.get_idkynang(idvitriX, idvitriY)
        if not idkynang:
            return

        self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()

        diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)

        deltax = x2 - x1
        deltay = y2 - y1

        khoangcach = round(math.sqrt(deltax ** 2 + deltay ** 2), 2)

        if khoangcach:
            deltax = deltax * khoangcachphudau / khoangcach
            deltay = deltay * khoangcachphudau / khoangcach
        else:
            deltax = khoangcachphudau
            deltay = khoangcachphudau

        targetx = round(x1 + deltax)
        targety = round(y1 + deltay)

        self.action_thucthicaulenh("pf {} {},{}".format(idkynang, targetx, targety), delay = 0)

    def get_is_damocuasotuychonnhanvatchinhlandau(self):
        x = read_int(self.tientrinh, self.diachixq + 0x3A531C)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0x2C)
        if x <= 10:
            return False

        return True

    def get_is_thietlapkynangphimtat(self, idvitriphimtat):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        x = read_short_int(self.tientrinh, x + 0xADFEA6 + idvitriphimtat)

        return x in (LOAIDOITUONGPHIMTAT_KYNANG, LOAIDOITUONGPHIMTAT_VATPHAM)

    def get_is_dangvankhi(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFDE8)

        if not x:
            return False

        return read_int(self.tientrinh, x + 0xD8) == TRANGTHAIVANKHI_DANGVANKHI

    def get_is_dakhoitaothongtinbando(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)

        return x > 0

    def action_khoitaothongtinbando(self, delay = 0.5):
        if time.time() - self._thoidiemkhoitaothongtinbandogannhat < delay:
            return

        if self.get_is_dakhoitaothongtinbando():
            return

        self._thoidiemkhoitaothongtinbandogannhat = time.time()

        self.auto_assemble_khoitaothongtinbando()

    def action_tudongtimduong(self, x, y, idbando, delay = 1.):
        if time.time() - self._thoidiemtudongtimduonggannhat < delay:
            return

        if not self.get_is_dakhoitaothongtinbando():
            self.action_khoitaothongtinbando()
            return

        self._thoidiemtudongtimduonggannhat = time.time()
        self.auto_assemble_tudongtimduong(x, y, idbando)

    def action_phucsinh(self, delay = 1.):
        if time.time() - self._thoidiemphucsinhgannhat < delay:
            return

        if not self.get_is_nhanvatdachet():
            return

        self._thoidiemphucsinhgannhat = time.time()

        if self.get_is_danghiencuasotuychon():
            self.set_is_danghiencuasotuychon(False)

        self.action_thucthicaulenh("desc revive")

    def action_doimaupk(self, idmaupk, delay = 1.):
        if time.time() - self._thoidiemmaupkgannhat < delay:
            return

        self._thoidiemmaupkgannhat = time.time()

        self.set_idmaupk(idmaupk)
        self.action_thucthicaulenh("set !attack {}".format(idmaupk))

    def action_suado(self, diachicosonhanvatthosuado, delay = 1.):
        if time.time() - self._thoidiemsuadogannhat < delay:
            return

        idthosuado = self.get_iddoituong(diachicosonhanvatthosuado)
        if not idthosuado:
            return
        
        self._thoidiemsuadogannhat = time.time()

        self.action_thucthicaulenh("repair ! {}# all".format(hex(idthosuado).replace("0x", "")))

    def get_diempk(self):
        x = read_int(self.tientrinh, self.diachixq + 0x371754)
        if not x:
            return False
        x = read_string(self.tientrinh, x + 0xC0)
        if not x:
            return False
        if not x.isnumeric():
            return False
        return int(x)

    def action_sudungchucnangmorong5(self, delay = 2.5):
        if time.time() - self._thoidiemsudungchucnangmorong5 < delay:
            return

        self._thoidiemsudungchucnangmorong5 = time.time()
        caulenh = "auto 5 1"

        self.action_thucthicaulenh(caulenh, delay = 0)

    def get_idmonphai(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1184)

    def get_is_vohieuhoadichuyen(self):
        return self._is_vohieuhoadichuyen
    def set_is_vohieuhoadichuyen(self, is_vohieuhoadichuyen):
        if self._is_vohieuhoadichuyen == is_vohieuhoadichuyen:
            return
        self._is_vohieuhoadichuyen = is_vohieuhoadichuyen
