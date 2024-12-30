import ctypes
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

logger = logging.getLogger(__name__)
logger.addHandler(log_handler)

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
        self._kichthuoccuasogame = 800, 600
        self._xmax, self._ymax = 800, 600
        self._centerx, self._centery = 430, 300

        self._is_dasetupautoassemblemocuasotuychonnhanvatchinh = False
        self._is_dasetupautoassemblesudungkynangphimtat = False
        self._is_dasetupautoassembledichuyen = False
        self._is_dasetupautoassemblesudungkynangvitri = False
        self._is_dasetupautoassemblenhatdo = False
        self._is_dasetupautoassemblekhoitaothongtinbando = False
        self._is_dasetupautoassemblethucthicaulenh = False
        self._is_dasetupautoassemblenhatdotoado = False
        self._is_dasetupautoassemblenhatruong = False
        self._is_dasetupautoassembledichuyenvatphamhanhtrang = False
        self._is_dasetupautoassembletrieuhoibaothu = False
        self._is_dasetupautoassemblesudungkynangbaothu = False
        self._is_dasetupautoassemblesudungvatpham = False
        self._is_dasetupautoassemblesudungvatphambaothu = False
        self._is_dasetupautoassembletudongtimduong = False
        self._is_dasetupautoassemblethaotacnhom = False
        self._is_dasetupautoassemblesudungkynang = False
        self._is_dasetupautoassemblesudungkynangmuctieunguoichoi = False
        self._is_dasetupautoassemblesudungkynangmuctieukhacnguoichoi = False
        self._is_dasetupautoassemblesudungkynangtoado = False
        self._is_dasetupautoassembletrochuyenvoinpc = False

        self._thoidiembattattheosaunhomgannhat = time.time() - 0.5
        self._thoidiemdichuyengannhat = time.time() - 0.5
        self._thoidiemsudungkynangphimtatgannhat_map = {}
        self._thoidiemsudungkynangvitrigannhat_map = {}
        self._thoidiemsudungkynanggannhat = time.time()
        self._thoidiemnhatdogannhat = time.time() - 2.
        self._thoidiemnhatdogannhat_map = {}
        self._thoidiemthucthicaulenhgannhat = time.time() - 0.5
        self._thoidiemthaotacnhomgannhat = time.time() - 1.
        self._thoidiemkhoitaothongtinbandogannhat = time.time() - 0.5
        self._thoidiemphucsinhgannhat = time.time() - 1.
        self._thoidiemmaupkgannhat = time.time() - 1.
        self._thoidiemsuadogannhat = time.time() - 1.
        self._thoidiemsudungchucnangmorong5 = time.time() - 2.5
        self._thoidiemtuthenhanvatdungimgannhat = time.time()
        self._thoidiemtuthenhanvatdungimcomuctieugannhat = time.time()
        self._thoidiemngungdichuyengannhat = time.time() - 0.25

        self._idthucuoi = False
        self._thoidiemkhongcuoithugannhat = time.time()

        self._is_tamngungtancong = False

        self._is_vohieuhoadichuyen = False

        self._thoidiemkhongcomuctieugannhat = time.time()

        self._soluonghieuungnhanvattruocdo_map = {}
        self._thoidiemsoluonghieuungbangkhonggannhat_map = {}

        self._diachicosothongtinnhanvatmuctieudangchon = False

        self._thoidiemthaydoibandogannhat = time.time()
        self._idbandohientai = False

        self._thoidiemcohieuungtienthanvodichgannhat = time.time()
        self._thoidiemcohieuungnoikhanggannhat = time.time()

        self._thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat = time.time()

        self._diachicosothongtinnhanvattruongnhom = False

    def __del__(self):
        if self._is_dasetupautoassemblesudungkynangphimtat:
            self.tientrinh.free(self._diachiautoassemblesudungkynangphimtat)

        if self._is_dasetupautoassembledichuyen:
            self.tientrinh.free(self._diachiautoassembledichuyen)

        if self._is_dasetupautoassemblekhoitaothongtinbando:
            self.tientrinh.free(self._diachiautoassemblekhoitaothongtinbando)

        if self._is_dasetupautoassembletudongtimduong:
            self.tientrinh.free(self._diachiautoassembletudongtimduong)

        if self._is_dasetupautoassemblethucthicaulenh:
            self.tientrinh.free(self._diachiautoassemblethucthicaulenh)

        if self._is_dasetupautoassembletrochuyenvoinpc:
            self.tientrinh.free(self._diachiautoassembletrochuyenvoinpc)

        if self._is_dasetupautoassembletrieuhoibaothu:
            self.tientrinh.free(self._diachiautoassembletrieuhoibaothu)

        if self._is_dasetupautoassemblesudungkynangbaothu:
            self.tientrinh.free(self._diachiautoassemblesudungkynangbaothu)

        if self._is_dasetupautoassemblesudungvatpham:
            self.tientrinh.free(self._diachiautoassemblesudungvatpham)

        if self._is_dasetupautoassemblesudungvatphambaothu:
            self.tientrinh.free(self._diachiautoassemblesudungvatphambaothu)

        if self._is_dasetupautoassembledichuyenvatphamhanhtrang:
            self.tientrinh.free(self._diachiautoassembledichuyenvatphamhanhtrang)

        if self._is_dasetupautoassemblethaotacnhom:
            self.tientrinh.free(self._diachiautoassemblethaotacnhom)

        if self._is_dasetupautoassemblesudungkynang:
            self.tientrinh.free(self._diachiautoassemblesudungkynang)

        if self._is_dasetupautoassemblesudungkynangmuctieunguoichoi:
            self.tientrinh.free(self._diachiautoassemblesudungkynangmuctieunguoichoi)

        if self._is_dasetupautoassemblesudungkynangmuctieukhacnguoichoi:
            self.tientrinh.free(self._diachiautoassemblesudungkynangmuctieukhacnguoichoi)

        if self._is_dasetupautoassemblesudungkynangtoado:
            self.tientrinh.free(self._diachiautoassemblesudungkynangtoado)

        if self._is_dasetupautoassemblenhatdo:
            self.tientrinh.free(self._diachiautoassemblenhatdo)

        if self._is_dasetupautoassemblenhatdotoado:
            self.tientrinh.free(self._diachiautoassemblenhatdotoado)

        if self._is_dasetupautoassemblenhatruong:
            self.tientrinh.free(self._diachiautoassemblenhatruong)

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
        return read_string(self.tientrinh, x + idvitri * 0x20 + 0x1A8)

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

    def get_thoidiemtuthenhanvatdungimcomuctieugannhat(self):
        return self._thoidiemtuthenhanvatdungimcomuctieugannhat

    def action_lammoitrangthaimoitruong(self):
        diachicosothongtinnhanvatmuctieuhientai = self.get_diachicosothongtinnhanvatmuctieudangchon()

        if diachicosothongtinnhanvatmuctieuhientai:
            self._thoidiemkhongcomuctieugannhat = time.time()

        if self.get_idtuthenhanvat() != TUTHENHANVAT_DUNGIM:
            self._thoidiemtuthenhanvatdungimgannhat = time.time()
            self._thoidiemtuthenhanvatdungimcomuctieugannhat = time.time()

        if not diachicosothongtinnhanvatmuctieuhientai:
            self._thoidiemtuthenhanvatdungimcomuctieugannhat = time.time()

        idbandohientai = self._get_idbandohientai()

        if idbandohientai != self._idbandohientai:
            self._thoidiemthaydoibandogannhat = time.time()

        self._idbandohientai = idbandohientai

        idthucuoi = self._get_idthucuoi()

        if idthucuoi:
            self._thoidiemkhongcuoithugannhat = time.time()

        self._idthucuoi = idthucuoi

        if not self.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, ), macdinh = True, is_hieuungcoloi = 1):
            self._thoidiemcohieuungtienthanvodichgannhat = time.time()

        if not self.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG, ), macdinh = True, is_hieuungcoloi = 1):
            self._thoidiemcohieuungnoikhanggannhat = time.time()

        idnguoichoitruongnhom = self.get_idnguoichoitruongnhom()
        if idnguoichoitruongnhom and not self.get_diachicosothongtinnhanvattruongnhom():
            self._diachicosothongtinnhanvattruongnhom = self.action_timkiemnhanvat(idnguoichoi = idnguoichoitruongnhom)

    def get_thoidiemthaydoibandogannhat(self):
        return self._thoidiemthaydoibandogannhat

    def get_is_cuasogametontai(self):
        tencuaso = str(win32gui.GetWindowText(self.idcuaso))
        # return "Chien Quoc" in tencuaso
        return "(" in tencuaso and ")" in tencuaso

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
        return self.get_iddoituong(diachicosothongtinnhanvat) > 0 and self.get_idloaidoituong(diachicosothongtinnhanvat) in (LOAIDOITUONG_NHANVAT1, LOAIDOITUONG_NHANVATKHAC1)

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
        return self._idbandohientai

    def _get_idbandohientai(self):
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

    def get_toadoxsaptoi(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN:
            return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x18)
        return read_int(self.tientrinh, diachicosothongtinnhanvat)

    def get_toadoysaptoi(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()

        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN:
            return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1C)

        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x4)

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

        logger.error("{} set_idmaupk: {}".format(self.get_tendoituong(), idmaupk))

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

        logger.error("{} set_idtrangthaichuot: {}".format(self.get_tendoituong(), idtrangthaichuot))

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

    def get_idthucuoi(self):
        return self._idthucuoi

    def _get_idthucuoi(self, diachicosothongtinnhanvat = None):
        if diachicosothongtinnhanvat is None:
            diachicosothongtinnhanvat = self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1198)


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

        logger.error("{} set_idtuthenhanvat: {}".format(self.get_tendoituong(), idtuthenhanvat))

        write_int(self.tientrinh, diachicosothongtinnhanvat + 0x1178, idtuthenhanvat)

    def get_is_muctieuchaytron(self, diachicosothongtinnhanvat):
        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) != TUTHENHANVAT_DICHUYEN:
            return False

        x1, y1 = self.get_toadox(diachicosothongtinnhanvat, is_vitrihientai = True), self.get_toadoy(diachicosothongtinnhanvat, is_vitrihientai = True)
        x2, y2 = self.get_toadoxsaptoi(diachicosothongtinnhanvat), self.get_toadoysaptoi(diachicosothongtinnhanvat)

        return self.get_khoangcachdiem(x2, y2) > self.get_khoangcachdiem(x1, y1)

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

    def get_thoigianconlaihieuungtienthanvodich(self, macdinh):
        x = self.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, ), macdinh = (True, macdinh), is_hieuungcoloi = 1, is_travethoigianhieuluctoida = True)
        if not x:
            return 0.

        is_cohieuung, thoigianhieuluctoida = x

        if not is_cohieuung:
            return 0.
        return thoigianhieuluctoida - (time.time() - self._thoidiemcohieuungtienthanvodichgannhat)

    def get_is_cohieuungs(self, idhieuungs, macdinh, diachicosothongtinnhanvat = None, is_hieuungcoloi: int = None, is_travethoigianhieuluctoida = False): #is_loihai: Kiểm tra lợi hại nữa
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
                    if is_travethoigianhieuluctoida:
                        return is_hieuungcoloixemxet == is_hieuungcoloi, thoigianhieuluctoida
                    return is_hieuungcoloixemxet == is_hieuungcoloi

                if is_travethoigianhieuluctoida:
                    return True, thoigianhieuluctoida
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

    def get_diachicosothongtinnhanvattruongnhom(self):
        idnguoichoitruongnhom = self.get_idnguoichoitruongnhom()
        if not idnguoichoitruongnhom:
            return False

        if not self._diachicosothongtinnhanvattruongnhom or not self.get_is_nhanvattontai(self._diachicosothongtinnhanvattruongnhom) or self.get_idnguoichoi(self._diachicosothongtinnhanvattruongnhom) != idnguoichoitruongnhom:
            return False

        return self._diachicosothongtinnhanvattruongnhom


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

    def get_idkynang(self, idvitri_x, idvitri_y):
        """
        :param idvitri_x: Số thứ tự cuốn sách bắt đầu từ 0
        :param idvitri_y: Số thứ tự kỹ năng ở trong cuốn sách ấy bắt đầu từ 0
        """
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang:
            return False

        idvitrikynang = 14 * idvitri_y + idvitri_x #Vì mỗi cuốn nó chỉ có tối đa 12 kỹ năng cho nên nó nhích lên 14 để không bao giờ trùng nhau

        return read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830)

    def get_tenkynang(self, idvitri_x, idvitri_y):
        """
        :param idvitri_x: Số thứ tự cuốn sách bắt đầu từ 0
        :param idvitri_y: Số thứ tự kỹ năng ở trong cuốn sách ấy bắt đầu từ 0
        """
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang:
            return False

        idvitrikynang = 14 * idvitri_y + idvitri_x #Vì mỗi cuốn nó chỉ có tối đa 12 kỹ năng cho nên nó nhích lên 14 để không bao giờ trùng nhau

        return read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830)

    def get_is_kynangsansang(self, idvitri_x, idvitri_y, delay = 0.):
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang:
            return False
        idvitrikynang = 14 * idvitri_y + idvitri_x #Vì mỗi cuốn nó chỉ có tối đa 12 kỹ năng cho nên nó nhích lên 14 để không bao giờ trùng nhau

        idkynang = read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830)
        is_dahockynang = True
        thoigiangiancach = read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6A4C) == 0

        return idkynang and is_dahockynang and thoigiangiancach and time.time() - self._thoidiemsudungkynangvitrigannhat_map.get((idvitri_x, idvitri_y), time.time() - delay - 1.) > delay

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

        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_NAMDUOIDAT:
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

        logger.error("{} set_is_batalt: {}".format(self.get_tendoituong(), is_batalt))

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

    def _get_diachicosothongtinnhanvatmuctieudangchon(self):
        return read_int(self.tientrinh, self.diachixq + 0x1BC3E0)

    def get_thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat(self):
        return self._thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat

    def set_diachicosothongtinnhanvatmuctieudangchon(self, diachicosothongtinnhanvat):
        if self.get_diachicosothongtinnhanvatmuctieudangchon() != diachicosothongtinnhanvat:
            self._thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat = time.time()
            self._diachicosothongtinnhanvatmuctieudangchon = diachicosothongtinnhanvat

            if diachicosothongtinnhanvat:
                iddoituong = self.get_iddoituong(diachicosothongtinnhanvat)
                if iddoituong > 0:
                    write_int(self.tientrinh, self.diachixq + 0x1BC3E0, diachicosothongtinnhanvat)
                    write_int(self.tientrinh, self.diachixq + 0x37173C, iddoituong)
                    write_int(self.tientrinh, self.diachixq + 0x1BC440, diachicosothongtinnhanvat)
                    write_int(self.tientrinh, self.diachixq + 0x1BC444, iddoituong)

                    return

            write_int(self.tientrinh, self.diachixq + 0x1BC3E0, 0)
            write_int(self.tientrinh, self.diachixq + 0x37173C, 0)
            write_int(self.tientrinh, self.diachixq + 0x1BC440, 0)
            write_int(self.tientrinh, self.diachixq + 0x1BC444, 0)

    def action_vohieuhoatuthedelaysautancong(self):
        if read_int(self.tientrinh, self.diachixq + 0x1AF43 + 0x6) != TUTHENHANVAT_DUNGIM:
            write_int(self.tientrinh, self.diachixq + 0x1AF43 + 0x6, TUTHENHANVAT_DUNGIM)
        if read_int(self.tientrinh, self.diachixq + 0x1B2D7 + 0x6) != TUTHENHANVAT_DUNGIM:
            write_int(self.tientrinh, self.diachixq + 0x1B2D7 + 0x6, TUTHENHANVAT_DUNGIM)

    def action_tatvohieuhoatuthedelaysautancong(self):
        if read_int(self.tientrinh, self.diachixq + 0x1AF43 + 0x6) != TUTHENHANVAT_DELAYSAUTANCONG:
            write_int(self.tientrinh, self.diachixq + 0x1AF43 + 0x6, TUTHENHANVAT_DELAYSAUTANCONG)
        if read_int(self.tientrinh, self.diachixq + 0x1B2D7 + 0x6) != TUTHENHANVAT_DELAYSAUTANCONG:
            write_int(self.tientrinh, self.diachixq + 0x1B2D7 + 0x6, TUTHENHANVAT_DELAYSAUTANCONG)

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

    def action_vohieuhoabangthongbaogocduoibenphai(self):
        if read_bytes(self.tientrinh, self.diachixq + 0xCE9FF, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xCE9FF, bytes.fromhex("90 90 90 90 90 90"), 6)

    def action_tatvohieubangthongbaogocduoibenphai(self):
        if read_bytes(self.tientrinh, self.diachixq + 0xCE9FF, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xCE9FF, bytes.fromhex("88 81 50 11 00 00"), 6)

    def action_vohieuhoalongclick(self):
        if read_int(self.tientrinh, self.diachixq + 0x4984C + 0x6) != 0:
            write_int(self.tientrinh, self.diachixq + 0x4984C + 0x6, 0)

    def action_tatvohieuhoalongclick(self):
        if read_int(self.tientrinh, self.diachixq + 0x4984C + 0x6) != 1:
            write_int(self.tientrinh, self.diachixq + 0x4984C + 0x6, 1)

    def action_vohieuhoatrangthaichuotchonmuctieukynang(self):
        if read_int(self.tientrinh, self.diachixq + 0x5405C + 0x6) != 0:
            write_int(self.tientrinh, self.diachixq + 0x5405C + 0x6, 0)

    def action_tatvohieuhoatrangthaichuotchonmuctieukynang(self):
        if read_int(self.tientrinh, self.diachixq + 0x5405C + 0x6) != 2:
            write_int(self.tientrinh, self.diachixq + 0x5405C + 0x6, 2)

    def action_vohieuhoakhoanhvungkynang(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x76148, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x76148, bytes.fromhex("90 90"), 2)

    def action_tatvohieuhoakhoanhvungkynang(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x76148, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x76148, bytes.fromhex("88 01"), 2)

    def action_vohieuhoaphimspace(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x3D8CB + 0x6, 1) != bytes.fromhex("00"):
            write_bytes(self.tientrinh, self.diachixq + 0x3D8CB + 0x6, bytes.fromhex("00"), 1)

    def action_tatvohieuhoaphimspace(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x3D8CB + 0x6, 1) != bytes.fromhex("01"):
            write_bytes(self.tientrinh, self.diachixq + 0x3D8CB + 0x6, bytes.fromhex("01"), 1)

    def get_is_dangmobando(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)
        if not x:
            return False
        return read_boolean(self.tientrinh, x)

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

        logger.error("{} set_is_danghiencuasotuychon: {}".format(self.get_tendoituong(), is_danghiencuasotuychon))

        return write_boolean(self.tientrinh, x + 0x1E38, is_danghiencuasotuychon)

    def get_caulenhmoinhomhientai(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False

        x = read_int(self.tientrinh, x + 0xADFE10)
        if not x:
            return False

        return read_string(self.tientrinh, x + 0x7C).strip()


    def action_thucthicaulenh(self, caulenh, delay = 0.25):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_thucthicaulenh(caulenh)

        return True

    def action_nhatdotoado(self, toadox, toadoy, delay = 0.05):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_nhatdotoado(toadox, toadoy)

        return True

    def action_nhatruong(self, iddoituong, delay = 0.05):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_nhatruong(iddoituong)

        return True

    def action_sudungkynang(self, idkynang, delay = 0.05):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_sudungkynang(idkynang)

        return True

    def action_sudungkynangmuctieunguoichoi(self, idkynang, idnguoichoi, delay = 0.05):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_sudungkynangmuctieunguoichoi(idkynang, idnguoichoi)

        return True

    def action_sudungkynangmuctieukhacnguoichoi(self, idkynang, iddoituong, delay = 0.05):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_sudungkynangmuctieukhacnguoichoi(idkynang, iddoituong)

        return True

    def action_sudungkynangtoado(self, idkynang, toadox, toadoy, delay = 0.05):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_sudungkynangtoado(idkynang, toadox, toadoy)

        return True

    def action_dichuyenvatphamhanhtrang(self, iddoituong, vitri, delay = 0.25):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_dichuyenvatphamhanhtrang(iddoituong, vitri)

        return True

    def action_trieuhoibaothu(self, iddoituong, delay = 0.25):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_trieuhoibaothu(iddoituong)

        return True
    
    def action_sudungkynangbaothu(self, iddoituong, idkynang, delay = 0.25):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_sudungkynangbaothu(iddoituong, idkynang)

        return True

    def action_trochuyenvoinpc(self, iddoituong, noidungtrochuyen, delay = 0.25):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_trochuyenvoinpc(iddoituong, noidungtrochuyen)

        return True

    def action_sudungvatpham(self, iddoituong, delay = 0.25):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_sudungvatpham(iddoituong)

        return True

    def action_sudungvatphambaothu(self, iddoituongvatpham, iddoituongbaothu, delay = 0.25):
        if time.time() - self._thoidiemthucthicaulenhgannhat < delay:
            return False

        self._thoidiemthucthicaulenhgannhat = time.time()

        self.auto_assemble_sudungvatphambaothu(iddoituongvatpham, iddoituongbaothu)

        return True

    def action_moihoacxinvaonhom(self, idnguoichoi, delay = 1.):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return
        if not idnguoichoi:
            return

        self._thoidiemthaotacnhomgannhat = time.time()

        self.auto_assemble_thaotacnhom("+", idnguoichoi)

        return True
    def action_thoatkhoinhom(self, idnguoichoitruongnhom, delay = 1.):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return
        if not idnguoichoitruongnhom:
            return

        self._thoidiemthaotacnhomgannhat = time.time()

        self.auto_assemble_thaotacnhom("x", idnguoichoitruongnhom)

        return True

    def action_kiemtravadongyloimoinhom(self, idnguoichoitruongnhom, delay = 1.):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return
        if not idnguoichoitruongnhom:
            return

        if "team + {}".format(idnguoichoitruongnhom) == self.get_caulenhmoinhomhientai() and self.get_is_danghiencuasoyesno():
            self.auto_assemble_thaotacnhom("+", idnguoichoitruongnhom)
            self._thoidiemthaotacnhomgannhat = time.time()

            if self.get_is_danghiencuasoyesno():
                self.set_is_danghiencuasoyesno(False)

        return True

    def auto_assemble_thucthicaulenh(self, caulenh):
        logger.error("{} auto_assemble_thucthicaulenh: {}".format(self.get_tendoituong(), caulenh))

        if not self._is_dasetupautoassemblethucthicaulenh:
            self._diachiautoassemblethucthicaulenh = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 6, self._diachiautoassemblethucthicaulenh + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblethucthicaulenh + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblethucthicaulenh + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblethucthicaulenh + 19, caulenh)

            self._is_dasetupautoassemblethucthicaulenh = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblethucthicaulenh + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblethucthicaulenh + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblethucthicaulenh + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblethucthicaulenh)
        time.sleep(0.05)

    def auto_assemble_thaotacnhom(self, idhoatdong, idnguoichoi):
        caulenh = "team {} {}".format(idhoatdong, idnguoichoi)
        logger.error("{} auto_assemble_thaotacnhom: {} {} {}".format(self.get_tendoituong(), idhoatdong, idnguoichoi, caulenh))
        if not self._is_dasetupautoassemblethaotacnhom:
            self._diachiautoassemblethaotacnhom = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblethaotacnhom, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethaotacnhom + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblethaotacnhom + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethaotacnhom + 6, self._diachiautoassemblethaotacnhom + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblethaotacnhom + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblethaotacnhom + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblethaotacnhom + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblethaotacnhom + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblethaotacnhom + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblethaotacnhom + 19, caulenh)

            self._is_dasetupautoassemblethaotacnhom = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblethaotacnhom + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblethaotacnhom + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblethaotacnhom + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblethaotacnhom + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblethaotacnhom)
        time.sleep(0.05)

    def auto_assemble_sudungkynang(self, idkynang):
        caulenh = "pf {}".format(idkynang)
        logger.error("{} auto_assemble_sudungkynang: {} {}".format(self.get_tendoituong(), idkynang, caulenh))
        if not self._is_dasetupautoassemblesudungkynang:
            self._diachiautoassemblesudungkynang = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynang, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynang + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynang + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynang + 6, self._diachiautoassemblesudungkynang + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynang + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynang + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblesudungkynang + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynang + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynang + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblesudungkynang + 19, caulenh)

            self._is_dasetupautoassemblesudungkynang = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblesudungkynang + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblesudungkynang + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblesudungkynang + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblesudungkynang + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblesudungkynang)
        time.sleep(0.05)

    def auto_assemble_sudungkynangmuctieunguoichoi(self, idkynang, idnguoichoi):
        caulenh = "pf {} {}".format(idkynang, idnguoichoi)
        logger.error("{} auto_assemble_sudungkynangmuctieunguoichoi: {} {} {}".format(self.get_tendoituong(), idkynang, idnguoichoi, caulenh))
        if not self._is_dasetupautoassemblesudungkynangmuctieunguoichoi:
            self._diachiautoassemblesudungkynangmuctieunguoichoi = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 6, self._diachiautoassemblesudungkynangmuctieunguoichoi + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblesudungkynangmuctieunguoichoi + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 19, caulenh)

            self._is_dasetupautoassemblesudungkynangmuctieunguoichoi = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblesudungkynangmuctieunguoichoi + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblesudungkynangmuctieunguoichoi)
        time.sleep(0.05)

    def auto_assemble_sudungkynangmuctieukhacnguoichoi(self, idkynang, iddoituong):
        caulenh = "pf {} {}#".format(idkynang, hex(iddoituong)).replace("0x", "")
        logger.error("{} auto_assemble_sudungkynangmuctieukhacnguoichoi: {} {} {}".format(self.get_tendoituong(), idkynang, iddoituong, caulenh))
        if not self._is_dasetupautoassemblesudungkynangmuctieukhacnguoichoi:
            self._diachiautoassemblesudungkynangmuctieukhacnguoichoi = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 6, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 19, caulenh)

            self._is_dasetupautoassemblesudungkynangmuctieukhacnguoichoi = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblesudungkynangmuctieukhacnguoichoi + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblesudungkynangmuctieukhacnguoichoi)
        time.sleep(0.05)

    def auto_assemble_sudungkynangtoado(self, idkynang, toadox, toadoy):
        caulenh = "pf {} {},{}".format(idkynang, toadox, toadoy).replace("0x", "")
        logger.error("{} auto_assemble_sudungkynangtoado: {} {} {} {}".format(self.get_tendoituong(), idkynang, toadox, toadoy, caulenh))
        if not self._is_dasetupautoassemblesudungkynangtoado:
            self._diachiautoassemblesudungkynangtoado = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangtoado, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 6, self._diachiautoassemblesudungkynangtoado + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblesudungkynangtoado + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 19, caulenh)

            self._is_dasetupautoassemblesudungkynangtoado = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblesudungkynangtoado + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblesudungkynangtoado)
        time.sleep(0.05)

    def auto_assemble_trochuyenvoinpc(self, iddoituong, noidungtrochuyen, caulenhtrochuyen = "talk"):
        caulenh = "{} {}# {}".format(caulenhtrochuyen, hex(iddoituong), noidungtrochuyen).replace("0x", "")
        logger.error("{} auto_assemble_trochuyenvoinpc: {} {} {}".format(self.get_tendoituong(), iddoituong, noidungtrochuyen, caulenh))
        if not self._is_dasetupautoassembletrochuyenvoinpc:
            self._diachiautoassembletrochuyenvoinpc = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassembletrochuyenvoinpc, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 6, self._diachiautoassembletrochuyenvoinpc + 19)

            write_bytes(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 11, self.diachixq + 0x951C0 - (self._diachiautoassembletrochuyenvoinpc + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 19, caulenh)

            self._is_dasetupautoassembletrochuyenvoinpc = True
        else:
            if read_int(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassembletrochuyenvoinpc + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassembletrochuyenvoinpc)
        time.sleep(0.05)

    def auto_assemble_dichuyenvatphamhanhtrang(self, iddoituong, vitri):
        caulenh = "move {}# {}".format(hex(iddoituong), vitri).replace("0x", "")
        logger.error("{} auto_assemble_dichuyenvatphamhanhtrang: {} {}".format(self.get_tendoituong(), iddoituong, vitri, caulenh))
        if not self._is_dasetupautoassembledichuyenvatphamhanhtrang:
            self._diachiautoassembledichuyenvatphamhanhtrang = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 6, self._diachiautoassembledichuyenvatphamhanhtrang + 19)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 11, self.diachixq + 0x951C0 - (self._diachiautoassembledichuyenvatphamhanhtrang + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 19, caulenh)

            self._is_dasetupautoassembledichuyenvatphamhanhtrang = True
        else:
            if read_int(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassembledichuyenvatphamhanhtrang + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassembledichuyenvatphamhanhtrang)
        time.sleep(0.05)

    def auto_assemble_sudungvatpham(self, iddoituong):
        caulenh = "use {}#".format(hex(iddoituong)).replace("0x", "")
        logger.error("{} auto_assemble_sudungvatpham: {} {}".format(self.get_tendoituong(), iddoituong, caulenh))
        if not self._is_dasetupautoassemblesudungvatpham:
            self._diachiautoassemblesudungvatpham = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatpham, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungvatpham + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatpham + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungvatpham + 6, self._diachiautoassemblesudungvatpham + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatpham + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungvatpham + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblesudungvatpham + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatpham + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatpham + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblesudungvatpham + 19, caulenh)

            self._is_dasetupautoassemblesudungvatpham = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblesudungvatpham + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblesudungvatpham + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblesudungvatpham + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblesudungvatpham + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblesudungvatpham)
        time.sleep(0.05)

    def auto_assemble_sudungvatphambaothu(self, iddoituongvatpham, iddoituongpet):
        caulenh = "use {}# pet {}#".format(hex(iddoituongvatpham), hex(iddoituongpet)).replace("0x", "")
        logger.error("{} auto_assemble_sudungvatphambaothu: {} {} {}".format(self.get_tendoituong(), iddoituongvatpham, iddoituongpet, caulenh))
        if not self._is_dasetupautoassemblesudungvatphambaothu:
            self._diachiautoassemblesudungvatphambaothu = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatphambaothu, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 6, self._diachiautoassemblesudungvatphambaothu + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblesudungvatphambaothu + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 19, caulenh)

            self._is_dasetupautoassemblesudungvatphambaothu = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblesudungvatphambaothu + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblesudungvatphambaothu)
        time.sleep(0.05)

    def auto_assemble_nhatruong(self, iddoituong):
        caulenh = "look {}#".format(hex(iddoituong)).replace("0x", "")
        logger.error("{} auto_assemble_nhatruong: {} {}".format(self.get_tendoituong(), iddoituong, caulenh))
        if not self._is_dasetupautoassemblenhatruong:
            self._diachiautoassemblenhatruong = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatruong, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatruong + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblenhatruong + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatruong + 6, self._diachiautoassemblenhatruong + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatruong + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatruong + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblenhatruong + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatruong + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatruong + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblenhatruong + 19, caulenh)

            self._is_dasetupautoassemblenhatruong = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblenhatruong + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblenhatruong + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblenhatruong + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblenhatruong + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblenhatruong)
        time.sleep(0.05)

    def auto_assemble_nhatdotoado(self, toadox, toadoy):
        caulenh = "get {} {}".format(toadox, toadoy)
        logger.error("{} auto_assemble_nhatdotoado: {} {} {}".format(self.get_tendoituong(), toadox, toadoy, caulenh))
        if not self._is_dasetupautoassemblenhatdotoado:
            self._diachiautoassemblenhatdotoado = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatdotoado, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatdotoado + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblenhatdotoado + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatdotoado + 6, self._diachiautoassemblenhatdotoado + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatdotoado + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatdotoado + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblenhatdotoado + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblenhatdotoado + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatdotoado + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblenhatdotoado + 19, caulenh)

            self._is_dasetupautoassemblenhatdotoado = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblenhatdotoado + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblenhatdotoado + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblenhatdotoado + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblenhatdotoado + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblenhatdotoado)
        time.sleep(0.05)

    def auto_assemble_trieuhoibaothu(self, iddoituong):
        caulenh = "pet {}# show".format(hex(iddoituong)).replace("0x", "")
        logger.error("{} auto_assemble_trieuhoibaothu: {} {}".format(self.get_tendoituong(), iddoituong, caulenh))
        if not self._is_dasetupautoassembletrieuhoibaothu:
            self._diachiautoassembletrieuhoibaothu = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassembletrieuhoibaothu, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 6, self._diachiautoassembletrieuhoibaothu + 19)

            write_bytes(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 11, self.diachixq + 0x951C0 - (self._diachiautoassembletrieuhoibaothu + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 19, caulenh)

            self._is_dasetupautoassembletrieuhoibaothu = True
        else:
            if read_int(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassembletrieuhoibaothu + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassembletrieuhoibaothu)
        time.sleep(0.05)


    def auto_assemble_sudungkynangbaothu(self, iddoituong, idkynang):
        caulenh = "pet {}# {}".format(hex(iddoituong), idkynang).replace("0x", "")
        logger.error("{} auto_assemble_sudungkynangbaothu: {} {} {}".format(self.get_tendoituong(), iddoituong, idkynang, caulenh))
        if not self._is_dasetupautoassemblesudungkynangbaothu:
            self._diachiautoassemblesudungkynangbaothu = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangbaothu, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 1, len(caulenh))

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 6, self._diachiautoassemblesudungkynangbaothu + 19)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 11, self.diachixq + 0x951C0 - (self._diachiautoassemblesudungkynangbaothu + 10) - 5)

            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 19, caulenh)

            self._is_dasetupautoassemblesudungkynangbaothu = True
        else:
            if read_int(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 1) != len(caulenh):
                write_int(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 1, len(caulenh))
            if read_string(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 19) != caulenh:
                write_string(self.tientrinh, self._diachiautoassemblesudungkynangbaothu + 19, caulenh)

        self.tientrinh.start_thread(self._diachiautoassemblesudungkynangbaothu)
        time.sleep(0.05)

    def auto_assemble_sudungkynangphimtat(self, idvitriphimtat):
        logger.error("{} auto_assemble_sudungkynangphimtat: {}".format(self.get_tendoituong(), idvitriphimtat))
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
        time.sleep(0.05)

    def auto_assemble_dichuyen(self, x, y):
        logger.error("{} auto_assemble_dichuyen: {} {}".format(self.get_tendoituong(), x, y))
        if not self._is_dasetupautoassembledichuyen:
            self._diachiautoassembledichuyen = self.tientrinh.allocate(64)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen, bytes.fromhex("8B 3D"), 2)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 2, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 6, bytes.fromhex("8D 77 14"), 3)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 9, bytes.fromhex("BB"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 10, y)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 14, bytes.fromhex("BD"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 15, x)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 19, bytes.fromhex("6A 00"), 2)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 21, bytes.fromhex("53"), 1)
            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 22, bytes.fromhex("55"), 1)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 23, bytes.fromhex("8B CF"), 2)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 25, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 26, self.diachixq + 0x476A0 - (self._diachiautoassembledichuyen + 25) - 5)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 30, bytes.fromhex("C3"), 1)
            self._is_dasetupautoassembledichuyen = True
        else:
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 10, y)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 15, x)

        self.tientrinh.start_thread(self._diachiautoassembledichuyen)
        time.sleep(0.05)

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
        logger.error("{} auto_assemble_khoitaothongtinbando".format(self.get_tendoituong()))
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
        time.sleep(0.05)

    def auto_assemble_tudongtimduong(self, x, y, idbando):
        if x <= 0 or y <= 0 or idbando <= 0:
            return

        logger.error("{} auto_assemble_tudongtimduong: {} {} {}".format(self.get_tendoituong(), x, y, idbando))
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
        time.sleep(0.05)

    def action_nhatdo(self, diachicosothongtinvatpham, delay = 0.05):
        if time.time() - self._thoidiemnhatdogannhat < delay:
            return

        if time.time() - self._thoidiemnhatdogannhat_map.get(diachicosothongtinvatpham, time.time() - 2.) < 1.:
            return

        x = self.get_toadox(diachicosothongtinvatpham, is_vitrihientai = True)
        y = self.get_toadoy(diachicosothongtinvatpham, is_vitrihientai = True)

        if x <= 0 or y <= 0:
            return

        self._thoidiemnhatdogannhat = time.time()
        self._thoidiemnhatdogannhat_map[diachicosothongtinvatpham] = time.time()

        self.action_nhatdotoado(x, y, delay = delay)

        return True

    def action_nhatdoxungquanh(self, delay = 0.05):
        if time.time() - self._thoidiemnhatdogannhat < delay:
            return

        self._thoidiemnhatdogannhat = time.time()
        self.auto_assemble_nhatdo()

        return True

    def action_battheosaunhom(self, delay = 1.):
        if time.time() - self._thoidiembattattheosaunhomgannhat < delay:
            return

        idnguoichoitruongnhom = self.get_idnguoichoitruongnhom()
        if not idnguoichoitruongnhom:
            return

        is_ok = self.action_thucthicaulenh("team follow {}".format(idnguoichoitruongnhom))

        if is_ok:
            self._thoidiembattattheosaunhomgannhat = time.time()

        return is_ok
    
    def action_sudungkynangphimtat(self, idvitriphimtat, delay = 0.25):
        # if time.time() - self._thoidiemsudungkynanggannhat < 0.125:
        #     return

        if idvitriphimtat in self._thoidiemsudungkynangphimtatgannhat_map and time.time() - self._thoidiemsudungkynangphimtatgannhat_map[idvitriphimtat] < delay:
            return

        self._thoidiemsudungkynanggannhat = time.time()
        self._thoidiemsudungkynangphimtatgannhat_map[idvitriphimtat] = time.time()
        self.auto_assemble_sudungkynangphimtat(idvitriphimtat)

        return True

    def get_thoidiemsudungkynangvitrigannhat(self, idvitri_x, idvitri_y, macdinh = None):
        return self._thoidiemsudungkynangvitrigannhat_map.get((idvitri_x, idvitri_y), macdinh)

    def action_sudungkynangvitrimuctieu(self, idvitri_x, idvitri_y, diachicosothongtinnhanvatmuctieu = False, is_khongkiemtracothetancong = False, delay = 0.25):
        # if time.time() - self._thoidiemsudungkynanggannhat < 0.125:
        #     return

        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return

        diachicosothongtinnhanvatmuctieudangchon = diachicosothongtinnhanvatmuctieu if diachicosothongtinnhanvatmuctieu else self.get_diachicosothongtinnhanvatmuctieudangchon()

        if not diachicosothongtinnhanvatmuctieudangchon or (not is_khongkiemtracothetancong and not self.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)):
            return

        is_ok = False

        if self.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon):
            idnguoichoi = self.get_idnguoichoi(diachicosothongtinnhanvatmuctieudangchon)
            is_ok = self.action_sudungkynangmuctieunguoichoi(idkynang, idnguoichoi)
        else:
            iddoituong = self.get_iddoituongmuctieudangchon()
            if iddoituong:
                is_ok = self.action_sudungkynangmuctieukhacnguoichoi(idkynang, iddoituong)

        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()

        return is_ok

    def action_sudungkynangvitri(self, idvitri_x, idvitri_y, delay = 0.25):
        # if time.time() - self._thoidiemsudungkynanggannhat < 0.125:
        #     return
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return

        is_ok = self.action_sudungkynang(idkynang)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()

        return is_ok

    def action_sudungkynangvitrilenbanthan(self, idvitri_x, idvitri_y, delay = 0.25):
        # if time.time() - self._thoidiemsudungkynanggannhat < 0.125:
        #     return
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return

        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return

        is_ok = self.action_sudungkynangmuctieunguoichoi(idkynang, self.get_idnguoichoi())
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()

        return is_ok

    def action_dichuyen(self, x, y, delay = 0.5, is_rangbuoctrongmanhinh = False):
        if self._is_vohieuhoadichuyen:
            return

        if time.time() - self._thoidiemdichuyengannhat < delay:
            return

        if is_rangbuoctrongmanhinh:
            x = max(min(x, self._xmax - 25), 25)
            y = max(min(y, self._ymax - 25), 25)

        self._thoidiemdichuyengannhat = time.time()
        self.auto_assemble_dichuyen(x, y)

        return True

    def action_dichuyengiukhoangcachtoithieu(self, diachicosothongtinnhanvat2, khoangcachtoithieu, khoangcachdichuyentoida = 0, delay = 0.5):
        if not diachicosothongtinnhanvat2:
            return

        if not self.get_iddoituong(diachicosothongtinnhanvat2):
            return

        return self.action_dichuyengiukhoangcachtoithieudiem(self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2), khoangcachtoithieu = khoangcachtoithieu, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyengiukhoangcachtoida(self, diachicosothongtinnhanvat2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.5):
        if not diachicosothongtinnhanvat2:
            return

        if not self.get_iddoituong(diachicosothongtinnhanvat2):
            return

        return self.action_dichuyengiukhoangcachtoidadiem(self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2), khoangcachtoida = khoangcachtoida, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyenphudau(self, diachicosothongtinnhanvat2, khoangcachphudau = 1, delay = 0.5):
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

        xmax = self._xmax
        ymax = self._ymax

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = round(self._centerx + deltax * toadomoidonvikhoangcachx)
        yclick = round(self._centery + deltay * toadomoidonvikhoangcachy)

        return self.action_dichuyen(xclick, yclick, delay = delay)

    def action_dichuyengiukhoangcachtoidadiem(self, x2, y2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.5, is_rangbuoctrongmanhinh = False):
        if x2 <= 0 or y2 <= 0:
            return

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

        xmax = self._xmax
        ymax = self._ymax

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = int(self._centerx + deltax * toadomoidonvikhoangcachx)
        yclick = int(self._centery + deltay * toadomoidonvikhoangcachy)

        return self.action_dichuyen(xclick, yclick, delay = delay, is_rangbuoctrongmanhinh = is_rangbuoctrongmanhinh)

    def action_dichuyengiukhoangcachtoithieudiem(self, x2, y2, khoangcachtoithieu, khoangcachdichuyentoida = 0, delay = 0.5):
        if x2 <= 0 or y2 <= 0:
            return
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

        xmax = self._xmax
        ymax = self._ymax

        toadomoidonvikhoangcachx = xmax / KHOANGCACHTOANMANHINH
        toadomoidonvikhoangcachy = ymax / KHOANGCACHTOANMANHINH

        xclick = int(self._centerx + deltax * toadomoidonvikhoangcachx)
        yclick = int(self._centery + deltay * toadomoidonvikhoangcachy)

        return self.action_dichuyen(xclick, yclick, delay = delay)

    def action_dichuyentaicho(self, delay = 0.5):
        return self.action_dichuyen(self._centerx, self._centery, delay = delay)

    def action_dichuyentiepcan(self, diachicosothongtinnhanvat2, khoangcachdichuyentoida = 0, delay = 0.5):
        return self.action_dichuyengiukhoangcachtoida(diachicosothongtinnhanvat2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyentiepcandiem(self, x2, y2, khoangcachdichuyentoida = 0, delay = 0.5, is_rangbuoctrongmanhinh = False):
        if x2 <= 0 or y2 <= 0:
            return
        return self.action_dichuyengiukhoangcachtoidadiem(x2, y2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay, is_rangbuoctrongmanhinh = is_rangbuoctrongmanhinh)

    def action_sudungkynangvitriphudau(self, idvitri_x, idvitri_y, diachicosothongtinnhanvat2, khoangcachphudau, delay = 0.5):
        # if time.time() - self._thoidiemsudungkynanggannhat < 0.125:
        #     return
        if not diachicosothongtinnhanvat2:
            return False
        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat2):
            return False
        return self.action_sudungkynangvitriphudaudiem(idvitri_x, idvitri_y, self.get_toadox(diachicosothongtinnhanvat2), self.get_toadoy(diachicosothongtinnhanvat2), khoangcachphudau = khoangcachphudau, delay = delay)

    def action_sudungkynangvitriphudaudiem(self, idvitri_x, idvitri_y, x2, y2, khoangcachphudau, delay = 0.5):
        # if time.time() - self._thoidiemsudungkynanggannhat < 0.125:
        #     return
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return False

        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return False

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

        is_ok = self.action_sudungkynangtoado(idkynang, targetx, targety)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()

        return is_ok

    def get_is_damocuasotuychonnhanvatchinhlandau(self):
        x = read_int(self.tientrinh, self.diachixq + 0x3A531C)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0x2C)
        if x <= 10:
            return False

        return True

    def get_is_dathietlapkynangphimtat(self, idvitriphimtat):
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

    def action_khoitaothongtinbando(self, delay = 1.):
        if time.time() - self._thoidiemkhoitaothongtinbandogannhat < delay:
            return

        if self.get_is_dakhoitaothongtinbando():
            return

        self._thoidiemkhoitaothongtinbandogannhat = time.time()
        self.auto_assemble_khoitaothongtinbando()

        return True
    def action_tudongtimduong(self, x, y, idbando, delay = 1.):
        return

        if time.time() - self._thoidiemdichuyengannhat < delay:
            return

        if not self.get_is_dakhoitaothongtinbando():
            time.sleep(0.5)
            self.action_khoitaothongtinbando()
            return

        self._thoidiemdichuyengannhat = time.time()
        self.auto_assemble_tudongtimduong(x, y, idbando)

    def action_phucsinh(self, is_duoccuu = False, delay = 1.):
        if time.time() - self._thoidiemphucsinhgannhat < delay:
            return

        if not self.get_is_nhanvatdachet():
            return

        if is_duoccuu:
            is_ok = self.action_thucthicaulenh("desc revive$")

        else:
            is_ok = self.action_thucthicaulenh("desc revive")

        if is_ok:
            self._thoidiemphucsinhgannhat = time.time()
            if self.get_is_danghiencuasotuychon():
                self.set_is_danghiencuasotuychon(False)

        return is_ok

    def action_doimaupk(self, idmaupk, delay = 1.):
        if time.time() - self._thoidiemmaupkgannhat < delay:
            return

        if self.get_idmaupk() == idmaupk:
            return

        is_ok = self.action_thucthicaulenh("set !attack {}".format(idmaupk), delay = delay)
        if is_ok:
            self.set_idmaupk(idmaupk)
            self._thoidiemmaupkgannhat = time.time()

        return is_ok

    def action_timkiemvatphamhanhtrang(self, tenvatpham = None):
        if not tenvatpham:
            return False

        i = -1

        while True:
            if i >= SOLUONGVATPHAMHANHTRANGTOIDA:
                break

            i += 1

            if tenvatpham:
                tenvatphamxemxet = self.get_tenvatphamhanhtrang(i)
                if tenvatphamxemxet != tenvatpham:
                    continue

            return self.get_iddoituongvatphamhanhtrang(i)

        return False

    def get_danhsachvatphamhanhtrang_map(self):
        i = -1
        vatphamhanhtrang_map = {}
        while True:
            if i >= SOLUONGVATPHAMHANHTRANGTOIDA:
                break

            i += 1

            tenvatphamxemxet = self.get_tenvatphamhanhtrang(i)

            if tenvatphamxemxet not in vatphamhanhtrang_map:
                vatphamhanhtrang_map[tenvatphamxemxet] = []

            vatphamhanhtrang_map[tenvatphamxemxet].append(
                (i, self.get_iddoituongvatphamhanhtrang(i)),
            )

        return vatphamhanhtrang_map

    def action_timkiemnhanvat(self, tennhanvat = None, idnguoichoi = None, iddoituong = None, tennhanvatchua = None):
        if not tennhanvat and not idnguoichoi and not iddoituong and not tennhanvatchua:
            return False

        i = 0

        while True:
            diachicosothongtinnhanvatxemxet = self.get_diachicosothongtindoituongx(i)
            if not diachicosothongtinnhanvatxemxet:
                break
            i += 1

            if not self.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                continue

            if tennhanvat:
                tennhanvatxemxet = self.get_tendoituong(diachicosothongtinnhanvatxemxet)

                if tennhanvatxemxet != tennhanvat:
                    continue

            if idnguoichoi:
                idnguoichoixemxet = self.get_idnguoichoi(diachicosothongtinnhanvatxemxet)

                if idnguoichoixemxet != idnguoichoi:
                    continue

            if iddoituong:
                iddoituongxemxet = self.get_iddoituong(diachicosothongtinnhanvatxemxet)

                if iddoituongxemxet != iddoituong:
                    continue

            if tennhanvatchua:
                tennhanvatxemxet = self.get_tendoituong(diachicosothongtinnhanvatxemxet)
                if tennhanvatxemxet or tennhanvatchua not in tennhanvatxemxet:
                    continue

            return diachicosothongtinnhanvatxemxet

        return False

    def action_suado(self, diachicosonhanvatthosuado, delay = 1.):
        if time.time() - self._thoidiemsuadogannhat < delay:
            return

        idthosuado = self.get_iddoituong(diachicosonhanvatthosuado)
        if not idthosuado:
            return

        is_ok = self.action_thucthicaulenh("repair ! {}# all".format(hex(idthosuado).replace("0x", "")))
        if is_ok:
            self._thoidiemsuadogannhat = time.time()
        return is_ok

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

        caulenh = "auto 5 1"

        is_ok = self.action_thucthicaulenh(caulenh, delay = delay)
        if is_ok:
            self._thoidiemsudungchucnangmorong5 = time.time()
        return is_ok

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

    def get_is_daketthucchientruong(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFE9C)
        if not x:
            return False
        return read_boolean(self.tientrinh, x + 0x34)

    def set_is_daketthucchientruong(self, is_daketthucchientruong):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return
        x = read_int(self.tientrinh, x + 0xADFE9C)
        if not x:
            return
        return write_boolean(self.tientrinh, x + 0x34, is_daketthucchientruong)

    def get_iddoituongbaothudautien(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDDC)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x47C)

    def get_is_datrieuhoibaothu(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDDC)
        if not x:
            return False
        return read_boolean(self.tientrinh, x + 0x1AE8)

    def get_is_dayhanhtrang(self):
        i = -1
        while True:
            if i >= SOLUONGVATPHAMHANHTRANGTOIDA:
                break

            i += 1

            iddoituongvatpham = self.get_iddoituongvatphamhanhtrang(i)
            if not iddoituongvatpham:
                return False

        return True

    def get_tenmonphai(self):
        return MONPHAI_MAP.get(self.get_idkynang(0, 0))