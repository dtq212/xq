# Dùng chung shared_data giữa nhiều máy trong LAN (vd. host + máy ảo VMware), để các tính năng "cùng máy" (theo sau sang bản đồ khác,
# Lăng Ly Sơn / Thành Kiều, Sư Gia, tầm nhìn chung, tập hoả...) chạy được cả khi nhân vật nằm ở máy khác.
# Cấu hình chung mọi máy (đồng bộ qua git): _internal/lan.json {"maychu": tên máy làm chủ, "diachi": IP máy chủ, "cong": cổng, "matkhau": ...}.
# Không có file / sai thì tắt, bot chạy như cũ.
#   - Máy chủ (tenmaynay() == "maychu") mở BaseManager trên cổng đó, giữ dữ liệu từng máy (HubLan)
#   - Mọi máy (cả máy chủ) mỗi CHUKYDONGBOLAN giây gửi phần cần chia sẻ của shared_data mình lên, nhận phần của máy khác về
#     shared_data_lan (Manager dict riêng, khoá "<tên máy>|<hwnd>"). Bot đọc gộp cả hai qua DuLieuNhieuMay; giao diện / Telegram /
#     âm thanh vẫn chỉ thấy cửa sổ máy mình (shared_data gốc)
# Giờ hai máy có thể lệch nhau: mốc thời gian trong dữ liệu máy khác đổi sang giờ máy mình (giữ nguyên "đã bao lâu")
import json
import os
import threading
import time
from multiprocessing.managers import BaseManager

from tienich_xq import _thumucthietlap, tenmaynay

CHUKYDONGBOLAN = 0.25
# Máy không gửi lên quá chừng này giây thì bỏ dữ liệu của nó (bot đọc cũng tự bỏ cửa sổ quá 5 giây)
THOIGIANGIUDULIEULAN = 10.
# Chỉ gửi những khoá bot máy khác đọc (tactu_*, thongke_xq), không gửi phần riêng cho giao diện (lịch sử cất kho, thống kê...)
KHOACHIASELANS = (
    "tennhanvat", "idnguoichoi", "thoidiemcapnhat", "tenbando", "tenmonphai", "idtruongnhom", "thanhviennhoms", "x", "y", "status",
    "_is_tudongtheosau", "_is_tudongsudungkynang", "_lotrinhmaudangdung",
    "_thoidiemphathienanthan", "_thoigiantamngungphathien", "_tenanthanphathien",
    "_is_danglanglyson", "_phobanlanglyson", "_khoathuonglanglyson", "_khoathuonglanglysondalanh", "_langlysonchothanhvien", "_langlysontattodoi", "_langlysongiunhom",
    "_is_dangsugia", "_sugianhiemvu", "_sugiachothanhvien", "_todoimotlan", "_is_dangtapkich",
    "tamnhin", "iddoituongmuctieu", "_biendongtainguyen",
)


def taicauhinhlan():
    # -> dict cấu hình (đủ diachi, cong, matkhau, maychu) hoặc None (tắt)
    duongdan = os.path.join(os.path.dirname(_thumucthietlap()), "lan.json")
    try:
        with open(duongdan, encoding = "utf-8-sig") as file:
            cauhinh = json.load(file)
    except FileNotFoundError:
        return None
    except Exception as err:
        print(f"[LAN] Lỗi đọc lan.json, tắt dùng chung qua LAN: {err}")
        return None
    if not cauhinh.get("batlan", True):
        return None
    if not all(cauhinh.get(k) for k in ("maychu", "diachi", "cong", "matkhau")):
        print("[LAN] lan.json thiếu maychu / diachi / cong / matkhau, tắt dùng chung qua LAN")
        return None
    return cauhinh


class HubLan:
    # Ở máy chủ: dữ liệu mới nhất của từng máy {tên máy: (lúc nhận theo giờ máy chủ, giờ máy gửi lúc gửi, {hwnd: info})}
    def __init__(self):
        self._khoa = threading.Lock()
        self._dulieu = {}

    def traodoi(self, tenmay, thoidiemgui, dulieu):
        # Ghi dữ liệu máy tenmay, trả dữ liệu các máy khác: [(tên máy, số giây từ lúc máy đó gửi, giờ máy đó lúc gửi, {hwnd: info})]
        now = time.time()
        with self._khoa:
            self._dulieu[tenmay] = (now, thoidiemgui, dulieu)
            for ten in [t for t, (lucnhan, _, _) in self._dulieu.items() if now - lucnhan > THOIGIANGIUDULIEULAN]:
                del self._dulieu[ten]
            return [(ten, now - lucnhan, guilan, dl) for ten, (lucnhan, guilan, dl) in self._dulieu.items() if ten != tenmay]


class _LanManager(BaseManager):
    pass


def _locinfo(info):
    return {k: info[k] for k in KHOACHIASELANS if k in info}


def _doigio(info, lech):
    # Đổi các mốc thời gian (giờ máy gửi) sang giờ máy này
    info = dict(info)
    for k in ("thoidiemcapnhat", "_thoidiemphathienanthan"):
        if info.get(k):
            info[k] += lech
    tamnhin = info.get("tamnhin")
    if isinstance(tamnhin, dict) and tamnhin.get("thoidiem"):
        info["tamnhin"] = {**tamnhin, "thoidiem": tamnhin["thoidiem"] + lech}
    if info.get("_biendongtainguyen"):
        info["_biendongtainguyen"] = [(b[0] + lech, *b[1:]) for b in info["_biendongtainguyen"]]
    return info


class DongBoLan:
    # Luồng đồng bộ chạy trong tiến trình chính (trochoi_xq): shared_data máy này <-> HubLan <-> shared_data_lan
    def __init__(self, cauhinh, shared_data, shared_data_lan):
        self.cauhinh = cauhinh
        self.shared_data = shared_data
        self.shared_data_lan = shared_data_lan
        self.tenmay = tenmaynay()
        self.is_maychu = self.tenmay == cauhinh["maychu"]
        self._hub = None
        self._loicuoi = None

    def batdau(self):
        if self.is_maychu:
            hub = HubLan()
            _LanManager.register("layhub", callable = lambda: hub, exposed = ("traodoi",))
            try:
                server = _LanManager(address = ("0.0.0.0", int(self.cauhinh["cong"])), authkey = self.cauhinh["matkhau"].encode()).get_server()
            except Exception as err:
                print(f"[LAN] Không mở được cổng {self.cauhinh['cong']} làm máy chủ: {err}")
                return
            threading.Thread(target = server.serve_forever, daemon = True).start()
            self._hub = hub
            print(f"[LAN] Máy chủ dùng chung dữ liệu: cổng {self.cauhinh['cong']}")
        else:
            _LanManager.register("layhub")
            print(f"[LAN] Nối tới máy chủ {self.cauhinh['maychu']} ({self.cauhinh['diachi']}:{self.cauhinh['cong']})")
        threading.Thread(target = self._loop, daemon = True).start()

    def _layhub(self):
        if self._hub is None:
            manager = _LanManager(address = (self.cauhinh["diachi"], int(self.cauhinh["cong"])), authkey = self.cauhinh["matkhau"].encode())
            manager.connect()
            self._hub = manager.layhub()
            print("[LAN] Đã nối máy chủ")
        return self._hub

    def _baoloi(self, err):
        # In mỗi kiểu lỗi một lần (máy chủ chưa bật thì client thử lại liên tục)
        thongbao = f"{type(err).__name__}: {err}"
        if thongbao != self._loicuoi:
            self._loicuoi = thongbao
            print(f"[LAN] Lỗi đồng bộ: {thongbao}")

    def _loop(self):
        while True:
            try:
                dulieu = {hwnd: _locinfo(info) for hwnd, info in dict(self.shared_data.items()).items() if isinstance(info, dict)}
                maykhacs = self._layhub().traodoi(self.tenmay, time.time(), dulieu)
                now = time.time()
                moi = {}
                for tenmay, tuoi, thoidiemgui, dl in maykhacs:
                    lech = (now - tuoi) - thoidiemgui
                    for hwnd, info in dl.items():
                        moi[f"{tenmay}|{hwnd}"] = {**_doigio(info, lech), "_tenmay": tenmay}
                for khoa in [k for k in self.shared_data_lan.keys() if k not in moi]:
                    self.shared_data_lan.pop(khoa, None)
                if moi:
                    self.shared_data_lan.update(moi)
                if self._loicuoi:
                    self._loicuoi = None
                    print("[LAN] Đồng bộ lại bình thường")
            except Exception as err:
                self._baoloi(err)
                if not self.is_maychu:
                    self._hub = None
                    self.shared_data_lan.clear()
                    time.sleep(2.)
            time.sleep(CHUKYDONGBOLAN)


class DuLieuNhieuMay:
    # shared_data cho bot (tactu): ghi vào phần máy mình, đọc gộp cả cửa sổ máy khác (shared_data_lan)
    def __init__(self, cucbo, maykhac):
        self.cucbo = cucbo
        self.maykhac = maykhac

    def items(self):
        return list(self.cucbo.items()) + list(self.maykhac.items())

    def values(self):
        return list(self.cucbo.values()) + list(self.maykhac.values())

    def keys(self):
        return list(self.cucbo.keys()) + list(self.maykhac.keys())

    def get(self, khoa, macdinh = None):
        giatri = self.cucbo.get(khoa)
        return giatri if giatri is not None else self.maykhac.get(khoa, macdinh)

    def __contains__(self, khoa):
        return khoa in self.cucbo or khoa in self.maykhac

    def __getitem__(self, khoa):
        giatri = self.get(khoa)
        if giatri is None:
            raise KeyError(khoa)
        return giatri

    def __setitem__(self, khoa, giatri):
        self.cucbo[khoa] = giatri

    def __delitem__(self, khoa):
        del self.cucbo[khoa]
