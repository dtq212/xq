"""So build theo công thức sát thương đo thực tế (congthucsatthuong_xq.py). Chạy tay, cần quyền Admin như bot (game chạy Admin).

    python -X utf8 sosanhbuild_xq.py                       xem mọi nhân vật đang mở: điểm tấn công, độ trâu, giá trị biên
    python -X utf8 sosanhbuild_xq.py --thu "Thọ"           mặc thử từng món trang bị trong túi, đọc lại bảng chỉ số rồi trả đồ cũ
    python -X utf8 sosanhbuild_xq.py --thu "Thọ" --mon "Phi Phong,Chi Dực"   chỉ thử món có tên chứa các chuỗi này
    tuỳ chọn: --he ngoai|noi (ép hệ đánh), --khang 1500,2000 (Kháng mục tiêu để so), --phongan (thử cả đồ mặc vào bị Phong Ấn)

Thử đồ bằng cách mặc thật (lệnh "use <id>#") nên tính đúng cả hiệu ứng bộ (vd hạng liên Thục Sơn đủ bộ +4% Bạo Kích) mà mô tả
từng món không ghi. Mỗi món: mặc, chờ bảng chỉ số đứng yên, ghi lại, mặc lại món cũ ô đó (ô trống thì "remove <ô>"). Đồ ghi
"Sau khi trang bị sẽ bị Phong Ấn" bỏ qua (mặc vào là khoá) trừ khi có --phongan. Đào Hoa đang Dã Tính / Kim Cường không đổi đồ
được: món nào mặc không vào thì bỏ qua. Nên chạy lúc bot của nhân vật đó đứng yên (bot tự đổi pháp bảo khi máu thấp).
"""
import argparse
import re
import sys
import time
import unicodedata

from congthucsatthuong_xq import (HE_NGOAI, HE_NOI, KHANGMUCTIEUMACDINHs, chonhe, diemtancong, giatribien, sodonchiu,
                                  satthuongkyvong)
from dosatthuong_xq import timnhanvats
from hangso_xq import CHISONHANVAT_MAP, SOLUONGOTRANGBI, TENMONPHAI, VITRITRANGBIDAUTIEN
from tienich_xq import ghilognhanvat, taithongtinnguoichoi, write_bytes
from diachi_xq import DC

TENHE_MAP = {HE_NGOAI: "Ngoại", HE_NOI: "Nội"}
TENOTRANGBIs = ("Nón", "Hạng liên", "Vũ khí", "Áo", "Yêu đới", "Giày", "Pháp bảo", "Ô 8", "Ô 9", "Ô 10")
# Loại vật phẩm (chữ trong ［］ dòng 2 mô tả) là trang bị. Tín vật, phi phong / cánh, ngoại trang không ghi loại trong mô tả
# (đo 2026-11-05 trên Thọ) nên chỉ thử khi chỉ tên bằng --mon
LOAITRANGBIs = {"Vũ Khí", "Nón", "Y Phục", "Yêu Đới", "Hạng Liên", "Giày", "Pháp Bảo"}
# Chờ mô tả / chờ món vào ô / chờ bảng chỉ số đứng yên sau khi đổi đồ (đo: chỉ số đổi trong ~0.2-0.5s sau lệnh). Đổi pháp bảo
# liền nhau có lúc không vào (thử Thượng Phương Bảo Kiếm rồi mặc lại Nhiếp Hồn Linh: 2.5s chưa vào, gửi lại sau đó vào ngay) nên
# chưa vào thì gửi lại lệnh mỗi GIANCACHGUILAIMAC giây
THOIGIANCHOMOTA = 1.5
THOIGIANCHOMAC = 6.
GIANCACHGUILAIMAC = 1.5
THOIGIANCHOCHISO = 0.6


def docchiso(mt):
    # {khihuyet, ngoaicong, ngoaikhang, thanthu, noicong, noikhang, baokich (%)} từ ô thấp mỗi cặp, None khi chưa đọc được
    dichs = [dichs[0] for dichs in CHISONHANVAT_MAP.values()]
    chisos = mt.get_chisonhanvats(dichs)
    if not chisos:
        return None
    ketqua = dict(zip(("khihuyet", "ngoaicong", "ngoaikhang", "thanthu", "noicong", "noikhang", "baokich"), chisos))
    ketqua["baokich"] /= 100.
    return ketqua


def guilenh(mt, lenh):
    # Gửi thẳng (cấp vùng nhớ riêng gọi HAMGUILENH, không qua hàng đợi của bot). Dòng log lệnh chỉ ghi vào file log nhân vật,
    # không in ra (thử 1 nhân vật in hơn 100 dòng desc / use lẫn vào kết quả)
    with mt._khoathucthicaulenh2:
        inlog = mt._inlog
        mt._inlog = lambda noidung: ghilognhanvat(mt.get_idnguoichoi() or f"cuaso_{mt.idcuaso}",
                                                   f"[{time.strftime('%H:%M:%S')} {mt.get_idnguoichoi()}] {noidung}")
        try:
            return mt._thucthicaulenh2(lenh)
        finally:
            mt._inlog = inlog


def chochisodungyen(mt, thoigiantoida = 3.):
    # Đọc lại tới khi 2 lần liền nhau giống nhau (đổi đồ xong chỉ số cập nhật vài nhịp)
    truoc, het = docchiso(mt), time.time() + thoigiantoida
    while time.time() < het:
        time.sleep(THOIGIANCHOCHISO)
        sau = docchiso(mt)
        if sau and sau == truoc:
            return sau
        truoc = sau
    return truoc


def docmota(mt, vitri):
    # Mô tả ô vitri (hành trang 0-95: "desc <id>#", trang bị 96-105: "desc <ô - 95>"), bỏ mã màu; "" nếu không ra
    x = mt.get_diachicosothongtinvatphamhanhtrang()
    iddoituong = mt.get_iddoituongvatphamhanhtrang(vitri)
    if not x or not iddoituong:
        return ""
    write_bytes(mt.tientrinh, x + vitri * DC.HT_KICHTHUOCMOTA + DC.HT_MOTA, b"\x00", 1)
    guilenh(mt, "desc {}".format(vitri - VITRITRANGBIDAUTIEN + 1) if vitri >= VITRITRANGBIDAUTIEN else "desc {:x}#".format(iddoituong))
    het = time.time() + THOIGIANCHOMOTA
    while time.time() < het:
        mota = mt.get_motavatphamhanhtrangcosan(vitri)
        if mota:
            return unicodedata.normalize("NFC", re.sub(r"\x1b[a-zA-Z0-9]", "", mota))
        time.sleep(0.05)
    return ""


def loaivatpham(mota):
    # Chữ trong cặp [] / ［］ đầu tiên sau dòng tên ("" nếu không có)
    dongs = [dong.strip() for dong in mota.split("\n") if dong.strip()]
    khop = re.search(r"[\[［]\s*([^\]］\n]*?)\s*[\]］]", "\n".join(dongs[1:]))
    return khop.group(1) if khop else ""


def tenvatpham(mt, vitri):
    return re.sub(r"\x1b[a-zA-Z0-9]", "", mt.get_tenvatphamhanhtrang(vitri) or "").strip()


def trangbihientai(mt):
    # {ô 96-105: id vật phẩm hoặc 0}
    return {vitri: mt.get_iddoituongvatphamhanhtrang(vitri) or 0 for vitri in range(VITRITRANGBIDAUTIEN, VITRITRANGBIDAUTIEN + SOLUONGOTRANGBI)}


def vitritrongtui(mt, iddoituong):
    for vitri in range(VITRITRANGBIDAUTIEN):
        if mt.get_iddoituongvatphamhanhtrang(vitri) == iddoituong:
            return vitri
    return None


def macvao(mt, iddoituong):
    # "use <id>#" rồi chờ món vào 1 ô trang bị (chưa vào thì gửi lại) -> ô đó, hết giờ thì None
    het, lucgui = time.time() + THOIGIANCHOMAC, 0.
    while time.time() < het:
        if time.time() - lucgui >= GIANCACHGUILAIMAC:
            guilenh(mt, f"use {iddoituong:x}#")
            lucgui = time.time()
        for vitri, idmon in trangbihientai(mt).items():
            if idmon == iddoituong:
                return vitri
        time.sleep(0.1)
    return None


def lydobo(mota, monphai, capdo):
    # Lý do khỏi thử theo mô tả (khác phái, chưa đủ cấp), None nếu thử được
    khop = re.search(r"Trang bị của phái:\s*([^\n]+)", mota)
    if khop and monphai in TENMONPHAI and khop.group(1).strip() != TENMONPHAI[monphai]:
        return "đồ phái " + khop.group(1).strip()
    khop = re.search(r"(?:Cấp độ sử dụng: cấp|Trang bị yêu cầu:)\s*(\d+)", mota)
    if khop and capdo and int(khop.group(1)) > capdo:
        return f"cần cấp {khop.group(1)}"
    return None


TENKHANG_MAP = {HE_NGOAI: "ngoaikhang", HE_NOI: "noikhang"}
TENCONG_MAP = {HE_NGOAI: "ngoaicong", HE_NOI: "noicong"}


def khangscho(thamso, he):
    # Các mức Kháng mục tiêu để tính hệ he: có đối thủ (--doithu) và đã đo Kháng hệ đó thì đúng số của họ, không thì mặc định / --khang
    doithu = getattr(thamso, "doithu", None)
    if doithu and doithu.get(TENKHANG_MAP[he]):
        return (doithu[TENKHANG_MAP[he]]["giatri"],)
    return thamso.khangs


def congdoithu(thamso):
    # (hệ, Công) đối thủ đã đo (đo khi họ đánh mình, chỉ lưu khi biết hệ theo môn phái), không có thì None
    doithu = getattr(thamso, "doithu", None) or {}
    for he in (HE_NGOAI, HE_NOI):
        if doithu.get(TENCONG_MAP[he]):
            return he, doithu[TENCONG_MAP[he]]["giatri"]
    return None


def sodonchiudoithu(chiso, thamso):
    # Số đòn thường (kỳ vọng, bạo 9%) của đối thủ đã đo Công để hạ nhân vật có chiso, None nếu chưa đo Công họ
    cd = congdoithu(thamso)
    if not cd:
        return None
    he, cong = cd
    khang = chiso["ngoaikhang"] if he == HE_NGOAI else chiso["noikhang"]
    return chiso["khihuyet"] / max(satthuongkyvong(cong, khang, he, 9.), 1.)


def danhgia(chiso, he, khangs, thamso = None):
    return {
        "tancong": diemtancong(chiso, he, khangs),
        "trau_ngoai": sodonchiu(chiso, HE_NGOAI),
        "trau_noi": sodonchiu(chiso, HE_NOI),
        "trau_doithu": sodonchiudoithu(chiso, thamso) if thamso else None,
    }


def inxem(ten, mt, thamso):
    chiso = docchiso(mt)
    if not chiso:
        print(f"== {ten}: chưa đọc được chỉ số")
        return
    monphai = mt.get_tenmonphai()
    he = thamso.he or chonhe(monphai, chiso)
    cong = chiso["ngoaicong"] if he == HE_NGOAI else chiso["noicong"]
    khangs = khangscho(thamso, he)
    dg = danhgia(chiso, he, khangs, thamso)
    print(f"\n== {ten} ({TENMONPHAI.get(monphai, monphai)}, đánh hệ {TENHE_MAP[he]})")
    print(f"   Khí Huyết {chiso['khihuyet']} | Ngoại Công {chiso['ngoaicong']} Kháng {chiso['ngoaikhang']} | Nội Công {chiso['noicong']}"
          f" Kháng {chiso['noikhang']} | Thân Thủ {chiso['thanthu']} | Bạo Kích {chiso['baokich']:.2f}%")
    print("   Sát thương kỳ vọng 1 đòn gốc: " + ", ".join(f"Kháng {k}: {satthuongkyvong(cong, k, he, chiso['baokich']):.0f}"
                                                     for k in khangs))
    print(f"   Độ trâu: chịu {dg['trau_ngoai']:.1f} đòn Ngoại / {dg['trau_noi']:.1f} đòn Nội của người đánh tham chiếu")
    khang = khangs[len(khangs) // 2]
    goc, bien = giatribien(cong, khang, he, chiso["baokich"])
    print(f"   Giá trị biên (mục tiêu Kháng {khang}, đòn {goc:.0f}): "
          + " | ".join(f"{t} {st / goc * 100:+.1f}%" + (f" (= {qd:.0f} Công)" if "Công" not in t else "") for t, (st, qd) in bien.items()))
    if getattr(thamso, "doithu", None):
        return inxemdoithu(ten, chiso, he, cong, thamso)
    return None


def inxemdoithu(ten, chiso, he, cong, thamso):
    # Phần riêng khi chọn đối thủ (--doithu): đánh người đó mỗi đòn bao nhiêu / mấy đòn hạ, chịu được mấy đòn của họ, nên build gì.
    # -> (tên, số đòn hạ hoặc sát thương 1 đòn nếu chưa biết máu họ) để xếp hạng ai đánh người đó tốt nhất
    doithu = thamso.doithu
    tendt = doithu.get("ten") or thamso.iddoithu
    print(f"   --- Đánh {tendt}:")
    if not doithu.get(TENKHANG_MAP[he]):
        print(f"   Chưa đo {TENHE_MAP[he]} Kháng của {tendt} (cần nhân vật hệ {TENHE_MAP[he]} đánh người này): đang tính theo Kháng {thamso.khangs}")
        return None
    khang = doithu[TENKHANG_MAP[he]]["giatri"]
    st = satthuongkyvong(cong, khang, he, chiso["baokich"])
    khihuyet = (doithu.get("khihuyet") or {}).get("giatri")
    print(f"   {TENHE_MAP[he]} Kháng {khang:,} => mỗi đòn gốc ≈ {st:.0f} (kỳ vọng tính bạo)"
          + (f", hạ {tendt} (Khí Huyết {khihuyet:,}) trong ≈ {khihuyet / st:.0f} đòn gốc" if khihuyet else ", chưa đo Khí Huyết của họ"))
    _, bien = giatribien(cong, khang, he, chiso["baokich"])
    motbk = bien["+1% Bạo Kích"][1]
    tram = bien["+100 Công"][0] / st * 100
    phagiap = -bien["+100 Kháng mục tiêu"][1]
    print(f"   Khuyên: +100 {TENHE_MAP[he]} Công = +{tram:.1f}% sát thương lên {tendt}; 1% Bạo Kích = {motbk:.0f} Công;"
          f" phá giáp -100 {TENHE_MAP[he]} Kháng của họ = {phagiap:.0f} Công")
    print(f"   => Món +X% Bạo Kích hơn món +Y {TENHE_MAP[he]} Công khi X * {motbk:.0f} > Y"
          + (f". Kháng của {tendt} cao so với Công của bạn: Công / phá giáp đáng hơn Bạo Kích" if khang > cong else ""))
    trau = sodonchiudoithu(chiso, thamso)
    cd = congdoithu(thamso)
    if trau and cd:
        hedt, congdt = cd
        khangminh = chiso["ngoaikhang"] if hedt == HE_NGOAI else chiso["noikhang"]
        chiso100 = dict(chiso, **{TENKHANG_MAP[hedt]: khangminh + 100})
        chisomau = dict(chiso, khihuyet = chiso["khihuyet"] + 1000)
        print(f"   {tendt} đánh {TENHE_MAP[hedt]} (Công ≈ {congdt:,}): bạn chịu ≈ {trau:.0f} đòn gốc của họ;"
              f" +100 {TENHE_MAP[hedt]} Kháng => +{(sodonchiudoithu(chiso100, thamso) / trau - 1) * 100:.1f}%,"
              f" +1000 Khí Huyết => +{(sodonchiudoithu(chisomau, thamso) / trau - 1) * 100:.1f}% số đòn chịu được")
    else:
        print(f"   Chưa đo Công của {tendt} (đo khi người này đánh nhân vật của bạn) nên chưa tính được bạn chịu mấy đòn")
    return ten, (khihuyet / st) if khihuyet else None, st


def thudo(ten, mt, thamso):
    monphai = mt.get_tenmonphai()
    goc = chochisodungyen(mt)
    if not goc:
        print("Chưa đọc được chỉ số")
        return
    he = thamso.he or chonhe(monphai, goc)
    khangs = khangscho(thamso, he)
    dggoc = danhgia(goc, he, khangs, thamso)
    trangbigoc = trangbihientai(mt)
    tendt = (thamso.doithu or {}).get("ten") if getattr(thamso, "doithu", None) else None
    print(f"== Thử đồ {ten} ({TENMONPHAI.get(monphai, monphai)}, hệ {TENHE_MAP[he]}), mức Kháng mục tiêu {khangs}"
          + (f" (của {tendt})" if tendt and khangs != thamso.khangs else ""))
    capdo = mt.get_capdonhanvat()
    monchidinhs = [m.strip() for m in (thamso.mon or "").split(",") if m.strip()]
    ungviens, bos = [], []
    for vitri in range(VITRITRANGBIDAUTIEN):
        idmon = mt.get_iddoituongvatphamhanhtrang(vitri)
        if not idmon:
            continue
        tenmon = tenvatpham(mt, vitri)
        chidinh = any(m in tenmon for m in monchidinhs)
        if monchidinhs and not chidinh and not thamso.ca:
            continue
        mota = docmota(mt, vitri)
        loai = loaivatpham(mota)
        if loai not in LOAITRANGBIs and not chidinh:
            continue
        dongten = mota.split("\n")[0]
        lydo = lydobo(mota, monphai, capdo)
        if not lydo and "sẽ bị Phong Ấn" in dongten and not thamso.phongan:
            lydo = "mặc vào sẽ bị Phong Ấn (--phongan để thử)"
        if lydo:
            bos.append(f"{tenmon} ({lydo})")
            continue
        ungviens.append((idmon, tenmon, loai or "?"))
    if bos:
        print(f"   Bỏ qua {len(bos)} món: " + "; ".join(bos))
    print(f"   {len(ungviens)} món để thử: " + ", ".join(u[1] for u in ungviens))

    ketquas = []
    for idmon, tenmon, loai in ungviens:
        truoc = trangbihientai(mt)
        o = macvao(mt, idmon)
        if o is None:
            print(f"   - {tenmon} [{loai}]: không mặc được (giới tính / đang khoá đổi đồ)")
            continue
        chiso = chochisodungyen(mt)
        dg = danhgia(chiso, he, khangs, thamso)
        ketquas.append((o, tenmon, loai, chiso, dg))
        # Trả món cũ của ô o
        idcu = truoc.get(o)
        if idcu:
            if macvao(mt, idcu) is None:
                print(f"   !! Không mặc lại được món cũ ô {o} (id {idcu:x}), dừng để bạn kiểm tra")
                break
        else:
            guilenh(mt, f"remove {o - VITRITRANGBIDAUTIEN + 1}")
            time.sleep(1.)
        chochisodungyen(mt)

    sau = trangbihientai(mt)
    if sau != trangbigoc:
        print(f"   !! Trang bị khác lúc đầu: {[(TENOTRANGBIs[v - VITRITRANGBIDAUTIEN], tenvatpham(mt, v)) for v in sau if sau[v] != trangbigoc[v]]}")

    print(f"\n   Gốc: tấn công {dggoc['tancong']:.0f} | trâu Ngoại {dggoc['trau_ngoai']:.1f} đòn | trâu Nội {dggoc['trau_noi']:.1f} đòn"
          + (f" | chịu {dggoc['trau_doithu']:.0f} đòn của {tendt}" if dggoc["trau_doithu"] else ""))
    for o in sorted(set(k[0] for k in ketquas)):
        tenhientai = tenvatpham(mt, o) or "(trống)"
        print(f"   [{TENOTRANGBIs[o - VITRITRANGBIDAUTIEN]}] đang mặc: {tenhientai}")
        for _, tenmon, loai, chiso, dg in sorted((k for k in ketquas if k[0] == o), key = lambda k: -k[4]["tancong"]):
            thaydoi = ", ".join(f"{k} {chiso[k] - goc[k]:+g}" for k in goc if abs(chiso[k] - goc[k]) > 1e-6)
            print(f"      {tenmon:28s} tấn công {(dg['tancong'] / dggoc['tancong'] - 1) * 100:+6.1f}%"
                  f" | trâu Ngoại {(dg['trau_ngoai'] / dggoc['trau_ngoai'] - 1) * 100:+6.1f}%"
                  f" | trâu Nội {(dg['trau_noi'] / dggoc['trau_noi'] - 1) * 100:+6.1f}%"
                  + (f" | chịu {tendt} {(dg['trau_doithu'] / dggoc['trau_doithu'] - 1) * 100:+6.1f}%" if dggoc["trau_doithu"] else "")
                  + f" | {thaydoi or 'không đổi chỉ số'}")
    print("   (So từng ô với bộ đang mặc; hiệu ứng bộ có thể đổi khi đổi nhiều ô cùng lúc)")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding = "utf-8", line_buffering = True)
    thamso = argparse.ArgumentParser(description = "So build theo công thức sát thương")
    thamso.add_argument("--thu", help = "tên nhân vật để mặc thử đồ trong túi")
    thamso.add_argument("--hwnd", type = int, help = "như --thu nhưng chỉ theo cửa sổ game (giao diện bot truyền cửa sổ đang chọn)")
    thamso.add_argument("--he", choices = (HE_NGOAI, HE_NOI), help = "ép hệ đánh (mặc định theo môn phái / Công cao hơn)")
    thamso.add_argument("--khang", help = "các mức Kháng mục tiêu, phẩy ngăn cách (mặc định 1200,1800,2400)")
    thamso.add_argument("--phongan", action = "store_true", help = "thử cả đồ mặc vào sẽ bị Phong Ấn")
    thamso.add_argument("--mon", help = "chỉ thử các món có tên chứa chuỗi này (phẩy ngăn cách) - dùng cho phi phong / cánh / tín vật"
                                        " không ghi loại trong mô tả")
    thamso.add_argument("--ca", action = "store_true", help = "cùng với --mon: thử cả các món trang bị khác trong túi")
    thamso.add_argument("--doithu", help = "ID người chơi trong _internal/thongtinnguoichoi.json: tính theo đúng Kháng / Khí Huyết / Công đã"
                                           " đo của người đó")
    thamso = thamso.parse_args()
    thamso.khangs = tuple(int(k) for k in thamso.khang.split(",")) if thamso.khang else KHANGMUCTIEUMACDINHs
    thamso.iddoithu = thamso.doithu
    thamso.doithu = None
    if thamso.iddoithu:
        thamso.doithu = taithongtinnguoichoi().get(str(thamso.iddoithu))
        if not thamso.doithu:
            print(f"Không có người chơi ID {thamso.iddoithu} trong thongtinnguoichoi.json")
            return
        dt = thamso.doithu
        print(f"Đối thủ: {dt.get('ten', '?')} (ID {thamso.iddoithu}) · {dt.get('monphai') or 'môn phái ?'} · "
              + (f"Bang {dt['bangphai']}" if dt.get("bangphai") else "không bang" if dt.get("bangphai") == "" else "bang ?") + " · "
              + " · ".join(f"{ten} {dt[k]['giatri']:,}" for k, ten in (("khihuyet", "Khí Huyết"), ("ngoaikhang", "Ngoại Kháng"),
                                                                       ("noikhang", "Nội Kháng"), ("ngoaicong", "Ngoại Công"), ("noicong", "Nội Công"))
                          if dt.get(k)))

    nhanvats = timnhanvats()
    if not nhanvats:
        print("Không thấy cửa sổ game nào có nhân vật (chạy bằng quyền Admin?)")
        return
    if thamso.hwnd:
        ten = next((ten for ten, mt in nhanvats.items() if mt.idcuaso == thamso.hwnd), None)
        if not ten:
            print(f"Cửa sổ {thamso.hwnd} chưa có nhân vật. Đang mở: {', '.join(nhanvats)}")
            return
        thudo(ten, nhanvats[ten], thamso)
    elif thamso.thu:
        from dangnhap_xq import chuanhoatennhanvat
        ten = chuanhoatennhanvat(thamso.thu)
        if ten not in nhanvats:
            print(f"Không thấy nhân vật '{thamso.thu}'. Đang mở: {', '.join(nhanvats)}")
            return
        thudo(ten, nhanvats[ten], thamso)
    else:
        xephangs = [kq for kq in (inxem(ten, mt, thamso) for ten, mt in nhanvats.items()) if kq]
        if xephangs:
            print(f"\n== Ai đánh {thamso.doithu.get('ten') or thamso.iddoithu} mạnh nhất (sát thương 1 đòn gốc, chưa tính tốc độ ra chiêu):")
            for tenminh, sodon, st in sorted(xephangs, key = lambda k: -k[2]):
                print(f"   {tenminh}: {st:.0f} / đòn" + (f", ≈ {sodon:.0f} đòn hạ" if sodon else ""))


if __name__ == "__main__":
    main()
