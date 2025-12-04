import win32gui
import win32con
import time
import pywintypes

def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)

class BackgroundInput:
    @staticmethod
    def _safe_post_message(hwnd, msg, wparam, lparam):
        """Hàm gửi tin nhắn an toàn, tự động bỏ qua nếu cửa sổ đã bị tắt"""
        try:
            win32gui.PostMessage(hwnd, msg, wparam, lparam)
        except pywintypes.error as e:
            # Mã lỗi 1400: Invalid window handle (Cửa sổ đã đóng)
            if e.winerror == 1400:
                return
            # Nếu là lỗi khác thì vẫn báo
            raise e

    @staticmethod
    def click(hwnd, x, y, delay=0.1):
        """Click chuột trái ngầm"""
        lparam = make_lparam(x, y)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
        time.sleep(delay)

    @staticmethod
    def right_click(hwnd, x, y, delay=0.1):
        """Click chuột phải ngầm"""
        lparam = make_lparam(x, y)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_RBUTTONUP, 0, lparam)
        time.sleep(delay)

    @staticmethod
    def press_key(hwnd, key_code, delay=0.1):
        """Nhấn một phím ngầm"""
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYDOWN, key_code, 0)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYUP, key_code, 0)
        time.sleep(delay)

    @staticmethod
    def type_text(hwnd, text, delay=0.05):
        """Gõ văn bản ngầm"""
        for char in text:
            BackgroundInput._safe_post_message(hwnd, win32con.WM_CHAR, ord(char), 0)
            time.sleep(delay)

    @staticmethod
    def press_combo(hwnd, modifier, key, delay=0.1):
        """Nhấn tổ hợp phím (Ví dụ Shift + Tab)"""
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYDOWN, modifier, 0)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYDOWN, key, 0)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYUP, key, 0)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYUP, modifier, 0)
        time.sleep(delay)