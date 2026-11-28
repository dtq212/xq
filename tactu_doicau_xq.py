# Đổi Lam Cầu + Hắc Cầu ở Thiên Sứ Trao Đổi (nút tab Khác, nhân vật đang chọn).
# Log Lầy (ID 1451) 27/11 19:54-19:55 (NPC 28b# ở Tân Thủ Thôn, đứng cạnh ~(154, 127)) gửi tay cả chuỗi:
#   look <NPC># -> tallk <NPC># bonus.1 -> tallk <NPC># bonus.28 -> tallk <NPC># bonus.29, mỗi lệnh cách ~1 giây, lặp lại.
# Lam Cầu / Hắc Cầu do acc khác give sang (thống kê ghi "Chuyển nhận") rồi đổi dần. Bấm 1 lần là lặp tới khi túi hết cả
# Lam Cầu lẫn Hắc Cầu; vài vòng liền số cầu không giảm (thiếu 1 loại / NPC không đổi nữa) thì dừng, khỏi gửi lệnh mãi.
# Chạy trong bộ điều phối di chuyển như Give & phân giải: bot đứng yên / lại gần NPC, không đi lộ trình điểm đánh.
import time

from hangso_xq import *
from moitruong_xq import DOUUTIEN_KHANCAP

TENNPCDOICAU = "Thiên Sứ Trao Đổi"
# Chỉ cần lệnh cuối "tallk <NPC># bonus.29" (đổi luôn, không phải mở menu look / bonus.1 / bonus.28 trước; bản cũ trong
# loop_xq cũng chỉ gửi bonus.29). Muốn đi đủ menu như gửi tay thì thêm lại các bước "look", "bonus.1", "bonus.28" phía trước
BUOCDOICAU = ("bonus.29", )
# Log Lầy: các lệnh cách nhau 0.5-1.5 giây (gửi tay); 1 giây để số cầu trong túi kịp cập nhật trước lần gửi kế
GIANCACHDOICAU = 1.
KHOANGCACHDOICAU = 3.
# Số vòng (mỗi vòng 1 lệnh) liền tổng Lam + Hắc Cầu không giảm thì thôi; 5 cho đỡ dừng nhầm lúc mạng chậm
SOVONGKHONGGIAMTOIDA = 5
THOIGIANTIMNPCDOICAU = 20.
# Chỗ Thiên Sứ Trao Đổi đứng ở Tân Thủ Thôn (log 1451 ~(154, 127), log 418 tới (153, 128) thì look được)
TOADONPCDOICAU = (154, 127)
# Đổi Tàng Bảo Đồ (log 418 28/11): chỉ cần lệnh cuối "tallk <NPC># bonus.23" (người dùng xác nhận 28/11, không phải mở menu
# look / bonus.1 / bonus.22 trước); 1 cặp cầu ra 2 tấm, luôn chừa ít nhất 2 ô trống
BUOCDOITANGBAODO = ("bonus.23", )
SOTANGBAODOMOICAP = 2
SOOTRONGGIUDOITANGBAODO = 2


class TacTuDoiCau:
    def batdau_doicau(self):
        if self._doicau:
            return
        self._doicau = {"batdau": time.time(), "lucgui": 0., "buoc": 0, "vong": 0, "truoc": None, "khonggiam": 0,
                        "dau": None, "trangthai": "bắt đầu"}
        self.moitruong._inlog("[ĐỔI CẦU] Bắt đầu đổi Lam Cầu + Hắc Cầu ở Thiên Sứ Trao Đổi")

    def huy_doicau(self, lydo = ""):
        d = self._doicau
        if d:
            dem = self._demcau()
            dadoi = ""
            if d["dau"] and dem:
                dadoi = f"đã dùng {d['dau'][0] - dem[0]} Lam Cầu, {d['dau'][1] - dem[1]} Hắc Cầu, {d['vong']} vòng"
            self.moitruong._inlog(f"[ĐỔI CẦU] Kết thúc{' (' + dadoi + ')' if dadoi else ''}{': ' + lydo if lydo else ''}")
            self._ketquadoicau = f"Lần trước: {lydo or 'xong'}{' – ' + dadoi if dadoi else ''} ({time.strftime('%H:%M')})"
        self._doicau = None

    def get_is_dangdoicau(self):
        return bool(self._doicau)

    def get_trangthaidoicau(self):
        d = self._doicau
        if not d:
            return self._ketquadoicau or ""
        dem = self._demcau()
        con = f" – còn {dem[0]} Lam, {dem[1]} Hắc" if dem else ""
        return f"Đổi cầu: {d['trangthai']} (vòng {d['vong']}){con}"

    def _demcau(self):
        # (số Lam Cầu, số Hắc Cầu) trong hành trang, None khi chưa đọc được
        soluongs = self.moitruong.get_soluongvatphamhanhtrangtheoten()
        if soluongs is None:
            return None
        return soluongs.get(LAMCAU, 0), soluongs.get(HACCAU, 0)

    def _xulydoicau(self):
        # Trả về yêu cầu di chuyển tự do (lại gần NPC) hoặc None (đứng yên)
        d = self._doicau
        moitruong = self.moitruong
        now = time.time()
        if now - d["lucgui"] < GIANCACHDOICAU:
            return None
        dem = self._demcau()
        if dem is None:
            return None
        if d["dau"] is None:
            d["dau"] = dem
        # Đầu mỗi vòng (trước "look"): xét còn cầu không, vòng trước có đổi được không
        if d["buoc"] == 0:
            if sum(dem) <= 0:
                self.huy_doicau("hết Lam Cầu và Hắc Cầu")
                return None
            if d["truoc"] is not None:
                d["khonggiam"] = d["khonggiam"] + 1 if sum(dem) >= sum(d["truoc"]) else 0
                if d["khonggiam"] >= SOVONGKHONGGIAMTOIDA:
                    self.huy_doicau(f"{SOVONGKHONGGIAMTOIDA} vòng liền số cầu không giảm (còn {dem[0]} Lam, {dem[1]} Hắc – thiếu 1 loại?)")
                    return None
            d["truoc"] = dem
        diachi = moitruong.action_timkiemnhanvat(TENNPCDOICAU)
        if not diachi:
            if now - d["batdau"] > THOIGIANTIMNPCDOICAU:
                self.huy_doicau(f"không thấy {TENNPCDOICAU} quanh mình")
            else:
                d["trangthai"] = f"tìm {TENNPCDOICAU}"
            return None
        if moitruong.get_khoangcach(diachi) > KHOANGCACHDOICAU:
            d["trangthai"] = "lại gần NPC"
            x, y = moitruong.get_toado(diachi)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()),
                    "khoangcachtoida": KHOANGCACHDOICAU - 1}
        moitruong.action_ngatdichuyen()
        idnpc = moitruong.get_iddoituong(diachi)
        if not idnpc:
            return None
        buoc = BUOCDOICAU[d["buoc"]]
        # "tallk" Niết Bàn tự đổi thành "talk" trong action_thucthicaulenh
        caulenh = f"look {idnpc:x}#" if buoc == "look" else f"tallk {idnpc:x}# {buoc}"
        moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_KHANCAP)
        d["lucgui"] = now
        d["trangthai"] = f"gửi {buoc}"
        d["buoc"] = (d["buoc"] + 1) % len(BUOCDOICAU)
        if d["buoc"] == 0:
            d["vong"] += 1
        return None

    # ---------------- Đổi Lam Cầu + Hắc Cầu lấy Tàng Bảo Đồ (bước trước khi đào, ô "Đào tàng bảo đồ") ----------------
    # Log Thien Dao (ID 418) 28/11 03:39 gửi tay ở Thiên Sứ Trao Đổi (28b#, đứng ~(153, 128) Tân Thủ Thôn):
    #   look 28b# -> tallk 28b# bonus.1 -> tallk 28b# bonus.22 -> tallk 28b# bonus.23 (cách ~1 giây)
    # 1 giây sau bonus.23 có 2 món mới (id 1f67f5, 1f67f6) = 1 cặp Lam + Hắc Cầu đổi được 2 Tàng Bảo Đồ (2 món đó bị luật
    # "Vứt tàng bảo đồ" vứt ngay; nay đang bật đào thì không vứt Tàng Bảo Đồ). Chỉ gửi lệnh cuối bonus.23 (BUOCDOITANGBAODO)
    def _xulydoitangbaodo(self):
        # Gọi từ action_tudongdaotangbaodo mỗi lượt khi self._doitangbaodo khác None. Đổi xong / dừng thì đặt None, lượt sau đi đào
        d = self._doitangbaodo
        moitruong = self.moitruong
        now = time.time()
        if now - d["lucgui"] < GIANCACHDOICAU:
            return
        if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            self._ketthucdoitangbaodo("rời Tân Thủ Thôn")
            return
        soluongs = moitruong.get_soluongvatphamhanhtrangtheoten()
        if soluongs is None:
            return
        dem = (soluongs.get(LAMCAU, 0), soluongs.get(HACCAU, 0), soluongs.get(TANGBAODO, 0))
        if d["dau"] is None:
            d["dau"] = dem
        # Đầu mỗi vòng: còn đủ cặp cầu, còn chỗ (sau khi đổi vẫn trống ít nhất SOOTRONGGIUDOITANGBAODO ô), vòng trước có đổi được không
        if d["buoc"] == 0:
            if min(dem[0], dem[1]) <= 0:
                self._ketthucdoitangbaodo(f"hết cặp cầu (còn {dem[0]} Lam, {dem[1]} Hắc)")
                return
            sootrong = moitruong.get_sootronghanhtrang()
            if sootrong < SOOTRONGGIUDOITANGBAODO + SOTANGBAODOMOICAP:
                self._ketthucdoitangbaodo(f"hành trang còn {sootrong} ô trống, giữ lại {SOOTRONGGIUDOITANGBAODO} ô")
                return
            # Chỉ xét sau 1 vòng đã gửi lệnh (log 1451 04:03: đếm cả lúc đang đi tới NPC => dừng oan "0 vòng" 3 lần liền)
            if d["truoc"] is not None and d["dagui"]:
                d["khonggiam"] = d["khonggiam"] + 1 if dem[0] + dem[1] >= d["truoc"][0] + d["truoc"][1] else 0
                if d["khonggiam"] >= SOVONGKHONGGIAMTOIDA:
                    self._ketthucdoitangbaodo(f"{SOVONGKHONGGIAMTOIDA} vòng liền số cầu không giảm (NPC không đổi?)")
                    return
            if d["truoc"] is None or d["dagui"]:
                d["truoc"] = dem
                d["dagui"] = False
        diachi = moitruong.action_timkiemnhanvat(TENNPCDOICAU)
        if not diachi:
            if now - d["batdau"] > THOIGIANTIMNPCDOICAU * 3:
                self._ketthucdoitangbaodo(f"không thấy {TENNPCDOICAU}")
            elif now - d["lucdi"] > 2.:
                # Chưa thấy NPC: đi về chỗ NPC đứng (log 418 / 1451)
                moitruong.action_tudongtimduong(*TOADONPCDOICAU, BANDO_TANTHUTHON)
                d["lucdi"] = now
            return
        if moitruong.get_khoangcach(diachi) > KHOANGCACHDOICAU:
            if now - d["lucdi"] > 2.:
                x, y = moitruong.get_toado(diachi)
                moitruong.action_tudongtimduong(round(x), round(y), BANDO_TANTHUTHON)
                d["lucdi"] = now
            return
        moitruong.action_tudongtimduong(0, 0, 0)
        moitruong.action_ngatdichuyen()
        idnpc = moitruong.get_iddoituong(diachi)
        if not idnpc:
            return
        buoc = BUOCDOITANGBAODO[d["buoc"]]
        # "tallk" Niết Bàn tự đổi thành "talk" trong action_thucthicaulenh
        caulenh = f"look {idnpc:x}#" if buoc == "look" else f"tallk {idnpc:x}# {buoc}"
        moitruong.action_thucthicaulenh(caulenh, douutien = DOUUTIEN_KHANCAP)
        d["lucgui"] = now
        d["buoc"] = (d["buoc"] + 1) % len(BUOCDOITANGBAODO)
        if d["buoc"] == 0:
            d["vong"] += 1
            d["dagui"] = True

    def batdau_doitangbaodo(self):
        if self._doitangbaodo:
            return
        self._doitangbaodo = {"batdau": time.time(), "lucgui": 0., "lucdi": 0., "buoc": 0, "vong": 0, "truoc": None,
                              "khonggiam": 0, "dau": None, "dagui": False}
        self.moitruong._inlog("[ĐỔI TÀNG BẢO ĐỒ] Hết Tàng Bảo Đồ, đổi Lam Cầu + Hắc Cầu ở Thiên Sứ Trao Đổi")

    def _ketthucdoitangbaodo(self, lydo):
        d = self._doitangbaodo
        thongke = ""
        if d and d["dau"]:
            soluongs = self.moitruong.get_soluongvatphamhanhtrangtheoten()
            if soluongs is not None:
                thongke = (f" – {d['vong']} vòng, dùng {d['dau'][0] - soluongs.get(LAMCAU, 0)} Lam, {d['dau'][1] - soluongs.get(HACCAU, 0)} Hắc,"
                           f" có {soluongs.get(TANGBAODO, 0)} Tàng Bảo Đồ")
        self.moitruong._inlog(f"[ĐỔI TÀNG BẢO ĐỒ] Kết thúc: {lydo}{thongke}")
        self._doitangbaodo = None
        # Đổi xong thì nhịp sau mới xét đào (chờ túi cập nhật món mới)
        self._thoidiemchodaotangbaodo = time.time() + 2.
