import ast
import threading
import time
import traceback

from loop_xq import (
    LoopLamMoiTrangThaiMoiTruong,
    LoopTimKiemMucTieu,
    LoopChinh,
    LoopPhu,
    LoopDieuPhoiDiChuyen,
    LoopXuLyLenh
)
from moitruong_xq import MoiTruong
from tactu_xq import TacTu


def khoidong_looptonghop(moitruong, tactu, stop):
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
        time.sleep(0.1)


def khoidong_loopphu(moitruong, tactu, stop):
    LoopPhu(moitruong, tactu, stop).loop()

def khoidong_loopxulylenh(moitruong, tactu, stop):
    LoopXuLyLenh(moitruong, tactu, stop).loop()

class CuaSo:
    def __init__(self, idcuaso, shared_data, command_dict):
        self.idcuaso = idcuaso
        self.shared_data = shared_data
        self.command_dict = command_dict

        self.moitruong = MoiTruong(idcuaso)
        self.moitruong.action_thietlaphooknoidungtrochuyen()
        self.tactu = TacTu(self.moitruong)
        self.main_stop = threading.Event()

        self.tennhanvat = None
        self.idnguoichoi = 0
        self.thoidiemluuthietlap = time.time()

        self.luongs = (
            threading.Thread(target = khoidong_looptonghop, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopphu, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
            threading.Thread(target = khoidong_loopxulylenh, args = [self.moitruong, self.tactu, self.main_stop], daemon = True),
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

        self.main_stop.set()
        self._chotoanbocacluongdunghan()

        if self.idcuaso in self.shared_data:
            del self.shared_data[self.idcuaso]

        if self.idcuaso in self.command_dict:
            del self.command_dict[self.idcuaso]

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

                    self.tactu.taithietlap(idnguoichoi)
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

                info = {
                    "tennhanvat": tennhanvat,
                    "tenbando": self.moitruong.get_idbandohientai(),
                    "x": x,
                    "y": y,
                    "status": tentrangthai,
                    "phantramsinhluc": phantramsinhluc,
                    "phantramnoiluc": phantramnoiluc,
                    "is_window_active": self.moitruong.get_is_cuasogamekichhoat(),

                    "_is_tudongtheosautruongnhom": self.tactu._is_tudongtheosautruongnhom,
                    "_is_tudongbattheosaunhom": self.tactu._is_tudongbattheosaunhom,
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

                    "_tenmuctieutancongs": ", ".join(self.tactu._tenmuctieutancongs),
                    "_tenmuctieukhongtancongs": ", ".join(self.tactu._tenmuctieukhongtancongs),
                    "_khoangcachtoidatruongnhom": self.tactu._khoangcachtoidatruongnhom,

                    "_is_tudongdichuyendiemdanhxungquanh": self.tactu._is_tudongdichuyendiemdanhxungquanh,
                    "_diemdanhxungquanhs": self.tactu._diemdanhxungquanhs,
                    "_is_tudongtrieuhoibaothugiangho": self.tactu._is_tudongtrieuhoibaothugiangho,
                    "_is_tudongbattatchucnangmorong": self.tactu._is_tudongbattatchucnangmorong,

                    "_is_tudongsudungkynangbaothu": self.tactu._is_tudongsudungkynangbaothu,
                }
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
                elif isinstance(cmd, str) and cmd.startswith("set_khoangcachtheosau:"):
                    try:
                        khoangcach = float(cmd.split(":")[1])
                        self.tactu.thietlap_khoangcachtheosau(khoangcach)
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
                elif cmd == "battat_tudongbattatchucnangmorong":
                    self.tactu.battat_tudongbattatchucnangmorong()
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
                elif cmd == "battat_tudongtheosautruongnhom":
                    self.tactu.battat_is_tudongtheosautruongnhom()
                elif cmd == "botoanbo_diemdanhxungquanh":
                    self.tactu.botoanbo_diemdanhxungquanh()
                elif cmd == "battat_tudongbattheosaunhom":
                    self.tactu.battat_is_tudongbattheosaunhom()
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
                self.command_dict[self.idcuaso] = None

            time.sleep(0.15)