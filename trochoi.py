import os
import sys
import time
import subprocess
import threading
import keyboard
import win32event
import win32gui
import win32process
import win32api
import locale
import pymem
import winerror

from cuaso import CuaSo
from tienich import phatam


def loop_cuaso(cuaso: CuaSo):
    try:
        cuaso.loop()
    except:
        pass


class TroChoiWorker:
    def __init__(self, target_hwnd):
        self.cuaso = None
        self.target_hwnd = target_hwnd  # ID cửa sổ được chỉ định từ Tool Mẹ
        self.is_dangchay = threading.Event()

        self.remove2 = keyboard.add_hotkey("ctrl + alt + f12", lambda: self.is_dangchay.set())

    def __del__(self):
        try:
            keyboard.remove_hotkey(self.remove2)
        except:
            pass

    def khoidong(self):
        if not win32gui.IsWindow(self.target_hwnd):
            print(f"Cửa sổ {self.target_hwnd} không tồn tại.")
            return

        print(f"Worker đang khởi động cho HWND: {self.target_hwnd}")
        self.cuaso = CuaSo(self.target_hwnd)

        threading.Thread(target = loop_cuaso, args = [self.cuaso], daemon = True).start()

        self.loop_quanly()

    def loop_quanly(self):
        print(f"Worker bắt đầu giám sát cửa sổ {self.target_hwnd}...")

        while not self.is_dangchay.is_set():
            try:
                if self.cuaso.main_stop.is_set() or not self.cuaso.moitruong.get_is_cuasogametontai():
                    print("Game kết thúc hoặc mất kết nối -> Worker dừng lại.")
                    self.is_dangchay.set()
                    break

                if win32api.GetAsyncKeyState(0x13) & 0x8000:
                    self.is_dangchay.set()
                    break

            except Exception as e:
                print(f"Worker lỗi: {e}")

            time.sleep(0.5)

        # Dọn dẹp trước khi thoát
        if self.cuaso:
            self.cuaso.tatauto()
        os._exit(0)

class TroChoiManager:
    def __init__(self):
        self.managed_processes = {}
        self.lock = threading.Lock()

        keyboard.add_hotkey("f12", self.spawn_worker)

        print("=" * 50)
        print("TOOL CHIẾN QUỐC (CHẾ ĐỘ QUẢN LÝ ĐA TIẾN TRÌNH)")
        print("Trạng thái: Đang chờ lệnh...")
        print("1. Vào game bất kỳ -> Bấm F12 để kích hoạt Auto cho game đó.")
        print("2. Tool Mẹ này sẽ tự động mở một cửa sổ console riêng cho game đó.")
        print("3. Khi game tắt, cửa sổ console con sẽ tự tắt.")
        print("-" * 50)
        print("👉 Giữ nguyên cửa sổ này và đừng tắt nó!")
        print("=" * 50)

    def spawn_worker(self):
        hwnd = win32gui.GetForegroundWindow()
        tencuaso = win32gui.GetWindowText(hwnd)

        if not (tencuaso and tencuaso.startswith("Chien Quoc")):
            phatam("Không phải cửa sổ game")
            return

        with self.lock:
            dead_hwnds = [h for h, p in self.managed_processes.items() if p.poll() is not None]
            for h in dead_hwnds:
                del self.managed_processes[h]

            if hwnd in self.managed_processes:
                phatam("Cửa sổ này đang chạy Auto rồi")
                return

            phatam("Đang khởi động Auto mới")

            cmd = [sys.executable, __file__, "--child", str(hwnd)]

            try:
                proc = subprocess.Popen(cmd, creationflags=0x08000000)

                self.managed_processes[hwnd] = proc
                print(f"[Manager] Đã tạo Worker cho HWND {hwnd} (PID: {proc.pid})")
            except Exception as e:
                print(f"[Manager] Lỗi tạo Worker: {e}")
                phatam("Lỗi khởi động")

    def run(self):
        while True:
            time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--child":
        try:
            target_hwnd = int(sys.argv[2])
            worker = TroChoiWorker(target_hwnd)
            worker.khoidong()
        except Exception as e:
            print(f"Worker crash: {e}")
            time.sleep(5)
    else:
        name = "trochoi.exe"
        my_pid = os.getpid()
        is_duplicate = False

        mutex_name = "Global_Tool_ChienQuoc_Manager_Mutex"
        mutex = win32event.CreateMutex(None, True, mutex_name)
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            print("⚠️ Tool Quản Lý đang chạy rồi! Bạn không cần mở thêm.")
            phatam("Tool quản lý đang chạy rồi")
            time.sleep(2)
            sys.exit(0)

        manager = TroChoiManager()
        try:
            manager.run()
        except KeyboardInterrupt:
            pass