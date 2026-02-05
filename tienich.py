import math
import os
import pickle
import re
import sys
import threading

import gtts
import pygame
import unicodedata

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

        file_path = os.path.join(duongdanthumucamthanh, "{}.mp3".format(tenfile))

        if not os.path.exists(file_path):
            try:
                gtts.gTTS(noidung, lang = "vi").save(file_path)
            except Exception as e_save:
                print(f"Lỗi khi lưu file âm thanh: {e_save}")
                return
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            if is_block:
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
        except Exception as e_play:
            print(f"Lỗi phát âm thanh: {e_play}")

    except Exception as err:
        print("Phát âm lỗi tổng quát: {}".format(err))

def phatam(noidung, is_block = True):
    t = threading.Thread(target = _phatam, args = (noidung, is_block), daemon = True)
    t.start()

def luuthietlap(tennhanvat, thietlap):
    tenfile = slugify(tennhanvat)

    try:
        thumuc = os.path.join(".", "_internal", "thietlap")
        if not os.path.exists(thumuc):
            os.makedirs(thumuc)
        with open(os.path.join(thumuc, str(tenfile)), "wb") as file:
            pickle.dump(thietlap, file)

    except Exception as err:
        print(err)


def taithietlap(tennhanvat):
    tenfile = slugify(tennhanvat)
    filepath = os.path.join(".", "_internal", "thietlap", str(tenfile))

    try:
        if os.path.exists(filepath):
            with open(filepath, "rb") as file:
                return pickle.load(file)
    except Exception as err:
        print(err)


def tinhkhoangcach(x1, y1, x2, y2):
    return round(math.dist((x1, y1), (x2, y2), ))


TCVN3TAB = "µ¸¶·¹¨»¾¼½Æ©ÇÊÈÉË®ÌÐÎÏÑªÒÕÓÔÖ×ÝØÜÞßãáâä«åèæçé¬êíëìîïóñòô-õøö÷ùúýûüþ¡¢§£¤¥¦Ù"  # NOQA
TCVN3TAB = [ch for ch in TCVN3TAB]

UNICODETAB = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĂÂĐÊÔƠƯ "  # NOQA
UNICODETAB = [ch for ch in UNICODETAB]

r = re.compile("|".join(TCVN3TAB))
replaces_dict = dict(zip(TCVN3TAB, UNICODETAB))


def TCVN3_to_unicode(tcvn3str):
    return r.sub(lambda m: replaces_dict[m.group(0)], tcvn3str)


if __name__ == "__main__":
    print(0. or 1)
