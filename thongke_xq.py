# Thống kê hiệu suất farm theo nhân vật:
#   Mỗi CHUKYLAYMAU giây lấy mẫu kinh nghiệm, ngân lượng, cờ đã chết; mỗi CHUKYDEMHANHTRANG giây đếm hành trang theo tên. Phần chênh
#   so với mẫu trước cộng vào ô (giờ, bản đồ, lộ trình) đang đứng. Lưu theo ID người chơi: _internal/thongke/<id>.json =
#   {"YYYY-MM-DD HH": {"<id bản đồ>|<lộ trình>": {giay, kinhnghiem, kinhnghiemmat, nganluongthu, nganluongchi, chet,
#                                                  vatphamnhan: {tên: số}, vatphammat: {tên: số}}}}
#   Hiệu suất chỉ tính phần nhận (kinhnghiem, nganluongthu): phần bị trừ (nâng cấp kỹ năng trừ cả kinh nghiệm lẫn ngân lượng, mua đồ,
#   sửa đồ, chết...) ghi riêng vào kinhnghiemmat / nganluongchi và hiện là "đã tiêu", không trừ vào hiệu suất farm.
#   Kinh nghiệm đã đầy (cấp tối đa) thì không tăng nữa, cột kinh nghiệm ra 0
#   Món "mất" gồm cả thuốc đã dùng, đồ đã bán / vứt / cất kho (đọc hành trang không phân biệt được)
#   Chuyển cho nhau giữa các nhân vật cùng máy (giao dịch, vứt cho người kia nhặt): biến động ngân lượng / vật phẩm chờ THOIGIANCHOKHOP
#   giây mới ghi. Mỗi cửa sổ đưa biến động gần đây lên shared_data ("_biendongtainguyen"); nhân vật khác có biến động ngược dấu đúng
#   bằng số đó, cùng tên món, lệch nhau không quá LECHTHOIGIANKHOP giây thì ghi vào nganluongchuyenden / nganluongchuyendi /
#   vatphamchuyenden / vatphamchuyendi, không tính là nhận / tiêu. Chuyển với người chơi máy khác thì không nhận ra được
import json
import os
import sys
import threading
import time

CHUKYLAYMAU = 2.
CHUKYDEMHANHTRANG = 10.
CHUKYLUU = 60.
# Hai mẫu cách nhau lâu hơn chừng này (bot treo, đang tải bản đồ...) thì không tính thời gian khoảng đó
KHOANGTRONGTOIDA = 10.
SONGAYGIULAI = 60
# Hành trang đếm mỗi CHUKYDEMHANHTRANG giây nên hai bên của một lần chuyển có thể lệch nhau chừng đó
LECHTHOIGIANKHOP = 15.
THOIGIANCHOKHOP = 20.
THOIGIANGIULAIBIENDONG = 45.
IS_LOGCHUYEN = True

LOTRINH_TATTUDANH = "Tắt tự đánh"
LOTRINH_DUNGTAICHO = "Đứng tại chỗ"
LOTRINH_TUDAT = "Điểm đánh tự đặt"

_khoaghi = threading.Lock()


def _thumucthongke():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "thongke")


def duongdanthongke(idnguoichoi):
    return os.path.join(_thumucthongke(), f"{idnguoichoi}.json")


def taithongke(idnguoichoi):
    try:
        with open(duongdanthongke(idnguoichoi), "r", encoding = "utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return {}


def _oxuatphat():
    return {"giay": 0., "kinhnghiem": 0, "kinhnghiemmat": 0, "nganluongthu": 0, "nganluongchi": 0, "chet": 0,
            "vatphamnhan": {}, "vatphammat": {}, "nganluongchuyenden": 0, "nganluongchuyendi": 0,
            "vatphamchuyenden": {}, "vatphamchuyendi": {}}


def _congo(dich, nguon):
    for khoa, giatri in nguon.items():
        if isinstance(giatri, dict):
            vatphams = dich.setdefault(khoa, {})
            for ten, soluong in giatri.items():
                vatphams[ten] = vatphams.get(ten, 0) + soluong
        else:
            dich[khoa] = dich.get(khoa, 0) + giatri


def gopthongke(dulieu, tugio = None):
    # Cộng các giờ từ tugio ("YYYY-MM-DD HH", None = tất cả) theo "<id bản đồ>|<lộ trình>" -> ô tổng
    tong = {}
    for gio, cacos in dulieu.items():
        if tugio and gio < tugio:
            continue
        for khoa, o in cacos.items():
            _congo(tong.setdefault(khoa, _oxuatphat()), o)
    return tong


class ThongKe:
    def __init__(self, moitruong, tactu):
        self.moitruong = moitruong
        self.tactu = tactu
        self._idnguoichoi = 0
        # step chạy ở luồng thống kê, luu còn được gọi lúc tắt bot từ luồng khác
        self._khoa = threading.RLock()
        # Phần chưa ghi xuống file: {"YYYY-MM-DD HH": {khoá: ô}}
        self._chualuu = {}
        self._thoidiemluugannhat = time.time()
        # Biến động ngân lượng / vật phẩm chưa ghi (chờ so với nhân vật khác): [(thời điểm, tên món hoặc "" là ngân lượng, số có dấu, giờ, khoá ô)]
        self._chokhops = []
        # Biến động gần đây đưa lên shared_data cho cửa sổ khác so: [(thời điểm, tên, số có dấu)]
        self._biendongs = []
        self._datlaimau()
        # Tổng từ lúc bật bot (hiện trên giao diện)
        self.phien = _oxuatphat()

    def _datlaimau(self):
        self._thoidiemmautruoc = None
        self._kinhnghiemtruoc = None
        self._capdotruoc = None
        self._nganluongtruoc = None
        self._is_chettruoc = None
        self._hanhtrangtruoc = None
        self._thoidiemdemhanhtrang = 0.

    def _get_tenlotrinh(self):
        if not self.tactu._is_tudongsudungkynang:
            return LOTRINH_TATTUDANH
        if not self.tactu._is_tudongdichuyendiemdanhxungquanh:
            return LOTRINH_DUNGTAICHO
        phan = (self.tactu._lotrinhmaudangdung or "").split("|")
        return phan[1] if len(phan) >= 2 and phan[1] else LOTRINH_TUDAT

    def _vitrihientai(self):
        return time.strftime("%Y-%m-%d %H"), f"{self.moitruong.get_idbandohientai()}|{self._get_tenlotrinh()}"

    def _layo(self, vitri = None):
        gio, khoa = vitri or self._vitrihientai()
        return self._chualuu.setdefault(gio, {}).setdefault(khoa, _oxuatphat())

    def _cong(self, ten, giatri, vitri = None):
        if not giatri:
            return
        self._layo(vitri)[ten] += giatri
        self.phien[ten] += giatri

    def _congvatpham(self, ten, tenvatpham, soluong, vitri = None):
        o = self._layo(vitri)[ten]
        o[tenvatpham] = o.get(tenvatpham, 0) + soluong
        self.phien[ten][tenvatpham] = self.phien[ten].get(tenvatpham, 0) + soluong

    def _ghinhanbiendong(self, tenvatpham, chenh):
        # Ngân lượng (tenvatpham "") / vật phẩm đổi: chưa ghi ngay, chờ xem có phải chuyển với nhân vật khác không
        now = time.time()
        self._chokhops.append((now, tenvatpham, chenh, *self._vitrihientai()))
        self._biendongs.append((now, tenvatpham, chenh))

    def get_biendongganday(self):
        moc = time.time() - THOIGIANGIULAIBIENDONG
        self._biendongs = [b for b in self._biendongs if b[0] >= moc]
        return list(self._biendongs)

    def _laybiendongnhanvatkhac(self):
        # [(thời điểm, tên, số có dấu)] của các cửa sổ khác cùng máy, không tính cửa sổ cùng nhân vật này
        shared_data = getattr(self.tactu, "shared_data", None)
        if shared_data is None:
            return []
        idcuaso = getattr(self.tactu, "idcuaso", None)
        ketqua = []
        try:
            for hwnd, info in shared_data.items():
                if hwnd == idcuaso or not isinstance(info, dict) or info.get("idnguoichoi") == self._idnguoichoi:
                    continue
                ketqua.extend(tuple(b) for b in info.get("_biendongtainguyen") or [])
        except Exception:
            return []
        return ketqua

    def _xulychokhop(self, is_tatca = False):
        now = time.time()
        dens = [c for c in self._chokhops if is_tatca or now - c[0] >= THOIGIANCHOKHOP]
        if not dens:
            return
        self._chokhops = self._chokhops[len(dens):] if not is_tatca else []
        khacs = self._laybiendongnhanvatkhac()
        for thoidiem, tenvatpham, chenh, gio, khoa in dens:
            vitri = (gio, khoa)
            khop = next((b for b in khacs if b[1] == tenvatpham and b[2] == -chenh and abs(b[0] - thoidiem) <= LECHTHOIGIANKHOP), None)
            if khop:
                # Mỗi biến động của bên kia chỉ khớp 1 lần
                khacs.remove(khop)
                if IS_LOGCHUYEN:
                    self.moitruong._inlog(f"[THỐNG KÊ] Chuyển {'nhận' if chenh > 0 else 'đi'} {abs(chenh)} {tenvatpham or 'ngân lượng'}")
            if not tenvatpham:
                loai = ("nganluongchuyenden" if chenh > 0 else "nganluongchuyendi") if khop else ("nganluongthu" if chenh > 0 else "nganluongchi")
                self._cong(loai, abs(chenh), vitri)
            else:
                loai = ("vatphamchuyenden" if chenh > 0 else "vatphamchuyendi") if khop else ("vatphamnhan" if chenh > 0 else "vatphammat")
                self._congvatpham(loai, tenvatpham, abs(chenh), vitri)

    def step(self):
        with self._khoa:
            self._step()

    def _step(self):
        moitruong = self.moitruong
        if not moitruong.get_is_nhanvattontai() or moitruong.get_is_dangmatketnoi():
            # Đang tải / mất kết nối: số đọc được không tin được, lấy mẫu lại từ đầu khi vào lại
            self._datlaimau()
            return

        idnguoichoi = moitruong.get_idnguoichoi()
        if not idnguoichoi:
            return
        if idnguoichoi != self._idnguoichoi:
            # Cửa sổ đổi sang nhân vật khác: ghi phần của nhân vật cũ rồi tính lại
            self.luu(is_tatca = True)
            self._idnguoichoi = idnguoichoi
            self._datlaimau()
            self.phien = _oxuatphat()

        now = time.time()
        if self._thoidiemmautruoc is not None and now - self._thoidiemmautruoc <= KHOANGTRONGTOIDA:
            self._cong("giay", now - self._thoidiemmautruoc)
        self._thoidiemmautruoc = now

        kinhnghiem = moitruong.get_kinhnghiem()
        capdo = moitruong.get_capdonhanvat()
        if kinhnghiem is not None and self._kinhnghiemtruoc is not None and capdo == self._capdotruoc:
            chenh = kinhnghiem - self._kinhnghiemtruoc
            # Lên cấp thì kinh nghiệm bị trừ (bỏ qua, cấp độ đổi); cùng cấp mà giảm là mất do chết...
            self._cong("kinhnghiem" if chenh > 0 else "kinhnghiemmat", abs(chenh))
        self._kinhnghiemtruoc, self._capdotruoc = kinhnghiem, capdo

        nganluong = moitruong.get_nganluong()
        if nganluong is not None and self._nganluongtruoc is not None:
            chenh = nganluong - self._nganluongtruoc
            if chenh:
                self._ghinhanbiendong("", chenh)
        self._nganluongtruoc = nganluong

        is_chet = bool(moitruong.get_is_nhanvatdachet())
        if is_chet and self._is_chettruoc is False:
            self._cong("chet", 1)
        self._is_chettruoc = is_chet

        if now - self._thoidiemdemhanhtrang >= CHUKYDEMHANHTRANG:
            self._thoidiemdemhanhtrang = now
            self._demhanhtrang()

        self._xulychokhop()

        if now - self._thoidiemluugannhat >= CHUKYLUU:
            self.luu()

    def _demhanhtrang(self):
        hanhtrang = self.moitruong.get_soluongvatphamhanhtrangtheoten()
        # Đọc hỏng (hành trang đang nạp lại ra toàn ô trống) thì bỏ lần này, không tính cả túi là mất rồi nhận lại
        if hanhtrang is None or (not hanhtrang and self._hanhtrangtruoc):
            return
        truoc = self._hanhtrangtruoc
        self._hanhtrangtruoc = hanhtrang
        if truoc is None:
            return
        for ten in hanhtrang.keys() | truoc.keys():
            chenh = hanhtrang.get(ten, 0) - truoc.get(ten, 0)
            if chenh:
                self._ghinhanbiendong(ten, chenh)

    def luu(self, is_tatca = False):
        # is_tatca: tắt bot / đổi nhân vật thì ghi luôn các biến động đang chờ so khớp
        with self._khoa:
            if is_tatca:
                self._xulychokhop(is_tatca = True)
            self._thoidiemluugannhat = time.time()
            if not self._idnguoichoi or not self._chualuu:
                return
            chualuu, self._chualuu = self._chualuu, {}
            idnguoichoi = self._idnguoichoi
        with _khoaghi:
            dulieu = taithongke(idnguoichoi)
            for gio, cacos in chualuu.items():
                for khoa, o in cacos.items():
                    _congo(dulieu.setdefault(gio, {}).setdefault(khoa, _oxuatphat()), o)
            mocxoa = time.strftime("%Y-%m-%d %H", time.localtime(time.time() - SONGAYGIULAI * 86400))
            dulieu = {gio: cacos for gio, cacos in dulieu.items() if gio >= mocxoa}
            try:
                os.makedirs(_thumucthongke(), exist_ok = True)
                duongdan = duongdanthongke(idnguoichoi)
                with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
                    json.dump(dulieu, file, ensure_ascii = False)
                os.replace(duongdan + ".tmp", duongdan)
            except OSError as err:
                print(f"[THỐNG KÊ] Lỗi ghi file: {err}")

    def get_tomtatphien(self):
        p = self.phien
        return {"giay": p["giay"], "kinhnghiem": p["kinhnghiem"], "kinhnghiemtieu": p["kinhnghiemmat"],
                "nganluong": p["nganluongthu"], "nganluongtieu": p["nganluongchi"], "chet": p["chet"],
                "nganluongchuyenden": p["nganluongchuyenden"], "nganluongchuyendi": p["nganluongchuyendi"]}
