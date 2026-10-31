# Bán ngân lượng lấy tiền chuyển khoản: người chơi chuyển khoản với nội dung "<tiền tố><ID nhân vật>" (vd NL12345), bot hỏi API SePay
# thấy giao dịch tiền vào thì quy ra ngân lượng, đưa vào hàng chờ giao đồ (tactu_giaodo_xq) của nhân vật bán; nhân vật bán về Tân Thủ
# Thôn đứng cạnh Chủ Tiệm Tạp Hóa chờ (không giới hạn) tới khi người chơi có ID đó lại gần thì give.
# Cấu hình _internal/bannganluong.json (tự tạo mẫu, đang tắt):
#   - "token": API token SePay (my.sepay.vn: Cấu hình Công ty -> API Access -> Thêm), "sotaikhoan": chỉ nhận tiền vào tài khoản này
#     (để trống = mọi tài khoản đã nối SePay)
#   - "tiento": tiền tố trước ID trong nội dung chuyển khoản; "nganluongmoi1000d": 1.000đ đổi được bao nhiêu ngân lượng;
#     "sotientoithieu": dưới số tiền này thì không tự giao (báo Telegram xử lý tay)
#   - "idnhanvatban": ID người chơi của nhân vật bán. Chỉ máy đang chạy nhân vật này mới hỏi SePay và giao (máy khác chép cùng cấu hình
#     cũng không giao trùng)
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
}
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


def _so(n):
    return f"{n:,}".replace(",", ".")


class BanNganLuong:
    # Chạy trong tiến trình giao diện (1 luồng cho cả máy), cạnh DieuKhienTelegram
    def __init__(self, shared_data, command_dict):
        self.shared_data = shared_data
        self.command_dict = command_dict
        self._luchoisepay = 0.
        self._trangthai_log = None

    def batdau(self):
        threading.Thread(target = self.loop, daemon = True).start()

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
                    dons[str(gd["id"])] = self._taodon(cauhinh, gd)

        self._dongbo(cauhinh, hwnd, info, dons)
        _ghijson(duongdandon(), trangthai)

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

    def _taodon(self, cauhinh, gd):
        sotien = int(float(gd["amount_in"]))
        noidung = gd.get("transaction_content") or ""
        idnguoichoi = docidnguoichoi(noidung, cauhinh["tiento"])
        don = {"luc": gd.get("transaction_date"), "sotien": sotien, "noidung": noidung, "idnguoichoi": idnguoichoi,
               "nganluong": sotien * int(cauhinh["nganluongmoi1000d"]) // 1000, "trangthai": "chogiao", "ghichu": "", "lucgui": 0, "dathay": None}
        if idnguoichoi is None:
            don.update(trangthai = "xulytay", ghichu = f"nội dung không có đúng 1 ID dạng {cauhinh['tiento']}<số>")
        elif sotien < int(cauhinh.get("sotientoithieu") or 0):
            don.update(trangthai = "xulytay", ghichu = f"dưới tối thiểu {_so(int(cauhinh['sotientoithieu']))}đ")
        print(f"[BÁN NL] Giao dịch {gd['id']}: {_so(sotien)}đ \"{noidung}\" -> {don['trangthai']} {don['ghichu']}")
        if don["trangthai"] == "xulytay":
            guitin(f"⚠️ Nhận {_so(sotien)}đ (GD {gd['id']}) nhưng {don['ghichu']}: <i>{html.escape(noidung)}</i>\n"
                   f"Sửa bannganluong_don.json: điền \"idnguoichoi\", đặt \"trangthai\": \"guilai\"", is_html = True)
        else:
            guitin(f"💳 Nhận {_so(sotien)}đ từ ID <b>{idnguoichoi}</b> → {_so(don['nganluong'])} ngân lượng, chờ người chơi tới Tiệm Tạp Hóa "
                   f"Tân Thủ Thôn", is_html = True)
        return don

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
                don.update(trangthai = "kiemtratay", ghichu = "bot đã gửi give rồi mất hàng chờ, chưa rõ đã giao chưa")
                guitin(f"⚠️ Đơn ngân lượng ID <b>{don['idnguoichoi']}</b> ({_so(don['nganluong'])}): {don['ghichu']}. Kiểm tra rồi đặt "
                       f"\"guilai\" nếu chưa nhận", is_html = True)
                continue
            if now - don.get("lucgui", 0) >= THOIGIANCHOBOTNHAN:
                # Chưa đưa lần nào, hoặc bot mất hàng chờ trước khi gửi give (mở lại client): đưa (lại)
                yeucau = dict(taoyeucau(f"ID {don['idnguoichoi']}", don["nganluong"]), id = mayeucau, idnguoichoi = don["idnguoichoi"],
                              is_ban = True)
                guiyeucau(self.command_dict, hwnd, yeucau)
                don["lucgui"] = now
                print(f"[BÁN NL] Đưa đơn {idgd} vào hàng chờ {info.get('tennhanvat')}: {_so(don['nganluong'])} ngân lượng cho ID {don['idnguoichoi']}")
