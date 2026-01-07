import math
import random
import time

import pymem

from hangso import *
from moitruong import MoiTruong
from tienich import luuthietlap as util_luuthietlap
from tienich import taithietlap as util_taithietlap, phatam


class TacTu:
    def __init__(self, moitruong: MoiTruong):
        self._thoidiembatdaudendiem = 0.
        self._thoidiemlogdebug = 0.
        self._is_tudongdieukhienbaothumaoson = True
        self._solanthatbaikhaithien = 0
        self._thoidiembiphatkhaithien = 0.
        self._is_tudonglamnhiemvulaoquangia = False
        self._is_tudongcatdovaoruong = True
        self._is_thucsondao = False
        self.moitruong = moitruong

        # Thiết lập có lưu
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
        self._is_uutiennguoichoi = True

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
        self._thoidiemdieukhienbaothumaosongannhat = time.time()
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
        self._thoidiemralenhbaothumaosontancong = 0.

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

        self._is_tudongdichientruong = False  # Flag bật tắt
        self._trangthaidichientruong = 0  # 0: Chưa làm gì, 1: Đã đăng ký chờ vào
        self._thoidiemdichientruong = 0.  # Timer delay

        self._is_tudonglamnhiemvusugia = False

        self._is_khaithientichdiasansang = False
        self._thoidiemkhaithientichdiakhongsansanggannhat = 0.
        self._is_luutinhtruymangsansang = False
        self._thoidiemluutinhtruymangkhongsansanggannhat = 0.

        self._is_yeucauvohieuhoadichuyen = False
        self._is_uutienbaothumaoson = False
        self._is_vohieuhoadichuyenanthan = False

        self._is_chedobufftoanbang = False
        self._is_khongcongidebuff = False

        self._thoidiemsudungbaothuvatphamgannhat = 0.
        self._thoidiemthietlaptrieuhoithudoilenhgannhat = 0.
        self._thoidiemkiemtrakhongcongidebuffgannhat = 0.

    def __del__(self):
        try:
            self.moitruong.action_bochantangcapdo()
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass

    def luuthietlap(self, tennhanvat):
        thietlap = {
            "_is_tudongbattheosaunhom": self._is_tudongbattheosaunhom,
            "_is_tudongtheosautruongnhom": self._is_tudongtheosautruongnhom,
            "_is_tudongtimkiemmuctieu": self._is_tudongtimkiemmuctieu,
            "_is_tudongsudungkynang": self._is_tudongsudungkynang,
            "_is_uutiennguoichoi": self._is_uutiennguoichoi,
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
        }

        util_luuthietlap(tennhanvat, thietlap)

    def taithietlap(self, tennhanvat):
        thietlap = util_taithietlap(tennhanvat)
        if thietlap:
            if "_is_tudongbattheosaunhom" in thietlap:
                self._is_tudongbattheosaunhom = thietlap["_is_tudongbattheosaunhom"]

            if "_is_tudongtheosautruongnhom" in thietlap:
                self._is_tudongtheosautruongnhom = thietlap["_is_tudongtheosautruongnhom"]

            if "_is_tudongtimkiemmuctieu" in thietlap:
                self._is_tudongtimkiemmuctieu = thietlap["_is_tudongtimkiemmuctieu"]

            if "_is_tudongsudungkynang" in thietlap:
                self._is_tudongsudungkynang = thietlap["_is_tudongsudungkynang"]

            if "_is_uutiennguoichoi" in thietlap:
                self._is_uutiennguoichoi = thietlap["_is_uutiennguoichoi"]

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

    def _kiemtrathuchienvohieuhoadichuyen(self):
        if self._is_yeucauvohieuhoadichuyen:
            self.moitruong.action_vohieuhoadichuyen()
        else:
            self.moitruong.action_tatvohieuhoadichuyen()

    def action_xulydichuyenuutien(self):
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

        if time.time() - self._thoidiemgapnguoichoigannhat < 10.0 and self.moitruong.get_idbandohientai() in BANDOFARMs and is_maupkhoabinh:
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Bắt gặp người chơi trên bản đồ cự thú đảo")
            return

        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieupk = diachimuctieudangchon and (self.moitruong.get_is_nguoichoi(diachimuctieudangchon) or CUONGTHI in self.moitruong.get_tendoituong(diachimuctieudangchon))
        yeucauduocchon = None
        lydochon = "KHÔNG CÓ"

        if is_yeucaunhatdo and not is_muctieupk:
            yeucauduocchon = self._yeucaunhatdo
            lydochon = "NHẶT ĐỒ"
        elif self._yeucaukhaikhoang and not is_muctieupk:
            yeucauduocchon = self._yeucaukhaikhoang
            lydochon = "KHAI KHOÁNG"
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
            hientai = time.time()

            if iddoituongmuctieudanggom != self._idmuctieudangtheokiemtraket or self.moitruong.get_is_dangvankhi():
                self._idmuctieudangtheokiemtraket = iddoituongmuctieudanggom
                self._thoidiemdungimkiemtraket = hientai
                self._toadokiemtraket = (self.moitruong.get_toadox(is_vitrihientai = True), self.moitruong.get_toadoy(is_vitrihientai = True))
                self._thoidiembatdaukiemtraket = hientai
            else:
                curr_x = self.moitruong.get_toadox(is_vitrihientai = True)
                curr_y = self.moitruong.get_toadoy(is_vitrihientai = True)

                khoangcachdadichuyen = math.dist((curr_x, curr_y), self._toadokiemtraket)

                if hientai - self._thoidiembatdaukiemtraket > 3.0:
                    if khoangcachdadichuyen < 1.0:
                        is_quai = False
                        if diachimuctieudanggom:
                            if self.moitruong.get_is_nhanvattontai(diachimuctieudanggom) and self.moitruong.get_idloainhanvat(diachimuctieudanggom) == LOAIMUCTIEU_QUAIVATHOACNPC:
                                is_quai = True

                        if is_quai:
                            print(f"[DEBUG-MOVE] KẸT TƯỜNG/GÓC LAG khi đến QUÁI {hex(iddoituongmuctieudanggom)}. Blacklist 120s.")
                            self._idmuctieubiloi_map[iddoituongmuctieudanggom] = hientai
                        else:
                            print(f"[DEBUG-MOVE] KẸT khi di chuyển. Reset hành động.")

                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                        self._idmuctieudangtheokiemtraket = 0
                        self._thoidiemdungimkiemtraket = 0.
                        return
                    else:
                        self._toadokiemtraket = (curr_x, curr_y)
                        self._thoidiembatdaukiemtraket = hientai
        else:
            self._idmuctieudangtheokiemtraket = 0
            self._thoidiemdungimkiemtraket = 0.

        if yeucauduocchon:
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
            if diachicosothongtinnhanvatmuctieudangchon := self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon():
                if self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon) or CUONGTHI in self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon):
                    break

            if self._is_tudongbattheosaunhom and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THEOSAUNHOM,), True, is_hieuungcoloi = 1):
                self.moitruong.action_battheosaunhom(2.)

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
                "khoangcachtoida": 0  # max(0, khoangcachtoidatruongnhom - 1.5)
            }
            break
        return

    def _tinhtoankhoangcachtoidatruongnhomphuhop(self):
        khoangcachtoidatruongnhom = self._khoangcachtoidatruongnhom
        diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon) or CUONGTHI not in self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon):
            khoangcachtoidatruongnhom -= 6.
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
        if self._is_tudongtimkiemmuctieu:
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

            hientai = time.time()
            idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if hientai - v > 120]
            for k in idcanxoas:
                del self._idmuctieubiloi_map[k]

            i = 0
            demmuctieugan3 = 0
            demmuctieugan5 = 0
            demmuctieugan7 = 0
            demmuctieugan9 = 0

            while True:
                idbandohientai = self.moitruong.get_idbandohientai()
                is_bandokhongpk = idbandohientai in BANDOKHONGPKs

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
                is_muctieudangchonlanguoichoi = False
                is_muctieudangchonpk = False
                
                if diachicosothongtinnhanvatmuctieudangchon:
                    tendoituongmuctieudangchon = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)
                    is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                    is_muctieudangchonlacuongthi = CUONGTHI in tendoituongmuctieudangchon
                    is_muctieudangchonpk = is_muctieudangchonlanguoichoi or is_muctieudangchonlacuongthi

                    is_boquamuctieuhientai = False

                    if is_bandokhongpk and is_muctieudangchonpk:
                        is_boquamuctieuhientai = True
                    elif not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                        is_boquamuctieuhientai = True
                    elif tendoituongmuctieudangchon in TENMUCTIEUKHONGTANCONGs:
                        is_boquamuctieuhientai = True
                    elif "Noel" in tendoituongmuctieudangchon:
                        is_boquamuctieuhientai = True
                    elif self._is_chidanhnguoichoi and not is_muctieudangchonpk:
                        is_boquamuctieuhientai = True
                    elif self._tenmuctieutancongs and tendoituongmuctieudangchon not in self._tenmuctieutancongs:
                        is_boquamuctieuhientai = True
                    elif self._tenmuctieukhongtancongs and tendoituongmuctieudangchon in self._tenmuctieukhongtancongs:
                        is_boquamuctieuhientai = True
                    elif is_muctieudangchonlacuongthi and TENNGUOICHOICUNGBANGs and any("( {} )".format(tennguoichoicungbang) in tendoituongmuctieudangchon for tennguoichoicungbang in TENNGUOICHOICUNGBANGs):
                        is_boquamuctieuhientai = True
                    elif is_muctieudangchonpk and self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieudangchon) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                        is_boquamuctieuhientai = True
                    elif is_muctieudangchonpk and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BISAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                        is_boquamuctieuhientai = True
                    elif is_muctieudangchonpk and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                        is_boquamuctieuhientai = True
                    elif self.moitruong.get_idmaupk() == MAUPK_HOABINH and is_muctieudangchonpk:
                        is_boquamuctieuhientai = True
                    elif idbandohientai == BANDO_CHIENTRUONG:
                        if self.moitruong.get_idphechientruong() == self.moitruong.get_idphechientruong(diachicosothongtinnhanvatmuctieudangchon):
                            is_boquamuctieuhientai = True
                    elif self._is_tudongvebanrac:
                        if self._idbandofarmbanrac and idbandohientai != self._idbandofarmbanrac:
                            is_boquamuctieuhientai = True

                        if not is_boquamuctieuhientai:
                            mx = self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieudangchon)
                            my = self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieudangchon)
                            if self._kiemtra_vungcam(mx, my):
                                is_boquamuctieuhientai = True

                        if not is_boquamuctieuhientai and vungdabichiemdongs:
                            qx = self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieudangchon)
                            qy = self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieudangchon)

                            khoangcachtoidenmuctieu = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                            for vung in vungdabichiemdongs:
                                khoangcachbotdenmuctieu = math.dist((qx, qy), (vung["x"], vung["y"]))
                                if khoangcachbotdenmuctieu <= 9.0:
                                    if khoangcachtoidenmuctieu > khoangcachbotdenmuctieu:
                                        is_boquamuctieuhientai = True
                                        break

                    if is_boquamuctieuhientai:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                        diachicosothongtinnhanvatmuctieudangchon = 0

                if not diachicosothongtinnhanvatmuctieudangchon and self._diachicosomuctieuduphong:
                    if self.moitruong.get_is_nhanvattontai(self._diachicosomuctieuduphong) and self.moitruong.get_is_cothetancong(self._diachicosomuctieuduphong) and self.moitruong.get_khoangcach(self._diachicosomuctieuduphong) <= KHOANGCACHTOANMANHINH:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(self._diachicosomuctieuduphong)
                        diachicosothongtinnhanvatmuctieudangchon = self._diachicosomuctieuduphong
                        self._diachicosomuctieuduphong = 0
                    else:
                        self._diachicosomuctieuduphong = 0

                diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtinnhanvatmuctieuxemxet:
                    break

                i += 1
                

                tendoituongmuctieuxemxet = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet)
                
                is_muctieudangxemxetlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieuxemxet)
                is_muctieudangxemxetlacuongthi = CUONGTHI in tendoituongmuctieuxemxet
                is_muctieudangxemxetpk = is_muctieudangxemxetlanguoichoi or is_muctieudangxemxetlacuongthi

                if time.time() - self._thoidiemphatamanthan > 5.0:
                    if is_muctieudangxemxetlanguoichoi:
                        if diachicosothongtinnhanvatmuctieuxemxet != self.moitruong.get_diachicosothongtinnhanvat1() and self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatmuctieuxemxet) not in NHANVATCUAMINHs:
                            if self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                                if self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet) <= KHOANGCACHTOIDAHOPLE:
                                    print("{} Có thích khách: {}".format(self.moitruong.get_tendoituong(), self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet)))
                                    phatam("{} Có thích khách: {}".format(self.moitruong.get_tendoituong(), self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet)))
                                    self._thoidiemphatamanthan = time.time()

                if is_muctieudangxemxetlanguoichoi and self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatmuctieuxemxet) and self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatmuctieuxemxet) not in NHANVATCUAMINHs and self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet) <= self._khoangcachtimkiemmuctieu and not self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatmuctieuxemxet):
                    self._thoidiemgapnguoichoigannhat = time.time()

                if self._is_tudongvebanrac and self._idbandofarmbanrac and idbandohientai != self._idbandofarmbanrac:
                    continue

                iddoituongmuctieuxemxet = self.moitruong.get_iddoituong(diachicosothongtinnhanvatmuctieuxemxet)
                if iddoituongmuctieuxemxet in self._idmuctieubiloi_map:
                    continue

                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                if tendoituongmuctieuxemxet in TENMUCTIEUKHONGTANCONGs:
                    continue

                if idbandohientai == BANDO_CHIENTRUONG:
                    if self.moitruong.get_idphechientruong() == self.moitruong.get_idphechientruong(diachicosothongtinnhanvatmuctieuxemxet):
                        continue

                if self._tenmuctieutancongs:
                    if tendoituongmuctieuxemxet not in self._tenmuctieutancongs:
                        continue

                if self._tenmuctieukhongtancongs:
                    if tendoituongmuctieuxemxet in self._tenmuctieukhongtancongs:
                        continue

                if is_muctieudangxemxetlacuongthi and TENNGUOICHOICUNGBANGs and any("( {} )".format(tennguoichoicungbang) in tendoituongmuctieuxemxet for tennguoichoicungbang in TENNGUOICHOICUNGBANGs):
                    continue

                if self._is_chidanhnguoichoi and not is_muctieudangxemxetpk:
                    continue

                if is_bandokhongpk and is_muctieudangchonpk:
                    continue

                if self._is_tudongvebanrac:
                    mx = self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieuxemxet)
                    my = self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieuxemxet)

                    if self._kiemtra_vungcam(mx, my):
                        continue

                    if vungdabichiemdongs:
                        is_cobotcanhtranh = False
                        qx = self.moitruong.get_toadox(diachicosothongtinnhanvatmuctieuxemxet)
                        qy = self.moitruong.get_toadoy(diachicosothongtinnhanvatmuctieuxemxet)
                        khoangcachtoidenmuctieu = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet)
                        for vung in vungdabichiemdongs:
                            khoangcachbotdenmuctieu = math.dist((qx, qy), (vung["x"], vung["y"]))
                            if khoangcachbotdenmuctieu <= 9.0:
                                if khoangcachtoidenmuctieu > khoangcachbotdenmuctieu:
                                    is_cobotcanhtranh = True
                                    break
                        if is_cobotcanhtranh:
                            continue

                diachicosothongtinnhanvattruongnhom = self.moitruong.get_diachicosothongtinnhanvattruongnhom()

                is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom() and diachicosothongtinnhanvattruongnhom

                if is_anhhuongboitruongnhom:
                    khoangcachmuctieuxemxet = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet, diachicosothongtinnhanvattruongnhom)
                    if khoangcachmuctieuxemxet >= self._khoangcachtimkiemmuctieu:
                        continue
                else:
                    khoangcachmuctieuxemxet = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet)
                    if khoangcachmuctieuxemxet >= self._khoangcachtimkiemmuctieu:
                        continue

                khoangcachdenbanthan = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet)

                if khoangcachdenbanthan <= 3.0:
                    demmuctieugan3 += 1

                if khoangcachdenbanthan <= 5.0:
                    demmuctieugan5 += 1

                if khoangcachdenbanthan <= 7.0:
                    demmuctieugan7 += 1

                if khoangcachdenbanthan <= 9.0:
                    demmuctieugan9 += 1

                if diachicosothongtinnhanvatmuctieuxemxet == diachicosothongtinnhanvatmuctieudangchon:
                    continue

                def _thaydoimuctieuhientai():
                    if diachicosothongtinnhanvatmuctieudangchon:
                        self._diachicosomuctieuduphong = diachicosothongtinnhanvatmuctieudangchon
                    self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvatmuctieuxemxet)

                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    _thaydoimuctieuhientai()
                    continue

                tendoituongmuctieudangchon = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)

                if self._is_uutienbaothumaoson:
                    is_muctieuxemxetlacuongthi = is_muctieudangxemxetlacuongthi
                    is_muctieudangchonlacuongthi = CUONGTHI in tendoituongmuctieudangchon if diachicosothongtinnhanvatmuctieudangchon else False

                    if is_muctieuxemxetlacuongthi:
                        if not is_muctieudangchonlacuongthi:
                            _thaydoimuctieuhientai()
                            continue
                    elif is_muctieudangchonlacuongthi:
                        continue

                if self._is_uutiennguoichoi:
                    if is_muctieudangxemxetpk:
                        if not is_muctieudangchonpk:
                            _thaydoimuctieuhientai()
                            continue
                    elif is_muctieudangchonpk:
                        continue

                if is_muctieudangchonpk and self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieudangchon) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                    if is_muctieudangxemxetpk:
                        if self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieuxemxet) > 5 or not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                            _thaydoimuctieuhientai()
                            continue

                if is_muctieudangchonpk and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BISAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                    if is_muctieudangxemxetpk:
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BISAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 0):
                            _thaydoimuctieuhientai()
                            continue

                if is_muctieudangchonpk and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                    if is_muctieudangxemxetpk:
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                            _thaydoimuctieuhientai()
                            continue

                if is_anhhuongboitruongnhom and khoangcachmuctieuxemxet < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon, diachicosothongtinnhanvattruongnhom):
                    _thaydoimuctieuhientai()
                    continue

                elif khoangcachmuctieuxemxet < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon):
                    _thaydoimuctieuhientai()
                    continue

            self._is_nhieumuctieugan3 = demmuctieugan3 >= self._soluongnhieumuctieu
            self._is_nhieumuctieugan5 = demmuctieugan5 >= self._soluongnhieumuctieu
            self._is_nhieumuctieugan7 = demmuctieugan7 >= self._soluongnhieumuctieu
            self._is_nhieumuctieugan9 = demmuctieugan9 >= self._soluongnhieumuctieu

    def action_tudongsudungvatpham(self):
        if self._is_tudongsudungvatpham:
            if self.moitruong.get_is_nhanvatdachet():
                return

            is_nhanvatchuasansang = self.moitruong.get_is_nhanvatchuasansang()
            if is_nhanvatchuasansang:
                if time.time() - self._thoidiemsudungbaothuvatphamgannhat > 1.:
                    for baothuvatpham in BAOTHUVATPHAMs:
                        if self.action_sudungvatphamhanhtrang(baothuvatpham):
                            self._thoidiemsudungbaothuvatphamgannhat = time.time()
                            break
            if not is_nhanvatchuasansang:
                if time.time() - self._thoidiemsudungbaothuvatphamgannhat < 1. and time.time() - self._thoidiemthietlaptrieuhoithudoilenhgannhat > 1.:
                    self.moitruong.action_thucthicaulenh("pf 4131.@", delay = 0.)
                    self._thoidiemthietlaptrieuhoithudoilenhgannhat = time.time()

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

            if time.time() - self._thoidiemkiemtrahieuunggannhat > 2.5:
                self._thoidiemkiemtrahieuunggannhat = time.time()

                # if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HUYETTHACH, HIEUUNGKYNANG_PHAPLUCTHACH, ), True, is_hieuungcoloi = 1):
                #     self.moitruong.action_sudungchucnangmorong5()

                if (self.moitruong.get_idbandohientai() not in BANDOKHONGPKs or self.moitruong.get_phantramnoilucconlai() < 25.) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHAPLUCTHACH,), True, is_hieuungcoloi = 1):
                    if not self.moitruong.action_timkiemvatphamhanhtrang(TIEUPHAPLUCTHACH):
                        pass
                    else:
                        self.action_sudungvatphamhanhtrang(TIEUPHAPLUCTHACH)

                if self.moitruong.get_tenmonphai() in ("camvequan", "daohoanguyen", "duongmon") and self.moitruong.get_idbandohientai() not in BANDOKHONGPKs and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HUYETTHACH,), True, is_hieuungcoloi = 1):
                    if not self.moitruong.action_timkiemvatphamhanhtrang(TIEUHUYETTHACH):
                        pass
                    else:
                        self.action_sudungvatphamhanhtrang(TIEUHUYETTHACH)

                if diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_idbandohientai() not in BANDOKHONGPKs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if self.moitruong.get_tenmonphai() == "camvequan" and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIENNGUYENDON,), macdinh = True, is_hieuungcoloi = 1):
                        self.action_sudungvatphamhanhtrang(THIENNGUYENDON)

            if self.moitruong.get_diempk() > 0:
                if not self.moitruong.action_timkiemvatphamhanhtrang(ANXAPHU):
                    pass
                else:
                    self.action_sudungvatphamhanhtrang(ANXAPHU)

            is_muctieupk = diachicosothongtinnhanvatmuctieudangchon and (self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon) or CUONGTHI in self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon))

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
            if self._is_tudongsudungkynang and self.moitruong.get_idbandohientai() not in BANDOKHONGPKs and time.time() - self._thoidiemsudungsotriduocgannhat > 2. and (phantramsinhlucconlai <= 25. or (is_muctieupk and phantramsinhlucconlai <= 75)):
                self._thoidiemsudungsotriduocgannhat = time.time()
                if not self.action_sudungvatphamhanhtrang(CAPCUUDON):
                    self.action_sudungvatphamhanhtrang(HOATLACHOAN)

            if time.time() - self._thoidiemsudungtusamdongannhat > 30. and self.moitruong.get_idnguoichoi() == 4599:
                if self.action_sudungvatphamhanhtrang(TUSAMDON):
                    self._thoidiemsudungtusamdongannhat = time.time()

    def action_xulyuutiensudungkynang(self, loaikynang, vitrikynang, diachimuctieu, khoangcachphudau = 0):
        if loaikynang == "sudungkynangkhongmuctieu":
            return self.moitruong.action_sudungkynangvitri(*vitrikynang)

        elif loaikynang == "sudungkynanglenbanthan":
            return self.moitruong.action_sudungkynangvitrilenbanthan(*vitrikynang)

        elif loaikynang == "tancongvatly":
            return self.moitruong.action_sudungtancongvatly(diachimuctieu)

        elif loaikynang == "sudungkynangmuctieu":
            return self.moitruong.action_sudungkynangvitrimuctieu(*vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu)

        elif loaikynang == "sudungkynanglendongdoi":
            return self.moitruong.action_sudungkynangvitrimuctieu(*vitrikynang, diachicosothongtinnhanvatmuctieu = diachimuctieu, is_khongkiemtracothetancong = True)

        elif loaikynang == "sudungkynangphudau":
            return self.moitruong.action_sudungkynangvitriphudau(*vitrikynang, diachicosothongtinnhanvat2 = diachimuctieu, khoangcachphudau = khoangcachphudau)

        return False

    def _action_tancong_duongmon(self):
        if not self._is_tudongsudungkynang: return
        if self._is_tudonggomquai: return self._action_sudungkynang_duongmon_canchien()

        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        hientai = time.time()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulacuongthi = diachimuctieu and CUONGTHI in self.moitruong.get_tendoituong(diachimuctieu)
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        is_muctieupk = is_muctieulanguoichoi or is_muctieulacuongthi

        idtuthehientai = self.moitruong.get_idtuthenhanvat()

        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        thoigiandungim = 0.
        if idtuthehientai == TUTHENHANVAT_DUNGIM:
            thoigiandungim = hientai - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

        is_anthan = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = True, is_hieuungcoloi = 1)
        is_bophonghanh = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BOPHONGHANH,), macdinh = False, is_hieuungcoloi = 1)
        is_bituocvukhi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, is_hieuungcoloi = 0)

        is_muctieucomatamthuat = False
        if diachimuctieu:
            is_muctieucomatamthuat = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MATAMTHUAT,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachimuctieu)

        if is_bophonghanh and not is_anthan:
            self._is_vohieuhoadichuyenanthan = True
        elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BOPHONGHANH):
            self._is_vohieuhoadichuyenanthan = False

        noilucconlai = self.moitruong.get_noilucconlai()

        danhsachuutien = [
            (VITRIKYNANG_ANTHANTHUAT, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and is_muctieupk and not is_anthan and self.moitruong.get_idbandohientai() not in (BANDO_CHU, BANDO_CHIENTRUONG), 0, None, True, True),
            (VITRIKYNANG_BISAT, "sudungkynangmuctieu", lambda: noilucconlai > 50 and is_muctieupk and is_anthan and (self._is_nhieumuctieugan9 or self.moitruong.get_phantramsinhlucconlai() < 10), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_LACTUYETVONGAN, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and is_muctieupk and not is_anthan and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACTUYETVONGAN,), True, is_hieuungcoloi = 1), 0, None, True, False),
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and diachimuctieu and not is_anthan and self.moitruong.get_idtuthenhanvat(diachimuctieu) == TUTHENHANVAT_TANCONGVATLY, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_BOPHONGHANH, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and is_anthan and diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, False, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and is_anthan and khoangcach >= KHOANGCACHSUDUNGKYNANGCANCHIEN and khoangcach < KHOANGCACHSUDUNGKYNANGCANCHIEN + 3., 0, None, False, True),
            (None, "dichuyentiepcantamxa", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, False, True),
            (VITRIKYNANG_AMKICH, "sudungkynangmuctieu", lambda: noilucconlai > 50 and is_bituocvukhi and not is_muctieucomatamthuat, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_THICHSAT, "sudungkynangmuctieu", lambda: noilucconlai > 50 and is_bituocvukhi and not is_muctieucomatamthuat, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and is_bituocvukhi and diachimuctieu and not is_anthan, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (None, "tancongvatly", lambda: is_bituocvukhi, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_NHIEPHONCHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and not is_muctieucomatamthuat and is_muctieupk and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and not is_muctieucomatamthuat and self._is_nhieumuctieugan5 and not is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_THAUCOTDINH, "sudungkynangmuctieu", lambda: noilucconlai > 50 and diachimuctieu and not is_bituocvukhi and not is_muctieucomatamthuat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_SONGLONGDOATCHAU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and diachimuctieu and not is_bituocvukhi and not is_muctieucomatamthuat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_MANTHIENHOAVU, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and not is_muctieucomatamthuat and self._is_nhieumuctieugan5 and is_muctieupk, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_AMKICH, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and not is_muctieucomatamthuat, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_HAPTINHMACHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and not is_muctieucomatamthuat and is_muctieulanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HAPTINHMACHAM,), macdinh = False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_THICHSAT, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and not is_muctieucomatamthuat, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_MAIHOACHAM, "sudungkynangmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and not is_muctieucomatamthuat, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_MATAMTHUAT, "sudungkynangkhongmuctieu", lambda: noilucconlai > 50 and not is_bituocvukhi and diachimuctieu and not is_anthan, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (None, "tancongvatly", lambda: True, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
        ]

        is_debug = False

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, muctieu_input, is_ngatdichuyen, is_ketthucvonglap = item
            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue
            diachimuctieu = muctieu_input if muctieu_input else diachimuctieu

            if not diachimuctieu and loaikynang in ("sudungkynangmuctieu", "sudungkynangphudau", "tancongvatly", "dichuyentiepcantamxa", "dichuyentiepcancanchien"): continue

            if loaikynang == "dichuyentiepcancanchien":
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    "khoangcachtoida": 0
                }
                return
            if loaikynang == "dichuyentiepcantamxa":
                nguongantoan = khoangcachyeucau - (1.5 + thoigiandungim * 2)
                if khoangcach >= nguongantoan:
                    if is_debug: print(f"[DEBUG] Position: Dist {khoangcach:.1f} >= Safe {nguongantoan:.1f} -> MOVE")
                    khoangcachgiutoida = khoangcachyeucau - (1.5 + thoigiandungim * 2) if thoigiandungim <= 4.5 else 0
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachimuctieu,
                        "khoangcachtoida": max(0, khoangcachgiutoida)
                    }
                    return
                else:
                    continue

            if loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynangphudau") and diachimuctieu:
                if khoangcach > khoangcachyeucau: continue

            if is_ngatdichuyen and idtuthehientai == TUTHENHANVAT_DICHUYEN:
                self.moitruong.action_ngatdichuyen()
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, hientai + 0.1)

            if is_debug: print(f"[DEBUG] EXECUTE: {loaikynang} - {vitrikynang}")

            offset = random.uniform(0, 1.0) if loaikynang == "sudungkynangphudau" else 0

            is_ok = self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, diachimuctieu, offset)

            if is_ok:
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, hientai + 0.1)
                self._yeucautancong = None
                if is_ketthucvonglap: return
            elif is_ketthucvonglap:
                return

    def _action_tancong_daohoanguyen(self):
        if not self._is_tudongsudungkynang: return

        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        hientai = time.time()

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        is_muctieulacuongthi = diachimuctieu and CUONGTHI in self.moitruong.get_tendoituong(diachimuctieu)
        is_muctieupk = is_muctieulanguoichoi or is_muctieulacuongthi
        khoangcach = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0
        nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai()

        thoigiandungim = 0.
        if idtuthenhanvat == TUTHENHANVAT_DUNGIM:
            thoigiandungim = hientai - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

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
            (VITRIKYNANG_TRANCOTHANUY, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_TRANCOTHANUY] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRANCOTHANUY,), True, is_hieuungcoloi = 1), 0, None, True, True),
            (VITRIKYNANG_KIMTRUNGCHAO, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KIMTRUNGCHAO] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), True, is_hieuungcoloi = 1) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMTRUNGCHAO,), True, is_hieuungcoloi = 1), 0, None, True, True),
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglenbanthan", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_HOTHEKIMCANG] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), True, is_hieuungcoloi = 1), 0, None, True, True),
            (VIRIKYNANG_NGUYENKHIQUYNGUYEN, "sudungkynangkhongmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_NGUYENKHIQUYNGUYEN] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGUYENKHIQUYNGUYEN,), True, is_hieuungcoloi = 1), 0, None, True, True),
            (VIRIKYNANG_HOTHEKIMCANG, "sudungkynanglendongdoi", lambda: diachidongdoicanbuff and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_HOTHEKIMCANG], KHOANGCACHSUDUNGKYNANGTAMXA, diachidongdoicanbuff, True, True),

            (VITRIKYNANG_DAIHAIVOLUONG, "sudungkynangkhongmuctieu", lambda: diachimuctieu and self._is_nhieumuctieugan3 and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAIHAIVOLUONG], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_DAOHOALACANH, "sudungkynangkhongmuctieu", lambda: diachimuctieu and is_muctieupk and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAOHOALACANH], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_THONKINH, "sudungkynangmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_THONKINH] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_LACKICH, "sudungkynangmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_LACKICH] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACKICH,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_KHONGTHUNHAPBACHNHAN, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieupk and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KHONGTHUNHAPBACHNHAN] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_PHONGMAQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieupk and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_PHONGMAQUYET] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachimuctieu), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_PHANTOA, "sudungkynangkhongmuctieu", lambda: diachimuctieu and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_PHANTOA] and (is_muctieupk or not self._is_nhieumuctieugan3) and self.moitruong.get_idtuthenhanvat(diachimuctieu) in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG), 0, None, True, True),
            (VITRIKYNANG_NHATQUYENBATSON, "sudungkynangmuctieu", lambda: diachimuctieu and self.moitruong.get_capdonhanvat() >= 60 and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_NHATQUYENBATSON] and (is_muctieupk or not self._is_nhieumuctieugan3), KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
            (VITRIKYNANG_HACHODAOTAM, "sudungkynangmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_HACHODAOTAM], KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),

            (VITRIKYNANG_BADONGQUYEN, "sudungkynangmuctieu", lambda: nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_BADONGQUYEN] and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (None, "dichuyentiepcancanchien", lambda: diachimuctieu and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN, 0, None, False, True),
            (None, "tancongvatly", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGCANCHIEN, None, True, True),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, muctieu_input, is_ngatdichuyen, is_ketthucvonglap = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            diachimuctieu = muctieu_input if muctieu_input else diachimuctieu
            if not diachimuctieu and loaikynang in ("sudungkynangmuctieu", "sudungkynangphudau", "tancongvatly", "dichuyentiepcancanchien"): continue

            if loaikynang == "dichuyentiepcancanchien":
                self._yeucautancong = {
                    "yeucau": YEUCAUDICHUYENTANCONG,
                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                    "diachimuctieu": diachimuctieu,
                    "khoangcachtoida": max(0, KHOANGCACHSUDUNGKYNANGCANCHIEN + 0. - thoigiandungim)
                }
                return

            if loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynangphudau") and diachimuctieu:
                dist = self.moitruong.get_khoangcach(diachimuctieu)
                if dist > khoangcachyeucau: continue

            if is_ngatdichuyen and idtuthenhanvat == TUTHENHANVAT_DICHUYEN:
                self.moitruong.action_ngatdichuyen()
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, hientai + 0.1)

            is_ok = self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, diachimuctieu)

            if is_ok:
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, hientai + 0.1)
                self._yeucautancong = None
                if is_ketthucvonglap: return
            elif is_ketthucvonglap:
                return

    def _action_tancong_vanmongcoc(self):
        if not self._is_tudongsudungkynang: return

        if self.moitruong.get_is_dangclickchuottrai(): return
        if self.moitruong.get_is_nhanvatdachet(): return
        if self.moitruong.get_is_dangvankhi(): return

        hientai = time.time()
        idnguoichoi = self.moitruong.get_idnguoichoi()

        diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        is_muctieulanguoichoi = diachimuctieu and self.moitruong.get_is_nguoichoi(diachimuctieu)
        khoangcach_muctieu = self.moitruong.get_khoangcach(diachimuctieu) if diachimuctieu else 0

        noiluc = self.moitruong.get_noilucconlai()
        phantramnoiluc = self.moitruong.get_phantramnoilucconlai()
        is_contranky = self.moitruong.action_timkiemvatphamhanhtrang(TRANKY)

        idtuthehientai = self.moitruong.get_idtuthenhanvat()
        thoigiandungim = 0.
        if idtuthehientai == TUTHENHANVAT_DUNGIM:
            thoigiandungim = hientai - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()

        diachidoituongcanhoisinh = None
        diachidoituongcanbommau = None
        diachidoituongcanbuffnoicong = None
        diachidoituongcanbuffngoaicong = None
        diachidoituongcanbuffsinhluctoida = None

        phantramsinhlucthapnhat = 100.

        idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
        danhsachdiachidoituongdangxemxet = [self.moitruong.get_diachicosothongtinnhanvat1()]
        i = -1
        while True:
            i += 1
            diachidoituongdangxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituongdangxemxet: break
            if not self.moitruong.get_is_nhanvattontai(diachidoituongdangxemxet): continue

            idnguoichoidangxemxet = self.moitruong.get_idnguoichoi(diachidoituongdangxemxet)
            if idnguoichoidangxemxet == idnguoichoi or (idnguoichoithanhviennhoms and idnguoichoidangxemxet in idnguoichoithanhviennhoms and self.moitruong.get_khoangcach(diachidoituongdangxemxet) < 12.):
                danhsachdiachidoituongdangxemxet.append(diachidoituongdangxemxet)

        for diachidoituongdangxemxet in danhsachdiachidoituongdangxemxet:
            if self.moitruong.get_is_nhanvatdachet(diachidoituongdangxemxet):
                diachidoituongcanhoisinh = diachidoituongdangxemxet
                break

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai(diachidoituongdangxemxet)

            if phantramsinhlucconlai < phantramsinhlucthapnhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = False, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 0):
                phantramsinhlucthapnhat = phantramsinhlucconlai
                diachidoituongcanbommau = diachidoituongdangxemxet

            if phantramsinhlucconlai >= 75. or self.moitruong.get_idbandohientai() in BANDOKHONGPKs:
                if not diachidoituongcanbuffnoicong and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1):
                    diachidoituongcanbuffnoicong = diachidoituongdangxemxet
                if not diachidoituongcanbuffngoaicong and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1):
                    diachidoituongcanbuffngoaicong = diachidoituongdangxemxet
                if not diachidoituongcanbuffsinhluctoida and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CUONGTHETHUAT,), macdinh = True, diachicosothongtinnhanvat = diachidoituongdangxemxet, is_hieuungcoloi = 1):
                    diachidoituongcanbuffsinhluctoida = diachidoituongdangxemxet
        
        if not any([
            diachidoituongcanhoisinh,
            diachidoituongcanbommau,
            diachidoituongcanbuffnoicong,
            diachidoituongcanbuffngoaicong,
            diachidoituongcanbuffsinhluctoida
        ]):
            self._is_khongcongidebuff = True
        else:
            self._is_khongcongidebuff = False

        danhsachuutien = [
            (VITRIKYNANG_CAITUHOANSINH, "sudungkynanglendongdoi", lambda: diachidoituongcanhoisinh, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanhoisinh, True, True),

            (VITRIKYNANG_SOTRI, "sudungkynanglendongdoi", lambda: diachidoituongcanbommau and phantramsinhlucthapnhat <= 75, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True, True),
            (VITRIKYNANG_VODINHLUUTHUY, "sudungkynanglendongdoi", lambda: diachidoituongcanbommau and phantramsinhlucthapnhat <= 75, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True, True),
            (VITRIKYNANG_CAMLOTRI, "sudungkynanglendongdoi", lambda: diachidoituongcanbommau and phantramsinhlucthapnhat <= 75, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True, True),
            (VITRIKYNANG_KHIETVANQUYET, "sudungkynanglendongdoi", lambda: diachidoituongcanbommau and phantramsinhlucthapnhat <= 75, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbommau, True, True),

            (VITRIKYNANG_KIMCHAMDOACH, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffnoicong, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffnoicong, True, True),
            (VITRIKYNANG_NGANCHAMDOACH, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffngoaicong, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffngoaicong, True, True),
            (VITRIKYNANG_CUONGTHETHUAT, "sudungkynanglendongdoi", lambda: diachidoituongcanbuffsinhluctoida, KHOANGCACHSUDUNGKYNANGTAMXA, diachidoituongcanbuffsinhluctoida, True, True),

            (VITRIKYNANG_PHONGANTHUAT, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA - 3, None, True, True),
            (VITRIKYNANG_HUYENQUANGTHIEMANH, "sudungkynangmuctieu", lambda: diachimuctieu and is_muctieulanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachimuctieu, is_hieuungcoloi = 0), KHOANGCACHSUDUNGKYNANGTAMXA - 3, None, True, True),

            (None, "dichuyentiepcantamxa", lambda: diachimuctieu, KHOANGCACHSUDUNGKYNANGTAMXA, None, False, True),
            (VITRIKYNANG_DONGIAPTRAN, "sudungkynangphudau", lambda: diachimuctieu and phantramnoiluc > 25 and is_contranky, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_KYMONTRAN, "sudungkynangphudau", lambda: diachimuctieu and phantramnoiluc > 25 and is_contranky, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
            (VITRIKYNANG_LIETPHONGQUYET, "sudungkynangmuctieu", lambda: diachimuctieu and phantramnoiluc > 25, KHOANGCACHSUDUNGKYNANGTAMXA, None, True, True),
        ]

        for i, item in enumerate(danhsachuutien):
            vitrikynang, loaikynang, dieukien, khoangcachyeucau, muctieu_input, is_ngatdichuyen, is_ketthucvonglap = item

            if callable(dieukien) and not dieukien(): continue
            if vitrikynang and not self.moitruong.get_is_kynangsansang(*vitrikynang): continue

            diachimuctieu = muctieu_input if muctieu_input else diachimuctieu
            if not diachimuctieu and loaikynang in ("sudungkynangmuctieu", "sudungkynangphudau", "tancongvatly", "dichuyentiepcantamxa"): continue

            if loaikynang == "dichuyentiepcantamxa":
                nguongantoan = khoangcachyeucau - (1.5 + thoigiandungim)
                if khoangcach_muctieu >= nguongantoan:
                    khoangcachgiutoida = khoangcachyeucau - (1.5 + thoigiandungim) if thoigiandungim <= 4.5 else 0
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachimuctieu,
                        "khoangcachtoida": max(0, khoangcachgiutoida)
                    }
                    return
                else:
                    continue

            khoangcach = self.moitruong.get_khoangcach(diachimuctieu)
            if loaikynang in ("sudungkynangmuctieu", "tancongvatly", "sudungkynangphudau") and khoangcach > khoangcachyeucau:
                continue

            if is_ngatdichuyen and idtuthehientai == TUTHENHANVAT_DICHUYEN:
                self.moitruong.action_ngatdichuyen()
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, hientai + 0.5)

            offset = random.uniform(0, 1.0) if loaikynang == "sudungkynangphudau" else 0
            is_ok = self.action_xulyuutiensudungkynang(loaikynang, vitrikynang, diachimuctieu, offset)

            if is_ok:
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, hientai + 0.8)
                self._yeucautancong = None
                if is_ketthucvonglap: return
            elif is_ketthucvonglap:
                return

    def _action_sudungkynang(self):
        self._yeucautancong = None

        if self._trangthaiveban != 0: return
        if self._is_danggomquai: return
        if self.moitruong.get_is_nhanvatchuasansang(self.moitruong.get_diachicosothongtinnhanvat1()): return
        if time.time() - self._thoidiemgapnguoichoigannhat < 10.0 and self.moitruong.get_idbandohientai() in BANDOFARMs and self.moitruong.get_idmaupk() == MAUPK_HOABINH: return

        tenmonphai = self.moitruong.get_tenmonphai()

        if hasattr(self, f"_action_tancong_{tenmonphai}"):
            getattr(self, f"_action_tancong_{tenmonphai}")()
        elif hasattr(self, f"_action_sudungkynang_{tenmonphai}"):
            getattr(self, f"_action_sudungkynang_{tenmonphai}")()

    def _action_sudungkynang_vanmongcoc(self):
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

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

            idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()
            danhsachtenthanhvien = self.moitruong.get_danhsachtennguoichoithanhviennhoms()

            i = -1
            diachicosothongtinnhanvatnguoichoithanhviennhoms = [self.moitruong.get_diachicosothongtinnhanvat1()]

            while True:
                i += 1
                diachicosothongtinnhanvatxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtinnhanvatxemxet:
                    break

                if not self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                    continue

                idnguoichoi = self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
                if self.moitruong.get_khoangcach(diachicosothongtinnhanvatxemxet) > KHOANGCACHSUDUNGKYNANGTAMXA:
                    continue

                tendoituong = self.moitruong.get_tendoituong(diachicosothongtinnhanvatxemxet)
                if idnguoichoi and idnguoichoi in idnguoichoithanhviennhoms:
                    diachicosothongtinnhanvatnguoichoithanhviennhoms.append(diachicosothongtinnhanvatxemxet)

                elif tendoituong:
                    for tenthanhvien in danhsachtenthanhvien:
                        if tenthanhvien in tendoituong:
                            diachicosothongtinnhanvatnguoichoithanhviennhoms.append(diachicosothongtinnhanvatxemxet)
                            break

            diachicosothongtinnhanvatdachet = False
            diachicosothongtinnhanvatphantramsinhlucthapnhat = False
            diachicosothongtinnhanvatphantramsinhlucthapnhatchuacolinhkhihothe = False
            phantramsinhlucconlaithapnhat = 100.
            phantramsinhlucconlaithapnhatchuacolinhkhihothe = 100.
            diachicosothongtinnhanvatchuacobuffnoicong = False
            diachicosothongtinnhanvatchuacobuffngoaicong = False
            diachicosothongtinnhanvatchuacobuffsinhluc = False

            for diachicosothongtinnhanvatnguoichoithanhviennhom in diachicosothongtinnhanvatnguoichoithanhviennhoms:
                if self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatnguoichoithanhviennhom):
                    diachicosothongtinnhanvatdachet = diachicosothongtinnhanvatnguoichoithanhviennhom
                    continue

                phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatnguoichoithanhviennhom)

                if phantramsinhlucconlai < phantramsinhlucconlaithapnhat:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 0):
                        diachicosothongtinnhanvatphantramsinhlucthapnhat = diachicosothongtinnhanvatnguoichoithanhviennhom
                        phantramsinhlucconlaithapnhat = phantramsinhlucconlai

                if phantramsinhlucconlai < phantramsinhlucconlaithapnhatchuacolinhkhihothe:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LINHKHIHOTHE,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 1):
                        diachicosothongtinnhanvatphantramsinhlucthapnhatchuacolinhkhihothe = diachicosothongtinnhanvatnguoichoithanhviennhom
                        phantramsinhlucconlaithapnhatchuacolinhkhihothe = phantramsinhlucconlai

                if phantramsinhlucconlai >= 75. or self.moitruong.get_idbandohientai() in BANDOKHONGPKs:
                    if not diachicosothongtinnhanvatchuacobuffnoicong and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 1):
                        diachicosothongtinnhanvatchuacobuffnoicong = diachicosothongtinnhanvatnguoichoithanhviennhom
                    if not diachicosothongtinnhanvatchuacobuffngoaicong and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 1):
                        diachicosothongtinnhanvatchuacobuffngoaicong = diachicosothongtinnhanvatnguoichoithanhviennhom
                    if not diachicosothongtinnhanvatchuacobuffsinhluc and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CUONGTHETHUAT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 1):
                        diachicosothongtinnhanvatchuacobuffsinhluc = diachicosothongtinnhanvatnguoichoithanhviennhom

            if diachicosothongtinnhanvatdachet and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAITUHOANSINH, delay = 1.):
                is_ngatdichuyen = True
                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CAITUHOANSINH, diachicosothongtinnhanvatdachet, is_khongkiemtracothetancong = True)
                break

            if diachicosothongtinnhanvatphantramsinhlucthapnhat:
                if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SOTRI):
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_SOTRI, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                    break
                if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VODINHLUUTHUY):
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VODINHLUUTHUY, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                    break
                if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAMLOTRI):
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CAMLOTRI, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                    break
                if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHIETVANQUYET):
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KHIETVANQUYET, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                    break

            if diachicosothongtinnhanvatphantramsinhlucthapnhatchuacolinhkhihothe:
                if phantramsinhlucconlaithapnhatchuacolinhkhihothe <= 75 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LINHKHIHOTHE):
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LINHKHIHOTHE, diachicosothongtinnhanvatphantramsinhlucthapnhatchuacolinhkhihothe, is_khongkiemtracothetancong = True)
                    break

            if diachicosothongtinnhanvatchuacobuffnoicong and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCHAMDOACH):
                is_ngatdichuyen = True
                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KIMCHAMDOACH, diachicosothongtinnhanvatchuacobuffnoicong, is_khongkiemtracothetancong = True)
                break
            if diachicosothongtinnhanvatchuacobuffngoaicong and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGANCHAMDOACH):
                is_ngatdichuyen = True
                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGANCHAMDOACH, diachicosothongtinnhanvatchuacobuffngoaicong, is_khongkiemtracothetancong = True)
                break
            if diachicosothongtinnhanvatchuacobuffsinhluc and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CUONGTHETHUAT):
                is_ngatdichuyen = True
                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CUONGTHETHUAT, diachicosothongtinnhanvatchuacobuffsinhluc, is_khongkiemtracothetancong = True)
                break

            if diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom()
                if thoigiantuthenhanvatdungim > 0.5 and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA - 3:
                    if thoigiantuthenhanvatdungim > 4.5:
                        khoangcachgiutoida = 0
                    else:
                        khoangcachgiutoida = KHOANGCACHSUDUNGKYNANGTAMXA - (1.5 + thoigiantuthenhanvatdungim)

                    if not is_anhhuongboitruongnhom:
                        self._yeucautancong = {
                            "yeucau": YEUCAUDICHUYENTANCONG,
                            "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                            "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                            "khoangcachtoida": khoangcachgiutoida
                        }
                    break
                else:
                    if is_muctieudangchonlanguoichoi and self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                        if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA - 3:
                            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGANTHUAT):
                                is_ngatdichuyen = True
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGANTHUAT)
                                break
                            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYENQUANGTHIEMANH):
                                is_ngatdichuyen = True
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HUYENQUANGTHIEMANH)
                                break
                    if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                        phantramnoiluc = int(self.moitruong.get_noilucconlai() * 100 / self.moitruong.get_noiluctoida())
                        is_contranky = self.moitruong.action_timkiemvatphamhanhtrang(TRANKY)
                        if phantramnoiluc > 25 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONGIAPTRAN) and is_contranky:
                            is_ngatdichuyen = True
                            # self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_DONGIAPTRAN)
                            self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_DONGIAPTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach + random.randint(0, 1))
                            break
                        if phantramnoiluc > 25 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KYMONTRAN) and is_contranky:
                            is_ngatdichuyen = True
                            # self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KYMONTRAN)
                            self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KYMONTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach + random.randint(-1, 0))
                            break
                        # if phantramnoiluc > 25 and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHAYMAU,), diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, macdinh = True, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGVUKINHTHIEN):
                        #     is_ngatdichuyen = True
                        #     self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGVUKINHTHIEN)
                        #     break
                        if phantramnoiluc > 25 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LIETPHONGQUYET):
                            is_ngatdichuyen = True
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LIETPHONGQUYET)
                            break

            break
        if is_ngatdichuyen:
            self.moitruong.action_ngatdichuyen()

    def _action_sudungkynang_maoson(self):
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

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

            noilucconlai = self.moitruong.get_noilucconlai()
            phantramnoilucconlai = self.moitruong.get_phantramnoilucconlai()

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
            if phantramsinhlucconlai > 25 and phantramnoilucconlai <= 50 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYETMACHU):
                if idtuthenhanvat not in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_HUYETMACHU)
                break

            if noilucconlai > 150 and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THANTUEPHAPCHU,), macdinh = True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THANTUEPHAPCHU):
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_THANTUEPHAPCHU)
                break

            iddoituongbaothumaoson = self.moitruong.get_iddoituongbaothumaoson()
            tendoituongbaothumaoson = self.moitruong.get_tendoituongbaothumaoson()

            if noilucconlai > 150 and iddoituongbaothumaoson and QUYTOT in tendoituongbaothumaoson:
                phantramnoilucconlaibaothummaoson = self.moitruong.get_phantramnoilucconlaibaothumaoson()
                if phantramnoilucconlaibaothummaoson < 50:
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DITINHDAIPHAP):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DITINHDAIPHAP)
                        break

            if iddoituongbaothumaoson:
                if phantramsinhlucconlai <= 33 and any(tenbaothuhiente in tendoituongbaothumaoson for tenbaothuhiente in (QUYTOT, THIENBINH)):
                    if self.moitruong.get_is_dangnamtrongnhom():
                        if noilucconlai > 150 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MENHTE):
                            is_ngatdichuyen = True
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MENHTE)
                            break
                    else:
                        if noilucconlai > 150 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYETTE):
                            is_ngatdichuyen = True
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_HUYETTE)
                            break

            else:
                if noilucconlai > 150 and self.moitruong.action_timkiemvatphamhanhtrang(BUAGIAY) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TRIEUHOITHIENBINH) and (not self._is_nhieumuctieugan5 or phantramsinhlucconlai <= 33):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                    if idtuthenhanvat not in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TRIEUHOITHIENBINH, delay = 0.25)
                    break

            if diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                thoigiantuthenhanvatkhongdichuyen = time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() if idtuthenhanvat != TUTHENHANVAT_DICHUYEN else 0.

                is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom()
                khoangcachhieuqua = KHOANGCACHSUDUNGKYNANGTAMXA
                if thoigiantuthenhanvatdungim > 0.5 and khoangcach > khoangcachhieuqua:
                    if thoigiantuthenhanvatdungim > 4.5:
                        khoangcachgiutoida = 0
                    else:
                        khoangcachgiutoida = khoangcachhieuqua - (1.5 + thoigiantuthenhanvatdungim)

                    if not is_anhhuongboitruongnhom:
                        self._yeucautancong = {
                            "yeucau": YEUCAUDICHUYENTANCONG,
                            "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                            "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                            "khoangcachtoida": khoangcachgiutoida
                        }
                    break
                else:
                    if noilucconlai > 50 and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LOIDONGCUUTHIEN):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                        if idtuthenhanvat not in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LOIDONGCUUTHIEN, delay = 0.25)
                        break
                    if noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHUCMAQUYET):
                        is_ngatdichuyen = True
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHUCMAQUYET)
                        break

            break
        if is_ngatdichuyen:
            self.moitruong.action_ngatdichuyen()

    def _action_sudungkynang_duongmon(self):
        if not self._is_tudongsudungkynang:
            return
        if self._is_tudonggomquai:
            return self._action_sudungkynang_duongmon_canchien()
        is_ngatdichuyen = False
        while True:
            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self.moitruong.get_is_dangvankhi():
                break
            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            is_muctieudangchonlanguoichoi = diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()

            is_anthan = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = True, is_hieuungcoloi = 1)
            is_bophonghanh = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BOPHONGHANH,), macdinh = False, is_hieuungcoloi = 1)

            if is_bophonghanh and not is_anthan:
                self._is_vohieuhoadichuyenanthan = True

            is_bophonghanhsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BOPHONGHANH)
            is_songlongdoatchausansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SONGLONGDOATCHAU)

            if is_bophonghanhsansang:
                self._is_vohieuhoadichuyenanthan = False

            if not is_anthan and is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_ANTHANTHUAT):
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_ANTHANTHUAT)
                break

            if not is_anthan and is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LACTUYETVONGAN) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACTUYETVONGAN,), macdinh = True, is_hieuungcoloi = 1):
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LACTUYETVONGAN)

            if diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                if not is_anthan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MATAMTHUAT) and self.moitruong.get_idtuthenhanvat(diachicosothongtinnhanvatmuctieudangchon) == TUTHENHANVAT_TANCONGVATLY:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MATAMTHUAT)
                    break

                if is_anthan and is_bophonghanhsansang and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BOPHONGHANH)
                    break

                if 0 and khoangcach < KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DONGBANG,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5
                    }
                    break

                if khoangcach >= KHOANGCACHSUDUNGKYNANGTAMXA - (1.5 + thoigiantuthenhanvatdungim):
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


                if thoigiantuthenhanvatdungim > 0.25 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcach": KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5
                    }
                    break
                
                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    is_muctieucomatamthuat = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MATAMTHUAT,), macdinh = False, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon)
                    is_bituocvukhi = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, is_hieuungcoloi = 0)
                    if is_bituocvukhi:
                        if not is_muctieucomatamthuat:
                            if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_AMKICH):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_AMKICH)
                                break
                            if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THICHSAT):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THICHSAT)
                                break
                        if not is_anthan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MATAMTHUAT):
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MATAMTHUAT)
                            break
                        if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                            self._yeucautancong = {
                                "yeucau": YEUCAUDICHUYENTANCONG,
                                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                                "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                                "khoangcach": KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5
                            }
                            break    
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungtancongvatly(diachicosothongtinnhanvatmuctieudangchon)
                        break
                    else:
                        if not is_muctieucomatamthuat:
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MANTHIENHOAVU) and self._is_nhieumuctieugan3 and not is_muctieudangchonlanguoichoi:
                                is_ngatdichuyen = True
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_MANTHIENHOAVU)
                                break
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                                is_ngatdichuyen = True
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THAUCOTDINH)
                                break
                            if is_muctieudangchonlanguoichoi and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHIEPHONCHAM):
                                is_ngatdichuyen = True
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NHIEPHONCHAM)
                                break
                            if is_songlongdoatchausansang and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                                is_ngatdichuyen = True
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_SONGLONGDOATCHAU)
                                break

                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                                is_ngatdichuyen = True
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THAUCOTDINH)
                                break
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MANTHIENHOAVU) and self._is_nhieumuctieugan5:
                                is_ngatdichuyen = True
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_MANTHIENHOAVU)
                                break
                            if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_AMKICH):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_AMKICH)
                                break
                            if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THICHSAT):
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THICHSAT)
                                break
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MAIHOACHAM):
                                is_ngatdichuyen = True
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_MAIHOACHAM)
                                break
                            if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                                self._yeucautancong = {
                                    "yeucau": YEUCAUDICHUYENTANCONG,
                                    "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                                    "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                                    "khoangcach": KHOANGCACHSUDUNGKYNANGCANCHIEN + 1.5
                                }
                                break
                            if not is_anthan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MATAMTHUAT):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MATAMTHUAT)
                                break
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH):
                                is_ngatdichuyen = True
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THAUCOTDINH)
                                break
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungtancongvatly(diachicosothongtinnhanvatmuctieudangchon)
                        break
            break
        if is_ngatdichuyen:
            self.moitruong.action_ngatdichuyen()

    def _action_sudungkynang_duongmon_canchien(self):
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
            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            is_muctieudangchonlanguoichoi = diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
            noilucconlai = self.moitruong.get_noilucconlai()

            is_anthan = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = True, is_hieuungcoloi = 1)
            is_bophonghanh = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BOPHONGHANH,), macdinh = False, is_hieuungcoloi = 1)

            if is_bophonghanh and not is_anthan:
                self._is_vohieuhoadichuyenanthan = True

            is_bophonghanhsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BOPHONGHANH)
            is_songlongdoatchausansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SONGLONGDOATCHAU)

            if is_bophonghanhsansang:
                self._is_vohieuhoadichuyenanthan = False

            if noilucconlai > 50 and not is_anthan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_ANTHANTHUAT) and not self._is_tudonggomquai:
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_ANTHANTHUAT)
                break

            if noilucconlai > 50 and not is_anthan and is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LACTUYETVONGAN) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACTUYETVONGAN,), macdinh = True, is_hieuungcoloi = 1):
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LACTUYETVONGAN)
                break

            if diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                if noilucconlai > 50 and is_anthan and is_bophonghanhsansang and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BOPHONGHANH)
                    break

                if noilucconlai > 50 and not is_anthan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MATAMTHUAT) and self.moitruong.get_idtuthenhanvat(diachicosothongtinnhanvatmuctieudangchon) == TUTHENHANVAT_TANCONGVATLY:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MATAMTHUAT)
                    break

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and noilucconlai > 50:
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MANTHIENHOAVU) and self._is_nhieumuctieugan3 and not is_muctieudangchonlanguoichoi:
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_MANTHIENHOAVU)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THAUCOTDINH,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THAUCOTDINH)
                        break
                    if is_songlongdoatchausansang and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_SONGLONGDOATCHAU)
                        break
                    if is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHIEPHONCHAM):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NHIEPHONCHAM)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MANTHIENHOAVU) and self._is_nhieumuctieugan3 and is_muctieudangchonlanguoichoi:
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_MANTHIENHOAVU)
                        break
                    if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_AMKICH):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_AMKICH)
                        break
                    if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THICHSAT):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THICHSAT)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MAIHOACHAM):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_MAIHOACHAM)
                        break
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THAUCOTDINH)
                        break
                    if not is_anthan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MATAMTHUAT):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MATAMTHUAT)
                        break

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungtancongvatly(diachicosothongtinnhanvatmuctieudangchon)
                    break

                if khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": 0
                    }
            break
        if is_ngatdichuyen:
            self.moitruong.action_ngatdichuyen()

    def _action_sudungkynang_camvequan(self):
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

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            is_muctieudangchonlanguoichoi = diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
            nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai()

            if not diachicosothongtinnhanvatmuctieudangchon:
                if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_MANHHOBOPHAP] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MANHHOBOPHAP) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MANHHOBOPHAP,), macdinh = True, is_hieuungcoloi = 1):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MANHHOBOPHAP)
                    break

                if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_KIMSUBOGIAP] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMSUBOGIAP) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMSUBOPHAP,), macdinh = True, is_hieuungcoloi = 1):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KIMSUBOGIAP)
                    break

            if diachicosothongtinnhanvatmuctieudangchon:
                if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_SINHTUTHANLUC] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SINHTUTHANLUC) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_SINHTUTHANLUC,), macdinh = True, is_hieuungcoloi = 1):
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_SINHTUTHANLUC)
                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HOANHTAOTHIENQUAN) and not is_muctieudangchonlanguoichoi and self._is_nhieumuctieugan3:
                        if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_HOANHTAOTHIENQUAN]:
                            is_ngatdichuyen = True
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_HOANHTAOTHIENQUAN)
                        else:
                            is_ngatdichuyen = True
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            self.moitruong.action_sudungtancongvatly(diachicosothongtinnhanvatmuctieudangchon)
                            break
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_CHANTHIENNOHONG] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CHANTHIENNOHONG) and is_muctieudangchonlanguoichoi and self._is_nhieumuctieugan3:
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_CHANTHIENNOHONG)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_TRUCDAOHOANGLONG] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TRUCDAOHOANGLONG) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TRUCDAOHOANGLONG)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_THIENBONGNHATKICH] and is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THIENBONGNHATKICH) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THIENBONGNHATKICH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_LOIDINHKICH] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LOIDINHKICH):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LOIDINHKICH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_BADAONOLANG] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BADAONOLANG):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BADAONOLANG)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_GIAOLONGNHAPHAI] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_GIAOLONGNHAPHAI):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_GIAOLONGNHAPHAI)
                        break

                elif KHOANGCACHSUDUNGKYNANGTAMXA / 2. <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if idtuthenhanvat == TUTHENHANVAT_DICHUYEN and is_muctieudangchonlanguoichoi and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_PHILONGTAMCHAU] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHILONGTAMCHAU):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHILONGTAMCHAU)
                        break

                    if idtuthenhanvat == TUTHENHANVAT_DICHUYEN and is_muctieudangchonlanguoichoi and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_THIENLYTATSAT] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THIENLYTATSAT):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THIENLYTATSAT)
                        break

                if nguyenkhiconlai < 4 and self.moitruong.get_phantramsinhlucconlai() <= 65 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUANHOIVANCHUYEN):
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LUANHOIVANCHUYEN)
                    break

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungtancongvatly(diachicosothongtinnhanvatmuctieudangchon)
                    break

                if khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": 0
                    }
            break

        if is_ngatdichuyen:
            self.moitruong.action_ngatdichuyen()

    def _action_sudungkynang_thucson(self):
        if self._is_thucsondao:
            if self.moitruong.get_capdonhanvat() > 25:
                self._action_sudungkynang_thucsondao()
            else:
                self._action_sudungkynang_thucsondaolvthap()
        else:
            self._action_sudungkynang_thucsonkiem()

    def _action_sudungkynang_thucsonkiem(self):
        if not self._is_tudongsudungkynang:
            return

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
                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG, HIEUUNGKYNANG_BANGPHACHNGANTAM), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_muctieubikhoaphapbao = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHOAPHAPBAO,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_muctieuchaytron = self.moitruong.get_is_muctieuchaytron(diachicosothongtinnhanvatmuctieudangchon)
                is_cothetancong = self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)

            is_duoitheonguoichoi = is_muctieudangchonlanguoichoi and khoangcach >= 6. and is_muctieuchaytron

            if not diachicosothongtinnhanvatmuctieudangchon or not is_muctieudangchonlanguoichoi:
                if self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                        break
                if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                    break
                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                    break
                if self.moitruong.get_idbandohientai() in BANDOKHONGPKs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGPHACHNGANTAM):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BANGPHACHNGANTAM)
                        break

                j = -1

                idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

                while True:
                    j += 1
                    diachicosothongtinnhanvatxemxet = self.moitruong.get_diachicosothongtindoituongx(j)
                    if not diachicosothongtinnhanvatxemxet:
                        break
                    if not self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                        continue
                    idnguoichoi = self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
                    if not idnguoichoi:
                        continue

                    if idnguoichoi in idnguoichoithanhviennhoms and self.moitruong.get_khoangcach(diachicosothongtinnhanvatxemxet) <= KHOANGCACHSUDUNGKYNANGTAMXA:
                        if not self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatxemxet):
                            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), diachicosothongtinnhanvat = diachicosothongtinnhanvatxemxet, macdinh = True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TIEUCHUTHIEN, diachicosothongtinnhanvatmuctieu = diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                break

            is_bandocuthudao = self.moitruong.get_idbandohientai() in BANDOFARMs

            if phantramsinhlucconlai <= 25 or (is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 50) or (is_bandocuthudao and is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 75):
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH)
                    break
            if is_bandocuthudao and is_muctieudangchonlanguoichoi and time.time() - self._thoidiemsudungphihanhphugannhat > 1. and phantramsinhlucconlai <= 25. and not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH) and self.moitruong.get_thoigianconlaihieuungtienthanvodich(macdinh = 2.5) < 2.:
                self._thoidiemsudungphihanhphugannhat = time.time()
                self.action_sudungvatphamhanhtrang(PHIHANHPHU)
                break

            if diachicosothongtinnhanvatmuctieudangchon and is_cothetancong:
                # if not self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA):
                #     self._solansudungkhaithientichdia = 0

                if 0 and is_duoitheonguoichoi:
                    if idtuthenhanvat == TUTHENHANVAT_DICHUYEN and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUUTINHTRUYMANG)
                    else:
                        thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                        self._yeucautancong = {
                            "yeucau": YEUCAUDICHUYENTANCONG,
                            "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                            "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                            "khoangcachtoida": khoangcach - thoigiantuthenhanvatdungim - 3.
                        }

                # elif is_muctieudangchonlanguoichoi and khoangcach <= 3 and idtuthenhanvat == TUTHENHANVAT_DICHUYEN:
                #     if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA, delay = min(1., 0.1 * self._solansudungkhaithientichdia)):
                #         is_ok = self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - KHOANGCACHSUDUNGKYNANGTAMXA)
                #         if is_ok:
                #             self._solansudungkhaithientichdia += 1

                elif 1 or not is_duoitheonguoichoi:
                    thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                    if thoigiantuthenhanvatdungim > 0.5 and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA:
                        if thoigiantuthenhanvatdungim > 4.5:
                            khoangcachgiutoida = 0
                        else:
                            khoangcachgiutoida = KHOANGCACHSUDUNGKYNANGTAMXA - max(1.5 + thoigiantuthenhanvatdungim, 0 if is_muctieudangchonlanguoichoi or not self.moitruong.get_is_truongnhom() else 9)

                        self._yeucautancong = {
                            "yeucau": YEUCAUDICHUYENTANCONG,
                            "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                            "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                            "khoangcachtoida": khoangcachgiutoida
                        }
                        break
                    else:
                        if self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN, HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_THIEUDOT), macdinh = False, is_hieuungcoloi = 0):
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                                break
                        elif is_muctieudangchonlanguoichoi and not is_muctieudangchonbichoang and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LANGKHONGCHIHUYET):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LANGKHONGCHIHUYET)
                            break
                        elif is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not is_muctieudangchonbichoang and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUCPHACHHOASON)
                            break
                        elif is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAKHONGKICH)
                            break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANKIEMXUYENTAM):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANKIEMXUYENTAM)
                            break
                        elif khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and not is_bandocuthudao and not is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN) and self.moitruong.get_noilucconlai() > 70:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN)
                            break
                        elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMTHUAT):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGUKIEMTHUAT)
                            break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANVUTIEUDIEU):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANVUTIEUDIEU)
                            break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGTAMTHUC):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BANGTAMTHUC)
                            break
                        elif khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN) and self.moitruong.get_noilucconlai() > 70:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN)
                            break
                        elif self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                                break
                        elif phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                            break
                        else:
                            j = -1

                            idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

                            while True:
                                j += 1
                                diachicosothongtinnhanvatxemxet = self.moitruong.get_diachicosothongtindoituongx(j)
                                if not diachicosothongtinnhanvatxemxet:
                                    break
                                if not self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                                    continue
                                idnguoichoi = self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
                                if not idnguoichoi:
                                    continue

                                if idnguoichoi in idnguoichoithanhviennhoms and self.moitruong.get_khoangcach(diachicosothongtinnhanvatxemxet) <= KHOANGCACHSUDUNGKYNANGTAMXA:
                                    if not self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatxemxet):
                                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), diachicosothongtinnhanvat = diachicosothongtinnhanvatxemxet, macdinh = True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TIEUCHUTHIEN, diachicosothongtinnhanvatmuctieu = diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                            break

                            if not is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENNHANCHILO):
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TIENNHANCHILO)
                                break
            break
        return

    def _action_sudungkynang_thucsondao(self):
        if not self._is_tudongsudungkynang:
            return

        is_khaithientichdiasansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA)
        is_luutinhtruymangsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG)

        idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
        diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
        noilucconlai = self.moitruong.get_noilucconlai()

        is_muctieudangchonlanguoichoi = False
        khoangcach = KHOANGCACHTOIDAHOPLE
        is_muctieudangchonbichoang = False
        is_cothetancong = False
        is_ngatdichuyen = False

        if diachicosothongtinnhanvatmuctieudangchon:
            is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
            khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
            is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG, HIEUUNGKYNANG_BANGPHACHNGANTAM), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
            is_cothetancong = self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)

        while True:
            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self.moitruong.get_is_dangvankhi():
                break
            
            
            if not diachicosothongtinnhanvatmuctieudangchon or not is_muctieudangchonlanguoichoi:
                if noilucconlai > 50 and self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                        break

                if noilucconlai > 50 and phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                        break

                if noilucconlai > 50 and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                        break

                if noilucconlai > 50 and self.moitruong.get_idbandohientai() in BANDOKHONGPKs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGPHACHNGANTAM):
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BANGPHACHNGANTAM)
                            break

            if noilucconlai > 50 and self.moitruong.get_idbandohientai() not in BANDOKHONGPKs and (phantramsinhlucconlai <= 25 or (is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 50)):
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH)
                    break

            if noilucconlai > 50 and diachicosothongtinnhanvatmuctieudangchon and is_cothetancong:
                if self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN, HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_THIEUDOT), macdinh = False, is_hieuungcoloi = 0):
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                        break

                is_cohieuungmatamthuat = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MATAMTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1)

                if noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and not is_cohieuungmatamthuat and is_luutinhtruymangsansang and idtuthenhanvat in (TUTHENHANVAT_DICHUYEN, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_DELAYSAUTANCONG):
                    if self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUUTINHTRUYMANG):
                        break

                if noilucconlai > 50 and khoangcach <= KHOANGCACHHIEUQUAKYNANGKHAITHIENTICHDIA and not is_cohieuungmatamthuat and is_khaithientichdiasansang and idtuthenhanvat == TUTHENHANVAT_DICHUYEN:
                    if self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach + random.randint(0, 1)):
                        break

                if noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAKHONGKICH)
                    break

                if noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs(
                        (HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, HIEUUNGKYNANG_NGANCHAMDOACH, HIEUUNGKYNANG_KIMCHAMDOACH, HIEUUNGKYNANG_CUONGTHETHUAT, HIEUUNGKYNANG_LACTUYETVONGAN, HIEUUNGKYNANG_MATAMTHUAT, HIEUUNGKYNANG_TRANCOTHANUY, HIEUUNGKYNANG_KIMTRUNGCHAO, HIEUUNGKYNANG_CANKHONNADI, HIEUUNGKYNANG_THANTUEPHAPCHU, HIEUUNGKYNANG_LINHKHIHOTHE, HIEUUNGKYNANG_MANHHOBOPHAP, HIEUUNGKYNANG_KIMSUBOPHAP, HIEUUNGKYNANG_SINHTUTHANLUC, HIEUUNGKYNANG_HOTHEKIMCANG), macdinh = 0, is_hieuungcoloi = 1,
                        diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAMATRAM)
                    break

                is_cothesudungkynangchoang = not is_muctieudangchonbichoang and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvatmuctieudangchon)
                if noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUCPHACHHOASON)
                    break

                if noilucconlai > 50 and self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                    break

                is_laydasudungkhaithientichdia = is_khaithientichdiasansang and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LAMCHAM, HIEUUNGKYNANG_ROILOAN, HIEUUNGKYNANG_CHOANG), macdinh = False, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon)

                if noilucconlai > 50 and not is_laydasudungkhaithientichdia and phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                    break

                if noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not is_laydasudungkhaithientichdia and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONDAOTRUCNHAP):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_DONDAOTRUCNHAP)
                    break

                if noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not is_laydasudungkhaithientichdia and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGHENHPHONGTRAM):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGHENHPHONGTRAM)
                    break

                is_muctieukhongbichamhayroiloan = not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LAMCHAM, HIEUUNGKYNANG_ROILOAN,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon)

                if noilucconlai > 50 and 4.5 <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and is_muctieudangchonlanguoichoi and is_cothesudungkynangchoang and is_muctieukhongbichamhayroiloan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LANGKHONGCHIHUYET):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LANGKHONGCHIHUYET)
                    break
                if noilucconlai > 50 and 4.5 <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and is_muctieudangchonlanguoichoi and is_muctieukhongbichamhayroiloan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANKIEMXUYENTAM):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANKIEMXUYENTAM)
                    break
                if noilucconlai > 50 and 4.5 <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and is_muctieudangchonlanguoichoi and is_muctieukhongbichamhayroiloan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANVUTIEUDIEU):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANVUTIEUDIEU)
                    break
                if noilucconlai > 50 and 4.5 <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and is_muctieudangchonlanguoichoi and is_muctieukhongbichamhayroiloan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGTAMTHUC):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BANGTAMTHUC)
                    break

                if noilucconlai > 50 and not is_laydasudungkhaithientichdia and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                    break

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    is_ngatdichuyen = True
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungtancongvatly(diachicosothongtinnhanvatmuctieudangchon)
                    break

                if is_laydasudungkhaithientichdia:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcach": khoangcach + 1.5
                    }
                    break
                elif khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": 0.
                    }
                    break
            break

        if self._is_khaithientichdiasansang and not is_khaithientichdiasansang:
            self._thoidiemkhaithientichdiakhongsansanggannhat = time.time()

        if self._is_luutinhtruymangsansang and not is_luutinhtruymangsansang:
            self._thoidiemluutinhtruymangkhongsansanggannhat = time.time()

        if time.time() - self._thoidiemkhaithientichdiakhongsansanggannhat < 1. or time.time() - self._thoidiemluutinhtruymangkhongsansanggannhat < 1.:
            is_ngatdichuyen = True

        if is_ngatdichuyen:
            self.moitruong.action_ngatdichuyen()

        self._is_khaithientichdiasansang = is_khaithientichdiasansang
        self._is_luutinhtruymangsansang = is_luutinhtruymangsansang

    def _action_sudungkynang_thucsondaolvthap(self):
        if not self._is_tudongsudungkynang:
            return

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

            khoangcach = KHOANGCACHTOIDAHOPLE
            is_cothetancong = False

            if diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_cothetancong = self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)

            if diachicosothongtinnhanvatmuctieudangchon and is_cothetancong:
                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_sudungkynangchoang = not is_muctieudangchonbichoang and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvatmuctieudangchon)

                if self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                    break
                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAKHONGKICH)
                    break
                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and is_sudungkynangchoang and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUCPHACHHOASON)
                    break
                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_cohieuungs(
                        (HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, HIEUUNGKYNANG_NGANCHAMDOACH, HIEUUNGKYNANG_KIMCHAMDOACH, HIEUUNGKYNANG_CUONGTHETHUAT, HIEUUNGKYNANG_LACTUYETVONGAN, HIEUUNGKYNANG_MATAMTHUAT, HIEUUNGKYNANG_TRANCOTHANUY, HIEUUNGKYNANG_KIMTRUNGCHAO, HIEUUNGKYNANG_CANKHONNADI, HIEUUNGKYNANG_THANTUEPHAPCHU, HIEUUNGKYNANG_LINHKHIHOTHE, HIEUUNGKYNANG_MANHHOBOPHAP, HIEUUNGKYNANG_KIMSUBOPHAP, HIEUUNGKYNANG_SINHTUTHANLUC, HIEUUNGKYNANG_HOTHEKIMCANG),
                        macdinh = 0, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAMATRAM)
                    break
                if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                    break
                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAMATRAM)
                        break
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONDAOTRUCNHAP):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_DONDAOTRUCNHAP)
                        break
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGHENHPHONGTRAM):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGHENHPHONGTRAM)
                        break

                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                if khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": max(0, KHOANGCACHSUDUNGKYNANGCANCHIEN - thoigiantuthenhanvatdungim)
                    }
                    break
            break

    def _action_sudungkynang_daohoanguyen(self):
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

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            is_muctieudangchonlanguoichoi = diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
            nguyenkhiconlai = self.moitruong.get_nguyenkhiconlai()

            if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_TRANCOTHANUY] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRANCOTHANUY,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TRANCOTHANUY):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TRANCOTHANUY)
                break

            if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KIMTRUNGCHAO] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_DATINCUONGLUC,), True, is_hieuungcoloi = 1) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMTRUNGCHAO,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMTRUNGCHAO):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KIMTRUNGCHAO)
                break

            if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_HOTHEKIMCANG] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VIRIKYNANG_HOTHEKIMCANG):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                self.moitruong.action_sudungkynangvitrilenbanthan(*VIRIKYNANG_HOTHEKIMCANG)
                break

            if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VIRIKYNANG_NGUYENKHIQUYNGUYEN] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGUYENKHIQUYNGUYEN,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VIRIKYNANG_NGUYENKHIQUYNGUYEN):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                self.moitruong.action_sudungkynangvitri(*VIRIKYNANG_NGUYENKHIQUYNGUYEN)
                break

            if not diachicosothongtinnhanvatmuctieudangchon:
                if self.moitruong.get_is_dangnamtrongnhom():
                    j = -1

                    idnguoichoithanhviennhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

                    while True:
                        j += 1
                        diachicosothongtinnhanvatxemxet = self.moitruong.get_diachicosothongtindoituongx(j)
                        if not diachicosothongtinnhanvatxemxet:
                            break
                        if not self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatxemxet):
                            continue
                        idnguoichoi = self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatxemxet)
                        if not idnguoichoi:
                            continue

                        if idnguoichoi in idnguoichoithanhviennhoms and self.moitruong.get_khoangcach(diachicosothongtinnhanvatxemxet) <= KHOANGCACHSUDUNGKYNANGTAMXA:
                            if not self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatxemxet):
                                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_HOTHEKIMCANG,), diachicosothongtinnhanvat = diachicosothongtinnhanvatxemxet, macdinh = True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VIRIKYNANG_HOTHEKIMCANG):
                                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VIRIKYNANG_HOTHEKIMCANG, diachicosothongtinnhanvatmuctieu = diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                    break
            elif diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    if self._is_nhieumuctieugan3 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DAIHAIVOLUONG):
                        if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAIHAIVOLUONG]:
                            is_ngatdichuyen = True
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DAIHAIVOLUONG)
                        else:
                            is_ngatdichuyen = True
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            self.moitruong.action_sudungtancongvatly(diachicosothongtinnhanvatmuctieudangchon)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAOHOALACANH] and is_muctieudangchonlanguoichoi and self._is_nhieumuctieugan3 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DAOHOALACANH):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DAOHOALACANH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_THONKINH] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THONKINH):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THONKINH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_LACKICH] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACKICH,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LACKICH):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LACKICH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KHONGTHUNHAPBACHNHAN] and is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = True, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHONGTHUNHAPBACHNHAN):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KHONGTHUNHAPBACHNHAN)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_PHONGMAQUYET] and is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC,), macdinh = True, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGMAQUYET):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGMAQUYET)
                        break
                    if self.moitruong.get_capdonhanvat() >= 60 and nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_NHATQUYENBATSON] and not self._is_nhieumuctieugan3 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHATQUYENBATSON):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.0)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NHATQUYENBATSON)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_HACHODAOTAM] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HACHODAOTAM):
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HACHODAOTAM)
                        break

                elif khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_BADONGQUYEN] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BADONGQUYEN) and thoigiantuthenhanvatdungim < 1.:
                        is_ngatdichuyen = True
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BADONGQUYEN)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    is_ngatdichuyen = True
                    self.moitruong.action_sudungtancongvatly(diachicosothongtinnhanvatmuctieudangchon)
                    break

                if khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": max(0, KHOANGCACHSUDUNGKYNANGCANCHIEN + 0. - thoigiantuthenhanvatdungim)
                    }
                    break
            break

        if is_ngatdichuyen:
            self.moitruong.action_ngatdichuyen()

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

    def battat_is_tudongdichientruong(self):
        self._is_tudongdichientruong = not self._is_tudongdichientruong
        self._trangthaidichientruong = 0
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
                elif tenvatpham in VATPHAMTUDONGNHATs:
                    is_cannhat = True
                elif VATPHAMTUDONGNHATFARMs and self.moitruong.get_idbandohientai() in BANDOFARMs and any(x in tenvatpham for x in VATPHAMTUDONGNHATFARMs):
                    is_cannhat = True
                elif self._tenvatphamnhats and tenvatpham in self._tenvatphamnhats:
                    is_cannhat = True

                if is_cannhat:
                    khoangcach = self.moitruong.get_khoangcach(diachivatpham)
                    if khoangcach <= KHOANGCACHTOANMANHINH:
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

        if time.time() - self._thoidiemgapnguoichoigannhat < 10.0 and self.moitruong.get_idbandohientai() in BANDOFARMs and self.moitruong.get_idmaupk() == MAUPK_HOABINH:
            return

        while True:
            if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT, TUTHENHANVAT_DELAYSAUTANCONG):
                break

            diachimuctieu = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            if diachimuctieu:
                if self.moitruong.get_is_nhanvattontai(diachimuctieu) and not self.moitruong.get_is_nhanvatdachet(diachimuctieu) and self.moitruong.get_is_cothetancong(diachimuctieu):
                    break

            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_dangvankhi():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self._idbandovuachet and self._is_tudongchaylenbandovuachet:
                break

            idbandohientai = self.moitruong.get_idbandohientai()
            diemdanhxungquanhs = self._diemdanhxungquanhs
            if not diemdanhxungquanhs:
                if self._is_tudongvebanrac and self._idbandofarmbanrac and self._idbandofarmbanrac != idbandohientai:
                    diemdanhxungquanhs = []
                else:
                    if idbandohientai != BANDO_CHIENTRUONG:
                        diemdanhxungquanhs = DIEMDANHXUNGQUANH_MAP.get(idbandohientai)
                    else:
                        diemdanhxungquanhs = DIEMDANHXUNGQUANH_MAP.get("{}_{}".format(idbandohientai, self.moitruong.get_idphechientruong()))
            diemdanhxungquanhs = diemdanhxungquanhs or []
            diemdanhxungquanhbandos = [dd for dd in diemdanhxungquanhs if dd[2] == idbandohientai]

            if not diemdanhxungquanhbandos:
                if time.time() - self._thoidiemphatamlacmapgannhat > 5.0:
                    if self.moitruong.get_tenmonphai() == "maoson" and self._is_tudongvebanrac:
                        self.moitruong.action_ngatdichuyen()
                        self.moitruong.action_thucthicaulenh("pf 4182.2")
                        self._thoidiemphatamlacmapgannhat = time.time()
                    elif self._is_tudongvebanrac and self._idbandofarmbanrac:
                        self.moitruong.action_ngatdichuyen()
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.)
                        self.action_sudunghoithanhphu()
                        self._thoidiemphatamlacmapgannhat = time.time()
                    else:
                        phatam("Lạc sang bản đồ lạ rồi")
                        self._thoidiemphatamlacmapgannhat = time.time()
                break

            if diemdanhxungquanhbandos:
                idnguoichoi = self.moitruong.get_idnguoichoi()
                if idnguoichoi % 2 == 0:
                    diemdanhxungquanhbandos.reverse()

                is_cantimdiemgannhat = False

                if self._iddiemdanhxungquanhhientai == -1:
                    is_cantimdiemgannhat = True
                elif not self._diemdanhxungquanhhientai:
                    is_cantimdiemgannhat = True
                elif self._diemdanhxungquanhhientai[2] != idbandohientai:
                    is_cantimdiemgannhat = True

                if self._thoidiembatdaudendiem == 0:
                    self._thoidiembatdaudendiem = time.time()

                if is_cantimdiemgannhat:
                    khoangcachgannhat = 999999.
                    iddiemdanhxungquanhgannhat = 0

                    for idx, dd in enumerate(diemdanhxungquanhbandos):
                        kc = self.moitruong.get_khoangcachdiem(dd[0], dd[1])
                        if kc < khoangcachgannhat:
                            khoangcachgannhat = kc
                            iddiemdanhxungquanhgannhat = idx

                    self._iddiemdanhxungquanhhientai = iddiemdanhxungquanhgannhat
                    self._diemdanhxungquanhhientai = diemdanhxungquanhbandos[iddiemdanhxungquanhgannhat]
                    self._thoidiembatdaudendiem = time.time()

                khoangcachdendiemhientai = self.moitruong.get_khoangcachdiem(*self._diemdanhxungquanhhientai[:-1])

                canchuyendendiemtieptheo = False

                if khoangcachdendiemhientai <= 4.0:
                    canchuyendendiemtieptheo = True
                else:
                    if time.time() - self._thoidiembatdaudendiem > 10.0:
                        canchuyendendiemtieptheo = True
                    else:
                        is_vuamoidaokhoang = (time.time() - self._thoidiemkhaikhoanggannhat < 6.0)
                        if not is_vuamoidaokhoang:
                            tuthe_hien_tai = self.moitruong.get_idtuthenhanvat()
                            if tuthe_hien_tai == TUTHENHANVAT_DUNGIM:
                                thoigian_dung_im = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimgannhat()
                                if thoigian_dung_im > 3.0:
                                    if time.time() - self._thoidiemphatamketduonggannhat > 5.0:
                                        self._thoidiemphatamketduonggannhat = time.time()
                                    canchuyendendiemtieptheo = True

                if canchuyendendiemtieptheo:
                    iddiemtieptheo = (self._iddiemdanhxungquanhhientai + 1) % len(diemdanhxungquanhbandos)
                    self._iddiemdanhxungquanhhientai = iddiemtieptheo
                    self._diemdanhxungquanhhientai = diemdanhxungquanhbandos[iddiemtieptheo]
                    self._thoidiembatdaudendiem = time.time()

                yeucautudomoi = {
                    "yeucau": YEUCAUDICHUYENDICHUYENTUDO,
                    "toadodich": self._diemdanhxungquanhhientai[:-1],
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

        if tenmonphai == "vanmongcoc" and self._is_chedobufftoanbang:
            if is_dangtrongnhom:
                if self.moitruong.get_is_truongnhom() or (self._is_khongcongidebuff and time.time() - self._thoidiemkiemtrakhongcongidebuffgannhat > 10.):
                    self._thoidiemkiemtrakhongcongidebuffgannhat = time.time()
                    self.moitruong.action_thoatkhoinhom()
            else:
                self.moitruong.action_kiemtravadongyloimoinhom(NHANVATCUNGBANGs)
            return

        if self.moitruong.get_idbandohientai() == BANDO_CHIENTRUONG and not is_dangtrongnhom:
            self.moitruong.action_kiemtravadongyloimoinhom(NHANVATCUNGBANGs)

        if not NHANVATTODOITUDONGs:
            return

        if idnguoichoi not in NHANVATTODOITUDONGs:
            return

        danhsachxungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()
        danhsachthanhviens = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

        dongdoixungquanhs = [id for id in danhsachxungquanhs if id in NHANVATTODOITUDONGs]

        if not dongdoixungquanhs and not is_dangtrongnhom:
            return

        if is_dangtrongnhom:
            idtruongnhom = self.moitruong.get_idnguoichoitruongnhom()
            if idtruongnhom and idtruongnhom not in NHANVATTODOITUDONGs and NHANVATTODOITUDONGs and NHANVATTODOITUDONGs[0] in danhsachxungquanhs and idtruongnhom not in danhsachthanhviens:
                self.moitruong.action_thoatkhoinhom()
                return

        xephangcuatoi = NHANVATTODOITUDONGs.index(idnguoichoi)
        idnguoichoixephangcaonhat = idnguoichoi
        giatrixephangcaonhat = xephangcuatoi

        for id_dongdoi in dongdoixungquanhs:
            xephangdongdoi = NHANVATTODOITUDONGs.index(id_dongdoi)
            if xephangdongdoi < giatrixephangcaonhat:
                giatrixephangcaonhat = xephangdongdoi
                idnguoichoixephangcaonhat = id_dongdoi

        if self.moitruong.get_is_truongnhom():
            if idnguoichoixephangcaonhat != idnguoichoi and idnguoichoixephangcaonhat not in danhsachthanhviens:
                if len(danhsachthanhviens) <= 1:
                    self.moitruong.action_thoatkhoinhom()
                    return

            if len(danhsachthanhviens) < 5:
                for id_dongdoi in dongdoixungquanhs:
                    if id_dongdoi not in danhsachthanhviens:
                        self.moitruong.action_moihoacxinvaonhom(id_dongdoi)
                        break

        elif is_dangtrongnhom:
            pass

        else:
            self.moitruong.action_kiemtravadongyloimoinhom(NHANVATTODOITUDONGs)

            if idnguoichoixephangcaonhat == idnguoichoi:
                if dongdoixungquanhs:
                    self.moitruong.action_moihoacxinvaonhom(dongdoixungquanhs[0])

    def action_tudongphucsinh(self):
        if self._is_tudongphucsinh:
            if self.moitruong.get_is_nhanvatdachet():
                time.sleep(2.5)
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

        is_ok = self.moitruong.action_sudungvatpham(iddoituongvatpham, is_boquaxacnhan)
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

                    if len(vitrivatphams) <= 1:
                        continue

                    for vitrivatpham in vitrivatphams[1:]:
                        is_ok = self.moitruong.action_dichuyenvatphamhanhtrang(vitrivatpham[1], vitrivatphams[0][0] + 1, delay = delay)
                        if is_ok:
                            self._thoidiemxepchongdogannhat = time.time()
                break

    def action_chantangcapdo(self):
        if self._is_chantangcapdo:
            self.moitruong.action_chantangcapdo()
        else:
            self.moitruong.action_bochantangcapdo()

    def action_tudongdieukhienbaothumaoson(self):
        if self._is_tudongdieukhienbaothumaoson:
            while True:
                if self._trangthaiveban != 0:
                    break
                if self.moitruong.get_is_nhanvatdachet():
                    break

                if self.moitruong.get_tenmonphai() not in ("maoson", "vanmongcoc"):
                    break

                iddoituongbaothumaoson = self.moitruong.get_iddoituongbaothumaoson()

                if not iddoituongbaothumaoson:
                    break

                # idhinhthuchanhvibaothumaoson = self.moitruong.get_idhinhthuchanhvibaothumaoson()
                # if idhinhthuchanhvibaothumaoson:
                #     self.moitruong.action_thucthicaulenh(f"pet {hex(iddoituongbaothumaoson)}# mode 0".replace("0x", ""))

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
                if self._is_danggomquai:
                    self.moitruong.action_ralenhbaothumaosontheosau(iddoituongbaothumaoson)
                elif diachicosothongtinnhanvatmuctieudangchon:
                    if self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon) <= KHOANGCACHTOANMANHINH:
                        iddoituongnhanvatmuctieudangchon = self.moitruong.get_iddoituong(diachicosothongtinnhanvatmuctieudangchon)
                        if iddoituongnhanvatmuctieudangchon:
                            if self.moitruong.get_idbandohientai() not in BANDOFARMs or time.time() - self._thoidiemgapnguoichoigannhat > 5. or self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon) <= 4.5:
                                self.moitruong.action_ralenhbaothumaosontancong(iddoituongbaothumaoson, iddoituongnhanvatmuctieudangchon)

                break

    def action_tudongtrieuhoibaothudautien(self):
        if self._is_tudongtrieuhoibaothudautien:
            while True:
                if self.moitruong.get_idbandohientai() not in BANDOKHONGPKs or time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() < 1.:
                    break

                if self.moitruong.get_is_dangvankhi():
                    break

                if self.moitruong.get_is_dangclickchuottrai():
                    break

                if self.moitruong.get_is_nhanvatdachet():
                    break

                if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DICHUYEN:
                    break

                if time.time() - self._thoidiemtamngungdichuyensudungkynang < 0.:
                    break

                iddoituongbaothudautien = self.moitruong.get_iddoituongbaothudautien()

                if not iddoituongbaothudautien:
                    break

                if self.moitruong.get_is_datrieuhoibaothudautien():
                    if time.time() - self._thoidiemsudungthucanbaothugannhat > 2. and self.moitruong.get_dotrungthanhbaothudautien() <= 90:
                        iddoituongcaocapbaothuthucpham = self.moitruong.action_timkiemvatphamhanhtrang(CAOCAPBAOTHUTHUCPHAM)
                        if iddoituongcaocapbaothuthucpham:
                            is_ok = self.moitruong.action_sudungvatphambaothu(iddoituongcaocapbaothuthucpham, iddoituongbaothudautien, delay = 0.5)
                            if is_ok:
                                self._thoidiemsudungthucanbaothugannhat = time.time()
                    diachicosonhanvatbaothudautien = self.moitruong.action_timkiemnhanvat(iddoituong = iddoituongbaothudautien)
                    tendoituong = self.moitruong.get_tendoituong(diachicosonhanvatbaothudautien) if diachicosonhanvatbaothudautien else ""
                    if diachicosonhanvatbaothudautien and not any(tenbaothumaoson in tendoituong for tenbaothumaoson in (CUONGTHI, QUYTOT, THIENBINH)) and time.time() - self._thoidiemthietlapbaothuchodoigannhat > 1.:
                        is_ok = self.moitruong.action_sudungkynangbaothu(iddoituongbaothudautien, 3, delay = 0.5)
                        if is_ok:
                            self._thoidiemthietlapbaothuchodoigannhat = time.time()
                    break

                if time.time() - self._thoidiemtudongtrieuhoibaothudautien > 1. and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                    is_ok = self.moitruong.action_trieuhoibaothu(iddoituongbaothudautien, delay = 0.5)
                    if is_ok:
                        self._thoidiemtudongtrieuhoibaothudautien = time.time()
                    break
                break

    def action_tudongbanrac(self):
        chutiemtaphoa = "Chá»§ Tiá»‡m Táº¡p HÃ³a"
        chutuulau = "Tá» KhÆ°Æ¡ng"
        quansuvosongthanh = "QuÃ¢n SÆ° VÃ´ Song ThÃ\xa0nh"

        diachi_npc = self.moitruong.action_timkiemnhanvat(chutiemtaphoa)
        if not diachi_npc:
            diachi_npc = self.moitruong.action_timkiemnhanvat(chutuulau)
            if not diachi_npc:
                diachi_npc = self.moitruong.action_timkiemnhanvat(quansuvosongthanh)
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
            if self.moitruong.get_is_nguoichoi(diachimuctieudangchon) or CUONGTHI in self.moitruong.get_tendoituong(diachimuctieudangchon):
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

        hientai = time.time()
        idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if hientai - v > 120.0]
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
            if "Noel" in tendoituongxemxet:
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

            if khoangcach <= KHOANGCACHTOANMANHINH:
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
                    if id_target not in self._danhsachidquaidagom and id_target not in self._idmuctieubiloi_map and 12.0 < kc_target <= KHOANGCACHTOANMANHINH:
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

        chutiemtaphoa = "Chá»§ Tiá»‡m Táº¡p HÃ³a"

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
            hientai = time.time()

            diachinpc = self.moitruong.action_timkiemnhanvat(tennhanvat = QUANSUVOSONGTHANH)
            if diachinpc:
                print("[AUTO-SELL] Đã về thành công. Chuyển sang di chuyển.")
                self._trangthaiveban = 2
                return

            if hientai - self._thoidiemhoithanhphu > 12.0 and not self.moitruong.get_is_dangvankhi():
                print("[AUTO-SELL] Đang dùng Hồi Thành Phù...")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu()
                self._thoidiemhoithanhphu = hientai

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

        if idbandohientai == 81:
            TOADOTHUDUONGSONs = [(233, 150, 81), (215, 144, 81), (219, 173, 81), (213, 160, 81), (203, 163, 81), (200, 137, 81), (184, 141, 81), (169, 130, 81), (174, 118, 81), (177, 95, 81), (165, 87, 81), (159, 102, 81), (141, 100, 81), (120, 101, 81), (119, 114, 81), (68, 81, 81), (61, 74, 81), (75, 64, 81), (49, 50, 81), (60, 42, 81), (62, 29, 81), (78, 27, 81), (96, 37, 81), (87, 62, 81), (125, 76, 81)]

            if self._index_thuduongson >= len(TOADOTHUDUONGSONs): self._index_thuduongson = 0
            curr_target = TOADOTHUDUONGSONs[self._index_thuduongson]

            self._xuly_lotrinh_chung(curr_target[0], curr_target[1], '_index_thuduongson', len(TOADOTHUDUONGSONs))

        elif idbandohientai == 82:
            TOADOTHUYHOASONs = [(188, 93, 82), (168, 102, 82), (150, 97, 82), (159, 117, 82), (182, 116, 82), (204, 115, 82), (201, 129, 82), (195, 143, 82), (179, 162, 82), (154, 151, 82), (144, 149, 82), (120, 154, 82), (111, 160, 82), (96, 154, 82), (119, 128, 82), (109, 100, 82), (60, 125, 82), (65, 115, 82), (74, 102, 82), (57, 86, 82), (111, 75, 82)]

            if self._index_thuyhoason >= len(TOADOTHUYHOASONs): self._index_thuyhoason = 0
            curr_target = TOADOTHUYHOASONs[self._index_thuyhoason]

            self._xuly_lotrinh_chung(curr_target[0], curr_target[1], '_index_thuyhoason', len(TOADOTHUYHOASONs))

        elif idbandohientai == 251:
            TOADOHAMCOCQUANs = [(215, 35, 251), (208, 59, 251), (193, 47, 251), (190, 73, 251), (174, 73, 251), (160, 75, 251), (150, 79, 251), (142, 81, 251), (135, 84, 251), (133, 99, 251), (136, 106, 251), (175, 137, 251), (187, 131, 251), (203, 136, 251), (205, 119, 251), (242, 101, 251), (252, 87, 251)]

            if self._index_hamcocquan >= len(TOADOHAMCOCQUANs): self._index_hamcocquan = 0
            curr_target = TOADOHAMCOCQUANs[self._index_hamcocquan]

            self._xuly_lotrinh_chung(curr_target[0], curr_target[1], '_index_hamcocquan', len(TOADOHAMCOCQUANs))

        else:
            hientai = time.time()
            idcanxoas = [k for k, v in self._idkhoangbiloi_map.items() if hientai - v > 120]
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
                if tendoituong and ("Khoáng" in tendoituong or "KhoÃ¡ng" in tendoituong):
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
            if time.time() - self._thoidiembatdautheokhoang > 7.0:
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

        is_dangnamtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        is_truongnhom = self.moitruong.get_is_truongnhom()
        if self.moitruong.get_idbandohientai() == BANDO_CHU and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 5.:
            diachinpc = self.moitruong.action_timkiemnhanvat(TRUONGQUALAO)
            if not diachinpc:
                return

            khoangcach = self.moitruong.get_khoangcach(diachinpc)
            if khoangcach > 12.0:
                return

            idnpc = self.moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                return
            
            if is_truongnhom and NHANVATTODOITUDONGs and self.moitruong.get_idnguoichoi() == NHANVATTODOITUDONGs[0]:
                caulenh = "tallk {}# welcome.1002".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(1.)
                caulenh = "tallk {}# welcome.1003".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(1.)
            elif is_dangnamtrongnhom:
                caulenh = "tallk {}# welcome.1003".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(1.)
            else:
                caulenh = "tallk {}# welcome.1001".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(1.)
                caulenh = "tallk {}# welcome.1003".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.0)
                time.sleep(1.)

    def action_tudonglamnhiemvusugia(self):
        if not self._is_tudonglamnhiemvusugia:
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        diachinpc = self.moitruong.action_timkiemnhanvat(SUGIANHIEMVU)

        if diachinpc and self.moitruong.get_khoangcach(diachinpc) <= 12.0:
            idnpc = self.moitruong.get_iddoituong(diachinpc)
            if idnpc:
                time.sleep(1.)
                caulenh = "talk {}# bonus.{}".format(hex(idnpc).replace("0x", ""), int(self.moitruong.get_capdonhanvat() / 10))
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0)
                time.sleep(1.)
                caulenh = "talk {}# welcome.1".format(hex(idnpc).replace("0x", ""))
                self.moitruong.action_thucthicaulenh(caulenh, delay = .0)
