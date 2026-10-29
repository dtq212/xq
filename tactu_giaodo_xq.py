# Phần giao tiền / đồ: hàng chờ yêu cầu giao (giaodo_xq). Yêu cầu mới chỉ nằm chờ (bot vẫn đánh tiếp), giao khi được kích hoạt
# ("kichhoat" của yêu cầu):
#   "banrac": về bán rác (bán, sửa đồ, cất kho xong) mà người nhận đang ở Tân Thủ Thôn trong tầm nhìn thì giao luôn trong chuyến đó
#             (bước 4 của _xulydangbanrac, di chuyển trực tiếp như cất kho); người nhận rời đi thì thôi, yêu cầu quay về chờ
#   "tay"   : bấm "Về giao ngay" / Telegram /vegiao: về Tân Thủ Thôn (phù / Hồi Thành Phù / chạy bộ như "Đi tới bản đồ"), tới Chủ Tiệm Tạp
#             Hóa chờ người nhận tối đa THOIGIANCHONGUOINHAN giây; trong lúc đó không chọn quái, lộ trình điểm đánh tạm dừng
# Giao: lại gần người nhận trong KHOANGCACHGIAODO ô rồi gửi lệnh give, kiểm tra ngân lượng / túi đồ đã giảm; xong bot tự quay lại việc cũ.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import time

from hangso_xq import *
from giaodo_xq import chiamon, taolenhgiao, motayeucau
from moitruong_xq import DOUUTIEN_KHANCAP
from thongbao_xq import baosuco

KHOANGCACHGIAODO = 3.
# Tới Tân Thủ Thôn mà chừng này giây chưa thấy người nhận thì bỏ yêu cầu (báo lỗi)
THOIGIANCHONGUOINHAN = 600.
# Gửi lệnh give xong chừng này giây thì xem ngân lượng / túi đồ đã giảm chưa, chưa thì gửi lại (tối đa SOLANGUIGIAODO lần)
THOIGIANKIEMTRAGIAODO = 3.
SOLANGUIGIAODO = 3
TRANGTHAICHOGIAO = "chưa giao (để dành: lần về bán rác gặp người nhận / bấm Về giao)"
KICHHOAT_TAY = "tay"
KICHHOAT_BANRAC = "banrac"


def _is_chuaxong(yeucau):
    return yeucau["trangthai"] not in ("xong", "lỗi")


class TacTuGiaoDo:
    def them_giaodo(self, yeucau):
        yeucau = dict(yeucau, trangthai = TRANGTHAICHOGIAO, solangui = 0, kichhoat = None)
        self._hangchogiaodo.append(yeucau)
        print(f"[GIAO ĐỒ] Thêm yêu cầu giao {yeucau['nguoinhan']}: {motayeucau(yeucau)} (để dành tới lần về bán rác gặp người nhận / bấm Về giao)")

    def huy_giaodo(self, idyeucau):
        self._hangchogiaodo = [y for y in self._hangchogiaodo if y["id"] != idyeucau]

    def kichhoat_giaodo(self):
        # Nút "Về giao ngay" / Telegram /vegiao: mọi yêu cầu đang chờ của nhân vật này về giao ngay
        dems = 0
        for yeucau in self._hangchogiaodo:
            if _is_chuaxong(yeucau) and yeucau.get("kichhoat") != KICHHOAT_TAY:
                yeucau["kichhoat"] = KICHHOAT_TAY
                yeucau.pop("luctoi", None)
                dems += 1
        print(f"[GIAO ĐỒ] Về giao ngay: {dems} yêu cầu")

    def get_is_danggiaodo(self):
        # Đang về giao do bấm tay (thay lộ trình điểm đánh); giao trong chuyến bán rác nằm trong quy trình về bán rác
        return any(_is_chuaxong(y) and y.get("kichhoat") == KICHHOAT_TAY for y in self._hangchogiaodo)

    def batdau_giaodo_sauban(self):
        # Bán rác (+ sửa đồ, cất kho) xong: yêu cầu đang chờ mà người nhận đang ở gần (thấy được) thì giao luôn trong chuyến này
        for yeucau in self._hangchogiaodo:
            if _is_chuaxong(yeucau) and not yeucau.get("kichhoat") and self.moitruong.action_timkiemnhanvat(tennhanvat = yeucau["nguoinhan"]):
                print(f"[GIAO ĐỒ] Về bán rác gặp {yeucau['nguoinhan']}: giao luôn")
                yeucau["kichhoat"] = KICHHOAT_BANRAC
                yeucau.pop("luctoi", None)

    def _xulygiaodobanrac(self):
        # Bước giao trong quy trình về bán rác (đang ở Tân Thủ Thôn, di chuyển trực tiếp như cất kho). -> True khi xong / không có việc
        if not any(_is_chuaxong(y) and y.get("kichhoat") == KICHHOAT_BANRAC for y in self._hangchogiaodo):
            return True
        yeucau = self._xulygiaodo(KICHHOAT_BANRAC)
        if yeucau and yeucau.get("toadodich"):
            x, y = yeucau["toadodich"][:2]
            self.moitruong.action_dichuyengiukhoangcachtoidadiem(x, y, khoangcachtoida = yeucau.get("khoangcachtoida", KHOANGCACHGIAODO - 1))
        return False

    def _bogiaodobanrac(self):
        # Quy trình bán rác dừng giữa chừng: yêu cầu đang giao trong chuyến bán rác quay về chờ
        for yeucau in self._hangchogiaodo:
            if _is_chuaxong(yeucau) and yeucau.get("kichhoat") == KICHHOAT_BANRAC and not yeucau.get("lucgui"):
                yeucau["kichhoat"], yeucau["trangthai"] = None, TRANGTHAICHOGIAO

    def get_hangchogiaodo(self):
        # Cho giao diện / Telegram: mọi yêu cầu, kể cả vừa xong / lỗi (giữ lại 10 yêu cầu đã kết thúc gần nhất)
        ketthucs = [y for y in self._hangchogiaodo if y["trangthai"] in ("xong", "lỗi")]
        if len(ketthucs) > 10:
            bo = {y["id"] for y in ketthucs[:-10]}
            self._hangchogiaodo = [y for y in self._hangchogiaodo if y["id"] not in bo]
        return [{k: y.get(k) for k in ("id", "nguoinhan", "tien", "giulaitien", "vatphams", "tienthucte", "vatphamthucte", "trangthai", "ghichu")}
                for y in self._hangchogiaodo]

    def _ketthucgiaodo(self, yeucau, is_thanhcong, ghichu):
        yeucau["trangthai"] = "xong" if is_thanhcong else "lỗi"
        yeucau["ghichu"] = ghichu
        # Xong thì báo số đã giao thật (tiền "giữ lại" / đồ "hết" đã quy ra số)
        mota = motayeucau(yeucau, is_thucte = is_thanhcong)
        print(f"[GIAO ĐỒ] {'Xong' if is_thanhcong else 'Lỗi'}: giao {yeucau['nguoinhan']} {mota} – {ghichu}")
        baosuco(self.moitruong, "giaodo", f"{'✅ Đã giao' if is_thanhcong else '❌ Không giao được'} cho {yeucau['nguoinhan']}: {mota}"
                                          f"{'' if is_thanhcong else ' – ' + ghichu}", khoa = yeucau["id"], giancach = 0.)

    def _xulygiaodo(self, kichhoat = KICHHOAT_TAY):
        # Yêu cầu giao đã kích hoạt kiểu kichhoat chưa xong: "tay" gọi thay lộ trình điểm đánh, "banrac" gọi trong bước giao của về bán
        # rác (_xulygiaodobanrac) -> yêu cầu di chuyển hoặc None
        yeucau = next((y for y in self._hangchogiaodo if _is_chuaxong(y) and y.get("kichhoat") == kichhoat), None)
        if yeucau is None:
            return None
        moitruong = self.moitruong
        if moitruong.get_is_nhanvatdachet() or moitruong.get_is_dangvankhi() or self.get_is_danghoithoainpc():
            return None
        if kichhoat == KICHHOAT_TAY and self._trangthaiveban != 0:
            return None
        now = time.time()

        if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            yeucau["trangthai"] = "đang về Tân Thủ Thôn"
            yeucau.pop("luctoi", None)
            buoc = self._lapbuocditoibando(BANDO_TANTHUTHON, is_hoithanhphu = True)
            if buoc["loai"] != "toinoi":
                return self._thuchienbuocditoibando(buoc, BANDO_TANTHUTHON, None, "[GIAO ĐỒ] Tân Thủ Thôn")
        yeucau.setdefault("luctoi", now)

        diachinguoinhan = moitruong.action_timkiemnhanvat(tennhanvat = yeucau["nguoinhan"])
        if not diachinguoinhan:
            if kichhoat == KICHHOAT_BANRAC and not yeucau.get("lucgui"):
                # Giao ké chuyến bán rác: người nhận đã đi khỏi thì không chờ, để lần sau
                print(f"[GIAO ĐỒ] Không thấy {yeucau['nguoinhan']}, bỏ qua (để dành tới lần về bán rác sau)")
                yeucau["kichhoat"], yeucau["trangthai"] = None, TRANGTHAICHOGIAO
                return None
            if now - yeucau["luctoi"] > THOIGIANCHONGUOINHAN:
                self._ketthucgiaodo(yeucau, False, f"chờ {int(THOIGIANCHONGUOINHAN // 60)} phút ở Tân Thủ Thôn không thấy {yeucau['nguoinhan']}")
                return None
            yeucau["trangthai"] = "chờ người nhận ở Tiệm Tạp Hóa"
            # Đứng cạnh Chủ Tiệm Tạp Hóa chờ (không thấy NPC thì đi tới chỗ tiệm)
            diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = CHUTIEMTAPHOA)
            x, y = moitruong.get_toado(diachinpc) if diachinpc else (X_CHUTIEMTAPHOA_TANTHUTHON, Y_CHUTIEMTAPHOA_TANTHUTHON)
            if moitruong.get_khoangcachdiem(x, y) > KHOANGCACHGIAODO:
                return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), BANDO_TANTHUTHON), "khoangcachtoida": KHOANGCACHGIAODO - 1}
            return None

        if moitruong.get_khoangcach(diachinguoinhan) > KHOANGCACHGIAODO:
            yeucau["trangthai"] = "đang lại gần người nhận"
            x, y = moitruong.get_toado(diachinguoinhan)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), BANDO_TANTHUTHON), "khoangcachtoida": KHOANGCACHGIAODO - 1}

        moitruong.action_ngatdichuyen()
        if yeucau.get("lucgui") and now - yeucau["lucgui"] < THOIGIANKIEMTRAGIAODO:
            return None
        if yeucau.get("lucgui"):
            # Đã gửi: ngân lượng / số món đã giảm đúng thì xong. Giảm một phần thì dừng, không gửi lại (gửi lại có thể giao 2 lần);
            # chưa giảm gì thì gửi lại
            tinhtrang = self._kiemtragiaodo(yeucau)
            if tinhtrang == "xong":
                self._ketthucgiaodo(yeucau, True, "đã giao")
                return None
            if tinhtrang == "motphan":
                self._ketthucgiaodo(yeucau, False, "mới giao được một phần, kiểm tra lại túi đồ / ngân lượng (không gửi lại kẻo giao trùng)")
                return None
            if tinhtrang is None:
                return None
            if yeucau["solangui"] >= SOLANGUIGIAODO:
                self._ketthucgiaodo(yeucau, False, f"gửi lệnh {SOLANGUIGIAODO} lần mà ngân lượng / đồ không giảm (đồ khoá, người nhận đầy túi...?)")
                return None
        self._guilenhgiao(yeucau, diachinguoinhan)
        return None

    def _guilenhgiao(self, yeucau, diachinguoinhan):
        # Lần gửi đầu: tính số giao thực tế (tiền "giữ lại" / đồ "hết" tính theo lúc này, sau khi đã trừ tiền phù dọc đường) và mốc trước
        # khi giao để kiểm tra; gửi lại (chưa giảm gì) thì dùng đúng số đã tính
        moitruong = self.moitruong
        nganluong = moitruong.get_nganluong()
        if nganluong is None:
            return
        cacchong = {}
        for ten, vitris in moitruong.get_danhsachvatphamhanhtrang_map().items():
            for vitri, iddoituong in vitris:
                if iddoituong:
                    cacchong.setdefault(ten, []).append((iddoituong, moitruong.get_soluongvatphamhanhtrang(vitri) or 1))
        so = lambda n: f"{n:,}".replace(",", ".")
        if not yeucau.get("truocgiao"):
            tien = yeucau["tien"] if yeucau.get("giulaitien") is None else max(0, nganluong - yeucau["giulaitien"])
            if tien > nganluong:
                self._ketthucgiaodo(yeucau, False, f"không đủ ngân lượng (cần {so(tien)}, có {so(nganluong)})")
                return
            _, thucte, loi = chiamon(yeucau["vatphams"], cacchong)
            if loi:
                self._ketthucgiaodo(yeucau, False, loi)
                return
            if not tien and not thucte:
                self._ketthucgiaodo(yeucau, False, f"không có gì để giao (ngân lượng {so(nganluong)}"
                                                   f"{', giữ ' + so(yeucau['giulaitien']) if yeucau.get('giulaitien') else ''})")
                return
            yeucau["tienthucte"], yeucau["vatphamthucte"] = tien, thucte
            yeucau["truocgiao"] = {"tien": nganluong, "mon": {ten: sum(max(1, sl) for _, sl in cacchong.get(ten, [])) for ten, _ in thucte}}
        cacmon, _, loi = chiamon(yeucau["vatphamthucte"], cacchong)
        if loi:
            self._ketthucgiaodo(yeucau, False, loi)
            return
        if moitruong.get_is_nguoichoi(diachinguoinhan):
            manguoinhan = str(moitruong.get_idnguoichoi(diachinguoinhan))
        else:
            manguoinhan = f"{moitruong.get_iddoituong(diachinguoinhan):x}#"
        for lenh in taolenhgiao(manguoinhan, cacmon, yeucau["tienthucte"]):
            print(f"[GIAO ĐỒ] {lenh}")
            moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_KHANCAP)
        yeucau["trangthai"] = "đã gửi lệnh, đang kiểm tra"
        yeucau["lucgui"] = time.time()
        yeucau["solangui"] += 1

    def _kiemtragiaodo(self, yeucau):
        # So với lúc gửi lần đầu: "xong" (ngân lượng và mọi món đã giảm đủ số thực tế), "motphan" (có giảm nhưng chưa đủ), "chuagiam",
        # None (chưa đọc được)
        truoc = yeucau.get("truocgiao") or {}
        nganluong = self.moitruong.get_nganluong()
        soluong = self.moitruong.get_soluongvatphamhanhtrangtheoten()
        if nganluong is None or soluong is None:
            return None
        thucte = yeucau["vatphamthucte"]
        dus = [nganluong <= truoc["tien"] - yeucau["tienthucte"]] + [soluong.get(ten, 0) <= truoc["mon"].get(ten, 0) - sl for ten, sl in thucte]
        cogiams = [nganluong < truoc["tien"]] + [soluong.get(ten, 0) < truoc["mon"].get(ten, 0) for ten, _ in thucte]
        if all(dus):
            return "xong"
        return "motphan" if any(cogiams) else "chuagiam"
