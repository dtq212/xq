# Tự động đi phó bản Lăng Ly Sơn / Thành Kiều Quân Doanh (PHOBAN_MAP; trạng thái chung self._langlyson, s["phoban"] là phó bản đang đi).
# Thành Kiều khác Lăng Ly Sơn ở chỗ vào / nhận thưởng: Tần Quốc (220, 65) Thảo Nghịch Tướng Quân "3. Sử dụng [Hạt Mè Khai Môn] tiến vào"
# -> Xác nhận, chỉ trưởng nhóm bấm, vận khí xong hệ thống đưa cả nhóm vào 701; 1 tầng 5 boss; nhận thưởng "4. Nhận thưởng" rồi "1. Nhận thưởng" cùng NPC.
# Phần dưới tả Lăng Ly Sơn, Thành Kiều đi y như vậy.
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
# Phong Yêu Kính (luachonvao "give", _buocvaophongyeu): người online đứng đầu nhóm Tổ đội tự động (todoi.json) lập nhóm 1 người
# ("team + <ID mình>"), tới Chu Quốc (252, 160) Tả Khâu Minh, give 1 món Lam Kim (_chondolamkim) -> menu hỏi thiêu đốt "1. Đúng vậy, ta
# muốn đi" -> mời các thành viên online của nhóm todoi vào nhóm -> mọi người hiện "Đội nhóm các ngươi đã mở Phong Yêu Kính..." "1. Đúng
# vậy, ta muốn vào" (_xulymenuphongyeu) -> "Phó Bản Phong Y" (mượn ID 1 bản đồ ngẫu nhiên, vd 133). Trong đó dò khắp bản đồ đánh mọi quái; 85% quái ra boss nhỏ,
# hết quái ra boss ẩn (TUBOSSPHONGYEUs, toạ độ ngẫu nhiên): giết 2 boss (hoặc dò 2 lượt bản đồ) là xong, Truyền Tống Thỏ Yêu (ở chỗ vào)
# "1. Ta muốn về Chu Quốc", không có thưởng phải lĩnh, đổi tổ đội như dưới.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import re
import time
import unicodedata

from hangso_xq import *
from giaodo_xq import taolenhgiao
from thongbao_xq import baosuco
from tienich_xq import phatam, laynhomtodoitudongs, taicauhinhphongyeu, CAUHINHPHONGYEU_MACDINH

BANDO_THUYHOASON = 82
NPCVAOLANGLYSON = ("Đào Vong Khổ Dịch", 137, 117)
NPCTHANHKIEU = ("Thảo Nghịch Tướng Quân", 220, 65)
NPCPHONGYEU = ("Tả Khâu Minh", 252, 160)
# Phong Yêu Kính: nhận ra qua đầu tên bản đồ game (ID là 1 bản đồ ngẫu nhiên, không bao giờ là Tân Thủ Thôn / quốc gia). Thỏ Yêu luôn
# có sẵn ở chỗ vào (toạ độ tuỳ bản đồ): thấy thì nhớ toạ độ thật, chưa thấy thì về chỗ mình xuất hiện lúc vào (diemvao)
TIENTOTENBANDOPHONGYEU = "Phó Bản Phong"
TENTHOYEU = "Truyền Tống Thỏ Yêu"
# Menu sau khi give, có 2 kiểu, chỉ chọn lựa chọn 1 khi lời có đủ các cụm của 1 kiểu:
#   - "Sau khi đem trang bị này thiêu đốt làm chất xúc tác thì có thể tiến vào Phong Yêu Kính..." -> "1. Đúng vậy, ta muốn đi"
#   - "Ta có thể đem trang bị này đốt đi, để làm chất xúc tác, ngươi muốn như vậy phải không ?" -> "1. Xác nhận"; trưởng nhóm thấy "Xin đợi
#     thành viên khác trả lời", thành viên thấy "Đội trưởng của ngươi muốn mở Phong Yêu Kính, ngươi Xác nhận không ?" -> "1. Xác nhận"
# Sau đó mọi người: "Đội nhóm các ngươi đã mở Phong Yêu Kính..." -> "1. Đúng vậy, ta muốn vào"
# Game viết cả "thêu đốt" (sai chính tả) lẫn "thiêu đốt" / "đốt đi" => chỉ xét "đốt" + "chất xúc tác"
LOIMENUTHIEUDOTs = (("đốt", "chất xúc tác"),)
LOIMENUVAOPHONGYEU = "đã mở phong yêu kính"
# Đội đã mở thì vào lúc nào cũng được: "look" Tả Khâu Minh -> menu chính "1. Tiến vào Phong Yêu Kính" -> "...đã mở Phong Yêu Kính..." ->
# "1. Đúng vậy, ta muốn vào" (lựa chọn đếm từ 0)
LUACHONVAOLAIPY = (0, 0)
LOIMENUTHANHVIENXACNHANPY = "muốn mở phong yêu kính"
LOIMENUDOITHANHVIENPY = "đợi thành viên"
# Đồ đem đốt (_phantichdolamkim, cấu hình ở giao diện: tienich_xq.taicauhinhphongyeu): màu tên được chọn (mã màu đầu mô tả: Lam Kim
# \x1bC, Hoàng Kim \x1bY), trang bị (dòng loại "［...］", không phải "[Pháp Bảo]"), (tuỳ chọn) Chưa giám định, chưa Phong Ấn / Khoá, cấp sử
# dụng >= cấp nhân vật - caphonnhanvat (quái trong phó bản = cấp đồ + 20, đồ thấp quá quái yếu không có kinh nghiệm) và >=
# CAPDOLAMKIMTOITHIEU (game: trang bị từ cấp 15), tên không chứa cụm "khongdot", có "chidot" thì tên phải chứa 1 cụm trong đó. Chọn món
# cấp thấp, giá bán thấp nhất. Chỉ lấy đồ trong túi, không bao giờ đụng đồ đang mặc
MAMAULAMKIM = "\x1bC"
MAMAUHOANGKIM = "\x1bY"
CAPDOLAMKIMTOITHIEU = 15
# Mỗi lượt gửi desc tối đa chừng này ô chưa có mô tả (mỗi lệnh chờ 0.2s); gửi xong chừng này giây chưa có mô tả thì gửi lại, tối đa
# SOLANDESCPY lần rồi bỏ ô đó
SODESCMOILUOT = 3
THOIGIANCHODESCPY = 3.
SOLANDESCPY = 3
SOBOSSPHONGYEU = 2
# Tên boss có đuôi cấp, vd "Trịnh Vương Tàn Phách (cấp 96)" (85%, "<nước> Vương Tàn Phách"), "Hổ Cảnh Kính Ma (cấp 97)" / "Long Nha Kính Ma (cấp 101)" / "Kính Ma Khuyển Thần (cấp 101)" (100%, còn có thể
# gặp tên khác: thêm vào đây). Quái thường có chữ "Quốc": "Trịnh Quốc Kính Yêu", "Ngô Quốc Kính Ma" (cũng chứa "Kính Ma", từng bị nhận
# nhầm là boss) => tên có TUKHONGPHAIBOSSPY thì không phải boss
TUBOSSPHONGYEUs = ("Vương Tàn Phách", "Kính Ma")
TUKHONGPHAIBOSSPY = "Quốc"
# Đọc boss các thành viên khác đã giết (shared_data, cả máy khác nối LAN) mỗi chừng này giây
GIANCACHDOCBOSSPY = 1.
# Chọn "ta muốn đi" / "ta muốn vào" xong chờ được đưa vào tối đa chừng này giây rồi mới hỏi lại Tả Khâu Minh (không give thêm)
THOIGIANCHOVAOPHONGYEU = 30.
GIANCACHCHONMENUPHONGYEU = 2.
# Người give: lập nhóm 1 người / rời nhóm mỗi chừng này giây; đã mở thì mời mỗi thành viên mỗi GIANCACHMOIPY giây, chờ đủ người tối đa
# THOIGIANCHOMOIPY giây rồi mới chọn "ta muốn vào"
GIANCACHLAPNHOMPY = 3.
# Vừa bật chờ chừng này giây (dữ liệu LAN về đủ) rồi mới xét ai là người give
THOIGIANDOCNHOMPY = 15.
# Vào phó bản chưa tới chừng này giây mà đã đủ boss thì không tin là xong (số boss cũ)
THOIGIANTOITHIEUPY = 120.
# Thành viên đã vào nhóm người give: "look" Tả Khâu Minh chưa có menu "đã mở" / chọn vào rồi chưa được đưa vào thì chừng này giây sau look lại
GIANCACHLOOKTHANHVIENPY = 10.
GIANCACHMOIPY = 5.
THOIGIANCHOMOIPY = 90.
# Dò hết 1 lượt bản đồ thì hỏi Thỏ Yêu số quái đã đánh (ghi log); trưởng nhóm dò chừng này lượt chưa đủ 2 boss thì ra luôn
SOLUOTDORAPHONGYEU = 2
THOIGIANHOISOQUAI = 40.
KHOANGCACHTOIDIEMPY = 3.
THOIGIANMOIDIEMPY = 25.
# Phó bản tự đi được: bandovao tầng đầu, bandonpc + npc nơi vào / nhận thưởng. luachonvao None: vào bằng lối đi NPC (LOIDINPC_MAP, lựa
# chọn đầu); số: tự nói chuyện NPC chọn lựa chọn thứ luachonvao (đếm từ 0, bỏ CLOSE) rồi Xác nhận, vatphamvao là vật phẩm phải có trong hành trang (không bị trừ).
# luachonthuong: lựa chọn nhận thưởng (tuple: chọn lần lượt qua từng menu, vd Thành Kiều "4. Nhận thưởng" rồi "1. Nhận thưởng"); is_kiemtrathuong: menu phải có lời chúc mừng mới chọn (Lăng Ly Sơn: NPC đổi menu khi đã xong)
PHOBAN_MAP = {
    "langlyson": {"ten": "Lăng Ly Sơn", "bandovao": BANDO_LANGLYSON1, "bandonpc": BANDO_THUYHOASON, "npc": NPCVAOLANGLYSON,
                  "luachonvao": None, "vatphamvao": None, "luachonthuong": 0, "is_kiemtrathuong": True, "tinhoanthanh": "lăng ly sơn"},
    "thanhkieu": {"ten": "Thành Kiều", "bandovao": BANDO_THANHKIEU, "bandonpc": BANDO_TANQUOC, "npc": NPCTHANHKIEU,
                  "luachonvao": 2, "vatphamvao": "Hạt Mè Khai Môn", "luachonthuong": (3, 0), "is_kiemtrathuong": False, "tinhoanthanh": "thành kiều"},
    # luachonthuong None: không có thưởng phải lĩnh, ra bằng Thỏ Yêu (_buocraphongyeu)
    "phongyeukinh": {"ten": "Phong Yêu Kính", "bandovao": None, "bandonpc": BANDO_CHUQUOC, "npc": NPCPHONGYEU,
                     "luachonvao": "give", "vatphamvao": None, "luachonthuong": None, "is_kiemtrathuong": False, "tinhoanthanh": "phong yêu kính"},
}
# id bản đồ -> các bước trong tầng: ("danh", tên boss (hoặc tuple các tên có thể gặp), x, y[, True: phải đủ thành viên]) |
# ("noichuyen", tên NPC, x, y) | ("sangtang", id tầng kế) | ("ra",)
BUOCLANGLYSON_MAP = {
    # Thành Kiều: 4 boss lần lượt hiện, quét sạch thì boss cuối hiện
    BANDO_THANHKIEU: (("danh", "Mã Quỷ", 245, 83), ("danh", "Lương Hưng", 123, 89), ("danh", "Yến Thập Tam", 130, 175),
                      ("danh", "Tư Tà", 61, 133), ("danh", "Thủ Lĩnh Thành Kiều", 122, 147, True), ("ra",)),
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
# Thành Kiều: nói chuyện vào mà quá SOLANTHUNOICHUYEN lần không vận khí (chưa xác nhận được / NPC không cho vào) thì chừng này giây sau thử lại
THOIGIANTHULAIVAO = 20.
# Trước khi vào: nhóm phải đủ người như vòng trước và đứng yên chừng này giây; chờ quá THOIGIANBAONHOMTHIEU giây chưa đủ thì báo
THOIGIANNHOMONDINH = 5.
THOIGIANBAONHOMTHIEU = 120.


def _tenboss(ten):
    # Tên hiển thị của boss (bước "danh" có thể ghi tuple các tên)
    return ten[0] if isinstance(ten, tuple) else ten


class TacTuLangLySon:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_langlyson(self, phoban = "langlyson"):
        if self._langlyson or phoban not in PHOBAN_MAP:
            return
        self._langlyson = {"phoban": phoban, "batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "giaidoan": "vao",
                           "buoc": {}, "hoithoai": None, "boss": None, "lucbatdauvong": time.time(), "sovong": 0, "dabao": set(),
                           "thanhviens": {}, "dudoi": False, "lucchodoi": 0., "lucmoi": {}, "diemvao": {}, "daxongphoban": False,
                           "tindaghi": set(), "davao": False}
        ten = PHOBAN_MAP[phoban]["ten"]
        self.moitruong._inlog(f"[{ten.upper()}] Bắt đầu tự động đi {ten}")
        phatam(f"Bắt đầu {ten}")

    def huy_langlyson(self):
        if self._langlyson:
            self._ketthuclanglyson(f"Đã dừng {self._tenpb(self._langlyson)} (bấm tay)")

    @staticmethod
    def _tenpb(s):
        return PHOBAN_MAP[s["phoban"]]["ten"]

    def _logpb(self, s, noidung):
        self.moitruong._inlog(f"[{self._tenpb(s).upper()}] {noidung}")

    def get_phobanlanglyson(self):
        # Phó bản đang đi ("langlyson" / "thanhkieu"), không đi thì ""
        return self._langlyson["phoban"] if self._langlyson else ""

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
        is_dangdi = (s["giaidoan"] == "vao" and (s["thanhviens"] or self._is_trongphobanlls(self.moitruong.get_idbandohientai()))) \
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
        #   - đang ở chế độ phó bản (mình bật, người mình theo sau bật, hoặc mình là thành viên vòng đang đi) mà ở ngoài bản đồ phó bản:
        #     không đánh quái dọc đường / ở Thuý Hoa Sơn (đỡ chạy linh tinh)
        #   - chính mình đang chờ thành viên, hoặc người mình theo sau (trưởng nhóm cùng máy) đang chờ và mình cũng ở tầng đó
        # Đang đánh thường ("kill") thì ngắt luôn (máy chủ giữ lệnh đánh cả khi bỏ chọn mục tiêu)
        idbando = self.moitruong.get_idbandohientai()
        info = self._laythongtinmuctieutheosaucuasokhac() if self._is_tudongtheosau else None
        if not self._is_trongphobanlls(idbando):
            is_cam = bool(self._langlyson) or bool(info and info.get("_is_danglanglyson")) or self.get_is_giunhomlanglyson()
        elif self.get_is_langlysonchothanhvien():
            is_cam = True
        else:
            is_cam = bool(info and info.get("_langlysonchothanhvien") and info.get("tenbando") == idbando)
        if is_cam and self._is_battudongtancongvatly and self._diachimuctieutancongvatly:
            self._ngattancongvatlydaohoa(self._diachimuctieutancongvatly)
        return is_cam

    def _is_trongphongyeu(self):
        # Phong Yêu Kính mượn ID 1 bản đồ ngẫu nhiên: chỉ nhận ra qua đầu tên bản đồ game
        ten = self.moitruong.get_tenbandogame()
        return bool(ten) and unicodedata.normalize("NFC", ten).startswith(TIENTOTENBANDOPHONGYEU)

    def _is_trongphobanlls(self, idbando):
        # Đang ở trong 1 phó bản tự đi được (tầng có bước trong BUOCLANGLYSON_MAP hoặc Phong Yêu Kính)
        return idbando in BUOCLANGLYSON_MAP or self._is_trongphongyeu()

    def get_is_langlysondanhquai(self):
        # Đang ở chỗ boss: đánh mọi quái quanh đó, không giới hạn theo danh sách tên / điểm đánh của nhân vật
        return bool(self._langlyson) and self._langlyson["chedo"] == "danhquai"

    def get_trangthailanglyson(self):
        if self._langlyson:
            return f"{self._tenpb(self._langlyson)} (xong {self._langlyson['sovong']} vòng): {self._langlyson['trangthai']}"
        return self._ketqualanglyson or ""

    def _ketthuclanglyson(self, thongbao):
        s = self._langlyson
        self._langlyson = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        ten = self._tenpb(s) if s else "Lăng Ly Sơn"
        if s and s["sovong"]:
            thongbao += f" (xong {s['sovong']} vòng)"
        self.moitruong._inlog(f"[{ten.upper()}] {thongbao}")
        self._ketqualanglyson = f"{time.strftime('%H:%M')} {ten}: {thongbao}"
        phatam(f"Kết thúc {ten}")

    def _baolanglyson(self, s, khoa, noidung):
        # Báo Telegram 1 lần cho mỗi việc cần người dùng để ý, bot vẫn chờ / chạy tiếp
        if khoa not in s["dabao"]:
            s["dabao"].add(khoa)
            self._logpb(s, noidung)
            baosuco(self.moitruong, "langlyson", noidung, khoa = f"{s['batdau']}|{khoa}", giancach = 0.)

    def _batdanhquailanglyson(self, s):
        # Ô cần cho đánh quái (cùng bộ với sư môn) người dùng quên bật thì đổi giúp, dừng thì trả lại. "Chỉ đánh người chơi" của người
        # dùng giữ nguyên trong phó bản
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            if thuoctinh != "_is_chidanhnguoichoi" and getattr(self, thuoctinh) != giatri:
                s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
                setattr(self, thuoctinh, giatri)
                self._logpb(s, f"{'Bật' if giatri else 'Tắt'} \"{ten}\" để đánh boss (dừng thì trả lại)")

    def _doctinphoban(self, s):
        # Tin trò chuyện có "phó bản" ghi log (mỗi câu 1 lần) để biết game báo gì; "hoàn thành phó bản <tên>" là chắc chắn đã xong
        # (game: "Bạn đã hoàn thành phó bản Lăng Ly Sơn, có thể quay về báo cáo Đào Vong Khổ Dịch để nhận thưởng!")
        for _, noidung in list(self.moitruong.get_lichsutrochuyen5s()):
            thuong = (noidung or "").lower()
            if "phó bản" not in thuong or noidung in s["tindaghi"]:
                continue
            s["tindaghi"].add(noidung)
            self._logpb(s, f"Tin game: {noidung[:120]!r}")
            if "hoàn thành phó bản" in thuong and PHOBAN_MAP[s["phoban"]]["tinhoanthanh"] in thuong and not s["daxongphoban"]:
                s["daxongphoban"] = True
                self._logpb(s, "Game báo đã hoàn thành phó bản")

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulylanglyson(self):
        # Gọi thay lộ trình điểm đánh khi đang đi Lăng Ly Sơn -> yêu cầu di chuyển hoặc None
        s = self._langlyson
        moitruong = self.moitruong
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logpb(s, s['trangthai'])
        s["chedo"] = "dichuyen"
        self._doctinphoban(s)
        if moitruong.get_is_nhanvatdachet() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0:
            return None
        if time.time() - s["lucbatdauvong"] > THOIGIANVONGTOIDA:
            self._baolanglyson(s, f"cham|{s['sovong']}", f"⚠️ {self._tenpb(s)}: vòng {s['sovong'] + 1} quá {int(THOIGIANVONGTOIDA // 60)} phút chưa xong "
                                                       f"({s['trangthai']})")
        if moitruong.get_is_dangvankhi():
            # Đang vận khí (vào phó bản / khởi động cơ quan / Hồi Thành Phù): đứng yên, việc nói chuyện dở thì ghi nhận đã thấy vận khí
            if s["hoithoai"]:
                s["hoithoai"]["vankhi"] = True
            return None
        if time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        if s["giaidoan"] == "vao" and moitruong.get_is_dangnamtrongnhom() and not moitruong.get_is_truongnhom() \
                and s["phoban"] == "phongyeukinh" and not self._is_tudongtheosau and self._is_trongphongyeu():
            # Phong Yêu Kính, thành viên KHÔNG bật Theo sau (bật thì Theo sau lo như cũ): tự đi lộ trình dò khắp bản đồ đánh hết quái / đánh
            # boss như trưởng nhóm; xong thì đứng đánh quái quanh đó chờ trưởng nhóm giải tán nhóm (thành viên được đưa ra Chu Quốc)
            s["lathanhvien"] = True
            idbando = moitruong.get_idbandohientai()
            s["diemvao"].setdefault(idbando, moitruong.get_toado())
            return self._buoctrongphongyeu(s, idbando, is_thanhvien = True)
        if s["giaidoan"] == "vao" and s["phoban"] == "phongyeukinh" and not self._is_trongphongyeu():
            # Phong Yêu Kính ngoài phó bản: người give (đứng đầu nhóm todoi, kể cả khi đang là thành viên nhóm người khác: tự rời) lập nhóm 1
            # người / give / mời; thành viên tới Tả Khâu Minh chờ mời rồi tự "look" vào (_buocvaophongyeu)
            s["chedo"] = "dichuyen"
            return self._buocvao(s)
        if s["giaidoan"] == "vao" and moitruong.get_is_dangnamtrongnhom() and not moitruong.get_is_truongnhom():
            # Bật ở thành viên (không phải trưởng nhóm): không tự đánh boss / lĩnh thưởng theo vòng riêng (từng làm cả 4 nhân vật đều tự
            # chạy, tự phát mã thưởng rồi chờ nhau). Theo sau lo đi theo, vào / qua tầng, lĩnh thưởng; trưởng nhóm dis mà mình thành trưởng
            # nhóm thì tự chạy tiếp
            s["chedo"] = "thanhvien"
            s["lathanhvien"] = True
            s["trangthai"] = "thành viên: đi theo trưởng nhóm" + ("" if self._is_tudongtheosau else " (chưa bật Theo sau!)")
            return None
        if s["giaidoan"] == "nhanthuong":
            return self._buocnhanthuong(s)
        if s["giaidoan"] == "doinhom":
            return self._buocdoinhom(s)
        idbando = moitruong.get_idbandohientai()
        is_trongphongyeu = self._is_trongphongyeu()
        if idbando in BUOCLANGLYSON_MAP or is_trongphongyeu:
            self._ghithanhvienvong(s)
            if not s["davao"]:
                s["davao"] = True
                s.pop("lucthulaivao", None)
                s.pop("lucvankhivao", None)
                s["hoithoai"] = None
            # Chỗ vừa vào tầng: chờ thành viên ở đây (xa boss, người vào sau cũng xuất hiện ở đây)
            s["diemvao"].setdefault(idbando, moitruong.get_toado())
            if is_trongphongyeu:
                return self._buoctrongphongyeu(s, idbando)
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
            self._logpb(s, f"Chờ đủ thành viên trước boss cuối: {', '.join(f'{t} ({l})' for _, t, l in vangs)}")
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
                               f"⚠️ {self._tenpb(s)}: chờ {int(THOIGIANBAOCHOTHANHVIEN // 60)} phút chưa đủ người để đánh boss cuối: "
                               + ", ".join(f"{t} ({l})" for _, t, l in vangs))
        diemvao = s["diemvao"].get(idbando)
        if diemvao and moitruong.get_khoangcachdiem(*diemvao) > 3.:
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (diemvao[0], diemvao[1], idbando), "khoangcachtoida": 1.}
        return None

    def _buocvao(self, s):
        # Ngoài phó bản: có tổ đội và là trưởng nhóm mới vào (phó bản giữ theo tổ đội), rồi tới Đào Vong Khổ Dịch (theo bước Đi tới bản đồ:
        # phù / chạy tới Thuý Hoa Sơn, nói chuyện NPC lối vào)
        moitruong = self.moitruong
        if PHOBAN_MAP[s["phoban"]]["luachonvao"] == "give":
            # Phong Yêu Kính tự lập nhóm 1 người rồi mới mời thành viên (_buocvaophongyeu), không chờ Tổ đội tự động
            return self._buocvaophongyeu(s)
        if not moitruong.get_is_dangnamtrongnhom():
            s["trangthai"] = "chờ có tổ đội (bật Tổ đội tự động để bot tự lập nhóm)"
            return None
        if not moitruong.get_is_truongnhom():
            s["trangthai"] = "chờ mình làm trưởng nhóm (người đi phó bản phải là trưởng nhóm, thành viên bật Theo sau)"
            return None
        if s.get("lathanhvien") and not s["davao"]:
            # Từng là thành viên (bật ở thành viên): không bao giờ tự dẫn nhóm vào phó bản. Lúc đổi tổ đội, vừa rời nhóm cũ có thể đọc
            # thấy mình "trưởng nhóm" của nhóm tạm (từng làm 1 thành viên tự vào Thành Kiều riêng). Trưởng nhóm thật vẫn là nhân vật
            # chưa từng làm thành viên
            s["trangthai"] = "thành viên: chờ trưởng nhóm (đang là trưởng nhóm tạm, không tự vào phó bản)"
            return None
        cauhinh = PHOBAN_MAP[s["phoban"]]
        ten = cauhinh["ten"]
        s["trangthai"] = f"vào {ten} (vòng {s['sovong'] + 1})"
        if cauhinh["luachonvao"] is None:
            if not self._is_nhomdu(s):
                return None
            buoc = self._lapbuocditoibando(cauhinh["bandovao"], is_hoithanhphu = True)
            if buoc["loai"] == "toinoi":
                return None
            return self._thuchienbuocditoibando(buoc, cauhinh["bandovao"], None, f"[{ten.upper()}] Vào {ten}")
        # Thành Kiều: tới NPC, chọn lựa chọn vào (phải có vatphamvao trong hành trang, vào không mất) rồi Xác nhận, vận khí xong cả nhóm được đưa vào
        tennpc, x, y = cauhinh["npc"]
        if moitruong.get_idbandohientai() != cauhinh["bandonpc"]:
            buoc = self._lapbuocditoibando(cauhinh["bandonpc"], is_hoithanhphu = True, toadodich = (x, y))
            if buoc["loai"] in ("toinoi", "khongduong"):
                s["trangthai"] = f"không có đường tới {laytenbando(cauhinh['bandonpc'])}: {buoc['mota']}"
                return None
            return self._thuchienbuocditoibando(buoc, cauhinh["bandonpc"], (x, y), f"[{ten.upper()}] Vào {ten}")
        if time.time() < s.get("lucthulaivao", 0.):
            s["trangthai"] = f"vào {ten}: chờ thử lại ({int(s['lucthulaivao'] - time.time())}s)"
            return None
        vatpham = cauhinh["vatphamvao"]
        if vatpham and not s["hoithoai"]:
            soluongs = moitruong.get_soluongvatphamhanhtrangtheoten()
            if soluongs is not None and not any(vatpham in tenvp for tenvp in soluongs):
                baosuco(moitruong, "langlyson", f"⚠️ {ten}: hết {vatpham} trong hành trang, dừng tự động", khoa = f"{s['batdau']}|hetvatpham",
                        giancach = 0.)
                self._ketthuclanglyson(f"❌ Dừng: hết {vatpham}")
                return None
        if s["davao"]:
            # Đã vào 1 lần trong vòng này mà giờ ở ngoài (chết / rớt ra): vào lại, báo người dùng để ý
            self._baolanglyson(s, f"vaolai|{s['sovong']}", f"⚠️ {ten}: vòng {s['sovong'] + 1} bị ra khỏi phó bản giữa chừng, nói chuyện "
                                                          f"{tennpc} vào lại")
        if not s["hoithoai"] and not self._is_nhomdu(s):
            return None
        s["trangthai"] = f"vào {ten} (vòng {s['sovong'] + 1}): nói chuyện {tennpc}"
        ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y, luachon = cauhinh["luachonvao"], is_xacnhan = True)
        if ketqua == "xong":
            # Vận khí xong mà THOIGIANTHULAIVAO giây vẫn chưa được đưa vào (vận khí bị ngắt...) thì nói chuyện lại từ đầu
            s.setdefault("lucvankhivao", time.time())
            if time.time() - s["lucvankhivao"] > THOIGIANTHULAIVAO:
                self._logpb(s, f"Vận khí xong {THOIGIANTHULAIVAO:.0f}s chưa vào được phó bản, nói chuyện {tennpc} lại")
                s.pop("lucvankhivao", None)
                s["hoithoai"] = None
        elif ketqua == "loi":
            s["lucthulaivao"] = time.time() + THOIGIANTHULAIVAO
            self._baolanglyson(s, f"khongvao|{s['sovong']}", f"⚠️ {ten}: nói chuyện {tennpc} {SOLANTHUNOICHUYEN} lần chưa vào được "
                                                            f"(chưa bấm được Xác nhận? xem log [PHÓ BẢN]), {THOIGIANTHULAIVAO:.0f}s sau thử lại")
        return yeucau

    def _is_nhomdu(self, s):
        # Trưởng nhóm chỉ vào phó bản khi nhóm đã đủ người như vòng trước (sothanhvien, vòng đầu: ít nhất 2) và danh sách nhóm đứng yên
        # THOIGIANNHOMONDINH giây: lúc đổi tổ đội Tổ đội tự động mời từng người một, vào sớm là bỏ lại người chưa kịp vào nhóm (từng vào
        # khi mới có 2/4 người). Chờ quá THOIGIANBAONHOMTHIEU giây thì báo, vẫn chờ
        now = time.time()
        ids = tuple(sorted(i for i in self.moitruong.get_danhsachidnguoichoithanhviennhoms() or () if i))
        if ids != s.get("nhomdangxet"):
            s.update(nhomdangxet = ids, lucnhomdoi = now)
        s.setdefault("lucchonhom", now)
        canco = max(2, s.get("sothanhvien", 0))
        if len(ids) < canco:
            s["trangthai"] = f"vào {self._tenpb(s)}: chờ đủ {canco} người trong nhóm (đang có {len(ids)})"
            if now - s["lucchonhom"] > THOIGIANBAONHOMTHIEU:
                self._baolanglyson(s, f"nhomthieu|{s['sovong']}", f"⚠️ {self._tenpb(s)}: chờ {int(THOIGIANBAONHOMTHIEU)}s nhóm mới chỉ có "
                                                                 f"{len(ids)}/{canco} người, chưa vào phó bản")
            return False
        if now - s["lucnhomdoi"] < THOIGIANNHOMONDINH:
            s["trangthai"] = f"vào {self._tenpb(s)}: nhóm đủ {len(ids)} người, chờ ổn định"
            return False
        s.pop("lucchonhom", None)
        return True

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
                        self._logpb(s, f"Đủ thành viên sau {int(time.time() - s['lucchodoi'])}s, đánh {_tenboss(tenboss)}")
                    s.update(dudoi = True, lucchodoi = 0.)
            # Boss cuối (bước có cờ): không "tới nơi lâu không thấy thì coi như đã giết" (ra nhầm là mất phó bản); game báo hoàn thành là xong
            is_bosscuoi = len(buoc) > 4 and buoc[4]
            if is_bosscuoi and s["daxongphoban"]:
                ketqua, yeucau = "game báo hoàn thành phó bản", None
            else:
                ketqua, yeucau = self._danhboss(s, idbando, tenboss, x, y, is_bosscuoi)
            if ketqua:
                self._logpb(s, f"{tenbando}: xong {_tenboss(tenboss)} ({ketqua})")
                self._sangbuoc(s, idbando)
            return yeucau
        if loai == "noichuyen":
            _, tennpc, x, y = buoc
            s["trangthai"] = f"{tenbando}: nói chuyện {tennpc} ({x}, {y})"
            ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y, is_baokhongmenu = True)
            if ketqua == "xong":
                self._sangbuoc(s, idbando)
            elif ketqua == "khongmenu":
                # NPC không mở menu: đã làm bước này rồi (dis / mở lại bot làm lại từ đầu tầng), sang bước kế
                self._logpb(s, f"{tennpc} không mở menu {SOLANTHUNOICHUYEN} lần (đã khởi động rồi?), sang bước kế")
                self._sangbuoc(s, idbando)
            elif ketqua == "loi":
                # Nói mãi không vận khí: có thể boss trước đó chưa chết, quay lại bước trước
                self._logpb(s, f"{tennpc} {SOLANTHUNOICHUYEN} lần không vận khí, quay lại bước trước")
                s["buoc"][idbando] = max(0, i - 1)
                s["boss"] = None
            return yeucau
        if loai == "sangtang":
            idke = buoc[1]
            s["trangthai"] = f"{tenbando}: sang {laytenbando(idke)}"
            ketqua = self._lapbuocditoibando(idke)
            if ketqua["loai"] in ("toinoi", "khongduong"):
                return None
            return self._thuchienbuocditoibando(ketqua, idke, None, f"[{self._tenpb(s).upper()}] {tenbando}")
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
        self._logpb(s, f"Xong phó bản, ra {laytenbando(PHOBAN_MAP[s['phoban']]['bandonpc'])} nhận thưởng")
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
            boss.update(lucthay = now, vitri = moitruong.get_toado(diachi), lucgan = 0.)
        elif boss["lucthay"]:
            # Đã thấy boss mà giờ không thấy nữa: chỉ coi là đã giết khi mình đang đứng gần chỗ thấy boss lần cuối THOIGIANBOSSBIENMAT giây
            # (từng thấy boss thoáng qua ở mép tầm nhìn, chạy đi đánh quái khác, boss khuất tầm nhìn là tưởng đã giết). Đứng xa thì quay lại đó
            xboss, yboss = boss.get("vitri") or (x, y)
            if moitruong.get_khoangcachdiem(xboss, yboss) > KHOANGCACHTOIBOSS:
                boss["lucgan"] = 0.
                s["trangthai"] = f"{laytenbando(idbando)}: {_tenboss(tenboss)} khuất tầm nhìn, quay lại ({xboss}, {yboss})"
                return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (xboss, yboss, idbando), "khoangcachtoida": 1.}
            boss["lucgan"] = boss.get("lucgan") or now
            if now - boss["lucgan"] > THOIGIANBOSSBIENMAT:
                return "đã giết", None
            # Đang đếm THOIGIANBOSSBIENMAT giây ở chỗ thấy boss lần cuối: đứng đây (boss chết xa toạ độ cấu hình, từng rơi xuống "tới đánh"
            # chạy về toạ độ cấu hình, ra xa > KHOANGCACHTOIBOSS là mất mốc đếm, quay lại, rồi lại chạy đi... mãi không sang bước)
            s["chedo"] = "danhquai"
            s["trangthai"] = f"{laytenbando(idbando)}: không còn thấy {_tenboss(tenboss)} ở ({xboss}, {yboss}), chờ xác nhận đã giết"
            return None, None
        if diachi or moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIBOSS:
            # Tới nơi (hoặc thấy boss): đánh mọi quái quanh đó
            boss["luctoi"] = boss["luctoi"] or now
            s["chedo"] = "danhquai"
            self._batdanhquailanglyson(s)
            if not diachi and not boss["lucthay"] and now - boss["luctoi"] > THOIGIANCHOBOSS:
                if not is_bosscuoi:
                    return f"tới nơi {THOIGIANCHOBOSS:.0f}s không thấy, coi như đã giết", None
                self._baolanglyson(s, f"khongthayboss|{s['sovong']}", f"⚠️ {self._tenpb(s)}: tới {_tenboss(tenboss)} {THOIGIANCHOBOSS:.0f}s không thấy boss, "
                                                                     f"game cũng chưa báo hoàn thành phó bản: bot đứng chờ, không ra (xem giúp)")
                s["trangthai"] = f"{laytenbando(idbando)}: không thấy {_tenboss(tenboss)}, chưa có tin hoàn thành phó bản, đứng chờ (không ra)"
                return None, None
            s["trangthai"] = f"{laytenbando(idbando)}: đánh {_tenboss(tenboss)}" + ("" if diachi else " (chờ boss hiện)")
            # Bị đánh dạt ra xa toạ độ boss thì quay về (đánh quái vẫn ưu tiên hơn)
            if moitruong.get_khoangcachdiem(x, y) > KHOANGCACHTOIBOSS and not diachi:
                return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}
            return None, None
        s["trangthai"] = f"{laytenbando(idbando)}: tới đánh {_tenboss(tenboss)} ({x}, {y})"
        self._capnhatbuocdichuyen(f"{self._tenpb(s)}: tới {_tenboss(tenboss)} ({x}, {y})")
        return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}

    def _timbosssong(self, tenboss):
        # tenboss: chuỗi hoặc tuple các tên có thể gặp
        moitruong = self.moitruong
        tens = tenboss if isinstance(tenboss, tuple) else (tenboss,)
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi):
                continue
            if (moitruong.get_tendoituong(diachi) or "").strip() in tens and not moitruong.get_is_nhanvatdachet(diachi):
                return diachi
        return None

    def _noichuyenlls(self, s, tennpc, x, y, is_chovankhi = True, kiemtramenu = None, luachon = 0, is_xacnhan = False, is_baokhongmenu = False,
                      kiemtramenucuoi = None):
        # Tới cạnh NPC, "look" mở menu, chọn lựa chọn thứ luachon (đếm từ 0, trừ CLOSE; tuple: chọn xong chờ menu kế chọn tiếp). is_chovankhi: chọn xong phải thấy vận khí rồi hết
        # vận khí mới là xong (quá THOIGIANCHOVANKHILLS giây chưa vận khí thì nói lại, quá SOLANTHUNOICHUYEN lần -> "loi"); không thì chọn
        # xong là xong. kiemtramenu(lời NPC) False thì không chọn -> "tuchoi". is_xacnhan: chọn xong game hỏi lại "Xác Nhận / Hủy Bỏ" thì
        # bấm Xác Nhận (_xacnhanlls). is_baokhongmenu: "look" SOLANTHUNOICHUYEN lần NPC không mở menu -> "khongmenu". kiemtramenucuoi: như
        # kiemtramenu nhưng xét lời menu cuối của luachon tuple (vd Phong Yêu Kính "1. Tiến vào" rồi mới tới "...đã mở Phong Yêu Kính...").
        # -> (None | "xong" | "loi" | "tuchoi" | "khongmenu", yêu cầu di chuyển)
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
            if is_xacnhan and self._xacnhanlls(h, tennpc, now):
                return None, None
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
            h.update(buoc = "chon", luc = now, cap = 0)
            return None, None
        # "chon": chờ menu hiện
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung:
            if now - h["luc"] > THOIGIANCHOMENULLS:
                h["buoc"] = "look"
                # NPC không mở menu (Cơ Quan Thạch đã khởi động rồi, dis vào lại làm từ đầu tầng): từng "look" mãi không thôi, đứng đực ra.
                # is_baokhongmenu: quá SOLANTHUNOICHUYEN lần thì báo nơi gọi
                h["solankhongmenu"] = h.get("solankhongmenu", 0) + 1
                if is_baokhongmenu and h["solankhongmenu"] >= SOLANTHUNOICHUYEN:
                    s["hoithoai"] = None
                    return "khongmenu", None
            return None, None
        h["solankhongmenu"] = 0
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        moitruong._inlog(f"[PHÓ BẢN] Menu {tennpc}: {noidung[:80]!r} {lenhs}")
        chons = luachon if isinstance(luachon, tuple) else (luachon,)
        cap = h.get("cap", 0)
        luachon = chons[cap]
        if (kiemtramenu and cap == 0 and not kiemtramenu(noidung)) or (kiemtramenucuoi and cap == len(chons) - 1 and not kiemtramenucuoi(noidung)):
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            s["hoithoai"] = None
            return "tuchoi", None
        if len(lenhs) > luachon:
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            if is_xacnhan:
                # Hộp xác nhận đang có trước khi chọn (của lần trước): không tính là hộp của lần này
                h["hopcu"] = moitruong.get_hopxacnhannpc()
            moitruong.action_thucthicaulenh(lenhs[luachon])
            moitruong._inlog(f"[PHÓ BẢN] {tennpc}: chọn lựa chọn {luachon + 1}: {lenhs[luachon]!r}")
            if cap + 1 < len(chons):
                # Còn menu kế (vd "1. Nhận thưởng" sau "4. Nhận thưởng"): chờ menu đó hiện rồi chọn tiếp
                h.update(buoc = "chon", luc = now, cap = cap + 1)
                return None, None
        elif lenhs:
            moitruong._inlog(f"[PHÓ BẢN] {tennpc}: menu chỉ có {len(lenhs)} lựa chọn, không có lựa chọn {luachon + 1}")
        h.update(buoc = "cho", luc = now, solan = h["solan"] + 1, vankhi = False, daxacnhan = False)
        return None, None

    def _xacnhanlls(self, h, tennpc, now):
        # Chọn xong game mở hộp xác nhận riêng (không phải menu hội thoại, moitruong.get_hopxacnhannpc): "Bạn sẽ sử dụng Hạt Mè Khai Môn để
        # tiến vào Thành Kiều. Xác Nhận / Hủy Bỏ". Hộp mới hiện (khác hộp có trước khi chọn) thì gửi lệnh nút Xác Nhận của hộp (vd
        # "tallk 15e6# welcome.4") rồi đóng hộp như game tự đóng sau khi bấm nút.
        # -> True: vừa xác nhận (lượt này không làm gì thêm)
        moitruong = self.moitruong
        if h.get("daxacnhan"):
            return False
        hop = moitruong.get_hopxacnhannpc()
        if not hop[0] or not hop[1].startswith("tallk ") or hop == h.get("hopcu"):
            return False
        moitruong.action_ngatdichuyen()
        moitruong.action_thucthicaulenh(hop[1])
        moitruong.action_donghopxacnhannpc()
        moitruong._inlog(f"[PHÓ BẢN] {tennpc}: bấm Xác Nhận ({hop[1]!r}), đóng hộp")
        h.update(daxacnhan = True, luc = now)
        return True

    def _buocnhanthuong(self, s):
        # Hồi Thành Phù ra khỏi phó bản (is_roiphoban), phù / chạy tới bản đồ NPC, nói chuyện chọn lựa chọn nhận thưởng (Lăng Ly Sơn: Thuý Hoa
        # Sơn, Đào Vong Khổ Dịch "1. Lĩnh nhận phần thưởng"; Thành Kiều: Tần Quốc, Thảo Nghịch Tướng Quân "4. Nhận thưởng")
        moitruong = self.moitruong
        cauhinh = PHOBAN_MAP[s["phoban"]]
        if cauhinh["luachonthuong"] is None:
            return self._buocraphongyeu(s)
        tennpc, x, y = cauhinh["npc"]
        bandonpc = cauhinh["bandonpc"]
        if moitruong.get_idbandohientai() != bandonpc:
            s["trangthai"] = f"ra {laytenbando(bandonpc)} nhận thưởng"
            buoc = self._lapbuocditoibando(bandonpc, is_hoithanhphu = True, is_roiphoban = True, toadodich = (x, y))
            if buoc["loai"] in ("toinoi", "khongduong"):
                s["trangthai"] = f"không có đường ra {laytenbando(bandonpc)}: {buoc['mota']}"
                return None
            return self._thuchienbuocditoibando(buoc, bandonpc, (x, y), f"[{cauhinh['ten'].upper()}] Nhận thưởng")
        s["trangthai"] = f"nhận thưởng ở {tennpc}"
        if time.time() < s.get("lucthulaithuong", 0.):
            return None
        ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y, is_chovankhi = False, luachon = cauhinh["luachonthuong"],
                                            kiemtramenu = self._is_menunhanthuong if cauhinh["is_kiemtrathuong"] else None)
        if ketqua == "tuchoi":
            # NPC không có lời chúc mừng / phần thưởng: chưa chắc phó bản đã xong => KHÔNG giải tán tổ đội (giải tán là mất phó bản), thử
            # lại vài lần rồi dừng hẳn, báo người dùng xem
            s["solantuchoi"] = s.get("solantuchoi", 0) + 1
            if s["solantuchoi"] < SOLANTHUNOICHUYEN:
                s["lucthulaithuong"] = time.time() + 10.
                self._logpb(s, f"{tennpc} chưa có phần thưởng, 10s nữa hỏi lại (lần {s['solantuchoi']})")
                return None
            baosuco(moitruong, "langlyson", f"⚠️ {cauhinh['ten']}: {tennpc} không có phần thưởng sau {s['solantuchoi']} lần hỏi, chưa chắc phó bản đã "
                                            f"xong nên KHÔNG giải tán tổ đội, dừng tự động (xem giúp)", khoa = f"{s['batdau']}|tuchoi", giancach = 0.)
            self._ketthuclanglyson(f"❌ Dừng: {tennpc} không có phần thưởng, không giải tán tổ đội")
            return None
        if ketqua == "xong":
            s["sovong"] += 1
            # Vòng sau phải đủ chừng này người mới vào (_is_nhomdu): mình + mọi người từng ở trong nhóm vòng này
            s["sothanhvien"] = len(s["thanhviens"]) + 1
            s.pop("solantuchoi", None)
            self._logpb(s, f"Xong vòng {s['sovong']} ({int((time.time() - s['lucbatdauvong']) // 60)} phút), chờ thành viên lĩnh "
                           f"thưởng rồi đổi tổ đội")
            # Mã thưởng của vòng này báo cho thành viên cùng máy (get_khoathuonglanglyson qua shared_data): ai chưa lĩnh mã này thì tự lĩnh.
            # Phần đầu mã là phó bản để thành viên biết tới NPC nào
            s.update(giaidoan = "doinhom", hoithoai = None, tattodoi = False, is_daroinhom = False, lucnhanthuong = time.time(),
                     khoathuong = f"{s['phoban']}|{moitruong.get_idnguoichoi()}|{int(s['batdau'])}|{s['sovong']}")
        return yeucau

    def get_khoathuonglanglyson(self):
        # Mã thưởng vòng vừa xong (trưởng nhóm đã lĩnh, chưa giải tán nhóm) cho thành viên theo sau biết mà tự lĩnh, không có thì ""
        s = self._langlyson
        return s["khoathuong"] if s and s["giaidoan"] == "doinhom" and not s["is_daroinhom"] else ""

    def _laythanhvienchualanh(self, khoathuong):
        # Tên thành viên trong nhóm chạy cùng máy (shared_data, gồm cả máy khác nối qua LAN - lan_xq) chưa báo đã lĩnh mã thưởng này.
        # Thành viên ở máy không nối LAN thì không biết được, bỏ qua
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
        # Thành viên theo sau: trưởng nhóm (người được theo sau, cùng máy) vừa lĩnh thưởng phó bản (mã thưởng trong shared_data, phần đầu là
        # phó bản) mà mình chưa lĩnh mã đó thì tới NPC nhận thưởng tự lĩnh. Chỉ làm khi đã ở bản đồ NPC (ra khỏi phó bản / tới đó là theo
        # sau lo). -> False: không có gì phải lĩnh (theo sau như thường); None / yêu cầu di chuyển: đang lĩnh
        info = self._laythongtinmuctieutheosaucuasokhac()
        khoathuong = info.get("_khoathuonglanglyson") if info else ""
        if not khoathuong or khoathuong == self._khoathuonglanglysondalanh:
            self._lanhthuonglanglyson = None
            return False
        cauhinh = PHOBAN_MAP.get(khoathuong.split("|", 1)[0]) or PHOBAN_MAP["langlyson"]
        moitruong = self.moitruong
        if moitruong.get_idbandohientai() != cauhinh["bandonpc"] or moitruong.get_is_nhanvatdachet():
            return False
        if moitruong.get_is_dangvankhi() or time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        tennpc, x, y = cauhinh["npc"]
        s = self._lanhthuonglanglyson
        if not s or s["khoa"] != khoathuong:
            s = self._lanhthuonglanglyson = {"khoa": khoathuong, "hoithoai": None}
            moitruong._inlog(f"[{cauhinh['ten'].upper()}] Trưởng nhóm đã lĩnh thưởng, tới {tennpc} tự lĩnh")
        self._capnhatbuocdichuyen(f"{cauhinh['ten']}: tới {tennpc} lĩnh thưởng")
        ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y, is_chovankhi = False, luachon = cauhinh["luachonthuong"],
                                            kiemtramenu = self._is_menunhanthuong if cauhinh["is_kiemtrathuong"] else None)
        if ketqua in ("xong", "tuchoi"):
            self._khoathuonglanglysondalanh = khoathuong
            self._lanhthuonglanglyson = None
            moitruong._inlog(f"[{cauhinh['ten'].upper()}] {'Đã lĩnh thưởng' if ketqua == 'xong' else f'{tennpc} không có phần thưởng cho mình'}")
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
        if s and s["giaidoan"] == "vao" and s.get("momophongyeu"):
            # Phong Yêu Kính đang lập nhóm 1 người để give: thành viên nhóm todoi tạm nghỉ Tổ đội tự động, rời nhóm (không kéo nhau vào nhóm)
            return list(s.get("thanhvienpy") or ())
        return []

    def get_is_tamtattodoilanglyson(self):
        # Tổ đội tự động phải tạm nghỉ: mình đang giải tán tổ đội cũ, hoặc trưởng nhóm cùng máy đang giải tán mà mình là thành viên vòng đó
        return bool(self.get_dsidtattodoilanglyson()) or self._is_trongdanhsachcuasokhac("_langlysontattodoi")

    def action_roinhomlanglyson(self):
        # Gọi đầu Tổ đội tự động: đang phải tạm nghỉ thì không mời / nhận lời mời / xin vào nhóm, còn trong nhóm thì rời (trưởng nhóm rời
        # là giải tán). -> True khi đang tạm nghỉ (Tổ đội tự động bỏ qua lượt này)
        if self._langlyson and self._langlyson.get("momophongyeu"):
            # Người give Phong Yêu Kính đang tự lập nhóm 1 người (_buocvaophongyeu lo rời / lập nhóm): Tổ đội tự động nghỉ, không tự rời
            return True
        if not self.get_is_tamtattodoilanglyson():
            return False
        if self.moitruong.get_is_dangnamtrongnhom() and time.time() - self._thoidiemroinhomlanglyson > GIANCACHROINHOM:
            self._thoidiemroinhomlanglyson = time.time()
            self.moitruong._inlog("[PHÓ BẢN] Rời nhóm để giải tán tổ đội cũ (Tổ đội tự động tạm nghỉ)")
            self.moitruong.action_thoatkhoinhom()
        return True

    def _buocdoinhom(self, s):
        # Phó bản cũ giữ theo tổ đội: trưởng nhóm rời nhóm (= giải tán), chờ Tổ đội tự động lập nhóm mới rồi vào vòng sau
        moitruong = self.moitruong
        is_trongnhom = moitruong.get_is_dangnamtrongnhom()
        if is_trongnhom and not s["is_daroinhom"]:
            # Mỗi thành viên tự lĩnh thưởng của mình: chờ các thành viên cùng máy lĩnh xong (tối đa THOIGIANCHOTHANHVIENLANH giây) mới giải tán
            # Không có mã thưởng (Phong Yêu Kính không có thưởng phải lĩnh): không chờ ai
            chualanhs = self._laythanhvienchualanh(s["khoathuong"]) if s["khoathuong"] else []
            conlai = THOIGIANCHOTHANHVIENLANH - (time.time() - s["lucnhanthuong"])
            if chualanhs and conlai > 0:
                s["trangthai"] = f"chờ {', '.join(chualanhs)} lĩnh thưởng (còn {int(conlai)}s)"
                return None
            if chualanhs:
                self._baolanglyson(s, f"chualanh|{s['sovong']}", f"⚠️ {self._tenpb(s)}: {', '.join(chualanhs)} chưa lĩnh thưởng vòng {s['sovong']} "
                                                                 f"sau {int(THOIGIANCHOTHANHVIENLANH)}s, vẫn giải tán tổ đội")
        if not s["is_daroinhom"]:
            # Giải tán: tạm tắt Tổ đội tự động ở mình và mọi thành viên vòng này cùng máy (không thì nó kéo nhau vào lại nhóm cũ, nhóm cũ
            # còn giữ phó bản đã xong), ai còn trong nhóm thì tự rời (action_roinhomlanglyson). Hết người trong nhóm cũ (hoặc quá
            # THOIGIANCHOGIAITAN giây) thì bật lại để Tổ đội tự động lập nhóm mới
            if not s.get("tattodoi"):
                s.update(tattodoi = True, luctattodoi = time.time())
                self._logpb(s, "Tạm tắt Tổ đội tự động, mọi người rời nhóm để giải tán tổ đội cũ")
            conlais = self._laythanhvienconnhom(s)
            if is_trongnhom:
                conlais = [moitruong.get_tendoituong() or "mình"] + conlais
            if conlais and time.time() - s["luctattodoi"] < THOIGIANCHOGIAITAN:
                s["trangthai"] = f"giải tán tổ đội cũ (tạm tắt Tổ đội tự động), còn trong nhóm: {', '.join(conlais)}"
                return None
            if conlais:
                self._baolanglyson(s, f"giaitan|{s['sovong']}", f"⚠️ {self._tenpb(s)}: {int(THOIGIANCHOGIAITAN)}s chưa giải tán hết tổ đội cũ "
                                                                f"({', '.join(conlais)} còn trong nhóm), vẫn lập nhóm mới")
            s.update(tattodoi = False, is_daroinhom = True)
            self._logpb(s, "Đã giải tán tổ đội cũ, bật lại Tổ đội tự động để lập nhóm mới")
            return None
        if not is_trongnhom and PHOBAN_MAP[s["phoban"]]["luachonvao"] != "give":
            # (Phong Yêu Kính tự lập nhóm 1 người ở vòng sau, không chờ Tổ đội tự động)
            s["trangthai"] = "đã giải tán tổ đội, chờ lập tổ đội mới"
            if not self._is_tudongtodoi:
                self._baolanglyson(s, "todoi", f"⚠️ {self._tenpb(s)}: chưa bật Tổ đội tự động, lập tổ đội mới bằng tay để đi vòng sau")
            return None
        s.update(giaidoan = "vao", buoc = {}, boss = None, hoithoai = None, lucbatdauvong = time.time(), thanhviens = {}, dudoi = False,
                 lucchodoi = 0., lucmoi = {}, diemvao = {}, daxongphoban = False, davao = False)
        # Phong Yêu Kính: vòng mới được give món mới
        for khoa in ("py", "giao", "dagive", "dolamkim", "lucchonvaopy", "solanvaolaipy", "solanchuyentui", "lucchuyentui", "dadescpy",
                     "lucdagive", "lucnhom1"):
            s.pop(khoa, None)
        self._logpb(s, f"Có tổ đội mới, bắt đầu vòng {s['sovong'] + 1}")
        return None

    # --- Phong Yêu Kính ----------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _phantichdolamkim(mota, ten, cauhinh = None):
        # Mô tả thô (còn mã màu) của 1 ô hành trang -> (cấp, giá bán) nếu là món được phép đem đốt theo cauhinh (taicauhinhphongyeu; không
        # truyền thì mặc định: chỉ Lam Kim chưa giám định), không thì None. Cấp tối thiểu theo cấp nhân vật xét ở _chondolamkim.
        # Dòng tên trong mô tả phải khớp tên ô (tên ô tối đa 31 byte nên chỉ so đầu): mô tả giữ theo ô, đồ chuyển chỗ có thể còn mô tả cũ
        cauhinh = cauhinh or CAUHINHPHONGYEU_MACDINH
        mamaus = ((MAMAULAMKIM,) if cauhinh["is_lamkim"] else ()) + ((MAMAUHOANGKIM,) if cauhinh["is_hoangkim"] else ())
        if not mota or not mamaus or not mota.startswith(mamaus):
            return None
        sach = unicodedata.normalize("NFC", re.sub(r"\x1b.", "", mota))
        dongs = [d.strip() for d in sach.split("\n") if d.strip()]
        ten = unicodedata.normalize("NFC", ten or "").strip()
        if len(dongs) < 2 or not ten or not dongs[0].startswith(ten) or not dongs[1].startswith("［"):
            return None
        if "đã Phong Ấn" in dongs[0] or "Khoá" in dongs[0] or "Khóa" in dongs[0]:
            return None
        # Chỉ đồ chưa giám định: đồ có sao (★) cũng là đồ đã làm gì đó, bỏ luôn; tắt thì đốt cả đồ đã giám định
        if cauhinh["is_chichuagiamdinh"] and ("Chưa giám định" not in sach or "★" in sach):
            return None
        tenthuong = dongs[0].lower()
        if any(unicodedata.normalize("NFC", t).lower() in tenthuong for t in cauhinh["khongdot"]):
            return None
        if cauhinh["chidot"] and not any(unicodedata.normalize("NFC", t).lower() in tenthuong for t in cauhinh["chidot"]):
            return None
        khop = re.search(r"Cấp độ sử dụng\s*[:：]\s*cấp\s*(\d+)", sach)
        if not khop or int(khop.group(1)) < CAPDOLAMKIMTOITHIEU:
            return None
        gia = re.search(r"Giá bán ra\s*[:：]\s*(\d+)", sach)
        return int(khop.group(1)), int(gia.group(1)) if gia else 0

    def _laynhompy(self):
        # Nhóm đi Phong Yêu Kính theo cấu hình Tổ đội tự động (todoi.json): nhóm có mình, chỉ tính người đang online (mình, hoặc cửa sổ
        # cùng máy / máy khác nối LAN còn cập nhật). -> (ID người give = người online đứng đầu nhóm, [ID các thành viên online khác]).
        # Mình không có trong nhóm nào thì mình tự give, đi 1 mình. Đọc shared_data tốn (chép qua Manager) nên nhớ 1s
        thoidiem, ketqua = self._bonhonhompy
        if time.time() - thoidiem < 1. and ketqua:
            return ketqua
        idtoi = self.moitruong.get_idnguoichoi()
        nhom = next((list(n) for n in laynhomtodoitudongs() if idtoi in n), [idtoi])
        onlines = {idtoi}
        try:
            for info in list(self.shared_data.values()) if self.shared_data is not None else ():
                if isinstance(info, dict) and time.time() - info.get("thoidiemcapnhat", 0.) <= 5. and info.get("idnguoichoi"):
                    onlines.add(info["idnguoichoi"])
        except Exception:
            pass
        nhom = [i for i in nhom if i in onlines]
        self._bonhonhompy = (time.time(), (nhom[0], nhom[1:]))
        return self._bonhonhompy[1]

    def _moithanhvienpy(self, s):
        # Người give đã mở Phong Yêu Kính: mời thành viên online của nhóm todoi (shared_data, gồm cả máy khác qua LAN; đọc lại mỗi lần vì
        # vừa bật có thể chưa có dữ liệu LAN, từng vào phó bản 1 mình không mời ai) chưa có trong nhóm, mỗi người mỗi GIANCACHMOIPY giây.
        # Mời được từ xa, không cần đứng cạnh; gọi cả khi đã ở trong phó bản (thành viên vào nhóm sau tự tới Tả Khâu Minh "look" để vào)
        moitruong = self.moitruong
        now = time.time()
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ())
        s["thanhvienpy"] = self._laynhompy()[1]
        for idtv in s["thanhvienpy"]:
            if idtv not in trongnhoms and now - s["lucmoi"].get(idtv, 0.) > GIANCACHMOIPY:
                s["lucmoi"][idtv] = now
                moitruong.action_moihoacxinvaonhom(idtv)
                return

    def _thanhvienchuavaonhompy(self, s):
        # Tên thành viên online nhóm todoi chưa vào nhóm của mình (người give đã mở Phong Yêu Kính, đang mời)
        trongnhoms = set(self.moitruong.get_danhsachidnguoichoithanhviennhoms() or ())
        return [self._laytencungmay(i) or f"ID {i}" for i in s.get("thanhvienpy") or () if i not in trongnhoms]

    def _thanhvienvaophongyeu(self, s, idgive):
        # Thành viên (không phải người give) ở ngoài phó bản: bỏ boss / điểm dò vòng trước, tới đứng gần Tả Khâu Minh chờ được mời. Đã vào
        # nhóm người give (người give chỉ mời sau khi đã mở) thì tự "look" Tả Khâu Minh: vào nhóm sau lúc mở thì game KHÔNG tự hiện menu
        # "ta muốn vào", phải nói chuyện NPC mới có "Đội nhóm các ngươi đã mở Phong Yêu Kính..." -> "1. Đúng vậy, ta muốn vào"
        moitruong = self.moitruong
        now = time.time()
        cauhinh = PHOBAN_MAP[s["phoban"]]
        ten = cauhinh["ten"]
        tennpc, x, y = cauhinh["npc"]
        tengive = self._laytencungmay(idgive) or idgive
        s.pop("py", None)
        s["diemvao"] = {}
        s.update(momophongyeu = False, lathanhvien = True)
        if moitruong.get_idbandohientai() != cauhinh["bandonpc"]:
            s["trangthai"] = f"thành viên: tới {laytenbando(cauhinh['bandonpc'])} chờ {tengive} mở {ten}"
            buoc = self._lapbuocditoibando(cauhinh["bandonpc"], is_hoithanhphu = True, toadodich = (x, y))
            if buoc["loai"] in ("toinoi", "khongduong"):
                return None
            return self._thuchienbuocditoibando(buoc, cauhinh["bandonpc"], (x, y), f"[{ten.upper()}] Thành viên")
        if not moitruong.get_is_dangnamtrongnhom() or moitruong.get_idnguoichoitruongnhom() != idgive:
            s["hoithoai"] = None
            s["trangthai"] = f"thành viên: chờ {tengive} mở {ten} rồi mời vào nhóm"
            if moitruong.get_khoangcachdiem(x, y) > KHOANGCACHNOICHUYENLLS * 2:
                return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
            return None
        if now < s.get("luclooktv", 0.):
            s["trangthai"] = f"thành viên: đã ở nhóm {tengive}, chờ được đưa vào {ten} ({int(s['luclooktv'] - now)}s)"
            return None
        s["trangthai"] = f"thành viên: nói chuyện {tennpc} vào {ten}"
        # Menu chính "1. Tiến vào Phong Yêu Kính" -> đội đã mở thì "Đội nhóm các ngươi đã mở Phong Yêu Kính..." "1. Đúng vậy, ta muốn vào"
        # (vào lúc nào cũng được, không chỉ lúc menu tự hiện khi vừa mở)
        ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y, is_chovankhi = False, luachon = LUACHONVAOLAIPY,
                                            kiemtramenucuoi = lambda noidung: LOIMENUVAOPHONGYEU in noidung.lower())
        if ketqua == "xong":
            self._logpb(s, f"Thành viên: đã chọn vào {ten} ở {tennpc}")
            s["luclooktv"] = time.time() + GIANCACHLOOKTHANHVIENPY
        elif ketqua == "tuchoi":
            # Chưa mở (người give chưa xác nhận xong): chờ rồi hỏi lại
            s["luclooktv"] = time.time() + GIANCACHLOOKTHANHVIENPY
        return yeucau

    def _buocvaophongyeu(self, s):
        # Vào Phong Yêu Kính theo nhóm todoi. Chỉ người online đứng đầu nhóm todoi give; người khác chờ được mời (_xulymenuphongyeu tự đồng
        # ý lời mời của người đó, chọn "ta muốn vào"). Người give:
        #   1. tới Chu Quốc (252, 160) Tả Khâu Minh, tạm nghỉ Tổ đội tự động của cả nhóm (momophongyeu: thành viên rời nhóm, không kéo nhau
        #      vào nhóm), mình rời nhóm đang có người khác, lập nhóm 1 người "team + <ID mình>"
        #   2. give + xác nhận (_giaophongyeu)
        #   3. mời từng thành viên (Tổ đội tự động cũng chạy lại), đủ người (hoặc quá THOIGIANCHOMOIPY giây) mới chọn "ta muốn vào"
        moitruong = self.moitruong
        now = time.time()
        cauhinh = PHOBAN_MAP[s["phoban"]]
        ten = cauhinh["ten"]
        tennpc, x, y = cauhinh["npc"]
        idtoi = moitruong.get_idnguoichoi()
        if now - s["batdau"] < THOIGIANDOCNHOMPY:
            # Vừa bật: dữ liệu cửa sổ máy khác (LAN) chưa về, đọc ngay thì tưởng mình đứng đầu nhóm (từng làm Thọ tự rời nhóm lập nhóm 1
            # người give trong khi ThiênĐạo mới là người give)
            s["trangthai"] = f"vào {ten}: chờ đọc nhóm Tổ đội tự động ({int(THOIGIANDOCNHOMPY - (now - s['batdau']))}s)"
            return None
        idgive, thanhviens = self._laynhompy()
        if idgive != idtoi:
            return self._thanhvienvaophongyeu(s, idgive)
        s["thanhvienpy"] = thanhviens
        if moitruong.get_idbandohientai() != cauhinh["bandonpc"]:
            s["trangthai"] = f"vào {ten}: tới {laytenbando(cauhinh['bandonpc'])}"
            buoc = self._lapbuocditoibando(cauhinh["bandonpc"], is_hoithanhphu = True, toadodich = (x, y))
            if buoc["loai"] in ("toinoi", "khongduong"):
                s["trangthai"] = f"không có đường tới {laytenbando(cauhinh['bandonpc'])}: {buoc['mota']}"
                return None
            return self._thuchienbuocditoibando(buoc, cauhinh["bandonpc"], (x, y), f"[{ten.upper()}] Vào {ten}")
        if now < s.get("lucthulaivao", 0.):
            s["trangthai"] = f"vào {ten}: chờ thử lại ({int(s['lucthulaivao'] - now)}s)"
            return None
        if s.get("dagive"):
            # Đã mở: mời thành viên, chờ đủ người rồi mới vào (thành viên vào sau cũng được menu riêng nhưng đi cùng cho chắc)
            s["momophongyeu"] = False
            self._moithanhvienpy(s)
            chuavaos = self._thanhvienchuavaonhompy(s)
            if chuavaos and not s["davao"] and now - s.get("lucdagive", now) < THOIGIANCHOMOIPY:
                s["trangthai"] = f"vào {ten}: đã mở, mời thành viên vào nhóm ({', '.join(chuavaos)} chưa vào)"
                return None
            return self._giaophongyeu(s, tennpc, x, y)
        # Chưa give: phải ở nhóm chỉ có mình
        s["momophongyeu"] = True
        if s.get("giao"):
            return self._giaophongyeu(s, tennpc, x, y)
        ids = [i for i in moitruong.get_danhsachidnguoichoithanhviennhoms() or () if i]
        if moitruong.get_is_dangnamtrongnhom():
            if not moitruong.get_is_truongnhom() or any(i != idtoi for i in ids):
                s["trangthai"] = f"vào {ten}: rời nhóm cũ để lập nhóm 1 người"
                if now - s.get("lucnhom1", 0.) > GIANCACHLAPNHOMPY:
                    s["lucnhom1"] = now
                    self._logpb(s, "Rời nhóm đang có người khác để lập nhóm 1 người give đồ")
                    moitruong.action_thoatkhoinhom()
                return None
        else:
            s["trangthai"] = f"vào {ten}: lập nhóm 1 người"
            if now - s.get("lucnhom1", 0.) > GIANCACHLAPNHOMPY:
                s["lucnhom1"] = now
                self._logpb(s, f"Lập nhóm 1 người (team + {idtoi})")
                moitruong.action_thucthicaulenh(f"team + {idtoi}")
            return None
        return self._giaophongyeu(s, tennpc, x, y)

    def _laycapdolamkimtoithieu(self):
        # Cấp đồ thấp nhất được đốt: cấp nhân vật - caphonnhanvat (giao diện), không dưới CAPDOLAMKIMTOITHIEU
        return max(CAPDOLAMKIMTOITHIEU, (self.moitruong.get_capdonhanvat() or 0) - taicauhinhphongyeu()["caphonnhanvat"])

    def _chondolamkim(self, s):
        # Món đem đốt: (cấp, giá, ô, id đối tượng, tên) cấp thấp / rẻ nhất trong túi (không xét đồ đang mặc), "doc" khi còn ô chưa có mô
        # tả (đã gửi desc, chờ máy chủ trả; THOIGIANCHODESCPY giây chưa có thì gửi lại, quá SOLANDESCPY lần thì bỏ ô đó), None khi không có
        # món nào. Đọc mô tả THÔ (giữ mã màu): get_motavatphamhanhtrangcosan bỏ hết mã màu nên không bao giờ thấy \x1bC (từng báo hết đồ
        # Lam Kim khi túi còn đầy)
        moitruong = self.moitruong
        now = time.time()
        dadesc = s.setdefault("dadescpy", {})
        ketquas, sodesc, soguidesc = [], 0, 0
        captoithieu = self._laycapdolamkimtoithieu()
        cauhinh = taicauhinhphongyeu()
        for ten, mons in moitruong.get_danhsachvatphamhanhtrang_map().items():
            if not ten:
                continue
            for vitri, iddoituong in mons:
                if not iddoituong or vitri >= VITRITRANGBIDAUTIEN:
                    continue
                mota = moitruong.get_motathovatphamhanhtrangcosan(vitri)
                if not mota:
                    lucgui, solan = dadesc.get((vitri, iddoituong), (0., 0))
                    if now - lucgui <= THOIGIANCHODESCPY:
                        sodesc += 1
                    elif solan < SOLANDESCPY:
                        sodesc += 1
                        if soguidesc < SODESCMOILUOT:
                            soguidesc += 1
                            dadesc[(vitri, iddoituong)] = (now, solan + 1)
                            moitruong.truyvan_motavatphamhanhtrang(vitri)
                    continue
                phantich = self._phantichdolamkim(mota, ten, cauhinh)
                if phantich and phantich[0] >= captoithieu:
                    ketquas.append((*phantich, vitri, iddoituong, ten))
        if sodesc:
            return "doc"
        return min(ketquas) if ketquas else None

    def _giaophongyeu(self, s, tennpc, x, y):
        # Trưởng nhóm ở Chu Quốc: chọn món Lam Kim, đưa lên hành trang 1, tới cạnh Tả Khâu Minh give, menu hỏi thiêu đốt đúng lời thì chọn
        # "1. Đúng vậy, ta muốn đi" (lời lạ thì đóng, không xác nhận). Mỗi vòng chỉ đốt 1 món: đốt rồi mà chưa vào được thì chỉ "look" hỏi
        # lại menu "đã mở Phong Yêu Kính", tuyệt đối không give thêm. -> yêu cầu di chuyển hoặc None
        moitruong = self.moitruong
        now = time.time()
        ten = self._tenpb(s)
        if s.get("dagive"):
            if now - s.get("lucchonvaopy", 0.) < THOIGIANCHOVAOPHONGYEU:
                s["trangthai"] = f"vào {ten} (vòng {s['sovong'] + 1}): đã mở, chờ được đưa vào ({int(now - s['lucchonvaopy'])}s)"
                return None
            s["trangthai"] = f"vào {ten} (vòng {s['sovong'] + 1}): đã đốt đồ, hỏi lại {tennpc} để vào"
            ketqua, yeucau = self._noichuyenlls(s, tennpc, x, y, is_chovankhi = False, luachon = LUACHONVAOLAIPY,
                                                kiemtramenucuoi = lambda noidung: any(k in noidung.lower() for k in
                                                                                      (LOIMENUVAOPHONGYEU, LOIMENUDOITHANHVIENPY)))
            if ketqua == "xong":
                s["lucchonvaopy"] = time.time()
                s["solanvaolaipy"] = s.get("solanvaolaipy", 0) + 1
                if s["solanvaolaipy"] > SOLANTHUNOICHUYEN:
                    baosuco(moitruong, "langlyson", f"⚠️ {ten}: chọn vào {SOLANTHUNOICHUYEN} lần chưa được đưa vào, dừng tự động (xem giúp)",
                            khoa = f"{s['batdau']}|khongvaopy", giancach = 0.)
                    self._ketthuclanglyson(f"❌ Dừng: chọn vào {SOLANTHUNOICHUYEN} lần chưa được đưa vào")
            elif ketqua == "tuchoi":
                baosuco(moitruong, "langlyson", f"⚠️ {ten}: đã đốt đồ mà {tennpc} không cho vào, dừng tự động (không đốt thêm, xem giúp)",
                        khoa = f"{s['batdau']}|tuchoipy", giancach = 0.)
                self._ketthuclanglyson(f"❌ Dừng: đã đốt đồ mà {tennpc} không cho vào")
            return yeucau
        d = s.get("dolamkim")
        if d and moitruong.get_iddoituongvatphamhanhtrang(d["vitri"]) != d["id"]:
            # Món đã chọn đổi chỗ (vừa chuyển lên hành trang 1): tìm lại theo id
            vitris = [v for mons in moitruong.get_danhsachvatphamhanhtrang_map().values() for v, i in mons
                      if i == d["id"] and v < VITRITRANGBIDAUTIEN]
            if vitris:
                d["vitri"] = vitris[0]
            else:
                d = s["dolamkim"] = None
                s["giao"] = None
        if not d:
            chon = self._chondolamkim(s)
            if chon == "doc":
                s["trangthai"] = f"vào {ten}: đọc mô tả hành trang tìm đồ Lam Kim"
                return None
            if not chon:
                captoithieu = self._laycapdolamkimtoithieu()
                baosuco(moitruong, "langlyson", f"⚠️ {ten}: hết đồ được phép đốt (cấp ≥ {captoithieu}, xem cấu hình đồ đem đốt) trong hành trang, "
                                                f"dừng tự động", khoa = f"{s['batdau']}|hetdopy", giancach = 0.)
                self._ketthuclanglyson(f"❌ Dừng: hết đồ được phép đốt (cấp ≥ {captoithieu})")
                return None
            cap, gia, vitri, iddoituong, tendo = chon
            # Đọc lại mô tả mới của chính ô này cho chắc rồi mới nhận (mô tả cũ có thể là của món trước ở ô đó)
            moitruong.get_motavatphamhanhtrang(vitri, is_napmoi = True)
            if not self._phantichdolamkim(moitruong.get_motathovatphamhanhtrangcosan(vitri), tendo, taicauhinhphongyeu()):
                self._logpb(s, f"{tendo} (ô {vitri}) mô tả mới không còn đúng đồ Lam Kim, chọn lại")
                return None
            d = s["dolamkim"] = {"vitri": vitri, "id": iddoituong, "ten": tendo, "cap": cap}
            self._logpb(s, f"Chọn đồ đem đốt: {tendo} (cấp {cap}, giá bán {gia}, ô {vitri})")
        if d["vitri"] >= SOLUONGOMOITUI:
            # Đồ give cho NPC phải nằm ở hành trang 1 (24 ô đầu)
            s["trangthai"] = f"vào {ten}: chuyển {d['ten']} lên hành trang 1"
            if now - s.get("lucchuyentui", 0.) > 3.:
                s["solanchuyentui"] = s.get("solanchuyentui", 0) + 1
                if s["solanchuyentui"] > SOLANTHUNOICHUYEN:
                    baosuco(moitruong, "langlyson", f"⚠️ {ten}: không chuyển được {d['ten']} lên hành trang 1 (hết ô trống?), dừng tự động",
                            khoa = f"{s['batdau']}|chuyentuipy", giancach = 0.)
                    self._ketthuclanglyson("❌ Dừng: hành trang 1 không còn ô trống để give đồ")
                    return None
                s["lucchuyentui"] = now
                self._logpb(s, f"Chuyển {d['ten']} lên hành trang 1 để give")
                moitruong.action_thucthicaulenh(f"move {d['id']:x}# to 1")
            return None
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = tennpc)
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHNOICHUYENLLS:
            s["trangthai"] = f"vào {ten}: tới {tennpc} ({x}, {y})"
            xdich, ydich = moitruong.get_toado(diachinpc) if diachinpc else (x, y)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (xdich, ydich, moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
        idnpc = moitruong.get_iddoituong(diachinpc)
        if not idnpc:
            return None
        g = s.get("giao")
        if not g or g["buoc"] == "give":
            solan = g["solan"] if g else 0
            if solan >= SOLANTHUNOICHUYEN:
                s["giao"] = None
                s["lucthulaivao"] = now + THOIGIANTHULAIVAO
                self._baolanglyson(s, f"khongmenupy|{s['sovong']}", f"⚠️ {ten}: give {d['ten']} cho {tennpc} {SOLANTHUNOICHUYEN} lần không thấy "
                                                                   f"menu, {THOIGIANTHULAIVAO:.0f}s sau thử lại")
                return None
            s["trangthai"] = f"vào {ten} (vòng {s['sovong'] + 1}): give {d['ten']} cho {tennpc}"
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            lenh = taolenhgiao(f"{idnpc:x}#", [(d["id"], 1)], 0)[0]
            moitruong.action_thucthicaulenh(lenh)
            self._logpb(s, f"Give {d['ten']} cho {tennpc} ({lenh!r})")
            s["giao"] = {"buoc": "menu", "luc": now, "solan": solan + 1}
            return None
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung:
            if now - g["luc"] > THOIGIANCHOMENULLS:
                g["buoc"] = "give"
            return None
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        self._logpb(s, f"Menu {tennpc} sau khi give: {noidung[:100]!r} {lenhs}")
        thuong = unicodedata.normalize("NFC", noidung).lower()
        if any(all(k in thuong for k in cums) for cums in LOIMENUTHIEUDOTs) and lenhs:
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(lenhs[0])
            self._logpb(s, f"Đốt {d['ten']} (cấp {d['cap']}): chọn {lenhs[0]!r}, chờ menu vào")
            s.update(dagive = True, lucchonvaopy = now, lucdagive = now, giao = None, dolamkim = None, solanvaolaipy = 0, momophongyeu = False)
            return None
        # Lời lạ: không xác nhận gì, đóng menu, thử lại sau
        if moitruong.get_is_danghiencuasotuychon():
            moitruong.set_is_danghiencuasotuychon(False)
        s["giao"] = None
        s["lucthulaivao"] = now + THOIGIANTHULAIVAO
        self._baolanglyson(s, f"menulapy|{s['sovong']}", f"⚠️ {ten}: give xong {tennpc} trả lời lạ ({noidung[:60]!r}), không xác nhận, "
                                                         f"{THOIGIANTHULAIVAO:.0f}s sau thử lại")
        return None

    def _xulymenuphongyeu(self):
        # Gọi mỗi lượt ở mọi người tham gia (mình bật Phong Yêu Kính, hoặc người mình theo sau đang đi Phong Yêu Kính): menu "Đội nhóm các
        # ngươi đã mở Phong Yêu Kính..." -> chọn "1. Đúng vậy, ta muốn vào". Trưởng nhóm đang tự nói chuyện NPC thì để _noichuyenlls chọn
        s = self._langlyson
        if s:
            if s["phoban"] != "phongyeukinh" or s["hoithoai"] or s.get("giao"):
                return
        else:
            info = self._laythongtinmuctieutheosaucuasokhac() if self._is_tudongtheosau else None
            if not info or info.get("_phobanlanglyson") != "phongyeukinh":
                return
        moitruong = self.moitruong
        now = time.time()
        if s and s["giaidoan"] == "vao" and not moitruong.get_is_dangnamtrongnhom() and not self._is_trongphongyeu():
            # Thành viên chờ ngoài: đồng ý lời mời vào nhóm của người give (người online đứng đầu nhóm todoi), kể cả khi tắt Tổ đội tự động
            idgive = self._laynhompy()[0]
            if idgive != moitruong.get_idnguoichoi():
                moitruong.action_kiemtravadongyloimoinhom([idgive])
        if now - self._lucchonmenuphongyeu < GIANCACHCHONMENUPHONGYEU or not moitruong.get_is_danghiencuasotuychon():
            return
        noidung = unicodedata.normalize("NFC", moitruong.get_noidungcuasotuychon() or "")
        # Menu vào (mọi người) hoặc menu thành viên xác nhận đội trưởng mở Phong Yêu Kính (kiểu give thứ 2)
        thuong = noidung.lower()
        if LOIMENUVAOPHONGYEU not in thuong and LOIMENUTHANHVIENXACNHANPY not in thuong:
            return
        if s and s.get("dagive") and not s["davao"] and self._thanhvienchuavaonhompy(s) \
                and now - s.get("lucdagive", now) < THOIGIANCHOMOIPY:
            # Người give: để menu "ta muốn vào" đó, mời đủ thành viên vào nhóm rồi mới chọn (_buocvaophongyeu)
            return
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        if not lenhs:
            return
        self._lucchonmenuphongyeu = now
        moitruong.action_ngatdichuyen()
        moitruong.xoa_noidungcuasotuychon()
        moitruong.action_thucthicaulenh(lenhs[0])
        moitruong._inlog(f"[PHONG YÊU KÍNH] Menu {noidung[:60]!r}: chọn {lenhs[0]!r}")
        if s:
            s["lucchonvaopy"] = now
            if LOIMENUVAOPHONGYEU in thuong and not moitruong.get_is_truongnhom():
                # Thành viên vào vòng mới: bỏ boss đã giết / điểm dò của vòng trước (thành viên không qua bước đổi tổ đội nên không ai xoá)
                s.pop("py", None)
                s["diemvao"] = {}

    def get_bossdagietphongyeu(self):
        # ID boss Phong Yêu Kính mình đã giết vòng này (báo qua shared_data để người cùng nhóm cộng vào, boss chết xa họ vẫn được tính)
        # Chỉ báo khi đang ở trong phó bản: ngoài phó bản là boss vòng trước (từng làm trưởng nhóm vừa vào vòng mới đã cộng 2 boss cũ của
        # thành viên chưa vào, tưởng xong ngay rồi ra)
        s = self._langlyson
        py = s.get("py") if s and s["phoban"] == "phongyeukinh" else None
        return sorted(py["bossdagiet"]) if py and self._is_trongphongyeu() else []

    def _congbossnguoikhac(self, s, py):
        # Cộng boss người cùng nhóm đã giết (cùng máy hoặc máy khác nối LAN) vào boss mình đã giết, mỗi GIANCACHDOCBOSSPY giây
        now = time.time()
        if self.shared_data is None or now - py.get("lucdocboss", 0.) < GIANCACHDOCBOSSPY:
            return
        py["lucdocboss"] = now
        thanhviens = set(self.moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) - {self.moitruong.get_idnguoichoi()}
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict) or info.get("idnguoichoi") not in thanhviens:
                continue
            if now - info.get("thoidiemcapnhat", 0.) > 5.:
                continue
            moi = set(info.get("_bossdagietphongyeu") or ()) - py["bossdagiet"]
            if moi:
                py["bossdagiet"] |= moi
                if py["boss"] and py["boss"]["id"] in moi:
                    py["boss"] = None
                self._logpb(s, f"{info.get('tennhanvat') or info.get('idnguoichoi')} đã giết boss ({len(py['bossdagiet'])}/{SOBOSSPHONGYEU})")

    def _vitrithoyeu(self, s, py, idbando):
        # Thỏ Yêu đứng ở chỗ vào: thấy thì nhớ toạ độ thật, chưa thấy thì chỗ vào, không biết cả 2 thì chỗ đang đứng
        diachi = self.moitruong.action_timkiemnhanvat(tennhanvat = TENTHOYEU)
        if diachi:
            py["vitrithoyeu"] = self.moitruong.get_toado(diachi)
        return py.get("vitrithoyeu") or s["diemvao"].get(idbando) or self.moitruong.get_toado()

    def _timbossphongyeu(self, py):
        # Boss Phong Yêu Kính còn sống trong tầm nhìn (tên chứa TUBOSSPHONGYEUs, không phải người chơi / NPC / bảo thú, chưa tính là đã
        # giết). Tên boss có đuôi "(cấp N)" nên không loại theo dấu ngoặc (từng loại hết, không bao giờ thấy boss); bảo thú triệu hồi của
        # người chơi "Đậu Binh ( X ) (cấp 105)" có 2 cặp ngoặc thì loại
        moitruong = self.moitruong
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi) or moitruong.get_is_npc(diachi):
                continue
            ten = (moitruong.get_tendoituong(diachi) or "").strip()
            if not any(tu in ten for tu in TUBOSSPHONGYEUs) or TUKHONGPHAIBOSSPY in ten or ten.count("(") > 1:
                continue
            if moitruong.get_is_baothuvatpham(diachi) or moitruong.get_is_nhanvatdachet(diachi):
                continue
            if moitruong.get_iddoituong(diachi) in py["bossdagiet"]:
                continue
            return diachi
        return None

    @staticmethod
    def _taopy(s):
        return s.setdefault("py", {"do": None, "bossdagiet": set(), "boss": None, "soluotdo": 0, "hoisoquai": None, "lucvao": time.time()})

    def _buoctrongphongyeu(self, s, idbando, is_thanhvien = False):
        # Trong Phong Yêu Kính: thấy boss thì đánh boss, không thì dò khắp bản đồ đánh mọi quái; hết 1 lượt dò thì hỏi Thỏ Yêu số quái.
        # Giết đủ SOBOSSPHONGYEU boss (hoặc game báo hoàn thành) thì chờ nhặt đồ rồi sang ra (_buocraphongyeu).
        # is_thanhvien: thành viên cũng dò / đánh như vậy nhưng không hỏi Thỏ Yêu, không tự ra, xong thì chờ trưởng nhóm giải tán nhóm
        moitruong = self.moitruong
        now = time.time()
        tenpb = self._tenpb(s)
        py = self._taopy(s)
        if not py.get("vitrithoyeu"):
            # Vừa vào Thỏ Yêu đứng ngay cạnh: nhớ toạ độ (tuỳ bản đồ) để lúc hỏi số quái / ra quay về đúng chỗ
            self._vitrithoyeu(s, py, idbando)
        s["chedo"] = "danhquai"
        self._batdanhquailanglyson(s)
        self._congbossnguoikhac(s, py)
        if not is_thanhvien:
            # Người give: thành viên nào chưa vào nhóm thì vẫn mời tiếp (vào sau tự "look" Tả Khâu Minh vào phó bản)
            self._moithanhvienpy(s)
        # Trưởng nhóm dò đủ SOLUOTDORAPHONGYEU lượt bản đồ mà chưa đủ boss (không đang đánh boss nào) thì cũng ra: boss chỉ để có thêm đồ
        # Lam Kim rơi ra xoay vòng, đứng dò mãi phí thời gian (người dùng)
        is_hetluot = not is_thanhvien and py["soluotdo"] >= SOLUOTDORAPHONGYEU and not py["boss"]
        # Đủ boss mà mới vào chưa tới THOIGIANTOITHIEUPY giây thì không tin (boss chỉ ra khi đã đánh 85% quái): chắc là số boss cũ
        is_duboss = len(py["bossdagiet"]) >= SOBOSSPHONGYEU and now - py["lucvao"] >= THOIGIANTOITHIEUPY
        if is_duboss or s["daxongphoban"] or is_hetluot:
            if is_thanhvien:
                s["trangthai"] = f"{tenpb}: xong {len(py['bossdagiet'])} boss, chờ trưởng nhóm giải tán nhóm"
                return None
            luc = s.setdefault("lucxongboss", now)
            if now - luc < THOIGIANCHORA:
                s["trangthai"] = f"{tenpb}: xong {len(py['bossdagiet'])} boss, chờ nhặt đồ rồi về Chu Quốc"
                return None
            s.pop("lucxongboss", None)
            s.update(giaidoan = "nhanthuong", hoithoai = None)
            self._logpb(s, f"Xong phó bản ({len(py['bossdagiet'])}/{SOBOSSPHONGYEU} boss"
                           + (f", đã dò {py['soluotdo']} lượt bản đồ" if is_hetluot else "") + "), nói chuyện Thỏ Yêu về Chu Quốc")
            return None
        diachi = self._timbossphongyeu(py)
        boss = py["boss"]
        if diachi:
            idboss = moitruong.get_iddoituong(diachi)
            if not boss or boss["id"] != idboss:
                boss = py["boss"] = {"id": idboss, "ten": moitruong.get_tendoituong(diachi), "lucgan": 0.}
                self._logpb(s, f"Thấy boss {boss['ten']} ở {moitruong.get_toado(diachi)}")
            boss.update(vitri = moitruong.get_toado(diachi), lucgan = 0.)
            s["trangthai"] = f"{tenpb}: đánh boss {boss['ten']} (đã giết {len(py['bossdagiet'])}/{SOBOSSPHONGYEU})"
            self._capnhatbuocdichuyen(f"{tenpb}: đánh boss {boss['ten']}")
            if moitruong.get_khoangcach(diachi) > KHOANGCACHTOIBOSS:
                return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (*boss["vitri"], idbando), "khoangcachtoida": 1.}
            return None
        if boss:
            # Boss không còn thấy: chỉ coi là đã giết khi đứng gần chỗ thấy lần cuối THOIGIANBOSSBIENMAT giây (như _danhboss)
            xboss, yboss = boss["vitri"]
            if moitruong.get_khoangcachdiem(xboss, yboss) > KHOANGCACHTOIBOSS:
                boss["lucgan"] = 0.
                s["trangthai"] = f"{tenpb}: boss {boss['ten']} khuất tầm nhìn, quay lại ({xboss}, {yboss})"
                return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (xboss, yboss, idbando), "khoangcachtoida": 1.}
            boss["lucgan"] = boss["lucgan"] or now
            if now - boss["lucgan"] <= THOIGIANBOSSBIENMAT:
                s["trangthai"] = f"{tenpb}: không còn thấy boss {boss['ten']}, chờ xác nhận đã giết"
                return None
            py["bossdagiet"].add(boss["id"])
            py["boss"] = None
            self._logpb(s, f"Đã giết boss {boss['ten']} ({len(py['bossdagiet'])}/{SOBOSSPHONGYEU})")
            return None
        if py["hoisoquai"]:
            if is_thanhvien:
                py["hoisoquai"] = None
            else:
                return self._hoisoquaiphongyeu(s, py)
        return self._dophongyeu(s, py, idbando)

    def _hoisoquaiphongyeu(self, s, py):
        # Về Thỏ Yêu "2. Hiện tại chúng ta đánh được bao nhiêu quái?" -> "Hiện tại nhóm đã đánh được N quái vật. Muốn phát hiện Boss phải
        # đánh tới M quái vật." ghi log / trạng thái (chỉ để biết tiến độ). Quá THOIGIANHOISOQUAI giây không được thì thôi
        moitruong = self.moitruong
        x, y = self._vitrithoyeu(s, py, self.moitruong.get_idbandohientai())
        s["trangthai"] = f"{self._tenpb(s)}: dò xong {py['soluotdo']} lượt, hỏi Thỏ Yêu số quái đã đánh"
        ketqua, yeucau = self._noichuyenlls(s, TENTHOYEU, x, y, is_chovankhi = False, luachon = 1)
        if ketqua != "xong" and time.time() - py["hoisoquai"] <= THOIGIANHOISOQUAI:
            return yeucau
        noidung = unicodedata.normalize("NFC", moitruong.get_noidungcuasotuychon() or "") if ketqua == "xong" else ""
        khop = re.search(r"được\s*(\d+)\s*quái", noidung)
        py["soquai"] = int(khop.group(1)) if khop else None
        self._logpb(s, f"Thỏ Yêu: {noidung[:100]!r}" if noidung else "Không hỏi được số quái từ Thỏ Yêu")
        if moitruong.get_is_danghiencuasotuychon():
            moitruong.set_is_danghiencuasotuychon(False)
        py["hoisoquai"] = None
        s["hoithoai"] = None
        return None

    def _dophongyeu(self, s, py, idbando):
        # Đi lần lượt các điểm dò phủ vùng đi được (lưới vật cản, _taodiemdo) từ điểm gần mình nhất, hết 1 lượt thì hỏi số quái rồi đi tiếp
        moitruong = self.moitruong
        do = py["do"]
        if not do or do["idbando"] != idbando:
            diems = list(self._taodiemdo(idbando))
            if not diems:
                s["trangthai"] = f"{self._tenpb(s)}: chưa đọc được bản đồ"
                return None
            toado = moitruong.get_toado()
            i = min(range(len(diems)), key = lambda k: math.dist(diems[k], toado))
            do = py["do"] = {"idbando": idbando, "diems": diems, "i": i, "batdau": i, "luc": time.time()}
            self._logpb(s, f"{len(diems)} điểm dò")
        x, y = do["diems"][do["i"]]
        if moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIDIEMPY or time.time() - do["luc"] > THOIGIANMOIDIEMPY:
            do["i"] = (do["i"] + 1) % len(do["diems"])
            do["luc"] = time.time()
            if do["i"] == do["batdau"]:
                py["soluotdo"] += 1
                py["hoisoquai"] = time.time()
                self._logpb(s, f"Dò xong lượt {py['soluotdo']}, đã giết {len(py['bossdagiet'])}/{SOBOSSPHONGYEU} boss")
            x, y = do["diems"][do["i"]]
        nhan = f"dò đánh quái (điểm {do['i'] + 1}/{len(do['diems'])}, boss {len(py['bossdagiet'])}/{SOBOSSPHONGYEU})"
        s["trangthai"] = f"{self._tenpb(s)}: {nhan}"
        self._capnhatbuocdichuyen(f"{self._tenpb(s)}: {nhan}")
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}

    def _buocraphongyeu(self, s):
        # Xong Phong Yêu Kính: Thỏ Yêu "1. Ta muốn về Chu Quốc" (ra cạnh Tả Khâu Minh). Ra rồi thì xong vòng, không có thưởng phải lĩnh:
        # sang đổi tổ đội luôn (giải tán tổ đội thì thành viên còn trong phó bản cũng bị đưa ra Chu Quốc (285, 177))
        if self._is_trongphongyeu():
            x, y = self._vitrithoyeu(s, self._taopy(s), self.moitruong.get_idbandohientai())
            s["trangthai"] = f"xong {self._tenpb(s)}, nói chuyện Thỏ Yêu về Chu Quốc"
            return self._noichuyenlls(s, TENTHOYEU, x, y, is_chovankhi = False, luachon = 0)[1]
        s["sovong"] += 1
        s["sothanhvien"] = len(s["thanhviens"]) + 1
        self._logpb(s, f"Xong vòng {s['sovong']} ({int((time.time() - s['lucbatdauvong']) // 60)} phút), đổi tổ đội")
        s.update(giaidoan = "doinhom", hoithoai = None, tattodoi = False, is_daroinhom = False, lucnhanthuong = time.time(), khoathuong = "")
        return None
