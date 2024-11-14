import math
import os
import pickle
import re
import sys

import gtts
import playsound
import unicodedata

from hangso import STRING_ENCODING

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


def read_string(process, address, sobytes = 32):
    return process.read_string(address, sobytes, encoding = STRING_ENCODING)


def write_string(process, address, sobytes = 32):
    return process.write_string(address, sobytes, encoding = STRING_ENCODING)



def slugify(value, allow_unicode = False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")

def phatam(noidung):
    tenfile = slugify(noidung)
    folder_amthanh_path = os.path.join(".", "_internal", "amthanh")
    if not os.path.exists(folder_amthanh_path):
        os.makedirs(folder_amthanh_path, exist_ok = True)

    file_path = os.path.join(folder_amthanh_path, "{}.mp3".format(tenfile))

    if not os.path.exists(file_path):
        gtts.gTTS(noidung, lang = "vi").save(file_path)
    try:
        playsound.playsound(file_path, False)
    except playsound.PlaysoundException as err:
        print("Phát âm lỗi: {}".format(err))

def luuthietlap(tennhanvat, thietlap):
    tenfile = slugify(tennhanvat)

    thumuc = os.path.join(".", "_internal", "thietlap")
    if not os.path.exists(thumuc):
        os.makedirs(thumuc)
    with open(os.path.join(thumuc, str(tenfile)), "wb") as file:
        pickle.dump(thietlap, file)

def taithietlap(tennhanvat):
    tenfile = slugify(tennhanvat)
    filepath = os.path.join(".", "_internal", "thietlap", str(tenfile))

    if os.path.exists(filepath):
        with open(filepath, "rb") as file:
            return pickle.load(file)

def tinhkhoangcach(x1, y1, x2, y2):
    return round(math.dist((x1, y1), (x2, y2), ))

if __name__ == "__main__":
    print(0. or 1)