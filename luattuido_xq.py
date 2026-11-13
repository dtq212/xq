# Luật túi đồ: _internal/luattuido.json (sửa ở tab "Hành trang" trên bảng điều khiển, hoặc bằng tay; bot tự đọc lại khi file đổi).
# Dùng chung mọi nhân vật trên máy; chưa có file thì tạo từ LUATMACDINH / MUABUMACDINH (luật viết cứng trước đây, chuyển sang đây 2026-10-29).
#   "luat": hành động (Giữ / Bán / Vứt): xét từ trên xuống, luật ĐẦU TIÊN khớp quyết định. Mỗi luật: {"bat": true,
#           "hanhdong": "giu" | "ban" | "vut", "ten": [tên đúng...], "tenchua": [tên có chứa...], "loai": [loại trong ［］ có chứa...],
#           "mota": [mô tả có chứa...], "ghichu": ...,
#           "is_bao": true = 📣 nhặt được món khớp luật này thì báo về Telegram kèm ảnh chụp (đồ hiếm), xem thongke_xq; xét riêng với
#           hành động: có luật bật nào khớp là báo, thứ tự không quan trọng}.
#           Mỗi điều kiện là danh sách, khớp 1 giá trị bất kỳ là được; để trống là không xét; có nhiều điều kiện thì phải khớp hết;
#           so không phân biệt hoa thường. Khi về bán rác, món không khớp luật nào thì BÁN (giữ món gì thì phải có luật Giữ).
#   "catkho": bảng Cất kho (tactu_catkho_xq), xét riêng với "luat": món khớp luật bật đầu tiên ở đây thì không bán / không vứt, đem gửi
#           Quản Khố ở Tân Thủ Thôn (sau bán rác nếu "is_catkhosauban", hoặc bấm Cất kho ngay / Telegram). Mỗi luật: {"bat": true,
#           "ten" / "tenchua" / "loai" / "mota" như "luat", "ruong": 0 = tự động (rương còn chỗ) hoặc số rương (từ 1), "giulai": số cái
#           chừa lại trong túi (tính theo tên món), "ghichu": ...}.
#           Luật cũ trong "luat" có "hanhdong": "catkho" (chuyển hẳn sang) hoặc "is_catkho": true (chép sang, luật cũ giữ hành động) tự
#           chuyển vào đây khi file chưa có "catkho"
#   "muabu": đứng gần NPC (hoặc Trân Bảo Khố, mua bằng KNB ở đâu cũng được) mà còn ít hơn "duoi" món (đếm cả các chồng) thì mua cho đủ "muatoi". Mỗi mục: {"bat": true,
#           "vatpham": tên (trong túi), "tencuahang": tên trong cửa hàng nếu khác ("" = như "vatpham"), "npc": tên / danh hiệu NPC bán,
#           "duoi": N, "muatoi": M, (ô / giá bot tự tra theo tên trong cửa hàng; "o" / "dongia" của bản cũ bỏ đi)
#           "thapnhat": còn <= chừng này (mặc định THAPNHATMACDINH) thì đang farm (bật Tự động về bán rác) cũng chạy về Tân Thủ Thôn mua
#           "xepchong": số món tối đa 1 ô chồng được (mặc định XEPCHONGMACDINH): mỗi lệnh buy mua không quá chừng này,
#           thiếu nhiều hơn thì gửi nhiều lệnh (vd Bùa Giấy chồng 5000, mua cho đủ 10000 thì 2 lệnh 5000)
#           "monphai": "" = mọi môn phái hoặc "maoson", "vanmongcoc"..., "chikhi": "" = luôn, "trieuhoibaothu" = chỉ khi bật triệu hồi
#           bảo thú giang hồ}. Mua lần lượt từ trên xuống trong số ngân lượng đang có, chừa NGANLUONGGIULAI
#   "nhat": nhặt vật phẩm dưới đất (tactu_vatpham_xq.action_tudongnhatvatpham): xét từ trên xuống, luật ĐẦU TIÊN khớp quyết định.
#           Mỗi luật: {"bat": true, "hanhdong": "nhat" | "uutien" | "khongnhat", "ten": [tên đúng...], "tenchua": [tên có chứa...],
#           "chibanrac": true = chỉ xét khi bật Tự động về bán rác, "ghichu": ...}. Dưới đất chỉ biết tên nên không có điều kiện loại /
#           mô tả; "tenchua" giữ khoảng trắng đầu / cuối (" Y" khác "Y"). Ưu tiên: nhặt trước mọi việc khác (tấn công, theo nhóm...),
#           vẫn nhặt khi đang theo sau. Không khớp luật nào thì còn xét đồ sư môn, phẩm chất (màu tên). Chuyển từ VATPHAMKHONGNHATs /
#           VATPHAMUUTIENNHATs / VATPHAMTUDONGNHATs / VATPHAMTUDONGNHATFARMs ở hangso_xq (2026-11-01), file cũ chưa có "nhat" thì lấy
#           NHATMACDINH
#   "dung": tự động sử dụng vật phẩm (tactu_vatpham_xq.action_tudongsudungvatpham, cần bật ô "Tự động sử dụng vật phẩm"): MỌI luật bật
#           đều được xét mỗi lượt (không phải luật đầu tiên). Luật đủ điều kiện thì dùng món đầu tiên trong "vatpham" còn trong túi và đã
#           hết thời gian hồi. Mỗi luật: {"bat": true, "vatpham": [tên đúng, ưu tiên từ trên], "sinhluc": dùng khi sinh lực < x% (0 = không
#           xét), "matsinhluc": và mất ít nhất N sinh lực, "noiluc" / "matnoiluc" như trên cho nội lực, "theluc": thể lực ≤ N (-1 = không
#           xét), "hieuung": điều kiện hiệu ứng (TENHIEUUNGDUNG), "noi": nơi dùng (TENNOIDUNG), "monphai": "" = mọi môn phái,
#           "chikhidanh": chỉ khi bật Tự động sử dụng kỹ năng, "khongphobanrieng": không dùng ở Lăng Ly Sơn / Phong Yêu Kính / Tập Kích,
#           "giancach": tối thiểu chừng này giây giữa 2 lần dùng của luật, "ghichu": ...}. Có nhiều điều kiện thì phải đủ hết.
#           File cũ chưa có "dung" thì lấy DUNGMACDINH (đúng các điều kiện viết cứng trước đây, chuyển sang 2026-11-14).
#           Pháp bảo theo sinh lực, An Xá Phù, bảo thú vật phẩm vẫn viết cứng (có tuỳ chọn riêng)
import copy
import functools
import json
import time
import os
import sys
import threading
import unicodedata

from hangso_xq import (HACCAU, LAMCAU, HOACAU, HONGCAU, TUSAMDON, CAPCUUDON, HOATTAMDON, TUTAMDON, HOANGKIMTHANHY, TUKIMBAOHOP, TIENTE,
                       LEBAOKHAIQUOC, THANHTAMDON, TOAICAM, BAOTHUVATPHAMs, BUAGIAY, HYDUONG, TRANKY, TUIPHAPBAO, SOCAPDOANTHACH, TRUNGCAPDOANTHACH,
                       CAOCAPDOANTHACH, CHIENQUOCLENH, NHIEPHONLINH, CHUONGHAMTHIEN, BATTIENDON, CUULONGTHANHOATRAO, DAIPHAPLUCTHACH,
                       TIEUPHAPLUCTHACH, DAIHUYETTHACH, TIEUHUYETTHACH, ANTHANHOAN, THUONGPHUONGBAOKIEM, DAUNANH, TIEUDAOTAN, QUYNGUYENDON,
                       KIMTANGTAN, KHIMACHDON, XALOITU, NGANHANHTU, TUTINHDON, PHUCSINHDON, THANHTAMDAN, KHUMATAN, THILUYENDON, THILUYENQUA,
                       CAOCAPBAOTHUTHUCPHAM, ANXAPHU, NHANSAM, TAITAOHOAN, HOITHANHPHU, THIENLYHUUTINH, PHIHANHPHU, THOHANHCHAU, CAOBOCTACDAN,
                       TANGBAODO, THIENNGUYENDON, THIENNGUYENDAN, HOIBANGPHU, TINHNGUYENDON, CUONGTHIPHU, NGUYENLIEULUYENDONs,
                       CHUTIEMTAPHOA, CHUTUULAU, LAOTUU, DUAHAU, TRIDUOC, PHUCDUOC, LONGTIENTHAO, HOATLACHOAN, CAPCUUDON)

HANHDONG_GIU = "giu"
HANHDONG_BAN = "ban"
HANHDONG_VUT = "vut"
# Chỉ còn để đọc luật cũ (trước khi Cất kho thành bảng riêng "catkho")
HANHDONG_CATKHO = "catkho"
RUONGTUDONG = 0
TENHANHDONG = {HANHDONG_GIU: "Giữ", HANHDONG_BAN: "Bán", HANHDONG_VUT: "Vứt"}
DIEUKIENs = ("ten", "tenchua", "loai", "mota")
TENDIEUKIEN = {"ten": "Tên đúng", "tenchua": "Tên chứa", "loai": "Loại chứa", "mota": "Mô tả chứa"}
TRUONGMUABU = ("vatpham", "tencuahang", "npc", "xepchong", "duoi", "muatoi", "thapnhat", "monphai", "chikhi")
TENTRUONGMUABU = {"vatpham": "Vật phẩm", "tencuahang": "Tên ở cửa hàng (nếu khác)", "npc": "NPC bán", "xepchong": "Xếp chồng tối đa / ô",
                  "duoi": "Mua khi dưới", "muatoi": "Mua cho đủ",
                  "thapnhat": "Chạy về mua khi còn ≤", "monphai": "Môn phái (trống = tất cả)", "chikhi": "Chỉ mua khi"}
XEPCHONGMACDINH = 100
# -1 = không tự chạy về mua bù (chỉ mua khi đang đứng gần NPC)
THAPNHATMACDINH = -1
CHIKHI_LUON = ""
CHIKHI_TRIEUHOIBAOTHU = "trieuhoibaothu"
TENCHIKHI = {CHIKHI_LUON: "Luôn", CHIKHI_TRIEUHOIBAOTHU: "Bật triệu hồi bảo thú giang hồ"}
NHAT_NHAT = "nhat"
NHAT_UUTIEN = "uutien"
NHAT_KHONGNHAT = "khongnhat"
TENHANHDONGNHAT = {NHAT_NHAT: "Nhặt", NHAT_UUTIEN: "Nhặt ưu tiên", NHAT_KHONGNHAT: "Không nhặt"}
DIEUKIENNHATs = ("ten", "tenchua")
# Nơi dùng của luật "dung" (bản đồ PK = không thuộc BANDOKHONGPKs; phó bản = BANDOPHOBANs khi không đang PK ở bản đồ PK)
NOI_MOINOI = "moinoi"
NOI_BANDOPK = "bandopk"
NOI_DANGPK = "dangpk"
NOI_KHAIKHOANG = "khaikhoang"
NOI_PHOBAN = "phoban"
NOI_KHAC = "khac"
TENNOIDUNG = {NOI_MOINOI: "Mọi nơi", NOI_BANDOPK: "Bản đồ PK", NOI_DANGPK: "Bản đồ PK, đang bật PK",
              NOI_KHAIKHOANG: "Bản đồ PK, đang bật PK hoặc khai khoáng", NOI_PHOBAN: "Phó bản (không đang PK)",
              NOI_KHAC: "Nơi khác (không đang PK, không phó bản)"}
# Điều kiện hiệu ứng của luật "dung": "thieu_..." = chỉ dùng khi CHƯA có hiệu ứng của món (buff), "co_..." / "bikhongche" = khi đang có.
# Mã hiệu ứng ứng với từng khoá ở tactu_vatpham_xq (HIEUUNGLUATDUNG)
HIEUUNG_KHONG = ""
TENHIEUUNGDUNG = {HIEUUNG_KHONG: "Không xét", "thieu_huyetthach": "Chưa có hiệu ứng Huyết Thạch",
                  "thieu_phapluc": "Chưa có hiệu ứng Pháp Lực Thạch", "thieu_thiennguyen": "Chưa có hiệu ứng Thiên Nguyên Đơn",
                  "thieu_nganhanh": "Chưa có hiệu ứng Ngân Hạnh Tử", "thieu_xaloi": "Chưa có hiệu ứng Xá Lợi Tử",
                  "co_datinh": "Đang có Dã Tính Cuồng Lực", "thieu_datinh": "Chưa có Dã Tính Cuồng Lực",
                  "bikhongche": "Đang dính Thực Cốt / Thực Giáp / Thiêu Đốt..."}
TRUONGSODUNG = ("sinhluc", "matsinhluc", "noiluc", "matnoiluc", "theluc", "giancach")
# Giãn cách mặc định giữa 2 lần dùng của 1 luật (giây): bằng THOIGIANCHOXACNHANHOIVATPHAM, gửi rồi mà chưa vào hồi thì chừng này giây
# sau gửi lại
GIANCACHDUNGMACDINH = 1.


def _khongtrung(*tens):
    kq = []
    for ten in tens:
        if ten not in kq:
            kq.append(ten)
    return kq


# Nhặt viết cứng trước đây: hangso_xq VATPHAMUUTIENNHATs / VATPHAMTUDONGNHATs / VATPHAMTUDONGNHATFARMs và danh sách thêm khi về bán
# rác trong tactu_vatpham_xq
_VATPHAMTUDONGNHATCU = (
    HACCAU, LAMCAU, HOACAU, HONGCAU, TUSAMDON, CAPCUUDON, HOATTAMDON, TIEUDAOTAN, KIMTANGTAN, QUYNGUYENDON, KHIMACHDON, TUTAMDON,
    HOANGKIMTHANHY, "Thanh Đồng Bảo Hộp", TUKIMBAOHOP, "Mồi Câu", "Đá Tương Uyên", TIENTE, "Vô Song Điểm Phiếu", "Cờ Đỏ", "Sao Vàng",
    LEBAOKHAIQUOC, "Âu Dã Bảo Thạch", "Long Cốt", "Phấn Huỳnh Quang", THANHTAMDON, TOAICAM, XALOITU,
    # Phôi vũ khí cấp 75: Kiếm, Đao, Thương, Côn, Ám Khí, Quyền
    "Ngọc Kiếm", "Kim Đao", "Xích Anh Thương", "Cổ Phương Côn", "Nguyệt Hoàn", "Thạch Điêu Quyền Nhẫn")
NHATMACDINH = [
    {"hanhdong": NHAT_UUTIEN, "ghichu": "Ưu tiên (cũ)", "ten": [LEBAOKHAIQUOC]},
    {"hanhdong": NHAT_NHAT, "ghichu": "Tự động nhặt (cũ)", "ten": _khongtrung(*_VATPHAMTUDONGNHATCU)},
    {"hanhdong": NHAT_NHAT, "chibanrac": True, "ghichu": "Nhặt thêm khi về bán rác (cũ)", "ten": [
        TIENTE, "Tơ Nhện", "Kịch Độc Châm", "Đuôi Bọ Cạp", "Ly Hồn", "Ly Phách", "Ma Tinh thạch", "Trái Táo", "Trái lê", "Phá Bố Y",
        "Toái Lăng", "Tơ Tằm", "Da Rắn", "Ống Tên", "Bao Kiếm", "Cán Đao", "Toái Sa", "Hồng Sắc Tiểu Thạch", "Mạng Nhện", "Tử Giả Di Vật",
        "Phi Hành Phiến", "Núm Vú", "Hành Quân Tán"]},
    {"hanhdong": NHAT_NHAT, "chibanrac": True, "ghichu": "Tên có chữ, khi về bán rác (cũ)", "tenchua": _khongtrung(
        "Kiếm", "Đao", "Mâu", "Thủ", "Thương", "Sáo", "Bổng", " Y", "Giáp", "Côn", "Kích", " Bào", " Lý", " Mạo", "Phi Phong", " Nguyệt",
        "Quan", " Liên", " Quần", " Hài", " Nhẫn", " Tiêu", "Đầu Cân", "Xú Diêm", "Nghênh Phong Trảm", " Mão", " Tố Quần", "Nhập môn",
        "Trứng gà", " cấp ", "Kim Cương")},
]

# Luật viết cứng trước đây trong tactu (bán rác) / hangso_xq (VATPHAMKHONGBANs, LOAIVATPHAMKHONGBANs, MOTAVATPHAMKHONGBANs)
LUATMACDINH = [
    {"hanhdong": HANHDONG_GIU, "ghichu": "Danh sách không bán (cũ)", "ten": _khongtrung(
        *_VATPHAMTUDONGNHATCU, *BAOTHUVATPHAMs, BUAGIAY, HYDUONG, TRANKY, TUIPHAPBAO, SOCAPDOANTHACH, TRUNGCAPDOANTHACH, CAOCAPDOANTHACH,
        CHIENQUOCLENH, NHIEPHONLINH, CHUONGHAMTHIEN, BATTIENDON, CUULONGTHANHOATRAO, DAIPHAPLUCTHACH, TIEUPHAPLUCTHACH, DAIHUYETTHACH,
        TIEUHUYETTHACH, THUONGPHUONGBAOKIEM, DAUNANH, TIEUDAOTAN, QUYNGUYENDON, KIMTANGTAN, KHIMACHDON, XALOITU, NGANHANHTU,
        TUTINHDON, PHUCSINHDON, THANHTAMDAN, KHUMATAN, THILUYENDON, THILUYENQUA, CAOCAPBAOTHUTHUCPHAM, ANXAPHU, NHANSAM, TAITAOHOAN,
        HOITHANHPHU, THIENLYHUUTINH, PHIHANHPHU, THOHANHCHAU, CAOBOCTACDAN, TANGBAODO, THIENNGUYENDON, THIENNGUYENDAN, HOIBANGPHU,
        TINHNGUYENDON, "Đá Kim Cương", "Đế Kim Cương", "Chuôi Kim Cương", "Khoan Kim Cương", "Cờ Đỏ", "Sao Vàng", "Cường Hóa Ngân Châm Độ Ách",
        "Trang Sách Cũ", "Bột Tiêu Thạch", "Huy Hiệu 2D", "Chiến Quốc Lệnh x3", CUONGTHIPHU, *NGUYENLIEULUYENDONs)},
    {"hanhdong": HANHDONG_GIU, "ghichu": "Tên có chữ không bán (cũ)",
     "tenchua": ["Bí kíp", "Nhập môn", "Bảo Thạch", "Ngọc Thạch", "cấp", "Tàng Đồ", "Phục Dược", "Trị Dược"]},
    {"hanhdong": HANHDONG_GIU, "ghichu": "Loại không bán (cũ)", "loai": ["nhập môn", "bí kíp", "pháp bảo"]},
    {"hanhdong": HANHDONG_GIU, "ghichu": "Mô tả không bán (cũ)", "mota": ["ngự thạch"]},
]
# Mua viết cứng trước đây trong tactu action_tudongmuavatpham (cùng thứ tự)
MUABUMACDINH = [
    {"vatpham": TRANKY, "npc": CHUTIEMTAPHOA, "duoi": 1999, "muatoi": 1999, "monphai": "vanmongcoc"},
    {"vatpham": DAUNANH, "npc": CHUTIEMTAPHOA, "duoi": 30, "muatoi": 30, "monphai": "vanmongcoc"},
    {"vatpham": BUAGIAY, "npc": CHUTIEMTAPHOA, "duoi": 999, "muatoi": 999, "monphai": "maoson"},
    {"vatpham": CAOCAPBAOTHUTHUCPHAM, "tencuahang": "Thức Ăn Bảo Thú Cao Cấp", "npc": CHUTIEMTAPHOA, "duoi": 30, "muatoi": 30,
     "chikhi": CHIKHI_TRIEUHOIBAOTHU},
    {"vatpham": LAOTUU, "npc": CHUTUULAU, "duoi": 30, "muatoi": 30, "chikhi": CHIKHI_TRIEUHOIBAOTHU},
    {"vatpham": DUAHAU, "npc": CHUTUULAU, "duoi": 30, "muatoi": 30, "chikhi": CHIKHI_TRIEUHOIBAOTHU},
]

# Dùng vật phẩm viết cứng trước đây trong tactu_vatpham_xq.action_tudongsudungvatpham (cùng điều kiện, cùng thứ tự)
_HOISINHLUCPK = [TRIDUOC, THILUYENQUA, THILUYENDON, CAPCUUDON, HOATLACHOAN]
_HOINOILUCPK = [PHUCDUOC, LONGTIENTHAO, THILUYENDON, HOATTAMDON]
DUNGMACDINH = [
    {"vatpham": [TIEUPHAPLUCTHACH], "noiluc": 50, "hieuung": "thieu_phapluc", "noi": NOI_BANDOPK, "giancach": 2.5,
     "ghichu": "Pháp Lực Thạch"},
    {"vatpham": [TIEUHUYETTHACH], "sinhluc": 75, "hieuung": "thieu_huyetthach", "noi": NOI_KHAIKHOANG, "giancach": 2.5,
     "ghichu": "Huyết Thạch khi PK / khai khoáng"},
    {"vatpham": [TIEUHUYETTHACH], "sinhluc": 50, "hieuung": "thieu_huyetthach", "monphai": "maoson", "giancach": 2.5,
     "ghichu": "Huyết Thạch Mao Sơn"},
    {"vatpham": [TIEUHUYETTHACH], "sinhluc": 25, "hieuung": "thieu_huyetthach", "giancach": 2.5, "ghichu": "Huyết Thạch máu thấp"},
    {"vatpham": [THIENNGUYENDON], "hieuung": "thieu_thiennguyen", "noi": NOI_DANGPK, "monphai": "daohoanguyen", "giancach": 2.5,
     "ghichu": "Buff khi PK"},
    {"vatpham": [NGANHANHTU], "hieuung": "thieu_nganhanh", "noi": NOI_DANGPK, "giancach": 2.5, "ghichu": "Buff khi PK"},
    {"vatpham": [XALOITU], "hieuung": "thieu_xaloi", "noi": NOI_DANGPK, "giancach": 2.5, "ghichu": "Buff khi PK"},
    # Hồi sinh lực: mỗi luật 1 cặp, đang Dã Tính Cuồng Lực (Đào Hoa) thì ≤ 15% mới dùng (người dùng 2026-11-14). Sinh lực đọc ra luôn
    # chẵn (x2) nên "< 15%" cũng là ≤ 15%
    {"vatpham": list(_HOISINHLUCPK), "sinhluc": 75, "matsinhluc": 2500, "hieuung": "thieu_datinh", "noi": NOI_DANGPK, "chikhidanh": True,
     "khongphobanrieng": True, "ghichu": "Hồi sinh lực khi PK"},
    {"vatpham": list(_HOISINHLUCPK), "sinhluc": 15, "matsinhluc": 2500, "hieuung": "co_datinh", "noi": NOI_DANGPK, "chikhidanh": True,
     "khongphobanrieng": True, "ghichu": "Hồi sinh lực khi PK (Dã Tính)"},
    {"vatpham": _HOISINHLUCPK[::-1], "sinhluc": 35, "matsinhluc": 2500, "hieuung": "thieu_datinh", "noi": NOI_PHOBAN, "khongphobanrieng": True,
     "ghichu": "Hồi sinh lực ở phó bản"},
    {"vatpham": _HOISINHLUCPK[::-1], "sinhluc": 15, "matsinhluc": 2500, "hieuung": "co_datinh", "noi": NOI_PHOBAN, "khongphobanrieng": True,
     "ghichu": "Hồi sinh lực ở phó bản (Dã Tính)"},
    {"vatpham": [HOATLACHOAN], "sinhluc": 75, "hieuung": "thieu_datinh", "noi": NOI_KHAC, "chikhidanh": True, "khongphobanrieng": True,
     "ghichu": "Hồi sinh lực"},
    {"vatpham": [HOATLACHOAN], "sinhluc": 15, "hieuung": "co_datinh", "noi": NOI_KHAC, "chikhidanh": True, "khongphobanrieng": True,
     "ghichu": "Hồi sinh lực (Dã Tính)"},
    {"vatpham": list(_HOINOILUCPK), "noiluc": 75, "matnoiluc": 3000, "noi": NOI_DANGPK, "chikhidanh": True, "khongphobanrieng": True,
     "ghichu": "Hồi nội lực khi PK"},
    {"vatpham": _HOINOILUCPK[::-1], "noiluc": 35, "matnoiluc": 3000, "noi": NOI_PHOBAN, "chikhidanh": True, "khongphobanrieng": True,
     "ghichu": "Hồi nội lực ở phó bản"},
    {"vatpham": [KHUMATAN, THANHTAMDON], "hieuung": "bikhongche", "noi": NOI_DANGPK, "chikhidanh": True, "ghichu": "Giải hiệu ứng xấu"},
    {"vatpham": [BATTIENDON], "theluc": 5, "giancach": 30., "ghichu": "Hồi thể lực"},
]

_cache = {"dulieu": None, "mtime": None, "lankiemtra": 0.}
# tailuat() xem file đổi chưa tối đa mỗi chừng này giây (mỗi lần xem là 2 lệnh hệ thống exists + getmtime, mà mỗi món mỗi lượt gọi
# tailuat vài lần; py-spy 2026-11-12: os.path.exists ~1.7% CPU). Sửa luật trên giao diện thì chậm nhất chừng này giây mới áp
GIANCACHKIEMTRAFILELUAT = 1.
_khoa = threading.Lock()


def duongdanluat():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "luattuido.json")


@functools.lru_cache(maxsize = 8192)
def chuanhoa(chu):
    # So khớp không phân biệt hoa thường, dựng sẵn dấu (NFC), gộp khoảng trắng. Nhớ kết quả: hàm thuần, mà mỗi lượt vứt / bán / cất kho
    # gọi lại cho cùng tên món, cùng chuỗi luật, cả đoạn mô tả dài, với mọi luật x mọi món (py-spy 2026-11-12 ~2% CPU tiến trình bot)
    return " ".join(unicodedata.normalize("NFC", str(chu or "")).lower().split())


def _danhsach(giatri):
    # Điều kiện: chuỗi (cũ / gõ tay) hoặc danh sách -> danh sách chuỗi khác rỗng (chuỗi nhiều dòng thì mỗi dòng 1 giá trị)
    if isinstance(giatri, str):
        giatri = giatri.split("\n")
    return [str(g).strip() for g in giatri or [] if str(g).strip()]


def _chuanhoaluat(luat):
    luat = dict(luat)
    luat["bat"] = bool(luat.get("bat", True))
    luat["is_bao"] = bool(luat.get("is_bao", False))
    luat.pop("is_catkho", None)
    if luat.get("hanhdong") not in TENHANHDONG:
        luat["hanhdong"] = HANHDONG_GIU
    for dieukien in DIEUKIENs:
        luat[dieukien] = _danhsach(luat.get(dieukien))
    luat["ghichu"] = str(luat.get("ghichu") or "")
    return luat


def _chuanhoamuabu(muc):
    muc = dict(muc)
    muc["bat"] = bool(muc.get("bat", True))
    for truong in ("vatpham", "tencuahang", "npc", "monphai"):
        muc[truong] = str(muc.get(truong) or "").strip()
    # Bản cũ ghi tay ô / đơn giá: bỏ, bot tự tra theo tên trong cửa hàng
    muc.pop("o", None)
    muc.pop("dongia", None)
    if muc.get("chikhi") not in TENCHIKHI:
        muc["chikhi"] = CHIKHI_LUON
    for truong in ("duoi", "muatoi"):
        try:
            muc[truong] = max(0, int(muc.get(truong) or 0))
        except (TypeError, ValueError):
            muc[truong] = 0
    try:
        muc["xepchong"] = max(1, int(muc.get("xepchong") or XEPCHONGMACDINH))
    except (TypeError, ValueError):
        muc["xepchong"] = XEPCHONGMACDINH
    try:
        muc["thapnhat"] = max(-1, int(muc.get("thapnhat", THAPNHATMACDINH)))
    except (TypeError, ValueError):
        muc["thapnhat"] = THAPNHATMACDINH
    return muc


def _chuanhoacatkho(luat):
    luat = dict(luat)
    luat["bat"] = bool(luat.get("bat", True))
    for dieukien in DIEUKIENs:
        luat[dieukien] = _danhsach(luat.get(dieukien))
    for truong in ("ruong", "giulai"):
        try:
            luat[truong] = max(0, int(luat.get(truong) or 0))
        except (TypeError, ValueError):
            luat[truong] = 0
    luat["ghichu"] = str(luat.get("ghichu") or "")
    return {k: luat[k] for k in ("bat", *DIEUKIENs, "ruong", "giulai", "ghichu")}


def _danhsachgiukhoangtrang(giatri):
    # Như _danhsach nhưng giữ khoảng trắng đầu / cuối của từng giá trị (" Y" để khỏi khớp mọi tên có chữ y)
    if isinstance(giatri, str):
        giatri = giatri.split("\n")
    return [unicodedata.normalize("NFC", str(g).rstrip("\r")) for g in giatri or [] if str(g).strip()]


def _chuanhoanhat(luat):
    luat = dict(luat)
    luat["bat"] = bool(luat.get("bat", True))
    luat["chibanrac"] = bool(luat.get("chibanrac", False))
    if luat.get("hanhdong") not in TENHANHDONGNHAT:
        luat["hanhdong"] = NHAT_NHAT
    luat["ten"] = _danhsach(luat.get("ten"))
    luat["tenchua"] = _danhsachgiukhoangtrang(luat.get("tenchua"))
    luat["ghichu"] = str(luat.get("ghichu") or "")
    return {k: luat[k] for k in ("bat", "hanhdong", *DIEUKIENNHATs, "chibanrac", "ghichu")}


def _chuanhoadung(luat):
    luat = dict(luat)
    kq = {"bat": bool(luat.get("bat", True)), "vatpham": _danhsach(luat.get("vatpham"))}
    for truong in TRUONGSODUNG:
        macdinhso = -1 if truong == "theluc" else GIANCACHDUNGMACDINH if truong == "giancach" else 0
        try:
            so = float(luat.get(truong, macdinhso))
        except (TypeError, ValueError):
            so = macdinhso
        kq[truong] = so if truong == "giancach" else int(so)
    kq["giancach"] = max(0.5, kq["giancach"])
    kq["theluc"] = max(-1, kq["theluc"])
    for truong in ("sinhluc", "noiluc", "matsinhluc", "matnoiluc"):
        kq[truong] = max(0, kq[truong])
    kq["hieuung"] = luat.get("hieuung") if luat.get("hieuung") in TENHIEUUNGDUNG else HIEUUNG_KHONG
    kq["noi"] = luat.get("noi") if luat.get("noi") in TENNOIDUNG else NOI_MOINOI
    kq["monphai"] = str(luat.get("monphai") or "").strip()
    kq["chikhidanh"] = bool(luat.get("chikhidanh", False))
    kq["khongphobanrieng"] = bool(luat.get("khongphobanrieng", False))
    kq["ghichu"] = str(luat.get("ghichu") or "")
    return kq


def motadieukiendung(luat):
    # 'Sinh lực < 75% · mất ≥ 2500 · Chưa có hiệu ứng Huyết Thạch' cho giao diện
    phans = []
    if luat["sinhluc"]:
        phans.append(f"Sinh lực < {luat['sinhluc']}%")
    if luat["matsinhluc"]:
        phans.append(f"mất ≥ {luat['matsinhluc']} sinh lực")
    if luat["noiluc"]:
        phans.append(f"Nội lực < {luat['noiluc']}%")
    if luat["matnoiluc"]:
        phans.append(f"mất ≥ {luat['matnoiluc']} nội lực")
    if luat["theluc"] >= 0:
        phans.append(f"Thể lực ≤ {luat['theluc']}")
    if luat["hieuung"]:
        phans.append(TENHIEUUNGDUNG[luat["hieuung"]])
    if luat["chikhidanh"]:
        phans.append("đang bật đánh")
    return " · ".join(phans) if phans else "Luôn (mỗi lần hết hồi)"


def _chuanhoa(dulieu):
    luats, catkhos = list(dulieu.get("luat") or []), dulieu.get("catkho")
    if catkhos is None:
        # File cũ (Cất kho còn là hành động / cờ 🗄 trong "luat"): chuyển sang bảng Cất kho
        catkhos = [l for l in luats if l.get("hanhdong") == HANHDONG_CATKHO or l.get("is_catkho")]
        luats = [l for l in luats if l.get("hanhdong") != HANHDONG_CATKHO]
    nhats = dulieu.get("nhat")
    if nhats is None:
        # File cũ chưa có bảng nhặt: lấy danh sách nhặt viết cứng trước đây
        nhats = copy.deepcopy(NHATMACDINH)
    dungs = dulieu.get("dung")
    if dungs is None:
        # File cũ chưa có bảng dùng vật phẩm: lấy các điều kiện viết cứng trước đây
        dungs = copy.deepcopy(DUNGMACDINH)
    return {"luat": [_chuanhoaluat(l) for l in luats], "muabu": [_chuanhoamuabu(m) for m in dulieu.get("muabu") or []],
            "catkho": [_chuanhoacatkho(l) for l in catkhos], "is_catkhosauban": bool(dulieu.get("is_catkhosauban", True)),
            "nhat": [_chuanhoanhat(l) for l in nhats], "dung": [_chuanhoadung(l) for l in dungs]}


def macdinh():
    return _chuanhoa({"luat": copy.deepcopy(LUATMACDINH), "muabu": copy.deepcopy(MUABUMACDINH), "catkho": []})


def tailuat():
    # Đọc lại khi file đổi. Chưa có file thì tạo từ luật mặc định; file hỏng thì dùng bản đọc được gần nhất, chưa đọc được lần nào thì
    # dùng luật mặc định (không bao giờ chạy với bộ luật rỗng do lỗi đọc: rỗng là bán hết)
    with _khoa:
        bayh = time.monotonic()
        if _cache["dulieu"] and bayh - _cache["lankiemtra"] < GIANCACHKIEMTRAFILELUAT:
            return _cache["dulieu"]
        _cache["lankiemtra"] = bayh
        duongdan = duongdanluat()
        if not os.path.exists(duongdan):
            try:
                luuluat(macdinh())
            except OSError as err:
                print(f"[LUẬT TÚI ĐỒ] Không tạo được {duongdan}: {err}")
                return macdinh()
        try:
            mtime = os.path.getmtime(duongdan)
        except OSError:
            return _cache["dulieu"] or macdinh()
        if mtime != _cache["mtime"]:
            try:
                with open(duongdan, encoding = "utf-8-sig") as file:
                    _cache["dulieu"] = _chuanhoa(json.load(file))
            except (OSError, ValueError, AttributeError) as err:
                print(f"[LUẬT TÚI ĐỒ] Lỗi đọc {duongdan}: {err}")
            _cache["mtime"] = mtime
        return _cache["dulieu"] or macdinh()


def luuluat(dulieu):
    duongdan = duongdanluat()
    os.makedirs(os.path.dirname(duongdan), exist_ok = True)
    with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
        json.dump(_chuanhoa(dulieu), file, ensure_ascii = False, indent = 2)
    os.replace(duongdan + ".tmp", duongdan)
    # Vừa lưu thì lần tailuat() kế tiếp xem lại file ngay (không chờ GIANCACHKIEMTRAFILELUAT)
    _cache["lankiemtra"] = 0.


def is_cancanmota(luat):
    return bool(luat.get("loai") or luat.get("mota"))


def khopluat(luat, ten, laymota):
    # laymota() -> (loại, mô tả) hoặc None khi chưa đọc được (chỉ gọi khi luật có điều kiện loại / mô tả). Trả về True / False / None
    # (None = chưa biết, cần mô tả mà chưa đọc được). Luật không có điều kiện nào thì không khớp gì (khớp mọi món mà là luật vứt / bán
    # thì mất cả túi)
    if not any(luat.get(d) for d in DIEUKIENs):
        return False
    tenchuan = chuanhoa(ten)
    if luat["ten"] and not any(chuanhoa(g) == tenchuan for g in luat["ten"]):
        return False
    if luat["tenchua"] and not any(chuanhoa(g) in tenchuan for g in luat["tenchua"]):
        return False
    if not is_cancanmota(luat):
        return True
    mota = laymota()
    if mota is None:
        return None
    loai, noidung = chuanhoa(mota[0]), chuanhoa(mota[1])
    if luat["loai"] and not any(chuanhoa(g) in loai for g in luat["loai"]):
        return False
    if luat["mota"] and not any(chuanhoa(g) in noidung for g in luat["mota"]):
        return False
    return True


def timluat(ten, laymota, dulieu = None):
    # Luật đầu tiên khớp món tên ten (dict), None = không luật nào khớp, "chuabiet" = có luật cần mô tả mà chưa đọc được
    if not ten:
        return None
    for luat in (dulieu or tailuat())["luat"]:
        if not luat["bat"]:
            continue
        khop = khopluat(luat, ten, laymota)
        if khop is None:
            return "chuabiet"
        if khop:
            return luat
    return None


def timhanhdong(ten, laymota, dulieu = None):
    # Hành động của luật đầu tiên khớp món tên ten: "giu" / "ban" / "vut", None = không luật nào khớp,
    # "chuabiet" = có luật cần mô tả mà chưa đọc được (lượt này đừng làm gì món đó)
    luat = timluat(ten, laymota, dulieu)
    return luat["hanhdong"] if isinstance(luat, dict) else luat


def timluatbao(ten, laymota, dulieu = None):
    # Luật 📣 đầu tiên khớp món tên ten (dict) hoặc None. Xét riêng với hành động: chỉ các luật có 📣, nên luật Giữ / Bán đứng trên
    # không chặn báo (vd luật Giữ 114 tên ở đầu cũng có "Hoa Cầu" mà luật 📣 "Hoa Cầu" đặt bên dưới vẫn báo). Chưa đọc được mô tả coi
    # như không khớp
    if not ten:
        return None
    for luat in (dulieu or tailuat())["luat"]:
        if luat["bat"] and luat["is_bao"] and khopluat(luat, ten, laymota):
            return luat
    return None


def timluatcatkho(ten, laymota, dulieu = None):
    # Luật bật đầu tiên trong bảng Cất kho khớp món tên ten (dict, có "ruong" / "giulai") hoặc None. Xét riêng với bảng luật hành động
    # (vd luật Giữ mặc định có "Nhiếp Hồn Linh" mà bảng Cất kho có "Nhiếp Hồn Linh" thì vẫn cất). Chưa đọc được mô tả coi như không khớp
    if not ten:
        return None
    for luat in (dulieu or tailuat())["catkho"]:
        if luat["bat"] and khopluat(luat, ten, laymota):
            return luat
    return None


def timhanhdongnhat(ten, is_banrac, dulieu = None):
    # Hành động nhặt của luật nhặt bật đầu tiên khớp món tên ten dưới đất: "nhat" / "uutien" / "khongnhat", None = không luật nào
    # khớp. Luật "chibanrac" chỉ xét khi is_banrac (bật Tự động về bán rác). So không phân biệt hoa thường; "tenchua" giữ khoảng trắng
    if not ten:
        return None
    tenchuan = chuanhoa(ten)
    # Tên chứa: chỉ dựng sẵn dấu + chữ thường, không gộp / cắt khoảng trắng (" Y" ở đầu mỗi từ)
    tenthuong = unicodedata.normalize("NFC", ten).lower()
    for luat in (dulieu or tailuat())["nhat"]:
        if not luat["bat"] or (luat["chibanrac"] and not is_banrac) or not any(luat.get(d) for d in DIEUKIENNHATs):
            continue
        if luat["ten"] and not any(chuanhoa(g) == tenchuan for g in luat["ten"]):
            continue
        if luat["tenchua"] and not any(g.lower() in tenthuong for g in luat["tenchua"]):
            continue
        return luat["hanhdong"]
    return None


def is_coluatbao(dulieu = None):
    return any(luat["bat"] and luat["is_bao"] for luat in (dulieu or tailuat())["luat"])


def motaluat(luat, sohienthi = 3):
    # 'Tên chứa "Bí kíp", "Nhập môn", "Bảo Thạch" +5' cho giao diện
    phans = []
    for d in DIEUKIENs:
        if luat.get(d):
            giatris = ", ".join(f'"{g}"' for g in luat[d][:sohienthi]) + (f" +{len(luat[d]) - sohienthi}" if len(luat[d]) > sohienthi else "")
            phans.append(f"{TENDIEUKIEN[d]} {giatris}")
    return " · ".join(phans) if phans else "(chưa có điều kiện, không khớp món nào)"
