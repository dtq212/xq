import os
import subprocess
import sys
import threading
import time
import signal
import hashlib

import keyboard
import win32api
import win32event
import win32gui
import win32process
import winerror

from cuaso import CuaSo
from moitruong import MoiTruong
from tienich import phatam, slugify
from hangso import NHANVATTODOITUDONGs, THONGTINTUDONGDANGNHAP_MAP, DUONGDAN_GAME

CREATE_NO_WINDOW = 0x08000000
VK_F12 = 0x7B

TEN_CARD_BLUETOOTH = "Bluetooth Network Connection"


def get_md5(text):
    return hashlib.md5(text.encode()).hexdigest().upper()


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
                    elif time.time() - thoi_gian_mat_nhan_vat > 60:
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
        self.last_check_login = 0

        print("=" * 50)
        print("TOOL CHIẾN QUỐC (AUTO MẠNG + AUTO LOGIN)")
        print("-" * 50)
        print("LOGIC MẠNG:")
        print("1. Có cửa sổ đang đăng nhập -> Ưu tiên Bluetooth.")
        print("2. Tất cả cửa sổ đã vào game -> Ưu tiên Wifi (Nhường mạng).")
        print("-" * 50)
        print("LOGIC LOGIN:")
        print(f"Giám sát {len(THONGTINTUDONGDANGNHAP_MAP)} tài khoản.")
        print("Nếu thiếu -> Tự mở game -> Tự đăng nhập.")
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
                phatam("Đã ưu tiên Bluetooth để đăng nhập")
                print(f"[Network] Bluetooth Metric = 1 (HIGH) -> Chế độ Đăng Nhập")
            else:
                phatam("Đã chuyển về Wifi")
                print(f"[Network] Bluetooth Metric = 100 (LOW) -> Chế độ Treo Game")
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

            try:
                mt = MoiTruong(hwnd)
                ten = mt.get_tendoituong()
                print(f"-> Phát hiện {ten} ({hwnd}) đã vào game -> Kích hoạt Auto!")
            except:
                print(f"-> Phát hiện cửa sổ {hwnd} -> Kích hoạt Auto!")

            script_path = os.path.abspath(__file__)
            cmd = [sys.executable, "-u", script_path, "--child", str(hwnd)]

            try:
                proc = subprocess.Popen(cmd, stdout = sys.stdout, stderr = sys.stderr)
                self.managed_processes[hwnd] = proc
            except Exception:
                pass

    def check_network_condition(self):
        tat_ca_cua_so = self._tim_cua_so_game()

        co_cua_so_chua_dang_nhap = False

        if not tat_ca_cua_so:
            self.thiet_lap_mang_bluetooth(100)
            return

        for hwnd in tat_ca_cua_so:
            try:
                mt = MoiTruong(hwnd)
                if not mt.get_is_nhanvattontai():
                    co_cua_so_chua_dang_nhap = True
                    break

                ten = mt.get_tendoituong()
                if not ten or len(ten) == 0:
                    co_cua_so_chua_dang_nhap = True
                    break
            except:
                co_cua_so_chua_dang_nhap = True
                break

        if co_cua_so_chua_dang_nhap:
            self.thiet_lap_mang_bluetooth(1)
        else:
            self.thiet_lap_mang_bluetooth(100)

    def check_and_restore_characters(self):
        if time.time() - self.last_check_login < 30.0:
            return

        self.last_check_login = time.time()

        online_chars = []
        tat_ca_cua_so = self._tim_cua_so_game()

        for hwnd in tat_ca_cua_so:
            try:
                mt = MoiTruong(hwnd)
                if mt.get_is_nhanvattontai():
                    ten = mt.get_tendoituong()
                    if ten: online_chars.append(ten)
            except:
                pass

        for ten_nv, config in THONGTINTUDONGDANGNHAP_MAP.items():
            if ten_nv not in online_chars:
                print(f"[MANAGER] Cảnh báo: {ten_nv} vắng mặt. Đang mở lại...")
                self.khoi_dong_va_dang_nhap(ten_nv, config)
                time.sleep(10)
                self.last_check_login = time.time()
                break

    def khoi_dong_va_dang_nhap(self, ten_can_login, config):
        try:
            game_dir = os.path.dirname(DUONGDAN_GAME)
            process = subprocess.Popen(DUONGDAN_GAME, cwd = game_dir)

            self.thiet_lap_mang_bluetooth(1)
            time.sleep(15)

            hwnd_target = 0

            def find_new_window(hwnd, ctx):
                nonlocal hwnd_target
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "Chien Quoc" in title or "Chiến Quốc" in title:
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            if pid == process.pid:
                                hwnd_target = hwnd
                        except:
                            pass

            win32gui.EnumWindows(find_new_window, None)

            if hwnd_target:
                print(f"[MANAGER] Đã tìm thấy cửa sổ mới (PID {process.pid}). Gửi lệnh Login...")
                mt = MoiTruong(hwnd_target)

                tk = config["tentaikhoan"]
                mk = config["matkhau"]
                vitri = config["vitrinhanvat"]
                mk_md5 = get_md5(mk)

                cmd = f"LOGIN {tk} {mk_md5} {vitri}"

                for _ in range(3):
                    mt.action_thucthicaulenh(cmd)
                    time.sleep(2)

                print(f"[MANAGER] Đã gửi lệnh Login cho {ten_can_login}.")
            else:
                print("[MANAGER] Không tìm thấy cửa sổ game vừa mở.")

        except Exception as e:
            print(f"[MANAGER] Lỗi khi mở game: {e}")

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

            self.check_and_restore_characters()

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