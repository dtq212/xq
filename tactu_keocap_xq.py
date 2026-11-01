# Kéo cấp acc gà (acc clone) để tăng kỹ năng bang: thành viên bang lên cấp thì kỹ năng bang phái nhận kinh nghiệm. Bật từ giao diện ở acc
# chính (nhân vật đang chọn), giao diện gửi luôn lệnh bật vai acc gà cho các cửa sổ cùng máy được chọn. Acc chính điều phối, báo giai đoạn
# qua shared_data ("_keocap"), acc gà đọc rồi tự làm phần của mình. Quy trình (dò theo log [LỆNH GAME] người dùng làm tay 2026-11-01):
#   tanthu  (acc gà): Tân Thủ Thôn (95, 123) Thần Tiên Gia Gia: "1. Sứ Mệnh Đưa Thư" (tallk welcome.1) -> "1. Hoàn thành nhiệm vụ"
#           (welcome.2); look lại -> "6. Nhập Code Tân Thủ" (welcome.11747) -> welcome.13747 -> "codett + welcome2d". Thưởng: lên cấp 8,
#           pháp bảo Cửu Long Thần Hỏa Trảo, đeo vai Hoàng Sa Chi Tâm, bảo thú Thủy Bình, 3 Chiến Quốc Lệnh x3 (cách dùng từng món xem
#           VATPHAMTANTHUs; Chiến Quốc Lệnh x3 "use !", "use" chỉ hiện hộp hỏi đồng ý)
#   taphop  : mọi người về Tân Thủ Thôn (143, 143); acc chính lập nhóm, mời acc gà ("team + <ID>"), mời vào bang ("org invite <ID>", log
#           acc 192 mời 187); acc gà đồng ý bằng lệnh của hộp Yes/No ("team + <ID chính>", "org join <ID chính>")
#   bai     : acc chính tới bãi (Hồi Thành Phù / phù Tân Thủ Tiên Cô / chạy bộ theo Đi tới bản đồ) đánh theo lộ trình điểm đánh của bản đồ (chưa
#           có mẫu thì tự đề xuất / dò); acc gà bật Theo sau acc chính (tự tìm đường / phù sang bản đồ khác). Cấp thấp nhất của acc gà đủ
#           cấp đích thì sang bãi kế: Ba Khâu -> 10, Thuý Hoa Sơn -> 20, Cự Lộc -> 30, Ranh Giới Đầm Lầy -> 35
#   phongyeu: Phong Yêu Kính (tactu_langlyson_xq) tới khi mọi acc gà cấp CAPKETTHUC: người give (lập nhóm, đốt đồ) là 1 ACC GÀ có đồ Lam
#           Kim (quái theo cấp người mở thì acc gà mới có kinh nghiệm), acc chính là thành viên dò bản đồ đánh quái. Trong phó bản acc gà
#           đứng yên cạnh Truyền Tống Thỏ Yêu; người give hỏi Thỏ Yêu số quái mỗi GIANCACHHOITHOYEU giây, đủ TILERAPHONGYEU thì ra mở vòng
#           mới. Bản đồ mượn ID Tây Thành (khó đi) thì ra ngay mở bản đồ khác
#           Đồ Lam Kim để ở acc chính: ngoài phó bản, acc gà nhận đồ (người give, không thì ID nhỏ nhất) hết đồ thì acc chính đứng yên, acc
#           gà đó tới cạnh, acc chính "give <ID acc gà> <đồ>#1 ... $0" (chuyển thẳng, không cần đồng ý, như giao đồ) mọi món đủ cấp acc gà
#   acc phụ (máy khác nối LAN, bật "Làm acc phụ"): tự nhận acc chính đang kéo cấp thấy qua LAN, chỉ vào Phong Yêu Kính làm thành viên dò
#           đánh quái như acc chính; giai đoạn khác để bot chạy như thường
# Acc gà Theo sau tự phù / chạy sang bản đồ của acc chính; không đủ tiền Hồi Thành Phù mà chạy bộ xa thì bộ tìm đường chung
# (_lapbuocditoibando) hồi môn phái về Tân Thủ Thôn (chưa vào môn phái) rồi phù tiếp.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._keocap...) khởi tạo trong TacTu.__init__
import math
import time
import unicodedata

from hangso_xq import *
from tienich_xq import phatam, taicauhinhphongyeu
from giaodo_xq import taolenhgiao
from tactu_langlyson_xq import CAPDOLAMKIMTOITHIEU

BANDO_BAKHAU = 162
BANDO_THUYHOASON_KC = 82
BANDO_TAYTHANH = 521
NPCTHANTIENGIAGIA = ("Thần Tiên Gia Gia", 95, 123)
DIEMTAPHOPKEOCAP = (143, 143)
# Đuôi lệnh của từng menu lần lượt (so với lệnh lựa chọn "tallk <id NPC># <đuôi>", không theo số thứ tự vì menu đổi theo nhiệm vụ)
MENUNHIEMVUTANTHU = ("welcome.1", "welcome.2")
MENUCODETANTHU = ("welcome.11747", "welcome.13747")
LENHCODETANTHU = "codett + welcome2d"
# Thưởng code tân thủ dùng ngay: (các cách viết dấu, cách dùng); tên ô hành trang tối đa 31 byte nên so đầu tên. "use !" không ăn với
# cả 3 món (acc 282-291 2026-11-01), người dùng dặn chỉ gửi "use2 <id>#" (lệnh nút Xác Nhận), không cần "use" trước:
#   "use2"  : pháp bảo / đeo vai, "use2 <id>#"
#   "baothu": bảo thú vật phẩm, dùng không mất khỏi túi: đặt vào ô mở cuối cùng để phần tự triệu hồi bảo thú vật phẩm lo (cũng "use2",
#             VATPHAMDUNGUSE2s; gọi lại khi bảo thú mất)
VATPHAMTANTHUs = ((("Cửu Long Thần Hỏa Trảo", "Cửu Long Thần Hoả Trảo"), "use2"), (("Hoàng Sa Chi Tâm",), "use2"), (THUYBINHs, "baothu"))
# Chỉ dùng đúng món "Chiến Quốc Lệnh x3", không đụng "Chiến Quốc Lệnh" thường (người dùng dặn)
CHIENQUOCLENHX3 = "Chiến Quốc Lệnh x3"
# Tên ô hành trang dài từ chừng này byte (UTF-8) trở lên là có thể đã bị cắt (ô chỉ 31 byte)
SOBYTETENBICAT = 30
SOLANDUNGVATPHAMTANTHU = 4
GIANCACHDOCVATPHAMSOTKC = 10.
SOLANDUNGCHIENQUOCLENH = 5
# Bật giữa chừng ngoài phó bản: mời bang lại tối đa chừng này lần mỗi acc gà chưa ghi nhận đã vào bang (đã ở bang thì lệnh vô hại)
SOLANMOIBANGGIUACHUNG = 3
GIANCACHDUNGVATPHAMKC = 1.5
# Gửi code xong chờ thưởng (lên cấp 8 / có món thưởng trong túi) tối đa chừng này giây rồi mới dùng đồ
THOIGIANCHOTHUONGCODE = 15.
# (bản đồ, cấp đích): acc gà thấp nhất chưa tới cấp đích thì acc chính đánh ở bản đồ đó
BAIKEOCAPs = ((BANDO_BAKHAU, 10), (BANDO_THUYHOASON_KC, 20), (BANDO_CULOC, 30), (BANDO_RANHGIOIDAMLAY, 35))
CAPKETTHUCKEOCAP = 60
TILERAPHONGYEU = 0.85
GIANCACHHOITHOYEU = 60.
KHOANGCACHNOICHUYENKC = 3.
THOIGIANCHOMENUKC = 3.
SOLANTHUMENUKC = 3
GIANCACHMOINHOMKC = 5.
GIANCACHMOIBANGKC = 15.
# Tập hợp: quá chừng này giây acc gà chưa đồng ý vào bang thì vẫn đi bãi (báo log, vẫn mời tiếp lúc đứng ở Tân Thủ Thôn)
THOIGIANCHOBANGKC = 120.
# Tới bãi chờ acc gà theo sang tối đa chừng này giây rồi mới đánh (có mặt mới được chia kinh nghiệm)
THOIGIANCHOGATOIBAI = 90.
# Phong Yêu Kính: người give tắt Phong Yêu Kính chừng này giây (hết đồ) thì acc chính chọn acc gà khác; ai tắt thì chừng này giây sau bật lại
THOIGIANDOINGUOIGIVE = 10.
THOIGIANBATLAIPYKC = 15.
GIANCACHDOCDOLAMKIMKC = 20.
THOIGIANBAOXONGKC = 20.
# Acc chính đưa đồ Lam Kim: đọc túi mình mỗi chừng này giây; give xong chừng này giây mới xét / gửi lại, tối đa SOLANGIAODOKC lần không giảm
GIANCACHDOCDOCHINHKC = 5.
GIANCACHGIAODOKC = 4.
SOLANGIAODOKC = 3
KHOANGCACHGIAODOKC = 3.
# Acc gà đang chờ nhận đồ đọc lại túi mỗi chừng này giây
GIANCACHDOCDONHANKC = 3.
# Đưa đồ xong chờ acc gà báo đã có đồ tối đa chừng này giây
THOIGIANCHONHANDOKC = 30.
GIANCACHROINHOMKC = 5.
TENGIAIDOANKEOCAP = {"tanthu": "nhận thưởng tân thủ", "taphop": "tập hợp Tân Thủ Thôn", "phongyeu": "Phong Yêu Kính", "xuatsu": "xuất sư",
                     "xong": "xong"}
# Nhận đồ đệ (tuỳ chọn): trước khi lập nhóm / mời bang, acc chính lập nhóm riêng với acc gà đồ đệ, Mạnh Tử "2. Ta đem đệ tử đến làm lễ bái
# sư" -> "1. Xác nhận", acc gà "1. Xác nhận" (tallk 17e5# welcome.13); mọi acc gà cấp 60 thì về Mạnh Tử "3. ... lễ xuất sư" như vậy.
# Nhãn lựa chọn không có trong bộ nhớ (chỉ có lệnh), chưa dò được đuôi lệnh của acc chính nên chọn theo thứ tự (0 = lựa chọn 1)
NPCMANHTU = ("Mạnh Tử", 136, 143)
CHISOBAISU = 1
CHISOXUATSU = 2
KHOANGCACHDODEMANHTU = 5.
# Chọn xong chờ acc gà đồ đệ báo đã xác nhận tối đa chừng này giây rồi làm lại, tối đa SOLANSUPHUKC lần
THOIGIANCHODODEKC = 20.
SOLANSUPHUKC = 3


def _chuanhoa(ten):
    return unicodedata.normalize("NFC", ten or "").strip()


class TacTuKeoCap:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_keocap(self, vaitro, idchinh = 0, idgas = (), dabang = False, xongtanthu = False, tuychoncu = None, muctieutheosaucu = None,
                      iddode = 0, dabaisu = False, daxuatsu = False, **_):
        # iddode (acc chính): ID acc gà nhận làm đồ đệ (0 = không); dabaisu / daxuatsu: đã xong (mở lại bot giữa chừng)
        # vaitro "chinh": điều phối, idgas là ID các acc gà; "ga": idchinh là ID acc chính; "phu": acc phụ (idchinh 0 = tự tìm qua LAN)
        if self._keocap or vaitro not in ("chinh", "ga", "phu"):
            return
        self._keocap = {"vaitro": vaitro, "idchinh": int(idchinh or 0), "idgas": [int(i) for i in idgas if int(i)], "batdau": time.time(),
                        "giaidoan": "taphop" if vaitro == "chinh" else ("taphop" if xongtanthu else "tanthu"), "trangthai": "bắt đầu",
                        "tanthu": "nhiemvu", "dabang": bool(dabang), "xongtanthu": bool(xongtanthu), "hoithoai": None, "lucmoi": {},
                        "lucmoibang": {}, "idgive": 0, "luctatgive": 0., "lucbatpy": 0., "codolamkim": None, "lucdocdo": 0., "dadescpy": {}}
        self._keocap.update(iddode = int(iddode or 0), dabaisu = bool(dabaisu), daxuatsu = bool(daxuatsu))
        # Mở lại bot giữa chừng: ô gốc của người dùng lưu từ lần trước (get_keocapluu)
        if tuychoncu:
            self._keocap["tuychoncu"] = dict(tuychoncu)
        if muctieutheosaucu:
            self._keocap["muctieutheosaucu"] = tuple(muctieutheosaucu)
        elif vaitro == "ga" and self._idmuctieutheosau == self._keocap["idchinh"]:
            # Còn Theo sau acc chính sót từ lần kéo cấp trước (bản cũ không lưu ô gốc): coi như gốc là không theo sau ai
            self._keocap.setdefault("tuychoncu", {})["_is_tudongtheosau"] = False
            self._keocap["muctieutheosaucu"] = (0, "")
        capdo = self.moitruong.get_capdonhanvat() or 0
        if vaitro == "ga" and not xongtanthu and capdo >= 8:
            # Bật giữa chừng: đã có cấp 8 = đã nhập code, bỏ nói chuyện Thần Tiên Gia Gia, chỉ dùng thưởng còn trong túi (nếu có)
            self._keocap["tanthu"] = "vatpham"
            self._logkc(f"Đã cấp {capdo}: bỏ bước trả nhiệm vụ / nhập code, chỉ dùng thưởng tân thủ còn trong túi")
        mota = {"chinh": "acc chính, acc gà " + ", ".join(map(str, self._keocap["idgas"])), "ga": f"acc gà của {idchinh}",
                "phu": f"acc phụ Phong Yêu Kính của {idchinh or 'acc chính tự tìm qua LAN'}"}[vaitro]
        self._logkc(f"Bắt đầu kéo cấp ({mota})")
        phatam({"chinh": "Bắt đầu kéo cấp acc gà", "ga": "Bắt đầu kéo cấp, vai acc gà", "phu": "Bắt đầu kéo cấp, vai acc phụ"}[vaitro])

    def huy_keocap(self):
        if self._keocap:
            self._ketthuckeocap("Đã dừng (bấm tay)")

    def _ketthuckeocap(self, thongbao):
        s = self._keocap
        self._keocap = None
        for thuoctinh, giatri in (s.get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if "muctieutheosaucu" in s:
            self.thietlap_muctieutheosau(*s["muctieutheosaucu"])
        if self._langlyson and self._langlyson["phoban"] == "phongyeukinh":
            self.huy_langlyson()
        self.moitruong._inlog(f"[KÉO CẤP] {thongbao}")
        self._ketquakeocap = f"{time.strftime('%H:%M')} Kéo cấp: {thongbao}"
        phatam("Kết thúc kéo cấp")

    def get_is_dangkeocap(self):
        return bool(self._keocap)

    def get_trangthaikeocap(self):
        s = self._keocap
        if not s:
            return self._ketquakeocap or ""
        vai = {"chinh": "acc chính", "ga": "acc gà", "phu": "acc phụ"}[s["vaitro"]]
        return f"Kéo cấp ({vai}, {self._tengiaidoan(s['giaidoan'])}): {s['trangthai']}"

    def get_keocapshare(self):
        # Báo qua shared_data cho cửa sổ khác cùng máy
        s = self._keocap
        if not s:
            return None
        return {"vaitro": s["vaitro"], "idchinh": s["idchinh"], "idgas": s["idgas"], "giaidoan": s["giaidoan"], "idgive": s["idgive"],
                "capdo": self.moitruong.get_capdonhanvat() or 0, "xongtanthu": s["xongtanthu"], "dabang": s["dabang"],
                "codolamkim": s["codolamkim"], "nhompy": s.get("nhompy") or [], "chuyendo": s.get("chuyendo") or 0,
                "iddode": s["iddode"], "dabaisu": s["dabaisu"], "daxuatsu": s["daxuatsu"]}

    def get_keocapluu(self):
        # Lưu thiết lập: dis / mở lại bot thì tự bật tiếp đúng vai
        s = self._keocap
        if not s:
            return None
        # Lưu cả ô gốc của người dùng (tuychoncu / muctieutheosaucu): không lưu thì mở lại bot coi giá trị kéo cấp đang đặt (Theo sau acc
        # chính) là gốc, xong kéo cấp "trả lại" đúng Theo sau đó, acc mới vào cùng cửa sổ tự chạy theo acc chính (gacon7_3 2026-11-01)
        luu = {"vaitro": s["vaitro"], "idchinh": s["idchinh"], "idgas": s["idgas"], "dabang": s["dabang"], "xongtanthu": s["xongtanthu"],
               "tuychoncu": dict(s.get("tuychoncu") or {}), "iddode": s["iddode"], "dabaisu": s["dabaisu"], "daxuatsu": s["daxuatsu"]}
        if "muctieutheosaucu" in s:
            luu["muctieutheosaucu"] = tuple(s["muctieutheosaucu"])
        return luu

    @staticmethod
    def _tengiaidoan(giaidoan):
        if isinstance(giaidoan, str) and giaidoan.startswith("bai:"):
            return f"bãi {laytenbando(int(giaidoan[4:]))}"
        return TENGIAIDOANKEOCAP.get(giaidoan, giaidoan)

    def _logkc(self, noidung):
        self.moitruong._inlog(f"[KÉO CẤP] {noidung}")

    def _sanggiaidoankc(self, s, giaidoan):
        if s["giaidoan"] == giaidoan:
            return
        self._logkc(f"Sang giai đoạn: {self._tengiaidoan(giaidoan)} (trước: {self._tengiaidoan(s['giaidoan'])})")
        phatam(f"Kéo cấp: {self._tengiaidoan(giaidoan)}")
        s["giaidoan"] = giaidoan
        s["hoithoai"] = None

    def _datkc(self, s, thuoctinh, giatri, ten):
        # Đổi ô của người dùng cho kéo cấp, dừng thì trả lại
        if getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self._logkc(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng kéo cấp thì trả lại)")

    def _laycuasokeocap(self):
        # {ID người chơi: info} các cửa sổ khác đang kéo cấp, còn cập nhật
        ketqua = {}
        if self.shared_data is None:
            return ketqua
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return ketqua
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict) or not isinstance(info.get("_keocap"), dict):
                continue
            if time.time() - info.get("thoidiemcapnhat", 0.) > 5. or not info.get("idnguoichoi"):
                continue
            ketqua[info["idnguoichoi"]] = info
        return ketqua

    # --- Vòng chính (gọi đầu action_tudongdichuyentudo) --------------------------------------------------------------------------------
    def _xulykeocap(self):
        # -> yêu cầu di chuyển / None (tự lo, đứng yên) hoặc False (để phần sau lo: lộ trình điểm đánh, Theo sau, Phong Yêu Kính)
        s = self._keocap
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logkc(s["trangthai"])
        if s["vaitro"] == "chinh":
            return self._xulykeocapchinh(s)
        if s["vaitro"] == "phu":
            return self._xulykeocapphu(s)
        return self._xulykeocapga(s)

    def _is_dangban(self):
        moitruong = self.moitruong
        return moitruong.get_is_nhanvatdachet() or moitruong.get_is_dangvankhi() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0 \
            or time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.

    def _ditoikc(self, s, idbando, toado, nhan):
        # Tới (toado) ở bản đồ idbando: chưa tới bản đồ thì theo bước Đi tới bản đồ (Hồi Thành Phù / phù / chạy bộ). -> yêu cầu / None
        moitruong = self.moitruong
        if moitruong.get_idbandohientai() != idbando:
            buoc = self._lapbuocditoibando(idbando, is_hoithanhphu = True, toadodich = toado, is_roiphoban = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                s["trangthai"] = f"{nhan}: {buoc['mota']}"
                return None
            s["trangthai"] = f"{nhan}: {buoc['mota']}"
            return self._thuchienbuocditoibando(buoc, idbando, toado, f"[KÉO CẤP] {nhan}")
        if toado and moitruong.get_khoangcachdiem(*toado) > 3.:
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (toado[0], toado[1], idbando), "khoangcachtoida": 1.}
        return None

    # --- Acc chính ----------------------------------------------------------------------------------------------------------------------
    def _laygaonline(self, s):
        # {ID acc gà: info _keocap} của acc gà trong danh sách đang chạy kéo cấp (cùng máy)
        cuasos = self._laycuasokeocap()
        return {i: cuasos[i] for i in s["idgas"] if i in cuasos and cuasos[i]["_keocap"].get("vaitro") == "ga"}

    def _xulykeocapchinh(self, s):
        moitruong = self.moitruong
        now = time.time()
        # Acc chính tự đi bãi / lộ trình điểm đánh: bật "Theo sau" thì bot bỏ lộ trình, đứng im (187 lưu sẵn Theo sau, 2026-11-01)
        if self._is_tudongtheosau:
            self._datkc(s, "_is_tudongtheosau", False, "Theo sau")
        gas = self._laygaonline(s)
        if not gas:
            s["trangthai"] = "chờ cửa sổ acc gà bật kéo cấp"
            return None
        caps ={i: info["_keocap"].get("capdo") or 0 for i, info in gas.items()}
        capthap = min(caps.values())
        if (capthap >= CAPKETTHUCKEOCAP or s["giaidoan"] in ("xuatsu", "xong")) and s["iddode"] and s["dabaisu"] and not s["daxuatsu"]:
            # Mọi acc gà cấp 60: dắt đồ đệ về Mạnh Tử xuất sư rồi mới báo xong
            self._sanggiaidoankc(s, "xuatsu")
            return self._buocsuphuchinh(s, gas, "xuatsu")
        if capthap >= CAPKETTHUCKEOCAP or s["giaidoan"] == "xong":
            # Báo "xong" thêm THOIGIANBAOXONGKC giây cho acc gà kịp đọc rồi tự dừng (Phong Yêu Kính của chúng)
            self._sanggiaidoankc(s, "xong")
            if self._langlyson:
                self.huy_langlyson()
            s.setdefault("lucxong", now)
            s["trangthai"] = f"mọi acc gà đã tới cấp {CAPKETTHUCKEOCAP}, báo acc gà dừng"
            if now - s["lucxong"] > THOIGIANBAOXONGKC:
                self._ketthuckeocap(f"✅ Mọi acc gà đã tới cấp {CAPKETTHUCKEOCAP}")
            return None
        if s["iddode"] and not s["dabaisu"] and all(info["_keocap"].get("xongtanthu") for info in gas.values()):
            # Nhận đồ đệ: bái sư trước khi lập nhóm cả đám / mời bang / đi bãi
            return self._buocsuphuchinh(s, gas, "baisu")
        if s["giaidoan"] == "taphop" and capthap >= BAIKEOCAPs[0][1] and all(info["_keocap"].get("xongtanthu") for info in gas.values()):
            # Bật giữa chừng (acc gà đã qua bãi đầu): không về Tân Thủ Thôn tập hợp, đi thẳng bãi theo cấp; mời nhóm / bang ở bãi
            self._logkc(f"Acc gà thấp nhất đã cấp {capthap}: bỏ tập hợp, đi thẳng bãi theo cấp")
            s["giaidoan"] = ""
        if s["giaidoan"] == "taphop":
            return self._buoctaphopchinh(s, gas)
        if capthap >= BAIKEOCAPs[-1][1]:
            self._sanggiaidoankc(s, "phongyeu")
            return self._buocphongyeuchinh(s, gas)
        idbai = next(b for b, cap in BAIKEOCAPs if capthap < cap)
        self._sanggiaidoankc(s, f"bai:{idbai}")
        if self._langlyson:
            self.huy_langlyson()
        if self._is_dangban():
            return None
        self._moinhomkc(s, gas)
        self._moibangkc(s, gas, SOLANMOIBANGGIUACHUNG)
        tenbai = laytenbando(idbai)
        captoi = dict(BAIKEOCAPs)[idbai]
        if moitruong.get_idbandohientai() != idbai:
            s.pop("lotrinhbando", None)
            s.pop("luctoibai", None)
            return self._ditoikc(s, idbai, None, f"tới {tenbai} (acc gà thấp nhất cấp {capthap}, cần {captoi})")
        s.setdefault("luctoibai", now)
        chuatoi = [info.get("tennhanvat") or str(i) for i, info in gas.items() if info.get("tenbando") != idbai]
        if chuatoi and now - s["luctoibai"] < THOIGIANCHOGATOIBAI:
            s["trangthai"] = f"{tenbai}: chờ acc gà theo sang ({', '.join(chuatoi)}, còn {int(THOIGIANCHOGATOIBAI - (now - s['luctoibai']))}s)"
            return None
        if s.get("lotrinhbando") != idbai:
            s["lotrinhbando"] = idbai
            if not self.tuchon_lotrinhmau(idbai):
                # dexuat_lotrinhmau đủ vị trí quái thì chỉ lưu mẫu, không nạp (mẫu dò thì nạp luôn): nạp lại mẫu vừa lưu
                is_dexuat = self.dexuat_lotrinhmau()
                is_nap = is_dexuat and self.tuchon_lotrinhmau(idbai)
                self._logkc(f"{tenbai} chưa có lộ trình mẫu: tự đề xuất " + ("và nạp" if is_nap else "được" if is_dexuat else "không được"))
            self._datkc(s, "_is_tudongdichuyendiemdanhxungquanh", True, "Tự động di chuyển điểm đánh xung quanh")
        s["trangthai"] = f"{tenbai}: đánh quái kéo acc gà tới cấp {captoi} (" + ", ".join(
            f"{gas[i].get('tennhanvat') or i} {c}" for i, c in sorted(caps.items(), key = lambda x: x[1])) + ")"
        return False

    def _moinhomkc(self, s, gas):
        # Acc chính làm trưởng nhóm, mời acc gà chưa ở trong nhóm (mỗi người mỗi GIANCACHMOINHOMKC giây)
        moitruong = self.moitruong
        now = time.time()
        idtoi = moitruong.get_idnguoichoi()
        if moitruong.get_is_dangnamtrongnhom() and not moitruong.get_is_truongnhom():
            # Đang là thành viên nhóm người khác (vd nhóm Phong Yêu Kính cũ): rời để tự lập nhóm
            if now - s.get("lucroinhom", 0.) > GIANCACHROINHOMKC:
                s["lucroinhom"] = now
                self._logkc("Đang ở nhóm người khác: rời để lập nhóm kéo cấp")
                moitruong.action_thoatkhoinhom()
            return
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if moitruong.get_is_dangnamtrongnhom() else set()
        for idga in gas:
            if idga in trongnhoms or now - s["lucmoi"].get(idga, 0.) < GIANCACHMOINHOMKC:
                continue
            s["lucmoi"][idga] = now
            if not moitruong.get_is_dangnamtrongnhom():
                # Chưa có nhóm: lập nhóm 1 người trước (như Phong Yêu Kính), lượt sau mới mời
                moitruong.action_thucthicaulenh(f"team + {idtoi}")
                return
            self._logkc(f"Mời {gas[idga].get('tennhanvat') or idga} vào nhóm")
            moitruong.action_moihoacxinvaonhom(idga)
            return

    def _buocsuphuchinh(self, s, gas, loai):
        # loai "baisu" / "xuatsu": về Tân Thủ Thôn, nhóm với acc gà đồ đệ (bái sư: nhóm riêng 2 người), đồ đệ đứng gần Mạnh Tử thì chọn
        # "2. ... bái sư" / "3. ... xuất sư" -> lựa chọn đầu ("1. Xác nhận") rồi chờ đồ đệ báo đã xác nhận (_xacnhansuphuga).
        # Hết SOLANSUPHUKC lần mà đồ đệ chưa báo thì coi như xong (báo log, làm tay giúp) để không kẹt cả kéo cấp
        moitruong = self.moitruong
        now = time.time()
        iddode = s["iddode"]
        co = "dabaisu" if loai == "baisu" else "daxuatsu"
        ten = "bái sư" if loai == "baisu" else "xuất sư"
        info = gas.get(iddode)
        if not info:
            s["trangthai"] = f"{ten}: chờ acc gà đồ đệ (ID {iddode}) online, bật kéo cấp"
            return None
        tendd = info.get("tennhanvat") or str(iddode)
        sp = s.setdefault("suphu", {"loai": loai, "buoc": "menu", "solan": 0, "luc": 0.})
        if sp["loai"] != loai:
            sp.update(loai = loai, buoc = "menu", solan = 0, luc = 0.)
        if info["_keocap"].get(co):
            s[co] = True
            s.pop("suphu", None)
            self._logkc(f"✅ {tendd} đã xác nhận {ten}")
            phatam(f"Xong {ten}")
            return None
        if self._langlyson:
            self.huy_langlyson()
        if self._is_dangban():
            return None
        _, xnpc, ynpc = NPCMANHTU
        yeucau = self._ditoikc(s, BANDO_TANTHUTHON, (xnpc, ynpc), ten)
        if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            return yeucau
        self._moinhomkc(s, {iddode: info})
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if moitruong.get_is_dangnamtrongnhom() else set()
        if iddode not in trongnhoms:
            s["trangthai"] = f"{ten}: mời {tendd} vào nhóm"
            return yeucau
        if info.get("tenbando") != BANDO_TANTHUTHON or not info.get("x") \
                or math.dist((info["x"], info["y"]), (xnpc, ynpc)) > KHOANGCACHDODEMANHTU:
            s["trangthai"] = f"{ten}: chờ {tendd} tới Mạnh Tử"
            return yeucau
        if sp["buoc"] == "menu":
            s["trangthai"] = f"{ten}: nói chuyện Mạnh Tử (lần {sp['solan'] + 1})"
            ketqua, yeucau = self._chonmenukc(s, NPCMANHTU[0], xnpc, ynpc, (CHISOBAISU if loai == "baisu" else CHISOXUATSU,))
            if ketqua == "xong":
                sp.update(buoc = "xacnhan", luc = now)
            elif ketqua in ("khongco", "khongmenu"):
                self._logkc(f"Mạnh Tử không có lựa chọn {ten} ({ketqua})")
                sp.update(buoc = "cho", luc = now - THOIGIANCHODODEKC)
            return yeucau
        if sp["buoc"] == "xacnhan":
            # Hộp "Hiện tại bạn có thể nhận <đồ đệ> làm đồ đệ ... 1. Xác nhận" (chưa thấy hộp này lúc xuất sư thì thôi, chờ đồ đệ)
            s["trangthai"] = f"{ten}: xác nhận với Mạnh Tử"
            lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
            if moitruong.get_noidungcuasotuychon() and lenhs:
                self._logkc(f"Mạnh Tử: {moitruong.get_noidungcuasotuychon()[:80]!r} -> chọn {lenhs[0]!r}")
                moitruong.xoa_noidungcuasotuychon()
                moitruong.action_thucthicaulenh(lenhs[0])
                sp.update(buoc = "cho", luc = now)
            elif now - sp["luc"] > THOIGIANCHOMENUKC:
                self._logkc(f"Mạnh Tử không hiện hộp Xác nhận {ten}: chờ {tendd} xác nhận")
                sp.update(buoc = "cho", luc = now)
            return None
        s["trangthai"] = f"{ten}: chờ {tendd} xác nhận"
        if now - sp["luc"] > THOIGIANCHODODEKC:
            sp["solan"] += 1
            if sp["solan"] >= SOLANSUPHUKC:
                s[co] = True
                s.pop("suphu", None)
                self._logkc(f"⚠️ {ten} {tendd}: {SOLANSUPHUKC} lần chưa thấy đồ đệ xác nhận, bỏ qua (làm tay giúp)")
                phatam(f"Không {ten} được")
                return None
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            sp["buoc"] = "menu"
        return None

    def _moibangkc(self, s, gas, solantoida = None):
        # Mời acc gà chưa đồng ý vào bang ("org invite <ID>"), mỗi GIANCACHMOIBANGKC giây 1 người, mỗi người tối đa solantoida lần (None:
        # không giới hạn). -> [ID acc gà chưa vào bang]
        now = time.time()
        chuabangs = [i for i, info in gas.items() if not info["_keocap"].get("dabang")]
        solans = s.setdefault("solanmoibang", {})
        for idga in chuabangs:
            if solantoida is not None and solans.get(idga, 0) >= solantoida:
                continue
            if now - s["lucmoibang"].get(idga, 0.) >= GIANCACHMOIBANGKC:
                s["lucmoibang"][idga] = now
                solans[idga] = solans.get(idga, 0) + 1
                self._logkc(f"Mời {gas[idga].get('tennhanvat') or idga} vào bang (org invite {idga})")
                self.moitruong.action_thucthicaulenh(f"org invite {idga}")
                break
        return chuabangs

    def _buoctaphopchinh(self, s, gas):
        # Về Tân Thủ Thôn (143, 143), chờ acc gà nhận thưởng tân thủ, mời vào nhóm và vào bang
        moitruong = self.moitruong
        now = time.time()
        if self._is_dangban():
            return None
        yeucau = self._ditoikc(s, BANDO_TANTHUTHON, DIEMTAPHOPKEOCAP, "tập hợp")
        if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            return yeucau
        s.setdefault("luctaphop", now)
        chuaxongs = [info.get("tennhanvat") or str(i) for i, info in gas.items() if not info["_keocap"].get("xongtanthu")]
        if chuaxongs:
            s["trangthai"] = f"tập hợp: chờ {', '.join(chuaxongs)} nhận thưởng tân thủ"
            return yeucau
        self._moinhomkc(s, gas)
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if moitruong.get_is_dangnamtrongnhom() else set()
        chuabangs = self._moibangkc(s, gas)
        chuanhoms = [gas[i].get("tennhanvat") or str(i) for i in gas if i not in trongnhoms]
        if chuanhoms:
            s["trangthai"] = f"tập hợp: mời vào nhóm ({', '.join(chuanhoms)} chưa vào)"
            return yeucau
        if chuabangs and now - s["luctaphop"] < THOIGIANCHOBANGKC:
            s["trangthai"] = f"tập hợp: mời vào bang ({', '.join(gas[i].get('tennhanvat') or str(i) for i in chuabangs)} chưa đồng ý)"
            return yeucau
        if chuabangs:
            self._logkc(f"⚠️ {', '.join(gas[i].get('tennhanvat') or str(i) for i in chuabangs)} chưa vào bang sau "
                        f"{int(THOIGIANCHOBANGKC)}s, vẫn đi bãi (mời tay giúp)")
        self._sanggiaidoankc(s, f"bai:{BAIKEOCAPs[0][0]}")
        return None

    def _buocphongyeuchinh(self, s, gas):
        # Chọn acc gà give (có đồ Lam Kim), báo qua shared_data; mình làm thành viên Phong Yêu Kính (dò đánh quái)
        now = time.time()
        if self._is_tudongtheosau:
            self._datkc(s, "_is_tudongtheosau", False, "Theo sau")
        idtoi = self.moitruong.get_idnguoichoi()
        phus = sorted(i for i, info in self._laycuasokeocap().items()
                      if info["_keocap"].get("vaitro") == "phu" and info["_keocap"].get("idchinh") == idtoi)
        if phus != s.get("phus"):
            self._logkc(f"Acc phụ Phong Yêu Kính: {', '.join(map(str, phus)) or 'không có'}")
            s["phus"] = phus
        s["nhompy"] = [idtoi, *sorted(gas), *phus]
        yeucau = self._chuyendolamkimkc(s, gas)
        if yeucau is not False:
            return yeucau
        give = gas.get(s["idgive"])
        if s["idgive"] and give and give.get("_is_danglanglyson"):
            s["luctatgive"] = 0.
        elif s["idgive"]:
            s["luctatgive"] = s["luctatgive"] or now
            if now - s["luctatgive"] > THOIGIANDOINGUOIGIVE:
                self._logkc(f"{(give or {}).get('tennhanvat') or s['idgive']} không còn đi Phong Yêu Kính (hết đồ / tắt), chọn acc gà khác give")
                s["bogive"] = s["idgive"]
                s["idgive"] = 0
        if not s["idgive"]:
            cos = [i for i in sorted(gas) if gas[i]["_keocap"].get("codolamkim") and i != s.get("bogive")]
            if not cos:
                cos = [i for i in sorted(gas) if gas[i]["_keocap"].get("codolamkim")]
            if not cos:
                if all(info["_keocap"].get("codolamkim") is False for info in gas.values()):
                    self._ketthuckeocap("❌ Không acc gà nào còn đồ Lam Kim để đốt (ném thêm đồ rồi bật lại)")
                    return None
                s["trangthai"] = "Phong Yêu Kính: chờ acc gà đọc hành trang tìm đồ Lam Kim"
                return None
            s["idgive"] = cos[0]
            s["luctatgive"] = 0.
            self._logkc(f"Chọn {gas[cos[0]].get('tennhanvat') or cos[0]} làm người give Phong Yêu Kính")
        self._roinhomkhacgivekc(s)
        self._batpykc(s)
        s["trangthai"] = f"Phong Yêu Kính: {gas.get(s['idgive'], {}).get('tennhanvat') or s['idgive']} give, mình dò đánh quái (" + ", ".join(
            f"{info.get('tennhanvat') or i} {info['_keocap'].get('capdo')}" for i, info in gas.items()) + ")"
        return False

    def _chuyendolamkimkc(self, s, gas):
        # Acc chính còn đồ Lam Kim mà acc gà nhận đồ (người give, chưa chọn thì ID nhỏ nhất) đã hết: đứng yên chờ acc gà đó tới cạnh rồi
        # give hết đồ đủ cấp acc gà. Chỉ làm ngoài phó bản. -> yêu cầu di chuyển / None khi đang lo đưa đồ, False khi không cần
        moitruong = self.moitruong
        now = time.time()
        if self._is_trongphongyeu() or s.get("bochuyendo"):
            s["chuyendo"] = 0
            return False
        idnhan = s["idgive"] if s["idgive"] in gas else min(gas)
        nhan = gas[idnhan]
        if nhan["_keocap"].get("codolamkim") is not False:
            s["chuyendo"] = 0
            return False
        if now - s.get("lucdocdochinh", 0.) > GIANCACHDOCDOCHINHKC or s.get("dolamkimchinh") == "doc":
            captoithieu = max(CAPDOLAMKIMTOITHIEU, (nhan["_keocap"].get("capdo") or 0) - taicauhinhphongyeu()["caphonnhanvat"])
            ds = self._chondolamkim(s, captoithieu = captoithieu, is_tatca = True)
            if ds != "doc":
                s["lucdocdochinh"] = now
                if s.get("dolamkimchinh") not in (None, "doc") and len(ds) < len(s["dolamkimchinh"]):
                    s["solangiaodo"] = 0
            s["dolamkimchinh"] = ds
        ds = s.get("dolamkimchinh")
        if ds == "doc":
            s["trangthai"] = "Phong Yêu Kính: đọc túi mình tìm đồ Lam Kim đưa acc gà"
            return None
        tennhan = nhan.get("tennhanvat") or str(idnhan)
        if not ds:
            if now - s.get("lucgiaodo", 0.) < THOIGIANCHONHANDOKC:
                # Vừa đưa hết đồ: chờ acc gà đọc lại túi (không thì tưởng không ai còn đồ, dừng kéo cấp)
                s["trangthai"] = f"Phong Yêu Kính: chờ {tennhan} nhận đồ Lam Kim"
                return None
            s["chuyendo"] = 0
            return False
        if s.get("chuyendo") != idnhan:
            self._logkc(f"{tennhan} hết đồ Lam Kim, mình còn {len(ds)} món: chờ {tennhan} tới để đưa")
            s.update(chuyendo = idnhan, solangiaodo = 0)
        diachi = moitruong.action_timkiemnhanvat(idnguoichoi = idnhan)
        if not diachi:
            if nhan.get("tenbando") != moitruong.get_idbandohientai():
                # Khác bản đồ: để Phong Yêu Kính đưa mình về Chu Quốc (acc gà cũng ở đó chờ)
                s["trangthai"] = f"Phong Yêu Kính: chờ gặp {tennhan} (khác bản đồ) để đưa {len(ds)} món Lam Kim"
                return False
            s["trangthai"] = f"Phong Yêu Kính: chờ {tennhan} tới để đưa {len(ds)} món Lam Kim"
            return None
        if moitruong.get_khoangcach(diachi) > KHOANGCACHGIAODOKC:
            s["trangthai"] = f"Phong Yêu Kính: lại gần {tennhan} để đưa đồ Lam Kim"
            x, y = moitruong.get_toado(diachi)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
        if now - s.get("lucgiaodo", 0.) < GIANCACHGIAODOKC:
            return None
        if s.get("solangiaodo", 0) >= SOLANGIAODOKC:
            self._logkc(f"⚠️ Give {SOLANGIAODOKC} lần mà đồ Lam Kim không giảm (đồ khoá / {tennhan} đầy túi?): thôi đưa đồ, ném tay giúp")
            s.update(bochuyendo = True, chuyendo = 0)
            return False
        moitruong.action_ngatdichuyen()
        for lenh in taolenhgiao(str(idnhan), [(mon[3], 1) for mon in ds], 0):
            moitruong.action_thucthicaulenh(lenh)
            self._logkc(f"Đưa đồ Lam Kim cho {tennhan}: {lenh}")
        self._logkc(f"Đã gửi {len(ds)} món: " + ", ".join(f"{mon[4]} (cấp {mon[0]})" for mon in ds))
        s.update(lucgiaodo = now, solangiaodo = s.get("solangiaodo", 0) + 1, lucdocdochinh = 0.)
        s["trangthai"] = f"Phong Yêu Kính: đưa {len(ds)} món Lam Kim cho {tennhan}"
        return None

    def _roinhomkhacgivekc(self, s):
        # Phong Yêu Kính: người give lập nhóm 1 người rồi mời; ai còn ở nhóm khác (nhóm kéo cấp của acc chính) thì không nhận được lời mời
        # => ở ngoài phó bản mà đang ở nhóm không phải của người give thì rời
        moitruong = self.moitruong
        if not s["idgive"] or s["idgive"] == moitruong.get_idnguoichoi() or self._is_trongphongyeu() or not moitruong.get_is_dangnamtrongnhom():
            return
        if moitruong.get_idnguoichoitruongnhom() == s["idgive"] or time.time() - s.get("lucroinhom", 0.) < GIANCACHROINHOMKC:
            return
        s["lucroinhom"] = time.time()
        self._logkc("Rời nhóm cũ để vào nhóm người give Phong Yêu Kính")
        moitruong.action_thoatkhoinhom()

    def _batpykc(self, s):
        # Bật Phong Yêu Kính (ai tắt thì THOIGIANBATLAIPYKC giây sau bật lại)
        if self._langlyson:
            if self._langlyson["phoban"] != "phongyeukinh":
                self.huy_langlyson()
            return
        if time.time() - s["lucbatpy"] < THOIGIANBATLAIPYKC:
            return
        s["lucbatpy"] = time.time()
        self._logkc("Bật Phong Yêu Kính")
        self.batdau_langlyson("phongyeukinh")

    # --- Acc gà -------------------------------------------------------------------------------------------------------------------------
    def _laychinh(self, s):
        info = self._laycuasokeocap().get(s["idchinh"])
        return info if info and info["_keocap"].get("vaitro") == "chinh" else None

    def _xulykeocapga(self, s):
        moitruong = self.moitruong
        self._datkc(s, "_is_tudongtangcap", True, "Tự tăng cấp")
        if self._captudongtangcaptoida < CAPKETTHUCKEOCAP:
            s.setdefault("tuychoncu", {}).setdefault("_captudongtangcaptoida", self._captudongtangcaptoida)
            self._captudongtangcaptoida = CAPKETTHUCKEOCAP
        self._dongykeocapga(s)
        if not s["xongtanthu"]:
            self._tatsautheokc(s)
            if self._is_dangban():
                return None
            return self._buoctanthuga(s)
        self._dungvatphamconsotkc(s)
        chinh = self._laychinh(s)
        if not chinh:
            s["trangthai"] = f"chờ acc chính (ID {s['idchinh']}) bật kéo cấp"
            self._tatsautheokc(s)
            return None
        giaidoan = chinh["_keocap"].get("giaidoan") or ""
        if giaidoan == "xong":
            self._ketthuckeocap("✅ Acc chính báo xong")
            return None
        s["giaidoan"] = giaidoan if giaidoan != "tanthu" else "taphop"
        self._xacnhansuphuga(s, chinh)
        if giaidoan == "phongyeu":
            self._tatsautheokc(s)
            if chinh["_keocap"].get("chuyendo") == moitruong.get_idnguoichoi() and not self._is_trongphongyeu():
                # Acc chính chờ đưa đồ Lam Kim cho mình: đọc túi thường xuyên, tới cạnh acc chính (khác bản đồ thì để Phong Yêu Kính đưa
                # về Chu Quốc, acc chính cũng về đó)
                s["lucdocdo"] = min(s["lucdocdo"], time.time() - GIANCACHDOCDOLAMKIMKC + GIANCACHDOCDONHANKC)
                self._docdolamkimkc(s)
                s["trangthai"] = f"Phong Yêu Kính: tới nhận đồ Lam Kim từ {chinh.get('tennhanvat') or s['idchinh']}"
                if chinh.get("tenbando") != moitruong.get_idbandohientai():
                    return False if self._langlyson else None
                x, y = chinh.get("x"), chinh.get("y")
                if x and y and moitruong.get_khoangcachdiem(x, y) > KHOANGCACHGIAODOKC - 1:
                    return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
                return None
            self._docdolamkimkc(s)
            s["idgive"] = chinh["_keocap"].get("idgive") or 0
            if not s["idgive"]:
                s["trangthai"] = "Phong Yêu Kính: chờ acc chính chọn người give"
                return None
            self._roinhomkhacgivekc(s)
            self._batpykc(s)
            s["trangthai"] = "Phong Yêu Kính: " + ("mình give, " if s["idgive"] == moitruong.get_idnguoichoi() else "") + \
                             (self.get_trangthailanglyson() or "chờ bật")
            return False
        if self._langlyson:
            self.huy_langlyson()
        self._roinhomkhacchinhkc(s)
        # Tập hợp / bãi: theo sau acc chính (tự tìm đường / phù sang bản đồ khác)
        if "muctieutheosaucu" not in s:
            s["muctieutheosaucu"] = (self._idmuctieutheosau, self._tenmuctieutheosau)
        if self._idmuctieutheosau != s["idchinh"]:
            self.thietlap_muctieutheosau(s["idchinh"], chinh.get("tennhanvat") or "")
        self._datkc(s, "_is_tudongtheosau", True, "Theo sau")
        self._datkc(s, "_is_tutimduongtheosau", True, "Tự tìm đường theo sau")
        s["trangthai"] = f"theo sau {chinh.get('tennhanvat') or s['idchinh']} ({self._tengiaidoan(giaidoan)}, cấp {moitruong.get_capdonhanvat()})"
        return False

    # --- Acc phụ (máy khác nối LAN) -----------------------------------------------------------------------------------------------------
    def _xulykeocapphu(self, s):
        # Chỉ vào Phong Yêu Kính làm thành viên dò đánh quái cùng acc chính; giai đoạn khác trả False để bot chạy như thường
        if not s["idchinh"]:
            chinhs = sorted(i for i, info in self._laycuasokeocap().items() if info["_keocap"].get("vaitro") == "chinh")
            if not chinhs:
                s["trangthai"] = "chờ thấy acc chính đang kéo cấp (cùng máy / qua LAN)"
                return False
            s["idchinh"] = chinhs[0]
            self._logkc(f"Làm acc phụ cho acc chính ID {s['idchinh']}" + (f" (thấy {len(chinhs)} acc chính, lấy ID nhỏ nhất)" if len(chinhs) > 1 else ""))
        chinh = self._laychinh(s)
        if not chinh:
            s["trangthai"] = f"chờ acc chính (ID {s['idchinh']}) online"
            return False
        giaidoan = chinh["_keocap"].get("giaidoan") or ""
        if giaidoan == "xong":
            self._ketthuckeocap("✅ Acc chính báo xong")
            return None
        s["giaidoan"] = giaidoan
        if giaidoan != "phongyeu":
            if self._langlyson and self._langlyson["phoban"] == "phongyeukinh":
                self.huy_langlyson()
            s["trangthai"] = f"chờ acc chính tới Phong Yêu Kính (đang {self._tengiaidoan(giaidoan)})"
            return False
        self._tatsautheokc(s)
        s["idgive"] = chinh["_keocap"].get("idgive") or 0
        if not s["idgive"]:
            s["trangthai"] = "Phong Yêu Kính: chờ acc chính chọn người give"
            return None
        self._roinhomkhacgivekc(s)
        self._batpykc(s)
        s["trangthai"] = f"Phong Yêu Kính: phụ đánh ({self.get_trangthailanglyson() or 'chờ bật'})"
        return False

    def _tatsautheokc(self, s):
        if self._is_tudongtheosau:
            self._datkc(s, "_is_tudongtheosau", False, "Theo sau")

    def _dongykeocapga(self, s):
        # Hộp Yes/No của acc chính: mời nhóm ("team + <ID chính>"), mời bang ("org join <ID chính>"). Phong Yêu Kính thì để
        # tactu_langlyson_xq đồng ý lời mời của người give
        moitruong = self.moitruong
        if s["giaidoan"] == "phongyeu" or not moitruong.get_is_danghiencuasoyesno():
            return
        lenh = moitruong.get_caulenhmoinhomhientai() or ""
        phan = lenh.split()
        if len(phan) == 3 and phan[:2] == ["org", "join"] and phan[2] == str(s["idchinh"]):
            moitruong.action_thucthicaulenh(lenh)
            moitruong.set_is_danghiencuasoyesno(False)
            s["dabang"] = True
            self._logkc(f"Đồng ý vào bang ({lenh!r})")
        elif lenh.startswith("team + "):
            moitruong.action_kiemtravadongyloimoinhom([s["idchinh"]])

    def _roinhomkhacchinhkc(self, s):
        # Tập hợp / bãi: đang ở nhóm không phải của acc chính (nhóm Phong Yêu Kính cũ...) thì rời để nhận lời mời acc chính
        moitruong = self.moitruong
        if not moitruong.get_is_dangnamtrongnhom() or moitruong.get_idnguoichoitruongnhom() == s["idchinh"]:
            return
        if time.time() - s.get("lucroinhom", 0.) > GIANCACHROINHOMKC:
            s["lucroinhom"] = time.time()
            self._logkc("Đang ở nhóm khác: rời để vào nhóm acc chính")
            moitruong.action_thoatkhoinhom()

    def _docdolamkimkc(self, s):
        # Có đồ Lam Kim đốt được không (báo acc chính chọn người give): True / False, None khi chưa đọc xong mô tả
        if self._is_trongphongyeu() or time.time() - s["lucdocdo"] < GIANCACHDOCDOLAMKIMKC:
            return
        chon = self._chondolamkim(s)
        if chon == "doc":
            return
        s["lucdocdo"] = time.time()
        co = bool(chon)
        if co != s["codolamkim"]:
            self._logkc(f"Đồ Lam Kim đốt được: {f'có ({chon[4]}, cấp {chon[0]})' if co else 'không còn'}")
        s["codolamkim"] = co

    def _buoctanthuga(self, s):
        # Thần Tiên Gia Gia: trả nhiệm vụ, nhập code tân thủ, dùng thưởng
        moitruong = self.moitruong
        now = time.time()
        tennpc, x, y = NPCTHANTIENGIAGIA
        buoc = s["tanthu"]
        if buoc in ("nhiemvu", "code"):
            if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                return self._ditoikc(s, BANDO_TANTHUTHON, (x, y), "tới Thần Tiên Gia Gia")
            if buoc == "nhiemvu":
                s["trangthai"] = f"tân thủ: {tennpc} trả nhiệm vụ Sứ Mệnh Đưa Thư"
                ketqua, yeucau = self._chonmenukc(s, tennpc, x, y, MENUNHIEMVUTANTHU)
                if ketqua in ("xong", "khongco", "khongmenu"):
                    self._logkc({"xong": "Đã trả nhiệm vụ Sứ Mệnh Đưa Thư", "khongco": "Không có nhiệm vụ Sứ Mệnh Đưa Thư để trả (đã trả?), bỏ qua",
                                 "khongmenu": f"{tennpc} không mở menu, bỏ qua trả nhiệm vụ"}[ketqua])
                    s.update(tanthu = "code", hoithoai = None, luccho = now + 1.5)
                return yeucau
            if now < s.get("luccho", 0.):
                return None
            if s.get("daguicode"):
                s.update(tanthu = "vatpham", hoithoai = None, luccho = now + 3.)
                return None
            s["trangthai"] = f"tân thủ: {tennpc} nhập code tân thủ"
            ketqua, yeucau = self._chonmenukc(s, tennpc, x, y, MENUCODETANTHU)
            if ketqua == "xong":
                moitruong.action_thucthicaulenh(LENHCODETANTHU)
                self._logkc(f"Nhập code tân thủ ({LENHCODETANTHU!r})")
                s.update({"daguicode": True, "luccho": now + 2., "hoithoai": None, "lucguicode": now})
            elif ketqua in ("khongco", "khongmenu"):
                self._logkc(f"{tennpc} không có lựa chọn Nhập Code Tân Thủ ({ketqua}), bỏ qua")
                s.update(tanthu = "vatpham", hoithoai = None)
            return yeucau
        if now < s.get("luccho", 0.):
            return None
        if buoc == "vatpham":
            # welcome.13747 mở hộp "Xin nhập mã Code Tân Thủ" (cửa sổ mã xác nhận), lệnh codett không tự đóng: tắt cờ mở như bấm Hủy Bỏ
            if moitruong.get_is_dangmocuasoxacnhan() and "Code Tân Thủ" in moitruong.get_noidungcuasomaxacnhan():
                moitruong.set_is_dangmocuasoxacnhan(False)
                self._logkc("Đóng hộp nhập mã Code Tân Thủ")
            dalam = s.setdefault("dungvatpham", {})
            if not dalam and now - s.get("lucguicode", 0.) < THOIGIANCHOTHUONGCODE and (moitruong.get_capdonhanvat() or 0) < 8 \
                    and not any(self._timvatphamkc(tens) for tens in (*(t for t, _ in VATPHAMTANTHUs), (CHIENQUOCLENHX3,))):
                s["trangthai"] = "tân thủ: chờ nhận thưởng code"
                return None
            for tens, cach in VATPHAMTANTHUs:
                mon = self._timvatphamkc(tens)
                if not mon or dalam.get(tens[0], 0) >= SOLANDUNGVATPHAMTANTHU:
                    continue
                if now - s.get("lucdung", 0.) < GIANCACHDUNGVATPHAMKC:
                    return None
                if not self._dungvatphamtanthukc(s, tens[0], cach, mon, dalam.get(tens[0], 0) + 1):
                    continue
                dalam[tens[0]] = dalam.get(tens[0], 0) + 1
                s["lucdung"] = now
                s["trangthai"] = f"tân thủ: dùng {tens[0]}"
                return None
            s["tanthu"] = "chienquoclenh"
            return None
        if buoc == "chienquoclenh":
            mon = self._timvatphamkc((CHIENQUOCLENHX3,))
            solan = s.get("solancql", 0)
            if mon and solan < SOLANDUNGCHIENQUOCLENH:
                if now - s.get("lucdung", 0.) < GIANCACHDUNGVATPHAMKC:
                    return None
                # "use" chỉ mở hộp hỏi đồng ý, "use !" mới thật sự dùng (người dùng xác nhận)
                s.update(solancql = solan + 1, lucdung = now)
                s["trangthai"] = f"tân thủ: dùng {CHIENQUOCLENHX3}"
                self._logkc(f"Dùng {CHIENQUOCLENHX3} (use !, lần {solan + 1})")
                moitruong.action_sudungvatpham(mon[1], is_boquaxacnhan = True, delay = 0.)
                return None
            s.update(tanthu = "xong", xongtanthu = True, giaidoan = "taphop")
            self._logkc(f"Xong thưởng tân thủ (cấp {moitruong.get_capdonhanvat()}), về tập hợp")
            phatam("Acc gà xong tân thủ")
        return None

    def _xacnhansuphuga(self, s, chinh):
        # Mình là đồ đệ acc chính chọn: Mạnh Tử hỏi "Bạn bằng lòng làm đồ đệ của <acc chính> không ?" (hoặc hỏi xuất sư) thì chọn lựa chọn
        # đầu "1. Xác nhận" (tallk 17e5# welcome.13), báo dabaisu / daxuatsu cho acc chính
        moitruong = self.moitruong
        if chinh["_keocap"].get("iddode") != moitruong.get_idnguoichoi() or time.time() - s.get("lucxacnhansp", 0.) < 2.:
            return
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung.startswith(NPCMANHTU[0]):
            return
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        if not lenhs:
            return
        co = "daxuatsu" if chinh["_keocap"].get("giaidoan") == "xuatsu" else "dabaisu"
        s["lucxacnhansp"] = time.time()
        self._logkc(f"Mạnh Tử: {noidung[:80]!r} -> chọn {lenhs[0]!r} ({'xuất sư' if co == 'daxuatsu' else 'bái sư'})")
        moitruong.xoa_noidungcuasotuychon()
        moitruong.action_thucthicaulenh(lenhs[0])
        s[co] = True

    def _dungvatphamconsotkc(self, s):
        # Đã qua tân thủ mà thưởng code (Hoàng Sa Chi Tâm, Cửu Long Thần Hỏa Trảo) còn trong túi (bản cũ dùng "use !", không ăn) / Thủy
        # Bình chưa ở ô mở cuối: dùng lại đúng cách, mỗi món tối đa SOLANDUNGVATPHAMTANTHU lần, GIANCACHDOCVATPHAMSOTKC giây đọc túi 1 lần
        now = time.time()
        if now - s.get("lucdocsot", 0.) < GIANCACHDOCVATPHAMSOTKC or self._is_dangban() or self.get_is_danghoithoainpc():
            return
        s["lucdocsot"] = now
        dalam = s.setdefault("dungvatphamsot", {})
        for tens, cach in VATPHAMTANTHUs:
            mon = self._timvatphamkc(tens)
            if mon and dalam.get(tens[0], 0) < SOLANDUNGVATPHAMTANTHU \
                    and self._dungvatphamtanthukc(s, tens[0], cach, mon, dalam.get(tens[0], 0) + 1, "còn trong túi: "):
                dalam[tens[0]] = dalam.get(tens[0], 0) + 1
                return

    def _dungvatphamtanthukc(self, s, ten, cach, mon, solan, tiento = ""):
        # Dùng món thưởng code tân thủ mon (ô, id) theo cách trong VATPHAMTANTHUs, solan: lần thứ mấy (từ 1).
        # -> True nếu đã gửi lệnh, False nếu không cần (bảo thú đã ở ô mở cuối)
        moitruong = self.moitruong
        vitri, idvatpham = mon
        if cach == "baothu":
            # Phần tự triệu hồi (action_tudongsudungvatpham) chỉ gọi bảo thú vật phẩm ở ô mở cuối cùng, cần bật Tự động sử dụng vật phẩm
            self._datkc(s, "_is_tudongsudungvatpham", True, "Tự động sử dụng vật phẩm")
            ocuoi = moitruong.get_soluongvatphamhanhtrangtoida()
            tencuoi = moitruong.get_tenvatphamhanhtrang(ocuoi)
            if vitri == ocuoi or (tencuoi in BAOTHUVATPHAMs and tencuoi not in THUYBINHs):
                return False
            if ocuoi // SOLUONGOMOITUI == vitri // SOLUONGOMOITUI:
                moitruong.action_dichuyenvatphamhanhtrang(idvatpham, ocuoi + 1, delay = 0.)
            else:
                # Khác túi: "to túi" vào ô trống đầu túi đó, lượt sau chuyển trong túi
                moitruong.action_dichuyenvatphamsanghanhtrangkhac(idvatpham, ocuoi // SOLUONGOMOITUI + 1, delay = 0.)
            self._logkc(f"{ten} {tiento}chuyển vào ô mở cuối ({ocuoi + 1}) cho tự triệu hồi bảo thú (lần {solan})")
            return True
        moitruong.action_sudungvatpham(idvatpham, delay = 0., is_use2 = True)
        self._logkc(f"{ten} {tiento}dùng (use2, lần {solan})")
        return True

    def _timvatphamkc(self, tens):
        # (ô, id) món trong túi có tên đúng là 1 trong tens, không có thì None. Tên ô tối đa 31 byte: chỉ tên đã bị cắt (đủ
        # SOBYTETENBICAT byte) mới so đầu tên, còn lại phải trùng hẳn (không thì "Chiến Quốc Lệnh" khớp nhầm "Chiến Quốc Lệnh x3")
        tens = [_chuanhoa(t) for t in tens]
        for ten, mons in self.moitruong.get_danhsachvatphamhanhtrang_map().items():
            ten = _chuanhoa(ten)
            is_bicat = len(ten.encode("utf-8")) >= SOBYTETENBICAT
            if not ten or not any(t == ten or (is_bicat and t.startswith(ten)) for t in tens):
                continue
            for vitri, iddoituong in mons:
                if iddoituong and vitri < VITRITRANGBIDAUTIEN:
                    return vitri, iddoituong
        return None

    def _chonmenukc(self, s, tennpc, x, y, duois):
        # Tới cạnh NPC, "look", chọn lần lượt lựa chọn có lệnh kết thúc bằng từng đuôi trong duois (mỗi đuôi 1 menu).
        # -> ("xong" | "khongco" (menu không có lựa chọn đó) | "khongmenu" | None, yêu cầu di chuyển)
        moitruong = self.moitruong
        now = time.time()
        idbando = moitruong.get_idbandohientai()
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = tennpc)
        h = s["hoithoai"]
        if not h or h["npc"] != tennpc:
            h = s["hoithoai"] = {"npc": tennpc, "buoc": "look", "luc": 0., "cap": 0, "solan": 0}
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHNOICHUYENKC:
            h.update(buoc = "look", cap = 0)
            xdich, ydich = moitruong.get_toado(diachinpc) if diachinpc else (x, y)
            return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (xdich, ydich, idbando), "khoangcachtoida": 1.}
        if h["buoc"] == "look":
            if now - h["luc"] < 1.:
                return None, None
            idnpc = moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                return None, None
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {idnpc:x}#")
            h.update(buoc = "menu", luc = now, cap = 0)
            return None, None
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung:
            if now - h["luc"] > THOIGIANCHOMENUKC:
                h.update(buoc = "look", solan = h["solan"] + 1, luc = now)
                if h["solan"] >= SOLANTHUMENUKC:
                    s["hoithoai"] = None
                    return "khongmenu", None
            return None, None
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        self._logkc(f"Menu {tennpc}: {noidung[:80]!r} {lenhs}")
        duoi = duois[h["cap"]]
        if isinstance(duoi, int):
            # Số: chọn theo thứ tự lựa chọn (0 = lựa chọn 1), dùng khi chưa biết đuôi lệnh
            lenh = lenhs[duoi] if duoi < len(lenhs) else None
        else:
            lenh = next((l for l in lenhs if l.split()[-1] == duoi), None)
        if not lenh:
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            s["hoithoai"] = None
            return "khongco", None
        moitruong.action_ngatdichuyen()
        moitruong.xoa_noidungcuasotuychon()
        moitruong.action_thucthicaulenh(lenh)
        self._logkc(f"{tennpc}: chọn {lenh!r}")
        if h["cap"] + 1 < len(duois):
            h.update(cap = h["cap"] + 1, luc = now)
            return None, None
        s["hoithoai"] = None
        return "xong", None

    # --- Phong Yêu Kính (gọi từ tactu_langlyson_xq) -----------------------------------------------------------------------------------
    def _is_donguocphongyeukeocap(self):
        # Acc phụ dò Phong Yêu Kính ngược chiều acc chính (_dophongyeu)
        return bool(self._keocap) and self._keocap["vaitro"] == "phu"

    def _laynhompykeocap(self):
        # Đang kéo cấp: (ID người give = acc gà acc chính chọn, [ID người khác: acc chính + acc gà online]) thay cho nhóm todoi, không thì None
        s = self._keocap
        if not s or s["giaidoan"] != "phongyeu" or not s["idgive"]:
            return None
        idtoi = self.moitruong.get_idnguoichoi()
        cuasos = self._laycuasokeocap()
        if s["vaitro"] == "chinh":
            nhom = s.get("nhompy") or []
        else:
            chinh = cuasos.get(s["idchinh"])
            if not chinh:
                return None
            nhom = chinh["_keocap"].get("nhompy") or []
        # Acc chính đứng đầu, rồi acc gà, acc phụ; chỉ tính người online (cửa sổ cùng máy / máy khác nối LAN còn cập nhật)
        ids = [i for i in nhom if i in cuasos or i == idtoi]
        if s["idgive"] not in ids:
            return None
        return s["idgive"], [i for i in ids if i != s["idgive"]]

    def _buoctrongphongyeukeocap(self, s, py, idbando, is_thanhvien):
        # Trong Phong Yêu Kính khi kéo cấp, acc gà không đi đâu: đứng cạnh Thỏ Yêu (đứng đâu cũng có kinh nghiệm), không đánh. Người give
        # hỏi Thỏ Yêu số quái mỗi GIANCACHHOITHOYEU giây, đủ TILERAPHONGYEU thì ra (vòng mới); bản đồ Tây Thành thì ra ngay.
        # -> yêu cầu di chuyển / None, False khi không phải acc gà kéo cấp (Phong Yêu Kính làm như cũ)
        kc = self._keocap
        if not kc or kc["vaitro"] != "ga":
            return False
        now = time.time()
        s["chedo"] = "cho"
        tenpb = self._tenpb(s)
        if not is_thanhvien:
            if idbando == BANDO_TAYTHANH and s.get("rataythanh") != s["sovong"]:
                s["rataythanh"] = s["sovong"]
                self._logpb(s, "Bản đồ Tây Thành (khó đi): ra mở bản đồ khác")
                s.update(giaidoan = "nhanthuong", hoithoai = None)
                return None
            if py["hoisoquai"]:
                return self._hoisoquaiphongyeu(s, py)
            soquai, socan = py.get("soquai"), py.get("soquaican")
            if soquai is not None and socan and soquai >= socan * TILERAPHONGYEU:
                self._logpb(s, f"Đã đánh {soquai}/{socan} quái (≥ {TILERAPHONGYEU:.0%}): ra mở vòng mới")
                s.update(giaidoan = "nhanthuong", hoithoai = None)
                return None
            if now - py.get("luchoithoyeu", py["lucvao"]) > GIANCACHHOITHOYEU:
                py["luchoithoyeu"] = now
                py["hoisoquai"] = now
                return None
            tiendo = f"{soquai}/{socan} quái" if soquai is not None and socan else "chưa hỏi số quái"
            s["trangthai"] = f"{tenpb}: acc gà đứng ở Thỏ Yêu chờ quái ({tiendo}, ra khi ≥ {TILERAPHONGYEU:.0%})"
        else:
            py["hoisoquai"] = None
            s["trangthai"] = f"{tenpb}: acc gà đứng ở Thỏ Yêu hưởng kinh nghiệm"
        x, y = self._vitrithoyeu(s, py, idbando)
        if self.moitruong.get_khoangcachdiem(x, y) > KHOANGCACHNOICHUYENKC:
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}
        return None
