import ctypes
import datetime
import time

import pymem
import win32gui

from hangso import *
from tienich import *

OFFSET_DIACHICOSOTHONGTINGAME = 0x371754

OFFSET_DIACHICOSOTHONGTINNHANVAT1 = 0x37F9E8
OFFSET_DIACHICOSOHIEUUNGNHANVAT = 0x1638
OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT = 0x13C

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

        self.kichthuoccuasogame = kichthuoccuaso[2] - kichthuoccuaso[0], kichthuoccuaso[3] - kichthuoccuaso[1]

        self.is_dasetupautoassemblebattattheosaunhom = False
        self.is_dasetupautoassemblemocuasoluachonnhanvatchinh = False
        self.is_dasetupautoassemblesudungkynangphimtat = False

        self.thoidiembattattheosaunhomgannhat = time.time() - 0.5
        self.thoidiemsudungkynangphimtatgannhat_map = {}

    def __del__(self):
        if self.is_dasetupautoassemblebattattheosaunhom:
            self.tientrinh.free(self.diachiautoassemblebattattheosaunhom)

        if self.is_dasetupautoassemblemocuasoluachonnhanvatchinh:
            self.tientrinh.free(self.diachiautoassemblemocuasoluachonnhanvatchinh)

        if self.is_dasetupautoassemblesudungkynangphimtat:
            self.tientrinh.free(self.diachiautoassemblesudungkynangphimtat)

    def get_diachicosothongtingame(self):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

    def get_diachicosothongtinnhanvat1(self):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVAT1)

    def get_diachicosothongtinnhanvatx(self, x):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVATX + x * 0x4)

    def action_lammoitrangthaimoitruong(self):
        pass

    def get_is_cuasogametontai(self):
        tencuaso = str(win32gui.GetWindowText(self.idcuaso))
        return "(" in tencuaso

    # def get_diachicosothongtinnhanvatdangchichuot(self):
    #     return read_int(self.tientrinh, self.diachixq + 0x37FA54)

    def get_idnhanvat(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x24)

    def get_is_dangmatketnoi(self):
        return not self.get_tennhanvat()

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

    def get_tennhanvat(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_string(self.tientrinh, diachicosothongtinnhanvat + 0x10AC)

    def get_sinhlucconlai(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x152C)

    def get_sinhluctoida(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x1530)

    def get_noilucconlai(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x1534)

    def get_noiluctoida(self):
        return read_int(self.tientrinh, self.get_diachicosothongtingame() + 0x1538)

    def get_phantramsinhlucconlai(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1410) * 2

    def get_toadox(self, diachicosothongtinnhanvat = False):
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x18)

    def get_toadoy(self, diachicosothongtinnhanvat = False):
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1C)

    def get_khoangcach(self, diachicosothongtinnhanvat2, diachicosothongtinnhanvat1 = False):
        if not diachicosothongtinnhanvat1:
            diachicosothongtinnhanvat1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat1), self.get_toadoy(diachicosothongtinnhanvat1)
        x2, y2 = self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2)

        return round(math.dist((x1, y1), (x2, y2)))

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

    def get_danhsachhieuungnhanvats(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        diachicosohieuungnhanvat = diachicosothongtinnhanvat + OFFSET_DIACHICOSOHIEUUNGNHANVAT
        hieuungs = []
        for i in range(SOLUONGHIEUUNGNHANVATTOIDA):
            # is_hieuungtontai = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT) > 0
            # if not is_hieuungtontai:
            #     continue
            idhieuung = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x4), read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x8)

            # idhieuung = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT), read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x4)
            # thoigiancohieuluc = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x8)

            hieuungs.append(idhieuung)

        return hieuungs

    def get_is_dangtheosaunhom(self):
        danhsachhieuungnhanvats = self.get_danhsachhieuungnhanvats()

        is_dangtheosaunhom = (1, -1) in danhsachhieuungnhanvats

        # if is_dangtheosaunhom:
        #     print("get_is_dangtheosaunhom: {}".format(is_dangtheosaunhom))

        return is_dangtheosaunhom

    def get_diachicosoidthanhviennhom(self):
        #Trong nhóm còn nhìn thấy máu của nhau nữa nhé
        x = read_int(self.tientrinh, self.diachixq + 0x37FA34)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDA4)
        if not x:
            return False
        return x

    def get_is_doitruong(self, diachicosothongtinnhanvat = False):
        if not diachicosothongtinnhanvat:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return False
        return self.get_idnhanvat(diachicosothongtinnhanvat) == read_int(self.tientrinh, diachicosothanhviennhom)

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

    def get_idloainhanvat(self, diachicosothongtinnhanvat):
        """
        0:  Quái vật hoặc NPC
        1: Người chơi có thể tấn công
        2: Người chơi không thể tấn công
        """
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x28)

    def get_is_npc(self, diachicosothongtinnhanvat):
        phantramsinhlucconlai = self.get_phantramsinhlucconlai(diachicosothongtinnhanvat)
        if phantramsinhlucconlai > 100:
            return True
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1414) in (7, 12) and not phantramsinhlucconlai

    def get_is_cothetancong(self, diachicosothongtinnhanvat):
        if not diachicosothongtinnhanvat:
            return False

        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
            return False

        if self.get_is_nhanvatdachet(diachicosothongtinnhanvat):
            return False

        idloainhanvat = self.get_idloainhanvat(diachicosothongtinnhanvat)

        if idloainhanvat == LOAIMUCTIEU_NGUOICHOIKHONGTHETANCONG:
            return False

        if self.get_is_npc(diachicosothongtinnhanvat):
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

    def get_diachicosothongtinnhanvatmuctieudangchon(self):
        return read_int(self.tientrinh, self.diachixq + 0x1BC3E0)

    def set_diachicosothongtinnhanvatmuctieudangchon(self, diachicosothongtinnhanvat):
        if not diachicosothongtinnhanvat:
            return

        if self.get_diachicosothongtinnhanvatmuctieudangchon() == diachicosothongtinnhanvat:
            return

        x = self.get_x(diachicosothongtinnhanvat)
        if x == -1:
            return

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

    def auto_assemble_mocuasoluachonnhanvatchinh(self):
        if not self.is_dasetupautoassemblemocuasoluachonnhanvatchinh:
            self.diachiautoassemblemocuasoluachonnhanvatchinh = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasoluachonnhanvatchinh, bytes.fromhex("BA 3F000000"), 5)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasoluachonnhanvatchinh + 5, bytes.fromhex("8B 3D"), 2)
            write_int(self.tientrinh, self.diachiautoassemblemocuasoluachonnhanvatchinh + 7, self.diachixq + 0x37FA34)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasoluachonnhanvatchinh + 11, bytes.fromhex("8D 77 14"), 3)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasoluachonnhanvatchinh + 14, bytes.fromhex("8B CF"), 2)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasoluachonnhanvatchinh + 16, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachiautoassemblemocuasoluachonnhanvatchinh + 17, self.diachixq + 0x70B20 - (self.diachiautoassemblemocuasoluachonnhanvatchinh + 16) - 5)

            write_bytes(self.tientrinh, self.diachiautoassemblemocuasoluachonnhanvatchinh + 21, bytes.fromhex("C3"), 1)

            self.is_dasetupautoassemblemocuasoluachonnhanvatchinh = True

        self.tientrinh.start_thread(self.diachiautoassemblemocuasoluachonnhanvatchinh)

    def auto_assemble_battattheosaunhom(self):
        print("auto_assemble_battattheosaunhom: {}".format(datetime.datetime.now()))
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

        #Phần này phải mở cái cửa sổ lựa chọn 1 lần để nó thiết lập cái gì ấy
        x = read_int(self.tientrinh, self.diachixq + 0x3A531C)
        if not x:
            phatam("Bật tắt theo sau nhóm thất bại")
            return
        x = read_int(self.tientrinh, x + 0x2C)
        if x <= 10:
            self.auto_assemble_mocuasoluachonnhanvatchinh()
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
            write_int(self.tientrinh, self.diachiautoassemblesudungkynangphimtat + 2, idvitriphimtat)

        self.tientrinh.start_thread(self.diachiautoassemblesudungkynangphimtat)

    def action_battattheosaunhom(self, delay = 2):
        if time.time() - self.thoidiembattattheosaunhomgannhat < delay:
            return

        self.thoidiembattattheosaunhomgannhat = time.time()

        self.auto_assemble_battattheosaunhom()
    
    def action_sudungkynangphimtat(self, idvitriphimtat, delay = 0.05):
        if time.time() - self.thoidiemsudungkynangphimtatgannhat_map.get(idvitriphimtat, time.time() - delay) < delay:
            return
        self.thoidiemsudungkynangphimtatgannhat_map[idvitriphimtat] = time.time()
        self.auto_assemble_sudungkynangphimtat(idvitriphimtat)