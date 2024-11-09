import locale
import os
import threading
import time

import keyboard
import win32gui

from cuaso import CuaSo
from tienich import phatam

def loop_cuaso(cuaso: CuaSo):
    cuaso.loop()

class TroChoi:
    def __init__(self):
        self.cuasos = {}
        self.is_dangchay = threading.Event()
        self.remove1 = keyboard.add_hotkey("f12", self.themcuasohientai)
        self.remove2 = keyboard.add_hotkey("ctrl + alt + f12", lambda: self.is_dangchay.set())
    def __del__(self):
        keyboard.remove_hotkey(self.remove1)
        keyboard.remove_hotkey(self.remove2)

    def themcuasohientai(self):
        idcuaso = win32gui.GetForegroundWindow()

        if idcuaso in self.cuasos:
            phatam("Cửa sổ đã tồn tại")
            return

        tencuaso = win32gui.GetWindowText(idcuaso)
        if tencuaso and tencuaso.startswith("Chien"):
            phatam("Khởi động thành công")
            cuaso = CuaSo(idcuaso)
            self.cuasos[idcuaso] = cuaso
            threading.Thread(target = loop_cuaso, args = [cuaso], daemon = False).start()
        else:
            phatam("Khởi động thất bại")

    def tatauto(self):
        for cuaso in self.cuasos.values():
            cuaso.tatauto()

    def loop(self):
        idcuasohethans = set()

        for idcuaso, cuaso in self.cuasos.items():
            if cuaso.main_stop.is_set():
                idcuasohethans.add(idcuaso)

        for idcuasohethan in idcuasohethans:
            self.cuasos.pop(idcuasohethan)

        time.sleep(1)

import pymem

if __name__ == "__main__":
    name = "trochoi.exe"

    is_datrung = False

    processes = pymem.process.list_processes()
    for process in processes:
        process_name = process.szExeFile.decode(locale.getpreferredencoding())
        if process_name == name:
            process_id = process.th32ProcessID
            if process_id != os.getpid():
                phatam("Khởi động thất bại. Phần mềm đã bật")
                is_datrung = True

    if not is_datrung:
        trochoi = TroChoi()
        while not trochoi.is_dangchay.is_set():
            trochoi.loop()

        trochoi.tatauto()
