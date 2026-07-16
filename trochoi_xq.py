import os
import time
import tkinter as tk
import traceback
from multiprocessing import Process, Manager, freeze_support

import keyboard
import win32gui

from cuaso_xq import CuaSo
from giaodienhienthi_xq import GiaoDienHienThi

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


def run_bot_process(hwnd, shared_data, command_dict):
    try:
        bot = CuaSo(hwnd, shared_data, command_dict)
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
        self.bot_processes = {}

    def _timcuasogame(self):
        ds_hwnd = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and "Chien Quoc" in title:
                    ds_hwnd.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return ds_hwnd

    def run(self):
        root = tk.Tk()
        gui = GiaoDienHienThi(root, self.shared_data, self.command_dict)

        import threading
        t_scan = threading.Thread(target = self.loop_scan, daemon = True)
        t_scan.start()

        t_hotkey = threading.Thread(target = self.loop_hotkey, daemon = True)
        t_hotkey.start()

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
                    p = Process(target = run_bot_process, args = (hwnd, self.shared_data, self.command_dict))
                    p.start()
                    self.bot_processes[hwnd] = p

            dead = [h for h, p in self.bot_processes.items() if not p.is_alive()]
            for h in dead:
                del self.bot_processes[h]
                if h in self.shared_data: del self.shared_data[h]
                if h in self.command_dict: del self.command_dict[h]

            time.sleep(2)

    def loop_hotkey(self):
        while True:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd in self.bot_processes:
                cmd = None
                if keyboard.is_pressed("ctrl+alt+shift+p"):
                    cmd = "battat_tudongdichuyendiemdanhxungquanh"
                elif keyboard.is_pressed("ctrl+alt+shift+c"):
                    cmd = "battat_chantangcapdo"
                elif keyboard.is_pressed("ctrl+alt+shift+k"):
                    cmd = "battat_tudongkhaikhoang"
                elif keyboard.is_pressed("ctrl+alt+shift+b"):
                    cmd = "thuchien_tudongbanrac"
                elif keyboard.is_pressed("ctrl+alt+c"):
                    cmd = "botoanbo_tenmuctieutancong"
                elif keyboard.is_pressed("ctrl+alt+x"):
                    cmd = "botoanbo_tenmuctieukhongtancong"
                elif keyboard.is_pressed("ctrl+alt+f"):
                    cmd = "battat_tudongtheosautruongnhom"
                elif keyboard.is_pressed("ctrl+alt+p"):
                    cmd = "botoanbo_diemdanhxungquanh"
                elif keyboard.is_pressed("ctrl+alt+t"):
                    cmd = "battat_tudongbattheosaunhom"
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
                elif keyboard.is_pressed("ctrl+alt+shift+g"):
                    cmd = "battat_tudonggomquai"
                elif keyboard.is_pressed("ctrl+alt+shift+h"):
                    cmd = "battat_tudongvebanrac"
                elif keyboard.is_pressed("ctrl+alt+shift+z"):
                    cmd = "battat_tudongdichientruong"
                elif keyboard.is_pressed("ctrl+alt+s"):
                    cmd = "battat_uutienbaothumaoson"
                elif keyboard.is_pressed("ctrl+alt+shift+r"):
                    cmd = "action_suado"
                elif keyboard.is_pressed("ctrl+alt+shift+n"):
                    cmd = "battat_chedobufftoanbang"
                elif keyboard.is_pressed("ctrl+alt+shift+i"):
                    cmd = "battat_tudongdaotangbaodo"

                if cmd:
                    self.command_dict[hwnd] = cmd
                    time.sleep(0.3)
            time.sleep(0.05)

    def stop_all(self):
        for p in self.bot_processes.values(): p.terminate()
        os._exit(0)


if __name__ == "__main__":
    freeze_support()
    TroChoiManager().run()