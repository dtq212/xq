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

# Tiêu đề cửa sổ game các bản client bot chạy được. Cùng 1 mã xq.exe: Niết Bàn là bản gốc, Aegis = bản gốc + lớp vá .v10fix
# (107/107 chữ ký diachi_xq ra cùng giá trị, cấu trúc .data giống hệt) nên không cần địa chỉ riêng theo bản
TIEUDECUASOGAMEs = ("Chien Quoc 2D", "Chien Quoc Niet Ban")


def is_tieudecuasogame(title):
    return bool(title) and any(tieude in title for tieude in TIEUDECUASOGAMEs)


class _PROCESS_POWER_THROTTLING_STATE(ctypes.Structure):
    _fields_ = [("Version", ctypes.c_ulong), ("ControlMask", ctypes.c_ulong), ("StateMask", ctypes.c_ulong)]


def toiuuhieunangtientrinh(handle = None):
    # Máy nặng / gần hết RAM thì nhân vật lúc nhanh lúc chậm: Windows 11 hạ xung tiến trình nền (EcoQoS), bỏ qua độ phân giải
    # timer khi cửa sổ bị che / thu nhỏ, và sleep mặc định tròn lên tick 15.6ms. handle None = tiến trình bot này (thêm timeBeginPeriod(1),
    # áp riêng từng tiến trình từ Win10 2004); có handle = tiến trình game (cần quyền PROCESS_SET_INFORMATION)
    kernel32 = ctypes.windll.kernel32
    if handle is None:
        handle = kernel32.GetCurrentProcess()
        try:
            ctypes.windll.winmm.timeBeginPeriod(1)
        except Exception:
            pass
    try:
        # ProcessPowerThrottling = 4; tắt EXECUTION_SPEED (0x1) và IGNORE_TIMER_RESOLUTION (0x4): StateMask 0 = luôn chạy hết tốc độ
        trangthai = _PROCESS_POWER_THROTTLING_STATE(1, 0x1 | 0x4, 0)
        kernel32.SetProcessInformation(ctypes.c_void_p(handle), 4, ctypes.byref(trangthai), ctypes.sizeof(trangthai))
    except Exception:
        pass
    try:
        kernel32.SetPriorityClass(ctypes.c_void_p(handle), 0x8000)  # ABOVE_NORMAL_PRIORITY_CLASS
    except Exception:
        pass


def laytylesudungram():
    # Phần trăm RAM đang dùng của cả máy (GlobalMemoryStatusEx.dwMemoryLoad)
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    trangthai = MEMORYSTATUSEX()
    trangthai.dwLength = ctypes.sizeof(trangthai)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(trangthai)):
        return None
    return trangthai.dwMemoryLoad


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


def read_chuoi(process, address, max_length):
    # Chuỗi kết thúc bằng 0 (bytes, chưa decode), đọc từng khúc không vượt ranh giới trang 4KB: chuỗi nằm sát cuối vùng nhớ thì đọc
    # liền max_length byte lỗi 299 (trang sau chưa cấp phát), dù chuỗi đã kết thúc trước đó
    raw_data = b""
    while len(raw_data) < max_length:
        diachi = address + len(raw_data)
        chunk = process.read_bytes(diachi, min(max_length - len(raw_data), 0x1000 - diachi % 0x1000))
        if b"\0" in chunk:
            return raw_data + chunk[:chunk.index(b"\0")]
        raw_data += chunk
    return raw_data


def write_bytes(process, address, value, n_bytes):
    return process.write_bytes(address, value, n_bytes)


# Bot nối thông tin ước lượng vào đuôi tên mục tiêu đang chọn trong client (danhhieumuctieu_xq): " <ESC>Y| KH ...". read_string bỏ mã
# màu nên còn " | ..."; MoiTruong._get_tenthucte cắt từ DAUNOITENMUCTIEU để lọc / so tên vẫn đúng tên gốc
DAUNOITENMUCTIEU = " |"
DAUNOITENMUCTIEU_BYTES = b" Y| "


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


def khoangcachtamdanh(a, b):
    # Khoảng cách máy chủ dùng để xét tầm chiêu giữa hai toạ độ ô: max(|dx|, |dy|) (vùng tầm là hình vuông, xem MoiTruong.get_khoangcachtamdanh)
    return float(max(abs(a[0] - b[0]), abs(a[1] - b[1])))


def donbangthoidiem(bang, giulai, kichthuoctoida = 256):
    # Bảng {khoá: thời điểm}: quá kichthuoctoida dòng thì bỏ các dòng cũ hơn giulai giây (chỉ ghi thêm mà không xoá thì phình mãi)
    if len(bang) <= kichthuoctoida:
        return bang
    thoidiemhientai = time.time()
    return {k: v for k, v in list(bang.items()) if thoidiemhientai - v < giulai}


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


# Cảnh báo gần đây của tiến trình bot này (mỗi cửa sổ 1 tiến trình): [(thời điểm, nội dung)], cuaso_xq đưa lên shared_data
# "_canhbaos", giao diện gộp mọi nhân vật ở tab Cảnh báo
CANHBAOGANDAYs = []
SOCANHBAOGIULAI = 30


def canhbao(moitruong, noidung, is_block = True):
    # Phát âm cảnh báo của 1 nhân vật: đọc ID người chơi ở đầu câu (nhiều nhân vật cùng máy biết ai bị) và ghi vào danh sách cảnh báo
    try:
        idnguoichoi = moitruong.get_idnguoichoi()
    except Exception:
        idnguoichoi = 0
    CANHBAOGANDAYs.append((time.time(), noidung))
    del CANHBAOGANDAYs[:-SOCANHBAOGIULAI]
    phatam(f"ID {idnguoichoi}. {noidung}" if idnguoichoi else noidung, is_block)


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


def thaythefile(filetam, filepath, solanthu = 5):
    # os.replace trên Windows bị từ chối (WinError 5 / 32) nếu đúng lúc đó chương trình khác đang mở file đích (diệt virus, Windows Search,
    # PyCharm, git, cửa sổ khác đang đọc...): chờ chút rồi thử lại, hết lượt thì báo lỗi như cũ (file đích cũ vẫn nguyên)
    for lanthu in range(solanthu):
        try:
            os.replace(filetam, filepath)
            return
        except PermissionError:
            if lanthu == solanthu - 1:
                raise
            time.sleep(0.05)


def luulotrinhmau(lotrinhmau):
    filepath = duongdanlotrinhmau()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(lotrinhmau, file, ensure_ascii = False, indent = 2)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def duongdanvatcanhoc():
    return os.path.join(os.path.dirname(_thumucthietlap()), "vatcanhoc.json")


# Ô máy chủ không cho đi mà lưới vật cản của client ghi là đi được (rào chắn cố ý làm kẹt ở Chu Quốc), bot tự học khi đi mãi bị kéo về
# (moitruong.action_dikhongcatgoc): {"<id bản đồ>": [[x, y], ...]}. Dùng chung mọi cửa sổ (mỗi cửa sổ 1 tiến trình): đọc lại khi file đổi
_vatcanhoc_cache = {"dulieu": {}, "thoidiemsua": None, "thoidiemkiemtra": 0.}


def taivatcanhoc(idbando):
    # -> set {(x, y)} ô học được là vật cản của bản đồ idbando
    nho = _vatcanhoc_cache
    if time.time() - nho["thoidiemkiemtra"] > 1.:
        nho["thoidiemkiemtra"] = time.time()
        try:
            thoidiemsua = os.path.getmtime(duongdanvatcanhoc())
        except OSError:
            thoidiemsua = None
        if thoidiemsua != nho["thoidiemsua"]:
            nho["thoidiemsua"] = thoidiemsua
            try:
                with open(duongdanvatcanhoc(), "r", encoding = "utf-8") as file:
                    nho["dulieu"] = {k: {tuple(o) for o in v} for k, v in json.load(file).items()}
            except Exception:
                nho["dulieu"] = {}
    return nho["dulieu"].get(str(idbando), set())


def _duongdantiendophoban():
    return os.path.join(os.path.dirname(_thumucthietlap()), "tiendophoban.json")


# Tiến độ phó bản đang đi dở theo ID người chơi ({"<id>": {...}}): tắt bot mở lại trong phó bản thì làm tiếp từ bước đang dở
def taitiendophoban(idnguoichoi):
    try:
        with open(_duongdantiendophoban(), "r", encoding = "utf-8") as file:
            return json.load(file).get(str(idnguoichoi))
    except Exception:
        return None


def luutiendophoban(idnguoichoi, tiendo):
    # tiendo None: xoá
    filepath = _duongdantiendophoban()
    try:
        try:
            with open(filepath, "r", encoding = "utf-8") as file:
                dulieu = json.load(file)
        except (FileNotFoundError, ValueError):
            dulieu = {}
        if tiendo is None:
            if dulieu.pop(str(idnguoichoi), None) is None:
                return
        else:
            dulieu[str(idnguoichoi)] = tiendo
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def _duongdanbossphongyeu(idnguoichoi):
    # Mỗi nhân vật 1 file (nhiều cửa sổ ghi cùng lúc không đè nhau)
    return os.path.join(os.path.dirname(_thumucthietlap()), "bossphongyeu", f"{idnguoichoi}.json")


def taibossphongyeu(idnguoichoi):
    # Boss Phong Yêu Kính đã giết vòng đang đánh (tactu_langlyson_xq lưu để mở lại bot giữa phó bản không mất số boss)
    try:
        with open(_duongdanbossphongyeu(idnguoichoi), "r", encoding = "utf-8") as file:
            return json.load(file)
    except Exception:
        return None


def luubossphongyeu(idnguoichoi, dulieu):
    # dulieu None: xoá
    filepath = _duongdanbossphongyeu(idnguoichoi)
    try:
        if dulieu is None:
            if os.path.exists(filepath):
                os.remove(filepath)
            return
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def duongdanthongtinnguoichoi():
    # Khí Huyết tối đa / Ngoại Kháng / Nội Kháng ước lượng của người chơi khác (uocluongmuctieu_xq), giao diện gộp mọi cửa sổ rồi ghi:
    # {"<ID người chơi>": {"ten", "khihuyet": {"giatri", "mautut", "luc"}, "ngoaikhang" / "noikhang": {"giatri", "sodon", "luc"}}}
    return os.path.join(os.path.dirname(_thumucthietlap()), "thongtinnguoichoi.json")


def taithongtinnguoichoi():
    try:
        with open(duongdanthongtinnguoichoi(), "r", encoding = "utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as err:
        print(f"Lỗi đọc thông tin người chơi: {err}")
        return {}


def luuthongtinnguoichoi(dulieu):
    filepath = duongdanthongtinnguoichoi()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False, indent = 1)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(f"Lỗi lưu thông tin người chơi: {err}")


def duongdanthongtinquai():
    # Chỉ số quái đã đo chắc theo tên + cấp (uocluongmuctieu_xq.capnhatkhoquai), giao diện ghi, bot đọc
    return os.path.join(os.path.dirname(_thumucthietlap()), "thongtinquai.json")


def taithongtinquai():
    try:
        with open(duongdanthongtinquai(), "r", encoding = "utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as err:
        print(f"Lỗi đọc thông tin quái: {err}")
        return {}


def luuthongtinquai(dulieu):
    filepath = duongdanthongtinquai()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False, indent = 1)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(f"Lỗi lưu thông tin quái: {err}")


def _duongdanvitrithoyeu():
    return os.path.join(os.path.dirname(_thumucthietlap()), "vitrithoyeu.json")


# Toạ độ Thỏ Yêu trong Phong Yêu Kính theo bản ("aegis" / "nietban") + ID bản đồ mượn ({"nietban|134": [x, y]}), dùng chung mọi nhân vật:
# tắt bot bật lại giữa phó bản (không còn chỗ vào, Thỏ Yêu ngoài tầm nhìn) vẫn biết đường về hỏi số quái / ra
def taivitrithoyeu(khoa):
    try:
        with open(_duongdanvitrithoyeu(), "r", encoding = "utf-8") as file:
            toado = json.load(file).get(khoa)
        return tuple(toado) if toado else None
    except Exception:
        return None


def luuvitrithoyeu(khoa, x, y):
    filepath = _duongdanvitrithoyeu()
    try:
        try:
            with open(filepath, "r", encoding = "utf-8") as file:
                dulieu = json.load(file)
        except (FileNotFoundError, ValueError):
            dulieu = {}
        if dulieu.get(khoa) == [x, y]:
            return
        dulieu[khoa] = [x, y]
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def themvatcanhoc(idbando, x, y):
    filepath = duongdanvatcanhoc()
    try:
        try:
            with open(filepath, "r", encoding = "utf-8") as file:
                dulieu = json.load(file)
        except FileNotFoundError:
            dulieu = {}
        os_ = dulieu.setdefault(str(idbando), [])
        if [x, y] not in os_:
            os_.append([x, y])
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False)
        thaythefile(filetam, filepath)
        _vatcanhoc_cache["dulieu"].setdefault(str(idbando), set()).add((x, y))
    except Exception as err:
        print(err)


def duongdantodoitudong():
    return os.path.join(os.path.dirname(_thumucthietlap()), "todoi.json")


# Danh sách tổ đội tự động dùng chung cho mọi cửa sổ: [[id ưu tiên làm trưởng nhóm nhất, ...], ...]
# Mỗi cửa sổ là một tiến trình riêng nên đọc từ file, chỉ đọc lại khi file đổi (kiểm tra tối đa 1 lần/giây)
_todoitudong_cache = {"nhoms": None, "nhanvats": (), "thoidiemsua": None, "thoidiemkiemtra": 0.}


def _chuanhoanhomtodoitudongs(nhoms):
    ketqua = []
    for nhom in nhoms or []:
        ids = []
        for id_ in nhom or []:
            try:
                id_ = int(id_)
            except (TypeError, ValueError):
                continue
            if id_ > 0 and id_ not in ids:
                ids.append(id_)
        if ids:
            ketqua.append(ids)
    return ketqua


def tainhomtodoitudongs():
    from hangso_xq import NHANVATTODOITUDONGs_LIST

    filepath = duongdantodoitudong()
    if not os.path.exists(filepath):
        return _chuanhoanhomtodoitudongs(NHANVATTODOITUDONGs_LIST)
    try:
        with open(filepath, "r", encoding = "utf-8") as file:
            return _chuanhoanhomtodoitudongs(json.load(file).get("nhoms"))
    except Exception as err:
        print(err)
        return _chuanhoanhomtodoitudongs(NHANVATTODOITUDONGs_LIST)


# Đồ đem đốt khi vào Phong Yêu Kính (tactu_langlyson_xq._phantichdolamkim), dùng chung mọi nhân vật trên máy, sửa ở giao diện:
# màu tên được đốt (Lam Kim / Hoàng Kim), chỉ đồ Chưa giám định, cấp đồ >= cấp nhân vật - caphonnhanvat, tên chứa cụm trong "khongdot"
# thì không bao giờ đốt, "chidot" không rỗng thì chỉ đốt món có tên chứa 1 cụm trong đó. is_laydothanhvien: người give hết đồ thì xin
# thành viên cùng nhóm (cùng máy / LAN) còn đồ đúng điều kiện tới give sang thay vì dừng. is_nhatbanrac: trong phó bản nhặt cả luật
# "chỉ khi về bán rác", ra Chu Quốc thì bán rác ở Chủ Tiệm Y Dược (chừa đồ Lam Kim / Hoàng Kim) rồi mới vào vòng sau; tách hẳn khỏi ô
# "Tự động về bán rác" tab Hành trang (tactu_langlyson_xq._banracphongyeu)
# dieukienrakeocap (giữ tên khoá cũ cho file đã lưu): người give ra Phong Yêu Kính mở vòng mới theo 1 trong các kiểu cố định
# DIEUKIENRAPYKEOCAPs: (khoá, nhãn giao diện, số boss phải diệt, có chờ hết quái không). Áp dụng cả kéo cấp lẫn Phong Yêu Kính
# thường (người dùng dặn 2026-11-05: chọn 1 boss mà PYK thường vẫn chờ 2 boss). Game báo hoàn thành phó bản thì coi như đủ boss. Không có kiểu
# "2 boss rồi chờ hết quái": boss 2 chỉ ra khi đã hết quái (người dùng dặn). Khoá lạ (bản lưu cũ "2boss_hetquai") thì về kiểu đầu
DIEUKIENRAPYKEOCAPs = (("2boss", "Diệt đủ 2 boss là ra ngay", 2, False),
                       ("1boss_hetquai", "Diệt 1 boss rồi chờ hết quái (kiểu cũ)", 1, True),
                       ("1boss", "Diệt 1 boss là ra ngay", 1, False))
CAUHINHPHONGYEU_MACDINH = {"is_lamkim": True, "is_hoangkim": False, "is_chichuagiamdinh": True, "caphonnhanvat": 25, "khongdot": [], "chidot": [],
                           "is_laydothanhvien": True, "is_nhatbanrac": False, "dieukienrakeocap": "2boss"}
_cauhinhphongyeu_cache = {"cauhinh": None, "thoidiemsua": None, "thoidiemkiemtra": 0.}


def duongdancauhinhphongyeu():
    return os.path.join(os.path.dirname(_thumucthietlap()), "phongyeukinh.json")


def _chuanhoacauhinhphongyeu(cauhinh):
    ketqua = dict(CAUHINHPHONGYEU_MACDINH)
    if isinstance(cauhinh, dict):
        for khoa in ("is_lamkim", "is_hoangkim", "is_chichuagiamdinh", "is_laydothanhvien", "is_nhatbanrac"):
            if khoa in cauhinh:
                ketqua[khoa] = bool(cauhinh[khoa])
        try:
            ketqua["caphonnhanvat"] = max(0, int(cauhinh.get("caphonnhanvat", ketqua["caphonnhanvat"])))
        except (TypeError, ValueError):
            pass
        for khoa in ("khongdot", "chidot"):
            ketqua[khoa] = [str(t).strip() for t in cauhinh.get(khoa) or [] if str(t).strip()]
        if cauhinh.get("dieukienrakeocap") in [d[0] for d in DIEUKIENRAPYKEOCAPs]:
            ketqua["dieukienrakeocap"] = cauhinh["dieukienrakeocap"]
    return ketqua


def laydieukienrapykeocap(cauhinh = None):
    # -> (số boss phải diệt, có chờ hết quái không) theo cấu hình Phong Yêu Kính
    khoa = (cauhinh or taicauhinhphongyeu())["dieukienrakeocap"]
    for d in DIEUKIENRAPYKEOCAPs:
        if d[0] == khoa:
            return d[2], d[3]
    return DIEUKIENRAPYKEOCAPs[0][2], DIEUKIENRAPYKEOCAPs[0][3]


def taicauhinhphongyeu():
    # Đọc file (nhớ theo thời điểm sửa file, xét lại mỗi 1s); không có / lỗi thì mặc định
    cache = _cauhinhphongyeu_cache
    if cache["cauhinh"] is not None and time.time() - cache["thoidiemkiemtra"] < 1.:
        return cache["cauhinh"]
    cache["thoidiemkiemtra"] = time.time()
    filepath = duongdancauhinhphongyeu()
    try:
        thoidiemsua = os.path.getmtime(filepath)
    except OSError:
        thoidiemsua = None
    if cache["cauhinh"] is None or thoidiemsua != cache["thoidiemsua"]:
        cauhinh = None
        if thoidiemsua is not None:
            try:
                with open(filepath, "r", encoding = "utf-8") as file:
                    cauhinh = json.load(file)
            except Exception as err:
                print(err)
        cache.update(cauhinh = _chuanhoacauhinhphongyeu(cauhinh), thoidiemsua = thoidiemsua)
    return cache["cauhinh"]


def luucauhinhphongyeu(cauhinh):
    filepath = duongdancauhinhphongyeu()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(_chuanhoacauhinhphongyeu(cauhinh), file, ensure_ascii = False, indent = 2)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def _duongdangiaodienkeocap():
    return os.path.join(os.path.dirname(_thumucthietlap()), "keocap.json")


def taigiaodienkeocap():
    # Ô kéo cấp trên giao diện (Kéo tới cấp, Nhận đồ đệ, tên đồ đệ) lưu từ lần trước; không có / lỗi thì {}
    try:
        with open(_duongdangiaodienkeocap(), "r", encoding = "utf-8") as file:
            dulieu = json.load(file)
        return dulieu if isinstance(dulieu, dict) else {}
    except Exception:
        return {}


def luugiaodienkeocap(dulieu):
    filepath = _duongdangiaodienkeocap()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False, indent = 2)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def _duongdancaidatgiaodien():
    return os.path.join(os.path.dirname(_thumucthietlap()), "giaodien.json")


def taicaidatgiaodien():
    # Cài đặt chung của giao diện (chế độ sáng/tối...); không có / lỗi thì {}
    try:
        with open(_duongdancaidatgiaodien(), "r", encoding = "utf-8") as file:
            dulieu = json.load(file)
        return dulieu if isinstance(dulieu, dict) else {}
    except Exception:
        return {}


def luucaidatgiaodien(dulieu):
    filepath = _duongdancaidatgiaodien()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False, indent = 2)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def _duongdandanhsachnhanvat():
    return os.path.join(os.path.dirname(_thumucthietlap()), "danhsachnhanvat.json")


def taidanhsachnhanvat():
    # Thứ tự (kéo thả) trên danh sách nhân vật của giao diện, theo ID người chơi: {"thutu": [id...]}
    try:
        with open(_duongdandanhsachnhanvat(), "r", encoding = "utf-8") as file:
            dulieu = json.load(file)
        return {"thutu": [int(i) for i in dulieu.get("thutu", [])]}
    except Exception:
        return {"thutu": []}


def luudanhsachnhanvat(dulieu):
    filepath = _duongdandanhsachnhanvat()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(dulieu, file, ensure_ascii = False, indent = 2)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def luunhomtodoitudongs(nhoms):
    filepath = duongdantodoitudong()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump({"nhoms": _chuanhoanhomtodoitudongs(nhoms)}, file, ensure_ascii = False, indent = 2)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def _capnhattodoitudong_cache():
    if _todoitudong_cache["nhoms"] is not None and time.time() - _todoitudong_cache["thoidiemkiemtra"] < 1.:
        return
    _todoitudong_cache["thoidiemkiemtra"] = time.time()
    try:
        thoidiemsua = os.path.getmtime(duongdantodoitudong())
    except OSError:
        thoidiemsua = None
    if _todoitudong_cache["nhoms"] is None or thoidiemsua != _todoitudong_cache["thoidiemsua"]:
        nhoms = tainhomtodoitudongs()
        _todoitudong_cache["nhoms"] = nhoms
        _todoitudong_cache["nhanvats"] = tuple(id_ for nhom in nhoms for id_ in nhom)
        _todoitudong_cache["thoidiemsua"] = thoidiemsua


def laynhomtodoitudongs():
    _capnhattodoitudong_cache()
    return _todoitudong_cache["nhoms"]


def laynhanvattodoitudongs():
    # Gộp mọi nhóm: nhân vật của mình (coi như đồng đội / cùng bang)
    _capnhattodoitudong_cache()
    return _todoitudong_cache["nhanvats"]


_idtaikhoan_cache = {"ids": frozenset(), "thoidiemsua": None, "thoidiemkiemtra": 0.}


def layidtaikhoans():
    # ID người chơi các nhân vật trong file tài khoản (mọi máy): nhân vật của mình, coi là người quen. Đọc lại khi file đổi (tối đa 1 lần/5 giây)
    c = _idtaikhoan_cache
    if time.time() - c["thoidiemkiemtra"] < 5.:
        return c["ids"]
    c["thoidiemkiemtra"] = time.time()
    try:
        thoidiemsua = os.path.getmtime(duongdantaikhoan())
    except OSError:
        return c["ids"]
    if thoidiemsua != c["thoidiemsua"]:
        c["thoidiemsua"] = thoidiemsua
        ids = set()
        try:
            with open(duongdantaikhoan(), encoding = "utf-8-sig") as file:
                for taikhoan in json.load(file).get("taikhoans") or []:
                    try:
                        if int(taikhoan.get("idnguoichoi") or 0) > 0:
                            ids.add(int(taikhoan["idnguoichoi"]))
                    except (TypeError, ValueError, AttributeError):
                        pass
        except Exception as err:
            print(err)
        c["ids"] = frozenset(ids)
    return c["ids"]


def duongdandoiphoban():
    return os.path.join(os.path.dirname(_thumucthietlap()), "doiphoban.json")


# Đội phó bản (bảng "Phó bản chung", tactu_doiphoban_xq) dùng chung cho mọi cửa sổ: [{"ma", "ten", "thanhviens": [ID, người đầu là
# trưởng đội], "thutu": [việc], "chon": [việc], "vong": {việc: số vòng}, "phai": môn phái Tập Kích}]. Đọc lại khi file đổi (tối đa 1 lần/giây)
_doiphoban_cache = {"dois": None, "thoidiemsua": None, "thoidiemkiemtra": 0.}


def _chuanhoadoiphobans(dois):
    from hangso_xq import VIECDOI_MAP, VIECCOVONGs

    ketqua = []
    for doi in dois or []:
        if not isinstance(doi, dict) or not doi.get("ma"):
            continue
        ids = []
        for id_ in doi.get("thanhviens") or []:
            try:
                id_ = int(id_)
            except (TypeError, ValueError):
                continue
            if id_ > 0 and id_ not in ids:
                ids.append(id_)
        if not ids:
            continue
        thutu = [k for k in doi.get("thutu") or [] if k in VIECDOI_MAP]
        vong = {}
        for k, v in (doi.get("vong") or {}).items():
            try:
                if k in VIECCOVONGs and int(v) > 0:
                    vong[k] = int(v)
            except (TypeError, ValueError):
                pass
        ketqua.append({"ma": str(doi["ma"]), "ten": str(doi.get("ten") or "Đội"), "thanhviens": ids,
                       "thutu": thutu + [k for k in VIECDOI_MAP if k not in thutu],
                       "chon": [k for k in doi.get("chon") or [] if k in VIECDOI_MAP], "vong": vong, "phai": str(doi.get("phai") or "")})
    return ketqua


def taidoiphobans():
    try:
        with open(duongdandoiphoban(), "r", encoding = "utf-8") as file:
            return _chuanhoadoiphobans(json.load(file).get("dois"))
    except FileNotFoundError:
        return []
    except Exception as err:
        print(err)
        return []


def luudoiphobans(dois):
    filepath = duongdandoiphoban()
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump({"dois": _chuanhoadoiphobans(dois)}, file, ensure_ascii = False, indent = 2)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def laydoiphobans():
    if _doiphoban_cache["dois"] is None or time.time() - _doiphoban_cache["thoidiemkiemtra"] >= 1.:
        _doiphoban_cache["thoidiemkiemtra"] = time.time()
        try:
            thoidiemsua = os.path.getmtime(duongdandoiphoban())
        except OSError:
            thoidiemsua = None
        if _doiphoban_cache["dois"] is None or thoidiemsua != _doiphoban_cache["thoidiemsua"]:
            _doiphoban_cache["dois"] = taidoiphobans()
            _doiphoban_cache["thoidiemsua"] = thoidiemsua
    return _doiphoban_cache["dois"]


def laydoiphoban(ma):
    return next((d for d in laydoiphobans() if d["ma"] == ma), None)


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
        thaythefile(filetam, filepath)

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


KICHTHUOCLOGTOIDA = 5 * 1024 * 1024


def ghilognhanvat(idnguoichoi, dong):
    # Log lệnh của từng nhân vật ra _internal/log/<ID người chơi>.log để đọc lại sau (console PyCharm khó tìm, mất khi tắt).
    # Quá KICHTHUOCLOGTOIDA thì đổi sang .log.cu (giữ 1 bản cũ) để file không phình mãi
    try:
        thumuc = os.path.join(os.path.dirname(_thumucthietlap()), "log")
        os.makedirs(thumuc, exist_ok = True)
        duongdan = os.path.join(thumuc, f"{idnguoichoi}.log")
        if os.path.exists(duongdan) and os.path.getsize(duongdan) > KICHTHUOCLOGTOIDA:
            os.replace(duongdan, duongdan + ".cu")
        with open(duongdan, "a", encoding = "utf-8") as file:
            file.write(dong + "\n")
    except Exception:
        pass


_thunghiem_cache = {"dulieu": {}, "mtime": None, "kiemtra": 0.}


def laythunghiem(khoa, macdinh = None):
    # Cấu hình thử nghiệm đổi được khi tool đang chạy: _internal/thunghiem.json, đọc lại tối đa mỗi giây khi file thay đổi
    if time.time() - _thunghiem_cache["kiemtra"] > 1.:
        _thunghiem_cache["kiemtra"] = time.time()
        duongdan = os.path.join(os.path.dirname(_thumucthietlap()), "thunghiem.json")
        try:
            mtime = os.path.getmtime(duongdan)
        except OSError:
            mtime = None
        if mtime != _thunghiem_cache["mtime"]:
            _thunghiem_cache["mtime"] = mtime
            try:
                with open(duongdan, encoding = "utf-8-sig") as file:
                    _thunghiem_cache["dulieu"] = json.load(file) if mtime else {}
            except Exception:
                _thunghiem_cache["dulieu"] = {}
    return _thunghiem_cache["dulieu"].get(khoa, macdinh)


def tenmaynay():
    import socket
    return re.sub(r"[^\w.-]", "_", socket.gethostname()) or "maynay"


def duongdantaikhoan():
    # Tài khoản tự đăng nhập chung mọi máy (đồng bộ qua git): mỗi dòng ghi "maydangnhap" = tên máy được tự đăng nhập tài khoản đó,
    # nên chép cả thư mục bot sang máy khác cũng không thành hai máy giành nhau một tài khoản (2026-10-29 đã bị). Không dùng lại tên
    # taikhoan.json: bot bản cũ tự tạo lại file mẫu rỗng với tên đó (đang bị .gitignore)
    return os.path.join(os.path.dirname(_thumucthietlap()), "taikhoan_chung.json")


def duongdantaikhoantheomay():
    # Các file riêng từng máy trước đây (taikhoan_<tên máy>.json): chưa có file chung thì gộp lại (dangnhap_xq.taicauhinhdangnhap)
    import glob
    return {os.path.basename(duongdan)[len("taikhoan_"):-len(".json")]: duongdan
            for duongdan in sorted(glob.glob(os.path.join(os.path.dirname(_thumucthietlap()), "taikhoan_*.json")))
            if os.path.basename(duongdan) != "taikhoan_chung.json"}


# Trạng thái tạm ngưng (ẩn thân / người lạ) ghi ra file, mỗi nhân vật 1 file theo ID, để luồng tự đăng nhập
# biết mà không đăng nhập lại; nhân vật bị out thì bot mất trạng thái trong bộ nhớ nhưng file vẫn còn
def _thumuctamngung():
    return os.path.join(os.path.dirname(_thumucthietlap()), "tamngung")


def ghitamngung(idnguoichoi, thoidiemhet, lydo):
    if not idnguoichoi:
        return
    try:
        thumuc = _thumuctamngung()
        os.makedirs(thumuc, exist_ok = True)
        filepath = os.path.join(thumuc, f"{int(idnguoichoi)}.json")
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump({"thoidiemhet": thoidiemhet, "lydo": lydo}, file, ensure_ascii = False)
        thaythefile(filetam, filepath)
    except Exception as err:
        print(f"Lỗi khi ghi trạng thái tạm ngưng: {err}")


def xoatamngung(idnguoichoi):
    if not idnguoichoi:
        return
    try:
        os.remove(os.path.join(_thumuctamngung(), f"{int(idnguoichoi)}.json"))
    except FileNotFoundError:
        pass
    except Exception as err:
        print(f"Lỗi khi xoá trạng thái tạm ngưng: {err}")


def laytamngungdanghieuluc():
    # [(ID người chơi, thời điểm hết, lý do)] còn hiệu lực, hết lâu nhất trước
    ketqua = []
    thumuc = _thumuctamngung()
    try:
        tenfiles = os.listdir(thumuc)
    except OSError:
        return ketqua
    for tenfile in tenfiles:
        if not tenfile.endswith(".json"):
            continue
        try:
            with open(os.path.join(thumuc, tenfile), encoding = "utf-8") as file:
                dulieu = json.load(file)
            if dulieu.get("thoidiemhet", 0.) > time.time():
                ketqua.append((int(tenfile[:-5]), dulieu["thoidiemhet"], dulieu.get("lydo", "")))
        except Exception:
            continue
    return sorted(ketqua, key = lambda x: x[1], reverse = True)


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