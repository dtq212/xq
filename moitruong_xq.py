import queue
from dataclasses import dataclass, field

import pymem
from keystone import Ks, KS_ARCH_X86, KS_MODE_32

from hangso_xq import *
from tienich_xq import *

OFFSET_DIACHICOSOTHONGTINGAME = 0x380B44
OFFSET_DIACHICOSOTHONGTINNHANVAT1 = 0x380AF8
OFFSET_DIACHICOSOHIEUUNGNHANVAT = 0x1638
OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT = 0x13C
OFFSET_DIACHICOSOMOIKYNANG = 0x224
OFFSET_DIACHICOSOTHONGTINNHANVATX = 0x1BDA60

DOUUTIEN_KHANCAP = 1  # Dành cho bơm máu, giải hiệu ứng, cứu sinh
DOUUTIEN_CAO = 3  # Dành cho kỹ năng tấn công, PK
DOUUTIEN_TRUNGBINH = 5  # Dành cho di chuyển, buff cơ bản, gọi pet
DOUUTIEN_THAP = 10  # Dành cho nhặt đồ, gom rác, nói chuyện NPC


@dataclass(order = True)
class LenhThucThi:
    douutien: int
    thoigiantao: float
    caulenh: str = field(compare = False)
    trihoansaulenh: float = field(compare = False)


class MoiTruong:
    def __init__(self, idcuaso):
        self._is_dasetupautoassemblethucthicaulenh2 = False
        self._thoidiemthucthicaulenh2gannhat = 0.
        self.diachihamthucthicaulenh2 = 0
        self.thoidiembatchucnangmoronggannhat = 0.
        self.thoidiemtatchucnangmoronggannhat = 0.
        self.thoidiemcochucnangmoronggannhat = 0.
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
        self.gamemodule = xqmodule

        kichthuoccuaso = win32gui.GetWindowRect(self.idcuaso)
        if not kichthuoccuaso:
            raise Exception("Lấy kích thước cửa sổ game không thành công")

        self._kichthuoccuasogame = 800, 600
        self._xmax, self._ymax = 800, 600
        self._centerx, self._centery = 430, 300

        self._is_dasetupautoassembledichuyen = False
        self._is_dasetupautoassemblenhatvatpham = False
        self._is_dasetupautoassemblekhoitaothongtinbando = False
        self._is_dasetupactionthietlaphooknoidungtrochuyen = False

        self._thoidiembattattheosaunhomgannhat = 0.
        self._thoidiemdichuyengannhat = 0.
        self._thoidiemsudungkynangvitrigannhat_map = {}
        self._thoidiemsudungkynanggannhat = 0.
        self._thoidiemnhatvatphamgannhat = 0.
        self._thoidiemnhatvatphamgannhat_map = {}
        self._thoidiemthucthicaulenhgannhat = 0.
        self._thoidiemsudungtancongvatlygannhat = 0.
        self._thoidiemthaotacnhomgannhat = 0.
        self._thoidiemphucsinhgannhat = 0.
        self._thoidiemmaupkgannhat = 0.
        self._thoidiemsuavatphamgannhat = 0.
        self._thoidiemsudungchucnangmorong5 = 0.
        self._thoidiemtuthenhanvatdungimgannhat = 0.
        self._thoidiemtuthenhanvattanconggannhat = 0.
        self._thoidiemtuthenhanvatdungimcomuctieugannhat = 0.
        self._thoidiemtuthenhanvatkhongdichuyengannhat = 0.
        self._thoidiemralenhbaothutancong = 0.
        self._thoidiemralenhbaothutheosau = 0.
        self._thoidiemralenhbaothudungim = 0.

        self._idthucuoi = False
        self._thoidiemkhongcuoithugannhat = 0.
        self._is_tamngungtancong = False
        self._is_vohieuhoadichuyen = False
        self._thoidiemkhongcomuctieugannhat = 0.

        self._soluonghieuungnhanvattruocdo_map = {}
        self._thoidiemsoluonghieuungbangkhonggannhat_map = {}
        self._thoidiemmuctieubichoanggannhat_map = {}

        self._diachicosothongtinnhanvatmuctieudangchon = False
        self._thoidiemthaydoibandogannhat = 0.
        self._idbandohientai = False
        self._thoidiemcohieuungtienthanvodichgannhat = 0.
        self._thoidiemcohieuunglactuyetvongan = 0.
        self._thoidiemcohieuungkimcuongbathoaidongannhat = 0.
        self._thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat = 0.
        self._diachicosothongtinnhanvattruongnhom = False
        self._idnguoichoi = False
        self._xdichuyengannhat = -1
        self._ydichuyengannhat = -1
        self._thoidiemboquadichuyencungtoadogannhat = 0.
        self._thoidiemnhanvatkhongsansanggannhat = 0.

        self._thoidiemsudungkynangmuctieugannhat = 0.
        self._thoidiemthietlapchedobaothugannhat = 0.
        self._thoidiemsudungthaotacbaothugannhat = 0.
        self._thoidiemtrieuhoibaothugannhat = 0.
        self._thoidiemsudungvatphambaothugannhat = 0.
        self._thoidiemsudungvatphamgannhat = 0.
        self._thoidiemtrochuyenvoinpcgannhat = 0.
        self._thoidiemkhaikhoanggannhat = 0.
        self._thoidiemdichuyenvatphamhanhtranggannhat = 0.
        self._thoidiemdichuyenvatphamsanghanhtrangkhacgannhat = 0.
        self._thoidiemsudungkynangtoadogannhat = 0.
        self._thoidiemnhatvatphamtoadogannhat = 0.

        self._is_nhanvatbichoang = False

        self.diachihamthucthicaulenh = 0

        self.hangdoicaulenh = queue.PriorityQueue()
        self.caulenhdangchos = set()

        self.thoidiemmuctieuanthangannhat_map = {}
        self.thoidiemmuctieuxuathiengannhat_map = {}

        self.thoidiembaothuxuathiengannhat_map = {}

        self._lichsutrochuyen5s = []
        self._noidungtrochuyencu = ""

        self._diachiautoassemblenhatvatpham = False
        self._diachiautoassemblekhoitaothongtinbando = False

        self._diachibodemnoidungtrochuyen = False
        self._diachihamkichbannoidungtrochuyen = False
        self._diachiautoassembledichuyen = False

    def __del__(self):
        def safe_free_old(flag_name, addr_name):
            try:
                if getattr(self, flag_name, False):
                    addr_ = getattr(self, addr_name, None)
                    if addr_ and hasattr(self, "tientrinh"):
                        self.tientrinh.free(addr_)
            except:
                pass

        if getattr(self, "_is_dasetupactionthietlaphooknoidungtrochuyen", False):
            safe_free_old("_is_dasetupactionthietlaphooknoidungtrochuyen", "_diachibodemnoidungtrochuyen")
            safe_free_old("_is_dasetupactionthietlaphooknoidungtrochuyen", "_diachihamkichbannoidungtrochuyen")

        mem_map = [
            ("_is_dasetupautoassembledichuyen", "_diachiautoassembledichuyen"),
            ("_is_dasetupautoassemblekhoitaothongtinbando", "_diachiautoassemblekhoitaothongtinbando"),
            ("_is_dasetupautoassemblenhatvatpham", "_diachiautoassemblenhatvatpham")
        ]

        for flag, addr in mem_map:
            safe_free_old(flag, addr)

        def safe_free(diachi):
            try:
                if diachi and hasattr(self, "tientrinh"):
                    self.tientrinh.free(diachi)
            except:
                pass

        if self.diachihamthucthicaulenh:
            safe_free(self.diachihamthucthicaulenh)

    def _ghilenhvaobonho(self, lenh):
        if not self.diachihamthucthicaulenh:
            self.khoitaohamthucthicaulenh()

        if self.diachihamthucthicaulenh:
            diachidulieu = self.diachihamthucthicaulenh + 0x40
            chuoi_bytes = lenh.caulenh.encode("utf-8")

            write_int(self.tientrinh, diachidulieu, len(chuoi_bytes))
            write_bytes(self.tientrinh, diachidulieu + 4, chuoi_bytes + b"\x00", len(chuoi_bytes) + 1)

            self.tientrinh.start_thread(self.diachihamthucthicaulenh)
            if lenh.trihoansaulenh > 0.:
                time.sleep(lenh.trihoansaulenh)

    def khoitaohamthucthicaulenh(self):
        if self.diachihamthucthicaulenh:
            return

        aob = "51 52 E8 ?? ?? ?? ?? 8B 86 ?? ?? ?? ?? 83 C4 08 89 86 ?? ?? ?? ?? 5F 5E 5D 5B"
        scan_diachi = pymem.pattern.pattern_scan_module(
            self.tientrinh.process_handle,
            self.gamemodule,
            taopatterntuaob(aob)
        )

        if not scan_diachi:
            print("[LỖI] Không tìm thấy Pattern hàm thực thi câu lệnh!")
            return

        diachi_lenh_call = scan_diachi + 2
        khoang_cach_call = read_int(self.tientrinh, diachi_lenh_call + 1)
        diachi_ham = diachi_lenh_call + 5 + khoang_cach_call

        self.diachihamthucthicaulenh = self.tientrinh.allocate(256)
        diachidulieu = self.diachihamthucthicaulenh + 0x40

        ks = Ks(KS_ARCH_X86, KS_MODE_32)
        asm_code = f"""
            mov eax, dword ptr [{hex(diachidulieu)}]
            push eax
            push {hex(diachidulieu + 4)}
            mov eax, {hex(diachi_ham)}
            call eax
            add esp, 8
            ret
        """

        encoding, _ = ks.asm(asm_code)
        write_bytes(self.tientrinh, self.diachihamthucthicaulenh, bytes(encoding), len(encoding))

    def action_thucthicaulenh(self, caulenh, douutien = DOUUTIEN_TRUNGBINH):
        if caulenh in self.caulenhdangchos:
            return False

        self.caulenhdangchos.add(caulenh)

        lenhthucthi = LenhThucThi(
            douutien = douutien,
            thoigiantao = time.time(),
            caulenh = caulenh,
            trihoansaulenh = 0.00,
        )
        self.hangdoicaulenh.put(lenhthucthi)
        self._thoidiemthucthicaulenhgannhat = time.time()
        return True

    def action_thucthicaulenh2(self, caulenh, delay = 0.05):
        if time.time() - self._thoidiemthucthicaulenh2gannhat < delay:
            return False
        self._thoidiemthucthicaulenh2gannhat = time.time()

        diachihampheduyetcaulenh = self.diachixq + 0x95468
        if read_bytes(self.tientrinh, diachihampheduyetcaulenh, 1) == b"\x74":
            write_bytes(self.tientrinh, diachihampheduyetcaulenh, b"\xEB", 1)

        if not self._is_dasetupautoassemblethucthicaulenh2:
            self.diachihamthucthicaulenh2 = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self.diachihamthucthicaulenh2, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self.diachihamthucthicaulenh2 + 1, len(caulenh.encode("utf-8")))

            write_bytes(self.tientrinh, self.diachihamthucthicaulenh2 + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self.diachihamthucthicaulenh2 + 6, self.diachihamthucthicaulenh2 + 19)

            write_bytes(self.tientrinh, self.diachihamthucthicaulenh2 + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachihamthucthicaulenh2 + 11, self.diachixq + 0x95450 - (self.diachihamthucthicaulenh2 + 10) - 5)

            write_bytes(self.tientrinh, self.diachihamthucthicaulenh2 + 15, bytes.fromhex("83 C4 08"), 3)
            write_bytes(self.tientrinh, self.diachihamthucthicaulenh2 + 18, bytes.fromhex("C3"), 1)

            write_string(self.tientrinh, self.diachihamthucthicaulenh2 + 19, caulenh)

            self._is_dasetupautoassemblethucthicaulenh2 = True
        else:
            if read_int(self.tientrinh, self.diachihamthucthicaulenh2 + 1) != len(caulenh.encode("utf-8")):
                write_int(self.tientrinh, self.diachihamthucthicaulenh2 + 1, len(caulenh.encode("utf-8")))
            if read_string(self.tientrinh, self.diachihamthucthicaulenh2 + 19) != caulenh:
                write_string(self.tientrinh, self.diachihamthucthicaulenh2 + 19, caulenh)

        self.tientrinh.start_thread(self.diachihamthucthicaulenh2)
        return True

    def action_ralenhbaothutancong(self, iddoituongbaothu, iddoituongnhanvatmuctieudangchon, delay = 1.):
        if time.time() - self._thoidiemralenhbaothutancong < delay:
            return False
        self._thoidiemralenhbaothutancong = time.time()
        caulenh = f"pet {hex(iddoituongbaothu)}# 1 {hex(iddoituongnhanvatmuctieudangchon)}#".replace("0x", "")
        return self.action_thucthicaulenh2(caulenh, delay = 0.)

    def action_ralenhbaothutheosau(self, iddoituongbaothu, delay = 0.25):
        if time.time() - self._thoidiemralenhbaothutheosau < delay:
            return False
        self._thoidiemralenhbaothutheosau = time.time()
        caulenh = f"pet {hex(iddoituongbaothu)}# 2".replace("0x", "")
        return self.action_thucthicaulenh2(caulenh, delay = 0.)

    def action_ralenhbaothudungim(self, iddoituongbaothu, delay = 0.25):
        if time.time() - self._thoidiemralenhbaothudungim < delay:
            return False
        self._thoidiemralenhbaothudungim = time.time()
        caulenh = f"pet {hex(iddoituongbaothu)}# 3".replace("0x", "")
        return self.action_thucthicaulenh2(caulenh, delay = 0.)

    def action_batchucnangmorong(self, delay = 5.):
        if self.get_is_dangbatchucnangmorong():
            return False

        if time.time() - self.thoidiembatchucnangmoronggannhat < delay:
            return False

        self.thoidiembatchucnangmoronggannhat = time.time()

        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        a = read_int(self.tientrinh, x + 0xAEBC0C)
        b = read_int(self.tientrinh, x + 0xAEBC10)
        c = read_int(self.tientrinh, x + 0xAEBC14)

        caulenh = f"auto open {a:04d}{b:04d}{c:04d}"

        return self.action_thucthicaulenh(caulenh)

    def action_tatchucnangmorong(self, delay = 1.):
        if not self.get_is_dangbatchucnangmorong():
            return False
        if time.time() - self.thoidiemtatchucnangmoronggannhat < delay:
            return False
        self.thoidiemtatchucnangmoronggannhat = time.time()

        caulenh = f"auto close"

        return self.action_thucthicaulenh(caulenh)

    def action_nhatvatphamtoado(self, toadox, toadoy, delay = 0.05):
        if time.time() - self._thoidiemnhatvatphamtoadogannhat < delay:
            return False
        self._thoidiemnhatvatphamtoadogannhat = time.time()
        caulenh = "get {} {}".format(toadox, toadoy)
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

    def action_khaikhoang(self, iddoituong, delay = 0.05):
        if time.time() - self._thoidiemkhaikhoanggannhat < delay:
            return False
        self._thoidiemkhaikhoanggannhat = time.time()
        caulenh = "look {}#".format(hex(iddoituong)).replace("0x", "")
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

    def action_sudungkynang(self, idkynang, delay = 0.05):
        if time.time() - self._thoidiemsudungkynanggannhat < delay:
            return False
        self._thoidiemsudungkynanggannhat = time.time()
        caulenh = "pf {}".format(idkynang)
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO)

    def action_sudungtancongvatly(self, diachicosothongtinnhanvatmuctieu, delay = 0.):
        if time.time() - self._thoidiemsudungtancongvatlygannhat < delay:
            return False
        self._thoidiemsudungtancongvatlygannhat = time.time()

        diachicosothongtinnhanvatmuctieudangchon = diachicosothongtinnhanvatmuctieu if diachicosothongtinnhanvatmuctieu else self.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachicosothongtinnhanvatmuctieudangchon:
            return False

        if self.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon):
            idnguoichoi = self.get_idnguoichoi(diachicosothongtinnhanvatmuctieudangchon)
            caulenh = "kill {}".format(idnguoichoi)
        else:
            caulenh = "kill {}#".format(hex(self.get_iddoituong(diachicosothongtinnhanvatmuctieudangchon)).replace("0x", ""))

        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO)

    def action_sudungkynangmuctieunguoichoi(self, idkynang, idnguoichoi, delay = 0.05):
        if time.time() - self._thoidiemsudungkynangmuctieugannhat < delay:
            return False
        self._thoidiemsudungkynangmuctieugannhat = time.time()
        caulenh = "pf {} {}".format(idkynang, idnguoichoi)
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO)

    def action_sudungkynangmuctieukhacnguoichoi(self, idkynang, iddoituong, delay = 0.05):
        if time.time() - self._thoidiemsudungkynangmuctieugannhat < delay:
            return False
        self._thoidiemsudungkynangmuctieugannhat = time.time()
        caulenh = "pf {} {}#".format(idkynang, hex(iddoituong)).replace("0x", "")
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO)

    def action_sudungkynangtoado(self, idkynang, toadox, toadoy, delay = 0.05):
        if time.time() - self._thoidiemsudungkynangtoadogannhat < delay:
            return False
        self._thoidiemsudungkynangtoadogannhat = time.time()
        caulenh = "pf {} {},{}".format(idkynang, toadox, toadoy).replace("0x", "")
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO)

    def action_dichuyenvatphamhanhtrang(self, iddoituong, vitri, delay = 0.4):
        if time.time() - self._thoidiemdichuyenvatphamhanhtranggannhat < delay:
            return False
        self._thoidiemdichuyenvatphamhanhtranggannhat = time.time()
        caulenh = "move {}# {}".format(hex(iddoituong), vitri).replace("0x", "")
        return self.action_thucthicaulenh(caulenh)

    def action_dichuyenvatphamsanghanhtrangkhac(self, iddoituong, vitri, delay = 0.4):
        if time.time() - self._thoidiemdichuyenvatphamsanghanhtrangkhacgannhat < delay:
            return False
        self._thoidiemdichuyenvatphamsanghanhtrangkhacgannhat = time.time()
        caulenh = "move {}# to {}".format(hex(iddoituong), vitri).replace("0x", "")
        return self.action_thucthicaulenh(caulenh)

    def action_trochuyenvoinpc(self, iddoituong, noidungtrochuyen, delay = 0.2, caulenhtrochuyen = "talk"):
        if time.time() - self._thoidiemtrochuyenvoinpcgannhat < delay:
            return False
        self._thoidiemtrochuyenvoinpcgannhat = time.time()
        caulenh = "{} {}# {}".format(caulenhtrochuyen, hex(iddoituong), noidungtrochuyen).replace("0x", "")
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

    def action_sudungvatpham(self, iddoituong, is_boquaxacnhan = False, delay = 0.2, douutien = DOUUTIEN_KHANCAP):
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False
        self._thoidiemsudungvatphamgannhat = time.time()
        caulenh = "use ! {}#".format(hex(iddoituong)).replace("0x", "") if is_boquaxacnhan else "use {}#".format(hex(iddoituong)).replace("0x", "")
        return self.action_thucthicaulenh(caulenh, douutien = douutien)

    def action_moihoacxinvaonhom(self, idnguoichoi, delay = 0.2):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return False
        if not idnguoichoi:
            return False
        self._thoidiemthaotacnhomgannhat = time.time()
        caulenh = "team + {}".format(idnguoichoi)
        return self.action_thucthicaulenh(caulenh)

    def action_nhuongquyentruongnhom(self, idnguoichoi, delay = 0.2):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return False
        if not idnguoichoi:
            return False
        self._thoidiemthaotacnhomgannhat = time.time()
        caulenh = "team = {}".format(idnguoichoi)
        return self.action_thucthicaulenh(caulenh)

    def action_thoatkhoinhom(self, delay = 0.2):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return False
        self._thoidiemthaotacnhomgannhat = time.time()
        caulenh = "team x {}".format(self.get_idnguoichoi())
        return self.action_thucthicaulenh(caulenh)

    def action_kiemtravadongyloimoinhom(self, idtruongnhoms, delay = 0.2):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return False
        if not idtruongnhoms:
            return False
        caulenhmoinhomhientai = self.get_caulenhmoinhomhientai()
        if not caulenhmoinhomhientai:
            return False

        if "team + " in caulenhmoinhomhientai and self.get_is_danghiencuasoyesno():
            idnguoichoitruongnhoms = caulenhmoinhomhientai.split("team + ")
            if len(idnguoichoitruongnhoms) > 1:
                idnguoichoitruongnhom = int(idnguoichoitruongnhoms[1])
                if idnguoichoitruongnhom in idtruongnhoms:
                    caulenh = "team + {}".format(idnguoichoitruongnhom)
                    self.action_thucthicaulenh(caulenh)
                    self._thoidiemthaotacnhomgannhat = time.time()

                    if self.get_is_danghiencuasoyesno():
                        self.set_is_danghiencuasoyesno(False)
        return True

    def action_sudungvatphambaothu(self, iddoituongvatpham, iddoituongbaothu, delay = 0.2):
        if time.time() - self._thoidiemsudungvatphambaothugannhat < delay:
            return False
        self._thoidiemsudungvatphambaothugannhat = time.time()
        caulenh = "use {}# pet {}#".format(hex(iddoituongvatpham), hex(iddoituongbaothu)).replace("0x", "")
        return self.action_thucthicaulenh2(caulenh, delay = 0.)

    def action_trieuhoibaothu(self, iddoituong, delay = 0.2):
        if time.time() - self._thoidiemtrieuhoibaothugannhat < delay:
            return False
        self._thoidiemtrieuhoibaothugannhat = time.time()
        caulenh = "pet {}# show".format(hex(iddoituong)).replace("0x", "")
        return self.action_thucthicaulenh2(caulenh, delay = 0.)

    def action_sudungthaotacbaothu(self, iddoituong, idkynang, delay = 0.2):
        if time.time() - self._thoidiemsudungthaotacbaothugannhat < delay:
            return False
        self._thoidiemsudungthaotacbaothugannhat = time.time()
        caulenh = "pet {}# {}".format(hex(iddoituong), idkynang).replace("0x", "")
        return self.action_thucthicaulenh2(caulenh, delay = 0.)

    def action_thietlapchedobaothu(self, iddoituong, idkynang, delay = 0.2):
        if time.time() - self._thoidiemthietlapchedobaothugannhat < delay:
            return False
        self._thoidiemthietlapchedobaothugannhat = time.time()
        caulenh = "pet {}# mode {}".format(hex(iddoituong), idkynang).replace("0x", "")
        return self.action_thucthicaulenh2(caulenh, delay = 0.)

    def action_sudungkynangbaothu(self, idkynang, diachimuctieu, delay = 1.):
        if idkynang in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idkynang] < delay:
            return False
        if not diachimuctieu:
            return False
        if self.get_is_nguoichoi(diachimuctieu):
            caulenh = "pf5 {} {}".format(idkynang, self.get_idnguoichoi(diachimuctieu)).replace("0x", "")
        else:
            caulenh = "pf5 {} {}#".format(idkynang, hex(self.get_iddoituong(diachimuctieu))).replace("0x", "")

        self._thoidiemsudungkynangvitrigannhat_map[idkynang] = time.time()

        return self.action_thucthicaulenh2(caulenh, delay = 0.)

    def auto_assemble_nhatvatpham(self):
        if not self._is_dasetupautoassemblenhatvatpham:
            self._diachiautoassemblenhatvatpham = self.tientrinh.allocate(64)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatvatpham, bytes.fromhex("8B 0D"), 2)
            write_int(self.tientrinh, self._diachiautoassemblenhatvatpham + 2, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatvatpham + 6, bytes.fromhex("8D 59 14"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatvatpham + 9, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatvatpham + 10, self.diachixq + 0xB400 - (self._diachiautoassemblenhatvatpham + 9) - 5)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatvatpham + 14, bytes.fromhex("C3"), 1)
            self._is_dasetupautoassemblenhatvatpham = True
        self.tientrinh.start_thread(self._diachiautoassemblenhatvatpham)

    def auto_assemble_khoitaothongtinbando(self):
        if not self._is_dasetupautoassemblekhoitaothongtinbando:
            self._diachiautoassemblekhoitaothongtinbando = self.tientrinh.allocate(128)
            addr_base_ptr = self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME
            addr_func_init = self.diachixq + 0x3C100
            asm_script = f"""
                mov eax, {addr_base_ptr}
                mov ecx, [eax]          
                push 0x01002020         
                push 0x64               
                mov eax, {addr_func_init}
                call eax                
                ret
            """
            ks = Ks(KS_ARCH_X86, KS_MODE_32)
            encoding, count = ks.asm(asm_script)
            if not encoding:
                return
            write_bytes(self.tientrinh, self._diachiautoassemblekhoitaothongtinbando, bytes(encoding), len(encoding))
            self._is_dasetupautoassemblekhoitaothongtinbando = True
        self.tientrinh.start_thread(self._diachiautoassemblekhoitaothongtinbando)
        time.sleep(0.1)

    def action_thietlaphooknoidungtrochuyen(self):
        hook_offset = 0x5964
        addr_at_hook = self.diachixq + hook_offset
        addr_return = self.diachixq + hook_offset + 6

        if not self._is_dasetupactionthietlaphooknoidungtrochuyen:
            self._diachibodemnoidungtrochuyen = self.tientrinh.allocate(128)
            self._diachihamkichbannoidungtrochuyen = self.tientrinh.allocate(256)

            ks = Ks(KS_ARCH_X86, KS_MODE_32)

            asm_script = f"""
                pushad
                mov esi, ebp
                mov edi, {self._diachibodemnoidungtrochuyen}
                mov ecx, 128
            loop_copy:
                mov al, byte ptr [esi]
                mov byte ptr [edi], al
                test al, al
                jz end_copy
                inc esi
                inc edi
                dec ecx
                jnz loop_copy
                mov byte ptr [edi], 0
            end_copy:
                popad
                mov ecx, [edx + 0xADFDD8]
                push {addr_return}
                ret
            """

            encoding, count = ks.asm(asm_script)
            if not encoding:
                raise Exception("Lỗi compile ASM Keystone")

            write_bytes(self.tientrinh, self._diachihamkichbannoidungtrochuyen, bytes(encoding), len(encoding))

            self._is_dasetupactionthietlaphooknoidungtrochuyen = True

        relative_offset = self._diachihamkichbannoidungtrochuyen - (addr_at_hook + 5)
        patch_bytes = b"\xE9" + relative_offset.to_bytes(4, byteorder = "little", signed = True) + b"\x90"
        write_bytes(self.tientrinh, addr_at_hook, patch_bytes, len(patch_bytes))

        return True

    def get_sinhlucconlai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x152C) if x else False

    def get_sinhluctoida(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x1530) if x else False

    def get_noilucconlai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x1534) if x else False

    def get_noiluctoida(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x1538) if x else False

    def get_thelucconlai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x15A8) if x else False

    def get_phantramnoilucconlai(self):
        noiluctoida = self.get_noiluctoida()
        return (self.get_noilucconlai() * 100. / noiluctoida) if noiluctoida else 0

    def get_nguyenkhiconlai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x1560) if x else False

    def get_capdonhanvat(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x15B0) if x else False

    def get_idbandohientai(self):
        return self._idbandohientai

    def _get_idbandohientai(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x15F4) if x else False

    def get_diempk(self):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        return read_int(self.tientrinh, x + 0x1568) if x else False

    def get_iddoituongbaothu(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x184 + 0x6C * (sothutu - 1))

    def get_tendoituongbaothu(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        if not x:
            return False
        return read_string(self.tientrinh, x + 0x188 + 0x6C * (sothutu - 1))

    def get_trangthaihanhvidoituongbaothu(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1E0 + 0x6C * (sothutu - 1))

    def get_toadodoituongbaothu(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1B4 + 0x6C * (sothutu - 1)), read_int(self.tientrinh, x + 0x1B8 + 0x6C * (sothutu - 1))

    def get_idbandohientaidoituongbaothu(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1E4 + 0x6C * (sothutu - 1))

    def get_phantramsinhlucconlaidoituongbaothukynangtrieuhoi(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1D4 + 0x6C * (sothutu - 1)) * 2

    def get_phantramnoilucconlaidoituongbaothukynangtrieuhoi(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + 0x372864)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1D8 + 0x6C * (sothutu - 1)) * 2

    def get_diachicosothongtinnhanvat1(self):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVAT1)

    def get_diachicosothongtindoituongx(self, x):
        return read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVATX + x * 0x4)

    def get_diachicosothongtinvatphamhanhtrang(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        return read_int(self.tientrinh, x + 0xADFD78) if x else False

    def get_iddoituongvatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        return read_int(self.tientrinh, x + idvitri * 0x4) if x else False

    def get_soluongvatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        return read_int(self.tientrinh, x + idvitri * 0x4 + 0x1D6CC) if x else False

    def get_tenvatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        return read_string(self.tientrinh, x + idvitri * 0x20 + 0x1A8) if x else False

    def truyvan_motavatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return False
        iddoituongvatphamhanhtrang = self.get_iddoituongvatphamhanhtrang(idvitri)
        if not iddoituongvatphamhanhtrang: return False
        is_ok = self.action_thucthicaulenh("desc {}#".format(hex(iddoituongvatphamhanhtrang)).replace("0x", ""))
        if is_ok: time.sleep(0.2)
        return is_ok

    def get_motavatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return False
        mota = read_string(self.tientrinh, x + idvitri * 0x44C + 0xF52, 1024)
        if not mota and self.get_iddoituongvatphamhanhtrang(idvitri):
            self.truyvan_motavatphamhanhtrang(idvitri)
            mota = read_string(self.tientrinh, x + idvitri * 0x44C + 0xF52, 1024)
        return mota

    def get_motavatphamhanhtrang_raw(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return b""

        mota_raw = read_bytes(self.tientrinh, x + idvitri * 0x44C + 0xF52, 1024)

        null_index = mota_raw.find(b"\x00")
        if null_index != -1:
            mota_raw = mota_raw[:null_index]

        if not mota_raw and self.get_iddoituongvatphamhanhtrang(idvitri):
            self.truyvan_motavatphamhanhtrang(idvitri)
            mota_raw = read_bytes(self.tientrinh, x + idvitri * 0x44C + 0xF52, 1024)
            null_index = mota_raw.find(b"\x00")
            if null_index != -1:
                mota_raw = mota_raw[:null_index]

        mota_raw = re.sub(rb'\x1b[a-zA-Z0-9]', b'', mota_raw).strip()

        return mota_raw

    def get_diachicosothongtinkynang(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        return read_int(self.tientrinh, x + 0xADFE18) if x else False

    def get_is_dangmocuasoxacnhan(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFD8C)
        return read_boolean(self.tientrinh, x + 0xB4) if x else False

    def set_is_dangmocuasoxacnhan(self, is_dangmocuasoxacnhan):
        if self.get_is_dangmocuasoxacnhan() == is_dangmocuasoxacnhan: return
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x: return
        x = read_int(self.tientrinh, x + 0xADFD8C)
        if not x: return
        write_boolean(self.tientrinh, x + 0xB4, is_dangmocuasoxacnhan)

    def get_noidungcuasomaxacnhan(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x: return ""
        x = read_int(self.tientrinh, x + 0xADFD8C)
        return read_string(self.tientrinh, x + 0xBC) if x else ""

    def get_danhsachidnguoichoixungquanhs(self):
        i = -1
        danhsachidnguoichoixungquanhs = []
        while i < 512:
            i += 1
            diachicosothongtinnhanvatxemxet = self.get_diachicosothongtindoituongx(i)
            if not diachicosothongtinnhanvatxemxet: break
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet): continue
            idnguoichoi = self.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
            if not idnguoichoi: continue
            if self.get_khoangcach(diachicosothongtinnhanvatxemxet) > KHOANGCACHTOANMANHINH: continue
            danhsachidnguoichoixungquanhs.append(idnguoichoi)
        return danhsachidnguoichoixungquanhs

    def get_idnguoichoixungquanh_map(self):
        i = -1
        idnguoichoixungquanh_map = {}
        while i < 512:
            i += 1
            diachicosothongtinnhanvatxemxet = self.get_diachicosothongtindoituongx(i)
            if not diachicosothongtinnhanvatxemxet: break
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet): continue
            if not self.get_is_nguoichoi(diachicosothongtinnhanvatxemxet): continue
            if self.get_khoangcach(diachicosothongtinnhanvatxemxet) > KHOANGCACHTOANMANHINH: continue
            idnguoichoixungquanh_map[diachicosothongtinnhanvatxemxet] = self.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
        return idnguoichoixungquanh_map

    def get_tenchunhanbaothuxungquanh_map(self):
        i = -1
        tenchunhanbaothu_map = {}
        while i < 512:
            i += 1
            diachicosothongtinnhanvatxemxet = self.get_diachicosothongtindoituongx(i)
            if not diachicosothongtinnhanvatxemxet: break
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet): continue
            if not self.get_is_baothukynangtrieuhoi(diachicosothongtinnhanvatxemxet): continue
            if self.get_khoangcach(diachicosothongtinnhanvatxemxet) > KHOANGCACHTOANMANHINH: continue

            tenchunhan = self.get_tenchunhan(diachicosothongtinnhanvatxemxet)
            if tenchunhan:
                tenchunhanbaothu_map[diachicosothongtinnhanvatxemxet] = tenchunhan
        return tenchunhanbaothu_map

    def get_idbaothuxungquanh_map(self):
        i = -1
        idbaothuxungquanh_map = {}
        while i < 512:
            i += 1
            diachicosothongtinnhanvatxemxet = self.get_diachicosothongtindoituongx(i)
            if not diachicosothongtinnhanvatxemxet: break
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet): continue
            if not self.get_is_baothukynangtrieuhoi(diachicosothongtinnhanvatxemxet): continue
            if self.get_khoangcach(diachicosothongtinnhanvatxemxet) > KHOANGCACHTOANMANHINH: continue
            idbaothuxungquanh_map[diachicosothongtinnhanvatxemxet] = self.get_iddoituong(diachicosothongtinnhanvatxemxet)
        return idbaothuxungquanh_map

    def get_thoidiemtuthenhanvatdungimgannhat(self):
        return self._thoidiemtuthenhanvatdungimgannhat

    def get_thoidiemtuthenhanvatdungimcomuctieugannhat(self):
        return self._thoidiemtuthenhanvatdungimcomuctieugannhat

    def get_thoidiemtuthenhanvatkhongdichuyen(self):
        return self._thoidiemtuthenhanvatkhongdichuyengannhat

    def action_lammoitrangthaimoitruong(self):
        idnguoichoi = self.get_idnguoichoi()
        if idnguoichoi:
            self._idnguoichoi = idnguoichoi

        diachicosothongtinnhanvatmuctieuhientai = self.get_diachicosothongtinnhanvatmuctieudangchon()
        now = time.time()

        idnguoichoixungquanh_map = self.get_idnguoichoixungquanh_map()
        idnguoichoixungquanh_list = list(idnguoichoixungquanh_map.values())
        for diachinguoichoixungquanh, idnguoichoi in idnguoichoixungquanh_map.items():
            if self.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), macdinh = False, diachicosothongtinnhanvat = diachinguoichoixungquanh, is_hieuungcoloi = 0):
                self._thoidiemmuctieubichoanggannhat_map[idnguoichoi] = now
            if idnguoichoi not in self.thoidiemmuctieuxuathiengannhat_map:
                self.thoidiemmuctieuxuathiengannhat_map[idnguoichoi] = now
            if self.get_is_nhanvatanthan(diachinguoichoixungquanh):
                self.thoidiemmuctieuanthangannhat_map[idnguoichoi] = now

        if len(self._thoidiemmuctieubichoanggannhat_map) > 128:
            self._thoidiemmuctieubichoanggannhat_map = {uid: ts for uid, ts in self._thoidiemmuctieubichoanggannhat_map.items() if now - ts < 15}

        self.thoidiemmuctieuxuathiengannhat_map = {uid: ts for uid, ts in self.thoidiemmuctieuxuathiengannhat_map.items() if uid in idnguoichoixungquanh_list}
        self.thoidiemmuctieuanthangannhat_map = {uid: ts for uid, ts in self.thoidiemmuctieuanthangannhat_map.items() if uid in idnguoichoixungquanh_list}

        tenchunhanbaothuxungquanh_map = self.get_tenchunhanbaothuxungquanh_map()
        tenchunhanbaothuxungquanh_list = list(tenchunhanbaothuxungquanh_map.values())

        for diachibaothuxungquanh, tenchunhan in tenchunhanbaothuxungquanh_map.items():
            if tenchunhan not in self.thoidiembaothuxuathiengannhat_map:
                self.thoidiembaothuxuathiengannhat_map[tenchunhan] = now

        self.thoidiembaothuxuathiengannhat_map = {name: ts for name, ts in self.thoidiembaothuxuathiengannhat_map.items() if name in tenchunhanbaothuxungquanh_list}

        idbandohientai = self._get_idbandohientai()
        if idbandohientai != self._idbandohientai:
            self._thoidiemthaydoibandogannhat = time.time()
        self._idbandohientai = idbandohientai

        idtuthenhanvat = self.get_idtuthenhanvat()
        if idtuthenhanvat != TUTHENHANVAT_DUNGIM or self.get_is_dangvankhi():
            self._thoidiemtuthenhanvatdungimgannhat = time.time()
            self._thoidiemtuthenhanvatdungimcomuctieugannhat = time.time()
        if idtuthenhanvat == TUTHENHANVAT_DICHUYEN or self.get_is_dangvankhi():
            self._thoidiemtuthenhanvatkhongdichuyengannhat = time.time()

        if idtuthenhanvat not in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT):
            self._thoidiemtuthenhanvattanconggannhat = time.time()
        elif time.time() - self._thoidiemtuthenhanvattanconggannhat > 0.4:
            self.set_idtuthenhanvat(TUTHENHANVAT_DELAYSAUTANCONG)

        if not diachicosothongtinnhanvatmuctieuhientai or self.get_is_dangvankhi():
            self._thoidiemtuthenhanvatdungimcomuctieugannhat = time.time()

        idthucuoi = self._get_idthucuoi()
        if idthucuoi: self._thoidiemkhongcuoithugannhat = time.time()
        self._idthucuoi = idthucuoi

        if self.get_tenmonphai() == "thucson" and not self.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH,), macdinh = True, is_hieuungcoloi = 1):
            self._thoidiemcohieuungtienthanvodichgannhat = time.time()

        if self.get_tenmonphai() == "duongmon" and not self.get_is_cohieuungs((HIEUUNGKYNANG_LACTUYETVONGAN,), macdinh = True, is_hieuungcoloi = 1):
            self._thoidiemcohieuunglactuyetvongan = time.time()

        if self.get_is_nhanvatchuasansang(self.get_diachicosothongtinnhanvat1()):
            self._thoidiemnhanvatkhongsansanggannhat = time.time()

        self._is_nhanvatbichoang = self.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), macdinh = False, is_hieuungcoloi = 0)

        if not self.get_is_dangbatchucnangmorong():
            self.thoidiemcochucnangmoronggannhat = time.time()

        noidungtrochuyen = self.get_noidungtrochuyenmoinhat()

        if noidungtrochuyen and noidungtrochuyen != self._noidungtrochuyencu:
            self._lichsutrochuyen5s.append((now, noidungtrochuyen))
            self._noidungtrochuyencu = noidungtrochuyen

        self._lichsutrochuyen5s = [msg for msg in self._lichsutrochuyen5s if now - msg[0] <= 5.0]

    def get_lichsutrochuyen5s(self):
        return self._lichsutrochuyen5s

    def xoalichsutrochuyen(self):
        self._lichsutrochuyen5s.clear()

    def get_is_nhanvatbichoang(self):
        return self._is_nhanvatbichoang

    def get_thoidiemthaydoibandogannhat(self):
        return self._thoidiemthaydoibandogannhat

    def get_is_cuasogametontai(self):
        return win32gui.IsWindow(self.idcuaso)

    def get_is_cuasogamekichhoat(self):
        return win32gui.GetForegroundWindow() == self.idcuaso

    def get_diachicosothongtinnhanvatdangchichuot(self):
        return read_int(self.tientrinh, self.diachixq + 0x380B64)

    def get_is_cothegaychoang(self, diachicosothongtinnhanvat, thoigiangiancach = 2.0):
        if not diachicosothongtinnhanvat or not self.get_is_nguoichoi(diachicosothongtinnhanvat): return False
        idnguoichoi = self.get_idnguoichoi(diachicosothongtinnhanvat)
        if idnguoichoi <= 0: return True
        if self.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat, is_hieuungcoloi = 0): return False
        thoidiembichoanggannhat = self._thoidiemmuctieubichoanggannhat_map.get(idnguoichoi, 0)
        return time.time() - thoidiembichoanggannhat >= thoigiangiancach

    def get_idnguoichoi(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x24)

    def get_idphechientruong(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x10AD, 1)

    def get_is_dangmatketnoi(self):
        return not self.get_is_nhanvattontai()

    def get_iddoituong(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x20)

    def get_idloaidoituong(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0xF0)

    def get_is_nhanvattontai(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return self.get_iddoituong(diachicosothongtinnhanvat) > 0 and self.get_idloaidoituong(diachicosothongtinnhanvat) in (LOAIDOITUONG_NHANVAT1, LOAIDOITUONG_NHANVATKHAC1)

    def get_is_nhanvatanthan(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x162D) > 0

    def get_is_vatphamtontai(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return self.get_iddoituong(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) == LOAIDOITUONG_VATPHAMDUOIDAT

    def get_is_nhanvatdachet(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_boolean(self.tientrinh, diachicosothongtinnhanvat + 0x1424)

    def get_tendoituong(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        tendoituong = read_string(self.tientrinh, diachicosothongtinnhanvat + 0x10AC)

        if tendoituong:
            if "( Cấp" in tendoituong:
                tendoituong = tendoituong.split("( Cấp")[0].strip()
            elif "(Cấp" in tendoituong:
                tendoituong = tendoituong.split("(Cấp")[0].strip()

        return tendoituong

    def get_tennhanvatchichuot(self):
        diachi = self.get_diachicosothongtinnhanvatdangchichuot()
        return self.get_tendoituong(diachi) if diachi else False

    def get_noidungthongbaogannhat(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFD70)
        return read_string(self.tientrinh, x + 0x24) if x else False

    def get_phantramsinhlucconlai(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1410) * 2

    def get_toado(self, diachicosothongtinnhanvat = None, is_toadosaptoi = False):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        toadox = read_int(self.tientrinh, diachicosothongtinnhanvat)
        toadoy = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x4)

        if is_toadosaptoi and self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN:
            deltax = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x18) - toadox
            deltay = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1C) - toadoy

            if deltax != 0:
                toadox += int(deltax / abs(deltax))
            if deltay != 0:
                toadoy += int(deltay / abs(deltay))

        return toadox, toadoy

    def get_huongdichuyenx(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN:
            deltax = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x18) - read_int(self.tientrinh, diachicosothongtinnhanvat)
            if deltax != 0:
                return deltax / abs(deltax)
        return 0

    def get_huongdichuyeny(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN:
            deltay = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x18) - read_int(self.tientrinh, diachicosothongtinnhanvat)
            if deltay != 0:
                return deltay / abs(deltay)
        return 0

    def get_toadosaptoi(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return (
            read_int(self.tientrinh, diachicosothongtinnhanvat + 0x18) if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN else read_int(self.tientrinh, diachicosothongtinnhanvat),
            read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1C) if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN else read_int(self.tientrinh, diachicosothongtinnhanvat),
        )

    def get_toadobandochichuot(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)
        return (read_int(self.tientrinh, x + 0x371C80), read_int(self.tientrinh, x + 0x371C84)) if x else False

    def get_idbandochichuot(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)
        if not x:
            return False
        y = read_int(self.tientrinh, x + 0x11F10)
        return read_int(self.tientrinh, x + 0x23C + 0x16C * y) if y else False

    def get_idmaupk(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        return read_int(self.tientrinh, x + 0xAED6CC) if x else False

    def set_idmaupk(self, idmaupk):
        if self.get_idmaupk() != idmaupk:
            x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
            if x: write_int(self.tientrinh, x + 0xAED6CC, idmaupk)

    def get_tenbang(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_string(self.tientrinh, diachicosothongtinnhanvat + 0x1136)

    def get_is_cungbang(self, diachicosothongtinnhanvat):
        return self.get_idnguoichoi(diachicosothongtinnhanvat) in NHANVATCUNGBANGs

    def get_idtrangthaichuot(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDA8)
        return read_int(self.tientrinh, x + 0x1A4) if x else False

    def set_idtrangthaichuot(self, idtrangthaichuot):
        if idtrangthaichuot != self.get_idtrangthaichuot():
            x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
            if x:
                x = read_int(self.tientrinh, x + 0xADFDA8)
                if x: write_int(self.tientrinh, x + 0x1A4, idtrangthaichuot)

    def get_khoangcach(self, diachicosothongtinnhanvat2, diachicosothongtinnhanvat1 = False):
        diachicosothongtinnhanvat1 = diachicosothongtinnhanvat1 or self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toado(diachicosothongtinnhanvat1)
        x2, y2 = self.get_toado(diachicosothongtinnhanvat2)

        return math.dist((x1, y1), (x2, y2))

    def get_khoangcachdiem(self, x2, y2, diachicosothongtinnhanvat1 = False):
        diachicosothongtinnhanvat1 = diachicosothongtinnhanvat1 or self.get_diachicosothongtinnhanvat1()
        x1, y1 = self.get_toado(diachicosothongtinnhanvat1)
        return math.dist((x1, y1), (x2, y2))

    def get_idthucuoi(self):
        return self._idthucuoi

    def _get_idthucuoi(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1198)

    def get_idtuthenhanvat(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1178)

    def set_idtuthenhanvat(self, idtuthenhanvat, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) != idtuthenhanvat:
            write_int(self.tientrinh, diachicosothongtinnhanvat + 0x1178, idtuthenhanvat)

    def get_is_muctieuchaytron(self, diachicosothongtinnhanvat):
        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) != TUTHENHANVAT_DICHUYEN:
            return False

        x_thucte, y_thucte = self.get_toado(diachicosothongtinnhanvat)
        kc_thucte = self.get_khoangcachdiem(x_thucte, y_thucte)

        x_dukien, y_dukien = self.get_toado(diachicosothongtinnhanvat)
        kc_dukien = self.get_khoangcachdiem(x_dukien, y_dukien)

        return kc_dukien > kc_thucte

    def get_is_dangdelaysautancong(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x11B8) == 11

    def get_soluonghieuungnhanvat(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        soluong = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x2EE8)
        soluongtruocdo = self._soluonghieuungnhanvattruocdo_map.get(diachicosothongtinnhanvat, -1)
        if soluongtruocdo > 0 and soluong == 0:
            self._thoidiemsoluonghieuungbangkhonggannhat_map[diachicosothongtinnhanvat] = time.time()
        self._soluonghieuungnhanvattruocdo_map[diachicosothongtinnhanvat] = soluong
        return soluong

    def get_danhsachhieuungnhanvats(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        hieuungs = []
        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat): return hieuungs
        diachicosohieuungnhanvat = diachicosothongtinnhanvat + OFFSET_DIACHICOSOHIEUUNGNHANVAT
        soluonghieuungnhanvat = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
        soluonghieuungdemduoc = 0
        i = -1
        while True:
            if not self.get_is_nhanvattontai(diachicosothongtinnhanvat): return hieuungs
            soluonghieuungnhanvatmoinhat = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
            if soluonghieuungnhanvat != soluonghieuungnhanvatmoinhat:
                soluonghieuungnhanvat = soluonghieuungnhanvatmoinhat
                soluonghieuungdemduoc = 0
                i = -1
            i += 1
            if i >= SOLUONGHIEUUNGNHANVATTOIDA: return hieuungs
            idvitrihieuungxemxet = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT)
            is_hieuungcoloi = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x4)
            thoigianhieuluctoida = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x8)
            if idvitrihieuungxemxet < 0 or is_hieuungcoloi < 0 or (not idvitrihieuungxemxet and not is_hieuungcoloi and not thoigianhieuluctoida): continue
            idhieuungxemxet = read_int(self.tientrinh, self.diachixq + 0x1C05E0 + idvitrihieuungxemxet * 4)
            hieuungs.append((idhieuungxemxet, is_hieuungcoloi, thoigianhieuluctoida))
            soluonghieuungdemduoc += 1
            if soluonghieuungdemduoc >= soluonghieuungnhanvatmoinhat: break
        return hieuungs

    def get_thoigianconlaihieuungtienthanvodich(self, macdinh):
        x = self.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH,), macdinh = (True, macdinh), is_hieuungcoloi = 1, is_travethoigianhieuluctoida = True)
        if not x: return 0.
        is_cohieuung, thoigianhieuluctoida = x
        return thoigianhieuluctoida - (time.time() - self._thoidiemcohieuungtienthanvodichgannhat) if is_cohieuung else 0.

    def get_thoigianconlaihieuungkimcuongbathoaidon(self, macdinh):
        x = self.get_is_cohieuungs((HIEUUNGKYNANG_KIMCUONGBATHOAIDON,), macdinh = (True, macdinh), is_hieuungcoloi = 1, is_travethoigianhieuluctoida = True)
        if not x: return 0.
        is_cohieuung, thoigianhieuluctoida = x
        return thoigianhieuluctoida - (time.time() - self._thoidiemcohieuungkimcuongbathoaidongannhat) if is_cohieuung else 0.

    def get_is_cohieuungs(self, idhieuungs, macdinh, diachicosothongtinnhanvat = None, is_hieuungcoloi = None, is_travethoigianhieuluctoida = False):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
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
            if soluonghieuungdemduoc >= soluonghieuungnhanvat: return False
            i += 1
            if i >= SOLUONGHIEUUNGNHANVATTOIDA: return macdinh
            idvitrihieuungxemxet = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT)
            is_hieuungcoloixemxet = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x4)
            thoigianhieuluctoida = read_int(self.tientrinh, diachicosohieuungnhanvat + i * OFFSET_DIACHICOSOMOIHIEUUNGNHANVAT + 0x8)
            if idvitrihieuungxemxet < 0 or is_hieuungcoloixemxet < 0 or (not idvitrihieuungxemxet and not is_hieuungcoloixemxet and not thoigianhieuluctoida): continue
            idhieuungxemxet = read_int(self.tientrinh, self.diachixq + 0x1C05E0 + idvitrihieuungxemxet * 4)
            if idhieuungxemxet in idhieuungs:
                if is_hieuungcoloi is not None:
                    if is_travethoigianhieuluctoida: return is_hieuungcoloixemxet == is_hieuungcoloi, thoigianhieuluctoida
                    return is_hieuungcoloixemxet == is_hieuungcoloi
                if is_travethoigianhieuluctoida: return True, thoigianhieuluctoida
                return True
            soluonghieuungdemduoc += 1
        return macdinh

    def get_diachicosoidthanhviennhom(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0xADFDA4) if x else False

    def get_toadotruongnhom(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        return (read_int(self.tientrinh, diachicosothanhviennhom + 0xBD0), read_int(self.tientrinh, diachicosothanhviennhom + 0xC00)) if diachicosothanhviennhom else False

    def get_idnguoichoitruongnhom(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        return read_int(self.tientrinh, diachicosothanhviennhom) if diachicosothanhviennhom else False

    def get_is_truongnhom(self):
        return self.get_idnguoichoi(self.get_diachicosothongtinnhanvat1()) == self.get_idnguoichoitruongnhom()

    def get_danhsachidnguoichoithanhviennhoms(self):
        idthanhviens = []
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom: return idthanhviens
        for i in range(SOLUONGTHANHVIENNHOMTOIDATHUCTE):
            idthanhvien = read_int(self.tientrinh, diachicosothanhviennhom + i * 0x4)
            if idthanhvien: idthanhviens.append(idthanhvien)
        return idthanhviens

    def get_is_dangnamtrongnhom(self):
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        return read_int(self.tientrinh, diachicosothanhviennhom) > 0 if diachicosothanhviennhom else False

    def get_is_tamngungtancong(self):
        return self._is_tamngungtancong

    def set_is_tamngungtancong(self, is_tamngungtancong):
        self._is_tamngungtancong = is_tamngungtancong

    def get_idloainhanvat(self, diachicosothongtinnhanvat):
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x28) if diachicosothongtinnhanvat else False

    def get_is_nguoichoi(self, diachicosothongtinnhanvat):
        if not diachicosothongtinnhanvat:
            return False
        return self.get_idloainhanvat(diachicosothongtinnhanvat) in (LOAIMUCTIEU_NGUOICHOIKHACNHOM, LOAIMUCTIEU_NGUOICHOICUNGNHOM)

    def get_is_npc(self, diachicosothongtinnhanvat):
        if self.get_phantramsinhlucconlai(diachicosothongtinnhanvat) > 100: return True
        return read_int(self.tientrinh, diachicosothongtinnhanvat + 0x155C) in (25, 40)

    def get_idkynang(self, idvitri_x, idvitri_y):
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang: return False
        idvitrikynang = 14 * idvitri_y + idvitri_x
        return read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830)

    def get_is_kynangsansang(self, idvitri_x, idvitri_y):
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang: return False
        idvitrikynang = 14 * idvitri_y + idvitri_x
        idkynang = read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6830)
        is_khongcothoigiangiancach = read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * OFFSET_DIACHICOSOMOIKYNANG + 0x6A4C) == 0
        return idkynang and True and is_khongcothoigiangiancach

    def get_is_nhanvatchuasansang(self, diachicosothongtinnhanvat = False):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x29) == 1

    def get_is_baothugiangho(self, diachicosodoituong):
        if not diachicosodoituong:
            return False
        tendoituong = read_string(self.tientrinh, diachicosodoituong + 0x10AC)
        if not tendoituong:
            return False
        return "(" in tendoituong and "( " not in tendoituong

    def get_is_baothukynangtrieuhoi(self, diachicosodoituong):
        if not diachicosodoituong:
            return False
        tendoituong = read_string(self.tientrinh, diachicosodoituong + 0x10AC)
        if not tendoituong:
            return False
        return tendoituong.count("(") == 2

    def get_tenchunhan(self, diachicosodoituong):
        if not diachicosodoituong:
            return False

        tendoituong = self.get_tendoituong(diachicosodoituong)

        if not tendoituong:
            return False

        if "(" in tendoituong and ")" in tendoituong:
            try:
                tenchunhan = tendoituong.split("(")[1].split(")")[0].strip()
                if tenchunhan:
                    return tenchunhan
            except Exception:
                pass

        return False

    def get_is_cothetancong(self, diachicosothongtinnhanvat):
        if not diachicosothongtinnhanvat or not self.get_is_nhanvattontai(diachicosothongtinnhanvat) or self.get_is_nhanvatdachet(diachicosothongtinnhanvat) or self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_NAMDUOIDAT:
            return False

        idloainhanvat = self.get_idloainhanvat(diachicosothongtinnhanvat)

        if self.get_idbandohientai() == BANDO_TIVO and self.get_is_nguoichoi(diachicosothongtinnhanvat):
            return True

        if idloainhanvat == LOAIMUCTIEU_NGUOICHOICUNGNHOM:
            return False
        if self.get_idbandohientai() == BANDO_CHIENTRUONG and self.get_idphechientruong() == self.get_idphechientruong(diachicosothongtinnhanvat):
            return False
        if self.get_is_npc(diachicosothongtinnhanvat) or self.get_is_nhanvatchuasansang(diachicosothongtinnhanvat):
            return False

        idmaupk = self.get_idmaupk()
        tenmuctieu = self.get_tendoituong(diachicosothongtinnhanvat)
        if tenmuctieu:
            if self.get_is_baothukynangtrieuhoi(diachicosothongtinnhanvat) or self.get_is_baothugiangho(diachicosothongtinnhanvat):
                if idmaupk == MAUPK_HOABINH:
                    return False
                tenchunhan = self.get_tenchunhan(diachicosothongtinnhanvat)
                if tenchunhan:
                    if tenchunhan == self.get_tendoituong() or tenchunhan in TENNGUOICHOICUNGBANGs:
                        return False
                    diachicosothongtinnhanvatchunhan = self.action_timkiemnhanvat(tennhanvat = tenchunhan)
                    if diachicosothongtinnhanvatchunhan:
                        return self.get_is_cothetancong(diachicosothongtinnhanvatchunhan)

        if idmaupk == MAUPK_TUDO:
            return True
        elif idmaupk == MAUPK_HOABINH and idloainhanvat in (LOAIMUCTIEU_NGUOICHOIKHACNHOM, LOAIMUCTIEU_NGUOICHOICUNGNHOM):
            return False
        elif idmaupk == MAUPK_NHOM and idloainhanvat == LOAIMUCTIEU_NGUOICHOICUNGNHOM:
            return False
        elif idmaupk == MAUPK_BANG and idloainhanvat == LOAIMUCTIEU_NGUOICHOIKHACNHOM and self.get_is_cungbang(diachicosothongtinnhanvat):
            return False

        return True

    def get_is_batalt(self):
        x = read_int(self.tientrinh, self.diachixq + 0x380B38)
        return read_boolean(self.tientrinh, x) if x else False

    def set_is_batalt(self, is_batalt):
        if self.get_is_batalt() != is_batalt:
            x = read_int(self.tientrinh, self.diachixq + 0x380B38)
            if x: write_boolean(self.tientrinh, x, is_batalt)

    def get_is_batautoingame(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        return read_boolean(self.tientrinh, x + 0xAEC924) if x else False

    def set_is_batautoingame(self, is_batautoingame):
        if not is_batautoingame:
            if read_bytes(self.tientrinh, self.diachixq + 0x6EC9, 1) != bytes.fromhex("90"):
                write_bytes(self.tientrinh, self.diachixq + 0x6EC9, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

        if self.get_is_batautoingame() != is_batautoingame:
            x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
            if x: write_boolean(self.tientrinh, x + 0xAEC924, is_batautoingame)

    def get_is_dangbatchucnangmorong(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINNHANVAT1)
        if not x:
            return True
        return read_string(self.tientrinh, x + 0x1136) == "Tự Động Đánh"

    def get_is_bathanhtrang(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFE0C)
        return read_boolean(self.tientrinh, x + 0x34) if x else False

    def get_is_dangbatenter(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFD60)
        return read_boolean(self.tientrinh, x + 0x8140) if x else False

    def get_thoidiemkhongcomuctieugannhat(self):
        return self._thoidiemkhongcomuctieugannhat

    def get_iddoituongmuctieudangchon(self):
        diachi = self.get_diachicosothongtinnhanvatmuctieudangchon()
        return self.get_iddoituong(diachi) if diachi else False

    def get_is_dangclickchuottrai(self):
        return read_boolean(self.tientrinh, self.diachixq + 0x380B7D)

    def get_diachicosothongtinnhanvatmuctieudangchon(self):
        return self._diachicosothongtinnhanvatmuctieudangchon

    def _get_diachicosothongtinnhanvatmuctieudangchon(self):
        return read_int(self.tientrinh, self.diachixq + 0x1BD4F0)

    def get_thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat(self):
        return self._thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat

    def set_diachicosothongtinnhanvatmuctieudangchon(self, diachi):
        if self._diachicosothongtinnhanvatmuctieudangchon != diachi: self._diachicosothongtinnhanvatmuctieudangchon = diachi

    def action_phananhdiachicosothongtinnhanvatmuctieudangchoningame(self, delay = 0.25):
        if time.time() - self._thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat < delay:
            return
        self._thoidiemthietlapdiachicosothongtinnhanvatmuctieudangchongannhat = time.time()
        diachi = self._diachicosothongtinnhanvatmuctieudangchon
        if diachi and self.get_iddoituong(diachi) > 0:
            write_int(self.tientrinh, self.diachixq + 0x1BD4F0, diachi)
            write_int(self.tientrinh, self.diachixq + 0x37284C, self.get_iddoituong(diachi))
            write_int(self.tientrinh, self.diachixq + 0x1BD550, diachi)
            write_int(self.tientrinh, self.diachixq + 0x1BD554, self.get_iddoituong(diachi))
            return
        write_int(self.tientrinh, self.diachixq + 0x1BD4F0, 0)
        write_int(self.tientrinh, self.diachixq + 0x37284C, 0)
        write_int(self.tientrinh, self.diachixq + 0x1BD550, 0)
        write_int(self.tientrinh, self.diachixq + 0x1BD554, 0)

    def action_vohieuhoatuthedelaysautancong(self):
        if read_int(self.tientrinh, self.diachixq + 0x1AFE3 + 0x6) != TUTHENHANVAT_DUNGIM: write_int(self.tientrinh, self.diachixq + 0x1AFE3 + 0x6, TUTHENHANVAT_DUNGIM)
        if read_int(self.tientrinh, self.diachixq + 0x1B377 + 0x6) != TUTHENHANVAT_DUNGIM: write_int(self.tientrinh, self.diachixq + 0x1B377 + 0x6, TUTHENHANVAT_DUNGIM)

    def action_tatvohieuhoatuthedelaysautancong(self):
        if read_int(self.tientrinh, self.diachixq + 0x1AFE3 + 0x6) != TUTHENHANVAT_DELAYSAUTANCONG: write_int(self.tientrinh, self.diachixq + 0x1AFE3 + 0x6, TUTHENHANVAT_DELAYSAUTANCONG)
        if read_int(self.tientrinh, self.diachixq + 0x1B377 + 0x6) != TUTHENHANVAT_DELAYSAUTANCONG: write_int(self.tientrinh, self.diachixq + 0x1B377 + 0x6, TUTHENHANVAT_DELAYSAUTANCONG)

    def action_vohieuhoathietlapmuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0xA20F0, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA20F0, bytes.fromhex("90 90 90 90 90"), 5)
        if read_bytes(self.tientrinh, self.diachixq + 0xA20F8, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + 0xA20F8, bytes.fromhex("90 90 90 90 90 90"), 6)
        if read_bytes(self.tientrinh, self.diachixq + 0xA20FE, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + 0xA20FE, bytes.fromhex("90 90 90 90 90"), 5)
        if read_bytes(self.tientrinh, self.diachixq + 0xA2106, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + 0xA2106, bytes.fromhex("90 90 90 90 90 90"), 6)

    def action_tatvohieuhoathietlapmuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0xA20F0, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA20F0, bytes.fromhex("A3"), 1)
            write_int(self.tientrinh, self.diachixq + 0xA20F0 + 1, self.diachixq + 0x1BD550)
        if read_bytes(self.tientrinh, self.diachixq + 0xA20F8, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA20F8, bytes.fromhex("89 0D"), 2)
            write_int(self.tientrinh, self.diachixq + 0xA20F8 + 2, self.diachixq + 0x1BD554)
        if read_bytes(self.tientrinh, self.diachixq + 0xA20FE, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA20FE, bytes.fromhex("A3"), 1)
            write_int(self.tientrinh, self.diachixq + 0xA20FE + 1, self.diachixq + 0x1BD4F0)
        if read_bytes(self.tientrinh, self.diachixq + 0xA2106, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0xA2106, bytes.fromhex("89 15"), 2)
            write_int(self.tientrinh, self.diachixq + 0xA2106 + 2, self.diachixq + 0x37284C)

    def action_vohieuhoaxoamuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x9542B, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + 0x9542B, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)
        if read_bytes(self.tientrinh, self.diachixq + 0x95435, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + 0x95435, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

    def action_tatvohieuhoaxoamuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x9542B, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x9542B, bytes.fromhex("C7 05"), 2)
            write_int(self.tientrinh, self.diachixq + 0x9542B + 2, self.diachixq + 0x1BD554)
            write_int(self.tientrinh, self.diachixq + 0x9542B + 6, 0)
        if read_bytes(self.tientrinh, self.diachixq + 0x95435, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x95435, bytes.fromhex("C7 05"), 2)
            write_int(self.tientrinh, self.diachixq + 0x95435 + 2, self.diachixq + 0x1BD4F0)
            write_int(self.tientrinh, self.diachixq + 0x95435 + 6, 0)

    def action_vohieuhoalongclick(self):
        if read_int(self.tientrinh, self.diachixq + 0x4993C + 0x6) != 0: write_int(self.tientrinh, self.diachixq + 0x4993C + 0x6, 0)

    def action_tatvohieuhoalongclick(self):
        if read_int(self.tientrinh, self.diachixq + 0x4993C + 0x6) != 1: write_int(self.tientrinh, self.diachixq + 0x4993C + 0x6, 1)

    def action_vohieuhoatrangthaichuotchonmuctieukynang(self):
        if read_int(self.tientrinh, self.diachixq + 0x5416C + 0x6) != 0: write_int(self.tientrinh, self.diachixq + 0x5416C + 0x6, 0)

    def action_tatvohieuhoatrangthaichuotchonmuctieukynang(self):
        if read_int(self.tientrinh, self.diachixq + 0x5416C + 0x6) != 2: write_int(self.tientrinh, self.diachixq + 0x5416C + 0x6, 2)

    def action_chantangcapdo(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x13FB61, 1) == bytes.fromhex("E8"): write_bytes(self.tientrinh, self.diachixq + 0x13FB61, bytes.fromhex("83 C4 08 90 90"), 5)

    def action_bochantangcapdo(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x13FB61, 1) == bytes.fromhex("83"):
            write_bytes(self.tientrinh, self.diachixq + 0x13FB61, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachixq + 0x13FB61 + 1, self.diachixq + 0x16C730 - (self.diachixq + 0x13FB61) - 5)

    def action_vohieuhoakhoanhvungkynang(self):
        pass

    def action_tatvohieuhoakhoanhvungkynang(self):
        pass

    def action_vohieuhoaphimspace(self):
        pass

    def action_tatvohieuhoaphimspace(self):
        pass

    def action_vohieuhoahookchienquoc2(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x95450, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + 0x95450, b'\x90\x90\x90\x90\x90', 5)

    def action_vohieuhieuungmuloa(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x4C0E + 0x6, 1) != bytes.fromhex("00"): write_bytes(self.tientrinh, self.diachixq + 0x4C0E + 0x6, bytes.fromhex("00"), 1)

    def action_vohieuhoadichuyen(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x9BE38, 1) != bytes.fromhex("EB"): write_bytes(self.tientrinh, self.diachixq + 0x9BE38, bytes.fromhex("EB"), 1)

    def action_tatvohieuhoadichuyen(self):
        if read_bytes(self.tientrinh, self.diachixq + 0x9BE38, 1) != bytes.fromhex("7E"): write_bytes(self.tientrinh, self.diachixq + 0x9BE38, bytes.fromhex("7E"), 1)

    def get_is_dangmobando(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)
        return read_boolean(self.tientrinh, x) if x else False

    def get_is_danghiencuasoyesno(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFE10)
        return read_boolean(self.tientrinh, x + 0x34) if x else False

    def set_is_danghiencuasoyesno(self, is_danghiencuasoyesno):
        if self.get_is_danghiencuasoyesno() != is_danghiencuasoyesno:
            x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
            if x:
                x = read_int(self.tientrinh, x + 0xADFE10)
                if x: write_boolean(self.tientrinh, x + 0x34, is_danghiencuasoyesno)

    def get_is_danghiencuasotuychon(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFD74)
        return read_boolean(self.tientrinh, x + 0x1E38) if x else False

    def set_is_danghiencuasotuychon(self, is_danghiencuasotuychon):
        if self.get_is_danghiencuasotuychon() != is_danghiencuasotuychon:
            x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
            if x:
                x = read_int(self.tientrinh, x + 0xADFD74)
                if x: write_boolean(self.tientrinh, x + 0x1E38, is_danghiencuasotuychon)

    def get_caulenhmoinhomhientai(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFE10)
        return read_string(self.tientrinh, x + 0x7C).strip() if x else False

    def auto_assemble_dichuyen(self, x, y):
        self._xdichuyengannhat = x
        self._ydichuyengannhat = y
        self._thoidiemboquadichuyencungtoadogannhat = time.time()

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
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 26, self.diachixq + 0x47790 - (self._diachiautoassembledichuyen + 25) - 5)

            write_bytes(self.tientrinh, self._diachiautoassembledichuyen + 30, bytes.fromhex("C3"), 1)
            self._is_dasetupautoassembledichuyen = True
        else:
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 10, y)
            write_int(self.tientrinh, self._diachiautoassembledichuyen + 15, x)

        self.tientrinh.start_thread(self._diachiautoassembledichuyen)
        time.sleep(0.05)

    def action_dichuyen(self, x, y, delay = 0.05, is_rangbuoctrongmanhinh = False):
        if self._is_vohieuhoadichuyen:
            return False

        if time.time() - self._thoidiemdichuyengannhat < delay:
            return False

        if self.get_is_cohieuungs((HIEUUNGKYNANG_ROILOAN,), macdinh = False, is_hieuungcoloi = 0):
            x = 2 * self._centerx - x
            y = 2 * self._centery - y
        if is_rangbuoctrongmanhinh:
            x = max(min(x, self._xmax - 25), 25)
            y = max(min(y, self._ymax - 25), 25)

        self._thoidiemdichuyengannhat = time.time()

        self.auto_assemble_dichuyen(int(x), int(y))

        return True

    def action_dichuyengiukhoangcachtoithieu(self, diachicosothongtinnhanvat2, khoangcachtoithieu, khoangcachdichuyentoida = 0, delay = 0.05):
        if not diachicosothongtinnhanvat2 or not self.get_iddoituong(diachicosothongtinnhanvat2):
            return False
        return self.action_dichuyengiukhoangcachtoithieudiem(*self.get_toado(diachicosothongtinnhanvat2), khoangcachtoithieu = khoangcachtoithieu, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyengiukhoangcachtoida(self, diachicosothongtinnhanvat2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.05):
        if not diachicosothongtinnhanvat2 or not self.get_iddoituong(diachicosothongtinnhanvat2):
            return False

        return self.action_dichuyengiukhoangcachtoidadiem(*self.get_toado(diachicosothongtinnhanvat2), khoangcachtoida = khoangcachtoida, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyenphudau(self, diachicosothongtinnhanvat2, khoangcachphudau = 1, delay = 0.05):
        if not diachicosothongtinnhanvat2 or not self.get_iddoituong(diachicosothongtinnhanvat2):
            return False
        diachi1 = self.get_diachicosothongtinnhanvat1()
        x2, y2 = self.get_toado(diachicosothongtinnhanvat2)
        x1, y1 = self.get_toado(diachi1)
        deltax, deltay = x2 - x1, y1 - y2
        khoangcach = math.dist((x1, y1), (x2, y2))
        khoangcachdichuyen = khoangcach + khoangcachphudau
        if not khoangcachdichuyen:
            return False
        if khoangcach > 0.:
            deltax, deltay = khoangcachdichuyen * deltax / khoangcach, khoangcachdichuyen * deltay / khoangcach
        else:
            deltax, deltay = khoangcachdichuyen, khoangcachdichuyen
        if not deltax and not deltay:
            return False
        xclick = round(self._centerx + deltax * (self._xmax / KHOANGCACHTOANMANHINH))
        yclick = round(self._centery + deltay * (self._ymax / KHOANGCACHTOANMANHINH))
        return self.action_dichuyen(xclick, yclick, delay = delay)

    def action_dichuyengiukhoangcachtoidadiem(self, x2, y2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.05, is_rangbuoctrongmanhinh = False):
        if x2 <= 0 or y2 <= 0:
            return False

        diachi1 = self.get_diachicosothongtinnhanvat1()

        x1, y1 = self.get_toado(diachi1)
        khoangcach = math.dist((x1, y1), (x2, y2))
        if khoangcach <= khoangcachtoida:
            return False

        khoangcachdichuyen = khoangcach - khoangcachtoida

        if khoangcachdichuyen <= 0.:
            return False

        x1, y1 = self.get_toado(diachi1)
        khoangcach = math.dist((x1, y1), (x2, y2))

        deltax, deltay = x2 - x1, y1 - y2

        if khoangcachdichuyentoida:
            khoangcachdichuyen = min(float(khoangcachdichuyentoida), khoangcachdichuyen)

        if khoangcach > 0.0:
            deltax = (khoangcachdichuyen * deltax) / khoangcach
            deltay = (khoangcachdichuyen * deltay) / khoangcach

        if not deltax and not deltay:
            return False

        offset_x = deltax * (self._xmax / KHOANGCACHTOANMANHINH)
        offset_y = deltay * (self._ymax / KHOANGCACHTOANMANHINH)

        dx_pixel = int(offset_x)
        dy_pixel = int(offset_y)

        xclick = self._centerx + dx_pixel
        yclick = self._centery + dy_pixel

        return self.action_dichuyen(xclick, yclick, delay = delay, is_rangbuoctrongmanhinh = is_rangbuoctrongmanhinh)

    def action_dichuyengiukhoangcachtoithieudiem(self, x2, y2, khoangcachtoithieu, khoangcachdichuyentoida = 0, delay = 0.05):
        if x2 <= 0 or y2 <= 0:
            return False
        diachi1 = self.get_diachicosothongtinnhanvat1()
        x1, y1 = self.get_toado(diachi1, )
        khoangcach = math.dist((x1, y1), (x2, y2))
        if khoangcach >= khoangcachtoithieu:
            return False
        deltax, deltay = x2 - x1, y1 - y2
        khoangcachdichuyen = khoangcachtoithieu
        if khoangcachdichuyen <= 0.:
            return False
        if khoangcachdichuyentoida:
            khoangcachdichuyen = min(khoangcachdichuyentoida * 1.5, khoangcachdichuyen)
        if khoangcach > 0.:
            deltax, deltay = int(-1 * khoangcachdichuyen * deltax / khoangcach), int(-1 * khoangcachdichuyen * deltay / khoangcach)
        if not deltax and not deltay:
            deltax, deltay = random.randint(-1, 1) * khoangcachdichuyentoida, random.randint(-1, 1) * khoangcachdichuyentoida
        xclick = int(self._centerx + deltax * (self._xmax / KHOANGCACHTOANMANHINH))
        yclick = int(self._centery + deltay * (self._ymax / KHOANGCACHTOANMANHINH))
        return self.action_dichuyen(xclick, yclick, delay = delay)

    def action_dichuyentiepcan(self, diachi2, khoangcachdichuyentoida = 0, delay = 0.05):
        return self.action_dichuyengiukhoangcachtoida(diachi2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyentiepcandiem(self, x2, y2, khoangcachdichuyentoida = 0, delay = 0.05, is_rangbuoctrongmanhinh = False):
        if x2 <= 0 or y2 <= 0:
            return False
        return self.action_dichuyengiukhoangcachtoidadiem(x2, y2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay, is_rangbuoctrongmanhinh = is_rangbuoctrongmanhinh)

    def action_sudungkynangvitriphudau(self, idvitri_x, idvitri_y, diachi2, khoangcachphudau, delay = 1):
        if not diachi2 or not self.get_is_nhanvattontai(diachi2):
            return False
        return self.action_sudungkynangvitriphudaudiem(idvitri_x, idvitri_y, *self.get_toado(diachi2), khoangcachphudau = khoangcachphudau, delay = delay)

    def action_sudungkynangvitriphudaudiem(self, idvitri_x, idvitri_y, x2, y2, khoangcachphudau, delay = 1):
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return False
        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return False
        diachi1 = self.get_diachicosothongtinnhanvat1()
        x1, y1 = self.get_toado(diachi1)
        deltax, deltay = x2 - x1, y2 - y1
        khoangcach = math.sqrt(deltax ** 2 + deltay ** 2)
        if khoangcach:
            deltax, deltay = deltax * khoangcachphudau / khoangcach, deltay * khoangcachphudau / khoangcach
        else:
            deltax, deltay = khoangcachphudau, khoangcachphudau
        targetx, targety = round(x1 + deltax), round(y1 + deltay)
        is_ok = self.action_sudungkynangtoado(idkynang, targetx, targety)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        return is_ok

    def get_is_damocuasotuychonnhanvatchinhlandau(self):
        x = read_int(self.tientrinh, self.diachixq + 0x3A642C)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0x2C)
        return False if x <= 10 else True

    def get_is_dangvankhi(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDE8)
        return read_int(self.tientrinh, x + 0xD8) == TRANGTHAIVANKHI_DANGVANKHI if x else False

    def get_is_dakhoitaothongtinbando(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0xADFDEC)
        return x > 0

    def action_tudongtimduong(self, x, y, idbando):
        a = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not a: return False
        a = read_int(self.tientrinh, a + 0xADFDEC)
        if not a:
            self.auto_assemble_khoitaothongtinbando()
            return False
        if read_int(self.tientrinh, a + 0x37C534) != x:
            write_int(self.tientrinh, a + 0x37C534, x)
        if read_int(self.tientrinh, a + 0x37C538) != y:
            write_int(self.tientrinh, a + 0x37C538, y)
        if read_int(self.tientrinh, a + 0x37C85C) != idbando:
            write_int(self.tientrinh, a + 0x37C85C, idbando)
        return True

    def action_ngungtudongtimduong(self):
        a = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        if not a:
            return False
        a = read_int(self.tientrinh, a + 0xADFDEC)
        if not a:
            self.auto_assemble_khoitaothongtinbando()
            return False
        if read_int(self.tientrinh, a + 0x37C534) != 0:
            write_int(self.tientrinh, a + 0x37C534, 0)
        if read_int(self.tientrinh, a + 0x37C538) != 0:
            write_int(self.tientrinh, a + 0x37C538, 0)
        if read_int(self.tientrinh, a + 0x37C85C) != 0:
            write_int(self.tientrinh, a + 0x37C85C, 0)
        return True

    def action_phucsinh(self, delay = 2.5):
        if time.time() - self._thoidiemphucsinhgannhat < delay or not self.get_is_nhanvatdachet():
            return False
        self._thoidiemphucsinhgannhat = time.time()
        self.action_thucthicaulenh("desc revive")
        time.sleep(1.)
        if self.get_is_danghiencuasotuychon():
            self.set_is_danghiencuasotuychon(False)
        return True

    def action_doimaupk(self, idmaupk, delay = 1.):
        if time.time() - self._thoidiemmaupkgannhat < delay or self.get_idmaupk() == idmaupk:
            return False
        is_ok = self.action_thucthicaulenh("set !attack {}".format(idmaupk))
        if is_ok:
            self.set_idmaupk(idmaupk)
            self._thoidiemmaupkgannhat = time.time()
        return is_ok

    def get_soluongvatphamhanhtrangtoida(self):
        return SOLUONGVATPHAMHANHTRANGTOIDA_MAP[self.get_idnguoichoi()]

    def action_timkiemvatphamhanhtrang(self, tenvatpham = None, is_ruongdautien = False, is_kiemtrahansudung = False):
        if not tenvatpham: return False
        i = -1
        soluongvatphamhanhtrangtoida = self.get_soluongvatphamhanhtrangtoida()
        if is_ruongdautien:
            soluongvatphamhanhtrangtoida = 24 - 1
        while True:
            if i >= soluongvatphamhanhtrangtoida: break
            i += 1
            if tenvatpham and self.get_tenvatphamhanhtrang(i) != tenvatpham:
                # if "Nhập môn" in self.get_tenvatphamhanhtrang(i):
                #    print(self.get_tenvatphamhanhtrang(i))
                continue
            if is_kiemtrahansudung:
                motavatpham = self.get_motavatphamhanhtrang(i)
                if "Hết hạn sử dụng" in motavatpham:
                    continue
            return self.get_iddoituongvatphamhanhtrang(i)
        return False

    def action_timkiemvitrivatphamhanhtrang(self, tenvatpham = None):
        if not tenvatpham:
            return False
        i = -1
        soluongvatphamhanhtrangtoida = self.get_soluongvatphamhanhtrangtoida()
        while True:
            if i >= soluongvatphamhanhtrangtoida: break
            i += 1
            if tenvatpham and self.get_tenvatphamhanhtrang(i) != tenvatpham:
                # if "Nhập môn" in self.get_tenvatphamhanhtrang(i):
                #    print(self.get_tenvatphamhanhtrang(i))
                continue
            return i
        return False

    def get_danhsachvatphamhanhtrang_map(self):
        i = -1
        vatphamhanhtrang_map = {}
        soluongvatphamhanhtrangtoida = self.get_soluongvatphamhanhtrangtoida()
        while True:
            if i >= soluongvatphamhanhtrangtoida: break
            i += 1
            tenvatphamxemxet = self.get_tenvatphamhanhtrang(i)
            if tenvatphamxemxet not in vatphamhanhtrang_map: vatphamhanhtrang_map[tenvatphamxemxet] = []
            vatphamhanhtrang_map[tenvatphamxemxet].append((i, self.get_iddoituongvatphamhanhtrang(i)))
        return vatphamhanhtrang_map

    def action_timkiemnhanvat(self, tennhanvat = None, idnguoichoi = None, iddoituong = None, tennhanvatchua = None, tenchunhan = None):
        if not tennhanvat and not idnguoichoi and not iddoituong and not tennhanvatchua and not tenchunhan: return False
        i = 0
        while True:
            diachi = self.get_diachicosothongtindoituongx(i)
            if not diachi: break
            i += 1
            if not self.get_is_nhanvattontai(diachi) or self.get_khoangcach(diachi) > KHOANGCACHTOANMANHINH: continue
            if tennhanvat and self.get_tendoituong(diachi) != tennhanvat: continue
            if idnguoichoi and self.get_idnguoichoi(diachi) != idnguoichoi: continue
            if iddoituong and self.get_iddoituong(diachi) != iddoituong: continue
            if tenchunhan:
                ten = self.get_tendoituong(diachi)
                if not ten or "({})".format(tenchunhan) not in ten: continue
            if tennhanvatchua:
                ten = self.get_tendoituong(diachi)
                if not ten or tennhanvatchua not in ten: continue
            return diachi
        return False

    def action_suavatpham(self, diachicosonhanvatthosuavatpham, delay = 1.):
        if time.time() - self._thoidiemsuavatphamgannhat < delay:
            return False
        idthosuavatpham = self.get_iddoituong(diachicosonhanvatthosuavatpham)
        if not idthosuavatpham:
            return False
        is_ok = self.action_thucthicaulenh("repair ! {}# all".format(hex(idthosuavatpham).replace("0x", "")), douutien = DOUUTIEN_THAP)
        if is_ok: self._thoidiemsuavatphamgannhat = time.time()
        return is_ok

    def action_sudungchucnangmorong5(self, delay = 2.5):
        if time.time() - self._thoidiemsudungchucnangmorong5 < delay:
            return False
        is_ok = self.action_thucthicaulenh("auto 5 1")
        if is_ok: self._thoidiemsudungchucnangmorong5 = time.time()
        return is_ok

    def get_idvukhi(self, diachi = None):
        return read_int(self.tientrinh, (diachi or self.get_diachicosothongtinnhanvat1()) + 0x1184)

    def set_idvukhi(self, idvukhi, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_idvukhi() != idvukhi: write_int(self.tientrinh, diachi + 0x1184, idvukhi)

    def get_idloaivukhi(self, diachi = None):
        return read_int(self.tientrinh, (diachi or self.get_diachicosothongtinnhanvat1()) + 0x1180)

    def set_idloaivukhi(self, idloaivukhi, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_idloaivukhi() != idloaivukhi: write_int(self.tientrinh, diachi + 0x1180, idloaivukhi)

    def get_idngoaitrang(self, diachi = None):
        return read_int(self.tientrinh, (diachi or self.get_diachicosothongtinnhanvat1()) + 0x1174)

    def set_idngoaitrang(self, idngoaitrang, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_idngoaitrang() != idngoaitrang: write_int(self.tientrinh, diachi + 0x1174, idngoaitrang)

    def get_idcanh(self, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachi + 0x119C), read_int(self.tientrinh, diachi + 0x11A0)

    def set_idcanh(self, idcanh, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_idcanh() != idcanh:
            write_int(self.tientrinh, diachi + 0x119C, idcanh[0])
            write_int(self.tientrinh, diachi + 0x11A0, idcanh[1])

    def get_mauvukhi(self, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        return read_short_int(self.tientrinh, diachi + 0xA4), read_short_int(self.tientrinh, diachi + 0xA5), read_short_int(self.tientrinh, diachi + 0xA6)

    def set_mauvukhi(self, mauvukhi, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_mauvukhi() != mauvukhi:
            write_short_int(self.tientrinh, diachi + 0xA4, mauvukhi[0])
            write_short_int(self.tientrinh, diachi + 0xA5, mauvukhi[1])
            write_short_int(self.tientrinh, diachi + 0xA6, mauvukhi[2])

    def get_maucanh(self, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        return (read_short_int(self.tientrinh, diachi + 0xA8), read_short_int(self.tientrinh, diachi + 0xA9), read_short_int(self.tientrinh, diachi + 0xAA),
                read_short_int(self.tientrinh, diachi + 0xB4), read_short_int(self.tientrinh, diachi + 0xB5), read_short_int(self.tientrinh, diachi + 0xB6))

    def set_maucanh(self, maucanh, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_maucanh() != maucanh:
            write_short_int(self.tientrinh, diachi + 0xA8, maucanh[0])
            write_short_int(self.tientrinh, diachi + 0xA9, maucanh[1])
            write_short_int(self.tientrinh, diachi + 0xAA, maucanh[2])
            write_short_int(self.tientrinh, diachi + 0xB4, maucanh[3])
            write_short_int(self.tientrinh, diachi + 0xB5, maucanh[4])
            write_short_int(self.tientrinh, diachi + 0xB6, maucanh[5])

    def get_mauyphuc(self, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        return read_short_int(self.tientrinh, diachi + 0xB0), read_short_int(self.tientrinh, diachi + 0xB1), read_short_int(self.tientrinh, diachi + 0xB2)

    def set_mauyphuc(self, mauyphuc, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_mauyphuc() != mauyphuc:
            write_short_int(self.tientrinh, diachi + 0xB0, mauyphuc[0])
            write_short_int(self.tientrinh, diachi + 0xB1, mauyphuc[1])
            write_short_int(self.tientrinh, diachi + 0xB2, mauyphuc[2])

    def get_mautoc(self, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        return read_short_int(self.tientrinh, diachi + 0xAC), read_short_int(self.tientrinh, diachi + 0xAD), read_short_int(self.tientrinh, diachi + 0xAE)

    def set_mautoc(self, mautoc, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_mautoc() != mautoc:
            write_short_int(self.tientrinh, diachi + 0xAC, mautoc[0])
            write_short_int(self.tientrinh, diachi + 0xAD, mautoc[1])
            write_short_int(self.tientrinh, diachi + 0xAE, mautoc[2])

    def get_is_vohieuhoadichuyen(self):
        return self._is_vohieuhoadichuyen

    def set_is_vohieuhoadichuyen(self, is_vohieuhoadichuyen):
        if self._is_vohieuhoadichuyen != is_vohieuhoadichuyen: self._is_vohieuhoadichuyen = is_vohieuhoadichuyen

    def get_is_dayhanhtrang(self):
        soluongvatphamhanhtrangtoida = self.get_soluongvatphamhanhtrangtoida()
        i = -1
        while True:
            if i >= soluongvatphamhanhtrangtoida:
                break
            i += 1
            if i % 10 == 0:
                time.sleep(0.001)
            if not self.get_iddoituongvatphamhanhtrang(i):
                return False
        return True

    def get_tenmonphai(self):
        return MONPHAI_MAP.get(self.get_idkynang(0, 0))

    def get_diachicosobaothugiangho(self):
        x = read_int(self.tientrinh, self.diachixq + OFFSET_DIACHICOSOTHONGTINGAME)
        return read_int(self.tientrinh, x + 0xADFDDC) if x else False

    def get_is_datrieuhoibaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        return read_boolean(self.tientrinh, diachi + 0x1AE8) if diachi else False

    def get_idkynangbaothugiangho(self, idvitri):
        diachi = self.get_diachicosobaothugiangho()
        return read_int(self.tientrinh, diachi + idvitri * 0x228 + 0x2E8) if diachi else False

    def get_tenkynangbaothugiangho(self, idvitri):
        diachi = self.get_diachicosobaothugiangho()
        return read_string(self.tientrinh, diachi + idvitri * 0x228 + 0x2EC) if diachi else False

    def get_is_kynangbaothugianghosansang(self, idvitri):
        diachi = self.get_diachicosobaothugiangho()
        return read_int(self.tientrinh, diachi + idvitri * 0x228 + 0x504) == 0 if diachi else False

    def get_iddoituongbaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        return read_int(self.tientrinh, diachi + 0x47C) if diachi else False

    def get_tendoituongbaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        return read_string(self.tientrinh, diachi + 0x4F5) if diachi else False

    def get_dotrungthanhbaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        return read_int(self.tientrinh, diachi + 0x4DC) if diachi else False

    def get_sinhlucconlaibaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        return read_int(self.tientrinh, diachi + 0x48C) if diachi else False

    def get_sinhluctoidabaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        return read_int(self.tientrinh, diachi + 0x490) if diachi else False

    def get_phantramsinhlucconlaibaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        if not diachi:
            return 100
        return self.get_sinhlucconlaibaothugiangho() * 100 / max(1, self.get_sinhluctoidabaothugiangho())

    def get_noilucconlaibaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        return read_int(self.tientrinh, diachi + 0x494) if diachi else False

    def get_noiluctoidabaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        return read_int(self.tientrinh, diachi + 0x498) if diachi else False

    def get_phantramnoilucconlaibaothugiangho(self):
        diachi = self.get_diachicosobaothugiangho()
        if not diachi:
            return 100
        return self.get_noilucconlaibaothugiangho() * 100 / max(1, self.get_noiluctoidabaothugiangho())

    def action_battheosaunhom(self, delay = 1.):
        if time.time() - self._thoidiembattattheosaunhomgannhat < delay:
            return False
        idnguoichoitruongnhom = self.get_idnguoichoitruongnhom()
        if not idnguoichoitruongnhom:
            return False
        is_ok = self.action_thucthicaulenh("team follow {}".format(idnguoichoitruongnhom))
        if is_ok: self._thoidiembattattheosaunhomgannhat = time.time()
        return is_ok

    def get_thoidiemsudungkynangvitrigannhat(self, idvitri_x, idvitri_y, macdinh = None):
        return self._thoidiemsudungkynangvitrigannhat_map.get((idvitri_x, idvitri_y), macdinh)

    def action_sudungkynangvitrimuctieu(self, idvitri_x, idvitri_y, diachicosothongtinnhanvatmuctieu = False, is_khongkiemtracothetancong = False, delay = 0.):
        if time.time() - self._thoidiemsudungkynanggannhat < 0.05:
            return False
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return False
        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return False
        diachi = diachicosothongtinnhanvatmuctieu if diachicosothongtinnhanvatmuctieu else self.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachi or (not is_khongkiemtracothetancong and not self.get_is_cothetancong(diachi)):
            return False
        is_ok = False
        if self.get_is_nguoichoi(diachi):
            idnguoichoi = self.get_idnguoichoi(diachi)
            is_ok = self.action_sudungkynangmuctieunguoichoi(idkynang, idnguoichoi)
        else:
            iddoituong = self.get_iddoituong(diachi)
            if iddoituong: is_ok = self.action_sudungkynangmuctieukhacnguoichoi(idkynang, iddoituong)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        return is_ok

    def action_sudungkynangvitri(self, idvitri_x, idvitri_y, delay = 0.):
        if time.time() - self._thoidiemsudungkynanggannhat < delay:
            return False
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return False
        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return False
        is_ok = self.action_sudungkynang(idkynang)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        return is_ok

    def action_sudungkynangvitrilenbanthan(self, idvitri_x, idvitri_y, delay = 0.):
        if time.time() - self._thoidiemsudungkynanggannhat < delay:
            return False
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return False
        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return False
        is_ok = self.action_sudungkynangmuctieunguoichoi(idkynang, self.get_idnguoichoi())
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        return is_ok

    def get_idlenhdichuyen(self):
        return read_int(self.tientrinh, self.diachixq + 0x380AFC)

    def set_idlenhdichuyen(self, idlenhdichuyen):
        write_int(self.tientrinh, self.diachixq + 0x380AFC, idlenhdichuyen)

    def action_ngatdichuyen(self):
        # if self.get_idlenhdichuyen() != 0:

        # if read_bytes(self.tientrinh, self.diachixq + 0x48789, 1) != bytes.fromhex("90"):
        #     write_bytes(self.tientrinh, self.diachixq + 0x48789, bytes.fromhex("90 90 90 90 90"), 5)

        self.set_idlenhdichuyen(0)
        self.action_ngungtudongtimduong()

    def action_nhatvatpham(self, diachi, delay = 0.05):
        if time.time() - self._thoidiemnhatvatphamgannhat < delay:
            return False
        if time.time() - self._thoidiemnhatvatphamgannhat_map.get(diachi, time.time() - 2.) < 0.4:
            return False
        x, y = self.get_toado(diachi, )
        if x <= 0 or y <= 0:
            return False
        self._thoidiemnhatvatphamgannhat = time.time()
        self._thoidiemnhatvatphamgannhat_map[diachi] = time.time()
        self.action_nhatvatphamtoado(x, y, delay = delay)
        return True

    def action_nhatvatphamxungquanh(self, delay = 0.05):
        if time.time() - self._thoidiemnhatvatphamgannhat < delay:
            return False
        self._thoidiemnhatvatphamgannhat = time.time()
        self.auto_assemble_nhatvatpham()
        return True

    def get_noidungtrochuyenmoinhat(self):
        if not hasattr(self, "_diachibodemnoidungtrochuyen"): return ""
        return read_string(self.tientrinh, self._diachibodemnoidungtrochuyen)
