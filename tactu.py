import math
import random
import time

import pymem

from hangso import *
from moitruongcu import MoiTruong
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
        self._is_phitac = False
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
        self._is_nhieumuctieugan = False
        self._soluongnhieumuctieu = 3
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

        self._thoigiantamngungauto = time.time()

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
        self._thoidiemsudungsinhkhitangannhat = time.time()  # - 300.
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
        self._is_tudongveban_maoson = False
        self._trangthaiveban = 0  # 0: Idle, 1: Đang về, 2: Đang đi shop, 3: Đang bán, 4: Đang quay lại
        self._thoidiemchuyentrangthai = 0.

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
        self._trangthailamnhiemvusugia = 0  # 0: Chưa nhận, 1: Đã nhận chờ map, 2: Đang đánh quái, 3: Về trả
        self._thoidiemlamnhiemvusugia = 0.
        self._idbandogoc_sugia = 0

        self._is_khaithientichdiasansang = False
        self._thoidiemkhaithientichdiakhongsansanggannhat = 0.
        self._is_luutinhtruymangsansang = False
        self._thoidiemluutinhtruymangkhongsansanggannhat = 0.

        self._is_yeucauvohieuhoadichuyen = False

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
            "_is_tudongveban_maoson": self._is_tudongveban_maoson,
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

            if "_is_tudongveban_maoson" in thietlap:
                self._is_tudongveban_maoson = thietlap["_is_tudongveban_maoson"]

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
        if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO):
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng vì đang dùng SKILL")
            return
        if self._trangthaiveban != 0:
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Đang tạm ngưng để về bán")
            return

        is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom()

        is_yeucaunhatdo = self._yeucaunhatdo and not is_anhhuongboitruongnhom

        if time.time() - self._thoidiemgapnguoichoigannhat < 5.0 and self.moitruong.get_idbandohientai() in BANDOCUTHUDAOs and self.moitruong.get_idmaupk() == MAUPK_HOABINH:
            if is_log: print("[DEBUG-MOVE] BỊ CHẶN: Bắt gặp người chơi trên bản đồ cự thú đảo")
            return

        yeucauduocchon = None
        lydochon = "KHÔNG CÓ"

        if is_yeucaunhatdo:
            yeucauduocchon = self._yeucaunhatdo
            lydochon = "NHẶT ĐỒ"
        elif self._yeucaukhaikhoang and not is_anhhuongboitruongnhom:
            yeucauduocchon = self._yeucaukhaikhoang
            lydochon = "KHAI KHOÁNG"
        elif self._yeucaugomquai and not is_anhhuongboitruongnhom:
            yeucauduocchon = self._yeucaugomquai
            lydochon = "GOM QUÁI"
        elif self._yeucautancong and self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs:
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
                        khoangcachtoida
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
            if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO):
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
        if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon):
            khoangcachtoidatruongnhom -= 6.
        return khoangcachtoidatruongnhom

    def _chonmuctieuantoan(self, diachicosothongtinnhanvat):
        if not diachicosothongtinnhanvat:
            return

        # idmuctieu = self.moitruong.get_iddoituong(diachicosothongtinnhanvat)
        #
        # thoidiemxuathien = self.moitruong.get_thoidiemxuathiendautien(idmuctieu)
        # hientai = time.time()
        #
        # thoigiandanhanbiet = hientai - thoidiemxuathien
        #
        # if thoidiemxuathien == 0 or thoigiandanhanbiet < 1.5:
        #     delay = random.uniform(1.2, 1.8)
        #     time.sleep(delay)
        # else:
        #     pass

        # if not self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon() and diachicosothongtinnhanvat and self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvat):
        #     time.sleep(random.uniform(1.2, 1.8))

        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(diachicosothongtinnhanvat)

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

            hientai = time.time()
            idcanxoas = [k for k, v in self._idmuctieubiloi_map.items() if hientai - v > 120]
            for k in idcanxoas:
                del self._idmuctieubiloi_map[k]

            i = 0
            demmuctieugan = 0

            while True:
                idbandohientai = self.moitruong.get_idbandohientai()
                is_bandokhongtancong = idbandohientai in BANDOKHONGTANCONGs

                diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

                is_muctieudangchonlanguoichoi = False
                if diachicosothongtinnhanvatmuctieudangchon:
                    is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                    tendoituongmuctieudangchon = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon)

                    is_boquamuctieuhientai = False

                    is_baothumaoson = any(tenbaothu in tendoituongmuctieudangchon for tenbaothu in (CUONGTHI, QUYTOT, THIENBINH))
                    if is_bandokhongtancong:
                        is_boquamuctieuhientai = True
                    elif not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                        is_boquamuctieuhientai = True
                    elif tendoituongmuctieudangchon in TENNHANVATKHONGTANCONGs:
                        is_boquamuctieuhientai = True
                    elif self._is_phitac and not is_muctieudangchonlanguoichoi and tendoituongmuctieudangchon not in VOTUHOCNHANs:
                        is_boquamuctieuhientai = True
                    elif self._tenmuctieutancongs and tendoituongmuctieudangchon not in self._tenmuctieutancongs:
                        is_boquamuctieuhientai = True
                    elif self._tenmuctieukhongtancongs and tendoituongmuctieudangchon in self._tenmuctieukhongtancongs:
                        is_boquamuctieuhientai = True
                    # elif self._is_chidanhnguoichoi and not is_muctieudangchonlanguoichoi and not is_baothumaoson:
                    elif self._is_chidanhnguoichoi and not is_muctieudangchonlanguoichoi:
                        is_boquamuctieuhientai = True
                    elif is_muctieudangchonlanguoichoi and self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieudangchon) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                        is_boquamuctieuhientai = True
                    elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BIENTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                        is_boquamuctieuhientai = True
                    elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                        is_boquamuctieuhientai = True
                    elif self.moitruong.get_idmaupk() == MAUPK_HOABINH and is_baothumaoson:
                        is_boquamuctieuhientai = True

                    if is_boquamuctieuhientai:
                        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
                        diachicosothongtinnhanvatmuctieudangchon = 0

                if is_bandokhongtancong:
                    break

                if not diachicosothongtinnhanvatmuctieudangchon and self._diachicosomuctieuduphong:
                    if self.moitruong.get_is_nhanvattontai(self._diachicosomuctieuduphong) and self.moitruong.get_is_cothetancong(self._diachicosomuctieuduphong) and self.moitruong.get_khoangcach(self._diachicosomuctieuduphong) <= KHOANGCACHTOANMANHINH:
                        self._chonmuctieuantoan(self._diachicosomuctieuduphong)
                        diachicosothongtinnhanvatmuctieudangchon = self._diachicosomuctieuduphong
                        self._diachicosomuctieuduphong = 0
                    else:
                        self._diachicosomuctieuduphong = 0

                diachicosothongtinnhanvatmuctieuxemxet = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachicosothongtinnhanvatmuctieuxemxet:
                    break

                i += 1

                is_muctieudangxemxetlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieuxemxet)

                if time.time() - self._thoidiemphatamanthan > 5.0:
                    if is_muctieudangxemxetlanguoichoi:
                        if diachicosothongtinnhanvatmuctieuxemxet != self.moitruong.get_diachicosothongtinnhanvat1():
                            if self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                                if self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet) <= KHOANGCACHTOIDAHOPLE:
                                    phatam("Có thích khách")
                                    self._thoidiemphatamanthan = time.time()

                if is_muctieudangxemxetlanguoichoi and self.moitruong.get_is_nhanvattontai(diachicosothongtinnhanvatmuctieuxemxet) and self.moitruong.get_idnguoichoi(diachicosothongtinnhanvatmuctieuxemxet) not in NHANVATTODOITUDONGs and self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieuxemxet) <= self._khoangcachtimkiemmuctieu and not self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatmuctieuxemxet):
                    self._thoidiemgapnguoichoigannhat = time.time()

                iddoituongmuctieuxemxet = self.moitruong.get_iddoituong(diachicosothongtinnhanvatmuctieuxemxet)
                if iddoituongmuctieuxemxet in self._idmuctieubiloi_map:
                    continue

                if not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieuxemxet):
                    continue

                tendoituongmuctieuxemxet = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet)
                if tendoituongmuctieuxemxet in TENNHANVATKHONGTANCONGs:
                    continue

                if self._is_phitac:
                    if not is_muctieudangxemxetlanguoichoi and tendoituongmuctieuxemxet not in VOTUHOCNHANs:
                        continue

                if self._tenmuctieutancongs:
                    if tendoituongmuctieuxemxet not in self._tenmuctieutancongs:
                        continue

                if self._tenmuctieukhongtancongs:
                    if tendoituongmuctieuxemxet in self._tenmuctieukhongtancongs:
                        continue

                tendoituongmuctieudangxemxet = self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieuxemxet)

                is_baothumaoson = any(tenbaothu in tendoituongmuctieudangxemxet for tenbaothu in (CUONGTHI, QUYTOT, THIENBINH))

                # if self._is_chidanhnguoichoi and not is_muctieudangxemxetlanguoichoi and not is_baothumaoson:
                if self._is_chidanhnguoichoi and not is_muctieudangxemxetlanguoichoi:
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
                if khoangcachdenbanthan <= 6.0:
                    demmuctieugan += 1

                if diachicosothongtinnhanvatmuctieuxemxet == diachicosothongtinnhanvatmuctieudangchon:
                    continue

                # if self.moitruong.get_idmaupk() == MAUPK_HOABINH and is_baothumaoson:
                #     continue

                def _thaydoimuctieuhientai():
                    if diachicosothongtinnhanvatmuctieudangchon:
                        self._diachicosomuctieuduphong = diachicosothongtinnhanvatmuctieudangchon
                    self._chonmuctieuantoan(diachicosothongtinnhanvatmuctieuxemxet)

                if not diachicosothongtinnhanvatmuctieudangchon or not self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    _thaydoimuctieuhientai()
                    continue

                if self._is_uutiennguoichoi:
                    if is_muctieudangxemxetlanguoichoi:
                        if not is_muctieudangchonlanguoichoi:
                            _thaydoimuctieuhientai()
                            continue
                    elif is_muctieudangchonlanguoichoi:
                        continue

                if is_muctieudangchonlanguoichoi and self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieudangchon) <= 5 and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                    if is_muctieudangxemxetlanguoichoi:
                        if self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatmuctieuxemxet) > 5 or not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TIENTHANVODICH, HIEUUNGKYNANG_KIMCUONGBATHOAIDON), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                            _thaydoimuctieuhientai()
                            continue

                if is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BIENTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                    if is_muctieudangxemxetlanguoichoi:
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BIENTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 0):
                            _thaydoimuctieuhientai()
                            continue

                if is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 1):
                    if is_muctieudangxemxetlanguoichoi:
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_ANTHANTHUAT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieuxemxet, is_hieuungcoloi = 1):
                            _thaydoimuctieuhientai()
                            continue

                if is_anhhuongboitruongnhom and khoangcachmuctieuxemxet < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon, diachicosothongtinnhanvattruongnhom):
                    _thaydoimuctieuhientai()
                    continue

                elif khoangcachmuctieuxemxet < self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon):
                    _thaydoimuctieuhientai()
                    continue

            self._is_nhieumuctieugan = demmuctieugan >= self._soluongnhieumuctieu

    def action_tudongsudungvatpham(self):
        if self._is_tudongsudungvatpham:
            if self.moitruong.get_is_nhanvatdachet():
                return

            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()

            if time.time() - self._thoidiemkiemtrahieuunggannhat > 2.5:
                self._thoidiemkiemtrahieuunggannhat = time.time()

                if self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_PHAPLUCTHACH,), True, is_hieuungcoloi = 1):
                    if not self.moitruong.action_timkiemvatphamhanhtrang(TIEUPHAPLUCTHACH):
                        pass
                    else:
                        self.action_sudungvatphamhanhtrang(TIEUPHAPLUCTHACH)

                if diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                    if is_muctieudangchonlanguoichoi and self.moitruong.get_idmaupk() != MAUPK_HOABINH:
                        if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NHANSAM,), True, is_hieuungcoloi = 1):
                            self.action_sudungvatphamhanhtrang(NHANSAM)
                        if self.moitruong.get_tenmonphai() in ("camvequan", "daohoanguyen") and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIENNGUYENDON,), macdinh = True, is_hieuungcoloi = True):
                            self.action_sudungvatphamhanhtrang(THIENNGUYENDON)

            if self.moitruong.get_diempk() > 0:
                if not self.moitruong.action_timkiemvatphamhanhtrang(ANXAPHU):
                    pass
                else:
                    self.action_sudungvatphamhanhtrang(ANXAPHU)

            is_muctieudangchonlanguoichoi = diachicosothongtinnhanvatmuctieudangchon and self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)

            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()
            if self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs and time.time() - self._thoidiemsudungsotriduocgannhat > 2. and (phantramsinhlucconlai <= 25. or (is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 75)):
                self._thoidiemsudungsotriduocgannhat = time.time()
                self.action_sudungvatphamhanhtrang(HOATLACHOAN)

    def _action_sudungkynang(self):
        self._yeucautancong = None

        if self._trangthaiveban != 0:
            return

        if self._is_danggomquai:
            return

        if time.time() - self._thoidiemgapnguoichoigannhat < 5.0 and self.moitruong.get_idbandohientai() in BANDOCUTHUDAOs and self.moitruong.get_idmaupk() == MAUPK_HOABINH:
            return

        tenmonphai = self.moitruong.get_tenmonphai()

        if hasattr(self, f"_action_sudungkynang_{tenmonphai}"):
            getattr(self, f"_action_sudungkynang_{tenmonphai}")()

    def _action_sudungkynang_vanmongcoc(self):
        if not self._is_tudongsudungkynang:
            return

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
                            # print(f"tenthanhvien: {tenthanhvien}, tendoituong: {tendoituong}, iddoituong: {hex(self.moitruong.get_iddoituong(diachicosothongtinnhanvatxemxet))}")
                            diachicosothongtinnhanvatnguoichoithanhviennhoms.append(diachicosothongtinnhanvatxemxet)
                            break

            diachicosothongtinnhanvatdachet = False
            diachicosothongtinnhanvatphantramsinhlucthapnhat = False
            phantramsinhlucconlaithapnhat = 100.
            diachicosothongtinnhanvatchuacobuffnoicong = False
            diachicosothongtinnhanvatchuacobuffngoaicong = False
            diachicosothongtinnhanvatchuacobuffsinhluc = False

            for diachicosothongtinnhanvatnguoichoithanhviennhom in diachicosothongtinnhanvatnguoichoithanhviennhoms:
                if self.moitruong.get_is_nhanvatdachet(diachicosothongtinnhanvatnguoichoithanhviennhom):
                    diachicosothongtinnhanvatdachet = diachicosothongtinnhanvatnguoichoithanhviennhom
                    break
                phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai(diachicosothongtinnhanvatnguoichoithanhviennhom)
                if phantramsinhlucconlai < phantramsinhlucconlaithapnhat and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 0):
                    diachicosothongtinnhanvatphantramsinhlucthapnhat = diachicosothongtinnhanvatnguoichoithanhviennhom
                    phantramsinhlucconlaithapnhat = phantramsinhlucconlai
                if phantramsinhlucconlai >= 75. or self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs:
                    if not diachicosothongtinnhanvatchuacobuffnoicong and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 1):
                        diachicosothongtinnhanvatchuacobuffnoicong = diachicosothongtinnhanvatnguoichoithanhviennhom
                    if not diachicosothongtinnhanvatchuacobuffngoaicong and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGANCHAMDOACH,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 1):
                        diachicosothongtinnhanvatchuacobuffngoaicong = diachicosothongtinnhanvatnguoichoithanhviennhom
                    if not diachicosothongtinnhanvatchuacobuffsinhluc and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CUONGTHETHUAT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatnguoichoithanhviennhom, is_hieuungcoloi = 1):
                        diachicosothongtinnhanvatchuacobuffsinhluc = diachicosothongtinnhanvatnguoichoithanhviennhom

            if diachicosothongtinnhanvatdachet and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAITUHOANSINH, delay = 1.):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CAITUHOANSINH, diachicosothongtinnhanvatdachet, is_khongkiemtracothetancong = True)
                break

            if diachicosothongtinnhanvatphantramsinhlucthapnhat and phantramsinhlucconlaithapnhat <= 75.:
                if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CAMLOTRI):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CAMLOTRI, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                    break
                if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHIETVANQUYET):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KHIETVANQUYET, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                    break

                if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SOTRI):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_SOTRI, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                    break
                if phantramsinhlucconlaithapnhat <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VODINHLUUTHUY):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VODINHLUUTHUY, diachicosothongtinnhanvatphantramsinhlucthapnhat, is_khongkiemtracothetancong = True)
                    break

            if diachicosothongtinnhanvatchuacobuffnoicong and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMCHAMDOACH):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KIMCHAMDOACH, diachicosothongtinnhanvatchuacobuffnoicong, is_khongkiemtracothetancong = True)
                break
            if diachicosothongtinnhanvatchuacobuffngoaicong and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGANCHAMDOACH):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGANCHAMDOACH, diachicosothongtinnhanvatchuacobuffngoaicong, is_khongkiemtracothetancong = True)
                break
            if diachicosothongtinnhanvatchuacobuffsinhluc and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CUONGTHETHUAT):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_CUONGTHETHUAT, diachicosothongtinnhanvatchuacobuffsinhluc, is_khongkiemtracothetancong = True)
                break

            is_bandocuthudao = self.moitruong.get_idbandohientai() in BANDOCUTHUDAOs

            if diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom()
                if thoigiantuthenhanvatdungim > 0.5 and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA - 3:
                    if thoigiantuthenhanvatdungim > 4.5 or is_bandocuthudao:
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
                    # if is_muctieudangchonlanguoichoi and self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon):
                    #     if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA - 3:
                    #         if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGANTHUAT):
                    #             self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    #             if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() -  self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                    #                 self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGANTHUAT)
                    #             break
                    #         elif not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYENQUANGTHIEMANH):
                    #             self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    #             if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() -  self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                    #                 self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HUYENQUANGTHIEMANH)
                    #             break
                    if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                        phantramnoiluc = int(self.moitruong.get_noilucconlai() * 100 / self.moitruong.get_noiluctoida())
                        is_contranky = self.moitruong.action_timkiemvatphamhanhtrang(TRANKY)
                        if phantramnoiluc > 25 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONGIAPTRAN) and ("Trá»™m Báº£o" in self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon) or self._is_nhieumuctieugan) and is_contranky:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_DONGIAPTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - random.randint(0, 1))
                            break
                        if phantramnoiluc > 25 and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KYMONTRAN) and ("Trá»™m Báº£o" in self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon) or self._is_nhieumuctieugan) and is_contranky:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KYMONTRAN, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach - random.randint(-1, 0))
                            break
                        if phantramnoiluc > 25 and not is_anhhuongboitruongnhom and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHAYMAU,), diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, macdinh = True, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGVUKINHTHIEN) and "Trá»™m Báº£o" in self.moitruong.get_tendoituong(diachicosothongtinnhanvatmuctieudangchon) and not self._is_nhieumuctieugan:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGVUKINHTHIEN)
                            break
                        if phantramnoiluc > 25 and not is_anhhuongboitruongnhom and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LIETPHONGQUYET) and (not self._is_nhieumuctieugan or not is_contranky):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LIETPHONGQUYET)
                            break

            break
        return

    def _action_sudungkynang_maoson(self):
        if not self._is_tudongsudungkynang:
            return

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

            if tendoituongbaothumaoson != THIENTHANTHANH:
                if iddoituongbaothumaoson:
                    if phantramsinhlucconlai <= 33 and any(tenbaothuhiente in tendoituongbaothumaoson for tenbaothuhiente in (QUYTOT, THIENBINH)):
                        if self.moitruong.get_is_dangnamtrongnhom():
                            if noilucconlai > 150 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MENHTE):
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MENHTE)
                                break
                        else:
                            if noilucconlai > 150 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HUYETTE):
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_HUYETTE)
                                break

                else:
                    if noilucconlai > 150 and self.moitruong.action_timkiemvatphamhanhtrang(BUAGIAY) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TRIEUHOITHIENBINH):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TRIEUHOITHIENBINH, delay = 1.)
                            time.sleep(1.)
                        break

            if diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                thoigiantuthenhanvatkhongdichuyen = time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() if idtuthenhanvat != TUTHENHANVAT_DICHUYEN else 0.

                is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom()
                khoangcachhieuqua = KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN  # KHOANGCACHSUDUNGKYNANGTAMXA
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
                    if noilucconlai > 50 and khoangcach <= KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN and thoigiantuthenhanvatkhongdichuyen > 0.5 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LOIDONGCUUTHIEN):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LOIDONGCUUTHIEN, delay = 1.)
                        break
                    # if not is_anhhuongboitruongnhom and noilucconlai > 50 and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHUCMAQUYET):
                    #     self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    #     if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                    #         self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHUCMAQUYET)
                    #     break

            break
        return

    def _action_sudungkynang_duongmon(self):
        if not self._is_tudongsudungkynang:
            return

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

            if noilucconlai > 25 and is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LACTUYETVONGAN) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACTUYETVONGAN,), macdinh = True, is_hieuungcoloi = 1):
                print("lac tuyet vo ngan")
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LACTUYETVONGAN)
                break

            if noilucconlai > 25 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MATAMTHUAT):
                print("ma tam thuat")
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MATAMTHUAT)
                break

            if noilucconlai > 25 and diachicosothongtinnhanvatmuctieudangchon:
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                is_anhhuongboitruongnhom = self._is_tudongtheosautruongnhom and self.moitruong.get_is_dangnamtrongnhom() and not self.moitruong.get_is_truongnhom()
                if thoigiantuthenhanvatdungim > 0.5 and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA:
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
                    if noilucconlai > 25 and not is_anhhuongboitruongnhom and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                        if is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SONGLONGDOATCHAU) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MULOA,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_SONGLONGDOATCHAU)
                            break
                        if is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHIEPHONCHAM):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NHIEPHONCHAM)
                            break
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MANTHIENHOAVU) and self._is_nhieumuctieugan:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_MANTHIENHOAVU)
                            break
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MAIHOACHAM):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                print("mai hoa cham")
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHUCMAQUYET)
                            break
                        if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THAUCOTDINH):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                print("thau cot dinh")
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THAUCOTDINH)
                            break

            break
        return

    def _action_sudungkynang_camvequan(self):
        if not self._is_tudongsudungkynang:
            return

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

            if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_MANHHOBOPHAP] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_MANHHOBOPHAP) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_MANHHOBOPHAP,), macdinh = True, is_hieuungcoloi = 1):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_MANHHOBOPHAP)
                break

            if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_KIMSUBOGIAP] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KIMSUBOGIAP) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KIMSUBOPHAP,), macdinh = True, is_hieuungcoloi = 1):
                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_KIMSUBOGIAP)
                break

            if diachicosothongtinnhanvatmuctieudangchon:
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_SINHTUTHANLUC) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_SINHTUTHANLUC,), macdinh = True, is_hieuungcoloi = 1):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_SINHTUTHANLUC)
                    break

                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_HOANHTAOTHIENQUAN] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HOANHTAOTHIENQUAN) and not is_muctieudangchonlanguoichoi and self._is_nhieumuctieugan:
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_HOANHTAOTHIENQUAN)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_TRUCDAOHOANGLONG] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TRUCDAOHOANGLONG) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TRUCDAOHOANGLONG)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_THIENBONGNHATKICH] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THIENBONGNHATKICH) and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THIENBONGNHATKICH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_LOIDINHKICH] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LOIDINHKICH):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LOIDINHKICH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_BADAONOLANG] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BADAONOLANG):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BADAONOLANG)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_GIAOLONGNHAPHAI] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_GIAOLONGNHAPHAI):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_GIAOLONGNHAPHAI)
                        break

                elif KHOANGCACHSUDUNGKYNANGTAMXA / 2. <= khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_PHILONGTAMCHAU] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHILONGTAMCHAU):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHILONGTAMCHAU)
                        break

                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGCAMVEQUAN_MAP[VITRIKYNANG_THIENLYTATSAT] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THIENLYTATSAT):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THIENLYTATSAT)
                        break

                if nguyenkhiconlai < 4 and self.moitruong.get_phantramsinhlucconlai() <= 65 and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUANHOIVANCHUYEN):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_LUANHOIVANCHUYEN)
                    break

                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.
                if thoigiantuthenhanvatdungim > 0.5 and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": 0
                    }
                    break
            break
        return

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
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                    break
                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                    break
                if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGPHACHNGANTAM):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
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
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TIEUCHUTHIEN, diachicosothongtinnhanvatmuctieu = diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                break

            is_bandocuthudao = self.moitruong.get_idbandohientai() in BANDOCUTHUDAOs

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
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LANGKHONGCHIHUYET)
                            break
                        elif is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not is_muctieudangchonbichoang and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUCPHACHHOASON)
                            break
                        elif is_muctieudangchonlanguoichoi and khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAKHONGKICH)
                            break
                        # elif is_muctieudangchonlanguoichoi and not is_muctieubikhoaphapbao and khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and self.moitruong.get_is_kynangphapbaosansang():
                        #     self.moitruong.action_sudungkynangphapbao(diachicosothongtinnhanvatmuctieudangchon)
                        #     break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANKIEMXUYENTAM):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANKIEMXUYENTAM)
                            break
                        elif khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and not is_bandocuthudao and not is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN) and self.moitruong.get_noilucconlai() > 70:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN)
                            break
                        elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMTHUAT):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGUKIEMTHUAT)
                            break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_VANVUTIEUDIEU):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_VANVUTIEUDIEU)
                            break
                        elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGTAMTHUC):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BANGTAMTHUC)
                            break
                        elif khoangcach <= KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN and is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGUKIEMPHITIEN) and self.moitruong.get_noilucconlai() > 70:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_NGUKIEMPHITIEN)
                            break
                        elif self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                            if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                                break
                        elif phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
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
                                            if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                                self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TIEUCHUTHIEN, diachicosothongtinnhanvatmuctieu = diachicosothongtinnhanvatxemxet, is_khongkiemtracothetancong = True)
                                            break

                            if not is_muctieudangchonlanguoichoi and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENNHANCHILO):
                                self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                                if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_TIENNHANCHILO)
                                break
            break
        return

    def _action_sudungkynang_thucsondao(self):
        if not self._is_tudongsudungkynang:
            return

        is_khaithientichdiasansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHAITHIENTICHDIA)
        is_luutinhtruymangsansang = self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUUTINHTRUYMANG)
        is_yeucauvohieuhoadichuyen = False

        while True:
            if self.moitruong.get_is_dangclickchuottrai():
                break
            if self.moitruong.get_is_nhanvatdachet():
                break
            if self.moitruong.get_is_dangvankhi():
                break

            is_yeucauvohieuhoadichuyen = not is_luutinhtruymangsansang and not is_khaithientichdiasansang

            idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
            diachicosothongtinnhanvatmuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
            phantramsinhlucconlai = self.moitruong.get_phantramsinhlucconlai()

            if not diachicosothongtinnhanvatmuctieudangchon:
                self._trangthaikhaithientichdia["is_danglui"] = False

            is_muctieudangchonlanguoichoi = False
            khoangcach = KHOANGCACHTOIDAHOPLE
            is_muctieudangchonbichoang = False
            is_cothetancong = False

            if diachicosothongtinnhanvatmuctieudangchon:
                is_muctieudangchonlanguoichoi = self.moitruong.get_is_nguoichoi(diachicosothongtinnhanvatmuctieudangchon)
                khoangcach = self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon)
                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG, HIEUUNGKYNANG_BANGPHACHNGANTAM), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_cothetancong = self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)

            if not diachicosothongtinnhanvatmuctieudangchon or not is_muctieudangchonlanguoichoi:
                if self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0):
                    if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                        break
                if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                        break
                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                        break
                if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 1.:
                    if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BANGPHACHNGANTAM, HIEUUNGKYNANG_LANHNGUYETTAMPHAP), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BANGPHACHNGANTAM):
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                            self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_BANGPHACHNGANTAM)
                            break

            if self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs and phantramsinhlucconlai <= 25 or (is_muctieudangchonlanguoichoi and phantramsinhlucconlai <= 50):
                if self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENTHANVODICH):
                    self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TIENTHANVODICH)
                    break

            if diachicosothongtinnhanvatmuctieudangchon and is_cothetancong:
                self._trangthaikhaithientichdia["is_danglui"] = False

                if khoangcach <= KHOANGCACHHIEUQUAKYNANGKHAITHIENTICHDIA and is_khaithientichdiasansang:
                    if idtuthenhanvat == TUTHENHANVAT_DICHUYEN:
                        if self.moitruong.action_sudungkynangvitriphudau(*VITRIKYNANG_KHAITHIENTICHDIA, diachicosothongtinnhanvatmuctieudangchon, khoangcachphudau = khoangcach):
                            break
                        break

                if khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA and is_luutinhtruymangsansang:
                    if idtuthenhanvat == TUTHENHANVAT_DICHUYEN:
                        if self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUUTINHTRUYMANG):
                            break
                        break

                if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    if is_yeucauvohieuhoadichuyen or (idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIENKHI)
                        break

                if khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    if self.moitruong.get_is_cohieuungs(HIEUUNGBATLOITHUCSONCOTHEGIAIs, macdinh = False, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TINHTAMQUYET):
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_TINHTAMQUYET)
                        break
                    elif not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAKHONGKICH):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAKHONGKICH)
                        break
                    elif not is_muctieudangchonbichoang and self.moitruong.get_is_cothegaychoang(diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LUCPHACHHOASON):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LUCPHACHHOASON)
                        break
                    elif is_muctieudangchonlanguoichoi and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, HIEUUNGKYNANG_NGANCHAMDOACH, HIEUUNGKYNANG_KIMCHAMDOACH, HIEUUNGKYNANG_CUONGTHETHUAT, HIEUUNGKYNANG_LACTUYETVONGAN, HIEUUNGKYNANG_MATAMTHUAT, HIEUUNGKYNANG_TRANCOTHANUY, HIEUUNGKYNANG_KIMTRUNGCHAO, HIEUUNGKYNANG_CANKHONNADI, HIEUUNGKYNANG_THANTUEPHAPCHU, HIEUUNGKYNANG_LINHKHIHOTHE, HIEUUNGKYNANG_MANHHOBOPHAP, HIEUUNGKYNANG_KIMSUBOPHAP, HIEUUNGKYNANG_SINHTUTHANLUC, HIEUUNGKYNANG_HOTHEKIMCANG), macdinh = 0, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAMATRAM)
                        break
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DONDAOTRUCNHAP):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_DONDAOTRUCNHAP)
                        break
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGHENHPHONGTRAM):
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGHENHPHONGTRAM)
                        break

                if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NOIKHANG,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIEUCHUTHIEN):
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrilenbanthan(*VITRIKYNANG_TIEUCHUTHIEN)
                    break

                if khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN and not self._yeucautancong:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcach": 0
                    }
                break
            break

        if self._is_khaithientichdiasansang and not is_khaithientichdiasansang:
            self._thoidiemkhaithientichdiakhongsansanggannhat = time.time()
            print("Vừa sử dụng khai thiên tịch địa")

        if self._is_luutinhtruymangsansang and not is_luutinhtruymangsansang:
            self._thoidiemluutinhtruymangkhongsansanggannhat = time.time()
            print("Vừa sử dụng lưu tinh truy mạng")

        self._is_khaithientichdiasansang = is_khaithientichdiasansang
        self._is_luutinhtruymangsansang = is_luutinhtruymangsansang
        self._is_yeucauvohieuhoadichuyen = is_yeucauvohieuhoadichuyen

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
                elif khoangcach <= KHOANGCACHSUDUNGKYNANGCANCHIEN and self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_NGOAIKHANG, HIEUUNGKYNANG_NOIKHANG, HIEUUNGKYNANG_NGANCHAMDOACH, HIEUUNGKYNANG_KIMCHAMDOACH, HIEUUNGKYNANG_CUONGTHETHUAT, HIEUUNGKYNANG_LACTUYETVONGAN, HIEUUNGKYNANG_MATAMTHUAT, HIEUUNGKYNANG_TRANCOTHANUY, HIEUUNGKYNANG_KIMTRUNGCHAO, HIEUUNGKYNANG_CANKHONNADI, HIEUUNGKYNANG_THANTUEPHAPCHU, HIEUUNGKYNANG_LINHKHIHOTHE, HIEUUNGKYNANG_MANHHOBOPHAP, HIEUUNGKYNANG_KIMSUBOPHAP, HIEUUNGKYNANG_SINHTUTHANLUC, HIEUUNGKYNANG_HOTHEKIMCANG),
                                                      macdinh = 0, is_hieuungcoloi = 1, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHAMATRAM):
                    self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                    self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHAMATRAM)
                    break
                if phantramsinhlucconlai <= 75. and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_TIENKHI):
                    if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
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
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAIHAIVOLUONG] and self._is_nhieumuctieugan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DAIHAIVOLUONG):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DAIHAIVOLUONG)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_DAOHOALACANH] and is_muctieudangchonlanguoichoi and self._is_nhieumuctieugan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_DAOHOALACANH):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_DAOHOALACANH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_THONKINH] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRONGTHUONG,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_THONKINH):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_THONKINH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_LACKICH] and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_LACKICH,), macdinh = True, is_hieuungcoloi = 0, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_LACKICH):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_LACKICH)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_KHONGTHUNHAPBACHNHAN] and is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN,), macdinh = True, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_KHONGTHUNHAPBACHNHAN):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_KHONGTHUNHAPBACHNHAN)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_PHONGMAQUYET] and is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC,), macdinh = True, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGMAQUYET):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGMAQUYET)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_NHATQUYENBATSON] and not self._is_nhieumuctieugan and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NHATQUYENBATSON):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 1.0)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NHATQUYENBATSON)
                        break
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_HACHODAOTAM] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HACHODAOTAM):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HACHODAOTAM)
                        break
                elif khoangcach <= KHOANGCACHSUDUNGKYNANGTAMXA:
                    if nguyenkhiconlai >= NGUYENKHIYEUCAUKYNANGDAOHOANGUYEN_MAP[VITRIKYNANG_BADONGQUYEN] and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BADONGQUYEN) and thoigiantuthenhanvatdungim < 1.:
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BADONGQUYEN)


                if thoigiantuthenhanvatdungim > 0. and khoangcach > KHOANGCACHSUDUNGKYNANGCANCHIEN:
                    self._yeucautancong = {
                        "yeucau": YEUCAUDICHUYENTANCONG,
                        "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                        "diachimuctieu": diachicosothongtinnhanvatmuctieudangchon,
                        "khoangcachtoida": max(0, KHOANGCACHSUDUNGKYNANGCANCHIEN + 0. - thoigiantuthenhanvatdungim)
                    }
                    break
            break

        return

    def _action_sudungkynang_conluan(self):
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
                is_muctieudangchonbichoang = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CHOANG,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_muctieubikhoaphapbao = self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_KHOAPHAPBAO,), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0)
                is_muctieuchaytron = self.moitruong.get_is_muctieuchaytron(diachicosothongtinnhanvatmuctieudangchon)
                is_cothetancong = self.moitruong.get_is_cothetancong(diachicosothongtinnhanvatmuctieudangchon)

            if not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_CANKHONNADI,), True, is_hieuungcoloi = 1) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_CANKHONNADI):
                self.moitruong.action_sudungkynangvitri(*VITRIKYNANG_CANKHONNADI)
                break

            if diachicosothongtinnhanvatmuctieudangchon and is_cothetancong:
                thoigiantuthenhanvatdungim = time.time() - self.moitruong.get_thoidiemtuthenhanvatdungimcomuctieugannhat() if idtuthenhanvat == TUTHENHANVAT_DUNGIM else 0.

                if thoigiantuthenhanvatdungim > 0.5 and khoangcach > KHOANGCACHSUDUNGKYNANGTAMXA:
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
                else:
                    if is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_THIEUDOT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_HOALONGQUYET):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_HOALONGQUYET)
                        break
                    elif is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_BIENTHANTHUAT,), macdinh = True, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_BIENTHANTHUAT):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_BIENTHANTHUAT)
                        break
                    elif is_muctieudangchonlanguoichoi and not self.moitruong.get_is_cohieuungs((HIEUUNGKYNANG_TRAMMAC, HIEUUNGKYNANG_CHOANG), False, diachicosothongtinnhanvat = diachicosothongtinnhanvatmuctieudangchon, is_hieuungcoloi = 0) and self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGMACHU):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGMACHU)
                        break
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_PHONGHOAQUYET):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_PHONGHOAQUYET)
                        break
                    elif self.moitruong.get_is_kynangsansang(*VITRIKYNANG_NGULOITHUAT):
                        self._thoidiemtamngungdichuyensudungkynang = max(self._thoidiemtamngungdichuyensudungkynang, time.time() + 0.5)
                        if idtuthenhanvat in (TUTHENHANVAT_DUNGIM, TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG) and time.time() - self.moitruong.get_thoidiemtuthenhanvatkhongdichuyen() > 0.25:
                            self.moitruong.action_sudungkynangvitrimuctieu(*VITRIKYNANG_NGULOITHUAT)
                        break
            break
        return

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

    def battat_is_phitac(self):
        self._is_phitac = not self._is_phitac
        if self._is_phitac:
            phatam("Bật phi tặc")
        else:
            phatam("Tắt phi tặc")

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

    def battat_tudongveban_maoson(self):
        self._is_tudongveban_maoson = not self._is_tudongveban_maoson
        self._trangthaiveban = 0
        if self._is_tudongveban_maoson:
            phatam("Bật tự động về bán (Mao Sơn)")
        else:
            phatam("Tắt tự động về bán")

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
        # if time.time() - self._thoidiemvutdogannhat < 2.:
        #     return
        #
        # if not self.moitruong.get_is_dayhanhtrang():
        #     return
        #
        # is_ok = self.moitruong.action_thucthicaulenh("drop ! {}#1".format(hex(iddoituongvatpham)).replace("0x", ""))
        # if is_ok:
        #     self._thoidiemvutdogannhat = time.time()
        return

    def action_nhatdo(self):
        yeucaunhatdomoi = None

        if not self._is_tudongnhatdo:
            self._yeucaunhatdo = None
            return

        if self.moitruong.get_is_dayhanhtrang():
            if time.time() - self._thoidiemphatamdayhanhtrang > 5.0:
                # phatam("Hành trang đầy")
                self._thoidiemphatamdayhanhtrang = time.time()

            self._diachicosovatphamdangnhat = False
            self._yeucaunhatdo = None
            return

        if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO):
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
                elif VATPHAMTUDONGNHATCUTHUDAOs and self.moitruong.get_idbandohientai() in BANDOCUTHUDAOs and any(x in tenvatpham for x in VATPHAMTUDONGNHATCUTHUDAOs):
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

        if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs:
            self._yeucautudo = None
            return

        if not self._is_tudongdichuyendiemdanhxungquanh:
            self._yeucautudo = None
            return

        if self._diachicosokhaikhoang:
            self._yeucautudo = None
            return

        if time.time() - self._thoidiemgapnguoichoigannhat < 5.0 and self.moitruong.get_idbandohientai() in BANDOCUTHUDAOs and self.moitruong.get_idmaupk() == MAUPK_HOABINH:
            return

        while True:
            if self.moitruong.get_idtuthenhanvat() in (TUTHENHANVAT_TANCONG, TUTHENHANVAT_SUDUNGKYNANGPHUTRO, TUTHENHANVAT_DELAYSAUTANCONG): break

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
                diemdanhxungquanhs = DIEMDANHXUNGQUANH_MAP.get(idbandohientai)

            if not diemdanhxungquanhs:
                break

            diemdanhxungquanhbandos = [dd for dd in diemdanhxungquanhs if dd[2] == idbandohientai]

            # [XỬ LÝ LẠC MAP]
            if not diemdanhxungquanhbandos:
                if self._diemdanhxungquanhs:
                    if time.time() - self._thoidiemphatamlacmapgannhat > 10.0:
                        if self.moitruong.get_tenmonphai() == "maoson":
                            if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                                print(f"[AUTO-MOVE] Lạc map {idbandohientai}. Đứng yên -> Di Tinh (pf 4182.2)")
                                self.moitruong.action_thucthicaulenh("pf 4182.2")
                                self._thoidiemphatamlacmapgannhat = time.time()
                            else:
                                pass
                        else:
                            phatam("Lạc sang bản đồ lạ rồi")
                            self._thoidiemphatamlacmapgannhat = time.time()
                break

            if diemdanhxungquanhbandos:
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
        if not self._is_tudongtodoi or not NHANVATTODOITUDONGs:
            return

        idnguoichoi = self.moitruong.get_idnguoichoi()
        if idnguoichoi not in NHANVATTODOITUDONGs:
            return

        danhsachxungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()
        danhsachthanhviens = self.moitruong.get_danhsachidnguoichoithanhviennhoms()

        dongdoixungquanhs = [id for id in danhsachxungquanhs if id in NHANVATTODOITUDONGs]

        if not dongdoixungquanhs and not self.moitruong.get_is_dangnamtrongnhom():
            return

        if self.moitruong.get_is_dangnamtrongnhom():
            idtruongnhom = self.moitruong.get_idnguoichoitruongnhom()
            if idtruongnhom and idtruongnhom not in NHANVATTODOITUDONGs and NHANVATTODOITUDONGs and NHANVATTODOITUDONGs[0] in danhsachxungquanhs and idtruongnhom not in danhsachthanhviens:
                self.moitruong.action_thoatkhoinhom(idtruongnhom)
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
                    self.moitruong.action_thoatkhoinhom(idnguoichoi)
                    return

            if len(danhsachthanhviens) < 5:
                for id_dongdoi in dongdoixungquanhs:
                    if id_dongdoi not in danhsachthanhviens:
                        self.moitruong.action_moihoacxinvaonhom(id_dongdoi)
                        break

        elif self.moitruong.get_is_dangnamtrongnhom():
            pass

        else:
            self.moitruong.action_kiemtravadongyloimoinhom(NHANVATTODOITUDONGs)

            if idnguoichoixephangcaonhat == idnguoichoi:
                if dongdoixungquanhs:
                    self.moitruong.action_moihoacxinvaonhom(dongdoixungquanhs[0])

    def action_tudongphucsinh(self):
        if self._is_tudongphucsinh:
            while True:
                if not self.moitruong.get_is_nhanvatdachet():
                    self._thoidiemnhanvatchetgannhat = time.time()
                else:
                    if time.time() - self._thoidiemnhanvatchetgannhat > 0.5:
                        idbandohientai = self.moitruong.get_idbandohientai()
                        if idbandohientai in BANDOTUDONGLENSAUKHICHETs:
                            self._idbandovuachet = idbandohientai
                    if time.time() - self._thoidiemnhanvatchetgannhat > 2.5 and self.moitruong.get_tenmonphai() != "vanmongcoc":
                        self._thoigiantamngungauto = time.time()
                        self.moitruong.action_phucsinh()
                break

    def action_tudongdoimaupk(self):
        if self._is_tudongdoimaupk and self.moitruong.get_idbandohientai() not in BANDOCUTHUDAOs:
            if time.time() - self._thoidiemdoimaupkgannhat > 5.:
                self._thoidiemdoimaupkgannhat = time.time()
                self.action_batpk()

    def action_batpk(self):
        self.moitruong.action_doimaupk(MAUPK_BANG)

    def action_tatpk(self):
        self.moitruong.action_doimaupk(MAUPK_HOABINH)

    def action_tudongsuado(self):
        if self._is_tudongsuado:
            if time.time() - self._thoidiemkiemtranpcsuadogannhat < 2.:
                return
            self._thoidiemkiemtranpcsuadogannhat = time.time()

            diachicosothongtinnhanvatchutiemsuachua = self.moitruong.action_timkiemnhanvat(CHUTIEMSUACHUA)

            if diachicosothongtinnhanvatchutiemsuachua and self.moitruong.get_khoangcach(diachicosothongtinnhanvatchutiemsuachua) <= 3.0:
                self.moitruong.action_suado(diachicosothongtinnhanvatchutiemsuachua)

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
                if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs:
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
                            if self.moitruong.get_idbandohientai() not in BANDOCUTHUDAOs or time.time() - self._thoidiemgapnguoichoigannhat > 2.5 or self.moitruong.get_khoangcach(diachicosothongtinnhanvatmuctieudangchon) <= 4.5:
                                self.moitruong.action_ralenhbaothumaosontancong(iddoituongbaothumaoson, iddoituongnhanvatmuctieudangchon)

                break

    def action_tudongtrieuhoibaothudautien(self):
        if self._is_tudongtrieuhoibaothudautien:
            while True:
                if self.moitruong.get_idbandohientai() not in BANDOKHONGTANCONGs or time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() < 1.:
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
        ten_npc = "Chá»§ Tiá»‡m Táº¡p HÃ³a"

        diachi_npc = self.moitruong.action_timkiemnhanvat(ten_npc)
        if not diachi_npc:
            # phatam("Không tìm thấy Chủ Tiệm Tạp Hóa")
            return

        khoangcach = self.moitruong.get_khoangcach(diachi_npc)
        if khoangcach > 6.0:
            # phatam(f"Đứng quá xa Chủ Tiệm Tạp Hóa ({round(khoangcach, 1)}m)")
            return

        id_npc = self.moitruong.get_iddoituong(diachi_npc)
        if not id_npc or id_npc <= 0:
            return

        npc_hex = hex(id_npc).replace("0x", "")
        # phatam("Bắt đầu bán rác")

        count_sold = 0
        for i in range(24, SOLUONGVATPHAMHANHTRANGTOIDA):
            id_item = self.moitruong.get_iddoituongvatphamhanhtrang(i)

            if id_item and id_item > 0:
                item_hex = hex(id_item).replace("0x", "")
                caulenh = f"sell {npc_hex}# {item_hex}# 1"
                self.moitruong.action_thucthicaulenh(caulenh, delay = 0.)
                count_sold += 1
                time.sleep(1.5)

        # if count_sold > 0:
        #     phatam(f"Đã bán {count_sold} món đồ")
        # else:
        #     phatam("Không có đồ để bán từ ô 24")

    def action_xulygomquai(self):
        yeucaugomquaimoi = None

        if not self._is_tudonggomquai:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            self._danhsachidquaidagom.clear()
            self._idquaidautien = 0
            return

        if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs:
            self._is_danggomquai = False
            self._yeucaugomquai = None
            self._idquaidangkeo = 0
            return

        is_canghilog = False
        if time.time() - self._thoidiemloggomquai > 1.5:
            is_canghilog = True
            self._thoidiemloggomquai = time.time()
        is_canghilog = False
        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_dangvankhi() or self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs:
            self._yeucaugomquai = None
            return

        if len(self._danhsachidquaidagom) == 0:
            self._idquaidautien = 0

        diachimuctieudangchon = self.moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        if diachimuctieudangchon:
            if self.moitruong.get_is_nguoichoi(diachimuctieudangchon):
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

            iddoituongquai = self.moitruong.get_iddoituong(diachidoituongxemxet)
            if iddoituongquai in self._idmuctieubiloi_map:
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

    def action_xulyveban_maoson(self):
        if not self._is_tudongveban_maoson:
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
                # phatam("Túi đầy, chuẩn bị biến về")
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
                    self.moitruong.action_thucthicaulenh("pf 4182.1")
                    self._thoidiemchuyentrangthai = time.time()

        elif self._trangthaiveban == 2:
            if time.time() - self._thoidiemchuyentrangthai > 3.0:
                diachi_npc = self.moitruong.action_timkiemnhanvat(chutiemtaphoa)

                if diachi_npc:
                    khoangcach = self.moitruong.get_khoangcach(diachi_npc)
                    if khoangcach <= 6.0:
                        print("[AUTO-SELL] Đã gặp NPC, bắt đầu bán")
                        self._trangthaiveban = 3
                    else:
                        x_npc = self.moitruong.get_toadox(diachi_npc, is_vitrihientai = True)
                        y_npc = self.moitruong.get_toadoy(diachi_npc, is_vitrihientai = True)
                        self.moitruong.action_dichuyen(x_npc, y_npc)
                        time.sleep(0.5)
                else:
                    print("[AUTO-SELL] Đang tìm NPC Tạp Hóa...")
                    if time.time() - self._thoidiemchuyentrangthai > 30.0:
                        print("[AUTO-SELL] Lỗi: Không tìm thấy NPC quá lâu -> Reset.")
                        self._trangthaiveban = 0

        elif self._trangthaiveban == 3:
            self.action_tudongbanrac()

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
                    self.moitruong.action_thucthicaulenh("pf 4182.2")
                    self._thoidiemchuyentrangthai = time.time()

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
            self._trangthaidichientruong = 0
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        diachinpc = self.moitruong.action_timkiemnhanvat(TRUONGQUALAO)
        if not diachinpc:
            self._trangthaidichientruong = 0
            return

        khoangcach = self.moitruong.get_khoangcach(diachinpc)
        if khoangcach > 12.0:
            return

        idnpc = self.moitruong.get_iddoituong(diachinpc)
        if not idnpc:
            return

        hientai = time.time()

        if self._trangthaidichientruong == 0:
            caulenh = "tallk {}# welcome.1001".format(hex(idnpc).replace("0x", ""))
            is_ok = self.moitruong.action_thucthicaulenh(caulenh, delay = 1.0)

            if is_ok:
                print(f"[CHIEN-TRUONG] Đã gửi lệnh đăng ký. Chờ 2s để vào...")
                self._trangthaidichientruong = 1
                self._thoidiemdichientruong = hientai

        elif self._trangthaidichientruong == 1:
            if hientai - self._thoidiemdichientruong > 2.0:
                caulenh = "tallk {}# welcome.1003".format(hex(idnpc).replace("0x", ""))
                is_ok = self.moitruong.action_thucthicaulenh(caulenh, delay = 1.0)

                if is_ok:
                    print(f"[CHIEN-TRUONG] Đã gửi lệnh tiến vào. Reset quy trình.")
                    self._trangthaidichientruong = 0
                    self._thoidiemdichientruong = hientai

    def action_tudonglamnhiemvusugia(self):
        if not self._is_tudonglamnhiemvusugia:
            self._trangthailamnhiemvusugia = 0
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        diachinpc = self.moitruong.action_timkiemnhanvat(SUGIANHIEMVU)

        idbandohientai = self.moitruong.get_idbandohientai()
        hientai = time.time()

        if self._trangthailamnhiemvusugia == 0:
            if diachinpc and self.moitruong.get_khoangcach(diachinpc) <= 12.0:
                idnpc = self.moitruong.get_iddoituong(diachinpc)
                if idnpc:
                    caulenh = "talk {}# welcome.1".format(hex(idnpc).replace("0x", ""))
                    is_ok = self.moitruong.action_thucthicaulenh(caulenh, delay = 1.0)
                    if is_ok:
                        print(f"[SU-GIA] Đã gửi lệnh nhận nhiệm vụ {caulenh}")
                        self._trangthailamnhiemvusugia = 1
                        self._thoidiemlamnhiemvusugia = hientai
                        self._idbandogoc_sugia = idbandohientai

        elif self._trangthailamnhiemvusugia == 1:
            if hientai - self._thoidiemlamnhiemvusugia > 6.0:
                if diachinpc and self.moitruong.get_khoangcach(diachinpc) <= 12.0:
                    self._trangthailamnhiemvusugia = 3
                else:
                    self._trangthailamnhiemvusugia = 0
                return

            if idbandohientai != self._idbandogoc_sugia:
                print(f"[SU-GIA] Phát hiện đã chuyển map ({self._idbandogoc_sugia} -> {idbandohientai}). Bắt đầu đánh quái.")
                self._trangthailamnhiemvusugia = 2

        elif self._trangthailamnhiemvusugia == 2:
            if idbandohientai == self._idbandogoc_sugia:
                print(f"[SU-GIA] Phát hiện đã quay về map gốc. Chuẩn bị trả nhiệm vụ.")
                self._trangthailamnhiemvusugia = 3
                self._thoidiemlamnhiemvusugia = hientai

        elif self._trangthailamnhiemvusugia == 3:
            if not diachinpc:
                return

            if self.moitruong.get_khoangcach(diachinpc) > 12.0:
                return

            idnpc = self.moitruong.get_iddoituong(diachinpc)
            if idnpc:
                if hientai - self._thoidiemlamnhiemvusugia > 1.0:
                    caulenh = "talk {}# bonus.11".format(hex(idnpc).replace("0x", ""))
                    is_ok = self.moitruong.action_thucthicaulenh(caulenh, delay = 1.0)
                    if is_ok:
                        print(f"[SU-GIA] Đã gửi lệnh trả nhiệm vụ (bonus.11). Hoàn tất vòng lặp.")
                        self._trangthailamnhiemvusugia = 0