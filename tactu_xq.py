import os
import time
import pymem

from hangso_xq import *
from moitruong_xq import MoiTruong, DOUUTIEN_THAP, DOUUTIEN_KHANCAP, DOUUTIEN_CAO, SOLUONGDOITUONGXUNGQUANHTOIDA, tinh_is_huongmatvediem
from tienich_xq import luuthietlap as util_luuthietlap
from tienich_xq import taithietlap as util_taithietlap, duongdanthietlap as util_duongdanthietlap, phatam
from dexuatlotrinh_xq import taiviquai as util_taiviquai, luuviquai as util_luuviquai, taiviquaibando, ghinhanvitriquai, dexuatlotrinh
from dexuatlotrinh_xq import THOIGIANGHIVITRIQUAI, THOIGIANLUUVITRIQUAI, SOLANTHAYQUAITOITHIEU, TENMAUDEXUAT
from tactu_dichuyen_xq import TacTuDiChuyen
from tactu_muctieu_xq import TacTuMucTieu
from tactu_kynang_xq import TacTuKyNang
from tactu_vatpham_xq import TacTuVatPham
from tactu_baothu_xq import TacTuBaoThu
from tactu_hoatdong_xq import TacTuHoatDong
from tactu_giaodo_xq import TacTuGiaoDo
from tactu_catkho_xq import TacTuCatKho
from tactu_sumon_xq import TacTuSuMon
from tactu_langlyson_xq import TacTuLangLySon
from tactu_sugia_xq import TacTuSuGia
from tactu_tapkich_xq import TacTuTapKich
from nhiemvu_xq import SoVitri


# Các nhóm việc nằm ở các file tactu_*_xq.py (mixin), TacTu giữ trạng thái (__init__), lưu / nạp thiết lập và các lệnh bật / tắt
class TacTu(TacTuDiChuyen, TacTuMucTieu, TacTuKyNang, TacTuVatPham, TacTuBaoThu, TacTuHoatDong, TacTuGiaoDo, TacTuCatKho, TacTuSuMon,
            TacTuLangLySon, TacTuSuGia, TacTuTapKich):
    def __init__(self, moitruong: MoiTruong):
        self._thoidiemhettangbaodogannhat = 0.
        self._thoidiemmuaautogannhat = 0.
        # Đào tàng bảo đồ tạm nghỉ tới thời điểm này (thay cho sleep 1s sau mỗi lần đào, 5s khi hết đồ/vừa phù sang nước khác)
        self._thoidiemchodaotangbaodo = 0.
        self._thoidiemsudungditinhdaiphapgannhat = 0.
        self._thoidiemsudungluuhuyetthuatgannhat = 0.
        self._thoidiemkiemtranpcmuavatphamgannhat = 0.
        self._is_tudongmuavatpham = True
        self._diachicosovatphamnhatduphong = False
        self._idquaidautien = 0
        self._thoidiemsudungthaotacbaothugannhat = 0.
        self._thoidiemtamngungsudungkynang = 0.
        self._thoidiemhoiphucbaothugannhat = 0.
        self._is_tudongdieukhienbaothu = True
        self._is_baothukynangtrieuhoihetnoiluc = False
        self._is_baothukynangtrieuhoihetsinhluc = False
        self._thoidiemdocsachgannhat = 0.
        self._thoidiemsudungbattiendongannhat = 0.
        self._thoidiemdichientruonggannhat = 0.
        # Các lệnh hội thoại Trương Quả Lão còn chờ gửi, cách nhau >= 0.25s (trước đây sleep 0.25s sau mỗi lệnh, chặn loop phụ)
        self._hangdoilenhchientruong = []
        self._thoidiemguilenhchientruongtieptheo = 0.
        self._thoidiembatdaudendiem = 0.
        self._thoidiemlogdebug = 0.
        self._solanthatbaikhaithien = 0
        self._solanthatbaikhaithientoida = 3
        self._thoidiembiphatkhaithien = 0.
        self._is_thucsondao = False
        self.moitruong = moitruong

        self._is_tudongtheosau = True
        # Người được theo sau: 0 = trưởng nhóm, khác 0 = ID nhân vật cùng máy (ID cố định, tên chỉ để hiển thị vì có thể đổi)
        self._idmuctieutheosau = 0
        self._tenmuctieutheosau = ""
        self._diachimuctieutheosau = 0
        self._bonhotoadomuctieutheosau = (0., False)
        self._is_tudongtimkiemmuctieu = True
        self._is_tudongsudungkynang = True
        self._is_tudongsudungvatpham = True
        self._is_tudongnhatvatpham = True
        self._is_chidanhnguoichoi = False
        self._is_tudongtodoi = True
        self._is_tudongphucsinh = True
        self._is_tudongsuavatpham = True
        self._is_tudongtrieuhoibaothugiangho = False
        self._is_tudongchaylenbandovuachet = True
        self._is_tudongxepchongvatpham = True
        self._is_tudongkhaikhoang = False
        self._thoidiemkhaikhoanggannhat = 0.
        self._yeucaukhaikhoang = None

        self._diachicosomuctieuduphong = 0
        self._diachicosokhaikhoang = 0
        self._idkhoangbiloi_map = {}
        self._idkhoangdangtheo = 0
        self._thoidiembatdautheokhoang = 0.
        self._idbandolanquetkhaikhoangtruoc = 0
        self._is_nhieumuctieugan3 = False
        self._is_nhieumuctieugan5 = False
        self._is_nhieumuctieugan7 = False
        self._is_nhieumuctieugan9 = False
        self._is_nhieumuctieuganbanthan3 = False
        self._is_nhieumuctieuganbanthan5 = False
        self._is_nhieumuctieuganbanthan7 = False
        self._is_nhieumuctieuganbanthan9 = False
        self._soluongnhieumuctieu = 2
        self._soluongquaigomtoithieu = 3
        self._is_tudonggomquai = False
        self._is_danggomquai = False
        self._danhsachidquaidagom = set()
        # Tập Kích Môn Phái: quái đã gom ít nhất 1 lần trong lượt gom này (rớt lại vẫn giữ, không kéo lại)
        self._danhsachidquaidagommotlan = set()
        self._yeucaugomquai = None

        self._is_uutienmuctieupk = True
        self._khoangcachtoidatheosau = 6.
        # Tầm dùng kỹ năng tầm xa (chỉnh ở giao diện, lưu theo nhân vật)
        self._khoangcachsudungkynangtamxa = KHOANGCACHSUDUNGKYNANGTAMXA
        # Thục Sơn: % nội lực tối thiểu để dùng Khai Thiên Tịch Địa lướt khi di chuyển (chỉnh ở giao diện, lưu theo nhân vật)
        self._phantramnoiluckhaithientichdia = PHANTRAMNOILUCKHAITHIENTICHDIA
        # Côn Luân: hết mốc này mới gửi chiêu sau khi lướt Đằng Vân Giá Vũ (xem THOIGIANKHOACHIEUSAULUOT)
        self._thoidiemhetkhoachieusauluot = 0.
        # Tầm đánh thực tế của nhân vật (học từ lần tiếp cận mục tiêu gần nhất), mặc định tầm xa đã trừ hao
        self._khoangcachvoitoimuctieu = self._khoangcachsudungkynangtamxa - TRUHAOTAMXACHONMUCTIEU
        # Đang trên đường về chỗ đứng riêng quanh trưởng nhóm
        self._is_dangvevitritheosau = False
        # Trưởng nhóm (cùng máy) ở bản đồ khác mà phù tới được => đang lo phù sang, lộ trình điểm đánh tạm nhường
        self._is_dangphutheosau = False
        self._idbandotheosaugannhat = None
        self._thoidiemdoibandotheosau = 0.
        self._thoidiemphutoibandogannhat = 0.
        # Đang nói chuyện NPC để sang bản đồ khác (bando_xq.LOIDINPC_MAP, vd. vào Lăng Ly Sơn): {"idbando", "manpc", "luc", "dachon"} hoặc None
        self._hoithoailoidinpc = None
        # Đi tới bản đồ (thietlap_ditoibando): id bản đồ đích, 0 = không đi. Bước di chuyển tiếp theo (mô tả, lúc cập nhật) cho giao diện
        self._idbandocandi = 0
        # Hàng chờ giao tiền / đồ (tactu_giaodo_xq): [yêu cầu giaodo_xq kèm trạng thái]
        self._hangchogiaodo = []
        # Việc cất kho đang làm (tactu_catkho_xq, None = không) và kết quả lần gần nhất cho giao diện
        self._catkho = None
        self._ketquacatkho = ""
        # Các lần cất kho trong THOIGIANGIULICHSUCATKHO giây gần nhất: [[thời điểm, {tên món: số lượng}]] cho báo cáo định kỳ Telegram
        self._lichsucatkho = []
        # Nhiệm vụ sư môn (tactu_sumon_xq): việc đang làm (None = không), kết quả lần gần nhất cho giao diện, NPC giao nhiệm vụ người dùng
        # đặt (rỗng = mặc định theo môn phái, lưu theo nhân vật); vị trí NPC / quái đã thấy (nhiemvu_xq.SoVitri) và lần ghi gần nhất
        self._sumon = None
        # Điểm dò quanh toạ độ nhiệm vụ {(bản đồ, toạ độ): [điểm]} và vùng tới được từ chỗ đứng (bản đồ, {ô: số bước}) (_laydiemdoquanh,
        # _layvungtoiduoc)
        self._diemdoquanh_cache = {}
        self._vungtoiduoc_cache = None
        self._ketquasumon = ""
        self._sumon_npcgiao = ""
        self._sovitri = SoVitri()
        self._thoidiemghivitridoituong = 0.
        # Tự động đi Lăng Ly Sơn (tactu_langlyson_xq): việc đang làm (None = không), kết quả lần gần nhất cho giao diện
        self._langlyson = None
        self._ketqualanglyson = ""
        # Thành viên theo sau: mã thưởng Lăng Ly Sơn đã tự lĩnh (báo trưởng nhóm qua shared_data), việc đang lĩnh dở (None = không)
        self._khoathuonglanglysondalanh = ""
        self._lanhthuonglanglyson = None
        # Lần rời nhóm gần nhất khi giải tán tổ đội cũ (Tổ đội tự động tạm nghỉ)
        self._thoidiemroinhomlanglyson = 0.
        # Lần đọc gần nhất (lúc, kết quả) "mình là thành viên vòng Lăng Ly Sơn đang đi" từ shared_data
        self._bonhogiunhomlanglyson = (0., False)
        # Lần chọn menu "ta muốn vào" Phong Yêu Kính gần nhất (tactu_langlyson_xq._xulymenuphongyeu)
        self._lucchonmenuphongyeu = 0.
        # Nhiệm vụ Sư Gia (tactu_sugia_xq): việc đang làm (None = không), kết quả lần gần nhất cho giao diện; thành viên: việc trả nhiệm vụ
        # đang dở, lần chọn "Nhận" theo trưởng nhóm gần nhất, (lúc, trạng thái) nhiệm vụ của mình báo qua shared_data
        self._sugia = None
        self._ketquasugia = ""
        self._sugiathanhvien = None
        self._lucnhanmoisugia = 0.
        self._lucxinmotasugia = 0.
        self._bonhonhiemvusugia = (0., "")
        # Tập Kích Môn Phái (tactu_tapkich_xq): việc đang làm (None = không), kết quả lần gần nhất cho giao diện, môn phái chọn (lưu theo
        # nhân vật, rỗng = môn phái của nhân vật); lần chọn menu vào / bấm hộp Xác Nhận gần nhất, lần chọn "Dùng 5 Ngân Bảo" gần nhất
        self._tapkich = None
        self._ketquatapkich = ""
        self._tapkich_phai = ""
        self._lucchonmenutapkich = 0.
        self._lucchonvaotapkich = 0.
        # Mở cửa hàng để đọc hàng (tactu_sumon_xq.batdau_mocuahang): việc đang làm (None = không), kết quả theo (bản đồ, tên NPC);
        # Mua bù: lần mở cửa hàng gần nhất theo NPC, các lệch ô / giá giữa luật và cửa hàng đã báo
        self._mocuahang = None
        self._ketquamocuahang = {}
        self._lucmocuahangmuabu_map = {}
        self._lechmuabudabao = set()
        self._buocdichuyen = ("", 0.)
        # Các lần Hồi Thành Phù gần đây (chặn lặp tốn tiền, get_lydokhonghoithanhphu)
        self._thoidiemhoithanhphus = []
        # Tên vật phẩm -> lần gần nhất báo không đủ tiền mua (5 phút báo 1 lần)
        self._thoidiembaothieutienmuagannhat_map = {}
        # Hội thoại NPC nhiều bước (Tân Thủ Tiên Cô...): các câu lệnh còn chờ gửi, cách nhau 1s, gửi hết thì đóng cửa sổ tuỳ chọn.
        # Trước đây gửi xong mỗi bước thì sleep 1s ngay trong loop. Chỉ loop phụ gửi (action_xulyhoithoainpc)
        self._hangdoihoithoainpc = []
        self._thoidiemguihoithoainpctieptheo = 0.
        self._is_chodongcuasohoithoainpc = False
        # Thời điểm bắt đầu nằm chết (0 = đang sống); chờ đủ THOIGIANCHOTRUOCKHIPHUCSINH mới phục sinh
        self._thoidiembatdauchet = 0.
        # Khi chạy theo lộ trình: quái phải cách một điểm đánh không quá bấy nhiêu ô mới được nhận làm mục tiêu/gom
        self._bankinhdiemdanh = 18.

        self._tenmuctieutancongs = set()
        self._tenmuctieukhongtancongs = set(TENMUCTIEUKHONGTANCONGs)
        self._tenvatphamnhats = set()
        # Phẩm chất (màu tên, PHAMCHATVATPHAM_MAP) vật phẩm dưới đất được nhặt dù tên không nằm trong danh sách nhặt
        self._phamchatnhats = set()

        self._thoidiemtamngungkhaithientichdia = time.time()
        self._thoidiemkiemtrahieuunggannhat = time.time()
        self._thoidiemnhatvatphamgannhat_map = {}
        self._thoidiemdoimaupkgannhat = time.time()
        self._thoidiemtudongtrieuhoibaothugiangho = time.time()
        self._thoidiemsudungvatphamgannhat = time.time()
        self._thoidiemsudungthucanbaothugannhat = time.time()
        self._thoidiemsudungvatphamhoinoilucgannhat = time.time()
        self._thoidiemsudungvatphamhoisinhlucgannhat = time.time()
        self._thoidiemsudungthanhtamdangannhat = time.time()
        self._thoidiemsudunghoithanhphugannhat = time.time()
        self._thoidiemxepchongvatphamgannhat = time.time()
        # Xếp chồng tự nhận biết (_get_soluongneuxepchongduoc): số lớn nhất từng thấy 1 ô theo tên; lần gộp đang chờ kết quả
        # (id nguồn, id đích, số lượng nguồn, số lượng đích, lúc chuyển) và các cặp id đã biết không gộp được (khác trạng thái khoá)
        self._soluongchonglonnhat_map = {}
        self._langopgannhat = None
        self._capkhonggopduocs = set()
        # Sắp xếp hành trang (bấm nút trên bảng điều khiển): mỗi lượt chuyển 1 vật phẩm, xem action_sapxephanhtrang.
        # {tên: loại vật phẩm trong mô tả, vd "Có thể sử dụng", "Tinh luyện", "" nếu không có}: cùng tên cùng loại nên nhớ theo tên,
        # chỉ desc tên chưa biết (_docloaivatpham)
        self._loaivatpham_map = {}
        # Luật túi đồ (luattuido_xq): {tên: mô tả bỏ dòng tên} cho điều kiện "mô tả chứa", lần vứt theo luật gần nhất,
        # {id món: lúc được thử vứt lại} (game không cho vứt thì khỏi gửi mãi), {tên: lần mua bù gần nhất}
        self._motavatpham_map = {}
        self._thoidiemvuttheoluatgannhat = 0.
        self._thoidiemthulaivut_map = {}
        self._thoidiemmuabu_map = {}
        self._thoidiemdoclaimota_map = {}
        # Tự động đặt vật phẩm mới vào chỗ hợp lý (action_tudongdatvatphammoi): id hành trang lượt trước, {id món mới: [lúc thấy,
        # số lần đã chuyển]}
        self._is_tudongdatvatphammoi = True
        self._idhanhtrangtruoc = None
        self._vatphammoi_map = {}
        self._thoidiemdatvatphammoigannhat = 0.
        # Đổi chỗ 2 viên đá khi túi đầy: (id món trung gian, id đá cần đặt, ô đích, lúc gửi bước 1), xem _timbuocsapxephanhtrang
        self._xoayvongsapxep = None
        self._is_dangsapxephanhtrang = False
        self._thoidiembatdausapxephanhtrang = 0.
        self._thoidiemsapxephanhtranggannhat = 0.
        self._solandichuyensapxep = 0
        self._lenhsapxepgannhat = None
        self._solanlaplenhsapxep = 0
        # Giữ ô cuối hành trang 1 luôn trống (action_giuotrongcuoihanhtrang): id vật phẩm đang chuyển đi, số lần chuyển chưa được,
        # thời điểm chuyển gần nhất; id -> thời điểm hết bỏ qua (chuyển mãi không được thì nghỉ một lúc, không spam lệnh)
        self._idvatphamotrongdangchuyen = 0
        self._solanchuyenotrongthatbai = 0
        self._thoidiemchuyenotronggannhat = 0.
        self._thoidiemhetboquaotrong_map = {}
        self._thoidiemphatamchuyenotronggannhat = 0.
        self._thoidiemvutvatphamgannhat = time.time()
        self._diachicosovatphamkhongnhat_map = {}
        self._thoidiemthaydoivatphamdangnhatgannhat = time.time()
        self._diemdanhxungquanhs = []
        self._iddiemdanhxungquanhhientai = -1
        # Điểm đánh đặt / nạp trong phó bản mượn ID bản đồ ngoài (Phong Yêu Kính): ra khỏi phó bản thì tự bỏ hết, kẻo chạy lên bản đồ thật
        self._is_lotrinhphobanmuonbando = False
        # Các thời điểm còn phải ngắt di chuyển sau khi vừa bỏ điểm đánh lúc ra khỏi phó bản đó
        self._thoidiemngatdichuyenroiphobans = []
        self._thoidiemroiphobanmuonbando = 0.
        # Tắt thì lộ trình chỉ đi các điểm cùng bản đồ đang đứng, không chạy sang bản đồ khác
        self._is_dilotrinhkhacbando = True
        # Lộ trình mẫu đang dùng dạng "<id bản đồ>|<tên mẫu>|<1 nếu đi ngược chiều>", rỗng nếu tự đặt điểm
        self._lotrinhmaudangdung = ""
        # Số điểm đã đi qua của lộ trình dò (mẫu TENMAUDO) kể từ lúc nạp / lần xét trước: đủ 1 vòng thì xét chuyển sang lộ trình thật
        self._sodiemdadilotrinhdo = 0
        # Ô "Đi ngược chiều" trên giao diện: chiều ưu tiên khi tự chọn lộ trình mẫu (tuchon_lotrinhmau), lưu theo nhân vật
        self._is_nguocchieulotrinh = False
        self._is_lotrinhtuchon = False
        self._thoidiemkiemtralotrinhgannhat = 0.
        # Tạm ngưng toàn bộ hoạt động khi phát hiện người chơi ẩn thân xung quanh (đang di chuyển theo lộ trình điểm đánh)
        self._thoidiemhettamngung = 0.
        self._lydotamngung = ""
        self._thoidiemkiemtraanthangannhat = 0.
        # Lần gần nhất TỰ phát hiện ẩn thân (chia sẻ cho nhân vật khác cùng bản đồ)
        self._thoidiemphathienanthan = 0.
        self._tenanthanphathien = ""
        self._thoigiantamngungphathien = 0.
        # Gán từ CuaSo để biết các cửa sổ khác đang dùng lộ trình mẫu nào
        self.shared_data = None
        self.idcuaso = None
        self._diemdanhxungquanhhientai = None
        self._thoidiemloggomquai = 0.

        self._idmuctieubiloi_map = {}
        # id -> (tên, lý do) mục tiêu đang bị bỏ qua, để giao diện hiện danh sách (get_danhsachmuctieuboqua)
        self._thongtinmuctieuboqua_map = {}
        self._thoidiemthaymuctieu_map = {}
        # Theo dõi đòn có trúng mục tiêu đang đánh không (xem _kiemtramuctieukhongtrungchieu)
        self._theodoitrungchieu = None
        self._idmuctieudangtheokiemtraket = 0
        self._thoidiemdungimkiemtraket = 0.

        self._yeucaunhatvatpham = None
        self._yeucautheosau = None
        self._yeucautancong = None
        self._yeucautudo = None

        # Kỹ năng vừa gửi cần ngắt di chuyển: hạn chờ nhân vật vào tư thế xuất chiêu (0 = không chờ), xem action_ngatdichuyenkhixuatchieu
        self._thoidiemhetchongatdichuyen = 0.
        self._thoidiemhetchantudichuyentruocxuatchieu = 0.
        # Kỹ năng is_yeucaukhongdichuyen vừa gửi: tạm ngưng di chuyển tới mốc này (mỗi lượt di chuyển / luồng nhanh đều ngắt di chuyển)
        self._thoidiemtamngungdichuyensudungkynang = 0.
        self._thoidiemhetgiuchieudangra = 0.
        # Giữ chiêu đang ra (Ngự Kiếm Phi Tiên, Tiểu Chu Thiên): lúc gửi chiêu, đã thấy tư thế ra chiêu chưa
        self._thoidiembatdaugiuchieudangra = 0.
        self._is_dathaychieudangra = False
        self._thoidiemsudungloidongcuuthiengannhat = 0.
        self._khoangcachtimkiemmuctieu = 18.
        self._is_tudongdichuyendiemdanhxungquanh = False
        self._is_tudongdoimaupk = False

        self._idbandovuachet = 0
        self._diachicosovatphamdangnhat = 0

        self._solansudungkhaithientichdia = 0
        self._solansudungluutinhtruymang = 0

        self._is_chantangcapdo = False
        self._idbandomuctieudangchon = 0

        self._idquaidangkeo = 0
        self._thoidiembatdaukeo = 0.
        self._thoidiemraidauthanhbinhgannhat = 0.
        # ID đối tượng mục tiêu -> lần dùng Phong Vũ Kinh Thiên gần nhất lên nó
        self._thoidiemphongvukinhthien_map = {}
        self._idgomtheodoiket = 0
        self._khoangcachgomtotnhat = 0.
        self._thoidiemgomcaithiengannhat = 0.
        self._is_tudongvebanrac = False
        self._trangthaiveban = 0  # 0: Idle, 1: Đang về, 2: Đang đi shop, 3: Đang bán, 4: Đang quay lại
        self._thoidiemchuyentrangthai = 0.

        self._thoidiemhoithanhphu = 0.  # Timer cho việc hồi thành phù
        # Bán rác/sửa đồ chạy dần theo từng lượt của loop phụ (trước đây sleep 1s mỗi món, chặn cả loop phụ hàng chục giây)
        self._hangdoibanrac = []  # câu lệnh bán còn chờ gửi, 1 lệnh/giây
        self._thoidiemguibanractieptheo = 0.
        self._thoidiemhetsuavatpham = 0.  # > 0: đang đi tìm Chủ Tiệm Sửa Chữa, bỏ cuộc lúc này
        self._thoidiemkiemtrasuavatpham = 0.
        self._buocbanrac = 0  # bước 3 (đang bán) của về bán rác: 0 chưa bán, 1 đang bán, 2 đang sửa đồ, 3 đang cất kho, 4 đang giao đồ
        self._thoidiemthulaibanrac = 0.
        self._thoidiembatdautimnpcbanrac = 0.  # phái khác, bước 2: bắt đầu đi tìm NPC tạp hoá (bỏ cuộc sau 45s)
        self._thoidiemkiemtranpcbanrac = 0.

        self._toadokiemtraket = (0, 0)
        self._thoidiembatdaukiemtraket = 0.

        self._thoidiemphatamlacmapgannhat = 0.
        self._thoidiemphatamlotrinhkhacbandogannhat = 0.
        self._thoidiemphatamdayhanhtrang = 0.
        self._thoidiemphatambaothuhethan = 0.
        self._is_tudongdichientruong = False

        self._is_yeucauvohieuhoadichuyen = False
        self._is_uutienbaothukynangtrieuhoi = False
        self._is_khonguutienbaothugiangho = False

        self._is_chedobufftoanbang = False
        self._is_khongcongidebuff = False

        self._thoidiemsudungbaothuvatphamgannhat = time.time()
        self._thoidiemkiemtrakhongcongidebuffgannhat = 0.

        self._is_battudongtancongvatly = False
        self._diachimuctieutancongvatly = 0
        # Lần gửi "pf2 14" gần nhất để ngắt đánh thường (_ngattancongvatlydaohoa)
        self._thoidiemguingattancongvatly = 0.
        # Lúc Nguyên Khí Quy Nguyên được bật gần nhất theo tin game (None = chưa biết) và tin cuối đã xét (_lammoinguyenkhiquynguyen)
        self._thoidiembatnguyenkhiquynguyen = None
        self._thoidiemxettinnguyenkhiquynguyen = 0.
        # Nhất Quyền lượt trước có sẵn sàng không, lúc nó vừa vào hồi chiêu (_get_thoigianconlaihoichieunhatquyen)
        self._is_nhatquyensansangtruoc = False
        self._thoidiemnhatquyenvaohoichieu = 0.
        self._khoalogdichuyencuoi = None
        self._thoidiemtodoigannhat_map = {}
        self._thoidiemxulytodoigannhat = 0.
        # Tổ đội 1 lần (Ctrl+Alt+T, tactu_hoatdong_xq): mình là trưởng nhóm đang gom người {"lucbatdau", "thanhviens", "dangmoi": ID đang mời,
        # "lucmoi"}, None = không;
        # trạng thái lần gần nhất cho giao diện; (lúc, id trưởng nhóm) lần đọc shared_data "có ai đang gom mình không"; lúc rời nhóm cũ gần nhất
        self._todoimotlan = None
        self._trangthaitodoimotlan = ""
        self._bonhotodoimotlan = (0., (0, False))
        self._thoidiemroinhomtodoimotlan = 0.
        # Đồng đội hạng cao hơn đang được mời vào nhóm (để biết đã mời bao lâu)
        self._idmoihangcaohon = 0
        self._thoidiembatdaumoihangcaohon = 0.
        self._thoidiemroinhomtodoigannhat = 0.
        # Nhóm khác ưu tiên cao hơn cùng bản đồ: (id trưởng nhóm đó, thời điểm bắt đầu thấy liên tục) để chỉ rời khi thấy đủ lâu
        self._nhomuutiencaohon = (0, 0.)
        self._thoidiemcaituhoansinh_map = {}

        self._thoidiemsudungamkichgannhat = 0.
        self._is_kynangamkichsansang = False

        self._thoidiemsudungthichsatgannhat = 0.
        self._is_kynangthichsatsansang = False

        self._thoidiemsudungbisatgannhat = 0.
        self._is_kynangbisatsansang = False

        self._thoidiemsudungnhiephonchamgannhat = False
        self._is_kynangnhiephonchamsansang = False

        self._thoidiembattathieuungphapbaogannhat = 0.

        self._is_kynangmatamthuatsansang = False
        self._thoidiemsudungmatamthuatgannhat = 0.

        self._is_tudongdaotangbaodo = False
        self._yeucaudaotangbaodo = None

        self._thoidiembuffkimchamgannhat_map = {}
        self._thoidiembuffnganchamgannhat_map = {}
        self._thoidiembuffcuongthethuatgannhat_map = {}

        self._is_nganchamdoachsansang = False
        self._is_kimchamdoachsansang = False
        self._is_cuongthethuatsansang = False

        self._idnguoichoibuffnganchamgannhat = 0
        self._idnguoichoibuffkimchamgannhat = 0
        self._idnguoichoibuffcuongthethuatgannhat = 0

        self._thoidiembuffnoikhanggannhat_map = {}
        self._is_tieuchuthiensansang = False
        self._idnguoichoibuffnoikhanggannhat = 0

        self._solanthatbailuutinhtruymang = 0
        self._solanthatbailuutinhtruymangtoida = 3
        self._thoidiembiphatluutinhtruymang = 0.
        self._thoidiemtamngungluutinhtruymang = 0.
        self._idmuctieuluutinhtruymang = 0

        self._is_khaithientichdiasansang = False
        self._is_luutinhtruymangsansang = False

        self._is_dangchaybukhoangcach = False
        self._thoidiemvohieuquadichuyennhatvatpham = 0.0
        # Tránh vùng cấm (VUNGCAM_MAP) khi chọn mục tiêu, nhặt đồ, gom quái và di chuyển
        self._is_tranhvungcam = True
        # Giữ khoảng cách với đối tượng đang tấn công mình (chỉnh ở giao diện, lưu theo nhân vật)
        self._is_giukhoangcachketancong = False
        self._khoangcachgiuketancong = KHOANGCACHGIUKETANCONG
        # Chỉ giữ khoảng cách với mục tiêu PK (người chơi / bảo thú); tắt để thử với cả quái
        self._is_giukhoangcachchimuctieupk = True
        # Tập hỏa khi đang theo sau: người được theo sau cùng máy thì đánh đúng mục tiêu họ chọn, khác máy thì mục tiêu gần họ nhất.
        # Tắt (mặc định): ưu tiên mục tiêu gần bản thân (vẫn chỉ chọn trong vùng quanh người được theo sau)
        self._is_taphoa = False
        # Yêu cầu lùi đang có (None = không cần lùi); tính lại mỗi THOIGIANTINHGIUKHOANGCACH giây trong action_xulyuutiendichuyen
        self._yeucaugiukhoangcach = None
        self._thoidiemtinhgiukhoangcachgannhat = 0.
        # id đối tượng -> lần gần nhất thấy nó ra đòn quay mặt về mình
        self._thoidiemketancong_map = {}
        # Vị trí quái đã thấy theo bản đồ để tự đề xuất lộ trình (dexuatlotrinh_xq): bảng của nhân vật đang chơi (ID _idnguoichoiviquai),
        # lần ghi / lưu file gần nhất
        self._bangviquai = {}
        self._idnguoichoiviquai = None
        self._thoidiemghiviquaigannhat = 0.
        self._thoidiemluuviquaigannhat = 0.
        # Tầm nhìn chung đọc từ cửa sổ khác cùng máy (xem _laytamnhinchung)
        self._tamnhinchung = {}
        self._thoidiemdoctamnhinchunggannhat = 0.
        # Hết mục tiêu thì đi tới mục tiêu nhân vật khác cùng máy thấy (_timmuctieuchung): tùy chọn, yêu cầu di chuyển,
        # (id, lúc bắt đầu) mục tiêu đang đi tới, id -> thời điểm hết bỏ qua
        self._is_timmuctieuchung = True
        self._yeucautimmuctieuchung = None
        self._muctieuchungdangtim = None
        self._thoidiemhetboquamuctieuchung_map = {}
        # Hướng đang lùi (8 hướng) + lúc / chỗ bắt đầu đo để phát hiện kẹt tường; hướng -> thời điểm hết chặn
        self._luigiukhoangcachdangchay = None
        self._thoidiemhetchanhuonglui_map = {}
        # Còn kỹ năng quan trọng dùng được không (xét trong danh sách kỹ năng của phái, xem _capnhatkynangquantrong)
        self._is_cokynangquantrongdungduoc = False
        self._thoidiemxetkynangquantronggannhat = 0.
        # Theo sau: người được theo sau ở bản đồ khác => tự tìm đường tới bản đồ đó (phù / Hồi Thành Phù / chạy bộ như Đi tới bản đồ).
        # Tắt thì chỉ theo sau trong cùng bản đồ
        self._is_tutimduongtheosau = True

        self._diachidoituongcanbuffthuccotmaoson = None
        self._diachidoituongcanbuffthucgiapmaoson = None
        self._diachidoituongcanbuffthuctammaoson = None
        self._diachidoituongcanbuffammanhapthemaoson = None
        self._thoidiemnhichgannhat = 0.

        # Đổi pháp bảo khi máu thấp: lúc ra lệnh đổi gần nhất, tên pháp bảo đang đeo trước khi đổi (None = không đang đổi,
        # "" = trước đó không đeo), % máu lúc đổi, lần thử đeo lại gần nhất
        # Đổi đồ khi vận khí gọi bảo thú triệu hồi (action_doidokhitrieuhoi): bật đeo đồ ô 0-5 (Mao Sơn), bộ đồ đang mặc lúc bắt đầu
        # vận khí {ô trang bị: (id, tên)} (None = không đang đổi), hàng đợi (id, tên) cần đeo, lần ra lệnh đeo / mặc lại gần nhất,
        # số lần mặc lại, lần nạp mô tả ô 0-5 gần nhất
        self._is_doidokhitrieuhoi = False
        # Bộ đồ triệu hồi đã ghi (ghi_bodotrieuhoi): [{"vitri": ô trang bị, "ten", "vantay": dấu vân tay mô tả}], lưu theo nhân vật
        self._bodotrieuhoi = []
        # Triệu hồi bảo thú kỹ năng nào (BAOTHUTRIEUHOIMAOSONs, dùng chung Mao Sơn / Vân Mộng Cốc), lưu theo nhân vật
        self._baothutrieuhoimaoson = BAOTHUTRIEUHOI_TUDONG
        # id món đã desc mà không ra mô tả: _napmotadotrieuhoi không hỏi lại
        self._idnapmotathatbais = set()
        self._bodotruoctrieuhoi = None
        self._hangdoideodotrieuhoi = []
        self._thoidiemdoidotrieuhoigannhat = 0.
        self._solanmaclaitrieuhoi = 0
        self._thoidiemnapmotadotrieuhoi = 0.
        self._thoidiemhoandoiphapbao = 0.
        self._tenphapbaocu = None
        self._mucsinhluckhihoandoi = 0
        self._thoidiemthumaclaiphapbao = 0.

        self._is_tudongsudungkynangbaothu = False

        self._trangthaitrieuhoibaothuvatpham = 0
        self._thoidiemchuyentrangthaitrieuhoibaothuvatpham = 0.
        # Bảo thú kỹ năng triệu hồi đang bị gọi về vì ra quá xa nhân vật
        self._idbaothudanggoive = set()
        self._thoidiemyeucaubaothuvatphamdoilenh = 0.

        self._is_danguutiennhatdo = False

        self._thoidiemkiemtranpcsuavatphamgannhat = 0.
        self._thoidiemtruyvandobengannhat = 0.  # > 0: đã desc các món sửa được, đang chờ máy chủ trả mô tả
        self._thoidiemkhongcansuavatphamden = 0.  # vừa kiểm tra thấy đồ còn nguyên độ bền: tự sửa đồ bỏ qua tới lúc này

        self._thoidiemdichuyendaotangbaodogannhat = 0.
        self._thoidiemsudungcaoboctacdangannhat = 0.
        self._thoidiemclickchientruonggannhat = 0.

        self._index_thuduongson = 0
        self._index_thuyhoason = 0
        self._index_hamcocquan = 0

        self._diachidoituongcanbuffhothekimcangdaohoanguyen = None
        # (thời điểm xét, có nhường Trấn Cổ Thần Uy / Hộ Thể Kim Cang cho Đào Hoa Nguyên ưu tiên hơn không)
        self._bonhonhuongbuffdaohoanguyen = (0., False)
        # Lần chọn gửi gần nhất của tâm pháp bật / tắt (Nguyên Khí Quy Nguyên, Dã Tính Cuồng Lực) theo vị trí kỹ năng
        self._thoidiemguitamphapbattat_map = {}

        self._diachidoituongcanhoisinhvanmongcoc = None
        self._diachidoituongcanbufftaytranquyetvanmongcoc = None
        self._diachidoituongcanbufftaytranquyet2vanmongcoc = None
        self._diachidoituongcanbufflinhkhihothevanmongcoc = None
        self._diachidoituongcanbommauvanmongcoc = None
        self._diachidoituongkhietvanquyetvanmongcoc = None
        self._diachidoituongcanbuffkimchamvanmongcoc = None
        self._diachidoituongcanbuffnganchamvanmongcoc = None
        self._diachidoituongcanbuffcuongthethuatvanmongcoc = None
        self._diachidoituongcanbuffphonganthuatvanmongcoc = None
        self._diachidoituongcanbuffhuyenquangthiemanhvanmongcoc = None
        self._thoidiemsudungtusamdongannhat = 0.

    def __del__(self):
        try:
            self.moitruong.action_bochantangcapdo()
        except (pymem.exception.PymemError, pymem.exception.WinAPIError):
            pass

    def luuthietlap(self, idnguoichoi):
        # Lưu theo ID người chơi (cố định, còn tên nhân vật thì có thể đổi)
        if not idnguoichoi or idnguoichoi <= 0:
            return

        thietlap = {
            "_is_tudongtheosau": self._is_tudongtheosau,
            "_idmuctieutheosau": self._idmuctieutheosau,
            "_tenmuctieutheosau": self._tenmuctieutheosau,
            "_is_tudongtimkiemmuctieu": self._is_tudongtimkiemmuctieu,
            "_is_tudongsudungkynang": self._is_tudongsudungkynang,
            "_is_uutienmuctieupk": self._is_uutienmuctieupk,
            "_is_tudongsudungvatpham": self._is_tudongsudungvatpham,
            "_is_tudongnhatvatpham": self._is_tudongnhatvatpham,
            "_is_chidanhnguoichoi": self._is_chidanhnguoichoi,
            "_is_tudongtodoi": self._is_tudongtodoi,
            "_is_thucsondao": self._is_thucsondao,
            "_is_chantangcapdo": self._is_chantangcapdo,
            "_is_tudongdichuyendiemdanhxungquanh": self._is_tudongdichuyendiemdanhxungquanh,
            "_diemdanhxungquanhs": self._diemdanhxungquanhs,
            "_is_lotrinhphobanmuonbando": self._is_lotrinhphobanmuonbando,
            "_is_dilotrinhkhacbando": self._is_dilotrinhkhacbando,
            "_lotrinhmaudangdung": self._lotrinhmaudangdung,
            "_is_nguocchieulotrinh": self._is_nguocchieulotrinh,
            "_is_tudonggomquai": self._is_tudonggomquai,
            "_is_tudongvebanrac": self._is_tudongvebanrac,
            "_is_chedobufftoanbang": self._is_chedobufftoanbang,
            "_is_tudongdichientruong": self._is_tudongdichientruong,
            "_is_tudongkhaikhoang": self._is_tudongkhaikhoang,
            "_is_tudongdaotangbaodo": self._is_tudongdaotangbaodo,
            "_tenmuctieutancongs": self._tenmuctieutancongs,

            "_is_uutienbaothukynangtrieuhoi": self._is_uutienbaothukynangtrieuhoi,
            "_tenmuctieukhongtancongs": self._tenmuctieukhongtancongs,
            "_tenvatphamnhats": self._tenvatphamnhats,
            "_phamchatnhats": self._phamchatnhats,
            "_khoangcachtoidatheosau": self._khoangcachtoidatheosau,
            "_bankinhdiemdanh": self._bankinhdiemdanh,
            "_khoangcachsudungkynangtamxa": self._khoangcachsudungkynangtamxa,
            "_phantramnoiluckhaithientichdia": self._phantramnoiluckhaithientichdia,
            "_is_tudongtrieuhoibaothugiangho": self._is_tudongtrieuhoibaothugiangho,
            "_is_tudongsudungkynangbaothu": self._is_tudongsudungkynangbaothu,
            "_is_tranhvungcam": self._is_tranhvungcam,
            "_is_giukhoangcachketancong": self._is_giukhoangcachketancong,
            "_khoangcachgiuketancong": self._khoangcachgiuketancong,
            "_is_giukhoangcachchimuctieupk": self._is_giukhoangcachchimuctieupk,
            "_is_taphoa": self._is_taphoa,
            "_is_timmuctieuchung": self._is_timmuctieuchung,
            "_is_tutimduongtheosau": self._is_tutimduongtheosau,
            "_is_doidokhitrieuhoi": self._is_doidokhitrieuhoi,
            "_bodotrieuhoi": self._bodotrieuhoi,
            "_baothutrieuhoimaoson": self._baothutrieuhoimaoson,
            "_sumon_npcgiao": self._sumon_npcgiao,
            "_tapkich_phai": self._tapkich_phai,
            # Sư môn đang bật: dis / mở lại bot vào lại thì tự bật tiếp (bấm Dừng, xong 20 lần, lỗi dừng thì là False)
            "_is_dangsumon": bool(self._sumon),
            # Sư Gia đang bật: như sư môn, dis / mở lại bot thì tự bật tiếp (bấm Dừng, đủ số lần trong ngày, lỗi dừng thì là False)
            "_is_dangsugia": bool(self._sugia),
            # Tập Kích đang bật: như sư môn, dis / mở lại bot thì tự bật tiếp với môn phái đã chọn (bấm Dừng, lỗi dừng thì là False)
            "_is_dangtapkich": bool(self._tapkich),
            # Phó bản đang đi ("langlyson" / "thanhkieu", "" = không): dis / mở lại bot thì tự bật tiếp
            "_phobandanglanglyson": self.get_phobanlanglyson(),
        }
        # Sư môn / Sư Gia đang tạm đổi ô nào (Theo sau, Tự động sử dụng kỹ năng...) thì lưu giá trị gốc của người dùng, dis vào lại không mất
        for s in (self._sumon, self._sugia, self._tapkich, self._langlyson):
            thietlap.update({k: v for k, v in ((s or {}).get("tuychoncu") or {}).items() if k in thietlap})
        util_luuthietlap(str(idnguoichoi), thietlap)
        # luuthietlap chạy mỗi giây: vị trí quái thì THOIGIANLUUVITRIQUAI giây mới ghi file một lần (thoát thì luuvitriquai(True))
        self.luuvitriquai()

    def luuvitriquai(self, is_ngay = False):
        if self._idnguoichoiviquai and (is_ngay or time.time() - self._thoidiemluuviquaigannhat > THOIGIANLUUVITRIQUAI):
            self._thoidiemluuviquaigannhat = time.time()
            util_luuviquai(self._idnguoichoiviquai, self._bangviquai)

    def taithietlap(self, idnguoichoi, tennhanvat = None):
        if not idnguoichoi or idnguoichoi <= 0:
            return
        # Đổi nhân vật: ghi vị trí quái của nhân vật cũ rồi nạp của nhân vật mới
        if idnguoichoi != self._idnguoichoiviquai:
            self.luuvitriquai(True)
            self._idnguoichoiviquai = idnguoichoi
            self._bangviquai = util_taiviquai(idnguoichoi)
            self._thoidiemluuviquaigannhat = time.time()

        # Có một giai đoạn thiết lập bị lưu theo tên nhân vật: nếu file theo tên mới hơn file theo ID thì lấy file theo tên
        khoathietlap = str(idnguoichoi)
        if tennhanvat:
            duongdanid = util_duongdanthietlap(str(idnguoichoi))
            duongdanten = util_duongdanthietlap(tennhanvat)
            if os.path.exists(duongdanten) and (not os.path.exists(duongdanid) or os.path.getmtime(duongdanten) > os.path.getmtime(duongdanid)):
                khoathietlap = str(tennhanvat)

        thietlap = util_taithietlap(khoathietlap)
        if thietlap:
            # Thiết lập lưu từ trước khi đổi tên (theo sau trưởng nhóm -> theo sau)
            for khoacu, khoamoi in (("_is_tudongtheosautruongnhom", "_is_tudongtheosau"), ("_khoangcachtoidatruongnhom", "_khoangcachtoidatheosau")):
                if khoacu in thietlap and khoamoi not in thietlap:
                    thietlap[khoamoi] = thietlap[khoacu]
            if "_is_tudongtheosau" in thietlap: self._is_tudongtheosau = thietlap["_is_tudongtheosau"]
            if "_idmuctieutheosau" in thietlap: self._idmuctieutheosau = int(thietlap["_idmuctieutheosau"] or 0)
            if "_tenmuctieutheosau" in thietlap: self._tenmuctieutheosau = thietlap["_tenmuctieutheosau"] or ""
            if "_is_tudongtimkiemmuctieu" in thietlap: self._is_tudongtimkiemmuctieu = thietlap["_is_tudongtimkiemmuctieu"]
            if "_is_tudongsudungkynang" in thietlap: self._is_tudongsudungkynang = thietlap["_is_tudongsudungkynang"]
            if "_is_uutienmuctieupk" in thietlap: self._is_uutienmuctieupk = thietlap["_is_uutienmuctieupk"]
            if "_is_tudongsudungvatpham" in thietlap: self._is_tudongsudungvatpham = thietlap["_is_tudongsudungvatpham"]
            if "_is_tudongnhatvatpham" in thietlap: self._is_tudongnhatvatpham = thietlap["_is_tudongnhatvatpham"]
            if "_is_chidanhnguoichoi" in thietlap: self._is_chidanhnguoichoi = thietlap["_is_chidanhnguoichoi"]
            if "_is_tudongtodoi" in thietlap: self._is_tudongtodoi = thietlap["_is_tudongtodoi"]
            if "_is_thucsondao" in thietlap: self._is_thucsondao = thietlap["_is_thucsondao"]
            if "_is_chantangcapdo" in thietlap: self._is_chantangcapdo = thietlap["_is_chantangcapdo"]
            if "_is_tudongdichuyendiemdanhxungquanh" in thietlap: self._is_tudongdichuyendiemdanhxungquanh = thietlap["_is_tudongdichuyendiemdanhxungquanh"]
            if "_diemdanhxungquanhs" in thietlap: self._diemdanhxungquanhs = thietlap["_diemdanhxungquanhs"]
            if "_is_lotrinhphobanmuonbando" in thietlap: self._is_lotrinhphobanmuonbando = thietlap["_is_lotrinhphobanmuonbando"]
            if "_is_dilotrinhkhacbando" in thietlap: self._is_dilotrinhkhacbando = thietlap["_is_dilotrinhkhacbando"]
            if "_lotrinhmaudangdung" in thietlap: self._lotrinhmaudangdung = thietlap["_lotrinhmaudangdung"]
            if "_is_nguocchieulotrinh" in thietlap: self._is_nguocchieulotrinh = thietlap["_is_nguocchieulotrinh"]
            if "_is_tudonggomquai" in thietlap: self._is_tudonggomquai = thietlap["_is_tudonggomquai"]
            if "_is_tudongvebanrac" in thietlap: self._is_tudongvebanrac = thietlap["_is_tudongvebanrac"]
            if "_is_chedobufftoanbang" in thietlap: self._is_chedobufftoanbang = thietlap["_is_chedobufftoanbang"]
            if "_is_tudongdichientruong" in thietlap: self._is_tudongdichientruong = thietlap["_is_tudongdichientruong"]
            if "_is_tudongkhaikhoang" in thietlap: self._is_tudongkhaikhoang = thietlap["_is_tudongkhaikhoang"]
            if "_is_tudongdaotangbaodo" in thietlap: self._is_tudongdaotangbaodo = thietlap["_is_tudongdaotangbaodo"]
            if "_tenmuctieutancongs" in thietlap: self._tenmuctieutancongs = thietlap["_tenmuctieutancongs"]

            if "_is_uutienbaothukynangtrieuhoi" in thietlap: self._is_uutienbaothukynangtrieuhoi = thietlap["_is_uutienbaothukynangtrieuhoi"]
            if "_tenmuctieukhongtancongs" in thietlap: self._tenmuctieukhongtancongs = thietlap["_tenmuctieukhongtancongs"]
            if "_tenvatphamnhats" in thietlap: self._tenvatphamnhats = thietlap["_tenvatphamnhats"]
            if "_phamchatnhats" in thietlap: self.thietlap_phamchatnhat(thietlap["_phamchatnhats"])
            if "_khoangcachtoidatheosau" in thietlap: self._khoangcachtoidatheosau = float(thietlap["_khoangcachtoidatheosau"])
            if "_bankinhdiemdanh" in thietlap: self._bankinhdiemdanh = float(thietlap["_bankinhdiemdanh"])
            if "_khoangcachsudungkynangtamxa" in thietlap: self.thietlap_khoangcachsudungkynangtamxa(thietlap["_khoangcachsudungkynangtamxa"])
            if "_phantramnoiluckhaithientichdia" in thietlap: self.thietlap_phantramnoiluckhaithientichdia(thietlap["_phantramnoiluckhaithientichdia"])
            if "_is_tudongtrieuhoibaothugiangho" in thietlap: self._is_tudongtrieuhoibaothugiangho = thietlap["_is_tudongtrieuhoibaothugiangho"]
            if "_is_tudongsudungkynangbaothu" in thietlap: self._is_tudongsudungkynangbaothu = thietlap["_is_tudongsudungkynangbaothu"]
            if "_is_tranhvungcam" in thietlap: self._is_tranhvungcam = thietlap["_is_tranhvungcam"]
            if "_is_giukhoangcachketancong" in thietlap: self._is_giukhoangcachketancong = thietlap["_is_giukhoangcachketancong"]
            if "_khoangcachgiuketancong" in thietlap: self.thietlap_khoangcachgiuketancong(thietlap["_khoangcachgiuketancong"])
            if "_is_giukhoangcachchimuctieupk" in thietlap: self._is_giukhoangcachchimuctieupk = thietlap["_is_giukhoangcachchimuctieupk"]
            if "_is_taphoa" in thietlap: self._is_taphoa = thietlap["_is_taphoa"]
            if "_is_timmuctieuchung" in thietlap: self._is_timmuctieuchung = thietlap["_is_timmuctieuchung"]
            if "_is_tutimduongtheosau" in thietlap: self._is_tutimduongtheosau = thietlap["_is_tutimduongtheosau"]
            if "_is_doidokhitrieuhoi" in thietlap: self._is_doidokhitrieuhoi = thietlap["_is_doidokhitrieuhoi"]
            if "_bodotrieuhoi" in thietlap: self._bodotrieuhoi = list(thietlap["_bodotrieuhoi"])
            if thietlap.get("_baothutrieuhoimaoson") in BAOTHUTRIEUHOIMAOSONs: self._baothutrieuhoimaoson = thietlap["_baothutrieuhoimaoson"]
            if "_sumon_npcgiao" in thietlap: self._sumon_npcgiao = thietlap["_sumon_npcgiao"] or ""
            if "_tapkich_phai" in thietlap: self._tapkich_phai = thietlap["_tapkich_phai"] or ""
            if thietlap.get("_is_dangsumon") and not self._sumon:
                self.batdau_sumon()
            if thietlap.get("_is_dangsugia") and not self._sugia:
                self.batdau_sugia()
            if thietlap.get("_is_dangtapkich") and not self._tapkich:
                self.batdau_tapkich()
            if thietlap.get("_phobandanglanglyson") and not self._langlyson:
                self.batdau_langlyson(thietlap["_phobandanglanglyson"])

    def battat_dilotrinhkhacbando(self):
        self._is_dilotrinhkhacbando = not self._is_dilotrinhkhacbando
        phatam("Bật đi lộ trình khác bản đồ" if self._is_dilotrinhkhacbando else "Chỉ đi điểm đánh cùng bản đồ")

    def battat_tranhvungcam(self):
        self._is_tranhvungcam = not self._is_tranhvungcam
        if self._is_tranhvungcam:
            phatam("Bật tránh vùng cấm")
        else:
            phatam("Tắt tránh vùng cấm")

    def battat_giukhoangcachketancong(self):
        self._is_giukhoangcachketancong = not self._is_giukhoangcachketancong
        self._yeucaugiukhoangcach = None
        if self._is_giukhoangcachketancong:
            phatam("Bật giữ khoảng cách với kẻ tấn công")
        else:
            phatam("Tắt giữ khoảng cách với kẻ tấn công")

    def battat_timmuctieuchung(self):
        self._is_timmuctieuchung = not self._is_timmuctieuchung
        self._yeucautimmuctieuchung = None
        if self._is_timmuctieuchung:
            phatam("Bật tìm mục tiêu theo nhân vật khác")
        else:
            phatam("Tắt tìm mục tiêu theo nhân vật khác")

    def battat_taphoa(self):
        self._is_taphoa = not self._is_taphoa
        if self._is_taphoa:
            phatam("Bật tập hỏa theo mục tiêu người theo sau")
        else:
            phatam("Tắt tập hỏa")

    def battat_giukhoangcachchimuctieupk(self):
        self._is_giukhoangcachchimuctieupk = not self._is_giukhoangcachchimuctieupk
        self._yeucaugiukhoangcach = None
        if self._is_giukhoangcachchimuctieupk:
            phatam("Chỉ giữ khoảng cách với mục tiêu PK")
        else:
            phatam("Giữ khoảng cách với cả quái")

    def thietlap_khoangcachgiuketancong(self, khoangcach):
        self._khoangcachgiuketancong = min(15., max(2., float(khoangcach)))

    def battat_sapxephanhtrang(self):
        if self._is_dangsapxephanhtrang:
            self._ketthucsapxephanhtrang("Dừng sắp xếp hành trang")
            return
        self._is_dangsapxephanhtrang = True
        self._thoidiembatdausapxephanhtrang = time.time()
        self._thoidiemsapxephanhtranggannhat = 0.
        self._solandichuyensapxep = 0
        self._lenhsapxepgannhat = None
        self._solanlaplenhsapxep = 0
        self._xoayvongsapxep = None
        phatam("Bắt đầu sắp xếp hành trang")

    def _ketthucsapxephanhtrang(self, thongbao):
        self._is_dangsapxephanhtrang = False
        print("{}: {} (đã chuyển {} lần)".format(self.moitruong.get_tendoituong(), thongbao, self._solandichuyensapxep))
        phatam(thongbao)

    def battat_tutimduongtheosau(self):
        self._is_tutimduongtheosau = not self._is_tutimduongtheosau
        if self._is_tutimduongtheosau:
            phatam("Bật tự tìm đường tới người được theo sau")
        else:
            phatam("Tắt tự tìm đường tới người được theo sau")

    def battat_tudongsudungkynangbaothu(self):
        self._is_tudongsudungkynangbaothu = not self._is_tudongsudungkynangbaothu
        if self._is_tudongsudungkynangbaothu:
            phatam("Bật dùng kỹ năng bảo thú")
        else:
            phatam("Tắt dùng kỹ năng bảo thú")

    def battat_tudongtrieuhoibaothugiangho(self):
        self._is_tudongtrieuhoibaothugiangho = not self._is_tudongtrieuhoibaothugiangho
        if self._is_tudongtrieuhoibaothugiangho:
            phatam("Bật tự động triệu hồi bảo thú")
        else:
            phatam("Tắt tự động triệu hồi bảo thú")

    def thietlap_khoangcachtheosau(self, khoangcach):
        self._khoangcachtoidatheosau = float(khoangcach)

    def thietlap_bankinhdiemdanh(self, bankinh):
        self._bankinhdiemdanh = max(1., float(bankinh))

    def thietlap_phamchatnhat(self, phamchats):
        # Thay hẳn bằng set mới (luồng khác đang duyệt)
        self._phamchatnhats = {int(x) for x in phamchats if int(x) in PHAMCHATVATPHAM_MAP}

    def thietlap_khoangcachsudungkynangtamxa(self, khoangcach):
        # Các chỗ trừ hao (-3) cần tầm đủ lớn
        self._khoangcachsudungkynangtamxa = max(4., float(khoangcach))
        self._khoangcachvoitoimuctieu = min(self._khoangcachvoitoimuctieu, self._khoangcachsudungkynangtamxa - TRUHAOTAMXACHONMUCTIEU)

    def thietlap_phantramnoiluckhaithientichdia(self, phantram):
        self._phantramnoiluckhaithientichdia = min(100., max(0., float(phantram)))

    def action_lammoitrangthai(self):
        danhhieu = DANHHIEU_MAP[self.moitruong.get_idnguoichoi()]
        if danhhieu:
            caulenhthietlapdanhhieu = "title show {}".format(danhhieu)
            self.moitruong.action_thucthicaulenh(caulenhthietlapdanhhieu, douutien = DOUUTIEN_KHANCAP)

    def battat_chedobufftoanbang(self):
        self._is_chedobufftoanbang = not self._is_chedobufftoanbang
        if self._is_chedobufftoanbang:
            phatam("Bật chế độ buff toàn bang")
        else:
            phatam("Tắt chế độ buff toàn bang")

    def battat_is_uutienbaothukynangtrieuhoi(self):
        self._is_uutienbaothukynangtrieuhoi = not self._is_uutienbaothukynangtrieuhoi
        if self._is_uutienbaothukynangtrieuhoi:
            phatam("Bật ưu tiên đánh đệ Mao Sơn")
        else:
            phatam("Tắt ưu tiên đánh đệ Mao Sơn")

    def battat_is_tudongsudungkynang(self):
        self._is_tudongsudungkynang = not self._is_tudongsudungkynang
        if self._is_tudongsudungkynang:
            phatam("Bật tự động sử dụng kỹ năng")
        else:
            phatam("Tắt tự động sử dụng kỹ năng")

    def battat_is_thucsondao(self):
        self._is_thucsondao = not self._is_thucsondao
        if self._is_thucsondao:
            phatam("Bật thục sơn đao")
        else:
            phatam("Tắt thục sơn đao")

    def battat_is_chantangcapdo(self):
        self._is_chantangcapdo = not self._is_chantangcapdo
        if self._is_chantangcapdo:
            phatam("Bật chặn tăng cấp độ")
        else:
            phatam("Tắt chặn tăng cấp độ")

    def battat_is_tudongdichuyendiemdanhxungquanh(self):
        self._is_tudongdichuyendiemdanhxungquanh = not self._is_tudongdichuyendiemdanhxungquanh
        if self._is_tudongdichuyendiemdanhxungquanh:
            phatam("Bật tự động di chuyển điểm đánh xung quanh")
        else:
            phatam("Tắt tự động di chuyển điểm đánh xung quanh")
        self._iddiemdanhxungquanhhientai = False
        self._diemdanhxungquanhhientai = False

    def battat_is_tudongtodoi(self):
        self._is_tudongtodoi = not self._is_tudongtodoi
        if self._is_tudongtodoi:
            phatam("Bật tổ đội tự động")
        else:
            phatam("Tắt tổ đội tự động")

    def batdau_todoimotlan(self):
        # Ctrl+Alt+T / nút "Tổ đội 1 lần": bắt đầu gom thành viên vào nhóm hiện tại của mình. Phím tắt chỉ bắt đầu (đang gom thì bắt đầu
        # lại từ đầu), không bao giờ huỷ: bấm nhầm 2 lần không được mất lượt gom. Huỷ chỉ bằng nút trên giao diện (huy_todoimotlan)
        self._todoimotlan = {"lucbatdau": time.time(), "thanhviens": [], "dangmoi": 0, "lucmoi": 0.}
        self._trangthaitodoimotlan = "Tổ đội 1 lần: bắt đầu gom thành viên"
        print("[TỔ ĐỘI 1 LẦN] Bắt đầu gom thành viên vào nhóm hiện tại")
        phatam("Tổ đội một lần")

    def huy_todoimotlan(self):
        # Nút "Huỷ tổ đội 1 lần" trên giao diện (phím tắt không huỷ): chỉ thôi mời, nhóm hiện tại giữ nguyên, thành viên thôi rời nhóm / chờ mời
        if self._todoimotlan:
            self._ketthuctodoimotlan("Đã huỷ tổ đội 1 lần (nhóm giữ nguyên)")

    def battat_is_tudongtheosau(self):
        self._is_tudongtheosau = not self._is_tudongtheosau
        if self._is_tudongtheosau:
            phatam("Bật tự động theo sau")
        else:
            phatam("Tắt tự động theo sau")

    def battat_is_tudongkhaikhoang(self):
        self._is_tudongkhaikhoang = not self._is_tudongkhaikhoang
        if self._is_tudongkhaikhoang:
            phatam("Bật tự động khai khoáng")
        else:
            phatam("Tắt tự động khai khoáng")

    def battat_tudonggomquai(self):
        self._is_tudonggomquai = not self._is_tudonggomquai
        self._is_danggomquai = False
        self._danhsachidquaidagom.clear()
        if self._is_tudonggomquai:
            phatam("Bật tự động gom quái")
        else:
            phatam("Tắt tự động gom quái")

    def battat_tudongvebanrac(self):
        self._is_tudongvebanrac = not self._is_tudongvebanrac
        self._trangthaiveban = 0

        if self._is_tudongvebanrac:
            phatam("Bật tự động về bán rác")
        else:
            phatam("Tắt tự động về bán rác")

    def battat_tudongdaotangbaodo(self):
        self._is_tudongdaotangbaodo = not self._is_tudongdaotangbaodo
        if self._is_tudongdaotangbaodo:
            phatam("Bật tự động đào tàng bảo đồ")
        else:
            phatam("Tắt tự động đào tàng bảo đồ")

    def battat_is_tudongdichientruong(self):
        self._is_tudongdichientruong = not self._is_tudongdichientruong
        if self._is_tudongdichientruong:
            phatam("Bật tự động đi chiến trường")
        else:
            phatam("Tắt tự động đi chiến trường")

    def them_tenmuctieutancong(self, tenmuctieutancong):
        if tenmuctieutancong:
            if "( Cấp" in tenmuctieutancong:
                tenmuctieutancong = tenmuctieutancong.split("( Cấp")[0].strip()
            elif "(Cấp" in tenmuctieutancong:
                tenmuctieutancong = tenmuctieutancong.split("(Cấp")[0].strip()

            if tenmuctieutancong not in self._tenmuctieutancongs:
                self._tenmuctieutancongs.add(tenmuctieutancong)
                if self._tenmuctieutancongs:
                    print("Danh sách mục tiêu tấn công: {}".format(self._tenmuctieutancongs))
                    phatam("Thêm tên mục tiêu tấn công. Tổng cộng {}".format(len(self._tenmuctieutancongs)))

    def them_tenmuctieukhongtancong(self, tenmuctieukhongtancong):
        if tenmuctieukhongtancong:
            if "( Cấp" in tenmuctieukhongtancong:
                tenmuctieukhongtancong = tenmuctieukhongtancong.split("( Cấp")[0].strip()
            elif "(Cấp" in tenmuctieukhongtancong:
                tenmuctieukhongtancong = tenmuctieukhongtancong.split("(Cấp")[0].strip()

            if tenmuctieukhongtancong not in self._tenmuctieukhongtancongs:
                self._tenmuctieukhongtancongs.add(tenmuctieukhongtancong)
                if self._tenmuctieukhongtancongs:
                    print("Danh sách mục tiêu không tấn công: {}".format(self._tenmuctieukhongtancongs))
                    phatam("Thêm tên mục tiêu không tấn công. Tổng cộng {}".format(len(self._tenmuctieukhongtancongs)))

    def thietlap_danhsachmuctieu(self, tenmuctieutancongs, tenmuctieukhongtancongs):
        # Giao diện sửa cả danh sách: thay hẳn bằng set mới (không sửa tại chỗ vì luồng khác đang duyệt)
        self._tenmuctieutancongs = {ten.strip() for ten in tenmuctieutancongs if ten and ten.strip()}
        self._tenmuctieukhongtancongs = {ten.strip() for ten in tenmuctieukhongtancongs if ten and ten.strip()}
        print("Danh sách mục tiêu tấn công: {}".format(self._tenmuctieutancongs))
        print("Danh sách mục tiêu không tấn công: {}".format(self._tenmuctieukhongtancongs))

    def them_tenvatphamnhat(self, tenvatphamnhat):
        if tenvatphamnhat and tenvatphamnhat not in self._tenvatphamnhats:
            self._tenvatphamnhats.add(tenvatphamnhat)

            if self._tenvatphamnhats:
                print("Danh sách tên vật phẩm nhặt: {}".format(self._tenvatphamnhats))
                phatam("Thêm tên tên vật phẩm nhặt. Tổng cộng {}".format(len(self._tenvatphamnhats)))

    def botoanbo_tenmuctieutancong(self):
        self._tenmuctieutancongs.clear()
        self._tenvatphamnhats.clear()

        phatam("Bỏ thiết lập tên tên vật phẩm nhặt và vật phẩm nhặt".format(len(self._tenmuctieutancongs)))

    def botoanbo_tenmuctieukhongtancong(self):
        self._tenmuctieukhongtancongs = set(TENMUCTIEUKHONGTANCONGs)
        phatam("Bỏ thiết lập tên mục tiêu không tấn công".format(len(self._tenmuctieukhongtancongs)))

    def thietlap_chidanhnguoichoi(self, is_chidanhnguoichoi):
        self._is_chidanhnguoichoi = is_chidanhnguoichoi
        if not is_chidanhnguoichoi:
            phatam("Bỏ thiết lập chỉ đánh người chơi")
        else:
            phatam("Thiết lập chỉ đánh người chơi")
