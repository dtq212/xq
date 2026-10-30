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
#   "hang": offset trong cấu trúc (hằng số 32 bit nằm trong lệnh, vd [eax+0x1178]) = số đọc tại vị trí khớp + lệch. Chữ ký là DANH SÁCH
#           [(chữ ký, lệch), ...] lấy từ các hàm khác nhau và phải ra cùng 1 giá trị (cùng con số có thể là offset của cấu trúc khác:
#           lệch nhau thì báo lỗi, không đoán)
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
    "HOOK_TINHETHONG": ("ma", "50 55 8B 89 64 FD AD 00", 2, 0x2b63),  # chỗ hook gói 0x3E chỉ in vào khung tin hệ thống (trả lời "desc user"), 6 byte
    "TG_TIMDUONG": ("hang", [('33 F6 39 B2 ?? ?? ?? ?? 75 42', 4), ('8B 1D ?? ?? ?? ?? 8B 93 ?? ?? ?? ?? 3B D6', 8), ('C7 05 ?? ?? ?? ?? 00 00 00 00 8B 96 ?? ?? ?? ??', 12)], None, 0xadfdec),  # cấu trúc tìm đường / bản đồ
    "TG_HANHTRANG": ("hang", [('8A 55 06 8B 0D ?? ?? ?? ?? 52 50 8B 89 ?? ?? ?? ??', 13), ('8B 88 ?? ?? ?? ?? 89 5C 24 18', 2), ('8A 55 02 51 8B 88 ?? ?? ?? ??', 6)], None, 0xadfd78),  # hành trang (id, tên, số lượng, mô tả vật phẩm)
    "TG_KYNANG": ("hang", [('83 C4 1C 8B 15 ?? ?? ?? ?? 8B 82 ?? ?? ?? ??', 11), ('83 C5 04 F3 AB 8B 15 ?? ?? ?? ?? 68 F3 01 00 00 55 8B 82 ?? ?? ?? ??', 19), ('8B B9 ?? ?? ?? ?? 8B 84 2F 60 FF FF FF', 2)], None, 0xadfe18),  # bảng kỹ năng
    "TG_TUIHANHTRANG": ("hang", [('8B 88 ?? ?? ?? ?? 85 C9 75 4D 68 F8 04 00 00', 2), ('74 58 40 83 C1 04 83 F8 6A 7C F3 8B 96 ?? ?? ?? ??', 13), ('FF 52 04 A1 ?? ?? ?? ?? 8B 88 ?? ?? ?? ?? 8B 11', 10)], None, 0xadfe0c),  # túi hành trang (số ô mở mỗi túi)
    "TG_MOCTUGUILENH": ("hang", [('8B 90 58 FC AD 00 89 90 ?? ?? ?? ??', 8), ('3B 82 ?? ?? ?? ?? 0F 86 ?? ?? ?? ?? 8B 0D ?? ?? ?? ?? 8B 06', 2), ('FF D5 8B 0D ?? ?? ?? ?? 3B 81 ?? ?? ?? ??', 10)], None, 0xadfc5c),  # mốc client được tự gửi lệnh (timeGetTime)
    "TG_TIMDUONGCUCBO": ("hang", [('8B 5C 24 10 B9 19 00 00 00 33 C0 8D BC 24 48 01 00 00 F3 AB 8B 83 ?? ?? ?? ??', 22), ('E9 ?? ?? ?? ?? B9 19 00 00 00 33 C0 8D BC 24 48 01 00 00 F3 AB 8B 83 ?? ?? ?? ??', 23), ('8B 81 ?? ?? ?? ?? 85 C0 75 3E', 2)], None, 0xae1178),  # đối tượng tìm đường cục bộ
    "TG_VANKHI": ("hang", [('8B 81 ?? ?? ?? ?? 85 C0 75 51 68 00 01 00 00', 2), ('8B 83 ?? ?? ?? ?? 33 FF 3B C7', 2), ('74 1C 8B 8B ?? ?? ?? ?? 3B CE', 4)], None, 0xadfde8),  # đối tượng vận khí
    "TG_AUTOINGAME": ("hang", [('8B 81 ?? ?? ?? ?? 85 C0 0F ?? ?? ?? ?? ?? 6A 12', 2), ('7C D8 A1 ?? ?? ?? ?? C7 80 ?? ?? ?? ?? 00 00 00 00', 9), ('C6 44 24 13 01 39 B3 ?? ?? ?? ??', 7)], None, 0xaec924),  # cờ bật auto trong game
    "TG_CUASOYESNO": ("hang", [('8B 88 ?? ?? ?? ?? 85 C9 75 4D 68 70 02 00 00', 2), ('8B 82 ?? ?? ?? ?? 85 C0 75 51 68 70 02 00 00', 2), ('89 9D ?? ?? ?? ?? 89 9D 18 FE AD 00', 2)], None, 0xadfe10),  # cửa sổ yes / no
    "TG_ENTER": ("hang", [('75 0D 8B 90 ?? ?? ?? ?? C6 82 40 81 00 00 00', 4), ('85 C0 74 36 8B 80 ?? ?? ?? ??', 6), ('8D 0C 82 E8 ?? ?? ?? ?? E9 ?? ?? ?? ?? 8B 8A ?? ?? ?? ??', 15)], None, 0xadfd60),  # khung chat (Enter)
    "TG_TROCHUYEN": ("hang", [('8B 81 ?? ?? ?? ?? 85 C0 0F ?? ?? ?? ?? ?? 68 B8 01 00 00', 2), ('8B 81 ?? ?? ?? ?? 85 C0 75 4D 68 B8 01 00 00', 2), ('55 8B 88 64 FD AD 00 E8 ?? ?? ?? ?? 8B 0D ?? ?? ?? ?? 8B 81 ?? ?? ?? ??', 20)], None, 0xadfdd8),  # nội dung trò chuyện
    "TG_GIAODIEN": ("hang", [('89 88 84 00 00 00 A1 ?? ?? ?? ?? 8B 88 ?? ?? ?? ??', 13), ('8B 80 ?? ?? ?? ?? C7 80 A4 01 00 00 31 00 00 00', 2), ('8B 80 ?? ?? ?? ?? 89 B0 A4 01 00 00', 2)], None, 0xadfda8),  # giao diện chính (con trỏ chuột...)
    "TG_CUASOXACNHAN": ("hang", [('8B 82 ?? ?? ?? ?? 85 C0 75 51 68 30 03 00 00', 2), ('8B 83 ?? ?? ?? ?? 8B B8 14 03 00 00', 2), ('89 9D 88 FD AD 00 89 9D ?? ?? ?? ??', 8)], None, 0xadfd8c),  # cửa sổ xác nhận
    "TG_THONGBAO": ("hang", [('8B 88 ?? ?? ?? ?? E8 ?? ?? ?? ?? 8B 15 ?? ?? ?? ?? B9 01 00 00 00', 2), ('8D 75 02 56 8B 88 ?? ?? ?? ??', 6), ('3B FD 5D 7E 19 8B 8B ?? ?? ?? ??', 7)], None, 0xadfd70),  # thông báo gần nhất
    "TG_NHOM": ("hang", [('8B 75 02 8B 81 ?? ?? ?? ?? 85 C0', 5), ('8B 0D ?? ?? ?? ?? 8B 81 ?? ?? ?? ?? 85 C0 75 42', 8), ('8B 83 ?? ?? ?? ?? 8B 55 07 8B 7D 03', 2)], None, 0xadfda4),  # thành viên nhóm
    "TG_MONPHAI": ("hang", [('8B 8A 24 FE AD 00 E8 ?? ?? ?? ?? E9 ?? ?? ?? ?? A1 ?? ?? ?? ?? 8B 88 ?? ?? ?? ??', 23), ('8B 80 ?? ?? ?? ?? 85 C0 74 48', 2), ('8B 80 ?? ?? ?? ?? 8B 88 00 E3 02 00 8B 94 30 A8 C5 01 00', 2)], None, 0xadfddc),  # môn phái
    "TG_MAUPK": ("hang", [('FF D6 33 C0 89 9D ?? ?? ?? ??', 6), ('83 C4 0C 89 9A ?? ?? ?? ?? E9 ?? ?? ?? ??', 5), ('33 F6 8A 85 ?? ?? ?? ?? 84 C0', 4)], None, 0xaed6cc),  # màu PK
    "TG_CHUCNANGMORONG": ("hang", [('83 C4 04 BE ?? ?? ?? ?? 8B 2D ?? ?? ?? ??', 4), ('83 C4 04 BE ?? ?? ?? ?? FF D7', 4)], None, 0xaebc0c),  # chức năng mở rộng
    "TG_CUASOTUYCHON": ("hang", [('33 FF 39 B9 ?? ?? ?? ?? 75 4D', 4), ('8B 8E ?? ?? ?? ?? 83 C4 04 85 C9', 2), ('8B 83 ?? ?? ?? ?? 83 C4 14 85 C0', 2)], None, 0xadfd74),  # cửa sổ tuỳ chọn
    "TG_KHO": ("hang", [('8B 88 ?? ?? ?? ?? 8B FA 85 C9', 2), ('8B 88 ?? ?? ?? ?? 85 C9 75 56 68 70 B2 01 00', 2), ('89 9D 84 FD AD 00 89 9D ?? ?? ?? ??', 8)], None, 0xadfd88),  # kho (Quản Khố): rương đang mở
    "TG_CUAHANG": ("hang", [('8B 88 ?? ?? ?? ?? 85 C9 75 56 68 10 8F 00 00', 2), ('8B 82 ?? ?? ?? ?? 8B F9 85 C0', 2), ('8B 91 ?? ?? ?? ?? 8D 4C 24 20', 2)], None, 0xadfd80),  # cửa hàng NPC đang / vừa mở (id NPC +0x110, hàng +0x7D78 mỗi món 0x58: ô +4, giá +8, tên +0x12)
    "TG_NHIEMVU": ("hang", [('8B 8A CC FD AD 00 E8 ?? ?? ?? ?? E9 ?? ?? ?? ?? A1 ?? ?? ?? ?? 8B 88 ?? ?? ?? ??', 23), ('89 9D ?? ?? ?? ?? 89 9D B4 FD AD 00', 2), ('8B 88 ?? ?? ?? ?? 85 C9 75 4B 68 AC D5 01 00', 2)], None, 0xadfdac),  # cửa sổ nhiệm vụ (tên mục +0x90, mô tả +0x860, mỗi mục 4 byte con trỏ)
    "TD_DICH": ("hang", [('8B 91 38 C5 37 00 8B 81 ?? ?? ?? ??', 8), ('8B 82 EC FD AD 00 89 98 ?? ?? ?? ??', 8), ('89 B0 ?? ?? ?? ?? 8B 4C 24 24', 2)], None, 0x37c534),  # đích tìm đường x (y ở + 4)
    "TD_BANDO": ("hang", [('83 BA ?? ?? ?? ?? FF 74 62 A1 ?? ?? ?? ??', 2), ('C7 81 ?? ?? ?? ?? FF FF FF FF A1 ?? ?? ?? ??', 2), ('C7 82 ?? ?? ?? ?? FF FF FF FF E9 ?? ?? ?? ??', 2)], None, 0x37c85c),  # bản đồ đích tìm đường (-1 = không đi)
    "KN_KICHTHUOC": ("hang", [('05 ?? ?? ?? ?? 4A 75 D9 8B 15 ?? ?? ?? ?? 8B 4C 24 14', 1), ('39 18 74 79 46 05 ?? ?? ?? ??', 6), ('39 31 74 56 40 81 C1 ?? ?? ?? ??', 7)], None, 0x224),  # kích thước 1 ô kỹ năng
    "KN_ID": ("hang", [('81 ?? ?? ?? ?? ?? 33 F6 8B C1 39 18', 2), ('8D 8C ?? ?? ?? ?? ?? 8B 74 24 14 39 31 74 56', 3), ('8D 9C ?? ?? ?? ?? ?? 81 FF 3E 08 00 00', 3)], None, 0x6830),  # id kỹ năng trong ô
    "KN_HOICHIEU": ("hang", [('0F 8E ?? ?? ?? ?? 8B ?? ?? ?? ?? ?? 85 C0 0F 85 ?? ?? ?? ??', 8), ('8B 8C ?? ?? ?? ?? ?? 85 C9 8D 44 95 00 0F 86 ?? ?? ?? ??', 3), ('8B 84 ?? ?? ?? ?? ?? 85 C0 76 40', 3)], None, 0x6a4c),  # thời gian hồi chiêu còn lại trong ô
    "HT_TEN": ("hang", [('89 44 24 14 8D AA ?? ?? ?? ??', 6), ('C1 E2 05 8D B4 02 ?? ?? ?? ??', 6), ('89 9E ?? ?? ?? ?? F3 AB 53 53', 2)], None, 0x1a8),  # tên vật phẩm (mỗi ô 0x20)
    "HT_MOTA": ("hang", [('8D 94 16 ?? ?? ?? ?? 52 FF D3', 3), ('83 EC 0C 8D 81 ?? ?? ?? ?? 53', 5), ('8D 0C 89 8D 94 8B ?? ?? ?? ??', 6)], None, 0xf52),  # mô tả vật phẩm (mỗi ô 0x44C)
    "HT_KICHTHUOCMOTA": ("hang", [('3B C3 74 07 68 ?? ?? ?? ?? EB 05', 5), ('81 C3 ?? ?? ?? ?? 81 FA 54 01 00 00', 2), ('81 C3 ?? ?? ?? ?? 81 FF 54 01 00 00', 2)], None, 0x44c),  # kích thước mô tả 1 ô
    "HT_SOLUONG": ("hang", [('89 5C 24 18 89 84 99 ?? ?? ?? ??', 7), ('8B 94 88 ?? ?? ?? ?? 89 54 24 18', 3), ('8D 91 ?? ?? ?? ?? 89 44 24 14', 2)], None, 0x1d6cc),  # số lượng vật phẩm
    "HT_NHOMHOI": ("hang", [('0F BE 8C 11 ?? ?? ?? ?? 8B 90 18 FE AD 00', 4), ('40 88 8C 37 ?? ?? ?? ?? 33 C9', 4), ('89 0C 83 0F BE 8C 2B ?? ?? ?? ??', 7)], None, 0xee8),  # nhóm thời gian hồi của vật phẩm (1 byte mỗi ô)
    "HT_THOILUONGHOI": ("hang", [('7C E4 EB 1C 8B 8C 86 ?? ?? ?? ??', 7), ('8D 74 24 14 F3 A5 8B 94 83 ?? ?? ?? ??', 9), ('56 8B B4 81 ?? ?? ?? ?? 33 D2', 4)], None, 0x1df80),  # thời lượng hồi của ô (giây, 0 = không hồi)
    "HT_BATDAUHOI": ("hang", [('89 8C BE 80 DF 01 00 8B 94 86 ?? ?? ?? ??', 10), ('89 8C 83 80 DF 01 00 8B 94 83 ?? ?? ?? ??', 10), ('8B 84 81 ?? ?? ?? ?? C2 04 00 90 90 90 90 83 EC 0C', 3)], None, 0x1e128),  # thời điểm bắt đầu hồi của ô (timeGetTime)
    "KHO_TEN": ("hang", [('75 03 89 45 28 8D 85 ?? ?? ?? ??', 7), ('8D 96 ?? ?? ?? ?? 2B C6 89 4C 24 14', 2), ('6A 1F 56 8D 9C 08 ?? ?? ?? ??', 6)], None, 0x1a118),  # tên vật phẩm ô rương đang mở (mỗi ô 0x20)
    "KHO_SOLUONG": ("hang", [('89 4C 24 10 8D 95 ?? ?? ?? ??', 6), ('8D BE ?? ?? ?? ?? F3 AB B9 60 00 00 00', 2)], None, 0x1ad18),  # số lượng vật phẩm ô rương (4 byte, đồ không chồng được = 0)
    "KHO_MA": ("hang", [('8D BE ?? ?? ?? ?? 8D 96 18 A1 01 00', 2), ('8D BE ?? ?? ?? ?? F3 AB ?? ?? ?? ?? 00 8B FB', 2)], None, 0x1ae98),  # mã loại vật phẩm ô rương (4 byte)
    "KHO_RUONGMO": ("hang", [('89 9D 04 B2 01 00 89 9D ?? ?? ?? ??', 8), ('8B 88 ?? ?? ?? ?? 83 C2 05 3B CA', 2), ('03 D0 8D 04 11 8B 8E ?? ?? ?? ??', 7)], None, 0x1b1f8),  # rương đang mở (từ 0)
    "KHO_SORUONG": ("hang", [('89 9D F8 B1 01 00 C7 85 ?? ?? ?? ?? 01 00 00 00', 8), ('3B C1 0F 84 ?? ?? ?? ?? 3B 86 ?? ?? ?? ??', 10), ('03 D0 8B 86 ?? ?? ?? ?? 03 D1', 4)], None, 0x1b1fc),  # số rương dùng được
    "KHO_DANGHIEN": ("hang", [('8B 8D ?? ?? ?? ?? 81 C5 DC 02 00 00', 2), ('3B C1 88 9D ?? ?? ?? ?? 89 5D 14', 4), ('8A 86 ?? ?? ?? ?? 84 C0 75 76', 2)], None, 0x304),  # cờ cửa sổ kho đang hiện (1 byte)
    "NV_TUTHE": ("hang", [('8B 86 ?? ?? ?? ?? 83 F8 01 74 16', 2), ('8B 86 ?? ?? ?? ?? 83 F8 01 74 09', 2), ('83 BE ?? ?? ?? ?? 03 74 24 83 FF 02', 2)], None, 0x1178),  # tư thế (1 đứng, 2 đi, 6 đánh, 9 phép)
    "NV_TEN": ("hang", [('51 52 8D 8E ?? ?? ?? ?? 50 51', 4), ('8D 96 ?? ?? ?? ?? 51 52 8D 84 24 24 02 00 00', 2), ('8D B2 ?? ?? ?? ?? 2B F9 8B C1', 2)], None, 0x10ac),  # tên đối tượng
    "NV_DANHHIEU": ("hang", [('B9 0F 00 00 00 8D BA ?? ?? ?? ??', 7), ('E8 ?? ?? ?? ?? 8A 8B ?? ?? ?? ?? 8D 83 34 11 00 00', 7), ('C2 04 00 90 90 8D 81 ?? ?? ?? ??', 7)], None, 0x1134),  # danh hiệu hiện trên tên (NPC cửa hàng các nước: "Chủ Tiệm Vũ Khí")
    "NV_PHANTRAMMAU": ("hang", [('C7 82 ?? ?? ?? ?? 32 00 00 00 F3 AB', 2), ('8B AD ?? ?? ?? ?? 8B B4 24 D8 01 00 00', 2), ('85 C0 0F 85 ?? ?? ?? ?? 8A 43 28 8B 8B ?? ?? ?? ??', 13)], None, 0x1410),  # % máu / 2
    "NV_CHET": ("hang", [('75 3F 8A 86 ?? ?? ?? ?? 84 C0', 4), ('75 26 8A 91 ?? ?? ?? ?? 84 D2', 4), ('85 F6 0F 84 ?? ?? ?? ?? 8A 86 ?? ?? ?? ??', 10)], None, 0x1424),  # cờ đã chết
    "NV_SOBAY": ("hang", [('89 5A 24 B9 0A 00 00 00 33 C0 8D BA ?? ?? ?? ??', 12), ('33 D2 33 FF 8D 81 ?? ?? ?? ??', 6), ('8B 44 24 10 8B 8C 82 ?? ?? ?? ??', 7)], None, 0x11c4),  # số máu bay (10 ô)
    "NV_HIEUUNG": ("hang", [('0F BF F1 8D 8F ?? ?? ?? ?? 8B 19', 5), ('0F BF FB 8D 8E ?? ?? ?? ?? 8B 19', 5), ('8A 88 ?? ?? ?? ?? 84 C9 74 6D', 2)], None, 0x1638),  # danh sách hiệu ứng
    "NV_KICHTHUOCHIEUUNG": ("hang", [('8B 88 ?? ?? ?? ?? 56 89 48 20', 2), ('3B 34 9D ?? ?? ?? ?? 74 10 40 81 C1 ?? ?? ?? ??', 12), ('3B 3C 9D ?? ?? ?? ?? 74 10 40 81 C1 ?? ?? ?? ??', 12)], None, 0x13c),  # kích thước 1 hiệu ứng
    "NV_HUONGMAT": ("hang", [('89 9A ?? ?? ?? ?? 89 9A 08 14 00 00', 2), ('74 40 0F BF 50 06 0F AF 96 ?? ?? ?? ?? 8B BE FC 13 00 00', 9), ('0F BF 4F 06 0F AF 8E ?? ?? ?? ??', 7)], None, 0x13f8),  # hướng mặt
    "NV_HOATANH": ("hang", [('59 C2 1C 00 8B 96 ?? ?? ?? ??', 6), ('3B 83 5C FC AD 00 76 76 8B 85 ?? ?? ?? ??', 10), ('8B 85 A4 10 00 00 8B 95 ?? ?? ?? ??', 8)], None, 0x10a0),  # chỉ số hàng hoạt ảnh (hiện tại, + 4 cuối)
    "NV_ANTHAN": ("hang", [('8A 8E ?? ?? ?? ?? 84 C9 0F 85 ?? ?? ?? ?? 83 F8 03', 2), ('88 9A 2C 16 00 00 88 9A ?? ?? ?? ??', 8), ('89 8E 98 12 00 00 8A 86 ?? ?? ?? ??', 8)], None, 0x162d),  # ẩn thân
    "NV_VUKHI": ("hang", [('89 9A ?? ?? ?? ?? 89 9A 7C 11 00 00', 2), ('89 96 ?? ?? ?? ?? 83 BE F0 00 00 00 04 0F 84 ?? ?? ?? ?? A1 ?? ?? ?? ?? 3B C3', 2), ('8B 86 ?? ?? ?? ?? 83 F8 01 89 44 24 7C', 2)], None, 0x1184),  # id vũ khí
    "NV_NGOAITRANG": ("hang", [('89 9A 7C 11 00 00 89 9A ?? ?? ?? ??', 8), ('8B 86 ?? ?? ?? ?? BD 64 00 00 00', 2), ('75 55 A1 ?? ?? ?? ?? 89 86 ?? ?? ?? ?? 8B 0D ?? ?? ?? ??', 9)], None, 0x1174),  # id ngoại trang
    "NV_CANH": ("hang", [('89 9A ?? ?? ?? ?? 89 9A AC 11 00 00', 2), ('7E 3F 8B 86 ?? ?? ?? ?? 3B C5', 4), ('8B A9 ?? ?? ?? ?? BA 07 00 00 00', 2)], None, 0x119c),  # id cánh (2 số)
    "KDK_SINHLUC": ("hang", [('8D BE 8C 15 00 00 F3 AB B9 18 00 00 00 8D BE ?? ?? ?? ??', 15), ('85 C0 8B 8E ?? ?? ?? ?? 89 4C 24 10', 4), ('8B 90 30 15 00 00 8B 80 ?? ?? ?? ??', 8)], None, 0x152c),  # sinh lực
    "KDK_SINHLUCTOIDA": ("hang", [('8D BA 30 14 00 00 89 9A ?? ?? ?? ??', 8), ('8B 8C 24 60 01 00 00 8B 81 ?? ?? ?? ??', 9), ('8B 86 ?? ?? ?? ?? 3B C3 7E 23', 2)], None, 0x1530),  # sinh lực tối đa
    "KDK_NOILUC": ("hang", [('8B 91 ?? ?? ?? ?? 8B C2 C1 E0 05 03 C2 99 F7 B9 38 15 00 00', 2), ('2B C2 8B 91 ?? ?? ?? ?? D1 F8', 4), ('EB 03 83 C1 10 8B 95 ?? ?? ?? ??', 7)], None, 0x1534),  # nội lực
    "KDK_NOILUCTOIDA": ("hang", [('E9 ?? ?? ?? ?? 8B 81 ?? ?? ?? ?? 85 C0 75 10', 7), ('8B 91 ?? ?? ?? ?? 8D 04 D5 00 00 00 00', 2), ('8B 85 ?? ?? ?? ?? 8B 54 24 1C', 2)], None, 0x1538),  # nội lực tối đa
    "KDK_NGUYENKHI": ("hang", [('89 9A ?? ?? ?? ?? 89 9A 00 16 00 00', 2), ('8B BE ?? ?? ?? ?? 8B AE 5C 15 00 00', 2), ('8B 91 ?? ?? ?? ?? 8B C2 C1 E0 05 03 C2 99 F7 B9 64 15 00 00', 2)], None, 0x1560),  # nguyên khí
    "KDK_DIEMPK": ("hang", [('8B 55 03 89 90 ?? ?? ?? ?? E9 ?? ?? ?? ?? 33 C0', 5), ('89 9A ?? ?? ?? ?? 89 5A 14 89 5A 0C', 2), ('8B 86 ?? ?? ?? ?? 3B C7 0F 85 ?? ?? ?? ??', 2)], None, 0x1568),  # điểm PK
    "KDK_KINHNGHIEM": ("hang", [('8B 88 C4 15 00 00 8B 80 ?? ?? ?? ??', 8), ('89 9E 98 15 00 00 89 9E ?? ?? ?? ??', 8), ('83 C4 0C 39 90 ?? ?? ?? ?? 72 21', 5)], None, 0x159c),  # kinh nghiệm (tích luỹ khi chặn tăng cấp, giảm khi lên cấp)
    "KDK_NGANLUONG": ("hang", [('8B 89 00 01 00 00 8B 90 ?? ?? ?? ??', 8), ('8B BE ?? ?? ?? ?? 03 C3 3B C7', 2), ('8B 80 ?? ?? ?? ?? 3B C5 75 04', 2)], None, 0x15a4),  # ngân lượng
    "KDK_THELUC": ("hang", [('89 90 ?? ?? ?? ?? 8B 0D ?? ?? ?? ?? 8B 81 A8 15 00 00', 2), ('8A 4D 23 89 8A ?? ?? ?? ?? 8B 0D ?? ?? ?? ??', 5), ('8D 54 24 50 8B 88 ?? ?? ?? ?? 51', 6)], None, 0x15a8),  # thể lực
    "KDK_TIENGUI": ("hang", [('88 9E 25 16 00 00 89 9E ?? ?? ?? ??', 8), ('8B 82 ?? ?? ?? ?? 8B 89 04 FE AD 00 50 E8 ?? ?? ?? ?? 8B 15 ?? ?? ?? ?? 6A 01 8B 8A 04 FE AD 00 E8 ?? ?? ?? ??', 2), ('8B 91 ?? ?? ?? ?? 6A 64 50 52', 2)], None, 0x15ac),  # tiền gửi trong kho
    "KDK_CAPDO": ("hang", [('8D 82 ?? ?? ?? ?? B9 0A 00 00 00', 2), ('01 96 ?? ?? ?? ?? EB 65 83 F8 01', 2), ('8B 96 84 15 00 00 89 94 8E ?? ?? ?? ??', 9)], None, 0x15b0),  # cấp độ
    "KDK_BANDO": ("hang", [('8B 91 ?? ?? ?? ?? 8B 88 EC FD AD 00', 2), ('8B 4C 24 30 83 C4 0C 89 8A ?? ?? ?? ??', 9), ('8B 93 ?? ?? ?? ?? 89 94 1E E4 01 00 00', 2)], None, 0x15f4),  # bản đồ hiện tại
    "KDK_MUCTIEUTANCONG": ("hang", [('8B 41 20 8B 0D ?? ?? ?? ?? 89 81 ?? ?? ?? ??', 11), ('8B 0D ?? ?? ?? ?? 8B 46 20 89 81 ?? ?? ?? ??', 11), ('89 8A ?? ?? ?? ?? A1 ?? ?? ?? ?? 89 B0 04 16 00 00 8B 0D ?? ?? ?? ?? A1 ?? ?? ?? ?? 8B 91 A4 10 00 00 89 90 14 16 00 00 8B 0D ?? ?? ?? ?? A1 ?? ?? ?? ?? 8B 51 18 89 90 18 16 00 00 8B 0D ?? ?? ?? ?? A1 ?? ?? ?? ?? 8B 51 1C 8D 8C 24 B0 01 00 00', 2)], None, 0x15f8),  # id mục tiêu tấn công của client (+ 0xC con trỏ)
    "KDK_DICHCLICK": ("hang", [('89 81 ?? ?? ?? ?? A1 ?? ?? ?? ?? 8B 56 04', 2), ('8B B8 ?? ?? ?? ?? 3B FE 0F 8E ?? ?? ?? ??', 2), ('B9 19 00 00 00 89 9A ?? ?? ?? ??', 7)], None, 0x1608),  # đích click chuột (x, y)
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
    if loai == "hang":
        return struct.unpack_from("<I", anh, vitri)[0], len(vitris)
    return vitri, len(vitris)


def giaimuc(anh, imagebase, vungma, mucchuky):
    # Giải 1 mục của CHUKY. Trả về (giá trị hoặc None, mô tả lỗi)
    loai, chuky, lech = mucchuky[:3]
    thutu = mucchuky[4] if len(mucchuky) > 4 else None
    if loai != "hang":
        giatri, sokhop = giaichuky(anh, imagebase, vungma, loai, chuky, lech, thutu)
        return giatri, (None if giatri is not None else f"khớp {sokhop} chỗ")
    giatris = []
    for ck, lc in chuky:
        giatri, sokhop = giaichuky(anh, imagebase, vungma, loai, ck, lc)
        if giatri is not None:
            giatris.append(giatri)
    if not giatris:
        return None, "không chữ ký nào khớp"
    if len(set(giatris)) > 1:
        return None, "các chữ ký ra giá trị khác nhau " + "/".join(hex(x) for x in giatris)
    return giatris[0], None


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
            duphong = mucchuky[3]
            khoa = json.dumps(mucchuky[1], ensure_ascii = False)
            if ten in daluu and daluu[ten].get("chuky") == khoa:
                ketqua[ten] = daluu[ten]["giatri"]
                continue
            giatri, mota = giaimuc(anh, imagebase, vungma, mucchuky)
            if giatri is None:
                loi.append(f"{ten} ({mota})")
                giatri = duphong
            else:
                daluu[ten] = {"chuky": khoa, "giatri": giatri}
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
