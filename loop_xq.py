import queue
import random
import re
import threading
import time
import traceback
import unicodedata

import pymem.exception

from hangso_xq import IS_BOKHUNGSAUTANCONG, CHUKYBOKHUNGSAUTANCONG, THOIGIANCHOBOKHUNGSAUTANCONG, TUTHENHANVAT_DELAYSAUTANCONG, TUTHENHANVAT_LOI, CHUKYGIUOTRONGHANHTRANG
from hangso_xq import BANDO_BANGPHAI, TRUONGPHONGTIENSINH, RUONGDUTRU
from hangso_xq import BANDO_CHIENTRUONG, BANDO_TANTHUTHON, TUTHENHANVAT_DUNGIM, BANDO_YENTRUONGTHANH3, BANDO_YENTRUONGTHANH2, BANDO_YENTRUONGTHANH1, TANGBAODO, LAMCAU, HACCAU, HIEUUNGKYNANG_TRONGTHUONG
from moitruong_xq import MoiTruong
from tactu_xq import TacTu
from tienich_xq import canhbao


class LoopLamMoiTrangThaiMoiTruong:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop LÀM MỚI] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                print(f"[Loop LÀM MỚI] Lỗi không xác định: {e}")
            time.sleep(0.2)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return
        self.moitruong.action_lammoitrangthaimoitruong()


class LoopTimKiemMucTieu:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop TÌM MỤC TIÊU] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                print(f"[Loop TÌM MỤC TIÊU] Lỗi không xác định: {e}")
            time.sleep(0.15)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return
        if self.tactu.get_is_dangtamngung():
            return
        self.tactu.action_tudongtimkiemmuctieu()
        self.tactu.action_tudongtimkiemmuctieumonphai()
        self.moitruong.action_phananhdiachicosothongtinnhanvatmuctieudangchoningame()


class LoopDieuPhoiDiChuyen:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except Exception as e:
                is_loibonho = isinstance(e, (pymem.exception.PymemError, pymem.exception.WinAPIError))
                print(f"[Loop DI CHUYỂN] Lỗi {'bộ nhớ' if is_loibonho else 'không xác định'}: {e}")
                # Sư môn / đi lại chạy ở vòng này: lỗi lặp lại làm nhân vật đứng im mà file log không thấy gì, ghi cả vào log nhân vật
                # (mỗi lỗi khác nhau ghi 1 lần, lặp mỗi 0.05s thì log đầy)
                vet = traceback.format_exc()
                if vet != getattr(self, "_loidaghi", None):
                    self._loidaghi = vet
                    try:
                        self.moitruong._inlog(f"[Loop DI CHUYỂN] Lỗi: {e}\n{vet}")
                    except Exception:
                        pass
                if is_loibonho:
                    time.sleep(1)
            time.sleep(0.05)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return
        # Sau lag giờ máy chủ của client bị tụt => máy chủ từ chối mọi bước đi: sửa ngay (chạy cả lúc bot tạm ngưng / người chơi tự đi)
        self.moitruong.action_suagiomaychu()
        if self.tactu.get_is_dangtamngung():
            return
        # Đang sắp xếp hành trang: đứng lại cho xếp xong (action_sapxephanhtrang bỏ lượt khi tư thế đang di chuyển, chạy lộ trình liên
        # tục thì gần như không xếp được món nào); xếp mỗi lệnh ~0.1s nên chỉ dừng vài giây
        if self.tactu._is_dangsapxephanhtrang:
            return
        # Tính đích theo nhóm ngay trước khi di chuyển (để ở loop chính thì phải chờ cả lượt dùng kỹ năng, đích bị cũ nên chạy theo vị trí trưởng nhóm từ lâu)
        self.tactu.action_tudongtheosau()
        self.tactu.action_chaytoibuffthanhvien()
        self.tactu.action_xulyuutiendichuyen()


class LoopChinh:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        self.thoidiemhopthanhtinhthach_map = {}
        self.thoidiemlogtinhthachgannhat = 0.

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop CHÍNH] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                print(f"[Loop CHÍNH] Lỗi không xác định: {e}")
                traceback.print_exc()
                # Ghi cả vào file log nhân vật: lỗi lặp lại mỗi lượt làm nhân vật đứng im không dùng kỹ năng mà log không thấy gì
                try:
                    self.moitruong._inlog(f"[Loop CHÍNH] Lỗi: {e}\n{traceback.format_exc()}")
                except Exception:
                    pass
                time.sleep(1)
            time.sleep(0.1)

    def _guilenhchomenu(self, caulenh, thoigianchotoida = 2.):
        # Gửi lệnh hội thoại NPC rồi chờ menu trả lời về (lời thoại cửa sổ tuỳ chọn có lại), tối đa thoigianchotoida giây.
        # -> True khi có menu về (không về thì lệnh trong cửa sổ là của menu cũ, đừng dùng)
        self.moitruong.xoa_noidungcuasotuychon()
        self.moitruong.action_thucthicaulenh(caulenh)
        hethan = time.time() + thoigianchotoida
        while time.time() < hethan and not self.moitruong.get_noidungcuasotuychon():
            time.sleep(0.1)
        time.sleep(0.25)
        return bool(self.moitruong.get_noidungcuasotuychon())

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        if self.tactu.get_is_dangtamngung():
            return

        self.tactu.action_tudongxulygomquai()
        self.tactu.action_tudongsudungkynang()
        self.tactu.action_tudongdieukhienbaothu()

        # if self.moitruong.get_idnguoichoi() == 59844:
        #     print("{}".format(self.moitruong.get_danhsachhieuungnhanvats()))

        if self.moitruong.get_idbandohientai() == BANDO_BANGPHAI:
            # Nộp Rương Dự Trữ qua Trưởng Phòng Tiên Sinh, 4 bước như bấm tay: Hỗ trợ nhiệm vụ trù bị, Nhận nhiệm vụ,
            # (bấm lại NPC) Hoàn thành nhiệm vụ trù bị, Xác nhận. Số lệnh info.xx máy chủ đổi (info.55 / 58, info.11 / 18...)
            # nên mỗi bước lấy lệnh của lựa chọn đầu tiên trong menu vừa hiện thay vì ghi cứng số
            diachitruongphong = self.moitruong.action_timkiemnhanvat(tennhanvat = TRUONGPHONGTIENSINH)
            idtruongphong = self.moitruong.get_iddoituong(diachitruongphong) if diachitruongphong else 0
            if idtruongphong and self.moitruong.action_timkiemvatphamhanhtrang(RUONGDUTRU):
                # Bấm NPC = "look <id>#" (mở menu gốc), mỗi bước chọn lựa chọn đầu tiên; menu không về thì thôi lượt này.
                # Nhận nhiệm vụ và Xác nhận không có menu trả lời: gửi xong làm tiếp luôn, không chờ (trước chờ hết 2s mỗi lần)
                for is_bamnpc, is_comenutraloi in ((True, True), (False, False), (True, True), (False, False)):
                    if is_bamnpc and not self._guilenhchomenu("look {:x}#".format(idtruongphong)):
                        break
                    lenhs = [lenh for lenh in self.moitruong.get_lenhcuasotuychons() if lenh.startswith("talk {:x}# info.".format(idtruongphong))]
                    if not lenhs:
                        break
                    if not is_comenutraloi:
                        self.moitruong.action_thucthicaulenh(lenhs[0])
                        time.sleep(0.3)
                    elif not self._guilenhchomenu(lenhs[0]):
                        break

        if self.moitruong.get_idnguoichoi() in (342, 347, 354, 359, 364):
            # Đọc tên hành trang 1 lần rồi chỉ gửi lệnh với món đang có: trước đây mỗi món gọi action_sudungvatphamhanhtrang đọc lại cả
            # ~96 ô (9 lần đọc cả hành trang mỗi lượt kể cả khi không có túi nào; py-spy 2026-11-14: ~8% thời gian bận của tiến trình)
            tenhanhtrangs = set(self.moitruong.get_danhsachtenvatphamhanhtrang())
            for tenvatpham in ("Lễ Bao Khai Quốc", "Túi Ngân Lượng", "Túi Ngân Lượng Lớn", "Túi Kim Bảo", "Túi Quà Vô Song", "Túi Pháp Bảo", "Lăng Mộ Bảo Rương", "Túi Quà Thành Kiều", "Túi Tử Kim 85"):
                if tenvatpham in tenhanhtrangs and self.tactu.action_sudungvatphamhanhtrang(tenvatpham):
                    break

            def chuanhoaten(ten):
                # Bỏ dấu, gộp khoảng trắng thừa và bỏ phân biệt hoa thường để "Thủy"/"Thuỷ", "Tinh  Thạch" đều khớp
                if not ten:
                    return ""
                ten = "".join(c for c in unicodedata.normalize("NFD", ten) if not unicodedata.combining(c))
                return " ".join(ten.replace("đ", "d").replace("Đ", "D").split()).lower()

            # Hợp thành Tinh Thạch khi có >= 5 viên cùng tên
            for tenvatphamhanhtrang, vatphams in self.moitruong.get_danhsachvatphamhanhtrang_map().items():
                tenchuanhoa = chuanhoaten(tenvatphamhanhtrang)
                if "tinh thach" not in tenchuanhoa:
                    continue
                capdo = re.search(r"cap\s*(\d+)", tenchuanhoa)
                # Chỉ hợp thành Tinh Thạch dưới cấp 3
                if capdo and int(capdo.group(1)) >= 3:
                    continue
                # Nhóm vừa gửi lệnh hợp thành thì nhường lượt cho nhóm khác, tránh một nhóm lỗi chặn cả các cấp sau
                if time.time() - self.thoidiemhopthanhtinhthach_map.get(tenvatphamhanhtrang, 0) < 2.:
                    continue
                iddoituongs = [iddoituong for vitri, iddoituong in vatphams if iddoituong]
                if len(iddoituongs) >= 5:
                    self.moitruong.action_thucthicaulenh2("mix5 {} 0".format(" ".join("{}#".format(hex(x).replace("0x", "")) for x in iddoituongs[:5])))
                    self.thoidiemhopthanhtinhthach_map[tenvatphamhanhtrang] = time.time()
                    time.sleep(0.25)
                    break

        # vitrivatphams = [0, ]
        # if self.moitruong.get_idnguoichoi() == 102:
        #     for vitrivatpham in vitrivatphams:
        #         while True:
        #             iddoituong = self.moitruong.get_iddoituongvatphamhanhtrang(vitrivatpham)
        #             if not iddoituong:
        #                 break
        #             self.moitruong.truyvan_motavatphamhanhtrang(vitrivatpham)
        #             motavatpham = self.moitruong.get_motavatphamhanhtrang(vitrivatpham)
        #             #print("Mô tả vật phẩm: {}".format(motavatpham))
        #
        #             match = re.search(r"Nội Kháng:\s*\+(\d+)", motavatpham)
        #
        #             if match:
        #                 chisohientai = int(match.group(1))
        #                 print(f"Đã tìm thấy Nội Kháng: {chisohientai}")
        #
        #                 if chisohientai >= 85:
        #                     print("Nội Kháng >= 85. Dừng tiến trình!")
        #                     break
        #                 else:
        #                     self.moitruong.action_thucthicaulenh2("tallk 165a# giaotrangbi.{}# 0".format(hex(iddoituong)).replace("0x", ""))
        #                     time.sleep(0.2)
        #             else:
        #                 print("Không tìm thấy dòng Nội Kháng trong mô tả vật phẩm này.")
        #                 self.moitruong.action_thucthicaulenh2("tallk 165a# giaotrangbi.{}# 0".format(hex(iddoituong)).replace("0x", ""))
        #                 time.sleep(0.2)

        # if self.moitruong.get_idnguoichoi() == 60055:
        #     if not self.moitruong.action_timkiemvatphamhanhtrang("Túi Pháp Bảo"):
        #         self.moitruong.action_thucthicaulenh("buyitem ! 5 4 1")
        #         time.sleep(0.25)

        # if self.moitruong.get_idnguoichoi() in (59844, 59845):
        #     diachithiensutraodoi = self.moitruong.action_timkiemnhanvat("Thiên Sứ Trao Đổi")
        #     if not diachithiensutraodoi:
        #         return
        #     idthiensutraodoi = self.moitruong.get_iddoituong(diachithiensutraodoi)
        #     if not idthiensutraodoi:
        #         return
        #     if self.moitruong.get_khoangcach(diachithiensutraodoi) > 6:
        #         return
        #     if not self.moitruong.action_timkiemvatphamhanhtrang(LAMCAU) or not self.moitruong.action_timkiemvatphamhanhtrang(HACCAU):
        #         return
        #     self.moitruong.action_thucthicaulenh("tallk {}# bonus.29".format(hex(idthiensutraodoi).replace("0x", "")))
        #     time.sleep(0.25)
        #
        #     iddoituongtuivaibaobo = self.moitruong.action_timkiemvatphamhanhtrang("Bao Vải Ma Bố")
        #
        #     if iddoituongtuivaibaobo:
        #         self.moitruong.action_thucthicaulenh("drop ! {}#1".format(hex(iddoituongtuivaibaobo)).replace("0x", ""))
        #         time.sleep(0.25)
        #

        # if self.moitruong.get_idnguoichoi() == 59996:
        #     idtinhnguyendon = self.moitruong.action_timkiemvatphamhanhtrang("Tinh Nguyên Đơn")
        #     iddoituongbaothugiangho = self.moitruong.get_iddoituongbaothugiangho()
        #     if idtinhnguyendon and iddoituongbaothugiangho:
        #         idtinhnguyendon = hex(idtinhnguyendon).replace("0x", "")
        #         iddoituongbaothugiangho = hex(iddoituongbaothugiangho).replace("0x", "")
        #
        #         caulenh = "pet {}# fuse_yy {}#".format(iddoituongbaothugiangho, idtinhnguyendon)
        #         print()
        #         self.moitruong.action_thucthicaulenh(caulenh)
        #         time.sleep(0.25)


class LoopPhu:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event, giamsat = None):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        # Watchdog (giamsat_xq): mỗi lượt đánh dấu nhịp, lâu không có là luồng treo
        self.giamsat = giamsat
        self.thoidiemthongbaochetgannhat = time.time()
        self.thoidiempfgannhat = time.time()

    def __del__(self):
        try:
            self.moitruong.action_tatvohieuhoathietlapmuctieu()
            self.moitruong.action_tatvohieuhoatuthedelaysautancong()
            self.moitruong.action_tatvohieuhoalongclick()
            self.moitruong.action_tatvohieuhoatrangthaichuotchonmuctieukynang()
            self.moitruong.action_tatvohieuhoaphimspace()
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass
        if not self.stop.is_set():
            self.stop.set()

    def _thongbaochet(self):
        if self.moitruong.get_is_nhanvatdachet() and self.moitruong.get_idbandohientai() != BANDO_CHIENTRUONG:
            if time.time() - self.thoidiemthongbaochetgannhat > 5.0:
                self.thoidiemthongbaochetgannhat = time.time()
                # Không đọc lên (người dùng dặn 2026-11-14: nghe đau đầu, đã có Telegram báo chết - thongbao_xq.TheoDoiSuCo)
                canhbao(self.moitruong, "Nhân vật đã chết", is_block = False, is_phatam = False)

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                self.step()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop PHỤ] Lỗi bộ nhớ: {err}")
                time.sleep(1)
            except Exception as e:
                traceback.print_exc()
                print(f"[Loop PHỤ] Lỗi không xác định: {e}")
                # Kéo cấp / phó bản / bán rác chạy ở vòng này: lỗi lặp lại làm nhân vật đứng im mà file log không thấy gì, ghi cả vào log
                # nhân vật (mỗi lỗi khác nhau ghi 1 lần, lặp mỗi 0.5s thì log đầy)
                vet = traceback.format_exc()
                if vet != getattr(self, "_loidaghi", None):
                    self._loidaghi = vet
                    try:
                        self.moitruong._inlog(f"[Loop PHỤ] Lỗi: {e}\n{vet}")
                    except Exception:
                        pass
            if self.giamsat:
                self.giamsat.danhdau("phụ")
            self._ngu_hoacsapxephanhtrang(0.5)

    def _ngu_hoacsapxephanhtrang(self, thoigian, chuky = 0.05):
        # Nghỉ giữa 2 lượt step; đang sắp xếp hành trang thì trong lúc nghỉ vẫn gọi action_sapxephanhtrang mỗi chuky giây để gửi lệnh
        # move kế ngay khi lệnh trước có kết quả (trước chỉ 1 lệnh/lượt step ~0.5-1s nên rất chậm), các việc khác giữ nhịp cũ
        hethan = time.time() + thoigian
        while not self.stop.is_set():
            conlai = hethan - time.time()
            if conlai <= 0:
                return
            if not self.tactu._is_dangsapxephanhtrang and not self.tactu._sapxepkho:
                time.sleep(conlai)
                return
            time.sleep(min(chuky, conlai))
            try:
                self.tactu.action_sapxephanhtrang()
                # Lệnh pawn client tự gửi (mã kho) cần đọc kịp trước khi sắp xếp kho tìm mã
                self.moitruong.action_loglenhgame()
                self.tactu.action_sapxepkho()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop PHỤ] Lỗi bộ nhớ khi sắp xếp hành trang / kho: {err}")
                time.sleep(0.5)
            except Exception as e:
                traceback.print_exc()
                print(f"[Loop PHỤ] Lỗi khi sắp xếp hành trang / kho: {e}")
                time.sleep(0.5)

    def step(self):
        if not self.moitruong.get_is_nhanvattontai():
            return

        self.moitruong.action_vohieuhoathietlapmuctieu()
        self.moitruong.action_vohieuhoatuthedelaysautancong()
        if self.tactu._is_tudongsudungkynang:
            self.moitruong.action_vohieuhoalongclick()
        else:
            self.moitruong.action_tatvohieuhoalongclick()
        self.moitruong.action_vohieuhoatrangthaichuotchonmuctieukynang()
        self.moitruong.action_vohieuhoakhoanhvungkynang()
        self.moitruong.action_vohieuhoaphimspace()
        self.moitruong.action_vohieuhieuungmuloa()
        self.moitruong.action_ghiloimoinhom()

        # Thấy người chơi ẩn thân, hoặc người lạ ở map train, khi đang di chuyển theo lộ trình điểm đánh, hoặc thấy ẩn thân trong phó bản:
        # ngưng mọi hoạt động, báo Telegram (có nút Bật lại trên bảng điều khiển)
        self.tactu.action_kiemtraanthan()
        if self.tactu.get_is_dangtamngung():
            return

        # Đang nằm chết chờ phục sinh: không làm gì khác (trước đây luồng này bị sleep chặn trong lúc chờ nên cũng không làm gì)
        self.tactu.action_tudongphucsinh()
        if self.tactu.get_is_dangchophucsinh():
            self._thongbaochet()
            return

        self.tactu.action_tudongsudungvatpham()
        self.tactu.action_chantangcapdo()
        self.tactu.action_tudongxepchongvatpham()
        self.tactu.action_sapxephanhtrang()
        self.tactu.action_sapxepkho()
        self.tactu.action_tudongdatvatphammoi()
        self.tactu.action_tudongtodoi()
        self.tactu.action_tudongdoimaupk()
        self.tactu.action_tudonghoibangphai()
        self.tactu.action_tudongmuavatpham()
        self.tactu.action_tudongsuavatpham()

        self.tactu.action_xulyhoithoainpc()
        self.tactu.action_xulyxaphunietban()
        self.tactu.action_xulybanracvasuado()
        self.tactu.action_tudongxulyvebanrac()
        self.tactu.action_tudongkhaikhoang()
        self.tactu.action_tudongdaotangbaodo()

        self.tactu.action_tudongtrieuhoibaothugiangho()

        self.tactu.action_tudongdichientruong()
        self.tactu.action_tudongdichuyentudo()
        self.tactu.action_tudongnhatvatpham()
        self.tactu.action_tudongvutvatpham()
        self.tactu.action_tudongvutvatphamtheoluat()
        self.tactu.action_tudongdeokythu()

        self._thongbaochet()

        if not self.moitruong.get_is_bathanhtrang():
            self.moitruong.set_is_batalt(True)

        self.moitruong.action_vohieuhoahookchienquoc2()
        self.moitruong.action_loglenhgame()
        self.moitruong.action_dokho()

        if self.moitruong.get_idnguoichoi() in (59996, ) and self.moitruong.get_idbandohientai() == BANDO_TANTHUTHON and self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
            diachi = self.moitruong.action_timkiemnhanvat("Thiên Sứ Trao Đổi")
            if diachi and self.moitruong.get_khoangcach(diachi) <= 3.:
                lamcau = self.moitruong.action_timkiemvatphamhanhtrang(LAMCAU)
                haccau = self.moitruong.action_timkiemvatphamhanhtrang(HACCAU)
                if lamcau and haccau:
                    self.moitruong.action_thucthicaulenh("tallk {}# bonus.23".format(hex(self.moitruong.get_iddoituong(diachi))).replace("0x", ""))
                    time.sleep(0.25)
                elif lamcau:
                    self.moitruong.action_thucthicaulenh("tallk {}# bonus.9".format(hex(self.moitruong.get_iddoituong(diachi))).replace("0x", ""))

                for _ in range(2):
                    iddoituongtangbaodo = self.moitruong.action_timkiemvatphamhanhtrang(TANGBAODO, is_ruongdautien = True)
                    if iddoituongtangbaodo:
                        self.moitruong.action_thucthicaulenh("move {}# to {}".format(hex(iddoituongtangbaodo), random.randint(2, 4)).replace("0x", ""))


class LoopBoKhungSauTanCong:
    # Luồng riêng, chu kỳ ngắn (CHUKYBOKHUNGSAUTANCONG): tư thế khựng sau đòn kéo dài quá THOIGIANCHOBOKHUNGSAUTANCONG giây
    # thì ghi về đứng im (các luồng khác chạy 0.1-0.5s/lượt nên không bắt kịp)
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop
        # Lúc nhân vật bắt đầu vào tư thế khựng sau đòn (0 = không đang khựng)
        self.thoidiembatdaukhung = 0.
        # Lần log gần nhất khi ghi bỏ tư thế lỗi (TUTHENHANVAT_LOI): luồng chạy 0.02s/lượt, game ghi lại liên tục thì khỏi tràn log
        self.thoidiemlogtuthelo = 0.

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                # Đọc tư thế 1 lần mỗi lượt (py-spy 2026-11-12: luồng 0.02s/lượt đọc 2 lần là điểm đọc bộ nhớ nhiều nhất còn lại)
                tuthe = self.moitruong.get_idtuthenhanvat() if self.moitruong.get_is_nhanvattontai() else None
                if tuthe == TUTHENHANVAT_LOI:
                    self.moitruong.set_idtuthenhanvat(TUTHENHANVAT_DUNGIM)
                    tuthe = TUTHENHANVAT_DUNGIM
                    if time.time() - self.thoidiemlogtuthelo > 5:
                        self.thoidiemlogtuthelo = time.time()
                        self.moitruong._inlog("[BỎ TƯ THẾ LỖI] tư thế 15 => ghi về đứng im")
                if IS_BOKHUNGSAUTANCONG and tuthe == TUTHENHANVAT_DELAYSAUTANCONG:
                    if not self.thoidiembatdaukhung:
                        self.thoidiembatdaukhung = time.time()
                    elif time.time() - self.thoidiembatdaukhung >= THOIGIANCHOBOKHUNGSAUTANCONG:
                        self.moitruong.set_idtuthenhanvat(TUTHENHANVAT_DUNGIM)
                        self.thoidiembatdaukhung = 0.
                else:
                    self.thoidiembatdaukhung = 0.
            except (pymem.exception.PymemError, pymem.exception.WinAPIError):
                time.sleep(1)
            except Exception as e:
                print(f"[Loop BỎ KHỰNG] Lỗi không xác định: {e}")
                time.sleep(1)
            time.sleep(CHUKYBOKHUNGSAUTANCONG)


class LoopGiuOTrongHanhTrang:
    # Luồng riêng, chu kỳ ngắn (CHUKYGIUOTRONGHANHTRANG) cho việc hành trang / trang bị cần nhanh trong lúc vận khí
    # (LoopPhu 0.5s/lượt không kịp): đang chế đồ thì vật phẩm vừa vào ô cuối hành trang 1 phải được chuyển đi ngay trước lần chế
    # kế tiếp; đang vận khí gọi bảo thú triệu hồi thì đổi đồ, xong mặc lại; kỹ năng vừa gửi cần đứng lại thì ngắt di chuyển
    # ngay khi nhân vật vào tư thế xuất chiêu
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                if self.moitruong.get_is_nhanvattontai():
                    # Cập nhật mốc xuất chiêu đủ dày để biết chính xác lúc hết tư thế xuất chiêu (khựng tính từ mốc này)
                    self.moitruong.get_is_dangxuatchieu()
                    self.moitruong.action_baogiuluotkhixuatchieu()
                    self.tactu.action_giuotrongcuoihanhtrang()
                    self.tactu.action_doidokhitrieuhoi()
                    self.tactu.action_ngatdichuyenkhixuatchieu()
            except (pymem.exception.PymemError, pymem.exception.WinAPIError):
                time.sleep(1)
            except Exception as e:
                print(f"[Loop GIỮ Ô TRỐNG] Lỗi không xác định: {e}")
                traceback.print_exc()
                time.sleep(1)
            time.sleep(CHUKYGIUOTRONGHANHTRANG)


class LoopXuLyLenh:
    def __init__(self, moitruong: MoiTruong, tactu: TacTu, stop: threading.Event):
        self.moitruong = moitruong
        self.tactu = tactu
        self.stop = stop

    def __del__(self):
        if not self.stop.is_set():
            self.stop.set()

    def loop(self):
        while not self.stop.is_set() and self.moitruong.get_is_cuasogametontai():
            try:
                lenhthucthi = self.moitruong.hangdoicaulenh.get(timeout = 0.05)
                if lenhthucthi.caulenh in self.moitruong.caulenhdangchos:
                    self.moitruong.caulenhdangchos.remove(lenhthucthi.caulenh)
                self.moitruong._ghilenhvaobonho(lenhthucthi)
                self.moitruong.hangdoicaulenh.task_done()
            except queue.Empty:
                continue
            except (pymem.exception.PymemError, pymem.exception.WinAPIError) as err:
                print(f"[Loop XỬ LÝ LỆNH] Lỗi bộ nhớ: {err}")
                time.sleep(0.1)
            except Exception as e:
                print(f"[Loop XỬ LÝ LỆNH] Lỗi không xác định: {e}")
                time.sleep(0.1)
