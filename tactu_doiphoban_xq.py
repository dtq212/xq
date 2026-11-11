# Đội phó bản (bảng "Phó bản chung" ở tab Tổ đội, cấu hình _internal/doiphoban.json qua tienich_xq.laydoiphobans): các nhân vật cố
# định đi chung các việc theo nhóm (VIECDOI_MAP: Sư Gia, Tập Kích, Lăng Ly Sơn, Thành Kiều, Phong Yêu Kính). Thành viên đầu là trưởng
# đội; bấm Chạy ở cửa sổ trưởng đội (máy đang mở giao diện), thành viên ở máy nào cũng được (đọc qua shared_data / LAN). Trưởng đội:
#   cho     : việc kế = việc tích đầu tiên (theo thứ tự) chưa có kết quả hôm nay; chờ mọi thành viên online (thiếu ai cả đội chờ, không
#             bao giờ đi thiếu người) và báo sẵn sàng. Thành viên (cả trưởng đội) đang làm Sư môn / Danh Vọng thì làm xong lượt đang dở rồi
#             tạm dừng (get_is_nhuongdoiphoban), đang Mã Tặc / Kéo cấp / giao đồ / cất kho thì đội chờ xong
#   lapnhom : trưởng đội rời nhóm có người ngoài / không phải mình làm trưởng nhóm, mời lần lượt từng thành viên (như Tổ đội 1 lần, chạy
#             ở luồng nhanh action_doiphobannhanh); thành viên rời nhóm khác, chỉ nhận lời mời của trưởng đội
#   lam     : trưởng đội bật việc; thành viên bật cùng việc (chế độ thành viên: Phong Yêu Kính cần, việc khác tự đi theo) và Theo sau
#             trưởng đội (nhớ thiết lập cũ để trả). Phó bản giải tán nhóm giữa các vòng thì đội tự mời lại (ngoài phó bản). Việc dừng ở
#             trưởng đội (_ghiketthucviecdoi) => ghi kết quả hôm nay, thành viên dừng việc đó, về "cho" làm việc kế
#   hết việc: giải tán nhóm, thành viên trả Theo sau cũ, quay về Hàng việc cá nhân
# Đội phó bản đang chạy giữ thành viên (get_idsdoiphobangiu): Tổ đội tự động / Tổ đội 1 lần không đụng tới nhân vật đó, nhân vật ngoài đội
# cũng không kéo họ. Trưởng đội mất kết nối: thành viên chờ THOIGIANGIUDOIKHIMAT giây rồi mới tạm về việc cá nhân; trưởng đội vào lại
# (trạng thái lưu theo nhân vật) thì gọi đội tiếp; trong lúc đó thành viên không tự dẫn đi (get_is_thanhviendoiviec). Sửa đội giữa
# chừng đổi trưởng đội sang thành viên khác: trưởng đội cũ chuyển đội (_chuyentruongdoi / _nhantruongdoi), việc đang làm giữ nguyên.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._...) khởi tạo trong TacTu.__init__
import time

from hangso_xq import *
from tienich_xq import phatam, laydoiphoban, laydoiphobans, layidtaikhoans, laynhanvattodoitudongs

# Trưởng đội mất tín hiệu quá chừng này giây thì thành viên mới thôi theo đội (tạm về việc cá nhân)
THOIGIANGIUDOIKHIMAT = 60.
# Đội xong / dừng: trưởng đội còn báo "xong" chừng này giây cho thành viên thôi ngay
THOIGIANBAOXONGDOI = 10.
# Bật việc rồi chừng này giây chưa thấy chạy thì coi là không bắt đầu được
THOIGIANCHOBATDAUVIECDOI = 5.
# Trưởng đội / thành viên rời nhóm, mời lại người rớt nhóm: mỗi lần cách nhau ít nhất chừng này giây
GIANCACHROINHOMDOI = 2.
GIANCACHMOILAIDOI = 5.
# Lập nhóm mà trưởng nhóm trong game là thành viên đội (đổi trưởng đội giữa chừng): chờ họ nhường trưởng nhóm chừng này giây rồi mới rời
THOIGIANCHONHUONGTRUONGNHOM = 15.


def _ngayhomnay():
    return time.strftime("%Y-%m-%d")


class TacTuDoiPhoBan:
    # --- Bật / tắt (trưởng đội) ----------------------------------------------------------------------------------------------------
    def batdau_doiphoban(self, ma):
        doi = laydoiphoban(ma)
        if not doi:
            self._trangthaidoiphoban = "Không tìm thấy đội (đã xoá?)"
            return
        if doi["thanhviens"][0] != self.moitruong.get_idnguoichoi():
            self._trangthaidoiphoban = f"Đội {doi['ten']}: nhân vật này không phải trưởng đội (thành viên đầu)"
            return
        self._doiphoban = {"ma": ma, "giaidoan": "cho", "viec": "", "lucviec": 0., "trangthai": "bắt đầu", "dangmoi": 0, "lucmoi": 0.,
                           "luclam": 0., "lucroinhom": 0., "lucmoilai": {}, "luclapnhom": 0.}
        self._doiphobanxong = None
        self._logdoi(f"Bắt đầu chạy đội {doi['ten']}: " + ", ".join(VIECDOI_MAP[k] for k in doi["thutu"] if k in doi["chon"]))
        phatam(f"Bắt đầu đội {doi['ten']}")

    def huy_doiphoban(self):
        s = self._doiphoban
        if s:
            # Kết thúc đội trước rồi mới dừng việc đang làm (đội đã None thì _ghiketthucviecdoi bỏ qua)
            self._ketthucdoiphoban("Đã dừng đội (bấm tay)", is_giaitan = False)
            if s["viec"] and self.get_viecdanglam() == s["viec"]:
                self._dungviec(s["viec"])

    def giaitan_doiphoban(self, ma = ""):
        # Nút "Giải tán" ở bảng Phó bản chung (gửi tới trưởng đội): dừng đội nếu đang chạy (thành viên thôi đội, trả Theo sau cũ), tắt Tổ
        # đội tự động ở trưởng đội và mọi thành viên (không thì nó lập lại nhóm cũ ngay: xin vào / mời / nhường trưởng nhóm) rồi ai cũng
        # rời nhóm trong game, kể cả đang trong phó bản (người dùng đã xác nhận). Thành viên (cả máy khác nối LAN) nhận qua share "xong"
        # kèm "giaitan" (_xulygiaitandoi)
        s = self._doiphoban
        ma = s["ma"] if s else ma
        if s:
            self._ketthucdoiphoban("Giải tán đội (bấm tay)", is_giaitan = False)
            if s["viec"] and self.get_viecdanglam() == s["viec"]:
                self._dungviec(s["viec"])
        doi = laydoiphoban(ma)
        self._doiphobanxong = {"ma": ma, "thanhviens": list(doi["thanhviens"]) if doi else [], "luc": time.time(), "giaitan": True}
        self._trangthaidoiphoban = f"{time.strftime('%H:%M')} Đội {doi['ten'] if doi else ''}: giải tán (bấm tay), đã tắt Tổ đội tự động"
        self._batdaugiaitan("Giải tán đội (bấm tay)")

    def _batdaugiaitan(self, lydo):
        # Tắt Tổ đội tự động / huỷ Tổ đội 1 lần, rời nhóm ngay; THOIGIANBAOXONGDOI giây sau đó còn trong nhóm (bị mời / nhường lại giữa
        # chừng) thì rời tiếp (_giunhomgiaitan)
        if self._is_tudongtodoi:
            self._is_tudongtodoi = False
            self._logdoi(f"{lydo}: tắt Tổ đội tự động (bật lại ở tab Tổ đội)")
        if self._todoimotlan:
            self.huy_todoimotlan()
        self._lucgiaitan = time.time()
        self._lucroinhomgiaitan = 0.
        self._giunhomgiaitan()

    def _giunhomgiaitan(self):
        if time.time() - self._lucgiaitan > THOIGIANBAOXONGDOI or not self.moitruong.get_is_dangnamtrongnhom():
            return
        if time.time() - self._lucroinhomgiaitan > 1.5:
            self._lucroinhomgiaitan = time.time()
            self.moitruong.action_thoatkhoinhom(delay = 0.)

    def _xulygiaitandoi(self):
        # Thành viên: trưởng đội vừa bấm Giải tán đội có mình (share "xong" kèm "giaitan") => tắt Tổ đội tự động, rời nhóm (1 lần mỗi lần
        # giải tán); trong lúc giải tán còn trong nhóm thì rời tiếp
        idtoi = self.moitruong.get_idnguoichoi()
        for _, d in self._laydoiphobancacsos():
            if d.get("giaidoan") == "xong" and d.get("giaitan") and idtoi in (d.get("thanhviens") or ()):
                khoa = (d.get("idtruong"), d.get("luc"))
                if khoa != self._giaitandaxuly:
                    self._giaitandaxuly = khoa
                    self._batdaugiaitan(f"Trưởng đội {self._tenidnguoichoi(d.get('idtruong'))} giải tán đội")
        self._giunhomgiaitan()

    def ngung_viecdoi(self):
        # Nút "Ngưng việc này" ở bảng Phó bản chung: ngưng việc đội đang làm, ghi "ngưng" hôm nay (không làm lại tới khi bấm Làm lại), đội
        # sang việc kế. Đổi giai đoạn trước rồi mới dừng việc: _ghiketthucviecdoi thấy không còn "lam" thì không dừng cả đội
        s = self._doiphoban
        if not s or s["giaidoan"] != "lam" or not s["viec"]:
            return
        viec = s["viec"]
        self._lamtuoingaydoiphoban()
        self._ketquadoiphoban["doi"].setdefault(s["ma"], {})[viec] = {"kq": "ngung", "luc": time.strftime("%H:%M"),
                                                                      "thongbao": f"Ngưng {VIECDOI_MAP.get(viec, viec)} (bấm tay), sang việc kế"}
        s.update(giaidoan = "cho", viec = "", lucviec = 0.)
        self._logdoi(f"Ngưng {VIECDOI_MAP.get(viec, viec)} (bấm tay), sang việc kế")
        if self.get_viecdanglam() == viec:
            self._dungviec(viec)

    def get_thanhviendoiphoban(self):
        # Thành viên đội phó bản mình đang chạy / đang theo (người đầu là trưởng đội), None nếu không ở đội nào
        if self._doiphoban:
            doi = laydoiphoban(self._doiphoban["ma"])
            return list(doi["thanhviens"]) if doi else None
        if self._doiphobantv:
            d = self._laydoicuatoi()
            return list(d.get("thanhviens") or ()) if d else None
        return None

    def lamlai_doiphoban(self, ma, viecs):
        # Xoá kết quả hôm nay của các việc này (đội ma) để đội làm lại
        self._lamtuoingaydoiphoban()
        kq = self._ketquadoiphoban["doi"].get(ma) or {}
        for viec in viecs:
            kq.pop(viec, None)

    def _ketthucdoiphoban(self, thongbao, is_giaitan = True):
        s = self._doiphoban
        if not s:
            return
        self._doiphoban = None
        doi = laydoiphoban(s["ma"])
        ten = doi["ten"] if doi else s["ma"]
        self._doiphobanxong = {"ma": s["ma"], "thanhviens": list(doi["thanhviens"]) if doi else [], "luc": time.time()}
        self._trangthaidoiphoban = f"{time.strftime('%H:%M')} Đội {ten}: {thongbao}"
        self._logdoi(f"Đội {ten}: {thongbao}")
        moitruong = self.moitruong
        if is_giaitan and moitruong.get_is_dangnamtrongnhom() and not self._is_trongphobandoi():
            # Trưởng nhóm rời nhóm = giải tán (trong phó bản thì không: phó bản ăn theo nhóm, giải tán là đóng phó bản)
            moitruong.action_thoatkhoinhom()
        phatam(f"Kết thúc đội {ten}")

    # --- Chia sẻ qua shared_data -------------------------------------------------------------------------------------------------------
    def get_doiphobanshare(self):
        # Trưởng đội đang chạy (hoặc vừa xong): cho thành viên (cả máy khác nối LAN) biết đội, việc, giai đoạn, ai đang được mời
        s = self._doiphoban
        if s:
            doi = laydoiphoban(s["ma"]) or {}
            return {"ma": s["ma"], "ten": doi.get("ten", ""), "idtruong": self.moitruong.get_idnguoichoi(),
                    "thanhviens": list(doi.get("thanhviens") or ()), "giaidoan": s["giaidoan"], "viec": s["viec"], "lucviec": s["lucviec"],
                    "phai": doi.get("phai", ""), "dangmoi": s["dangmoi"], "trangthai": s["trangthai"]}
        x = self._doiphobanxong
        if x and time.time() - x["luc"] < THOIGIANBAOXONGDOI:
            return {"ma": x["ma"], "idtruong": self.moitruong.get_idnguoichoi(), "thanhviens": x["thanhviens"], "giaidoan": "xong",
                    "giaitan": bool(x.get("giaitan")), "luc": x["luc"], "chuyentruong": x.get("chuyentruong", 0)}
        return None

    def get_doiphobanthanhvienshare(self):
        # Thành viên đang theo đội: báo trưởng đội mình sẵn sàng chưa (lý do nếu chưa)
        tv = self._doiphobantv
        if not tv:
            return None
        # Việc của đội đang chạy sẵn ở mình (bot mở lại giữa chừng) không tính là bận
        lydo = self._lydobanviecrieng(tv.get("viecdoi"))
        return {"ma": tv["ma"], "idtruong": tv["idtruong"], "sansang": not lydo, "lydo": lydo}

    def get_ketquadoiphobanshare(self):
        # Kết quả hôm nay các đội mình làm trưởng đội: {mã đội: {việc: {"kq", "luc", "thongbao"}}} cho bảng Phó bản chung
        self._lamtuoingaydoiphoban()
        return {ma: dict(kq) for ma, kq in self._ketquadoiphoban["doi"].items()}

    def get_trangthaidoiphoban(self):
        # Một dòng cho giao diện: mình đang làm gì với đội phó bản ("" = không dính đội nào)
        s = self._doiphoban
        if s:
            doi = laydoiphoban(s["ma"]) or {}
            viec = VIECDOI_MAP.get(s["viec"], "")
            return f"Trưởng đội {doi.get('ten', '')}" + (f" – {viec}" if viec else "") + f": {s['trangthai']}"
        tv = self._doiphobantv
        if tv:
            return f"Thành viên đội {tv.get('ten', '')}: {tv.get('trangthai', '')}"
        return self._trangthaidoiphoban

    def _laydoiphobancacsos(self):
        # [(info cửa sổ khác còn cập nhật, share đội)] (cùng máy / LAN). Nhớ 0.3s: đọc shared_data là chép qua Manager
        thoidiem, ketqua = self._bonhodoiphoban
        if time.time() - thoidiem < 0.3:
            return ketqua
        ketqua = [(info, info["_doiphoban"]) for info in self._laybotkhacs().values() if isinstance(info.get("_doiphoban"), dict)]
        self._bonhodoiphoban = (time.time(), ketqua)
        return ketqua

    def get_idsdoiphobangiu(self):
        # ID mọi nhân vật đang bị đội phó bản đang chạy giữ (đội của mình và của cửa sổ khác)
        ids = set()
        share = self.get_doiphobanshare()
        for d in ([share] if share else []) + [d for _, d in self._laydoiphobancacsos()]:
            if d.get("giaidoan") != "xong":
                ids.update(d.get("thanhviens") or ())
        return ids

    def get_is_dangtrongdoiphoban(self):
        # Mình đang là trưởng đội đang chạy hoặc thành viên đang theo đội: Tổ đội tự động / Tổ đội 1 lần nghỉ
        return bool(self._doiphoban) or bool(self._doiphobantv)

    def get_is_nhuongdoiphoban(self):
        # Đội đang cần mình (trưởng đội đang chạy / thành viên đang theo đội): Hàng việc cá nhân không bật việc mới, Sư môn / Danh Vọng
        # làm xong lượt đang dở thì tạm dừng
        return self.get_is_dangtrongdoiphoban()

    def get_is_thanhviendoiviec(self, viec):
        # Mình là thành viên (không phải trưởng đội) đội phó bản đang làm viec: ngoài phó bản không tự dẫn đi (trưởng đội dis / nhóm tan
        # thì mình thành trưởng nhóm hoặc không có nhóm: chờ trưởng đội, không tự vào phó bản một mình / thay trưởng đội)
        return bool(self.get_idtruongdoiviec(viec))

    def get_idtruongdoiviec(self, viec):
        # ID trưởng đội mình phải chờ cho viec (0 = không): đang theo đội làm viec, hoặc chưa thấy trưởng đội (chưa online / mất tín hiệu
        # quá lâu / bot mở lại tự bật lại việc đã lưu) mà mình là thành viên (không phải người đầu) một đội có tích viec. Từng để thành
        # viên tự đi Phong Yêu Kính riêng lẻ khi trưởng đội còn chưa online
        tv = self._doiphobantv
        if tv:
            return tv["idtruong"] if tv.get("viecdoi") == viec else 0
        if self._doiphoban:
            return 0
        idtoi = self.moitruong.get_idnguoichoi()
        return next((d["thanhviens"][0] for d in laydoiphobans() if idtoi in d["thanhviens"][1:] and viec in d["chon"]), 0)

    def get_idnguoiquens(self):
        # Người quen (không báo người lạ, đồng đội: buff, không đánh): mình, nhân vật đang chạy bot (cùng máy / LAN), nhân vật trong file
        # tài khoản, danh sách tổ đội, đội phó bản đang chạy. Gọi trong vòng quét đối tượng nên nhớ 2s
        thoidiem, ketqua = self._bonhonguoiquen
        if time.time() - thoidiem < 2.:
            return ketqua
        ids = {self.moitruong.get_idnguoichoi()}
        try:
            for info in list(self.shared_data.values()) if self.shared_data is not None else ():
                if isinstance(info, dict) and info.get("idnguoichoi"):
                    ids.add(info["idnguoichoi"])
        except Exception:
            pass
        ids |= layidtaikhoans()
        ids.update(laynhanvattodoitudongs())
        ids |= self.get_idsdoiphobangiu()
        ids.discard(0)
        ketqua = frozenset(ids)
        self._bonhonguoiquen = (time.time(), ketqua)
        return ketqua

    # --- Kết quả / số vòng -----------------------------------------------------------------------------------------------------------
    def _lamtuoingaydoiphoban(self):
        if self._ketquadoiphoban.get("ngay") != _ngayhomnay():
            self._ketquadoiphoban = {"ngay": _ngayhomnay(), "doi": {}}

    def _ghiketthucviecdoi(self, viec, thongbao):
        # Gọi từ _ghiketthucviec (mọi việc dừng): việc đội đang làm ở trưởng đội dừng => ghi kết quả, sang việc kế. Dừng tay việc đó thì
        # dừng cả đội (không ghi kết quả). "(nhường đội)" là việc cá nhân tạm dừng, không liên quan
        s = self._doiphoban
        if not s or s["giaidoan"] != "lam" or viec != s["viec"]:
            return
        if "(bấm tay)" in thongbao:
            self._ketthucdoiphoban(f"dừng tay {VIECDOI_MAP.get(viec, viec)}: dừng cả đội (bấm Chạy để làm tiếp)", is_giaitan = False)
            return
        self._lamtuoingaydoiphoban()
        self._ketquadoiphoban["doi"].setdefault(s["ma"], {})[viec] = {"kq": "xong" if thongbao.startswith("✅") else "loi",
                                                                      "luc": time.strftime("%H:%M"), "thongbao": thongbao}
        self._logdoi(f"Xong {VIECDOI_MAP.get(viec, viec)}: {thongbao}")
        s.update(giaidoan = "cho", viec = "", lucviec = 0.)

    def _is_dugioihanvong(self, viec, sovong):
        # Việc có vòng (phó bản, Tập Kích) do đội bật: đủ số vòng đặt ở bảng Phó bản chung thì dừng ở chỗ an toàn (gọi từ module việc đó)
        s = self._doiphoban
        if not s or s["giaidoan"] != "lam" or s["viec"] != viec:
            return False
        gioihan = ((laydoiphoban(s["ma"]) or {}).get("vong") or {}).get(viec, 0)
        return bool(gioihan) and sovong >= gioihan

    # --- Bận việc riêng ---------------------------------------------------------------------------------------------------------------
    def _lydobanviecrieng(self, viecdoi = None):
        # Mình còn bận gì phải xong trước khi đi đội ("" = sẵn sàng). viecdoi: việc đội mình đang làm theo (không tính là bận)
        dang = self.get_viecdanglam()
        if dang and dang != viecdoi:
            if dang in ("sumon", "danhvong"):
                return f"làm nốt lượt {VIECHANG_MAP[dang]} đang dở"
            if dang in VIECDOI_MAP:
                return f"đang làm {VIECDOI_MAP[dang]} riêng"
            return f"đang {VIECRIENG_MAP.get(dang, dang)}"
        if self.get_is_danggiaodo():
            return "đang giao tiền / đồ"
        if self.get_is_dangcatkho():
            return "đang cất kho"
        return ""

    # --- Vòng chính (luồng phụ, gọi cạnh action_hangviec) ----------------------------------------------------------------------------
    def action_doiphoban(self):
        if self._doiphoban:
            self._buoctruongdoi()
        else:
            self._xulygiaitandoi()
            self._buocthanhviendoi()

    def action_doiphobannhanh(self):
        # Luồng nhanh của Tổ đội 1 lần (0.25s/lượt): trưởng đội đang lập nhóm thì mời, thành viên được gom thì rời nhóm cũ / nhận lời mời
        # ngay. -> True khi đang lập nhóm / được gom
        s = self._doiphoban
        if s and s["giaidoan"] == "lapnhom":
            self._buoclapnhom(s)
            return True
        tv = self._doiphobantv
        if tv and tv.get("giaidoan") in ("lapnhom", "lam"):
            self._xulynhomthanhvien(tv)
            return tv["giaidoan"] == "lapnhom"
        return False

    def _buoctruongdoi(self):
        s = self._doiphoban
        moitruong = self.moitruong
        doi = laydoiphoban(s["ma"])
        if not doi:
            self._ketthucdoiphoban("đội đã bị xoá", is_giaitan = False)
            return
        idtoi = moitruong.get_idnguoichoi()
        if doi["thanhviens"][0] != idtoi:
            if idtoi in doi["thanhviens"]:
                self._chuyentruongdoi(s, doi)
            else:
                self._ketthucdoiphoban("nhân vật này không còn là trưởng đội", is_giaitan = False)
            return
        if s["giaidoan"] == "lam":
            self._buoclamviec(s, doi)
            return
        # Chọn việc kế
        self._lamtuoingaydoiphoban()
        daxong = self._ketquadoiphoban["doi"].get(s["ma"]) or {}
        viec = next((k for k in doi["thutu"] if k in doi["chon"] and k not in daxong), "")
        if not viec:
            self._ketthucdoiphoban("✅ Xong mọi việc của đội hôm nay")
            return
        s["viec"] = viec
        tenviec = VIECDOI_MAP[viec]
        if self.get_viecdanglam() == viec:
            # Việc đã đang chạy (bot mở lại giữa chừng, việc tự bật tiếp): làm tiếp luôn
            s.update(giaidoan = "lam", lucviec = time.time(), luclam = time.time(), dangmoi = 0, trangthai = f"làm tiếp {tenviec}")
            self._logdoi(f"{tenviec} đang chạy sẵn: làm tiếp")
            return
        lydo = self._lydobanviecrieng()
        if lydo:
            s.update(giaidoan = "cho", trangthai = f"{tenviec}: chờ mình {lydo}")
            return
        botkhacs = self._laybotkhacs()
        thanhviens = doi["thanhviens"][1:]
        offlines = [i for i in thanhviens if i not in botkhacs]
        if offlines:
            s.update(giaidoan = "cho", trangthai = f"{tenviec}: chờ online: {', '.join(self._tenidnguoichoi(i) for i in offlines)}")
            return
        chuasansangs = []
        for i in thanhviens:
            tv = botkhacs[i].get("_doiphobanthanhvien") or {}
            if tv.get("ma") != s["ma"] or tv.get("idtruong") != idtoi:
                # Online mà không báo gì về đội: Foxia bên đó là bản cũ (chưa có đội phó bản) hoặc chưa thấy trưởng đội qua LAN
                chuasansangs.append(f"{self._tenidnguoichoi(i)} (chưa nhận đội: Foxia bên đó bản cũ / chưa thấy trưởng đội qua LAN?)")
            elif not tv.get("sansang"):
                chuasansangs.append(f"{self._tenidnguoichoi(i)} ({tv.get('lydo') or 'chưa sẵn sàng'})")
        if chuasansangs:
            s.update(giaidoan = "cho", trangthai = f"{tenviec}: chờ {', '.join(chuasansangs)}")
            return
        if s["giaidoan"] == "cho":
            s.update(giaidoan = "lapnhom", dangmoi = 0, lucmoi = 0., luclapnhom = time.time())
            self._logdoi(f"Đủ người, lập nhóm đi {tenviec}")
        # Lập nhóm chạy ở luồng nhanh (action_doiphobannhanh); đủ người thì _buoclapnhom chuyển sang "lam"

    def _buoclapnhom(self, s):
        # Trưởng đội: nhóm phải đúng mình làm trưởng nhóm, chỉ có người trong đội; thiếu ai thì mời lần lượt. Đủ thì bật việc
        moitruong = self.moitruong
        doi = laydoiphoban(s["ma"])
        if not doi:
            return
        idtoi = moitruong.get_idnguoichoi()
        thanhviens = doi["thanhviens"][1:]
        is_trongnhom = moitruong.get_is_dangnamtrongnhom()
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if is_trongnhom else set()
        if is_trongnhom and self._is_trongphobandoi():
            # Đang trong phó bản (bot mở lại / đổi trưởng đội giữa chừng): không bao giờ rời nhóm (rời là bị đưa ra ngoài). Nhóm toàn người
            # trong đội thì bật việc luôn (chưa làm trưởng nhóm thì việc tự đi theo, ra phó bản được nhường lại), có người ngoài thì chờ ra
            if not trongnhoms - set(doi["thanhviens"]):
                self._logdoi("Đang trong phó bản cùng nhóm đội: bật việc luôn, không lập lại nhóm")
                self._batdauviecdoi(s, doi)
            else:
                s["trangthai"] = f"{VIECDOI_MAP[s['viec']]}: đang trong phó bản (nhóm có người ngoài đội), chờ ra mới lập nhóm"
            return
        if is_trongnhom and (not moitruong.get_is_truongnhom() or trongnhoms - set(doi["thanhviens"])):
            idtruongnhom = moitruong.get_idnguoichoitruongnhom()
            if not trongnhoms - set(doi["thanhviens"]) and idtruongnhom in doi["thanhviens"]:
                # Nhóm toàn người trong đội, trưởng nhóm là thành viên đội (đổi trưởng đội giữa chừng): chờ họ nhường trưởng nhóm
                # (_xulynhomthanhvien) thay vì rời nhóm
                if time.time() - s["luclapnhom"] < THOIGIANCHONHUONGTRUONGNHOM:
                    trangthai = f"{VIECDOI_MAP[s['viec']]}: chờ {self._tenidnguoichoi(idtruongnhom)} nhường trưởng nhóm"
                    if s["trangthai"] != trangthai:
                        self._logdoi(f"Trưởng nhóm là {self._tenidnguoichoi(idtruongnhom)} (trong đội): chờ nhường trưởng nhóm "
                                     f"{int(THOIGIANCHONHUONGTRUONGNHOM)}s thay vì rời nhóm")
                    s["trangthai"] = trangthai
                    return
                if s["lucroinhom"] < s["luclapnhom"]:
                    self._logdoi(f"Chờ {int(THOIGIANCHONHUONGTRUONGNHOM)}s mà {self._tenidnguoichoi(idtruongnhom)} chưa nhường trưởng nhóm")
            if time.time() - s["lucroinhom"] > GIANCACHROINHOMDOI:
                s["lucroinhom"] = time.time()
                self._logdoi("Rời nhóm hiện tại (có người ngoài đội / mình không làm trưởng nhóm) để lập nhóm đội")
                moitruong.action_thoatkhoinhom()
            s["trangthai"] = f"{VIECDOI_MAP[s['viec']]}: rời nhóm cũ để lập nhóm đội"
            return
        chuavaos = [i for i in thanhviens if i not in trongnhoms]
        if not chuavaos:
            self._batdauviecdoi(s, doi)
            return
        botkhacs = self._laybotkhacs()
        if not is_trongnhom:
            # Chờ nhường trưởng nhóm tính từ lúc vào nhóm
            s["luclapnhom"] = time.time()
            truongnhomdois = [i for i in thanhviens if (botkhacs.get(i) or {}).get("idtruongnhom") == i]
            if truongnhomdois:
                # Thành viên đội đang làm trưởng nhóm (trong phó bản không được rời / giải tán: họ mời mình vào rồi nhường): nhận lời mời
                # của họ, không tự mời người khác chen ngang
                moitruong.action_kiemtravadongyloimoinhom(truongnhomdois)
                s["trangthai"] = f"{VIECDOI_MAP[s['viec']]}: chờ vào nhóm của {', '.join(self._tenidnguoichoi(i) for i in truongnhomdois)} để được nhường"
                return
        sansangs, conkets = self._moilanluot(s, chuavaos, botkhacs)
        phans = [f"đang mời {self._tenidnguoichoi(s['dangmoi'])}"] if s["dangmoi"] else []
        if conkets:
            phans.append(f"chờ rời nhóm cũ: {', '.join(self._tenidnguoichoi(i) for i in conkets)}")
        s["trangthai"] = f"{VIECDOI_MAP[s['viec']]}: lập nhóm" + (f" ({'; '.join(phans)})" if phans else "")

    def _batdauviecdoi(self, s, doi):
        viec = s["viec"]
        s.update(giaidoan = "lam", lucviec = time.time(), luclam = time.time(), dangmoi = 0, trangthai = f"bắt đầu {VIECDOI_MAP[viec]}")
        self._logdoi(f"Đủ nhóm, bắt đầu {VIECDOI_MAP[viec]}")
        self._batviecdoi(viec, doi.get("phai"))

    def _batviecdoi(self, viec, phai = None):
        if viec == "sugia":
            self.batdau_sugia()
        elif viec == "tapkich":
            self.batdau_tapkich(phai or None)
        else:
            self.batdau_langlyson(viec)

    def _is_trongphobandoi(self):
        idbando = self.moitruong.get_idbandohientai()
        return idbando in BANDOPHOBANs or self._is_trongphobanlls(idbando) or self.moitruong.get_is_bandotapkichmonphai()

    def _buoclamviec(self, s, doi):
        # Trưởng đội đang làm việc: việc chưa chạy nổi thì ghi lỗi; còn chạy thì mời lại người rớt nhóm (ngoài phó bản, phó bản không
        # đang giải tán tổ đội, Phong Yêu Kính tự mời theo _laynhompy)
        viec = s["viec"]
        moitruong = self.moitruong
        if self.get_viecdanglam() != viec:
            if time.time() - s["luclam"] > THOIGIANCHOBATDAUVIECDOI:
                self._ghiketthucviec(viec, "❌ Không bắt đầu được (thiếu thiết lập? xem log)")
            return
        s["trangthai"] = {"sugia": self.get_trangthaisugia, "tapkich": self.get_trangthaitapkich}.get(viec, self.get_trangthailanglyson)()
        if viec == "phongyeukinh" or self.get_is_tamtattodoilanglyson() or self._is_trongphobandoi():
            return
        if moitruong.get_is_dangnamtrongnhom() and not moitruong.get_is_truongnhom():
            return
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if moitruong.get_is_dangnamtrongnhom() else set()
        now = time.time()
        for i in doi["thanhviens"][1:]:
            if i not in trongnhoms and now - s["lucmoilai"].get(i, 0.) > GIANCACHMOILAIDOI:
                s["lucmoilai"][i] = now
                moitruong.action_moihoacxinvaonhom(i)
                return

    def _chuyentruongdoi(self, s, doi):
        # Sửa đội giữa chừng, trưởng đội mới là người khác trong đội (mình vẫn trong đội): không dừng việc đang làm, báo trưởng đội mới
        # nhận đội (share "xong" kèm "chuyentruong", _nhantruongdoi) và mình thành thành viên của trưởng đội mới luôn; đang làm trưởng
        # nhóm trong game thì nhường cho trưởng đội mới (_xulynhomthanhvien)
        idmoi = doi["thanhviens"][0]
        self._ketthucdoiphoban(f"đổi trưởng đội sang {self._tenidnguoichoi(idmoi)}: chuyển đội, việc đang làm giữ nguyên", is_giaitan = False)
        self._doiphobanxong["chuyentruong"] = idmoi
        self._doiphobantv = {"ma": s["ma"], "idtruong": idmoi, "ten": doi["ten"], "viec": "", "lucviec": 0., "theosaucu": None,
                             "giaidoan": "", "luccuoi": time.time(), "lucroinhom": 0., "viecdoi": s["viec"],
                             "trangthai": "chờ trưởng đội mới nhận đội"}

    def _nhantruongdoi(self, d):
        # Trưởng đội cũ chuyển đội cho mình: thôi theo đội nhưng giữ việc đang chạy, trả Theo sau cũ (không theo trưởng đội cũ nữa) rồi
        # chạy đội luôn (việc đang chạy sẵn thì làm tiếp, không phải lập lại nhóm)
        tv = self._doiphobantv
        if tv and tv["theosaucu"] is not None:
            self._is_tudongtheosau, self._idmuctieutheosau, self._tenmuctieutheosau = tv["theosaucu"]
        self._doiphobantv = None
        self._logdoi(f"{self._tenidnguoichoi(d['idtruong'])} chuyển trưởng đội {d.get('ten', '')} cho mình: nhận đội, chạy tiếp")
        self.batdau_doiphoban(d["ma"])

    # --- Thành viên ------------------------------------------------------------------------------------------------------------------
    def _laydoicuatoi(self):
        # Share đội (cửa sổ khác) có mình là thành viên, None nếu không có. Trưởng đội có nhiều đội cùng chạy có mình (lỗi cấu hình) thì
        # theo đội mình đang theo, không thì đội đầu tiên thấy
        idtoi = self.moitruong.get_idnguoichoi()
        tv = self._doiphobantv
        thay = [d for _, d in self._laydoiphobancacsos() if idtoi in (d.get("thanhviens") or ()) and d.get("idtruong") != idtoi]
        if tv:
            cu = next((d for d in thay if d.get("ma") == tv["ma"] and d.get("idtruong") == tv["idtruong"]), None)
            if cu:
                return cu
        return next((d for d in thay if d.get("giaidoan") != "xong"), None)

    def _buocthanhviendoi(self):
        d = self._laydoicuatoi()
        tv = self._doiphobantv
        now = time.time()
        idtoi = self.moitruong.get_idnguoichoi()
        if d and d.get("giaidoan") == "xong" and d.get("chuyentruong") == idtoi \
                and ((laydoiphoban(d["ma"]) or {}).get("thanhviens") or [0])[0] == idtoi:
            self._nhantruongdoi(d)
            return
        if not d or d.get("giaidoan") == "xong":
            if tv and (d or now - tv["luccuoi"] > THOIGIANGIUDOIKHIMAT):
                self._thoidoithanhvien("đội xong / dừng" if d else f"mất tín hiệu trưởng đội quá {int(THOIGIANGIUDOIKHIMAT)}s")
            elif tv:
                tv["trangthai"] = f"mất tín hiệu trưởng đội, chờ (còn {int(THOIGIANGIUDOIKHIMAT - (now - tv['luccuoi']))}s)"
            return
        if not tv or tv["ma"] != d["ma"] or tv["idtruong"] != d["idtruong"]:
            if tv:
                self._thoidoithanhvien("sang đội khác")
            # Theo sau cũ đã lưu (bot tắt / mở lại giữa lúc theo đội) thì dùng lại để còn trả về đúng
            tv = self._doiphobantv = {"ma": d["ma"], "idtruong": d["idtruong"], "ten": d.get("ten", ""), "viec": "", "lucviec": 0.,
                                      "theosaucu": self._theosaucudoi, "giaidoan": "", "luccuoi": now, "lucroinhom": 0.}
            self._theosaucudoi = None
            self._logdoi(f"Vào đội {d.get('ten', '')} (trưởng đội {self._tenidnguoichoi(d['idtruong'])})")
        tv.update(luccuoi = now, giaidoan = d.get("giaidoan", ""), ten = d.get("ten", ""), viecdoi = d.get("viec", ""))
        if tv["giaidoan"] == "lam" and d.get("viec"):
            if tv["viec"] and (tv["viec"] != d["viec"] or tv["lucviec"] != d.get("lucviec")):
                self._dungviecthanhvien(tv)
            if not tv["viec"]:
                self._batdauviecthanhvien(tv, d)
            tv["trangthai"] = f"{VIECDOI_MAP.get(d['viec'], '')} cùng {self._tenidnguoichoi(d['idtruong'])}"
            return
        if tv["viec"]:
            self._dungviecthanhvien(tv)
        lydo = self._lydobanviecrieng(tv["viecdoi"])
        tv["trangthai"] = f"chờ đội ({d.get('trangthai') or tv['giaidoan']})" + (f", mình {lydo}" if lydo else "")

    def _xulynhomthanhvien(self, tv):
        # Đang ở nhóm không phải của trưởng đội thì rời (ngoài phó bản, phó bản không đang giữ nhóm); chưa có nhóm thì nhận lời mời của
        # trưởng đội (chỉ trưởng đội, không tự xin vào: xin vào chen ngang lời mời trưởng đội đang gửi người khác)
        moitruong = self.moitruong
        if moitruong.get_is_dangnamtrongnhom() and moitruong.get_is_truongnhom():
            # Mình làm trưởng nhóm (đổi trưởng đội giữa chừng / bot mở lại): trưởng đội trong nhóm thì nhường trưởng nhóm; chưa trong nhóm
            # mà mình đang trong phó bản (phó bản ăn theo nhóm, rời / giải tán là đóng phó bản) thì mời trưởng đội vào rồi nhường
            if tv["idtruong"] in (moitruong.get_danhsachidnguoichoithanhviennhoms() or ()):
                if time.time() - tv["lucroinhom"] > 1.5:
                    tv["lucroinhom"] = time.time()
                    self._logdoi(f"Nhường trưởng nhóm cho trưởng đội {self._tenidnguoichoi(tv['idtruong'])}")
                    moitruong.action_nhuongquyentruongnhom(tv["idtruong"])
                return
            if self._is_trongphobandoi():
                if time.time() - tv["lucroinhom"] > GIANCACHMOILAIDOI:
                    tv["lucroinhom"] = time.time()
                    self._logdoi(f"Trong phó bản, mình là trưởng nhóm: mời trưởng đội {self._tenidnguoichoi(tv['idtruong'])} vào nhóm để nhường")
                    moitruong.action_moihoacxinvaonhom(tv["idtruong"])
                return
        if self.get_is_tamtattodoilanglyson():
            # Phó bản đang giải tán tổ đội cũ / Phong Yêu Kính đang lập nhóm 1 người: action_roinhomlanglyson lo rời, chưa nhận lời mời
            return
        if moitruong.get_is_dangnamtrongnhom():
            if moitruong.get_idnguoichoitruongnhom() == tv["idtruong"] or self.get_is_giunhomlanglyson() or self._is_trongphobandoi():
                return
            if time.time() - tv["lucroinhom"] > 1.5:
                tv["lucroinhom"] = time.time()
                self._logdoi(f"Rời nhóm hiện tại để vào nhóm trưởng đội {self._tenidnguoichoi(tv['idtruong'])}")
                moitruong.action_thoatkhoinhom()
            return
        moitruong.action_kiemtravadongyloimoinhom([tv["idtruong"]])

    def _batdauviecthanhvien(self, tv, d):
        # Bật cùng việc với trưởng đội (chế độ thành viên) và Theo sau trưởng đội; Theo sau cũ nhớ lại để trả khi thôi đội
        if tv["theosaucu"] is None:
            tv["theosaucu"] = (self._is_tudongtheosau, self._idmuctieutheosau, self._tenmuctieutheosau)
        if d["viec"] in ("phongyeukinh", "tapkich"):
            # Tập Kích: trong phó bản đánh theo cấu hình Theo sau hiện tại; ngoài phó bản _xulytapkich tự ép Theo sau trưởng đội lúc đi
            # tìm Võ Lâm Bại Hoại rồi trả lại khi vào phó bản (trước ép ở đây nên vào phó bản vẫn bám trưởng đội).
            # Phong Yêu Kính: thành viên tự nói chuyện Tả Khâu Minh vào, tắt Theo sau thì tự dò lệch điểm với trưởng đội (_buoctrongphongyeu).
            # Không ép bật Theo sau: giữ đúng ô Theo sau đang đặt (không lấy Theo sau cũ đã lưu: mở lại bot thì nó bật lại dù đã tắt tay),
            # trừ khi Theo sau đang là do đội ép bật ở việc trước (Lăng Ly Sơn / Thành Kiều) thì trả về Theo sau cũ
            if self._is_tudongtheosau and self._idmuctieutheosau == int(d["idtruong"]):
                self._is_tudongtheosau, self._idmuctieutheosau, self._tenmuctieutheosau = tv["theosaucu"]
            tv["theosaucu"] = (self._is_tudongtheosau, self._idmuctieutheosau, self._tenmuctieutheosau)
        else:
            self._is_tudongtheosau = True
            self._idmuctieutheosau = int(d["idtruong"])
            self._tenmuctieutheosau = self._tenidnguoichoi(d["idtruong"])
        tv.update(viec = d["viec"], lucviec = d.get("lucviec", 0.))
        if self.get_viecdanglam() != d["viec"]:
            self._logdoi(f"Bật {VIECDOI_MAP.get(d['viec'], d['viec'])} (thành viên)"
                         + (f", Theo sau {self._tenmuctieutheosau}" if self._is_tudongtheosau else ", không Theo sau (tự dò)"))
            self._batviecdoi(d["viec"], d.get("phai"))

    def _dungviecthanhvien(self, tv):
        viec = tv["viec"]
        tv.update(viec = "", lucviec = 0.)
        if viec and self.get_viecdanglam() == viec:
            self._logdoi(f"Trưởng đội đã xong / đổi việc: dừng {VIECDOI_MAP.get(viec, viec)}")
            self._dungviec(viec)

    def _thoidoithanhvien(self, lydo):
        tv = self._doiphobantv
        if not tv:
            return
        self._dungviecthanhvien(tv)
        if tv["theosaucu"] is not None:
            self._is_tudongtheosau, self._idmuctieutheosau, self._tenmuctieutheosau = tv["theosaucu"]
        self._doiphobantv = None
        self._trangthaidoiphoban = f"{time.strftime('%H:%M')} Thôi đội {tv.get('ten', '')}: {lydo}"
        self._logdoi(f"Thôi đội {tv.get('ten', '')}: {lydo}")

    def _logdoi(self, noidung):
        self.moitruong._inlog(f"[ĐỘI PHÓ BẢN] {noidung}")
