import math
import random
import re
import time

import pymem

from hangso import *
from moitruong import MoiTruong
from tienich import luuthietlap as util_luuthietlap
from tienich import taithietlap as util_taithietlap, phatam


class TacTu:
    def __init__(self, moitruong: MoiTruong):
        self._thoidiemsudungthaotacbaothugannhat = 0.
        self._thoidiemthietlaptudongsudungkynangthiencangannhat = 0.
        self._thoidiemyeucaubaothuvatphamdoilenhgannhat = 0.
        self._thoidiemtamngungsudungkynang = 0.
        self._thoidiemhoiphucbaothugannhat = 0.
        self._is_tudongsudungkynangbaothu = True
        self._thoidiemdocsachgannhat = 0.
        self._thoidiemdichientruonggannhat = 0.
        self._thoidiembatdaudendiem = 0.
        self._thoidiemlogdebug = 0.
        self._is_tudongdieukhienbaothu = True
        self._solanthatbaikhaithien = 0
        self._thoidiembiphatkhaithien = 0.
        self._is_tudonglamnhiemvulaoquangia = False
        self._is_tudongcatdovaoruong = True
        self._is_thucsondao = False
        self.moitruong = moitruong

        self._is_tudongtheosautruongnhom = False
        self._is_tudongbattheosaunhom = True
        self._is_tudongtimkiemmuctieu = True
        self._is_tudongsudungkynang = True
        self._is_tudongsudungvatpham = True
        self._is_tudongnhatdo = True
        self._is_chidanhnguoichoi = False
        self._is_tudongtodoi = True
        self._is_tudongphucsinh = True
        self._is_tudongsuado = True
        self._is_tudongtrieuhoibaothudautien = True
        self._is_tudongchaylenbandovuachet = True
        self._is_tudongxepchongdo = True
        self._is_tudongkhaikhoang = False
        self._thoidiemkhaikhoanggannhat = 0.
        self._yeucaukhaikhoang = None

        self._diachicosomuctieuduphong = 0
        self._thoidiemphatamanthan = 0.
        self._diachicosokhaikhoang = 0
        self._idkhoangbiloi_map = {}
        self._thoidiembatdaudichuyendenmotdiem = 0.
        self._idkhoangdangtheo = 0
        self._thoidiembatdautheokhoang = 0.
        self._idbandolanquetkhaikhoangtruoc = 0
        self._is_nhieumuctieugan3 = False
        self._is_nhieumuctieugan5 = False
        self._is_nhieumuctieugan7 = False
        self._is_nhieumuctieugan9 = False
        self._soluongnhieumuctieu = 2
        self._soluongquaigomtoithieu = 6
        self._is_tudonggomquai = False
        self._is_danggomquai = False
        self._danhsachidquaidagom = set()
        self._yeucaugomquai = None

        self._thoidiemphatamketduonggannhat = 0.
        self._is_uutienmuctieupk = True

        self._khoangcachtoidatruongnhom = 9

        self._tenmuctieutancongs = set()
        self._tenmuctieukhongtancongs = set(TENMUCTIEUKHONGTANCONGs)

        self._tenvatphamnhats = set()

        self._thoidiembattattheosaunhomgannhat = time.time()
        self._thoidiemtamngungkhaithientichdia = time.time()
        self._thoidiemkiemtrahieuunggannhat = time.time()
        self._thoidiemdichuyenkhacbandodichuyenxungquanhgannhat = time.time()
        self._thoidiemnhanvatchetgannhat = time.time()
        self._thoidiemthongbaotudongtimduonggannhat = time.time()
        self._thoidiemkiemtranpcsuadogannhat = time.time()
        self._thoidiemnhatdogannhat_map = {}
        self._thoidiemdoimaupkgannhat = time.time()
        self._thoidiemdichuyengiukhoangcachtoithieugannhat = time.time()
        self._thoidiemdichuyendiemdanhxungquanhgannhat = time.time()
        self._thoidiemyeucauroikhoichientruonggannhat = time.time()
        self._thoidiemtudongtrieuhoibaothudautien = time.time()
        self._thoidiemthietlapbaothuchodoigannhat = time.time()
        self._thoidiemdieukhienbaothugannhat = time.time()
        self._thoidiemkiemtracuoithugannhat = time.time()
        self._thoidiemsudungvatphamgannhat = time.time()
        self._thoidiemsudungthucanbaothugannhat = time.time()
        self._thoidiemmochangiabaoruonggannhat = time.time()
        self._thoidiemsudungtusamdongannhat = 0.
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
        self._thoidiemloggomquai = 0.

        self._idmuctieubiloi_map = {}
        self._idmuctieudangtheokiemtraket = 0
        self._thoidiemdungimkiemtraket = 0.

        self._yeucaunhatdo = None
        self._yeucautheonhom = None
        self._yeucautancong = None
        self._yeucautudo = None

        self._thoidiemtamngungdichuyensudungkynang = 0.
        self._khoangcachtimkiemmuctieu = 18.
        self._is_tudongtrieuhoithanthu = True
        self._is_tudongdichuyendiemdanhxungquanh = False
        self._is_tudongdoimaupk = False

        self._idbandohientai = False
        self._phehientai = False

        self._idbandovuachet = False

        self._diachicosovatphamdangnhat = False

        self._solansudungkhaithientichdia = 0
        self._solansudungluutinhtruymang = 0

        self._is_chantangcapdo = True

        self._trangthaikhaithientichdia = {
            "is_danglui": False,
            "thoidiembatdau": 0.,
            "idmuctieu": 0,
        }

        self._diachicosonhanvatmuctieudangdichuyenkhaithien = 0
        self._thoidiembatdaudichuyenkhaithien = 0.
        self._thoidiemralenhbaothutancong = 0.

        self._idbandomuctieudangchon = 0

        self._idquaidangkeo = 0
        self._thoidiembatdaukeo = 0.
        self._is_tudongvebanrac = False
        self._trangthaiveban = 0  # 0: Idle, 1: Đang về, 2: Đang đi shop, 3: Đang bán, 4: Đang quay lại
        self._thoidiemchuyentrangthai = 0.

        self._idbandofarmbanrac = 0
        self._thoidiemhoithanhphu = 0.  # Timer cho việc hồi thành phù

        self._toadokiemtraket = (0, 0)
        self._thoidiembatdaukiemtraket = 0.

        self._idquaigomdautien = 0
        self._thoidiemphatamlacmapgannhat = 0.
        self._thoidiemphatamdayhanhtrang = 0.

        self._thoidiemgapnguoichoigannhat = 0.
        self._thoidiemdichuyentudogannhat = 0.

        self._is_tudongdichientruong = False

        self._is_tudonglamnhiemvusugia = False

        self._is_khaithientichdiasansang = False
        self._thoidiemkhaithientichdiakhongsansanggannhat = 0.
        self._is_luutinhtruymangsansang = False
        self._thoidiemluutinhtruymangkhongsansanggannhat = 0.

        self._is_yeucauvohieuhoadichuyen = False
        self._is_uutienbaothumaoson = False
        self._is_khonguutienbaothugiangho = False

        self._is_chedobufftoanbang = False
        self._is_khongcongidebuff = False

        self._thoidiemsudungbaothuvatphamgannhat = 0.
        self._thoidiemthietlaptrieuhoithudoilenhgannhat = 0.
        self._thoidiemkiemtrakhongcongidebuffgannhat = 0.

        self._is_battudongtancongvatly = False
        self._thoidiemtodoigannhat_map = {}
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

        self._is_dasudungbaothuvatpham = False
        self._thoidiemsudungcaoboctacdangannhat = 0.
        self._soluongcaoboctacdan = 0

        self._is_tudongdaotangbaodo = False
        self._yeucaudaotangbaodo = None

        self._thoidiemdichuyendaotangbaodogannhat = 0.

        self._thoidiembuffkimchamgannhat_map = {}
        self._thoidiembuffnganchamgannhat_map = {}
        self._thoidiembuffcuongthethuatgannhat_map = {}

        self._is_nganchamdoachsansang = False
        self._is_kimchamdoachsansang = False
        self._is_cuongthethuatsansang = False

        self._idnguoichoibuffnganchamgannhat = 0
        self._idnguoichoibuffkimchamgannhat = 0
        self._idnguoichoibuffcuongthethuatgannhat = 0

    def __del__(self):
        try:
            self.moitruong.action_bochantangcapdo()
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass

    def luuthietlap(self, idnguoichoi):
        thietlap = {
            "_is_tudongbattheosaunhom": self._is_tudongbattheosaunhom,
            "_is_tudongtheosautruongnhom": self._is_tudongtheosautruongnhom,
            "_is_tudongtimkiemmuctieu": self._is_tudongtimkiemmuctieu,
            "_is_tudongsudungkynang": self._is_tudongsudungkynang,
            "_is_uutienmuctieupk": self._is_uutienmuctieupk,
            "_is_tudongsudungvatpham": self._is_tudongsudungvatpham,
            "_is_tudongnhatdo": self._is_tudongnhatdo,
            "_is_chidanhnguoichoi": self._is_chidanhnguoichoi,
            "_is_tudongtodoi": self._is_tudongtodoi,
            "_is_thucsondao": self._is_thucsondao,
            "_is_chantangcapdo": self._is_chantangcapdo,
            "_is_tudongdichuyendiemdanhxungquanh": self._is_tudongdichuyendiemdanhxungquanh,
            "_diemdanhxungquanhs": self._diemdanhxungquanhs,
            "_is_tudonggomquai": self._is_tudonggomquai,
            "_is_tudongvebanrac": self._is_tudongvebanrac,
            "_idbandofarmbanrac": self._idbandofarmbanrac,
            "_is_chedobufftoanbang": self._is_chedobufftoanbang,
            "_is_tudongdichientruong": self._is_tudongdichientruong,
            "_is_tudongkhaikhoang": self._is_tudongkhaikhoang,
            "_is_tudongdaotangbaodo": self._is_tudongdaotangbaodo,
            "_tenmuctieutancongs": self._tenmuctieutancongs,
        }
        util_luuthietlap(str(idnguoichoi), thietlap)

    def taithietlap(self, idnguoichoi):
        thietlap = util_taithietlap(str(idnguoichoi))
        if thietlap:
            if "_is_tudongbattheosaunhom" in thietlap:
                self._is_tudongbattheosaunhom = thietlap["_is_tudongbattheosaunhom"]

            if "_is_tudongtheosautruongnhom" in thietlap:
                self._is_tudongtheosautruongnhom = thietlap["_is_tudongtheosautruongnhom"]

            if "_is_tudongtimkiemmuctieu" in thietlap:
                self._is_tudongtimkiemmuctieu = thietlap["_is_tudongtimkiemmuctieu"]

            if "_is_tudongsudungkynang" in thietlap:
                self._is_tudongsudungkynang = thietlap["_is_tudongsudungkynang"]

            if "_is_uutienmuctieupk" in thietlap:
                self._is_uutienmuctieupk = thietlap["_is_uutienmuctieupk"]

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

            if "_is_tudongdichuyendiemdanhxungquanh" in thietlap:
                self._is_tudongdichuyendiemdanhxungquanh = thietlap["_is_tudongdichuyendiemdanhxungquanh"]

            if "_diemdanhxungquanhs" in thietlap:
                self._diemdanhxungquanhs = thietlap["_diemdanhxungquanhs"]

            if "_is_tudonggomquai" in thietlap:
                self._is_tudonggomquai = thietlap["_is_tudonggomquai"]

            if "_is_tudongvebanrac" in thietlap:
                self._is_tudongvebanrac = thietlap["_is_tudongvebanrac"]

            if "_idbandofarmbanrac" in thietlap:
                self._idbandofarmbanrac = thietlap["_idbandofarmbanrac"]

            if "_is_chedobufftoanbang" in thietlap:
                self._is_chedobufftoanbang = thietlap["_is_chedobufftoanbang"]

            if "_is_tudongdichientruong" in thietlap:
                self._is_tudongdichientruong = thietlap["_is_tudongdichientruong"]

            if "_is_tudongkhaikhoang" in thietlap:
                self._is_tudongkhaikhoang = thietlap["_is_tudongkhaikhoang"]

            if "_is_tudongdaotangbaodo" in thietlap:
                self._is_tudongdaotangbaodo = thietlap["_is_tudongdaotangbaodo"]

            if "_tenmuctieutancongs" in thietlap:
                self._tenmuctieutancongs = thietlap["_tenmuctieutancongs"]

    def _kiemtrathuchienvohieuhoadichuyen(self):
        if self._is_yeucauvohieuhoadichuyen:
            self.moitruong.action_vohieuhoadichuyen()
        else:
            self.moitruong.action_tatvohieuhoadichuyen()

    def action_xulydichuyenuutien(self):
        if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
            self._is_battudongtancongvatly = False

        self._kiemtrathuchienvohieuhoadichuyen()

        is_log = False
        if time.time() - self._thoidiemlogdebug > 2.0:
            is_log = True
            self._thoidiemlogdebug = time.time()

        is_log = False
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
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng để dùng SKILL")
            return
        if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT):
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng vì đang dùng SKILL")
            return
        if self._trangthaiveban != 0:
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng để về bán rác")
            return

        is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom()

        is_yeucaunhatdo = self._yeucaunhatdo and not is_anhhuongboitruongnhom

        is_maupkhoabinh = self.moitruong.get_idmaupk() == MAUPK_HOABINH

        if time.time() - self._thoidiemgapnguoichoigannhat < 30.0 and self.moitruong.get_idbandohientai() in BANDOFARMs and is_maupkhoabinh:
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Bắt gặp người chơi trên bản đồ cự thú đảo")
            return

        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieudangchonlanguoichoi = diachimuctieudangchon and self.moitruong.get_is_nguoichoi(diachimuctieudangchon)
        is_muctieudangchonlacuongthi = diachimuctieudangchon and CUONGTHI in self.moitruong.get_tendoituong(diachimuctieudangchon)
        is_muctieudangchonlabaothugiangho = diachimuctieudangchon and self.moitruong.get_is_baothugiangho(self.moitruong.get_tendoituong(diachimuctieudangchon))
        is_muctieupk = is_muctieudangchonlanguoichoi or is_muctieudangchonlacuongthi or is_muctieudangchonlabaothugiangho

        yeucauduocchon = None
        lydochon = "KHÔNG CÓ"

        if is_yeucaunhatdo and not is_muctieupk:
            yeucauduocchon = self._yeucaunhatdo
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
        elif self._yeucautancong:
            yeucauduocchon = self._yeucautancong
            lydochon = "TẤN CÔNG"
        elif self._yeucautheonhom:
            yeucauduocchon = self._yeucautheonhom
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
            x_truongnhom = self.moitruong.get_toadoxtruongnhom()
            y_truongnhom = self.moitruong.get_toadoytruongnhom()

            if x_truongnhom and y_truongnhom:
                x_muctieu, y_muctieu = None, None
                toadodich_ = yeucauduocchon.get("toadodich")
                diachimuctieu_ = diachimuctieudanggom

                if toadodich_:
                    x_muctieu, y_muctieu = toadodich_
                elif diachimuctieu_:
                    x_muctieu = self.moitruong.get_toadox(diachimuctieu_, is_vitrihientai = True)
                    y_muctieu = self.moitruong.get_toadoy(diachimuctieu_, is_vitrihientai = True)

                if x_muctieu and y_muctieu:
                    khoangcachmuctieuvatruongnhom = math.dist((x_muctieu, y_muctieu), (x_truongnhom, y_truongnhom))
                    khoangcachtoidatruongnhom = self._tinhtoankhoangcachtoidatruongnhomphuhop() - 1.5

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

        if iddoituongmuctieudanggom > 0:
            if iddoituongmuctieudanggom != self._idmuctieudangtheokiemtraket or self.moitruong.get_is_dangvankhi():
                self._idmuctieudangtheokiemtraket = iddoituongmuctieudanggom
                self._thoidiemdungimkiemtraket = time.time()
                self._toadokiemtraket = (self.moitruong.get_toadox(is_vitrihientai = True), self.moitruong.get_toadoy(is_vitrihientai = True))
                self._thoidiembatdaukiemtraket = time.time()
            else:
                curr_x = self.moitruong.get_toadox(is_vitrihientai = True)
                curr_y = self.moitruong.get_toadoy(is_vitrihientai = True)

                khoangcachdadichuyen = math.dist((curr_x, curr_y), self._toadokiemtraket)

                if time.time() - self._thoidiembatdaukiemtraket > 3.0:
                    if khoangcachdadichuyen < 1.0:
                        is_quai = False
                        if diachimuctieudanggom:
                            if self.moitruong.get_is_nhanvattontai(diachimuctieudanggom) and self.moitruong.get_idloainhanvat(diachimuctieudanggom) == LOAIMUCTIEU_QUAIVATHOACNPC:
                                is_quai = True

                        if is_quai:
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

            kieudichuyen = yeucauduocchon.get("kieudichuyen", KIEUDICHUYEN_GIUKHOANGCACHTOIDA)

            if kieudichuyen == KIEUDICHUYEN_GIUKHOANGCACHTOIDA:
                khoangcachtoida = yeucauduocchon.get("khoangcachtoida", 0.0)
                if toadodich:
                    self.moitruong.action_dichuyengiukhoangcachtoidadiem(
                        toadodich[0],
                        toadodich[1],
                        khoangcachtoida,
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
            if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT):
                break

            if self._is_tudongbattheosaunhom and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THEOSAUNHOM,), True, is_hieuungcoloi = 1):
                self.moitruong.action_battheosaunhom(3.)

            xtruongnhom = self.moitruong.get_toadoxtruongnhom()
            ytruongnhom = self.moitruong.get_toadoytruongnhom()

            if not xtruongnhom and not ytruongnhom:
                break

            khoangcachtruongnhom = self.moitruong.get_khoangcachdiem(xtruongnhom, ytruongnhom)
            khoangcachtoidatruongnhom = self._tinhtoankhoangcachtoidatruongnhomphuhop()

            if khoangcachtruongnhom <= khoangcachtoidatruongnhom:
                break
            if khoangcachtruongnhom >= KHOANGCACHTOIDAHOPLE:
                break

            self._yeucautheonhom = {
                "yeucau": YEUCAUDICHUYENTHEONHOM,
                "toadodich": (xtruongnhom, ytruongnhom),
                "khoangcachtoida": max(0, khoangcachtoidatruongnhom - 1.5)
            }
            break
        return

    def _tinhtoankhoangcachtoidatruongnhomphuhop(self):
        khoangcachtoidatruongnhom = self._khoangcachtoidatruongnhom
        diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon) or CUONGTHI not in self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon):
            khoangcachtoidatruongnhom -= 1.5
        return khoangcachtoidatruongnhom

    def _kiemtra_vungcam(self, x, y):
        idbandohientai = self.moitruong.get_idbandohientai()
        if idbandohientai in VUNGCAM_MAP:
            danhsachvungcam = VUNGCAM_MAP[idbandohientai]
            for vung in danhsachvungcam:
                if vung["type"] == "circle":
                    if math.dist((x, y), (vung["x"], vung["y"])) <= vung["r"]:
                        return True
                elif vung["type"] == "line":
                    if self._tinhkhoangcachdendoanthang(x, y, vung["x1"], vung["y1"], vung["x2"], vung["y2"]) <= vung["r"]:
                        return True
        return False

    def action_tudongtimkiemmuctieu(self):
        if not self._is_tudongtimkiemmuctieu:
            return

        def _thaydoimuctieu(diachimuctieu):
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachimuctieu)
            self.moitruong._thoidiemtuthenhanvatdungimcomuctieugannhat = time.time()
            self._is_battudongtancongvatly = False

        idbandohientai = self.moitruong.get_idbandohientai()
        if idbandohientai != self._idbandomuctieudangchon:
            self._idbandomuctieudangchon = idbandohientai
            self._diachicosomuctieuduphong = 0
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)

        if self._diachicosonhanvatmuctieudangdichuyenkhaithien > 0:
            if time.time() - self._thoidiembatdaudichuyenkhaithien > 1.5:
                self._diachicosonhanvatmuctieudangdichuyenkhaithien = 0
            else:
                if self.moitruong.get_is_nhanvattontai(self._diachicosonhanvatmuctieudangdichuyenkhaithien) and not self.moitruong.get_is_nhanvatdachet(self._diachicosonhanvatmuctieudangdichuyenkhaithien):
                    if self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon() != self._diachicosonhanvatmuctieudangdichuyenkhaithien:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(self._diachicosonhanvatmuctieudangdichuyenkhaithien)
                    return
                else:
                    self._diachicosonhanvatmuctieudangdichuyenkhaithien = 0

        vungdabichiemdongs = []
        if self._is_tudongvebanrac:
            idnhanvathientai = self.moitruong.get_idnguoichoi()
            idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
            index_bot = -1
            while True:
                index_bot += 1
                diachidoituongbotxemxet = self.moitruong.get_diachicosothongtindoituongx(index_bot)
                if not diachidoituongbotxemxet: break
                idnguoichoibot = self.moitruong.get_idnguoichoi(diachidoituongbotxemxet)
                if idnguoichoibot in NHANVATCUAMINHs and idnguoichoibot != idnhanvathientai:
                    if not idnguoichoithanhviennhoms or idnguoichoibot not in idnguoichoithanhviennhoms:
                        vungdabichiemdongs.append({
                            "x": self.moitruong.get_toadox(diachidoituongbotxemxet),
                            "y": self.moitruong.get_toadoy(diachidoituongbotxemxet)
                        })

        thoidiemhientai = time.time()
        idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if thoidiemhientai - v > 120]
        for k in idcanxoas:
            del self._idmuctieubiloi_map[k]

        diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_bandokhongpk = idbandohientai in BANDOKHONGPKs

        diachinhanvatmuctieudemquaixungquanh = diachicosothongtinnhanvatmuctieudangchon

        thongtinmuctieuhientai = {
            "diachi": diachicosothongtinnhanvatmuctieudangchon,
            "is_hople": False,
            "is_muctieupk": False,
            "is_nguoichoi": False,
            "is_baothugiangho": False,
            "is_cuongthi": False,
            "ten": ""
        }

        if diachicosothongtinnhanvatmuctieudangchon:
            tendoituongmuctieudangchon = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)
            is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
            is_muctieudangchonlacuongthi = CUONGTHI in tendoituongmuctieudangchon
            is_muctieudangchonlabaothugiangho = self.moitruong.get_is_baothugiangho(tendoituongmuctieudangchon)
            is_muctieupk = is_muctieudangchonlanguoichoi or is_muctieudangchonlacuongthi or is_muctieudangchonlabaothugiangho

            thongtinmuctieuhientai["ten"] = tendoituongmuctieudangchon
            thongtinmuctieuhientai["is_nguoichoi"] = is_muctieudangchonlanguoichoi
            thongtinmuctieuhientai["is_muctieupk"] = is_muctieupk
            thongtinmuctieuhientai["is_cuongthi"] = is_muctieudangchonlacuongthi
            thongtinmuctieuhientai["is_baothugiangho"] = is_muctieudangchonlabaothugiangho

            is_boquamuctieuhientai = False

            if is_bandokhongpk and is_muctieupk:
                is_boquamuctieuhientai = True
            elif not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                is_boquamuctieuhientai = True
            elif tendoituongmuctieudangchon in TENMUCTIEUKHONGTANCONGs:
                is_boquamuctieuhientai = True
            elif self._is_chidanhnguoichoi and not is_muctieupk:
                is_boquamuctieuhientai = True
            elif self._tenmuctieutancongs and tendoituongmuctieudangchon not in self._tenmuctieutancongs:
                is_boquamuctieuhientai = True
            elif self._tenmuctieukhongtancongs and tendoituongmuctieudangchon in self._tenmuctieukhongtancongs:
                is_boquamuctieuhientai = True
            elif is_muctieudangchonlacuongthi and TENNGUOICHOICUNGBANGs and any("( {} )".format(n) in tendoituongmuctieudangchon for n in TENNGUOICHOICUNGBANGs):
                is_boquamuctieuhientai = True
            elif self.moitruong.get_idmaupk() == MAUPK_HOABINH and is_muctieupk:
                is_boquamuctieuhientai = True
            elif self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                is_boquamuctieuhientai = True
            if not is_boquamuctieuhientai and self._is_tudongvebanrac:
                if self._idbandofarmbanrac and idbandohientai != self._idbandofarmbanrac:
                    is_boquamuctieuhientai = True
                if not is_boquamuctieuhientai:
                    toadox = self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieudangchon)
                    toadoy = self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieudangchon)
                    if self._kiemtra_vungcam(toadox, toadoy):
                        is_boquamuctieuhientai = True

                    if not is_boquamuctieuhientai and vungdabichiemdongs:
                        khoangcachhientai = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                        for vung in vungdabichiemdongs:
                            if math.dist((toadox, toadoy), (vung["x"], vung["y"])) <= 9.0 and khoangcachhientai > math.dist((toadox, toadoy), (vung["x"], vung["y"])):
                                is_boquamuctieuhientai = True
                                break

            if is_boquamuctieuhientai:
                _thaydoimuctieu(0)
                diachicosothongtinnhanvatmuctieudangchon = 0
                diachinhanvatmuctieudemquaixungquanh = 0
                thongtinmuctieuhientai["diachi"] = 0
            else:
                thongtinmuctieuhientai["is_hople"] = True

        if not diachicosothongtinnhanvatmuctieudangchon and self._diachicosomuctieuduphong:
            if self.moitruong.get_is_nhanvattontai(self._diachicosomuctieuduphong) and self.moitruong.get_is_cothetancong(self._diachicosomuctieuduphong) and self.moitruong.get_khoangcach(self._diachicosomuctieuduphong) < KHOANGCACHTOANMANHINH:
                _thaydoimuctieu(self._diachicosomuctieuduphong)
                diachicosothongtinnhanvatmuctieudangchon = self._diachicosomuctieuduphong
                diachinhanvatmuctieudemquaixungquanh = self._diachicosomuctieuduphong
                self._diachicosomuctieuduphong = 0
            else:
                self._diachicosomuctieuduphong = 0

        iii = 0
        demmuctieugan3 = 0
        demmuctieugan5 = 0
        demmuctieugan7 = 0
        demmuctieugan9 = 0

        diachicosothongtinnhanvattruongnhom = self.moitruong.get_diachicosothongtinnhanvattruongnhom()
        is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom() and diachicosothongtinnhanvattruongnhom

        khoangcachtimkiem = self._khoangcachtimkiemmuctieu

        while True:
            diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(iii)
            if not diachicosothongtinnhanvatmuctieuxemxet:
                break
            iii += 1

            khoangcachmuctieuxemxettoitruongnhom = 0

            khoangcachmuctieuxemxettoibanthan = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet)
            if khoangcachmuctieuxemxettoibanthan > khoangcachtimkiem:
                continue

            iddoituongmuctieuxemxet = self.moitruong.get_iddoituong(diachicosothongtinnhanvatmuctieuxemxet)
            if iddoituongmuctieuxemxet in self._idmuctieubiloi_map:
                continue

            tendoituongmuctieuxemxet = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet)
            is_muctieuxemxetlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieuxemxet)

            if self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                if thoidiemhientai - self._thoidiemphatamanthan > 5.0 and is_muctieuxemxetlanguoichoi:
                    if self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatmuctieuxemxet) and diachicosothongtinnhanvatmuctieuxemxet != self.moitruong.get_diachicosothongtinnhanvat1() and self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatmuctieuxemxet) not in NHANVATCUAMINHs:
                        phatam("{} Có thích khách: {}".format(self.moitruong.get_tendoituong(), tendoituongmuctieuxemxet))
                        self._thoidiemphatamanthan = thoidiemhientai

            if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieuxemxet):
                continue

            if tendoituongmuctieuxemxet in TENMUCTIEUKHONGTANCONGs:
                continue
            if self._tenmuctieutancongs and tendoituongmuctieuxemxet not in self._tenmuctieutancongs:
                continue
            if self._tenmuctieukhongtancongs and tendoituongmuctieuxemxet in self._tenmuctieukhongtancongs:
                continue

            is_muctieuxemxetlacuongthi = CUONGTHI in tendoituongmuctieuxemxet
            is_muctieuxemxetlabaothugiangho = self.moitruong.get_is_baothugiangho(tendoituongmuctieuxemxet)
            is_muctieuxemxetpk = is_muctieuxemxetlanguoichoi or is_muctieuxemxetlacuongthi or is_muctieuxemxetlabaothugiangho

            if self._is_tudongvebanrac and self._idbandofarmbanrac and idbandohientai != self._idbandofarmbanrac:
                continue
            if is_muctieuxemxetlacuongthi and TENNGUOICHOICUNGBANGs and any("( {} )".format(n) in tendoituongmuctieuxemxet for n in TENNGUOICHOICUNGBANGs):
                continue
            if self._is_chidanhnguoichoi and not is_muctieuxemxetpk:
                continue
            if is_bandokhongpk and is_muctieuxemxetpk:
                continue

            if self._is_tudongvebanrac:
                toadox, toadoy = self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieuxemxet), self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieuxemxet)
                if self._kiemtra_vungcam(toadox, toadoy):
                    continue
                if vungdabichiemdongs:
                    is_cobotcanhtranh = False
                    for vung in vungdabichiemdongs:
                        if math.dist((toadox, toadoy), (vung["x"], vung["y"])) <= 9.0 and khoangcachmuctieuxemxettoibanthan > math.dist((toadox, toadoy), (vung["x"], vung["y"])):
                            is_cobotcanhtranh = True
                            break
                    if is_cobotcanhtranh:
                        continue

            if is_anhhuongboitruongnhom:
                khoangcachmuctieuxemxettoitruongnhom = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet, diachicosothongtinnhanvattruongnhom)
                if khoangcachmuctieuxemxettoitruongnhom >= khoangcachtimkiem: continue
            else:
                if khoangcachmuctieuxemxettoibanthan >= khoangcachtimkiem: continue

            khoangcachmuctieuxemxettoimuctieudemquaixungquanh = khoangcachmuctieuxemxettoibanthan
            if diachinhanvatmuctieudemquaixungquanh:
                khoangcachmuctieuxemxettoimuctieudemquaixungquanh = self.moitruong.get_khoangcach(
                    diachicosothongtinnhanvatmuctieuxemxet,
                    diachinhanvatmuctieudemquaixungquanh
                )

            if khoangcachmuctieuxemxettoimuctieudemquaixungquanh <= 9.0:
                if khoangcachmuctieuxemxettoimuctieudemquaixungquanh <= 3.0:
                    demmuctieugan3 += 1
                if khoangcachmuctieuxemxettoimuctieudemquaixungquanh <= 5.0:
                    demmuctieugan5 += 1
                if khoangcachmuctieuxemxettoimuctieudemquaixungquanh <= 7.0:
                    demmuctieugan7 += 1
                demmuctieugan9 += 1

            if is_muctieuxemxetlanguoichoi and self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatmuctieuxemxet) and self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatmuctieuxemxet) not in NHANVATCUAMINHs and khoangcachmuctieuxemxettoibanthan <= khoangcachtimkiem and not self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatmuctieuxemxet):
                self._thoidiemgapnguoichoigannhat = thoidiemhientai

            if diachicosothongtinnhanvatmuctieuxemxet == diachicosothongtinnhanvatmuctieudangchon:
                continue

            if self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                continue

            def _thaydoimuctieutrongvonglap():
                if diachicosothongtinnhanvatmuctieudangchon:
                    self._diachicosomuctieuduphong = diachicosothongtinnhanvatmuctieudangchon
                _thaydoimuctieu(diachicosothongtinnhanvatmuctieuxemxet)

            if not thongtinmuctieuhientai["is_hople"]:
                _thaydoimuctieutrongvonglap()
                thongtinmuctieuhientai["is_hople"] = True
                thongtinmuctieuhientai["is_muctieupk"] = is_muctieuxemxetpk
                thongtinmuctieuhientai["is_nguoichoi"] = is_muctieuxemxetlanguoichoi
                thongtinmuctieuhientai["is_cuongthi"] = is_muctieuxemxetlacuongthi
                thongtinmuctieuhientai["is_baothugiangho"] = is_muctieuxemxetlabaothugiangho
                thongtinmuctieuhientai["ten"] = tendoituongmuctieuxemxet
                diachicosothongtinnhanvatmuctieudangchon = diachicosothongtinnhanvatmuctieuxemxet
                continue

            is_muctieuhientailamuctieupk = thongtinmuctieuhientai["is_muctieupk"]
            is_muctieuhientailacuongthi = thongtinmuctieuhientai["is_cuongthi"]
            is_muctieuhientailabaothugiangho = thongtinmuctieuhientai["is_baothugiangho"]
            is_muctieuhientailanguoichoi = thongtinmuctieuhientai["is_nguoichoi"]

            if self._is_uutienbaothumaoson:
                if is_muctieuxemxetlacuongthi and not is_muctieuhientailacuongthi:
                    _thaydoimuctieutrongvonglap()
                    continue
                elif is_muctieuhientailacuongthi and not is_muctieuxemxetlacuongthi:
                    continue

            if self._is_khonguutienbaothugiangho and not self.moitruong.get_is_nhanvatbichoang():
                if (is_muctieuxemxetlanguoichoi or is_muctieuxemxetlacuongthi) and is_muctieuhientailabaothugiangho:
                    _thaydoimuctieutrongvonglap()
                    continue
                elif (is_muctieuhientailanguoichoi or is_muctieuhientailacuongthi) and is_muctieuxemxetlabaothugiangho:
                    continue

            if self._is_uutienmuctieupk:
                if is_muctieuxemxetpk and not is_muctieuhientailamuctieupk:
                    _thaydoimuctieutrongvonglap()
                    continue
                elif is_muctieuhientailamuctieupk and not is_muctieuxemxetpk:
                    continue

            if is_muctieuxemxetpk and is_muctieuhientailamuctieupk:
                phantramsinhlucmuctieuhientai = self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieudangchon)

                is_muctieuhientaicohieuungbattu = False
                if phantramsinhlucmuctieuhientai <= 5:
                    is_muctieuhientaicohieuungbattu = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1)

                phantramsinhlucmuctieuxemxet = self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieuxemxet)
                is_muctieuxemxetcohieuungbattu = False
                if phantramsinhlucmuctieuxemxet <= 5:
                    is_muctieuxemxetcohieuungbattu = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1)

                is_vanmongcoc = self.moitruong.get_tenmonphai() == "vanmongcoc"

                if not is_vanmongcoc and is_muctieuhientaicohieuungbattu and (phantramsinhlucmuctieuxemxet > 5 or not is_muctieuxemxetcohieuungbattu):
                    _thaydoimuctieutrongvonglap()
                    continue

            if is_anhhuongboitruongnhom:
                khoangcachxemxetmuctieuxemxet = khoangcachmuctieuxemxettoitruongnhom
                khoangcachxemxetmuctieuhientai = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon, diachicosothongtinnhanvattruongnhom)
            else:
                khoangcachxemxetmuctieuxemxet = khoangcachmuctieuxemxettoibanthan
                khoangcachxemxetmuctieuhientai = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

            if khoangcachxemxetmuctieuxemxet < khoangcachxemxetmuctieuhientai:
                _thaydoimuctieutrongvonglap()

                diachicosothongtinnhanvatmuctieudangchon = diachicosothongtinnhanvatmuctieuxemxet

                thongtinmuctieuhientai["ten"] = tendoituongmuctieuxemxet
                thongtinmuctieuhientai["is_muctieupk"] = is_muctieuxemxetpk
                thongtinmuctieuhientai["is_nguoichoi"] = is_muctieuxemxetlanguoichoi
                thongtinmuctieuhientai["is_cuongthi"] = is_muctieuxemxetlacuongthi
                thongtinmuctieuhientai["is_baothugiangho"] = is_muctieuxemxetlabaothugiangho

                demmuctieugan3 = 0
                demmuctieugan5 = 0
                demmuctieugan7 = 0
                demmuctieugan9 = 0

                diachinhanvatmuctieudemquaixungquanh = diachicosothongtinnhanvatmuctieudangchon
                continue

        self._is_nhieumuctieugan3 = demmuctieugan3 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan5 = demmuctieugan5 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan7 = demmuctieugan7 >= self._soluongnhieumuctieu
        self._is_nhieumuctieugan9 = demmuctieugan9 >= self._soluongnhieumuctieu

    def action_tudongsudungvatpham(self):
        if self._is_tudongsudungvatpham:
            if self.moitruong.get_is_nhanvatdachet():
                return

            noidungtrochuyen = self.moitruong.get_noidungtrochuyenmoinhat()
            if noidungtrochuyen and ("Hành động" in noidungtrochuyen or "Đợi lệnh" in noidungtrochuyen):
                self._is_dasudungbaothuvatpham = True
            if not self._is_dasudungbaothuvatpham and time.time() - self._thoidiemsudungbaothuvatphamgannhat < 1.5 and time.time() - self._thoidiemyeucaubaothuvatphamdoilenhgannhat > 0.25:
                self._thoidiemtamngungsudungkynang = time.time() + 0.5
                self._thoidiemyeucaubaothuvatphamdoilenhgannhat = time.time()
                self.moitruong.action_thucthicaulenh("pf 4131.@", delay = 0.)

            if not self._is_dasudungbaothuvatpham and time.time() - self._thoidiemsudungbaothuvatphamgannhat > 1.5:
                for baothuvatpham in BAOTHUVATPHAMs:
                    if self.action_sudungvatphamhanhtrang(baothuvatpham, delay = 0.):
                        self._thoidiemsudungbaothuvatphamgannhat = time.time()
                        break

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

            is_bandokhongpk = self.moitruong.get_idbandohientai() not in BANDOKHONGPKs
            if time.time() - self._thoidiemkiemtrahieuunggannhat > 2.5:
                self._thoidiemkiemtrahieuunggannhat = time.time()

                if ((is_bandokhongpk and self.moitruong.get_phantramnoilucconlai() < 25.) or (not is_bandokhongpk and self.moitruong.get_phantramnoilucconlai() < 75.)) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHAPLUCTHACH,), True, is_hieuungcoloi = 1):
                    if not self.moitruong.action_timkiemvatphamhanhtrang(TIEUPHAPLUCTHACH):
                        pass
                    else:
                        self.action_sudungvatphamhanhtrang(TIEUPHAPLUCTHACH)

                if self.moitruong.get_tenmonphai() in ("camvequan", "daohoanguyen", "duongmon") and is_bandokhongpk and self.moitruong.get_phantramsinhlucconlai() < 75. and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HUYETTHACH,), True, is_hieuungcoloi = 1):
                    if not self.moitruong.action_timkiemvatphamhanhtrang(TIEUHUYETTHACH):
                        pass
                    else:
                        self.action_sudungvatphamhanhtrang(TIEUHUYETTHACH)

                if diachicosothongtinnhanvatmuctieudangchon and is_bandokhongpk and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if self.moitruong.get_tenmonphai() == "camvequan" and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIENNGUYENDON,), macdinh = True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(THIENNGUYENDON)

            if self.moitruong.get_diempk() > 0:
                if not self.moitruong.action_timkiemvatphamhanhtrang(ANXAPHU):
                    pass
                else:
                    self.action_sudungvatphamhanhtrang(ANXAPHU)

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
            if self._is_tudongsudungkynang and is_bandokhongpk and time.time() - self._thoidiemsudungsotriduocgannhat > 5. and self.moitruong.get_idmaupk() != MAUPK_HOABINH and phantramsinhlucconlai <= 75:
                if not self.action_sudungvatphamhanhtrang(CAPCUUDON, delay = 0.):
                    self.action_sudungvatphamhanhtrang(HOATLACHOAN, delay = 0.)
                self._thoidiemsudungsotriduocgannhat = time.time()

            if self._is_tudongsudungkynang and self.moitruong.get_idbandohientai() == 395 and time.time() - self._thoidiemsudungsotriduocgannhat > 2. and phantramsinhlucconlai <= 25:
                self._thoidiemsudungsotriduocgannhat = time.time()
                if not self.action_sudungvatphamhanhtrang(CAPCUUDON, delay = 0.):
                    self.action_sudungvatphamhanhtrang(HOATLACHOAN, delay = 0.)

            if self.moitruong.get_idnguoichoi() == 4599:
                if time.time() - self._thoidiemsudungtusamdongannhat > 30.:
                    if self.action_sudungvatphamhanhtrang(TUSAMDON):
                        self._thoidiemsudungtusamdongannhat = time.time()

                if time.time() - self._thoidiemdocsachgannhat > 30.:
                    sachcanhocs = [
                        "Nhập Môn Mãn Thiên Hoa Vũ",
                        "Nhập Môn Đường Môn Tâm",
                        "Nhập Môn Lạc Tuyết Vô Ngân",
                        "Nhập Môn Cực Tà Sát Phá"
                    ]
                    for sachcanhoc in sachcanhocs:
                        if self.action_sudungvatphamhanhtrang(sachcanhoc):
                            self._thoidiemdocsachgannhat = time.time()
                            break

    def action_xulyuutiensudungkynang(self, loaikynang, vitrikynang, diachimuctieu, khoangcachyeucau = 0, is_ngatdichuyen = False):
        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        thoigiandungim = 0.
        if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
            thoigiandungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0.

        if is_ngatdichuyen and idtuthenhanvat == TUTHENHANVAT_DICHUYEN:
            self.moitruong.action_ngatdichuyen()
            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.1)

        if loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynangphudau", "sudungkynanglendongdoi") and diachimuctieu:
            if khoangcach > khoangcachyeucau:
                return False

        if loaikynang == "dichuyentiepcancanchien":
            self._yeucautancong = {
                "yeucau": YEUCAUDICHUYENTANCONG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                "diachimuctieu": diachimuctieu,
                "khoangcachtoida": max(0, KHOANGCACHSUDUNGKYNANGCANCHIEN - thoigiandungim)
            }
            return True

        elif loaikynang == "dichuyengiukhoangcach":
            self._yeucautancong = {
                "yeucau": YEUCAUDICHUYENTANCONG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                "diachimuctieu": diachimuctieu,
                "khoangcach": khoangcachyeucau
            }
            return True
        elif loaikynang == "dichuyentiepcantamxa":
            nguongantoan = khoangcachyeucau - (2.5 + thoigiandungim)
            if khoangcach >= nguongantoan:
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    "khoangcachtoida": 0,
                }
                return True
            return False

        if loaikynang == "battathieuungphapbao":
            self.moitruong.action_thucthicaulenh("pf2 908.6", delay = 0.)
            self._thoidiembattathieuungphapbaogannhat = time.time()

        elif loaikynang == "sudungcaoboctacdan":
            if diachimuctieu:
                iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN)
                if iddoituongvatpham:
                    if self.moitruong.get_is_nguoichoi(diachimuctieu):
                        caulenh = "use {}# for {}".format(hex(iddoituongvatpham).replace("0x", ""), self.moitruong.get_idnguoichoi(diachimuctieu))
                    else:
                        caulenh = "use {}# for {}#".format(hex(iddoituongvatpham).replace("0x", ""), hex(self.moitruong.get_iddoituong(diachimuctieu)).replace("0x", ""))
                    if self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0):
                        self._thoidiemsudungcaoboctacdangannhat = time.time()
        else:
            offset = random.uniform(0, 1.0) if loaikynang == "sudungkynangphudau" else 0
            if loaikynang == "sudungkynangkhongmuctieu":
                self.moitruong.action_sudungkynangvitri(*vitrikynang)
            elif loaikynang == "sudungkynanglenbanthan":
                self.moitruong.action_sudungkynangvitrilenbanthan(*vitrikynang)
            elif loaikynang == "tancongvatly":
                if self.moitruong.action_sudungtancongvatly(diachimuctieu):
                    self._is_battudongtancongvatly = True
            elif loaikynang == "sudungkynangmuctieu":
                self.moitruong.action_sudungkynangvitrimuctieu(*vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu)
            elif loaikynang == "sudungkynanglendongdoi":
                self.moitruong.action_sudungkynangvitrimuctieu(*vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu, is_khongkiemtracothetancong = True)
            elif loaikynang == "sudungkynangphudau":
                self.moitruong.action_sudungkynangvitriphudau(*vitrikynang, diachicosothongtinnhanvat2 = diachimuctieu, khoangcachphudau = offset)

        if is_ngatdichuyen:
            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.1)
            self._yeucautancong = None

        return True

    def _action_tancong_duongmon(self):
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

        is_muctieusudungphapluc = diachimuctieu and self.moitruong.get_idloaivukhi(diachimuctieu) in (LOAIVUKHI_KIEM, LOAIVUKHI_AMKHI)
        is_muctieulacuongthi = diachimuctieu and CUONGTHI in self.moitruong.get_tendoituong(diachimuctieu)
        is_muctieulabaothugiangho = diachimuctieu and self.moitruong.get_is_baothugiangho(self.moitruong.get_tendoituong(diachimuctieu))
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        is_muctieugiukhoangcach = is_muctieulanguoichoi and self.moitruong.get_idloaivukhi(diachimuctieu) not in (LOAIVUKHI_KIEM, LOAIVUKHI_AMKHI)
        is_muctieupk = is_muctieulanguoichoi or is_muctieulacuongthi or is_muctieulabaothugiangho

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        is_anthan = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = True, is_hieuungcoloi = 1)
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
            (None, "dichuyentiepcantamxa", lambda: not is_bidaohoalacanh and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
            (VITRIKYNANG_NHIEPHONCHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and is_muctieupk and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "tancongvatly", lambda: diachimuctieu and not self._is_battudongtancongvatly, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and self._is_nhieumuctieugan5 and not is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_SONGLONGDOATCHAU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and (is_muctieupk or is_bandochientruong) and not is_muctieucomatamthuat, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and self._is_nhieumuctieugan5 and is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and not is_muctieucomatamthuat and is_muctieulanguoichoi and is_muctieusudungphapluc and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HAPTINHMACHAM,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_MAIHOACHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_AMKICH, "sudungkynangmuctieu", lambda: not is_bidaohoalacanh and noilucconlai > 50 and diachimuctieu and not is_muctieucomatamthuat and (is_muctieugiukhoangcach or is_bituocvukhi), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "sudungcaoboctacdan", lambda: self.moitruong.get_idbandohientai() != 885 and diachimuctieu and is_muctieulanguoichoi and time.time() - self._thoidiemsudungcaoboctacdangannhat > 30. and self.moitruong.action_timkiemvatphamhanhtrang(CAOBOCTACDAN), KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
            (VITRIKYNANG_THICHSAT, "sudungkynangmuctieu", lambda: not is_bidaohoalacanh and noilucconlai > 50 and diachimuctieu and not is_muctieucomatamthuat and (is_muctieugiukhoangcach or is_bituocvukhi), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (None, "dichuyengiukhoangcach", lambda: not is_bidaohoalacanh and diachimuctieu and is_muctieugiukhoangcach and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5, khoangcach + 3., None, False),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "tancongvatly", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngatdichuyen = item

            if callable(dieukien) and not dieukien():
                continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang):
                continue

            target = target if target else diachimuctieu

            is_ok = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_ngatdichuyen = is_ngatdichuyen
            )
            if is_ok:
                return

    def _action_tancong_daohoanguyen(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        is_muctieulacuongthi = diachimuctieu and CUONGTHI in self.moitruong.get_tendoituong(diachimuctieu)
        is_muctieulabaothugiangho = diachimuctieu and self.moitruong.get_is_baothugiangho(self.moitruong.get_tendoituong(diachimuctieu))
        is_muctieupk = is_muctieulanguoichoi or is_muctieulacuongthi or is_muctieulabaothugiangho
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai()

        diachidongdoicanbuff = None
        if not diachimuctieu and self.moitruong.get_is_dangnamtrongnhom():
            j = -1
            idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
            while True:
                j += 1
                diachixemxet = self.moitruong.get_diachicosothongtindoituongx(j)
                if not diachixemxet: break
                if not self.moitruong.get_is_nhanvattontai(diachixemxet): continue

                idnguoichoi = self.moitruong.get_idnguoichoi(diachixemxet)
                if not idnguoichoi: continue

                if idnguoichoi in idnguoichoithanhviennhoms and self.moitruong.get_khoangcach(diachixemxet) <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if not self.moitruong.get_is_nhanvatdachet(diachixemxet):
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), diachicosothongtinnhanvat = diachixemxet, macdinh = True, is_hieuungcoloi = 1):
                            diachidongdoicanbuff = diachixemxet
                            break

        danhsachuutien = [
            (VITRIKYNANG_TRANCOTHANUY, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_TRANCOTHANUY] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRANCOTHANUY,), True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_KIMTRUNGCHAO, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KIMTRUNGCHAO] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), True, is_hieuungcoloi = 1) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMTRUNGCHAO,), True, is_hieuungcoloi = 1), 0, None, True),
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglenbanthan", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_HOTHEKIMCANG] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), True, is_hieuungcoloi = 1), 0, None, True),
            (VIRIKYNANG_NGUYENKHIQUYNGUYEN, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_NGUYENKHIQUYNGUYEN] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGUYENKHIQUYNGUYEN,), True, is_hieuungcoloi = 1), 0, None, True),
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglendongdoi", lambda: diachidongdoicanbuff and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_HOTHEKIMCANG], KHOANGCACHSUDUNGKYNANGTAMXA, diachidongdoicanbuff, False),

            (VITRIKYNANG_KHONGTHUNHAPBACHNHAN, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieupk and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KHONGTHUNHAPBACHNHAN] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_DAIHAIVOLUONG, "sudungkynangkhongmuctieu", lambda: diachimuctieu and self._is_nhieumuctieugan3 and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAIHAIVOLUONG] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, False),
            (VITRIKYNANG_DAOHOALACANH, "sudungkynangkhongmuctieu", lambda: khoangcach < KHOANGCACHSUDUNGKYNANGCANCHIEN and diachimuctieu and is_muctieupk and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAOHOALACANH] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_THONKINH, "sudungkynangmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_THONKINH] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_LACKICH, "sudungkynangmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_LACKICH] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACKICH,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_PHONGMAQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieupk and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_PHONGMAQUYET] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_NHATQUYENBATSON, "sudungkynangmuctieu", lambda: diachimuctieu and self.moitruong.get_capdonhanvat() >= 60 and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_NHATQUYENBATSON] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and (is_muctieupk or not self._is_nhieumuctieugan3), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_HACHODAOTAM, "sudungkynangmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_HACHODAOTAM] and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and diachimuctieu != self.moitruong.get_diachicosothongtinnhanvat1(), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_BADONGQUYEN, "sudungkynangmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_BADONGQUYEN] and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN and idtuthenhanvat == TUTHENHANVAT_DICHUYEN and is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA - 3, None, False),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False),
            (None, "tancongvatly", lambda: diachimuctieu and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngatdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            target = target if target else diachimuctieu

            is_ok = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_ngatdichuyen = is_ngatdichuyen
            )

            if is_ok:
                return

    def _action_tancong_camvequan(self):
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
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngatdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            target = target if target else diachimuctieu

            is_ok = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_ngatdichuyen = is_ngatdichuyen
            )
            if is_ok:
                return

    def _action_tancong_vanmongcoc(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        idnguoichoi = self.moitruong.get_idnguoichoi()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)

        diachidoituongcanhoisinh = None
        diachidoituongcanbufftaytranquyet = None
        diachidoituongcanbommau = None
        phantramsinhlucthapnhat = 100.

        diachidoituongcanhoisinhduphong = None
        diachidoituongcanbufftaytranquyetduphong = None
        diachidoituongcanbommauduphong = None
        phantramsinhlucthapnhatduphong = 100.

        diachidoituongcanbuffkimcham = None
        diachidoituongcanbuffngancham = None
        diachidoituongcanbuffcuongthethuat = None

        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

        danhsachungviens = []
        danhsachungviens.append((0, self.moitruong.get_diachicosothongtinnhanvat1()))

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
            if self.moitruong.get_khoangcach(diachidoituongdangxemxet) >= KHOANGCACHSUDUNGKYNANGTAMXA - 3.:
                continue

            priority = -1
            if self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet):
                idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
                if idnguoichoidangxemxet == idnguoichoi:
                    continue
                if idnguoichoithanhviennhoms and idnguoichoidangxemxet in idnguoichoithanhviennhoms:
                    priority = 1
                elif idnguoichoidangxemxet in NHANVATCUNGBANGs:
                    priority = 2
            elif "(TieuLyPhiDao)" in self.moitruong.get_tendoituong(diachidoituongdangxemxet) and 4599 in idnguoichoithanhviennhoms:
                priority = 2
            elif "({})".format(self.moitruong.get_tendoituong(diachidoituongdangxemxet)) in TENNGUOICHOICUNGBANGs or "( {} )".format(self.moitruong.get_tendoituong(diachidoituongdangxemxet)) in TENNGUOICHOICUNGBANGs:
                priority = 2
            if priority != -1:
                danhsachungviens.append((priority, diachidoituongdangxemxet))

        danhsachungviens.sort(key = lambda x: x[0])

        for item in danhsachungviens:
            priority, diachidoituongdangxemxet = item

            is_uutiennhom = priority <= 1
            is_uutienbang = priority == 2

            if self.moitruong.get_is_nhanvatdachet(diachidoituongdangxemxet) and self.moitruong.get_idbandohientai() != BANDO_CHIENTRUONG:
                idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
                if time.time() - self._thoidiemcaituhoansinh_map.get(idnguoichoidangxemxet, 0) > 5.0:
                    if is_uutiennhom and not diachidoituongcanhoisinh:
                        diachidoituongcanhoisinh = diachidoituongdangxemxet
                    elif is_uutienbang and not diachidoituongcanhoisinhduphong:
                        diachidoituongcanhoisinhduphong = diachidoituongdangxemxet
                continue

            is_cantaytran = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THUCGIAP, HIEUUNGKYNANG_THUCCOT), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0)

            if is_cantaytran:
                if is_uutiennhom and not diachidoituongcanbufftaytranquyet:
                    diachidoituongcanbufftaytranquyet = diachidoituongdangxemxet
                elif is_uutienbang and not diachidoituongcanbufftaytranquyetduphong:
                    diachidoituongcanbufftaytranquyetduphong = diachidoituongdangxemxet

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai(diachidoituongdangxemxet)
            is_khongbithieudot = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0)

            if is_khongbithieudot and phantramsinhlucconlai <= 75:
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

            if phantramsinhlucconlai >= 25. or self.moitruong.get_idbandohientai() in BANDOKHONGPKs:
                idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)

                if not diachidoituongcanbuffngancham:
                    is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                    is_quathoigian = self.moitruong.get_diachicosothongtinnhanvat1() != diachidoituongdangxemxet and self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet) and time.time() - self._thoidiembuffnganchamgannhat_map.get(idnguoichoidangxemxet, 0) > 60
                    if is_thieuhieuung or is_quathoigian:
                        diachidoituongcanbuffngancham = diachidoituongdangxemxet

                if not diachidoituongcanbuffkimcham:
                    is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                    is_quathoigian = self.moitruong.get_diachicosothongtinnhanvat1() != diachidoituongdangxemxet and self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet) and time.time() - self._thoidiembuffkimchamgannhat_map.get(idnguoichoidangxemxet, 0) > 60
                    if is_thieuhieuung or is_quathoigian:
                        diachidoituongcanbuffkimcham = diachidoituongdangxemxet

                if not diachidoituongcanbuffcuongthethuat:
                    is_thieuhieuung = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CUONGTHETHUAT,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1)
                    is_quathoigian = self.moitruong.get_diachicosothongtinnhanvat1() != diachidoituongdangxemxet and self.moitruong.get_is_nguoichoi(diachidoituongdangxemxet) and time.time() - self._thoidiembuffcuongthethuatgannhat_map.get(idnguoichoidangxemxet, 0) > 60
                    if is_thieuhieuung or is_quathoigian:
                        diachidoituongcanbuffcuongthethuat = diachidoituongdangxemxet

        if not diachidoituongcanhoisinh:
            diachidoituongcanhoisinh = diachidoituongcanhoisinhduphong

        if not diachidoituongcanbufftaytranquyet:
            diachidoituongcanbufftaytranquyet = diachidoituongcanbufftaytranquyetduphong

        if not diachidoituongcanbommau:
            diachidoituongcanbommau = diachidoituongcanbommauduphong
            if diachidoituongcanbommauduphong:
                phantramsinhlucthapnhat = phantramsinhlucthapnhatduphong

        self._is_khongcongidebuff = not any([diachidoituongcanhoisinh, diachidoituongcanbufftaytranquyet, diachidoituongcanbommau, diachidoituongcanbuffkimcham, diachidoituongcanbuffngancham, diachidoituongcanbuffcuongthethuat])
        is_bandochientruong = self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG

        is_cohieuungdauchuyentinhdi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DAUCHUYENTINHDI,), macdinh = False, is_hieuungcoloi = 1)

        diachicantiepcan = None
        if diachidoituongcanhoisinh:
            diachicantiepcan = diachidoituongcanhoisinh
        elif diachidoituongcanbufftaytranquyet:
            diachicantiepcan = diachidoituongcanbufftaytranquyet
        elif diachidoituongcanbommau:
            if not is_bandochientruong or phantramsinhlucthapnhat < 25:
                diachicantiepcan = diachidoituongcanbommau
        elif diachidoituongcanbuffkimcham:
            diachicantiepcan = diachidoituongcanbuffkimcham
        elif diachidoituongcanbuffngancham:
            diachicantiepcan = diachidoituongcanbuffngancham
        elif diachidoituongcanbuffcuongthethuat:
            diachicantiepcan = diachidoituongcanbuffcuongthethuat
        elif diachimuctieu and is_muctieulanguoichoi and (self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGANTHUAT) or self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYENQUANGTHIEMANH)):
            diachicantiepcan = diachimuctieu

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

        danhsachuutien = [
            (VITRIKYNANG_CAITUHOANSINH, "sudungkynanglendongdoi", lambda: diachidoituongcanhoisinh, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanhoisinh, True),
            (VITRIKYNANG_TAYTRANQUYET, "sudungkynanglendongdoi", lambda: diachidoituongcanbufftaytranquyet, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbufftaytranquyet, True),
            (VITRIKYNANG_CAMLOTRI, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and (not is_bandochientruong and phantramsinhlucthapnhat <= 75 or phantramsinhlucthapnhat < 25), KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True),
            (VITRIKYNANG_KHIETVANQUYET, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and (not is_bandochientruong and phantramsinhlucthapnhat <= 75 or phantramsinhlucthapnhat < 25), KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True),
            (VITRIKYNANG_SOTRI, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and (not is_bandochientruong and phantramsinhlucthapnhat <= 75 or phantramsinhlucthapnhat < 25), KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True),
            (VITRIKYNANG_VODINHLUUTHUY, "sudungkynanglendongdoi", lambda: not is_cohieuungdauchuyentinhdi and diachidoituongcanbommau and (not is_bandochientruong and phantramsinhlucthapnhat <= 75 or phantramsinhlucthapnhat < 25), KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True),
            (VITRIKYNANG_NGANCHAMDOACH, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffngancham, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffngancham, True),
            (VITRIKYNANG_KIMCHAMDOACH, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffkimcham, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffkimcham, True),
            (VITRIKYNANG_CUONGTHETHUAT, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffcuongthethuat, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffcuongthethuat, True),
            (VITRIKYNANG_TOANPHONGQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and self.moitruong.get_phantramsinhlucconlai(diachimuctieu) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 1), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_PHONGANTHUAT, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_HUYENQUANGTHIEMANH, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "dichuyentiepcantamxa", lambda: diachicantiepcan, KHOANGCACHSUDUNGKYNANGTAMXA, diachicantiepcan, False),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngatdichuyen = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            target = target if target else diachimuctieu

            is_ok = self.action_xulyuutiensudungkynang(
                loaikynang = loaikynang,
                vitrikynang = vitrikynang,
                diachimuctieu = target,
                khoangcachyeucau = khoangcachyeucau,
                is_ngatdichuyen = is_ngatdichuyen
            )

            if is_ok:
                if target:
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
                return

    def _action_sudungkynang(self):
        self._yeucautancong = None

        if self._trangthaiveban != 0:
            return
        if self._is_danggomquai:
            return
        if self.moitruong.get_is_nhanvatchuasansang(self.moitruong.get_diachicosothongtinnhanvat1()):
            return
        if time.time() - self._thoidiemgapnguoichoigannhat < 10.0 and self.moitruong.get_idbandohientai() in BANDOFARMs and self.moitruong.get_idmaupk() == MAUPK_HOABINH:
            return
        if time.time() - self._thoidiemtamngungsudungkynang < 0.:
            return

        tenmonphai = self.moitruong.get_tenmonphai()

        if hasattr(self, f"_action_tancong_{tenmonphai}"):
            getattr(self, f"_action_tancong_{tenmonphai}")()
        elif hasattr(self, f"_action_sudungkynang_{tenmonphai}"):
            getattr(self, f"_action_sudungkynang_{tenmonphai}")()

    def _action_tancong_thucson(self):
        if self._is_thucsondao:
            self._action_tancong_thucsondao()
        else:
            self._action_tancong_thucsonkiem()

    def _action_tancong_thucsonkiem(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        if not hasattr(self, "_thoidiembuffnoikhanggannhat_map"): self._thoidiembuffnoikhanggannhat_map = {}
        if not hasattr(self, "_is_tieuchuthiensansang"): self._is_tieuchuthiensansang = False
        if not hasattr(self, "_idnguoichoibuffnoikhanggannhat"): self._idnguoichoibuffnoikhanggannhat = 0

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
                elif "(TieuLyPhiDao)" in self.moitruong.get_tendoituong(addr) and 4599 in idnguoichoithanhviennhoms:
                    danhsachungviens.append(addr)
                elif "({})".format(self.moitruong.get_tendoituong(addr)) in TENNGUOICHOICUNGBANGs or "( {} )".format(self.moitruong.get_tendoituong(addr)) in TENNGUOICHOICUNGBANGs:
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

        danhsachuutien = [
            (VITRIKYNANG_TINHTAMQUYET, "sudungkynangkhongmuctieu", lambda: self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0), 0, None, True),
            (VITRIKYNANG_TIENKHI, "sudungkynanglenbanthan", lambda: phantramsinhluc <= 75, 0, None, True),
            (VITRIKYNANG_TIENTHANVODICH, "sudungkynangkhongmuctieu", lambda: phantramsinhluc <= 25 or (is_muctieupk and phantramsinhluc <= 50), 0, None, True),
            (VITRIKYNANG_TIEUCHUTHIEN, "sudungkynanglendongdoi", lambda: diachidongdoicanbuff, KHOANGCACHSUDUNGKYNANGTAMXA, diachidongdoicanbuff, False),
            (VITRIKYNANG_BANGPHACHNGANTAM, "sudungkynangkhongmuctieu", lambda: not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1), 0, None, True),
            (VITRIKYNANG_LANGKHONGCHIHUYET, "sudungkynangmuctieu", lambda: is_muctieupk and self.moitruong.get_is_cothegaychoang(diachimuctieu), KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_LUCPHACHHOASON, "sudungkynangmuctieu", lambda: is_muctieupk and self.moitruong.get_is_cothegaychoang(diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_PHAKHONGKICH, "sudungkynangmuctieu", lambda: is_muctieupk and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_VANKIEMXUYENTAM, "sudungkynangmuctieu", lambda: is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_NGUKIEMPHITIEN, "sudungkynangkhongmuctieu", lambda: not is_muctieupk and self.moitruong.get_noilucconlai() > 70 and khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN, 0, None, True),
            (VITRIKYNANG_NGUKIEMTHUAT, "sudungkynangmuctieu", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_TIENNHANCHILO, "sudungkynangmuctieu", lambda: diachimuctieu and not is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "dichuyentiepcantamxa", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
            (None, "tancongvatly", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
        ]

        for vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngat in danhsachuutien:
            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            if self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, target if target else diachimuctieu, khoangcachyeucau, is_ngat):
                if vitrikynang == VITRIKYNANG_TIEUCHUTHIEN and target:
                    self._idnguoichoibuffnoikhanggannhat = self.moitruong.get_idnguoichoi(target)
                return

    def _action_tancong_thucsondao(self):
        if not self._is_tudongsudungkynang: return
        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        if not hasattr(self, "_thoidiembuffnoikhanggannhat_map"): self._thoidiembuffnoikhanggannhat_map = {}
        if not hasattr(self, "_is_tieuchuthiensansang"): self._is_tieuchuthiensansang = False
        if not hasattr(self, "_idnguoichoibuffnoikhanggannhat"): self._idnguoichoibuffnoikhanggannhat = 0

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieupk = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
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
                if not addr:
                    break
                if not self.moitruong.get_is_nhanvattontai(addr) or self.moitruong.get_is_nhanvatdachet(addr):
                    continue
                if self.moitruong.get_khoangcach(addr) > KHOANGCACHSUDUNGKYNANGTAMXA:
                    continue
                id_nd = self.moitruong.get_idnguoichoi(addr)
                if id_nd in idnguoichoithanhviennhoms and id_nd != self.moitruong.get_idnguoichoi():
                    danhsachungviens.append(addr)
                elif "(TieuLyPhiDao)" in self.moitruong.get_tendoituong(addr) and 4599 in idnguoichoithanhviennhoms:
                    danhsachungviens.append(addr)
                elif "({})".format(self.moitruong.get_tendoituong(addr)) in TENNGUOICHOICUNGBANGs or "( {} )".format(self.moitruong.get_tendoituong(addr)) in TENNGUOICHOICUNGBANGs:
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

        danhsachuutien = [
            (VITRIKYNANG_TINHTAMQUYET, "sudungkynangkhongmuctieu", lambda: noiluc > 50 and self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0), 0, None, True),
            (VITRIKYNANG_TIENTHANVODICH, "sudungkynangkhongmuctieu", lambda: noiluc > 50 and (phantramsinhluc <= 25 or (is_muctieupk and phantramsinhluc <= 50)), 0, None, True),
            (VITRIKYNANG_TIEUCHUTHIEN, "sudungkynanglendongdoi", lambda: noiluc > 50 and diachidongdoicanbuff, KHOANGCACHSUDUNGKYNANGTAMXA, diachidongdoicanbuff, False),
            (VITRIKYNANG_LUUTINHTRUYMANG, "sudungkynangmuctieu", lambda: noiluc > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN, KHOANGCACHSUDUNGKYNANGTAMXA, None, False),
            (VITRIKYNANG_LUCPHACHHOASON, "sudungkynangmuctieu", lambda: noiluc > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_PHAKHONGKICH, "sudungkynangmuctieu", lambda: noiluc > 50 and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_PHAMATRAM, "sudungkynangmuctieu", lambda: noiluc > 50 and is_muctieupk and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, HIEUUNGKYNANG_NGANCHAMDOACH, HIEUUNGKYNANG_KIMCHAMDOACH, HIEUUNGKYNANG_MATAMTHUAT, HIEUUNGKYNANG_HOTHEKIMCANG), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_DONDAOTRUCNHAP, "sudungkynangmuctieu", lambda: noiluc > 50, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_NGHENHPHONGTRAM, "sudungkynangmuctieu", lambda: noiluc > 50, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
            (VITRIKYNANG_TIENKHI, "sudungkynanglenbanthan", lambda: noiluc > 50 and phantramsinhluc <= 75, 0, None, True),
            (VITRIKYNANG_LANGKHONGCHIHUYET, "sudungkynangmuctieu", lambda: noiluc > 50 and is_muctieupk and 4.5 <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (VITRIKYNANG_VANKIEMXUYENTAM, "sudungkynangmuctieu", lambda: noiluc > 50 and is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False),
            (None, "tancongvatly", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True),
        ]

        for vitrikynang, loaikynang, dieukien, khoangcachyeucau, target, is_ngat in danhsachuutien:
            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            if self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, target if target else diachimuctieu, khoangcachyeucau, is_ngat):
                if vitrikynang == VITRIKYNANG_TIEUCHUTHIEN and target:
                    self._idnguoichoibuffnoikhanggannhat = self.moitruong.get_idnguoichoi(target)
                return

    def _action_sudungkynang_conluan(self):
        if not self._is_tudongsudungkynang:
            return

        is_ngatdichuyen = False

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
            is_muctieubikhoaphapbao = True
            is_muctieuchaytron = False
            is_cothetancong = False

            if diachicosothongtinnhanvatmuctieudangchon:
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_muctieubikhoaphapbao = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHOAPHAPBAO,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_muctieuchaytron = self.moitruong.get_is_muctieuchaytron(diachicosothongtinnhanvatmuctieudangchon)
                is_cothetancong = self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)

            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CANKHONNADI,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CANKHONNADI):
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_CANKHONNADI)
                break

            if diachicosothongtinnhanvatmuctieudangchon and is_cothetancong:
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                if thoigiantuthenhanvatdungim > 0.5 and khoangcach >= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if thoigiantuthenhanvatdungim > 4.5:
                        khoangcachgiutoida = 0
                    else:
                        khoangcachgiutoida = KHOANGCACHSUDUNGKYNANGTAMXA - (1.5 + thoigiantuthenhanvatdungim)

                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": khoangcachgiutoida
                    }
                    break
                elif khoangcach < KHOANGCACHSUDUNGKYNANGTAMXA:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HOALONGQUYET):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HOALONGQUYET)
                        break
                    if is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BIENTHANTHUAT, HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGMACHU):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGMACHU)
                        break
                    if is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BIENTHANTHUAT, HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BIENTHANTHUAT):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BIENTHANTHUAT)
                        break
                    # if is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BIENTHANTHUAT, ), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DANGVANGIAVU):
                    #     self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_DANGVANGIAVU, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach)
                    #     break
                    if self.moitruong.get_idkynang(*VITRIKYNANG_LOINONHANGIAN) and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LOINONHANGIAN):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LOINONHANGIAN)
                        break
                    if khoangcach <= 3. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HANBANGTRAN):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_HANBANGTRAN)
                        break
                    if khoangcach <= 5. and self._is_nhieumuctieugan5 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LOILONGQUYET):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LOILONGQUYET)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYENLONGCHANKHI):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HUYENLONGCHANKHI)
                        break
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG, HIEUUNGKYNANG_DONGBANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THUONGLONGQUYET):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THUONGLONGQUYET)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGHOAQUYET):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGHOAQUYET)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGULOITHUAT):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGULOITHUAT)
                        break

            break

        if is_ngatdichuyen:
            self.moitruong.action_ngatdichuyen()

    def battat_chedobufftoanbang(self):
        self._is_chedobufftoanbang = not self._is_chedobufftoanbang
        if self._is_chedobufftoanbang:
            phatam("Bật chế độ buff toàn bang")
        else:
            phatam("Tắt chế độ buff toàn bang")

    def battat_is_uutienbaothumaoson(self):
        self._is_uutienbaothumaoson = not self._is_uutienbaothumaoson
        if self._is_uutienbaothumaoson:
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
            self._idbandofarmbanrac = self.moitruong.get_idbandohientai()
            phatam("Bật tự động về bán rác")
            print(f"[AUTO-SELL] Đã lưu bản đồ farm: {self._idbandofarmbanrac}")
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

    def battat_is_tudonglamnhiemvusugia(self):
        self._is_tudonglamnhiemvusugia = not self._is_tudonglamnhiemvusugia
        self._trangthailamnhiemvusugia = 0
        if self._is_tudonglamnhiemvusugia:
            phatam("Bật tự động làm nhiệm vụ sứ giả")
        else:
            phatam("Tắt tự động làm nhiệm vụ sứ giả")

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
        if time.time() - self._thoidiemvutdogannhat < 1.:
            return

        iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPDOANTHACH)

        if not iddoituongvatpham:
            return

        is_ok = self.moitruong.action_thucthicaulenh("drop ! {}#1".format(hex(iddoituongvatpham)).replace("0x", ""))
        if is_ok:
            self._thoidiemvutdogannhat = time.time()

        return

    def action_nhatdo(self):
        yeucaunhatdomoi = None

        if not self._is_tudongnhatdo:
            self._yeucaunhatdo = None
            return

        if self.moitruong.get_is_dayhanhtrang():
            if time.time() - self._thoidiemphatamdayhanhtrang > 5.0:
                if not self._is_tudongvebanrac:
                   phatam("Hành trang đầy")
                self._thoidiemphatamdayhanhtrang = time.time()

            self._diachicosovatphamdangnhat = False
            self._yeucaunhatdo = None
            return

        if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT):
            return

        if self._diachicosovatphamdangnhat:
            if not self.moitruong.get_is_vatphamtontai(self._diachicosovatphamdangnhat):
                self._diachicosovatphamdangnhat = False
            elif time.time() - self._thoidiemthaydoivatphamdangnhatgannhat > 10:
                self._diachicosovatphamkhongnhat_map[self._diachicosovatphamdangnhat] = time.time()
                self._diachicosovatphamdangnhat = False
                # phatam("Bỏ qua vật phẩm lỗi")

        vatphamtudongnhats = VATPHAMTUDONGNHATs
        if self._is_tudongdichuyendiemdanhxungquanh:
            vatphamtudongnhats = (*vatphamtudongnhats, HOATLACHOAN, TIENTE)

        if not self._diachicosovatphamdangnhat:
            danhsachvatpham = []
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

                is_cannhat = False

                if tenvatpham in VATPHAMKHONGNHATs:
                    pass
                elif tenvatpham in vatphamtudongnhats:
                    is_cannhat = True
                elif VATPHAMTUDONGNHATFARMs and self.moitruong.get_idbandohientai() in BANDOFARMs and any(x in tenvatpham for x in VATPHAMTUDONGNHATFARMs):
                    is_cannhat = True
                elif self._tenvatphamnhats and tenvatpham in self._tenvatphamnhats:
                    is_cannhat = True

                if is_cannhat:
                    khoangcach = self.moitruong.get_khoangcach(diachivatpham)
                    if khoangcach < KHOANGCACHTOANMANHINH:
                        danhsachvatpham.append((khoangcach, diachivatpham))

            if danhsachvatpham:
                danhsachvatpham.sort(key = lambda x: x[0])
                self._diachicosovatphamdangnhat = danhsachvatpham[0][1]
                self._thoidiemthaydoivatphamdangnhatgannhat = time.time()

        if self._diachicosovatphamdangnhat:
            khoangcach = self.moitruong.get_khoangcach(self._diachicosovatphamdangnhat)
            yeucaunhatdomoi = {
                "yeucau": YEUCAUDICHUYENNHATDO,
                "toadodich": (
                    self.moitruong.get_toadox(self._diachicosovatphamdangnhat, is_vitrihientai = True),
                    self.moitruong.get_toadoy(self._diachicosovatphamdangnhat, is_vitrihientai = True)
                ),
                "khoangcachtoida": 0
            }

            if khoangcach <= 3.0:
                if time.time() - self._thoidiemnhatdogannhat_map.get(self._diachicosovatphamdangnhat, 0) > 0.2:
                    self.moitruong.action_nhatdo(self._diachicosovatphamdangnhat)
                    self._thoidiemnhatdogannhat_map[self._diachicosovatphamdangnhat] = time.time()

        self._yeucaunhatdo = yeucaunhatdomoi

    def action_dichuyentudo(self):
        yeucautudomoi = None

        if not self._is_tudongdichuyendiemdanhxungquanh:
            self._yeucautudo = None
            return

        if self._diachicosokhaikhoang:
            self._yeucautudo = None
            return

        if time.time() - self._thoidiemgapnguoichoigannhat < 15.0 and self.moitruong.get_idbandohientai() in BANDOFARMs and self.moitruong.get_idmaupk() == MAUPK_HOABINH:
            return

        while True:
            if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
                break

            diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            if diachimuctieu:
                if self.moitruong.get_is_nhanvattontai(diachimuctieu) and not self.moitruong.get_is_nhanvatdachet(diachimuctieu) and self.moitruong.get_is_cothetancong(diachimuctieu):
                    break

            if self.moitruong.get_is_dangclickchuottrai(): break
            if self.moitruong.get_is_dangvankhi(): break
            if self.moitruong.get_is_nhanvatdachet(): break
            if self._idbandovuachet and self._is_tudongchaylenbandovuachet: break

            idbandohientai = self.moitruong.get_idbandohientai()

            diemdanhxungquanhs = self._diemdanhxungquanhs

            if not diemdanhxungquanhs:
                if self._is_tudongvebanrac and self._idbandofarmbanrac and self._idbandofarmbanrac != idbandohientai:
                    diemdanhxungquanhs = []
                else:
                    key_map = idbandohientai if idbandohientai != BANDO_CHIENTRUONG else "{}_{}".format(idbandohientai, self.moitruong.get_idphechientruong())
                    diemdanhxungquanhs = DIEMDANHXUNGQUANH_MAP.get(key_map, [])

            if not diemdanhxungquanhs:
                if time.time() - self._thoidiemphatamlacmapgannhat > 5.0:
                    if self._is_tudongvebanrac and self._idbandofarmbanrac:
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
                if time.time() - self._thoidiembatdaudendiem > 45.0:
                    print("[Move] Quá thời gian chuyển map/đến điểm khác map -> Bỏ qua điểm này.")
                    canchuyendendiemtieptheo = True

            if canchuyendendiemtieptheo:
                next_index = (self._iddiemdanhxungquanhhientai + 1) % len(diemdanhxungquanhs)

                self._iddiemdanhxungquanhhientai = next_index
                self._diemdanhxungquanhhientai = diemdanhxungquanhs[next_index]
                self._thoidiembatdaudendiem = time.time()

            yeucautudomoi = {
                "yeucau": YEUCAUDICHUYENDICHUYENTUDO,
                "toadodich": self._diemdanhxungquanhhientai,
                "khoangcachtoida": 0
            }
            break

        self._yeucautudo = yeucautudomoi

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
        if not self._is_tudongtodoi:
            return

        idnguoichoi = self.moitruong.get_idnguoichoi()
        tenmonphai = self.moitruong.get_tenmonphai()
        is_dangtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        idbandohientai = self.moitruong.get_idbandohientai()

        danhsachuutientodoi = list(NHANVATTODOITUDONGs)

        if idbandohientai == BANDO_CHIENTRUONG:
            for nv in NHANVATTODOICHIENTRUONGS:
                if nv not in danhsachuutientodoi:
                    danhsachuutientodoi.append(nv)

        if tenmonphai in ("vanmongcoc", "thucson") and self._is_chedobufftoanbang and self.moitruong.get_idbandohientai() in BANDOKHONGPKs:
            if is_dangtrongnhom:
                if self.moitruong.get_is_truongnhom() or (self._is_khongcongidebuff and time.time() - self._thoidiemkiemtrakhongcongidebuffgannhat > 10.):
                    self._thoidiemkiemtrakhongcongidebuffgannhat = time.time()
                    self.moitruong.action_thoatkhoinhom()
            else:
                self.moitruong.action_kiemtravadongyloimoinhom(NHANVATCUNGBANGs)
            return

        if idbandohientai == BANDO_CHIENTRUONG and not is_dangtrongnhom:
            self.moitruong.action_kiemtravadongyloimoinhom(NHANVATCUNGBANGs)

        if not danhsachuutientodoi:
            return

        if idnguoichoi not in danhsachuutientodoi:
            return

        danhsachthanhviens = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
        danhsachxungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()
        dongdoicanxuly = []

        if idbandohientai == BANDO_CHIENTRUONG:
            for id_uu_tien in danhsachuutientodoi:
                if id_uu_tien == idnguoichoi: continue

                if id_uu_tien in NHANVATTODOITUDONGs:
                    dongdoicanxuly.append(id_uu_tien)

                elif id_uu_tien in NHANVATTODOICHIENTRUONGS:
                    if id_uu_tien in danhsachxungquanhs:
                        dongdoicanxuly.append(id_uu_tien)
        else:
            dongdoicanxuly = [id for id in danhsachxungquanhs if id in danhsachuutientodoi]

        if not dongdoicanxuly and not is_dangtrongnhom:
            return

        if is_dangtrongnhom:
            idtruongnhom = self.moitruong.get_idnguoichoitruongnhom()
            is_leader_invalid = False

            if idtruongnhom and idtruongnhom not in danhsachuutientodoi and dongdoicanxuly:
                if idbandohientai == BANDO_CHIENTRUONG:
                    is_leader_invalid = True
                else:
                    if dongdoicanxuly[0] in danhsachxungquanhs:
                        is_leader_invalid = True

            if is_leader_invalid and idtruongnhom not in danhsachthanhviens:
                self.moitruong.action_thoatkhoinhom()
                return

        xephangcuatoi = danhsachuutientodoi.index(idnguoichoi)
        idnguoichoixephangcaonhat = idnguoichoi
        giatrixephangcaonhat = xephangcuatoi

        for id_dongdoi in dongdoicanxuly:
            if id_dongdoi in danhsachuutientodoi:
                xephangdongdoi = danhsachuutientodoi.index(id_dongdoi)
                if xephangdongdoi < giatrixephangcaonhat:
                    giatrixephangcaonhat = xephangdongdoi
                    idnguoichoixephangcaonhat = id_dongdoi

        if self.moitruong.get_is_truongnhom():
            if danhsachthanhviens:
                for thanhvien_id in danhsachthanhviens:
                    if thanhvien_id in danhsachuutientodoi:
                        xephangthanhvien = danhsachuutientodoi.index(thanhvien_id)
                        if xephangthanhvien < xephangcuatoi:
                            self.moitruong.action_nhuongquyentruongnhom(thanhvien_id)
                            return

            if idnguoichoixephangcaonhat != idnguoichoi and idnguoichoixephangcaonhat not in danhsachthanhviens:
                if len(danhsachthanhviens) <= 1:
                    self.moitruong.action_thoatkhoinhom()
                    return

                if idbandohientai == BANDO_CHIENTRUONG and idnguoichoixephangcaonhat in dongdoicanxuly:
                    self.moitruong.action_thoatkhoinhom()
                    return

            if len(danhsachthanhviens) < 5:
                for id_dongdoi in dongdoicanxuly:
                    if id_dongdoi not in danhsachthanhviens:
                        thoidiemmoigannhat = self._thoidiemtodoigannhat_map.get(id_dongdoi, 0)
                        if time.time() - thoidiemmoigannhat > 5.0:
                            self.moitruong.action_moihoacxinvaonhom(id_dongdoi)
                            self._thoidiemtodoigannhat_map[id_dongdoi] = time.time()
                            break
                        else:
                            continue

        elif is_dangtrongnhom:
            pass
        else:
            self.moitruong.action_kiemtravadongyloimoinhom(danhsachuutientodoi)

            if idnguoichoixephangcaonhat != idnguoichoi:
                target_id = idnguoichoixephangcaonhat
                if time.time() - self._thoidiemtodoigannhat_map.get(target_id, 0) > 5.0:
                    self.moitruong.action_moihoacxinvaonhom(target_id)
                    self._thoidiemtodoigannhat_map[target_id] = time.time()

    def action_tudongphucsinh(self):
        if self._is_tudongphucsinh:
            if self.moitruong.get_is_nhanvatdachet() and self.moitruong.get_idnguoichoi() != 4599:
                dfgdfb = 1
                while dfgdfb <= 10:
                    if self.moitruong.get_is_nhanvatdachet():
                        time.sleep(1.)
                    else:
                        return
                    dfgdfb += 1
                self.moitruong.action_phucsinh()

    def action_tudongdoimaupk(self):
        if self._is_tudongdoimaupk and self.moitruong.get_idbandohientai() not in BANDOFARMs:
            if time.time() - self._thoidiemdoimaupkgannhat > 5.:
                self._thoidiemdoimaupkgannhat = time.time()
                self.action_batpk()

    def action_batpk(self):
        self.moitruong.action_doimaupk(MAUPK_BANG)

    def action_tatpk(self):
        self.moitruong.action_doimaupk(MAUPK_HOABINH)

    def action_tudongsuado(self, delay = 3.):
        if self._is_tudongsuado:
            if time.time() - self._thoidiemkiemtranpcsuadogannhat < delay:
                return
            self._thoidiemkiemtranpcsuadogannhat = time.time()

            diachicosothongtinnhanvatchutiemsuachua = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)

            if diachicosothongtinnhanvatchutiemsuachua and self.moitruong.get_khoangcach(diachicosothongtinnhanvatchutiemsuachua) <= 12.0:
                self.moitruong.action_suado(diachicosothongtinnhanvatchutiemsuachua)

    def action_suado(self):
        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        thoidiembatdau = time.time()
        THOIGIANTOIDA = 30.0

        while True:
            if time.time() - thoidiembatdau > THOIGIANTOIDA:
                print(f"[Auto-SuaDo] Quá {THOIGIANTOIDA}s không tìm thấy Chủ Tiệm Sửa Chữa. Hủy bỏ.")
                break

            diachinpc = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)

            if diachinpc:
                khoangcach = self.moitruong.get_khoangcach(diachinpc)
                if khoangcach <= 9.0:
                    print("[Auto-SuaDo] Đã tìm thấy NPC, đang sửa đồ...")
                    self.moitruong.action_suado(diachinpc)
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

        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham, is_boquaxacnhan, delay = delay)
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
                    vitrivatphamcanxepchongs = [vitrivatpham for vitrivatpham in vitrivatphams if self.moitruong.get_soluongvatphamhanhtrang(vitrivatpham[0]) < SOLUONGXEPCHONGTOIDA_MAP.get(tenvatpham, 30)]
                    
                    if len(vitrivatphamcanxepchongs) <= 1:
                        continue

                    for vitrivatpham in vitrivatphamcanxepchongs[1:]:
                        if vitrivatpham[0] // 24 != vitrivatphamcanxepchongs[0][0] // 24:
                            #print("1: {}, {}, {}, {}".format(tenvatpham, vitrivatphamcanxepchongs, vitrivatpham[0] // 24, vitrivatphamcanxepchongs[0][0] // 24))
                            is_ok = self.moitruong.action_dichuyenvatphamsanghanhtrangkhac(vitrivatpham[1], vitrivatphamcanxepchongs[0][0] // 24 + 1, delay = delay)
                        else:
                            #print("2: {}, {}, {}, {}".format(tenvatpham, vitrivatphamcanxepchongs, vitrivatpham[0] // 24, vitrivatphamcanxepchongs[0][0] // 24))
                            is_ok = self.moitruong.action_dichuyenvatphamhanhtrang(vitrivatpham[1], vitrivatphamcanxepchongs[0][0] + 1, delay = delay)
                        if is_ok:
                            self._thoidiemxepchongdogannhat = time.time()
                break

    def action_chantangcapdo(self):
        if self._is_chantangcapdo:
            self.moitruong.action_chantangcapdo()
        else:
            self.moitruong.action_bochantangcapdo()

    def action_tudongtrieuhoibaothudautien(self):
        if self._is_tudongtrieuhoibaothudautien:
            while True:
                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                iddoituongbaothudautien = self.moitruong.get_iddoituongbaothudautien()

                if not iddoituongbaothudautien:
                    break

                if self.moitruong.get_is_datrieuhoibaothudautien():
                    if time.time() - self._thoidiemsudungthucanbaothugannhat > 2. and self.moitruong.get_dotrungthanhbaothudautien() <= 80:
                        iddoituongcaocapbaothuthucpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPBAOTHUTHUCPHAM)
                        if iddoituongcaocapbaothuthucpham:
                            is_ok = self.moitruong.action_sudungvatphambaothu(iddoituongcaocapbaothuthucpham, iddoituongbaothudautien, delay = 0.5)
                            if is_ok:
                                self._thoidiemsudungthucanbaothugannhat = time.time()

                    diachicosonhanvatbaothudautien = self.moitruong.get_diachicosonhanvatbaothudautien()

                    tendoituong = self.moitruong.get_tendoituong(diachicosonhanvatbaothudautien) if diachicosonhanvatbaothudautien else ""
                    if diachicosonhanvatbaothudautien and not any(tenbaothumaoson in tendoituong for tenbaothumaoson in (CUONGTHI, QUYTOT, THIENBINH, DAUBINH, THIENTUONG)):
                        if self.moitruong.get_idbandohientai() in BANDOKHONGPKs:
                            self.moitruong.action_sudungthaotacbaothu(iddoituongbaothudautien, 3, delay = 0.25)
                        elif self.moitruong.get_khoangcach(diachicosonhanvatbaothudautien) < KHOANGCACHTOANMANHINH:
                            self.moitruong.action_sudungthaotacbaothu(iddoituongbaothudautien, 2, delay = 0.25)
                            self.moitruong.action_thietlapchedobaothu(iddoituongbaothudautien, "0", delay = 5.)
                    break

                if self.moitruong.get_idbandohientai() in BANDOKHONGPKs and time.time() - self._thoidiemtudongtrieuhoibaothudautien > 1. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM and time.time() - self._thoidiemtamngungdichuyensudungkynang > 0.:
                    is_ok = self.moitruong.action_trieuhoibaothu(iddoituongbaothudautien, delay = 0.5)
                    if is_ok:
                        self._thoidiemtudongtrieuhoibaothudautien = time.time()
                    break
                break

    def action_tudongsudungkynangbaothu(self):
        if self._is_tudongsudungkynangbaothu:
            while True:
                if self.moitruong.get_tenmonphai() in ("maoson", "vanmongcoc"):
                    break
                if self.moitruong.get_is_nhanvatdachet():
                    break

                if not self.moitruong.get_is_datrieuhoibaothudautien():
                    break

                iddoituongbaothu = self.moitruong.get_iddoituongbaothudautien()
                if not iddoituongbaothu:
                    break

                idkynangbaothu_map = {self.moitruong.get_idkynangbaothudautien(i): i for i in range(11)}
                idkynangbaothucothesudungs = {KYNANGBAOTHU_THOIDICHTHUAT, KYNANGBAOTHU_THIENCAN, KYNANGBAOTHU_CAOCAPTHIENCAN, KYNANGBAOTHU_CAOCAPTHIEUDOT, KYNANGBAOTHU_PHONGMATHUAT}
                if set(idkynangbaothu_map.keys()) & idkynangbaothucothesudungs:
                    if time.time() - self._thoidiemhoiphucbaothugannhat > 5.:
                        if self.moitruong.get_noilucconlaibaothudautien() <= 120:
                            iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang("Lão Tửu")
                            if iddoituongvatpham:
                                if self.moitruong.action_sudungvatphambaothu(iddoituongvatpham, iddoituongbaothu):
                                    self._thoidiemhoiphucbaothugannhat = time.time()
                            else:
                                phatam("Hết lão tửu")
                                self._thoidiemhoiphucbaothugannhat = time.time()

                        if self.moitruong.get_sinhluctoidabaothudautien() - self.moitruong.get_sinhlucconlaibaothudautien() >= 1200:
                            iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang("Trái Đào")
                            if not iddoituongvatpham:
                                iddoituongvatpham = self.moitruong.action_timkiemvatphamhanhtrang("Chuối")

                            if iddoituongvatpham:
                                if self.moitruong.action_sudungvatphambaothu(iddoituongvatpham, iddoituongbaothu):
                                    self._thoidiemhoiphucbaothugannhat = time.time()
                            else:
                                phatam("Hết trái đào")
                                self._thoidiemhoiphucbaothugannhat = time.time()

                    diachicosonhanvatbaothu = self.moitruong.get_diachicosonhanvatbaothudautien()
                    diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                    if diachimuctieu and (self.moitruong.get_is_nguoichoi(diachimuctieu) or CUONGTHI in self.moitruong.get_tendoituong(diachimuctieu)) and self.moitruong.get_noilucconlaibaothudautien() >= 60:
                        if KYNANGBAOTHU_CAOCAPTHIENCAN in idkynangbaothu_map and self.moitruong.get_is_kynangbaothudautiensansang(idkynangbaothu_map[KYNANGBAOTHU_CAOCAPTHIENCAN]) and self.moitruong.get_is_cothegaychoang(diachimuctieu) and time.time() - self._thoidiemsudungnhiephonchamgannhat >= 8. and (not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHIEPHONCHAM) or self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), macdinh = False, is_hieuungcoloi = 0)):
                            if not diachicosonhanvatbaothu or time.time() - self._thoidiemsudungthaotacbaothugannhat > 0.25:
                                self._thoidiemsudungthaotacbaothugannhat = time.time()
                                self.moitruong.action_sudungthaotacbaothu(iddoituongbaothu, 2, delay = 0.)
                            if diachicosonhanvatbaothu:
                                self.moitruong.action_sudungkynangbaothu(KYNANGBAOTHU_CAOCAPTHIENCAN, diachimuctieu)
                            break
                        if KYNANGBAOTHU_THIENCAN in idkynangbaothu_map and self.moitruong.get_is_kynangbaothudautiensansang(idkynangbaothu_map[KYNANGBAOTHU_THIENCAN]) and self.moitruong.get_is_cothegaychoang(diachimuctieu) and time.time() - self._thoidiemsudungnhiephonchamgannhat >= 8. and (not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHIEPHONCHAM) or self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), macdinh = False, is_hieuungcoloi = 0)):
                            if not diachicosonhanvatbaothu or time.time() - self._thoidiemsudungthaotacbaothugannhat > 0.25:
                                self._thoidiemsudungthaotacbaothugannhat = time.time()
                                self.moitruong.action_sudungthaotacbaothu(iddoituongbaothu, 2, delay = 0.)
                            if diachicosonhanvatbaothu:
                                self.moitruong.action_sudungkynangbaothu(KYNANGBAOTHU_THIENCAN, diachimuctieu)
                            break
                        if KYNANGBAOTHU_PHONGMATHUAT in idkynangbaothu_map and self.moitruong.get_is_kynangbaothudautiensansang(idkynangbaothu_map[KYNANGBAOTHU_PHONGMATHUAT]) and self.moitruong.get_idloaivukhi(diachimuctieu) == LOAIVUKHI_KIEM and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0):
                            if not diachicosonhanvatbaothu or time.time() - self._thoidiemsudungthaotacbaothugannhat > 0.25:
                                self._thoidiemsudungthaotacbaothugannhat = time.time()
                                self.moitruong.action_sudungthaotacbaothu(iddoituongbaothu, 2, delay = 0.)
                            if diachicosonhanvatbaothu:
                                self.moitruong.action_sudungkynangbaothu(KYNANGBAOTHU_PHONGMATHUAT, diachimuctieu)
                            break
                        if KYNANGBAOTHU_THOIDICHTHUAT in idkynangbaothu_map and self.moitruong.get_is_kynangbaothudautiensansang(idkynangbaothu_map[KYNANGBAOTHU_THOIDICHTHUAT]) and self.moitruong.get_idloaivukhi(diachimuctieu) not in (LOAIVUKHI_KIEM, LOAIVUKHI_AMKHI) and self.moitruong.get_khoangcach(diachimuctieu) <= 4.5:
                            if not diachicosonhanvatbaothu or time.time() - self._thoidiemsudungthaotacbaothugannhat > 0.25:
                                self._thoidiemsudungthaotacbaothugannhat = time.time()
                                self.moitruong.action_sudungthaotacbaothu(iddoituongbaothu, 2, delay = 0.)
                            if diachicosonhanvatbaothu:
                                self.moitruong.action_sudungkynangbaothu(KYNANGBAOTHU_THOIDICHTHUAT, diachimuctieu)
                            break
                        if KYNANGBAOTHU_CAOCAPTHIEUDOT in idkynangbaothu_map and self.moitruong.get_is_kynangbaothudautiensansang(idkynangbaothu_map[KYNANGBAOTHU_CAOCAPTHIEUDOT]) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT, ), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0):
                            if not diachicosonhanvatbaothu or time.time() - self._thoidiemsudungthaotacbaothugannhat > 0.25:
                                self._thoidiemsudungthaotacbaothugannhat = time.time()
                                self.moitruong.action_sudungthaotacbaothu(iddoituongbaothu, 2, delay = 0.)
                            if diachicosonhanvatbaothu:
                                self.moitruong.action_sudungkynangbaothu(KYNANGBAOTHU_CAOCAPTHIEUDOT, diachimuctieu)
                            break

                break

    def action_tudongbanrac(self):
        diachi_npc = self.moitruong.action_timkiemnhanvat(CHUTIEMTAPHOA)
        if not diachi_npc:
            diachi_npc = self.moitruong.action_timkiemnhanvat(CHUTIEMTAPHOA)
            if not diachi_npc:
                return

        khoangcach = self.moitruong.get_khoangcach(diachi_npc)
        if khoangcach > 12.0:
            return

        idnpc = self.moitruong.get_iddoituong(diachi_npc)
        if not idnpc or idnpc <= 0:
            return

        sovatphamdaban = 0
        for i in range(12, SOLUONGVATPHAMHANHTRANGTOIDA):
            iddoituongvatphamhanhtrang = self.moitruong.get_iddoituongvatphamhanhtrang(i)

            if iddoituongvatphamhanhtrang and iddoituongvatphamhanhtrang > 0 and self.moitruong.get_tenvatphamhanhtrang(i) not in VATPHAMKHONGBANs:
                caulenh = "sell ! {}# {}# 1".format(hex(idnpc).replace("0x", ""), hex(iddoituongvatphamhanhtrang).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.)
                sovatphamdaban += 1
                time.sleep(1.5)

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

    def action_xulygomquai(self):
        yeucaugomquaimoi = None

        if not self._is_tudonggomquai:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            self._danhsachidquaidagom.clear()
            self._idquaidautien = 0
            return

        idbandohientai = self.moitruong.get_idbandohientai()

        if self._is_tudongvebanrac and self._idbandofarmbanrac and self._idbandofarmbanrac != idbandohientai:
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

        vungdabichiemdongs = []
        idnhanvathientai = self.moitruong.get_idnguoichoi()
        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

        iiii = -1
        while True:
            iiii += 1
            diachidoituongbotxemxet = self.moitruong.get_diachicosothongtindoituongx(iiii)
            if not diachidoituongbotxemxet: break

            idnguoichoibot = self.moitruong.get_idnguoichoi(diachidoituongbotxemxet)
            if idnguoichoibot in NHANVATCUAMINHs and idnguoichoibot != idnhanvathientai:
                if not idnguoichoithanhviennhoms or idnguoichoibot not in idnguoichoithanhviennhoms:
                    vungdabichiemdongs.append({
                        "x": self.moitruong.get_toadox(diachidoituongbotxemxet),
                        "y": self.moitruong.get_toadoy(diachidoituongbotxemxet)
                    })

        is_canghilog = False
        if time.time() - self._thoidiemloggomquai > 1.5:
            is_canghilog = True
            self._thoidiemloggomquai = time.time()
        is_canghilog = False
        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_dangvankhi() or idbandohientai in BANDOKHONGPKs:
            self._yeucaugomquai = None
            return

        if len(self._danhsachidquaidagom) == 0:
            self._idquaidautien = 0

        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if diachimuctieudangchon:
            tendoituongmuctieudangchon = self.moitruong.get_tendoituong(diachimuctieudangchon)
            if self.moitruong.get_is_nguoichoi(diachimuctieudangchon) or CUONGTHI in tendoituongmuctieudangchon or self.moitruong.get_is_baothugiangho(tendoituongmuctieudangchon):
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
        soluongquaidagom = 0
        soluongquaigan = 0

        idquaicankeogannhat = 0
        khoangcachquaicankeo = 9999.
        diachicosoquaicankeo = 0

        is_coquaixungquanh = False

        idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if time.time() - v > 120.0]
        for k in idcanxoas:
            del self._idmuctieubiloi_map[k]

        is_neobirotlai = (diachiquaidautien and khoangcachneohientai > 12.0)

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

            mx = self.moitruong.get_toadox(diachidoituongxemxet)
            my = self.moitruong.get_toadoy(diachidoituongxemxet)

            if self._kiemtra_vungcam(mx, my):
                continue

            iddoituongquai = self.moitruong.get_iddoituong(diachidoituongxemxet)
            if iddoituongquai in self._idmuctieubiloi_map:
                continue

            qx = self.moitruong.get_toadox(diachidoituongxemxet)
            qy = self.moitruong.get_toadoy(diachidoituongxemxet)

            is_cobotkhacdangtranh = False

            khoangcachtoidenquai = self.moitruong.get_khoangcach(diachidoituongxemxet)
            for vung in vungdabichiemdongs:
                khoangcachbotdenquai = math.dist((qx, qy), (vung["x"], vung["y"]))
                if khoangcachbotdenquai <= 9.0:
                    if khoangcachtoidenquai > khoangcachbotdenquai:
                        is_cobotkhacdangtranh = True
                        break

            if is_cobotkhacdangtranh:
                if iddoituongquai in self._danhsachidquaidagom:
                    self._danhsachidquaidagom.remove(iddoituongquai)
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
                    if id_target not in self._danhsachidquaidagom and id_target not in self._idmuctieubiloi_map and 12.0 < kc_target < KHOANGCACHTOANMANHINH:
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

                x_neo = self.moitruong.get_toadox(diachiquaidautien, is_vitrihientai = True)
                y_neo = self.moitruong.get_toadoy(diachiquaidautien, is_vitrihientai = True)

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

            is_quahan = time.time() - self._thoidiembatdaukeo > 5.0

            if khoangcachquaicankeo <= 1.5 or is_quahan:
                self._danhsachidquaidagom.add(idquaicankeogannhat)
                if self._idquaidautien == 0:
                    self._idquaidautien = idquaicankeogannhat
                yeucaugomquaimoi = None
                self._idquaidangkeo = 0
                if is_canghilog: print(f"[GOM] Đã tiếp cận {hex(idquaicankeogannhat)}")
            else:
                x_quai = self.moitruong.get_toadox(diachicosoquaicankeo, is_vitrihientai = True)
                y_quai = self.moitruong.get_toadoy(diachicosoquaicankeo, is_vitrihientai = True)

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

    def action_xulyvebanrac(self):
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
                if self.moitruong.get_khoangcach(diachi_npc) <= 12.0:
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
                    self.moitruong.action_thucthicaulenh("pf 4182.1", delay = 0.)
                    self._thoidiemchuyentrangthai = time.time()

        elif self._trangthaiveban == 2:
            if time.time() - self._thoidiemchuyentrangthai > 3.0:
                diachi_npc = self.moitruong.action_timkiemnhanvat(chutiemtaphoa)
                if diachi_npc:
                    khoangcach = self.moitruong.get_khoangcach(diachi_npc)
                    if khoangcach <= 12.0:
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
            self.action_suado()
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

            if time.time() - self._thoidiemchuyentrangthai > 1.0:
                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                    print("[AUTO-SELL] Đã đứng yên. Sử dụng Xuyên không hành (Quay lại)")
                    self.moitruong.action_ngatdichuyen()
                    self.moitruong.action_thucthicaulenh("pf 4182.2", delay = 0.)
                    self._thoidiemchuyentrangthai = time.time()

    def _action_xulyvebanrac_phaikhac(self):
        if self._trangthaiveban == 0:
            diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = QUANSUVOSONGTHANH)

            if diachinpc and self.moitruong.get_khoangcach(diachinpc) <= 12.0:
                if not self.moitruong.get_is_dayhanhtrang():
                    if self._idbandofarmbanrac != 0:
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
            diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = QUANSUVOSONGTHANH)
            if diachinpc:
                print("[AUTO-SELL] Đã về thành công. Chuyển sang di chuyển.")
                self._trangthaiveban = 2
                return

            if time.time() - self._thoidiemhoithanhphu > 12.0 and not self.moitruong.get_is_dangvankhi():
                print("[AUTO-SELL] Đang dùng Hồi Thành Phù...")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu()
                self._thoidiemhoithanhphu = time.time()

        elif self._trangthaiveban == 2:
            diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = QUANSUVOSONGTHANH)
            if not diachinpc:
                self._trangthaiveban = 1
                return

            khoangcach = self.moitruong.get_khoangcach(diachinpc)
            if khoangcach > 12.0:
                self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, 3.)
                time.sleep(0.5)
            else:
                self._trangthaiveban = 3

        elif self._trangthaiveban == 3:
            self.action_tudongbanrac()
            time.sleep(1.0)
            self.action_suado()
            time.sleep(1.)

            if not self.moitruong.get_is_dayhanhtrang():
                print("[AUTO-SELL] Đã bán xong.")
                self._trangthaiveban = 4
        elif self._trangthaiveban == 4:
            if self._idbandofarmbanrac == 0:
                print("[AUTO-SELL] Lỗi: Không nhớ ID bản đồ farm!")
                self._trangthaiveban = 0
                return

            self.action_dichuyenlenbandofarm()

            if self.moitruong.get_idbandohientai() == self._idbandofarmbanrac:
                print(f"[AUTO-SELL] Đã tới bãi farm {self._idbandofarmbanrac}.")
                self._trangthaiveban = 0

    def action_sudunghoithanhphu(self):
        if time.time() - self._thoidiemsudunghoithanhphugannhat > 12.:
            self._thoidiemsudunghoithanhphugannhat = time.time()
            self.moitruong.action_thucthicaulenh("dGludmF0 2", delay = 0)

    def action_dichuyenlenbandofarm(self):
        diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = TANTHUTIENCO)

        if not diachinpc:
            if self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON:
                print(f"[DI-CHUYEN] Chưa thấy {TANTHUTIENCO}, di chuyển đến vị trí (148, 145)...")
                self.moitruong.action_dichuyengiukhoangcachtoidadiem(148, 145, khoangcachtoida = 3.)
                self._thoidiemsudunghoithanhphugannhat = time.time()
            else:
                print(f"[DI-CHUYEN] Không tìm thấy NPC {TANTHUTIENCO}. Đang tìm kiếm...")
            return

        khoangcach = self.moitruong.get_khoangcach(diachinpc)

        if khoangcach > 6.0:
            self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, 3.)
            return

        steps = DICHUYENTANTHUTIENCO_MAP.get(self._idbandofarmbanrac)

        if not steps:
            print(f"[DI-CHUYEN] Chưa định nghĩa đường đi cho Map ID: {self._idbandofarmbanrac}")
            return

        idnpc = self.moitruong.get_iddoituong(diachinpc)
        hex_id = hex(idnpc).replace("0x", "")

        print(f"[DI-CHUYEN] Bắt đầu di chuyển lên map {self._idbandofarmbanrac}...")

        for step in steps:
            caulenh = f"tallk {hex_id}# {step}"
            self.moitruong.action_thucthicaulenh(caulenh, delay = 0.)
            time.sleep(1.0)

        if self.moitruong.get_is_danghiencuasotuychon():
            self.moitruong.set_is_danghiencuasotuychon(False)

    def action_tudongkhaikhoang(self):
        yeucaukhaikhoangmoi = None
        diachikhoangvatmoi = 0

        if not self._is_tudongkhaikhoang:
            self._yeucaukhaikhoang = None
            self._diachicosokhaikhoang = 0
            return

        if not hasattr(self, '_index_thuduongson'): self._index_thuduongson = 0
        if not hasattr(self, '_index_thuyhoason'): self._index_thuyhoason = 0
        if not hasattr(self, '_index_hamcocquan'): self._index_hamcocquan = 0

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
                if tendoituong and ("Khoáng" in tendoituong):
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
                mx, my = self.moitruong.get_toadox(diachidoituong), self.moitruong.get_toadoy(diachidoituong)

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
            mx_move = self.moitruong.get_toadox(diachikhoang, is_vitrihientai = True)
            my_move = self.moitruong.get_toadoy(diachikhoang, is_vitrihientai = True)

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

        char_x = self.moitruong.get_toadox(is_vitrihientai = True)
        char_y = self.moitruong.get_toadoy(is_vitrihientai = True)
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

        is_dangnamtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        is_truongnhom = self.moitruong.get_is_truongnhom()
        if self.moitruong.get_idbandohientai() == BANDO_CHU and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 0.5:
            diachinpc = self.moitruong.action_timkiemnhanvat(TRUONGQUALAO)
            if not diachinpc:
                return

            khoangcach = self.moitruong.get_khoangcach(diachinpc)
            if khoangcach > 9.0:
                self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 3.)
                return

            idnpc = self.moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                return

            self._thoidiemdichientruonggannhat = time.time()

            if is_truongnhom and NHANVATTODOITUDONGs and self.moitruong.get_idnguoichoi() == NHANVATTODOITUDONGs[0]:
                caulenh = "tallk {}# welcome.1002".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(0.25)
                # time.sleep(1.)

                # if self.moitruong.get_is_dangmocuasoxacnhan():
                #     noidungcuasoxacnhan = self.moitruong.get_noidungcuasomaxacnhan()

                #     try:
                #         maxacnhan = noidungcuasoxacnhan.split("(")[1].split(")")[0]
                #         caulenh = "tallk {}# welcome.9999.{}".format(hex(idnpc).replace("0x", ""), maxacnhan)
                #         self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                #         self.moitruong.set_is_dangmocuasoxacnhan(False)
                #         time.sleep(1.)
                #     except IndexError:
                #         print("Không tìm thấy mã xác nhận đúng định dạng")

                caulenh = "tallk {}# welcome.1003".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(0.25)
                # time.sleep(1.)

                # if self.moitruong.get_is_dangmocuasoxacnhan():
                #     noidungcuasoxacnhan = self.moitruong.get_noidungcuasomaxacnhan()
                #
                #     try:
                #         maxacnhan = noidungcuasoxacnhan.split("(")[1].split(")")[0]
                #         caulenh = "tallk {}# welcome.9999.{}".format(hex(idnpc).replace("0x", ""), maxacnhan)
                #         self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                #         self.moitruong.set_is_dangmocuasoxacnhan(False)
                #         time.sleep(1.)
                #     except IndexError:
                #         print("Không tìm thấy mã xác nhận đúng định dạng")

            elif is_dangnamtrongnhom:
                caulenh = "tallk {}# welcome.1003".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(0.25)
                # time.sleep(1.)

                # if self.moitruong.get_is_dangmocuasoxacnhan():
                #     noidungcuasoxacnhan = self.moitruong.get_noidungcuasomaxacnhan()

                #     try:
                #         maxacnhan = noidungcuasoxacnhan.split("(")[1].split(")")[0]
                #         caulenh = "tallk {}# welcome.9999.{}".format(hex(idnpc).replace("0x", ""), maxacnhan)
                #         self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                #         self.moitruong.set_is_dangmocuasoxacnhan(False)
                #         time.sleep(1.)
                #     except IndexError:
                #         print("Không tìm thấy mã xác nhận đúng định dạng")

            else:
                caulenh = "tallk {}# welcome.1001".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(0.25)
                # time.sleep(1.)

                # if self.moitruong.get_is_dangmocuasoxacnhan():
                #     noidungcuasoxacnhan = self.moitruong.get_noidungcuasomaxacnhan()
                #
                #     try:
                #         maxacnhan = noidungcuasoxacnhan.split("(")[1].split(")")[0]
                #         caulenh = "tallk {}# welcome.9999.{}".format(hex(idnpc).replace("0x", ""), maxacnhan)
                #         self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                #         self.moitruong.set_is_dangmocuasoxacnhan(False)
                #         time.sleep(1.)
                #     except IndexError:
                #         print("Không tìm thấy mã xác nhận đúng định dạng")

                caulenh = "tallk {}# welcome.1003".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(0.25)
                # time.sleep(1.)
                #
                # if self.moitruong.get_is_dangmocuasoxacnhan():
                #     noidungcuasoxacnhan = self.moitruong.get_noidungcuasomaxacnhan()
                #
                #     try:
                #         maxacnhan = noidungcuasoxacnhan.split("(")[1].split(")")[0]
                #         caulenh = "tallk {}# welcome.9999.{}".format(hex(idnpc).replace("0x", ""), maxacnhan)
                #         self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                #         self.moitruong.set_is_dangmocuasoxacnhan(False)
                #         time.sleep(1.)
                #     except IndexError:
                #         print("Không tìm thấy mã xác nhận đúng định dạng")

    def action_tudongdaotangbaodo(self):
        self._yeucaudaotangbaodo = None

        if not self._is_tudongdaotangbaodo:
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        idbandohientai = self.moitruong.get_idbandohientai()
        x_hientai = self.moitruong.get_toadox(is_vitrihientai = True)
        y_hientai = self.moitruong.get_toadoy(is_vitrihientai = True)

        for i in range(SOLUONGVATPHAMHANHTRANGTOIDA):
            tenvatpham = self.moitruong.get_tenvatphamhanhtrang(i)
            if not tenvatpham or tenvatpham != TANGBAODO:
                continue

            mota = self.moitruong.get_motavatphamhanhtrang(i)
            if not mota: continue

            timthay = re.search(r"Vị trí:\s*(.*?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", mota)
            if timthay:
                tenbando_trongmota = timthay.group(1).strip()
                x_dich = int(timthay.group(2))
                y_dich = int(timthay.group(3))

                idbando_dich = IDBANDO_MAP.get(tenbando_trongmota)

                if idbando_dich == idbandohientai:
                    khoangcach = math.sqrt((x_hientai - x_dich) ** 2 + (y_hientai - y_dich) ** 2)
                    if khoangcach < 1.:
                        print(f"[DAOTAOBAODO] Đang đào tại {tenbando_trongmota} ({x_dich}, {y_dich})")
                        iddoituong = self.moitruong.get_iddoituongvatphamhanhtrang(i)
                        if iddoituong:
                            self.moitruong.action_sudungvatpham(iddoituong)
                            time.sleep(1.0)
                    else:
                        self.moitruong.action_tudongtimduong(x_dich, y_dich, idbando_dich)
                    return

        self.moitruong.action_tudongtimduong(0, 0, 0)

        quoc_gia_can_den = None
        for i in range(SOLUONGVATPHAMHANHTRANGTOIDA):
            tenvatpham = self.moitruong.get_tenvatphamhanhtrang(i)
            if tenvatpham == TANGBAODO:
                mota = self.moitruong.get_motavatphamhanhtrang(i)
                if mota:
                    timthay = re.search(r"Vị trí:\s*(.*?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", mota)
                    if timthay:
                        tenbando_trongmota = timthay.group(1).strip()
                        quoc_gia_can_den = f"{tenbando_trongmota} Quốc"
                        break

        if not quoc_gia_can_den:
            if self.moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                phatam("{} hết tàng bảo đồ".format(self.moitruong.get_tendoituong()))
                time.sleep(5)
            return

        print(f"[DAOTAOBAODO] Hết map hiện tại. Chuẩn bị sang: {quoc_gia_can_den}")

        if idbandohientai != BANDO_TANTHUTHON:
            if time.time() - self._thoidiemsudunghoithanhphugannhat > 12.0:
                print(f"[DAOTAOBAODO] Dùng Hồi Thành Phù về Tân Thủ Thôn")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu()
                self._thoidiemsudunghoithanhphugannhat = time.time()
            return

        chu_dich_tram_name = "Chủ Dịch Trạm"
        diachinpc = self.moitruong.action_timkiemnhanvat(chu_dich_tram_name)

        if not diachinpc:
            return

        khoangcach_npc = self.moitruong.get_khoangcach(diachinpc)
        if khoangcach_npc > 9.0:
            self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, 3.0)
            return

        idnpc = self.moitruong.get_iddoituong(diachinpc)
        if idnpc:
            self.moitruong.action_ngatdichuyen()
            timestamp = int(time.time())
            hex_id = hex(idnpc).replace("0x", "")
            caulenh = f"tallk {hex_id}# goto.! {quoc_gia_can_den} t{timestamp}"
            self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
            self.moitruong.action_ngatdichuyen()
            time.sleep(5.0)
