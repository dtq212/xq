import os
import subprocess
import sys
import threading
import time
import signal

import keyboard
import win32api
import win32event
import win32gui
import winerror

from cuaso import CuaSo
from moitruong import MoiTruong
from tienich import phatam
from hangso import NHANVATTODOITUDONGs

CREATE_NO_WINDOW = 0x08000000
VK_F12 = 0x7B

TEN_CARD_BLUETOOTH = "Bluetooth Network Connection"


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

        if not self.kiem_tra_nhan_vat_hop_le():
            return

        phatam("Đã kết nối nhân vật")

        threading.Thread(target = loop_cuaso, args = [self.cuaso], daemon = True).start()
        self.loop_quanly()

    def kiem_tra_nhan_vat_hop_le(self):
        try:
            if not self.cuaso.moitruong.get_is_nhanvattontai(): return False
            ten = self.cuaso.moitruong.get_tendoituong()
            if not ten or len(ten) == 0: return False
            return True
        except:
            return False

    def loop_quanly(self):
        thoi_gian_mat_nhan_vat = 0

        while not self.is_dangchay.is_set():
            try:
                if not win32gui.IsWindow(self.target_hwnd):
                    os.kill(os.getpid(), signal.SIGTERM)
                    break

                if self.cuaso.main_stop.is_set():
                    self.is_dangchay.set()
                    break

                if win32api.GetAsyncKeyState(VK_F12) & 0x8000:
                    self.is_dangchay.set()
                    break

                if not self.kiem_tra_nhan_vat_hop_le():
                    if thoi_gian_mat_nhan_vat == 0:
                        thoi_gian_mat_nhan_vat = time.time()
                    elif time.time() - thoi_gian_mat_nhan_vat > 2:
                        os.kill(os.getpid(), signal.SIGTERM)
                        break
                else:
                    thoi_gian_mat_nhan_vat = 0

            except Exception:
                os.kill(os.getpid(), signal.SIGTERM)
                break

            time.sleep(0.5)

        if self.cuaso:
            try:
                self.cuaso.main_stop.set()
                if hasattr(self.cuaso, 'systray'):
                    self.cuaso.systray.shutdown()
            except:
                pass

        os._exit(0)


class TroChoiManager:
    def __init__(self):
        self.managed_processes = {}
        self.lock = threading.Lock()
        self.is_running = True
        self.current_metric = None

        print("=" * 50)
        print("TOOL CHIẾN QUỐC (AUTO BLUETOOTH SWITCHER)")
        print(f"Đại Ca (Dùng Bluetooth): {NHANVATTODOITUDONGs[0] if NHANVATTODOITUDONGs else 'Chưa cấu hình'}")
        print("1. Chưa thấy Đại Ca -> Ưu tiên Bluetooth (Để log Đại Ca).")
        print("2. Thấy Đại Ca -> Giảm ưu tiên Bluetooth (Để log Clone bằng Wifi).")
        print("3. Ctrl+Alt+1: Ép dùng Bluetooth.")
        print("4. Ctrl+Alt+2: Ép dùng Wifi.")
        print("-" * 50)
        print("Nhấn phím F12 để dừng toàn bộ!")
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
        time.sleep(1)
        os._exit(0)

    def thiet_lap_mang_bluetooth(self, metric):
        if self.current_metric == metric:
            return

        try:
            cmd = f'powershell -Command "Get-NetAdapter \'{TEN_CARD_BLUETOOTH}\' | Set-NetIPInterface -InterfaceMetric {metric}"'

            subprocess.run(cmd, shell = True, creationflags = CREATE_NO_WINDOW)

            self.current_metric = metric

            if metric == 1:
                phatam("Đã ưu tiên Bluetooth")
                print(f"[Network] Bluetooth Metric = 1 (HIGH) -> Chế độ Đại Ca")
            else:
                phatam("Đã ưu tiên Wifi")
                print(f"[Network] Bluetooth Metric = 100 (LOW) -> Chế độ Clone")
        except Exception as e:
            print(f"Lỗi chỉnh mạng: {e}")

    def _tim_cua_so_game(self):
        ds_hwnd = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ("Chien Quoc" in title or "Chiến Quốc" in title):
                    ds_hwnd.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return ds_hwnd

    def kiem_tra_du_dieu_kien_manager(self, hwnd):
        try:
            mt = MoiTruong(hwnd)
            if not mt.get_is_nhanvattontai(): return False
            ten = mt.get_tendoituong()
            if not ten or len(ten) == 0: return False
            return True
        except:
            return False

    def spawn_worker_for_hwnd(self, hwnd):
        with self.lock:
            if hwnd in self.managed_processes:
                return

            print(f"-> Phát hiện cửa sổ {hwnd} hợp lệ -> Kích hoạt Auto!")

            script_path = os.path.abspath(__file__)
            cmd = [sys.executable, "-u", script_path, "--child", str(hwnd)]

            try:
                proc = subprocess.Popen(cmd, stdout = sys.stdout, stderr = sys.stderr)
                self.managed_processes[hwnd] = proc
            except Exception:
                pass

    def check_network_condition(self):
        if not NHANVATTODOITUDONGs:
            return

        id_dai_ca = NHANVATTODOITUDONGs[0]
        is_dai_ca_online = False

        with self.lock:
            active_hwnds = list(self.managed_processes.keys())

        for hwnd in active_hwnds:
            try:
                mt = MoiTruong(hwnd)
                if mt.get_is_nhanvattontai():
                    if mt.get_idnguoichoi() == id_dai_ca:
                        is_dai_ca_online = True
                        break
            except:
                pass

        if is_dai_ca_online:
            self.thiet_lap_mang_bluetooth(100)
        else:
            self.thiet_lap_mang_bluetooth(1)

    def run(self):
        time.sleep(1)

        while self.is_running:
            if win32api.GetAsyncKeyState(VK_F12) & 0x8000:
                self.stop_all()
                break

            if keyboard.is_pressed("ctrl+alt+1"):
                self.thiet_lap_mang_bluetooth(1)
                time.sleep(0.5)
            elif keyboard.is_pressed("ctrl+alt+2"):
                self.thiet_lap_mang_bluetooth(100)
                time.sleep(0.5)

            with self.lock:
                dead_hwnds = []
                for h, p in self.managed_processes.items():
                    if p.poll() is not None:
                        dead_hwnds.append(h)

                for h in dead_hwnds:
                    del self.managed_processes[h]

            game_hwnds = self._tim_cua_so_game()
            for hwnd in game_hwnds:
                if hwnd not in self.managed_processes:
                    if self.kiem_tra_du_dieu_kien_manager(hwnd):
                        self.spawn_worker_for_hwnd(hwnd)

            self.check_network_condition()

            time.sleep(0.5)


if __name__ == "__main__":
    if "--child" in sys.argv:
        try:
            idx = sys.argv.index("--child")
            target_hwnd = int(sys.argv[idx + 1])
            worker = TroChoiWorker(target_hwnd)
            worker.khoidong()
        except Exception:
            os.kill(os.getpid(), signal.SIGTERM)
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