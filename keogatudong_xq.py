# Kéo gà A-Z: tự đăng nhập lần lượt các tài khoản gà, mỗi tài khoản chọn nhân vật còn dưới cấp kết thúc (không có thì tạo nhân vật mới
# ở ô trống, dangnhap_xq._DangNhapBangHam.chonhoactaoga), vào game thì bật vai acc gà, đủ lượt thì bật acc chính kéo cấp như nút "Bắt đầu
# kéo cấp" (tactu_keocap_xq). Acc chính báo xong (mọi acc gà của lượt tới cấp kết thúc, đã trả đồ Lam Kim) thì đóng client acc gà, ghi
# nhân vật đã xong, đăng nhập lượt kế. Tài khoản hết chỗ (6 ô đều là nhân vật đã kéo xong) thì bỏ qua; mọi tài khoản hết thì dừng.
# Chạy trong luồng tự đăng nhập (dangnhap_xq.TuDongDangNhap.loop, sau lượt đăng nhập lại thường) để hai bên không cùng mở client.
# Cấu hình (người dùng nhập trên giao diện, có mật khẩu): _internal/keogatudong.json. Tiến độ (bot ghi liên tục): _internal/keogatudong_tiendo.json
import html
import json
import os
import time

import win32gui
import win32process

import dangnhap_xq
from tienich_xq import thaythefile, _thumucthietlap

# Số acc gà mỗi lượt mặc định (người dùng đang kéo tay 1 acc chính + 4 acc gà)
SOGAMACDINH = 4
SOGATOIDA = 7
CAPKETTHUCMACDINH = 45
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
        self._solanloi = {}
        self._lucbatchinh = 0.
        self._lucchinhhetvai = 0.
        self._is_chinhdabat = False
        tiendo = _docjson("keogatudong_tiendo.json", {})
        if tiendo.get("bat") and tiendo.get("idchinh"):
            # Mở lại bot giữa chừng: làm tiếp lượt cũ (acc gà còn online thì nhận lại theo ID)
            self.is_bat = True
            self.idchinh = int(tiendo["idchinh"])
            self.capketthuc = int(tiendo.get("capketthuc") or CAPKETTHUCMACDINH)
            self.moibang = bool(tiendo.get("moibang", True))
            self.luot = [dict(g, hwnd = 0, lucvang = 0., lucguilenh = 0., lucvaogame = 0.) for g in tiendo.get("luot") or []]
            self._is_chinhdabat = bool(tiendo.get("chinhdabat"))
            self.trangthai = "Làm tiếp lượt kéo gà trước khi tắt bot"
            print(f"[KÉO GÀ A-Z] Làm tiếp: acc chính ID {self.idchinh}, lượt {', '.join(g['ten'] for g in self.luot) or 'trống'}")

    # --- Bật / tắt từ giao diện -----------------------------------------------------------------------------------------------------
    def batdau(self, idchinh, capketthuc, moibang = True):
        self.is_bat = True
        self.idchinh = int(idchinh)
        self.capketthuc = int(capketthuc)
        self.moibang = bool(moibang)
        self.luot = []
        self._solanloi = {}
        self._is_chinhdabat = False
        self._lucbatchinh = 0.
        self.trangthai = "Bắt đầu"
        # Cờ "hết chỗ" của lần trước xét lại (người dùng có thể đã xoá nhân vật / đổi cấp kết thúc)
        tiendo = self._tiendo()
        for tk in (tiendo.get("taikhoans") or {}).values():
            tk.pop("het", None)
        self._luutiendo(tiendo)
        print(f"[KÉO GÀ A-Z] Bắt đầu: acc chính ID {idchinh}, kéo tới cấp {capketthuc}")

    def dung(self, lydo = "Đã dừng (bấm tay)"):
        if not self.is_bat:
            return
        self.is_bat = False
        self.trangthai = lydo
        self._luutiendo()
        print(f"[KÉO GÀ A-Z] {lydo}")

    # --- Tiến độ -----------------------------------------------------------------------------------------------------------------------
    def _tiendo(self):
        return _docjson("keogatudong_tiendo.json", {})

    def _luutiendo(self, tiendo = None):
        tiendo = tiendo or self._tiendo()
        tiendo.update(bat = self.is_bat, idchinh = self.idchinh, capketthuc = self.capketthuc, moibang = self.moibang,
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
        now = time.time()
        cauhinh = taicauhinhkeoga()
        infos = self._infotheoid()
        chinh = infos.get(self.idchinh)
        if not chinh:
            self.trangthai = f"Chờ acc chính (ID {self.idchinh}) online trên máy này"
            return
        hwndchinh, infochinh = chinh
        kcchinh = infochinh.get("_keocap") or {}
        online = dangnhap_xq.laydanhsachnhanvatonlines()

        # Cập nhật acc gà của lượt: cửa sổ, cấp
        for g in self.luot:
            if g["id"] in infos:
                g["hwnd"] = infos[g["id"]][0]
                g["lucvang"] = 0.
                cap = infos[g["id"]][1].get("capdo") or 0
                if cap > int(g.get("cap") or 0):
                    g["cap"] = cap
                    self._ghinhanvat(g["user"], g["id"], g["ten"], cap)
            elif g["id"] in online["id"]:
                g["lucvang"] = 0.
            elif not g["lucvang"]:
                g["lucvang"] = now

        # Lượt xong: mọi acc gà tới cấp kết thúc và acc chính đã hết vai kéo cấp (xong thu hồi đồ Lam Kim)
        if self.luot and self._is_chinhdabat and all(int(g.get("cap") or 0) >= self.capketthuc for g in self.luot):
            if kcchinh and kcchinh.get("giaidoan") != "xong":
                self.trangthai = f"Mọi acc gà đã cấp {self.capketthuc}, chờ acc chính thu hồi đồ / báo xong"
                return
            self._lucchinhhetvai = self._lucchinhhetvai or now
            conga = [g for g in self.luot if g["id"] in infos and infos[g["id"]][1].get("_keocap")]
            if conga and now - self._lucchinhhetvai < THOIGIANCHODONGGA:
                self.trangthai = "Chờ acc gà đọc xong rồi đóng client"
                return
            self._ketthucluot(infos)
            return
        self._lucchinhhetvai = 0.

        # Đăng nhập: acc gà vắng (dis) thì vào lại trước, sau đó thêm tài khoản cho đủ lượt (chưa bật acc chính)
        for g in self.luot:
            if g["lucvang"] and now - g["lucvang"] >= THOIGIANVANGDANGNHAPLAI and not dangnhap_xq.laycuasodangvaogame():
                taikhoan = next((t for t in cauhinh["taikhoans"] if t["user"] == g["user"]), None)
                if not taikhoan:
                    print(f"[KÉO GÀ A-Z] Tài khoản {g['user']} không còn trong danh sách, bỏ {g['ten']} khỏi lượt")
                    self.luot.remove(g)
                    self._luutiendo()
                    return
                self.trangthai = f"Đăng nhập lại {g['ten']} ({g['user']})"
                self._dangnhap(taikhoan, cauhinh, len(self.luot), g)
                return
        soga = max(1, min(SOGATOIDA, int(cauhinh.get("soga") or SOGAMACDINH)))
        if not self._is_chinhdabat and len(self.luot) < soga:
            dangdung = {g["user"] for g in self.luot}
            cho = [t for t in cauhinh["taikhoans"] if t["user"] not in dangdung and not self._is_het(t["user"])
                   and self._solanloi.get(t["user"], 0) < SOLANLOITOIDA]
            if cho:
                if dangnhap_xq.laycuasodangvaogame():
                    self.trangthai = "Chờ acc gà vừa đăng nhập vào game..."
                    return
                taikhoan = cho[0]
                self.trangthai = f"Đăng nhập acc gà {len(self.luot) + 1}/{soga}: {taikhoan['user']}"
                self._dangnhap(taikhoan, cauhinh, len(self.luot))
                return
            if not self.luot:
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
            if chuasan:
                self.trangthai = f"Chờ acc gà vào game / nhận vai: {', '.join(chuasan)}"
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

    def _battangcap(self, g, hwnd, info, now):
        # Acc gà thường đăng nhập tay không bật "Tự tăng cấp"; kéo gà A-Z thì bật cho acc gà của lượt, "tới cấp" ít nhất cấp kết thúc
        # (người dùng dặn 2026-11-08). command_dict mỗi cửa sổ giữ 1 lệnh: chờ lệnh trước bot đã đọc, mỗi lệnh cách GIANCACHLENHTANGCAP giây
        # (bật là lệnh đảo, gửi dồn thì tắt lại)
        if hwnd in self.command_dict or now - g.get("luctangcap", 0.) < GIANCACHLENHTANGCAP:
            return
        if not info.get("_is_tudongtangcap"):
            g["luctangcap"] = now
            self.command_dict[hwnd] = "battat_tudongtangcap"
            print(f"[KÉO GÀ A-Z] Bật Tự tăng cấp cho {g['ten']} (ID {g['id']})")
        elif int(info.get("_captudongtangcaptoida") or 0) < self.capketthuc:
            g["luctangcap"] = now
            self.command_dict[hwnd] = f"set_captudongtangcaptoida:{self.capketthuc}"
            print(f"[KÉO GÀ A-Z] Đặt Tự tăng cấp tới cấp {self.capketthuc} cho {g['ten']} (ID {g['id']})")

    def _batchinh(self, hwndchinh, kcchinh, now):
        if kcchinh and kcchinh.get("vaitro") != "chinh":
            self.trangthai = "Acc chính đang kéo cấp vai khác, dừng nó trước"
            return
        if not kcchinh:
            ids = ",".join(str(g["id"]) for g in self.luot)
            self.command_dict[hwndchinh] = f"keocapchinh:{ids};;{self.capketthuc};;{int(self.moibang)}"
            print(f"[KÉO GÀ A-Z] Bật acc chính kéo cấp lượt: {', '.join(g['ten'] for g in self.luot)}")
        self._lucbatchinh = now
        self._is_chinhdabat = True
        self._luutiendo()
        self.trangthai = "Đã bật acc chính kéo cấp"

    def _dangnhap(self, taikhoan, cauhinh, vitri, ga = None):
        # Đăng nhập 1 tài khoản gà: chọn nhân vật chưa xong / tạo mới. ga: acc gà đang trong lượt (vào lại đúng nhân vật đó)
        user = taikhoan["user"]
        taoga = {"capketthuc": self.capketthuc, "idsdaxong": self._idsdaxong(user), "tiento": cauhinh.get("tiento") or TIENTOMACDINH,
                 "gioitinh": int(cauhinh.get("gioitinh") or 0), "idchon": ga["id"] if ga else 0}
        config = {"user": user, "pass": taikhoan["pass"], "group": int(taikhoan.get("group") or cauhinh.get("group") or 1),
                  "server": int(taikhoan.get("server") or cauhinh.get("server") or 1), "char_index": 1, "vitricuaso": vitri + 2,
                  "tennhanvat": ga["ten"] if ga else "", "idnguoichoi": ga["id"] if ga else None, "taoga": taoga}
        ten = ga["ten"] if ga else user
        hwndcu = ga.get("hwnd") if ga else 0
        if hwndcu and win32gui.IsWindow(hwndcu) and dangnhap_xq._is_cuasomanhinhdangnhap(hwndcu):
            # Bị dis về màn hình đăng nhập: vào lại trong chính cửa sổ đó
            dangnhap_xq.dangnhaptrongcuaso(hwndcu, ten, config)
        else:
            dangnhap_xq.mogamevadangnhap(ten, config, dangnhap_xq.duongdangamemaynay(dangnhap_xq.taicauhinhdangnhap()))
        ketqua = taoga.get("ketqua") or {}
        for idnv, cap in (ketqua.get("caps") or {}).items():
            # Ghi cấp mọi nhân vật thấy ở màn chọn (nhân vật cũ đã đủ cấp cũng tính là xong)
            if cap >= self.capketthuc:
                self._ghinhanvat(user, idnv, "", cap, True)
        if ketqua.get("het"):
            print(f"[KÉO GÀ A-Z] Tài khoản {user} hết chỗ (6 nhân vật đã kéo xong): bỏ qua")
            self._danhdauhet(user)
            self._dongcuaso(ketqua.get("hwnd"))
            if ga:
                self.luot.remove(ga)
                self._luutiendo()
            return
        if not ketqua.get("id"):
            self._solanloi[user] = self._solanloi.get(user, 0) + 1
            print(f"[KÉO GÀ A-Z] Đăng nhập / tạo nhân vật tài khoản {user} không được (lần {self._solanloi[user]}/{SOLANLOITOIDA})")
            if self._solanloi[user] >= SOLANLOITOIDA:
                from thongbao_xq import guitinmay
                guitinmay("dangnhap", f"⚠️ Kéo gà A-Z: tài khoản <b>{html.escape(user)}</b> đăng nhập / tạo nhân vật lỗi {SOLANLOITOIDA} lần, "
                                      f"bỏ qua (sai mật khẩu / đang online / máy chủ từ chối tên?)", khoa = ("keoga", user), giancach = 600.)
                if ga:
                    self.luot.remove(ga)
                    self._luutiendo()
            return
        self._solanloi.pop(user, None)
        if ga:
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
            tens.append(f"{g['ten']} ({g['user']})")
        print(f"[KÉO GÀ A-Z] ✅ Xong lượt (cấp {self.capketthuc}): {', '.join(tens)}. Đóng client, đăng nhập lượt kế")
        guitinmay("dangnhap", f"✅ Kéo gà A-Z xong lượt cấp {self.capketthuc}: {html.escape(', '.join(tens))}", khoa = "keogaluot", giancach = 0.)
        self.luot = []
        self._is_chinhdabat = False
        self._lucchinhhetvai = 0.
        self._luutiendo()
        self.trangthai = "Xong lượt, chờ client đóng rồi đăng nhập lượt kế"

    def _hoanthanh(self, cauhinh):
        from thongbao_xq import guitinmay
        bo = [t["user"] for t in cauhinh["taikhoans"] if self._solanloi.get(t["user"], 0) >= SOLANLOITOIDA]
        lydo = "✅ Mọi tài khoản gà đã hết chỗ" + (f" (bỏ qua vì lỗi: {', '.join(bo)})" if bo else "") if cauhinh["taikhoans"] \
            else "Danh sách tài khoản gà trống"
        guitinmay("dangnhap", f"🏁 Kéo gà A-Z: {html.escape(lydo)}", khoa = "keogaxong", giancach = 0.)
        self.dung(lydo)
