# Phần hoạt động khác: hội thoại NPC, tạm ngưng khi thấy ẩn thân / người lạ, tổ đội, phục sinh, PK, chặn tăng cấp, khai khoáng, chiến trường, tàng bảo đồ, auto trong game.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import re
import time
import unicodedata
import win32gui
import win32con

from hangso_xq import *
from tactu_doicau_xq import SOOTRONGGIUDOITANGBAODO, SOTANGBAODOMOICAP
from tactu_catkho_xq import LYDOCATKHO_DAOBAODO, TENCHUACATKHODAOBAODOs, KHOANGCACHQUANKHO
from thongbao_xq import baosuco, LYDOTAMNGUNGTUXA
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam, canhbao
from tienich_xq import laynhomtodoitudongs, donbangthoidiem, layvanglaitodois, layis_nhomtodoibat
from tienich_xq import ghitamngung as util_ghitamngung, xoatamngung as util_xoatamngung


class TacTuHoatDong:
    def get_is_danghoithoainpc(self):
        return bool(self._hangdoihoithoainpc) or self._is_chodongcuasohoithoainpc

    def action_batdauhoithoainpc(self, caulenhs):
        # Đang dở 1 cuộc hội thoại thì không bắt đầu cuộc mới (tránh gửi trùng các bước)
        if self.get_is_danghoithoainpc() or not caulenhs:
            return False
        self._thoidiemguihoithoainpctieptheo = 0.
        self._hangdoihoithoainpc = list(caulenhs)
        return True

    def action_xulyhoithoainpc(self):
        # Gọi mỗi lượt loop phụ: gửi tối đa 1 bước, bước sau cách bước trước 1s; gửi hết thì 1s sau đóng cửa sổ tuỳ chọn
        if time.time() < self._thoidiemguihoithoainpctieptheo:
            return
        if self._hangdoihoithoainpc:
            self.moitruong.action_thucthicaulenh(self._hangdoihoithoainpc.pop(0))
            self._thoidiemguihoithoainpctieptheo = time.time() + 1.
            if not self._hangdoihoithoainpc:
                self._is_chodongcuasohoithoainpc = True
            return
        if self._is_chodongcuasohoithoainpc:
            self._is_chodongcuasohoithoainpc = False
            if self.moitruong.get_is_danghiencuasotuychon():
                self.moitruong.set_is_danghiencuasotuychon(False)

    def get_is_dangchophucsinh(self):
        return self._is_tudongphucsinh and bool(self._thoidiembatdauchet)

    def get_is_dangtamngung(self):
        # Tắt bot cũng tính là tạm ngưng: mọi luồng chặn hoạt động theo hàm này
        return self._is_tatbot or time.time() < self._thoidiemhettamngung

    def thietlap_tatbot(self, is_tat):
        if is_tat == self._is_tatbot:
            return
        self._is_tatbot = is_tat
        print(f"[TẮT FOXIA] {'Tắt' if is_tat else 'Bật lại'} Foxia nhân vật này từ bảng điều khiển")
        phatam("Tắt Foxia" if is_tat else "Bật Foxia")
        if is_tat:
            self._dungmoihoatdong()

    def _dungmoihoatdong(self):
        self.moitruong.action_ngatdichuyen()
        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
        self._yeucautancong = None
        self._yeucautancongxuat = None
        self._yeucaunhatvatpham = None
        self._yeucaugomquai = None
        self._yeucautudo = None
        self._is_battudongtancongvatly = False

    def action_kiemtraanthan(self):
        # 1) Tự quét: thấy người chơi lạ ẩn thân, hoặc (ở map train) thấy người ngoài danh sách tổ đội, thì ghi nhận
        #    và công bố cho các cửa sổ khác (qua shared_data)
        # 2) Đang di chuyển theo lộ trình điểm đánh mà mình thấy, hoặc nhân vật khác CÙNG BẢN ĐỒ vừa thấy => ngưng hết mọi hoạt động
        #    (ẩn thân: THOIGIANTAMNGUNGANTHAN, người lạ: _thoigiantamngungnguoila). Người lạ thì làm theo _chienluocnguoila
        #    (CHIENLUOCNGUOILA_*: ngưng cả máy / chỉ mình / tránh xa / chỉ cảnh báo / bỏ qua)
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemkiemtraanthangannhat < 0.5:
            return
        self._thoidiemkiemtraanthangannhat = thoidiemhientai

        # Tân Thủ Thôn / Chu Quốc (BANDOKHONGTANCONGs) là thành an toàn, đông người qua lại: thấy người lạ hay ẩn thân cũng không tạm ngưng,
        # và không quét/công bố (nhân vật khác chỉ ngưng theo khi cùng bản đồ, mà cùng bản đồ thì cũng đang ở đây)
        if self.moitruong.get_idbandohientai() in BANDOKHONGTANCONGs:
            return

        phathien = self._quetnguoichoibatthuong()
        chienluoc = self._laychienluocnguoila()
        # Mọi chiến lược trừ "tatca": người lạ không công bố cho cửa sổ khác, chỉ xử lý ở nhân vật này và chỉ khi đang đi lộ trình
        # điểm đánh (như cũ: ô tạm ngưng cũ cũng chỉ ngưng trong trường hợp này). Ẩn thân (ADMIN kiểm tra) thì luôn ngưng
        if self._is_tudongdichuyendiemdanhxungquanh and chienluoc == CHIENLUOCNGUOILA_TRANH:
            # Đã tránh (bỏ quái / đổi điểm đánh) mà người lạ vẫn ở sát mình quá lâu => bám theo, chỉ nhân vật này ngưng
            bamtheo = self._laynguoilabamtheo()
            if bamtheo:
                self._batdautamngung(f"phát hiện người lạ {bamtheo} bám theo", self._thoigiantamngungnguoila, is_rieng = True)
                return
        if phathien and "ẩn thân" not in phathien[0] and chienluoc != CHIENLUOCNGUOILA_TATCA:
            if self._is_tudongdichuyendiemdanhxungquanh:
                if chienluoc == CHIENLUOCNGUOILA_MOT:
                    self._batdautamngung(f"phát hiện {phathien[0]}", phathien[1], is_rieng = True)
                    return
                if chienluoc in (CHIENLUOCNGUOILA_CANHBAO, CHIENLUOCNGUOILA_TRANH):
                    self._canhbaonguoila(phathien[0], "tránh xa, đánh tiếp" if chienluoc == CHIENLUOCNGUOILA_TRANH else "không tạm ngưng")
            phathien = None
        if phathien:
            # Chỉ công bố phát hiện trực tiếp (không công bố trạng thái tạm ngưng) để các nhân vật không gia hạn lẫn nhau mãi
            self._thoidiemphathienanthan = thoidiemhientai
            self._tenanthanphathien, self._thoigiantamngungphathien = phathien

        # Trong phó bản thì luôn kiểm tra (không cần bật lộ trình điểm đánh) nhưng chỉ ngưng vì ẩn thân, người ngoài nhóm trong phó bản là chuyện thường
        is_chianthan = not self._is_tudongdichuyendiemdanhxungquanh
        if is_chianthan and not (self.moitruong.get_idbandohientai() in BANDOPHOBANs or self.moitruong.get_is_phobanmuonbando()):
            # Không đi lộ trình, ngoài phó bản: vẫn ngưng khi chính mình hoặc nhân vật cùng bản đồ thấy tên trong TENANTHANLUONNGUNGs
            # ẩn thân, trừ khi mình đang bật PK (người dùng dặn 2026-11-18)
            if self.moitruong.get_idmaupk():
                return
            if phathien and self._is_anthanluonngung(phathien[0]):
                self._batdautamngung(f"phát hiện {phathien[0]}", phathien[1])
                return
            phathienkhac = self._layanthantucuasokhac()
            if phathienkhac and self._is_anthanluonngung(phathienkhac[0]):
                self._batdautamngung(*phathienkhac)
            return
        if phathien and (not is_chianthan or "ẩn thân" in phathien[0]):
            self._batdautamngung(f"phát hiện {phathien[0]}", phathien[1])
            return
        phathienkhac = self._layanthantucuasokhac()
        # Nhân vật khác thấy người lạ (nó chọn "tatca") thì mình chỉ ngưng theo khi mình cũng chọn "tatca"
        if phathienkhac and (not (is_chianthan or chienluoc != CHIENLUOCNGUOILA_TATCA) or "ẩn thân" in phathienkhac[0]):
            self._batdautamngung(*phathienkhac)

    def _laychienluocnguoila(self):
        # Đang kéo cấp (mọi vai, kể cả kéo gà A-Z): bãi / Phong Yêu Kính đông người, thấy người lạ không làm gì, không công bố cho cửa sổ
        # khác (người dùng dặn 2026-11-08). Bật Tự động khai khoáng cũng vậy: bãi khoáng đông người (người dùng dặn 2026-11-10)
        if self._keocap or self._is_tudongkhaikhoang:
            return CHIENLUOCNGUOILA_BOQUA
        return self._chienluocnguoila

    def _laynguoilabamtheo(self):
        # Tên người lạ đang thấy (vừa quét) ở trong _bankinhtranhnguoila quanh mình liên tục >= THOIGIANBAMTHEONGUOILA giây, không có thì None
        thoidiemhientai = time.time()
        for banghi in self._nguoilas.values():
            if banghi["gandau"] and thoidiemhientai - banghi["thaycuoi"] <= 1.5 \
                    and thoidiemhientai - banghi["gandau"] >= THOIGIANBAMTHEONGUOILA:
                return banghi["ten"]
        return None

    def get_toadonguoilatranh(self):
        # Chỗ người lạ mình thấy trong THOIGIANNHONGUOILA giây gần đây, khi đang chọn "tranh" (để tránh và chia sẻ cho bot cùng bản đồ): [(x, y)]
        if self._laychienluocnguoila() != CHIENLUOCNGUOILA_TRANH:
            return []
        thoidiemhientai = time.time()
        return [banghi["toado"] for banghi in self._nguoilas.values() if thoidiemhientai - banghi["thaycuoi"] <= THOIGIANNHONGUOILA]

    def _laytoadonguoilatranh(self):
        # Chỗ người lạ cần tránh: của mình + bot khác cùng bản đồ đang tránh (shared_data "_toadonguoilas"); đọc shared_data nhớ 1s
        toados = self.get_toadonguoilatranh()
        if self._laychienluocnguoila() != CHIENLUOCNGUOILA_TRANH:
            return toados
        thoidiem, toadokhacs = self._bonhonguoilabotkhac
        if time.time() - thoidiem >= 1.:
            toadokhacs = []
            idbando = self.moitruong.get_idbandohientai()
            try:
                danhsach = list(self.shared_data.items()) if self.shared_data is not None else []
            except Exception:
                danhsach = []
            for idcuaso, info in danhsach:
                if idcuaso == self.idcuaso or not isinstance(info, dict) or not info.get("_toadonguoilas"):
                    continue
                if time.time() - info.get("thoidiemcapnhat", 0.) > 5. or not self.moitruong.get_is_cungbando(info, idbando):
                    continue
                toadokhacs.extend(tuple(toado) for toado in info["_toadonguoilas"])
            self._bonhonguoilabotkhac = (time.time(), toadokhacs)
        return toados + toadokhacs

    def _is_gannguoila(self, x, y, toadonguoilas = None):
        # (x, y) nằm trong _bankinhtranhnguoila quanh chỗ một người lạ cần tránh (chiến lược "tranh"; chiến lược khác luôn False)
        toadonguoilas = self._laytoadonguoilatranh() if toadonguoilas is None else toadonguoilas
        return any(math.dist((x, y), toado) <= self._bankinhtranhnguoila for toado in toadonguoilas)

    @staticmethod
    def _is_anthanluonngung(mota):
        # mota: "<tên> ẩn thân" (tự thấy) hoặc "<nhân vật> phát hiện <tên> ẩn thân" (cửa sổ khác thấy) -> tên có trong TENANTHANLUONNGUNGs
        if not mota or not mota.endswith(" ẩn thân"):
            return False
        ten = mota[:-len(" ẩn thân")].rsplit(" phát hiện ", 1)[-1]

        def gon(chu):
            chu = "".join(c for c in unicodedata.normalize("NFD", chu) if not unicodedata.combining(c))
            return "".join(chu.replace("đ", "d").replace("Đ", "D").split()).lower()
        return gon(ten) in {gon(t) for t in TENANTHANLUONNGUNGs}

    def _canhbaonguoila(self, mota, hanhdong = "không tạm ngưng"):
        # Thấy người lạ mà không tạm ngưng (chỉ cảnh báo / tránh xa): phát âm + tin Telegram (theo 2 ô tuỳ chọn thông báo), tối đa 1 lần
        # mỗi THOIGIANTAMNGUNGNGUOILA giây (quét 0.5s/lần)
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemcanhbaonguoila < THOIGIANTAMNGUNGNGUOILA:
            return
        self._thoidiemcanhbaonguoila = thoidiemhientai
        print(f"[CẢNH BÁO] Phát hiện {mota} ({hanhdong})")
        canhbao(self.moitruong, "Phát hiện người lạ", is_phatam = self._is_phatamnguoila)
        if self._is_telegramnguoila:
            baosuco(self.moitruong, "tamngung", f"Phát hiện {mota} ({hanhdong})", khoa = mota)

    def _layidnguoichoicungmays(self):
        # ID các nhân vật đang chạy ở mọi cửa sổ trên máy này (qua shared_data)
        if self.shared_data is None:
            return set()
        try:
            danhsach = list(self.shared_data.values())
        except Exception:
            return set()
        return {info.get("idnguoichoi") for info in danhsach if isinstance(info, dict) and info.get("idnguoichoi")}

    def _is_nguoichoinoibo(self, idnguoichoi, idnhanvathientai, idcungmays, idcungnhoms = ()):
        # Nội bộ = chính mình + nhân vật cùng máy + thành viên cùng nhóm + người quen (get_idnguoiquens: bot đang chạy, file tài khoản, danh
        # sách tổ đội, đội phó bản đang chạy);
        # ai khác (kể cả cùng bang mà khác nhóm) đều là người lạ
        return idnguoichoi == idnhanvathientai or idnguoichoi in idcungmays or idnguoichoi in idcungnhoms or idnguoichoi in self.get_idnguoiquens()

    def _quetnguoichoibatthuong(self):
        # Trả về (mô tả, số giây tạm ngưng): ("X ẩn thân", THOIGIANTAMNGUNGANTHAN) / ("người lạ X", _thoigiantamngungnguoila) hoặc None.
        # Người lạ (map train) được ghi vào _nguoilas (chỗ đứng, lúc thấy đầu / cuối, lúc bắt đầu ở sát mình) cho chiến lược tránh / bám
        # theo; chỉ trả về người lạ đã ở lại >= _thoigianphanungnguoila giây (người đi ngang qua thì bỏ qua)
        idnhanvathientai = self.moitruong.get_idnguoichoi()
        idcungmays = self._layidnguoichoicungmays()
        idcungnhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms() or ()
        idbando = self.moitruong.get_idbandohientai()
        is_maptrain = idbando not in BANDOKHONGPKs
        thoidiemhientai = time.time()
        if idbando != self._idbandonguoilas:
            self._nguoilas = {}
            self._idbandonguoilas = idbando
        else:
            for idcu in [i for i, banghi in self._nguoilas.items() if thoidiemhientai - banghi["thaycuoi"] > THOIGIANNHONGUOILA]:
                self._nguoilas.pop(idcu, None)
        toadobanthan = None
        nguoila = None
        # Bản chụp chỉ có nhân vật còn tồn tại: bỏ được ô đối tượng còn sót (nhân vật đã rời đi / chưa tải xong), không báo nhầm người lạ
        for diachidoituong in self.moitruong.get_diachinhanvattontais():
            if not self.moitruong.get_is_nguoichoi(diachidoituong):
                continue
            idnguoichoi = self.moitruong.get_idnguoichoi(diachidoituong)
            if self._is_nguoichoinoibo(idnguoichoi, idnhanvathientai, idcungmays, idcungnhoms):
                continue
            if self.moitruong.get_khoangcach(diachidoituong) > KHOANGCACHTOANMANHINH:
                continue
            tendoituong = self.moitruong.get_tendoituong(diachidoituong) or str(idnguoichoi)
            if self.moitruong.get_is_nhanvatanthan(diachidoituong):
                # Ẩn thân luôn ưu tiên báo trước (thời gian tạm ngưng dài hơn)
                return f"{tendoituong} ẩn thân", THOIGIANTAMNGUNGANTHAN
            if not is_maptrain:
                continue
            toado = tuple(self.moitruong.get_toado(diachidoituong))
            if toadobanthan is None:
                toadobanthan = self.moitruong.get_toado()
            banghi = self._nguoilas.get(idnguoichoi)
            if banghi is None or thoidiemhientai - banghi["thaycuoi"] > THOIGIANGIANDOANNGUOILA:
                banghi = {"thaydau": thoidiemhientai, "gandau": 0.}
                self._nguoilas[idnguoichoi] = banghi
            banghi.update(ten = tendoituong, toado = toado, thaycuoi = thoidiemhientai)
            if math.dist(toado, toadobanthan) <= self._bankinhtranhnguoila:
                banghi["gandau"] = banghi["gandau"] or thoidiemhientai
            else:
                banghi["gandau"] = 0.
            if nguoila is None and thoidiemhientai - banghi["thaydau"] >= self._thoigianphanungnguoila:
                nguoila = f"người lạ {tendoituong}", self._thoigiantamngungnguoila
        return nguoila

    def _layanthantucuasokhac(self):
        # Nhân vật khác cùng bản đồ vừa tự phát hiện (trong vài giây gần đây) => (lý do, số giây) để tạm ngưng theo.
        # Có nhiều nguồn thì lấy nguồn có thời gian tạm ngưng dài nhất (ẩn thân trước người lạ)
        if self.shared_data is None:
            return None
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return None
        idbandohientai = self.moitruong.get_idbandohientai()
        ketqua = None
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict):
                continue
            if not self.moitruong.get_is_cungbando(info, idbandohientai):
                continue
            if time.time() - info.get("_thoidiemphathienanthan", 0.) > THOIGIANCHIASEANTHAN:
                continue
            thoigian = info.get("_thoigiantamngungphathien") or THOIGIANTAMNGUNGANTHAN
            if ketqua is None or thoigian > ketqua[1]:
                ketqua = (f"{info.get('tennhanvat') or idcuaso} phát hiện {info.get('_tenanthanphathien') or 'người lạ'}", thoigian)
        return ketqua

    def _batdautamngung(self, lydo, thoigian = None, is_rieng = False):
        # is_rieng: chỉ nhân vật này ngưng (chiến lược người lạ "mot" / bị bám theo), file tạm ngưng không chặn tự đăng nhập acc khác.
        # Đang ngưng chung thì giữ chung
        thoigian = thoigian or THOIGIANTAMNGUNGANTHAN
        is_moibatdau = time.time() >= self._thoidiemhettamngung
        is_rieng = is_rieng and (is_moibatdau or self._is_tamngungrieng)
        # Chỉ kéo dài, không rút ngắn (đang ngưng 10 phút vì ẩn thân mà gặp người lạ thì vẫn giữ 10 phút)
        thoidiemhetmoi = time.time() + thoigian
        if is_moibatdau or thoidiemhetmoi >= self._thoidiemhettamngung:
            self._thoidiemhettamngung = thoidiemhetmoi
            self._lydotamngung = lydo
            self._is_tamngungrieng = is_rieng
            util_ghitamngung(self.moitruong.get_idnguoichoi(), thoidiemhetmoi, lydo, is_rieng = is_rieng)
        if is_moibatdau:
            thoigianhienthi = f"{int(thoigian // 60)} phút" if thoigian >= 60 else f"{int(thoigian)} giây"
            print(f"[TẠM NGƯNG] {lydo} -> Ngưng mọi hoạt động {thoigianhienthi}")
            if lydo == LYDOTAMNGUNGTUXA:
                canhbao(self.moitruong, "Tạm ngưng từ xa")
            else:
                # Người lạ: phát âm / Telegram theo 2 ô tuỳ chọn thông báo (người dùng 2026-11-26: điếc tai, phiền). Ẩn thân luôn báo
                is_anthan = "ẩn thân" in lydo
                canhbao(self.moitruong, "Phát hiện ẩn thân, tạm ngưng" if is_anthan else "Phát hiện người lạ, tạm ngưng",
                        is_phatam = is_anthan or self._is_phatamnguoila)
                # Chỉ nhân vật tự phát hiện ("phát hiện <tên>") báo, các nhân vật ngưng theo ("<ai đó> phát hiện ...") thì không, cho
                # 1 lần phát hiện chỉ ra 1 tin
                if lydo.startswith("phát hiện") and (is_anthan or self._is_telegramnguoila):
                    phamvi = "nhân vật này" if is_rieng else "cả máy"
                    baosuco(self.moitruong, "tamngung", f"Phát hiện {lydo[len('phát hiện '):]}, {phamvi} tạm ngưng {thoigianhienthi}", khoa = lydo)
            self._dungmoihoatdong()

    def tieptuchoatdong(self):
        # Bật lại thủ công: vẫn tiếp tục kiểm tra ẩn thân, gặp người ẩn thân là tạm ngưng tiếp
        self._thoidiemhettamngung = 0.
        self._lydotamngung = ""
        self._is_tamngungrieng = False
        util_xoatamngung(self.moitruong.get_idnguoichoi())
        print("[TẠM NGƯNG] Bật lại hoạt động thủ công")
        phatam("Bật lại hoạt động")

    def _laybotkhacs(self):
        # {ID người chơi: info} các cửa sổ khác đang chạy bot (cùng máy / máy khác nối LAN, còn cập nhật), đọc shared_data 1 lần
        try:
            danhsach = list(self.shared_data.items()) if self.shared_data is not None else []
        except Exception:
            return {}
        return {info["idnguoichoi"]: info for idcuaso, info in danhsach if idcuaso != self.idcuaso and isinstance(info, dict)
                and info.get("idnguoichoi") and time.time() - info.get("thoidiemcapnhat", 0.) <= 5.}

    def get_is_tudongtodoi(self):
        # Tổ đội tự động bật theo NHÓM trong todoi.json (người dùng 2026-11-26: cấu hình cho đội nhóm, không cho từng nhân vật), trừ khi
        # nhân vật này đang bị tạm tắt riêng (_is_tudongtodoi, đội phó bản giải tán). Không ở nhóm nào thì tắt
        if not self._is_tudongtodoi:
            return False
        idtoi = self.moitruong.get_idnguoichoi()
        nhom = next((n for n in laynhomtodoitudongs() if idtoi in n), None)
        return bool(nhom) and layis_nhomtodoibat(nhom)

    def _laynhomtodoicuatoi(self):
        # Nhóm todoi.json có mình (Tổ đội tự động), bỏ người đang bị đội phó bản đang chạy giữ (đội phó bản lo, không kéo
        # họ đi). -> [ID theo thứ tự ưu tiên] hoặc None (mình không có trong nhóm nào)
        idtoi = self.moitruong.get_idnguoichoi()
        nhom = next((list(n) for n in laynhomtodoitudongs() if idtoi in n), None)
        if not nhom:
            return None
        giu = self.get_idsdoiphobangiu()
        nhom = [i for i in nhom if i == idtoi or i not in giu]
        # Vãng lai xếp sau mọi thường trực (không được nhường trưởng nhóm: vãng lai hay ra vào, trưởng nhóm rời là đổi chủ cả nhóm)
        vanglais = layvanglaitodois()
        return [i for i in nhom if i not in vanglais] + [i for i in nhom if i in vanglais]

    def get_vanglaishare(self):
        # Mình là vãng lai: {"canbuffs": [buff nhóm đang thiếu], "lucvaonhom", "lucnhuong"} cho trưởng nhóm / vãng lai khác đọc; không thì None
        if self.moitruong.get_idnguoichoi() not in layvanglaitodois():
            return None
        return {"canbuffs": list(self._buffnhomthieu[1]), "lucvaonhom": self._vanglai["lucvaonhom"], "lucnhuong": self._vanglai["lucnhuong"]}

    def _tinhbuffnhomthieu(self, nhom, botkhacs):
        # Buff chỉ thành viên nhóm mới nhận (giống luật _canbuffthanhvienxa nhánh thành viên nhóm) mà mình đang thiếu / sắp hết, chỉ tính
        # buff có người buff THƯỜNG TRỰC cùng nhóm tổ đội, cùng bản đồ, đang bật Tự động sử dụng kỹ năng. -> [tên buff]. 1s tính 1 lần;
        # bảng hiệu ứng đang tải lại thì giữ kết quả cũ
        lucxet, cu = self._buffnhomthieu
        if time.time() - lucxet < 1.:
            return cu
        moitruong = self.moitruong
        if moitruong.get_is_nhanvatdachet():
            self._buffnhomthieu = (time.time(), [])
            return []
        if moitruong.get_is_cohieuungs((), None) is None:
            return cu
        idbando = moitruong.get_idbandohientai()
        vanglais = layvanglaitodois()
        monphaibuffs = {info.get("tenmonphai") for id_, info in botkhacs.items() if id_ in nhom and id_ not in vanglais
                        and info.get("tenbando") == idbando and info.get("_is_tudongsudungkynang")}

        def thieu(idhieuung):
            conlai = moitruong.get_thoigianconlaihieuung(idhieuung, is_hieuungcoloi = 1)
            return conlai is None or conlai < THOIGIANBUFFNHOMSAPHET

        thieus = []
        if "vanmongcoc" in monphaibuffs:
            is_canngancham, is_cankimcham = self._loaichamcanbuff(moitruong.get_tenmonphai(), moitruong.get_idloaivukhi())
            if is_canngancham and thieu(HIEUUNGKYNANG_NGANCHAMDOACH):
                thieus.append("Ngân Châm Độ Ách")
            if is_cankimcham and thieu(HIEUUNGKYNANG_KIMCHAMDOACH):
                thieus.append("Kim Châm Độ Ách")
            if thieu(HIEUUNGKYNANG_CUONGTHETHUAT):
                thieus.append("Cường Thể Thuật")
        if "daohoanguyen" in monphaibuffs and not moitruong.is_nietban and thieu(HIEUUNGKYNANG_HOTHEKIMCANG):
            thieus.append("Hộ Thể Kim Cang")
        if "thucson" in monphaibuffs and thieu(HIEUUNGKYNANG_NOIKHANG):
            thieus.append("Tiêu Chu Thiên")
        self._buffnhomthieu = (time.time(), thieus)
        return thieus

    def _ghitrangthaivanglai(self, trangthai):
        if trangthai != self._trangthaivanglai:
            self._trangthaivanglai = trangthai
            if trangthai:
                self.moitruong._inlog(f"[TỔ ĐỘI VÃNG LAI] {trangthai}")

    def _layidtruongnhomchinh(self, nhom, botkhacs, idbando):
        # Nhóm chính = nhóm của các thường trực cùng bản đồ (trưởng nhóm nhiều thường trực theo nhất), 0 nếu không có
        vanglais = layvanglaitodois()
        dem = {}
        for id_, info in botkhacs.items():
            if id_ in nhom and id_ not in vanglais and info.get("tenbando") == idbando and info.get("idtruongnhom"):
                dem[info["idtruongnhom"]] = dem.get(info["idtruongnhom"], 0) + 1
        return max(dem, key = dem.get) if dem else 0

    def _xulyvanglai(self, nhom, botkhacs, idbando):
        # Mình là thành viên vãng lai và có nhóm chính (thường trực) cùng bản đồ: nhóm giữ đủ số tối đa (Aegis 5), vãng lai
        # đang trong nhóm chỉ nhường slot (tự rời) khi có vãng lai khác ngoài nhóm cần buff nhóm mà nhóm hết chỗ; ngoài nhóm thì chỉ
        # nhận lời mời của trưởng nhóm chính (không tự xin vào, không lập nhóm phụ), vừa nhường thì nghỉ THOIGIANVANGLAINGHISAUNHUONG
        # giây trừ khi chính mình cần buff. -> luôn True (Tổ đội tự động thường bỏ lượt này)
        # Vãng lai KHÔNG BAO GIỜ chạy luật Tổ đội tự động thường (người dùng 2026-11-28): trước đây không có nhóm chính cùng bản đồ
        # (thường trực ở bản đồ khác) thì trả False chạy như thường trực => các vãng lai tự mời nhau lập nhóm riêng (không mời từ xa
        # để gọi Thiên Lý Hữu Tình được nữa), đang ở nhóm trưởng nhóm thường trực mời từ xa cũng tự rời để "vào nhóm hạng cao hơn"
        moitruong = self.moitruong
        idtoi = moitruong.get_idnguoichoi()
        s = self._vanglai
        now = time.time()
        vanglais = layvanglaitodois()
        thuongtrucs = [i for i in nhom if i not in vanglais]
        idchinh = self._layidtruongnhomchinh(nhom, botkhacs, idbando)
        if idchinh == idtoi:
            idchinh = 0

        def ten(id_):
            return (botkhacs.get(id_) or {}).get("tennhanvat") or str(id_)

        def vl(id_):
            return (botkhacs.get(id_) or {}).get("_vanglai") or {}

        is_trongnhom = moitruong.get_is_dangnamtrongnhom()
        idtruongnhom = moitruong.get_idnguoichoitruongnhom() if is_trongnhom else 0
        if is_trongnhom and (not idchinh or idtruongnhom != idchinh):
            # Không phải nhóm chính cùng bản đồ: ở yên, chỉ rời nhóm do vãng lai tự ghép với nhau (trưởng nhóm là vãng lai cùng nhóm
            # todoi.json, trong nhóm không có thường trực nào) để thường trực mời được. Nhóm thường trực mời từ xa / người ngoài lập thì giữ
            s["lucvaonhom"] = 0.
            self._buffnhomthieu = (0., [])
            thanhviens = list(moitruong.get_danhsachidnguoichoithanhviennhoms() or ())
            is_nhomvanglai = not any(i in thuongtrucs for i in thanhviens) and all(i == idtoi or i in vanglais for i in thanhviens)
            if is_nhomvanglai and (len(thanhviens) > 1 or idtruongnhom == idtoi):
                self._ghitrangthaivanglai("rời nhóm vãng lai tự ghép (không có thường trực)")
                if now - s["lucroi"] > 1.5:
                    s["lucroi"] = now
                    moitruong.action_thoatkhoinhom()
            elif idtruongnhom == idtoi and len(thanhviens) > 1:
                # Mình là trưởng nhóm có thường trực: nhường quyền cho thường trực đầu tiên (vãng lai không làm trưởng nhóm)
                idnhan = next((i for i in thuongtrucs if i in thanhviens), 0)
                self._ghitrangthaivanglai(f"nhường trưởng nhóm cho {ten(idnhan)}")
                if idnhan and now - s["lucroi"] > 1.5:
                    s["lucroi"] = now
                    moitruong.action_nhuongquyentruongnhom(idnhan)
            else:
                self._ghitrangthaivanglai(f"ở nhóm {ten(idtruongnhom)} (không phải nhóm chính cùng bản đồ), giữ nguyên")
            return True
        if not is_trongnhom and not idchinh:
            # Chưa có nhóm, không có nhóm chính cùng bản đồ: chỉ nhận lời mời của thường trực (mời từ xa được), không tự mời / xin vào ai
            s["lucvaonhom"] = 0.
            self._buffnhomthieu = (0., [])
            self._ghitrangthaivanglai("chờ thường trực mời")
            self._dongytodoitudong = (now, list(thuongtrucs))
            moitruong.action_kiemtravadongyloimoinhom(thuongtrucs)
            return True
        canbuffs = self._tinhbuffnhomthieu(nhom, botkhacs)
        if not is_trongnhom:
            s["lucvaonhom"] = 0.
            is_nghi = not canbuffs and now - s["lucnhuong"] < THOIGIANVANGLAINGHISAUNHUONG
            if is_nghi:
                self._ghitrangthaivanglai(f"vừa nhường slot, nghỉ {int(THOIGIANVANGLAINGHISAUNHUONG - (now - s['lucnhuong']))}s")
                return True
            self._ghitrangthaivanglai(f"chờ nhóm {ten(idchinh)} mời" + (f" (cần {', '.join(canbuffs)})" if canbuffs else ""))
            # Nhóm chính trước, rồi tới thường trực khác (mời từ xa để gọi Thiên Lý Hữu Tình)
            idsdongy = [idchinh] + [i for i in thuongtrucs if i != idchinh]
            self._dongytodoitudong = (now, idsdongy)
            moitruong.action_kiemtravadongyloimoinhom(idsdongy)
            return True
        # Trong nhóm chính
        if not s["lucvaonhom"]:
            s["lucvaonhom"] = now
        thanhviens = list(moitruong.get_danhsachidnguoichoithanhviennhoms() or ())

        def ngoainhom(i):
            # Người chạy bot cùng nhóm tổ đội, cùng bản đồ, chưa ở nhóm chính
            return i != idtoi and i not in thanhviens and i in botkhacs and botkhacs[i].get("tenbando") == idbando                 and botkhacs[i].get("idtruongnhom") != idchinh

        # Thường trực bắt buộc luôn trong nhóm: thường trực quay lại (vừa online / về bản đồ / rời nhóm phụ) mà nhóm đầy thì vãng lai
        # nhường ngay, không chờ đủ buff. Chỉ tính người đang bật Tổ đội tự động (nhóm bật, không bị tạm tắt riêng)
        ttngoais = [i for i in nhom if i not in vanglais and ngoainhom(i) and botkhacs[i].get("_is_tudongtodoi")]
        canngoais = [i for i in nhom if i in vanglais and ngoainhom(i) and vl(i).get("canbuffs")]
        controng = max(0, moitruong.get_soluongthanhviennhomtoida() - len(thanhviens))
        thieucho_tt = max(0, len(ttngoais) - controng)
        thieucho_vl = max(0, len(canngoais) - max(0, controng - len(ttngoais)))
        if not thieucho_tt and not thieucho_vl:
            self._ghitrangthaivanglai(f"giữ slot nhóm {ten(idchinh)}" + (f", chờ buff {', '.join(canbuffs)}" if canbuffs else ""))
            return True

        def damoivao(lucvao):
            return lucvao and now - lucvao >= THOIGIANVANGLAIOTOITHIEU

        def duocnhuong(cb, lucvao):
            # Cho vãng lai cần buff: chỉ khi đã đủ buff (vừa vào thì chưa xét). Bỏ nhánh "chờ quá THOIGIANVANGLAICHOBUFF giây" 2026-11-28:
            # người buff ở xa thì vãng lai chưa được buff cũng tự rời (người dùng báo)
            return damoivao(lucvao) and not cb

        # Vãng lai trong nhóm (cả mình), người đủ buff trước rồi người vào sớm nhất: thieucho_tt người đầu (đã vào đủ lâu) nhường cho
        # thường trực, rồi thieucho_vl người kế (đủ điều kiện duocnhuong) nhường cho vãng lai cần buff
        ungviens = [(bool(canbuffs), s["lucvaonhom"], idtoi)]
        for i in thanhviens:
            if i != idtoi and i in vanglais and i in botkhacs:
                d = vl(i)
                ungviens.append((bool(d.get("canbuffs")), d.get("lucvaonhom") or 0., i))
        ungviens.sort()
        roi_tt = [u[2] for u in ungviens if damoivao(u[1])][:thieucho_tt]
        roi_vl = [u[2] for u in ungviens if u[2] not in roi_tt and duocnhuong(u[0], u[1])][:thieucho_vl]
        if idtoi in roi_tt:
            lydo = f"thường trực {', '.join(ten(i) for i in ttngoais[:thieucho_tt])} quay lại"
        elif idtoi in roi_vl:
            lydo = f"{', '.join(ten(i) for i in canngoais[:thieucho_vl])} cần {', '.join(vl(canngoais[0]).get('canbuffs') or ())}"
        else:
            chos = [ten(i) for i in ttngoais + canngoais]
            if not damoivao(s["lucvaonhom"]):
                self._ghitrangthaivanglai(f"giữ slot (mới vào), {', '.join(chos)} đang chờ")
            elif canbuffs and thieucho_vl and not thieucho_tt:
                self._ghitrangthaivanglai(f"giữ slot, chờ buff {', '.join(canbuffs)}; {', '.join(chos)} đang chờ")
            else:
                self._ghitrangthaivanglai(f"giữ slot, vãng lai khác nhường cho {', '.join(chos)}")
            return True
        self._ghitrangthaivanglai(f"nhường slot: {lydo}")
        s["lucnhuong"] = now
        if now - s["lucroi"] > 1.5:
            s["lucroi"] = now
            moitruong.action_thoatkhoinhom()
        return True

    def _locvanglaimoi(self, chuavaos, botkhacs):
        # Trưởng nhóm thường trực mời: thường trực trước như cũ; vãng lai cần buff nhóm thì chỉ mời họ, không ai cần thì mời vãng lai
        # chưa nhường gần đây cho đủ nhóm (vừa nhường THOIGIANVANGLAINGHISAUNHUONG giây thì chừa chỗ cho người cần buff)
        vanglais = layvanglaitodois()
        if not vanglais:
            return chuavaos
        now = time.time()
        thuongtrucs = [i for i in chuavaos if i not in vanglais]
        vls = [i for i in chuavaos if i in vanglais]
        canbuffs = [i for i in vls if ((botkhacs.get(i) or {}).get("_vanglai") or {}).get("canbuffs")]
        if canbuffs:
            return thuongtrucs + canbuffs
        return thuongtrucs + [i for i in vls
                              if now - (((botkhacs.get(i) or {}).get("_vanglai") or {}).get("lucnhuong") or 0.) >= THOIGIANVANGLAINGHISAUNHUONG]

    def _moilanluot(self, s, chuavaos, botkhacs):
        # Mời lần lượt từng người (Tổ đội tự động, đội phó bản lập nhóm), s: {"dangmoi": ID đang mời, "lucmoi"}. Trưởng nhóm có lời mời đang
        # chờ mà mời thêm người khác thì người trước bấm đồng ý lại thành "xin vào nhóm", chỉ người được mời sau đồng ý mới vào. Người đang
        # mời đã vào / quá THOIGIANCHOMOITHANHVIEN giây chưa vào thì mới mời người kế. Người chạy bot còn ở nhóm khác (đang tự rời) thì chưa
        # mời: mời lúc đó họ không đồng ý được, phí cả THOIGIANCHOMOITHANHVIEN giây chờ. Người không chạy bot (không biết nhóm) coi như
        # đang lẻ. -> (người sẵn sàng được mời, người còn kẹt ở nhóm khác)
        now = time.time()
        idnguoichoi = self.moitruong.get_idnguoichoi()
        conkets = [i for i in chuavaos if (botkhacs.get(i) or {}).get("idtruongnhom", 0) not in (0, idnguoichoi)]
        if s["dangmoi"] and (s["dangmoi"] not in chuavaos or s["dangmoi"] in conkets or now - s["lucmoi"] > THOIGIANCHOMOITHANHVIEN):
            s["dangmoi"] = 0
        sansangs = [i for i in chuavaos if i not in conkets]
        if not s["dangmoi"] and sansangs:
            # Người lâu chưa được mời nhất trước
            idmoi = min(sansangs, key = lambda i: self._thoidiemtodoigannhat_map.get(i, 0))
            if self.moitruong.action_moihoacxinvaonhom(idmoi):
                self._thoidiemtodoigannhat_map[idmoi] = now
                s.update(dangmoi = idmoi, lucmoi = now)
        return sansangs, conkets

    def action_todoinhanh(self):
        # Luồng riêng (cuaso_xq.khoidong_looptodoinhanh): luồng phụ chứa Tổ đội tự động mỗi lượt ~1s (nghỉ 0.5s + cả chục việc khác) nên
        # mời / đồng ý từng người chậm 3-4s. Đội phó bản đang lập nhóm (action_doiphobannhanh), Tổ đội tự động đang mời lần lượt / chờ đồng
        # ý thì xử lý ở đây. -> True khi đang mời / được mời (luồng chạy nhanh), False khi rảnh (luồng nghỉ lâu).
        # Nút "Tổ đội 1 lần" đã bỏ 2026-11-26 (bật rồi tắt Tổ đội tự động là đủ)
        if self.action_doiphobannhanh():
            return True
        if self._moitieptodoitudong():
            return True
        # Tổ đội tự động, mình chưa có nhóm: đồng ý lời mời ở đây (0.25s/lượt) thay vì đợi luồng phụ ~1s/lượt. Danh sách luồng phụ ghi
        # quá 3s (luồng phụ nghỉ / Tổ đội tự động tạm nghỉ) thì bỏ
        lucdongy, idsdongy = self._dongytodoitudong
        if idsdongy and time.time() - lucdongy < 3. and self.get_is_tudongtodoi() and not self._matac \
                and not self.moitruong.get_is_dangnamtrongnhom():
            self.moitruong.action_kiemtravadongyloimoinhom(idsdongy)
            return True
        return False

    def _moitieptodoitudong(self):
        # Tổ đội tự động, mình là trưởng nhóm đang mời lần lượt: luồng phụ ~1s/lượt (+ chặn 0.5s) nên người đang mời vào nhóm rồi vẫn
        # phải chờ lượt sau mới mời người kế, cả nhóm vào rất chậm (người dùng nhắc 2026-11-22). Ở đây (luồng nhanh 0.25s): người đang
        # mời đã vào nhóm thì mời ngay người kế trong danh sách sẵn sàng luồng phụ vừa ghi (quá 3s thì bỏ, để luồng phụ tính lại).
        # -> True khi còn người chờ mời (giữ luồng chạy nhanh)
        s = self._moiluottodoitudong
        sansangs = s.get("sansangs") or []
        if not sansangs or time.time() - s.get("lucsansang", 0.) > 3. or not self.get_is_tudongtodoi():
            return False
        moitruong = self.moitruong
        if not moitruong.get_is_dangnamtrongnhom() or not moitruong.get_is_truongnhom():
            return False
        thanhviens = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ())
        if len(thanhviens) >= moitruong.get_soluongthanhviennhomtoida():
            s["sansangs"] = []
            return False
        conlai = [i for i in sansangs if i not in thanhviens]
        s["sansangs"] = conlai
        if conlai:
            # Người đang mời vừa vào / quá hạn thì _moilanluot mời người kế luôn (botkhacs rỗng: luồng phụ đã lọc người còn kẹt nhóm khác)
            self._moilanluot(s, conlai, {})
        return bool(conlai)

    def _tenidnguoichoi(self, idnguoichoi):
        try:
            for info in list(self.shared_data.values()) if self.shared_data is not None else ():
                if isinstance(info, dict) and info.get("idnguoichoi") == idnguoichoi and info.get("tennhanvat"):
                    return info["tennhanvat"]
        except Exception:
            pass
        return str(idnguoichoi)

    def _buffthieucuathanhvien(self, diachi, tenmonphai):
        # Buff nhóm mình (phái tenmonphai, đã học chiêu) buff được mà thành viên ở diachi đang thiếu -> [tên buff]. Cùng luật chọn người
        # buff của từng phái (tactu_muctieu Vân Mộng Cốc, tactu_kynang Thục Sơn / Đào Hoa): đọc hiệu ứng lỗi coi như đã có
        moitruong = self.moitruong

        def thieu(idhieuung):
            return not moitruong.get_is_cohieuungs((idhieuung,), macdinh = True, diachicosothongtinnhanvat = diachi, is_hieuungcoloi = 1)

        thieus = []
        if tenmonphai == "vanmongcoc":
            is_canngancham, is_cankimcham = self._loaichamcanbuff(moitruong.get_tenmonphai(diachi), moitruong.get_idloaivukhi(diachi))
            if is_canngancham and moitruong.get_is_kynangdahoc(VITRIKYNANG_NGANCHAMDOACH) and thieu(HIEUUNGKYNANG_NGANCHAMDOACH):
                thieus.append("Ngân Châm Độ Ách")
            if is_cankimcham and moitruong.get_is_kynangdahoc(VITRIKYNANG_KIMCHAMDOACH) and thieu(HIEUUNGKYNANG_KIMCHAMDOACH):
                thieus.append("Kim Châm Độ Ách")
            if moitruong.get_is_kynangdahoc(VITRIKYNANG_CUONGTHETHUAT) and thieu(HIEUUNGKYNANG_CUONGTHETHUAT):
                thieus.append("Cường Thể Thuật")
        elif tenmonphai == "thucson":
            if moitruong.get_is_kynangdahoc(VITRIKYNANG_TIEUCHUTHIEN) and thieu(HIEUUNGKYNANG_NOIKHANG):
                thieus.append("Tiểu Chu Thiên")
        elif tenmonphai == "daohoanguyen" and not moitruong.is_nietban:
            if moitruong.get_is_kynangdahoc(VIRIKYNANG_HOTHEKIMCANG) and thieu(HIEUUNGKYNANG_HOTHEKIMCANG):
                thieus.append("Hộ Thể Kim Cang")
        return thieus

    def _ghitrangthaibufftoanbang(self, trangthai):
        s = self._bufftoanbang
        if trangthai != s["trangthai"]:
            s["trangthai"] = trangthai
            if trangthai:
                self.moitruong._inlog(f"[BUFF TOÀN BANG] {trangthai}")

    def action_bufftoanbang(self):
        # Chế độ buff toàn bang (người dùng 2026-11-28, làm lại bản gỡ 02/11): đứng buff cho người đi phó bản tổ đội đơn (Đoạt Bảo Mã
        # Tặc...). Chưa có nhóm thì đồng ý lời mời của BẤT KỲ AI (bản cũ chỉ nhận người trong todoi.json); trong nhóm thì để luật kỹ năng
        # của phái buff thành viên (cần bật Tự động sử dụng kỹ năng, buff theo tầm, không chạy tới); không còn thành viên nào thiếu buff
        # (đã thấy đủ buff, hoặc vào nhóm / khuất tầm nhìn quá THOIGIANBUFFTOANBANGCHOTHANHVIEN giây) thì tự rời, mình là trưởng nhóm thì
        # nhường quyền trước (trưởng nhóm rời = giải tán cả nhóm). Chỉ Vân Mộng Cốc / Thục Sơn / Đào Hoa (Aegis), ngoài phó bản / chiến
        # trường / đội phó bản / Lăng Ly Sơn. -> True khi chế độ đang lo nhóm (Tổ đội tự động bỏ lượt này)
        if not self._is_chedobufftoanbang:
            return False
        moitruong = self.moitruong
        tenmonphai = moitruong.get_tenmonphai()
        if tenmonphai not in ("vanmongcoc", "thucson") and not (tenmonphai == "daohoanguyen" and not moitruong.is_nietban):
            self._ghitrangthaibufftoanbang("phái này không có buff nhóm, chế độ không chạy")
            return False
        idbando = moitruong.get_idbandohientai()
        if idbando in BANDOPHOBANs or idbando == BANDO_CHIENTRUONG or self.get_is_giunhomlanglyson() or self.get_is_dangtrongdoiphoban():
            self._ghitrangthaibufftoanbang("")
            return False
        s = self._bufftoanbang
        now = time.time()
        # Đọc toàn bộ đối tượng xung quanh khá tốn: 0.5s xét 1 lần như Tổ đội tự động
        if now - s.get("lucxet", 0.) < 0.5:
            return True
        s["lucxet"] = now
        s["boquas"] = {i: t for i, t in s.get("boquas", {}).items() if t > now}
        idtoi = moitruong.get_idnguoichoi()

        if not moitruong.get_is_dangnamtrongnhom():
            s.update(lucvaonhom = 0., daxongs = {}, lucthays = {}, lucdudieukien = 0.)
            ids = [i for i in moitruong.get_idsloimoinhom() if i != idtoi and i not in s["boquas"]]
            if ids:
                self._ghitrangthaibufftoanbang(f"đồng ý lời mời nhóm của {self._tenidnguoichoi(ids[0])} ({ids[0]})")
                moitruong.action_kiemtravadongyloimoinhom(ids[:1])
            else:
                self._ghitrangthaibufftoanbang("chờ lời mời nhóm")
            return True

        if not s["lucvaonhom"]:
            s["lucvaonhom"] = now
        idtruongnhom = moitruong.get_idnguoichoitruongnhom()
        thanhviens = [i for i in (moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if i != idtoi]

        # Thành viên trong tầm nhìn: xét buff thiếu. Khác chế độ PK (game không cho buff) / đã chết thì không tính là đã xong
        diachis = {}
        for diachi in moitruong.get_diachinhanvattontais():
            if moitruong.get_is_nguoichoi(diachi):
                idxet = moitruong.get_idnguoichoi(diachi)
                if idxet in thanhviens:
                    diachis[idxet] = diachi
        canbuffs = {}
        for i in thanhviens:
            diachi = diachis.get(i)
            if not diachi or moitruong.get_khoangcach(diachi) >= KHOANGCACHTOANMANHINH:
                continue
            s["lucthays"][i] = now
            if moitruong.get_is_nhanvatdachet(diachi) or self._is_khacmaupkdongdoi(diachi):
                canbuffs[i] = ["(chết / khác chế độ PK)"]
                continue
            thieus = self._buffthieucuathanhvien(diachi, tenmonphai)
            if thieus:
                canbuffs[i] = thieus
            else:
                s["daxongs"].setdefault(i, now)

        def ten(i):
            # Người lạ không chạy bot: lấy tên đối tượng đang thấy, không thì ID
            if i in diachis:
                return moitruong.get_tendoituong(diachis[i]) or str(i)
            if i == idtoi:
                return "mình"
            return self._tenidnguoichoi(i)

        def is_boqua(i):
            # Chưa từng thấy từ lúc vào nhóm / đã khuất quá lâu mà chưa xong
            return now - max(s["lucthays"].get(i, 0.), s["lucvaonhom"]) > THOIGIANBUFFTOANBANGCHOTHANHVIEN

        choids = [i for i in thanhviens if i in canbuffs or (i not in s["daxongs"] and not is_boqua(i))]
        is_quahan = now - s["lucvaonhom"] > THOIGIANBUFFTOANBANGTOIDA
        if choids and not is_quahan:
            s["lucdudieukien"] = 0.
            mota = ", ".join(f"{ten(i)}: {', '.join(canbuffs[i])}" if i in canbuffs
                             else f"{ten(i)}: chưa thấy" for i in choids)
            canhbao = "" if self._is_tudongsudungkynang else " — CHƯA BẬT Tự động sử dụng kỹ năng, không buff được"
            self._ghitrangthaibufftoanbang(f"đang buff nhóm {ten(idtruongnhom)}: {mota}{canhbao}")
            return True
        # Đủ điều kiện rời: giữ liên tục THOIGIANBUFFTOANBANGGIU giây (bảng hiệu ứng người khác cập nhật trễ ngay sau khi buff)
        if not s.get("lucdudieukien"):
            s["lucdudieukien"] = now
        if now - s["lucdudieukien"] < THOIGIANBUFFTOANBANGGIU and not is_quahan:
            return True
        if now - s["lucroi"] < 1.5:
            return True
        s["lucroi"] = now
        lydo = "ở nhóm quá lâu" if is_quahan else ("nhóm không còn ai" if not thanhviens else "không còn ai cần buff")
        if idtruongnhom == idtoi and thanhviens:
            # Trưởng nhóm rời = giải tán: nhường quyền trước, lượt sau mới rời
            idnhan = next((i for i in thanhviens if i in diachis), thanhviens[0])
            self._ghitrangthaibufftoanbang(f"{lydo}, nhường trưởng nhóm cho {ten(idnhan)} rồi rời")
            moitruong.action_nhuongquyentruongnhom(idnhan)
            return True
        self._ghitrangthaibufftoanbang(f"{lydo}, rời nhóm {ten(idtruongnhom)}")
        if idtruongnhom and idtruongnhom != idtoi:
            s["boquas"][idtruongnhom] = now + THOIGIANBUFFTOANBANGBOQUAMOI
        moitruong.action_thoatkhoinhom()
        return True

    def action_tudongtodoi(self):
        # Lăng Ly Sơn đang giải tán tổ đội cũ (tactu_langlyson_xq): tạm nghỉ, còn trong nhóm thì rời; xong thì lập nhóm mới như thường
        if self.action_roinhomlanglyson():
            return
        # Đoạt Bảo Mã Tặc chỉ đi nhóm 1 người (tactu_matac_xq tự lo rời / lập nhóm): Tổ đội tự động nghỉ suốt lúc đang bật
        if self._matac:
            return
        # Chế độ buff toàn bang lo nhóm (nhận mời bất kỳ ai, buff xong thì rời): Tổ đội tự động nghỉ
        if self.action_bufftoanbang():
            return
        if not self.get_is_tudongtodoi():
            return
        # Đội phó bản đang chạy giữ mình (trưởng đội / thành viên): đội phó bản tự lo nhóm, Tổ đội tự động nghỉ tới khi đội xong
        if self.get_is_dangtrongdoiphoban():
            return

        # Quét người chơi xung quanh khá tốn (đọc bộ nhớ toàn bộ đối tượng), thao tác nhóm cũng có delay riêng nên không cần chạy liên tục
        if time.time() - self._thoidiemxulytodoigannhat < 0.5:
            return
        self._thoidiemxulytodoigannhat = time.time()
        # Chỉ nhánh "chưa có nhóm" bên dưới ghi lại danh sách được đồng ý
        self._dongytodoitudong = (0., [])

        idnguoichoi = self.moitruong.get_idnguoichoi()
        is_dangtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        idbandohientai = self.moitruong.get_idbandohientai()

        # Nhóm todoi.json có mình, trừ người đang đi đội phó bản
        danhsachuutientodoi = self._laynhomtodoicuatoi()

        if not danhsachuutientodoi:
            return

        # Lăng Ly Sơn đang đi dở (đã vào phó bản, chưa lĩnh thưởng xong): không rời nhóm / nhường quyền trưởng nhóm (phó bản giữ theo tổ
        # đội, người đi phó bản phải là trưởng nhóm), vẫn nhận lời mời / mời người rớt nhóm vào lại
        is_giunhom = self.get_is_giunhomlanglyson()

        # Thành viên vãng lai: ngoài phó bản / chiến trường thì giữ slot / nhường slot theo nhóm chính (_xulyvanglai)
        if idnguoichoi in layvanglaitodois() and idbandohientai not in BANDOPHOBANs and idbandohientai != BANDO_CHIENTRUONG \
                and not is_giunhom:
            if self._xulyvanglai(danhsachuutientodoi, self._laybotkhacs(), idbandohientai):
                return
        else:
            self._vanglai["lucvaonhom"] = 0.
            self._ghitrangthaivanglai("")

        if idbandohientai == BANDO_CHIENTRUONG and not is_dangtrongnhom:
            self.moitruong.action_kiemtravadongyloimoinhom(list(self.get_idnguoiquens()))

        # Thứ hạng: số nhỏ = ưu tiên làm trưởng nhóm cao hơn
        xephang_map = {id_: i for i, id_ in enumerate(danhsachuutientodoi)}
        xephangcuatoi = xephang_map[idnguoichoi]

        danhsachthanhviens = self.moitruong.get_danhsachidnguoichoithanhviennhoms() if is_dangtrongnhom else []

        # 2 nhóm cùng tồn tại trên 1 bản đồ: nhóm có hạng tốt nhất thấp hơn rời nhóm để vào nhóm hạng cao hơn
        cacnhomcungbandos, nguoichoilecungbandos = self._laythongtintodoicungbando(idbandohientai, xephang_map)
        idtruongnhomcuatoi = self.moitruong.get_idnguoichoitruongnhom() if is_dangtrongnhom else 0
        # Nhóm "khác" mà thành viên trùng với mình / nhóm mình là cùng 1 nhóm nhìn qua dữ liệu cũ
        # (vd: trưởng nhóm vừa dis, cửa sổ đó chưa kịp cập nhật vẫn ghi mình là trưởng nhóm) => không tính là nhóm khác
        thanhviennhomcuatois = set(danhsachthanhviens) | {idnguoichoi}
        cacnhomkhacs = {idtn: v for idtn, v in cacnhomcungbandos.items()
                        if idtn != idtruongnhomcuatoi and not (v[1] & thanhviennhomcuatois)}
        # Nhóm khác đã đủ người (Aegis 5): không rời nhóm mình / không xin vào nhóm đó. Trước đây vẫn gửi "team + <trưởng nhóm>" mỗi 5s,
        # trưởng nhóm cứ hiện "Nhóm đã đạt thành viên tối đa (5)" (ảnh 2026-11-26)
        sotoida = self.moitruong.get_soluongthanhviennhomtoida()
        nguoinhomdays = set()
        for idtn, v in list(cacnhomkhacs.items()):
            if len(v[1]) >= sotoida:
                nguoinhomdays |= v[1] | {idtn}
                del cacnhomkhacs[idtn]
        idtruongnhomtotnhat = min(cacnhomkhacs, key = lambda idtn: cacnhomkhacs[idtn][0]) if cacnhomkhacs else 0
        if is_dangtrongnhom and idtruongnhomtotnhat:
            hangnhomcuatoi = min(xephang_map.get(id_, len(xephang_map)) for id_ in thanhviennhomcuatois)
            if cacnhomkhacs[idtruongnhomtotnhat][0] < hangnhomcuatoi:
                if self._nhomuutiencaohon[0] != idtruongnhomtotnhat:
                    self._nhomuutiencaohon = (idtruongnhomtotnhat, time.time())
                # Phó bản không bao giờ tự rời (trưởng nhóm rời = giải tán, cả đội bị đá ra); ngoài ra phải thấy liên tục 3s mới rời
                if idbandohientai not in BANDOPHOBANs and not is_giunhom and time.time() - self._nhomuutiencaohon[1] > 3. \
                        and time.time() - self._thoidiemroinhomtodoigannhat > 3.:
                    self._thoidiemroinhomtodoigannhat = time.time()
                    print(f"[TỔ ĐỘI] Nhóm khác cùng bản đồ ưu tiên cao hơn (trưởng nhóm {idtruongnhomtotnhat}) => rời nhóm để vào nhóm đó")
                    self.moitruong.action_thoatkhoinhom()
                return
        self._nhomuutiencaohon = (0, 0.)
        if not is_dangtrongnhom and idtruongnhomtotnhat:
            # Chỉ nhận lời mời / xin vào nhóm ưu tiên cao nhất, tránh bị nhóm cũ mời lại
            self._dongytodoitudong = (time.time(), [idtruongnhomtotnhat])
            self.moitruong.action_kiemtravadongyloimoinhom([idtruongnhomtotnhat])
            if time.time() - self._thoidiemtodoigannhat_map.get(idtruongnhomtotnhat, 0) > 5.0:
                self.moitruong.action_moihoacxinvaonhom(idtruongnhomtotnhat)
                self._thoidiemtodoigannhat_map[idtruongnhomtotnhat] = time.time()
                self._thoidiemtodoigannhat_map = donbangthoidiem(self._thoidiemtodoigannhat_map, 120.)
            return

        danhsachxungquanhs = self.moitruong.get_danhsachidnguoichoixungquanhs()

        # Loại chính mình và trùng lặp
        dongdoicanxulys = []
        for id_ in danhsachxungquanhs:
            # Người đang ở nhóm khác đã đủ người: mời không được, xin vào cũng không được => bỏ qua
            if id_ != idnguoichoi and id_ in xephang_map and id_ not in dongdoicanxulys and id_ not in nguoinhomdays:
                dongdoicanxulys.append(id_)

        if not dongdoicanxulys and not is_dangtrongnhom:
            return

        # Cùng 1 nhóm thì hạn chế rời/giải tán nhóm (giải tán sẽ đá văng cả đội ra khỏi phó bản): ưu tiên mời rồi nhường quyền.
        # Trưởng nhóm là người ngoài danh sách tổ đội thì cứ ở lại nhóm, không rời để ghép lại như trước.

        idnguoichoixephangcaonhat = min(dongdoicanxulys + [idnguoichoi], key = lambda id_: xephang_map[id_])

        if is_dangtrongnhom and self.moitruong.get_is_truongnhom():
            for thanhvien_id in danhsachthanhviens:
                if xephang_map.get(thanhvien_id, len(xephang_map)) < xephangcuatoi and not is_giunhom:
                    self.moitruong.action_nhuongquyentruongnhom(thanhvien_id)
                    return

            # Đồng đội hạng cao hơn ở gần nhưng chưa trong nhóm: MỜI vào (vào rồi sẽ được nhường quyền ở vòng sau).
            # Chỉ khi nhóm chỉ có mình mình (rời không đá ai) và mời quá 15s không được (họ đang ở nhóm khác) mới rời để xin vào nhóm họ.
            if idnguoichoixephangcaonhat != idnguoichoi and idnguoichoixephangcaonhat not in danhsachthanhviens:
                if self._idmoihangcaohon != idnguoichoixephangcaonhat:
                    self._idmoihangcaohon = idnguoichoixephangcaonhat
                    self._thoidiembatdaumoihangcaohon = time.time()
                if len(danhsachthanhviens) <= 1 and time.time() - self._thoidiembatdaumoihangcaohon > 15. and idbandohientai not in BANDOPHOBANs \
                        and not is_giunhom:
                    self._idmoihangcaohon = 0
                    self.moitruong.action_thoatkhoinhom()
                    return
            else:
                self._idmoihangcaohon = 0

            if len(danhsachthanhviens) < self.moitruong.get_soluongthanhviennhomtoida():
                # Mời cả người đang lẻ cùng bản đồ (vd: vừa rời nhóm hạng thấp hơn) dù chưa đứng gần. Mời lần lượt: trước đây mỗi lượt mời
                # 1 người khác nên lời mời trước bị đè, người trước bấm đồng ý thành "xin vào nhóm" (không ai nhận) => chờ 5s mời lại, nhóm
                # đông vào rất chậm
                chuavaos = [i for i in dongdoicanxulys + [id_ for id_ in nguoichoilecungbandos if id_ not in dongdoicanxulys]
                            if i not in danhsachthanhviens]
                botkhacs = self._laybotkhacs()
                chuavaos = self._locvanglaimoi(chuavaos, botkhacs)
                if chuavaos:
                    sansangs, _ = self._moilanluot(self._moiluottodoitudong, chuavaos, botkhacs)
                    # Luồng tổ đội nhanh (_moitieptodoitudong) mời ngay người kế trong danh sách này khi người đang mời đã vào
                    self._moiluottodoitudong.update(sansangs = list(sansangs), lucsansang = time.time())
                    self._thoidiemtodoigannhat_map = donbangthoidiem(self._thoidiemtodoigannhat_map, 120.)
                else:
                    self._moiluottodoitudong.update(dangmoi = 0, sansangs = [])

        elif not is_dangtrongnhom:
            self._dongytodoitudong = (time.time(), list(danhsachuutientodoi))
            self.moitruong.action_kiemtravadongyloimoinhom(danhsachuutientodoi)

            if idnguoichoixephangcaonhat != idnguoichoi:
                if time.time() - self._thoidiemtodoigannhat_map.get(idnguoichoixephangcaonhat, 0) > 5.0:
                    self.moitruong.action_moihoacxinvaonhom(idnguoichoixephangcaonhat)
                    self._thoidiemtodoigannhat_map[idnguoichoixephangcaonhat] = time.time()
                    self._thoidiemtodoigannhat_map = donbangthoidiem(self._thoidiemtodoigannhat_map, 120.)

    def action_tudongphucsinh(self):
        # Trước đây vòng while + sleep(1) chặn luồng phụ tới 30s mỗi lần chết; giờ chỉ ghi nhận lúc bắt đầu chết, đủ thời gian mới phục sinh
        self.moitruong.action_dongcuasosauphucsinh()
        if not self.moitruong.get_is_nhanvatdachet():
            self._thoidiembatdauchet = 0.
            return
        if not self._is_tudongphucsinh:
            return
        if not self._thoidiembatdauchet:
            self._thoidiembatdauchet = time.time()
        if time.time() - self._thoidiembatdauchet < THOIGIANCHOTRUOCKHIPHUCSINH:
            return
        if self.moitruong.action_phucsinh():
            self._xoatrangthaisaukhichet()

    def action_tudongdoimaupk(self):
        if self._is_tudongdoimaupk and self.moitruong.get_idbandohientai() not in BANDOFARMs:
            if time.time() - self._thoidiemdoimaupkgannhat > 5.:
                self._thoidiemdoimaupkgannhat = time.time()
                self.action_batpk()

    def action_tudonghoibangphai(self):
        # Đang PK bang: hỏi bang người chơi xung quanh ("desc user") để get_is_cungbang so được; chưa biết thì coi như cùng bang, không đánh
        if self.moitruong.get_idmaupk() == MAUPK_BANG:
            self.moitruong.action_hoibangphai()

    def action_batpk(self):
        self.moitruong.action_doimaupk(MAUPK_BANG)

    def action_tatpk(self):
        self.moitruong.action_doimaupk(MAUPK_HOABINH)

    def action_chantangcapdo(self):
        if self._is_chantangcapdo:
            self.moitruong.action_chantangcapdo()
        else:
            self.moitruong.action_bochantangcapdo()
        self._tudongquayso()
        self._tudongtangcap()

    def _tudongquayso(self):
        # Cấp nhân vật tăng (bot tự tăng hay người chơi bấm) thì quay vòng số ở Bảo Điển, mỗi cấp tăng 1 lượt, chỉ khi cấp không quá
        # CAPTOIDAQUAYSO (cao hơn thì bỏ lượt còn chờ). Từng lượt: gửi lần lượt LENHQUAYSOLENCAPs (máy chủ chọn món), Bảo Điển để mở (người
        # dùng xem phần thưởng); trước lệnh cuối ("Khởi động Game") xoá tên món cũ, chờ máy chủ trả tên món (tối đa THOIGIANCHODONGVONGQUAY giây) rồi
        # đóng vòng quay, mới tới lượt kế. Còn đồ chờ cộng vào túi (hoạt ảnh chưa quay tới món trúng) thì chưa đóng, chưa quay lượt kế: đóng
        # hay hiện lại cửa sổ lúc đó là client mất đồ (máy chủ vẫn ghi nhận, phải thoát game vào lại). Lần đầu đọc được cấp chỉ ghi nhớ
        moitruong = self.moitruong
        capdo = moitruong.get_capdonhanvat()
        if capdo:
            if self._capdoquaysotruoc and capdo > self._capdoquaysotruoc:
                self._soluotquaysocho += capdo - self._capdoquaysotruoc
                moitruong._inlog(f"[QUAY SỐ] lên cấp {self._capdoquaysotruoc} -> {capdo}: còn {self._soluotquaysocho} lượt quay")
            self._capdoquaysotruoc = capdo
            if capdo > CAPTOIDAQUAYSO and self._soluotquaysocho:
                moitruong._inlog(f"[QUAY SỐ] cấp {capdo} > {CAPTOIDAQUAYSO}: không quay được, bỏ {self._soluotquaysocho} lượt")
                self._soluotquaysocho = 0
        danghien, tenmon, is_chocongdo = moitruong.get_vongquayso()
        if self._thoidiemguiquayso:
            if is_chocongdo:
                if danghien and time.time() - self._thoidiemguiquayso < THOIGIANCHOCONGDOVONGQUAY:
                    return
                # Quá lâu hoặc cửa sổ đã bị đóng: không đóng nữa (để hoạt ảnh tự chạy nốt nếu còn hiện), lượt kế chờ đồ cộng xong
                moitruong._inlog(f"[QUAY SỐ] {tenmon or 'món trúng'} chưa được cộng vào túi client (cửa sổ {'còn' if danghien else 'đã'} "
                                 f"{'hiện' if danghien else 'đóng'}), còn {self._soluotquaysocho} lượt")
                self._thoidiemguiquayso = 0.
                return
            if tenmon:
                moitruong._inlog(f"[QUAY SỐ] máy chủ trả {tenmon}, còn {self._soluotquaysocho} lượt")
            elif time.time() - self._thoidiemguiquayso >= THOIGIANCHODONGVONGQUAY:
                moitruong._inlog(f"[QUAY SỐ] {THOIGIANCHODONGVONGQUAY:.0f}s không thấy kết quả, còn {self._soluotquaysocho} lượt")
            else:
                return
            self._thoidiemguiquayso = 0.
            if danghien:
                moitruong.action_dongvongquayso()
            return
        if not self._lenhquaysochos:
            # Lượt trước còn đồ chờ cộng: "zgdict rock open" hiện lại cửa sổ sẽ xoá danh sách món chờ
            if not self._soluotquaysocho or (danghien and is_chocongdo):
                return
            self._soluotquaysocho -= 1
            self._lenhquaysochos = list(LENHQUAYSOLENCAPs)
        if time.time() - self._thoidiemlenhquayso < THOIGIANGIUALENHQUAYSO:
            return
        caulenh = self._lenhquaysochos[0]
        if not moitruong.action_thucthicaulenh(caulenh):
            return
        self._lenhquaysochos.pop(0)
        self._thoidiemlenhquayso = time.time()
        if not self._lenhquaysochos:
            moitruong.action_xoamonvongquayso()
            self._thoidiemguiquayso = time.time()

    def _is_dangquayso(self):
        # Còn lượt quay số chưa xong: tự tăng cấp chờ, không thì lên cấp liền bị dồn lượt
        return bool(self._soluotquaysocho or self._lenhquaysochos or self._thoidiemguiquayso)

    def _tudongtangcap(self):
        # Tự tăng cấp tới _captudongtangcaptoida: kinh nghiệm hiện có >= kinh nghiệm cần thì gửi "gift upgrade" (nút Thăng Cấp ở bảng Nhân
        # Vật, dò bằng log [LỆNH GAME]). Gửi lệnh trực tiếp nên chạy được cả khi đang Chặn tăng cấp độ (chỉ chặn hộp hỏi lên cấp).
        # Niết Bàn: "gift upgrade" chỉ làm máy chủ gửi hộp Yes/No hỏi lại, nút Xác Nhận gửi "gift ! upgrade" (dò 2026-11-02 ở hộp
        # TG_CUASOYESNO + 0x7C) => gửi thẳng lệnh đó, không hiện hộp.
        # Mỗi lần gửi cách nhau THOIGIANGUILAITANGCAP giây (chờ máy chủ trừ kinh nghiệm / tăng cấp)
        if not self._is_tudongtangcap or time.time() - self._thoidiemtudongtangcap < THOIGIANGUILAITANGCAP or self._is_dangquayso():
            return
        moitruong = self.moitruong
        capdo = moitruong.get_capdonhanvat()
        kinhnghiem, kinhnghiemcan = moitruong.get_kinhnghiem(), moitruong.get_kinhnghiemcanlencap()
        # Nhân vật mới tạo là cấp 0 (kéo gà A-Z): chỉ bỏ khi không đọc được cấp (False / None), không bỏ cấp 0
        if capdo is False or capdo is None or capdo >= self._captudongtangcaptoida or kinhnghiem is None or not kinhnghiemcan                 or kinhnghiem < kinhnghiemcan:
            return
        self._thoidiemtudongtangcap = time.time()
        caulenh = "gift ! upgrade" if moitruong.is_nietban else "gift upgrade"
        if moitruong.action_thucthicaulenh(caulenh):
            moitruong._inlog(f"[TĂNG CẤP] cấp {capdo}, kinh nghiệm {kinhnghiem} / {kinhnghiemcan}: gửi {caulenh} (tự tăng tới cấp {self._captudongtangcaptoida})")
            phatam(f"Tăng lên cấp {capdo + 1}", is_block = False)

    def _get_loaikhaikhoang(self):
        # Theo pháp bảo đang đeo: "Liềm" = hái dược, "Cuốc" = khai khoáng. Không đeo cái nào (đang đổi pháp bảo không hư hỏng
        # lúc máu thấp, hoặc tháo) thì giữ loại lần trước; "" = chưa biết lần nào
        tenphapbao = self.moitruong.get_tenphapbaohientai() or ""
        loai = ""
        if PHAPBAOHAIDUOC in tenphapbao:
            loai = "haiduoc"
        elif PHAPBAOKHAIKHOANG in tenphapbao:
            loai = "khaikhoang"
        if loai and loai != self._loaikhaikhoang:
            self._loaikhaikhoang = loai
            self.moitruong._inlog(f"[KHAI KHOÁNG] Pháp bảo {tenphapbao} -> {'Hái dược' if loai == 'haiduoc' else 'Khai khoáng'}")
        return self._loaikhaikhoang

    @staticmethod
    def _is_doituongkhaikhoang(tendoituong, loai):
        is_duoc = tendoituong in NGUYENLIEULUYENDONs
        is_khoang = CHUTENKHOANG in tendoituong
        if loai == "haiduoc":
            return is_duoc
        if loai == "khaikhoang":
            return is_khoang
        return is_duoc or is_khoang

    def action_tudongkhaikhoang(self):
        if not self._is_tudongkhaikhoang:
            self._yeucaukhaikhoang = None
            self._diachicosokhaikhoang = 0
            return

        idbandohientai = self.moitruong.get_idbandohientai()

        if idbandohientai != self._idbandolanquetkhaikhoangtruoc:
            self._idkhoangbiloi_map.clear()
            self._duongtoikhoang_map.clear()
            self._idbandolanquetkhaikhoangtruoc = idbandohientai

        if self.moitruong._get_is_dangvankhitrongame():
            # Đào khoáng / hái dược không đổi tư thế mà là vận khí: "look" vừa gửi đã có tác dụng => đếm lại số lần look, không tính giờ.
            # Chỉ tính vận khí thật của game, không tính khoảng chờ action_chovankhi (look không ăn thì vẫn phải đếm tới SOLANLOOKKHOANGTOIDA)
            self._solanlookkhoang = 0
            self._thoidiembatdautheokhoang = time.time()
        elif self.moitruong.get_is_dangvankhi():
            self._thoidiembatdautheokhoang = time.time()
        if self.moitruong.get_is_dangvankhi() or self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_nhanvatdachet() or time.time() - self._thoidiemtamngungdichuyensudungkynang < 0.:
            self._yeucaukhaikhoang = None
            self._diachicosokhaikhoang = 0
            return

        if 0:
            pass
        else:
            idcanxoas = [k for k, v in self._idkhoangbiloi_map.items() if time.time() - v > THOIGIANBOQUAKHOANG]
            for k in idcanxoas:
                del self._idkhoangbiloi_map[k]
            idcanxoas = [k for k, v in self._duongtoikhoang_map.items() if time.time() - v[1] > THOIGIANNHODUONGKHOANG]
            for k in idcanxoas:
                del self._duongtoikhoang_map[k]

            i = -1
            diachidoituonggannhat = None
            khoangcachgannhat = KHOANGCACHTOIDAHOPLE + 1
            loai = self._get_loaikhaikhoang()

            while True:
                i += 1
                diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachidoituong: break

                tendoituong = self.moitruong.get_tendoituong(diachidoituong)
                if tendoituong and self._is_doituongkhaikhoang(tendoituong, loai):
                    iddoituong = self.moitruong.get_iddoituong(diachidoituong)
                    if iddoituong <= 0: continue
                    if iddoituong in self._idkhoangbiloi_map: continue

                    khoangcach = self.moitruong.get_khoangcach(diachidoituong)
                    if khoangcach > KHOANGCACHTOANMANHINH: continue
                    # Khoáng sau vách / bị vật cản bao kín: bỏ luôn, chọn khoáng khác đi tới được
                    if not self._is_khoangtoiduoc(diachidoituong, iddoituong, khoangcach): continue

                    if khoangcach < khoangcachgannhat:
                        khoangcachgannhat = khoangcach
                        diachidoituonggannhat = diachidoituong
            if diachidoituonggannhat:
                self._xuly_daokhoang(diachidoituonggannhat, khoangcachgannhat)
            else:
                self._idkhoangdangtheo = 0
                self._yeucaukhaikhoang = None
                self._diachicosokhaikhoang = 0

    def _xuly_lotrinh_chung(self, target_x, target_y, index_var_name, len_list):
        i = -1
        best_mineral_addr = 0
        min_char_dist = 9999.

        while True:
            i += 1
            diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituong: break
            tendoituong = self.moitruong.get_tendoituong(diachidoituong)
            if tendoituong and ("Khoáng" in tendoituong or "KhoÃ¡ng" in tendoituong):
                iddoituong = self.moitruong.get_iddoituong(diachidoituong)
                if iddoituong <= 0 or iddoituong in self._idkhoangbiloi_map: continue
                mx, my = self.moitruong.get_toado(diachidoituong)

                if math.dist((mx, my), (target_x, target_y)) <= 12.0:
                    char_dist = self.moitruong.get_khoangcach(diachidoituong)
                    if not self._is_khoangtoiduoc(diachidoituong, iddoituong, char_dist): continue
                    if char_dist < min_char_dist:
                        min_char_dist = char_dist
                        best_mineral_addr = diachidoituong

        if best_mineral_addr:
            self._xuly_daokhoang(best_mineral_addr, min_char_dist)
        else:
            self._xuly_chaylotrinh(target_x, target_y, index_var_name, len_list)

    def _is_khoangtoiduoc(self, diachikhoang, idkhoang, khoangcach):
        # Tìm đường 1 lần trên lưới vật cản (+ ô học được) tới cách khoáng KHOANGCACHDUNGDAOKHOANG ô, nhớ THOIGIANNHODUONGKHOANG giây theo
        # id (khoáng đứng yên). Không có đường / phải vòng quá xa (như quái: HESODUONGVONGTOIDA) thì bỏ khoáng THOIGIANBOQUAKHOANG giây
        if khoangcach < KHOANGCACHDAOKHOANG:
            return True
        nho = self._duongtoikhoang_map.get(idkhoang)
        if nho is None:
            sobuoc = self.moitruong.get_sobuocduongtoi(*self.moitruong.get_toado(diachikhoang), KHOANGCACHDUNGDAOKHOANG)
            nho = self._duongtoikhoang_map[idkhoang] = (sobuoc, time.time())
            lydo = None
            if sobuoc is None:
                lydo = "không có đường tới (vật cản)"
            elif sobuoc > khoangcach * HESODUONGVONGTOIDA + SOBUOCDUONGVONGCONGTHEM:
                lydo = f"đường vòng {sobuoc} bước cho {khoangcach:.1f} ô"
            if lydo:
                self.moitruong._inlog(f"[KHAI KHOÁNG] Bỏ khoáng {hex(idkhoang)} {self.moitruong.get_tendoituong(diachikhoang)} "
                                      f"{self.moitruong.get_toado(diachikhoang)}: {lydo}")
                self._idkhoangbiloi_map[idkhoang] = time.time()
                return False
        return nho[0] is not None

    def _boquakhoang(self, idkhoang, lydo):
        self.moitruong._inlog(f"[KHAI KHOÁNG] Bỏ khoáng {hex(idkhoang)} {THOIGIANBOQUAKHOANG:.0f}s: {lydo}")
        canhbao(self.moitruong, "Khoáng lỗi, bỏ qua", is_block = False)
        self._idkhoangbiloi_map[idkhoang] = time.time()
        self._idkhoangdangtheo = 0
        self._yeucaukhaikhoang = None
        self._diachicosokhaikhoang = 0
        self._thoidiemhetgiukhaikhoang = 0.

    def _xuly_daokhoang(self, diachikhoang, khoangcach):
        id_min = self.moitruong.get_iddoituong(diachikhoang)
        now = time.time()

        if id_min != self._idkhoangdangtheo:
            self._idkhoangdangtheo = id_min
            self._thoidiembatdautheokhoang = now
            self._khoangcachgannhatkhoang = khoangcach
            self._solanlookkhoang = 0
            self.moitruong._inlog(f"[KHAI KHOÁNG] Theo khoáng {hex(id_min)} {self.moitruong.get_tendoituong(diachikhoang)} "
                                  f"{self.moitruong.get_toado(diachikhoang)} cách {khoangcach:.1f} ô")

        self._diachicosokhaikhoang = diachikhoang

        if khoangcach >= KHOANGCACHDAOKHOANG:
            self._solanlookkhoang = 0
            if khoangcach < self._khoangcachgannhatkhoang - KHOANGCACHGANTHEMKHOANG:
                # Đang gần thêm: tính lại giờ
                self._khoangcachgannhatkhoang = khoangcach
                self._thoidiembatdautheokhoang = now
            elif now - self._thoidiemchondikhaikhoang > 1.5:
                # Bộ điều phối di chuyển đang làm việc khác (đánh quái, nhặt đồ, giữ khoảng cách...): không tính giờ, trước đây đánh quái quá
                # 10s cạnh khoáng là báo "Khoáng lỗi" dù chưa hề đi tới
                self._thoidiembatdautheokhoang = now
            elif now - self._thoidiembatdautheokhoang > THOIGIANKHONGGANKHOANG:
                self._boquakhoang(id_min, f"{THOIGIANKHONGGANKHOANG:.0f}s đi mà không gần thêm (còn {khoangcach:.1f} ô, "
                                          f"gần nhất {self._khoangcachgannhatkhoang:.1f} ô), có thể vướng vật cản")
                return

            mx_move, my_move = self.moitruong.get_toado(diachikhoang)
            # is_khongcatgoc: đi đường bot tự tìm theo lưới vật cản (action_dikhongcatgoc), không click thẳng vào ô khoáng rồi húc vách
            self._yeucaukhaikhoang = {
                "yeucau": YEUCAUDICHUYENKHAIKHOANG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                "toadodich": (mx_move, my_move),
                "khoangcachtoida": KHOANGCACHDUNGDAOKHOANG,
                "is_khongcatgoc": True,
            }
            return

        self._yeucaukhaikhoang = None
        self._thoidiembatdautheokhoang = now
        # Tới tầm hái: giữ đứng yên, không ra chiêu tới khi look xong vào vận khí (trước đây bật đánh quái thì vừa chạy tới khoáng, chưa
        # kịp look / vận khí đã quay ra đánh quái => look mãi không ăn, báo "Khoáng lỗi"). Hết SOLANLOOKKHOANGTOIDA lần thì _boquakhoang
        self._thoidiemhetgiukhaikhoang = now + THOIGIANGIUKHAIKHOANG
        self.moitruong.action_khoakynang(THOIGIANGIUKHAIKHOANG)
        if self.moitruong.get_idtuthenhanvat() != TUTHENHANVAT_DUNGIM:
            # Đang đánh / đi: chờ đứng im mới look (lúc đào không đổi tư thế mà vận khí, đếm lại ở action_tudongkhaikhoang)
            return
        if now - self._thoidiemkhaikhoanggannhat > 1.0:
            if self._solanlookkhoang >= SOLANLOOKKHOANGTOIDA:
                self._boquakhoang(id_min, f"{SOLANLOOKKHOANGTOIDA} lần look mà vẫn đứng im (cách {khoangcach:.1f} ô)")
                return
            if self.moitruong.action_khaikhoang(id_min):
                self._solanlookkhoang += 1
                # Từ lúc gửi look tới khi máy chủ bật vận khí: coi như đang vận khí (chặn chiêu / di chuyển ngắt việc hái)
                self.moitruong.action_chovankhi(caulenh = "look {}#".format(hex(id_min)).replace("0x", ""), ten = "KHAI KHOÁNG")
            self._thoidiemkhaikhoanggannhat = now

    def _xuly_chaylotrinh(self, tx, ty, index_var_name, len_list):
        self._diachicosokhaikhoang = 0
        self._idkhoangdangtheo = 0

        char_x, char_y = self.moitruong.get_toado()
        dist_to_target = math.dist((char_x, char_y), (tx, ty))

        if dist_to_target <= 3.0:
            current_index = getattr(self, index_var_name)
            setattr(self, index_var_name, (current_index + 1) % len_list)
            self._yeucaukhaikhoang = None
        else:
            self._yeucaukhaikhoang = {
                "yeucau": YEUCAUDICHUYENKHAIKHOANG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                "toadodich": (tx, ty),
                "khoangcachtoida": 0,
                "is_khongcatgoc": True,
            }

    def action_tudongdichientruong(self):
        if not self._is_tudongdichientruong:
            self._hangdoilenhchientruong = []
            return

        if self._hangdoilenhchientruong:
            if time.time() >= self._thoidiemguilenhchientruongtieptheo:
                self.moitruong.action_thucthicaulenh(self._hangdoilenhchientruong.pop(0))
                self._thoidiemguilenhchientruongtieptheo = time.time() + 0.25
            return

        if time.time() - self._thoidiemdichientruonggannhat < 0.5:
            return

        # Đang tự đi phó bản (tactu_langlyson_xq): không kéo về Trương Quả Lão (Chu Quốc (245, 158)), không thì giành đường với phó bản
        # (trưởng đội Phong Yêu Kính ra cạnh Tả Khâu Minh đi bán rác ở Chủ Tiệm Y Dược bị kéo qua kéo lại tại chỗ 2 phút, 2026-11-03)
        if self.get_is_danglanglyson():
            return

        idbandohientai = self.moitruong.get_idbandohientai()
        is_dangnamtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        is_truongnhom = self.moitruong.get_is_truongnhom()

        if idbandohientai == BANDO_CHIENTRUONG:
            if time.time() - self._thoidiemclickchientruonggannhat >= 5.0:
                hwnd = self.moitruong.idcuaso
                x, y = 405, 315
                lparam = (y << 16) | (x & 0xFFFF)

                win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
                time.sleep(0.05)
                win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lparam)

                self._thoidiemclickchientruonggannhat = time.time()
            return

        if idbandohientai == BANDO_CHUQUOC and time.time() - self.moitruong.get_thoidiemthaydoibandogannhat() > 0.5:
            diachinpc = self.moitruong.action_timkiemnhanvat(TRUONGQUALAO)

            if not diachinpc:
                self.moitruong.action_dichuyengiukhoangcachtoidadiem(X_TRUONGQUALAO, Y_TRUONGQUALAO, khoangcachtoida = 3.0)
                self._thoidiemdichientruonggannhat = time.time()
                return

            khoangcach = self.moitruong.get_khoangcach(diachinpc)
            if khoangcach > 9.0:
                self.moitruong.action_dichuyengiukhoangcachtoida(diachinpc, khoangcachtoida = 3.)
                self._thoidiemdichientruonggannhat = time.time()
                return

            idnpc = self.moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                return

            self._thoidiemdichientruonggannhat = time.time()

            hex_id = hex(idnpc).replace("0x", "")
            if is_truongnhom:
                buocs = ("welcome.2", "welcome.3")
            elif is_dangnamtrongnhom:
                buocs = ("welcome.3",)
            else:
                buocs = ("welcome.1", "welcome.3")
            # Gửi bước đầu ngay, các bước sau gửi dần ở các lượt kế tiếp (đầu hàm)
            self._hangdoilenhchientruong = ["tallk {}# {}".format(hex_id, buoc) for buoc in buocs[1:]]
            self.moitruong.action_thucthicaulenh("tallk {}# {}".format(hex_id, buocs[0]))
            self._thoidiemguilenhchientruongtieptheo = time.time() + 0.25

    def action_tudongdaotangbaodo(self):
        self._yeucaudaotangbaodo = None

        if not self._is_tudongdaotangbaodo:
            self._thoidiemhettangbaodogannhat = 0.
            self._doitangbaodo = None
            self._viecbantrangdaobaodo = None
            self._is_dabantrangdaobaodo = False
            self._is_dacatkhodaobaodo = False
            self._vieccatkhodaobaodo = None
            self._is_dacanhbaohettangbaodo = False
            return

        if time.time() < self._thoidiemchodaotangbaodo:
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
            return

        # Đang đổi Lam + Hắc Cầu lấy Tàng Bảo Đồ (tactu_doicau_xq): đổi tới gần đầy hành trang / hết cầu rồi mới đi đào
        if self._doitangbaodo:
            self._xulydoitangbaodo()
            return

        idbandohientai = self.moitruong.get_idbandohientai()
        x_hientai, y_hientai = self.moitruong.get_toado()

        # if time.time() - self._thoidiemhettangbaodogannhat < 60 * 3 and math.dist((x_hientai, y_hientai), (150, 128)) < 3.:
        #     return

        soluongvatphamhanhtrangtoida = self.moitruong.get_soluongvatphamhanhtrangtoida()
        for i in range(soluongvatphamhanhtrangtoida):
            tenvatpham = self.moitruong.get_tenvatphamhanhtrang(i)
            if not tenvatpham or tenvatpham != TANGBAODO:
                continue

            mota = self.moitruong.get_motavatphamhanhtrang(i)
            if not mota: continue

            timthay = re.search(r"Vị trí: \s*(.*?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", mota)
            if timthay:
                # Còn tấm để đào: lần hết sau về lại bán đồ trắng
                self._is_dabantrangdaobaodo = False
                self._viecbantrangdaobaodo = None
                self._is_dacatkhodaobaodo = False
                self._vieccatkhodaobaodo = None
                self._is_dacanhbaohettangbaodo = False
                tenbandotrongmota = timthay.group(1).strip()
                x_dich = int(timthay.group(2))
                y_dich = int(timthay.group(3))

                idbandodich = layidbandotheoten(tenbandotrongmota)

                if idbandodich == idbandohientai:
                    khoangcach = math.sqrt((x_hientai - x_dich) ** 2 + (y_hientai - y_dich) ** 2)
                    if khoangcach < 1.:
                        print(f"[DAOTAOBAODO] Đang đào tại {tenbandotrongmota} ({x_dich}, {y_dich})")
                        iddoituong = self.moitruong.get_iddoituongvatphamhanhtrang(i)
                        if iddoituong:
                            self.moitruong.action_sudungvatpham(iddoituong)
                            self._thoidiemchodaotangbaodo = time.time() + 1.
                    else:
                        self.moitruong.action_tudongtimduong(x_dich, y_dich, idbandodich)
                    return

        # Đang đi tới Chủ Tiệm Tạp Hóa bán đồ trắng thì đừng huỷ đường đi (mỗi lượt gọi lại)
        if not self._viecbantrangdaobaodo and not self._vieccatkhodaobaodo:
            self.moitruong.action_tudongtimduong(0, 0, 0)

        quocgiacanden = None
        soluongvatphamhanhtrangtoida = self.moitruong.get_soluongvatphamhanhtrangtoida()
        for i in range(soluongvatphamhanhtrangtoida):
            tenvatpham = self.moitruong.get_tenvatphamhanhtrang(i)
            if tenvatpham == TANGBAODO:
                mota = self.moitruong.get_motavatphamhanhtrang(i)
                if mota:
                    timthay = re.search(r"Vị trí: \s*(.*?)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", mota)
                    if timthay:
                        tenbandotrongmota = timthay.group(1).strip()
                        quocgiacanden = f"{tenbandotrongmota} Quốc"
                        break

        if not quocgiacanden:
            self._thoidiemhettangbaodogannhat = time.time()
            if self.moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                # Log 1451 28/11 04:42: đào xong tấm cuối ở Hàn Quốc thì kẹt, chỉ báo "Hết tàng bảo đồ" mãi. Gọi không truyền đích => mỗi lần
                # Hồi Thành Phù nhảy nước (7 lần 04:17-04:38) bị đếm là lặp, chặn; thêm việc tự ghi _thoidiemsudunghoithanhphugannhat sau mỗi
                # lần gọi (5s) làm khoá 6s của action_sudunghoithanhphu không bao giờ hết. Đích là Tân Thủ Thôn thì luôn được thử lại
                self.moitruong.action_ngatdichuyen()
                if self.action_sudunghoithanhphu(BANDO_TANTHUTHON, nguon = "Đào tàng bảo đồ: hết tấm, về Tân Thủ Thôn"):
                    self.moitruong._inlog("[ĐÀO TÀNG BẢO ĐỒ] Hết tấm, về Tân Thủ Thôn bán đồ trắng + đổi cầu")
                if not self._is_dacanhbaohettangbaodo:
                    canhbao(self.moitruong, "Hết tàng bảo đồ")
                    self._is_dacanhbaohettangbaodo = True
                self._thoidiemchodaotangbaodo = time.time() + 5.
            else:
                # Ở Tân Thủ Thôn: bán trang bị trắng đào được ở Chủ Tiệm Tạp Hóa trước (lấy chỗ cho Tàng Bảo Đồ), xong mới đổi cầu
                if not self._is_dabantrangdaobaodo:
                    if self._viecbantrangdaobaodo is None:
                        self._viecbantrangdaobaodo = {"banrac": "cho", "lucdi": 0.}
                        self.moitruong._inlog("[ĐÀO TÀNG BẢO ĐỒ] Đào hết, bán trang bị trắng + Lam Kim ở Chủ Tiệm Tạp Hóa trước khi đổi cầu")
                    viec = self._viecbantrangdaobaodo
                    ketqua = self._buocbantrangtinhanh(viec, nhan = "Đào tàng bảo đồ", is_banlamkim = True)
                    if isinstance(ketqua, tuple):
                        if time.time() - viec["lucdi"] > 2.:
                            self.moitruong.action_tudongtimduong(ketqua[1], ketqua[2], BANDO_TANTHUTHON)
                            viec["lucdi"] = time.time()
                        return
                    if ketqua != "xong":
                        return
                    self.moitruong.action_tudongtimduong(0, 0, 0)
                    self._is_dabantrangdaobaodo = True
                    self._viecbantrangdaobaodo = None
                # Bán xong thì cất kho Tinh Nguyên Đơn / Bảo Thạch / Ngọc Thạch / Tinh Thạch ở Quản Khố (TENCHUACATKHODAOBAODOs), rồi mới đổi cầu
                if not self._is_dacatkhodaobaodo:
                    if self._vieccatkhodaobaodo is None:
                        if not self._laymoncatkho(tenchuas = TENCHUACATKHODAOBAODOs):
                            self._is_dacatkhodaobaodo = True
                        else:
                            viec = self._taoviec(LYDOCATKHO_DAOBAODO)
                            viec["tenchuas"] = TENCHUACATKHODAOBAODOs
                            self._vieccatkhodaobaodo = viec
                            self.moitruong._inlog("[ĐÀO TÀNG BẢO ĐỒ] Cất kho " + " / ".join(TENCHUACATKHODAOBAODOs) + " trước khi đổi cầu")
                    if self._vieccatkhodaobaodo is not None:
                        ketqua = self._buoccatkho(self._vieccatkhodaobaodo)
                        if isinstance(ketqua, tuple):
                            self.moitruong.action_dichuyengiukhoangcachtoidadiem(ketqua[1], ketqua[2], khoangcachtoida = KHOANGCACHQUANKHO - 1)
                            return
                        if ketqua not in ("xong", "lỗi"):
                            return
                        self._vieccatkhodaobaodo = None
                        self._is_dacatkhodaobaodo = True
                # Còn cặp Lam + Hắc Cầu và còn chỗ thì đổi Tàng Bảo Đồ (1 cặp ra 2 tấm, chừa 2 ô trống)
                soluongs = self.moitruong.get_soluongvatphamhanhtrangtheoten()
                if soluongs is None:
                    return
                if min(soluongs.get(LAMCAU, 0), soluongs.get(HACCAU, 0)) > 0:
                    sootrong = self.moitruong.get_sootronghanhtrang()
                    if sootrong >= SOOTRONGGIUDOITANGBAODO + SOTANGBAODOMOICAP:
                        self.batdau_doitangbaodo()
                        return
                    canhbao(self.moitruong, f"Hết tàng bảo đồ, hành trang chỉ còn {sootrong} ô trống không đổi được")
                    self._thoidiemchodaotangbaodo = time.time() + 30.
                    return
                if not self._is_dacanhbaohettangbaodo:
                    canhbao(self.moitruong, "Hết tàng bảo đồ và hết cặp Lam + Hắc Cầu")
                    self._is_dacanhbaohettangbaodo = True
                self._thoidiemchodaotangbaodo = time.time() + 5.
                return

                # print("[DAOTAOBAODO] Tiến hành bán rác & sửa đồ...")
                # self.action_tudongbanrac()
                #
                # khoangcachdennpc = math.dist((x_hientai, y_hientai), (150, 128))
                # if khoangcachdennpc > 3.:
                #     self.moitruong.action_tudongtimduong(150, 128, idbandohientai)
            return

        print(f"[DAOTAOBAODO] Hết map hiện tại. Chuẩn bị sang: {quocgiacanden}")

        if idbandohientai != BANDO_TANTHUTHON:
            if time.time() - self._thoidiemsudunghoithanhphugannhat > 12.0:
                print(f"[DAOTAOBAODO] Dùng Hồi Thành Phù về Tân Thủ Thôn")
                self.moitruong.action_ngatdichuyen()
                # Đích Tân Thủ Thôn: không bị đếm lặp khi nhảy nhiều nước liền (xem nhánh hết tấm phía trên)
                self.action_sudunghoithanhphu(BANDO_TANTHUTHON, nguon = f"Đào tàng bảo đồ: sang {quocgiacanden}")
            return

        khoangcachdennpc = math.dist((x_hientai, y_hientai), (148, 149))

        if khoangcachdennpc > 3.0:
            self.moitruong.action_tudongtimduong(148, 149, idbandohientai)
            return

        tenchudichtram = "Chủ Dịch Trạm"
        diachinpc = self.moitruong.action_timkiemnhanvat(tenchudichtram)

        if not diachinpc:
            return

        idnpc = self.moitruong.get_iddoituong(diachinpc)
        if idnpc:
            self.moitruong.action_ngatdichuyen()
            timestamp = int(time.time())
            hex_id = hex(idnpc).replace("0x", "")
            caulenh = f"tallk {hex_id}# goto.! {self.get_diemdendichtram(quocgiacanden)} t{timestamp}"
            self.moitruong.action_thucthicaulenh2(caulenh, delay = 0.0)
            self.moitruong.action_ngatdichuyen()
            # Chờ chuyển bản đồ xong mới xét tiếp (trước đây sleep 5s chặn cả loop phụ)
            self._thoidiemchodaotangbaodo = time.time() + 5.

    def _xoatrangthaisaukhichet(self):
        self._yeucaunhatvatpham = None
        self._yeucautheosau = None
        self._yeucautancong = None
        self._yeucautancongxuat = None
        self._yeucautudo = None
        self._yeucaugomquai = None
        self._yeucaukhaikhoang = None
        self._yeucaudaotangbaodo = None

        self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
        self._diachicosomuctieuduphong = 0
        self._diachicosovatphamdangnhat = False
        self._diachicosokhaikhoang = 0

        self._is_danggomquai = False
        self._danhsachidquaidagom.clear()
        self._idquaidautien = 0
        self._idquaidangkeo = 0

        self._trangthaiveban = 0

        self._idmuctieudangtheokiemtraket = 0
        self._thoidiemdungimkiemtraket = 0.
        self._idmuctieubiloi_map.clear()
        self._theodoitrungchieu = None
        self._idkhoangbiloi_map.clear()

        self._solanthatbaikhaithien = 0
