# Phần hoạt động khác: hội thoại NPC, tạm ngưng khi thấy ẩn thân / người lạ, tổ đội, phục sinh, PK, chặn tăng cấp, khai khoáng, chiến trường, tàng bảo đồ, auto trong game.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import math
import re
import time
import win32gui
import win32con

from hangso_xq import *
from thongbao_xq import baosuco, LYDOTAMNGUNGTUXA
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam
from tienich_xq import laynhomtodoitudongs, laynhanvattodoitudongs, donbangthoidiem
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
        return time.time() < self._thoidiemhettamngung

    def action_kiemtraanthan(self):
        # 1) Tự quét: thấy người chơi lạ ẩn thân, hoặc (ở map train) thấy người ngoài danh sách tổ đội, thì ghi nhận
        #    và công bố cho các cửa sổ khác (qua shared_data)
        # 2) Đang di chuyển theo lộ trình điểm đánh mà mình thấy, hoặc nhân vật khác CÙNG BẢN ĐỒ vừa thấy => ngưng hết mọi hoạt động
        #    (ẩn thân: THOIGIANTAMNGUNGANTHAN, người lạ: THOIGIANTAMNGUNGNGUOILA)
        thoidiemhientai = time.time()
        if thoidiemhientai - self._thoidiemkiemtraanthangannhat < 0.5:
            return
        self._thoidiemkiemtraanthangannhat = thoidiemhientai

        phathien = self._quetnguoichoibatthuong()
        if phathien:
            # Chỉ công bố phát hiện trực tiếp (không công bố trạng thái tạm ngưng) để các nhân vật không gia hạn lẫn nhau mãi
            self._thoidiemphathienanthan = thoidiemhientai
            self._tenanthanphathien, self._thoigiantamngungphathien = phathien

        if not self._is_tudongdichuyendiemdanhxungquanh:
            return
        if phathien:
            self._batdautamngung(f"phát hiện {phathien[0]}", phathien[1])
            return
        phathienkhac = self._layanthantucuasokhac()
        if phathienkhac:
            self._batdautamngung(*phathienkhac)

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
        # Nội bộ = chính mình + nhân vật cùng máy + nhân vật trong danh sách tổ đội tự động + thành viên cùng nhóm (đang tổ đội);
        # ai khác (kể cả cùng bang mà khác nhóm) đều là người lạ
        return idnguoichoi == idnhanvathientai or idnguoichoi in idcungmays or idnguoichoi in idcungnhoms or idnguoichoi in laynhanvattodoitudongs()

    def _quetnguoichoibatthuong(self):
        # Trả về (mô tả, số giây tạm ngưng): ("X ẩn thân", THOIGIANTAMNGUNGANTHAN) / ("người lạ X", THOIGIANTAMNGUNGNGUOILA) hoặc None
        idnhanvathientai = self.moitruong.get_idnguoichoi()
        idcungmays = self._layidnguoichoicungmays()
        idcungnhoms = self.moitruong.get_danhsachidnguoichoithanhviennhoms() or ()
        is_maptrain = self.moitruong.get_idbandohientai() not in BANDOKHONGPKs
        nguoila = None
        i = -1
        while True:
            i += 1
            diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
            if not diachidoituong:
                return nguoila
            # Bỏ các ô đối tượng còn sót (nhân vật đã rời đi / chưa tải xong) để không báo nhầm người lạ
            if not self.moitruong.get_is_nhanvattontai(diachidoituong) or not self.moitruong.get_is_nguoichoi(diachidoituong):
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
            if is_maptrain and nguoila is None:
                nguoila = f"người lạ {tendoituong}", THOIGIANTAMNGUNGNGUOILA

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
            if info.get("tenbando") != idbandohientai:
                continue
            if time.time() - info.get("_thoidiemphathienanthan", 0.) > THOIGIANCHIASEANTHAN:
                continue
            thoigian = info.get("_thoigiantamngungphathien") or THOIGIANTAMNGUNGANTHAN
            if ketqua is None or thoigian > ketqua[1]:
                ketqua = (f"{info.get('tennhanvat') or idcuaso} phát hiện {info.get('_tenanthanphathien') or 'người lạ'}", thoigian)
        return ketqua

    def _batdautamngung(self, lydo, thoigian = None):
        thoigian = thoigian or THOIGIANTAMNGUNGANTHAN
        is_moibatdau = not self.get_is_dangtamngung()
        # Chỉ kéo dài, không rút ngắn (đang ngưng 10 phút vì ẩn thân mà gặp người lạ thì vẫn giữ 10 phút)
        thoidiemhetmoi = time.time() + thoigian
        if is_moibatdau or thoidiemhetmoi >= self._thoidiemhettamngung:
            self._thoidiemhettamngung = thoidiemhetmoi
            self._lydotamngung = lydo
            util_ghitamngung(self.moitruong.get_idnguoichoi(), thoidiemhetmoi, lydo)
        if is_moibatdau:
            thoigianhienthi = f"{int(thoigian // 60)} phút" if thoigian >= 60 else f"{int(thoigian)} giây"
            print(f"[TẠM NGƯNG] {lydo} -> Ngưng mọi hoạt động {thoigianhienthi}")
            if lydo == LYDOTAMNGUNGTUXA:
                phatam("Tạm ngưng từ xa")
            else:
                phatam("Phát hiện ẩn thân, tạm ngưng" if "ẩn thân" in lydo else "Phát hiện người lạ, tạm ngưng")
                # Chỉ nhân vật tự phát hiện ("phát hiện <tên>") báo, các nhân vật ngưng theo ("<ai đó> phát hiện ...") thì không, cho
                # 1 lần phát hiện chỉ ra 1 tin
                if lydo.startswith("phát hiện"):
                    baosuco(self.moitruong, "tamngung", f"Phát hiện {lydo[len('phát hiện '):]}, cả máy tạm ngưng {thoigianhienthi}", khoa = lydo)
            self.moitruong.action_ngatdichuyen()
            self.moitruong.set_diachicosothongtinnhanvatmuctieudangchon(0)
            self._yeucautancong = None
            self._yeucaunhatvatpham = None
            self._yeucaugomquai = None
            self._yeucautudo = None
            self._is_battudongtancongvatly = False

    def tieptuchoatdong(self):
        # Bật lại thủ công: vẫn tiếp tục kiểm tra ẩn thân, gặp người ẩn thân là tạm ngưng tiếp
        self._thoidiemhettamngung = 0.
        self._lydotamngung = ""
        util_xoatamngung(self.moitruong.get_idnguoichoi())
        print("[TẠM NGƯNG] Bật lại hoạt động thủ công")
        phatam("Bật lại hoạt động")

    def get_todoimotlanshare(self):
        # Đang gom tổ đội 1 lần: báo qua shared_data để cửa sổ thành viên (cả máy khác nối LAN) rời nhóm khác, nhận lời mời của mình
        s = self._todoimotlan
        return {"idtruongnhom": self.moitruong.get_idnguoichoi(), "thanhviens": list(s["thanhviens"]), "dangmoi": s["dangmoi"]} if s else None

    def _ketthuctodoimotlan(self, trangthai):
        self._todoimotlan = None
        self._trangthaitodoimotlan = trangthai
        print(f"[TỔ ĐỘI 1 LẦN] {trangthai}")
        phatam(trangthai)

    def _laybotkhacs(self):
        # {ID người chơi: info} các cửa sổ khác đang chạy bot (cùng máy / máy khác nối LAN, còn cập nhật), đọc shared_data 1 lần
        try:
            danhsach = list(self.shared_data.items()) if self.shared_data is not None else []
        except Exception:
            return {}
        return {info["idnguoichoi"]: info for idcuaso, info in danhsach if idcuaso != self.idcuaso and isinstance(info, dict)
                and info.get("idnguoichoi") and time.time() - info.get("thoidiemcapnhat", 0.) <= 5.}

    def action_todoimotlan(self):
        # Luồng riêng (cuaso_xq.khoidong_looptodoimotlan): luồng phụ chứa Tổ đội tự động mỗi lượt ~1s (nghỉ 0.5s + cả chục việc khác) nên
        # mời / đồng ý từng người chậm 3-4s. Trưởng nhóm đang gom / thành viên đang được gom thì xử lý ngay (rời nhóm cũ, mời, đồng ý khi
        # tới lượt). -> True khi đang gom / được gom (luồng chạy nhanh), False khi rảnh (luồng nghỉ lâu)
        if self._todoimotlan:
            self._xulytodoimotlantruongnhom()
            return True
        idtruongnhommotlan, is_dangmoitoi = self._layidtruongnhomtodoimotlan()
        if idtruongnhommotlan:
            self._xulytodoimotlanthanhvien(idtruongnhommotlan, is_dangmoitoi)
            return True
        return False

    def _xulytodoimotlantruongnhom(self):
        # Mình bấm Tổ đội 1 lần: giữ nguyên nhóm hiện tại (không rời / nhường quyền, nhóm đang giữ phó bản), mời các nhân vật cùng danh sách
        # tổ đội tự động đang online hoặc ở gần tới khi đủ hoặc quá THOIGIANTODOIMOTLAN giây
        s = self._todoimotlan
        moitruong = self.moitruong
        idnguoichoi = moitruong.get_idnguoichoi()
        botkhacs = self._laybotkhacs()

        def ten(id_):
            return (botkhacs.get(id_) or {}).get("tennhanvat") or str(id_)

        danhsach = next((list(nhom) for nhom in laynhomtodoitudongs() if idnguoichoi in nhom), None)
        if not danhsach:
            self._ketthuctodoimotlan("Tổ đội 1 lần: nhân vật này chưa có trong danh sách Tổ đội tự động")
            return
        is_dangtrongnhom = moitruong.get_is_dangnamtrongnhom()
        if is_dangtrongnhom and not moitruong.get_is_truongnhom():
            self._ketthuctodoimotlan("Tổ đội 1 lần: mình không phải trưởng nhóm, không mời được")
            return
        # Quét người chơi xung quanh tốn (đọc mọi đối tượng): 1s/lần là đủ
        if time.time() - s.get("lucquetxungquanh", 0.) > 1.:
            s.update(lucquetxungquanh = time.time(), xungquanhs = set(moitruong.get_danhsachidnguoichoixungquanhs() or ()))
        onlines = set(botkhacs) | s["xungquanhs"]
        s["thanhviens"] = [id_ for id_ in danhsach if id_ != idnguoichoi and id_ in onlines]
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if is_dangtrongnhom else set()
        chuavaos = [id_ for id_ in s["thanhviens"] if id_ not in trongnhoms]
        if not s["thanhviens"]:
            self._ketthuctodoimotlan("Tổ đội 1 lần: không thấy thành viên nào trong danh sách đang online")
            return
        if not chuavaos:
            self._ketthuctodoimotlan(f"Tổ đội 1 lần: đã đủ {len(s['thanhviens'])} thành viên")
            return
        if len(trongnhoms) >= SOLUONGTHANHVIENNHOMTOIDA:
            self._ketthuctodoimotlan("Tổ đội 1 lần: nhóm đã đầy")
            return
        conlai = THOIGIANTODOIMOTLAN - (time.time() - s["lucbatdau"])
        if conlai <= 0:
            self._ketthuctodoimotlan(f"Tổ đội 1 lần: hết {int(THOIGIANTODOIMOTLAN)}s, còn thiếu {', '.join(ten(i) for i in chuavaos)}")
            return
        # Mời lần lượt từng người: trưởng nhóm có lời mời đang chờ mà mời thêm người khác thì người trước bấm đồng ý lại thành "xin vào nhóm",
        # chỉ người được mời sau đồng ý mới vào. Người đang mời đã vào / quá THOIGIANCHOMOITHANHVIEN giây chưa vào thì mới mời người kế
        # Người chạy bot còn ở nhóm khác (đang tự rời, xem _xulytodoimotlanthanhvien) thì chưa mời: mời lúc đó họ không đồng ý được, phí cả
        # THOIGIANCHOMOITHANHVIEN giây chờ. Người không chạy bot (không biết nhóm) coi như đang lẻ
        now = time.time()
        conkets = [i for i in chuavaos if (botkhacs.get(i) or {}).get("idtruongnhom", 0) not in (0, idnguoichoi)]
        if s["dangmoi"] and (s["dangmoi"] not in chuavaos or s["dangmoi"] in conkets or now - s["lucmoi"] > THOIGIANCHOMOITHANHVIEN):
            s["dangmoi"] = 0
        sansangs = [i for i in chuavaos if i not in conkets]
        if not s["dangmoi"] and sansangs:
            # Người lâu chưa được mời nhất trước
            idmoi = min(sansangs, key = lambda i: self._thoidiemtodoigannhat_map.get(i, 0))
            if not moitruong.action_moihoacxinvaonhom(idmoi):
                return
            self._thoidiemtodoigannhat_map[idmoi] = now
            s.update(dangmoi = idmoi, lucmoi = now)
        phans = [f"đang mời {ten(s['dangmoi'])}"] if s["dangmoi"] else []
        chotoiluots = [ten(i) for i in sansangs if i != s["dangmoi"]]
        if chotoiluots:
            phans.append(f"chờ tới lượt: {', '.join(chotoiluots)}")
        if conkets:
            phans.append(f"chờ rời nhóm cũ: {', '.join(ten(i) for i in conkets)}")
        self._trangthaitodoimotlan = f"Tổ đội 1 lần: {'; '.join(phans)} (còn {int(conlai)}s)"

    def _tenidnguoichoi(self, idnguoichoi):
        try:
            for info in list(self.shared_data.values()) if self.shared_data is not None else ():
                if isinstance(info, dict) and info.get("idnguoichoi") == idnguoichoi and info.get("tennhanvat"):
                    return info["tennhanvat"]
        except Exception:
            pass
        return str(idnguoichoi)

    def _layidtruongnhomtodoimotlan(self):
        # Trưởng nhóm (cửa sổ khác, cùng máy hoặc LAN) đang gom tổ đội 1 lần có mình trong danh sách: (ID trưởng nhóm, có đang mời đúng
        # mình không), không thì (0, False). Mỗi lần đọc là chép cả shared_data qua Manager: đang được gom thì đọc mỗi lượt luồng tổ đội
        # 1 lần (0.25s, đồng ý ngay khi tới lượt), không ai gom thì nhớ 1s
        thoidiem, ketqua = self._bonhotodoimotlan
        if time.time() - thoidiem < (0.2 if ketqua[0] else 1.):
            return ketqua
        idtoi = self.moitruong.get_idnguoichoi()
        ketqua = (0, False)
        try:
            danhsach = list(self.shared_data.items()) if self.shared_data is not None else []
        except Exception:
            danhsach = []
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict) or time.time() - info.get("thoidiemcapnhat", 0.) > 5.:
                continue
            gom = info.get("_todoimotlan")
            if gom and idtoi in (gom.get("thanhviens") or ()) and gom.get("idtruongnhom"):
                ketqua = (gom["idtruongnhom"], gom.get("dangmoi") == idtoi)
                break
        self._bonhotodoimotlan = (time.time(), ketqua)
        return ketqua

    def _xulytodoimotlanthanhvien(self, idtruongnhom, is_dangmoitoi):
        # Trưởng nhóm đang gom mình (tổ đội 1 lần): đang ở nhóm khác thì rời ngay (Lăng Ly Sơn đang đi dở thì không) để sẵn sàng; chỉ đồng ý
        # lời mời của trưởng nhóm đó khi tới lượt mình. Không tự xin vào (xin vào chen ngang lời mời trưởng nhóm đang gửi người khác).
        # Chạy cả khi mình tắt Tổ đội tự động
        moitruong = self.moitruong
        if moitruong.get_is_dangnamtrongnhom():
            if moitruong.get_idnguoichoitruongnhom() == idtruongnhom or self.get_is_giunhomlanglyson():
                return
            # Gửi lại lệnh rời nếu 1.5s vẫn còn trong nhóm (lệnh rơi / game chưa nhận)
            if time.time() - self._thoidiemroinhomtodoimotlan > 1.5:
                self._thoidiemroinhomtodoimotlan = time.time()
                print(f"[TỔ ĐỘI 1 LẦN] Rời nhóm hiện tại để vào nhóm {self._tenidnguoichoi(idtruongnhom)}")
                moitruong.action_thoatkhoinhom()
            return
        if is_dangmoitoi:
            moitruong.action_kiemtravadongyloimoinhom([idtruongnhom])

    def action_tudongtodoi(self):
        # Lăng Ly Sơn đang giải tán tổ đội cũ (tactu_langlyson_xq): tạm nghỉ, còn trong nhóm thì rời; xong thì lập nhóm mới như thường
        if self.action_roinhomlanglyson():
            return
        # Đoạt Bảo Mã Tặc chỉ đi nhóm 1 người (tactu_matac_xq tự lo rời / lập nhóm): Tổ đội tự động nghỉ suốt lúc đang bật
        if self._matac:
            return
        # Tổ đội 1 lần (Ctrl+Alt+T, luồng riêng action_todoimotlan): đang gom (mình trưởng nhóm) hoặc đang được gom thì bỏ Tổ đội tự động
        # lượt này, khỏi giành nhau
        if self._todoimotlan or self._layidtruongnhomtodoimotlan()[0]:
            return
        if not self._is_tudongtodoi:
            return

        # Quét người chơi xung quanh khá tốn (đọc bộ nhớ toàn bộ đối tượng), thao tác nhóm cũng có delay riêng nên không cần chạy liên tục
        if time.time() - self._thoidiemxulytodoigannhat < 0.5:
            return
        self._thoidiemxulytodoigannhat = time.time()

        idnguoichoi = self.moitruong.get_idnguoichoi()
        tenmonphai = self.moitruong.get_tenmonphai()
        is_dangtrongnhom = self.moitruong.get_is_dangnamtrongnhom()
        idbandohientai = self.moitruong.get_idbandohientai()

        danhsachuutientodoi = None
        for thanhvientodoitudongs in laynhomtodoitudongs():
            if idnguoichoi in thanhvientodoitudongs:
                danhsachuutientodoi = list(thanhvientodoitudongs)
                break

        if not danhsachuutientodoi:
            return

        # Lăng Ly Sơn đang đi dở (đã vào phó bản, chưa lĩnh thưởng xong): không rời nhóm / nhường quyền trưởng nhóm (phó bản giữ theo tổ
        # đội, người đi phó bản phải là trưởng nhóm), vẫn nhận lời mời / mời người rớt nhóm vào lại
        is_giunhom = self.get_is_giunhomlanglyson()

        if tenmonphai in ("vanmongcoc", "thucson") and self._is_chedobufftoanbang and idbandohientai in BANDOKHONGPKs and not is_giunhom:
            if is_dangtrongnhom:
                if self.moitruong.get_is_truongnhom() or (self._is_khongcongidebuff and time.time() - self._thoidiemkiemtrakhongcongidebuffgannhat > 10.):
                    self._thoidiemkiemtrakhongcongidebuffgannhat = time.time()
                    # Trưởng nhóm rời nhóm = giải tán (đá văng cả đội): nhường quyền cho thành viên khác trước, lần sau mới rời
                    thanhvienkhacs = [id_ for id_ in self.moitruong.get_danhsachidnguoichoithanhviennhoms() if id_ != idnguoichoi]
                    if self.moitruong.get_is_truongnhom() and thanhvienkhacs:
                        self.moitruong.action_nhuongquyentruongnhom(thanhvienkhacs[0])
                    else:
                        self.moitruong.action_thoatkhoinhom()
            else:
                self.moitruong.action_kiemtravadongyloimoinhom(laynhanvattodoitudongs())
            return

        if idbandohientai == BANDO_CHIENTRUONG and not is_dangtrongnhom:
            self.moitruong.action_kiemtravadongyloimoinhom(laynhanvattodoitudongs())

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
            if id_ != idnguoichoi and id_ in xephang_map and id_ not in dongdoicanxulys:
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

            if len(danhsachthanhviens) < SOLUONGTHANHVIENNHOMTOIDA:
                # Mời cả người đang lẻ cùng bản đồ (vd: vừa rời nhóm hạng thấp hơn) dù chưa đứng gần
                for iddongdoi in dongdoicanxulys + [id_ for id_ in nguoichoilecungbandos if id_ not in dongdoicanxulys]:
                    if iddongdoi in danhsachthanhviens:
                        continue
                    if time.time() - self._thoidiemtodoigannhat_map.get(iddongdoi, 0) > 5.0:
                        self.moitruong.action_moihoacxinvaonhom(iddongdoi)
                        self._thoidiemtodoigannhat_map[iddongdoi] = time.time()
                        self._thoidiemtodoigannhat_map = donbangthoidiem(self._thoidiemtodoigannhat_map, 120.)
                        break

        elif not is_dangtrongnhom:
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

    def action_tudongkhaikhoang(self):
        if not self._is_tudongkhaikhoang:
            self._yeucaukhaikhoang = None
            self._diachicosokhaikhoang = 0
            return

        idbandohientai = self.moitruong.get_idbandohientai()

        if idbandohientai != self._idbandolanquetkhaikhoangtruoc:
            self._idkhoangbiloi_map.clear()
            self._idbandolanquetkhaikhoangtruoc = idbandohientai

        if self.moitruong.get_is_dangvankhi() or self.moitruong.get_is_dangclickchuottrai() or self.moitruong.get_is_nhanvatdachet() or time.time() - self._thoidiemtamngungdichuyensudungkynang < 0.:
            self._yeucaukhaikhoang = None
            self._diachicosokhaikhoang = 0
            return

        if 0:
            pass
        else:
            idcanxoas = [k for k, v in self._idkhoangbiloi_map.items() if time.time() - v > 30]
            for k in idcanxoas:
                del self._idkhoangbiloi_map[k]

            i = -1
            diachidoituonggannhat = None
            khoangcachgannhat = KHOANGCACHTOIDAHOPLE + 1

            while True:
                i += 1
                diachidoituong = self.moitruong.get_diachicosothongtindoituongx(i)
                if not diachidoituong: break

                tendoituong = self.moitruong.get_tendoituong(diachidoituong)
                tenvatphamkhangs = NGUYENLIEULUYENDONs
                if self.moitruong.get_idnguoichoi() == 59845:
                    tenvatphamkhangs = ("Thiết Khoáng", "Ngân Khoáng", "Tích Khoáng")

                if tendoituong and tendoituong in tenvatphamkhangs:
                    iddoituong = self.moitruong.get_iddoituong(diachidoituong)
                    if iddoituong <= 0: continue
                    if iddoituong in self._idkhoangbiloi_map: continue

                    khoangcach = self.moitruong.get_khoangcach(diachidoituong)
                    if khoangcach > KHOANGCACHTOANMANHINH: continue

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
                    if char_dist < min_char_dist:
                        min_char_dist = char_dist
                        best_mineral_addr = diachidoituong

        if best_mineral_addr:
            self._xuly_daokhoang(best_mineral_addr, min_char_dist)
        else:
            self._xuly_chaylotrinh(target_x, target_y, index_var_name, len_list)

    def _xuly_daokhoang(self, diachikhoang, khoangcach):
        id_min = self.moitruong.get_iddoituong(diachikhoang)

        if id_min != self._idkhoangdangtheo:
            self._idkhoangdangtheo = id_min
            self._thoidiembatdautheokhoang = time.time()
        else:
            if time.time() - self._thoidiembatdautheokhoang > 10.0:
                phatam("Khoáng lỗi, bỏ qua")
                self._idkhoangbiloi_map[id_min] = time.time()
                self._idkhoangdangtheo = 0
                self._yeucaukhaikhoang = None
                return

        if khoangcach >= 6.0:
            mx_move, my_move = self.moitruong.get_toado(diachikhoang, )

            self._yeucaukhaikhoang = {
                "yeucau": YEUCAUDICHUYENKHAIKHOANG,
                "kieudichuyen": KIEUDICHUYEN_GIUKHOANGCACHTOIDA,
                "toadodich": (mx_move, my_move),
                "khoangcachtoida": 0
            }
        else:
            self._yeucaukhaikhoang = None

            if self.moitruong.get_idtuthenhanvat() == TUTHENHANVAT_DUNGIM:
                if time.time() - self._thoidiemkhaikhoanggannhat > 1.0:
                    self.moitruong.action_khaikhoang(id_min)
                    self._thoidiemkhaikhoanggannhat = time.time()
                    self._thoidiembatdautheokhoang = time.time()
            else:
                pass

        self._diachicosokhaikhoang = diachikhoang

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
                "khoangcachtoida": 0
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
            return

        if time.time() < self._thoidiemchodaotangbaodo:
            return

        if self.moitruong.get_is_nhanvatdachet() or self.moitruong.get_is_dangvankhi():
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
                print(f"[DAOTAOBAODO] Dùng Hồi Thành Phù về Tân Thủ Thôn")
                self.moitruong.action_ngatdichuyen()
                self.action_sudunghoithanhphu()
                self._thoidiemsudunghoithanhphugannhat = time.time()
                phatam("{} hết tàng bảo đồ".format(self.moitruong.get_tendoituong()))
                self._thoidiemchodaotangbaodo = time.time() + 5.
            else:
                if not self.moitruong.action_timkiemvatphamhanhtrang(LAMCAU):
                    phatam("{} hết tàng bảo đồ".format(self.moitruong.get_tendoituong()))
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
                self.action_sudunghoithanhphu()
                self._thoidiemsudunghoithanhphugannhat = time.time()
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
            caulenh = f"tallk {hex_id}# goto.! {quocgiacanden} t{timestamp}"
            self.moitruong.action_thucthicaulenh2(caulenh, delay = 0.0)
            self.moitruong.action_ngatdichuyen()
            # Chờ chuyển bản đồ xong mới xét tiếp (trước đây sleep 5s chặn cả loop phụ)
            self._thoidiemchodaotangbaodo = time.time() + 5.

    def action_tudongbatautoingame(self):
        self.moitruong.set_is_batautoingame(False)

    def _xoatrangthaisaukhichet(self):
        self._yeucaunhatvatpham = None
        self._yeucautheosau = None
        self._yeucautancong = None
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
