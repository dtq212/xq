"""Đo Cường Hoá Ngoại Công (kỹ năng bang, 2026-11-27): mỗi cấp cộng bao nhiêu sát thương. Chạy tay, cần quyền Admin như bot.

Cường Hoá không cộng vào Ngoại Công trên bảng mà cộng thẳng vào sát thương (người dùng 2026-11-27) nên đo bằng máu tụt của
một nhân vật làm bia ở lôi đài. Mỗi đòn chia cho sát thương công thức (congthucsatthuong_xq, theo Công bảng người đánh lúc trước đòn
và Kháng bảng của bia) -> "tỉ số"; Công trôi theo máu (Đào Hoa Dã Tính) vẫn so được giữa các đợt. So tỉ số đợt CH<n> với CH0.

    python -X utf8 docuonghoa_xq.py --nhan CH0 [--danh Thỏ --bi Kng --hoi Thk --sodon 30]
    python -X utf8 docuonghoa_xq.py --phantich

Một đợt: người dùng đưa 3 nhân vật vào lôi đài, đứng sát nhau, TẠM DỪNG bot của cả 3 (bot tự đánh / buff / uống thuốc làm sai số).
Công cụ tự xếp nhóm (người hồi + bia chung nhóm để hồi được, người đánh ra ngoài nhóm để đánh được bia), gửi "kill <ID bia>" cho
người đánh (máy chủ tự đánh thường tới khi bia chết / đổi mục tiêu), người hồi "pf <chiêu hồi> <ID bia>" khi bia dưới NGUONGHOI.
Đủ --sodon đòn sạch thì báo xong, vẫn hồi cho bia tới khi người đánh rời bản đồ (về bang nâng cấp) hoặc hết THOIGIANCHOROI.
Đòn ngay sau một lần máu bia tăng bị đánh dấu "ganhoi" (máu tụt cùng nhịp đọc với máu hồi thì lượng tụt sai) và bỏ khi phân tích.
Người đánh đang vận khí (bật / tắt tâm pháp) thì không gửi "kill" (kill ngắt vận khí).
Ghi _internal/dosatthuong/cuonghoa_<nhãn>_<lúc>.csv (cùng cột dosatthuong_xq + ganhoi) và in kèm vào cuonghoa.log.

Phân tích: mỗi nhãn tỉ số trung bình (bỏ bạo kích: tỉ số > HESOTACHBAOKICH x trung vị) -> Δ% so với CH0 cùng hậu tố (CH1-thao so với
CH0-thao). Cộng theo %: Δ% như nhau ở 2 mức Kháng; cộng số cố định: Δ điểm như nhau, Δ% lớn hơn ở mức Kháng cao (đòn nhỏ).
"""
import argparse
import csv
import glob
import os
import re
import statistics
import sys
import time
import unicodedata

from congthucsatthuong_xq import HE_NGOAI, SATTHUONGTOITHIEUSUYRA, satthuong
from dosatthuong_xq import COTCHISOs, THUMUCDOSATTHUONG, docnhanvat, timnhanvats
from hangso_xq import VITRIKYNANG_CAMLOTRI, VITRIKYNANG_SOTRI
from sosanhbuild_xq import guilenh

DUONGDANLOG = os.path.join(THUMUCDOSATTHUONG, "cuonghoa.log")
# Đợt đang chạy ghi mã của mình vào đây; đợt cũ thấy mã khác thì tự dừng (đợt cũ chạy quyền Admin, cửa sổ hay bị che, tắt từ ngoài
# không ăn: 2026-11-27 hai đợt chạy song song ~1 phút, cùng gửi kill / hồi)
DUONGDANDANGCHAY = os.path.join(THUMUCDOSATTHUONG, "dangchay.txt")
CHUKYDOC = 0.01
# Bia dưới chừng này % máu thì người hồi hồi; giãn cách giữa 2 lần gửi chiêu hồi
NGUONGHOI = 0.6
GIANCACHHOI = 1.2
# Đòn tới trong chừng này giây sau 1 lần máu bia tăng (hồi) thì đánh dấu ganhoi: chỉ đòn trùng nhịp đọc với máu hồi mới bị sai lượng tụt.
# Bản đầu đánh dấu cả [gửi hồi - 0.2s, + 2s]: Thk hồi dày, 27/46 đòn CH0 bị bỏ (2026-11-27)
SAUMAUTANG = 0.05
# Không có đòn nào trong chừng này giây thì gửi lại "kill"
THOIGIANGUILAIKILL = 4.
# Xong đợt mà người đánh chưa rời bản đồ: vẫn hồi cho bia tối đa chừng này giây rồi thoát
THOIGIANCHOROI = 600.
# Khoảng cách ô vuông tối đa giữa người đánh và bia để bắt đầu (Đào Hoa cận chiến, tầm 1)
KHOANGCACHTOIDA = 3
# Đòn có tỉ số > hệ số này x trung vị là bạo kích (bạo x2, random ±1.5%)
HESOTACHBAOKICH = 1.5
# Đòn thường lệch trung vị quá chừng này thì bỏ (hồi máu trùng nhịp, đòn lẻ của pháp bảo đỡ...)
LECHTOIDA = 0.08


def inlog(noidung):
    dong = f"[{time.strftime('%H:%M:%S')}] {noidung}"
    print(dong, flush = True)
    os.makedirs(THUMUCDOSATTHUONG, exist_ok = True)
    with open(DUONGDANLOG, "a", encoding = "utf-8") as f:
        f.write(dong + "\n")


def bodau(chuoi):
    chuoi = unicodedata.normalize("NFD", " ".join((chuoi or "").split()).lower()).replace("đ", "d")
    return "".join(c for c in chuoi if unicodedata.category(c) != "Mn")


def timnhanvat(nhanvats, ten):
    # Theo ID người chơi, tên đúng, rồi tên bỏ dấu (gõ "Tho" vẫn ra "Thỏ")
    if ten.isdigit():
        return next((t for t, mt in nhanvats.items() if mt.get_idnguoichoi() == int(ten)), None)
    for t in nhanvats:
        if bodau(t) == bodau(ten):
            return t
    return None


def ngoainhom(mt):
    # Người đánh đang có nhóm: rời (cùng nhóm không đánh nhau được)
    if mt.get_is_dangnamtrongnhom():
        guilenh(mt, f"team x {mt.get_idnguoichoi()}")
        time.sleep(1.)


def xepnhom(mthoi, mtbi):
    # Người hồi + bia chung nhóm: người hồi mời ("team + <bia>"), bia đồng ý bằng lệnh nút Xác Nhận ("team + <người hồi>")
    idhoi, idbi = mthoi.get_idnguoichoi(), mtbi.get_idnguoichoi()
    for _ in range(5):
        if idbi in mthoi.get_danhsachidnguoichoithanhviennhoms():
            return True
        if mtbi.get_is_dangnamtrongnhom():
            guilenh(mtbi, f"team x {idbi}")
            time.sleep(1.)
        guilenh(mthoi, f"team + {idbi}")
        time.sleep(1.)
        guilenh(mtbi, f"team + {idhoi}")
        time.sleep(1.5)
    return idbi in mthoi.get_danhsachidnguoichoithanhviennhoms()


def khoangcach(mt1, mt2):
    (x1, y1), (x2, y2) = mt1.get_toado()[:2], mt2.get_toado()[:2]
    return max(abs(x1 - x2), abs(y1 - y2))


def dodot(thamso):
    nhanvats = timnhanvats()
    if not nhanvats:
        inlog("Không thấy cửa sổ game nào có nhân vật (chạy bằng quyền Admin?)")
        return
    tens = {}
    for vai, ten in (("danh", thamso.danh), ("bi", thamso.bi), ("hoi", thamso.hoi)):
        tens[vai] = timnhanvat(nhanvats, ten)
        if not tens[vai]:
            inlog(f"Không thấy nhân vật '{ten}'. Đang mở: {', '.join(nhanvats)}")
            return
    mtdanh, mtbi, mthoi = nhanvats[tens["danh"]], nhanvats[tens["bi"]], nhanvats[tens["hoi"]]
    iddanh, idbi = mtdanh.get_idnguoichoi(), mtbi.get_idnguoichoi()
    bando = {vai: nhanvats[t]._get_idbandohientai() for vai, t in tens.items()}
    if len(set(bando.values())) != 1:
        inlog(f"3 nhân vật chưa cùng bản đồ: {bando}")
        return
    kc = khoangcach(mtdanh, mtbi)
    if kc > KHOANGCACHTOIDA:
        inlog(f"{tens['danh']} cách {tens['bi']} {kc} ô (cần <= {KHOANGCACHTOIDA}): đưa lại gần rồi chạy lại")
        return
    chieuhoi = VITRIKYNANG_CAMLOTRI if mthoi.get_is_kynangdahoc(VITRIKYNANG_CAMLOTRI) else VITRIKYNANG_SOTRI
    idbandogoc = bando["danh"]

    danh0, bi0 = docnhanvat(mtdanh), docnhanvat(mtbi)
    if not danh0 or not bi0:
        inlog("Chưa đọc được chỉ số người đánh / bia")
        return
    inlog(f"=== Đợt {thamso.nhan}: {tens['danh']} ({iddanh}) đánh {tens['bi']} ({idbi}), {tens['hoi']} hồi bằng pf {chieuhoi}, "
          f"bản đồ {idbandogoc}")
    inlog(f"Bảng {tens['danh']}: Ngoại Công {danh0[2]['ngoaicong1']}-{danh0[2]['ngoaicong2']}, Bạo Kích {danh0[2]['baokich'] / 100:.2f}%, "
          f"máu {danh0[0]}/{danh0[1]} | {tens['bi']}: Ngoại Kháng {bi0[2]['ngoaikhang1']}-{bi0[2]['ngoaikhang2']}, máu {bi0[0]}/{bi0[1]}")

    ngoainhom(mtdanh)
    if not xepnhom(mthoi, mtbi):
        inlog(f"Không xếp được {tens['hoi']} + {tens['bi']} chung nhóm: vẫn đo, hồi có thể không ăn")
    if mtdanh.get_is_dangnamtrongnhom() and iddanh in mtbi.get_danhsachidnguoichoithanhviennhoms():
        inlog(f"{tens['danh']} vẫn chung nhóm với {tens['bi']}: không đánh được, dừng")
        return

    duongdan = os.path.join(THUMUCDOSATTHUONG, f"cuonghoa_{re.sub(r'[^0-9A-Za-z_-]', '_', thamso.nhan)}_{time.strftime('%Y%m%d-%H%M%S')}.csv")
    cots = (["thoidiem", "nhan", "nguoibidanh", "satthuong", "mautruoc", "mautoida"] + ["bi_" + c for c in COTCHISOs]
            + ["nguoidanh"] + ["danh_" + c for c in COTCHISOs] + ["ganhoi", "tiso"])
    inlog(f"Ghi vào {duongdan}")

    lucguihois, lucdonsau, luckill, lucmautang = [], time.time(), 0., 0.
    madot = f"{os.getpid()}-{time.time()}"
    with open(DUONGDANDANGCHAY, "w", encoding = "utf-8") as fd:
        fd.write(madot)
    lucxetdangchay = 0.
    sodon = sosach = 0
    tisos = []
    lucxong = None
    truocdanh, truocbi = danh0, bi0
    with open(duongdan, "w", newline = "", encoding = "utf-8-sig") as f:
        ghi = csv.writer(f)
        ghi.writerow(cots)
        try:
            while True:
                time.sleep(CHUKYDOC)
                baygio = time.time()
                sau = docnhanvat(mtbi)
                saudanh = docnhanvat(mtdanh) or truocdanh
                if not sau:
                    continue
                if baygio - lucxetdangchay > 1.:
                    lucxetdangchay = baygio
                    try:
                        with open(DUONGDANDANGCHAY, encoding = "utf-8") as fd:
                            is_dotmoi = fd.read().strip() != madot
                    except OSError:
                        is_dotmoi = False
                    if is_dotmoi:
                        inlog(f"Có đợt mới chạy: dừng đợt {thamso.nhan}")
                        break
                # Người đánh rời bản đồ (về bang nâng cấp) -> hết đợt
                if mtdanh._get_idbandohientai() != idbandogoc:
                    inlog(f"{tens['danh']} đã rời bản đồ")
                    break
                # "kill" ngắt vận khí (tắt Dã Tính / Nguyên Khí cũng là vận khí): người đánh đang vận khí thì không gửi lại
                if (lucxong is None and baygio - max(lucdonsau, luckill) > THOIGIANGUILAIKILL
                        and not mtdanh._get_is_dangvankhitrongame()):
                    guilenh(mtdanh, f"kill {idbi}")
                    luckill = baygio
                # Hồi cho bia
                if sau[0] < sau[1] * NGUONGHOI and (not lucguihois or baygio - lucguihois[-1] > GIANCACHHOI):
                    guilenh(mthoi, f"pf {chieuhoi} {idbi}")
                    lucguihois.append(baygio)
                satthuongdon = truocbi[0] - sau[0]
                if satthuongdon < 0:
                    lucmautang = baygio
                if satthuongdon > 0 and truocbi[1] == sau[1] and truocdanh:
                    lucdonsau = baygio
                    sodon += 1
                    cong, khang = truocdanh[2]["ngoaicong1"], truocbi[2]["ngoaikhang1"]
                    tiso = satthuongdon / max(satthuong(cong, khang, HE_NGOAI), 1.)
                    ganhoi = int(baygio - lucmautang <= SAUMAUTANG + CHUKYDOC)
                    ghi.writerow([round(baygio, 3), thamso.nhan, tens["bi"], satthuongdon, truocbi[0], truocbi[1]]
                                 + [truocbi[2][c] for c in COTCHISOs] + [tens["danh"]] + [truocdanh[2][c] for c in COTCHISOs]
                                 + [ganhoi, round(tiso, 4)])
                    f.flush()
                    if not ganhoi and satthuongdon >= SATTHUONGTOITHIEUSUYRA:
                        tisos.append(tiso)
                        trungvi = statistics.median(tisos)
                        if tiso < trungvi * HESOTACHBAOKICH:
                            sosach += 1
                    print(f"#{sodon} -{satthuongdon} tỉ số {tiso:.3f}{' (gần hồi)' if ganhoi else ''} | NC {cong} Kháng {khang} | "
                          f"sạch {sosach}/{thamso.sodon}", flush = True)
                    if lucxong is None and sosach >= thamso.sodon:
                        lucxong = baygio
                        inlog(f"XONG đợt {thamso.nhan}: {sosach} đòn sạch. Đưa {tens['danh']} về bang nâng cấp (công cụ vẫn hồi cho "
                              f"{tens['bi']} tới khi {tens['danh']} rời bản đồ)")
                if lucxong is not None and baygio - lucxong > THOIGIANCHOROI:
                    break
                truocbi, truocdanh = sau, saudanh
        except KeyboardInterrupt:
            pass
    inlog(f"Đợt {thamso.nhan}: ghi {sodon} đòn, {sosach} đòn sạch")
    phantich(inra = True)


def docdons():
    dons = []
    for duongdan in sorted(glob.glob(os.path.join(THUMUCDOSATTHUONG, "cuonghoa_*.csv"))):
        with open(duongdan, encoding = "utf-8-sig") as f:
            for dong in csv.DictReader(f):
                dons.append({"nhan": dong["nhan"], "satthuong": float(dong["satthuong"]), "ganhoi": dong["ganhoi"] == "1",
                             "cong": float(dong["danh_ngoaicong1"]), "khang": float(dong["bi_ngoaikhang1"])})
    return dons


def tomtat(dons):
    # Đòn thường sạch của 1 nhãn -> (số đòn, tỉ số TB, sai số chuẩn, sát thương TB, sát thương công thức TB, Công TB, Kháng TB, số bạo)
    for don in dons:
        don["congthuc"] = satthuong(don["cong"], don["khang"], HE_NGOAI)
        don["tiso"] = don["satthuong"] / max(don["congthuc"], 1.)
    dons = [d for d in dons if not d["ganhoi"] and d["satthuong"] >= SATTHUONGTOITHIEUSUYRA]
    if not dons:
        return None
    trungvi = statistics.median(d["tiso"] for d in dons)
    sobao = sum(1 for d in dons if d["tiso"] >= trungvi * HESOTACHBAOKICH)
    thuongs = [d for d in dons if d["tiso"] < trungvi * HESOTACHBAOKICH]
    trungvi = statistics.median(d["tiso"] for d in thuongs)
    thuongs = [d for d in thuongs if abs(d["tiso"] / trungvi - 1) <= LECHTOIDA]
    n = len(thuongs)
    tisos = [d["tiso"] for d in thuongs]
    tb = statistics.mean(tisos)
    ssc = statistics.stdev(tisos) / n ** 0.5 if n > 1 else 0.
    return {"n": n, "tiso": tb, "ssc": ssc, "st": statistics.mean(d["satthuong"] for d in thuongs),
            "ct": statistics.mean(d["congthuc"] for d in thuongs), "cong": statistics.mean(d["cong"] for d in thuongs),
            "khang": statistics.mean(d["khang"] for d in thuongs), "bao": sobao}


def phantich(inra = True):
    nhoms = {}
    for don in docdons():
        nhoms.setdefault(don["nhan"], []).append(don)
    if not nhoms:
        inlog("Chưa có dữ liệu cuonghoa_*.csv")
        return
    tts = {nhan: tomtat(dons) for nhan, dons in nhoms.items()}
    inlog("--- Phân tích Cường Hoá (tỉ số = sát thương thật / công thức theo Công + Kháng bảng) ---")
    for nhan in sorted(tts, key = lambda x: (re.sub(r"^CH\d+", "", x), int(re.match(r"CH(\d+)", x).group(1)) if re.match(r"CH(\d+)", x) else 0)):
        tt = tts[nhan]
        if not tt:
            continue
        dong = (f"{nhan:>10}: {tt['n']:3d} đòn, tỉ số {tt['tiso']:.4f} ±{tt['ssc']:.4f}, ST TB {tt['st']:.0f} (công thức {tt['ct']:.0f}), "
                f"NC {tt['cong']:.0f} Kháng {tt['khang']:.0f}, bạo {tt['bao']}")
        hauto = re.sub(r"^CH\d+", "", nhan)
        goc = tts.get("CH0" + hauto)
        if goc and nhan != "CH0" + hauto:
            phantram = (tt["tiso"] / goc["tiso"] - 1) * 100
            saiso = ((tt["ssc"] / tt["tiso"]) ** 2 + (goc["ssc"] / goc["tiso"]) ** 2) ** 0.5 * 100
            # Cộng số cố định: phần thừa so với CH0 quy về mức Công / Kháng của đợt này
            diem = tt["st"] - goc["tiso"] * tt["ct"]
            dong += f" | so CH0{hauto}: {phantram:+.2f}% ±{saiso:.2f}%, {diem:+.0f} điểm/đòn"
        inlog(dong)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding = "utf-8", line_buffering = True)
    thamso = argparse.ArgumentParser(description = "Đo Cường Hoá Ngoại Công")
    thamso.add_argument("--nhan", help = "nhãn đợt: CH0 (chưa nâng), CH1, CH2...; thêm -thao khi bia tháo 1 món thủ")
    thamso.add_argument("--danh", default = "Thỏ", help = "người đánh (tên hoặc ID)")
    thamso.add_argument("--bi", default = "Kng", help = "bia (tên hoặc ID)")
    thamso.add_argument("--hoi", default = "Thk", help = "người hồi máu cho bia, Vân Mộng Cốc (tên hoặc ID)")
    thamso.add_argument("--sodon", type = int, default = 30, help = "số đòn thường sạch mỗi đợt")
    thamso.add_argument("--phantich", action = "store_true", help = "chỉ phân tích các đợt đã đo")
    thamso = thamso.parse_args()
    if thamso.phantich:
        phantich()
    elif not thamso.nhan:
        print("Cần --nhan (CH0, CH1...) hoặc --phantich")
    else:
        dodot(thamso)


if __name__ == "__main__":
    main()
