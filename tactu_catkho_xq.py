# Cất kho: món trong túi khớp bảng Cất kho (luattuido_xq "catkho") đem gửi Quản Khố ở Tân Thủ Thôn (X_QUANKHO_TANTHUTHON, ...).
# Chạy sau mỗi lần về bán rác (bước sau sửa đồ của _xulydangbanrac, nếu bật "is_catkhosauban") và khi bấm tay / Telegram (/catkho):
# về Tân Thủ Thôn như giao đồ, trong lúc đó không chọn quái, lộ trình điểm đánh tạm dừng.
# Túi Càn Khôn hết hạn còn đồ: luồng về bán rác tự về (_is_canvecatkhotuihethan) và bước cất kho cất hết đồ trong túi đó (rương tự động),
# kể cả khi tắt "Tự cất sau bán rác"; cất tay cũng kèm đồ túi hết hạn.
# Lệnh game (7e# = id đối tượng Quản Khố hệ 16, tìm theo tên):
# Lệnh tay khi đang ở Chu Quốc: cất luôn ở Quản Khố Chu Quốc (X_KHO_CHU, Y_KHO_CHU), không Hồi Thành Phù về Tân Thủ Thôn.
#   mở rương  : pawn 7e# <rương>                        (rương từ 1)
#   cất vào   : pawn + 7e# <id món>#<số lượng> <ô rương>   (ô từ 1; ô đang có cùng món thì gộp chồng; số lượng nhỏ hơn chồng = cất 1 phần)
# Đọc rương đang mở bằng moitruong.get_khodangmo (chỉ rương vừa mở có dữ liệu). Mỗi món: cất vào rương luật chỉ định (đầy thì bỏ món
# đó, báo), luật để tự động thì rương đang mở còn chỗ / rương kế, hết rương thì báo kho đầy; trong rương ưu tiên gộp chồng cùng tên,
# không thì ô trống đầu tiên. "Giữ lại" của luật: chừa chừng đó cái (theo tên) trong túi, cất phần còn lại. Gửi xong chờ rồi xem món đã
# rời túi / chồng đã giảm chưa: chưa thì ô đó không gộp được (đầy chồng...) / thử lại, quá SOLANTHUCATKHO lần thì bỏ món đó (đồ khoá...)
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import re
import time
import unicodedata
import uuid
from collections import Counter

from hangso_xq import *
from luattuido_xq import tailuat, HANHDONG_BAN
from moitruong_xq import DOUUTIEN_KHANCAP
from thongbao_xq import baosuco
from tienich_xq import phatam
from tactu_vatpham_xq import cattenhanhtrang

LYDOCATKHO_BANRAC = "banrac"
LYDOCATKHO_LENHTAY = "lenhtay"
# Kéo cấp xong: acc chính cất sách "Nhập Môn" thu hồi từ acc gà (tactu_keocap_xq._catsachthuhoikc), việc giữ trong trạng thái kéo cấp
LYDOCATKHO_KEOCAP = "keocap"
KHOANGCACHQUANKHO = 3.
# Săn Tinh Anh: bán đồ trắng ở Chủ Tiệm Tạp Hóa trước khi cất kho, quá chừng này giây chưa xong thì bỏ bán
THOIGIANBANTRANGTINHANHTOIDA = 90.
# Bán đồ trắng Săn Tinh Anh: mỗi lượt desc tối đa chừng này ô có mô tả chưa khớp tên (không chờ); gửi xong chừng này giây chưa có mô tả
# thì gửi lại, tối đa SOLANDESCTRANGTINHANH lần rồi chừa món đó (như bán rác Phong Yêu Kính)
SODESCTRANGTINHANHMOILUOT = 3
THOIGIANCHODESCTRANGTINHANH = 3.
SOLANDESCTRANGTINHANH = 3
# Xét từ ô đầu hành trang: 6 ô dòng đầu không còn là ô dùng nhanh phải chừa (người dùng 16/11 bỏ, từng bỏ qua từ 29/10)
VITRICATKHODAUTIEN = 0
GIANCACHBUOCCATKHO = 0.5
# Gửi lệnh mở rương xong chờ chừng này giây cho game nạp dữ liệu rương; mở chừng ấy lần không thấy đổi rương thì bỏ
THOIGIANCHOMORUONG = 1.5
SOLANMORUONG = 3
# Sắp xếp kho: mở rương 3 lần (cách 1.5s) không được thì dừng cả việc => lag mạng 4-5s là đứt (364 2026-11-24 22:38 dừng ở rương 6
# sau 169 lệnh chuyển). Cho mở nhiều lần hơn
SOLANMORUONGSAPXEP = 6
# Sắp xếp kho qua hành trang (_buocxepquatui): gửi lệnh pawn - / + xong chừng này giây chưa thấy túi đổi thì gửi lại, chừng ấy lần thì bỏ
# ô / món đó; cách tối thiểu giữa 2 lệnh (lệnh trước đã có kết quả); số lượt quét kiểm tra - làm lại tối đa; số ô trống túi tối thiểu
THOIGIANCHOLENHQUATUI = 1.
SOLANLENHQUATUI = 3
GIANCACHLENHQUATUI = 0.05
SOLUOTQUATUITOIDA = 3
SOOTRONGTUIQUATUI = 2
# "pawn +" có ghi ô rương: máy chủ chỉ nhận khi cách lần "pawn +" được nhận trước >= ~1s, sớm hơn là bỏ (359 2026-11-25 22:57: 169
# lệnh, "pawn -" 0 lần hỏng dù cách 0.15s; "pawn +" cách lần nhận trước < 1s hỏng ~60%, >= 1.01s gần như luôn ăn; mở rương ngay sau
# "pawn +" cũng hỏng 5/7). Nên chờ đủ chừng này giây mới gửi (trong lúc chờ vẫn rút món khác ra túi), mở rương cũng chờ.
# Ctrl + chuột trái của client gửi "pawn + <mã> <id>#<số>" không ghi ô (log tay 1041: 4 lệnh trong 0.5s) => vào ô trống đầu thì
# dùng dạng đó, thống kê ghi log để xem có thoát giới hạn 1s không
GIANCACHDATOQUATUI = 1.02
# Gửi lệnh cất xong chừng này giây thì xem món đã rời túi chưa
THOIGIANKIEMTRACATKHO = 1.5
SOLANTHUCATKHO = 3
# Quá lâu (kẹt đường, không thấy Quản Khố...) thì bỏ, báo lỗi
THOIGIANCATKHOTOIDA = 300.
THOIGIANCATKHOLENHTAYTOIDA = 600.
# Lịch sử cất kho giữ chừng này giây (báo cáo định kỳ Telegram chỉ cần từ kỳ trước, tối đa vài giờ)
THOIGIANGIULICHSUCATKHO = 24 * 3600.
# Túi Càn Khôn hết hạn còn đồ: về Tân Thủ Thôn (theo quy trình về bán rác) cất hết vào kho. Xét lại mỗi chừng này giây; mỗi lần đã cho về
# thì chừng kia giây sau mới cho về lại (kho đầy / cất hỏng thì khỏi chạy về liên tục)
GIANCACHXETTUIHETHAN = 10.
THOIGIANCHOVECATTUIHETHANLAI = 1800.
# Trước khi cất, chuyển đồ túi hết hạn về túi còn hạn (ưu tiên túi 1) bằng "move <id># to <túi>" mỗi chừng này giây 1 món; chờ chừng
# này giây xem món đã rời túi hết hạn chưa, hỏng chừng ấy lần thì bỏ món đó (để cất kho)
GIANCACHDONTUIHETHAN = 0.6
THOIGIANCHODONTUIHETHAN = 1.5
SOLANDONTUIHETHANTOIDA = 3


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
                "mohinh": {}, "solanloi": {}, "boqua": {}, "dangcho": None, "dacat": {}, "is_damokho": False}

    def _laytengiutuihethan(self):
        # Tên món bot cần dùng, không đem cất kho dù nằm trong túi hết hạn (vẫn dùng được từ túi hết hạn, chuyển về túi còn hạn trước):
        # bảo thú vật phẩm, Bùa Giấy (Mao Sơn: chiêu + Xuyên Không Hành), kỵ thú giữ, món trong bảng Mua bù (thuốc...)
        tens = set(BAOTHUVATPHAMs) | {BUAGIAY} | set(KYTHUGIUs)
        try:
            tens |= {m["vatpham"] for m in self._laymucmuabus()} | {m["vatpham"] for m in self._laymucmuabus(is_tranbaokho = True)}
        except Exception as e:
            print(f"[TÚI HẾT HẠN] Không đọc được bảng Mua bù: {e}")
        return tens

    def _laymontuihethan(self, is_cagiu = False):
        # Chồng nằm trong túi Càn Khôn đã hết hạn (không bỏ thêm đồ vào được, MoiTruong.get_danhsachtuihethan), theo thứ tự ô:
        # [{"vitri", "id", "ten", "soluong", "cat" (cả chồng), "ruong": 0}]. Cất hết, không theo bảng Cất kho / "giữ lại", trừ món cần
        # dùng (_laytengiutuihethan; is_cagiu = lấy cả các món đó)
        moitruong = self.moitruong
        tuihethans = moitruong.get_danhsachtuihethan()
        if not tuihethans:
            return []
        soluongo = (tuihethans[-1] + 1) * SOLUONGOMOITUI
        tens = moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        ids = moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        tengius = set() if is_cagiu else self._laytengiutuihethan()
        mons = []
        for tui in tuihethans:
            for vitri in range(tui * SOLUONGOMOITUI, min((tui + 1) * SOLUONGOMOITUI, len(tens), len(ids))):
                if not ids[vitri] or ids[vitri] <= 0 or not tens[vitri]:
                    continue
                if tens[vitri] in tengius or self._is_kythugiu(tens[vitri]):
                    continue
                soluong = moitruong.get_soluongvatphamhanhtrang(vitri) or 0
                mons.append({"vitri": vitri, "id": ids[vitri], "ten": tens[vitri], "soluong": soluong, "cat": max(1, soluong), "ruong": 0})
        return mons

    def _laycachdontuihethan(self):
        # Lần chuyển kế, None khi không còn gì chuyển được (túi còn hạn hết ô trống thật - không phải sức chứa máy chủ: chuyển chỗ không
        # đổi tổng số món - hoặc túi hết hạn không còn món chưa bỏ):
        #   ("o", id, ô đích từ 0): bảo thú vật phẩm từng ở ô cuối túi hết hạn (con được chọn triệu hồi) đã về túi còn hạn, đưa vào ô mở
        #                           cuối (_get_baothuvatphamocuoi chỉ gọi con ở ô đó)
        #   ("tui", id, túi đích từ 0): chuyển món trong túi hết hạn sang túi còn hạn còn ô trống (túi 1 trước). Món cần dùng
        #                           (_laytengiutuihethan, con bảo thú ô cuối trước hết) chuyển trước
        moitruong = self.moitruong
        tuihethans = moitruong.get_danhsachtuihethan()
        if not tuihethans:
            self._idbaothuocuoituihethan = 0
            return None
        vitrimos = moitruong.get_danhsachvitrimohanhtrang()
        soluongo = max(vitrimos[-1] + 1, (tuihethans[-1] + 1) * SOLUONGOMOITUI)
        ids = moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        tens = moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        if len(ids) < soluongo or len(tens) < soluongo:
            return None
        vitrihethans = [vitri for tui in tuihethans for vitri in range(tui * SOLUONGOMOITUI, (tui + 1) * SOLUONGOMOITUI)]
        # Ô mở cuối cũ (trước khi hết hạn) là ô cuối của túi hết hạn cuối cùng: bảo thú vật phẩm ở đó là con đang được chọn
        ocuoicu = vitrihethans[-1]
        if ocuoicu > vitrimos[-1] and ids[ocuoicu] and tens[ocuoicu] in BAOTHUVATPHAMs:
            self._idbaothuocuoituihethan = ids[ocuoicu]
        idbaothu = self._idbaothuocuoituihethan
        if idbaothu and idbaothu in ids and ids.index(idbaothu) not in vitrihethans:
            vitri, ocuoi = ids.index(idbaothu), vitrimos[-1]
            if vitri == ocuoi or idbaothu in self._iddontuihethanloi:
                self._idbaothuocuoituihethan = 0
            elif vitri // SOLUONGOMOITUI == ocuoi // SOLUONGOMOITUI:
                return "o", idbaothu, ocuoi
            elif any(not ids[o] for o in vitrimos if o // SOLUONGOMOITUI == ocuoi // SOLUONGOMOITUI):
                return "tui", idbaothu, ocuoi // SOLUONGOMOITUI
        # Túi đích: túi còn hạn đầu tiên còn ô trống (túi 1 trước)
        tuidich = next((vitri // SOLUONGOMOITUI for vitri in vitrimos if not ids[vitri]), None)
        if tuidich is None:
            return None
        tengius = self._laytengiutuihethan()
        ungviens = [vitri for vitri in vitrihethans if ids[vitri] and ids[vitri] > 0 and ids[vitri] not in self._iddontuihethanloi]
        if not ungviens:
            return None
        vitri = min(ungviens, key = lambda v: (ids[v] != idbaothu, not (tens[v] in tengius or self._is_kythugiu(tens[v])), v))
        return "tui", ids[vitri], tuidich

    def action_dontuihethan(self):
        # LoopPhu: chuyển dần đồ trong túi Càn Khôn hết hạn về túi còn hạn còn ô trống (ưu tiên túi 1), mỗi lần 1 món; phần không còn
        # chỗ thì về cất kho (_is_canvecatkhotuihethan / bước cất kho). Lệnh "move <id># to <túi>" rơi vào ô trống đầu của túi đích
        now = time.time()
        if now - self._thoidiemdontuihethan < GIANCACHDONTUIHETHAN:
            return
        self._thoidiemdontuihethan = now
        moitruong = self.moitruong
        if self._is_dangsapxephanhtrang or moitruong.get_is_nhanvatdachet() or (self._catkho and self._catkho.get("dangcho")):
            return
        dangchuyen = self._dontuihethan
        if dangchuyen:
            if now - dangchuyen["luc"] < THOIGIANCHODONTUIHETHAN:
                return
            self._dontuihethan = None
            # Thành công khi món đã rời ô cũ (đúng id ở đúng ô lúc gửi là chưa chuyển)
            ids = moitruong._docdanhsachidvatphamhanhtrang(moitruong.get_soluongvatphamhanhtrangtoida() + 1)
            if dangchuyen["vitri"] < len(ids) and ids[dangchuyen["vitri"]] == dangchuyen["id"]:
                solan = self._solandontuihethanloi.get(dangchuyen["id"], 0) + 1
                self._solandontuihethanloi[dangchuyen["id"]] = solan
                print(f"[TÚI HẾT HẠN] {dangchuyen['ten']} chưa rời ô {dangchuyen['vitri'] + 1} sau lệnh chuyển (lần {solan})")
                if solan >= SOLANDONTUIHETHANTOIDA:
                    self._iddontuihethanloi.add(dangchuyen["id"])
                    print(f"[TÚI HẾT HẠN] Bỏ chuyển {dangchuyen['ten']}")
            return
        cach = self._laycachdontuihethan()
        if not cach:
            return
        kieu, iddoituong, dich = cach
        ids = moitruong._docdanhsachidvatphamhanhtrang(moitruong.get_soluongvatphamhanhtrangtoida() + 1)
        if iddoituong not in ids:
            return
        vitri = ids.index(iddoituong)
        ten = moitruong.get_tenvatphamhanhtrang(vitri) or ""
        if kieu == "o":
            is_ok = moitruong.action_dichuyenvatphamhanhtrang(iddoituong, dich + 1, delay = 0.)
            mota = f"vào ô mở cuối {dich + 1} (bảo thú được chọn triệu hồi)"
        else:
            is_ok = moitruong.action_dichuyenvatphamsanghanhtrangkhac(iddoituong, dich + 1, delay = 0.)
            mota = f"về hành trang {dich + 1}"
        if is_ok:
            print(f"[TÚI HẾT HẠN] Chuyển {ten} (ô {vitri + 1}) {mota}")
            self._dontuihethan = {"id": iddoituong, "ten": ten, "vitri": vitri, "luc": now}

    def _is_dangdontuihethan(self):
        # Còn món túi hết hạn chuyển được về túi còn hạn (đang chuyển dở hoặc chưa chuyển): cất kho đồ túi hết hạn phải chờ
        return bool(self._dontuihethan) or self._laycachdontuihethan() is not None

    def _is_canvecatkhotuihethan(self):
        # Luồng về bán rác (tactu_vatpham_xq._is_canve): túi hết hạn còn món cất được thì về, tới bước cất kho sẽ cất hết các món đó.
        # Còn chuyển được về túi còn hạn thì chuyển trước (action_dontuihethan), chưa về
        now = time.time()
        if now < self._thoidiemxetcatkhotuihethan or self._is_dangdontuihethan():
            return False
        self._thoidiemxetcatkhotuihethan = now + GIANCACHXETTUIHETHAN
        mons = [m for m in self._laymontuihethan() if m["ten"] not in self._tenkhongcattuihethan]
        if not mons:
            return False
        self._thoidiemxetcatkhotuihethan = now + THOIGIANCHOVECATTUIHETHANLAI
        print(f"[CẤT KHO] Túi Càn Khôn hết hạn còn {len(mons)} món ({', '.join(sorted({m['ten'] for m in mons})[:5])}...), về Tân Thủ Thôn cất kho")
        return True

    def _laymoncatkho(self, tientos = None, is_chituihethan = False, mamaus = (), tenboquas = ()):
        # Chồng trong túi cần cất theo bảng Cất kho, theo thứ tự ô: [{"vitri", "id", "ten", "soluong" (của chồng, 0 = không chồng được),
        # "cat" (số cất từ chồng này), "ruong" (0 = tự động)}]. Tính theo tên: tổng trong túi trừ "giữ lại" của luật, lấy dần từ ô đầu
        # (chồng cuối có thể chỉ cất 1 phần). Luật cần mô tả mà chưa đọc được thì bỏ qua lượt này
        # tientos (việc cất riêng, vd kéo cấp cất sách "Nhập Môn"): bỏ bảng Cất kho, cất hết món có tên bắt đầu bằng 1 trong các tiền tố
        # (không phân biệt hoa thường), rương tự động; trừ món có tên trong tenboquas (tên đầy đủ, so theo tên cắt 31 byte như ô hành trang)
        # Không có tientos thì luôn cất thêm cả chồng trong túi hết hạn (_laymontuihethan, bảng Cất kho chỉ xét các túi còn hạn);
        # is_chituihethan (việc tạo vì túi hết hạn khi tắt "Tự cất sau bán rác"): chỉ cất đồ túi hết hạn
        # mamaus (việc của Săn Tinh Anh, viec["mamaus"]): CHỈ cất trang bị tên màu này (_is_cattheomau), bỏ bảng Cất kho (người dùng
        # 16/11: lúc săn về cất mà cất cả món không phải Lam Kim). Đồ túi hết hạn vẫn cất (không dùng được, chiếm chỗ)
        if tientos:
            return self._laymoncatkhotheoluat(tientos, tenboquas = tenboquas)
        # Còn chuyển được về túi còn hạn thì chưa cất đồ túi hết hạn (action_dontuihethan chuyển trước, _buoccatkho chờ)
        montuihethans = [] if self._is_dangdontuihethan() else self._laymontuihethan()
        if is_chituihethan:
            return montuihethans
        mons = self._laymoncatkhotheoluat(vitriboquas = {m["vitri"] for m in montuihethans}, mamaus = mamaus)
        return sorted(mons + montuihethans, key = lambda m: m["vitri"])

    def _laymoncatkhotheoluat(self, tientos = None, vitriboquas = (), mamaus = (), tenboquas = ()):
        # vitriboquas: ô không xét theo luật (đồ túi hết hạn, cất riêng cả chồng), "giữ lại" chỉ tính trên các ô còn lại
        moitruong = self.moitruong
        layluat = self._layluatcatkho
        if mamaus and not tientos:
            luatmau = {"ruong": 0, "giulai": 0}

            def layluat(ten, vitri):
                return luatmau if self._is_cattheomau(ten, vitri, mamaus) else None
        if tientos:
            tientos = tuple(unicodedata.normalize("NFC", t).lower() for t in tientos)
            luatrieng = {"ruong": 0, "giulai": 0}

            tenboquas = {unicodedata.normalize("NFC", cattenhanhtrang(t)).lower() for t in tenboquas}

            def layluat(ten, vitri):
                ten = unicodedata.normalize("NFC", ten).strip().lower()
                return luatrieng if ten.startswith(tientos) and ten not in tenboquas else None
        soluongo = moitruong.get_soluongvatphamhanhtrangtoida() + 1
        tens = moitruong._docdanhsachtenvatphamhanhtrang(soluongo)
        ids = moitruong._docdanhsachidvatphamhanhtrang(soluongo)
        nhoms = {}
        for vitri in range(VITRICATKHODAUTIEN, min(len(tens), len(ids))):
            if not ids[vitri] or ids[vitri] <= 0 or not tens[vitri] or vitri in vitriboquas:
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

    def _is_cattheomau(self, ten, vitri, mamaus):
        # Săn Tinh Anh cất đồ rơi (Lam Kim) không cần luật trong bảng Cất kho. Chỉ việc của Săn Tinh Anh dùng: luật chung "Màu tên" sẽ
        # chặn bán rác Phong Yêu Kính bán bớt Lam Kim / kéo cấp give đồ Lam Kim (tactu_langlyson_xq: món khớp Cất kho không bán).
        # Bỏ món bot cần dùng (bảo thú vật phẩm, Bùa Giấy, kỵ thú giữ, Mua bù), món đã giám định / không phải trang bị và Pháp Bảo (Trảo kéo cấp...);
        # chưa đọc được thì chưa cất
        if self._chuanhoatenvatpham(ten) in self._laytengiutuihethan() or self._is_kythugiu(ten):
            return False
        if self._laymautenluat(ten, vitri) not in mamaus:
            return False
        # Chỉ đồ Lam Kim rơi ra (mô tả có "Chưa giám định", chưa có dòng Độ bền): Tiểu Huyết Thạch / Tiểu Pháp Lực Thạch tên cũng màu
        # Lam Kim mà là vật phẩm dùng, trước bị cất theo (người dùng 16/11)
        mota = self._laymotaluat(ten, vitri)
        if not mota or "chưa giám định" not in unicodedata.normalize("NFC", mota[1] or "").lower():
            return False
        return "pháp bảo" not in unicodedata.normalize("NFC", mota[0] or "").lower()

    def _lydokhongbantrangtinhanh(self, ten, vitri):
        # Trang bị trắng (tên không màu, mô tả có "Độ bền" / "Chưa giám định") Săn Tinh Anh nhặt về bán gỡ vốn (người dùng 16/11). Theo luật túi đồ: chỉ món
        # không khớp luật hoặc luật Bán, không khớp Cất kho; bỏ món bot cần dùng, kỵ thú giữ, Pháp Bảo, đồ có sao. Chưa đọc được thì không bán.
        # -> None = bán, "" = không phải đồ trắng (Lam Kim, vật phẩm...: không cần ghi log), chuỗi khác = lý do chừa món trắng (ghi log)
        if self._chuanhoatenvatpham(ten) in self._laytengiutuihethan() or self._is_kythugiu(ten):
            return ""
        mau = self._laymautenluat(ten, vitri)
        if mau is None:
            return "chưa đọc được màu tên"
        if mau != "":
            return self._lydokhongbanmautinhanh(ten, vitri)
        hanhdong = self._layhanhdongluat(ten, vitri)
        if hanhdong == "chuabiet":
            return "luật túi đồ chưa đọc được mô tả"
        if hanhdong not in (None, HANHDONG_BAN):
            return f"luật túi đồ: {hanhdong}"
        if self._is_catkhovatpham(ten, vitri):
            return "khớp bảng Cất kho"
        # Món trắng không phải trang bị nhặt vì Săn Tinh Anh (vật liệu rác: Tử Giả Di Vật, Khô Đầu Lâu...): bán luôn (người dùng 16/11).
        # Món người dùng cần thì đặt luật Giữ / Cất kho ở tab Hành trang
        if self._chuanhoatenvatpham(ten) not in self._tenractinhanhs:
            # Trang bị: có "Độ bền", hoặc "Chưa giám định" (đồ trắng cấp >= 30 rơi ra cũng chưa giám định, chưa có dòng Độ bền)
            mota = self._laymotaluat(ten, vitri)
            if mota is None:
                return "chưa đọc được mô tả"
            chu = unicodedata.normalize("NFC", mota[1] or "")
            if "Độ bền" not in chu and "chưa giám định" not in chu.lower():
                return ""
            if "pháp bảo" in unicodedata.normalize("NFC", mota[0] or "").lower():
                return ""
        if self._is_dosaokhongban(vitri, ten, is_docmoi = False):
            return "đồ có sao"
        return None

    def _chandoanbantrangtinhanh(self, ten, vitri):
        # Log chẩn đoán cho món _lydokhongbantrangtinhanh bỏ qua không ghi lý do (""). 26/11 Xí Diễm / Xích Kim Giản / Xích Vân Cân Mạo
        # trắng chưa giám định (ảnh người dùng) nhặt từ 06h mà chỉ bán được 1, không nằm trong cả danh sách chừa lẫn bán => không biết nhánh nào
        try:
            mau = self._laymautenluat(ten, vitri)
            luat = self._layluatvatpham(ten, vitri)
            mota = self._laymotaluat(ten, vitri)
        except Exception as e:
            return f"{ten} (ô {vitri}: lỗi chẩn đoán {e})"
        if isinstance(luat, dict):
            luat = f"{luat.get('hanhdong')}/{luat.get('ghichu') or '-'}"
        if mota is None:
            motangan = "chưa đọc"
        else:
            chu = unicodedata.normalize("NFC", mota[1] or "")
            motangan = (f"loại '{mota[0]}', độ bền {'Độ bền' in chu}, chưa GĐ {'chưa giám định' in chu.lower()}, "
                        f"rác {self._chuanhoatenvatpham(ten) in self._tenractinhanhs}, đầu '{chu[:40]}'")
        return f"{ten} (ô {vitri}: màu {mau!r}, luật {luat}, {motangan})"

    def _lydokhongbanmautinhanh(self, ten, vitri):
        # Đồ tên có màu (Lam Kim...) Săn Tinh Anh mặc định không bán (cất kho). 22/11 Quản Khố + hành trang đầy hết chỗ: bán theo luật túi đồ
        # ở tab Hành trang, khỏi thêm tuỳ chọn riêng. CHỈ bán khi luật khớp ĐẦU TIÊN là luật Bán CÓ điều kiện "Màu tên": món tên màu không
        # khớp luật nào vẫn giữ (khác bán rác thường), luật Bán chung không có Màu tên (vd Tên chứa "Kiếm") cũng không tính, kẻo bán nhầm.
        # Giữ cấp đang cần thì đặt luật Giữ phía TRÊN: Màu tên "Lam Kim" + Mô tả chứa "cấp 70" / "cấp 80" (Niết Bàn "70 cấp")
        # -> None = bán, "" = không bán (không ghi log), chuỗi khác = lý do chừa (ghi log)
        luat = self._layluatvatpham(ten, vitri)
        if luat == "chuabiet":
            return "luật túi đồ chưa đọc được mô tả"
        if not isinstance(luat, dict) or luat.get("hanhdong") != HANHDONG_BAN or not luat.get("mau"):
            return ""
        if self._is_catkhovatpham(ten, vitri):
            return "khớp bảng Cất kho"
        mota = self._laymotaluat(ten, vitri)
        if mota is None:
            return "chưa đọc được mô tả"
        if "pháp bảo" in unicodedata.normalize("NFC", mota[0] or "").lower():
            return ""
        if self._is_dosaokhongban(vitri, ten, is_docmoi = False):
            return "đồ có sao"
        return None

    def _is_motaokhopten(self, vitri, ten):
        # Mô tả game đang giữ cho ô vitri là của đúng món này chưa (mô tả theo ô, có thể còn của món trước ở ô đó): dòng đầu khớp tên
        tenchuan = unicodedata.normalize("NFC", re.sub(r"\x1b.", "", ten or "")).strip()
        sach = unicodedata.normalize("NFC", re.sub(r"\x1b.", "", self.moitruong.get_motathovatphamhanhtrangcosan(vitri) or ""))
        dongs = [d.strip() for d in sach.split("\n") if d.strip()]
        return bool(dongs and tenchuan and dongs[0].startswith(tenchuan))

    def _buocbantrangtinhanh(self, viec):
        # 1 bước bán đồ trắng (Săn Tinh Anh) ở Chủ Tiệm Tạp Hóa. viec["banrac"]: "cho" -> "dagui" (lệnh bán đã xếp, action_xulybanracvasuado
        # gửi dần) -> "xong". -> ("dichuyen", x, y) / "dang" / "xong". Quá THOIGIANBANTRANGTINHANHTOIDA giây chưa xong thì bỏ, đi cất kho
        moitruong = self.moitruong
        viec.setdefault("lucbanrac", time.time())
        if viec["banrac"] == "dagui":
            if self.get_is_dangbanrac() or time.time() < self._thoidiemguibanractieptheo:
                return "dang"
            viec["banrac"] = "xong"
            return "xong"
        if time.time() - viec["lucbanrac"] > THOIGIANBANTRANGTINHANHTOIDA:
            moitruong._inlog(f"[CẤT KHO] Săn Tinh Anh: quá {int(THOIGIANBANTRANGTINHANHTOIDA)}s chưa bán xong đồ trắng ở Chủ Tiệm Tạp Hóa, bỏ bán, đi cất kho")
            viec["banrac"] = "xong"
            return "xong"
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = CHUTIEMTAPHOA)
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > 3.:
            if not diachinpc and moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                # Chu Quốc không có tiệm này: thôi bán, cất luôn
                viec["banrac"] = "xong"
                return "xong"
            viec["trangthai"] = f"đang tới {CHUTIEMTAPHOA} bán đồ trắng"
            x, y = moitruong.get_toado(diachinpc) if diachinpc else (X_CHUTIEMTAPHOA_TANTHUTHON, Y_CHUTIEMTAPHOA_TANTHUTHON)
            return "dichuyen", round(x), round(y)
        moitruong.action_ngatdichuyen()
        idnpc = moitruong.get_iddoituong(diachinpc)
        if not idnpc or idnpc <= 0:
            return "dang"
        # Trước đây quét 1 lượt, mỗi ô desc chờ tối đa 1s: ô nào mô tả chưa về kịp (mô tả theo ô còn của món trước, desc chậm) thì món đó bị
        # bỏ cả chuyến và ô đó 60s không desc lại => về bán mà vẫn còn 1 đống đồ trắng (người dùng 19/11). Giờ như bán rác Phong Yêu Kính:
        # desc không chờ các ô chưa khớp tên, chờ đọc đủ rồi mới bán; desc SOLANDESCTRANGTINHANH lần vẫn không được thì chừa, ghi log lý do
        now = time.time()
        dadesc = viec.setdefault("dadesctrang", {})
        lenhs, tens, boquas, imlangs, sodesc, soguidesc = [], [], [], [], 0, 0
        for vitri in range(moitruong.get_soluongvatphamhanhtrangtoida() + 1):
            iddoituong = moitruong.get_iddoituongvatphamhanhtrang(vitri)
            ten = moitruong.get_tenvatphamhanhtrang(vitri) if iddoituong and iddoituong > 0 else None
            if not ten:
                continue
            if not self._is_motaokhopten(vitri, ten):
                lucgui, solan = dadesc.get((vitri, iddoituong), (0., 0))
                if now - lucgui <= THOIGIANCHODESCTRANGTINHANH:
                    sodesc += 1
                elif solan < SOLANDESCTRANGTINHANH:
                    sodesc += 1
                    if soguidesc < SODESCTRANGTINHANHMOILUOT:
                        soguidesc += 1
                        dadesc[(vitri, iddoituong)] = (now, solan + 1)
                        moitruong.get_motavatphamhanhtrang(vitri, thoigianchotoida = 0., is_napmoi = True)
                else:
                    boquas.append(f"{ten} (ô {vitri}: không đọc được mô tả)")
                continue
            lydo = self._lydokhongbantrangtinhanh(ten, vitri)
            if lydo is None:
                lenhs.append(self._lenhbanvatpham(idnpc, iddoituong, self._soluongbanvatpham(vitri)))
                tens.append(ten)
            elif lydo:
                boquas.append(f"{ten} (ô {vitri}: {lydo})")
            else:
                imlangs.append(self._chandoanbantrangtinhanh(ten, vitri))
        if sodesc:
            viec["trangthai"] = f"bán đồ trắng: đọc mô tả hành trang ({sodesc} ô)"
            return "dang"
        if boquas:
            moitruong._inlog(f"[CẤT KHO] Săn Tinh Anh: chừa {len(boquas)} món trắng: " + ", ".join(boquas))
        if imlangs:
            moitruong._inlog(f"[CẤT KHO] Săn Tinh Anh: không bán {len(imlangs)} món (không phải đồ trắng / luật không Bán): " + ", ".join(imlangs))
        moitruong._inlog(f"[CẤT KHO] Săn Tinh Anh: bán {len(lenhs)} món (đồ trắng + đồ màu theo luật Bán) ({', '.join(tens[:10])}{'...' if len(tens) > 10 else ''})")
        if not lenhs:
            viec["banrac"] = "xong"
            return "xong"
        viec["trangthai"] = f"bán {len(lenhs)} món ở {CHUTIEMTAPHOA}"
        self._datnhangdoibanrac(lenhs)
        viec["banrac"] = "dagui"
        return "dang"

    def _chonokho(self, viec, kho, mon):
        # (ô rương từ 0, is_gop, số gửi, (tên, số lượng) ô kho sau khi cất) cho món, (None, False, 0, None) khi rương này không còn chỗ.
        # Gộp chỉ với món xếp chồng được (số lượng > 0) và chồng kho còn chỗ: 1 ô kho cũng chỉ chồng tối đa như hành trang
        # (_get_soluongxepchongtoida, 100). Bản đầu gộp không xét trần => gộp vào chồng 100 bị máy chủ từ chối, 3 lần là bỏ cả món;
        # chồng 70 mà gửi 60 thì máy chủ chỉ nhận 30 cho đủ 100, 30 còn lại ở túi (người dùng xác nhận 2026-11-17). Vẫn gửi đúng số
        # còn chứa được để kiểm tra "đã cất xong" theo số lượng túi khớp, phần dư lượt sau sang chồng / ô trống khác.
        # Dữ liệu rương chỉ làm mới khi mở lại rương => cất xong ghi ô đó vào viec["mohinh"] (đè dữ liệu đọc được), mở lại rương thì xoá
        ruong = kho["ruong"]
        mohinh = viec["mohinh"]
        os = [mohinh.get((ruong, o), (ten, soluong)) for o, (ten, soluong, _) in enumerate(kho["os"])]
        if mon["soluong"] > 0:
            toida = self._get_soluongxepchongtoida(mon["ten"])
            for o, (ten, soluong) in enumerate(os):
                if 0 < soluong < toida and (ruong, o) not in viec["khonggop"] and is_trungtenkho(ten, mon["ten"]):
                    gui = min(mon["cat"], toida - soluong)
                    return o, True, gui, (ten, soluong + gui)
        for o, (ten, _) in enumerate(os):
            if not ten and (ruong, o) not in viec["odadung"]:
                gui = min(mon["cat"], self._get_soluongxepchongtoida(mon["ten"])) if mon["soluong"] > 0 else mon["cat"]
                return o, False, gui, (mon["ten"], gui if mon["soluong"] > 0 else 0)
        return None, False, 0, None

    def _ketthuccatkho(self, viec, loi = None):
        # Báo kết quả (Telegram + log), xoá việc, đóng cửa sổ kho bot đã mở. -> "xong" / "lỗi"
        # Việc cất riêng (kéo cấp cất sách, không nằm ở self._catkho) xong thì đừng xoá việc cất kho khác đang chạy
        if self._catkho is viec or viec.get("lydo") != LYDOCATKHO_KEOCAP:
            self._catkho = None
        if viec["is_damokho"]:
            self.moitruong.action_dongcuasokho()
        # Món trong túi hết hạn thử cất không được (đồ khoá...): thôi không vì nó mà về Tân Thủ Thôn nữa
        if viec["boqua"] and not viec.get("tientos"):
            tenhethans = {m["ten"] for m in self._laymontuihethan()}
            self._tenkhongcattuihethan |= {ten for ten in viec["boqua"] if ten in tenhethans}
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
                viec["mohinh"][(dangcho["ruong"], dangcho["o"])] = dangcho["okho"]
            else:
                viec["solanloi"][dangcho["ten"]] = viec["solanloi"].get(dangcho["ten"], 0) + 1
                (viec["khonggop"] if dangcho["is_gop"] else viec["odadung"]).add((dangcho["ruong"], dangcho["o"]))
                print(f"[CẤT KHO] {dangcho['ten']} chưa rời túi sau lệnh cất (lần {viec['solanloi'][dangcho['ten']]})")
                if viec["solanloi"][dangcho["ten"]] >= SOLANTHUCATKHO:
                    viec["boqua"][dangcho["ten"]] = f"thử {SOLANTHUCATKHO} lần không được, đồ khoá?"
            return "dang"

        mons = [m for m in self._laymoncatkho(viec.get("tientos"), viec.get("is_chituihethan", False), viec.get("mamaus", ()),
                                              viec.get("tenboquas", ()))
                if m["ten"] not in viec["boqua"]]
        if not mons:
            if not viec.get("tientos") and self._is_dangdontuihethan():
                # Đồ túi hết hạn đang được chuyển về túi còn hạn: chờ chuyển xong rồi cất phần còn lại
                viec["trangthai"] = "chờ chuyển đồ túi hết hạn về hành trang"
                return "dang"
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
                # Dữ liệu rương vừa mở là thật: bỏ mô hình cũ của rương này
                viec["mohinh"] = {k: v for k, v in viec["mohinh"].items() if k[0] != viec["ruong"]}
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

        o, is_gop, cat, okho = self._chonokho(viec, kho, mon)
        if o is None:
            # Rương này hết chỗ: lượt sau chọn lại rương (món chỉ định rương này thì bỏ món)
            viec["ruongday"].add(viec["ruong"])
            return "dang"
        viec["trangthai"] = f"cất {mon['ten']} ×{cat} vào rương {viec['ruong']} ô {o + 1}"
        lenh = f"pawn + {manpc} {mon['id']:x}#{cat} {o + 1}"
        print(f"[CẤT KHO] {lenh} ({mon['ten']}{f', gộp chồng thành {okho[1]}' if is_gop else ''})")
        moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_KHANCAP)
        viec["dangcho"] = {"id": mon["id"], "ten": mon["ten"], "soluong": mon["soluong"], "cat": cat, "ruong": viec["ruong"], "o": o,
                           "is_gop": is_gop, "okho": okho, "lucgui": now}
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
                           "quetcu": {}, "dachuyen": [], "dadat": set(),
                           # luctiendo: lần gần nhất có dữ liệu rương / gửi được lệnh (quá THOIGIANKHONGTIENDO giây không có thì dừng);
                           # chamtoi: các rương lượt gom trước có chuyển ra / vào (lượt quét sau chỉ mở lại các rương này), None = quét hết
                           "luctiendo": time.time(), "chamtoi": None,
                           # Xếp qua hành trang (_buocxepquatui): giu = món rút từ kho đang nằm trong túi [{id, ten, sl, ma}], dangcho =
                           # lệnh pawn - / + chờ túi đổi, moden = rương cần mở, khongrut = (rương, ô) rút không được
                           "is_quatui": self.moitruong.get_sootronghanhtrang() >= SOOTRONGTUIQUATUI,
                           "giu": [], "dangcho": None, "moden": 0, "khongrut": set(), "luotquatui": 0, "soquatui": 0,
                           "rdich": 1, "vovan": set(), "dalam": False, "lucbatdauluot": time.time(), "lucdatcuoi": 0.,
                           # thongke: kiểu lệnh ("-", "+ô", "+tựdo") -> [số món xong, số lần phải gửi lại]
                           "thongke": {}}
        # Ngưng desc nhãn ô trong lúc xếp (xem MoiTruong._is_tamdungdescnhan)
        self.moitruong._is_tamdungdescnhan = True
        phatam("Bắt đầu sắp xếp kho")
        print(f"{self.moitruong.get_tendoituong()}: [SẮP XẾP KHO] bắt đầu")

    def get_is_dangsapxepkho(self):
        return bool(self._sapxepkho)

    def _ketthucsapxepkho(self, thongbao):
        viec = self._sapxepkho
        self._sapxepkho = None
        self.moitruong._is_tamdungdescnhan = False
        if viec and viec.get("giu"):
            viec["loi"].append(f"còn {len(viec['giu'])} món rút từ kho đang ở hành trang: {', '.join(m['ten'] for m in viec['giu'][:10])}")
        solenh = viec["solenh"] if viec else 0
        sochuyen = viec["sochuyen"] if viec else 0
        loi = f" | {'; '.join(viec['loi'])}" if viec and viec["loi"] else ""
        if viec and viec.get("soquatui"):
            noidung = f"[SẮP XẾP KHO] {thongbao} (rút / cất qua hành trang {viec['soquatui']} lần: {self._chuoithongkequatui(viec)}){loi}"
        else:
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
        # SOLANMORUONGSAPXEP lần không được
        if viec["canmo"] != ruong or not viec["lucmo"]:
            viec["canmo"], viec["solanmo"] = ruong, 0
            self._moruongsapxepkho(viec, makho, kho, now, ruong = ruong, pha = viec["pha"])
            return None
        if kho and kho["ruong"] == ruong and (kho["os"] != viec["anhmo"] or now - viec["lucmo"] >= thoigiancho):
            viec["lucmo"], viec["canmo"], viec["solanmo"] = 0., 0, 0
            viec["luctiendo"] = now
            return list(kho["os"])
        if now - viec["lucmo"] < thoigiancho:
            return None
        if viec["solanmo"] >= SOLANMORUONGSAPXEP:
            return False
        self._moruongsapxepkho(viec, makho, kho, now, ruong = ruong, pha = viec["pha"])
        return None

    def _buocgomkho(self, viec, makho, kho, now, thoigiancho, soluotgomtoida):
        # 1 bước pha "quet" / "gom"
        moitruong = self.moitruong
        tennv = moitruong.get_tendoituong()
        soruong = max(1, viec["soruong"])
        if viec["pha"] == "quet":
            # Quét lại sau lượt gom: rương lượt trước không chuyển ra / vào món nào thì giữ dữ liệu cũ, khỏi mở (mỗi lần mở ~1-1.5s;
            # 359 2026-11-24 gom 5 lượt, lượt cuối chỉ còn 1-4 món mà lượt nào cũng mở lại cả 5 rương)
            chamtoi = viec["chamtoi"]
            while chamtoi is not None and viec["ruong"] < soruong and viec["ruong"] not in chamtoi and viec["ruong"] in viec["ruongs"]:
                viec["ruong"] += 1
            if chamtoi is not None and viec["ruong"] not in chamtoi and viec["ruong"] in viec["ruongs"]:
                os = viec["ruongs"][viec["ruong"]]
            else:
                os = self._chodulieuruong(viec, makho, kho, now, viec["ruong"], thoigiancho)
                if os is None:
                    return
                if os is False:
                    viec["loi"].append(f"không mở được rương {viec['ruong']}")
                    self._ketthucsapxepkho(f"Dừng sắp xếp kho ở rương {viec['ruong']}")
                    return
                viec["ruongmo"] = viec["ruong"]
            viec["ruongs"][viec["ruong"]] = os
            if viec["ruong"] < soruong:
                viec["ruong"] += 1
                return
            viec["chamtoi"] = None
            viec["ban"] = set()
            dich = self._dichgomkho(viec["ruongs"])
            lech = self._lechgomkho(viec["ruongs"], dich)
            self._kiemchungchuyenruong(viec)
            viec["quetcu"] = {r: list(os) for r, os in viec["ruongs"].items()}
            viec["dachuyen"], viec["dadat"] = [], set()
            trongs = ", ".join(f"r{r} trống {sum(1 for _, _, ma in os if not ma)}" for r, os in sorted(viec["ruongs"].items()))
            # Ước thời gian: mỗi lệnh pawn ~1s (máy chủ chỉ nhận ~1 lệnh/s), gom ~1.3 lệnh / món sai rương (kho ít ô trống thì phải chuyển
            # qua rương trung gian), xếp trong rương tối đa ~1 lệnh / ô sai
            saitrong = sum(sum(1 for a, b in zip(os, self._dichtrongruong(os)) if a[2] != b) for os in viec["ruongs"].values())
            uoc = "" if viec["is_quatui"] else f", ước còn ~{max(1, round((lech * 1.3 + saitrong + 3 * soruong) / 60))} phút"
            self._logsapxepkho(f"đã quét {soruong} rương ({trongs}), {lech} món nằm sai rương (lượt gom {viec['luotgom'] + 1}){uoc}")
            if viec["is_quatui"]:
                self._batdauxepquatui(viec)
                return
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
                viec["lucgui"] = viec["luctiendo"] = now
                viec["sochuyen"] += 1
                viec["solenhgom"] += 1
                viec["chuyenvong"] += 1
            return

        dich, dem, trong = viec["dich"], viec["dem"], viec["trong"]
        r = viec["rdich"]
        if r > soruong:
            # Gom xong mọi rương theo mô hình: quét lại kiểm tra (lệnh có thể bị bỏ), chỉ các rương lượt này có chuyển ra / vào
            viec["pha"], viec["ruong"], viec["lucmo"], viec["canmo"] = "quet", 1, 0., 0
            viec["chamtoi"] = {n for n, _, d, _, _, _ in viec["dachuyen"]} | {d for _, _, d, _, _, _ in viec["dachuyen"]}
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
    # Thời gian: kho 9 rương gần đầy (364 2026-11-24: 232 món sai rương, 16 ô trống) cần ~400 lệnh chuyển + ~400 lệnh đổi chỗ, mỗi lệnh
    # ~1s => 12-15 phút, nên bản cũ dừng cứng sau 600s là cắt ngang giữa chừng. Giờ chỉ dừng khi thoigiankhongtiendo giây liền không
    # mở được rương / không gửi được lệnh nào (kẹt thật); lặp vô ích đã có soluottoida / soluotgomtoida / solankhongdoi chặn.
    # thoigiantoida chỉ là chốt an toàn
    def action_sapxepkho(self, giancachlenh = 1.0, thoigianchomoruong = 1.5, soluottoida = 6, soluotgomtoida = 15,
                         thoigiankhongtiendo = 120., thoigiantoida = 3600.):
        viec = self._sapxepkho
        if not viec:
            return
        moitruong = self.moitruong
        now = time.time()
        if now - viec["luctiendo"] > thoigiankhongtiendo:
            self._ketthucsapxepkho(f"Sắp xếp kho {int(thoigiankhongtiendo)} giây không tiến triển, dừng lại")
            return
        if now - viec["batdau"] > thoigiantoida:
            self._ketthucsapxepkho("Sắp xếp kho quá lâu, dừng lại")
            return
        if moitruong.get_is_nhanvatdachet():
            self._ketthucsapxepkho("Nhân vật chết, dừng sắp xếp kho")
            return
        is_quatui = viec["pha"].startswith("t_")
        if now - viec["lucgui"] < (GIANCACHLENHQUATUI if is_quatui and not viec["dangcho"] else 0. if is_quatui else giancachlenh):
            return
        makho = self._laymakho()
        if not makho:
            self._ketthucsapxepkho("Không biết mã kho: mở kho (Quản Khố / Bảo Khố Di Động) rồi bấm lại")
            return
        kho = moitruong.get_khodangmo()
        if kho and 0 < kho["soruong"] <= 20:
            viec["soruong"] = kho["soruong"]
        tennv = moitruong.get_tendoituong()

        if is_quatui:
            self._buocxepquatui(viec, makho, kho, now)
            return
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
                if viec["solanmo"] >= SOLANMORUONGSAPXEP:
                    viec["loi"].append(f"không mở được rương {viec['ruong']}")
                    self._ketthucsapxepkho(f"Dừng sắp xếp kho ở rương {viec['ruong']}")
                    return
                self._moruongsapxepkho(viec, makho, kho, now)
                return
            viec["solanmo"] = 0
            viec["lucmo"] = 0.
            viec["luctiendo"] = now
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
            viec["lucgui"] = viec["luctiendo"] = now
            viec["solenh"] += 1

    # ---------------- Sắp xếp kho qua hành trang ----------------
    # Lệnh Ctrl + chuột trái của client: "pawn - <mã> <ô rương>#<số>" rút 1 ô của rương đang mở ra ô trống hành trang, "pawn + <mã>
    # <id>#<số> <ô rương>" cất món trong túi vào đúng ô rương. Máy chủ nhận gần như ngay (<0.25s, người dùng 2026-11-25), không bị
    # giới hạn ~1 lệnh/s như "pawn >" / "pawn &", và hành trang đổi ngay => biết lệnh ăn chưa bằng ảnh túi (get_anhsoluonghanhtrang),
    # không phải mở lại rương. Nên dùng hành trang làm chỗ trung chuyển, đặt từng món thẳng vào ô đích cuối cùng:
    # - Đích: cả kho sắp như 1 dãy (như _dichgomkho) => mã loại từng ô từng rương (dichs).
    # - Lấp từng rương r: ở r thì cất món đang giữ vào ô trống mà đích cần mã đó, rút món sai chỗ ra túi (chừa 1 ô túi để còn đi lấy
    #   đồ); r còn ô trống cần món nằm ở rương sau thì mở rương đó, rút đúng số món còn thiếu cho ô trống của r, cất món đang giữ mà r
    #   chưa dùng vào ô trống rương đó (ưu tiên ô đích của chính nó), rồi về r. Rương trước r đã đúng nên không đụng tới.
    # - Rương mở ra thì lấy dữ liệu thật; mô hình rương (ruongs) cập nhật theo từng lệnh đã xác nhận. Xong hết thì quét lại cả kho
    #   kiểm tra, còn sai thì làm lại (tối đa SOLUOTQUATUITOIDA lượt).
    # Cần >= 2 ô trống hành trang (1 ô thì rút 1 món ra là không lấy thêm được gì), không đủ thì dùng cách cũ "pawn &" / "pawn >".
    # Đang xếp thì loop_xq ngưng các việc đụng hành trang (dùng / vứt / bán / xếp chồng / xếp túi) để không mất đồ rút từ kho ra
    def _batdauxepquatui(self, viec):
        ruongs = viec["ruongs"]
        dangcos = sorted((self._khoasapxepvatpham(ten), ma) for r in sorted(ruongs) for ten, _, ma in ruongs[r] if ma)
        dichs, vitri = {}, 0
        for r in sorted(ruongs):
            soo = len(ruongs[r])
            phan = [ma for _, ma in dangcos[vitri:vitri + soo]]
            dichs[r] = phan + [0] * (soo - len(phan))
            vitri += soo
        viec["dichs"] = dichs
        sai = {r: sum(1 for (_, _, ma), d in zip(ruongs[r], dichs[r]) if ma != d) for r in sorted(ruongs)}
        viec["pha"], viec["rdich"], viec["vovan"], viec["moden"] = "t_xep", min(ruongs), set(), 0
        viec["lucbatdauluot"] = time.time()
        self._logsapxepkho(f"xếp qua hành trang lượt {viec['luotquatui'] + 1}: ô sai mỗi rương {sai}, túi trống "
                           f"{self.moitruong.get_sootronghanhtrang()} ô")

    @staticmethod
    def _mondatngayquatui(viec, r):
        # Rương r còn phải đi lấy bao nhiêu món mỗi mã (đã trừ món đang giữ): canrong = cho ô trống của r, canmo = cho mọi ô r đang
        # sai (cả ô còn món sai chỗ chưa rút); thuas = món đang giữ r không cần (đem gửi rương sau)
        ruongs, dichs = viec["ruongs"], viec["dichs"]
        canrong = Counter(d for (_, _, ma), d in zip(ruongs[r], dichs[r]) if not ma and d)
        canmo = Counter(d for (_, _, ma), d in zip(ruongs[r], dichs[r]) if ma != d and d)
        thuas = []
        for mon in viec["giu"]:
            if canrong[mon["ma"]] > 0:
                canrong[mon["ma"]] -= 1
            if canmo[mon["ma"]] > 0:
                canmo[mon["ma"]] -= 1
            else:
                thuas.append(mon)
        return +canrong, +canmo, thuas

    def _guilenhquatui(self, viec, loai, lenh, now, kieu = None, **thongtin):
        anh = self.moitruong.get_anhsoluonghanhtrang()
        if anh is None:
            return
        if self.moitruong.action_thucthicaulenh(lenh, douutien = DOUUTIEN_KHANCAP):
            if viec["solenh"] < 3:
                self.moitruong._inlog(f"[SẮP XẾP KHO] {lenh}")
            viec["dangcho"] = dict(thongtin, loai = loai, kieu = kieu or loai, lenh = lenh, anh = anh, lucgui = now, solan = 1)
            viec["lucgui"] = viec["luctiendo"] = now

    def _rutquatui(self, viec, makho, ruong, o, now):
        ten, sl, ma = viec["ruongs"][ruong][o]
        self._guilenhquatui(viec, "-", f"pawn - {makho} {o + 1}#{max(1, sl)}", now, ruong = ruong, o = o, mon = (ten, sl, ma))

    def _catquatui(self, viec, makho, ruong, o, mon, now):
        # -> False khi chưa gửi vì chưa đủ GIANCACHDATOQUATUI từ lần cất trước (người gọi làm việc khác: rút món ra túi...)
        # Ô o là ô trống đầu của rương và món không chồng được / rương chưa có món cùng mã (khỏi bị gộp chồng chỗ khác) thì gửi
        # dạng Ctrl + chuột không ghi ô
        os = viec["ruongs"][ruong]
        otrongdau = next((i for i, (_, _, ma) in enumerate(os) if not ma), None)
        is_tudo = o == otrongdau and (not mon["sl"] or not any(ma == mon["ma"] for _, _, ma in os))
        if not is_tudo and now - viec["lucdatcuoi"] < GIANCACHDATOQUATUI:
            return False
        lenh = f"pawn + {makho} {mon['id']:x}#{max(1, mon['sl'])}" + ("" if is_tudo else f" {o + 1}")
        self._guilenhquatui(viec, "+", lenh, now, kieu = "+tựdo" if is_tudo else "+ô", ruong = ruong, o = o, giu = mon)
        return True

    @staticmethod
    def _thongkequatui(viec, cho):
        tk = viec["thongke"].setdefault(cho["kieu"], [0, 0])
        tk[0] += 1
        tk[1] += cho["solan"] - 1

    @staticmethod
    def _chuoithongkequatui(viec):
        return ", ".join(f"{k} {xong} món gửi lại {lai} lần" for k, (xong, lai) in viec.get("thongke", {}).items())

    def _kiemtralenhquatui(self, viec, now):
        # Lệnh vừa gửi đã ăn chưa (so ảnh túi lúc gửi): rút = có id mới / chồng tăng; cất = id mất / chồng giảm đủ.
        # Quá THOIGIANCHOLENHQUATUI chưa thấy thì gửi lại (lệnh trước có ăn muộn thì lệnh sau cũng không làm gì: ô rút đã trống / món
        # cất đã rời túi), SOLANLENHQUATUI lần không được thì bỏ ô / món đó
        cho = viec["dangcho"]
        anhcu = cho["anh"]
        anh = self.moitruong.get_anhsoluonghanhtrang()
        if anh is None:
            return
        ruongs = viec["ruongs"]
        if cho["loai"] == "-":
            ten, sl, ma = cho["mon"]
            tangs = {i: anh[i] - anhcu.get(i, 0) for i in anh if i not in anhcu or anh[i] > anhcu[i]}
            if tangs:
                if len(tangs) == 1:
                    i = next(iter(tangs))
                    viec["giu"].append({"id": i, "ten": ten, "sl": sl, "ma": ma})
                else:
                    # Chồng rút ra gộp vào chồng cùng tên trong túi rồi tràn sang ô mới: giữ từng phần
                    viec["giu"].extend({"id": i, "ten": ten, "sl": d, "ma": ma} for i, d in tangs.items())
                ruongs[cho["ruong"]][cho["o"]] = ("", 0, 0)
                self._thongkequatui(viec, cho)
                viec["dangcho"] = None
                viec["solenh"] += 1
                viec["soquatui"] += 1
                return
        else:
            mon = cho["giu"]
            i = mon["id"]
            if i not in anh or (mon["sl"] > 0 and anh[i] <= anhcu.get(i, 0) - mon["sl"]):
                if mon in viec["giu"]:
                    viec["giu"].remove(mon)
                ruongs[cho["ruong"]][cho["o"]] = (mon["ten"], mon["sl"], mon["ma"])
                if cho["kieu"] == "+ô":
                    viec["lucdatcuoi"] = cho["lucgui"]
                self._thongkequatui(viec, cho)
                viec["dangcho"] = None
                viec["solenh"] += 1
                viec["soquatui"] += 1
                return
        if now - cho["lucgui"] < THOIGIANCHOLENHQUATUI:
            return
        if cho["solan"] < SOLANLENHQUATUI:
            if self.moitruong.action_thucthicaulenh(cho["lenh"], douutien = DOUUTIEN_KHANCAP):
                cho["solan"] += 1
                cho["lucgui"] = viec["lucgui"] = now
            return
        viec["dangcho"] = None
        self._logsapxepkho(f"{cho['lenh']} gửi {cho['solan']} lần không ăn")
        if cho["loai"] == "-":
            viec["khongrut"].add((cho["ruong"], cho["o"]))
        else:
            mon = cho["giu"]
            mon["loi"] = mon.get("loi", 0) + 1
            if mon["loi"] >= 2 and mon in viec["giu"]:
                viec["giu"].remove(mon)
                viec["loi"].append(f"{mon['ten']} không cất lại vào kho được, đang ở hành trang")
            # Có thể mô hình lệch (ô đó thật ra có đồ): mở lại rương lấy dữ liệu thật
            viec["moden"] = cho["ruong"]
            viec["ruongmo"] = 0

    def _buocxepquatui(self, viec, makho, kho, now):
        ruongs, dichs, giu = viec["ruongs"], viec["dichs"], viec["giu"]
        if viec["dangcho"]:
            self._kiemtralenhquatui(viec, now)
            return
        if viec["moden"]:
            r = viec["moden"]
            if (viec["canmo"] != r or not viec["lucmo"]) and now - viec["lucdatcuoi"] < GIANCACHDATOQUATUI:
                return
            os = self._chodulieuruong(viec, makho, kho, now, r, THOIGIANCHOMORUONG)
            if os is None:
                return
            if os is False:
                viec["loi"].append(f"không mở được rương {r}")
                self._ketthucsapxepkho(f"Dừng sắp xếp kho ở rương {r}")
                return
            ruongs[r] = os
            viec["ruongmo"], viec["moden"], viec["dalam"] = r, 0, False
            return
        sotrong = self.moitruong.get_sootronghanhtrang()
        soruong = max(ruongs)
        hientai = viec["ruongmo"]
        r = viec["rdich"]

        if viec["pha"] == "t_kiemtra":
            # Quét lại cả kho từ rương viec["ruong"]
            if hientai != viec["ruong"]:
                viec["moden"] = viec["ruong"]
                return
            if viec["ruong"] < soruong:
                viec["ruong"] += 1
                viec["moden"] = viec["ruong"]
                return
            sais = {t: sum(1 for (_, _, ma), d in zip(ruongs[t], dichs[t]) if ma != d) for t in sorted(ruongs)}
            if not any(sais.values()):
                self._ketthucsapxepkho(f"Đã sắp xếp xong kho ({soruong} rương, {int(now - viec['batdau'])}s)")
                return
            viec["luotquatui"] += 1
            if viec["luotquatui"] >= SOLUOTQUATUITOIDA:
                viec["loi"].append(f"còn ô sai sau {SOLUOTQUATUITOIDA} lượt: {sais}")
                self._ketthucsapxepkho("Sắp xếp kho chưa xong, dừng lại")
                return
            self._logsapxepkho(f"kiểm tra còn ô sai {sais}, làm lại")
            self._batdauxepquatui(viec)
            return

        if r > soruong:
            # Xong mọi rương theo mô hình: món còn giữ (chồng bị tách...) cất vào ô trống bất kỳ, rồi quét lại kiểm tra
            if giu:
                if hientai and any(not ma for _, _, ma in ruongs[hientai]):
                    mon = giu[0]
                    o = next((o for o, ((_, _, ma), d) in enumerate(zip(ruongs[hientai], dichs[hientai])) if not ma and d == mon["ma"]),
                             next(o for o, (_, _, ma) in enumerate(ruongs[hientai]) if not ma))
                    self._catquatui(viec, makho, hientai, o, mon, now)
                    return
                t = next((t for t in sorted(ruongs) if any(not ma for _, _, ma in ruongs[t])), None)
                if t is None:
                    viec["loi"].append(f"kho hết ô trống, {len(giu)} món còn ở hành trang")
                    viec["giu"] = []
                    return
                viec["moden"] = t
                return
            self._logsapxepkho(f"xếp xong theo mô hình ({viec['soquatui']} lệnh, {int(now - viec['lucbatdauluot'])}s), quét lại kiểm tra")
            viec["pha"], viec["ruong"] = "t_kiemtra", 1
            viec["moden"] = 1
            return

        if all(ma == d for (_, _, ma), d in zip(ruongs[r], dichs[r])):
            self._logsapxepkho(f"xong rương {r} ({int(now - viec['lucbatdauluot'])}s từ đầu lượt; {self._chuoithongkequatui(viec)})")
            viec["rdich"] += 1
            viec["vovan"] = set()
            return

        canrong, canmo, thuas = self._mondatngayquatui(viec, r)
        if hientai == r:
            # Cất món đang giữ vào ô trống mà đích cần đúng mã đó (chưa tới lượt cất thì rút tiếp món khác trong lúc chờ; không
            # còn gì để rút thì chờ)
            chocat = False
            for o, ((_, _, ma), d) in enumerate(zip(ruongs[r], dichs[r])):
                if not ma and d:
                    mon = next((m for m in giu if m["ma"] == d), None)
                    if mon:
                        viec["vovan"] = set()
                        if self._catquatui(viec, makho, r, o, mon, now):
                            return
                        chocat = True
                        break
            # Rút món sai chỗ, ưu tiên ô mà đang giữ đúng món cho nó (rút xong cất vào ngay, như đổi chỗ: túi còn 1 ô cũng làm được).
            # Ô khác thì chừa 1 ô túi để còn đi lấy đồ (giả lập kho đầy + túi 2-3 ô trống: không chừa / không ưu tiên thì kẹt)
            # Món rút ra mà cất ngay được vào ô trống của r (đích ô trống cần mã đó) cũng thế
            if sotrong >= 1:
                giuma = {m["ma"] for m in giu}
                os = [(d in giuma or canrong[ma] > 0, -o) for o, ((_, _, ma), d) in enumerate(zip(ruongs[r], dichs[r]))
                      if ma and ma != d and (r, o) not in viec["khongrut"] and (sotrong >= 2 or d in giuma or canrong[ma] > 0)]
                if os:
                    viec["vovan"] = set()
                    self._rutquatui(viec, makho, r, -max(os)[1], now)
                    return
            if chocat:
                return
            # Còn ô trống cần món ở rương sau: tới rương có nhiều món cần nhất. Không còn ô trống (kho đầy, túi ít chỗ) thì đi lấy món
            # cho ô đang có món sai: về r rút ô đó rồi cất ngay vào (giả lập kho đầy 100% + túi 3 ô: không làm vậy thì kẹt)
            ungviens = []
            can = canrong or (canmo if sotrong >= 2 else Counter())
            if can:
                for t in range(r + 1, soruong + 1):
                    if t in viec["vovan"]:
                        continue
                    so = sum(min(sl, Counter(ma for _, _, ma in ruongs[t])[m]) for m, sl in can.items())
                    if so:
                        ungviens.append((so, -t, t))
            if not ungviens and thuas:
                # Túi gần đầy vì giữ món r chưa dùng: đem gửi rương sau còn ô trống
                ungviens = [(1, -t, t) for t in range(r + 1, soruong + 1)
                            if t not in viec["vovan"] and any(not ma for _, _, ma in ruongs[t])]
            if ungviens:
                viec["moden"] = max(ungviens)[2]
                return
            sai = sum(1 for (_, _, ma), d in zip(ruongs[r], dichs[r]) if ma != d)
            self._logsapxepkho(f"rương {r} còn {sai} ô chưa xếp được (túi trống {sotrong} ô), bỏ qua")
            viec["rdich"] += 1
            viec["vovan"] = set()
            return

        if not hientai or hientai <= r:
            viec["moden"] = r
            return
        # Đang ở rương sau t: rút món r còn thiếu, cất món đang giữ mà r chưa dùng được vào ô trống của t
        t = hientai
        # Món cho ô trống của r: túi còn 1 ô cũng rút (về r cất ngay được); món cho ô r đang có món sai: chừa 1 ô túi (về r còn rút
        # được ô đó). Ưu tiên ô t đang sai chỗ (ô đúng chỗ rút đi thì t lại thiếu)
        if sotrong >= 1 and (canrong or canmo):
            os = [((canrong[ma] > 0), ma != d, -o) for o, ((_, _, ma), d) in enumerate(zip(ruongs[t], dichs[t]))
                  if ma and (t, o) not in viec["khongrut"] and (canrong[ma] > 0 or (canmo[ma] > 0 and sotrong >= 2))]
            if os:
                viec["dalam"] = True
                self._rutquatui(viec, makho, t, -max(os)[2], now)
                return
        if thuas:
            otrongs = [o for o, (_, _, ma) in enumerate(ruongs[t]) if not ma]
            if otrongs:
                for m in thuas:
                    o = next((o for o in otrongs if dichs[t][o] == m["ma"]), None)
                    if o is not None:
                        break
                else:
                    m, o = thuas[0], otrongs[0]
                viec["dalam"] = True
                self._catquatui(viec, makho, t, o, m, now)
                return
        if not viec.get("dalam"):
            viec["vovan"].add(t)
        viec["moden"] = r

    def batdau_catkho_sauban(self):
        # Gọi khi bán rác + sửa đồ xong: bật "Tự cất sau bán rác" và có món cần cất thì tạo việc (đang có việc bấm tay thì làm tiếp việc đó)
        # Tắt "Tự cất sau bán rác" thì vẫn cất đồ trong túi Càn Khôn hết hạn (chỉ đồ đó)
        if self._catkho:
            return
        is_chituihethan = not tailuat()["is_catkhosauban"]
        # Đồ túi hết hạn tính cả khi đang chuyển dở về túi còn hạn (bán rác xong túi 1 có chỗ): việc cất chờ chuyển xong rồi cất phần dư
        if not self._laymoncatkho(is_chituihethan = is_chituihethan) and not self._laymontuihethan():
            return
        self._catkho = self._taoviec(LYDOCATKHO_BANRAC)
        self._catkho["is_chituihethan"] = is_chituihethan
        print("[CẤT KHO] Bắt đầu cất kho sau bán rác{}".format(" (đồ túi Càn Khôn hết hạn)" if is_chituihethan else ""))

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
        # Săn Tinh Anh: bán đồ trắng nhặt được ở Chủ Tiệm Tạp Hóa trước rồi mới tới Quản Khố cất Lam Kim
        if viec.get("banrac") and viec["banrac"] != "xong":
            kq = self._buocbantrangtinhanh(viec)
            if isinstance(kq, tuple):
                return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (kq[1], kq[2], idbando), "khoangcachtoida": 2.}
            return None
        kq = self._buoccatkho(viec)
        if isinstance(kq, tuple):
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (kq[1], kq[2], idbando), "khoangcachtoida": KHOANGCACHQUANKHO - 1}
        return None
