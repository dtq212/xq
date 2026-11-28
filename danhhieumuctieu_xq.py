"""Vẽ chữ lên đầu đối tượng ngay trong game, sửa bộ nhớ client của mình (máy chủ / người khác không thấy).
- Từ 2026-11-27 (người dùng yêu cầu): bật ở đầu tab Chiến đấu thì MỌI người chơi xung quanh (trừ mình) có 1 dòng "<tên bang> |
  <môn phái>" (DanhHieuMucTieu._buocnguoichois, mỗi người 1 khối hook từ OKHOINGUOICHOIDAU, cách ghi như ODauNhanVat: có danh hiệu thật
  thì vẽ lên trên, ô rỗng thì mượn ô). Bang / phái lấy từ "desc user" (MoiTruong.get_thongtinnguoichoi, nạp sẵn thongtinnguoichoi.json),
  người chưa biết trong tầm hỏi thì tự hỏi dần. Bỏ hẳn phần vẽ Kết luận / Khí huyết / Công / Kháng lên mục tiêu và chế độ đuôi tên
  (người dùng thấy không hữu ích); Kết luận / ước lượng mục tiêu (uocluongmuctieu_xq) gỡ hẳn 2026-11-27 cho nhẹ bot. Phần dưới là
  ghi chú cách làm cũ, giữ để tham khảo.
Cũ: 2 chế độ (giao diện chọn theo từng cửa sổ ở đầu tab Chiến đấu, hangso_xq.CHEDOHIENMUCTIEU_*):
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

from diachi_xq import DC
from hangso_xq import CHEDOHIENMUCTIEU_DANHHIEU, CHEDOHIENMUCTIEU_TEN, MAUHIENMUCTIEU_THEOMAU, KHOANGCACHHOIBANGPHAI
from hangso_xq import OKHOINHANVAT, MAUHANHDONGTRENDAU, KICHTHUOCDONGVEDANHHIEU, CHUTATFOXIATRENDAU, MAUTATFOXIATRENDAU
from hangso_xq import OKHOINGUOICHOIDAU, SOKHOINGUOICHOI, MAUBANGTRENDAU, MAUPHAITRENDAU, MAUPHUTRENDAU, TENVOMONPHAI
from tienich_xq import read_bytes, write_bytes, DAUNOITENMUCTIEU_BYTES

CHUKYGHI = 0.3
# Người chơi xung quanh (bang + phái): ghi lại mỗi chừng này giây (game ghi lại ô danh hiệu khi họ vào tầm nhìn); hỏi "desc user" người
# chưa biết mỗi CHUKYHOINGUOICHOI giây 1 người, cùng 1 ID cách nhau GIANCACHHOILAINGUOICHOI giây (người không trả lời khỏi hỏi dồn)
CHUKYNGUOICHOI = 0.6
CHUKYHOINGUOICHOI = 3.
GIANCACHHOILAINGUOICHOI = 120.
# Ô tên +0x10AC tới ô độ rộng tên +0x112C = 0x80 byte; ô danh hiệu 0x3B byte, độ rộng danh hiệu ở +0x1130. Chừa 1 byte NUL
KICHTHUOCTEN = 0x112C - 0x10AC
KICHTHUOCDANHHIEU = 0x3B
DORONGTEN = 0x112C
DORONGDANHHIEU = 0x1130
# Màu dòng không phải Khí huyết khi chọn "Theo % máu"
MAUPHANSAU = "W"


def dinhdangso(n):
    # 60234 -> "60.234" (dấu . ngăn phần nghìn kiểu Việt)
    return f"{int(round(n)):,}".replace(",", ".")


def dinhdangkhoang(khoang):
    # (3332, 3367) -> "3.332-3.367", 2 đầu bằng nhau thì 1 số
    return dinhdangso(khoang[0]) if khoang[0] == khoang[1] else f"{dinhdangso(khoang[0])}-{dinhdangso(khoang[1])}"


def mamau(chu):
    return b"\x1b" + chu.encode("ascii")


def taodongnguoichoi(monphai, bangphai, chumau = MAUHIENMUCTIEU_THEOMAU):
    # Dòng trên đầu người chơi: "<tên bang> | <môn phái>" (bytes UTF-8 có mã màu, không nhãn - người dùng yêu cầu 2026-11-27). bangphai
    # "" = không bang, None = chưa biết; monphai None = chưa biết. Màu "Mặc định": tên bang MAUBANGTRENDAU, phái MAUPHAITRENDAU, dấu ngăn /
    # chưa biết MAUPHUTRENDAU; màu khác cả dòng 1 màu
    # Không bang thì chỉ hiện môn phái; phái "-" (chưa vào phái, kể cả số cũ đã lưu) hiện "Vô Môn Phái" (người dùng yêu cầu 2026-11-28)
    if monphai is not None and not monphai.strip().strip("－-").strip():
        monphai = TENVOMONPHAI
    phai = monphai or "?"
    mauphai = MAUPHAITRENDAU if monphai else MAUPHUTRENDAU
    if bangphai == "":
        return mamau(chumau if chumau != MAUHIENMUCTIEU_THEOMAU else mauphai) + phai.encode("utf-8")
    bang = bangphai or "?"
    if chumau != MAUHIENMUCTIEU_THEOMAU:
        return mamau(chumau) + f"{bang} | {phai}".encode("utf-8")
    return (mamau(MAUBANGTRENDAU if bangphai else MAUPHUTRENDAU) + bang.encode("utf-8")
            + mamau(MAUPHUTRENDAU) + b" | " + mamau(mauphai) + phai.encode("utf-8"))


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


def taodongtheosau(is_bat, ten = ""):
    # Dòng trên cùng đầu nhân vật mình: "Theo sau: BẬT (tên)" (xanh lá, tên vàng) / "Theo sau: TẮT" (đỏ)
    dong = mamau(MAUHANHDONGTRENDAU["dau"]) + "Theo sau: ".encode("utf-8")
    if not is_bat:
        return dong + mamau("R") + "TẮT".encode("utf-8")
    dong += mamau("G") + "BẬT".encode("utf-8")
    if ten:
        dong += mamau(MAUHANHDONGTRENDAU["doituong"]) + f" ({ten})".encode("utf-8")
    return dong


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

    def ghi(self, diachi, dongs):
        # dongs: các dòng bytes UTF-8 có mã màu, từ trên xuống (dòng cuối sát danh hiệu / nằm trong ô danh hiệu)
        chedo = CHEDOHIENMUCTIEU_DANHHIEU
        dongs = [catutf8(d, KICHTHUOCDONGVEDANHHIEU - 1) for d in dongs if d]
        if not dongs:
            self.khoiphuc()
            return
        iddoituong = self.moitruong.get_iddoituong(diachi)
        if self._dangghi != (diachi, iddoituong, chedo):
            self.khoiphuc()
            self._dangghi = (diachi, iddoituong, chedo)
        hientai = self._docoi(diachi, chedo).split(b"\0")[0]
        if hientai and hientai != self._daghi:
            # Danh hiệu thật (có sẵn / máy chủ vừa ghi sau "title show"): vẽ các dòng trên nó, thôi mượn ô. Hook lỗi thì thôi, không đè
            self._daghi = b""
            self._datdongthem(diachi, list(reversed(dongs)))
            return
        # Ô rỗng ("title hide" / chưa có danh hiệu) hoặc chữ mình: dòng cuối vừa ô thì ghi thẳng (hook vẽ các dòng trên), dài thì ô giữ " "
        # cho game gọi vẽ, hook vẽ hết
        chu = dongs[-1]
        if len(chu) <= KICHTHUOCDANHHIEU - 1 and (len(dongs) == 1 or self._datdongthem(diachi, list(reversed(dongs[:-1])))):
            noidung = chu
            if len(dongs) == 1:
                self._datdongthem(0, [])
        elif self._datdongthem(diachi, list(reversed(dongs))):
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
        self._nhanvat = ODauNhanVat(moitruong, OKHOINHANVAT)
        # Người chơi xung quanh: địa chỉ -> ODauNhanVat đang dùng; các ô (khối hook) còn rảnh
        self._nguoichois = {}
        self._onguoichoirans = [ODauNhanVat(moitruong, OKHOINGUOICHOIDAU + i) for i in range(SOKHOINGUOICHOI)]
        self._lucnguoichoi = 0.
        self._luchoinguoichoi = 0.
        # ID người chơi -> lúc hỏi "desc user" gần nhất (người không trả lời thì khỏi hỏi lại liền)
        self._dahoi = {}

    def khoiphuc(self):
        self._khoiphucnguoichois()
        self._nhanvat.khoiphuc()

    def _khoiphucnguoichois(self, giu = ()):
        # Trả ô / thôi vẽ cho người chơi không còn trong giu
        for diachi in [d for d in self._nguoichois if d not in giu]:
            o = self._nguoichois.pop(diachi)
            try:
                o.khoiphuc()
            except Exception:
                pass
            self._onguoichoirans.append(o)

    def _buocnguoichois(self, chedo, chumau):
        # Mọi người chơi xung quanh (trừ mình): 1 dòng bang + môn phái (taodongnguoichoi). Nhiều hơn SOKHOINGUOICHOI thì lấy người gần nhất.
        # Người chưa biết bang / phái trong tầm KHOANGCACHHOIBANGPHAI: hỏi "desc user" người gần nhất, mỗi CHUKYHOINGUOICHOI giây 1 người,
        # mỗi ID cách nhau ít nhất GIANCACHHOILAINGUOICHOI giây (MoiTruong cũng tự giãn cách / chờ trả lời)
        if not chedo:
            self._khoiphucnguoichois()
            return
        luc = time.time()
        if luc - self._lucnguoichoi < CHUKYNGUOICHOI:
            return
        self._lucnguoichoi = luc
        mt = self.moitruong
        diachiminh = mt.get_diachicosothongtinnhanvat1()
        cans = []
        for diachi in mt._get_diachidoituongxungquanhs(is_nguoichoi = True):
            if diachi and diachi != diachiminh and mt.get_is_nhanvattontai(diachi):
                cans.append((mt.get_khoangcach(diachi), diachi))
        cans.sort()
        cans = cans[:SOKHOINGUOICHOI]
        self._khoiphucnguoichois({d for _, d in cans})
        canhoi = None
        for khoangcach, diachi in cans:
            idnguoichoi = mt.get_idnguoichoi(diachi)
            monphai, bangphai = mt.get_thongtinnguoichoi(idnguoichoi) if idnguoichoi and idnguoichoi > 0 else (None, None)
            if canhoi is None and (monphai is None or bangphai is None) and idnguoichoi and idnguoichoi > 0 \
                    and khoangcach <= KHOANGCACHHOIBANGPHAI and luc - self._dahoi.get(idnguoichoi, 0.) >= GIANCACHHOILAINGUOICHOI:
                canhoi = (idnguoichoi, diachi)
            o = self._nguoichois.get(diachi)
            if o is None:
                if not self._onguoichoirans:
                    continue
                o = self._onguoichoirans.pop()
                self._nguoichois[diachi] = o
            o.ghi(diachi, [taodongnguoichoi(monphai, bangphai, chumau)])
        if canhoi and luc - self._luchoinguoichoi >= CHUKYHOINGUOICHOI and mt.action_hoithongtinnguoichoimuctieu(canhoi[1]):
            self._luchoinguoichoi = luc
            self._dahoi[canhoi[0]] = luc

    def _buocnhanvat(self, hanhdong, is_tatbot = False, theosau = None):
        # Trên đầu nhân vật mình, từ trên xuống: dòng Theo sau (theosau = (is_bật, tên người được theo) / None = không hiện), rồi hành động
        # hiện tại. Không còn dòng nào thì trả ô. Đang tắt Foxia thì dòng dưới luôn là CHUTATFOXIATRENDAU (màu đỏ) thay hành động
        mt = self.moitruong
        diachi = mt.get_diachicosothongtinnhanvat1()
        dongs = []
        if theosau is not None:
            dongs.append(taodongtheosau(*theosau))
        if is_tatbot:
            dongs.append(mamau(MAUTATFOXIATRENDAU) + CHUTATFOXIATRENDAU.encode("utf-8"))
        elif hanhdong:
            dongs.append(tomauhanhdong(hanhdong))
        if not dongs or not diachi:
            self._nhanvat.khoiphuc()
            return
        self._nhanvat.ghi(diachi, dongs)

    def step(self, chedo, chumau = MAUHIENMUCTIEU_THEOMAU, hanhdong = "", is_tatbot = False, theosau = None):
        chedo = chedo if chedo in (CHEDOHIENMUCTIEU_DANHHIEU, CHEDOHIENMUCTIEU_TEN) else None
        self._buocnguoichois(chedo, chumau)
        self._buocnhanvat(hanhdong, is_tatbot, theosau)
