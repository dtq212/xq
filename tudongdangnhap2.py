DUONGDAN_GAME = r"E:\Games\ChienQuoc2D_Aegis\xq.exe"
LAUNCHER_TITLE = "client 2.01.07"
GAME_TITLE_LOGIN_SCREEN = "Chien Quoc 2D --ooo2026ooo-- v.2.01.07"
GAME_TITLE_PREFIX = "Chien Quoc 2D"

DANH_SACH_CUA_SO_LOI = ["warning", "play"]

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

# Mỗi phần tử là 1 tài khoản; nhận diện online theo "idnguoichoi" (cố định). Chưa điền ID thì tạm so theo "tennhanvat"
THONGTINDANGNHAPs = [
    {
        "tennhanvat": "Mộc Lan",
        "idnguoichoi": 132,
        "user": "moclan",
        "pass": "hateva",
        "group": 1,
        "server": 1,
        "char_index": 1,
        "vitricuaso": 1,
    },
    {
        "tennhanvat": "tieuhac",
        "idnguoichoi": 133,
        "user": "tieuhac",
        "pass": "hateva",
        "group": 1,
        "server": 1,
        "char_index": 1,
        "vitricuaso": 2,
    },
    {
        "tennhanvat": "Suong Chieu",
        "idnguoichoi": 134,
        "user": "suongchieu",
        "pass": "hateva",
        "group": 1,
        "server": 1,
        "char_index": 1,
        "vitricuaso": 3,
    },
    {
        "tennhanvat": "BốBánhBao",
        "idnguoichoi": 135,
        "user": "bobanhbao",
        "pass": "hateva",
        "group": 1,
        "server": 1,
        "char_index": 1,
        "vitricuaso": 4,
    },
]

import csv
import os
import subprocess
import time

import pywintypes
import win32api
import win32con
import win32gui
import win32process

from moitruong_xq import MoiTruong
from tienich_xq import laytamngungdanghieuluc


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


def right_click(hwnd, x, y, delay = 0.1):
    chonhaphimdieukhien()
    lparam = make_lparam(x, y)
    _safe_post_message(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_RBUTTONUP, 0, lparam)
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


def press_combo(hwnd, modifier, key, delay = 0.1):
    chonhaphimdieukhien()
    _safe_post_message(hwnd, win32con.WM_KEYDOWN, modifier, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYUP, key, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYUP, modifier, 0)
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
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output = True)
            print(f"✅ Đã đóng thành công cửa sổ lỗi (PID: {pid}).")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi cố gắng dọn dẹp cửa sổ: {e}")
            return False


def chuanhoatennhanvat(tennhanvat):
    # Gộp mọi loại khoảng trắng (kể cả Alt+255 / U+00A0 trong tên nhân vật) thành dấu cách thường trước khi so
    return " ".join((tennhanvat or "").split()).lower()


def laydanhsachnhanvatonlines():
    online_chars = {"ten": set(), "id": set()}

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
                        tennhanvat = chuanhoatennhanvat(mt.get_tendoituong())
                        if tennhanvat:
                            online_chars["ten"].add(tennhanvat)
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


def timcuasogamedangbiket():
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if GAME_TITLE_LOGIN_SCREEN in title:
                r = win32gui.GetWindowRect(hwnd)
                w, h = r[2] - r[0], r[3] - r[1]
                if 790 < w < 830 and 590 < h < 660 and not _is_cuasodadangnhap(hwnd):
                    hwnd_found = hwnd

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def mogamevadangnhap(char_name, config):
    print(f"\n[MANAGER] >>> BẮT ĐẦU QUY TRÌNH CHO: {char_name}")
    try:
        hwnd_game_stuck = timcuasogamedangbiket()
        if hwnd_game_stuck:
            print(f"   -> Phát hiện cửa sổ chờ (HWND: {hwnd_game_stuck}). Đang đóng...")
            try:
                win32gui.PostMessage(hwnd_game_stuck, win32con.WM_CLOSE, 0, 0)
                time.sleep(5)
            except Exception as e:
                print(f"   -> Lỗi khi đóng cửa sổ cũ: {e}")

        hwnd_launcher = timlauncherdangmo()
        if hwnd_launcher:
            print(f"   -> Tìm thấy Launcher (HWND: {hwnd_launcher}).")
            if win32gui.IsIconic(hwnd_launcher):
                win32gui.ShowWindow(hwnd_launcher, win32con.SW_SHOWNOACTIVATE)
        else:
            print("   -> Mở file exe mới...")
            game_dir = os.path.dirname(DUONGDAN_GAME)

            dondepclientkhongdangnhap()

            max_retries = 3
            success_open = False

            for attempt in range(max_retries):
                print(f"      [Lần thử {attempt + 1}/{max_retries}] Đang chạy lệnh mở game...")
                subprocess.Popen(DUONGDAN_GAME, cwd = game_dir)

                # Chờ launcher tối đa 10s, kiểm tra mỗi 0.5s (trước đây 15 x 2s = 30s)
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
                            win32gui.PostMessage(hwnd_error, win32con.WM_CLOSE, 0, 0)
                        except Exception as e:
                            print(f"      -> Lỗi khi đóng: {e}")

                        dondeptientrinhaovuabithoatgame()
                        dondepclientkhongdangnhap(tuoitoithieu = 0.)

                        break

                    time.sleep(0.5)
                    print(f"\r      Chờ Launcher... {(i + 1) * 0.5:.1f}s", end = "")

                print("")

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
            hwnd_game = timcuasogamedangbiket()
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

    xq_pids = set()
    try:
        output = subprocess.check_output(
            ['tasklist', '/FI', 'IMAGENAME eq xq.exe', '/FO', 'CSV', '/NH']
        ).decode('utf-8', errors = 'ignore')

        reader = csv.reader(output.splitlines())
        for row in reader:
            if len(row) > 1 and 'xq.exe' in row[0].lower():
                xq_pids.add(int(row[1]))
    except subprocess.CalledProcessError:
        pass
    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách tiến trình: {e}")

    ghost_pids = xq_pids - valid_pids

    if ghost_pids:
        print(f"[CLEANUP] Đang kiểm tra các tiến trình xq.exe bị treo ngầm...")

        for pid in ghost_pids:
            print(f"   ⚠️ Phát hiện xq.exe ảo (PID: {pid}). Đang tiến hành kill...")
            try:
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output = True)
                print(f"   ✅ Đã đóng thành công xq.exe ảo (PID: {pid}).")
            except Exception as e:
                print(f"   ❌ Lỗi khi kill PID {pid}: {e}")

        chotientrinhthoat(ghost_pids)


def donglauncher(hwnd_launcher):
    # Launcher bị đơ không vào được game: đóng nhẹ trước, không được thì kill tiến trình rồi chờ thoát hẳn
    if not hwnd_launcher or not win32gui.IsWindow(hwnd_launcher):
        return
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd_launcher)
    except pywintypes.error:
        return
    try:
        win32gui.PostMessage(hwnd_launcher, win32con.WM_CLOSE, 0, 0)
    except pywintypes.error:
        pass
    for _ in range(10):
        time.sleep(0.5)
        if not win32gui.IsWindow(hwnd_launcher):
            break
    else:
        print(f"   ⚠️ Launcher không tự đóng (PID: {pid}). Đang kill...")
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output = True)
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


def dondepclientkhongdangnhap(tuoitoithieu = 120.):
    # Client vừa bị dis vẫn còn cửa sổ "Chien Quoc 2D..." nên không bị coi là tiến trình ảo, nhưng vẫn chiếm suất
    # => game báo "You can not run more client program!". Kill các client không có nhân vật đang đăng nhập.
    # Bỏ qua client mới mở (< tuoitoithieu giây) vì có thể đang đăng nhập dở (vd tudongdangnhap2.py chạy song song).
    pid_dangnhaps = set()
    pid_cuasogames = set()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and GAME_TITLE_PREFIX in win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pid_cuasogames.add(pid)
            if _is_cuasodadangnhap(hwnd):
                pid_dangnhaps.add(pid)

    win32gui.EnumWindows(callback, None)

    pid_cankills = [pid for pid in pid_cuasogames - pid_dangnhaps if _laytuoitientrinh(pid) >= tuoitoithieu]
    for pid in pid_cankills:
        print(f"   ⚠️ Client không còn nhân vật đăng nhập (bị dis?) (PID: {pid}). Đang kill...")
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output = True)
    if pid_cankills:
        chotientrinhthoat(pid_cankills)


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
        (0, 0),                                                                  # 1 (Index 0): Trái Trên
        (screen_width - window_width, 0),                                        # 2 (Index 1): Phải Trên
        (0, screen_height - window_height - taskbar_height),                     # 3 (Index 2): Trái Dưới
        (screen_width - window_width, screen_height - window_height - taskbar_height) # 4 (Index 3): Phải Dưới
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

def main():
    print("=== TRÌNH QUẢN LÝ ĐĂNG NHẬP THÔNG MINH ===")
    while True:
        try:
            # Nhân vật nào đang tạm ngưng (ẩn thân / người lạ) thì không đăng nhập ai cả cho tới khi hết hạn
            tamngungs = laytamngungdanghieuluc()
            if tamngungs:
                idnguoichoi, thoidiemhet, lydo = tamngungs[0]
                conlai = int(thoidiemhet - time.time())
                print(f"[TẠM NGƯNG] ID {idnguoichoi}: {lydo} -> không đăng nhập, còn {conlai // 60}:{conlai % 60:02d}")
                time.sleep(5)
                continue
            dondeptientrinhaovuabithoatgame()
            online = laydanhsachnhanvatonlines()
            print(f"\n[SCAN] Đang online: {sorted(online['ten'])}")
            for cauhinh in THONGTINDANGNHAPs:
                tennhanvat = cauhinh.get("tennhanvat")
                idnguoichoi = cauhinh.get("idnguoichoi")
                # Ưu tiên ID (cố định); chưa điền ID thì tạm so theo tên (tên có thể đổi)
                if idnguoichoi:
                    is_online = int(idnguoichoi) in online["id"]
                elif tennhanvat:
                    is_online = chuanhoatennhanvat(tennhanvat) in online["ten"]
                else:
                    print(f"⚠️ Tài khoản {cauhinh.get('user')} chưa điền 'idnguoichoi' hay 'tennhanvat' -> Bỏ qua.")
                    continue
                tennhanvat = tennhanvat or str(idnguoichoi)
                if not is_online:
                    print(f"⚠️ {tennhanvat} vắng mặt -> Kích hoạt đăng nhập.")
                    mogamevadangnhap(tennhanvat, cauhinh)
                    break
            print("[WAIT] Chờ 5s quét lại...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Dừng tool.")
            break
        except Exception as e:
            print(f"Lỗi vòng lặp chính: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()