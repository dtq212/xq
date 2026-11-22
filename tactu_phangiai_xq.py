# Give & phân giải (nút "⚒ Give & phân giải" ở tab Khác, 2026-11-18): món khớp luật túi đồ "Phân giải" (luattuido_xq) thì
#   - nhân vật thường ("give"): làm 1 LẦN (người dùng dặn 18/11): tới cạnh người phân giải (trong KHOANGCACHGIVEPHANGIAI ô, give người
#     chơi ~3 ô), gửi 1 lượt lệnh give cho hết các món ("give <ID người chơi> <món>#<số> x6 $0", 6 món / lệnh, như giaodo_xq), chờ
#     THOIGIANKIEMTRAGIVE giây đếm số món đã đi rồi kết thúc, không give lại
#   - người phân giải ("phangiai", tên nhân vật = ô "Người phân giải"): đứng cạnh Chủ Tiệm Sửa Chữa, mỗi GIANCACHPHANGIAI giây gửi
#     "pf4 <id NPC hệ 16>#  6502 <id món hệ 16>#" cho 1 món (bắt từ log Dieu Khac 1041 ngày 18/11: tự bấm phân giải ở "be#" =
#     Chủ Tiệm Sửa Chữa Tân Thủ Thôn, cách nhau 1,5-2s, không có hộp xác nhận). Món gửi SOLANPHANGIAITOIDA lần vẫn còn thì bỏ qua.
#     Chờ đồ give tới: THOIGIANCHODOPHANGIAI giây không có món nào thì xong
# Trong lúc chạy không chọn quái, lộ trình điểm đánh tạm dừng (như giao đồ). Bấm lại nút để huỷ.
# Tự kích hoạt (action_tudongphangiaitheoluat, như luật Vứt, người dùng 18/11): không cần bấm nút, nhân vật nào đứng cách Chủ Tiệm Sửa
# Chữa trong KHOANGCACHNPCPHANGIAI ô mà túi có món khớp luật Phân giải thì tự phân giải từng món (không tự đi tới tiệm, không give)
# Ô trống (người dùng 18/11): phân giải cần ít nhất 2 ô trống, nên trước mỗi món dọn SOOTRONGPHANGIAI ô CUỐI túi 1 ("move <id># to
# <túi 2-4>" sang túi còn hạn còn ô trống, _donochophangiai). Không túi nào còn chỗ / move SOLANDONOTOIDA lần không đi thì báo lỗi
# (log + Telegram) và thôi phân giải (cả tự động lẫn nút) tới khi bấm nút Give & phân giải lại, hoặc (19/11) tự phân giải đếm lại
# thấy hành trang đã đủ chỗ (_xemlailoiphangiai, mỗi THOIGIANXEMLOIPHANGIAI giây)
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._phangiai) khởi tạo trong TacTu.__init__
import json
import os
import sys
import time
import unicodedata

from hangso_xq import *
from giaodo_xq import taolenhgiao
from luattuido_xq import HANHDONG_PHANGIAI, tailuat, is_apdungnhanvat, timluat
from moitruong_xq import DOUUTIEN_KHANCAP
from thongbao_xq import baosuco
from tienich_xq import canhbao

VAITRO_GIVE = "give"
VAITRO_PHANGIAI = "phangiai"
KHOANGCACHGIVEPHANGIAI = 3.
# Đứng cách Chủ Tiệm Sửa Chữa tối đa chừng này ô (Dieu Khac tự bấm khi đứng (108,160), tiệm ở ~(111,157): 3 ô)
KHOANGCACHNPCPHANGIAI = 4.
X_CHUTIEMSUACHUA_TANTHUTHON, Y_CHUTIEMSUACHUA_TANTHUTHON = 111, 157
MAKYNANGPHANGIAI = 6502
GIANCACHPHANGIAI = 1.5
SOLANPHANGIAITOIDA = 3
THOIGIANCHODOPHANGIAI = 90.
SOOTRONGPHANGIAI = 2
SOLANDONOTOIDA = 5
# Đang lỗi hết ô trống: chừng này giây đếm lại hành trang một lần, đủ chỗ thì tự gỡ lỗi
THOIGIANXEMLOIPHANGIAI = 10.
# Give xong chừng này giây thì đếm lại túi xem đã đi bao nhiêu món
THOIGIANKIEMTRAGIVE = 3.
# Không thấy người phân giải quanh mình chừng này giây thì thôi
THOIGIANTIMNGUOIPHANGIAI = 60.
THOIGIANTIMNPCPHANGIAI = 30.


def _bodau(chu):
    # "Diêu Khắc" -> "dieu khac" để so tên gõ không dấu
    chu = unicodedata.normalize("NFD", (chu or "").replace("đ", "d").replace("Đ", "D"))
    return " ".join("".join(c for c in chu if unicodedata.category(c) != "Mn").lower().split())


def _duongdantenphangiai():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "phangiai.json")


def taitenphangiai():
    # Ô "Người phân giải" lần trước (giao diện), "" nếu chưa có
    try:
        with open(_duongdantenphangiai(), encoding = "utf-8") as f:
            return str(json.load(f).get("nguoiphangiai") or "")
    except (OSError, ValueError, AttributeError):
        return ""


def luutenphangiai(ten):
    try:
        with open(_duongdantenphangiai(), "w", encoding = "utf-8") as f:
            json.dump({"nguoiphangiai": str(ten or "").strip()}, f, ensure_ascii = False)
    except OSError as e:
        print(f"[PHÂN GIẢI] Không lưu được tên người phân giải: {e}")


class TacTuPhanGiai:
    def batdau_phangiai(self, nguoiphangiai):
        # Bấm nút: nhân vật này là người phân giải (so tên không dấu / ID) thì phân giải, không thì give cho người đó. Người phân giải
        # đang chạy mà có người khác bấm give tiếp thì chỉ gia hạn chờ đồ (huỷ là lệnh riêng "huyphangiai")
        nguoiphangiai = str(nguoiphangiai or "").strip()
        if not nguoiphangiai:
            return
        moitruong = self.moitruong
        is_toi = _bodau(moitruong.get_tendoituong()) == _bodau(nguoiphangiai) or \
            (nguoiphangiai.isdigit() and int(nguoiphangiai) == moitruong.get_idnguoichoi())
        now = time.time()
        if is_toi and self._loiphangiai:
            self.moitruong._inlog(f"[PHÂN GIẢI] Bấm nút: thử phân giải lại (lỗi trước: {self._loiphangiai})")
            self._loiphangiai = ""
            self._solandonophangiai = 0
        if self._phangiai and self._phangiai["vaitro"] == (VAITRO_PHANGIAI if is_toi else VAITRO_GIVE):
            self._phangiai["lucthaymon"] = now
            return
        self._phangiai = {"vaitro": VAITRO_PHANGIAI if is_toi else VAITRO_GIVE, "nguoiphangiai": nguoiphangiai, "batdau": now,
                          "lucthaymon": now, "lucgui": 0., "truocgive": None, "solangui": {}, "dagive": 0,
                          "daphangiai": 0, "trangthai": "bắt đầu"}
        self.moitruong._inlog(f"[PHÂN GIẢI] {moitruong.get_tendoituong()}: " + ("phân giải đồ ở Chủ Tiệm Sửa Chữa" if is_toi else f"give đồ cho {nguoiphangiai}"))

    def huy_phangiai(self, lydo = ""):
        if self._phangiai:
            p = self._phangiai
            tong = f"đã give {p['dagive']} món" if p["vaitro"] == VAITRO_GIVE else f"đã phân giải {p['daphangiai']} món"
            self.moitruong._inlog(f"[PHÂN GIẢI] Kết thúc ({tong}){': ' + lydo if lydo else ''}")
            self._ketquaphangiai = f"Lần trước: {tong}{' – ' + lydo if lydo else ''} ({time.strftime('%H:%M')})"
        self._phangiai = None

    def get_is_dangphangiai(self):
        return bool(self._phangiai)

    def get_trangthaiphangiai(self):
        p = self._phangiai
        if not p:
            return self._ketquaphangiai or ""
        if p["vaitro"] == VAITRO_GIVE:
            return f"Give cho {p['nguoiphangiai']}: {p['trangthai']} (đã give {p['dagive']})"
        return f"Phân giải: {p['trangthai']} (đã phân giải {p['daphangiai']})"

    def _laymonphangiai(self, tennhanvat = None):
        # [(ô, id đối tượng, tên, số lượng)] các món trong túi khớp luật "Phân giải"; is_chuabiet: có món chưa đọc được mô tả để xét luật.
        # tennhanvat: xét luật như nhân vật này (người give xét theo tên người phân giải: luật Phân giải thường có NV = người phân giải,
        # 18/11 luật "NV: Dieu Khac" làm Thỏ báo "túi không có món nào khớp"); None = theo mình
        moitruong = self.moitruong
        mons, is_chuabiet = [], False
        for vitri in range(moitruong.get_soluongvatphamhanhtrangtoida() + 1):
            iddoituong = moitruong.get_iddoituongvatphamhanhtrang(vitri)
            if not iddoituong or iddoituong <= 0:
                continue
            ten = moitruong.get_tenvatphamhanhtrang(vitri)
            if not ten:
                continue
            if tennhanvat is None:
                hanhdong = self._layhanhdongluat(ten, vitri)
            else:
                luat = timluat(self._chuanhoatenvatpham(ten), lambda t = ten, v = vitri: self._laymotaluat(t, v), tennhanvat = tennhanvat,
                               laymau = lambda t = ten, v = vitri: self._laymautenluat(t, v))
                hanhdong = luat["hanhdong"] if isinstance(luat, dict) else luat
            if hanhdong == "chuabiet":
                is_chuabiet = True
            elif hanhdong == HANHDONG_PHANGIAI and not self._is_catkhovatpham(ten, vitri):
                mons.append((vitri, iddoituong, ten, max(1, moitruong.get_soluongvatphamhanhtrang(vitri) or 1)))
        return mons, is_chuabiet

    def _donochophangiai(self):
        # Dọn SOOTRONGPHANGIAI ô cuối túi 1 trước khi phân giải: True = đã trống, None = đang chuyển / chưa đọc được (lượt sau xem lại),
        # False = không chuyển được (đã báo lỗi, đặt _loiphangiai để thôi phân giải)
        moitruong = self.moitruong
        dem = self._demonophangiai()
        if dem is None:
            return None
        cuois, trongs = dem
        if not cuois:
            self._solandonophangiai = 0
            return True
        if not self._is_duochophangiai(cuois, trongs):
            return self._baoloiphangiai(f"không dọn được {SOOTRONGPHANGIAI} ô cuối hành trang 1 (túi 2-4 hết chỗ: còn "
                                        f"{sum(trongs.values())} ô trống, cần {len(cuois)}; hoặc cả hành trang còn dưới {SOOTRONGPHANGIAI} ô)")
        if self._solandonophangiai >= SOLANDONOTOIDA:
            return self._baoloiphangiai(f"chuyển 2 món cuối hành trang 1 sang túi khác {SOLANDONOTOIDA} lần mà không đi")
        vitri, iddoituong = cuois[0]
        tui = max(trongs, key = trongs.get)
        if moitruong.action_dichuyenvatphamsanghanhtrangkhac(iddoituong, tui + 1, delay = 0.6):
            self._solandonophangiai += 1
            self.moitruong._inlog(f"[PHÂN GIẢI] Dọn ô {vitri} ({moitruong.get_tenvatphamhanhtrang(vitri)}) sang hành trang {tui + 1}")
        return None

    def _demonophangiai(self):
        # ([(ô, id) món đang nằm ở SOOTRONGPHANGIAI ô cuối túi 1], {túi 2-4 còn hạn: số ô trống}); None = chưa đọc được dung lượng túi
        moitruong = self.moitruong
        dungluongs = moitruong.get_dungluongtuihanhtrangs()
        if not dungluongs or dungluongs[0] < SOOTRONGPHANGIAI:
            return None
        cuois = [(vitri, moitruong.get_iddoituongvatphamhanhtrang(vitri)) for vitri in range(dungluongs[0] - SOOTRONGPHANGIAI, dungluongs[0])]
        cuois = [(vitri, iddoituong) for vitri, iddoituong in cuois if iddoituong and iddoituong > 0]
        trongs = {}
        for tui in range(1, len(dungluongs)):
            dungluong = dungluongs[tui]
            if dungluong in DUNGLUONGTUIHETHANs or dungluong <= 0:
                continue
            so = sum(1 for o in range(dungluong) if not moitruong.get_iddoituongvatphamhanhtrang(tui * SOLUONGOMOITUI + o))
            if so:
                trongs[tui] = so
        return cuois, trongs

    def _is_duochophangiai(self, cuois, trongs):
        # Đủ chỗ: ô cuối túi 1 đã trống, hoặc túi 2-4 đủ ô nhận các món đó và cả hành trang còn ≥ SOOTRONGPHANGIAI ô
        if not cuois:
            return True
        return sum(trongs.values()) >= len(cuois) and self.moitruong.get_sootronghanhtrang() >= SOOTRONGPHANGIAI

    def _xemlailoiphangiai(self):
        # 19/11 Dieu Khac báo hết ô trống, người dùng dọn túi rồi mà tự phân giải vẫn đứng (lỗi chỉ gỡ khi bấm nút): mỗi
        # THOIGIANXEMLOIPHANGIAI giây đếm lại, đủ chỗ thì tự gỡ lỗi
        now = time.time()
        if now - self._thoidiemxemloiphangiai < THOIGIANXEMLOIPHANGIAI:
            return
        self._thoidiemxemloiphangiai = now
        dem = self._demonophangiai()
        if dem is None or not self._is_duochophangiai(*dem):
            return
        self.moitruong._inlog(f"[PHÂN GIẢI] Hành trang đã có chỗ, phân giải lại (lỗi trước: {self._loiphangiai})")
        self._loiphangiai = ""
        self._solandonophangiai = 0
        self._ketquaphangiai = ""

    def _baoloiphangiai(self, lydo):
        self._loiphangiai = lydo
        self.moitruong._inlog(f"[PHÂN GIẢI] ⚠️ Thôi phân giải: {lydo}")
        baosuco(self.moitruong, "vatpham", f"⚒ Thôi phân giải: {lydo}", khoa = "phangiai")
        # 18/11 lỗi chỉ nằm trong log / dòng trạng thái của người phân giải nên người dùng (đang chọn người give) không thấy:
        # đọc lên + ghi tab Cảnh báo
        canhbao(self.moitruong, "Hết ô trống, không phân giải được", is_block = False)
        if self._phangiai:
            self.huy_phangiai(lydo)
        else:
            self._ketquaphangiai = f"Lỗi phân giải: {lydo} (bấm nút để thử lại)"
        return False

    def action_tudongphangiaitheoluat(self):
        # Gọi mỗi vòng loop phụ: đứng cạnh Chủ Tiệm Sửa Chữa + có món khớp luật Phân giải thì gửi pf4 cho 1 món mỗi GIANCACHPHANGIAI giây.
        # Món gửi SOLANPHANGIAITOIDA lần vẫn còn thì bỏ qua (tới khi bot khởi động lại). Đang bấm nút Give & phân giải thì để nút lo
        now = time.time()
        if self._loiphangiai and not self._phangiai:
            self._xemlailoiphangiai()
        if self._phangiai or self._loiphangiai or now - self._thoidiemphangiaitudong < GIANCACHPHANGIAI:
            return
        self._thoidiemphangiaitudong = now
        tennhanvat = self._tennhanvatluattuido()
        if not any(luat["bat"] and luat["hanhdong"] == HANHDONG_PHANGIAI and is_apdungnhanvat(luat, tennhanvat) for luat in tailuat()["luat"]):
            return
        moitruong = self.moitruong
        if self.get_is_dangbanrac() or self._is_dangsapxephanhtrang or moitruong.get_is_nhanvatdachet() or moitruong.get_is_dangvankhi():
            return
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = CHUTIEMSUACHUA)
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHNPCPHANGIAI:
            return
        idnpc = moitruong.get_iddoituong(diachinpc)
        if not idnpc or idnpc <= 0:
            return
        mons, _ = self._laymonphangiai()
        conlai = [m for m in mons if self._solanphangiaitudong.get(m[1], 0) < SOLANPHANGIAITOIDA]
        if not conlai or not self._donochophangiai():
            return
        vitri, idmon, ten, _ = min(conlai, key = lambda m: self._solanphangiaitudong.get(m[1], 0))
        if moitruong.action_thucthicaulenh(f"pf4 {idnpc:x}# {MAKYNANGPHANGIAI} {idmon:x}#", douutien = DOUUTIEN_KHANCAP):
            solan = self._solanphangiaitudong[idmon] = self._solanphangiaitudong.get(idmon, 0) + 1
            self.moitruong._inlog(f"[PHÂN GIẢI] Tự phân giải {ten} (ô {vitri}, còn {len(conlai)} món)" +
                  (f" – gửi {solan} lần chưa mất, bỏ qua" if solan == SOLANPHANGIAITOIDA else ""))

    def _tenluatnguoiphangiai(self, p):
        # Tên để xét luật NV của người phân giải: tên thật trong game khi đã thấy người đó (gõ không dấu / ID vẫn khớp NV), không thì chữ gõ
        if not p.get("tenthat"):
            diachi = self._timnguoiphangiai(p["nguoiphangiai"])
            if diachi:
                p["tenthat"] = self.moitruong.get_tendoituong(diachi) or ""
        return p.get("tenthat") or p["nguoiphangiai"]

    def _timnguoiphangiai(self, nguoiphangiai):
        moitruong = self.moitruong
        if nguoiphangiai.isdigit():
            return moitruong.action_timkiemnhanvat(idnguoichoi = int(nguoiphangiai))
        diachi = moitruong.action_timkiemnhanvat(tennhanvat = nguoiphangiai)
        if diachi:
            return diachi
        # Gõ không dấu / khác hoa thường: so tên bỏ dấu trong số người chơi quanh mình
        can = _bodau(nguoiphangiai)
        i = 0
        while True:
            diachi = moitruong.get_diachicosothongtindoituongx(i)
            if not diachi:
                return False
            i += 1
            if moitruong.get_is_nhanvattontai(diachi) and moitruong.get_is_nguoichoi(diachi) and _bodau(moitruong.get_tendoituong(diachi)) == can:
                return diachi

    def _xulyphangiai(self):
        # Gọi thay lộ trình điểm đánh khi đang Give & phân giải -> yêu cầu di chuyển hoặc None
        p = self._phangiai
        if not p:
            return None
        moitruong = self.moitruong
        if moitruong.get_is_nhanvatdachet() or moitruong.get_is_dangvankhi() or self.get_is_danghoithoainpc():
            return None
        if p["vaitro"] == VAITRO_GIVE:
            return self._xulygivephangiai(p)
        return self._xulyphangiaitaicho(p)

    def _xulygivephangiai(self, p):
        moitruong = self.moitruong
        now = time.time()
        if p["lucgui"]:
            # Đã give 1 lượt: chờ túi cập nhật, đếm số món đã đi rồi kết thúc (làm 1 lần, không give lại)
            if now - p["lucgui"] < THOIGIANKIEMTRAGIVE:
                return None
            mons, _ = self._laymonphangiai(self._tenluatnguoiphangiai(p))
            p["dagive"] = max(0, p["truocgive"] - sum(m[3] for m in mons))
            if not p["dagive"]:
                self.huy_phangiai(f"give mà đồ không giảm (đồ khoá / {p['nguoiphangiai']} đầy túi / ở xa?)")
            else:
                self.huy_phangiai("xong" + (f", còn {len(mons)} món chưa đi (đồ khoá / {p['nguoiphangiai']} đầy túi?)" if mons else ""))
            return None
        mons, is_chuabiet = self._laymonphangiai(self._tenluatnguoiphangiai(p))
        if is_chuabiet:
            # Chờ đọc xong mô tả mọi món rồi mới give (kẻo sót món có luật theo loại / mô tả)
            p["trangthai"] = "đang đọc mô tả đồ trong túi"
            return None
        if not mons:
            self.huy_phangiai("túi không có món nào khớp luật Phân giải (tab Hành trang)")
            return None
        diachi = self._timnguoiphangiai(p["nguoiphangiai"])
        if not diachi:
            if now - p["batdau"] > THOIGIANTIMNGUOIPHANGIAI:
                self.huy_phangiai(f"không thấy {p['nguoiphangiai']} quanh mình")
                return None
            p["trangthai"] = f"tìm {p['nguoiphangiai']} quanh mình"
            return None
        if moitruong.get_khoangcach(diachi) > KHOANGCACHGIVEPHANGIAI:
            p["trangthai"] = "lại gần"
            x, y = moitruong.get_toado(diachi)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()),
                    "khoangcachtoida": KHOANGCACHGIVEPHANGIAI - 1}
        moitruong.action_ngatdichuyen()
        idnguoinhan = moitruong.get_idnguoichoi(diachi)
        if not idnguoinhan or idnguoinhan <= 0:
            return None
        for lenh in taolenhgiao(str(idnguoinhan), [(m[1], m[3]) for m in mons], 0):
            moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_KHANCAP)
        self.moitruong._inlog(f"[PHÂN GIẢI] Give {len(mons)} món cho {p['nguoiphangiai']}: " + ", ".join(m[2] for m in mons))
        p["truocgive"] = sum(m[3] for m in mons)
        p["lucgui"] = now
        p["trangthai"] = f"đã gửi give {len(mons)} món, đang kiểm tra"
        return None

    def _xulyphangiaitaicho(self, p):
        moitruong = self.moitruong
        now = time.time()
        mons, is_chuabiet = self._laymonphangiai()
        # Bỏ món đã gửi đủ số lần mà vẫn còn (máy chủ không cho phân giải món đó)
        conlai = [m for m in mons if p["solangui"].get(m[1], 0) < SOLANPHANGIAITOIDA]
        # Món vừa phân giải xong (không còn trong túi): đếm
        for idmon in [i for i in p["solangui"] if i not in {m[1] for m in mons}]:
            p["solangui"].pop(idmon)
            p["daphangiai"] += 1
        if conlai or is_chuabiet:
            p["lucthaymon"] = now
        if not conlai:
            if now - p["lucthaymon"] > THOIGIANCHODOPHANGIAI:
                bo = len(mons)
                self.huy_phangiai(f"{int(THOIGIANCHODOPHANGIAI)}s không có đồ mới" + (f", {bo} món không phân giải được" if bo else ""))
                return None
            p["trangthai"] = f"chờ đồ give tới ({int(THOIGIANCHODOPHANGIAI - (now - p['lucthaymon']))}s)"
            return None
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = CHUTIEMSUACHUA)
        if not diachinpc:
            if moitruong.get_idbandohientai() == BANDO_TANTHUTHON and \
                    moitruong.get_khoangcachdiem(X_CHUTIEMSUACHUA_TANTHUTHON, Y_CHUTIEMSUACHUA_TANTHUTHON) > KHOANGCACHNPCPHANGIAI:
                p["trangthai"] = f"đi tới {CHUTIEMSUACHUA}"
                return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (X_CHUTIEMSUACHUA_TANTHUTHON, Y_CHUTIEMSUACHUA_TANTHUTHON, BANDO_TANTHUTHON),
                        "khoangcachtoida": KHOANGCACHNPCPHANGIAI - 1}
            if now - p["batdau"] > THOIGIANTIMNPCPHANGIAI and not p["daphangiai"]:
                self.huy_phangiai(f"không thấy {CHUTIEMSUACHUA} (đứng cạnh tiệm ở Tân Thủ Thôn rồi bấm lại)")
                return None
            p["trangthai"] = f"tìm {CHUTIEMSUACHUA}"
            return None
        if moitruong.get_khoangcach(diachinpc) > KHOANGCACHNPCPHANGIAI:
            p["trangthai"] = f"lại gần {CHUTIEMSUACHUA}"
            x, y = moitruong.get_toado(diachinpc)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()),
                    "khoangcachtoida": KHOANGCACHNPCPHANGIAI - 1}
        if now - p["lucgui"] < GIANCACHPHANGIAI:
            return None
        idnpc = moitruong.get_iddoituong(diachinpc)
        if not idnpc or idnpc <= 0:
            return None
        moitruong.action_ngatdichuyen()
        if self._loiphangiai:
            self.huy_phangiai(self._loiphangiai)
            return None
        if not self._donochophangiai():
            p["lucgui"] = now
            p["trangthai"] = f"dọn {SOOTRONGPHANGIAI} ô cuối hành trang 1"
            return None
        # Món gửi ít lần nhất trước (món lỗi không chặn món sau)
        vitri, idmon, ten, _ = min(conlai, key = lambda m: p["solangui"].get(m[1], 0))
        lenh = f"pf4 {idnpc:x}# {MAKYNANGPHANGIAI} {idmon:x}#"
        if moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_KHANCAP):
            p["solangui"][idmon] = p["solangui"].get(idmon, 0) + 1
            p["lucgui"] = now
            p["trangthai"] = f"phân giải {ten} (còn {len(conlai)} món)"
            if p["solangui"][idmon] == SOLANPHANGIAITOIDA:
                self.moitruong._inlog(f"[PHÂN GIẢI] {ten} (ô {vitri}) gửi {SOLANPHANGIAITOIDA} lần chưa mất, bỏ qua")
        return None
