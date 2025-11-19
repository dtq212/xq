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

        while not self.is_dangchay.is_set():
            if not win32gui.IsWindow(self.target_hwnd):
                return

            if self.cuaso.moitruong.get_is_nhanvattontai():
                phatam("Đã kết nối nhân vật")
                break

            time.sleep(1)

        threading.Thread(target = loop_cuaso, args = [self.cuaso], daemon = True).start()
        self.loop_quanly()

    def loop_quanly(self):
        thoigianmatketnoi = 0

        while not self.is_dangchay.is_set():
            try:
                if self.cuaso.main_stop.is_set() or not self.cuaso.moitruong.get_is_cuasogametontai():
                    self.is_dangchay.set()
                    break

                if win32api.GetAsyncKeyState(0x13) & 0x8000:
                    self.is_dangchay.set()
                    break

                if self.cuaso.moitruong.get_is_dangmatketnoi():
                    if thoigianmatketnoi == 0:
                        thoigianmatketnoi = time.time()
                    elif time.time() - thoigianmatketnoi > 2.5:
                        self.is_dangchay.set()
                        break
                else:
                    thoigianmatketnoi = 0
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

        keyboard.add_hotkey("ctrl + alt + f12", self.stop_all)

        print("=" * 50)
        print("TOOL CHIEN QUOC (AUTO-DETECT MANAGER)")
        print("Trang thai: Dang quet game va cho dang nhap...")
        print("1. Ban cu mo game thoai mai.")
        print("2. Khi nao DANG NHAP xong, Auto se tu dong kich hoat.")
        print("3. Ctrl + Alt + F12: Tat TOAN BO.")
        print("-" * 50)
        print("Dung tat cua so nay!")
        print("=" * 50)

    def stop_all(self):
        print("\nDang dung toan bo he thong...")
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

    def _tim_cua_so_game(self):
        ds_hwnd = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ("Chien Quoc" in title or "Chiến Quốc" in title):
                    ds_hwnd.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return ds_hwnd

    def spawn_worker_for_hwnd(self, hwnd):
        with self.lock:
            if hwnd in self.managed_processes:
                return

            print(f"-> Phat hien cua so {hwnd}, dang gan Auto (Che do cho)...")

            script_path = os.path.abspath(__file__)
            cmd = [sys.executable, script_path, "--child", str(hwnd)]

            try:
                proc = subprocess.Popen(cmd, creationflags = CREATE_NO_WINDOW)
                self.managed_processes[hwnd] = proc
            except Exception:
                pass

    def run(self):
        while self.is_running:
            with self.lock:
                dead_hwnds = [h for h, p in self.managed_processes.items() if p.poll() is not None]
                for h in dead_hwnds:
                    del self.managed_processes[h]

            game_hwnds = self._tim_cua_so_game()

            for hwnd in game_hwnds:
                if hwnd not in self.managed_processes:
                    self.spawn_worker_for_hwnd(hwnd)
                    time.sleep(1)

            time.sleep(2)


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