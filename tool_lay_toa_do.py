import time
import win32gui
import win32api

# Tên cửa sổ game (Chỉ cần một phần tên là được)
WINDOW_TITLE = "Chien Quoc - Loan The Anh Hung"


def main():
    print("=" * 50)
    print("   TOOL LẤY TỌA ĐỘ TƯƠNG ĐỐI (RELATIVE)")
    print("=" * 50)
    print(f"[-] Đang tìm cửa sổ chứa từ khóa: '{WINDOW_TITLE}'...")
    print("[-] Hướng dẫn:")
    print("    1. Di chuột vào vị trí cần lấy (Ô tài khoản, Nút bấm...)")
    print("    2. Nhìn con số (X, Y) hiện trên màn hình console này.")
    print("    3. Ghi lại số đó vào file cấu hình.")
    print("[-] Nhấn Ctrl + C để dừng chương trình.\n")

    hwnd_found = 0

    # Tìm cửa sổ game
    def callback(hwnd, _):
        nonlocal hwnd_found
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if WINDOW_TITLE in title:
                hwnd_found = hwnd

    win32gui.EnumWindows(callback, None)

    if not hwnd_found:
        print("❌ LỖI: Không tìm thấy cửa sổ game! Hãy mở game trước.")
        return

    title = win32gui.GetWindowText(hwnd_found)
    print(f"✅ Đã kết nối với cửa sổ: [{title}]")
    print("-" * 50)

    try:
        while True:
            # Lấy vị trí chuột trên toàn màn hình
            mouse_x, mouse_y = win32api.GetCursorPos()

            # Lấy vị trí góc trái trên của cửa sổ game
            rect = win32gui.GetWindowRect(hwnd_found)
            win_x = rect[0]
            win_y = rect[1]

            # Tính toán tọa độ tương đối
            # Công thức: Tọa độ chuột - Tọa độ cửa sổ
            rel_x = mouse_x - win_x
            rel_y = mouse_y - win_y

            # In đè lên dòng cũ để dễ nhìn
            print(f"\r👉 Tọa độ Relative: ({rel_x}, {rel_y})        ", end = "")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nĐã dừng tool.")


if __name__ == "__main__":
    main()