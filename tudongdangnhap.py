import os
import subprocess
import time

import pywintypes
import win32process
import win32gui
import win32con
from moitruong_xq import MoiTruong


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


def _safe_post_message(hwnd, msg, wparam, lparam):
    try:
        win32gui.PostMessage(hwnd, msg, wparam, lparam)
    except pywintypes.error as e:
        if e.winerror == 1400:
            return
        raise e


def click(hwnd, x, y, delay = 0.1):
    lparam = make_lparam(x, y)
    _safe_post_message(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
    time.sleep(delay)


def right_click(hwnd, x, y, delay = 0.1):
    lparam = make_lparam(x, y)
    _safe_post_message(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_RBUTTONUP, 0, lparam)
    time.sleep(delay)


def press_key(hwnd, key_code, delay = 0.1):
    _safe_post_message(hwnd, win32con.WM_KEYDOWN, key_code, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYUP, key_code, 0)
    time.sleep(delay)


def type_text(hwnd, text, delay = 0.05):
    for char in text:
        _safe_post_message(hwnd, win32con.WM_CHAR, ord(char), 0)
        time.sleep(delay)


def press_combo(hwnd, modifier, key, delay = 0.1):
    _safe_post_message(hwnd, win32con.WM_KEYDOWN, modifier, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYUP, key, 0)
    time.sleep(0.05)
    _safe_post_message(hwnd, win32con.WM_KEYUP, modifier, 0)
    time.sleep(delay)


DUONGDAN_GAME = r"C:\Users\Admin\Desktop\ChienQuoc2\ChienQuoc2 - Live\xq.exe"
LAUNCHER_TITLE = "client 1.01.82"
GAME_TITLE_LOGIN_SCREEN = "Chien Quoc 2 - That Hung Tranh Ba.1.01.82"
GAME_TITLE_PREFIX = "Chien Quoc 2 ("

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

THONGTINDANGNHAP_MAP = {
    # "59309": {
    #     "user": "kngaivacham",
    #     "pass": "hateva",
    #     "group": 1,
    #     "server": 1,
    # },
    # "59306": {
    #     "user": "dtq21295",
    #     "pass": "hateva",
    #     "group": 1,
    #     "server": 2,
    # },
    # "59410": {
    #     "user": "tholuumanh",
    #     "pass": "hateva",
    #     "group": 1,
    #     "server": 1,
    # },
    "59844": {
        "user": "tholuumanh",
        "pass": "hateva",
        "group": 1,
        "server": 1,
        "char_index": 5,
    },
    "59845": {
        "user": "ngoclasat",
        "pass": "hateva",
        "group": 1,
        "server": 1,
        "char_index": 5,
    }, 
    "59503": {
        "user": "dtq21295",
        "pass": "hateva",
        "group": 1,
        "server": 1,
        "char_index": 6,
    },
    # "59500": {
    #     "user": "tholuumanh",
    #     "pass": "hateva",
    #     "group": 1,
    #     "server": 1,
    #     "char_index": 3,
    # },
    # "59562": {
    #     "user": "ngoclasat",
    #     "pass": "hateva",
    #     "group": 1,
    #     "server": 2,
    #     "char_index": 3,
    # },
}


def kiem_tra_va_dong_cua_so_treo(hwnd):
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


def laydanhsachnhanvatonlines():
    online_chars = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if GAME_TITLE_PREFIX in title:
                is_hung = kiem_tra_va_dong_cua_so_treo(hwnd)
                if is_hung:
                    return

                try:
                    mt = MoiTruong(hwnd)
                    if mt.get_is_nhanvattontai():
                        idnguoichoi = mt.get_idnguoichoi()
                        if idnguoichoi:
                            online_chars.append(str(idnguoichoi))
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
            for loi_title in DANH_SACH_CUA_SO_LOI:
                if loi_title.lower() == title.lower():
                    hwnd_found = hwnd
                    break

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def timcuasogamedangbiket():
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if GAME_TITLE_LOGIN_SCREEN in title:
                r = win32gui.GetWindowRect(hwnd)
                w, h = r[2] - r[0], r[3] - r[1]
                if 790 < w < 830 and 590 < h < 660:
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
                win32gui.ShowWindow(hwnd_launcher, win32con.SW_RESTORE)
            try:
                win32gui.SetForegroundWindow(hwnd_launcher)
            except:
                pass
        else:
            print("   -> Mở file exe mới...")
            game_dir = os.path.dirname(DUONGDAN_GAME)

            max_retries = 3
            success_open = False

            for attempt in range(max_retries):
                print(f"      [Lần thử {attempt + 1}/{max_retries}] Đang chạy lệnh mở game...")
                subprocess.Popen(DUONGDAN_GAME, cwd = game_dir)

                for i in range(15):
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

                        print("      -> Chờ 15s để hệ thống ổn định...")
                        time.sleep(15)
                        continue

                    time.sleep(2)
                    print(f"\r      Chờ Launcher... {i + 1}", end = "")

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

        if not hwnd_game:
            print("❌ Lỗi: Cửa sổ Game không hiện lên!")
            return

        print(f"[5] Game đã lên (HWND: {hwnd_game}). Đợi load Login (2s)...")
        time.sleep(2)

        group_name = config.get("group")
        server_index = config.get("server", 1)

        if group_name in TOADO_CUMMAYCHU:
            print(f"   -> Chọn cụm {group_name}")
            gx, gy = TOADO_CUMMAYCHU[group_name]
            click(hwnd_game, gx, gy)
            time.sleep(0.5)

        try:
            idx = int(server_index)
            if idx in TOADO_MAYCHU:
                print(f"   -> Chọn server thứ {idx}")
                sx, sy = TOADO_MAYCHU[idx]
                click(hwnd_game, sx, sy)
                time.sleep(0.5)
                bx, by = TOADO_GAME["BTN_XACNHAN_SERVER"]
                click(hwnd_game, bx, by)
                time.sleep(2)
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

        print("   -> Chờ load nhân vật (5s)...")
        time.sleep(5)

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

        print(f"✅ Hoàn tất cho {char_name}. Nghỉ 5s...")
        time.sleep(15)

    except Exception as e:
        print(f"❌ Exception: {e}")


def main():
    print("=== TRÌNH QUẢN LÝ ĐĂNG NHẬP THÔNG MINH ===")
    while True:
        try:
            online = laydanhsachnhanvatonlines()
            print(f"\n[SCAN] Đang online: {online}")
            for tennhanvat, cauhinh in THONGTINDANGNHAP_MAP.items():
                if tennhanvat not in online:
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
