import ctypes
import heapq
import queue
from collections import deque
import re
import struct
import threading
import unicodedata
from dataclasses import dataclass, field

import pymem
from keystone import Ks, KS_ARCH_X86, KS_MODE_32

import astar_c_xq
import diachi_xq
from dexuatlotrinh_xq import HUONGTIMDUONG_MAP
from dieuphoi_xq import is_lenhxoayvong
from diachi_xq import DC
from hangso_xq import *
from tienich_xq import *
import ctypes.wintypes


# Quét vùng nhớ tiến trình game (VirtualQueryEx): gói tin hàng Trân Bảo Khố nằm rải trong heap (MoiTruong._quetbanghitranbaokho)
class _MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p), ("AllocationProtect", ctypes.wintypes.DWORD),
                ("RegionSize", ctypes.c_size_t), ("State", ctypes.wintypes.DWORD), ("Protect", ctypes.wintypes.DWORD),
                ("Type", ctypes.wintypes.DWORD)]


_VirtualQueryEx = ctypes.windll.kernel32.VirtualQueryEx
_VirtualQueryEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(_MBI), ctypes.c_size_t]
_VirtualQueryEx.restype = ctypes.c_size_t
# 1 bản ghi hàng: 45 03 <tab> <stt> <3 giá int> <6 byte> <tên> <>=2 dấu cách> (xem _quetbanghitranbaokho)
MAUBANGHITRANBAOKHO = re.compile(rb"\x45\x03([\x01-\x0f])([\x01-\x7f])(.{12})(.{6})([^\x00]{2,80}?) {2,}", re.S)

# Thông tin túi hành trang: con trỏ tại [thông tin game] + 0xADFE0C (cạnh con trỏ hành trang + 0xADFD78),
# số ô mở của 4 túi là 4 int32 tại + 0xD4 (đo: túi đủ [24, 24, 24, 24], mới mở túi 2 loại 4 ô [24, 4, 0, 0])
OFFSET_DUNGLUONGTUIHANHTRANG = 0xD4
# Trong ô kỹ năng, tính từ chỗ chứa id (KN_ID): cờ đã học (3 = đã học, 0 = chưa học), xem MoiTruong.get_is_kynangdahoc
OFFSET_KYNANGDAHOC = 0x1C
# Bảng vị trí kỹ năng đã học đọc lại sau chừng này giây
THOIGIANNHOBANGKYNANG = 2.
# Lưới vật cản của bản đồ hiện tại trong [thông tin game] (client tra ở xq + 0x4998F0, hàm tìm đường cục bộ gọi cho từng ô):
# rộng / cao là 2 int32 tại + 0x56D8B8, ô (x, y) là dword tại + 0xBE3C8 + 4 * (501 * x + y + 701400), & 3: 0 đi được, khác 0 vật cản
# (thử 2026-10-30 trên bản đồ 54: 1 đá / tường, 2 nước)
OFFSET_KICHTHUOCBANDO = 0x56D8B8
OFFSET_LUOIVATCAN = 0xBE3C8 + 4 * 701400
SOCOTLUOIVATCAN = 501
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


# action_dioochangtoidich: đi theo ô chừng này giây mà không gần đích hơn thì coi như kẹt, dùng tự động tìm đường của game
THOIGIANKETDIOO = 8.
KHOANGCACHCUNGDICHDIOO = 8.
# action_dikhongcatgoc: đang đi mà ô thật đứng yên chừng này giây (bị máy chủ kéo về) thì ô kế tiếp là vật cản học được
THOIGIANKETKHONGCATGOC = 1.5
# Chuỗi đường đi xq + 0x1FC2B4 là 100 byte (ô 0 bỏ trống), byte ngay sau là con trỏ khác 0 => ghi đủ 99 bước thì chuỗi không có ký tự
# kết thúc, client gửi "go" kèm rác phía sau, máy chủ từ chối => đứng giật giật tại chỗ (Ngọc ở Chu (216, 200) -> (232, 187)). Tối đa 98
SOBUOCCHUOIDUONGDITOIDA = 98
GIANCACHGOIKHONGCATGOC = 1.
THOIGIANGIATKHONGCATGOC = 4.
SOLANGIATKHONGCATGOC = 2
# Mỗi ô trong khu vực cấm khai tay tính thêm chừng này bước khi tìm đường không cắt góc
PHATKHUVUCCAMKHONGCATGOC = 20.
# Ô NPC (lớp +0x29 == 0x80) đang đứng: lưới vật cản client không ghi NPC => A* vạch đường xuyên qua NPC, nhân vật vấp vào đó (người dùng
# thấy 2026-11-11). Tính thêm chừng này bước cho ô đó (phạt chứ không chặn hẳn: lối hẹp 1 ô có NPC đứng vẫn đi qua được, đích là NPC vẫn
# tới được); danh sách ô NPC đọc lại sau THOIGIANNHOONPC giây (A* gọi mỗi ~0.1s, quét cả bảng đối tượng mỗi lần thì tốn)
PHATONPCKHONGCATGOC = 10.
THOIGIANNHOONPC = 1.
# Đi liên tục mà client không bước ra khỏi ô chừng này giây (ô "sắp tới" không lệch nên _hockhongcatgoc không học được) thì chặn tạm
# bước đầu của đường đang đi THOIGIANTAMCHAN giây (A* tính thêm PHATTAMCHANKHONGCATGOC bước cho ô đó)
THOIGIANKETTAMCHAN = 3.
THOIGIANTAMCHAN = 30.
PHATTAMCHANKHONGCATGOC = 30.
# A* / đánh số vùng liên thông lâu hơn chừng này giây thì log [A* CHẬM]. Đo ngoài game 2026-11-12: khung ±25 0.2-1.5 ms, cả bản đồ có
# đường 4-106 ms (bản đồ 80 có lúc 400 ms)
THOIGIANASTARCHAM = 0.03
# Dùng A* bản C (astar_xq.dll, build bằng build_astar.bat) khi có; False thì luôn chạy bản Python
IS_DUNGASTARC = True
# get_is_nhanvattontai() của nhân vật mình nhớ kết quả chừng này giây (luồng nhanh nhất chạy 0.02s/lượt: trễ tối đa 2-3 lượt)
THOIGIANNHONHANVATTONTAI = 0.05
# Bản chụp đối tượng xung quanh (_get_banchupdoituongxungquanh) dùng lại trong chừng này giây: các chỗ quét trong cùng 1 lượt vòng lặp
# (cách nhau vài ms) dùng chung 1 lần quét
THOIGIANNHODOITUONGXUNGQUANH = 0.05
# Con trỏ nhân vật mình (get_diachicosothongtinnhanvat1) dùng lại trong chừng này giây
THOIGIANNHOCONTRONHANVAT = 0.05
# Chạy trốn theo đường tính sẵn (get_duongchaytron): xét lưới vật cản trong ô vuông bán kính BANKINHLUOICHAYTRON quanh mình, chọn đích
# cách SOBUOCDICHCHAYTRONTOITHIEU..SOBUOCDICHCHAYTRONTOIDA bước (đích không sát mép lưới để còn đếm được khoảng trống phía sau nó)
BANKINHLUOICHAYTRON = 40
SOBUOCDICHCHAYTRONTOITHIEU = 4
SOBUOCDICHCHAYTRONTOIDA = 24
# Đích cũ còn an toàn và điểm kém đích tốt nhất không quá chừng này thì giữ đích cũ (không đổi hướng qua lại)
DIEMGIUDICHCHAYTRON = 3.
# Cùng đích mà chuỗi đang đi chưa hết thì chừng này giây mới ghi lại chuỗi mới (đường né kẻ địch vừa đổi chỗ)
THOIGIANGHILAICHAYTRON = 1.2


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

        # Niết Bàn: ChienQuocNietBan.dll tự hook đầu hàm gửi lệnh => không NOP đầu HAMGUILENH, không hook lệnh game; lệnh gửi kèm "\r\n"
        self.is_nietban = "Chien Quoc Niet Ban" in win32gui.GetWindowText(self.idcuaso)
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
        # Nhiều vòng lặp cùng gọi auto_assemble_khoitaothongtinbando: hàm khởi tạo xq + 0xCEEB0 chạy lâu (nạp place.txt + mọi ảnh
        # thành trì .tcb qua engine.dll), 2 luồng chạy song song đè heap của nhau => crash engine.dll + 0x180C8 (Thk 354, 2026-11-08 23:57)
        self._khoakhoitaothongtinbando = threading.Lock()
        # Lần gửi "desc pf <id>" gần nhất theo id kỹ năng (get_tieuhaokynang)
        self._thoidiemtruyvanmotakynang_map = {}
        # id kỹ năng -> (thời điểm đọc, tiêu hao hoặc None): hàm ra chiêu xét tiêu hao mỗi lượt cho mọi chiêu nên nhớ lại một lúc
        self._tieuhaokynang_cache = {}
        # Bảng {id kỹ năng đã học: vị trí} (_get_bangvitrikynangdahoc) và lúc đọc
        self._bangvitrikynangdahoc = {}
        self._thoidiemdocbangkynang = 0.
        # Đích đi theo ô gần nhất (action_dichuyenoo): còn đang đi tới đích này thì không ghi lại chuỗi
        self._dichdioogannhat = None
        # Chặng đang đi của action_dioochangtoidich: ((đích cuối), (điểm cuối chặng)); tiến độ [đích, khoảng cách gần nhất, lúc gần hơn,
        # đã kẹt (chuyển sang tự động tìm đường)]
        self._changdioo = None
        self._tiendodioo = None
        # Đích đang đi của action_dikhongcatgoc (chuỗi hướng bot tự tìm, không lách chéo qua khe góc)
        self._dichkhongcatgoc = None
        # Đường đang đi (các ô), [ô thật, lúc đứng ở ô đó từ] để biết bị máy chủ kéo về, lúc vừa học 1 ô vật cản
        self._duongkhongcatgoc = []
        self._kettiendokhongcatgoc = None
        self._lucvuahockhongcatgoc = 0.
        # (bản đồ, ô) -> lúc chặn tạm: client đứng mãi không bước sang ô đó (NPC / người chắn), A* né THOIGIANTAMCHAN giây
        self._tamchankhongcatgoc = {}
        self._lucgoikhongcatgoc = 0.
        # Đích / lúc ghi chuỗi gần nhất của action_dichuoihuongchaytron (chạy trốn theo đường tính sẵn)
        self._dichchaytrondaghi = None
        self._thoidiemghichaytron = 0.
        # Các ô thật gần đây [(lúc, ô)] và lần bị giật về theo (ô mốc, bước đầu) để bắt kiểu giật về ô mốc
        self._lichsukhongcatgoc = []
        self._giatkhongcatgoc = {}
        self._dulieutimduongcucbo = None
        self._buftimduongcucbo = None
        self._doituongtimduongcucbo = None
        # (bản đồ, x, y) -> ô đi được đã kéo về (get_oditduocganhat): giữ cố định để đích không nhảy theo vị trí mình
        self._oditduoc_cache = {}
        # (bản đồ, từ x, từ y, tới x, tới y) -> lúc thấy đoạn cụt (action_dichuyenoo): khỏi tìm đường lại liên tục cùng 1 đoạn
        self._doancut_cache = {}
        # (bản đồ, lúc đọc, lưới cả bản đồ) cho A* cả bản đồ (_timduongkhongcatgoc lechtoida = None): lưới tĩnh theo bản đồ, khỏi đọc
        # lại ~300 cột mỗi lần tìm
        self._luoicabando_cache = None
        # is_chocatgoc -> (lưới cả bản đồ, mảng nhãn vùng liên thông) (_get_nhanvunglienthong): A* cả bản đồ khác vùng thì bỏ qua ngay
        self._vunglienthong_cache = {}
        # (lưới cả bản đồ, bytes trong[x * cao + y]) cho A* bản C; đã log 1 lần chuyện không nạp được astar_xq.dll
        self._luoicabandoc_cache = None
        self._is_dalogastarc = False
        # (lúc đọc theo time.monotonic, nhân vật mình còn tồn tại) cho get_is_nhanvattontai(), dùng chung mọi luồng
        self._nhanvattontai_nho = (-1e9, False)
        # (lúc chụp, tuple địa chỉ đối tượng còn tồn tại trong tầm màn hình) cho _get_banchupdoituongxungquanh
        self._doituongxungquanh_nho = (-1e9, ((0, 0), ()))
        # (lúc đọc, con trỏ nhân vật mình) cho get_diachicosothongtinnhanvat1
        self._contronhanvat_nho = (-1e9, 0)
        # (bản đồ, lúc đọc, set ô NPC đang đứng) cho A* né NPC (_get_onpcdung)
        self._onpc_cache = None
        # action_dikhongcatgoc: chuỗi đang đi là đường tìm trên cả bản đồ; (bản đồ, từ, tới) -> lúc thấy không có đường
        self._is_duongcabando = False
        self._khongduongkhongcatgoc_cache = {}
        # Bản đồ đã ghi lưới ra file khi cả bản đồ không có đường (_ghiluoikhongduong)
        self._dadghiluoi = set()
        # (bản đồ, x, y, tầm) -> (lúc chọn, ô tới được trong tầm hoặc None) (_chondichtoiduoc)
        self._dichtoiduoc_cache = {}
        self._diembanthong = None
        self._is_dasetupautoassemblenhatvatpham = False
        self._is_dasetupautoassemblekhoitaothongtinbando = False
        # (vị trí con trỏ cửa sổ trong thông tin game, hiện?) -> đoạn mã gọi vtable[1] ẩn / hiện cửa sổ (_goivtableanhien)
        self._diachivtableanhien_map = {}
        self._is_dasetupactionthietlaphooknoidungtrochuyen = False
        # Giữ chân sau chiêu delay 0 tới khi có số bay (action_giuchansauchieudelay0): {diachi, id, sobay, batdau} hoặc None
        self._giuchandelay0 = None
        # Đo mã hoạt ảnh chiêu (_dohoatanhchieu): None hoặc {nhanvat, ghi}; (id kỹ năng, lúc gửi) chiêu đo gần nhất bot gửi
        self._dohoatanh = None
        self._thoidiembotguidohoatanh = None

        self._thoidiemdichuyengannhat = 0.
        # Chờ xác nhận vận khí (action_chovankhi): None hoặc {"caulenh", "vitrikynang", "tao", "gui", "guitgt", "chapnhan", "ten"}
        self._chovankhi = None
        # Lệnh vừa ghi vào game gần nhất: (câu lệnh, time.time(), timeGetTime) để khớp lệnh vận khí đã gửi trước khi đăng ký chờ
        self._lenhguigannhat = None
        # Lúc Tín Vật vào vận khí gần nhất (get_thoigianhoitinvatconlai)
        self._thoidiemtinvatgannhat = 0.
        self._thoidiemdongvankhiket = 0.
        # Khoá vận khí triệu hồi bảo thú (action_khoavankhitrieuhoi): None hoặc {"batdau", "toida", "caulenhduocpheps"}
        self._khoavankhitrieuhoi = None
        # Đang spam lệnh triệu hồi bảo thú (pf 4131.@) => không cho dùng kỹ năng nào khác tới thời điểm này
        self._thoidiemhetkhoakynang = 0.
        self._thoidiemlogkhoakynanggannhat = 0.
        # Chống spam kỹ năng không mục tiêu: {id kỹ năng: [thời điểm gửi gần đây]} và {id kỹ năng: thời điểm hết tạm khoá}
        self._thoidiemguikynangkhongmuctieu_map = {}
        self._thoidiemlogspamkynang_map = {}
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
        self._loimoinhom_map = {}  # id trưởng nhóm -> thời điểm nhận lời mời (action_ghiloimoinhom ghi)
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
        # Click xuống đất để đi (get_is_dangclickchuottrai): lần gần nhất thấy chuột trái thật đang bấm trên cửa sổ game, đích click
        # chuột của game (KDK_DICHCLICK) lượt trước
        self._thoidiembamchuottraigannhat = 0.
        self._dichclicktruoc = None
        self._dichclicknguoichoi = None

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
        self._toadolantruoc = None
        self._toadobandocu = None
        self._lucvaobando = {}
        # Lần cuối thấy mình còn ở phó bản mượn ID bản đồ ngoài (Phong Yêu Kính, Tập Kích) và ID mượn đó (get_is_vuaroiphobanmuonbando)
        self._thoidiemophobanmuonbando = 0.
        self._idbandophobanmuon = None
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
        # Hiệu ứng mặt đất: địa chỉ nút -> mã hiệu ứng đã thấy (sprite bị đẩy khỏi bộ đệm thì vẫn biết mã), xem get_danhsachhieuungdat
        self._mahieuungdattheonut = {}
        # Khối cờ ẩn hiển thị (COHIENTHI_VITRI) cấp trong game cho các hook vẽ đọc, xem _get_diachicohienthi
        self._diachicohienthi = None
        # Tâm trận mình vừa đặt: (x, y) -> thời điểm (THOIGIANNHOTAMTRANVUADAT); chữ ký danh sách trận đã ghi log gần nhất
        self._tamtranvuadat = {}
        self._logdanhsachtrangannhat = None
        self._logdanhsachlacanhgannhat = None

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
        # Giữ chỗ Hồi Thành Phù / Tín Vật giữa các bot (GiuHoiThanh, CuaSo gán vào): không bao giờ 2 nhân vật cùng về thành 1 lúc
        self.giuhoithanh = None

        self.thoidiemmuctieuanthangannhat_map = {}
        self.thoidiemmuctieuxuathiengannhat_map = {}

        self.thoidiembaothuxuathiengannhat_map = {}

        self._lichsutrochuyen5s = []
        # Tin mật đến ("<tên> nói thầm với bạn : <nội dung>", chữ tím): [{luc, ten, noidung, id}] 5 phút gần nhất; tên đã gửi "friend ?"
        # (Dò tìm) -> thời điểm; danh sách mật ngữ gần đây lần trước (log khi đổi)
        self._tinmatdens = []
        # Hook đầu hàm thêm dòng khung chat (action_thietlaphookkhungchat): bộ đệm vòng, kịch bản, số dòng đã đọc
        self._diachibodemkhungchat = 0
        self._diachihamkichbankhungchat = 0
        self._demdongkhungchatdadoc = 0
        self._thoidiemdotimtens = {}
        self._lienhetinmatcu = None
        # Bang phái người chơi (action_hoibangphai): ID người chơi -> (tên bang, "" nếu không có bang, thời điểm biết); tên -> ID để tra chủ bảo thú
        self._bangphainguoichoi_map = {}
        self._idnguoichoitheoten_map = {}
        # Môn phái người chơi theo "desc user": ID người chơi -> mã môn phái (khoá của TENMONPHAI) hoặc tên game in ra nếu chưa có trong TENMONPHAI
        self._monphainguoichoi_map = {}
        # (ID, tên, thời điểm gửi) lần "desc user" đang chờ trả lời; tên người chơi đang gom dòng trả lời (sau dòng "Danh tính") và môn phái đã gom
        self._yeucaubangphai = None
        self._tendanggomthongtin = None
        self._monphaidanggomthongtin = None
        self._thoidiemhoibangphaiganhat = 0.
        # Bộ đếm dòng của bộ đệm vòng trò chuyện (action_thietlaphooknoidungtrochuyen) đã đọc tới đâu
        self._demdongtrochuyendadoc = 0

        self._diachiautoassemblenhatvatpham = False
        self._diachiautoassemblekhoitaothongtinbando = False

        self._diachibodemnoidungtrochuyen = False
        self._diachihamkichbannoidungtrochuyen = False
        self._diachihamkichbantinhethong = False
        # Hàm + bộ đệm chuỗi của action_themdongkhungchat
        self._diachithemdongkhungchat = False
        # Vùng dữ liệu của hook vẽ thêm dòng trên danh hiệu (action_thietlaphookvedanhhieu), 0 = chưa đặt
        self._diachidulieuvedanhhieu = 0

        # Hook dò lệnh game tự gửi (action_thietlaphooklenhgame): bộ đệm vòng, đã đọc tới đâu, lệnh bot vừa gửi (để không log trùng)
        self._diachibodemlenhgame = False
        self._diachihamkichbanlenhgame = False
        self._demdonglenhgamedadoc = 0
        self._lenhbotganday = {}
        # Mã đứng sau "pawn" trong lệnh client tự gửi gần nhất (vd "7e#": id Quản Khố hệ 16 kèm #), lúc bắt được: mở kho bằng cách khác
        # (Bảo Khố Di Động...) rồi bấm 1 rương thì client gửi "pawn <mã> <rương>" => sắp xếp kho dùng lại mã này (get_makhoganday)
        self._makhoganday = None
        # Kim Nguyên Bảo đọc được gần nhất (get_kimnguyenbao), None khi chưa đọc
        self._kimnguyenbao = None
        # Trân Bảo Khố: vùng heap lần trước thấy gói tin hàng [(đầu, cỡ)], hàng đã đọc {tên: (tab, ô, giá 0,1 KNB)}
        self._vungtranbaokho = []
        self._hangtranbaokho = {}
        self._thoidiemmakhoganday = 0.
        # Dò cửa sổ kho (action_dokho): cờ đang hiện lần đọc trước, ảnh vùng đầu cấu trúc kho lúc kho đóng (so khi mở)
        self._is_khodanghientruoc = False
        self._anhkhotruoc = None
        # Sửa giờ máy chủ của client sau lag (action_suagiomaychu): độ lệch giờ máy chủ - giờ máy mình lúc mạng tốt, lần đồng bộ đã
        # xét (giờ máy mình lúc đồng bộ), số lần đồng bộ liền nhau cùng tụt (đủ SOLANDONGBOTUTGIOMAYCHU thì tin là giờ thật), lúc đọc
        # gần nhất, lúc vừa sửa giờ gần nhất (get_is_vuasuagiomaychu)
        self._dolechgiomaychutot = None
        self._landongbogiomaychu = 0
        self._solandongbotutgiomaychu = 0
        self._thoidiemsuagiomaychu = 0.
        self._thoidiemvuasuagiomaychu = 0.

    def __del__(self):
        def safe_free_old(flag_name, addr_name):
            try:
                if getattr(self, flag_name, False):
                    addr_ = getattr(self, addr_name, None)
                    if addr_ and hasattr(self, "tientrinh"):
                        self.tientrinh.free(addr_)
            except:
                pass

        # KHÔNG giải phóng kịch bản / bộ đệm của các hook (trò chuyện, tin hệ thống, lệnh game, danh hiệu, cờ nhiệm vụ NPC): mã game vẫn
        # "jmp" vào đó sau khi bot thôi chạy, giải phóng thì client văng ở lần nhận tin / gửi lệnh kế tiếp. Trước đây có giải phóng: nguy
        # hiểm khi CuaSo.__init__ lỗi sau lúc đặt hook (run_bot_process bắt lỗi, MoiTruong bị huỷ trong khi game còn sống). Lần chạy sau
        # hook lệnh game dùng lại kịch bản cũ, hook trò chuyện cấp vùng mới (mỗi lần mở bot sót ~0,6 KB, không đáng kể).
        # Chỉ giải phóng các hàm bot tự gọi bằng luồng riêng (start_thread), mã game không nhảy vào.
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
        if getattr(self, "_doituongtimduongcucbo", None):
            safe_free(self._doituongtimduongcucbo)
        if getattr(self, "_diachithemdongkhungchat", None):
            safe_free(self._diachithemdongkhungchat)

    def _ghilenhvaobonho(self, lenh):
        if not self.diachihamthucthicaulenh:
            self.khoitaohamthucthicaulenh()

        if self.diachihamthucthicaulenh:
            if self._is_lenhkynangdavaohoichieu(lenh):
                # Kỹ năng đã vào hồi chiêu = lệnh cùng chiêu trước đó đã được nhận: chờ vận khí coi như đã chấp nhận
                self._bochovankhi(lenh.caulenh, is_dachapnhan = True)
                return
            # Lệnh vào hàng đợi trước khi khoá vận khí triệu hồi mà tới giờ mới gửi: bỏ (vòng lặp sau tự gửi lại nếu còn cần)
            if self._is_lenhbichankhoavankhi(lenh.caulenh):
                self._loglenh(lenh.caulenh, "bỏ: đang khoá vận khí triệu hồi")
                self._bochovankhi(lenh.caulenh)
                return
            # Lệnh chiêu / đánh vào hàng đợi trước khi bị choáng (hoặc Trầm Mặc với phái phép thuật) mà tới giờ mới gửi: bỏ, hết khống chế vòng lặp tự gửi lại
            if (lenh.caulenh.startswith("pf ") and self.get_is_khongthedungkynang()) or (lenh.caulenh.startswith("kill ") and self._is_nhanvatbichoang):
                self._loglenh(lenh.caulenh, "bỏ: đang bị khống chế")
                self._bochovankhi(lenh.caulenh)
                return
            self._loglenh(lenh.caulenh, f"hàng đợi, ưu tiên {lenh.douutien}")
            diachidulieu = self.diachihamthucthicaulenh + 0x40
            chuoi_bytes = lenh.caulenh.encode("utf-8")

            write_int(self.tientrinh, diachidulieu, len(chuoi_bytes))
            write_bytes(self.tientrinh, diachidulieu + 4, chuoi_bytes + b"\x00", len(chuoi_bytes) + 1)

            self.tientrinh.start_thread(self.diachihamthucthicaulenh)
            self._danhdauguilenhvankhi(lenh.caulenh)
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

        # Hàm gửi lệnh dò sẵn từ file (DC). Trước đây quét bộ nhớ tìm chỗ gọi nó: Niết Bàn (ChienQuocNietBan.dll vá mã) làm quét bộ nhớ
        # không ra => mọi lệnh hàng đợi bị bỏ im lặng
        diachi_ham = self.diachixq + DC.HAMGUILENH

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

    def _doilenhnietban(self, caulenh):
        # Niết Bàn nói chuyện NPC bằng "talk", không phải "tallk"
        if self.is_nietban and caulenh.startswith("tallk "):
            return "talk " + caulenh[6:]
        return caulenh

    def action_thucthicaulenh(self, caulenh, douutien = DOUUTIEN_TRUNGBINH, vitrikynang = None):
        caulenh = self._doilenhnietban(caulenh)
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
        caulenh = self._doilenhnietban(caulenh)
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
        self._lenhbotganday[caulenh] = time.time()
        if IS_LOGCAULENH:
            self._inlog(f"[LỆNH {nguon}] {caulenh}")

    def get_thoidiemlenhdanhgannhat(self):
        # Lần gửi kỹ năng gần nhất. "kill" chỉ là yêu cầu máy chủ bắt đầu đánh thường (không phải chiêu / đòn đánh, không ra ngay) nên
        # không tính: gửi kill xong vẫn gửi chiêu được ngay
        return self._thoidiemsudungkynanggannhat

    def get_is_kynangdangbikhoa(self, idkynang):
        # Đang khoá mọi kỹ năng hoặc riêng kỹ năng này đang giãn nhịp chống spam: gửi lúc này chắc chắn không đi (không log)
        thoidiemhientai = time.time()
        return thoidiemhientai < self._thoidiemhetkhoakynang or self._is_dangiannhipspam(idkynang, thoidiemhientai)

    def _is_dangiannhipspam(self, idkynang, thoidiemhientai):
        # Đã gửi >= SOLANGUITOIDASPAMKYNANG lần trong SOGIAYDEMSPAMKYNANG giây mà chưa ra và lần gửi cuối chưa quá KHOANGCACHGUISPAMKYNANG giây
        thoidiemguis = [t for t in self._thoidiemguikynangkhongmuctieu_map.get(idkynang, []) if thoidiemhientai - t < SOGIAYDEMSPAMKYNANG]
        return len(thoidiemguis) >= SOLANGUITOIDASPAMKYNANG and thoidiemhientai - thoidiemguis[-1] < KHOANGCACHGUISPAMKYNANG

    def _is_kynangbispam(self, idkynang):
        # Không kỹ năng nào cần gửi dồn dập (chiêu nào cũng có hồi chiêu >= 1s): game báo "sẵn sàng" mà kỹ năng không ra (bị khống chế
        # mà bot chưa biết hiệu ứng như mộng du, mục tiêu đặc biệt...) thì trước đây cứ gửi lại mỗi lượt (Cam Lộ Trì 625 lần / 3 phút làm
        # server đơ), ngập hàng đợi lệnh khiến các kỹ năng khác không chen vào được. Áp cho cả kỹ năng có mục tiêu.
        # Không khoá kỹ năng: chỉ giãn nhịp còn 1 lần / KHOANGCACHGUISPAMKYNANG giây, giữa các lần gửi kỹ năng khác vẫn chen vào
        if idkynang in IDKYNANGKHONGCHANSPAMs:
            return False
        thoidiemhientai = time.time()
        thoidiemguis = [t for t in self._thoidiemguikynangkhongmuctieu_map.get(idkynang, []) if thoidiemhientai - t < SOGIAYDEMSPAMKYNANG]
        if len(thoidiemguis) >= SOLANGUITOIDASPAMKYNANG:
            if thoidiemhientai - thoidiemguis[-1] < KHOANGCACHGUISPAMKYNANG:
                return True
            if thoidiemhientai - self._thoidiemlogspamkynang_map.get(idkynang, 0.) >= THOIGIANLOGSPAMKYNANG:
                self._thoidiemlogspamkynang_map[idkynang] = thoidiemhientai
                # Ghi kèm hiệu ứng đang có trên người để tìm ra khống chế nào làm kỹ năng không ra
                hieuungs = [(idhieuung, is_coloi) for idhieuung, is_coloi, _ in self.get_danhsachhieuungnhanvats()]
                self._inlog(f"[CHẶN SPAM] kỹ năng {idkynang} gửi {len(thoidiemguis)} lần trong {SOGIAYDEMSPAMKYNANG}s mà vẫn sẵn sàng => giãn nhịp"
                            f" {KHOANGCACHGUISPAMKYNANG}s/lần | hiệu ứng (id, có lợi): {hieuungs}")
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
        is_ok = self.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO, vitrikynang = vitrikynang)
        if is_ok and idkynang in KYNANGDOHOATANHs:
            self._thoidiembotguidohoatanh = (idkynang, time.time())
        return is_ok

    def _dohoatanhchieu(self):
        # Đo mã hoạt ảnh chiêu (tạm, bật khi KYNANGDOHOATANHs khác rỗng): theo dõi liên tục chỉ số ghi hàng đợi hành động của nhân vật
        # mình, log ô đòn đánh mới (mã >= 0x28) có mã hoạt ảnh chưa biết (ngoài MAHOATANHDABIETs) - bắt được cả chiêu bấm tay; trong
        # THOIGIANDOHOATANH giây sau khi bot gửi chiêu trong KYNANGDOHOATANHs thì log mọi ô.
        if not KYNANGDOHOATANHs:
            return
        try:
            nhanvat = struct.unpack("<I", read_bytes(self.tientrinh, self.diachixq + DC.NHANVAT, 4))[0]
            moi = struct.unpack("<I", read_bytes(self.tientrinh, nhanvat + DC.NV_HOATANH + 4, 4))[0]
        except Exception:
            return
        do = self._dohoatanh
        if not do or do["nhanvat"] != nhanvat or not 0 <= do["ghi"] < 100:
            self._dohoatanh = {"nhanvat": nhanvat, "ghi": moi}
            return
        botgui = self._thoidiembotguidohoatanh
        thoidiemhientai = time.time()
        try:
            while do["ghi"] != moi and 0 <= moi < 100:
                o = read_bytes(self.tientrinh, nhanvat + 0x100 + do["ghi"] * 0x28, 12)
                is_botvuagui = botgui and thoidiemhientai - botgui[1] < THOIGIANDOHOATANH
                if o[0] >= 0x28 and (o[4] not in MAHOATANHDABIETs or is_botvuagui):
                    nguon = f"bot gửi {botgui[0]} +{thoidiemhientai - botgui[1]:.2f}s" if is_botvuagui else "không do bot gửi"
                    self._inlog(f"[ĐO HOẠT ẢNH] ({nguon}) ô {do['ghi']} mã {o[0]} biến thể {o[1]} hoạt ảnh {o[4]} | {o.hex(' ')}")
                do["ghi"] = (do["ghi"] + 1) % 100
        except Exception:
            self._dohoatanh = None

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
            muctieu = str(self.get_idnguoichoi(diachicosothongtinnhanvatmuctieudangchon))
        else:
            muctieu = "{:x}#".format(self.get_iddoituong(diachicosothongtinnhanvatmuctieudangchon))
        # Niết Bàn Đường Môn: "kill" vẫn bắn từ xa (đo: bấm chuột trái client cũng gửi đúng "kill <id>#", đứng yên bắn ở 5 ô).
        # Không dùng "pf2 15" (Tự Động Xạ Kích): gửi lần 2 là tắt
        caulenh = "kill {}".format(muctieu)

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

    def action_sudungvatpham(self, iddoituong, is_boquaxacnhan = False, delay = 0.2, douutien = DOUUTIEN_KHANCAP, is_use2 = False):
        # is_use2: "use2 <id>#" = lệnh nút Xác Nhận của hộp hỏi khi dùng (VATPHAMDUNGUSE2s), gửi thẳng không cần "use" trước
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False
        self._thoidiemsudungvatphamgannhat = time.time()
        if is_use2:
            caulenh = f"use2 {iddoituong:x}#"
        else:
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

    def action_ghiloimoinhom(self):
        # Hộp "Đội ngũ X muốn cùng bạn kết thành nhóm" (lệnh Xác Nhận "team + <id>"): ghi lời mời vào _loimoinhom_map để
        # action_kiemtravadongyloimoinhom nhận lời được kể cả khi hộp đã bị lời mời khác ghi đè. KHÔNG đóng hộp: lời mời của người
        # bot không tự nhận vẫn hiện cho người dùng tự bấm
        hop, lenh = self.get_hopxacnhannpc()
        if not hop or not lenh.startswith("team "):
            return
        phan = lenh.split("team + ")
        if len(phan) > 1 and phan[1].strip().isdigit():
            self._loimoinhom_map[int(phan[1])] = time.time()

    def action_kiemtravadongyloimoinhom(self, idtruongnhoms, delay = 0.2):
        if time.time() - self._thoidiemthaotacnhomgannhat < delay:
            return False
        if not idtruongnhoms:
            return False
        self.action_ghiloimoinhom()
        # Lời mời quá 60s coi như hết hạn
        self._loimoinhom_map = {id: t for id, t in self._loimoinhom_map.items() if time.time() - t < 60}
        for idnguoichoitruongnhom in idtruongnhoms:
            if idnguoichoitruongnhom in self._loimoinhom_map:
                del self._loimoinhom_map[idnguoichoitruongnhom]
                caulenh = "team + {}".format(idnguoichoitruongnhom)
                # Hộp đang hiện đúng lời mời này thì đóng như game tự đóng sau khi bấm Xác Nhận
                if self.get_hopxacnhannpc()[1] == caulenh:
                    self.action_donghopxacnhannpc()
                self.action_thucthicaulenh(caulenh)
                self._thoidiemthaotacnhomgannhat = time.time()
                break
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
        # tạo xq + 0xCEEB0 (trả về this) rồi gán vào [thông tin game] + 0xADFDEC, không đụng tới cửa sổ bản đồ.
        # Chỉ 1 luồng khởi tạo mỗi lúc: start_thread chờ luồng chạy xong, luồng gọi sau chờ khoá rồi thấy đã có cấu trúc thì bỏ qua
        with self._khoakhoitaothongtinbando:
            if self.get_is_dakhoitaothongtinbando():
                return
            self._khoitaothongtinbando()

    def _khoitaothongtinbando(self):
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
        # 2 chỗ hook cùng chép vào 1 bộ đệm vòng: tin khung trò chuyện (HOOK_TROCHUYEN) và gói 0x3E game chỉ in vào khung tin hệ thống
        # (HOOK_TINHETHONG, vd trả lời "desc user": " Danh tính / Bang phái ..."), cả 2 đều có dòng chữ ở ebp
        diachihooks = (
            (self.diachixq + DC.HOOK_TROCHUYEN, f"mov ecx, [edx + {hex(DC.TG_TROCHUYEN)}]", "_diachihamkichbannoidungtrochuyen"),
            (self.diachixq + DC.HOOK_TINHETHONG, "mov ecx, [ecx + 0xadfd64]", "_diachihamkichbantinhethong"),
        )

        if not self._is_dasetupactionthietlaphooknoidungtrochuyen:
            # Bộ đệm vòng: [+0] bộ đếm số dòng đã ghi, rồi SOLUONGDONGTROCHUYEN ô x KICHTHUOCDONGTROCHUYEN byte. Trước đây chỉ 1 ô, dòng sau
            # đè dòng trước nên nhiều tin trong cùng 1 vòng làm mới (dame, nhặt đồ, bảo thú...) thì bot chỉ thấy tin cuối
            self._diachibodemnoidungtrochuyen = self.tientrinh.allocate(4 + SOLUONGDONGTROCHUYEN * KICHTHUOCDONGTROCHUYEN)
            write_int(self.tientrinh, self._diachibodemnoidungtrochuyen, 0)

            ks = Ks(KS_ARCH_X86, KS_MODE_32)
            for addr_at_hook, lenhgoc, tenbien in diachihooks:
                diachikichban = self.tientrinh.allocate(256)
                setattr(self, tenbien, diachikichban)
                # Chép dòng (ebp) vào ô [bộ đếm % số ô], chép xong mới tăng bộ đếm để bot không đọc ô đang chép dở; rồi chạy lại lệnh gốc bị đè
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
                    {lenhgoc}
                    push {addr_at_hook + 6}
                    ret
                """

                encoding, count = ks.asm(asm_script)
                if not encoding:
                    raise Exception("Lỗi compile ASM Keystone")

                write_bytes(self.tientrinh, diachikichban, bytes(encoding), len(encoding))

            self._is_dasetupactionthietlaphooknoidungtrochuyen = True

        for addr_at_hook, _, tenbien in diachihooks:
            relative_offset = getattr(self, tenbien) - (addr_at_hook + 5)
            patch_bytes = b"\xE9" + relative_offset.to_bytes(4, byteorder = "little", signed = True) + b"\x90"
            write_bytes(self.tientrinh, addr_at_hook, patch_bytes, len(patch_bytes))

        return True

    def action_thietlaphookvedanhhieu(self):
        # Game vẽ danh hiệu (+0x1134) phía trên tên bằng 1 lần gọi HAMVECHU, hàm này KHÔNG xử lý xuống dòng => chèn mã ở chỗ gọi. Có 3
        # chỗ (dò 2026-11-05): HOOK_VEDANHHIEU xq+0x1D0A8 quái / NPC (ebx = đối tượng), HOOK_VEDANHHIEU2 xq+0x9C34F nhân vật mình (ebx),
        # HOOK_VEDANHHIEU3 xq+0x9CF52 người chơi khác (edi) - trước chỉ hook chỗ đầu nên mục tiêu là người chơi không hiện dòng thêm.
        # Dữ liệu chung: SODOITUONGVEDANHHIEU khối KICHTHUOCKHOIVEDANHHIEU byte, mỗi khối [+0] đối tượng, [+4] số dòng, dòng i ở +8 +
        # i * KICHTHUOCDONGVEDANHHIEU. Đối tượng đang vẽ trùng khối nào thì vẽ thêm các dòng của khối đó lên trên danh hiệu, mỗi dòng
        # cao KHOANGCACHDONGCHU px, canh giữa theo độ rộng HAMDORONGCHU như game canh danh hiệu (+0x1130). Rồi vẽ danh hiệu như cũ.
        # Tham số HAMVECHU (thiscall ecx = [BIENVECHU], ret 0x18): surface, chữ, x, y, màu, 0. Chỉ ở client này, không gửi gì lên máy chủ.
        # Bản Aegis có chienquoc2d.dll (bộ vẽ chữ tiếng Việt) đã thay các call này bằng "jmp <đoạn nối của DLL>": pushfd, pushad, gọi
        # f(ecx gốc, đối tượng, &6 tham số, tâm ngang) (cdecl; "53 50 52 51 E8 rel32"), bỏ 6 tham số rồi nhảy về sau lệnh. f tự canh
        # giữa theo tâm (chỗ 1: edi, chỗ 2 / 3: ebp). Khi đó chèn nối tiếp: jmp sang mã mình, vẽ dòng thêm bằng f, rồi nhảy vào đoạn nối.
        # Mã mình đánh dấu DAUHIEUKICHBANVEDANHHIEU + 5 byte gốc ở cuối vùng => lần chạy bot sau nhận ra, lấy lại byte gốc (không nối chồng)
        # -> địa chỉ vùng dữ liệu, 0 nếu không đặt được chỗ nào
        if self._diachidulieuvedanhhieu:
            return self._diachidulieuvedanhhieu
        dulieu = self.tientrinh.allocate(SODOITUONGVEDANHHIEU * KICHTHUOCKHOIVEDANHHIEU)
        for k in range(SODOITUONGVEDANHHIEU):
            write_bytes(self.tientrinh, dulieu + k * KICHTHUOCKHOIVEDANHHIEU, b"\0" * 8, 8)
        # (chỗ hook, ô pushad của thanh ghi đối tượng, ô pushad của tâm ngang): ô pushad edi 0, ebp 8, ebx 0x10
        chohooks = ((DC.HOOK_VEDANHHIEU, 0x10, 0), (DC.HOOK_VEDANHHIEU2, 0x10, 8), (DC.HOOK_VEDANHHIEU3, 0, 8))
        dadat = []
        for chohook, odoituong, otam in chohooks:
            try:
                kieu = self._dathookvedanhhieu(self.diachixq + chohook, dulieu, odoituong, otam)
            except Exception as err:
                kieu = None
                self._inlog(f"[DANH HIỆU] lỗi đặt hook ở xq+{chohook:#x}: {err}")
            if kieu:
                dadat.append(f"xq+{chohook:#x} {kieu}")
        if not dadat:
            return 0
        self._diachidulieuvedanhhieu = dulieu
        self._inlog(f"[DANH HIỆU] đã đặt hook vẽ thêm dòng trên danh hiệu: {', '.join(dadat)}")
        return dulieu

    def _dathookvedanhhieu(self, diachihook, dulieu, odoituong, otam):
        # Đặt 1 chỗ hook (xem action_thietlaphookvedanhhieu) -> "call gốc" / "nối sau chienquoc2d.dll", None nếu không đặt được
        hamvechu = self.diachixq + DC.HAMVECHU
        mahook = read_bytes(self.tientrinh, diachihook, 5)
        if mahook[0] in (0xE8, 0xE9):
            dich = diachihook + 5 + struct.unpack("<i", mahook[1:5])[0]
            try:
                danhdau = read_bytes(self.tientrinh, dich + KICHTHUOCKICHBANVEDANHHIEU - 0x10, 9)
            except Exception:
                danhdau = b""
            if danhdau[:4] == DAUHIEUKICHBANVEDANHHIEU:
                mahook = danhdau[4:9]
            elif mahook[0] == 0xE8 and dich != hamvechu:
                # Kịch bản bản cũ (chưa đánh dấu) trỏ call vào nó: gốc là call HAMVECHU
                mahook = b"\xE8" + struct.pack("<i", hamvechu - (diachihook + 5))
        if mahook[0] == 0xE8:
            # Lệnh gốc: call HAMVECHU (không có DLL) -> mã mình được call: tham số gốc từ [ebp + 0x24] (sau pushad + địa chỉ trở về)
            is_dll, dichcuoi, base, hamdll = False, hamvechu, 0x24, 0
        elif mahook[0] == 0xE9:
            dichcuoi = diachihook + 5 + struct.unpack("<i", mahook[1:5])[0]
            try:
                noidll = read_bytes(self.tientrinh, dichcuoi, 0x28)
            except Exception:
                noidll = b""
            vitri = noidll.find(bytes.fromhex("53505251E8"))
            if noidll[:6] != bytes.fromhex("9C608D442424") or vitri < 0:
                self._inlog(f"[DANH HIỆU] chỗ vẽ danh hiệu bị chèn lạ: {mahook.hex(' ')} -> {noidll.hex(' ')}")
                return None
            is_dll, base = True, 0x20
            hamdll = dichcuoi + vitri + 9 + struct.unpack("<i", noidll[vitri + 5:vitri + 9])[0]
        else:
            self._inlog(f"[DANH HIỆU] chỗ vẽ danh hiệu không phải lệnh call / jmp: {mahook.hex(' ')}")
            return None
        kichban = self.tientrinh.allocate(KICHTHUOCKICHBANVEDANHHIEU)
        # ebx = đối tượng (lấy từ ô pushad của thanh ghi gốc); [ebp - 4] khối của đối tượng, [ebp - 8] tâm ngang danh hiệu; tham số gốc
        # (surface, chữ, x, y, màu, 0) từ [ebp + base]
        if is_dll:
            # f(ecx = [BIENVECHU], đối tượng, &tham số, tâm ngang gốc), cdecl: tự dọn 4 + 6 tham số
            goive = f"""
            mov eax, esp
            push dword ptr [ebp + {otam}]
            push eax
            push ebx
            push dword ptr [{self.diachixq + DC.BIENVECHU}]
            mov eax, {hamdll}
            call eax
            add esp, 0x28
            """
        else:
            goive = f"""
            mov ecx, dword ptr [{self.diachixq + DC.BIENVECHU}]
            mov eax, {hamvechu}
            call eax
            """
        asm_script = f"""
            pushad
            mov ebp, esp
            mov ebx, dword ptr [ebp + {odoituong}]
            mov eax, {dulieu}
            mov ecx, {SODOITUONGVEDANHHIEU}
        tim:
            cmp ebx, dword ptr [eax]
            je thay
            add eax, {KICHTHUOCKHOIVEDANHHIEU}
            dec ecx
            jnz tim
            jmp xong
        thay:
            push eax
            mov edx, dword ptr [ebx + 0x1130]
            sar edx, 1
            add edx, dword ptr [ebp + {base + 8}]
            push edx
            xor esi, esi
        lap:
            mov eax, dword ptr [ebp - 4]
            cmp esi, dword ptr [eax + 4]
            jge xong
            mov edi, esi
            imul edi, edi, {KICHTHUOCDONGVEDANHHIEU}
            add edi, eax
            add edi, 8
            push edi
            mov ecx, ebx
            mov eax, {self.diachixq + DC.HAMDORONGCHU}
            call eax
            sar eax, 1
            mov edx, dword ptr [ebp - 8]
            sub edx, eax
            push dword ptr [ebp + {base + 0x14}]
            push dword ptr [ebp + {base + 0x10}]
            lea eax, [esi + 1]
            imul eax, eax, {KHOANGCACHDONGCHU}
            mov ecx, dword ptr [ebp + {base + 0xC}]
            sub ecx, eax
            push ecx
            push edx
            push edi
            push dword ptr [ebp + {base}]
            {goive}
            inc esi
            jmp lap
        xong:
            mov esp, ebp
            popad
        goc:
            push {dichcuoi}
            ret
        """
        encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
        if not encoding or len(encoding) > KICHTHUOCKICHBANVEDANHHIEU - 0x10:
            self._inlog("[DANH HIỆU] lỗi dịch mã hook vẽ danh hiệu")
            return None
        write_bytes(self.tientrinh, kichban, bytes(encoding), len(encoding))
        write_bytes(self.tientrinh, kichban + KICHTHUOCKICHBANVEDANHHIEU - 0x10, DAUHIEUKICHBANVEDANHHIEU + mahook, 9)
        lenhmoi = (b"\xE9" if is_dll else b"\xE8") + struct.pack("<i", kichban - (diachihook + 5))
        write_bytes(self.tientrinh, diachihook, lenhmoi, 5)
        return "nối sau chienquoc2d.dll" if is_dll else "call gốc"

    def action_ghidongvedanhhieu(self, diachidoituong, dongs, okhoi = 0):
        # Đặt các dòng vẽ thêm trên danh hiệu của diachidoituong vào khối okhoi (OKHOIMUCTIEU / OKHOINHANVAT; dongs: bytes, dòng 0 sát danh hiệu,
        # tối đa SODONGVEDANHHIEU); diachidoituong 0 / dongs rỗng = thôi vẽ. Ghi chữ trước, số dòng và đối tượng sau để game không đọc
        # ô đang ghi dở
        dulieu = self.action_thietlaphookvedanhhieu()
        if not dulieu or not 0 <= okhoi < SODOITUONGVEDANHHIEU:
            return False
        khoi = dulieu + okhoi * KICHTHUOCKHOIVEDANHHIEU
        dongs = [d[:KICHTHUOCDONGVEDANHHIEU - 1] for d in (dongs or [])][:SODONGVEDANHHIEU]
        if not diachidoituong or not dongs:
            write_bytes(self.tientrinh, khoi, b"\0" * 8, 8)
            return True
        if read_int(self.tientrinh, khoi) != diachidoituong:
            write_int(self.tientrinh, khoi + 4, 0)
        for i, dong in enumerate(dongs):
            write_bytes(self.tientrinh, khoi + 8 + i * KICHTHUOCDONGVEDANHHIEU, dong + b"\0", len(dong) + 1)
        write_int(self.tientrinh, khoi + 4, len(dongs))
        write_int(self.tientrinh, khoi, diachidoituong)
        return True

    def action_themdongkhungchat(self, noidung):
        # In dòng chữ của bot vào khung trò chuyện của client (chỉ hiện ở máy này, không gửi gì lên máy chủ): gọi đúng hàm game dùng khi
        # nhận tin trò chuyện / tin hệ thống, [TG + TG_KHUNGCHAT]->HAMTHEMDONGKHUNGCHAT(chuỗi UTF-8, 0) (thiscall, ret 8).
        # "\n" xuống dòng, ESC + 1 chữ là mã màu của game. Chạy ở luồng riêng như các hàm gọi khác, chờ xong mới trả về để lần gọi
        # sau không ghi đè chuỗi đang in
        if not self._diachithemdongkhungchat:
            diachi = self.tientrinh.allocate(0x40 + KICHTHUOCDONGKHUNGCHAT)
            asm_script = f"""
                mov eax, dword ptr [{hex(self.diachixq + DC.THONGTINGAME)}]
                test eax, eax
                je ketthuc
                mov ecx, dword ptr [eax + {hex(DC.TG_KHUNGCHAT)}]
                test ecx, ecx
                je ketthuc
                push 0
                push {hex(diachi + 0x40)}
                mov eax, {hex(self.diachixq + DC.HAMTHEMDONGKHUNGCHAT)}
                call eax
            ketthuc:
                ret 4
            """
            encoding, count = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
            if not encoding or len(encoding) > 0x40:
                return False
            write_bytes(self.tientrinh, diachi, bytes(encoding), len(encoding))
            self._diachithemdongkhungchat = diachi
        # Cắt theo byte UTF-8 cho vừa bộ đệm, không cắt đôi ký tự
        chuoi_bytes = noidung.encode("utf-8")[:KICHTHUOCDONGKHUNGCHAT - 1].decode("utf-8", errors = "ignore").encode("utf-8")
        write_bytes(self.tientrinh, self._diachithemdongkhungchat + 0x40, chuoi_bytes + b"\x00", len(chuoi_bytes) + 1)
        luong = self.tientrinh.start_thread(self._diachithemdongkhungchat)
        if luong:
            ctypes.windll.kernel32.WaitForSingleObject(luong, 2000)
            ctypes.windll.kernel32.CloseHandle(luong)
        return True

    def action_thietlaphooklenhgame(self):
        # Dò lệnh client tự gửi lên máy chủ: hook đầu hàm gửi lệnh (HAMGUILENH + 5 là "sub esp, 0xC8", 5 byte đầu là chỗ
        # action_vohieuhoahookchienquoc2 NOP nên không đụng), chép câu lệnh (tham số 1) vào bộ đệm vòng rồi chạy tiếp hàm gốc
        if not IS_LOGLENHGAME:
            return False
        addr_at_hook = self.diachixq + DC.HAMGUILENH + 5
        mahook = read_bytes(self.tientrinh, addr_at_hook, 6)
        if mahook[0] == 0xE9 and mahook[5] == 0x90:
            # Hook của lần bot chạy trước vẫn còn trong game (vẫn ghi lệnh vào bộ đệm cũ): đọc lại địa chỉ bộ đệm từ "mov ebx, <bộ đệm>"
            # trong kịch bản, không thì lần chạy sau không log được lệnh game nào (Niết Bàn 2026-11-03)
            kichban = addr_at_hook + 5 + struct.unpack("<i", mahook[1:5])[0]
            try:
                ma = read_bytes(self.tientrinh, kichban, 16)
            except Exception:
                return False
            vitri = ma.find(b"\xBB")
            if vitri < 0 or vitri + 5 > len(ma):
                return False
            self._diachihamkichbanlenhgame = kichban
            self._diachibodemlenhgame = struct.unpack("<I", ma[vitri + 1:vitri + 5])[0]
            self._demdonglenhgamedadoc = read_int(self.tientrinh, self._diachibodemlenhgame)
            self._inlog("[LỆNH GAME] dùng lại hook dò lệnh game của lần chạy trước")
            return True
        if mahook != bytes.fromhex("81 EC C8 00 00 00"):
            return False

        if not self._diachihamkichbanlenhgame:
            self._diachibodemlenhgame = self.tientrinh.allocate(4 + SOLUONGDONGLENHGAME * KICHTHUOCDONGLENHGAME)
            write_int(self.tientrinh, self._diachibodemlenhgame, 0)
            diachikichban = self.tientrinh.allocate(256)
            # Sau pushad tham số 1 (câu lệnh) ở [esp + 0x24]; chép xong mới tăng bộ đếm để bot không đọc ô đang chép dở
            asm_script = f"""
                pushad
                mov esi, dword ptr [esp + 0x24]
                test esi, esi
                jz ketthuc
                mov ebx, {self._diachibodemlenhgame}
                mov eax, dword ptr [ebx]
                and eax, {SOLUONGDONGLENHGAME - 1}
                imul eax, eax, {KICHTHUOCDONGLENHGAME}
                lea edi, [ebx + eax + 4]
                mov ecx, {KICHTHUOCDONGLENHGAME - 1}
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
            ketthuc:
                popad
                sub esp, 0xc8
                push {addr_at_hook + 6}
                ret
            """
            encoding, count = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
            if not encoding:
                return False
            write_bytes(self.tientrinh, diachikichban, bytes(encoding), len(encoding))
            self._diachihamkichbanlenhgame = diachikichban

        relative_offset = self._diachihamkichbanlenhgame - (addr_at_hook + 5)
        patch_bytes = b"\xE9" + relative_offset.to_bytes(4, byteorder = "little", signed = True) + b"\x90"
        write_bytes(self.tientrinh, addr_at_hook, patch_bytes, len(patch_bytes))
        self._inlog("[LỆNH GAME] đã đặt hook dò lệnh game tự gửi")
        return True

    def action_thietlaphookkhungchat(self):
        # Tin mật "<tên> nói thầm với bạn : ..." không đi qua HOOK_TROCHUYEN / HOOK_TINHETHONG (test 2026-11-10: ChâuSa nhắn, bot không
        # thấy dòng nào). Hook thẳng đầu hàm thêm dòng khung chat HAMTHEMDONGKHUNGCHAT (156 chỗ gọi, mọi dòng khung chat đều qua đây),
        # thiscall (chuỗi, cờ): sau pushad chuỗi ở [esp + 0x24]. 7 byte đầu "push -1; push <SEH>" (6A FF 68 ..) chép nguyên vào kịch bản
        # rồi nhảy về +7. Bộ đệm vòng riêng, không lẫn với bộ đệm trò chuyện cũ (tránh xử lý 2 lần tin hệ thống)
        addr_at_hook = self.diachixq + DC.HAMTHEMDONGKHUNGCHAT
        try:
            mahook = read_bytes(self.tientrinh, addr_at_hook, 7)
        except Exception:
            return False
        if mahook[0] == 0xE9 and mahook[5:7] == b"\x90\x90":
            # Hook của lần bot chạy trước còn trong game: đọc lại bộ đệm từ "mov ebx, <bộ đệm>" trong kịch bản
            kichban = addr_at_hook + 5 + struct.unpack("<i", mahook[1:5])[0]
            try:
                ma = read_bytes(self.tientrinh, kichban, 24)
            except Exception:
                return False
            vitri = ma.find(b"\xBB")
            if vitri < 0 or vitri + 5 > len(ma):
                return False
            self._diachihamkichbankhungchat = kichban
            self._diachibodemkhungchat = struct.unpack("<I", ma[vitri + 1:vitri + 5])[0]
            self._demdongkhungchatdadoc = read_int(self.tientrinh, self._diachibodemkhungchat)
            self._inlog("[KHUNG CHAT] dùng lại hook khung chat của lần chạy trước")
            return True
        if mahook[0:3] != b"\x6A\xFF\x68":
            self._inlog(f"[KHUNG CHAT] đầu hàm thêm dòng khung chat lạ ({mahook.hex(' ')}), không hook: không đọc được tin mật")
            return False
        if not self._diachihamkichbankhungchat:
            self._diachibodemkhungchat = self.tientrinh.allocate(4 + SOLUONGDONGTROCHUYEN * KICHTHUOCDONGTROCHUYEN)
            write_int(self.tientrinh, self._diachibodemkhungchat, 0)
            diachikichban = self.tientrinh.allocate(256)
            seh = struct.unpack("<I", mahook[3:7])[0]
            asm_script = f"""
                pushad
                mov esi, dword ptr [esp + 0x24]
                test esi, esi
                jz ketthuc
                mov ebx, {self._diachibodemkhungchat}
                mov eax, dword ptr [ebx]
                and eax, {SOLUONGDONGTROCHUYEN - 1}
                imul eax, eax, {KICHTHUOCDONGTROCHUYEN}
                lea edi, [ebx + eax + 4]
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
            ketthuc:
                popad
                push -1
                push {seh}
                push {addr_at_hook + 7}
                ret
            """
            encoding, count = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
            if not encoding:
                return False
            write_bytes(self.tientrinh, diachikichban, bytes(encoding), len(encoding))
            self._diachihamkichbankhungchat = diachikichban
        relative_offset = self._diachihamkichbankhungchat - (addr_at_hook + 5)
        patch_bytes = b"\xE9" + relative_offset.to_bytes(4, byteorder = "little", signed = True) + b"\x90\x90"
        write_bytes(self.tientrinh, addr_at_hook, patch_bytes, len(patch_bytes))
        self._inlog("[KHUNG CHAT] đã đặt hook đọc dòng khung chat (tin mật)")
        return True

    def _docdongkhungchatmois(self):
        # Các dòng mới thêm vào khung chat từ lần đọc trước (bỏ mã màu ESC + 1 chữ), như _docdongtrochuyenmois
        if not self._diachibodemkhungchat:
            return []
        try:
            dulieu = read_bytes(self.tientrinh, self._diachibodemkhungchat, 4 + SOLUONGDONGTROCHUYEN * KICHTHUOCDONGTROCHUYEN)
        except Exception:
            return []
        dem = struct.unpack_from("<I", dulieu, 0)[0]
        dadoc = self._demdongkhungchatdadoc
        if dem < dadoc:
            dadoc = 0
        dadoc = max(dadoc, dem - SOLUONGDONGTROCHUYEN)
        self._demdongkhungchatdadoc = dem
        dongs = []
        for i in range(dadoc, dem):
            vitri = 4 + (i % SOLUONGDONGTROCHUYEN) * KICHTHUOCDONGTROCHUYEN
            o = dulieu[vitri:vitri + KICHTHUOCDONGTROCHUYEN]
            o = o[:o.find(b"\x00")] if b"\x00" in o else o
            tho = o.decode("utf-8", errors = "ignore")
            noidung = re.sub(r"\x1b[a-zA-Z0-9]", "", tho).strip()
            if "thầm" in noidung:
                # Dòng thô (còn mã màu) để dò khi mẫu tin mật không khớp
                self._inlog(f"[KHUNG CHAT] {tho!r}")
            if noidung:
                dongs.append(noidung)
        return dongs

    def action_thietlaphookcotnhiemvunpc(self):
        # Chặn crash client ở xq+0x21837 (dump C:\CrashDumps 2026-11-08 16:15 và 16:42, cả 2 lần acc chính 364, 3-5s sau khi rời Phong
        # Yêu Kính về bản đồ 80): hàm xq+0x21790 duyệt bảng dấu nhiệm vụ NPC xq+0x206040 (400 bản ghi x 0xE94, mỗi dòng 0x7C = loại +
        # 30 số cờ), lấy số cờ / 8 làm chỉ số byte trong vùng cờ [KHOIDIEUKHIEN] + 0x1663. Gói tin máy chủ chỉ ghi số cờ 16 bit (movsx
        # word, xq+0x9FBA3), thật đo được ~0x628-0x62A; nhưng cả 2 dump đều có 1 ô rác giống con trỏ heap (0x0E6CB7C8 / 0x11780898) ở
        # đúng 0x606118 => đọc lệch ~30MB, văng game. Chưa tìm ra ai ghi rác (không lệnh ghi nào của bot nhắm vào đó).
        # Chỗ hook HOOK_COTNHIEMVUNPC: "mov ecx, [esi]; test ecx, ecx; je <bỏ ô>" (6 byte) -> thêm: số cờ ngoài 1..0x7FFF cũng bỏ ô
        # như ô trống. Kịch bản không bao giờ giải phóng (game còn nhảy vào sau khi bot tắt); lần chạy sau thấy đã vá thì thôi.
        diachihook = self.diachixq + DC.HOOK_COTNHIEMVUNPC
        try:
            mahook = read_bytes(self.tientrinh, diachihook, 6)
        except Exception:
            return False
        if mahook[0] == 0xE9 and mahook[5] == 0x90:
            return True
        if mahook[:5] != bytes.fromhex("8B 0E 85 C9 74"):
            self._inlog(f"[CHẶN CRASH] chỗ đọc cờ nhiệm vụ NPC không như dự kiến: {mahook.hex(' ')}")
            return False
        diachiboqua = diachihook + 6 + struct.unpack("<b", mahook[5:6])[0]
        asm_script = f"""
            mov ecx, dword ptr [esi]
            test ecx, ecx
            je boqua
            cmp ecx, 0x7FFF
            ja boqua
            push {diachihook + 6}
            ret
        boqua:
            push {diachiboqua}
            ret
        """
        encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
        if not encoding:
            return False
        kichban = self.tientrinh.allocate(64)
        write_bytes(self.tientrinh, kichban, bytes(encoding), len(encoding))
        write_bytes(self.tientrinh, diachihook, b"\xE9" + struct.pack("<i", kichban - (diachihook + 5)) + b"\x90", 6)
        self._inlog("[CHẶN CRASH] đã vá chỗ đọc cờ dấu nhiệm vụ NPC (bỏ số cờ rác)")
        return True

    def action_thietlaphookvehieuungdat(self):
        # Chặn crash engine.dll + 0x424D (Thỏ 342 ngày 10/11 lúc 00:13:37, dump đầy đủ XQ.exe.1002140.dmp; Ngốc 347 ngày 09/11 lúc 01:39).
        # Danh sách hiệu ứng mặt đất (đầu ở [xq + 0x376CA4], nút 0x2C: +0 sprite, +8 bộ đếm khung, +0xC tốc độ, +0x10/+0x14 ô),
        # ví dụ trận pháp Vân Mộng Cốc (Kỳ Môn Trận, Độn Giáp Trận). Hàm vẽ có 2 vòng (xq+0x4F83A, xq+0x4FE8E) lấy khung
        # [sprite + 0x1C] + chỉ số * 8 rồi gọi vẽ mà không kiểm tra; lúc văng, sprite có 26 khung nhưng [+0x1C] = 0 (chưa nạp / đã nhả)
        # => engine đọc vtable ở địa chỉ 0x50. Đường vẽ đối tượng (xq+0x15134) thì có kiểm tra khung NULL rồi bỏ qua.
        # Vá: sprite hoặc mảng khung NULL thì bỏ lời gọi vẽ (2 push + call thiscall ret 8 => ngăn xếp cân), vẫn tăng bộ đếm như thường.
        # Kịch bản không giải phóng (game còn nhảy vào sau khi bot tắt); lần chạy sau thấy đã vá thì thôi.
        # Kng 359 ngày 13/11 lúc 21:24:39 vẫn văng engine+0x424D dù đã vá (dump C:\CrashDumps\XQ.exe.1874180.dmp, gọi từ xq+0x4F852).
        # Nút ở ô (113,149), cạnh Trận Lạc Ảnh của người chơi đang đánh Thk; sprite đã bị nhả HẲN, vùng nhớ bị ghi đè rác:
        # [sprite] = 0x69D659D8, [sprite+0x1C] = 0x8D775C59 (không phải NULL nên lọt qua bản vá cũ).
        # Sprite còn lành có [sprite] = vtable xq+0x18A580 (nằm trong ảnh xq.exe). Vì vậy kiểm tra thêm: vtable phải nằm trong
        # [xq, xq + 0x400000) và mảng khung phải trong [0x10000, 0x80000000).
        # Bổ sung 2026-11-14: gốc crash là bộ đệm sprite hiệu ứng 100 ô (mã [MAHIEUUNGDAT+i*4], sprite [BANGSPRITEHIEUUNG+4+i*4]) xoay vòng
        # nhả sprite cũ trong khi nút đất còn trỏ tới. Nút đất không gắn đối tượng (+4 = 0) mà sprite không còn trong bộ đệm => đã bị nhả,
        # bỏ vẽ. Sprite còn trong bộ đệm thì tra mã; mã thuộc MAHIEUUNGDATKHONGVE (Độn Giáp Trận, người dùng chấp nhận không thấy để khỏi dis)
        # cũng bỏ vẽ. Bot vẫn đọc trận từ danh sách nút nên né trận / chọn tâm không ảnh hưởng.
        # Bản vá cũ đã nằm trong game (lần chạy trước) mà khác kịch bản mới thì trỏ lại lệnh nhảy sang kịch bản mới.
        # (tên hằng, mã gốc, số byte ghi đè, chỗ tiếp sau lệnh gọi vẽ tính từ chỗ hook, lệnh gốc chạy lại)
        dsvongve = [
            ("HOOK_VEHIEUUNGDAT1", "8B 16 89 4C 24 10", 6, 0x18, "mov dword ptr [esp + 0x10], ecx"),
            ("HOOK_VEHIEUUNGDAT2", "8B 16 33 FF 89 4C 24 10", 8, 0x19, "xor edi, edi\n            mov dword ptr [esp + 0x10], ecx"),
        ]
        diachima = self.diachixq + DC.MAHIEUUNGDAT
        diachibangsprite = self.diachixq + DC.BANGSPRITEHIEUUNG + 4
        sosanhma = "\n".join(f"            cmp eax, {ma}\n            je boqua2" for ma in MAHIEUUNGDATKHONGVE)
        cotranphap = self._get_diachicohienthi() + COHIENTHI_VITRI["tranphap"]
        ketqua = True
        for tenhang, magoc, sobyte, dotiep, lenhgoc in dsvongve:
            diachihook = self.diachixq + getattr(DC, tenhang)
            try:
                mahook = read_bytes(self.tientrinh, diachihook, sobyte)
            except Exception:
                ketqua = False
                continue
            if mahook[0] != 0xE9 and mahook != bytes.fromhex(magoc):
                self._inlog(f"[CHẶN CRASH] chỗ vẽ hiệu ứng mặt đất {tenhang} không như dự kiến: {mahook.hex(' ')}")
                ketqua = False
                continue
            asm_script = f"""
            mov edx, dword ptr [esi]
            {lenhgoc}
            cmp edx, 0x10000
            jb boqua
            push eax
            push ecx
            cmp dword ptr [esi + 4], 0
            jne kiemtrasprite
            xor ecx, ecx
        timsprite:
            cmp edx, dword ptr [ecx * 4 + {diachibangsprite}]
            je thaysprite
            inc ecx
            cmp ecx, {self.SOOBODEMHIEUUNG}
            jb timsprite
            jmp boqua2
        thaysprite:
            cmp byte ptr [{cotranphap}], 0
            je kiemtrasprite
            mov eax, dword ptr [ecx * 4 + {diachima}]
{sosanhma}
        kiemtrasprite:
            mov eax, dword ptr [edx]
            sub eax, {self.diachixq}
            cmp eax, 0x400000
            jae boqua2
            mov eax, dword ptr [edx + 0x1C]
            cmp eax, 0x10000
            jb boqua2
            cmp eax, 0x80000000
            jae boqua2
            pop ecx
            pop eax
            push {diachihook + sobyte}
            ret
        boqua2:
            pop ecx
            pop eax
        boqua:
            push {diachihook + dotiep}
            ret
            """
            encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
            if not encoding:
                ketqua = False
                continue
            encoding = bytes(encoding)
            if mahook[0] == 0xE9:
                # Đã vá từ lần chạy trước: giống kịch bản mới thì thôi, khác thì chỉ ghi lại 4 byte đích nhảy
                kichbancu = diachihook + 5 + struct.unpack("<i", mahook[1:5])[0]
                try:
                    if read_bytes(self.tientrinh, kichbancu, len(encoding)) == encoding:
                        continue
                except Exception:
                    pass
            kichban = self.tientrinh.allocate(256)
            write_bytes(self.tientrinh, kichban, encoding, len(encoding))
            if mahook[0] == 0xE9:
                write_bytes(self.tientrinh, diachihook + 1, struct.pack("<i", kichban - (diachihook + 5)), 4)
            else:
                mavanew = b"\xE9" + struct.pack("<i", kichban - (diachihook + 5)) + b"\x90" * (sobyte - 5)
                write_bytes(self.tientrinh, diachihook, mavanew, sobyte)
        if ketqua:
            self._inlog("[CHẶN CRASH] đã vá chỗ vẽ hiệu ứng mặt đất (bỏ sprite đã nhả, ẩn trận theo cờ hiển thị)")
        return ketqua

    def action_thietlaphookvetilenen(self):
        # Chặn crash engine.dll + 0x424D trên LUỒNG NỀN của game (Thk 354 ngày 11/11 lúc 01:55:19, dump trong thư mục game
        # xq.exe.2026-11-11.01.55.19.dmp; ~10 phút sau khi đăng nhập lại vì dis, đang đi bộ ở Tề Quốc).
        # Game tự tạo luồng (xq+0x99591, hàm luồng xq+0x99EB0) vẽ trước nền đất quanh nhân vật vào 2 bộ đệm luân phiên
        # ([THONGTINGAME]+0xAEBF48), gọi xq+0x53100. Hàm lấy khung tile xq+0xCE620 trả [sprite + 0x1C] + chỉ số * 8 mà không kiểm tra
        # (nạp xong thấy [+0x1C] = 0 chỉ báo lỗi rồi chạy tiếp) => lúc văng trả về 8, engine đọc vtable ở 8.
        # Luồng nền đọc tile trong lúc luồng chính nạp / nhả => tranh chấp của chính game, bot không gọi tới.
        # Hàm lấy khung tile chỉ có 2 chỗ gọi: xq+0x535BA (luồng nền) và xq+0x9BAF9. Vá ngay sau lời gọi: khung < 0x10000 hoặc
        # vtable = 0 thì bỏ lời gọi vẽ "push eax; call [edx+0x30]" (chưa push nên ngăn xếp cân), mất 1 ô nền trong 1 khung hình.
        # Kịch bản không giải phóng; lần chạy sau thấy đã vá (E9) thì thôi.
        # (tên hằng, mã gốc, số byte ghi đè, chỗ tiếp sau lệnh gọi vẽ tính từ chỗ hook, lệnh gốc chạy lại)
        dschove = [
            ("HOOK_VETILENEN1", "8B 54 24 2C 8B 4C 24 14", 8, 0xC, "mov edx, dword ptr [esp + 0x2C]\n            mov ecx, dword ptr [esp + 0x14]"),
            ("HOOK_VETILENEN2", "8B 54 24 30 50", 5, 0xA, "mov edx, dword ptr [esp + 0x30]\n            push eax"),
        ]
        ketqua = True
        for tenhang, magoc, sobyte, dotiep, lenhgoc in dschove:
            diachihook = self.diachixq + getattr(DC, tenhang)
            try:
                mahook = read_bytes(self.tientrinh, diachihook, sobyte)
            except Exception:
                ketqua = False
                continue
            if mahook[0] == 0xE9:
                continue
            if mahook != bytes.fromhex(magoc):
                self._inlog(f"[CHẶN CRASH] chỗ vẽ tile nền {tenhang} không như dự kiến: {mahook.hex(' ')}")
                ketqua = False
                continue
            asm_script = f"""
            cmp eax, 0x10000
            jb boqua
            cmp dword ptr [eax], 0
            je boqua
            {lenhgoc}
            push {diachihook + sobyte}
            ret
        boqua:
            push {diachihook + dotiep}
            ret
            """
            encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
            if not encoding:
                ketqua = False
                continue
            kichban = self.tientrinh.allocate(64)
            write_bytes(self.tientrinh, kichban, bytes(encoding), len(encoding))
            mavanew = b"\xE9" + struct.pack("<i", kichban - (diachihook + 5)) + b"\x90" * (sobyte - 5)
            write_bytes(self.tientrinh, diachihook, mavanew, sobyte)
        if ketqua:
            self._inlog("[CHẶN CRASH] đã vá chỗ vẽ tile nền (bỏ qua khung tile NULL)")
        return ketqua

    def action_thietlaphookvecuaso(self):
        # Chặn crash xq+0x4B2B0 (Kng 359 ngày 13/11 lúc 00:29:35, dump C:\CrashDumps\XQ.exe.910616.dmp; 2s sau "tallk 17ba# welcome.301"
        # phù Tân Thủ Tiên Cô ở Vô Định Hà 1). Vòng vẽ cửa sổ giao diện duyệt mảng con trỏ [THONGTINGAME]+0xADFC78 (số lượng +0xADFD40),
        # gọi vẽ từng cửa sổ (xq+0x17D640) rồi đọc lại [esi] để vẽ chú thích. Cửa sổ hội thoại NPC tự đóng ngay trong lời gọi vẽ (mảng
        # dồn lại: lúc văng số lượng còn 4, ô thứ 5 = 0) => đọc [0 + 0x1C], văng game. Lỗi của chính client, bot không ghi vào mảng này.
        # Vá chỗ "mov eax, [esi]; cmp [eax+0x1C], edi" (5 byte) sau lời gọi vẽ: ô đã NULL thì nhảy tới cuối thân vòng (HOOK + 0x45,
        # tăng đếm rồi so lại với số lượng mới) như nhánh "không vẽ chú thích" của game. Kịch bản không giải phóng; thấy E9 thì thôi.
        diachihook = self.diachixq + DC.HOOK_VECUASO
        try:
            mahook = read_bytes(self.tientrinh, diachihook, 7)
        except Exception:
            return False
        if mahook[0] == 0xE9:
            return True
        if mahook != bytes.fromhex("8B 06 39 78 1C 7E 3E"):
            self._inlog(f"[CHẶN CRASH] chỗ vẽ cửa sổ không như dự kiến: {mahook.hex(' ')}")
            return False
        asm_script = f"""
            mov eax, dword ptr [esi]
            test eax, eax
            je boqua
            cmp dword ptr [eax + 0x1C], edi
            push {diachihook + 5}
            ret
        boqua:
            push {diachihook + 0x45}
            ret
        """
        encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
        if not encoding:
            return False
        kichban = self.tientrinh.allocate(64)
        write_bytes(self.tientrinh, kichban, bytes(encoding), len(encoding))
        write_bytes(self.tientrinh, diachihook, b"\xE9" + struct.pack("<i", kichban - (diachihook + 5)), 5)
        self._inlog("[CHẶN CRASH] đã vá chỗ vẽ cửa sổ (bỏ qua cửa sổ vừa tự đóng)")
        return True

    def action_thietlaphookvedoituong(self):
        # Ẩn phân thân chiêu (Ngự Kiếm Phi Tiên...): đầu hàm vẽ 1 đối tượng xq+0x14200 (thiscall, ecx = đối tượng, ret 8; chính hàm này có
        # nhánh thoát sớm tương tự ở 0x414233). Cờ "phanthan" bật và lớp +0x29 = LOPDOITUONG_PHANTHAN thì ret 8 luôn, không vẽ gì.
        # Lệnh gốc ghi đè: mov eax, fs:[0] (6 byte)
        hook = self.diachixq + DC.HOOK_VEDOITUONG
        cophanthan = self._get_diachicohienthi() + COHIENTHI_VITRI["phanthan"]
        asm = f"""
            cmp byte ptr [{cophanthan}], 0
            je ve
            cmp ecx, 0x10000
            jb ve
            cmp byte ptr [ecx + 0x29], {LOPDOITUONG_PHANTHAN}
            jne ve
            ret 8
        ve:
            mov eax, dword ptr fs:[0]
            push {hook + 6}
            ret
        """
        ok = self._vahook("HOOK_VEDOITUONG", "64 A1 00 00 00 00", asm, "ẨN PHÂN THÂN")
        if ok:
            self._inlog("[ẨN PHÂN THÂN] đã vá đầu hàm vẽ đối tượng (bỏ đối tượng lớp 0x40 theo cờ hiển thị)")
        return ok

    def _get_diachicohienthi(self):
        # Khối 16 byte trong game, mỗi cờ 1 byte (COHIENTHI_VITRI), khác 0 = ẩn. Cấp 1 lần mỗi lần bot chạy (không giải phóng: kịch bản
        # hook còn đọc sau khi bot tắt); hook của lần chạy trước khác kịch bản mới nên được trỏ lại sang khối mới
        if not self._diachicohienthi:
            self._diachicohienthi = self.tientrinh.allocate(16)
            for ten, vitri in COHIENTHI_VITRI.items():
                write_bytes(self.tientrinh, self._diachicohienthi + vitri, bytes([1 if COHIENTHI_MACDINH[ten] else 0]), 1)
        return self._diachicohienthi

    def set_cohienthi(self, ten, is_an):
        # Bật / tắt 1 cờ ẩn hiển thị, có tác dụng ngay ở khung hình sau
        if ten in COHIENTHI_VITRI:
            write_bytes(self.tientrinh, self._get_diachicohienthi() + COHIENTHI_VITRI[ten], bytes([1 if is_an else 0]), 1)

    def _vahook(self, tenhang, magoc, asm_script, tenlog):
        # Vá 1 chỗ bằng jmp sang kịch bản (không giải phóng). Đã vá từ lần chạy trước: giống kịch bản mới thì thôi, khác thì trỏ lại.
        # magoc: byte gốc ở chỗ vá (số byte ghi đè = len, >= 5). -> True khi vá xong / đã đúng
        diachihook = self.diachixq + getattr(DC, tenhang)
        magoc = bytes.fromhex(magoc)
        try:
            mahook = read_bytes(self.tientrinh, diachihook, len(magoc))
        except Exception:
            return False
        if mahook[0] != 0xE9 and mahook != magoc:
            self._inlog(f"[{tenlog}] chỗ vá {tenhang} không như dự kiến: {mahook.hex(' ')}")
            return False
        encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
        if not encoding:
            return False
        encoding = bytes(encoding)
        if mahook[0] == 0xE9:
            kichbancu = diachihook + 5 + struct.unpack("<i", mahook[1:5])[0]
            try:
                if read_bytes(self.tientrinh, kichbancu, len(encoding)) == encoding:
                    return True
            except Exception:
                pass
        kichban = self.tientrinh.allocate(256)
        write_bytes(self.tientrinh, kichban, encoding, len(encoding))
        if mahook[0] == 0xE9:
            write_bytes(self.tientrinh, diachihook + 1, struct.pack("<i", kichban - (diachihook + 5)), 4)
        else:
            mavanew = b"\xE9" + struct.pack("<i", kichban - (diachihook + 5)) + b"\x90" * (len(magoc) - 5)
            write_bytes(self.tientrinh, diachihook, mavanew, len(magoc))
        return True

    def action_thietlaphookvehieuungnhanvat(self):
        # Hiệu ứng chiêu vẽ trên người (tia sét Lôi Động Cửu Thiên từ đầu xuống chân, vòng sáng trúng chiêu...): hàm vẽ đối tượng
        # (xq+0x14FEC..0x151C8) lặp 10 lớp ở đối tượng +0x12A0 (chỉ số sprite trong bộ đệm hiệu ứng 100 ô BANGSPRITEHIEUUNG), +0x12C8
        # bộ đếm khung, +0x1318 tốc độ, +0x1340 = 2 đang bật; lớp có sprite = hiệu ứng 9003 vẽ riêng sau vòng (xq+0x15194).
        # Bộ đệm đó xoay vòng nhả sprite cũ (gốc crash engine.dll+0x424D, xem action_thietlaphookvehieuungdat), và chỗ vẽ lớp riêng đọc
        # lại [sprite+0x1C] ở xq+0x151B5 mà không kiểm tra: crash 2026-11-07 / 347 ngày 09/11 ở xq+0x151BE. Người dùng báo 2026-11-14 dis
        # chủ yếu lúc PK (bị dính nhiều hiệu ứng chiêu), không cần xem hiệu ứng => bỏ vẽ.
        #  - Vòng 10 lớp (HOOK_VELOPHIEUUNGNV, chỗ tra sprite "mov eax,[eax*4+bảng]"): cờ "hieuungnhanvat" bật thì nhảy thẳng tới cuối thân
        #    vòng (+0xAC) như nhánh "sprite NULL" của game. Bộ đếm khung do chỗ khác tăng nên hiệu ứng vẫn hết hạn như thường.
        #  - Lớp riêng 9003 (HOOK_VELOPDACBIETNV, chưa rõ là gì, có thể là dấu chọn): vẫn vẽ, nhưng sprite hỏng (vtable ngoài xq.exe /
        #    mảng khung ngoài [0x10000, 0x80000000)) thì bỏ (+0x2D, chưa push gì nên ngăn xếp cân).
        bang = self.diachixq + DC.BANGSPRITEHIEUUNG
        hook1 = self.diachixq + DC.HOOK_VELOPHIEUUNGNV
        cohieuung = self._get_diachicohienthi() + COHIENTHI_VITRI["hieuungnhanvat"]
        diachima = self.diachixq + DC.MAHIEUUNGDAT

        def taoasmlop(hook, dobo):
            # eax = chỉ số sprite của lớp (1..100, ô i ứng với mã [MAHIEUUNGDAT + (i-1)*4]). Cờ bật: lớp có mã trong
            # MAHIEUUNGNHANVATGIULAI (hiệu ứng pháp bảo dưới chân...) vẫn vẽ, còn lại nhảy tới cuối thân vòng (hook + dobo).
            # ecx sau chỗ vá bị ghi đè ngay ("mov ecx,[eax+0x1C]") nhưng vẫn push / pop cho chắc
            giulai = "\n".join(f"            cmp ecx, {ma}\n            je giu" for ma in MAHIEUUNGNHANVATGIULAI)
            return f"""
            cmp byte ptr [{cohieuung}], 0
            je ve
            cmp eax, 1
            jb boqua
            cmp eax, 100
            ja boqua
            push ecx
            mov ecx, dword ptr [eax * 4 + {diachima - 4}]
{giulai}
            pop ecx
        boqua:
            push {hook + dobo}
            ret
        giu:
            pop ecx
        ve:
            mov eax, dword ptr [eax * 4 + {bang}]
            push {hook + 7}
            ret
            """

        ok1 = self._vahook("HOOK_VELOPHIEUUNGNV", "8B 04 85" + struct.pack("<I", bang).hex(), taoasmlop(hook1, 0xAC), "CHẶN CRASH")
        # Vòng lớp thứ 2 (xq+0x1575A..0x1581C, vẽ sau thân những lớp có +0x1368 <= 1; vòng 1 chỉ vẽ lớp +0x1368 >= 2): cùng cờ, bỏ lớp
        # -> cuối thân vòng (+0x94)
        hook3 = self.diachixq + DC.HOOK_VELOPHIEUUNGNV2
        ok1 = self._vahook("HOOK_VELOPHIEUUNGNV2", "8B 04 85" + struct.pack("<I", bang).hex(), taoasmlop(hook3, 0x94), "CHẶN CRASH") and ok1
        hook2 = self.diachixq + DC.HOOK_VELOPDACBIETNV
        asm2 = f"""
            mov edx, dword ptr [esi + ebp * 4 + 0x12A0]
            push eax
            push ecx
            mov ecx, dword ptr [edx * 4 + {bang}]
            cmp ecx, 0x10000
            jb boqua
            mov eax, dword ptr [ecx]
            sub eax, {self.diachixq}
            cmp eax, 0x400000
            jae boqua
            mov eax, dword ptr [ecx + 0x1C]
            cmp eax, 0x10000
            jb boqua
            cmp eax, 0x80000000
            jae boqua
            pop ecx
            pop eax
            push {hook2 + 7}
            ret
        boqua:
            pop ecx
            pop eax
            push {hook2 + 0x2D}
            ret
        """
        ok2 = self._vahook("HOOK_VELOPDACBIETNV", "8B 94 AE A0 12 00 00", asm2, "CHẶN CRASH")
        if ok1 and ok2:
            self._inlog("[CHẶN CRASH] đã vá chỗ vẽ hiệu ứng trên người (ẩn theo cờ hiển thị, kiểm tra sprite lớp riêng)")
        return ok1 and ok2

    # Hàm vẽ sprite nén RLE theo bảng màu trong engine.dll (stdcall 2 tham số, ret 8; tham số 2 = nút vẽ
    # [+0 x, +4 y, +8 rộng, +0xC cao, +0x10 bảng con trỏ hàng, +0x14 bảng màu]) và 17 byte đầu để đối chiếu trước khi vá
    ENGINE_HAMVERLE = 0x1F3C0
    ENGINE_HAMVERLE_MAGOC = "55 53 56 57 8B 54 24 14 8B 5C 24 18 8B 02 8B 4B 08"

    def action_thietlaphookverle(self):
        # Chặn crash engine.dll + 0x1F5A4 (đã 4 lần: 10/11 08:30, 10/11 18:59, Kng 359 12/11 01:40, Thk 354 13/11 21:07:33,
        # dump C:\CrashDumps\XQ.exe.47860.dmp). Hàm vẽ RLE engine+0x1F3C0 lấy con trỏ từng hàng ảnh esi = [bảng hàng + hàng*4].
        # Ba lần esi = 0x2C3225C3 cùng một sprite: nút vẽ ghi 30x37 nhưng bảng hàng chỉ có 36 ô (hàng 0 trỏ đúng bảng + 36*4),
        # hàng thứ 37 đọc 4 byte RLE đầu "C3 25 32 2C" làm con trỏ => văng. Trong cùng danh sách vẽ có nút dùng chung bảng đó ghi 28x36
        # (kích thước thật) => game ghép w/h của khung khác, lỗi của chính client. Lần 18:59 bảng hàng đã bị nhả (hàng 0 trỏ rác).
        # Vá ở đầu hàm: số hàng thật = ([bảng] - bảng) / 4; bảng NULL, hàng 0 trỏ ngược hoặc quá 4096 hàng thì bỏ vẽ (ret 8);
        # cao > số hàng thật thì kẹp cao lại. Mất tối đa 1 hàng / 1 hình trong 1 khung hình. Kịch bản không giải phóng.
        # Siết 2026-11-14: bảng hàng đã bị nhả hẳn (lần 10/11 18:59) thì [bảng] có thể vẫn lọt kiểm tra trên mà các hàng là rác.
        # Dữ liệu RLE các hàng nằm liền nhau tăng dần sau bảng => con trỏ hàng cuối phải >= hàng 0 và cách không quá 2MB, sai thì bỏ vẽ.
        # Bản vá cũ (lần chạy trước) khác kịch bản mới thì trỏ lại lệnh nhảy sang kịch bản mới.
        try:
            enginemodule = pymem.process.module_from_name(self.tientrinh.process_handle, "engine.dll")
        except Exception:
            enginemodule = None
        if not enginemodule:
            self._inlog("[CHẶN CRASH] không tìm thấy engine.dll, bỏ vá chỗ vẽ RLE")
            return False
        diachihook = enginemodule.lpBaseOfDll + self.ENGINE_HAMVERLE
        magoc = bytes.fromhex(self.ENGINE_HAMVERLE_MAGOC)
        try:
            mahook = read_bytes(self.tientrinh, diachihook, len(magoc))
        except Exception:
            return False
        if mahook[0] != 0xE9 and mahook != magoc:
            self._inlog(f"[CHẶN CRASH] chỗ vẽ RLE engine.dll không như dự kiến: {mahook.hex(' ')}")
            return False
        asm_script = f"""
            push eax
            push ecx
            mov ecx, dword ptr [esp + 0x10]
            mov eax, dword ptr [ecx + 0x10]
            cmp eax, 0x10000
            jb boqua
            push edx
            mov edx, dword ptr [eax]
            sub edx, eax
            jb boqua2
            shr edx, 2
            je boqua2
            cmp edx, 0x1000
            ja boqua2
            cmp dword ptr [ecx + 0xC], edx
            jle kiemtrahangcuoi
            mov dword ptr [ecx + 0xC], edx
        kiemtrahangcuoi:
            mov edx, dword ptr [ecx + 0xC]
            dec edx
            js duoc
            mov edx, dword ptr [eax + edx * 4]
            sub edx, dword ptr [eax]
            jb boqua2
            cmp edx, 0x200000
            ja boqua2
        duoc:
            pop edx
            pop ecx
            pop eax
            push ebp
            push ebx
            push esi
            push edi
            mov edx, dword ptr [esp + 0x14]
            push {diachihook + 8}
            ret
        boqua2:
            pop edx
        boqua:
            pop ecx
            pop eax
            ret 8
        """
        encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
        if not encoding:
            return False
        encoding = bytes(encoding)
        if mahook[0] == 0xE9:
            kichbancu = diachihook + 5 + struct.unpack("<i", mahook[1:5])[0]
            try:
                if read_bytes(self.tientrinh, kichbancu, len(encoding)) == encoding:
                    return True
            except Exception:
                pass
        kichban = self.tientrinh.allocate(256)
        write_bytes(self.tientrinh, kichban, encoding, len(encoding))
        if mahook[0] == 0xE9:
            write_bytes(self.tientrinh, diachihook + 1, struct.pack("<i", kichban - (diachihook + 5)), 4)
        else:
            write_bytes(self.tientrinh, diachihook, b"\xE9" + struct.pack("<i", kichban - (diachihook + 5)) + b"\x90" * 3, 8)
        self._inlog("[CHẶN CRASH] đã vá chỗ vẽ RLE engine.dll (kẹp số hàng, bỏ bảng hàng đã nhả)")
        return True

    def action_gohookhoatanhtancong(self):
        # Hook bỏ hoạt ảnh chiêu delay 0 (HOOK_HOATANHTANCONG, xq+0x1AE5B) đã GỠ 2026-11-12: người dùng thấy lâu lâu toạ độ đứng ở client
        # lệch so với máy chủ. Hàm này chỉ trả 6 byte gốc nếu client còn mang bản vá từ lần chạy bot cũ (lệnh nhảy E9 tới kịch bản)
        diachihook = self.diachixq + DC.HOOK_HOATANHTANCONG
        magoc = bytes.fromhex("8B 96 80 11 00 00")
        try:
            mahook = read_bytes(self.tientrinh, diachihook, 6)
            if mahook[0] == 0xE9:
                write_bytes(self.tientrinh, diachihook, magoc, 6)
                self._inlog("[BỎ HOẠT ẢNH] đã trả byte gốc (gỡ hook bỏ hoạt ảnh chiêu delay 0)")
        except Exception:
            return False
        return True

    def action_loglenhgame(self):
        # Log [LỆNH GAME] các lệnh hook bắt được mà bot không vừa gửi (bot gửi cũng đi qua hàm này)
        if not self._diachibodemlenhgame:
            return
        try:
            dulieu = read_bytes(self.tientrinh, self._diachibodemlenhgame, 4 + SOLUONGDONGLENHGAME * KICHTHUOCDONGLENHGAME)
        except Exception:
            return
        dem = struct.unpack_from("<I", dulieu, 0)[0]
        dadoc = self._demdonglenhgamedadoc
        if dem < dadoc:
            dadoc = 0
        dadoc = max(dadoc, dem - SOLUONGDONGLENHGAME)
        self._demdonglenhgamedadoc = dem
        thoidiemhientai = time.time()
        self._lenhbotganday = {k: v for k, v in self._lenhbotganday.items() if thoidiemhientai - v < 5.}
        for i in range(dadoc, dem):
            vitri = 4 + (i % SOLUONGDONGLENHGAME) * KICHTHUOCDONGLENHGAME
            o = dulieu[vitri:vitri + KICHTHUOCDONGLENHGAME]
            o = o[:o.find(b"\x00")] if b"\x00" in o else o
            caulenh = o.decode("utf-8", errors = "replace")
            khop = re.match(r"pawn\s+(?:[+\->]\s+)?([0-9a-fA-F]+#)", caulenh)
            if khop:
                self._makhoganday = khop.group(1).lower()
                self._thoidiemmakhoganday = thoidiemhientai
            if caulenh and caulenh.rstrip("\r\n") not in self._lenhbotganday:
                # "use <id>#": ghi kèm tên món trong túi (biết người chơi vừa dùng gì, vd Bảo Khố Di Động)
                khopuse = re.match(r"use2?\s+([0-9a-fA-F]+)#", caulenh)
                tenmon = ""
                if khopuse:
                    try:
                        soluongo = self.get_soluongvatphamhanhtrangtoida() + 1
                        ids = self._docdanhsachidvatphamhanhtrang(soluongo)
                        iddung = int(khopuse.group(1), 16)
                        if iddung in ids:
                            vitri = ids.index(iddung)
                            tenmon = f"  [món: {self.get_tenvatphamhanhtrang(vitri)} ô {vitri}]"
                    except Exception:
                        pass
                self._inlog(f"[LỆNH GAME] {caulenh}{tenmon}  (hex: {o.hex(' ')})")

    def get_makhoganday(self):
        # Mã kho ("7e#") client tự gửi trong lệnh pawn gần nhất, None nếu chưa bắt được (Niết Bàn không có hook lệnh game)
        return self._makhoganday

    def _docanhdaukho(self, kho):
        # Vùng đầu cấu trúc kho (cờ đang hiện ở +0x304) và vùng quanh rương đang mở / số rương / ô vừa thao tác (+0x1b180..+0x1b280)
        return read_bytes(self.tientrinh, kho, 0x400) + read_bytes(self.tientrinh, kho + 0x1b180, 0x100)

    def action_dokho(self):
        # Dò cách mở kho ngoài Quản Khố (Bảo Khố Di Động...): lúc cửa sổ kho vừa hiện thì log bản đồ / toạ độ, NPC quanh (tên, id),
        # vật phẩm tên có "Khố" trong túi, mã pawn client gửi gần nhất, và các ô 4 byte của cấu trúc kho đổi so với lúc kho đóng
        # (tìm chỗ game nhớ "kho mở bằng gì"). Lệnh client gửi khi dùng vật phẩm đã có [LỆNH GAME] ghi riêng
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        kho = read_int(self.tientrinh, x + DC.TG_KHO) if x else 0
        if not kho:
            return
        is_danghien = read_boolean(self.tientrinh, kho + DC.KHO_DANGHIEN)
        if not is_danghien:
            if self._is_khodanghientruoc or self._anhkhotruoc is None:
                self._anhkhotruoc = self._docanhdaukho(kho)
            self._is_khodanghientruoc = False
            return
        if self._is_khodanghientruoc:
            return
        self._is_khodanghientruoc = True
        try:
            anh = self._docanhdaukho(kho)
            phans = [f"bản đồ {self.get_idbandohientai()} toạ độ {self.get_toado()}",
                     f"rương mở {read_int(self.tientrinh, kho + DC.KHO_RUONGMO) + 1}/{read_int(self.tientrinh, kho + DC.KHO_SORUONG)}",
                     f"mã pawn gần nhất {self._makhoganday} ({round(time.time() - self._thoidiemmakhoganday, 1)}s trước)"
                     if self._makhoganday else "chưa bắt được lệnh pawn nào"]
            toadobanthan = self.get_toado()
            npcs = []
            i = 0
            while len(npcs) < 15:
                diachi = self.get_diachicosothongtindoituongx(i)
                if not diachi:
                    break
                i += 1
                if not self.get_is_nhanvattontai(diachi) or diachi == self.get_diachicosothongtinnhanvat1():
                    continue
                kc = math.dist(toadobanthan, self.get_toado(diachi))
                if kc <= 12:
                    npcs.append(f"{self.get_tendoituong(diachi)}={self.get_iddoituong(diachi):x}# ({round(kc, 1)} ô)")
            phans.append("quanh: " + (", ".join(npcs) or "không có ai"))
            soluongo = self.get_soluongvatphamhanhtrangtoida() + 1
            tens = self._docdanhsachtenvatphamhanhtrang(soluongo)
            ids = self._docdanhsachidvatphamhanhtrang(soluongo)
            khos = [f"{ten} id={iddt:x}# ô {vt}" for vt, (ten, iddt) in enumerate(zip(tens, ids)) if iddt and ten
                    and "khố" in unicodedata.normalize("NFC", re.sub(r'\x1b[a-zA-Z0-9]', '', ten)).lower()]
            phans.append("túi: " + (", ".join(khos) or "không có món tên có 'Khố'"))
            if self._anhkhotruoc and len(self._anhkhotruoc) == len(anh):
                doi = []
                for vt in range(0, len(anh), 4):
                    cu, moi = struct.unpack_from("<I", self._anhkhotruoc, vt)[0], struct.unpack_from("<I", anh, vt)[0]
                    if cu != moi:
                        doi.append(f"+{(vt if vt < 0x400 else 0x1b180 + vt - 0x400):x}: {cu:x}->{moi:x}")
                phans.append("ô kho đổi: " + (", ".join(doi[:60]) or "không"))
            self._inlog("[DÒ KHO] cửa sổ kho vừa mở | " + " | ".join(phans))
        except Exception as e:
            self._inlog(f"[DÒ KHO] lỗi khi dò: {e}")

    def action_suagiomaychu(self):
        # Nguyên nhân "khoá di chuyển oan" sau lag (dò 2026-11-06 trên Gạ 364): lệnh go client gửi kèm giờ máy chủ client ước, tính ở
        # xq + 0x95660 = time() + [TG + TG_GIOMAYCHU] - [TG + TG_GIOMAYMINH] (giờ máy chủ / giờ máy mình ở lần đồng bộ gần nhất). Lag thì gói
        # đồng bộ tới trễ nên giờ máy chủ bị ước lùi (Gạ lùi 37s rồi 43s, Thỏ 21s); máy chủ từ chối mọi lệnh go mang giờ cũ => client bước
        # rồi bị kéo về, vẫn đánh được. Phải chờ lần đồng bộ sau (~5 phút) mới hết: Gạ đồng bộ lại lúc 22:02:22 (lệch -43 -> 0) thì
        # 22:02:23 đi được ngay. Sửa: nhớ độ lệch lúc mạng tốt, độ lệch tụt >= NGUONGLUIGIOMAYCHULAGMANG giây thì ghi lại TG_GIOMAYCHU
        # cho đúng độ lệch cũ. Máy chủ đổi giờ thật (SOLANDONGBOTUTGIOMAYCHU lần đồng bộ liền nhau cùng tụt) thì nhận giờ mới.
        # Đọc thẳng bộ nhớ, không cần hook nên chạy cả Niết Bàn. -> True khi vừa sửa
        now = time.time()
        if now - self._thoidiemsuagiomaychu < 0.2:
            return False
        self._thoidiemsuagiomaychu = now
        thongtingame = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not thongtingame:
            return False
        giomaychu = read_int(self.tientrinh, thongtingame + DC.TG_GIOMAYCHU)
        giomayminh = read_int(self.tientrinh, thongtingame + DC.TG_GIOMAYMINH)
        if giomaychu <= 1e9 or giomayminh <= 1e9:
            return False
        dolech = giomaychu - giomayminh
        tot = self._dolechgiomaychutot
        is_dongbomoi = giomayminh != self._landongbogiomaychu
        self._landongbogiomaychu = giomayminh
        if tot is None or tot - dolech < NGUONGLUIGIOMAYCHULAGMANG:
            # Mạng tốt / giờ tiến lên: nhận làm độ lệch chuẩn
            self._dolechgiomaychutot = dolech
            self._solandongbotutgiomaychu = 0
            return False
        if is_dongbomoi:
            self._solandongbotutgiomaychu += 1
            if self._solandongbotutgiomaychu >= SOLANDONGBOTUTGIOMAYCHU:
                self._inlog(f"[LAG MẠNG] giờ máy chủ {self._solandongbotutgiomaychu} lần đồng bộ liền đều lệch {dolech}s (trước {tot}s): "
                            f"nhận là giờ thật của máy chủ, không sửa nữa")
                self._dolechgiomaychutot = dolech
                self._solandongbotutgiomaychu = 0
                return False
        write_int(self.tientrinh, thongtingame + DC.TG_GIOMAYCHU, giomayminh + tot)
        self._thoidiemvuasuagiomaychu = now
        self._inlog(f"[LAG MẠNG] giờ máy chủ của client tụt {tot - dolech}s (lệch {dolech}s, lúc mạng tốt {tot}s): máy chủ sẽ từ chối "
                    f"lệnh go mang giờ cũ (khoá di chuyển) => ghi lại giờ máy chủ cho đúng độ lệch {tot}s")
        return True

    def get_is_vuasuagiomaychu(self):
        # Vừa sửa giờ máy chủ sau lag chưa quá THOIGIANKHONGHOCVATCANSAULAG giây: lệnh go gửi trước lúc sửa mang giờ cũ nên bị kéo về,
        # không phải vật cản => _hockhongcatgoc không học (vatcanhoc.json dùng chung mọi cửa sổ, học nhầm thì kẹt lâu dài)
        return time.time() - self._thoidiemvuasuagiomaychu < THOIGIANKHONGHOCVATCANSAULAG

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

    def get_chisonhanvats(self, dichs):
        # Chỉ số nhân vật ở các ô KDK + dich (xem CHISONHANVAT_MAP), đọc 1 lần cả vùng. None khi chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x or not dichs:
            return None
        dau = min(dichs)
        dulieu = read_bytes(self.tientrinh, x + dau, max(dichs) - dau + 4)
        chisos = tuple(struct.unpack_from("<i", dulieu, dich - dau)[0] for dich in dichs)
        return chisos if any(chisos) else None

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

    def _doc_kimnguyenbaotumenu(self):
        # Số KNB trong lời thoại menu chọn tiền tệ đang giữ ("Kim Nguyên Bảo:  324", mã màu đã bỏ), None nếu menu khác
        khop = re.search(r"Kim Nguyên Bảo:\s*(\d+)", self.get_noidungcuasotuychon())
        return int(khop.group(1)) if khop else None

    def get_kimnguyenbao(self, is_molai = True, thoigiancho = 3., is_dongmenu = True):
        # Kim Nguyên Bảo còn lại, None nếu không đọc được. Số này chỉ có trong menu máy chủ gửi khi "buyitem" (xem TABTRANBAOKHOs):
        # is_molai xoá lời thoại cũ, gửi "buyitem" rồi chờ menu tới thoigiancho giây; không thì chỉ đọc menu đang giữ (có thể cũ).
        # is_dongmenu: đọc xong ẩn menu (không thì để mở cho action_muavatphamtranbaokho chọn tiếp)
        if not is_molai:
            return self._doc_kimnguyenbaotumenu()
        self.xoa_noidungcuasotuychon()
        if not self.action_thucthicaulenh2("buyitem", delay = 0., is_khancap = True):
            return None
        hethan = time.time() + thoigiancho
        knb = None
        while time.time() < hethan:
            knb = self._doc_kimnguyenbaotumenu()
            if knb is not None:
                break
            time.sleep(0.1)
        if is_dongmenu and knb is not None:
            self.set_is_danghiencuasotuychon(False)
        self._kimnguyenbao = knb if knb is not None else self._kimnguyenbao
        return knb

    def _quetbanghitranbaokho(self, vungs = None):
        # Bản ghi hàng Trân Bảo Khố trong bộ nhớ: {địa chỉ: (tab, ô, giá, tên)}. Máy chủ trả "buyitem <tab>" bằng 1 gói liệt kê CẢ tab,
        # mỗi món 1 bản ghi "45 03 <tab> <stt từ 1> <giá> <giá VIP> <giá ưu đãi> (3 int, đơn vị 0,1 KNB: 25 = 2 KNB 5 Ngân Bảo)
        # <6 byte> <tên đệm dấu cách> <mô tả>\0". Cửa sổ Trân Bảo Khố không chép danh sách ra chỗ riêng (dò 2026-11-13 trên Thỏ 342 đang mở
        # tab Chiến Đấu: tên món chỉ có trong các bản gói tin nằm rải trong heap, bị gói sau ghi đè dần) => quét heap.
        # vungs: [(đầu, cỡ)] chỉ quét các vùng này (vùng lần trước thấy bản ghi); None = quét mọi vùng nhớ riêng đọc/ghi (vài giây).
        # Ô dùng cho lệnh mua = stt - 1 (Rương Dự Trữ stt 8 tab 5 -> "buyitem 5 7 <n>", khớp log client)
        if vungs is None:
            vungs = []
            mbi = _MBI()
            diachi = 0
            while diachi < 0x7FFF0000 and _VirtualQueryEx(self.tientrinh.process_handle, diachi, ctypes.byref(mbi), ctypes.sizeof(mbi)):
                co = mbi.RegionSize or 0x1000
                if mbi.State == 0x1000 and mbi.Type == 0x20000 and mbi.Protect in (0x04, 0x40) and co <= 0x4000000:
                    vungs.append((diachi, co))
                diachi += co
        banghis = {}
        vungthays = []
        for dau, co in vungs:
            try:
                dulieu = read_bytes(self.tientrinh, dau, co)
            except Exception:
                continue
            cothay = False
            for khop in MAUBANGHITRANBAOKHO.finditer(dulieu):
                try:
                    ten = khop.group(5).decode("utf-8").strip()
                except UnicodeDecodeError:
                    continue
                gias = struct.unpack("<3i", khop.group(3))
                # Lọc rác trùng mẫu: tên phải in được, có chữ, giá hợp lý
                if not ten or not ten.isprintable() or not any(c.isalpha() for c in ten) or not 0 < gias[0] < 1000000:
                    continue
                banghis[dau + khop.start()] = (khop.group(1)[0], khop.group(2)[0] - 1, gias[0], ten)
                cothay = True
            if cothay:
                vungthays.append((dau, co))
        return banghis, vungthays

    def get_hangtranbaokho(self, tab, thoigiancho = 3.):
        # Hàng 1 tab Trân Bảo Khố đọc mới: gửi "buyitem <tab>" (cửa sổ phải đã mở bằng "buyitem paytype 1") rồi lấy các bản ghi của tab
        # vừa xuất hiện trong heap (so với trước khi gửi, bản cũ có thể từ lần mở trước). -> {tên: (ô, giá 0,1 KNB)}, {} nếu không đọc được.
        # Lần đầu quét cả bộ nhớ, sau đó chỉ quét vùng đã thấy bản ghi; vùng cũ không ra gì thì quét lại cả bộ nhớ 1 lần
        for is_quetca in ((False, True) if self._vungtranbaokho else (True, )):
            vungs = None if is_quetca else self._vungtranbaokho
            cu, _ = self._quetbanghitranbaokho(vungs)
            if not self.action_thucthicaulenh2(f"buyitem {tab}", delay = 0., is_khancap = True):
                return {}
            hethan = time.time() + thoigiancho
            hang = {}
            while time.time() < hethan:
                time.sleep(0.5)
                banghis, vungthays = self._quetbanghitranbaokho(vungs)
                moi = {dc: bh for dc, bh in banghis.items() if dc not in cu and bh[0] == tab}
                if moi:
                    # Gói tới đủ thì số món không đổi giữa 2 lần quét
                    if len(moi) == len(hang):
                        break
                    hang = moi
                    if vungthays:
                        self._vungtranbaokho = vungthays
            if hang:
                ketqua = {ten: (o, gia) for _, o, gia, ten in sorted(hang.values(), key = lambda bh: bh[1])}
                self._hangtranbaokho.update({ten: (tab, o, gia) for ten, (o, gia) in ketqua.items()})
                return ketqua
        self._inlog(f"[TRÂN BẢO KHỐ] không đọc được hàng tab {tab} (không thấy gói tin hàng sau \"buyitem {tab}\")")
        return {}

    def _timhangtranbaokho(self, tenvatpham):
        # (tab, ô, giá) của món ở Trân Bảo Khố, đọc mới từ máy chủ (không tin ô nhớ cũ, Trân Bảo Khố đổi thứ tự là mua nhầm): xem tab đã
        # thấy món lần trước trước, không có thì lần lượt các tab. Cửa sổ phải đã mở ("buyitem paytype 1"). None nếu không bán
        from nhiemvu_xq import is_trungtenvatpham
        tabtruoc = self._hangtranbaokho.get(tenvatpham, (None, ))[0]
        for tab in ([tabtruoc] if tabtruoc else []) + [t for t in TABTRANBAOKHOs if t != tabtruoc]:
            hang = self.get_hangtranbaokho(tab)
            for ten, (o, gia) in hang.items():
                if is_trungtenvatpham(tenvatpham, ten):
                    return tab, o, gia
        return None

    def _demvatphamtheoten(self, tenvatpham):
        # Tổng số món trong túi khớp tên (tên trong túi bị cắt 31 byte), None nếu không đọc được túi
        from nhiemvu_xq import is_trungtenvatpham
        soluongtheoten = self.get_soluongvatphamhanhtrangtheoten()
        if soluongtheoten is None:
            return None
        return sum(sl for ten, sl in soluongtheoten.items() if is_trungtenvatpham(ten, tenvatpham))

    def action_muavatphamtranbaokho(self, tenvatpham, soluong):
        # Mua soluong món (tên như trên Trân Bảo Khố) bằng Kim Nguyên Bảo, không cần đứng gần NPC. Làm như client: "buyitem" (đọc KNB) ->
        # "buyitem paytype 1" -> đọc hàng từng tab tìm ô của món (get_hangtranbaokho, không ghi cứng ô) -> mỗi lần tối đa
        # SOLUONGMUATRANBAOKHOTOIDA "buyitem <tab> <ô> <n>" + "zip 123". Không đủ KNB thì chỉ mua phần đủ tiền. Số mua được đếm bằng túi
        # trước / sau. Trả (số mua được, KNB còn): số mua được None nếu không kiểm được, 0 nếu không mua
        if soluong <= 0:
            return 0, None
        if self.is_nietban:
            # Quét heap tìm gói tin hàng: Niết Bàn không quét bộ nhớ (ChienQuocNietBan.dll), hàng và lệnh cũng chưa dò
            self._inlog(f"[TRÂN BẢO KHỐ] Niết Bàn chưa hỗ trợ mua tự động, bỏ mua {tenvatpham}")
            return 0, None
        knbtruoc = self.get_kimnguyenbao(is_dongmenu = False)
        if knbtruoc is None:
            self._inlog(f"[TRÂN BẢO KHỐ] không đọc được Kim Nguyên Bảo (menu chọn tiền tệ không về), bỏ mua {tenvatpham}")
            return None, None
        time.sleep(0.5)
        self.action_thucthicaulenh2("buyitem paytype 1", delay = 0., is_khancap = True)
        time.sleep(0.5)
        hang = self._timhangtranbaokho(tenvatpham)
        if not hang:
            self._inlog(f"[TRÂN BẢO KHỐ] không thấy \"{tenvatpham}\" ở tab nào của Trân Bảo Khố "
                        f"(đang bán: {', '.join(self._hangtranbaokho) or '?'})")
            return 0, knbtruoc
        tab, o, gia = hang
        # Giá đơn vị 0,1 KNB; chỉ tính phần KNB (Ngân Bảo lẻ không biết số dư)
        soluong = min(soluong, knbtruoc * 10 // gia) if gia > 0 else soluong
        if soluong <= 0:
            self._inlog(f"[TRÂN BẢO KHỐ] KNB {knbtruoc} không đủ mua {tenvatpham} (giá {gia / 10:g})")
            return 0, knbtruoc
        demtruoc = self._demvatphamtheoten(tenvatpham)
        conlai = soluong
        while conlai > 0:
            n = min(conlai, SOLUONGMUATRANBAOKHOTOIDA)
            time.sleep(0.5)
            self.action_thucthicaulenh2(f"buyitem {tab} {o} {n}", delay = 0., is_khancap = True)
            time.sleep(0.05)
            self.action_thucthicaulenh2(CAULENHXACNHANTRANBAOKHO, delay = 0., is_khancap = True)
            conlai -= n
        time.sleep(1.5)
        demsau = self._demvatphamtheoten(tenvatpham)
        damua = demsau - demtruoc if demtruoc is not None and demsau is not None else None
        knbsau = self.get_kimnguyenbao()
        self._inlog(f"[TRÂN BẢO KHỐ] mua {soluong} {tenvatpham} (tab {tab} ô {o}, giá {gia / 10:g}): KNB {knbtruoc} -> {knbsau}, "
                    f"túi {demtruoc} -> {demsau}, mua được {damua if damua is not None else '?'}")
        return damua, knbsau

    def get_danhsachdanhhieu(self):
        # Danh hiệu đang có (ô Danh Hiệu ở bảng Nhân Vật, chưa gồm "Ẩn danh hiệu"): [(mã dùng cho "title show <mã>", tên)], bỏ mục trùng mã
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return []
        danhsach = []
        for i in range(SODANHHIEUTOIDA):
            muc = read_bytes(self.tientrinh, x + DC.KDK_DANHSACHDANHHIEU + i * KICHTHUOCMUCDANHHIEU, KICHTHUOCMUCDANHHIEU)
            ma = muc[:6].split(b"\0")[0].decode("ascii", "ignore").strip()
            if not ma:
                # Mục trống có thể nằm giữa danh sách (đo 2026-11-03: TieuLyPhiDao mục 0 trống, danh hiệu ở mục 1-4): bỏ qua, đừng dừng
                continue
            ten = re.sub(r"\x1b.", "", muc[6:].split(b"\0")[0].decode("utf-8", "ignore")).strip()
            if ma not in (m for m, _ in danhsach):
                danhsach.append((ma, ten or ma))
        return danhsach

    def get_kinhnghiem(self):
        # Kinh nghiệm hiện có (chặn tăng cấp thì cứ cộng dồn, lên cấp thì bị trừ đi), None khi chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_KINHNGHIEM) if x else None

    def get_kinhnghiemcanlencap(self):
        # Kinh nghiệm cần để lên cấp kế (bảng Nhân Vật "521363 / 7347434" là số sau), ngay sau kinh nghiệm hiện có 0x28 byte
        # (đo 2026-11-01: cấp 84 cần 7347434, cấp 100 cần 21365653), None khi chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + DC.KDK_KINHNGHIEM + 0x28) if x else None

    def get_thuoctinhtiemnang(self):
        # 5 ô thuộc tính tiềm năng (bảng Nhân Vật, ô 4 = Nại lực) ở KDK+0x1518..0x1528, đo 2026-11-05; None khi chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return None
        giatris = [read_int(self.tientrinh, x + 0x1518 + 4 * i) for i in range(5)]
        return None if any(g is None or g is False for g in giatris) else giatris

    def get_diemtiemnangconlai(self):
        # Điểm tiềm năng chưa cộng KDK+0x1598 (acc gà = 4 × cấp), None khi chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_int(self.tientrinh, x + 0x1598) if x else None

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

    def get_tenbandogame(self):
        # Tên bản đồ game đang hiện (khối điều khiển +0x2C, chuỗi 20 byte nên tên dài bị cắt, vd "Phó Bản Phong Y"), "" nếu chưa đọc được
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        return read_string(self.tientrinh, x + 0x2C, 20) if x else ""

    def get_is_phobanmuonbando(self, tenbandogame = None):
        # Phó bản mượn ID bản đồ ngoài (Phong Yêu Kính, Tập Kích Môn Phái: TIENTOTENPHOBANMUONBANDOs), chỉ khác tên. None nếu chưa đọc được tên
        tenbandogame = self.get_tenbandogame() if tenbandogame is None else tenbandogame
        if not tenbandogame:
            return None
        tenbandogame = unicodedata.normalize("NFC", tenbandogame)
        idbando = self.get_idbandohientai()
        return (tenbandogame.startswith(TIENTOTENPHOBANMUONBANDOs) or self._is_tentapkich(tenbandogame, idbando)) and idbando not in BANDOPHOBANs

    def get_tenphobanmuonbando(self):
        # Đầu tên phó bản mượn ID bản đồ ngoài đang ở ("Phó Bản" / "Tập Kích Môn"), "" nếu ở bản đồ thật hoặc chưa đọc được tên.
        # Chia sẻ qua shared_data ("_phobanmuonbando") để cửa sổ khác phân biệt Phong Yêu Kính với bản đồ thật cùng ID
        tenbandogame = unicodedata.normalize("NFC", self.get_tenbandogame() or "")
        idbando = self.get_idbandohientai()
        if not tenbandogame or idbando in BANDOPHOBANs:
            return ""
        if self._is_tentapkich(tenbandogame, idbando):
            return TIENTOTENBANDOTAPKICHMONPHAI
        return next((tiento for tiento in TIENTOTENPHOBANMUONBANDOs if tenbandogame.startswith(tiento)), "")

    def get_is_cungbando(self, info, idbando = None):
        # Nhân vật cửa sổ khác (info trong shared_data) có đang cùng bản đồ với mình: cùng ID và cùng là / không là phó bản mượn ID
        # (Phong Yêu Kính mượn ID bản đồ thật, nhân vật ở hai nơi không thấy nhau). Cửa sổ chưa khởi động lại chưa có trường thì chỉ so ID
        idbando = self.get_idbandohientai() if idbando is None else idbando
        if not info or info.get("tenbando") != idbando:
            return False
        phobanmuon = self.get_tenphobanmuonbando()
        return info.get("_phobanmuonbando", phobanmuon) == phobanmuon

    def get_is_vuaroiphobanmuonbando(self):
        # Vừa ra khỏi phó bản mượn ID bản đồ ngoài: tên đổi trước, ID còn là ID mượn vài giây => tưởng đang ở bản đồ thật cùng ID (ra Phong
        # Yêu Kính về Chu Quốc mà tưởng ở Thanh Khê 1, theo sau / tìm đường Tín Vật về phái - QuanSuMuMuu 2026-11-04). True thì chờ
        if not self._thoidiemophobanmuonbando or self.get_is_phobanmuonbando():
            return False
        daqua = time.time() - self._thoidiemophobanmuonbando
        if self._idbandohientai == self._idbandophobanmuon:
            return daqua < THOIGIANCHOIDROIPHOBANMUON
        return time.time() - self._thoidiemthaydoibandogannhat < THOIGIANCHOSAUROIPHOBANMUON and daqua < THOIGIANCHOIDROIPHOBANMUON

    def get_is_bandophongyeu(self):
        # Phong Yêu Kính mượn ID 1 bản đồ ngẫu nhiên: chỉ nhận ra qua đầu tên bản đồ game
        tenbandogame = self.get_tenbandogame()
        return bool(tenbandogame) and unicodedata.normalize("NFC", tenbandogame).startswith(TIENTOTENBANDOPHONGYEU)

    def get_is_bandotapkichmonphai(self):
        # Tập Kích Môn Phái mượn ID 151 (Kênh Trịnh Quốc 1) nên chỉ nhận ra qua tên bản đồ game
        tenbandogame = self.get_tenbandogame()
        return bool(tenbandogame) and self._is_tentapkich(unicodedata.normalize("NFC", tenbandogame), self.get_idbandohientai())

    def get_is_dangophobandocbonho(self):
        # Đang ở phó bản (Lăng Ly Sơn, Thành Kiều, Bát Quái Trận..., hoặc phó bản mượn ID bản đồ ngoài như Phong Yêu Kính / Tập Kích),
        # đọc thẳng bộ nhớ, không dùng ID đệm của vòng lặp: dangnhap_xq gọi trên MoiTruong vừa dựng cho cửa sổ đang đơ
        idbando = self._get_idbandohientai()
        if idbando in BANDOPHOBANs:
            return True
        tenbandogame = unicodedata.normalize("NFC", self.get_tenbandogame() or "")
        return bool(tenbandogame) and (tenbandogame.startswith(TIENTOTENPHOBANMUONBANDOs) or self._is_tentapkich(tenbandogame, idbando))

    @staticmethod
    def _is_tentapkich(tenbandogame, idbando):
        # Aegis tên "Tập Kích Môn Ph..."; Niết Bàn tên khác (chưa biết) nhưng vẫn mượn ID 151: ở ID 151 mà tên không phải Kênh Trịnh Quốc
        # thì cũng là Tập Kích
        if tenbandogame.startswith(TIENTOTENBANDOTAPKICHMONPHAI):
            return True
        return idbando == BANDO_KENHTRINHQUOC1 and not tenbandogame.startswith(TIENTOTENBANDOKENHTRINHQUOC)

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

    def get_vitritruyna(self):
        # Vị trí đối thủ nhiệm vụ máy chủ trả khi dùng Công Văn Truy Nã (chấm vàng trên bản đồ): khối điều khiển + 0x334, mỗi ô 12 byte
        # (id đối tượng, x, y), ô trống id -1. Chỉ đổi khi dùng công văn, không tự cập nhật theo đối thủ (đo 2026-10-31). -> [(id, x, y)]
        x = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if not x:
            return []
        so = struct.unpack("<15i", read_bytes(self.tientrinh, x + 0x334, 60))
        return [(so[k], so[k + 1], so[k + 2]) for k in range(0, 15, 3) if so[k] > 0 and so[k + 1] > 0 and so[k + 2] > 0]

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
        # Con trỏ nhân vật của mình: mọi get_*() không truyền địa chỉ đều đọc lại nó (py-spy 2026-11-12 lần 3: ~9% CPU tiến trình bot).
        # Nhớ THOIGIANNHOCONTRONHANVAT giây, chỉ nhớ con trỏ khác 0 (đang đăng nhập / tải bản đồ thì đọc mới mỗi lần). Con trỏ chỉ đổi
        # khi chuyển bản đồ / đăng nhập lại; get_is_nhanvattontai() luôn đọc mới và xoá bản nhớ khi nhân vật không còn
        nho = self._contronhanvat_nho
        if nho[1] and time.monotonic() - nho[0] < THOIGIANNHOCONTRONHANVAT:
            return nho[1]
        return self._doccontronhanvat()

    def _doccontronhanvat(self):
        diachi = read_int(self.tientrinh, self.diachixq + DC.NHANVAT)
        self._contronhanvat_nho = (time.monotonic(), diachi)
        return diachi

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
        # Bỏ phần thông tin bot tự nối vào đuôi tên mục tiêu (danhhieumuctieu_xq)
        if ten and DAUNOITENMUCTIEU in ten:
            ten = ten.split(DAUNOITENMUCTIEU)[0].strip()
        if len(self._tendoituong_map) > 1024:
            self._tendoituong_map = {k: v for k, v in list(self._tendoituong_map.items()) if thoidiemhientai - v[0] < THOIGIANNHOTENDOITUONG}
        self._tendoituong_map[diachicosothongtinnhanvat] = (thoidiemhientai, ten)
        return ten

    def _get_diachidoituongxungquanhs(self, is_nguoichoi = False, is_baothukynangtrieuhoi = False):
        # Các đối tượng còn tồn tại trong tầm màn hình, lấy từ bản chụp dùng chung (_get_banchupdoituongxungquanh)
        toadobanthan, doituongs = self._get_banchupdoituongxungquanh()
        for diachi, x, y in doituongs:
            if math.dist(toadobanthan, (x, y)) > KHOANGCACHTOANMANHINH:
                continue
            if is_nguoichoi and not self.get_is_nguoichoi(diachi):
                continue
            if is_baothukynangtrieuhoi and not self.get_is_baothukynangtrieuhoi(diachi):
                continue
            yield diachi

    def get_diachinhanvattontais(self):
        # Mọi nhân vật / quái còn tồn tại trong bảng đối tượng (KHÔNG giới hạn khoảng cách), đúng tập mà vòng cũ "duyệt
        # get_diachicosothongtindoituongx(i) rồi lọc get_is_nhanvattontai" ra, nhưng lấy từ bản chụp dùng chung
        return tuple(diachi for diachi, _, _ in self._get_banchupdoituongxungquanh()[1])

    def _get_banchupdoituongxungquanh(self):
        # -> (toạ độ bản thân lúc chụp, tuple (địa chỉ, x, y) mọi nhân vật / quái còn tồn tại, theo thứ tự trong bảng đối tượng).
        # Nhớ THOIGIANNHODOITUONGXUNGQUANH giây, dùng chung mọi
        # luồng. py-spy 2026-11-12: ~40 chỗ (tìm mục tiêu, tầm nhìn chia sẻ, chủ nhân bảo thú, quét kẻ đánh, sư môn...) mỗi chỗ tự quét
        # lại cả bảng đối tượng, mỗi đối tượng 3-4 lần đọc bộ nhớ (id, loại, toạ độ) => đọc bộ nhớ là ~40% CPU tiến trình bot.
        # Giờ mỗi đối tượng 1 lần đọc 0xF4 byte (toạ độ +0x0, id +0x20, loại +0xF0). Đối tượng đọc lỗi (vừa bị huỷ) thì bỏ qua
        bayh = time.monotonic()
        nho = self._doituongxungquanh_nho
        if bayh - nho[0] < THOIGIANNHODOITUONGXUNGQUANH:
            return nho[1]
        toadobanthan = self.get_toado()
        try:
            bang = struct.unpack("<%di" % SOLUONGDOITUONGXUNGQUANHTOIDA,
                                 read_bytes(self.tientrinh, self.diachixq + DC.BANGDOITUONG, SOLUONGDOITUONGXUNGQUANHTOIDA * 4))
        except Exception:
            bang = ()
        diachis = []
        loainhanvats = (LOAIDOITUONG_NHANVAT1, LOAIDOITUONG_NHANVATKHAC1)
        for diachi in bang:
            if not diachi:
                break
            try:
                dulieu = read_bytes(self.tientrinh, diachi, 0xF4)
            except (pymem.exception.PymemError, pymem.exception.WinAPIError):
                continue
            x, y = struct.unpack_from("<ii", dulieu, 0)
            iddoituong, = struct.unpack_from("<i", dulieu, 0x20)
            idloai, = struct.unpack_from("<i", dulieu, 0xF0)
            if iddoituong <= 0 or idloai not in loainhanvats:
                continue
            diachis.append((diachi, x, y))
        ketqua = (toadobanthan, tuple(diachis))
        self._doituongxungquanh_nho = (bayh, ketqua)
        return ketqua

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

    def get_makhodangmo(self):
        # ID NPC kho của cửa sổ kho đang mở, dạng đứng sau "pawn" ("a6#"), None nếu kho không hiện. Đọc ở S + 0x310 (KHO_DANGHIEN + 0xC):
        # dò 2026-11-12 trên Gạ 364, dùng Bảo Khố Di Động ("use 108819#") thì ô này đổi ac -> a6 và client gửi "pawn a6# <rương>"; ac là
        # Quản Khố lần mở trước, a6 là ID NPC Bảo Khố ở Tề Quốc (người dùng xác nhận). Bảo Khố Di Động là hiệu ứng có hạn bỏ qua
        # khoảng cách tới NPC đó (hết hạn thì máy chủ báo xa Thủ Khố); NPC không đứng quanh nhân vật nên không tìm theo tên được
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        kho = read_int(self.tientrinh, x + DC.TG_KHO) if x else 0
        if not kho or not read_boolean(self.tientrinh, kho + DC.KHO_DANGHIEN):
            return None
        ma = read_int(self.tientrinh, kho + DC.KHO_DANGHIEN + 0xC)
        return f"{ma:x}#" if 0 < ma < 0x10000000 else None

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

    def get_motathovatphamhanhtrangcosan(self, idvitri):
        # Như get_motavatphamhanhtrangcosan nhưng giữ mã màu "\x1b<ký tự>" (read_string bỏ hết): mã đầu mô tả là màu tên món
        # (\x1bC Lam Kim, \x1bY vàng). "" nếu chưa nạp
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return ""
        return read_bytes(self.tientrinh, x + idvitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, 1024).split(b"\0")[0].decode("utf-8", "ignore")

    def truyvan_motavatphamhanhtrang(self, idvitri, is_cho = True):
        # is_cho = False: xoá mô tả cũ của ô rồi gửi desc, không ngủ (gửi desc nhiều ô một lượt, đọc lại sau bằng
        # get_motavatphamhanhtrangcosan)
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x:
            return False
        iddoituongvatphamhanhtrang = self.get_iddoituongvatphamhanhtrang(idvitri)
        if not iddoituongvatphamhanhtrang: return False
        if not is_cho:
            write_bytes(self.tientrinh, x + idvitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, b"\x00", 1)
            if idvitri >= VITRITRANGBIDAUTIEN:
                return self.action_thucthicaulenh("desc {}".format(idvitri - VITRITRANGBIDAUTIEN + 1))
            return self.action_thucthicaulenh("desc {}#".format(hex(iddoituongvatphamhanhtrang)).replace("0x", ""))
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
            dobens[vitri] = self.get_dobenmota(read_string(self.tientrinh, x + vitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, 1024))
        return dobens

    @staticmethod
    def get_dobenmota(mota):
        # (độ bền hiện tại, tối đa) từ dòng "Độ bền: 86 / 125" của mô tả; None nếu mô tả không có độ bền
        khop = re.search(r"bền\s*[:：]\s*(\d+)\s*/\s*(\d+)", unicodedata.normalize("NFC", mota or ""))
        return (int(khop.group(1)), int(khop.group(2))) if khop else None

    @staticmethod
    def get_khihuyetphapbaomota(mota):
        # (khí huyết hiện tại, tối đa) của pháp bảo từ dòng "Khí Huyết: 100 / 600" (Cửu Long Thần Hỏa Trảo); None nếu không có.
        # Dòng chỉ số "Khí Huyết: +200" không khớp vì không có "x / y"
        khop = re.search(r"Khí\s*Huyết\s*[:：]\s*(\d+)\s*/\s*(\d+)", unicodedata.normalize("NFC", mota or ""), re.IGNORECASE)
        return (int(khop.group(1)), int(khop.group(2))) if khop else None

    def action_truyvanmotatrangbi(self, vitri):
        # Xoá mô tả cũ của ô trang bị (độ bền trong đó không tự cập nhật) rồi "desc <ô>" độ ưu tiên thấp, không chờ:
        # máy chủ trả sau đó, đọc bằng get_motavatphamhanhtrangcosan
        x = self.get_diachicosothongtinvatphamhanhtrang()
        if not x or not self.get_iddoituongvatphamhanhtrang(vitri):
            return False
        write_bytes(self.tientrinh, x + vitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, b"\x00", 1)
        return self.action_thucthicaulenh("desc {}".format(vitri - VITRITRANGBIDAUTIEN + 1), douutien = DOUUTIEN_THAP)

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

    def get_hopxacnhannpc(self):
        # Hộp yes / no (TG_CUASOYESNO, khác cửa sổ xác nhận TG_CUASOXACNHAN) máy chủ gửi về: Thảo Nghịch Tướng Quân "Bạn sẽ sử dụng Hạt Mè
        # Khai Môn để tiến vào Thành Kiều", "Đội ngũ Thọ muốn cùng bạn kết thành nhóm...". 1 hộp dùng lại; + 0x34 đang hiện, + 0x7C lệnh
        # nút Xác Nhận (vd "tallk 15e6# welcome.4", "team g@+ 29"), + 0x176 lệnh nút Hủy Bỏ. Nút Xác Nhận của game (xq + 0x131960) gửi
        # lệnh + 0x7C rồi đóng hộp (vtable[1](0), xq + 0x131840: tắt + 0x34, gỡ khỏi danh sách cửa sổ, xoá lệnh). Hộp ẩn mà lệnh chưa xoá
        # (ẩn kiểu chỉ ghi + 0x34, vẫn kẹt trong danh sách cửa sổ) cũng coi là còn.
        # -> (địa chỉ hộp, lệnh Xác Nhận) khi hộp còn, không thì (0, "")
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        x = read_int(self.tientrinh, x + DC.TG_CUASOYESNO) if x else 0
        lenh = read_bytes(self.tientrinh, x + 0x7C, 0x80).split(b"\0")[0].decode("utf-8", "ignore").strip() if x else ""
        return (x, lenh) if lenh else (0, "")

    def action_donghopxacnhannpc(self):
        # Đóng hộp get_hopxacnhannpc như game tự đóng sau khi bấm nút, không gửi lệnh nào. Hộp đã đóng thì không làm gì
        if self.get_hopxacnhannpc()[0]:
            self._goivtableanhien(DC.TG_CUASOYESNO, False)

    def _get_diachivongquayso(self):
        # Cửa sổ vòng quay số Bảo Điển (TG_VONGQUAYSO, client tạo sẵn, vtable 0x590378): + 0x34 đang hiện, + 0xA0 đang quay, + 0xA2 hoạt
        # ảnh đã dừng ở món trúng, + 0xA3 còn đồ chờ cộng vào túi, + 0x9C số món chờ, món chờ từ + 0xAE (mỗi món 0x1F4 byte, + 0xBB tên món
        # đầu). Ẩn / hiện bằng vtable[1] như hộp yes / no (hiện lại thì xoá danh sách món chờ).
        # Gói "thêm vật phẩm" tới khi vòng quay đang hiện, chưa dừng (+ 0xA2 = 0) mà + 0xA3 = 1 thì client KHÔNG cộng vào túi ngay mà giữ ở
        # danh sách món chờ (xq + 0x1B58), tới khi hoạt ảnh (vẽ ở vtable[2]) quay tới món trúng mới cộng (xq + 0x11DB60) rồi tắt + 0xA3.
        # Đóng cửa sổ khi + 0xA3 còn 1 thì hoạt ảnh dừng, đồ máy chủ đã ghi nhận mà túi client không có (đầy túi lúc nào không biết)
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return read_int(self.tientrinh, x + DC.TG_VONGQUAYSO) if x else 0

    def get_vongquayso(self):
        # -> (đang hiện, tên món máy chủ trả về, còn đồ chờ cộng vào túi), chưa có cửa sổ thì (False, "", False)
        x = self._get_diachivongquayso()
        if not x:
            return False, "", False
        return (read_boolean(self.tientrinh, x + 0x34), read_bytes(self.tientrinh, x + 0xBB, 0x20).split(b"\0")[0].decode("utf-8", "ignore").strip(),
                read_boolean(self.tientrinh, x + 0xA3))

    def action_xoamonvongquayso(self):
        # Xoá tên món cũ trước khi quay, để biết máy chủ đã trả kết quả lượt mới (tên chỉ để hiện, không ảnh hưởng món nhận)
        x = self._get_diachivongquayso()
        if x:
            write_bytes(self.tientrinh, x + 0xBB, b"\0" * 0x20, 0x20)

    def action_dongvongquayso(self):
        self._goivtableanhien(DC.TG_VONGQUAYSO, False)

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
        try:
            toado = self.get_toado()
        except (pymem.exception.PymemError, pymem.exception.WinAPIError, struct.error):
            toado = None
        if idbandohientai != self._idbandohientai:
            self._thoidiemthaydoibandogannhat = time.time()
            # Toạ độ lượt trước (còn ở bản đồ cũ): mã bản đồ đổi trước, toạ độ có khi 2-3s sau mới đổi (get_is_toadochuaondinh)
            self._toadobandocu = self._toadolantruoc
            self._lucvaobando[idbandohientai] = time.time()
            # Vừa qua cổng mà đích tìm đường của client còn là cổng ở bản đồ cũ: client tự tìm đường quay lại cổng đó (bot đang chờ toạ
            # độ ổn định nên chưa đặt đích mới) => qua lại một cổng mãi. Huỷ đích đó ngay
            if self._idbandohientai and idbandohientai and self.get_bandotimduong() == self._idbandohientai:
                self.action_ngungtudongtimduong()
                self._inlog(f"[TÌM ĐƯỜNG] Đã sang bản đồ {idbandohientai}: huỷ đích tìm đường còn ở bản đồ cũ {self._idbandohientai}")
        self._idbandohientai = idbandohientai
        self._toadolantruoc = toado
        if idbandohientai and self.get_is_phobanmuonbando():
            self._thoidiemophobanmuonbando = time.time()
            self._idbandophobanmuon = idbandohientai

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
            # Tâm trận đọc được trên mặt đất (nút 21151 / 21152) thì dùng luôn, không thì đoán theo người dùng chiêu như cũ
            tamdat = self._timtamtrandolacanhtrendat()
            if tamdat:
                if tamdat != self._toadotrandolacanh:
                    self._inlog(f"[TRẬN ĐỒ] Dính Trận Pháp Lạc Ảnh tại {self.get_toado()}, tâm trận trên mặt đất {tamdat} (đoán trước đó {self._toadotrandolacanh})")
                    self._toadotrandolacanh = tamdat
            elif not self._toadotrandolacanh:
                self._toadotrandolacanh = self._timtamtrandolacanh()
        else:
            self._toadotrandolacanh = None

        if not self.get_is_dangbatchucnangmorong():
            self.thoidiemcochucnangmoronggannhat = time.time()

        for noidungtrochuyen in self._docdongtrochuyenmois():
            self._lichsutrochuyen5s.append((now, noidungtrochuyen))
            self._xulydongthongtinnguoichoi(noidungtrochuyen)
        for dongkhungchat in self._docdongkhungchatmois():
            self._xulydongtinmat(now, dongkhungchat)

        self._lichsutrochuyen5s = [msg for msg in self._lichsutrochuyen5s if now - msg[0] <= 5.0]

    def _xulydongtinmat(self, now, noidung):
        # Tin mật đến hiện ở khung trò chuyện "Gạ nói thầm với bạn : abc" (ảnh người dùng 2026-11-10); tên là liên kết có sẵn ID
        # (MAUTINMATDEN), không có liên kết thì ID tra sau ở get_tinmatdens
        m = MAUTINMATDEN.search(noidung)
        if not m:
            return
        ten = (m.group("ten") or m.group("tenthuong") or "").strip()
        idnguoigui = int(m.group("id")) if m.group("id") else None
        noidungtin = m.group("noidung").strip()
        self._tinmatdens = [t for t in self._tinmatdens if now - t["luc"] <= 300.] + [{"luc": now, "ten": ten, "noidung": noidungtin, "id": idnguoigui}]
        self._inlog(f"[TIN MẬT] {ten} (ID {idnguoigui}): {noidungtin}")

    def get_lienhetinmats(self):
        # Danh sách mật ngữ gần đây của client (bấm lên/xuống ở ô chat ra "/<tên>(<ID>) "): TG + TG_LIENHETINMAT, LIENHETINMAT_SOLUONG ô
        # x LIENHETINMAT_KICHTHUOC byte {tên 0x14 byte, ID int ở +0x14}, ô trống ID 0. Dò từ XQ.exe 0x43F110 ("/%s(%d)%s") và 0x425CA5
        # (gửi "/<tên>(<ID>)" kiểm tên khớp ID trong danh sách này). -> {tên: ID}
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return {}
        try:
            dulieu = read_bytes(self.tientrinh, x + TG_LIENHETINMAT, LIENHETINMAT_SOLUONG * LIENHETINMAT_KICHTHUOC)
        except Exception:
            return {}
        ketqua = {}
        for i in range(LIENHETINMAT_SOLUONG):
            o = dulieu[i * LIENHETINMAT_KICHTHUOC:(i + 1) * LIENHETINMAT_KICHTHUOC]
            idnguoichoi = struct.unpack_from("<i", o, 0x14)[0]
            ten = o[:0x14].split(b"\x00")[0].decode("utf-8", errors = "ignore").strip()
            if idnguoichoi > 0 and ten:
                ketqua[ten] = idnguoichoi
        return ketqua

    def get_tinmatdens(self):
        # Tin mật 5 phút gần nhất kèm ID người gửi: tra danh sách mật ngữ gần đây, rồi tên -> ID đã biết (desc user, người chơi quanh đây).
        # Chưa ra thì gửi "friend ? <tên>" (nút Dò tìm ở Thêm Bạn hữu) 1 lần / 30s để client có ID, log để dò chỗ đọc kết quả
        if not self._tinmatdens:
            return []
        now = time.time()
        lienhe = self.get_lienhetinmats()
        if lienhe != self._lienhetinmatcu:
            self._lienhetinmatcu = lienhe
            self._inlog(f"[TIN MẬT] Danh sách mật ngữ gần đây: {lienhe}")
        for tin in self._tinmatdens:
            if tin["id"] is None:
                tin["id"] = lienhe.get(tin["ten"]) or self._idnguoichoitheoten_map.get(tin["ten"])
                if tin["id"] is None and now - self._thoidiemdotimtens.get(tin["ten"], 0.) >= 30.:
                    self._thoidiemdotimtens[tin["ten"]] = now
                    self._inlog(f"[TIN MẬT] Chưa biết ID của {tin['ten']}, gửi Dò tìm")
                    self.action_thucthicaulenh2(f"friend ? {tin['ten']}", delay = 0., is_khancap = True)
                elif tin["id"] is not None:
                    self._inlog(f"[TIN MẬT] {tin['ten']} có ID {tin['id']}")
        return [dict(t) for t in self._tinmatdens]

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

    def _timtamtrandolacanhtrendat(self):
        # Trận Lạc Ảnh trên mặt đất gần mình nhất (đang bị giữ thì mình ở trong trận: cách tâm tối đa BANKINHTRANDOLACANH, nới thêm 2 ô
        # cho lệch toạ độ), None nếu không thấy
        toadobanthan = self.get_toado()
        tots = [(math.dist(toadobanthan, (tran["x"], tran["y"])), (tran["x"], tran["y"])) for tran in self.get_danhsachtranlacanh()]
        tots = [t for t in tots if t[0] <= BANKINHTRANDOLACANH + 2.]
        return min(tots)[1] if tots else None

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

    # Danh sách hiệu ứng mặt đất (dịch ngược xq+0x4935D0 và gói máy chủ xử lý ở xq+0x4A2E09). Gói: ô x, y (word) + các mục 4 byte
    # (mã hiệu ứng word, tốc độ, giá trị +0x1C) + byte cuối là cờ: 0 = gỡ (game ghi +0x18 = 1, bộ đếm khung 0x2710 để hết hình rồi xoá),
    # khác 0 = đặt. Danh sách sắp theo y - x để vẽ, chung với nút đối tượng (xq+0x41F4D9: +0 = 0, +4 = đối tượng).
    # Nút 0x2C byte: +0 sprite, +4 đối tượng, +8 bộ đếm khung, +0xC tốc độ, +0x10 / +0x14 ô x / y (cùng hệ get_toado), +0x18 cờ đặt
    # (đo 2), +0x1C (đo 2), +0x20 mã sprite kế tiếp (0xFFFF = không), +0x24 nút trước, +0x28 nút sau.
    # Nút KHÔNG có mã kỹ năng / người đặt / thời hạn: mã lấy ngược từ sprite qua bộ đệm 100 ô của hàm nạp perform/<mã>.dat
    # (xq+0x4083A0): [MAHIEUUNGDAT + i*4] = mã, [BANGSPRITEHIEUUNG + (i+1)*4] = sprite. Bộ đệm đầy thì đẩy ô cũ ra (xoay vòng) và nhả
    # sprite dù nút còn trỏ tới (chính là crash engine.dll+0x424D) => nhớ mã theo địa chỉ nút lúc còn tra được
    OFFSET_HIEUUNGDAT_SPRITE = 0x0
    OFFSET_HIEUUNGDAT_DOITUONG = 0x4
    OFFSET_HIEUUNGDAT_X = 0x10
    OFFSET_HIEUUNGDAT_Y = 0x14
    OFFSET_HIEUUNGDAT_CO = 0x18
    OFFSET_HIEUUNGDAT_SAU = 0x28
    KICHTHUOCNUTHIEUUNGDAT = 0x2C
    SOOBODEMHIEUUNG = 100
    # Chặn vòng lặp khi đọc trúng lúc game đang sửa danh sách
    SONUTHIEUUNGDATTOIDA = 1000

    def get_danhsachhieuungdat(self):
        # [{"diachi", "ma" (None khi không tra được), "x", "y", "co"}] các nút có sprite (bỏ nút đối tượng)
        ketqua = []
        try:
            dau = read_int(self.tientrinh, self.diachixq + DC.DSHIEUUNGDAT)
            if not dau:
                return ketqua
            mas = struct.unpack(f"<{self.SOOBODEMHIEUUNG}I", read_bytes(self.tientrinh, self.diachixq + DC.MAHIEUUNGDAT, 4 * self.SOOBODEMHIEUUNG))
            sprites = struct.unpack(f"<{self.SOOBODEMHIEUUNG}I", read_bytes(self.tientrinh, self.diachixq + DC.BANGSPRITEHIEUUNG + 4, 4 * self.SOOBODEMHIEUUNG))
        except Exception:
            return ketqua
        matheosprite = {sprite: ma for sprite, ma in zip(sprites, mas) if sprite and ma}
        nut, danhdau, nhomoi = dau, set(), {}
        while nut and nut not in danhdau and len(danhdau) < self.SONUTHIEUUNGDATTOIDA:
            danhdau.add(nut)
            try:
                sprite, doituong, _, _, x, y, co, _, _, _, sau = struct.unpack("<11I", read_bytes(self.tientrinh, nut, self.KICHTHUOCNUTHIEUUNGDAT))
            except Exception:
                break
            if sprite and not doituong:
                ma = matheosprite.get(sprite)
                ma = ma if ma is not None else self._mahieuungdattheonut.get(nut)
                if ma is not None:
                    nhomoi[nut] = ma
                ketqua.append({"diachi": nut, "ma": ma, "x": x, "y": y, "co": co})
            nut = sau
        self._mahieuungdattheonut = nhomoi
        return ketqua

    def get_danhsachtranphap(self):
        # Trận pháp Vân Mộng Cốc đang có: [{"ma", "ten", "x", "y", ...}], bỏ nút đang gỡ (cờ 1). Nút không tra được mã (sprite đã bị
        # đẩy khỏi bộ đệm trước khi bot kịp thấy) vẫn tính là trận chưa rõ loại: tránh nhầm còn hơn đặt trùng tâm
        dstran = []
        for nut in self.get_danhsachhieuungdat():
            if nut["co"] == 1:
                continue
            if nut["ma"] is None or nut["ma"] in TRANPHAPVANMONGCOCs:
                nut["ten"] = TRANPHAPVANMONGCOCs.get(nut["ma"], "trận chưa rõ")
                dstran.append(nut)
        return dstran

    def get_danhsachtranlacanh(self):
        # Trận Pháp Lạc Ảnh (Đào Hoa Lạc Ảnh 2115) trên mặt đất: 2 nút cùng tâm mã MAHIEUUNGDATLACANHs (21151 + 21152), gộp theo tâm.
        # Tâm = người dùng chiêu. Ghi log khi danh sách đổi, kèm mọi mã hiệu ứng đất đang thấy
        dsnut = [nut for nut in self.get_danhsachhieuungdat() if nut["co"] != 1]
        dstran = list({(nut["x"], nut["y"]): nut for nut in dsnut if nut["ma"] in MAHIEUUNGDATLACANHs}.values())
        chuky = (tuple(sorted((nut["x"], nut["y"]) for nut in dstran)), tuple(sorted({nut["ma"] or 0 for nut in dsnut})))
        if chuky != self._logdanhsachlacanhgannhat:
            self._logdanhsachlacanhgannhat = chuky
            mota = ", ".join(f"({nut['x']},{nut['y']})" for nut in dstran)
            self._inlog(f"[TRẬN LẠC ẢNH] thấy {len(dstran)} trận{' tâm ' + mota if mota else ''}; mã hiệu ứng đất đang có: {list(chuky[1])}")
        return dstran

    def get_tamtrandangco(self):
        # Ô tâm không đặt trận được: trận đang có trên mặt đất + tâm mình vừa đặt (gói tạo nút chưa về)
        thoidiemhientai = time.time()
        self._tamtranvuadat = {o: t for o, t in self._tamtranvuadat.items() if thoidiemhientai - t < THOIGIANNHOTAMTRANVUADAT}
        dstran = self.get_danhsachtranphap()
        chuky = tuple(sorted((tran["ma"] or 0, tran["x"], tran["y"]) for tran in dstran))
        if chuky != self._logdanhsachtrangannhat:
            self._logdanhsachtrangannhat = chuky
            mota = ", ".join(f"{tran['ten']}{'' if tran['ma'] is None else ' ' + str(tran['ma'])} tâm ({tran['x']},{tran['y']})" for tran in dstran)
            self._inlog(f"[TRẬN PHÁP] thấy {len(dstran)} trận trên mặt đất{': ' + mota if mota else ''}")
        return {(tran["x"], tran["y"]) for tran in dstran} | set(self._tamtranvuadat)

    def _chontamtranvanmongcoc(self, matran, x2, y2, x1, y1, tamxa):
        # Chọn tâm trận Vân Mộng Cốc cho mục tiêu ở (x2, y2), mình ở (x1, y1); mọi khoảng cách đo kiểu ô vuông như tầm đánh.
        #  - Kỳ Môn (3x3): ưu tiên đúng ô mục tiêu; ô đó đã có trận thì ô kề (vẫn phủ mục tiêu) gần mục tiêu nhất
        #  - Độn Giáp (5x5): ô lệch 1 khỏi ô mục tiêu (không bao giờ đặt vào ô mục tiêu: chừa tâm cho Kỳ Môn), ưu tiên phía mình
        #    (chắc chắn trong tầm); hết ô lệch 1 thì lệch 2 (mục tiêu vẫn ở mép vùng)
        # Bỏ ô đã có trận (game không cho 2 trận chung tâm) và ô ngoài tầm tamxa. Không có ô nào thì trả None (bỏ lượt đặt)
        nuacanh = NUACANHTRANVANMONGCOCs.get(matran, 1)
        tx, ty = round(x2), round(y2)
        tamdangco = self.get_tamtrandangco()
        ungvien = []
        for dx in range(-nuacanh, nuacanh + 1):
            for dy in range(-nuacanh, nuacanh + 1):
                o = (tx + dx, ty + dy)
                lech = max(abs(dx), abs(dy))
                if matran == VITRIKYNANG_DONGIAPTRAN and lech == 0:
                    continue
                if o in tamdangco or max(abs(o[0] - x1), abs(o[1] - y1)) > tamxa:
                    continue
                phu = math.dist(o, (x1, y1)) if matran == VITRIKYNANG_DONGIAPTRAN else math.dist(o, (x2, y2))
                ungvien.append((lech, phu, o))
        ten = TRANPHAPVANMONGCOCs.get(matran, "trận")
        if not ungvien:
            self._inlog(f"[TRẬN PHÁP] {ten}: quanh mục tiêu ({tx},{ty}) không còn ô tâm trống trong tầm => không đặt")
            return None
        lech, _, o = min(ungvien)
        if matran != VITRIKYNANG_DONGIAPTRAN and lech:
            self._inlog(f"[TRẬN PHÁP] {ten}: ô mục tiêu ({tx},{ty}) đã có trận => đặt ô kề ({o[0]},{o[1]})")
        return o

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

    def get_lucvaobando(self, idbando):
        # Lần gần nhất vào bản đồ idbando (0. nếu chưa vào từ lúc chạy bot)
        return self._lucvaobando.get(idbando, 0.)

    def get_is_toadochuaondinh(self):
        # Vừa đổi bản đồ (phù / cổng) mà toạ độ vẫn là toạ độ ở bản đồ cũ: mã bản đồ đổi trước, toạ độ 2-3s sau mới đổi (ThichVaCham phù về
        # Tân Thủ Thôn: bản đồ 1 mà còn ở (73, 182) Tần Quốc => tính ra cổng (244, 254), đi bộ vòng về Tề). Chờ tối đa THOIGIANCHOTOADOSAUDOIBANDO
        conlai = time.time() - self._thoidiemthaydoibandogannhat
        if conlai < THOIGIANCHOSAUDOIBANDO:
            return True
        return conlai < THOIGIANCHOTOADOSAUDOIBANDO and self._toadobandocu is not None and self.get_toado() == self._toadobandocu

    def get_is_cuasogametontai(self):
        return win32gui.IsWindow(self.idcuaso)

    def get_is_cuasogamekichhoat(self):
        return win32gui.GetForegroundWindow() == self.idcuaso

    def get_diachicosothongtinnhanvatdangchichuot(self):
        return read_int(self.tientrinh, self.diachixq + DC.NHANVATDANGCHICHUOT)

    def get_is_cothegaychoang(self, diachicosothongtinnhanvat, thoigiangiancach = 2.0):
        if not diachicosothongtinnhanvat:
            return False
        idnguoichoi = self.get_idnguoichoi(diachicosothongtinnhanvat)
        if idnguoichoi <= 0:
            return True
        if self.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat, is_hieuungcoloi = 0):
            return False
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
        # py-spy 2026-11-12: hàm này chiếm 21% CPU tiến trình bot (luồng bỏ khựng 0.02s/lượt, giữ ô trống 0.03s/lượt, ước lượng mục tiêu,
        # vòng chính... đều gọi, mỗi lần 3 lần đọc bộ nhớ). Nhân vật của mình: nhớ kết quả THOIGIANNHONHANVATTONTAI giây, dùng chung mọi
        # luồng; đối tượng khác: đọc id (+0x20) và loại (+0xF0) bằng 1 lần đọc thay vì 2
        if diachicosothongtinnhanvat:
            return self._is_doituongnhanvat(diachicosothongtinnhanvat)
        bayh = time.monotonic()
        nho = self._nhanvattontai_nho
        if bayh - nho[0] < THOIGIANNHONHANVATTONTAI:
            return nho[1]
        # Luôn đọc mới con trỏ (cập nhật luôn bản nhớ của get_diachicosothongtinnhanvat1). Nhân vật không còn (chuyển bản đồ, mất kết
        # nối) hoặc đọc lỗi thì xoá bản nhớ con trỏ để các get_*() sau đọc mới, không đọc tiếp vào đối tượng cũ
        try:
            ketqua = self._is_doituongnhanvat(self._doccontronhanvat())
        except Exception:
            self._contronhanvat_nho = (-1e9, 0)
            raise
        if not ketqua:
            self._contronhanvat_nho = (-1e9, 0)
        self._nhanvattontai_nho = (bayh, ketqua)
        return ketqua

    def _is_doituongnhanvat(self, diachi):
        # id > 0 và loại là nhân vật. Địa chỉ hỏng thì read_bytes báo lỗi như read_int trước đây (nơi gọi bắt PymemError)
        dulieu = read_bytes(self.tientrinh, diachi + 0x20, 0xF4 - 0x20)
        iddoituong, = struct.unpack_from("<i", dulieu, 0)
        idloai, = struct.unpack_from("<i", dulieu, 0xF0 - 0x20)
        return iddoituong > 0 and idloai in (LOAIDOITUONG_NHANVAT1, LOAIDOITUONG_NHANVATKHAC1)

    def get_is_nhanvatanthan(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + DC.NV_ANTHAN) > 0

    def get_phamchatvatpham(self, diachi):
        # Phẩm chất (màu tên) vật phẩm dưới đất, xem PHAMCHATVATPHAM_MAP; 0 = thường
        return read_short_int(self.tientrinh, diachi + 0x29)

    def get_is_vatphamtontai(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return self.get_iddoituong(diachicosothongtinnhanvat) != -1 and self.get_idloaidoituong(diachicosothongtinnhanvat) == LOAIDOITUONG_VATPHAMDUOIDAT

    def get_is_nhanvatdachet(self, diachicosothongtinnhanvat = None):
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return read_boolean(self.tientrinh, diachicosothongtinnhanvat + DC.NV_CHET)

    def get_danhhieudoituong(self, diachi):
        # Danh hiệu hiện phía trên tên (NPC cửa hàng các nước: tên riêng "Ô Địch", danh hiệu "Chủ Tiệm Vũ Khí"), "" nếu không có
        return re.sub(r"\x1b.", "", read_bytes(self.tientrinh, diachi + DC.NV_DANHHIEU, 0x40).split(b"\0")[0].decode("utf-8", "ignore")).strip()

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

    def get_toadobuoc(self, diachicosothongtinnhanvat = None):
        # Ô đích của bước đang đi (+ 0x18, + 0x1C); đứng yên thì trùng toạ độ đang vẽ
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return struct.unpack("<ii", read_bytes(self.tientrinh, diachicosothongtinnhanvat + 0x18, 8))

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

    def get_ngoaihieu(self, diachicosothongtinnhanvat = None):
        # Ngoại hiệu hiện trên tên người chơi (+0x1134, vd "2VIP"), bỏ mã màu ESC + chữ cái / [ ] như game (xq + 0x22010). Không phải tên bang
        diachicosothongtinnhanvat = diachicosothongtinnhanvat or self.get_diachicosothongtinnhanvat1()
        return re.sub(r"\x1b[a-zA-Z\[\]]", "", read_string(self.tientrinh, diachicosothongtinnhanvat + 0x1134) or "").strip()

    def get_bangphai(self, idnguoichoi):
        # Tên bang của người chơi theo lần "desc user" gần nhất: "" không có bang, None chưa biết
        thongtin = self._bangphainguoichoi_map.get(idnguoichoi)
        return thongtin[0] if thongtin else None

    def get_thoidiembangphai(self, idnguoichoi):
        # Thời điểm biết bang của người chơi (lần "desc user" trả lời gần nhất), chưa biết thì 0
        thongtin = self._bangphainguoichoi_map.get(idnguoichoi)
        return thongtin[1] if thongtin else 0.

    def action_hoibangphaicuaminh(self):
        # "desc user <ID mình>" hỏi lại bang của chính mình ngay (bỏ qua THOIGIANLAMMOIBANGPHAI, vd kéo cấp kiểm tra đã vào bang chưa);
        # trả lời ghi vào get_bangphai / get_thoidiembangphai. -> True nếu đã gửi
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemhoibangphaiganhat < GIANCACHHOIBANGPHAI:
            return False
        if self._yeucaubangphai and thoidiemhientai - self._yeucaubangphai[2] < THOIGIANCHOTRALOIBANGPHAI:
            return False
        diachi = self.get_diachicosothongtinnhanvat1()
        idnguoichoi = self.get_idnguoichoi(diachi)
        if not idnguoichoi or idnguoichoi < 0:
            return False
        if self.action_thucthicaulenh("desc user {}".format(idnguoichoi), douutien = DOUUTIEN_THAP):
            self._yeucaubangphai = (idnguoichoi, self.get_tendoituong(diachi), thoidiemhientai)
            self._thoidiemhoibangphaiganhat = thoidiemhientai
            return True
        return False

    def get_is_cungbang(self, diachicosothongtinnhanvat):
        # So bang của mình với bang người đó (hỏi qua "desc user", action_hoibangphai). Chưa biết bang của mình hoặc của họ thì coi như cùng
        # bang để không đánh nhầm; mình không có bang thì không ai cùng bang
        return self._is_cungbangtheoid(self.get_idnguoichoi(diachicosothongtinnhanvat))

    def get_is_cungbangtheoten(self, tennguoichoi):
        # Như get_is_cungbang, dùng khi người đó không ở gần (chủ bảo thú): tra ID theo tên đã gặp trong trả lời "desc user"
        return self._is_cungbangtheoid(self._idnguoichoitheoten_map.get(tennguoichoi))

    def _is_cungbangtheoid(self, idnguoichoi):
        bangminh = self.get_bangphai(self.get_idnguoichoi())
        bangho = self.get_bangphai(idnguoichoi) if idnguoichoi else None
        if bangminh is None or bangho is None:
            return True
        return bool(bangminh) and bangminh == bangho

    def action_hoibangphai(self):
        # Gửi "desc user <ID>" (game gửi lệnh này khi giữ Ctrl bấm vào người chơi, xq + 0x9967; "desc char" là quan sát, người kia nhận tin
        # "có ai đó đang lén quan sát bạn") cho mình rồi cho người chơi khác nhóm xung quanh
        # chưa biết bang / đã lâu; mỗi lần 1 người, chờ trả lời (_xulydongthongtinnguoichoi) hoặc hết THOIGIANCHOTRALOIBANGPHAI mới hỏi tiếp
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemhoibangphaiganhat < GIANCACHHOIBANGPHAI:
            return
        if self._yeucaubangphai and thoidiemhientai - self._yeucaubangphai[2] < THOIGIANCHOTRALOIBANGPHAI:
            return
        self._yeucaubangphai = None
        cans = [self.get_diachicosothongtinnhanvat1()] + [diachi for diachi in self._get_diachidoituongxungquanhs(is_nguoichoi = True)
                                                          if self.get_idloainhanvat(diachi) == LOAIMUCTIEU_NGUOICHOIKHACNHOM
                                                          and self.get_khoangcach(diachi) <= KHOANGCACHHOIBANGPHAI]
        for diachi in cans:
            idnguoichoi = self.get_idnguoichoi(diachi)
            if not idnguoichoi or idnguoichoi < 0:
                continue
            thongtin = self._bangphainguoichoi_map.get(idnguoichoi)
            if thongtin and thoidiemhientai - thongtin[1] < THOIGIANLAMMOIBANGPHAI:
                continue
            if self.action_thucthicaulenh("desc user {}".format(idnguoichoi), douutien = DOUUTIEN_THAP):
                self._yeucaubangphai = (idnguoichoi, self.get_tendoituong(diachi), thoidiemhientai)
                self._thoidiemhoibangphaiganhat = thoidiemhientai
            return

    def action_hoithongtinnguoichoimuctieu(self, diachicosothongtinnhanvat):
        # "desc user <ID>" cho riêng 1 người chơi (mục tiêu đang chọn, uocluongmuctieu_xq) để biết môn phái / bang phái, kể cả khi không
        # bật PK bang (action_hoibangphai chỉ chạy lúc đó). Cùng giãn cách / chờ trả lời / tầm hỏi / thời gian làm mới với action_hoibangphai
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemhoibangphaiganhat < GIANCACHHOIBANGPHAI:
            return False
        if self._yeucaubangphai and thoidiemhientai - self._yeucaubangphai[2] < THOIGIANCHOTRALOIBANGPHAI:
            return False
        idnguoichoi = self.get_idnguoichoi(diachicosothongtinnhanvat)
        if not idnguoichoi or idnguoichoi < 0 or self.get_khoangcach(diachicosothongtinnhanvat) > KHOANGCACHHOIBANGPHAI:
            return False
        thongtin = self._bangphainguoichoi_map.get(idnguoichoi)
        if thongtin and thoidiemhientai - thongtin[1] < THOIGIANLAMMOIBANGPHAI:
            return False
        if self.action_thucthicaulenh("desc user {}".format(idnguoichoi), douutien = DOUUTIEN_THAP):
            self._yeucaubangphai = (idnguoichoi, self.get_tendoituong(diachicosothongtinnhanvat), thoidiemhientai)
            self._thoidiemhoibangphaiganhat = thoidiemhientai
            return True
        return False

    def get_thongtinnguoichoi(self, idnguoichoi):
        # (tên môn phái hiển thị, tên bang) theo lần "desc user" gần nhất: None = chưa biết, bang "" = không có bang
        ma = self._monphainguoichoi_map.get(idnguoichoi)
        return (TENMONPHAI.get(ma, ma) if ma else None), self.get_bangphai(idnguoichoi)

    def _xulydongthongtinnguoichoi(self, noidung):
        # Trả lời "desc user": " Danh tính: <tên> ( .. )", " Môn phái: ...", " Quốc gia: ...", " Bang phái: <tên bang>", " Ngoại hiệu: ...",
        # " Điểm PK: ..." cả khối nối "\n" trong 1 tin (xq + 0xC9AF0 nhận cả khối rồi mới tách dòng). Không có dòng Bang phái tới Ngoại hiệu /
        # Điểm PK thì coi như không có bang
        for dong in noidung.split("\n"):
            dong = dong.strip()
            # Đầu khối còn vài byte điều khiển trước "Danh tính" nên tìm, không khớp từ đầu
            m = re.search(r"Danh tính:\s*(.+?)\s*\(\s*\d+\s*\)$", dong)
            if m:
                self._tendanggomthongtin = m.group(1).strip()
                self._monphaidanggomthongtin = None
                continue
            ten = self._tendanggomthongtin
            if not ten:
                continue
            if dong.startswith("Môn phái:"):
                self._monphaidanggomthongtin = dong.split(":", 1)[1].strip()
            elif dong.startswith("Bang phái:"):
                # Niết Bàn ghi "－－" khi không có bang (Aegis bỏ hẳn dòng Bang phái)
                self._ghibangphai(ten, dong.split(":", 1)[1].strip().strip("－-"))
            elif dong.startswith(("Ngoại hiệu:", "Điểm PK:")):
                self._ghibangphai(ten, "")

    def _ghibangphai(self, ten, tenbang):
        tenmonphaigame = self._monphaidanggomthongtin
        self._tendanggomthongtin = None
        self._monphaidanggomthongtin = None
        yeucau = self._yeucaubangphai
        if yeucau and yeucau[1] == ten:
            idnguoichoi = yeucau[0]
            self._yeucaubangphai = None
        else:
            # Người chơi tự xem thông tin người khác (chuột): tìm ID theo tên trong số người chơi xung quanh
            idnguoichoi = next((self.get_idnguoichoi(diachi) for diachi in [self.get_diachicosothongtinnhanvat1()] + list(self._get_diachidoituongxungquanhs(is_nguoichoi = True))
                                if self.get_tendoituong(diachi) == ten), None)
        if not idnguoichoi:
            return
        if self.get_bangphai(idnguoichoi) != tenbang:
            self._inlog(f"[BANG PHÁI] {ten} ({idnguoichoi}): {tenbang or 'không có bang'}")
        self._bangphainguoichoi_map[idnguoichoi] = (tenbang, time.time())
        self._idnguoichoitheoten_map[ten] = idnguoichoi
        if tenmonphaigame:
            monphai = self._mamonphaitheoten(tenmonphaigame)
            if self._monphainguoichoi_map.get(idnguoichoi) != monphai:
                self._inlog(f"[MÔN PHÁI] {ten} ({idnguoichoi}): {tenmonphaigame}" + ("" if monphai in TENMONPHAI else " (chưa có trong TENMONPHAI)"))
            self._monphainguoichoi_map[idnguoichoi] = monphai

    @staticmethod
    def _mamonphaitheoten(tenmonphaigame):
        # Tên môn phái game in trong "desc user" -> mã trong TENMONPHAI (so bỏ khoảng trắng / hoa thường, chấp nhận tên ngắn hơn
        # như "Đào Hoa"); không khớp thì giữ nguyên tên game in ra
        chuanhoa = lambda s: re.sub(r"\s+", "", s).lower()
        tengame = chuanhoa(tenmonphaigame)
        for ma, tenhienthi in TENMONPHAI.items():
            if chuanhoa(tenhienthi) == tengame:
                return ma
        for ma, tenhienthi in TENMONPHAI.items():
            if tengame and (tengame in chuanhoa(tenhienthi) or chuanhoa(tenhienthi) in tengame):
                return ma
        return tenmonphaigame

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

    def get_khoangcachtamdanh(self, diachicosothongtinnhanvat2, diachicosothongtinnhanvat1 = False):
        # Khoảng cách máy chủ dùng để xét tầm chiêu: theo ô, max(|dx|, |dy|) (vùng tầm là hình vuông: chéo tầm 8 với tới ~11.3 ô thẳng).
        # Đo bằng log [TẦM XA CHI TIẾT]: max 8 / thẳng 10 ra 7/7, max 9 / thẳng 9 chỉ ra 16/56
        x2, y2 = self.get_toado(diachicosothongtinnhanvat2)
        return self.get_khoangcachtamdanhdiem(x2, y2, diachicosothongtinnhanvat1)

    def get_khoangcachtamdanhdiem(self, x2, y2, diachicosothongtinnhanvat1 = False):
        diachicosothongtinnhanvat1 = diachicosothongtinnhanvat1 or self.get_diachicosothongtinnhanvat1()
        x1, y1 = self.get_toado(diachicosothongtinnhanvat1)
        return float(max(abs(x2 - x1), abs(y2 - y1)))

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

    def get_toadothanhviennhoms(self):
        # Toạ độ các thành viên nhóm (chấm trên bản đồ): x ở + 0xBD0, y ở + 0xC00, mỗi người 4 byte theo thứ tự id ở + 0; 65535 = ở bản đồ
        # khác, 0 = chính mình (đo 2026-10-31). -> [(x, y)] những người cùng bản đồ
        diachicosothanhviennhom = self.get_diachicosoidthanhviennhom()
        if not diachicosothanhviennhom:
            return []
        xs = struct.unpack("<%di" % SOLUONGTHANHVIENNHOMTOIDATHUCTE, read_bytes(self.tientrinh, diachicosothanhviennhom + 0xBD0, SOLUONGTHANHVIENNHOMTOIDATHUCTE * 4))
        ys = struct.unpack("<%di" % SOLUONGTHANHVIENNHOMTOIDATHUCTE, read_bytes(self.tientrinh, diachicosothanhviennhom + 0xC00, SOLUONGTHANHVIENNHOMTOIDATHUCTE * 4))
        return [(x, y) for x, y in zip(xs, ys) if 0 < x < 65535 and 0 < y < 65535]

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

    def get_is_quai(self, diachicosothongtinnhanvat):
        # Lớp +0x29 == 0x82 (xem get_is_npc)
        if not diachicosothongtinnhanvat:
            return False
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x29) == 0x82

    def get_is_npc(self, diachicosothongtinnhanvat):
        # Lớp đối tượng +0x29 (gói tin xuất hiện): < 0x80 người chơi, 0x80 NPC, 0x82 quái, 0xA0 / 0xA1 bảo thú. Game nhận NPC đúng
        # bằng == 0x80 (xq + 0x55870 tô tên thù địch, xq + 0xB5C1D cập nhật dấu nhiệm vụ NPC). Trước đây đoán qua +0x155C (nhịp hoạt
        # ảnh, game chỉ gán cứng 40 / 25 cho NPC ở tư thế 1 / 5) và %máu > 100 (bảo thú vật phẩm 120%) => sót NPC đang đi, nhận nhầm quái
        if not diachicosothongtinnhanvat:
            return False
        return read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x29) == 0x80

    def get_is_baothuvatpham(self, diachicosothongtinnhanvat):
        # Bảo thú gọi bằng vật phẩm (Thần Thú, Song Tử, Thuỷ Bình...): không tấn công được, không mất máu. Nhận theo tên trong BAOTHUVATPHAMs,
        # hoặc tên không có chủ nhân trong ngoặc mà lớp +0x29 là bảo thú (0xA0 / 0xA1) hoặc máu hiện > 100% (bảo thú vật phẩm 120%).
        # get_is_npc cũ có nhánh %máu > 100 nên chặn luôn mọi bảo thú vật phẩm; đổi sang +0x29 == 0x80 thì mất nhánh đó, con nào ngoài
        # danh sách tên (Thuỷ Bình) bị chọn làm mục tiêu => xét lại ở đây
        if not diachicosothongtinnhanvat:
            return False
        if self.get_tendoituong(diachicosothongtinnhanvat) in BAOTHUVATPHAMs:
            return True
        lop = read_short_int(self.tientrinh, diachicosothongtinnhanvat + 0x29)
        # Người chơi (< 0x80) không bao giờ là bảo thú vật phẩm (kẻo máu > 100% vì buff mà bỏ sót mục tiêu PK)
        if lop < 0x80 or "(" in (self._get_tenthucte(diachicosothongtinnhanvat) or ""):
            return False
        return lop in (0xA0, 0xA1) or self.get_phantramsinhlucconlai(diachicosothongtinnhanvat) > 100

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

    def get_tenkynangtheoid(self, idkynang):
        # Tên đầy đủ lấy ở dòng tiêu đề mô tả trong ô kỹ năng ("\x1bC Giao Long Nhập Hải (Cấp 3)", chỉ có khi game đã lấy mô tả); chưa có
        # thì lấy tên ở + KN_ID + 0x8 (cố định 0x14 byte, tên dài bị cắt, có khi dính "(Cấp"). Không có trên bảng thì None
        dulieu = self._docokynangtheoid(idkynang)
        if not dulieu:
            return None
        noidung = unicodedata.normalize("NFC", dulieu.replace(b"\x00", b"\n").decode("utf-8", "ignore"))
        tieude = re.search(r"\x1bC\s*([^\n\x1b]+?)\s*\(Cấp", noidung)
        if tieude:
            return tieude.group(1)
        ten = unicodedata.normalize("NFC", dulieu[0x8:0x8 + 0x14].split(b"\x00")[0].decode("utf-8", "ignore"))
        return ten.split("(")[0].strip() or None

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
        # Tâm pháp hộ thể chuyển sát thương thành pháp lực (Côn Luân Càn Khôn Na Di "chuyển hóa 700 điểm sát thương thành tiêu hao Pháp
        # Lực"): lấy số đầu tiên = cấp hiện tại (mô tả cấp tiếp theo nằm sau)
        chuyenhoa = re.search(r"chuyển hóa\s+(\d+)\s+điểm sát thương", noidung)
        if chuyenhoa:
            ketqua["chuyển hóa"] = int(chuyenhoa.group(1))
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

    def _is_quainhiemvu(self, tendoituong):
        # Quái nhiệm vụ sinh riêng cho 1 người (Lưu Manh của Hiệp Trợ Trị An): trong ngoặc là ID người nhận nhiệm vụ "Lưu Manh (31)",
        # còn bảo thú thì trong ngoặc là tên nhân vật chủ => ngoặc đầu toàn số thì là quái, không phải bảo thú
        m = re.search(r"\(([^()]*)\)", tendoituong or "")
        return bool(m) and m.group(1).strip().isdigit()

    def get_is_baothugiangho(self, diachicosodoituong):
        if not diachicosodoituong:
            return False
        tendoituong = self._get_tenthucte(diachicosodoituong)
        if not tendoituong or self._is_quainhiemvu(tendoituong):
            return False
        return "(" in tendoituong and "cấp" not in tendoituong.lower()

    def get_is_baothukynangtrieuhoi(self, diachicosodoituong):
        if not diachicosodoituong:
            return False
        tendoituong = self._get_tenthucte(diachicosodoituong)
        if not tendoituong or self._is_quainhiemvu(tendoituong):
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
        if self.get_is_npc(diachicosothongtinnhanvat) or self.get_is_baothuvatpham(diachicosothongtinnhanvat)                 or self.get_is_nhanvatchuasansang(diachicosothongtinnhanvat):
            return False

        idmaupk = self.get_idmaupk()
        tenmuctieu = self.get_tendoituong(diachicosothongtinnhanvat)

        if tenmuctieu:
            if self.get_is_baothukynangtrieuhoi(diachicosothongtinnhanvat) or self.get_is_baothugiangho(diachicosothongtinnhanvat):
                if idmaupk == MAUPK_HOABINH:
                    return False
                tenchunhan = self.get_tenchunhan(diachicosothongtinnhanvat)
                if tenchunhan:
                    if tenchunhan == self.get_tendoituong():
                        return False
                    diachicosothongtinnhanvatchunhan = self.action_timkiemnhanvat(tennhanvat = tenchunhan)
                    if diachicosothongtinnhanvatchunhan:
                        return self.get_is_cothetancong(diachicosothongtinnhanvatchunhan)
                    # Chủ không ở gần: chế độ bang thì tra bang theo tên (chưa biết thì coi như cùng bang, không đánh)
                    if idmaupk == MAUPK_BANG and self.get_is_cungbangtheoten(tenchunhan):
                        return False

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
        # Click xuống đất để đi (kể cả click nhanh, cả lúc đang xuất chiêu): chuột trái thật vừa bấm trên cửa sổ game và đích click
        # chuột của game vừa đổi sang ô mới => tính như đã giữ đủ lâu, bot thôi chặn di chuyển. Click quái / bảng giao diện không đặt
        # đích click nên không tính; bot tự đi thì xoá đích về 0 (không tính)
        # Click hay giữ chuột đều KHÔNG cắt tư thế xuất chiêu: cắt hoạt ảnh cho đi sớm thì máy chủ vẫn đang tính chiêu, toạ độ client
        # lệch máy chủ => nhân vật giật. Để hoạt ảnh chiêu cuối chạy hết, chỉ thả mốc client tự gửi lệnh (client tự đi khi hết hoạt
        # ảnh). Đang tính giữ / click thì bot không gửi chiêu nào (các chỗ gọi hàm này) và tactu gửi ngắt đánh thường
        # (action_ngatdichuyenkhixuatchieu)
        thoidiemhientai = time.time()
        is_bamchuotthat = self._is_dangdichuottraitrongcuaso()
        if is_bamchuotthat:
            self._thoidiembamchuottraigannhat = thoidiemhientai
        khoidieukhien = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        dichclick = read_bytes(self.tientrinh, khoidieukhien + DC.KDK_DICHCLICK, 8) if khoidieukhien else None
        if dichclick != self._dichclicktruoc:
            if self._dichclicktruoc is not None and dichclick and any(dichclick) \
                    and thoidiemhientai - self._thoidiembamchuottraigannhat < THOIGIANNHANCLICKDICHUYEN:
                self._thoidiemgiuchuottraigannhat = thoidiemhientai
                self._dichclicknguoichoi = dichclick
                self._inlog(f"[CLICK ĐI] Người chơi click tới {struct.unpack('<ii', dichclick)}, tư thế {self.get_idtuthenhanvat()}: Foxia nhường di chuyển")
                self.action_thamocchonguoichoi()
            self._dichclicktruoc = dichclick
        # Còn đang đi tới đích người chơi vừa click thì vẫn tính (không để bot ra chiêu / đi cắt ngang giữa đường)
        if self._dichclicknguoichoi:
            if dichclick == self._dichclicknguoichoi and self.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
                self._thoidiemgiuchuottraigannhat = thoidiemhientai
            elif thoidiemhientai - self._thoidiemgiuchuottraigannhat >= THOIGIANNGUNGSAUNHACHUOT:
                self._dichclicknguoichoi = None
        if read_boolean(self.tientrinh, self.diachixq + DC.DANGCLICKCHUOTTRAI) or is_bamchuotthat:
            if not self._thoidiembatdaugiuchuottrai:
                self._thoidiembatdaugiuchuottrai = thoidiemhientai
            if thoidiemhientai - self._thoidiembatdaugiuchuottrai >= THOIGIANGIUCHUOTTOITHIEU:
                self._thoidiemgiuchuottraigannhat = thoidiemhientai
                self.action_thamocchonguoichoi()
                return True
        else:
            self._thoidiembatdaugiuchuottrai = 0.
        return thoidiemhientai - self._thoidiemgiuchuottraigannhat < THOIGIANNGUNGSAUNHACHUOT

    def action_thamocchonguoichoi(self):
        # Người chơi giữ chuột / click để đi: bỏ khựng sau chiêu của bot và kéo mốc client tự gửi lệnh (bot có thể đã đẩy tới bằng
        # action_chandichuyen) về hiện tại, KHÔNG đụng hoạt ảnh / tư thế: client chờ hết hoạt ảnh chiêu cuối rồi tự đi tới đích chuột
        # Chỉ làm khi còn tư thế xuất chiêu: lúc đang đi, mốc này là nhịp gửi "go" của chính client (lúc gửi + 500ms), kéo về liên
        # tục thì client gửi "go" dồn dập, toạ độ lệch máy chủ => đi bình thường cũng giật
        diachi = self.get_diachicosothongtinnhanvat1()
        if not diachi or self.get_idtuthenhanvat(diachi) not in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT):
            return
        self._is_chieucanngatdichuyen = False
        self._thoidiemxuatchieugannhat = 0.
        thongtingame = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not thongtingame:
            return
        baygio = ctypes.windll.winmm.timeGetTime() & 0xFFFFFFFF
        mochientai = struct.unpack("<I", read_bytes(self.tientrinh, thongtingame + DC.TG_MOCTUGUILENH, 4))[0]
        if 0 < (mochientai - baygio) & 0xFFFFFFFF < 0x80000000:
            write_bytes(self.tientrinh, thongtingame + DC.TG_MOCTUGUILENH, struct.pack("<I", baygio), 4)

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
        if self.is_nietban:
            return
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
                # Bằng hàm của game (vtable[1]): chỉ ghi + 0x34 thì hộp ẩn mà vẫn kẹt trong danh sách cửa sổ, chặn chuột
                if read_int(self.tientrinh, x + DC.TG_CUASOYESNO):
                    self._goivtableanhien(DC.TG_CUASOYESNO, is_danghiencuasoyesno)

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

    def get_nhanluachoncuasotuychons(self):
        # Nhãn hiển thị của từng lựa chọn, cùng thứ tự với get_lenhcuasotuychons, vd "7.Ẩn hiệu ứng Kĩ năng" (bỏ mã màu). Mỗi lựa chọn là
        # 1 ô chữ con: mảng con trỏ ở cửa sổ tuỳ chọn + 0x1D78, chữ ở ô + 0x24 (ô + 0x20 trỏ ngược về cửa sổ tuỳ chọn). Đo 2026-11-08
        # trên menu Chức năng hệ thống ("pf2 908", acc 535 Aegis). Ô thừa của menu dài cũ còn nằm sau, chỉ lấy đủ số lựa chọn
        x = self._get_diachicuasotuychon()
        if not x:
            return []
        soluachon = read_int(self.tientrinh, x + 0x1DB8)
        if not 0 < soluachon <= 20:
            return []
        nhans = []
        for k in range(soluachon):
            o = read_int(self.tientrinh, x + 0x1D78 + k * 4)
            nhan = read_bytes(self.tientrinh, o + 0x24, 0x80).split(b"\0")[0].decode("utf-8", "ignore") if o else ""
            nhans.append(re.sub(r'\x1b.', '', nhan))
        return nhans

    def get_danhsachmucnhiemvu(self):
        # Các mục của cửa sổ nhiệm vụ ([thông tin game] + TG_NHIEMVU) theo thứ tự hiển thị: [(tên, mô tả)]. Tên mục ở + 0x90, mô tả cùng
        # thứ tự ở + 0x860 (mỗi mục 1 con trỏ, hết danh sách là con trỏ 0); mục cha (vd "Nhiệm Vụ Sư Môn") không có mô tả, mục con thụt
        # đầu dòng. Máy chủ tự gửi lại khi nhiệm vụ đổi, cửa sổ không cần đang mở; nhưng chưa mở bảng nhiệm vụ lần nào (con trỏ 0) thì
        # không có dữ liệu -> None (không đọc được, khác với [] là không có nhiệm vụ nào)
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        x = read_int(self.tientrinh, x + DC.TG_NHIEMVU) if x else 0
        if not x:
            return None
        sotoida = 64
        controtens = struct.unpack("<%dI" % sotoida, read_bytes(self.tientrinh, x + 0x90, sotoida * 4))
        contromotas = struct.unpack("<%dI" % sotoida, read_bytes(self.tientrinh, x + 0x860, sotoida * 4))
        mucs = []
        for controten, contromota in zip(controtens, contromotas):
            if not controten:
                break
            ten = read_chuoi(self.tientrinh, controten, 0x80).decode("utf-8", "ignore")
            mota = read_chuoi(self.tientrinh, contromota, 0x1000).decode("utf-8", "ignore") if contromota else ""
            mucs.append((re.sub(r"\x1b.", "", ten), mota))
        return mucs

    def get_is_quairiengnguoikhac(self, ten):
        # Quái nhiệm vụ riêng mang ID người chơi trong ngoặc ("Thủ Lĩnh Thích Khách (29)", "Cuồng Đồ (30)"): chỉ chủ của nó đánh được,
        # con mang ID người khác thì bỏ qua
        m = re.search(r"\(\s*(\d+)\s*\)", ten or "")
        return bool(m) and int(m.group(1)) != self.get_idnguoichoi()

    def get_manhiemvu(self, tenmuccha):
        # Mã của mục con đầu tiên dưới mục cha tenmuccha ("Nhiệm Vụ Sư Môn") để gửi "quest intro <a> <b> <c>" (xin mô tả, như bấm vào dòng
        # đó; mẫu lệnh trong xq.exe, cùng mã với nút "Hủy Bỏ" ở 0x4BADBB): a = [Q+0x1854], b / c = word [Q+dòng*4+0x1858] / [+0x185A],
        # dòng tính như danh sách tên +0x90 (sư môn: 1 1000 <loại>, Thu Thập 5, Truy Bắt Thích Khách 13). -> (a, b, c) hoặc None.
        # a là thẻ đang chọn của cửa sổ (1 Giang Hồ, 2 Cốt Truyện "quest intro 2 8000 ..."). Sư Môn / Danh Vọng / Sư Gia đều ở thẻ
        # Giang Hồ nên luôn gửi a = THENHIEMVUGIANGHO: đăng nhập lại mà cửa sổ còn ở thẻ Cốt Truyện thì [Q+0x1854] = 2, gửi
        # "quest intro 2 1000 4" 4 lần không ra mô tả, sư môn dừng "chưa biết làm nhiệm vụ này: Mua Sắm" (acc 364, 2026-11-05 21:05);
        # bấm tay ở thẻ Giang Hồ game gửi "quest intro 1 1000 4"
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        x = read_int(self.tientrinh, x + DC.TG_NHIEMVU) if x else 0
        if not x:
            return None
        is_trongmuc = False
        for dong in range(64):
            controten = read_int(self.tientrinh, x + 0x90 + dong * 4)
            if not controten:
                return None
            ten = re.sub(r"\x1b.", "", read_chuoi(self.tientrinh, controten, 0x80).decode("utf-8", "ignore"))
            if not ten.startswith(" "):
                is_trongmuc = ten.strip().lower() == tenmuccha.strip().lower()
                continue
            if is_trongmuc:
                nhom, loai = struct.unpack("<hh", read_bytes(self.tientrinh, x + 0x1858 + dong * 4, 4))
                return THENHIEMVUGIANGHO, nhom, loai
        return None

    def get_cuahangdangmo(self):
        # Cửa hàng NPC đang / vừa mở ([thông tin game] + TG_CUAHANG, giữ nguyên sau khi đóng tới lần mở cửa hàng khác):
        # {"is_danghien": cửa sổ đang hiện (+ 0x108), "hang": [(ô, giá, tên)]}; hàng ở + 0x7D78, mỗi món 0x58 byte: ô + 4 (0 = hết), giá + 8, tên + 0x12.
        # Mua: "buy <id NPC># <ô> <số lượng> <giá>"
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        x = read_int(self.tientrinh, x + DC.TG_CUAHANG) if x else 0
        if not x:
            return None
        somon = 60
        dulieu = read_bytes(self.tientrinh, x + 0x7D78, somon * 0x58)
        hang = []
        for k in range(somon):
            mon = dulieu[k * 0x58:(k + 1) * 0x58]
            o, gia = struct.unpack("<ii", mon[4:12])
            if o <= 0:
                break
            hang.append((o, gia, mon[0x12:].split(b"\0")[0].decode("utf-8", "ignore")))
        return {"is_danghien": read_boolean(self.tientrinh, x + 0x108), "hang": hang}

    def get_motahangcuahang(self, o):
        # Mô tả món ở ô o của cửa hàng (như rê chuột lên món): game lưu theo số ô trong cấu trúc cửa hàng + 0x164C + (ô - 1) * 0x44C (tên ô
        # ở + 0x1AC + (ô - 1) * 0xC8), nạp bằng lệnh "desc <id NPC># <ô>" (mẫu xq + 0x19D8E4, cạnh "buy"). Còn mô tả cũ của cửa hàng mở
        # trước nên nơi gọi phải so dòng tên. Đo 2026-10-31 trên 4 cửa hàng. -> chuỗi (bỏ mã màu \x1b + 1 ký tự) hoặc ""
        if not 1 <= o <= 60:
            return ""
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        x = read_int(self.tientrinh, x + DC.TG_CUAHANG) if x else 0
        if not x:
            return ""
        mota = read_bytes(self.tientrinh, x + 0x164C + (o - 1) * 0x44C, 0x44C).split(b"\0")[0].decode("utf-8", "ignore")
        return re.sub(r"\x1b.", "", mota)

    def action_dongcuasocuahang(self):
        # Đóng cửa sổ cửa hàng như bấm X (cờ đang hiện + 0x108, như cửa sổ kho); danh sách hàng vẫn còn trong bộ nhớ
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        cuahang = read_int(self.tientrinh, x + DC.TG_CUAHANG) if x else 0
        if cuahang and read_boolean(self.tientrinh, cuahang + 0x108):
            write_boolean(self.tientrinh, cuahang + 0x108, False)

    def set_is_danghiencuasotuychon(self, is_danghiencuasotuychon):
        # Ẩn / hiện bằng hàm của game vtable[1](cờ) (xq + 0xCB170): ghi + 0x1E38 rồi cập nhật danh sách cửa sổ (xq + 0x90FA0). Chỉ ghi
        # + 0x1E38 thì menu ẩn mà vẫn đứng đầu danh sách cửa sổ, chặn chuột (không cuộn được khung trò chuyện)
        if self.get_is_danghiencuasotuychon() != is_danghiencuasotuychon:
            x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
            if x and read_int(self.tientrinh, x + DC.TG_CUASOTUYCHON):
                self._goivtableanhien(DC.TG_CUASOTUYCHON, is_danghiencuasotuychon)

    def _goivtableanhien(self, vitritg, is_hien):
        # Gọi vtable[1](is_hien) (ẩn / hiện + cập nhật danh sách cửa sổ) của cửa sổ có con trỏ ở [thông tin game] + vitritg, bằng luồng
        # trong game. Đoạn mã mỗi (vitritg, is_hien) cấp phát 1 lần
        khoa = (vitritg, bool(is_hien))
        diachi = self._diachivtableanhien_map.get(khoa)
        if not diachi:
            asm_script = f"""
                mov eax, dword ptr [{hex(self.diachixq + DC.THONGTINGAME)}]
                test eax, eax
                je ketthuc
                mov ecx, dword ptr [eax + {hex(vitritg)}]
                test ecx, ecx
                je ketthuc
                push {1 if is_hien else 0}
                mov eax, dword ptr [ecx]
                call dword ptr [eax + 4]
            ketthuc:
                ret
            """
            encoding, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(asm_script)
            if not encoding:
                return
            diachi = self.tientrinh.allocate(64)
            write_bytes(self.tientrinh, diachi, bytes(encoding), len(encoding))
            self._diachivtableanhien_map[khoa] = diachi
        self.tientrinh.start_thread(diachi)

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
        # Hàm giữ toàn bộ trạng thái A* trong đối tượng (bộ đếm nút + 0x1E000, danh sách mở + 0x40FBC, lưới chi phí + 0x3C008, gốc
        # + 0x54FC8...), vật cản đọc từ lưới bản đồ trong [thông tin game]. Game tự gọi hàm này ở 12 chỗ trên luồng chính (click, tiếp
        # cận, tự động tìm đường) => gọi từ luồng ngoài trên đối tượng của game là 2 luồng cùng sửa 1 danh sách mở, danh sách thành
        # vòng và luồng chính lặp mãi (cửa sổ đơ, hay gặp ở chỗ vật cản vì tìm lâu, lại xen kẽ với tự động tìm đường). Nên dùng đối
        # tượng riêng cấp trong tiến trình game, hàm tự khởi tạo lại mỗi lần gọi
        if not self._diachitimduongcucbo:
            self._doituongtimduongcucbo = self.tientrinh.allocate(KICHTHUOCDOITUONGTIMDUONGCUCBO)
            vung = self.tientrinh.allocate(512)
            self._dulieutimduongcucbo, self._buftimduongcucbo = vung + 0x80, vung + 0x100
            dulieu = self._dulieutimduongcucbo
            ma = f"""
                mov eax, dword ptr [{hex(self.diachixq + DC.THONGTINGAME)}]
                test eax, eax
                je ketthuc
                mov ecx, {hex(self._doituongtimduongcucbo)}
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
            # pymem không đóng handle luồng, gọi rất nhiều lần (đứng ở vật cản gọi liên tục) thì rò handle
            ctypes.windll.kernel32.CloseHandle(self.tientrinh.start_thread(self._diachitimduongcucbo))
            return read_bytes(self.tientrinh, self._buftimduongcucbo, 100).split(b"\0")[0] or None

    def get_is_cotimduongcucbo(self):
        # Client đã tạo đối tượng tìm đường cục bộ chưa (tạo khi click di chuyển lần đầu)
        thongtingame = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        return bool(thongtingame and read_int(self.tientrinh, thongtingame + DC.TG_TIMDUONGCUCBO))

    def _get_luoivatcan(self, x1, y1, x2, y2):
        # Lưới vật cản vùng [x1, x2] x [y1, y2] của bản đồ hiện tại: luoi[x - x1][y - y1], 0 đi được, khác 0 vật cản (ngoài bản đồ = 1).
        # Cùng x thì các y nằm liền nhau => mỗi x 1 lần đọc. None: chưa có thông tin game / đang tải bản đồ
        thongtingame = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not thongtingame:
            return None
        rong, cao = struct.unpack("<ii", read_bytes(self.tientrinh, thongtingame + OFFSET_KICHTHUOCBANDO, 8))
        if not (0 < rong <= SOCOTLUOIVATCAN and 0 < cao <= SOCOTLUOIVATCAN):
            return None
        ya, yb = max(y1, 0), min(y2, cao - 1)
        luoi = []
        for x in range(x1, x2 + 1):
            hang = [1] * (y2 - y1 + 1)
            if 0 <= x < rong and ya <= yb:
                dulieu = read_bytes(self.tientrinh, thongtingame + OFFSET_LUOIVATCAN + 4 * (SOCOTLUOIVATCAN * x + ya), 4 * (yb - ya + 1))
                hang[ya - y1:yb - y1 + 1] = [o & 3 for o in struct.unpack(f"<{yb - ya + 1}I", dulieu)]
            luoi.append(hang)
        return luoi

    def get_luoivatcanvung(self, x1, y1, x2, y2):
        # Lưới vật cản vùng [x1, x2] x [y1, y2]: luoi[x - x1][y - y1], khác 0 là vật cản. None khi chưa đọc được
        return self._get_luoivatcan(int(x1), int(y1), int(x2), int(y2))

    def get_luoivatcanbando(self):
        # Cả lưới vật cản của bản đồ hiện tại: luoi[x][y] (mỗi cột x 1 lần đọc, bản đồ 304 x 228 là 304 lần)
        thongtingame = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not thongtingame:
            return None
        rong, cao = struct.unpack("<ii", read_bytes(self.tientrinh, thongtingame + OFFSET_KICHTHUOCBANDO, 8))
        return self._get_luoivatcan(0, 0, rong - 1, cao - 1)

    def get_is_vatcan(self, x, y):
        luoi = self._get_luoivatcan(round(x), round(y), round(x), round(y))
        return bool(luoi and luoi[0][0])

    def get_is_doanthangcovatcan(self, x1, y1, x2, y2):
        # Đoạn thẳng (x1, y1) -> (x2, y2) có đi qua ô vật cản không (lấy mẫu mỗi 0.5 ô, bỏ ô đầu và ô cuối như _chonhuonglui). Chiêu lướt
        # (Khai Thiên Tịch Địa, Lưu Tinh Truy Mạng) không lướt được qua vật cản. Không đọc được lưới thì coi như không có
        xa, ya, xb, yb = round(x1), round(y1), round(x2), round(y2)
        ox, oy = min(xa, xb), min(ya, yb)
        luoi = self._get_luoivatcan(ox, oy, max(xa, xb), max(ya, yb))
        if not luoi:
            return False
        sobuoc = max(1, math.ceil(math.dist((x1, y1), (x2, y2)) * 2))
        for i in range(1, sobuoc):
            x, y = round(x1 + (x2 - x1) * i / sobuoc), round(y1 + (y2 - y1) * i / sobuoc)
            if (x, y) not in ((xa, ya), (xb, yb)) and luoi[x - ox][y - oy]:
                return True
        return False

    def get_oditduocganhat(self, x, y, bankinhtoida = BANKINHKEODICH):
        # Đích (x, y) của bản đồ hiện tại rơi vào vật cản (toạ độ nhiệm vụ / NPC lệch vào tường, nước...) thì trả ô đi được gần nhất trong
        # bankinhtoida ô (cùng khoảng cách thì ô gần mình hơn, kẻo lấy ô bên kia tường); đi được / không thấy ô nào thì giữ nguyên.
        # Kết quả giữ cố định theo (bản đồ, x, y): đích không nhảy qua lại khi mình di chuyển
        x, y = round(x), round(y)
        luoi = self._get_luoivatcan(x, y, x, y)
        if not luoi or not luoi[0][0]:
            return x, y
        khoa = (self.get_idbandohientai(), x, y)
        if khoa in self._oditduoc_cache:
            return self._oditduoc_cache[khoa]
        r = bankinhtoida
        luoi = self._get_luoivatcan(x - r, y - r, x + r, y + r)
        if not luoi:
            return x, y
        toado = self.get_toado()
        tot = None
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if luoi[dx + r][dy + r]:
                    continue
                diem = (round(math.hypot(dx, dy)), math.dist((x + dx, y + dy), toado))
                if tot is None or diem < tot[0]:
                    tot = (diem, (x + dx, y + dy))
        ketqua = tot[1] if tot else (x, y)
        if len(self._oditduoc_cache) > 512:
            self._oditduoc_cache.clear()
        self._oditduoc_cache[khoa] = ketqua
        if IS_LOGDICHUYEN and ketqua != (x, y):
            self._inlog(f"[KÉO ĐÍCH] {(x, y)} là vật cản -> ô đi được {ketqua}")
        return ketqua

    @staticmethod
    def _get_diemcuoichuoihuong(x, y, chuoihuong):
        for kytu in chuoihuong.decode("latin1"):
            dx, dy = HUONGTIMDUONG_MAP.get(kytu, (0, 0))
            x, y = x + dx, y + dy
        return x, y

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
        x, y = self.get_oditduocganhat(dichtrongtran[0], dichtrongtran[1])
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
        # Đoạn cụt: không tới được đích thì hàm tìm đường vẫn trả chuỗi tới ô gần đích nhất (xq + 0x4B0C40) => chuỗi chưa đủ 100 bước
        # mà dừng ở ô khác đích thì coi như không ra đường: nơi gọi chuyển ngay sang tự động tìm đường của game thay vì đi tới chân
        # tường rồi đứng chờ kẹt. Nhớ đoạn cụt một lúc, kẻo mỗi lượt lại tìm đường hỏng (tốn tới 0x2800 nút) cho đúng đoạn đó
        khoadoan = (self.get_idbandohientai(), xsaptoi, ysaptoi, x, y)
        if time.time() - self._doancut_cache.get(khoadoan, 0.) < THOIGIANNHODOANCUT:
            return None
        chuoihuong = self._get_chuoihuongtimduongcucbo(xsaptoi, ysaptoi, x, y)
        if not chuoihuong:
            return None
        if len(chuoihuong) < 100 and self._get_diemcuoichuoihuong(xsaptoi, ysaptoi, chuoihuong) != (x, y):
            if len(self._doancut_cache) > 256:
                self._doancut_cache.clear()
            self._doancut_cache[khoadoan] = time.time()
            if IS_LOGDICHUYEN:
                self._inlog(f"[ĐOẠN CỤT] {(xsaptoi, ysaptoi)} -> {(x, y)} chỉ tới {self._get_diemcuoichuoihuong(xsaptoi, ysaptoi, chuoihuong)}")
            return None
        if is_dungkedich:
            chuoihuong = chuoihuong[:-1]
            if not chuoihuong:
                return False
        if sobuoctoida:
            chuoihuong = chuoihuong[:sobuoctoida]
        chuoihuong = chuoihuong[:SOBUOCCHUOIDUONGDITOIDA]
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

    def action_dikhongcatgoc(self, x2, y2, khoangcachtoida = 0., is_cabando = False, is_doancut = False,
                             sobuoctoida = None, is_dungkedich = False, thoigiantinhlai = 0.):
        # sobuoctoida / is_dungkedich / thoigiantinhlai: như action_dichuyenoo, cho tiếp cận cận chiến kiểu client (_tiepcancanchien) trên
        # bản đồ có chỗ giật: trước đây tấn công ở đó gọi thẳng hàm này với đích = ô quái => đi cả chuỗi tới đúng ô quái, không dừng kề, chạy
        # sát rạt / xuyên qua (log 347 2026-11-12: 0 dòng TIẾP CẬN CẬN CHIẾN, 598 dòng ĐI KHÔNG CẮT GÓC). is_dungkedich: không ra đường
        # thì trả None (nơi gọi dùng tìm đường của game) thay vì đi theo ô thường tới đúng ô quái
        # is_doancut: gọi từ _dicabandokhidoancut (tìm đường cục bộ của client ra đoạn cụt trên bản đồ thường): không học vật cản (lag
        # khoá tại chỗ dễ học nhầm), không ra đường thì trả None để nơi gọi dùng tự động tìm đường của game (không lùi về đi theo ô)
        # is_cabando: tìm đường trên cả bản đồ (đi vòng vách đá dài tới quái tầng bên kia). Đích (quái lang thang) nhích không quá
        # LECHDICHCABANDO ô thì đi hết chuỗi đang có rồi mới tìm lại (mỗi lần tìm cả bản đồ tốn tới ~1s)
        # Đi tới (x2, y2) cùng bản đồ theo đường bot tự tìm trên lưới vật cản, KHÔNG đi chéo qua khe giữa 2 vật cản chỉ chạm góc (chéo chỉ
        # khi 2 ô kề đều trống), rồi ghi chuỗi hướng như action_dichuyenoo. Chu Quốc có rào xếp chéo thành khối 2x2 chạm góc (quanh Từ Phúc
        # (345, 159)): tìm đường của client / game lách chéo qua khe đó mà máy chủ không cho đi => húc rào giật giật. Không tìm được đường
        # thì đi như action_dioochangtoidich. -> như action_dichuyenoo
        if self._is_vohieuhoadichuyen or self.get_is_khoavankhitrieuhoi() or self.get_is_dangxuatchieu():
            return False
        if not self._get_is_duocbatdaudichuyen():
            return False
        if khoangcachtoida < 1:
            x2, y2 = self.get_oditduocganhat(x2, y2)
        diachinhanvat = self.get_diachicosothongtinnhanvat1()
        if not diachinhanvat:
            return None
        x1, y1 = struct.unpack("<ii", read_bytes(self.tientrinh, diachinhanvat + 0x18, 8))
        if math.dist((x1, y1), (x2, y2)) <= max(1., khoangcachtoida):
            self._kettiendokhongcatgoc = None
            return False
        now = time.time()
        if not is_doancut and self._hockhongcatgoc((x1, y1), now):
            return True
        # Đang đi chuỗi tới đúng đích này thì để client đi tiếp (hết chuỗi 99 bước thì lần gọi sau tìm tiếp). Đích nhích ít (theo sau người
        # đang đi) thì 1.5s mới tìm lại: ghi lại chuỗi mỗi lượt làm đứt nhịp gửi "go", đi khựng
        if thoigiantinhlai:
            # Tiếp cận kiểu client: ghi đoạn mới mỗi thoigiantinhlai giây kể cả đích không đổi (đoạn chỉ sobuoctoida bước)
            if self.get_idlenhdichuyen() and now - self._thoidiemdichuyengannhat < thoigiantinhlai:
                return True
        elif self._dichkhongcatgoc and self.get_idlenhdichuyen() and (self._dichkhongcatgoc == (x2, y2) or (
                math.dist(self._dichkhongcatgoc, (x2, y2)) <= 3 and now - self._thoidiemdichuyengannhat < 1.5)
                or ((is_cabando or self._is_duongcabando) and math.dist(self._dichkhongcatgoc, (x2, y2)) <= LECHDICHCABANDO)):
            return True
        # Đoạn vừa thấy không có đường (cả khung ±25 ô lẫn cả bản đồ): khỏi tìm lại mỗi lượt (0.1s), đi như action_dioochangtoidich
        khoadoan = (self.get_idbandohientai(), x1, y1, x2, y2)
        if now - self._khongduongkhongcatgoc_cache.get(khoadoan, 0.) < THOIGIANNHOKHONGDUONGCABANDO:
            return None if is_doancut or is_dungkedich else self.action_dioochangtoidich(x2, y2, khoangcachtoida)
        if is_cabando:
            chuoihuong = self._timduongcabando(x1, y1, x2, y2, khoangcachtoida)
        else:
            chuoihuong = self._timduongkhongcatgoc(x1, y1, x2, y2, khoangcachtoida)
        self._is_duongcabando = is_cabando
        if not chuoihuong and not is_cabando:
            # Khung ±25 ô không ra đường (vách đá dài Mã Lăng Đạo: điểm lộ trình / quái bên kia vách, log 418 2026-11-06 "(139, 125) ->
            # (164, 146) không ra đường" mỗi 0.1s, tìm đường của game chạy tới chân vách rồi "Hoàn tất tự động tìm đường"): tìm cả bản đồ
            chuoihuong = self._timduongcabando(x1, y1, x2, y2, khoangcachtoida)
            self._is_duongcabando = bool(chuoihuong)
            if chuoihuong and IS_LOGDICHUYEN:
                self._inlog(f"[ĐI KHÔNG CẮT GÓC] {(x1, y1)} -> {(x2, y2)} khung ±25 ô không ra đường, cả bản đồ {len(chuoihuong)} bước")
        # A* không né vòng quanh cổng (VUNGCAM_MAP): đường vòng cả bản đồ trên bản đồ thường mà đi qua cổng là sang bản đồ khác => bỏ, để
        # tự động tìm đường của game như cũ
        if chuoihuong and is_doancut and self.is_tranhvungcam and self._is_chuoihuongquavungcam(x1, y1, chuoihuong):
            if IS_LOGDICHUYEN:
                self._inlog(f"[ĐOẠN CỤT CẢ BẢN ĐỒ] {(x1, y1)} -> {(x2, y2)}: đường {len(chuoihuong)} bước đi qua vùng cổng, bỏ")
            chuoihuong = None
        if not chuoihuong:
            if len(self._khongduongkhongcatgoc_cache) > 256:
                self._khongduongkhongcatgoc_cache.clear()
            self._khongduongkhongcatgoc_cache[khoadoan] = now
        if chuoihuong and is_dungkedich:
            # Bỏ bước cuối (ô quái đang đứng), dừng ở ô kề
            chuoihuong = chuoihuong[:-1]
            if not chuoihuong:
                return False
        if chuoihuong and sobuoctoida:
            chuoihuong = chuoihuong[:sobuoctoida]
        if chuoihuong:
            self._duongkhongcatgoc = [(x1, y1)]
            for kytu in chuoihuong[:SOBUOCCHUOIDUONGDITOIDA].decode():
                dx, dy = HUONGTIMDUONG_MAP[kytu]
                self._duongkhongcatgoc.append((self._duongkhongcatgoc[-1][0] + dx, self._duongkhongcatgoc[-1][1] + dy))
        if not chuoihuong:
            if is_dungkedich:
                return None
            if is_doancut:
                if IS_LOGDICHUYEN:
                    self._inlog(f"[ĐOẠN CỤT CẢ BẢN ĐỒ] {(x1, y1)} -> {(x2, y2)} không ra đường, dùng tự động tìm đường của game")
                return None
            if IS_LOGDICHUYEN:
                self._inlog(f"[ĐI KHÔNG CẮT GÓC] {(x1, y1)} -> {(x2, y2)} không ra đường, đi theo ô thường")
            return self.action_dioochangtoidich(x2, y2, khoangcachtoida)
        chuoihuong = chuoihuong[:SOBUOCCHUOIDUONGDITOIDA]
        self.action_ngungtudongtimduong()
        self._dichkhongcatgoc = (x2, y2)
        self._dichdioogannhat = None
        khoidieukhien = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if khoidieukhien:
            write_bytes(self.tientrinh, khoidieukhien + DC.KDK_DICHCLICK, bytes(8), 8)
        write_bytes(self.tientrinh, self.diachixq + DC.CHUOIDUONGDI, b"\0" + chuoihuong + bytes(99 - len(chuoihuong)), 100)
        self.set_idlenhdichuyen(1)
        self._thoidiemdichuyengannhat = time.time()
        self._thoidiemboquadichuyencungtoadogannhat = time.time()
        # Tiếp cận cận chiến ghi đoạn mỗi 0.25s, nơi gọi tự log khi đổi đích
        if IS_LOGDICHUYEN and not is_dungkedich:
            self._inlog(f"[ĐI KHÔNG CẮT GÓC] {(x1, y1)} -> {(x2, y2)}: {len(chuoihuong)} bước")
        return True

    def _is_chuoihuongquavungcam(self, x, y, chuoihuong):
        # Có ô nào trên chuỗi hướng (bắt đầu từ (x, y), không tính ô đứng) nằm trong vùng cấm / vòng quanh cổng của bản đồ hiện tại
        for kytu in chuoihuong.decode("latin1"):
            dx, dy = HUONGTIMDUONG_MAP.get(kytu, (0, 0))
            x, y = x + dx, y + dy
            if self.get_is_duongdicatvungcam(x, y, x, y):
                return True
        return False

    def _dicabandokhidoancut(self, x, y, khoangcachtoida = 0.):
        # Tìm đường cục bộ của client (~50-100 bước) không ra đường / ra đoạn cụt (mê cung, vách dài: chạy tới ngõ cụt rồi quay lại, log 342
        # Khốn Ma Trận 1 2026-11-09): đi bằng A* cả bản đồ của bot thay vì tự động tìm đường của game. Bản đồ nào cũng dùng được, không phải
        # thêm tay vào BANDOBOTTUTIMDUONGs. None: cả bản đồ cũng không ra đường (nơi gọi dùng tự động tìm đường của game như cũ)
        return self.action_dikhongcatgoc(round(x), round(y), khoangcachtoida, is_cabando = True, is_doancut = True)

    def _layokhuvuccam(self, xa, ya, xb, yb):
        # Các ô trong vùng [xa, xb] x [ya, yb] thuộc khu vực cấm khai tay của bản đồ hiện tại (KHUVUCCAM_MAP, không tính vòng quanh cổng)
        return self._layotrongvung(KHUVUCCAM_MAP.get(self.get_idbandohientai(), ()), xa, ya, xb, yb)

    @staticmethod
    def _layotrongvung(danhsachvung, xa, ya, xb, yb):
        # Các ô trong vùng [xa, xb] x [ya, yb] nằm trong danh sách vùng {"type": "circle"/"line", ...} (KHUVUCCAM_MAP, VUNGCAM_MAP)
        os_ = set()
        for vung in danhsachvung:
            if vung["type"] == "circle":
                r = vung["r"]
                for x in range(max(xa, math.floor(vung["x"] - r)), min(xb, math.ceil(vung["x"] + r)) + 1):
                    for y in range(max(ya, math.floor(vung["y"] - r)), min(yb, math.ceil(vung["y"] + r)) + 1):
                        if math.dist((x, y), (vung["x"], vung["y"])) <= r:
                            os_.add((x, y))
            elif vung["type"] == "line":
                ax, ay, bx, by, r = vung["x1"], vung["y1"], vung["x2"], vung["y2"], vung["r"]
                vx, vy = bx - ax, by - ay
                v2 = vx * vx + vy * vy
                for x in range(max(xa, math.floor(min(ax, bx) - r)), min(xb, math.ceil(max(ax, bx) + r)) + 1):
                    for y in range(max(ya, math.floor(min(ay, by) - r)), min(yb, math.ceil(max(ay, by) + r)) + 1):
                        u = max(0., min(1., ((x - ax) * vx + (y - ay) * vy) / v2)) if v2 else 0.
                        if math.dist((x, y), (ax + u * vx, ay + u * vy)) <= r:
                            os_.add((x, y))
        return os_

    def _hockhongcatgoc(self, sap, now):
        # Máy chủ chặn ô mà lưới client ghi đi được (rào cố ý làm kẹt): đang đi liên tục bằng action_dikhongcatgoc (lần gọi trước cách chưa
        # tới GIANCACHGOIKHONGCATGOC giây: không bị đánh quái / nhặt đồ chen giữa) mà ô thật (get_toado) đứng yên quá THOIGIANKETKHONGCATGOC
        # giây, VÀ trong lúc đó ô "sắp tới" của client (+ 0x18) lệch khỏi ô thật (client bước rồi bị máy chủ kéo về, giật giật) thì ghi ô kế
        # tiếp theo hướng lệch là vật cản nghi ngờ (_ghivatcanhoc: chặn tạm trong bộ nhớ, không ghi file), tìm đường lại né nó.
        # Chỉ đứng yên mà không lệch (đang ra chiêu / đánh quái) thì không học: từng học nhầm gần 50 ô ở Kênh Trịnh Quốc 1 lúc gom quái.
        # -> True: vừa học / đang chờ client về đúng ô thật (lượt này không ghi chuỗi)
        that = tuple(round(v) for v in self.get_toado())
        if self.get_is_vuasuagiomaychu():
            # Vừa sửa giờ máy chủ sau lag: bị kéo về là do lệnh go mang giờ cũ, không phải vật cản => không học, xoá tiến độ dở
            self._lichsukhongcatgoc.clear()
            self._kettiendokhongcatgoc = [that, now, None]
            self._lucgoikhongcatgoc = now
            return False
        tiendo = self._kettiendokhongcatgoc
        is_lientuc = now - self._lucgoikhongcatgoc <= GIANCACHGOIKHONGCATGOC
        self._lucgoikhongcatgoc = now
        # Giật về ô mốc: máy chủ chỉ nhận tới ô mốc, từ chối bước kế, nhưng client kịp đi 1-2 bước rồi mới bị kéo về đúng ô mốc (người dùng tả
        # "toạ độ thay đổi, đi được 1 2 bước lại giật lại đúng vị trí đó"; ô thật có đổi nên cách đứng yên ở dưới không bắt được). Quay về 1 ô
        # từng đứng trong THOIGIANGIATKHONGCATGOC giây (sau khi đã đi khỏi) là 1 lần giật, SOLANGIATKHONGCATGOC lần cùng (ô mốc, bước đầu ra
        # khỏi mốc) trong 10s thì ghi bước đầu đó là vật cản
        lichsu = self._lichsukhongcatgoc
        if not is_lientuc:
            lichsu.clear()
        if not lichsu or lichsu[-1][1] != that:
            buocdau = None
            for i in range(len(lichsu) - 2, -1, -1):
                if now - lichsu[i][0] > THOIGIANGIATKHONGCATGOC:
                    break
                if lichsu[i][1] == that:
                    buocdau = lichsu[i + 1][1]
                    break
            lichsu.append((now, that))
            del lichsu[:-20]
            if buocdau and max(abs(buocdau[0] - that[0]), abs(buocdau[1] - that[1])) == 1 and now - self._lucvuahockhongcatgoc >= 1.:
                khoa = (that, buocdau)
                lans = [l for l in self._giatkhongcatgoc.get(khoa, []) if now - l <= 10.] + [now]
                self._giatkhongcatgoc[khoa] = lans
                if len(self._giatkhongcatgoc) > 64:
                    self._giatkhongcatgoc = {khoa: lans}
                if len(lans) >= SOLANGIATKHONGCATGOC:
                    self._giatkhongcatgoc.pop(khoa, None)
                    lichsu[:] = [(now, that)]
                    self._kettiendokhongcatgoc = [that, now, None]
                    return self._ghivatcanhoc(that, buocdau, f"bị giật về {that} {len(lans)} lần khi bước sang")
        if not tiendo or tiendo[0] != that or not is_lientuc:
            self._kettiendokhongcatgoc = [that, now, None]
            return False
        if now - self._lucvuahockhongcatgoc < 1.:
            # Vừa học: chờ client nhận lại ô thật rồi mới tìm đường từ đó
            return sap != that
        if sap != that and max(abs(sap[0] - that[0]), abs(sap[1] - that[1])) <= 3:
            tiendo[2] = (that[0] + (sap[0] > that[0]) - (sap[0] < that[0]), that[1] + (sap[1] > that[1]) - (sap[1] < that[1]))
        if now - tiendo[1] < THOIGIANKETKHONGCATGOC or not self._dichkhongcatgoc:
            return False
        if not tiendo[2]:
            # Client không bước ra khỏi ô (ô "sắp tới" luôn = ô thật) nên không biết lệch về đâu: Thỏ ở Yên Quốc (206, 241) cạnh Bảo Thạch
            # Thương Nhân 2026-11-12 02:51 gửi "go 206,241 88" 13s liền không nhích. Đứng quá THOIGIANKETTAMCHAN giây thì chặn tạm bước đầu
            # của đường đang đi (chỉ trong bộ nhớ, THOIGIANTAMCHAN giây, không ghi vatcanhoc.json: có thể là NPC / người chơi đứng chắn)
            duong = self._duongkhongcatgoc
            if now - tiendo[1] < THOIGIANKETTAMCHAN or len(duong) < 2 or duong[0] != that:
                return False
            ke = duong[1]
            tiendo[1] = now
            idbando = self.get_idbandohientai()
            if len(self._tamchankhongcatgoc) > 64:
                self._tamchankhongcatgoc.clear()
            self._tamchankhongcatgoc[(idbando, ke)] = now
            self._dichkhongcatgoc = None
            self._inlog(f"[ĐI KHÔNG CẮT GÓC] Ở {that} đứng {THOIGIANKETTAMCHAN:.0f}s không bước sang {ke} được: chặn tạm {ke} "
                        f"{THOIGIANTAMCHAN:.0f}s (NPC / người đứng chắn?), tìm đường khác")
            return False
        ke = tiendo[2]
        tiendo[1], tiendo[2] = now, None
        return self._ghivatcanhoc(that, ke, f"đứng {THOIGIANKETKHONGCATGOC:.1f}s không qua được")

    def _ghivatcanhoc(self, that, ke, lydo):
        # Không ghi vatcanhoc.json nữa (người dùng 2026-11-12): tự học nhầm rất nhiều (Kênh Trịnh Quốc 1 340 ô, Tề Quốc 85 ô, Tân Thủ Thôn
        # 17 ô...) làm bản đồ đó bị coi là có chỗ giật => mọi kiểu đi đổi sang A* của bot. Chỉ chặn tạm trong bộ nhớ THOIGIANTAMCHAN giây
        # để thoát kẹt lúc đó và log [NGHI VẬT CẢN]; vật cản thật người dùng báo rồi ghi tay (vatcanhoc.json / KHUVUCCAM_MAP)
        self._dichkhongcatgoc = None
        idbando = self.get_idbandohientai()
        now = time.time()
        if len(self._tamchankhongcatgoc) > 64:
            self._tamchankhongcatgoc.clear()
        self._tamchankhongcatgoc[(idbando, tuple(ke))] = now
        self._lucvuahockhongcatgoc = now
        self._inlog(f"[NGHI VẬT CẢN] Bản đồ {idbando}: ở {that} {lydo} {tuple(ke)} (máy chủ chặn?): chặn tạm {THOIGIANTAMCHAN:.0f}s, "
                    f"tìm đường khác")
        return True

    def get_sobuocduongtoi(self, x2, y2, khoangcachtoida = 0., is_cabando = False):
        # Số bước đi bộ (theo lưới vật cản + ô học được, như action_dikhongcatgoc) từ chỗ mình tới cách (x2, y2) không quá khoangcachtoida.
        # is_cabando: tìm trên cả bản đồ thay vì khung ±25 ô quanh 2 điểm (chậm hơn, ~0.1-1s).
        # 0: đã trong tầm, None: không có đường (bị vật cản bao kín / khác vùng liên thông) / chưa đọc được
        diachinhanvat = self.get_diachicosothongtinnhanvat1()
        if not diachinhanvat:
            return None
        x1, y1 = struct.unpack("<ii", read_bytes(self.tientrinh, diachinhanvat + 0x18, 8))
        x2, y2 = round(x2), round(y2)
        if math.dist((x1, y1), (x2, y2)) <= max(1., khoangcachtoida):
            return 0
        if is_cabando:
            chuoihuong = self._timduongcabando(x1, y1, x2, y2, max(1., khoangcachtoida))
        else:
            chuoihuong = self._timduongkhongcatgoc(x1, y1, x2, y2, max(1., khoangcachtoida))
        return len(chuoihuong) if chuoihuong else None

    def _get_luoicabando(self):
        # Lưới vật cản cả bản đồ hiện tại (luoi[x][y]), nhớ THOIGIANNHOLUOICABANDO giây theo bản đồ
        idbando = self.get_idbandohientai()
        cache = self._luoicabando_cache
        if cache and cache[0] == idbando and time.time() - cache[1] < THOIGIANNHOLUOICABANDO:
            return cache[2]
        luoi = self.get_luoivatcanbando()
        # Lưới không đổi thì giữ đối tượng cũ: nhãn vùng liên thông (_get_nhanvunglienthong) khoá theo đúng đối tượng lưới
        if luoi and cache and cache[0] == idbando and cache[2] == luoi:
            luoi = cache[2]
        self._luoicabando_cache = (idbando, time.time(), luoi) if luoi else None
        return luoi

    def _get_nhanvunglienthong(self, is_chocatgoc):
        # Đánh số vùng liên thông của lưới cả bản đồ (chỉ theo lưới client, không tính ô chặn tạm: chặn tạm chỉ bớt đường, khác vùng trên
        # lưới thì chắc chắn không có đường). Không cắt góc: chéo chỉ khi 2 ô kề đều trống => liên thông 4 hướng; cho cắt góc: 8 hướng.
        # Đo 2026-11-12 trên _internal/luoi_*.json: A* cả bản đồ không có đường (đích ở vùng khác) phải quét hết 25.000-35.000 ô, 230-290 ms
        # mỗi lần, cả lần cho cắt góc là 400-510 ms. -> (luoi, nhan[x * cao + y], cao): nhãn 0 = vật cản; hoặc (None, None, 0)
        luoi = self._get_luoicabando()
        if not luoi:
            return None, None, 0
        cache = self._vunglienthong_cache.get(is_chocatgoc)
        if cache and cache[0] is luoi:
            return cache
        batdau = time.time()
        rong, cao = len(luoi), len(luoi[0])
        nhan = [0] * (rong * cao)
        if is_chocatgoc:
            lechs = (-cao - 1, -cao, -cao + 1, -1, 1, cao - 1, cao, cao + 1)
        else:
            lechs = (-cao, -1, 1, cao)
        trong = bytearray(rong * cao)
        for x in range(rong):
            cot = luoi[x]
            for y in range(cao):
                if not cot[y]:
                    trong[x * cao + y] = 1
        sovung = 0
        for k in range(rong * cao):
            if not trong[k] or nhan[k]:
                continue
            sovung += 1
            nhan[k] = sovung
            ngan = [k]
            while ngan:
                o = ngan.pop()
                oy = o % cao
                for d in lechs:
                    n = o + d
                    # Không tràn sang cột bên cạnh khi ở mép trên / dưới
                    if n < 0 or n >= rong * cao or abs(n % cao - oy) > 1 or not trong[n] or nhan[n]:
                        continue
                    nhan[n] = sovung
                    ngan.append(n)
        ketqua = (luoi, nhan, cao)
        self._vunglienthong_cache[is_chocatgoc] = ketqua
        thoigian = time.time() - batdau
        if thoigian > THOIGIANASTARCHAM:
            self._inlog(f"[A* CHẬM] Đánh số vùng liên thông bản đồ {self.get_idbandohientai()} ({rong}x{cao}, "
                        f"{'8' if is_chocatgoc else '4'} hướng): {sovung} vùng, {thoigian * 1000:.0f} ms")
        return ketqua

    def _get_is_cungvunglienthong(self, x1, y1, x2, y2, khoangcachtoida, is_chocatgoc):
        # Từ (x1, y1) có thể tới (x2, y2) (hoặc ô cách nó không quá khoangcachtoida) trên lưới không. -> True / False / None (chưa biết)
        luoi, nhan, cao = self._get_nhanvunglienthong(is_chocatgoc)
        if not luoi:
            return None
        rong = len(luoi)

        def lay(x, y):
            return nhan[x * cao + y] if 0 <= x < rong and 0 <= y < cao else 0

        # Ô đứng có thể bị lưới ghi là vật cản (đứng mép rào): lấy vùng các ô kề
        vungdau = {lay(x1, y1)} - {0} or {lay(x1 + dx, y1 + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - {0}
        if not vungdau:
            return None
        nguong = max(0., khoangcachtoida)
        if not nguong:
            return lay(x2, y2) in vungdau
        r = int(nguong)
        return any(lay(x2 + dx, y2 + dy) in vungdau for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                   if math.hypot(dx, dy) <= nguong)

    def _timduongcabando(self, x1, y1, x2, y2, khoangcachtoida = 0.):
        # A* cả bản đồ: không cắt góc trước, không ra thì cho đi chéo qua khe 2 vật cản chạm góc (cầu thang chéo tây Mã Lăng Đạo lên tầng
        # trên, 2026-11-06: không cắt góc thì báo "khác vùng liên thông" dù có cầu thang). Vẫn không ra: ghi lưới ra file để xem
        # Khác vùng liên thông trên lưới thì khỏi chạy A* (quét hết vùng mới biết không có đường, 230-510 ms)
        if self._get_is_cungvunglienthong(x1, y1, x2, y2, khoangcachtoida, False) is not False:
            chuoihuong = self._timduongkhongcatgoc(x1, y1, x2, y2, khoangcachtoida, lechtoida = None)
            if chuoihuong:
                return chuoihuong
        chuoihuong = None
        if self._get_is_cungvunglienthong(x1, y1, x2, y2, khoangcachtoida, True) is not False:
            chuoihuong = self._timduongkhongcatgoc(x1, y1, x2, y2, khoangcachtoida, lechtoida = None, is_chocatgoc = True)
        if chuoihuong:
            self._inlog(f"[ĐI VÒNG] {(x1, y1)} -> {(x2, y2)}: phải đi chéo qua khe góc, {len(chuoihuong)} bước")
            return chuoihuong
        self._ghiluoikhongduong(x1, y1, x2, y2)
        return None

    def _ghiluoikhongduong(self, x1, y1, x2, y2):
        # Mỗi bản đồ 1 lần: ghi lưới vật cản + ô học + 2 đầu đoạn không có đường ra _internal/luoi_<bản đồ>.json để xem vì sao
        idbando = self.get_idbandohientai()
        if idbando in self._dadghiluoi:
            return
        self._dadghiluoi.add(idbando)
        luoi = self._get_luoicabando()
        if not luoi:
            return
        try:
            duongdan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_internal", f"luoi_{idbando}.json")
            with open(duongdan, "w", encoding = "utf-8") as f:
                json.dump({"tu": [x1, y1], "toi": [x2, y2], "hoc": sorted(taivatcanhoc(idbando)), "luoi": luoi}, f)
            self._inlog(f"[ĐI VÒNG] {(x1, y1)} -> {(x2, y2)} cả bản đồ không có đường: đã ghi lưới vào {duongdan}")
        except Exception as e:
            self._inlog(f"[ĐI VÒNG] Không ghi được lưới: {e}")

    def _get_onpcdung(self):
        # Set các ô NPC (lớp +0x29 == 0x80) đang đứng trong tầm màn hình, nhớ THOIGIANNHOONPC giây theo bản đồ. Lỗi đọc thì coi như không có
        idbando = self.get_idbandohientai()
        cache = self._onpc_cache
        now = time.time()
        if cache and cache[0] == idbando and now - cache[1] < THOIGIANNHOONPC:
            return cache[2]
        os_ = set()
        try:
            for diachi in self._get_diachidoituongxungquanhs():
                if self.get_is_npc(diachi):
                    os_.add(tuple(round(v) for v in self.get_toado(diachi)))
        except Exception:
            pass
        self._onpc_cache = (idbando, now, os_)
        return os_

    def _timduongbangc(self, luoi, ox, oy, rong, cao, x1, y1, x2, y2, khoangcachtoida, is_chocatgoc, hocs, cams, npcs, tamchans,
                       lechtoida, batdaudo, thoigiandocluoi):
        # Phần A* của _timduongkhongcatgoc chạy bằng astar_xq.dll. Lưới cả bản đồ đổi sang byte 1 lần mỗi đối tượng lưới (~1 ms)
        if lechtoida is None:
            cache = self._luoicabandoc_cache
            if cache and cache[0] is luoi:
                trong = cache[1]
            else:
                trong = astar_c_xq.doi_luoi(luoi)
                self._luoicabandoc_cache = (luoi, trong)
        else:
            trong = astar_c_xq.doi_luoi(luoi)
        # Ô vật cản ghi tay: đặt 0 trên bản sao (không sửa bản nhớ)
        hocstrong = [(x - ox) * cao + (y - oy) for x, y in hocs if 0 <= x - ox < rong and 0 <= y - oy < cao]
        if hocstrong:
            trong = bytearray(trong)
            for k in hocstrong:
                trong[k] = 0
        phats = {}
        for os_, phat in ((cams, PHATKHUVUCCAMKHONGCATGOC), (npcs, PHATONPCKHONGCATGOC), (tamchans, PHATTAMCHANKHONGCATGOC)):
            for x, y in os_:
                o = (x - ox, y - oy)
                phats[o] = phats.get(o, 0.) + phat
        chuoihuong, somo = astar_c_xq.timduong(trong, rong, cao, x1 - ox, y1 - oy, x2 - ox, y2 - oy, max(0., khoangcachtoida),
                                               is_chocatgoc, phats)
        thoigian = time.time() - batdaudo
        if thoigian > THOIGIANASTARCHAM:
            self._inlog(f"[A* CHẬM] (C) {'cả bản đồ' if lechtoida is None else f'khung ±{lechtoida}'}{' cho cắt góc' if is_chocatgoc else ''} "
                        f"{(x1, y1)} -> {(x2, y2)}: {thoigian * 1000:.0f} ms (đọc lưới {thoigiandocluoi * 1000:.0f} ms), mở {somo} ô, "
                        f"{'có đường' if chuoihuong else 'không có đường'}")
        return chuoihuong

    def _timduongkhongcatgoc(self, x1, y1, x2, y2, khoangcachtoida = 0., lechtoida = 25, is_chocatgoc = False):
        # A* trên lưới vật cản vùng bao 2 điểm (thêm lechtoida ô mỗi bên), 8 hướng nhưng chéo chỉ khi 2 ô kề đều trống. Tới ô cách đích
        # không quá khoangcachtoida (0: đúng ô đích) là xong. lechtoida = None: tìm trên cả bản đồ (vách đá dài ở Mã Lăng Đạo: đường vòng
        # lên tầng trên nằm ngoài khung ±25 ô). -> chuỗi hướng (bytes "1".."8", HUONGTIMDUONG_MAP) hoặc None
        # Quá THOIGIANASTARCHAM thì log [A* CHẬM] (tổng, đọc lưới, số ô mở) để đo trong game
        batdaudo = time.time()
        if lechtoida is None:
            ox, oy = 0, 0
            luoi = self._get_luoicabando()
        else:
            ox, oy = min(x1, x2) - lechtoida, min(y1, y2) - lechtoida
            luoi = self._get_luoivatcan(ox, oy, max(x1, x2) + lechtoida, max(y1, y2) + lechtoida)
        if not luoi:
            return None
        thoigiandocluoi = time.time() - batdaudo
        rong, cao = len(luoi), len(luoi[0])
        # Ô máy chủ chặn mà lưới client không ghi (ghi tay vào vatcanhoc.json)
        idbando = self.get_idbandohientai()
        hocs = taivatcanhoc(idbando)

        def trong(x, y):
            return 0 <= x - ox < rong and 0 <= y - oy < cao and not luoi[x - ox][y - oy] and (x, y) not in hocs

        # Khu vực cấm khai tay (KHUVUCCAM_MAP: chỗ đi vào là kẹt, vd Tập Kích Môn Phái (103, 53), (96, 96)): mỗi ô trong đó tính thêm
        # PHATKHUVUCCAMKHONGCATGOC bước (né được thì né; đang đứng / đích ở trong thì vẫn đi ra / vào được)
        cams = self._layokhuvuccam(ox, oy, ox + rong - 1, oy + cao - 1)
        if self.is_tranhvungcam:
            # Vòng quanh cổng (VUNGCAM_MAP) cũng phạt như khu vực cấm: A* giờ chạy trên mọi bản đồ (IS_BOTTUTIMDUONGMOIBANDO), đường cắt
            # qua cổng là lọt sang bản đồ khác. Đích nằm trong vòng cổng (chạy tới cổng) vẫn vào được, chỉ né khi có đường khác
            cams = cams | self._layotrongvung(VUNGCAM_MAP.get(idbando, ()), ox, oy, ox + rong - 1, oy + cao - 1)
        # Ô NPC đang đứng: phạt PHATONPCKHONGCATGOC bước (ô đứng / ô đích không tính: đi tới nói chuyện với NPC)
        npcs = self._get_onpcdung() - {(x1, y1), (x2, y2)}
        bayh = time.time()
        tamchans = {o for (b, o), luc in self._tamchankhongcatgoc.items()
                    if b == idbando and bayh - luc < THOIGIANTAMCHAN and o not in ((x1, y1), (x2, y2))}

        # Bản C (astar_xq.dll): cùng thuật toán, ra đúng y chuỗi (so 480/480 cặp trên _internal/luoi_*.json 2026-11-12), cả bản đồ nhanh
        # hơn 19-51 lần (bản đồ 80: 74 ms -> 1.5 ms). Không có DLL / lỗi thì chạy bản Python ở dưới
        if IS_DUNGASTARC and astar_c_xq.is_cosan():
            try:
                return self._timduongbangc(luoi, ox, oy, rong, cao, x1, y1, x2, y2, khoangcachtoida, is_chocatgoc, hocs, cams,
                                           npcs, tamchans, lechtoida, batdaudo, thoigiandocluoi)
            except Exception as e:
                self._inlog(f"[A* C] Lỗi {e!r}, chạy bản Python")
        elif IS_DUNGASTARC and not self._is_dalogastarc:
            self._is_dalogastarc = True
            self._inlog(f"[A* C] Không dùng được astar_xq.dll ({astar_c_xq.get_loinap()}), chạy bản Python")

        huongs = [(dx, dy, kytu.encode()) for kytu, (dx, dy) in HUONGTIMDUONG_MAP.items()]
        nguong = max(0., khoangcachtoida)
        batdau = (x1, y1)
        gs = {batdau: 0.}
        truoc = {}
        hang = [(math.dist(batdau, (x2, y2)), 0., batdau)]
        dich = None
        somo = 0
        while hang:
            _, g, o = heapq.heappop(hang)
            if g > gs.get(o, float("inf")):
                continue
            somo += 1
            if (math.dist(o, (x2, y2)) <= nguong) if nguong else o == (x2, y2):
                dich = o
                break
            x, y = o
            for dx, dy, kytu in huongs:
                nx, ny = x + dx, y + dy
                if not trong(nx, ny) or (dx and dy and not is_chocatgoc and not (trong(x + dx, y) and trong(x, y + dy))):
                    continue
                ng = g + (1.4142 if dx and dy else 1.) + (PHATKHUVUCCAMKHONGCATGOC if (nx, ny) in cams else 0.) \
                    + (PHATONPCKHONGCATGOC if (nx, ny) in npcs else 0.) + (PHATTAMCHANKHONGCATGOC if (nx, ny) in tamchans else 0.)
                if ng < gs.get((nx, ny), float("inf")):
                    gs[(nx, ny)] = ng
                    truoc[(nx, ny)] = (o, kytu)
                    heapq.heappush(hang, (ng + math.dist((nx, ny), (x2, y2)), ng, (nx, ny)))
        thoigian = time.time() - batdaudo
        if thoigian > THOIGIANASTARCHAM:
            self._inlog(f"[A* CHẬM] {'cả bản đồ' if lechtoida is None else f'khung ±{lechtoida}'}{' cho cắt góc' if is_chocatgoc else ''} "
                        f"{(x1, y1)} -> {(x2, y2)}: {thoigian * 1000:.0f} ms (đọc lưới {thoigiandocluoi * 1000:.0f} ms), mở {somo} ô, "
                        f"{'có đường' if dich and dich != batdau else 'không có đường'}")
        if not dich or dich == batdau:
            return None
        kytus = []
        while dich != batdau:
            dich, kytu = truoc[dich]
            kytus.append(kytu)
        return b"".join(reversed(kytus))

    def get_duongchaytron(self, ketancongs, dichcu = None, dichboquas = (), is_tranhvungcam = True):
        # Tính đường chạy trốn trên lưới vật cản (thay cho kiểu cũ mỗi 0.15s nhích 2-6 ô theo hướng ngược kẻ địch, hay lùi vào góc chết):
        #  1. BFS từ mọi kẻ tấn công ketancongs [(x, y, _)]: số bước nó cần để tới từng ô (kẻ địch được lách chéo qua góc: tính bi quan).
        #     Mỗi bước thẳng hay chéo đều mất 1 nhịp "go" (2 ô / 0.5s), tầm đánh tính theo ô vuông => BFS đơn vị là đúng thời gian
        #  2. BFS từ ô mình (không lách chéo qua góc như máy chủ) chỉ mở rộng sang ô mình tới TRƯỚC mọi kẻ địch (bước của mình < bước của
        #     nó): đường đi ra không bao giờ cắt ngang qua trước mặt kẻ địch
        #  3. Chấm điểm các ô tới được cách 4..24 bước: xa kẻ địch (bước đi + ô vuông), độ thoáng 7x7 quanh ô, và "khoảng trống phía sau"
        #     (số ô an toàn đi tiếp được qua ô đó trong cây BFS) => góc chết / túi cụt ít ô phía sau bị điểm thấp, đường mở rộng điểm cao
        # dichcu: đích đang chạy, còn an toàn và điểm không kém quá DIEMGIUDICHCHAYTRON thì giữ. dichboquas: đích vừa kẹt (máy chủ chặn)
        # -> {"dich", "chuoihuong", "batdau", "sobuoc", "buocke", "diem"} hoặc None (bị vây kín / chưa đọc được lưới)
        diachinhanvat = self.get_diachicosothongtinnhanvat1()
        if not diachinhanvat or not ketancongs:
            return None
        x1, y1 = struct.unpack("<ii", read_bytes(self.tientrinh, diachinhanvat + 0x18, 8))
        r = BANKINHLUOICHAYTRON
        n = 2 * r + 1
        ox, oy = x1 - r, y1 - r
        luoi = self._get_luoivatcan(ox, oy, x1 + r, y1 + r)
        if not luoi:
            return None
        idbando = self.get_idbandohientai()
        hocs = taivatcanhoc(idbando)
        cams = self._layokhuvuccam(ox, oy, ox + n - 1, oy + n - 1)
        if is_tranhvungcam and not self.get_is_bandophongyeu():
            cams |= self._layotrongvung(VUNGCAM_MAP.get(idbando, ()), ox, oy, ox + n - 1, oy + n - 1)
        tran = self._toadotrandolacanh
        trong = bytearray(n * n)
        for i in range(n):
            cot = luoi[i]
            x = ox + i
            for j in range(n):
                if cot[j]:
                    continue
                o = (x, oy + j)
                if o in hocs or o in cams or (tran and math.dist(tran, o) > BANKINHTRANDOLACANH):
                    continue
                trong[i * n + j] = 1
        batdau = r * n + r
        trong[batdau] = 1
        lancans = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
        vocuc = 1 << 20

        # 1. Số bước kẻ địch tới từng ô
        buocke = [vocuc] * (n * n)
        hang = deque()
        toadokes = []
        for x, y, _ in ketancongs:
            i, j = round(x) - ox, round(y) - oy
            toadokes.append((round(x), round(y)))
            if 0 <= i < n and 0 <= j < n and buocke[i * n + j]:
                buocke[i * n + j] = 0
                hang.append(i * n + j)
        while hang:
            k = hang.popleft()
            i, j = divmod(k, n)
            d = buocke[k] + 1
            for dx, dy in lancans:
                ni, nj = i + dx, j + dy
                if 0 <= ni < n and 0 <= nj < n:
                    nk = ni * n + nj
                    if trong[nk] and buocke[nk] > d:
                        buocke[nk] = d
                        hang.append(nk)

        # 2. Vùng mình tới trước kẻ địch
        buocminh = [-1] * (n * n)
        cha = [-1] * (n * n)
        buocminh[batdau] = 0
        thutu = [batdau]
        hang = deque([batdau])
        while hang:
            k = hang.popleft()
            i, j = divmod(k, n)
            d = buocminh[k] + 1
            for dx, dy in lancans:
                ni, nj = i + dx, j + dy
                if not (0 <= ni < n and 0 <= nj < n):
                    continue
                nk = ni * n + nj
                if not trong[nk] or buocminh[nk] >= 0 or d >= buocke[nk]:
                    continue
                if dx and dy and not (trong[(i + dx) * n + j] and trong[i * n + j + dy]):
                    continue
                buocminh[nk] = d
                cha[nk] = k
                hang.append(nk)
                thutu.append(nk)
        if len(thutu) <= 1:
            return None
        # Khoảng trống phía sau: kích thước cây con trong cây BFS
        socon = [1] * (n * n)
        for k in reversed(thutu):
            if cha[k] >= 0:
                socon[cha[k]] += socon[k]
        # Độ thoáng: tỉ lệ ô trống trong 7x7 quanh ô (tổng tiền tố 2 chiều)
        tong = [0] * ((n + 1) * (n + 1))
        for i in range(n):
            dong = 0
            for j in range(n):
                dong += trong[i * n + j]
                tong[(i + 1) * (n + 1) + j + 1] = tong[i * (n + 1) + j + 1] + dong

        def dothoang(i, j):
            a, b, c, d = max(0, i - 3), max(0, j - 3), min(n, i + 4), min(n, j + 4)
            return (tong[c * (n + 1) + d] - tong[a * (n + 1) + d] - tong[c * (n + 1) + b] + tong[a * (n + 1) + b]) / 49.

        def chamdiem(k):
            i, j = divmod(k, n)
            x, y = ox + i, oy + j
            oke = min(min(max(abs(x - kx), abs(y - ky)) for kx, ky in toadokes), 25)
            # Bước đi của kẻ địch, khoảng ô vuông (đánh xa), khoảng dẫn trước khi tới nơi, độ thoáng, khoảng trống phía sau
            return min(buocke[k], 30) + 0.5 * oke + 0.5 * min(buocke[k] - buocminh[k], 20) + 8. * dothoang(i, j) \
                + 2. * math.log2(1 + min(socon[k], 256)) - 0.1 * buocminh[k]

        tot, diemtot = None, None
        for sobuoctoithieu in (SOBUOCDICHCHAYTRONTOITHIEU, 1):
            for k in thutu:
                if not sobuoctoithieu <= buocminh[k] <= SOBUOCDICHCHAYTRONTOIDA:
                    continue
                i, j = divmod(k, n)
                if any(max(abs(ox + i - bx), abs(oy + j - by)) <= 2 for bx, by in dichboquas):
                    continue
                diem = chamdiem(k)
                if diemtot is None or diem > diemtot:
                    tot, diemtot = k, diem
            if tot is not None:
                break
        if tot is None:
            return None
        if dichcu:
            i, j = dichcu[0] - ox, dichcu[1] - oy
            if 0 <= i < n and 0 <= j < n:
                k = i * n + j
                if buocminh[k] >= 1 and buocminh[k] <= SOBUOCDICHCHAYTRONTOIDA + 10:
                    diem = chamdiem(k)
                    if diem >= diemtot - DIEMGIUDICHCHAYTRON:
                        tot, diemtot = k, diem
        kytu_map = {v: kt.encode() for kt, v in HUONGTIMDUONG_MAP.items()}
        kytus = []
        k = tot
        while cha[k] >= 0:
            p = cha[k]
            kytus.append(kytu_map[(k // n - p // n, k % n - p % n)])
            k = p
        return {
            "dich": (ox + tot // n, oy + tot % n),
            "chuoihuong": b"".join(reversed(kytus)),
            "batdau": (x1, y1),
            "sobuoc": buocminh[tot],
            "buocke": buocke[tot] if buocke[tot] < vocuc else None,
            "diem": round(diemtot, 1),
        }

    def action_dichuoihuongchaytron(self, duong):
        # Đi theo chuỗi hướng get_duongchaytron vừa tính (ghi thẳng như action_dikhongcatgoc). Cùng đích mà chuỗi chưa hết thì
        # THOIGIANGHILAICHAYTRON giây mới ghi lại. -> True đang đi; False bị chặn (vận khí, xuất chiêu, chưa tới lượt);
        # None: ô bắt đầu của chuỗi không còn đúng ô mình (đã đi tiếp), nơi gọi tính lại đường
        if self._is_vohieuhoadichuyen or self.get_is_khoavankhitrieuhoi() or self.get_is_dangxuatchieu():
            return False
        diachinhanvat = self.get_diachicosothongtinnhanvat1()
        if not diachinhanvat or not duong or not duong.get("chuoihuong"):
            return False
        now = time.time()
        if self._dichchaytrondaghi == duong["dich"] and self.get_idlenhdichuyen() and now - self._thoidiemghichaytron < THOIGIANGHILAICHAYTRON:
            return True
        x1, y1 = struct.unpack("<ii", read_bytes(self.tientrinh, diachinhanvat + 0x18, 8))
        if (x1, y1) != tuple(duong["batdau"]):
            return None
        if not self._get_is_duocbatdaudichuyen():
            return False
        chuoihuong = duong["chuoihuong"][:SOBUOCCHUOIDUONGDITOIDA]
        self.action_ngungtudongtimduong()
        self._dichkhongcatgoc = None
        self._dichdioogannhat = None
        khoidieukhien = read_int(self.tientrinh, self.diachixq + DC.KHOIDIEUKHIEN)
        if khoidieukhien:
            write_bytes(self.tientrinh, khoidieukhien + DC.KDK_DICHCLICK, bytes(8), 8)
        write_bytes(self.tientrinh, self.diachixq + DC.CHUOIDUONGDI, b"\0" + chuoihuong + bytes(99 - len(chuoihuong)), 100)
        self.set_idlenhdichuyen(1)
        self._thoidiemdichuyengannhat = now
        self._thoidiemboquadichuyencungtoadogannhat = now
        if IS_LOGDICHUYEN and self._dichchaytrondaghi != duong["dich"]:
            self._inlog(f"[CHẠY TRỐN] {(x1, y1)} -> {duong['dich']}: {len(chuoihuong)} bước")
        self._dichchaytrondaghi = duong["dich"]
        self._thoidiemghichaytron = now
        return True

    def get_is_duongdicatvungcam(self, x1, y1, x2, y2):
        # Đường chạy thẳng (x1, y1) -> (x2, y2) có chạm vùng cấm của bản đồ hiện tại không (VUNGCAM_MAP: đi vào sẽ bị chuyển bản đồ)
        danhsachvungcam = VUNGCAM_MAP.get(self.get_idbandohientai())
        # Phong Yêu Kính: cổng của bản đồ thật mượn ID không có tác dụng, không né
        if not danhsachvungcam or self.get_is_bandophongyeu():
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
        if self._is_vohieuhoadichuyen or (not deltax and not deltay):
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
            nhan = "ĐI Ô CẢ BẢN ĐỒ"
            is_ok = self._dicabandokhidoancut(xdich, ydich)
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

    def action_dichuyengiukhoangcachtoida(self, diachicosothongtinnhanvat2, khoangcachtoida, khoangcachdichuyentoida = 0, delay = 0.05,
                                          is_dikhongcatgoc = False):
        # is_dikhongcatgoc: bản đồ có chỗ máy chủ giật lại (TacTu._is_bandocochoket), tiếp cận cận chiến tìm đường bằng A* của bot
        if not diachicosothongtinnhanvat2 or not self.get_iddoituong(diachicosothongtinnhanvat2):
            return False

        if khoangcachtoida <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
            return self._tiepcancanchien(diachicosothongtinnhanvat2, khoangcachtoida, is_dikhongcatgoc = is_dikhongcatgoc)
        toadomuctieu = self._laytoadodondau(diachicosothongtinnhanvat2)
        # Tiếp cận luôn bằng tìm đường của game (đo A/B: click lệch tâm màn hình quay đầu không lý do 5.3/ph, tìm đường 1.3/ph)
        return self._tiepcanbangtimduong(*toadomuctieu, khoangcachtoida)

    def _tiepcancanchien(self, diachimuctieu, khoangcachtoida, is_dikhongcatgoc = False):
        # is_dikhongcatgoc: bản đồ có chỗ giật (khu vực cấm / ô học được là chặn): đường lấy từ A* của bot (action_dikhongcatgoc, né ô học
        # được) thay vì tìm đường cục bộ của client, còn lại (2 bước, tính lại 0.25s, kề thì ngắt, chờ, đón đầu) giữ nguyên
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
        # Mục tiêu đang đi về phía mình và bước tới đã gần (KHOANGCACHCHOMUCTIEUTOI ô) thì đứng chờ nó tới, không đi rồi quay đầu.
        # Quái (lớp 0x82) đi chậm hơn mình nhiều: dùng KHOANGCACHCHOQUAITOI, tự đi tới nhanh hơn đứng chờ
        khoangcachcho = KHOANGCACHCHOQUAITOI if read_short_int(self.tientrinh, diachimuctieu + 0x29) == 0x82 else KHOANGCACHCHOMUCTIEUTOI
        if kc(x2, y2) <= 1 or (kc(x2, y2) < kc(xhientai, yhientai) and kc(x2, y2) <= khoangcachcho):
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
        if is_dikhongcatgoc:
            nhan += " (KHÔNG CẮT GÓC)"
            is_ok = self.action_dikhongcatgoc(xdich, ydich, 0., sobuoctoida = SOBUOCTIEPCANCANCHIEN, is_dungkedich = True,
                                              thoigiantinhlai = THOIGIANTINHLAITIEPCANCANCHIEN)
        else:
            is_ok = self.action_dichuyenoo(xdich, ydich, delay = 0., sobuoctoida = SOBUOCTIEPCANCANCHIEN, is_dungkedich = True,
                                           thoigiantinhlai = THOIGIANTINHLAITIEPCANCANCHIEN)
        if is_ok is None:
            # Không ra đường (chưa có đối tượng tìm đường, xa / bị bao kín): tự động tìm đường của game như cũ
            return self._tiepcanbangtimduong(xdich, ydich, khoangcachtoida)
        if is_ok and IS_LOGDICHUYEN and (xdich, ydich) != self._dichclicklogcuoi:
            self._dichclicklogcuoi = (xdich, ydich)
            self._inlog(f"[{nhan}] (đang ở {(x1, y1)}, tư thế {self.get_idtuthenhanvat()}) -> {(xdich, ydich)}, mục tiêu {(x2, y2)}")
        return is_ok

    def action_dioochangtoidich(self, x2, y2, khoangcachtoida = 0.):
        # Đi tới (x2, y2) trong cùng bản đồ bằng đi theo ô (tìm đường cục bộ của client, đi gần thẳng) thay vì tự động tìm đường của game
        # (vào thành / vào môn phái nó hay chạy vòng ra xa rồi mới vòng vào). Tìm đường cục bộ chỉ tính tối đa ~100 bước: xa thì đi từng
        # chặng trên đường thẳng tới đích (thử chặng dài trước), không chặng nào ra đường thì mới dùng tự động tìm đường
        # Đích là vật cản thì nhắm ô đi được gần nhất (tới đó là xong, không đứng chân tường chờ kẹt). Có khoangcachtoida thì vẫn đo
        # theo đích thật (NPC hay đứng trên ô vật cản: kéo đích rồi mới lùi khoangcachtoida là lệch cộng dồn, vd Văn Xương (111, 137)
        # kéo về (110, 136), dừng cách đó 2 ô thành đứng ở (109, 134) cách NPC 3.6 ô); ô dừng chọn trong tầm ở dưới (_chondichtoiduoc)
        if khoangcachtoida < 1:
            x2, y2 = self.get_oditduocganhat(x2, y2)
        x1, y1 = self.get_toado()
        khoangcach = math.dist((x1, y1), (x2, y2))
        if khoangcach <= max(1., khoangcachtoida):
            return False
        xdich, ydich = (x2, y2)
        if khoangcachtoida > 0:
            tyle = khoangcachtoida / khoangcach
            xdich, ydich = round(x2 + (x1 - x2) * tyle), round(y2 + (y1 - y2) * tyle)
            # Gần rồi: điểm trên đường thẳng có khi ở sau tường thấp (vd NPC đứng sau quầy / bậc thềm) => lấy ô trong tầm tới được thật
            if khoangcach <= KHOANGCACHCHONDICHTOIDUOC:
                dichtoiduoc = self._chondichtoiduoc(x2, y2, khoangcachtoida)
                if dichtoiduoc:
                    xdich, ydich = dichtoiduoc
        # Theo dõi theo đích cuối (x2, y2): điểm dừng (xdich, ydich) lùi lại theo khoangcachtoida nên đổi theo vị trí hiện tại.
        # Kẹt (đi theo ô THOIGIANKETDIOO giây không gần đích hơn, vd tường / cọc gỗ trong thành chắn mà tìm đường cục bộ chỉ ra đoạn
        # cụt): đích này dùng tự động tìm đường của game. Đích nhích ít (đuổi quái đang chạy) vẫn coi là cùng đích, kẻo đếm lại mãi
        now = time.time()
        tiendo = self._tiendodioo
        if not tiendo or math.dist(tiendo[0], (x2, y2)) > KHOANGCACHCUNGDICHDIOO:
            tiendo = self._tiendodioo = [(x2, y2), khoangcach, now, False]
        elif khoangcach < tiendo[1] - 1:
            tiendo[1], tiendo[2] = khoangcach, now
        elif now - tiendo[2] > THOIGIANKETDIOO:
            tiendo[3] = True
        if tiendo[3]:
            is_ok = self._dicabandokhidoancut(x2, y2, khoangcachtoida)
            if is_ok is not None:
                return is_ok
            return self.action_tudongtimduong(xdich, ydich, self.get_idbandohientai(), is_lotrinh = False)
        # Đang đi chặng tới đúng đích này, chưa tới gần điểm cuối chặng: đi tiếp (tính lại mỗi lượt thì ghi đè chuỗi liên tục, đi khựng)
        if self._changdioo and self._changdioo[0] == (x2, y2) and self.get_idlenhdichuyen() \
                and math.dist((x1, y1), self._changdioo[1]) > 3:
            return True
        dai = math.dist((x1, y1), (xdich, ydich))
        for chang in (dai, 60., 40., 25.):
            if chang > dai or chang <= 0:
                continue
            t = chang / dai
            diem = (round(x1 + (xdich - x1) * t), round(y1 + (ydich - y1) * t))
            is_ok = self.action_dichuyenoo(*diem, delay = 0.)
            if is_ok is not None:
                if is_ok:
                    self._changdioo = ((x2, y2), diem)
                return is_ok
        self._changdioo = None
        is_ok = self._dicabandokhidoancut(x2, y2, khoangcachtoida)
        if is_ok is not None:
            return is_ok
        return self.action_tudongtimduong(xdich, ydich, self.get_idbandohientai(), is_lotrinh = False)

    def _chondichtoiduoc(self, x2, y2, khoangcachtoida):
        # Ô đi được cách (x2, y2) không quá khoangcachtoida mà tìm đường cục bộ tới được đúng ô đó (không phải đoạn cụt): thử các ô
        # gần mình trước, tối đa SOOTHUDICHTOIDUOC ô. Nhớ kết quả THOIGIANNHODICHTOIDUOC giây theo đích (mỗi lần thử tốn vài lần tìm
        # đường). None: không ô nào tới được (nơi gọi đi như cũ, kẹt thì tự động tìm đường của game)
        khoa = (self.get_idbandohientai(), x2, y2, khoangcachtoida)
        nho = self._dichtoiduoc_cache.get(khoa)
        if nho and time.time() - nho[0] < THOIGIANNHODICHTOIDUOC:
            return nho[1]
        diachinhanvat = self.get_diachicosothongtinnhanvat1()
        r = math.floor(khoangcachtoida)
        luoi = self._get_luoivatcan(x2 - r, y2 - r, x2 + r, y2 + r)
        if not diachinhanvat or not luoi:
            return None
        x1, y1 = struct.unpack("<ii", read_bytes(self.tientrinh, diachinhanvat + 0x18, 8))
        ungviens = sorted(((x2 + dx, y2 + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                           if not luoi[dx + r][dy + r] and math.hypot(dx, dy) <= khoangcachtoida),
                          key = lambda o: math.dist(o, (x1, y1)))
        ketqua = None
        for o in ungviens[:SOOTHUDICHTOIDUOC]:
            if o == (x1, y1):
                ketqua = o
                break
            chuoihuong = self._get_chuoihuongtimduongcucbo(x1, y1, *o)
            if chuoihuong and (len(chuoihuong) >= 100 or self._get_diemcuoichuoihuong(x1, y1, chuoihuong) == o):
                ketqua = o
                break
        if len(self._dichtoiduoc_cache) > 64:
            self._dichtoiduoc_cache.clear()
        self._dichtoiduoc_cache[khoa] = (time.time(), ketqua)
        return ketqua

    def get_diembanthong(self, x2, y2, tamtoida):
        # Ô đứng bắn mục tiêu ở (x2, y2) được (tầm xa bị vật cản chắn): ô đi được, đoạn thẳng tới mục tiêu không qua vật cản, tầm
        # max(|dx|, |dy|) <= tamtoida. Không chọn điểm giữa mình và mục tiêu: chi phí = quãng đi + HESOPHATGANMUCTIEU x số ô gần mục
        # tiêu hơn bây giờ => ưu tiên đi ngang / lùi ra chỗ thông, giữ khoảng cách. Thử SOOTHUDICHTOIDUOC ô rẻ nhất bằng tìm đường cục
        # bộ, bỏ ô phải vòng xa hay đường đi lướt sát mục tiêu. Ô đã chọn giữ tới khi hết dùng được. None: không có ô nào
        diachinhanvat = self.get_diachicosothongtinnhanvat1()
        if not diachinhanvat:
            return None
        x1, y1 = struct.unpack("<ii", read_bytes(self.tientrinh, diachinhanvat + 0x18, 8))
        x2, y2 = round(x2), round(y2)
        idbando = self.get_idbandohientai()
        now = time.time()
        r = BANKINHTIMDIEMBAN
        ox, oy = min(x1 - r, x2), min(y1 - r, y2)
        luoi = self._get_luoivatcan(ox, oy, max(x1 + r, x2), max(y1 + r, y2))
        if not luoi:
            return None

        def is_vatcan(x, y):
            return luoi[x - ox][y - oy]

        def is_thong(xa, ya):
            sobuoc = max(1, math.ceil(math.dist((xa, ya), (x2, y2)) * 2))
            for i in range(1, sobuoc):
                x, y = round(xa + (x2 - xa) * i / sobuoc), round(ya + (y2 - ya) * i / sobuoc)
                if (x, y) not in ((xa, ya), (x2, y2)) and is_vatcan(x, y):
                    return False
            return True

        def tam(x, y):
            return max(abs(x - x2), abs(y - y2))

        def is_dungduoc(o):
            return abs(o[0] - x1) <= r and abs(o[1] - y1) <= r and not is_vatcan(*o) and tam(*o) <= tamtoida and is_thong(*o)

        # Giữ ô cũ (cùng bản đồ) khi còn bắn được từ đó: mục tiêu nhích ít thì không chọn lại, kẻo đổi hướng đi liên tục
        cu = self._diembanthong
        if cu and cu[0] == idbando and cu[1] and is_dungduoc(cu[1]):
            return cu[1]
        # Vừa tính mà không ra ô nào: chờ THOIGIANTINHLAIDIEMBAN giây mới tính lại (mỗi lần tốn tới SOOTHUDICHTOIDUOC lần tìm đường)
        if cu and cu[0] == idbando and cu[1] is None and now - cu[2] < THOIGIANTINHLAIDIEMBAN and cu[3] == (x2, y2):
            return None

        tamhientai = min(tam(x1, y1), tamtoida)
        ungviens = []
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                o = (x1 + dx, y1 + dy)
                if not is_dungduoc(o):
                    continue
                tamo = tam(*o)
                chiphi = math.hypot(dx, dy) + HESOPHATGANMUCTIEU * max(0., tamhientai - tamo)
                ungviens.append((tamo < KHOANGCACHDIEMBANTOITHIEU, chiphi, o))
        ungviens.sort()

        ketqua = None
        for _, _, o in ungviens[:SOOTHUDICHTOIDUOC]:
            if o == (x1, y1):
                ketqua = o
                break
            chuoihuong = self._get_chuoihuongtimduongcucbo(x1, y1, *o)
            if not chuoihuong or len(chuoihuong) >= 100 or self._get_diemcuoichuoihuong(x1, y1, chuoihuong) != o:
                continue
            if len(chuoihuong) > HESODUONGVONGDIEMBAN * math.dist((x1, y1), o) + 4:
                continue
            # Đường đi không được lao lại gần mục tiêu hơn cả điểm đầu lẫn điểm cuối (vòng qua phía mục tiêu)
            tamsan = min(tam(x1, y1), tam(*o)) - 1
            x, y = x1, y1
            is_satmuctieu = False
            for kytu in chuoihuong.decode("latin1"):
                ddx, ddy = HUONGTIMDUONG_MAP.get(kytu, (0, 0))
                x, y = x + ddx, y + ddy
                if tam(x, y) < tamsan:
                    is_satmuctieu = True
                    break
            if not is_satmuctieu:
                ketqua = o
                break
        if ketqua is None and ungviens and not self.get_is_cotimduongcucbo():
            # Chưa có đối tượng tìm đường cục bộ (client chưa click lần nào): lấy ô rẻ nhất, đi bằng tìm đường của game
            ketqua = ungviens[0][2]
        self._diembanthong = (idbando, ketqua, now, (x2, y2))
        if ketqua and IS_LOGDICHUYEN:
            self._inlog(f"[ĐIỂM BẮN THÔNG] (đang ở {(x1, y1)}, tầm {tam(x1, y1)}) -> {ketqua} (tầm {tam(*ketqua)}), mục tiêu {(x2, y2)}")
        return ketqua

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
        # Điểm trên đường thẳng rơi vào vật cản (nhích tầm xa khi lệch toạ độ client - server hay gặp): lấy ô đi được trong tầm, tới được
        # thật, gần mình nhất (_chondichtoiduoc); không có thì ô đi được gần điểm đó nhất (có thể hơi ngoài tầm, lượt sau nhích tiếp)
        if self.get_is_vatcan(xdich, ydich):
            dichtoiduoc = self._chondichtoiduoc(round(x2), round(y2), max(0., khoangcachtoida))
            xcu, ycu = xdich, ydich
            xdich, ydich = dichtoiduoc if dichtoiduoc else self.get_oditduocganhat(xdich, ydich)
            if IS_LOGDICHUYEN:
                self._inlog(f"[TIẾP CẬN] đích {(xcu, ycu)} là vật cản => {(xdich, ydich)}")
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
            nhan = "TIẾP CẬN CẢ BẢN ĐỒ"
            is_ok = self._dicabandokhidoancut(xdich, ydich)
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
            # Sau lưng là vật cản thì lùi chéo / ngang (hướng lệch ít nhất mà đường thẳng không vướng vật cản), kẻo lùi vào tường
            # (kéo đích về ô đi được gần nhất có khi lại sát mục tiêu hơn)
            huong = self._chonhuonglui(x1, y1, x2, y2, khoangcachtoithieu, khoangcachdichuyen, bool(khoangcachdichuyentoida))
            if huong:
                deltax, deltay = huong
        else:
            # Đứng trùng vị trí mục tiêu: chọn hướng ngẫu nhiên để thoát ra
            goc = random.uniform(0, 2 * math.pi)
            deltax, deltay = khoangcachdichuyen * math.cos(goc), khoangcachdichuyen * math.sin(goc)

        return self._action_dichuyentheovector(x1, y1, deltax, deltay, delay = delay)

    def _chonhuonglui(self, x1, y1, x2, y2, khoangcachtoithieu, khoangcachdichuyen, is_gioihanquang):
        # Hướng lùi khỏi (x2, y2): thử ngược hướng mục tiêu trước rồi lệch dần 2 bên (GOCLECHLUIs). Hướng được nhận khi ô tới đi được,
        # mọi ô trên đường thẳng tới đó đi được, không cắt vùng cấm và tới đó cách mục tiêu đủ khoangcachtoithieu (lệch hướng thì quãng
        # lùi dài thêm tối đa QUANGLUITHEMTOIDA ô cho đủ; is_gioihanquang: không được dài thêm, chỉ cần xa mục tiêu hơn bây giờ).
        # -> (deltax, deltay) theo quy ước _action_dichuyentheovector (deltay = y1 - y2); None: sau lưng trống (lùi thẳng như cũ).
        # Bị dồn góc (không hướng nào đủ xa): tới ô xa mục tiêu nhất trong các hướng đi được, không ô nào xa hơn bây giờ thì (0, 0) =
        # đứng yên (lùi thẳng vào nước / tường thì đích kéo về có khi ở bên kia, tự động tìm đường chạy vòng)
        khoangcach = math.dist((x1, y1), (x2, y2))
        quangtoida = khoangcachdichuyen if is_gioihanquang else khoangcachdichuyen + QUANGLUITHEMTOIDA
        r = math.ceil(quangtoida) + 1
        luoi = self._get_luoivatcan(x1 - r, y1 - r, x1 + r, y1 + r)
        if not luoi:
            return None

        def is_vatcan(x, y):
            return luoi[x - x1 + r][y - y1 + r] if abs(x - x1) <= r and abs(y - y1) <= r else 1

        if not any(is_vatcan(round(x1 - (x2 - x1) / khoangcach * t), round(y1 - (y2 - y1) / khoangcach * t))
                   for t in [i / 2 for i in range(1, math.ceil(khoangcachdichuyen * 2) + 1)]):
            return None  # Sau lưng trống: lùi thẳng như cũ
        def is_diduoc(xd, yd):
            if (xd, yd) == (x1, y1) or is_vatcan(xd, yd):
                return False
            sobuoc = max(1, math.ceil(math.dist((x1, y1), (xd, yd)) * 2))
            if any(is_vatcan(round(x1 + (xd - x1) * i / sobuoc), round(y1 + (yd - y1) * i / sobuoc)) for i in range(1, sobuoc)):
                return False
            return not (self.is_tranhvungcam and self.get_is_duongdicatvungcam(x1, y1, xd, yd))

        gocgoc = math.atan2(y1 - y2, x1 - x2)
        xanhat = None
        for goclech in GOCLECHLUIs:
            for dau in ((1, -1) if goclech else (1,)):
                goc = gocgoc + dau * math.radians(goclech)
                quang = khoangcachdichuyen
                while quang <= quangtoida + 1e-6:
                    xd, yd = round(x1 + quang * math.cos(goc)), round(y1 + quang * math.sin(goc))
                    kc = math.dist((xd, yd), (x2, y2))
                    if not is_diduoc(xd, yd):
                        break
                    if xanhat is None or kc > xanhat[0]:
                        xanhat = (kc, xd, yd)
                    if kc >= khoangcachtoithieu or (is_gioihanquang and kc > khoangcach + 0.5):
                        return xd - x1, y1 - yd
                    quang += 0.5
        if xanhat and xanhat[0] > khoangcach + 0.5:
            return xanhat[1] - x1, y1 - xanhat[2]
        return 0, 0

    def action_dichuyentiepcan(self, diachi2,khoangcachdichuyentoida = 0, delay = 0.05):
        return self.action_dichuyengiukhoangcachtoida(diachi2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_dichuyentiepcandiem(self, x2, y2, khoangcachdichuyentoida = 0, delay = 0.05):
        if x2 <= 0 or y2 <= 0:
            return False
        return self.action_dichuyengiukhoangcachtoidadiem(x2, y2, khoangcachtoida = 0, khoangcachdichuyentoida = khoangcachdichuyentoida, delay = delay)

    def action_sudungkynangvitriphudau(self, idvitri_x, idvitri_y, diachi2, khoangcachphudau, delay = 1, tamxatranphap = None):
        # idvitri_x là mã kỹ năng (id hoặc vị trí (x, y)) khi không truyền idvitri_y
        matranphap = idvitri_x if idvitri_y is None and idvitri_x in TRANPHAPVANMONGCOCs else None
        vitri = self._giaivitrikynang(idvitri_x, idvitri_y)
        if not vitri:
            return False
        idvitri_x, idvitri_y = vitri
        if not diachi2 or not self.get_is_nhanvattontai(diachi2):
            return False
        return self.action_sudungkynangvitriphudaudiem(idvitri_x, idvitri_y, *self.get_toado(diachi2), khoangcachphudau = khoangcachphudau, delay = delay,
                                                       tamxatranphap = tamxatranphap, matranphap = matranphap)

    def action_sudungkynangvitriphudaudiem(self, idvitri_x, idvitri_y, x2, y2, khoangcachphudau, delay = 1, tamxatranphap = None, matranphap = None):
        # tamxatranphap + matranphap (trận pháp Vân Mộng Cốc): tâm chọn theo loại trận quanh (x2, y2), trong tầm tamxatranphap
        # (_chontamtranvanmongcoc), bỏ qua khoangcachphudau
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
        if tamxatranphap is not None:
            tam = self._chontamtranvanmongcoc(matranphap, x2, y2, x1, y1, tamxatranphap)
            if not tam:
                return False
            targetx, targety = tam
        is_ok = self.action_sudungkynangtoado(idkynang, targetx, targety)
        if is_ok:
            self._thoidiemsudungkynanggannhat = time.time()
            self._thoidiemsudungkynangvitrigannhat_map[idvitri] = time.time()
            if tamxatranphap is not None:
                self._tamtranvuadat[(targetx, targety)] = time.time()
        return is_ok

    def get_is_damocuasotuychonnhanvatchinhlandau(self):
        x = read_int(self.tientrinh, self.diachixq + DC.CUASOTUYCHONNHANVAT)
        if not x:
            return False
        x = read_int(self.tientrinh, x + 0x2C)
        return False if x <= 10 else True

    def action_chovankhi(self, vitrikynang = None, caulenh = None, ten = "VẬN KHÍ"):
        # Kỹ năng vận khí cần một lúc mới bật trạng thái "Đang vận khí": coi như đang vận khí trong khoảng chờ đó để không thao tác gì
        # làm ngắt chiêu, nhưng không chờ mù một khoảng cố định. Khoảng chờ chỉ tính từ lúc lệnh thật sự ghi vào game (_danhdauguilenhvankhi)
        # và kết thúc sớm khi (xem _get_is_dangchovankhi):
        #   - thanh vận khí có gói bắt đầu mới (+ 0xF8 sau lúc gửi): đã vào vận khí, từ đó theo trạng thái thật của game
        #   - lệnh bị bỏ khỏi hàng đợi (hồi chiêu / khống chế / khoá) hoặc nằm hàng đợi quá THOIGIANCHOGUILENHVANKHI
        #   - gửi xong THOIGIANXACNHANRACHIEUVANKHI giây không vào tư thế xuất chiêu, kỹ năng chưa hồi chiêu: chiêu không ra
        # Có dấu hiệu chiêu đã ra mà chưa thấy thanh vận khí thì chờ tối đa THOIGIANCHOVAOVANKHI kể từ lúc gửi
        if caulenh is None and vitrikynang is not None:
            idkynang = self.get_idkynang(vitrikynang)
            caulenh = "pf {}".format(idkynang) if idkynang else None
        thoidiemhientai = time.time()
        cho = {"caulenh": caulenh, "vitrikynang": vitrikynang, "tao": thoidiemhientai, "gui": None, "guitgt": None, "chapnhan": False, "ten": ten}
        lenhgui = self._lenhguigannhat
        if caulenh is None:
            # Không biết lệnh nào: tính như vừa gửi
            cho["guitgt"], cho["gui"] = ctypes.windll.winmm.timeGetTime(), thoidiemhientai
        elif lenhgui and lenhgui[0] == caulenh and thoidiemhientai - lenhgui[1] < 1.:
            # Luồng xử lý lệnh đã ghi lệnh vào game trước khi kịp đăng ký chờ
            cho["guitgt"], cho["gui"] = lenhgui[2], lenhgui[1]
        self._chovankhi = cho
        return cho

    def _danhdauguilenhvankhi(self, caulenh):
        # Gọi ngay sau khi ghi lệnh vào game (luồng xử lý lệnh)
        thoidiemgui, tgtgui = time.time(), ctypes.windll.winmm.timeGetTime()
        self._lenhguigannhat = (caulenh, thoidiemgui, tgtgui)
        cho = self._chovankhi
        if cho and cho["gui"] is None and cho["caulenh"] == caulenh:
            cho["guitgt"] = tgtgui
            cho["gui"] = thoidiemgui

    def _bochovankhi(self, caulenh, is_dachapnhan = False):
        # Lệnh vận khí bị bỏ khỏi hàng đợi trước khi gửi. is_dachapnhan: bỏ vì kỹ năng đã vào hồi chiêu (lệnh trước đã được nhận) =>
        # vẫn chờ như chiêu đã ra, thanh vận khí bắt đầu trong THOIGIANCHOVAOVANKHI giây gần đây cũng tính là xác nhận
        cho = self._chovankhi
        if not cho or cho["gui"] is not None or cho["caulenh"] != caulenh:
            return
        if is_dachapnhan:
            cho["chapnhan"] = True
            cho["guitgt"] = (ctypes.windll.winmm.timeGetTime() - int(THOIGIANCHOVAOVANKHI * 1000)) & 0xFFFFFFFF
            cho["gui"] = time.time()
            return
        self._ketthucchovankhi(cho, "lệnh bị bỏ trước khi gửi")

    def _ketthucchovankhi(self, cho, lydo, is_vao = False):
        # Đánh dấu vào cho ("ketthuc", "vao") để nơi giữ cho biết lệnh có vào vận khí không (Hồi Thành Phù không vào thì không đếm lần)
        cho["ketthuc"], cho["vao"] = True, is_vao
        if is_vao and is_lenhtinvat(cho["caulenh"]):
            self._thoidiemtinvatgannhat = time.time()
        if self._chovankhi is cho:
            self._chovankhi = None
            self._inlog(f"[CHỜ VẬN KHÍ] {cho['ten']} '{cho['caulenh']}': {lydo}")
        return False

    def _docthanhvankhi(self):
        # (trạng thái + 0xD8, timeGetTime lúc nhận gói bắt đầu + 0xF8, địa chỉ đối tượng) hoặc None
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        x = read_int(self.tientrinh, x + DC.TG_VANKHI) if x else 0
        if not x:
            return None
        return read_int(self.tientrinh, x + 0xD8), read_int(self.tientrinh, x + 0xF8) & 0xFFFFFFFF, x

    def _get_is_dangchovankhi(self):
        cho = self._chovankhi
        if not cho:
            return False
        thoidiemhientai = time.time()
        if cho["gui"] is None:
            if thoidiemhientai - cho["tao"] < THOIGIANCHOGUILENHVANKHI:
                return True
            return self._ketthucchovankhi(cho, f"nằm hàng đợi quá {THOIGIANCHOGUILENHVANKHI}s chưa gửi")
        dagui = thoidiemhientai - cho["gui"]
        thanh = self._docthanhvankhi()
        if thanh and thanh[0] != TRANGTHAIVANKHI_KHONGVANKHI and ((thanh[1] - cho["guitgt"]) & 0xFFFFFFFF) < 0x80000000:
            ten = read_string(self.tientrinh, thanh[2] + 0xE0).strip()
            return self._ketthucchovankhi(cho, f"vào vận khí '{ten}' sau {round(dagui * 1000)}ms", is_vao = True)
        if not cho["chapnhan"] and cho["vitrikynang"] is not None:
            idtuthe = self.get_idtuthenhanvat()
            if idtuthe in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT) or not self.get_is_kynangsansang(cho["vitrikynang"]):
                cho["chapnhan"] = True
                self._inlog(f"[CHỜ VẬN KHÍ] {cho['ten']} '{cho['caulenh']}': chiêu đã ra sau {round(dagui * 1000)}ms (tư thế {idtuthe}), chờ thanh vận khí")
            elif dagui >= THOIGIANXACNHANRACHIEUVANKHI:
                return self._ketthucchovankhi(cho, f"gửi {round(dagui * 1000)}ms không ra chiêu (tư thế {idtuthe}, kỹ năng vẫn sẵn sàng), bỏ chờ")
        if dagui < THOIGIANCHOVAOVANKHI:
            return True
        return self._ketthucchovankhi(cho, f"quá {THOIGIANCHOVAOVANKHI}s không thấy thanh vận khí")

    def get_thoigianhoitinvatconlai(self):
        # Số giây Tín Vật còn hồi (THOIGIANHOITINVAT tính từ lần bot dùng gần nhất vào vận khí), 0 = dùng được.
        # Chỉ Niết Bàn có giãn cách 60s; Aegis dùng liền không cần chờ (người dùng dặn 2026-11-05)
        if not self.is_nietban:
            return 0.
        return max(0.,THOIGIANHOITINVAT - (time.time() - self._thoidiemtinvatgannhat))

    def action_huychovankhi(self):
        # Bỏ khoảng chờ vận khí (action_chovankhi) khi chủ động ngắt vận khí để di chuyển / dùng chiêu khác.
        # Đang khoá vận khí triệu hồi bảo thú thì không bỏ
        if not self.get_is_khoavankhitrieuhoi():
            self._chovankhi = None

    def action_khoavankhitrieuhoi(self, caulenhduocpheps = (), ten = "TRIỆU HỒI", vitrikynang = None):
        # Triệu hồi bảo thú (tốn bùa, thất bại là mất bùa) / Hồi Thành Phù: khoá các thao tác ngắt vận khí (ra chiêu / đánh thường, di
        # chuyển, tìm đường) cho tới khi vận khí xong. caulenhduocpheps: chính lệnh triệu hồi (đã vào hàng đợi) vẫn được gửi.
        # Khoá giữ trong lúc chờ vào vận khí (action_chovankhi theo lệnh đó: chiêu không ra thì mở khoá sớm) rồi theo thanh vận khí
        thoidiemhientai = time.time()
        self._khoavankhitrieuhoi = {
            "batdau": thoidiemhientai,
            "toida": thoidiemhientai + THOIGIANKHOAVANKHITRIEUHOITOIDA,
            "caulenhduocpheps": set(caulenhduocpheps),
            "ten": ten,
        }
        cho = self.action_chovankhi(vitrikynang, next(iter(caulenhduocpheps), None), ten = ten)
        self._khoavankhitrieuhoi["cho"] = cho
        self._inlog(f"[KHOÁ VẬN KHÍ {ten}] bắt đầu, cho phép {sorted(caulenhduocpheps)}")
        return cho

    def get_is_dangxuatchieu(self):
        # Đang xuất chiêu (tư thế tấn công vật lý 6 / phép 9; 11 chỉ còn khi bot tự ghi) hoặc chưa hết THOIGIANKHUNGSAUXUATCHIEU giây
        # khựng sau khi hết tư thế xuất chiêu (game không có tư thế riêng cho khựng): vẫn được dùng kỹ năng nhưng TUYỆT ĐỐI không
        # di chuyển (di chuyển lúc này vẫn tính hồi chiêu mà chiêu mất tác dụng). Đo 2026-10-25: game giữ tư thế 6 ~0.68s rồi về
        # thẳng 1 / 2. Các hàm phát lệnh di chuyển đều kiểm tra hàm này; luồng nhanh gọi liên tục để cập nhật mốc xuất chiêu
        # Chỉ tính chiêu cần đứng yên (set_is_chieucanngatdichuyen theo chiêu bot gửi gần nhất). Hoạt ảnh xuất chiêu (~0.68s) luôn giữ
        # trọn (cắt ngang bị game đánh vi phạm); phần khựng sau đó thì thả sớm khi chiêu đã tác động xong: mục tiêu đã chết / biến mất,
        # hoặc mục tiêu đã hiện số bay (server báo trúng, _is_muctieudatrungchieu); không thấy thì giữ tối đa THOIGIANKHUNGSAUXUATCHIEU
        thoidiemhientai = time.time()
        self._dohoatanhchieu()
        if self._is_giuchandelay0():
            return True
        idtuthe = self.get_idtuthenhanvat()
        # Đã bỏ ghi tư thế về đứng im khi mục tiêu hiện số bay (thêm 2026-11-07, bỏ 2026-11-09 theo người dùng): không cắt được hoạt
        # ảnh nên game đặt lại tư thế 6 (Lạc Kích ~45% lần), tua hoạt ảnh thì hình nhân vật vẽ lệch chỗ thật
        if self._is_chieucanngatdichuyen \
                and idtuthe in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
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

    def action_giuchansauchieudelay0(self, diachimuctieu, tenchieu = ""):
        # Chiêu delay 0 vừa vào hồi chiêu: giữ chân (get_is_dangxuatchieu True => mọi hàm đi bị chặn, đang đi thì bị ngắt) tới khi mục
        # tiêu hiện số bay mới, tối đa THOIGIANGIUCHANDELAY0 giây (xem _is_giuchandelay0)
        if not diachimuctieu:
            return
        self._giuchandelay0 = {"diachi": diachimuctieu, "id": self.get_iddoituong(diachimuctieu), "ten": tenchieu,
                               "sobay": self._docsobaydoituong(diachimuctieu), "batdau": time.time()}

    def get_is_giuchandelay0(self):
        return self._giuchandelay0 is not None

    def _is_giuchandelay0(self):
        giu = self._giuchandelay0
        if not giu:
            return False
        thoigian = time.time() - giu["batdau"]
        diachi = giu["diachi"]
        lydo = None
        if self.get_iddoituong(diachi) != giu["id"] or self.get_is_nhanvatdachet(diachi):
            lydo = "mục tiêu chết / mất"
        elif thoigian >= THOIGIANGIUCHANDELAY0:
            lydo = "hết giờ, không thấy số bay"
        else:
            sobay = self._docsobaydoituong(diachi)
            if sobay:
                (giatri, dem), cu = sobay, giu["sobay"]
                for i in range(10):
                    if giatri[i] > 0 and (dem[i] <= DEMSOBAYMOI or not cu or giatri[i] != cu[0][i] or dem[i] < cu[1][i]):
                        lydo = f"thấy số bay {giatri[i]}"
                        break
        if not lydo:
            return True
        self._giuchandelay0 = None
        self._inlog(f"[GIỮ CHÂN DELAY 0] {giu['ten']}: {lydo} sau {thoigian:.2f}s => thả")
        return False

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

    def get_sobaydoituong(self, diachi):
        # ((10 giá trị), (10 bộ đếm)) số bay trên đầu đối tượng, chỉ là sát thương do chính mình gây ra (xem _docsobaydoituong); None khi lỗi
        return self._docsobaydoituong(diachi)

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
        # Khoá từ lúc gửi lệnh triệu hồi: giữ trong lúc chờ vào vận khí (_get_is_dangchovankhi), sau đó giữ tới khi game hết vận khí (tối đa THOIGIANKHOAVANKHITRIEUHOITOIDA)
        khoa = self._khoavankhitrieuhoi
        if not khoa:
            return False
        thoidiemhientai = time.time()
        if thoidiemhientai < khoa["toida"] and (self._get_is_dangchovankhi() or self._get_is_dangvankhitrongame()):
            return True
        self._khoavankhitrieuhoi = None
        self._inlog(f"[KHOÁ VẬN KHÍ {khoa.get('ten', 'TRIỆU HỒI')}] kết thúc sau {round(thoidiemhientai - khoa['batdau'], 1)}s")
        if khoa.get("ten") in TENKHOAVANKHIHOITHANHs and self.giuhoithanh is not None:
            # Hết vận khí về thành: giữ chỗ thêm khoảng nghỉ ngẫu nhiên rồi mới nhường bot khác (GiuHoiThanh)
            cho = khoa.get("cho")
            try:
                self.giuhoithanh.ketthuc(is_davao = bool(cho.get("vao")) if cho else True)
            except Exception as err:
                self._inlog(f"[HỒI THÀNH PHÙ] Lỗi nhả giữ chỗ: {err}")
        return False

    def get_is_khoavankhitrieuhoibaothu(self):
        # Khoá vận khí đúng của triệu hồi bảo thú (không phải Hồi Thành Phù)
        khoa = self._khoavankhitrieuhoi
        return bool(khoa) and khoa.get("ten") == "TRIỆU HỒI" and self.get_is_khoavankhitrieuhoi()

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
        if self._get_is_dangchovankhi():
            return True
        return self._get_is_dangvankhitrongame()

    def _get_is_dangvankhitrongame(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_VANKHI)
        if not x or read_int(self.tientrinh, x + 0xD8) != TRANGTHAIVANKHI_DANGVANKHI:
            return False
        # Gói máy chủ bắt đầu vận khí ghi + 0xF8 timeGetTime lúc nhận, + 0xFC thời lượng (ms); gói kết thúc đổi + 0xD8 sang thành công /
        # thất bại rồi ẩn thanh. Dis giữa lúc vận khí thì gói kết thúc không tới, đăng nhập lại (cùng client) thanh đứng 100% mãi, game cũng
        # chặn thao tác vì vtable[0] (+ 0x34 đang hiện) => quá thời lượng thì đóng bằng vtable[1](0) (xq + 0xB4B40: tắt + 0x34, xoá trạng thái)
        # Hiệu có dấu: game ghi + 0xF8 có thể mới hơn timeGetTime bot vừa đọc vài ms (game ghi xen giữa / độ phân giải timer khác),
        # để không dấu thì ra ~4294967s => tưởng kẹt mà đóng thanh ngay lúc vừa vào vận khí (log 2026-11-02 Lôi Động Cửu Thiên)
        dachay = (ctypes.windll.winmm.timeGetTime() - read_int(self.tientrinh, x + 0xF8)) & 0xFFFFFFFF
        if dachay >= 0x80000000:
            return True
        if dachay <= (read_int(self.tientrinh, x + 0xFC) & 0xFFFFFFFF) + THOIGIANVANKHIKETTHEM * 1000:
            return True
        if time.time() - self._thoidiemdongvankhiket > 1.:
            self._thoidiemdongvankhiket = time.time()
            self._inlog(f"[VẬN KHÍ KẸT] '{read_string(self.tientrinh, x + 0xE0).strip()}' đã {round(dachay / 1000)}s, đóng thanh vận khí")
            self._goivtableanhien(DC.TG_VANKHI, False)
        return False

    def get_is_dakhoitaothongtinbando(self):
        x = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        if not x:
            return False
        x = read_int(self.tientrinh, x + DC.TG_TIMDUONG)
        return x > 0

    def get_bandotimduong(self):
        # Bản đồ của đích tìm đường client đang đi (0 = không có đích)
        a = read_int(self.tientrinh, self.diachixq + DC.THONGTINGAME)
        a = read_int(self.tientrinh, a + DC.TG_TIMDUONG) if a else 0
        return read_int(self.tientrinh, a + DC.TD_BANDO) if a else 0

    def action_tudongtimduong(self, x, y, idbando, is_lotrinh = True):
        # Đặt đích tìm đường mới là bắt đầu di chuyển => ngắt vận khí triệu hồi / mất tác dụng chiêu đang xuất
        # (huỷ tìm đường thì qua action_ngungtudongtimduong, không chặn)
        if (x or y) and (self._is_vohieuhoadichuyen or self.get_is_khoavankhitrieuhoi() or self.get_is_dangxuatchieu()):
            return False
        if x or y:
            dichtrongtran = self._kepdichtrongtrando(x, y)
            if dichtrongtran is None:
                return False
            x, y = round(dichtrongtran[0]), round(dichtrongtran[1])
            # Lưới vật cản chỉ có của bản đồ đang đứng
            if idbando == self.get_idbandohientai():
                x, y = self.get_oditduocganhat(x, y)
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
        if is_dichmoi and self._dichchaytrondaghi is not None:
            # Chuỗi hướng chạy trốn (action_dichuoihuongchaytron ghi thẳng CHUOIDUONGDI) còn dở thì client đi nốt chuỗi đó rồi mới theo
            # đích tìm đường mới => cắt chuỗi. Log 835 2026-11-14: đã chuyển sang "Chạy tới cổng (244, 254)" mà vẫn đi thêm 8 bước
            # ngược về (208, 224) theo chuỗi chạy trốn cũ
            self.set_idlenhdichuyen(0)
            self._dichchaytrondaghi = None
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

    def get_tenmonphai(self, diachicosothongtinnhanvat = None):
        # Không truyền địa chỉ (hoặc là mình): theo kỹ năng ô đầu. Người chơi khác: theo dòng "Môn phái" của lần "desc user" gần nhất
        # (action_hoibangphai), chưa hỏi được thì None. Mã như TENMONPHAI, môn phái chưa có trong TENMONPHAI thì là tên game in ra
        if diachicosothongtinnhanvat:
            idnguoichoi = self.get_idnguoichoi(diachicosothongtinnhanvat)
            if idnguoichoi != self.get_idnguoichoi():
                return self._monphainguoichoi_map.get(idnguoichoi)
        return MONPHAI_MAP.get(self.get_idkynang(0, 0)) or self._monphainguoichoi_map.get(self.get_idnguoichoi())

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

    def get_danhsachtenbaothugiangho(self, soo = 10):
        # Tên các bảo thú giang hồ đang có (cả con chưa triệu hồi): mỗi ô 0x1670 byte tính từ cùng gốc, id + 0x47C (0 = ô trống), tên + 0x4F5
        diachi = self.get_diachicosobaothugiangho()
        if not diachi:
            return []
        tens = []
        for k in range(soo):
            o = diachi + 0x1670 * k
            if read_int(self.tientrinh, o + 0x47C) > 0:
                tens.append(read_bytes(self.tientrinh, o + 0x4F5, 0x20).split(b"\0")[0].decode("utf-8", "ignore"))
        return tens

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
