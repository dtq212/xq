# Săn Tinh Anh: người dùng chọn các bản đồ có quái Tinh Anh (tên vàng, QUAITINHANH_MAP), bot lần lượt tới từng bản đồ (đường đi + phù như
# Mã Tặc), dò khắp bản đồ theo lưới vật cản và chỉ đánh quái Tinh Anh (lấy đồ Lam Kim đốt Phong Yêu Kính). Người chơi / bảo thú PK đánh
# mình thì vẫn phản công như thường. Nhặt đồ, về bán, sửa đồ, phục sinh theo thiết lập sẵn có của nhân vật.
# Mỗi bản đồ:
#   - đi qua các chỗ đã từng thấy Tinh Anh (mọi nhân vật ghi, _internal/vitritinhanh/<ID>.json) trước, rồi các điểm dò phủ vùng đi được
#   - thấy Tinh Anh thì đi tới (chọn mục tiêu / tấn công của bot lo phần đánh, ưu tiên hơn đi dò)
#   - đi hết 1 lượt điểm thì sang bản đồ kế, hết danh sách thì quay lại bản đồ đầu (Tinh Anh hồi sinh lâu nên xoay vòng các bản đồ)
# Chạy tới khi bấm dừng. Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import json
import math
import os
import re
import sys
import time

from hangso_xq import *
from luattuido_xq import MAUTEN
from tienich_xq import phatam

# Đi dò: tới cách điểm chừng này ô là tới, quá THOIGIANMOIDIEMTINHANH giây chưa tới (kẹt / điểm bên kia vách) thì sang điểm kế
KHOANGCACHTOIDIEMTINHANH = 3.
THOIGIANMOIDIEMTINHANH = 25.
# Chỗ thấy Tinh Anh: cách chỗ đã ghi dưới chừng này ô thì coi là cùng chỗ (Tinh Anh đi lang thang quanh điểm xuất hiện)
KHOANGCACHGOPVITRITINHANH = 15.
GIANCACHGHIVITRITINHANH = 3.
# Thấy Tinh Anh mà chừng này giây chưa đánh được (bị chắn, chọn mục tiêu bỏ qua...) thì thôi đi tới con đó, dò tiếp
THOIGIANDUOITINHANHTOIDA = 40.
# Túi đầy lúc săn: về Tân Thủ Thôn cất kho (bảng Cất kho + đồ Lam Kim rơi từ Tinh Anh), không bán rác; cất xong săn tiếp. Cất xong
# chưa tới chừng này giây mà túi vẫn đầy (không có món nào cất được) thì dừng săn, kẻo đi về Tân Thủ Thôn mãi
MAUCATTINHANHs = (MAUTEN["lam kim"],)
THOIGIANCATLAITINHANH = 300.
# Giết được con Tinh Anh của bản đồ (mỗi bản đồ 1 con) mà quanh đó không còn con nào sống: sang bản đồ kế luôn, khỏi dò hết các
# điểm. Trước khi đi chờ nhặt đồ rơi: ít nhất chừng này giây (đồ mới hiện dưới đất), còn đồ đang nhặt thì chờ tới tối đa
THOIGIANCHONHATSAUTINHANH = 3.
THOIGIANCHONHATSAUTINHANHTOIDA = 20.
# Bản đồ không có đường / không đọc được lưới chừng này lần liền thì bỏ bản đồ đó khỏi lượt này
SOLANLOIBANDOTINHANH = 3


def _thumucvitritinhanh():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "vitritinhanh")


def taivitritinhanh(idbando):
    # Gộp chỗ từng thấy Tinh Anh trên bản đồ của mọi nhân vật -> [(x, y), ...] (bỏ chỗ trùng)
    diems = []
    try:
        tenfiles = os.listdir(_thumucvitritinhanh())
    except FileNotFoundError:
        return diems
    for tenfile in tenfiles:
        if not tenfile.endswith(".json"):
            continue
        try:
            with open(os.path.join(_thumucvitritinhanh(), tenfile), "r", encoding = "utf-8") as file:
                bang = json.load(file)
        except Exception:
            continue
        for x, y in bang.get(str(idbando), []):
            if all(math.dist((x, y), d) >= KHOANGCACHGOPVITRITINHANH for d in diems):
                diems.append((int(x), int(y)))
    return diems


def tachbandotinhanh(chuoi):
    # "71, 72, 528" -> [71, 72, 528] (chỉ bản đồ có trong QUAITINHANH_MAP, bỏ trùng, giữ thứ tự)
    ids = []
    for so in re.findall(r"\d+", str(chuoi or "")):
        idbando = int(so)
        if idbando in QUAITINHANH_MAP and idbando not in ids:
            ids.append(idbando)
    return ids


class TacTuTinhAnh:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_tinhanh(self):
        if self._tinhanh:
            return
        self._tinhanh = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "ibando": 0, "do": None, "sovong": 0,
                         "sogiet": 0, "idsong": set(), "iddachet": set(), "lucghi": 0., "duoi": None, "dabatdanh": False}
        self._logta(f"Bắt đầu săn Tinh Anh ở: {self._motabandotinhanh() or '(chưa chọn bản đồ)'}")
        # Tự đi một mình: Theo sau đang bật thì bot bị kéo về người được theo sau; tạm tắt, dừng thì trả lại
        self._doituychontinhanh("_is_tudongtheosau", False, "Theo sau")
        phatam("Bắt đầu săn tinh anh")

    def huy_tinhanh(self):
        if self._tinhanh:
            self._ketthuctinhanh("Đã dừng săn Tinh Anh (bấm tay)")

    def thietlap_bandotinhanh(self, chuoi):
        self._tinhanh_bandos = tachbandotinhanh(chuoi)
        self._logta(f"Bản đồ: {self._motabandotinhanh() or '(trống)'}")
        if self._tinhanh:
            self._tinhanh.update(ibando = 0, do = None, duoi = None)

    def get_is_dangtinhanh(self):
        return bool(self._tinhanh)

    def _is_tinhanhdangchay(self):
        # Săn Tinh Anh đứng sau Lăng Ly Sơn / Sư Gia / Mã Tặc... trong vòng di chuyển: việc đó đang chạy thì _xulytinhanh không được gọi,
        # "chedo" đứng yên ở giá trị cũ. 16/11 Ngốc đang đi Lăng Ly Sơn lỡ bật Săn Tinh Anh -> chedo kẹt "dichuyen" -> không chọn mục
        # tiêu suốt 15 phút. Chỉ tính khi _xulytinhanh mới được gọi gần đây
        return bool(self._tinhanh) and time.time() - self._tinhanh.get("lucxuly", 0.) < 2.

    def get_is_tinhanhdichuyen(self):
        # Đang đi tới bản đồ chọn: không chọn quái dọc đường
        return self._is_tinhanhdangchay() and self._tinhanh["chedo"] == "dichuyen"

    def get_is_tinhanhdanhquai(self):
        # Đang ở bản đồ chọn đi dò: chỉ đánh Tinh Anh, không giới hạn theo lộ trình điểm đánh của nhân vật
        return self._is_tinhanhdangchay() and self._tinhanh["chedo"] == "danhquai"

    def _is_loctinhanh(self):
        # Chỉ chọn quái Tinh Anh: ô "Chỉ đánh mục tiêu tên màu vàng" hoặc đang săn Tinh Anh ở bản đồ chọn
        return self._is_chidanhtinhanh or self.get_is_tinhanhdanhquai()

    def _is_doituongtinhanh(self, diachi, ten = None):
        # Quái Tinh Anh theo tên hoặc theo cấp so với bản đồ đang đứng (hangso is_quaitinhanh). Phó bản mượn ID bản đồ (Phong Yêu Kính)
        # thì không xét cấp: quái trong đó cấp không theo bản đồ thật
        moitruong = self.moitruong
        ten = ten or moitruong.get_tendoituong(diachi)
        if is_quaitinhanh(ten):
            return True
        idbando = moitruong.get_idbandohientai() if moitruong.get_is_phobanmuonbando() is False else None
        return is_quaitinhanh(ten, idbando, laycaptrongten(moitruong._get_tenthucte(diachi)))

    def get_trangthaitinhanh(self):
        if self._tinhanh:
            return f"Săn Tinh Anh (giết {self._tinhanh['sogiet']} con, {self._tinhanh['sovong']} vòng): {self._tinhanh['trangthai']}"
        return self._ketquatinhanh or ""

    def _motabandotinhanh(self):
        return ", ".join(f"{laytenbando(i) or i}" for i in self._tinhanh_bandos)

    def _logta(self, noidung):
        self.moitruong._inlog(f"[TINH ANH] {noidung}")

    def _doituychontinhanh(self, thuoctinh, giatri, ten):
        # Đổi 1 ô thiết lập trong lúc săn, nhớ giá trị cũ để trả lại khi dừng (luuthietlap lưu giá trị cũ này)
        s = self._tinhanh
        if s is not None and getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self._logta(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng săn thì trả lại)")

    def _ketthuctinhanh(self, thongbao):
        s = self._tinhanh
        self._tinhanh = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if s and s["sogiet"]:
            thongbao += f" (giết {s['sogiet']} con)"
        self._logta(thongbao)
        self._ketquatinhanh = f"{time.strftime('%H:%M')} {thongbao}"
        phatam("Kết thúc săn tinh anh")

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulytinhanh(self):
        # Gọi thay lộ trình điểm đánh khi đang săn Tinh Anh -> yêu cầu di chuyển hoặc None
        s = self._tinhanh
        moitruong = self.moitruong
        s["lucxuly"] = time.time()
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logta(s["trangthai"])
        bandos = [b for b in self._tinhanh_bandos if b in QUAITINHANH_MAP]
        if not bandos:
            s["chedo"] = "dichuyen"
            s["trangthai"] = "chưa chọn bản đồ: bấm \"Chọn bản đồ\" ở tab Chiến đấu"
            return None
        if moitruong.get_is_nhanvatdachet() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0 or moitruong.get_is_dangvankhi():
            return None
        if time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        if moitruong.get_is_dayhanhtrang():
            if self._catkho:
                return None
            if time.time() - s.get("luccatkho", 0.) < THOIGIANCATLAITINHANH:
                self._ketthuctinhanh("Túi đầy mà về cất kho không bớt được món nào (thêm luật ở bảng Cất kho / dọn túi)")
                return None
            s["luccatkho"] = time.time()
            s["trangthai"] = "túi đầy: về Tân Thủ Thôn cất kho"
            self._logta("Túi đầy: về Tân Thủ Thôn cất kho (bảng Cất kho + đồ Lam Kim), xong săn tiếp")
            # Việc "Cất kho ngay" (tactu_catkho_xq): vòng di chuyển xét nó trước Săn Tinh Anh, cất xong thì đây tự đi lại bản đồ đang săn
            self.yeucau_catkho()
            if self._catkho:
                self._catkho["mamaus"] = MAUCATTINHANHs
            return None
        idbando = moitruong.get_idbandohientai()
        # Lúc bắt đầu (bấm Bắt đầu / mở lại bot) mà đang đứng ở 1 bản đồ trong danh sách: dò luôn bản đồ đó trước. Chỉ xét 1 lần, kẻo dò
        # xong bản đồ này chuyển sang bản đồ kế lại bị kéo về đây mãi
        if not s.get("daxetbatdau"):
            s["daxetbatdau"] = True
            if idbando in bandos:
                s["ibando"] = bandos.index(idbando)
        s["ibando"] %= len(bandos)
        bandodich = bandos[s["ibando"]]
        if idbando != bandodich:
            s["chedo"] = "dichuyen"
            s["trangthai"] = f"tới {laytenbando(bandodich)} săn {self._tentinhanhbando(bandodich)}"
            buoc = self._lapbuocditoibando(bandodich, is_hoithanhphu = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                self._logta(f"Không có đường tới {laytenbando(bandodich)}: {buoc['mota']}, sang bản đồ kế")
                self._sangbandoketinhanh(s, bandos)
                return None
            return self._thuchienbuocditoibando(buoc, bandodich, None, f"[TINH ANH] Tới {laytenbando(bandodich)}")

        s["chedo"] = "danhquai"
        self._batdanhquaitinhanh(s)
        tinhanhs = self._timtinhanhxungquanh(s, idbando)
        # Thấy Tinh Anh còn sống (chưa bị bot đánh dấu lỗi): đi tới nó, chọn mục tiêu / tấn công của bot lo phần đánh (ưu tiên hơn đi dò)
        # s["duoi"]: id -> lúc bắt đầu đi tới con đó (mỗi con tính riêng, kẻo 2 con không tới được thay nhau đặt lại giờ)
        duoi = s["duoi"] = {i: luc for i, luc in (s["duoi"] or {}).items() if any(i == t[1] for t in tinhanhs)}
        for khoangcach, iddoituong, x, y, ten in tinhanhs:
            if iddoituong in self._idmuctieubiloi_map:
                continue
            if time.time() - duoi.setdefault(iddoituong, time.time()) > THOIGIANDUOITINHANHTOIDA:
                continue
            s["trangthai"] = f"đánh {ten} ở {laytenbando(idbando)} ({x}, {y})"
            self._capnhatbuocdichuyen(f"Săn Tinh Anh: tới {ten} ({x}, {y})")
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 2.}
        # Mỗi bản đồ chỉ có 1 con Tinh Anh (người dùng 16/11, ~30 phút mới mọc lại): giết được 1 con là sang bản đồ kế, cứ quay vòng
        if not tinhanhs and s.get("bandogiet") == idbando and s.get("loaidagiet"):
            chuagiet = time.time() - s["lucgiet"]
            if chuagiet < THOIGIANCHONHATSAUTINHANH or (self._yeucaunhatvatpham and chuagiet < THOIGIANCHONHATSAUTINHANHTOIDA):
                s["trangthai"] = f"đã giết hết {self._tentinhanhbando(idbando)} ở {laytenbando(idbando)}: chờ nhặt đồ"
                return None
            self._logta(f"Đã giết hết {self._tentinhanhbando(idbando)} ở {laytenbando(idbando)}, sang bản đồ kế")
            self._sangbandoketinhanh(s, bandos)
            return None
        yeucau, is_hetluot = self._ditheodiemtinhanh(s, idbando, f"dò {laytenbando(idbando)} tìm {self._tentinhanhbando(idbando)}")
        if is_hetluot:
            self._logta(f"Dò hết {laytenbando(idbando)}, sang bản đồ kế")
            self._sangbandoketinhanh(s, bandos)
            return None
        return yeucau

    def _sangbandoketinhanh(self, s, bandos):
        s["ibando"] = (s["ibando"] + 1) % len(bandos)
        s["do"] = None
        s["duoi"] = None
        s["bandogiet"] = None
        if s["ibando"] == 0:
            s["sovong"] += 1

    def _tentinhanhbando(self, idbando):
        # Tên trong bảng chỉ là 1 biến thể (quái nào của bản đồ cũng có thể ra Tinh Anh): hiện theo cấp
        cap = CAPTINHANH_MAP.get(idbando)
        return f"Tinh Anh (cấp {cap[0]}~{cap[1]})" if cap else "Tinh Anh"

    def _batdanhquaitinhanh(self, s):
        # Ô cần cho đánh quái người dùng quên bật (hoặc đang "Chỉ đánh người chơi") thì đổi giúp, dừng thì trả lại
        if s["dabatdanh"]:
            return
        s["dabatdanh"] = True
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            self._doituychontinhanh(thuoctinh, giatri, ten)

    def _timtinhanhxungquanh(self, s, idbando):
        # Tinh Anh trong tầm nhìn -> [(khoảng cách, id, x, y, tên), ...] con còn sống, gần trước. Đồng thời: đếm con đã chết (từng thấy
        # sống), ghi chỗ thấy Tinh Anh cho lần sau
        moitruong = self.moitruong
        toado = moitruong.get_toado()
        songs, vitris = [], []
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi) or moitruong.get_is_npc(diachi):
                continue
            ten = moitruong.get_tendoituong(diachi)
            if not self._is_doituongtinhanh(diachi, ten):
                self._ghinghitinhanh(s, idbando, diachi, ten)
                continue
            iddoituong = moitruong.get_iddoituong(diachi)
            x, y = moitruong.get_toado(diachi)
            if moitruong.get_is_nhanvatdachet(diachi):
                if iddoituong in s["idsong"] and iddoituong not in s["iddachet"]:
                    s["iddachet"].add(iddoituong)
                    s["sogiet"] += 1
                    # Loại đã giết ở bản đồ đang dò (đổi bản đồ thì tính lại) -> đủ loại thì sang bản đồ kế (_xulytinhanh)
                    if s.get("bandogiet") != idbando:
                        s["bandogiet"], s["loaidagiet"] = idbando, set()
                    s["loaidagiet"].add(ten.split("(")[0].strip().replace("Thuỷ", "Thủy"))
                    s["lucgiet"] = time.time()
                    self._logta(f"Đã giết {ten} ở {laytenbando(idbando)} ({x}, {y}): tổng {s['sogiet']} con")
                continue
            if not moitruong.get_is_cothetancong(diachi):
                continue
            s["idsong"].add(iddoituong)
            vitris.append((int(x), int(y)))
            songs.append((math.dist(toado, (x, y)), iddoituong, int(x), int(y), ten))
        # Id cũ chất đống cả phiên: giữ gọn
        if len(s["idsong"]) > 2000:
            s["idsong"] = set(i for _, i, _, _, _ in songs)
            s["iddachet"].clear()
        if vitris and time.time() - s["lucghi"] > GIANCACHGHIVITRITINHANH:
            s["lucghi"] = time.time()
            self._ghivitritinhanh(idbando, vitris)
        return sorted(songs)

    def _ghinghitinhanh(self, s, idbando, diachi, ten):
        # Sợ bỏ sót Tinh Anh khi mô tả bản đồ (tips) ghi sai khoảng cấp (Bành Thành tips sai tên): quái ở bản đồ đang săn cấp CAO hơn khoảng
        # Tinh Anh thì không đánh (người dùng: cấp Tinh Anh đúng như mô tả) nhưng ghi log "Nghi Tinh Anh" mỗi tên + cấp 1 lần để đối chiếu
        khoang = CAPTINHANH_MAP.get(idbando)
        if not khoang or not ten or ten in TENKHONGPHAITINHANHs or "Bảo Bảo" in ten or "Quốc Kính" in ten or "Tàn Phách" in ten:
            return
        cap = laycaptrongten(self.moitruong._get_tenthucte(diachi))
        if cap is None or cap <= khoang[1]:
            return
        danghi = s.setdefault("danghi", set())
        if (idbando, ten, cap) in danghi:
            return
        danghi.add((idbando, ten, cap))
        x, y = self.moitruong.get_toado(diachi)
        self._logta(f"Nghi Tinh Anh: {ten} cấp {cap} ở {laytenbando(idbando)} ({x}, {y}), cao hơn khoảng cấp mô tả {khoang[0]}~{khoang[1]} "
                    f"nên không đánh. Đúng là tên vàng thì sửa QUAITINHANH_MAP")

    def _ghivitritinhanh(self, idbando, vitris):
        idnguoichoi = self.moitruong.get_idnguoichoi()
        if not idnguoichoi:
            return
        # Phó bản mượn ID bản đồ ngoài (Phong Yêu Kính...): quái trong đó không có ở bản đồ thật, không ghi
        if self.moitruong.get_is_phobanmuonbando() is not False:
            return
        duongdan = os.path.join(_thumucvitritinhanh(), f"{idnguoichoi}.json")
        try:
            with open(duongdan, "r", encoding = "utf-8") as file:
                bang = json.load(file)
        except Exception:
            bang = {}
        diems = bang.setdefault(str(idbando), [])
        is_doi = False
        for x, y in vitris:
            if all(math.dist((x, y), d) >= KHOANGCACHGOPVITRITINHANH for d in diems):
                diems.append([x, y])
                is_doi = True
                self._logta(f"Ghi chỗ thấy Tinh Anh {laytenbando(idbando)} ({x}, {y})")
        if not is_doi:
            return
        try:
            from tienich_xq import thaythefile
            os.makedirs(os.path.dirname(duongdan), exist_ok = True)
            with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
                json.dump(bang, file, separators = (",", ":"))
            thaythefile(duongdan + ".tmp", duongdan)
        except Exception as err:
            self._logta(f"Lỗi ghi chỗ Tinh Anh: {err}")
        # Điểm dò đang đi của bản đồ này chưa có chỗ mới: thêm vào cuối lượt
        do = self._tinhanh and self._tinhanh["do"]
        if do and do["idbando"] == idbando:
            for x, y in vitris:
                if all(math.dist((x, y), d) >= KHOANGCACHGOPVITRITINHANH for d in do["diems"]):
                    do["diems"].append((x, y))

    def _ditheodiemtinhanh(self, s, idbando, nhan):
        # Đi lần lượt chỗ từng thấy Tinh Anh rồi các điểm dò phủ vùng đi được (lưới vật cản, _taodiemdo).
        # -> (yêu cầu di chuyển, đã đi hết 1 lượt các điểm)
        moitruong = self.moitruong
        do = s["do"]
        if not do or do["idbando"] != idbando:
            toado = moitruong.get_toado()
            vitris = taivitritinhanh(idbando)
            dos = list(self._taodiemdo(idbando))
            if not dos and not vitris:
                s["trangthai"] = f"{nhan}: chưa đọc được bản đồ"
                s["solanloi"] = s.get("solanloi", 0) + 1
                if s["solanloi"] >= SOLANLOIBANDOTINHANH:
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
            dos = [d for d in dos if all(math.dist(d, v) >= KHOANGCACHGOPVITRITINHANH for v in vitris)]
            if dos:
                i = min(range(len(dos)), key = lambda k: math.dist(dos[k], vitrihientai))
                diems += dos[i:] + dos[:i]
            do = s["do"] = {"idbando": idbando, "diems": diems, "i": 0, "luc": time.time()}
            self._logta(f"{laytenbando(idbando)}: {len(vitris)} chỗ từng thấy Tinh Anh + {len(dos)} điểm dò")
        x, y = do["diems"][do["i"]]
        if moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIDIEMTINHANH or time.time() - do["luc"] > THOIGIANMOIDIEMTINHANH:
            do["i"] += 1
            do["luc"] = time.time()
            if do["i"] >= len(do["diems"]):
                return None, True
            x, y = do["diems"][do["i"]]
        s["trangthai"] = f"{nhan} (điểm {do['i'] + 1}/{len(do['diems'])})"
        self._capnhatbuocdichuyen(f"Săn Tinh Anh: {nhan} (điểm {do['i'] + 1}/{len(do['diems'])})")
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1., "is_dioo": False}, False
