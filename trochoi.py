import threading
import sys
import threading
import time
import traceback

import keyboard
import win32api
import win32gui

from cuaso import CuaSo
from tienich import phatam


def debug_dump_threads():
    print("\n" + "=" * 30 + " DEBUG: DUMP STACK TRACE " + "=" * 30)
    frames = sys._current_frames()
    for thread_id, frame in frames.items():
        thread_name = "Unknown"
        for t in threading.enumerate():
            if t.ident == thread_id:
                thread_name = t.name
                break
        print(f"\n🧵 Thread: {thread_name} (ID: {thread_id})")
        traceback.print_stack(frame)
    print("=" * 80 + "\n")


def loop_cuaso(cuaso: CuaSo):
    try:
        cuaso.loop()
    except:
        pass


class TroChoi:
    def __init__(self):
        self.cuaso = None
        self.is_dangchay = threading.Event()
        self.remove1 = keyboard.add_hotkey("f12", self.themcuasohientai)
        self.remove2 = keyboard.add_hotkey("ctrl + alt + f12", lambda: self.is_dangchay.set())
        self.thoidiemmogamemoigannhat = time.time()

    def __del__(self):
        try:
            keyboard.remove_hotkey(self.remove1)
            keyboard.remove_hotkey(self.remove2)
        except:
            pass

    def themcuasohientai(self):
        if self.cuaso is not None:
            return

        idcuaso = win32gui.GetForegroundWindow()
        tencuaso = win32gui.GetWindowText(idcuaso)

        if not (tencuaso and tencuaso.startswith("Chien Quoc")):
            phatam("Không phải cửa sổ game")
            return

        phatam("Đã kết nối thành công")
        print(f"Tool đã kết nối với cửa sổ: {tencuaso} (ID: {idcuaso})")

        self.cuaso = CuaSo(idcuaso)

        threading.Thread(target = loop_cuaso, args = [self.cuaso], daemon = True).start()

    def tatauto(self):
        if self.cuaso:
            self.cuaso.tatauto()

    def loop_quanly(self):
        while not self.is_dangchay.is_set():
            try:
                if self.cuaso:
                    if self.cuaso.main_stop.is_set() or not self.cuaso.moitruong.get_is_cuasogametontai():
                        phatam("Game đã bị đóng hoặc ngắt kết nối")
                        self.cuaso.main_stop.set()
                        self.cuaso = None
            except Exception as e:
                print(f"Lỗi giám sát: {e}")

            time.sleep(1)


if __name__ == "__main__":
    trochoi = TroChoi()

    t_quanly = threading.Thread(target = trochoi.loop_quanly, daemon = True)
    t_quanly.start()

    print("=" * 50)
    print("TOOL CHIẾN QUỐC (CHẾ ĐỘ ĐA CỬA SỔ)")
    print("Hướng dẫn:")
    print("1. Mở Tool này lên.")
    print("2. Vào game, bấm F12 để kết nối.")
    print("3. Muốn chạy thêm acc khác? -> Mở thêm 1 bản Tool nữa rồi làm lại bước 2.")
    print("-" * 50)
    print("👉 Bấm [INSERT] để Debug.")
    print("👉 Bấm [PAUSE] để Dừng.")
    print("=" * 50)

    while not trochoi.is_dangchay.is_set():
        if win32api.GetAsyncKeyState(0x2D) & 0x8000:
            debug_dump_threads()
            time.sleep(1)

        if win32api.GetAsyncKeyState(0x13) & 0x8000:
            print("\n🛑 Dừng tool!")
            trochoi.is_dangchay.set()
            break

        time.sleep(0.1)

    trochoi.tatauto()