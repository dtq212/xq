import os
import random
import re
import threading
import time

from hangso_xq import *
from tactu_muctieu_xq import _demsao, _duongdanlogepda, _ghilogepda, _docthatbailientiep

# Ép Đoạn Thạch từ hộp thoại tab Khác (giaodienhienthi_xq._mohopepda), thay cho Ctrl+Y (chỉ ép món ô 0 lên 6 sao).
# Lệnh "mix3 0# <id đồ># <id đá>#": đá theo sao hiện tại 0-1 Sơ Cấp, 2-3 Trung Cấp, 4-5 Cao Cấp; 1->4 sao 100%, 4->5 ~71%, 5->6 ~41%
# (người dùng 2026-10-31). Kết quả do máy chủ quay nên chỉ gửi từng lần rồi đọc lại sao.
SAOTOIDA = 6
# Loại trang bị (chữ trong cặp ［］ đầu mô tả, như sosanhbuild_xq.LOAITRANGBIs) mới hiện trong danh sách chọn ép
# Pháp Bảo không ép Đoạn Thạch được (người dùng 2026-11-19)
LOAITRANGBIEPDAs = {"Vũ Khí", "Nón", "Y Phục", "Yêu Đới", "Hạng Liên", "Giày"}
# Sau mix3: chờ đá trong túi giảm (máy chủ đã nhận) tối đa bấy nhiêu giây, rồi desc lại đọc sao. Ctrl+Y cũ gửi cách 0.25s vẫn chạy
THOIGIANCHOKETQUAEPDA = 3.
GIANCACHEPDA = 0.3
# % thành công theo sao hiện tại (người dùng cho biết): 4->5 71%, 5->6 41%, dưới 4★ 100%. Bot quay số theo đúng tỉ lệ này, trúng mới
# gửi lệnh ép (_luongepda_ep); trượt thì chờ bấy nhiêu giây rồi quay lại
TILETHANHCONGEPDA = {4: 71., 5: 41.}
GIANCACHQUAYEPDA = 0.05
# Danh sách món: desc cả lượt không chờ, đợi bấy nhiêu giây rồi đọc mô tả đã nạp
THOIGIANCHOMOTAEPDA = 1.5


def _soquayepda(khe):
    # Số 0-100 của khe thời gian (int(giây / GIANCACHQUAYEPDA)): như nhau ở mọi tiến trình bot cùng máy
    return random.Random(khe).random() * 100.


# Ép lần lượt giữa các nhân vật cùng máy (người dùng 2026-11-19: Ngốc lên 6★ mà Thỏ / Kng vẫn ép cùng lúc nên xịt cả 2): các bot cùng
# mã nhóm (hộp thoại tạo mỗi lần bấm Ép) dùng file trong _internal/epda: "<mã>.khoa" tạo kiểu O_EXCL = đang có người ép (người khác
# chờ), "<mã>.dat" = đã có món đạt sao đích, cả nhóm dừng. Khoá quá THOIGIANKHOACU giây coi như bỏ dở (bot tắt giữa chừng), xoá đi
THOIGIANKHOACU = 15.
# Vừa ép xong thì nhường các khe trúng trong bấy nhiêu giây cho nhân vật khác đang chờ (xoay vòng giữa các nhân vật)
GIANCACHNHUONGEPDA = 0.3


def _taonhomepda(manhom):
    thumuc = os.path.dirname(_duongdanlogepda(0))
    # Dọn file nhóm cũ hơn 1 ngày
    try:
        for ten in os.listdir(thumuc):
            duongdan = os.path.join(thumuc, ten)
            if ten.endswith((".khoa", ".dat")) and time.time() - os.path.getmtime(duongdan) > 86400:
                os.remove(duongdan)
    except OSError:
        pass
    manhom = re.sub(r"[^0-9A-Za-z_]", "", str(manhom)) or "macdinh"
    return {"khoa": os.path.join(thumuc, f"nhom_{manhom}.khoa"), "dat": os.path.join(thumuc, f"nhom_{manhom}.dat"), "lucnha": 0.,
            "is_giu": False}


def _giukhoaepda(nhom):
    try:
        fd = os.open(nhom["khoa"], os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        nhom["is_giu"] = True
        return True
    except FileExistsError:
        try:
            if time.time() - os.path.getmtime(nhom["khoa"]) > THOIGIANKHOACU:
                os.remove(nhom["khoa"])
        except OSError:
            pass
    except OSError:
        pass
    return False


def _nhakhoaepda(nhom):
    if not nhom.get("is_giu"):
        return
    nhom["is_giu"] = False
    nhom["lucnha"] = time.time()
    try:
        os.remove(nhom["khoa"])
    except OSError:
        pass


def _ghifileepda(duongdan, noidung):
    try:
        with open(duongdan, "w", encoding = "utf-8") as f:
            f.write(noidung)
    except OSError:
        pass


def _docfileepda(duongdan):
    try:
        with open(duongdan, encoding = "utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def _daepchosao(sao):
    return CAOCAPDOANTHACH if sao >= 4 else TRUNGCAPDOANTHACH if sao >= 2 else SOCAPDOANTHACH


def _loaitrongmota(mota):
    # Chữ trong cặp [] / ［］ đầu tiên sau dòng tên ("" nếu không có)
    dongs = [dong.strip() for dong in (mota or "").split("\n") if dong.strip()]
    khop = re.search(r"[\[［]\s*([^\]］\n]*?)\s*[\]］]", "\n".join(dongs[1:]))
    return khop.group(1) if khop else ""


class TacTuEpDa:
    def get_trangthaiepda(self):
        return self._trangthaiepda

    def get_is_dangepda(self):
        return bool(self._luongepda and self._luongepda.is_alive())

    def get_dsepda(self):
        return self._dsepda

    def _demdaepda(self):
        # {tên đá: tổng số lượng trong hành trang}
        moitruong = self.moitruong
        soluongs = {SOCAPDOANTHACH: 0, TRUNGCAPDOANTHACH: 0, CAOCAPDOANTHACH: 0}
        for vitri, ten in enumerate(moitruong.get_danhsachtenvatphamhanhtrang() or []):
            if ten in soluongs:
                soluongs[ten] += max(1, moitruong.get_soluongvatphamhanhtrang(vitri) or 1)
        return soluongs

    def _chayluongepda(self, ham, *thamso):
        if self.get_is_dangepda():
            return False
        self._is_dungepda = False
        self._luongepda = threading.Thread(target = ham, args = thamso, daemon = True)
        self._luongepda.start()
        return True

    def lay_dsepda(self):
        # Lệnh "epda_ds": đọc các món trang bị trong hành trang kèm số sao để hộp thoại hiện (shared_data "_dsepda")
        self._chayluongepda(self._luongdsepda)

    def _luongdsepda(self):
        moitruong = self.moitruong
        self._trangthaiepda = "Đang đọc hành trang..."
        try:
            vitris = []
            for vitri in range(moitruong.get_soluongvatphamhanhtrangtoida() + 1):
                iddoituong = moitruong.get_iddoituongvatphamhanhtrang(vitri)
                if iddoituong and iddoituong > 0 and moitruong.get_tenvatphamhanhtrang(vitri):
                    moitruong.truyvan_motavatphamhanhtrang(vitri, is_cho = False)
                    vitris.append((vitri, iddoituong))
                    time.sleep(0.03)
            time.sleep(THOIGIANCHOMOTAEPDA)
            mons = []
            for vitri, iddoituong in vitris:
                if moitruong.get_iddoituongvatphamhanhtrang(vitri) != iddoituong:
                    continue
                mota = moitruong.get_motavatphamhanhtrangcosan(vitri)
                if not mota:
                    mota = moitruong.get_motavatphamhanhtrang(vitri) or ""
                if _loaitrongmota(mota) not in LOAITRANGBIEPDAs:
                    continue
                ten = re.sub(r"\x1b.", "", moitruong.get_tenvatphamhanhtrang(vitri) or "").strip()
                mons.append({"vitri": vitri, "id": iddoituong, "ten": ten, "sao": _demsao(mota)})
            self._dsepda = {"luc": time.time(), "mons": mons, "da": self._demdaepda()}
            self._trangthaiepda = f"Tìm thấy {len(mons)} món trang bị"
        except Exception as err:
            self._trangthaiepda = f"Lỗi đọc hành trang: {err}"
            moitruong._inlog(f"[ÉP ĐÁ] Lỗi đọc hành trang: {err}")

    def batdau_epda(self, saodich, is_lanluot, manhom, mons, is_giu5sao = False):
        # Lệnh "epda:<sao đích>:<1 = lần lượt>:<mã nhóm>:<ô>,<id>;<ô>,<id>...": ép xoay vòng các món đã chọn tới sao đích.
        # is_lanluot: các nhân vật cùng mã nhóm ép lần lượt (mỗi lúc 1 người), 1 món đạt sao đích là cả nhóm dừng
        saodich = max(1, min(SAOTOIDA, int(saodich)))
        mons = [(int(vitri), int(iddoituong)) for vitri, iddoituong in mons]
        if not mons:
            return
        nhom = _taonhomepda(manhom) if is_lanluot else None
        if not self._chayluongepda(self._luongepda_ep, mons, saodich, nhom, bool(is_giu5sao)):
            self._trangthaiepda = "Đang bận việc trước, bấm Dừng rồi thử lại"

    def dung_epda(self):
        self._is_dungepda = True

    def _chothoidiemepda(self, mon, sao, tile, nhom):
        # Chờ khe số quay chung trúng (< tile); chế độ lần lượt thì còn phải giữ được khoá nhóm. Trả về số lần quay, None = thôi
        # (bấm dừng / nhân vật khác trong nhóm đã đạt)
        solanquay = 0
        khetruoc = None
        while not self._is_dungepda:
            if nhom and os.path.exists(nhom["dat"]):
                return None
            khe = int(time.time() / GIANCACHQUAYEPDA)
            if khe == khetruoc:
                time.sleep(max(0.005, (khe + 1) * GIANCACHQUAYEPDA - time.time()))
                continue
            khetruoc = khe
            solanquay += 1
            so = _soquayepda(khe)
            if so < tile:
                # Vừa ép xong thì nhường các khe trúng trong GIANCACHNHUONGEPDA giây cho nhân vật khác đang chờ
                if not nhom or (time.time() - nhom["lucnha"] >= GIANCACHNHUONGEPDA and _giukhoaepda(nhom)):
                    return solanquay
                if solanquay % 10 == 1:
                    self._trangthaiepda = f"{mon['ten']} (ô {mon['vitri'] + 1}): {sao}★, khe trúng nhưng nhân vật khác đang ép -> chờ lượt"
                continue
            if solanquay % 10 == 1:
                self._trangthaiepda = f"{mon['ten']} (ô {mon['vitri'] + 1}): {sao}★, quay {so:.1f} ≥ {tile:g}% -> chờ (lần quay {solanquay})"
        return None

    def _ep1lanepda(self, mon, saodich, duongdanlog, nhom, is_giu5sao = False):
        # Ép món 1 lần (quay số trúng mới gửi). Trả về "" nếu còn ép tiếp được, không thì lý do món này thôi (ghi vào mon["xong"])
        moitruong = self.moitruong
        vitri, iddoituong, ten = mon["vitri"], mon["id"], mon["ten"]
        if moitruong.get_iddoituongvatphamhanhtrang(vitri) != iddoituong:
            return "không còn ở ô cũ"
        mota = moitruong.get_motavatphamhanhtrang(vitri, thoigianchotoida = 2., is_napmoi = True)
        if not mota:
            return "không đọc được mô tả"
        sao = _demsao(mota)
        mon["sao"] = sao
        if sao >= saodich:
            return f"đạt {sao}★"
        tenda = _daepchosao(sao)
        if self._demdaepda()[tenda] <= 0 or not moitruong.action_timkiemvatphamhanhtrang(tenda):
            return f"hết {tenda}"
        # Giữ 5★ (người dùng 2026-11-19): món 5★ mà chỉ còn 1 Cao Cấp thì không ép 5->6 (41%, hỏng về 0★), giữ món 5★
        if is_giu5sao and sao == 5 and self._demdaepda()[CAOCAPDOANTHACH] <= 1:
            return f"giữ 5★ (chỉ còn {self._demdaepda()[CAOCAPDOANTHACH]} Cao Cấp)"
        # Chọn thời điểm ép như máy chủ quay (người dùng 2026-11-18, "tâm linh"): số quay chung mọi nhân vật theo khe đồng hồ máy
        # (_soquayepda), nhỏ hơn % thành công của cấp này mới gửi lệnh ép. 1->4★ 100% nên ép luôn
        tile = TILETHANHCONGEPDA.get(sao, 100.)
        solanquay = self._chothoidiemepda(mon, sao, tile, nhom)
        if solanquay is None:
            return ""
        try:
            # Đọc lại đá sau lúc chờ (có thể chờ lâu ở chế độ lần lượt)
            soda = self._demdaepda()
            iddoanthach = moitruong.action_timkiemvatphamhanhtrang(tenda) if soda[tenda] > 0 else 0
            if not iddoanthach:
                return f"hết {tenda}"
            self._trangthaiepda = f"{ten} (ô {vitri + 1}): {sao}★ -> {sao + 1}★, quay {solanquay} lần mới trúng (còn {soda[tenda]} {tenda})"
            moitruong.action_thucthicaulenh("mix3 0# {}# {}#".format(hex(iddoituong), hex(iddoanthach)).replace("0x", ""))
            mon["solan"] += 1
            # Chờ đá giảm = máy chủ đã xử lý; không giảm thì lệnh không được nhận (đồ khoá, không ép được...) -> thôi món này
            hetgio = time.time() + THOIGIANCHOKETQUAEPDA
            while time.time() < hetgio and self._demdaepda()[tenda] >= soda[tenda]:
                time.sleep(0.1)
            if self._demdaepda()[tenda] >= soda[tenda]:
                return "máy chủ không nhận lệnh ép (đá không giảm)"
            motasau = moitruong.get_motavatphamhanhtrang(vitri, thoigianchotoida = 2., is_napmoi = True) or ""
            saosau = _demsao(motasau) if motasau else sao
            mon["sao"] = saosau
            thanhcong = saosau > sao
            mon["thanhcong"] += thanhcong
            moitruong._inlog(f"[ÉP ĐÁ] {ten} (ô {vitri + 1}): {sao}★ -> {saosau}★ {'thành công' if thanhcong else 'thất bại'} (quay {solanquay} lần mới ép)")
            # Log đo tỉ lệ (xem _docthatbailientiep): chỉ ghi lần ép từ 4 sao, 1->4 luôn thành công
            if sao >= 4:
                thatbaitheocap, thatbaichung = _docthatbailientiep(duongdanlog)
                _ghilogepda(duongdanlog, {"luc": time.strftime("%Y-%m-%d %H:%M:%S"), "ten": ten, "saotruoc": sao, "saosau": saosau,
                                          "thanhcong": thanhcong, "thatbaitruoccap": thatbaitheocap.get(sao, 0),
                                          "thatbaitruocchung": thatbaichung, "nguon": "hopthoai", "solanquay": solanquay,
                                          "chedo": "lanluot" if nhom else "dongloat"})
            if saosau >= saodich:
                if nhom:
                    # Báo cả nhóm dừng: tạo file "đạt" trước khi nhả khoá để người kế không kịp ép
                    _ghifileepda(nhom["dat"], f"{moitruong.get_idnguoichoi()} {ten} {saosau}")
                return f"đạt {saosau}★"
            return ""
        finally:
            if nhom:
                _nhakhoaepda(nhom)

    def _luongepda_ep(self, dsmon, saodich, nhom, is_giu5sao = False):
        # Ép hàng loạt (người dùng 2026-11-19): leo từng món lên 4★ rồi xoay vòng các bước rủi ro ("xịt cái này thì hoạ may cái khác
        # lên"), món đạt sao / hết đá cấp của nó / lỗi thì bỏ khỏi vòng.
        # nhom (chế độ lần lượt): mỗi khe trúng chỉ 1 nhân vật trong nhóm ép (khoá file), chờ kết quả rồi mới tới khe trúng kế; 1 món
        # đạt sao đích là cả nhóm dừng. Đồng loạt (nhom None) thì mọi nhân vật ép cùng khe, không dừng được nhau (lệnh đã gửi cùng lúc)
        moitruong = self.moitruong
        duongdanlog = _duongdanlogepda(moitruong.get_idnguoichoi())
        mons = [{"vitri": vitri, "id": iddoituong, "ten": re.sub(r"\x1b.", "", moitruong.get_tenvatphamhanhtrang(vitri) or "").strip(),
                 "sao": None, "solan": 0, "thanhcong": 0, "xong": ""} for vitri, iddoituong in dsmon]
        lydo = ""
        try:
            # Sao ban đầu từng món để chọn thứ tự ép
            for mon in mons:
                if moitruong.get_iddoituongvatphamhanhtrang(mon["vitri"]) != mon["id"]:
                    mon["xong"] = "không còn ở ô cũ"
                    continue
                mota = moitruong.get_motavatphamhanhtrang(mon["vitri"], thoigianchotoida = 2., is_napmoi = True)
                mon["sao"] = _demsao(mota) if mota else None
            # Thứ tự ép (người dùng 2026-11-19): xoay vòng đều mỗi món 1 lần làm phí Trung Cấp (2 món cùng 2★ còn 2 Trung -> mỗi món
            # 1 viên, cả 2 kẹt 3★, không món nào tới bước thử 4->5; mô phỏng 9 Sơ / 6 Trung / 6 Cao: ép 2 món chỉ 43,7% có 6★, 1 món
            # 53,9%). Giờ: có món >= 4★ thì xoay vòng các món đó (bước rủi ro, xịt món này thì sang món kia); không có thì dồn đá
            # leo hẳn 1 món (món nhiều sao nhất) lên 4★ rồi mới tính tiếp
            iruirocuoi = -1
            while not lydo:
                if self._is_dungepda:
                    lydo = "bấm dừng"
                    break
                if nhom and os.path.exists(nhom["dat"]):
                    lydo = f"cả nhóm dừng: {_docfileepda(nhom['dat'])}★ đã đạt"
                    break
                conlais = [i for i, mon in enumerate(mons) if not mon["xong"]]
                if not conlais:
                    # Mọi món đều đạt thì ghi "xong" (trước đây ghi "hết món để ép" cả khi lên 6★ thành công, người dùng 2026-11-19)
                    lydo = f"xong, đạt {saodich}★" if all(mon["xong"].startswith("đạt") for mon in mons) else "hết món để ép"
                    break
                ruiros = [i for i in conlais if (mons[i]["sao"] or 0) >= 4]
                if ruiros:
                    i = next((i for i in ruiros if i > iruirocuoi), ruiros[0])
                    iruirocuoi = i
                else:
                    i = max(conlais, key = lambda i: (mons[i]["sao"] or 0, -i))
                mon = mons[i]
                mon["xong"] = self._ep1lanepda(mon, saodich, duongdanlog, nhom, is_giu5sao)
                if nhom and mon["xong"].startswith("đạt") and mon["solan"]:
                    lydo = f"{mon['ten']} (ô {mon['vitri'] + 1}) đã {mon['xong']}, cả nhóm dừng"
                    break
                time.sleep(GIANCACHEPDA)
        except Exception as err:
            lydo = f"lỗi: {err}"
        tong = sum(mon["solan"] for mon in mons)
        chitiet = "; ".join(f"ô {mon['vitri'] + 1} {mon['ten']}: {mon['sao'] if mon['sao'] is not None else '?'}★"
                            f"{' (' + mon['xong'] + ')' if mon['xong'] and not mon['xong'].startswith('đạt') else ''}" for mon in mons)
        self._trangthaiepda = (f"Dừng ({lydo}) sau {tong} lần ép, {sum(mon['thanhcong'] for mon in mons)} lần lên sao "
                               f"({time.strftime('%H:%M')})\n{chitiet}")
        moitruong._inlog(f"[ÉP ĐÁ] {self._trangthaiepda}")
        # Cập nhật sao mới và số đá còn cho hộp thoại
        try:
            if self._dsepda:
                saomoi = {(mon["vitri"], mon["id"]): mon["sao"] for mon in mons if mon["sao"] is not None}
                for m in self._dsepda.get("mons", []):
                    if (m["vitri"], m["id"]) in saomoi:
                        m["sao"] = saomoi[(m["vitri"], m["id"])]
                self._dsepda = dict(self._dsepda, luc = time.time(), da = self._demdaepda())
        except Exception:
            pass
