import os
import subprocess
import time

import pywintypes
import win32process
import win32gui
import win32con
from moitruong_xq import MoiTruong
import csv
import win32api

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
        "server": 2,
        "char_index": 5,
    },
    "59845": {
        "user": "ngoclasat",
        "pass": "hateva",
        "group": 1,
        "server": 2,
        "char_index": 5,
    }, 

    "59636": {
        "user": "shoudi",
        "pass": "hateva",
        "group": 1,
        "server": 2,
        "char_index": 3,
    },
    "59637": {
        "user": "yuuhou",
        "pass": "hateva",
        "group": 1,
        "server": 2,
        "char_index": 3,
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

        print("   -> Đang sắp xếp lại các cửa sổ game...")
        sap_xep_cua_so_game()

        time.sleep(15)

    except Exception as e:
        print(f"❌ Exception: {e}")
def don_dep_process_xq_ao():
    """
    Quét và tiêu diệt các process xq.exe chạy ngầm không có cửa sổ game hợp lệ.
    """
    # Bước 1: Lấy danh sách Process ID (PID) của các cửa sổ game CÓ THẬT
    valid_pids = set() # Sử dụng set (tập hợp) để so sánh cho nhanh
    
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Nếu tiêu đề có chứa tiền tố game
            if GAME_TITLE_PREFIX in title:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                valid_pids.add(pid)

    win32gui.EnumWindows(callback, None)

    # Bước 2: Lấy tất cả PID của tiến trình xq.exe đang chạy ngầm trên hệ thống
    xq_pids = set()
    try:
        # Dùng lệnh tasklist của Windows để lấy danh sách xq.exe dưới dạng CSV
        output = subprocess.check_output(
            ['tasklist', '/FI', 'IMAGENAME eq xq.exe', '/FO', 'CSV', '/NH']
        ).decode('utf-8', errors='ignore')

        reader = csv.reader(output.splitlines())
        for row in reader:
            if len(row) > 1 and 'xq.exe' in row[0].lower():
                xq_pids.add(int(row[1])) # Cột 2 trong CSV của tasklist là PID
    except subprocess.CalledProcessError:
        # Sẽ nhảy vào đây nếu không có tiến trình xq.exe nào đang chạy (không sao cả)
        pass
    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách tiến trình: {e}")

    # Bước 3: Tìm ra các process ảo bằng phép trừ tập hợp và Kill chúng
    ghost_pids = xq_pids - valid_pids
    
    if ghost_pids:
        print(f"[CLEANUP] Đang kiểm tra các tiến trình xq.exe bị treo ngầm...")
        
    for pid in ghost_pids:
        print(f"   ⚠️ Phát hiện xq.exe ảo (PID: {pid}). Đang tiến hành kill...")
        try:
            # Ép buộc đóng tiến trình (/F) theo PID (/PID)
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
            print(f"   ✅ Đã dọn dẹp thành công xq.exe ảo (PID: {pid}).")
        except Exception as e:
            print(f"   ❌ Lỗi khi kill PID {pid}: {e}")

def sap_xep_cua_so_game():
    """
    Tìm tất cả các cửa sổ game đang mở và tự động sắp xếp chúng
    dàn đều trên màn hình theo dạng lưới (grid).
    """
    # 1. Tìm tất cả HWND của các cửa sổ game hợp lệ
    danh_sach_hwnd = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Chỉ lấy các cửa sổ có tên bắt đầu bằng "Chien Quoc 2 ("
            if GAME_TITLE_PREFIX in title:
                danh_sach_hwnd.append(hwnd)

    win32gui.EnumWindows(callback, None)

    if not danh_sach_hwnd:
        return  # Không có cửa sổ nào thì thoát luôn

    # 2. Lấy kích thước thật của màn hình máy tính
    screen_width = win32api.GetSystemMetrics(0)  # Chiều rộng (VD: 1920)
    # screen_height = win32api.GetSystemMetrics(1) # Chiều cao (VD: 1080) - Lưu lại nếu sau này cần

    # 3. Kích thước ước tính của một cửa sổ game (bạn có thể tinh chỉnh con số này)
    # Dựa vào hàm timcuasogamedangbiket của bạn, width ~ 810, height ~ 630
    window_width = 810
    window_height = 630

    # 4. Tính toán số lượng cột tối đa có thể xếp vừa trên màn hình
    so_cot = screen_width // window_width
    if so_cot == 0:
        so_cot = 1  # Đảm bảo ít nhất có 1 cột dù màn hình nhỏ

    # 5. Duyệt qua từng cửa sổ và đặt tọa độ
    for index, hwnd in enumerate(danh_sach_hwnd):
        # Tính toán hàng và cột dựa trên số thứ tự (index)
        hang = index // so_cot
        cot = index % so_cot

        # Tính tọa độ X (ngang) và Y (dọc)
        toado_x = cot * window_width
        toado_y = hang * window_height

        try:
            # Di chuyển cửa sổ.
            # Dùng cờ SWP_NOSIZE để giữ nguyên kích thước cửa sổ.
            # Dùng cờ SWP_NOZORDER để không làm thay đổi thứ tự lớp của cửa sổ.
            win32gui.SetWindowPos(
                hwnd,
                0,  # Không quan tâm đến Z-order vì đã có cờ SWP_NOZORDER
                toado_x,
                toado_y,
                0,
                0,
                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
            )
        except Exception as e:
            print(f"   ❌ Lỗi khi di chuyển cửa sổ (HWND: {hwnd}): {e}")
def main():
    print("=== TRÌNH QUẢN LÝ ĐĂNG NHẬP THÔNG MINH ===")
    while True:
        try:
            # Thêm dòng này: Dọn dẹp process ảo trước khi thực hiện các bước khác
            don_dep_process_xq_ao()

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