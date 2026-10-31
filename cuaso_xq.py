import ast
import json
import threading
import time
import traceback

from loop_xq import (
    LoopLamMoiTrangThaiMoiTruong,
    LoopTimKiemMucTieu,
    LoopChinh,
    LoopPhu,
    LoopDieuPhoiDiChuyen,
    LoopXuLyLenh,
    LoopBoKhungSauTanCong,
    LoopGiuOTrongHanhTrang
)
from dieuphoi_xq import DieuPhoiLuot, GiuKyNangMucTieu, KENH_LENH, KENH_DICHUYEN
from lan_xq import DuLieuNhieuMay
from moitruong_xq import MoiTruong
from tactu_xq import TacTu
from thongke_xq import ThongKe, CHUKYLAYMAU
from giamsat_xq import GiamSat, CHUKYGIAMSAT
from thongbao_xq import TheoDoiSuCo, LYDOTAMNGUNGTUXA


def khoidong_looptonghop(moitruong, tactu, stop, giamsat):
    l_lammoi = LoopLamMoiTrangThaiMoiTruong(moitruong, tactu, stop)
    l_timkiem = LoopTimKiemMucTieu(moitruong, tactu, stop)
    l_dieuphoi = LoopDieuPhoiDiChuyen(moitruong, tactu, stop)
    l_chinh = LoopChinh(moitruong, tactu, stop)

    while not stop.is_set() and moitruong.get_is_cuasogametontai():
        try:
            l_lammoi.step()
            l_timkiem.step()
            l_dieuphoi.step()
            l_chinh.step()
        except Exception as e:
            print(f"Lỗi luồng tổng hợp: {e}")
            traceback.print_exc()
            time.sleep(1)
        giamsat.danhdau("tổng hợp")
        time.sleep(0.1)


def khoidong_loopphu(moitruong, tactu, stop, giamsat):
    LoopPhu(moitruong, tactu, stop, giamsat).loop()

def khoidong_loopxulylenh(moitruong, tactu, stop):
    LoopXuLyLenh(moitruong, tactu, stop).loop()

def khoidong_loopbokhung(moitruong, tactu, stop):
    LoopBoKhungSauTanCong(moitruong, tactu, stop).loop()

def khoidong_loopgiuotrong(moitruong, tactu, stop):
    LoopGiuOTrongHanhTrang(moitruong, tactu, stop).loop()

def khoidong_loopthongke(thongke, moitruong, stop):
    while not stop.is_set() and moitruong.get_is_cuasogametontai():
        try:
            thongke.step()
        except Exception as e:
            print(f"[Loop THỐNG KÊ] Lỗi: {e}")
        time.sleep(CHUKYLAYMAU)

def khoidong_looptodoimotlan(tactu, moitruong, stop):
    # Tổ đội 1 lần (Ctrl+Alt+T) chạy riêng: để trong luồng phụ (~1s/lượt) thì mỗi người vào nhóm chậm 3-4s. Đang gom / được gom thì
    # 0.25s/lượt, rảnh thì 0.5s/lượt
    while not stop.is_set() and moitruong.get_is_cuasogametontai():
        is_dangchay = False
        try:
            if moitruong.get_is_nhanvattontai() and not moitruong.get_is_dangmatketnoi():
                is_dangchay = tactu.action_todoimotlan()
        except Exception as e:
            print(f"[Loop TỔ ĐỘI 1 LẦN] Lỗi: {e}")
            time.sleep(1)
        time.sleep(0.25 if is_dangchay else 0.5)

def khoidong_loopgiamsat(giamsat, theodoisuco, moitruong, stop):
    while not stop.is_set() and moitruong.get_is_cuasogametontai():
        try:
            giamsat.step()
        except Exception as e:
            print(f"[Loop GIÁM SÁT] Lỗi: {e}")
        try:
            theodoisuco.step()
        except Exception as e:
            print(f"[Loop GIÁM SÁT] Lỗi theo dõi sự cố: {e}")
        time.sleep(CHUKYGIAMSAT)

class CuaSo:
    def __init__(self, idcuaso, shared_data, command_dict, dieuphoi_khoa = None, dieuphoi_trangthai = None, dieuphoi_dangchos = None, dieuphoi_giukynangs = None,
                 shared_data_lan = None):
        self.idcuaso = idcuaso
        self.shared_data = shared_data
        self.command_dict = command_dict

        self.moitruong = MoiTruong(idcuaso)
        if dieuphoi_khoa is not None:
            self.moitruong.dieuphoi = DieuPhoiLuot(idcuaso, dieuphoi_khoa, dieuphoi_trangthai, dieuphoi_dangchos, KENH_LENH)
            self.moitruong.dieuphoidichuyen = DieuPhoiLuot(idcuaso, dieuphoi_khoa, dieuphoi_trangthai, dieuphoi_dangchos, KENH_DICHUYEN)
            if dieuphoi_giukynangs is not None:
                self.moitruong.giukynang = GiuKyNangMucTieu(idcuaso, dieuphoi_khoa, dieuphoi_giukynangs)
        self.moitruong.action_thietlaphooknoidungtrochuyen()
        self.tactu = TacTu(self.moitruong)
        # Bot đọc gộp cả cửa sổ máy khác trong LAN (lan_xq), ghi vẫn vào máy này
        self.tactu.shared_data = DuLieuNhieuMay(shared_data, shared_data_lan) if shared_data_lan is not None else shared_data
        self.tactu.idcuaso = idcuaso
        self.main_stop = threading.Event()
        self.thongke = ThongKe(self.moitruong, self.tactu)
        self.giamsat = GiamSat(self.moitruong, self.tactu)
        # Tin sự cố gửi về Telegram (thongbao_xq): chết, bị người chơi đánh
        self.theodoisuco = TheoDoiSuCo(self.moitruong, self.tactu)

        self.tennhanvat = None
        self.idnguoichoi = 0
        self.thoidiemluuthietlap = time.time()

        self.luongs = (
            threading.Thread(target = khoidong_looptonghop, args = [self.moitruong, self.tactu, self.main_stop, self.giamsat], daemon = True),
            threading.Thread(target = khoidong_loopphu, args = [self.moitruong, self.tactu, self.main_stop, self.giamsat], daemon = True),
            threading.Thread(target = khoidong_loopxulylenh, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopbokhung, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopgiuotrong, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopthongke, args = [self.thongke, self.moitruong, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopgiamsat, args = [self.giamsat, self.theodoisuco, self.moitruong, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_looptodoimotlan, args = [self.tactu, self.moitruong, self.main_stop], daemon = True),
        )

        for luong in self.luongs:
            luong.start()

        threading.Thread(target = self.loop_xulyphimtat, daemon = True).start()
        threading.Thread(target = self.loop_hienthigiaodien, daemon = True).start()

    def __del__(self):
        self.tatauto()

    def _chotoanbocacluongdunghan(self):
        for luong in self.luongs:
            if luong.is_alive():
                luong.join(timeout = 0.2)

    def tatauto(self, *args, **kwargs):
        if self.idnguoichoi:
            self.tactu.luuthietlap(self.idnguoichoi)
            self.tactu.luuvitriquai(True)
            self.tactu._sovitri.luu(is_ngay = True)
        self.thongke.luu(is_tatca = True)

        self.main_stop.set()
        self._chotoanbocacluongdunghan()

        if self.idcuaso in self.shared_data:
            del self.shared_data[self.idcuaso]

        if self.idcuaso in self.command_dict:
            del self.command_dict[self.idcuaso]

    def _laydiemdanhdangden(self):
        tactu = self.tactu
        diem = tactu._diemdanhxungquanhhientai
        if not tactu._is_tudongdichuyendiemdanhxungquanh or not diem or len(diem) < 3:
            return None
        return [round(diem[0]), round(diem[1]), diem[2], tactu._iddiemdanhxungquanhhientai, len(tactu._diemdanhxungquanhs)]

    def loop_hienthigiaodien(self):
        while not self.main_stop.is_set():
            try:
                if not self.moitruong.get_is_cuasogametontai():
                    break

                tennhanvat = self.moitruong.get_tendoituong()
                idnguoichoi = self.moitruong.get_idnguoichoi()

                if idnguoichoi and idnguoichoi != self.idnguoichoi:
                    if self.idnguoichoi:
                        self.tactu.luuthietlap(self.idnguoichoi)

                    self.tactu.taithietlap(idnguoichoi, tennhanvat)
                    print(f"-> Đã tải cấu hình cho: {tennhanvat} (ID: {idnguoichoi})")

                    self.idnguoichoi = idnguoichoi
                    self.tennhanvat = tennhanvat
                    self.thoidiemluuthietlap = time.time()
                elif idnguoichoi and (time.time() - self.thoidiemluuthietlap > 1.0):
                    self.tactu.luuthietlap(idnguoichoi)
                    self.thoidiemluuthietlap = time.time()

                if not idnguoichoi:
                    time.sleep(1.0)
                    continue

                phantramsinhluc = 0
                phantramnoiluc = 0
                try:
                    phantramsinhluc = int(self.moitruong.get_phantramsinhlucconlai())
                    phantramnoiluc = int(self.moitruong.get_phantramnoilucconlai())
                except:
                    pass

                idtuthenhanvat = self.moitruong.get_idtuthenhanvat()
                tentrangthai = "Đứng im"
                if idtuthenhanvat == 1:
                    tentrangthai = "Di chuyển"
                elif idtuthenhanvat == 2:
                    tentrangthai = "Tấn công"
                elif self.moitruong.get_is_nhanvatdachet():
                    tentrangthai = "Đã chết"

                x, y = self.moitruong.get_toado()
                is_dangtrongnhom = self.moitruong.get_is_dangnamtrongnhom()

                info = {
                    "tennhanvat": tennhanvat,
                    # Thành viên cùng máy dùng để tìm cửa sổ trưởng nhóm (bản đồ/tọa độ) mà phù theo
                    "idnguoichoi": self.moitruong.get_idnguoichoi(),
                    "thoidiemcapnhat": time.time(),
                    "tenbando": self.moitruong.get_idbandohientai(),
                    # Vân Mộng Cốc cùng máy dùng để biết buff Ngân Châm hay Kim Châm cho nhân vật này
                    "tenmonphai": self.moitruong.get_tenmonphai(),
                    # Tổ đội tự động dùng để biết các nhóm khác đang cùng bản đồ
                    "idtruongnhom": self.moitruong.get_idnguoichoitruongnhom() if is_dangtrongnhom else 0,
                    "thanhviennhoms": self.moitruong.get_danhsachidnguoichoithanhviennhoms() if is_dangtrongnhom else [],
                    "x": x,
                    "y": y,
                    "status": tentrangthai,
                    "phantramsinhluc": phantramsinhluc,
                    "phantramnoiluc": phantramnoiluc,
                    "is_window_active": self.moitruong.get_is_cuasogamekichhoat(),

                    "_is_tudongtheosau": self.tactu._is_tudongtheosau,
                    "_idmuctieutheosau": self.tactu._idmuctieutheosau,
                    "_tenmuctieutheosau": self.tactu._tenmuctieutheosau,
                    "_is_tudongtodoi": self.tactu._is_tudongtodoi,
                    # Tổ đội 1 lần: trưởng nhóm đang gom ai (cửa sổ thành viên đọc), trạng thái cho giao diện
                    "_todoimotlan": self.tactu.get_todoimotlanshare(),
                    "_is_dangtodoimotlan": bool(self.tactu._todoimotlan),
                    "_trangthaitodoimotlan": self.tactu._trangthaitodoimotlan,
                    "_is_tudongsudungkynang": self.tactu._is_tudongsudungkynang,
                    "_is_uutienmuctieupk": self.tactu._is_uutienmuctieupk,
                    "_is_tudongtimkiemmuctieu": self.tactu._is_tudongtimkiemmuctieu,
                    "_is_tudonggomquai": self.tactu._is_tudonggomquai,
                    "_is_tudongvebanrac": self.tactu._is_tudongvebanrac,
                    "_is_tudongkhaikhoang": self.tactu._is_tudongkhaikhoang,
                    "_is_tudongdichientruong": self.tactu._is_tudongdichientruong,
                    "_is_tudongdaotangbaodo": self.tactu._is_tudongdaotangbaodo,

                    "_is_chidanhnguoichoi": self.tactu._is_chidanhnguoichoi,
                    "_is_uutienbaothukynangtrieuhoi": self.tactu._is_uutienbaothukynangtrieuhoi,
                    "_is_chedobufftoanbang": self.tactu._is_chedobufftoanbang,
                    "_is_chantangcapdo": self.tactu._is_chantangcapdo,

                    # Danh sách (không nối chuỗi) để giao diện sửa được từng tên
                    "_tenmuctieutancongs": sorted(self.tactu._tenmuctieutancongs),
                    "_tenmuctieukhongtancongs": sorted(self.tactu._tenmuctieukhongtancongs),
                    # Mục tiêu bot tự bỏ qua theo id (bị chặn, đánh không trúng...), giao diện xoá được khi bỏ nhầm
                    "_muctieuboquas": self.tactu.get_danhsachmuctieuboqua(),
                    "_khoangcachtoidatheosau": self.tactu._khoangcachtoidatheosau,
                    "_bankinhdiemdanh": self.tactu._bankinhdiemdanh,
                    "_phamchatnhats": sorted(self.tactu._phamchatnhats),
                    "_khoangcachsudungkynangtamxa": self.tactu._khoangcachsudungkynangtamxa,
                    "_phantramnoiluckhaithientichdia": self.tactu._phantramnoiluckhaithientichdia,

                    "_is_tudongdichuyendiemdanhxungquanh": self.tactu._is_tudongdichuyendiemdanhxungquanh,
                    "_diemdanhxungquanhs": self.tactu._diemdanhxungquanhs,
                    "_lotrinhmaudangdung": self.tactu._lotrinhmaudangdung,
                    "_thoigiantamngungconlai": max(0., self.tactu._thoidiemhettamngung - time.time()),
                    "_lydotamngung": self.tactu._lydotamngung,
                    "_thoidiemphathienanthan": self.tactu._thoidiemphathienanthan,
                    "_tenanthanphathien": self.tactu._tenanthanphathien,
                    "_thoigiantamngungphathien": self.tactu._thoigiantamngungphathien,
                    "_is_tudongtrieuhoibaothugiangho": self.tactu._is_tudongtrieuhoibaothugiangho,

                    "_is_tudongsudungkynangbaothu": self.tactu._is_tudongsudungkynangbaothu,
                    "_is_tranhvungcam": self.tactu._is_tranhvungcam,
                    "_is_dilotrinhkhacbando": self.tactu._is_dilotrinhkhacbando,
                    "_is_giukhoangcachketancong": self.tactu._is_giukhoangcachketancong,
                    "_khoangcachgiuketancong": self.tactu._khoangcachgiuketancong,
                    "_is_giukhoangcachchimuctieupk": self.tactu._is_giukhoangcachchimuctieupk,
                    "_is_taphoa": self.tactu._is_taphoa,
                    "_is_timmuctieuchung": self.tactu._is_timmuctieuchung,
                    "_is_tutimduongtheosau": self.tactu._is_tutimduongtheosau,
                    "_is_dangsapxephanhtrang": self.tactu._is_dangsapxephanhtrang,
                    "_is_doidokhitrieuhoi": self.tactu._is_doidokhitrieuhoi,
                    "_tenbodotrieuhoi": [mon["ten"] for mon in self.tactu._bodotrieuhoi],
                    "_baothutrieuhoimaoson": self.tactu._baothutrieuhoimaoson,
                    "_is_nguocchieulotrinh": self.tactu._is_nguocchieulotrinh,
                    "_solanthayquaibando": self.tactu.get_solanthayquaibando(),
                    "_buocdichuyen": self.tactu.get_buocdichuyen(),
                    "_idbandocandi": self.tactu._idbandocandi,
                    # Điểm đánh lộ trình đang đi tới [x, y, id bản đồ, số thứ tự, tổng số điểm] (cột "Đang đi tới" trên Telegram)
                    "_diemdanhdangden": self._laydiemdanhdangden(),
                    "_hangchogiaodo": self.tactu.get_hangchogiaodo(),
                    "_trangthaicatkho": self.tactu.get_trangthaicatkho(),
                    "_is_dangcatkho": bool(self.tactu._catkho),
                    "_lichsucatkho": self.tactu._lichsucatkho,
                    "_trangthaisumon": self.tactu.get_trangthaisumon(),
                    "_is_dangsumon": self.tactu.get_is_dangsumon(),
                    "_sumon_npcgiao": self.tactu._sumon_npcgiao,
                    "_npcgiaosumon": self.tactu._laynpcgiaosumon(),
                    "_trangthailanglyson": self.tactu.get_trangthailanglyson(),
                    "_is_danglanglyson": self.tactu.get_is_danglanglyson(),
                    "_phobanlanglyson": self.tactu.get_phobanlanglyson(),
                    # Lăng Ly Sơn: trưởng nhóm báo mã thưởng vòng vừa xong, thành viên báo mã đã tự lĩnh (tactu_langlyson_xq)
                    "_khoathuonglanglyson": self.tactu.get_khoathuonglanglyson(),
                    "_khoathuonglanglysondalanh": self.tactu._khoathuonglanglysondalanh,
                    "_langlysonchothanhvien": self.tactu.get_is_langlysonchothanhvien(),
                    "_langlysontattodoi": self.tactu.get_dsidtattodoilanglyson(),
                    "_langlysongiunhom": self.tactu.get_dsidgiunhomlanglyson(),
                    # Phong Yêu Kính: ID boss mình đã giết vòng này, người cùng nhóm cộng vào (boss chết xa họ vẫn được tính)
                    "_bossdagietphongyeu": self.tactu.get_bossdagietphongyeu(),
                    # Sư Gia (tactu_sugia_xq): trạng thái cho giao diện; nhiệm vụ của mình ("" / "dang" / "xong") cho trưởng nhóm cùng máy chờ
                    "_trangthaisugia": self.tactu.get_trangthaisugia(),
                    "_is_dangsugia": self.tactu.get_is_dangsugia(),
                    "_sugianhiemvu": self.tactu.get_nhiemvusugiashare(),
                    "_sugiachothanhvien": self.tactu.get_is_sugiachothanhvien(),
                    # Tập Kích Môn Phái (tactu_tapkich_xq): trạng thái cho giao diện; đang đi thì thành viên theo sau tự chọn menu vào / Lễ Bao
                    "_trangthaitapkich": self.tactu.get_trangthaitapkich(),
                    "_is_dangtapkich": self.tactu.get_is_dangtapkich(),
                    "_tapkich_phai": self.tactu._tapkich_phai or self.moitruong.get_tenmonphai() or "",
                    # Đoạt Bảo Mã Tặc (tactu_matac_xq): trạng thái, danh sách bản đồ cho giao diện
                    "_trangthaimatac": self.tactu.get_trangthaimatac(),
                    "_is_dangmatac": self.tactu.get_is_dangmatac(),
                    "_matac_bandos": self.tactu._matac_bandos,
                    "_is_tubatmatac": self.tactu._is_tubatmatac,
                    # Nhiệm vụ Danh Vọng (tactu_danhvong_xq): trạng thái cho giao diện
                    "_trangthaidanhvong": self.tactu.get_trangthaidanhvong(),
                    "_is_dangdanhvong": self.tactu.get_is_dangdanhvong(),
                    "_thongkephien": self.thongke.get_tomtatphien(),
                    # Ngân lượng mang theo hiện tại (báo cáo Telegram)
                    "nganluong": self.moitruong.get_nganluong(),
                    # Biến động ngân lượng / vật phẩm gần đây để cửa sổ khác nhận ra chuyển cho nhau (thongke_xq)
                    "_biendongtainguyen": self.thongke.get_biendongganday(),
                }
                # Tầm nhìn chia sẻ cho nhân vật khác cùng máy (đối tượng thù địch mình thấy); lỗi thì vẫn cập nhật phần còn lại
                try:
                    info["tamnhin"] = self.tactu.get_tamnhinchiase()
                except Exception as err:
                    print(f"Lỗi tạo tầm nhìn chia sẻ: {err}")
                # Mục tiêu đang chọn trong game (bot chọn hay người chơi tự click đều ghi vào cùng ô) cho nhân vật theo sau tập hỏa
                try:
                    diachimuctieugame = self.moitruong._get_diachicosothongtinnhanvatmuctieudangchon()
                    info["iddoituongmuctieu"] = self.moitruong.get_iddoituong(diachimuctieugame) if diachimuctieugame else 0
                except Exception:
                    info["iddoituongmuctieu"] = 0
                self.shared_data[self.idcuaso] = info

            except Exception as err:
                print(f"Lỗi ở loop_hienthigiaodien: {err}")
                traceback.print_exc()
            time.sleep(0.25)

    def loop_xulyphimtat(self):
        while not self.main_stop.is_set():
            cmd = self.command_dict.get(self.idcuaso)

            if cmd:
                if cmd == "action_lammoitrangthai":
                    self.tactu.action_lammoitrangthai()
                elif cmd == "battat_tudongdichuyendiemdanhxungquanh":
                    self.tactu.battat_is_tudongdichuyendiemdanhxungquanh()
                elif isinstance(cmd, str) and cmd.startswith(("nap_lotrinhmau:", "bosung_lotrinhmau:")):
                    # nap_lotrinhmau / bosung_lotrinhmau:<id bản đồ>|<tên mẫu>|<1 nếu ngược chiều> (bổ sung: nối vào lộ trình đang có)
                    phan = cmd.split(":", 1)[1].split("|")
                    if len(phan) == 3:
                        self.tactu.nap_lotrinhmau(int(phan[0]), phan[1], phan[2] == "1", is_bosung = cmd.startswith("bosung_lotrinhmau:"))
                elif isinstance(cmd, str) and cmd.startswith("ditoibando:"):
                    # ditoibando:<id bản đồ> (0 = dừng)
                    try:
                        self.tactu.thietlap_ditoibando(int(cmd.split(":", 1)[1]))
                    except ValueError:
                        pass
                elif cmd == "dexuat_lotrinhmau":
                    self.tactu.dexuat_lotrinhmau()
                elif cmd == "tuchon_lotrinhmau":
                    self.tactu.tuchon_lotrinhmau()
                elif isinstance(cmd, str) and cmd.startswith("set_nguocchieulotrinh:"):
                    self.tactu.thietlap_nguocchieulotrinh(cmd.split(":", 1)[1] == "1")
                elif cmd == "tieptuchoatdong":
                    self.tactu.tieptuchoatdong()
                elif isinstance(cmd, str) and cmd.startswith("giaodo:"):
                    # Yêu cầu giao tiền / đồ (giaodo_xq) dạng JSON từ giao diện / Telegram: 1 yêu cầu hoặc danh sách (gửi dồn trước khi bot nhận)
                    yeucaus = json.loads(cmd.split(":", 1)[1])
                    for yeucau in (yeucaus if isinstance(yeucaus, list) else [yeucaus]):
                        self.tactu.them_giaodo(yeucau)
                elif cmd == "vegiao":
                    # Nút "Về giao ngay" / Telegram /vegiao: các yêu cầu giao đang chờ về giao ngay
                    self.tactu.kichhoat_giaodo()
                elif isinstance(cmd, str) and cmd.startswith("huygiaodo:"):
                    self.tactu.huy_giaodo(cmd.split(":", 1)[1])
                elif cmd == "catkho":
                    # Cất kho ngay (tactu_catkho_xq) từ giao diện / Telegram
                    self.tactu.yeucau_catkho()
                elif cmd == "huycatkho":
                    self.tactu.huy_catkho()
                elif cmd == "sumon":
                    # Nhiệm vụ sư môn (tactu_sumon_xq) bật / tắt từ giao diện
                    self.tactu.batdau_sumon()
                elif cmd == "huysumon":
                    self.tactu.huy_sumon()
                elif cmd == "langlyson":
                    # Tự động đi Lăng Ly Sơn (tactu_langlyson_xq) bật / tắt từ giao diện
                    self.tactu.batdau_langlyson()
                elif cmd == "thanhkieu":
                    # Tự động đi Thành Kiều Quân Doanh (cùng module tactu_langlyson_xq)
                    self.tactu.batdau_langlyson("thanhkieu")
                elif cmd == "phongyeukinh":
                    # Tự động đi Phong Yêu Kính (cùng module tactu_langlyson_xq)
                    self.tactu.batdau_langlyson("phongyeukinh")
                elif cmd == "huylanglyson":
                    self.tactu.huy_langlyson()
                elif cmd == "sugia":
                    # Nhiệm vụ Sư Gia (tactu_sugia_xq) bật / tắt từ giao diện
                    self.tactu.batdau_sugia()
                elif cmd == "huysugia":
                    self.tactu.huy_sugia()
                elif isinstance(cmd, str) and cmd.startswith("tapkich:"):
                    # Tập Kích Môn Phái (tactu_tapkich_xq) bật từ giao diện, kèm môn phái chọn
                    self.tactu.batdau_tapkich(cmd.split(":", 1)[1])
                elif cmd == "huytapkich":
                    self.tactu.huy_tapkich()
                elif isinstance(cmd, str) and cmd.startswith("set_tapkich_phai:"):
                    self.tactu.thietlap_phaitapkich(cmd.split(":", 1)[1])
                elif cmd == "matac":
                    # Đoạt Bảo Mã Tặc (tactu_matac_xq) bật / tắt từ giao diện
                    self.tactu.batdau_matac()
                elif cmd == "huymatac":
                    self.tactu.huy_matac()
                elif isinstance(cmd, str) and cmd.startswith("set_matac_bando:"):
                    self.tactu.thietlap_bandomatac(cmd.split(":", 1)[1])
                elif isinstance(cmd, str) and cmd.startswith("set_matac_tubat:"):
                    self.tactu.thietlap_tubatmatac(cmd.split(":", 1)[1] == "1")
                elif cmd == "danhvong":
                    # Nhiệm vụ Danh Vọng (tactu_danhvong_xq) bật / tắt từ giao diện
                    self.tactu.batdau_danhvong()
                elif cmd == "huydanhvong":
                    self.tactu.huy_danhvong()
                elif isinstance(cmd, str) and cmd.startswith("set_sumon_npcgiao:"):
                    self.tactu.thietlap_npcgiaosumon(cmd.split(":", 1)[1])
                elif isinstance(cmd, str) and cmd.startswith("tamngungtuxa:"):
                    # Lệnh /tamdung từ Telegram: tạm ngưng như khi phát hiện ẩn thân (cả tự động đăng nhập cũng chờ), số giây sau dấu ":"
                    self.tactu._batdautamngung(LYDOTAMNGUNGTUXA, float(cmd.split(":", 1)[1]))
                elif isinstance(cmd, str) and cmd.startswith("luu_lotrinhmau:"):
                    self.tactu.luu_lotrinhmau(cmd.split(":", 1)[1])
                elif isinstance(cmd, str) and cmd.startswith("set_khoangcachtheosau:"):
                    try:
                        khoangcach = float(cmd.split(":")[1])
                        self.tactu.thietlap_khoangcachtheosau(khoangcach)
                    except Exception:
                        pass
                elif isinstance(cmd, str) and cmd.startswith("set_muctieutheosau:"):
                    # set_muctieutheosau:<ID người chơi, 0 = trưởng nhóm>|<tên>
                    try:
                        idmuctieu, _, tenmuctieu = cmd.split(":", 1)[1].partition("|")
                        self.tactu.thietlap_muctieutheosau(int(idmuctieu), tenmuctieu)
                    except Exception as e:
                        print(f"Lỗi khi chọn người theo sau: {e}")
                elif isinstance(cmd, str) and cmd.startswith("set_khoangcachsudungkynangtamxa:"):
                    try:
                        self.tactu.thietlap_khoangcachsudungkynangtamxa(float(cmd.split(":")[1]))
                    except Exception:
                        pass
                elif isinstance(cmd, str) and cmd.startswith("set_phantramnoiluckhaithientichdia:"):
                    try:
                        self.tactu.thietlap_phantramnoiluckhaithientichdia(float(cmd.split(":")[1]))
                    except Exception:
                        pass
                elif isinstance(cmd, str) and cmd.startswith("set_phamchatnhat:"):
                    try:
                        self.tactu.thietlap_phamchatnhat([x for x in cmd.split(":", 1)[1].split(",") if x])
                    except Exception:
                        pass
                elif isinstance(cmd, str) and cmd.startswith("set_bankinhdiemdanh:"):
                    try:
                        self.tactu.thietlap_bankinhdiemdanh(float(cmd.split(":")[1]))
                    except Exception:
                        pass
                elif isinstance(cmd, str) and cmd.startswith("them_diemdanh_nhaptay:"):
                    try:
                        toa_do_str = cmd.split(":", 1)[1].strip()
                        danh_sach_diem = ast.literal_eval(toa_do_str)
                        if isinstance(danh_sach_diem, list):
                            for diem in danh_sach_diem:
                                if isinstance(diem, (list, tuple)) and len(diem) >= 3:
                                    x = int(diem[0])
                                    y = int(diem[1])
                                    map_id = int(diem[2])
                                    self.tactu.them_diemdanhxungquanh((x, y, map_id))
                        elif isinstance(danh_sach_diem, tuple) and len(danh_sach_diem) >= 3:
                            x = int(danh_sach_diem[0])
                            y = int(danh_sach_diem[1])
                            map_id = int(danh_sach_diem[2])
                            self.tactu.them_diemdanhxungquanh((x, y, map_id))

                    except Exception as e:
                        print(f"Lỗi khi phân tích cú pháp toạ độ: {e}")
                elif isinstance(cmd, str) and cmd.startswith("set_danhsachmuctieu:"):
                    # set_danhsachmuctieu:{"tancong": [...], "boqua": [...]}
                    try:
                        danhsach = json.loads(cmd.split(":", 1)[1])
                        self.tactu.thietlap_danhsachmuctieu(danhsach.get("tancong", []), danhsach.get("boqua", []))
                    except Exception as e:
                        print(f"Lỗi khi đọc danh sách mục tiêu: {e}")
                elif isinstance(cmd, str) and cmd.startswith("xoa_muctieuboqua:"):
                    # xoa_muctieuboqua:[id, ...] hoặc xoa_muctieuboqua:all
                    try:
                        thamso = cmd.split(":", 1)[1]
                        self.tactu.xoa_muctieuboqua(None if thamso == "all" else [int(i) for i in json.loads(thamso)])
                    except Exception as e:
                        print(f"Lỗi khi xoá mục tiêu bỏ qua: {e}")
                elif cmd == "battat_tranhvungcam":
                    self.tactu.battat_tranhvungcam()
                elif cmd == "battat_dilotrinhkhacbando":
                    self.tactu.battat_dilotrinhkhacbando()
                elif cmd == "battat_giukhoangcachketancong":
                    self.tactu.battat_giukhoangcachketancong()
                elif cmd == "battat_giukhoangcachchimuctieupk":
                    self.tactu.battat_giukhoangcachchimuctieupk()
                elif cmd == "battat_taphoa":
                    self.tactu.battat_taphoa()
                elif cmd == "battat_timmuctieuchung":
                    self.tactu.battat_timmuctieuchung()
                elif isinstance(cmd, str) and cmd.startswith("set_khoangcachgiuketancong:"):
                    try:
                        self.tactu.thietlap_khoangcachgiuketancong(float(cmd.split(":")[1]))
                    except Exception:
                        pass
                elif cmd == "battat_tutimduongtheosau":
                    self.tactu.battat_tutimduongtheosau()
                elif cmd == "battat_sapxephanhtrang":
                    self.tactu.battat_sapxephanhtrang()
                elif cmd == "battat_doidokhitrieuhoi":
                    self.tactu.battat_doidokhitrieuhoi()
                elif cmd == "ghi_bodotrieuhoi":
                    self.tactu.ghi_bodotrieuhoi()
                elif isinstance(cmd, str) and cmd.startswith("set_baothutrieuhoimaoson:"):
                    self.tactu.thietlap_baothutrieuhoimaoson(cmd.split(":", 1)[1])
                elif cmd == "battat_chantangcapdo":
                    self.tactu.battat_is_chantangcapdo()
                elif cmd == "battat_tudongkhaikhoang":
                    self.tactu.battat_is_tudongkhaikhoang()
                elif cmd == "thuchien_tudongbanrac":
                    self.tactu.action_tudongbanrac()
                elif cmd == "botoanbo_tenmuctieutancong":
                    self.tactu.botoanbo_tenmuctieutancong()
                elif cmd == "botoanbo_tenmuctieukhongtancong":
                    self.tactu.botoanbo_tenmuctieukhongtancong()
                elif cmd == "battat_tudongtheosau":
                    self.tactu.battat_is_tudongtheosau()
                elif cmd == "botoanbo_diemdanhxungquanh":
                    self.tactu.botoanbo_diemdanhxungquanh()
                elif cmd == "battat_tudongtodoi":
                    self.tactu.battat_is_tudongtodoi()
                elif cmd == "todoimotlan":
                    self.tactu.batdau_todoimotlan()
                elif cmd == "huytodoimotlan":
                    self.tactu.huy_todoimotlan()
                elif cmd == "battat_thucsondao":
                    self.tactu.battat_is_thucsondao()
                elif cmd == "battat_tudongsudungkynang":
                    self.tactu.battat_is_tudongsudungkynang()
                elif cmd == "them_tenmuctieutancong":
                    self.tactu.them_tenmuctieutancong(self.moitruong.get_tennhanvatchichuot())
                elif cmd == "them_tenmuctieukhongtancong":
                    self.tactu.them_tenmuctieukhongtancong(self.moitruong.get_tennhanvatchichuot())
                elif cmd == "toggle_chidanhnguoichoi":
                    current_state = self.tactu._is_chidanhnguoichoi
                    self.tactu.thietlap_chidanhnguoichoi(not current_state)
                elif cmd == "thietlap_chidanhnguoichoi":
                    self.tactu.thietlap_chidanhnguoichoi(True)
                elif cmd == "bo_thietlap_chidanhnguoichoi":
                    self.tactu.thietlap_chidanhnguoichoi(False)
                elif cmd == "bat_pk":
                    self.tactu.action_batpk()
                elif cmd == "tat_pk":
                    self.tactu.action_tatpk()
                elif cmd == "battat_tudongtrieuhoibaothugiangho":
                    self.tactu.battat_tudongtrieuhoibaothugiangho()
                elif cmd == "them_diemdanhxungquanh":
                    if self.moitruong.get_is_dangmobando():
                        self.tactu.them_diemdanhxungquanh((*self.moitruong.get_toadobandochichuot(), self.moitruong.get_idbandochichuot()))
                    else:
                        self.tactu.them_diemdanhxungquanh((*self.moitruong.get_toado(), self.moitruong.get_idbandohientai()))
                elif cmd == "battat_tudonggomquai":
                    self.tactu.battat_tudonggomquai()
                elif cmd == "battat_tudongvebanrac":
                    self.tactu.battat_tudongvebanrac()
                elif cmd == "battat_tudongdichientruong":
                    self.tactu.battat_is_tudongdichientruong()
                elif cmd == "battat_uutienbaothukynangtrieuhoi":
                    self.tactu.battat_is_uutienbaothukynangtrieuhoi()
                elif cmd == "action_suavatpham":
                    self.tactu.action_suavatpham()
                elif cmd == "battat_chedobufftoanbang":
                    self.tactu.battat_chedobufftoanbang()
                elif cmd == "battat_tudongdaotangbaodo":
                    self.tactu.battat_tudongdaotangbaodo()
                elif cmd == "action_muaauto":
                    self.tactu.action_tudongmuaauto()
                elif cmd == "battat_tudongsudungkynangbaothu":
                    self.tactu.battat_tudongsudungkynangbaothu()
                elif cmd == "action_test":
                    self.tactu.action_test()
                self.command_dict[self.idcuaso] = None

            time.sleep(0.15)