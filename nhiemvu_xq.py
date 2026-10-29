# Nhiệm vụ sư môn: đọc nội dung nhiệm vụ trong cửa sổ nhiệm vụ của game, phân loại và tách các thông tin cần làm; vị trí NPC / quái
# (bảng có sẵn, file game, tự ghi lại mỗi khi thấy). Phần làm nhiệm vụ nằm ở tactu_sumon_xq.py.
#
# Cửa sổ nhiệm vụ ([thông tin game] + TG_NHIEMVU, moitruong.get_danhsachmucnhiemvu): danh sách mục theo thứ tự hiển thị, mục cha
# (vd "Nhiệm Vụ Sư Môn") không thụt đầu dòng, mục con thụt 2 dấu cách ("  Bắt Yêu Quái", "  Luyện Tập(Xong)"); mô tả của mục con:
#   "<Tên> (Lượt thứ N)\nMục đích nhiệm vụ：\n    <mục đích>\n[Nâng cao kinh nghiệm: 0/5720\n]Mô tả nhiệm vụ：\n    <mô tả>"
# Máy chủ tự gửi lại cả danh sách khi nhiệm vụ đổi (không cần mở cửa sổ).
import json
import os
import re
import sys
import threading
import time
import unicodedata

from bando_xq import layidbandotheoten, BANDOCONG_MAP
from hangso_xq import BANDO_TANTHUTHON, BANDO_CONLUAN, BANDO_MAOSON, BANDO_THUCSON, BANDO_DUONGMON, BANDO_DAOHOANGUYEN, BANDO_VANMONGCOC

MUCSUMON = "Nhiệm Vụ Sư Môn"
SOLUOTSUMONTOIDA = 20

LOAI_DENTIM = "dentim"          # Đi tìm Thạch Sư: tới NPC phụ nhận việc Thu thập / Mua sắm
LOAI_THUTHAP = "thuthap"        # Thu thập N cái <vật phẩm>, và giao cho <NPC>
LOAI_THUMUA = "thumua"          # Thu mua N <vật phẩm>, và giao cho <NPC>
LOAI_THAMVIENG = "thamvieng"    # Thăm Viếng <NPC>
LOAI_LUYENTAP = "luyentap"      # Tăng lên N điểm Kinh nghiệm
LOAI_DULICH = "dulich"          # Tăng lên N điểm Tiềm Năng
LOAI_BATYEUQUAI = "batyeuquai"  # Bắt <quái> rồi trở về
LOAI_KHONGRO = "khongro"

TENLOAI = {LOAI_DENTIM: "Đi tìm", LOAI_THUTHAP: "Thu thập", LOAI_THUMUA: "Mua sắm", LOAI_THAMVIENG: "Thăm viếng", LOAI_LUYENTAP: "Luyện tập",
           LOAI_DULICH: "Du lịch", LOAI_BATYEUQUAI: "Bắt yêu quái", LOAI_KHONGRO: "Chưa rõ"}

# Bản đồ của môn phái (Hồi môn phái "dGludmF0 1" về đây)
BANDOMONPHAI = {"conluan": BANDO_CONLUAN, "maoson": BANDO_MAOSON, "thucson": BANDO_THUCSON, "duongmon": BANDO_DUONGMON,
                "daohoanguyen": BANDO_DAOHOANGUYEN, "vanmongcoc": BANDO_VANMONGCOC}

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
    return layidbandotheoten(ten)


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
    tiendo = re.search(r"Nâng cao [^:：\n]*[:：]\s*(\d+)\s*/\s*(\d+)", mucdich)
    mucdich = re.sub(r"Nâng cao [^\n]*", "", mucdich)
    mucdich = " ".join(mucdich.split())
    motachitiet = " ".join(motachitiet.split())
    nv = {"ten": ten, "is_xong": is_xong, "luot": int(luot.group(1)) if luot else 0, "loai": LOAI_KHONGRO, "mucdich": mucdich,
          "mota": motachitiet, "tiendo": (int(tiendo.group(1)), int(tiendo.group(2))) if tiendo else None}

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
    # "Chủ Tiệm Vũ Khí Tần Quốc" -> ("Chủ Tiệm Vũ Khí", bản đồ Tần Quốc); không ghi nước ("Chủ Tiệm Y Dược") thì ở Tân Thủ Thôn
    tus = (cuahang or "").split()
    for sotu in (2, 3):
        if len(tus) > sotu:
            nuoc = tus[-sotu:]
            # "Nước Ngụy" = "Ngụy Quốc"
            idbando = timbandotheoten(" ".join(nuoc[1:] + ["Quốc"]) if nuoc[0] == "Nước" else " ".join(nuoc))
            if idbando and idbando % 10 == 0 and idbando <= 80:
                return " ".join(tus[:-sotu]), idbando
    return " ".join(tus), BANDO_TANTHUTHON


def is_dutiendo(nv):
    return bool(nv and nv.get("tiendo") and nv["tiendo"][1] and nv["tiendo"][0] >= nv["tiendo"][1])


def motanhiemvu(nv):
    if not nv:
        return "không có nhiệm vụ sư môn"
    chu = f"{TENLOAI.get(nv['loai'], nv['ten'])} (lượt {nv['luot']})"
    if nv["is_xong"]:
        return chu + " – xong, về trả"
    return f"{chu}: {nv['mucdich']}" if nv["mucdich"] else chu


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
    # kích thước + thời điểm sửa của các file đó
    if _bandonho["duongdan"] == thumucgame:
        return _bandonho["dulieu"]
    dulieu = {}
    try:
        thumucbando = os.path.join(thumucgame, "map")
        tenfiles = sorted(f for f in os.listdir(thumucbando) if f.endswith(".dat") and f[:-4].isdigit())
        dau = [os.path.join(thumucgame, "menu", "main", "vl.dat")] + [os.path.join(thumucbando, f) for f in tenfiles]
        dau = "|".join(f"{os.path.getsize(p)}:{int(os.path.getmtime(p))}" for p in dau)
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
    # "cuahang": {"<bản đồ>|<tên / danh hiệu NPC>": {"luc": lúc đọc, "hang": [[ô, giá, tên], ...]}}} (hàng đọc được lần mở cửa hàng gần nhất)
    def __init__(self):
        self._khoa = threading.Lock()
        self._idnguoichoi = None
        self._cuatoi = {"npc": {}, "quai": {}, "cuahang": {}}
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
            self._gop = None

    @staticmethod
    def _docfile(duongdan):
        try:
            with open(duongdan, encoding = "utf-8") as file:
                dulieu = json.load(file)
            return {"npc": dict(dulieu.get("npc") or {}), "quai": dict(dulieu.get("quai") or {}), "cuahang": dict(dulieu.get("cuahang") or {})}
        except (OSError, ValueError):
            return {"npc": {}, "quai": {}, "cuahang": {}}

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
            gop = {"npc": {}, "quai": {}, "cuahang": {}}
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
            self._gop, self._lucgop = gop, time.time()
        with self._khoa:
            gop = {"npc": dict(self._gop["npc"]), "quai": {k: dict(v) for k, v in self._gop["quai"].items()},
                   "cuahang": dict(self._gop["cuahang"])}
            gop["npc"].update(self._cuatoi["npc"])
            gop["cuahang"].update(self._cuatoi["cuahang"])
            for ten, theobando in self._cuatoi["quai"].items():
                gop["quai"].setdefault(ten, {}).update(theobando)
        return gop

    def timnpc(self, ten, thumucgame = None, idbando = None):
        # -> (bản đồ, x, y) hoặc None: bot từng thấy > bản đồ nhỏ của game > bảng biết sẵn > questlink. idbando: chỉ lấy NPC ở bản đồ đó
        # (cửa hàng cùng tên đầu "Chủ Tiệm Vũ Khí" có ở mọi nước)
        for nguon in self._laynguonnpc(thumucgame):
            for tenxet, *vitri in sorted(nguon, key = lambda m: m[0] != ten):
                if (tenxet == ten or is_trungten(ten, tenxet)) and (idbando is None or vitri[0] == idbando):
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
