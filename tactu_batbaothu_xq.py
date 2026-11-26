# Bắt bảo thú (tab Khác, bật tay theo nhân vật): bắt quái làm bảo thú giang hồ bằng Dây Càn Khôn ("pf2 51 <id>#" như Bắt yêu quái của sư
# môn), con bắt được mà tư chất (Thể Chất / Tinh Thần / Sức Mạnh / Nại Lực / Mẫn Tiệp đọc ở ô bảo thú, MoiTruong.get_danhsachbaothugiangho)
# không đạt ngưỡng người dùng điền thì phóng sinh ("pet <id># free"), đạt thì giữ, đủ số con thì dừng.
#   - Đang bắt thì bỏ giới hạn quái theo lộ trình điểm đánh (_is_bolotrinhdiemdanh): bản đồ bắt thường không có điểm đánh, trước đây
#     cả bản đồ bị coi "Chưa có điểm đánh" nên không đánh con nào (log 354 26/11 Cầu Cửu Khúc 2, mục tiêu "-")
#   - Chạy SONG SONG với farm (người dùng 26/11): quái phải chết thì con khác mới ra đúng loại / cấp, nên bot vẫn đánh quái, đi lộ trình
#     như thường; quái đúng tên + cấp thì không bao giờ chọn đánh (_is_quaicanbat trong _kiemtramuctieuhople), thấy nó trong
#     KHOANGCACHTHAYBATBAOTHU ô thì bỏ việc đánh, tới gần bắt (get_is_batbaothudichuyen), bắt xong / nó mất thì farm tiếp
#   - Lọc quái theo tên (khớp nguyên tên) và cấp trong tên gốc "( Cấp N )"; không đọc được cấp thì vẫn bắt (ghi log 1 lần)
#   - Máu từ NGUONGMAUBATBAOTHU% trở lên thì chưa bắt (bắt lúc đầy máu chỉ tốn dây): đánh từng cái cho giảm máu (TacTuSuMon._danhgiammau:
#     chiêu đơn mục tiêu của phái, không có thì "kill" rồi ngắt; nhớ 1 cái tụt bao nhiêu %, cú kế có thể làm máu dưới NGUONGMAUANTOAN%
#     thì thôi đánh mà bắt luôn kẻo chết), dưới ngưỡng mới dùng Dây Càn Khôn
#   - Chỉ phóng sinh con MỚI bắt trong lần chạy này (id chưa có lúc bắt đầu), không bao giờ đụng bảo thú đang có sẵn
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import json
import time

from hangso_xq import *
from nhiemvu_xq import chuanhoaten
from tactu_sumon_xq import MAUCAPTRONGTEN, DAYCANKHON, LENHBATBAOTHU, GIANCACHBATBAOTHU, KHOANGCACHBATBAOTHU, NGUONGMAUANTOAN
from tienich_xq import phatam

# 5 tư chất bảo thú (khoá trong MoiTruong.get_danhsachbaothugiangho, tên trên bảng Bảo Thú)
TUCHATBAOTHUs = (("thechat", "Thể Chất"), ("tinhthan", "Tinh Thần"), ("sucmanh", "Sức Mạnh"), ("nailuc", "Nại Lực"), ("mantiep", "Mẫn Tiệp"))
# Bắt được mà 5 tư chất còn đọc ra 0 (máy chủ chưa gửi xong): chờ tối đa chừng này giây rồi mới xét; quá thì giữ lại cho chắc (không phóng sinh
# con chưa biết tư chất)
THOIGIANCHOTUCHATBAOTHU = 5.
# Mặc định: đánh cho quái cần bắt xuống dưới chừng này % máu rồi mới bắt (người dùng 26/11: bắt lúc đầy máu là chưa ổn); chỉnh ở ô
# "Bắt khi máu <" (thiết lập "nguongmau")
NGUONGMAUBATBAOTHU = 50
# Đang chờ chiêu đánh giảm máu (chưa tới lượt / đang khoá) thì chờ tối đa chừng này giây rồi bắt luôn dù máu còn cao
THOIGIANCHODANHGIAMMAUTOIDA = 8.
# Quái cần bắt cách mình trong chừng này ô thì thôi farm, tới bắt
KHOANGCACHTHAYBATBAOTHU = 15.
# Bắt liền chừng này lần mà không ra con mới nào thì dừng (ô bảo thú đầy / quái không bắt được), kẻo tốn hết dây
SOLANBATKHONGRATOIDA = 400
# Thiết lập mặc định (lưu theo nhân vật: _batbaothu_thietlap)
THIETLAPBATBAOTHUMACDINH = {"ten": "", "captu": 0, "capden": 0, "soluong": 1, "nguongmau": NGUONGMAUBATBAOTHU, "is_phongsinh": True, "is_batky": False,
                            "tuchat": {k: 0 for k, _ in TUCHATBAOTHUs}}


def chuanhoathietlapbatbaothu(thietlap):
    # dict / chuỗi JSON từ giao diện hoặc file lưu -> dict đủ khoá đúng kiểu
    if isinstance(thietlap, str):
        try:
            thietlap = json.loads(thietlap)
        except ValueError:
            thietlap = {}
    thietlap = thietlap if isinstance(thietlap, dict) else {}

    def so(v, macdinh = 0):
        try:
            return max(0, int(float(v)))
        except (TypeError, ValueError):
            return macdinh
    tuchat = thietlap.get("tuchat") if isinstance(thietlap.get("tuchat"), dict) else {}
    return {"ten": str(thietlap.get("ten") or "").strip(), "captu": so(thietlap.get("captu")), "capden": so(thietlap.get("capden")),
            "soluong": max(1, so(thietlap.get("soluong"), 1)), "nguongmau": min(100, max(1, so(thietlap.get("nguongmau"), NGUONGMAUBATBAOTHU))), "is_phongsinh": bool(thietlap.get("is_phongsinh", True)),
            "is_batky": bool(thietlap.get("is_batky", False)), "tuchat": {k: so(tuchat.get(k)) for k, _ in TUCHATBAOTHUs}}


def motatuchat(bt):
    return ", ".join(f"{ten} {bt.get(k, 0)}" for k, ten in TUCHATBAOTHUs)


class TacTuBatBaoThu:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def thietlap_batbaothu(self, thietlap):
        self._batbaothu_thietlap = chuanhoathietlapbatbaothu(thietlap)

    def batdau_batbaothu(self):
        if self._batbaothu:
            return
        tl = self._batbaothu_thietlap
        if not tl["ten"]:
            self._ketquabatbaothu = "Chưa điền tên bảo thú (tên quái) cần bắt"
            return
        self._batbaothu = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "farm", "khampha": None, "lucbat": 0., "lucmonphai": 0., "solanmonphai": 0, "solanbat": {}, "idcu": None, "thaymoi": {},
                           "sogiu": 0, "sophongsinh": 0, "solanbatkhongra": 0, "dabaocap": False}
        self._logbbt(f"Bắt đầu bắt {self._motathietlapbatbaothu()} (vừa farm vừa bắt)")
        phatam("Bắt đầu bắt bảo thú")

    def huy_batbaothu(self):
        if self._batbaothu:
            self._ketthucbatbaothu("Đã dừng bắt bảo thú (bấm tay)")

    def get_is_dangbatbaothu(self):
        return bool(self._batbaothu)

    def _is_batbaothudangchay(self):
        # Như Đào khoáng: việc khác đứng trước trong vòng di chuyển đang chạy thì _xulybatbaothu không được gọi
        return bool(self._batbaothu) and time.time() - self._batbaothu.get("lucxuly", 0.) < 2.

    def get_is_batbaothudichuyen(self):
        # Đang tới / đang bắt 1 con đúng tên + cấp: thôi chọn quái đánh, thay lộ trình điểm đánh; không thấy con nào thì farm như thường
        return self._is_batbaothudangchay() and self._batbaothu["chedo"] == "bat"

    def _is_quaicanbat(self, diachi, ten = None):
        # Quái đúng tên + cấp cần bắt: bộ chọn mục tiêu không đánh nó (đánh chết là mất), chỉ _danhgiammau mới đánh 1 cái
        if not self._batbaothu:
            return False
        tl = self._batbaothu_thietlap
        if chuanhoaten(ten if ten is not None else self.moitruong.get_tendoituong(diachi)) != chuanhoaten(tl["ten"]):
            return False
        if tl["captu"] or tl["capden"]:
            khop = MAUCAPTRONGTEN.search(self.moitruong._get_tenthucte(diachi) or "")
            if khop:
                cap = int(khop.group(1))
                if cap < tl["captu"] or (tl["capden"] and cap > tl["capden"]):
                    return False
            elif not self._batbaothu["dabaocap"]:
                self._batbaothu["dabaocap"] = True
                self._logbbt(f"Không đọc được cấp của {tl['ten']} trong tên gốc \"{self.moitruong._get_tenthucte(diachi)}\": bắt không lọc cấp")
        return True

    def get_trangthaibatbaothu(self):
        s = self._batbaothu
        if s:
            return f"Bắt bảo thú (giữ {s['sogiu']}/{self._batbaothu_thietlap['soluong']}, phóng sinh {s['sophongsinh']}): {s['trangthai']}"
        return self._ketquabatbaothu or ""

    def _motathietlapbatbaothu(self):
        tl = self._batbaothu_thietlap
        cap = ""
        if tl["captu"] or tl["capden"]:
            cap = f" cấp {tl['captu'] or 1}-{tl['capden']}" if tl["capden"] else f" cấp từ {tl['captu']}"
        nguongs = [f"{ten} >= {tl['tuchat'][k]}" for k, ten in TUCHATBAOTHUs if tl["tuchat"][k]]
        dieukien = (" hoặc " if tl["is_batky"] else " và ").join(nguongs) if nguongs else "không lọc tư chất"
        return f"\"{tl['ten']}\"{cap}, bắt khi máu < {tl['nguongmau']}%, giữ {tl['soluong']} con ({dieukien})"

    def _logbbt(self, noidung):
        self.moitruong._inlog(f"[BẮT BẢO THÚ] {noidung}")

    def _doituychonbatbaothu(self, thuoctinh, giatri, ten):
        s = self._batbaothu
        if s is not None and getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self._logbbt(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng bắt bảo thú thì trả lại)")

    def _ketthucbatbaothu(self, thongbao):
        s = self._batbaothu
        self._batbaothu = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if s:
            thongbao += f" (giữ {s['sogiu']}, phóng sinh {s['sophongsinh']})"
        self._logbbt(thongbao)
        self._ketquabatbaothu = f"{time.strftime('%H:%M')} {thongbao}"
        phatam("Kết thúc bắt bảo thú")

    # --- Xét tư chất ---------------------------------------------------------------------------------------------------------------
    def _is_tuchatdat(self, bt):
        tl = self._batbaothu_thietlap
        nguongs = [(k, n) for k, n in tl["tuchat"].items() if n]
        if not nguongs:
            return True
        dats = [bt.get(k, 0) >= n for k, n in nguongs]
        return any(dats) if tl["is_batky"] else all(dats)

    def _xetbaothumoi(self, s):
        # Con mới (id chưa có lúc bắt đầu): đạt thì giữ, không đạt thì phóng sinh (nếu bật). -> True khi vừa xử lý / đang chờ tư chất
        moitruong = self.moitruong
        ds = moitruong.get_danhsachbaothugiangho()
        if ds is None:
            return False
        if s["idcu"] is None:
            s["idcu"] = {bt["id"] for bt in ds}
            cos = ", ".join("{} cấp {}".format(bt["ten"], bt["cap"]) for bt in ds) or "(không có)"
            self._logbbt(f"Bảo thú đang có (không bao giờ phóng sinh): {cos}")
            return False
        for bt in ds:
            if bt["id"] in s["idcu"]:
                continue
            luc = s["thaymoi"].setdefault(bt["id"], time.time())
            s["solanbatkhongra"] = 0
            if not any(bt[k] for k, _ in TUCHATBAOTHUs):
                if time.time() - luc < THOIGIANCHOTUCHATBAOTHU:
                    s["trangthai"] = f"bắt được {bt['ten']}, chờ đọc tư chất"
                    return True
                s["idcu"].add(bt["id"])
                s["sogiu"] += 1
                self._logbbt(f"Bắt được {bt['ten']} cấp {bt['cap']} nhưng {THOIGIANCHOTUCHATBAOTHU:.0f}s chưa đọc được tư chất: giữ lại")
                continue
            s["idcu"].add(bt["id"])
            mota = f"{bt['ten']} cấp {bt['cap']} (Khí Huyết {bt['khihuyet']}; {motatuchat(bt)})"
            if self._is_tuchatdat(bt):
                s["sogiu"] += 1
                self._logbbt(f"Bắt được {mota}: ĐẠT, giữ lại ({s['sogiu']}/{self._batbaothu_thietlap['soluong']})")
                phatam("Bắt được bảo thú đẹp")
            elif self._batbaothu_thietlap["is_phongsinh"]:
                moitruong.action_phongsinhbaothu(bt["id"])
                s["sophongsinh"] += 1
                self._logbbt(f"Bắt được {mota}: không đạt, phóng sinh (pet {bt['id']:x}# free)")
                return True
            else:
                s["sogiu"] += 1
                self._logbbt(f"Bắt được {mota}: không đạt, tắt phóng sinh nên vẫn giữ")
        return False

    # --- Tìm quái ------------------------------------------------------------------------------------------------------------------
    def _timquaibatbaothu(self):
        # Quái cần bắt (_is_quaicanbat) gần nhất trong KHOANGCACHTHAYBATBAOTHU ô, còn sống, đánh được, không phải bảo thú của người khác
        moitruong = self.moitruong
        tot, khoangcachtot = None, None
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi) or not moitruong.get_is_cothetancong(diachi):
                continue
            if not self._is_quaicanbat(diachi) or self._is_baothukhongphainpc(diachi):
                continue
            khoangcach = moitruong.get_khoangcach(diachi)
            if khoangcach <= KHOANGCACHTHAYBATBAOTHU and (khoangcachtot is None or khoangcach < khoangcachtot):
                tot, khoangcachtot = diachi, khoangcach
        return tot

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulybatbaothu(self):
        # Gọi thay lộ trình điểm đánh khi đang bắt bảo thú -> yêu cầu di chuyển hoặc None
        s = self._batbaothu
        moitruong = self.moitruong
        tl = self._batbaothu_thietlap
        s["lucxuly"] = time.time()
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logbbt(s["trangthai"])
        # Còn Tự Động Công Kích từ lúc đánh giảm máu thì ngắt (dùng chung với sư môn)
        self._xulyngatdanhsumon()
        if self._xetbaothumoi(s):
            return None
        if s["sogiu"] >= tl["soluong"]:
            self._ketthucbatbaothu(f"Đã bắt đủ {tl['soluong']} con {tl['ten']} đạt tư chất")
            return None
        if s["solanbatkhongra"] >= SOLANBATKHONGRATOIDA:
            self._ketthucbatbaothu(f"Bắt {SOLANBATKHONGRATOIDA} lần không ra con mới (ô bảo thú đầy / quái không bắt được?)")
            return None
        if not self._demvatpham(DAYCANKHON):
            self._ketthucbatbaothu(f"Hết {DAYCANKHON}")
            return None
        diachi = None
        if not (moitruong.get_is_nhanvatdachet() or moitruong.get_is_dangvankhi() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0):
            diachi = self._timquaibatbaothu()
        if not diachi:
            # Không có con cần bắt quanh đây: farm như thường (lộ trình điểm đánh / chọn mục tiêu của nhân vật)
            s["chedo"] = "farm"
            s["trangthai"] = f"farm, chờ {tl['ten']} đúng cấp xuất hiện"
            return None
        s["chedo"] = "bat"
        idbando = moitruong.get_idbandohientai()
        nhan = f"bắt {tl['ten']}"
        if moitruong.get_khoangcach(diachi) > KHOANGCACHBATBAOTHU:
            x, y = moitruong.get_toado(diachi)
            s["trangthai"] = f"tới {tl['ten']} để bắt"
            return self._dentoi(s, idbando, x, y, nhan)
        iddt = moitruong.get_iddoituong(diachi)
        cho = s.setdefault("chogiammau", {})
        if self._danhgiammau(s, {"quai": tl["ten"], "nhanlog": "BẮT BẢO THÚ", "is_satthuonggannhat": True}, diachi, solanbattruoc = 0,
                             nguongdung = tl["nguongmau"]):
            # Đang đánh: đồng hồ chờ tính lại từ cú đánh này
            cho.pop(iddt, None)
            return None
        if s.get("lydokhongdanh") == "xa":
            # Cần đánh thường ("kill") mà chưa kề: "kill" không kéo nhân vật đi, chạy tới ô kề trước; đồng hồ chờ tính lại khi tới nơi
            cho.pop(iddt, None)
            x, y = moitruong.get_toado(diachi)
            s["trangthai"] = f"tới sát {tl['ten']} để đánh giảm máu"
            return self._dentoi(s, idbando, x, y, nhan, khoangcach = 0.)
        mau = moitruong.get_phantramsinhlucconlai(diachi)
        if mau >= tl["nguongmau"]:
            # _danhgiammau không đánh: MỌI cách đánh (chiêu, đánh thường) đều có thể giết (sức đã đo x1.5 làm máu dưới NGUONGMAUANTOAN%)
            # thì bắt luôn; còn lại (chiêu chưa tới lượt...) thì chờ, quá THOIGIANCHODANHGIAMMAUTOIDA giây không đánh được mới bắt luôn
            if s.get("lydokhongdanh") != "nguyhiem" and time.time() - cho.setdefault(iddt, time.time()) < THOIGIANCHODANHGIAMMAUTOIDA:
                s["trangthai"] = f"chờ đánh {tl['ten']} xuống dưới {tl['nguongmau']}% máu ({mau}%)"
                return None
            if iddt not in s.setdefault("dabaobatluon", set()):
                s["dabaobatluon"].add(iddt)
                self._logbbt(f"{tl['ten']} còn {mau}% máu mà không đánh thêm được "
                             f"({'cú đánh kế có thể làm chết' if s.get('lydokhongdanh') == 'nguyhiem' else 'quá ' + str(int(THOIGIANCHODANHGIAMMAUTOIDA)) + 's không đánh được'}): bắt luôn")
        # Tỉ lệ bắt thấp: cứ dùng tới khi được, cách nhau ít nhất GIANCACHBATBAOTHU giây
        if time.time() - s["lucbat"] >= GIANCACHBATBAOTHU:
            s["solanbat"][iddt] = s["solanbat"].get(iddt, 0) + 1
            s["solanbatkhongra"] += 1
            moitruong.action_ngatdichuyen()
            moitruong.action_thucthicaulenh(LENHBATBAOTHU.format(iddt))
            s["lucbat"] = time.time()
        s["trangthai"] = f"đang bắt {tl['ten']}"
        return None
