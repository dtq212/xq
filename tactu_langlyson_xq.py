# Tự động đi phó bản Lăng Ly Sơn (bật tay trên giao diện, chạy vòng này sang vòng khác tới khi bấm dừng). Nhân vật bật là trưởng nhóm,
# các thành viên khác bật Theo sau (theo sau tự nói chuyện NPC vào / qua tầng, bando_xq.LOIDINPC_MAP). Mỗi vòng:
#   vào     : chờ có tổ đội và mình là trưởng nhóm (phó bản giữ theo tổ đội), tới Thuý Hoa Sơn (137, 117) nói chuyện Đào Vong Khổ Dịch
#             "1. Tiến vào Lăng Ly Sơn" -> Tầng Trên Lăng Mộ (702)
#   702     : đánh Tướng Quân Dũng (234, 207); Cơ Quan Thạch (234, 207) "1. Khởi động Cơ Quan Thạch", chờ vận khí xong;
#             Cơ Quan Thạch Sư (166, 106) "1. Chuyển đến Tầng tiếp theo" -> Tầng Dưới Lăng Mộ (703)
#   703     : đánh Đường Truy (166, 178), Thế Công Minh (204, 97), Thạch Tướng Quân (204, 97, hiện sau khi Thế Công Minh chết),
#             Hào Quật (140, 51); Lăng Mộ Thạch Sư (137, 59) "1. Tiến vào thư phòng" -> Tổng Giám Công Thư Phòng (704)
#   704     : đánh Cơ Quan Tướng Quân (35, 25)
#   nhận thưởng: Hồi Thành Phù ra (chỉ ở bước này mới cho Hồi Thành Phù trong phó bản), phù tới Thuý Hoa Sơn, Đào Vong Khổ Dịch
#             "1. Lĩnh nhận phần thưởng". Mỗi thành viên phải tự lĩnh: trưởng nhóm lĩnh xong báo mã thưởng qua shared_data, thành viên
#             theo sau (cùng máy) thấy mã mới thì tự tới lĩnh (_xulylanhthuongtheosau) rồi báo lại đã lĩnh
#   đổi nhóm: chờ thành viên cùng máy lĩnh xong (tối đa THOIGIANCHOTHANHVIENLANH giây), tạm tắt Tổ đội tự động ở mọi người cùng máy
#             của vòng đó (không thì nó kéo nhau vào lại nhóm cũ còn giữ phó bản đã xong), ai cũng rời nhóm; hết nhóm cũ thì bật lại cho
#             Tổ đội tự động lập nhóm mới rồi vào vòng sau
# Bật ở thành viên (không phải trưởng nhóm) thì chỉ làm thành viên: Theo sau lo mọi việc
# Bước trong từng tầng nhớ theo bản đồ: chết / rớt ra ngoài thì vào lại (tổ đội còn giữ phó bản) làm tiếp từ bước đang dở.
# Đánh boss: tới gần toạ độ thì đánh mọi quái quanh đó (boss là con gần nhất); đã thấy boss mà THOIGIANBOSSBIENMAT giây không thấy nữa,
# hoặc tới nơi THOIGIANCHOBOSS giây không thấy boss đâu thì coi như đã giết.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import time

from hangso_xq import *
from thongbao_xq import baosuco
from tienich_xq import phatam

BANDO_THUYHOASON = 82
NPCVAOLANGLYSON = ("Đào Vong Khổ Dịch", 137, 117)
# id bản đồ -> các bước trong tầng: ("danh", tên boss, x, y[, True: phải đủ thành viên]) | ("noichuyen", tên NPC, x, y) |
# ("sangtang", id tầng kế) | ("ra",)
BUOCLANGLYSON_MAP = {
    BANDO_LANGLYSON1: (("danh", "Tướng Quân Dũng", 234, 207), ("noichuyen", "Cơ Quan Thạch", 234, 207), ("sangtang", BANDO_LANGLYSON2)),
    BANDO_LANGLYSON2: (("danh", "Đường Truy", 166, 178), ("danh", "Thế Công Minh", 204, 97), ("danh", "Thạch Tướng Quân", 204, 97),
                       ("danh", "Hào Quật", 140, 51), ("sangtang", BANDO_LANGLYSON3)),
    # Boss cuối: thành viên nào không có mặt (bị dis, chưa vào tới) lúc boss chết thì không được nhận thưởng => chờ đủ người
    BANDO_LANGLYSON3: (("danh", "Cơ Quan Tướng Quân", 35, 25, True), ("ra",)),
}
# Chờ đủ thành viên trước boss cuối: thành viên (mọi người từng ở trong nhóm vòng này) phải còn trong nhóm, còn sống và đứng cách mình
# tối đa KHOANGCACHTHANHVIENGAN ô mới bắt đầu đánh; đã đủ rồi thì chỉ dừng lại khi có người rời nhóm / không còn thấy trên bản đồ
# (theo sau tụt lại vài ô không tính). Thành viên rời nhóm thì GIANCACHMOILAI giây mời lại 1 lần; chờ quá THOIGIANBAOCHOTHANHVIEN giây thì báo
KHOANGCACHTHANHVIENGAN = 10.
GIANCACHMOILAI = 10.
THOIGIANBAOCHOTHANHVIEN = 180.
# Cách toạ độ boss chừng này ô thì coi như tới nơi, bắt đầu đánh mọi quái quanh đó
KHOANGCACHTOIBOSS = 6.
THOIGIANCHOBOSS = 30.
THOIGIANBOSSBIENMAT = 3.
# Giết xong boss cuối chờ chừng này giây (nhặt đồ) rồi mới Hồi Thành Phù ra
THOIGIANCHORA = 8.
# Boss cuối đã chết mà chưa đọc được tin "hoàn thành phó bản" (tin có thể không vào khung trò chuyện): chờ tối đa chừng này giây rồi mới ra
THOIGIANCHOTINHOANTHANH = 15.
# Nói chuyện NPC trong phó bản: chờ menu, chọn rồi chờ vận khí bắt đầu tối đa chừng này giây, không thì nói lại; quá SOLANTHUNOICHUYEN
# lần thì quay lại bước trước (boss trước đó có thể chưa chết)
KHOANGCACHNOICHUYENLLS = 3.
THOIGIANCHOMENULLS = 3.
THOIGIANCHOVANKHILLS = 5.
SOLANTHUNOICHUYEN = 3
GIANCACHROINHOM = 5.
# Trưởng nhóm lĩnh xong chờ thành viên cùng máy tự lĩnh tối đa chừng này giây rồi mới giải tán tổ đội
THOIGIANCHOTHANHVIENLANH = 120.
# Giải tán tổ đội cũ: tạm tắt Tổ đội tự động ở mọi người, chờ hết người trong nhóm cũ tối đa chừng này giây rồi bật lại
THOIGIANCHOGIAITAN = 30.
# Mỗi vòng quá chừng này giây chưa xong thì báo (vẫn chạy tiếp)
THOIGIANVONGTOIDA = 40 * 60.


class TacTuLangLySon:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_langlyson(self):
        if self._langlyson:
            return
        self._langlyson = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "giaidoan": "vao", "buoc": {},
                           "hoithoai": None, "boss": None, "lucbatdauvong": time.time(), "sovong": 0, "dabao": set(),
                           "thanhviens": {}, "dudoi": False, "lucchodoi": 0., "lucmoi": {}, "diemvao": {}, "daxongphoban": False,
                           "tindaghi": set()}
        self.moitruong._inlog("[LĂNG LY SƠN] Bắt đầu tự động đi Lăng Ly Sơn")
        phatam("Bắt đầu Lăng Ly Sơn")

    def huy_langlyson(self):
        if self._langlyson:
            self._ketthuclanglyson("Đã dừng Lăng Ly Sơn (bấm tay)")

    def get_is_danglanglyson(self):
        return bool(self._langlyson)

    def get_is_langlysondichuyen(self):
        # Đang tự lo đi lại / nói chuyện NPC / chờ thành viên: không chọn quái, đi trước đánh / nhặt
        return bool(self._langlyson) and self._langlyson["chedo"] in ("dichuyen", "cho")

    def get_is_langlysonchothanhvien(self):
        # Trưởng nhóm đang chờ đủ thành viên trước boss cuối: báo qua shared_data để thành viên theo sau cũng không đánh
        # (theo mốc bắt đầu chờ chứ không theo chedo: chedo mỗi lượt đặt lại từ đầu, thành viên đọc giữa chừng không bị chập chờn)
        return bool(self._langlyson) and bool(self._langlyson["lucchodoi"])

    def get_dsidgiunhomlanglyson(self):
        # Vòng đang đi dở (đã vào phó bản, chưa lĩnh thưởng xong / chưa bắt đầu giải tán): ID mình và thành viên vòng này, báo qua
        # shared_data để Tổ đội tự động của ai cũng không rời nhóm / nhường quyền (rời giữa chừng là mất phó bản). Không thì []
        s = self._langlyson
        if not s or s["chedo"] == "thanhvien":
            return []
        is_dangdi = (s["giaidoan"] == "vao" and (s["thanhviens"] or self.moitruong.get_idbandohientai() in BUOCLANGLYSON_MAP)) \
            or s["giaidoan"] == "nhanthuong" or (s["giaidoan"] == "doinhom" and not s.get("tattodoi") and not s["is_daroinhom"])
        return [self.moitruong.get_idnguoichoi(), *s["thanhviens"]] if is_dangdi else []

    def _is_trongdanhsachcuasokhac(self, khoa):
        # ID mình có trong danh sách khoa (list ID) mà cửa sổ khác cùng máy đang báo (còn cập nhật)
        if self.shared_data is None:
            return False
        idtoi = self.moitruong.get_idnguoichoi()
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return False
        return any(idcuaso != self.idcuaso and isinstance(info, dict) and time.time() - info.get("thoidiemcapnhat", 0.) <= 5.
                   and idtoi in (info.get(khoa) or ()) for idcuaso, info in danhsach)

    def get_is_giunhomlanglyson(self):
        # Tổ đội tự động không được rời nhóm / nhường quyền trưởng nhóm (xem get_dsidgiunhomlanglyson). Gọi mỗi lượt chọn mục tiêu nên nhớ
        # kết quả đọc shared_data 0.5s
        if self.get_dsidgiunhomlanglyson():
            return True
        thoidiem, ketqua = self._bonhogiunhomlanglyson
        if time.time() - thoidiem > 0.5:
            ketqua = self._is_trongdanhsachcuasokhac("_langlysongiunhom")
            self._bonhogiunhomlanglyson = (time.time(), ketqua)
        return ketqua

    def get_is_camdanhlanglyson(self):
        # Không được đánh lúc này:
        #   - đang ở chế độ Lăng Ly Sơn (mình bật, người mình theo sau bật, hoặc mình là thành viên vòng đang đi) mà ở ngoài 3 tầng phó bản:
        #     không đánh quái dọc đường / ở Thuý Hoa Sơn (đỡ chạy linh tinh)
        #   - chính mình đang chờ thành viên, hoặc người mình theo sau (trưởng nhóm cùng máy) đang chờ và mình cũng ở tầng đó
        # Đang đánh thường ("kill") thì ngắt luôn (máy chủ giữ lệnh đánh cả khi bỏ chọn mục tiêu)
        idbando = self.moitruong.get_idbandohientai()
        info = self._laythongtinmuctieutheosaucuasokhac() if self._is_tudongtheosau else None
        if idbando not in BUOCLANGLYSON_MAP:
            is_cam = bool(self._langlyson) or bool(info and info.get("_is_danglanglyson")) or self.get_is_giunhomlanglyson()
        elif self.get_is_langlysonchothanhvien():
            is_cam = True
        else:
            is_cam = bool(info and info.get("_langlysonchothanhvien") and info.get("tenbando") == idbando)
        if is_cam and self._is_battudongtancongvatly and self._diachimuctieutancongvatly:
            self._ngattancongvatlydaohoa(self._diachimuctieutancongvatly)
        return is_cam

    def get_is_langlysondanhquai(self):
        # Đang ở chỗ boss: đánh mọi quái quanh đó, không giới hạn theo danh sách tên / điểm đánh của nhân vật
        return bool(self._langlyson) and self._langlyson["chedo"] == "danhquai"

    def get_trangthailanglyson(self):
        if self._langlyson:
            return f"Lăng Ly Sơn (xong {self._langlyson['sovong']} vòng): {self._langlyson['trangthai']}"
        return self._ketqualanglyson or ""

    def _ketthuclanglyson(self, thongbao):
        s = self._langlyson
        self._langlyson = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if s and s["sovong"]:
            thongbao += f" (xong {s['sovong']} vòng)"
        self.moitruong._inlog(f"[LĂNG LY SƠN] {thongbao}")
        self._ketqualanglyson = f"{time.strftime('%H:%M')} {thongbao}"
        phatam("Kết thúc Lăng Ly Sơn")

    def _baolanglyson(self, s, khoa, noidung):
        # Báo Telegram 1 lần cho mỗi việc cần người dùng để ý, bot vẫn chờ / chạy tiếp
        if khoa not in s["dabao"]:
            s["dabao"].add(khoa)
            self.moitruong._inlog(f"[LĂNG LY SƠN] {noidung}")
            baosuco(self.moitruong, "langlyson", noidung, khoa = f"{s['batdau']}|{khoa}", giancach = 0.)

    def _batdanhquailanglyson(self, s):
        # Ô cần cho đánh quái (cùng bộ với sư môn) người dùng quên bật thì đổi giúp, dừng thì trả lại
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            if getattr(self, thuoctinh) != giatri:
                s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
                setattr(self, thuoctinh, giatri)
                self.moitruong._inlog(f"[LĂNG LY SƠN] {'Bật' if giatri else 'Tắt'} \"{ten}\" để đánh boss (dừng thì trả lại)")

    def _doctinphoban(self, s):
        # Tin trò chuyện có "phó bản" ghi log (mỗi câu 1 lần) để biết game báo gì; "hoàn thành phó bản Lăng Ly Sơn" là chắc chắn đã xong
        # (game: "Bạn đã hoàn thành phó bản Lăng Ly Sơn, có thể quay về báo cáo Đào Vong Khổ Dịch để nhận thưởng!")
        for _, noidung in list(self.moitruong.get_lichsutrochuyen5s()):
            thuong = (noidung or "").lower()
            if "phó bản" not in thuong or noidung in s["tindaghi"]:
                continue
            s["tindaghi"].add(noidung)
            self.moitruong._inlog(f"[LĂNG LY SƠN] Tin game: {noidung[:120]!r}")
            if "hoàn thành phó bản" in thuong and "lăng ly sơn" in thuong and not s["daxongphoban"]:
                s["daxongphoban"] = True
                self.moitruong._inlog("[LĂNG LY SƠN] Game báo đã hoàn thành phó bản")

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulylanglyson(self):
        # Gọi thay lộ trình điểm đánh khi đang đi Lăng Ly Sơn -> yêu cầu di chuyển hoặc None
        s = self._langlyson
        moitruong = self.moitruong
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            moitruong._inlog(f"[LĂNG LY SƠN] {s['trangthai']}")
        s["chedo"] = "dichuyen"
        self._doctinphoban(s)
        if moitruong.get_is_nhanvatdachet() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0:
            return None
        if time.time() - s["lucbatdauvong"] > THOIGIANVONGTOIDA:
            self._baolanglyson(s, f"cham|{s['sovong']}", f"⚠️ Lăng Ly Sơn: vòng {s['sovong'] + 1} quá {int(THOIGIANVONGTOIDA // 60)} phút chưa xong "
                                                       f"({s['trangthai']})")
        if moitruong.get_is_dangvankhi():
            # Đang vận khí (vào phó bản / khởi động cơ quan / Hồi Thành Phù): đứng yên, việc nói chuyện dở thì ghi nhận đã thấy vận khí
            if s["hoithoai"]:
                s["hoithoai"]["vankhi"] = True
            return None
        if time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        if s["giaidoan"] == "vao" and moitruong.get_is_dangnamtrongnhom() and not moitruong.get_is_truongnhom():
            # Bật ở thành viên (không phải trưởng nhóm): không tự đánh boss / lĩnh thưởng theo vòng riêng (từng làm cả 4 nhân vật đều tự
            # chạy, tự phát mã thưởng rồi chờ nhau). Theo sau lo đi theo, vào / qua tầng, lĩnh thưởng; trưởng nhóm dis mà mình thành trưởng
            # nhóm thì tự chạy tiếp
            s["chedo"] = "thanhvien"
            s["trangthai"] = "thành viên: đi theo trưởng nhóm" + ("" if self._is_tudongtheosau else " (chưa bật Theo sau!)")
            return None
        if s["giaidoan"] == "nhanthuong":
            return self._buocnhanthuong(s)
        if s["giaidoan"] == "doinhom":
            return self._buocdoinhom(s)
        idbando = moitruong.get_idbandohientai()
        if idbando in BUOCLANGLYSON_MAP:
            self._ghithanhvienvong(s)
            # Chỗ vừa vào tầng: chờ thành viên ở đây (xa boss, người vào sau cũng xuất hiện ở đây)
            s["diemvao"].setdefault(idbando, moitruong.get_toado())
            return self._buoctrongphoban(s, idbando)
        return self._buocvao(s)

    def _ghithanhvienvong(self, s):
        # Mọi người từng ở trong nhóm trong phó bản vòng này (id -> tên): bị dis rớt khỏi nhóm vẫn nhớ để chờ trước boss cuối
        moitruong = self.moitruong
        idtoi = moitruong.get_idnguoichoi()
        for idtv in moitruong.get_danhsachidnguoichoithanhviennhoms() or ():
            if idtv and idtv != idtoi and not s["thanhviens"].get(idtv):
                diachi = moitruong.action_timkiemnhanvat(idnguoichoi = idtv)
                s["thanhviens"][idtv] = (moitruong.get_tendoituong(diachi) if diachi else "") or self._laytencungmay(idtv)

    def _laytencungmay(self, idnguoichoi):
        try:
            for info in list(self.shared_data.values()) if self.shared_data is not None else ():
                if isinstance(info, dict) and info.get("idnguoichoi") == idnguoichoi and info.get("tennhanvat"):
                    return info["tennhanvat"]
        except Exception:
            pass
        return ""

    def _laythanhvienvang(self, s):
        # Thành viên vòng này chưa có mặt cho boss cuối: [(id, tên, lý do)]. Chưa đủ lần nào (dudoi False) thì phải đứng gần; đủ rồi chỉ
        # tính người rời nhóm / không thấy trên bản đồ / đã chết
        moitruong = self.moitruong
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ())
        vangs = []
        for idtv, ten in s["thanhviens"].items():
            ten = ten or self._laytencungmay(idtv) or f"ID {idtv}"
            if idtv not in trongnhoms:
                vangs.append((idtv, ten, "không còn trong nhóm"))
                continue
            diachi = moitruong.action_timkiemnhanvat(idnguoichoi = idtv)
            if not diachi:
                vangs.append((idtv, ten, "chưa thấy ở tầng này"))
            elif moitruong.get_is_nhanvatdachet(diachi):
                vangs.append((idtv, ten, "đã chết"))
            elif not s["dudoi"] and moitruong.get_khoangcach(diachi) > KHOANGCACHTHANHVIENGAN:
                vangs.append((idtv, ten, f"chưa tới gần (cần trong {KHOANGCACHTHANHVIENGAN:.0f} ô)"))
        return vangs

    def _chothanhvien(self, s, idbando, vangs):
        # Đứng ở chỗ vào tầng, không đánh (cả thành viên theo sau: get_is_camdanhlanglyson), mời lại người rời nhóm. -> yêu cầu di chuyển
        moitruong = self.moitruong
        now = time.time()
        if s["chedo"] != "cho":
            s["chedo"] = "cho"
        if not s["lucchodoi"]:
            s["lucchodoi"] = now
            moitruong._inlog(f"[LĂNG LY SƠN] Chờ đủ thành viên trước boss cuối: {', '.join(f'{t} ({l})' for _, t, l in vangs)}")
        self.get_is_camdanhlanglyson()
        moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
        # Bỏ mốc "đã thấy boss": đứng chờ xa không thấy boss không phải là boss đã chết, đủ người thì tới đánh lại từ đầu
        s["boss"] = None
        for idtv, ten, lydo in vangs:
            if lydo == "không còn trong nhóm" and now - s["lucmoi"].get(idtv, 0.) > GIANCACHMOILAI:
                s["lucmoi"][idtv] = now
                moitruong.action_moihoacxinvaonhom(idtv)
        s["trangthai"] = f"{laytenbando(idbando)}: chờ đủ người mới đánh boss cuối (từ {time.strftime('%H:%M', time.localtime(s['lucchodoi']))}): " \
                         + ", ".join(f"{t} {l}" for _, t, l in vangs)
        if now - s["lucchodoi"] > THOIGIANBAOCHOTHANHVIEN:
            self._baolanglyson(s, f"chodoi|{s['sovong']}|{int(s['lucchodoi'])}",
                               f"⚠️ Lăng Ly Sơn: chờ {int(THOIGIANBAOCHOTHANHVIEN // 60)} phút chưa đủ người để đánh boss cuối: "
                               + ", ".join(f"{t} ({l})" for _, t, l in vangs))
        diemvao = s["diemvao"].get(idbando)
        if diemvao and moitruong.get_khoangcachdiem(*diemvao) > 3.:
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (diemvao[0], diemvao[1], idbando), "khoangcachtoida": 1.}
        return None

    def _buocvao(self, s):
        # Ngoài phó bản: có tổ đội và là trưởng nhóm mới vào (phó bản giữ theo tổ đội), rồi tới Đào Vong Khổ Dịch (theo bước Đi tới bản đồ:
        # phù / chạy tới Thuý Hoa Sơn, nói chuyện NPC lối vào)
        moitruong = self.moitruong
        if not moitruong.get_is_dangnamtrongnhom():
            s["trangthai"] = "chờ có tổ đội (bật Tổ đội tự động để bot tự lập nhóm)"
            return None
        if not moitruong.get_is_truongnhom():
            s["trangthai"] = "chờ mình làm trưởng nhóm (người đi phó bản phải là trưởng nhóm, thành viên bật Theo sau)"
            return None
        s["trangthai"] = f"vào Lăng Ly Sơn (vòng {s['sovong'] + 1})"
        buoc = self._lapbuocditoibando(BANDO_LANGLYSON1, is_hoithanhphu = True)
        if buoc["loai"] == "toinoi":
            return None
        return self._thuchienbuocditoibando(buoc, BANDO_LANGLYSON1, None, "[LĂNG LY SƠN] Vào Lăng Ly Sơn")

    def _buoctrongphoban(self, s, idbando):
        buocs = BUOCLANGLYSON_MAP[idbando]
        i = s["buoc"].setdefault(idbando, 0)
        if i >= len(buocs):
            i = s["buoc"][idbando] = len(buocs) - 1
        buoc = buocs[i]
        loai = buoc[0]
        tenbando = laytenbando(idbando)
        if loai == "danh":
            _, tenboss, x, y = buoc[:4]
            if len(buoc) > 4 and buoc[4]:
                vangs = self._laythanhvienvang(s)
                if vangs:
                    s["dudoi"] = False
                    return self._chothanhvien(s, idbando, vangs)
                if not s["dudoi"]:
                    if s["lucchodoi"]:
                        self.moitruong._inlog(f"[LĂNG LY SƠN] Đủ thành viên sau {int(time.time() - s['lucchodoi'])}s, đánh {tenboss}")
                    s.update(dudoi = True, lucchodoi = 0.)
            # Boss cuối (bước có cờ): không "tới nơi lâu không thấy thì coi như đã giết" (ra nhầm là mất phó bản); game báo hoàn thành là xong
            is_bosscuoi = len(buoc) > 4 and buoc[4]
            if is_bosscuoi and s["daxongphoban"]:
                ketqua, yeucau = "game báo hoàn thành phó bản", None
            else:
                ketqua, yeucau = self._danhboss(s, idbando, tenboss, x, y, is_bosscuoi)
            if ketqua:
                self.moitruong._inlog(f"[LĂNG LY SƠN] {tenbando}: xong {tenboss} ({ketqua})")
                self._sangbuoc(s, idbando)
            return yeucau
        if loai == "noichuyen":
            _, tennpc, x, y = buoc
            s["trangthai"] = f"{tenbando}: nói chuyện {tennpc} ({x}, {y})"
            ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y)
            if ketqua == "xong":
                self._sangbuoc(s, idbando)
            elif ketqua == "loi":
                # Nói mãi không vận khí: có thể boss trước đó chưa chết, quay lại bước trước
                self.moitruong._inlog(f"[LĂNG LY SƠN] {tennpc} {SOLANTHUNOICHUYEN} lần không vận khí, quay lại bước trước")
                s["buoc"][idbando] = max(0, i - 1)
                s["boss"] = None
            return yeucau
        if loai == "sangtang":
            idke = buoc[1]
            s["trangthai"] = f"{tenbando}: sang {laytenbando(idke)}"
            ketqua = self._lapbuocditoibando(idke)
            if ketqua["loai"] in ("toinoi", "khongduong"):
                return None
            return self._thuchienbuocditoibando(ketqua, idke, None, f"[LĂNG LY SƠN] {tenbando}")
        # "ra": boss cuối xong, chờ nhặt đồ rồi sang nhận thưởng (Hồi Thành Phù ra khỏi phó bản)
        luc = s.setdefault("lucxongboss", time.time())
        if not s["daxongphoban"] and time.time() - luc < THOIGIANCHOTINHOANTHANH:
            # Thấy boss cuối chết rồi: chờ thêm tin game báo hoàn thành cho chắc (đọc được tin thì đi ngay sau THOIGIANCHORA)
            s["chedo"] = "danhquai"
            s["trangthai"] = f"{tenbando}: boss cuối đã chết, chờ game báo hoàn thành phó bản"
            return None
        if time.time() - luc < THOIGIANCHORA:
            s["chedo"] = "danhquai"
            s["trangthai"] = f"{tenbando}: xong phó bản, chờ nhặt đồ rồi ra nhận thưởng"
            return None
        s.pop("lucxongboss", None)
        s["giaidoan"] = "nhanthuong"
        self.moitruong._inlog("[LĂNG LY SƠN] Xong phó bản, ra Thuý Hoa Sơn nhận thưởng")
        return None

    def _sangbuoc(self, s, idbando):
        s["buoc"][idbando] = s["buoc"].get(idbando, 0) + 1
        s["boss"] = None
        s["hoithoai"] = None

    def _danhboss(self, s, idbando, tenboss, x, y, is_bosscuoi = False):
        # -> (lý do xong hoặc None, yêu cầu di chuyển). is_bosscuoi: chỉ xong khi đã thấy boss rồi boss biến mất, không thấy thì chờ mãi
        # (báo Telegram) chứ không đi ra
        moitruong = self.moitruong
        boss = s["boss"]
        if not boss or boss["ten"] != tenboss:
            boss = s["boss"] = {"ten": tenboss, "luctoi": 0., "lucthay": 0.}
        now = time.time()
        diachi = self._timbosssong(tenboss)
        if diachi:
            boss["lucthay"] = now
        elif boss["lucthay"] and now - boss["lucthay"] > THOIGIANBOSSBIENMAT:
            # Đã thấy boss mà giờ không thấy nữa (kể cả khi đang đứng hơi xa toạ độ: đuổi đánh / bị đẩy ra)
            return "đã giết", None
        if diachi or moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIBOSS:
            # Tới nơi (hoặc thấy boss): đánh mọi quái quanh đó
            boss["luctoi"] = boss["luctoi"] or now
            s["chedo"] = "danhquai"
            self._batdanhquailanglyson(s)
            if not diachi and not boss["lucthay"] and now - boss["luctoi"] > THOIGIANCHOBOSS:
                if not is_bosscuoi:
                    return f"tới nơi {THOIGIANCHOBOSS:.0f}s không thấy, coi như đã giết", None
                self._baolanglyson(s, f"khongthayboss|{s['sovong']}", f"⚠️ Lăng Ly Sơn: tới {tenboss} {THOIGIANCHOBOSS:.0f}s không thấy boss, "
                                                                     f"game cũng chưa báo hoàn thành phó bản: bot đứng chờ, không ra (xem giúp)")
                s["trangthai"] = f"{laytenbando(idbando)}: không thấy {tenboss}, chưa có tin hoàn thành phó bản, đứng chờ (không ra)"
                return None, None
            s["trangthai"] = f"{laytenbando(idbando)}: đánh {tenboss}" + ("" if diachi else " (chờ boss hiện)")
            # Bị đánh dạt ra xa toạ độ boss thì quay về (đánh quái vẫn ưu tiên hơn)
            if moitruong.get_khoangcachdiem(x, y) > KHOANGCACHTOIBOSS and not diachi:
                return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}
            return None, None
        s["trangthai"] = f"{laytenbando(idbando)}: tới đánh {tenboss} ({x}, {y})"
        self._capnhatbuocdichuyen(f"Lăng Ly Sơn: tới {tenboss} ({x}, {y})")
        return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}

    def _timbosssong(self, tenboss):
        moitruong = self.moitruong
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi):
                continue
            if (moitruong.get_tendoituong(diachi) or "").strip() == tenboss and not moitruong.get_is_nhanvatdachet(diachi):
                return diachi
        return None

    def _noichuyenlls(self, s, tennpc, x, y, is_chovankhi = True, kiemtramenu = None):
        # Tới cạnh NPC, "look" mở menu, chọn lựa chọn đầu (trừ CLOSE). is_chovankhi: chọn xong phải thấy vận khí rồi hết vận khí mới là xong
        # (quá THOIGIANCHOVANKHILLS giây chưa vận khí thì nói lại, quá SOLANTHUNOICHUYEN lần -> "loi"); không thì chọn xong là xong.
        # kiemtramenu(lời NPC) False thì không chọn -> "tuchoi". -> (None | "xong" | "loi" | "tuchoi", yêu cầu di chuyển)
        moitruong = self.moitruong
        idbando = moitruong.get_idbandohientai()
        now = time.time()
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = tennpc)
        h = s["hoithoai"]
        if not h or h["npc"] != tennpc:
            h = s["hoithoai"] = {"npc": tennpc, "buoc": "look", "luc": 0., "solan": 0, "vankhi": False}
        if h["buoc"] == "cho":
            if h["vankhi"]:
                return "xong", None
            if not is_chovankhi and now - h["luc"] > 1.5:
                if moitruong.get_is_danghiencuasotuychon():
                    moitruong.set_is_danghiencuasotuychon(False)
                return "xong", None
            if now - h["luc"] < THOIGIANCHOVANKHILLS:
                return None, None
            if h["solan"] >= SOLANTHUNOICHUYEN:
                s["hoithoai"] = None
                return "loi", None
            h["buoc"] = "look"
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHNOICHUYENLLS:
            h["buoc"] = "look"
            xdich, ydich = moitruong.get_toado(diachinpc) if diachinpc else (x, y)
            return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (xdich, ydich, idbando), "khoangcachtoida": 1.}
        if h["buoc"] == "look":
            idnpc = moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                return None, None
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {idnpc:x}#")
            h.update(buoc = "chon", luc = now)
            return None, None
        # "chon": chờ menu hiện
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung:
            if now - h["luc"] > THOIGIANCHOMENULLS:
                h["buoc"] = "look"
            return None, None
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        moitruong._inlog(f"[LĂNG LY SƠN] Menu {tennpc}: {noidung[:80]!r} {lenhs}")
        if kiemtramenu and not kiemtramenu(noidung):
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            s["hoithoai"] = None
            return "tuchoi", None
        if lenhs:
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(lenhs[0])
        h.update(buoc = "cho", luc = now, solan = h["solan"] + 1, vankhi = False)
        return None, None

    def _buocnhanthuong(self, s):
        # Hồi Thành Phù ra khỏi phó bản (is_roiphoban), phù / chạy tới Thuý Hoa Sơn, Đào Vong Khổ Dịch "1. Lĩnh nhận phần thưởng"
        moitruong = self.moitruong
        tennpc, x, y = NPCVAOLANGLYSON
        if moitruong.get_idbandohientai() != BANDO_THUYHOASON:
            s["trangthai"] = f"ra Thuý Hoa Sơn nhận thưởng"
            buoc = self._lapbuocditoibando(BANDO_THUYHOASON, is_hoithanhphu = True, is_roiphoban = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                s["trangthai"] = f"không có đường ra Thuý Hoa Sơn: {buoc['mota']}"
                return None
            return self._thuchienbuocditoibando(buoc, BANDO_THUYHOASON, (x, y), "[LĂNG LY SƠN] Nhận thưởng")
        s["trangthai"] = f"nhận thưởng ở {tennpc}"
        if time.time() < s.get("lucthulaithuong", 0.):
            return None
        ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y, is_chovankhi = False, kiemtramenu = self._is_menunhanthuong)
        if ketqua == "tuchoi":
            # NPC không có lời chúc mừng / phần thưởng: chưa chắc phó bản đã xong => KHÔNG giải tán tổ đội (giải tán là mất phó bản), thử
            # lại vài lần rồi dừng hẳn, báo người dùng xem
            s["solantuchoi"] = s.get("solantuchoi", 0) + 1
            if s["solantuchoi"] < SOLANTHUNOICHUYEN:
                s["lucthulaithuong"] = time.time() + 10.
                moitruong._inlog(f"[LĂNG LY SƠN] {tennpc} chưa có phần thưởng, 10s nữa hỏi lại (lần {s['solantuchoi']})")
                return None
            baosuco(moitruong, "langlyson", f"⚠️ Lăng Ly Sơn: {tennpc} không có phần thưởng sau {s['solantuchoi']} lần hỏi, chưa chắc phó bản đã "
                                            f"xong nên KHÔNG giải tán tổ đội, dừng tự động (xem giúp)", khoa = f"{s['batdau']}|tuchoi", giancach = 0.)
            self._ketthuclanglyson(f"❌ Dừng: {tennpc} không có phần thưởng, không giải tán tổ đội")
            return None
        if ketqua == "xong":
            s["sovong"] += 1
            s.pop("solantuchoi", None)
            moitruong._inlog(f"[LĂNG LY SƠN] Xong vòng {s['sovong']} ({int((time.time() - s['lucbatdauvong']) // 60)} phút), chờ thành viên lĩnh "
                             f"thưởng rồi đổi tổ đội")
            # Mã thưởng của vòng này báo cho thành viên cùng máy (get_khoathuonglanglyson qua shared_data): ai chưa lĩnh mã này thì tự lĩnh
            s.update(giaidoan = "doinhom", hoithoai = None, tattodoi = False, is_daroinhom = False, lucnhanthuong = time.time(),
                     khoathuong = f"{moitruong.get_idnguoichoi()}|{int(s['batdau'])}|{s['sovong']}")
        return yeucau

    def get_khoathuonglanglyson(self):
        # Mã thưởng vòng vừa xong (trưởng nhóm đã lĩnh, chưa giải tán nhóm) cho thành viên theo sau biết mà tự lĩnh, không có thì ""
        s = self._langlyson
        return s["khoathuong"] if s and s["giaidoan"] == "doinhom" and not s["is_daroinhom"] else ""

    def _laythanhvienchualanh(self, khoathuong):
        # Tên thành viên trong nhóm chạy cùng máy (shared_data) chưa báo đã lĩnh mã thưởng này. Thành viên ở máy khác không biết được, bỏ qua
        if self.shared_data is None:
            return []
        thanhviens = set(self.moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) - {self.moitruong.get_idnguoichoi()}
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return []
        tens = []
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict) or info.get("idnguoichoi") not in thanhviens:
                continue
            if time.time() - info.get("thoidiemcapnhat", 0.) > 5.:
                continue
            if info.get("_khoathuonglanglysondalanh") != khoathuong:
                tens.append(info.get("tennhanvat") or str(info.get("idnguoichoi")))
        return tens

    def _xulylanhthuongtheosau(self):
        # Thành viên theo sau: trưởng nhóm (người được theo sau, cùng máy) vừa lĩnh thưởng Lăng Ly Sơn (mã thưởng trong shared_data) mà mình
        # chưa lĩnh mã đó thì tới Đào Vong Khổ Dịch ở Thuý Hoa Sơn tự lĩnh. Chỉ làm khi đã ở Thuý Hoa Sơn (ra khỏi phó bản / tới Thuý Hoa
        # Sơn là theo sau lo). -> False: không có gì phải lĩnh (theo sau như thường); None / yêu cầu di chuyển: đang lĩnh
        info = self._laythongtinmuctieutheosaucuasokhac()
        khoathuong = info.get("_khoathuonglanglyson") if info else ""
        if not khoathuong or khoathuong == self._khoathuonglanglysondalanh:
            self._lanhthuonglanglyson = None
            return False
        moitruong = self.moitruong
        if moitruong.get_idbandohientai() != BANDO_THUYHOASON or moitruong.get_is_nhanvatdachet():
            return False
        if moitruong.get_is_dangvankhi() or time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        s = self._lanhthuonglanglyson
        if not s or s["khoa"] != khoathuong:
            s = self._lanhthuonglanglyson = {"khoa": khoathuong, "hoithoai": None}
            moitruong._inlog("[LĂNG LY SƠN] Trưởng nhóm đã lĩnh thưởng, tới Đào Vong Khổ Dịch tự lĩnh")
        tennpc, x, y = NPCVAOLANGLYSON
        self._capnhatbuocdichuyen(f"Lăng Ly Sơn: tới {tennpc} lĩnh thưởng")
        ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y, is_chovankhi = False, kiemtramenu = self._is_menunhanthuong)
        if ketqua in ("xong", "tuchoi"):
            self._khoathuonglanglysondalanh = khoathuong
            self._lanhthuonglanglyson = None
            moitruong._inlog(f"[LĂNG LY SƠN] {'Đã lĩnh thưởng' if ketqua == 'xong' else f'{tennpc} không có phần thưởng cho mình'}")
            return None
        return yeucau

    @staticmethod
    def _is_menunhanthuong(noidung):
        # Menu sau khi xong phó bản là lời chúc mừng ("Chúc mừng ngươi đã thành công rửa hận...") + "1. Lĩnh nhận phần thưởng"; menu vào
        # phó bản (lời "...báo thù rửa hận giùm ta...", "1. Tiến vào") thì không chọn
        return any(k in noidung.lower() for k in ("chúc mừng", "phần thưởng"))

    def _laythanhvienconnhom(self, s):
        # Tên thành viên vòng này chạy cùng máy (shared_data) còn đang ở trong nhóm
        tens = []
        try:
            danhsach = list(self.shared_data.items()) if self.shared_data is not None else []
        except Exception:
            return tens
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict) or info.get("idnguoichoi") not in s["thanhviens"]:
                continue
            if time.time() - info.get("thoidiemcapnhat", 0.) <= 5. and info.get("idtruongnhom"):
                tens.append(info.get("tennhanvat") or str(info.get("idnguoichoi")))
        return tens

    def get_dsidtattodoilanglyson(self):
        # Đang giải tán tổ đội cũ: ID mình và các thành viên vòng này (báo qua shared_data để cửa sổ của họ tạm tắt Tổ đội tự động)
        s = self._langlyson
        if s and s["giaidoan"] == "doinhom" and s.get("tattodoi"):
            return [self.moitruong.get_idnguoichoi(), *s["thanhviens"]]
        return []

    def get_is_tamtattodoilanglyson(self):
        # Tổ đội tự động phải tạm nghỉ: mình đang giải tán tổ đội cũ, hoặc trưởng nhóm cùng máy đang giải tán mà mình là thành viên vòng đó
        return bool(self.get_dsidtattodoilanglyson()) or self._is_trongdanhsachcuasokhac("_langlysontattodoi")

    def action_roinhomlanglyson(self):
        # Gọi đầu Tổ đội tự động: đang phải tạm nghỉ thì không mời / nhận lời mời / xin vào nhóm, còn trong nhóm thì rời (trưởng nhóm rời
        # là giải tán). -> True khi đang tạm nghỉ (Tổ đội tự động bỏ qua lượt này)
        if not self.get_is_tamtattodoilanglyson():
            return False
        if self.moitruong.get_is_dangnamtrongnhom() and time.time() - self._thoidiemroinhomlanglyson > GIANCACHROINHOM:
            self._thoidiemroinhomlanglyson = time.time()
            self.moitruong._inlog("[LĂNG LY SƠN] Rời nhóm để giải tán tổ đội cũ (Tổ đội tự động tạm nghỉ)")
            self.moitruong.action_thoatkhoinhom()
        return True

    def _buocdoinhom(self, s):
        # Phó bản cũ giữ theo tổ đội: trưởng nhóm rời nhóm (= giải tán), chờ Tổ đội tự động lập nhóm mới rồi vào vòng sau
        moitruong = self.moitruong
        is_trongnhom = moitruong.get_is_dangnamtrongnhom()
        if is_trongnhom and not s["is_daroinhom"]:
            # Mỗi thành viên tự lĩnh thưởng của mình: chờ các thành viên cùng máy lĩnh xong (tối đa THOIGIANCHOTHANHVIENLANH giây) mới giải tán
            chualanhs = self._laythanhvienchualanh(s["khoathuong"])
            conlai = THOIGIANCHOTHANHVIENLANH - (time.time() - s["lucnhanthuong"])
            if chualanhs and conlai > 0:
                s["trangthai"] = f"chờ {', '.join(chualanhs)} lĩnh thưởng (còn {int(conlai)}s)"
                return None
            if chualanhs:
                self._baolanglyson(s, f"chualanh|{s['sovong']}", f"⚠️ Lăng Ly Sơn: {', '.join(chualanhs)} chưa lĩnh thưởng vòng {s['sovong']} "
                                                                 f"sau {int(THOIGIANCHOTHANHVIENLANH)}s, vẫn giải tán tổ đội")
        if not s["is_daroinhom"]:
            # Giải tán: tạm tắt Tổ đội tự động ở mình và mọi thành viên vòng này cùng máy (không thì nó kéo nhau vào lại nhóm cũ, nhóm cũ
            # còn giữ phó bản đã xong), ai còn trong nhóm thì tự rời (action_roinhomlanglyson). Hết người trong nhóm cũ (hoặc quá
            # THOIGIANCHOGIAITAN giây) thì bật lại để Tổ đội tự động lập nhóm mới
            if not s.get("tattodoi"):
                s.update(tattodoi = True, luctattodoi = time.time())
                moitruong._inlog("[LĂNG LY SƠN] Tạm tắt Tổ đội tự động, mọi người rời nhóm để giải tán tổ đội cũ")
            conlais = self._laythanhvienconnhom(s)
            if is_trongnhom:
                conlais = [moitruong.get_tendoituong() or "mình"] + conlais
            if conlais and time.time() - s["luctattodoi"] < THOIGIANCHOGIAITAN:
                s["trangthai"] = f"giải tán tổ đội cũ (tạm tắt Tổ đội tự động), còn trong nhóm: {', '.join(conlais)}"
                return None
            if conlais:
                self._baolanglyson(s, f"giaitan|{s['sovong']}", f"⚠️ Lăng Ly Sơn: {int(THOIGIANCHOGIAITAN)}s chưa giải tán hết tổ đội cũ "
                                                                f"({', '.join(conlais)} còn trong nhóm), vẫn lập nhóm mới")
            s.update(tattodoi = False, is_daroinhom = True)
            moitruong._inlog("[LĂNG LY SƠN] Đã giải tán tổ đội cũ, bật lại Tổ đội tự động để lập nhóm mới")
            return None
        if not is_trongnhom:
            s["trangthai"] = "đã giải tán tổ đội, chờ lập tổ đội mới"
            if not self._is_tudongtodoi:
                self._baolanglyson(s, "todoi", "⚠️ Lăng Ly Sơn: chưa bật Tổ đội tự động, lập tổ đội mới bằng tay để đi vòng sau")
            return None
        s.update(giaidoan = "vao", buoc = {}, boss = None, hoithoai = None, lucbatdauvong = time.time(), thanhviens = {}, dudoi = False,
                 lucchodoi = 0., lucmoi = {}, diemvao = {}, daxongphoban = False)
        moitruong._inlog(f"[LĂNG LY SƠN] Có tổ đội mới, bắt đầu vòng {s['sovong'] + 1}")
        return None
