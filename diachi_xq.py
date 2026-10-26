# Địa chỉ trong xq.exe (tính từ base của module) dò tự động bằng chữ ký thay vì viết cứng: game cập nhật làm mã dịch chuyển thì
# chỉ cần chữ ký còn khớp là địa chỉ mới tự đúng. Chữ ký sinh bằng taochuky_xq.py từ xq.exe hiện tại.
#
# Dò trên FILE xq.exe trên đĩa (dựng lại ảnh bộ nhớ theo section PE), không dò trên bộ nhớ game: bot đã vá nhiều chỗ trong bộ nhớ
# (NOP, đổi hằng số...) nên chữ ký trên bộ nhớ có thể không khớp; mã trên đĩa giống hệt bộ nhớ trừ đúng các chỗ vá đó.
# Kết quả lưu đệm theo SHA-1 của xq.exe (_internal/diachi_cache.json): game chưa đổi thì không dò lại.
# Mỗi chữ ký phải khớp đúng 1 chỗ; không khớp / khớp nhiều chỗ thì ghi log tên địa chỉ và dùng giá trị dự phòng (giá trị đúng với
# bản game lúc sinh chữ ký). Đoạn mã game có 2 bản sao y hệt (không chữ ký nào duy nhất được) thì chữ ký kèm (thứ tự, tổng số chỗ khớp):
# dò ra đúng tổng số đó mới lấy chỗ thứ tự, khác thì vẫn báo lỗi.
#
# Mỗi mục: tên: (loại, chữ ký, lệch, giá trị dự phòng[, (thứ tự, tổng số chỗ khớp)])
#   "ma"  : địa chỉ mã (hàm, chỗ vá)              = vị trí khớp + lệch
#   "bien": biến toàn cục mà lệnh trong mã trỏ tới = (số 32 bit đọc tại vị trí khớp + lệch) - ImageBase
#   "goi" : hàm được lệnh call trong chữ ký gọi    = đích của call (lệch trỏ vào 4 byte độ lệch của call)
import hashlib
import json
import os
import re
import struct
import threading

DUONGDANDEM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_internal", "diachi_cache.json")

# --- BẮT ĐẦU CHỮ KÝ (sinh bởi taochuky_xq.py, không sửa tay) ---
CHUKY = {
    "THONGTINGAME": ("bien", "8B 15 ?? ?? ?? ?? 56 8B 42 14", 2, 0x380b44),  # con trỏ thông tin game (hành trang, kỹ năng, tìm đường...)
    "NHANVAT": ("bien", "66 8B 69 FE 8B 35 ?? ?? ?? ??", 6, 0x380af8),  # con trỏ nhân vật mình
    "BANGDOITUONG": ("bien", "B8 ?? ?? ?? ?? 89 59 20 8B 08", 1, 0x1bda60),  # bảng địa chỉ đối tượng xung quanh
    "KHOIDIEUKHIEN": ("bien", "3B EE 75 33 8B 15 ?? ?? ?? ??", 6, 0x372864),  # khối điều khiển / chỉ số nhân vật (sinh lực +0x152C, bản đồ +0x15F4, mục tiêu tấn công +0x15F8...)
    "NHANVATDANGCHICHUOT": ("bien", "3B C6 75 10 89 1D ?? ?? ?? ??", 6, 0x380b64),  # đối tượng đang trỏ chuột
    "BANGHIEUUNG": ("bien", "3B 34 9D ?? ?? ?? ?? 74 10 40", 3, 0x1c05e0),  # bảng id hiệu ứng theo vị trí
    "CONTROALT": ("bien", "03 D0 8B FA 8B 15 ?? ?? ?? ??", 6, 0x380b38),  # con trỏ cờ bật Alt
    "DANGCLICKCHUOTTRAI": ("bien", "74 10 EB 09 A0 ?? ?? ?? ?? 84 C0", 5, 0x380b7d),  # đang giữ chuột trái
    "MUCTIEUDANGCHON": ("bien", "8D 7C 24 4C 8B 2D ?? ?? ?? ??", 6, 0x1bd4f0),  # địa chỉ mục tiêu đang chọn
    "IDMUCTIEUDANGCHON": ("bien", "8B 0D ?? ?? ?? ?? 85 C9 7E 11", 2, 0x37284c),  # id mục tiêu đang chọn
    "MUCTIEUDANGCHON2": ("bien", "3B C3 7D 1D 89 35 ?? ?? ?? ??", 6, 0x1bd550),  # địa chỉ mục tiêu đang chọn (bản 2)
    "IDMUCTIEUDANGCHON2": ("bien", "7E 67 3B 05 ?? ?? ?? ?? 75 5F", 4, 0x1bd554),  # id mục tiêu đang chọn (bản 2)
    "CHISOBUOCDICHUYEN": ("bien", "89 35 ?? ?? ?? ?? 5F 5E 5D 5B", 2, 0x380afc),  # chỉ số bước kế tiếp trong chuỗi đường đi (0 = không đi)
    "CHUOIDUONGDI": ("bien", "8D 82 ?? ?? ?? ?? 8B 55 18 50", 2, 0x1fc2b4),  # chuỗi đường đi toàn cục (ký tự hướng '1'..'8', bắt đầu từ chỉ số 1)
    "CUASOTUYCHONNHANVAT": ("bien", "85 DB 7C 44 8B 0D ?? ?? ?? ??", 6, 0x3a642c),  # cửa sổ tuỳ chọn nhân vật chính lần đầu
    "HAMGUILENH": ("goi", "E8 ?? ?? ?? ?? 83 C4 24 33 D2", 1, 0x95450),  # hàm gửi lệnh lên server (không xét mốc tự gửi lệnh)
    "HAMPHEDUYETCAULENH": ("ma", "56 57 74 11 A1 ?? ?? ?? ?? 55", 2, 0x95468),  # đoạn phê duyệt câu lệnh trong hàm gửi lệnh
    "HAMNHATVATPHAM": ("ma", "83 EC 1C 89 4C 24 04", 0, 0xb400),  # nhặt vật phẩm xung quanh
    "HAMCAPPHAT": ("goi", "75 45 68 18 08 00 00 E8 ?? ?? ?? ??", 8, 0x17dd0c),  # toán tử new của game
    "HAMKHOITAOTIMDUONG": ("goi", "74 3D 8B C8 E8 ?? ?? ?? ?? EB 36", 5, 0xceeb0),  # hàm khởi tạo cấu trúc tìm đường / bản đồ
    "HAMCLICKMANHINH": ("goi", "6A 00 53 55 8B CF ?? ?? ?? ?? ??", 7, 0x47790),  # xử lý click chuột tại điểm ảnh
    "HAMTIMDUONGCUCBO": ("ma", "C2 18 00 90 90 90 90 90 51", 8, 0xb0d60),  # tìm đường cục bộ (chuỗi hướng né vật cản)
    "HAMTANGCAPDO": ("goi", "57 52 E8 ?? ?? ?? ?? 5F 5E 5D", 3, 0x16c730),  # hàm được gọi ở chỗ vá chặn tăng cấp độ
    "VA_AUTOINGAME": ("ma", "C7 81 24 C9 AE 00 01 00 00 00", 0, 0x6ec9),  # NOP 10 byte khi tắt auto trong game
    "VA_GHIMUCTIEU2": ("ma", "8B 04 95 ?? ?? ?? ?? 83 B8 F0 00 00 00 03 0F 8D ?? ?? ?? ?? A3 ?? ?? ?? ??", 20, 0xa20f0),  # mov [MUCTIEUDANGCHON2], eax
    "VA_GHIIDMUCTIEU2": ("ma", "89 0D ?? ?? ?? ?? A3 ?? ?? ?? ?? 8B 50 20 89 15 ?? ?? ?? ?? E9 ?? ?? ?? ?? 33 C9", 0, 0xa20f8),  # mov [IDMUCTIEUDANGCHON2], ecx
    "VA_GHIMUCTIEU": ("ma", "A3 ?? ?? ?? ?? 8B 50 20 89 15 ?? ?? ?? ?? E9 ?? ?? ?? ?? 33 C9", 0, 0xa20fe),  # mov [MUCTIEUDANGCHON], eax
    "VA_GHIIDMUCTIEU": ("ma", "89 15 ?? ?? ?? ?? E9 ?? ?? ?? ?? 33 C9 8B 5E 02", 0, 0xa2106),  # mov [IDMUCTIEUDANGCHON], edx
    "VA_XOAIDMUCTIEU2": ("ma", "C3 C7 05 ?? ?? ?? ?? FF FF FF FF", 1, 0x9542b),  # mov [IDMUCTIEUDANGCHON2], 0
    "VA_XOAMUCTIEU": ("ma", "C7 05 ?? ?? ?? ?? 00 00 00 00 32 C0", 0, 0x95435),  # mov [MUCTIEUDANGCHON], 0
    "VA_LONGCLICK": ("ma", "C7 82 10 16 00 00 01 00 00 00", 0, 0x4993c),  # hằng số tại +6: 1 = bật long click
    "VA_CHUOTCHONMUCTIEUKYNANG": ("ma", "C7 86 A4 01 00 00 02 00 00 00", 0, 0x5416c),  # hằng số tại +6: 2 = trạng thái chuột chọn mục tiêu kỹ năng
    "VA_TANGCAPDO": ("ma", "8B 84 24 B4 00 00 00 52 50 E8 ?? ?? ?? ??", 9, 0x13fb61),  # call HAMTANGCAPDO (vá thành add esp, 8)
    "VA_HIEUUNGMULOA": ("ma", "C6 80 88 BC AE 00 01", 0, 0x4c0e, (0, 2)),  # byte tại +6 = 0 tắt hiệu ứng mù loà
    "VA_DICHUYEN": ("ma", "85 C0 7E 19 57 56", 2, 0x9be38),  # jle (7E) -> jmp (EB) để vô hiệu hoá di chuyển
    "VA_TUTHEDELAY1": ("ma", "83 F8 06 74 0A 83 F8 09 74 05 83 F8 07 75 16 C7 86 B8 11 00 00 0B 00 00 00", 15, 0x1afe3),  # mov [esi+0x11B8], 0x0B (tư thế delay sau tấn công)
    "VA_TUTHEDELAY2": ("ma", "3B C2 74 0A 83 F8 09 74 05 83 F8 07 75 16 C7 86 B8 11 00 00 0B 00 00 00", 14, 0x1b377),  # mov [esi+0x11B8], 0x0B (tư thế delay sau tấn công)
    "HOOK_TROCHUYEN": ("ma", "55 8B 8A D8 FD AD 00", 1, 0x5964),  # chỗ hook đọc nội dung trò chuyện (6 byte)
}
# --- KẾT THÚC CHỮ KÝ ---


class _DiaChi:
    # Giá trị dự phòng = địa chỉ ở bản game lúc sinh chữ ký; khoitao() thay bằng địa chỉ dò được
    def __init__(self):
        for ten, mucchuky in CHUKY.items():
            setattr(self, ten, mucchuky[3])
        self.dakhoitao = False
        self.loi = []


DC = _DiaChi()
_khoa = threading.Lock()


def docanhexe(duongdan):
    # Dựng ảnh bộ nhớ của exe từ file (các section đặt tại VirtualAddress). Trả về (ảnh, ImageBase, [(đầu, cuối) các vùng mã])
    with open(duongdan, "rb") as f:
        dulieu = f.read()
    pe = struct.unpack_from("<I", dulieu, 0x3C)[0]
    sosection, kichthuocopt = struct.unpack_from("<H", dulieu, pe + 6)[0], struct.unpack_from("<H", dulieu, pe + 20)[0]
    opt = pe + 24
    imagebase, sizeofimage = struct.unpack_from("<I", dulieu, opt + 28)[0], struct.unpack_from("<I", dulieu, opt + 56)[0]
    anh = bytearray(sizeofimage)
    vungma = []
    for i in range(sosection):
        s = opt + kichthuocopt + 40 * i
        virtualsize, virtualaddress, sizeofrawdata, pointertorawdata = struct.unpack_from("<IIII", dulieu, s + 8)
        characteristics = struct.unpack_from("<I", dulieu, s + 36)[0]
        doan = min(sizeofrawdata, virtualsize or sizeofrawdata)
        anh[virtualaddress:virtualaddress + doan] = dulieu[pointertorawdata:pointertorawdata + doan]
        if characteristics & 0x20000000:
            vungma.append((virtualaddress, virtualaddress + max(virtualsize, doan)))
    return bytes(anh), imagebase, vungma, hashlib.sha1(dulieu).hexdigest()


def chukythanhregex(chuky):
    # "8B 0D ?? ?? ?? ?? 85 C9" -> regex byte ("??" khớp 1 byte bất kỳ)
    return re.compile(b"".join(b"." if b == "??" else re.escape(bytes([int(b, 16)])) for b in chuky.split()), re.DOTALL)


def timkhop(anh, vungma, chuky):
    # Mọi vị trí khớp chữ ký trong các vùng mã
    bieuthuc = chukythanhregex(chuky)
    vitris = []
    for dau, cuoi in vungma:
        # khớp chồng nhau cũng tính (lookahead) để biết chữ ký có duy nhất thật không
        vitris += [dau + m.start() for m in re.finditer(b"(?=" + bieuthuc.pattern + b")", anh[dau:cuoi], re.DOTALL)]
    return vitris


def giaichuky(anh, imagebase, vungma, loai, chuky, lech, thutu = None):
    # Địa chỉ (tính từ base) theo chữ ký, None khi không khớp đúng 1 chỗ (hoặc đúng tổng số chỗ khi có thutu = (thứ tự, tổng số))
    vitris = timkhop(anh, vungma, chuky)
    if thutu is None:
        if len(vitris) != 1:
            return None, len(vitris)
        vitri = vitris[0] + lech
    else:
        if len(vitris) != thutu[1]:
            return None, len(vitris)
        vitri = sorted(vitris)[thutu[0]] + lech
    if loai == "bien":
        return struct.unpack_from("<I", anh, vitri)[0] - imagebase, len(vitris)
    if loai == "goi":
        return vitri + 4 + struct.unpack_from("<i", anh, vitri)[0], len(vitris)
    return vitri, len(vitris)


def khoitao(duongdanexe, inlog = print):
    # Dò toàn bộ địa chỉ cho xq.exe tại duongdanexe (1 lần cho cả chương trình; các cửa sổ game dùng chung 1 file exe)
    with _khoa:
        if DC.dakhoitao:
            return DC
        try:
            anh, imagebase, vungma, sha1 = docanhexe(duongdanexe)
        except Exception as e:
            inlog(f"[ĐỊA CHỈ] Không đọc được {duongdanexe}: {e} => dùng địa chỉ dự phòng")
            DC.dakhoitao = True
            return DC
        dem = {}
        try:
            with open(DUONGDANDEM, "r", encoding = "utf-8") as f:
                dem = json.load(f)
        except Exception:
            pass
        daluu = dem.get(sha1, {})
        ketqua, loi = {}, []
        for ten, mucchuky in CHUKY.items():
            loai, chuky, lech, duphong = mucchuky[:4]
            thutu = mucchuky[4] if len(mucchuky) > 4 else None
            if ten in daluu and daluu[ten].get("chuky") == chuky:
                ketqua[ten] = daluu[ten]["giatri"]
                continue
            giatri, sokhop = giaichuky(anh, imagebase, vungma, loai, chuky, lech, thutu)
            if giatri is None:
                loi.append(f"{ten} (khớp {sokhop} chỗ)")
                giatri = duphong
            else:
                daluu[ten] = {"chuky": chuky, "giatri": giatri}
            ketqua[ten] = giatri
        for ten, giatri in ketqua.items():
            setattr(DC, ten, giatri)
        DC.loi = loi
        DC.dakhoitao = True
        doi = [f"{ten} {hex(CHUKY[ten][3])} -> {hex(giatri)}" for ten, giatri in ketqua.items() if giatri != CHUKY[ten][3]]
        if loi:
            inlog(f"[ĐỊA CHỈ] {len(loi)} chữ ký không dò được, dùng địa chỉ dự phòng (có thể sai nếu game đã cập nhật): {', '.join(loi)}")
        if doi:
            inlog(f"[ĐỊA CHỈ] Địa chỉ khác bản lúc sinh chữ ký (game đã cập nhật?): {'; '.join(doi)}")
        try:
            dem[sha1] = daluu
            os.makedirs(os.path.dirname(DUONGDANDEM), exist_ok = True)
            with open(DUONGDANDEM, "w", encoding = "utf-8") as f:
                json.dump(dem, f, ensure_ascii = False, indent = 1)
        except Exception:
            pass
        return DC
