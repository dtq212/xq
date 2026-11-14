# Cất kho: món trong túi khớp bảng Cất kho (luattuido_xq "catkho") đem gửi Quản Khố ở Tân Thủ Thôn (X_QUANKHO_TANTHUTHON, ...).
# Chạy sau mỗi lần về bán rác (bước sau sửa đồ của _xulydangbanrac, nếu bật "is_catkhosauban") và khi bấm tay / Telegram (/catkho):
# về Tân Thủ Thôn như giao đồ, trong lúc đó không chọn quái, lộ trình điểm đánh tạm dừng.
# Lệnh game (7e# = id đối tượng Quản Khố hệ 16, tìm theo tên):
# Lệnh tay khi đang ở Chu Quốc: cất luôn ở Quản Khố Chu Quốc (X_KHO_CHU, Y_KHO_CHU), không Hồi Thành Phù về Tân Thủ Thôn.
#   mở rương  : pawn 7e# <rương>                        (rương từ 1)
#   cất vào   : pawn + 7e# <id món>#<số lượng> <ô rương>   (ô từ 1; ô đang có cùng món thì gộp chồng; số lượng nhỏ hơn chồng = cất 1 phần)
# Đọc rương đang mở bằng moitruong.get_khodangmo (chỉ rương vừa mở có dữ liệu). Mỗi món: cất vào rương luật chỉ định (đầy thì bỏ món
# đó, báo), luật để tự động thì rương đang mở còn chỗ / rương kế, hết rương thì báo kho đầy; trong rương ưu tiên gộp chồng cùng tên,
# không thì ô trống đầu tiên. "Giữ lại" của luật: chừa chừng đó cái (theo tên) trong túi, cất phần còn lại. Gửi xong chờ rồi xem món đã
# rời túi / chồng đã giảm chưa: chưa thì ô đó không gộp được (đầy chồng...) / thử lại, quá SOLANTHUCATKHO lần thì bỏ món đó (đồ khoá...)
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import time
import unicodedata
import uuid
from collections import Counter

from hangso_xq import *
from luattuido_xq import tailuat
from moitruong_xq import DOUUTIEN_KHANCAP
from thongbao_xq import baosuco
from tienich_xq import phatam

LYDOCATKHO_BANRAC = "banrac"
LYDOCATKHO_LENHTAY = "lenhtay"
# Kéo cấp xong: acc chính cất sách "Nhập Môn" thu hồi từ acc gà (tactu_keocap_xq._catsachthuhoikc), việc giữ trong trạng thái kéo cấp
LYDOCATKHO_KEOCAP = "keocap"
KHOANGCACHQUANKHO = 3.
# Các ô hành trang đầu bỏ qua (ô dùng nhanh)
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

    def _laymoncatkho(self, tientos = None):
        # Chồng trong túi cần cất theo bảng Cất kho, theo thứ tự ô: [{"vitri", "id", "ten", "soluong" (của chồng, 0 = không chồng được),
        # "cat" (số cất từ chồng này), "ruong" (0 = tự động)}]. Tính theo tên: tổng trong túi trừ "giữ lại" của luật, lấy dần từ ô đầu
        # (chồng cuối có thể chỉ cất 1 phần). Luật cần mô tả mà chưa đọc được thì bỏ qua lượt này
        # tientos (việc cất riêng, vd kéo cấp cất sách "Nhập Môn"): bỏ bảng Cất kho, cất hết món có tên bắt đầu bằng 1 trong các tiền tố
        # (không phân biệt hoa thường), rương tự động
        moitruong = self.moitruong
        layluat = self._layluatcatkho
        if tientos:
            tientos = tuple(unicodedata.normalize("NFC", t).lower() for t in tientos)
            luatrieng = {"ruong": 0, "giulai": 0}

            def layluat(ten, vitri):
                return luatrieng if unicodedata.normalize("NFC", ten).strip().lower().startswith(tientos) else None
        soluongo = moitruong.get_soluongvatphamhanhtrangtoida() + 1
        tens = moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        ids = moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        nhoms = {}
        for vitri in range(VITRICATKHODAUTIEN, min(len(tens), len(ids))):
            if not ids[vitri] or ids[vitri] <= 0 or not tens[vitri]:
                continue
            luat = layluat(tens[vitri], vitri)
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
        # Việc cất riêng (kéo cấp cất sách, không nằm ở self._catkho) xong thì đừng xoá việc cất kho khác đang chạy
        if self._catkho is viec or viec.get("lydo") != LYDOCATKHO_KEOCAP:
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
        # Cất xong bình thường thì chỉ ghi log, không gửi Telegram (người dùng thấy quá nhiều);
        # vẫn gửi khi có món không cất được, có lỗi, hoặc cất theo lệnh tay
        if bo or loi or viec["lydo"] == LYDOCATKHO_LENHTAY:
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

        mons = [m for m in self._laymoncatkho(viec.get("tientos")) if m["ten"] not in viec["boqua"]]
        if not mons:
            return self._ketthuccatkho(viec)

        # Chu Quốc: cất ở Quản Khố Chu Quốc (X_KHO_CHU, Y_KHO_CHU). Không gửi pawn qua Chủ Tiệm Sửa Chữa nữa (chỉ mở được rương 1)
        tennpc = QUANKHO
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = QUANKHO)
        if moitruong.get_idbandohientai() == BANDO_CHUQUOC:
            xmacdinh, ymacdinh = X_KHO_CHU, Y_KHO_CHU
        else:
            xmacdinh, ymacdinh = X_QUANKHO_TANTHUTHON, Y_QUANKHO_TANTHUTHON
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHQUANKHO:
            viec["trangthai"] = f"đang tới {tennpc}"
            x, y = moitruong.get_toado(diachinpc) if diachinpc else (xmacdinh, ymacdinh)
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

    # ---------------- Sắp xếp kho ----------------
    # Bấm tay khi cửa sổ kho đang mở (Quản Khố, hoặc Bảo Khố Di Động "use <id>#" ở bất kỳ đâu: mã kho đọc ở moitruong.get_makhodangmo),
    # hoặc đứng cạnh Quản Khố / Chủ Tiệm Sửa Chữa (Chu). Không di chuyển nhân vật.
    # Lệnh kho (mã = ID NPC kho, vd "a6#" NPC Bảo Khố): đổi chỗ "pawn >" CHỈ trong cùng rương; sang rương khác chỉ có lệnh chuyển
    # "pawn & <mã> <ô> <rương đích>" (món rơi vào ô trống của rương đích, rương đích đầy thì không được; kéo tay ô 44 sang rương 2,
    # Gạ 364 2026-11-12), không đổi chỗ được 2 món khác rương. Nên làm như xếp 4 túi hành trang:
    # 1. "quet": mở lần lượt mọi rương lấy dữ liệu (chỉ rương đang mở có dữ liệu).
    # 2. "gom": coi cả kho là 1 dãy ô (rương 1 ô 1 .. rương cuối ô 49), đồ sắp theo thứ tự hành trang (_khoasapxepvatpham) rồi mã loại,
    #    cắt mỗi rương 1 đoạn 49 món => số món từng mã mỗi rương cần có. Lấp dần từng rương (ý người dùng, ít lần mở rương: mỗi lần mở
    #    tốn 1 lệnh pawn ~1s): với rương r, "don": mở r, chuyển liền các món thừa của r sang rương sau còn ô trống (ưu tiên rương cần
    #    món đó); "nap": mở lần lượt các rương sau đang có món r thiếu (rương không có thì khỏi mở), chuyển hết sang r tới khi r đầy.
    #    r chưa đủ (kho ít ô trống) thì lặp don / nap, vòng không chuyển được gì thì bỏ qua r. Rương trước r đã đủ 49 món đúng nên không
    #    đụng tới. Mô hình đếm số món + ô trống mỗi rương; rương nào mở ra cũng lấy dữ liệu thật. Hết rương thì quét lại cả kho kiểm
    #    tra, còn lệch thì gom lại từ rương 1 (tối đa soluotgomtoida lượt, 2 lượt liền không bớt lệch thì thôi). Kho hết ô trống thì bỏ gom.
    # 3. Xếp trong từng rương như dưới.
    # Từng rương: mở rương ("pawn <mã> <rương>"), xếp đồ theo cùng thứ tự với hành trang (_khoasapxepvatpham) dồn từ ô 1, bằng lệnh
    # kéo thả "pawn > <mã> <ô nguồn> <ô đích>" (ô từ 1, trong rương đang mở; đích có đồ thì đổi chỗ 2 món). Mỗi lệnh đặt ít nhất 1 món
    # vào đúng ô cuối (tối đa 48 lệnh / rương).
    # Dữ liệu rương trong bộ nhớ KHÔNG đổi sau lệnh kéo thả, chỉ đổi khi mở lại rương, mà mở lại thì 0.8-1.6s mới có dữ liệu (đo Gạ 364
    # 2026-11-12; bản đầu chờ dữ liệu đổi nên tưởng lệnh hỏng, gửi lại 2-3 lần => 2 món đổi chỗ chẵn lần là về chỗ cũ). Nên bot tự nhớ
    # rương (mô hình): mở rương lấy dữ liệu thật, gửi liền cả loạt lệnh (cách GIANCACHLENHSAPXEPKHO giây), mỗi lệnh đổi chỗ trong mô hình;
    # mô hình xong thì mở lại rương kiểm tra, còn sai thì xếp tiếp từ dữ liệu thật, quá soluottoida lượt / 3 lượt liền rương không đổi
    # thì dừng báo lỗi.
    # Chưa gộp chồng trong kho (chưa biết lệnh), chỉ xếp các chồng cùng tên nằm cạnh nhau
    def battat_sapxepkho(self):
        if self._sapxepkho:
            self._ketthucsapxepkho("Dừng sắp xếp kho")
            return
        # pha "quet" / "gom": gom giữa các rương (ruongs: mô hình {rương: [ô]}, ban: rương vừa nhận đồ chưa biết ô, ruongmo: rương có dữ
        # liệu mới nhất, canmo: rương _chodulieuruong đang chờ); "mo": đã / cần gửi lệnh mở rương (lucmo = 0 là chưa gửi), chờ dữ liệu;
        # "xep": gửi lệnh đổi chỗ trong rương theo mô hình
        self._sapxepkho = {"batdau": time.time(), "ruong": 1, "soruong": 0, "pha": "quet", "lucmo": 0., "anhmo": None, "solanmo": 0,
                           "mohinh": None, "lucgui": 0., "soluot": 0, "anhluottruoc": None, "solankhongdoi": 0, "solenh": 0, "loi": [],
                           "ruongs": {}, "ban": set(), "ruongmo": 0, "canmo": 0, "luotgom": 0, "solenhgom": 0, "lechtruoc": None,
                           "solangomkhongbot": 0, "sochuyen": 0,
                           "quetcu": {}, "dachuyen": [], "dadat": set()}
        phatam("Bắt đầu sắp xếp kho")
        print(f"{self.moitruong.get_tendoituong()}: [SẮP XẾP KHO] bắt đầu")

    def get_is_dangsapxepkho(self):
        return bool(self._sapxepkho)

    def _ketthucsapxepkho(self, thongbao):
        viec = self._sapxepkho
        self._sapxepkho = None
        solenh = viec["solenh"] if viec else 0
        sochuyen = viec["sochuyen"] if viec else 0
        loi = f" | {'; '.join(viec['loi'])}" if viec and viec["loi"] else ""
        noidung = f"[SẮP XẾP KHO] {thongbao} (chuyển rương {sochuyen} lần, đổi chỗ {solenh} lần){loi}"
        print(f"{self.moitruong.get_tendoituong()}: {noidung}")
        self.moitruong._inlog(noidung)
        phatam(thongbao)

    def _logsapxepkho(self, noidung):
        print(f"{self.moitruong.get_tendoituong()}: [SẮP XẾP KHO] {noidung}")
        self.moitruong._inlog(f"[SẮP XẾP KHO] {noidung}")

    def _laymakho(self):
        # Mã đứng sau "pawn": cửa sổ kho đang mở (cả kho mở bằng Bảo Khố Di Động), không thì NPC kho đứng gần (Quản Khố, ở Chu thì cả
        # Chủ Tiệm Sửa Chữa), không có nữa thì mã client tự gửi gần nhất
        moitruong = self.moitruong
        makho = moitruong.get_makhodangmo()
        if makho:
            return makho
        for tennpc in (QUANKHO, CHUTIEMSUACHUA):
            diachi = moitruong.action_timkiemnhanvat(tennhanvat = tennpc)
            if diachi and moitruong.get_khoangcach(diachi) <= KHOANGCACHQUANKHO + 2:
                return f"{moitruong.get_iddoituong(diachi):x}#"
        return moitruong.get_makhoganday()

    def _timbuocsapxepkho(self, os):
        # (ô a, ô b) từ 0 cần đổi chỗ cho rương đang mở, None nếu rương đã xếp xong. Đích: đồ dồn từ ô 0 theo _khoasapxepvatpham rồi
        # mã loại (cùng tên nằm cạnh), ô trống ở cuối. So bằng mã loại (cùng tên cùng mã), ô trống mã 0
        mas = [ma for _, _, ma in os]
        dangcos = sorted(((self._khoasapxepvatpham(ten), ma) for ten, _, ma in os if ma), key = lambda k: k)
        dich = [ma for _, ma in dangcos] + [0] * (len(os) - len(dangcos))
        for o in range(len(os)):
            if mas[o] == dich[o]:
                continue
            nguons = [i for i in range(o + 1, len(os)) if mas[i] == dich[o] and mas[i] != dich[i]]
            if not nguons:
                continue
            # Ưu tiên nguồn mà món đang ở ô o cũng về đúng chỗ sau khi đổi (1 lệnh đặt đúng 2 món)
            nguon = next((i for i in nguons if dich[i] == mas[o]), nguons[0])
            return o, nguon
        return None

    def _dichgomkho(self, ruongs):
        # {rương: Counter(mã loại)} rương đó cần có: cả kho sắp như 1 dãy, mỗi rương 1 đoạn len(ô) món
        dangcos = sorted((self._khoasapxepvatpham(ten), ma) for r in sorted(ruongs) for ten, _, ma in ruongs[r] if ma)
        dich = {}
        vitri = 0
        for r in sorted(ruongs):
            soo = len(ruongs[r])
            dich[r] = Counter(ma for _, ma in dangcos[vitri:vitri + soo])
            vitri += soo
        return dich

    @staticmethod
    def _lechgomkho(ruongs, dich):
        # Tổng số món đang nằm sai rương (0 = đã gom xong)
        return sum(max(0, sl - dich[r][ma]) for r in ruongs for ma, sl in Counter(ma for _, _, ma in ruongs[r] if ma).items())

    def _chodulieuruong(self, viec, makho, kho, now, ruong, thoigiancho):
        # Mở rương ruong (luôn mở lại để có dữ liệu mới) rồi chờ dữ liệu về: danh sách ô khi có, None khi đang chờ, False khi mở
        # SOLANMORUONG lần không được
        if viec["canmo"] != ruong or not viec["lucmo"]:
            viec["canmo"], viec["solanmo"] = ruong, 0
            self._moruongsapxepkho(viec, makho, kho, now, ruong = ruong, pha = viec["pha"])
            return None
        if kho and kho["ruong"] == ruong and (kho["os"] != viec["anhmo"] or now - viec["lucmo"] >= thoigiancho):
            viec["lucmo"], viec["canmo"], viec["solanmo"] = 0., 0, 0
            return list(kho["os"])
        if now - viec["lucmo"] < thoigiancho:
            return None
        if viec["solanmo"] >= SOLANMORUONG:
            return False
        self._moruongsapxepkho(viec, makho, kho, now, ruong = ruong, pha = viec["pha"])
        return None

    def _buocgomkho(self, viec, makho, kho, now, thoigiancho, soluotgomtoida):
        # 1 bước pha "quet" / "gom"
        moitruong = self.moitruong
        tennv = moitruong.get_tendoituong()
        soruong = max(1, viec["soruong"])
        if viec["pha"] == "quet":
            os = self._chodulieuruong(viec, makho, kho, now, viec["ruong"], thoigiancho)
            if os is None:
                return
            if os is False:
                viec["loi"].append(f"không mở được rương {viec['ruong']}")
                self._ketthucsapxepkho(f"Dừng sắp xếp kho ở rương {viec['ruong']}")
                return
            viec["ruongs"][viec["ruong"]] = os
            viec["ruongmo"] = viec["ruong"]
            if viec["ruong"] < soruong:
                viec["ruong"] += 1
                return
            viec["ban"] = set()
            dich = self._dichgomkho(viec["ruongs"])
            lech = self._lechgomkho(viec["ruongs"], dich)
            self._kiemchungchuyenruong(viec)
            viec["quetcu"] = {r: list(os) for r, os in viec["ruongs"].items()}
            viec["dachuyen"], viec["dadat"] = [], set()
            trongs = ", ".join(f"r{r} trống {sum(1 for _, _, ma in os if not ma)}" for r, os in sorted(viec["ruongs"].items()))
            self._logsapxepkho(f"đã quét {soruong} rương ({trongs}), {lech} món nằm sai rương (lượt gom {viec['luotgom'] + 1})")
            # 2 lượt gom liền không bớt được món sai rương nào (1 lượt thì có thể chỉ còn 1-2 lệnh mà game bỏ mất) / quá số lượt: thôi
            # gom, chỉ xếp trong rương
            if lech and viec["lechtruoc"] is not None and lech >= viec["lechtruoc"]:
                viec["solangomkhongbot"] += 1
            else:
                viec["solangomkhongbot"] = 0
            if lech and viec["solangomkhongbot"] >= 2:
                viec["loi"].append(f"còn {lech} món chưa gom được về đúng rương (lệnh chuyển rương không có tác dụng?)")
                lech = 0
            elif lech and viec["luotgom"] >= soluotgomtoida:
                viec["loi"].append(f"còn {lech} món chưa gom được sau {soluotgomtoida} lượt")
                lech = 0
            if not lech:
                viec["pha"], viec["ruong"], viec["lucmo"], viec["solanmo"] = "mo", 1, 0., 0
                return
            viec["lechtruoc"] = lech
            viec["luotgom"] += 1
            viec["solenhgom"] = 0
            viec["pha"] = "gom"
            # Mô hình gom: đích, số món đang có và số ô trống mỗi rương (từ lần quét vừa xong)
            viec["dich"] = dich
            viec["dem"] = {r: Counter(ma for _, _, ma in os if ma) for r, os in viec["ruongs"].items()}
            viec["trong"] = {r: sum(1 for _, _, ma in os if not ma) for r, os in viec["ruongs"].items()}
            viec["rdich"], viec["buocgom"], viec["nguonnap"], viec["hangdoi"], viec["chuyenvong"] = 1, "don", 0, [], 0
            return

        # pha "gom": gửi hết hàng đợi lệnh chuyển của rương đang mở trước
        if viec["hangdoi"]:
            nguon, o, dich, ma, ten = viec["hangdoi"].pop(0)
            lenh = f"pawn & {makho} {o + 1} {dich}"
            if moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_KHANCAP):
                if viec["sochuyen"] < 3:
                    moitruong._inlog(f"[SẮP XẾP KHO] {lenh} ({ten} từ rương {nguon} sang rương {dich})")
                quetdich = viec["quetcu"].get(dich)
                is_cungotrong = bool(quetdich) and not quetdich[o][2] and (dich, o) not in viec["dadat"]
                viec["dachuyen"].append((nguon, o, dich, ma, ten, is_cungotrong))
                viec["dadat"].add((dich, o))
                viec["lucgui"] = now
                viec["sochuyen"] += 1
                viec["solenhgom"] += 1
                viec["chuyenvong"] += 1
            return

        dich, dem, trong = viec["dich"], viec["dem"], viec["trong"]
        r = viec["rdich"]
        if r > soruong:
            # Gom xong mọi rương theo mô hình: quét lại cả kho kiểm tra (lệnh có thể bị bỏ)
            viec["pha"], viec["ruong"], viec["lucmo"], viec["canmo"] = "quet", 1, 0., 0
            return

        def thieu(ma):
            return dich[r][ma] - dem[r][ma]

        def chuyen(nguon, o, ma, ten, toi):
            # Xếp 1 lệnh vào hàng đợi, cập nhật mô hình luôn (chọn đích cho món sau theo số ô trống mới)
            viec["hangdoi"].append((nguon, o, toi, ma, ten))
            dem[nguon][ma] -= 1
            dem[toi][ma] += 1
            trong[nguon] += 1
            trong[toi] -= 1

        def ketthucvong():
            # Hết 1 vòng don / nap của r: đủ rồi / vòng không chuyển được gì thì sang rương sau, không thì lặp vòng mới
            dudu = all(dem[r][ma] == sl for ma, sl in dich[r].items()) and not any(sl > dich[r][ma] for ma, sl in dem[r].items())
            if not dudu and not viec["chuyenvong"]:
                self._logsapxepkho(f"rương {r} chưa gom đủ (không còn chỗ để đổi), bỏ qua")
            if dudu or not viec["chuyenvong"]:
                viec["rdich"] += 1
            viec["buocgom"], viec["chuyenvong"] = "don", 0

        if viec["buocgom"] == "don":
            sothua = sum(max(0, sl - dich[r][ma]) for ma, sl in dem[r].items())
            chosau = sum(trong[t] for t in range(r + 1, soruong + 1))
            if sothua and chosau:
                os = self._chodulieuruong(viec, makho, kho, now, r, thoigiancho)
                if os is None:
                    return
                if os is False:
                    viec["loi"].append(f"không mở được rương {r}")
                    self._ketthucsapxepkho(f"Dừng sắp xếp kho ở rương {r}")
                    return
                dem[r] = Counter(ma for _, _, ma in os if ma)
                trong[r] = sum(1 for _, _, ma in os if not ma)
                for o, (ten, _, ma) in enumerate(os):
                    if not ma or dem[r][ma] <= dich[r][ma]:
                        continue
                    toidas = [t for t in range(r + 1, soruong + 1) if trong[t]]
                    if not toidas:
                        break
                    # Ưu tiên rương cần món này (khỏi chuyển lần nữa), không thì rương còn nhiều ô trống nhất
                    toi = max(toidas, key = lambda t: (dich[t][ma] > dem[t][ma], trong[t]))
                    chuyen(r, o, ma, ten, toi)
            viec["buocgom"], viec["nguonnap"] = "nap", r + 1
            return

        # buocgom "nap": rương sau kế tiếp đang có món r thiếu
        if not trong[r] or not any(thieu(ma) > 0 for ma in dich[r]):
            ketthucvong()
            return
        nguon = next((t for t in range(viec["nguonnap"], soruong + 1) if any(thieu(ma) > 0 and dem[t][ma] > 0 for ma in dem[t])), None)
        if nguon is None:
            ketthucvong()
            return
        os = self._chodulieuruong(viec, makho, kho, now, nguon, thoigiancho)
        if os is None:
            return
        if os is False:
            viec["loi"].append(f"không mở được rương {nguon}")
            self._ketthucsapxepkho(f"Dừng sắp xếp kho ở rương {nguon}")
            return
        dem[nguon] = Counter(ma for _, _, ma in os if ma)
        trong[nguon] = sum(1 for _, _, ma in os if not ma)
        for o, (ten, _, ma) in enumerate(os):
            if ma and thieu(ma) > 0 and trong[r]:
                chuyen(nguon, o, ma, ten, r)
        viec["nguonnap"] = nguon + 1

    def _kiemchungchuyenruong(self, viec):
        # So lần quét này với lần quét đầu lượt gom: từng lệnh "pawn &" có đi không (ô nguồn hết món đó), rơi vào ô cùng số ở rương đích
        # không, và lúc gửi ô cùng số đó trống hay có đồ. Để biết "pawn &" thả món vào ô trống bất kỳ hay vào đúng ô cùng số
        # (nghi vì lần chạy Gạ 18:42 có lệnh gửi mấy lượt vẫn không đi)
        if not viec["dachuyen"]:
            return
        ruongs = viec["ruongs"]
        thongke = {}
        chitiets = []
        for nguon, o, dich, ma, ten, is_cungotrong in viec["dachuyen"]:
            is_di = ruongs[nguon][o][2] != ma
            is_cungo = ruongs[dich][o][2] == ma
            khoa = ("đi" if is_di else "KHÔNG đi") + (", ô cùng số lúc gửi trống" if is_cungotrong else ", ô cùng số lúc gửi có đồ")
            thongke[khoa] = thongke.get(khoa, 0) + 1
            if len(chitiets) < 20:
                chitiets.append(f"r{nguon}ô{o + 1}->r{dich} {ten}: {'đi' if is_di else 'KHÔNG đi'}"
                                f"{' (rơi đúng ô cùng số)' if is_di and is_cungo else ''}{'' if is_cungotrong else ' [ô cùng số có đồ]'}")
        self._logsapxepkho("kiểm chứng chuyển rương: " + "; ".join(f"{k}: {v}" for k, v in thongke.items()))
        self._logsapxepkho("chi tiết: " + " | ".join(chitiets))

    def _dichtrongruong(self, os):
        # Mã loại từng ô sau khi xếp xong 1 rương (như _timbuocsapxepkho)
        dangcos = sorted((self._khoasapxepvatpham(ten), ma) for ten, _, ma in os if ma)
        return [ma for _, ma in dangcos] + [0] * (len(os) - len(dangcos))

    def _moruongsapxepkho(self, viec, makho, kho, now, ruong = None, pha = "mo"):
        # Gửi lệnh mở rương (mặc định viec["ruong"]), nhớ dữ liệu lúc gửi để biết dữ liệu mới đã về
        viec["pha"] = pha
        viec["anhmo"] = kho["os"] if kho else None
        viec["lucmo"] = now
        viec["lucgui"] = now
        viec["solanmo"] += 1
        self.moitruong.action_thucthicaulenh(f"pawn {makho} {ruong or viec['ruong']}", douutien = DOUUTIEN_KHANCAP)

    # giancachlenh: máy chủ chỉ nhận ~1 lệnh pawn mỗi ~0.9-1s, lệnh tới sớm hơn bị bỏ (Gạ 2026-11-12 18:42 gửi cách 0.3s: các lệnh "pawn &"
    # ăn được cách nhau 0.91-1.27s, lượt 1 gửi 16 ăn 3, lượt 2 gửi 13 ăn 4; lệnh mở rương gửi sau lệnh trước 0.2s không ăn, gửi lại thì
    # ~0.2s có dữ liệu). Không spam thử lại được: lệnh kéo thả / chuyển rương không làm đổi dữ liệu rương trong bộ nhớ (phải mở lại rương
    # mới biết ăn chưa, cũng tốn 1 lệnh pawn), gửi lại lệnh đổi chỗ đã ăn thì 2 món đổi về chỗ cũ. Gửi đều 1 lệnh / 1s là nhanh nhất
    def action_sapxepkho(self, giancachlenh = 1.0, thoigianchomoruong = 1.5, soluottoida = 6, soluotgomtoida = 15, thoigiantoida = 600.):
        viec = self._sapxepkho
        if not viec:
            return
        moitruong = self.moitruong
        now = time.time()
        if now - viec["batdau"] > thoigiantoida:
            self._ketthucsapxepkho("Sắp xếp kho quá lâu, dừng lại")
            return
        if moitruong.get_is_nhanvatdachet():
            self._ketthucsapxepkho("Nhân vật chết, dừng sắp xếp kho")
            return
        if now - viec["lucgui"] < giancachlenh:
            return
        makho = self._laymakho()
        if not makho:
            self._ketthucsapxepkho("Không biết mã kho: mở kho (Quản Khố / Bảo Khố Di Động) rồi bấm lại")
            return
        kho = moitruong.get_khodangmo()
        if kho and 0 < kho["soruong"] <= 20:
            viec["soruong"] = kho["soruong"]
        tennv = moitruong.get_tendoituong()

        if viec["pha"] in ("quet", "gom"):
            self._buocgomkho(viec, makho, kho, now, thoigianchomoruong, soluotgomtoida)
            return

        if viec["pha"] == "mo":
            if not viec["lucmo"]:
                self._moruongsapxepkho(viec, makho, kho, now)
                return
            # Dữ liệu mới về: đúng rương và khác lúc gửi lệnh mở; giống hệt thì chờ đủ thoigianchomoruong (rương không đổi gì cũng thế)
            if not kho or kho["ruong"] != viec["ruong"] or (kho["os"] == viec["anhmo"] and now - viec["lucmo"] < thoigianchomoruong):
                if now - viec["lucmo"] < thoigianchomoruong:
                    return
                if viec["solanmo"] >= SOLANMORUONG:
                    viec["loi"].append(f"không mở được rương {viec['ruong']}")
                    self._ketthucsapxepkho(f"Dừng sắp xếp kho ở rương {viec['ruong']}")
                    return
                self._moruongsapxepkho(viec, makho, kho, now)
                return
            viec["solanmo"] = 0
            viec["lucmo"] = 0.
            if self._timbuocsapxepkho(kho["os"]) is None:
                self._logsapxepkho(f"xong rương {viec['ruong']} ({viec['soluot']} lượt)")
                if viec["ruong"] >= max(1, viec["soruong"]):
                    self._ketthucsapxepkho(f"Đã sắp xếp xong kho ({viec['ruong']} rương)")
                    return
                viec["ruong"] += 1
                viec["soluot"], viec["anhluottruoc"], viec["solankhongdoi"] = 0, None, 0
                return
            # Còn sai: lượt mới từ dữ liệu thật. 3 lượt liền gửi lệnh mà rương y như trước lượt => lệnh không có tác dụng (1 lượt thì có
            # thể chỉ còn 1-2 lệnh mà game bỏ mất)
            if viec["soluot"] and kho["os"] == viec["anhluottruoc"]:
                viec["solankhongdoi"] += 1
                if viec["solankhongdoi"] >= 3:
                    viec["loi"].append(f"rương {viec['ruong']}: lệnh kéo thả không có tác dụng")
                    self._ketthucsapxepkho("Không đổi chỗ được đồ trong kho, dừng sắp xếp kho")
                    return
            else:
                viec["solankhongdoi"] = 0
            if viec["soluot"] >= soluottoida:
                viec["loi"].append(f"rương {viec['ruong']}: {soluottoida} lượt vẫn chưa xếp xong")
                self._ketthucsapxepkho("Sắp xếp kho chưa xong, dừng lại")
                return
            viec["soluot"] += 1
            viec["anhluottruoc"] = kho["os"]
            viec["mohinh"] = list(kho["os"])
            viec["pha"] = "xep"
            if viec["soluot"] > 1:
                sai = sum(1 for a, b in zip(kho["os"], self._dichtrongruong(kho["os"])) if a[2] != b)
                self._logsapxepkho(f"rương {viec['ruong']} còn {sai} ô sai sau lượt trước, xếp lượt {viec['soluot']}")
            return

        # pha "xep": lệnh kế theo mô hình; mô hình đã xong thì mở lại rương kiểm tra
        mohinh = viec["mohinh"]
        buoc = self._timbuocsapxepkho(mohinh)
        if buoc is None:
            self._moruongsapxepkho(viec, makho, kho, now)
            viec["solanmo"] = 1
            return
        a, b = buoc
        # "pawn > <mã> <ô nguồn> <ô đích>": nguồn trước (kéo tay ô 9 thả ô 8 thì client gửi "pawn > a6# 9 8", Gạ 364 2026-11-12)
        lenh = f"pawn > {makho} {b + 1} {a + 1}"
        if moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_KHANCAP):
            if viec["solenh"] < 3:
                moitruong._inlog(f"[SẮP XẾP KHO] {lenh} ({mohinh[b][0]} <-> {mohinh[a][0] or 'ô trống'})")
            mohinh[a], mohinh[b] = mohinh[b], mohinh[a]
            viec["lucgui"] = now
            viec["solenh"] += 1

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
        idbando = moitruong.get_idbandohientai()
        # Đang ở Chu Quốc thì cất luôn ở Chu (chạy bộ tới Chủ Tiệm Sửa Chữa), không phù về Tân Thủ Thôn
        if idbando not in (BANDO_TANTHUTHON, BANDO_CHUQUOC):
            viec["trangthai"] = "đang về Tân Thủ Thôn"
            if time.time() - viec["batdau"] > THOIGIANCATKHOLENHTAYTOIDA:
                self._ketthuccatkho(viec, f"quá {int(THOIGIANCATKHOLENHTAYTOIDA // 60)} phút chưa về tới Tân Thủ Thôn")
                return None
            buoc = self._lapbuocditoibando(BANDO_TANTHUTHON, is_hoithanhphu = True)
            if buoc["loai"] != "toinoi":
                return self._thuchienbuocditoibando(buoc, BANDO_TANTHUTHON, None, "[CẤT KHO] Tân Thủ Thôn")
        kq = self._buoccatkho(viec)
        if isinstance(kq, tuple):
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (kq[1], kq[2], idbando), "khoangcachtoida": KHOANGCACHQUANKHO - 1}
        return None
