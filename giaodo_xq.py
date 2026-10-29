# Giao tiền / đồ cho nhân vật khác ở Tân Thủ Thôn (cạnh Chủ Tiệm Tạp Hóa): phần dùng chung cho giao diện, Telegram và bot
# (tactu_giaodo_xq). Một yêu cầu giao: {"id": mã, "nguoinhan": tên người nhận, "tien": ngân lượng, "giulaitien": None hoặc số,
# "vatphams": [[tên, số lượng, giữ lại], ...]}
#   Tiền: "giulaitien" khác None = giao hết, chừa lại chừng đó (tính lúc giao, sau khi đã trừ tiền phù / Hồi Thành Phù dọc đường);
#         None = giao đúng "tien"
#   Đồ: số lượng TATCA = giao hết món đó, chừa lại "giữ lại" cái (thường 0)
# Lệnh game: give <người nhận> <id món>#<số> x6 $<tiền>
#   người nhận là người chơi: ID người chơi (thập phân, không "#", như "team + <id>"); đối tượng khác: id đối tượng hệ 16 kèm "#"
#   6 ô vật phẩm: id đối tượng hệ 16 "#" số lượng, ô trống "0#0"; nhiều hơn 6 món / chồng thì tách thành nhiều lệnh (tiền ở lệnh đầu)
import re
import time
import uuid

SOOVATPHAMMOILENH = 6
TATCA = -1
# Chữ nghĩa là "hết" (giao toàn bộ) và "chừa lại" trong ô tiền / số lượng đồ
CHUHETs = ("hết", "het", "tất cả", "tatca", "tat ca", "all", "*")
CHUGIULAIs = ("giữ", "giu", "chừa", "chua", "để lại", "de lai", "-")


def taoyeucau(nguoinhan, tien = 0, vatphams = (), giulaitien = None):
    return {"id": uuid.uuid4().hex[:8], "nguoinhan": str(nguoinhan).strip(), "tien": max(0, int(tien or 0)),
            "giulaitien": None if giulaitien is None else max(0, int(giulaitien)),
            "vatphams": [[str(v[0]).strip(), int(v[1]) if int(v[1]) == TATCA else max(1, int(v[1])), max(0, int(v[2]) if len(v) > 2 else 0)]
                         for v in vatphams if str(v[0]).strip()], "luctao": time.time()}


def guiyeucau(command_dict, hwnd, yeucau):
    # Gửi yêu cầu cho bot của cửa sổ hwnd qua command_dict (mỗi cửa sổ chỉ 1 lệnh chờ): bot chưa nhận lệnh giao trước thì gộp chung
    # thành danh sách, kẻo yêu cầu sau đè mất yêu cầu trước (cuaso_xq nhận cả 1 yêu cầu lẫn danh sách)
    import json
    cu = command_dict.get(hwnd)
    yeucaus = []
    if isinstance(cu, str) and cu.startswith("giaodo:"):
        try:
            dacho = json.loads(cu.split(":", 1)[1])
            yeucaus = dacho if isinstance(dacho, list) else [dacho]
        except ValueError:
            pass
    command_dict[hwnd] = "giaodo:" + json.dumps(yeucaus + [yeucau], ensure_ascii = False)


def _docso(chu):
    # "500000", "500.000", "500,000", "500k", "1.5tr" -> số; không đọc được thì None
    chu = (chu or "").strip().lower().replace(" ", "")
    khop = re.fullmatch(r"(\d+(?:[.,]\d+)?)(k|tr|m)?", chu)
    if khop and khop.group(2):
        return int(float(khop.group(1).replace(",", ".")) * {"k": 1_000, "tr": 1_000_000, "m": 1_000_000}[khop.group(2)])
    so = chu.replace(".", "").replace(",", "")
    return int(so) if so.isdigit() else None


def _dochetgiulai(chu):
    # "hết" -> (True, 0); "giữ 10k" / "chừa 10k" / "-10k" / "hết giữ 10k" -> (True, 10000); khác -> (False, None)
    chu = (chu or "").strip().lower()
    for chuhet in CHUHETs:
        if chu == chuhet:
            return True, 0
        if chu.startswith(chuhet + " "):
            chu = chu[len(chuhet):].strip()
            break
    for chugiu in CHUGIULAIs:
        if chu.startswith(chugiu):
            so = _docso(chu[len(chugiu):])
            return (True, so) if so is not None else (False, None)
    return False, None


def doctien(chu):
    # Ô tiền -> (tiền cố định, giữ lại) hoặc None khi không đọc được. "500k" -> (500000, None); "giữ 10k" -> (0, 10000); "hết" -> (0, 0);
    # để trống -> (0, None)
    if not (chu or "").strip():
        return 0, None
    is_het, giulai = _dochetgiulai(chu)
    if is_het:
        return 0, giulai
    so = _docso(chu)
    return (so, None) if so is not None else None


def docsotien(chu):
    # Chỉ số cố định (giữ cho chỗ cũ dùng); "giữ 10k" / "hết" thì None
    kq = doctien(chu)
    return kq[0] if kq and kq[1] is None else None


def docvatphams(chu):
    # "Linh Thạch cấp 5 x3; Trị Dược x hết; Bùa Giấy x giữ 100" hoặc mỗi dòng 1 món -> [[tên, số lượng | TATCA, giữ lại], ...];
    # không ghi số lượng thì là 1
    vatphams = []
    for phan in re.split(r"[;\n]+", chu or ""):
        phan = phan.strip()
        if not phan:
            continue
        khop = re.match(r"^(.*?)\s+[x×]\s+(.+)$", phan, re.I) or re.match(r"^(.*?)\s*[x×*]\s*(\d+)$", phan, re.I)
        if khop:
            ten, phansoluong = khop.group(1).strip(), khop.group(2).strip()
            is_het, giulai = _dochetgiulai(phansoluong)
            if is_het:
                vatphams.append([ten, TATCA, giulai])
                continue
            so = _docso(phansoluong)
            if so is not None:
                vatphams.append([ten, max(1, so), 0])
                continue
        vatphams.append([phan, 1, 0])
    return [v for v in vatphams if v[0]]


def _so(n):
    return f"{n:,}".replace(",", ".")


def motayeucau(yeucau, is_thucte = False):
    # "toàn bộ ngân lượng (giữ 10.000), Trị Dược ×hết" cho giao diện / Telegram; is_thucte: dùng số đã tính lúc giao (sau khi giao)
    phans = []
    if is_thucte and yeucau.get("tienthucte") is not None:
        if yeucau["tienthucte"]:
            phans.append(f"{_so(yeucau['tienthucte'])} ngân lượng")
    elif yeucau.get("giulaitien") is not None:
        phans.append("toàn bộ ngân lượng" + (f" (giữ {_so(yeucau['giulaitien'])})" if yeucau["giulaitien"] else ""))
    elif yeucau.get("tien"):
        phans.append(f"{_so(yeucau['tien'])} ngân lượng")
    vatphams = yeucau.get("vatphamthucte") if is_thucte and yeucau.get("vatphamthucte") is not None else yeucau.get("vatphams", [])
    for v in vatphams:
        ten, sl, giulai = v[0], v[1], (v[2] if len(v) > 2 else 0)
        phans.append(f"{ten} ×{'hết' + (f' (giữ {giulai})' if giulai else '') if sl == TATCA else sl}")
    return ", ".join(phans) or "(trống)"


def taolenhgiao(manguoinhan, cacmon, tien):
    # manguoinhan: chuỗi người nhận đã định dạng ("29" hoặc "65#"); cacmon: [(id đối tượng món, số lượng), ...] -> danh sách lệnh give
    lenhs = []
    nhoms = [cacmon[i:i + SOOVATPHAMMOILENH] for i in range(0, len(cacmon), SOOVATPHAMMOILENH)] or [[]]
    for i, nhom in enumerate(nhoms):
        os = [f"{iddoituong:x}#{soluong}" for iddoituong, soluong in nhom] + ["0#0"] * (SOOVATPHAMMOILENH - len(nhom))
        lenhs.append(f"give {manguoinhan} {' '.join(os)} ${tien if i == 0 else 0}")
    return lenhs


def chiamon(vatphams, cacchong):
    # Chia số lượng cần giao của mỗi món ra các chồng trong túi. cacchong: {tên: [(id đối tượng, số lượng chồng), ...]}.
    # Món "hết" thì lấy tổng đang có trừ phần giữ lại. -> ([(id, số lượng), ...], [[tên, số giao thực tế], ...], lỗi hoặc None)
    cacmon, thucte = [], []
    for v in vatphams:
        ten, can, giulai = v[0], v[1], (v[2] if len(v) > 2 else 0)
        co = sum(max(1, sl) for _, sl in cacchong.get(ten, []))
        if can == TATCA:
            can = co - giulai
            if can <= 0:
                return [], [], f"không có {ten} để giao (có {co}, giữ {giulai})"
        conlai = can
        for iddoituong, soluong in cacchong.get(ten, []):
            if conlai <= 0:
                break
            lay = min(conlai, max(1, soluong))
            cacmon.append((iddoituong, lay))
            conlai -= lay
        if conlai > 0:
            return [], [], f"không đủ {ten} (cần {can}, có {co})"
        thucte.append([ten, can])
    return cacmon, thucte, None
