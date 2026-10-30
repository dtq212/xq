import os
import time
import tkinter as tk
import traceback
from multiprocessing import Process, Manager, freeze_support

import keyboard
import win32api
import win32gui
import win32job
# Thêm các thư viện cần thiết để xử lý tiến trình rác
import csv
import subprocess
import win32process

from amthanh_xq import khoitaocom, datamthanhtientrinhs
from cuaso_xq import CuaSo
from dangnhap_xq import TuDongDangNhap
from dieuphoi_xq import taicauhinhdieuphoi, KENH_LENH, KENH_DICHUYEN
from giaodienhienthi_xq import GiaoDienHienThi
from hangso_xq import IS_CHIBATAMTHANHCUASOUUTIEN, THOIGIANKIEMTRAAMTHANH
from lan_xq import DongBoLan, taicauhinhlan
from thongbao_xq import DieuKhienTelegram
from tienich_xq import laynhomtodoitudongs

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

def run_bot_process(hwnd, shared_data, command_dict, dieuphoi_khoa, dieuphoi_trangthai, dieuphoi_dangchos, dieuphoi_giukynangs, shared_data_lan = None):
    try:
        bot = CuaSo(hwnd, shared_data, command_dict, dieuphoi_khoa, dieuphoi_trangthai, dieuphoi_dangchos, dieuphoi_giukynangs, shared_data_lan)
        while not bot.main_stop.is_set():
            if not win32gui.IsWindow(hwnd):
                break
            time.sleep(1)
        bot.tatauto()
    except Exception as e:
        print(f"\n[CRASH TẠI PROCESS CON - HWND {hwnd}]:")
        traceback.print_exc()
        time.sleep(10)


class TroChoiManager:
    def __init__(self):
        self.manager = Manager()
        self.shared_data = self.manager.dict()
        self.command_dict = self.manager.dict()
        # Chia lượt gửi lệnh giữa các bot (xem dieuphoi_xq.py)
        self.dieuphoi_khoa = self.manager.Lock()
        self.dieuphoi_trangthai = self.manager.dict()
        self.dieuphoi_dangchos = self.manager.dict()
        # Giữ chỗ chiêu khống chế trên mục tiêu, để 2 bot không cùng gửi 1 hiệu ứng (xem GiuKyNangMucTieu)
        self.dieuphoi_giukynangs = self.manager.dict()
        # Cấu hình nhịp lệnh dùng chung mọi bot, giao diện sửa trực tiếp ở đây (bot đọc lại mỗi giây)
        self.dieuphoi_trangthai["cauhinh"] = taicauhinhdieuphoi()
        # Cửa sổ ở máy khác trong LAN (lan_xq, có _internal/lan.json mới bật): chỉ bot đọc, giao diện vẫn chỉ thấy máy này
        self.cauhinhlan = taicauhinhlan()
        self.shared_data_lan = self.manager.dict() if self.cauhinhlan else None
        self.bot_processes = {}

    def _timcuasogame(self):
        ds_hwnd = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and "Chien Quoc 2" in title:
                    ds_hwnd.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return ds_hwnd

    def run(self):
        # Khai báo hỗ trợ DPI cao trước khi tạo cửa sổ để Windows không phóng to kiểu ảnh làm nhòe chữ.
        # Chỉ đặt ở tiến trình giao diện chính, không ảnh hưởng các tiến trình bot.
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        # Tự động đăng nhập lại nhân vật vắng mặt (thay cho các kịch bản tudongdangnhap*.py chạy riêng)
        self.dangnhap = TuDongDangNhap()
        self.dangnhap.batdau()
        # Lệnh từ Telegram và báo cáo định kỳ (thongbao_xq), 1 luồng cho cả máy
        DieuKhienTelegram(self.shared_data, self.command_dict).batdau()
        if self.cauhinhlan:
            DongBoLan(self.cauhinhlan, self.shared_data, self.shared_data_lan).batdau()

        root = tk.Tk()
        gui = GiaoDienHienThi(root, self.shared_data, self.command_dict, self.dieuphoi_trangthai, self.dangnhap)
        # Phím tắt xoay vòng chiêu là cấu hình chung (không gửi cho 1 bot): luồng phím tắt nhờ luồng giao diện bật / tắt
        self.root, self.gui = root, gui

        root.protocol("WM_DELETE_WINDOW", self.stop_all)

        import threading
        t_scan = threading.Thread(target = self.loop_scan, daemon = True)
        t_scan.start()

        t_hotkey = threading.Thread(target = self.loop_hotkey, daemon = True)
        t_hotkey.start()

        if IS_CHIBATAMTHANHCUASOUUTIEN:
            t_amthanh = threading.Thread(target = self.loop_amthanh, daemon = True)
            t_amthanh.start()

        print("--- ĐANG CHẠY MANAGER CHIẾN QUỐC ---")
        try:
            root.mainloop()
        except KeyboardInterrupt:
            pass
        self.stop_all()

    def loop_scan(self):
        while True:
            game_hwnds = self._timcuasogame()
            for hwnd in game_hwnds:
                if hwnd not in self.bot_processes:
                    p = Process(target = run_bot_process, args = (hwnd, self.shared_data, self.command_dict, self.dieuphoi_khoa, self.dieuphoi_trangthai, self.dieuphoi_dangchos, self.dieuphoi_giukynangs, self.shared_data_lan))
                    p.daemon = True
                    p.start()
                    self.bot_processes[hwnd] = p

            dead = [h for h, p in self.bot_processes.items() if not p.is_alive()]
            for h in dead:
                del self.bot_processes[h]
                if h in self.shared_data: del self.shared_data[h]
                if h in self.command_dict: del self.command_dict[h]
                for kenh in (KENH_LENH, KENH_DICHUYEN):
                    self.dieuphoi_dangchos.pop((kenh, h), None)

            time.sleep(2)

    def _pidcuasogames(self):
        pids = {}
        for hwnd in list(self.bot_processes):
            try:
                pids[hwnd] = win32process.GetWindowThreadProcessId(hwnd)[1]
            except Exception:
                pass
        return pids

    def _chonhwndphatamthanh(self, hwnds):
        # Cửa sổ có nhân vật đứng trước nhất trong danh sách tổ đội tự động; chưa ai có trong danh sách (hoặc chưa đọc được ID)
        # thì lấy cửa sổ mở sớm nhất (hwnd nhỏ nhất) để khỏi đổi qua lại
        thutus = {id_: (i, j) for i, nhom in enumerate(laynhomtodoitudongs()) for j, id_ in enumerate(nhom)}

        def khoa(hwnd):
            info = self.shared_data.get(hwnd)
            idnguoichoi = info.get("idnguoichoi") if isinstance(info, dict) else None
            return thutus.get(idnguoichoi, (len(thutus), 0)), hwnd

        return min(hwnds, key = khoa) if hwnds else None

    def loop_amthanh(self):
        try:
            khoitaocom()
        except Exception as err:
            print(f"Lỗi khởi tạo âm thanh: {err}")
            return
        while True:
            try:
                pids = self._pidcuasogames()
                hwndphat = self._chonhwndphatamthanh(list(pids))
                if pids:
                    datamthanhtientrinhs({pid: hwnd != hwndphat for hwnd, pid in pids.items()})
            except Exception as err:
                print(f"Lỗi chỉnh âm thanh: {err}")
            time.sleep(THOIGIANKIEMTRAAMTHANH)

    def _batlaiamthanh(self):
        # Windows nhớ trạng thái tắt tiếng của client: thoát tool thì bật lại hết, lần sau mở game riêng vẫn có tiếng
        if not IS_CHIBATAMTHANHCUASOUUTIEN:
            return
        try:
            khoitaocom()
            pids = self._pidcuasogames()
            if pids:
                datamthanhtientrinhs({pid: False for pid in pids.values()})
        except Exception as err:
            print(f"Lỗi bật lại âm thanh: {err}")

    def loop_hotkey(self):
        while True:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd in self.bot_processes:
                cmd = None
                if keyboard.is_pressed("ctrl+r"):
                    cmd = "action_lammoitrangthai"
                elif keyboard.is_pressed("ctrl+alt+shift+p"):
                    cmd = "battat_tudongdichuyendiemdanhxungquanh"
                elif keyboard.is_pressed("ctrl+alt+shift+c"):
                    cmd = "battat_chantangcapdo"
                elif keyboard.is_pressed("ctrl+alt+shift+k"):
                    cmd = "battat_tudongkhaikhoang"
                elif keyboard.is_pressed("ctrl+alt+shift+b"):
                    cmd = "thuchien_tudongbanrac"
                elif keyboard.is_pressed("ctrl+alt+shift+f"):
                    self.root.after(0, self.gui.battat_xoayvongchieu)
                    time.sleep(0.3)
                elif keyboard.is_pressed("ctrl+alt+shift+g"):
                    cmd = "battat_tudonggomquai"
                elif keyboard.is_pressed("ctrl+alt+shift+h"):
                    cmd = "battat_tudongvebanrac"
                elif keyboard.is_pressed("ctrl+alt+shift+z"):
                    cmd = "battat_tudongdichientruong"
                elif keyboard.is_pressed("ctrl+alt+shift+r"):
                    cmd = "action_suavatpham"
                elif keyboard.is_pressed("ctrl+alt+shift+n"):
                    cmd = "battat_chedobufftoanbang"
                elif keyboard.is_pressed("ctrl+alt+shift+i"):
                    cmd = "battat_tudongdaotangbaodo"
                elif keyboard.is_pressed("ctrl+alt+shift+y"):
                    cmd = "action_muaauto"
                elif keyboard.is_pressed("ctrl+alt+c"):
                    cmd = "botoanbo_tenmuctieutancong"
                elif keyboard.is_pressed("ctrl+alt+x"):
                    cmd = "botoanbo_tenmuctieukhongtancong"
                elif keyboard.is_pressed("ctrl+alt+t"):
                    cmd = "todoimotlan"
                elif keyboard.is_pressed("ctrl+alt+f"):
                    cmd = "battat_tudongtheosau"
                elif keyboard.is_pressed("ctrl+alt+p"):
                    cmd = "botoanbo_diemdanhxungquanh"
                elif keyboard.is_pressed("ctrl+alt+d"):
                    cmd = "battat_thucsondao"
                elif keyboard.is_pressed("ctrl+f"):
                    cmd = "battat_tudongsudungkynang"
                elif keyboard.is_pressed("ctrl+c"):
                    cmd = "them_tenmuctieutancong"
                elif keyboard.is_pressed("ctrl+x"):
                    cmd = "them_tenmuctieukhongtancong"
                elif keyboard.is_pressed("ctrl+d"):
                    cmd = "thietlap_chidanhnguoichoi"
                elif keyboard.is_pressed("ctrl+a"):
                    cmd = "bo_thietlap_chidanhnguoichoi"
                elif keyboard.is_pressed("ctrl+e"):
                    cmd = "bat_pk"
                elif keyboard.is_pressed("ctrl+q"):
                    cmd = "tat_pk"
                elif keyboard.is_pressed("ctrl+p"):
                    cmd = "them_diemdanhxungquanh"
                elif keyboard.is_pressed("ctrl+b"):
                    cmd = "them_diemdanhxungquanh"
                elif keyboard.is_pressed("ctrl+y"):
                    cmd = "action_test"
                elif keyboard.is_pressed("ctrl+alt+s"):
                    cmd = "battat_uutienbaothukynangtrieuhoi"
                if cmd:
                    self.command_dict[hwnd] = cmd
                    time.sleep(0.3)
            time.sleep(0.05)

    def stop_all(self):
        print("\nĐang dọn dẹp và thoát...")
        self._batlaiamthanh()
        for p in self.bot_processes.values():
            try:
                p.terminate()
            except Exception:
                pass
        os._exit(0)


def _gantientrinhvaojob():
    # Tiến trình chính bị tắt ngang (Stop trong PyCharm, đóng console, crash) thì không kịp dọn: tiến trình Manager và tiến trình bot
    # từng cửa sổ (multiprocessing) sống mãi (đo 2026-10-29: 209 tiến trình sót từ 5 ngày, ~3,2 GB RAM). Gắn tiến trình chính vào Job
    # "đóng là kill hết": tiến trình con tạo sau đó cũng vào Job, tiến trình chính chết thì Windows đóng Job, kill cả bọn.
    # Cho phép tách khỏi Job để game mở từ dangnhap_xq.mogame không bị tắt theo. Giữ handle tới khi thoát (đóng handle = kill)
    try:
        job = win32job.CreateJobObject(None, "")
        thongtin = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
        thongtin["BasicLimitInformation"]["LimitFlags"] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | win32job.JOB_OBJECT_LIMIT_BREAKAWAY_OK
        win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, thongtin)
        win32job.AssignProcessToJobObject(job, win32api.GetCurrentProcess())
        return job
    except Exception as err:
        print(f"Không gắn được Job tự dọn tiến trình con: {err}")
        return None


if __name__ == "__main__":
    freeze_support()
    jobdondep = _gantientrinhvaojob()
    manager = TroChoiManager()
    manager.run()