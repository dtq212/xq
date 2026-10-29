# Cất kho: món trong túi khớp bảng Cất kho (luattuido_xq "catkho") đem gửi Quản Khố ở Tân Thủ Thôn (X_QUANKHO_TANTHUTHON, ...).
# Chạy sau mỗi lần về bán rác (bước sau sửa đồ của _xulydangbanrac, nếu bật "is_catkhosauban") và khi bấm tay / Telegram (/catkho):
# về Tân Thủ Thôn như giao đồ, trong lúc đó không chọn quái, lộ trình điểm đánh tạm dừng.
# Lệnh game (7e# = id đối tượng Quản Khố hệ 16, tìm theo tên):
#   mở rương  : pawn 7e# <rương>                         (rương từ 1)
#   cất vào   : pawn + 7e# <id món>#<số lượng> <ô rương>   (ô từ 1; ô đang có cùng món thì gộp chồng; số lượng nhỏ hơn chồng = cất 1 phần)
# Đọc rương đang mở bằng moitruong.get_khodangmo (chỉ rương vừa mở có dữ liệu). Mỗi món: cất vào rương luật chỉ định (đầy thì bỏ món
# đó, báo), luật để tự động thì rương đang mở còn chỗ / rương kế, hết rương thì báo kho đầy; trong rương ưu tiên gộp chồng cùng tên,
# không thì ô trống đầu tiên. "Giữ lại" của luật: chừa chừng đó cái (theo tên) trong túi, cất phần còn lại. Gửi xong chờ rồi xem món đã
# rời túi / chồng đã giảm chưa: chưa thì ô đó không gộp được (đầy chồng...) / thử lại, quá SOLANTHUCATKHO lần thì bỏ món đó (đồ khoá...)
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import time
import uuid

from hangso_xq import *
from luattuido_xq import tailuat
from moitruong_xq import DOUUTIEN_KHANCAP
from thongbao_xq import baosuco

LYDOCATKHO_BANRAC = "banrac"
LYDOCATKHO_LENHTAY = "lenhtay"
KHOANGCACHQUANKHO = 3.
# Các ô hành trang đầu bán rác cũng bỏ qua (ô dùng nhanh)
VITRICATKHODAUTIEN = 6
GIANCACHBUOCCATKHO = 0.5
# Gửi lệnh mở rương xong chờ chừng này giây cho game nạp dữ liệu rương; mở chừng ấy lần không thấy đổi rương thì bỏ
THOIGIANCHOMORUONG = 1.5
SOLANMORUONG = 3
# Gửi lệnh cất xong chừng này giây thì xem món đã rời túi chưa
THOIGIANKIEMTRACATKHO = 1.5
SOLANTHUCATKHO = 3
# Quá lâu (kẹt đường, không thấy Quản Khố...) thì bỏ, báo lỗi
THOIGIANCATKHOTOIDA = 300.
THOIGIANCATKHOLENHTAYTOIDA = 600.
# Lịch sử cất kho giữ chừng này giây (báo cáo định kỳ Telegram chỉ cần từ kỳ trước, tối đa vài giờ)
THOIGIANGIULICHSUCATKHO = 24 * 3600.


def is_trungtenkho(tenkho, ten):
    # Tên trong kho đọc tối đa 0x20 byte (tên dài bị cắt, ký tự cuối có thể mất nửa) => tên dài thì so phần đầu
    if not tenkho or not ten:
        return False
    return tenkho == ten or (len(tenkho.encode("utf-8")) >= 0x1D and ten.startswith(tenkho))


class TacTuCatKho:
    def yeucau_catkho(self):
        # Bấm tay / Telegram: về Tân Thủ Thôn cất ngay (đang cất rồi thì thôi)
        if self._catkho:
            print("[CẤT KHO] Đang cất kho rồi")
            return
        self._catkho = self._taoviec(LYDOCATKHO_LENHTAY)
        print("[CẤT KHO] Bắt đầu cất kho (lệnh tay)")

    def huy_catkho(self):
        if self._catkho:
            print("[CẤT KHO] Huỷ cất kho")
        self._catkho = None

    def get_is_dangcatkho(self):
        # Việc cất kho bấm tay (thay lộ trình điểm đánh như giao đồ); cất sau bán rác nằm trong quy trình về bán rác
        return bool(self._catkho) and self._catkho["lydo"] == LYDOCATKHO_LENHTAY

    def get_trangthaicatkho(self):
        # Cho giao diện / Telegram: việc đang làm, hoặc kết quả lần gần nhất
        if self._catkho:
            return f"đang cất kho: {self._catkho['trangthai']}"
        return self._ketquacatkho or ""

    @staticmethod
    def _taoviec(lydo):
        return {"id": uuid.uuid4().hex[:8], "lydo": lydo, "batdau": time.time(), "trangthai": "bắt đầu", "lucbuoc": 0., "ruong": 1,
                "soruong": 1, "ruongdamo": 0, "lucmo": 0., "solanmo": 0, "ruongday": set(), "khongmo": set(), "khonggop": set(), "odadung": set(),
                "solanloi": {}, "boqua": {}, "dangcho": None, "dacat": {}, "is_damokho": False}

    def _laymoncatkho(self):
        # Chồng trong túi cần cất theo bảng Cất kho, theo thứ tự ô: [{"vitri", "id", "ten", "soluong" (của chồng, 0 = không chồng được),
        # "cat" (số cất từ chồng này), "ruong" (0 = tự động)}]. Tính theo tên: tổng trong túi trừ "giữ lại" của luật, lấy dần từ ô đầu
        # (chồng cuối có thể chỉ cất 1 phần). Luật cần mô tả mà chưa đọc được thì bỏ qua lượt này
        moitruong = self.moitruong
        soluongo = moitruong.get_soluongvatphamhanhtrangtoida() + 1
        tens = moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        ids = moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        nhoms = {}
        for vitri in range(VITRICATKHODAUTIEN, min(len(tens), len(ids))):
            if not ids[vitri] or ids[vitri] <= 0 or not tens[vitri]:
                continue
            luat = self._layluatcatkho(tens[vitri], vitri)
            if luat:
                nhoms.setdefault(tens[vitri], (luat, []))[1].append((vitri, ids[vitri], moitruong.get_soluongvatphamhanhtrang(vitri) or 0))
        mons = []
        for ten, (luat, chongs) in nhoms.items():
            can = sum(max(1, sl) for _, _, sl in chongs) - luat["giulai"]
            for vitri, iddoituong, soluong in chongs:
                if can <= 0:
                    break
                cat = min(can, max(1, soluong))
                mons.append({"vitri": vitri, "id": iddoituong, "ten": ten, "soluong": soluong, "cat": cat, "ruong": luat["ruong"]})
                can -= cat
        return sorted(mons, key = lambda m: m["vitri"])

    def _chonokho(self, viec, kho, mon):
        # (ô rương từ 0, is_gop) cho món, (None, False) khi rương này không còn chỗ. Gộp chỉ với món xếp chồng được (số lượng > 0)
        ruong = kho["ruong"]
        if mon["soluong"] > 0:
            for o, (ten, soluong, _) in enumerate(kho["os"]):
                if soluong > 0 and (ruong, o) not in viec["khonggop"] and is_trungtenkho(ten, mon["ten"]):
                    return o, True
        for o, (ten, _, _) in enumerate(kho["os"]):
            if not ten and (ruong, o) not in viec["odadung"]:
                return o, False
        return None, False

    def _ketthuccatkho(self, viec, loi = None):
        # Báo kết quả (Telegram + log), xoá việc, đóng cửa sổ kho bot đã mở. -> "xong" / "lỗi"
        self._catkho = None
        if viec["is_damokho"]:
            self.moitruong.action_dongcuasokho()
        if viec["dacat"]:
            now = time.time()
            self._lichsucatkho = [l for l in self._lichsucatkho if now - l[0] < THOIGIANGIULICHSUCATKHO] + [[now, dict(viec["dacat"])]]
        dacat = ", ".join(f"{ten} ×{sl}" for ten, sl in viec["dacat"].items())
        bo = [f"{ten} ({lydo})" for ten, lydo in viec["boqua"].items()]
        phans = [f"✅ Đã cất kho: {dacat}"] if dacat else []
        if bo:
            phans.append(f"⚠️ Không cất được: {', '.join(bo)}")
        if loi:
            phans.append(f"❌ {loi}")
        if not phans:
            phans.append("Không có món nào cần cất (bảng Cất kho)")
        noidung = "\n".join(phans)
        print(f"[CẤT KHO] {noidung.replace(chr(10), ' | ')}")
        self._ketquacatkho = f"{time.strftime('%H:%M')} {noidung.splitlines()[0]}"
        if viec["dacat"] or bo or loi or viec["lydo"] == LYDOCATKHO_LENHTAY:
            baosuco(self.moitruong, "catkho", noidung, khoa = viec["id"], giancach = 0.)
        return "lỗi" if loi else "xong"

    def _buoccatkho(self, viec):
        # 1 bước cất kho khi đã ở Tân Thủ Thôn. -> ("dichuyen", x, y) cần tới gần Quản Khố, "dang" đang làm, "xong" / "lỗi" đã kết thúc
        moitruong = self.moitruong
        now = time.time()
        if now - viec["lucbuoc"] < GIANCACHBUOCCATKHO:
            return "dang"
        viec["lucbuoc"] = now
        thoigiantoida = THOIGIANCATKHOLENHTAYTOIDA if viec["lydo"] == LYDOCATKHO_LENHTAY else THOIGIANCATKHOTOIDA
        if now - viec["batdau"] > thoigiantoida:
            return self._ketthuccatkho(viec, f"quá {int(thoigiantoida // 60)} phút chưa cất xong ({viec['trangthai']})")

        # Lệnh cất vừa gửi: món đã rời túi (tìm theo id, ô có thể đổi do xếp chồng) / chồng đã giảm đủ (cất 1 phần) là xong; không thì ô
        # gộp đó không gộp được / thử lại
        dangcho = viec["dangcho"]
        if dangcho:
            if now - dangcho["lucgui"] < THOIGIANKIEMTRACATKHO:
                return "dang"
            viec["dangcho"] = None
            ids = moitruong._docdanhsachidvatphamhanhtrang(moitruong.get_soluongvatphamhanhtrangtoida() + 1)
            is_xong = dangcho["id"] not in ids
            if not is_xong and dangcho["soluong"] > dangcho["cat"]:
                is_xong = (moitruong.get_soluongvatphamhanhtrang(ids.index(dangcho["id"])) or 0) <= dangcho["soluong"] - dangcho["cat"]
            if is_xong:
                viec["dacat"][dangcho["ten"]] = viec["dacat"].get(dangcho["ten"], 0) + dangcho["cat"]
                viec["odadung"].add((dangcho["ruong"], dangcho["o"]))
            else:
                viec["solanloi"][dangcho["ten"]] = viec["solanloi"].get(dangcho["ten"], 0) + 1
                (viec["khonggop"] if dangcho["is_gop"] else viec["odadung"]).add((dangcho["ruong"], dangcho["o"]))
                print(f"[CẤT KHO] {dangcho['ten']} chưa rời túi sau lệnh cất (lần {viec['solanloi'][dangcho['ten']]})")
                if viec["solanloi"][dangcho["ten"]] >= SOLANTHUCATKHO:
                    viec["boqua"][dangcho["ten"]] = f"thử {SOLANTHUCATKHO} lần không được, đồ khoá?"
            return "dang"

        mons = [m for m in self._laymoncatkho() if m["ten"] not in viec["boqua"]]
        if not mons:
            return self._ketthuccatkho(viec)

        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = QUANKHO)
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHQUANKHO:
            viec["trangthai"] = "đang tới Quản Khố"
            x, y = moitruong.get_toado(diachinpc) if diachinpc else (X_QUANKHO_TANTHUTHON, Y_QUANKHO_TANTHUTHON)
            return "dichuyen", round(x), round(y)
        moitruong.action_ngatdichuyen()
        manpc = f"{moitruong.get_iddoituong(diachinpc):x}#"

        kho = moitruong.get_khodangmo()
        if kho and 0 < kho["soruong"] <= 20:
            # Rương đã thử mở không được thì không tính nó và các rương sau, dù game báo số rương nhiều hơn
            viec["soruong"] = min([kho["soruong"]] + [r - 1 for r in viec["khongmo"] if r > 1])
        # Rương cho món đầu tiên: luật chỉ định thì đúng rương đó (không có / đã đầy thì bỏ món, báo); tự động thì rương đang dùng nếu
        # chưa đầy, không thì rương kế chưa đầy, hết thì kho đầy
        mon = mons[0]
        if mon["ruong"]:
            # Chưa đọc được kho lần nào (chưa biết số rương) thì cứ thử mở rương chỉ định
            if kho and mon["ruong"] > viec["soruong"]:
                viec["boqua"][mon["ten"]] = f"chỉ có {viec['soruong']} rương, không có rương {mon['ruong']}"
                return "dang"
            if mon["ruong"] in viec["ruongday"]:
                viec["boqua"][mon["ten"]] = f"không mở được rương {mon['ruong']}" if mon["ruong"] in viec["khongmo"] else f"rương {mon['ruong']} đầy"
                return "dang"
            ruongdich = mon["ruong"]
        else:
            conlai = [r for r in range(1, viec["soruong"] + 1) if r not in viec["ruongday"]]
            if not conlai:
                return self._ketthuccatkho(viec, f"kho đầy ({viec['soruong']} rương), còn {len(mons)} món chưa cất")
            ruongdich = viec["ruong"] if viec["ruong"] in conlai else conlai[0]
        if ruongdich != viec["ruong"]:
            viec["ruong"], viec["lucmo"], viec["solanmo"] = ruongdich, 0., 0

        # Mở rương cần dùng (mở lại cả khi game đang giữ đúng rương đó, cho dữ liệu mới), chờ game nạp xong
        if viec["ruongdamo"] != viec["ruong"] or not kho or kho["ruong"] != viec["ruong"]:
            if viec["lucmo"] and now - viec["lucmo"] < THOIGIANCHOMORUONG:
                return "dang"
            if viec["lucmo"] and kho and kho["ruong"] == viec["ruong"]:
                viec["ruongdamo"], viec["lucmo"], viec["solanmo"] = viec["ruong"], 0., 0
                return "dang"
            if viec["solanmo"] >= SOLANMORUONG:
                # Phòng hờ số rương đọc từ game lệch: rương không mở được thì coi như không có rương đó và các rương sau nó (món chỉ định
                # rương đó thì bỏ món ở lượt sau)
                print(f"[CẤT KHO] Mở rương {viec['ruong']} {SOLANMORUONG} lần không được, coi như không có")
                viec["khongmo"].add(viec["ruong"])
                viec["ruongday"].add(viec["ruong"])
                if viec["ruong"] > 1:
                    viec["soruong"] = min(viec["soruong"], viec["ruong"] - 1)
                viec["lucmo"], viec["solanmo"] = 0., 0
                return "dang"
            viec["trangthai"] = f"mở rương {viec['ruong']}"
            viec["ruongdamo"] = 0
            viec["lucmo"] = now
            viec["solanmo"] += 1
            viec["is_damokho"] = True
            moitruong.action_thucthicaulenh(f"pawn {manpc} {viec['ruong']}", douutien = DOUUTIEN_KHANCAP)
            return "dang"

        o, is_gop = self._chonokho(viec, kho, mon)
        if o is None:
            # Rương này hết chỗ: lượt sau chọn lại rương (món chỉ định rương này thì bỏ món)
            viec["ruongday"].add(viec["ruong"])
            return "dang"
        viec["trangthai"] = f"cất {mon['ten']} ×{mon['cat']} vào rương {viec['ruong']} ô {o + 1}"
        lenh = f"pawn + {manpc} {mon['id']:x}#{mon['cat']} {o + 1}"
        print(f"[CẤT KHO] {lenh} ({mon['ten']}{', gộp chồng' if is_gop else ''})")
        moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_KHANCAP)
        viec["dangcho"] = {"id": mon["id"], "ten": mon["ten"], "soluong": mon["soluong"], "cat": mon["cat"], "ruong": viec["ruong"], "o": o,
                           "is_gop": is_gop, "lucgui": now}
        return "dang"

    def batdau_catkho_sauban(self):
        # Gọi khi bán rác + sửa đồ xong: bật "Tự cất sau bán rác" và có món cần cất thì tạo việc (đang có việc bấm tay thì làm tiếp việc đó)
        if self._catkho or not tailuat()["is_catkhosauban"] or not self._laymoncatkho():
            return
        self._catkho = self._taoviec(LYDOCATKHO_BANRAC)
        print("[CẤT KHO] Bắt đầu cất kho sau bán rác")

    def _xulycatkhobanrac(self):
        # Bước cất kho trong quy trình về bán rác (đang đứng ở Tân Thủ Thôn, di chuyển trực tiếp như sửa đồ). -> True khi xong / không có việc
        viec = self._catkho
        if not viec:
            return True
        if self.moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            self._ketthuccatkho(viec, "không ở Tân Thủ Thôn")
            return True
        kq = self._buoccatkho(viec)
        if isinstance(kq, tuple):
            self.moitruong.action_dichuyengiukhoangcachtoidadiem(kq[1], kq[2], khoangcachtoida = KHOANGCACHQUANKHO - 1)
            return False
        return kq in ("xong", "lỗi")

    def _dondepcatkho(self):
        # Quy trình về bán rác bị dừng giữa chừng (tắt bán rác, làm mới...) khi đang cất kho / giao đồ: bỏ việc dở (yêu cầu giao quay về
        # chờ), bước bán về 0 (kẻo lần về bán sau nhảy thẳng vào bước cất kho / giao mà bỏ qua bán)
        if self._trangthaiveban == 0 and self._buocbanrac in (3, 4):
            self._buocbanrac = 0
            self._bogiaodobanrac()
            if self._catkho and self._catkho["lydo"] == LYDOCATKHO_BANRAC:
                print("[CẤT KHO] Quy trình bán rác đã dừng, bỏ việc cất kho dở")
                self._catkho = None

    def _xulycatkho(self):
        # Việc cất kho bấm tay, gọi thay lộ trình điểm đánh -> yêu cầu di chuyển hoặc None
        viec = self._catkho
        if not viec:
            return None
        moitruong = self.moitruong
        if moitruong.get_is_nhanvatdachet() or moitruong.get_is_dangvankhi() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0:
            return None
        if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            viec["trangthai"] = "đang về Tân Thủ Thôn"
            if time.time() - viec["batdau"] > THOIGIANCATKHOLENHTAYTOIDA:
                self._ketthuccatkho(viec, f"quá {int(THOIGIANCATKHOLENHTAYTOIDA // 60)} phút chưa về tới Tân Thủ Thôn")
                return None
            buoc = self._lapbuocditoibando(BANDO_TANTHUTHON, is_hoithanhphu = True)
            if buoc["loai"] != "toinoi":
                return self._thuchienbuocditoibando(buoc, BANDO_TANTHUTHON, None, "[CẤT KHO] Tân Thủ Thôn")
        kq = self._buoccatkho(viec)
        if isinstance(kq, tuple):
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (kq[1], kq[2], BANDO_TANTHUTHON), "khoangcachtoida": KHOANGCACHQUANKHO - 1}
        return None
