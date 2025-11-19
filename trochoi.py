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
from moitruong import MoiTruong
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

    def khoidong(self):
        if not win32gui.IsWindow(self.target_hwnd):
            return

        self.cuaso = CuaSo(self.target_hwnd)

        if not self.kiemtranhanvathople():
            return

        phatam("Đã kết nối nhân vật")

        threading.Thread(target = loop_cuaso, args = [self.cuaso], daemon = True).start()
        self.loop_quanly()

    def kiemtranhanvathople(self):
        try:
            if not self.cuaso.moitruong.get_is_nhanvattontai():
                return False

            ten = self.cuaso.moitruong.get_tendoituong()
            if not ten or len(ten) == 0:
                return False

            return True
        except:
            return False

    def loop_quanly(self):
        thoi_gian_mat_nhan_vat = 0

        while not self.is_dangchay.is_set():
            try:
                if self.cuaso.main_stop.is_set() or not win32gui.IsWindow(self.target_hwnd):
                    self.is_dangchay.set()
                    break

                if win32api.GetAsyncKeyState(0x13) & 0x8000:
                    self.is_dangchay.set()
                    break

                if not self.kiemtranhanvathople():
                    if thoi_gian_mat_nhan_vat == 0:
                        thoi_gian_mat_nhan_vat = time.time()
                    elif time.time() - thoi_gian_mat_nhan_vat > 2:
                        self.is_dangchay.set()
                        break
                else:
                    thoi_gian_mat_nhan_vat = 0

            except Exception:
                self.is_dangchay.set()
                break

            time.sleep(0.5)

        if self.cuaso:
            self.cuaso.tatauto()

        os._exit(0)


class TroChoiManager:
    def __init__(self):
        self.managed_processes = {}
        self.lock = threading.Lock()
        self.is_running = True

        keyboard.add_hotkey("ctrl + alt + f12", self.dungtatca)

        print("=" * 50)
        print("TOOL CHIẾN QUỐC (SMART DETECT - NO LAG)")
        print("Trạng thái: Đang soi cửa sổ game...")
        print("1. Tự chạy khi đăng nhập.")
        print("2. Tự tắt khi thoát game.")
        print("3. Ctrl + Alt + F12: Tắt TOÀN BỘ.")
        print("-" * 50)
        print("Đừng tắt cửa sổ này!")
        print("=" * 50)

    def dungtatca(self):
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

    def timcuasogame(self):
        ds_hwnd = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ("Chien Quoc" in title or "Chiến Quốc" in title):
                    ds_hwnd.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return ds_hwnd

    def kiemtradudieukienmanager(self, hwnd):
        try:
            mt = MoiTruong(hwnd)
            if not mt.get_is_nhanvattontai():
                return False
            ten = mt.get_tendoituong()
            if not ten or len(ten) == 0:
                return False
            return True
        except:
            return False

    def mothemtientrinhcuasomoi(self, hwnd):
        with self.lock:
            if hwnd in self.managed_processes:
                return

            print(f"-> Phát hiện cửa sổ {hwnd} hợp lệ -> Kích hoạt Auto!")

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

            game_hwnds = self.timcuasogame()

            for hwnd in game_hwnds:
                if hwnd not in self.managed_processes:
                    if self.kiemtradudieukienmanager(hwnd):
                        self.mothemtientrinhcuasomoi(hwnd)

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