# Nhiệm vụ sư môn (bật tay trên giao diện, tối đa 20 lượt / ngày): mỗi lượt đọc nhiệm vụ trong cửa sổ nhiệm vụ (nhiemvu_xq) rồi làm bước
# kế tiếp, nhiệm vụ đổi thì bước đổi theo (không nhớ quy trình riêng nên bot tắt / bật lại giữa chừng vẫn làm tiếp được):
#   không có nhiệm vụ   : tới NPC giao nhiệm vụ (Côn Luân dưới 60: Văn Xương Chân Quân), "2. Tiếp nhận nhiệm vụ" -> "1. Tiếp nhận"
#                         (tallk <id># quest -> tallk <id># accept_quest)
#   đã xong (Xong) / đủ tiến độ: về NPC giao, "Hoàn thành nhiệm vụ" (tallk <id># task_info)
#   Đi tìm Thạch Sư     : tới Thạch Sư nhận việc (accept_task.1 -> accept_task.11)
#   Thu thập            : tới bản đồ trong mô tả đánh đúng quái đó, nhặt vật phẩm; đủ số thì Hồi môn phái, tới Thạch Sư "Hoàn thành"
#   Mua sắm             : tới cửa hàng trong mô tả (NPC các nước có tên riêng, tên cửa hàng là danh hiệu), tra ô / giá theo tên món
#                         (chưa biết thì mở cửa hàng đọc 1 lần rồi đóng), mua bằng lệnh buy; đủ thì đưa lên hành trang 1, give Thạch Sư
#   Thăm viếng          : tới NPC (chưởng môn / quân vương, bảng BANDOTHAMVIENG), "Hoàn thành nhiệm vụ"
#   Luyện tập / Du lịch : farm theo lộ trình điểm đánh của nhân vật tới khi xong
#   Bắt yêu quái        : có Dây Càn Khôn (hết thì về Chủ Tiệm Tạp Hóa mua), tới bản đồ, đứng gần quái dùng "pf2 51 <id>#"
#                         cách nhau ít nhất 0.25s tới khi bắt được
# Hội thoại NPC: "look <id>#" mở menu, mỗi bước chọn lựa chọn trong menu vừa hiện có lệnh đúng từ khoá (số info / task đổi theo máy chủ),
# menu không có thì gửi thẳng lệnh. Gửi xong chờ nhiệm vụ đổi, quá SOLANTHUSUMON lần không đổi thì dừng, báo Telegram.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import os
import time

from hangso_xq import *
from bando_xq import timduongbando
from giaodo_xq import taolenhgiao
from nhiemvu_xq import *
from thongbao_xq import baosuco
from tienich_xq import phatam, tailotrinhmau as util_tailotrinhmau

DAYCANKHON = "Dây Càn Khôn"
# Hết Dây Càn Khôn thì về Chủ Tiệm Tạp Hóa ở Tân Thủ Thôn mua chừng này (ô / giá tra theo tên trong cửa hàng)
SOLUONGMUADAYCANKHON = 30
# Mở cửa hàng (action_xulymocuahang): quá chừng này giây kể từ lúc bấm NPC mà cửa sổ chưa hiện thì coi như không mở được
THOIGIANMOCUAHANGTOIDA = 10.
THOIGIANCHOLIST = 3.
LENHBATBAOTHU = "pf2 51 {:x}#"
GIANCACHBATBAOTHU = 0.3
KHOANGCACHBATBAOTHU = 3.
KHOANGCACHNOICHUYEN = 3.
# Gửi xong hội thoại chừng này giây mà nhiệm vụ chưa đổi thì thử lại, quá SOLANTHUSUMON lần thì dừng
THOIGIANCHONHIEMVUDOI = 4.
SOLANTHUSUMON = 3
# Mỗi bước hội thoại cách nhau, chờ menu trả lời tối đa
GIANCACHBUOCHOITHOAI = 0.8
THOIGIANCHOMENU = 2.
GIANCACHHOIMONPHAI = 15.
SOLANHOIMONPHAI = 3
# Điểm khám phá / tuần tra: tới gần chừng này ô, hoặc quá chừng này giây thì sang điểm kế
KHOANGCACHTOIDIEM = 4.
THOIGIANMOIDIEM = 45.
THOIGIANSUMONTOIDA = 4 * 3600.
GIANCACHGHIVITRI = 3.


class TacTuSuMon:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_sumon(self):
        if self._sumon:
            return
        self._sumon = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "thu": {}, "hoithoai": None, "lucmonphai": 0.,
                       "solanmonphai": 0, "khampha": None, "lucbat": 0., "luotdangnhan": 0, "soluotxong": 0, "tenquai": set(),
                       "vatphamnhat": set(), "dabao": set(), "kinhnghiem": {}}
        print("[SƯ MÔN] Bắt đầu làm nhiệm vụ sư môn")
        phatam("Bắt đầu nhiệm vụ sư môn")

    def huy_sumon(self):
        if self._sumon:
            self._ketthucsumon(thongbao = "Đã dừng nhiệm vụ sư môn (bấm tay)")

    def get_is_dangsumon(self):
        return bool(self._sumon)

    def get_is_sumondichuyen(self):
        # Sư môn đang tự lo di chuyển (đi đường, nói chuyện NPC, bắt yêu quái): không chọn quái dọc đường, đi trước đánh / nhặt
        return bool(self._sumon) and self._sumon["chedo"] in ("dichuyen", "cho")

    def get_is_sumonfarm(self):
        # Luyện tập / Du lịch: farm như thường theo lộ trình điểm đánh của nhân vật (kể cả khi chưa bật ô lộ trình)
        return bool(self._sumon) and self._sumon["chedo"] == "farm"

    def get_trangthaisumon(self):
        if self._sumon:
            return f"Sư môn: {self._sumon['trangthai']}"
        return self._ketquasumon or ""

    def thietlap_npcgiaosumon(self, ten):
        self._sumon_npcgiao = (ten or "").strip()
        print(f"[SƯ MÔN] NPC giao nhiệm vụ: {self._sumon_npcgiao or '(mặc định theo môn phái)'}")

    def _laynpcgiaosumon(self):
        return self._sumon_npcgiao or NPCSUMONMACDINH.get(self.moitruong.get_tenmonphai(), ("", ""))[0]

    def _laytenmuctieutancongs(self):
        # Danh sách tên được đánh: lúc Thu thập thì chỉ đánh quái ra vật phẩm cần, còn lại là danh sách của người dùng
        if self._sumon and self._sumon["chedo"] == "danhquai" and self._sumon["tenquai"]:
            return self._sumon["tenquai"]
        return self._tenmuctieutancongs

    def _layvatphamnhatsumon(self):
        return self._sumon["vatphamnhat"] if self._sumon and self._sumon["chedo"] == "danhquai" else ()

    def _ketthucsumon(self, loi = None, thongbao = None):
        s = self._sumon
        self._sumon = None
        self._yeucautudo = None
        noidung = thongbao or (f"❌ Sư môn dừng: {loi}" if loi else "✅ Xong nhiệm vụ sư môn")
        if s and s["soluotxong"]:
            noidung += f" (phiên này trả {s['soluotxong']} lượt)"
        print(f"[SƯ MÔN] {noidung}")
        self._ketquasumon = f"{time.strftime('%H:%M')} {noidung}"
        baosuco(self.moitruong, "sumon", noidung, khoa = s["batdau"] if s else None, giancach = 0.)
        phatam("Lỗi nhiệm vụ sư môn" if loi else "Kết thúc nhiệm vụ sư môn")

    def _baomotlan(self, s, khoa, noidung):
        # Báo Telegram 1 lần cho mỗi việc cần người dùng làm (mua tay, thêm luật...), bot vẫn chờ
        if khoa not in s["dabao"]:
            s["dabao"].add(khoa)
            print(f"[SƯ MÔN] {noidung}")
            baosuco(self.moitruong, "sumon", noidung, khoa = f"{s['batdau']}|{khoa}", giancach = 0.)

    # --- Vị trí NPC / quái -------------------------------------------------------------------------------------------------------
    def action_ghivitridoituong(self):
        # Ghi lại NPC / quái đang thấy (tên, bản đồ, toạ độ) cho sư môn tìm về sau, kể cả khi không làm sư môn
        if time.time() - self._thoidiemghivitridoituong < GIANCACHGHIVITRI:
            return
        self._thoidiemghivitridoituong = time.time()
        moitruong = self.moitruong
        idnguoichoi = moitruong.get_idnguoichoi()
        idbando = moitruong.get_idbandohientai()
        if not idnguoichoi or not idbando:
            return
        self._sovitri.nap(idnguoichoi)
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi):
                continue
            ten = moitruong.get_tendoituong(diachi)
            # Bảo thú có tên chủ trong ngoặc
            if not ten or "(" in ten:
                continue
            x, y = moitruong.get_toado(diachi)
            if moitruong.get_is_npc(diachi):
                self._sovitri.ghinpc(ten, idbando, x, y)
                # Cửa hàng các nước: ghi cả theo danh hiệu ("Chủ Tiệm Vũ Khí") để tìm theo tên cửa hàng trong nhiệm vụ
                danhhieu = moitruong.get_danhhieudoituong(diachi)
                if danhhieu:
                    self._sovitri.ghinpc(danhhieu, idbando, x, y)
            elif moitruong.get_is_cothetancong(diachi):
                self._sovitri.ghiquai(ten, idbando, x, y)
        # Cửa hàng đang mở (người chơi tự mở): nhớ hàng theo NPC gần nhất
        if not self._mocuahang:
            cuahang = moitruong.get_cuahangdangmo()
            if cuahang and cuahang["is_danghien"] and cuahang["hang"]:
                diachi = self._timnpcganhat(KHOANGCACHNOICHUYEN + 2)
                if diachi:
                    self._sovitri.ghicuahang(idbando, (moitruong.get_tendoituong(diachi), moitruong.get_danhhieudoituong(diachi)), cuahang["hang"])
        self._sovitri.luu()

    def _timnpcganhat(self, khoangcachtoida):
        moitruong = self.moitruong
        tot, khoangcachtot = None, khoangcachtoida
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if moitruong.get_is_nguoichoi(diachi) or not moitruong.get_is_npc(diachi):
                continue
            khoangcach = moitruong.get_khoangcach(diachi)
            if khoangcach <= khoangcachtot:
                tot, khoangcachtot = diachi, khoangcach
        return tot

    # --- Cửa hàng ------------------------------------------------------------------------------------------------------------------
    def batdau_mocuahang(self, diachinpc):
        # Mở cửa hàng NPC ("list <id>#", như lựa chọn trong menu NPC), đọc hàng (ô / giá theo tên) vào SoVitri rồi đóng ngay cửa sổ. Dùng cho Mua sắm,
        # Dây Càn Khôn, Mua bù.
        # -> False khi đang mở cửa hàng khác
        if self._mocuahang:
            return False
        moitruong = self.moitruong
        # Cửa sổ cửa hàng còn đang hiện (người chơi mở) thì đóng trước, để biết lần hiện sau là của cửa hàng này
        moitruong.action_dongcuasocuahang()
        idnpc = moitruong.get_iddoituong(diachinpc)
        self._mocuahang = {"idnpc": idnpc, "manpc": f"{idnpc:x}#", "idbando": moitruong.get_idbandohientai(),
                           "tens": (moitruong.get_tendoituong(diachinpc), moitruong.get_danhhieudoituong(diachinpc)), "buoc": 0,
                           "luc": 0., "batdau": time.time()}
        print(f"[CỬA HÀNG] Mở cửa hàng {self._mocuahang['tens']} để đọc hàng")
        return True

    def get_ketquamocuahang(self, idbando, tennpc):
        # Lần mở cửa hàng gần nhất của NPC này (tên riêng hoặc danh hiệu): (True / False, lúc), chưa mở thì None
        return self._ketquamocuahang.get((idbando, chuanhoaten(tennpc)))

    def action_xulymocuahang(self):
        # Mỗi lượt 1 bước: "list <id>#" mở cửa hàng; THOIGIANCHOLIST giây chưa hiện thì bấm NPC (look) -> chọn lựa chọn có lệnh mua / list /
        # shop trong menu. Cửa sổ hiện thì đọc hàng, đóng
        mc = self._mocuahang
        if not mc:
            return
        moitruong = self.moitruong
        now = time.time()
        if now - mc["luc"] < GIANCACHBUOCHOITHOAI:
            return
        cuahang = moitruong.get_cuahangdangmo()
        if mc["buoc"] > 0 and cuahang and cuahang["is_danghien"] and cuahang["hang"]:
            self._sovitri.ghicuahang(mc["idbando"], mc["tens"], cuahang["hang"])
            self._sovitri.luu(is_ngay = True)
            self._ketthucmocuahang(True, f"đọc được {len(cuahang['hang'])} món: " + ", ".join(f"{t} (ô {o}, {g})" for o, g, t in cuahang["hang"]))
            return
        if now - mc["batdau"] > THOIGIANMOCUAHANGTOIDA or moitruong.get_idbandohientai() != mc["idbando"]:
            self._ketthucmocuahang(False, "không thấy cửa sổ cửa hàng hiện")
            return
        if mc["buoc"] == 0:
            moitruong.action_ngatdichuyen()
            moitruong.action_thucthicaulenh(f"list {mc['manpc']}")
            mc["buoc"] = 1
        elif mc["buoc"] == 1:
            if now - mc["batdau"] < THOIGIANCHOLIST:
                return
            print(f"[CỬA HÀNG] list {mc['manpc']} chưa mở được cửa hàng {mc['tens']}, thử bấm NPC")
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {mc['manpc']}")
            mc["buoc"] = 2
        elif mc["buoc"] == 2:
            if not moitruong.get_noidungcuasotuychon() and now - mc["luc"] < THOIGIANCHOMENU:
                return
            lenhs = moitruong.get_lenhcuasotuychons() if moitruong.get_noidungcuasotuychon() else []
            lenh = next((l for l in lenhs if any(k in l.lower() for k in ("buy", "list", "shop", "trade", "mua"))), None)
            print(f"[CỬA HÀNG] Menu {mc['tens']}: {lenhs} -> {lenh or 'không có lựa chọn mua'}")
            moitruong._inlog(f"[CỬA HÀNG] Menu {mc['tens']} {mc['manpc']}: {lenhs} -> {lenh}")
            if lenh:
                moitruong.action_thucthicaulenh(lenh)
            mc["buoc"] = 3
        mc["luc"] = now

    def _ketthucmocuahang(self, is_ok, mota):
        mc = self._mocuahang
        self._mocuahang = None
        moitruong = self.moitruong
        # Đọc xong thì đóng luôn: cửa sổ (cờ đang hiện) và báo máy chủ như bấm X; menu NPC còn hiện cũng đóng
        cuahang = moitruong.get_cuahangdangmo()
        if cuahang and cuahang["is_danghien"]:
            moitruong.action_dongcuasocuahang()
            moitruong.action_thucthicaulenh("buy close")
        if moitruong.get_is_danghiencuasotuychon():
            moitruong.set_is_danghiencuasotuychon(False)
        for ten in mc["tens"]:
            if ten:
                self._ketquamocuahang[(mc["idbando"], chuanhoaten(ten))] = (is_ok, time.time())
        print(f"[CỬA HÀNG] {mc['tens']}: {mota}")
        moitruong._inlog(f"[CỬA HÀNG] {mc['tens']}: {mota}")

    def _timdoituongxungquanh(self, ten, is_quai = False):
        # Đối tượng gần nhất khớp tên (NPC: tên nhiệm vụ có thể ngắn hơn tên NPC; quái: còn sống, đánh được)
        moitruong = self.moitruong
        tot, khoangcachtot = None, None
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi):
                continue
            if is_quai:
                if chuanhoaten(moitruong.get_tendoituong(diachi)) != chuanhoaten(ten) or not moitruong.get_is_cothetancong(diachi):
                    continue
            elif not is_trungten(ten, moitruong.get_tendoituong(diachi)) and not is_trungten(ten, moitruong.get_danhhieudoituong(diachi)):
                continue
            khoangcach = moitruong.get_khoangcach(diachi)
            if khoangcachtot is None or khoangcach < khoangcachtot:
                tot, khoangcachtot = diachi, khoangcach
        return tot

    def _thumucgame(self):
        try:
            return os.path.dirname(self.moitruong.gamemodule.filename)
        except Exception:
            return None

    # --- Di chuyển ---------------------------------------------------------------------------------------------------------------
    def _dentoi(self, s, idbando, x, y, nhan, khoangcach = 2.):
        # Đi tới (x, y) ở bản đồ idbando (x None: chỉ cần tới bản đồ). Bản đồ môn phái ở xa thì Hồi môn phái ("dGludmF0 1")
        moitruong = self.moitruong
        idbandohientai = moitruong.get_idbandohientai()
        bandomonphai = BANDOMONPHAI.get(moitruong.get_tenmonphai())
        if idbandohientai == bandomonphai:
            s["solanmonphai"] = 0
        if idbandohientai != idbando:
            s["trangthai"] = f"đi tới {nhan} ({laytenbando(idbando)})"
            duongdi = timduongbando(idbandohientai, idbando, moitruong.get_toado())
            if idbando == bandomonphai and s["solanmonphai"] < SOLANHOIMONPHAI and (duongdi is None or len(duongdi) > 2):
                now = time.time()
                if now - s["lucmonphai"] > GIANCACHHOIMONPHAI and now - moitruong.get_thoidiemthaydoibandogannhat() >= 2.:
                    print(f"[SƯ MÔN] Hồi môn phái để tới {nhan}")
                    moitruong.action_ngatdichuyen()
                    moitruong.action_thucthicaulenh("dGludmF0 1")
                    s["lucmonphai"] = now
                    s["solanmonphai"] += 1
                self._capnhatbuocdichuyen(f"Sư môn: Hồi môn phái tới {nhan}")
                return None
            buoc = self._lapbuocditoibando(idbando, is_hoithanhphu = True)
            if buoc["loai"] != "toinoi":
                return self._thuchienbuocditoibando(buoc, idbando, (x, y) if x is not None else None, f"[SƯ MÔN] {nhan}")
        if x is None:
            return None
        s["trangthai"] = f"tới {nhan} ({x}, {y})"
        self._capnhatbuocdichuyen(f"Sư môn: tới {nhan} ({x}, {y}) ở {laytenbando(idbando)}")
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": khoangcach}

    def _diquadiem(self, s, khoa, idbando, diems, nhan):
        # Đi lần lượt qua các điểm (tìm NPC / quái chưa biết chỗ, tuần tra chờ quái): tới gần hoặc quá THOIGIANMOIDIEM thì sang điểm kế
        if not diems:
            return self._dentoi(s, idbando, None, None, nhan)
        kp = s["khampha"]
        if not kp or kp["khoa"] != khoa:
            kp = s["khampha"] = {"khoa": khoa, "i": 0, "luc": time.time()}
        if self.moitruong.get_idbandohientai() == idbando:
            x, y = diems[kp["i"] % len(diems)]
            if self.moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIDIEM or time.time() - kp["luc"] > THOIGIANMOIDIEM:
                kp["i"] += 1
                kp["luc"] = time.time()
        else:
            kp["luc"] = time.time()
        x, y = diems[kp["i"] % len(diems)]
        return self._dentoi(s, idbando, x, y, f"{nhan} (điểm {kp['i'] % len(diems) + 1}/{len(diems)})", khoangcach = 1.)

    def _laydiemtimquai(self, tenquai, idbando):
        # Chỗ từng thấy quái này, rồi lộ trình mẫu của bản đồ, rồi các cổng / điểm xuất hiện
        diems = []
        vitri = self._sovitri.timquai(tenquai, idbando)
        if vitri:
            diems.append(tuple(vitri))
        for mau in util_tailotrinhmau().get(str(idbando), []):
            for d in mau.get("diem") or []:
                if len(d) < 3 or int(d[2]) == idbando:
                    diems.append((int(d[0]), int(d[1])))
        return diems or laydiemkhampha(idbando)

    def _tinpc(self, s, tennpc, idbandogoiy = None, is_chibandogoiy = False):
        # Đi tìm NPC: thấy rồi -> địa chỉ; chưa thấy -> yêu cầu di chuyển tới chỗ đã biết / đi khắp bản đồ gợi ý. -> (địa chỉ, yêu cầu).
        # is_chibandogoiy: NPC phải ở đúng bản đồ gợi ý (Chủ Tiệm Vũ Khí nước nào cũng có)
        is_dungbando = not is_chibandogoiy or self.moitruong.get_idbandohientai() == idbandogoiy
        diachi = self._timdoituongxungquanh(tennpc) if is_dungbando else None
        if diachi:
            return diachi, None
        vitri = self._sovitri.timnpc(tennpc, self._thumucgame(), idbandogoiy if is_chibandogoiy else None)
        # Tới chỗ đã biết mà không thấy (NPC đổi chỗ / vị trí sai): đi khắp bản đồ đó tìm
        if vitri and not (self.moitruong.get_idbandohientai() == vitri[0] and self.moitruong.get_khoangcachdiem(vitri[1], vitri[2]) <= KHOANGCACHTOIDIEM):
            return None, self._dentoi(s, vitri[0], vitri[1], vitri[2], tennpc)
        idbandogoiy = vitri[0] if vitri else idbandogoiy
        if idbandogoiy:
            return None, self._diquadiem(s, f"npc|{tennpc}", idbandogoiy, laydiemkhampha(idbandogoiy), f"tìm {tennpc}")
        return None, None

    # --- Hội thoại NPC -----------------------------------------------------------------------------------------------------------
    def _noichuyen(self, s, nv, tennpc, buocs, viec, idbandogoiy = None, is_chibandogoiy = False):
        # Tới gần NPC rồi nói chuyện theo các bước (xem _xulyhoithoaisumon). Mỗi việc (theo lượt + loại) thử tối đa SOLANTHUSUMON lần,
        # mỗi lần chờ THOIGIANCHONHIEMVUDOI giây cho nhiệm vụ đổi. -> yêu cầu di chuyển hoặc None
        if not tennpc:
            self._ketthucsumon(f"chưa biết NPC để {viec}")
            return None
        moitruong = self.moitruong
        diachi, yeucau = self._tinpc(s, tennpc, idbandogoiy, is_chibandogoiy)
        if not diachi:
            if yeucau is None and not idbandogoiy:
                self._ketthucsumon(f"không biết {tennpc} ở đâu ({viec}): đứng gần NPC đó 1 lần cho bot ghi lại vị trí")
            return yeucau
        if moitruong.get_khoangcach(diachi) > KHOANGCACHNOICHUYEN:
            x, y = moitruong.get_toado(diachi)
            return self._dentoi(s, moitruong.get_idbandohientai(), x, y, tennpc)
        khoa = f"{nv['luot'] if nv else 0}|{nv['loai'] if nv else ''}|{viec}"
        solan, luc = s["thu"].get(khoa, (0, 0.))
        if time.time() - luc < THOIGIANCHONHIEMVUDOI:
            s["trangthai"] = f"chờ {tennpc} ({viec})"
            return None
        if solan >= SOLANTHUSUMON:
            self._ketthucsumon(f"{viec} ở {tennpc} {solan} lần mà nhiệm vụ không đổi ({motanhiemvu(nv)})")
            return None
        moitruong.action_ngatdichuyen()
        idnpc = moitruong.get_iddoituong(diachi)
        s["thu"][khoa] = (solan + 1, time.time() + 10.)
        s["hoithoai"] = {"manpc": f"{idnpc:x}#", "buocs": list(buocs), "luc": 0., "khoa": khoa, "dangchomenu": False}
        s["trangthai"] = f"{viec} ở {tennpc} (lần {solan + 1})"
        print(f"[SƯ MÔN] {viec} ở {tennpc} (lần {solan + 1}): {buocs}")
        return None

    def _xulyhoithoaisumon(self, s):
        # Mỗi lượt gửi tối đa 1 bước. Bước: "look" (mở menu gốc), "give:<lệnh>" (gửi nguyên lệnh), hoặc từ khoá lệnh: chọn lựa chọn có lệnh
        # "tallk <id># <từ khoá>" trong menu vừa hiện (chờ tối đa THOIGIANCHOMENU), không có thì gửi thẳng lệnh đó
        hoithoai = s["hoithoai"]
        moitruong = self.moitruong
        now = time.time()
        if now - hoithoai["luc"] < GIANCACHBUOCHOITHOAI:
            return
        if not hoithoai["buocs"]:
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            s["thu"][hoithoai["khoa"]] = (s["thu"][hoithoai["khoa"]][0], now)
            s["hoithoai"] = None
            return
        buoc = hoithoai["buocs"][0]
        manpc = hoithoai["manpc"]
        if buoc == "look":
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {manpc}")
            hoithoai["dangchomenu"] = True
        elif buoc.startswith("give:"):
            moitruong.action_thucthicaulenh(buoc[5:])
            hoithoai["dangchomenu"] = False
        else:
            if hoithoai["dangchomenu"] and not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            lenhs = moitruong.get_lenhcuasotuychons() if moitruong.get_noidungcuasotuychon() else []
            lenh = next((l for l in lenhs if l.split("# ", 1)[-1].strip() == buoc), None) or f"tallk {manpc} {buoc}"
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(lenh)
            hoithoai["dangchomenu"] = True
        hoithoai["buocs"].pop(0)
        hoithoai["luc"] = now

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulysumon(self):
        # Gọi thay lộ trình điểm đánh khi đang làm sư môn -> yêu cầu di chuyển hoặc None. Chế độ "farm" thì lộ trình điểm đánh chạy tiếp
        s = self._sumon
        moitruong = self.moitruong
        if moitruong.get_is_nhanvatdachet() or moitruong.get_is_dangvankhi() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0:
            return None
        if time.time() - s["batdau"] > THOIGIANSUMONTOIDA:
            self._ketthucsumon(f"quá {int(THOIGIANSUMONTOIDA // 3600)} giờ chưa xong")
            return None
        if s["hoithoai"]:
            s["chedo"] = "dichuyen"
            self._xulyhoithoaisumon(s)
            return None

        nv = laynhiemvusumon(moitruong.get_danhsachmucnhiemvu())
        # Lượt đang nhận đổi (trả xong / sang lượt mới): đếm lượt đã trả, xong lượt cuối thì dừng
        if s["luotdangnhan"] and (not nv or nv["luot"] != s["luotdangnhan"]):
            s["soluotxong"] += 1
            print(f"[SƯ MÔN] Đã trả lượt {s['luotdangnhan']}")
            if s["luotdangnhan"] >= SOLUOTSUMONTOIDA:
                self._ketthucsumon(thongbao = f"✅ Đã làm xong {SOLUOTSUMONTOIDA} lượt sư môn hôm nay")
                return None
        s["luotdangnhan"] = nv["luot"] if nv else 0
        s["tenquai"], s["vatphamnhat"] = set(), set()
        s["chedo"] = "dichuyen"

        npcgiao = self._laynpcgiaosumon()
        bandomonphai = BANDOMONPHAI.get(moitruong.get_tenmonphai())
        if not nv:
            s["trangthai"] = "nhận nhiệm vụ"
            return self._noichuyen(s, nv, npcgiao, ["look", "quest", "accept_quest"], "nhận nhiệm vụ", bandomonphai)
        loai = nv["loai"]
        if nv["is_xong"] or (loai in (LOAI_LUYENTAP, LOAI_DULICH) and (is_dutiendo(nv) or self._is_dukinhnghiem(s, nv))):
            return self._noichuyen(s, nv, npcgiao, ["look", "task_info"], "trả nhiệm vụ", bandomonphai)
        if loai == LOAI_DENTIM:
            return self._noichuyen(s, nv, nv["npc"], ["look", "accept_task.1", "accept_task.11"], "nhận việc", bandomonphai)
        if loai == LOAI_THUTHAP:
            return self._buocthuthap(s, nv, bandomonphai)
        if loai == LOAI_THUMUA:
            return self._buocthumua(s, nv, bandomonphai)
        if loai == LOAI_THAMVIENG:
            idbando = next((b for ten, b in BANDOTHAMVIENG.items() if is_trungten(ten, nv["npc"]) or is_trungten(nv["npc"], ten)), None) \
                      or timbandotheoten(nv.get("bando"))
            return self._noichuyen(s, nv, nv["npc"], ["look", "task_info"], "thăm viếng", idbando)
        if loai in (LOAI_LUYENTAP, LOAI_DULICH):
            s["chedo"] = "farm"
            s["trangthai"] = f"{TENLOAI[loai]}: farm theo lộ trình" + (f" ({nv['tiendo'][0]}/{nv['tiendo'][1]})" if nv["tiendo"] else "")
            if not self._diemdanhxungquanhs:
                self._baomotlan(s, "chualotrinh", f"{TENLOAI[loai]} cần lộ trình farm hợp cấp: nhân vật chưa có điểm đánh, đang đánh quanh chỗ đứng")
            return None
        if loai == LOAI_BATYEUQUAI:
            # Bắt được thì quái thành bảo thú trong danh sách (cửa sổ nhiệm vụ không báo Xong): về trả ngay
            if any(chuanhoaten(ten) == chuanhoaten(nv["quai"]) for ten in moitruong.get_danhsachtenbaothugiangho()):
                return self._noichuyen(s, nv, npcgiao, ["look", "task_info"], f"nộp {nv['quai']}", bandomonphai)
            return self._buocbatyeuquai(s, nv)
        self._ketthucsumon(f"chưa biết làm nhiệm vụ này: {nv['ten']} – {nv['mucdich']}")
        return None

    def _is_dukinhnghiem(self, s, nv):
        # Luyện tập mà máy chủ không gửi tiến độ: tự đếm kinh nghiệm tăng từ lúc thấy lượt này
        if nv["loai"] != LOAI_LUYENTAP or not nv.get("can"):
            return False
        kinhnghiem = self.moitruong.get_kinhnghiem()
        if kinhnghiem is None:
            return False
        batdau = s["kinhnghiem"].setdefault(nv["luot"], kinhnghiem)
        return kinhnghiem - batdau >= nv["can"]

    def _buocthuthap(self, s, nv, bandomonphai):
        soluong = (self.moitruong.get_soluongvatphamhanhtrangtheoten() or {}).get(nv["vatpham"], 0)
        if soluong >= nv["soluong"]:
            return self._noichuyen(s, nv, nv["npc"], ["look", "task_info"], f"giao {nv['soluong']} {nv['vatpham']}", bandomonphai)
        idbando = timbandotheoten(nv.get("bando"))
        if not idbando or not nv.get("quai"):
            self._ketthucsumon(f"không rõ đánh quái gì / ở đâu để thu thập {nv['vatpham']}: {nv['mota']}")
            return None
        nhan = f"thu thập {nv['vatpham']} {soluong}/{nv['soluong']} (đánh {nv['quai']})"
        if self.moitruong.get_idbandohientai() != idbando:
            return self._dentoi(s, idbando, None, None, nhan)
        s["chedo"] = "danhquai"
        s["tenquai"], s["vatphamnhat"] = {nv["quai"]}, {nv["vatpham"]}
        s["trangthai"] = nhan
        return self._diquadiem(s, f"quai|{nv['quai']}|{idbando}", idbando, self._laydiemtimquai(nv["quai"], idbando), nhan)

    def _demvatpham(self, ten):
        # Tổng số món tên này trong túi (không phân biệt "Thuỷ" / "Thủy")
        return sum(sl for tenxet, sl in (self.moitruong.get_soluongvatphamhanhtrangtheoten() or {}).items() if chuanhoaten(tenxet) == chuanhoaten(ten))

    def _buocthumua(self, s, nv, bandomonphai):
        # Chưa đủ món: tới cửa hàng trong mô tả (vd Chủ Tiệm Vũ Khí ở Tần Quốc, không ghi nước thì Tân Thủ Thôn), mở cửa hàng, tìm món
        # theo tên lấy ô / giá rồi mua. Đủ rồi thì đưa lên hành trang 1 và give cho Thạch Sư
        moitruong = self.moitruong
        ids = [(vitri, iddoituong) for tenxet, mons in moitruong.get_danhsachvatphamhanhtrang_map().items()
               if chuanhoaten(tenxet) == chuanhoaten(nv["vatpham"]) for vitri, iddoituong in mons if iddoituong]
        if self._demvatpham(nv["vatpham"]) < nv["soluong"]:
            return self._buocmuahang(s, nv)
        # Đồ giao cho NPC phải nằm ở hành trang 1 (24 ô đầu); vừa mua mà túi chưa kịp có id thì chờ lượt sau
        if not ids:
            return None
        vitri, iddoituong = ids[0]
        if vitri >= 24:
            if time.time() - s.get("lucchuyentui", 0.) > 3.:
                s["lucchuyentui"] = time.time()
                print(f"[SƯ MÔN] Chuyển {nv['vatpham']} lên hành trang 1 để giao")
                moitruong.action_thucthicaulenh(f"move {iddoituong:x}# to 1")
            s["trangthai"] = f"chuyển {nv['vatpham']} lên hành trang 1"
            return None
        diachi = self._timdoituongxungquanh(nv["npc"])
        manpc = f"{moitruong.get_iddoituong(diachi):x}#" if diachi else ""
        lenhgive = taolenhgiao(manpc, [(iddoituong, min(nv["soluong"], max(1, moitruong.get_soluongvatphamhanhtrang(vitri) or 1)))], 0)[0]
        return self._noichuyen(s, nv, nv["npc"], [f"give:{lenhgive}"], f"giao {nv['vatpham']}", bandomonphai)

    def _buocmuahang(self, s, nv):
        # Tới cửa hàng (tên riêng hoặc danh hiệu), tra ô / giá theo tên món trong hàng đã nhớ (chưa có thì mở cửa hàng đọc 1 lần) rồi mua
        # thẳng bằng lệnh buy, không để cửa sổ cửa hàng mở
        loaicuahang, idbando = phantichcuahang(nv.get("cuahang") or CHUTIEMTAPHOA)
        moitruong = self.moitruong
        s["trangthai"] = f"mua {nv['vatpham']} ở {loaicuahang} ({laytenbando(idbando)})"
        diachi = self._timdoituongxungquanh(loaicuahang) if moitruong.get_idbandohientai() == idbando else None
        if not diachi:
            _, yeucau = self._tinpc(s, loaicuahang, idbando, is_chibandogoiy = True)
            return yeucau
        if moitruong.get_khoangcach(diachi) > KHOANGCACHNOICHUYEN:
            x, y = moitruong.get_toado(diachi)
            return self._dentoi(s, idbando, x, y, loaicuahang)
        if self._mocuahang:
            s["trangthai"] = f"đọc hàng của {loaicuahang}"
            return None
        tra = self._sovitri.timhang(idbando, loaicuahang, nv["vatpham"])
        if not tra:
            # Chưa biết hàng (hoặc lần đọc cũ không có món này): mở cửa hàng đọc lại, tối đa SOLANTHUSUMON lần
            khoa = f"{nv['luot']}|{nv['vatpham']}|mocuahang"
            solan, _ = s["thu"].get(khoa, (0, 0.))
            ketqua = self.get_ketquamocuahang(idbando, loaicuahang)
            if solan and ketqua and ketqua[0]:
                self._ketthucsumon(f"{loaicuahang} ở {laytenbando(idbando)} không bán {nv['vatpham']}")
                return None
            if solan >= SOLANTHUSUMON:
                self._ketthucsumon(f"mở cửa hàng {loaicuahang} {solan} lần không được (xem menu trong log [CỬA HÀNG])")
                return None
            s["thu"][khoa] = (solan + 1, time.time())
            self.batdau_mocuahang(diachi)
            return None
        o, gia = tra
        khoa = f"{nv['luot']}|{nv['vatpham']}|mua"
        solan, luc = s["thu"].get(khoa, (0, 0.))
        if time.time() - luc < THOIGIANCHONHIEMVUDOI:
            s["trangthai"] = f"chờ mua {nv['vatpham']}"
            return None
        if solan >= SOLANTHUSUMON:
            self._ketthucsumon(f"mua {nv['vatpham']} (ô {o}, giá {gia}) {solan} lần không được")
            return None
        moitruong.action_ngatdichuyen()
        nganquy = (moitruong.get_nganluong() or 0) - NGANLUONGGIULAI
        if not self._muavatpham(moitruong.get_iddoituong(diachi), o, nv["soluong"] - self._demvatpham(nv["vatpham"]), gia, nv["vatpham"], nganquy):
            self._ketthucsumon(f"không đủ ngân lượng mua {nv['vatpham']} ({gia} lượng, chừa {NGANLUONGGIULAI})")
            return None
        s["thu"][khoa] = (solan + 1, time.time())
        s["trangthai"] = f"mua {nv['vatpham']} (ô {o}, giá {gia})"
        print(f"[SƯ MÔN] Mua {nv['vatpham']} ở {moitruong.get_tendoituong(diachi)}: ô {o}, giá {gia}")
        return None

    def _buocbatyeuquai(self, s, nv):
        moitruong = self.moitruong
        if not self._demvatpham(DAYCANKHON):
            # Hết dây: về Chủ Tiệm Tạp Hóa ở Tân Thủ Thôn mua như món Mua sắm
            return self._buocmuahang(s, {"vatpham": DAYCANKHON, "soluong": SOLUONGMUADAYCANKHON, "cuahang": CHUTIEMTAPHOA, "luot": nv["luot"]})
        idbando = timbandotheoten(nv.get("bando"))
        if not idbando:
            self._ketthucsumon(f"không rõ bắt {nv['quai']} ở bản đồ nào: {nv['mota']}")
            return None
        nhan = f"bắt {nv['quai']}"
        if moitruong.get_idbandohientai() != idbando:
            return self._dentoi(s, idbando, None, None, nhan)
        diachi = self._timdoituongxungquanh(nv["quai"], is_quai = True)
        if not diachi:
            s["trangthai"] = f"tìm {nv['quai']} để bắt"
            return self._diquadiem(s, f"quai|{nv['quai']}|{idbando}", idbando, self._laydiemtimquai(nv["quai"], idbando), f"tìm {nv['quai']}")
        if moitruong.get_khoangcach(diachi) > KHOANGCACHBATBAOTHU:
            x, y = moitruong.get_toado(diachi)
            return self._dentoi(s, idbando, x, y, nhan)
        # Tỉ lệ bắt thấp: cứ dùng tới khi được, cách nhau ít nhất 0.25s
        if time.time() - s["lucbat"] >= GIANCACHBATBAOTHU:
            moitruong.action_ngatdichuyen()
            moitruong.action_thucthicaulenh(LENHBATBAOTHU.format(moitruong.get_iddoituong(diachi)))
            s["lucbat"] = time.time()
        s["trangthai"] = f"đang bắt {nv['quai']}"
        return None
