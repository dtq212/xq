from collections import defaultdict
from math import sqrt

from bando_xq import laytenbandogame, layidbandotheoten, get_solanchuyenbando, BANDOCONG_MAP, SOLANCHUYENBANDOTOIDA

CHUACHONHANVAT = "Chưa chọn nhân vật"
STRING_ENCODING = "mbcs"

CHUTIEMSUACHUA = "Chủ Tiệm Sửa Chữa"
CHUTIEMTAPHOA = "Chủ Tiệm Tạp Hóa"
# NPC kho ở Tân Thủ Thôn (lệnh pawn, tactu_catkho_xq)
QUANKHO = "Quản Khố"
# NPC ở bản đồ bang phái để nạp Rương Dự Trữ (tìm theo tên, id đối tượng có thể đổi)
TRUONGPHONGTIENSINH = "Trưởng Phòng Tiên Sinh"
RUONGDUTRU = "Rương Dự Trữ"
CHUTUULAU = "Chủ Tửu Lâu"
TANTHUTIENCO = "Tân Thủ Tiên Cô"
SUGIAMONPHAI = "Sứ Giả Môn Phái"
XAPHU = "Xa Phu"
TRUONGQUALAO = "Trương Quả Lão"
QUANSUVOSONGTHANH = "Quân Sư Vô Song Thành"
HYDUONG = "Hỷ Đường"

TAITAOHOAN = "Tái Tạo Hoàn"
TIENTE = "Tiền Tệ"
CAOCAPBAOTHUTHUCPHAM = "Cao Cấp Bảo Thú Thực Ph"
ANXAPHU = "Ân Xá Phù"
TUKIMBAOHOP = "Tử Kim Bảo Hộp"
NHANSAM = "Nhân Sâm"
TIEUPHAPLUCTHACH = "Tiểu Pháp Lực Thạch"
TIEUHUYETTHACH = "Tiểu Huyết Thạch"
HONGCAU = "Hồng Cầu"
HOACAU = "Hoa Cầu"
LAMCAU = "Lam Cầu"
HACCAU = "Hắc Cầu"
SOTRIDUOC = "Sơ Trị Dược"
TRIDUOC = "Trị Dược"
PHUCDUOC = "Phục Dược"
GATAYNOEL = "Gà Tây Noel"
LIXI = "Phong Bao Lì Xì"
LEBAOKHAIQUOC = "Lễ Bao Khai Quốc"
HACLANTHACH = "Hắc Lân Thạch"

SONGTUDUNGCAM = "Song Tử Dũng Cảm"
SONGTUANHMINH = "Song Tử Anh Minh"
THANTHUMAYET = "Thần Thú - Ma Yết"
THANTHUDAN = "Thần Thú - Dần (Giới hạn)"
THANTHUDAN2 = "Thần Thú - Dần (Giới h"
THANTHUSUU = "Thần Thú - Sửu (Giới hạn)"
THANTHUSUU2 = "Thần Thú - Sửu (Giới h"
THANTHUCHUOT = "Thần Thú - Chuột"
THANTHUTHO = "Thần Thú - Thỏ"
THANTHUTHIN = "Thần Thú - Thìn"
THANTHUTINHLINHNOEL = "Thần Thú - Tinh Linh Noel"
THANTHUYEULINHNOEL = "Thần Thú - Yêu Linh Noel"

TIEUDAOTAN = "Tiêu Dao Tán"
QUYNGUYENDON = "Quy Nguyên Đơn"
TUTAMDON = "Tử Tâm Đơn"
CHUTHIENDON = "Chu Thiên Đơn"
KIMTANGTAN = "Kim Tang Tán"
KHIMACHDON = "Khí Mạch Đơn"
XALOITU = "Xá Lợi Tử"
NGANHANHTU = "Ngân Hạnh Tử"
TUTINHDON = "Tử Tinh Đơn"
PHUCSINHDON = "Phục Sinh Đơn"
THANHTAMDAN = "Thanh Tâm Đan"
THANHTAMDON = "Thanh Tâm Đơn"
KHUMATAN = "Khu Ma Tán"
THILUYENQUA = "Thí Luyện Quả"
THILUYENDON = "Thí Luyện Đơn"
LONGTIENTHAO = "Long Tiên Thảo"

TUILINHTHACHCAP1 = "Túi Linh Thạch cấp 1"
TUILINHTHACHCAP2 = "Túi Linh Thạch cấp 2"
HOATLACHOAN = "Hoạt Lạc Hoàn"
ANTHANHOAN = "An Thần Hoàn"
THIENNGUYENDAN = "Thiên Nguyên Đan"
THIENNGUYENDON = "Thiên Nguyên Đơn"

PHIHANHPHU = "Phi Hành Phù"
KIMCUONGBATHOAIDON = "Kim Cương Bất Hoại Đơn"
BATTIENDON = "Bát Tiên Đơn"
HOITHANHPHU = "Hồi Thành Phù"
# Giá (ngân lượng): Hồi Thành Phù qua Tín Vật (menu Tín Vật trong game), phù Tân Thủ Tiên Cô (từ cấp 50)
GIAHOITHANHPHU = 1500
GIAPHUTANTHUTIENCO = 500
# Mua đồ luôn chừa lại bấy nhiêu ngân lượng (đủ Hồi Thành Phù về rồi phù đi)
NGANLUONGGIULAI = GIAHOITHANHPHU + GIAPHUTANTHUTIENCO
# Tối đa bấy nhiêu lần Hồi Thành Phù trong THOIGIANDEMHOITHANHPHU giây: quá thì coi như đang lặp, ngưng dùng (mỗi lần 1.500 lượng)
SOLANHOITHANHPHUTOIDA = 3
THOIGIANDEMHOITHANHPHU = 600.

# Sắp xếp hành trang: thuốc dồn về cuối túi cuối cùng, trước nó là đồ có "[Có thể sử dụng]" trong mô tả. So theo đầu tên nên
# bản "... Luyện Chế" (và tên bị cắt ngắn) cũng tính
THUOCSAPXEPs = (NGANHANHTU, TUTAMDON, KHIMACHDON, TIEUDAOTAN, LONGTIENTHAO, THILUYENQUA, THILUYENDON, KIMTANGTAN,
                QUYNGUYENDON, KHUMATAN, THANHTAMDON)
# Đá không được "move" đè lên ô có món khác: game tưởng là muốn đập / tinh luyện đá vào đồ đó. Đá = loại ［Tinh luyện］ (Kim / Thổ /
# Ám Tinh Thạch...), tên có chữ trong DAKHONGDEDOs, hoặc tên có "Thạch" mà mô tả không ghi loại (cho chắc). Món có loại khác như
# Đại Huyết Thạch ［Có thể sử dụng］, Hồng Bảo Thạch Hạng Liên ［Hạng Liên］ thì không phải đá. Đổi chỗ thì chuyển món kia sang ô của đá
DAKHONGDEDOs = ("Đoạn Thạch", "Linh Thạch", "Tinh Thạch")
# Loại vật phẩm = chữ trong cặp ［］ đầu tiên của mô tả (sau dòng tên), vd ［Vũ Khí］［Nón］［Tinh luyện］［Có thể sử dụng］[Pháp Bảo]
LOAIVATPHAM_COTHESUDUNG = "Có thể sử dụng"
LOAIVATPHAMDAs = ("Tinh luyện",)

SOCAPDOANTHACH = "Sơ Cấp Đoạn Thạch"
TRUNGCAPDOANTHACH = "Trung Cấp Đoạn Thạch"
CAOCAPDOANTHACH = "Cao Cấp Đoạn Thạch"

CAOBOCTACDAN = "Cao Bộc Tạc Đạn"
NHIEPHONLINH = "Nhiếp Hồn Linh"
HUYNHQUANGTHACH = "Huỳnh Quang Thạch"
CAPCUUDON = "Cấp Cứu Đơn"
HOATTAMDON = "Hoạt Tâm Đơn"
THIENLYHUUTINH = "Thiên Lý Hữu Tình"
DAIHUYETTHACH = "Đại Huyết Thạch"
DAIPHAPLUCTHACH = "Đại Pháp Lực Thạch"
THOHANHCHAU = "Thổ Hành Châu"
TRANKY = "Trận Kì"
DAUNANH = "Đậu Nành"
TUSAMDON = "Tử Sâm Đơn"
TAYGAU = "Tay Gấu"
TUIQUAVOSONG = "Túi Quà Vô Song"
HOANGKIMTHANHY = "Hoàng Kim Thánh Y"

TOAILANG = "Toái Lăng"
TOAISA = "Toái Sa"
TOAICAM = "Toái Cẩm"
NHIEPHONTHACH = "Nhiếp Hồn Thạch"
DASOI = "Da Sói"
LYHON = "Ly Hồn"
LYPHACH = "Ly Phách"
DONGVATBIMAO = "Động Vật Bi Mao"
TANGBAODO = "Tàng Bảo Đồ"
BUAGIAY = "Bùa Giấy"
DAUBINH = "Đậu Binh"
CUONGTHI = "Cương Thi"
QUYTOT = "Quỷ Tốt"
THIENBINH = "Thiên Binh"
THIENTUONG = "Thiên Tướng"
THANTUONG = "Thần Tướng"  # Chỉ gọi ra được bằng Tế Thần Tướng
# Triệu hồi bảo thú kỹ năng nào (chọn trên bảng điều khiển, lưu theo nhân vật): tự động = Mao Sơn gọi Cương Thi nếu có Cương Thi Phù,
# không thì Thiên Binh; Vân Mộng Cốc gọi Đậu Binh. Hoặc chỉ gọi đúng 1 loại CUONGTHI / THIENBINH / QUYTOT (Mao Sơn) / DAUBINH (Vân Mộng Cốc);
# BAOTHUTRIEUHOI_KHONG thì không triệu hồi con nào
BAOTHUTRIEUHOI_TUDONG = "Tự động"
BAOTHUTRIEUHOI_KHONG = "Không triệu hồi"
BAOTHUTRIEUHOIMAOSONs = (BAOTHUTRIEUHOI_TUDONG, CUONGTHI, THIENBINH, QUYTOT, DAUBINH, BAOTHUTRIEUHOI_KHONG)
TROMBAOPHITAC = "Trộm Bảo Phi Tặc"

KHUYENTHAILANG = "Khuyển Thái Lang"

BAOTHUKYNANGTRIEUHOIs = (CUONGTHI, QUYTOT, DAUBINH, THIENBINH, THIENTUONG, THANTUONG, KHUYENTHAILANG)

KHOANGCACHNUAMANHINH = 9.
KHOANGCACHTOANMANHINH = 18.

KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN = 3
# Kỹ năng vận khí: từ lúc gửi lệnh tới lúc game vào trạng thái vận khí thường 0.5-1.5s, có lúc tới ~1.6-2s
# (log: chờ 1.5s hết là Huyết Ma Chú chen vào ngắt vận khí triệu hồi) nên chờ dư
THOIGIANCHOVAOVANKHI = 2.5
# Khoá vận khí triệu hồi bảo thú giữ tối đa chừng này (phòng đọc trạng thái vận khí sai mà khoá mãi)
THOIGIANKHOAVANKHITRIEUHOITOIDA = 15.
# Lôi Động Cửu Thiên (Mao Sơn) vận khí 6s (phạm vi 7x7 ô quanh bản thân); Lôi Long Quyết (Côn Luân, 9x9 ô liên tục 6s) cùng cơ chế,
# dùng chung các hằng / cách ngắt vận khí này
THOIGIANVANKHILOIDONGCUUTHIEN = 6.
# Phong Vũ Kinh Thiên (Vân Mộng Cốc) gọi cuồng phong đánh mục tiêu liên tục 8s: trong khoảng này không dùng lại lên cùng mục tiêu
THOIGIANPHONGVUKINHTHIEN = 8.
# Mao Sơn: có cụm quái quanh mục tiêu mà mục tiêu xa hơn chừng này thì chạy vào (dừng cách ~1 ô) để ra Lôi Động Cửu Thiên trúng cả cụm
KHOANGCACHTIEPCANLOIDONGCUUTHIEN = 2.

KHOANGCACHTOIDAHOPLE = 255.
KHOANGCACHSUDUNGKYNANGCANCHIEN = 1.5
KHOANGCACHSUDUNGKYNANGTAMXA = 9.  # 12.
# Tầm xa 9 ô đã là con số trừ hao lệch tọa độ client - server (tầm thật ~12 ô), nên không trừ thêm nhiều nữa:
# - lọc mục tiêu quanh người theo sau dùng tầm xa - TRUHAOTAMXACHONMUCTIEU (dùng trọn 9 ô)
# - đứng đánh lâu / đang chạy bù thì tầm yêu cầu giảm BUKHOANGCACHTAMXA ô (đánh ở ~8 ô), chạy vào tầm thì dừng ở tầm xa - BU - 1 (~7 ô)
TRUHAOTAMXACHONMUCTIEU = 0.
BUKHOANGCACHTAMXA = 1.
# Tiếp cận cận chiến như client khi bấm chiêu trên phím tắt (xq + 0x1873A, đọc 2026-10-28): tìm đường tới ô mục tiêu, mỗi lần chỉ
# ghi chừng này bước (client: KDK + 0x1620 = 2), đích đổi thì chừng này giây sau lần ghi trước mới tìm lại (client: mốc +500ms)
SOBUOCTIEPCANCANCHIEN = 2
# Bot tìm đường lại và ghi đoạn mới mỗi chừng này giây kể cả khi đích không đổi (client 0.5s; ngắn hơn để chuỗi không cạn giữa đường)
THOIGIANTINHLAITIEPCANCANCHIEN = 0.25
# Mục tiêu đang đi về phía mình, bước tới của nó cách mình không quá chừng này ô (theo ô, max |dx| |dy|) thì đứng chờ
KHOANGCACHCHOMUCTIEUTOI = 2
# Mục tiêu chạy ra xa mà còn cách từ chừng này ô thì đón đầu nhẹ, tối đa QUANGDONDAUCANCHIEN ô; gần hơn thì nhắm ô của nó như client
KHOANGCACHDONDAUCANCHIEN = 3
QUANGDONDAUCANCHIEN = 2.
# Thục Sơn chỉ dùng Khai Thiên Tịch Địa để lướt khi nội lực trên mức này (%), chỉnh được ở giao diện
PHANTRAMNOILUCKHAITHIENTICHDIA = 75.
KHOANGCACHHIEUQUAKYNANGNGUKIEMPHITIEN = 9.
# Di chuyển tự do: mục tiêu xa hơn chừng này thì Thục Sơn chạy vào (dừng cách mục tiêu ~1 ô ít hơn, tức ~3 ô)
# rồi mới ra Ngự Kiếm Phi Tiên, để trúng cả cụm quái quanh mục tiêu (chiêu đánh quanh bản thân 9 ô)
KHOANGCACHTIEPCANNGUKIEMPHITIEN = 4.
KHOANGCACHHIEUQUAKYNANGKHAITHIENTICHDIA = 6.0
KHOANGCACHNHATDO = KHOANGCACHTOANMANHINH

# Mục tiêu mới nhìn thấy phải chờ ngần này giây mới được chọn tấn công; mất dấu quá THOIGIANMATDAUMUCTIEU thì thấy lại tính là mới
THOIGIANCHOCHONMUCTIEUMOI = 1.
THOIGIANMATDAUMUCTIEU = 3.

# Thấy người chơi ẩn thân quanh mình khi đang di chuyển theo lộ trình điểm đánh thì ngưng mọi hoạt động trong khoảng thời gian này (giây)
THOIGIANTAMNGUNGANTHAN = 600.
# Thấy người lạ (ngoài danh sách tổ đội) ở map train thì ngưng ngắn hơn (giây)
THOIGIANTAMNGUNGNGUOILA = 60.
# Tín hiệu "vừa thấy ẩn thân" của nhân vật khác cùng bản đồ còn hiệu lực trong bấy nhiêu giây (nhân vật thấy sẽ làm mới liên tục mỗi 0.5s)
THOIGIANCHIASEANTHAN = 3.

SOLUONGTHANHVIENNHOMTOIDA = 5
SOLUONGTHANHVIENNHOMTOIDATHUCTE = 5
SOLUONGHIEUUNGNHANVATTOIDA = 20

TUTHENHANVAT_DUNGIM = 1
TUTHENHANVAT_DICHUYEN = 2
TUTHENHANVAT_NAMDUOIDAT = 3  # cả đồ lẫn vật phẩm
TUTHENHANVAT_NGOI = 4
TUTHENHANVAT_TANCONGVATLY = 6
TUTHENHANVAT_TANCONGPHEPTHUAT = 9
TUTHENHANVAT_DELAYSAUTANCONG = 11

LOAIMUCTIEU_QUAIVATHOACNPC = 0
LOAIMUCTIEU_NGUOICHOIKHACNHOM = 1
LOAIMUCTIEU_NGUOICHOICUNGNHOM = 2

LOAIDOITUONG_NHANVAT1 = 1
LOAIDOITUONG_NHANVATKHAC1 = 2
LOAIDOITUONG_VATPHAMDUOIDAT = 3

KETQUA_HANHDONG_THATBAI = 0
KETQUA_HANHDONG_THANHCONG = 1
KETQUA_HANHDONG_DICHUYEN = 2

VITRIPHIMTATKYNANG_1 = 19
VITRIPHIMTATKYNANG_2 = 18
VITRIPHIMTATKYNANG_3 = 17
VITRIPHIMTATKYNANG_4 = 16
VITRIPHIMTATKYNANG_5 = 15
VITRIPHIMTATKYNANG_6 = 14
VITRIPHIMTATKYNANG_7 = 13
VITRIPHIMTATKYNANG_8 = 12
VITRIPHIMTATKYNANG_9 = 11
VITRIPHIMTATKYNANG_0 = 10

VITRIPHIMTATKYNANG_THUCANTHUCUOI = VITRIPHIMTATKYNANG_9

VITRIPHIMTATKYNANG_Q = 0
VITRIPHIMTATKYNANG_W = 1
VITRIPHIMTATKYNANG_E = 2
VITRIPHIMTATKYNANG_R = 3
VITRIPHIMTATKYNANG_A = 4
VITRIPHIMTATKYNANG_S = 5
VITRIPHIMTATKYNANG_D = 6
VITRIPHIMTATKYNANG_F = 7
VITRIPHIMTATKYNANG_Z = 8
VITRIPHIMTATKYNANG_X = 9

VITRIPHIMTATKYNANG_THUCANBAOTHU = VITRIPHIMTATKYNANG_X

# Bộ đệm vòng hook trò chuyện (MoiTruong.action_thietlaphooknoidungtrochuyen): số ô (lũy thừa của 2, asm lấy dư bằng and) và số
# byte mỗi ô (dòng dài hơn bị cắt)
SOLUONGDONGTROCHUYEN = 64
KICHTHUOCDONGTROCHUYEN = 128

VITRIKYNANG_DONDAOTRUCNHAP = 2210
VITRIKYNANG_NGHENHPHONGTRAM = 2211
VITRIKYNANG_PHAKHONGKICH = 2212
VITRIKYNANG_PHAMATRAM = 2213
VITRIKYNANG_LUUTINHTRUYMANG = 2214
VITRIKYNANG_LUCPHACHHOASON = 2215
VITRIKYNANG_KHAITHIENTICHDIA = 2216

VITRIKYNANG_LANHNGUYETTAMPHAP = 2221
VITRIKYNANG_BANGPHACHNGANTAM = 2222

VITRIKYNANG_NGUKIEMTHUAT = 2310
VITRIKYNANG_TIENNHANCHILO = 2311
VITRIKYNANG_VANKIEMXUYENTAM = 2312
VITRIKYNANG_VANVUTIEUDIEU = 2315
VITRIKYNANG_BANGTAMTHUC = 2313
VITRIKYNANG_LANGKHONGCHIHUYET = 2314
VITRIKYNANG_NGUKIEMPHITIEN = 2316

VITRIKYNANG_TIENKHI = 3252
VITRIKYNANG_TINHTAMQUYET = 3253
VITRIKYNANG_TIENTHANVODICH = 3254

VITRIKYNANG_LIETPHONGQUYET = 2811
VITRIKYNANG_TOANPHONGQUYET = 2812
VITRIKYNANG_PHONGVUKINHTHIEN = 2813

VITRIKYNANG_NGANCHAMDOACH = 5011
VITRIKYNANG_KIMCHAMDOACH = 5012
VITRIKYNANG_TAYTRANQUYET = 5013
VITRIKYNANG_CUONGTHETHUAT = 5014
VITRIKYNANG_DAUCHUYENTINHDI = 5016

VITRIKYNANG_SOTRI = 5112
VITRIKYNANG_VODINHLUUTHUY = 5115
VITRIKYNANG_CAITUHOANSINH = 5114
VITRIKYNANG_KHIETVANQUYET = 5113
VITRIKYNANG_CAMLOTRI = 5116

VITRIKYNANG_RAIDAUTHANHBINH = 5312
VITRIKYNANG_THOIMIENTHUAT = 5313
VITRIKYNANG_HUYENQUANGTHIEMANH = 5314
VITRIKYNANG_PHONGANTHUAT = 5315

VITRIKYNANG_LINHKHIHOTHE = 5911
VITRIKYNANG_KYMONTRAN = 5912
VITRIKYNANG_DONGIAPTRAN = 5913

VITRIKYNANG_TIEUCHUTHIEN = 3291

VITRIKYNANG_MAIHOACHAM = 2612
VITRIKYNANG_THAUCOTDINH = 2614
VITRIKYNANG_HAPTINHMACHAM = 2616
VITRIKYNANG_NHIEPHONCHAM = 2617
VITRIKYNANG_SONGLONGDOATCHAU = 2613
VITRIKYNANG_MANTHIENHOAVU = 2618

VITRIKYNANG_LACTUYETVONGAN = 3641
VITRIKYNANG_MATAMTHUAT = 3642
VITRIKYNANG_BOPHONGHANH = 3643

VITRIKYNANG_ANTHANTHUAT = 3683
VITRIKYNANG_THICHSAT = 3684
VITRIKYNANG_AMKICH = 3685
VITRIKYNANG_BISAT = 3686

VITRIKYNANG_TRANCOTHANUY = 3162
VITRIKYNANG_KIMTRUNGCHAO = 3161
VITRIKYNANG_DATINCUONGLUC = 3191
VITRIKYNANG_KIMCUONGTHANPHAP = 3192

# Côn Luân (đọc bảng kỹ năng + "desc pf" trên ThiênĐạo 2026-10-29), cách dùng ở action_sudungkynangmonphaiconluan:
#   Lôi Long Quyết 9x9 quanh bản thân liên tục 6s, vận khí (6 bùa, 250 pháp lực, hồi 4s) - như Lôi Động Cửu Thiên của Mao Sơn;
#   Hàn Băng Trận 7x7 quanh bản thân, Đóng Băng 6s (5 bùa); Kim Quang Trận 5x5 quanh mục tiêu (3 bùa); Huyền Long Chân Khí (4 bùa);
#   Hỏa Long Quyết Thiêu Đốt 12s (3 bùa); Thương Long Quyết Đóng Băng 6s (3 bùa); Hàn Băng Thuật Chậm Chạp 6s (1 bùa); Ngự Lôi Thuật
#   choáng 1s (1 bùa); Phong Hỏa Quyết (không bùa); Phong Ma Chú Trầm Mặc 6s; Càn Khôn Na Di tâm pháp hộ thể 5 phút (bấm lại là tắt,
#   hiệu ứng trùng id kỹ năng); Đằng Vân Giá Vũ dịch chuyển (chiêu lướt như Khai Thiên Tịch Địa). Chưa dùng: Biến Thân Thuật, Khốn Ma
#   Thuật / Trận (không tác dụng lên người chơi), Phá Chú (giải bùa cho đồng đội), Long Du Tứ Hải (tới người chơi theo ID)
VITRIKYNANG_BIENTHANTHUAT = 4211

VITRIKYNANG_PHACHU = 4221
VITRIKYNANG_PHONGMACHU = 4222

VITRIKYNANG_PHONGHOAQUYET = 4231
VITRIKYNANG_NGULOITHUAT = 4232
VITRIKYNANG_HOALONGQUYET = 4233
VITRIKYNANG_HANBANGTHUAT = 4234
VITRIKYNANG_THUONGLONGQUYET = 4235
VITRIKYNANG_HANBANGTRAN = 4236
VITRIKYNANG_HUYENLONGCHANKHI = 4237

VITRIKYNANG_KHONMATHUAT = 4241
VITRIKYNANG_KIMQUANGTRAN = 4242
VITRIKYNANG_KHONMATRAN = 4243
VITRIKYNANG_LOILONGQUYET = 4244

VITRIKYNANG_CANKHONNADI = 4252
VITRIKYNANG_DANGVANGIAVU = 4253
VITRIKYNANG_LONGDUTUHAI = 4254
HIEUUNGKYNANG_CANKHONNADI = 4252

VITRIKYNANG_PHUCMAQUYET = 2711
VITRIKYNANG_LOIDONGCUUTHIEN = 2712

VITRIKYNANG_TRIEUHOIQUYTOT = 4131
VITRIKYNANG_TRIEUHOITHIENBINH = 4132
VITRIKYNANG_TRIEUHOICUONGTHI = 4134

VITRIKYNANG_HUYETTE = 4174
VITRIKYNANG_MENHTE = 4175
VITRIKYNANG_TETHANTUONG = 4176

VITRIKYNANG_HUYETMACHU = 4147
VITRIKYNANG_THUCGIAP = 4143
VITRIKYNANG_THUCCOT = 4144
VITRIKYNANG_THUCTAM = 4145
VITRIKYNANG_THUCHON = 4148
VITRIKYNANG_AMMANHAPTHE = 4141

VITRIKYNANG_XUYENKHONGHANH = 4182

VITRIKYNANG_LUUHUYETTHUAT = 4172
VITRIKYNANG_DITINHDAIPHAP = 4173

# Nhân vật mới chưa học đủ kỹ năng: chỉ được dùng các kỹ năng liệt kê ở đây.
# Khoá là ID người chơi (ưu tiên, cố định) hoặc tên nhân vật viết thường (khoảng trắng Alt+255 coi như dấu cách).
KYNANGCHOPHEPTHEONHANVAT_MAP = {

}
VITRIKYNANG_THANTUEPHAPCHU = 4171

VITRIKYNANG_GIAOLONGNHAPHAI = 2411
VITRIKYNANG_TRUCDAOHOANGLONG = 2414
VITRIKYNANG_THIENLYTATSAT = 2413
VITRIKYNANG_PHILONGTAMCHAU = 2415
VITRIKYNANG_LOIDINHKICH = 2416

VITRIKYNANG_MANHHOBOPHAP = 2421
VITRIKYNANG_KIMSUBOGIAP = 2422

VITRIKYNANG_HOANHTAOTHIENQUAN = 2514
VITRIKYNANG_THIENBONGNHATKICH = 2513
VITRIKYNANG_NGULOIAPDINH = 2516
VITRIKYNANG_MEHONTHUC = 2517
VITRIKYNANG_DAIHAICUONGDAO = 2512
VITRIKYNANG_BADAONOLANG = 2515

VITRIKYNANG_THIENTRI = 3481
VITRIKYNANG_CHANTHIENNOHONG = 3483
VITRIKYNANG_SINHTUTHANLUC = 3484
VITRIKYNANG_LUANHOIVANCHUYEN = 3485


VITRIKYNANG_HACHODAOTAM = 2110
VITRIKYNANG_KHITRANGSONHA = 2111
VITRIKYNANG_BADONGQUYEN = 2117
VITRIKYNANG_THONKINH = 2112
VITRIKYNANG_DAOHOALACANH = 2115
VITRIKYNANG_PHONGMAQUYET = 2113
VITRIKYNANG_METUNGQUYEN = 2116
VITRIKYNANG_KHONGTHUNHAPBACHNHAN = 2114
VITRIKYNANG_DAIHAIVOLUONG = 2118
VITRIKYNANG_NHATQUYENBATSON = 2119

VITRIKYNANG_LACKICH = 2123
VITRIKYNANG_PHANTOA = 2124

VIRIKYNANG_NGUYENKHIQUYNGUYEN = 3172
# Nguyên Khí Quy Nguyên quá ~30 phút thì server cho hết hạn nhưng client vẫn hiện hiệu ứng: bật được chừng này giây thì bấm làm mới
# (thu hồi rồi bật lại). Người dùng chọn 10 phút cho an toàn
TENKYNANG_NGUYENKHIQUYNGUYEN = "Nguyên Khí Quy Nguyên"
THOIGIANLAMMOINGUYENKHIQUYNGUYEN = 10 * 60.
# Sau mỗi lần gửi Nguyên Khí Quy Nguyên, chừng này giây mới được làm mới lần nữa (chờ tin; lỡ không bắt được tin thì không bấm qua lại)
THOIGIANCHOTINLAMMOINGUYENKHIQUYNGUYEN = 30.
VIRIKYNANG_HOTHEKIMCANG = 3173
VITRIKYNANG_DATINHCUONGLUC = 3191

# "kill" (bật tự động đánh thường lên mục tiêu, không phải kỹ năng) đã bật với mục tiêu này thì chừng này giây mới gửi lại cho chắc
THOIGIANGUILAITANCONGVATLY = 5.
# Đào Hoa Nguyên chỉ "kill" (bật đánh thường) khi nguyên khí không quá chừng này: còn nguyên khí thì spam chiêu, đánh thường làm chiêu ra chậm.
# 3 = chưa đủ 4 cho Nhất Quyền (để 2 thì nguyên khí 3 + mục tiêu đã có Trọng Thương / Lạc Kích không chiêu nào được dùng, đứng im ~1s)
NGUYENKHITANCONGVATLYDAOHOA = 3
# Nguyên khí hồi tới chừng này thì ngắt đánh thường (cách xa ngưỡng bật để không đánh vài chiêu lại phải "kill" lại)
NGUYENKHINGATTANCONGVATLYDAOHOA = 8
# Thốn Kình lấp chỗ (mục tiêu đã có Trọng Thương) chỉ dùng khi nguyên khí dư hẳn (cùng mức ngắt đánh thường), không ăn phần tích cho Nhất Quyền
NGUYENKHITOITHIEUTHONKINHLAPCHO = 8
# Ba Động cận chiến / Lạc Kích lặp lại (mục tiêu đã có Lạc Kích): dùng khi sau nó còn đủ cho Nhất Quyền (2 + 4 trên mô tả), hoặc khi
# Nhất Quyền còn hồi ít nhất THOIGIANHOICHIEUCONLAICHIEULOT giây (bước chờ delay 0 -> Nhất Quyền 0.8-1.7s bị hồi chiêu che mất) và
# nguyên khí còn NGUYENKHITOITHIEUCHIEULOTKHIHOICHIEU. Thời gian còn lại tính từ lúc Nhất Quyền vào hồi chiêu + tái sử dụng trên mô tả
NGUYENKHITOITHIEUCHIEULOT = 6
THOIGIANHOICHIEUCONLAICHIEULOT = 1.
NGUYENKHITOITHIEUCHIEULOTKHIHOICHIEU = 4
THOIGIANHOICHIEUNHATQUYEN = 2.
# Nhất Quyền đã hồi chiêu mà nguyên khí không quá chừng này thì không dùng Đại Hải (tốn 4) để lót, đánh thường để dành cho Nhất Quyền
NGUYENKHIGIUCHONHATQUYEN = 4
# Ngắt đánh thường: Tự Động Công Kích (thẻ Cơ Bản, gửi bằng pf2; "pf 14" máy chủ bỏ qua) "pf2 14 <mục tiêu>" là bật / tắt qua lại,
# máy chủ báo "Sử dụng “Tự Động Công Kích”." / "Bạn đã ngừng “Tự Động Công Kích”." => gửi tới khi thấy tin ngừng, mỗi lần cách nhau
# THOIGIANCHONGATTANCONGVATLY giây chờ tin. Đổi mục tiêu / mục tiêu chết thì máy chủ tự ngừng, không báo
IDKYNANG_TUDONGCONGKICH = 14
TENKYNANG_TUDONGCONGKICH = "Tự Động Công Kích"
THOIGIANCHONGATTANCONGVATLY = 0.25


HINHTHUCSUDUNGKYNANG_CANMUCTIEU = 3
HINHTHUCSUDUNGKYNANG_KHONGCANMUCTIEU = 1
HINHTHUCSUDUNGKYNANG_CANKHOANHVUNG = 6

TRANGTHAICHUOT_BINHTHUONG = 0
TRANGTHAICHUOT_CHONMUCTIEU = 1  # Đang chỉ vào mục tiêu
TRANGTHAICHUOT_CHONMUCTIEUKYNANG = 2  # Bấm kỹ năng cần mục tiêu nhưng chưa có mục tiêu
TRANGTHAICHUOT_KHOANHVUNGKYNANG = 14  # Ví dụ Khai Thiên Tịch Địa của Thục Sơn
TRANGTHAICHUOT_DOITHOAI = 25

SUDUNGTUDONGXAKICH = "Sử dụng “Tự Động Xạ Kích”."

MAUPK_HOABINH = 0
MAUPK_NHOM = 1
MAUPK_BANG = 2
MAUPK_TUDO = 3

HIEUUNGKYNANG_THEOSAUNHOM = 11
HIEUUNGKYNANG_NGOAIKHANG = 3291
HIEUUNGKYNANG_NOIKHANG = 3292
HIEUUNGKYNANG_TIENTHANVODICH = 3254
HIEUUNGKYNANG_KIMCUONGBATHOAIDON = 653
HIEUUNGKYNANG_HUYETTHACH = 2
HIEUUNGKYNANG_PHAPLUCTHACH = 4
HIEUUNGKYNANG_LANHNGUYETTAMPHAP = 2221
HIEUUNGKYNANG_BANGPHACHNGANTAM = 2222
HIEUUNGKYNANG_TRONGTHUONG = 9020
HIEUUNGKYNANG_CHOANG = 9002
# Choáng, Bất Động (Côn Luân), Hôn Mê (Đường Môn) cùng hiệu ứng 9002; tên chỉ có trong ô hiệu ứng sau khi rê chuột xem tooltip nên phân biệt
# theo thời gian tối đa (đo 2026-10-27 trên Ngọc: choáng 1s, Bất Động 6s, Hôn Mê 30s): <= THOIGIANTOIDACHOANG giây là choáng (không làm gì
# được), <= THOIGIANTOIDABATDONG là Bất Động (không đi được, vẫn ra chiêu), dài hơn là Hôn Mê (không làm gì được, bị đánh thì tỉnh lại).
# Chưa chính xác hẳn: có choáng dài 6s (Thiên Cân của bảo thú giang hồ) sẽ bị coi là Bất Động
THOIGIANTOIDACHOANG = 3
THOIGIANTOIDABATDONG = 15
HIEUUNGKYNANG_NHANSAM = 6

HIEUUNGKYNANG_ROILOAN = 9018
HIEUUNGKYNANG_LAMCHAM = 9012
HIEUUNGKYNANG_DONGBANG = 9013

HIEUUNGKYNANG_KHOAPHAPBAO = 9561

HIEUUNGKYNANG_THAUCOTDINH = 2614
HIEUUNGKYNANG_HAPTINHMACHAM = 2616
HIEUUNGKYNANG_CHAYMAU = 9022

HIEUUNGKYNANG_DAUCHUYENTINHDI = 5016
HIEUUNGKYNANG_NGANCHAMDOACH = 5011  # Ngoại
HIEUUNGKYNANG_KIMCHAMDOACH = 5012  # Nội
HIEUUNGKYNANG_CUONGTHETHUAT = 5014
HIEUUNGKYNANG_ANTHANTHUAT = 3631
HIEUUNGKYNANG_LACTUYETVONGAN = 3641
HIEUUNGKYNANG_MATAMTHUAT = 3642
HIEUUNGKYNANG_BOPHONGHANH = 3643

HIEUUNGKYNANG_DAOHOALACANH = 211
HIEUUNGKYNANG_TRANCOTHANUY = 3162
HIEUUNGKYNANG_KIMTRUNGCHAO = 3161
HIEUUNGKYNANG_DATINCUONGLUC = 3191
HIEUUNGKYNANG_KIMCUONGTHANPHAP = 3192
HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN = 2114
HIEUUNGKYNANG_TRAMMAC = 9010
# Mộng du (Thôi Miên Thuật của Vân Mộng Cốc): không dùng được kỹ năng, người bị cũng không bị tấn công. Đo 2026-10-27 trên ThichVaCham:
# hiệu ứng 9016, có hại, 30s (không trùng id chiêu 5313)
HIEUUNGKYNANG_MONGDU = 9016
# Bảng hiệu ứng của mỗi đối tượng đọc 1 lần rồi nhớ bấy nhiêu giây (ngắn hơn 1 vòng bot): trong 1 vòng nhiều lượt quét / nhiều kiểm tra
# hiệu ứng (mộng du khi chọn mục tiêu, Thực Cốt, choáng, Hộ Thể Kim Cang...) trên cùng đối tượng dùng chung 1 lần đọc
THOIGIANNHOBANGHIEUUNG = 0.1
HIEUUNGKYNANG_MULOA = 9024

HIEUUNGKYNANG_THUCGIAP = 4143
HIEUUNGKYNANG_THUCCOT = 4144
HIEUUNGKYNANG_THUCTAM = 4145
HIEUUNGKYNANG_AMMANHAPTHE = 4147

HIEUUNGKYNANG_THIEUDOT = 9026
HIEUUNGKYNANG_CANKHONNADI = 4252
# Biến Thân Thuật (Côn Luân): biến thành cóc, không dùng được kỹ năng nào
HIEUUNGKYNANG_BIENTHANTHUAT = 4243
HIEUUNGKYNANG_THANTUEPHAPCHU = 4171
HIEUUNGKYNANG_LINHKHIHOTHE = 5911

HIEUUNGKYNANG_MANHHOBOPHAP = 2421
HIEUUNGKYNANG_KIMSUBOPHAP = 2422
HIEUUNGKYNANG_NGULOIAPDINH = 2516
HIEUUNGKYNANG_SINHTUTHANLUC = 3484
HIEUUNGKYNANG_THIENNGUYENDON = 298

HIEUUNGKYNANG_NGUYENKHIQUYNGUYEN = 3172
HIEUUNGKYNANG_HOTHEKIMCANG = 3173
HIEUUNGKYNANG_LACKICH = 2123

HIEUUNGKYNANG_PHUCHOISINHLUC = 9154

KYNANGBAOTHU_TROICHAN = 74139
KYNANGBAOTHU_THIENCAN = 74137
KYNANGBAOTHU_CAOCAPTHIENCAN = 74234
KYNANGBAOTHU_XUNHPHONG = 74241
KYNANGBAOTHU_CAOCAPTHIEUDOT = 74233
KYNANGBAOTHU_THOIDICHTHUAT = 74238
KYNANGBAOTHU_PHONGMATHUAT = 74237

HIEUUNGKYNANG_NGANHANHTU = 1808
HIEUUNGKYNANG_XALOITU = 1811

HIEUUNGBATLOITHUCSONCOTHEGIAIs = (HIEUUNGKYNANG_THUCCOT, HIEUUNGKYNANG_THUCGIAP, HIEUUNGKYNANG_THAUCOTDINH, HIEUUNGKYNANG_MULOA, HIEUUNGKYNANG_KHONGTHUNHAPBACHNHAN, HIEUUNGKYNANG_THIEUDOT)

LOAIDOITUONGPHIMTAT_KYNANG = 1
LOAIDOITUONGPHIMTAT_VATPHAM = 2

TRANGTHAIVANKHI_KHONGVANKHI = 0
TRANGTHAIVANKHI_DANGVANKHI = 1
TRANGTHAIVANKHI_VANKHITHANHCONG = 2
TRANGTHAIVANKHI_VANKHITHATBAI = 3

# Hành trang: 4 túi x 24 ô; số ô đang mở của từng túi đọc từ game (MoiTruong.get_dungluongtuihanhtrangs),
# không đọc được thì coi cả 4 túi mở đủ
SOLUONGTUIHANHTRANG = 4
SOLUONGOMOITUI = 24

# Trang bị đang mặc nằm ngay sau 96 ô hành trang, cùng cấu trúc ô (id ở +ô*4, tên ở +0x1A8 + ô*0x20):
# 96 mũ, 97 dây chuyền, 98 vũ khí, 99 áo, 100 đai, 101 giày, 102 pháp bảo, 103 ngọc, 104 cánh, 105 ngoại trang (đã đo trên 3 nhân vật)
# Mao Sơn: Di Tinh Đại Pháp (hồi nội lực bảo thú triệu hồi) dùng cách nhau tối thiểu chừng này giây, còn lại theo hồi chiêu của game
GIANCACHHOIBAOTHUTRIEUHOI = 5.
# Lưu Huyết Thuật hồi máu DẦN cho bảo thú triệu hồi: liên tục 8 giây, mỗi 2 giây 80 khí huyết (cấp 8, hồi chiêu 2s, 90 pháp lực)
# => chỉ dùng lại khi lần trước đã hồi xong
GIANCACHLUUHUYETTHUAT = 8.

# Tiêu hao kỹ năng (pháp lực / khí huyết / nguyên khí) đọc từ mô tả trong game được nhớ lại bấy nhiêu giây
THOIGIANNHOTIEUHAOKYNANG = 10.
# Có bảo thú (thú triệu hồi) còn dưới bấy nhiêu % sinh lực thì dùng Lưu Huyết Thuật
PHANTRAMSINHLUCLUUHUYETTHUAT = 90

VITRITRANGBIDAUTIEN = 96
SOLUONGOTRANGBI = 10
# Mảng thời gian hồi vật phẩm của client có đủ 106 ô (hành trang + trang bị)
SOLUONGOTHOIGIANHOI = VITRITRANGBIDAUTIEN + SOLUONGOTRANGBI
# Đã gửi lệnh dùng vật phẩm hồi sinh lực / nội lực mà chưa thấy client báo vào thời gian hồi (lệnh không thành công) thì
# chờ bấy nhiêu giây rồi gửi lại
THOIGIANCHOXACNHANHOIVATPHAM = 1.
# Vật phẩm cần dùng sẽ hồi xong trong vòng chừng này giây (≈ 1 vòng loop phụ 0.5s) thì chờ luôn tới lúc xong rồi dùng ngay
THOIGIANCHOHOIXONGTOIDA = 0.5
VITRITRANGBI_PHAPBAO = VITRITRANGBIDAUTIEN + 6
# Ô trang bị Chủ Tiệm Sửa Chữa sửa được: nón, hạng liên, vũ khí, áo, yêu đới, giày (pháp bảo / ngọc / cánh / ngoại trang không sửa)
VITRITRANGBISUADUOCs = tuple(range(VITRITRANGBIDAUTIEN, VITRITRANGBI_PHAPBAO))
# Mao Sơn bật "đổi đồ khi triệu hồi": trong lúc vận khí gọi bảo thú triệu hồi thì đeo "bộ đồ triệu hồi" đã ghi (thường là đồ tấn công),
# vận khí xong mặc lại bộ cũ. Bộ đồ ghi từ đồ đang mặc ở các ô trang bị này (nón, hạng liên, vũ khí, áo, yêu đới, giày, pháp bảo;
# không ngọc / cánh / ngoại trang). Loại theo ô nên không cần mô tả để biết món nào được ghi
VITRITRANGBIDOITRIEUHOIs = tuple(range(VITRITRANGBIDAUTIEN, VITRITRANGBI_PHAPBAO + 1))
# Pháp bảo đổi sang khi máu thấp (không hư hỏng), xong đeo lại pháp bảo cũ
PHAPBAOKHONGHUHONGs = ("Thượng Phương Bảo Kiếm", )

PHELIEMPHA = 66
PHEBACHKHOI = 82

MONPHAI_MAP = {
    2711: "maoson",
    2811: "vanmongcoc",
    2210: "thucson",
    2612: "duongmon",
    2110: "daohoanguyen",
    4211: "conluan",
    2410: "camvequan",
}
# Tên hiển thị của mã môn phái (giao diện chọn tên này, file cấu hình lưu mã)
TENMONPHAI = {
    "maoson": "Mao Sơn",
    "vanmongcoc": "Vân Mộng Cốc",
    "thucson": "Thục Sơn",
    "duongmon": "Đường Môn",
    "daohoanguyen": "Đào Hoa Nguyên",
    "conluan": "Côn Luân",
    "camvequan": "Cấm Vệ Quân",
}

# Vân Mộng Cốc buff đồng đội cùng máy theo môn phái: chỉ Ngân Châm Độ Ách hoặc chỉ Kim Châm Độ Ách.
# Môn phái không có trong 2 danh sách (hoặc không biết vì khác máy) thì buff cả hai như cũ
# Môn phái dùng chiêu phép thuật: bị Trầm Mặc thì không dùng được kỹ năng (vẫn đánh thường, di chuyển được)
# Dính Trận Pháp Lạc Ảnh (hiệu ứng HIEUUNGKYNANG_DAOHOALACANH, ~13s) thì không ra khỏi được chừng 3 ô quanh NGƯỜI DÙNG CHIÊU
# (đo 2026-10-26, Thọ nhốt 30: bị giữ ở cách Thọ 2-2.8 ô, có lần cách chỗ bị dính tới 4.5 ô): đích di chuyển ngoài bán kính này
# quanh tâm trận bị kéo về mép trận. Tâm trận = người chơi ngoài nhóm trong KHOANGCACHTIMNGUOIDUNGTRANDO ô lúc vừa bị dính, ưu tiên người đánh tay không (Đào Hoa Nguyên) rồi tới người gần nhất
BANKINHTRANDOLACANH = 2.5
KHOANGCACHTIMNGUOIDUNGTRANDO = 4.

MONPHAIPHEPTHUATs = ("vanmongcoc", "maoson", "conluan")

MONPHAICHIBUFFNGANCHAMs = ("daohoanguyen", "camvequan", "duongmon")
MONPHAICHIBUFFKIMCHAMs = ("vanmongcoc", "maoson", "conluan")

BANDO_TANTHUTHON = 1
BANDO_BACHMATRANG = 142
BANDO_TUONGLANG = 21
BANDO_MUCDA = 241
BANDO_QUELANG = 242
BANDO_THUCSON = 273
BANDO_DAOHOANGUYEN = 289
# Khai khoáng ở Hư Lăng Động quái đánh đau: ưu tiên Đại Huyết Thạch (hết mới dùng Tiểu Huyết Thạch)
BANDO_HULANGDONG = 381
BANDO_DUONGMON = 324
BANDO_VANMONGCOC = 165
BANDO_CONLUAN = 54
BANDO_MAOSON = 269
BANDO_RANHGIOIDAMLAY = 163
BANDO_DIAGIOIDAMLAY = 164
BANDO_MALANGDAO = 141
BANDO_DONGHAINGUTHON = 11
BANDO_KENHTRINHQUOC1 = 151
BANDO_KENHTRINHQUOC2 = 152
BANDO_KENHTRINHQUOC3 = 153
BANDO_CHIENTRUONG = 903
BANDO_COMO = 395

BANDO_YENTRUONGTHANH1 = 71
BANDO_YENTRUONGTHANH2 = 72
BANDO_YENTRUONGTHANH3 = 73
BANDO_TRIEUTRUONGTHANH1 = 31
BANDO_TRIEUTRUONGTHANH2 = 32
BANDO_TANTRUONGTHANH2 = 52
BANDO_LINHCOCDONG1 = 311
BANDO_LINHCOCDONG2 = 312
BANDO_LOANDAO1 = 321
BANDO_LOANDAO2 = 322
BANDO_BATQUAITRAN = 894
# Thành Kiều Quân Doanh: vào ở Tần Quốc (216, 64). Lăng Ly Sơn 3 tầng (Tầng Trên Lăng Mộ, Tầng Dưới Lăng Mộ, Tổng Giám Công Thư Phòng):
# vào ở Thuý Hoa Sơn (138, 117). id theo thứ tự tên trong menu/main/vl.dat và map/701..704.dat
BANDO_THANHKIEU = 701
BANDO_LANGLYSON1 = 702
BANDO_LANGLYSON2 = 703
BANDO_LANGLYSON3 = 704
# Phó bản: rời nhóm khi đang là trưởng nhóm sẽ giải tán, đá cả đội ra ngoài => tổ đội tự động không tự rời nhóm ở đây.
# Hồi Thành Phù là ra khỏi phó bản => tuyệt đối không dùng ở đây (get_lydokhonghoithanhphu)
BANDOPHOBANs = (BANDO_BATQUAITRAN, BANDO_THANHKIEU, BANDO_LANGLYSON1, BANDO_LANGLYSON2, BANDO_LANGLYSON3, 891, 892, 893, 894, 895, 896, 897, 898, 899)

BANDO_MADAPHO = 211
BANDO_CUTHUDAO = 549

BANDOFARMs = (BANDO_BACHMATRANG, BANDO_TUONGLANG, BANDO_QUELANG, BANDO_MUCDA, BANDO_RANHGIOIDAMLAY, BANDO_DIAGIOIDAMLAY, BANDO_MADAPHO, BANDO_YENTRUONGTHANH1, BANDO_TRIEUTRUONGTHANH1, BANDO_YENTRUONGTHANH2, BANDO_CUTHUDAO, BANDO_KENHTRINHQUOC1, BANDO_KENHTRINHQUOC2, BANDO_KENHTRINHQUOC3)

BANDOTUDONGLENSAUKHICHETs = (
    BANDO_RANHGIOIDAMLAY, BANDO_DIAGIOIDAMLAY, BANDO_DONGHAINGUTHON, BANDO_KENHTRINHQUOC1, BANDO_KENHTRINHQUOC2, BANDO_KENHTRINHQUOC3,
)

X_CHUTIEMTAPHOA_TANTHUTHON = 113
Y_CHUTIEMTAPHOA_TANTHUTHON = 145

X_QUANKHO_TANTHUTHON = 103
Y_QUANKHO_TANTHUTHON = 127
# Mỗi rương kho 7 x 7 ô
SOOMOIRUONGKHO = 49

X_SUGIAMONPHAI_CHU = 280
Y_SUGIAMONPHAI_CHU = 180

X_PHITACDOATNGANTRUYENTONG_CHU = 322
Y_PHITACDOATNGANTRUYENTONG_CHU = 127

X_PHITACDOATNGANTRUYENTONG_TANTHUTHON = 157
Y_PHITACDOATNGANTRUYENTONG_TANTHUTHON = 144

X_TANTHUTIENCO_THUCSON = 198
Y_TANTHUTIENCO_THUCSON = 154

X_XAPHU_THUCSON = 187
Y_XAPHU_THUCSON = 143

X_XAPHU_VANMONGCOC = 124
Y_XAPHU_VANMONGCOC = 48

X_TANTHUTIENCO_CHU = 322
Y_TANTHUTIENCO_CHU = 132

X_TRUONGQUALAO = 245
Y_TRUONGQUALAO = 158

X_BATQUAITRAN = 126
Y_BATQUAITRAN = 167

X_BACHKHOI = 67
Y_BACHKHOI = 51
X_LIEMPHA = 181
Y_LIEMPHA = 142

GOs = {
    (1, 0): 1,
    (1, 1): 2,
    (0, 1): 3,
    (-1, 1): 4,
    (-1, 0): 5,
    (-1, -1): 6,
    (0, -1): 7,
    (1, -1): 8,
}

BANDO_TEQUOC = 10
BANDO_HANQUOC = 20
BANDO_TRIEUQUOC = 30
BANDO_NGUYQUOC = 40
BANDO_TANQUOC = 50
BANDO_SOQUOC = 60
BANDO_YENQUOC = 70
BANDO_CHUQUOC = 80

BANDO_CULOC = 131

BAOTHUVATPHAMs = (SONGTUDUNGCAM, SONGTUANHMINH, THANTHUTHO, THANTHUTHIN, THANTHUMAYET, THANTHUDAN, THANTHUSUU, THANTHUDAN2, THANTHUSUU2, THANTHUCHUOT)
VATPHAMKHONGNHATs = tuple()
# Vật phẩm ưu tiên nhặt trên mọi hành động khác (tấn công, theo nhóm, gom quái, ...)
VATPHAMUUTIENNHATs = (LEBAOKHAIQUOC,)
VATPHAMTUDONGNHATs = (HACCAU, LAMCAU, HOACAU, HONGCAU, TUSAMDON, CAPCUUDON, HOATTAMDON, TIEUDAOTAN, KIMTANGTAN, QUYNGUYENDON, KHIMACHDON, TUTAMDON,  HOANGKIMTHANHY, "Thanh Đồng Bảo Hộp", TUKIMBAOHOP, "Mồi Câu", "Đá Tương Uyên", TIENTE, "Vô Song Điểm Phiếu", "Cờ Đỏ", "Sao Vàng", LEBAOKHAIQUOC, "Âu Dã Bảo Thạch", "Long Cốt", "Phấn Huỳnh Quang",
                      THANHTAMDON, TOAICAM, XALOITU,
                      # Phôi vũ khí cấp 75: Kiếm, Đao, Thương, Côn, Ám Khí, Quyền
                      "Ngọc Kiếm", "Kim Đao", "Xích Anh Thương", "Cổ Phương Côn", "Nguyệt Hoàn", "Thạch Điêu Quyền Nhẫn", )

DUAHAU = "Dưa hấu"
LAOTUU = "Lão Tửu"
THUONGPHUONGBAOKIEM = "Thượng Phương Bảo Kiếm"
CHUONGHAMTHIEN = "Chuông Hám Thiên"
TUIPHAPBAO = "Túi Pháp Bảo"
CHIENQUOCLENH = "Chiến Quốc Lệnh"
CUULONGTHANHOATRAO = "Cửu Long Thần Hỏa Trảo"
TINHNGUYENDON = "Tinh Nguyên Đơn"
HOIBANGPHU = "Hồi Bang Phù"
NGUYENLIEULUYENDONs = ("Hoàng Kỳ", "Cúc Dại", "Quả Anh Túc", "Điền Thất", "Táo Đỏ", "Trần Bì", "Dương Kim Hoa", "Linh Chi Thảo", "Sơn Sâm", "Cát Cánh", "Cam Thảo", "Sinh Địa", "Xuyên Tâm Liên", "Hoàng Liên", "Hà Thủ Ô", "La Hán Quả", "Bạch Kỳ", "Đương Quy", "Xuyên Bối", "Đông Trùng Thảo")
CUONGTHIPHU = "Cương Thi Phù"
# Danh sách không bán (VATPHAMKHONGBANs) đã chuyển thành luật Giữ mặc định trong luattuido_xq.LUATMACDINH (sửa ở tab Túi đồ)

# Khai khoáng (hái dược) ở các bản đồ này thì tự vứt các dược không cần (dù có luật Giữ)
BANDOHAIDUOCs = (261, 262, 263)
VATPHAMVUTKHIHAIDUOCs = ("La Hán Quả", "Hoàng Liên", "Hà Thủ Ô", "Xuyên Tâm Liên")

VATPHAMTUDONGNHATFARMs = (
    "Kiếm", "Đao", "Mâu", "Thủ", "Thương", "Sáo", "Bổng", " Y", "Giáp",
    "Côn", "Kích", " Bào", " Lý", " Mạo", "Phi Phong", " Nguyệt",
    "Quan", " Bào", " Liên", " Quần", " Hài", " Nhẫn", " Tiêu",
    "Đầu Cân", "Xú Diêm", " Đầu Cân", "Nghênh Phong Trảm", " Mão", " Tố Quần", "Nhập môn", " Quần",
    " Nguyệt", "Trứng gà", " cấp ", "Kim Cương"
)

# Xếp chồng tự nhận biết (món có số lượng >= 1 trong hành trang), 1 ô tối đa = số lớn nhất từng thấy (ít nhất 30);
# món có số tối đa khác thì ghi ở đây
# 1 ô hành trang chồng tối đa bao nhiêu món (game nâng từ 30 lên 100); món nào khác mức này thì ghi riêng vào SOLUONGXEPCHONGTOIDA_MAP
SOLUONGXEPCHONGMACDINH = 100
SOLUONGXEPCHONGTOIDA_MAP = {
}

DANHHIEU_MAP = defaultdict(lambda: False)

BANDO_TIVO = 885
BANDO_BANGPHAI = 886
BANDOKHONGTANCONGs = (BANDO_TANTHUTHON, BANDO_CHUQUOC, )
BANDOKHONGPKs = (BANDO_TANTHUTHON, BANDO_CHUQUOC, BANDO_THUCSON, BANDO_DAOHOANGUYEN, BANDO_DUONGMON, BANDO_VANMONGCOC, BANDO_TEQUOC, BANDO_HANQUOC, BANDO_TRIEUQUOC, BANDO_NGUYQUOC, BANDO_TANQUOC, BANDO_SOQUOC, BANDO_YENQUOC, )

TEQUOC = [(127, 87, 10), (137, 96, 10), (152, 104, 10), (164, 104, 10), (170, 84, 10), (148, 86, 10), (156, 61, 10), (171, 82, 10), (181, 96, 10), (198, 87, 10), (212, 82, 10), (169, 107, 10), (189, 125, 10), (226, 103, 10), (249, 95, 10), (220, 134, 10), (202, 154, 10), (202, 157, 10), (173, 177, 10), (166, 194, 10), (131, 213, 10), (133, 206, 10), (160, 203, 10), (171, 243, 10), (183, 196, 10), (190, 233, 10), (205, 234, 10), (227, 241, 10), (235, 215, 10), (198, 168, 10), (236, 174, 10), (247, 200, 10),
          (268, 138, 10), (312, 119, 10), (297, 131, 10), (324, 142, 10), (338, 172, 10), (291, 195, 10), (256, 192, 10), (266, 159, 10)]
HANQUOC = [(110, 106, 20), (134, 122, 20), (156, 136, 20), (174, 153, 20), (150, 168, 20), (112, 193, 20), (166, 190, 20), (192, 183, 20), (233, 209, 20), (262, 182, 20), (239, 165, 20), (221, 138, 20), (252, 147, 20), (255, 112, 20), (274, 134, 20), (278, 113, 20), (274, 134, 20), (255, 112, 20), (252, 147, 20), (221, 138, 20), (239, 165, 20), (262, 182, 20), (233, 209, 20), (192, 183, 20), (166, 190, 20), (112, 193, 20), (150, 168, 20), (174, 153, 20), (156, 136, 20), (134, 122, 20), (110, 106, 20)]
TRIEUQUOC = [(112, 108, 30), (64, 140, 30), (103, 159, 30), (134, 178, 30), (143, 115, 30), (176, 140, 30), (209, 156, 30), (243, 143, 30), (261, 115, 30), (257, 148, 30), (277, 162, 30), (308, 178, 30), (286, 192, 30), (254, 208, 30), (230, 226, 30), (214, 207, 30), (171, 206, 30), (163, 225, 30), (171, 206, 30), (214, 207, 30), (230, 226, 30), (254, 208, 30), (286, 192, 30), (308, 178, 30), (277, 162, 30), (257, 148, 30), (261, 115, 30), (243, 143, 30), (209, 156, 30), (176, 140, 30), (143, 115, 30),
             (134, 178, 30), (103, 159, 30), (64, 140, 30), (112, 108, 30)]
NGUYQUOC = [(254, 90, 40), (218, 116, 40), (178, 105, 40), (187, 132, 40), (195, 161, 40), (236, 179, 40), (258, 216, 40), (231, 206, 40), (204, 189, 40), (166, 178, 40), (146, 160, 40), (131, 131, 40), (119, 104, 40), (94, 135, 40), (117, 150, 40), (87, 177, 40), (130, 215, 40), (87, 177, 40), (117, 150, 40), (94, 135, 40), (119, 104, 40), (131, 131, 40), (146, 160, 40), (166, 178, 40), (204, 189, 40), (231, 206, 40), (258, 216, 40), (236, 179, 40), (195, 161, 40), (187, 132, 40), (178, 105, 40),
            (218, 116, 40), (254, 90, 40)]
TANQUOC = [(136, 81, 50), (161, 92, 50), (185, 53, 50), (206, 71, 50), (169, 92, 50), (188, 108, 50), (202, 123, 50), (223, 125, 50), (235, 113, 50), (253, 127, 50), (229, 139, 50), (213, 165, 50), (185, 177, 50), (174, 194, 50), (143, 204, 50), (171, 237, 50), (202, 197, 50), (218, 236, 50), (239, 235, 50), (254, 191, 50), (285, 166, 50), (248, 161, 50), (285, 166, 50), (254, 191, 50), (239, 235, 50), (218, 236, 50), (202, 197, 50), (171, 237, 50), (143, 204, 50), (174, 194, 50), (185, 177, 50),
           (213, 165, 50), (229, 139, 50), (253, 127, 50), (235, 113, 50), (223, 125, 50), (202, 123, 50), (188, 108, 50), (169, 92, 50), (206, 71, 50), (185, 53, 50), (161, 92, 50), (136, 81, 50)]
SOQUOC = [(105, 167, 60), (116, 130, 60), (141, 158, 60), (140, 118, 60), (168, 128, 60), (159, 96, 60), (193, 107, 60), (176, 67, 60), (217, 58, 60), (214, 92, 60), (213, 113, 60), (236, 134, 60), (259, 156, 60), (299, 172, 60), (324, 156, 60), (312, 125, 60), (296, 105, 60), (275, 90, 60), (229, 92, 60), (220, 61, 60), (203, 100, 60), (175, 70, 60), (180, 108, 60), (182, 127, 60), (155, 98, 60), (158, 143, 60), (136, 120, 60), (116, 122, 60), (85, 153, 60), (109, 162, 60), (133, 163, 60)]

YENQUOC = [(355, 147, 70), (331, 129, 70), (327, 165, 70), (307, 148, 70), (291, 178, 70), (293, 197, 70), (270, 180, 70), (240, 158, 70), (221, 137, 70), (224, 78, 70), (205, 53, 70), (184, 92, 70), (187, 133, 70), (160, 146, 70), (129, 173, 70), (105, 193, 70), (111, 163, 70), (139, 145, 70), (128, 144, 70), (110, 141, 70), (88, 133, 70), (74, 127, 70), (69, 130, 70), (50, 151, 70), (84, 115, 70), (106, 102, 70), (129, 98, 70), (142, 88, 70), (139, 89, 70), (133, 98, 70), (102, 98, 70), (82, 119, 70)]
# Điểm đi vòng ngoài thành 7 nước (đi được hết, không lọt vào chỗ kẹt): dùng khi đi khắp bản đồ tìm đối thủ (Truy Bắt Thích Khách /
# Truy Sát Phản Đồ). id bản đồ -> [(x, y), ...]
DIEMNGOAITHANH_MAP = {idbando: [(x, y) for x, y, _ in diems] for idbando, diems in ((BANDO_TEQUOC, TEQUOC), (BANDO_HANQUOC, HANQUOC),
    (BANDO_TRIEUQUOC, TRIEUQUOC), (BANDO_NGUYQUOC, NGUYQUOC), (BANDO_TANQUOC, TANQUOC), (BANDO_SOQUOC, SOQUOC), (BANDO_YENQUOC, YENQUOC))}

TRIEUTRUONGTHANH2 = [(52, 82, 32), (63, 92, 32), (76, 104, 32), (90, 112, 32), (104, 122, 32), (116, 133, 32), (129, 142, 32), (144, 150, 32), (162, 164, 32), (176, 156, 32), (191, 145, 32), (206, 136, 32), (218, 126, 32), (230, 118, 32)]
TANTRUONGTHANH2 = [(232, 111, 52), (219, 102, 52), (205, 90, 52), (192, 80, 52), (176, 81, 52), (162, 94, 52), (149, 106, 52), (134, 116, 52), (118, 128, 52), (98, 141, 52), (84, 131, 52), (67, 121, 52), (51, 106, 52), (29, 92, 52)]
YENTRUONGTHANH2 = [(158, 142, 72), (144, 131, 72), (128, 117, 72), (112, 105, 72), (96, 94, 72), (79, 81, 72), (67, 73, 72), (48, 62, 72), (31, 51, 72)]

LINHCOCDONG1 = [(105, 53, 311), (108, 70, 311), (95, 85, 311), (106, 99, 311), (89, 120, 311), (110, 135, 311), (132, 147, 311), (147, 133, 311), (139, 102, 311), (154, 76, 311), (167, 55, 311), (182, 68, 311), (169, 84, 311), (190, 69, 311), (207, 80, 311), (215, 96, 311), (196, 101, 311), (176, 110, 311), (187, 133, 311), (170, 145, 311), (149, 159, 311), (130, 149, 311)]
LINHCOCDONG2 = [(158, 135, 312), (152, 117, 312), (173, 109, 312), (197, 103, 312), (205, 83, 312), (183, 68, 312), (167, 50, 312), (141, 39, 312), (132, 56, 312), (153, 75, 312), (158, 99, 312), (132, 90, 312), (114, 99, 312), (93, 83, 312), (106, 67, 312), (110, 41, 312), (79, 56, 312), (84, 79, 312), (61, 76, 312), (51, 94, 312), (72, 109, 312), (88, 125, 312), (111, 141, 312), (135, 154, 312), (158, 144, 312)]

LOANDAO1 = [(92, 122, 321), (110, 108, 321), (124, 95, 321), (145, 109, 321), (161, 98, 321), (143, 109, 321), (126, 96, 321), (108, 107, 321), (91, 95, 321), (74, 81, 321), (54, 93, 321), (37, 79, 321), (55, 63, 321), (72, 53, 321), (88, 66, 321), (108, 42, 321), (133, 62, 321), (144, 81, 321), (162, 69, 321), (180, 81, 321)]
LOANDAO2 = [(46, 98, 322), (65, 84, 322), (56, 65, 322), (70, 52, 322), (86, 63, 322), (129, 31, 322), (165, 59, 322), (143, 75, 322), (124, 63, 322), (107, 76, 322), (127, 93, 322), (142, 103, 322), (184, 74, 322), (142, 104, 322), (127, 95, 322), (104, 111, 322), (85, 126, 322), (67, 112, 322), (84, 99, 322), (67, 85, 322)]

TANTHUTHON = [(174, 119, 1), (212, 90, 1), (229, 99, 1), (210, 143, 1), (240, 133, 1), (285, 127, 1), (307, 150, 1), (241, 176, 1), (213, 189, 1), (214, 218, 1), (244, 236, 1), (295, 198, 1), (315, 175, 1), (273, 192, 1), (245, 203, 1)]
BACHMATRANG = [(115, 46, 264), (92, 67, 264), (69, 95, 264), (88, 107, 264), (115, 132, 264), (128, 91, 264), (149, 73, 264), (172, 71, 264), (197, 83, 264), (213, 98, 264), (180, 146, 264), (149, 172, 264), (44, 98, 142), (73, 116, 142), (105, 73, 142), (140, 50, 142), (143, 71, 142), (161, 93, 142), (178, 91, 142), (197, 110, 142), (215, 125, 142), (238, 114, 142), (249, 112, 142), (225, 128, 142), (198, 141, 142), (164, 159, 142), (151, 161, 142), (177, 129, 142), (153, 103, 142), (116, 95, 142),
               (88, 108, 142), (69, 113, 142)]
TUONGLANG = [(140, 56, 21), (158, 59, 21), (174, 63, 21), (169, 76, 21), (178, 81, 21), (180, 97, 21), (178, 108, 21), (164, 110, 21), (154, 105, 21), (146, 101, 21), (128, 96, 21), (101, 103, 21), (80, 100, 21), (71, 97, 21), (71, 78, 21), (82, 66, 21), (110, 71, 21), (117, 77, 21), (123, 95, 21), (95, 108, 21), (72, 105, 21), (107, 117, 21), (128, 132, 21), (154, 128, 21)]
QUELANG = [(129, 47, 242), (132, 68, 242), (117, 77, 242), (124, 92, 242), (127, 104, 242), (126, 119, 242), (105, 122, 242), (88, 112, 242), (70, 90, 242), (54, 84, 242), (58, 78, 242), (75, 75, 242), (87, 62, 242), (92, 65, 242), (107, 63, 242), (125, 56, 242), (131, 53, 242)]
MUCDA = [(57, 90, 241), (76, 60, 241), (100, 48, 241), (125, 43, 241), (132, 49, 241), (134, 77, 241), (142, 60, 241), (155, 64, 241), (161, 91, 241), (152, 102, 241), (137, 116, 241), (109, 125, 241), (100, 130, 241), (101, 113, 241), (84, 105, 241), (74, 95, 241), (93, 93, 241), (94, 82, 241)]

RANHGIOIDAMLAY = [(89, 94, 163), (76, 87, 163), (67, 77, 163), (79, 61, 163), (90, 36, 163), (91, 40, 163), (92, 55, 163), (103, 63, 163), (98, 71, 163), (112, 65, 163), (125, 64, 163), (130, 74, 163), (113, 86, 163), (100, 93, 163), (89, 97, 163)]
MALANGDAO = [(245, 193, 141), (242, 174, 141), (230, 147, 141), (217, 130, 141), (216, 160, 141), (222, 178, 141), (223, 200, 141), (208, 199, 141), (202, 174, 141), (184, 156, 141), (171, 147, 141), (163, 149, 141), (147, 148, 141), (130, 137, 141), (124, 124, 141), (114, 113, 141), (96, 101, 141), (73, 93, 141), (69, 87, 141), (73, 69, 141), (88, 68, 141), (105, 75, 141), (123, 91, 141), (138, 103, 141), (147, 117, 141), (158, 120, 141), (164, 108, 141), (147, 85, 141), (135, 75, 141), (118, 67, 141),
             (110, 52, 141), (107, 48, 141)]
CULOC = [(64, 109, 131), (56, 89, 131), (76, 68, 131), (103, 53, 131), (120, 69, 131), (98, 91, 131), (90, 116, 131), (90, 130, 131), (98, 93, 131), (122, 118, 131), (160, 105, 131), (150, 64, 131), (130, 40, 131), (102, 52, 131)]
MADAPHO = [(144, 141, 211), (103, 142, 211), (80, 113, 211), (78, 76, 211), (110, 70, 211), (117, 90, 211), (131, 97, 211), (118, 64, 211), (155, 61, 211), (182, 85, 211), (188, 119, 211), (168, 138, 211)]
KENHTRINHQUOC1 = [(106, 101, 151), (90, 87, 151), (79, 77, 151), (76, 66, 151), (63, 53, 151), (74, 40, 151), (88, 36, 151), (101, 48, 151), (106, 51, 151), (83, 33, 151), (67, 46, 151), (63, 56, 151), (79, 65, 151), (83, 73, 151), (77, 81, 151), (93, 91, 151), (103, 100, 151)]
KENHTRINHQUOC2 = [(126, 79, 152), (110, 66, 152), (90, 52, 152), (74, 41, 152), (62, 39, 152), (49, 52, 152), (56, 68, 152), (72, 79, 152), (87, 88, 152), (96, 97, 152), (101, 101, 152), (98, 99, 152), (83, 88, 152), (64, 73, 152), (50, 61, 152), (64, 41, 152), (90, 50, 152), (106, 63, 152), (118, 73, 152)]
KENHTRINHQUOC3 = [(89, 111, 3), (69, 104, 3), (55, 99, 3), (47, 78, 3), (68, 49, 3), (116, 42, 3), (138, 49, 3), (142, 67, 3), (101, 82, 3), (146, 82, 3), (117, 98, 3), (108, 108, 3), (94, 113, 3), (87, 99, 3), (37, 51, 153), (56, 63, 153), (67, 72, 153), (79, 84, 153), (86, 90, 153), (99, 84, 153), (105, 100, 153), (113, 101, 153), (119, 99, 153), (102, 96, 153), (116, 72, 153), (102, 58, 153), (87, 47, 153), (67, 33, 153), (75, 37, 153), (92, 53, 153), (111, 67, 153), (103, 84, 153), (103, 99, 153),
                  (118, 101, 153), (103, 95, 153), (89, 86, 153), (70, 75, 153), (44, 54, 153)]
YENTRUONGTHANH1 = [(220, 123, 71), (200, 136, 71), (182, 148, 71), (161, 142, 71), (144, 128, 71), (121, 116, 71), (98, 101, 71), (71, 74, 71), (55, 65, 71), (77, 81, 71), (97, 97, 71), (122, 115, 71), (150, 132, 71), (175, 153, 71), (192, 140, 71), (215, 125, 71)]

THAONGUYEN = [(79, 125, 510), (142, 64, 510), (179, 58, 510), (227, 86, 510), (246, 118, 510), (198, 173, 510), (142, 175, 510), (133, 109, 510), (194, 98, 510), (177, 149, 510), (145, 122, 510), (168, 125, 510)]

# Tên hiển thị của bản đồ theo ID (dùng cho lộ trình mẫu trên bảng điều khiển). Tên nào sai dấu thì sửa trực tiếp ở đây.
def laytenbando(idbando):
    try:
        return laytenbandogame(int(idbando)) or f"Bản đồ {idbando}"
    except (TypeError, ValueError):
        return f"Bản đồ {idbando}"


DIEMDANHXUNGQUANH_MAP = {
    BANDO_TRIEUTRUONGTHANH2: TRIEUTRUONGTHANH2,
    BANDO_TANTRUONGTHANH2: TANTRUONGTHANH2,
    BANDO_YENTRUONGTHANH2: YENTRUONGTHANH2,
    BANDO_YENTRUONGTHANH1: YENTRUONGTHANH1,

    BANDO_LINHCOCDONG1: LINHCOCDONG1,
    BANDO_LINHCOCDONG2: LINHCOCDONG2,

    BANDO_LOANDAO1: LOANDAO1,
    BANDO_LOANDAO2: LOANDAO2,

    BANDO_BACHMATRANG: BACHMATRANG,
    BANDO_TUONGLANG: TUONGLANG,
    BANDO_QUELANG: QUELANG,
    BANDO_MUCDA: MUCDA,
    BANDO_RANHGIOIDAMLAY: RANHGIOIDAMLAY,
    BANDO_MALANGDAO: MALANGDAO,
    BANDO_CULOC: CULOC,
    BANDO_MADAPHO: MADAPHO,
    BANDO_KENHTRINHQUOC1: KENHTRINHQUOC1,
    BANDO_KENHTRINHQUOC2: KENHTRINHQUOC2,
    BANDO_KENHTRINHQUOC3: KENHTRINHQUOC3,
    510: THAONGUYEN,

    "{}_{}".format(BANDO_CHIENTRUONG, PHELIEMPHA): [(60, 49, 903)],
    "{}_{}".format(BANDO_CHIENTRUONG, PHEBACHKHOI): [(181, 141, 903)]
}

# Vùng cấm (đi vào sẽ bị chuyển bản đồ): mọi cổng chuyển bản đồ (bando_xq.BANDOCONG_MAP, vòng tròn BANKINHVUNGCAMCONG quanh tâm cổng)
# cộng các vùng cấm khác cổng ghi tay dưới đây (vùng rộng / đường dài, điểm dịch chuyển không có trong jmp.dat)
BANKINHVUNGCAMCONG = 6.
# Đứng cách tâm cổng trong khoảng này thì không dùng lệnh nhặt xung quanh của game (nó tự chạy tới vật phẩm, có thể lọt vào cổng)
KHOANGCACHGANCONGKHONGNHATXUNGQUANH = 15.
KHUVUCCAM_MAP = {
    BANDO_BACHMATRANG: [
        {"type": "circle", "x": 80, "y": 122, "r": 9.0},
        {"type": "line", "x1": 132, "y1": 159, "x2": 160, "y2": 139, "r": 9.0},
        {"type": "line", "x1": 131, "y1": 111, "x2": 160, "y2": 139, "r": 9.0},
    ],
    BANDO_MALANGDAO: [
        {"type": "line", "x1": 116, "y1": 116, "x2": 145, "y2": 150, "r": 9.0},
        {"type": "line", "x1": 93, "y1": 96, "x2": 124, "y2": 118, "r": 9.0},
    ],
    BANDO_KENHTRINHQUOC1: [
        {"type": "circle", "x": 108, "y": 57, "r": 6.0},
        # Phó bản Tập Kích Môn Phái dùng chung bản đồ (id vẫn là 151): đi vào 2 chỗ này bị kẹt không đi tiếp được, phải lùi tay
        {"type": "circle", "x": 103, "y": 53, "r": 3.0},
        {"type": "circle", "x": 96, "y": 96, "r": 3.0},
    ],
}
VUNGCAM_MAP = {
    idbando: [{"type": "circle", "x": x, "y": y, "r": BANKINHVUNGCAMCONG} for _, x, y, _, _ in BANDOCONG_MAP.get(idbando, ("", ()))[1]]
             + KHUVUCCAM_MAP.get(idbando, [])
    for idbando in BANDOCONG_MAP.keys() | KHUVUCCAM_MAP.keys()
}

# Menu phù của Tân Thủ Tiên Cô (máy chủ gửi, không có trong file game; chụp trong game 2026-10-27): nhóm thứ i (theo cấp) mở bằng
# "welcome.<i>00", lựa chọn thứ j trong nhóm là "welcome.<i * 100 + j>". Tên lựa chọn là tên bản đồ, tra id bằng bando_xq.layidbandotheoten
MENUTANTHUTIENCOs = (
    ("Sở Phương Thành 1", "Sở Phương Thành 2", "Sở Phương Thành 3", "Thượng Dung Quan", "Hoa Sơn", "Đào Hoa Nguyên", "Triều Dương Phong"),  # cấp 10-14
    ("Thủ Dương Sơn", "Thuý Hoa Sơn", "Hàm Cốc Quan"),  # cấp 15-19
    ("Vô Định Hà 1", "Vô Định Hà 2", "Bờ Vô Định Hà", "Tương Lăng", "Mã Lăng Đạo", "Bạch Mã Trang", "Mã Đạp Hồ"),  # cấp 20-24
    ("Hổ Lao Quan", "Ky Quan", "Cự Lộc", "Trác Lộc", "Dị Thủy", "Quế Lăng", "Mục Dã", "Thái Hành Sơn", "Tấn Dương", "Bình Nguyên",
     "Nhạn Môn Quan", "Trường Bình"),  # cấp 25-30
    ("Ranh Giới Đầm Lầy", "Địa Giới Đầm Lầy", "Chân Núi Đại Biệt", "Đại Biệt Sơn", "Vu Sơn", "Bà Dương Hồ", "Xích Bích", "Thái Hồ",
     "Chân Núi Thái Sơn", "Thái Sơn"),  # cấp 31-40
    ("Đông Hải Ngư Thôn", "Bờ Đông Hải", "Hải Tân 1", "Hải Tân 2", "Đông Hải Đảo", "Kênh Trịnh Quốc 1", "Kênh Trịnh Quốc 2", "Kênh Trịnh Quốc 3"),  # cấp 41-50
)
# id bản đồ -> các bước "tallk <id NPC># <bước>" để phù tới
DICHUYENTANTHUTIENCO_MAP = {
    layidbandotheoten(ten): [f"welcome.{nhom}00", f"welcome.{nhom * 100 + thutu}"]
    for nhom, tens in enumerate(MENUTANTHUTIENCOs, 1) for thutu, ten in enumerate(tens, 1)
}

CHUDICHTRAM = "Chủ Dịch Trạm"

# In ra console mọi câu lệnh gửi vào game và mỗi lần kỹ năng bị khoá chặn (để dò lỗi), tắt thì để False
IS_LOGCAULENH = True
# Ghi log mỗi lần lý do / điểm đích di chuyển thay đổi, và đích thật sự gửi đi ([DI CHUYỂN], [ĐI Ô], [TÌM ĐƯỜNG])
IS_LOGDICHUYEN = True

# Xoay vòng lệnh chiêu / đánh giữa các bot: tại mỗi thời điểm chỉ 1 bot được ra chiêu / đánh, giữ lượt ngẫu nhiên KHOANGGIULUOTLENH giây
# (trong đó gửi bao nhiêu lệnh cũng được) rồi nhường bot đang chờ kế tiếp, để các bot không cùng ra chiêu một lúc như máy.
# Đây là giá trị mặc định: chỉnh trên giao diện (tab Chiến đấu > Nhịp lệnh) thì lưu vào _internal/dieuphoi.json và dùng giá trị trong đó
IS_XOAYVONGLENHGIUACACBOT = True
KHOANGGIULUOTLENH = (1.0, 2.0)
# Bot đang giữ lượt mà quá ngần này giây không gửi chiêu có mục tiêu nào (không có chiêu cần dùng, hồi chiêu, hết quái...) thì nhường ngay
# cho bot khác. Lúc đang xuất chiêu (bot không gửi gì) luồng nhanh báo còn hoạt động nên không mất lượt giữa 2 chiêu; phần còn lại
# (vòng lặp chính 0.1s + chờ game chuyển tư thế 0.15s) cần dư ra. Cũng chỉnh được trên giao diện
THOIGIANNHUONGLUOTKHIRANH = 0.5
# Chỉ xoay vòng chiêu của nhân vật (pf <id> [mục tiêu], cả pf2), xem dieuphoi_xq.is_lenhxoayvong. Chiêu vận khí (IDKYNANGVANKHIs: đứng
# vận khí cả lúc, ít lộ), lệnh chiêu đặc biệt dạng "pf <id>.<x>" (triệu hồi khẩn cấp, Xuyên Không Hành), kỹ năng bảo thú (pf5),
# đánh thường (kill) và mọi lệnh khác (get, desc, use, move đồ, tallk NPC, pet, team, bán, vứt...) gửi ngay không chờ lượt
IDKYNANGVANKHIs = {VITRIKYNANG_LOIDONGCUUTHIEN, VITRIKYNANG_TRIEUHOIQUYTOT, VITRIKYNANG_TRIEUHOITHIENBINH, VITRIKYNANG_TRIEUHOICUONGTHI,
                   VITRIKYNANG_RAIDAUTHANHBINH, VITRIKYNANG_TOANPHONGQUYET, VITRIKYNANG_LOILONGQUYET}
# Bắt đầu di chuyển (nhân vật đang đứng mà bắt đầu chạy) cũng chia lượt như vậy nhưng trên kênh riêng (không làm chậm lệnh),
# để 3-4 nhân vật không cùng lúc nhấc chân. Đang chạy rồi thì các lần click chỉnh hướng đi ngay. Cũng chỉnh được trên giao diện
IS_XOAYVONGBATDAUDICHUYEN = True
KHOANGNGHIBATDAUDICHUYEN = (0.15, 0.5)
# Lệnh khẩn cấp (bơm máu, cứu sinh...) không phải chờ lượt
IS_LENHKHANCAPKHONGCHOLUOT = True
# Chờ lượt quá lâu (bot khác treo/crash giữa chừng) thì cứ gửi, không kẹt mãi
THOIGIANCHOLUOTTOIDA = 2.0
# Chiêu khống chế (Thôn Kình -> Trọng Thương, Phong Ma Quyết -> Trầm Mặc...) gửi lên 1 mục tiêu thì giữ chỗ trong khoảng này:
# các bot khác thấy mục tiêu chưa dính hiệu ứng (chiêu đang bay / chưa cập nhật) cũng không gửi trùng, chuyển sang chiêu khác.
# Hết khoảng mà mục tiêu vẫn chưa dính (né, kháng) thì bot nào cũng được gửi lại
THOIGIANGIUKYNANGMUCTIEU = 2.0

# Nhiều cửa sổ cùng phát nhạc nghe bị vọng: chỉ để tiếng cửa sổ có nhân vật ưu tiên cao nhất trong danh sách tổ đội tự động
# (nhóm đầu, ID đứng trước), các cửa sổ khác tắt tiếng trong Volume Mixer của Windows. Thoát tool thì bật lại tiếng tất cả
IS_CHIBATAMTHANHCUASOUUTIEN = True
THOIGIANKIEMTRAAMTHANH = 2.

# Dữ liệu chung giữa các cửa sổ (shared_data) đọc lại sau mỗi khoảng này (các cửa sổ cập nhật 0.25s/lần)
THOIGIANNHOSHAREDDATA = 0.25

# Chết rồi chờ bấy nhiêu giây (có thể được người khác cứu) mới tự phục sinh
THOIGIANCHOTRUOCKHIPHUCSINH = 30.

# Kỹ năng (có hay không mục tiêu) gửi >= SOLANGUITOIDASPAMKYNANG lần trong SOGIAYDEMSPAMKYNANG giây (tức là game báo sẵn sàng mà kỹ năng không ra)
# thì tạm khoá riêng kỹ năng đó THOIGIANKHOASPAMKYNANG giây
CAPDOTOITHIEUTETHANTUONG = 60
# Bảo thú triệu hồi còn dưới PHANTRAMSINHLUCTETHANTUONG% sinh lực thì Tế Thần Tướng
PHANTRAMSINHLUCTETHANTUONG = 25
# Mệnh Tế hồi cho cả nhóm trong 21x21 ô quanh bản thân (10 ô mỗi phía)
KHOANGCACHHIEUQUAMENHTE = 10

# Bảo thú kỹ năng triệu hồi xa nhân vật quá KHOANGCACHGOIBAOTHUVE ô thì gọi theo sau, tới khi về trong KHOANGCACHBAOTHUDAVE ô mới cho đánh tiếp
KHOANGCACHGOIBAOTHUVE = 18.
KHOANGCACHBAOTHUDAVE = 9.
# Đang gọi về thì gửi lệnh Theo sau đều mỗi chừng này giây tới khi về gần: xa đủ thì mỗi lệnh phù bảo thú về cạnh chủ, chưa đủ
# xa thì mỗi lệnh chỉ chạy thêm một đoạn => gọi một lần (hoặc dãn cách dài) nó chạy được một đoạn lại quay về chỗ cũ
THOIGIANGOIBAOTHUVE = 0.5

# Chờ lệnh đánh: đang ra đòn / dùng phép thì không gửi lệnh đánh nào (game đang bận; game cập nhật cờ sẵn sàng chậm, gửi chiêu khác là
# cắt ngang chiêu đang ra), còn lại (đứng im, di chuyển, khựng sau đòn) gửi ngay, riêng vừa gửi xong thì chờ tối đa ngần này giây
# cho game kịp chuyển tư thế (nếu không sẽ gửi tiếp chiêu khác, cắt ngang chiêu vừa gửi). Phải ngắn hơn 1 vòng bot (~0.123s):
# 0.15 làm cứ gửi 1 vòng lại bỏ 1 vòng => spam chiêu thực tế 0.25s/lần (đo log 2026-10-28), lúc server nhận bị làm tròn theo 0.25s
THOIGIANCHOPHANUNGLENH = 0.1
# Chọn mục tiêu khi đang chạy: con nằm sau lưng (ngược hướng đang chạy) bị tính xa thêm ngần này ô, để không quay đầu đổi qua lại
PHATMUCTIEUSAULUNG = 3.
# Mục tiêu đang đánh chỉ bị thay bằng con khác chỉ vì gần hơn khi con đó gần hơn ít nhất ngần này ô (giữa các ứng viên khác chỉ cần 0.5):
# hai con hai bên gần ngang nhau thì cứ chạy về phía con này vài bước là con kia lại "gần hơn" => đổi qua lại liên tục, đứng một chỗ
CHENHLECHKHOANGCACHDOIMUCTIEU = 1.5

# Khựng sau đòn (tư thế 11) chỉ là hiệu ứng che mắt ở client (máy chủ không tính): luồng nhanh thấy tư thế 11 là ghi về đứng im ngay
IS_BOKHUNGSAUTANCONG = True
CHUKYBOKHUNGSAUTANCONG = 0.02
# Chỉ bỏ khựng khi tư thế khựng sau đòn đã kéo dài chừng này giây (đặt ngay khi vừa vào khựng thì cắt ngang đòn / chiêu chưa xong)
THOIGIANCHOBOKHUNGSAUTANCONG = 1.
# Sau khi hết tư thế xuất chiêu (6 / 9, ~0.68s) còn khựng chừng này giây: vẫn dùng kỹ năng được nhưng không di chuyển
# (MoiTruong.get_is_dangxuatchieu)
THOIGIANKHUNGSAUXUATCHIEU = 1.
# Trong lúc xuất chiêu / khựng, mỗi vòng đẩy mốc "được tự gửi lệnh" của client lên trước chừng này giây để client không tự
# bước (MoiTruong.action_chandichuyen); phải dài hơn chu kỳ LoopGiuOTrongHanhTrang
THOIGIANCHANTUDICHUYENCLIENT = 0.15
# Người chơi giữ chuột trái trên cửa sổ game quá THOIGIANGIUCHUOTTOITHIEU giây (kéo nhân vật đi, click thường không tính):
# bot ngưng tấn công / di chuyển, nhả chuột rồi còn ngưng thêm THOIGIANNGUNGSAUNHACHUOT giây để nhân vật kịp đi tiếp theo
# click cuối (MoiTruong.get_is_dangclickchuottrai)
THOIGIANGIUCHUOTTOITHIEU = 0.3
THOIGIANNGUNGSAUNHACHUOT = 0.4
# Gửi chiêu trong tầm rồi thì chặn client tự bước tối đa chừng này giây chờ vào tư thế xuất chiêu
THOIGIANCHANTUDICHUYENTRUOCXUATCHIEU = 0.25
# Trong lúc xuất chiêu / khựng chỉ gửi chiêu nhắm mục tiêu khi mục tiêu trong chừng này ô (ngoài tầm thì game tự chạy lại gần)
KHOANGCACHCHIEUKHIXUATCHIEU = KHOANGCACHSUDUNGKYNANGCANCHIEN
# Đang chế đồ (vận khí): kiểm tra ô cuối hành trang 1 mỗi chừng này giây, có vật phẩm thì chuyển sang hành trang khác ngay
CHUKYGIUOTRONGHANHTRANG = 0.03
# Kỹ năng cần đứng lại khi ra đòn: chờ tối đa chừng này giây để nhân vật vào tư thế xuất chiêu rồi mới ngắt di chuyển
THOIGIANCHONGATDICHUYENXUATCHIEU = 1.

SOLANGUITOIDASPAMKYNANG = 3
SOGIAYDEMSPAMKYNANG = 1.5
THOIGIANKHOASPAMKYNANG = 3.
# Trấn Cổ Thần Uy (Đào Hoa Nguyên) đứng im thì game hay báo sẵn sàng mà không ra chiêu, đang di chuyển thì ra ngay
# => chỉ dùng khi đang di chuyển; đứng im mà cần dùng thì nhích trước
# (đứng trùng ô quái: ra 1 ô bên cạnh, cạnh quái: xuyên qua sang ô đối diện), mỗi lần nhích cách nhau THOIGIANGIUAHAILANNHICH giây
THOIGIANGIUAHAILANNHICH = 1.
VITRIKYNANGCANNHICHDAOHOANGUYENs = (VITRIKYNANG_TRANCOTHANUY,)
# Kỹ năng không áp chống spam (gửi dồn bao nhiêu cũng được): Đại Hải Vô Lượng bấm tay liên tục vẫn ra chiêu bình thường,
# chặn spam chỉ làm nó nghỉ 3s vô ích. Các chiêu đánh Đào Hoa Nguyên: server nhận chiêu kế lúc sẵn sàng (lệch ngẫu nhiên
# 0.5-1.7s sau chiêu trước, đo 2026-10-28) nên nối chiêu phải gửi lại tới khi được nhận, khoá 3s làm đứt chuỗi
# Tâm pháp bật / tắt (Nguyên Khí Quy Nguyên, Dã Tính Cuồng Lực): gửi 1 lần rồi chờ chừng này giây cho hiệu ứng hiện mới gửi lại
THOIGIANCHOTAMPHAPBATTAT = 3.
IDKYNANGKHONGCHANSPAMs = (
    VITRIKYNANG_DAIHAIVOLUONG, VITRIKYNANG_THONKINH, VITRIKYNANG_PHONGMAQUYET, VITRIKYNANG_KHONGTHUNHAPBACHNHAN,
    VITRIKYNANG_DAOHOALACANH, VITRIKYNANG_METUNGQUYEN, VITRIKYNANG_BADONGQUYEN, VITRIKYNANG_NHATQUYENBATSON, VITRIKYNANG_LACKICH,
)

# Nhân vật trong tổ đội tự động (cùng hay khác nhóm, trừ khi đang theo sau trưởng nhóm) có ID nhỏ hơn được giữ vùng: nhân vật ID lớn hơn tránh mọi quái
# và điểm lộ trình trong bán kính này quanh nó
BANKINHVUNGNHUONGQUAIDONGDOI = 15.
# Gom quái: đủ số tối thiểu rồi mà còn quái chưa kéo cách đám đang gom (con neo) không quá bấy nhiêu mét thì kéo nốt rồi mới đánh
BANKINHKEOTHEMGOMQUAI = 8.

# Chỗ đứng NPC trên từng bản đồ (khi chưa thấy NPC thì chạy tới đây)
VITRITANTHUTIENCO_MAP = {
    BANDO_TANTHUTHON: (148, 145),
    BANDO_CHUQUOC: (X_TANTHUTIENCO_CHU, Y_TANTHUTIENCO_CHU),
    BANDO_THUCSON: (X_TANTHUTIENCO_THUCSON, Y_TANTHUTIENCO_THUCSON),
}
VITRICHUDICHTRAM_MAP = {
    BANDO_TANTHUTHON: (148, 149),
    BANDO_CHUQUOC: (330, 122),
}
# Tên NPC Chủ Dịch Trạm trên từng bản đồ (ở Chu là Trường Hoằng)
TENCHUDICHTRAM_MAP = {
    BANDO_TANTHUTHON: CHUDICHTRAM,
    BANDO_CHUQUOC: "Trường Hoằng",
}

# Bản đồ phù tới được qua Chủ Dịch Trạm => điểm đến trong câu lệnh "goto.! <điểm đến>"
DIEMDENCHUDICHTRAM_MAP = {
    BANDO_TEQUOC: laytenbandogame(BANDO_TEQUOC),
    BANDO_HANQUOC: laytenbandogame(BANDO_HANQUOC),
    BANDO_TRIEUQUOC: laytenbandogame(BANDO_TRIEUQUOC),
    # Menu / dữ liệu game viết "Nguỵ" (dấu kiểu cũ), gửi "Ngụy" thì Dịch Trạm không nhận
    BANDO_NGUYQUOC: "Nguỵ Quốc",
    BANDO_TANQUOC: laytenbandogame(BANDO_TANQUOC),
    BANDO_SOQUOC: laytenbandogame(BANDO_SOQUOC),
    BANDO_YENQUOC: laytenbandogame(BANDO_YENQUOC),
    BANDO_CHUQUOC: laytenbandogame(BANDO_CHUQUOC),
    # Môn phái: tên điểm đến như trong menu Chủ Dịch Trạm ở Tân Thủ Thôn (đọc trong bộ nhớ game 2026-10-27)
    BANDO_THUCSON: "Thục Sơn",
    BANDO_DAOHOANGUYEN: "Đào Hoa Nguyên",
    BANDO_DUONGMON: "Đường Môn",
    BANDO_VANMONGCOC: "Vân Mộng Cốc",
    BANDO_CONLUAN: "Côn Luân",
    BANDO_MAOSON: "Mao Sơn",
}

# Tới bản đồ đích không chỉ chạy bộ: từ Tân Thủ Thôn / Chu phù qua Tân Thủ Tiên Cô hoặc Chủ Dịch Trạm tới bản đồ gần đích nhất rồi chạy bộ tiếp
_phuongandichuyen_cache = {}


def layphuongandichuyen(idbando):
    # -> (tên NPC, bước: list lệnh welcome (Tân Thủ Tiên Cô) hoặc điểm đến "goto.!" (Chủ Dịch Trạm), id bản đồ phù tới, số cổng chạy bộ tiếp)
    # của cách phù tới idbando ít cổng chạy bộ nhất (phù thẳng tới = 0 cổng; cổng client tự tìm đường được), vd. Yên Trường Thành 1: Chủ
    # Dịch Trạm tới Yên Quốc rồi chạy 1 cổng; Tề Quốc: Chủ Dịch Trạm thẳng tới. Không giới hạn số cổng chạy tiếp (Thiên Môn Trận 1: phù Tề
    # Quốc rồi chạy 6 cổng vẫn hơn chạy bộ 15 cổng từ Sở Quốc), nơi gọi tự so với chạy bộ. Không phù tới được thì None
    # Về Tân Thủ Thôn thì dùng Hồi Thành Phù, không phù tới bản đồ khác rồi chạy về
    if idbando == BANDO_TANTHUTHON:
        return None
    if idbando not in _phuongandichuyen_cache:
        tot = None
        for tennpc, buoc_map in ((TANTHUTIENCO, DICHUYENTANTHUTIENCO_MAP), (CHUDICHTRAM, DIEMDENCHUDICHTRAM_MAP)):
            for idphutoi, buoc in buoc_map.items():
                solan = 0 if idphutoi == idbando else get_solanchuyenbando(idphutoi, idbando, is_chicongclienttudi = True)
                if solan is not None and (not tot or solan < tot[3]):
                    tot = (tennpc, buoc, idphutoi, solan)
        _phuongandichuyen_cache[idbando] = tot
    return _phuongandichuyen_cache[idbando]


# Đường người dùng chỉ là nhanh nhất (đếm cổng không ra): (bản đồ đích, vùng đích (x, y) -> bool, bản đồ phù Tân Thủ Tiên Cô tới).
# Cấm Vệ Quân (phía tây Chu Quốc, Thân Binh (165, 79)): Tân Thủ Tiên Cô phù Thủ Dương Sơn (81) rồi chạy 1 cổng vào Chu (ra ở (46, 144)),
# không chạy bộ từ môn phái khác qua Triều Dương Phong, không phù Dịch Trạm tới Chu (ra ở tận phía đông (330, 122))
DUONGUUTIENs = (
    (BANDO_CHUQUOC, lambda x, y: x < 200, 81),
)


def layduonguutien(idbandodich, toadodich):
    # -> phương án dạng layphuongandichuyen (Tân Thủ Tiên Cô, bước, bản đồ phù tới, số cổng chạy tiếp) hoặc None
    if not toadodich:
        return None
    for idbando, is_trongvung, idphutoi in DUONGUUTIENs:
        if idbando == idbandodich and is_trongvung(*toadodich) and idphutoi in DICHUYENTANTHUTIENCO_MAP:
            return TANTHUTIENCO, DICHUYENTANTHUTIENCO_MAP[idphutoi], idphutoi, 1
    return None


def laynpcphu(loainpc, idbando):
    # Loại NPC phù (TANTHUTIENCO / CHUDICHTRAM) -> (tên NPC trên bản đồ idbando, chỗ đứng của NPC hoặc None)
    if loainpc == TANTHUTIENCO:
        return TANTHUTIENCO, VITRITANTHUTIENCO_MAP.get(idbando)
    return TENCHUDICHTRAM_MAP.get(idbando, CHUDICHTRAM), VITRICHUDICHTRAM_MAP.get(idbando)


# Trưởng nhóm phải ở yên bản đồ mới bấy nhiêu giây mới phù theo (tránh chạy theo khi trưởng nhóm chỉ đi ngang qua)
THOIGIANCHOBANDOTHEOSAUONDINH = 5.
# Sang bản đồ bằng nói chuyện NPC (bando_xq.LOIDINPC_MAP): đứng cách NPC tối đa chừng này ô mới nói chuyện, chờ menu hiện tối đa
# THOIGIANCHOMENULOIDINPC giây, chọn rồi quá THOIGIANTHULAILOIDINPC giây vẫn chưa sang (NPC không cho qua, vận khí bị ngắt) thì nói chuyện lại
KHOANGCACHNOICHUYENLOIDINPC = 4.
THOIGIANCHOMENULOIDINPC = 3.
THOIGIANTHULAILOIDINPC = 15.

IDLOAIVUKHI_TAYKHONG = 60
IDLOAIVUKHI_DAO = 61
IDLOAIVUKHI_KIEM = 62
IDLOAIVUKHI_THUONG = 63
IDLOAIVUKHI_CON = 64
IDLOAIVUKHI_AMKHI = 69

YEUCAUDICHUYEN_NONE = 0
YEUCAUDICHUYENNHATDO = 1
YEUCAUDICHUYENTANCONG = 2
YEUCAUDICHUYENDICHUYENTUDO = 3
YEUCAUDICHUYENTHEOSAU = 4
YEUCAUDICHUYENGOMQUAI = 5
YEUCAUDICHUYENGIUKHOANGCACH = 6
YEUCAUDICHUYENTIMMUCTIEUCHUNG = 7

# Hết mục tiêu quanh mình thì đi tới mục tiêu nhân vật khác cùng máy đang thấy (tầm nhìn chung): chỉ xét mục tiêu cách mình tối đa
# KHOANGCACHTIMMUCTIEUCHUNGTOIDA ô, tìm đường tới cách nó KHOANGCACHDUNGTIMMUCTIEUCHUNG ô (đủ gần để tự thấy rồi chọn như thường).
# Đi tới 1 mục tiêu quá THOIGIANTOIDATIMMUCTIEUCHUNG giây mà vẫn chưa thấy nó thì bỏ qua nó THOIGIANBOQUAMUCTIEUCHUNG giây
KHOANGCACHTIMMUCTIEUCHUNGTOIDA = 40.
KHOANGCACHDUNGTIMMUCTIEUCHUNG = 5.
THOIGIANTOIDATIMMUCTIEUCHUNG = 15.
THOIGIANBOQUAMUCTIEUCHUNG = 60.

# Đứng đánh mà đòn không trúng (bị chắn tầm nhìn, quái lỗi, server từ chối...): từ chiêu đầu tiên gửi vào mục tiêu (tính lại mỗi lần
# thấy số bay mất máu mới trên nó) đã quá THOIGIANKHONGTRUNGCHIEUTOIDA giây và gửi ít nhất SOCHIEUKHONGTRUNGTOIDA chiêu mà vẫn
# không có số bay mới thì bỏ qua quái đó THOIGIANBOQUAMUCTIEUKHONGTRUNG giây (không áp cho mục tiêu PK: có thể đang bất tử)
THOIGIANKHONGTRUNGCHIEUTOIDA = 8.
SOCHIEUKHONGTRUNGTOIDA = 3
THOIGIANBOQUAMUCTIEUKHONGTRUNG = 60.

# Giữ khoảng cách với đối tượng đang tấn công mình (tùy chọn trên giao diện, hay bật cho Mao Sơn / Vân Mộng Cốc khi giao tranh)
KHOANGCACHGIUKETANCONG = 6.
# Đối tượng ra đòn quay mặt về mình thì coi là đang tấn công mình trong chừng này giây (tư thế ra đòn nhấp nháy giữa các đòn)
THOIGIANNHOKETANCONG = 2.
# Tính lại điểm lùi giữ khoảng cách mỗi chừng này giây (quét đối tượng xung quanh)
THOIGIANTINHGIUKHOANGCACH = 0.15
# Lùi theo một hướng mà chừng này giây chưa nhích được 0.5 ô thì coi là kẹt tường, chặn hướng đó THOIGIANCHANHUONGLUI giây
THOIGIANKETLUIGIUKHOANGCACH = 0.7
THOIGIANCHANHUONGLUI = 3.
# Giữ khoảng cách chỉ lùi khi "rảnh": mọi kỹ năng quan trọng của phái đang hồi chiêu hoặc không có mục tiêu thích hợp.
# Còn kỹ năng quan trọng dùng được thì đứng lại dùng. Phái không có trong danh sách: luôn lùi khi kẻ tấn công lại gần
KYNANGQUANTRONGGIUKHOANGCACH_MAP = {
    "maoson": (VITRIKYNANG_THUCCOT, VITRIKYNANG_THUCGIAP, VITRIKYNANG_THUCTAM),
    "vanmongcoc": (VITRIKYNANG_PHONGANTHUAT, VITRIKYNANG_HUYENQUANGTHIEMANH, VITRIKYNANG_TOANPHONGQUYET, VITRIKYNANG_CAITUHOANSINH,
                   VITRIKYNANG_TAYTRANQUYET, VITRIKYNANG_CAMLOTRI, VITRIKYNANG_KHIETVANQUYET),
    # Thục Sơn Kiếm / Thục Sơn Đao cùng tên môn phái "thucson", tách khoá theo _is_thucsondao (xem _laykhoakynangquantrong)
    "thucsonkiem": (VITRIKYNANG_TINHTAMQUYET, VITRIKYNANG_TIENKHI, VITRIKYNANG_TIENTHANVODICH, VITRIKYNANG_LANGKHONGCHIHUYET,
                    VITRIKYNANG_VANKIEMXUYENTAM, VITRIKYNANG_BANGTAMTHUC, VITRIKYNANG_NGUKIEMPHITIEN, VITRIKYNANG_NGUKIEMTHUAT),
}
# Tầm nhìn chung giữa các nhân vật cùng máy (qua shared_data): mỗi cửa sổ ghi đối tượng thù địch nó thấy (tối đa SOLUONGTAMNHINTOIDA,
# gần nhất trước); tầm nhìn cũ hơn THOIGIANHIEULUCTAMNHIN giây thì bỏ, đọc lại tầm nhìn của cửa sổ khác mỗi THOIGIANDOCTAMNHIN giây
SOLUONGTAMNHINTOIDA = 40
# Tập hỏa: mục tiêu người theo sau (cùng máy) công bố cũ hơn chừng này giây thì không theo nữa, chọn mục tiêu như cũ
THOIGIANHIEULUCTAPHOA = 1.
THOIGIANHIEULUCTAMNHIN = 1.
THOIGIANDOCTAMNHIN = 0.3
# Giữ chỗ chiêu lên 1 mục tiêu giữa các bot cùng máy (GiuKyNangMucTieu), theo phái: ô kỹ năng -> khoá hiệu ứng.
# Bot khác vừa gửi cùng chiêu lên mục tiêu đó (hiệu ứng chưa kịp hiện) thì dùng chiêu tiếp theo, không gửi trùng
HIEUUNGGIUCHOKYNANG_MAP = {
    "vanmongcoc": {VITRIKYNANG_PHONGANTHUAT: HIEUUNGKYNANG_TRAMMAC, VITRIKYNANG_HUYENQUANGTHIEMANH: HIEUUNGKYNANG_MULOA, VITRIKYNANG_CAITUHOANSINH: "caituhoansinh"},
    "maoson": {VITRIKYNANG_THUCCOT: HIEUUNGKYNANG_THUCCOT, VITRIKYNANG_THUCGIAP: HIEUUNGKYNANG_THUCGIAP, VITRIKYNANG_THUCTAM: HIEUUNGKYNANG_THUCTAM},
    "thucsonkiem": {VITRIKYNANG_LANGKHONGCHIHUYET: HIEUUNGKYNANG_CHOANG},
}
# Kết quả xét kỹ năng quan trọng (tính trong danh sách kỹ năng của phái) cũ hơn chừng này giây thì coi như rảnh
THOIGIANHIEULUCKYNANGQUANTRONG = 0.5
YEUCAUDICHUYENKHAIKHOANG = 100
YEUCAUDICHUYENDAOTANGBAODO = 200

KIEUDICHUYEN_GIUKHOANGCACHTOIDA = 1
KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU = 2
KIEUDICHUYEN_TOADOCHUAN = 3

# Chỉ là mặc định khi chưa có file _internal/todoi.json; cấu hình thật ở giao diện (tab Chiến đấu > Tổ đội tự động)
NHANVATTODOITUDONGs_LIST = [
    [29, 30, 32, 31],
    [132, 133, 134, 135]
]

TENMUCTIEUKHONGTANCONGs = (*BAOTHUVATPHAMs, "Tần QuốcBinh Sĩ", "Triệu QuốcBinh Sĩ", QUYTOT, THIENBINH, DAUBINH, "CAVE1", "CAVE.2", 'Đỗ Độc', 'Ôn Thần', "Liễu Vọng Tháp")
TENNGUOICHOICUNGBANGs = tuple()
TENBOSSBUFFMAOSONs = ("Mã Quỷ", "Lương Hưng", "Yến Thập Tam", "Tư Tà", "Thủ Lĩnh Thành Kiều", TROMBAOPHITAC, "Bảo Hộp Phi Tặc",
                      "Tướng Quân Dũng", "Lăng Mộ Tà Linh", "Đường Truy", "Thế Công Minh", "Thạch Tướng Quân", "Cơ Quan Tướng Quân",
                      "Hào Quật")
