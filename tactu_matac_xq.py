# Tự động đánh Đoạt Bảo Mã Tặc (hoạt động 10h, 14h, 18h, 22h thứ 4, 5, 7, chủ nhật; bật tay trên giao diện, chạy tới khi bấm dừng).
# Mỗi nhân vật đi riêng, phải ở nhóm chỉ có mình: tới gần Mã Tặc thì rời nhóm có người khác / lập nhóm 1 người
# ("team + <ID mình>"), Tổ đội tự động nghỉ suốt lúc đang bật; dừng thì rời nhóm 1 người đã lập cho Tổ đội tự động gom lại. Bản đồ có Mã Tặc ngẫu nhiên mỗi lần: người dùng tự nhập, hoặc bot đọc tin hệ thống
# "Nghe nói có một đám Đoạt Bảo Mã Tặc đã xuất hiện tại Bờ Vô Định Hà, Vô Định Hà 1, ... !" (báo đúng giờ bắt đầu) rồi tự điền.
# Bật ô "Tự bật khi có tin" thì tin đó cũng là lúc tự bắt đầu (nhân vật đang rảnh: không làm sư môn / phó bản / giao đồ...).
# Mỗi vòng:
#   ngoài : tới bản đồ trong danh sách, dò khắp bản đồ tìm NPC Đoạt Bảo Mã Tặc (cưỡi ngựa, nhiều con), "look" -> "Ngươi muốn khiêu chiến
#           với ta sao, suy nghĩ kĩ chưa ?" -> "1. Khiêu chiến" -> hệ thống đưa vào phó bản. Dò hết bản đồ không thấy thì sang bản đồ kế
#   trong : phó bản riêng (nhận ra khi bản đồ / tên bản đồ game đổi sau lúc chọn Khiêu chiến, hoặc thấy Mã Tặc là quái), đánh Đoạt Bảo
#           Mã Tặc (cấp 100) tới chết -> hệ thống đưa về bản đồ cũ => xong vòng, tìm con khác
# Đi hết danh sách bản đồ SOLANDOTRONGMATAC lượt liền không thấy con nào thì coi như hết hoạt động, tự dừng.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import re
import time
import unicodedata

from hangso_xq import *
from bando_xq import layidbandotheoten
from nhiemvu_xq import chuanhoaten
from thongbao_xq import baosuco
from tienich_xq import phatam

TENMATAC = "Đoạt Bảo Mã Tặc"
# Tin hệ thống báo bản đồ: "... Đoạt Bảo Mã Tặc đã xuất hiện tại <bản đồ>, <bản đồ>, ... !"
MAUTINBANDOMATAC = re.compile(r"Đoạt Bảo Mã Tặc đã xuất hiện tại\s*(.+?)\s*!?\s*$")
# Menu NPC: "Ngươi muốn khiêu chiến với ta sao, suy nghĩ kĩ chưa ?" 1. Khiêu chiến 2. Rời khỏi
LOINPCKHIEUCHIENMATAC = "khiêu chiến"
KHOANGCACHNOICHUYENMATAC = 3.
THOIGIANCHOMENUMATAC = 3.
# Chọn Khiêu chiến xong chờ được đưa vào phó bản tối đa chừng này giây, không thì nói chuyện lại; con đó quá SOLANTHUVAOMATAC lần (bị
# người khác giành / NPC từ chối) thì bỏ qua con đó BOQUAMATAC giây
THOIGIANCHOVAOMATAC = 20.
SOLANTHUVAOMATAC = 3
BOQUAMATAC = 120.
# Rời nhóm / lập nhóm 1 người: mỗi lần cách nhau ít nhất chừng này giây (chờ máy chủ cập nhật nhóm)
GIANCACHLAPNHOMMATAC = 3.
# Đi dò: tới cách điểm chừng này ô là tới, quá THOIGIANMOIDIEMMATAC giây chưa tới (kẹt) thì sang điểm kế
KHOANGCACHTOIDIEMMATAC = 3.
THOIGIANMOIDIEMMATAC = 25.
# Trong phó bản: Mã Tặc khuất tầm nhìn mà cách chỗ thấy lần cuối quá chừng này ô thì quay lại đó
KHOANGCACHVEMATAC = 6.
# Đi hết danh sách bản đồ chừng này lượt liền không thấy Mã Tặc nào thì dừng (hết hoạt động / bị giết hết)
SOLANDOTRONGMATAC = 2
# Ở trong phó bản quá chừng này giây thì báo (vẫn chạy tiếp)
THOIGIANPHOBANMATACTOIDA = 10 * 60.


def tachbandomatac(chuoi):
    # "Bờ Vô Định Hà, Vô Định Hà 1" -> ([id bản đồ...], [tên không nhận ra...]), bỏ trùng, giữ thứ tự
    ids, loi = [], []
    for ten in re.split(r"[,;\n]", chuoi or ""):
        ten = ten.strip(" !.")
        if not ten:
            continue
        idbando = layidbandotheoten(ten)
        if idbando is None:
            loi.append(ten)
        elif idbando not in ids:
            ids.append(idbando)
    return ids, loi


class TacTuMaTac:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_matac(self):
        if self._matac:
            return
        self._matac = {"batdau": time.time(), "trangthai": "bắt đầu", "chedo": "dichuyen", "hoithoai": None, "dabao": set(), "sovong": 0,
                       "davao": False, "lucchon": 0., "ngoai": None, "solanloi": 0, "boqua": {}, "ibando": 0, "do": None,
                       "solandotrong": 0, "lucvao": 0., "vitriboss": None}
        self._logmt(f"Bắt đầu tự động đánh {TENMATAC} (bản đồ: {self._matac_bandos or 'chờ tin hệ thống'})")
        phatam("Bắt đầu Đoạt Bảo Mã Tặc")

    def huy_matac(self):
        if self._matac:
            self._ketthucmatac("Đã dừng Đoạt Bảo Mã Tặc (bấm tay)")

    def thietlap_bandomatac(self, chuoi):
        ids, loi = tachbandomatac(chuoi)
        self._matac_bandos = ", ".join(laytenbando(i) for i in ids)
        self._logmt(f"Bản đồ: {self._matac_bandos or '(trống)'}" + (f", không nhận ra: {', '.join(loi)}" if loi else ""))
        if self._matac and not self._matac["davao"]:
            self._matac.update(ibando = 0, do = None, hoithoai = None, solandotrong = 0)

    def get_is_dangmatac(self):
        return bool(self._matac)

    def get_is_matacdichuyen(self):
        # Đang tự lo đi lại / tìm NPC ngoài phó bản: không chọn quái dọc đường
        return bool(self._matac) and self._matac["chedo"] == "dichuyen"

    def get_is_matacdanhquai(self):
        # Trong phó bản: đánh mọi quái (chỉ có Mã Tặc)
        return bool(self._matac) and self._matac["chedo"] == "danhquai"

    def get_trangthaimatac(self):
        if self._matac:
            return f"Đoạt Bảo Mã Tặc (giết {self._matac['sovong']} con): {self._matac['trangthai']}"
        return self._ketquamatac or ""

    def _logmt(self, noidung):
        self.moitruong._inlog(f"[MÃ TẶC] {noidung}")

    def _ketthucmatac(self, thongbao):
        s = self._matac
        self._matac = None
        self._yeucautudo = None
        for thuoctinh, giatri in ((s or {}).get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if s and s["sovong"]:
            thongbao += f" (giết {s['sovong']} con)"
        if s and s.get("dalapnhom") and self.moitruong.get_is_dangnamtrongnhom():
            # Nhóm 1 người mình lập: rời (giải tán) để Tổ đội tự động gom lại như cũ
            self.moitruong.action_thoatkhoinhom()
            thongbao += ", rời nhóm 1 người"
        self._logmt(thongbao)
        self._ketquamatac = f"{time.strftime('%H:%M')} {thongbao}"
        phatam("Kết thúc Đoạt Bảo Mã Tặc")

    def _baomatac(self, s, khoa, noidung):
        # Báo Telegram 1 lần cho mỗi việc cần người dùng để ý, bot vẫn chạy tiếp
        if khoa not in s["dabao"]:
            s["dabao"].add(khoa)
            self._logmt(noidung)
            baosuco(self.moitruong, "langlyson", noidung, khoa = f"matac|{s['batdau']}|{khoa}", giancach = 0.)

    def _batdanhquaimatac(self, s):
        # Ô cần cho đánh quái người dùng quên bật thì đổi giúp, dừng thì trả lại. "Chỉ đánh người chơi" của người dùng giữ nguyên
        for thuoctinh, giatri, ten in self._TUYCHONDANHQUAI:
            if thuoctinh != "_is_chidanhnguoichoi" and getattr(self, thuoctinh) != giatri:
                s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
                setattr(self, thuoctinh, giatri)
                self._logmt(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" để đánh quái (dừng thì trả lại)")

    def thietlap_tubatmatac(self, is_bat):
        self._is_tubatmatac = bool(is_bat)
        self._logmt("Tự bật khi có tin hệ thống" if is_bat else "Tắt tự bật khi có tin hệ thống")

    def _is_bantubatmatac(self):
        # Đang làm việc khác thay lộ trình điểm đánh thì không tự bật Mã Tặc chen ngang
        return bool(self._idbandocandi or self.get_is_danggiaodo() or self.get_is_dangcatkho() or self.get_is_dangsumon()
                    or self.get_is_danglanglyson() or self.get_is_dangsugia() or self.get_is_dangtapkich() or self.get_is_dangdanhvong())

    def action_doctinmatac(self):
        # Gọi mỗi lượt (kể cả khi chưa bật): tin hệ thống báo bản đồ có Mã Tặc -> điền thay danh sách bản đồ (lưu theo nhân vật, giao diện
        # hiện lại); bật ô tự bật mà đang rảnh thì bắt đầu luôn
        for thoidiem, noidung in self.moitruong.get_lichsutrochuyen5s():
            if thoidiem <= self._thoidiemxettinmatac:
                continue
            self._thoidiemxettinmatac = thoidiem
            khop = MAUTINBANDOMATAC.search(unicodedata.normalize("NFC", noidung or ""))
            if not khop:
                continue
            ids, loi = tachbandomatac(khop.group(1))
            if not ids:
                self._logmt(f"Tin hệ thống không đọc được bản đồ: {noidung!r}")
                continue
            chuoi = ", ".join(laytenbando(i) for i in ids)
            if chuoi != self._matac_bandos:
                self._logmt(f"Tin hệ thống: Mã Tặc xuất hiện tại {chuoi}" + (f" (không nhận ra: {', '.join(loi)})" if loi else ""))
                self.thietlap_bandomatac(chuoi)
            if self._is_tubatmatac and not self._matac:
                if self._is_bantubatmatac():
                    self._logmt("Có tin Mã Tặc nhưng đang làm việc khác, không tự bật")
                else:
                    self.batdau_matac()

    # --- Vòng chính ------------------------------------------------------------------------------------------------------------------
    def _xulymatac(self):
        # Gọi thay lộ trình điểm đánh khi đang đánh Mã Tặc -> yêu cầu di chuyển hoặc None
        s = self._matac
        moitruong = self.moitruong
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logmt(s["trangthai"])
        s["chedo"] = "dichuyen"
        if moitruong.get_is_nhanvatdachet() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0 or moitruong.get_is_dangvankhi():
            return None
        if time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.:
            return None
        idbando = moitruong.get_idbandohientai()
        tengame = moitruong.get_tenbandogame()
        # Vào phó bản: bản đồ / tên bản đồ game khác chỗ chọn Khiêu chiến, hoặc (phó bản mượn đúng bản đồ đó) thấy Mã Tặc là quái
        if not s["davao"] and s["lucchon"] and s["ngoai"] and tengame \
                and ((idbando, tengame) != s["ngoai"] or self._timdoituongmatac(is_npc = False)[0]):
            s.update(davao = True, lucchon = 0., hoithoai = None, do = None, vitriboss = None, lucvao = time.time(), solanloi = 0)
            self._logmt(f"Đã vào phó bản (bản đồ {idbando} \"{tengame}\")")
        if s["davao"] and (idbando, tengame) == s["ngoai"] and not self._timdoituongmatac(is_npc = False)[0]:
            # Giết xong hệ thống đưa về chỗ cũ (hoặc chết / rớt ra): xong vòng, tìm con khác
            s["sovong"] += 1
            s.update(davao = False, ngoai = None, do = None, hoithoai = None, solandotrong = 0)
            self._logmt(f"Ra khỏi phó bản: xong con thứ {s['sovong']}, tìm con khác")
        if s["davao"]:
            return self._danhmatac(s, idbando)
        return self._timmatac(s, idbando)

    def _danhmatac(self, s, idbando):
        moitruong = self.moitruong
        s["chedo"] = "danhquai"
        self._batdanhquaimatac(s)
        if time.time() - s["lucvao"] > THOIGIANPHOBANMATACTOIDA:
            self._baomatac(s, f"cham|{s['sovong']}", f"⚠️ Mã Tặc: ở trong phó bản quá {int(THOIGIANPHOBANMATACTOIDA // 60)} phút chưa ra")
        diachi = self._timdoituongmatac(is_npc = False)[0]
        if diachi:
            s["vitriboss"] = moitruong.get_toado(diachi)
        if s["vitriboss"]:
            s["trangthai"] = f"con thứ {s['sovong'] + 1}: đánh {TENMATAC}"
            x, y = s["vitriboss"]
            if not diachi and moitruong.get_khoangcachdiem(x, y) > KHOANGCACHVEMATAC:
                return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}
            return None
        yeucau, is_hetluot = self._ditheodiemmatac(s, idbando, f"con thứ {s['sovong'] + 1}: dò phó bản tìm {TENMATAC}")
        if is_hetluot:
            s["do"] = None
        return yeucau

    def _timmatac(self, s, idbando):
        moitruong = self.moitruong
        bandos = tachbandomatac(self._matac_bandos)[0]
        if not bandos:
            s["trangthai"] = "chưa có bản đồ: nhập trên giao diện hoặc chờ tin hệ thống"
            return None
        if idbando in bandos:
            s["ibando"] = bandos.index(idbando)
        s["ibando"] %= len(bandos)
        bandodich = bandos[s["ibando"]]
        if idbando != bandodich:
            s["trangthai"] = f"tới {laytenbando(bandodich)} tìm {TENMATAC}"
            buoc = self._lapbuocditoibando(bandodich, is_hoithanhphu = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                s["trangthai"] = f"không có đường tới {laytenbando(bandodich)}: {buoc['mota']}, sang bản đồ kế"
                s["ibando"] += 1
                return None
            return self._thuchienbuocditoibando(buoc, bandodich, None, f"[MÃ TẶC] Tới {laytenbando(bandodich)}")
        now = time.time()
        if s["lucchon"]:
            # Đã chọn Khiêu chiến: chờ hệ thống đưa vào phó bản
            if now - s["lucchon"] < THOIGIANCHOVAOMATAC:
                s["trangthai"] = f"đã chọn Khiêu chiến, chờ được đưa vào phó bản ({int(now - s['lucchon'])}s)"
                return None
            s["solanloi"] += 1
            idnpc = (s["hoithoai"] or {}).get("id") or s.get("idchon")
            s.update(lucchon = 0., ngoai = None, hoithoai = None)
            if s["solanloi"] >= SOLANTHUVAOMATAC:
                s["solanloi"] = 0
                if idnpc:
                    s["boqua"][idnpc] = now + BOQUAMATAC
                self._logmt(f"Chọn Khiêu chiến {SOLANTHUVAOMATAC} lần không được đưa vào phó bản: bỏ qua con này {BOQUAMATAC:.0f}s")
            else:
                self._logmt(f"Chọn Khiêu chiến {THOIGIANCHOVAOMATAC:.0f}s chưa được đưa vào phó bản, nói chuyện lại (lần {s['solanloi'] + 1})")
        h = s["hoithoai"]
        diachinpc, idnpc = self._timdoituongmatac(h["id"] if h else 0, is_npc = True)
        if not diachinpc:
            s["hoithoai"] = None
            yeucau, is_hetluot = self._ditheodiemmatac(s, idbando, f"dò {laytenbando(idbando)} tìm {TENMATAC}", is_timnpc = True)
            if is_hetluot:
                # Dò hết bản đồ này không thấy: sang bản đồ kế; hết cả danh sách SOLANDOTRONGMATAC lượt thì dừng
                s["ibando"] = (s["ibando"] + 1) % len(bandos)
                s["do"] = None
                if s["ibando"] == 0:
                    s["solandotrong"] += 1
                    if s["solandotrong"] >= SOLANDOTRONGMATAC:
                        self._ketthucmatac(f"Dò {SOLANDOTRONGMATAC} lượt mọi bản đồ không còn {TENMATAC}, dừng")
                        return None
                self._logmt(f"Dò hết {laytenbando(idbando)} không thấy {TENMATAC}, sang {laytenbando(bandos[s['ibando']])}")
            return yeucau
        s["solandotrong"] = 0
        s["trangthai"] = f"con thứ {s['sovong'] + 1}: nói chuyện {TENMATAC} (id {idnpc:x})"
        # Chỉ Khiêu chiến được khi ở nhóm 1 người: lo nhóm trong lúc đi tới, tới nơi mà chưa xong thì đứng chờ
        if not self._is_nhommotnguoimatac(s) and moitruong.get_khoangcach(diachinpc) <= KHOANGCACHNOICHUYENMATAC:
            return None
        ketqua, yeucau = self._noichuyenmatac(s, diachinpc, idnpc)
        if ketqua == "xong":
            s.update(lucchon = time.time(), ngoai = (idbando, self.moitruong.get_tenbandogame()), idchon = idnpc)
            self._logmt("Đã chọn \"1. Khiêu chiến\", chờ được đưa vào phó bản")
        elif ketqua == "tuchoi":
            s["boqua"][idnpc] = time.time() + BOQUAMATAC
        return yeucau

    def _is_nhommotnguoimatac(self, s):
        # Đang ở nhóm chỉ có mình (làm trưởng nhóm) -> True; chưa thì rời nhóm có người khác / lập nhóm 1 người "team + <ID mình>", -> False
        moitruong = self.moitruong
        idtoi = moitruong.get_idnguoichoi()
        now = time.time()
        if moitruong.get_is_dangnamtrongnhom():
            ids = [i for i in moitruong.get_danhsachidnguoichoithanhviennhoms() or () if i]
            if moitruong.get_is_truongnhom() and all(i == idtoi for i in ids):
                return True
            s["trangthai"] = "rời nhóm có người khác để lập nhóm 1 người"
            if now - s.get("lucnhom", 0.) > GIANCACHLAPNHOMMATAC:
                s["lucnhom"] = now
                self._logmt("Rời nhóm đang có người khác để lập nhóm 1 người")
                moitruong.action_thoatkhoinhom()
            return False
        s["trangthai"] = "lập nhóm 1 người"
        if now - s.get("lucnhom", 0.) > GIANCACHLAPNHOMMATAC:
            s.update(lucnhom = now, dalapnhom = True)
            self._logmt(f"Lập nhóm 1 người (team + {idtoi})")
            moitruong.action_thucthicaulenh(f"team + {idtoi}")
        return False

    def _noichuyenmatac(self, s, diachinpc, idnpc):
        # Tới cạnh đúng con NPC idnpc, "look" -> menu "Ngươi muốn khiêu chiến..." chọn lựa chọn 1 "Khiêu chiến". Menu khác (không có Khiêu
        # chiến: hết lượt / đang bị người khác đánh?) thì bỏ qua con đó. -> (None | "xong" | "tuchoi", yêu cầu di chuyển)
        moitruong = self.moitruong
        now = time.time()
        h = s["hoithoai"]
        if not h or h["id"] != idnpc:
            h = s["hoithoai"] = {"id": idnpc, "buoc": "look", "luc": 0.}
        if moitruong.get_khoangcach(diachinpc) > KHOANGCACHNOICHUYENMATAC:
            h["buoc"] = "look"
            x, y = moitruong.get_toado(diachinpc)
            return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
        if h["buoc"] == "look":
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {idnpc:x}#")
            h.update(buoc = "chon", luc = now)
            return None, None
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung:
            if now - h["luc"] > THOIGIANCHOMENUMATAC:
                h["buoc"] = "look"
            return None, None
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        self._logmt(f"Menu {TENMATAC}: {noidung[:80]!r} {lenhs}")
        s["hoithoai"] = None
        if LOINPCKHIEUCHIENMATAC not in noidung.lower() or not lenhs:
            moitruong.xoa_noidungcuasotuychon()
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            self._baomatac(s, f"menu|{noidung[:40]}", f"⚠️ Mã Tặc: menu lạ, bỏ qua con này {BOQUAMATAC:.0f}s: {noidung[:120]!r}")
            return "tuchoi", None
        moitruong.action_ngatdichuyen()
        moitruong.xoa_noidungcuasotuychon()
        moitruong.action_thucthicaulenh(lenhs[0])
        self._logmt(f"{TENMATAC}: chọn \"1. Khiêu chiến\" ({lenhs[0]!r})")
        return "xong", None

    def _timdoituongmatac(self, idgiu = 0, is_npc = True):
        # Đoạt Bảo Mã Tặc còn sống trong tầm nhìn -> (địa chỉ, id đối tượng) hoặc (0, 0). is_npc: NPC ngoài bản đồ (bỏ con đang bỏ qua),
        # False: quái trong phó bản. Lấy con idgiu (đang tới) nếu còn thấy, không thì con gần nhất
        moitruong = self.moitruong
        s = self._matac
        canten = chuanhoaten(TENMATAC)
        toado = moitruong.get_toado()
        now = time.time()
        tot = None
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nhanvattontai(diachi) or moitruong.get_is_nguoichoi(diachi) or moitruong.get_is_nhanvatdachet(diachi):
                continue
            if canten not in chuanhoaten(moitruong.get_tendoituong(diachi) or ""):
                continue
            if moitruong.get_is_npc(diachi) != is_npc:
                continue
            iddoituong = moitruong.get_iddoituong(diachi)
            if is_npc and s and s["boqua"].get(iddoituong, 0.) > now:
                continue
            khoangcach = math.dist(toado, moitruong.get_toado(diachi))
            if khoangcach > KHOANGCACHTOANMANHINH:
                continue
            if idgiu and iddoituong == idgiu:
                return diachi, iddoituong
            if not tot or khoangcach < tot[0]:
                tot = (khoangcach, diachi, iddoituong)
        return tot[1:] if tot else (0, 0)

    def _ditheodiemmatac(self, s, idbando, nhan, is_timnpc = False):
        # Đi lần lượt các điểm dò phủ vùng đi được (lưới vật cản, _taodiemdo). Tìm NPC thì chỗ từng thấy NPC đi trước.
        # -> (yêu cầu di chuyển, đã đi hết 1 lượt các điểm)
        moitruong = self.moitruong
        do = s["do"]
        if not do or do["idbando"] != idbando:
            diems = list(self._taodiemdo(idbando))
            vitri = self._sovitri.timnpc(TENMATAC, idbando = idbando) if is_timnpc else None
            if vitri:
                diems.insert(0, tuple(vitri[1:3]))
            if not diems:
                s["trangthai"] = f"{nhan}: chưa đọc được bản đồ"
                return None, False
            toado = moitruong.get_toado()
            i = 0 if vitri else min(range(len(diems)), key = lambda k: math.dist(diems[k], toado))
            do = s["do"] = {"idbando": idbando, "diems": diems, "i": i, "luc": time.time(), "dadi": 0}
            self._logmt(f"{laytenbando(idbando)}: {len(diems)} điểm dò")
        x, y = do["diems"][do["i"]]
        if moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHTOIDIEMMATAC or time.time() - do["luc"] > THOIGIANMOIDIEMMATAC:
            do["dadi"] += 1
            if do["dadi"] >= len(do["diems"]):
                return None, True
            do["i"] = (do["i"] + 1) % len(do["diems"])
            do["luc"] = time.time()
            x, y = do["diems"][do["i"]]
        s["trangthai"] = f"{nhan} (điểm {do['dadi'] + 1}/{len(do['diems'])})"
        self._capnhatbuocdichuyen(f"Mã Tặc: {nhan} (điểm {do['dadi'] + 1}/{len(do['diems'])})")
        return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1., "is_dioo": is_timnpc}, False
