"""Công thức sát thương đo thực tế (2026-11-05, Tỉ Võ Trường, 882 đòn trong _internal/dosatthuong_claude.jsonl) và các phép tính
so build dựa trên nó (sosanhbuild_xq.py dùng).

C = Công trên bảng nhân vật của người đánh (ô thấp của cặp, KDK+0x153C Ngoại / +0x1548 Nội), K = Kháng cùng hệ của mục tiêu (ô thấp),
r = K / C. Sát thương chỉ phụ thuộc C và r (cùng K/C thì cùng sát thương / C), K = 0 thì sát thương ≈ C:
- Ngoại (đánh thường + chiêu Đào Hoa): ST = 0.926 * C / (1 + 3.25 r)^1.18 - sai số trung bình 0.20%, lớn nhất 1.2% trên 22 nhóm
  (C 1140-3381, K 811-2279).
- Nội (chiêu gốc Ngự Kiếm Thục Sơn): ST = 0.741 * C / (1 + 1.15 r)^2.18 - sai số trung bình 0.55% trên 28 nhóm (C 1198-2713,
  K 1181-2345). Kháng hại phe Nội nặng hơn phe Ngoại.
- Chiêu "tăng thêm X điểm Ngoại / Nội Công": cộng X vào C rồi tính (Hắc Hổ +100, Đại Hải +120, Tiên Nhân Chỉ Lộ +210 khớp ±1%).
  Chiêu "bỏ qua X% phòng thủ" (Nhất Quyền 70%): K * (1 - X) (khớp +0.7%).
- Bạo kích x2.00 (dao động 1.97-2.05). Tỉ lệ ra bạo: mẫu lớn nhất (Thọ, bảng 8.01%) đo 7.2 ± 1.8%; gộp mọi đợt ra ~74% số trên
  bảng - chưa chắc, nên để HESOTILEBAOKICH = 1 (đổi ở đây nếu đo thêm thấy thấp hơn).
- Mỗi đòn random ±1.5% quanh giá trị trên.
"""

HE_NGOAI = "ngoai"
HE_NOI = "noi"

# (s, b, p) của ST = s * C / (1 + b * K / C)^p
HESOCONGTHUC_MAP = {
    HE_NGOAI: (0.926, 3.25, 1.18),
    HE_NOI: (0.741, 1.15, 2.18),
}
HESOBAOKICH = 2.
# Tỉ lệ ra bạo thật = Bạo Kích trên bảng * hệ số này (đo 2026-11-05 ra 0.74-0.9, chưa đủ mẫu để khẳng định khác 1)
HESOTILEBAOKICH = 1.

# Kháng mục tiêu mặc định để so build (cấp 100 đo được: người chơi 1150-2550, đủ đồ thường 1800-2300)
KHANGMUCTIEUMACDINHs = (1200, 1800, 2400)
# Người đánh tham chiếu để tính độ trâu (sát thương phải nhận): Công mỗi hệ
CONGNGUOIDANHTHAMCHIEU_MAP = {HE_NGOAI: 3000, HE_NOI: 2500}

# Môn phái -> hệ đánh chính (không có: lấy hệ có Công cao hơn trên bảng). Đã thấy 2026-11-05: Đào Hoa Ngoại; Mao Sơn, Vân Mộng
# Nội Công gấp 3-4 lần Ngoại Công. Thục Sơn có cả đao (Ngoại) lẫn kiếm (Nội); Đường Môn là phái Ngoại đánh xa (người dùng nói
# 2026-11-05); Cẩm Vệ Quân, Côn Luân chưa đo
HEMONPHAI_MAP = {
    "daohoanguyen": HE_NGOAI,
    "duongmon": HE_NGOAI,
    "maoson": HE_NOI,
    "vanmongcoc": HE_NOI,
}


def satthuong(cong, khang, he, congthem = 0, boquaphongthu = 0.):
    # Sát thương 1 đòn thường (không bạo). congthem: "+X Công" của chiêu; boquaphongthu: 0.7 = bỏ qua 70% phòng thủ
    s, b, p = HESOCONGTHUC_MAP[he]
    c = max(cong + congthem, 1)
    k = max(khang, 0) * (1. - boquaphongthu)
    return s * c / (1. + b * k / c) ** p


def khangtusatthuong(satthuongdo, cong, he, congthem = 0, boquaphongthu = 0.):
    # Lật ngược satthuong(): Kháng mục tiêu suy ra từ 1 đòn không bạo. None khi đòn lớn hơn mức Kháng 0 (đòn bạo / chiêu có cộng /
    # đòn bỏ qua Kháng - không suy ra được)
    s, b, p = HESOCONGTHUC_MAP[he]
    c = max(cong + congthem, 1)
    if satthuongdo <= 0 or satthuongdo >= s * c:
        return None
    k = ((s * c / satthuongdo) ** (1. / p) - 1.) / b * c
    return k / (1. - boquaphongthu) if boquaphongthu < 1 else None


def congtusatthuong(satthuongdo, khang, he, congtoida = 30000):
    # Lật ngược satthuong() theo Công: Công người đánh suy ra từ 1 đòn không bạo lên mục tiêu có Kháng khang (đo Công đối thủ từ
    # máu mình tụt). satthuong() tăng dần theo Công nên chia đôi. None khi không nằm trong [1, congtoida]
    if satthuongdo <= 0 or satthuong(congtoida, khang, he) < satthuongdo:
        return None
    thap, cao = 1., float(congtoida)
    for _ in range(60):
        giua = (thap + cao) / 2.
        if satthuong(giua, khang, he) < satthuongdo:
            thap = giua
        else:
            cao = giua
    return (thap + cao) / 2.


def satthuongkyvong(cong, khang, he, baokich, congthem = 0, boquaphongthu = 0.):
    # Sát thương trung bình 1 đòn tính cả bạo kích; baokich là % trên bảng (9.01 = 9.01%)
    tile = min(max(baokich, 0.) * HESOTILEBAOKICH / 100., 1.)
    return satthuong(cong, khang, he, congthem, boquaphongthu) * (1. + (HESOBAOKICH - 1.) * tile)


def diemtancong(chiso, he, khangs = KHANGMUCTIEUMACDINHs):
    # Sát thương kỳ vọng trung bình lên các mức Kháng mục tiêu. chiso: dict như sosanhbuild (ngoaicong, noicong, baokich %...)
    cong = chiso["ngoaicong"] if he == HE_NGOAI else chiso["noicong"]
    return sum(satthuongkyvong(cong, k, he, chiso["baokich"]) for k in khangs) / len(khangs)


def sodonchiu(chiso, he):
    # Độ trâu trước hệ he: số đòn thường (kỳ vọng, bạo 9%) của người đánh tham chiếu cần để hết máu
    khang = chiso["ngoaikhang"] if he == HE_NGOAI else chiso["noikhang"]
    return chiso["khihuyet"] / max(satthuongkyvong(CONGNGUOIDANHTHAMCHIEU_MAP[he], khang, he, 9.), 1.)


def giatribien(cong, khang, he, baokich):
    # Giá trị biên quanh 1 điểm build: {tên: (thêm bao nhiêu sát thương kỳ vọng, quy ra bao nhiêu điểm Công)}
    goc = satthuongkyvong(cong, khang, he, baokich)
    motcong = satthuongkyvong(cong + 1, khang, he, baokich) - goc
    ketqua = {
        "+100 Công": satthuongkyvong(cong + 100, khang, he, baokich) - goc,
        "+1% Bạo Kích": satthuongkyvong(cong, khang, he, baokich + 1) - goc,
        "+100 Kháng mục tiêu": satthuongkyvong(cong, khang + 100, he, baokich) - goc,
    }
    return goc, {ten: (st, st / motcong if motcong else 0.) for ten, st in ketqua.items()}


def chonhe(monphai, chiso):
    # Hệ đánh chính của nhân vật: theo môn phái, không rõ thì hệ có Công cao hơn
    he = HEMONPHAI_MAP.get(monphai)
    if he:
        return he
    return HE_NGOAI if chiso["ngoaicong"] >= chiso["noicong"] else HE_NOI
