# Phân tích log đo Khai Thiên Tịch Địa (bot ghi ở _internal/khaithien/<id người chơi>.jsonl, xem tactu_kynang_xq._capnhatdokhaithien):
#   py _internal/phantich_khaithien.py [id người chơi] [--tu "2026-11-04 20:00"]
# Không ghi id thì gộp mọi file. In: tỉ lệ game nhận chiêu, dự đoán trúng so với trúng thật (con trong hình mất máu / chết), con ngoài
# hình mất máu (người khác đánh hoặc vùng sát thương không đúng hình chữ nhật), hiệu quả lấy góc (đi có đáng không).
import glob
import json
import os
import sys
from collections import Counter, defaultdict

thumuc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "khaithien")
doiso = [a for a in sys.argv[1:] if not a.startswith("--")]
tu = sys.argv[sys.argv.index("--tu") + 1] if "--tu" in sys.argv else ""
if "--tu" in sys.argv:
    doiso = [a for a in doiso if a != tu]
tep = [os.path.join(thumuc, f"{doiso[0]}.jsonl")] if doiso else glob.glob(os.path.join(thumuc, "*.jsonl"))

banghis = []
for duongdan in tep:
    try:
        with open(duongdan, encoding = "utf-8") as f:
            for dong in f:
                try:
                    b = json.loads(dong)
                except ValueError:
                    continue
                if b.get("thoidiem", "") >= tu:
                    banghis.append(b)
    except OSError as err:
        print(f"Không đọc được {duongdan}: {err}")

if not banghis:
    print("Chưa có dữ liệu")
    sys.exit()

# Từ khi đo bằng số bay ("dodem": "sobay", chỉ sát thương của mình) thì bỏ các bản ghi cũ đo bằng máu (lẫn người khác cùng đánh)
# "sobay2": đếm số bay từ lúc gửi + quái chết tính là trúng (bản "sobay" đếm từ lúc chiêu vào hồi nên hụt gần hết)
mocsobay = next((b["thoidiem"] for b in banghis if b.get("dodem") == "sobay2"), None)
if mocsobay and "--tatca" not in sys.argv:
    socu = sum(1 for b in banghis if b["thoidiem"] < mocsobay)
    banghis = [b for b in banghis if b["thoidiem"] >= mocsobay]
    print(f"(Bỏ {socu} bản ghi cũ đo bằng máu trước {mocsobay}; thêm --tatca để xem cả)")
elif not mocsobay:
    print("(Chưa có bản ghi đo bằng số bay: trúng = máu giảm, lẫn cả người khác cùng đánh)")


def is_trung(d):
    if "satthuong" in d:
        return bool(d["satthuong"]) or d["chet"]
    return d["chet"] or (d["mausau"] is not None and d["mausau"] < d["mautruoc"])

loai = Counter(b["loai"] for b in banghis)
rachieu = [b for b in banghis if b["loai"] == "rachieu"]
print(f"Bản ghi: {len(banghis)} (từ {banghis[0]['thoidiem']} tới {banghis[-1]['thoidiem']})")
print(f"  ra chiêu (game nhận): {loai['rachieu']}   gửi mà game không nhận: {loai['khongnhan']}   đi lấy góc rồi bỏ: {loai['laygoc_huy']}")


def tb(ds):
    return sum(ds) / len(ds) if ds else 0.


def inthongke(ten, ds):
    if not ds:
        print(f"\n{ten}: chưa có")
        return
    dudoan = [b["sodudoan"] for b in ds]
    trong = [b["trungtrong"] for b in ds]
    ngoai = [b["trungngoai"] for b in ds]
    sotrong = [b["sotronghinh"] for b in ds]
    # Độ chính xác hình: trong số con nằm trong hình lúc gửi, bao nhiêu % mất máu
    tile = sum(trong) / sum(sotrong) * 100 if sum(sotrong) else 0.
    muctieu = [d for b in ds for d in b["doituongs"] if d["lamuctieu"]]
    trungmuctieu = sum(1 for d in muctieu if is_trung(d))
    print(f"\n{ten}: {len(ds)} lần")
    print(f"  dự đoán trúng tb {tb(dudoan):.2f} | trong hình lúc gửi tb {tb(sotrong):.2f} | trúng thật trong hình tb {tb(trong):.2f} "
          f"({tile:.0f}% con trong hình trúng)")
    print(f"  con ngoài hình trúng tb {tb(ngoai):.2f} (đo bằng số bay mà cao => vùng sát thương rộng hơn hình chữ nhật)")
    print(f"  mục tiêu đang chọn trúng: {trungmuctieu}/{len(muctieu)}   game nhận chiêu sau tb {tb([b['tregui'] for b in ds]):.2f}s")
    phanbo = Counter(b["trungtrong"] for b in ds)
    print("  phân bố trúng thật: " + "  ".join(f"{k} con: {v}" for k, v in sorted(phanbo.items())))


bam = [b for b in rachieu if b.get("chedo", "bammuctieu") == "bammuctieu"]
inthongke("Bám mục tiêu (Lưu Tinh không nối được: rơi kề mục tiêu)", bam)
if bam:
    cach = [max(abs(b["diemroi"][0] - d["toado"][0]), abs(b["diemroi"][1] - d["toado"][1])) for b in bam for d in b["doituongs"] if d["lamuctieu"]]
    print(f"  điểm rơi cách mục tiêu tb {tb(cach):.2f} ô (1 = kề, đánh tiếp được ngay)")
rong = [b for b in rachieu if b.get("chedo") == "rong"]
inthongke("Rộng tại chỗ (Lưu Tinh nối sau)", [b for b in rong if not b.get("laygoc")])
cogoc = [b for b in rong if b.get("laygoc")]
inthongke("Rộng sau khi đi lấy góc", cogoc)
if cogoc:
    print(f"  trước khi đi dự đoán trúng tb {tb([b['laygoc']['sotruoc'] for b in cogoc]):.2f} -> lúc chốt chỗ {tb([b['laygoc']['sodudoan'] for b in cogoc]):.2f}"
          f" -> trúng thật {tb([b['trungtrong'] for b in cogoc]):.2f}")
    print(f"  thời gian đi tb {tb([b['laygoc']['thoigiandi'] for b in cogoc]):.2f}s   lý do dừng: "
          + ", ".join(f"{k} {v}" for k, v in Counter(b['laygoc']['lydo'] for b in cogoc).items()))
    loi = [b["trungtrong"] - b["laygoc"]["sotruoc"] for b in cogoc]
    print(f"  lợi thật so với ra tại chỗ (trúng thật - dự đoán trước khi đi) tb {tb(loi):+.2f}; lần lỗ: {sum(1 for x in loi if x < 0)}")
if rong:
    noi = [b["luutinhnoi"] for b in rong if b.get("luutinhnoi") is not None]
    print(f"\nLưu Tinh nối sau Khai Thiên rộng: {len(noi)}/{len(rong)} lần, sau tb {tb(noi):.2f}s (ghi lúc đo, Lưu Tinh gửi muộn hơn "
          f"1.2s thì không thấy)")
    dung = [b["luutinhdungmuctieu"] for b in rong if b.get("luutinhdungmuctieu") is not None]
    if dung:
        print(f"  Lưu Tinh lướt về đúng mục tiêu của Khai Thiên: {sum(dung)}/{len(dung)}")
# Game không nhận chiêu theo tư thế / đang đánh thường lúc gửi và độ dài cú lướt
guis = [b for b in banghis if b["loai"] in ("rachieu", "khongnhan") and "tuthe" in b]
if guis:
    nhom = defaultdict(lambda: [0, 0])
    for b in guis:
        dai = max(abs(b["diemroi"][0] - b["toado"][0]), abs(b["diemroi"][1] - b["toado"][1]))
        khoa = (f"tư thế {b['tuthe']}", "đánh thường" if b["is_danhthuong"] else "không đánh thường", f"lướt {'<=3' if dai <= 3 else '>3'} ô")
        nhom[khoa][b["loai"] == "khongnhan"] += 1
    print("\nGame không nhận chiêu theo lúc gửi:")
    for khoa, (nhan, hong) in sorted(nhom.items()):
        print(f"  {' | '.join(khoa)}: hỏng {hong}/{nhan + hong} ({hong / (nhan + hong) * 100:.0f}%)")
huy = [b for b in banghis if b["loai"] == "laygoc_huy"]
if huy:
    print(f"\nĐi lấy góc rồi bỏ: {len(huy)} lần, lý do: " + ", ".join(f"{k} {v}" for k, v in Counter(b['lydo'] for b in huy).items())
          + f", đi tb {tb([b['thoigiandi'] for b in huy]):.2f}s")

# Vùng sát thương: con ngoài hình mất máu nằm cách mép hình bao xa (dồn ở 1 ô => hình rộng hơn 1 ô mỗi bên)
khoangngoai = defaultdict(int)
for b in rachieu:
    (x0, y0), (px, py) = b["toado"], b["diemroi"]
    for d in b["doituongs"]:
        if d["tronghinh"] or not is_trung(d):
            continue
        qx, qy = d["toado"]
        cach = max(max(min(x0, px) - qx, qx - max(x0, px), 0), max(min(y0, py) - qy, qy - max(y0, py), 0))
        khoangngoai[round(cach)] += 1
if khoangngoai:
    print("\nCon ngoài hình trúng theo khoảng cách tới mép hình: " + "  ".join(f"{k} ô: {v}" for k, v in sorted(khoangngoai.items())))
