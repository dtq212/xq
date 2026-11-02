# Thử in 1 dòng vào khung trò chuyện của client (giống moitruong_xq.action_themdongkhungchat), không qua bot:
#   py _internal/thu_khungchat.py [pid] ["nội dung"]
# Không ghi pid thì lấy xq.exe đầu tiên. Thử thêm mã màu: ESC + 1 chữ, vd "\x1bR".
import ctypes
import sys

import pymem
import pymem.process
from keystone import Ks, KS_ARCH_X86, KS_MODE_32

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))))
from diachi_xq import DC

pid = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
noidung = next((a for a in sys.argv[1:] if not a.isdigit()), "[Foxia] Thử in dòng vào khung trò chuyện")
noidung = noidung.encode("utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")  # cho phép gõ \x1bR

pm = pymem.Pymem(pid) if pid else pymem.Pymem("xq.exe")
base = pymem.process.module_from_name(pm.process_handle, "xq.exe").lpBaseOfDll
diachi = pm.allocate(0x40 + 1024)
ma, _ = Ks(KS_ARCH_X86, KS_MODE_32).asm(f"""
    mov eax, dword ptr [{hex(base + DC.THONGTINGAME)}]
    test eax, eax
    je ketthuc
    mov ecx, dword ptr [eax + {hex(DC.TG_KHUNGCHAT)}]
    test ecx, ecx
    je ketthuc
    push 0
    push {hex(diachi + 0x40)}
    mov eax, {hex(base + DC.HAMTHEMDONGKHUNGCHAT)}
    call eax
ketthuc:
    ret 4
""")
pm.write_bytes(diachi, bytes(ma), len(ma))
chuoi = noidung.encode("utf-8")[:1023]
pm.write_bytes(diachi + 0x40, chuoi + b"\x00", len(chuoi) + 1)
luong = pm.start_thread(diachi)
ctypes.windll.kernel32.WaitForSingleObject(luong, 2000)
pm.free(diachi)
print("Đã gọi, xem khung trò chuyện trong game")
