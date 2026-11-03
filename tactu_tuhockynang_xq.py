# Chế độ kỹ năng Tự học: học từ số bay trên đầu quái chiêu nào ra bao nhiêu sát thương TRONG TRẠNG THÁI NÀO (hiệu ứng trên quái, buff trên
# mình), chiêu nào gây hiệu ứng gì, ra chiêu mất bao lâu, ăn / hồi bao nhiêu nguyên khí; rồi mỗi lượt lập kế hoạch chuỗi chiêu cho
# THOIGIANKEHOACHTUHOC giây tới cho tổng sát thương lớn nhất, đánh chiêu đầu chuỗi, lượt sau tính lại theo trạng thái mới.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
# Chế độ Luật cố định (mặc định) dùng nguyên danh sách ưu tiên viết tay của từng môn phái trong tactu_kynang_xq.py. Chế độ Tự học dùng
# chính danh sách đó (điều kiện dùng được, tầm, vật cản, giữ nguyên khí... vẫn của luật viết tay), chỉ đổi thứ tự các chiêu đánh mục
# tiêu (_sapxepuutientuhoc) => luật viết tay không mất, đổi lại chế độ là về như cũ. Đo chạy ở cả hai chế độ.
# Chỉ học / lập kế hoạch với quái (không phải người chơi, không ở chiến trường)
import json
import math
import os
import time

import numpy as np

from hangso_xq import *
from tienich_xq import thaythefile, _thumucthietlap

# Tên hiệu ứng cho giao diện khi game không có tên: {id hiệu ứng: tên hằng HIEUUNGKYNANG_*}
_TENHIEUUNG_MAP = {}
for _ten, _giatri in list(globals().items()):
    if _ten.startswith("HIEUUNGKYNANG_") and isinstance(_giatri, int):
        _TENHIEUUNG_MAP.setdefault(_giatri, _ten[len("HIEUUNGKYNANG_"):].replace("_", " ").title())


class TacTuTuHocKyNang:
    def thietlap_chedokynang(self, chedo):
        self._chedokynang = CHEDOKYNANG_TUHOC if chedo == CHEDOKYNANG_TUHOC else CHEDOKYNANG_CODINH

    # ------------------------------------------------------------------ lưu / nạp

    def _duongdantuhoc(self, idnguoichoi):
        return os.path.join(os.path.dirname(_thumucthietlap()), "tuhockynang", f"{idnguoichoi}.json")

    def _taituhoc(self):
        # Số liệu theo ID người chơi (ID cố định, tên đổi được):
        #  "maus": mỗi chiêu đã đo [id chiêu, tên quái, sát thương, thời gian ra chiêu, [hiệu ứng trên quái lúc gửi], [hiệu ứng trên mình],
        #          [hiệu ứng mới trên quái sau chiêu], nguyên khí đổi, thời điểm] (giữ SOMAUTOIDATUHOC mẫu gần nhất)
        #  "thoigianhieuung": {id hiệu ứng: [số lần, tổng giây tồn tại trên quái]}
        #  "tran": {tên quái: {chế độ: [tổng sát thương, tổng giây đánh, số con]}}
        # Bản cũ (chưa có trạng thái) bỏ, học lại từ đầu
        idnguoichoi = self.moitruong.get_idnguoichoi()
        if not idnguoichoi:
            return None
        if self._idnguoichoituhoc == idnguoichoi:
            return self._dulieutuhoc
        self._luutuhoc(is_batbuoc = True)
        try:
            with open(self._duongdantuhoc(idnguoichoi), "r", encoding = "utf-8") as file:
                dulieu = json.load(file)
        except FileNotFoundError:
            dulieu = {}
        except Exception as err:
            print(err)
            dulieu = {}
        if dulieu.get("phienban") != PHIENBANTUHOC:
            dulieu = {"phienban": PHIENBANTUHOC, "maus": [], "thoigianhieuung": {}, "tran": {}}
        self._idnguoichoituhoc = idnguoichoi
        self._dulieutuhoc = dulieu
        self._is_tuhocthaydoi = False
        self._mohinhtuhoc = None
        self._somaumoituhoc = len(dulieu["maus"])
        return dulieu

    def _luutuhoc(self, is_batbuoc = False):
        if not self._is_tuhocthaydoi or not self._idnguoichoituhoc:
            return
        if not is_batbuoc and time.time() - self._thoidiemluutuhoc < THOIGIANLUUTUHOC:
            return
        self._thoidiemluutuhoc = time.time()
        filepath = self._duongdantuhoc(self._idnguoichoituhoc)
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok = True)
            filetam = filepath + ".tmp"
            with open(filetam, "w", encoding = "utf-8") as file:
                json.dump(self._dulieutuhoc, file, ensure_ascii = False, separators = (",", ":"))
            thaythefile(filetam, filepath)
            self._is_tuhocthaydoi = False
        except Exception as err:
            print(err)

    # ------------------------------------------------------------------ đo

    def _idhieuungs(self, diachi = None):
        try:
            return sorted({hieuung[0] for hieuung in self.moitruong.get_danhsachhieuungnhanvats(diachi) if hieuung[0] > 0})
        except Exception:
            return []

    def _is_muctieuhoplehoc(self, diachimuctieu):
        # Client chỉ hiện số bay do chính nhân vật mình đánh ra (dò 2026-11-03: cùng con quái, mỗi client thấy số khác nhau, đúng cỡ
        # sát thương môn phái của nó) => đánh nhóm vẫn đo được. Chỉ bỏ người chơi / chiến trường (luật riêng, kháng khác quái)
        moitruong = self.moitruong
        return bool(diachimuctieu) and not moitruong.get_is_nguoichoi(diachimuctieu) and moitruong.get_idbandohientai() != BANDO_CHIENTRUONG

    def _ghichieututhoc(self, vitrikynang, diachimuctieu, is_sansanglucgui = True):
        # Vừa gửi chiêu đánh mục tiêu (action_xulyuutiensudungkynang): mở cửa sổ chờ số bay cho chiêu này, chụp trạng thái lúc gửi.
        # is_sansanglucgui: chiêu sẵn sàng ngay trước khi gửi (đọc trước lệnh gửi)
        moitruong = self.moitruong
        if not diachimuctieu:
            return
        thoidiemhientai = time.time()
        idmuctieu = moitruong.get_iddoituong(diachimuctieu)
        danhsach = self._chieuchotuhoc
        if danhsach and danhsach[-1]["idmuctieu"] != idmuctieu:
            # Đổi mục tiêu: chốt hết chiêu cũ (số bay đang theo dõi là của mục tiêu cũ)
            while danhsach:
                self._chotchieututhoc(danhsach.pop(0))
        for chieu in danhsach:
            self._chuphieuungsautuhoc(chieu)
        if danhsach and not danhsach[-1]["is_danhan"]:
            # Bot gửi lại chiêu tới khi máy chủ nhận (mỗi lượt ~0.1s): lần gửi trước chưa được nhận thì bỏ, chỉ giữ lần gửi mới nhất
            danhsach.pop()
        is_hople = self._is_muctieuhoplehoc(diachimuctieu)
        danhsach.append({
            "vitri": vitrikynang, "idkynang": moitruong.get_idkynang(vitrikynang), "diachi": diachimuctieu, "idmuctieu": idmuctieu,
            "tenquai": moitruong.get_tendoituong(diachimuctieu), "thoidiem": thoidiemhientai, "satthuongs": [],
            "is_danhan": False, "is_xuatchieulucgui": moitruong.get_idtuthenhanvat() in TUTHEXUATCHIEUTUHOCs,
            "is_sansanglucgui": is_sansanglucgui,
            "is_dathayxuatchieu": False, "thoigiankhoa": None, "is_hople": is_hople,
            "hieuungmuctieu": self._idhieuungs(diachimuctieu) if is_hople else [], "hieuungminh": self._idhieuungs() if is_hople else [],
            "nguyenkhi": moitruong.get_nguyenkhiconlai() or 0, "hieuungsau": None,
        })

    def _chuphieuungsautuhoc(self, chieu):
        # Hiệu ứng mới trên quái sau chiêu (so với lúc gửi), chụp 1 lần: chiêu đã nhận và còn đúng con đó
        if chieu["hieuungsau"] is not None or not chieu["is_danhan"] or not chieu["is_hople"]:
            return
        if self.moitruong.get_iddoituong(chieu["diachi"]) != chieu["idmuctieu"]:
            chieu["hieuungsau"] = []
            return
        chieu["hieuungsau"] = sorted(set(self._idhieuungs(chieu["diachi"])) - set(chieu["hieuungmuctieu"]))

    def _is_chieudanhan(self, chieu):
        # Máy chủ đã nhận chiêu: kỹ năng đang sẵn sàng lúc gửi rồi vào hồi chiêu, hoặc nhân vật chuyển sang tư thế xuất chiêu sau lúc gửi
        # (lúc gửi chưa ở tư thế đó, tránh nhận nhầm tư thế của chiêu trước). Lúc gửi chiêu còn đang hồi (lệnh xếp hàng gửi lại, log 9176
        # 2026-11-03: "pf 2711" vào hàng đợi 3 lần, lần đầu lúc Phục Ma còn hồi từ lần trước) thì máy chủ không nhận lần đó
        moitruong = self.moitruong
        if not chieu["is_sansanglucgui"]:
            return False
        if not moitruong.get_is_kynangsansang(chieu["vitri"]):
            return True
        return not chieu["is_xuatchieulucgui"] and moitruong.get_idtuthenhanvat() in TUTHEXUATCHIEUTUHOCs

    def _capnhattuhockynang(self):
        # Mỗi lượt (gọi đầu action_tudongsudungkynang): đọc số bay mới trên mục tiêu (cộng vào trận đang đánh, tính cho chiêu đã nhận), theo
        # dõi hiệu ứng trên mục tiêu (thời gian tồn tại), chiêu đã gửi được nhận chưa, thời gian ra chiêu, chốt chiêu hết cửa sổ; học lại
        # mô hình định kỳ, lưu, log
        moitruong = self.moitruong
        thoidiemhientai = time.time()
        danhsach = self._chieuchotuhoc
        diachimuctieu = moitruong.get_diachicosothongtinnhanvatmuctieudangchon()
        idmuctieu = moitruong.get_iddoituong(diachimuctieu) if diachimuctieu else 0
        if danhsach and danhsach[-1]["idmuctieu"] != idmuctieu:
            # Đổi / mất mục tiêu: số bay đang theo dõi không còn là của các chiêu này
            while danhsach:
                self._chotchieututhoc(danhsach.pop(0))
        if diachimuctieu and self._is_muctieuhoplehoc(diachimuctieu):
            self._theodoihieuungtuhoc(diachimuctieu, idmuctieu, thoidiemhientai)
            sobaymois = self._docsobaymoituhoc(diachimuctieu, idmuctieu)
            if sobaymois:
                self._congtrantuhoc(diachimuctieu, idmuctieu, sum(sobaymois), thoidiemhientai)
        else:
            sobaymois = []
            self._chottrantuhoc()
        if danhsach:
            moinhat = danhsach[-1]
            if not moinhat["is_danhan"] and self._is_chieudanhan(moinhat):
                moinhat["is_danhan"] = True
                if moinhat["idkynang"]:
                    self._thoidiemnhantuhoc[moinhat["idkynang"]] = moinhat["thoidiem"]
                truoc = danhsach[-2] if len(danhsach) > 1 else None
                if truoc and truoc["thoigiankhoa"] is None:
                    # Chiêu kế được nhận khi chiêu trước chưa hết tư thế xuất chiêu: chiêu trước chiếm tới lúc gửi chiêu kế
                    truoc["thoigiankhoa"] = moinhat["thoidiem"] - truoc["thoidiem"]
            # Số bay mới tính cho chiêu đã nhận gần nhất đã gửi cách ít nhất THOIGIANTRESOBAYTUHOC giây (máy chủ trả chậm: số hiện ngay sau
            # khi gửi chiêu kế vẫn là của chiêu trước); chưa có chiêu nào được nhận thì số đó là đòn thường, bỏ. Đòn thường "kill" lẫn vào
            # mọi chiêu theo thời gian => cộng gần như cùng một lượng cho mọi chiêu
            for chieu in danhsach:
                if thoidiemhientai - chieu["thoidiem"] >= THOIGIANDOHIEUUNGMOITUHOC:
                    self._chuphieuungsautuhoc(chieu)
            danhans = [c for c in danhsach if c["is_danhan"]]
            for so in sobaymois:
                if danhans:
                    chieu = next((c for c in reversed(danhans) if thoidiemhientai - c["thoidiem"] >= THOIGIANTRESOBAYTUHOC), danhans[0])
                    chieu["satthuongs"].append(so)
            if moinhat["is_danhan"]:
                if moitruong.get_idtuthenhanvat() in TUTHEXUATCHIEUTUHOCs:
                    moinhat["is_dathayxuatchieu"] = True
                elif moinhat["is_dathayxuatchieu"] and moinhat["thoigiankhoa"] is None:
                    moinhat["thoigiankhoa"] = thoidiemhientai - moinhat["thoidiem"]
            # Chốt: hết cửa sổ, hoặc chiêu đã nhận kế tiếp đã gửi quá THOIGIANTRESOBAYTUHOC (số mới thuộc về chiêu đó)
            while danhsach and (thoidiemhientai - danhsach[0]["thoidiem"] > THOIGIANCUASOSOBAYTUHOC
                                or any(c["is_danhan"] and thoidiemhientai - c["thoidiem"] > THOIGIANTRESOBAYTUHOC for c in danhsach[1:])):
                self._chotchieututhoc(danhsach.pop(0))
        nguyenkhi = moitruong.get_nguyenkhiconlai() or 0
        self._nguyenkhitoidatuhoc = max(self._nguyenkhitoidatuhoc, nguyenkhi)
        self._hoctuhoc(thoidiemhientai)
        self._luutuhoc()
        self._logtuhoc()

    def _docsobaymoituhoc(self, diachimuctieu, idmuctieu):
        # Số bay mất máu mới trên mục tiêu so với lần đọc trước (ô đổi số hoặc bộ đếm chạy lại); đổi mục tiêu thì chỉ ghi mốc
        sobay = self.moitruong._docsobaydoituong(diachimuctieu)
        if not sobay:
            return []
        cu = self._sobaytuhoc
        self._sobaytuhoc = (idmuctieu, sobay)
        if not cu or cu[0] != idmuctieu:
            return []
        (giatricu, demcu), (giatri, dem) = cu[1], sobay
        return [giatri[i] for i in range(10) if giatri[i] > 0 and (giatri[i] != giatricu[i] or dem[i] < demcu[i])]

    def _theodoihieuungtuhoc(self, diachimuctieu, idmuctieu, thoidiemhientai):
        # Hiệu ứng trên quái không có thời gian còn lại (client chỉ ghi 1): ghi lúc xuất hiện, lúc mất thì cộng thời gian tồn tại vào
        # "thoigianhieuung". Hiệu ứng đã có khi bắt đầu theo dõi (không biết lúc xuất hiện) thì không tính
        if thoidiemhientai - self._thoidiemdochieuungtuhoc < 0.2:
            return
        self._thoidiemdochieuungtuhoc = thoidiemhientai
        hieuungs = set(self._idhieuungs(diachimuctieu))
        theodoi = self._hieuungtheodoituhoc
        if not theodoi or theodoi["id"] != idmuctieu:
            self._hieuungtheodoituhoc = {"id": idmuctieu, "dau": {e: None for e in hieuungs}}
            return
        dau = theodoi["dau"]
        for e in hieuungs - dau.keys():
            dau[e] = thoidiemhientai
        for e in list(dau.keys() - hieuungs):
            batdau = dau.pop(e)
            if batdau is not None and self.moitruong.get_iddoituong(diachimuctieu) == idmuctieu:
                dulieu = self._taituhoc()
                if dulieu is not None:
                    dem = dulieu["thoigianhieuung"].setdefault(str(e), [0., 0.])
                    dem[0] += 1.
                    dem[1] += thoidiemhientai - batdau
                    if dem[0] > 50.:
                        dem[:] = [dem[0] * 50. / dem[0], dem[1] * 50. / dem[0]]
                    self._is_tuhocthaydoi = True

    def _thoigianhieuungtuhoc(self, e):
        dem = (self._dulieutuhoc.get("thoigianhieuung") or {}).get(str(e)) if self._idnguoichoituhoc else None
        return dem[1] / dem[0] if dem and dem[0] else THOIGIANHIEUUNGMACDINHTUHOC

    def _congtrantuhoc(self, diachimuctieu, idmuctieu, satthuong, thoidiemhientai):
        # Sát thương / giây cả trận: cộng mọi số bay của mình trên 1 con quái (cả đòn thường), từ số đầu tới số cuối. Đổi con thì chốt con cũ
        tran = self._trantuhoc
        if tran and tran["id"] != idmuctieu:
            self._chottrantuhoc()
            tran = None
        if not tran:
            self._trantuhoc = tran = {"id": idmuctieu, "tenquai": self.moitruong.get_tendoituong(diachimuctieu), "dau": thoidiemhientai,
                                      "cuoi": thoidiemhientai, "tong": 0., "chedo": self._chedokynang}
        tran["tong"] += satthuong
        tran["cuoi"] = thoidiemhientai

    def _chottrantuhoc(self):
        tran = self._trantuhoc
        self._trantuhoc = None
        if not tran or not tran["tenquai"]:
            return
        # Thời gian từ số đầu tới số cuối + 1 nhịp ra chiêu (số đầu đã là kết quả của 1 đòn)
        thoigian = tran["cuoi"] - tran["dau"] + THOIGIANKHOAMACDINHTUHOC
        dulieu = self._taituhoc()
        if dulieu is None or thoigian < THOIGIANTRANTOITHIEUTUHOC:
            return
        dem = dulieu["tran"].setdefault(tran["tenquai"], {}).setdefault(tran["chedo"], [0., 0., 0.])
        dem[0] += tran["tong"]
        dem[1] += thoigian
        dem[2] += 1.
        if dem[2] > SOTRANTOIDATUHOC:
            dem[:] = [giatri * SOTRANTOIDATUHOC / dem[2] for giatri in dem]
        self._is_tuhocthaydoi = True

    def _chotchieututhoc(self, chieu):
        # Chiêu máy chủ không nhận: bỏ lặng lẽ (lần gửi lại đã thay nó). Chiêu đã nhận mà không thấy số bay nào (né / bị chặn) thì bỏ,
        # không tính 0
        if not chieu["is_danhan"]:
            return
        if not chieu["is_hople"] or not chieu["satthuongs"] or not chieu["idkynang"] or not chieu["tenquai"]:
            if IS_LOGTUHOC:
                lydo = "người chơi / chiến trường" if not chieu["is_hople"] else \
                    ("không thấy số bay" if not chieu["satthuongs"] else "không đọc được id chiêu / tên quái")
                self.moitruong._inlog(f"[TỰ HỌC CHIÊU] bỏ {self._tenchieututhoc(chieu['vitri'])} -> {chieu['tenquai']}: {lydo}")
            return
        dulieu = self._taituhoc()
        if dulieu is None:
            return
        moitruong = self.moitruong
        thoigiankhoa = chieu["thoigiankhoa"] if chieu["thoigiankhoa"] is not None else THOIGIANKHOAMACDINHTUHOC
        thoigiankhoa = min(THOIGIANCUASOSOBAYTUHOC, max(THOIGIANKHOATOITHIEUTUHOC, thoigiankhoa))
        # Hiệu ứng mới trên quái do chiêu gây ra (_chuphieuungsautuhoc); nguyên khí đổi ròng (tốn + hồi khi trúng) trong cửa sổ chiêu
        self._chuphieuungsautuhoc(chieu)
        hieuungmoi = chieu["hieuungsau"] or []
        nguyenkhidoi = (moitruong.get_nguyenkhiconlai() or 0) - chieu["nguyenkhi"]
        satthuong = sum(chieu["satthuongs"])
        dulieu["maus"].append([chieu["idkynang"], chieu["tenquai"], satthuong, round(thoigiankhoa, 3), chieu["hieuungmuctieu"],
                               chieu["hieuungminh"], hieuungmoi, nguyenkhidoi, round(chieu["thoidiem"], 1)])
        if len(dulieu["maus"]) > SOMAUTOIDATUHOC:
            # Giữ SOMAUTOIDATUHOC mẫu gần nhất: đổi đồ / lên cấp thì số mới dần thay số cũ
            del dulieu["maus"][:len(dulieu["maus"]) - SOMAUTOIDATUHOC]
        self._somaumoituhoc += 1
        self._is_tuhocthaydoi = True
        self._lancuoituhoc = {"thoidiem": time.time(), "ten": self._tenchieututhoc(chieu["vitri"]), "tenquai": chieu["tenquai"],
                              "satthuongs": list(chieu["satthuongs"]), "thoigiankhoa": thoigiankhoa,
                              "hieuungmoi": [self._tenhieuungtuhoc(e) for e in hieuungmoi]}
        if IS_LOGTUHOC:
            moi = f", gây {', '.join(self._lancuoituhoc['hieuungmoi'])}" if hieuungmoi else ""
            moitruong._inlog(f"[TỰ HỌC CHIÊU] {self._lancuoituhoc['ten']} -> {chieu['tenquai']}: {chieu['satthuongs']} trong {thoigiankhoa:.2f}s"
                             f" | quái có {chieu['hieuungmuctieu']}{moi} | nguyên khí {nguyenkhidoi:+d}")

    # ------------------------------------------------------------------ học

    def _hoctuhoc(self, thoidiemhientai):
        # Học lại mô hình khi có mẫu mới, tối đa mỗi THOIGIANHOCLAITUHOC giây (lần đầu học ngay khi có mẫu):
        #  log(sát thương) = gốc chiêu + hệ số quái + tổng ảnh hưởng các hiệu ứng đang có (trên quái "m", trên mình "b")
        #  (hồi quy ridge: ảnh hưởng hiệu ứng kéo về 0 khi ít mẫu; chỉ xét hiệu ứng có ít nhất SOMAUHIEUUNGTUHOC mẫu có và không có nó)
        #  + thời gian ra chiêu (trung vị), nguyên khí đổi (trung bình), hiệu ứng chiêu gây ra (tỉ lệ xuất hiện mới sau chiêu)
        if self._mohinhtuhoc is not None and (not self._somaumoituhoc or thoidiemhientai - self._thoidiemhoctuhoc < THOIGIANHOCLAITUHOC):
            return
        dulieu = self._taituhoc()
        if dulieu is None:
            return
        self._thoidiemhoctuhoc = thoidiemhientai
        self._somaumoituhoc = 0
        maus = [m for m in dulieu["maus"] if m[2] > 0]
        mohinh = {"goc": {}, "quai": {}, "hieuung": {}, "khoa": {}, "nguyenkhi": {}, "gay": {}, "solan": {}, "solanquai": {}}
        if maus:
            idchieus = sorted({m[0] for m in maus})
            tenquais = sorted({m[1] for m in maus})
            # Ảnh hưởng hiệu ứng học riêng từng chiêu (phá giáp tăng chiêu này mà có khi không tăng chiêu kia): đặc trưng "<id chiêu>|m<id
            # hiệu ứng>" (trên quái) / "<id chiêu>|b<id hiệu ứng>" (trên mình), chỉ xét khi chiêu đó có đủ mẫu có và không có hiệu ứng
            solanchieu, demco = {}, {}
            for m in maus:
                solanchieu[m[0]] = solanchieu.get(m[0], 0) + 1
                for khoa in self._dactrungtuhoc(m):
                    demco[khoa] = demco.get(khoa, 0) + 1
            dactrungs = sorted(k for k, n in demco.items()
                               if n >= SOMAUHIEUUNGTUHOC and solanchieu[int(k.split("|")[0])] - n >= SOMAUHIEUUNGTUHOC)
            cot = {("c", i): j for j, i in enumerate(idchieus)}
            cot.update({("q", q): len(idchieus) + j for j, q in enumerate(tenquais)})
            batdauhu = len(idchieus) + len(tenquais)
            cot.update({("h", k): batdauhu + j for j, k in enumerate(dactrungs)})
            x = np.zeros((len(maus), len(cot)))
            y = np.log(np.array([m[2] for m in maus], dtype = float))
            for i, m in enumerate(maus):
                x[i, cot[("c", m[0])]] = 1.
                x[i, cot[("q", m[1])]] = 1.
                for khoa in self._dactrungtuhoc(m):
                    j = cot.get(("h", khoa))
                    if j is not None:
                        x[i, j] = 1.
            phat = np.array([1e-3] * len(idchieus) + [1.] * len(tenquais) + [LAMDAHIEUUNGTUHOC] * len(dactrungs))
            try:
                beta = np.linalg.solve(x.T @ x + np.diag(phat), x.T @ y)
            except np.linalg.LinAlgError:
                beta = np.zeros(len(cot))
            for (loai, khoa), j in cot.items():
                {"c": mohinh["goc"], "q": mohinh["quai"], "h": mohinh["hieuung"]}[loai][khoa] = float(beta[j])
            for idchieu in idchieus:
                cua = [m for m in maus if m[0] == idchieu]
                mohinh["solan"][idchieu] = len(cua)
                mohinh["khoa"][idchieu] = float(np.median([m[3] for m in cua]))
                mohinh["nguyenkhi"][idchieu] = float(np.mean([m[7] for m in cua]))
                demgay = {}
                for m in cua:
                    for e in m[6]:
                        demgay[e] = demgay.get(e, 0) + 1
                # Hiệu ứng mới xuất hiện sau chiêu ở ít nhất TILEGAYHIEUUNGTUHOC số lần (bot khác cũng có thể gây hiệu ứng đó cùng lúc)
                mohinh["gay"][idchieu] = {e: n / len(cua) for e, n in demgay.items() if n >= 3 and n / len(cua) >= TILEGAYHIEUUNGTUHOC}
                for m in cua:
                    mohinh["solanquai"][(idchieu, m[1])] = mohinh["solanquai"].get((idchieu, m[1]), 0) + 1
        self._mohinhtuhoc = mohinh

    @staticmethod
    def _dactrungtuhoc(mau):
        return [f"{mau[0]}|m{e}" for e in mau[4]] + [f"{mau[0]}|b{e}" for e in mau[5]]

    def _satthuonggoctuhoc(self, idkynang, tenquai):
        # Sát thương 1 lần của chiêu với loại quái, chưa tính hiệu ứng. Chiêu chưa đủ SOMAUTOITHIEUTUHOC mẫu: lấy mức cao nhất đã biết
        # (lạc quan để bộ lập kế hoạch chịu dùng thử), chưa biết gì thì SATTHUONGMACDINHTUHOC
        mohinh = self._mohinhtuhoc or {}
        goc = mohinh.get("goc", {})
        if mohinh.get("solan", {}).get(idkynang, 0) >= SOMAUTOITHIEUTUHOC:
            return math.exp(goc[idkynang] + mohinh["quai"].get(tenquai, 0.))
        dabiet = [math.exp(goc[i] + mohinh["quai"].get(tenquai, 0.)) for i, n in mohinh.get("solan", {}).items() if n >= SOMAUTOITHIEUTUHOC]
        return max(dabiet) if dabiet else SATTHUONGMACDINHTUHOC

    # ------------------------------------------------------------------ lập kế hoạch

    def _lapkehoachtuhoc(self, idkynangs, diachimuctieu, thoidiemhientai):
        # Tìm chuỗi chiêu cho THOIGIANKEHOACHTUHOC giây tới (tìm chùm, giữ DORONGCHUMTUHOC chuỗi tốt nhất mỗi bước, tối đa
        # SOBUOCTOIDATUHOC chiêu): mỗi chiêu bắt đầu khi hết hồi chiêu và hết ra chiêu trước, sát thương = gốc * ảnh hưởng các hiệu ứng
        # còn hiệu lực lúc đó (trên quái và trên mình), chiêu gây hiệu ứng thì hiệu ứng có thêm từ lúc đó, đủ nguyên khí mới dùng được.
        # Trả về {"giatri": {id chiêu đầu: tổng sát thương chuỗi tốt nhất bắt đầu bằng nó}, "chuoi": [id], "tong", "dudoan": {id: sát
        # thương nếu dùng ngay}}
        moitruong = self.moitruong
        mohinh = self._mohinhtuhoc or {}
        anhhuong = mohinh.get("hieuung", {})
        tenquai = moitruong.get_tendoituong(diachimuctieu)
        nguyenkhi = moitruong.get_nguyenkhiconlai() or 0
        nguyenkhitoida = max(self._nguyenkhitoidatuhoc, nguyenkhi)
        hieuungquai = {}
        dau = self._hieuungtheodoituhoc["dau"] if self._hieuungtheodoituhoc and self._hieuungtheodoituhoc["id"] == moitruong.get_iddoituong(diachimuctieu) else {}
        for e in self._idhieuungs(diachimuctieu):
            thoigian = self._thoigianhieuungtuhoc(e)
            batdau = dau.get(e)
            hieuungquai[e] = max(0.2, thoigian - (thoidiemhientai - batdau)) if batdau else thoigian / 2.
        # Hiệu ứng trên mình: trường thứ 3 là số giây còn lại
        hieuungminh = {}
        for e, _, conlai in moitruong.get_danhsachhieuungnhanvats():
            if any(khoa.endswith(f"|b{e}") for khoa in anhhuong):
                hieuungminh[e] = conlai if conlai > 0 else THOIGIANKEHOACHTUHOC
        thongso = {}
        for idk in idkynangs:
            tieuhao = moitruong.get_tieuhaokynang(idk, is_truyvan = False) or {}
            hoichieu = tieuhao.get("tái sử dụng") or THOIGIANHOIMACDINHTUHOC
            tonnguyenkhi = tieuhao.get("nguyên khí", 0)
            if moitruong.get_is_kynangsansang(idk):
                sansang = 0.
            else:
                thoidiemnhan = self._thoidiemnhantuhoc.get(idk)
                sansang = max(0.05, hoichieu - (thoidiemhientai - thoidiemnhan)) if thoidiemnhan else hoichieu
            thongso[idk] = {"goc": self._satthuonggoctuhoc(idk, tenquai), "hoichieu": hoichieu, "ton": tonnguyenkhi, "sansang": sansang,
                            "khoa": mohinh.get("khoa", {}).get(idk, THOIGIANKHOAMACDINHTUHOC),
                            "nguyenkhi": mohinh.get("nguyenkhi", {}).get(idk, -tonnguyenkhi),
                            "gay": [e for e in mohinh.get("gay", {}).get(idk, {})]}
        if not thongso:
            return None
        # Tốc độ tham chiếu để so chuỗi dừng sớm với chuỗi dài: thời gian còn trống tính theo nửa tốc độ chiêu trung bình
        tocdo = 0.5 * float(np.median([t["goc"] / max(t["khoa"], t["hoichieu"]) for t in thongso.values()]))
        cuoi = THOIGIANKEHOACHTUHOC

        def anhhuonglucdo(idk, hieuungq, lucdo):
            tong = sum(anhhuong.get(f"{idk}|m{e}", 0.) for e, het in hieuungq.items() if het > lucdo)
            tong += sum(anhhuong.get(f"{idk}|b{e}", 0.) for e, het in hieuungminh.items() if het > lucdo)
            return math.exp(tong)

        dudoan = {idk: t["goc"] * anhhuonglucdo(idk, hieuungquai, max(0., t["sansang"])) for idk, t in thongso.items()}
        # Nút: (thời điểm rảnh, nguyên khí, sát thương đã giảm dần, {id: lúc hết hồi chiêu}, {hiệu ứng quái: lúc hết}, chuỗi, sát thương thật)
        chum = [(0., nguyenkhi, 0., {idk: t["sansang"] for idk, t in thongso.items()}, hieuungquai, [], 0.)]
        xong = []
        for _ in range(SOBUOCTOIDATUHOC):
            moi = []
            for luc, nk, tong, hethoi, hieuungq, chuoi, tongthuc in chum:
                is_morong = False
                for idk, t in thongso.items():
                    batdau = max(luc, hethoi[idk])
                    if batdau >= cuoi or (t["ton"] and nk < t["ton"]):
                        continue
                    # Sát thương ra sớm giá trị hơn (quái chết sớm, chuỗi bị cắt ngang): giảm GIAMDANTUHOC mỗi giây
                    satthuong = t["goc"] * anhhuonglucdo(idk, hieuungq, batdau)
                    hieuungq2 = {e: het for e, het in hieuungq.items() if het > batdau}
                    for e in t["gay"]:
                        hieuungq2[e] = batdau + THOIGIANTRESOBAYTUHOC + self._thoigianhieuungtuhoc(e)
                    hethoi2 = dict(hethoi)
                    hethoi2[idk] = batdau + t["hoichieu"]
                    nk2 = min(nguyenkhitoida, max(0., nk + t["nguyenkhi"])) if nguyenkhitoida else nk
                    moi.append((batdau + t["khoa"], nk2, tong + satthuong * GIAMDANTUHOC ** batdau, hethoi2, hieuungq2, chuoi + [idk],
                                tongthuc + satthuong))
                    is_morong = True
                if not is_morong:
                    xong.append((luc, nk, tong, hethoi, hieuungq, chuoi, tongthuc))
            if not moi:
                break
            moi.sort(key = lambda nut: nut[2] + max(0., cuoi - nut[0]) * tocdo * GIAMDANTUHOC ** cuoi, reverse = True)
            chum = moi[:DORONGCHUMTUHOC]
        xong.extend(chum)
        giatri = {}
        totnhat = None
        for luc, _, tong, _, _, chuoi, tongthuc in xong:
            if not chuoi:
                continue
            diem = tong + max(0., cuoi - luc) * tocdo * GIAMDANTUHOC ** cuoi
            if diem > giatri.get(chuoi[0], -1.):
                giatri[chuoi[0]] = diem
            if not totnhat or diem > totnhat[0]:
                totnhat = (diem, chuoi, tongthuc, min(luc, cuoi))
        if not totnhat:
            return None
        return {"giatri": giatri, "chuoi": totnhat[1], "tong": totnhat[2], "thoigian": totnhat[3], "dudoan": dudoan, "thongso": thongso,
                "tenquai": tenquai}

    def _sapxepuutientuhoc(self, danhsachuutien, diachimuctieu):
        # Chế độ Luật cố định: trả nguyên danh sách. Chế độ Tự học: các chiêu đánh mục tiêu (trừ CHIEUGIULUATTUHOCs) xếp lại theo giá trị
        # chuỗi tốt nhất bắt đầu bằng chiêu đó (_lapkehoachtuhoc), đặt lại vào đúng các ô của chúng trong danh sách; buff, di chuyển,
        # đánh thường giữ chỗ. Điều kiện từng mục vẫn của luật viết tay: chiêu đầu chuỗi không dùng được lúc này thì vòng lặp tự sang chiêu
        # kế. Đánh người chơi, chiến trường, MONPHAIKHONGTUHOCs vẫn dùng luật cố định.
        # Chế độ Luật cố định vẫn lập kế hoạch (thưa hơn) để giao diện hiện chuỗi Tự học sẽ dùng
        if not self._is_muctieuhoplehoc(diachimuctieu) or self._taituhoc() is None:
            return danhsachuutien
        moitruong = self.moitruong
        is_tuhoc = self._chedokynang == CHEDOKYNANG_TUHOC and moitruong.get_tenmonphai() not in MONPHAIKHONGTUHOCs
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemkehoachtuhoc >= (THOIGIANTINHKEHOACHTUHOC if is_tuhoc else 1.):
            self._thoidiemkehoachtuhoc = thoidiemhientai
            idkynangs = []
            for item in danhsachuutien:
                if item[0] and item[1] == "sudungkynangmuctieu" and item[0] not in CHIEUGIULUATTUHOCs and (len(item) < 5 or item[4] is None):
                    idkynang = moitruong.get_idkynang(item[0])
                    if idkynang and idkynang not in idkynangs:
                        idkynangs.append(idkynang)
            kehoach = self._lapkehoachtuhoc(idkynangs, diachimuctieu, thoidiemhientai) if idkynangs else None
            if kehoach:
                kehoach["thoidiem"] = thoidiemhientai
                kehoach["giuluats"] = list(dict.fromkeys(item[0] for item in danhsachuutien if item[0] in CHIEUGIULUATTUHOCs))
                self._kehoachtuhoc = kehoach
        kehoach = self._kehoachtuhoc
        if not is_tuhoc or not kehoach or thoidiemhientai - kehoach["thoidiem"] > 2.:
            return danhsachuutien
        giatri = kehoach["giatri"]
        vitris = [i for i, item in enumerate(danhsachuutien) if item[0] and item[1] == "sudungkynangmuctieu"
                  and item[0] not in CHIEUGIULUATTUHOCs and (len(item) < 5 or item[4] is None)]
        if len(vitris) < 2:
            return danhsachuutien
        # sorted giữ thứ tự cũ khi bằng điểm: cùng chiêu nhiều mục (điều kiện khác nhau) vẫn giữ thứ tự viết tay giữa chúng
        sapxep = sorted((danhsachuutien[i] for i in vitris), key = lambda item: giatri.get(moitruong.get_idkynang(item[0]), -1.), reverse = True)
        moi = list(danhsachuutien)
        for i, item in zip(vitris, sapxep):
            moi[i] = item
        return moi

    # ------------------------------------------------------------------ hiển thị

    def _tenchieututhoc(self, vitrikynang):
        # Tên chiêu đọc từ game (moitruong.get_tenkynangtheoid), nhớ theo id; chưa đọc được thì dùng id
        idkynang = self.moitruong.get_idkynang(vitrikynang)
        if not idkynang:
            return str(vitrikynang)
        ten = self._tenkynangtuhoc_map.get(idkynang)
        if not ten:
            ten = self.moitruong.get_tenkynangtheoid(idkynang)
            if ten:
                self._tenkynangtuhoc_map[idkynang] = ten
        return ten or f"Chiêu {idkynang}"

    def _tenhieuungtuhoc(self, e):
        # Hiệu ứng thường trùng id với chiêu gây ra nó: có chiêu đó trên bảng kỹ năng thì lấy tên chiêu, không thì tên hằng, không thì id
        khoa = ("hieuung", e)
        if khoa not in self._tenkynangtuhoc_map:
            ten = self._tenchieututhoc(e) if self.moitruong.get_vitrikynangtheoid(e) else None
            self._tenkynangtuhoc_map[khoa] = ten or _TENHIEUUNG_MAP.get(e) or f"Hiệu ứng {e}"
        return self._tenkynangtuhoc_map[khoa]

    def get_tinhhinhtuhoc(self):
        # Tình hình học cho giao diện (tính lại tối đa mỗi giây): chế độ, tổng số liệu, sát thương / giây cả trận theo chế độ, chuỗi đang
        # định dùng, từng chiêu (dự kiến lúc này, gốc, ra chiêu, hồi chiêu, gây hiệu ứng, số mẫu), ảnh hưởng của hiệu ứng, lần đo gần nhất
        thoidiemhientai = time.time()
        if self._tinhhinhtuhoc and thoidiemhientai - self._tinhhinhtuhoc["thoidiemtinh"] < 1.:
            return self._tinhhinhtuhoc
        dulieu = self._dulieutuhoc if self._idnguoichoituhoc else {}
        mohinh = self._mohinhtuhoc or {}
        kehoach = self._kehoachtuhoc
        chieus, chuoi, tenquai = [], [], None
        if kehoach:
            tenquai = kehoach["tenquai"]
            giatri = kehoach["giatri"]
            for thutu, idk in enumerate(sorted(kehoach["thongso"], key = lambda i: giatri.get(i, -1.), reverse = True), 1):
                t = kehoach["thongso"][idk]
                solan = mohinh.get("solanquai", {}).get((idk, tenquai), 0)
                tong = mohinh.get("solan", {}).get(idk, 0)
                chieus.append({
                    "thutu": thutu, "ten": self._tenchieututhoc(idk), "dudoan": kehoach["dudoan"].get(idk),
                    "goc": t["goc"] if tong >= SOMAUTOITHIEUTUHOC else None, "khoa": t["khoa"], "hoichieu": t["hoichieu"],
                    "gay": [self._tenhieuungtuhoc(e) for e in t["gay"]], "solan": solan, "tongsolan": tong,
                    "trangthai": "Đã học" if tong >= SOMAUTOITHIEUTUHOC else f"Đang thử ({tong}/{SOMAUTOITHIEUTUHOC})"})
            for vitri in kehoach.get("giuluats", []):
                chieus.append({"thutu": None, "ten": self._tenchieututhoc(vitri), "dudoan": None, "goc": None, "khoa": None, "hoichieu": None,
                               "gay": [], "solan": None, "tongsolan": None, "trangthai": "Giữ luật cố định"})
            chuoi = [self._tenchieututhoc(idk) for idk in kehoach["chuoi"]]
        # Hiệu ứng ảnh hưởng sát thương rõ (|log| >= 0.05, tức >= ~5%), gom theo hiệu ứng, ảnh hưởng lớn trước
        theohieuung = {}
        for khoa, w in mohinh.get("hieuung", {}).items():
            if abs(w) < 0.05:
                continue
            idchieu, hieuung = khoa.split("|")
            muc = theohieuung.setdefault(hieuung, {"ten": self._tenhieuungtuhoc(int(hieuung[1:])), "tren": "quái" if hieuung[0] == "m" else "mình",
                                                   "chieus": [], "lonnhat": 0.})
            muc["chieus"].append((self._tenchieututhoc(int(idchieu)), (math.exp(w) - 1.) * 100.))
            muc["lonnhat"] = max(muc["lonnhat"], abs(w))
        anhhuongs = sorted(theohieuung.values(), key = lambda muc: -muc["lonnhat"])
        for muc in anhhuongs:
            muc["chieus"].sort(key = lambda c: -abs(c[1]))
        trans = (dulieu.get("tran") or {})
        def dps(chedo, quai = None):
            tong = [0., 0., 0.]
            for ten, theochedo in trans.items():
                if quai and ten != quai:
                    continue
                dem = theochedo.get(chedo)
                if dem:
                    tong = [a + b for a, b in zip(tong, dem)]
            return (tong[0] / tong[1], tong[2]) if tong[1] else (None, 0)
        self._tinhhinhtuhoc = {
            "thoidiemtinh": thoidiemhientai,
            "chedo": self._chedokynang,
            "is_monphaikhonghoc": self.moitruong.get_tenmonphai() in MONPHAIKHONGTUHOCs,
            "somau": len(dulieu.get("maus") or []),
            "soquai": len({m[1] for m in dulieu.get("maus") or []}),
            "tenquai": tenquai,
            "giaytruoc": thoidiemhientai - kehoach["thoidiem"] if kehoach else None,
            "chieus": chieus,
            "chuoi": chuoi,
            "tongchuoi": kehoach["tong"] if kehoach else None,
            "thoigianchuoi": kehoach["thoigian"] if kehoach else None,
            "anhhuongs": anhhuongs[:6],
            "dps": {chedo: {"tatca": dps(chedo), "quai": dps(chedo, tenquai) if tenquai else (None, 0)}
                    for chedo in (CHEDOKYNANG_CODINH, CHEDOKYNANG_TUHOC)},
            "lancuoi": self._lancuoituhoc,
        }
        return self._tinhhinhtuhoc

    def _logtuhoc(self):
        # Mỗi THOIGIANLOGTUHOC giây: chuỗi đang định dùng, hiệu ứng ảnh hưởng, sát thương / giây cả trận theo chế độ
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemlogtuhoc < THOIGIANLOGTUHOC:
            return
        self._thoidiemlogtuhoc = thoidiemhientai
        tinhhinh = self.get_tinhhinhtuhoc()
        chedo = "Tự học" if self._chedokynang == CHEDOKYNANG_TUHOC else "Luật cố định"
        dps = " | ".join(f"{ten}: {tinhhinh['dps'][ma]['tatca'][0]:.0f}/s ({tinhhinh['dps'][ma]['tatca'][1]:.0f} con)"
                         for ma, ten in ((CHEDOKYNANG_CODINH, "cố định"), (CHEDOKYNANG_TUHOC, "tự học")) if tinhhinh["dps"][ma]["tatca"][0])
        anhhuong = "; ".join(f"{a['ten']} trên {a['tren']}: " + ", ".join(f"{ten} {pt:+.0f}%" for ten, pt in a["chieus"])
                             for a in tinhhinh["anhhuongs"])
        self.moitruong._inlog(f"[TỰ HỌC CHIÊU] ({chedo}) {tinhhinh['somau']} mẫu | chuỗi với {tinhhinh['tenquai']}: {' -> '.join(tinhhinh['chuoi'])}"
                              f" | hiệu ứng: {anhhuong or 'chưa rõ'} | sát thương/giây cả trận: {dps or 'chưa có'}")
