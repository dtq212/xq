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
        self.is_dangloop = False
        self.soluongcuaso = 0
    def __del__(self):
        keyboard.remove_hotkey(self.remove1)
        keyboard.remove_hotkey(self.remove2)

    def themcuasohientai(self):
        if self.is_dangloop:
            return
        idcuaso = win32gui.GetForegroundWindow()

        if idcuaso in self.cuasos:
            phatam("Cửa sổ đã tồn tại")
            return

        tencuaso = win32gui.GetWindowText(idcuaso)
        if tencuaso and tencuaso.startswith("Chien Quoc"):
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
        self.is_dangloop = True

        idcuasohethans = set()
        idnguoichoihethans = set()

        for idcuaso, cuaso in self.cuasos.items():
            if cuaso.main_stop.is_set() or not cuaso.moitruong.get_is_cuasogametontai():
                idcuasohethans.add(idcuaso)
                idnguoichoihethans.add(cuaso.moitruong._idnguoichoi)
                cuaso.main_stop.set()

        for idcuasohethan in idcuasohethans:
            del self.cuasos[idcuasohethan]

        soluongcuaso = len(self.cuasos)
        if soluongcuaso < self.soluongcuaso:
            phatam("Game đã bị đóng")
            os.startfile("C:\\Users\\ACER\\Desktop\\ChienQuoc New\\ChienQuoc New\\xq.exe")
            print(idnguoichoihethans)
            if {3735, 3705, 3706} & idnguoichoihethans:
                os.startfile("C:\\Users\\ACER\\PycharmProjects\\xq\\wifi30.bat")
            else:
                os.startfile("C:\\Users\\ACER\\PycharmProjects\\xq\\wifi1.bat")

        self.is_dangloop = False
        self.soluongcuaso = soluongcuaso

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
