import os
import subprocess
import time
import win32gui
import win32process
import win32con
from moitruong import MoiTruong
from background_input import BackgroundInput

DUONGDAN_GAME = r"D:\Games\ChienQuoc2D_New\ChienQuoc.exe"
LAUNCHER_TITLE = "client 1.01.68"
GAME_TITLE = "Chien Quoc - Loan The Anh Hung"

TOADO_LAUNCHER = {
    "BTN_VAO_GAME": (530, 495)
}

TOADO_GAME = {
    "BTN_XACNHAN_SERVER": (760, 465),
}

TOADO_SERVER_LIST = {
    "Kênh 1": (460, 185),
    "Kênh 2": (550, 205),
    "Kênh 3": (550, 225),
    "Kênh 4": (550, 245),
}

DANH_SACH_ACC = {
    "Xanh365": {
        "user": "xanh365",
        "pass": "xanh365",
        "server": "Kênh 1",
    },
    "Dasshu": {
        "user": "dasshu",
        "pass": "dasshu",
        "server": "Kênh 1",
    },
    "Dasmurai": {
        "user": "Dasmurai",
        "pass": "Dasmurai",
        "server": "Kênh 1",
    },
}


def get_online_characters():
    online_chars = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if GAME_TITLE in title:
                try:
                    mt = MoiTruong(hwnd)
                    if mt.get_is_nhanvattontai():
                        ten = mt.get_tendoituong()
                        if ten: online_chars.append(ten)
                except:
                    pass

    win32gui.EnumWindows(callback, None)
    return online_chars


def mo_va_dang_nhap(char_name, config):
    print(f"\n[MANAGER] >>> BẮT ĐẦU QUY TRÌNH CHO: {char_name}")
    try:
        print("[1] Mở file exe...")
        game_dir = os.path.dirname(DUONGDAN_GAME)
        process = subprocess.Popen(DUONGDAN_GAME, cwd = game_dir)

        hwnd_launcher = 0
        for _ in range(30):
            time.sleep(1)

            def find_launcher(hwnd, _):
                nonlocal hwnd_launcher
                if win32gui.IsWindowVisible(hwnd) and LAUNCHER_TITLE in win32gui.GetWindowText(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid == process.pid: hwnd_launcher = hwnd

            win32gui.EnumWindows(find_launcher, None)
            if hwnd_launcher: break

        if not hwnd_launcher:
            def find_launcher_nopid(hwnd, _):
                nonlocal hwnd_launcher
                if win32gui.IsWindowVisible(hwnd) and LAUNCHER_TITLE in win32gui.GetWindowText(hwnd):
                    hwnd_launcher = hwnd

            win32gui.EnumWindows(find_launcher_nopid, None)

        if not hwnd_launcher:
            print("❌ Lỗi: Không thấy Launcher!")
            return

        print(f"[2] Launcher lên (HWND: {hwnd_launcher}). Click 'Vào Game'...")
        time.sleep(2)
        lx, ly = TOADO_LAUNCHER["BTN_VAO_GAME"]
        BackgroundInput.click(hwnd_launcher, lx, ly)
        time.sleep(1)
        BackgroundInput.click(hwnd_launcher, lx, ly)

        print("[3] Đợi cửa sổ Game...")
        hwnd_game = 0
        for _ in range(60):
            time.sleep(1)

            def find_game(hwnd, _):
                nonlocal hwnd_game
                if win32gui.IsWindowVisible(hwnd) and GAME_TITLE in win32gui.GetWindowText(hwnd):
                    # Check kích thước game (khoảng 800x600 + viền)
                    r = win32gui.GetWindowRect(hwnd)
                    w, h = r[2] - r[0], r[3] - r[1]
                    if 790 < w < 830 and 590 < h < 660:
                        try:
                            mt = MoiTruong(hwnd)
                            if not mt.get_is_nhanvattontai():  # Chưa có nhân vật -> Cửa sổ Login
                                hwnd_game = hwnd
                        except:
                            pass

            win32gui.EnumWindows(find_game, None)
            if hwnd_game: break

        if not hwnd_game:
            print("❌ Lỗi: Game không lên!")
            return

        print(f"[4] Game lên (HWND: {hwnd_game}). Đợi load Login (8s)...")
        time.sleep(8)

        sv_name = config["server"]
        if sv_name in TOADO_SERVER_LIST:
            print(f"   -> Chọn {sv_name}")
            sx, sy = TOADO_SERVER_LIST[sv_name]
            BackgroundInput.click(hwnd_game, sx, sy)
            time.sleep(0.5)
            bx, by = TOADO_GAME["BTN_XACNHAN_SERVER"]
            BackgroundInput.click(hwnd_game, bx, by)
            print("   -> Chờ chuyển màn hình nhập liệu (3s)...")
            time.sleep(2)

        print("   -> Bắt đầu nhập liệu...")

        BackgroundInput.press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)

        for _ in range(30):
            BackgroundInput.press_key(hwnd_game, win32con.VK_BACK, delay = 0.01)
        time.sleep(0.5)

        BackgroundInput.type_text(hwnd_game, config["user"])
        time.sleep(0.5)

        BackgroundInput.press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)

        BackgroundInput.type_text(hwnd_game, config["pass"])
        time.sleep(0.5)

        print("   -> Enter Đăng nhập")
        BackgroundInput.press_key(hwnd_game, win32con.VK_RETURN)

        print("   -> Chờ load nhân vật (5s)...")
        time.sleep(2)

        print("   -> Vào game (Enter chọn nhân vật)!")
        BackgroundInput.press_key(hwnd_game, win32con.VK_RETURN)

        print(f"✅ Hoàn tất cho {char_name}. Nghỉ 10s...")
        time.sleep(10)

    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("=== TRÌNH QUẢN LÝ ĐĂNG NHẬP ĐỘC LẬP (ĐÃ FIX LOGIC TAB) ===")
    while True:
        try:
            online = get_online_characters()
            print(f"\n[SCAN] Đang online: {online}")

            for char_name, config in DANH_SACH_ACC.items():
                if char_name not in online:
                    print(f"⚠️ {char_name} vắng mặt -> Kích hoạt đăng nhập.")
                    mo_va_dang_nhap(char_name, config)
                    break

            print("[WAIT] Chờ 30s quét lại...")
            time.sleep(30)

        except KeyboardInterrupt:
            print("Dừng tool.")
            break
        except Exception as e:
            print(f"Lỗi vòng lặp chính: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()