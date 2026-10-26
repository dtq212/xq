# Sinh chữ ký cho diachi_xq.py từ xq.exe hiện tại (chạy tay khi thêm địa chỉ mới, hoặc sau khi game cập nhật mà diachi_xq báo
# chữ ký không dò được: sửa lại địa chỉ đúng trong MUCTIEU rồi chạy lại). Cần capstone (pip install capstone); bot chạy thì không cần.
#
#   python taochuky_xq.py [đường dẫn xq.exe]
#
# Với mỗi địa chỉ: tìm các lệnh trong mã dùng tới nó ("ma": lệnh bắt đầu tại địa chỉ đó; "bien": lệnh có toán hạng là địa chỉ
# tuyệt đối của biến), che (??) các byte có thể đổi khi game cập nhật (địa chỉ tuyệt đối trỏ vào exe, độ lệch call / jmp / jcc 32 bit),
# nới dần cửa sổ lệnh tới khi chữ ký khớp đúng 1 chỗ, chọn chữ ký ngắn nhất. Ghi vào khối CHUKY của diachi_xq.py rồi tự kiểm tra lại.
import os
import struct
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_32

import diachi_xq

DUONGDANMACDINH = r"E:\Games\ChienQuoc2D_Aegis\xq.exe"

# (tên, địa chỉ tính từ base ở bản game hiện tại, loại, ghi chú)
MUCTIEU = [
    # Biến toàn cục
    ("THONGTINGAME", 0x380B44, "bien", "con trỏ thông tin game (hành trang, kỹ năng, tìm đường...)"),
    ("NHANVAT", 0x380AF8, "bien", "con trỏ nhân vật mình"),
    ("BANGDOITUONG", 0x1BDA60, "bien", "bảng địa chỉ đối tượng xung quanh"),
    ("KHOIDIEUKHIEN", 0x372864, "bien", "khối điều khiển / chỉ số nhân vật (sinh lực +0x152C, bản đồ +0x15F4, mục tiêu tấn công +0x15F8...)"),
    ("NHANVATDANGCHICHUOT", 0x380B64, "bien", "đối tượng đang trỏ chuột"),
    ("BANGHIEUUNG", 0x1C05E0, "bien", "bảng id hiệu ứng theo vị trí"),
    ("CONTROALT", 0x380B38, "bien", "con trỏ cờ bật Alt"),
    ("DANGCLICKCHUOTTRAI", 0x380B7D, "bien", "đang giữ chuột trái"),
    ("MUCTIEUDANGCHON", 0x1BD4F0, "bien", "địa chỉ mục tiêu đang chọn"),
    ("IDMUCTIEUDANGCHON", 0x37284C, "bien", "id mục tiêu đang chọn"),
    ("MUCTIEUDANGCHON2", 0x1BD550, "bien", "địa chỉ mục tiêu đang chọn (bản 2)"),
    ("IDMUCTIEUDANGCHON2", 0x1BD554, "bien", "id mục tiêu đang chọn (bản 2)"),
    ("CHISOBUOCDICHUYEN", 0x380AFC, "bien", "chỉ số bước kế tiếp trong chuỗi đường đi (0 = không đi)"),
    ("CHUOIDUONGDI", 0x1FC2B4, "bien", "chuỗi đường đi toàn cục (ký tự hướng '1'..'8', bắt đầu từ chỉ số 1)"),
    ("CUASOTUYCHONNHANVAT", 0x3A642C, "bien", "cửa sổ tuỳ chọn nhân vật chính lần đầu"),
    # Hàm
    ("HAMGUILENH", 0x95450, "ma", "hàm gửi lệnh lên server (không xét mốc tự gửi lệnh)"),
    ("HAMPHEDUYETCAULENH", 0x95468, "ma", "đoạn phê duyệt câu lệnh trong hàm gửi lệnh"),
    ("HAMNHATVATPHAM", 0xB400, "ma", "nhặt vật phẩm xung quanh"),
    ("HAMCAPPHAT", 0x17DD0C, "ma", "toán tử new của game"),
    ("HAMKHOITAOTIMDUONG", 0xCEEB0, "ma", "hàm khởi tạo cấu trúc tìm đường / bản đồ"),
    ("HAMCLICKMANHINH", 0x47790, "ma", "xử lý click chuột tại điểm ảnh"),
    ("HAMTIMDUONGCUCBO", 0xB0D60, "ma", "tìm đường cục bộ (chuỗi hướng né vật cản)"),
    ("HAMTANGCAPDO", 0x16C730, "ma", "hàm được gọi ở chỗ vá chặn tăng cấp độ"),
    # Chỗ vá mã
    ("VA_AUTOINGAME", 0x6EC9, "ma", "NOP 10 byte khi tắt auto trong game"),
    ("VA_GHIMUCTIEU2", 0xA20F0, "ma", "mov [MUCTIEUDANGCHON2], eax"),
    ("VA_GHIIDMUCTIEU2", 0xA20F8, "ma", "mov [IDMUCTIEUDANGCHON2], ecx"),
    ("VA_GHIMUCTIEU", 0xA20FE, "ma", "mov [MUCTIEUDANGCHON], eax"),
    ("VA_GHIIDMUCTIEU", 0xA2106, "ma", "mov [IDMUCTIEUDANGCHON], edx"),
    ("VA_XOAIDMUCTIEU2", 0x9542B, "ma", "mov [IDMUCTIEUDANGCHON2], 0"),
    ("VA_XOAMUCTIEU", 0x95435, "ma", "mov [MUCTIEUDANGCHON], 0"),
    ("VA_LONGCLICK", 0x4993C, "ma", "hằng số tại +6: 1 = bật long click"),
    ("VA_CHUOTCHONMUCTIEUKYNANG", 0x5416C, "ma", "hằng số tại +6: 2 = trạng thái chuột chọn mục tiêu kỹ năng"),
    ("VA_TANGCAPDO", 0x13FB61, "ma", "call HAMTANGCAPDO (vá thành add esp, 8)"),
    ("VA_HIEUUNGMULOA", 0x4C0E, "ma", "byte tại +6 = 0 tắt hiệu ứng mù loà"),
    ("VA_DICHUYEN", 0x9BE38, "ma", "jle (7E) -> jmp (EB) để vô hiệu hoá di chuyển"),
    ("VA_TUTHEDELAY1", 0x1AFE3, "ma", "mov [esi+0x11B8], 0x0B (tư thế delay sau tấn công)"),
    ("VA_TUTHEDELAY2", 0x1B377, "ma", "mov [esi+0x11B8], 0x0B (tư thế delay sau tấn công)"),
    ("HOOK_TROCHUYEN", 0x5964, "ma", "chỗ hook đọc nội dung trò chuyện (6 byte)"),
]

SOLENHTRUOCTOIDA = 6
SOLENHSAUTOIDA = 16
SOBYTECODINHTOITHIEU = 6


def _lenhquanh(anh, md, vitri):
    # Các lệnh quanh vitri, đảm bảo có 1 lệnh bắt đầu đúng tại vitri: trả về (trước, từ vitri trở đi) dạng [(đầu, byte)]
    for lui in range(0x60, 0x60 + 16):
        dau = max(0, vitri - lui)
        lenhs = [(l.address, bytes(l.bytes)) for l in md.disasm(anh[dau:vitri + 0x80], dau)]
        chiso = next((i for i, (a, _) in enumerate(lenhs) if a == vitri), None)
        if chiso is not None and chiso >= 3:
            return lenhs[max(0, chiso - SOLENHTRUOCTOIDA):chiso], lenhs[chiso:chiso + SOLENHSAUTOIDA]
    lenhs = [(l.address, bytes(l.bytes)) for l in md.disasm(anh[vitri:vitri + 0x80], vitri)]
    return [], lenhs[:SOLENHSAUTOIDA]


def _lenhchua(anh, md, vitri):
    # Đầu lệnh chứa byte tại vitri (toán hạng địa chỉ của biến)
    for lui in range(0x60, 0x60 + 16):
        dau = max(0, vitri - lui)
        for l in md.disasm(anh[dau:vitri + 0x10], dau):
            if l.address <= vitri < l.address + l.size:
                if vitri + 4 <= l.address + l.size:
                    return l.address
                break
            if l.address > vitri:
                break
    return None


def _che(byte, imagebase, kichthuoc):
    # Che các byte có thể đổi khi game cập nhật
    che = [False] * len(byte)
    if len(byte) == 5 and byte[0] in (0xE8, 0xE9):
        che[1:5] = [True] * 4
    if len(byte) == 6 and byte[0] == 0x0F and 0x80 <= byte[1] <= 0x8F:
        che[2:6] = [True] * 4
    for i in range(len(byte) - 3):
        if imagebase <= struct.unpack_from("<I", byte, i)[0] < imagebase + kichthuoc:
            che[i:i + 4] = [True] * 4
    return " ".join("??" if c else "%02X" % b for b, c in zip(byte, che))


def _sinhchuky(anh, imagebase, vungma, md, dauvung, mucdich, loai):
    # Chữ ký ngắn nhất khớp đúng 1 chỗ cho cửa sổ lệnh quanh dauvung; mucdich = vị trí cần lấy (lệch = mucdich - đầu chữ ký).
    # Không chữ ký nào duy nhất (game có bản sao y hệt đoạn mã) thì trả chữ ký ít chỗ khớp nhất kèm (thứ tự, tổng số)
    # Trả về (chữ ký, lệch, thutu hoặc None)
    truoc, sau = _lenhquanh(anh, md, dauvung)
    ungviens = []
    for sosau in range(1, len(sau) + 1):
        for sotruoc in range(0, len(truoc) + 1):
            lenhs = (truoc[len(truoc) - sotruoc:] if sotruoc else []) + sau[:sosau]
            chuky = " ".join(_che(b, imagebase, len(anh)) for _, b in lenhs)
            if sum(1 for x in chuky.split() if x != "??") < SOBYTECODINHTOITHIEU:
                continue
            ungviens.append((len(chuky.split()), chuky, mucdich - lenhs[0][0]))
    duphong = None
    for _, chuky, lech in sorted(ungviens):
        vitris = sorted(diachi_xq.timkhop(anh, vungma, chuky))
        if len(vitris) == 1:
            return chuky, lech, None
        daukhop = mucdich - lech
        if daukhop in vitris and (duphong is None or len(vitris) < len(duphong[3])):
            duphong = (chuky, lech, (vitris.index(daukhop), len(vitris)), vitris)
    if duphong:
        return duphong[0], duphong[1], duphong[2]
    return None, None, None


def _chogoi(anh, vungma, diachiham, toida = 8):
    # Các lệnh call rel32 gọi tới diachiham: [vị trí lệnh call]
    kq = []
    for dau, cuoi in vungma:
        vitri = anh.find(b"\xE8", dau, cuoi)
        while vitri != -1 and len(kq) < toida:
            if vitri + 5 <= cuoi and vitri + 5 + struct.unpack_from("<i", anh, vitri + 1)[0] == diachiham:
                kq.append(vitri)
            vitri = anh.find(b"\xE8", vitri + 1, cuoi)
    return kq


def main():
    duongdan = sys.argv[1] if len(sys.argv) > 1 else DUONGDANMACDINH
    anh, imagebase, vungma, _ = diachi_xq.docanhexe(duongdan)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    dong, loi, ketqua = [], [], {}
    for ten, diachi, loai, ghichu in MUCTIEU:
        chuky = lech = thutu = None
        if loai == "ma":
            # Ô nhảy sang hàm thư viện (jmp [import]) thì chữ ký tại chỗ dựa vào thứ tự bảng nhập khẩu: chỉ dò qua chỗ gọi
            if anh[diachi:diachi + 2] != b"\xFF\x25":
                chuky, lech, thutu = _sinhchuky(anh, imagebase, vungma, md, diachi, diachi, "ma")
            # Hàm: thử cả dò qua chỗ gọi tới nó, lấy chữ ký ngắn hơn (ưu tiên chữ ký duy nhất)
            if ten.startswith("HAM"):
                for vitricall in _chogoi(anh, vungma, diachi):
                    ck, lc, tt = _sinhchuky(anh, imagebase, vungma, md, vitricall, vitricall + 1, "goi")
                    if ck and (chuky is None or (tt is None and thutu is not None)
                               or ((tt is None) == (thutu is None) and len(ck.split()) < len(chuky.split()))):
                        chuky, lech, thutu, loai = ck, lc, tt, "goi"
        else:
            mau = struct.pack("<I", imagebase + diachi)
            tot = None
            for dau, cuoi in vungma:
                vitri = anh.find(mau, dau, cuoi)
                solan = 0
                while vitri != -1 and solan < 40:
                    solan += 1
                    daulenh = _lenhchua(anh, md, vitri)
                    if daulenh is not None:
                        ck, lc, tt = _sinhchuky(anh, imagebase, vungma, md, daulenh, vitri, loai)
                        if ck and (tot is None or (tt is None and tot[2] is not None)
                                   or ((tt is None) == (tot[2] is None) and len(ck.split()) < len(tot[0].split()))):
                            tot = (ck, lc, tt)
                    vitri = anh.find(mau, vitri + 1, cuoi)
            if tot:
                chuky, lech, thutu = tot
        if not chuky:
            loi.append(ten)
            print("KHÔNG SINH ĐƯỢC:", ten)
            continue
        phan = f', {thutu}' if thutu else ''
        dong.append(f'    "{ten}": ("{loai}", "{chuky}", {lech}, {hex(diachi)}{phan}),  # {ghichu}')
        ketqua[ten] = (loai, chuky, lech, thutu)
        print(f"{ten:28s} {hex(diachi):>10s}  {loai:4s} {chuky}  (lệch {lech}{', thứ tự ' + str(thutu) if thutu else ''})")
    duongdanpy = diachi_xq.__file__
    with open(duongdanpy, "r", encoding = "utf-8") as f:
        noidung = f.read()
    dau = noidung.index("# --- BẮT ĐẦU CHỮ KÝ")
    dau = noidung.index("\n", dau) + 1
    cuoi = noidung.index("# --- KẾT THÚC CHỮ KÝ ---")
    noidung = noidung[:dau] + "CHUKY = {\n" + "\n".join(dong) + "\n}\n" + noidung[cuoi:]
    with open(duongdanpy, "w", encoding = "utf-8", newline = "") as f:
        f.write(noidung)
    # Tự kiểm tra: dò lại bằng chính bảng vừa ghi
    sai = 0
    for ten, diachi, loai, _ in MUCTIEU:
        if ten in loi:
            continue
        kieu, chuky, lech, thutu = ketqua[ten]
        giatri, _ = diachi_xq.giaichuky(anh, imagebase, vungma, kieu, chuky, lech, thutu)
        if giatri != diachi:
            sai += 1
            print("KIỂM TRA SAI:", ten, hex(diachi), giatri)
    print(f"\nĐã ghi {len(dong)} chữ ký vào {os.path.basename(duongdanpy)}; không sinh được {len(loi)}; kiểm tra sai {sai}")


if __name__ == "__main__":
    main()
