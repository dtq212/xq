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
GAME_TITLE = "Chien Quoc"

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
        "server": "Kênh 3",
    },
    "Dasmurai": {
        "user": "Dasmurai",
        "pass": "Dasmurai",
        "server": "Kênh 4",
    },
}


def get_online_characters():
    """Quét tất cả cửa sổ game để xem ai đang online"""
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


def tim_launcher_dang_mo():
    """Tìm xem có Launcher nào đang mở sẵn không"""
    hwnd_found = 0

    def callback(hwnd, _):
        nonlocal hwnd_found
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Tìm chính xác tiêu đề Launcher
            if title == LAUNCHER_TITLE:
                hwnd_found = hwnd

    win32gui.EnumWindows(callback, None)
    return hwnd_found


def mo_va_dang_nhap(char_name, config):
    print(f"\n[MANAGER] >>> BẮT ĐẦU QUY TRÌNH CHO: {char_name}")
    try:
        # 1. Tìm hoặc Mở Launcher
        print("[1] Kiểm tra Launcher...")
        hwnd_launcher = tim_launcher_dang_mo()

        if hwnd_launcher:
            print(f"   -> Tìm thấy Launcher có sẵn (HWND: {hwnd_launcher}). Tái sử dụng.")
            # Nếu cửa sổ bị ẩn (minimize), khôi phục lại để click ăn
            if win32gui.IsIconic(hwnd_launcher):
                win32gui.ShowWindow(hwnd_launcher, win32con.SW_RESTORE)
            # Đưa lên trên cùng cho chắc (tùy chọn)
            try:
                win32gui.SetForegroundWindow(hwnd_launcher)
            except:
                pass
        else:
            print("   -> Không có Launcher. Đang mở file exe mới...")
            game_dir = os.path.dirname(DUONGDAN_GAME)
            process = subprocess.Popen(DUONGDAN_GAME, cwd = game_dir)

            # Chờ Launcher hiện lên (30s)
            for i in range(30):
                hwnd_launcher = tim_launcher_dang_mo()
                if hwnd_launcher: break
                time.sleep(1)
                print(f"\r      Chờ Launcher... {i + 1}s", end = "")
            print("")

        if not hwnd_launcher:
            print("❌ Lỗi: Không bật được Launcher!")
            return

        print(f"[2] Đang thao tác Launcher ({hwnd_launcher}). Click 'Vào Game'...")
        time.sleep(2)
        lx, ly = TOADO_LAUNCHER["BTN_VAO_GAME"]

        # Click 2 lần cho chắc ăn
        BackgroundInput.click(hwnd_launcher, lx, ly)
        time.sleep(1)
        BackgroundInput.click(hwnd_launcher, lx, ly)

        # 2. Chờ Game Client (Cửa sổ mới 800x600)
        print("[3] Đang đợi cửa sổ Game hiện lên...")
        hwnd_game = 0
        for i in range(60):
            time.sleep(1)

            def find_game(hwnd, _):
                nonlocal hwnd_game
                if win32gui.IsWindowVisible(hwnd) and GAME_TITLE in win32gui.GetWindowText(hwnd):
                    r = win32gui.GetWindowRect(hwnd)
                    w, h = r[2] - r[0], r[3] - r[1]
                    # Check kích thước chuẩn để không nhầm với Launcher (nếu launcher chưa tắt)
                    if 790 < w < 830 and 590 < h < 660:
                        # Kiểm tra xem cửa sổ này đã có nhân vật chưa (chưa có = Login screen)
                        try:
                            mt = MoiTruong(hwnd)
                            if not mt.get_is_nhanvattontai():
                                hwnd_game = hwnd
                        except:
                            pass

            win32gui.EnumWindows(find_game, None)
            if hwnd_game: break

        if not hwnd_game:
            print("❌ Lỗi: Cửa sổ Game không hiện lên sau khi bấm Launcher!")
            return

        print(f"[4] Game đã lên (HWND: {hwnd_game}). Đợi load Login (8s)...")
        time.sleep(8)

        # 3. Thao tác đăng nhập
        # Chọn Server
        sv_name = config["server"]
        if sv_name in TOADO_SERVER_LIST:
            print(f"   -> Chọn {sv_name}")
            sx, sy = TOADO_SERVER_LIST[sv_name]
            BackgroundInput.click(hwnd_game, sx, sy)
            time.sleep(0.5)
            # Xác nhận
            bx, by = TOADO_GAME["BTN_XACNHAN_SERVER"]
            BackgroundInput.click(hwnd_game, bx, by)
            print("   -> Chờ chuyển màn hình (3s)...")
            time.sleep(3)

        # Nhập TK/MK (Logic mới: Tab -> Xóa -> Gõ)
        print("   -> Nhập liệu (Tab & Backspace)...")

        # Nhấn Tab để lên ô Tài khoản (do mặc định ở ô Pass)
        BackgroundInput.press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)

        # Xóa sạch (Backspace 30 lần)
        for _ in range(30):
            BackgroundInput.press_key(hwnd_game, win32con.VK_BACK, delay = 0.01)
        time.sleep(0.5)

        # Gõ User
        BackgroundInput.type_text(hwnd_game, config["user"])
        time.sleep(0.5)

        # Tab xuống Pass
        BackgroundInput.press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)

        # Gõ Pass
        BackgroundInput.type_text(hwnd_game, config["pass"])
        time.sleep(0.5)

        # Enter Login
        print("   -> Enter đăng nhập")
        BackgroundInput.press_key(hwnd_game, win32con.VK_RETURN)

        print("   -> Chờ load nhân vật (5s)...")
        time.sleep(5)

        # Chọn nhân vật (Enter)
        print("   -> Chọn nhân vật (Vào game)!")
        BackgroundInput.press_key(hwnd_game, win32con.VK_RETURN)

        print(f"✅ Hoàn tất quy trình cho {char_name}. Nghỉ 10s...")
        time.sleep(10)

    except Exception as e:
        print(f"❌ Exception: {e}")


def main():
    print("=== TRÌNH QUẢN LÝ ĐĂNG NHẬP (TỰ DÙNG LAUNCHER CÓ SẴN) ===")
    while True:
        try:
            # 1. Kiểm tra ai đang online
            online = get_online_characters()
            print(f"\n[SCAN] Đang online: {online}")

            # 2. Đối chiếu danh sách cần online
            for char_name, config in DANH_SACH_ACC.items():
                if char_name not in online:
                    print(f"⚠️ {char_name} vắng mặt -> Kích hoạt đăng nhập.")
                    mo_va_dang_nhap(char_name, config)
                    break  # Mở từng acc một

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