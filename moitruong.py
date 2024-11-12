import ctypes
import datetime
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
        self.kichthuoccuasogame = 800., 600.
        self.centerx, self.centery = 430., 300.

        self.is_dasetupautoassemblebattattheosaunhom = False
        self.is_dasetupautoassemblemocuasotuychonnhanvatchinh = False
        self.is_dasetupautoassemblesudungkynangphimtat = False
        self.is_dasetupautoassembledichuyen = False
        self.is_dasetupautoassemblechonvungsudungkynang = False
        self.is_dasetupautoassemblesudungkynangvitri = False
        self.is_dasetupautoassemblenhatdo = False

        self.thoidiembattattheosaunhomgannhat = time.time() - 0.5
        self.thoidiemdichuyengannhat = time.time() - 0.5
        self.thoidiemchonvungsudungkynanggannhat = time.time() - 0.5
        self.thoidiemsudungkynangphimtatgannhat_map = {}
        self.thoidiemsudungkynangvitrigannhat_map = {}
        self.thoidiemnhatdogannhat = time.time() - 2.

        self.diachicosothongtinnhanvattruongnhom = False
        self._is_tamngungtancong = False

        self._idtrangthaichuot = 0
        # self.thoidiemchokhoanhvungkynanggannhat = time.time()
        # self.thoidiemlammoicuasotuychonnhanvatchinh = time.time()
        

    def __del__(self):
        if self.is_dasetupautoassemblebattattheosaunhom:
            self.tientrinh.free(self.diachiautoassemblebattattheosaunhom)

        if self.is_dasetupautoassemblemocuasotuychonnhanvatchinh:
            self.tientrinh.free(self.diachiautoassemblemocuasotuychonnhanvatchinh)

        if self.is_dasetupautoassemblesudungkynangphimtat:
            self.tientrinh.free(self.diachiautoassemblesudungkynangphimtat)

        if self.is_dasetupautoassembledichuyen:
            self.tientrinh.free(self.diachiautoassembledichuyen)

        if self.is_dasetupautoassemblechonvungsudungkynang:
            self.tientrinh.free(self.diachiautoassemblechonvungsudungkynang)

        if self.is_dasetupautoassemblesudungkynangvitri:
            self.tientrinh.free(self.diachiautoassemblesudungkynangvitri)

        if self.is_dasetupautoassemblenhatdo:
            self.tientrinh.free(self.diachiautoassemblenhatdo)

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

    def action_lammoitrangthaimoitruong(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return False

        diachicosothongtinnhanvattruongnhom = False

        idnhanvattruongnhom = read_int(self.tientrinh, diachicosothanhviennhom)

        if idnhanvattruongnhom:
            if self.diachicosothongtinnhanvattruongnhom and self.get_idnhanvat(self.diachicosothongtinnhanvattruongnhom) == idnhanvattruongnhom and self.get_is_nhanvattontai(self.diachicosothongtinnhanvattruongnhom):
                diachicosothongtinnhanvattruongnhom = self.diachicosothongtinnhanvattruongnhom
            else:
                i = 0
                while True:
                    diachicosothongtinnhanvatxemxet = self.get_diachicosothongtindoituongx(i)
                    if not diachicosothongtinnhanvatxemxet:
                        break
                    i += 1
                    if not self.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                        continue
                    idnhanvat = self.get_idnhanvat(diachicosothongtinnhanvatxemxet)
                    if not idnhanvat:
                        continue
                    if idnhanvat == idnhanvattruongnhom:
                        diachicosothongtinnhanvattruongnhom = diachicosothongtinnhanvatxemxet
                        break

        self.diachicosothongtinnhanvattruongnhom = diachicosothongtinnhanvattruongnhom

        idtrangthaichuot = self.get_idtrangthaichuot()

        if idtrangthaichuot != self._idtrangthaichuot:
            # if idtrangthaichuot == TRANGTHAICHUOT_KHOANHVUNGKYNANG:
            #     self.thoidiemchokhoanhvungkynanggannhat = time.time()
            self._idtrangthaichuot = idtrangthaichuot


        # if time.time() - self.thoidiemlammoicuasotuychonnhanvatchinh > 2:
        #     x = read_int(self.tientrinh, self.diachixq + 0x3A531C)
        #     if x:
        #         write_int(self.tientrinh, x + 0x2C, 0)
        #         self.thoidiemlammoicuasotuychonnhanvatchinh = time.time()

    def get_is_cuasogametontai(self):
        tencuaso = str(win32gui.GetWindowText(self.idcuaso))
        return "(" in tencuaso

    def get_is_cuasogamekichhoat(self):
        return win32gui.GetForegroundWindow() == self.idcuaso

    def get_diachicosothongtinnhanvatdangchichuot(self):
        return read_int(self.tientrinh, self.diachixq + 0x37FA54)

    def get_idnhanvat(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x24)

    def get_is_dangmatketnoi(self):
        return not self.get_is_nhanvattontai()

    def get_x(self, diachicosothongtinnhanvat = False):
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x20)

    def get_idloaidoituong(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0xF0)

    def get_is_nhanvattontai(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return self.get_x(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) != LOAIDOITUONG_VATPHAMDUOIDAT

    def get_is_vatphamtontai(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return self.get_x(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) == LOAIDOITUONG_VATPHAMDUOIDAT

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

    def get_khoangcachdiem(self, diem, diachicosothongtinnhanvat1 = False):
        if not diachicosothongtinnhanvat1:
            diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)
        x2, y2 = diem

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
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x2EE8)

    def get_is_cohieuung(self, idhieuung, macdinh, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
            return macdinh

        diachicosohieuungnhanvat = diachicosothongtinnhanvat + OFFSET_DIACHICOSOHIEUUNGNHANVAT
        soluonghieuungnhanvat = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
        soluonghieuungdemduoc = 0
        i = -1

        while True:
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
                return macdinh

            soluonghieuungnhanvatmoinhat = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
            if soluonghieuungnhanvat != soluonghieuungnhanvatmoinhat:
                soluonghieuungnhanvat = soluonghieuungnhanvatmoinhat
                soluonghieuungdemduoc = 0
                i = -1

            i += 1
            if i >= SOLUONGHIEUUNGNHANVATTOIDA:
                return macdinh

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

            if idhieuungxemxet == idhieuung:
                return True

            soluonghieuungdemduoc += 1

            if soluonghieuungdemduoc >= soluonghieuungnhanvatmoinhat:
                return False

        return macdinh

    def get_is_dangtheosaunhom(self):
        return self.get_is_cohieuung(HIEUUNGKYNANG_THEOSAUNHOM, False)

    def get_diachicosoidthanhviennhom(self):
        #Trong nhóm còn nhìn thấy máu của nhau nữa nhé
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDA4)
        if not x:
            return False
        return x

    def get_diachicosothongtintruongnhom(self):
        return self.diachicosothongtinnhanvattruongnhom

    def get_is_truongnhom(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return False
        return self.get_idnhanvat(self.get_diachicosothongtinnhanvat1()) == read_int(self.tientrinh, diachicosothanhviennhom)

    def get_danhsachidthanhviennhoms(self):
        idthanhviens = []
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return idthanhviens
        for i in range(SOLUONGTHANHVIENNHOMTOIDA):
            idthanhvien = read_int(self.tientrinh, diachicosothanhviennhom + i * 0x4)
            if not idthanhvien:
                break
            idthanhviens.append(idthanhviens)

        return idthanhviens
    def get_is_dangotrongnhom(self):
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
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x155C) == 40

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


    def get_is_batenter(self):
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFD60)
        if not x:
            return False
        return read_boolean(self.tientrinh, x + 0x8140)

    def get_diachicosothongtinnhanvatmuctieudangchon(self):
        return read_int(self.tientrinh, self.diachixq + 0x1BC440)

    def get_is_dangclickchuottrai(self):
        return read_boolean(self.tientrinh, self.diachixq + 0x37FA6D)

    def set_diachicosothongtinnhanvatmuctieudangchon(self, diachicosothongtinnhanvat):
        if self.get_diachicosothongtinnhanvatmuctieudangchon() == diachicosothongtinnhanvat:
            return

        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = 0
            x = 0
        else:
            x = self.get_x(diachicosothongtinnhanvat)
            if x == -1:
                diachicosothongtinnhanvat = 0
                x = 0

        write_int(self.tientrinh, self.diachixq + 0x1BC3E0, diachicosothongtinnhanvat)
        write_int(self.tientrinh, self.diachixq + 0x37173C, x)

        write_int(self.tientrinh, self.diachixq + 0x1BC440, diachicosothongtinnhanvat)
        write_int(self.tientrinh, self.diachixq + 0x1BC444, x)

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

    def auto_assemble_mocuasotuychonnhanvatchinh(self):
        if not self.is_dasetupautoassemblemocuasotuychonnhanvatchinh:
            self.diachiautoassemblemocuasotuychonnhanvatchinh = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasotuychonnhanvatchinh, bytes.fromhex("BA 3F000000"), 5)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasotuychonnhanvatchinh + 5, bytes.fromhex("8B 3D"), 2)
            write_int(self.tientrinh, self.diachiautoassemblemocuasotuychonnhanvatchinh + 7, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasotuychonnhanvatchinh + 11, bytes.fromhex("8D 77 14"), 3)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasotuychonnhanvatchinh + 14, bytes.fromhex("8B CF"), 2)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasotuychonnhanvatchinh + 16, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblemocuasotuychonnhanvatchinh + 17, self.diachixq + 0x70B20 - (self.diachiautoassemblemocuasotuychonnhanvatchinh + 16) - 5)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasotuychonnhanvatchinh + 21, bytes.fromhex("C3"), 1)

            self.is_dasetupautoassemblemocuasotuychonnhanvatchinh = True

        self.tientrinh.start_thread(self.diachiautoassemblemocuasotuychonnhanvatchinh)

    def auto_assemble_battattheosaunhom(self):
        if not self.is_dasetupautoassemblebattattheosaunhom:
            self.diachiautoassemblebattattheosaunhom = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom, bytes.fromhex("BB 0B 00 00 00"), 5)

            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 5, bytes.fromhex("8B 0D 1C 53 7A 00"), 6)
            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 11, bytes.fromhex("8B 3C 99"), 3)
            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 14, bytes.fromhex("8B F7"), 2)
            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 16, bytes.fromhex("B8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 17, 2)
            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 21, bytes.fromhex("8B 8C 86 34 10 00 00"), 7)
            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 28, bytes.fromhex("51"), 1)
            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 29, bytes.fromhex("8B 8C C6 B4 10 00 00"), 7)
            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 36, bytes.fromhex("03 8E 78 11 00 00"), 6)

            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 42, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 43, self.diachixq + 0x3A330 - (self.diachiautoassemblebattattheosaunhom + 42) - 5)

            write_bytes(self.tientrinh, self.diachiautoassemblebattattheosaunhom + 47, bytes.fromhex("C3"), 1)

            self.is_dasetupautoassemblebattattheosaunhom = True

        if not self.get_is_damocuasotuychonnhanvatchinhlandau():
            phatam("Bật tắt theo sau nhóm thất bại. Chưa mở cửa sổ tùy chọn nhân vật chính lần đầu")
            return

        self.tientrinh.start_thread(self.diachiautoassemblebattattheosaunhom)


    def auto_assemble_sudungkynangphimtat(self, idvitriphimtat):
        if not self.is_dasetupautoassemblesudungkynangphimtat:
            self.diachiautoassemblesudungkynangphimtat = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangphimtat, bytes.fromhex("B8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 1, idvitriphimtat)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 5, bytes.fromhex("8B 15"), 2)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 7, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 11, bytes.fromhex("50"), 1)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 12, bytes.fromhex("8D 8A"), 2)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 14, 0xADFEA0)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 18, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 19, self.diachixq + 0x72E70 - (self.diachiautoassemblesudungkynangphimtat + 18) - 5)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 23, bytes.fromhex("C3"), 1)

            self.is_dasetupautoassemblesudungkynangphimtat = True
        else:
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 1, idvitriphimtat)

        self.tientrinh.start_thread(self.diachiautoassemblesudungkynangphimtat)


    def auto_assemble_sudungkynangvitri(self, idvitriX, idvitriY, hinhthucsudungkynang = HINHTHUCSUDUNGKYNANG_CANMUCTIEU):
        idkynang = self.get_idkynang(idvitriX, idvitriY)
        if not idkynang:
            return

        if not self.is_dasetupautoassemblesudungkynangvitri:
            self.diachiautoassemblesudungkynangvitri = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangvitri, bytes.fromhex("B8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 1, idkynang)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 5, bytes.fromhex("8B 0D"), 2)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 7, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 11, bytes.fromhex("BA"), 1)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 12, hinhthucsudungkynang)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 16, bytes.fromhex("52"), 1)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 17, bytes.fromhex("50"), 1)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 18, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 19, self.diachixq + 0x53D60 - (self.diachiautoassemblesudungkynangvitri + 18) - 5)

            write_bytes(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 23, bytes.fromhex("C3"), 1)

            self.is_dasetupautoassemblesudungkynangvitri = True
        else:
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 12, hinhthucsudungkynang)
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangvitri + 1, idkynang)

        self.tientrinh.start_thread(self.diachiautoassemblesudungkynangvitri)


    def auto_assemble_chonvungsudungkynang(self, x, y):
        if not self.is_dasetupautoassemblechonvungsudungkynang:
            self.diachiautoassemblechonvungsudungkynang = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self.diachiautoassemblechonvungsudungkynang, bytes.fromhex("8B 3D"), 2)
            write_int(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 2, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 6, bytes.fromhex("BD"), 1)
            write_int(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 7, x)

            write_bytes(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 11, bytes.fromhex("BB"), 1)
            write_int(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 12, y)

            write_bytes(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 16, bytes.fromhex("53"), 1)

            write_bytes(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 17, bytes.fromhex("55"), 1)

            write_bytes(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 18, bytes.fromhex("8B CF"), 2)


            write_bytes(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 20, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 21, self.diachixq + 0x9200 - (self.diachiautoassemblechonvungsudungkynang + 20) - 5)

            write_bytes(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 25, bytes.fromhex("C3"), 1)
            self.is_dasetupautoassemblechonvungsudungkynang = True
        else:
            write_int(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 7, x)
            write_int(self.tientrinh, self.diachiautoassemblechonvungsudungkynang + 12, y)

        self.tientrinh.start_thread(self.diachiautoassemblechonvungsudungkynang)

    def auto_assemble_dichuyen(self, x, y):
        if not self.is_dasetupautoassembledichuyen:
            self.diachiautoassembledichuyen = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen, bytes.fromhex("8B 35"), 2)
            write_int(self.tientrinh, self.diachiautoassembledichuyen + 2, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen + 6, bytes.fromhex("BB"), 1)
            write_int(self.tientrinh, self.diachiautoassembledichuyen + 7, x)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen + 11, bytes.fromhex("BF"), 1)
            write_int(self.tientrinh, self.diachiautoassembledichuyen + 12, y)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen + 16, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self.diachiautoassembledichuyen + 17, 0)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen + 21, bytes.fromhex("57"), 1)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen + 22, bytes.fromhex("53"), 1)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen + 23, bytes.fromhex("8B CE"), 2)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen + 25, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachiautoassembledichuyen + 26, self.diachixq + 0x476A0 - (self.diachiautoassembledichuyen + 25) - 5)

            write_bytes(self.tientrinh, self.diachiautoassembledichuyen + 30, bytes.fromhex("C3"), 1)
            self.is_dasetupautoassembledichuyen = True
        else:
            write_int(self.tientrinh, self.diachiautoassembledichuyen + 7, x)
            write_int(self.tientrinh, self.diachiautoassembledichuyen + 12, y)

        self.tientrinh.start_thread(self.diachiautoassembledichuyen)

    def auto_assemble_nhatdo(self):
        if not self.is_dasetupautoassemblenhatdo:
            self.diachiautoassemblenhatdo = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self.diachiautoassemblenhatdo, bytes.fromhex("8B 0D"), 2)
            write_int(self.tientrinh, self.diachiautoassemblenhatdo + 2, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self.diachiautoassemblenhatdo + 6, bytes.fromhex("8D 59 14"), 3)

            write_bytes(self.tientrinh, self.diachiautoassemblenhatdo + 9, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblenhatdo + 10, self.diachixq + 0xB3F0 - (self.diachiautoassemblenhatdo + 9) - 5)

            write_bytes(self.tientrinh, self.diachiautoassemblenhatdo + 14, bytes.fromhex("C3"), 1)
            self.is_dasetupautoassemblenhatdo = True

        self.tientrinh.start_thread(self.diachiautoassemblenhatdo)

    def action_nhatdo(self, delay = 2):
        if time.time() - self.thoidiemnhatdogannhat < delay:
            return
        self.thoidiemnhatdogannhat = time.time()
        self.auto_assemble_nhatdo()

    def action_battattheosaunhom(self, delay = 1):
        if time.time() - self.thoidiembattattheosaunhomgannhat < delay:
            return

        self.thoidiembattattheosaunhomgannhat = time.time()

        self.auto_assemble_mocuasotuychonnhanvatchinh()
        self.auto_assemble_battattheosaunhom()
    
    def action_sudungkynangphimtat(self, idvitriphimtat, delay = 0.5):
        if idvitriphimtat in self.thoidiemsudungkynangphimtatgannhat_map and time.time() - self.thoidiemsudungkynangphimtatgannhat_map[idvitriphimtat] < delay:
            return
        self.thoidiemsudungkynangphimtatgannhat_map[idvitriphimtat] = time.time()
        self.auto_assemble_sudungkynangphimtat(idvitriphimtat)

    def action_sudungkynangvitri(self, idvitriX, idvitriY, hinhthucsudungkynang = HINHTHUCSUDUNGKYNANG_CANMUCTIEU, delay = 0.25):
        idvitri = (idvitriX, idvitriY)
        if idvitri in self.thoidiemsudungkynangvitrigannhat_map and time.time() - self.thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        self.thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        self.auto_assemble_sudungkynangvitri(idvitriX, idvitriY, hinhthucsudungkynang)

    def action_dichuyen(self, x, y, delay = 0.5):
        if time.time() - self.thoidiemdichuyengannhat < delay:
            return

        self.thoidiemdichuyengannhat = time.time()

        self.auto_assemble_dichuyen(x, y)

    def action_chonvungsudungkynang(self, x, y, delay = 0.5):
        if time.time() - self.thoidiemchonvungsudungkynanggannhat < delay:
            return

        self.thoidiemchonvungsudungkynanggannhat = time.time()

        self.auto_assemble_chonvungsudungkynang(x, y)

    def action_dichuyengiukhoangcachtoida(self, diachicosothongtinnhanvat2, khoangcachtoida):
        khoangcach = self.get_khoangcach(diachicosothongtinnhanvat2)

        if khoangcach <= khoangcachtoida:
            return

        khoangcachtoida = max(0., khoangcachtoida - 1.) #Đi gần vào hơn khoangcachtoida 1 chút

        diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)
        x2, y2 = self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2)

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

        xmax = self.kichthuoccuasogame[0]
        ymax = self.kichthuoccuasogame[1]

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = round(self.centerx + deltax * toadomoidonvikhoangcachx)
        yclick = round(self.centery + deltay * toadomoidonvikhoangcachy)

        # print(xclick, yclick, khoangcach, khoangcachdichuyen)

        self.action_dichuyen(xclick, yclick)

    def action_dichuyentiepcan(self, diachicosothongtinnhanvat2):
        self.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvat2, khoangcachtoida = 0)

    def action_chonvungsudungkynangphudau(self, diachicosothongtinnhanvat2, khoangcachphudau = 2):
        khoangcach = self.get_khoangcach(diachicosothongtinnhanvat2)

        diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)
        x2, y2 = self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2)

        deltax = x2 - x1
        deltay = y1 - y2

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

        xmax = self.kichthuoccuasogame[0]
        ymax = self.kichthuoccuasogame[1]

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = round(self.centerx + deltax * toadomoidonvikhoangcachx)
        yclick = round(self.centery + deltay * toadomoidonvikhoangcachy)

        self.action_chonvungsudungkynang(xclick, yclick)

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