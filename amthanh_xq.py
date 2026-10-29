import ctypes
import uuid
from ctypes import wintypes

# Tắt / bật tiếng theo tiến trình qua Windows Audio Session API (giống bảng Volume Mixer), gọi COM bằng ctypes thuần
# để khỏi thêm thư viện (pycaw/comtypes). Mỗi client game là 1 tiến trình có phiên âm thanh riêng trên loa mặc định

_ole32 = ctypes.OleDLL("ole32")
COINIT_MULTITHREADED = 0x0
CLSCTX_ALL = 0x17
RPC_E_CHANGED_MODE = -2147417850
# eRender, eMultimedia
EDATAFLOW_RENDER = 0
EROLE_MULTIMEDIA = 1


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

    def __init__(self, chuoi):
        super().__init__()
        ctypes.memmove(ctypes.byref(self), uuid.UUID(chuoi).bytes_le, ctypes.sizeof(self))


CLSID_MMDEVICEENUMERATOR = GUID("BCDE0395-E52F-467C-8E3D-C4579291692E")
IID_IMMDEVICEENUMERATOR = GUID("A95664D2-9614-4F35-A746-DE8DB63617E6")
IID_IAUDIOSESSIONMANAGER2 = GUID("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F")
IID_IAUDIOSESSIONCONTROL2 = GUID("BFB7FF88-7239-4FC9-8FA2-07C950BE9C6D")
IID_ISIMPLEAUDIOVOLUME = GUID("87CE5498-68D6-44E5-9215-6DA47EF883D8")

# Thứ tự hàm trong vtable (0-2 là IUnknown: QueryInterface, AddRef, Release)
_QUERYINTERFACE, _RELEASE = 0, 2
_ENUMERATOR_GETDEFAULTAUDIOENDPOINT = 4
_DEVICE_ACTIVATE = 3
_MANAGER2_GETSESSIONENUMERATOR = 5
_SESSIONENUM_GETCOUNT, _SESSIONENUM_GETSESSION = 3, 4
_CONTROL2_GETPROCESSID = 14
_VOLUME_SETMUTE, _VOLUME_GETMUTE = 5, 6
_KIEUBYREF = type(ctypes.byref(ctypes.c_int()))


def _goi(contro, vitri, *thamsos):
    # contro là con trỏ giao diện COM (c_void_p); hàm thứ vitri trong vtable, trả HRESULT (OleDLL/HRESULT tự raise khi lỗi)
    vtable = ctypes.cast(contro, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]
    # byref(...) truyền như con trỏ, còn lại (c_int, DWORD, BOOL, c_void_p) giữ đúng kiểu
    kieuthamsos = [ctypes.c_void_p] + [ctypes.c_void_p if isinstance(t, _KIEUBYREF) else type(t) for t in thamsos]
    ham = ctypes.WINFUNCTYPE(ctypes.HRESULT, *kieuthamsos)(vtable[vitri])
    return ham(contro, *thamsos)


def _release(contro):
    if contro:
        vtable = ctypes.cast(contro, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]
        ctypes.WINFUNCTYPE(wintypes.ULONG, ctypes.c_void_p)(vtable[_RELEASE])(contro)


def khoitaocom():
    # Gọi 1 lần ở luồng sẽ dùng các hàm dưới
    try:
        _ole32.CoInitializeEx(None, COINIT_MULTITHREADED)
    except OSError as err:
        if getattr(err, "winerror", None) != RPC_E_CHANGED_MODE:
            raise


def _laysessionmanager():
    enumerator, thietbi, manager = ctypes.c_void_p(), ctypes.c_void_p(), ctypes.c_void_p()
    _ole32.CoCreateInstance(ctypes.byref(CLSID_MMDEVICEENUMERATOR), None, CLSCTX_ALL, ctypes.byref(IID_IMMDEVICEENUMERATOR),
                            ctypes.byref(enumerator))
    try:
        _goi(enumerator, _ENUMERATOR_GETDEFAULTAUDIOENDPOINT, ctypes.c_int(EDATAFLOW_RENDER), ctypes.c_int(EROLE_MULTIMEDIA),
             ctypes.byref(thietbi))
        try:
            _goi(thietbi, _DEVICE_ACTIVATE, ctypes.byref(IID_IAUDIOSESSIONMANAGER2), wintypes.DWORD(CLSCTX_ALL), ctypes.c_void_p(),
                 ctypes.byref(manager))
        finally:
            _release(thietbi)
    finally:
        _release(enumerator)
    return manager


def datamthanhtientrinhs(pid_tattieng):
    # pid_tattieng: {pid: True (tắt tiếng) / False (bật tiếng)}; tiến trình không có trong đây thì để nguyên.
    # Chỉ gọi SetMute khi khác trạng thái hiện tại (khỏi làm nhấp nháy Volume Mixer)
    manager = _laysessionmanager()
    dsphien = ctypes.c_void_p()
    try:
        _goi(manager, _MANAGER2_GETSESSIONENUMERATOR, ctypes.byref(dsphien))
        try:
            soluong = ctypes.c_int()
            _goi(dsphien, _SESSIONENUM_GETCOUNT, ctypes.byref(soluong))
            for i in range(soluong.value):
                control, control2, amluong = ctypes.c_void_p(), ctypes.c_void_p(), ctypes.c_void_p()
                try:
                    _goi(dsphien, _SESSIONENUM_GETSESSION, ctypes.c_int(i), ctypes.byref(control))
                    _goi(control, _QUERYINTERFACE, ctypes.byref(IID_IAUDIOSESSIONCONTROL2), ctypes.byref(control2))
                    pid = wintypes.DWORD()
                    # Phiên âm thanh hệ thống / nhiều tiến trình trả mã lỗi riêng: bỏ qua
                    try:
                        _goi(control2, _CONTROL2_GETPROCESSID, ctypes.byref(pid))
                    except OSError:
                        continue
                    if pid.value not in pid_tattieng:
                        continue
                    _goi(control, _QUERYINTERFACE, ctypes.byref(IID_ISIMPLEAUDIOVOLUME), ctypes.byref(amluong))
                    dangtat = wintypes.BOOL()
                    _goi(amluong, _VOLUME_GETMUTE, ctypes.byref(dangtat))
                    cantat = bool(pid_tattieng[pid.value])
                    if bool(dangtat.value) != cantat:
                        _goi(amluong, _VOLUME_SETMUTE, wintypes.BOOL(cantat), ctypes.c_void_p())
                finally:
                    _release(amluong)
                    _release(control2)
                    _release(control)
        finally:
            _release(dsphien)
    finally:
        _release(manager)
