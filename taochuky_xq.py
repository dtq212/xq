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
from capstone.x86 import X86_OP_IMM, X86_OP_MEM

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
    # Offset trong cấu trúc ("hang": hằng số nằm trong lệnh). TG_: trong [THONGTINGAME]; TD_: trong cấu trúc tìm đường [TG + TG_TIMDUONG];
    # KN_: bảng kỹ năng [TG + TG_KYNANG]; HT_: hành trang [TG + TG_HANHTRANG]; NV_: nhân vật / đối tượng; KDK_: trong [KHOIDIEUKHIEN]
    ("TG_TIMDUONG", 0xADFDEC, "hang", "cấu trúc tìm đường / bản đồ"),
    ("TG_HANHTRANG", 0xADFD78, "hang", "hành trang (id, tên, số lượng, mô tả vật phẩm)"),
    ("TG_KYNANG", 0xADFE18, "hang", "bảng kỹ năng"),
    ("TG_TUIHANHTRANG", 0xADFE0C, "hang", "túi hành trang (số ô mở mỗi túi)"),
    ("TG_MOCTUGUILENH", 0xADFC5C, "hang", "mốc client được tự gửi lệnh (timeGetTime)"),
    ("TG_TIMDUONGCUCBO", 0xAE1178, "hang", "đối tượng tìm đường cục bộ"),
    ("TG_VANKHI", 0xADFDE8, "hang", "đối tượng vận khí"),
    ("TG_AUTOINGAME", 0xAEC924, "hang", "cờ bật auto trong game"),
    ("TG_CUASOYESNO", 0xADFE10, "hang", "cửa sổ yes / no"),
    ("TG_ENTER", 0xADFD60, "hang", "khung chat (Enter)"),
    ("TG_TROCHUYEN", 0xADFDD8, "hang", "nội dung trò chuyện"),
    ("TG_GIAODIEN", 0xADFDA8, "hang", "giao diện chính (con trỏ chuột...)"),
    ("TG_CUASOXACNHAN", 0xADFD8C, "hang", "cửa sổ xác nhận"),
    ("TG_THONGBAO", 0xADFD70, "hang", "thông báo gần nhất"),
    ("TG_NHOM", 0xADFDA4, "hang", "thành viên nhóm"),
    ("TG_MONPHAI", 0xADFDDC, "hang", "môn phái"),
    ("TG_MAUPK", 0xAED6CC, "hang", "màu PK"),
    ("TG_CHUCNANGMORONG", 0xAEBC0C, "hang", "chức năng mở rộng"),
    ("TG_CUASOTUYCHON", 0xADFD74, "hang", "cửa sổ tuỳ chọn"),
    ("TG_KHO", 0xADFD88, "hang", "kho (Quản Khố): rương đang mở"),
    ("TG_CUAHANG", 0xADFD80, "hang", "cửa hàng NPC đang / vừa mở (id NPC +0x110, hàng +0x7D78 mỗi món 0x58: ô +4, giá +8, tên +0x12)"),
    ("TG_NHIEMVU", 0xADFDAC, "hang", "cửa sổ nhiệm vụ (tên mục +0x90, mô tả +0x860, mỗi mục 4 byte con trỏ)"),
    ("TD_DICH", 0x37C534, "hang", "đích tìm đường x (y ở + 4)"),
    ("TD_BANDO", 0x37C85C, "hang", "bản đồ đích tìm đường (-1 = không đi)"),
    ("KN_KICHTHUOC", 0x224, "hang", "kích thước 1 ô kỹ năng"),
    ("KN_ID", 0x6830, "hang", "id kỹ năng trong ô"),
    ("KN_HOICHIEU", 0x6A4C, "hang", "thời gian hồi chiêu còn lại trong ô"),
    ("HT_TEN", 0x1A8, "hang", "tên vật phẩm (mỗi ô 0x20)"),
    ("HT_MOTA", 0xF52, "hang", "mô tả vật phẩm (mỗi ô 0x44C)"),
    ("HT_KICHTHUOCMOTA", 0x44C, "hang", "kích thước mô tả 1 ô"),
    ("HT_SOLUONG", 0x1D6CC, "hang", "số lượng vật phẩm"),
    ("HT_NHOMHOI", 0xEE8, "hang", "nhóm thời gian hồi của vật phẩm (1 byte mỗi ô)"),
    ("HT_THOILUONGHOI", 0x1DF80, "hang", "thời lượng hồi của ô (giây, 0 = không hồi)"),
    ("HT_BATDAUHOI", 0x1E128, "hang", "thời điểm bắt đầu hồi của ô (timeGetTime)"),
    ("KHO_TEN", 0x1A118, "hang", "tên vật phẩm ô rương đang mở (mỗi ô 0x20)"),
    ("KHO_SOLUONG", 0x1AD18, "hang", "số lượng vật phẩm ô rương (4 byte, đồ không chồng được = 0)"),
    ("KHO_MA", 0x1AE98, "hang", "mã loại vật phẩm ô rương (4 byte)"),
    ("KHO_RUONGMO", 0x1B1F8, "hang", "rương đang mở (từ 0)"),
    ("KHO_SORUONG", 0x1B1FC, "hang", "số rương dùng được"),
    ("KHO_DANGHIEN", 0x304, "hang", "cờ cửa sổ kho đang hiện (1 byte)"),
    ("NV_TUTHE", 0x1178, "hang", "tư thế (1 đứng, 2 đi, 6 đánh, 9 phép)"),
    ("NV_TEN", 0x10AC, "hang", "tên đối tượng"),
    ("NV_DANHHIEU", 0x1134, "hang", "danh hiệu hiện trên tên (NPC cửa hàng các nước: \"Chủ Tiệm Vũ Khí\")"),
    ("NV_PHANTRAMMAU", 0x1410, "hang", "% máu / 2"),
    ("NV_CHET", 0x1424, "hang", "cờ đã chết"),
    ("NV_SOBAY", 0x11C4, "hang", "số máu bay (10 ô)"),
    ("NV_HIEUUNG", 0x1638, "hang", "danh sách hiệu ứng"),
    ("NV_KICHTHUOCHIEUUNG", 0x13C, "hang", "kích thước 1 hiệu ứng"),
    ("NV_HUONGMAT", 0x13F8, "hang", "hướng mặt"),
    ("NV_HOATANH", 0x10A0, "hang", "chỉ số hàng hoạt ảnh (hiện tại, + 4 cuối)"),
    ("NV_ANTHAN", 0x162D, "hang", "ẩn thân"),
    ("NV_VUKHI", 0x1184, "hang", "id vũ khí"),
    ("NV_NGOAITRANG", 0x1174, "hang", "id ngoại trang"),
    ("NV_CANH", 0x119C, "hang", "id cánh (2 số)"),
    ("KDK_SINHLUC", 0x152C, "hang", "sinh lực"),
    ("KDK_SINHLUCTOIDA", 0x1530, "hang", "sinh lực tối đa"),
    ("KDK_NOILUC", 0x1534, "hang", "nội lực"),
    ("KDK_NOILUCTOIDA", 0x1538, "hang", "nội lực tối đa"),
    ("KDK_NGUYENKHI", 0x1560, "hang", "nguyên khí"),
    ("KDK_DIEMPK", 0x1568, "hang", "điểm PK"),
    ("KDK_KINHNGHIEM", 0x159C, "hang", "kinh nghiệm (tích luỹ khi chặn tăng cấp, giảm khi lên cấp)"),
    ("KDK_NGANLUONG", 0x15A4, "hang", "ngân lượng"),
    ("KDK_THELUC", 0x15A8, "hang", "thể lực"),
    ("KDK_TIENGUI", 0x15AC, "hang", "tiền gửi trong kho"),
    ("KDK_CAPDO", 0x15B0, "hang", "cấp độ"),
    ("KDK_BANDO", 0x15F4, "hang", "bản đồ hiện tại"),
    ("KDK_MUCTIEUTANCONG", 0x15F8, "hang", "id mục tiêu tấn công của client (+ 0xC con trỏ)"),
    ("KDK_DICHCLICK", 0x1608, "hang", "đích click chuột (x, y)"),
]

SOCHUKYHANG = 3

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


def _che(byte, imagebase, kichthuoc, chethem = ()):
    # Che các byte có thể đổi khi game cập nhật (chethem: chỉ số byte trong lệnh cần che thêm, vd chính hằng số offset cần dò)
    che = [i in chethem for i in range(len(byte))]
    if len(byte) == 5 and byte[0] in (0xE8, 0xE9):
        che[1:5] = [True] * 4
    if len(byte) == 6 and byte[0] == 0x0F and 0x80 <= byte[1] <= 0x8F:
        che[2:6] = [True] * 4
    for i in range(len(byte) - 3):
        if imagebase <= struct.unpack_from("<I", byte, i)[0] < imagebase + kichthuoc:
            che[i:i + 4] = [True] * 4
    return " ".join("??" if c else "%02X" % b for b, c in zip(byte, che))


def _demkhop(anh, vungma, chuky, toida = 2):
    # Đếm nhanh số chỗ khớp (dừng khi đủ toida), dùng để lọc ứng viên trước khi kiểm tra kỹ bằng diachi_xq.timkhop
    bieuthuc = diachi_xq.chukythanhregex(chuky)
    dem = 0
    for dau, cuoi in vungma:
        for _ in bieuthuc.finditer(anh, dau, cuoi):
            dem += 1
            if dem >= toida:
                return dem
    return dem


def _sinhchuky(anh, imagebase, vungma, md, dauvung, mucdich, loai, vungche = None):
    # Chữ ký ngắn nhất khớp đúng 1 chỗ cho cửa sổ lệnh quanh dauvung; mucdich = vị trí cần lấy (lệch = mucdich - đầu chữ ký).
    # Không chữ ký nào duy nhất (game có bản sao y hệt đoạn mã) thì trả chữ ký ít chỗ khớp nhất kèm (thứ tự, tổng số)
    # Trả về (chữ ký, lệch, thutu hoặc None)
    truoc, sau = _lenhquanh(anh, md, dauvung)
    ungviens = []
    for sosau in range(1, len(sau) + 1):
        for sotruoc in range(0, len(truoc) + 1):
            lenhs = (truoc[len(truoc) - sotruoc:] if sotruoc else []) + sau[:sosau]
            chuky = " ".join(_che(b, imagebase, len(anh), [i for i in range(len(b)) if vungche and vungche[0] <= a + i < vungche[1]])
                             for a, b in lenhs)
            if sum(1 for x in chuky.split() if x != "??") < SOBYTECODINHTOITHIEU:
                continue
            ungviens.append((len(chuky.split()), chuky, mucdich - lenhs[0][0]))
    duphong = None
    for _, chuky, lech in sorted(ungviens):
        if loai == "hang":
            if _demkhop(anh, vungma, chuky) == 1 and len(diachi_xq.timkhop(anh, vungma, chuky)) == 1:
                return chuky, lech, None
            continue
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


def _sinhchukyhang(anh, imagebase, vungma, md, mdct, giatri):
    # Tối đa SOCHUKYHANG chữ ký cho hằng số offset giatri, lấy từ các lệnh có toán hạng [reg + giatri] hoặc giá trị tức thời = giatri,
    # ở các hàm khác nhau (cách nhau > 0x400 byte). Trả về [(chữ ký, lệch)]
    mau = struct.pack("<I", giatri)
    kq, dadung, dathu = [], [], 0
    for dau, cuoi in vungma:
        vitri = anh.find(mau, dau, cuoi)
        while vitri != -1 and len(kq) < SOCHUKYHANG and dathu < 60:
            if all(abs(vitri - x) > 0x400 for x in dadung):
                daulenh = _lenhchua(anh, md, vitri)
                lenh = next(mdct.disasm(anh[daulenh:daulenh + 16], daulenh), None) if daulenh is not None else None
                if lenh and any((o.type == X86_OP_MEM and o.mem.disp == giatri) or (o.type == X86_OP_IMM and o.imm == giatri) for o in lenh.operands):
                    dathu += 1
                    ck, lc, _ = _sinhchuky(anh, imagebase, vungma, md, daulenh, vitri, "hang", (vitri, vitri + 4))
                    if ck:
                        kq.append((ck, lc))
                        dadung.append(vitri)
            vitri = anh.find(mau, vitri + 1, cuoi)
    return kq


def main():
    duongdan = sys.argv[1] if len(sys.argv) > 1 else DUONGDANMACDINH
    anh, imagebase, vungma, _ = diachi_xq.docanhexe(duongdan)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    mdct = Cs(CS_ARCH_X86, CS_MODE_32)
    mdct.detail = True
    dong, loi, ketqua = [], [], {}
    for ten, diachi, loai, ghichu in MUCTIEU:
        chuky = lech = thutu = None
        if loai == "hang":
            danhsach = _sinhchukyhang(anh, imagebase, vungma, md, mdct, diachi)
            if not danhsach:
                loi.append(ten)
                print("KHÔNG SINH ĐƯỢC:", ten)
                continue
            dong.append(f'    "{ten}": ("hang", {danhsach!r}, None, {hex(diachi)}),  # {ghichu}')
            ketqua[ten] = ("hang", danhsach, None, None)
            print(f"{ten:28s} {hex(diachi):>10s}  hang {len(danhsach)} chữ ký: {danhsach[0][0]}")
            continue
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
        giatri, _ = diachi_xq.giaimuc(anh, imagebase, vungma, (kieu, chuky, lech, diachi) + ((thutu,) if thutu else ()))
        if giatri != diachi:
            sai += 1
            print("KIỂM TRA SAI:", ten, hex(diachi), giatri)
    print(f"\nĐã ghi {len(dong)} chữ ký vào {os.path.basename(duongdanpy)}; không sinh được {len(loi)}; kiểm tra sai {sai}")


if __name__ == "__main__":
    main()
