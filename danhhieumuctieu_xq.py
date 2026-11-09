"""Hiện thông tin mục tiêu đang chọn ngay trong game, sửa bộ nhớ client của mình (máy chủ / người khác không thấy). 2 chế độ (giao diện
chọn theo từng cửa sổ ở đầu tab Chiến đấu, hangso_xq.CHEDOHIENMUCTIEU_*):
- Danh hiệu: game vẽ danh hiệu (+0x1134, 0x3B byte) cả cho quái, ngay trên tên (test 2026-11-05). Hàm vẽ chữ của game không xuống dòng
  => dòng cuối ghi vào danh hiệu, các dòng trên vẽ bằng hook ở chỗ game vẽ danh hiệu (MoiTruong.action_ghidongvedanhhieu; bản Aegis
  nối sau chienquoc2d.dll). Từ trên xuống:
      Kết luận: AN TOÀN - hạ nó ~12 giây, nó hạ mình ~1 phút 5 giây      (xanh lá / vàng CÂN SỨC / đỏ NGUY HIỂM / xám chưa rõ)
      Khí huyết: 19.944/55.400
      Ngoại công: 3.352, Nội công: 1.200      (đo khi nó đánh mình; có cái nào hiện cái đó)
      Ngoại kháng: 1.922, Nội kháng: 1.757    (có cái nào hiện cái đó)
  Hook lỗi thì gộp hết vào danh hiệu từ dòng Kết luận (cắt phần không vừa).
- Đuôi tên: nối 1 dòng vào sau TÊN (+0x10AC, 0x80 byte), vd "Thủ Lĩnh Thích Khách ( 29 ) ( Cấp 102) | Kết luận: ...". Bot lọc mục
  tiêu / tìm NPC / quái nhiệm vụ theo tên: phần nối bắt đầu bằng DAUNOITENMUCTIEU_BYTES, MoiTruong._get_tenthucte cắt từ đó.
- Game nhớ độ rộng chữ (px) để canh giữa: tên ở +0x112C, danh hiệu ở +0x1130 (dò xq + 0x1CFD5 / 0x1D014), chỉ tính lại khi = 0 => mỗi
  lần đổi chữ phải ghi 0 vào đó. Ô tên chỉ 0x80 byte (+0x112C là độ rộng), đừng ghi lấn.
- Số viết đủ, dấu . ngăn phần nghìn, nhãn viết đủ (người dùng yêu cầu). Màu ESC + chữ cái (hangso_xq.MAUHIENMUCTIEU_MAP); "Theo % máu":
  dòng Khí huyết xanh lá / vàng / đỏ, dòng khác trắng. Dòng Kết luận luôn tô theo mức.
- Kết luận (tinhketluan): thời gian mình hạ nó = máu nó còn / DPS mình lên nó, thời gian nó hạ mình = máu mình còn / DPS nó lên mình.
  Nó hạ mình lâu hơn HESOANTOAN lần => AN TOÀN, lâu hơn => CÂN SỨC, nhanh hơn => NGUY HIỂM. DPS mình: các cửa sổ đang đánh nó (số bay,
  uocluongmuctieu_xq.dpstheodon) cộng lại; chưa ai đánh thì hệ số DPS của mình * sát thương 1 đòn theo công thức với Kháng nó. DPS nó:
  nhịp đánh * sát thương theo Công nó (đo khi nó đánh mình) và Kháng mình. Không tính thuốc / hồi máu / né.
- Quái: chỉ số đã đo chắc lưu theo tên + cấp (_internal/thongtinquai.json, giao diện ghi) dùng luôn, khỏi đo lại. Người chơi chưa đo
  lần này thì lấy số đã lưu theo ID.
- Bỏ qua NPC (sư môn đọc tên / danh hiệu NPC cửa hàng). Số đo gộp mọi cửa sổ cùng máy như đầu tab Chiến đấu (uocluongmuctieu_xq.gopuocluong).
- Game / máy chủ ghi lại ô (vào lại tầm nhìn...) => ghi lại mỗi CHUKYGHI giây; ô khác chữ mình ghi thì nhận làm gốc mới.
- Đổi đối tượng / đổi chế độ / tắt / bot dừng: trả ô gốc (chỉ khi ô còn đúng chữ mình ghi), thôi vẽ dòng thêm.
- Hành động hiện tại của bot trên đầu nhân vật mình (ODauNhanVat, khối hook OKHOINHANVAT): game chỉ gọi vẽ danh hiệu khi ô +0x1134
  khác rỗng (xq+0x9CEB9 / 0x9C2A4 "test cl, cl; je", dò 2026-11-09) => có danh hiệu thật thì hook vẽ 1 dòng lên trên, KHÔNG đụng ô;
  ô rỗng (chưa có / "title hide") thì ghi chữ vào ô (dài quá thì ô giữ " " và hook vẽ cả dòng). Làm mới toạ độ (TacTu.action_
  lammoitrangthai) chỉ gửi lệnh "title ..." không đọc ô này; máy chủ ghi lại ô thì nhận theo danh hiệu thật / ô rỗng ở vòng sau.
"""
import re
import struct
import time

from congthucsatthuong_xq import HE_NGOAI, HE_NOI, satthuong, chonhe
from diachi_xq import DC
from hangso_xq import CHEDOHIENMUCTIEU_DANHHIEU, CHEDOHIENMUCTIEU_TEN, MAUHIENMUCTIEU_THEOMAU, NGUONGMAUHIENMUCTIEU
from hangso_xq import OKHOIMUCTIEU, OKHOINHANVAT, MAUHANHDONGTRENDAU, KICHTHUOCDONGVEDANHHIEU
from uocluongmuctieu_xq import gopuocluong, gopcongdoithu, khoaquaitheoten, DICHCONG, DICHKHANG, THOIGIANDANGDANH
from tienich_xq import read_bytes, write_bytes, taithongtinnguoichoi, taithongtinquai, DAUNOITENMUCTIEU_BYTES

CHUKYGHI = 0.3
# Ô tên +0x10AC tới ô độ rộng tên +0x112C = 0x80 byte; ô danh hiệu 0x3B byte, độ rộng danh hiệu ở +0x1130. Chừa 1 byte NUL
KICHTHUOCTEN = 0x112C - 0x10AC
KICHTHUOCDANHHIEU = 0x3B
DORONGTEN = 0x112C
DORONGDANHHIEU = 0x1130
# Màu dòng không phải Khí huyết khi chọn "Theo % máu"
MAUPHANSAU = "W"
# Gộp ước lượng mọi cửa sổ (đọc cả shared_data qua Manager, nặng) mỗi chừng này giây; % máu đọc trực tiếp mỗi lần ghi
CHUKYGOP = 1.
# Đọc lại số đã lưu (thongtinnguoichoi.json theo ID người chơi, thongtinquai.json theo tên + cấp quái; giao diện ghi) mỗi chừng này giây
CHUKYDOCKHO = 10.
# Kết luận: thời gian nó hạ mình / thời gian mình hạ nó >= HESOANTOAN => AN TOÀN, >= HESOCANSUC => CÂN SỨC, nhỏ hơn => NGUY HIỂM
HESOANTOAN = 1.5
HESOCANSUC = 1.
# (chữ, màu) theo mức kết luận; None = chưa đủ số
KETLUAN_MAP = {"antoan": ("AN TOÀN", "G"), "cansuc": ("CÂN SỨC", "Y"), "nguyhiem": ("NGUY HIỂM", "R")}
MAUCHUARO = "w"
# Chưa đo được nhịp đánh của nó: coi như 1 đòn / giây. Chưa có hệ số DPS của mình (chưa đánh mục tiêu nào biết Kháng): 1 đòn thường / giây
NHIPMACDINH = 1.
HESODPSMACDINH = 1.


def dinhdangso(n):
    # 60234 -> "60.234" (dấu . ngăn phần nghìn kiểu Việt)
    return f"{int(round(n)):,}".replace(",", ".")


def dinhdangkhoang(khoang):
    # (3332, 3367) -> "3.332-3.367", 2 đầu bằng nhau thì 1 số
    return dinhdangso(khoang[0]) if khoang[0] == khoang[1] else f"{dinhdangso(khoang[0])}-{dinhdangso(khoang[1])}"


def mamau(chu):
    return b"\x1b" + chu.encode("ascii")


def _maudongs(mau, chumau):
    # (màu dòng Khí huyết, màu các dòng khác)
    if chumau == MAUHIENMUCTIEU_THEOMAU:
        return ("G" if mau > NGUONGMAUHIENMUCTIEU[0] else ("Y" if mau > NGUONGMAUHIENMUCTIEU[1] else "R")), MAUPHANSAU
    return chumau, chumau


def taodongs(mau, khihuyet, khangs, congs, chumau = MAUHIENMUCTIEU_THEOMAU):
    # Mục tiêu -> các dòng (bytes UTF-8 có mã màu) từ trên xuống: Khí huyết, Công (nếu có), Kháng (nếu có)
    maukh, mausau = _maudongs(mau, chumau)
    dongs = [mamau(maukh) + (f"Khí huyết: {dinhdangso(khihuyet * mau / 100.)}/{dinhdangso(khihuyet)}" if khihuyet
                             else f"Khí huyết: {mau}%").encode("utf-8")]
    for bang, tens in ((congs, ("Ngoại công", "Nội công")), (khangs, ("Ngoại kháng", "Nội kháng"))):
        phans = [f"{ten}: {dinhdangso(bang[he])}" for he, ten in zip(("ngoai", "noi"), tens) if bang.get(he)]
        if phans:
            dongs.append(mamau(mausau) + ", ".join(phans).encode("utf-8"))
    return dongs


# Phần cần nhấn trong câu hành động: số đếm "1/4", toạ độ "(320, 144)", tên bản đồ sau "ở " (tới dấu câu / số / ngoặc kế tiếp).
# Giao diện (khối 📢) dùng chung
NHANHANHDONG = re.compile(r"(?P<dem>\b(?P<da>\d+)/(?P<can>\d+)\b)|(?P<toado>\(\d+,\s*\d+\))|(?<=\bở )(?P<bando>[^:·,;()\d]+[^:·,;()\d\s])")

# Câu hành động có tên đối tượng ngay sau động từ (TacTu._ghihanhdongdichuyen): (động từ, tên tới trước toạ độ "(x, y)" / hết câu).
# Tên quái có thể chứa ngoặc "( 29 ) ( Cấp 102)" nên chỉ dừng ở toạ độ
TIENTODOITUONG = re.compile(r"^(Tiếp cận để tấn công|Tấn công|Lùi giữ khoảng cách với|Đi theo|Đi nhặt|Tới mục tiêu) "
                            r"(.+?)(?=\s*\(\d+,\s*\d+\)\s*$|$)")


def tomauhanhdong(hanhdong):
    # Câu hành động -> bytes UTF-8 tô màu từng phần theo MAUHANHDONGTRENDAU (giống cách giao diện tô khối 📢)
    hanhdong = re.sub(r"(\(\d+,\s*\d+\))(?:\s+\1)+", r"\1", " ".join(str(hanhdong).split()))
    phans = []
    vitri = 0
    dau = hanhdong.find(": ")
    kqdoituong = TIENTODOITUONG.match(hanhdong)
    if kqdoituong:
        # "Tiếp cận để tấn công <tên>": động từ màu tên việc, tên đối tượng màu riêng (toạ độ sau tên tô như thường)
        phans += [("dau", kqdoituong.group(1) + " "), ("doituong", kqdoituong.group(2))]
        vitri = kqdoituong.end()
    elif 0 < dau <= 30:
        phans.append(("dau", hanhdong[:dau + 1]))
        vitri = dau + 1
    elif dau < 0 and len(hanhdong) <= 30 and not NHANHANHDONG.search(hanhdong) and not kqdoituong:
        # Câu ngắn chỉ có tên việc ("Lộ trình", "Tấn công") thì cả câu màu tên việc
        return mamau(MAUHANHDONGTRENDAU["dau"]) + hanhdong.encode("utf-8")
    for kq in NHANHANHDONG.finditer(hanhdong, vitri):
        phans.append(("thuong", hanhdong[vitri:kq.start()]))
        if kq.group("dem"):
            loai = "du" if int(kq.group("da")) >= int(kq.group("can")) else "thieu"
        else:
            loai = "toado" if kq.group("toado") else "bando"
        phans.append((loai, kq.group()))
        vitri = kq.end()
    phans.append(("thuong", hanhdong[vitri:]))
    ketqua, maucuoi = b"", None
    for loai, chu in phans:
        if not chu:
            continue
        mau = MAUHANHDONGTRENDAU[loai]
        # Khoảng trắng không cần đổi màu (đỡ tốn byte, ô chỉ 0x80)
        if mau != maucuoi and chu.strip():
            ketqua += mamau(mau)
            maucuoi = mau
        ketqua += chu.encode("utf-8")
    return ketqua


def dinhdangthoigian(giay):
    # 12 -> "12 giây", 65 -> "1 phút 5 giây", quá 10 phút -> "hơn 10 phút"
    giay = int(round(giay))
    if giay >= 600:
        return "hơn 10 phút"
    if giay < 60:
        return f"{max(giay, 1)} giây"
    return f"{giay // 60} phút" + (f" {giay % 60} giây" if giay % 60 else "")


def tinhketluan(maunoconlai, dpsminh, mauminhconlai, dpsno):
    # -> (mức "antoan" / "cansuc" / "nguyhiem" hoặc None, giây mình hạ nó, giây nó hạ mình, lý do chưa rõ)
    tminh = maunoconlai / dpsminh if maunoconlai and dpsminh else None
    tno = mauminhconlai / dpsno if mauminhconlai and dpsno else None
    if tminh is None or tno is None:
        thieus = []
        if not maunoconlai:
            thieus.append("Khí huyết")
        if not dpsminh:
            thieus.append("Kháng")
        if not dpsno:
            thieus.append("sức đánh")
        return None, tminh, tno, "chưa biết " + ", ".join(thieus) + " của nó"
    tile = tno / max(tminh, 0.1)
    muc = "antoan" if tile >= HESOANTOAN else ("cansuc" if tile >= HESOCANSUC else "nguyhiem")
    return muc, tminh, tno, ""


def taodongketluan(muc, tminh, tno, lydo):
    # Dòng Kết luận (bytes có mã màu)
    if not muc:
        return mamau(MAUCHUARO) + f"Kết luận: chưa rõ - {lydo}".encode("utf-8")
    chu, mau = KETLUAN_MAP[muc]
    return mamau(mau) + f"Kết luận: {chu} - hạ nó ~{dinhdangthoigian(tminh)}, nó hạ mình ~{dinhdangthoigian(tno)}".encode("utf-8")


def gopmotdong(dongs, sobytetoida):
    # Gộp các dòng thành 1 dòng (", " nối, bỏ mã màu từ dòng 2 nếu trùng màu) vừa sobytetoida byte; dòng không vừa thì bỏ
    ketqua = b""
    for dong in dongs:
        them = dong if not ketqua else b", " + (dong[2:] if dong[:2] == ketqua[:2] else dong)
        if len(ketqua) + len(them) > sobytetoida:
            if not ketqua:
                ketqua = catutf8(them, sobytetoida)
            break
        ketqua += them
    return ketqua


def catutf8(dulieu, sobyte):
    # Cắt bytes UTF-8 tối đa sobyte byte, không cắt giữa 1 ký tự / giữa mã màu (ESC + chữ cái)
    dulieu = dulieu[:sobyte].decode("utf-8", "ignore").encode("utf-8")
    return dulieu[:-1] if dulieu.endswith(b"\x1b") else dulieu


class ODoiTuong:
    # Ghi chữ lên 1 đối tượng (danh hiệu / đuôi tên + các dòng vẽ thêm ở khối okhoi của hook), nhớ ô gốc để trả lại
    def __init__(self, moitruong, okhoi):
        self.moitruong = moitruong
        self.okhoi = okhoi
        # Đối tượng đang bị ghi: (địa chỉ, id đối tượng, chế độ), ô gốc (bytes đủ ô), chữ (tới NUL) mình ghi lần gần nhất
        self._dangghi = None
        self._goc = b""
        self._daghi = b""
        # Dòng vẽ thêm đã đặt cho hook (so để khỏi ghi lại mỗi vòng); hook lỗi thì thôi không thử lại
        self._dongthem = None
        self._is_hookloi = False

    def get_diachi(self):
        return self._dangghi[0] if self._dangghi else 0

    @staticmethod
    def _o(chedo):
        # (offset ô chữ, kích thước, offset độ rộng) theo chế độ
        if chedo == CHEDOHIENMUCTIEU_DANHHIEU:
            return DC.NV_DANHHIEU, KICHTHUOCDANHHIEU, DORONGDANHHIEU
        return DC.NV_TEN, KICHTHUOCTEN, DORONGTEN

    def _docoi(self, diachi, chedo):
        offset, kichthuoc, _ = self._o(chedo)
        return read_bytes(self.moitruong.tientrinh, diachi + offset, kichthuoc)

    def _ghioi(self, diachi, chedo, dulieu):
        # Ghi chữ rồi xoá độ rộng đã nhớ để game đo lại (canh giữa đúng)
        offset, _, dorong = self._o(chedo)
        write_bytes(self.moitruong.tientrinh, diachi + offset, dulieu, len(dulieu))
        write_bytes(self.moitruong.tientrinh, diachi + dorong, struct.pack("<i", 0), 4)

    def _datdongthem(self, diachi, dongs):
        if self._is_hookloi or (diachi, dongs) == self._dongthem:
            return not self._is_hookloi
        try:
            is_ok = self.moitruong.action_ghidongvedanhhieu(diachi, dongs, self.okhoi)
        except Exception as err:
            print(f"[DANH HIỆU MỤC TIÊU] Lỗi hook vẽ dòng: {err}")
            is_ok = False
        if not is_ok:
            self._is_hookloi = True
            return False
        self._dongthem = (diachi, dongs)
        return True

    def khoiphuc(self):
        # Thôi vẽ dòng thêm; trả ô gốc cho đối tượng đang ghi (nếu đối tượng còn đó và ô còn đúng chữ mình ghi)
        if self._dongthem and self._dongthem[0]:
            self._datdongthem(0, [])
        if not self._dangghi:
            return
        diachi, iddoituong, chedo = self._dangghi
        self._dangghi = None
        try:
            if self._daghi and self.moitruong.get_iddoituong(diachi) == iddoituong \
                    and self._docoi(diachi, chedo).split(b"\0")[0] == self._daghi:
                self._ghioi(diachi, chedo, self._goc)
        except Exception:
            pass

    def ghi(self, diachi, chedo, dongs):
        # dongs: các dòng từ trên xuống (taodongs / taodongsde)
        iddoituong = self.moitruong.get_iddoituong(diachi)
        _, kichthuoc, _ = self._o(chedo)
        if self._dangghi != (diachi, iddoituong, chedo):
            self.khoiphuc()
            self._dangghi = (diachi, iddoituong, chedo)
            self._goc, self._daghi = self._docoi(diachi, chedo), b""
        hientai = self._docoi(diachi, chedo)
        chu = hientai.split(b"\0")[0]
        if self._daghi and chu != self._daghi:
            # Game vừa ghi lại ô (máy chủ gửi lại trạng thái...): nhận làm gốc mới
            self._goc = hientai
        if chedo == CHEDOHIENMUCTIEU_TEN:
            # Tên gốc còn sót phần nối cũ (bot tắt đột ngột) thì cắt đi
            tengoc = self._goc.split(b"\0")[0]
            dau = tengoc.split(DAUNOITENMUCTIEU_BYTES)[0]
            if dau != tengoc:
                self._goc = (dau + b"\0" * kichthuoc)[:kichthuoc]
            dau += DAUNOITENMUCTIEU_BYTES
            noidung = dau + gopmotdong(dongs, kichthuoc - 1 - len(dau))
            self._datdongthem(0, [])
        elif self._datdongthem(diachi, list(reversed(dongs[:-1]))):
            # Dòng cuối vào danh hiệu, các dòng trên do hook vẽ (dòng 0 sát danh hiệu)
            noidung = catutf8(dongs[-1], kichthuoc - 1)
        else:
            noidung = gopmotdong(dongs, kichthuoc - 1)
        if chu == noidung:
            return
        self._ghioi(diachi, chedo, noidung + b"\0")
        self._daghi = noidung


class ODauNhanVat(ODoiTuong):
    # 1 dòng chữ trên đầu nhân vật mình (hành động hiện tại): có danh hiệu thật thì hook vẽ lên trên (không đụng ô), ô danh hiệu rỗng thì
    # mượn ô (xem đầu file). _dangghi / _daghi chỉ dùng khi đang mượn ô (_daghi = chữ mình ghi, rỗng = không mượn)
    def khoiphuc(self):
        if self._dongthem and self._dongthem[0]:
            self._datdongthem(0, [])
        if not self._dangghi:
            return
        diachi, iddoituong, chedo = self._dangghi
        self._dangghi = None
        try:
            if self._daghi and self.moitruong.get_iddoituong(diachi) == iddoituong \
                    and self._docoi(diachi, chedo).split(b"\0")[0] == self._daghi:
                # Ô gốc rỗng (mình chỉ mượn ô rỗng)
                self._ghioi(diachi, chedo, b"\0")
        except Exception:
            pass
        self._daghi = b""

    def ghi(self, diachi, chu):
        # chu: bytes UTF-8 có mã màu, 1 dòng
        chedo = CHEDOHIENMUCTIEU_DANHHIEU
        chu = catutf8(chu, KICHTHUOCDONGVEDANHHIEU - 1)
        iddoituong = self.moitruong.get_iddoituong(diachi)
        if self._dangghi != (diachi, iddoituong, chedo):
            self.khoiphuc()
            self._dangghi = (diachi, iddoituong, chedo)
        hientai = self._docoi(diachi, chedo).split(b"\0")[0]
        if hientai and hientai != self._daghi:
            # Danh hiệu thật (có sẵn / máy chủ vừa ghi sau "title show"): vẽ dòng trên nó, thôi mượn ô. Hook lỗi thì thôi, không đè
            self._daghi = b""
            self._datdongthem(diachi, [chu])
            return
        # Ô rỗng ("title hide" / chưa có danh hiệu) hoặc chữ mình: chữ vừa ô thì ghi thẳng, dài thì ô giữ " " cho game gọi vẽ, hook vẽ chữ
        if len(chu) <= KICHTHUOCDANHHIEU - 1:
            noidung = chu
            self._datdongthem(0, [])
        elif self._datdongthem(diachi, [chu]):
            noidung = b" "
        else:
            noidung = catutf8(chu, KICHTHUOCDANHHIEU - 1)
        if hientai != noidung:
            self._ghioi(diachi, chedo, noidung + b"\0")
        self._daghi = noidung


class DanhHieuMucTieu:
    def __init__(self, moitruong, tactu, shared_data, idcuaso):
        self.moitruong = moitruong
        self.tactu = tactu
        self.shared_data = shared_data
        self.idcuaso = idcuaso
        self._muctieu = ODoiTuong(moitruong, OKHOIMUCTIEU)
        self._nhanvat = ODauNhanVat(moitruong, OKHOINHANVAT)
        self._lucgop = 0.
        self._gop = {}
        self._lucdockho = 0.
        self._kho = {}
        self._khoquai = {}
        # Mục tiêu đang chọn cho giao diện: {id, khoaquai, ketluan (chữ không mã màu), muc}
        self._share = {}

    def khoiphuc(self):
        self._muctieu.khoiphuc()
        self._nhanvat.khoiphuc()

    def get_share(self):
        return dict(self._share)

    def _laygop(self, iddoituong, idnguoichoi, khoaquai):
        # Số đo gộp mọi cửa sổ cùng máy + số đã lưu -> {khihuyet, khangs {hệ: Kháng}, congs {hệ: Công nó}, nhip (đòn / giây nó đánh),
        # dpsminh (tổng DPS các cửa sổ đang đánh nó, None nếu không ai đang đánh), hesodps (của cửa sổ này), daluu (dùng số quái đã lưu)}
        luc = time.time()
        if luc - self._lucgop < CHUKYGOP and self._gop.get("id") == iddoituong:
            return self._gop
        self._lucgop = luc
        try:
            infos = {k: i for k, i in dict(self.shared_data.items()).items() if isinstance(i, dict)}
        except Exception:
            infos = {}
        if luc - self._lucdockho >= CHUKYDOCKHO:
            self._lucdockho = luc
            self._kho = taithongtinnguoichoi()
            self._khoquai = taithongtinquai()
        tomtats = [i["_uocluongmuctieu"][iddoituong] for i in infos.values() if iddoituong in (i.get("_uocluongmuctieu") or {})]
        gop = gopuocluong(tomtats)
        khihuyet = gop["khihuyet"]
        khangs = {he: v[0] for he, v in gop["khang"].items()}
        # DPS các cửa sổ đang đánh nó
        dpss = [tt["dps"] for tt in tomtats if tt.get("dps") and luc - tt.get("lucdanh", 0) <= THOIGIANDANGDANH]
        # Nó đánh mình: Công (cụm đông nhất mỗi hệ) + nhịp (nhiều khoảng nhất) từ mọi cửa sổ bị nó đánh
        bidanhs = [i["_bidanh"][iddoituong] for i in infos.values() if iddoituong in (i.get("_bidanh") or {})]
        congs = {}
        for he in (HE_NGOAI, HE_NOI):
            tot = max((b["cong"][he] for b in bidanhs if he in (b.get("cong") or {})), key = lambda v: v[1], default = None)
            if tot:
                congs[he] = tot[0]
        nhip = max(((b["nhip"], b["sokhoang"]) for b in bidanhs if b.get("nhip")), key = lambda v: v[1], default = (None, 0))[0]
        if idnguoichoi:
            # Người chơi: Công lọc theo hệ môn phái (gộp như giao diện), thiếu thì số đã lưu theo ID
            congdoithus = [i["_congdoithu"][idnguoichoi] for i in infos.values() if idnguoichoi in (i.get("_congdoithu") or {})]
            congnguoichoi = {he: v[0] for he, v in gopcongdoithu(congdoithus)[0].items()}
            congs = congnguoichoi or congs
            muc = self._kho.get(str(idnguoichoi)) or {}
            if not khihuyet and muc.get("khihuyet"):
                khihuyet = muc["khihuyet"]["giatri"]
            for he, khoa in ((HE_NGOAI, "ngoaikhang"), (HE_NOI, "noikhang")):
                if he not in khangs and muc.get(khoa):
                    khangs[he] = muc[khoa]["giatri"]
            for he, khoa in ((HE_NGOAI, "ngoaicong"), (HE_NOI, "noicong")):
                if he not in congs and muc.get(khoa):
                    congs[he] = muc[khoa]["giatri"]
        daluu = False
        quai = self._khoquai.get(khoaquai) if khoaquai else None
        if quai:
            # Quái đã lưu (số chắc): dùng luôn thay số đang đo
            daluu = True
            if quai.get("khihuyet"):
                khihuyet = quai["khihuyet"]["giatri"]
            for he, khoa in ((HE_NGOAI, "ngoaikhang"), (HE_NOI, "noikhang")):
                if quai.get(khoa):
                    khangs[he] = quai[khoa]["giatri"]
            for he, khoa in ((HE_NGOAI, "ngoaicong"), (HE_NOI, "noicong")):
                if quai.get(khoa):
                    congs[he] = quai[khoa]["giatri"]
            if quai.get("nhip"):
                nhip = quai["nhip"]["giatri"]
        hesodps = (infos.get(self.idcuaso) or {}).get("_hesodps")
        self._gop = {"id": iddoituong, "khihuyet": khihuyet, "khangs": khangs, "congs": congs, "nhip": nhip,
                     "dpsminh": sum(dpss) if dpss else None, "hesodps": hesodps, "daluu": daluu}
        return self._gop

    def _ketluan(self, gop, mau):
        # -> (mức hoặc None, thời gian mình hạ nó, thời gian nó hạ mình, lý do chưa rõ)
        mt = self.moitruong
        congminh = mt.get_chisonhanvats(DICHCONG)
        khangminh = mt.get_chisonhanvats(DICHKHANG)
        mauminh = mt.get_sinhlucconlai()
        heminh = chonhe(mt.get_tenmonphai(), {"ngoaicong": congminh[0], "noicong": congminh[1]}) if congminh else None
        dpsminh = gop["dpsminh"]
        if not dpsminh and heminh and gop["khangs"].get(heminh):
            c = congminh[0] if heminh == HE_NGOAI else congminh[1]
            dpsminh = (gop["hesodps"] or HESODPSMACDINH) * satthuong(c, gop["khangs"][heminh], heminh)
        dpsno = None
        if gop["congs"] and khangminh:
            stno = max(satthuong(cong, khangminh[0] if he == HE_NGOAI else khangminh[1], he) for he, cong in gop["congs"].items())
            dpsno = stno * (gop["nhip"] or NHIPMACDINH)
        return tinhketluan(gop["khihuyet"] * mau / 100. if gop["khihuyet"] else None, dpsminh, mauminh or None, dpsno)

    def _buocmuctieu(self, chedo, chumau):
        mt = self.moitruong
        diachi = mt._get_diachicosothongtinnhanvatmuctieudangchon()
        if not diachi or not mt.get_is_nhanvattontai(diachi) or mt.get_is_npc(diachi):
            self._share = {}
            self._muctieu.khoiphuc()
            return
        iddoituong = mt.get_iddoituong(diachi)
        idnguoichoi = mt.get_idnguoichoi(diachi) if mt.get_is_nguoichoi(diachi) else 0
        khoaquai = self._share.get("khoaquai", "") if self._share.get("id") == iddoituong else \
            (khoaquaitheoten(mt._get_tenthucte(diachi)) if mt.get_is_quai(diachi) else "")
        gop = self._laygop(iddoituong, idnguoichoi, khoaquai)
        mau = mt.get_phantramsinhlucconlai(diachi)
        ketluan = self._ketluan(gop, mau)
        dongketluan = taodongketluan(*ketluan)
        self._share = {"id": iddoituong, "khoaquai": khoaquai, "muc": ketluan[0], "daluu": gop["daluu"],
                       "ketluan": dongketluan[2:].decode("utf-8", "ignore")}
        if not chedo:
            self._muctieu.khoiphuc()
            return
        self._muctieu.ghi(diachi, chedo, [dongketluan] + taodongs(mau, gop["khihuyet"], gop["khangs"], gop["congs"], chumau))

    def _buocnhanvat(self, hanhdong, chedomuctieu):
        # Hành động hiện tại lên đầu nhân vật mình; rỗng (tắt ô / chưa có hành động) thì trả ô. Đang tự chọn mình làm mục tiêu và đang
        # ghi thông tin mục tiêu thì nhường ô cho phần mục tiêu
        mt = self.moitruong
        diachi = mt.get_diachicosothongtinnhanvat1()
        if not hanhdong or not diachi or (chedomuctieu == CHEDOHIENMUCTIEU_DANHHIEU and diachi == self._muctieu.get_diachi()):
            self._nhanvat.khoiphuc()
            return
        self._nhanvat.ghi(diachi, tomauhanhdong(hanhdong))

    def step(self, chedo, chumau = MAUHIENMUCTIEU_THEOMAU, hanhdong = ""):
        chedo = chedo if chedo in (CHEDOHIENMUCTIEU_DANHHIEU, CHEDOHIENMUCTIEU_TEN) else None
        self._buocmuctieu(chedo, chumau)
        self._buocnhanvat(hanhdong, chedo)
