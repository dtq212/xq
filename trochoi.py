import os
import subprocess
import sys
import threading
import time

import keyboard
import win32api
import win32event
import win32gui
import winerror

from cuaso import CuaSo
from tienich import phatam

CREATE_NO_WINDOW = 0x08000000


def loop_cuaso(cuaso: CuaSo):
    try:
        cuaso.loop()
    except:
        pass


class TroChoiWorker:
    def __init__(self, target_hwnd):
        self.cuaso = None
        self.target_hwnd = target_hwnd
        self.is_dangchay = threading.Event()
        self.remove2 = keyboard.add_hotkey("ctrl + alt + f12", lambda: self.is_dangchay.set())

    def __del__(self):
        try:
            keyboard.remove_hotkey(self.remove2)
        except:
            pass

    def khoidong(self):
        if not win32gui.IsWindow(self.target_hwnd):
            return

        self.cuaso = CuaSo(self.target_hwnd)
        threading.Thread(target = loop_cuaso, args = [self.cuaso], daemon = True).start()
        self.loop_quanly()

    def loop_quanly(self):
        thoi_gian_mat_ket_noi = 0

        while not self.is_dangchay.is_set():
            try:
                if self.cuaso.main_stop.is_set() or not self.cuaso.moitruong.get_is_cuasogametontai():
                    self.is_dangchay.set()
                    break

                if win32api.GetAsyncKeyState(0x13) & 0x8000:
                    self.is_dangchay.set()
                    break

                if self.cuaso.moitruong.get_is_dangmatketnoi():
                    if thoi_gian_mat_ket_noi == 0:
                        thoi_gian_mat_ket_noi = time.time()
                    elif time.time() - thoi_gian_mat_ket_noi > 5:
                        self.is_dangchay.set()
                        break
                else:
                    thoi_gian_mat_ket_noi = 0

            except Exception:
                pass

            time.sleep(0.5)

        if self.cuaso:
            self.cuaso.tatauto()

        os._exit(0)


class TroChoiManager:
    def __init__(self):
        self.managed_processes = {}
        self.lock = threading.Lock()
        self.is_running = True

        keyboard.add_hotkey("f12", self.spawn_worker)
        keyboard.add_hotkey("ctrl + alt + f12", self.stop_all)

        print("=" * 50)
        print("TOOL CHIEN QUOC (MANAGER)")
        print("Trang thai: Dang cho lenh...")
        print("1. Vao game -> Bam F12 de chay Auto (Chay ngam).")
        print("2. Ctrl + Alt + F12: Tat TOAN BO.")
        print("-" * 50)
        print("Dung tat cua so nay!")
        print("=" * 50)

    def stop_all(self):
        print("\nĐang dừng toàn bộ hệ thống...")
        self.is_running = False
        with self.lock:
            for hwnd, proc in self.managed_processes.items():
                try:
                    proc.kill()
                except:
                    pass
        phatam("Đã tắt tool")
        time.sleep(1)
        os._exit(0)

    def spawn_worker(self):
        hwnd = win32gui.GetForegroundWindow()
        tencuaso = win32gui.GetWindowText(hwnd)

        if not (tencuaso and ("Chien Quoc" in tencuaso or "Chiến Quốc" in tencuaso)):
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

            script_path = os.path.abspath(__file__)
            cmd = [sys.executable, script_path, "--child", str(hwnd)]

            try:
                proc = subprocess.Popen(cmd, creationflags = CREATE_NO_WINDOW)
                self.managed_processes[hwnd] = proc
            except Exception:
                phatam("Lỗi khởi động")

    def run(self):
        while self.is_running:
            time.sleep(1)


if __name__ == "__main__":
    if "--child" in sys.argv:
        try:
            idx = sys.argv.index("--child")
            target_hwnd = int(sys.argv[idx + 1])
            worker = TroChoiWorker(target_hwnd)
            worker.khoidong()
        except Exception:
            os._exit(1)
    else:
        mutex_name = "Global_Tool_ChienQuoc_Manager_Mutex"
        mutex = win32event.CreateMutex(None, True, mutex_name)

        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            phatam("Tool quản lý đang chạy rồi")
            time.sleep(2)
            sys.exit(0)

        manager = TroChoiManager()
        try:
            manager.run()
        except KeyboardInterrupt:
            pass