# Tự động đăng nhập lại nhân vật vắng mặt (trước đây là các kịch bản tudongdangnhap*.py chạy riêng).
# Tài khoản + đường dẫn game của từng máy nằm trong _internal/taikhoan_<tên máy tính>.json, luồng chạy trong trochoi_xq.py

import csv
import json
import os
import shutil
import subprocess
import threading
import time

import pywintypes
import win32api
import win32con
import win32gui
import win32process

from moitruong_xq import MoiTruong
from tienich_xq import duongdantaikhoan, duongdantaikhoancu, laytamngungdanghieuluc

LAUNCHER_TITLE = "client 2.01.07"
GAME_TITLE_LOGIN_SCREEN = "Chien Quoc 2D --ooo2026ooo-- v.2.01.07"
GAME_TITLE_PREFIX = "Chien Quoc 2D"

DANH_SACH_CUA_SO_LOI = ["warning", "play"]

# Cửa sổ bị dis về màn hình đăng nhập: thử đăng nhập lại ngay trong nó tối đa bấy nhiêu lần (vào lại tại chỗ, không mất chỗ phó bản),
# vẫn không vào được thì thôi giữ chỗ, xử lý như client không đăng nhập (đóng, mở game mới)
SOLANDANGNHAPLAICUASODIS = 2

# Game chỉ cho chạy bấy nhiêu client cùng lúc, mở thêm thì client mới báo lỗi và treo cả quy trình đăng nhập
SOCLIENTTOIDA = 4

# Rớt khỏi game chừng này lần trong THOIGIANDEMBIDA giây thì coi như đang giành tài khoản với máy khác: tạm hoãn tự đăng nhập
# tài khoản đó THOIGIANTAMHOAN giây (xem TuDongDangNhap._theodoiroigame)
SOLANBIDALIENTUC = 3
THOIGIANDEMBIDA = 1800
THOIGIANTAMHOAN = 1800
# Nhân vật vắng chừng này giây mà tự đăng nhập vẫn chưa đưa vào lại được thì báo Telegram (kẹt quy trình đăng nhập...)
THOIGIANBAOVANG = 600

TOADO_LAUNCHER = {
    "BTN_VAO_GAME": (530, 495)
}

TOADO_GAME = {
    "BTN_XACNHAN_SERVER": (760, 465),
}

TOADO_CUMMAYCHU = {
    1: (190, 185),
    2: (190, 221),
    3: (190, 234),
    4: (190, 259),
}

TOADO_MAYCHU = {
    1: (377, 182),
    2: (372, 206),
}

TOADO_CHONNHANVAT = {
    2: (369, 146),
    3: (560, 146),
    4: (188, 352),
    5: (369, 352),
    6: (560, 352),
}

# Mẫu file cấu hình khi máy chưa có. Mỗi tài khoản nhận diện online theo "idnguoichoi" (cố định); chưa điền ID thì tạm so theo "tennhanvat"
CAUHINHMAU = {
    "is_tudongdangnhap": False,
    "duongdangame": r"E:\Games\ChienQuoc2D_Aegis\xq.exe",
    "taikhoans": [
        {
            "tennhanvat": "Tên nhân vật",
            "idnguoichoi": None,
            "user": "taikhoan",
            "pass": "matkhau",
            "group": 1,
            "server": 1,
            "char_index": 1,
            "vitricuaso": 1,
        },
    ],
}


def taicauhinhdangnhap():
    # Đọc lỗi (sai cú pháp JSON...) thì trả về cấu hình rỗng có khoá "loi" để báo lên giao diện, và không được lưu đè lên file
    duongdan = duongdantaikhoan()
    if not os.path.exists(duongdan):
        # Lần đầu chạy bản tách file theo tên máy: dùng tiếp file chung tên cũ (taikhoan.json) nếu có, không thì tạo file mẫu
        if os.path.exists(duongdantaikhoancu()):
            shutil.copy2(duongdantaikhoancu(), duongdan)
            print(f"[ĐĂNG NHẬP] Đã chép {os.path.basename(duongdantaikhoancu())} sang {os.path.basename(duongdan)} (file riêng của máy này)")
        else:
            luucauhinhdangnhap(CAUHINHMAU)
    try:
        # utf-8-sig: Notepad (nhất là Windows 7) lưu "UTF-8" kèm BOM ở đầu file
        with open(duongdan, encoding = "utf-8-sig") as file:
            cauhinh = json.load(file)
        if not isinstance(cauhinh, dict):
            raise ValueError("nội dung phải là một đối tượng JSON { ... }")
    except Exception as err:
        print(f"[ĐĂNG NHẬP] Lỗi đọc {duongdan}: {err}")
        return dict(CAUHINHMAU, is_tudongdangnhap = False, taikhoans = [], loi = f"File tài khoản bị lỗi: {err}")
    cauhinh.setdefault("is_tudongdangnhap", False)
    cauhinh.setdefault("duongdangame", CAUHINHMAU["duongdangame"])
    cauhinh.setdefault("taikhoans", [])
    return cauhinh


def luucauhinhdangnhap(cauhinh):
    duongdan = duongdantaikhoan()
    if cauhinh.get("loi"):
        # Cấu hình rỗng do đọc lỗi: lưu vào sẽ xoá mất tài khoản người dùng vừa nhập
        print(f"[ĐĂNG NHẬP] Không lưu vì file đang lỗi, sửa lại {duongdan} trước")
        return False
    try:
        os.makedirs(os.path.dirname(duongdan), exist_ok = True)
        filetam = duongdan + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(cauhinh, file, ensure_ascii = False, indent = 4)
        os.replace(filetam, duongdan)
    except Exception as err:
        print(f"[ĐĂNG NHẬP] Lỗi lưu {duongdan}: {err}")


# Tắt tự động đăng nhập thì tuyệt đối không kill tiến trình / đóng cửa sổ nào, kể cả cửa sổ bị đơ (tắt giữa lúc đang đăng nhập dở
# thì các bước dọn dẹp còn lại cũng bỏ qua). TuDongDangNhap cập nhật cờ này theo nút bật/tắt
is_chophepdong = False


def _killtientrinh(pid):
    if not is_chophepdong:
        print(f"   -> Đang tắt tự động đăng nhập, không kill tiến trình (PID: {pid})")
        return False
    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output = True)
    return True


def mogame(duongdangame, thumuc):
    # Tiến trình bot nằm trong Job "đóng là kill hết" (trochoi_xq._gantientrinhvaojob): game mở từ đây phải tách khỏi Job, không thì
    # tắt bot là game cũng tắt theo. Đang chạy trong Job khác không cho tách (vd Job của IDE) thì mở bình thường
    try:
        return subprocess.Popen(duongdangame, cwd = thumuc, creationflags = subprocess.CREATE_BREAKAWAY_FROM_JOB)
    except OSError:
        return subprocess.Popen(duongdangame, cwd = thumuc)


def _dongcuaso(hwnd):
    if not is_chophepdong:
        print(f"   -> Đang tắt tự động đăng nhập, không đóng cửa sổ (HWND: {hwnd})")
        return False
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    return True


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


def _safe_post_message(hwnd, msg, wparam, lparam):
    try:
        win32gui.PostMessage(hwnd, msg, wparam, lparam)
    except pywintypes.error as e:
        if e.winerror == 1400:
            return
        raise e


PHIMDIEUKHIENs = (win32con.VK_SHIFT, win32con.VK_CONTROL, win32con.VK_MENU, win32con.VK_LWIN, win32con.VK_RWIN)


def chonhaphimdieukhien(thoigiantoida = 5.):
    # Chỉ đọc trạng thái phím thật (không gửi gì ra bàn phím): nếu người dùng đang giữ Ctrl/Shift/Alt/Win
    # thì chờ nhả ra rồi mới gửi click/phím, tránh game hiểu thành tổ hợp phím (vd Shift+Tab, Alt+Enter)
    hethan = time.time() + thoigiantoida
    while time.time() < hethan:
        if not any(win32api.GetAsyncKeyState(phim) & 0x8000 for phim in PHIMDIEUKHIENs):
            return True
        time.sleep(0.05)
    return False


def click(hwnd, x, y, delay = 0.1):
    chonhaphimdieukhien()
    lparam = make_lparam(x, y)
    _safe_post_message(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
    time.sleep(delay)


def press_key(hwnd, key_code, delay = 0.1):
    chonhaphimdieukhien()
    _safe_post_message(hwnd, win32con.WM_KEYDOWN, key_code, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYUP, key_code, 0)
    time.sleep(delay)


def type_text(hwnd, text, delay = 0.05):
    for char in text:
        _safe_post_message(hwnd, win32con.WM_CHAR, ord(char), 0)
        time.sleep(delay)


def kiemtravadongcuasotreo(hwnd):
    try:
        win32gui.PostMessage(hwnd, win32con.WM_NCMOUSEMOVE, 0, 0)
        time.sleep(0.2)

        win32gui.SendMessageTimeout(
            hwnd,
            win32con.WM_GETTEXTLENGTH,
            0,
            0,
            win32con.SMTO_NORMAL,
            1000
        )
        return False

    except Exception:
        print(f"⚠️ Phát hiện cửa sổ bị đơ ngầm (HWND: {hwnd}). Đang thực hiện dọn dẹp...")
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if _killtientrinh(pid):
                print(f"✅ Đã đóng thành công cửa sổ lỗi (PID: {pid}).")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi cố gắng dọn dẹp cửa sổ: {e}")
            return False


def chuanhoatennhanvat(tennhanvat):
    # Gộp mọi loại khoảng trắng (kể cả Alt+255 / U+00A0 trong tên nhân vật) thành dấu cách thường trước khi so
    return " ".join((tennhanvat or "").split()).lower()


def laydanhsachnhanvatonlines():
    # "cuaso": {hwnd: ID người chơi} của các cửa sổ đang có nhân vật (để nhận ra cửa sổ đó khi bị dis về màn hình đăng nhập),
    # "tentheocuaso": {hwnd: tên đã chuẩn hoá} (nhận ra cửa sổ của tài khoản chưa điền ID / tự điền ID)
    online_chars = {"ten": set(), "id": set(), "cuaso": {}, "tentheocuaso": {}}

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if GAME_TITLE_PREFIX in title:
                is_hung = kiemtravadongcuasotreo(hwnd)
                if is_hung:
                    return

                try:
                    mt = MoiTruong(hwnd)
                    if mt.get_is_nhanvattontai():
                        idnguoichoi = mt.get_idnguoichoi()
                        if idnguoichoi:
                            online_chars["id"].add(int(idnguoichoi))
                            online_chars["cuaso"][hwnd] = int(idnguoichoi)
                        tennhanvat = chuanhoatennhanvat(mt.get_tendoituong())
                        if tennhanvat:
                            online_chars["ten"].add(tennhanvat)
                            online_chars["tentheocuaso"][hwnd] = tennhanvat
                except:
                    pass

    win32gui.EnumWindows(callback, None)
    return online_chars


def timlauncherdangmo():
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == LAUNCHER_TITLE:
                hwnd_found = hwnd

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def timcuanhbaoloi():
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            title_thuong = title.lower()
            for loi_title in DANH_SACH_CUA_SO_LOI:
                # Bản 2.01.06 tiêu đề có hậu tố, vd "warning -- Ping: N/A"
                if title_thuong == loi_title or title_thuong.startswith(loi_title + " "):
                    hwnd_found = hwnd
                    break

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def _is_cuasodadangnhap(hwnd):
    # Bản 2.01.06 tiêu đề màn hình đăng nhập và trong game có thể trùng tiền tố, kiểm tra bộ nhớ để không đóng nhầm cửa sổ đang chơi
    try:
        mt = MoiTruong(hwnd)
        return bool(mt.get_is_nhanvattontai() and mt.get_idnguoichoi())
    except:
        return False


def _is_cuasomanhinhdangnhap(hwnd):
    # Cửa sổ game đang ở màn hình đăng nhập (mới mở, hoặc bị dis về), chưa có nhân vật. Chỉ so tiền tố tiêu đề: trong game tiêu đề
    # là "Chien Quoc 2D (ID) -oo2026oo- ...", bị dis về màn chọn máy chủ có thể vẫn giữ tiêu đề đó chứ không đổi về tiêu đề đăng nhập
    if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd) or GAME_TITLE_PREFIX not in win32gui.GetWindowText(hwnd):
        return False
    r = win32gui.GetWindowRect(hwnd)
    w, h = r[2] - r[0], r[3] - r[1]
    return 790 < w < 830 and 590 < h < 660 and not _is_cuasodadangnhap(hwnd)


def timcuasogamedangbiket(boquas = ()):
    # boquas: cửa sổ bị dis đang giữ chỗ cho nhân vật khác (đăng nhập lại ngay trong đó thì vào lại tại chỗ, đóng là mất chỗ phó bản)
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if hwnd in boquas:
            return
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if GAME_TITLE_LOGIN_SCREEN in title:
                r = win32gui.GetWindowRect(hwnd)
                w, h = r[2] - r[0], r[3] - r[1]
                if 790 < w < 830 and 590 < h < 660 and not _is_cuasodadangnhap(hwnd):
                    hwnd_found = hwnd

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def mogamevadangnhap(char_name, config, duongdangame, cuasogiuchos = ()):
    # cuasogiuchos: cửa sổ bị dis của nhân vật khác, không đóng / không nhận nhầm là cửa sổ mới mở
    print(f"\n[ĐĂNG NHẬP] >>> BẮT ĐẦU QUY TRÌNH CHO: {char_name}")
    try:
        hwnd_game_stuck = timcuasogamedangbiket(cuasogiuchos)
        if hwnd_game_stuck:
            print(f"   -> Phát hiện cửa sổ chờ (HWND: {hwnd_game_stuck}). Đang đóng...")
            try:
                if _dongcuaso(hwnd_game_stuck):
                    time.sleep(5)
            except Exception as e:
                print(f"   -> Lỗi khi đóng cửa sổ cũ: {e}")

        if not giaiphongchoclient(cuasogiuchos):
            print(f"   -> Đã đủ {SOCLIENTTOIDA} client mà không có client nào đóng được (đều đang chơi / giữ chỗ). Không mở thêm.")
            return False

        hwnd_launcher = timlauncherdangmo()
        if hwnd_launcher:
            print(f"   -> Tìm thấy Launcher (HWND: {hwnd_launcher}).")
            if win32gui.IsIconic(hwnd_launcher):
                win32gui.ShowWindow(hwnd_launcher, win32con.SW_SHOWNOACTIVATE)
        else:
            if not os.path.exists(duongdangame):
                print(f"❌ Không tìm thấy file game: {duongdangame} (sửa 'duongdangame' trong {duongdantaikhoan()})")
                return
            print("   -> Mở file exe mới...")
            game_dir = os.path.dirname(duongdangame)

            dondepclientkhongdangnhap(cuasogiuchos = cuasogiuchos)

            max_retries = 3
            success_open = False

            for attempt in range(max_retries):
                print(f"      [Lần thử {attempt + 1}/{max_retries}] Đang chạy lệnh mở game...")
                mogame(duongdangame, game_dir)

                # Chờ launcher tối đa 10s, kiểm tra mỗi 0.5s
                for i in range(20):
                    hwnd_launcher = timlauncherdangmo()
                    if hwnd_launcher:
                        success_open = True
                        break

                    hwnd_error = timcuanhbaoloi()
                    if hwnd_error:
                        title_error = win32gui.GetWindowText(hwnd_error)
                        print(f"\n      ⚠️ CẢNH BÁO: Phát hiện cửa sổ '{title_error}' (HWND: {hwnd_error}).")
                        print("      -> Đang gửi lệnh ĐÓNG cửa sổ lỗi...")
                        try:
                            _dongcuaso(hwnd_error)
                        except Exception as e:
                            print(f"      -> Lỗi khi đóng: {e}")

                        dondeptientrinhaovuabithoatgame()
                        dondepclientkhongdangnhap(tuoitoithieu = 0., cuasogiuchos = cuasogiuchos)

                        break

                    time.sleep(0.5)

                if success_open:
                    break
                else:
                    print("      -> Hết thời gian chờ. Thử lại quy trình...")
                    time.sleep(5)

        if not hwnd_launcher:
            print("❌ Lỗi: Không bật được Launcher sau nhiều lần thử!")
            return
        time.sleep(2)
        lx, ly = TOADO_LAUNCHER["BTN_VAO_GAME"]
        click(hwnd_launcher, lx, ly)
        time.sleep(1)
        click(hwnd_launcher, lx, ly)

        hwnd_game = 0
        for i in range(60):
            time.sleep(1)
            hwnd_game = timcuasogamedangbiket(cuasogiuchos)
            if hwnd_game: break
            # Click có thể bị launcher nuốt mất: bấm lại "Vào game" mỗi 15s
            if (i + 1) % 15 == 0 and win32gui.IsWindow(hwnd_launcher):
                print(f"   -> Chưa thấy cửa sổ game sau {i + 1}s, bấm lại Vào game...")
                click(hwnd_launcher, lx, ly)

        if not hwnd_game:
            print("❌ Lỗi: Cửa sổ Game không hiện lên! Launcher có thể bị đơ -> Đóng launcher để lần sau mở lại từ đầu.")
            donglauncher(hwnd_launcher)
            return

        print(f"[5] Game đã lên (HWND: {hwnd_game}). Đợi load Login (2s)...")
        dangnhaptrongcuaso(hwnd_game, char_name, config)

    except Exception as e:
        print(f"❌ Exception: {e}")


def dangnhaptrongcuaso(hwnd_game, char_name, config):
    # Từ màn hình chọn cụm / máy chủ (cửa sổ mới mở, hoặc cửa sổ bị dis quay về) tới khi vào game
    try:
        vitri = config.get("vitricuaso", 1)
        dichuyencuasotheovitri(hwnd_game, vitri)

        time.sleep(2)

        group_name = config.get("group")
        server_index = config.get("server", 1)

        if group_name in TOADO_CUMMAYCHU:
            print(f"   -> Chọn cụm {group_name}")
            gx, gy = TOADO_CUMMAYCHU[group_name]
            click(hwnd_game, gx, gy)
            time.sleep(0.2)

        try:
            idx = int(server_index)
            if idx in TOADO_MAYCHU:
                print(f"   -> Chọn server thứ {idx}")
                sx, sy = TOADO_MAYCHU[idx]
                click(hwnd_game, sx, sy)
                time.sleep(0.2)
                bx, by = TOADO_GAME["BTN_XACNHAN_SERVER"]
                click(hwnd_game, bx, by)
                # Chuyển sang màn nhập tài khoản gần như tức thì, chỉ chờ ngắn để ô nhập kịp hiện
                time.sleep(0.5)
            else:
                print(f"⚠️ Không có tọa độ cho server index {idx}")
        except ValueError:
            print(f"❌ Lỗi: Server index '{server_index}' không hợp lệ!")
            return

        print("   -> Nhập Tài khoản & Mật khẩu...")
        press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)
        for _ in range(30):
            press_key(hwnd_game, win32con.VK_BACK, delay = 0.01)
        time.sleep(0.5)

        type_text(hwnd_game, config["user"])
        time.sleep(0.5)
        press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)
        type_text(hwnd_game, config["pass"])
        time.sleep(0.5)
        press_key(hwnd_game, win32con.VK_RETURN)

        print("   -> Chờ load nhân vật (2.5s)...")
        time.sleep(2.5)

        char_idx = config.get("char_index", 1)

        if char_idx >= 2:
            cx, cy = TOADO_CHONNHANVAT.get(char_idx)
            click(hwnd_game, cx, cy)
            time.sleep(1)
        else:
            print("   -> Chọn nhân vật số 1 (Mặc định)")

        press_key(hwnd_game, win32con.VK_RETURN)
        time.sleep(1)
        press_key(hwnd_game, win32con.VK_RETURN)

        print(f"✅ Hoàn tất cho {char_name}. Nghỉ 15s...")

        time.sleep(15)

    except Exception as e:
        print(f"❌ Exception: {e}")


def dondeptientrinhaovuabithoatgame():
    valid_pids = set()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and "Chien Quoc 2" in title:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                valid_pids.add(pid)

    win32gui.EnumWindows(callback, None)

    ghost_pids = _laypidxq() - valid_pids

    if ghost_pids:
        print(f"[CLEANUP] Đang kiểm tra các tiến trình xq.exe bị treo ngầm...")

        pid_dakills = []
        for pid in ghost_pids:
            print(f"   ⚠️ Phát hiện xq.exe ảo (PID: {pid}). Đang tiến hành kill...")
            try:
                if _killtientrinh(pid):
                    pid_dakills.append(pid)
                    print(f"   ✅ Đã đóng thành công xq.exe ảo (PID: {pid}).")
            except Exception as e:
                print(f"   ❌ Lỗi khi kill PID {pid}: {e}")

        if pid_dakills:
            chotientrinhthoat(pid_dakills)


def donglauncher(hwnd_launcher):
    # Launcher bị đơ không vào được game: đóng nhẹ trước, không được thì kill tiến trình rồi chờ thoát hẳn
    if not hwnd_launcher or not win32gui.IsWindow(hwnd_launcher):
        return
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd_launcher)
    except pywintypes.error:
        return
    try:
        if not _dongcuaso(hwnd_launcher):
            return
    except pywintypes.error:
        pass
    for _ in range(10):
        time.sleep(0.5)
        if not win32gui.IsWindow(hwnd_launcher):
            break
    else:
        print(f"   ⚠️ Launcher không tự đóng (PID: {pid}). Đang kill...")
        if not _killtientrinh(pid):
            return
    chotientrinhthoat([pid])
    print(f"   ✅ Đã đóng launcher (PID: {pid}).")


def _laypidxq():
    xq_pids = set()
    try:
        output = subprocess.check_output(
            ['tasklist', '/FI', 'IMAGENAME eq xq.exe', '/FO', 'CSV', '/NH']
        ).decode('utf-8', errors = 'ignore')
        for row in csv.reader(output.splitlines()):
            if len(row) > 1 and 'xq.exe' in row[0].lower():
                xq_pids.add(int(row[1]))
    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách tiến trình: {e}")
    return xq_pids


def _laytuoitientrinh(pid):
    try:
        handle = win32api.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        try:
            return time.time() - win32process.GetProcessTimes(handle)["CreationTime"].timestamp()
        finally:
            win32api.CloseHandle(handle)
    except Exception:
        return 0.


def dondepclientkhongdangnhap(tuoitoithieu = 120., cuasogiuchos = ()):
    # Client vừa bị dis vẫn còn cửa sổ "Chien Quoc 2D..." nên không bị coi là tiến trình ảo, nhưng vẫn chiếm suất
    # => game báo "You can not run more client program!". Kill các client không có nhân vật đang đăng nhập.
    # Bỏ qua client mới mở (< tuoitoithieu giây) vì có thể đang đăng nhập dở.
    pid_dangnhaps = set()
    pid_cuasogames = set()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and GAME_TITLE_PREFIX in win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pid_cuasogames.add(pid)
            # Cửa sổ bị dis đang giữ chỗ: coi như đang đăng nhập, không kill
            if hwnd in cuasogiuchos or _is_cuasodadangnhap(hwnd):
                pid_dangnhaps.add(pid)

    win32gui.EnumWindows(callback, None)

    pid_cankills = [pid for pid in pid_cuasogames - pid_dangnhaps if _laytuoitientrinh(pid) >= tuoitoithieu]
    pid_dakills = []
    for pid in pid_cankills:
        print(f"   ⚠️ Client không còn nhân vật đăng nhập (bị dis?) (PID: {pid}). Đang kill...")
        if _killtientrinh(pid):
            pid_dakills.append(pid)
    if pid_dakills:
        chotientrinhthoat(pid_dakills)


def giaiphongchoclient(cuasogiuchos = ()):
    # Trước khi mở client mới: đã đủ SOCLIENTTOIDA cửa sổ game thì kill client không có nhân vật (cửa sổ chờ, cửa sổ bị dis đã hết
    # lượt thử...), trừ cửa sổ bị dis đang giữ chỗ. Không cần tuổi tối thiểu như dondepclientkhongdangnhap vì đằng nào cũng phải mở mới.
    # Trả về False khi không giải phóng được chỗ (mở thêm sẽ thành client thứ SOCLIENTTOIDA + 1)
    pidtheocuasos = {}

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and GAME_TITLE_PREFIX in win32gui.GetWindowText(hwnd):
            pidtheocuasos[hwnd] = win32process.GetWindowThreadProcessId(hwnd)[1]

    win32gui.EnumWindows(callback, None)

    pids = set(pidtheocuasos.values())
    socanbot = len(pids) - SOCLIENTTOIDA + 1
    if socanbot <= 0:
        return True
    pid_dangnhaps = {pid for hwnd, pid in pidtheocuasos.items() if hwnd in cuasogiuchos or _is_cuasodadangnhap(hwnd)}
    pid_cankills = sorted(pids - pid_dangnhaps)[:socanbot]
    pid_dakills = []
    for pid in pid_cankills:
        print(f"   ⚠️ Đã đủ {SOCLIENTTOIDA} client, kill client không có nhân vật (PID: {pid}) để lấy chỗ...")
        if _killtientrinh(pid):
            pid_dakills.append(pid)
    if pid_dakills:
        chotientrinhthoat(pid_dakills)
    return len(pid_dakills) >= socanbot


def chotientrinhthoat(pids, thoigiantoida = 15.):
    # taskkill trả về ngay nhưng tiến trình cần một lúc mới thoát hẳn; mở xq.exe mới quá sớm vẫn bị tính quá số client
    pids = set(pids)
    hethan = time.time() + thoigiantoida
    while pids and time.time() < hethan:
        pids &= _laypidxq()
        if pids:
            time.sleep(0.5)
    time.sleep(1.)


def dichuyencuasotheovitri(hwnd, vitricuaso):
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    window_width = 810
    window_height = 630
    taskbar_height = 40

    index_goc = (vitricuaso - 1) % 4

    toa_do_4_goc = [
        (0, 0),                                                                       # 1: Trái Trên
        (screen_width - window_width, 0),                                             # 2: Phải Trên
        (0, screen_height - window_height - taskbar_height),                          # 3: Trái Dưới
        (screen_width - window_width, screen_height - window_height - taskbar_height)  # 4: Phải Dưới
    ]

    toado_x, toado_y = toa_do_4_goc[index_goc]

    try:
        win32gui.SetWindowPos(
            hwnd,
            0,
            toado_x,
            toado_y,
            0,
            0,
            win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
        )
        print(f"   -> [GIAO DIỆN] Đã ghim cửa sổ vào vị trí số {vitricuaso}.")
    except Exception as e:
        print(f"   ❌ Lỗi khi di chuyển cửa sổ: {e}")


def _is_cuasocuataikhoan(taikhoan, idnguoichoi, tennhanvat):
    # Cửa sổ (đã biết ID / tên nhân vật lúc còn online) có phải của tài khoản này: so ID, chưa điền ID thì so tên
    if taikhoan.get("idnguoichoi"):
        return idnguoichoi is not None and int(taikhoan["idnguoichoi"]) == idnguoichoi
    return bool(tennhanvat) and chuanhoatennhanvat(taikhoan.get("tennhanvat")) == tennhanvat


def _is_taikhoanonline(taikhoan, online):
    # Ưu tiên ID (cố định); chưa điền ID thì tạm so theo tên (tên có thể đổi). None = cấu hình thiếu cả hai
    idnguoichoi = taikhoan.get("idnguoichoi")
    tennhanvat = taikhoan.get("tennhanvat")
    if idnguoichoi:
        return int(idnguoichoi) in online["id"]
    if tennhanvat:
        return chuanhoatennhanvat(tennhanvat) in online["ten"]
    return None


class TuDongDangNhap:
    # Luồng nền trong tiến trình giao diện: bật/tắt lưu vào file cấu hình, giao diện đọc "trangthai" để hiển thị
    def __init__(self):
        global is_chophepdong
        self.is_bat = bool(taicauhinhdangnhap().get("is_tudongdangnhap"))
        is_chophepdong = self.is_bat
        self.trangthai = "Đang tắt" if not self.is_bat else "Đang khởi động..."
        # [(tên, ID, "online"/"vắng"/"đang đăng nhập")] lần quét gần nhất
        self.danhsach = []
        # hwnd -> ID nhân vật lần cuối thấy trong cửa sổ đó: cửa sổ bị dis về màn hình đăng nhập vẫn giữ chỗ (phó bản), đăng nhập lại
        # ngay trong nó thì vào lại tại chỗ, đóng cửa sổ là mất chỗ. hwnd -> số lần đã thử đăng nhập lại trong cửa sổ bị dis
        self._idtheocuaso = {}
        self._solandangnhaplaicuaso = {}
        # hwnd -> tên nhân vật (đã chuẩn hoá) lần cuối thấy trong cửa sổ đó: nhận ra cửa sổ bị dis của tài khoản chưa có ID
        self._tentheocuaso = {}
        # Tài khoản ("user") -> lúc bắt đầu vắng mà chưa đăng nhập lại được (báo Telegram khi vắng quá THOIGIANBAOVANG giây)
        self._batdauvang = {}
        # Theo dõi rớt game theo tài khoản ("user"): online lượt quét trước, [các lần rớt trong THOIGIANDEMBIDA giây], tạm hoãn tự
        # đăng nhập tới thời điểm này
        self._onlinetruoc = {}
        self._lanroigames = {}
        self._tamhoanden = {}
        self._luong = threading.Thread(target = self.loop, daemon = True)

    def batdau(self):
        self._luong.start()

    def _is_dangtamhoan(self, taikhoan):
        return time.time() < self._tamhoanden.get(taikhoan.get("user"), 0.)

    def _theodoiroigame(self, taikhoans, online):
        # Nhân vật đang online (lượt quét trước) mà giờ vắng: rớt mạng / bị đá (tài khoản đăng nhập ở máy khác) / game đóng -> báo
        # Telegram. Rớt SOLANBIDALIENTUC lần trong THOIGIANDEMBIDA giây thì gần như chắc có máy khác đang đăng nhập cùng tài khoản (vd chép
        # nhầm file tài khoản sang máy ảo, 2026-10-29 hai máy đá nhau cả buổi sáng): tạm hoãn tự đăng nhập tài khoản đó THOIGIANTAMHOAN
        # giây và báo, để hai máy thôi giành nhau
        import html
        from thongbao_xq import guitinmay
        now = time.time()
        for taikhoan in taikhoans:
            khoa = taikhoan.get("user")
            is_online = _is_taikhoanonline(taikhoan, online)
            if not khoa or is_online is None:
                continue
            if self._onlinetruoc.get(khoa) and not is_online:
                ten = html.escape(taikhoan.get("tennhanvat") or str(taikhoan.get("idnguoichoi") or khoa))
                lans =[t for t in self._lanroigames.get(khoa, []) if now - t < THOIGIANDEMBIDA] + [now]
                self._lanroigames[khoa] = lans
                if len(lans) >= SOLANBIDALIENTUC:
                    self._tamhoanden[khoa] = now + THOIGIANTAMHOAN
                    self._lanroigames[khoa] = []
                    print(f"[ĐĂNG NHẬP] {ten} rớt {len(lans)} lần trong {THOIGIANDEMBIDA // 60} phút: tạm hoãn tự đăng nhập {THOIGIANTAMHOAN // 60} phút")
                    guitinmay("dangnhap", f"🚫 <b>{ten}</b> bị đá khỏi game {len(lans)} lần trong {THOIGIANDEMBIDA // 60} phút\n"
                                          f"Có thể máy khác đang đăng nhập cùng tài khoản <b>{html.escape(khoa)}</b>. "
                                          f"Tạm hoãn tự đăng nhập tài khoản này {THOIGIANTAMHOAN // 60} phút.", khoa = ("bida", khoa), giancach = 600.)
                else:
                    guitinmay("dangnhap", f"⚠️ <b>{ten}</b> rớt khỏi game (mất kết nối, game đóng hoặc tài khoản bị đăng nhập ở nơi khác)"
                                          f"{(', đang tạm hoãn tự đăng nhập' if self._is_dangtamhoan(taikhoan) else ', đang tự đăng nhập lại') if self.is_bat else ''}",
                             khoa = ("roigame", khoa), giancach = 120.)
            self._onlinetruoc[khoa] = is_online

    def set_is_bat(self, is_bat):
        global is_chophepdong
        self.is_bat = bool(is_bat)
        is_chophepdong = self.is_bat
        cauhinh = taicauhinhdangnhap()
        cauhinh["is_tudongdangnhap"] = self.is_bat
        luucauhinhdangnhap(cauhinh)
        print(f"[ĐĂNG NHẬP] {'Bật' if self.is_bat else 'Tắt'} tự động đăng nhập")

    def loop(self):
        while True:
            try:
                self._mot_luot()
            except Exception as e:
                self.trangthai = f"Lỗi: {e}"
                print(f"[ĐĂNG NHẬP] Lỗi vòng lặp: {e}")
            time.sleep(5)

    def _mot_luot(self):
        # Đọc file cả khi đang tắt để giao diện thấy danh sách tài khoản / lỗi file ngay sau khi sửa
        cauhinh = taicauhinhdangnhap()
        if cauhinh.get("loi"):
            self.trangthai = cauhinh["loi"]
            self.danhsach = []
            return
        if not self.is_bat:
            self.trangthai = "Đang tắt"
            self.danhsach = [(taikhoan.get("tennhanvat") or str(taikhoan.get("user")), taikhoan.get("idnguoichoi"), "chưa kiểm tra")
                             for taikhoan in cauhinh["taikhoans"]]
            return

        # Nhân vật nào đang tạm ngưng (ẩn thân / người lạ) thì không đăng nhập ai cả cho tới khi hết hạn
        tamngungs = laytamngungdanghieuluc()
        if tamngungs:
            idnguoichoi, thoidiemhet, lydo = tamngungs[0]
            conlai = int(thoidiemhet - time.time())
            self.trangthai = f"Tạm ngưng (ID {idnguoichoi}: {lydo}) – còn {conlai // 60}:{conlai % 60:02d}"
            return

        taikhoans = cauhinh["taikhoans"]
        if not taikhoans:
            self.trangthai = f"Chưa có tài khoản nào trong {os.path.basename(duongdantaikhoan())}"
            return

        dondeptientrinhaovuabithoatgame()
        online = laydanhsachnhanvatonlines()

        self._tudienid(cauhinh, online)

        # Cửa sổ đang có nhân vật: nhớ là của ai. Cửa sổ đã đóng thì quên
        for hwnd, idnguoichoi in online["cuaso"].items():
            self._idtheocuaso[hwnd] = idnguoichoi
            if online["tentheocuaso"].get(hwnd):
                self._tentheocuaso[hwnd] = online["tentheocuaso"][hwnd]
            self._solandangnhaplaicuaso.pop(hwnd, None)
        for hwnd in [h for h in self._idtheocuaso if not win32gui.IsWindow(h)]:
            self._idtheocuaso.pop(hwnd, None)
            self._tentheocuaso.pop(hwnd, None)
            self._solandangnhaplaicuaso.pop(hwnd, None)
        # Cửa sổ bị dis: đang ở màn hình đăng nhập, nhân vật của nó chưa online ở cửa sổ khác, chưa thử đăng nhập lại quá
        # SOLANDANGNHAPLAICUASODIS lần. Không đóng / kill, không nhận nhầm là cửa sổ mới mở
        cuasodis = {hwnd: idnguoichoi for hwnd, idnguoichoi in self._idtheocuaso.items()
                    if hwnd not in online["cuaso"] and idnguoichoi not in online["id"]
                    and self._solandangnhaplaicuaso.get(hwnd, 0) < SOLANDANGNHAPLAICUASODIS and _is_cuasomanhinhdangnhap(hwnd)}

        # Nhân vật vắng có cửa sổ bị dis được đăng nhập trước: dis cùng lúc nhiều acc mà lấy nhân vật đầu danh sách (cửa sổ của nó đã
        # hết lượt thử) thì phải mở client mới trong khi các cửa sổ bị dis khác vẫn chiếm đủ chỗ. Khớp cửa sổ theo ID, tài khoản chưa có
        # ID thì theo tên (trước đây chỉ theo ID: 4 tài khoản chưa điền ID bị dis cùng lúc thì không cửa sổ nào khớp, mở client mới
        # cũng không được vì cả 4 cửa sổ đang giữ chỗ -> kẹt mãi, 2026-10-29)
        def cuasodiscua(taikhoan):
            return next((hwnd for hwnd, idnguoichoi in cuasodis.items()
                         if _is_cuasocuataikhoan(taikhoan, idnguoichoi, self._tentheocuaso.get(hwnd))), None)

        self._theodoiroigame(taikhoans, online)
        # Tài khoản đang tạm hoãn (bị đá liên tục: máy khác đang đăng nhập cùng tài khoản) thì không đăng nhập lại, kẻo hai máy đá nhau mãi
        vangs = [taikhoan for taikhoan in taikhoans if _is_taikhoanonline(taikhoan, online) is False and not self._is_dangtamhoan(taikhoan)]
        self._baovanglau(taikhoans, online, vangs)
        canhdangnhap = next((taikhoan for taikhoan in vangs if cuasodiscua(taikhoan)), vangs[0] if vangs else None)
        danhsach = []
        for taikhoan in taikhoans:
            is_online = _is_taikhoanonline(taikhoan, online)
            ten = taikhoan.get("tennhanvat") or str(taikhoan.get("idnguoichoi") or taikhoan.get("user"))
            if is_online is None:
                danhsach.append((ten, None, "thiếu ID/tên"))
            elif is_online is False and self._is_dangtamhoan(taikhoan):
                conlai = int(self._tamhoanden[taikhoan.get("user")] - time.time()) // 60 + 1
                danhsach.append((ten, taikhoan.get("idnguoichoi"), f"tạm hoãn {conlai} phút (bị đá liên tục)"))
            elif taikhoan is canhdangnhap:
                danhsach.append((ten, taikhoan.get("idnguoichoi"), "đang đăng nhập"))
            else:
                danhsach.append((ten, taikhoan.get("idnguoichoi"), "online" if is_online else "vắng"))
        self.danhsach = danhsach

        if canhdangnhap is None:
            self.trangthai = f"Đủ {sum(1 for d in danhsach if d[2] == 'online')}/{len(taikhoans)} nhân vật online"
            return

        ten = canhdangnhap.get("tennhanvat") or str(canhdangnhap.get("idnguoichoi"))
        hwnd_dis = cuasodiscua(canhdangnhap)
        if hwnd_dis:
            # Đăng nhập lại ngay trong cửa sổ bị dis: vào lại tại chỗ (phó bản), không về thành
            self._solandangnhaplaicuaso[hwnd_dis] = self._solandangnhaplaicuaso.get(hwnd_dis, 0) + 1
            self.trangthai = f"Đang đăng nhập lại {ten} trong cửa sổ bị dis..."
            print(f"\n[ĐĂNG NHẬP] {ten} bị dis, đăng nhập lại ngay trong cửa sổ cũ (HWND: {hwnd_dis}, lần {self._solandangnhaplaicuaso[hwnd_dis]})")
            dangnhaptrongcuaso(hwnd_dis, ten, canhdangnhap)
            return
        self.trangthai = f"Đang đăng nhập {ten}..."
        if mogamevadangnhap(ten, canhdangnhap, cauhinh["duongdangame"], cuasogiuchos = set(cuasodis)) is False and cuasodis:
            # Đủ client mà chỗ nào cũng bị cửa sổ dis giữ (của nhân vật khác / không nhận ra của ai): bỏ giữ chỗ để lượt sau đóng được
            # một cửa sổ mà mở client mới, không thì kẹt mãi
            import html
            from thongbao_xq import guitinmay
            print(f"   -> Bỏ giữ chỗ {len(cuasodis)} cửa sổ bị dis để mở được client mới cho {ten}")
            for hwnd in cuasodis:
                self._solandangnhaplaicuaso[hwnd] = SOLANDANGNHAPLAICUASODIS
            guitinmay("dangnhap", f"⚠️ Đủ {SOCLIENTTOIDA} client đều là cửa sổ bị dis đang giữ chỗ, không mở thêm được để đăng nhập "
                                  f"<b>{html.escape(ten)}</b>: bỏ giữ chỗ, đóng bớt cửa sổ dis rồi mở client mới", khoa = "kethetcho", giancach = 600.)

    def _tudienid(self, cauhinh, online):
        # Tài khoản chưa điền ID mà nhân vật cùng tên đang online: ghi ID vào file tài khoản (ID cố định, tên có thể đổi; nhận cửa sổ bị
        # dis theo ID chắc hơn theo tên)
        tentheoid = {}
        for hwnd, idnguoichoi in online["cuaso"].items():
            if online["tentheocuaso"].get(hwnd):
                tentheoid[online["tentheocuaso"][hwnd]] = idnguoichoi
        dadien = []
        for taikhoan in cauhinh["taikhoans"]:
            ten = chuanhoatennhanvat(taikhoan.get("tennhanvat"))
            if not taikhoan.get("idnguoichoi") and ten in tentheoid:
                taikhoan["idnguoichoi"] = tentheoid[ten]
                dadien.append(f"{taikhoan.get('tennhanvat')} = {tentheoid[ten]}")
        if dadien:
            print(f"[ĐĂNG NHẬP] Tự điền ID vào {os.path.basename(duongdantaikhoan())}: {', '.join(dadien)}")
            luucauhinhdangnhap(cauhinh)

    def _baovanglau(self, taikhoans, online, vangs):
        # Nhân vật vắng quá THOIGIANBAOVANG giây mà vẫn chưa vào lại được: báo Telegram (30 phút nhắc lại 1 lần)
        import html
        from thongbao_xq import guitinmay
        now = time.time()
        khoavangs = {taikhoan.get("user") for taikhoan in vangs}
        for khoa in [k for k in self._batdauvang if k not in khoavangs]:
            self._batdauvang.pop(khoa)
        for taikhoan in vangs:
            khoa = taikhoan.get("user")
            batdau = self._batdauvang.setdefault(khoa, now)
            if now - batdau >= THOIGIANBAOVANG:
                ten = html.escape(taikhoan.get("tennhanvat") or str(taikhoan.get("idnguoichoi") or khoa))
                guitinmay("dangnhap", f"❗ <b>{ten}</b> vắng {int(now - batdau) // 60} phút mà tự đăng nhập chưa đưa vào lại được "
                                      f"({self.trangthai})", khoa = ("vanglau", khoa), giancach = 1800.)
