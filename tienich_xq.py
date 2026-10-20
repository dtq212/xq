import json
import math
import os
import pickle
import re
import sys
import threading
import random
import ctypes

import gtts
import unicodedata
import win32gui
import win32con
import time
import pywintypes


def taopatterntuaob(aob_string):
    pattern = b""
    for byte_str in aob_string.split():
        if byte_str == "?" or byte_str == "??":
            pattern += b"."
        else:
            b = bytes.fromhex(byte_str)
            if b in b".^$*+?{}[]\\|()":
                pattern += b"\\" + b
            else:
                pattern += b
    return pattern

def to_hex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))


def read_boolean(process, address):
    return process.read_bool(address)


def write_boolean(process, address, value):
    process.write_bool(address, value)


def read_int(process, address):
    return process.read_int(address)


def write_int(process, address, value):
    process.write_int(address, value)


def read_short_int(process, address, n_bytes = 1):
    return int.from_bytes(process.read_bytes(address, n_bytes), sys.byteorder)


def write_short_int(process, address, value, n_bytes = 1):
    process.write_bytes(address, value.to_bytes(n_bytes, sys.byteorder), n_bytes)


def read_bytes(process, address, n_bytes):
    return process.read_bytes(address, n_bytes)


def write_bytes(process, address, value, n_bytes):
    return process.write_bytes(address, value, n_bytes)


def read_string(process, address, max_length = 2048):
    try:
        initial_size = 256
        if initial_size > max_length: initial_size = max_length
        buffer = process.read_bytes(address, initial_size)
        null_index = buffer.find(b"\x00")
        if null_index != -1:
            raw_data = buffer[:null_index]
        else:
            current_offset = initial_size
            raw_data = buffer

            while len(raw_data) < max_length:
                try:
                    chunk = process.read_bytes(address + current_offset, 128)
                    if b"\x00" in chunk:
                        raw_data += chunk[:chunk.index(b"\x00")]
                        break
                    raw_data += chunk
                    current_offset += 128
                except:
                    break
        text = raw_data.decode("utf-8", errors = "ignore")
        return re.sub(r'\x1b[a-zA-Z0-9]', '', text).strip()
    except Exception:
        return ""


def write_string(process, address, value):
    return process.write_string(address, value)


def slugify(value, allow_unicode = False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def _phatam(noidung, is_block):
    try:
        print(f"phatam (thread): {noidung}")
        tenfile = slugify(noidung)

        duongdanthumucamthanh = os.path.join(os.getcwd(), "_internal", "amthanh")

        if not os.path.exists(duongdanthumucamthanh):
            os.makedirs(duongdanthumucamthanh, exist_ok = True)

        file_path = os.path.join(duongdanthumucamthanh, f"{tenfile}.mp3")

        if not os.path.exists(file_path):
            try:
                gtts.gTTS(noidung, lang = "vi").save(file_path)
            except Exception as e_save:
                print(f"Lỗi khi lưu file âm thanh: {e_save}")
                return
        try:
            alias = f"audio_{random.randint(10000, 99999)}"
            ctypes.windll.winmm.mciSendStringW(f'open "{file_path}" alias {alias}', None, 0, None)

            if is_block:
                ctypes.windll.winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
            else:
                ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, None)
        except Exception as e_play:
            print(f"Lỗi phát âm thanh: {e_play}")

    except Exception as err:
        print(f"Phát âm lỗi tổng quát: {err}")


def phatam(noidung, is_block = True):
    t = threading.Thread(target = _phatam, args = (noidung, is_block), daemon = True)
    t.start()


def _thumucthietlap():
    # Không dùng "." vì nó phụ thuộc thư mục đang đứng khi chạy lệnh (PyCharm và PowerShell khác nhau)
    if getattr(sys, "frozen", False):
        thumucgoc = os.path.dirname(sys.executable)
    else:
        thumucgoc = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "thietlap")


def duongdanlotrinhmau():
    return os.path.join(os.path.dirname(_thumucthietlap()), "lotrinh.json")


def tailotrinhmau():
    # Thư viện lộ trình mẫu: {"<id bản đồ>": [{"ten": "Vòng A", "diem": [[x, y], ...]}, ...]}
    try:
        with open(duongdanlotrinhmau(), "r", encoding = "utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as err:
        print(err)
        return {}


def luulotrinhmau(lotrinhmau):
    filepath = duongdanlotrinhmau()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(lotrinhmau, file, ensure_ascii = False, indent = 2)
        os.replace(filetam, filepath)
    except Exception as err:
        print(err)


def duongdanthietlap(tennhanvat):
    return os.path.join(_thumucthietlap(), str(slugify(tennhanvat)))


def luuthietlap(tennhanvat, thietlap):
    filepath = duongdanthietlap(tennhanvat)

    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        # Ghi ra file tạm rồi thay thế để không bị hỏng file nếu tắt tool giữa chừng (lưu mỗi giây)
        filetam = filepath + ".tmp"
        with open(filetam, "wb") as file:
            pickle.dump(thietlap, file)
        os.replace(filetam, filepath)

    except Exception as err:
        print(err)


def taithietlap(tennhanvat):
    filepath = duongdanthietlap(tennhanvat)

    try:
        if os.path.exists(filepath):
            with open(filepath, "rb") as file:
                return pickle.load(file)
    except Exception as err:
        print(err)


def tinhkhoangcach(x1, y1, x2, y2):
    return round(math.dist((x1, y1), (x2, y2), ))


TCVN3TAB = "µ¸¶·¹¨»¾¼½Æ©ÇÊÈÉË®ÌÐÎÏÑªÒÕÓÔÖ×ÝØÜÞßãáâä«åèæçé¬êíëìîïóñòô-õøö÷ùúýûüþ¡¢§£¤¥¦Ù"
TCVN3TAB = [ch for ch in TCVN3TAB]

UNICODETAB = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĂÂĐÊÔƠƯ "
UNICODETAB = [ch for ch in UNICODETAB]

r = re.compile("|".join(TCVN3TAB))
replaces_dict = dict(zip(TCVN3TAB, UNICODETAB))


def TCVN3_to_unicode(tcvn3str):
    return r.sub(lambda m: replaces_dict[m.group(0)], tcvn3str)


UNICODE_TO_TCVN3_MAP = dict(zip(UNICODETAB, TCVN3TAB))
if ' ' in UNICODE_TO_TCVN3_MAP:
    del UNICODE_TO_TCVN3_MAP[' ']


def Unicode_to_TCVN3(unicode_str):
    if not unicode_str:
        return b""

    result = bytearray()
    for char in unicode_str:
        if ord(char) < 128:
            result.append(ord(char))
            continue

        tcvn_char = UNICODE_TO_TCVN3_MAP.get(char)

        if tcvn_char:
            try:
                result.extend(tcvn_char.encode('latin-1'))
            except UnicodeEncodeError:
                result.extend(b'?')
        else:
            try:
                result.extend(char.encode('mbcs'))
            except:
                result.extend(b'?')

    return bytes(result)


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


class BackgroundInput:
    @staticmethod
    def _safe_post_message(hwnd, msg, wparam, lparam):
        try:
            win32gui.PostMessage(hwnd, msg, wparam, lparam)
        except pywintypes.error as e:
            if e.winerror == 1400:
                return
            raise e

    @staticmethod
    def click(hwnd, x, y, delay = 0.1):
        lparam = make_lparam(x, y)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
        time.sleep(delay)

    @staticmethod
    def right_click(hwnd, x, y, delay = 0.1):
        lparam = make_lparam(x, y)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_RBUTTONUP, 0, lparam)
        time.sleep(delay)

    @staticmethod
    def press_key(hwnd, key_code, delay = 0.1):
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYDOWN, key_code, 0)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYUP, key_code, 0)
        time.sleep(delay)

    @staticmethod
    def type_text(hwnd, text, delay = 0.05):
        for char in text:
            BackgroundInput._safe_post_message(hwnd, win32con.WM_CHAR, ord(char), 0)
            time.sleep(delay)

    @staticmethod
    def press_combo(hwnd, modifier, key, delay = 0.1):
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYDOWN, modifier, 0)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYDOWN, key, 0)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYUP, key, 0)
        time.sleep(0.05)
        BackgroundInput._safe_post_message(hwnd, win32con.WM_KEYUP, modifier, 0)
        time.sleep(delay)