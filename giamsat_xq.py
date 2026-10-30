# Watchdog trong tiến trình bot của từng cửa sổ, bổ sung cho dangnhap_xq (client mất / treo "Not responding" / bị dis đã có ở đó):
#   1. Nhân vật kẹt: đang tự đánh theo lộ trình mà quá THOIGIANKETLAMMOI giây không đổi tọa độ / bản đồ / mục tiêu, không lên kinh nghiệm,
#      không đổi ngân lượng / số vật phẩm hành trang (kinh nghiệm đầy ở cấp tối đa thì không tăng nữa, nên không chỉ dựa vào nó) (kẹt vật cản, lệch đồng bộ với server, mạng chết ngầm mà client vẫn hiện trong game) => ngắt di chuyển, bỏ mục tiêu,
#      chọn lại điểm đánh gần nhất. Vẫn kẹt tới THOIGIANKETKILL giây => kill client cho dangnhap_xq mở lại, đăng nhập rồi lộ trình tự đưa về
#      bãi. Chỉ kill khi đang bật tự động đăng nhập, nhân vật có trong file tài khoản, không có nhân vật nào đang tạm ngưng, và chưa kill
#      nhân vật này quá SOLANKILLTOIDA lần trong 1 giờ (lưu _internal/giamsat.json vì tiến trình bot chết theo client)
#   2. Luồng bot treo: vòng tổng hợp / vòng phụ quá THOIGIANTREOLUONG giây không chạy hết 1 lượt => thoát tiến trình bot, trochoi_xq tự
#      mở lại tiến trình mới cho cửa sổ đó
import json
import os
import subprocess
import sys
import threading
import time

from dangnhap_xq import taicauhinhdangnhap, taikhoanbatchomaynay
from hangso_xq import BANDO_CHIENTRUONG
from thongbao_xq import baosuco
from tienich_xq import phatam, laytamngungdanghieuluc

CHUKYGIAMSAT = 5.
THOIGIANKETLAMMOI = 180.
THOIGIANKETKILL = 600.
SOLANKILLTOIDA = 3
THOIGIANTREOLUONG = 180.

_khoaghi = threading.Lock()


def _duongdangiamsat():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "giamsat.json")


def _tailankill():
    try:
        with open(_duongdangiamsat(), "r", encoding = "utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return {}


def _ghinhankill(idnguoichoi):
    # {"<ID>": [thời điểm kill...]} chỉ giữ trong 1 giờ gần nhất
    with _khoaghi:
        dulieu = _tailankill()
        moc = time.time() - 3600
        dulieu = {k: [t for t in v if t > moc] for k, v in dulieu.items()}
        dulieu.setdefault(str(idnguoichoi), []).append(time.time())
        try:
            with open(_duongdangiamsat(), "w", encoding = "utf-8") as file:
                json.dump(dulieu, file)
        except OSError as err:
            print(f"[GIÁM SÁT] Lỗi ghi file: {err}")


def _solankillgiogannhat(idnguoichoi):
    moc = time.time() - 3600
    return sum(1 for t in _tailankill().get(str(idnguoichoi), []) if t > moc)


class GiamSat:
    def __init__(self, moitruong, tactu):
        self.moitruong = moitruong
        self.tactu = tactu
        # Tên vòng lặp -> thời điểm chạy xong lượt gần nhất (các vòng tự ghi qua danhdau)
        self.nhiploops = {}
        self._datlai()

    def danhdau(self, tenloop):
        self.nhiploops[tenloop] = time.time()

    def _datlai(self):
        self._dauhieutruoc = None
        self._thoidiemtienchien = time.time()
        self._is_dalammoi = False

    def _is_canxetket(self):
        # Chỉ xét kẹt khi bot đang tự đánh theo lộ trình (đứng tại chỗ không có quái thì đứng yên là bình thường)
        tactu = self.tactu
        if not tactu._is_tudongsudungkynang or not tactu._is_tudongdichuyendiemdanhxungquanh:
            return False
        if tactu.get_is_dangtamngung() or tactu.get_is_dangchophucsinh():
            return False
        return self.moitruong.get_idbandohientai() != BANDO_CHIENTRUONG

    def _dauhieu(self):
        moitruong = self.moitruong
        x, y = moitruong.get_toado() or (0, 0)
        hanhtrang = moitruong.get_soluongvatphamhanhtrangtheoten()
        return (round(x), round(y), moitruong.get_idbandohientai(), moitruong.get_iddoituongmuctieudangchon(), moitruong.get_kinhnghiem(),
                moitruong.get_nganluong(), sum(hanhtrang.values()) if hanhtrang else None)

    def step(self):
        self._kiemtratreoluong()

        moitruong = self.moitruong
        if not moitruong.get_is_nhanvattontai() or not self._is_canxetket():
            self._datlai()
            return

        dauhieu = self._dauhieu()
        now = time.time()
        if dauhieu != self._dauhieutruoc:
            self._dauhieutruoc = dauhieu
            self._thoidiemtienchien = now
            self._is_dalammoi = False
            return

        thoigianket = now - self._thoidiemtienchien
        if thoigianket >= THOIGIANKETKILL:
            self._killclient(thoigianket)
        elif thoigianket >= THOIGIANKETLAMMOI and not self._is_dalammoi:
            self._is_dalammoi = True
            moitruong._inlog(f"[GIÁM SÁT] {int(thoigianket)}s không di chuyển, không đổi mục tiêu, không nhận gì: ngắt di chuyển, chọn lại điểm đánh")
            phatam("Nhân vật bị kẹt, chọn lại điểm đánh", is_block = False)
            baosuco(moitruong, "giamsat", f"Kẹt {int(thoigianket) // 60} phút (không đi, không đổi mục tiêu, không nhận gì), đã chọn lại điểm đánh")
            moitruong.action_ngatdichuyen()
            moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            self.tactu._iddiemdanhxungquanhhientai = -1
            self.tactu._diemdanhxungquanhhientai = None

    def _killclient(self, thoigianket):
        moitruong = self.moitruong
        idnguoichoi = moitruong.get_idnguoichoi()
        cauhinh = taicauhinhdangnhap()
        lydo = None
        if not any(str(tk.get("idnguoichoi") or "") == str(idnguoichoi) for tk in cauhinh.get("taikhoans", [])):
            lydo = "nhân vật không có trong file tài khoản"
        elif not any(str(tk.get("idnguoichoi") or "") == str(idnguoichoi) for tk in taikhoanbatchomaynay(cauhinh)):
            lydo = "tài khoản đang tắt tự đăng nhập trên máy này"
        elif laytamngungdanghieuluc():
            lydo = "đang có nhân vật tạm ngưng"
        elif _solankillgiogannhat(idnguoichoi) >= SOLANKILLTOIDA:
            lydo = f"đã mở lại {SOLANKILLTOIDA} lần trong 1 giờ"
        if lydo:
            # Không mở lại được thì nhắc mỗi lần đủ THOIGIANKETLAMMOI nữa, tính lại từ đầu
            moitruong._inlog(f"[GIÁM SÁT] Kẹt {int(thoigianket)}s nhưng không mở lại client: {lydo}")
            phatam("Nhân vật bị kẹt lâu, cần kiểm tra", is_block = False)
            baosuco(moitruong, "giamsat", f"Kẹt {int(thoigianket) // 60} phút, không tự mở lại client được ({lydo}), cần kiểm tra", khoa = "khongmolai", giancach = 1800.)
            self._datlai()
            return
        moitruong._inlog(f"[GIÁM SÁT] Kẹt {int(thoigianket)}s: đóng client để tự đăng nhập lại")
        baosuco(moitruong, "giamsat", f"Kẹt {int(thoigianket) // 60} phút: đóng client để tự đăng nhập lại (lần {_solankillgiogannhat(idnguoichoi) + 1} trong 1 giờ)")
        _ghinhankill(idnguoichoi)
        subprocess.run(["taskkill", "/F", "/PID", str(moitruong.tientrinh.process_id)], capture_output = True)
        self._datlai()

    def _kiemtratreoluong(self):
        now = time.time()
        for tenloop, thoidiem in self.nhiploops.items():
            if now - thoidiem > THOIGIANTREOLUONG:
                self.moitruong._inlog(f"[GIÁM SÁT] Vòng {tenloop} không chạy {int(now - thoidiem)}s: thoát tiến trình bot để mở lại")
                os._exit(1)
