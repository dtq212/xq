import math
import os
import random
import re
import time

import pymem
import win32gui
import win32con

from hangso_xq import *
from moitruong_xq import MoiTruong, DOUUTIEN_THAP, DOUUTIEN_KHANCAP, DOUUTIEN_CAO
from tienich_xq import luuthietlap as util_luuthietlap
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam
from tienich_xq import tailotrinhmau as util_tailotrinhmau, luulotrinhmau as util_luulotrinhmau


class TacTu:
    def __init__(self, moitruong: MoiTruong):
        self._thoidiemhettangbaodogannhat = 0.
        self._thoidiemmuaautogannhat = 0.
        self._thoidiemsudungditinhdaiphapgannhat = 0.
        self._thoidiemsudungluuhuyetthuatgannhat = 0.
        self._thoidiemkiemtranpcmuavatphamgannhat = 0.
        self._is_tudongmuavatpham = True
        self._diachicosovatphamnhatduphong = False
        self._idquaidautien = 0
        self._thoidiemvohieuhoatatchucnangmoronggannhat = 0.
        self._thoidiemvohieuhoabatchucnangmoronggannhat = 0.
        self._thoidiemsudungthaotacbaothugannhat = 0.
        self._thoidiemtamngungsudungkynang = 0.
        self._thoidiemhoiphucbaothugannhat = 0.
        self._is_tudongdieukhienbaothu = True
        self._is_baothukynangtrieuhoihetnoiluc = False
        self._is_baothukynangtrieuhoihetsinhluc = False
        self._thoidiemdocsachgannhat = 0.
        self._thoidiemsudungbattiendongannhat = 0.
        self._thoidiemdichientruonggannhat = 0.
        self._thoidiembatdaudendiem = 0.
        self._thoidiemlogdebug = 0.
        self._solanthatbaikhaithien = 0
        self._solanthatbaikhaithientoida = 3
        self._thoidiembiphatkhaithien = 0.
        self._is_thucsondao = False
        self.moitruong = moitruong

        self._is_tudongtheosautruongnhom = True
        self._is_tudongbattheosaunhom = False
        self._is_tudongtimkiemmuctieu = True
        self._is_tudongsudungkynang = True
        self._is_tudongsudungvatpham = True
        self._is_tudongnhatvatpham = True
        self._is_chidanhnguoichoi = False
        self._is_tudongtodoi = True
        self._is_tudongphucsinh = True
        self._is_tudongsuavatpham = True
        self._is_tudongtrieuhoibaothugiangho = False
        self._is_tudongchaylenbandovuachet = True
        self._is_tudongxepchongvatpham = True
        self._is_tudongkhaikhoang = False
        self._thoidiemkhaikhoanggannhat = 0.
        self._yeucaukhaikhoang = None

        self._diachicosomuctieuduphong = 0
        self._diachicosokhaikhoang = 0
        self._idkhoangbiloi_map = {}
        self._idkhoangdangtheo = 0
        self._thoidiembatdautheokhoang = 0.
        self._idbandolanquetkhaikhoangtruoc = 0
        self._is_nhieumuctieugan3 = False
        self._is_nhieumuctieugan5 = False
        self._is_nhieumuctieugan7 = False
        self._is_nhieumuctieugan9 = False
        self._is_nhieumuctieuganbanthan3 = False
        self._is_nhieumuctieuganbanthan5 = False
        self._is_nhieumuctieuganbanthan7 = False
        self._is_nhieumuctieuganbanthan9 = False
        self._soluongnhieumuctieu = 2
        self._soluongquaigomtoithieu = 3
        self._is_tudonggomquai = False
        self._is_danggomquai = False
        self._danhsachidquaidagom = set()
        self._yeucaugomquai = None

        self._is_uutienmuctieupk = True
        self._khoangcachtoidatruongnhom = 6.
        # Tầm đánh thực tế của nhân vật (học từ lần tiếp cận mục tiêu gần nhất), mặc định tầm xa đã trừ hao
        self._khoangcachvoitoimuctieu = KHOANGCACHSUDUNGKYNANGTAMXA - 3.
        # Đang trên đường về chỗ đứng riêng quanh trưởng nhóm
        self._is_dangvevitritheosau = False
        # Khi chạy theo lộ trình: quái phải cách một điểm đánh không quá bấy nhiêu ô mới được nhận làm mục tiêu/gom
        self._bankinhdiemdanh = 18.

        self._tenmuctieutancongs = set()
        self._tenmuctieukhongtancongs = set(TENMUCTIEUKHONGTANCONGs)
        self._tenvatphamnhats = set()

        self._thoidiembattattheosaunhomgannhat = time.time()
        self._thoidiemtamngungkhaithientichdia = time.time()
        self._thoidiemkiemtrahieuunggannhat = time.time()
        self._thoidiemnhatvatphamgannhat_map = {}
        self._thoidiemdoimaupkgannhat = time.time()
        self._thoidiemtudongtrieuhoibaothugiangho = time.time()
        self._thoidiemsudungvatphamgannhat = time.time()
        self._thoidiemsudungthucanbaothugannhat = time.time()
        self._thoidiemsudungvatphamhoinoilucgannhat = time.time()
        self._thoidiemsudungvatphamhoisinhlucgannhat = time.time()
        self._thoidiemsudungthanhtamdangannhat = time.time()
        self._thoidiemsudunghoithanhphugannhat = time.time()
        self._thoidiemxepchongvatphamgannhat = time.time()
        self._thoidiemvutvatphamgannhat = time.time()
        self._diachicosovatphamkhongnhat_map = {}
        self._thoidiemthaydoivatphamdangnhatgannhat = time.time()
        self._diemdanhxungquanhs = []
        self._iddiemdanhxungquanhhientai = -1
        # Lộ trình mẫu đang dùng dạng "<id bản đồ>|<tên mẫu>|<1 nếu đi ngược chiều>", rỗng nếu tự đặt điểm
        self._lotrinhmaudangdung = ""
        self._is_lotrinhtuchon = False
        self._thoidiemkiemtralotrinhgannhat = 0.
        # Tạm ngưng toàn bộ hoạt động khi phát hiện người chơi ẩn thân xung quanh (đang farm & bán rác)
        self._thoidiemhettamngung = 0.
        self._lydotamngung = ""
        self._thoidiemkiemtraanthangannhat = 0.
        # Lần gần nhất TỰ phát hiện ẩn thân (chia sẻ cho nhân vật khác cùng bản đồ)
        self._thoidiemphathienanthan = 0.
        self._tenanthanphathien = ""
        self._thoigiantamngungphathien = 0.
        # Gán từ CuaSo để biết các cửa sổ khác đang dùng lộ trình mẫu nào
        self.shared_data = None
        self.idcuaso = None
        self._diemdanhxungquanhhientai = None
        self._thoidiemloggomquai = 0.

        self._idmuctieubiloi_map = {}
        self._idmuctieudangtheokiemtraket = 0
        self._thoidiemdungimkiemtraket = 0.

        self._yeucaunhatvatpham = None
        self._yeucautheosautruongnhom = None
        self._yeucautancong = None
        self._yeucautudo = None

        self._thoidiemtamngungdichuyensudungkynang = 0.
        self._khoangcachtimkiemmuctieu = 18.
        self._is_tudongdichuyendiemdanhxungquanh = False
        self._is_tudongdoimaupk = False

        self._idbandovuachet = 0
        self._diachicosovatphamdangnhat = 0

        self._solansudungkhaithientichdia = 0
        self._solansudungluutinhtruymang = 0

        self._is_chantangcapdo = False
        self._idbandomuctieudangchon = 0

        self._idquaidangkeo = 0
        self._thoidiembatdaukeo = 0.
        self._thoidiemtrieuhoithienbinhgannhat = 0.
        self._thoidiemraidauthanhbinhgannhat = 0.
        self._idgomtheodoiket = 0
        self._khoangcachgomtotnhat = 0.
        self._thoidiemgomcaithiengannhat = 0.
        self._is_tudongvebanrac = False
        self._trangthaiveban = 0  # 0: Idle, 1: Đang về, 2: Đang đi shop, 3: Đang bán, 4: Đang quay lại
        self._thoidiemchuyentrangthai = 0.

        self._thoidiemhoithanhphu = 0.  # Timer cho việc hồi thành phù

        self._toadokiemtraket = (0, 0)
        self._thoidiembatdaukiemtraket = 0.

        self._thoidiemphatamlacmapgannhat = 0.
        self._thoidiemphatamdayhanhtrang = 0.
        self._thoidiemdichuyentudogannhat = 0.
        self._is_tudongdichientruong = False

        self._is_yeucauvohieuhoadichuyen = False
        self._is_uutienbaothukynangtrieuhoi = False
        self._is_khonguutienbaothugiangho = False

        self._is_chedobufftoanbang = False
        self._is_khongcongidebuff = False

        self._thoidiemsudungbaothuvatphamgannhat = time.time()
        self._thoidiemkiemtrakhongcongidebuffgannhat = 0.

        self._is_battudongtancongvatly = False
        self._thoidiemtodoigannhat_map = {}
        self._thoidiemxulytodoigannhat = 0.
        # Đồng đội hạng cao hơn đang được mời vào nhóm (để biết đã mời bao lâu)
        self._idmoihangcaohon = 0
        self._thoidiembatdaumoihangcaohon = 0.
        self._thoidiemcaituhoansinh_map = {}

        self._thoidiemsudungamkichgannhat = 0.
        self._is_kynangamkichsansang = False

        self._thoidiemsudungthichsatgannhat = 0.
        self._is_kynangthichsatsansang = False

        self._thoidiemsudungbisatgannhat = 0.
        self._is_kynangbisatsansang = False

        self._thoidiemsudungnhiephonchamgannhat = False
        self._is_kynangnhiephonchamsansang = False

        self._thoidiembattathieuungphapbaogannhat = 0.

        self._is_kynangmatamthuatsansang = False
        self._thoidiemsudungmatamthuatgannhat = 0.

        self._is_tudongdaotangbaodo = False
        self._yeucaudaotangbaodo = None

        self._thoidiembuffkimchamgannhat_map = {}
        self._thoidiembuffnganchamgannhat_map = {}
        self._thoidiembuffcuongthethuatgannhat_map = {}

        self._is_nganchamdoachsansang = False
        self._is_kimchamdoachsansang = False
        self._is_cuongthethuatsansang = False

        self._idnguoichoibuffnganchamgannhat = 0
        self._idnguoichoibuffkimchamgannhat = 0
        self._idnguoichoibuffcuongthethuatgannhat = 0

        self._thoidiembuffnoikhanggannhat_map = {}
        self._is_tieuchuthiensansang = False
        self._idnguoichoibuffnoikhanggannhat = 0

        self._solanthatbailuutinhtruymang = 0
        self._solanthatbailuutinhtruymangtoida = 3
        self._thoidiembiphatluutinhtruymang = 0.
        self._thoidiemtamngungluutinhtruymang = 0.
        self._idmuctieuluutinhtruymang = 0

        self._is_khaithientichdiasansang = False
        self._is_luutinhtruymangsansang = False

        self._is_dangchaybukhoangcach = False
        self._thoidiemvohieuquadichuyennhatvatpham = 0.0
        self._is_tudongbattatchucnangmorong = False
        # Tránh vùng cấm (VUNGCAM_MAP) khi chọn mục tiêu, nhặt đồ, gom quái và di chuyển
        self._is_tranhvungcam = True

        self._diachidoituongcanbuffthuccotmaoson = None
        self._diachidoituongcanbuffthucgiapmaoson = None
        self._diachidoituongcanbuffthuctammaoson = None
        self._diachidoituongcanbuffammanhapthemaoson = None
        self._thoidiemlammoitrangthaigannhat = 0.

        self._thoidiemhoandoiphapbao = 0.
        self._vitriphapbaovuahoandoi = -1
        self._tenphapbaocu = None
        self._mucsinhluckhihoandoi = 0
        self._tenphapbaokhonghuhongdangmac = None
        self._thoidiemthumaclaiphapbao = 0.

        self._is_tudongsudungkynangbaothu = False

        self._trangthaitrieuhoibaothuvatpham = 0
        self._thoidiemchuyentrangthaitrieuhoibaothuvatpham = 0.
        self._thoidiemyeucaubaothuvatphamdoilenh = 0.

        self._is_danguutiennhatdo = False

        self._thoidiemkiemtranpcsuavatphamgannhat = 0.

        self._thoidiemdichuyendaotangbaodogannhat = 0.
        self._thoidiemsudungcaoboctacdangannhat = 0.
        self._thoidiemclickchientruonggannhat = 0.

        self._index_thuduongson = 0
        self._index_thuyhoason = 0
        self._index_hamcocquan = 0

        self._diachidoituongcanbuffhothekimcangdaohoanguyen = None

        self._diachidoituongcanhoisinhvanmongcoc = None
        self._diachidoituongcanbufftaytranquyetvanmongcoc = None
        self._diachidoituongcanbufftaytranquyet2vanmongcoc = None
        self._diachidoituongcanbufflinhkhihothevanmongcoc = None
        self._diachidoituongcanbommauvanmongcoc = None
        self._diachidoituongcanbuffkimchamvanmongcoc = None
        self._diachidoituongcanbuffnganchamvanmongcoc = None
        self._diachidoituongcanbuffcuongthethuatvanmongcoc = None
        self._diachidoituongcanbuffphonganthuatvanmongcoc = None
        self._diachidoituongcanbuffhuyenquangthiemanhvanmongcoc = None
        self._thoidiemsudungtusamdongannhat = 0.

    def __del__(self):
        try:
            self.moitruong.action_bochantangcapdo()
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass

    def luuthietlap(self, idnguoichoi):
        # Lưu theo ID người chơi (cố định, còn tên nhân vật thì có thể đổi)
        if not idnguoichoi or idnguoichoi <= 0:
            return

        thietlap = {
            "_is_tudongbattheosaunhom": self._is_tudongbattheosaunhom,
            "_is_tudongtheosautruongnhom": self._is_tudongtheosautruongnhom,
            "_is_tudongtimkiemmuctieu": self._is_tudongtimkiemmuctieu,
            "_is_tudongsudungkynang": self._is_tudongsudungkynang,
            "_is_uutienmuctieupk": self._is_uutienmuctieupk,
            "_is_tudongsudungvatpham": self._is_tudongsudungvatpham,
            "_is_tudongnhatvatpham": self._is_tudongnhatvatpham,
            "_is_chidanhnguoichoi": self._is_chidanhnguoichoi,
            "_is_tudongtodoi": self._is_tudongtodoi,
            "_is_thucsondao": self._is_thucsondao,
            "_is_chantangcapdo": self._is_chantangcapdo,
            "_is_tudongdichuyendiemdanhxungquanh": self._is_tudongdichuyendiemdanhxungquanh,
            "_diemdanhxungquanhs": self._diemdanhxungquanhs,
            "_lotrinhmaudangdung": self._lotrinhmaudangdung,
            "_is_tudonggomquai": self._is_tudonggomquai,
            "_is_tudongvebanrac": self._is_tudongvebanrac,
            "_is_chedobufftoanbang": self._is_chedobufftoanbang,
            "_is_tudongdichientruong": self._is_tudongdichientruong,
            "_is_tudongkhaikhoang": self._is_tudongkhaikhoang,
            "_is_tudongdaotangbaodo": self._is_tudongdaotangbaodo,
            "_tenmuctieutancongs": self._tenmuctieutancongs,

            "_is_uutienbaothukynangtrieuhoi": self._is_uutienbaothukynangtrieuhoi,
            "_tenmuctieukhongtancongs": self._tenmuctieukhongtancongs,
            "_tenvatphamnhats": self._tenvatphamnhats,
            "_khoangcachtoidatruongnhom": self._khoangcachtoidatruongnhom,
            "_bankinhdiemdanh": self._bankinhdiemdanh,
            "_is_tudongtrieuhoibaothugiangho": self._is_tudongtrieuhoibaothugiangho,
            "_is_tudongbattatchucnangmorong": self._is_tudongbattatchucnangmorong,
            "_is_tudongsudungkynangbaothu": self._is_tudongsudungkynangbaothu,
            "_is_tranhvungcam": self._is_tranhvungcam,
        }
        util_luuthietlap(str(idnguoichoi), thietlap)

    def taithietlap(self, idnguoichoi, tennhanvat = None):
        if not idnguoichoi or idnguoichoi <= 0:
            return

        # Có một giai đoạn thiết lập bị lưu theo tên nhân vật: nếu file theo tên mới hơn file theo ID thì lấy file theo tên
        khoathietlap = str(idnguoichoi)
        if tennhanvat:
            duongdanid = util_duongdanthietlap(str(idnguoichoi))
            duongdanten = util_duongdanthietlap(tennhanvat)
            if os.path.exists(duongdanten) and (not os.path.exists(duongdanid) or os.path.getmtime(duongdanten) > os.path.getmtime(duongdanid)):
                khoathietlap = str(tennhanvat)

        thietlap = util_taithietlap(khoathietlap)
        if thietlap:
            if "_is_tudongbattheosaunhom" in thietlap: self._is_tudongbattheosaunhom = thietlap["_is_tudongbattheosaunhom"]
            if "_is_tudongtheosautruongnhom" in thietlap: self._is_tudongtheosautruongnhom = thietlap["_is_tudongtheosautruongnhom"]
            if "_is_tudongtimkiemmuctieu" in thietlap: self._is_tudongtimkiemmuctieu = thietlap["_is_tudongtimkiemmuctieu"]
            if "_is_tudongsudungkynang" in thietlap: self._is_tudongsudungkynang = thietlap["_is_tudongsudungkynang"]
            if "_is_uutienmuctieupk" in thietlap: self._is_uutienmuctieupk = thietlap["_is_uutienmuctieupk"]
            if "_is_tudongsudungvatpham" in thietlap: self._is_tudongsudungvatpham = thietlap["_is_tudongsudungvatpham"]
            if "_is_tudongnhatvatpham" in thietlap: self._is_tudongnhatvatpham = thietlap["_is_tudongnhatvatpham"]
            if "_is_chidanhnguoichoi" in thietlap: self._is_chidanhnguoichoi = thietlap["_is_chidanhnguoichoi"]
            if "_is_tudongtodoi" in thietlap: self._is_tudongtodoi = thietlap["_is_tudongtodoi"]
            if "_is_thucsondao" in thietlap: self._is_thucsondao = thietlap["_is_thucsondao"]
            if "_is_chantangcapdo" in thietlap: self._is_chantangcapdo = thietlap["_is_chantangcapdo"]
            if "_is_tudongdichuyendiemdanhxungquanh" in thietlap: self._is_tudongdichuyendiemdanhxungquanh = thietlap["_is_tudongdichuyendiemdanhxungquanh"]
            if "_diemdanhxungquanhs" in thietlap: self._diemdanhxungquanhs = thietlap["_diemdanhxungquanhs"]
            if "_lotrinhmaudangdung" in thietlap: self._lotrinhmaudangdung = thietlap["_lotrinhmaudangdung"]
            if "_is_tudonggomquai" in thietlap: self._is_tudonggomquai = thietlap["_is_tudonggomquai"]
            if "_is_tudongvebanrac" in thietlap: self._is_tudongvebanrac = thietlap["_is_tudongvebanrac"]
            if "_is_chedobufftoanbang" in thietlap: self._is_chedobufftoanbang = thietlap["_is_chedobufftoanbang"]
            if "_is_tudongdichientruong" in thietlap: self._is_tudongdichientruong = thietlap["_is_tudongdichientruong"]
            if "_is_tudongkhaikhoang" in thietlap: self._is_tudongkhaikhoang = thietlap["_is_tudongkhaikhoang"]
            if "_is_tudongdaotangbaodo" in thietlap: self._is_tudongdaotangbaodo = thietlap["_is_tudongdaotangbaodo"]
            if "_tenmuctieutancongs" in thietlap: self._tenmuctieutancongs = thietlap["_tenmuctieutancongs"]

            if "_is_uutienbaothukynangtrieuhoi" in thietlap: self._is_uutienbaothukynangtrieuhoi = thietlap["_is_uutienbaothukynangtrieuhoi"]
            if "_tenmuctieukhongtancongs" in thietlap: self._tenmuctieukhongtancongs = thietlap["_tenmuctieukhongtancongs"]
            if "_tenvatphamnhats" in thietlap: self._tenvatphamnhats = thietlap["_tenvatphamnhats"]
            if "_khoangcachtoidatruongnhom" in thietlap: self._khoangcachtoidatruongnhom = float(thietlap["_khoangcachtoidatruongnhom"])
            if "_bankinhdiemdanh" in thietlap: self._bankinhdiemdanh = float(thietlap["_bankinhdiemdanh"])
            if "_is_tudongtrieuhoibaothugiangho" in thietlap: self._is_tudongtrieuhoibaothugiangho = thietlap["_is_tudongtrieuhoibaothugiangho"]
            if "_is_tudongbattatchucnangmorong" in thietlap: self._is_tudongbattatchucnangmorong = thietlap["_is_tudongbattatchucnangmorong"]
            if "_is_tudongsudungkynangbaothu" in thietlap: self._is_tudongsudungkynangbaothu = thietlap["_is_tudongsudungkynangbaothu"]
            if "_is_tranhvungcam" in thietlap: self._is_tranhvungcam = thietlap["_is_tranhvungcam"]

    def battat_tranhvungcam(self):
        self._is_tranhvungcam = not self._is_tranhvungcam
        if self._is_tranhvungcam:
            phatam("Bật tránh vùng cấm")
        else:
            phatam("Tắt tránh vùng cấm")

    def battat_tudongsudungkynangbaothu(self):
        self._is_tudongsudungkynangbaothu = not self._is_tudongsudungkynangbaothu
        if self._is_tudongsudungkynangbaothu:
            phatam("Bật dùng kỹ năng bảo thú")
        else:
            phatam("Tắt dùng kỹ năng bảo thú")

    def battat_tudongbattatchucnangmorong(self):
        self._is_tudongbattatchucnangmorong = not self._is_tudongbattatchucnangmorong
        if self._is_tudongbattatchucnangmorong:
            phatam("Bật tự động bật tắt chức năng mở rộng")
        else:
            phatam("Tắt tự động bật tắt chức năng mở rộng")

    def battat_tudongtrieuhoibaothugiangho(self):
        self._is_tudongtrieuhoibaothugiangho = not self._is_tudongtrieuhoibaothugiangho
        if self._is_tudongtrieuhoibaothugiangho:
            phatam("Bật tự động triệu hồi bảo thú")
        else:
            phatam("Tắt tự động triệu hồi bảo thú")

    def thietlap_khoangcachtheosau(self, khoangcach):
        self._khoangcachtoidatruongnhom = float(khoangcach)

    def thietlap_bankinhdiemdanh(self, bankinh):
        self._bankinhdiemdanh = max(1., float(bankinh))

    def _kiemtrathuchienvohieuhoadichuyen(self):
        if self._is_yeucauvohieuhoadichuyen:
            self.moitruong.action_vohieuhoadichuyen()
        else:
            self.moitruong.action_tatvohieuhoadichuyen()

    def action_xulyuutiendichuyen(self):
        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        if idtuthenhanvat == TUTHENHANVAT_DICHUYEN:
            self._is_battudongtancongvatly = False

        # Lớp chặn vùng cấm cuối cùng ở môi trường theo tùy chọn tránh vùng cấm
        self.moitruong.is_tranhvungcam = self._is_tranhvungcam

        self._kiemtrathuchienvohieuhoadichuyen()

        is_log = False

        # if time.time() - self._thoidiemlogdebug > 2.0:
        #     is_log = True
        #     self._thoidiemlogdebug = time.time()

        if self.moitruong.get_is_nhanvatdachet():
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Nhân vật đang CHẾT")
            return
        if self.moitruong.get_is_dangclickchuottrai():
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang CLICK CHUỘT TRÁI")
            return
        if self.moitruong.get_is_dangvankhi():
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang VẬN KHÍ")
            return
        if time.time() - self._thoidiemtamngungdichuyensudungkynang < 0.:
            if idtuthenhanvat == TUTHENHANVAT_DICHUYEN:
                self.moitruong.action_ngatdichuyen()
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng để dùng SKILL")
            return
        if self._trangthaiveban != 0:
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng để về bán rác")
            return

        is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom() and self.moitruong.get_toadotruongnhom() != (65535, 65535)

        is_yeucaunhatvatpham = self._yeucaunhatvatpham and not is_anhhuongboitruongnhom and time.time() - self._thoidiemvohieuquadichuyennhatvatpham > 0.

        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieudangchonlanguoichoi = diachimuctieudangchon and self.moitruong.get_is_nguoichoi(diachimuctieudangchon)
        is_muctieudangchonlabaothukynangtrieuhoi = self.moitruong.get_is_baothukynangtrieuhoi(diachimuctieudangchon)
        is_muctieudangchonlabaothugiangho = self.moitruong.get_is_baothugiangho(diachimuctieudangchon)
        is_muctieupk = is_muctieudangchonlanguoichoi or is_muctieudangchonlabaothukynangtrieuhoi or is_muctieudangchonlabaothugiangho

        yeucauduocchon = None
        lydochon = "KHÔNG CÓ"

        is_yeucaunhatvatphamganhon = False
        if is_yeucaunhatvatpham and not is_muctieupk and self._is_tudongvebanrac:
            khoangcachnhatvatpham = self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat) if self._diachicosovatphamdangnhat else KHOANGCACHTOIDAHOPLE
            khoangcachtancong = KHOANGCACHTOIDAHOPLE
            if self._yeucautancong and self._yeucautancong.get("diachimuctieu"):
                khoangcachtancong = self.moitruong.get_khoangcach(self._yeucautancong.get("diachimuctieu"))
            elif diachimuctieudangchon:
                khoangcachtancong = self.moitruong.get_khoangcach(diachimuctieudangchon)

            if khoangcachnhatvatpham + 0.5 < khoangcachtancong:
                is_yeucaunhatvatphamganhon = True

        # Vật phẩm ưu tiên (VATPHAMUUTIENNHATs) bỏ qua mọi điều kiện: mục tiêu PK, theo nhóm, khóa nhặt sau khi dùng skill
        is_yeucaunhatvatphamuutien = bool(self._yeucaunhatvatpham and self._yeucaunhatvatpham.get("is_uutien"))

        self._is_danguutiennhatdo = is_yeucaunhatvatphamganhon or is_yeucaunhatvatphamuutien

        if is_yeucaunhatvatphamuutien:
            yeucauduocchon = self._yeucaunhatvatpham
            lydochon = "NHẶT ĐỒ ƯU TIÊN"
        elif is_yeucaunhatvatphamganhon:
            yeucauduocchon = self._yeucaunhatvatpham
            lydochon = "NHẶT ĐỒ (GẦN HƠN MỤC TIÊU)"
        elif self._yeucautancong:
            yeucauduocchon = self._yeucautancong
            lydochon = "TẤN CÔNG"
        elif is_yeucaunhatvatpham and not is_muctieupk:
            yeucauduocchon = self._yeucaunhatvatpham
            lydochon = "NHẶT ĐỒ"
        elif self._yeucaukhaikhoang and not is_muctieupk:
            yeucauduocchon = self._yeucaukhaikhoang
            lydochon = "KHAI KHOÁNG"
        elif self._yeucaudaotangbaodo and not is_muctieupk:
            yeucauduocchon = self._yeucaudaotangbaodo
            lydochon = "ĐÀO TÀNG BẢO ĐỒ"
            self._thoidiemdichuyendaotangbaodogannhat = time.time()
        elif self._yeucaugomquai and not is_anhhuongboitruongnhom and not is_muctieupk:
            yeucauduocchon = self._yeucaugomquai
            lydochon = "GOM QUÁI"
        elif self._yeucautheosautruongnhom:
            yeucauduocchon = self._yeucautheosautruongnhom
            lydochon = "THEO NHÓM"
        elif self._yeucautudo and not is_anhhuongboitruongnhom:
            if time.time() - self._thoidiemdichuyentudogannhat > 2.0:
                yeucauduocchon = self._yeucautudo
                lydochon = "ĐI DẠO (TỰ DO)"
                self._thoidiemdichuyentudogannhat = time.time()
            else:
                if is_log: print(f"[DEBUG-MOVE] ĐI DẠO: Đang delay ({round(time.time() - self._thoidiemdichuyentudogannhat, 1)}s < 2.0s)")
                pass

        diachimuctieudanggom = yeucauduocchon.get("diachimuctieu") if yeucauduocchon else False
        if is_log:
            msg_dich = str(yeucauduocchon.get("toadodich")) if yeucauduocchon else "None"
            msg_diachimuctieudanggom = diachimuctieudanggom if yeucauduocchon else "None"
            print(f"[DEBUG-MOVE] Quyết định: {lydochon} | Đích: {msg_dich} | Mục tiêu: {msg_diachimuctieudanggom}")

        if yeucauduocchon and yeucauduocchon.get("yeucau") == YEUCAUDICHUYENTANCONG and is_anhhuongboitruongnhom:
            # Sao chép để việc cắt tọa độ theo trưởng nhóm không ghi đè vào self._yeucautancong
            yeucauduocchon = dict(yeucauduocchon)
            x_truongnhom, y_truongnhom = self.moitruong.get_toadotruongnhom()

            if x_truongnhom and y_truongnhom:
                x_muctieu, y_muctieu = None, None
                toadodich_ = yeucauduocchon.get("toadodich")
                diachimuctieu_ = diachimuctieudanggom

                if toadodich_:
                    x_muctieu, y_muctieu = toadodich_
                elif diachimuctieu_:
                    x_muctieu, y_muctieu = self.moitruong.get_toado(diachimuctieu_, )

                if x_muctieu and y_muctieu:
                    khoangcachmuctieuvatruongnhom = math.dist((x_muctieu, y_muctieu), (x_truongnhom, y_truongnhom))
                    khoangcachtoidatruongnhom = self._tinhtoanbankinhdungtancongtruongnhom()

                    if khoangcachmuctieuvatruongnhom > khoangcachtoidatruongnhom:
                        vec_x = x_muctieu - x_truongnhom
                        vec_y = y_muctieu - y_truongnhom

                        x_clipped = int(x_truongnhom + (vec_x * khoangcachtoidatruongnhom / khoangcachmuctieuvatruongnhom))
                        y_clipped = int(y_truongnhom + (vec_y * khoangcachtoidatruongnhom / khoangcachmuctieuvatruongnhom))

                        yeucauduocchon["toadodich"] = (x_clipped, y_clipped)
                        yeucauduocchon["diachimuctieu"] = None
                        yeucauduocchon["khoangcachtoida"] = 0

        iddoituongmuctieudanggom = 0
        if yeucauduocchon:
            loaiyeucau = yeucauduocchon.get("yeucau")
            if loaiyeucau in (YEUCAUDICHUYENTANCONG, YEUCAUDICHUYENGOMQUAI):
                diachimuctieu = diachimuctieudanggom
                if diachimuctieu:
                    iddoituongmuctieudanggom = self.moitruong.get_iddoituong(diachimuctieu)
                else:
                    iddoituongmuctieudanggom = yeucauduocchon.get("idmuctieu", 0)

        # Chỉ coi là kẹt khi thực sự còn phải di chuyển (chưa vào tầm), đứng yên trong tầm để đánh/buff thì không tính
        is_candichuyendendich = False
        if iddoituongmuctieudanggom > 0:
            toadodichkiemtra = yeucauduocchon.get("toadodich")
            diachidichkiemtra = yeucauduocchon.get("diachimuctieu")
            if toadodichkiemtra:
                khoangcachdendich = self.moitruong.get_khoangcachdiem(toadodichkiemtra[0], toadodichkiemtra[1])
            elif diachidichkiemtra:
                khoangcachdendich = self.moitruong.get_khoangcach(diachidichkiemtra)
            else:
                khoangcachdendich = 0.
            if yeucauduocchon.get("kieudichuyen", KIEUDICHUYEN_GIUKHOANGCACHTOIDA) == KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU:
                is_candichuyendendich = khoangcachdendich < yeucauduocchon.get("khoangcach", 1.0) - 1.0
            else:
                is_candichuyendendich = khoangcachdendich > yeucauduocchon.get("khoangcachtoida", 0.0) + 1.0

        if iddoituongmuctieudanggom > 0:
            if iddoituongmuctieudanggom != self._idmuctieudangtheokiemtraket or not is_candichuyendendich or idtuthenhanvat != TUTHENHANVAT_DUNGIM:
                self._idmuctieudangtheokiemtraket = iddoituongmuctieudanggom
                self._thoidiemdungimkiemtraket = time.time()
                self._toadokiemtraket = self.moitruong.get_toado()
                self._thoidiembatdaukiemtraket = time.time()
            else:
                curr_x, curr_y = self.moitruong.get_toado()

                khoangcachdadichuyen = math.dist((curr_x, curr_y), self._toadokiemtraket)

                if time.time() - self._thoidiembatdaukiemtraket > 5.0:
                    if khoangcachdadichuyen < 1.0:
                        is_quai = False
                        if diachimuctieudanggom:
                            if self.moitruong.get_is_nhanvattontai(diachimuctieudanggom) and self.moitruong.get_idloainhanvat(diachimuctieudanggom) == LOAIMUCTIEU_QUAIVATHOACNPC:
                                is_quai = True

                        if is_quai:
                            if not is_anhhuongboitruongnhom:
                                print(f"[DEBUG-MOVE] KẸT TƯỜNG/GÓC LAG khi đến QUÁI {hex(iddoituongmuctieudanggom)}. Blacklist 120s.")
                                self._idmuctieubiloi_map[iddoituongmuctieudanggom] = time.time()
                        else:
                            print(f"[DEBUG-MOVE] KẸT khi di chuyển. Reset hành động.")

                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                        self._idmuctieudangtheokiemtraket = 0
                        self._thoidiemdungimkiemtraket = 0.
                        return
                    else:
                        self._toadokiemtraket = (curr_x, curr_y)
                        self._thoidiembatdaukiemtraket = time.time()
        else:
            self._idmuctieudangtheokiemtraket = 0
            self._thoidiemdungimkiemtraket = 0.

        if yeucauduocchon:
            if yeucauduocchon.get("yeucau") == YEUCAUDICHUYENDICHUYENTUDO:
                toadodich = yeucauduocchon.get("toadodich")
                if toadodich:
                    self.moitruong.action_tudongtimduong(*toadodich)
                return

            toadodich = yeucauduocchon.get("toadodich")
            diachimuctieu = diachimuctieudanggom

            if idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self.moitruong.get_tenmonphai() == "thucson" and self.moitruong.get_noilucconlai() > 50:
                x_dich, y_dich = None, None
                if toadodich:
                    x_dich, y_dich = toadodich[0], toadodich[1]
                elif diachimuctieu:
                    x_dich, y_dich = self.moitruong.get_toado(diachimuctieu)

                if x_dich and y_dich:
                    x_banthan, y_banthan = self.moitruong.get_toado()

                    if math.dist((x_banthan, y_banthan), (x_dich, y_dich)) > 3.:
                        is_khaithiensansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA)
                        if self._is_khaithientichdiasansang and not is_khaithiensansang:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)

                        self._is_khaithientichdiasansang = is_khaithiensansang

                        if is_khaithiensansang:
                            if self._solanthatbaikhaithien >= self._solanthatbaikhaithientoida and time.time() - self._thoidiembiphatkhaithien > 3.0:
                                self._solanthatbaikhaithien = 0
                                self._thoidiembiphatkhaithien = 0

                            is_bicam = time.time() - self._thoidiemtamngungkhaithientichdia < 0.8
                            if is_bicam and self._solanthatbaikhaithien < self._solanthatbaikhaithientoida:
                                self._solanthatbaikhaithien += 1
                                if self._solanthatbaikhaithien == self._solanthatbaikhaithientoida:
                                    self._thoidiembiphatkhaithien = time.time()

                            if self._solanthatbaikhaithien < self._solanthatbaikhaithientoida:
                                idkynang = self.moitruong.get_idkynang(*VITRIKYNANG_KHAITHIENTICHDIA)
                                if idkynang and self.moitruong.action_sudungkynangtoado(idkynang, int(x_dich), int(y_dich), delay = 0.05):
                                    self._thoidiemtamngungkhaithientichdia = time.time()
                                    self._solansudungkhaithientichdia += 1
                                    return

            kieudichuyen = yeucauduocchon.get("kieudichuyen", KIEUDICHUYEN_GIUKHOANGCACHTOIDA)

            if kieudichuyen == KIEUDICHUYEN_GIUKHOANGCACHTOIDA:
                khoangcachtoida = yeucauduocchon.get("khoangcachtoida", 0.0)
                if toadodich:
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(
                        toadodich[0],
                        toadodich[1],
                        khoangcachtoida,
                        is_bokiemtravungcam = yeucauduocchon.get("yeucau") == YEUCAUDICHUYENTHEOSAUTRUONGNHOM,
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
            elif kieudichuyen == KIEUDICHUYEN_TOADOCHUAN:
                self.moitruong.action_dichuyenphudau(
                    diachimuctieu,
                    khoangcachphudau = 0
                )

    def action_tudongtheosautruongnhom(self):
        self._yeucautheosautruongnhom = None

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

            # if self._is_tudongbattheosaunhom and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THEOSAUNHOM,), True, is_hieuungcoloi = 1):
            #     self.moitruong.action_battheosaunhom(3.)

            xtruongnhom, ytruongnhom = self.moitruong.get_toadotruongnhom()

            if not xtruongnhom and not ytruongnhom:
                break

            khoangcachtruongnhom = self.moitruong.get_khoangcachdiem(xtruongnhom, ytruongnhom)
            khoangcachtoidatruongnhom = self._tinhtoankhoangcachtoidatruongnhomphuhop()

            if khoangcachtruongnhom >= KHOANGCACHTOIDAHOPLE:
                break

            # Mỗi thành viên có một chỗ đứng riêng quanh trưởng nhóm (chia đều góc theo thứ tự trong nhóm) thay vì cùng chạy thẳng về phía trưởng nhóm rồi dính vào nhau
            xvitri, yvitri = self._tinhtoanvitritheosautruongnhom(xtruongnhom, ytruongnhom, khoangcachtoidatruongnhom)
            khoangcachvitri = self.moitruong.get_khoangcachdiem(xvitri, yvitri)

            # Chỉ bắt đầu đi khi đã ra quá xa trưởng nhóm, nhưng đã đi thì đi hẳn tới chỗ đứng riêng (không dừng ngay mép vùng cho phép)
            if khoangcachtruongnhom > khoangcachtoidatruongnhom:
                self._is_dangvevitritheosau = True
            elif khoangcachvitri <= 1.0:
                self._is_dangvevitritheosau = False

            if not self._is_dangvevitritheosau:
                break

            self._yeucautheosautruongnhom = {
                "yeucau": YEUCAUDICHUYENTHEOSAUTRUONGNHOM,
                "toadodich": (xvitri, yvitri),
                "khoangcachtoida": 0.5
            }
            break

        if not self._yeucautheosautruongnhom:
            self._is_dangvevitritheosau = False
        return

    def _tinhtoanvitritheosautruongnhom(self, xtruongnhom, ytruongnhom, khoangcachtoidatruongnhom):
        idnguoichoi = self.moitruong.get_idnguoichoi()
        idtruongnhom = self.moitruong.get_idnguoichoitruongnhom()
        idthanhviens = [i for i in self.moitruong.get_danhsachidnguoichoithanhviennhoms() if i != idtruongnhom]

        if idnguoichoi in idthanhviens:
            # Thứ tự trong nhóm giống nhau ở mọi máy nên các thành viên tự chia góc không trùng nhau
            goc = 2 * math.pi * idthanhviens.index(idnguoichoi) / len(idthanhviens)
        else:
            # Chưa đọc được danh sách nhóm: rải góc theo ID (góc vàng) để vẫn khác nhau
            goc = (idnguoichoi or 0) * 2.39996

        bankinh = max(1.5, khoangcachtoidatruongnhom * 0.6)
        return xtruongnhom + bankinh * math.cos(goc), ytruongnhom + bankinh * math.sin(goc)

    def _tinhtoankhoangcachtoidatruongnhomphuhop(self):
        khoangcachtoidatruongnhom = self._khoangcachtoidatruongnhom
        diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        tendoituongmuctieudangchon = diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)
        is_muctieudangchonlabaothukynangtrieuhoi = tendoituongmuctieudangchon and any(tenbaothu in tendoituongmuctieudangchon for tenbaothu in BAOTHUKYNANGTRIEUHOIs)
        if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon) or is_muctieudangchonlabaothukynangtrieuhoi:
            khoangcachtoidatruongnhom -= 1.5
        return khoangcachtoidatruongnhom

    def _tinhtoanbankinhdungtancongtruongnhom(self):
        # Chỗ đứng đánh xa nhất quanh trưởng nhóm; chừa 0.5 để tọa độ làm tròn không vượt ngưỡng kéo về theo nhóm
        return max(0., self._tinhtoankhoangcachtoidatruongnhomphuhop() - 0.5)

    def _tinhtoankhoangcachchophepmuctieutruongnhom(self):
        # Mục tiêu phải đánh được từ chỗ đứng đó, nếu không sẽ chọn quái không bao giờ với tới
        return self._tinhtoanbankinhdungtancongtruongnhom() + self._khoangcachvoitoimuctieu

    def _kiemtra_vungcam(self, x, y):
        # Vùng cấm trên bản đồ (VUNGCAM_MAP): đi vào sẽ bị dịch chuyển sang bản đồ khác
        danhsachvungcam = VUNGCAM_MAP.get(self.moitruong.get_idbandohientai())
        if not danhsachvungcam:
            return False
        for vung in danhsachvungcam:
            if vung["type"] == "circle":
                if math.dist((x, y), (vung["x"], vung["y"])) <= vung["r"]:
                    return True
            elif vung["type"] == "line":
                if self._tinhkhoangcachdendoanthang(x, y, vung["x1"], vung["y1"], vung["x2"], vung["y2"]) <= vung["r"]:
                    return True
        return False

    def _kiemtra_divaovungcam(self, x, y):
        # Nhân vật chạy thẳng tới điểm đích: chặn cả khi điểm đích nằm ngoài vùng cấm nhưng đường chạy cắt qua vùng cấm
        if not self._is_tranhvungcam or not VUNGCAM_MAP.get(self.moitruong.get_idbandohientai()):
            return False
        if self._kiemtra_vungcam(x, y):
            return True
        x1, y1 = self.moitruong.get_toado()
        sobuoc = int(math.dist((x1, y1), (x, y)))
        for i in range(1, sobuoc):
            t = i / sobuoc
            if self._kiemtra_vungcam(x1 + (x - x1) * t, y1 + (y - y1) * t):
                return True
        return False

    def _kiemtra_tamdiemdanh(self, x, y):
        # Đang chạy theo lộ trình điểm đánh: mục tiêu phải nằm trong bán kính _bankinhdiemdanh quanh ít nhất 1 điểm đánh của bản đồ hiện tại.
        # Không có điểm đánh nào trên bản đồ này (hoặc không bật lộ trình) thì không giới hạn.
        if not self._is_tudongdichuyendiemdanhxungquanh or not self._diemdanhxungquanhs:
            return True
        idbandohientai = self.moitruong.get_idbandohientai()
        diemcungbandos = [d for d in self._diemdanhxungquanhs if len(d) >= 3 and d[2] == idbandohientai]
        if not diemcungbandos:
            return True
        return any(math.dist((x, y), (d[0], d[1])) <= self._bankinhdiemdanh for d in diemcungbandos)

    def _kiemtramuctieuhople(self, diachidoituong, is_dongdoi = False):
        # Trả về False nếu không hợp lệ, ngược lại trả về dict thông tin mục tiêu để tái sử dụng
        if is_dongdoi:
            return True

        if not self.moitruong.get_is_cothetancong(diachidoituong):
            return False

        tendoituong = self.moitruong.get_tendoituong(diachidoituong)
        if tendoituong in TENMUCTIEUKHONGTANCONGs:
            return False
        if self._tenmuctieutancongs and tendoituong not in self._tenmuctieutancongs:
            return False
        if self._tenmuctieukhongtancongs and tendoituong in self._tenmuctieukhongtancongs:
            return False

        is_nguoichoi = self.moitruong.get_is_nguoichoi(diachidoituong)
        is_baothukynangtrieuhoi = self.moitruong.get_is_baothukynangtrieuhoi(diachidoituong)
        is_baothugiangho = self.moitruong.get_is_baothugiangho(diachidoituong)
        is_muctieupk = is_nguoichoi or is_baothukynangtrieuhoi or is_baothugiangho

        if self._is_chidanhnguoichoi and not is_muctieupk:
            return False

        idbandohientai = self.moitruong.get_idbandohientai()
        if (idbandohientai in BANDOKHONGPKs) and is_muctieupk:
            return False

        if self._diemdanhxungquanhs and self._is_tudongdichuyendiemdanhxungquanh:
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if danhsachbandohople and idbandohientai not in danhsachbandohople:
                return False

        if self.moitruong.get_is_nhanvatanthan(diachidoituong):
            return False

        toadodoituong = self.moitruong.get_toado(diachidoituong)

        # Tránh vùng cấm (theo tùy chọn tránh vùng cấm)
        if self._kiemtra_divaovungcam(*toadodoituong):
            return False

        # Quái phải nằm trong tầm của một điểm đánh (người chơi/bảo thú PK thì không giới hạn để còn phản công)
        if not is_muctieupk and not self._kiemtra_tamdiemdanh(*toadodoituong):
            return False

        if is_nguoichoi:
            idnguoichoixemxet = self.moitruong.get_idnguoichoi(diachidoituong)
            if time.time() - self.moitruong.thoidiemmuctieuanthangannhat_map.get(idnguoichoixemxet, 0) < 1.5:
                return False
            if time.time() - self.moitruong.thoidiemmuctieuxuathiengannhat_map.get(idnguoichoixemxet, 0) < 1.5:
                return False

        if is_baothukynangtrieuhoi:
            tenchunhanxemxet = self.moitruong.get_tenchunhan(diachidoituong)
            if tenchunhanxemxet and time.time() - self.moitruong.thoidiembaothuxuathiengannhat_map.get(tenchunhanxemxet, 0) < 1.5:
                return False

        return {
            "diachi": diachidoituong,
            "ten": tendoituong,
            "is_nguoichoi": is_nguoichoi,
            "is_baothukynangtrieuhoi": is_baothukynangtrieuhoi,
            "is_baothugiangho": is_baothugiangho,
            "is_muctieupk": is_muctieupk,
        }

    def action_tudongtimkiemmuctieu(self):
        if not self._is_tudongtimkiemmuctieu:
            return

        idbandohientai = self.moitruong.get_idbandohientai()
        if idbandohientai in BANDOKHONGTANCONGs:
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            return

        def _thaydoimuctieu(diachimuctieu):
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachimuctieu)
            self.moitruong._thoidiemtuthenhanvatdungimcomuctieugannhat = time.time()
            self._is_battudongtancongvatly = False
            self._thoidiemdoimuctieugannhat = time.time()

        if idbandohientai != self._idbandomuctieudangchon:
            self._idbandomuctieudangchon = idbandohientai
            self._diachicosomuctieuduphong = 0
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

        thoidiemhientai = time.time()
        idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if thoidiemhientai - v > 120]
        for k in idcanxoas:
            del self._idmuctieubiloi_map[k]

        diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

        toadotruongnhom = self.moitruong.get_toadotruongnhom()
        is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom() and toadotruongnhom != (65535, 65535)
        khoangcachtoidatruongnhom = self._tinhtoankhoangcachtoidatruongnhomphuhop()

        khoangcachchophepmuctieutruongnhom = self._tinhtoankhoangcachchophepmuctieutruongnhom()

        # Đọc tọa độ bản thân 1 lần, tính khoảng cách bằng math.dist thay vì đọc lại bộ nhớ cho mỗi đối tượng
        toadobanthan = self.moitruong.get_toado()

        def _bosungvitri(thongtin, toado = None):
            toado = toado or self.moitruong.get_toado(thongtin["diachi"])
            thongtin["toado"] = toado
            thongtin["khoangcach"] = math.dist(toado, toadobanthan)
            thongtin["khoangcachtruongnhom"] = math.dist(toado, toadotruongnhom) if is_anhhuongboitruongnhom else 0.
            return thongtin

        # Đang farm & bán rác: nhường quái đang ở gần nhân vật khác của mình (không cùng nhóm) cho nhân vật đó,
        # tránh các nhân vật đánh chung một chỗ, đi sát rạt vào nhau (giống logic nhường quái khi gom)
        toadodongdois = self._laytoadodongdoikhacnhom() if self._is_tudongvebanrac else []

        def _is_nhuongdongdoi(thongtin):
            if thongtin["is_muctieupk"] or not toadodongdois:
                return False
            return any(math.dist(thongtin["toado"], toadodongdoi) <= 9.0 and math.dist(thongtin["toado"], toadodongdoi) < thongtin["khoangcach"]
                       for toadodongdoi in toadodongdois)

        muctieuhientai = None

        if diachicosothongtinnhanvatmuctieudangchon:
            if self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatmuctieudangchon):
                self._thoidiemvohieuhoatatchucnangmoronggannhat = max(self._thoidiemvohieuhoatatchucnangmoronggannhat, time.time() + 10.)

            thongtin = self._kiemtramuctieuhople(diachicosothongtinnhanvatmuctieudangchon, is_dongdoi = False)
            if thongtin:
                _bosungvitri(thongtin)
                if is_anhhuongboitruongnhom and thongtin["khoangcachtruongnhom"] > khoangcachchophepmuctieutruongnhom:
                    thongtin = False
                elif self.moitruong.get_idmaupk() == MAUPK_HOABINH and thongtin["is_muctieupk"]:
                    thongtin = False
                elif _is_nhuongdongdoi(thongtin):
                    thongtin = False

            if self.moitruong.get_tenmonphai() == "daohoanguyen" and self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon) > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                self._is_battudongtancongvatly = False

            if thongtin:
                muctieuhientai = thongtin
            else:
                _thaydoimuctieu(0)
                diachicosothongtinnhanvatmuctieudangchon = 0
                self._diachicosomuctieuduphong = 0

        if not diachicosothongtinnhanvatmuctieudangchon and self._diachicosomuctieuduphong:
            diachiduphong = self._diachicosomuctieuduphong
            self._diachicosomuctieuduphong = 0

            thongtin = self.moitruong.get_is_nhanvattontai(diachiduphong) and self._kiemtramuctieuhople(diachiduphong, is_dongdoi = False)
            if thongtin:
                _bosungvitri(thongtin)
                is_duphonghople = thongtin["khoangcach"] < KHOANGCACHTOANMANHINH and not _is_nhuongdongdoi(thongtin)
                if is_anhhuongboitruongnhom and thongtin["khoangcachtruongnhom"] > khoangcachchophepmuctieutruongnhom:
                    is_duphonghople = False

                if is_duphonghople:
                    _thaydoimuctieu(diachiduphong)
                    diachicosothongtinnhanvatmuctieudangchon = diachiduphong
                    muctieuhientai = thongtin

        if is_anhhuongboitruongnhom:
            khoangcachtoibanthanvatruongnhom = math.dist(toadobanthan, toadotruongnhom)
            # Chừa thêm một khoảng: ngưỡng này trùng chỗ dừng khi theo nhóm nên lệch chút xíu (trưởng nhóm đang đi) là không chọn được mục tiêu
            if khoangcachtoibanthanvatruongnhom > khoangcachtoidatruongnhom + KHOANGCACHSUDUNGKYNANGCANCHIEN:
                return

        is_nhanvatbichoang = self.moitruong.get_is_nhanvatbichoang()
        is_vanmongcoc = self.moitruong.get_tenmonphai() == "vanmongcoc"

        def _is_codieukienbattu(diachi):
            if self.moitruong.get_phantramsinhlucconlai(diachi) > 5:
                return False, False
            return True, self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachi, is_hieuungcoloi = 1)

        def _is_uutienhon(xemxet, hientai):
            is_baothuxemxettrongtam = xemxet["is_baothukynangtrieuhoi"] and xemxet["khoangcach"] < KHOANGCACHSUDUNGKYNANGTAMXA
            is_baothuhientaitrongtam = hientai["is_baothukynangtrieuhoi"] and hientai["khoangcach"] < KHOANGCACHSUDUNGKYNANGTAMXA

            if self._is_uutienbaothukynangtrieuhoi and (is_baothuxemxettrongtam or is_baothuhientaitrongtam):
                if is_baothuxemxettrongtam != is_baothuhientaitrongtam:
                    return is_baothuxemxettrongtam
            elif xemxet["is_nguoichoi"] != hientai["is_nguoichoi"]:
                return xemxet["is_nguoichoi"]

            if self._is_khonguutienbaothugiangho and not is_nhanvatbichoang:
                if (xemxet["is_nguoichoi"] or xemxet["is_baothukynangtrieuhoi"]) and hientai["is_baothugiangho"]:
                    return True
                if (hientai["is_nguoichoi"] or hientai["is_baothukynangtrieuhoi"]) and xemxet["is_baothugiangho"]:
                    return False

            if self._is_uutienmuctieupk and xemxet["is_muctieupk"] != hientai["is_muctieupk"]:
                return xemxet["is_muctieupk"]

            if xemxet["is_muctieupk"] and hientai["is_muctieupk"]:
                is_hientaibikhongthu = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, diachicosothongtinnhanvat = hientai["diachi"], is_hieuungcoloi = 0)
                if is_hientaibikhongthu and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, diachicosothongtinnhanvat = xemxet["diachi"], is_hieuungcoloi = 0):
                    return True

                if not is_vanmongcoc:
                    _, is_hientaibattu = _is_codieukienbattu(hientai["diachi"])
                    if is_hientaibattu:
                        is_xemxetmauthap, is_xemxetbattu = _is_codieukienbattu(xemxet["diachi"])
                        if not is_xemxetmauthap or not is_xemxetbattu:
                            return True

            if is_anhhuongboitruongnhom:
                return xemxet["khoangcachtruongnhom"] + 0.5 < hientai["khoangcachtruongnhom"]
            return xemxet["khoangcach"] + 0.5 < hientai["khoangcach"]

        demmuctieuganbanthan3 = 0
        demmuctieuganbanthan5 = 0
        demmuctieuganbanthan7 = 0
        demmuctieuganbanthan9 = 0

        khoangcachtimkiem = self._khoangcachtimkiemmuctieu
        muctieutotnhat = muctieuhientai
        diachimuctieutruocdo = 0
        toadomuctieuhoples = []

        iii = 0
        while True:
            diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(iii)
            if not diachicosothongtinnhanvatmuctieuxemxet:
                break
            iii += 1

            toadomuctieuxemxet = self.moitruong.get_toado(diachicosothongtinnhanvatmuctieuxemxet)
            khoangcachmuctieuxemxettoibanthan = math.dist(toadomuctieuxemxet, toadobanthan)
            if khoangcachmuctieuxemxettoibanthan >= khoangcachtimkiem:
                continue

            if self.moitruong.get_iddoituong(diachicosothongtinnhanvatmuctieuxemxet) in self._idmuctieubiloi_map:
                continue

            thongtinmuctieuxemxet = self._kiemtramuctieuhople(diachicosothongtinnhanvatmuctieuxemxet, is_dongdoi = False)
            if not thongtinmuctieuxemxet:
                continue

            _bosungvitri(thongtinmuctieuxemxet, toadomuctieuxemxet)
            if is_anhhuongboitruongnhom and thongtinmuctieuxemxet["khoangcachtruongnhom"] > khoangcachchophepmuctieutruongnhom:
                continue
            if _is_nhuongdongdoi(thongtinmuctieuxemxet):
                continue

            toadomuctieuhoples.append(toadomuctieuxemxet)

            if khoangcachmuctieuxemxettoibanthan <= 9.0:
                if khoangcachmuctieuxemxettoibanthan <= 3.0:
                    demmuctieuganbanthan3 += 1
                if khoangcachmuctieuxemxettoibanthan <= 5.0:
                    demmuctieuganbanthan5 += 1
                if khoangcachmuctieuxemxettoibanthan <= 7.0:
                    demmuctieuganbanthan7 += 1
                demmuctieuganbanthan9 += 1

            if muctieutotnhat and diachicosothongtinnhanvatmuctieuxemxet == muctieutotnhat["diachi"]:
                continue

            if not muctieutotnhat or _is_uutienhon(thongtinmuctieuxemxet, muctieutotnhat):
                if muctieutotnhat:
                    diachimuctieutruocdo = muctieutotnhat["diachi"]
                muctieutotnhat = thongtinmuctieuxemxet

        # Chỉ ghi mục tiêu vào game 1 lần sau khi đã chọn xong
        diachimuctieumoi = muctieutotnhat["diachi"] if muctieutotnhat else 0
        if diachimuctieumoi != diachicosothongtinnhanvatmuctieudangchon:
            diachiduphong = diachicosothongtinnhanvatmuctieudangchon or diachimuctieutruocdo
            if diachiduphong:
                self._diachicosomuctieuduphong = diachiduphong
            _thaydoimuctieu(diachimuctieumoi)

        # Đếm quanh mục tiêu cuối cùng (trước đây đếm theo mục tiêu tạm thời trong vòng lặp nên bị sai)
        demmuctieugan3 = 0
        demmuctieugan5 = 0
        demmuctieugan7 = 0
        demmuctieugan9 = 0

        toadotamdem = muctieutotnhat["toado"] if muctieutotnhat else toadobanthan
        for toadomuctieuhople in toadomuctieuhoples:
            khoangcachtoitamdem = math.dist(toadomuctieuhople, toadotamdem)
            if khoangcachtoitamdem <= 9.0:
                if khoangcachtoitamdem <= 3.0:
                    demmuctieugan3 += 1
                if khoangcachtoitamdem <= 5.0:
                    demmuctieugan5 += 1
                if khoangcachtoitamdem <= 7.0:
                    demmuctieugan7 += 1
                demmuctieugan9 += 1

        self._is_nhieumuctieugan3 = demmuctieugan3 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan5 = demmuctieugan5 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan7 = demmuctieugan7 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan9 = demmuctieugan9 >= self._soluongnhieumuctieu

        self._is_nhieumuctieuganbanthan3 = demmuctieuganbanthan3 >= self._soluongnhieumuctieu
        self._is_nhieumuctieuganbanthan5 = demmuctieuganbanthan5 >= self._soluongnhieumuctieu
        self._is_nhieumuctieuganbanthan7 = demmuctieuganbanthan7 >= self._soluongnhieumuctieu
        self._is_nhieumuctieuganbanthan9 = demmuctieuganbanthan9 >= self._soluongnhieumuctieu

    def _kiemtramuctieuhoplemonphai(self, diachidoituong, is_dongdoi = False):
        if is_dongdoi:
            return True
        iddoituong = self.moitruong.get_iddoituong(diachidoituong)
        if iddoituong in self._idmuctieubiloi_map:
            return False
        tendoituong = self.moitruong.get_tendoituong(diachidoituong)
        if tendoituong in TENMUCTIEUKHONGTANCONGs:
            return False
        if self._tenmuctieutancongs and tendoituong not in self._tenmuctieutancongs:
            return False
        if self._tenmuctieukhongtancongs and tendoituong in self._tenmuctieukhongtancongs:
            return False
        is_nguoichoi = self.moitruong.get_is_nguoichoi(diachidoituong)
        is_baothu = self.moitruong.get_is_baothukynangtrieuhoi(diachidoituong) or self.moitruong.get_is_baothugiangho(diachidoituong)
        is_muctieupk = is_nguoichoi or is_baothu

        if self._is_chidanhnguoichoi and not is_muctieupk:
            return False
        if self.moitruong.get_is_nhanvatanthan(diachidoituong):
            return False
        idbandohientai = self.moitruong.get_idbandohientai()
        is_bandokhongpk = idbandohientai in BANDOKHONGPKs
        if is_bandokhongpk and is_muctieupk:
            return False
        if self._diemdanhxungquanhs and self._is_tudongdichuyendiemdanhxungquanh:
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if danhsachbandohople and idbandohientai not in danhsachbandohople:
                return False

        return True

    def action_test(self):
        vitrivatpham = 0
        iddoituong = self.moitruong.get_iddoituongvatphamhanhtrang(vitrivatpham)
        if iddoituong:
            while True:
                self.moitruong.truyvan_motavatphamhanhtrang(vitrivatpham)
                motavatpham = self.moitruong.get_motavatphamhanhtrang(vitrivatpham)
                if not motavatpham:
                    break
                if "★★★★★★" in motavatpham:
                    break
                if "★★★★★" in motavatpham or "★★★★" in motavatpham:
                    iddoituongdoanthach = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPDOANTHACH)
                elif "★★★" in motavatpham or "★★" in motavatpham:
                    iddoituongdoanthach = self.moitruong.action_timkiemvatphamhanhtrang(TRUNGCAPDOANTHACH)
                else:
                    iddoituongdoanthach = self.moitruong.action_timkiemvatphamhanhtrang(SOCAPDOANTHACH)
                if iddoituongdoanthach:
                    self.moitruong.action_thucthicaulenh("mix3 0# {}# {}#".format(hex(iddoituong), hex(iddoituongdoanthach)).replace("0x", ""))
                    time.sleep(0.25)
                else:
                    break
    def action_tudongtimkiemmuctieumonphai(self):
        tenmonphai = self.moitruong.get_tenmonphai()

        toadotruongnhom = self.moitruong.get_toadotruongnhom()
        is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom() and toadotruongnhom != (65535, 65535)
        khoangcachtoidatruongnhom = self._tinhtoankhoangcachtoidatruongnhomphuhop()
        khoangcachchophepmuctieutruongnhom = KHOANGCACHSUDUNGKYNANGTAMXA + khoangcachtoidatruongnhom

        idbandohientai = self.moitruong.get_idbandohientai()
        if tenmonphai == "daohoanguyen":
            idnguoichoi = self.moitruong.get_idnguoichoi()
            idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

            diachidoituongcanbuff = None

            if self.moitruong.get_is_dangnamtrongnhom():
                i = -1
                while True:
                    i += 1
                    diachicosothongtindoituongmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)

                    if not diachicosothongtindoituongmuctieuxemxet:
                        break

                    if not self.moitruong.get_is_nhanvattontai(diachicosothongtindoituongmuctieuxemxet):
                        continue
                    if self.moitruong.get_is_nhanvatdachet(diachicosothongtindoituongmuctieuxemxet):
                        continue

                    if is_anhhuongboitruongnhom:
                        if self.moitruong.get_khoangcachdiem(*toadotruongnhom, diachicosothongtindoituongmuctieuxemxet) > khoangcachchophepmuctieutruongnhom:
                            continue

                    if self.moitruong.get_khoangcach(diachicosothongtindoituongmuctieuxemxet) > KHOANGCACHSUDUNGKYNANGTAMXA:
                        continue

                    if self.moitruong.get_is_nguoichoi(diachicosothongtindoituongmuctieuxemxet):
                        idnguoichoixemxet = self.moitruong.get_idnguoichoi(diachicosothongtindoituongmuctieuxemxet)

                        if idnguoichoixemxet != idnguoichoi and idnguoichoithanhviennhoms and idnguoichoixemxet in idnguoichoithanhviennhoms:
                            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, macdinh = True, is_hieuungcoloi = 1):
                                diachidoituongcanbuff = diachicosothongtindoituongmuctieuxemxet
                                break

            self._diachidoituongcanbuffhothekimcangdaohoanguyen = diachidoituongcanbuff

        elif tenmonphai == "maoson":
            diachidoituongcanbuffthuccot = None
            khoangcachthuccotgannhat = 9999.

            diachidoituongcanbuffthucgiap = None
            khoangcachthucgiapgannhat = 9999.

            diachidoituongcanbuffthuctam = None
            khoangcachthuctamgannhat = 9999.

            diachidoituongcanbuffammanhapthe = None
            khoangcachammanhapthegannhat = 9999.

            if idbandohientai not in BANDOKHONGPKs:
                i = -1
                while True:
                    i += 1
                    diachicosothongtindoituongmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                    if not diachicosothongtindoituongmuctieuxemxet:
                        break

                    if not self.moitruong.get_is_nhanvattontai(diachicosothongtindoituongmuctieuxemxet): continue
                    if self.moitruong.get_is_nhanvatdachet(diachicosothongtindoituongmuctieuxemxet): continue
                    if not self.moitruong.get_is_cothetancong(diachicosothongtindoituongmuctieuxemxet): continue

                    if not self._kiemtramuctieuhoplemonphai(diachicosothongtindoituongmuctieuxemxet, is_dongdoi = False):
                        continue

                    if is_anhhuongboitruongnhom:
                        if self.moitruong.get_khoangcachdiem(*toadotruongnhom, diachicosothongtindoituongmuctieuxemxet) > khoangcachchophepmuctieutruongnhom:
                            continue

                    khoangcach = self.moitruong.get_khoangcach(diachicosothongtindoituongmuctieuxemxet)
                    if khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA:
                        continue

                    is_nguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtindoituongmuctieuxemxet)
                    is_baothu = self.moitruong.get_is_baothukynangtrieuhoi(diachicosothongtindoituongmuctieuxemxet) or self.moitruong.get_is_baothugiangho(diachicosothongtindoituongmuctieuxemxet)
                    if not is_nguoichoi and not is_baothu and idbandohientai not in (BANDO_COMO, BANDO_BATQUAITRAN):
                        continue

                    if khoangcach < khoangcachthuccotgannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCCOT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, is_hieuungcoloi = 0):
                        diachidoituongcanbuffthuccot = diachicosothongtindoituongmuctieuxemxet
                        khoangcachthuccotgannhat = khoangcach

                    if khoangcach < khoangcachthucgiapgannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCGIAP,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, is_hieuungcoloi = 0):
                        diachidoituongcanbuffthucgiap = diachicosothongtindoituongmuctieuxemxet
                        khoangcachthucgiapgannhat = khoangcach

                    if khoangcach < khoangcachthuctamgannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCTAM,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, is_hieuungcoloi = 0):
                        diachidoituongcanbuffthuctam = diachicosothongtindoituongmuctieuxemxet
                        khoangcachthuctamgannhat = khoangcach

                    idloaivukhi = self.moitruong.get_idloaivukhi(diachicosothongtindoituongmuctieuxemxet)
                    if is_nguoichoi and idloaivukhi in (IDLOAIVUKHI_THUONG, IDLOAIVUKHI_CON):
                        if khoangcach < khoangcachammanhapthegannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_AMMANHAPTHE,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtindoituongmuctieuxemxet, is_hieuungcoloi = 0):
                            diachidoituongcanbuffammanhapthe = diachicosothongtindoituongmuctieuxemxet
                            khoangcachammanhapthegannhat = khoangcach

            self._diachidoituongcanbuffthuccotmaoson = diachidoituongcanbuffthuccot
            self._diachidoituongcanbuffthucgiapmaoson = diachidoituongcanbuffthucgiap
            self._diachidoituongcanbuffthuctammaoson = diachidoituongcanbuffthuctam
            self._diachidoituongcanbuffammanhapthemaoson = diachidoituongcanbuffammanhapthe

        elif tenmonphai == "vanmongcoc":
            idnguoichoi = self.moitruong.get_idnguoichoi()
            idbandohientai = idbandohientai
            idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

            diachidoituongcanhoisinh = None
            diachidoituongcanbufftaytranquyet = None
            diachidoituongcanbufftaytranquyet2 = None
            diachidoituongcanbufflinhkhihothe = None
            diachidoituongcanbommau = None
            phantramsinhlucthapnhat = 100.

            diachidoituongcanhoisinhduphong = None
            diachidoituongcanbufftaytranquyetduphong = None
            diachidoituongcanbufftaytranquyet2duphong = None
            diachidoituongcanbommauduphong = None
            phantramsinhlucthapnhatduphong = 100.

            diachidoituongcanbuffkimcham = None
            diachidoituongcanbuffngancham = None
            diachidoituongcanbuffcuongthethuat = None

            diachidoituongcanbuffphonganthuat = None
            khoangcachphonganthuatgannhat = 9999.

            diachidoituongcanbuffhuyenquangthiemanh = None
            khoangcachhuyenquanggannhat = 9999.

            danhsachungviens = [(0, self.moitruong.get_diachicosothongtinnhanvat1())]

            diachicosodoituongnguoichoi_map = {}
            danhsachdoituonghoples = []

            diachicosobanthan = self.moitruong.get_diachicosothongtinnhanvat1()
            if diachicosobanthan:
                tenbanthan = self.moitruong.get_tendoituong(diachicosobanthan)
                if tenbanthan:
                    diachicosodoituongnguoichoi_map[tenbanthan] = diachicosobanthan

            i = -1
            while True:
                i += 1
                diachidoituongdangxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachidoituongdangxemxet:
                    break
                if not self.moitruong.get_is_nhanvattontai(diachidoituongdangxemxet):
                    continue
                if self.moitruong.get_is_nhanvatchuasansang(diachidoituongdangxemxet):
                    continue

                is_muctieudangxemxetlanguoichoi = self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet)
                is_dongdoi = False
                if is_muctieudangxemxetlanguoichoi:
                    idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
                    is_dongdoi = (idnguoichoi == idnguoichoidangxemxet) or (idnguoichoithanhviennhoms and idnguoichoidangxemxet in idnguoichoithanhviennhoms) or (idnguoichoidangxemxet in NHANVATCUNGBANGs)

                if not self._kiemtramuctieuhoplemonphai(diachidoituongdangxemxet, is_dongdoi = is_dongdoi):
                    continue

                if is_anhhuongboitruongnhom:
                    if self.moitruong.get_khoangcachdiem(*toadotruongnhom, diachidoituongdangxemxet) > khoangcachchophepmuctieutruongnhom:
                        continue

                khoangcachhientai = self.moitruong.get_khoangcach(diachidoituongdangxemxet)
                if khoangcachhientai >= KHOANGCACHTOANMANHINH:
                    continue
                if idbandohientai == BANDO_CHIENTRUONG and self.moitruong.get_idphechientruong() != self.moitruong.get_idphechientruong(diachidoituongdangxemxet):
                    continue

                is_nguoichoi = self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet)
                is_baothu = self.moitruong.get_is_baothukynangtrieuhoi(diachidoituongdangxemxet) or self.moitruong.get_is_baothugiangho(diachidoituongdangxemxet)
                tendoituong = self.moitruong.get_tendoituong(diachidoituongdangxemxet)

                if is_nguoichoi:
                    diachicosodoituongnguoichoi_map[tendoituong] = diachidoituongdangxemxet

                    idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
                    is_dongdoi = (idnguoichoi == idnguoichoidangxemxet) or (idnguoichoithanhviennhoms and idnguoichoidangxemxet in idnguoichoithanhviennhoms) or (idnguoichoidangxemxet in NHANVATCUNGBANGs)

                    if not is_dongdoi and self.moitruong.get_is_cothetancong(diachidoituongdangxemxet):
                        idloaivukhi = self.moitruong.get_idloaivukhi(diachidoituongdangxemxet)

                        if idloaivukhi in (IDLOAIVUKHI_DAO, IDLOAIVUKHI_KIEM):
                            if khoangcachhientai < khoangcachphonganthuatgannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0):
                                diachidoituongcanbuffphonganthuat = diachidoituongdangxemxet
                                khoangcachphonganthuatgannhat = khoangcachhientai

                        if idloaivukhi != IDLOAIVUKHI_KIEM:
                            if khoangcachhientai < khoangcachhuyenquanggannhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0):
                                diachidoituongcanbuffhuyenquangthiemanh = diachidoituongdangxemxet
                                khoangcachhuyenquanggannhat = khoangcachhientai

                if is_nguoichoi or is_baothu:
                    danhsachdoituonghoples.append({
                        "diachi": diachidoituongdangxemxet,
                        "is_nguoichoi": is_nguoichoi,
                        "is_baothu": is_baothu
                    })

            for doituong in danhsachdoituonghoples:
                diachicosodoituongxemxet = doituong["diachi"]
                priority = -1

                if doituong["is_nguoichoi"]:
                    idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachicosodoituongxemxet)
                    if idnguoichoidangxemxet == idnguoichoi:
                        continue
                    if idnguoichoithanhviennhoms and idnguoichoidangxemxet in idnguoichoithanhviennhoms:
                        priority = 1
                    elif idnguoichoidangxemxet in NHANVATCUNGBANGs:
                        priority = 2

                elif doituong["is_baothu"]:
                    tendoituongchunhan = self.moitruong.get_tenchunhan(diachicosodoituongxemxet)
                    if tendoituongchunhan and tendoituongchunhan in diachicosodoituongnguoichoi_map:
                        diachicosodoituongchunhan = diachicosodoituongnguoichoi_map[tendoituongchunhan]
                        idnguoichoichunhan = self.moitruong.get_idnguoichoi(diachicosodoituongchunhan)

                        if idnguoichoichunhan == idnguoichoi:
                            priority = 1
                        elif idnguoichoithanhviennhoms and idnguoichoichunhan in idnguoichoithanhviennhoms:
                            priority = 1
                        elif idnguoichoichunhan in NHANVATCUNGBANGs:
                            priority = 2

                if priority != -1:
                    danhsachungviens.append((priority, diachicosodoituongxemxet))

            danhsachungviens.sort(key = lambda x: x[0])

            for item in danhsachungviens:
                priority, diachidoituongdangxemxet = item
                is_uutiennhom = priority <= 1
                is_uutienbang = priority == 2

                is_nguoichoi_hientai = self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet)

                if self.moitruong.get_is_nhanvatdachet(diachidoituongdangxemxet):
                    if idbandohientai == BANDO_CHIENTRUONG:
                        continue
                    if is_nguoichoi_hientai:
                        idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
                        if time.time() - self._thoidiemcaituhoansinh_map.get(idnguoichoidangxemxet, 0) > 5.0:
                            if is_uutiennhom and not diachidoituongcanhoisinh:
                                diachidoituongcanhoisinh = diachidoituongdangxemxet
                            elif is_uutienbang and not diachidoituongcanhoisinhduphong:
                                diachidoituongcanhoisinhduphong = diachidoituongdangxemxet
                    continue

                is_cantaytran = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCCOT, HIEUUNGKYNANG_THUCGIAP, HIEUUNGKYNANG_THIEUDOT, HIEUUNGKYNANG_THAUCOTDINH, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0)

                if is_cantaytran:
                    if is_uutiennhom and not diachidoituongcanbufftaytranquyet:
                        diachidoituongcanbufftaytranquyet = diachidoituongdangxemxet
                    elif is_uutienbang and not diachidoituongcanbufftaytranquyetduphong:
                        diachidoituongcanbufftaytranquyetduphong = diachidoituongdangxemxet

                is_cantaytran2 = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCTAM, HIEUUNGKYNANG_LACKICH, HIEUUNGKYNANG_DONGBANG), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0)

                if is_cantaytran2:
                    if is_uutiennhom and not diachidoituongcanbufftaytranquyet2:
                        diachidoituongcanbufftaytranquyet2 = diachidoituongdangxemxet
                    elif is_uutienbang and not diachidoituongcanbufftaytranquyet2duphong:
                        diachidoituongcanbufftaytranquyet2duphong = diachidoituongdangxemxet

                is_dangbithieudot = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0)

                if is_uutiennhom and is_dangbithieudot:
                    if not diachidoituongcanbufflinhkhihothe and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LINHKHIHOTHE,), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1):
                        diachidoituongcanbufflinhkhihothe = diachidoituongdangxemxet

                phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai(diachidoituongdangxemxet)
                is_khongbithieudot = not is_dangbithieudot
                is_datinhcuongluc = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                is_dangbatpk = self.moitruong.get_idmaupk() != MAUPK_HOABINH

                if is_khongbithieudot and (phantramsinhlucconlai <= 35 or ((not is_datinhcuongluc or is_dangbatpk) and phantramsinhlucconlai <= 75)):
                    if is_uutiennhom:
                        if phantramsinhlucconlai < phantramsinhlucthapnhat:
                            phantramsinhlucthapnhat = phantramsinhlucconlai
                            diachidoituongcanbommau = diachidoituongdangxemxet
                    elif is_uutienbang:
                        if phantramsinhlucconlai < phantramsinhlucthapnhatduphong:
                            phantramsinhlucthapnhatduphong = phantramsinhlucconlai
                            diachidoituongcanbommauduphong = diachidoituongdangxemxet

                if is_uutienbang:
                    continue

                if phantramsinhlucconlai >= 25. or idbandohientai in BANDOKHONGPKs:
                    if not diachidoituongcanbuffngancham:
                        is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                        if is_thieuhieuung:
                            diachidoituongcanbuffngancham = diachidoituongdangxemxet

                    if not diachidoituongcanbuffkimcham:
                        is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                        if is_thieuhieuung:
                            diachidoituongcanbuffkimcham = diachidoituongdangxemxet

                    if not diachidoituongcanbuffcuongthethuat:
                        is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CUONGTHETHUAT,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                        if is_thieuhieuung:
                            diachidoituongcanbuffcuongthethuat = diachidoituongdangxemxet

            if not diachidoituongcanhoisinh:
                diachidoituongcanhoisinh = diachidoituongcanhoisinhduphong
            if not diachidoituongcanbufftaytranquyet:
                diachidoituongcanbufftaytranquyet = diachidoituongcanbufftaytranquyetduphong
            if not diachidoituongcanbommau:
                diachidoituongcanbommau = diachidoituongcanbommauduphong
            if not diachidoituongcanbufftaytranquyet2:
                diachidoituongcanbufftaytranquyet2 = diachidoituongcanbufftaytranquyet2duphong

            self._diachidoituongcanhoisinhvanmongcoc = diachidoituongcanhoisinh
            self._diachidoituongcanbufftaytranquyetvanmongcoc = diachidoituongcanbufftaytranquyet
            self._diachidoituongcanbufftaytranquyet2vanmongcoc = diachidoituongcanbufftaytranquyet2
            self._diachidoituongcanbufflinhkhihothevanmongcoc = diachidoituongcanbufflinhkhihothe
            self._diachidoituongcanbommauvanmongcoc = diachidoituongcanbommau
            self._diachidoituongcanbuffkimchamvanmongcoc = diachidoituongcanbuffkimcham
            self._diachidoituongcanbuffnganchamvanmongcoc = diachidoituongcanbuffngancham
            self._diachidoituongcanbuffcuongthethuatvanmongcoc = diachidoituongcanbuffcuongthethuat

            self._diachidoituongcanbuffphonganthuatvanmongcoc = diachidoituongcanbuffphonganthuat
            self._diachidoituongcanbuffhuyenquangthiemanhvanmongcoc = diachidoituongcanbuffhuyenquangthiemanh

            self._is_khongcongidebuff = not any([
                self._diachidoituongcanhoisinhvanmongcoc,
                self._diachidoituongcanbufftaytranquyetvanmongcoc,
                self._diachidoituongcanbommauvanmongcoc,
                self._diachidoituongcanbufftaytranquyet2vanmongcoc,
                self._diachidoituongcanbuffkimchamvanmongcoc,
                self._diachidoituongcanbuffnganchamvanmongcoc,
                self._diachidoituongcanbuffcuongthethuatvanmongcoc,
                self._diachidoituongcanbuffphonganthuatvanmongcoc,
                self._diachidoituongcanbuffhuyenquangthiemanhvanmongcoc
            ])

    def action_tudongsudungvatpham(self):
        if self._is_tudongsudungvatpham:
            if self.moitruong.get_is_nhanvatdachet():
                return

            lichsutrochuyen5s = self.moitruong.get_lichsutrochuyen5s()

            if self._trangthaitrieuhoibaothuvatpham != 3:
                is_doilenh = False
                is_hanhdong = False
                for _, noidungtrochuyen in lichsutrochuyen5s:
                    if "Đợi lệnh" in noidungtrochuyen:
                        is_doilenh = True
                    if "Hành động" in noidungtrochuyen:
                        is_hanhdong = True

                    if is_doilenh and is_hanhdong:
                        self._trangthaitrieuhoibaothuvatpham = 3

                        if self.moitruong.get_idnguoichoi() in DANHHIEU_MAP:
                            self.moitruong.action_thucthicaulenh("title show {}".format(DANHHIEU_MAP[self.moitruong.get_idnguoichoi()]), douutien = DOUUTIEN_KHANCAP)

                        break

            if self._trangthaitrieuhoibaothuvatpham == 0:
                if time.time() - self._thoidiemsudungbaothuvatphamgannhat > 3.0:
                    for baothuvatpham in BAOTHUVATPHAMs:
                        if not self.moitruong.action_timkiemvatphamhanhtrang(baothuvatpham, is_kiemtrahansudung = True):
                            continue
                        if self.action_sudungvatphamhanhtrang(baothuvatpham, delay = 0.):
                            self._thoidiemtamngungsudungkynang = max(self._thoidiemtamngungsudungkynang, time.time() + 0.5)
                            self._thoidiemsudungbaothuvatphamgannhat = time.time()

                            self._trangthaitrieuhoibaothuvatpham = 1
                            self._thoidiemchuyentrangthaitrieuhoibaothuvatpham = time.time()
                            self.moitruong.xoalichsutrochuyen()
                            break

            elif self._trangthaitrieuhoibaothuvatpham == 1:
                if time.time() - self._thoidiemchuyentrangthaitrieuhoibaothuvatpham > 1.0:
                    self.moitruong.action_thucthicaulenh("pf 4131.@", douutien = DOUUTIEN_KHANCAP)

                    self._trangthaitrieuhoibaothuvatpham = 2
                    self._thoidiemchuyentrangthaitrieuhoibaothuvatpham = time.time()
                    self._thoidiemyeucaubaothuvatphamdoilenh = time.time()

            elif self._trangthaitrieuhoibaothuvatpham == 2:
                thoigianchochuyentrangthaitrieuhoibaothuvatpham = time.time() - self._thoidiemchuyentrangthaitrieuhoibaothuvatpham

                if time.time() - self._thoidiemyeucaubaothuvatphamdoilenh > 0.25:
                    self.moitruong.action_thucthicaulenh("pf 4131.@", douutien = DOUUTIEN_KHANCAP)
                    self._thoidiemyeucaubaothuvatphamdoilenh = time.time()

                if thoigianchochuyentrangthaitrieuhoibaothuvatpham > 3.:
                    self._trangthaitrieuhoibaothuvatpham = 0
                    self._thoidiemsudungbaothuvatphamgannhat = time.time()

            idbandohientai = self.moitruong.get_idbandohientai()
            is_bandokhongpk = idbandohientai in BANDOKHONGPKs
            is_bandopk = not is_bandokhongpk
            is_dangbatpk = self.moitruong.get_idmaupk() != MAUPK_HOABINH
            tenmonphai = self.moitruong.get_tenmonphai()

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
            phantramnoilucconlai = self.moitruong.get_phantramnoilucconlai()
            noilucmatdi = self.moitruong.get_noiluctoida() - self.moitruong.get_noilucconlai()
            if time.time() - self._thoidiemkiemtrahieuunggannhat > 2.5:
                self._thoidiemkiemtrahieuunggannhat = time.time()

                if is_bandopk and phantramnoilucconlai < 50. and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHAPLUCTHACH,), True, is_hieuungcoloi = 1):
                    if self.moitruong.action_timkiemvatphamhanhtrang(TIEUPHAPLUCTHACH):
                        self.action_sudungvatphamhanhtrang(TIEUPHAPLUCTHACH)

                if is_bandopk and (is_dangbatpk or self._is_tudongkhaikhoang) and phantramsinhlucconlai < 75. and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HUYETTHACH,), True, is_hieuungcoloi = 1):
                    if self.moitruong.action_timkiemvatphamhanhtrang(TIEUHUYETTHACH):
                        self.action_sudungvatphamhanhtrang(TIEUHUYETTHACH)

                if is_dangbatpk and is_bandopk:
                    if tenmonphai == "daohoanguyen" and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIENNGUYENDON,), macdinh = True, is_hieuungcoloi = 1):
                        if self.moitruong.action_timkiemvatphamhanhtrang(THIENNGUYENDON):
                            self.action_sudungvatphamhanhtrang(THIENNGUYENDON, delay = 0.)
                    if self.moitruong.action_timkiemvatphamhanhtrang(NGANHANHTU) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANHANHTU,), macdinh = True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(NGANHANHTU, delay = 0.)
                    if self.moitruong.action_timkiemvatphamhanhtrang(XALOITU) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_XALOITU,), macdinh = True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(XALOITU, delay = 0.)
                    if phantramsinhlucconlai < 75 and self.moitruong.action_timkiemvatphamhanhtrang(DUAHAU) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHUCHOISINHLUC,), macdinh = True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(DUAHAU, delay = 0.)

            if self.moitruong.get_diempk() > 0:
                if self.moitruong.action_timkiemvatphamhanhtrang(ANXAPHU):
                    self.action_sudungvatphamhanhtrang(ANXAPHU, is_boquaxacnhan = True, delay = 0.)

            if not self._is_tudongdichientruong:
                if self._thoidiemhoandoiphapbao > 0. and self._tenphapbaocu is None:
                    if time.time() - self._thoidiemhoandoiphapbao <= 1.5:
                        tenvatphamtaivitrihoandoi = self.moitruong.get_tenvatphamhanhtrang(self._vitriphapbaovuahoandoi)
                        if tenvatphamtaivitrihoandoi and tenvatphamtaivitrihoandoi not in ["Thượng Phương Bảo Kiếm", ]:
                            self._tenphapbaocu = tenvatphamtaivitrihoandoi
                    else:
                        self._thoidiemhoandoiphapbao = 0.
                        self._vitriphapbaovuahoandoi = -1

                if self._tenphapbaocu is not None:
                    if phantramsinhlucconlai >= self._mucsinhluckhihoandoi + 15:

                        is_phapbaokhonghuhongdavehanhtrang = False
                        if self._tenphapbaokhonghuhongdangmac is not None:
                            if self.moitruong.action_timkiemvatphamhanhtrang(self._tenphapbaokhonghuhongdangmac):
                                is_phapbaokhonghuhongdavehanhtrang = True

                        if is_phapbaokhonghuhongdavehanhtrang:
                            self._thoidiemhoandoiphapbao = 0.
                            self._vitriphapbaovuahoandoi = -1
                            self._tenphapbaocu = None
                            self._mucsinhluckhihoandoi = 0
                            self._tenphapbaokhonghuhongdangmac = None

                        else:
                            if time.time() - self._thoidiemthumaclaiphapbao > 2.0:
                                if self.moitruong.action_timkiemvatphamhanhtrang(self._tenphapbaocu):
                                    self.action_sudungvatphamhanhtrang(self._tenphapbaocu, delay = 0.)
                                    self._thoidiemthumaclaiphapbao = time.time()

                if (phantramsinhlucconlai <= 25 and idbandohientai not in (BANDO_CHIENTRUONG, BANDO_COMO, BANDO_TIVO, *BANDOKHONGPKs)) or (phantramsinhlucconlai < 15 and idbandohientai == BANDO_COMO):
                    for phapbaokhonghuhong in ["Thượng Phương Bảo Kiếm", ]:
                        vitriphapbao = self.moitruong.action_timkiemvitrivatphamhanhtrang(phapbaokhonghuhong)

                        if vitriphapbao is False:
                            continue

                        if self.action_sudungvatphamhanhtrang(phapbaokhonghuhong, delay = 0.):
                            self._vitriphapbaovuahoandoi = vitriphapbao
                            self._thoidiemhoandoiphapbao = time.time()
                            self._mucsinhluckhihoandoi = phantramsinhlucconlai
                            self._tenphapbaocu = None
                            self._tenphapbaokhonghuhongdangmac = phapbaokhonghuhong
                        break

                if is_dangbatpk and is_bandopk and self._is_tudongsudungkynang and phantramsinhlucconlai <= 75 and time.time() - self._thoidiemsudungvatphamhoisinhlucgannhat > 5.:
                    for tenvatphamhoisinhluc in [THILUYENDON, THILUYENQUA, CAPCUUDON, ]:
                        if self.moitruong.action_timkiemvatphamhanhtrang(tenvatphamhoisinhluc):
                            self._thoidiemsudungvatphamhoisinhlucgannhat = time.time()
                            self.action_sudungvatphamhanhtrang(tenvatphamhoisinhluc, delay = 0.)
                            break
                elif self._is_tudongsudungkynang and phantramsinhlucconlai <= 75 and time.time() - self._thoidiemsudungvatphamhoisinhlucgannhat > 5.:
                    if self.moitruong.action_timkiemvatphamhanhtrang(HOATLACHOAN):
                        self._thoidiemsudungvatphamhoisinhlucgannhat = time.time()
                        self.action_sudungvatphamhanhtrang(HOATLACHOAN, delay = 0.)

                if (is_dangbatpk or (idbandohientai == BANDO_BATQUAITRAN and phantramnoilucconlai < 25)) and is_bandopk and self._is_tudongsudungkynang and noilucmatdi > 2000 and time.time() - self._thoidiemsudungvatphamhoinoilucgannhat > 5.:
                    if self.moitruong.action_timkiemvatphamhanhtrang(HOATTAMDON):
                        self._thoidiemsudungvatphamhoinoilucgannhat = time.time()
                        self.action_sudungvatphamhanhtrang(HOATTAMDON, delay = 0.)

                if is_dangbatpk and is_bandopk and self._is_tudongsudungkynang and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCCOT, HIEUUNGKYNANG_THUCGIAP, HIEUUNGKYNANG_THIEUDOT, HIEUUNGKYNANG_THAUCOTDINH, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN), macdinh = False, is_hieuungcoloi = 0) and time.time() - self._thoidiemsudungthanhtamdangannhat > 5.:
                    if self.moitruong.action_timkiemvatphamhanhtrang(KHUMATAN):
                        self._thoidiemsudungthanhtamdangannhat = time.time()
                        self.action_sudungvatphamhanhtrang(KHUMATAN, delay = 0.)

                elif self._is_tudongsudungkynang and phantramnoilucconlai <= 75 and time.time() - self._thoidiemsudungvatphamhoinoilucgannhat > 5.:
                    if self.moitruong.action_timkiemvatphamhanhtrang(ANTHANHOAN):
                        self._thoidiemsudungvatphamhoinoilucgannhat = time.time()
                        self.action_sudungvatphamhanhtrang(ANTHANHOAN, delay = 0.)

            if self.moitruong.get_idnguoichoi() == 59844:
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Luyện Đơn",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

            if self.moitruong.get_idnguoichoi() in (59844, 59845):
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Thái Cổ Thần Quy",
                        "Nhập môn Quyền Cước Chi",
                        "Nhập môn Kim Cương Bất H",
                        "Nhập môn Chu Thiên Vận Ch",
                        "Nhập môn Thái Cổ Thần Q",
                        "Nhập môn Hộ Thể Kim Cang",
                        "Nhập môn Kinh Lạc Học Th",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

                # if time.time() - self._thoidiemsudungtusamdongannhat > 30.:
                #     if self.action_sudungvatphamhanhtrang(TUSAMDON, delay = 0.0):
                #         self._thoidiemsudungtusamdongannhat = time.time()

            if self.moitruong.get_idnguoichoi() == 59996:
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Y Thuật",
                        "Nhập môn Trung Y Dược Lý",
                        "Nhập môn Tu Tâm",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

            if self.moitruong.get_idnguoichoi() == 60055:
                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập môn Tụng Kinh",
                        "Nhập môn Nghịch Thiên Ph",
                        "Nhập môn Cơ Quan",
                    ]
                    for sachcanhoc in sachcanhocs:
                        if self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

            if self.moitruong.get_thelucconlai() <= 5:
                if time.time() - self._thoidiemsudungbattiendongannhat > 30.:
                    if self.action_sudungvatphamhanhtrang(BATTIENDON):
                        self._thoidiemsudungbattiendongannhat = time.time()

    def action_lammoitrangthai(self):
        caulenhthietlapdanhhieu = "title show {}".format(DANHHIEU_MAP[self.moitruong.get_idnguoichoi()])
        self.moitruong.action_thucthicaulenh(caulenhthietlapdanhhieu, douutien = DOUUTIEN_KHANCAP)

    def action_xulyuutiensudungkynang(self, loaikynang, vitrikynang, diachimuctieu, khoangcachyeucau = 0, is_yeucaukhongdichuyen = False, is_ngatdichuyen = False):
        thoidiemhientai = time.time()
        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        thoigiandungim = 0.
        if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
            thoigiandungim = thoidiemhientai - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0.

        if loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynanglendongdoi"):
            if khoangcach <= khoangcachyeucau:
                khoangcachthucteyeucau = khoangcachyeucau
                if thoigiandungim > 0.5 or (idtuthenhanvat == TUTHENHANVAT_DICHUYEN and self._is_dangchaybukhoangcach):
                    # Giới hạn trên để đứng im lâu (đang đánh) không làm khoảng cách yêu cầu giảm mãi khiến nhân vật cứ bò lại gần mục tiêu
                    thoigianbu = min(max(thoigiandungim, 0.5), 1.5)
                    if khoangcachyeucau >= KHOANGCACHSUDUNGKYNANGTAMXA:
                        khoangcachthucteyeucau = khoangcachthucteyeucau - 1.5 - thoigianbu

                if khoangcach > khoangcachthucteyeucau:
                    self._is_dangchaybukhoangcach = True
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachimuctieu,
                        "khoangcachtoida": max(0, khoangcachthucteyeucau - 1.)
                    }
                    return False, True
                else:
                    self._is_dangchaybukhoangcach = False
            else:
                self._is_dangchaybukhoangcach = False
                return False, False

        if thoidiemhientai - self.moitruong.thoidiembatchucnangmoronggannhat < 0.5 or thoidiemhientai - self.moitruong.thoidiemtatchucnangmoronggannhat < 0.5:
            return False, True

        if loaikynang in ("dichuyentiepcancanchien", "dichuyengiukhoangcach", "dichuyentiepcantamxa"):
            if loaikynang == "dichuyengiukhoangcach":
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                    "diachimuctieu": diachimuctieu,
                    "khoangcach": khoangcachyeucau
                }
            else:
                # Ghi nhớ tầm thực sự đánh được (tầm xa bị trừ hao phần bù khi đứng im) để lọc mục tiêu quanh trưởng nhóm
                self._khoangcachvoitoimuctieu = KHOANGCACHSUDUNGKYNANGCANCHIEN if loaikynang == "dichuyentiepcancanchien" else max(KHOANGCACHSUDUNGKYNANGCANCHIEN, khoangcachyeucau - 3.)
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    # Tầm xa chỉ cần chạy vào trong tầm (trừ hao phần bù khoảng cách khi đứng im), không chạy sát mục tiêu
                    "khoangcachtoida": max(0, KHOANGCACHSUDUNGKYNANGCANCHIEN - 1.) if loaikynang == "dichuyentiepcancanchien" else max(0, khoangcachyeucau - 3.),
                }
            return True, True

        elif loaikynang == "battathieuungphapbao":
            self.moitruong.action_thucthicaulenh("pf2 908.6", douutien = DOUUTIEN_CAO)
            self._thoidiembattathieuungphapbaogannhat = thoidiemhientai

        elif loaikynang == "sudungcaoboctacdan":
            if diachimuctieu:
                iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN)
                if iddoituongvatpham:
                    if self.moitruong.get_is_nguoichoi(diachimuctieu):
                        caulenh = "use {}# for {}".format(hex(iddoituongvatpham).replace("0x", ""), self.moitruong.get_idnguoichoi(diachimuctieu))
                    else:
                        caulenh = "use {}# for {}#".format(hex(iddoituongvatpham).replace("0x", ""), hex(self.moitruong.get_iddoituong(diachimuctieu)).replace("0x", ""))
                    if self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_CAO):
                        self._thoidiemsudungcaoboctacdangannhat = thoidiemhientai
        else:
            is_dasudung = True
            if loaikynang == "sudungkynangkhongmuctieu":
                self.moitruong.action_sudungkynangvitri(*vitrikynang)
            elif loaikynang == "sudungkynanglenbanthan":
                self.moitruong.action_sudungkynangvitrilenbanthan(*vitrikynang)
            elif loaikynang == "tancongvatly":
                is_dasudung = self.moitruong.action_sudungtancongvatly(diachimuctieu)
                if is_dasudung:
                    self._is_battudongtancongvatly = True
            elif loaikynang == "sudungkynangmuctieu":
                self.moitruong.action_sudungkynangvitrimuctieu(*vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu)
            elif loaikynang == "sudungkynanglendongdoi":
                self.moitruong.action_sudungkynangvitrimuctieu(*vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu, is_khongkiemtracothetancong = True)
            elif loaikynang == "sudungkynangphudau":
                self.moitruong.action_sudungkynangvitriphudau(*vitrikynang, diachimuctieu, khoangcachphudau = khoangcachyeucau)
            else:
                is_dasudung = False

            if is_dasudung:
                self._thoidiemvohieuquadichuyennhatvatpham = max(self._thoidiemvohieuquadichuyennhatvatpham, thoidiemhientai + 0.5)

            # Kỹ năng không mục tiêu thì không tạo yêu cầu di chuyển rỗng (chặn nhặt đồ/theo nhóm mà không đi đâu cả)
            if diachimuctieu:
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    "khoangcachtoida": khoangcachyeucau
                }

        if khoangcach <= khoangcachyeucau:
            if is_ngatdichuyen:
                self.moitruong.action_ngatdichuyen()

            if is_yeucaukhongdichuyen:
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, thoidiemhientai + 0.5)

        return True, True

    def action_sudungkynangmonphaiduongmon(self):
        if not self._is_tudongsudungkynang: return

        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        is_kynangamkichsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_AMKICH)
        if self._is_kynangamkichsansang and not is_kynangamkichsansang:
            self._thoidiemsudungamkichgannhat = time.time()
        self._is_kynangamkichsansang = is_kynangamkichsansang

        is_kynangthichsatsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THICHSAT)
        if self._is_kynangthichsatsansang and not is_kynangthichsatsansang:
            self._thoidiemsudungthichsatgannhat = time.time()
        self._is_kynangthichsatsansang = is_kynangthichsatsansang

        is_kynangbisatsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BISAT)
        if self._is_kynangbisatsansang and not is_kynangbisatsansang:
            self._thoidiemsudungbisatgannhat = time.time()
        self._is_kynangbisatsansang = is_kynangbisatsansang

        is_kynangmatamthuatsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MATAMTHUAT)
        if self._is_kynangmatamthuatsansang and not is_kynangmatamthuatsansang:
            self._thoidiemsudungmatamthuatgannhat = time.time()
        self._is_kynangmatamthuatsansang = is_kynangmatamthuatsansang

        is_kynangnhiephonchamsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHIEPHONCHAM)
        if self._is_kynangnhiephonchamsansang and not is_kynangnhiephonchamsansang:
            self._thoidiemsudungnhiephonchamgannhat = time.time()
        self._is_kynangnhiephonchamsansang = is_kynangnhiephonchamsansang
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

        is_muctieusudungphapluc = diachimuctieu and self.moitruong.get_idloaivukhi(diachimuctieu) in (IDLOAIVUKHI_KIEM, IDLOAIVUKHI_AMKHI)
        is_muctieulabaothukynangtrieuhoi = self.moitruong.get_is_baothukynangtrieuhoi(diachimuctieu)
        is_muctieulabaothugiangho = self.moitruong.get_is_baothugiangho(diachimuctieu)
        is_muctieulanguoichoi = self.moitruong.get_is_nguoichoi(diachimuctieu)
        is_muctieugiukhoangcach = (is_muctieulanguoichoi and self.moitruong.get_idloaivukhi(diachimuctieu) not in (IDLOAIVUKHI_KIEM, IDLOAIVUKHI_AMKHI))  # or self._is_tudongdichuyendiemdanhxungquanh
        is_muctieupk = is_muctieulanguoichoi or is_muctieulabaothukynangtrieuhoi or is_muctieulabaothugiangho

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0

        is_anthan = self.moitruong.get_is_nhanvatanthan()
        is_bituocvukhi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, is_hieuungcoloi = 0)
        is_bidaohoalacanh = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DAOHOALACANH,), macdinh = False, is_hieuungcoloi = 0)

        is_muctieucomatamthuat = False
        is_muctieutienthanvodich = False
        if diachimuctieu:
            is_muctieucomatamthuat = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MATAMTHUAT,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu)
            is_muctieutienthanvodich = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu)

        is_bandochientruong = self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG

        noilucconlai = self.moitruong.get_noilucconlai()

        danhsachuutien = [
            (VITRIKYNANG_ANTHANTHUAT, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and not is_anthan and diachimuctieu and is_muctieutienthanvodich and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BISAT), 0, None, False),
            (VITRIKYNANG_BISAT, "sudungkynangmuctieu", lambda: noilucconlai > 50 and is_anthan and diachimuctieu and is_muctieutienthanvodich and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and not is_anthan and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5 and time.time() - self._thoidiemsudungnhiephonchamgannhat < 1., 0, None, False),
            (None, "dichuyengiukhoangcach", lambda: not is_bidaohoalacanh and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5 and (time.time() - self._thoidiemsudungmatamthuatgannhat < 0.5 or time.time() - self._thoidiemsudungamkichgannhat < 0.5 or time.time() - self._thoidiemsudungthichsatgannhat < 0.5), khoangcach + 3., None, False),
            (VITRIKYNANG_LACTUYETVONGAN, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and not is_anthan and diachimuctieu and is_muctieupk and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACTUYETVONGAN,), True, is_hieuungcoloi = 1), 0, None, False),
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and not is_anthan and diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA, 0, None, False),
            (VITRIKYNANG_NHIEPHONCHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and is_muctieupk and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "tancongvatly", lambda: diachimuctieu and not self._is_battudongtancongvatly, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and self._is_nhieumuctieugan5 and not is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_SONGLONGDOATCHAU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and (is_muctieupk or is_bandochientruong or self._is_tudongdichuyendiemdanhxungquanh) and not is_muctieucomatamthuat, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and self._is_nhieumuctieugan5 and is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and is_muctieulanguoichoi and is_muctieusudungphapluc and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HAPTINHMACHAM,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_MAIHOACHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_AMKICH, "sudungkynangmuctieu", lambda: not is_bidaohoalacanh and noilucconlai > 50 and diachimuctieu and not is_muctieucomatamthuat and (is_muctieugiukhoangcach or is_bituocvukhi), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() != BANDO_TIVO and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 30. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
            (VITRIKYNANG_THICHSAT, "sudungkynangmuctieu", lambda: not is_bidaohoalacanh and noilucconlai > 50 and diachimuctieu and not is_muctieucomatamthuat and (is_muctieugiukhoangcach or is_bituocvukhi), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "dichuyengiukhoangcach", lambda: not is_bidaohoalacanh and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5, khoangcach + 3., None, False),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "tancongvatly", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "dichuyentiepcantamxa", lambda: not is_bidaohoalacanh and diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen = item

            if callable(dieukien) and not dieukien():
                continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang):
                continue

            target = target if target else diachimuctieu

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen
            )
            if is_break:
                return

    def action_sudungkynangmonphaidaohoanguyen(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = self.moitruong.get_is_nguoichoi(diachimuctieu)
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai()

        thoigiandungim = 0.
        if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
            thoigiandungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

        if diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
            if idtuthenhanvat == TUTHENHANVAT_DUNGIM and thoigiandungim > 1.0:
                if time.time() - self._thoidiemlammoitrangthaigannhat > 1.0:
                    self.action_lammoitrangthai()
                    self._thoidiemlammoitrangthaigannhat = time.time()
                    return

        diachidongdoicanbuff = None
        if not diachimuctieu and self.moitruong.get_is_dangnamtrongnhom():
            diachidongdoicanbuff = self._diachidoituongcanbuffhothekimcangdaohoanguyen

        is_nhatquyenbatsonsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHATQUYENBATSON)
        is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom() and self.moitruong.get_toadotruongnhom() != (65535, 65535)

        danhsachuutien = [
            (VITRIKYNANG_TRANCOTHANUY, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_TRANCOTHANUY] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRANCOTHANUY,), True, is_hieuungcoloi = 1), 0, None, False, False),
            (VITRIKYNANG_KIMTRUNGCHAO, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KIMTRUNGCHAO] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), True, is_hieuungcoloi = 1) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMTRUNGCHAO,), True, is_hieuungcoloi = 1), 0, None, False, False),
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglenbanthan", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_HOTHEKIMCANG] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), True, is_hieuungcoloi = 1), 0, None, False, False),
            (VIRIKYNANG_NGUYENKHIQUYNGUYEN, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_NGUYENKHIQUYNGUYEN] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGUYENKHIQUYNGUYEN,), True, is_hieuungcoloi = 1), 0, None, False, False),
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglendongdoi", lambda: diachidongdoicanbuff and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_HOTHEKIMCANG], KHOANGCACHSUDUNGKYNANGTAMXA, diachidongdoicanbuff, False, False),
            (VITRIKYNANG_KHONGTHUNHAPBACHNHAN, "sudungkynangmuctieu", lambda: diachimuctieu and not is_anhhuongboitruongnhom and is_muctieulanguoichoi and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KHONGTHUNHAPBACHNHAN] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN, HIEUUNGKYNANG_CHOANG), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_DAIHAIVOLUONG, "sudungkynangkhongmuctieu", lambda: diachimuctieu and self._is_nhieumuctieuganbanthan3 and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAIHAIVOLUONG] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, False),
            (VITRIKYNANG_BADONGQUYEN, "sudungkynangmuctieu", lambda: diachimuctieu and not is_anhhuongboitruongnhom and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_BADONGQUYEN] and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN and idtuthenhanvat == TUTHENHANVAT_DICHUYEN, KHOANGCACHSUDUNGKYNANGTAMXA, None, False, False),
            (VITRIKYNANG_BADONGQUYEN, "sudungkynangmuctieu", lambda: diachimuctieu and is_anhhuongboitruongnhom and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_BADONGQUYEN] and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN and idtuthenhanvat == TUTHENHANVAT_DICHUYEN and khoangcach < KHOANGCACHSUDUNGKYNANGTAMXA - 3, KHOANGCACHSUDUNGKYNANGTAMXA, None, False, False),
            (VITRIKYNANG_DAOHOALACANH, "sudungkynangkhongmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAOHOALACANH] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_THONKINH, "sudungkynangmuctieu", lambda: diachimuctieu and not is_anhhuongboitruongnhom and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_THONKINH] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_LACKICH, "sudungkynangmuctieu", lambda: diachimuctieu and not is_anhhuongboitruongnhom and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_LACKICH] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACKICH,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_LACKICH, "sudungkynangmuctieu", lambda: diachimuctieu and is_anhhuongboitruongnhom and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_LACKICH] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACKICH,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_THONKINH, "sudungkynangmuctieu", lambda: diachimuctieu and is_anhhuongboitruongnhom and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_THONKINH] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_PHONGMAQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_PHONGMAQUYET] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_idloaivukhi(diachimuctieu) in (IDLOAIVUKHI_DAO, IDLOAIVUKHI_KIEM) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_METUNGQUYEN, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_METUNGQUYEN] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ROILOAN, HIEUUNGKYNANG_CHOANG), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_KHONGTHUNHAPBACHNHAN, "sudungkynangmuctieu", lambda: diachimuctieu and is_anhhuongboitruongnhom and is_muctieulanguoichoi and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KHONGTHUNHAPBACHNHAN] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN, HIEUUNGKYNANG_CHOANG), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_NHATQUYENBATSON, "sudungkynangmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_NHATQUYENBATSON] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_HACHODAOTAM, "sudungkynangmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_HACHODAOTAM] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (None, "tancongvatly", lambda: diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and (not self._is_battudongtancongvatly or time.time() - self.moitruong._thoidiemsudungtancongvatlygannhat > 5.), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() not in (BANDO_TIVO, BANDO_CHIENTRUONG) and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 5. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), KHOANGCACHSUDUNGKYNANGTAMXA, None, False, False),
            (VITRIKYNANG_KHITRANGSONHA, "sudungkynangmuctieu", lambda: diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and nguyenkhiconlai <= 2, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_BADONGQUYEN, "sudungkynangmuctieu", lambda: diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and ((nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_BADONGQUYEN] + NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_NHATQUYENBATSON]) or (nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_BADONGQUYEN] and not is_nhatquyenbatsonsansang)), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (VITRIKYNANG_LACKICH, "sudungkynangmuctieu", lambda: diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and ((nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_LACKICH] + NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_NHATQUYENBATSON]) or (nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_LACKICH] and not is_nhatquyenbatsonsansang)), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (None, "tancongvatly", lambda: diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False, False),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen, is_ngatdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            target = target if target else diachimuctieu

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen,
                is_ngatdichuyen = is_ngatdichuyen
            )

            if is_break:
                return

    def action_sudungkynangmonphaicamvequan(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai()
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        is_bandochientruong = self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG

        danhsachuutien = [
            (VITRIKYNANG_MANHHOBOPHAP, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_MANHHOBOPHAP] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MANHHOBOPHAP,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_KIMSUBOGIAP, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_KIMSUBOGIAP] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMSUBOPHAP,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_SINHTUTHANLUC, "sudungkynangkhongmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_SINHTUTHANLUC] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_SINHTUTHANLUC,), macdinh = True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_LUANHOIVANCHUYEN, "sudungkynangkhongmuctieu", lambda: diachimuctieu and nguyenkhiconlai < 4 and self.moitruong.get_phantramsinhlucconlai() <= 65, 0, None, True),
            (VITRIKYNANG_PHILONGTAMCHAU, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and idtuthenhanvat == TUTHENHANVAT_DICHUYEN and KHOANGCACHSUDUNGKYNANGTAMXA / 2 <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_PHILONGTAMCHAU], KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
            (VITRIKYNANG_THIENLYTATSAT, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and idtuthenhanvat == TUTHENHANVAT_DICHUYEN and KHOANGCACHSUDUNGKYNANGTAMXA / 2 <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_THIENLYTATSAT], KHOANGCACHSUDUNGKYNANGTAMXA, None, False),

            (VITRIKYNANG_HOANHTAOTHIENQUAN, "sudungkynangkhongmuctieu", lambda: not is_bandochientruong and diachimuctieu and not is_muctieulanguoichoi and self._is_nhieumuctieugan3 and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_HOANHTAOTHIENQUAN], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_CHANTHIENNOHONG, "sudungkynangkhongmuctieu", lambda: not is_bandochientruong and diachimuctieu and is_muctieulanguoichoi and self._is_nhieumuctieugan3 and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_CHANTHIENNOHONG], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "tancongvatly", lambda: diachimuctieu and not self._is_battudongtancongvatly, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_NGULOIAPDINH, "sudungkynangmuctieu", lambda: is_bandochientruong and diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_NGULOIAPDINH], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_TRUCDAOHOANGLONG, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_TRUCDAOHOANGLONG] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_THIENBONGNHATKICH, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu and is_muctieulanguoichoi and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_THIENBONGNHATKICH] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_LOIDINHKICH, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_LOIDINHKICH], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_BADAONOLANG, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_BADAONOLANG], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_GIAOLONGNHAPHAI, "sudungkynangmuctieu", lambda: not is_bandochientruong and diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_GIAOLONGNHAPHAI], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False),
            (None, "tancongvatly", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            target = target if target else diachimuctieu

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen
            )
            if is_break:
                return

    def _get_kynangchophep(self):
        # None = không giới hạn; ngược lại là tập vị trí kỹ năng được phép dùng (xem KYNANGCHOPHEPTHEONHANVAT_MAP)
        kynangchopheps = KYNANGCHOPHEPTHEONHANVAT_MAP.get(self.moitruong.get_idnguoichoi())
        if kynangchopheps is None:
            tennhanvat = " ".join((self.moitruong.get_tendoituong() or "").split()).lower()
            kynangchopheps = KYNANGCHOPHEPTHEONHANVAT_MAP.get(tennhanvat)
        return set(kynangchopheps) if kynangchopheps is not None else None

    def _get_is_cobaothukynangtrieuhoi(self):
        # Bảo thú kỹ năng triệu hồi có tên dạng "Thiên binh (...)", bảo thú giang hồ thì không có ngoặc
        for sothutu in range(1, 4):
            if not self.moitruong.get_iddoituongbaothu(sothutu):
                continue
            tendoituongbaothu = self.moitruong.get_tendoituongbaothu(sothutu) or ""
            if "(" in tendoituongbaothu and ")" in tendoituongbaothu:
                return True
        return False

    def action_sudungkynangmonphaimaoson(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0

        noilucconlai = self.moitruong.get_noilucconlai()
        phantramnoilucconlai = self.moitruong.get_phantramnoilucconlai()
        phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()

        diachithuccot = self._diachidoituongcanbuffthuccotmaoson
        diachithucgiap = self._diachidoituongcanbuffthucgiapmaoson
        diachithuctam = self._diachidoituongcanbuffthuctammaoson
        diachiammanhapthe = self._diachidoituongcanbuffammanhapthemaoson

        idbandohientai = self.moitruong.get_idbandohientai()

        is_cobaothukynangtrieuhoi = self._get_is_cobaothukynangtrieuhoi()
        kynangchopheps = self._get_kynangchophep()

        danhsachuutien = [
            # Huyết Tế: hy sinh 50% khí huyết của bảo thú triệu hồi để hồi cho bản thân (tốn 100 pháp lực)
            (VITRIKYNANG_HUYETTE, "sudungkynangkhongmuctieu", lambda: phantramsinhlucconlai < 50 and is_cobaothukynangtrieuhoi and noilucconlai >= 100, 0, None, True, True),
            # Chưa có bảo thú triệu hồi thì gọi Thiên Binh (tốn 105 pháp lực + 3 Bùa Giấy); chờ 3s sau mỗi lần gọi để bảo thú kịp xuất hiện
            (VITRIKYNANG_TRIEUHOITHIENBINH, "sudungkynangkhongmuctieu", lambda: not is_cobaothukynangtrieuhoi and noilucconlai >= 105 and time.time() - self._thoidiemtrieuhoithienbinhgannhat > 3. and self.moitruong.action_timkiemvatphamhanhtrang(BUAGIAY), 0, None, True, True),
            (VITRIKYNANG_HUYETMACHU, "sudungkynangkhongmuctieu", lambda: phantramsinhlucconlai > 25 and phantramnoilucconlai <= 50, 0, None, True, False),
            (VITRIKYNANG_THANTUEPHAPCHU, "sudungkynangkhongmuctieu", lambda: noilucconlai > 150 and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THANTUEPHAPCHU,), macdinh = True, is_hieuungcoloi = 1), 0, None, True, False),

            # (VITRIKYNANG_AMMANHAPTHE, "sudungkynangmuctieu", lambda: diachiammanhapthe and noilucconlai > 50, KHOANGCACHSUDUNGKYNANGTAMXA, diachiammanhapthe, True, True),
            (VITRIKYNANG_THUCCOT, "sudungkynangmuctieu", lambda: diachithuccot and idbandohientai != BANDO_BATQUAITRAN and noilucconlai > 50, KHOANGCACHSUDUNGKYNANGTAMXA, diachithuccot, True, True),
            (VITRIKYNANG_THUCGIAP, "sudungkynangmuctieu", lambda: diachithucgiap and idbandohientai != BANDO_BATQUAITRAN and noilucconlai > 50, KHOANGCACHSUDUNGKYNANGTAMXA, diachithucgiap, True, True),
            (VITRIKYNANG_THUCTAM, "sudungkynangmuctieu", lambda: diachithuctam and noilucconlai > 50, KHOANGCACHSUDUNGKYNANGTAMXA, diachithuctam, True, True),

            (VITRIKYNANG_DITINHDAIPHAP, "sudungkynangkhongmuctieu", lambda: noilucconlai > 150 and time.time() - self._thoidiemsudungditinhdaiphapgannhat > 30 and self._is_baothukynangtrieuhoihetnoiluc, 0, None, True, True),
            (VITRIKYNANG_LUUHUYETTHUAT, "sudungkynangkhongmuctieu", lambda: noilucconlai > 150 and time.time() - self._thoidiemsudungluuhuyetthuatgannhat > 30 and self._is_baothukynangtrieuhoihetsinhluc, 0, None, True, True),

            (VITRIKYNANG_LOIDONGCUUTHIEN, "sudungkynangkhongmuctieu", lambda: diachimuctieu and noilucconlai > 50 and self._is_nhieumuctieuganbanthan3 and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN, None, True, True),
            (VITRIKYNANG_PHUCMAQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),

            (None, "dichuyentiepcantamxa", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, False, False),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen, is_ngatdichuyen = item
            if vitrikynang and kynangchopheps is not None and vitrikynang not in kynangchopheps:
                continue
            if callable(dieukien) and not dieukien():
                continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang):
                continue
            target_use = target if target else diachimuctieu
            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target_use,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen,
                is_ngatdichuyen = is_ngatdichuyen
            )

            if vitrikynang == VITRIKYNANG_LOIDONGCUUTHIEN and is_ok:
                self.moitruong.action_chovankhi(1.5)
            if vitrikynang == VITRIKYNANG_TRIEUHOITHIENBINH and is_ok:
                self._thoidiemtrieuhoithienbinhgannhat = time.time()
                self.moitruong.action_chovankhi(1.5)
            if vitrikynang == VITRIKYNANG_DITINHDAIPHAP and is_ok:
                self._thoidiemsudungditinhdaiphapgannhat = time.time()
            if vitrikynang == VITRIKYNANG_LUUHUYETTHUAT and is_ok:
                self._thoidiemsudungluuhuyetthuatgannhat = time.time()
            if is_break:
                return

    def action_sudungkynangmonphaivanmongcoc(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)

        diachidoituongcanhoisinh = self._diachidoituongcanhoisinhvanmongcoc
        diachidoituongcanbufftaytranquyet = self._diachidoituongcanbufftaytranquyetvanmongcoc
        diachidoituongcanbufftaytranquyet2 = self._diachidoituongcanbufftaytranquyet2vanmongcoc
        diachidoituongcanbufflinhkhihothe = self._diachidoituongcanbufflinhkhihothevanmongcoc
        diachidoituongcanbommau = self._diachidoituongcanbommauvanmongcoc
        diachidoituongcanbuffkimcham = self._diachidoituongcanbuffkimchamvanmongcoc
        diachidoituongcanbuffngancham = self._diachidoituongcanbuffnganchamvanmongcoc
        diachidoituongcanbuffcuongthethuat = self._diachidoituongcanbuffcuongthethuatvanmongcoc

        diachidoituongcanbuffphonganthuat = self._diachidoituongcanbuffphonganthuatvanmongcoc
        diachidoituongcanbuffhuyenquangthiemanh = self._diachidoituongcanbuffhuyenquangthiemanhvanmongcoc

        is_cohieuungdauchuyentinhdi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DAUCHUYENTINHDI,), macdinh = False, is_hieuungcoloi = 1)

        diachicantiepcan = None

        if diachidoituongcanbuffphonganthuat and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGANTHUAT):
            diachicantiepcan = diachidoituongcanbuffphonganthuat
        elif diachidoituongcanbuffhuyenquangthiemanh and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYENQUANGTHIEMANH):
            diachicantiepcan = diachidoituongcanbuffhuyenquangthiemanh
        # Chỉ tiếp cận đối tượng cần buff khi kỹ năng tương ứng đã học và sẵn sàng, tránh đứng yên cạnh đồng đội/bản thân mà không đánh quái
        elif diachidoituongcanhoisinh and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAITUHOANSINH):
            diachicantiepcan = diachidoituongcanhoisinh
        elif diachidoituongcanbufftaytranquyet and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TAYTRANQUYET):
            diachicantiepcan = diachidoituongcanbufftaytranquyet
        elif diachidoituongcanbommau and any(self.moitruong.get_is_kynangsansang(*vitri) for vitri in (VITRIKYNANG_CAMLOTRI, VITRIKYNANG_KHIETVANQUYET, VITRIKYNANG_SOTRI, VITRIKYNANG_VODINHLUUTHUY)):
            diachicantiepcan = diachidoituongcanbommau
        elif diachidoituongcanbufftaytranquyet2 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TAYTRANQUYET):
            diachicantiepcan = diachidoituongcanbufftaytranquyet2
        elif diachidoituongcanbuffkimcham and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCHAMDOACH):
            diachicantiepcan = diachidoituongcanbuffkimcham
        elif diachidoituongcanbuffngancham and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGANCHAMDOACH):
            diachicantiepcan = diachidoituongcanbuffngancham
        elif diachidoituongcanbuffcuongthethuat and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CUONGTHETHUAT):
            diachicantiepcan = diachidoituongcanbuffcuongthethuat
        elif diachimuctieu and not is_muctieulanguoichoi:
            diachicantiepcan = diachimuctieu
        elif diachidoituongcanbufflinhkhihothe and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LINHKHIHOTHE):
            diachicantiepcan = diachidoituongcanbufflinhkhihothe

        is_nganchamdoachsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGANCHAMDOACH)
        if self._is_nganchamdoachsansang and not is_nganchamdoachsansang and self._idnguoichoibuffnganchamgannhat:
            self._thoidiembuffnganchamgannhat_map[self._idnguoichoibuffnganchamgannhat] = time.time()
        self._is_nganchamdoachsansang = is_nganchamdoachsansang

        is_kimchamdoachsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCHAMDOACH)
        if self._is_kimchamdoachsansang and not is_kimchamdoachsansang and self._idnguoichoibuffkimchamgannhat:
            self._thoidiembuffkimchamgannhat_map[self._idnguoichoibuffkimchamgannhat] = time.time()
        self._is_kimchamdoachsansang = is_kimchamdoachsansang

        is_cuongthethuatsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CUONGTHETHUAT)
        if self._is_cuongthethuatsansang and not is_cuongthethuatsansang and self._idnguoichoibuffcuongthethuatgannhat:
            self._thoidiembuffcuongthethuatgannhat_map[self._idnguoichoibuffcuongthethuatgannhat] = time.time()
        self._is_cuongthethuatsansang = is_cuongthethuatsansang

        noilucconlai = self.moitruong.get_noilucconlai()
        noiluctoida = self.moitruong.get_noiluctoida()
        phantramnoiluc = int(noilucconlai * 100 / noiluctoida) if noiluctoida else 0
        khoangcachmuctieutancong = self.moitruong.get_khoangcach(diachimuctieu)
        is_contranky = self.moitruong.action_timkiemvatphamhanhtrang(TRANKY)
        is_dangbatpk = self.moitruong.get_idmaupk() != MAUPK_HOABINH

        idloaivukhimuctieu = self.moitruong.get_idloaivukhi(diachimuctieu)
        is_muctieugiukhoangcach = (is_muctieulanguoichoi and idloaivukhimuctieu not in (IDLOAIVUKHI_KIEM, IDLOAIVUKHI_AMKHI))

        is_cobaothukynangtrieuhoi = self._get_is_cobaothukynangtrieuhoi()

        danhsachuutien = [
            # Chưa có bảo thú triệu hồi thì Rải Đậu Thành Binh (tốn 60 pháp lực + Đậu Nành); chờ 3s sau mỗi lần gọi để Đậu Binh kịp xuất hiện
            (VITRIKYNANG_RAIDAUTHANHBINH, "sudungkynangkhongmuctieu", lambda: not is_cobaothukynangtrieuhoi and noilucconlai >= 60 and time.time() - self._thoidiemraidauthanhbinhgannhat > 3. and self.moitruong.action_timkiemvatphamhanhtrang(DAUNANH), 0, None, True),
            (VITRIKYNANG_PHONGANTHUAT, "sudungkynangmuctieu", lambda: noilucconlai > 200 and diachidoituongcanbuffphonganthuat and self.moitruong.get_khoangcach(diachidoituongcanbuffphonganthuat) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffphonganthuat, True),
            (VITRIKYNANG_HUYENQUANGTHIEMANH, "sudungkynangmuctieu", lambda: noilucconlai > 200 and diachidoituongcanbuffhuyenquangthiemanh and self.moitruong.get_khoangcach(diachidoituongcanbuffhuyenquangthiemanh) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffhuyenquangthiemanh, True),

            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() not in (BANDO_TIVO, BANDO_CHIENTRUONG) and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 5. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
            (VITRIKYNANG_TOANPHONGQUYET, "sudungkynangmuctieu", lambda: noilucconlai > 200 and diachimuctieu and is_muctieulanguoichoi and khoangcachmuctieutancong <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_phantramsinhlucconlai(diachimuctieu) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 1), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_CAITUHOANSINH, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and diachidoituongcanhoisinh and self.moitruong.get_khoangcach(diachidoituongcanhoisinh) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanhoisinh, True),
            (VITRIKYNANG_TAYTRANQUYET, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and diachidoituongcanbufftaytranquyet and self.moitruong.get_khoangcach(diachidoituongcanbufftaytranquyet) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbufftaytranquyet, True),
            (VITRIKYNANG_CAMLOTRI, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcach(diachidoituongcanbommau) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True),
            (VITRIKYNANG_KHIETVANQUYET, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcach(diachidoituongcanbommau) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True),
            (VITRIKYNANG_SOTRI, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcach(diachidoituongcanbommau) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True),
            (VITRIKYNANG_VODINHLUUTHUY, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and self.moitruong.get_khoangcach(diachidoituongcanbommau) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True),
            (VITRIKYNANG_TAYTRANQUYET, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and diachidoituongcanbufftaytranquyet2 and self.moitruong.get_khoangcach(diachidoituongcanbufftaytranquyet2) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbufftaytranquyet2, True),
            (VITRIKYNANG_NGANCHAMDOACH, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and diachidoituongcanbuffngancham and self.moitruong.get_khoangcach(diachidoituongcanbuffngancham) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffngancham, True),
            (VITRIKYNANG_KIMCHAMDOACH, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and diachidoituongcanbuffkimcham and self.moitruong.get_khoangcach(diachidoituongcanbuffkimcham) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffkimcham, True),
            (VITRIKYNANG_CUONGTHETHUAT, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and diachidoituongcanbuffcuongthethuat and self.moitruong.get_khoangcach(diachidoituongcanbuffcuongthethuat) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffcuongthethuat, True),

            (None, "dichuyentiepcantamxa", lambda: diachicantiepcan and self.moitruong.get_khoangcach(diachicantiepcan) > KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachicantiepcan, False),

            (VITRIKYNANG_DONGIAPTRAN, "sudungkynangphudau", lambda: noilucconlai > 200 and not is_dangbatpk and diachimuctieu and is_contranky and phantramnoiluc > 25 and khoangcachmuctieutancong <= KHOANGCACHSUDUNGKYNANGTAMXA, khoangcachmuctieutancong + random.choice([-1, 1]), None, True),
            (VITRIKYNANG_KYMONTRAN, "sudungkynangphudau", lambda: noilucconlai > 200 and not is_dangbatpk and diachimuctieu and is_contranky and phantramnoiluc > 25 and khoangcachmuctieutancong <= KHOANGCACHSUDUNGKYNANGTAMXA, khoangcachmuctieutancong + random.randint(0, 0), None, True),
            (VITRIKYNANG_LIETPHONGQUYET, "sudungkynangmuctieu", lambda: noilucconlai > 200 and not is_dangbatpk and diachimuctieu and khoangcachmuctieutancong <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "tancongvatly", lambda: diachimuctieu and khoangcachmuctieutancong <= KHOANGCACHSUDUNGKYNANGTAMXA and (not self._is_battudongtancongvatly or time.time() - self.moitruong._thoidiemsudungtancongvatlygannhat > 5.), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            # (VITRIKYNANG_PHONGVUKINHTHIEN, "sudungkynangmuctieu", lambda: noilucconlai > 200 and not is_dangbatpk and diachimuctieu and khoangcachmuctieutancong <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),

            (VITRIKYNANG_LINHKHIHOTHE, "sudungkynanglendongdoi", lambda: noilucconlai > 200 and diachidoituongcanbufflinhkhihothe and self.moitruong.get_khoangcach(diachidoituongcanbufflinhkhihothe) <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbufflinhkhihothe, True),
            (None, "dichuyengiukhoangcach", lambda: diachimuctieu and is_muctieugiukhoangcach and khoangcachmuctieutancong <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5, khoangcachmuctieutancong + 3., None, False),

            (None, "dichuyentiepcantamxa", lambda: diachicantiepcan and self.moitruong.get_khoangcach(diachicantiepcan) > KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, diachicantiepcan, False),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            target = target if target else diachimuctieu

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen
            )

            if vitrikynang == VITRIKYNANG_RAIDAUTHANHBINH and is_ok:
                self._thoidiemraidauthanhbinhgannhat = time.time()
                # Danh sách ưu tiên Vân Mộng Cốc không có tham số ngắt di chuyển nên ngắt thủ công: đang chạy sẽ làm hỏng vận khí
                self.moitruong.action_ngatdichuyen()
                self.moitruong.action_chovankhi(1.5)

            if is_ok and target:
                if self.moitruong.get_is_nguoichoi(target):
                    idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(target)
                    if idnguoichoidangxemxet:
                        if vitrikynang == VITRIKYNANG_CAITUHOANSINH:
                            self._thoidiemcaituhoansinh_map[idnguoichoidangxemxet] = time.time()
                        if vitrikynang == VITRIKYNANG_NGANCHAMDOACH:
                            self._idnguoichoibuffnganchamgannhat = idnguoichoidangxemxet
                        if vitrikynang == VITRIKYNANG_KIMCHAMDOACH:
                            self._idnguoichoibuffkimchamgannhat = idnguoichoidangxemxet
                        if vitrikynang == VITRIKYNANG_CUONGTHETHUAT:
                            self._idnguoichoibuffcuongthethuatgannhat = idnguoichoidangxemxet

            if is_break:
                return

    def action_tudongsudungkynang(self):
        self._yeucautancong = None

        if self._is_battudongtancongvatly and self.moitruong.get_is_nhanvatbichoang():
            self._is_battudongtancongvatly = False

        if self._trangthaiveban != 0:
            return

        if self._is_danggomquai:
            return

        if self._is_danguutiennhatdo:
            return

        if self.moitruong.get_is_nhanvatchuasansang(self.moitruong.get_diachicosothongtinnhanvat1()):
            return
        if time.time() - self._thoidiemtamngungsudungkynang < 0.:
            return

        tenmonphai = self.moitruong.get_tenmonphai()

        if tenmonphai is None:
            self.action_sudungkynangvomonphai()
        elif hasattr(self, f"action_sudungkynangmonphai{tenmonphai}"):
            getattr(self, f"action_sudungkynangmonphai{tenmonphai}")()
        elif hasattr(self, f"_action_sudungkynang_{tenmonphai}"):
            getattr(self, f"_action_sudungkynang_{tenmonphai}")()

    def action_sudungkynangvomonphai(self):
        # Nhân vật chưa có môn phái: chỉ dùng tấn công vật lý
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachimuctieu: return

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu)
        # Cầm ám khí thì đánh tầm xa, còn lại đánh cận chiến
        khoangcachtancong = KHOANGCACHSUDUNGKYNANGTAMXA if self.moitruong.get_idloaivukhi() == IDLOAIVUKHI_AMKHI else KHOANGCACHSUDUNGKYNANGCANCHIEN

        danhsachuutien = [
            (None, "tancongvatly", lambda: khoangcach <= khoangcachtancong and (not self._is_battudongtancongvatly or time.time() - self.moitruong._thoidiemsudungtancongvatlygannhat > 5.), khoangcachtancong, None, False, True),
            (None, "dichuyentiepcancanchien", lambda: khoangcachtancong == KHOANGCACHSUDUNGKYNANGCANCHIEN and khoangcach > khoangcachtancong, 0, None, False, False),
            (None, "dichuyentiepcantamxa", lambda: khoangcachtancong == KHOANGCACHSUDUNGKYNANGTAMXA and khoangcach > khoangcachtancong, khoangcachtancong, None, False, False),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen, is_ngatdichuyen = item

            if callable(dieukien) and not dieukien(): continue

            target = target if target else diachimuctieu

            is_ok, is_break = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_yeucaukhongdichuyen = is_yeucaukhongdichuyen,
                is_ngatdichuyen = is_ngatdichuyen
            )

            if is_break:
                return

    def action_sudungkynangmonphaithucson(self):
        if self._is_thucsondao:
            self.action_sudungkynangmonphaithucsondao()
        else:
            self.action_sudungkynangmonphaithucsonkiem()

    def action_sudungkynangmonphaithucsonkiem(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieupk = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        phantramsinhluc = self.moitruong.get_phantramsinhlucconlai()

        diachidongdoicanbuff = None
        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

        danhsachungviens = [self.moitruong.get_diachicosothongtinnhanvat1()]
        if self.moitruong.get_is_dangnamtrongnhom():
            j = -1
            while True:
                j += 1
                addr = self.moitruong.get_diachicosothongtindoituongx(j)
                if not addr:
                    break
                if not self.moitruong.get_is_nhanvattontai(addr) or self.moitruong.get_is_nhanvatdachet(addr):
                    continue
                if self.moitruong.get_khoangcach(addr) > KHOANGCACHSUDUNGKYNANGTAMXA:
                    continue
                id_nd = self.moitruong.get_idnguoichoi(addr)
                if id_nd in idnguoichoithanhviennhoms and id_nd != self.moitruong.get_idnguoichoi():
                    danhsachungviens.append(addr)

        for addr in danhsachungviens:
            is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), diachicosothongtinnhanvat = addr, macdinh = True, is_hieuungcoloi = 1)
            is_quathoigian = False

            if is_thieuhieuung or is_quathoigian:
                diachidongdoicanbuff = addr
                break
        self._is_khongcongidebuff = not diachidongdoicanbuff
        is_tieuchuthiensansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN)
        if self._is_tieuchuthiensansang and not is_tieuchuthiensansang and self._idnguoichoibuffnoikhanggannhat:
            self._thoidiembuffnoikhanggannhat_map[self._idnguoichoibuffnoikhanggannhat] = time.time()
        self._is_tieuchuthiensansang = is_tieuchuthiensansang

        capdonhanvat = self.moitruong.get_capdonhanvat()

        noilucconlai = self.moitruong.get_noilucconlai()
        danhsachuutien = [
            (VITRIKYNANG_TINHTAMQUYET, "sudungkynangkhongmuctieu", lambda: noilucconlai > 100 and self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0), 0, None, True),
            (VITRIKYNANG_TIENKHI, "sudungkynanglenbanthan", lambda: phantramsinhluc <= 75 and noilucconlai > 100, 0, None, True),
            (VITRIKYNANG_TIENTHANVODICH, "sudungkynangkhongmuctieu", lambda: noilucconlai > 100 and (phantramsinhluc <= 25 or (is_muctieupk and phantramsinhluc <= 50)), 0, None, True),
            (VITRIKYNANG_TIEUCHUTHIEN, "sudungkynanglendongdoi", lambda: noilucconlai > 100 and diachidongdoicanbuff, KHOANGCACHSUDUNGKYNANGTAMXA, diachidongdoicanbuff, False),
            (VITRIKYNANG_BANGPHACHNGANTAM, "sudungkynangkhongmuctieu", lambda: noilucconlai > 100 and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_LANGKHONGCHIHUYET, "sudungkynangmuctieu", lambda: noilucconlai > 100 and is_muctieupk and self.moitruong.get_is_cothegaychoang(diachimuctieu) and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_VANKIEMXUYENTAM, "sudungkynangmuctieu", lambda: noilucconlai > 100 and is_muctieupk and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_NGUKIEMPHITIEN, "sudungkynangkhongmuctieu", lambda: noilucconlai > 100 and capdonhanvat > 35 and diachimuctieu and self._is_nhieumuctieugan9 and khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN, 0, None, True),
            (VITRIKYNANG_NGUKIEMTHUAT, "sudungkynangmuctieu", lambda: noilucconlai > 100 and diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_BANGTAMTHUC, "sudungkynangmuctieu", lambda: noilucconlai > 100 and diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_VANVUTIEUDIEU, "sudungkynangmuctieu", lambda: noilucconlai > 100 and diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_TIENNHANCHILO, "sudungkynangmuctieu", lambda: noilucconlai > 100 and diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "dichuyentiepcantamxa", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
            (None, "tancongvatly", lambda: noilucconlai < 100 and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
        ]

        for vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_yeucaukhongdichuyen in danhsachuutien:
            if callable(dieukien) and not dieukien():
                continue

            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang):
                continue

            is_ok, is_break = self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, target if target else diachimuctieu, khoangcachyeucau, is_yeucaukhongdichuyen)
            if is_ok and vitrikynang == VITRIKYNANG_TIEUCHUTHIEN and target:
                self._idnguoichoibuffnoikhanggannhat = self.moitruong.get_idnguoichoi(target)
            if is_break:
                return

    def action_sudungkynangmonphaithucsondao(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        phantramsinhluc = self.moitruong.get_phantramsinhlucconlai()
        noiluc = self.moitruong.get_noilucconlai()

        diachidongdoicanbuff = None
        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
        danhsachungviens = [self.moitruong.get_diachicosothongtinnhanvat1()]

        if self.moitruong.get_is_dangnamtrongnhom():
            j = -1
            while True:
                j += 1
                addr = self.moitruong.get_diachicosothongtindoituongx(j)
                if not addr: break
                if not self.moitruong.get_is_nhanvattontai(addr) or self.moitruong.get_is_nhanvatdachet(addr): continue
                if self.moitruong.get_khoangcach(addr) > KHOANGCACHSUDUNGKYNANGTAMXA: continue
                id_nd = self.moitruong.get_idnguoichoi(addr)
                if id_nd in idnguoichoithanhviennhoms and id_nd != self.moitruong.get_idnguoichoi():
                    danhsachungviens.append(addr)

        for addr in danhsachungviens:
            id_nd = self.moitruong.get_idnguoichoi(addr)
            is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), diachicosothongtinnhanvat = addr, macdinh = True, is_hieuungcoloi = 1)
            is_quathoigian = self.moitruong.get_diachicosothongtinnhanvat1() != addr and self.moitruong.get_is_nguoichoi(addr) and time.time() - self._thoidiembuffnoikhanggannhat_map.get(id_nd, 0) > 60
            if is_thieuhieuung or is_quathoigian:
                diachidongdoicanbuff = addr
                break

        self._is_khongcongidebuff = not diachidongdoicanbuff
        is_tieuchuthiensansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN)
        if self._is_tieuchuthiensansang and not is_tieuchuthiensansang and self._idnguoichoibuffnoikhanggannhat:
            self._thoidiembuffnoikhanggannhat_map[self._idnguoichoibuffnoikhanggannhat] = time.time()
        self._is_tieuchuthiensansang = is_tieuchuthiensansang

        if diachimuctieu and self.moitruong.get_is_cothetancong(diachimuctieu):
            if self._idmuctieuluutinhtruymang != diachimuctieu:
                self._idmuctieuluutinhtruymang = diachimuctieu
                self._solanthatbailuutinhtruymang = 0

            is_luutinhtruymangsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG)

            if self._is_luutinhtruymangsansang and not is_luutinhtruymangsansang:
                if khoangcach <= 1.5:
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)

            self._is_luutinhtruymangsansang = is_luutinhtruymangsansang

            if self._solanthatbailuutinhtruymang >= self._solanthatbailuutinhtruymangtoida and time.time() - self._thoidiembiphatluutinhtruymang > 3.0:
                self._solanthatbailuutinhtruymang = 0
                self._thoidiembiphatluutinhtruymang = 0.

            if not is_luutinhtruymangsansang:
                self._solanthatbailuutinhtruymang = 0
                self._thoidiembiphatluutinhtruymang = 0.

            is_luutinhtruymangbicam = time.time() - self._thoidiemtamngungluutinhtruymang < 0.8
            is_sudungluutinhtruymangthatbai = is_luutinhtruymangbicam and is_luutinhtruymangsansang
            if is_sudungluutinhtruymangthatbai and self._solanthatbailuutinhtruymang < self._solanthatbailuutinhtruymangtoida:
                self._solanthatbailuutinhtruymang += 1
                if self._solanthatbailuutinhtruymang == self._solanthatbailuutinhtruymangtoida:
                    self._thoidiembiphatluutinhtruymang = time.time()

            is_duocphepsudungluutinhtruymang = is_luutinhtruymangsansang and noiluc > 50 and self._solanthatbailuutinhtruymang < self._solanthatbailuutinhtruymangtoida and idtuthenhanvat not in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT)
            is_bimatamthuat = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MATAMTHUAT,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu)

            if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and is_duocphepsudungluutinhtruymang and not is_bimatamthuat:
                self._yeucautancong = None
                if self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUUTINHTRUYMANG):
                    self._thoidiemtamngungluutinhtruymang = time.time()
                    self._solansudungluutinhtruymang += 1
                    return

        danhsachuutien = [
            (VITRIKYNANG_TINHTAMQUYET, "sudungkynangkhongmuctieu", lambda: noiluc > 150 and self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0), 0, None, True),
            (VITRIKYNANG_TIENKHI, "sudungkynanglenbanthan", lambda: noiluc > 150 and phantramsinhluc <= 75, 0, None, True),
            (VITRIKYNANG_TIEUCHUTHIEN, "sudungkynanglendongdoi", lambda: noiluc > 150 and diachidongdoicanbuff, KHOANGCACHSUDUNGKYNANGTAMXA, diachidongdoicanbuff, True),
            (VITRIKYNANG_BANGPHACHNGANTAM, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1), 0, None, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False),
            (VITRIKYNANG_NGHENHPHONGTRAM, "sudungkynangmuctieu", lambda: diachimuctieu and noiluc > 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_PHAKHONGKICH, "sudungkynangmuctieu", lambda: diachimuctieu and noiluc > 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_PHAMATRAM, "sudungkynangmuctieu", lambda: diachimuctieu and noiluc > 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_DONDAOTRUCNHAP, "sudungkynangmuctieu", lambda: diachimuctieu and noiluc > 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (None, "tancongvatly", lambda: diachimuctieu and noiluc < 150, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
        ]

        for vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngat in danhsachuutien:
            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            is_ok, is_break = self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, target if target else diachimuctieu, khoangcachyeucau, is_ngat)
            if is_ok and vitrikynang == VITRIKYNANG_TIEUCHUTHIEN and target:
                self._idnguoichoibuffnoikhanggannhat = self.moitruong.get_idnguoichoi(target)
            if is_break:
                return

    def battat_chedobufftoanbang(self):
        self._is_chedobufftoanbang = not self._is_chedobufftoanbang
        if self._is_chedobufftoanbang:
            phatam("Bật chế độ buff toàn bang")
        else:
            phatam("Tắt chế độ buff toàn bang")

    def battat_is_uutienbaothukynangtrieuhoi(self):
        self._is_uutienbaothukynangtrieuhoi = not self._is_uutienbaothukynangtrieuhoi
        if self._is_uutienbaothukynangtrieuhoi:
            phatam("Bật ưu tiên đánh đệ Mao Sơn")
        else:
            phatam("Tắt ưu tiên đánh đệ Mao Sơn")

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

    def battat_is_tudongtheosautruongnhom(self):
        self._is_tudongtheosautruongnhom = not self._is_tudongtheosautruongnhom
        if self._is_tudongtheosautruongnhom:
            phatam("Bật tự động theo sau trưởng nhóm")
        else:
            phatam("Tắt tự động theo sau trưởng nhóm")

    def battat_is_tudongkhaikhoang(self):
        self._is_tudongkhaikhoang = not self._is_tudongkhaikhoang
        if self._is_tudongkhaikhoang:
            phatam("Bật tự động khai khoáng")
        else:
            phatam("Tắt tự động khai khoáng")

    def battat_tudonggomquai(self):
        self._is_tudonggomquai = not self._is_tudonggomquai
        self._is_danggomquai = False
        self._danhsachidquaidagom.clear()
        if self._is_tudonggomquai:
            phatam("Bật tự động gom quái")
        else:
            phatam("Tắt tự động gom quái")

    def battat_tudongvebanrac(self):
        self._is_tudongvebanrac = not self._is_tudongvebanrac
        self._trangthaiveban = 0

        if self._is_tudongvebanrac:
            phatam("Bật tự động về bán rác")
        else:
            phatam("Tắt tự động về bán rác")

    def battat_tudongdaotangbaodo(self):
        self._is_tudongdaotangbaodo = not self._is_tudongdaotangbaodo
        if self._is_tudongdaotangbaodo:
            phatam("Bật tự động đào tàng bảo đồ")
        else:
            phatam("Tắt tự động đào tàng bảo đồ")

    def battat_is_tudongdichientruong(self):
        self._is_tudongdichientruong = not self._is_tudongdichientruong
        if self._is_tudongdichientruong:
            phatam("Bật tự động đi chiến trường")
        else:
            phatam("Tắt tự động đi chiến trường")

    def them_tenmuctieutancong(self, tenmuctieutancong):
        if tenmuctieutancong:
            if "( Cấp" in tenmuctieutancong:
                tenmuctieutancong = tenmuctieutancong.split("( Cấp")[0].strip()
            elif "(Cấp" in tenmuctieutancong:
                tenmuctieutancong = tenmuctieutancong.split("(Cấp")[0].strip()

            if tenmuctieutancong not in self._tenmuctieutancongs:
                self._tenmuctieutancongs.add(tenmuctieutancong)
                if self._tenmuctieutancongs:
                    print("Danh sách mục tiêu tấn công: {}".format(self._tenmuctieutancongs))
                    phatam("Thêm tên mục tiêu tấn công. Tổng cộng {}".format(len(self._tenmuctieutancongs)))

    def them_tenmuctieukhongtancong(self, tenmuctieukhongtancong):
        if tenmuctieukhongtancong:
            if "( Cấp" in tenmuctieukhongtancong:
                tenmuctieukhongtancong = tenmuctieukhongtancong.split("( Cấp")[0].strip()
            elif "(Cấp" in tenmuctieukhongtancong:
                tenmuctieukhongtancong = tenmuctieukhongtancong.split("(Cấp")[0].strip()

            if tenmuctieukhongtancong not in self._tenmuctieukhongtancongs:
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

    def action_tudongmuaauto(self):
        if not self._is_tudongbattatchucnangmorong:
            return
        if not self._is_tudongdichuyendiemdanhxungquanh:
            return
        if time.time() - self._thoidiemmuaautogannhat < 5.:
            return
        self._thoidiemmuaautogannhat = time.time()
        self.moitruong.action_thucthicaulenh("auto buy 5 10")

    def action_tudongvutvatpham(self):
        if time.time() - self._thoidiemvutvatphamgannhat < 1.:
            return

        if not self._is_tudongkhaikhoang:
            return

        tenvatphamvutdis = []
        for i in range(6, self.moitruong.get_soluongvatphamhanhtrangtoida()):
            tenvatphamhanhtrang = self.moitruong.get_tenvatphamhanhtrang(i)
            if tenvatphamhanhtrang and tenvatphamhanhtrang not in VATPHAMKHONGBANs and tenvatphamhanhtrang in tenvatphamvutdis:
                motavatpham = self.moitruong.get_motavatphamhanhtrang(i)
                if "Phong Ấn" not in motavatpham:
                    self.moitruong.action_thucthicaulenh2("drop ! {}#30".format(hex(self.moitruong.get_iddoituongvatphamhanhtrang(i))).replace("0x", ""))
                    break

        return

    def action_tudongnhatvatpham(self):
        yeucaunhatvatphammoi = None

        if not self._is_tudongnhatvatpham:
            self._yeucaunhatvatpham = None
            return

        is_dangnamtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        is_truongnhom = self.moitruong.get_is_truongnhom()

        # Đang theo sau trưởng nhóm thì chỉ nhặt vật phẩm ưu tiên
        is_chinhatvatphamuutien = is_dangnamtrongnhom and not is_truongnhom and self._is_tudongtheosautruongnhom

        if self.moitruong.get_is_dayhanhtrang():
            if time.time() - self._thoidiemphatamdayhanhtrang > 5.0:
                if not self._is_tudongvebanrac:
                    pass
                self._thoidiemphatamdayhanhtrang = time.time()

            self._diachicosovatphamdangnhat = False
            self._yeucaunhatvatpham = None
            return

        vatphamtudongnhats = VATPHAMTUDONGNHATs
        if self._is_tudongvebanrac:
            vatphamtudongnhats = (*vatphamtudongnhats,
                                  TIENTE, "Tơ Nhện", "Kịch Độc Châm", "Đuôi Bọ Cạp", "Ly Hồn", "Ly Phách", "Ma Tinh thạch", "Trái Táo", "Trái lê", "Phá Bố Y", "Toái Lăng", "Tơ Tằm", "Da Rắn", "Ống Tên", "Bao Kiếm", "Cán Đao", "Toái Sa", "Hồng Sắc Tiểu Thạch", "Mạng Nhện", "Tử Giả Di Vật", "Phi Hành Phiến", "Núm Vú", "Hành Quân Tán"
                                  )

        def kiemtradieukiennhat(tenvatphamkiemtra):
            if tenvatphamkiemtra in VATPHAMKHONGNHATs:
                return False
            if tenvatphamkiemtra in VATPHAMUUTIENNHATs:
                return True
            if is_chinhatvatphamuutien:
                return False
            if tenvatphamkiemtra in vatphamtudongnhats:
                return True
            if VATPHAMTUDONGNHATFARMs and self._is_tudongvebanrac and any(x in tenvatphamkiemtra for x in VATPHAMTUDONGNHATFARMs):
                return True
            if self._tenvatphamnhats and tenvatphamkiemtra in self._tenvatphamnhats:
                return True
            return False

        is_vatphamdangnhathople = True

        if self._diachicosovatphamdangnhat:
            tenvatphamhientai = self.moitruong.get_tendoituong(self._diachicosovatphamdangnhat)

            if not self.moitruong.get_is_vatphamtontai(self._diachicosovatphamdangnhat):
                is_vatphamdangnhathople = False
            elif self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat) >= KHOANGCACHNHATDO:
                is_vatphamdangnhathople = False
            elif not kiemtradieukiennhat(tenvatphamhientai):
                is_vatphamdangnhathople = False
            elif self._kiemtra_divaovungcam(*self.moitruong.get_toado(self._diachicosovatphamdangnhat)):
                is_vatphamdangnhathople = False
            elif time.time() - self._thoidiemthaydoivatphamdangnhatgannhat > 10:
                self._diachicosovatphamkhongnhat_map[self._diachicosovatphamdangnhat] = time.time()
                is_vatphamdangnhathople = False
        else:
            is_vatphamdangnhathople = False

        if not is_vatphamdangnhathople:
            self._diachicosovatphamdangnhat = False

            diachiduphong = self._diachicosovatphamnhatduphong
            if diachiduphong:
                if self.moitruong.get_is_vatphamtontai(diachiduphong):
                    tenvatphamduphong = self.moitruong.get_tendoituong(diachiduphong)
                    if self.moitruong.get_khoangcach(diachiduphong) < KHOANGCACHNHATDO and kiemtradieukiennhat(tenvatphamduphong) and not self._kiemtra_divaovungcam(*self.moitruong.get_toado(diachiduphong)):
                        self._diachicosovatphamdangnhat = diachiduphong
                        self._thoidiemthaydoivatphamdangnhatgannhat = time.time()
                self._diachicosovatphamnhatduphong = False

        danhsachvatpham = []
        # Lệnh nhặt xung quanh của game tự đi tới vật phẩm gần đó (không chọn được món nào), nên có món nằm trong vùng cấm ở gần thì không dùng lệnh này
        # Bản đồ có vùng cấm thì không dùng lệnh nhặt xung quanh, chỉ nhặt đích danh từng món
        is_covatphamvungcamgan = bool(VUNGCAM_MAP.get(self.moitruong.get_idbandohientai()))
        i = -1
        while True:
            i += 1
            diachivatpham = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachivatpham:
                break

            if not self.moitruong.get_is_vatphamtontai(diachivatpham):
                continue

            if time.time() - self._diachicosovatphamkhongnhat_map.get(diachivatpham, 0) < 60:
                continue

            tenvatpham = self.moitruong.get_tendoituong(diachivatpham)
            khoangcach = self.moitruong.get_khoangcach(diachivatpham)

            # Vật phẩm nằm trong vùng cấm (đi vào sẽ bị dịch chuyển sang bản đồ khác) thì bỏ qua, kể cả vật phẩm ưu tiên
            if self._kiemtra_divaovungcam(*self.moitruong.get_toado(diachivatpham)):
                if khoangcach <= 6.:
                    is_covatphamvungcamgan = True
                continue

            if kiemtradieukiennhat(tenvatpham) and khoangcach < KHOANGCACHNHATDO:
                danhsachvatpham.append((tenvatpham not in VATPHAMUUTIENNHATs, khoangcach, diachivatpham))

        if danhsachvatpham:
            # Vật phẩm ưu tiên lên đầu, sau đó mới xét gần nhất
            danhsachvatpham.sort(key = lambda x: (x[0], x[1]))
            diachigannhat = danhsachvatpham[0][2]

            if diachigannhat != self._diachicosovatphamdangnhat:
                self._diachicosovatphamdangnhat = diachigannhat
                self._thoidiemthaydoivatphamdangnhatgannhat = time.time()

            if len(danhsachvatpham) > 1:
                self._diachicosovatphamnhatduphong = danhsachvatpham[1][2]
            else:
                self._diachicosovatphamnhatduphong = False
        else:
            self._diachicosovatphamdangnhat = False
            self._diachicosovatphamnhatduphong = False

        # Nhặt đồ là thao tác click, làm ngắt kỹ năng vận khí
        is_dangvankhi = self.moitruong.get_is_dangvankhi()

        if self._diachicosovatphamdangnhat:
            khoangcach = self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat)
            is_vatphamuutien = self.moitruong.get_tendoituong(self._diachicosovatphamdangnhat) in VATPHAMUUTIENNHATs
            if khoangcach > 1.5:
                yeucaunhatvatphammoi = {
                    "yeucau": YEUCAUDICHUYENNHATDO,
                    "toadodich": (
                        *self.moitruong.get_toado(self._diachicosovatphamdangnhat, ),
                    ),
                    "khoangcachtoida": 0,
                    "is_uutien": is_vatphamuutien,
                }
            if khoangcach <= 3. and not is_dangvankhi:
                if self._is_tudongvebanrac and not is_vatphamuutien and not is_covatphamvungcamgan:
                    self.moitruong.action_nhatvatphamxungquanh(delay = 0.2)
                elif time.time() - self._thoidiemnhatvatphamgannhat_map.get(self._diachicosovatphamdangnhat, 0) > 0.2:
                    self.moitruong.action_nhatvatpham(self._diachicosovatphamdangnhat)
                    self._thoidiemnhatvatphamgannhat_map[self._diachicosovatphamdangnhat] = time.time()

        elif self._is_tudongvebanrac and not is_chinhatvatphamuutien and not is_dangvankhi and not is_covatphamvungcamgan:
            self.moitruong.action_nhatvatphamxungquanh(delay = 0.5)

        self._yeucaunhatvatpham = yeucaunhatvatphammoi

    def action_tudongdichuyentudo(self):
        yeucautudomoi = None

        if not self._is_tudongdichuyendiemdanhxungquanh:
            self._yeucautudo = None
            return

        if self._diachicosokhaikhoang:
            self._yeucautudo = None
            return

        # Đang trong quy trình về bán rác: không tự đi/phù lên bãi farm (trước đây vừa Hồi Thành Phù về tới thành,
        # đứng gần Tân Thủ Tiền Cơ là bị nói chuyện NPC phù thẳng lên map farm trước khi kịp bán)
        if self._trangthaiveban != 0:
            self._yeucautudo = None
            return

        while True:
            if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
                break

            diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            if diachimuctieu:
                if self.moitruong.get_is_nhanvattontai(diachimuctieu) and not self.moitruong.get_is_nhanvatdachet(diachimuctieu) and self.moitruong.get_is_cothetancong(diachimuctieu):
                    if self._yeucautudo is not None:
                        self.moitruong.action_ngatdichuyen()
                    break

            if self.moitruong.get_is_dangclickchuottrai(): break
            if self.moitruong.get_is_dangvankhi(): break
            if self.moitruong.get_is_nhanvatdachet(): break
            if self._idbandovuachet and self._is_tudongchaylenbandovuachet: break

            idbandohientai = self.moitruong.get_idbandohientai()

            # Chưa đặt điểm đánh mà bản đồ có lộ trình mẫu thì tự chọn mẫu chưa ai dùng
            if not self._diemdanhxungquanhs and idbandohientai != BANDO_CHIENTRUONG and time.time() - self._thoidiemkiemtralotrinhgannhat > 5.:
                self._thoidiemkiemtralotrinhgannhat = time.time()
                self.tuchon_lotrinhmau(idbandohientai)
            else:
                self._kiemtratrunglotrinh()

            diemdanhxungquanhs = self._diemdanhxungquanhs

            if not diemdanhxungquanhs:
                key_map = idbandohientai if idbandohientai != BANDO_CHIENTRUONG else "{}_{}".format(idbandohientai, self.moitruong.get_idphechientruong())
                diemdanhxungquanhs = DIEMDANHXUNGQUANH_MAP.get(key_map, [])

            if not diemdanhxungquanhs:
                if time.time() - self._thoidiemphatamlacmapgannhat > 5.0:
                    if self.moitruong.get_tenmonphai() == "maoson":
                        print("[AUTO-MOVE] Bản đồ không có trong cấu hình. Mao Sơn dùng Xuyên Không Hành bay lên.")
                        self.moitruong.action_ngatdichuyen()
                        self.moitruong.action_thucthicaulenh("pf 4182.2")
                        self._thoidiemphatamlacmapgannhat = time.time()
                    elif self._is_tudongvebanrac and self._diemdanhxungquanhs:
                        self.moitruong.action_ngatdichuyen()
                        self.action_sudunghoithanhphu()
                        self._thoidiemphatamlacmapgannhat = time.time()
                    else:
                        if not self._is_tudongdichientruong:
                            phatam("Chưa có điểm đánh")
                        self._thoidiemphatamlacmapgannhat = time.time()
                break

            if self._iddiemdanhxungquanhhientai == -1 or not self._diemdanhxungquanhhientai:
                best_index = 0
                min_dist = 999999.
                found_on_current_map = False

                for idx, point in enumerate(diemdanhxungquanhs):
                    p_map_id = point[2]

                    if p_map_id == idbandohientai:
                        dist = self.moitruong.get_khoangcachdiem(point[0], point[1])
                        if dist < min_dist:
                            min_dist = dist
                            best_index = idx
                            found_on_current_map = True

                if not found_on_current_map:
                    best_index = 0

                self._iddiemdanhxungquanhhientai = best_index
                self._diemdanhxungquanhhientai = diemdanhxungquanhs[best_index]
                self._thoidiembatdaudendiem = time.time()
                print(f"[Move] Bắt đầu lộ trình tại điểm #{best_index} (Map {self._diemdanhxungquanhhientai[2]})")

            canchuyendendiemtieptheo = False
            target_point = self._diemdanhxungquanhhientai
            target_map = target_point[2]

            if idbandohientai == target_map:
                dist_to_target = self.moitruong.get_khoangcachdiem(target_point[0], target_point[1])

                if dist_to_target <= 4.0:
                    canchuyendendiemtieptheo = True
                else:
                    if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                        if time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat() > 3.0:
                            if time.time() - self._thoidiembatdaudendiem > 10.0:
                                canchuyendendiemtieptheo = True
            else:
                if time.time() - self._thoidiembatdaudendiem > 90.0:
                    print("[Move] Quá thời gian chuyển map/đến điểm khác map -> Bỏ qua điểm này.")
                    canchuyendendiemtieptheo = True

            if canchuyendendiemtieptheo:
                next_index = (self._iddiemdanhxungquanhhientai + 1) % len(diemdanhxungquanhs)

                self._iddiemdanhxungquanhhientai = next_index
                self._diemdanhxungquanhhientai = diemdanhxungquanhs[next_index]
                self._thoidiembatdaudendiem = time.time()
                target_map = self._diemdanhxungquanhhientai[2]

            is_khacbando = idbandohientai != target_map

            if is_khacbando:
                self._thoidiemvohieuhoabatchucnangmoronggannhat = max(self._thoidiemvohieuhoabatchucnangmoronggannhat, time.time() + 1.)

            if is_khacbando and idbandohientai in (BANDO_TANTHUTHON, BANDO_CHU):
                diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = TANTHUTIENCO)

                if not diachinpc:
                    if idbandohientai == BANDO_TANTHUTHON:
                        yeucautudomoi = {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (148, 145, idbandohientai), "khoangcachtoida": 0}
                    elif idbandohientai == BANDO_CHU:
                        yeucautudomoi = {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (X_TANTHUTIENCO_CHU, Y_TANTHUTIENCO_CHU, idbandohientai), "khoangcachtoida": 0}
                else:
                    khoangcach = self.moitruong.get_khoangcach(diachinpc)
                    if khoangcach > 6.0:
                        x_npc, y_npc = self.moitruong.get_toado(diachinpc, )
                        yeucautudomoi = {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x_npc, y_npc, idbandohientai), "khoangcachtoida": 0}
                    else:
                        steps = DICHUYENTANTHUTIENCO_MAP.get(target_map)
                        if steps:
                            idnpc = self.moitruong.get_iddoituong(diachinpc)
                            hex_id = hex(idnpc).replace("0x", "")
                            print(f"[Move] Đang sử dụng {TANTHUTIENCO} để phù lên map {target_map}...")
                            for step in steps:
                                caulenh = f"tallk {hex_id}# {step}"
                                self.moitruong.action_thucthicaulenh(caulenh)
                                time.sleep(1.0)
                            if self.moitruong.get_is_danghiencuasotuychon():
                                self.moitruong.set_is_danghiencuasotuychon(False)
                        yeucautudomoi = None

                self._yeucautudo = yeucautudomoi
                break
            yeucautudomoi = {
                "yeucau": YEUCAUDICHUYENDICHUYENTUDO,
                "toadodich": self._diemdanhxungquanhhientai,
                "khoangcachtoida": 0
            }
            break

        self._yeucautudo = yeucautudomoi

    def get_is_dangtamngung(self):
        return time.time() < self._thoidiemhettamngung

    def action_kiemtraanthan(self):
        # 1) Tự quét: thấy người chơi lạ ẩn thân, hoặc (ở map train) thấy người ngoài danh sách tổ đội, thì ghi nhận
        #    và công bố cho các cửa sổ khác (qua shared_data)
        # 2) Đang farm & bán rác mà mình thấy, hoặc nhân vật khác CÙNG BẢN ĐỒ vừa thấy => ngưng hết mọi hoạt động
        #    (ẩn thân: THOIGIANTAMNGUNGANTHAN, người lạ: THOIGIANTAMNGUNGNGUOILA)
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemkiemtraanthangannhat < 0.5:
            return
        self._thoidiemkiemtraanthangannhat = thoidiemhientai

        phathien = self._quetnguoichoibatthuong()
        if phathien:
            # Chỉ công bố phát hiện trực tiếp (không công bố trạng thái tạm ngưng) để các nhân vật không gia hạn lẫn nhau mãi
            self._thoidiemphathienanthan = thoidiemhientai
            self._tenanthanphathien, self._thoigiantamngungphathien = phathien

        if not self._is_tudongvebanrac:
            return
        if phathien:
            self._batdautamngung(f"phát hiện {phathien[0]}", phathien[1])
            return
        phathienkhac = self._layanthantucuasokhac()
        if phathienkhac:
            self._batdautamngung(*phathienkhac)

    def _is_nguoichoinoibo(self, idnguoichoi, idnhanvathientai):
        # Nội bộ = chính mình + nhân vật trong danh sách tổ đội tự động; ai khác (kể cả cùng nhóm/cùng bang) đều là người lạ
        return idnguoichoi == idnhanvathientai or idnguoichoi in NHANVATTODOITUDONGs

    def _quetnguoichoibatthuong(self):
        # Trả về (mô tả, số giây tạm ngưng): ("X ẩn thân", THOIGIANTAMNGUNGANTHAN) / ("người lạ X", THOIGIANTAMNGUNGNGUOILA) hoặc None
        idnhanvathientai = self.moitruong.get_idnguoichoi()
        is_maptrain = self.moitruong.get_idbandohientai() not in BANDOKHONGPKs
        nguoila = None
        i = -1
        while True:
            i += 1
            diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituong:
                return nguoila
            # Bỏ các ô đối tượng còn sót (nhân vật đã rời đi / chưa tải xong) để không báo nhầm người lạ
            if not self.moitruong.get_is_nhanvattontai(diachidoituong) or not self.moitruong.get_is_nguoichoi(diachidoituong):
                continue
            idnguoichoi = self.moitruong.get_idnguoichoi(diachidoituong)
            if self._is_nguoichoinoibo(idnguoichoi, idnhanvathientai):
                continue
            if self.moitruong.get_khoangcach(diachidoituong) > KHOANGCACHTOANMANHINH:
                continue
            tendoituong = self.moitruong.get_tendoituong(diachidoituong) or str(idnguoichoi)
            if self.moitruong.get_is_nhanvatanthan(diachidoituong):
                # Ẩn thân luôn ưu tiên báo trước (thời gian tạm ngưng dài hơn)
                return f"{tendoituong} ẩn thân", THOIGIANTAMNGUNGANTHAN
            if is_maptrain and nguoila is None:
                nguoila = f"người lạ {tendoituong}", THOIGIANTAMNGUNGNGUOILA

    def _layanthantucuasokhac(self):
        # Nhân vật khác cùng bản đồ vừa tự phát hiện (trong vài giây gần đây) => (lý do, số giây) để tạm ngưng theo.
        # Có nhiều nguồn thì lấy nguồn có thời gian tạm ngưng dài nhất (ẩn thân trước người lạ)
        if self.shared_data is None:
            return None
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return None
        idbandohientai = self.moitruong.get_idbandohientai()
        ketqua = None
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict):
                continue
            if info.get("tenbando") != idbandohientai:
                continue
            if time.time() - info.get("_thoidiemphathienanthan", 0.) > THOIGIANCHIASEANTHAN:
                continue
            thoigian = info.get("_thoigiantamngungphathien") or THOIGIANTAMNGUNGANTHAN
            if ketqua is None or thoigian > ketqua[1]:
                ketqua = (f"{info.get('tennhanvat') or idcuaso} phát hiện {info.get('_tenanthanphathien') or 'người lạ'}", thoigian)
        return ketqua

    def _batdautamngung(self, lydo, thoigian = None):
        thoigian = thoigian or THOIGIANTAMNGUNGANTHAN
        is_moibatdau = not self.get_is_dangtamngung()
        # Chỉ kéo dài, không rút ngắn (đang ngưng 10 phút vì ẩn thân mà gặp người lạ thì vẫn giữ 10 phút)
        thoidiemhetmoi = time.time() + thoigian
        if is_moibatdau or thoidiemhetmoi >= self._thoidiemhettamngung:
            self._thoidiemhettamngung = thoidiemhetmoi
            self._lydotamngung = lydo
        if is_moibatdau:
            thoigianhienthi = f"{int(thoigian // 60)} phút" if thoigian >= 60 else f"{int(thoigian)} giây"
            print(f"[TẠM NGƯNG] {lydo} -> Ngưng mọi hoạt động {thoigianhienthi}")
            phatam("Phát hiện ẩn thân, tạm ngưng" if "ẩn thân" in lydo else "Phát hiện người lạ, tạm ngưng")
            self.moitruong.action_ngatdichuyen()
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            self._yeucautancong = None
            self._yeucaunhatvatpham = None
            self._yeucaugomquai = None
            self._yeucautudo = None
            self._is_battudongtancongvatly = False

    def tieptuchoatdong(self):
        # Bật lại thủ công: vẫn tiếp tục kiểm tra ẩn thân, gặp người ẩn thân là tạm ngưng tiếp
        self._thoidiemhettamngung = 0.
        self._lydotamngung = ""
        print("[TẠM NGƯNG] Bật lại hoạt động thủ công")
        phatam("Bật lại hoạt động")

    def nap_lotrinhmau(self, idbando, tenmau, is_nguocchieu = False, is_tuchon = False):
        mau = next((m for m in util_tailotrinhmau().get(str(idbando), []) if m.get("ten") == tenmau), None)
        if not mau or not mau.get("diem"):
            print(f"[LỘ TRÌNH] Không tìm thấy mẫu '{tenmau}' của bản đồ {idbando}")
            return False
        # Mỗi điểm là [x, y] (cùng bản đồ của mẫu) hoặc [x, y, id bản đồ] khi lộ trình đi qua bản đồ khác
        diemdanhs = [(int(d[0]), int(d[1]), int(d[2]) if len(d) >= 3 else int(idbando)) for d in mau["diem"]]
        if is_nguocchieu:
            diemdanhs.reverse()
        self._diemdanhxungquanhs = diemdanhs
        self._iddiemdanhxungquanhhientai = -1
        self._diemdanhxungquanhhientai = None
        self._lotrinhmaudangdung = f"{idbando}|{tenmau}|{1 if is_nguocchieu else 0}"
        self._is_lotrinhtuchon = is_tuchon
        print(f"[LỘ TRÌNH] Nạp mẫu '{tenmau}' bản đồ {idbando}{' (ngược chiều)' if is_nguocchieu else ''}: {len(diemdanhs)} điểm")
        phatam("Nạp lộ trình mẫu")
        return True

    def luu_lotrinhmau(self, tenmau):
        tenmau = (tenmau or "").replace("|", " ").strip()
        if not tenmau or not self._diemdanhxungquanhs:
            return False
        # Lộ trình gắn với bản đồ chiếm đa số điểm trong danh sách
        demtheobando = {}
        for diem in self._diemdanhxungquanhs:
            demtheobando[diem[2]] = demtheobando.get(diem[2], 0) + 1
        idbando = max(demtheobando, key = demtheobando.get)
        lotrinhmau = util_tailotrinhmau()
        dsmau = [m for m in lotrinhmau.get(str(idbando), []) if m.get("ten") != tenmau]
        dsmau.append({"ten": tenmau, "diem": [[d[0], d[1]] if d[2] == idbando else [d[0], d[1], d[2]] for d in self._diemdanhxungquanhs]})
        lotrinhmau[str(idbando)] = dsmau
        util_luulotrinhmau(lotrinhmau)
        self._lotrinhmaudangdung = f"{idbando}|{tenmau}|0"
        self._is_lotrinhtuchon = False
        print(f"[LỘ TRÌNH] Đã lưu mẫu '{tenmau}' cho bản đồ {idbando}")
        phatam("Lưu lộ trình mẫu")
        return True

    def _laylotrinhcuasokhac(self, idbando):
        # {(tên mẫu, ngược chiều): [id cửa sổ, ...]} của các cửa sổ khác đang dùng mẫu trên cùng bản đồ
        dangdung = {}
        if self.shared_data is None:
            return dangdung
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return dangdung
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict):
                continue
            phan = (info.get("_lotrinhmaudangdung") or "").split("|")
            if len(phan) == 3 and phan[0] == str(idbando):
                dangdung.setdefault((phan[1], phan[2] == "1"), []).append(idcuaso)
        return dangdung

    def tuchon_lotrinhmau(self, idbando = None):
        # Chọn mẫu ít nhân vật khác dùng nhất trên cùng bản đồ; mẫu nào cũng có người dùng thì đi ngược chiều để không bám đuôi nhau
        idbando = idbando or self.moitruong.get_idbandohientai()
        dsmau = [m["ten"] for m in util_tailotrinhmau().get(str(idbando), []) if m.get("diem")]
        if not dsmau:
            return False
        dangdung = self._laylotrinhcuasokhac(idbando)
        def doban(luachon):
            tenmau, is_nguocchieu = luachon
            tong = len(dangdung.get((tenmau, False), [])) + len(dangdung.get((tenmau, True), []))
            return tong, len(dangdung.get(luachon, [])), is_nguocchieu
        luachon = min(((tenmau, is_nguocchieu) for tenmau in dsmau for is_nguocchieu in (False, True)), key = doban)
        return self.nap_lotrinhmau(idbando, *luachon, is_tuchon = True)

    def _kiemtratrunglotrinh(self):
        # Hai nhân vật tự chọn cùng lúc có thể trùng mẫu: cửa sổ có id lớn hơn tự chọn lại
        if not self._is_lotrinhtuchon or time.time() - self._thoidiemkiemtralotrinhgannhat < 10.:
            return
        self._thoidiemkiemtralotrinhgannhat = time.time()
        phan = self._lotrinhmaudangdung.split("|")
        if len(phan) != 3:
            return
        cuasotrung = self._laylotrinhcuasokhac(phan[0]).get((phan[1], phan[2] == "1"), [])
        if any(idcuaso < self.idcuaso for idcuaso in cuasotrung):
            print(f"[LỘ TRÌNH] Trùng mẫu '{phan[1]}' với nhân vật khác -> Chọn lại")
            self.tuchon_lotrinhmau(int(phan[0]))

    def them_diemdanhxungquanh(self, diemdanhxungquanh):
        if diemdanhxungquanh and diemdanhxungquanh not in self._diemdanhxungquanhs:
            self._diemdanhxungquanhs.append(diemdanhxungquanh)
            self._lotrinhmaudangdung = ""
            self._is_lotrinhtuchon = False
            print(self._diemdanhxungquanhs)
            phatam("Thêm điểm đánh xung quanh. Tổng cộng {}".format(len(self._diemdanhxungquanhs)))

    def botoanbo_diemdanhxungquanh(self):
        self._diemdanhxungquanhs.clear()
        self._iddiemdanhxungquanhhientai = -1
        self._diemdanhxungquanhhientai = None
        self._lotrinhmaudangdung = ""
        self._is_lotrinhtuchon = False
        phatam("Bỏ toàn bộ điểm đánh xung quanh")

    def thietlap_chidanhnguoichoi(self, is_chidanhnguoichoi):
        self._is_chidanhnguoichoi = is_chidanhnguoichoi
        if not is_chidanhnguoichoi:
            phatam("Bỏ thiết lập chỉ đánh người chơi")
        else:
            phatam("Thiết lập chỉ đánh người chơi")

    def action_tudongtodoi(self):
        if not self._is_tudongtodoi:
            return

        # Quét người chơi xung quanh khá tốn (đọc bộ nhớ toàn bộ đối tượng), thao tác nhóm cũng có delay riêng nên không cần chạy liên tục
        if time.time() - self._thoidiemxulytodoigannhat < 0.5:
            return
        self._thoidiemxulytodoigannhat = time.time()

        idnguoichoi = self.moitruong.get_idnguoichoi()
        tenmonphai = self.moitruong.get_tenmonphai()
        is_dangtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        idbandohientai = self.moitruong.get_idbandohientai()

        danhsachuutientodoi = None
        for thanhvientodoitudongs in NHANVATTODOITUDONGs_LIST:
            if idnguoichoi in thanhvientodoitudongs:
                danhsachuutientodoi = list(thanhvientodoitudongs)
                break

        if not danhsachuutientodoi:
            return

        if tenmonphai in ("vanmongcoc", "thucson") and self._is_chedobufftoanbang and idbandohientai in BANDOKHONGPKs:
            if is_dangtrongnhom:
                if self.moitruong.get_is_truongnhom() or (self._is_khongcongidebuff and time.time() - self._thoidiemkiemtrakhongcongidebuffgannhat > 10.):
                    self._thoidiemkiemtrakhongcongidebuffgannhat = time.time()
                    # Trưởng nhóm rời nhóm = giải tán (đá văng cả đội): nhường quyền cho thành viên khác trước, lần sau mới rời
                    thanhvienkhacs = [id_ for id_ in self.moitruong.get_danhsachidnguoichoithanhviennhoms() if id_ != idnguoichoi]
                    if self.moitruong.get_is_truongnhom() and thanhvienkhacs:
                        self.moitruong.action_nhuongquyentruongnhom(thanhvienkhacs[0])
                    else:
                        self.moitruong.action_thoatkhoinhom()
            else:
                self.moitruong.action_kiemtravadongyloimoinhom(NHANVATCUNGBANGs)
            return

        if idbandohientai == BANDO_CHIENTRUONG and not is_dangtrongnhom:
            self.moitruong.action_kiemtravadongyloimoinhom(NHANVATCUNGBANGs)

        # Thứ hạng: số nhỏ = ưu tiên làm trưởng nhóm cao hơn
        xephang_map = {id_: i for i, id_ in enumerate(danhsachuutientodoi)}
        xephangcuatoi = xephang_map[idnguoichoi]

        danhsachthanhviens = self.moitruong.get_danhsachidnguoichoithanhviennhoms() if is_dangtrongnhom else []
        danhsachxungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()

        # Loại chính mình và trùng lặp
        dongdoicanxulys = []
        for id_ in danhsachxungquanhs:
            if id_ != idnguoichoi and id_ in xephang_map and id_ not in dongdoicanxulys:
                dongdoicanxulys.append(id_)

        if not dongdoicanxulys and not is_dangtrongnhom:
            return

        # Tuyệt đối hạn chế rời/giải tán nhóm (giải tán sẽ đá văng cả đội ra khỏi phó bản): ưu tiên mời rồi nhường quyền.
        # Trưởng nhóm là người ngoài danh sách tổ đội thì cứ ở lại nhóm, không rời để ghép lại như trước.

        idnguoichoixephangcaonhat = min(dongdoicanxulys + [idnguoichoi], key = lambda id_: xephang_map[id_])

        if is_dangtrongnhom and self.moitruong.get_is_truongnhom():
            for thanhvien_id in danhsachthanhviens:
                if xephang_map.get(thanhvien_id, len(xephang_map)) < xephangcuatoi:
                    self.moitruong.action_nhuongquyentruongnhom(thanhvien_id)
                    return

            # Đồng đội hạng cao hơn ở gần nhưng chưa trong nhóm: MỜI vào (vào rồi sẽ được nhường quyền ở vòng sau).
            # Chỉ khi nhóm chỉ có mình mình (rời không đá ai) và mời quá 15s không được (họ đang ở nhóm khác) mới rời để xin vào nhóm họ.
            if idnguoichoixephangcaonhat != idnguoichoi and idnguoichoixephangcaonhat not in danhsachthanhviens:
                if self._idmoihangcaohon != idnguoichoixephangcaonhat:
                    self._idmoihangcaohon = idnguoichoixephangcaonhat
                    self._thoidiembatdaumoihangcaohon = time.time()
                if len(danhsachthanhviens) <= 1 and time.time() - self._thoidiembatdaumoihangcaohon > 15.:
                    self._idmoihangcaohon = 0
                    self.moitruong.action_thoatkhoinhom()
                    return
            else:
                self._idmoihangcaohon = 0

            if len(danhsachthanhviens) < SOLUONGTHANHVIENNHOMTOIDA:
                for iddongdoi in dongdoicanxulys:
                    if iddongdoi in danhsachthanhviens:
                        continue
                    if time.time() - self._thoidiemtodoigannhat_map.get(iddongdoi, 0) > 5.0:
                        self.moitruong.action_moihoacxinvaonhom(iddongdoi)
                        self._thoidiemtodoigannhat_map[iddongdoi] = time.time()
                        break

        elif not is_dangtrongnhom:
            self.moitruong.action_kiemtravadongyloimoinhom(danhsachuutientodoi)

            if idnguoichoixephangcaonhat != idnguoichoi:
                if time.time() - self._thoidiemtodoigannhat_map.get(idnguoichoixephangcaonhat, 0) > 5.0:
                    self.moitruong.action_moihoacxinvaonhom(idnguoichoixephangcaonhat)
                    self._thoidiemtodoigannhat_map[idnguoichoixephangcaonhat] = time.time()

    def action_tudongphucsinh(self):
        if self._is_tudongphucsinh:
            if self.moitruong.get_is_nhanvatdachet():
                dfgdfb = 1
                while dfgdfb <= 30:
                    if self.moitruong.get_is_nhanvatdachet():
                        time.sleep(1.)
                    else:
                        return
                    dfgdfb += 1
                if self.moitruong.action_phucsinh():
                    self._xoatrangthaisaukhichet()

    def action_tudongdoimaupk(self):
        if self._is_tudongdoimaupk and self.moitruong.get_idbandohientai() not in BANDOFARMs:
            if time.time() - self._thoidiemdoimaupkgannhat > 5.:
                self._thoidiemdoimaupkgannhat = time.time()
                self.action_batpk()

    def action_batpk(self):
        return
        self.moitruong.action_doimaupk(MAUPK_BANG)

    def action_tatpk(self):
        self.moitruong.action_doimaupk(MAUPK_HOABINH)

    def action_tudongmuavatpham(self, delay = 3.):
        if self._is_tudongmuavatpham:
            if time.time() - self._thoidiemkiemtranpcmuavatphamgannhat < delay:
                return
            if self.moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                return

            self._thoidiemkiemtranpcmuavatphamgannhat = time.time()

            diachicosothongtinnhanvatchutiemtaphoa = self.moitruong.action_timkiemnhanvat(CHUTIEMTAPHOA)

            if diachicosothongtinnhanvatchutiemtaphoa and self.moitruong.get_khoangcach(diachicosothongtinnhanvatchutiemtaphoa) <= 12.0:
                idnpc = self.moitruong.get_iddoituong(diachicosothongtinnhanvatchutiemtaphoa)
                vitrihoithanhphu = self.moitruong.action_timkiemvitrivatphamhanhtrang(HOITHANHPHU)
                soluonghoithanhphu = self.moitruong.get_soluongvatphamhanhtrang(vitrihoithanhphu) if vitrihoithanhphu is not False else 0
            #
            #     if soluonghoithanhphu < 30:
            #         caulenh = "buy {}# 2 {} 1500".format(hex(idnpc).replace("0x", ""), 30 - soluonghoithanhphu)
            #         self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)
            #
                if self.moitruong.get_tenmonphai() == "vanmongcoc":
                    vitritranky = self.moitruong.action_timkiemvitrivatphamhanhtrang(TRANKY)
                    soluongtranky = self.moitruong.get_soluongvatphamhanhtrang(vitritranky) if vitritranky is not False else 0

                    if soluongtranky < 999:
                        caulenh = "buy {}# 6 {} 60".format(hex(idnpc).replace("0x", ""), 999 - soluongtranky)
                        self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

                    vitridaunanh = self.moitruong.action_timkiemvitrivatphamhanhtrang(DAUNANH)
                    soluongdaunanh = self.moitruong.get_soluongvatphamhanhtrang(vitridaunanh) if vitridaunanh is not False else 0

                    if soluongdaunanh < 30:
                        caulenh = "buy {}# 7 {} 400".format(hex(idnpc).replace("0x", ""), 30 - soluongdaunanh)
                        self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

                if self.moitruong.get_tenmonphai() == "maoson":
                    vitribuagiay = self.moitruong.action_timkiemvitrivatphamhanhtrang(BUAGIAY)
                    soluongbuagiay = self.moitruong.get_soluongvatphamhanhtrang(vitribuagiay) if vitribuagiay is not False else 0

                    if soluongbuagiay < 999:
                        caulenh = "buy {}# 1 {} 10".format(hex(idnpc).replace("0x", ""), 999 - soluongbuagiay)
                        self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

                if self._is_tudongtrieuhoibaothugiangho:
                    vitribaothuthucpham = self.moitruong.action_timkiemvitrivatphamhanhtrang(CAOCAPBAOTHUTHUCPHAM)
                    soluongbaothuthucpham = self.moitruong.get_soluongvatphamhanhtrang(vitribaothuthucpham) if vitribaothuthucpham is not False else 0

                    if soluongbaothuthucpham < 30:
                        caulenh = "buy {}# 18 {} 400".format(hex(idnpc).replace("0x", ""), 30 - soluongbaothuthucpham)
                        self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

            diachicosothongtinnhanvatchutuulau = self.moitruong.action_timkiemnhanvat(CHUTUULAU)

            if diachicosothongtinnhanvatchutuulau and self.moitruong.get_khoangcach(diachicosothongtinnhanvatchutuulau) <= 12.0:
                idnpc = self.moitruong.get_iddoituong(diachicosothongtinnhanvatchutuulau)

                if self._is_tudongtrieuhoibaothugiangho:
                    vitrilaotuu = self.moitruong.action_timkiemvitrivatphamhanhtrang(LAOTUU)
                    soluonglaotuu = self.moitruong.get_soluongvatphamhanhtrang(vitrilaotuu) if vitrilaotuu is not False else 0

                    if soluonglaotuu < 30:
                        caulenh = "buy {}# 3 {} 1150".format(hex(idnpc).replace("0x", ""), 30 - soluonglaotuu)
                        self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

                    vitriduahau = self.moitruong.action_timkiemvitrivatphamhanhtrang(DUAHAU)
                    soluongduahau = self.moitruong.get_soluongvatphamhanhtrang(vitriduahau) if vitriduahau is not False else 0

                    if soluongduahau < 30:
                        caulenh = "buy {}# 4 {} 1100".format(hex(idnpc).replace("0x", ""), 30 - soluongduahau)
                        self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)

    def action_tudongsuavatpham(self, delay = 3.):
        if self._is_tudongsuavatpham:
            if time.time() - self._thoidiemkiemtranpcsuavatphamgannhat < delay:
                return
            self._thoidiemkiemtranpcsuavatphamgannhat = time.time()

            diachicosothongtinnhanvatchutiemsuachua = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)

            if diachicosothongtinnhanvatchutiemsuachua and self.moitruong.get_khoangcach(diachicosothongtinnhanvatchutiemsuachua) <= 12.0:
                self.moitruong.action_suavatpham(diachicosothongtinnhanvatchutiemsuachua)

    def action_suavatpham(self):
        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        thoidiembatdau = time.time()
        thoigiantoida = 30.0

        while True:
            if time.time() - thoidiembatdau > thoigiantoida:
                print(f"[Auto-SuaDo] Quá {thoigiantoida}s không tìm thấy Chủ Tiệm Sửa Chữa. Hủy bỏ.")
                break

            diachinpc = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)

            if diachinpc:
                khoangcach = self.moitruong.get_khoangcach(diachinpc)
                if khoangcach <= 9.0:
                    print("[Auto-SuaDo] Đã tìm thấy NPC, đang sửa đồ...")
                    self.moitruong.action_suavatpham(diachinpc)
                    return

            if self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
                if not diachinpc:
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(111, 157, khoangcachtoida = 3.)
                else:
                    self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 3.)

            self._thoidiemsudunghoithanhphugannhat = time.time()

            time.sleep(1.0)

    def action_sudungvatphamhanhtrang(self, tenvatpham, is_boquaxacnhan = False, delay = 0.25):
        if time.time() - self._thoidiemsudungvatphamgannhat < delay:
            return False

        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(tenvatpham)

        if not iddoituongvatpham:
            return False

        print("{}: sử dụng vật phẩm: {}".format(self.moitruong.get_tendoituong(), tenvatpham))

        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham, is_boquaxacnhan, delay = delay)
        if is_ok:
            self._thoidiemsudungvatphamgannhat = time.time()

        return is_ok

    def action_tudongxepchongvatpham(self, delay = 0.5):
        if self._is_tudongxepchongvatpham and VATPHAMXEPCHONGs:
            while True:
                if time.time() - self._thoidiemxepchongvatphamgannhat < delay:
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
                    vitrivatphamcanxepchongs = [vitrivatpham for vitrivatpham in vitrivatphams if self.moitruong.get_soluongvatphamhanhtrang(vitrivatpham[0]) < SOLUONGXEPCHONGTOIDA_MAP.get(tenvatpham, 30)]

                    if len(vitrivatphamcanxepchongs) <= 1:
                        continue

                    for vitrivatpham in vitrivatphamcanxepchongs[1:]:
                        if vitrivatpham[0] // 24 != vitrivatphamcanxepchongs[0][0] // 24:
                            is_ok = self.moitruong.action_dichuyenvatphamsanghanhtrangkhac(vitrivatpham[1], vitrivatphamcanxepchongs[0][0] // 24 + 1, delay = delay)
                        else:
                            is_ok = self.moitruong.action_dichuyenvatphamhanhtrang(vitrivatpham[1], vitrivatphamcanxepchongs[0][0] + 1, delay = delay)
                        if is_ok:
                            self._thoidiemxepchongvatphamgannhat = time.time()
                break

    def action_chantangcapdo(self):
        if self._is_chantangcapdo:
            self.moitruong.action_chantangcapdo()
        else:
            self.moitruong.action_bochantangcapdo()

    def action_tudongtrieuhoibaothugiangho(self):
        if self._is_tudongtrieuhoibaothugiangho:
            while True:
                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                iddoituongbaothugiangho = self.moitruong.get_iddoituongbaothugiangho()

                if not iddoituongbaothugiangho:
                    break

                if time.time() - self._thoidiemsudungthucanbaothugannhat > 2. and self.moitruong.get_dotrungthanhbaothugiangho() <= 80:
                    iddoituongcaocapbaothuthucpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPBAOTHUTHUCPHAM)
                    if iddoituongcaocapbaothuthucpham:
                        if self.moitruong.action_sudungvatphambaothu(iddoituongcaocapbaothuthucpham, iddoituongbaothugiangho, delay = 0.0):
                            self._thoidiemsudungthucanbaothugannhat = time.time()

                if not self.moitruong.get_is_datrieuhoibaothugiangho() and self.moitruong.get_idbandohientai() in BANDOKHONGPKs and time.time() - self._thoidiemtudongtrieuhoibaothugiangho > 1. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM and time.time() - self._thoidiemtamngungdichuyensudungkynang > 0.:
                    if self.moitruong.action_trieuhoibaothu(iddoituongbaothugiangho, delay = 0.0):
                        self._thoidiemtudongtrieuhoibaothugiangho = time.time()

                break

    def action_tudongdieukhienbaothu(self):
        is_baothukynangtrieuhoihetnoiluc = False
        is_baothukynangtrieuhoihetsinhluc = False
        if self._is_tudongdieukhienbaothu:
            while True:
                if self.moitruong.get_is_nhanvatdachet():
                    break

                idbandohientai = self.moitruong.get_idbandohientai()
                soluongbaothutoida = 3

                for sothutu in range(1, soluongbaothutoida + 1):
                    iddoituongbaothu = self.moitruong.get_iddoituongbaothu(sothutu)

                    if not iddoituongbaothu:
                        continue

                    tendoituongbaothu = self.moitruong.get_tendoituongbaothu(sothutu) or ""
                    is_baothukynangtrieuhoi = "(" in tendoituongbaothu and ")" in tendoituongbaothu
                    is_baothugiangho = not is_baothukynangtrieuhoi

                    toadodoituongbaothu = self.moitruong.get_toadodoituongbaothu(sothutu)
                    idbandohientaidoituongbaothu = self.moitruong.get_idbandohientaidoituongbaothu(sothutu)

                    khoangcach = self.moitruong.get_khoangcachdiem(*toadodoituongbaothu)

                    is_baothudangogan = idbandohientaidoituongbaothu == idbandohientai and khoangcach <= KHOANGCACHTOANMANHINH

                    if is_baothukynangtrieuhoi:
                        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                        is_baothukynangtrieuhoihetnoiluc = self.moitruong.get_phantramnoilucconlaidoituongbaothukynangtrieuhoi(sothutu) < 50
                        is_baothukynangtrieuhoihetsinhluc = self.moitruong.get_phantramsinhlucconlaidoituongbaothukynangtrieuhoi(sothutu) < 50

                        if self._is_danggomquai:
                            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu)
                        elif diachimuctieu:
                            if self.moitruong.get_is_cothetancong(diachimuctieu):
                                iddoituongnhanvatmuctieu = self.moitruong.get_iddoituong(diachimuctieu)
                                if iddoituongnhanvatmuctieu:
                                    self.moitruong.action_ralenhbaothutancong(iddoituongbaothu, iddoituongnhanvatmuctieu)

                    elif is_baothugiangho:
                        if self.moitruong.get_idbandohientai() in BANDOKHONGPKs and self.moitruong.get_trangthaihanhvidoituongbaothu(sothutu) != 3:
                            self.moitruong.action_ralenhbaothudungim(iddoituongbaothu, delay = 0.)
                        elif self._is_tudongsudungkynangbaothu:
                            idkynangbaothu_map = {self.moitruong.get_idkynangbaothugiangho(i): i for i in range(11)}
                            idkynangbaothucothesudungs = {KYNANGBAOTHU_CAOCAPTHIENCAN, }
                            if set(idkynangbaothu_map.keys()) & idkynangbaothucothesudungs:
                                if time.time() - self._thoidiemhoiphucbaothugannhat > 5.:
                                    if self.moitruong.get_noilucconlaibaothugiangho() <= 120:
                                        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(LAOTUU)
                                        if iddoituongvatpham:
                                            if self.moitruong.action_sudungvatphambaothu(iddoituongvatpham, iddoituongbaothu):
                                                self._thoidiemhoiphucbaothugannhat = time.time()
                                        else:
                                            phatam("Hết lão tửu")
                                            self._thoidiemhoiphucbaothugannhat = time.time()

                                    if self.moitruong.get_sinhluctoidabaothugiangho() - self.moitruong.get_sinhlucconlaibaothugiangho() >= 1200:
                                        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(DUAHAU)
                                        if iddoituongvatpham:
                                            if self.moitruong.action_sudungvatphambaothu(iddoituongvatpham, iddoituongbaothu):
                                                self._thoidiemhoiphucbaothugannhat = time.time()

                                diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                                if diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu) and self.moitruong.get_noilucconlaibaothugiangho() >= 60:
                                    if KYNANGBAOTHU_CAOCAPTHIENCAN in idkynangbaothu_map and self.moitruong.get_is_kynangbaothugianghosansang(idkynangbaothu_map[KYNANGBAOTHU_CAOCAPTHIENCAN]) and self.moitruong.get_is_cothegaychoang(diachimuctieu):
                                        if not is_baothudangogan and time.time() - self._thoidiemsudungthaotacbaothugannhat > 0.25:
                                            self._thoidiemsudungthaotacbaothugannhat = time.time()
                                            self.moitruong.action_ralenhbaothutheosau(iddoituongbaothu, delay = 0.)
                                        elif is_baothudangogan:
                                            self.moitruong.action_sudungkynangbaothu(KYNANGBAOTHU_CAOCAPTHIENCAN, diachimuctieu)
                break
        self._is_baothukynangtrieuhoihetnoiluc = is_baothukynangtrieuhoihetnoiluc
        self._is_baothukynangtrieuhoihetsinhluc = is_baothukynangtrieuhoihetsinhluc

    def action_tudongbanrac(self):
        diachi_npc = self.moitruong.action_timkiemnhanvat(CHUTIEMTAPHOA)
        if not diachi_npc:
            diachi_npc = self.moitruong.action_timkiemnhanvat(CHUTIEMTAPHOA)
            if not diachi_npc:
                return

        khoangcach = self.moitruong.get_khoangcach(diachi_npc)
        if khoangcach > 3.0:
            return

        idnpc = self.moitruong.get_iddoituong(diachi_npc)
        if not idnpc or idnpc <= 0:
            return

        sovatphamdaban = 0
        soluongvatphamhanhtrangtoida = self.moitruong.get_soluongvatphamhanhtrangtoida()
        for i in range(6, soluongvatphamhanhtrangtoida):
            iddoituongvatphamhanhtrang = self.moitruong.get_iddoituongvatphamhanhtrang(i)

            tenvatphamhanhtrang = self.moitruong.get_tenvatphamhanhtrang(i)
            if iddoituongvatphamhanhtrang and iddoituongvatphamhanhtrang > 0 and tenvatphamhanhtrang not in VATPHAMKHONGBANs and "Bí kíp" not in tenvatphamhanhtrang and "Nhập môn" not in tenvatphamhanhtrang and "Bảo Thạch" not in tenvatphamhanhtrang and "Ngọc Thạch" not in tenvatphamhanhtrang and "cấp" not in tenvatphamhanhtrang and "Tàng Đồ" not in tenvatphamhanhtrang and "Phục Dược" not in tenvatphamhanhtrang and "Trị Dược" not in tenvatphamhanhtrang:
                caulenh = "sell ! {}# {}# 30".format(hex(idnpc).replace("0x", ""), hex(iddoituongvatphamhanhtrang).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_THAP)
                sovatphamdaban += 1
                time.sleep(1.)

    def _tinhkhoangcachdendoanthang(self, px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.dist((px, py), (x1, y1))

        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)

        t = max(0, min(1, t))

        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy

        return math.dist((px, py), (nearest_x, nearest_y))

    def _kiemtraketgomquai(self, idmuctieu, khoangcach):
        # Quái sau tường: đường chim bay thì gần nhưng chạy mãi không lại gần hơn. Trả về True nếu bị kẹt.
        thoidiemhientai = time.time()
        # Đang bận việc khác (nhặt đồ ưu tiên, đứng im dùng skill) thì không tính là kẹt
        is_dangbanviec = self._is_danguutiennhatdo or thoidiemhientai - self._thoidiemtamngungdichuyensudungkynang < 0.
        if idmuctieu != self._idgomtheodoiket or is_dangbanviec or khoangcach < self._khoangcachgomtotnhat - 0.5:
            self._idgomtheodoiket = idmuctieu
            self._khoangcachgomtotnhat = khoangcach
            self._thoidiemgomcaithiengannhat = thoidiemhientai
            return False
        return thoidiemhientai - self._thoidiemgomcaithiengannhat > 2.5

    def _boquaquaibichan(self, idquai):
        print(f"[GOM] Quái {hex(idquai)} bị chặn (tường/vật cản) -> Bỏ qua 120s")
        self._idmuctieubiloi_map[idquai] = time.time()
        self._danhsachidquaidagom.discard(idquai)
        if self._idquaidautien == idquai:
            self._idquaidautien = 0
        if self._idquaidangkeo == idquai:
            self._idquaidangkeo = 0
        self._idgomtheodoiket = 0
        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if diachimuctieudangchon and self.moitruong.get_iddoituong(diachimuctieudangchon) == idquai:
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

    def _laytoadodongdoikhacnhom(self):
        # Nhân vật của mình (NHANVATTODOITUDONGs) đang ở gần nhưng không cùng nhóm => đang farm riêng, tránh giành quái của nhau
        idnhanvathientai = self.moitruong.get_idnguoichoi()
        idthanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms() if self.moitruong.get_is_dangnamtrongnhom() else []
        toadodongdois = []
        i = -1
        while True:
            i += 1
            diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituong:
                break
            if not self.moitruong.get_is_nhanvattontai(diachidoituong) or not self.moitruong.get_is_nguoichoi(diachidoituong):
                continue
            idnguoichoi = self.moitruong.get_idnguoichoi(diachidoituong)
            if idnguoichoi in NHANVATTODOITUDONGs and idnguoichoi != idnhanvathientai and idnguoichoi not in idthanhviennhoms:
                toadodongdois.append(self.moitruong.get_toado(diachidoituong))
        return toadodongdois

    def action_tudongxulygomquai(self):
        yeucaugomquaimoi = None

        if not self._is_tudonggomquai or not self._is_tudongsudungkynang:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            self._danhsachidquaidagom.clear()
            self._idquaidautien = 0
            return

        idbandohientai = self.moitruong.get_idbandohientai()

        if self._is_tudongvebanrac and self._diemdanhxungquanhs:
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if danhsachbandohople and idbandohientai not in danhsachbandohople:
                self._is_danggomquai = False
                self._yeucaugomquai = None
                self._idquaidangkeo = 0
                self._danhsachidquaidagom.clear()
                self._idquaidautien = 0
                return

        if idbandohientai in BANDOKHONGPKs:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            return

        if time.time() - self._thoidiemloggomquai > 1.5:
            self._thoidiemloggomquai = time.time()
        is_canghilog = False
        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_dangvankhi() or idbandohientai in BANDOKHONGPKs:
            self._yeucaugomquai = None
            return

        if len(self._danhsachidquaidagom) == 0:
            self._idquaidautien = 0

        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if diachimuctieudangchon:
            if self.moitruong.get_is_nguoichoi(diachimuctieudangchon) or self.moitruong.get_is_baothukynangtrieuhoi(diachimuctieudangchon) or self.moitruong.get_is_baothugiangho(diachimuctieudangchon):
                self._is_danggomquai = False
                self._yeucaugomquai = None
                self._idquaidangkeo = 0
                self._danhsachidquaidagom.clear()
                self._idquaidautien = 0
                return

        diachiquaidautien = 0
        khoangcachneohientai = 0.0

        if self._idquaidautien > 0:
            diachiquaidautien = self.moitruong.action_timkiemnhanvat(iddoituong = self._idquaidautien)

            if not diachiquaidautien or self.moitruong.get_is_nhanvatdachet(diachiquaidautien):
                if is_canghilog: print(f"[GOM] Neo {hex(self._idquaidautien)} chết/mất -> Xóa")
                if self._idquaidautien in self._danhsachidquaidagom:
                    self._danhsachidquaidagom.remove(self._idquaidautien)
                self._idquaidautien = 0
                diachiquaidautien = 0
            else:
                khoangcachneohientai = self.moitruong.get_khoangcach(diachiquaidautien)
                if khoangcachneohientai > 18.0:
                    if is_canghilog: print(f"[GOM] Neo rớt quá xa (>18m) -> Reset Neo")
                    self._idquaidautien = 0
                    diachiquaidautien = 0
                    khoangcachneohientai = 0.0

        if self._idquaidautien == 0 and len(self._danhsachidquaidagom) > 0:
            idungvien = 0
            khoangcachungviennhonhat = 9999.
            diachiungvien = 0

            for id_mob in list(self._danhsachidquaidagom):
                addr_mob = self.moitruong.action_timkiemnhanvat(iddoituong = id_mob)
                if addr_mob and not self.moitruong.get_is_nhanvatdachet(addr_mob):
                    kc = self.moitruong.get_khoangcach(addr_mob)
                    if kc < khoangcachungviennhonhat:
                        khoangcachungviennhonhat = kc
                        idungvien = id_mob
                        diachiungvien = addr_mob
                else:
                    self._danhsachidquaidagom.remove(id_mob)

            if idungvien != 0:
                self._idquaidautien = idungvien
                diachiquaidautien = diachiungvien
                khoangcachneohientai = khoangcachungviennhonhat
                if is_canghilog: print(f"[GOM] Bầu Neo mới: {hex(idungvien)} (KC: {round(khoangcachungviennhonhat, 1)}m)")

        i = -1
        soluongquaigan = 0

        idquaicankeogannhat = 0
        khoangcachquaicankeo = 9999.
        diachicosoquaicankeo = 0

        is_coquaixungquanh = False

        idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if time.time() - v > 120.0]
        for k in idcanxoas:
            del self._idmuctieubiloi_map[k]

        is_neobirotlai = (diachiquaidautien and khoangcachneohientai > 12.0)

        # Chỉ khi bật farm & bán rác: quái gần nhân vật khác trong danh sách tổ đội tự động (không cùng nhóm) hơn mình thì nhường.
        # Không bật farm & bán rác thì không nhường gì cả.
        toadobanthan = self.moitruong.get_toado()
        toadodongdois = self._laytoadodongdoikhacnhom() if self._is_tudongvebanrac else []

        while True:
            i += 1
            diachidoituongxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituongxemxet: break

            if not self.moitruong.get_is_cothetancong(diachidoituongxemxet): continue
            if self.moitruong.get_idloainhanvat(diachidoituongxemxet) != LOAIMUCTIEU_QUAIVATHOACNPC: continue

            tendoituongxemxet = self.moitruong.get_tendoituong(diachidoituongxemxet)
            if tendoituongxemxet in self._tenmuctieukhongtancongs:
                continue
            if self._tenmuctieutancongs and tendoituongxemxet not in self._tenmuctieutancongs:
                continue

            toadoquai = self.moitruong.get_toado(diachidoituongxemxet)
            if self._kiemtra_divaovungcam(*toadoquai):
                continue
            if not self._kiemtra_tamdiemdanh(*toadoquai):
                continue

            iddoituongquai = self.moitruong.get_iddoituong(diachidoituongxemxet)

            if toadodongdois:
                khoangcachtoiquai = math.dist(toadoquai, toadobanthan)
                if any(math.dist(toadoquai, toadodongdoi) <= 9.0 and math.dist(toadoquai, toadodongdoi) < khoangcachtoiquai for toadodongdoi in toadodongdois):
                    self._danhsachidquaidagom.discard(iddoituongquai)
                    if self._idquaidautien == iddoituongquai:
                        self._idquaidautien = 0
                        diachiquaidautien = 0
                    continue

            if iddoituongquai in self._idmuctieubiloi_map:
                continue

            khoangcach = self.moitruong.get_khoangcach(diachidoituongxemxet)

            if khoangcach < KHOANGCACHTOANMANHINH:
                is_coquaixungquanh = True

            if iddoituongquai in self._danhsachidquaidagom:
                if khoangcach > 12.0:
                    if is_canghilog: print(f"[GOM] Quái {hex(iddoituongquai)} rớt lại (>12m) -> Xóa để đón")
                    self._danhsachidquaidagom.remove(iddoituongquai)
                    if iddoituongquai == self._idquaidautien:
                        self._idquaidautien = 0
                        diachiquaidautien = 0
                else:
                    if khoangcach <= 6.0: soluongquaigan += 1
                continue

            if khoangcach <= 4.5:
                self._danhsachidquaidagom.add(iddoituongquai)
                if self._idquaidautien == 0:
                    self._idquaidautien = iddoituongquai
                    diachiquaidautien = diachidoituongxemxet
                    khoangcachneohientai = khoangcach
                soluongquaigan += 1
                continue

            if not is_neobirotlai and khoangcach <= 15.0 and iddoituongquai not in self._danhsachidquaidagom:
                is_thoamandieukienneo = True
                if diachiquaidautien:
                    khoangcachneo = self.moitruong.get_khoangcach(diachidoituongxemxet, diachiquaidautien)
                    if khoangcachneo > 18.0: is_thoamandieukienneo = False

                if is_thoamandieukienneo:
                    if khoangcach < khoangcachquaicankeo:
                        khoangcachquaicankeo = khoangcach
                        idquaicankeogannhat = iddoituongquai
                        diachicosoquaicankeo = diachidoituongxemxet

        soluongquaidagom = len(self._danhsachidquaidagom)

        if idquaicankeogannhat == 0 and not is_neobirotlai:
            diachinhanvatmuctieudangchon = diachimuctieudangchon
            if diachinhanvatmuctieudangchon and self.moitruong.get_is_nhanvattontai(diachinhanvatmuctieudangchon) and self.moitruong.get_is_cothetancong(diachinhanvatmuctieudangchon):
                if self.moitruong.get_idloainhanvat(diachinhanvatmuctieudangchon) == LOAIMUCTIEU_QUAIVATHOACNPC:
                    id_target = self.moitruong.get_iddoituong(diachinhanvatmuctieudangchon)
                    kc_target = self.moitruong.get_khoangcach(diachinhanvatmuctieudangchon)
                    toadotarget = self.moitruong.get_toado(diachinhanvatmuctieudangchon)
                    is_dongdoigannhuong = any(math.dist(toadotarget, t) <= 9.0 and math.dist(toadotarget, t) < kc_target for t in toadodongdois)
                    if id_target not in self._danhsachidquaidagom and id_target not in self._idmuctieubiloi_map and 12.0 < kc_target < KHOANGCACHTOANMANHINH and not is_dongdoigannhuong:
                        idquaicankeogannhat = id_target
                        diachicosoquaicankeo = diachinhanvatmuctieudangchon
                        khoangcachquaicankeo = kc_target
                        if is_canghilog: print(f"[GOM] dự phòng mục tiêu: {hex(idquaicankeogannhat)}")

        if not is_coquaixungquanh:
            self._danhsachidquaidagom.clear()
            self._idquaidautien = 0

        if is_canghilog:
            neo_str = f"{hex(self._idquaidautien)}" if self._idquaidautien else "None"
            neo_kc = f"({round(khoangcachneohientai, 1)}m)" if self._idquaidautien else ""
            print(f"[GOM] Neo: {neo_str}{neo_kc} | List: {soluongquaidagom} | Gần: {soluongquaigan}/{self._soluongquaigomtoithieu} | Target: {hex(idquaicankeogannhat) if idquaicankeogannhat else 'None'}")

        if soluongquaidagom == 0 and idquaicankeogannhat == 0:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            return

        is_dusoluongquaigan = soluongquaigan >= self._soluongquaigomtoithieu
        is_quatai = soluongquaidagom >= 20
        is_khongkeoduocnua = (idquaicankeogannhat == 0 and soluongquaidagom > 0)
        is_dangdanh = (not self._is_danggomquai and soluongquaidagom > 0)

        if is_dusoluongquaigan or is_quatai or is_khongkeoduocnua or is_dangdanh or is_neobirotlai:
            is_canluive = False
            lydolui = ""

            if diachiquaidautien:
                if (is_dusoluongquaigan or is_quatai) and khoangcachneohientai > 4.5:
                    is_canluive = True
                    lydolui = "Tụ quái"
                elif is_neobirotlai:
                    is_canluive = True
                    lydolui = "Đón Neo"

            if is_canluive:
                if is_canghilog: print(f"[GOM] {lydolui}: Quay lại Neo ({round(khoangcachneohientai, 1)}m)")

                if self._kiemtraketgomquai(self._idquaidautien, khoangcachneohientai):
                    self._boquaquaibichan(self._idquaidautien)
                    self._yeucaugomquai = None
                    return

                x_neo, y_neo = self.moitruong.get_toado(diachiquaidautien, )

                yeucaugomquaimoi = {
                    "yeucau": YEUCAUDICHUYENGOMQUAI,
                    "toadodich": (x_neo, y_neo),
                    "khoangcachtoida": 3.0,
                    "idmuctieu": self._idquaidautien,
                    "diachimuctieu": diachiquaidautien
                }
            else:
                if not is_neobirotlai:
                    if self._is_danggomquai and is_canghilog:
                        print(f"[GOM] >>> ĐỦ ({soluongquaigan} gần) & TỤ XONG -> ĐÁNH <<<")
                    self._is_danggomquai = False
                    self._yeucaugomquai = None
                    self._idquaidangkeo = 0
                    if soluongquaidagom == 0: self._danhsachidquaidagom.clear()
                    return

        if not self._is_danggomquai and is_canghilog:
            print("[GOM] >>> BẮT ĐẦU CHẠY GOM")
        self._is_danggomquai = True

        if yeucaugomquaimoi:
            self._yeucaugomquai = yeucaugomquaimoi
            return

        if idquaicankeogannhat > 0:
            if diachicosoquaicankeo == 0:
                self._yeucaugomquai = None
                return

            if idquaicankeogannhat != self._idquaidangkeo:
                self._idquaidangkeo = idquaicankeogannhat
                self._thoidiembatdaukeo = time.time()

            # Trước đây hết 5s vẫn coi quái là đã gom (kể cả khi bị tường chặn) nên lại bầu nó làm neo và kẹt tiếp
            if khoangcachquaicankeo > 1.5 and (self._kiemtraketgomquai(idquaicankeogannhat, khoangcachquaicankeo) or time.time() - self._thoidiembatdaukeo > 8.0):
                self._boquaquaibichan(idquaicankeogannhat)
                self._yeucaugomquai = None
                return

            if khoangcachquaicankeo <= 1.5:
                self._danhsachidquaidagom.add(idquaicankeogannhat)
                if self._idquaidautien == 0:
                    self._idquaidautien = idquaicankeogannhat
                yeucaugomquaimoi = None
                self._idquaidangkeo = 0
                if is_canghilog: print(f"[GOM] Đã tiếp cận {hex(idquaicankeogannhat)}")
            else:
                x_quai, y_quai = self.moitruong.get_toado(diachicosoquaicankeo, )

                if x_quai > 0 and y_quai > 0:
                    if is_canghilog: print(f"[GOM] SET MOVE -> {hex(idquaicankeogannhat)}")
                    yeucaugomquaimoi = {
                        "yeucau": YEUCAUDICHUYENGOMQUAI,
                        "toadodich": (x_quai, y_quai),
                        "khoangcachtoida": 0.,
                        "idmuctieu": idquaicankeogannhat,
                        "diachimuctieu": diachicosoquaicankeo
                    }
        else:
            yeucaugomquaimoi = None
            self._idquaidangkeo = 0

        self._yeucaugomquai = yeucaugomquaimoi

    def action_tudongxulyvebanrac(self):
        if not self._is_tudongvebanrac:
            return

        tenmonphai = self.moitruong.get_tenmonphai()

        if tenmonphai == "maoson":
            self._action_xulyvebanrac_maoson()
        else:
            self._action_xulyvebanrac_phaikhac()

    def _action_xulyvebanrac_maoson(self):
        if not self._is_tudongvebanrac:
            self._trangthaiveban = 0
            return

        if self.moitruong.get_tenmonphai() != "maoson":
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        chutiemtaphoa = "Chủ Tiệm Tạp Hóa"

        if self._trangthaiveban == 0:
            is_dayhanhtrang = self.moitruong.get_is_dayhanhtrang()

            diachi_npc = self.moitruong.action_timkiemnhanvat(chutiemtaphoa)
            is_dangganchutiemtaphoa = False
            if diachi_npc:
                if self.moitruong.get_khoangcach(diachi_npc) <= 3.0:
                    is_dangganchutiemtaphoa = True

            if is_dangganchutiemtaphoa:
                if is_dayhanhtrang:
                    print("[AUTO-RECOVERY] Phát hiện đang ở cạnh NPC và túi đầy -> Tiếp tục bán.")
                    self._trangthaiveban = 2
                    self._thoidiemchuyentrangthai = time.time()
                else:
                    print("[AUTO-RECOVERY] Đang ở cạnh NPC và túi đã gọn -> Quay lại bãi train.")
                    self._trangthaiveban = 4
                    self._thoidiemchuyentrangthai = time.time()

            elif is_dayhanhtrang:
                self._trangthaiveban = 1
                self._thoidiemchuyentrangthai = time.time()

        elif self._trangthaiveban == 1:
            if not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_XUYENKHONGHANH):
                print("[AUTO-SELL] Xuyên không hành thành công (đang hồi chiêu). Chuyển bước.")
                self._trangthaiveban = 2
                self._thoidiemchuyentrangthai = time.time()
                return

            if time.time() - self._thoidiemchuyentrangthai > 1.5:
                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                    print("[AUTO-SELL] Đã đứng yên. Sử dụng Xuyên không hành (Về thành)")
                    self.moitruong.action_ngatdichuyen()
                    self.moitruong.action_thucthicaulenh("pf 4182.1")
                    self._thoidiemchuyentrangthai = time.time()

        elif self._trangthaiveban == 2:
            if time.time() - self._thoidiemchuyentrangthai > 3.0:
                diachi_npc = self.moitruong.action_timkiemnhanvat(chutiemtaphoa)
                if diachi_npc:
                    khoangcach = self.moitruong.get_khoangcach(diachi_npc)
                    if khoangcach <= 3.0:
                        print("[AUTO-SELL] Đã gặp NPC, bắt đầu bán")
                        self._trangthaiveban = 3
                    else:
                        self.moitruong.action_dichuyengiukhoangcachtoida(diachi_npc, 3.)
                        time.sleep(0.5)
                else:
                    print("[AUTO-SELL] Đang tìm NPC Tạp Hóa...")
                    if time.time() - self._thoidiemchuyentrangthai > 6.0:
                        print("[AUTO-SELL] Lỗi: Không tìm thấy NPC quá lâu -> Reset.")
                        self._trangthaiveban = 0

        elif self._trangthaiveban == 3:
            self.action_tudongbanrac()
            time.sleep(1.)
            self.action_suavatpham()
            time.sleep(1.)

            if not self.moitruong.get_is_dayhanhtrang():
                print("[AUTO-SELL] Đã bán xong, chuẩn bị quay lại")
                self._trangthaiveban = 4
                self._thoidiemchuyentrangthai = time.time()
            else:
                time.sleep(1.0)

        elif self._trangthaiveban == 4:
            if not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_XUYENKHONGHANH):
                print("[AUTO-SELL] Xuyên không hành (Quay lại) thành công. Kết thúc quy trình.")
                self._trangthaiveban = 0
                self._yeucautudo = None
                self._diachicosokhaikhoang = 0
                self._thoidiemphatamlacmapgannhat = time.time()
                return

            if time.time() - self._thoidiemchuyentrangthai > 1.0:
                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                    print("[AUTO-SELL] Đã đứng yên. Sử dụng Xuyên không hành (Quay lại)")
                    self.moitruong.action_ngatdichuyen()
                    self.moitruong.action_thucthicaulenh("pf 4182.2")
                    self._thoidiemchuyentrangthai = time.time()

    def _action_xulyvebanrac_phaikhac(self):
        if self._trangthaiveban == 0:
            diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = CHUTIEMTAPHOA)

            if diachinpc and self.moitruong.get_khoangcach(diachinpc) <= 3.0:
                if not self.moitruong.get_is_dayhanhtrang():
                    if self._diemdanhxungquanhs:
                        print("[AUTO-SELL] Đứng cạnh NPC và túi đã gọn. Tiếp tục quay lại bãi farm.")
                        self._trangthaiveban = 4
                        return
                else:
                    print("[AUTO-SELL] Đứng cạnh NPC nhưng túi đầy. Tiếp tục bán.")
                    self._trangthaiveban = 2
                    return
            if self.moitruong.get_is_dayhanhtrang():
                print("[AUTO-SELL] Hành trang đầy. Bắt đầu quy trình về bán.")
                self._trangthaiveban = 1
                self._thoidiemhoithanhphu = 0

        elif self._trangthaiveban == 1:
            if self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
                print("[AUTO-SELL] Đã về thành công. Chuyển sang di chuyển.")
                self._trangthaiveban = 2
                return

            if time.time() - self._thoidiemhoithanhphu > 12.0 and not self.moitruong.get_is_dangvankhi():
                print("[AUTO-SELL] Đang dùng Hồi Thành Phù...")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu()
                self._thoidiemhoithanhphu = time.time()

        elif self._trangthaiveban == 2:
            thoidiembatdau = time.time()
            thoigiantoida = 45.0
            while True:
                if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
                    return
                if time.time() - thoidiembatdau > thoigiantoida:
                    print(f"[AUTO-SELL] Quá {thoigiantoida}s không tới được Tiệm Tạp Hóa. Thử lại.")
                    self._trangthaiveban = 1
                    return
                diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = CHUTIEMTAPHOA)
                if self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
                    if not diachinpc:
                        self.moitruong.action_dichuyengiukhoangcachtoidadiem(X_CHUTIEMTAPHOA_TANTHUTHON, Y_CHUTIEMTAPHOA_TANTHUTHON, khoangcachtoida = 0.)
                    else:
                        khoangcach = self.moitruong.get_khoangcach(diachinpc)
                        if khoangcach <= 3.0:
                            print("[AUTO-SELL] Đã tìm thấy NPC, chuẩn bị bán đồ...")
                            self._trangthaiveban = 3
                            return
                        else:
                            self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 0.)
                else:
                    if not diachinpc:
                        print("[AUTO-SELL] Đang chờ load map hoặc chưa về thành...")

                time.sleep(1.0)

        elif self._trangthaiveban == 3:
            self.action_tudongbanrac()
            time.sleep(1.0)
            self.action_suavatpham()
            time.sleep(1.)

            if not self.moitruong.get_is_dayhanhtrang():
                print("[AUTO-SELL] Đã bán xong.")
                self._trangthaiveban = 4

        elif self._trangthaiveban == 4:
            if not self._diemdanhxungquanhs:
                print("[AUTO-SELL] Lỗi: Không có danh sách điểm đánh!")
                self._trangthaiveban = 0
                return
            self.action_dichuyenlenbandofarm()
            danhsachbandohople = [diem[2] for diem in self._diemdanhxungquanhs if len(diem) >= 3]
            if self.moitruong.get_idbandohientai() in danhsachbandohople:
                print("[AUTO-SELL] Đã tới bãi farm hợp lệ.")
                self._trangthaiveban = 0

    def action_sudunghoithanhphu(self):
        if time.time() - self._thoidiemsudunghoithanhphugannhat > 6.:
            self._thoidiemsudunghoithanhphugannhat = time.time()
            self._thoidiemvohieuhoatatchucnangmoronggannhat = time.time() + 10.
            #self.action_sudungvatphamhanhtrang(HOITHANHPHU)
            self.moitruong.action_thucthicaulenh("dGludmF0 2")

    def action_dichuyenlenbandofarm(self):
        diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = TANTHUTIENCO)

        if not diachinpc:
            if self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
                print(f"[DI-CHUYEN] Chưa thấy {TANTHUTIENCO}, di chuyển đến vị trí (148, 145)...")
                self.moitruong.action_dichuyengiukhoangcachtoidadiem(148, 145, khoangcachtoida = 3.)
                self._thoidiemsudunghoithanhphugannhat = time.time()
            elif self.moitruong.get_idbandohientai() == BANDO_CHU:
                print(f"[DI-CHUYEN] Chưa thấy {TANTHUTIENCO}, di chuyển đến vị trí (322, 132)...")
                self.moitruong.action_dichuyengiukhoangcachtoidadiem(X_TANTHUTIENCO_CHU, Y_TANTHUTIENCO_CHU, khoangcachtoida = 3.)
                self._thoidiemsudunghoithanhphugannhat = time.time()
            else:
                print(f"[DI-CHUYEN] Không tìm thấy NPC {TANTHUTIENCO}. Đang tìm kiếm...")
            return

        khoangcach = self.moitruong.get_khoangcach(diachinpc)

        if khoangcach > 6.0:
            self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, 3.)
            return

        target_map = self._diemdanhxungquanhs[0][2] if self._diemdanhxungquanhs else 0
        if not target_map:
            return

        steps = DICHUYENTANTHUTIENCO_MAP.get(target_map)

        if not steps:
            print(f"[DI-CHUYEN] Chưa định nghĩa đường đi cho Map ID: {target_map}")
            return

        idnpc = self.moitruong.get_iddoituong(diachinpc)
        hex_id = hex(idnpc).replace("0x", "")

        print(f"[DI-CHUYEN] Bắt đầu di chuyển lên map {target_map}...")

        for step in steps:
            caulenh = f"tallk {hex_id}# {step}"
            self.moitruong.action_thucthicaulenh(caulenh)
            time.sleep(1.0)

        if self.moitruong.get_is_danghiencuasotuychon():
            self.moitruong.set_is_danghiencuasotuychon(False)

    def action_tudongkhaikhoang(self):
        if not self._is_tudongkhaikhoang:
            self._yeucaukhaikhoang = None
            self._diachicosokhaikhoang = 0
            return

        idbandohientai = self.moitruong.get_idbandohientai()

        if idbandohientai != self._idbandolanquetkhaikhoangtruoc:
            self._idkhoangbiloi_map.clear()
            self._idbandolanquetkhaikhoangtruoc = idbandohientai

        if self.moitruong.get_is_dangvankhi() or self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_nhanvatdachet() or time.time() - self._thoidiemtamngungdichuyensudungkynang < 0.:
            self._yeucaukhaikhoang = None
            self._diachicosokhaikhoang = 0
            return

        if 0:
            pass
        else:
            idcanxoas = [k for k, v in self._idkhoangbiloi_map.items() if time.time() - v > 30]
            for k in idcanxoas:
                del self._idkhoangbiloi_map[k]

            i = -1
            diachidoituonggannhat = None
            khoangcachgannhat = KHOANGCACHTOIDAHOPLE + 1

            while True:
                i += 1
                diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachidoituong: break

                tendoituong = self.moitruong.get_tendoituong(diachidoituong)
                tenvatphamkhangs = NGUYENLIEULUYENDONs
                if self.moitruong.get_idnguoichoi() == 59845:
                    tenvatphamkhangs = ("Thiết Khoáng", "Ngân Khoáng", "Tích Khoáng")

                if tendoituong and tendoituong in tenvatphamkhangs:
                    iddoituong = self.moitruong.get_iddoituong(diachidoituong)
                    if iddoituong <= 0: continue
                    if iddoituong in self._idkhoangbiloi_map: continue

                    khoangcach = self.moitruong.get_khoangcach(diachidoituong)
                    if khoangcach > KHOANGCACHTOANMANHINH: continue

                    if khoangcach < khoangcachgannhat:
                        khoangcachgannhat = khoangcach
                        diachidoituonggannhat = diachidoituong
            if diachidoituonggannhat:
                self._xuly_daokhoang(diachidoituonggannhat, khoangcachgannhat)
            else:
                self._idkhoangdangtheo = 0
                self._yeucaukhaikhoang = None
                self._diachicosokhaikhoang = 0

    def _xuly_lotrinh_chung(self, target_x, target_y, index_var_name, len_list):
        i = -1
        best_mineral_addr = 0
        min_char_dist = 9999.

        while True:
            i += 1
            diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituong: break
            tendoituong = self.moitruong.get_tendoituong(diachidoituong)
            if tendoituong and ("Khoáng" in tendoituong or "KhoÃ¡ng" in tendoituong):
                iddoituong = self.moitruong.get_iddoituong(diachidoituong)
                if iddoituong <= 0 or iddoituong in self._idkhoangbiloi_map: continue
                mx, my = self.moitruong.get_toado(diachidoituong)

                if math.dist((mx, my), (target_x, target_y)) <= 12.0:
                    char_dist = self.moitruong.get_khoangcach(diachidoituong)
                    if char_dist < min_char_dist:
                        min_char_dist = char_dist
                        best_mineral_addr = diachidoituong

        if best_mineral_addr:
            self._xuly_daokhoang(best_mineral_addr, min_char_dist)
        else:
            self._xuly_chaylotrinh(target_x, target_y, index_var_name, len_list)

    def _xuly_daokhoang(self, diachikhoang, khoangcach):
        id_min = self.moitruong.get_iddoituong(diachikhoang)

        if id_min != self._idkhoangdangtheo:
            self._idkhoangdangtheo = id_min
            self._thoidiembatdautheokhoang = time.time()
        else:
            if time.time() - self._thoidiembatdautheokhoang > 10.0:
                phatam("Khoáng lỗi, bỏ qua")
                self._idkhoangbiloi_map[id_min] = time.time()
                self._idkhoangdangtheo = 0
                self._yeucaukhaikhoang = None
                return

        if khoangcach >= 6.0:
            mx_move, my_move = self.moitruong.get_toado(diachikhoang, )

            self._yeucaukhaikhoang = {
                "yeucau": YEUCAUDICHUYENKHAIKHOANG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                "toadodich": (mx_move, my_move),
                "khoangcachtoida": 0
            }
        else:
            self._yeucaukhaikhoang = None

            if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                if time.time() - self._thoidiemkhaikhoanggannhat > 1.0:
                    self.moitruong.action_khaikhoang(id_min)
                    self._thoidiemkhaikhoanggannhat = time.time()
                    self._thoidiembatdautheokhoang = time.time()
            else:
                pass

        self._diachicosokhaikhoang = diachikhoang

    def _xuly_chaylotrinh(self, tx, ty, index_var_name, len_list):
        self._diachicosokhaikhoang = 0
        self._idkhoangdangtheo = 0

        char_x, char_y = self.moitruong.get_toado()
        dist_to_target = math.dist((char_x, char_y), (tx, ty))

        if dist_to_target <= 3.0:
            current_index = getattr(self, index_var_name)
            setattr(self, index_var_name, (current_index + 1) % len_list)
            self._yeucaukhaikhoang = None
        else:
            self._yeucaukhaikhoang = {
                "yeucau": YEUCAUDICHUYENKHAIKHOANG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                "toadodich": (tx, ty),
                "khoangcachtoida": 0
            }

    def action_tudongdichientruong(self):
        if not self._is_tudongdichientruong:
            return

        if time.time() - self._thoidiemdichientruonggannhat < 0.5:
            return

        idbandohientai = self.moitruong.get_idbandohientai()
        is_dangnamtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        is_truongnhom = self.moitruong.get_is_truongnhom()

        if idbandohientai == BANDO_CHIENTRUONG:
            if time.time() - self._thoidiemclickchientruonggannhat >= 5.0:
                hwnd = self.moitruong.idcuaso
                x, y = 405, 315
                lparam = (y << 16) | (x & 0xFFFF)

                win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
                time.sleep(0.05)
                win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lparam)

                self._thoidiemclickchientruonggannhat = time.time()
            return

        if idbandohientai == BANDO_CHU and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 0.5:
            diachinpc = self.moitruong.action_timkiemnhanvat(TRUONGQUALAO)

            if not diachinpc:
                self.moitruong.action_dichuyengiukhoangcachtoidadiem(X_TRUONGQUALAO, Y_TRUONGQUALAO, khoangcachtoida = 3.0)
                self._thoidiemdichientruonggannhat = time.time()
                return

            khoangcach = self.moitruong.get_khoangcach(diachinpc)
            if khoangcach > 9.0:
                self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 3.)
                self._thoidiemdichientruonggannhat = time.time()
                return

            idnpc = self.moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                return

            self._thoidiemdichientruonggannhat = time.time()

            if is_truongnhom:
                caulenh = "tallk {}# welcome.2".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh)
                time.sleep(0.25)
                caulenh = "tallk {}# welcome.3".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh)
                time.sleep(0.25)
            elif is_dangnamtrongnhom:
                caulenh = "tallk {}# welcome.3".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh)
                time.sleep(0.25)
            else:
                caulenh = "tallk {}# welcome.1".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh)
                time.sleep(0.25)
                caulenh = "tallk {}# welcome.3".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh)
                time.sleep(0.25)

    def action_tudongdaotangbaodo(self):
        self._yeucaudaotangbaodo = None

        if not self._is_tudongdaotangbaodo:
            self._thoidiemhettangbaodogannhat = 0.
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        idbandohientai = self.moitruong.get_idbandohientai()
        x_hientai, y_hientai = self.moitruong.get_toado()

        # if time.time() - self._thoidiemhettangbaodogannhat < 60 * 3 and math.dist((x_hientai, y_hientai), (150, 128)) < 3.:
        #     return

        soluongvatphamhanhtrangtoida = self.moitruong.get_soluongvatphamhanhtrangtoida()
        for i in range(soluongvatphamhanhtrangtoida):
            tenvatpham = self.moitruong.get_tenvatphamhanhtrang(i)
            if not tenvatpham or tenvatpham != TANGBAODO:
                continue

            mota = self.moitruong.get_motavatphamhanhtrang(i)
            if not mota: continue

            timthay = re.search(r"Vị trí: \s*(.*?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", mota)
            if timthay:
                tenbandotrongmota = timthay.group(1).strip()
                x_dich = int(timthay.group(2))
                y_dich = int(timthay.group(3))

                idbandodich = IDBANDO_MAP.get(tenbandotrongmota)

                if idbandodich == idbandohientai:
                    khoangcach = math.sqrt((x_hientai - x_dich) ** 2 + (y_hientai - y_dich) ** 2)
                    if khoangcach < 1.:
                        print(f"[DAOTAOBAODO] Đang đào tại {tenbandotrongmota} ({x_dich}, {y_dich})")
                        iddoituong = self.moitruong.get_iddoituongvatphamhanhtrang(i)
                        if iddoituong:
                            self.moitruong.action_sudungvatpham(iddoituong)
                            time.sleep(1.0)
                    else:
                        self.moitruong.action_tudongtimduong(x_dich, y_dich, idbandodich)
                    return

        self.moitruong.action_tudongtimduong(0, 0, 0)

        quocgiacanden = None
        soluongvatphamhanhtrangtoida = self.moitruong.get_soluongvatphamhanhtrangtoida()
        for i in range(soluongvatphamhanhtrangtoida):
            tenvatpham = self.moitruong.get_tenvatphamhanhtrang(i)
            if tenvatpham == TANGBAODO:
                mota = self.moitruong.get_motavatphamhanhtrang(i)
                if mota:
                    timthay = re.search(r"Vị trí: \s*(.*?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", mota)
                    if timthay:
                        tenbandotrongmota = timthay.group(1).strip()
                        quocgiacanden = f"{tenbandotrongmota} Quốc"
                        break

        if not quocgiacanden:
            self._thoidiemhettangbaodogannhat = time.time()
            if self.moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                print(f"[DAOTAOBAODO] Dùng Hồi Thành Phù về Tân Thủ Thôn")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu()
                self._thoidiemsudunghoithanhphugannhat = time.time()
                phatam("{} hết tàng bảo đồ".format(self.moitruong.get_tendoituong()))
                time.sleep(5)
            else:
                if not self.moitruong.action_timkiemvatphamhanhtrang(LAMCAU):
                    phatam("{} hết tàng bảo đồ".format(self.moitruong.get_tendoituong()))
                    time.sleep(5)
                    return

                # print("[DAOTAOBAODO] Tiến hành bán rác & sửa đồ...")
                # self.action_tudongbanrac()
                #
                # khoangcachdennpc = math.dist((x_hientai, y_hientai), (150, 128))
                # if khoangcachdennpc > 3.:
                #     self.moitruong.action_tudongtimduong(150, 128, idbandohientai)
            return

        print(f"[DAOTAOBAODO] Hết map hiện tại. Chuẩn bị sang: {quocgiacanden}")

        if idbandohientai != BANDO_TANTHUTHON:
            if time.time() - self._thoidiemsudunghoithanhphugannhat > 12.0:
                print(f"[DAOTAOBAODO] Dùng Hồi Thành Phù về Tân Thủ Thôn")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu()
                self._thoidiemsudunghoithanhphugannhat = time.time()
            return

        khoangcachdennpc = math.dist((x_hientai, y_hientai), (148, 149))

        if khoangcachdennpc > 3.0:
            self.moitruong.action_tudongtimduong(148, 149, idbandohientai)
            return

        tenchudichtram = "Chủ Dịch Trạm"
        diachinpc = self.moitruong.action_timkiemnhanvat(tenchudichtram)

        if not diachinpc:
            return

        idnpc = self.moitruong.get_iddoituong(diachinpc)
        if idnpc:
            self.moitruong.action_ngatdichuyen()
            timestamp = int(time.time())
            hex_id = hex(idnpc).replace("0x", "")
            caulenh = f"tallk {hex_id}# goto.! {quocgiacanden} t{timestamp}"
            self.moitruong.action_thucthicaulenh2(caulenh, delay = 0.0)
            self.moitruong.action_ngatdichuyen()
            time.sleep(5.0)

    def action_tudongbatautoingame(self):
        self.moitruong.set_is_batautoingame(False)

        if self.moitruong.get_is_dangvankhi():
            return

        if self.moitruong.get_idbandohientai() in (701, 395, 894, 135, 139, BANDO_CHIENTRUONG, BANDO_TIVO, BANDO_BANGPHAI):
            return

        if self.moitruong.get_idmaupk() != MAUPK_HOABINH:
            return

        if not self._is_tudongbattatchucnangmorong:
            return

        if not self._is_tudongdichuyendiemdanhxungquanh:
            self.moitruong.action_tatchucnangmorong()
            return

        if self.moitruong.get_idbandohientai() not in BANDOKHONGPKs:
            if time.time() - self._thoidiemvohieuhoabatchucnangmoronggannhat < 0.:
                self.moitruong.action_tatchucnangmorong()
            elif not self._is_tudongsudungkynang or (self.moitruong.get_is_dangbatchucnangmorong() and time.time() - self.moitruong.thoidiemcochucnangmoronggannhat > 10.):
                if time.time() - self._thoidiemvohieuhoatatchucnangmoronggannhat > 0.:
                    self.moitruong.action_tatchucnangmorong()
            else:
                self.moitruong.action_batchucnangmorong()
        else:
            self.moitruong.action_tatchucnangmorong()

    def _xoatrangthaisaukhichet(self):
        self._yeucaunhatvatpham = None
        self._yeucautheosautruongnhom = None
        self._yeucautancong = None
        self._yeucautudo = None
        self._yeucaugomquai = None
        self._yeucaukhaikhoang = None
        self._yeucaudaotangbaodo = None

        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
        self._diachicosomuctieuduphong = 0
        self._diachicosovatphamdangnhat = False
        self._diachicosokhaikhoang = 0

        self._is_danggomquai = False
        self._danhsachidquaidagom.clear()
        self._idquaidautien = 0
        self._idquaidangkeo = 0

        self._trangthaiveban = 0

        self._idmuctieudangtheokiemtraket = 0
        self._thoidiemdungimkiemtraket = 0.
        self._idmuctieubiloi_map.clear()
        self._idkhoangbiloi_map.clear()

        self._solanthatbaikhaithien = 0
