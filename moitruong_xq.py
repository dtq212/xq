import ctypes
import queue
import re
import struct
import threading
import unicodedata
from dataclasses import dataclass, field

import pymem
from keystone import Ks, KS_ARCH_X86, KS_MODE_32

import diachi_xq
from dieuphoi_xq import is_lenhxoayvong
from diachi_xq import DC
from hangso_xq import *
from tienich_xq import *

# Thông tin túi hành trang: con trỏ tại [thông tin game] + 0xADFE0C (cạnh con trỏ hành trang + 0xADFD78),
# số ô mở của 4 túi là 4 int32 tại + 0xD4 (đo: túi đủ [24, 24, 24, 24], mới mở túi 2 loại 4 ô [24, 4, 0, 0])
OFFSET_DUNGLUONGTUIHANHTRANG = 0xD4
# Trong ô kỹ năng, tính từ chỗ chứa id (KN_ID): cờ đã học (3 = đã học, 0 = chưa học), xem MoiTruong.get_is_kynangdahoc
OFFSET_KYNANGDAHOC = 0x1C
# Bảng vị trí kỹ năng đã học đọc lại sau chừng này giây
THOIGIANNHOBANGKYNANG = 2.
# Bảng địa chỉ đối tượng xung quanh: các vòng quét đều chạy từ ô 0 tới ô 512 (hoặc gặp ô trống)
SOLUONGDOITUONGXUNGQUANHTOIDA = 513
# Tên đối tượng đọc lại trong khoảng này thì dùng bản vừa đọc (1 vòng chọn mục tiêu đọc tên cùng 1 đối tượng 5-6 lần)
THOIGIANNHOTENDOITUONG = 0.1

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
    # Lệnh dùng kỹ năng: ô kỹ năng, để lúc gửi vào game kiểm tra lại (đã vào hồi chiêu thì bỏ lệnh)
    vitrikynang: tuple = field(default = None, compare = False)


def tinh_is_huongmatvediem(x1, y1, huong, x2, y2, solechtoida = 1):
    # Đối tượng ở (x1, y1) quay mặt theo huong (8 hướng, ô +0x13F8) có trỏ về (x2, y2) không, lệch tối đa solechtoida hướng.
    # Đo trên quái đang ra đòn: huong = round((225 - goc) / 45) mod 8, goc = atan2(y2 - y1, x2 - x1) theo tọa độ ô (y hướng xuống)
    if (x1, y1) == (x2, y2):
        return True
    goc = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 360
    huongdukien = round((225 - goc) / 45) % 8
    lech = (huong - huongdukien) % 8
    return min(lech, 8 - lech) <= solechtoida


class MoiTruong:
    def __init__(self, idcuaso):
        self._is_dasetupautoassemblethucthicaulenh2 = False
        self._thoidiemthucthicaulenh2gannhat = 0.
        # Lệnh trực tiếp dùng chung 1 vùng nhớ chứa câu lệnh trong game: nhiều luồng gửi cùng lúc thì ghi đè lệnh của nhau
        self._khoathucthicaulenh2 = threading.Lock()
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
        # Địa chỉ trong xq.exe (DC.<tên>, tính từ base) dò bằng chữ ký trên file xq.exe (1 lần cho mọi cửa sổ, có lưu đệm)
        diachi_xq.khoitao(xqmodule.filename)

        kichthuoccuaso = win32gui.GetWindowRect(self.idcuaso)
        if not kichthuoccuaso:
            raise Exception("Lấy kích thước cửa sổ game không thành công")

        self._kichthuoccuasogame = 800, 600

        # Đoạn mã gọi hàm tìm đường cục bộ của client (_get_chuoihuongtimduongcucbo): địa chỉ mã, ô tham số, bộ đệm chuỗi hướng
        self._diachitimduongcucbo = None
        # Luồng di chuyển và lệnh tự đề xuất lộ trình cùng gọi hàm tìm đường cục bộ (chung ô tham số / bộ đệm trong game)
        self._khoatimduongcucbo = threading.Lock()
        # Lần gửi "desc pf <id>" gần nhất theo id kỹ năng (get_tieuhaokynang)
        self._thoidiemtruyvanmotakynang_map = {}
        # id kỹ năng -> (thời điểm đọc, tiêu hao hoặc None): hàm ra chiêu xét tiêu hao mỗi lượt cho mọi chiêu nên nhớ lại một lúc
        self._tieuhaokynang_cache = {}
        # Bảng {id kỹ năng đã học: vị trí} (_get_bangvitrikynangdahoc) và lúc đọc
        self._bangvitrikynangdahoc = {}
        self._thoidiemdocbangkynang = 0.
        # Đích đi theo ô gần nhất (action_dichuyenoo): còn đang đi tới đích này thì không ghi lại chuỗi
        self._dichdioogannhat = None
        self._dulieutimduongcucbo = None
        self._buftimduongcucbo = None
        self._is_dasetupautoassemblenhatvatpham = False
        self._is_dasetupautoassemblekhoitaothongtinbando = False
        self._is_dasetupactionthietlaphooknoidungtrochuyen = False

        self._thoidiemdichuyengannhat = 0.
        self._thoidiemhetchovankhi = 0.
        # Khoá vận khí triệu hồi bảo thú (action_khoavankhitrieuhoi): None hoặc {"batdau", "toida", "caulenhduocpheps"}
        self._khoavankhitrieuhoi = None
        # Đang spam lệnh triệu hồi bảo thú (pf 4131.@) => không cho dùng kỹ năng nào khác tới thời điểm này
        self._thoidiemhetkhoakynang = 0.
        self._thoidiemlogkhoakynanggannhat = 0.
        # Chống spam kỹ năng không mục tiêu: {id kỹ năng: [thời điểm gửi gần đây]} và {id kỹ năng: thời điểm hết tạm khoá}
        self._thoidiemguikynangkhongmuctieu_map = {}
        self._thoidiemhetkhoaspamkynang_map = {}
        self._vitrikynangdalog = set()
        # Lịch sử vị trí mục tiêu đang đuổi theo (để tính hướng/tốc độ chạy mà click đón đầu)
        self._lichsutoadomuctieu_map = {}
        self._thoidiemsudungkynangvitrigannhat_map = {}
        self._thoidiemsudungkynanggannhat = 0.
        self._thoidiemnhatvatphamgannhat = 0.
        self._thoidiemnhatvatphamgannhat_map = {}
        self._thoidiemthucthicaulenhgannhat = 0.
        self._thoidiemsudungtancongvatlygannhat = 0.
        self._thoidiemthaotacnhomgannhat = 0.
        self._thoidiemphucsinhgannhat = 0.
        self._thoidiemdongcuasosauphucsinh = 0.
        self._thoidiemmaupkgannhat = 0.
        self._thoidiemsuavatphamgannhat = 0.
        self._thoidiemsudungchucnangmorong5 = 0.
        self._thoidiemtuthenhanvatdungimgannhat = 0.
        self._thoidiemtuthenhanvattanconggannhat = 0.
        # Lần cuối còn thấy tư thế xuất chiêu (get_is_dangxuatchieu): chặn di chuyển thêm THOIGIANKHUNGSAUXUATCHIEU giây sau mốc này
        self._thoidiemxuatchieugannhat = 0.
        # Chiêu bot gửi gần nhất có cần đứng yên lúc ra đòn không (is_ngatdichuyen trong danh sách kỹ năng); chiêu ra sát thương ngay
        # (Đại Hải Vô Lượng, Ba Động Quyền...) thì tư thế xuất chiêu của nó không chặn di chuyển
        self._is_chieucanngatdichuyen = True
        # Có giữ thêm THOIGIANKHUNGSAUXUATCHIEU giây khựng sau tư thế xuất chiêu không (chiêu lướt Khai Thiên Tịch Địa: chỉ giữ hoạt ảnh)
        self._is_khungsauxuatchieu = True
        # Mục tiêu của chiêu đó (địa chỉ, id lúc gửi): mục tiêu đã chết / biến mất thì thôi chặn di chuyển ngay
        self._diachimuctieuxuatchieu = None
        self._idmuctieuxuatchieu = None
        # Số bay của mục tiêu lúc gửi chiêu (_docsobaydoituong) và đã thấy số bay mới chưa (chiêu đã trúng): thả khựng sớm
        self._sobaymuctieuxuatchieu = None
        self._is_datrungchieu = False
        self._thoidiemtuthenhanvatdungimcomuctieugannhat = 0.
        self._thoidiemtuthenhanvatkhongdichuyengannhat = 0.
        # Theo từng bảo thú (Mao Sơn có thể có nhiều bảo thú triệu hồi cùng lúc, dùng chung một mốc thì con sau bị chặn lệnh)
        self._thoidiemralenhbaothutancong_map = {}
        self._thoidiemralenhbaothutheosau_map = {}
        # id bảo thú -> lệnh cuối bot đã ra (1 tấn công, 2 theo sau, 3 dừng im): biết bảo thú đang theo sau để khỏi gọi lại mãi
        self._lenhbaothugannhat_map = {}
        # id bảo thú -> (địa chỉ đối tượng trong danh sách xung quanh, lúc tìm) (_get_diachidoituongbaothu)
        self._diachidoituongbaothu_map = {}
        self._thoidiemralenhbaothudungim = 0.

        self._idthucuoi = False
        self._thoidiemkhongcuoithugannhat = 0.
        self._is_tamngungtancong = False
        self._is_vohieuhoadichuyen = False
        self._thoidiemkhongcomuctieugannhat = 0.
        # Lúc bắt đầu giữ chuột trái (0 = không giữ) và lần gần nhất thấy đã giữ đủ lâu trên cửa sổ game (get_is_dangclickchuottrai)
        self._thoidiembatdaugiuchuottrai = 0.
        self._thoidiemgiuchuottraigannhat = 0.

        self._soluonghieuungnhanvattruocdo_map = {}
        self._thoidiemsoluonghieuungbangkhonggannhat_map = {}
        # {vị trí trong bảng hiệu ứng của game: id hiệu ứng} (bảng tĩnh trong xq.exe, đọc 1 lần là đủ)
        self._idhieuungtheovitri_map = {}
        # Ảnh chụp bảng địa chỉ đối tượng xung quanh, chụp lại mỗi khi một vòng quét bắt đầu từ ô 0
        self._bangdiachidoituongs = ()
        # {địa chỉ đối tượng: (thời điểm đọc, tên)}
        self._tendoituong_map = {}
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
        # Tác tử đồng bộ theo tùy chọn tránh vùng cấm: mọi di chuyển không được cắt qua vùng cấm
        self.is_tranhvungcam = True
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
        self._is_nhanvatbibatdong = False
        self._is_nhanvatbitrammac = False
        self._is_nhanvatbimongdu = False
        self._is_nhanvatbibienthan = False
        # địa chỉ đối tượng -> (thời điểm đọc, (số lượng, [(id, có lợi, thời gian)])), xem THOIGIANNHOBANGHIEUUNG
        self._banghieuung_cache = {}
        # Tâm Trận Pháp Lạc Ảnh đang giữ mình (người dùng chiêu, xem _timtamtrandolacanh), None khi không bị giữ
        self._toadotrandolacanh = None

        self.diachihamthucthicaulenh = 0

        self.hangdoicaulenh = queue.PriorityQueue()
        self.caulenhdangchos = set()
        # Ô đích click di chuyển đã log gần nhất (IS_LOGDICHUYEN: chỉ log khi đổi ô)
        self._dichclicklogcuoi = None
        # Bộ chia lượt gửi lệnh / bắt đầu di chuyển giữa các bot (CuaSo gán vào), None thì làm ngay như cũ
        self.dieuphoi = None
        self.dieuphoidichuyen = None
        # Giữ chỗ chiêu khống chế trên mục tiêu giữa các bot (GiuKyNangMucTieu, CuaSo gán vào), None thì không giữ
        self.giukynang = None

        self.thoidiemmuctieuanthangannhat_map = {}
        self.thoidiemmuctieuxuathiengannhat_map = {}

        self.thoidiembaothuxuathiengannhat_map = {}

        self._lichsutrochuyen5s = []
        # Bộ đếm dòng của bộ đệm vòng trò chuyện (action_thietlaphooknoidungtrochuyen) đã đọc tới đâu
        self._demdongtrochuyendadoc = 0

        self._diachiautoassemblenhatvatpham = False
        self._diachiautoassemblekhoitaothongtinbando = False

        self._diachibodemnoidungtrochuyen = False
        self._diachihamkichbannoidungtrochuyen = False

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
        if getattr(self, "_diachitimduongcucbo", None):
            safe_free(self._diachitimduongcucbo)

    def _ghilenhvaobonho(self, lenh):
        if not self.diachihamthucthicaulenh:
            self.khoitaohamthucthicaulenh()

        if self.diachihamthucthicaulenh:
            if self._is_lenhkynangdavaohoichieu(lenh):
                return
            # Lệnh vào hàng đợi trước khi khoá vận khí triệu hồi mà tới giờ mới gửi: bỏ (vòng lặp sau tự gửi lại nếu còn cần)
            if self._is_lenhbichankhoavankhi(lenh.caulenh):
                self._loglenh(lenh.caulenh, "bỏ: đang khoá vận khí triệu hồi")
                return
            # Lệnh chiêu / đánh vào hàng đợi trước khi bị choáng (hoặc Trầm Mặc với phái phép thuật) mà tới giờ mới gửi: bỏ, hết khống chế vòng lặp tự gửi lại
            if (lenh.caulenh.startswith("pf ") and self.get_is_khongthedungkynang()) or (lenh.caulenh.startswith("kill ") and self._is_nhanvatbichoang):
                self._loglenh(lenh.caulenh, "bỏ: đang bị khống chế")
                return
            self._loglenh(lenh.caulenh, f"hàng đợi, ưu tiên {lenh.douutien}")
            diachidulieu = self.diachihamthucthicaulenh + 0x40
            chuoi_bytes = lenh.caulenh.encode("utf-8")

            write_int(self.tientrinh, diachidulieu, len(chuoi_bytes))
            write_bytes(self.tientrinh, diachidulieu + 4, chuoi_bytes + b"\x00", len(chuoi_bytes) + 1)

            self.tientrinh.start_thread(self.diachihamthucthicaulenh)
            if lenh.trihoansaulenh > 0.:
                time.sleep(lenh.trihoansaulenh)

    def _is_lenhkynangdavaohoichieu(self, lenh):
        # Lệnh dùng kỹ năng nằm chờ mà kỹ năng đó đã vào hồi chiêu (lệnh trước đã ra chiêu) => gửi cũng vô ích, bỏ
        if not lenh.vitrikynang or self.get_is_kynangsansang(lenh.vitrikynang):
            return False
        self._loglenh(lenh.caulenh, "BỎ - kỹ năng đã vào hồi chiêu")
        return True

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

    def _is_chuatoiluotlenh(self, caulenh = None, is_khancap = False):
        # Chiêu có mục tiêu chia lượt theo thời gian giữa các nhân vật: chưa tới lượt nhân vật này thì không gửi (vòng lặp tự gửi lại khi
        # tới lượt). caulenh None: lệnh chiêu có mục tiêu sắp tạo (gọi sớm, trước bộ đếm chống spam)
        if not self.dieuphoi or (caulenh is not None and not is_lenhxoayvong(caulenh)) or (is_khancap and IS_LENHKHANCAPKHONGCHOLUOT):
            return False
        return not self.dieuphoi.thugiuluot()

    def get_is_batxoayvongchieu(self):
        # Đang bật xoay vòng chiêu có mục tiêu giữa các nhân vật (giao diện > Nhịp lệnh): phái có chiêu không mục tiêu thay được thì dùng chiêu đó
        return bool(self.dieuphoi) and self.dieuphoi.get_is_batxoayvong()

    def action_baogiuluotkhixuatchieu(self):
        # Đang xuất chiêu thì bot không gửi gì: báo vẫn đang dùng lượt để không bị nhường mất giữa 2 chiêu
        if self.dieuphoi and self.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT):
            self.dieuphoi.baogiuluot()

    def action_thucthicaulenh(self, caulenh, douutien = DOUUTIEN_TRUNGBINH, vitrikynang = None):
        if self._is_lenhbichankhoavankhi(caulenh):
            return False
        if self._is_chuatoiluotlenh(caulenh, douutien == DOUUTIEN_KHANCAP):
            return False
        if caulenh in self.caulenhdangchos:
            return False

        self.caulenhdangchos.add(caulenh)

        lenhthucthi = LenhThucThi(
            douutien = douutien,
            thoigiantao = time.time(),
            caulenh = caulenh,
            trihoansaulenh = 0.00,
            vitrikynang = vitrikynang,
        )
        self.hangdoicaulenh.put(lenhthucthi)
        self._thoidiemthucthicaulenhgannhat = time.time()
        return True

    def action_thucthicaulenh2(self, caulenh, delay = 0.05, is_khancap = False):
        # is_khancap: gửi ngay không chờ lượt chia giữa các nhân vật
        if self._is_lenhbichankhoavankhi(caulenh):
            return False
        if time.time() - self._thoidiemthucthicaulenh2gannhat < delay:
            return False
        if self._is_chuatoiluotlenh(caulenh, is_khancap):
            return False
        self._thoidiemthucthicaulenh2gannhat = time.time()
        with self._khoathucthicaulenh2:
            return self._thucthicaulenh2(caulenh)

    def _thucthicaulenh2(self, caulenh):
        self._loglenh(caulenh, "trực tiếp")

        diachihampheduyetcaulenh = self.diachixq + DC.HAMPHEDUYETCAULENH
        if read_bytes(self.tientrinh, diachihampheduyetcaulenh, 1) == b"\x74":
            write_bytes(self.tientrinh, diachihampheduyetcaulenh, b"\xEB", 1)

        if not self._is_dasetupautoassemblethucthicaulenh2:
            self.diachihamthucthicaulenh2 = self.tientrinh.allocate(128)

            write_bytes(self.tientrinh, self.diachihamthucthicaulenh2, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self.diachihamthucthicaulenh2 + 1, len(caulenh.encode("utf-8")))

            write_bytes(self.tientrinh, self.diachihamthucthicaulenh2 + 5, bytes.fromhex("68"), 1)
            write_int(self.tientrinh, self.diachihamthucthicaulenh2 + 6, self.diachihamthucthicaulenh2 + 19)

            write_bytes(self.tientrinh, self.diachihamthucthicaulenh2 + 10, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachihamthucthicaulenh2 + 11, self.diachixq + DC.HAMGUILENH - (self.diachihamthucthicaulenh2 + 10) - 5)

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
        if time.time() - self._thoidiemralenhbaothutancong_map.get(iddoituongbaothu, 0.) < delay:
            return False
        self._thoidiemralenhbaothutancong_map[iddoituongbaothu] = time.time()
        self._thoidiemralenhbaothutancong_map = donbangthoidiem(self._thoidiemralenhbaothutancong_map, 120.)
        caulenh = f"pet {hex(iddoituongbaothu)}# 1 {hex(iddoituongnhanvatmuctieudangchon)}#".replace("0x", "")
        if not self.action_thucthicaulenh2(caulenh, delay = 0.):
            return False
        self._ghilenhbaothu(iddoituongbaothu, 1)
        return True

    def _ghilenhbaothu(self, iddoituongbaothu, lenh):
        if len(self._lenhbaothugannhat_map) > 64:
            self._lenhbaothugannhat_map.clear()
        self._lenhbaothugannhat_map[iddoituongbaothu] = lenh

    def get_is_baothudangtheosau(self, iddoituongbaothu):
        # Lệnh cuối bot ra cho bảo thú này là theo sau (chưa bị lệnh tấn công / dừng im thay)
        return self._lenhbaothugannhat_map.get(iddoituongbaothu) == 2

    def action_ralenhbaothutheosau(self, iddoituongbaothu, delay = 0.25):
        if time.time() - self._thoidiemralenhbaothutheosau_map.get(iddoituongbaothu, 0.) < delay:
            return False
        self._thoidiemralenhbaothutheosau_map[iddoituongbaothu] = time.time()
        self._thoidiemralenhbaothutheosau_map = donbangthoidiem(self._thoidiemralenhbaothutheosau_map, 120.)
        caulenh = f"pet {hex(iddoituongbaothu)}# 2".replace("0x", "")
        if not self.action_thucthicaulenh2(caulenh, delay = 0.):
            return False
        self._set_trangthaihanhvibaothu(iddoituongbaothu, 2)
        self._ghilenhbaothu(iddoituongbaothu, 2)
        return True

    def action_ralenhbaothudungim(self, iddoituongbaothu, delay = 0.25):
        if time.time() - self._thoidiemralenhbaothudungim < delay:
            return False
        self._thoidiemralenhbaothudungim = time.time()
        caulenh = f"pet {hex(iddoituongbaothu)}# 3".replace("0x", "")
        if not self.action_thucthicaulenh2(caulenh, delay = 0.):
            return False
        self._set_trangthaihanhvibaothu(iddoituongbaothu, 3)
        self._ghilenhbaothu(iddoituongbaothu, 3)
        return True

    def _set_trangthaihanhvibaothu(self, iddoituongbaothu, trangthai):
        # Lệnh gõ chỉ gửi lên server, không như chuột phải vào nút Theo sau / Chờ đợi (xq.exe gửi cùng lệnh rồi ghi ô +0x1E0
        # = 2 / 3, vòng sáng vẽ theo ô này) => tự ghi. Vòng sáng kẹt ở Chờ đợi còn làm sang bản đồ mới client không cập nhật
        # bản đồ của bảo thú (+0x1E4, chỉ cập nhật khi +0x1E0 == 2) => tưởng bảo thú ở bản đồ khác mà gọi về mãi
        # Chuột phải nút Tấn công trong game không làm gì nên lệnh tấn công không ghi
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return
        for sothutu in range(3):
            diachi = x + 0x184 + 0x6C * sothutu
            if read_int(self.tientrinh, diachi) == iddoituongbaothu:
                if read_int(self.tientrinh, diachi + 0x1E0 - 0x184) != trangthai:
                    write_int(self.tientrinh, diachi + 0x1E0 - 0x184, trangthai)
                return

    def action_batchucnangmorong(self, delay = 5.):
        if self.get_is_dangbatchucnangmorong():
            return False

        if time.time() - self.thoidiembatchucnangmoronggannhat < delay:
            return False

        self.thoidiembatchucnangmoronggannhat = time.time()

        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        a = read_int(self.tientrinh, x + DC.TG_CHUCNANGMORONG)
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
        # "get x y" chỉ nhặt tại chỗ (không chạy tới vật phẩm) => không ngắt vận khí, không cắt chiêu đang xuất
        self._thoidiemnhatvatphamtoadogannhat = time.time()
        caulenh = "get {} {}".format(toadox, toadoy)
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

    def action_khaikhoang(self, iddoituong, delay = 0.05):
        if time.time() - self._thoidiemkhaikhoanggannhat < delay:
            return False
        self._thoidiemkhaikhoanggannhat = time.time()
        caulenh = "look {}#".format(hex(iddoituong)).replace("0x", "")
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

    def action_khoakynang(self, thoigian):
        self._thoidiemhetkhoakynang = max(self._thoidiemhetkhoakynang, time.time() + thoigian)

    def action_mokhoakynang(self):
        self._thoidiemhetkhoakynang = 0.

    def get_is_dangkhoakynang(self):
        is_dangkhoa = time.time() < self._thoidiemhetkhoakynang
        # Log tối đa 1 lần/giây để biết kỹ năng đang bị khoá chặn (và còn khoá bao lâu)
        if is_dangkhoa and IS_LOGCAULENH and time.time() - self._thoidiemlogkhoakynanggannhat > 1.:
            self._thoidiemlogkhoakynanggannhat = time.time()
            self._inlog(f"[KHOÁ KỸ NĂNG] chặn dùng kỹ năng, còn khoá {round(self._thoidiemhetkhoakynang - time.time(), 2)}s")
        return is_dangkhoa

    def _inlog(self, noidung):
        # In ra console và ghi file _internal/log/<ID người chơi>.log; tiền tố là ID người chơi (cố định), chưa đọc được thì dùng mã cửa sổ
        try:
            idnguoichoi = self.get_idnguoichoi()
        except Exception:
            idnguoichoi = 0
        dong = f"[{time.strftime('%H:%M:%S')}.{int(time.time() * 1000) % 1000:03d} {idnguoichoi or f'cửa sổ {self.idcuaso}'}] {noidung}"
        print(dong)
        ghilognhanvat(idnguoichoi or f"cuaso_{self.idcuaso}", dong)

    def _loglenh(self, caulenh, nguon):
        if IS_LOGCAULENH:
            self._inlog(f"[LỆNH {nguon}] {caulenh}")

    def get_thoidiemlenhdanhgannhat(self):
        # Lần gửi kỹ năng gần nhất. "kill" chỉ là yêu cầu máy chủ bắt đầu đánh thường (không phải chiêu / đòn đánh, không ra ngay) nên
        # không tính: gửi kill xong vẫn gửi chiêu được ngay
        return self._thoidiemsudungkynanggannhat

    def get_is_kynangdangbikhoa(self, idkynang):
        # Đang khoá mọi kỹ năng hoặc riêng kỹ năng này đang bị khoá chống spam: gửi lúc này chắc chắn không đi (không log)
        thoidiemhientai = time.time()
        return thoidiemhientai < self._thoidiemhetkhoakynang or thoidiemhientai < self._thoidiemhetkhoaspamkynang_map.get(idkynang, 0.)

    def _is_kynangbispam(self, idkynang):
        # Không kỹ năng nào cần gửi dồn dập (chiêu nào cũng có hồi chiêu >= 1s): game báo "sẵn sàng" mà kỹ năng không ra (bị khống chế
        # mà bot chưa biết hiệu ứng như mộng du, mục tiêu đặc biệt...) thì trước đây cứ gửi lại mỗi lượt (Cam Lộ Trì 625 lần / 3 phút làm
        # server đơ), ngập hàng đợi lệnh khiến các kỹ năng khác không chen vào được. Áp cho cả kỹ năng có mục tiêu
        if idkynang in IDKYNANGKHONGCHANSPAMs:
            return False
        thoidiemhientai = time.time()
        if thoidiemhientai < self._thoidiemhetkhoaspamkynang_map.get(idkynang, 0.):
            return True
        thoidiemguis = [t for t in self._thoidiemguikynangkhongmuctieu_map.get(idkynang, []) if thoidiemhientai - t < SOGIAYDEMSPAMKYNANG]
        if len(thoidiemguis) >= SOLANGUITOIDASPAMKYNANG:
            self._thoidiemhetkhoaspamkynang_map[idkynang] = thoidiemhientai + THOIGIANKHOASPAMKYNANG
            self._thoidiemguikynangkhongmuctieu_map[idkynang] = []
            # Ghi kèm hiệu ứng đang có trên người để tìm ra khống chế nào làm kỹ năng không ra
            hieuungs = [(idhieuung, is_coloi) for idhieuung, is_coloi, _ in self.get_danhsachhieuungnhanvats()]
            self._inlog(f"[CHẶN SPAM] kỹ năng {idkynang} gửi {len(thoidiemguis)} lần trong {SOGIAYDEMSPAMKYNANG}s mà vẫn sẵn sàng => tạm khoá {THOIGIANKHOASPAMKYNANG}s | hiệu ứng (id, có lợi): {hieuungs}")
            return True
        thoidiemguis.append(thoidiemhientai)
        self._thoidiemguikynangkhongmuctieu_map[idkynang] = thoidiemguis
        return False

    def action_sudungkynang(self, idkynang, delay = 0.05, vitrikynang = None):
        if self.get_is_dangkhoakynang() or self.get_is_khongthedungkynang():
            return False
        if time.time() - self._thoidiemsudungkynanggannhat < delay:
            return False
        caulenh = "pf {}".format(idkynang)
        # Chờ lượt xét trước bộ đếm chống spam: lần chưa tới lượt không tính là 1 lần gửi
        if self._is_chuatoiluotlenh(caulenh) or self._is_kynangbispam(idkynang):
            return False
        self._thoidiemsudungkynanggannhat = time.time()
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO, vitrikynang = vitrikynang)

    def action_sudungtancongvatly(self, diachicosothongtinnhanvatmuctieu, delay = 0.):
        if self._is_nhanvatbichoang:
            return False
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

    def action_sudungkynangmuctieunguoichoi(self, idkynang, idnguoichoi, delay = 0.05, vitrikynang = None):
        if self.get_is_dangkhoakynang() or self.get_is_khongthedungkynang():
            return False
        if time.time() - self._thoidiemsudungkynangmuctieugannhat < delay:
            return False
        if self._is_chuatoiluotlenh() or self._is_kynangbispam(idkynang):
            return False
        self._thoidiemsudungkynangmuctieugannhat = time.time()
        caulenh = "pf {} {}".format(idkynang, idnguoichoi)
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO, vitrikynang = vitrikynang)

    def action_sudungkynangmuctieukhacnguoichoi(self, idkynang, iddoituong, delay = 0.05, vitrikynang = None):
        if self.get_is_dangkhoakynang() or self.get_is_khongthedungkynang():
            return False
        if time.time() - self._thoidiemsudungkynangmuctieugannhat < delay:
            return False
        if self._is_chuatoiluotlenh() or self._is_kynangbispam(idkynang):
            return False
        self._thoidiemsudungkynangmuctieugannhat = time.time()
        caulenh = "pf {} {}#".format(idkynang, hex(iddoituong)).replace("0x", "")
        return self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO, vitrikynang = vitrikynang)

    def action_sudungkynangtoado(self, idkynang, toadox, toadoy, delay = 0.05):
        if self.get_is_dangkhoakynang() or self.get_is_khongthedungkynang():
            return False
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

    def action_dichuyenvatphamsanghanhtrangkhac(self, iddoituong, vitri, delay = 0.4, is_guingay = False):
        # is_guingay: gửi thẳng vào game, không qua hàng đợi lệnh / chờ lượt (cần nhanh, vd giữ ô trống khi đang chế đồ)
        if time.time() - self._thoidiemdichuyenvatphamsanghanhtrangkhacgannhat < delay:
            return False
        self._thoidiemdichuyenvatphamsanghanhtrangkhacgannhat = time.time()
        caulenh = "move {}# to {}".format(hex(iddoituong), vitri).replace("0x", "")
        if is_guingay:
            return self.action_thucthicaulenh2(caulenh, delay = 0., is_khancap = True)
        return self.action_thucthicaulenh(caulenh)

    def action_trochuyenvoinpc(self, iddoituong, noidungtrochuyen, delay = 0.2, caulenhtrochuyen = "tallk"):
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
        # Nhặt toàn bộ vật phẩm xung quanh tại chỗ (như "get x y" nhưng không theo 1 toạ độ): không di chuyển => không ngắt vận khí, không cắt chiêu
        if not self._is_dasetupautoassemblenhatvatpham:
            self._diachiautoassemblenhatvatpham = self.tientrinh.allocate(64)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatvatpham, bytes.fromhex("8B 0D"), 2)
            write_int(self.tientrinh, self._diachiautoassemblenhatvatpham + 2, self.diachixq + DC.THONGTINGAME)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatvatpham + 6, bytes.fromhex("8D 59 14"), 3)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatvatpham + 9, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self._diachiautoassemblenhatvatpham + 10, self.diachixq + DC.HAMNHATVATPHAM - (self._diachiautoassemblenhatvatpham + 9) - 5)
            write_bytes(self.tientrinh, self._diachiautoassemblenhatvatpham + 14, bytes.fromhex("C3"), 1)
            self._is_dasetupautoassemblenhatvatpham = True
        self.tientrinh.start_thread(self._diachiautoassemblenhatvatpham)

    def auto_assemble_khoitaothongtinbando(self):
        # Cấu trúc tìm đường / bản đồ [thông tin game] + 0xADFDEC (đích tìm đường + 0x37C534, bản đồ + 0x37C85C) game chỉ tạo khi cần,
        # 1 lần mỗi phiên đăng nhập (đặt về 0 duy nhất ở xq + 0x3755F lúc khởi tạo thông tin game, đổi bản đồ vẫn giữ).
        # Trước đây gọi hàm phím tắt xq + 0x3C100 (phím mở bản đồ 0x64): tạo cấu trúc rồi bật / tắt cửa sổ bản đồ => bản đồ hiện lên.
        # Nay làm như game tự làm ở xq + 0x225D0 / 0x22A51 (luồng tìm đường): cấp phát 0x37C868 byte (new, xq + 0x17DD0C), gọi hàm khởi
        # tạo xq + 0xCEEB0 (trả về this) rồi gán vào [thông tin game] + 0xADFDEC, không đụng tới cửa sổ bản đồ
        if not self._is_dasetupautoassemblekhoitaothongtinbando:
            self._diachiautoassemblekhoitaothongtinbando = self.tientrinh.allocate(128)
            addr_base_ptr = self.diachixq + DC.THONGTINGAME
            asm_script = f"""
                mov eax, dword ptr [{hex(addr_base_ptr)}]
                test eax, eax
                je ketthuc
                cmp dword ptr [eax + {hex(DC.TG_TIMDUONG)}], 0
                jne ketthuc
                push 0x37C868
                mov eax, {hex(self.diachixq + DC.HAMCAPPHAT)}
                call eax
                add esp, 4
                test eax, eax
                je ketthuc
                mov ecx, eax
                mov eax, {hex(self.diachixq + DC.HAMKHOITAOTIMDUONG)}
                call eax
                mov ecx, dword ptr [{hex(addr_base_ptr)}]
                cmp dword ptr [ecx + {hex(DC.TG_TIMDUONG)}], 0
                jne ketthuc
                mov dword ptr [ecx + {hex(DC.TG_TIMDUONG)}], eax
            ketthuc:
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
        addr_at_hook = self.diachixq + DC.HOOK_TROCHUYEN
        addr_return = self.diachixq + DC.HOOK_TROCHUYEN + 6

        if not self._is_dasetupactionthietlaphooknoidungtrochuyen:
            # Bộ đệm vòng: [+0] bộ đếm số dòng đã ghi, rồi SOLUONGDONGTROCHUYEN ô x KICHTHUOCDONGTROCHUYEN byte. Trước đây chỉ 1 ô, dòng sau
            # đè dòng trước nên nhiều tin trong cùng 1 vòng làm mới (dame, nhặt đồ, bảo thú...) thì bot chỉ thấy tin cuối
            self._diachibodemnoidungtrochuyen = self.tientrinh.allocate(4 + SOLUONGDONGTROCHUYEN * KICHTHUOCDONGTROCHUYEN)
            write_int(self.tientrinh, self._diachibodemnoidungtrochuyen, 0)
            self._diachihamkichbannoidungtrochuyen = self.tientrinh.allocate(256)

            ks = Ks(KS_ARCH_X86, KS_MODE_32)

            # Chép dòng (ebp) vào ô [bộ đếm % số ô], chép xong mới tăng bộ đếm để bot không đọc ô đang chép dở
            asm_script = f"""
                pushad
                mov ebx, {self._diachibodemnoidungtrochuyen}
                mov eax, dword ptr [ebx]
                and eax, {SOLUONGDONGTROCHUYEN - 1}
                imul eax, eax, {KICHTHUOCDONGTROCHUYEN}
                lea edi, [ebx + eax + 4]
                mov esi, ebp
                mov ecx, {KICHTHUOCDONGTROCHUYEN - 1}
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
                inc dword ptr [ebx]
                popad
                mov ecx, [edx + {hex(DC.TG_TROCHUYEN)}]
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
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_SINHLUC) if x else False

    def get_sinhluctoida(self):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_SINHLUCTOIDA) if x else False

    def get_noilucconlai(self):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_NOILUC) if x else False

    def get_noiluctoida(self):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_NOILUCTOIDA) if x else False

    def get_thelucconlai(self):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_THELUC) if x else False

    def get_nganluong(self):
        # Ngân lượng mang theo (khung Hành Trang), None khi chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_NGANLUONG) if x else None

    def get_tiengui(self):
        # Tiền gửi trong kho (Quản Khố), None khi chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_TIENGUI) if x else None

    def get_kinhnghiem(self):
        # Kinh nghiệm hiện có (chặn tăng cấp thì cứ cộng dồn, lên cấp thì bị trừ đi), None khi chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_KINHNGHIEM) if x else None

    def get_soluongvatphamhanhtrangtheoten(self):
        # {tên: tổng số lượng} của cả hành trang trong 2 lần đọc; món không xếp chồng (số lượng 0) tính là 1
        soluongo = self.get_soluongvatphamhanhtrangtoida() + 1
        tens = self._docdanhsachtenvatphamhanhtrang(soluongo)
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x or len(tens) != soluongo:
            return None
        soluongs = struct.unpack("<%di" % soluongo, read_bytes(self.tientrinh, x + DC.HT_SOLUONG, soluongo * 4))
        ketqua = {}
        for ten, soluong in zip(tens, soluongs):
            if ten:
                ketqua[ten] = ketqua.get(ten, 0) + max(1, soluong)
        return ketqua

    def get_phantramnoilucconlai(self):
        noiluctoida = self.get_noiluctoida()
        return (self.get_noilucconlai() * 100. / noiluctoida) if noiluctoida else 0

    def get_nguyenkhiconlai(self):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_NGUYENKHI) if x else False

    def get_capdonhanvat(self):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_CAPDO) if x else False

    def get_idbandohientai(self):
        return self._idbandohientai

    def _get_idbandohientai(self):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_BANDO) if x else False

    def get_diempk(self):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_DIEMPK) if x else False

    def get_iddoituongbaothu(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x184 + 0x6C * (sothutu - 1))

    def get_tendoituongbaothu(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return False
        return read_string(self.tientrinh, x + 0x188 + 0x6C * (sothutu - 1))

    def get_trangthaihanhvidoituongbaothu(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1E0 + 0x6C * (sothutu - 1))

    def _get_diachidoituongbaothu(self, sothutu = 1):
        # Đối tượng bảo thú trong danh sách đối tượng xung quanh (đang trong tầm nhìn), 0 nếu không thấy. Nhớ địa chỉ lần trước
        idbaothu = self.get_iddoituongbaothu(sothutu)
        if not idbaothu:
            return 0
        diachi, thoidiem = self._diachidoituongbaothu_map.get(idbaothu, (0, 0.))
        if diachi and self.get_is_nhanvattontai(diachi) and read_int(self.tientrinh, diachi + 0x20) == idbaothu:
            return diachi
        # Không thấy thì 1s sau mới quét lại cả danh sách đối tượng
        if not diachi and time.time() - thoidiem < 1.:
            return 0
        diachi = self.action_timkiemnhanvat(iddoituong = idbaothu) or 0
        if len(self._diachidoituongbaothu_map) > 16:
            self._diachidoituongbaothu_map.clear()
        self._diachidoituongbaothu_map[idbaothu] = (diachi, time.time())
        return diachi

    def get_toadodoituongbaothu(self, sothutu = 1):
        # Toạ độ trong ô bảo thú của khối điều khiển có lúc đứng yên ở chỗ cũ (đo: lệch ~36 ô khi bảo thú đứng ngay cạnh chủ)
        # => bảo thú trong tầm nhìn thì lấy toạ độ thật của đối tượng, không thấy mới dùng ô của khối điều khiển
        diachi = self._get_diachidoituongbaothu(sothutu)
        if diachi:
            return self.get_toado(diachi)
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1B4 + 0x6C * (sothutu - 1)), read_int(self.tientrinh, x + 0x1B8 + 0x6C * (sothutu - 1))

    def get_idbandohientaidoituongbaothu(self, sothutu = 1):
        # Đang thấy bảo thú trong tầm nhìn tức là cùng bản đồ (ô bản đồ của khối điều khiển chỉ cập nhật khi vòng sáng là Theo sau)
        if self._get_diachidoituongbaothu(sothutu):
            return self.get_idbandohientai()
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1E4 + 0x6C * (sothutu - 1))

    def get_phantramsinhlucconlaidoituongbaothukynangtrieuhoi(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1D4 + 0x6C * (sothutu - 1)) * 2

    def get_phantramnoilucconlaidoituongbaothukynangtrieuhoi(self, sothutu = 1):
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return False
        return read_int(self.tientrinh, x + 0x1D8 + 0x6C * (sothutu - 1)) * 2

    def get_diachicosothongtinnhanvat1(self):
        return read_int(self.tientrinh, self.diachixq + DC.NHANVAT)

    def get_diachicosothongtindoituongx(self, x):
        # Mọi vòng quét đối tượng đều đi từ ô 0 lên: tới ô 0 thì đọc cả bảng 1 lần, các ô sau lấy từ bản vừa đọc
        # (trước đây mỗi ô 1 lần đọc bộ nhớ, mỗi vòng quét hàng trăm lần)
        if x == 0:
            try:
                kichthuoc = SOLUONGDOITUONGXUNGQUANHTOIDA * 4
                dulieu = read_bytes(self.tientrinh, self.diachixq + DC.BANGDOITUONG, kichthuoc)
                self._bangdiachidoituongs = struct.unpack("<%di" % SOLUONGDOITUONGXUNGQUANHTOIDA, dulieu)
            except Exception:
                self._bangdiachidoituongs = ()
        bang = self._bangdiachidoituongs
        if 0 <= x < len(bang):
            return bang[x]
        return read_int(self.tientrinh, self.diachixq + DC.BANGDOITUONG + x * 0x4)

    def _get_tenthucte(self, diachicosothongtinnhanvat):
        # Tên gốc (còn phần "( Cấp ...)", tên chủ nhân bảo thú) tại +0x10AC, nhớ tạm THOIGIANNHOTENDOITUONG giây
        thoidiemhientai = time.time()
        daluu = self._tendoituong_map.get(diachicosothongtinnhanvat)
        if daluu and thoidiemhientai - daluu[0] < THOIGIANNHOTENDOITUONG:
            return daluu[1]
        ten = read_string(self.tientrinh, diachicosothongtinnhanvat + DC.NV_TEN)
        if len(self._tendoituong_map) > 1024:
            self._tendoituong_map = {k: v for k, v in list(self._tendoituong_map.items()) if thoidiemhientai - v[0] < THOIGIANNHOTENDOITUONG}
        self._tendoituong_map[diachicosothongtinnhanvat] = (thoidiemhientai, ten)
        return ten

    def _get_diachidoituongxungquanhs(self, is_nguoichoi = False, is_baothukynangtrieuhoi = False):
        # Các đối tượng còn tồn tại trong tầm màn hình; tọa độ bản thân đọc 1 lần cho cả vòng (get_khoangcach đọc lại mỗi đối tượng)
        toadobanthan = self.get_toado()
        i = 0
        while i < SOLUONGDOITUONGXUNGQUANHTOIDA:
            diachi = self.get_diachicosothongtindoituongx(i)
            if not diachi:
                break
            i += 1
            if not self.get_is_nhanvattontai(diachi):
                continue
            if is_nguoichoi and not self.get_is_nguoichoi(diachi):
                continue
            if is_baothukynangtrieuhoi and not self.get_is_baothukynangtrieuhoi(diachi):
                continue
            if math.dist(toadobanthan, self.get_toado(diachi)) > KHOANGCACHTOANMANHINH:
                continue
            yield diachi

    def get_diachicosothongtinvatphamhanhtrang(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return read_int(self.tientrinh, x + DC.TG_HANHTRANG) if x else False

    def get_iddoituongvatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        return read_int(self.tientrinh, x + idvitri * 0x4) if x else False

    def get_soluongvatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        return read_int(self.tientrinh, x + idvitri * 0x4 + DC.HT_SOLUONG) if x else False

    def get_tenvatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        return read_string(self.tientrinh, x + idvitri * 0x20 + DC.HT_TEN) if x else False

    def get_khodangmo(self):
        # Rương kho đang mở (dữ liệu game giữ từ lần mở gần nhất, mở lại để có số mới): {"ruong": số rương (từ 1), "soruong": số rương
        # dùng được, "os": [(tên, số lượng, mã loại) x SOOMOIRUONGKHO]} hoặc None. Ô trống: tên rỗng, số lượng 0; đồ không chồng được số
        # lượng 0. Xét trống theo MÃ LOẠI = 0: đổi rương game xoá mã nhưng giữ tên / số lượng cũ của rương trước ở ô trống (bot từng tưởng
        # mọi rương đều đầy). Tên tối đa 0x20 byte như hành trang (tên dài bị cắt, so bằng is_trungtenkho)
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        kho = read_int(self.tientrinh, x + DC.TG_KHO) if x else 0
        if not kho:
            return None
        dulieu = read_bytes(self.tientrinh, kho + DC.KHO_TEN, SOOMOIRUONGKHO * 0x20)
        tens = []
        for i in range(SOOMOIRUONGKHO):
            ten = dulieu[i * 0x20:(i + 1) * 0x20].split(b"\x00")[0].decode("utf-8", errors = "ignore")
            tens.append(re.sub(r'\x1b[a-zA-Z0-9]', '', ten).strip())
        soluongs = struct.unpack("<%dI" % SOOMOIRUONGKHO, read_bytes(self.tientrinh, kho + DC.KHO_SOLUONG, SOOMOIRUONGKHO * 4))
        mas = struct.unpack("<%dI" % SOOMOIRUONGKHO, read_bytes(self.tientrinh, kho + DC.KHO_MA, SOOMOIRUONGKHO * 4))
        return {"ruong": read_int(self.tientrinh, kho + DC.KHO_RUONGMO) + 1, "soruong": read_int(self.tientrinh, kho + DC.KHO_SORUONG),
                "os": [(ten, soluong, ma) if ma else ("", 0, 0) for ten, soluong, ma in zip(tens, soluongs, mas)]}

    def get_is_danghienkho(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        kho = read_int(self.tientrinh, x + DC.TG_KHO) if x else 0
        return read_boolean(self.tientrinh, kho + DC.KHO_DANGHIEN) if kho else False

    def action_dongcuasokho(self):
        # Đóng cửa sổ kho như bấm X (ghi cờ đang hiện, như cửa sổ tuỳ chọn); dữ liệu rương vẫn còn trong bộ nhớ
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        kho = read_int(self.tientrinh, x + DC.TG_KHO) if x else 0
        if kho and read_boolean(self.tientrinh, kho + DC.KHO_DANGHIEN):
            write_boolean(self.tientrinh, kho + DC.KHO_DANGHIEN, False)

    def get_tentrangbi(self, vitri):
        # Tên món đang mặc ở ô trang bị vitri (VITRITRANGBIDAUTIEN...), "" nếu ô trống
        if not self.get_iddoituongvatphamhanhtrang(vitri):
            return ""
        return re.sub(r'\x1b[a-zA-Z0-9]', '', self.get_tenvatphamhanhtrang(vitri) or "").strip()

    def get_tenphapbaohientai(self):
        # Pháp bảo đang đeo: ô trang bị VITRITRANGBI_PHAPBAO (sau 96 ô hành trang), "" nếu không đeo
        return self.get_tentrangbi(VITRITRANGBI_PHAPBAO)

    @staticmethod
    def get_vantayvatpham(mota):
        # "Dấu vân tay" của 1 món từ mô tả, để phân biệt các món cùng tên (khác sao / chỉ số / cường hoá). Chỉ giữ phần cố định:
        # dòng tên (bỏ ngoặc cuối như "（Vật phẩm sẽ Phong Ấn）", "(Vật phẩm hiệu ứng [Khoá])" vì đổi khi đeo), dòng loại "［Nón］...",
        # dòng sao và các dòng chỉ số "...: +x". Bỏ độ bền (giảm dần), dòng bộ "Cự Tượng(5/5)" và hiệu ứng bộ (đổi theo số món đang mặc)
        dongs = [dong.strip() for dong in re.sub(r'\x1b[a-zA-Z0-9]', '', mota or "").split("\n") if dong.strip()]
        if not dongs:
            return ""
        giu = [re.sub(r"\s*[（(][^（()）]*(?:\[[^\]]*\])?[^（()）]*[）)]\s*$", "", dongs[0]).strip()]
        for dong in dongs[1:]:
            if re.match(r"^[\[［]", dong) or "★" in dong or re.search(r":\s*\+", dong):
                giu.append(dong)
        return "|".join(giu)

    def get_motavatphamhanhtrangcosan(self, idvitri):
        # Mô tả game đã nạp sẵn cho ô này (không gửi lệnh desc như get_motavatphamhanhtrang), "" nếu chưa nạp
        x = self.get_diachicosothongtinvatphamhanhtrang()
        return (read_string(self.tientrinh, x + idvitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, 1024) or "") if x else ""

    def truyvan_motavatphamhanhtrang(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return False
        iddoituongvatphamhanhtrang = self.get_iddoituongvatphamhanhtrang(idvitri)
        if not iddoituongvatphamhanhtrang: return False
        if idvitri >= VITRITRANGBIDAUTIEN:
            # Đồ đang mặc: desc theo vị trí ô trang bị đếm từ 1 (vũ khí = "desc 3"); "desc <id>#" không nạp mô tả đồ đang mặc
            is_ok = self.action_thucthicaulenh("desc {}".format(idvitri - VITRITRANGBIDAUTIEN + 1))
        else:
            is_ok = self.action_thucthicaulenh("desc {}#".format(hex(iddoituongvatphamhanhtrang)).replace("0x", ""))
        if is_ok: time.sleep(0.2)
        return is_ok

    def _chomotavatphamhanhtrang(self, x, idvitri, thoigianchotoida):
        # Sau lệnh desc, máy chủ trả mô tả sau khoảng 0.25-0.5s (qua hàng đợi lệnh còn lâu hơn): đọc lại mỗi 0.05s tới khi có hoặc hết giờ
        thoidiemhet = time.time() + thoigianchotoida
        while True:
            mota = read_string(self.tientrinh, x + idvitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, 1024)
            if mota or time.time() >= thoidiemhet:
                return mota
            time.sleep(0.05)

    def get_motavatphamhanhtrang(self, idvitri, thoigianchotoida = 1., is_napmoi = False):
        # is_napmoi: xoá mô tả đang có rồi desc lại (mô tả theo ô, chuyển đồ xong có thể còn mô tả của món trước đó ở ô này)
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return False
        if is_napmoi:
            write_bytes(self.tientrinh, x + idvitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, b"\x00", 1)
        mota = read_string(self.tientrinh, x + idvitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, 1024)
        if not mota and self.get_iddoituongvatphamhanhtrang(idvitri):
            if self.truyvan_motavatphamhanhtrang(idvitri):
                mota = self._chomotavatphamhanhtrang(x, idvitri, thoigianchotoida)
        return mota

    def action_truyvandobentrangbi(self):
        # Xoá mô tả cũ (độ bền trong đó không tự cập nhật) rồi desc lại các món sửa được đang mặc; trả về số lệnh desc đã gửi.
        # Không chờ: máy chủ trả mô tả sau đó, đọc bằng get_dobentrangbisuaduocs
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return 0
        soluong = 0
        for vitri in VITRITRANGBISUADUOCs:
            if not self.get_iddoituongvatphamhanhtrang(vitri):
                continue
            write_bytes(self.tientrinh, x + vitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, b"\x00", 1)
            if self.action_thucthicaulenh("desc {}".format(vitri - VITRITRANGBIDAUTIEN + 1), douutien = DOUUTIEN_THAP):
                soluong += 1
        return soluong

    def get_dobentrangbisuaduocs(self):
        # {ô trang bị: (độ bền hiện tại, tối đa)} cho các món sửa được đang mặc, None nếu mô tả chưa nạp / không đọc được độ bền
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return {}
        dobens = {}
        for vitri in VITRITRANGBISUADUOCs:
            if not self.get_iddoituongvatphamhanhtrang(vitri):
                continue
            mota = unicodedata.normalize("NFC", read_string(self.tientrinh, x + vitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, 1024) or "")
            khop = re.search(r"bền\s*[:：]\s*(\d+)\s*/\s*(\d+)", mota)
            dobens[vitri] = (int(khop.group(1)), int(khop.group(2))) if khop else None
        return dobens

    def get_motavatphamhanhtrang_raw(self, idvitri):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return b""

        mota_raw = read_bytes(self.tientrinh, x + idvitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, 1024)

        null_index = mota_raw.find(b"\x00")
        if null_index != -1:
            mota_raw = mota_raw[:null_index]

        if not mota_raw and self.get_iddoituongvatphamhanhtrang(idvitri):
            if self.truyvan_motavatphamhanhtrang(idvitri):
                self._chomotavatphamhanhtrang(x, idvitri, 1.)
            mota_raw = read_bytes(self.tientrinh, x + idvitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, 1024)
            null_index = mota_raw.find(b"\x00")
            if null_index != -1:
                mota_raw = mota_raw[:null_index]

        mota_raw = re.sub(rb'\x1b[a-zA-Z0-9]', b'', mota_raw).strip()

        return mota_raw

    def get_diachicosothongtinkynang(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return read_int(self.tientrinh, x + DC.TG_KYNANG) if x else False

    def get_is_dangmocuasoxacnhan(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_CUASOXACNHAN)
        return read_boolean(self.tientrinh, x + 0xB4) if x else False

    def set_is_dangmocuasoxacnhan(self, is_dangmocuasoxacnhan):
        if self.get_is_dangmocuasoxacnhan() == is_dangmocuasoxacnhan: return
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x: return
        x = read_int(self.tientrinh, x + DC.TG_CUASOXACNHAN)
        if not x: return
        write_boolean(self.tientrinh, x + 0xB4, is_dangmocuasoxacnhan)

    def get_noidungcuasomaxacnhan(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x: return ""
        x = read_int(self.tientrinh, x + DC.TG_CUASOXACNHAN)
        return read_string(self.tientrinh, x + 0xBC) if x else ""

    def get_danhsachidnguoichoixungquanhs(self):
        danhsachidnguoichoixungquanhs = []
        for diachi in self._get_diachidoituongxungquanhs():
            idnguoichoi = self.get_idnguoichoi(diachi)
            if idnguoichoi:
                danhsachidnguoichoixungquanhs.append(idnguoichoi)
        return danhsachidnguoichoixungquanhs

    def get_idnguoichoixungquanh_map(self):
        return {diachi: self.get_idnguoichoi(diachi) for diachi in self._get_diachidoituongxungquanhs(is_nguoichoi = True)}

    def get_tenchunhanbaothuxungquanh_map(self):
        tenchunhanbaothu_map = {}
        for diachi in self._get_diachidoituongxungquanhs(is_baothukynangtrieuhoi = True):
            tenchunhan = self.get_tenchunhan(diachi)
            if tenchunhan:
                tenchunhanbaothu_map[diachi] = tenchunhan
        return tenchunhanbaothu_map

    def get_idbaothuxungquanh_map(self):
        return {diachi: self.get_iddoituong(diachi) for diachi in self._get_diachidoituongxungquanhs(is_baothukynangtrieuhoi = True)}

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
        idnguoichoixungquanh_list = set(idnguoichoixungquanh_map.values())
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
        tenchunhanbaothuxungquanh_list = set(tenchunhanbaothuxungquanh_map.values())

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

        # elif time.time() - self._thoidiemtuthenhanvattanconggannhat > 0.4 and not self.get_is_khoavankhitrieuhoi():
        #     # Đang vận khí triệu hồi thì không ghi đè tư thế (có thể làm game coi như dừng chiêu)
        #     self.set_idtuthenhanvat(TUTHENHANVAT_DELAYSAUTANCONG)

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

        loai9002 = self.get_loaihieuung9002()
        # Hôn Mê cũng không làm gì được như choáng; Bất Động chỉ không đi được
        self._is_nhanvatbichoang = loai9002 in ("choang", "honme")
        self._is_nhanvatbibatdong = loai9002 == "batdong"
        self._is_nhanvatbitrammac = self.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC,), macdinh = False, is_hieuungcoloi = 0)
        self._is_nhanvatbimongdu = self.get_is_cohieuungs((HIEUUNGKYNANG_MONGDU,), macdinh = False, is_hieuungcoloi = 0)
        self._is_nhanvatbibienthan = self.get_is_cohieuungs((HIEUUNGKYNANG_BIENTHANTHUAT,), macdinh = False, is_hieuungcoloi = 0)
        if self.get_is_cohieuungs((HIEUUNGKYNANG_DAOHOALACANH,), macdinh = False, is_hieuungcoloi = 0):
            if not self._toadotrandolacanh:
                self._toadotrandolacanh = self._timtamtrandolacanh()
        else:
            self._toadotrandolacanh = None

        if not self.get_is_dangbatchucnangmorong():
            self.thoidiemcochucnangmoronggannhat = time.time()

        for noidungtrochuyen in self._docdongtrochuyenmois():
            self._lichsutrochuyen5s.append((now, noidungtrochuyen))

        self._lichsutrochuyen5s = [msg for msg in self._lichsutrochuyen5s if now - msg[0] <= 5.0]

    def get_lichsutrochuyen5s(self):
        return self._lichsutrochuyen5s

    def xoalichsutrochuyen(self):
        self._lichsutrochuyen5s.clear()

    def get_is_nhanvatbichoang(self):
        # Choáng hoặc Hôn Mê: không dùng kỹ năng, không đánh thường, không di chuyển
        return self._is_nhanvatbichoang

    def get_is_nhanvatbibatdong(self):
        # Bất Động: không di chuyển, vẫn dùng kỹ năng
        return self._is_nhanvatbibatdong

    def get_loaihieuung9002(self, diachicosothongtinnhanvat = None):
        # Hiệu ứng 9002 (có hại) trên đối tượng là "choang" / "batdong" / "honme" theo thời gian tối đa (xem THOIGIANTOIDACHOANG), không có thì None
        for idhieuung, is_hieuungcoloi, thoigianhieuluctoida in self.get_danhsachhieuungnhanvats(diachicosothongtinnhanvat):
            if idhieuung == HIEUUNGKYNANG_CHOANG and is_hieuungcoloi == 0:
                if thoigianhieuluctoida <= THOIGIANTOIDACHOANG:
                    return "choang"
                return "batdong" if thoigianhieuluctoida <= THOIGIANTOIDABATDONG else "honme"
        return None

    def _timtamtrandolacanh(self):
        # Trận lấy người dùng chiêu làm tâm: lúc vừa bị dính, người chơi ngoài nhóm trong KHOANGCACHTIMNGUOIDUNGTRANDO ô, ưu tiên người
        # đánh tay không (Đào Hoa Nguyên dùng quyền) rồi tới người gần nhất (đứng sát nhau thì chỉ xét gần nhất hay chọn nhầm người phái khác);
        # không thấy ai thì lấy chỗ mình đang đứng
        toadobanthan = self.get_toado()
        idbanthan = self.get_idnguoichoi()
        idcungnhoms = set(self.get_danhsachidnguoichoithanhviennhoms() or ()) if self.get_is_dangnamtrongnhom() else set()
        tam, tennguoidung, khoatot = toadobanthan, None, None
        for diachi in self._get_diachidoituongxungquanhs(is_nguoichoi = True):
            idnguoichoi = self.get_idnguoichoi(diachi)
            if idnguoichoi == idbanthan or idnguoichoi in idcungnhoms:
                continue
            toado = self.get_toado(diachi)
            khoangcach = math.dist(toadobanthan, toado)
            if khoangcach > KHOANGCACHTIMNGUOIDUNGTRANDO:
                continue
            khoa = (self.get_idloaivukhi(diachi) != IDLOAIVUKHI_TAYKHONG, khoangcach)
            if khoatot is None or khoa < khoatot:
                tam, tennguoidung, khoatot = toado, self.get_tendoituong(diachi), khoa
        self._inlog(f"[TRẬN ĐỒ] Dính Trận Pháp Lạc Ảnh tại {toadobanthan}, tâm trận {tam} ({tennguoidung or 'không thấy người dùng chiêu, lấy chỗ mình đứng'})")
        return tam

    def get_is_bigiutrongtrando(self):
        return bool(self._toadotrandolacanh)

    def _kepdichtrongtrando(self, x, y):
        # Đang bị Trận Pháp Lạc Ảnh giữ: đích ngoài trận kéo về mép trận theo hướng tâm trận -> đích (vẫn tiến về phía đích hết mức được).
        # Trả về None nếu đích sau khi kéo trùng chỗ đang đứng (bấm cũng không đi được)
        tam = self._toadotrandolacanh
        if not tam:
            return x, y
        khoangcach = math.dist(tam, (x, y))
        if khoangcach > BANKINHTRANDOLACANH:
            tyle = BANKINHTRANDOLACANH / khoangcach
            x, y = tam[0] + (x - tam[0]) * tyle, tam[1] + (y - tam[1]) * tyle
            if math.dist(self.get_toado(), (x, y)) < 0.7:
                return None
        return x, y

    def get_is_khongthedungkynang(self):
        # Bị choáng thì không dùng được kỹ năng nào (cũng không đánh thường, không di chuyển được); bị mộng du / Biến Thân Thuật (cóc) thì
        # không dùng được kỹ năng; bị Trầm Mặc thì môn phái phép thuật (MONPHAIPHEPTHUATs) không dùng được kỹ năng
        return self._is_nhanvatbichoang or self._is_nhanvatbimongdu or self._is_nhanvatbibienthan or (self._is_nhanvatbitrammac and self.get_tenmonphai() in MONPHAIPHEPTHUATs)

    def get_thoidiemthaydoibandogannhat(self):
        return self._thoidiemthaydoibandogannhat

    def get_is_cuasogametontai(self):
        return win32gui.IsWindow(self.idcuaso)

    def get_is_cuasogamekichhoat(self):
        return win32gui.GetForegroundWindow() == self.idcuaso

    def get_diachicosothongtinnhanvatdangchichuot(self):
        return read_int(self.tientrinh, self.diachixq + DC.NHANVATDANGCHICHUOT)

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
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + DC.NV_ANTHAN) > 0

    def get_is_vatphamtontai(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return self.get_iddoituong(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) == LOAIDOITUONG_VATPHAMDUOIDAT

    def get_is_nhanvatdachet(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_boolean(self.tientrinh, diachicosothongtinnhanvat + DC.NV_CHET)

    def get_tendoituong(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        tendoituong = self._get_tenthucte(diachicosothongtinnhanvat)

        if tendoituong:
            for nhancap in ("( Cấp", "( Cấp", "( cấp", "(cấp"):
                if nhancap in tendoituong:
                    tendoituong = tendoituong.split(nhancap)[0].strip()
                    break

        return tendoituong

    def get_tennhanvatchichuot(self):
        diachi = self.get_diachicosothongtinnhanvatdangchichuot()
        return self.get_tendoituong(diachi) if diachi else False

    def get_noidungthongbaogannhat(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_THONGBAO)
        return read_string(self.tientrinh, x + 0x24) if x else False

    def get_phantramsinhlucconlai(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + DC.NV_PHANTRAMMAU) * 2

    def get_toado(self, diachicosothongtinnhanvat = None, is_toadosaptoi = False):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        # x, y nằm liền nhau: 1 lần đọc thay vì 2
        toadox, toadoy = struct.unpack("<ii", read_bytes(self.tientrinh, diachicosothongtinnhanvat, 8))

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
            deltay = read_int(self.tientrinh, diachicosothongtinnhanvat + 0x1C) - read_int(self.tientrinh, diachicosothongtinnhanvat + 0x4)
            if deltay != 0:
                return deltay / abs(deltay)
        return 0

    def get_toadosaptoi(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        offset = 0x18 if self.get_idtuthenhanvat(diachicosothongtinnhanvat) == TUTHENHANVAT_DICHUYEN else 0x0
        return struct.unpack("<ii", read_bytes(self.tientrinh, diachicosothongtinnhanvat + offset, 8))

    def get_toadobandochichuot(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_TIMDUONG)
        return (read_int(self.tientrinh, x + 0x371C80), read_int(self.tientrinh, x + 0x371C84)) if x else False

    def get_idbandochichuot(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_TIMDUONG)
        if not x:
            return False
        y = read_int(self.tientrinh, x + 0x11F10)
        return read_int(self.tientrinh, x + 0x23C + 0x16C * y) if y else False

    def get_idmaupk(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return read_int(self.tientrinh, x + DC.TG_MAUPK) if x else False

    def set_idmaupk(self, idmaupk):
        if self.get_idmaupk() != idmaupk:
            x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
            if x: write_int(self.tientrinh, x + DC.TG_MAUPK, idmaupk)

    def get_tenbang(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_string(self.tientrinh, diachicosothongtinnhanvat + 0x1136)

    def get_is_cungbang(self, diachicosothongtinnhanvat):
        return self.get_idnguoichoi(diachicosothongtinnhanvat) in laynhanvattodoitudongs()

    def get_idtrangthaichuot(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_GIAODIEN)
        return read_int(self.tientrinh, x + 0x1A4) if x else False

    def set_idtrangthaichuot(self, idtrangthaichuot):
        if idtrangthaichuot != self.get_idtrangthaichuot():
            x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
            if x:
                x = read_int(self.tientrinh, x + DC.TG_GIAODIEN)
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
        return read_int(self.tientrinh, diachicosothongtinnhanvat + DC.NV_TUTHE)

    def set_idtuthenhanvat(self, idtuthenhanvat, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) != idtuthenhanvat:
            write_int(self.tientrinh, diachicosothongtinnhanvat + DC.NV_TUTHE, idtuthenhanvat)

    def get_huongmat(self, diachicosothongtinnhanvat = None):
        # Hướng mặt 8 hướng (0..7). Game không lưu đối tượng đang nhắm vào ai, nhưng lúc ra đòn thì quay mặt về mục tiêu
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachicosothongtinnhanvat + DC.NV_HUONGMAT)

    def get_is_huongmatvediem(self, diachicosothongtinnhanvat, x2, y2, solechtoida = 1):
        # Hướng mặt của đối tượng có trỏ về điểm (x2, y2) không (lệch tối đa solechtoida trong 8 hướng).
        # Đo trên quái đang ra đòn: huong = round((225 - goc) / 45) mod 8, goc = atan2(y2 - y, x2 - x) theo tọa độ ô (y hướng xuống)
        x1, y1 = self.get_toado(diachicosothongtinnhanvat)
        return tinh_is_huongmatvediem(x1, y1, self.get_huongmat(diachicosothongtinnhanvat), x2, y2, solechtoida)

    def get_is_muctieuchaytron(self, diachicosothongtinnhanvat):
        if self.get_idtuthenhanvat(diachicosothongtinnhanvat) != TUTHENHANVAT_DICHUYEN:
            return False

        x_thucte, y_thucte = self.get_toado(diachicosothongtinnhanvat)
        kc_thucte = self.get_khoangcachdiem(x_thucte, y_thucte)

        # Trước đây đọc lại đúng tọa độ hiện tại nên kc_dukien luôn bằng kc_thucte => hàm luôn trả về False
        x_dukien, y_dukien = self.get_toado(diachicosothongtinnhanvat, is_toadosaptoi = True)
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
        self._donbanghieuung()
        return soluong

    def _donbanghieuung(self):
        # Hai bảng theo địa chỉ đối tượng trước đây không bao giờ xoá: bỏ đối tượng không còn quanh mình,
        # và mốc "vừa về 0" đã quá 2s (chỉ dùng trong 1s)
        if len(self._soluonghieuungnhanvattruocdo_map) > 1024:
            congiu = set(self._bangdiachidoituongs)
            congiu.add(self.get_diachicosothongtinnhanvat1())
            self._soluonghieuungnhanvattruocdo_map = {k: v for k, v in list(self._soluonghieuungnhanvattruocdo_map.items()) if k in congiu}
        if len(self._thoidiemsoluonghieuungbangkhonggannhat_map) > 256:
            thoidiemhientai = time.time()
            self._thoidiemsoluonghieuungbangkhonggannhat_map = {k: v for k, v in list(self._thoidiemsoluonghieuungbangkhonggannhat_map.items()) if thoidiemhientai - v < 2.}

    def _get_idhieuungtheovitri(self, idvitrihieuung):
        idhieuung = self._idhieuungtheovitri_map.get(idvitrihieuung)
        if idhieuung is None:
            idhieuung = read_int(self.tientrinh, self.diachixq + DC.BANGHIEUUNG + idvitrihieuung * 4)
            # Game chưa nạp xong bảng thì ô còn 0: chưa nhớ, lần sau đọc lại
            if idhieuung:
                self._idhieuungtheovitri_map[idvitrihieuung] = idhieuung
        return idhieuung

    def _docbanghieuung(self, diachicosothongtinnhanvat):
        thoidiemhientai = time.time()
        dem = self._banghieuung_cache.get(diachicosothongtinnhanvat)
        if dem and thoidiemhientai - dem[0] < THOIGIANNHOBANGHIEUUNG:
            return dem[1]
        ketqua = self._docbanghieuungtubonho(diachicosothongtinnhanvat)
        if len(self._banghieuung_cache) > 1024:
            self._banghieuung_cache = {k: v for k, v in list(self._banghieuung_cache.items()) if thoidiemhientai - v[0] < THOIGIANNHOBANGHIEUUNG}
        self._banghieuung_cache[diachicosothongtinnhanvat] = (thoidiemhientai, ketqua)
        return ketqua

    def _docbanghieuungtubonho(self, diachicosothongtinnhanvat):
        # Đọc cả bảng hiệu ứng trong 1 lần (trước đây 3-4 lần đọc bộ nhớ cho mỗi ô, lại đọc lại số lượng/tồn tại ở mỗi ô).
        # Số lượng đổi giữa lúc đọc thì đọc lại (giống bản cũ bắt đầu đếm lại). Trả về (số lượng, [(id hiệu ứng, có lợi, thời gian)])
        kichthuoc = SOLUONGHIEUUNGNHANVATTOIDA * DC.NV_KICHTHUOCHIEUUNG
        for _ in range(3):
            soluong = self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat)
            dulieu = read_bytes(self.tientrinh, diachicosothongtinnhanvat + DC.NV_HIEUUNG, kichthuoc)
            if self.get_soluonghieuungnhanvat(diachicosothongtinnhanvat) == soluong:
                break
        hieuungs = []
        for i in range(SOLUONGHIEUUNGNHANVATTOIDA):
            idvitri, is_hieuungcoloi, thoigianhieuluctoida = struct.unpack_from("<iii", dulieu, i * DC.NV_KICHTHUOCHIEUUNG)
            if idvitri < 0 or is_hieuungcoloi < 0 or (not idvitri and not is_hieuungcoloi and not thoigianhieuluctoida):
                continue
            hieuungs.append((self._get_idhieuungtheovitri(idvitri), is_hieuungcoloi, thoigianhieuluctoida))
        return soluong, hieuungs

    def get_danhsachhieuungnhanvats(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        if not self.get_is_nhanvattontai(diachicosothongtinnhanvat):
            return []
        soluong, hieuungs = self._docbanghieuung(diachicosothongtinnhanvat)
        return hieuungs[:max(soluong, 0)]

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

        def _is_vuabangkhong():
            # Số hiệu ứng vừa tụt về 0 (đang tải lại) thì chưa tin được, trả về mặc định
            return time.time() - self._thoidiemsoluonghieuungbangkhonggannhat_map.get(diachicosothongtinnhanvat, time.time() - 2.) < 1

        if _is_vuabangkhong():
            return macdinh
        soluonghieuungnhanvat, hieuungs = self._docbanghieuung(diachicosothongtinnhanvat)
        if _is_vuabangkhong():
            return macdinh
        if soluonghieuungnhanvat <= 0:
            return False

        soluonghieuungdemduoc = 0
        for idhieuungxemxet, is_hieuungcoloixemxet, thoigianhieuluctoida in hieuungs:
            if idhieuungxemxet in idhieuungs:
                if is_hieuungcoloi is not None:
                    if is_travethoigianhieuluctoida: return is_hieuungcoloixemxet == is_hieuungcoloi, thoigianhieuluctoida
                    return is_hieuungcoloixemxet == is_hieuungcoloi
                if is_travethoigianhieuluctoida: return True, thoigianhieuluctoida
                return True
            soluonghieuungdemduoc += 1
            if soluonghieuungdemduoc >= soluonghieuungnhanvat:
                return False
        return macdinh

    def get_diachicosoidthanhviennhom(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        return read_int(self.tientrinh, x + DC.TG_NHOM) if x else False

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

    def get_idkynang(self, idvitri_x, idvitri_y = None):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return False
        idvitri_x, idvitri_y = vitri
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang: return False
        idvitrikynang = 14 * idvitri_y + idvitri_x
        return read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * DC.KN_KICHTHUOC + DC.KN_ID)

    def _giaivitrikynang(self, idvitri_x, idvitri_y = None):
        # Mã kỹ năng -> vị trí (x, y) trên bảng kỹ năng, None khi không dùng được. Mã kỹ năng là id kỹ năng (VITRIKYNANG_* của các phái đã
        # chuyển sang id: tra vị trí hiện tại, chưa học thì None - hàng kỹ năng đổi chỗ / chèn hàng khi học chiêu mới vẫn đúng) hoặc vị trí
        # (x, y) cũ (phái chưa có id: Đường Môn, Cẩm Vệ Quân)
        if idvitri_y is not None:
            return idvitri_x, idvitri_y
        if isinstance(idvitri_x, tuple):
            return idvitri_x
        return self._get_bangvitrikynangdahoc().get(idvitri_x)

    def _get_bangvitrikynangdahoc(self):
        # {id kỹ năng đã học: (x, y)} đọc cả bảng 1 lần, nhớ THOIGIANNHOBANGKYNANG giây (hàm kỹ năng gọi liên tục mỗi lượt)
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemdocbangkynang < THOIGIANNHOBANGKYNANG:
            return self._bangvitrikynangdahoc
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        bang = {}
        if diachicosothongtinkynang:
            dulieu = read_bytes(self.tientrinh, diachicosothongtinkynang + DC.KN_ID, 14 * 6 * DC.KN_KICHTHUOC)
            for idvitri in range(14 * 6):
                idkynang, dahoc = struct.unpack_from("<i", dulieu, idvitri * DC.KN_KICHTHUOC)[0], struct.unpack_from("<i", dulieu, idvitri * DC.KN_KICHTHUOC + OFFSET_KYNANGDAHOC)[0]
                if idkynang and dahoc:
                    bang[idkynang] = (idvitri % 14, idvitri // 14)
        self._bangvitrikynangdahoc = bang
        self._thoidiemdocbangkynang = thoidiemhientai
        return bang

    def get_vitrikynangtheoid(self, idkynang):
        # Vị trí (x, y) của kỹ năng có id idkynang trên bảng kỹ năng (14 ô mỗi hàng, 6 hàng; id tại ô + KN_ID), không có thì None.
        # Id kỹ năng cố định theo kỹ năng (vd Không Thủ Nhập Bạch Nhẫn 2114, Hộ Thể Kim Cang 3173 - đa số trùng HIEUUNGKYNANG_*),
        # còn vị trí thì cùng 1 ô mỗi phái là 1 kỹ năng khác (ô (0, 2) Mao Sơn là Huyết Ma Chú, Đào Hoa là Kim Trung Chao)
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang:
            return None
        dulieu = read_bytes(self.tientrinh, diachicosothongtinkynang + DC.KN_ID, 14 * 6 * DC.KN_KICHTHUOC)
        for idvitri in range(14 * 6):
            if struct.unpack_from("<i", dulieu, idvitri * DC.KN_KICHTHUOC)[0] == idkynang:
                return idvitri % 14, idvitri // 14
        return None

    def _docokynangtheoid(self, idkynang):
        # Dữ liệu ô kỹ năng (tính từ + KN_ID) của kỹ năng idkynang, không có trên bảng thì None
        vitri = self.get_vitrikynangtheoid(idkynang)
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not vitri or not diachicosothongtinkynang:
            return None
        return read_bytes(self.tientrinh, diachicosothongtinkynang + (14 * vitri[1] + vitri[0]) * DC.KN_KICHTHUOC + DC.KN_ID, DC.KN_KICHTHUOC)

    def get_is_kynangdahoc(self, idkynang):
        # Ô kỹ năng + KN_ID + OFFSET_KYNANGDAHOC = 3 khi đã học, 0 khi chưa (game dựa vào đây để bôi mờ chiêu chưa học). Đo trên Vân Mộng
        # Cốc: Nghênh Phong Trảm 0 -> 3 lúc học, Phá Không Kích 0 -> 3, Đơn Đao Trực Nhập lên cấp 2 vẫn 3; tên kỹ năng ở + 0x8 cố định
        # 0x14 byte nên trường này không bị chữ đè. Kỹ năng không có trên bảng cũng là chưa học
        dulieu = self._docokynangtheoid(idkynang)
        return bool(dulieu) and struct.unpack_from("<i", dulieu, OFFSET_KYNANGDAHOC)[0] != 0

    def get_tieuhaokynang(self, idkynang, is_truyvan = True):
        # Tiêu hao / tái sử dụng của kỹ năng lấy từ các dòng mô tả nằm trong ô kỹ năng (vd "Pháp Lực tiêu hao: 6 điểm", "Nguyên khí tiêu
        # hao: 1 điểm", "Tái sử dụng sau: 10 giây"): {"pháp lực": 6, ..., "tái sử dụng": 10.0}. Mô tả chỉ có sau khi game lấy về (rê chuột
        # hoặc "desc pf <id>"): chưa có thì gửi "desc pf <id>" (tối đa 1 lần / 2s mỗi kỹ năng) và trả None, lần gọi sau sẽ có;
        # có mô tả mà không ghi số tiêu hao thì {}.
        # Đọc được thì nhớ THOIGIANNHOTIEUHAOKYNANG giây (tiêu hao chỉ đổi khi lên cấp chiêu), chưa đọc được thì nhớ 0.5s
        dem = self._tieuhaokynang_cache.get(idkynang)
        if dem and time.time() - dem[0] < (THOIGIANNHOTIEUHAOKYNANG if dem[1] is not None else 0.5):
            return dem[1]
        ketqua = self._doctieuhaokynang(idkynang, is_truyvan)
        self._tieuhaokynang_cache[idkynang] = (time.time(), ketqua)
        return ketqua

    def _doctieuhaokynang(self, idkynang, is_truyvan):
        dulieu = self._docokynangtheoid(idkynang)
        if not dulieu:
            return None
        noidung = unicodedata.normalize("NFC", dulieu.replace(b"\x00", b"\n").decode("utf-8", "ignore"))
        ketqua = {loai.strip().lower(): int(so) for loai, so in re.findall(r"([^\n:]+?) tiêu hao: (\d+)", noidung)}
        taisudung = re.search(r"Tái sử dụng sau: ([\d.]+) giây", noidung)
        if taisudung:
            ketqua["tái sử dụng"] = float(taisudung.group(1))
        # Mô tả đã có (dòng "Võ công yêu cầu" / "Yêu cầu võ công") mà không ghi số tiêu hao (Triệu Hoán Chú, Nguyên Khí Quy Nguyên,
        # "Nguyên khí tiêu hao: Toàn bộ"...) thì trả {} để không gửi "desc pf" mãi
        if ketqua or "yêu cầu" in noidung.lower():
            return ketqua
        if is_truyvan and time.time() - self._thoidiemtruyvanmotakynang_map.get(idkynang, 0.) > 2.:
            self._thoidiemtruyvanmotakynang_map[idkynang] = time.time()
            self.action_thucthicaulenh(f"desc pf {idkynang}")
        return None

    def get_is_kynangsansang(self, idvitri_x, idvitri_y = None):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return False
        idvitri_x, idvitri_y = vitri
        diachicosothongtinkynang = self.get_diachicosothongtinkynang()
        if not diachicosothongtinkynang: return False
        idvitrikynang = 14 * idvitri_y + idvitri_x
        idkynang = read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * DC.KN_KICHTHUOC + DC.KN_ID)
        is_khongcothoigiangiancach = read_int(self.tientrinh, diachicosothongtinkynang + idvitrikynang * DC.KN_KICHTHUOC + DC.KN_HOICHIEU) == 0
        return idkynang and True and is_khongcothoigiangiancach

    def get_is_nhanvatchuasansang(self, diachicosothongtinnhanvat = False):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x29) == 1

    def get_is_baothugiangho(self, diachicosodoituong):
        if not diachicosodoituong:
            return False
        tendoituong = self._get_tenthucte(diachicosodoituong)
        if not tendoituong:
            return False
        return "(" in tendoituong and "cấp" not in tendoituong.lower()

    def get_is_baothukynangtrieuhoi(self, diachicosodoituong):
        if not diachicosodoituong:
            return False
        tendoituong = self._get_tenthucte(diachicosodoituong)
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

        # Người chơi đang mộng du (Thôi Miên Thuật chỉ dùng lên người chơi) thì không tấn công được, đang Hôn Mê thì đánh vào là tỉnh lại:
        # bỏ qua để chọn mục tiêu khác. Quái không bị hai hiệu ứng này nên khỏi đọc bảng hiệu ứng
        if idloainhanvat == LOAIMUCTIEU_NGUOICHOIKHACNHOM:
            if self.get_is_cohieuungs((HIEUUNGKYNANG_MONGDU,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvat, is_hieuungcoloi = 0):
                return False
            if self.get_loaihieuung9002(diachicosothongtinnhanvat) == "honme":
                return False

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
        x = read_int(self.tientrinh, self.diachixq + DC.CONTROALT)
        return read_boolean(self.tientrinh, x) if x else False

    def set_is_batalt(self, is_batalt):
        if self.get_is_batalt() != is_batalt:
            x = read_int(self.tientrinh, self.diachixq + DC.CONTROALT)
            if x: write_boolean(self.tientrinh, x, is_batalt)

    def get_is_batautoingame(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return read_boolean(self.tientrinh, x + DC.TG_AUTOINGAME) if x else False

    def set_is_batautoingame(self, is_batautoingame):
        if not is_batautoingame:
            if read_bytes(self.tientrinh, self.diachixq + DC.VA_AUTOINGAME, 1) != bytes.fromhex("90"):
                write_bytes(self.tientrinh, self.diachixq + DC.VA_AUTOINGAME, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

        if self.get_is_batautoingame() != is_batautoingame:
            x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
            if x: write_boolean(self.tientrinh, x + DC.TG_AUTOINGAME, is_batautoingame)

    def get_is_dangbatchucnangmorong(self):
        x = read_int(self.tientrinh, self.diachixq + DC.NHANVAT)
        if not x:
            return True
        return read_string(self.tientrinh, x + 0x1136) == "Tự Động Đánh"

    def get_is_bathanhtrang(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_TUIHANHTRANG)
        return read_boolean(self.tientrinh, x + 0x34) if x else False

    def get_is_dangbatenter(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_ENTER)
        return read_boolean(self.tientrinh, x + 0x8140) if x else False

    def get_thoidiemkhongcomuctieugannhat(self):
        return self._thoidiemkhongcomuctieugannhat

    def get_iddoituongmuctieudangchon(self):
        diachi = self.get_diachicosothongtinnhanvatmuctieudangchon()
        return self.get_iddoituong(diachi) if diachi else False

    def get_is_dangclickchuottrai(self):
        # Cờ của game chỉ bật khi giữ chuột để đi, game tự tắt khi nhân vật vào đánh (lệnh "kill" / chiêu bot gửi) => bot đánh
        # tiếp, người chơi không kéo ra được. Xét thêm phím chuột trái thật đang giữ khi cửa sổ game đang kích hoạt và con trỏ nằm
        # trong vùng game. Chỉ tính khi giữ liền quá THOIGIANGIUCHUOTTOITHIEU giây (click thường để chọn mục tiêu không làm bot
        # dừng); nhả chuột sau khi đã giữ đủ lâu thì vẫn tính đang giữ thêm THOIGIANNGUNGSAUNHACHUOT giây
        thoidiemhientai = time.time()
        if read_boolean(self.tientrinh, self.diachixq + DC.DANGCLICKCHUOTTRAI) or self._is_dangdichuottraitrongcuaso():
            if not self._thoidiembatdaugiuchuottrai:
                self._thoidiembatdaugiuchuottrai = thoidiemhientai
            if thoidiemhientai - self._thoidiembatdaugiuchuottrai >= THOIGIANGIUCHUOTTOITHIEU:
                self._thoidiemgiuchuottraigannhat = thoidiemhientai
                return True
        else:
            self._thoidiembatdaugiuchuottrai = 0.
        return thoidiemhientai - self._thoidiemgiuchuottraigannhat < THOIGIANNGUNGSAUNHACHUOT

    def _is_dangdichuottraitrongcuaso(self):
        if not ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000 or not self.get_is_cuasogamekichhoat():
            return False
        try:
            x, y = win32gui.ScreenToClient(self.idcuaso, win32gui.GetCursorPos())
            _, _, rong, cao = win32gui.GetClientRect(self.idcuaso)
        except Exception:
            return False
        return 0 <= x < rong and 0 <= y < cao

    def get_diachicosothongtinnhanvatmuctieudangchon(self):
        return self._diachicosothongtinnhanvatmuctieudangchon

    def _get_diachicosothongtinnhanvatmuctieudangchon(self):
        return read_int(self.tientrinh, self.diachixq + DC.MUCTIEUDANGCHON)

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
            write_int(self.tientrinh, self.diachixq + DC.MUCTIEUDANGCHON, diachi)
            write_int(self.tientrinh, self.diachixq + DC.IDMUCTIEUDANGCHON, self.get_iddoituong(diachi))
            write_int(self.tientrinh, self.diachixq + DC.MUCTIEUDANGCHON2, diachi)
            write_int(self.tientrinh, self.diachixq + DC.IDMUCTIEUDANGCHON2, self.get_iddoituong(diachi))
            return
        write_int(self.tientrinh, self.diachixq + DC.MUCTIEUDANGCHON, 0)
        write_int(self.tientrinh, self.diachixq + DC.IDMUCTIEUDANGCHON, 0)
        write_int(self.tientrinh, self.diachixq + DC.MUCTIEUDANGCHON2, 0)
        write_int(self.tientrinh, self.diachixq + DC.IDMUCTIEUDANGCHON2, 0)

    # Các lệnh "mov dword ptr [esi+0x11B8], 0x0B" của game đặt tư thế delay sau tấn công; vá giá trị 0x0B thành đứng im.
    # Đã thử vá thêm 0x19EBE, 0x1A0CE (ghi thẳng 0x0B vào tư thế +0x1178) nhưng Đào Hoa Nguyên vẫn delay ~0.25s sau đòn như cũ => đã bỏ
    # (địa chỉ dò bằng chữ ký, xem diachi_xq.py)
    @property
    def DIACHIGHITUTHEDELAYSAUTANCONGs(self):
        return (DC.VA_TUTHEDELAY1, DC.VA_TUTHEDELAY2)

    def action_vohieuhoatuthedelaysautancong(self):
        for diachi in self.DIACHIGHITUTHEDELAYSAUTANCONGs:
            if read_int(self.tientrinh, self.diachixq + diachi + 0x6) != TUTHENHANVAT_DUNGIM: write_int(self.tientrinh, self.diachixq + diachi + 0x6, TUTHENHANVAT_DUNGIM)

    def action_tatvohieuhoatuthedelaysautancong(self):
        for diachi in self.DIACHIGHITUTHEDELAYSAUTANCONGs:
            if read_int(self.tientrinh, self.diachixq + diachi + 0x6) != TUTHENHANVAT_DELAYSAUTANCONG: write_int(self.tientrinh, self.diachixq + diachi + 0x6, TUTHENHANVAT_DELAYSAUTANCONG)

    def action_vohieuhoathietlapmuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU2, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU2, bytes.fromhex("90 90 90 90 90"), 5)
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU2, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU2, bytes.fromhex("90 90 90 90 90 90"), 6)
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU, bytes.fromhex("90 90 90 90 90"), 5)
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU, bytes.fromhex("90 90 90 90 90 90"), 6)

    def action_tatvohieuhoathietlapmuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU2, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU2, bytes.fromhex("A3"), 1)
            write_int(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU2 + 1, self.diachixq + DC.MUCTIEUDANGCHON2)
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU2, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU2, bytes.fromhex("89 0D"), 2)
            write_int(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU2 + 2, self.diachixq + DC.IDMUCTIEUDANGCHON2)
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU, bytes.fromhex("A3"), 1)
            write_int(self.tientrinh, self.diachixq + DC.VA_GHIMUCTIEU + 1, self.diachixq + DC.MUCTIEUDANGCHON)
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU, bytes.fromhex("89 15"), 2)
            write_int(self.tientrinh, self.diachixq + DC.VA_GHIIDMUCTIEU + 2, self.diachixq + DC.IDMUCTIEUDANGCHON)

    def action_vohieuhoaxoamuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_XOAIDMUCTIEU2, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + DC.VA_XOAIDMUCTIEU2, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_XOAMUCTIEU, 1) != bytes.fromhex("90"): write_bytes(self.tientrinh, self.diachixq + DC.VA_XOAMUCTIEU, bytes.fromhex("90 90 90 90 90 90 90 90 90 90"), 10)

    def action_tatvohieuhoaxoamuctieu(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_XOAIDMUCTIEU2, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + DC.VA_XOAIDMUCTIEU2, bytes.fromhex("C7 05"), 2)
            write_int(self.tientrinh, self.diachixq + DC.VA_XOAIDMUCTIEU2 + 2, self.diachixq + DC.IDMUCTIEUDANGCHON2)
            write_int(self.tientrinh, self.diachixq + DC.VA_XOAIDMUCTIEU2 + 6, 0)
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_XOAMUCTIEU, 1) == bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + DC.VA_XOAMUCTIEU, bytes.fromhex("C7 05"), 2)
            write_int(self.tientrinh, self.diachixq + DC.VA_XOAMUCTIEU + 2, self.diachixq + DC.MUCTIEUDANGCHON)
            write_int(self.tientrinh, self.diachixq + DC.VA_XOAMUCTIEU + 6, 0)

    def action_vohieuhoalongclick(self):
        if read_int(self.tientrinh, self.diachixq + DC.VA_LONGCLICK + 0x6) != 0: write_int(self.tientrinh, self.diachixq + DC.VA_LONGCLICK + 0x6, 0)

    def action_tatvohieuhoalongclick(self):
        if read_int(self.tientrinh, self.diachixq + DC.VA_LONGCLICK + 0x6) != 1: write_int(self.tientrinh, self.diachixq + DC.VA_LONGCLICK + 0x6, 1)

    def action_vohieuhoatrangthaichuotchonmuctieukynang(self):
        if read_int(self.tientrinh, self.diachixq + DC.VA_CHUOTCHONMUCTIEUKYNANG + 0x6) != 0: write_int(self.tientrinh, self.diachixq + DC.VA_CHUOTCHONMUCTIEUKYNANG + 0x6, 0)

    def action_tatvohieuhoatrangthaichuotchonmuctieukynang(self):
        if read_int(self.tientrinh, self.diachixq + DC.VA_CHUOTCHONMUCTIEUKYNANG + 0x6) != 2: write_int(self.tientrinh, self.diachixq + DC.VA_CHUOTCHONMUCTIEUKYNANG + 0x6, 2)

    def action_chantangcapdo(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_TANGCAPDO, 1) == bytes.fromhex("E8"): write_bytes(self.tientrinh, self.diachixq + DC.VA_TANGCAPDO, bytes.fromhex("83 C4 08 90 90"), 5)

    def action_bochantangcapdo(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_TANGCAPDO, 1) == bytes.fromhex("83"):
            write_bytes(self.tientrinh, self.diachixq + DC.VA_TANGCAPDO, bytes.fromhex("E8"), 1)
            write_int(self.tientrinh, self.diachixq + DC.VA_TANGCAPDO + 1, self.diachixq + DC.HAMTANGCAPDO - (self.diachixq + DC.VA_TANGCAPDO) - 5)

    def action_vohieuhoakhoanhvungkynang(self):
        pass

    def action_tatvohieuhoakhoanhvungkynang(self):
        pass

    def action_vohieuhoaphimspace(self):
        pass

    def action_tatvohieuhoaphimspace(self):
        pass

    def action_vohieuhoahookchienquoc2(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.HAMGUILENH, 1) != bytes.fromhex("90"):
            write_bytes(self.tientrinh, self.diachixq + DC.HAMGUILENH, b'\x90\x90\x90\x90\x90', 5)

    def action_vohieuhieuungmuloa(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_HIEUUNGMULOA + 0x6, 1) != bytes.fromhex("00"): write_bytes(self.tientrinh, self.diachixq + DC.VA_HIEUUNGMULOA + 0x6, bytes.fromhex("00"), 1)

    def action_vohieuhoadichuyen(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_DICHUYEN, 1) != bytes.fromhex("EB"): write_bytes(self.tientrinh, self.diachixq + DC.VA_DICHUYEN, bytes.fromhex("EB"), 1)

    def action_tatvohieuhoadichuyen(self):
        if read_bytes(self.tientrinh, self.diachixq + DC.VA_DICHUYEN, 1) != bytes.fromhex("7E"): write_bytes(self.tientrinh, self.diachixq + DC.VA_DICHUYEN, bytes.fromhex("7E"), 1)

    def get_is_dangmobando(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_TIMDUONG)
        return read_boolean(self.tientrinh, x) if x else False

    def get_is_danghiencuasoyesno(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_CUASOYESNO)
        return read_boolean(self.tientrinh, x + 0x34) if x else False

    def set_is_danghiencuasoyesno(self, is_danghiencuasoyesno):
        if self.get_is_danghiencuasoyesno() != is_danghiencuasoyesno:
            x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
            if x:
                x = read_int(self.tientrinh, x + DC.TG_CUASOYESNO)
                if x: write_boolean(self.tientrinh, x + 0x34, is_danghiencuasoyesno)

    def get_is_danghiencuasotuychon(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_CUASOTUYCHON)
        return read_boolean(self.tientrinh, x + 0x1E38) if x else False

    def _get_diachicuasotuychon(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return read_int(self.tientrinh, x + DC.TG_CUASOTUYCHON) if x else 0

    def get_noidungcuasotuychon(self):
        # Lời thoại của menu hội thoại NPC gần nhất (cửa sổ tuỳ chọn + 0x34, bỏ mã màu), giữ nguyên cả khi cửa sổ đã đóng
        x = self._get_diachicuasotuychon()
        if not x:
            return ""
        return re.sub(r'\x1b.', '', read_bytes(self.tientrinh, x + 0x34, 1024).split(b"\0")[0].decode("utf-8", "ignore"))

    def xoa_noidungcuasotuychon(self):
        # Xoá lời thoại đang giữ để biết khi nào menu mới (trả lời của lệnh vừa gửi) về tới
        x = self._get_diachicuasotuychon()
        if x:
            write_bytes(self.tientrinh, x + 0x34, b"\0", 1)

    def get_lenhcuasotuychons(self):
        # Lệnh của từng lựa chọn trong menu hội thoại NPC gần nhất theo thứ tự (+ 0x1070, mỗi ô 0xC9 byte, số lựa chọn ở + 0x1DB8),
        # vd ["talk 87bd# info.21", "CLOSE"]. Nhãn lựa chọn không lưu ở đây (chỉ có trong gói tin)
        x = self._get_diachicuasotuychon()
        if not x:
            return []
        soluachon = read_int(self.tientrinh, x + 0x1DB8)
        if not 0 < soluachon <= 20:
            return []
        return [read_bytes(self.tientrinh, x + 0x1070 + k * 0xC9, 0xC9).split(b"\0")[0].decode("utf-8", "ignore") for k in range(soluachon)]

    def set_is_danghiencuasotuychon(self, is_danghiencuasotuychon):
        if self.get_is_danghiencuasotuychon() != is_danghiencuasotuychon:
            x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
            if x:
                x = read_int(self.tientrinh, x + DC.TG_CUASOTUYCHON)
                if x: write_boolean(self.tientrinh, x + 0x1E38, is_danghiencuasotuychon)

    def get_caulenhmoinhomhientai(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_CUASOYESNO)
        return read_string(self.tientrinh, x + 0x7C).strip() if x else False

    def _get_is_duocbatdaudichuyen(self):
        # Đang đứng mà sắp chạy: phải tới lượt (các nhân vật lần lượt nhấc chân, không cùng lúc). Đang chạy rồi thì chỉnh hướng tự do.
        # Không chờ: chưa tới lượt thì bỏ lần này, loop di chuyển tự gọi lại ngay sau
        if not self.dieuphoidichuyen or self.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
            return True
        return self.dieuphoidichuyen.thuxinluot()

    def _get_chuoihuongtimduongcucbo(self, x1, y1, x2, y2):
        # Gọi hàm tìm đường cục bộ của client xq + 0x4B0D60 (hàm dùng khi click chuột: thiscall, ecx = [thông tin game] + 0xAE1178,
        # tham số x1, y1, x2, y2, buf, 100) => chuỗi hướng '1'..'8' né vật cản ('1' (+1, 0), '2' (+1, -1), '3' (0, -1), '4' (-1, -1),
        # '5' (-1, 0), '6' (-1, +1), '7' (0, +1), '8' (+1, +1)). Chưa có đối tượng tìm đường (client chưa click lần nào) thì None
        if not self._diachitimduongcucbo:
            vung = self.tientrinh.allocate(512)
            self._dulieutimduongcucbo, self._buftimduongcucbo = vung + 0x80, vung + 0x100
            dulieu = self._dulieutimduongcucbo
            ma = f"""
                mov eax, dword ptr [{hex(self.diachixq + DC.THONGTINGAME)}]
                mov ecx, dword ptr [eax + {hex(DC.TG_TIMDUONGCUCBO)}]
                test ecx, ecx
                je ketthuc
                push 0x64
                push {hex(self._buftimduongcucbo)}
                push dword ptr [{hex(dulieu + 12)}]
                push dword ptr [{hex(dulieu + 8)}]
                push dword ptr [{hex(dulieu + 4)}]
                push dword ptr [{hex(dulieu)}]
                mov eax, {hex(self.diachixq + DC.HAMTIMDUONGCUCBO)}
                call eax
            ketthuc:
                ret
            """
            encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(ma)
            write_bytes(self.tientrinh, vung, bytes(encoding), len(encoding))
            self._diachitimduongcucbo = vung
        if not self.get_is_cotimduongcucbo():
            return None
        with self._khoatimduongcucbo:
            write_bytes(self.tientrinh, self._dulieutimduongcucbo, struct.pack("<iiii", x1, y1, x2, y2), 16)
            write_bytes(self.tientrinh, self._buftimduongcucbo, bytes(100), 100)
            self.tientrinh.start_thread(self._diachitimduongcucbo)
            return read_bytes(self.tientrinh, self._buftimduongcucbo, 100).split(b"\0")[0] or None

    def get_is_cotimduongcucbo(self):
        # Client đã tạo đối tượng tìm đường cục bộ chưa (tạo khi click di chuyển lần đầu)
        thongtingame = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return bool(thongtingame and read_int(self.tientrinh, thongtingame + DC.TG_TIMDUONGCUCBO))

    def action_dichuyenoo(self, x, y, delay = 0.05, sobuoctoida = None, is_dungkedich = False, thoigiantinhlai = 0.):
        # sobuoctoida: chỉ ghi chừng này bước đầu của chuỗi (hết bước thì lần gọi sau tìm đường lại). is_dungkedich: bỏ bước cuối, dừng ở
        # ô kề đích (đích là ô mục tiêu đang đứng). thoigiantinhlai: tìm đường lại và ghi đoạn mới mỗi chừng này giây kể cả khi đích không
        # đổi (như client tính lại liên tục trong lúc đi, chuỗi không cạn giữa đường => không khựng / không phải chờ lượt nhấc chân)
        # Đi tới đúng ô (x, y): lấy chuỗi hướng từ hàm tìm đường cục bộ của client rồi ghi vào chuỗi đường đi xq + 0x1FC2B4 (từ chỉ số 1)
        # và đặt chỉ số bước xq + 0x380AFC = 1 => client tự gửi "go x,y <chuỗi>" mỗi ~0.5s 2 bước tới hết chuỗi (thử trên Ngọc: lệch 0 ô).
        # Không qua click điểm ảnh nên không lệch theo camera / khung màn hình. False: bị chặn (vô hiệu hoá di chuyển, khoá vận khí, đang xuất chiêu, chưa tới lượt); None: không tìm
        # được đường (nơi gọi dùng tự động tìm đường của game)
        if self._is_vohieuhoadichuyen:
            return False
        if self.get_is_khoavankhitrieuhoi() or self.get_is_dangxuatchieu():
            return False
        if time.time() - self._thoidiemdichuyengannhat < delay:
            return False
        if not self._get_is_duocbatdaudichuyen():
            return False
        dichtrongtran = self._kepdichtrongtrando(x, y)
        if dichtrongtran is None:
            return False
        x, y = round(dichtrongtran[0]), round(dichtrongtran[1])
        diachinhanvat = self.get_diachicosothongtinnhanvat1()
        if not diachinhanvat:
            return None
        xsaptoi, ysaptoi = struct.unpack("<ii", read_bytes(self.tientrinh, diachinhanvat + 0x18, 8))
        if (xsaptoi, ysaptoi) == (x, y):
            return False
        # Đang đi theo ô tới đúng đích này (chuỗi chưa hết) thì để client đi tiếp, ghi lại chuỗi làm đứt nhịp gửi "go"
        if thoigiantinhlai:
            if self.get_idlenhdichuyen() and time.time() - self._thoidiemdichuyengannhat < thoigiantinhlai:
                return True
        elif self._dichdioogannhat == (x, y) and self.get_idlenhdichuyen():
            return True
        chuoihuong = self._get_chuoihuongtimduongcucbo(xsaptoi, ysaptoi, x, y)
        if not chuoihuong:
            return None
        if is_dungkedich:
            chuoihuong = chuoihuong[:-1]
            if not chuoihuong:
                return False
        if sobuoctoida:
            chuoihuong = chuoihuong[:sobuoctoida]
        # Huỷ đích tự động tìm đường đang có: game tự tìm đường lại khi đứng yên và ghi đè chuỗi đi theo ô (2 nguồn cùng gửi "go")
        self.action_ngungtudongtimduong()
        self._dichdioogannhat = (x, y)
        khoidieukhien = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if khoidieukhien:
            write_bytes(self.tientrinh, khoidieukhien + DC.KDK_DICHCLICK, bytes(8), 8)
        write_bytes(self.tientrinh, self.diachixq + DC.CHUOIDUONGDI, b"\0" + chuoihuong + bytes(99 - len(chuoihuong)), 100)
        self.set_idlenhdichuyen(1)
        self._thoidiemdichuyengannhat = time.time()
        self._thoidiemboquadichuyencungtoadogannhat = time.time()
        return True

    def get_is_duongdicatvungcam(self, x1, y1, x2, y2):
        # Đường chạy thẳng (x1, y1) -> (x2, y2) có chạm vùng cấm của bản đồ hiện tại không (VUNGCAM_MAP: đi vào sẽ bị chuyển bản đồ)
        danhsachvungcam = VUNGCAM_MAP.get(self.get_idbandohientai())
        if not danhsachvungcam:
            return False
        dx, dy = x2 - x1, y2 - y1
        dodai2 = dx * dx + dy * dy
        for vung in danhsachvungcam:
            if vung["type"] == "circle":
                px, py = vung["x"], vung["y"]
                t = max(0., min(1., ((px - x1) * dx + (py - y1) * dy) / dodai2)) if dodai2 else 0.
                if math.dist((px, py), (x1 + t * dx, y1 + t * dy)) <= vung["r"]:
                    return True
            elif vung["type"] == "line":
                sobuoc = max(1, int(math.sqrt(dodai2)))
                for i in range(sobuoc + 1):
                    t = i / sobuoc
                    px, py = x1 + t * dx, y1 + t * dy
                    ax, ay, bx, by = vung["x1"], vung["y1"], vung["x2"], vung["y2"]
                    vx, vy = bx - ax, by - ay
                    v2 = vx * vx + vy * vy
                    u = max(0., min(1., ((px - ax) * vx + (py - ay) * vy) / v2)) if v2 else 0.
                    if math.dist((px, py), (ax + u * vx, ay + u * vy)) <= vung["r"]:
                        return True
        return False

    def _action_dichuyentheovector(self, x1, y1, deltax, deltay, delay = 0.05, is_bokiemtravungcam = False):
        # deltax, deltay: độ lệch theo đơn vị toạ độ game tính từ bản thân (deltay = y1 - y2)
        if not deltax and not deltay:
            return False

        xdich, ydich = x1 + deltax, y1 - deltay

        # Đang bị Trận Pháp Lạc Ảnh giữ thì không bấm ra ngoài trận
        dichtrongtran = self._kepdichtrongtrando(xdich, ydich)
        if dichtrongtran is None:
            return False
        if dichtrongtran != (xdich, ydich):
            xdich, ydich = dichtrongtran
            deltax, deltay = xdich - x1, y1 - ydich

        # Lớp chặn cuối: mọi kiểu di chuyển (tiếp cận, lùi giữ khoảng cách, phủ đầu...) đều không được cắt qua vùng cấm
        # (trừ khi chạy theo trưởng nhóm: lỡ đứng trong vùng cấm thì mọi đường đi đều "cắt vùng cấm" và nhân vật bị kẹt luôn)
        if self.is_tranhvungcam and not is_bokiemtravungcam and self.get_is_duongdicatvungcam(x1, y1, xdich, ydich):
            return False

        # Bỏ qua nếu vẫn đang chạy tới đúng điểm đích vừa gửi (tránh gửi dồn làm nhân vật khựng lại)
        if time.time() - self._thoidiemboquadichuyencungtoadogannhat < 0.3 and math.dist((xdich, ydich), (self._xdichuyengannhat, self._ydichuyengannhat)) < 0.5 and self.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
            return True

        if (round(xdich), round(ydich)) == (x1, y1):
            return False

        # Đi theo ô (tìm đường cục bộ của client, đúng ô đích). Rối Loạn chỉ đảo hướng chuột ở client, chuỗi hướng ghi thẳng vào bộ nhớ
        # không bị đảo nên vẫn đi theo ô được. Không ra đường (chưa có đối tượng tìm đường, xa / bị bao kín) thì dùng tự động tìm đường của game.
        # Đã bỏ hẳn di chuyển bằng click điểm ảnh (lệch theo camera, không có sự kiện nhả chuột nên dính long click)
        nhan = "ĐI Ô"
        is_ok = self.action_dichuyenoo(round(xdich), round(ydich), delay = delay)
        if is_ok is None:
            nhan = "TÌM ĐƯỜNG"
            is_ok = self.action_tudongtimduong(round(xdich), round(ydich), self.get_idbandohientai(), is_lotrinh = False)
        if is_ok and IS_LOGDICHUYEN and (round(xdich), round(ydich)) != self._dichclicklogcuoi:
            self._dichclicklogcuoi = (round(xdich), round(ydich))
            self._inlog(f"[{nhan}] từ {(x1, y1)} (đang ở {self.get_toado()}, tư thế {self.get_idtuthenhanvat()}) -> {(round(xdich, 1), round(ydich, 1))}")
        if is_ok:
            self._xdichuyengannhat, self._ydichuyengannhat = xdich, ydich
            self._thoidiemboquadichuyencungtoadogannhat = time.time()
        return is_ok

    def action_dichuyengiukhoangcachtoithieu(self, diachicosothongtinnhanvat2, khoangcachtoithieu, khoangcachdichuyentoida = 0, delay = 0.05):
        if not diachicosothongtinnhanvat2 or not self.get_iddoituong(diachicosothongtinnhanvat2):
            return False
        return self.action_dichuyengiukhoangcachtoithieudiem(*self.get_toado(diachicosothongtinnhanvat2), khoangcachtoithieu = khoangcachtoithieu, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyengiukhoangcachtoida(self, diachicosothongtinnhanvat2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.05):
        if not diachicosothongtinnhanvat2 or not self.get_iddoituong(diachicosothongtinnhanvat2):
            return False

        if khoangcachtoida <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
            return self._tiepcancanchien(diachicosothongtinnhanvat2, khoangcachtoida)
        toadomuctieu = self._laytoadodondau(diachicosothongtinnhanvat2)
        # Tiếp cận luôn bằng tìm đường của game (đo A/B: click lệch tâm màn hình quay đầu không lý do 5.3/ph, tìm đường 1.3/ph)
        return self._tiepcanbangtimduong(*toadomuctieu, khoangcachtoida)

    def _tiepcancanchien(self, diachimuctieu, khoangcachtoida):
        # Tiếp cận cận chiến như client khi bấm chiêu trên phím tắt (xq + 0x1873A): tìm đường tới ô mục tiêu đang đứng, không đón đầu,
        # mỗi lần chỉ SOBUOCTIEPCANCANCHIEN bước (client ghi KDK + 0x1620 = 2), đổi đích thì THOIGIANTINHLAITIEPCANCANCHIEN giây mới tìm lại,
        # dừng khi đã kề mục tiêu (ô lệch không quá 1 theo cả x lẫn y) => không chạy quá / xuyên qua khi mục tiêu dừng hay quay đầu
        # Như client: so theo ô đích bước đang đi (+ 0x18, + 0x1C) của cả mình lẫn mục tiêu, không phải toạ độ đang vẽ (+ 0x0)
        diachinhanvat = self.get_diachicosothongtinnhanvat1()
        if not diachinhanvat:
            return False
        x1, y1 = struct.unpack("<ii", read_bytes(self.tientrinh, diachinhanvat + 0x18, 8))
        x2, y2 = struct.unpack("<ii", read_bytes(self.tientrinh, diachimuctieu + 0x18, 8))
        xhientai, yhientai = struct.unpack("<ii", read_bytes(self.tientrinh, diachimuctieu, 8))

        def kc(xa, ya):
            return max(abs(xa - x1), abs(ya - y1))

        # Đã kề: còn chuỗi bước thì ngắt ngay, không chạy xuyên qua mục tiêu (ngắt chỉ chặn client tự bước THOIGIANCHANTUDICHUYENCLIENT)
        # Mục tiêu đang đi về phía mình và bước tới đã gần (KHOANGCACHCHOMUCTIEUTOI ô) thì đứng chờ nó tới, không đi rồi quay đầu
        if kc(x2, y2) <= 1 or (kc(x2, y2) < kc(xhientai, yhientai) and kc(x2, y2) <= KHOANGCACHCHOMUCTIEUTOI):
            if self.get_idlenhdichuyen():
                self.action_ngatdichuyen()
            return False

        # Mục tiêu chạy ra xa mà còn cách xa (KHOANGCACHDONDAUCANCHIEN ô): đón đầu nhẹ (tối đa QUANGDONDAUCANCHIEN ô), gần rồi thì nhắm ô
        # của nó như client. Chạy xuyên đã có chặn ở trên: vừa kề là ngắt
        nhan = "TIẾP CẬN CẬN CHIẾN"
        xdich, ydich = x2, y2
        if kc(x2, y2) >= KHOANGCACHDONDAUCANCHIEN:
            xdon, ydon = self._laytoadodondau(diachimuctieu, quangdondautoida = QUANGDONDAUCANCHIEN)
            if (round(xdon), round(ydon)) != (xhientai, yhientai):
                xdich, ydich, nhan = round(xdon), round(ydon), "TIẾP CẬN CẬN CHIẾN ĐÓN ĐẦU"
        if self.is_tranhvungcam and self.get_is_duongdicatvungcam(x1, y1, xdich, ydich):
            return self.action_dichuyengiukhoangcachtoidadiem(xdich, ydich, khoangcachtoida)
        is_ok = self.action_dichuyenoo(xdich, ydich, delay = 0., sobuoctoida = SOBUOCTIEPCANCANCHIEN, is_dungkedich = True,
                                       thoigiantinhlai = THOIGIANTINHLAITIEPCANCANCHIEN)
        if is_ok is None:
            # Không ra đường (chưa có đối tượng tìm đường, xa / bị bao kín): tự động tìm đường của game như cũ
            return self._tiepcanbangtimduong(xdich, ydich, khoangcachtoida)
        if is_ok and IS_LOGDICHUYEN and (xdich, ydich) != self._dichclicklogcuoi:
            self._dichclicklogcuoi = (xdich, ydich)
            self._inlog(f"[{nhan}] (đang ở {(x1, y1)}, tư thế {self.get_idtuthenhanvat()}) -> {(xdich, ydich)}, mục tiêu {(x2, y2)}")
        return is_ok

    def action_dichuyengiukhoangcachtoidadiembangtimduong(self, x2, y2, khoangcachtoida):
        if x2 <= 0 or y2 <= 0:
            return False
        return self._tiepcanbangtimduong(x2, y2, khoangcachtoida)

    def _tiepcanbangtimduong(self, x2, y2, khoangcachtoida):
        # Tiếp cận bằng tìm đường của game với tọa độ ô tuyệt đối (không quy đổi ô <-> pixel quanh tâm màn hình như click):
        # đích là ô trên đường thẳng mình -> mục tiêu, cách mục tiêu khoangcachtoida
        x1, y1 = self.get_toado()
        khoangcach = math.dist((x1, y1), (x2, y2))
        if khoangcach <= max(0., khoangcachtoida) or khoangcach <= 0.:
            return False
        tyle = max(0., khoangcachtoida) / khoangcach
        xdich, ydich = round(x2 + (x1 - x2) * tyle), round(y2 + (y1 - y2) * tyle)
        if (xdich, ydich) == (x1, y1):
            return False
        # Game không biết vùng cấm: đích tìm đường rơi vào vùng cấm thì đi theo vector (có lớp chặn đường đi cắt vùng cấm)
        if self.is_tranhvungcam and self.get_is_duongdicatvungcam(xdich, ydich, xdich, ydich):
            return self.action_dichuyengiukhoangcachtoidadiem(x2, y2, khoangcachtoida)
        # Đi theo ô (tìm đường cục bộ của client, không hiện "Bắt đầu / Hoàn tất tự động tìm đường"); không ra đường (xa quá 100 bước,
        # chưa có đối tượng tìm đường) thì dùng tự động tìm đường của game như cũ
        nhan = "TIẾP CẬN ĐI Ô"
        is_ok = self.action_dichuyenoo(xdich, ydich, delay = 0.)
        if is_ok is None:
            nhan = "TIẾP CẬN TÌM ĐƯỜNG"
            is_ok = self.action_tudongtimduong(xdich, ydich, self.get_idbandohientai(), is_lotrinh = False)
        if is_ok and IS_LOGDICHUYEN and (xdich, ydich) != self._dichclicklogcuoi:
            self._dichclicklogcuoi = (xdich, ydich)
            self._inlog(f"[{nhan}] (đang ở {(x1, y1)}, tư thế {self.get_idtuthenhanvat()}) -> {(xdich, ydich)}")
        return is_ok

    def _laytoadodondau(self, diachimuctieu, quangdondautoida = 6.0):
        # Mục tiêu đang chạy ra xa: click vào vị trí hiện tại thì tới nơi nó đã chạy tiếp (đuổi theo cái bóng, không bao giờ kịp).
        # Ước lượng vận tốc từ vị trí trong ~1s gần nhất rồi nhắm điểm phía trước mục tiêu.
        x, y = self.get_toado(diachimuctieu)
        thoidiemhientai = time.time()
        lichsu = self._lichsutoadomuctieu_map.setdefault(diachimuctieu, [])
        lichsu.append((thoidiemhientai, x, y))
        while lichsu and thoidiemhientai - lichsu[0][0] > 1.0:
            lichsu.pop(0)
        if len(self._lichsutoadomuctieu_map) > 30:
            for diachi in [k for k, v in self._lichsutoadomuctieu_map.items() if not v or thoidiemhientai - v[-1][0] > 5.]:
                del self._lichsutoadomuctieu_map[diachi]

        thoigiando = thoidiemhientai - lichsu[0][0]
        if thoigiando < 0.3:
            return x, y
        vx, vy = (x - lichsu[0][1]) / thoigiando, (y - lichsu[0][2]) / thoigiando
        tocdo = math.hypot(vx, vy)
        if tocdo < 1.0:
            return x, y

        x1, y1 = self.get_toado()
        # Chỉ đón đầu khi mục tiêu đang chạy ra xa mình; chạy về phía mình thì cứ nhắm vị trí hiện tại
        if (x - x1) * vx + (y - y1) * vy <= 0:
            return x, y
        khoangcach = math.dist((x1, y1), (x, y))
        quangdondau = min(tocdo * min(1.5, khoangcach / tocdo), quangdondautoida)
        return x + vx / tocdo * quangdondau, y + vy / tocdo * quangdondau

    def action_dichuyenphudau(self, diachicosothongtinnhanvat2, khoangcachphudau = 1, delay = 0.05):
        if not diachicosothongtinnhanvat2 or not self.get_iddoituong(diachicosothongtinnhanvat2):
            return False
        x2, y2 = self.get_toado(diachicosothongtinnhanvat2)
        x1, y1 = self.get_toado()
        deltax, deltay = x2 - x1, y1 - y2
        khoangcach = math.dist((x1, y1), (x2, y2))
        khoangcachdichuyen = khoangcach + khoangcachphudau
        if khoangcachdichuyen <= 0.:
            return False
        if khoangcach > 0.:
            deltax, deltay = khoangcachdichuyen * deltax / khoangcach, khoangcachdichuyen * deltay / khoangcach
        else:
            deltax, deltay = khoangcachdichuyen, khoangcachdichuyen
        return self._action_dichuyentheovector(x1, y1, deltax, deltay, delay = delay)

    def action_dichuyengiukhoangcachtoidadiem(self, x2, y2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.05, is_bokiemtravungcam = False):
        if x2 <= 0 or y2 <= 0:
            return False

        # Đang chạy thì tính từ ô sắp tới (click lệch theo tâm màn hình, mà màn hình đã đi theo nhân vật về phía trước),
        # nhưng chỉ khi ô sắp tới gần đích hơn ô hiện tại; không thì tính từ ô hiện tại (hướng click không chỉ ngược ra sau)
        xhientai, yhientai = self.get_toado()
        x1, y1 = xhientai, yhientai
        xsap, ysap = self.get_toado(is_toadosaptoi = True)
        if math.dist((xsap, ysap), (x2, y2)) < math.dist((xhientai, yhientai), (x2, y2)):
            x1, y1 = xsap, ysap
        khoangcach = math.dist((x1, y1), (x2, y2))
        if khoangcach <= 0.:
            return False

        khoangcachdichuyen = khoangcach - max(0., khoangcachtoida)
        if khoangcachdichuyen <= 0.:
            return False

        if khoangcachdichuyentoida:
            khoangcachdichuyen = min(float(khoangcachdichuyentoida), khoangcachdichuyen)

        deltax = khoangcachdichuyen * (x2 - x1) / khoangcach
        deltay = khoangcachdichuyen * (y1 - y2) / khoangcach

        # Lớp chặn cuối: điểm sắp click phải gần đích hơn chỗ đang đứng (chỉ được rút ngắn khoảng cách, không đi vòng / quay đầu)
        if math.dist((x1 + deltax, y1 - deltay), (x2, y2)) >= math.dist((xhientai, yhientai), (x2, y2)):
            return False

        return self._action_dichuyentheovector(x1, y1, deltax, deltay, delay = delay, is_bokiemtravungcam = is_bokiemtravungcam)

    def action_dichuyengiukhoangcachtoithieudiem(self, x2, y2, khoangcachtoithieu, khoangcachdichuyentoida = 0, delay = 0.05):
        if x2 <= 0 or y2 <= 0:
            return False

        x1, y1 = self.get_toado()
        khoangcach = math.dist((x1, y1), (x2, y2))
        if khoangcach >= khoangcachtoithieu:
            return False

        # Chỉ lùi phần còn thiếu (+0.5 dư) thay vì lùi nguyên khoảng cách tối thiểu
        khoangcachdichuyen = khoangcachtoithieu - khoangcach + 0.5
        if khoangcachdichuyentoida:
            khoangcachdichuyen = min(float(khoangcachdichuyentoida), khoangcachdichuyen)

        if khoangcach > 0.:
            deltax = -khoangcachdichuyen * (x2 - x1) / khoangcach
            deltay = -khoangcachdichuyen * (y1 - y2) / khoangcach
        else:
            # Đứng trùng vị trí mục tiêu: chọn hướng ngẫu nhiên để thoát ra
            goc = random.uniform(0, 2 * math.pi)
            deltax, deltay = khoangcachdichuyen * math.cos(goc), khoangcachdichuyen * math.sin(goc)

        return self._action_dichuyentheovector(x1, y1, deltax, deltay, delay = delay)

    def action_dichuyentiepcan(self, diachi2, khoangcachdichuyentoida = 0, delay = 0.05):
        return self.action_dichuyengiukhoangcachtoida(diachi2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyentiepcandiem(self, x2, y2, khoangcachdichuyentoida = 0, delay = 0.05):
        if x2 <= 0 or y2 <= 0:
            return False
        return self.action_dichuyengiukhoangcachtoidadiem(x2, y2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_sudungkynangvitriphudau(self, idvitri_x, idvitri_y, diachi2, khoangcachphudau, delay = 1):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return False
        idvitri_x, idvitri_y = vitri
        if not diachi2 or not self.get_is_nhanvattontai(diachi2):
            return False
        return self.action_sudungkynangvitriphudaudiem(idvitri_x, idvitri_y, *self.get_toado(diachi2), khoangcachphudau = khoangcachphudau, delay = delay)

    def action_sudungkynangvitriphudaudiem(self, idvitri_x, idvitri_y, x2, y2, khoangcachphudau, delay = 1):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return False
        idvitri_x, idvitri_y = vitri
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
        x = read_int(self.tientrinh, self.diachixq + DC.CUASOTUYCHONNHANVAT)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0x2C)
        return False if x <= 10 else True

    def action_chovankhi(self, thoigian):
        # Kỹ năng vận khí cần một lúc mới bật trạng thái "Đang vận khí"; coi như đang vận khí trong khoảng chờ đó để không thao tác gì làm ngắt chiêu
        self._thoidiemhetchovankhi = max(self._thoidiemhetchovankhi, time.time() + thoigian)

    def action_huychovankhi(self):
        # Bỏ khoảng chờ vận khí giả (action_chovankhi) khi chủ động ngắt vận khí để di chuyển / dùng chiêu khác.
        # Đang khoá vận khí triệu hồi bảo thú thì không bỏ
        if not self.get_is_khoavankhitrieuhoi():
            self._thoidiemhetchovankhi = 0.

    def action_khoavankhitrieuhoi(self, caulenhduocpheps = ()):
        # Triệu hồi bảo thú (tốn bùa, thất bại là mất bùa): khoá các thao tác ngắt vận khí (ra chiêu / đánh thường, di chuyển,
        # tìm đường) cho tới khi vận khí xong. caulenhduocpheps: chính lệnh triệu hồi (đã vào hàng đợi) vẫn được gửi
        thoidiemhientai = time.time()
        self._khoavankhitrieuhoi = {
            "batdau": thoidiemhientai,
            "toida": thoidiemhientai + THOIGIANKHOAVANKHITRIEUHOITOIDA,
            "caulenhduocpheps": set(caulenhduocpheps),
        }
        self.action_chovankhi(THOIGIANCHOVAOVANKHI)
        self._inlog(f"[KHOÁ VẬN KHÍ TRIỆU HỒI] bắt đầu, cho phép {sorted(caulenhduocpheps)}")

    def get_is_dangxuatchieu(self):
        # Đang xuất chiêu (tư thế tấn công vật lý 6 / phép 9; 11 chỉ còn khi bot tự ghi) hoặc chưa hết THOIGIANKHUNGSAUXUATCHIEU giây
        # khựng sau khi hết tư thế xuất chiêu (game không có tư thế riêng cho khựng): vẫn được dùng kỹ năng nhưng TUYỆT ĐỐI không
        # di chuyển (di chuyển lúc này vẫn tính hồi chiêu mà chiêu mất tác dụng). Đo 2026-10-25: game giữ tư thế 6 ~0.68s rồi về
        # thẳng 1 / 2. Các hàm phát lệnh di chuyển đều kiểm tra hàm này; luồng nhanh gọi liên tục để cập nhật mốc xuất chiêu
        # Chỉ tính chiêu cần đứng yên (set_is_chieucanngatdichuyen theo chiêu bot gửi gần nhất). Hoạt ảnh xuất chiêu (~0.68s) luôn giữ
        # trọn (cắt ngang bị game đánh vi phạm); phần khựng sau đó thì thả sớm khi chiêu đã tác động xong: mục tiêu đã chết / biến mất,
        # hoặc mục tiêu đã hiện số bay (server báo trúng, _is_muctieudatrungchieu); không thấy thì giữ tối đa THOIGIANKHUNGSAUXUATCHIEU
        thoidiemhientai = time.time()
        if self._is_chieucanngatdichuyen \
                and self.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
            if self._is_khungsauxuatchieu:
                self._thoidiemxuatchieugannhat = thoidiemhientai
            self._is_muctieudatrungchieu()
            return True
        if thoidiemhientai - self._thoidiemxuatchieugannhat >= THOIGIANKHUNGSAUXUATCHIEU:
            return False
        if self._is_muctieuxuatchieudahet() or self._is_muctieudatrungchieu():
            self._thoidiemxuatchieugannhat = 0.
            return False
        return True

    def _is_muctieuxuatchieudahet(self):
        if not self._diachimuctieuxuatchieu:
            return False
        return self.get_iddoituong(self._diachimuctieuxuatchieu) != self._idmuctieuxuatchieu \
            or self.get_is_nhanvatdachet(self._diachimuctieuxuatchieu)

    def _docsobaydoituong(self, diachi):
        # Số máu bay trên đầu đối tượng (dịch ngược xq + 0x1BD21): 10 ô, giá trị + 0x11C4 (dương = mất máu, âm = hồi máu),
        # bộ đếm khung + 0x1214 (0 -> ~50-70 rồi ô bị xoá về 0). Server báo chiêu trúng thì 1 ô đổi sang số mới, bộ đếm chạy lại từ 0
        try:
            dulieu = read_bytes(self.tientrinh, diachi + DC.NV_SOBAY, 0x78)
        except Exception:
            return None
        return struct.unpack("<10i", dulieu[:40]), struct.unpack("<10i", dulieu[80:120])

    def _is_muctieudatrungchieu(self):
        # Mục tiêu đã hiện số bay mới so với lúc gửi chiêu (chiêu đánh: mất máu, chiêu hồi: hồi máu). Nhớ lại kết quả (số bay mờ đi sau ~1s)
        if self._is_datrungchieu:
            return True
        if not self._diachimuctieuxuatchieu or not self._sobaymuctieuxuatchieu:
            return False
        sobay = self._docsobaydoituong(self._diachimuctieuxuatchieu)
        if not sobay:
            return False
        (giatricu, demcu), (giatri, dem) = self._sobaymuctieuxuatchieu, sobay
        for i in range(10):
            if giatri[i] and (giatri[i] != giatricu[i] or dem[i] < demcu[i]):
                self._is_datrungchieu = True
                return True
        self._sobaymuctieuxuatchieu = sobay
        return False

    def set_is_chieucanngatdichuyen(self, is_chieucanngatdichuyen, diachimuctieu = None, is_khungsauxuatchieu = True):
        self._is_chieucanngatdichuyen = is_chieucanngatdichuyen
        self._is_khungsauxuatchieu = is_khungsauxuatchieu
        self._diachimuctieuxuatchieu = diachimuctieu
        self._idmuctieuxuatchieu = self.get_iddoituong(diachimuctieu) if diachimuctieu else None
        self._sobaymuctieuxuatchieu = self._docsobaydoituong(diachimuctieu) if diachimuctieu else None
        self._is_datrungchieu = False

    def get_is_khoavankhitrieuhoi(self):
        # Khoá từ lúc gửi lệnh triệu hồi: chờ tối đa THOIGIANCHOVAOVANKHI để vào vận khí, sau đó giữ tới khi game hết vận khí (tối đa THOIGIANKHOAVANKHITRIEUHOITOIDA)
        khoa = self._khoavankhitrieuhoi
        if not khoa:
            return False
        thoidiemhientai = time.time()
        if thoidiemhientai < khoa["toida"] and (thoidiemhientai - khoa["batdau"] < THOIGIANCHOVAOVANKHI or self._get_is_dangvankhitrongame()):
            return True
        self._khoavankhitrieuhoi = None
        self._inlog(f"[KHOÁ VẬN KHÍ TRIỆU HỒI] kết thúc sau {round(thoidiemhientai - khoa['batdau'], 1)}s")
        return False

    def _is_lenhbichankhoavankhi(self, caulenh):
        # Đọc khoá 1 lần: luồng khác có thể vừa mở khoá (gán None) ngay sau khi kiểm tra
        khoa = self._khoavankhitrieuhoi
        if not khoa or not self.get_is_khoavankhitrieuhoi():
            return False
        # Chỉ ra chiêu (pf, pf2, pf5...) / đánh thường (kill) mới ngắt vận khí; nhặt đồ tại ô (get x y, không chạy tới),
        # dùng / đeo vật phẩm, desc, move đồ, vứt, bán, nói chuyện NPC, điều khiển bảo thú, thao tác nhóm đều không ảnh hưởng
        # (đã thử trong game) => cho gửi. Di chuyển / tìm đường chặn riêng ở action_dichuyenoo,
        # action_tudongtimduong
        if not caulenh.startswith(("pf", "kill ")):
            return False
        return caulenh not in khoa["caulenhduocpheps"]

    def get_is_dangvankhi(self):
        if time.time() < self._thoidiemhetchovankhi:
            return True
        return self._get_is_dangvankhitrongame()

    def _get_is_dangvankhitrongame(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_VANKHI)
        return read_int(self.tientrinh, x + 0xD8) == TRANGTHAIVANKHI_DANGVANKHI if x else False

    def get_is_dakhoitaothongtinbando(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_TIMDUONG)
        return x > 0

    def action_tudongtimduong(self, x, y, idbando, is_lotrinh = True):
        # Đặt đích tìm đường mới là bắt đầu di chuyển => ngắt vận khí triệu hồi / mất tác dụng chiêu đang xuất
        # (huỷ tìm đường thì qua action_ngungtudongtimduong, không chặn)
        if (x or y) and (self.get_is_khoavankhitrieuhoi() or self.get_is_dangxuatchieu()):
            return False
        if x or y:
            dichtrongtran = self._kepdichtrongtrando(x, y)
            if dichtrongtran is None:
                return False
            x, y = round(dichtrongtran[0]), round(dichtrongtran[1])
        a = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not a: return False
        a = read_int(self.tientrinh, a + DC.TG_TIMDUONG)
        if not a:
            self.auto_assemble_khoitaothongtinbando()
            return False
        # Đích tìm đường mới (không phải huỷ, không phải đích đang đi) cũng là bắt đầu di chuyển: phải tới lượt
        is_dichmoi = (x or y) and (read_int(self.tientrinh, a + DC.TD_DICH), read_int(self.tientrinh, a + DC.TD_DICH + 4), read_int(self.tientrinh, a + DC.TD_BANDO)) != (x, y, idbando)
        if is_dichmoi and not self._get_is_duocbatdaudichuyen():
            return False
        if is_dichmoi and IS_LOGDICHUYEN and is_lotrinh:
            self._inlog(f"[TÌM ĐƯỜNG] (đang ở {self.get_toado()}) -> {(x, y)} bản đồ {idbando}")
        if read_int(self.tientrinh, a + DC.TD_DICH) != x:
            write_int(self.tientrinh, a + DC.TD_DICH, x)
        if read_int(self.tientrinh, a + DC.TD_DICH + 4) != y:
            write_int(self.tientrinh, a + DC.TD_DICH + 4, y)
        if read_int(self.tientrinh, a + DC.TD_BANDO) != idbando:
            write_int(self.tientrinh, a + DC.TD_BANDO, idbando)
        return True

    def action_ngungtudongtimduong(self):
        a = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not a:
            return False
        a = read_int(self.tientrinh, a + DC.TG_TIMDUONG)
        if not a:
            self.auto_assemble_khoitaothongtinbando()
            return False
        is_dahuy = False
        if read_int(self.tientrinh, a + DC.TD_DICH) != 0:
            write_int(self.tientrinh, a + DC.TD_DICH, 0)
            is_dahuy = True
        if read_int(self.tientrinh, a + DC.TD_DICH + 4) != 0:
            write_int(self.tientrinh, a + DC.TD_DICH + 4, 0)
            is_dahuy = True
        if read_int(self.tientrinh, a + DC.TD_BANDO) != 0:
            write_int(self.tientrinh, a + DC.TD_BANDO, 0)
            is_dahuy = True
        # True khi thật sự đang có đích tìm đường và vừa huỷ
        return is_dahuy

    def action_phucsinh(self, delay = 2.5):
        if time.time() - self._thoidiemphucsinhgannhat < delay or not self.get_is_nhanvatdachet():
            return False
        self._thoidiemphucsinhgannhat = time.time()
        self.action_thucthicaulenh("desc revive")
        # Đóng cửa sổ tuỳ chọn sau 1s ở lượt sau (action_dongcuasosauphucsinh), không sleep chặn luồng
        self._thoidiemdongcuasosauphucsinh = time.time() + 1.
        return True

    def action_dongcuasosauphucsinh(self):
        if not self._thoidiemdongcuasosauphucsinh or time.time() < self._thoidiemdongcuasosauphucsinh:
            return
        self._thoidiemdongcuasosauphucsinh = 0.
        if self.get_is_danghiencuasotuychon():
            self.set_is_danghiencuasotuychon(False)

    def action_doimaupk(self, idmaupk, delay = 1.):
        if time.time() - self._thoidiemmaupkgannhat < delay or self.get_idmaupk() == idmaupk:
            return False
        is_ok = self.action_thucthicaulenh("set !attack {}".format(idmaupk))
        if is_ok:
            self.set_idmaupk(idmaupk)
            self._thoidiemmaupkgannhat = time.time()
        return is_ok

    def get_dungluongtuihanhtrangs(self):
        # Số ô đang mở của 4 túi hành trang (túi phụ mở bằng Túi Càn Khôn 4/6/12/24 ô, có hạn dùng), vd [24, 4, 0, 0].
        # Đọc tại [x + DC.TG_TUIHANHTRANG] + OFFSET_DUNGLUONGTUIHANHTRANG; đọc lỗi / số lạ thì None
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        p = read_int(self.tientrinh, x + DC.TG_TUIHANHTRANG) if x else 0
        if not p:
            return None
        try:
            dungluongs = list(struct.unpack("<4i", read_bytes(self.tientrinh, p + OFFSET_DUNGLUONGTUIHANHTRANG, 16)))
        except Exception:
            return None
        if not all(0 <= dungluong <= SOLUONGOMOITUI for dungluong in dungluongs) or not dungluongs[0]:
            return None
        return dungluongs

    def get_danhsachvitrimohanhtrang(self):
        # Vị trí các ô hành trang đang mở (ô ngoài dung lượng túi là ô khoá, trống nhưng không đặt được vật phẩm).
        # Không đọc được dung lượng túi thì coi cả SOLUONGTUIHANHTRANG túi mở đủ
        dungluongs = self.get_dungluongtuihanhtrangs() or [SOLUONGOMOITUI] * SOLUONGTUIHANHTRANG
        return [tui * SOLUONGOMOITUI + o for tui, dungluong in enumerate(dungluongs) for o in range(dungluong)]

    def get_soluongvatphamhanhtrangtoida(self):
        # Vị trí ô mở cuối cùng (các vòng lặp dùng range(... + 1)); ô khoá xen giữa vẫn nằm trong khoảng này, đọc ra id 0
        return self.get_danhsachvitrimohanhtrang()[-1]

    def _docdanhsachtenvatphamhanhtrang(self, soluongo):
        # Tên của soluongo ô đầu hành trang trong 1 lần đọc (mỗi ô 0x20 byte), thay vì mỗi ô đọc lại địa chỉ gốc + đọc tên riêng.
        # Ô có tên dài hết 0x20 byte (không có ký tự kết thúc) thì đọc riêng như cũ cho chắc
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return []
        dulieu = read_bytes(self.tientrinh, x + DC.HT_TEN, soluongo * 0x20)
        tens = []
        for i in range(soluongo):
            o = dulieu[i * 0x20:(i + 1) * 0x20]
            vitriketthuc = o.find(b"\x00")
            if vitriketthuc == -1:
                tens.append(read_string(self.tientrinh, x + i * 0x20 + DC.HT_TEN))
                continue
            ten = o[:vitriketthuc].decode("utf-8", errors = "ignore")
            tens.append(re.sub(r'\x1b[a-zA-Z0-9]', '', ten).strip())
        return tens

    def get_thoigianhoiconlaivatphams(self, tenvatphams):
        # Số giây còn phải chờ để dùng lại từng vật phẩm (0 = dùng được ngay), theo đúng dữ liệu client dùng để vẽ ô tối xoay dần.
        # Máy chủ báo hồi theo nhóm (vd Trị Dược / Thí Luyện Quả / Cấp Cứu Đơn chung nhóm 4, hồi 5s), client ghi thời lượng (giây) +
        # timeGetTime lúc nhận vào mọi ô cùng nhóm, hết hồi thì về 0 => còn lại = bắt đầu + thời lượng - bây giờ.
        # Xét cả nhóm (lấy ô hồi muộn nhất) vì ô mới nhặt sau lúc dùng không được ghi hồi. Nhóm 0 = không có nhóm, xét riêng từng ô
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return {ten: 0. for ten in tenvatphams}
        tens = self._docdanhsachtenvatphamhanhtrang(SOLUONGOTHOIGIANHOI)
        nhoms = read_bytes(self.tientrinh, x + DC.HT_NHOMHOI, SOLUONGOTHOIGIANHOI)
        thoiluongs = struct.unpack("<%dI" % SOLUONGOTHOIGIANHOI, read_bytes(self.tientrinh, x + DC.HT_THOILUONGHOI, SOLUONGOTHOIGIANHOI * 4))
        batdaus = struct.unpack("<%dI" % SOLUONGOTHOIGIANHOI, read_bytes(self.tientrinh, x + DC.HT_BATDAUHOI, SOLUONGOTHOIGIANHOI * 4))
        baygio = ctypes.windll.winmm.timeGetTime()
        conlais = []
        for i in range(SOLUONGOTHOIGIANHOI):
            # Trừ theo 32 bit (timeGetTime quay vòng ~49 ngày); quá hạn thì ra số âm => đã hồi xong
            conlai = (batdaus[i] + thoiluongs[i] * 1000 - baygio) & 0xFFFFFFFF
            conlais.append(conlai if thoiluongs[i] and conlai < 0x80000000 else 0)
        conlainhoms = {}
        for i in range(SOLUONGOTHOIGIANHOI):
            if nhoms[i]:
                conlainhoms[nhoms[i]] = max(conlainhoms.get(nhoms[i], 0), conlais[i])
        ketqua = {}
        for i, ten in enumerate(tens):
            if ten in tenvatphams and ten not in ketqua:
                ketqua[ten] = (conlainhoms[nhoms[i]] if nhoms[i] else conlais[i]) / 1000.
        return {ten: ketqua.get(ten, 0.) for ten in tenvatphams}

    def _docdanhsachidvatphamhanhtrang(self, soluongo):
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return [False] * soluongo
        return list(struct.unpack("<%di" % soluongo, read_bytes(self.tientrinh, x, soluongo * 4)))

    def action_timkiemvatphamhanhtrang(self, tenvatpham = None, is_ruongdautien = False, is_kiemtrahansudung = False):
        if not tenvatpham: return False
        soluongvatphamhanhtrangtoida = self.get_soluongvatphamhanhtrangtoida()
        if is_ruongdautien:
            soluongvatphamhanhtrangtoida = 24 - 1
        for i, tenvatphamxemxet in enumerate(self._docdanhsachtenvatphamhanhtrang(soluongvatphamhanhtrangtoida + 1)):
            if tenvatphamxemxet != tenvatpham:
                continue
            if is_kiemtrahansudung:
                motavatpham = self.get_motavatphamhanhtrang(i)
                if "Hết hạn sử dụng" in motavatpham:
                    continue
            return self.get_iddoituongvatphamhanhtrang(i)
        return False

    def get_danhsachtenvatphamhanhtrang(self):
        return self._docdanhsachtenvatphamhanhtrang(self.get_soluongvatphamhanhtrangtoida() + 1)

    def action_timkiemvitrivatphamhanhtrang(self, tenvatpham = None):
        if not tenvatpham:
            return False
        tens = self._docdanhsachtenvatphamhanhtrang(self.get_soluongvatphamhanhtrangtoida() + 1)
        return tens.index(tenvatpham) if tenvatpham in tens else False

    def get_danhsachvatphamhanhtrang_map(self):
        vatphamhanhtrang_map = {}
        soluongo = self.get_soluongvatphamhanhtrangtoida() + 1
        tens = self._docdanhsachtenvatphamhanhtrang(soluongo)
        idvatphams = self._docdanhsachidvatphamhanhtrang(soluongo)
        for i, tenvatphamxemxet in enumerate(tens):
            vatphamhanhtrang_map.setdefault(tenvatphamxemxet, []).append((i, idvatphams[i]))
        return vatphamhanhtrang_map

    def action_timkiemnhanvat(self, tennhanvat = None, idnguoichoi = None, iddoituong = None, tennhanvatchua = None, tenchunhan = None):
        if not tennhanvat and not idnguoichoi and not iddoituong and not tennhanvatchua and not tenchunhan: return False
        toadobanthan = self.get_toado()
        i = 0
        while True:
            diachi = self.get_diachicosothongtindoituongx(i)
            if not diachi: break
            i += 1
            if not self.get_is_nhanvattontai(diachi): continue
            # Lọc theo tên/id trước (rẻ, loại gần hết đối tượng), khoảng cách để sau cùng
            if tennhanvat and self.get_tendoituong(diachi) != tennhanvat: continue
            if idnguoichoi and self.get_idnguoichoi(diachi) != idnguoichoi: continue
            if iddoituong and self.get_iddoituong(diachi) != iddoituong: continue
            if tenchunhan:
                ten = self.get_tendoituong(diachi)
                if not ten or "({})".format(tenchunhan) not in ten: continue
            if tennhanvatchua:
                ten = self.get_tendoituong(diachi)
                if not ten or tennhanvatchua not in ten: continue
            if math.dist(toadobanthan, self.get_toado(diachi)) > KHOANGCACHTOANMANHINH: continue
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
        return read_int(self.tientrinh, (diachi or self.get_diachicosothongtinnhanvat1()) + DC.NV_VUKHI)

    def set_idvukhi(self, idvukhi, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_idvukhi() != idvukhi: write_int(self.tientrinh, diachi + DC.NV_VUKHI, idvukhi)

    def get_idloaivukhi(self, diachi = None):
        return read_int(self.tientrinh, (diachi or self.get_diachicosothongtinnhanvat1()) + 0x1180)

    def set_idloaivukhi(self, idloaivukhi, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_idloaivukhi() != idloaivukhi: write_int(self.tientrinh, diachi + 0x1180, idloaivukhi)

    def get_idngoaitrang(self, diachi = None):
        return read_int(self.tientrinh, (diachi or self.get_diachicosothongtinnhanvat1()) + DC.NV_NGOAITRANG)

    def set_idngoaitrang(self, idngoaitrang, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_idngoaitrang() != idngoaitrang: write_int(self.tientrinh, diachi + DC.NV_NGOAITRANG, idngoaitrang)

    def get_idcanh(self, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        return read_int(self.tientrinh, diachi + DC.NV_CANH), read_int(self.tientrinh, diachi + DC.NV_CANH + 4)

    def set_idcanh(self, idcanh, diachi = None):
        diachi = diachi or self.get_diachicosothongtinnhanvat1()
        if self.get_idcanh() != idcanh:
            write_int(self.tientrinh, diachi + DC.NV_CANH, idcanh[0])
            write_int(self.tientrinh, diachi + DC.NV_CANH + 4, idcanh[1])

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
        # Chỉ xét ô đang mở: ô khoá luôn trống (id 0) nhưng không chứa được vật phẩm
        vitrimos = self.get_danhsachvitrimohanhtrang()
        ids = self._docdanhsachidvatphamhanhtrang(vitrimos[-1] + 1)
        return all(ids[vitri] for vitri in vitrimos)

    def get_tenmonphai(self):
        return MONPHAI_MAP.get(self.get_idkynang(0, 0))

    def get_diachicosobaothugiangho(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return read_int(self.tientrinh, x + DC.TG_MONPHAI) if x else False

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

    def get_thoidiemsudungkynangvitrigannhat(self, idvitri_x, idvitri_y = None, macdinh = None):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return macdinh
        idvitri_x, idvitri_y = vitri
        return self._thoidiemsudungkynangvitrigannhat_map.get((idvitri_x, idvitri_y), macdinh)

    def action_sudungkynangvitrimuctieu(self, idvitri_x, idvitri_y = None, diachicosothongtinnhanvatmuctieu = False, is_khongkiemtracothetancong = False, delay = 0.):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return False
        idvitri_x, idvitri_y = vitri
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
            is_ok = self.action_sudungkynangmuctieunguoichoi(idkynang, idnguoichoi, vitrikynang = idvitri)
        else:
            iddoituong = self.get_iddoituong(diachi)
            if iddoituong: is_ok = self.action_sudungkynangmuctieukhacnguoichoi(idkynang, iddoituong, vitrikynang = idvitri)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        return is_ok

    def action_sudungkynangvitri(self, idvitri_x, idvitri_y = None, delay = 0.):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return False
        idvitri_x, idvitri_y = vitri
        if time.time() - self._thoidiemsudungkynanggannhat < delay:
            return False
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return False
        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return False
        if IS_LOGCAULENH and (idvitri, idkynang) not in self._vitrikynangdalog:
            self._vitrikynangdalog.add((idvitri, idkynang))
            self._inlog(f"[KỸ NĂNG] ô {idvitri} = kỹ năng {idkynang}")
        is_ok = self.action_sudungkynang(idkynang, vitrikynang = idvitri)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        return is_ok

    def action_sudungkynangvitrilenbanthan(self, idvitri_x, idvitri_y = None, delay = 0.):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return False
        idvitri_x, idvitri_y = vitri
        if time.time() - self._thoidiemsudungkynanggannhat < delay:
            return False
        idvitri = (idvitri_x, idvitri_y)
        if idvitri in self._thoidiemsudungkynangvitrigannhat_map and time.time() - self._thoidiemsudungkynangvitrigannhat_map[idvitri] < delay:
            return False
        idkynang = self.get_idkynang(idvitri_x, idvitri_y)
        if not idkynang:
            return False
        is_ok = self.action_sudungkynangmuctieunguoichoi(idkynang, self.get_idnguoichoi(), vitrikynang = idvitri)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
        return is_ok

    def get_idlenhdichuyen(self):
        return read_int(self.tientrinh, self.diachixq + DC.CHISOBUOCDICHUYEN)

    def set_idlenhdichuyen(self, idlenhdichuyen):
        write_int(self.tientrinh, self.diachixq + DC.CHISOBUOCDICHUYEN, idlenhdichuyen)

    def action_chandichuyen(self):
        # Vòng xử lý di chuyển của client (xq + 0x182E0) tự gửi "go x,y <chuỗi hướng>" rồi bước nhân vật ở 3 nhánh, nhánh nào cũng
        # chỉ chạy khi timeGetTime() > [thông tin game] + 0xADFC5C (mốc client được tự gửi lệnh, game tự đặt = lúc gửi + 500ms):
        #  - đuổi mục tiêu tấn công ngoài tầm ([xq + 0x372864] + 0x15F8 / + 0x1604) khi hoạt ảnh vừa xong (nhân vật + 0x10A0 == + 0x10A4)
        #  - đi tới đích click chuột còn cất ở [xq + 0x372864] + 0x1608 / + 0x160C
        #  - bước tiếp chuỗi đường đi toàn cục xq + 0x1FC2B4 (ký tự hướng '1'..'8'); xq + 0x380AFC là chỉ số bước kế tiếp trong
        #    chuỗi đó (get_idlenhdichuyen), hai nhánh trên đặt nó = [xq + 0x372864] + 0x1620 (2) -> bước 1 - 2 ô ngay khi hết chiêu
        # Hàm gửi lệnh (xq + 0x95450) không xét mốc này nên lệnh của bot vẫn đi. True khi vừa đẩy mốc
        thongtingame = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not thongtingame:
            return False
        mocmoi = (ctypes.windll.winmm.timeGetTime() + int(THOIGIANCHANTUDICHUYENCLIENT * 1000)) & 0xFFFFFFFF
        mochientai = struct.unpack("<I", read_bytes(self.tientrinh, thongtingame + DC.TG_MOCTUGUILENH, 4))[0]
        if (mochientai - mocmoi) & 0xFFFFFFFF < 0x80000000:
            return False
        write_bytes(self.tientrinh, thongtingame + DC.TG_MOCTUGUILENH, struct.pack("<I", mocmoi), 4)
        return True

    def action_huybuocdichuyen(self):
        # Huỷ bước đi đang dở: "ô sắp tới" (nhân vật + 0x18 / + 0x1C) khác vị trí hiện tại thì game vẫn bước tới đó dù đã xoá
        # lệnh di chuyển và đích tìm đường (đo: bước tiếp 2 ô sau khi hết chiêu). Đặt ô sắp tới = vị trí hiện tại để đứng yên.
        # True khi thật sự có bước dở vừa huỷ
        diachi = self.get_diachicosothongtinnhanvat1()
        if not diachi:
            return False
        x, y = struct.unpack("<ii", read_bytes(self.tientrinh, diachi, 8))
        xsaptoi, ysaptoi = struct.unpack("<ii", read_bytes(self.tientrinh, diachi + 0x18, 8))
        if (xsaptoi, ysaptoi) == (x, y):
            return False
        write_bytes(self.tientrinh, diachi + 0x18, struct.pack("<ii", x, y), 8)
        return True

    def action_ngatdichuyen(self):
        # if self.get_idlenhdichuyen() != 0:

        # if read_bytes(self.tientrinh, self.diachixq + 0x48789, 1) != bytes.fromhex("90"):
        #     write_bytes(self.tientrinh, self.diachixq + 0x48789, bytes.fromhex("90 90 90 90 90"), 5)

        self.set_idlenhdichuyen(0)
        self.action_ngungtudongtimduong()
        # Xoá lệnh di chuyển chưa đủ: client còn tự sinh lại "go" (đuổi mục tiêu, đích click, bước dở) => chặn luôn client tự gửi
        self.action_chandichuyen()

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
        self._thoidiemnhatvatphamgannhat_map = donbangthoidiem(self._thoidiemnhatvatphamgannhat_map, 120.)
        self.action_nhatvatphamtoado(x, y, delay = delay)
        return True

    def action_nhatvatphamxungquanh(self, delay = 0.05):
        if time.time() - self._thoidiemnhatvatphamgannhat < delay:
            return False
        self._thoidiemnhatvatphamgannhat = time.time()
        self.auto_assemble_nhatvatpham()
        return True

    def _docdongtrochuyenmois(self):
        # Mọi dòng trò chuyện hook ghi thêm từ lần đọc trước (cả các dòng giống nhau liên tiếp). Chậm quá SOLUONGDONGTROCHUYEN dòng
        # thì các dòng cũ nhất đã bị ghi đè, chỉ lấy SOLUONGDONGTROCHUYEN dòng mới nhất
        if not self._diachibodemnoidungtrochuyen:
            return []
        try:
            dulieu = read_bytes(self.tientrinh, self._diachibodemnoidungtrochuyen, 4 + SOLUONGDONGTROCHUYEN * KICHTHUOCDONGTROCHUYEN)
        except Exception:
            return []
        dem = struct.unpack_from("<I", dulieu, 0)[0]
        dadoc = self._demdongtrochuyendadoc
        if dem < dadoc:
            dadoc = 0
        dadoc = max(dadoc, dem - SOLUONGDONGTROCHUYEN)
        self._demdongtrochuyendadoc = dem
        dongs = []
        for i in range(dadoc, dem):
            vitri = 4 + (i % SOLUONGDONGTROCHUYEN) * KICHTHUOCDONGTROCHUYEN
            o = dulieu[vitri:vitri + KICHTHUOCDONGTROCHUYEN]
            o = o[:o.find(b"\x00")] if b"\x00" in o else o
            noidung = re.sub(r"\x1b[a-zA-Z0-9]", "", o.decode("utf-8", errors = "ignore")).strip()
            if noidung:
                dongs.append(noidung)
        return dongs
