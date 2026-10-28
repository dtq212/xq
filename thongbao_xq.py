# Thông báo về điện thoại qua Telegram. Cấu hình _internal/telegram.json (tự tạo mẫu):
#   - Tạo bot: nhắn @BotFather lệnh /newbot, dán token vào "token", đặt "is_bat": true
#   - Mở bot vừa tạo trên điện thoại, gửi /start: chat đầu tiên nhắn tới được ghi vào "chat_id", từ đó chỉ chat này nhận tin / ra lệnh
#   - "loaisuco": tắt từng loại tin sự cố; "phutbaocao": báo cáo định kỳ mỗi bấy nhiêu phút (0 = tắt)
#   - Nhiều máy chung 1 bot: chép telegram.json (đã có chat_id) sang máy khác, đổi "tenmay" cho khác nhau. Telegram chỉ cho 1 nơi nhận tin
#     của bot tại 1 thời điểm (getUpdates cùng lúc báo 409 Conflict) nên mỗi máy hỏi nhanh (không chờ) mỗi CHUKYHOILENH giây, không xác
#     nhận tin ngay để máy khác cũng đọc được; tin mình thấy quá THOIGIANGIUTIN giây mới xác nhận cho Telegram xoá. Máy nào có nhân vật
#     được gọi tên thì làm, /trangthai /baocao thì máy nào cũng trả lời phần của mình
# Tiến trình bot (từng cửa sổ) gửi tin sự cố qua baosuco / TheoDoiSuCo; tiến trình giao diện chạy DieuKhienTelegram (nhận lệnh + báo cáo)
import hashlib
import html
import json
import os
import random
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from hangso_xq import laytenbando, BANDO_CHIENTRUONG, TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT

CAUHINHMAU = {
    "is_bat": False,
    "token": "",
    "chat_id": "",
    # Tên máy hiện trong mọi tin (để trống = tên máy tính Windows)
    "tenmay": "",
    "phutbaocao": 120,
    "loaisuco": {"chet": True, "bipk": True, "tamngung": True, "giamsat": True, "vatpham": True},
}
TENLOAISUCO = {"chet": "chết", "bipk": "bị người chơi đánh", "tamngung": "tạm ngưng", "giamsat": "kẹt / mở lại client", "vatpham": "vật phẩm"}

# Cùng một tin (khoá) của một tiến trình không gửi lại trong chừng này giây
GIANCACHTINMACDINH = 120.
CHUKYTHEODOI = 5.
BANKINHBIPK = 10.
LYDOTAMNGUNGTUXA = "Tạm ngưng từ Telegram"
CHUKYHOILENH = 1.
THOIGIANGIUTIN = 60.

_cache = {"dulieu": None, "mtime": None}
_khoacauhinh = threading.Lock()
_thoidiemguitheokhoa = {}


def duongdancauhinh():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "telegram.json")


def taicauhinh():
    duongdan = duongdancauhinh()
    with _khoacauhinh:
        if not os.path.exists(duongdan):
            luucauhinh(CAUHINHMAU)
        try:
            mtime = os.path.getmtime(duongdan)
            if mtime != _cache["mtime"]:
                with open(duongdan, encoding = "utf-8-sig") as file:
                    dulieu = json.load(file)
                cauhinh = dict(CAUHINHMAU, **dulieu)
                cauhinh["loaisuco"] = dict(CAUHINHMAU["loaisuco"], **(dulieu.get("loaisuco") or {}))
                _cache.update(dulieu = cauhinh, mtime = mtime)
        except (OSError, ValueError) as err:
            print(f"[TELEGRAM] Lỗi đọc {duongdan}: {err}")
            return dict(CAUHINHMAU)
        return _cache["dulieu"]


def luucauhinh(cauhinh):
    duongdan = duongdancauhinh()
    try:
        os.makedirs(os.path.dirname(duongdan), exist_ok = True)
        with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
            json.dump(cauhinh, file, ensure_ascii = False, indent = 2)
        os.replace(duongdan + ".tmp", duongdan)
    except OSError as err:
        print(f"[TELEGRAM] Lỗi ghi {duongdan}: {err}")


def laytenmay(cauhinh = None):
    return ((cauhinh or taicauhinh()).get("tenmay") or "").strip() or socket.gethostname()


def _goiapi(token, phuongthuc, thamso, thoigiancho = 15.):
    dulieu = urllib.parse.urlencode(thamso).encode("utf-8")
    yeucau = urllib.request.Request(f"https://api.telegram.org/bot{token}/{phuongthuc}", data = dulieu)
    with urllib.request.urlopen(yeucau, timeout = thoigiancho) as phanhoi:
        return json.loads(phanhoi.read().decode("utf-8"))


def _gui(token, chat_id, noidung, is_html = False, nutbam = None, idtin = None):
    # is_html: nội dung định dạng HTML của Telegram (<b>, <i>, <code>); chữ lấy từ game phải qua html.escape.
    # nutbam: reply_markup (nút dưới tin / thanh nút cố định). idtin: sửa tin đó (bấm nút) thay vì gửi tin mới
    thamso = {"chat_id": chat_id, "text": noidung[:4000]}
    if is_html:
        thamso["parse_mode"] = "HTML"
    if nutbam is not None:
        thamso["reply_markup"] = json.dumps(nutbam, ensure_ascii = False)
    if idtin is not None:
        thamso["message_id"] = idtin
    try:
        _goiapi(token, "editMessageText" if idtin is not None else "sendMessage", thamso)
    except urllib.error.HTTPError as err:
        # Làm mới mà nội dung không đổi: Telegram báo 400 "message is not modified", bỏ qua
        if not (idtin is not None and err.code == 400):
            print(f"[TELEGRAM] Gửi tin lỗi: {err}")
    except Exception as err:
        print(f"[TELEGRAM] Gửi tin lỗi: {err}")


def _guidangsoan(token, chat_id):
    try:
        _goiapi(token, "sendChatAction", {"chat_id": chat_id, "action": "typing"}, thoigiancho = 5.)
    except Exception:
        pass


def guitin(noidung, khoa = None, giancach = GIANCACHTINMACDINH, is_html = False):
    # Gửi ở luồng riêng (không chặn bot khi mạng chậm). Trả về False khi đang tắt / chưa cấu hình / trùng tin vừa gửi
    cauhinh = taicauhinh()
    if not cauhinh.get("is_bat") or not cauhinh.get("token") or not cauhinh.get("chat_id"):
        return False
    if khoa is not None:
        now = time.time()
        if now - _thoidiemguitheokhoa.get(khoa, 0.) < giancach:
            return False
        _thoidiemguitheokhoa[khoa] = now
    threading.Thread(target = _gui, args = (cauhinh["token"], cauhinh["chat_id"], noidung, is_html), daemon = True).start()
    return True


BIEUTUONGSUCO = {"chet": "💀", "bipk": "⚔️", "tamngung": "🕵️", "giamsat": "🛠", "vatpham": "🎒"}


def baosuco(moitruong, loai, noidung, khoa = None, giancach = GIANCACHTINMACDINH):
    # Tin sự cố của 1 nhân vật (dòng ngắn cho khỏi xuống dòng trên điện thoại):
    #   💀 <b>tên</b> · bản đồ
    #   nội dung
    #   <i>🖥 tên máy</i>
    # Tắt được theo loại trong "loaisuco"
    cauhinh = taicauhinh()
    if not cauhinh["loaisuco"].get(loai, True):
        return False
    try:
        ten = moitruong.get_tendoituong() or f"ID {moitruong.get_idnguoichoi()}"
        bando = laytenbando(moitruong.get_idbandohientai())
    except Exception:
        ten, bando = "?", "?"
    return guitin(f"{BIEUTUONGSUCO.get(loai, '⚠️')} <b>{html.escape(ten)}</b> · {html.escape(bando)}\n{html.escape(noidung)}"
                  f"\n<i>🖥 {html.escape(laytenmay(cauhinh))}</i>",
                  khoa = (loai, khoa if khoa is not None else noidung), giancach = giancach, is_html = True)


class TheoDoiSuCo:
    # Chạy trong tiến trình bot (cùng vòng giám sát): báo khi nhân vật vừa chết, khi bị người chơi đánh (đang ra đòn, quay mặt về mình
    # và sinh lực mình vừa giảm)
    def __init__(self, moitruong, tactu):
        self.moitruong = moitruong
        self.tactu = tactu
        self._is_chettruoc = None
        self._sinhluctruoc = None

    def step(self):
        moitruong = self.moitruong
        if not moitruong.get_is_nhanvattontai():
            self._is_chettruoc = self._sinhluctruoc = None
            return
        if moitruong.get_idbandohientai() == BANDO_CHIENTRUONG:
            return
        is_chet = bool(moitruong.get_is_nhanvatdachet())
        if is_chet and self._is_chettruoc is False:
            x, y = moitruong.get_toado() or (0, 0)
            baosuco(moitruong, "chet", f"Nhân vật đã chết tại ({round(x)}, {round(y)})", khoa = "chet", giancach = 30.)
        self._is_chettruoc = is_chet

        sinhluc = moitruong.get_sinhlucconlai()
        is_matmau = self._sinhluctruoc is not None and sinhluc is not False and sinhluc < self._sinhluctruoc
        self._sinhluctruoc = sinhluc
        if is_matmau and not is_chet:
            for ten in self._laykeketancong():
                baosuco(moitruong, "bipk", f"Bị {ten} tấn công, còn {moitruong.get_phantramsinhlucconlai():.0f}% sinh lực", khoa = ten, giancach = 180.)

    def _laykeketancong(self):
        moitruong = self.moitruong
        x1, y1 = moitruong.get_toado() or (0, 0)
        tenchunhanphe_map = {}
        tens = []
        for diachi in moitruong._get_diachidoituongxungquanhs():
            if not moitruong.get_is_nguoichoi(diachi) or diachi == moitruong.get_diachicosothongtinnhanvat1():
                continue
            x, y = moitruong.get_toado(diachi)
            if (x - x1) ** 2 + (y - y1) ** 2 > BANKINHBIPK ** 2 or not self.tactu._is_doituongthudich(diachi, tenchunhanphe_map):
                continue
            if moitruong.get_idtuthenhanvat(diachi) in (TUTHENHANVAT_TANCONGVATLY, TUTHENHANVAT_TANCONGPHEPTHUAT) \
                    and moitruong.get_is_huongmatvediem(diachi, x1, y1):
                tens.append(moitruong.get_tendoituong(diachi) or "người lạ")
        return tens


BIEUTUONGTRANGTHAI = {"Tấn công": "⚔️", "Di chuyển": "🏃", "Đã chết": "💀"}


def _so(n):
    return f"{round(n or 0):,}".replace(",", ".")


def _thoigian(giay):
    phut = int(giay or 0) // 60
    return f"{phut // 60}h{phut % 60:02d}"


def _the(dongs):
    # Mỗi nhân vật là 1 thẻ (khung trích dẫn có vạch màu bên trái), dòng ngắn cho vừa màn hình điện thoại
    return "<blockquote>" + "\n".join(dongs) + "</blockquote>"


def _tomtatnhanvat(info, is_daydu = False):
    #   ┃ Thọ · Vũ Lăng Bí Đạo
    #   ┃ 🏃 Di chuyển · ❤️ 96%
    #   ┃ 💰 1.234.567 ngân lượng
    #   ┃ 📈 +81.000/giờ · ⏱ 1h05 · ☠️ 0      (is_daydu)
    status = info.get("status", "-")
    dongs = [f"<b>{html.escape(info.get('tennhanvat') or '?')}</b> · {html.escape(laytenbando(info.get('tenbando')))}",
             f"{BIEUTUONGTRANGTHAI.get(status, '🧍')} {html.escape(status)} · ❤️ {info.get('phantramsinhluc', 0)}%"]
    if info.get("nganluong") is not None:
        dongs.append(f"💰 {_so(info['nganluong'])} ngân lượng")
    if info.get("_thoigiantamngungconlai", 0) > 0:
        dongs.append(f"⏸ <i>{html.escape(info.get('_lydotamngung', ''))}</i> · còn {int(info['_thoigiantamngungconlai']) // 60} phút")
    elif info.get("_is_tudongsudungkynang") is False:
        dongs.append("⚠️ <i>Đang tắt tự động tấn công</i>")
    if is_daydu:
        phien = info.get("_thongkephien") or {}
        giay = phien.get("giay", 0)
        tylegio = f"📈 +{_so(phien.get('nganluong', 0) * 3600. / giay)}/giờ · " if giay >= 60 else ""
        dongs.append(f"{tylegio}⏱ {_thoigian(giay)} · ☠️ {phien.get('chet', 0)}")
        if phien.get("kinhnghiem"):
            dongs.append(f"✨ +{_so(phien['kinhnghiem'])} kinh nghiệm")
    return _the(dongs)


def _tieude(tieude):
    return f"<b>{tieude}</b>\n🖥 {html.escape(laytenmay())} · 🕒 {time.strftime('%H:%M:%S')}"


def taobaocao(cacinfo, tieude, is_daydu):
    # Cả tin: tiêu đề, mỗi nhân vật 1 thẻ, cuối là tổng ngân lượng
    cacinfo = sorted(cacinfo, key = lambda i: i.get("tennhanvat") or "")
    tongnganluong = sum(i.get("nganluong") or 0 for i in cacinfo)
    return "\n".join([_tieude(tieude)] + [_tomtatnhanvat(i, is_daydu) for i in cacinfo] + [f"💰 Tổng: <b>{_so(tongnganluong)}</b> ngân lượng"])


def taothongkehomnay(cacinfo):
    # Từ file thống kê (thongke_xq, cập nhật mỗi phút): thời gian, ngân lượng nhận, bãi tốt nhất, đồ nhặt nhiều nhất của hôm nay
    from thongke_xq import taithongke, gopthongke
    tugio = time.strftime("%Y-%m-%d 00")
    thes = []
    tongnhan = 0
    for info in sorted(cacinfo, key = lambda i: i.get("tennhanvat") or ""):
        if not info.get("idnguoichoi"):
            continue
        cacos = gopthongke(taithongke(info["idnguoichoi"]), tugio)
        giay = sum(o["giay"] for o in cacos.values())
        nhan = sum(o["nganluongthu"] for o in cacos.values())
        tongnhan += nhan
        dongs = [f"<b>{html.escape(info.get('tennhanvat') or '?')}</b>"]
        if giay < 60:
            dongs.append("<i>Chưa có số liệu hôm nay</i>")
            thes.append(_the(dongs))
            continue
        dongs.append(f"⏱ {_thoigian(giay)} · 💰 +{_so(nhan)} · 📈 {_so(nhan * 3600. / giay)}/giờ")
        dongs.append(f"☠️ chết {sum(o['chet'] for o in cacos.values())} lần · 💸 tiêu {_so(sum(o['nganluongchi'] for o in cacos.values()))}")
        totnhat = max(((k, o) for k, o in cacos.items() if o["giay"] >= 600), key = lambda m: m[1]["nganluongthu"] / m[1]["giay"], default = None)
        if totnhat:
            idbando, _, lotrinh = totnhat[0].partition("|")
            dongs.append(f"🏆 {html.escape(laytenbando(idbando))} – {html.escape(lotrinh)}: {_so(totnhat[1]['nganluongthu'] * 3600. / totnhat[1]['giay'])}/giờ")
        vatphams = {}
        for o in cacos.values():
            for ten, soluong in o["vatphamnhan"].items():
                vatphams[ten] = vatphams.get(ten, 0) + soluong
        if vatphams:
            dongs.append("🎁 " + ", ".join(f"{html.escape(ten)} ×{_so(sl)}" for ten, sl in sorted(vatphams.items(), key = lambda m: -m[1])[:3]))
        thes.append(_the(dongs))
    if not thes:
        return None
    return "\n".join([_tieude("📈 Hôm nay")] + thes + [f"💰 Cả máy nhận: <b>{_so(tongnhan)}</b> ngân lượng"])


def chupcuaso(hwnd):
    # Ảnh JPEG vùng trong cửa sổ game, chụp bằng PrintWindow nên cửa sổ bị che vẫn chụp được (thu nhỏ thì không)
    import ctypes
    import io
    import win32gui
    import win32ui
    from PIL import Image
    _, _, rong, cao = win32gui.GetClientRect(hwnd)
    if rong <= 0 or cao <= 0:
        return None
    hdc = win32gui.GetWindowDC(hwnd)
    mfc = win32ui.CreateDCFromHandle(hdc)
    bonho = mfc.CreateCompatibleDC()
    anh = win32ui.CreateBitmap()
    try:
        anh.CreateCompatibleBitmap(mfc, rong, cao)
        bonho.SelectObject(anh)
        # 3 = PW_CLIENTONLY | PW_RENDERFULLCONTENT
        ctypes.windll.user32.PrintWindow(hwnd, bonho.GetSafeHdc(), 3)
        thongtin = anh.GetInfo()
        hinh = Image.frombuffer("RGB", (thongtin["bmWidth"], thongtin["bmHeight"]), anh.GetBitmapBits(True), "raw", "BGRX", 0, 1)
    finally:
        win32gui.DeleteObject(anh.GetHandle())
        bonho.DeleteDC()
        mfc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hdc)
    dem = io.BytesIO()
    hinh.save(dem, "JPEG", quality = 85)
    return dem.getvalue()


def _guianh(token, chat_id, anh, chuthich):
    # sendPhoto dạng multipart/form-data (urllib không có sẵn)
    ranhgioi = "----xq" + hashlib.md5(str(time.time()).encode()).hexdigest()
    phans = []
    for ten, giatri in (("chat_id", str(chat_id)), ("caption", chuthich), ("parse_mode", "HTML")):
        phans.append(f'--{ranhgioi}\r\nContent-Disposition: form-data; name="{ten}"\r\n\r\n{giatri}\r\n'.encode("utf-8"))
    phans.append(f'--{ranhgioi}\r\nContent-Disposition: form-data; name="photo"; filename="game.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode("utf-8"))
    phans.append(anh + f"\r\n--{ranhgioi}--\r\n".encode("utf-8"))
    yeucau = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendPhoto", data = b"".join(phans),
                                    headers = {"Content-Type": f"multipart/form-data; boundary={ranhgioi}"})
    try:
        with urllib.request.urlopen(yeucau, timeout = 30) as phanhoi:
            phanhoi.read()
    except Exception as err:
        print(f"[TELEGRAM] Gửi ảnh lỗi: {err}")


def chuanhoalenh(chu):
    # "/Trạng thái", "📋 Trạng thái", "trangthai" -> "trangthai": bỏ dấu, emoji, dấu cách, "/" và "@tên_bot"
    import unicodedata
    chu = chu.split("@")[0].lower().replace("đ", "d")
    chu = "".join(k for k in unicodedata.normalize("NFD", chu) if unicodedata.category(k) != "Mn")
    return "".join(k for k in chu if k.isascii() and k.isalnum())


NUT_TRANGTHAI = "📋 Trạng thái"
NUT_BAOCAO = "📊 Báo cáo"
NUT_HOMNAY = "📈 Hôm nay"
NUT_DIEUKHIEN = "🎮 Điều khiển"
NUT_CHUPMANHINH = "📸 Chụp màn hình"
NUT_TAMDUNG = "⏸ Tạm dừng"
NUT_TIEPTUC = "▶️ Tiếp tục"
# Thanh nút cố định dưới ô nhập tin, cả 7 nút trên 1 hàng (người dùng muốn vậy; điện thoại hẹp thì chữ bị cắt bớt): bấm là gửi đúng chữ trên nút
THANHNUT = {"keyboard": [[NUT_TRANGTHAI, NUT_BAOCAO, NUT_HOMNAY, NUT_DIEUKHIEN, NUT_CHUPMANHINH, NUT_TAMDUNG, NUT_TIEPTUC]],
            "resize_keyboard": True, "is_persistent": True}
# Tên lệnh Telegram chỉ được chữ thường không dấu (a-z, 0-9, _): menu "/" dùng tên không dấu, mô tả có dấu. Gõ tay "/trạng thái",
# "/tạm dừng Thọ 30"... vẫn hiểu (chuanhoalenh)
MENULENH = [{"command": "trangthai", "description": "📋 Trạng thái nhân vật"}, {"command": "baocao", "description": "📊 Báo cáo phiên này"},
            {"command": "homnay", "description": "📈 Thống kê hôm nay"}, {"command": "dieukhien", "description": "🎮 Bảng điều khiển"},
            {"command": "chupmanhinh", "description": "📸 Chụp màn hình game"}, {"command": "tamdung", "description": "⏸ Tạm dừng"},
            {"command": "tieptuc", "description": "▶️ Tiếp tục"}, {"command": "menu", "description": "Hiện thanh nút"}]
# Lệnh (đã chuẩn hoá) -> loại
LENH_MAP = {"trangthai": "trangthai", "baocao": "baocao", "homnay": "homnay", "thongkehomnay": "homnay", "dieukhien": "dieukhien",
            "chupmanhinh": "chupmanhinh", "chup": "chupmanhinh", "tamdung": "tamdung", "tamngung": "tamdung", "tieptuc": "tieptuc",
            "batlai": "tieptuc"}
PHUTTAMNGUNGs = (15, 30, 60, 120)
GIANCACHBAMTRUNG = 15.
HUONGDAN = ("📋 <b>Trạng thái</b> – nhân vật đang làm gì\n📊 <b>Báo cáo</b> – ngân lượng, thời gian phiên này\n"
            "📈 <b>Hôm nay</b> – thống kê cả ngày, bãi tốt nhất\n🎮 <b>Điều khiển</b> – bật/tắt tấn công, theo sau, gom quái, farm, di chuyển tự do\n"
            "📸 <b>Chụp màn hình</b> – xem cửa sổ game\n⏸ <b>Tạm dừng</b> / ▶️ <b>Tiếp tục</b>\n\n"
            "Gõ tay cũng được: <code>/tạm dừng Thọ 30</code>, <code>/tiếp tục tất cả</code>")
# Thao tác trong bảng điều khiển: mã -> (chữ trên nút, lệnh gửi bot, khoá trạng thái bật/tắt trong shared_data)
THAOTAC = {
    "tc": ("⚔️ Tấn công", "battat_tudongsudungkynang", "_is_tudongsudungkynang"),
    "ts": ("👣 Theo sau", "battat_tudongtheosau", "_is_tudongtheosau"),
    "gq": ("🧲 Gom quái", "battat_tudonggomquai", "_is_tudonggomquai"),
    "fr": ("🛒 Farm & bán rác", "battat_tudongvebanrac", "_is_tudongvebanrac"),
    "dc": ("🧭 Di chuyển lộ trình", "battat_tudongdichuyendiemdanhxungquanh", "_is_tudongdichuyendiemdanhxungquanh"),
}


def _nut(chu, dulieu):
    return {"text": chu, "callback_data": dulieu}


class DieuKhienTelegram:
    # Chạy trong tiến trình giao diện (1 luồng cho cả máy): nhận lệnh / bấm nút từ chat đã ghi, gửi báo cáo định kỳ.
    # Nút dưới tin (callback_data "<loại>|<mã máy>|<nhân vật>|<thêm>") chỉ máy có đúng mã máy xử lý, máy khác bỏ qua:
    #   tn: chọn nhân vật tạm dừng -> hỏi bao lâu   tp: tạm dừng   tt: tiếp tục   lm: làm mới   huy: huỷ
    #   dk: mở bảng điều khiển (không nhân vật = danh sách nhân vật)   ac: thao tác THAOTAC   cm: chụp màn hình   ml/mlok: mở lại client
    # Nhân vật là hwnd cửa sổ (khoá shared_data) hoặc "all" = cả máy này
    def __init__(self, shared_data, command_dict):
        self.shared_data = shared_data
        self.command_dict = command_dict
        # Tin đã xác nhận với Telegram (offset) và tin đã xử lý trên máy này: {update_id: thời điểm thấy lần đầu}
        self._offset = None
        self._dathay = {}
        self._thoidiembaocao = time.time()
        self._is_dadatmenu = False
        # Nút đã xử lý: {(id tin, callback_data): thời điểm}. Telegram không khoá được nút, bấm liền 2-3 lần trong 1 nhịp hỏi thành
        # 2-3 lần bấm riêng (vd gửi 2-3 ảnh chụp): cùng nút trên cùng tin trong GIANCACHBAMTRUNG giây thì bỏ qua
        self._dabamnut = {}

    def batdau(self):
        threading.Thread(target = self.loop, daemon = True).start()

    def loop(self):
        while True:
            cauhinh = taicauhinh()
            if not cauhinh.get("is_bat") or not cauhinh.get("token"):
                time.sleep(10)
                continue
            try:
                if not self._is_dadatmenu:
                    _goiapi(cauhinh["token"], "setMyCommands", {"commands": json.dumps(MENULENH, ensure_ascii = False)})
                    self._is_dadatmenu = True
                self._nhanlenh(cauhinh)
                self._baocaodinhky(cauhinh)
            except urllib.error.HTTPError as err:
                # 409: máy khác đang hỏi đúng lúc này, lượt sau hỏi lại
                if err.code != 409:
                    print(f"[TELEGRAM] Lỗi: {err}")
                    time.sleep(10)
            except Exception as err:
                print(f"[TELEGRAM] Lỗi: {err}")
                time.sleep(10)
            # Lệch nhịp ngẫu nhiên cho các máy ít hỏi trùng lúc
            time.sleep(CHUKYHOILENH + random.random() * 0.5)

    @staticmethod
    def _mamay():
        # Mã ngắn của máy cho callback_data (giới hạn 64 byte, tên máy có dấu thì dài)
        return hashlib.md5(laytenmay().encode("utf-8")).hexdigest()[:8]

    def _nhanlenh(self, cauhinh):
        # Hỏi không chờ (timeout 0): giữ kết nối lâu thì máy khác hỏi là bị 409. Offset chỉ tiến tới tin mình đã thấy quá THOIGIANGIUTIN
        # giây (các máy khác đang chạy cũng đã kịp đọc), tin mới hơn để nguyên cho máy khác
        thamso = {"timeout": 0}
        if self._offset is not None:
            thamso["offset"] = self._offset
        ketqua = _goiapi(cauhinh["token"], "getUpdates", thamso)
        now = time.time()
        for capnhat in ketqua.get("result", []):
            idcapnhat = capnhat["update_id"]
            if idcapnhat in self._dathay:
                continue
            self._dathay[idcapnhat] = now
            if capnhat.get("callback_query"):
                self._xulynut(cauhinh, capnhat["callback_query"])
                continue
            tinnhan = capnhat.get("message") or {}
            chat_id = str((tinnhan.get("chat") or {}).get("id", ""))
            noidung = (tinnhan.get("text") or "").strip()
            if not chat_id or not noidung:
                continue
            if not cauhinh.get("chat_id"):
                # Chat đầu tiên nhắn tới bot: nhận làm chủ
                cauhinh = dict(cauhinh, chat_id = chat_id)
                luucauhinh(cauhinh)
                _gui(cauhinh["token"], chat_id, f"🖥 <b>{html.escape(laytenmay(cauhinh))}</b> đã kết nối với bot Chiến Quốc\n\n{HUONGDAN}",
                     True, THANHNUT)
                continue
            if chat_id != str(cauhinh["chat_id"]):
                continue
            traloi = self._xulylenh(noidung)
            if traloi:
                # "đang soạn tin…" hiện tới khi có tin trả lời (tối đa 5s): các máy khác hỏi sau vài nhịp vẫn còn đang trả lời tiếp
                _guidangsoan(cauhinh["token"], chat_id)
                _gui(cauhinh["token"], chat_id, *traloi)
        cuxacnhans = [idcapnhat for idcapnhat, thoidiem in self._dathay.items() if now - thoidiem >= THOIGIANGIUTIN]
        if cuxacnhans:
            self._offset = max(cuxacnhans) + 1
            self._dathay = {idcapnhat: thoidiem for idcapnhat, thoidiem in self._dathay.items() if idcapnhat >= self._offset}

    def _cacnhanvat(self):
        return {hwnd: info for hwnd, info in dict(self.shared_data.items()).items() if isinstance(info, dict)}

    def _timnhanvat(self, ten):
        cacnhanvat = self._cacnhanvat()
        if chuanhoalenh(ten) in ("tatca", "all", ""):
            return list(cacnhanvat)
        return [hwnd for hwnd, info in cacnhanvat.items() if chuanhoalenh(ten) in chuanhoalenh(info.get("tennhanvat") or "")]

    def _tennhanvats(self, hwnds):
        cacnhanvat = self._cacnhanvat()
        return ", ".join(cacnhanvat.get(h, {}).get("tennhanvat") or str(h) for h in hwnds)

    def _guilenhbot(self, hwnds, phut):
        # phut: tạm dừng bấy nhiêu phút, None = tiếp tục
        for hwnd in hwnds:
            self.command_dict[hwnd] = f"tamngungtuxa:{phut * 60}" if phut else "tieptuchoatdong"

    def _trangthai(self, is_baocao):
        # (nội dung, is_html, nút) của Trạng thái / Báo cáo máy này, kèm nút Làm mới
        cacnhanvat = self._cacnhanvat()
        if not cacnhanvat:
            return f"🖥 <b>{html.escape(laytenmay())}</b>: không có nhân vật nào đang chạy bot", True, None
        noidung = taobaocao(cacnhanvat.values(), "📊 Báo cáo" if is_baocao else "📋 Trạng thái", is_baocao)
        mamay = self._mamay()
        return noidung, True, {"inline_keyboard": [[_nut("🔄 Làm mới", f"lm|{mamay}|{'bc' if is_baocao else 'tt'}"),
                                                    _nut("🎮 Điều khiển", f"dk|{mamay}")]]}

    def _chonnhanvat(self, loai, tieude):
        # Tin chọn nhân vật của máy này: cả các nhân vật trên 1 hàng (đang tạm dừng có dấu ⏸), loai là loại callback khi bấm
        cacnhanvat = self._cacnhanvat()
        if not cacnhanvat:
            return None
        mamay = self._mamay()
        nuts = []
        for hwnd, info in sorted(cacnhanvat.items(), key = lambda m: m[1].get("tennhanvat") or ""):
            dau = "⏸ " if info.get("_thoigiantamngungconlai", 0) > 0 else ""
            nuts.append(_nut(f"{dau}{info.get('tennhanvat') or hwnd}", f"{loai}|{mamay}|{hwnd}"))
        hangcuoi = [_nut("🖥 Cả máy này", f"{loai}|{mamay}|all")] if loai in ("tn", "tt", "cm") else []
        hangs = [nuts, hangcuoi + [_nut("✖️ Đóng", f"huy|{mamay}")]]
        return f"{tieude}\n🖥 {html.escape(laytenmay())} · chọn nhân vật:", True, {"inline_keyboard": hangs}

    def _bangdieukhien(self, hwnd, thongbao = ""):
        # Bảng điều khiển 1 nhân vật: thẻ trạng thái + nút thao tác (nút bật/tắt hiện trạng thái hiện tại)
        info = self._cacnhanvat().get(hwnd)
        if not info:
            return "Nhân vật không còn chạy bot", False, None
        mamay = self._mamay()
        nuts = []
        for ma, (chu, _, khoa) in THAOTAC.items():
            if khoa:
                chu = f"{chu}: {'✅ Bật' if info.get(khoa) else '⬜ Tắt'}"
            nuts.append(_nut(chu, f"ac|{mamay}|{hwnd}|{ma}"))
        hangs = [nuts[i:i + 2] for i in range(0, len(nuts), 2)]
        is_tamdung = info.get("_thoigiantamngungconlai", 0) > 0
        hangs.append([_nut("▶️ Tiếp tục" if is_tamdung else "⏸ Tạm dừng", f"{'tt' if is_tamdung else 'tn'}|{mamay}|{hwnd}"),
                      _nut("📸 Chụp màn hình", f"cm|{mamay}|{hwnd}")])
        hangs.append([_nut("🔁 Mở lại client", f"ml|{mamay}|{hwnd}"), _nut("🔄 Làm mới", f"dk|{mamay}|{hwnd}")])
        hangs.append([_nut("↩️ Nhân vật khác", f"dk|{mamay}"), _nut("✖️ Đóng", f"huy|{mamay}")])
        noidung = f"<b>🎮 Điều khiển</b>\n🖥 {html.escape(laytenmay())} · 🕒 {time.strftime('%H:%M:%S')}\n{_tomtatnhanvat(info, True)}"
        if thongbao:
            noidung += f"\n{thongbao}"
        return noidung, True, {"inline_keyboard": hangs}

    def _xulylenh(self, noidung):
        # Trả về (nội dung trả lời, is_html, nút), None = máy này không trả lời (lệnh cho nhân vật ở máy khác)
        tus = noidung.split()
        # Lệnh 1 hoặc 2 chữ ("/tạm dừng Thọ 30", "📋 Trạng thái"), phần sau là tham số
        loai, thamsos = None, []
        for sotu in (2, 1, 3):
            if len(tus) >= sotu and chuanhoalenh("".join(tus[:sotu])) in LENH_MAP:
                loai, thamsos = LENH_MAP[chuanhoalenh("".join(tus[:sotu]))], tus[sotu:]
                break
        if loai in ("trangthai", "baocao"):
            return self._trangthai(loai == "baocao")
        if loai == "homnay":
            noidung = taothongkehomnay(self._cacnhanvat().values())
            return (noidung, True, None) if noidung else None
        if loai == "dieukhien":
            return self._chonnhanvat("dk", "<b>🎮 Điều khiển</b>")
        if loai == "chupmanhinh":
            return self._chonnhanvat("cm", "<b>📸 Chụp màn hình</b>")
        if loai in ("tamdung", "tieptuc") and not thamsos:
            return self._chonnhanvat("tn" if loai == "tamdung" else "tt", "<b>⏸ Tạm dừng</b>" if loai == "tamdung" else "<b>▶️ Tiếp tục</b>")
        if loai in ("tamdung", "tieptuc"):
            is_tamdung = loai == "tamdung"
            phut = 60
            if is_tamdung and len(thamsos) >= 2 and thamsos[-1].isdigit():
                phut = int(thamsos[-1])
                thamsos = thamsos[:-1]
            hwnds = self._timnhanvat(" ".join(thamsos))
            if not hwnds:
                # Có thể nhân vật ở máy khác: im lặng, máy có nhân vật sẽ trả lời
                return None
            self._guilenhbot(hwnds, phut if is_tamdung else None)
            viec = f"⏸ Đã tạm dừng {phut} phút" if is_tamdung else "▶️ Đã tiếp tục"
            return f"{viec}: <b>{html.escape(self._tennhanvats(hwnds))}</b>\n🖥 {html.escape(laytenmay())}", True, None
        # /start, /menu, lệnh lạ: máy nào cũng báo sẵn sàng (biết luôn máy nào đang chạy) kèm thanh nút
        return f"🖥 <b>{html.escape(laytenmay())}</b> sẵn sàng · {len(self._cacnhanvat())} nhân vật\n\n{HUONGDAN}", True, THANHNUT

    def _xulynut(self, cauhinh, bam):
        token = cauhinh["token"]
        tinnhan = bam.get("message") or {}
        chat_id = str((tinnhan.get("chat") or {}).get("id", ""))
        phan = (bam.get("data") or "").split("|")
        if chat_id != str(cauhinh.get("chat_id")) or len(phan) < 2 or phan[1] != self._mamay():
            return
        loai, idtin = phan[0], tinnhan.get("message_id")
        now = time.time()
        self._dabamnut = {k: t for k, t in self._dabamnut.items() if now - t < GIANCACHBAMTRUNG}
        khoabam = (idtin, bam.get("data"))
        if khoabam in self._dabamnut:
            self._traloinut(token, bam, "⏳ Đang xử lý, chờ chút…")
            return
        self._dabamnut[khoabam] = now
        tenmay = html.escape(laytenmay())
        cacnhanvat = self._cacnhanvat()
        doituong = phan[2] if len(phan) >= 3 else ""
        hwnds = list(cacnhanvat) if doituong == "all" else [h for h in cacnhanvat if str(h) == doituong]
        hwnd = hwnds[0] if len(hwnds) == 1 and doituong != "all" else None
        ten = "cả máy" if doituong == "all" else html.escape(self._tennhanvats(hwnds))
        thongbao = ""
        sua = lambda traloi: _gui(token, chat_id, *traloi, idtin = idtin)

        if loai == "huy":
            sua((f"✖️ Đã đóng · 🖥 {tenmay}", True, None))
        elif loai == "lm" and doituong in ("tt", "bc"):
            sua(self._trangthai(doituong == "bc"))
            thongbao = "Đã làm mới"
        elif loai == "dk" and not doituong:
            traloi = self._chonnhanvat("dk", "<b>🎮 Điều khiển</b>")
            sua(traloi or (f"🖥 {tenmay}: không có nhân vật nào", True, None))
        elif doituong and not hwnds:
            thongbao = "Nhân vật không còn chạy bot"
        elif loai == "dk" and hwnd:
            sua(self._bangdieukhien(hwnd))
        elif loai == "ac" and hwnd and len(phan) >= 4 and phan[3] in THAOTAC:
            chu, lenh, khoa = THAOTAC[phan[3]]
            # Gỡ nút ngay (Telegram không khoá được nút) cho khỏi bấm tiếp trong lúc chờ
            sua((f"⏳ Đang gửi lệnh <b>{chu}</b> cho <b>{ten}</b>…\n🖥 {tenmay}", True, None))
            self.command_dict[hwnd] = lenh
            # Chờ bot nhận lệnh và cập nhật shared_data rồi mới vẽ lại trạng thái bật/tắt
            time.sleep(1.5)
            sua(self._bangdieukhien(hwnd, f"✅ Đã gửi: {chu}"))
            thongbao = f"Đã gửi: {chu}"
        elif loai == "cm":
            thongbao = "Đang chụp…"
            self._traloinut(token, bam, thongbao)
            sua((f"📸 Đang chụp <b>{ten}</b>…\n🖥 {tenmay}", True, None))
            for h in hwnds:
                try:
                    anh = chupcuaso(h)
                except Exception as err:
                    print(f"[TELEGRAM] Chụp màn hình lỗi: {err}")
                    anh = None
                info = cacnhanvat.get(h, {})
                if anh:
                    _guianh(token, chat_id, anh, f"📸 <b>{html.escape(info.get('tennhanvat') or str(h))}</b> · "
                                                 f"{html.escape(laytenbando(info.get('tenbando')))}\n🖥 {tenmay} · 🕒 {time.strftime('%H:%M:%S')}")
            # Xong mới hiện lại nút; "Chụp lại" thêm mốc thời gian vào dữ liệu nút cho khỏi bị coi là bấm trùng
            nuts = [_nut("📸 Chụp lại", f"cm|{phan[1]}|{doituong}|{int(now) % 100000}")]
            if hwnd:
                nuts.append(_nut("🎮 Điều khiển", f"dk|{phan[1]}|{hwnd}"))
            sua((f"📸 Đã gửi ảnh <b>{ten}</b> · 🕒 {time.strftime('%H:%M:%S')}\n🖥 {tenmay}", True,
                 {"inline_keyboard": [nuts + [_nut("✖️ Đóng", f"huy|{phan[1]}")]]}))
            return
        elif loai == "ml" and hwnd:
            sua((f"🔁 <b>Mở lại client {ten}?</b>\nGame sẽ bị đóng rồi tự đăng nhập lại.\n🖥 {tenmay}", True,
                 {"inline_keyboard": [[_nut("✅ Mở lại", f"mlok|{phan[1]}|{hwnd}"), _nut("↩️ Thôi", f"dk|{phan[1]}|{hwnd}")]]}))
        elif loai == "mlok" and hwnd:
            sua((f"⏳ Đang đóng client <b>{ten}</b>…\n🖥 {tenmay}", True, None))
            sua((self._molaiclient(hwnd, ten, tenmay), True, {"inline_keyboard": [[_nut("↩️ Nhân vật khác", f"dk|{phan[1]}")]]}))
        elif loai == "tn":
            # Đã chọn nhân vật: hỏi tạm dừng bao lâu
            nuts = [_nut(f"{p} phút" if p < 60 else f"{p // 60} giờ", f"tp|{phan[1]}|{doituong}|{p}") for p in PHUTTAMNGUNGs]
            sua((f"⏸ <b>Tạm dừng {ten}</b> bao lâu?\n🖥 {tenmay}", True, {"inline_keyboard": [nuts, [_nut("✖️ Huỷ", f"huy|{phan[1]}")]]}))
        elif loai == "tp" and len(phan) >= 4 and phan[3].isdigit():
            phut = int(phan[3])
            self._guilenhbot(hwnds, phut)
            sua((f"⏸ Đã tạm dừng <b>{ten}</b> {phut} phút\n🖥 {tenmay}", True,
                 {"inline_keyboard": [[_nut("▶️ Tiếp tục", f"tt|{phan[1]}|{doituong}")]]}))
            thongbao = f"Đã tạm dừng {phut} phút"
        elif loai == "tt":
            self._guilenhbot(hwnds, None)
            sua((f"▶️ Đã tiếp tục <b>{ten}</b>\n🖥 {tenmay}", True, None))
            thongbao = "Đã tiếp tục"
        self._traloinut(token, bam, thongbao)

    @staticmethod
    def _traloinut(token, bam, thongbao):
        # Tắt vòng xoay chờ trên nút (chỉ máy xử lý mới trả lời), thongbao hiện thành dòng nhỏ trên đầu màn hình
        try:
            _goiapi(token, "answerCallbackQuery", {"callback_query_id": bam.get("id"), "text": thongbao}, thoigiancho = 5.)
        except Exception:
            pass

    def _molaiclient(self, hwnd, ten, tenmay):
        # Đóng game của nhân vật để tự đăng nhập (dangnhap_xq) mở lại; đang tắt tự đăng nhập thì không đóng (sẽ mất nhân vật luôn)
        from dangnhap_xq import taicauhinhdangnhap
        if not taicauhinhdangnhap().get("is_tudongdangnhap"):
            return f"⚠️ Không mở lại <b>{ten}</b>: đang tắt tự động đăng nhập\n🖥 {tenmay}"
        import subprocess
        import win32process
        try:
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output = True)
        except Exception as err:
            return f"⚠️ Không đóng được client <b>{ten}</b>: {html.escape(str(err))}\n🖥 {tenmay}"
        return f"🔁 Đã đóng client <b>{ten}</b>, đang chờ tự đăng nhập lại\n🖥 {tenmay}"

    def _baocaodinhky(self, cauhinh):
        phut = cauhinh.get("phutbaocao") or 0
        if phut <= 0 or time.time() - self._thoidiembaocao < phut * 60:
            return
        self._thoidiembaocao = time.time()
        cacnhanvat = self._cacnhanvat()
        if cacnhanvat and cauhinh.get("chat_id"):
            noidung, is_html, nut = self._trangthai(True)
            _gui(cauhinh["token"], cauhinh["chat_id"], noidung.replace("📊 Báo cáo", "📊 Báo cáo định kỳ", 1), is_html, nut)
