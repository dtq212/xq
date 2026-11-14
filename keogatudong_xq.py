# Kéo gà A-Z: tự đăng nhập lần lượt các tài khoản gà, mỗi tài khoản chọn nhân vật còn dưới cấp kết thúc (không có thì tạo nhân vật mới
# ở ô trống, dangnhap_xq._DangNhapBangHam.chonhoactaoga), vào game thì bật vai acc gà, đủ lượt thì bật acc chính kéo cấp như nút "Bắt đầu
# kéo cấp" (tactu_keocap_xq). Acc chính báo xong (mọi acc gà của lượt tới cấp kết thúc, đã trả đồ Lam Kim) thì đóng client acc gà, ghi
# nhân vật đã xong, đăng nhập lượt kế. Tài khoản hết chỗ (6 ô đều là nhân vật đã kéo xong) thì bỏ qua; mọi tài khoản hết thì dừng.
# Chạy trong luồng tự đăng nhập (dangnhap_xq.TuDongDangNhap.loop, sau lượt đăng nhập lại thường) để hai bên không cùng mở client.
# Cấu hình (người dùng nhập trên giao diện, có mật khẩu): _internal/keogatudong.json. Tiến độ (bot ghi liên tục): _internal/keogatudong_tiendo.json
import html
import json
import os
import threading
import time

import win32gui
import win32process

import dangnhap_xq
from tienich_xq import thaythefile, _thumucthietlap

# Số acc gà mỗi lượt mặc định (người dùng đang kéo tay 1 acc chính + 4 acc gà)
SOGAMACDINH = 4
SOGATOIDA = 7
CAPKETTHUCMACDINH = 50
TIENTOMACDINH = "ga"
# Lượt quét của luồng đăng nhập là 5s; acc gà vắng (dis / game đóng) quá chừng này giây thì đăng nhập lại
THOIGIANVANGDANGNHAPLAI = 20.
# Vào game xong chờ bot cửa sổ đó báo ID tối đa chừng này giây rồi mới gửi lệnh vai acc gà; gửi lệnh xong chừng này giây chưa thấy vai thì gửi lại
THOIGIANCHOBOT = 120.
GIANCACHGUILENH = 30.
# Acc chính dừng kéo cấp giữa lượt (không phải xong): bật lại sau chừng này giây
GIANCACHBATLAICHINH = 60.
# Tài khoản đăng nhập / tạo nhân vật lỗi liên tục chừng này lần thì bỏ qua tới khi bấm bắt đầu lại
SOLANLOITOIDA = 3
# Lượt xong: acc chính hết vai kéo cấp mà acc gà còn vai (chưa đọc "xong") thì chờ thêm tối đa chừng này giây rồi vẫn đóng
THOIGIANCHODONGGA = 60.
GIANCACHLENHTANGCAP = 10.
# Acc gà của lượt (acc chính đã bật) chừng này giây không lên cấp thì nhắn Telegram, nhắc lại mỗi chừng ấy (người dùng dặn 2026-11-08: 2 lượt
# kẹt cấp 0 / 10 tổng ~4,5 giờ lúc ngủ vì tự tăng cấp không bật mà không ai biết)
THOIGIANKHONGLENCAP = 30 * 60.
# Vừa đóng / kill client của tài khoản thì máy chủ vẫn coi tài khoản đang online thêm một lúc: đăng nhập lại ngay bị báo tài khoản
# đang online / đầy (người dùng báo 2026-11-08, xong lượt vào lại gacon5 ngay thì hỏng, lượt đó thiếu acc). Chờ chừng này giây
THOIGIANCHOTHOATTAIKHOAN = 45.
# Acc gà trong lượt vào lại hỏng: lần thứ n chờ 30*n giây rồi thử lại, tối đa chừng này
THOIGIANTHULAIGATOIDA = 180.
# Nhận đồ đệ (ô "Nhận đồ đệ" của kéo cấp, người dùng dặn 2026-11-14): mỗi lượt chọn 1 acc gà cấp không quá chừng này (trùng
# tactu_keocap_xq.CAPTOIDANHANDODE: quá cấp này acc chính coi như đã bái sư, chỉ đi xuất sư) làm đồ đệ, acc chính bái sư ở Mạnh Tử
# trước khi lập nhóm, đồ đệ cấp 50 / cấp kết thúc thì xuất sư trước khi thu hồi đồ, lượt mới nhận đồ đệ mới
CAPTOIDANHANDODEAZ = 30

CAUHINHMAU = {"soga": SOGAMACDINH, "tiento": TIENTOMACDINH, "gioitinh": 0, "group": 1, "server": 1, "taikhoans": []}


def _duongdan(ten):
    return os.path.join(os.path.dirname(_thumucthietlap()), ten)


def _docjson(ten, macdinh):
    try:
        with open(_duongdan(ten), "r", encoding = "utf-8") as f:
            dulieu = json.load(f)
        return dulieu if isinstance(dulieu, dict) else dict(macdinh)
    except Exception:
        return json.loads(json.dumps(macdinh))


def _ghijson(ten, dulieu):
    duongdan = _duongdan(ten)
    try:
        os.makedirs(os.path.dirname(duongdan), exist_ok = True)
        with open(duongdan + ".tmp", "w", encoding = "utf-8") as f:
            json.dump(dulieu, f, ensure_ascii = False, indent = 1)
        thaythefile(duongdan + ".tmp", duongdan)
    except Exception as e:
        print(f"[KÉO GÀ A-Z] Lỗi ghi {ten}: {e}")


def taicauhinhkeoga():
    cauhinh = _docjson("keogatudong.json", CAUHINHMAU)
    for khoa, giatri in CAUHINHMAU.items():
        cauhinh.setdefault(khoa, giatri)
    cauhinh["taikhoans"] = [t for t in cauhinh["taikhoans"] if isinstance(t, dict) and t.get("user") and t.get("pass")]
    return cauhinh


def luucauhinhkeoga(cauhinh):
    _ghijson("keogatudong.json", cauhinh)


def phantichdanhsachtaikhoan(chu):
    # Mỗi dòng 1 tài khoản: "tài khoản mật khẩu [cụm máy chủ]" (cách nhau dấu cách / tab / "|" / ","); dòng trống, dòng bắt đầu "#" bỏ qua.
    # -> ([{user, pass, group?, server?}], [dòng lỗi])
    taikhoans, lois = [], []
    for so, dong in enumerate((chu or "").splitlines(), 1):
        dong = dong.strip()
        if not dong or dong.startswith("#"):
            continue
        phans = dong.replace("|", " ").replace(",", " ").replace("\t", " ").split()
        if len(phans) < 2:
            lois.append(f"dòng {so}: thiếu mật khẩu")
            continue
        taikhoan = {"user": phans[0], "pass": phans[1]}
        try:
            if len(phans) >= 3:
                taikhoan["group"] = int(phans[2])
            if len(phans) >= 4:
                taikhoan["server"] = int(phans[3])
        except ValueError:
            lois.append(f"dòng {so}: cụm / máy chủ phải là số")
            continue
        taikhoans.append(taikhoan)
    return taikhoans, lois


def chudanhsachtaikhoan(taikhoans):
    return "\n".join(" ".join([t["user"], t["pass"]] + ([str(t["group"]), str(t.get("server", 1))] if "group" in t else []))
                     for t in taikhoans)


def _timcuasodistheoid(idnguoichoi):
    # Cửa sổ game đang ở màn hình đăng nhập (bị dis) mà bộ nhớ vẫn giữ ID nhân vật này (dis không xoá ID, đo 2026-11-08)
    from moitruong_xq import MoiTruong
    ketqua = []

    def callback(hwnd, _):
        if ketqua or not dangnhap_xq._is_cuasomanhinhdangnhap(hwnd):
            return
        try:
            if int(MoiTruong(hwnd).get_idnguoichoi() or 0) == int(idnguoichoi):
                ketqua.append(hwnd)
        except Exception:
            pass

    win32gui.EnumWindows(callback, None)
    return ketqua[0] if ketqua else 0


class KeoGaTuDong:
    def __init__(self, shared_data, command_dict):
        self.shared_data = shared_data
        self.command_dict = command_dict
        self.is_bat = False
        self.trangthai = "Đang tắt"
        # Lượt đang kéo: [{"user", "id", "ten", "hwnd", "lucvang", "lucguilenh", "lucvaogame"}]
        self.luot = []
        self.idchinh = 0
        self.capketthuc = CAPKETTHUCMACDINH
        self.moibang = True
        # Nhận đồ đệ: iddode là acc gà đồ đệ của lượt (0 = chưa chọn / lượt không có), dabaisu / daxuatsu đọc từ acc chính
        self.nhandode = False
        self.iddode = 0
        self.dabaisu = False
        self.daxuatsu = False
        self._solanloi = {}
        self._lucbatchinh = 0.
        self._lucchinhhetvai = 0.
        self._is_chinhdabat = False
        # Tài khoản ("user") -> lúc vừa đóng client của nó (chờ THOIGIANCHOTHOATTAIKHOAN giây rồi mới đăng nhập lại)
        self._lucdong = {}
        # Đăng nhập song song (người dùng dặn 2026-11-14; trước đây lần lượt, mỗi acc gà ~25s và chờ acc trước load xong): "user" ->
        # {"luong", "taikhoan", "ga", "taoga", "xong", "bo"}. Luồng chỉ gọi dangnhap_xq (mở client vẫn lần lượt nhờ _khoamoclient,
        # nhập tài khoản / chọn / tạo nhân vật / vào game chạy song song như tự đăng nhập thường); kết quả xử lý ở mot_luot (luồng tự
        # đăng nhập) nên self.luot / tiến độ chỉ một luồng sửa. "bo": bấm dừng / bắt đầu lại / xong lượt lúc luồng còn chạy thì bỏ kết quả
        # (nhân vật đã vào game thì lần sau _nhanlaigaonline nhận lại) nhưng vẫn giữ chỗ để không đăng nhập đè cùng tài khoản
        self._luongdangnhap = {}
        tiendo = _docjson("keogatudong_tiendo.json", {})
        if tiendo.get("bat") and tiendo.get("idchinh"):
            # Mở lại bot giữa chừng: làm tiếp lượt cũ (acc gà còn online thì nhận lại theo ID)
            self.is_bat = True
            self.idchinh = int(tiendo["idchinh"])
            self.capketthuc = int(tiendo.get("capketthuc") or CAPKETTHUCMACDINH)
            self.moibang = bool(tiendo.get("moibang", True))
            self.nhandode = bool(tiendo.get("nhandode"))
            self.iddode = int(tiendo.get("iddode") or 0)
            self.dabaisu = bool(tiendo.get("dabaisu"))
            self.daxuatsu = bool(tiendo.get("daxuatsu"))
            self.luot = [dict(g, hwnd = 0, lucvang = 0., lucguilenh = 0., lucvaogame = 0.) for g in tiendo.get("luot") or []]
            self._is_chinhdabat = bool(tiendo.get("chinhdabat"))
            self.trangthai = "Làm tiếp lượt kéo gà trước khi tắt bot"
            print(f"[KÉO GÀ A-Z] Làm tiếp: acc chính ID {self.idchinh}, lượt {', '.join(g['ten'] for g in self.luot) or 'trống'}")

    # --- Bật / tắt từ giao diện -----------------------------------------------------------------------------------------------------
    def batdau(self, idchinh, capketthuc, moibang = True, nhandode = False):
        self.is_bat = True
        self.idchinh = int(idchinh)
        self.capketthuc = int(capketthuc)
        self.moibang = bool(moibang)
        self.nhandode = bool(nhandode)
        self._datlaidode()
        self.luot = []
        self._solanloi = {}
        self._is_chinhdabat = False
        self._lucbatchinh = 0.
        self._boluongdangnhap()
        self.trangthai = "Bắt đầu"
        # Cờ "hết chỗ" của lần trước xét lại (người dùng có thể đã xoá nhân vật / đổi cấp kết thúc)
        tiendo = self._tiendo()
        for tk in (tiendo.get("taikhoans") or {}).values():
            tk.pop("het", None)
        self._luutiendo(tiendo)
        print(f"[KÉO GÀ A-Z] Bắt đầu: acc chính ID {idchinh}, kéo tới cấp {capketthuc}" + (", nhận đồ đệ mỗi lượt" if nhandode else ""))

    def _datlaidode(self):
        self.iddode = 0
        self.dabaisu = False
        self.daxuatsu = False

    def dung(self, lydo = "Đã dừng (bấm tay)"):
        if not self.is_bat:
            return
        self.is_bat = False
        self.trangthai = lydo
        self._boluongdangnhap()
        self._luutiendo()
        print(f"[KÉO GÀ A-Z] {lydo}")

    # --- Tiến độ -----------------------------------------------------------------------------------------------------------------------
    def _tiendo(self):
        return _docjson("keogatudong_tiendo.json", {})

    def _luutiendo(self, tiendo = None):
        tiendo = tiendo or self._tiendo()
        tiendo.update(bat = self.is_bat, idchinh = self.idchinh, capketthuc = self.capketthuc, moibang = self.moibang,
                      nhandode = self.nhandode, iddode = self.iddode, dabaisu = self.dabaisu, daxuatsu = self.daxuatsu,
                      chinhdabat = self._is_chinhdabat, luot = [{"user": g["user"], "id": g["id"], "ten": g["ten"]} for g in self.luot])
        tiendo.setdefault("taikhoans", {})
        _ghijson("keogatudong_tiendo.json", tiendo)

    def _ghinhanvat(self, user, idnv, ten, cap, is_xong = None):
        tiendo = self._tiendo()
        tk = tiendo.setdefault("taikhoans", {}).setdefault(user, {})
        nv = tk.setdefault("nhanvats", {}).setdefault(str(idnv), {})
        nv.update(ten = ten, cap = max(int(cap or 0), int(nv.get("cap") or 0)))
        if is_xong is not None:
            nv["xong"] = bool(is_xong)
        self._luutiendo(tiendo)

    def _idsdaxong(self, user):
        nvs = ((self._tiendo().get("taikhoans") or {}).get(user) or {}).get("nhanvats") or {}
        return [int(i) for i, nv in nvs.items() if int(nv.get("cap") or 0) >= self.capketthuc]

    def _is_het(self, user):
        return bool(((self._tiendo().get("taikhoans") or {}).get(user) or {}).get("het"))

    def _danhdauhet(self, user):
        tiendo = self._tiendo()
        tiendo.setdefault("taikhoans", {}).setdefault(user, {})["het"] = True
        self._luutiendo(tiendo)

    # --- Đọc cửa sổ -------------------------------------------------------------------------------------------------------------------
    def _infotheoid(self):
        # {ID người chơi: (hwnd, info)} cửa sổ cùng máy còn cập nhật
        ketqua = {}
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return ketqua
        for hwnd, info in danhsach:
            if isinstance(info, dict) and info.get("idnguoichoi") and time.time() - info.get("thoidiemcapnhat", 0.) <= 10.:
                ketqua[int(info["idnguoichoi"])] = (int(hwnd), info)
        return ketqua

    # --- Vòng chính (gọi mỗi lượt quét của luồng đăng nhập) ---------------------------------------------------------------------------
    def mot_luot(self):
        if not self.is_bat:
            return
        try:
            self._mot_luot()
        except Exception as e:
            self.trangthai = f"Lỗi: {e}"
            print(f"[KÉO GÀ A-Z] Lỗi: {e}")

    def _mot_luot(self):
        self._xulyluongxong()
        now = time.time()
        cauhinh = taicauhinhkeoga()
        infos = self._infotheoid()
        chinh = infos.get(self.idchinh)
        if not chinh:
            self.trangthai = f"Chờ acc chính (ID {self.idchinh}) online trên máy này"
            return
        hwndchinh, infochinh = chinh
        kcchinh = infochinh.get("_keocap") or {}
        if self.iddode and kcchinh.get("vaitro") == "chinh" and kcchinh.get("iddode") == self.iddode \
                and (bool(kcchinh.get("dabaisu")), bool(kcchinh.get("daxuatsu"))) != (self.dabaisu, self.daxuatsu):
            # Nhớ bái sư / xuất sư acc chính đã làm: acc chính dừng giữa lượt mà bật lại thì không bái sư lần nữa
            self.dabaisu, self.daxuatsu = bool(kcchinh.get("dabaisu")), bool(kcchinh.get("daxuatsu"))
            print(f"[KÉO GÀ A-Z] Đồ đệ ID {self.iddode}: {'đã xuất sư' if self.daxuatsu else 'đã bái sư' if self.dabaisu else 'chưa bái sư'}")
            self._luutiendo()
        online = dangnhap_xq.laydanhsachnhanvatonlines()

        # Cập nhật acc gà của lượt: cửa sổ, cấp
        for g in self.luot:
            g.setdefault("luclencap", now)
            if g["id"] in infos:
                g["hwnd"] = infos[g["id"]][0]
                g["lucvang"] = 0.
                cap = infos[g["id"]][1].get("capdo") or 0
                if cap > int(g.get("cap") or 0):
                    g["cap"] = cap
                    g["luclencap"] = now
                    self._ghinhanvat(g["user"], g["id"], g["ten"], cap)
            elif g["id"] in online["id"]:
                g["lucvang"] = 0.
            elif not g["lucvang"]:
                g["lucvang"] = now

        self._canhbaokhonglencap(infos, now)

        is_dutcap = bool(self.luot) and self._is_chinhdabat and all(int(g.get("cap") or 0) >= self.capketthuc for g in self.luot)
        # Acc gà vắng (dis) thì vào lại trước mọi việc, kể cả khi mọi acc gà đã đủ cấp mà acc chính chưa báo xong: acc chính còn chờ chúng
        # trả đồ Lam Kim (thu hồi) / đang Phong Yêu Kính dở. Trước đây nhánh "chờ acc chính thu hồi đồ" return trước nên acc gà dis lúc đó
        # không bao giờ được đăng nhập lại (572 dis 19:40 2026-11-08, cả lượt đứng chờ). Acc chính đã báo xong thì thôi, sắp đóng client
        if not (is_dutcap and (not kcchinh or kcchinh.get("giaidoan") == "xong")) and self._dangnhaplaigavang(cauhinh, now):
            return

        # Lượt xong: mọi acc gà tới cấp kết thúc và acc chính đã hết vai kéo cấp (xong thu hồi đồ Lam Kim)
        if is_dutcap:
            if kcchinh and kcchinh.get("giaidoan") != "xong":
                vangs = [g["ten"] for g in self.luot if g["lucvang"]]
                self.trangthai = f"Mọi acc gà đã cấp {self.capketthuc}, chờ acc chính thu hồi đồ / báo xong" +                                  (f" (chờ vào lại: {', '.join(vangs)})" if vangs else "")
                return
            self._lucchinhhetvai = self._lucchinhhetvai or now
            conga = [g for g in self.luot if g["id"] in infos and infos[g["id"]][1].get("_keocap")]
            if conga and now - self._lucchinhhetvai < THOIGIANCHODONGGA:
                self.trangthai = "Chờ acc gà đọc xong rồi đóng client"
                return
            self._ketthucluot(infos)
            return
        self._lucchinhhetvai = 0.

        soga = max(1, min(SOGATOIDA, int(cauhinh.get("soga") or SOGAMACDINH)))
        # Acc gà mới đang đăng nhập (luồng chưa xong, không tính luồng vào lại acc đã trong lượt)
        somoi = sum(1 for v in self._luongdangnhap.values() if not v["ga"] and not v["bo"])
        if not self._is_chinhdabat and len(self.luot) + somoi < soga:
            dangdung = {g["user"] for g in self.luot} | set(self._luongdangnhap)
            cho = [t for t in cauhinh["taikhoans"] if t["user"] not in dangdung and not self._is_het(t["user"])
                   and self._solanloi.get(t["user"], 0) < SOLANLOITOIDA]
            # Nhân vật của tài khoản đang online sẵn (bấm Bắt đầu lại / mở lại bot giữa lượt): nhận vào lượt luôn, không đăng nhập đè
            # (trước đây đăng nhập lần lượt từ tài khoản đầu dù đang online: client mới đá nhân vật đang chơi, hoặc báo tài khoản
            # đang online, 2026-11-08)
            if self._nhanlaigaonline(cho, infos, online, soga - somoi, now):
                return
            chothoat = [t for t in cho if now - self._lucdong.get(t["user"], 0.) < THOIGIANCHOTHOATTAIKHOAN]
            if chothoat and len(chothoat) == len(cho) and not somoi:
                conlai = int(THOIGIANCHOTHOATTAIKHOAN - (now - self._lucdong[chothoat[0]["user"]])) + 1
                self.trangthai = f"Chờ {chothoat[0]['user']} thoát hẳn khỏi máy chủ ({conlai}s) rồi đăng nhập"
                return
            cho = [t for t in cho if t not in chothoat]
            if cho:
                # Mở luồng cho mọi chỗ còn thiếu cùng lúc (không chờ acc trước vào hẳn game như trước)
                for taikhoan in cho[:soga - len(self.luot) - somoi]:
                    self._batluongdangnhap(taikhoan, cauhinh, len(self.luot) + somoi)
                    somoi += 1
                self.trangthai = f"Đang đăng nhập {somoi} acc gà ({len(self.luot) + somoi}/{soga}): " + ", ".join(self._luongdangnhap)
                return
            if not self.luot and not self._luongdangnhap:
                self._hoanthanh(cauhinh)
                return

        # Gửi vai acc gà cho cửa sổ vừa vào game
        chuasan = []
        for g in self.luot:
            info = infos.get(g["id"])
            if not info:
                chuasan.append(g["ten"])
                continue
            hwnd, i = info
            kc = i.get("_keocap") or {}
            if not (kc.get("vaitro") == "ga" and kc.get("idchinh") == self.idchinh) and int(g.get("cap") or 0) < self.capketthuc:
                if now - g.get("lucguilenh", 0.) >= GIANCACHGUILENH:
                    g["lucguilenh"] = now
                    self.command_dict[hwnd] = f"keocapga:{self.idchinh}"
                    print(f"[KÉO GÀ A-Z] Bật vai acc gà cho {g['ten']} (ID {g['id']})")
                chuasan.append(g["ten"])
                continue
            self._battangcap(g, hwnd, i, now)

        # Đủ lượt (hết tài khoản chờ thì lượt ít hơn): bật acc chính
        if not self._is_chinhdabat:
            dangvao = [u for u, v in self._luongdangnhap.items() if not v["bo"]]
            if chuasan or dangvao:
                self.trangthai = "Chờ acc gà vào game / nhận vai: " + ", ".join(chuasan + [f"{u} (đang đăng nhập)" for u in dangvao])
                return
            self._batchinh(hwndchinh, kcchinh, now)
            return
        if not kcchinh or kcchinh.get("vaitro") != "chinh":
            # Acc chính dừng kéo cấp giữa lượt (dis / mở lại bot chưa tự bật): bật lại
            if now - self._lucbatchinh >= GIANCACHBATLAICHINH:
                self._batchinh(hwndchinh, kcchinh, now)
            else:
                self.trangthai = "Acc chính chưa kéo cấp, chờ bật lại"
            return
        self.trangthai = f"Lượt {len(self.luot)} acc gà: " + ", ".join(f"{g['ten']} cấp {g.get('cap') or 0}" for g in self.luot) + \
                         (f" (chờ vào lại: {', '.join(chuasan)})" if chuasan else "")

    def _nhanlaigaonline(self, cho, infos, online, soga, now):
        # Tài khoản trong danh sách chờ mà có nhân vật (đã ghi trong tiến độ) đang online trên máy này: nhân vật chưa tới cấp kết thúc
        # thì nhận vào lượt (không đăng nhập), đã xong thì đóng client của nó trước (đăng nhập đè sẽ báo tài khoản đang online).
        # -> True: lượt này đã làm gì đó (vòng sau xét tiếp)
        nvtheouser = self._tiendo().get("taikhoans") or {}
        hwndtheoid = {idnv: hwnd for hwnd, idnv in online["cuaso"].items()}
        hwndtheoid.update({idnv: hwnd for idnv, (hwnd, _) in infos.items()})
        dalam = False
        for t in cho:
            if len(self.luot) >= soga:
                break
            user = t["user"]
            nvs = (nvtheouser.get(user) or {}).get("nhanvats") or {}
            dangons = [int(i) for i in nvs if int(i) in hwndtheoid and int(i) != self.idchinh]
            if not dangons:
                continue

            def capcua(idnv):
                return max(int((infos.get(idnv) or (0, {}))[1].get("capdo") or 0), int(nvs[str(idnv)].get("cap") or 0))

            chuaxongs = [i for i in dangons if capcua(i) < self.capketthuc]
            if chuaxongs:
                idnv = max(chuaxongs, key = capcua)
                info = (infos.get(idnv) or (0, {}))[1]
                g = {"user": user, "id": idnv, "ten": info.get("tennhanvat") or nvs[str(idnv)].get("ten") or "", "cap": capcua(idnv),
                     "hwnd": hwndtheoid[idnv], "lucvang": 0., "lucguilenh": 0., "lucvaogame": now}
                self.luot.append(g)
                self._luutiendo()
                print(f"[KÉO GÀ A-Z] {g['ten']} (ID {idnv}, cấp {g['cap']}) của {user} đang online: nhận vào lượt, không đăng nhập lại")
                dalam = True
            elif now - self._lucdong.get(user, 0.) >= THOIGIANCHOTHOATTAIKHOAN:
                print(f"[KÉO GÀ A-Z] {user}: nhân vật đã kéo xong (ID {', '.join(map(str, dangons))}) còn online, đóng client rồi mới đăng nhập")
                for i in dangons:
                    self._dongcuaso(hwndtheoid[i])
                self._lucdong[user] = now
                dalam = True
        return dalam

    def _dangnhaplaigavang(self, cauhinh, now):
        # Acc gà trong lượt vắng quá THOIGIANVANGDANGNHAPLAI giây: đăng nhập lại (cửa sổ bị dis thì vào lại trong chính nó), mỗi acc một
        # luồng, nhiều acc vắng thì vào lại song song. -> True: đã làm
        dalam = False
        for g in list(self.luot):
            if not g["lucvang"] or now - g["lucvang"] < THOIGIANVANGDANGNHAPLAI or now < g.get("lucthulai", 0.) \
                    or g["user"] in self._luongdangnhap:
                continue
            taikhoan = next((t for t in cauhinh["taikhoans"] if t["user"] == g["user"]), None)
            if not taikhoan:
                print(f"[KÉO GÀ A-Z] Tài khoản {g['user']} không còn trong danh sách, bỏ {g['ten']} khỏi lượt")
                self.luot.remove(g)
                self._luutiendo()
                dalam = True
                continue
            self.trangthai = f"Đăng nhập lại {g['ten']} ({g['user']})"
            print(f"[KÉO GÀ A-Z] {g['ten']} (ID {g['id']}) vắng {int(now - g['lucvang'])}s: đăng nhập lại {g['user']}")
            self._batluongdangnhap(taikhoan, cauhinh, self.luot.index(g), g)
            dalam = True
        return dalam

    def _canhbaokhonglencap(self, infos, now):
        # Acc gà dưới cấp kết thúc mà THOIGIANKHONGLENCAP giây không lên cấp (chỉ tính khi acc chính đã bật kéo cấp lượt này): nhắn Telegram
        if not self._is_chinhdabat:
            for g in self.luot:
                g["luclencap"] = now
            return
        kets = []
        for g in self.luot:
            if int(g.get("cap") or 0) >= self.capketthuc or now - g["luclencap"] < THOIGIANKHONGLENCAP:
                continue
            if now - g.get("luccanhbao", 0.) < THOIGIANKHONGLENCAP:
                continue
            g["luccanhbao"] = now
            info = (infos.get(g["id"]) or (0, {}))[1]
            if not info:
                tinhtrang = "không online"
            else:
                tinhtrang = (f"tự tăng cấp {'bật tới cấp ' + str(info.get('_captudongtangcaptoida')) if info.get('_is_tudongtangcap') else 'TẮT'}, "
                             f"{info.get('_trangthaikeocap') or 'không kéo cấp'}")
            kets.append(f"{g['ten']} (ID {g['id']}) cấp {g.get('cap') or 0}, {int((now - g['luclencap']) // 60)} phút: {tinhtrang}")
        if kets:
            from thongbao_xq import guitinmay
            print("[KÉO GÀ A-Z] ⚠️ Acc gà lâu không lên cấp: " + "; ".join(kets))
            guitinmay("dangnhap", "⚠️ Kéo gà A-Z: acc gà lâu không lên cấp\n" + "\n".join("• " + html.escape(k) for k in kets),
                      khoa = "keogakhonglencap", giancach = 0.)

    def _battangcap(self, g, hwnd, info, now):
        # Acc gà thường đăng nhập tay không bật "Tự tăng cấp"; kéo gà A-Z thì bật cho acc gà của lượt, "tới cấp" ít nhất cấp kết thúc
        # (người dùng dặn 2026-11-08). command_dict mỗi cửa sổ giữ 1 lệnh: chờ lệnh trước bot đã đọc, mỗi lệnh cách GIANCACHLENHTANGCAP giây
        # (bật là lệnh đảo, gửi dồn thì tắt lại)
        # Bot đọc lệnh xong ghi None chứ không xoá khoá (cuaso_xq): xét giá trị, không xét "in" (từng không bao giờ gửi được, 2026-11-08)
        if self.command_dict.get(hwnd) or now - g.get("luctangcap", 0.) < GIANCACHLENHTANGCAP:
            return
        if not info.get("_is_tudongtangcap"):
            g["luctangcap"] = now
            self.command_dict[hwnd] = "battat_tudongtangcap"
            print(f"[KÉO GÀ A-Z] Bật Tự tăng cấp cho {g['ten']} (ID {g['id']})")
        elif int(info.get("_captudongtangcaptoida") or 0) < self.capketthuc:
            g["luctangcap"] = now
            self.command_dict[hwnd] = f"set_captudongtangcaptoida:{self.capketthuc}"
            print(f"[KÉO GÀ A-Z] Đặt Tự tăng cấp tới cấp {self.capketthuc} cho {g['ten']} (ID {g['id']})")
        elif info.get("_is_tudongsudungkynang"):
            # Tắt "Tự động sử dụng kỹ năng" (người dùng dặn 2026-11-08): bật thì trong Phong Yêu Kính acc gà dò đánh chạy khắp bản đồ,
            # tắt thì đứng cạnh Thỏ Yêu hưởng kinh nghiệm (tactu_keocap_xq._buoctrongphongyeukeocap); ở bãi chỉ theo sau acc chính
            g["luctangcap"] = now
            self.command_dict[hwnd] = "battat_tudongsudungkynang"
            print(f"[KÉO GÀ A-Z] Tắt Tự động sử dụng kỹ năng cho {g['ten']} (ID {g['id']})")

    def _batchinh(self, hwndchinh, kcchinh, now):
        if kcchinh and kcchinh.get("vaitro") != "chinh":
            self.trangthai = "Acc chính đang kéo cấp vai khác, dừng nó trước"
            return
        if not kcchinh:
            ids = ",".join(str(g["id"]) for g in self.luot)
            self._chondode()
            self.command_dict[hwndchinh] = f"keocapchinh:{ids};{self.iddode or ''};{self.capketthuc};;{int(self.moibang)};" \
                                           f"{int(self.dabaisu)};{int(self.daxuatsu)}"
            dode = next((g for g in self.luot if g["id"] == self.iddode), None)
            print(f"[KÉO GÀ A-Z] Bật acc chính kéo cấp lượt: {', '.join(g['ten'] for g in self.luot)}"
                  + (f", đồ đệ {dode['ten']} (ID {dode['id']}{', đã bái sư' if self.dabaisu else ''})" if dode else ""))
        self._lucbatchinh = now
        self._is_chinhdabat = True
        self._luutiendo()
        self.trangthai = "Đã bật acc chính kéo cấp"

    def _chondode(self):
        # Chọn acc gà đồ đệ cho lượt (một lần mỗi lượt, giữ qua lúc bật lại acc chính): acc gà cấp thấp nhất, không quá CAPTOIDANHANDODEAZ
        # (acc gà nhận lại giữa chừng đã cao cấp thì acc chính sẽ coi như đã bái sư mà thực ra chưa: không nhận)
        if not self.nhandode or (self.iddode and any(g["id"] == self.iddode for g in self.luot)):
            return
        self._datlaidode()
        chon = [g for g in self.luot if int(g.get("cap") or 0) <= CAPTOIDANHANDODEAZ]
        if not chon:
            print(f"[KÉO GÀ A-Z] Không acc gà nào của lượt từ cấp {CAPTOIDANHANDODEAZ} trở xuống: lượt này không nhận đồ đệ")
            return
        self.iddode = min(chon, key = lambda g: (int(g.get("cap") or 0), g["ten"]))["id"]

    def _batluongdangnhap(self, taikhoan, cauhinh, vitri, ga = None):
        # Mở luồng đăng nhập 1 tài khoản gà: chọn nhân vật chưa xong / tạo mới. ga: acc gà đang trong lượt (vào lại đúng nhân vật đó).
        # Dữ liệu cần (idsdaxong, cấu hình) đọc ở đây (luồng tự đăng nhập), luồng mới chỉ gọi dangnhap_xq
        user = taikhoan["user"]
        taoga = {"capketthuc": self.capketthuc, "idsdaxong": self._idsdaxong(user), "tiento": cauhinh.get("tiento") or TIENTOMACDINH,
                 "gioitinh": int(cauhinh.get("gioitinh") or 0), "idchon": ga["id"] if ga else 0}
        config = {"user": user, "pass": taikhoan["pass"], "group": int(taikhoan.get("group") or cauhinh.get("group") or 1),
                  "server": int(taikhoan.get("server") or cauhinh.get("server") or 1), "char_index": 1, "vitricuaso": vitri + 2,
                  "tennhanvat": ga["ten"] if ga else "", "idnguoichoi": ga["id"] if ga else None, "taoga": taoga}
        viec = {"taikhoan": taikhoan, "ga": ga, "taoga": taoga, "xong": False, "bo": False}
        viec["luong"] = threading.Thread(target = self._chayluongdangnhap, args = (viec, config), daemon = True)
        self._luongdangnhap[user] = viec
        print(f"[KÉO GÀ A-Z] Bắt đầu đăng nhập {user}" + (f" (vào lại {ga['ten']})" if ga else ""))
        viec["luong"].start()

    @staticmethod
    def _chayluongdangnhap(viec, config):
        ga = viec["ga"]
        ten = ga["ten"] if ga else config["user"]
        try:
            hwndcu = ga.get("hwnd") if ga else 0
            if ga and not (hwndcu and win32gui.IsWindow(hwndcu) and dangnhap_xq._is_cuasomanhinhdangnhap(hwndcu)):
                # Mở lại bot giữa lượt thì hwnd = 0: tìm cửa sổ bị dis theo ID còn trong bộ nhớ, không thì mở thêm client trong khi
                # cửa sổ dis vẫn chiếm chỗ (giới hạn số client)
                hwndcu = _timcuasodistheoid(ga["id"]) or hwndcu
            if hwndcu and win32gui.IsWindow(hwndcu) and dangnhap_xq._is_cuasomanhinhdangnhap(hwndcu):
                # Bị dis về màn hình đăng nhập: vào lại trong chính cửa sổ đó
                dangnhap_xq.dangnhaptrongcuaso(hwndcu, ten, config)
            else:
                dangnhap_xq.mogamevadangnhap(ten, config, dangnhap_xq.duongdangamemaynay(dangnhap_xq.taicauhinhdangnhap()))
        except Exception as e:
            print(f"[KÉO GÀ A-Z] Lỗi đăng nhập {config['user']}: {e}")
        finally:
            viec["xong"] = True

    def _xulyluongxong(self):
        # Luồng đăng nhập đã xong: xử lý kết quả (ghi lượt / tiến độ) ở luồng tự đăng nhập
        for user, viec in list(self._luongdangnhap.items()):
            if not viec["xong"] and viec["luong"].is_alive():
                continue
            self._luongdangnhap.pop(user, None)
            if viec["bo"]:
                print(f"[KÉO GÀ A-Z] Bỏ kết quả đăng nhập {user} (đã dừng / sang lượt khác lúc đang đăng nhập)")
                continue
            if viec["ga"] and viec["ga"] not in self.luot:
                continue
            self._xulyketquadangnhap(viec["taikhoan"], viec["taoga"].get("ketqua") or {}, viec["ga"])

    def _boluongdangnhap(self):
        for viec in self._luongdangnhap.values():
            viec["bo"] = True

    def _xulyketquadangnhap(self, taikhoan, ketqua, ga = None):
        user = taikhoan["user"]
        for idnv, cap in (ketqua.get("caps") or {}).items():
            # Ghi cấp mọi nhân vật thấy ở màn chọn (nhân vật cũ đã đủ cấp cũng tính là xong)
            if cap >= self.capketthuc:
                self._ghinhanvat(user, idnv, "", cap, True)
        if ketqua.get("het"):
            print(f"[KÉO GÀ A-Z] Tài khoản {user} hết chỗ (6 nhân vật đã kéo xong): bỏ qua")
            self._danhdauhet(user)
            self._dongcuaso(ketqua.get("hwnd"))
            self._lucdong[user] = time.time()
            if ga:
                self.luot.remove(ga)
                self._luutiendo()
            return
        if not ketqua.get("id"):
            self._solanloi[user] = self._solanloi.get(user, 0) + 1
            print(f"[KÉO GÀ A-Z] Đăng nhập / tạo nhân vật tài khoản {user} không được (lần {self._solanloi[user]}/{SOLANLOITOIDA})")
            if self._solanloi[user] >= SOLANLOITOIDA:
                from thongbao_xq import guitinmay
                guitinmay("dangnhap", f"⚠️ Kéo gà A-Z: tài khoản <b>{html.escape(user)}</b> đăng nhập / tạo nhân vật lỗi {SOLANLOITOIDA} lần"
                                      + (f", vẫn thử vào lại {html.escape(ga['ten'])} mỗi {int(THOIGIANTHULAIGATOIDA)}s" if ga
                                         else ", bỏ qua (sai mật khẩu / đang online / máy chủ từ chối tên?)"),
                          khoa = ("keoga", user), giancach = 600.)
            if ga:
                # Acc gà trong lượt bị dis mà vào lại hỏng (thường do máy chủ chưa nhả tài khoản: báo đang online / đầy): không bỏ khỏi lượt
                # (acc chính vẫn đang chờ nó), thử lại giãn dần. Trước đây hỏng 3 lần là bỏ hẳn, lượt kéo thiếu acc (2026-11-08)
                ga["lucthulai"] = time.time() + min(THOIGIANTHULAIGATOIDA, 30. * self._solanloi[user])
                self._solanloi[user] = min(self._solanloi[user], SOLANLOITOIDA - 1)
            return
        self._solanloi.pop(user, None)
        if ga:
            if int(ketqua["id"]) != ga["id"]:
                # Không thấy đúng nhân vật cũ ở màn chọn (đã đổi ô / bị xoá?): báo, không lặng lẽ thay nhân vật khác vào lượt
                from thongbao_xq import guitinmay
                print(f"[KÉO GÀ A-Z] ⚠️ Vào lại {ga['ten']} (ID {ga['id']}) mà ra nhân vật ID {ketqua['id']}")
                guitinmay("dangnhap", f"⚠️ Kéo gà A-Z: vào lại <b>{html.escape(ga['ten'])}</b> (ID {ga['id']}) của {html.escape(user)} mà ra "
                                      f"nhân vật ID {ketqua['id']}, kiểm tra tay giúp", khoa = ("keogasainv", user), giancach = 600.)
            ga.update(lucvang = 0., hwnd = ketqua.get("hwnd") or 0)
            return
        g = {"user": user, "id": int(ketqua["id"]), "ten": ketqua.get("ten") or "", "cap": int(ketqua.get("cap") or 0),
             "hwnd": ketqua.get("hwnd") or 0, "lucvang": 0., "lucguilenh": 0., "lucvaogame": time.time()}
        self.luot.append(g)
        self._ghinhanvat(user, g["id"], g["ten"], g["cap"], False)
        print(f"[KÉO GÀ A-Z] Vào lượt: {g['ten']} (ID {g['id']}, cấp {g['cap']}{', mới tạo' if ketqua.get('tao') else ''}) của {user}")

    def _dongcuaso(self, hwnd):
        if not hwnd or not win32gui.IsWindow(hwnd):
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            dangnhap_xq._killtientrinh(pid)
        except Exception as e:
            print(f"[KÉO GÀ A-Z] Lỗi đóng client (HWND {hwnd}): {e}")

    def _ketthucluot(self, infos):
        from thongbao_xq import guitinmay
        tens = []
        for g in self.luot:
            self._ghinhanvat(g["user"], g["id"], g["ten"], g.get("cap") or 0, True)
            hwnd = infos[g["id"]][0] if g["id"] in infos else g.get("hwnd")
            self._dongcuaso(hwnd)
            self._lucdong[g["user"]] = time.time()
            tens.append(f"{g['ten']} ({g['user']})")
        print(f"[KÉO GÀ A-Z] ✅ Xong lượt (cấp {self.capketthuc}): {', '.join(tens)}. Đóng client, đăng nhập lượt kế")
        guitinmay("dangnhap", f"✅ Kéo gà A-Z xong lượt cấp {self.capketthuc}: {html.escape(', '.join(tens))}", khoa = "keogaluot", giancach = 0.)
        if self.iddode and not self.daxuatsu:
            print(f"[KÉO GÀ A-Z] ⚠️ Đồ đệ ID {self.iddode} chưa thấy acc chính báo xuất sư (lượt sau acc chính bái sư có thể hỏng)")
        self.luot = []
        self._datlaidode()
        self._is_chinhdabat = False
        self._lucchinhhetvai = 0.
        self._boluongdangnhap()
        self._luutiendo()
        self.trangthai = "Xong lượt, chờ client đóng rồi đăng nhập lượt kế"

    def _hoanthanh(self, cauhinh):
        from thongbao_xq import guitinmay
        bo = [t["user"] for t in cauhinh["taikhoans"] if self._solanloi.get(t["user"], 0) >= SOLANLOITOIDA]
        lydo = "✅ Mọi tài khoản gà đã hết chỗ" + (f" (bỏ qua vì lỗi: {', '.join(bo)})" if bo else "") if cauhinh["taikhoans"] \
            else "Danh sách tài khoản gà trống"
        guitinmay("dangnhap", f"🏁 Kéo gà A-Z: {html.escape(lydo)}", khoa = "keogaxong", giancach = 0.)
        self.dung(lydo)
