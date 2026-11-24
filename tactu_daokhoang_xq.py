# Đào khoáng theo bản đồ (như Săn Tinh Anh): người dùng chọn các bản đồ, bot lần lượt tới từng bản đồ (đường đi + phù như Săn Tinh Anh),
# dò khắp bản đồ theo lưới vật cản; thấy khoáng / dược thì phần "Tự động khai khoáng/Hái dược" sẵn có (tactu_hoatdong_xq
# action_tudongkhaikhoang, loại theo pháp bảo đang đeo: Cuốc = khoáng, Liềm = dược) đi tới đào. Đánh quái, nhặt đồ, phục sinh theo
# thiết lập sẵn có của nhân vật.
# Mỗi bản đồ:
#   - đi qua các chỗ đã từng thấy khoáng (mọi nhân vật ghi, _internal/vitrikhoang/<ID>.json) trước, rồi các điểm dò phủ vùng đi được
#   - đi hết 1 lượt điểm thì sang bản đồ kế, hết danh sách thì quay lại bản đồ đầu (khoáng mọc lại)
# Chạy tới khi bấm dừng. Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import json
import math
import os
import re
import sys
import time

from bando_xq import BANDOCONG_MAP, laycapquaibando
from hangso_xq import *
from tienich_xq import phatam

# Đi dò: tới cách điểm chừng này ô là tới, quá THOIGIANMOIDIEMDAOKHOANG giây chưa tới (kẹt / điểm bên kia vách) thì sang điểm kế.
# Đang đào / đi tới khoáng thì đồng hồ dừng
KHOANGCACHTOIDIEMDAOKHOANG = 3.
THOIGIANMOIDIEMDAOKHOANG = 25.
# Chỗ thấy khoáng: cách chỗ đã ghi dưới chừng này ô thì coi là cùng chỗ (khoáng mọc thành cụm quanh 1 điểm)
KHOANGCACHGOPVITRIKHOANG = 10.
GIANCACHGHIVITRIKHOANG = 3.
# Túi đầy: bật "Tự động về bán rác" thì để quy trình bán rác (+ cất kho sau bán) lo; không bật thì "Cất kho ngay" theo bảng Cất kho.
# Cất xong chưa tới chừng này giây mà túi vẫn đầy (không có món nào cất được) thì dừng, kẻo đi về mãi
THOIGIANCATLAIDAOKHOANG = 300.
# Bản đồ không đọc được lưới chừng này lần liền thì bỏ bản đồ đó khỏi lượt này
SOLANLOIBANDODAOKHOANG = 3


def _thumucvitrikhoang():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "vitrikhoang")


def taivitrikhoang(idbando = None):
    # Gộp chỗ từng thấy khoáng của mọi nhân vật. idbando: -> [(x, y), ...] của bản đồ đó; None: -> {id bản đồ: [(x, y), ...]} mọi bản đồ
    # (giao diện chọn bản đồ đếm số chỗ)
    bangs = {}
    try:
        tenfiles = os.listdir(_thumucvitrikhoang())
    except FileNotFoundError:
        tenfiles = []
    for tenfile in tenfiles:
        if not tenfile.endswith(".json"):
            continue
        try:
            with open(os.path.join(_thumucvitrikhoang(), tenfile), "r", encoding = "utf-8") as file:
                bang = json.load(file)
        except Exception:
            continue
        for khoa, toados in bang.items():
            if idbando is not None and khoa != str(idbando):
                continue
            try:
                diems = bangs.setdefault(int(khoa), [])
            except ValueError:
                continue
            for x, y in toados:
                if all(math.dist((x, y), d) >= KHOANGCACHGOPVITRIKHOANG for d in diems):
                    diems.append((int(x), int(y)))
    if idbando is not None:
        return bangs.get(int(idbando), [])
    return bangs


def thutubandodaokhoang(idbando):
    # Khoá xếp thứ tự đi: cấp quái của bản đồ tăng dần (bản đồ nối nhau chạy 1 mạch), không biết cấp thì cuối, cùng cấp thì id tăng dần
    cap = laycapquaibando(idbando)
    return (cap is None, cap or (0, 0), idbando)


def tachbandodaokhoang(chuoi):
    # "71, 528, 263" / [71, 528] -> [71, 528, 263] (chỉ bản đồ có trong BANDOCONG_MAP, bỏ trùng), xếp theo thutubandodaokhoang
    ids = []
    for so in re.findall(r"\d+", str(chuoi or "")):
        idbando = int(so)
        if idbando in BANDOCONG_MAP and idbando not in ids:
            ids.append(idbando)
    return sorted(ids, key = thutubandodaokhoang)


class TacTuDaoKhoang:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_daokhoang(self):
        if self._daokhoang:
            return
        self._daokhoang = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "ibando": 0, "do": None, "sovong": 0,
                           "lucghi": 0., "sokhoang": 0, "iddathay": set()}
        self._logdk(f"Bắt đầu đào khoáng ở: {self._motabandodaokhoang() or '(chưa chọn bản đồ)'}")
        # Tự đi một mình: Theo sau đang bật thì bot bị kéo về người được theo sau; tạm tắt, dừng thì trả lại
        self._doituychondaokhoang("_is_tudongtheosau", False, "Theo sau")
        # Phần đi tới khoáng / look / vận khí là của "Tự động khai khoáng/Hái dược"
        self._doituychondaokhoang("_is_tudongkhaikhoang", True, "Tự động khai khoáng/Hái dược")
        phatam("Bắt đầu đào khoáng")

    def huy_daokhoang(self):
        if self._daokhoang:
            self._ketthucdaokhoang("Đã dừng đào khoáng (bấm tay)")

    def thietlap_bandodaokhoang(self, chuoi):
        self._daokhoang_bandos = tachbandodaokhoang(chuoi)
        self._logdk(f"Bản đồ: {self._motabandodaokhoang() or '(trống)'}")
        if self._daokhoang:
            self._daokhoang.update(ibando = 0, do = None)

    def get_is_dangdaokhoang(self):
        return bool(self._daokhoang)

    def _is_daokhoangdangchay(self):
        # Đào khoáng đứng sau các việc khác trong vòng di chuyển (như Săn Tinh Anh): việc khác đang chạy thì _xulydaokhoang không được gọi,
        # "chedo" đứng yên ở giá trị cũ => chỉ tính khi _xulydaokhoang mới được gọi gần đây
        return bool(self._daokhoang) and time.time() - self._daokhoang.get("lucxuly", 0.) < 2.

    def get_is_daokhoangdichuyen(self):
        # Đang đi tới bản đồ chọn: không chọn quái dọc đường
        return self._is_daokhoangdangchay() and self._daokhoang["chedo"] == "dichuyen"

    def get_is_daokhoangdo(self):
        # Đang ở bản đồ chọn đi dò: quái đánh theo thiết lập, không giới hạn theo lộ trình điểm đánh của nhân vật
        return self._is_daokhoangdangchay() and self._daokhoang["chedo"] == "do"

    def get_trangthaidaokhoang(self):
        if self._daokhoang:
            return f"Đào khoáng (thấy {self._daokhoang['sokhoang']} khoáng, {self._daokhoang['sovong']} vòng): {self._daokhoang['trangthai']}"
        return self._ketquadaokhoang or ""

    def _motabandodaokhoang(self):
        return ", ".join(f"{laytenbando(i) or i}" for i in self._daokhoang_bandos)

    def _logdk(self, noidung):
        self.moitruong._inlog(f"[ĐÀO KHOÁNG] {noidung}")

    def _doituychondaokhoang(self, thuoctinh, giatri, ten):
        # Đổi 1 ô thiết lập trong lúc đào, nhớ giá trị cũ để trả lại khi dừng (luuthietlap lưu giá trị cũ này)
        s = self._daokhoang
        if s is not None and getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self._logdk(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng đào khoáng thì trả lại)")

    def _ketthucdaokhoang(self, thongbao):
        s = self._daokhoang
        self._daokhoang = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if s and s["sokhoang"]:
            thongbao += f" (thấy {s['sokhoang']} khoáng)"
        self._logdk(thongbao)
        self._ketquadaokhoang = f"{time.strftime('%H:%M')} {thongbao}"
        phatam("Kết thúc đào khoáng")

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulydaokhoang(self):
        # Gọi thay lộ trình điểm đánh khi đang đào khoáng -> yêu cầu di chuyển hoặc None
        s = self._daokhoang
        moitruong = self.moitruong
        s["lucxuly"] = time.time()
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logdk(s["trangthai"])
        bandos = [b for b in self._daokhoang_bandos if b in BANDOCONG_MAP]
        if not bandos:
            s["chedo"] = "dichuyen"
            s["trangthai"] = "chưa chọn bản đồ: bấm \"Chọn bản đồ…\" ở tab Khác"
            return None
        if moitruong.get_is_nhanvatdachet() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0:
            return None
        if time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        if moitruong.get_is_dayhanhtrang():
            if self._is_tudongvebanrac:
                # Quy trình về bán rác (tactu_vatpham_xq) tự bắt đầu khi túi đầy, xong thì đây đi lại bản đồ đang đào
                s["trangthai"] = "túi đầy: chờ về bán rác"
                return None
            if self._catkho:
                return None
            if time.time() - s.get("luccatkho", 0.) < THOIGIANCATLAIDAOKHOANG:
                self._ketthucdaokhoang("Túi đầy mà cất kho không bớt được món nào (thêm luật ở bảng Cất kho hoặc bật Tự động về bán rác)")
                return None
            s["luccatkho"] = time.time()
            s["trangthai"] = "túi đầy: về Tân Thủ Thôn cất kho (theo bảng Cất kho)"
            self.yeucau_catkho()
            return None
        idbando = moitruong.get_idbandohientai()
        # Lúc bắt đầu mà đang đứng ở 1 bản đồ trong danh sách: dò luôn bản đồ đó trước (chỉ xét 1 lần)
        if not s.get("daxetbatdau"):
            s["daxetbatdau"] = True
            if idbando in bandos:
                s["ibando"] = bandos.index(idbando)
        s["ibando"] %= len(bandos)
        bandodich = bandos[s["ibando"]]
        if idbando != bandodich:
            s["chedo"] = "dichuyen"
            s["trangthai"] = f"tới {laytenbando(bandodich)}"
            buoc = self._lapbuocditoibando(bandodich, is_hoithanhphu = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                self._logdk(f"Không có đường tới {laytenbando(bandodich)}: {buoc['mota']}, sang bản đồ kế")
                self._sangbandokedaokhoang(s, bandos)
                return None
            return self._thuchienbuocditoibando(buoc, bandodich, None, f"[ĐÀO KHOÁNG] Tới {laytenbando(bandodich)}")

        s["chedo"] = "do"
        self._timkhoangxungquanh(s, idbando)
        # Đang đi tới khoáng / đứng đào / vận khí: khai khoáng lo (yêu cầu KHAI KHOÁNG ưu tiên hơn đi dò), dừng đồng hồ điểm dò
        if (self._diachicosokhaikhoang or moitruong.get_is_dangvankhi() or time.time() < self._thoidiemhetgiukhaikhoang):
            if s["do"]:
                s["do"]["luc"] = time.time()
            s["trangthai"] = f"đào khoáng ở {laytenbando(idbando)}"
            return None
        yeucau, is_hetluot = self._ditheodiemdaokhoang(s, idbando, f"dò {laytenbando(idbando)} tìm khoáng")
        if is_hetluot:
            self._logdk(f"Dò hết {laytenbando(idbando)}, sang bản đồ kế")
            self._sangbandokedaokhoang(s, bandos)
            return None
        return yeucau

    def _sangbandokedaokhoang(self, s, bandos):
        s["ibando"] = (s["ibando"] + 1) % len(bandos)
        s["do"] = None
        if s["ibando"] == 0:
            s["sovong"] += 1

    def _timkhoangxungquanh(self, s, idbando):
        # Khoáng / dược (theo loại pháp bảo đang đeo) trong danh sách đối tượng: đếm khoáng mới thấy, ghi chỗ thấy cho lần sau
        moitruong = self.moitruong
        loai = self._get_loaikhaikhoang()
        vitris = []
        i = -1
        while True:
            i += 1
            diachi = moitruong.get_diachicosothongtindoituongx(i)
            if not diachi:
                break
            ten = moitruong.get_tendoituong(diachi)
            if not ten or not self._is_doituongkhaikhoang(ten, loai):
                continue
            iddoituong = moitruong.get_iddoituong(diachi)
            if iddoituong <= 0:
                continue
            x, y = moitruong.get_toado(diachi)
            vitris.append((int(x), int(y)))
            if iddoituong not in s["iddathay"]:
                s["iddathay"].add(iddoituong)
                s["sokhoang"] += 1
        if len(s["iddathay"]) > 2000:
            s["iddathay"].clear()
        if vitris and time.time() - s["lucghi"] > GIANCACHGHIVITRIKHOANG:
            s["lucghi"] = time.time()
            self._ghivitrikhoang(idbando, vitris)

    def _ghivitrikhoang(self, idbando, vitris):
        idnguoichoi = self.moitruong.get_idnguoichoi()
        if not idnguoichoi or self.moitruong.get_is_phobanmuonbando() is not False:
            return
        duongdan = os.path.join(_thumucvitrikhoang(), f"{idnguoichoi}.json")
        try:
            with open(duongdan, "r", encoding = "utf-8") as file:
                bang = json.load(file)
        except Exception:
            bang = {}
        diems = bang.setdefault(str(idbando), [])
        is_doi = False
        for x, y in vitris:
            if all(math.dist((x, y), d) >= KHOANGCACHGOPVITRIKHOANG for d in diems):
                diems.append([x, y])
                is_doi = True
                self._logdk(f"Ghi chỗ thấy khoáng {laytenbando(idbando)} ({x}, {y})")
        if not is_doi:
            return
        try:
            from tienich_xq import thaythefile
            os.makedirs(os.path.dirname(duongdan), exist_ok = True)
            with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
                json.dump(bang, file, separators = (",", ":"))
            thaythefile(duongdan + ".tmp", duongdan)
        except Exception as err:
            self._logdk(f"Lỗi ghi chỗ khoáng: {err}")

    def _ditheodiemdaokhoang(self, s, idbando, nhan):
        # Đi lần lượt chỗ từng thấy khoáng rồi các điểm dò phủ vùng đi được (lưới vật cản, _taodiemdo).
        # -> (yêu cầu di chuyển, đã đi hết 1 lượt các điểm)
        moitruong = self.moitruong
        do = s["do"]
        if not do or do["idbando"] != idbando:
            toado = moitruong.get_toado()
            vitris = taivitrikhoang(idbando)
            dos = list(self._taodiemdo(idbando))
            if not dos and not vitris:
                s["trangthai"] = f"{nhan}: chưa đọc được bản đồ"
                s["solanloi"] = s.get("solanloi", 0) + 1
                if s["solanloi"] >= SOLANLOIBANDODAOKHOANG:
                    s["solanloi"] = 0
                    return None, True
                return None, False
            s["solanloi"] = 0
            # Chỗ từng thấy: gần mình trước rồi lần lượt điểm gần điểm trước; điểm dò giữ thứ tự vòng của dexuatlotrinhdo, bắt đầu từ
            # điểm gần chỗ kết thúc phần chỗ từng thấy
            diems = []
            con = list(vitris)
            vitrihientai = toado
            while con:
                gan = min(con, key = lambda d: math.dist(d, vitrihientai))
                con.remove(gan)
                diems.append(gan)
                vitrihientai = gan
            dos = [d for d in dos if all(math.dist(d, v) >= KHOANGCACHGOPVITRIKHOANG for v in vitris)]
            if dos:
                i = min(range(len(dos)), key = lambda k: math.dist(dos[k], vitrihientai))
                diems += dos[i:] + dos[:i]
            do = s["do"] = {"idbando": idbando, "diems": diems, "i": 0, "luc": time.time()}
            self._logdk(f"{laytenbando(idbando)}: {len(vitris)} chỗ từng thấy khoáng + {len(dos)} điểm dò")
        x, y = do["diems"][do["i"]]
        if moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIDIEMDAOKHOANG or time.time() - do["luc"] > THOIGIANMOIDIEMDAOKHOANG:
            do["i"] += 1
            do["luc"] = time.time()
            if do["i"] >= len(do["diems"]):
                return None, True
            x, y = do["diems"][do["i"]]
        s["trangthai"] = f"{nhan} (điểm {do['i'] + 1}/{len(do['diems'])})"
        self._capnhatbuocdichuyen(f"Đào khoáng: {nhan} (điểm {do['i'] + 1}/{len(do['diems'])})")
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1., "is_dioo": False}, False
