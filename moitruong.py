import ctypes
import datetime
import math
import random
import time

import pymem
import win32gui

from hangso import *
from tienich import *

OFFSET_DIACHICOSOTHONGTINGAME = 0x371754

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
        self._thoidiemthucthicaulenhgannhat = time.time() - 0.5
        self._thoidiemthaotacnhomgannhat = time.time() - 1.
        self._thoidiemkhoitaothongtinbandogannhat = time.time() - 0.5
        self._thoidiemtudongtimduonggannhat = time.time() - 1.

        self._is_tamngungtancong = False

        self._thoidiemkhongcomuctieugannhat = time.time()
        self._diachicosothongtinnhanvatmuctieutruocdo = False

        self._soluonghieuungnhanvattruocdo_map = {}
        self._thoidiemsoluonghieuungbangkhonggannhat_map = {}

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

    def get_diachicosothongtingame(self):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

    def get_diachicosothongtinnhanvat1(self):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVAT1)

    def get_diachicosothongtindoituongx(self, x):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVATX + x * 0x4)

    def get_diachicosothongtinkynang(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
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

    def action_lammoitrangthaimoitruong(self):
        diachicosothongtinnhanvatmuctieuhientai = self.get_diachicosothongtinnhanvatmuctieudangchon()

        if diachicosothongtinnhanvatmuctieuhientai:
            self._thoidiemkhongcomuctieugannhat = time.time()

        if self._diachicosothongtinnhanvatmuctieutruocdo != diachicosothongtinnhanvatmuctieuhientai:
            self._diachicosothongtinnhanvatmuctieutruocdo = diachicosothongtinnhanvatmuctieuhientai

        # print(self.get_danhsachhieuungnhanvats())

    def get_is_cuasogametontai(self):
        tencuaso = str(win32gui.GetWindowText(self.idcuaso))
        return "(" in tencuaso

    def get_is_cuasogamekichhoat(self):
        return win32gui.GetForegroundWindow() == self.idcuaso

    def get_diachicosothongtinnhanvatdangchichuot(self):
        return read_int(self.tientrinh, self.diachixq + 0x37FA54)

    def get_idnguoichoi(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x24)

    def get_is_dangmatketnoi(self):
        return not self.get_is_nhanvattontai()

    def get_iddoituong(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x20)

    def get_idloaidoituong(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0xF0)

    #Gọi là không tồn tại nó không đúng. Mà là nó ngoài tầm mà nhân vật thấy được nên không có thông tin về nó nữa
    def get_is_nhanvattontai(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return self.get_iddoituong(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) != LOAIDOITUONG_VATPHAMDUOIDAT

    def get_is_vatphamtontai(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return self.get_iddoituong(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) == LOAIDOITUONG_VATPHAMDUOIDAT

    def get_is_nhanvatdachet(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        return read_boolean(self.tientrinh, diachicosothongtinnhanvat + 0x1424)

    def get_tendoituong(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_string(self.tientrinh, diachicosothongtinnhanvat + 0x10AC)

    def get_tennhanvatchichuot(self):
        diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvatdangchichuot()
        if not diachicosothongtinnhanvat:
            return False
        return self.get_tendoituong(diachicosothongtinnhanvat)

    def get_sinhlucconlai(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x152C)

    def get_sinhluctoida(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x1530)

    def get_noilucconlai(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x1534)

    def get_noiluctoida(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x1538)

    def get_idmaphientai(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x15F4)

    def get_phantramsinhlucconlai(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1410) * 2

    def get_toadox(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x18)

    def get_toadoy(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1C)

    def get_idloaipk(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0xAED6CC)

    def get_tenbang(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        return read_string(self.tientrinh, diachicosothongtinnhanvat + 0x1136)

    def get_is_cungbang(self, diachicosothongtinnhanvat):
        return False

    def get_idtrangthaichuot(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDA8)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1A4)

    def set_idtrangthaichuot(self, idtrangthaichuot):
        if idtrangthaichuot == self.get_idtrangthaichuot():
            return
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
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

    def get_idtuthenhanvat(self, diachicosothongtinnhanvat = False):
        """
            1: đứng yên, 2: di chuyển, 6: tấn công, 11: delay sau tấn công
        """
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1178)

    def get_is_dangdelaysautancong(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x11B8) == 11

    def get_soluonghieuungnhanvat(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        soluonghieuungnhanvat = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x2EE8)

        soluonghieuungnhanvattruocdo = self._soluonghieuungnhanvattruocdo_map.get(diachicosothongtinnhanvat, -1)

        if soluonghieuungnhanvattruocdo > 0 and soluonghieuungnhanvat == 0:
            self._thoidiemsoluonghieuungbangkhonggannhat_map[diachicosothongtinnhanvat] = time.time()

        self._soluonghieuungnhanvattruocdo_map[diachicosothongtinnhanvat] = soluonghieuungnhanvat

        return soluonghieuungnhanvat

    def get_danhsachhieuungnhanvats(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
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

    def get_is_cohieuungcoloinhanvat(self, diachicosothongtinnhanvat = False):
        return self.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, ), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvat, is_hieuungcoloi = 1)

    def get_is_cohieuungbatloinhanvat(self, diachicosothongtinnhanvat = False):
        return self.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG, HIEUUNGKYNANG_CHOANG, ), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvat, is_hieuungcoloi = 0)

    def get_is_cohieuungs(self, idhieuungs, macdinh, diachicosothongtinnhanvat = False, is_hieuungcoloi: int = None): #is_loihai: Kiểm tra lợi hại nữa
        if not diachicosothongtinnhanvat:
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
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
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

    def get_is_kynangsansang(self, idvitriX, idvitriY):
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang:
            return False
        idvitrikynang = 14 * idvitriY + idvitriX #Vì mỗi cuốn nó chỉ có tối đa 12 kỹ năng cho nên nó nhích lên 14 để không bao giờ trùng nhau

        return read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830) and read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6A4C) == 0

    def get_is_cothetancong(self, diachicosothongtinnhanvat):
        if not diachicosothongtinnhanvat:
            return False

        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
            return False

        if self.get_is_nhanvatdachet(diachicosothongtinnhanvat):
            return False

        if self.get_idnguoichoi(diachicosothongtinnhanvat) in NHANVATTODOITUDONGs:
            return False

        idloainhanvat = self.get_idloainhanvat(diachicosothongtinnhanvat)

        if idloainhanvat == LOAIMUCTIEU_NGUOICHOICUNGNHOM:
            return False

        if self.get_is_npc(diachicosothongtinnhanvat):
            return False

        idloaipk = self.get_idloaipk()

        if idloaipk == LOAIPK_HOABINH:
            if idloainhanvat in (LOAIMUCTIEU_NGUOICHOIKHACNHOM, LOAIMUCTIEU_NGUOICHOICUNGNHOM):
                return False
        elif idloaipk == LOAIPK_NHOM:
            if idloainhanvat == LOAIMUCTIEU_NGUOICHOICUNGNHOM:
                return False
        elif idloaipk == LOAIPK_BANG:
            if idloainhanvat == LOAIMUCTIEU_NGUOICHOIKHACNHOM and self.get_is_cungbang(diachicosothongtinnhanvat):
                return False
        elif idloaipk == LOAIPK_TUDO:
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
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFE0C)

        if not x:
            return False

        return read_boolean(self.tientrinh, x + 0x34)


    def get_is_dangbatenter(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFD60)
        if not x:
            return False
        return read_boolean(self.tientrinh, x + 0x8140)

    def get_thoidiemkhongcomuctieugannhat(self):
        return self._thoidiemkhongcomuctieugannhat

    def get_diachicosothongtinnhanvatmuctieudangchon(self):
        return read_int(self.tientrinh, self.diachixq + 0x1BC440)

    def get_is_dangclickchuottrai(self):
        return read_boolean(self.tientrinh, self.diachixq + 0x37FA6D)

    def set_diachicosothongtinnhanvatmuctieudangchon(self, diachicosothongtinnhanvat):
        if self.get_diachicosothongtinnhanvatmuctieudangchon() == diachicosothongtinnhanvat:
            return

        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = 0
            iddoituong = 0
        else:
            iddoituong = self.get_iddoituong(diachicosothongtinnhanvat)
            if iddoituong == -1:
                diachicosothongtinnhanvat = 0
                iddoituong = 0

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

    def action_vohieuhoaxoamuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x951A5, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x951A5, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)
        if read_bytes(self.tientrinh, self.diachixq + 0x9519B, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x9519B, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

    def action_tatvohieuhoaxoamuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x951A5, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x951A5, bytes.fromhex("C7 05"), 2)
            write_int(self.tientrinh, self.diachixq + 0x951A5 + 2, self.diachixq + 0x1BC3E0)
            write_int(self.tientrinh, self.diachixq + 0x951A5 + 6, 0)
        if read_bytes(self.tientrinh, self.diachixq + 0x9519B, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x9519B, bytes.fromhex("C7 05"), 2)
            write_int(self.tientrinh, self.diachixq + 0x9519B + 2, self.diachixq + 0x37173C)
            write_int(self.tientrinh, self.diachixq + 0x9519B + 6, 0)

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
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFE10)
        if not x:
            return False

        return read_boolean(self.tientrinh, x + 0x34)

    def set_is_danghiencuasoyesno(self, is_danghiencuasoyesno):
        if self.get_is_danghiencuasoyesno() == is_danghiencuasoyesno:
            return

        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return

        x = read_int(self.tientrinh, x + 0xADFE10)
        if not x:
            return

        return write_boolean(self.tientrinh, x + 0x34, is_danghiencuasoyesno)

    def get_caulenhthucthihientai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFE10)
        if not x:
            return False

        return read_string(self.tientrinh, x + 0x7C).strip()

    def set_caulenhthucthihientai(self, caulenh):
        if self.get_caulenhthucthihientai() == caulenh:
            return
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
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
            write_int(self.tientrinh, self._diachiautoassemblemocuasotuychonnhanvatchinh + 7, self.diachixq + 0x37FA34)

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
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangphimtat + 7, self.diachixq + 0x37FA34)

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
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangvitri + 7, self.diachixq + 0x37FA34)

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
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 2, self.diachixq + 0x37FA34)

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
            write_int(self.tientrinh, self._diachiautoassemblenhatdo + 2, self.diachixq + 0x37FA34)

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
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 2, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 6, bytes.fromhex("BF"), 1)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 7, 64)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 11, bytes.fromhex("BE"), 1)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 12, 20200001)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 16, bytes.fromhex("56"), 1)
            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 17, bytes.fromhex("57"), 1)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 18, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 19, self.diachixq + 0x3C020 - (self._diachiautoassemblekhoitaothongtinbando + 18) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 23, bytes.fromhex("8B 35"), 2)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 25, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 29, bytes.fromhex("8B B6"), 2)
            write_int(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 31, self.diachixq + 0xADFDEC)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 35, bytes.fromhex("B0 00 88 06"), 4)

            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando + 39, bytes.fromhex("C3"), 1)
            self._is_dasetupautoassemblekhoitaothongtinbando = True

        self.tientrinh.start_thread(self._diachiautoassemblekhoitaothongtinbando)

    def auto_assemble_tudongtimduong(self, x, y, idbando):
        if not self._is_dasetupautoassembletudongtimduong:
            self._diachiautoassembletudongtimduong = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong, bytes.fromhex("8B 35"), 2)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 2, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self._diachiautoassembletudongtimduong + 6, bytes.fromhex("8B B6"), 2)
            write_int(self.tientrinh, self._diachiautoassembletudongtimduong + 8, self.diachixq + 0xADFDEC)

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

        self.tientrinh.start_thread(self._diachiautoassembletudongtimduong)

    def action_nhatdo(self, delay = 2):
        if time.time() - self._thoidiemnhatdogannhat < delay:
            return
        self._thoidiemnhatdogannhat = time.time()
        self.auto_assemble_nhatdo()

    def action_battheosaunhom(self, delay = 1):
        if time.time() - self._thoidiembattattheosaunhomgannhat < delay:
            return

        self._thoidiembattattheosaunhomgannhat = time.time()

        idnguoichoitruongnhom = self.get_idnguoichoitruongnhom()
        if not idnguoichoitruongnhom:
            return

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

    def action_sudungkynangvitrilenbanthan(self, idvitriX, idvitriY, delay = 0.25):
        idvitri = (idvitriX, idvitriY)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()

        idkynang = self.get_idkynang(idvitriX, idvitriY)
        if not idkynang:
            return

        self.action_thucthicaulenh("pf {} {}".format(idkynang, self.get_idnguoichoi()))

    def action_dichuyen(self, x, y, delay = 0.5):
        if time.time() - self._thoidiemdichuyengannhat < delay:
            return

        self._thoidiemdichuyengannhat = time.time()

        self.auto_assemble_dichuyen(x, y)

    def action_dichuyengiukhoangcachtoida(self, diachicosothongtinnhanvat2, khoangcachtoida):
        if not diachicosothongtinnhanvat2:
            return
        return self.action_dichuyengiukhoangcachtoidadiem(self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2), khoangcachtoida = khoangcachtoida)

    def action_dichuyengiukhoangcachtoidadiem(self, x2, y2, khoangcachtoida):
        diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)

        khoangcach = round(math.dist((x1, y1), (x2, y2)), 2)

        if khoangcach <= khoangcachtoida:
            return

        khoangcachtoida = max(0., khoangcachtoida - 1.) #Đi gần vào hơn khoảng cách tối đa 1 chút

        deltax = x2 - x1
        deltay = y1 - y2

        khoangcachdichuyen = khoangcach - khoangcachtoida

        if not khoangcachdichuyen:
            return

        if khoangcach > 0.:
            deltax = round(khoangcachdichuyen * deltax / khoangcach, 2)
            deltay = round(khoangcachdichuyen * deltay / khoangcach, 2)

        if not deltax and not deltay:
            return

        xmax = self._kichthuoccuasogame[0]
        ymax = self._kichthuoccuasogame[1]

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = round(self._centerx + deltax * toadomoidonvikhoangcachx)
        yclick = round(self._centery + deltay * toadomoidonvikhoangcachy)

        self.action_dichuyen(xclick, yclick)

    def action_dichuyentiepcan(self, diachicosothongtinnhanvat2):
        self.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvat2, khoangcachtoida = 0)

    def action_sudungkynangvitriphudau(self, idvitriX, idvitriY, diachicosothongtinnhanvat2, khoangcachphudau = 2, delay = 0.25):
        if not diachicosothongtinnhanvat2:
            return
        return self.action_sudungkynangvitriphudaudiem(idvitriX, idvitriY, self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2), khoangcachphudau = khoangcachphudau, delay = delay)

    def action_sudungkynangvitriphudaudiem(self, idvitriX, idvitriY, x2, y2, khoangcachphudau = 2, delay = 0.25):
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

        if khoangcachphudau:
            if khoangcach:
                khoangcachdichuyen = khoangcach + khoangcachphudau
                deltax = deltax * khoangcachdichuyen / khoangcach
                deltay = deltay * khoangcachdichuyen / khoangcach
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
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False

        x = read_short_int(self.tientrinh, x + 0xADFEA6 + idvitriphimtat)

        return x in (LOAIDOITUONGPHIMTAT_KYNANG, LOAIDOITUONGPHIMTAT_VATPHAM)

    def get_is_dangvankhi(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFDE8)

        if not x:
            return False

        return read_int(self.tientrinh, x + 0xD8) == TRANGTHAIVANKHI_DANGVANKHI

    def get_is_dakhoitaothongtinbando(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)

        return x > 0

    def action_khoitaothongtinbando(self, delay = 0.5):
        if time.time() - self._thoidiemkhoitaothongtinbandogannhat < delay:
            return

        if self.get_is_dakhoitaothongtinbando():
            return

        self.auto_assemble_khoitaothongtinbando()

    def action_tudongtimduong(self, x, y, idbando, delay = 1.):
        if time.time() - self._thoidiemtudongtimduonggannhat < delay:
            return

        if not self.get_is_dakhoitaothongtinbando():
            return

        self.auto_assemble_tudongtimduong(x, y, idbando)
