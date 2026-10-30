# Nhiệm vụ sư môn: đọc nội dung nhiệm vụ trong cửa sổ nhiệm vụ của game, phân loại và tách các thông tin cần làm; vị trí NPC / quái
# (bảng có sẵn, file game, tự ghi lại mỗi khi thấy). Phần làm nhiệm vụ nằm ở tactu_sumon_xq.py.
#
# Cửa sổ nhiệm vụ ([thông tin game] + TG_NHIEMVU, moitruong.get_danhsachmucnhiemvu): danh sách mục theo thứ tự hiển thị, mục cha
# (vd "Nhiệm Vụ Sư Môn") không thụt đầu dòng, mục con thụt 2 dấu cách ("  Bắt Yêu Quái", "  Luyện Tập(Xong)"); mô tả của mục con:
#   "<Tên> (Lượt thứ N)\nMục đích nhiệm vụ：\n    <mục đích>\n[Nâng cao kinh nghiệm: 0/5720\n]Mô tả nhiệm vụ：\n    <mô tả>"
# Máy chủ tự gửi lại cả danh sách khi nhiệm vụ đổi (không cần mở cửa sổ).
import json
import math
import os
import re
import sys
import threading
import time
import unicodedata

from bando_xq import layidbandotheoten, BANDOCONG_MAP
from hangso_xq import BANDO_CHUQUOC, BANDO_TANTHUTHON, BANDO_CONLUAN, BANDO_MAOSON, BANDO_THUCSON, BANDO_DUONGMON, BANDO_DAOHOANGUYEN, BANDO_VANMONGCOC
from hangso_xq import TENMONPHAI

MUCSUMON = "Nhiệm Vụ Sư Môn"
# Quá chừng này lần trong ngày (số NPC giao nhiệm vụ báo "Số lần nhiệm vụ đã tích lũy ngày hôm nay") thì làm thêm không có thưởng
SOLANSUMONTOIDA = 20

LOAI_DENTIM = "dentim"          # Đi tìm Thạch Sư: tới NPC phụ nhận việc Thu thập / Mua sắm
LOAI_THUTHAP = "thuthap"        # Thu thập N cái <vật phẩm>, và giao cho <NPC>
LOAI_THUMUA = "thumua"          # Thu mua N <vật phẩm>, và giao cho <NPC>
LOAI_THAMVIENG = "thamvieng"    # Thăm Viếng <NPC>
LOAI_LUYENTAP = "luyentap"      # Tăng lên N điểm Kinh nghiệm
LOAI_DULICH = "dulich"          # Tăng lên N điểm Tiềm Năng
LOAI_BATYEUQUAI = "batyeuquai"  # Bắt <quái> rồi trở về
LOAI_HIEPTRO = "hieptro"      # Hiệp Trợ Trị An: Tìm <Nước> Giám Ngục Quan -> Tiêu diệt <quái> ngoài thành (toạ độ trong mô tả)
LOAI_TYTHI = "tythi"          # Môn Phái Tỷ Thý: Đi tới <phái> tỷ thý võ công, khiêu chiến <phái> Đệ Tử ("<phái> đệ tử: 0/1")
LOAI_TRUYBAT = "truybat"      # Truy Bắt Thích Khách / Truy Sát Phản Đồ: Tìm <Nước> Tổng Quản Vương Phủ (look là nhận) -> đuổi đánh ở <Nước>
LOAI_TUANSON = "tuanson"      # Tuần Sơn: Tuần tra ở bổn môn, bắt hết kẻ khả nghi (toạ độ trong mô tả, ở bản đồ môn phái mình)
LOAI_KHONGRO = "khongro"

TENLOAI = {LOAI_DENTIM: "Đi tìm", LOAI_THUTHAP: "Thu thập", LOAI_THUMUA: "Mua sắm", LOAI_THAMVIENG: "Thăm viếng", LOAI_LUYENTAP: "Luyện tập",
           LOAI_DULICH: "Du lịch", LOAI_BATYEUQUAI: "Bắt yêu quái", LOAI_HIEPTRO: "Hiệp trợ trị an", LOAI_TYTHI: "Môn phái tỷ thí", LOAI_TRUYBAT: "Truy bắt / truy sát", LOAI_TUANSON: "Tuần sơn",
           LOAI_KHONGRO: "Chưa rõ"}
# Môn Phái Tỷ Thý: đối thủ ở phái nào không phải "<phái> Đệ Tử" (người dùng cho biết): (tên, x, y) hoặc (tên,) khi chưa biết toạ độ;
# cùng tên có nhiều NPC thì tới đúng toạ độ rồi lấy con gần nhất
NPCTYTHI = {"daohoanguyen": ("Thôn Trang Hộ Vệ", 43, 59), "camvequan": ("Thân Binh", 168, 79), "duongmon": ("Đường Gia Thị Vệ",)}


def tenthaythe(ten):
    # Tên NPC trong nhiệm vụ / danh hiệu trong game khác tên trên bản đồ nhỏ -> ([tên để thử, ...], bản đồ của nước hoặc None):
    #   "Triệu Quốc Giám Ngục Quan" = "Quản Ngục" ở Triệu Quốc, "Sở Quốc Tổng Quản Vương Phủ" = "Sở Tổng Quản" ở Sở Quốc,
    #   danh hiệu "Chủ Tiệm Trang Sức" = "Chủ Tiệm Kim Hoàn ..."
    ten = (ten or "").strip()
    m = re.match(r"(\S+) Quốc Giám Ngục", ten)
    if m:
        return [ten, "Quản Ngục"], timbandotheoten(m.group(1) + " Quốc")
    m = re.match(r"(\S+) Quốc Tổng Quản", ten)
    if m:
        return [ten, f"{m.group(1)} Tổng Quản"], timbandotheoten(m.group(1) + " Quốc")
    if chuanhoaten(ten).startswith(chuanhoaten("Chủ Tiệm Trang Sức")):
        return [ten, "Chủ Tiệm Kim Hoàn" + ten[len("Chủ Tiệm Trang Sức"):]], None
    return [ten], None

# Bản đồ của môn phái (Hồi môn phái "dGludmF0 1" về đây)
BANDOMONPHAI = {"conluan": BANDO_CONLUAN, "maoson": BANDO_MAOSON, "thucson": BANDO_THUCSON, "duongmon": BANDO_DUONGMON,
                "daohoanguyen": BANDO_DAOHOANGUYEN, "vanmongcoc": BANDO_VANMONGCOC, "camvequan": BANDO_CHUQUOC}

# NPC giao nhiệm vụ / NPC Thu thập - Mua sắm mặc định theo môn phái (sửa được trên giao diện, lưu theo nhân vật). Người giao có thể đổi
# theo cấp (Côn Luân dưới 60: Văn Xương Chân Quân)
NPCSUMONMACDINH = {
    "conluan": ("Văn Xương Chân Quân", "Thạch Sư"),
}

# Vị trí NPC biết sẵn: tên -> (bản đồ, x, y). Thêm vào đó: menu/quest/questlink.txt của game và vị trí bot tự ghi (_internal/vitridoituong)
VITRINPCCODINH = {
    "Văn Xương Chân Quân": (BANDO_CONLUAN, 111, 137),
    "Thạch Sư": (BANDO_CONLUAN, 104, 132),
    "Quảng Thành Tử": (BANDO_CONLUAN, 102, 144),
    "Chủ Tiệm Tạp Hóa": (BANDO_TANTHUTHON, 113, 147),
    "Chủ Tiệm Vũ Khí": (BANDO_TANTHUTHON, 101, 146),
    "Chủ Tiệm Giáp Trụ": (BANDO_TANTHUTHON, 120, 166),
    "Chủ Tiệm Y Dược": (BANDO_TANTHUTHON, 135, 170),
    "Đại Tướng Quân": (BANDO_CHUQUOC, 227, 50),
}

# Thăm Viếng: NPC (chưởng môn, quân vương) -> bản đồ, khi chưa biết toạ độ thì tới bản đồ đó tìm. So theo tên rút gọn (tên trong
# nhiệm vụ có thể ngắn hơn tên NPC: "Tề Vương" / "Tề Vương Điền Kiến")
BANDOTHAMVIENG = {
    "Quỷ Cốc Tử": BANDO_VANMONGCOC,
    "Mao Chân Nhân": BANDO_MAOSON,
    "Thục Sơn Chân Nhân": BANDO_THUCSON,
    "Quảng Thành Tử": BANDO_CONLUAN,
    "Đường Lão Gia": BANDO_DUONGMON,
    "Tề Vương": 10,
    "Hàn Vương": 20,
    "Triệu Vương": 30,
    "Nguỵ Chiêu Vương": 40,
    "Ngụy Chiêu Vương": 40,
    "Tần Vương": 50,
    "Sở Khảo Liệt Vương": 60,
    "Yên Vương": 70,
    "Chu Vương": 80,
    "Đại Tướng Quân": BANDO_CHUQUOC,
}

_DAUTHANHs = frozenset("̣̀́̉̃")


def chuanhoaten(ten):
    # So tên không phân biệt hoa thường, vị trí dấu thanh ("Thuỷ" / "Thủy"), khoảng trắng thừa
    tus = []
    for tu in unicodedata.normalize("NFD", str(ten or "")).lower().split():
        tus.append("".join(c for c in tu if c not in _DAUTHANHs) + "".join(c for c in tu if c in _DAUTHANHs))
    return " ".join(tus)


def is_trungten(ten, tenxet):
    # Tên NPC trong nhiệm vụ khớp tên đối tượng: bằng nhau, hoặc tên đối tượng bắt đầu bằng tên nhiệm vụ ("Tề Vương" ~ "Tề Vương Điền Kiến")
    a, b = chuanhoaten(ten), chuanhoaten(tenxet)
    return bool(a) and (a == b or b.startswith(a + " "))


def is_trungtenvatpham(ten, tenday):
    # Tên món (trong túi / luật, có thể bị cắt còn 31 byte) khớp tên đầy đủ trong cửa hàng: bằng nhau, hoặc tên bị cắt là phần đầu
    a, b = chuanhoaten(ten), chuanhoaten(tenday)
    return bool(a) and (a == b or (len((ten or "").encode("utf-8")) >= 29 and b.startswith(a)))


def boma(chuoi):
    # Bỏ mã màu "\x1b<ký tự>" của game
    return re.sub(r"\x1b.", "", chuoi or "")


def timbandotheoten(ten):
    ten = (ten or "").strip()
    if not ten:
        return None
    if chuanhoaten(ten) == chuanhoaten("Tân Thủ Thôn"):
        return BANDO_TANTHUTHON
    # Nhiệm vụ ghi "Khốn Ma Trận tầng 2" = bản đồ "Khốn Ma Trận 2"
    ten = re.sub(r"\s+tầng\s*(\d+)$", r" \1", ten, flags = re.IGNORECASE)
    # Bản đồ nhiều tầng mà nhiệm vụ không ghi tầng ("Cầu Cửu Khúc" = "Cầu Cửu Khúc 1")
    return layidbandotheoten(ten) or layidbandotheoten(ten + " 1")


def laynhiemvusumon(mucs):
    # mucs: [(tên mục, mô tả), ...] của cửa sổ nhiệm vụ -> nhiệm vụ sư môn đang nhận (dict, xem phantichnhiemvu) hoặc None khi không có
    is_trongsumon = False
    for ten, mota in mucs:
        if not ten.startswith(" "):
            is_trongsumon = chuanhoaten(ten) == chuanhoaten(MUCSUMON)
            continue
        if is_trongsumon:
            return phantichnhiemvu(ten.strip(), mota)
    return None


def phantichnhiemvu(tenmuc, mota):
    # -> {"ten", "is_xong", "luot", "loai", "mucdich", "mota", ...thông tin theo loại}
    is_xong = bool(re.search(r"\(\s*Xong\s*\)\s*$", tenmuc))
    ten = re.sub(r"\(\s*Xong\s*\)\s*$", "", tenmuc).strip()
    vanban = boma(mota).replace("\r", "")
    luot = re.search(r"Lượt thứ\s*(\d+)", vanban)
    phans = re.split(r"(Mục đích nhiệm vụ|Mô tả nhiệm vụ)\s*[：:]", vanban)
    mucdich, motachitiet = "", ""
    for i in range(1, len(phans) - 1, 2):
        if phans[i] == "Mục đích nhiệm vụ":
            mucdich = phans[i + 1]
        else:
            motachitiet = phans[i + 1]
    # Tiến độ "Nâng cao kinh nghiệm: 0/5720" nằm sau mục đích
    # Tiến độ nằm sau mục đích: "Nâng cao kinh nghiệm: 0/5720", "Lưu Manh: 0/1 (Thời hạn 60 phút)"
    # Tiến độ nằm sau mục đích, có thể nhiều dòng: "Nâng cao kinh nghiệm: 0/5720", "Lưu Manh: 0/1 (Thời hạn 60 phút)",
    # "Thủ Lĩnh Thích Khách0/1" (không có dấu ":")
    tiendos = [(t.strip(), int(a), int(b)) for t, a, b in re.findall(r"([^\n:：\d]+?)\s*[:：]?\s*(\d+)\s*/\s*(\d+)", mucdich)]
    tentiendo = tiendos[0][0] if tiendos else ""
    tiendo = tiendos[0][1:] if tiendos else None
    mucdich = re.sub(r"[^\n:：\d]+?\s*[:：]?\s*\d+\s*/\s*\d+[^\n]*", "", mucdich)
    mucdich = " ".join(mucdich.split())
    motachitiet = " ".join(motachitiet.split())
    nv = {"ten": ten, "is_xong": is_xong, "luot": int(luot.group(1)) if luot else 0, "loai": LOAI_KHONGRO, "mucdich": mucdich,
          "mota": motachitiet, "tiendo": tiendo, "tiendos": tiendos}

    if chuanhoaten(ten) in (chuanhoaten("Truy Bắt Thích Khách"), chuanhoaten("Truy Sát Phản Đồ")):
        nv["loai"] = LOAI_TRUYBAT
        # Tổng Quản nước giao (nhận + trả): "Tìm Sở Quốc Tổng Quản Vương Phủ" / "thư từ Sở Quốc Tổng Quản Vương Phủ"
        m = re.search(r"(\S+ Quốc) Tổng Quản", mucdich + " " + motachitiet)
        nv["tongquan"] = f"{m.group(1)} Tổng Quản Vương Phủ" if m else None
        m = re.match(r"Tìm (.+?)\.?$", mucdich)
        if m:
            # "Tìm Sở Quốc Tổng Quản Vương Phủ Truy bắt Thích khách": NPC là phần Tổng Quản
            nv.update(buoc = "tim", npc = nv["tongquan"] or m.group(1).strip())
            return nv
        # Nước đích (thường khác nước Tổng Quản giao): "Quan Viên Đào Tẩu đang ở Hàn Quốc (149,143) chạy trốn" -> nước sát toạ độ /
        # sau "đang ở" trong mô tả; không có thì mục đích (tới / ở <X> Quốc, "Đuổi bắt Thích Khách tới Yên Quốc"), rồi nước bất kỳ khác
        # nước Tổng Quản. Đối thủ lấy ở các dòng tiến độ, không có thì tên trước "đang ở" trong mô tả; mô tả có toạ độ thì tới đó trước
        nuoctongquan = (nv["tongquan"] or "").replace(" Tổng Quản Vương Phủ", "")
        nuoc = (re.search(r"(\S+ Quốc)\s*\(\s*\d+\s*,\s*\d+\s*\)", motachitiet) or re.search(r"đang ở (\S+ Quốc)", motachitiet)
                or re.search(r"(?:tới|ở|đến) (\S+ Quốc)", mucdich))
        nuoc = nuoc.group(1) if nuoc else next((n for n in re.findall(r"(\S+ Quốc)", mucdich) + re.findall(r"(\S+ Quốc)", motachitiet)[::-1]
                                                if n != nuoctongquan), None)
        toado = re.search(rf"{re.escape(nuoc)}\s*\((\d+)\s*,\s*(\d+)\)" if nuoc else r"$^", motachitiet) \
                or re.search(r"\((\d+)\s*,\s*(\d+)\)", motachitiet)
        doithu = re.search(r"(?:báo|nói) rằng ([^.,]+?) (?:đang|đã) (?:ở|trốn|chạy)", motachitiet)
        nv.update(buoc = "diet", bando = timbandotheoten(nuoc) if nuoc else None,
                  quais = [t for t, a, b in tiendos if a < b] or [t for t, _, _ in tiendos]
                          or [doithu.group(1).strip() if doithu else ten.split()[-1]],
                  toado = (int(toado.group(1)), int(toado.group(2))) if toado else None)
        return nv
    if chuanhoaten(ten) == chuanhoaten("Hiệp Trợ Trị An"):
        nv["loai"] = LOAI_HIEPTRO
        # Nước: "Tìm Triệu Quốc Giám Ngục Quan" / "Triệu Quốc Giám Ngục Quan gửi thư..."
        m = re.search(r"(\S+ Quốc) Giám Ngục", mucdich + " " + motachitiet)
        nv["bando"] = timbandotheoten(m.group(1)) if m else None
        nv["giamnguc"] = f"{m.group(1)} Giám Ngục Quan" if m else "Quản Ngục"
        m = re.match(r"Tìm (.+?)\.?$", mucdich)
        if m:
            nv.update(buoc = "tim", npc = m.group(1).strip())
            return nv
        nv["buoc"] = "diet"
        nv["quai"] = tentiendo or (re.search(r"Tiêu diệt (.+?)(?: ngoài thành|\.|$)", mucdich) or [None, ""])[1].strip().title()
        m = re.search(r"\((\d+)\s*,\s*(\d+)\)", motachitiet)
        nv["toado"] = (int(m.group(1)), int(m.group(2))) if m else None
        return nv
    if chuanhoaten(ten) == chuanhoaten("Tuần Sơn") or re.match(r"Tuần tra ở bổn môn", mucdich, re.IGNORECASE):
        # "Tuần tra ở bổn môn, bắt hết kẻ khả nghi" / "Kẻ Khả Nghi: 0/1" / "Có đệ tử bẩm báo ở Sư môn (71,83) xuất hiện kẻ khả nghi":
        # bản đồ là môn phái của nhân vật (tactu_sumon lấy theo môn phái), đối thủ lấy ở dòng tiến độ
        m = re.search(r"\((\d+)\s*,\s*(\d+)\)", motachitiet)
        nv.update(loai = LOAI_TUANSON, quai = tentiendo or "Kẻ Khả Nghi", toado = (int(m.group(1)), int(m.group(2))) if m else None)
        return nv
    m = re.match(r"Đi tới (.+?) tỷ th[ýíi]", mucdich, re.IGNORECASE)
    if m:
        # Môn Phái Tỷ Thý: phái -> bản đồ môn phái; đệ tử cần đánh lấy ở dòng tiến độ ("Côn Luân đệ tử: 0/1")
        tenphai = m.group(1).strip()
        maphai = next((ma for ma, ten in TENMONPHAI.items() if chuanhoaten(ten) == chuanhoaten(tenphai)
                       or chuanhoaten(ten).startswith(chuanhoaten(tenphai))), None)
        # Ghi tên bản đồ môn phái thay tên phái ("Đào Nguyên Thôn")
        if not maphai:
            idbando = timbandotheoten(tenphai)
            maphai = next((ma for ma, b in BANDOMONPHAI.items() if b == idbando), None)
        # detu: NPC nói chuyện để khiêu chiến; doithus: tên đối thủ có thể gặp trong trận (bản đồ tỷ thí riêng, vd 891 "Đào Hoa Nguyên đệ tử")
        ten_xy = NPCTYTHI.get(maphai)
        nv.update(loai = LOAI_TYTHI, phai = tenphai, bando = BANDOMONPHAI.get(maphai),
                  detu = ten_xy[0] if ten_xy else (tentiendo or f"{tenphai} Đệ Tử"), vitridetu = ten_xy[1:] if ten_xy else None,
                  doithus = [t for t in (tentiendo, f"{tenphai} đệ tử", ten_xy[0] if ten_xy else None) if t])
        return nv
    m = re.match(r"Đi tìm (.+?)\.?$", mucdich)
    if m:
        nv.update(loai = LOAI_DENTIM, npc = m.group(1).strip())
        return nv
    m = re.match(r"Thu thập (\d+) (?:cái |con |chiếc )?(.+?), và giao cho (.+?)\.?$", mucdich)
    if m:
        nv.update(loai = LOAI_THUTHAP, soluong = int(m.group(1)), vatpham = m.group(2).strip(), npc = m.group(3).strip())
        # "Nghe nói ở Đông Hải Ngư Thôn đánh Binh Tôm sẽ có Càng Lớn"
        m2 = re.search(r"ở (.+?) đánh (.+?) (?:sẽ|thì|có thể) ", motachitiet)
        if m2:
            nv.update(bando = m2.group(1).strip(), quai = m2.group(2).strip())
        return nv
    m = re.match(r"Thu mua (\d+) (?:cái |chiếc )?(.+?), và giao cho (.+?)\.?$", mucdich)
    if m:
        nv.update(loai = LOAI_THUMUA, soluong = int(m.group(1)), vatpham = m.group(2).strip(), npc = m.group(3).strip())
        # "Thạch Sư nhờ ta đi Chủ Tiệm Vũ Khí Tề Quốc thu mua Thuý Mộc Kiếm"
        m2 = re.search(r"đi (Chủ Tiệm .+?) (?:thu )?mua ", motachitiet)
        if m2:
            nv["cuahang"] = m2.group(1).strip()
        return nv
    m = re.match(r"Thăm [Vv]iếng (.+?)\.?$", mucdich)
    if m:
        nv.update(loai = LOAI_THAMVIENG, npc = m.group(1).strip())
        m2 = re.search(r"bảo ta đi tới (.+?) để", motachitiet)
        if m2:
            nv["bando"] = m2.group(1).strip()
        return nv
    m = re.match(r"Tăng lên (\d+) điểm Kinh nghiệm", mucdich, re.IGNORECASE)
    if m:
        nv.update(loai = LOAI_LUYENTAP, can = int(m.group(1)))
        return nv
    m = re.match(r"Tăng lên (\d+) điểm Tiềm Năng", mucdich, re.IGNORECASE)
    if m:
        nv.update(loai = LOAI_DULICH, can = int(m.group(1)))
        return nv
    m = re.match(r"Bắt (.+?) rồi trở về", mucdich)
    if m:
        nv.update(loai = LOAI_BATYEUQUAI, quai = m.group(1).strip())
        # "Nghe nói ở Xích Bích có thể bắt được Thuỷ Tặc"
        m2 = re.search(r"ở (.+?) (?:có thể )?bắt được", motachitiet)
        if m2:
            nv["bando"] = m2.group(1).strip()
        return nv
    return nv


def phantichcuahang(cuahang):
    # "Chủ Tiệm Vũ Khí Tần Quốc" -> ("Chủ Tiệm Vũ Khí", bản đồ Tần Quốc); đuôi là tên bản đồ bất kỳ ("Tân Thủ Thôn", "Nước Ngụy"...);
    # không ghi nơi ("Chủ Tiệm Y Dược") thì ở Tân Thủ Thôn
    tus = (cuahang or "").split()
    for sotu in (3, 2):
        if len(tus) > sotu + 1:
            noi = tus[-sotu:]
            # "Nước Ngụy" = "Ngụy Quốc"
            idbando = timbandotheoten(" ".join(noi[1:] + ["Quốc"]) if noi[0] == "Nước" else " ".join(noi))
            if idbando:
                return " ".join(tus[:-sotu]), idbando
    return " ".join(tus), BANDO_TANTHUTHON


def laysolanhomnay(loithoai):
    # "Số lần nhiệm vụ đã tích lũy ngày hôm nay: 29 lần" trong lời NPC giao nhiệm vụ (sau "Tiếp nhận nhiệm vụ") -> 29, không có thì None
    m = re.search(r"tích lũy ngày hôm nay\s*[:：]\s*(\d+)", boma(loithoai or ""))
    return int(m.group(1)) if m else None


def is_dutiendo(nv):
    # Mọi dòng tiến độ đều đủ
    if nv and nv.get("tiendos"):
        return all(a >= b for _, a, b in nv["tiendos"])
    return bool(nv and nv.get("tiendo") and nv["tiendo"][1] and nv["tiendo"][0] >= nv["tiendo"][1])


def motanhiemvu(nv):
    if not nv:
        return "không có nhiệm vụ sư môn"
    chu = f"{TENLOAI.get(nv['loai'], nv['ten'])} (lượt {nv['luot']})"
    if nv["is_xong"]:
        return chu + " – xong, về trả"
    # Nơi bot sẽ tới (đọc từ mô tả) để xem log biết bóc tách đúng chưa: "-> Hàn Quốc (149, 143)"
    dich = ""
    if isinstance(nv.get("bando"), int) and nv["bando"] in BANDOCONG_MAP:
        dich = f" -> {BANDOCONG_MAP[nv['bando']][0]}{' ' + str(nv['toado']) if nv.get('toado') else ''}"
    return (f"{chu}: {nv['mucdich']}" if nv["mucdich"] else chu) + dich


# --- Vị trí NPC / quái -------------------------------------------------------------------------------------------------------------

def _thumucgoc():
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))


def _thumucvitri():
    return os.path.join(_thumucgoc(), "_internal", "vitridoituong")


_bandonho = {"duongdan": None, "dulieu": {}}


def _taibandonho(thumucgame):
    # Biểu tượng trên bản đồ nhỏ của mọi bản đồ: đoạn chữ trong map/<id>.dat, mỗi dòng "<loại> (<x>,<y>) <số dòng tên>" (loại 0 = cổng,
    # 1 = NPC, 2 Bảo Khố, 3 Giáp Trụ / Trang Phục, 4 Kim Hoàn, 5 Vũ Khí, 6 Sửa Chữa, 7 Y Dược, 8 Dịch Trạm, 9 Tạp Hóa, 10 Tửu Lâu), tên
    # là dòng đó (đếm từ 0) của menu/main/vl.dat, NPC cửa hàng các nước ghi "<danh hiệu> <tên riêng>" ("Chủ Tiệm Vũ Khí Ô Địch").
    # -> {id bản đồ: [(loại, x, y, tên)]}. Đọc hết file bản đồ (~125MB) mất vài giây nên lưu đệm _internal/bandonho_cache.json theo
    # tên + kích thước các file đó (không theo thời điểm sửa: file đệm nằm trong repo, dùng chung cho mọi máy)
    if _bandonho["duongdan"] == thumucgame:
        return _bandonho["dulieu"]
    dulieu = {}
    try:
        thumucbando = os.path.join(thumucgame, "map")
        tenfiles = sorted(f for f in os.listdir(thumucbando) if f.endswith(".dat") and f[:-4].isdigit())
        dau = [os.path.join(thumucgame, "menu", "main", "vl.dat")] + [os.path.join(thumucbando, f) for f in tenfiles]
        dau = "|".join(f"{os.path.basename(p)}:{os.path.getsize(p)}" for p in dau)
        duongdandem = os.path.join(_thumucgoc(), "_internal", "bandonho_cache.json")
        try:
            with open(duongdandem, encoding = "utf-8") as file:
                dem = json.load(file)
            if dem.get("dau") == dau:
                dulieu = {int(k): [tuple(m) for m in v] for k, v in dem["bando"].items()}
        except (OSError, ValueError, KeyError):
            pass
        if not dulieu:
            with open(os.path.join(thumucgame, "menu", "main", "vl.dat"), encoding = "utf-8-sig") as file:
                tens = file.read().splitlines()
            for tenfile in tenfiles:
                with open(os.path.join(thumucbando, tenfile), "rb") as file:
                    noidung = file.read()
                mucs = []
                for loai, x, y, stt in re.findall(rb"(\d+) \((\d+),(\d+)\) (\d+)\r\n", noidung):
                    stt = int(stt)
                    if stt < len(tens) and tens[stt].strip():
                        muc = (int(loai), int(x), int(y), tens[stt].strip())
                        if muc not in mucs:
                            mucs.append(muc)
                if mucs:
                    dulieu[int(tenfile[:-4])] = mucs
            with open(duongdandem, "w", encoding = "utf-8") as file:
                json.dump({"dau": dau, "bando": dulieu}, file, ensure_ascii = False, separators = (",", ":"))
    except OSError as err:
        print(f"[SƯ MÔN] Không đọc được bản đồ nhỏ của game: {err}")
    if dulieu:
        _bandonho.update(duongdan = thumucgame, dulieu = dulieu)
    return dulieu


def _laynpcbandonho(thumucgame):
    # NPC trên bản đồ nhỏ dạng [(tên, bản đồ, x, y)], bỏ cổng (loại 0)
    if not thumucgame:
        return []
    return [(ten, idbando, x, y) for idbando, mucs in _taibandonho(thumucgame).items() for loai, x, y, ten in mucs if loai]


_questlink = {"duongdan": None, "dulieu": {}}


def _taiquestlink(thumucgame):
    # menu/quest/questlink.txt (dòng "nhóm,số,thứ tự tên,bản đồ,x,y") + questname.txt (dòng thứ tự tên, dòng đầu "test" = 0)
    # -> {tên: (bản đồ, x, y)}; tên nhiều chỗ thì lấy chỗ đầu tiên
    if _questlink["duongdan"] == thumucgame:
        return _questlink["dulieu"]
    dulieu = {}
    try:
        with open(os.path.join(thumucgame, "menu", "quest", "questname.txt"), encoding = "utf-8-sig") as file:
            tens = file.read().splitlines()
        with open(os.path.join(thumucgame, "menu", "quest", "questlink.txt"), encoding = "utf-8-sig") as file:
            for dong in file:
                cot = dong.strip().split(",")
                if len(cot) < 6:
                    continue
                try:
                    stt, idbando, x, y = int(cot[2]), int(cot[3]), int(cot[4]), int(cot[5])
                except ValueError:
                    continue
                if 0 < stt < len(tens) and tens[stt].strip():
                    dulieu.setdefault(tens[stt].strip(), (idbando, x, y))
    except OSError as err:
        print(f"[SƯ MÔN] Không đọc được questlink của game: {err}")
    _questlink.update(duongdan = thumucgame, dulieu = dulieu)
    return dulieu


class SoVitri:
    # Vị trí NPC / quái bot thấy được, ghi theo từng nhân vật (_internal/vitridoituong/<ID>.json, nhiều cửa sổ không ghi đè nhau),
    # đọc thì gộp file của mọi nhân vật: {"npc": {tên: [bản đồ, x, y]}, "quai": {tên: {"<bản đồ>": [x, y]}},
    # "cuahang": {"<bản đồ>|<tên / danh hiệu NPC>": {"luc": lúc đọc, "hang": [[ô, giá, tên], ...]}}} (hàng đọc được lần mở cửa hàng gần nhất),
    # "dadi": {"<bản đồ>": [[x, y], ...]}} (ô nhân vật đã đứng ở bản đồ thành / môn phái: chắc chắn đi được, làm điểm di chuyển về sau)
    def __init__(self):
        self._khoa = threading.Lock()
        self._idnguoichoi = None
        self._cuatoi = {"npc": {}, "quai": {}, "cuahang": {}, "dadi": {}}
        # Ô đã đi dạng {id bản đồ: set((x, y))} cho nhanh, lưu ra "dadi" lúc ghi file
        self._dadi = {}
        self._is_doi = False
        self._lucluu = 0.
        self._gop = None
        self._lucgop = 0.

    def nap(self, idnguoichoi):
        with self._khoa:
            if idnguoichoi == self._idnguoichoi:
                return
            self._luu()
            self._idnguoichoi = idnguoichoi
            self._cuatoi = self._docfile(os.path.join(_thumucvitri(), f"{idnguoichoi}.json"))
            self._dadi = {int(b): {tuple(o) for o in dsos} for b, dsos in self._cuatoi["dadi"].items()}
            self._gop = None

    @staticmethod
    def _docfile(duongdan):
        try:
            with open(duongdan, encoding = "utf-8") as file:
                dulieu = json.load(file)
            return {"npc": dict(dulieu.get("npc") or {}), "quai": dict(dulieu.get("quai") or {}), "cuahang": dict(dulieu.get("cuahang") or {}),
                    "dadi": dict(dulieu.get("dadi") or {})}
        except (OSError, ValueError):
            return {"npc": {}, "quai": {}, "cuahang": {}, "dadi": {}}

    def ghinpc(self, ten, idbando, x, y):
        with self._khoa:
            cu = self._cuatoi["npc"].get(ten)
            # NPC đứng yên: chỉ ghi khi đổi chỗ hơn 2 ô (đi lại quanh chỗ đứng)
            if not cu or cu[0] != idbando or abs(cu[1] - x) + abs(cu[2] - y) > 4:
                self._cuatoi["npc"][ten] = [idbando, x, y]
                self._is_doi = True

    def ghiquai(self, ten, idbando, x, y):
        with self._khoa:
            theobando = self._cuatoi["quai"].setdefault(ten, {})
            cu = theobando.get(str(idbando))
            if not cu or abs(cu[0] - x) + abs(cu[1] - y) > 20:
                theobando[str(idbando)] = [x, y]
                self._is_doi = True

    def ghicuahang(self, idbando, tennpcs, hang):
        # Hàng của cửa hàng vừa mở, ghi theo cả tên riêng lẫn danh hiệu NPC
        with self._khoa:
            for ten in tennpcs:
                if ten:
                    self._cuatoi["cuahang"][f"{idbando}|{ten}"] = {"luc": time.time(), "hang": [list(m) for m in hang]}
            self._is_doi = True

    def ghidadi(self, idbando, x, y):
        # Ô nhân vật đang đứng (đã đi tới được) ở bản đồ thành / môn phái
        with self._khoa:
            os_ = self._dadi.setdefault(idbando, set())
            if (x, y) not in os_:
                os_.add((x, y))
                self._is_doi = True

    def laydadi(self, idbando):
        # Mọi ô đã đi ở bản đồ này, gộp mọi nhân vật -> set((x, y))
        kq = {tuple(o) for o in self._laygop()["dadi"].get(str(idbando), [])}
        with self._khoa:
            return kq | self._dadi.get(idbando, set())

    def luu(self, is_ngay = False):
        with self._khoa:
            if is_ngay or time.time() - self._lucluu > 60.:
                self._luu()

    def _luu(self):
        self._lucluu = time.time()
        if not self._is_doi or not self._idnguoichoi:
            return
        from tienich_xq import thaythefile
        duongdan = os.path.join(_thumucvitri(), f"{self._idnguoichoi}.json")
        self._cuatoi["dadi"] = {str(b): sorted(list(o) for o in os_) for b, os_ in self._dadi.items()}
        try:
            os.makedirs(os.path.dirname(duongdan), exist_ok = True)
            with open(duongdan + ".tmp", "w", encoding = "utf-8") as file:
                json.dump(self._cuatoi, file, ensure_ascii = False, separators = (",", ":"))
            thaythefile(duongdan + ".tmp", duongdan)
            self._is_doi = False
            self._gop = None
        except Exception as err:
            print(f"[SƯ MÔN] Lỗi lưu vị trí đối tượng: {err}")

    def _laygop(self):
        # Gộp file của mọi nhân vật, đọc lại tối đa mỗi 30s; của mình ghi đè cùng tên
        if self._gop is None or time.time() - self._lucgop > 30.:
            gop = {"npc": {}, "quai": {}, "cuahang": {}, "dadi": {}}
            try:
                tenfiles = os.listdir(_thumucvitri())
            except OSError:
                tenfiles = []
            for tenfile in tenfiles:
                if tenfile.endswith(".json"):
                    dulieu = self._docfile(os.path.join(_thumucvitri(), tenfile))
                    gop["npc"].update(dulieu["npc"])
                    for ten, theobando in dulieu["quai"].items():
                        gop["quai"].setdefault(ten, {}).update(theobando)
                    # Cùng cửa hàng: lấy lần đọc mới nhất
                    for khoa, ch in dulieu["cuahang"].items():
                        if ch.get("luc", 0) >= gop["cuahang"].get(khoa, {}).get("luc", 0):
                            gop["cuahang"][khoa] = ch
                    for idbando, os_ in dulieu["dadi"].items():
                        gop["dadi"].setdefault(idbando, []).extend(os_)
            self._gop, self._lucgop = gop, time.time()
        with self._khoa:
            gop = {"npc": dict(self._gop["npc"]), "quai": {k: dict(v) for k, v in self._gop["quai"].items()},
                   "cuahang": dict(self._gop["cuahang"]), "dadi": self._gop["dadi"]}
            gop["npc"].update(self._cuatoi["npc"])
            gop["cuahang"].update(self._cuatoi["cuahang"])
            for ten, theobando in self._cuatoi["quai"].items():
                gop["quai"].setdefault(ten, {}).update(theobando)
        return gop

    def timnpc(self, ten, thumucgame = None, idbando = None):
        # -> (bản đồ, x, y) hoặc None: bot từng thấy > bản đồ nhỏ của game > bảng biết sẵn > questlink. idbando: chỉ lấy NPC ở bản đồ đó
        # (cửa hàng cùng tên đầu "Chủ Tiệm Vũ Khí" có ở mọi nước)
        tens, idbandonuoc = tenthaythe(ten)
        # Tên thay thế chung cho mọi nước ("Quản Ngục") thì chỉ lấy ở nước trong tên
        idbando = idbando or idbandonuoc
        nguons = self._laynguonnpc(thumucgame)
        for tenthu in tens:
            for nguon in nguons:
                for tenxet, *vitri in sorted(nguon, key = lambda m: m[0] != tenthu):
                    if (tenxet == tenthu or is_trungten(tenthu, tenxet)) and (idbando is None or vitri[0] == idbando):
                        return tuple(vitri[:3])
        return None

    def _laynguonnpc(self, thumucgame):
        # Các nguồn vị trí NPC theo thứ tự tin cậy, mỗi nguồn [(tên, bản đồ, x, y)] (cùng tên có thể ở nhiều bản đồ)
        return ([(ten, *v[:3]) for ten, v in self._laygop()["npc"].items()], _laynpcbandonho(thumucgame),
                [(ten, *v[:3]) for ten, v in VITRINPCCODINH.items()],
                [(ten, *v[:3]) for ten, v in (_taiquestlink(thumucgame) if thumucgame else {}).items()])

    def timhang(self, idbando, tennpc, tenvatpham):
        # -> (ô, giá) của món ở cửa hàng NPC (tên riêng hoặc danh hiệu) trên bản đồ, theo lần mở gần nhất; chưa biết thì None
        tot = None
        for khoa, ch in self._laygop()["cuahang"].items():
            idbandoxet, tenxet = khoa.split("|", 1)
            if idbandoxet != str(idbando) or not (tenxet == tennpc or is_trungten(tennpc, tenxet)):
                continue
            for o, gia, ten in ch.get("hang") or []:
                if is_trungtenvatpham(tenvatpham, ten) and (not tot or ch.get("luc", 0) > tot[0]):
                    tot = (ch.get("luc", 0), int(o), int(gia))
        return tot[1:] if tot else None

    def timnpccungloai(self, tennpc, idbando, thumucgame = None):
        # Cửa hàng chưa biết chỗ: các cửa hàng ("Chủ Tiệm ...") của một nước đứng sát nhau, lấy chỗ của cửa hàng bất kỳ đã biết trên
        # bản đồ đó (bot từng thấy, questlink của game) -> (bản đồ, x, y) hoặc None
        tiento = chuanhoaten("Chủ Tiệm")
        if not chuanhoaten(tennpc).startswith(tiento):
            return None
        for nguon in self._laynguonnpc(thumucgame):
            for tenxet, *vitri in nguon:
                if vitri[0] == idbando and chuanhoaten(tenxet).startswith(tiento):
                    return tuple(vitri[:3])
        return None

    def timquai(self, ten, idbando):
        # -> (x, y) chỗ gần nhất từng thấy quái tên này trên bản đồ, hoặc None
        for tenxet, theobando in self._laygop()["quai"].items():
            if chuanhoaten(tenxet) == chuanhoaten(ten) and str(idbando) in theobando:
                return tuple(theobando[str(idbando)])
        return None


KHOANGCACHTRANHCONG = 12


def _laydiemcong(idbando):
    # Cổng của bản đồ và các điểm xuất hiện khi từ bản đồ khác sang (cạnh đó thường có cổng ngược lại, dữ liệu cổng có thể thiếu:
    # Hàn Quốc không ghi cổng sang Tuyết Phong Sơn Bí Đạo nhưng điểm xuất hiện từ đó sang (164, 244) nằm ngay trên cổng)
    diems = [(xcong, ycong) for _, xcong, ycong, _, _ in (BANDOCONG_MAP.get(idbando) or ("", ()))[1]]
    for _, (_, congs) in BANDOCONG_MAP.items():
        for idke, _, _, xden, yden in congs:
            if idke == idbando and xden is not None:
                diems.append((xden, yden))
    return diems


def dirtranhcong(idbando, diem, khoangcach = 5):
    # Điểm trong nhiệm vụ nằm sát cổng (Tuần Sơn Đào Hoa: "Sư môn (71,83)" ngay cổng (70,82) sang Đào Hoa Nguyên): tới đó là bị chuyển bản
    # đồ, nên lùi ra cách cổng gần nhất `khoangcach` ô theo hướng từ cổng ra điểm (trùng cổng thì hướng về điểm xuất hiện / tâm các cổng)
    congs = _laydiemcong(idbando)
    if not congs:
        return diem
    cong = min(congs, key = lambda c: math.dist(c, diem))
    if math.dist(cong, diem) >= khoangcach:
        return diem
    dx, dy = diem[0] - cong[0], diem[1] - cong[1]
    if not (dx or dy):
        tam = (sum(c[0] for c in congs) / len(congs), sum(c[1] for c in congs) / len(congs))
        dx, dy = tam[0] - cong[0], tam[1] - cong[1]
        if not (dx or dy):
            dx, dy = 1, 1
    do = math.hypot(dx, dy)
    return round(cong[0] + dx * khoangcach / do), round(cong[1] + dy * khoangcach / do)


def laydiemluoi(idbando, buoc = 30):
    # Đi khắp bản đồ (thích khách trốn đâu đó trên bản đồ): lưới điểm cách nhau buoc ô trong khung bao các cổng / điểm xuất hiện,
    # đi theo hàng zíc zắc, bỏ điểm sát cổng
    congs = _laydiemcong(idbando)
    if not congs:
        return []
    xmin, xmax = min(c[0] for c in congs), max(c[0] for c in congs)
    ymin, ymax = min(c[1] for c in congs), max(c[1] for c in congs)
    diems = []
    for hang, y in enumerate(range(ymin, ymax + 1, buoc)):
        xs = list(range(xmin, xmax + 1, buoc))
        for x in (xs if hang % 2 == 0 else xs[::-1]):
            if all(abs(x - c[0]) + abs(y - c[1]) >= KHOANGCACHTRANHCONG for c in congs):
                diems.append((x, y))
    return diems or laydiemkhampha(idbando)


def laydiemkhampha(idbando, tam = None):
    # Chưa biết NPC / quái ở đâu trên bản đồ: đi vòng quanh tâm (tam, hoặc tâm các cổng của bản đồ) theo 2 vòng 20 / 40 ô.
    # Bỏ mọi điểm cách cổng / điểm xuất hiện dưới KHOANGCACHTRANHCONG ô (đi tới đó là bị chuyển bản đồ)
    congs = _laydiemcong(idbando)
    if tam is None:
        if not congs:
            return []
        tam = (sum(d[0] for d in congs) // len(congs), sum(d[1] for d in congs) // len(congs))
    xtam, ytam = tam
    diems = [(xtam, ytam)]
    for bankinh in (20, 40):
        diems += [(xtam + dx * bankinh, ytam + dy * bankinh) for dx, dy in ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))]
    return [d for d in diems if d[0] > 0 and d[1] > 0
            and all(abs(d[0] - c[0]) + abs(d[1] - c[1]) >= KHOANGCACHTRANHCONG for c in congs)]
