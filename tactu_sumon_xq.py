# Nhiệm vụ sư môn (bật tay trên giao diện, tới khi NPC báo đã làm đủ 20 lần trong ngày): mỗi lượt đọc nhiệm vụ trong cửa sổ nhiệm vụ (nhiemvu_xq) rồi làm bước
# kế tiếp, nhiệm vụ đổi thì bước đổi theo (không nhớ quy trình riêng nên bot tắt / bật lại giữa chừng vẫn làm tiếp được):
#   không có nhiệm vụ   : tới NPC giao nhiệm vụ (Côn Luân dưới 60: Văn Xương Chân Quân), "2. Tiếp nhận nhiệm vụ" -> "1. Tiếp nhận"
#                         (tallk <id># quest -> tallk <id># accept_quest)
#   đã xong (Xong) / đủ tiến độ: về NPC giao, "Hoàn thành nhiệm vụ" (tallk <id># task_info)
#   Đi tìm Thạch Sư     : tới Thạch Sư nhận việc theo menu: Thu mua accept_task.1 -> .11, Thu thập accept_task.2 -> .21
#   Thu thập            : tới bản đồ trong mô tả đánh mọi quái (quái có hạn, giết con khác thì con cần mới ra), nhặt vật phẩm; đủ số thì Hồi môn phái, tới Thạch Sư chọn "Hoàn thành" theo menu
#   Mua sắm             : tới cửa hàng trong mô tả (NPC các nước có tên riêng, tên cửa hàng là danh hiệu), tra ô / giá theo tên món
#                         (chưa biết thì mở cửa hàng đọc 1 lần rồi đóng), mua bằng lệnh buy; đủ thì đưa lên hành trang 1, give Thạch Sư
#   Thăm viếng          : tới NPC (chưởng môn / quân vương, bảng BANDOTHAMVIENG), "Hoàn thành nhiệm vụ"
#   Luyện tập / Du lịch : farm theo lộ trình điểm đánh của nhân vật tới khi xong
#   Bắt yêu quái        : có Dây Càn Khôn (hết thì về Chủ Tiệm Tạp Hóa mua), tới bản đồ, đứng gần quái dùng "pf2 51 <id>#"
#                         cách nhau ít nhất 0.25s tới khi bắt được
# Hội thoại NPC: "look <id>#" mở menu, mỗi bước chọn lựa chọn trong menu vừa hiện có lệnh đúng từ khoá (số info / task đổi theo máy chủ),
# menu không có thì gửi thẳng lệnh. Gửi xong chờ nhiệm vụ đổi, quá SOLANTHUSUMON lần không đổi thì dừng, báo Telegram.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import os
import re
import time

from hangso_xq import *
from bando_xq import timduongbando, CAPQUAI_MAP, BANDOCONG_MAP
from dexuatlotrinh_xq import taiviquaibando, dexuatlotrinh, dexuatlotrinhdo, layvungtoiduoc, SOLANTHAYQUAITOITHIEU, TENMAUDO, CANHKHOIDO
from giaodo_xq import taolenhgiao
from nhiemvu_xq import *
from nhiemvu_xq import _laynpcbandonho as nhiemvu_layvitri_soluong
from thongbao_xq import baosuco
from tienich_xq import phatam, tailotrinhmau as util_tailotrinhmau, luulotrinhmau as util_luulotrinhmau

DAYCANKHON = "Dây Càn Khôn"
# Hết Dây Càn Khôn thì về Chủ Tiệm Tạp Hóa ở Tân Thủ Thôn mua chừng này (ô / giá tra theo tên trong cửa hàng)
SOLUONGMUADAYCANKHON = 30
# Mở cửa hàng (action_xulymocuahang): quá chừng này giây kể từ lúc bấm NPC mà cửa sổ chưa hiện thì coi như không mở được
THOIGIANMOCUAHANGTOIDA = 10.
THOIGIANCHOLIST = 3.
LENHBATBAOTHU = "pf2 51 {:x}#"
GIANCACHBATBAOTHU = 0.3
KHOANGCACHBATBAOTHU = 3.
# Bắt chừng này lần chưa được thì đánh thường 1 cái cho giảm máu (TacTuSuMon._danhgiammau): chỉ đánh khi máu từ NGUONGMAUDUNGDANH% trở
# lên và máu dự kiến sau cú đánh (sức đánh đã đo x1.5) còn trên NGUONGMAUANTOAN%; đánh rồi quá THOIGIANCHODANH giây máu chưa tụt thì thôi
SOLANBATTRUOCKHIDANH = 10
NGUONGMAUDUNGDANH = 40
NGUONGMAUANTOAN = 15
THOIGIANCHODANH = 3.
KHOANGCACHNOICHUYEN = 3.
# Gần NPC dưới chừng này ô mà không đi lại gần hơn được (vật cản) thì vẫn thử nói chuyện
KHOANGCACHNOICHUYENKET = 6.
# Gửi xong hội thoại chừng này giây mà nhiệm vụ chưa đổi thì thử lại, quá SOLANTHUSUMON lần thì dừng
THOIGIANCHONHIEMVUDOI = 4.
# Nhận nhiệm vụ: cửa sổ nhiệm vụ có lúc cập nhật chậm (Luyện tập), chờ lâu hơn trước khi gửi lại
THOIGIANCHONHANNHIEMVU = 12.
# Cửa sổ nhiệm vụ có tên mà mô tả còn trống (máy chủ chưa gửi xong): chờ tối đa chừng này giây rồi mới coi là nhiệm vụ chưa biết
THOIGIANCHOMOTANHIEMVU = 30.
GIANCACHXINNHIEMVU = 10.
# Luyện tập / Du lịch tự chọn bãi: quái cấp thấp nhất >= cấp - CAPTHAPHONTOIDA, cấp cao nhất <= cấp + CAPCAOHONTOIDA
CAPTHAPHONTOIDA = 12
CAPCAOHONTOIDA = 3
# Bãi train người dùng chọn theo cấp (ưu tiên hơn tự chọn; các bãi này game không ghi cấp quái): (từ cấp, tới dưới cấp, các tầng).
# Lấy tầng đầu tiên có lộ trình mẫu, không có thì tầng đầu
BANDOTRAINTHEOCAP = (
    (70, 80, (311, 312, 313)),             # Linh Cốc Động
    (80, 90, (291, 292, 293)),             # Khốn Ma Trận
    (90, 100, (331, 332, 333, 334, 335)),  # Hầm Vạn Nhân
    (100, 1000, (291,)),                   # Khốn Ma Trận 1 (người dùng chọn cho cấp 100)
)
SOLANTHUSUMON = 3
# Mỗi bước hội thoại cách nhau, chờ menu trả lời tối đa
GIANCACHBUOCHOITHOAI = 0.8
THOIGIANCHOMENU = 2.
GIANCACHHOIMONPHAI = 15.
SOLANHOIMONPHAI = 3
# Điểm khám phá / tuần tra: tới gần chừng này ô, hoặc quá chừng này giây thì sang điểm kế
KHOANGCACHTOIDIEM = 4.
THOIGIANMOIDIEM = 45.
# Đi mãi không gần điểm thêm (chỗ không đi được) chừng này giây thì thôi; đã cách dưới KHOANGCACHGANDUOC ô thì coi như tới
THOIGIANKHONGNHICH = 10.
KHOANGCACHGANDUOC = 12.
# Truy Sát / Tuần Sơn: tới toạ độ trong nhiệm vụ thì đứng chờ chừng này giây cho đối thủ hiện rồi mới đi dò quanh
THOIGIANCHODIEMNHIEMVU = 15.
# Dò quanh toạ độ trong nhiệm vụ theo lưới vật cản (_laydiemdoquanh): trong chừng này ô quanh toạ độ, khối cạnh chừng này ô mỗi khối 1 điểm
BANKINHDOQUANH = 35
CANHDOQUANH = 14
THOIGIANSUMONTOIDA = 4 * 3600.
GIANCACHGHIVITRI = 3.
THOIGIANCHOSAUCHUYENBANDO = 3.
# Bản đồ ghi lại ô nhân vật đã đứng (SoVitri.ghidadi): thành 7 nước + Chu và bản đồ môn phái
# Bản đồ đi tuần / đuổi quái bằng tự động tìm đường của game (TacTuSuMon._is_dioo): 7 nước, Chu, môn phái
BANDOTIMDUONGs = set(DIEMNGOAITHANH_MAP) | {BANDO_CHUQUOC} | set(BANDOMONPHAI.values())
BANDOGHIDADIs = {BANDO_TEQUOC, BANDO_HANQUOC, BANDO_TRIEUQUOC, BANDO_NGUYQUOC, BANDO_TANQUOC, BANDO_SOQUOC, BANDO_YENQUOC, BANDO_CHUQUOC} \
                | set(BANDOMONPHAI.values())


class TacTuSuMon:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_sumon(self):
        if self._sumon:
            return
        self._sumon = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "thu": {}, "hoithoai": None, "lucmonphai": 0.,
                       "solanmonphai": 0, "khampha": None, "lucbat": 0., "luotdangnhan": 0, "soluotxong": 0, "tenquai": set(),
                       "vatphamnhat": set(), "dabao": set(), "kinhnghiem": {}}
        self.moitruong._inlog("[SƯ MÔN] Bắt đầu làm nhiệm vụ sư môn")
        # Sư môn tự đi một mình: Theo sau đang bật thì bot chỉ chọn quái quanh người được theo sau và bị kéo về phía họ (Kim Tinh
        # trước mặt không đánh); tạm tắt, dừng sư môn thì trả lại
        self._doituychonsumon(self._sumon, "_is_tudongtheosau", False, "Theo sau")
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
            solan = self._sumon.get("solanhomnay")
            return f"Sư môn{f' (hôm nay {solan}/{SOLANSUMONTOIDA} lần)' if solan is not None else ''}: {self._sumon['trangthai']}"
        return self._ketquasumon or ""

    def thietlap_npcgiaosumon(self, ten):
        self._sumon_npcgiao = (ten or "").strip()
        self.moitruong._inlog(f"[SƯ MÔN] NPC giao nhiệm vụ: {self._sumon_npcgiao or '(mặc định theo môn phái)'}")

    def _laynpcgiaosumon(self):
        return self._sumon_npcgiao or NPCSUMONMACDINH.get(self.moitruong.get_tenmonphai(), ("", ""))[0]

    def _laytenmuctieutancongs(self):
        # Danh sách tên được đánh: Thu thập / bãi train tự chọn thì đánh mọi quái (rỗng, is_train), Hiệp Trợ / Truy Bắt... thì chỉ con
        # nhiệm vụ, còn lại là danh sách của người dùng
        if self._sumon and self._sumon["chedo"] == "danhquai" and (self._sumon["tenquai"] or self._sumon.get("is_train")):
            return self._sumon["tenquai"]
        # Lăng Ly Sơn ở chỗ boss: đánh mọi quái (boss và quái quanh nó)
        if self.get_is_langlysondanhquai():
            return ()
        # Sư Gia: chỉ đánh tội phạm của nhiệm vụ
        if self.get_is_sugiadanhquai() and self._sugia["tenquai"]:
            return self._sugia["tenquai"]
        return self._tenmuctieutancongs

    def _layvatphamnhatsumon(self):
        return self._sumon["vatphamnhat"] if self._sumon and self._sumon["chedo"] == "danhquai" else ()

    # Ô cần cho đánh quái: (thuộc tính, giá trị cần, tên trên giao diện)
    _TUYCHONDANHQUAI = (("_is_tudongsudungkynang", True, "Tự động sử dụng kỹ năng"), ("_is_tudongtimkiemmuctieu", True, "Tự tìm mục tiêu"),
                        ("_is_chidanhnguoichoi", False, "Chỉ đánh người chơi"))

    def _batdanhquai(self, s):
        # Bước cần đánh quái (Luyện tập, Du lịch, Thu thập): ô nào người dùng quên bật (hoặc đang "Chỉ đánh người chơi") thì đổi giúp,
        # nhớ giá trị cũ để trả lại khi dừng sư môn
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            self._doituychonsumon(s, thuoctinh, giatri, ten)

    def _doituychonsumon(self, s, thuoctinh, giatri, ten):
        # Đổi 1 ô thiết lập cho sư môn, nhớ giá trị cũ (s["tuychoncu"]) để trả lại khi dừng; luuthietlap lưu giá trị cũ này
        if getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self.moitruong._inlog(f"[SƯ MÔN] {'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng sư môn thì trả lại)")

    def _ketthucsumon(self, loi = None, thongbao = None):
        s = self._sumon
        self._sumon = None
        self._yeucautudo = None
        # Trả lại các ô đánh quái bot đã tự đổi
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        noidung = thongbao or (f"❌ Sư môn dừng: {loi}" if loi else "✅ Xong nhiệm vụ sư môn")
        if s and s["soluotxong"]:
            noidung += f" (phiên này trả {s['soluotxong']} lượt)"
        self.moitruong._inlog(f"[SƯ MÔN] {noidung}")
        self._ketquasumon = f"{time.strftime('%H:%M')} {noidung}"
        baosuco(self.moitruong, "sumon", noidung, khoa = s["batdau"] if s else None, giancach = 0.)
        phatam("Lỗi nhiệm vụ sư môn" if loi else "Kết thúc nhiệm vụ sư môn")

    def _baomotlan(self, s, khoa, noidung):
        # Báo Telegram 1 lần cho mỗi việc cần người dùng làm (mua tay, thêm luật...), bot vẫn chờ
        if khoa not in s["dabao"]:
            s["dabao"].add(khoa)
            self.moitruong._inlog(f"[SƯ MÔN] {noidung}")
            baosuco(self.moitruong, "sumon", noidung, khoa = f"{s['batdau']}|{khoa}", giancach = 0.)

    # --- Vị trí NPC / quái -------------------------------------------------------------------------------------------------------
    def action_ghivitridoituong(self):
        # Ghi lại NPC / quái đang thấy (tên, bản đồ, toạ độ) cho sư môn tìm về sau, kể cả khi không làm sư môn. Ở bản đồ thành / môn phái
        # thì mỗi lượt ghi cả ô nhân vật đang đứng (ô đi được, làm dữ liệu điểm di chuyển về sau)
        idbando = self.moitruong.get_idbandohientai()
        # Vừa chuyển bản đồ: mã bản đồ đã đổi mà đối tượng / toạ độ còn của bản đồ cũ (từng ghi "Vong Tình Bà Bà" ở Tân Thủ Thôn), chờ
        # ổn định rồi mới ghi
        if time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() < THOIGIANCHOSAUCHUYENBANDO:
            return
        if idbando in BANDOGHIDADIs and self._sovitri._idnguoichoi:
            toado = self.moitruong.get_toado()
            if toado:
                self._sovitri.ghidadi(idbando, int(round(toado[0])), int(round(toado[1])))
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
        self.moitruong._inlog(f"[CỬA HÀNG] Mở cửa hàng {self._mocuahang['tens']} để đọc hàng")
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
            self.moitruong._inlog(f"[CỬA HÀNG] list {mc['manpc']} chưa mở được cửa hàng {mc['tens']}, thử bấm NPC")
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {mc['manpc']}")
            mc["buoc"] = 2
        elif mc["buoc"] == 2:
            if not moitruong.get_noidungcuasotuychon() and now - mc["luc"] < THOIGIANCHOMENU:
                return
            lenhs = moitruong.get_lenhcuasotuychons() if moitruong.get_noidungcuasotuychon() else []
            lenh = next((l for l in lenhs if any(k in l.lower() for k in ("buy", "list", "shop", "trade", "mua"))), None)
            self.moitruong._inlog(f"[CỬA HÀNG] Menu {mc['tens']} {mc['manpc']}: {lenhs} -> {lenh or 'không có lựa chọn mua'}")
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
        self.moitruong._inlog(f"[CỬA HÀNG] {mc['tens']}: {mota}")

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
            elif not any(is_trungten(t, moitruong.get_tendoituong(diachi)) or is_trungten(t, moitruong.get_danhhieudoituong(diachi))
                         for t in tenthaythe(ten)[0]):
                continue
            khoangcach = moitruong.get_khoangcach(diachi)
            if khoangcachtot is None or khoangcach < khoangcachtot:
                tot, khoangcachtot = diachi, khoangcach
        return tot

    def _layquairieng(self, tens):
        # Quái nhiệm vụ riêng mang ID người chơi trong tên ("Cuồng Đồ (30)", "Quan Viên Đào Tẩu (29)", "Tùy Tùng (32)"), tên trong nhiệm vụ
        # có thể khác ("Kẻ Khả Nghi" là Cuồng Đồ): đánh mọi con mang ID mình, con khớp tên mà mang ID người khác thì bỏ.
        # -> (tên được đánh, địa chỉ con mang ID mình gần nhất hoặc None)
        moitruong = self.moitruong
        duoi = f"({moitruong.get_idnguoichoi()})"
        tens = [chuanhoaten(t) for t in tens if t]
        kq, gannhat = set(), None
        for d in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(d) or moitruong.get_is_nguoichoi(d):
                continue
            ten = moitruong.get_tendoituong(d) or ""
            if re.search(r"\(\d+\)\s*$", ten):
                if not ten.rstrip().endswith(duoi):
                    continue
                if moitruong.get_is_cothetancong(d) and (gannhat is None or moitruong.get_khoangcach(d) < moitruong.get_khoangcach(gannhat)):
                    gannhat = d
            elif not any(t in chuanhoaten(ten) for t in tens):
                continue
            kq.add(ten)
        return kq, gannhat

    def _thumucgame(self):
        try:
            return os.path.dirname(self.moitruong.gamemodule.filename)
        except Exception:
            return None

    # --- Di chuyển ---------------------------------------------------------------------------------------------------------------
    def _dentoi(self, s, idbando, x, y, nhan, khoangcach = 2., is_dioo = True):
        # Đi tới (x, y) ở bản đồ idbando (x None: chỉ cần tới bản đồ). Bản đồ môn phái ở xa thì Hồi môn phái ("dGludmF0 1").
        # is_dioo False: dùng tự động tìm đường của game (đi tuần / đuổi quái ngoài thành, xem _is_dioo)
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
                    self.moitruong._inlog(f"[SƯ MÔN] Hồi môn phái để tới {nhan}")
                    moitruong.action_ngatdichuyen()
                    moitruong.action_thucthicaulenh("dGludmF0 1")
                    s["lucmonphai"] = now
                    s["solanmonphai"] += 1
                self._capnhatbuocdichuyen(f"Sư môn: Hồi môn phái tới {nhan}")
                return None
            buoc = self._lapbuocditoibando(idbando, is_hoithanhphu = True, toadodich = (x, y) if x is not None else None)
            if buoc["loai"] != "toinoi":
                return self._thuchienbuocditoibando(buoc, idbando, (x, y) if x is not None else None, f"[SƯ MÔN] {nhan}")
        if x is None:
            return None
        s["trangthai"] = f"tới {nhan} ({x}, {y})"
        self._capnhatbuocdichuyen(f"Sư môn: tới {nhan} ({x}, {y}) ở {laytenbando(idbando)}")
        # is_dioo: trong cùng bản đồ đi theo ô (gần thẳng) thay vì tự động tìm đường của game (hay chạy vòng khi vào thành / môn phái)
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": khoangcach, "is_dioo": is_dioo}

    @staticmethod
    def _is_dioo(idbando, khoa = ""):
        # Bản đồ 7 nước, Chu, môn phái (BANDOTIMDUONGs): đi tới NPC (nhận / trả nhiệm vụ, trong thành) thì đi thẳng theo ô (tìm đường của
        # game chạy vòng); đi tuần / đuổi quái (ngoài thành, nhiều cọc gỗ / vật cản) thì dùng tự động tìm đường kẻo kẹt tới đứt kết nối
        # (người dùng dặn)
        return idbando not in BANDOTIMDUONGs or khoa.startswith("npc|")

    def _diquadiem(self, s, khoa, idbando, diems, nhan, chodiemdau = 0.):
        # Đi lần lượt qua các điểm (tìm NPC / quái chưa biết chỗ, tuần tra chờ quái): tới gần hoặc quá THOIGIANMOIDIEM thì sang điểm kế.
        # chodiemdau: tới điểm đầu (toạ độ trong nhiệm vụ) thì đứng chờ chừng này giây cho quái hiện rồi mới đi
        if not diems:
            return self._dentoi(s, idbando, None, None, nhan)
        kp = s["khampha"]
        if not kp or kp["khoa"] != khoa:
            kp = s["khampha"] = {"khoa": khoa, "i": 0, "luc": time.time()}
        if self.moitruong.get_idbandohientai() == idbando:
            # Điểm không thông với chỗ đứng (bên kia sông / vách, ngoài bản đồ; kéo về ô đi được gần nhất vẫn không tới được) thì bỏ luôn,
            # không đứng kẹt THOIGIANKHONGNHICH giây mỗi điểm. Mọi điểm đều không thông (lưới đọc sai?) thì đi như cũ
            vung = self._layvungtoiduoc(idbando)
            if vung:
                for buoc in range(len(diems)):
                    if self.moitruong.get_oditduocganhat(*diems[(kp["i"] + buoc) % len(diems)]) in vung:
                        if buoc:
                            self.moitruong._inlog(f"[SƯ MÔN] {nhan}: bỏ {buoc} điểm không đi tới được")
                            kp["i"] += buoc
                            kp["luc"] = time.time()
                            for k in ("ganhat", "lucgan", "datoi"):
                                kp.pop(k, None)
                        break
            # Điểm rơi vào vật cản thì đo theo ô đi được gần nhất (nơi đi cũng nhắm ô đó), tới đó là tới
            x, y = self.moitruong.get_oditduocganhat(*diems[kp["i"] % len(diems)])
            # Điểm không tới được (toạ độ trong nhiệm vụ có khi lệch vào chỗ không đi được, nhất là Tuần Sơn): THOIGIANKHONGNHICH giây không
            # gần thêm thì thôi, đã cách dưới KHOANGCACHGANDUOC ô thì coi như tới (vẫn đứng chờ điểm đầu), xa hơn thì sang điểm kế
            khoangcach = self.moitruong.get_khoangcachdiem(x, y)
            if khoangcach < kp.get("ganhat", float("inf")) - 1:
                kp["ganhat"], kp["lucgan"] = khoangcach, time.time()
            is_ket = time.time() - kp.setdefault("lucgan", time.time()) > THOIGIANKHONGNHICH
            is_toi = khoangcach <= KHOANGCACHTOIDIEM or kp.get("datoi") or (is_ket and khoangcach <= KHOANGCACHGANDUOC)
            if is_toi and kp["i"] == 0 and chodiemdau:
                kp["datoi"] = True
                kp.setdefault("luctoi", time.time())
                if time.time() - kp["luctoi"] < chodiemdau:
                    s["trangthai"] = f"{nhan}: chờ ở gần ({x}, {y})"
                    return None
            if is_toi or is_ket or time.time() - kp["luc"] > THOIGIANMOIDIEM:
                kp["i"] += 1
                kp["luc"] = time.time()
                for k in ("ganhat", "lucgan", "datoi"):
                    kp.pop(k, None)
        else:
            kp["luc"] = time.time()
        x, y = diems[kp["i"] % len(diems)]
        return self._dentoi(s, idbando, x, y, f"{nhan} (điểm {kp['i'] % len(diems) + 1}/{len(diems)})", khoangcach = 1.,
                            is_dioo = self._is_dioo(idbando, khoa))

    def _laydiemtimquai(self, tenquai, idbando):
        # Chỗ từng thấy quái này, rồi điểm đi tuần của bản đồ (_laydiemtrain: lộ trình mẫu / tự đề xuất / lộ trình dò theo lưới vật cản)
        vitri = self._sovitri.timquai(tenquai, idbando)
        return ([tuple(vitri)] if vitri else []) + self._laydiemtrain(idbando)

    def _laylotrinhdo(self, idbando):
        # Chưa có lộ trình mẫu / đủ vị trí quái: lộ trình dò phủ vùng đi được nối với chỗ đứng (lưới vật cản của client, tránh cổng / vùng
        # cấm) như nút "Lộ trình dò", lưu thành mẫu TENMAUDO (lần sau dùng lại, hiện trên bảng Lộ trình mẫu) nhưng không nạp vào lộ trình
        # của nhân vật. Chỉ tính được khi đang ở bản đồ đó. -> [(x, y), ...] hoặc []
        diems = self._taodiemdo(idbando)
        if len(diems) < 2:
            return []
        lotrinhmau = util_tailotrinhmau()
        lotrinhmau[str(idbando)] = [m for m in lotrinhmau.get(str(idbando), []) if m.get("ten") != TENMAUDO]             + [{"ten": TENMAUDO, "diem": [[x, y] for x, y in diems]}]
        util_luulotrinhmau(lotrinhmau)
        self.moitruong._inlog(f"[SƯ MÔN] {laytenbando(idbando)} chưa có lộ trình mẫu: tạo lộ trình dò {len(diems)} điểm")
        return [tuple(d) for d in diems]

    def _taodiemdo(self, idbando, tam = None, bankinh = None, canh = CANHKHOIDO):
        # Điểm dò theo lưới vật cản (dexuatlotrinhdo): cả vùng đi được nối với chỗ đứng, hoặc trong bankinh ô quanh tam. Tránh cổng / điểm
        # xuất hiện và vùng cấm. Chỉ tính được khi đang ở bản đồ đó. -> [(x, y), ...] hoặc []
        if self.moitruong.get_idbandohientai() != idbando:
            return []
        luoi = self.moitruong.get_luoivatcanbando()
        if not luoi:
            return []
        congs = [(x, y) for _, x, y, _, _ in (BANDOCONG_MAP.get(idbando) or ("", ()))[1]]
        return [tuple(d) for d in dexuatlotrinhdo(luoi, self.moitruong.get_toado(),
                                                  lambda x, y: any(math.dist((x, y), c) < 12 for c in congs) or self._kiemtra_vungcam(x, y),
                                                  canh = canh, tam = tam, bankinh = bankinh)]

    def _laydiemdoquanh(self, idbando, toado):
        # Đi dò quanh toạ độ trong nhiệm vụ (Tuần Sơn, Hiệp Trợ Trị An, Truy Bắt có toạ độ): toạ độ trước (chờ quái hiện), rồi điểm dò dày
        # (khối CANHDOQUANH ô) trong BANKINHDOQUANH ô, chỉ ô thông với chỗ đứng, đi theo quãng đi bộ. Tính 1 lần cho mỗi toạ độ (gọi mỗi
        # lượt). Không tính được (chưa ở bản đồ đó / không đọc được lưới) -> None, nơi gọi dùng vòng quanh cũ
        khoa = (idbando, tuple(toado))
        if khoa not in self._diemdoquanh_cache:
            diems = self._taodiemdo(idbando, tam = tuple(toado), bankinh = BANKINHDOQUANH, canh = CANHDOQUANH)
            if not diems:
                return None
            if len(self._diemdoquanh_cache) > 32:
                self._diemdoquanh_cache.clear()
            self._diemdoquanh_cache[khoa] = [tuple(toado)] + [d for d in diems if d != tuple(toado)]
            self.moitruong._inlog(f"[SƯ MÔN] Dò quanh {tuple(toado)} ở {laytenbando(idbando)}: {len(diems)} điểm theo lưới vật cản")
        return self._diemdoquanh_cache[khoa]

    def _layvungtoiduoc(self, idbando):
        # Các ô đi tới được từ chỗ đứng trên bản đồ hiện tại (lưới vật cản), nhớ theo bản đồ; mình ra ngoài vùng đã nhớ (sang đảo khác /
        # phù) thì tính lại. Không đọc được lưới -> None (không lọc)
        if self.moitruong.get_idbandohientai() != idbando:
            return None
        nho = self._vungtoiduoc_cache
        toado = self.moitruong.get_oditduocganhat(*self.moitruong.get_toado())
        if not nho or nho[0] != idbando or toado not in nho[1]:
            luoi = self.moitruong.get_luoivatcanbando()
            vung = layvungtoiduoc(luoi, toado) if luoi else None
            if not vung:
                return None
            nho = self._vungtoiduoc_cache = (idbando, vung)
        return nho[1]

    def _tinpc(self, s, tennpc, idbandogoiy = None, is_chibandogoiy = False):
        # Đi tìm NPC: thấy rồi -> địa chỉ; chưa thấy -> yêu cầu di chuyển tới chỗ đã biết / đi khắp bản đồ gợi ý. -> (địa chỉ, yêu cầu).
        # is_chibandogoiy: NPC phải ở đúng bản đồ gợi ý (Chủ Tiệm Vũ Khí nước nào cũng có)
        is_dungbando = not is_chibandogoiy or self.moitruong.get_idbandohientai() == idbandogoiy
        diachi = self._timdoituongxungquanh(tennpc) if is_dungbando else None
        if diachi:
            return diachi, None
        # Có bản đồ gợi ý (môn phái...) thì ưu tiên chỗ biết ở đúng bản đồ đó, không có mới lấy chỗ bất kỳ (dữ liệu cũ có thể ghi sai bản
        # đồ lúc vừa chuyển bản đồ: "Vong Tình Bà Bà" ở Tân Thủ Thôn)
        vitri = self._sovitri.timnpc(tennpc, self._thumucgame(), idbandogoiy) if idbandogoiy else None
        if not vitri and not is_chibandogoiy:
            vitri = self._sovitri.timnpc(tennpc, self._thumucgame())
        nhan = tennpc
        if not vitri and is_chibandogoiy:
            # Cửa hàng chưa biết chỗ: tới chỗ cửa hàng khác cùng nước (đứng sát nhau)
            vitri = self._sovitri.timnpccungloai(tennpc, idbandogoiy, self._thumucgame())
            nhan = f"{tennpc} (khu cửa hàng)"
        # Tới chỗ đã biết mà không thấy (NPC đổi chỗ / vị trí sai / chỉ biết khu cửa hàng): đi vòng quanh chỗ đó tìm
        if vitri and not (self.moitruong.get_idbandohientai() == vitri[0] and self.moitruong.get_khoangcachdiem(vitri[1], vitri[2]) <= KHOANGCACHTOIDIEM):
            if not (s["khampha"] and s["khampha"]["khoa"] == f"npc|{tennpc}"):
                return None, self._dentoi(s, vitri[0], vitri[1], vitri[2], nhan)
        idbandogoiy = vitri[0] if vitri else idbandogoiy
        if idbandogoiy:
            if f"timnpc|{tennpc}" not in s["dabao"]:
                s["dabao"].add(f"timnpc|{tennpc}")
                self.moitruong._inlog(f"[SƯ MÔN] Đi vòng tìm {tennpc} ở {laytenbando(idbandogoiy)}: "
                                      + (f"chỗ đã biết {vitri} không thấy NPC" if vitri else
                                         f"không tra được vị trí (thư mục game: {self._thumucgame()}, "
                                         f"{len(nhiemvu_layvitri_soluong(self._thumucgame()))} NPC trên bản đồ nhỏ)"))
            diems = laydiemkhampha(idbandogoiy, vitri[1:] if vitri else None)
            return None, self._diquadiem(s, f"npc|{tennpc}", idbandogoiy, diems, f"tìm {tennpc}")
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
        khoangcach = moitruong.get_khoangcach(diachi)
        if khoangcach > KHOANGCACHNOICHUYEN:
            # NPC đứng sau tường / vật cản (Văn Xương Chân Quân): đã gần dưới KHOANGCACHNOICHUYENKET ô mà THOIGIANKHONGNHICH giây không
            # nhích lại gần được thì thử nói chuyện luôn, không đứng đơ
            gan = s.get("gannpc")
            if not gan or gan[0] != tennpc or khoangcach < gan[1] - 0.5:
                gan = s["gannpc"] = (tennpc, khoangcach, time.time())
            if khoangcach > KHOANGCACHNOICHUYENKET or time.time() - gan[2] < THOIGIANKHONGNHICH:
                x, y = moitruong.get_toado(diachi)
                return self._dentoi(s, moitruong.get_idbandohientai(), x, y, tennpc)
        # Khoá theo cả số lượt đã trả trong phiên: nhận nhiệm vụ (chưa có nhiệm vụ, lượt 0) mỗi lượt là 1 việc mới, không cộng dồn số lần thử
        # từ các lượt trước (từng dừng "nhận ... 3 lần mà không đổi" ngay lần nhận thứ 4 trong phiên dù chưa thử lần nào)
        khoa = f"{s['soluotxong']}|{nv['luot'] if nv else 0}|{nv['loai'] if nv else ''}|{viec}"
        solan, luc = s["thu"].get(khoa, (0, 0.))
        if time.time() - luc < (THOIGIANCHONHIEMVUDOI if nv else THOIGIANCHONHANNHIEMVU):
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
        self.moitruong._inlog(f"[SƯ MÔN] {viec} ở {tennpc} (lần {solan + 1}): {buocs}")
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
        elif buoc == "doithoai":
            # Menu gốc có "Đối thoại" (welcome.99) thì chọn rồi chọn lựa chọn đầu của menu sau (Giám Ngục Quan: Đối thoại -> Hiệp Trợ Trị
            # An); không có thì chọn lựa chọn đầu luôn
            if not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            lenhs = moitruong.get_lenhcuasotuychons() if moitruong.get_noidungcuasotuychon() else []
            lenh = next((l for l in lenhs if l.split("# ", 1)[-1].strip() == "welcome.99"), None)
            if not lenh:
                hoithoai["buocs"][0] = "chon1"
                return
            self.moitruong._inlog(f"[SƯ MÔN] Menu {manpc}: {lenhs} -> {lenh}")
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(lenh)
            hoithoai["buocs"][0] = "chon1"
            hoithoai["luc"] = now
            return
        elif buoc == "hoanthanh":
            # Trả ở Thạch Sư: menu có task_info thì chọn, không thì lựa chọn đầu không phải CLOSE (menu Thạch Sư chỉ 1 lựa chọn); ghi menu
            if not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"] \
                if moitruong.get_noidungcuasotuychon() else []
            lenh = next((l for l in lenhs if l.split("# ", 1)[-1].strip() == "task_info"), None) or (lenhs[0] if lenhs else None)
            self.moitruong._inlog(f"[SƯ MÔN] Menu {manpc}: {lenhs} -> {lenh or 'không có lựa chọn'}")
            if lenh:
                moitruong.xoa_noidungcuasotuychon()
                moitruong.action_thucthicaulenh(lenh)
            hoithoai["buocs"].pop(0)
            hoithoai["luc"] = now
            return
        elif buoc == "nhanviec":
            # Thạch Sư / Thôn Dân / Dược Đồng chỉ có 1 lựa chọn tuỳ máy chủ giao: "1. Thu mua" (accept_task.1) hoặc "1. Thu thập"
            # (accept_task.2); chọn đúng lệnh trong menu rồi "1. Nhận" = accept_task.<n>1. Gửi nhầm loại thì ra nhiệm vụ hỏng ("Nghe nói ở 0")
            if not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            lenhs = moitruong.get_lenhcuasotuychons() if moitruong.get_noidungcuasotuychon() else []
            lenh = next((l for l in lenhs if re.fullmatch(r"accept_task\.\d", l.split("# ", 1)[-1].strip())), None)
            self.moitruong._inlog(f"[SƯ MÔN] Menu {manpc}: {lenhs} -> {lenh or 'không có lựa chọn nhận việc'}")
            if not lenh:
                hoithoai["buocs"] = []
                return
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(lenh)
            hoithoai["buocs"] = [lenh.split("# ", 1)[-1].strip() + "1"] + hoithoai["buocs"][1:]
            hoithoai["dangchomenu"] = True
            hoithoai["luc"] = now
            return
        elif buoc == "ghimenu":
            if not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            self.moitruong._inlog(f"[SƯ MÔN] Menu {manpc}: {moitruong.get_noidungcuasotuychon()[:80]!r} {moitruong.get_lenhcuasotuychons()}")
            hoithoai["buocs"].pop(0)
            hoithoai["luc"] = now
            return
        elif buoc == "trahieptro":
            # Trả Hiệp Trợ Trị An ở Giám Ngục Quan: chọn task_info nếu menu có, không thì lựa chọn đầu (trừ Rời khỏi / CLOSE)
            if not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.upper() != "CLOSE"] if moitruong.get_noidungcuasotuychon() else []
            lenh = next((l for l in lenhs if l.split("# ", 1)[-1].strip() == "task_info"), None) or (lenhs[0] if lenhs else f"tallk {manpc} task_info")
            self.moitruong._inlog(f"[SƯ MÔN] Menu {manpc}: {lenhs} -> {lenh}")
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(lenh)
            hoithoai["buocs"].pop(0)
            hoithoai["luc"] = now
            return
        elif buoc == "thamvieng":
            # Thăm viếng: "Hoàn thành nhiệm vụ" là lệnh "look <id>#" trong menu (log Sở Vương / Chu Vương / Triệu Vương; gửi task_info
            # thì không ăn), có thì chọn, không thì task_info nếu có; quân vương có khi menu gốc là "1. Đối thoại" (welcome.99) -> menu sau
            # mới có "1. Hoàn thành nhiệm vụ" (look <id>#): chọn Đối thoại rồi chọn lựa chọn đầu của menu sau
            if not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            lenhs = moitruong.get_lenhcuasotuychons() if moitruong.get_noidungcuasotuychon() else []
            lenh = next((l for l in lenhs if l.strip().startswith("look ")), None) \
                or next((l for l in lenhs if l.split("# ", 1)[-1].strip() == "task_info"), None)
            buocsau = []
            if not lenh:
                lenh = next((l for l in lenhs if l.split("# ", 1)[-1].strip() == "welcome.99"), None)
                buocsau = ["chon1"] if lenh else []
            # Menu chưa đọc được (trống): gửi lệnh "Hoàn thành nhiệm vụ" quen thuộc là look <id>#
            lenh = lenh or f"look {manpc}"
            self.moitruong._inlog(f"[SƯ MÔN] Menu {manpc}: {lenhs} -> {lenh}")
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(lenh)
            hoithoai["buocs"] = buocsau + hoithoai["buocs"][1:]
            hoithoai["luc"] = now
            return
        elif buoc == "chon1":
            if not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"] if moitruong.get_noidungcuasotuychon() else []
            self.moitruong._inlog(f"[SƯ MÔN] Menu {manpc}: {lenhs} -> chọn {lenhs[0] if lenhs else 'không có'}")
            if lenhs:
                moitruong.xoa_noidungcuasotuychon()
                moitruong.action_thucthicaulenh(lenhs[0])
            hoithoai["buocs"].pop(0)
            hoithoai["luc"] = now
            return
        elif buoc == "demsolan":
            # Lời NPC sau "Tiếp nhận nhiệm vụ" có số lần đã làm hôm nay: đủ SOLANSUMONTOIDA thì không nhận nữa (làm thêm không có thưởng)
            if not moitruong.get_noidungcuasotuychon() and now - hoithoai["luc"] < THOIGIANCHOMENU:
                return
            solan = laysolanhomnay(moitruong.get_noidungcuasotuychon())
            if solan is not None:
                s["solanhomnay"] = solan
                self.moitruong._inlog(f"[SƯ MÔN] Hôm nay đã làm {solan} lần")
                if solan >= SOLANSUMONTOIDA:
                    s["hoithoai"] = None
                    if moitruong.get_is_danghiencuasotuychon():
                        moitruong.set_is_danghiencuasotuychon(False)
                    self._ketthucsumon(thongbao = f"✅ Hôm nay đã làm {solan} lần sư môn (từ {SOLANSUMONTOIDA} lần trở lên không còn thưởng), dừng")
                    return
            hoithoai["buocs"].pop(0)
            return
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
        # Ghi log khi trạng thái sư môn đổi / đang bị chặn (đứng im không rõ lý do thì xem log biết đang chờ gì)
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            moitruong._inlog(f"[SƯ MÔN] Trạng thái: {s['trangthai']}")
        chan = next((ly for ly, co in (("nhân vật chết", moitruong.get_is_nhanvatdachet()), ("đang vận khí", moitruong.get_is_dangvankhi()),
                                       ("đang hội thoại NPC", self.get_is_danghoithoainpc()),
                                       (f"đang về bán (bước {self._trangthaiveban})", self._trangthaiveban != 0)) if co), None)
        if chan:
            if chan != s.get("chan"):
                s["chan"] = chan
                moitruong._inlog(f"[SƯ MÔN] Tạm chờ: {chan}")
            return None
        s["chan"] = None
        if time.time() - s["batdau"] > THOIGIANSUMONTOIDA:
            self._ketthucsumon(f"quá {int(THOIGIANSUMONTOIDA // 3600)} giờ chưa xong")
            return None
        if s["hoithoai"]:
            s["chedo"] = "dichuyen"
            self._xulyhoithoaisumon(s)
            return None

        mucs = moitruong.get_danhsachmucnhiemvu()
        if mucs is None:
            # Chưa đọc được cửa sổ nhiệm vụ (chưa mở bảng nhiệm vụ lần nào): không coi là không có nhiệm vụ mà chạy đi nhận lại
            s["trangthai"] = "chưa đọc được nhiệm vụ: mở bảng nhiệm vụ trong game 1 lần"
            # Lệnh xin danh sách nhiệm vụ của client (chuỗi "quest list" trong xq.exe): thử xin lại, cách nhau GIANCACHXINNHIEMVU giây
            if time.time() - s.get("lucxinnhiemvu", 0.) > GIANCACHXINNHIEMVU:
                s["lucxinnhiemvu"] = time.time()
                moitruong._inlog("[SƯ MÔN] Chưa đọc được cửa sổ nhiệm vụ: gửi \"quest list\"")
                moitruong.action_thucthicaulenh("quest list")
            self._baomotlan(s, "chuadocnhiemvu", "⚠️ Sư môn: chưa đọc được cửa sổ nhiệm vụ, mở bảng nhiệm vụ trong game 1 lần")
            return None
        nv = laynhiemvusumon(mucs)
        # Có tên mà mô tả còn trống (sau "quest list" máy chủ chỉ gửi tên; mô tả gửi khi bấm vào dòng đó = "quest intro <mã>"): xin mô tả,
        # cách nhau GIANCACHXINNHIEMVU giây, chờ tối đa THOIGIANCHOMOTANHIEMVU giây, không coi là nhiệm vụ lạ mà dừng
        if nv and not nv["mucdich"] and not nv["mota"] and not nv["is_xong"]:
            s.setdefault("luctrongmota", time.time())
            ma = moitruong.get_manhiemvu(MUCSUMON)
            if ma and time.time() - s.get("lucxinmota", 0.) > GIANCACHXINNHIEMVU:
                s["lucxinmota"] = time.time()
                moitruong._inlog(f"[SƯ MÔN] Mô tả {nv['ten']} còn trống: gửi \"quest intro {ma[0]} {ma[1]} {ma[2]}\"")
                moitruong.action_thucthicaulenh(f"quest intro {ma[0]} {ma[1]} {ma[2]}")
            if time.time() - s["luctrongmota"] < THOIGIANCHOMOTANHIEMVU:
                s["trangthai"] = f"chờ mô tả nhiệm vụ {nv['ten']}"
                return None
        else:
            s.pop("luctrongmota", None)
        # Lượt đang nhận đổi (trả xong / sang lượt mới): đếm số lượt phiên này đã trả. Giới hạn trong ngày xét lúc nhận nhiệm vụ mới theo
        # số NPC báo (bước "demsolan"); "Lượt thứ" trong tên nhiệm vụ chỉ là thứ tự trong chuỗi (lặp lại), không phải số lần trong ngày
        if s["luotdangnhan"] and (not nv or nv["luot"] != s["luotdangnhan"]):
            s["soluotxong"] += 1
            self.moitruong._inlog(f"[SƯ MÔN] Đã trả lượt {s['luotdangnhan']}")
        s["luotdangnhan"] = nv["luot"] if nv else 0
        # Ghi nhiệm vụ đọc được mỗi khi đổi (xem log biết bot đang làm bước nào)
        motanv = motanhiemvu(nv)
        if motanv != s.get("motanv"):
            s["motanv"] = motanv
            self.moitruong._inlog(f"[SƯ MÔN] Nhiệm vụ: {motanv}")
        s["tenquai"], s["vatphamnhat"], s["is_train"] = set(), set(), False
        s["chedo"] = "dichuyen"

        npcgiao = self._laynpcgiaosumon()
        bandomonphai = BANDOMONPHAI.get(moitruong.get_tenmonphai())
        if not nv:
            s["trangthai"] = "nhận nhiệm vụ"
            return self._noichuyen(s, nv, npcgiao, ["look", "quest", "demsolan", "accept_quest"], "nhận nhiệm vụ", bandomonphai)
        loai = nv["loai"]
        # Hiệp Trợ Trị An xong (kể cả "(Xong)") trả ở Giám Ngục Quan của nước đó, không phải NPC giao sư môn
        if loai == LOAI_HIEPTRO:
            return self._buochieptro(s, nv)
        if loai == LOAI_TRUYBAT:
            return self._buoctruybat(s, nv)
        # Tỷ thí thắng rồi mà còn ở đấu trường riêng (không có trong dữ liệu cổng, không chạy về được): nói chuyện với đối thủ chọn
        # "1. Rời khỏi đấu trường" trước
        if loai == LOAI_TYTHI and (nv["is_xong"] or is_dutiendo(nv)) and moitruong.get_idbandohientai() not in BANDOCONG_MAP:
            return self._roidautruong(s, nv)
        if nv["is_xong"] or (loai in (LOAI_LUYENTAP, LOAI_DULICH) and (is_dutiendo(nv) or self._is_dukinhnghiem(s, nv))) \
                or (loai == LOAI_TUANSON and is_dutiendo(nv)):
            return self._noichuyen(s, nv, npcgiao, ["look", "task_info"], "trả nhiệm vụ", bandomonphai)
        if loai == LOAI_DENTIM:
            return self._noichuyen(s, nv, nv["npc"], ["look", "nhanviec"], "nhận việc", bandomonphai)
        if loai == LOAI_THUTHAP:
            return self._buocthuthap(s, nv, bandomonphai)
        if loai == LOAI_THUMUA:
            return self._buocthumua(s, nv, bandomonphai)
        if loai == LOAI_THAMVIENG:
            idbando = next((b for ten, b in BANDOTHAMVIENG.items() if is_trungten(ten, nv["npc"]) or is_trungten(nv["npc"], ten)), None) \
                      or timbandotheoten(nv.get("bando"))
            return self._noichuyen(s, nv, nv["npc"], ["look", "thamvieng"], "thăm viếng", idbando)
        if loai in (LOAI_LUYENTAP, LOAI_DULICH):
            tiendo = f" ({nv['tiendo'][0]}/{nv['tiendo'][1]})" if nv["tiendo"] else ""
            if self._diemdanhxungquanhs:
                # Nhân vật có lộ trình điểm đánh riêng: farm theo lộ trình đó
                s["chedo"] = "farm"
                self._batdanhquai(s)
                s["trangthai"] = f"{TENLOAI[loai]}: farm theo lộ trình{tiendo}"
                return None
            return self._buoctrain(s, f"{TENLOAI[loai]}{tiendo}")
        if loai == LOAI_HIEPTRO:
            return self._buochieptro(s, nv)
        if loai == LOAI_TUANSON:
            return self._buoctuanson(s, nv, bandomonphai)
        if loai == LOAI_TYTHI:
            if is_dutiendo(nv):
                return self._noichuyen(s, nv, npcgiao, ["look", "task_info"], "trả tỷ thí", bandomonphai)
            return self._buoctythi(s, nv)
        if loai == LOAI_BATYEUQUAI:
            # Bắt được thì quái thành bảo thú trong danh sách (cửa sổ nhiệm vụ không báo Xong): về trả ngay
            if any(chuanhoaten(ten) == chuanhoaten(nv["quai"]) for ten in moitruong.get_danhsachtenbaothugiangho()):
                return self._noichuyen(s, nv, npcgiao, ["look", "task_info"], f"nộp {nv['quai']}", bandomonphai)
            return self._buocbatyeuquai(s, nv)
        self._ketthucsumon(f"chưa biết làm nhiệm vụ này: {nv['ten']} – {nv['mucdich']}")
        return None

    def _chonbandotrain(self):
        # Bãi hợp cấp cho Luyện tập / Du lịch (CAPQUAI_MAP: cấp quái theo bản đồ, từ file game): quái không thấp hơn cấp - CAPTHAPHONTOIDA,
        # không cao hơn cấp + CAPCAOHONTOIDA, không phải phó bản, phù tới được. Ưu tiên phù thẳng tới, có sẵn điểm đánh (lộ trình mẫu /
        # vị trí quái đã thấy), quái cấp cao nhất. Không có bãi nào thì lấy bãi có cấp quái gần nhất. -> id bản đồ hoặc None
        capdo = self.moitruong.get_capdonhanvat() or 0
        lotrinhmau = util_tailotrinhmau()
        for captu, capden, tangs in BANDOTRAINTHEOCAP:
            if captu <= capdo < capden:
                return next((t for t in tangs if str(t) in lotrinhmau), tangs[0])
        ungviens = []
        for idbando, (captoithieu, captoida) in CAPQUAI_MAP.items():
            phuongan = layphuongandichuyen(idbando)
            if idbando in BANDOPHOBANs or idbando not in BANDOCONG_MAP or not phuongan:
                continue
            is_hopcap = captoithieu >= capdo - CAPTHAPHONTOIDA and captoida <= capdo + CAPCAOHONTOIDA
            is_codiem = str(idbando) in lotrinhmau or sum(taiviquaibando(idbando).values()) >= SOLANTHAYQUAITOITHIEU
            ungviens.append(((not is_hopcap, abs((captoithieu + captoida) / 2 - capdo) if not is_hopcap else 0, phuongan[3] > 0,
                              not is_codiem, -captoida), idbando))
        return min(ungviens)[1] if ungviens else None

    def _laydiemtrain(self, idbando):
        # Điểm đi tuần ở bãi train / bản đồ Thu thập: lộ trình mẫu, không có thì đề xuất từ vị trí quái đã thấy, không nữa thì lộ trình
        # dò theo lưới vật cản (_laylotrinhdo), cuối cùng mới đi vòng quanh tâm bản đồ (tránh cổng; hay lọt chỗ không đi được)
        for mau in util_tailotrinhmau().get(str(idbando), []):
            diems = [(int(d[0]), int(d[1])) for d in mau.get("diem") or [] if len(d) < 3 or int(d[2]) == idbando]
            if diems:
                return diems
        demo = taiviquaibando(idbando)
        if sum(demo.values()) >= SOLANTHAYQUAITOITHIEU:
            diems, _ = dexuatlotrinh(demo)
            if diems:
                return [tuple(d) for d in diems]
        return self._laylotrinhdo(idbando) or laydiemkhampha(idbando)

    def _buoctrain(self, s, nhan):
        # Luyện tập / Du lịch khi nhân vật chưa có lộ trình điểm đánh: tự chọn bãi hợp cấp (giữ nguyên bãi trong cả phiên sư môn, lên cấp
        # thì chọn lại), phù tới, đi tuần qua các điểm và đánh mọi quái (theo danh sách tên mục tiêu của nhân vật nếu có)
        capdo = self.moitruong.get_capdonhanvat() or 0
        if not s.get("bandotrain") or s.get("captrain") != capdo:
            s["bandotrain"], s["captrain"] = self._chonbandotrain(), capdo
            if s["bandotrain"]:
                capquai = CAPQUAI_MAP.get(s["bandotrain"])
                self.moitruong._inlog(f"[SƯ MÔN] {nhan}: chọn bãi {laytenbando(s['bandotrain'])}"
                      f" ({f'quái cấp {capquai[0]}~{capquai[1]}, ' if capquai else ''}nhân vật cấp {capdo})")
        idbando = s["bandotrain"]
        if not idbando:
            self._ketthucsumon(f"không tìm được bãi train hợp cấp {capdo} cho {nhan}")
            return None
        s["trangthai"] = f"{nhan}: train ở {laytenbando(idbando)}"
        if self.moitruong.get_idbandohientai() != idbando:
            return self._dentoi(s, idbando, None, None, f"bãi train {laytenbando(idbando)}")
        s["chedo"], s["is_train"] = "danhquai", True
        self._batdanhquai(s)
        return self._diquadiem(s, f"train|{idbando}", idbando, self._laydiemtrain(idbando), f"train ở {laytenbando(idbando)}")

    def _buochieptro(self, s, nv):
        # Hiệp Trợ Trị An: tới Quản Ngục (Giám Ngục Quan) của nước trong nhiệm vụ nhận việc ("1. Hiệp Trợ Trị An" = lựa chọn đầu), tới
        # toạ độ trong mô tả diệt quái (tên lấy ở dòng tiến độ "Lưu Manh: 0/1"), đủ tiến độ thì về Quản Ngục trả
        idbando = nv.get("bando")
        if not idbando:
            self._ketthucsumon(f"không rõ Giám Ngục Quan ở nước nào: {nv['mucdich']}")
            return None
        if nv.get("buoc") == "tim":
            return self._noichuyen(s, nv, nv["npc"], ["look", "doithoai"], "nhận Hiệp Trợ Trị An", idbando, is_chibandogoiy = True)
        if nv["is_xong"] or is_dutiendo(nv):
            # Menu Giám Ngục Quan không có task_info: chọn "1. Hiệp Trợ Trị An" (accept_task), menu sau mới có "1. Hoàn thành nhiệm vụ"
            # (trahieptro lần 2: task_info nếu có, không thì lựa chọn đầu)
            return self._noichuyen(s, nv, nv["giamnguc"], ["look", "trahieptro", "trahieptro"], "trả Hiệp Trợ Trị An", idbando,
                                   is_chibandogoiy = True)
        quai, toado = nv.get("quai"), nv.get("toado")
        nhan = f"diệt {quai} ({nv['tiendo'][0]}/{nv['tiendo'][1]})" if nv.get("tiendo") else f"diệt {quai}"
        if self.moitruong.get_idbandohientai() != idbando:
            return self._dentoi(s, idbando, None, None, nhan)
        s["chedo"] = "danhquai"
        self._batdanhquai(s)
        # Tên quái trong game có thể dài hơn tên trong nhiệm vụ ("Lưu Manh ..."), con riêng mang ID người chơi thì chỉ đánh con của mình
        s["tenquai"] = {quai} | self._layquairieng([quai])[0]
        s["trangthai"] = nhan
        if toado:
            diems = self._laydiemdoquanh(idbando, toado) or [toado] + laydiemkhampha(idbando, toado)
        else:
            diems = self._laydiemtimquai(quai, idbando)
        return self._diquadiem(s, f"hieptro|{nv['luot']}", idbando, diems, nhan)

    def _buoctuanson(self, s, nv, bandomonphai):
        # Tuần Sơn: ở bản đồ môn phái mình, tới toạ độ trong mô tả rồi đi quanh đó diệt Kẻ Khả Nghi (tên lấy ở dòng tiến độ); đủ tiến độ
        # thì về NPC giao trả như thường (_xulysumon)
        if not bandomonphai:
            self._ketthucsumon(f"không rõ bản đồ môn phái để Tuần Sơn: {nv['mota']}")
            return None
        quai, toado = nv["quai"], nv.get("toado")
        nhan = f"tuần sơn diệt {quai} ({nv['tiendo'][0]}/{nv['tiendo'][1]})" if nv.get("tiendo") else f"tuần sơn diệt {quai}"
        if self.moitruong.get_idbandohientai() != bandomonphai:
            return self._dentoi(s, bandomonphai, None, None, nhan)
        s["chedo"] = "danhquai"
        self._batdanhquai(s)
        # "Kẻ Khả Nghi" trong game là con mang ID mình ("Cuồng Đồ (30)"); toạ độ có thể nằm ngay cổng (Đào Hoa: (71,83) cạnh cổng
        # (70,82)) thì đứng lùi ra kẻo bị chuyển bản đồ
        s["tenquai"], gannhat = self._layquairieng([quai])
        s["trangthai"] = nhan
        if gannhat:
            x, y = self.moitruong.get_toado(gannhat)
            return self._dentoi(s, bandomonphai, x, y, f"{nhan}: đánh {self.moitruong.get_tendoituong(gannhat)}",
                                khoangcach = self._khoangcachsudungkynangtamxa, is_dioo = self._is_dioo(bandomonphai))
        toado = dirtranhcong(bandomonphai, toado) if toado else None
        # Toạ độ Tuần Sơn hay lệch (chỗ không đi được): tới gần được tới đâu thì đứng chờ, rồi dò quanh đó theo lưới vật cản (đọc
        # không được thì đi vòng sát quanh đó (8 ô) trước vòng xa như cũ)
        if toado:
            vong8 = [(toado[0] + dx * 8, toado[1] + dy * 8) for dx, dy in ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))]
            diems = self._laydiemdoquanh(bandomonphai, toado) or [toado] + vong8 + laydiemkhampha(bandomonphai, toado)
        else:
            diems = self._laydiemtimquai(quai, bandomonphai)
        return self._diquadiem(s, f"tuanson|{nv['luot']}", bandomonphai, diems, nhan,
                               chodiemdau = THOIGIANCHODIEMNHIEMVU if toado else 0.)

    def _buoctruybat(self, s, nv):
        # Truy Bắt Thích Khách: tới Tổng Quản Vương Phủ của nước giao, bấm NPC là nhận; sang nước thích khách trốn, đi khắp bản đồ đánh
        # các loại còn thiếu ở dòng tiến độ (Thủ Lĩnh / Mộng Diện Thích Khách); đủ hết (hoặc Xong) thì về Tổng Quản trả
        tongquan = nv.get("tongquan")
        if nv.get("buoc") == "tim":
            return self._noichuyen(s, nv, nv["npc"], ["look", "ghimenu"], f"nhận {nv['ten']}", tenthaythe(nv["npc"])[1], is_chibandogoiy = True)
        if nv["is_xong"] or is_dutiendo(nv):
            if not tongquan:
                self._ketthucsumon(f"không rõ Tổng Quản nào để trả Truy Bắt Thích Khách: {nv['mota']}")
                return None
            return self._noichuyen(s, nv, tongquan, ["look", "thamvieng"], f"trả {nv['ten']}", tenthaythe(tongquan)[1],
                                   is_chibandogoiy = True)
        idbando = nv.get("bando")
        if not idbando:
            self._ketthucsumon(f"không rõ phải tới nước nào ({nv['ten']}): {nv['mucdich']}")
            return None
        nhan = f"{nv['ten']}: " + (", ".join(f"{t} {a}/{b}" for t, a, b in nv["tiendos"]) if nv.get("tiendos") else ", ".join(nv["quais"]))
        if self.moitruong.get_idbandohientai() != idbando:
            return self._dentoi(s, idbando, None, None, nhan)
        s["chedo"] = "danhquai"
        self._batdanhquai(s)
        # Đối thủ mang ID mình ("Quan Viên Đào Tẩu (29)", hộ vệ "Tùy Tùng (29)"), bị đánh thì chạy trốn chỗ khác: thấy là đuổi theo
        s["tenquai"], gannhat = self._layquairieng(nv["quais"])
        s["trangthai"] = nhan
        if gannhat:
            x, y = self.moitruong.get_toado(gannhat)
            return self._dentoi(s, idbando, x, y, f"{nhan}: đuổi {self.moitruong.get_tendoituong(gannhat)}",
                                khoangcach = self._khoangcachsudungkynangtamxa, is_dioo = self._is_dioo(idbando))
        # Lưới điểm đi khắp bản đồ, bắt đầu từ điểm gần chỗ vừa tới nhất (tính 1 lần cho lượt này, giữ thứ tự để đi tiếp vòng)
        khoa = f"truybat|{nv['luot']}|{idbando}"
        if s.get("luoi", (None,))[0] != khoa:
            # Nước có điểm đi vòng ngoài thành (DIEMNGOAITHANH_MAP, đi được hết): đi theo đó, không dùng lưới / vòng tự tính (hay lọt chỗ
            # không đi được, đứng kẹt tới bị đứt kết nối)
            ngoaithanh = DIEMNGOAITHANH_MAP.get(idbando)
            # Không có điểm vẽ tay thì lộ trình dò phủ cả vùng đi được (lưới vật cản), không được nữa mới lưới 30 ô theo khung cổng
            diems = list(ngoaithanh or self._taodiemdo(idbando) or laydiemluoi(idbando))
            if diems:
                i = min(range(len(diems)), key = lambda k: self.moitruong.get_khoangcachdiem(*diems[k]))
                diems = diems[i:] + diems[:i]
            # Mô tả có toạ độ (chỗ đối thủ hay lui tới): tới đó và quanh đó trước
            # (đứng chờ ở đó, dò vòng 10 ô rồi vòng 20 ô; Thọ gặp đối thủ cách toạ độ ~12 ô)
            if nv.get("toado") and ngoaithanh:
                # Bắt đầu vòng ngoài thành từ điểm gần toạ độ nhất (đối thủ hay chạy quanh đó)
                i = min(range(len(diems)), key = lambda k: math.dist(diems[k], nv["toado"]))
                diems = [nv["toado"]] + diems[i:] + diems[:i]
            elif nv.get("toado"):
                xt, yt = nv["toado"]
                doquanh = self._laydiemdoquanh(idbando, nv["toado"])
                if doquanh:
                    diems = doquanh + [nv["toado"]] + diems
                else:
                    vong10 = [(xt + dx * 10, yt + dy * 10) for dx, dy in ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))]
                    diems = [nv["toado"]] + vong10 + laydiemkhampha(idbando, nv["toado"])[1:9] + [nv["toado"]] + diems
            s["luoi"] = (khoa, diems)
        return self._diquadiem(s, khoa, idbando, s["luoi"][1], nhan, chodiemdau = THOIGIANCHODIEMNHIEMVU if nv.get("toado") else 0.)

    def _buoctythi(self, s, nv):
        # Môn Phái Tỷ Thý: tới bản đồ môn phái, tìm <phái> Đệ Tử. Còn là NPC thì nói chuyện chọn "1. Lập tức Khiêu chiến" (lựa chọn đầu),
        # thành đối tượng đánh được thì đánh (chỉ đánh nó)
        idbando = nv.get("bando")
        if not idbando:
            self._ketthucsumon(f"không rõ bản đồ môn phái {nv.get('phai')} để tỷ thí")
            return None
        moitruong = self.moitruong
        nhan = f"tỷ thí với {nv['detu']}"
        idbandohientai = moitruong.get_idbandohientai()
        # Ở đấu trường riêng mà đối thủ đã chịu thua ("tại hạ thật sự không thể thắng, mời trở về đi~", menu "1. Rời khỏi đấu trường"):
        # rời luôn, không chờ tiến độ (cửa sổ nhiệm vụ có khi chỉ cập nhật sau khi ra), không coi nó là đối thủ đứng chờ mãi
        if idbandohientai not in BANDOCONG_MAP:
            noidung = moitruong.get_noidungcuasotuychon() if moitruong.get_is_danghiencuasotuychon() else ""
            if noidung and any(chu in noidung for chu in ("không thể thắng", "trở về", "đấu trường")):
                return self._roidautruong(s, nv)
        # Đối thủ đang đánh được (đã khiêu chiến, thường ở bản đồ tỷ thí riêng): chỉ đánh nó, ở bản đồ nào cũng đánh
        doithus = [chuanhoaten(t) for t in nv.get("doithus") or [nv["detu"]]]
        diachi = next((d for d in moitruong._get_diachidoituongxungquanhs() if not moitruong.get_is_nguoichoi(d)
                       and any(t in chuanhoaten(moitruong.get_tendoituong(d)) for t in doithus) and moitruong.get_is_cothetancong(d)), None)
        if diachi:
            s["chedo"] = "danhquai"
            self._batdanhquai(s)
            s["tenquai"] = {moitruong.get_tendoituong(diachi)}
            s["trangthai"] = f"{nhan}: đánh {moitruong.get_tendoituong(diachi)}"
            x, y = moitruong.get_toado(diachi)
            return self._dentoi(s, idbandohientai, x, y, nhan, khoangcach = self._khoangcachsudungkynangtamxa)
        if idbandohientai != idbando:
            # Bản đồ không có trong dữ liệu cổng (bản đồ tỷ thí riêng): chờ đối thủ hiện, không chạy về
            if idbandohientai not in BANDOCONG_MAP:
                s["trangthai"] = f"{nhan}: ở bản đồ tỷ thí, chờ đối thủ"
                return None
            # Kèm chỗ đối thủ để chọn đường theo điểm đích (Cấm Vệ Quân: phù Thủ Dương Sơn, DUONGUUTIENs)
            return self._dentoi(s, idbando, *(nv.get("vitridetu") or (None, None)), nhan)
        # Biết toạ độ đối thủ (NPCTYTHI): tới đó trước, nói chuyện với con trùng tên gần nhất
        if nv.get("vitridetu"):
            if moitruong.get_khoangcachdiem(*nv["vitridetu"]) > 6:
                return self._dentoi(s, idbando, *nv["vitridetu"], nv["detu"])
            # Tới chỗ rồi mà chưa thấy: đi vòng quanh chỗ đó, không chạy sang con trùng tên ở chỗ khác
            if not self._timdoituongxungquanh(nv["detu"]):
                return self._diquadiem(s, f"tythi|{nv['luot']}", idbando, laydiemkhampha(idbando, nv["vitridetu"]), f"tìm {nv['detu']}")
        return self._noichuyen(s, nv, nv["detu"], ["look", "chon1"], "khiêu chiến", idbando)

    def _roidautruong(self, s, nv):
        # Thua xong đối thủ thành NPC ("Đường Môn đệ tử: ... mời trở về đi~"), lựa chọn đầu là "1. Rời khỏi đấu trường"
        moitruong = self.moitruong
        # Menu đang hiện có "Rời khỏi đấu trường" (lệnh "tallk <id># kickout"): gửi thẳng, cách nhau THOIGIANCHONHIEMVUDOI giây
        lenh = next((l for l in (moitruong.get_lenhcuasotuychons() if moitruong.get_is_danghiencuasotuychon() else [])
                     if l.split("# ", 1)[-1].strip() == "kickout"), None)
        if lenh:
            if time.time() - s.get("lucroidautruong", 0.) > THOIGIANCHONHIEMVUDOI:
                s["lucroidautruong"] = time.time()
                moitruong._inlog(f"[SƯ MÔN] Rời đấu trường: {lenh}")
                moitruong.action_thucthicaulenh(lenh)
            s["trangthai"] = "tỷ thí xong: rời đấu trường"
            return None
        doithus = [chuanhoaten(t) for t in nv.get("doithus") or [nv["detu"]]]
        diachi = next((d for d in moitruong._get_diachidoituongxungquanhs() if not moitruong.get_is_nguoichoi(d)
                       and any(t in chuanhoaten(moitruong.get_tendoituong(d)) for t in doithus)), None)
        if not diachi:
            s["trangthai"] = "tỷ thí xong: chờ đối thủ hiện để rời đấu trường"
            return None
        return self._noichuyen(s, nv, moitruong.get_tendoituong(diachi), ["look", "chon1"], "rời đấu trường", moitruong.get_idbandohientai())

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
            # Đủ thì tới Thạch Sư chọn "Hoàn thành": lệnh trong menu (gửi thẳng task_info không có trong menu thì NPC không nhận)
            return self._noichuyen(s, nv, nv["npc"], ["look", "hoanthanh"], f"giao {nv['soluong']} {nv['vatpham']}", bandomonphai)
        idbando = timbandotheoten(nv.get("bando"))
        if not idbando or not nv.get("quai"):
            # Game không ghi chỗ ("Nghe nói ở 0"): do nhận việc nhầm loại (gửi lệnh Thu mua khi Thạch Sư giao Thu thập); bước "nhanviec"
            # đã chọn đúng lệnh trong menu nên không còn gặp, gặp thì dừng báo
            self._ketthucsumon(f"không rõ đánh quái gì / ở đâu để thu thập {nv['vatpham']}: {nv['mota']}")
            return None
        nhan = f"thu thập {nv['vatpham']} {soluong}/{nv['soluong']} (đánh {nv['quai']})"
        if self.moitruong.get_idbandohientai() != idbando:
            return self._dentoi(s, idbando, None, None, nhan)
        s["chedo"] = "danhquai"
        self._batdanhquai(s)
        # Đánh mọi quái trong bãi (như bãi train), không chỉ con ra vật phẩm: quái trong bãi có hạn, không giết các con khác thì con cần
        # đánh không ra thêm (người dùng). Chỉ nhặt món nhiệm vụ
        s["tenquai"], s["is_train"], s["vatphamnhat"] = set(), True, {nv["vatpham"]}
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
                self.moitruong._inlog(f"[SƯ MÔN] Chuyển {nv['vatpham']} lên hành trang 1 để giao")
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
        self.moitruong._inlog(f"[SƯ MÔN] Mua {nv['vatpham']} ở {moitruong.get_tendoituong(diachi)}: ô {o}, giá {gia}")
        return None

    def _danhgiammau(self, s, nv, diachi):
        # Bắt SOLANBATTRUOCKHIDANH lần chưa được thì đánh thường 1 cái cho quái giảm máu (máu càng thấp càng dễ bắt), rồi bắt tiếp.
        # Đánh chết là mất con đó nên cẩn thận: mỗi lần chỉ 1 cái ("kill", thấy máu tụt là dùng chiêu bắt ngay để ngắt đánh), ghi lại 1 cái
        # làm tụt bao nhiêu % máu (theo tên quái) và chỉ đánh khi máu còn lại sau cú đánh (tính dư x1.5) vẫn trên NGUONGMAUANTOAN%;
        # máu đã dưới NGUONGMAUDUNGDANH% thì thôi đánh. -> True khi đang chờ cú đánh (không bắt lượt này)
        moitruong = self.moitruong
        iddt = moitruong.get_iddoituong(diachi)
        mau = moitruong.get_phantramsinhlucconlai(diachi)
        satthuong = s.setdefault("satthuong", {})
        cho = s.get("chodanh")
        if cho and cho["id"] == iddt:
            if mau < cho["mau"]:
                # Đã trúng: nhớ sức đánh, bắt ngay (chiêu bắt ngắt đánh thường)
                satthuong[nv["quai"]] = max(satthuong.get(nv["quai"], 0), cho["mau"] - mau)
                s["chodanh"] = None
                moitruong._inlog(f"[SƯ MÔN] Đánh {nv['quai']}: máu {cho['mau']}% -> {mau}% (1 cái tụt {cho['mau'] - mau}%), bắt tiếp")
                moitruong.action_ngatdichuyen()
                return False
            if time.time() - cho["luc"] < THOIGIANCHODANH:
                s["trangthai"] = f"đánh {nv['quai']} 1 cái cho giảm máu ({mau}%)"
                return True
            s["chodanh"] = None
            moitruong.action_ngatdichuyen()
            return False
        if s.get("solanbat", {}).get(iddt, 0) < SOLANBATTRUOCKHIDANH or mau < NGUONGMAUDUNGDANH:
            return False
        dukien = satthuong.get(nv["quai"])
        if dukien is not None and mau - dukien * 1.5 < NGUONGMAUANTOAN:
            return False
        # Đánh 1 cái rồi đếm lại SOLANBATTRUOCKHIDANH lần bắt nữa mới đánh tiếp
        s["solanbat"][iddt] = 0
        s["chodanh"] = {"id": iddt, "mau": mau, "luc": time.time()}
        moitruong._inlog(f"[SƯ MÔN] Bắt {nv['quai']} {SOLANBATTRUOCKHIDANH} lần chưa được, máu {mau}%: đánh 1 cái"
                         f"{f' (1 cái tụt ~{dukien}%)' if dukien is not None else ' (chưa biết sức đánh)'}")
        moitruong.action_thucthicaulenh(f"kill {iddt:x}#")
        s["trangthai"] = f"đánh {nv['quai']} 1 cái cho giảm máu ({mau}%)"
        return True

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
        if self._danhgiammau(s, nv, diachi):
            return None
        # Tỉ lệ bắt thấp: cứ dùng tới khi được, cách nhau ít nhất 0.25s
        if time.time() - s["lucbat"] >= GIANCACHBATBAOTHU:
            s.setdefault("solanbat", {})
            iddt = moitruong.get_iddoituong(diachi)
            s["solanbat"][iddt] = s["solanbat"].get(iddt, 0) + 1
            moitruong.action_ngatdichuyen()
            moitruong.action_thucthicaulenh(LENHBATBAOTHU.format(moitruong.get_iddoituong(diachi)))
            s["lucbat"] = time.time()
        s["trangthai"] = f"đang bắt {nv['quai']}"
        return None
