import os
import subprocess
import time
import win32gui
import shutil
import win32con
from moitruongcu import MoiTruong
from background_input import BackgroundInput

DUONGDAN_GAME = r"D:\Games\ChienQuocNew\chienquocnew\xq.exe"
LAUNCHER_TITLE = "client 1.01.68"
GAME_TITLE_LOGIN_SCREEN = "Chien Quoc - Loan The Anh Hung"
GAME_TITLE_PREFIX = "Chien Quoc ("

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

THONGTINDANGNHAP_MAP = {
    "Zhuangzi1": {
        "user": "zhuangzi1",
        "pass": "hateva1",
        "server": "Kênh 1",
    },
    "Zhuangzi2": {
        "user": "zhuangzi2",
        "pass": "hateva1",
        "server": "Kênh 1",
    },
    # "Dasshu": {
    #     "user": "dasshu",
    #     "pass": "hateva1",
    #     "server": "Kênh 3",
    # },
    # "Dasmurai": {
    #     "user": "dasmurai",
    #     "pass": "hateva1",
    #     "server": "Kênh 4",
    # },
    # "Laotsezu": {
    #     "user": "laotsezu",
    #     "pass": "hateva1",
    #     "server": "Kênh 2",
    # },
    # "TruyÂ Má»‡nh": {
    #     "user": "truymenh",
    #     "pass": "hateva1",
    #     "server": "Kênh 1",
    # },
}

def laydanhsachnhanvatonlines():
    online_chars = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if GAME_TITLE_PREFIX in title:
                try:
                    mt = MoiTruong(hwnd)
                    if mt.get_is_nhanvattontai():
                        ten = mt.get_tendoituong()
                        if ten: online_chars.append(ten)
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


def timgamevadangnhap():
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
        print("[1] Kiểm tra và dọn dẹp các cửa sổ Game đang kẹt ở màn hình chờ...")
        hwnd_game_stuck = timgamevadangnhap()

        if hwnd_game_stuck:
            print(f"   -> Phát hiện cửa sổ chờ (HWND: {hwnd_game_stuck}). Đang đóng để mở mới an toàn...")
            try:
                win32gui.PostMessage(hwnd_game_stuck, win32con.WM_CLOSE, 0, 0)
                time.sleep(15)
            except Exception as e:
                print(f"   -> Lỗi khi đóng cửa sổ cũ: {e}")
        else:
            print("   -> Không có cửa sổ thừa. Sạch sẽ.")

        print("[2] Tìm Launcher để khởi động game mới...")
        hwnd_launcher = timlauncherdangmo()

        if hwnd_launcher:
            print(f"   -> Tìm thấy Launcher có sẵn (HWND: {hwnd_launcher}).")
            if win32gui.IsIconic(hwnd_launcher):
                win32gui.ShowWindow(hwnd_launcher, win32con.SW_RESTORE)
            try:
                win32gui.SetForegroundWindow(hwnd_launcher)
            except:
                pass
        else:
            print("   -> Không có Launcher. Mở file exe mới...")
            game_dir = os.path.dirname(DUONGDAN_GAME)
            process = subprocess.Popen(DUONGDAN_GAME, cwd = game_dir)

            for i in range(30):
                hwnd_launcher = timlauncherdangmo()
                if hwnd_launcher: break
                time.sleep(1)
                print(f"\r      Chờ Launcher... {i + 1}s", end = "")
            print("")

        if not hwnd_launcher:
            print("❌ Lỗi: Không bật được Launcher!")
            return

        print(f"[3] Thao tác Launcher ({hwnd_launcher}). Click 'Vào Game'...")
        time.sleep(2)
        lx, ly = TOADO_LAUNCHER["BTN_VAO_GAME"]

        BackgroundInput.click(hwnd_launcher, lx, ly)
        time.sleep(1)
        BackgroundInput.click(hwnd_launcher, lx, ly)

        print("[4] Đang đợi cửa sổ Game mới bật lên...")
        hwnd_game = 0
        for i in range(60):
            time.sleep(1)
            hwnd_game = timgamevadangnhap()
            if hwnd_game: break

        if not hwnd_game:
            print("❌ Lỗi: Cửa sổ Game không hiện lên sau khi bấm Launcher!")
            return

        print(f"[5] Game đã lên (HWND: {hwnd_game}). Đợi load Login (8s)...")
        time.sleep(8)

        print("[6] Bắt đầu đăng nhập...")

        sv_name = config["server"]
        if sv_name in TOADO_SERVER_LIST:
            print(f"   -> Chọn {sv_name}")
            sx, sy = TOADO_SERVER_LIST[sv_name]
            BackgroundInput.click(hwnd_game, sx, sy)
            time.sleep(1)

            bx, by = TOADO_GAME["BTN_XACNHAN_SERVER"]
            BackgroundInput.click(hwnd_game, bx, by)
            print("   -> Chờ chuyển màn hình nhập liệu (3s)...")
            time.sleep(3)
        else:
            print(f"⚠️ Không tìm thấy tọa độ server {sv_name}. Bỏ qua bước chọn server.")

        print("   -> Nhập Tài khoản & Mật khẩu...")

        BackgroundInput.press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)

        # Xóa sạch ô cũ (phòng hờ)
        for _ in range(30):
            BackgroundInput.press_key(hwnd_game, win32con.VK_BACK, delay = 0.01)
        time.sleep(0.5)

        BackgroundInput.type_text(hwnd_game, config["user"])
        time.sleep(0.5)

        BackgroundInput.press_key(hwnd_game, win32con.VK_TAB)
        time.sleep(0.5)

        BackgroundInput.type_text(hwnd_game, config["pass"])
        time.sleep(0.5)

        print("   -> Enter đăng nhập")
        BackgroundInput.press_key(hwnd_game, win32con.VK_RETURN)

        print("   -> Chờ load nhân vật (5s)...")
        time.sleep(5)

        print("   -> Chọn nhân vật (Vào game)!")
        BackgroundInput.press_key(hwnd_game, win32con.VK_RETURN)

        print(f"✅ Hoàn tất cho {char_name}. Nghỉ 5s...")
        time.sleep(5)

    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("=== TRÌNH QUẢN LÝ ĐĂNG NHẬP THÔNG MINH (TITLE CHECK) ===")
    print(f"Màn hình Login: '{GAME_TITLE_LOGIN_SCREEN}'")

    while True:
        try:
            online = laydanhsachnhanvatonlines()
            print(f"\n[SCAN] Đang online: {online}")

            for tennhanvat, cauhinh in THONGTINDANGNHAP_MAP.items():
                if tennhanvat not in online:
                    print(f"⚠️ {tennhanvat} vắng mặt -> Kích hoạt đăng nhập.")
                    mogamevadangnhap(tennhanvat, cauhinh)
                    break

            print("[WAIT] Chờ 15s quét lại...")
            time.sleep(15)

        except KeyboardInterrupt:
            print("Dừng tool.")
            break
        except Exception as e:
            print(f"Lỗi vòng lặp chính: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()