# Tự động đi phó bản Tập Kích Môn Phái (bật tay trên giao diện, chọn 1 trong 7 môn phái, chạy vòng này sang vòng khác tới khi bấm dừng).
# Nhân vật bật là trưởng nhóm (đi một mình cũng được), các thành viên bật Theo sau. Mỗi vòng:
#   vào     : tới bản đồ môn phái đã chọn, đi dò khắp bản đồ tìm NPC Võ Lâm Bại Hoại (vị trí không cố định; chỗ từng thấy đi trước),
#             "look" -> "1. Bớt nói nhảm đi, ta oánh nè !" -> "1. Dùng 5 Ngân Bảo gia tăng 50% kinh nghiệm" (mọi thành viên cũng hiện menu
#             "Muốn vào không ?", bot thành viên tự chọn lựa chọn 1: _xulymenutapkich) -> hệ thống đưa vào phó bản
#   trong   : bản đồ mượn ID 151 (Kênh Trịnh Quốc 1), nhận ra qua tên "Tập Kích Môn Ph". Có thể hỏi mua Võ Lâm Bại Hoại Lễ Bao (hộp Xác Nhận /
#             Hủy Bỏ) -> bấm Xác Nhận. Đi dò khắp bản đồ đánh mọi quái (500 con + boss Thủ Lĩnh Võ Lâm Bại Hoại); giết boss xong 15s hệ
#             thống tự đưa ra ngoài => vòng xong, vào vòng sau
# Bật ở thành viên (đang trong nhóm, không phải trưởng nhóm) thì chỉ làm thành viên: tự chọn menu vào / mua Lễ Bao, Theo sau lo đi lại.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import time

from hangso_xq import *
from nhiemvu_xq import BANDOMONPHAI, chuanhoaten
from thongbao_xq import baosuco
from tienich_xq import phatam

TENNPCTAPKICH = "Võ Lâm Bại Hoại"
# Boss cuối trong phó bản: thấy rồi thì thôi đi dò, đứng đánh; khuất tầm nhìn mà cách chỗ thấy lần cuối quá chừng này ô thì quay lại đó
TENBOSSTAPKICH = "Thủ Lĩnh Võ Lâm Bại Hoại"
KHOANGCACHVEBOSSTAPKICH = 6.
# Menu thứ 2 (mọi thành viên đều hiện): "Muốn vào không ?" 1. Dùng 5 Ngân Bảo gia tăng 50% kinh nghiệm 2. Tiến vào
LOINPCVAOTAPKICH = "muốn vào không"
# Thành viên chưa tới gần NPC: "Hãy gọi tất cả thành viên trong đội tới đây rồi muốn vào th..." (không có lựa chọn) -> chờ chừng này giây
# rồi nói lại
LOINPCGOITHANHVIEN = "gọi tất cả thành viên"
GIANCACHCHOTHANHVIENTAPKICH = 5.
# Đứng cách NPC tối đa chừng này ô mới "look"; look xong chờ menu tối đa THOIGIANCHOMENUTAPKICH giây rồi look lại
KHOANGCACHNOICHUYENTAPKICH = 3.
THOIGIANCHOMENUTAPKICH = 3.
# Chọn xong menu vào chờ được đưa vào phó bản tối đa chừng này giây, không thì nói chuyện lại; quá SOLANTHUVAOTAPKICH lần thì dừng (hết
# Ngân Bảo / hết lượt trong ngày?)
THOIGIANCHOVAOTAPKICH = 30.
SOLANTHUVAOTAPKICH = 3
# Đi dò: tới cách điểm chừng này ô là tới, quá THOIGIANMOIDIEMTAPKICH giây chưa tới (kẹt) thì sang điểm kế
KHOANGCACHTOIDIEMTAPKICH = 3.
THOIGIANMOIDIEMTAPKICH = 25.
# Thành viên / trưởng nhóm tự chọn menu vào, bấm Xác Nhận hộp mua Lễ Bao: mỗi lần cách nhau ít nhất chừng này giây
GIANCACHCHONMENUTAPKICH = 2.
# Chọn menu vào xong chừng này giây vẫn coi hộp xác nhận hiện ra là của Tập Kích (Lễ Bao có thể hỏi ngay lúc vừa vào)
THOIGIANHOPSAUVAO = 60.
# Mỗi vòng quá chừng này giây chưa xong thì báo (vẫn chạy tiếp)
THOIGIANVONGTAPKICHTOIDA = 40 * 60.


class TacTuTapKich:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_tapkich(self, phai = None):
        phai = phai or self._tapkich_phai or self.moitruong.get_tenmonphai()
        if self._tapkich or phai not in BANDOMONPHAI:
            return
        self._tapkich_phai = phai
        self._tapkich = {"phai": phai, "batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "hoithoai": None, "dabao": set(),
                         "sovong": 0, "davao": False, "lucchon": 0., "solanloi": 0, "lucbatdauvong": time.time(), "do": None}
        self._logtk(f"Bắt đầu tự động đi Tập Kích Môn Phái ({TENMONPHAI.get(phai, phai)})")
        phatam("Bắt đầu Tập Kích Môn Phái")

    def huy_tapkich(self):
        if self._tapkich:
            self._ketthuctapkich("Đã dừng Tập Kích Môn Phái (bấm tay)")

    def thietlap_phaitapkich(self, phai):
        if phai in BANDOMONPHAI:
            self._tapkich_phai = phai
            if self._tapkich and self._tapkich["phai"] != phai and not self._tapkich["davao"]:
                self._tapkich.update(phai = phai, do = None, hoithoai = None)
                self._logtk(f"Đổi môn phái: {TENMONPHAI.get(phai, phai)}")

    def get_is_dangtapkich(self):
        return bool(self._tapkich)

    def get_is_tapkichdichuyen(self):
        # Đang tự lo đi lại / tìm NPC ngoài phó bản: không chọn quái dọc đường, đi trước đánh / nhặt
        return bool(self._tapkich) and self._tapkich["chedo"] == "dichuyen"

    def get_is_tapkichdanhquai(self):
        # Trong phó bản: đánh mọi quái, không giới hạn theo danh sách tên / điểm đánh của nhân vật
        return bool(self._tapkich) and self._tapkich["chedo"] == "danhquai"

    def get_trangthaitapkich(self):
        if self._tapkich:
            s = self._tapkich
            return f"Tập Kích {TENMONPHAI.get(s['phai'], s['phai'])} (xong {s['sovong']} vòng): {s['trangthai']}"
        return self._ketquatapkich or ""

    def _logtk(self, noidung):
        self.moitruong._inlog(f"[TẬP KÍCH] {noidung}")

    def _ketthuctapkich(self, thongbao):
        s = self._tapkich
        self._tapkich = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if s and s["sovong"]:
            thongbao += f" (xong {s['sovong']} vòng)"
        self._logtk(thongbao)
        self._ketquatapkich = f"{time.strftime('%H:%M')} {thongbao}"
        phatam("Kết thúc Tập Kích Môn Phái")

    def _baotapkich(self, s, khoa, noidung):
        # Báo Telegram 1 lần cho mỗi việc cần người dùng để ý, bot vẫn chạy tiếp
        if khoa not in s["dabao"]:
            s["dabao"].add(khoa)
            self._logtk(noidung)
            baosuco(self.moitruong, "langlyson", noidung, khoa = f"tapkich|{s['batdau']}|{khoa}", giancach = 0.)

    def _batdanhquaitapkich(self, s):
        # Ô cần cho đánh quái người dùng quên bật thì đổi giúp, dừng thì trả lại. "Chỉ đánh người chơi" của người dùng giữ nguyên
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            if thuoctinh != "_is_chidanhnguoichoi" and getattr(self, thuoctinh) != giatri:
                s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
                setattr(self, thuoctinh, giatri)
                self._logtk(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" để đánh quái (dừng thì trả lại)")

    # --- Menu vào / hộp mua Lễ Bao (trưởng nhóm và thành viên) ----------------------------------------------------------------------
    def _is_thamgiatapkich(self):
        # Mình bật Tập Kích, hoặc người mình theo sau (cùng máy) đang đi Tập Kích
        if self._tapkich:
            return True
        if not self._is_tudongtheosau:
            return False
        info = self._laythongtinmuctieutheosaucuasokhac()
        return bool(info and info.get("_is_dangtapkich"))

    def _xulymenutapkich(self):
        # Gọi mỗi lượt: menu "Muốn vào không ?" (trưởng nhóm chọn "Bớt nói nhảm" thì mọi thành viên đều hiện) -> chọn lựa chọn 1 "Dùng 5 Ngân
        # Bảo gia tăng 50% kinh nghiệm"; hộp Xác Nhận / Hủy Bỏ mua Võ Lâm Bại Hoại Lễ Bao (trong phó bản / ngay sau khi chọn vào) -> Xác Nhận.
        # Trưởng nhóm đang tự nói chuyện NPC (hoithoai) thì để _noichuyenlls chọn
        if not self._is_thamgiatapkich():
            return
        moitruong = self.moitruong
        now = time.time()
        if now - self._lucchonmenutapkich < GIANCACHCHONMENUTAPKICH:
            return
        if moitruong.get_is_danghiencuasotuychon() and not (self._tapkich and self._tapkich["hoithoai"]):
            noidung = moitruong.get_noidungcuasotuychon() or ""
            if LOINPCVAOTAPKICH in noidung.lower():
                lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
                if lenhs:
                    self._lucchonmenutapkich = self._lucchonvaotapkich = now
                    moitruong.action_ngatdichuyen()
                    moitruong.xoa_noidungcuasotuychon()
                    moitruong.action_thucthicaulenh(lenhs[0])
                    self._logtk(f"Menu vào phó bản: chọn lựa chọn 1 (Dùng 5 Ngân Bảo) ({lenhs[0]!r})")
                    return
        hop = moitruong.get_hopxacnhannpc()
        # Hộp mời / xin vào nhóm ("team ...") không phải của Tập Kích
        if hop[0] and not hop[1].startswith("team ") \
                and (moitruong.get_is_bandotapkichmonphai() or now - self._lucchonvaotapkich < THOIGIANHOPSAUVAO):
            self._lucchonmenutapkich = now
            moitruong.action_ngatdichuyen()
            moitruong.action_thucthicaulenh(hop[1])
            moitruong.action_donghopxacnhannpc()
            self._logtk(f"Hộp xác nhận (mua Lễ Bao): bấm Xác Nhận ({hop[1]!r}), đóng hộp")

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulytapkich(self):
        # Gọi thay lộ trình điểm đánh khi đang đi Tập Kích -> yêu cầu di chuyển hoặc None
        s = self._tapkich
        moitruong = self.moitruong
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logtk(s["trangthai"])
        s["chedo"] = "dichuyen"
        if moitruong.get_is_nhanvatdachet() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0 or moitruong.get_is_dangvankhi():
            return None
        if time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        if time.time() - s["lucbatdauvong"] > THOIGIANVONGTAPKICHTOIDA:
            self._baotapkich(s, f"cham|{s['sovong']}", f"⚠️ Tập Kích: vòng {s['sovong'] + 1} quá {int(THOIGIANVONGTAPKICHTOIDA // 60)} phút chưa xong "
                                                     f"({s['trangthai']})")
        idbando = moitruong.get_idbandohientai()
        is_trongphoban = moitruong.get_is_bandotapkichmonphai()
        if is_trongphoban:
            if not s["davao"]:
                s.update(davao = True, hoithoai = None, lucchon = 0., solanloi = 0, do = None, vitriboss = None)
                self._logtk(f"Đã vào phó bản (vòng {s['sovong'] + 1})")
            s["chedo"] = "danhquai"
            self._batdanhquaitapkich(s)
            # Thủ Lĩnh là con cuối: thấy rồi thì thôi đi dò, đứng đánh; khuất tầm nhìn thì quay về chỗ thấy lần cuối
            diachiboss = self._timnpctapkich(tenca = TENBOSSTAPKICH)[0]
            if diachiboss:
                if not s.get("vitriboss"):
                    self._logtk(f"Thấy {TENBOSSTAPKICH}: thôi dò bản đồ, đánh boss")
                s["vitriboss"] = moitruong.get_toado(diachiboss)
            if s.get("vitriboss"):
                s["trangthai"] = f"vòng {s['sovong'] + 1}: đánh {TENBOSSTAPKICH}"
                xboss, yboss = s["vitriboss"]
                if not diachiboss and moitruong.get_khoangcachdiem(xboss, yboss) > KHOANGCACHVEBOSSTAPKICH:
                    return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (xboss, yboss, idbando), "khoangcachtoida": 1.}
                return None
            return self._ditheodiem(s, idbando, f"vòng {s['sovong'] + 1}: dò khắp bản đồ đánh quái")
        if s["davao"]:
            # Giết boss xong hệ thống tự đưa ra (hoặc chết / rớt ra): xong vòng, vào vòng sau
            s["sovong"] += 1
            s.update(davao = False, do = None, hoithoai = None, lucbatdauvong = time.time())
            self._logtk(f"Ra khỏi phó bản: xong vòng {s['sovong']}, vào vòng sau")
        if moitruong.get_is_dangnamtrongnhom() and not moitruong.get_is_truongnhom():
            # Thành viên: Theo sau lo đi lại, menu vào / Lễ Bao tự chọn (_xulymenutapkich)
            s["chedo"] = "thanhvien"
            s["trangthai"] = "thành viên: đi theo trưởng nhóm" + ("" if self._is_tudongtheosau else " (chưa bật Theo sau!)")
            return None
        return self._buocvaotapkich(s, idbando)

    def _buocvaotapkich(self, s, idbando):
        moitruong = self.moitruong
        bandophai = BANDOMONPHAI[s["phai"]]
        tenphai = TENMONPHAI.get(s["phai"], s["phai"])
        if idbando != bandophai:
            s["trangthai"] = f"tới {laytenbando(bandophai)} tìm {TENNPCTAPKICH}"
            buoc = self._lapbuocditoibando(bandophai, is_hoithanhphu = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                s["trangthai"] = f"không có đường tới {laytenbando(bandophai)}: {buoc['mota']}"
                return None
            return self._thuchienbuocditoibando(buoc, bandophai, None, f"[TẬP KÍCH] Tới {tenphai}")
        now = time.time()
        if s["lucchon"]:
            # Đã chọn vào: chờ hệ thống đưa vào phó bản
            if now - s["lucchon"] < THOIGIANCHOVAOTAPKICH:
                s["trangthai"] = f"đã chọn vào, chờ được đưa vào phó bản ({int(now - s['lucchon'])}s)"
                return None
            s["solanloi"] += 1
            s.update(lucchon = 0., hoithoai = None)
            if s["solanloi"] >= SOLANTHUVAOTAPKICH:
                baosuco(moitruong, "langlyson", f"⚠️ Tập Kích: chọn vào {SOLANTHUVAOTAPKICH} lần không được đưa vào phó bản (hết Ngân Bảo / hết lượt?), "
                                                f"dừng tự động", khoa = f"tapkich|{s['batdau']}|khongvao", giancach = 0.)
                self._ketthuctapkich(f"❌ Dừng: chọn vào {SOLANTHUVAOTAPKICH} lần không vào được phó bản")
                return None
            self._logtk(f"Chọn vào {THOIGIANCHOVAOTAPKICH:.0f}s chưa được đưa vào phó bản, nói chuyện lại (lần {s['solanloi'] + 1})")
        if now < s.get("lucthulai", 0.):
            s["trangthai"] = f"chờ thành viên tới gần {TENNPCTAPKICH} ({int(s['lucthulai'] - now)}s)"
            return None
        h = s["hoithoai"]
        diachinpc, idnpc = self._timnpctapkich(h["id"] if h else 0)
        if not diachinpc:
            s["hoithoai"] = None
            return self._ditheodiem(s, idbando, f"dò {laytenbando(idbando)} tìm {TENNPCTAPKICH}", is_timnpc = True)
        # Không ghi toạ độ vào trạng thái: NPC đi lại, mỗi lần đổi là 1 dòng log
        s["trangthai"] = f"vào phó bản (vòng {s['sovong'] + 1}): nói chuyện {TENNPCTAPKICH} (id {idnpc:x})"
        ketqua, yeucau = self._noichuyentapkich(s, diachinpc, idnpc)
        if ketqua == "xong":
            s["lucchon"] = self._lucchonvaotapkich = time.time()
            self._logtk("Đã chọn \"Bớt nói nhảm\" -> \"Dùng 5 Ngân Bảo\", chờ được đưa vào phó bản")
        elif ketqua == "chothanhvien":
            s["lucthulai"] = time.time() + GIANCACHCHOTHANHVIENTAPKICH
            self._logtk(f"NPC bảo gọi đủ thành viên tới: chờ {GIANCACHCHOTHANHVIENTAPKICH:.0f}s rồi nói lại")
        return yeucau

    def _noichuyentapkich(self, s, diachinpc, idnpc):
        # Tới cạnh đúng con NPC idnpc, "look" -> menu 1 chọn lựa chọn 1 "Bớt nói nhảm đi, ta oánh nè !" -> menu "Muốn vào không ?" chọn lựa
        # chọn 1 "Dùng 5 Ngân Bảo". NPC bảo "Hãy gọi tất cả thành viên trong đội tới đây..." (không có lựa chọn) thì chờ thành viên.
        # -> (None | "xong" | "chothanhvien", yêu cầu di chuyển)
        moitruong = self.moitruong
        now = time.time()
        h = s["hoithoai"]
        if not h or h["id"] != idnpc:
            h = s["hoithoai"] = {"id": idnpc, "buoc": "look", "luc": 0., "cap": 0}
        if moitruong.get_khoangcach(diachinpc) > KHOANGCACHNOICHUYENTAPKICH:
            h["buoc"] = "look"
            x, y = moitruong.get_toado(diachinpc)
            # Đi thẳng theo ô (tìm đường của game trong môn phái hay chạy vòng)
            return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, moitruong.get_idbandohientai()), "khoangcachtoida": 1.,
                          "is_dioo": True}
        if h["buoc"] == "look":
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {idnpc:x}#")
            h.update(buoc = "chon", luc = now, cap = 0)
            return None, None
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung:
            if now - h["luc"] > THOIGIANCHOMENUTAPKICH:
                h["buoc"] = "look"
            return None, None
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        self._logtk(f"Menu {TENNPCTAPKICH}: {noidung[:80]!r} {lenhs}")
        thuong = noidung.lower()
        if LOINPCGOITHANHVIEN in thuong:
            s["hoithoai"] = None
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            return "chothanhvien", None
        if not lenhs:
            moitruong.xoa_noidungcuasotuychon()
            h.update(buoc = "look", luc = now)
            return None, None
        moitruong.action_ngatdichuyen()
        moitruong.xoa_noidungcuasotuychon()
        moitruong.action_thucthicaulenh(lenhs[0])
        self._logtk(f"{TENNPCTAPKICH}: chọn lựa chọn 1 ({lenhs[0]!r})")
        if LOINPCVAOTAPKICH in thuong:
            s["hoithoai"] = None
            return "xong", None
        # Menu 1 xong: chờ menu "Muốn vào không ?"
        h.update(buoc = "chon", luc = now, cap = 1)
        return None, None

    def _timnpctapkich(self, idgiu = 0, tenca = None):
        # NPC Võ Lâm Bại Hoại trong tầm nhìn -> (địa chỉ, id đối tượng) hoặc (0, 0). Môn phái có nhiều con cùng lúc: lấy con idgiu (đang
        # tới) nếu còn thấy, không thì con gần nhất (trước lấy con đầu danh sách, thứ tự đổi liên tục nên chạy qua chạy lại giữa các con).
        # tenca: tìm con có đúng tên này (đã chuẩn hoá) còn sống thay vì tên chứa "Võ Lâm Bại Hoại" (boss Thủ Lĩnh cũng chứa)
        moitruong = self.moitruong
        canten = chuanhoaten(tenca or TENNPCTAPKICH)
        toado = moitruong.get_toado()
        tot = None
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi):
                continue
            tenxet = chuanhoaten(moitruong.get_tendoituong(diachi) or "")
            if (tenxet != canten if tenca else canten not in tenxet):
                continue
            if tenca and moitruong.get_is_nhanvatdachet(diachi):
                continue
            khoangcach = math.dist(toado, moitruong.get_toado(diachi))
            iddoituong = moitruong.get_iddoituong(diachi)
            if khoangcach > KHOANGCACHTOANMANHINH:
                continue
            if idgiu and iddoituong == idgiu:
                return diachi, iddoituong
            if not tot or khoangcach < tot[0]:
                tot = (khoangcach, diachi, iddoituong)
        return tot[1:] if tot else (0, 0)

    def _ditheodiem(self, s, idbando, nhan, is_timnpc = False):
        # Đi lần lượt các điểm dò phủ vùng đi được (lưới vật cản, _taodiemdo), hết thì đi lại từ đầu. Tìm NPC thì chỗ từng thấy NPC đi trước
        moitruong = self.moitruong
        do = s["do"]
        if not do or do["idbando"] != idbando:
            diems = list(self._taodiemdo(idbando))
            vitri = self._sovitri.timnpc(TENNPCTAPKICH, idbando = idbando) if is_timnpc else None
            if vitri:
                diems.insert(0, tuple(vitri[1:3]))
            if not diems:
                s["trangthai"] = f"{nhan}: chưa đọc được bản đồ"
                return None
            # Bắt đầu từ chỗ từng thấy NPC, không có thì từ điểm gần mình nhất
            toado = moitruong.get_toado()
            i = 0 if vitri else min(range(len(diems)), key = lambda k: math.dist(diems[k], toado))
            do = s["do"] = {"idbando": idbando, "diems": diems, "i": i, "luc": time.time()}
            self._logtk(f"{laytenbando(idbando)}: {len(diems)} điểm dò")
        x, y = do["diems"][do["i"]]
        if moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIDIEMTAPKICH or time.time() - do["luc"] > THOIGIANMOIDIEMTAPKICH:
            do["i"] = (do["i"] + 1) % len(do["diems"])
            do["luc"] = time.time()
            x, y = do["diems"][do["i"]]
        s["trangthai"] = f"{nhan} (điểm {do['i'] + 1}/{len(do['diems'])})"
        self._capnhatbuocdichuyen(f"Tập Kích: {nhan} (điểm {do['i'] + 1}/{len(do['diems'])})")
        # Dò môn phái tìm NPC: đi theo ô (tìm đường của game chạy vòng); trong phó bản giữ như cũ
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1., "is_dioo": is_timnpc}
