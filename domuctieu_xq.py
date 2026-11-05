"""Dự đoán Khí Huyết tối đa, Ngoại Kháng, Nội Kháng của mục tiêu đang chọn (người chơi hoặc quái) từ sát thương mình gây ra.
Chạy tay hoặc từ tab Khác của giao diện; cần quyền Admin như bot.

    python -X utf8 domuctieu_xq.py [--hwnd <cửa sổ> | --ten <nhân vật>] [--giay 60]

Mục tiêu lấy theo nhân vật được chọn (--hwnd / --ten, bỏ trống: nhân vật đầu tiên đang có mục tiêu). Mọi nhân vật của mình đang mở
cùng đánh mục tiêu đó đều được ghi (mỗi client chỉ thấy số bay của chính mình, xem MoiTruong._docsobaydoituong), nên muốn ra cả
2 loại Kháng thì cho 1 nhân vật hệ Ngoại và 1 nhân vật hệ Nội cùng đánh.
- Kháng: lật ngược công thức (congthucsatthuong_xq.khangtusatthuong) với Công trên bảng của người đánh. Kiểm bằng 882 đòn đo
  2026-11-05: lấy trung vị các đòn thường thì lệch Kháng thật 0.3% (lớn nhất 1.2%), từng đòn lệch ±2.5%. Bỏ đòn bạo / bỏ qua Kháng
  (lớn hơn 1.3 lần trung vị) và đòn bị đỡ (dưới 0.85 lần). Chiêu "+X Công" làm Kháng ra THẤP hơn thật: đo chính xác nhất khi chỉ
  đánh thường (Ngoại) hoặc Ngự Kiếm (Nội), hoặc truyền --congthem X cho cả lượt đo.
- Khí Huyết tối đa: tổng sát thương mình gây / phần % máu mục tiêu tụt (client chỉ có % máu mục tiêu, bước 2%: cần máu tụt ≥ 6%). Người khác cùng
  đánh làm máu tụt nhanh hơn => ra thấp hơn thật; mục tiêu hồi máu => ra cao hơn.
Mục tiêu là nhân vật của mình đang mở thì in thêm chỉ số thật để so.
"""
import argparse
import sys
import time

import numpy as np

from congthucsatthuong_xq import HE_NGOAI, HE_NOI, chonhe, khangtusatthuong
from dosatthuong_xq import timnhanvats
from sosanhbuild_xq import TENHE_MAP, docchiso

CHUKYDOC = 0.02
# Đòn thường nằm trong [THAP, CAO] lần trung vị sát thương của người đánh đó (bạo x2, bỏ qua Kháng = Công, pháp bảo đỡ thì nhỏ hẳn)
NGUONGTHAP, NGUONGCAO = 0.85, 1.3
INMOI = 10.
# Máu mục tiêu phải tụt ít nhất chừng này % mới ước Khí Huyết tối đa (bước % máu 2 => sai số mỗi đầu ±1%)
MAUTUTTOITHIEU = 6.


def timdiachi(mt, iddoituong):
    # Địa chỉ đối tượng iddoituong trong client mt (id đối tượng do máy chủ cấp, giống nhau ở mọi client), None nếu không thấy
    for diachi in mt._get_diachidoituongxungquanhs():
        if mt.get_iddoituong(diachi) == iddoituong:
            return diachi
    return None


def phantrammau(mt, diachi):
    # % máu còn lại của đối tượng: client chỉ có ô NV_PHANTRAMMAU = % / 2 (đầy = 50) nên bước 2%
    return float(mt.get_phantramsinhlucconlai(diachi))


def tomtat(dons, mt_nguoidanh, thamso):
    # dons: [(sát thương, chỉ số người đánh lúc đó)] của 1 người đánh -> (hệ, Kháng dự đoán, số đòn dùng, khoảng từng đòn) hoặc None
    if not dons:
        return None
    sts = np.array([d[0] for d in dons], float)
    trungvi = np.median(sts)
    he = thamso.he or chonhe(mt_nguoidanh.get_tenmonphai(), dons[-1][1])
    khangs = []
    for st, chiso in dons:
        if NGUONGTHAP * trungvi <= st <= NGUONGCAO * trungvi:
            k = khangtusatthuong(st, chiso["ngoaicong"] if he == HE_NGOAI else chiso["noicong"], he, thamso.congthem, thamso.boqua)
            if k is not None:
                khangs.append(k)
    if not khangs:
        return he, None, 0, None
    return he, float(np.median(khangs)), len(khangs), (float(np.percentile(khangs, 10)), float(np.percentile(khangs, 90)))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding = "utf-8", line_buffering = True)
    thamso = argparse.ArgumentParser(description = "Dự đoán Khí Huyết tối đa / Kháng của mục tiêu đang chọn")
    thamso.add_argument("--hwnd", type = int, help = "cửa sổ game của nhân vật lấy mục tiêu")
    thamso.add_argument("--ten", help = "tên nhân vật lấy mục tiêu")
    thamso.add_argument("--giay", type = float, default = 60., help = "thời gian đo (giây), mặc định 60")
    thamso.add_argument("--he", choices = (HE_NGOAI, HE_NOI), help = "ép hệ sát thương của mọi người đánh")
    thamso.add_argument("--congthem", type = int, default = 0, help = "chiêu đang dùng cộng thêm bao nhiêu Công (mặc định 0)")
    thamso.add_argument("--boqua", type = float, default = 0., help = "chiêu bỏ qua bao nhiêu phần phòng thủ (Nhất Quyền 0.7)")
    thamso = thamso.parse_args()

    nhanvats = timnhanvats()
    if not nhanvats:
        print("Không thấy cửa sổ game nào có nhân vật (chạy bằng quyền Admin?)")
        return
    chinh = None
    for ten, mt in nhanvats.items():
        if (thamso.hwnd and mt.idcuaso == thamso.hwnd) or (thamso.ten and thamso.ten.lower() in ten.lower()):
            chinh = ten
    if not chinh and not thamso.hwnd and not thamso.ten:
        chinh = next((ten for ten, mt in nhanvats.items() if mt._get_diachicosothongtinnhanvatmuctieudangchon()), None)
    if not chinh:
        print("Không thấy nhân vật được chọn / chưa nhân vật nào có mục tiêu")
        return
    mtchinh = nhanvats[chinh]
    diachimuctieu = mtchinh._get_diachicosothongtinnhanvatmuctieudangchon()
    if not diachimuctieu or not mtchinh.get_is_nhanvattontai(diachimuctieu):
        print(f"{chinh} chưa chọn mục tiêu (bấm chọn mục tiêu trong game rồi chạy lại)")
        return
    idmuctieu = mtchinh.get_iddoituong(diachimuctieu)
    tenmuctieu = mtchinh.get_tendoituong(diachimuctieu)
    print(f"Mục tiêu: {tenmuctieu} (theo {chinh}), đo {thamso.giay:.0f}s. Cho các nhân vật đánh mục tiêu này")

    # Mỗi nhân vật của mình (trừ chính mục tiêu): địa chỉ mục tiêu trong client đó + số bay lần đọc trước
    nguoidanhs = {}
    for ten, mt in nhanvats.items():
        diachi = diachimuctieu if ten == chinh else timdiachi(mt, idmuctieu)
        if diachi and mt.get_iddoituong() != idmuctieu:
            nguoidanhs[ten] = {"mt": mt, "diachi": diachi, "sobay": mt.get_sobaydoituong(diachi), "dons": []}
    muctieula = next((mt for ten, mt in nhanvats.items() if mt.get_iddoituong() == idmuctieu), None)

    tongst, diemmaus = 0, []     # [(tổng sát thương mình gây tới lúc đó, % máu)]
    mauthap = phantrammau(mtchinh, diachimuctieu)
    diemmaus.append((0, mauthap))
    batdau = lucin = time.time()
    while time.time() - batdau < thamso.giay:
        time.sleep(CHUKYDOC)
        if mtchinh.get_iddoituong(diachimuctieu) != idmuctieu:
            print("Mục tiêu đã biến mất (chết / ra khỏi tầm nhìn), dừng đo")
            break
        for ten, nd in nguoidanhs.items():
            mt = nd["mt"]
            moi = mt.get_sobaydoituong(nd["diachi"])
            cu = nd["sobay"]
            if moi and cu:
                chiso = docchiso(mt)
                for i in range(10):
                    if moi[0][i] > 0 and (moi[0][i] != cu[0][i] or moi[1][i] < cu[1][i]):
                        nd["dons"].append((moi[0][i], chiso))
                        tongst += moi[0][i]
            nd["sobay"] = moi or cu
        mau = phantrammau(mtchinh, diachimuctieu)
        if mau != diemmaus[-1][1]:
            diemmaus.append((tongst, mau))
        if time.time() - lucin >= INMOI:
            lucin = time.time()
            print(f"  {time.time() - batdau:.0f}s: " + ", ".join(f"{ten} {len(nd['dons'])} đòn" for ten, nd in nguoidanhs.items())
                  + f", máu mục tiêu {mau:.1f}%")

    print(f"\n== Kết quả: {tenmuctieu}")
    khangdudoan = {}
    for ten, nd in nguoidanhs.items():
        kq = tomtat(nd["dons"], nd["mt"], thamso)
        if not kq:
            continue
        he, khang, sodon, khoang = kq
        if khang is None:
            print(f"   {ten}: {len(nd['dons'])} đòn nhưng không suy ra được Kháng (đòn quá lớn so với Công: chiêu cộng Công / bạo)")
            continue
        khangdudoan.setdefault(he, []).append((khang, sodon))
        print(f"   {TENHE_MAP[he]} Kháng ≈ {khang:.0f} (theo {ten}, {sodon}/{len(nd['dons'])} đòn thường; từng đòn {khoang[0]:.0f}-{khoang[1]:.0f})")
    for he in (HE_NGOAI, HE_NOI):
        if he not in khangdudoan:
            print(f"   {TENHE_MAP[he]} Kháng: chưa có nhân vật hệ {TENHE_MAP[he]} đánh")

    # Khí Huyết tối đa: hồi quy % máu theo tổng sát thương -> độ dốc (% / sát thương)
    if len(diemmaus) >= 3 and diemmaus[0][1] - diemmaus[-1][1] >= MAUTUTTOITHIEU:
        x = np.array([d[0] for d in diemmaus], float)
        y = np.array([d[1] for d in diemmaus], float)
        doc = np.polyfit(x, y, 1)[0]
        if doc < 0:
            print(f"   Khí Huyết tối đa ≈ {-100. / doc:.0f} (máu tụt {diemmaus[0][1]:.1f}% -> {diemmaus[-1][1]:.1f}% sau {tongst} sát thương;"
                  f" người khác cùng đánh thì số này thấp hơn thật)")
    else:
        print(f"   Khí Huyết tối đa: chưa đủ (máu mới tụt {diemmaus[0][1] - diemmaus[-1][1]:.1f}%, cần ≥ {MAUTUTTOITHIEU:.0f}%)")

    if muctieula:
        thuc = docchiso(muctieula)
        print(f"   [Mục tiêu là nhân vật của mình - chỉ số thật: Khí Huyết {thuc['khihuyet']}, Ngoại Kháng {thuc['ngoaikhang']},"
              f" Nội Kháng {thuc['noikhang']}]")


if __name__ == "__main__":
    main()
