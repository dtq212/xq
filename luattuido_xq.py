# Luật túi đồ: _internal/luattuido.json (sửa ở tab "Túi đồ" trên bảng điều khiển, hoặc bằng tay; bot tự đọc lại khi file đổi).
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
#   "muabu": đứng gần NPC ở Tân Thủ Thôn mà còn ít hơn "duoi" món (đếm cả các chồng) thì mua cho đủ "muatoi". Mỗi mục: {"bat": true,
#           "vatpham": tên, "npc": tên NPC bán, "o": số ô trong cửa hàng NPC, "dongia": giá 1 món, "duoi": N, "muatoi": M,
#           "monphai": "" = mọi môn phái hoặc "maoson", "vanmongcoc"..., "chikhi": "" = luôn, "trieuhoibaothu" = chỉ khi bật triệu hồi
#           bảo thú giang hồ}. Mua lần lượt từ trên xuống trong số ngân lượng đang có, chừa NGANLUONGGIULAI
import copy
import json
import os
import sys
import threading
import unicodedata

from hangso_xq import (VATPHAMTUDONGNHATs, BAOTHUVATPHAMs, BUAGIAY, HYDUONG, TRANKY, TUIPHAPBAO, SOCAPDOANTHACH, TRUNGCAPDOANTHACH,
                       CAOCAPDOANTHACH, CHIENQUOCLENH, NHIEPHONLINH, CHUONGHAMTHIEN, BATTIENDON, CUULONGTHANHOATRAO, DAIPHAPLUCTHACH,
                       TIEUPHAPLUCTHACH, DAIHUYETTHACH, TIEUHUYETTHACH, ANTHANHOAN, THUONGPHUONGBAOKIEM, DAUNANH, TIEUDAOTAN, QUYNGUYENDON,
                       KIMTANGTAN, KHIMACHDON, XALOITU, NGANHANHTU, TUTINHDON, PHUCSINHDON, THANHTAMDAN, KHUMATAN, THILUYENDON, THILUYENQUA,
                       CAOCAPBAOTHUTHUCPHAM, ANXAPHU, NHANSAM, TAITAOHOAN, HOITHANHPHU, THIENLYHUUTINH, PHIHANHPHU, THOHANHCHAU, CAOBOCTACDAN,
                       TANGBAODO, THIENNGUYENDON, THIENNGUYENDAN, HOIBANGPHU, TINHNGUYENDON, CUONGTHIPHU, NGUYENLIEULUYENDONs,
                       CHUTIEMTAPHOA, CHUTUULAU, LAOTUU, DUAHAU)

HANHDONG_GIU = "giu"
HANHDONG_BAN = "ban"
HANHDONG_VUT = "vut"
# Chỉ còn để đọc luật cũ (trước khi Cất kho thành bảng riêng "catkho")
HANHDONG_CATKHO = "catkho"
RUONGTUDONG = 0
TENHANHDONG = {HANHDONG_GIU: "Giữ", HANHDONG_BAN: "Bán", HANHDONG_VUT: "Vứt"}
DIEUKIENs = ("ten", "tenchua", "loai", "mota")
TENDIEUKIEN = {"ten": "Tên đúng", "tenchua": "Tên chứa", "loai": "Loại chứa", "mota": "Mô tả chứa"}
TRUONGMUABU = ("vatpham", "npc", "o", "dongia", "duoi", "muatoi", "monphai", "chikhi")
TENTRUONGMUABU = {"vatpham": "Vật phẩm", "npc": "NPC bán", "o": "Ô trong cửa hàng", "dongia": "Đơn giá", "duoi": "Mua khi dưới",
                  "muatoi": "Mua cho đủ", "monphai": "Môn phái (trống = tất cả)", "chikhi": "Chỉ mua khi"}
CHIKHI_LUON = ""
CHIKHI_TRIEUHOIBAOTHU = "trieuhoibaothu"
TENCHIKHI = {CHIKHI_LUON: "Luôn", CHIKHI_TRIEUHOIBAOTHU: "Bật triệu hồi bảo thú giang hồ"}


def _khongtrung(*tens):
    kq = []
    for ten in tens:
        if ten not in kq:
            kq.append(ten)
    return kq


# Luật viết cứng trước đây trong tactu (bán rác) / hangso_xq (VATPHAMKHONGBANs, LOAIVATPHAMKHONGBANs, MOTAVATPHAMKHONGBANs)
LUATMACDINH = [
    {"hanhdong": HANHDONG_GIU, "ghichu": "Danh sách không bán (cũ)", "ten": _khongtrung(
        *VATPHAMTUDONGNHATs, *BAOTHUVATPHAMs, BUAGIAY, HYDUONG, TRANKY, TUIPHAPBAO, SOCAPDOANTHACH, TRUNGCAPDOANTHACH, CAOCAPDOANTHACH,
        CHIENQUOCLENH, NHIEPHONLINH, CHUONGHAMTHIEN, BATTIENDON, CUULONGTHANHOATRAO, DAIPHAPLUCTHACH, TIEUPHAPLUCTHACH, DAIHUYETTHACH,
        TIEUHUYETTHACH, ANTHANHOAN, THUONGPHUONGBAOKIEM, DAUNANH, TIEUDAOTAN, QUYNGUYENDON, KIMTANGTAN, KHIMACHDON, XALOITU, NGANHANHTU,
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
    {"vatpham": TRANKY, "npc": CHUTIEMTAPHOA, "o": 6, "dongia": 60, "duoi": 1999, "muatoi": 1999, "monphai": "vanmongcoc"},
    {"vatpham": DAUNANH, "npc": CHUTIEMTAPHOA, "o": 7, "dongia": 400, "duoi": 30, "muatoi": 30, "monphai": "vanmongcoc"},
    {"vatpham": BUAGIAY, "npc": CHUTIEMTAPHOA, "o": 1, "dongia": 10, "duoi": 999, "muatoi": 999, "monphai": "maoson"},
    {"vatpham": CAOCAPBAOTHUTHUCPHAM, "npc": CHUTIEMTAPHOA, "o": 18, "dongia": 400, "duoi": 30, "muatoi": 30, "chikhi": CHIKHI_TRIEUHOIBAOTHU},
    {"vatpham": LAOTUU, "npc": CHUTUULAU, "o": 3, "dongia": 1150, "duoi": 30, "muatoi": 30, "chikhi": CHIKHI_TRIEUHOIBAOTHU},
    {"vatpham": DUAHAU, "npc": CHUTUULAU, "o": 4, "dongia": 1100, "duoi": 30, "muatoi": 30, "chikhi": CHIKHI_TRIEUHOIBAOTHU},
]

_cache = {"dulieu": None, "mtime": None}
_khoa = threading.Lock()


def duongdanluat():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "luattuido.json")


def chuanhoa(chu):
    # So khớp không phân biệt hoa thường, dựng sẵn dấu (NFC), gộp khoảng trắng
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
    for truong in ("vatpham", "npc", "monphai"):
        muc[truong] = str(muc.get(truong) or "").strip()
    if muc.get("chikhi") not in TENCHIKHI:
        muc["chikhi"] = CHIKHI_LUON
    for truong in ("o", "dongia", "duoi", "muatoi"):
        try:
            muc[truong] = max(0, int(muc.get(truong) or 0))
        except (TypeError, ValueError):
            muc[truong] = 0
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


def _chuanhoa(dulieu):
    luats, catkhos = list(dulieu.get("luat") or []), dulieu.get("catkho")
    if catkhos is None:
        # File cũ (Cất kho còn là hành động / cờ 🗄 trong "luat"): chuyển sang bảng Cất kho
        catkhos = [l for l in luats if l.get("hanhdong") == HANHDONG_CATKHO or l.get("is_catkho")]
        luats = [l for l in luats if l.get("hanhdong") != HANHDONG_CATKHO]
    return {"luat": [_chuanhoaluat(l) for l in luats], "muabu": [_chuanhoamuabu(m) for m in dulieu.get("muabu") or []],
            "catkho": [_chuanhoacatkho(l) for l in catkhos], "is_catkhosauban": bool(dulieu.get("is_catkhosauban", True))}


def macdinh():
    return _chuanhoa({"luat": copy.deepcopy(LUATMACDINH), "muabu": copy.deepcopy(MUABUMACDINH), "catkho": []})


def tailuat():
    # Đọc lại khi file đổi. Chưa có file thì tạo từ luật mặc định; file hỏng thì dùng bản đọc được gần nhất, chưa đọc được lần nào thì
    # dùng luật mặc định (không bao giờ chạy với bộ luật rỗng do lỗi đọc: rỗng là bán hết)
    duongdan = duongdanluat()
    with _khoa:
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
