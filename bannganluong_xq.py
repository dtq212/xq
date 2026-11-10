# Bán ngân lượng lấy tiền chuyển khoản: người chơi chuyển khoản với nội dung "<tiền tố><ID nhân vật>" (vd NL12345), bot hỏi API SePay
# thấy giao dịch tiền vào thì quy ra ngân lượng, đưa vào hàng chờ giao đồ (tactu_giaodo_xq) của nhân vật bán; nhân vật bán về Tân Thủ
# Thôn đứng cạnh Chủ Tiệm Tạp Hóa chờ (không giới hạn) tới khi người chơi có ID đó lại gần thì give.
# Cấu hình _internal/bannganluong.json (tự tạo mẫu, đang tắt):
#   - "token": API token SePay (my.sepay.vn: Cấu hình Công ty -> API Access -> Thêm), "sotaikhoan": chỉ nhận tiền vào tài khoản này
#     (để trống = mọi tài khoản đã nối SePay)
#   - "tiento": tiền tố trước ID trong nội dung chuyển khoản; "nganluongmoi1000d": 1.000đ đổi được bao nhiêu ngân lượng;
#     "sotientoithieu": dưới số tiền này thì không tự giao (báo Telegram xử lý tay)
#   - "giulaitoithieu": ngân lượng nhân vật bán luôn giữ lại làm quỹ; đơn mà giao xong số dư tụt dưới mức này thì bot không give,
#     đơn thành "loi" (báo Telegram), bổ sung ngân lượng rồi đặt "guilai". 0 = bán tới hết
#   - "tanglandau": % ngân lượng tặng thêm cho đơn đầu tiên của mỗi ID (0 = tắt). "Lần đầu" = trong bannganluong_don.json chưa có đơn
#     nào của ID đó ngoài đơn "huy" / "xulytay" (đơn xulytay là chưa giao được, đặt "guilai" thì giao đúng số đã tính lúc tạo, không
#     tặng thêm). Khách mua trước khi có file đơn thì bot không biết, vẫn tính là lần đầu
#   - "idnhanvatban": ID người chơi của nhân vật bán. Chỉ máy đang chạy nhân vật này mới hỏi SePay và giao (máy khác chép cùng cấu hình
#     cũng không giao trùng)
#   - Rao bán: "is_rao" bật, nhân vật bán rao theo từng mục "raos": {"kenh", "chuky": [x, y] giây ngẫu nhiên (1 số = cố định),
#     "noidung"}, mỗi mục giờ hẹn riêng. Kênh lấy từ chuỗi trong XQ.exe ("vipchat %s", "say %s"...): "vipchat" kênh VIP/thế giới (test
#     2026-11-10 hiện đủ câu ~160 byte), "say" kênh lân cận. Kênh thế giới chỉ rao giá + "ai mua ib", không lộ số tài khoản.
#   - Trả lời tin mật: "is_traloitinmat" bật thì ai nhắn tin mật cho nhân vật bán ("<tên> nói thầm với bạn : ...") được nhắn lại
#     "tell <ID> <noidungtraloi>" (hết mil thì "noidunghetmil"). ID người nhắn tra ở danh sách mật ngữ gần đây của client
#     (MoiTruong.get_tinmatdens), không ra thì gửi Dò tìm và báo Telegram để nhắn tay.
#   - Ô thay trong câu: {mil100k} (100.000đ được bao nhiêu mil, vd 1,5), {dongia} (giá 1 mil, vd 66,7k), {tiento}, {stk} (sotaikhoan),
#     {nganhang}, {chutaikhoan}, {conlai} (mil còn bán được = ngân lượng đang có - giulaitoithieu - đơn chờ giao); câu trả lời thêm
#     {ten}, {idnguoimua}. Hết mil thì không rao
# Đơn lưu ở _internal/bannganluong_don.json (KHÔNG đưa lên git: đồng bộ git ghi đè bản cũ là giao lại đơn đã giao). Chạy lần đầu (chưa có
# file) chỉ nhận giao dịch từ lúc đó, không giao lại lịch sử. Trạng thái đơn ("trangthai"):
#   chogiao: đã đưa vào hàng chờ của nhân vật bán. Bot mất hàng chờ (mở lại client) mà chưa gửi lệnh give thì tự đưa lại
#   xong / loi: bot báo giao xong / lỗi (vd hết ngân lượng; bot đã báo Telegram)
#   kiemtratay: bot đã gửi give rồi mất hàng chờ trước khi biết kết quả -> không tự giao lại, xem túi người chơi rồi xử lý tay
#   xulytay: nội dung không có ID hợp lệ / dưới số tiền tối thiểu
#   Muốn giao lại đơn loi / kiemtratay / xulytay: sửa file, đặt "trangthai": "guilai" (đơn xulytay thì điền thêm "idnguoichoi");
#   muốn bỏ hẳn đơn đang chờ: "trangthai": "huy" (nút Huỷ ở bảng giao đồ không đủ, bot mất hàng chờ là đơn được đưa lại)
import html
import json
import os
import random
import re
import sys
import threading
import time
import urllib.parse
import urllib.request

from giaodo_xq import taoyeucau, guiyeucau
from thongbao_xq import guitin, _moketnoi

CAUHINHMAU = {
    "is_bat": False,
    "token": "",
    "sotaikhoan": "",
    "tiento": "NL",
    "nganluongmoi1000d": 0,
    "sotientoithieu": 10000,
    "idnhanvatban": 0,
    "giulaitoithieu": 0,
    "tanglandau": 20,
    "is_rao": False,
    "nganhang": "",
    "chutaikhoan": "",
    "raos": [
        {"kenh": "vipchat", "chuky": [70, 150],
         "noidung": "bán mil {mil100k}m = 100k ai có nhu cầu vui lòng IB. Ưu đãi mua lần đầu tặng thêm 20%"},
    ],
    "is_traloitinmat": True,
    "trehoantraloi": [5, 12],
    "noidungtraloi": [
        "mình bán mil giá 100k = {mil100k}m, bạn mua thì ck vào {nganhang} {stk} nd {tiento}{idnguoimua}, xong ra tạp hóa tân thủ thôn chỗ mình đứng là nhận. còn {conlai}m",
        "mình bán 100k {mil100k}m nha, b mua thì chuyển khoản vào {nganhang} {stk} nội dung {tiento}{idnguoimua} rồi qua tạp hóa tân thủ thôn nhận. mình còn {conlai}m",
        "mil mình bán giá 100k = {mil100k}m b ơi. b mua thì ck {stk} {nganhang}, nd ghi {tiento}{idnguoimua}, ck xong ra tạp hóa ttt gặp mình nhận liền. còn {conlai}m",
        "mình bán giá 100k {mil100k}m, còn {conlai}m. bạn mua thì ck vào {nganhang} {stk} nd {tiento}{idnguoimua} nhé, xong ghé tạp hóa tân thủ thôn đứng cạnh mình là có",
        "mình đang bán 100k = {mil100k}m nè. b lấy thì ck qua {nganhang} {stk} ghi nd {tiento}{idnguoimua}, rồi ra tạp hóa tân thủ thôn nhận nha. còn {conlai}m",
        "giá mình bán 100k {mil100k}m b nhé. mua thì ck vào {stk} ({nganhang}) nd {tiento}{idnguoimua}, tiền vào là ra tạp hóa tân thủ thôn nhận. còn {conlai}m thôi",
        "mình bán mil 100k = {mil100k}m, còn {conlai}m. b mua thì chuyển vào {nganhang} {stk}, nội dung {tiento}{idnguoimua}, xong qua tạp hóa ttt chỗ mình nhận",
        "ok b, mình bán giá 100k {mil100k}m. b mua thì ck {nganhang} {stk} nd đúng {tiento}{idnguoimua} giúp mình, xong ra tạp hóa tân thủ thôn lấy. còn {conlai}m",
        "mình bán 100k ra {mil100k}m b ạ. muốn mua thì ck vào {stk} {nganhang} ghi {tiento}{idnguoimua}, rồi chạy ra tạp hóa tân thủ thôn gặp mình. còn {conlai}m",
        "có b, mình bán giá 100k = {mil100k}m, còn {conlai}m. b mua thì ck vào {nganhang} {stk} nd {tiento}{idnguoimua} rồi ra tạp hóa tân thủ thôn đứng gần mình là nhận",
        "mình bán mil 100k {mil100k}m nhé b. b mua thì ck {stk} {nganhang}, nd {tiento}{idnguoimua}, ck xong qua tạp hóa ttt nhận luôn. mình còn {conlai}m",
        "mình bán giá 100k = {mil100k}m. b cần thì chuyển khoản vào {nganhang} {stk} với nd {tiento}{idnguoimua}, xong ra tạp hóa tân thủ thôn mình đưa. còn {conlai}m",
    ],
    "noidunghetmil": [
        "hết mil rồi b ơi, lát có mình báo nha",
        "tạm hết rồi b, tí nữa quay lại nhé",
        "vừa bán hết mất r b, chút có thêm mình nhắn",
    ],
}
# Trả lời tin mật: cùng 1 người cách nhau tối thiểu chừng này giây (nhắn liên tục không bị spam lại); chờ tra ID tối đa chừng này giây
GIANCACHTRALOICUNGNGUOI = 30.
THOIGIANCHOIDTINMAT = 15.
# Kênh chat được rao (cuaso_xq chỉ nhận các kênh này); khoảng rao tối thiểu để khỏi spam khi cấu hình sai
KENHRAOs = ("chat", "say", "rumor", "vipchat", "ct", "ot", "ft", "et", "tt")
KHOANGRAOTOITHIEU = 3.
# 1 mil = 1 triệu ngân lượng
NGANLUONGMOIMIL = 1000000
# Hỏi SePay mỗi chừng này giây; đồng bộ trạng thái đơn với bot nhanh hơn
CHUKYHOISEPAY = 30.
CHUKYDONGBO = 5.
# Đưa đơn vào hàng chờ của bot rồi mà chừng này giây không thấy trong hàng chờ thì đưa lại
THOIGIANCHOBOTNHAN = 30.
TRANGTHAIBOTDAGUI = "đã gửi lệnh"


def _thumucgoc():
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))


def duongdancauhinh():
    return os.path.join(_thumucgoc(), "_internal", "bannganluong.json")


def duongdandon():
    return os.path.join(_thumucgoc(), "_internal", "bannganluong_don.json")


def _docjson(duongdan, macdinh):
    try:
        with open(duongdan, encoding = "utf-8-sig") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as err:
        print(f"[BÁN NL] Lỗi đọc {duongdan}: {err}")
        return macdinh


def _ghijson(duongdan, dulieu):
    try:
        os.makedirs(os.path.dirname(duongdan), exist_ok = True)
        with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False, indent = 2)
        os.replace(duongdan + ".tmp", duongdan)
    except OSError as err:
        print(f"[BÁN NL] Lỗi ghi {duongdan}: {err}")


def taicauhinh():
    dulieu = _docjson(duongdancauhinh(), {})
    if dulieu is None:
        _ghijson(duongdancauhinh(), CAUHINHMAU)
        dulieu = {}
    return dict(CAUHINHMAU, **dulieu)


def docidnguoichoi(noidung, tiento):
    # "MBVCB.123.NL12345.CT tu ..." -> 12345. Tiền tố đứng riêng (trước nó không dính chữ / số), sau có thể cách bằng khoảng trắng / . - _ :
    # Không có hoặc có từ 2 ID khác nhau thì None (không đoán)
    if not tiento:
        return None
    ids = {int(m) for m in re.findall(rf"(?<![0-9A-Za-z]){re.escape(tiento)}[\s.\-_:]*(\d{{1,12}})(?!\d)", noidung or "", re.I)}
    return ids.pop() if len(ids) == 1 else None


def _dien(mau, thongtin):
    # Điền các ô {..} vào mẫu câu, gộp khoảng trắng (ô trống trong mẫu); mẫu sai thì None. Mẫu là danh sách thì bốc ngẫu nhiên 1 câu
    # (câu giống hệt nhau lặp lại dễ bị nhận ra là bot)
    if isinstance(mau, (list, tuple)):
        mau = random.choice(mau) if mau else ""
    try:
        return re.sub(r"\s+", " ", str(mau).format(**thongtin)).strip()
    except (KeyError, IndexError, ValueError) as err:
        print(f"[BÁN NL] Mẫu câu sai ({err}): {mau}")
        return None


def _khoangrao(chuky, toithieu = None):
    # [x, y] -> ngẫu nhiên x..y giây; 1 số -> cố định; sai thì 60..120
    toithieu = KHOANGRAOTOITHIEU if toithieu is None else toithieu
    try:
        x, y = (chuky[0], chuky[-1]) if isinstance(chuky, (list, tuple)) else (chuky, chuky)
        x, y = sorted((max(toithieu, float(x)), max(toithieu, float(y))))
    except (TypeError, ValueError, IndexError):
        x, y = 60., 120.
    return random.uniform(x, y)


def _somil(nganluong):
    # Ngân lượng -> số mil 1 chữ số thập phân, dấu phẩy: 1.500.000 -> "1,5", 10.448.500 -> "10,4", 2.000.000 -> "2"
    return f"{nganluong / NGANLUONGMOIMIL:.1f}".rstrip("0").rstrip(".").replace(".", ",")


def _so(n):
    return f"{n:,}".replace(",", ".")


class BanNganLuong:
    # Chạy trong tiến trình giao diện (1 luồng cho cả máy), cạnh DieuKhienTelegram
    def __init__(self, shared_data, command_dict):
        self.shared_data = shared_data
        self.command_dict = command_dict
        self._luchoisepay = 0.
        # Giờ hẹn rao tiếp theo từng mục "raos" (chỉ số -> time); lần in "hết mil" gần nhất
        self._lucraoteps = {}
        self._luchetmil = 0.
        # Tin mật đã xử lý (thời điểm, tên); lần trả lời gần nhất theo ID người chơi
        self._tinmatdaxuly = set()
        self._luctraloiids = {}
        # Thời điểm sẽ trả lời từng tin mật (đã cộng trễ giả gõ phím)
        self._luctraloitins = {}
        self._trangthai_log = None

    def batdau(self):
        threading.Thread(target = self.loop, daemon = True).start()
        # Rao chạy luồng riêng, 1s/lượt: kênh lân cận rao 5-10s, luồng chính 5s/lượt lại có lúc chờ SePay 15s
        threading.Thread(target = self.loop_rao, daemon = True).start()

    def _log(self, trangthai):
        # In 1 dòng mỗi khi đổi trạng thái
        if trangthai != self._trangthai_log:
            self._trangthai_log = trangthai
            print(f"[BÁN NL] {trangthai} · {duongdancauhinh()}")

    def loop(self):
        while True:
            try:
                self._mot_luot()
            except Exception as err:
                print(f"[BÁN NL] Lỗi: {err}")
                time.sleep(10)
            time.sleep(CHUKYDONGBO)

    def _timnhanvatban(self, idnhanvatban):
        for hwnd, info in dict(self.shared_data.items()).items():
            if isinstance(info, dict) and info.get("idnguoichoi") == idnhanvatban:
                return hwnd, info
        return None, None

    def _mot_luot(self):
        cauhinh = taicauhinh()
        if not cauhinh.get("is_bat") or not cauhinh.get("token") or not cauhinh.get("nganluongmoi1000d") or not cauhinh.get("idnhanvatban"):
            self._log("đang tắt (cần is_bat, token, nganluongmoi1000d, idnhanvatban)")
            return
        hwnd, info = self._timnhanvatban(int(cauhinh["idnhanvatban"]))
        if hwnd is None:
            self._log(f"máy này không chạy nhân vật bán (ID {cauhinh['idnhanvatban']}), không hỏi SePay")
            return
        self._log(f"đang bật · nhân vật bán {info.get('tennhanvat')} (ID {cauhinh['idnhanvatban']})")

        trangthai = _docjson(duongdandon(), None)
        if trangthai is None:
            # Lần đầu: chỉ nhận giao dịch từ giờ trở đi
            trangthai = {"lucbatdau": time.strftime("%Y-%m-%d %H:%M:%S"), "idcuoi": 0, "dons": {}}
            print(f"[BÁN NL] Bắt đầu nhận giao dịch từ {trangthai['lucbatdau']}")
        dons = trangthai["dons"]

        if time.time() - self._luchoisepay >= CHUKYHOISEPAY:
            self._luchoisepay = time.time()
            for gd in self._laygiaodich(cauhinh, trangthai):
                trangthai["idcuoi"] = max(trangthai["idcuoi"], int(gd["id"]))
                if str(gd["id"]) not in dons:
                    dons[str(gd["id"])] = self._taodon(cauhinh, gd, dons)

        self._dongbo(cauhinh, hwnd, info, dons)
        _ghijson(duongdandon(), trangthai)

    def loop_rao(self):
        while True:
            try:
                self._rao()
            except Exception as err:
                print(f"[BÁN NL] Lỗi rao: {err}")
                time.sleep(10)
            time.sleep(1.)

    def _thongtinban(self, cauhinh, info):
        # Các ô thay trong câu rao / trả lời; None khi chưa đọc được ngân lượng. "conlaing" = ngân lượng còn bán được
        nganluong = info.get("nganluong")
        if nganluong is None:
            return None
        dons = (_docjson(duongdandon(), None) or {}).get("dons") or {}
        dangcho = sum(int(don.get("nganluong") or 0) for don in dons.values() if don.get("trangthai") == "chogiao")
        conlai = nganluong - int(cauhinh.get("giulaitoithieu") or 0) - dangcho
        # Giá 1 mil theo nghìn đồng: 1.000đ = nganluongmoi1000d ngân lượng; lẻ thì 1 số thập phân ("100k", 15.000 NL/1k -> "66,7k")
        dongia = NGANLUONGMOIMIL / int(cauhinh["nganluongmoi1000d"])
        return {"dongia": f"{dongia:.1f}".rstrip("0").rstrip(".").replace(".", ",") + "k",
                "mil100k": _somil(100 * int(cauhinh["nganluongmoi1000d"])), "tiento": cauhinh.get("tiento") or "",
                "stk": cauhinh.get("sotaikhoan") or "", "nganhang": cauhinh.get("nganhang") or "",
                "chutaikhoan": cauhinh.get("chutaikhoan") or "", "conlai": _somil(max(0, conlai)), "conlaing": conlai,
                "nganluong": nganluong, "dangcho": dangcho}

    def _rao(self):
        cauhinh = taicauhinh()
        if not cauhinh.get("is_bat") or not cauhinh.get("nganluongmoi1000d") or not cauhinh.get("idnhanvatban"):
            return
        hwnd, info = self._timnhanvatban(int(cauhinh["idnhanvatban"]))
        # command_dict mỗi cửa sổ chỉ giữ 1 lệnh: đang có lệnh chờ (vd giaodo) thì để giây sau, kẻo đè mất
        if hwnd is None or self.command_dict.get(hwnd):
            return
        thongtin = self._thongtinban(cauhinh, info)
        if thongtin is None:
            return
        # Trả lời tin mật trước (người đang chờ), mỗi lượt 1 lệnh
        if cauhinh.get("is_traloitinmat") and self._traloitinmat(cauhinh, hwnd, info, thongtin):
            return
        if not cauhinh.get("is_rao"):
            return
        raos = [r for r in (cauhinh.get("raos") or []) if isinstance(r, dict) and r.get("kenh") in KENHRAOs and r.get("noidung")]
        now = time.time()
        dendens = [i for i in range(len(raos)) if now >= self._lucraoteps.get(i, 0.)]
        if not dendens:
            return
        if thongtin["conlaing"] < NGANLUONGMOIMIL:
            if now - self._luchetmil >= 300:
                self._luchetmil = now
                print(f"[BÁN NL] Hết mil để rao (ngân lượng {_so(thongtin['nganluong'])}, chờ giao {_so(thongtin['dangcho'])})")
            return
        # Mỗi lượt gửi 1 mục (mục hẹn sớm nhất), mục khác tới hẹn cùng lúc thì giây sau
        i = min(dendens, key = lambda j: self._lucraoteps.get(j, 0.))
        rao = raos[i]
        self._lucraoteps[i] = now + _khoangrao(rao.get("chuky"))
        noidung = _dien(rao["noidung"], thongtin)
        if noidung is None:
            return
        self.command_dict[hwnd] = f"raoban:{rao['kenh']}|{noidung}"
        print(f"[BÁN NL] Rao {rao['kenh']}: {noidung} (lần sau sau {self._lucraoteps[i] - now:.0f}s)")

    def _traloitinmat(self, cauhinh, hwnd, info, thongtin):
        # Người nhắn tin mật (bất kỳ nội dung) -> nhắn lại hướng dẫn chuyển khoản riêng cho ID đó (nội dung CK đúng ID của họ) và số mil còn.
        # Mỗi tin trả lời 1 lần; cùng 1 người nhắn liên tục thì cách nhau GIANCACHTRALOICUNGNGUOI giây. Không tra được ID sau
        # THOIGIANCHOIDTINMAT giây thì báo Telegram để nhắn tay. -> True khi vừa gửi lệnh
        now = time.time()
        for tin in info.get("_tinmatdens") or []:
            khoa = (round(tin["luc"], 3), tin["ten"])
            if khoa in self._tinmatdaxuly:
                continue
            # Chờ vài giây như người đang gõ ("trehoantraloi" [x, y] giây, bốc 1 lần cho mỗi tin)
            if khoa not in self._luctraloitins:
                self._luctraloitins[khoa] = tin["luc"] + _khoangrao(cauhinh.get("trehoantraloi") or [5, 12], 1.)
            if now < self._luctraloitins[khoa]:
                continue
            if tin.get("id") is None:
                if now - tin["luc"] >= THOIGIANCHOIDTINMAT:
                    self._tinmatdaxuly.add(khoa)
                    print(f"[BÁN NL] Tin mật từ {tin['ten']} nhưng không tra được ID, cần nhắn tay")
                    guitin(f"⚠️ {html.escape(tin['ten'])} nhắn mua mil (<i>{html.escape(tin['noidung'])}</i>) nhưng bot không tra được ID, "
                           f"nhắn tay giúp", is_html = True)
                continue
            self._tinmatdaxuly.add(khoa)
            if now - self._luctraloiids.get(tin["id"], 0.) < GIANCACHTRALOICUNGNGUOI:
                continue
            mau = cauhinh.get("noidungtraloi") if thongtin["conlaing"] >= NGANLUONGMOIMIL else cauhinh.get("noidunghetmil")
            noidung = _dien(mau or "", dict(thongtin, ten = tin["ten"], idnguoimua = tin["id"]))
            if not noidung:
                continue
            self._luctraloiids[tin["id"]] = now
            self.command_dict[hwnd] = f"tinmat:{tin['id']}|{noidung}"
            print(f"[BÁN NL] Trả lời tin mật {tin['ten']} (ID {tin['id']}, nhắn \"{tin['noidung']}\"): {noidung}")
            return True
        return False

    def _laygiaodich(self, cauhinh, trangthai):
        # Giao dịch tiền vào mới (id tăng dần). SePay: since_id lấy id >= giá trị
        thamso = {"limit": 200}
        if trangthai["idcuoi"]:
            thamso["since_id"] = trangthai["idcuoi"] + 1
        else:
            thamso["transaction_date_min"] = trangthai["lucbatdau"]
        if cauhinh.get("sotaikhoan"):
            thamso["account_number"] = cauhinh["sotaikhoan"]
        yeucau = urllib.request.Request("https://my.sepay.vn/userapi/transactions/list?" + urllib.parse.urlencode(thamso),
                                        headers = {"Authorization": f"Bearer {cauhinh['token']}", "Content-Type": "application/json",
                                                   "User-Agent": "Mozilla/5.0"})
        with _moketnoi(yeucau, 15.) as phanhoi:
            ketqua = json.loads(phanhoi.read().decode("utf-8"))
        gds = [gd for gd in ketqua.get("transactions") or [] if float(gd.get("amount_in") or 0) > 0
               and str(gd.get("transaction_date") or "") >= trangthai["lucbatdau"]]
        return sorted(gds, key = lambda gd: int(gd["id"]))

    def _taodon(self, cauhinh, gd, dons):
        sotien = int(float(gd["amount_in"]))
        noidung = gd.get("transaction_content") or ""
        idnguoichoi = docidnguoichoi(noidung, cauhinh["tiento"])
        don = {"luc": gd.get("transaction_date"), "sotien": sotien, "noidung": noidung, "idnguoichoi": idnguoichoi,
               "nganluong": sotien * int(cauhinh["nganluongmoi1000d"]) // 1000, "trangthai": "chogiao", "ghichu": "", "lucgui": 0, "dathay": None}
        if idnguoichoi is None:
            don.update(trangthai = "xulytay", ghichu = f"nội dung không có đúng 1 ID dạng {cauhinh['tiento']}<số>")
        elif sotien < int(cauhinh.get("sotientoithieu") or 0):
            don.update(trangthai = "xulytay", ghichu = f"dưới tối thiểu {_so(int(cauhinh['sotientoithieu']))}đ")
        else:
            phantram = self._phantramtanglandau(cauhinh, idnguoichoi, dons)
            if phantram:
                # Lưu cả số gốc và phần tặng để đối soát; "nganluong" là tổng sẽ give
                tang = don["nganluong"] * phantram // 100
                don.update(nganluonggoc = don["nganluong"], nganluongtang = tang, nganluong = don["nganluong"] + tang,
                           ghichu = f"lần đầu tặng {phantram}%")
        print(f"[BÁN NL] Giao dịch {gd['id']}: {_so(sotien)}đ \"{noidung}\" -> {don['trangthai']} {don['ghichu']}")
        if don["trangthai"] == "xulytay":
            guitin(f"⚠️ Nhận {_so(sotien)}đ (GD {gd['id']}) nhưng {don['ghichu']}: <i>{html.escape(noidung)}</i>\n"
                   f"Sửa bannganluong_don.json: điền \"idnguoichoi\", đặt \"trangthai\": \"guilai\"", is_html = True)
        else:
            tang = f" (gồm {_so(don['nganluongtang'])} tặng lần đầu)" if don.get("nganluongtang") else ""
            guitin(f"💳 Nhận {_so(sotien)}đ từ ID <b>{idnguoichoi}</b> → {_so(don['nganluong'])} ngân lượng{tang}, chờ người chơi tới Tiệm "
                   f"Tạp Hóa Tân Thủ Thôn", is_html = True)
        return don

    @staticmethod
    def _phantramtanglandau(cauhinh, idnguoichoi, dons):
        # % tặng cho đơn này: chỉ khi ID chưa có đơn nào khác (bỏ qua đơn huỷ / xử lý tay = chưa nhận được gì). Các giao dịch cùng 1 lượt
        # hỏi SePay được thêm vào dons lần lượt nên 2 lần chuyển liền nhau chỉ lần đầu được tặng
        try:
            phantram = max(0, int(cauhinh.get("tanglandau") or 0))
        except (TypeError, ValueError):
            return 0
        if not phantram:
            return 0
        for don in dons.values():
            if don.get("idnguoichoi") == idnguoichoi and don.get("trangthai") not in ("huy", "xulytay"):
                return 0
        return phantram

    def _dongbo(self, cauhinh, hwnd, info, dons):
        # Đối chiếu đơn với hàng chờ giao đồ của nhân vật bán (shared_data "_hangchogiaodo", id yêu cầu = "nl<id giao dịch>-<lần guilai>")
        hangcho = {y["id"]: y for y in info.get("_hangchogiaodo") or []}
        now = time.time()
        for idgd, don in dons.items():
            if don["trangthai"] == "guilai":
                if don.get("idnguoichoi") is None:
                    continue
                # Mã yêu cầu mới: yêu cầu lỗi cũ còn nằm trong danh sách đã kết thúc của bot
                don.update(trangthai = "chogiao", ghichu = "", lucgui = 0, dathay = None, lan = don.get("lan", 0) + 1)
            if don["trangthai"] == "huy":
                # Bỏ đơn: rút khỏi hàng chờ của bot nếu chưa gửi give
                yeucau = hangcho.get(f"nl{idgd}-{don.get('lan', 0)}")
                if yeucau and yeucau["trangthai"] not in ("xong", "lỗi") and not yeucau["trangthai"].startswith(TRANGTHAIBOTDAGUI):
                    self.command_dict[hwnd] = f"huygiaodo:{yeucau['id']}"
                continue
            if don["trangthai"] != "chogiao":
                continue
            mayeucau = f"nl{idgd}-{don.get('lan', 0)}"
            yeucau = hangcho.get(mayeucau)
            if yeucau:
                don["dathay"] = yeucau["trangthai"]
                if yeucau["trangthai"] == "xong":
                    don.update(trangthai = "xong", ghichu = yeucau.get("ghichu") or "", lucxong = time.strftime("%Y-%m-%d %H:%M:%S"))
                elif yeucau["trangthai"] == "lỗi":
                    don.update(trangthai = "loi", ghichu = yeucau.get("ghichu") or "")
                continue
            if don.get("dathay") and don["dathay"].startswith(TRANGTHAIBOTDAGUI):
                don.update(trangthai = "kiemtratay", ghichu = "Foxia đã gửi give rồi mất hàng chờ, chưa rõ đã giao chưa")
                guitin(f"⚠️ Đơn ngân lượng ID <b>{don['idnguoichoi']}</b> ({_so(don['nganluong'])}): {don['ghichu']}. Kiểm tra rồi đặt "
                       f"\"guilai\" nếu chưa nhận", is_html = True)
                continue
            if now - don.get("lucgui", 0) >= THOIGIANCHOBOTNHAN:
                # Chưa đưa lần nào, hoặc bot mất hàng chờ trước khi gửi give (mở lại client): đưa (lại)
                yeucau = dict(taoyeucau(f"ID {don['idnguoichoi']}", don["nganluong"]), id = mayeucau, idnguoichoi = don["idnguoichoi"],
                              is_ban = True, giulaitoithieu = int(cauhinh.get("giulaitoithieu") or 0))
                guiyeucau(self.command_dict, hwnd, yeucau)
                don["lucgui"] = now
                print(f"[BÁN NL] Đưa đơn {idgd} vào hàng chờ {info.get('tennhanvat')}: {_so(don['nganluong'])} ngân lượng cho ID {don['idnguoichoi']}")
