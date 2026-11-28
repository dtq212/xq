from collections import defaultdict
from math import sqrt
import re
import unicodedata

from bando_xq import laytenbandogame, layidbandotheoten, get_solanchuyenbando, BANDOCONG_MAP, SOLANCHUYENBANDOTOIDA, CAPQUAI_DAGAP_MAP, _laycapquaidahoc

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
# Aegis (2026-11-25, acc 364): túi đồ ghi đúng tên cửa hàng "Thức Ăn Bảo Thú Cao Cấp", không phải tên cũ ở trên => tìm / đếm theo cả hai
# (trước đây mua bù đếm ra 0 nên cứ 10s mua thêm 1 chồng, cho bảo thú ăn cũng không thấy món)
THUCANBAOTHUCAOCAP = "Thức Ăn Bảo Thú Cao Cấp"
CAOCAPBAOTHUTHUCPHAMs = (CAOCAPBAOTHUTHUCPHAM, THUCANBAOTHUCAOCAP)
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
# Bản Niết Bàn: con Chuột tên "12 con Giáp - Chuột" (vật phẩm và đối tượng cùng tên), mô tả không ghi chỉ số cộng cho chủ
CONGIAPCHUOT = "12 con Giáp - Chuột"
# Bảo thú vật phẩm thưởng code tân thủ (vật phẩm / con bảo thú game viết "Thuỷ" hoặc "Thủy")
THUYBINHs = ("Thuỷ Bình", "Thủy Bình")
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
# Hồi môn phái: miễn phí, chưa vào môn phái thì về Tân Thủ Thôn (acc ít tiền thay Hồi Thành Phù)
LENHHOIMONPHAI = "dGludmF0 1"
# Niết Bàn không có tinvat 1 / 2: kỹ năng "Sử dụng tín vật" (thẻ Cơ Bản, id 61, đọc bảng kỹ năng 2026-11-02) về môn phái, đứng cạnh
# Xa Phu, nói chuyện "1. Chấp nhận" về Tân Thủ Thôn; quá THOIGIANXAPHUNIETBAN giây chưa về được thì thôi
LENHTINVAT_NIETBAN = "pf2 61"
# Kỹ năng "Chức năng hệ thống" (thẻ Cơ Bản > Hệ thống) = "pf2 908": máy chủ trả menu thiết lập, mỗi lựa chọn "pf2 908.<n>", bấm là bật /
# tắt qua lại, trạng thái lưu trên máy chủ nên chỉ biết qua nhãn (vd "7.Ẩn hiệu ứng Kĩ năng" = đang hiện, lựa chọn là "pf2 908.14").
# Bot từng tự Ẩn hiệu ứng Kĩ năng mỗi lần vào game (2026-11-08); người dùng bảo bỏ 2026-11-14 vì bật hay tắt đều không thấy khác
LENHCHUCNANGHETHONG = "pf2 908"
# Tín Vật Niết Bàn ("pf2 61") giãn cách 60s (người dùng dặn 2026-11-03): gửi trong lúc hồi thì game không vận khí,
# đừng tưởng là không dùng được. Tính từ lúc vào vận khí, dư 2s. Aegis ("dGludmF0 ...") không hồi, không chờ (2026-11-05)
THOIGIANHOITINVAT = 62.

# Số thẻ Giang Hồ trong cửa sổ nhiệm vụ (số đầu của "quest intro / giveup <thẻ> <nhóm> <loại>"; Cốt Truyện là 2)
THENHIEMVUGIANGHO = 1


def is_lenhtinvat(caulenh):
    return bool(caulenh) and (caulenh == LENHTINVAT_NIETBAN or caulenh.startswith("dGludmF0 "))


TENXAPHU_NIETBANs = ("Xa Phu", "Thị Giả")
THOIGIANXAPHUNIETBAN = 90.
# Tân Thủ Tiên Cô lấy chừng này lượng mỗi lần phù từ cấp CAPTINHTIENPHUTANTHUTIENCO (người dùng 16/11 lúc đầu nói miễn phí rồi nói hình
# như có tính tiền: giữ kiểm tra; vẫn rẻ hơn hẳn Hồi Thành Phù 1.500 và Dịch Trạm)
GIAPHUTANTHUTIENCO = 500
# Đích cách chừng này cổng chạy bộ trở xuống thì chạy bộ luôn, không Hồi Thành Phù / Tín Vật về rồi phù lại (người dùng 16/11: Săn Tinh
# Anh từ Bà Dương Hồ sang Vu Sơn 1 cổng mà Hồi Thành Phù về Tân Thủ Thôn rồi phù). Về Tân Thủ Thôn vẫn không bao giờ chạy bộ
SOCONGCHAYBOLUON = 2
CAPTINHTIENPHUTANTHUTIENCO = 50
# Mua đồ luôn chừa lại bấy nhiêu ngân lượng (đủ Hồi Thành Phù về rồi phù đi)
NGANLUONGGIULAI = GIAHOITHANHPHU + GIAPHUTANTHUTIENCO
# Tối đa bấy nhiêu lần Hồi Thành Phù trong THOIGIANDEMHOITHANHPHU giây: quá thì coi như đang lặp, ngưng dùng (mỗi lần 1.500 lượng)
SOLANHOITHANHPHUTOIDA = 3
THOIGIANDEMHOITHANHPHU = 600.
# Không bao giờ để 2 nhân vật (các cửa sổ cùng máy) Hồi Thành Phù / Tín Vật / Hồi Môn Phái cùng lúc: rất lộ (người dùng dặn 2026-11-06).
# Bot dùng giữ chỗ chung (dieuphoi_xq.GiuHoiThanh) suốt lúc chờ + vận khí (tối đa THOIGIANKHOAVANKHITRIEUHOITOIDA), hết vận khí
# thì giữ thêm ngẫu nhiên trong khoảng này (giây) rồi bot khác mới được dùng. Người dùng dặn 2026-11-07: chỉ cần cách nhau 5s
# (6-15s cũ cộng vận khí làm 3-4 bot xếp hàng về thành rất chậm)
KHOANGNGHIHOITHANHGIUACACBOT = (0., 1.)
# Người dùng dặn 2026-11-14: tính khoảng cách từ lúc DÙNG phù, không chờ bot trước vận khí xong (giữ cả chờ + vận khí làm các bot
# xếp hàng rất chậm). Bot gửi lệnh thì giữ chỗ ngẫu nhiên trong khoảng này (giây) tính từ lúc gửi, hết là bot khác dùng được luôn
# dù bot trước còn đang vận khí. Lệnh không vào vận khí (nhân vật không biến mất) thì nhả sớm (GiuHoiThanh.ketthuc)
# Người dùng dặn 2026-11-27: 5-7s làm đội tập hợp chậm (5 bot thì bot cuối chờ 20-28s) => chỉ cách nhau 1-3s
KHOANGCACHHOITHANHGIUACACBOT = (1., 3.)
# Cũ: giữ chỗ phủ cả chờ vào vận khí + vận khí. Giờ chỉ còn dùng làm trần an toàn
THOIGIANGIUHOITHANHTOIDA = 25.
# Tên khoá vận khí (action_khoavankhitrieuhoi) là về thành: hết khoá thì nhả giữ chỗ GiuHoiThanh
TENKHOAVANKHIHOITHANHs = ("HỒI THÀNH PHÙ", "TÍN VẬT")

# Sắp xếp hành trang: thuốc dồn về cuối túi cuối cùng, trước nó là đồ có "[Có thể sử dụng]" trong mô tả. So theo đầu tên nên
# bản "... Luyện Chế" (và tên bị cắt ngắn) cũng tính
THUOCSAPXEPs = (NGANHANHTU, TUTAMDON, KHIMACHDON, TIEUDAOTAN, LONGTIENTHAO, THILUYENQUA, THILUYENDON, KIMTANGTAN,
                QUYNGUYENDON, KHUMATAN, THANHTAMDON)
# Đá không được "move" đè lên ô có món khác: game tưởng là muốn đập / tinh luyện đá vào đồ đó. Đá = loại ［Tinh luyện］ (Kim / Thổ /
# Ám Tinh Thạch...), tên có chữ trong DAKHONGDEDOs, hoặc tên có "Thạch" mà mô tả không ghi loại (cho chắc). Món có loại khác như
# Đại Huyết Thạch ［Có thể sử dụng］, Hồng Bảo Thạch Hạng Liên ［Hạng Liên］ thì không phải đá. Đổi chỗ thì chuyển món kia sang ô của đá
# Ngự Thạch (Thổ Ngự Thạch cấp 1...) cũng đập vào đồ như Linh Thạch dù mô tả ghi loại khác
DAKHONGDEDOs = ("Đoạn Thạch", "Linh Thạch", "Tinh Thạch", "Ngự Thạch")
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
# Vật phẩm người chơi hay dùng: sắp xếp hành trang luôn đặt đầu hành trang 1 theo đúng thứ tự này (người dùng 2026-11-22 thêm Cao Bộc Tạc Đạn)
DAUTUI1SAPXEPs = (THIENLYHUUTINH, CAOBOCTACDAN)
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
# Tầm thấy đối tượng: bảng đối tượng của client là Ô VUÔNG quanh mình (đo [ĐO TẦM NHÌN] 26/11/2026, 7 acc ~10 phút: đối tượng rời bảng ở
# max(|dx|, |dy|) 19-21 mọi acc, đường thẳng thì 22-27; vẫn giữ con lệch (22, 21) = 27.7 ô thẳng). Bot lọc max(|dx|, |dy|) <= chừng này
# (chừa 2-3 ô với mép thật ~20). Trước đây lọc hình tròn 18 => bỏ mất góc client vẫn thấy. Các so sánh get_khoangcach (đường thẳng) với
# hằng này ở chỗ khác vẫn giữ: chỉ chặt hơn ở góc
KHOANGCACHTOANMANHINH = 18.

KHOANGCACHHIEUQUAKYNANGLOIDONGCUUTHIEN = 3
# Kỹ năng vận khí: từ lúc gửi lệnh tới lúc game vào trạng thái vận khí thường 0.5-1.5s, có lúc tới ~1.6-2s
# (log: chờ 1.5s hết là Huyết Ma Chú chen vào ngắt vận khí triệu hồi) nên chờ dư
THOIGIANCHOVAOVANKHI = 2.5
# Chờ xác nhận vận khí (moitruong.action_chovankhi): lệnh nằm trong hàng đợi quá chừng này giây chưa gửi thì bỏ chờ
THOIGIANCHOGUILENHVANKHI = 1.5
# Gửi lệnh xong chừng này giây mà nhân vật không vào tư thế xuất chiêu 6 / 9, kỹ năng chưa vào hồi chiêu, thanh vận khí chưa có
# gói mới => chiêu không ra (máy chủ từ chối / lệnh hỏng), bỏ chờ ngay thay vì đứng đủ THOIGIANCHOVAOVANKHI
THOIGIANXACNHANRACHIEUVANKHI = 0.6
# Khoá vận khí triệu hồi bảo thú giữ tối đa chừng này (phòng đọc trạng thái vận khí sai mà khoá mãi)
THOIGIANKHOAVANKHITRIEUHOITOIDA = 15.
# Thanh vận khí quá thời lượng máy chủ báo chừng này giây mà vẫn "đang vận khí" => kẹt (vd đang Lôi Động Cửu Thiên thì dis: máy chủ không
# bao giờ gửi gói kết thúc, đăng nhập lại thanh vẫn đứng 100%), tự đóng thanh
THOIGIANVANKHIKETTHEM = 5.
# Đổi đồ khi triệu hồi: hết vận khí mà chừng này giây chưa thấy bảo thú triệu hồi mới (triệu hồi hỏng / bị ngắt) thì vẫn mặc lại
THOIGIANCHOBAOTHUSAUTRIEUHOI = 5.
# Lôi Động Cửu Thiên (Mao Sơn) vận khí 6s (phạm vi 7x7 ô quanh bản thân); Lôi Long Quyết (Côn Luân, 9x9 ô liên tục 6s) cùng cơ chế,
# dùng chung các hằng / cách ngắt vận khí này
THOIGIANVANKHILOIDONGCUUTHIEN = 6.
# Phong Vũ Kinh Thiên (Vân Mộng Cốc) gọi cuồng phong đánh mục tiêu liên tục 8s: trong khoảng này không dùng lại lên cùng mục tiêu
THOIGIANPHONGVUKINHTHIEN = 8.
# Mao Sơn: có cụm quái quanh mục tiêu mà mục tiêu xa hơn chừng này thì chạy vào (dừng cách ~1 ô) để ra Lôi Động Cửu Thiên trúng cả cụm
KHOANGCACHTIEPCANLOIDONGCUUTHIEN = 2.
# Chiêu vận khí diện rộng (Lôi Động Cửu Thiên / Lôi Long Quyết) chỉ dùng / chạy vào cụm khi có từ chừng này quái trở lên: ít hơn thì
# đánh chiêu đơn mục tiêu nhanh hơn là tiếp cận rồi đứng vận khí 6s (người dùng 2026-11-04)
SOLUONGQUAITOITHIEUCHIEUVANKHI = 5
# Riêng Lôi Động Cửu Thiên (Mao Sơn): từ 3 quái đã coi là đông, ra chiêu / chạy vào cụm (người dùng 2026-11-06);
# Lôi Long Quyết (Côn Luân) vẫn theo SOLUONGQUAITOITHIEUCHIEUVANKHI
SOLUONGQUAITOITHIEULOIDONGCUUTHIEN = 3

KHOANGCACHTOIDAHOPLE = 255.
# Tầm cận chiến thật (bot tự học, 01/11/2026): 1 ô theo max(|dx|, |dy|) => ô kề, tính cả ô chéo
KHOANGCACHSUDUNGKYNANGCANCHIEN = 1.
# Mục tiêu (người chơi giữ khoảng cách) trong chừng này ô thì lùi / dùng chiêu thoát (Ma Tâm Thuật...)
KHOANGCACHLUIGIUKHOANGCACH = 3.
# Đang theo sau: mình ra xa trưởng nhóm quá vùng đứng đánh chừng này ô (trưởng nhóm đang đi) thì chưa chọn mục tiêu, chạy về trước
DUKHOANGCACHTHEOSAUCHONMUCTIEU = 1.5
# Đang theo sau mà đánh nhau: vùng đứng đánh / tìm mục tiêu quanh người được theo sau rộng hơn khoảng cách theo sau chừng này ô
# (người dùng 2026-11-09: đánh xa 3 ô, cận chiến 6 ô vì phải chạy sát quái). Không có mục tiêu thì vẫn bám đúng khoảng cách theo sau.
# Cận chiến hay đánh xa xét theo tầm đánh của chiêu tiếp cận gần nhất (_khoangcachvoitoimuctieu), xem _tinhtoannoikhoangcachdanhtheosau.
# Phải cộng đồng bộ ở: bán kính chỗ đứng đánh (_tinhtoanbankinhdungtancongtheosau → tầm tìm mục tiêu, cắt chỗ đứng, điểm lùi),
# ngưỡng kéo về khi đang có mục tiêu (action_tudongtheosau) và ngưỡng chặn chọn mục tiêu (tactu_muctieu), nếu không sẽ chọn
# quái không với tới hoặc chạy ra đánh rồi bị kéo về liên tục
NOIKHOANGCACHDANHTHEOSAU = 3.
NOIKHOANGCACHDANHTHEOSAUCANCHIEN = 6.
# Vừa hết mục tiêu (quái chết, đổi mục tiêu) vẫn giữ ngưỡng kéo về rộng như lúc có mục tiêu chừng này giây: trước đây mất mục tiêu
# 1 nhịp là ngưỡng tụt từ 9.5 xuống 3.5 ô => quay đầu chạy về trưởng nhóm, 0.1-0.3s sau chọn con mới lại quay ra (log 342/347
# Hải Tân 2026-11-22: 466 / 265 lần "THEO SAU" chen giữa 11 phút đánh)
THOIGIANGIUVUNGDANHSAUMUCTIEU = 2.
KHOANGCACHSUDUNGKYNANGTAMXA = 8.  # 9., 12.
# Tầm xa 8 ô đã là con số trừ hao lệch tọa độ client - server (tầm thật ~12 ô), nên không trừ thêm nhiều nữa:
# - lọc mục tiêu quanh người theo sau dùng tầm xa - TRUHAOTAMXACHONMUCTIEU (dùng trọn 8 ô)
# - đứng đánh lâu / đang chạy bù thì tầm yêu cầu giảm BUKHOANGCACHTAMXA ô (đánh ở ~7 ô), chạy vào tầm thì dừng ở tầm xa - BU - 1 (~6 ô)
TRUHAOTAMXACHONMUCTIEU = 0.
BUKHOANGCACHTAMXA = 1.
# Tầm xa tự học (TacTu._capnhattamxa): ô tầm xa trên giao diện là tầm TỐI ĐA (tầm thật ~12), bot dùng tầm hiện tại. Chiêu nhắm mục tiêu
# gửi từ khoảng cách >= TAMXATOITHIEU - VUNGMEPTAMXA: vào hồi chiêu / tư thế xuất chiêu trong THOIGIANCHOCHIEUNHAN giây là "ra", không
# thì "không ra" (lệch toạ độ client - server, máy chủ thấy xa hơn). Đếm theo khoảng cách lúc gửi làm tròn xuống (ô d = [d, d+1));
# tầm hiện tại = mép trên của ô xa nhất mà mọi ô từ TAMXATOITHIEU tới đó có tỉ lệ ra >= NGUONGTILERATAMXA (ô chưa đủ SOMAUTOITHIEUTAMXA
# lần gửi coi như đạt => tự thử xa hơn). Số đếm mỗi ô giữ tối đa SOMAUTOIDATAMXA và giảm một nửa sau mỗi BANRATAMXA giây nhưng không
# xuống dưới SOMAUTOITHIEUTAMXA (ô đã biết hay trượt không bị coi là chưa đủ mẫu rồi nhảy tầm lên tối đa).
# Thống kê 2026-11-01 (187, tầm tối đa 12, ~1 giờ, ra/gửi): 7 ô 95%, 8 ô 96%, 9 ô 79%, 10 ô 56%, 11 ô 40% (bản co / nới cũ giữ tầm TB
# 10.7 nên hụt gần nửa số chiêu). 85%: hụt 1 chiêu mất ~0.5s, đắt hơn chạy thêm 1 ô (~0.25s).
# Đo spam tới khi nhận (187, ~5000 chuỗi): lần gửi đầu -> cuối trung vị 0.12s, 90% 0.25s => chiêu ra thấy trong ~0.4s
THOIGIANCHOCHIEUNHAN = 0.5
# Chế độ đứng yên (TacTu._chontamxa): mình không di chuyển >= THOIGIANDUNGYENTAMXA giây và mục tiêu không di chuyển thì toạ độ client
# khớp server, dùng bảng học riêng (chưa có mẫu => thử tới tầm tối đa). Trượt thì nhích vào NHICHTAMXA ô với mục tiêu đó; đang nhích /
# tiếp cận thì giữ chế độ đứng yên THOIGIANNHICHTAMXA giây; tiếp cận chỉ vào trong tầm VUNGTIEPCANTAMXADUNGYEN ô rồi bắn
THOIGIANDUNGYENTAMXA = 0.3
NHICHTAMXA = 1.
THOIGIANNHICHTAMXA = 1.
VUNGTIEPCANTAMXADUNGYEN = 0.5
# Chiêu tầm xa trượt: làm mới toạ độ bằng lệnh danh hiệu (TacTu.action_lammoitrangthai), chờ THOIGIANCHOLAMMOITOADO giây mới bắn lại.
# Làm mới tốn tài nguyên game (tính lại nhiều thứ), lệch pha cũng hiếm, nên cách lần trước tối thiểu THOIGIANGIANCACHLAMMOITOADO giây.
# Log độ lệch toạ độ client đo được trong THOIGIANDOLECHLAMMOI giây sau khi gửi
THOIGIANCHOLAMMOITOADO = 0.3
THOIGIANGIANCACHLAMMOITOADO = 5.
# Đào Hoa Nguyên (cận chiến): client thấy mục tiêu cách 1 sải (người dùng 25/11: 3-4 ô, tính rộng tới 5) mà mình đang tư thế tấn
# công (không phải Ba Động / Đại Hải / Lạc Ảnh vừa nhận) => toạ độ client lệch máy chủ, làm mới toạ độ. Giữ đủ THOIGIANGIULECHCANCHIEN
# giây mới gửi (khỏi bắt nhầm khung mục tiêu vừa bước đi), giãn cách chung THOIGIANGIANCACHLAMMOITOADO
KHOANGCACHLECHCANCHIENTOITHIEU = 3.
KHOANGCACHLECHCANCHIENTOIDA = 5.
THOIGIANGIULECHCANCHIEN = 0.2
THOIGIANBOQUACHIEUXADAOHOA = 1.5
THOIGIANDOLECHLAMMOI = 1.5
# Sau lệnh làm mới, bảng đối tượng client chập chờn (mục tiêu bị coi là không hợp lệ ~0.1-0.4s, đo log 2026-11-09): trong
# THOIGIANGIUMUCTIEUSAULAMMOI giây giữ nguyên mục tiêu theo ID, không chọn lại
THOIGIANGIUMUCTIEUSAULAMMOI = 1.
VUNGMEPTAMXA = 2.
TAMXATOITHIEU = 8.
NGUONGTILERATAMXA = 0.85
SOMAUTOITHIEUTAMXA = 8
SOMAUTOIDATAMXA = 40
BANRATAMXA = 600.
THOIGIANLOGTHONGKETAMXA = 120.
# Thống kê khởi đầu {ô: tỉ lệ ra} (số đo trên, tính như 10 lần gửi mỗi ô, phai dần như số liệu thật): khỏi học lại từ đầu mỗi lần chạy.
# Đổi tầm tối đa ở giao diện thì bỏ hết (cả số này), học lại từ đầu
# Đo theo khoảng cách tầm đánh max(|dx|, |dy|) (log [TẦM XA CHI TIẾT] 01/11/2026, 303 phát); số cũ đo theo đường thẳng:
# {7: 0.95, 8: 0.96, 9: 0.79, 10: 0.56, 11: 0.40}
TILERATAMXAMACDINH = {6: 0.91, 7: 0.96, 8: 0.89, 9: 0.27, 10: 0.14}
# Tiếp cận cận chiến như client khi bấm chiêu trên phím tắt (xq + 0x1873A, đọc 2026-10-28): tìm đường tới ô mục tiêu, mỗi lần chỉ
# ghi chừng này bước (client: KDK + 0x1620 = 2), đích đổi thì chừng này giây sau lần ghi trước mới tìm lại (client: mốc +500ms)
SOBUOCTIEPCANCANCHIEN = 2
# Đối tượng tìm đường cục bộ riêng của bot (xq + 0x4B0D60 dùng tới + 0x54FD0: lưới 101x101, 0x2800 nút, mảng ô đường đi)
KICHTHUOCDOITUONGTIMDUONGCUCBO = 0x56000
# Đích rơi vào vật cản (toạ độ nhiệm vụ / NPC lệch vào tường, nước...) thì kéo về ô đi được gần nhất trong bán kính chừng này ô
BANKINHKEODICH = 15
# Đoạn tìm đường cục bộ ra đoạn cụt (không tới được đích) thì chừng này giây sau mới thử lại đúng đoạn đó
THOIGIANNHODOANCUT = 1.
# Vừa đổi bản đồ thì chừng này giây coi toạ độ chưa ổn định (moitruong.get_is_toadochuaondinh): không lập bước đi tới bản đồ khác,
# không quyết định di chuyển, cửa sổ khác cùng máy vẫn thấy bản đồ / toạ độ cũ. Game đổi mã bản đồ trước, toạ độ sau (2026-11-08 17:52:
# ra Phong Yêu Kính về Chu (292,185) mà 0,2s sau vẫn báo (94,137) của PYK, acc gà chạy theo toạ độ đó ra ngoài thành rồi quay lại).
# Người dùng dặn: chậm 1-1,5s sau đổi bản đồ không sao, đổi lại khỏi dùng dữ liệu cũ
THOIGIANCHOSAUDOIBANDO = 1.5
# ... và toạ độ còn y như ở bản đồ cũ thì chờ tiếp, tối đa chừng này giây
THOIGIANCHOTOADOSAUDOIBANDO = 5.
# Giữ khoảng cách tối thiểu mà sau lưng là vật cản: thử lùi lệch khỏi hướng thẳng chừng này độ (cả 2 bên, lệch ít trước), lệch hướng
# thì quãng lùi được dài thêm tối đa chừng này ô cho đủ xa mục tiêu
# Đi theo ô tới gần đích (NPC...) còn trong chừng này ô thì chọn ô trong tầm mà tìm đường cục bộ tới được thật (thử tối đa SOOTHU ô
# gần mình trước, nhớ kết quả THOIGIANNHO giây) thay vì điểm trên đường thẳng (hay ở sau tường thấp / quầy hàng)
KHOANGCACHCHONDICHTOIDUOC = 40.
SOOTHUDICHTOIDUOC = 8
THOIGIANNHODICHTOIDUOC = 3.
GOCLECHLUIs =(0, 25, 50, 75, 100, 125)
QUANGLUITHEMTOIDA = 3.
# Tầm xa (Đường Môn) bị vật cản chắn đường bắn: tìm ô đứng bắn được (đường thẳng tới mục tiêu thông, trong tầm) quanh mình trong
# BANKINHTIMDIEMBAN ô thay vì chạy lại gần. Chi phí = quãng đi + HESOPHATGANMUCTIEU x số ô gần mục tiêu hơn bây giờ (máu yếu, không
# lao vào); ô cách mục tiêu dưới KHOANGCACHDIEMBANTOITHIEU ô chỉ dùng khi không còn ô nào khác. Đường đi tới ô đó không được vòng
# quá HESODUONGVONGDIEMBAN x đường thẳng + 4 bước, không được lại gần mục tiêu quá 1 ô so với điểm đầu / điểm cuối.
# Ô đã chọn giữ nguyên tới khi hết thông / ra ngoài tầm (không nhảy qua lại); không ra ô nào thì THOIGIANTINHLAIDIEMBAN giây mới tính lại
BANKINHTIMDIEMBAN = 10
HESOPHATGANMUCTIEU = 3.
KHOANGCACHDIEMBANTOITHIEU = 4.
HESODUONGVONGDIEMBAN = 2.
THOIGIANTINHLAIDIEMBAN = 0.5
# Bot tìm đường lại và ghi đoạn mới mỗi chừng này giây kể cả khi đích không đổi (client 0.5s; ngắn hơn để chuỗi không cạn giữa đường)
THOIGIANTINHLAITIEPCANCANCHIEN = 0.25
# Mục tiêu đang đi về phía mình, bước tới của nó cách mình không quá chừng này ô (theo ô, max |dx| |dy|) thì đứng chờ
KHOANGCACHCHOMUCTIEUTOI = 2
# Quái đi chậm (đo 2026-11-02: quái ~0.41s/ô, người ~0.25s/ô, bảo thú ~0.3s/ô): chờ nó tới lâu hơn mình đi tới => chỉ đứng khi đã kề
KHOANGCACHCHOQUAITOI = 1
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
# Khai Thiên Tịch Địa góc xấu: xét chỗ đứng trong chừng này ô quanh mình, chỗ nào trúng thêm từ SOMUCTIEUTANGDOICHOKHAITHIEN mục tiêu
# thì đi tới đó rồi mới ra chiêu; chỗ đã chốt giữ tối đa THOIGIANGIUCHODOIKHAITHIEN giây (không tới được thì thôi, ra chiêu tại chỗ)
QUANGDOICHOKHAITHIEN = 3
SOMUCTIEUTANGDOICHOKHAITHIEN = 2
THOIGIANGIUCHODOIKHAITHIEN = 2.5
# Sau Khai Thiên rộng giữ mục tiêu cũ tối đa bấy nhiêu giây chờ Lưu Tinh Truy Mạng lướt về (log: Lưu Tinh nối sau ~0.6-0.9s)
THOIGIANKHOAMUCTIEULUUTINH = 3.
# Đo hiệu quả Khai Thiên Tịch Địa: đọc lại máu quái bấy nhiêu giây sau khi game nhận chiêu (lướt xong + số bay)
THOIGIANDOKHAITHIEN = 1.2
KHOANGCACHNHATDO = KHOANGCACHTOANMANHINH
# Vừa mất mục tiêu chưa quá bấy nhiêu giây thì chưa đi nhặt đồ, chờ chọn con kế (món trong tầm nhặt tại chỗ vẫn nhặt luôn, món Nhặt ưu
# tiên / đồ sư môn không phải chờ): tránh vừa giết xong con này đã chạy đi nhặt rồi lại quay về đánh con kế
THOIGIANCHOMUCTIEUKETRUOCKHINHATDO = 2.
# Tầm gửi "get x y" nhặt tại chỗ (không đi tới), theo ô vuông max(|dx|, |dy|). Trước đây ≤3 ô đường thẳng: log 342 26/11 boss Phong Yêu
# Kính rơi Tịch Tà Kiếm, đứng cách 3~5 ô gửi "get" 4 lần trong 2s đều trượt (bot tưởng trong tầm nên đứng yên), bước tới cách 2 ô là
# nhặt được ngay cả món kế bên
KHOANGCACHNHATTAICHO = 2
# Vừa mất mục tiêu (đang chờ chọn con kế) mà món cách không quá bấy nhiêu ô (ô vuông) thì vẫn đi nhặt luôn: quãng ngắn, nhặt xong quay lại
# đánh không tốn bao nhiêu; món xa hơn mới chờ THOIGIANCHOMUCTIEUKETRUOCKHINHATDO
KHOANGCACHNHATDOGANKHIVUAMATMUCTIEU = 5
# Lượt kỹ năng không ra yêu cầu tấn công mà vẫn chọn đúng con vừa đánh, nó chưa chết: luồng di chuyển giữ yêu cầu cũ tối đa bấy nhiêu
# giây (không Đi dạo / Tìm mục tiêu chung chạy đi chỗ khác rồi quay lại đánh)
THOIGIANGIUYEUCAUTANCONG = 1.5
# Như trên nhưng mục tiêu còn trong tầm đánh xa (chỉ đang chờ chiêu hồi / chờ số bay): giữ tối đa bấy nhiêu giây
THOIGIANGIUYEUCAUTANCONGTRONGTAM = 8.
# Có món cần đi nhặt mà chờ (bận đánh) quá bấy nhiêu giây thì đi nhặt luôn dù còn mục tiêu: quái ra liên tục vẫn nhặt được
THOIGIANCHONHATDOTOIDA = 6.

# Mục tiêu mới nhìn thấy phải chờ ngần này giây mới được chọn tấn công; mất dấu quá THOIGIANMATDAUMUCTIEU thì thấy lại tính là mới
THOIGIANCHOCHONMUCTIEUMOI = 1.
THOIGIANMATDAUMUCTIEU = 3.
# Luồng tìm mục tiêu (lặp ~0.15s) thấy quái đánh được đang chờ THOIGIANCHOCHONMUCTIEUMOI trong ngần này giây gần đây thì không Đi dạo
THOIGIANGIUCHOMUCTIEUMOI = 0.5

# Thấy người chơi ẩn thân quanh mình khi đang di chuyển theo lộ trình điểm đánh thì ngưng mọi hoạt động trong khoảng thời gian này (giây)
THOIGIANTAMNGUNGANTHAN = 600.
# Ẩn thân của những tên này (ADMIN hay đi kiểm tra: "2D" bị phát hiện 14-17/11) thì ngưng cả khi không đi lộ trình điểm đánh,
# trừ lúc mình đang bật PK (màu PK khác Hoà bình). So sau khi bỏ dấu, bỏ khoảng trắng, chữ thường: "Chiến Quốc 2D" = "ChienQuoc2D".
# Khớp nguyên tên, "Sứ Giả 2D" không tính
TENANTHANLUONNGUNGs = ("2D", "ChienQuoc2D")
# Thấy người lạ (ngoài danh sách tổ đội) ở map train thì ngưng ngắn hơn (giây); mặc định của ô "Tạm ngưng (giây)" tab Khác
THOIGIANTAMNGUNGNGUOILA = 60.
# Chiến lược khi gặp người lạ ở map train (ô chọn tab Khác, theo từng nhân vật; người dùng 2026-11-26: thay ô bật/tắt tạm ngưng cũ).
# Chỉ áp dụng khi đang đi lộ trình điểm đánh như cũ; ẩn thân (ADMIN) thì luôn ngưng cả máy, không theo chiến lược này.
#   tatca: mình ngưng + công bố, mọi nhân vật cùng bản đồ (cùng máy / LAN) đang chọn tatca ngưng theo (cách cũ khi bật ô)
#   mot: chỉ nhân vật thấy ngưng, không công bố; file tạm ngưng đánh dấu riêng nên không chặn tự đăng nhập các acc khác
#   tranh: vẫn đánh, bỏ quái / điểm đánh trong BANKINHTRANHNGUOILA quanh chỗ người lạ đứng (nhớ THOIGIANNHONGUOILA sau khi khuất,
#          chia sẻ cho bot cùng bản đồ); người lạ cứ ở sát mình quá THOIGIANBAMTHEONGUOILA (bám theo) thì nhân vật này ngưng như "mot"
#   canhbao: chỉ phát âm + Telegram (cách cũ khi tắt ô) · boqua: không làm gì
CHIENLUOCNGUOILA_TATCA = "tatca"
CHIENLUOCNGUOILA_MOT = "mot"
CHIENLUOCNGUOILA_TRANH = "tranh"
CHIENLUOCNGUOILA_CANHBAO = "canhbao"
CHIENLUOCNGUOILA_BOQUA = "boqua"
CHIENLUOCNGUOILA_MAP = {
    "Tạm ngưng cả máy (cùng bản đồ)": CHIENLUOCNGUOILA_TATCA,
    "Chỉ tạm ngưng nhân vật thấy": CHIENLUOCNGUOILA_MOT,
    "Tránh xa người lạ, đánh tiếp": CHIENLUOCNGUOILA_TRANH,
    "Chỉ cảnh báo": CHIENLUOCNGUOILA_CANHBAO,
    "Bỏ qua": CHIENLUOCNGUOILA_BOQUA,
}
# Bán kính (ô, đường chim bay) quanh người lạ mà chiến lược "tranh" bỏ quái / điểm đánh; mặc định = vùng nhường quái đồng đội
BANKINHTRANHNGUOILA = 15.
# Chỗ người lạ đứng còn được tránh bấy nhiêu giây sau lần thấy cuối (đi khuất màn hình vẫn có thể quay lại)
THOIGIANNHONGUOILA = 60.
# Thấy lại cùng người lạ sau khi khuất quá bấy nhiêu giây thì tính là lần gặp mới (đếm lại "Phản ứng sau" / bám theo)
THOIGIANGIANDOANNGUOILA = 5.
# Chiến lược "tranh": người lạ ở trong BANKINHTRANHNGUOILA quanh mình liên tục bấy nhiêu giây (đã đổi điểm đánh mà vẫn sát) => coi là bám theo
THOIGIANBAMTHEONGUOILA = 90.
# Tín hiệu "vừa thấy ẩn thân" của nhân vật khác cùng bản đồ còn hiệu lực trong bấy nhiêu giây (nhân vật thấy sẽ làm mới liên tục mỗi 0.5s)
THOIGIANCHIASEANTHAN = 3.

# Nhóm game đầy theo máy chủ (moitruong.get_soluongthanhviennhomtoida): Aegis 5 ("Nhóm đã đạt thành viên tối đa (5)", ảnh 2026-11-26),
# Niết Bàn 9 (commit "niết bàn"). Trước đây dùng chung 9 nên trưởng nhóm Aegis đủ 5 người vẫn mời thêm mỗi 3s
SOLUONGTHANHVIENNHOMTOIDA = 5
SOLUONGTHANHVIENNHOMTOIDA_NIETBAN = 9
# Số ô id thành viên đọc trong bộ nhớ (lấy theo bản lớn nhất)
SOLUONGTHANHVIENNHOMTOIDATHUCTE = 9
# Tổ đội tự động / đội phó bản lập nhóm mời lần lượt từng người: người đang mời quá chừng này giây chưa vào thì mời người kế (lượt sau
# mời lại). Người đồng ý vào nhóm trong 0.3-0.5s (log 364 2026-11-19 22:23); 8s cũ làm mỗi lần ai đó lỡ lời mời đầu tốn trọn 8s (cả vòng ~26s)
THOIGIANCHOMOITHANHVIEN = 3.
# Thành viên vãng lai (todoi.json "vanglais", tactu_hoatdong_xq._xulyvanglai): cả nhóm giữ đủ số tối đa (get_soluongthanhviennhomtoida),
# người vãng lai đang chiếm slot chỉ nhường khi vãng lai khác cần buff nhóm.
# Buff nhóm còn dưới chừng này giây coi như thiếu: người buff chỉ thấy có / không hiệu ứng của người khác (thời gian chỉ đọc được của
# chính mình), không buff lại trước khi hết, vào sớm chỉ ngồi chờ
THOIGIANBUFFNHOMSAPHET = 3.
# Chế độ buff toàn bang (tactu_hoatdong.action_bufftoanbang): thành viên vào nhóm chừng này giây chưa từng đứng trong tầm nhìn / đã khuất
# chừng này giây mà chưa đủ buff thì bỏ qua (mời từ xa không tới); ở nhóm quá THOIGIANBUFFTOANBANGTOIDA giây thì rời luôn (buff không lên
# được: khác chế độ PK, chưa học chiêu...); vừa rời nhóm của ai thì chừng này giây không nhận lại lời mời của người đó (bot Tổ đội tự
# động mời lại liên tục); đủ điều kiện rời phải giữ liên tục THOIGIANBUFFTOANBANGGIU giây (bảng hiệu ứng cập nhật trễ sau khi buff)
THOIGIANBUFFTOANBANGCHOTHANHVIEN = 60.
THOIGIANBUFFTOANBANGTOIDA = 180.
THOIGIANBUFFTOANBANGBOQUAMOI = 30.
THOIGIANBUFFTOANBANGGIU = 1.5
# Chế độ buff toàn bang: Ngân Châm / Kim Châm Độ Ách, Tiểu Chu Thiên trên người khác còn dưới chừng này giây thì buff lại (người dùng
# 2026-11-28). Máy chủ không gửi thời gian hiệu ứng của người khác => còn lại = thời gian buff (học từ chính mình) - lúc mình gửi buff;
# chưa từng gửi buff lên người đó (có buff từ trước, không rõ còn bao lâu) thì buff lại 1 lần. {vị trí kỹ năng: mã hiệu ứng}
THOIGIANBUFFTOANBANGBUFFLAI = 750.
# (ghi số: VITRIKYNANG_ / HIEUUNGKYNANG_ khai báo bên dưới) Ngân Châm 5011 -> 5011, Kim Châm 5012 -> 5012, Tiểu Chu Thiên 3291 -> Nội Kháng 3292
VITRIKYNANGBUFFLAITOANBANGs = {5011: 5011, 5012: 5012, 3291: 3292}
# Gửi buff lại lên cùng người cách nhau ít nhất chừng này giây (phòng gửi rồi không lên, bảng hiệu ứng trễ)
THOIGIANBUFFTOANBANGGIUALAN = 20.
# (Bỏ THOIGIANVANGLAICHOBUFF 2026-11-28: chờ 30s chưa được buff — người buff ở xa — vãng lai cũng tự rời; giờ chỉ nhường khi đủ buff)
# Vào nhóm ít nhất chừng này giây mới xét nhường (bảng hiệu ứng / shared_data cập nhật sau khi vào)
THOIGIANVANGLAIOTOITHIEU = 3.
# Vừa nhường slot thì chừng này giây không nhận lời mời lại (trừ khi chính mình cần buff) để người cần buff vào trước
THOIGIANVANGLAINGHISAUNHUONG = 20.
SOLUONGHIEUUNGNHANVATTOIDA = 20

TUTHENHANVAT_DUNGIM = 1
TUTHENHANVAT_DICHUYEN = 2
TUTHENHANVAT_NAMDUOIDAT = 3  # cả đồ lẫn vật phẩm
TUTHENHANVAT_NGOI = 4
TUTHENHANVAT_TANCONGVATLY = 6
TUTHENHANVAT_TANCONGPHEPTHUAT = 9
TUTHENHANVAT_DELAYSAUTANCONG = 11
# Tư thế lỗi: dính chiêu boss Kính Ma Hổ Dực (PYK, hiệu ứng 2114) thì kẹt ở đây, mất hình, client không tự bước (không gửi go) => ghi về đứng im
TUTHENHANVAT_LOI = 15

LOAIMUCTIEU_QUAIVATHOACNPC = 0
LOAIMUCTIEU_NGUOICHOIKHACNHOM = 1
LOAIMUCTIEU_NGUOICHOICUNGNHOM = 2

LOAIDOITUONG_NHANVAT1 = 1
LOAIDOITUONG_NHANVATKHAC1 = 2
LOAIDOITUONG_VATPHAMDUOIDAT = 3

# Phẩm chất vật phẩm dưới đất = byte +0x29 (gói tin xuất hiện vật phẩm), game tô màu tên theo nó (xq + 0x9C19B): 0 trắng (thường),
# 1 xanh lam 0x00FFFF, 2 vàng 0xFFFF00, 3 tím 0xF076FC, 4 xanh lục 0x00FF00
PHAMCHATVATPHAM_MAP = {1: "Xanh lam", 2: "Vàng", 3: "Tím", 4: "Xanh lục"}
# Số hiệu hình vật phẩm (file item/bag/<số>.tcb), dưới đất ở đối tượng +0x128C (gói "vật phẩm xuất hiện" xq+0xA0F5A), trong túi ở
# hành trang +0x1DA1C + ô*4. Đo 18/11 (Aegis) đối chiếu loại trong mô tả: Y Phục 6034~6162, Nón 6540~6658, Vũ Khí 7022~7623,
# Hạng Liên 8607~8610, Yêu Đới 8712~8714, Giày 8810~8811 => trang bị là [6000, 8900). Đồ rác tên giống trang bị thì hình khác hẳn:
# Giáp Trụ 4072, Cương Thi Quán 4063, Phá Bố Y 4048, Tử Giả Di Vật 4034; đá 89xx (Lục Ngọc Thạch 8910); Pháp Bảo 95xx không tính.
# Riêng Dây Càn Khôn (túi) 8700 lọt vào khoảng nên loại ra
HINHTRANGBI_KHOANGs = ((6000, 8700), (8710, 8900))

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
# Dòng khung chat chứa các từ này (so chữ thường) thì log [CHẾ TẠO] (MoiTruong._xulydongchetao): đo tỉ lệ chế / luyện / ghép thật
TUKHOADONGCHETAOs = ("luyện ra", "luyện chế", "thất bại", "thành công", "hợp thành", "tinh thạch", "khảm", "ngẫu nhiên", "random",
                     # Hợp thành Tinh Thạch (ảnh 2026-11-17): "Số lượng 5, tỉ lệ thành công 20 xác xuất 93" rồi "Hợp thành thất bại, ..."
                     # -> số random (xác xuất) > tỉ lệ thì xịt
                     "xác xuất", "xác suất", "tỉ lệ")
# Dòng khớp từ khoá nhưng không phải kết quả chế (log 17/11: loa "<ai đó> đã mở Túi Linh Thạch ... nhận được X Tinh Thạch", vứt đá)
TUKHOADONGCHETAOBOQUAs = ("đã mở", "quăng")
# Tự hợp thành Tinh Thạch dưới cấp 3 đủ 5 viên (loop_xq, acc 342/347/354/359/364). Tắt tạm 2026-11-17 để người dùng tự ghép
# 2-5 viên đo tỉ lệ / số random máy chủ (2/3/4/5 viên = 20/30/50/90%); bật lại 2026-11-19
IS_TUDONGHOPTHANHTINHTHACH = True
# Dò lệnh client tự gửi lên máy chủ (MoiTruong.action_thietlaphooklenhgame, vd bấm xác nhận lên cấp): bật thì log [LỆNH GAME] mọi lệnh
# game gửi mà bot không gửi. Bộ đệm vòng SOLUONGDONGLENHGAME ô (lũy thừa của 2) x KICHTHUOCDONGLENHGAME byte
IS_LOGLENHGAME = True
SOLUONGDONGLENHGAME = 32
KICHTHUOCDONGLENHGAME = 160
# Bang phái người chơi khác hỏi bằng "desc user <ID>" (máy chủ trả các dòng " Danh tính: ...", " Bang phái: ..." vào khung tin hệ thống):
# mỗi lần hỏi cách nhau GIANCACHHOIBANGPHAI giây, chờ trả lời tối đa THOIGIANCHOTRALOIBANGPHAI giây. Đã biết (kể cả nạp từ
# thongtinnguoichoi.json) thì không tự hỏi lại người khác: môn phái / bang gần như cố định, cần thì người dùng tự bấm xem để cập nhật
GIANCACHHOIBANGPHAI = 1.5
THOIGIANCHOTRALOIBANGPHAI = 3.
# Câu trả lời "desc user" mới nhận giữ trong shared_data chừng này giây cho cửa sổ khác / giao diện (ghi file mỗi 5s) lấy
THOIGIANCHIASETHONGTINNGUOICHOI = 120.
# Danh sách thành viên bang mình (moitruong_xq.get_thanhvienbangs): gửi "org status" (lệnh client gửi khi mở tab Bang Phái ở Alt+B)
# mỗi chừng này giây để biết người vào / rời bang; tối đa 200 người, mỗi người 0x48 byte (xq + 0x143487 xoá 0xE10 dword trước khi ghi)
THOIGIANLAMMOITHANHVIENBANG = 600.
SOTHANHVIENBANGTOIDA = 200
KICHTHUOCTHANHVIENBANG = 0x48
# Máy chủ chỉ trả lời "desc user" khi người đó cách mình trong chừng này ô (người dùng thấy), xa hơn thì chờ lại gần mới hỏi
KHOANGCACHHOIBANGPHAI = 12.
# Game gửi cả khối nhiều dòng (nối "\n", tới 0x640 byte) vào 1 tin, vd trả lời "desc user": ô 128 byte cắt mất dòng Bang phái
KICHTHUOCDONGTROCHUYEN = 512
# Tin mật đến ở khung trò chuyện: "<tên> nói thầm với bạn : <nội dung>" (chữ tím, ảnh 2026-11-10, Aegis); gửi tin mật "tell <ID> <nội dung>"
# (gõ "/tell <ID> ..." thì client gửi nguyên văn bỏ "/", XQ.exe 0x425BC3)
# Dòng thô hàm thêm dòng khung chat nhận (đo 2026-11-10): "ESC Y \t+16711926,Gạ=364\t- nói thầm với bạn : chao" -> tên là liên kết
# "\t+<màu>,<tên>=<ID>\t-" (bấm vào tên ra "/tell <ID>"), ID người gửi có sẵn trong dòng
MAUTINMATDEN = re.compile(r"^\s*(?:\t?\+\d+,(?P<ten>[^=\t]+)=(?P<id>\d+)\t-|(?P<tenthuong>\S.{0,30}?))\s*nói thầm với bạn\s*:\s*(?P<noidung>.*)$", re.M)
# Danh sách mật ngữ gần đây trong THONGTINGAME (XQ.exe 0x43F110 dựng "/%s(%d)%s" từ đây): LIENHETINMAT_SOLUONG ô x LIENHETINMAT_KICHTHUOC
# byte {tên 0x14 byte, ID int +0x14}. Chưa dò bằng chữ ký vì chưa thấy lệnh nào dùng hằng này mà ổn định đủ (mới đọc tĩnh, chưa đo trong game)
TG_LIENHETINMAT = 0xADFA5C
LIENHETINMAT_SOLUONG = 20
LIENHETINMAT_KICHTHUOC = 0x18
# Bộ đệm chuỗi bot tự in vào khung trò chuyện (moitruong_xq.action_themdongkhungchat), byte UTF-8 kể cả số 0 cuối
KICHTHUOCDONGKHUNGCHAT = 1024

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
# Thục Sơn Kiếm đánh quái không dùng các chiêu này, quá tốn pháp lực (người dùng 2026-11-14); PK vẫn dùng
THUCSONKIEMBOCHIEUDANHQUAIs = (VITRIKYNANG_VANKIEMXUYENTAM, VITRIKYNANG_VANVUTIEUDIEU, VITRIKYNANG_BANGTAMTHUC, VITRIKYNANG_LANGKHONGCHIHUYET)

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

# Chiêu hồi máu vẫn dùng ở thành an toàn Tân Thủ Thôn / Chu Quốc (BANDOKHONGTANCONGs) (người dùng 2026-11-25): Vân Mộng Cốc
# Cam Lộ Trị / Khiết Vân Quyết / Sơ Trị, Thục Sơn Tiên Khí. Buff Kháng / buff sát thương và bước chạy lại gần để buff vẫn bị chặn
# Máy chủ từ chối buff lên người khác chế độ PK (mình đang bật PK): khung chat "Đối với đối phương không thể sử dụng<tên chiêu>"
# (người dùng chụp 2026-11-25; Khiết Vân Quyết đánh vùng không báo). Tin tới trong THOIGIANCHOTINKHONGTHEBUFF giây sau lần buff thì
# chặn buff người đó THOIGIANCHANBUFFKHACPK giây (TacTu._xulytinkhongthebuff)
TINKHONGTHEBUFF = unicodedata.normalize("NFC", "Đối với đối phương không thể sử dụng")
THOIGIANCHOTINKHONGTHEBUFF = 2.
THOIGIANCHANBUFFKHACPK = 60.

KYNANGHOIMAUTHANHANTOANs =(VITRIKYNANG_CAMLOTRI, VITRIKYNANG_KHIETVANQUYET, VITRIKYNANG_SOTRI, VITRIKYNANG_TIENKHI)

VITRIKYNANG_RAIDAUTHANHBINH = 5312
VITRIKYNANG_THOIMIENTHUAT = 5313
VITRIKYNANG_HUYENQUANGTHIEMANH = 5314
VITRIKYNANG_PHONGANTHUAT = 5315

VITRIKYNANG_LINHKHIHOTHE = 5911
VITRIKYNANG_KYMONTRAN = 5912
VITRIKYNANG_DONGIAPTRAN = 5913
# Trận pháp Vân Mộng Cốc nằm trong danh sách hiệu ứng mặt đất (MoiTruong.get_danhsachhieuungdat) với mã hiệu ứng = mã kỹ năng
# (dump Thỏ 342 lúc 2026-11-10 00:13: nút mã 5913 tại (165,177), nút kia tại (166,176)). Game không cho đặt 2 trận chung 1 tâm
# (người dùng báo) => trước khi đặt, đổi tâm nếu ô định đặt đã có trận
TRANPHAPVANMONGCOCs = {VITRIKYNANG_KYMONTRAN: "Kỳ Môn Trận", VITRIKYNANG_DONGIAPTRAN: "Độn Giáp Trận"}
# Mã hiệu ứng mặt đất client bỏ vẽ (MoiTruong.action_thietlaphookvehieuungdat). Trận pháp Vân Mộng Cốc hay làm văng engine.dll+0x424D,
# người dùng chấp nhận không thấy Kỳ Môn + Độn Giáp để khỏi dis (2026-11-14). Bot vẫn đọc nút trận nên né trận / chọn tâm vẫn chạy
MAHIEUUNGDATKHONGVE = (VITRIKYNANG_KYMONTRAN, VITRIKYNANG_DONGIAPTRAN)
# Cờ ẩn hiển thị trong client (MoiTruong._get_diachicohienthi: 1 byte mỗi cờ, hook đọc mỗi lần vẽ nên bật / tắt có tác dụng ngay).
# Người dùng chọn ở tab Khác (ô tích), lưu _internal/hienthi.json, bot đọc lại khi file đổi (ngoaihinh_xq.NgoaiHinh)
#  - hieuungnhanvat: 10 lớp hiệu ứng chiêu trên người nhân vật / quái (tia sét Lôi Động Cửu Thiên, hào quang 9321 / 9325 / 9326...),
#    dùng chung bộ đệm sprite hay nhả sớm; người dùng báo dis chủ yếu lúc PK (2026-11-14). action_thietlaphookvehieuungnhanvat
#  - tranphap: trận trên đất có mã trong MAHIEUUNGDATKHONGVE. action_thietlaphookvehieuungdat
#  - phanthan: đối tượng phân thân của chiêu (Ngự Kiếm Phi Tiên Thục Sơn: cả chục bóng đen bay tới mục tiêu). Đo trên 364 2026-11-14:
#    lớp +0x29 = 0x40, id +0x20 = 0 / -1, không tên, chép ngoại hình người dùng chiêu, tư thế 6, sống 0,06-15s.
#    action_thietlaphookvedoituong (bot vốn bỏ qua đối tượng id <= 0 nên không ảnh hưởng chọn mục tiêu)
COHIENTHI_VITRI = {"hieuungnhanvat": 0, "tranphap": 1, "phanthan": 2}
COHIENTHI_MACDINH = {"hieuungnhanvat": True, "tranphap": True, "phanthan": True}
LOPDOITUONG_PHANTHAN = 0x40
# Mã lớp hiệu ứng trên người vẫn vẽ khi bật Ẩn hiệu ứng chiêu trên người: hiệu ứng pháp bảo dưới chân (người dùng muốn giữ, 2026-11-14).
# Thử trên Gạ 364: giữ 9111 thì pháp bảo chưa hiện; giữ 9111 + 9326 + 9154 lúc Gạ chỉ còn lớp 9326 thì hiện => pháp bảo Gạ = 9326.
# Người chơi khác thấy 9321 / 9325 cùng kiểu thường trực => coi 9320-9329 là nhóm pháp bảo (chưa kiểm từng mã). 9111 / 9154 vẫn ẩn
MAHIEUUNGNHANVATGIULAI = tuple(range(9320, 9330))
# Tâm mình vừa đặt trận: gói máy chủ tạo nút về sau vài trăm ms, trong lúc đó vẫn coi ô là đã có trận
THOIGIANNHOTAMTRANVUADAT = 3.
# Vùng tác dụng trận Vân Mộng Cốc (người dùng báo 2026-11-10): Kỳ Môn 3x3 ô, Độn Giáp 5x5 ô quanh tâm => nửa cạnh (ô vuông)
# 1 và 2. Đặt: Kỳ Môn ngay ô mục tiêu (vùng nhỏ, lệch là mục tiêu dễ ra ngoài); Độn Giáp lệch 1 ô khỏi ô mục tiêu (vẫn phủ mục tiêu,
# chừa tâm cho Kỳ Môn vì game không cho 2 trận chung tâm) — MoiTruong._chontamtranvanmongcoc
NUACANHTRANVANMONGCOCs = {VITRIKYNANG_KYMONTRAN: 1, VITRIKYNANG_DONGIAPTRAN: 2}

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
# Trấn Cổ Thần Uy (Đào Hoa, buff ~60s, hoạt ảnh tư thế 9 ~1.4s): dùng lại giữa trận thì chen chuỗi chiêu (log 347 23/11: 55 lần / 3h,
# trung bình 1.9s từ lần gửi đầu tới chiêu đánh kế). Người dùng 23/11: không có mục tiêu thì làm mới sớm khi còn dưới
# THOIGIANLAMMOISOMTRANCO giây; đang kề mục tiêu thì chỉ dùng khi không còn chiêu đánh nào dùng được (cuối danh sách); hết buff quá
# THOIGIANTRANCOQUAHAN giây mà vẫn chưa có khe thì dùng như cũ (đầu danh sách)
THOIGIANLAMMOISOMTRANCO = 15.
THOIGIANTRANCOQUAHAN = 10.
VITRIKYNANG_KIMTRUNGCHAO = 3161
VITRIKYNANG_DATINCUONGLUC = 3191
VITRIKYNANG_KIMCUONGTHANPHAP = 3192

# Côn Luân (đọc bảng kỹ năng + "desc pf" trên ThiênĐạo 2026-10-29), cách dùng ở action_sudungkynangmonphaiconluan:
#   Lôi Long Quyết 9x9 quanh bản thân liên tục 6s, vận khí (6 bùa, 250 pháp lực, hồi 4s) - như Lôi Động Cửu Thiên của Mao Sơn;
#   Hàn Băng Trận 7x7 quanh bản thân, Đóng Băng 6s (5 bùa); Kim Quang Trận 5x5 quanh mục tiêu (3 bùa); Huyền Long Chân Khí (4 bùa);
#   Hỏa Long Quyết Thiêu Đốt 12s (3 bùa); Thương Long Quyết Đóng Băng 6s (3 bùa); Hàn Băng Thuật Chậm Chạp 6s (1 bùa); Ngự Lôi Thuật
#   choáng 1s (1 bùa); Phong Hỏa Quyết (không bùa); Phong Ma Chú Trầm Mặc 6s; Càn Khôn Na Di tâm pháp hộ thể 5 phút (bấm lại không tắt
#   được, hiệu ứng trùng id kỹ năng); Đằng Vân Giá Vũ dịch chuyển (chiêu lướt như Khai Thiên Tịch Địa). Chưa dùng: Biến Thân Thuật, Khốn Ma
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
# Định Tiêu (Mao Sơn): "pf 4181" mở menu 16 ô định tiêu (tối đa bao nhiêu ô theo cấp), Xuyên Không Hành "pf 4182.<ô>" bay tới ô đó.
# Bot chỉ mở menu đọc ô nào ở bản đồ nào (moitruong.get_danhsachdinhtieu), không chọn ô (chọn là ghi đè định tiêu)
VITRIKYNANG_DINHTIEU = 4181
# Chờ menu Định Tiêu về tối đa chừng này giây; danh sách đọc rồi thì chừng này giây sau mới đọc lại (người chơi đổi định tiêu)
THOIGIANCHODINHTIEU = 4.
GIANCACHDOCDINHTIEU = 600.

VITRIKYNANG_LUUHUYETTHUAT = 4172
VITRIKYNANG_DITINHDAIPHAP = 4173

# Nhân vật mới chưa học đủ kỹ năng: chỉ được dùng các kỹ năng liệt kê ở đây.
# Khoá là ID người chơi (ưu tiên, cố định) hoặc tên nhân vật viết thường (khoảng trắng Alt+255 coi như dấu cách).
KYNANGCHOPHEPTHEONHANVAT_MAP = {

}
VITRIKYNANG_THANTUEPHAPCHU = 4171

VITRIKYNANG_MANGXAXUATDONG = 2410
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
# Phản Tỏa (người dùng 2026-11-18): đòn chí mạng 100%, delay 0. Máy chủ phản tỏa vào mục tiêu của Tự Động Công Kích => phải "kill"
# mục tiêu trước rồi mới dùng (TacTu.action_sudungkynangmonphaidaohoanguyen)
VITRIKYNANG_PHANTOA = 2124
# Chiêu làm máy chủ xoá cờ "kill" (người dùng thử tay 28/11): ra xong là Đào Hoa gửi lại "kill" ngay (TacTu._guikilldaohoa). Choáng cũng xoá
# (TacTu._tudongsudungkynang hạ _is_battudongtancongvatly khi bị choáng, hết choáng là kill lại)
VITRIKYNANGXOAKILLs = (VITRIKYNANG_DAOHOALACANH, VITRIKYNANG_DAIHAIVOLUONG)
# Phản Tỏa chỉ dùng khi máy chủ đã thật sự ép đòn đánh thường (gói 0x41, MoiTruong.get_is_vuadanhthuong) lên mục tiêu trong chừng này giây
# (từ 24/11 tối tính cả ô vung máy chủ chèn vào gói chiêu bị cắt hình: cũng là đánh thường do cờ "kill" đang chạy)
THOIGIANXACNHANDANHTHUONGPHANTOA = 2.
# Đào Hoa chỉ "kill" khi đã xong chiêu mở đầu (Thốn Kình / Lạc Ảnh / Lạc Kích / khống chế người chơi); đứng cạnh mục tiêu quá chừng
# này giây mà vẫn còn chiêu mở đầu chưa dính hiệu ứng (miễn khống chế, máy chủ từ chối...) thì kill luôn
THOIGIANCHOMODAUKILLTOIDA = 3.
# Đã bỏ chờ số bay đánh thường trước khi chen chiêu (thêm 18/11, bỏ 24/11, người dùng: kỹ năng ra đều hơn): yêu cầu cũ là do tưởng
# cú vung dư sau chiêu delay 0 / buff là đòn đánh thường bị chiêu chen làm mất. Đánh thường thật ra số bay 0.65-0.85s sau khi vung
#
# NGUỒN GỐC CÚ VUNG DƯ (đo 24/11 tối, log 342): gần như mọi ô vung mã 0 không sát thương quanh chiêu là ĐÁNH THƯỜNG máy chủ chèn vào
# do "kill" đang bật (cùng gói / cùng bộ đếm với ô chiêu), không phải hoạt ảnh của chiêu: bật "kill" ~18.5 ô/phút, tắt ~2/phút. Người
# dùng chốt giữ "kill" mọi lúc (tắt thì hết nguyên khí đứng im) => chỉ cắt hình các ô này, bot không chờ đánh thường mới dùng chiêu.
# Đã gỡ THOIGIANOPHATLAISAUCAT (0.15s bỏ qua ô sau lần cắt, giả thuyết client phát lại; đo 01:43 chỉ ~3% => bỏ qua nhầm đánh thường thật)
#
# Log 342 24/11 14:00-15:13: chiêu delay 0 (Lạc Ảnh, Phản Tỏa, Đại Hải, Ba Động) => ô 42/00 (đánh thường chèn vào) tới CÙNG LÚC với
# số bay của chiêu (43/57 lần trong ±0.04s). Ô có số bay mới tới cùng lượt đọc, hoặc trong chừng này giây sau ô, là ô vung không sát
# thương (sát thương lượt đó là của chiêu): cắt ngay, không tính là đánh thường (Phản Tỏa)
THOIGIANSOBAYCUNGLUCO = 0.1
# Ô chiêu delay 0 đã có số bay (trên) thì cắt hẳn khi nó bắt đầu phát (MoiTruong.action_cathoatanhkhicosobay, người dùng 24/11); quá
# chừng này giây sau khi ô tới mà chưa thấy phát thì thôi
THOIGIANCATOCHIEUDELAY0TOIDA = 1.5
# Sau lệnh các chiêu này máy chủ hay chèn 1 ô đánh thường (ô 42/00 tới 0.00-0.11s sau lệnh, không sát thương; buff không có số bay nên
# cách số bay cùng lúc không bắt được) => ô mã 0 hiện trong THOIGIANOCHIEUSAUGUI giây sau lệnh: không tính đánh thường, cắt ngay khi phát
# Nhất Quyền (thêm 24/11 tối): ô của nó là mã 90, số bay 0.28-0.59s sau ô (log 342 19:57-19:59, tắt "kill": 13/13 đợt chỉ 1 ô mã 90).
# Khi bật "kill", 429/947 đợt (342.log.cu) có thêm 1 ô mã 0 tới 0.01-0.1s sau lệnh, xếp TRƯỚC ô mã 90 => vung thừa ~0.7s trước Nhất
# Quyền. Cắt ô mã 0 đó (20:05-20:22: 53/56 lần); ô mã 90 không bị đụng (chỉ xét ô mã 0)
KYNANGCATHOATANHNGAYs = (VITRIKYNANG_DAOHOALACANH, VITRIKYNANG_PHANTOA, VITRIKYNANG_KIMTRUNGCHAO, VITRIKYNANG_TRANCOTHANUY,
                         VITRIKYNANG_NHATQUYENBATSON)
# 24/11: log 342 15:43-15:49, ô sau lệnh các chiêu này (trừ ô có số bay cùng lúc): 0-0.2s 18 ô và 0.2-0.3s 2 ô đều là ô dư (không số
# bay); 0.3-0.5s 4 ô thì 2 có số bay kiểu đánh thường 0.55-1s (đòn thật) => mốc 0.3 (người dùng duyệt; đã thử 0.5 nhưng cắt nhầm đòn thật)
THOIGIANOCHIEUSAUGUI = 0.3
# Chiêu có mã hoạt ảnh 0 giống đánh thường (Lạc Kích): ô đòn mã 0 hiện trong chừng này giây sau khi xếp lệnh chiêu thì không coi là đánh thường
KYNANGHOATANHMA0s = (VITRIKYNANG_LACKICH, )
THOIGIANBOQUAHOATANHMA0 = 1.
# Lạc Kích: số bay của nó ra ở cuối hoạt ảnh (cặp 2 số, ~0.8-1.15s sau khi vung); log 342 24/11 16:00-16:15 sau cặp số đó 26/30 lần
# có thêm 1 cụm ô vung dư 0.13-0.22s sau (không sát thương, ngay trước Nhất Quyền). Ô tới trong THOIGIANVUNGDULACKICH giây sau số bay
# của Lạc Kích (1 ô mỗi đợt) là vung dư: cắt ngay (MoiTruong._theodoidanhthuong). Xét trong THOIGIANDOTLACKICH giây sau lệnh cuối
THOIGIANVUNGDULACKICH = 0.4
THOIGIANDOTLACKICH = 2.5
# Log chẩn đoán ô mã 0 ([Ô MÃ 0]: byte ô, chiêu gửi gần nhất, tư thế), hàng đợi lúc cắt và [SAU CẮT] (tư thế / hàng đợi 1s sau cắt).
# Tắt 24/11 sau khi xong việc cắt ô vung dư (log dài); bật lại khi cần dò
IS_LOGOMA0 = False
# Ba Động (đánh từ xa) chỉ dùng khi mục tiêu cách ít nhất chừng này ô (max(|dx|, |dy|)): gần hơn thì chạy vào cận chiến, dùng Ba Động
# vẫn bị máy chủ khoá chiêu kế như chiêu delay 0 mà không chạy tới được (người dùng dặn 2026-11-10).
# 3 -> 5 (người dùng 2026-11-23: cách 2-3 ô vẫn dùng, tới nơi đứng chờ mới được Lạc Kích). Tính: sau Ba Động client đứng tư thế 6
# ~0.68s không bước, rồi chạy ~0.42s/ô => tới kề sau 0.68 + 0.42 * (d - 1) giây; Lạc Kích (delay 0) bị THOIGIANCHANDELAY0LIENTIEP = 2s
# chặn, khoá máy chủ 0.8-1.7s => cần d >= 4.1 => 5 ô (tới nơi ~2.36s, vừa hết chặn). Gần hơn chỉ dùng khi mục tiêu đang chạy ra xa
# (get_is_muctieuchaytron, từ KHOANGCACHTOITHIEUBADONGCHAYTRON ô) hoặc đã kề (chiêu lót cận chiến)
KHOANGCACHTOITHIEUBADONG = 5.
KHOANGCACHTOITHIEUBADONGCHAYTRON = 2.

# Dịch chỗ đứng sau chiêu delay 0 của Đào Hoa (người dùng đề xuất 2026-11-09): Ba Động / Lạc Kích / Đại Hải ra dame ngay, không cần đứng
# yên, nhưng máy chủ khoá chiêu kế 0.8-1.7s => dùng lúc đó đi sang ô kề mục tiêu tốt hơn (tối đa SOBUOCDICHODELAY0 bước, vẫn kề mục
# tiêu nên hết khoá đánh được ngay). Điểm ô: + HESOGOMQUAIDELAY0 mỗi quái trong BANKINHDAIHAI ô (Đại Hải trúng nhiều con), - khoảng
# cách tới mục tiêu kế khi mục tiêu chính còn <= PHANTRAMMAUDONMUCTIEUKE % máu, - khoảng cách tới chỗ người chơi đang chạy tới (đón
# đầu), + ô thoáng (ô kề đi được, tránh kẹt góc vật cản). Chỉ đi khi hơn ô đang đứng NGUONGDICHODELAY0 điểm. Đi quá THOIGIANDICHODELAY0
# giây chưa tới thì thôi, đánh tiếp (khoá ngắn nhất ~0.8s, không để chậm chiêu kế)
# Log 342/347 ngày 2026-11-09 (102 lần, bản đi 2 ô, ngưỡng 1): 2 ô mất ~0.75s (43/102 lần chưa tới), chiêu kế chậm thêm ~0.3s (trung vị
# 1.18-1.34s so với 0.86-1.06s không dịch); 1 ô ~0.42s => chỉ đi 1 ô. "Mục tiêu kế" chiếm 77/102 lần, nhiều lần con kế cách 7-9 ô
# (đi 1 ô gần hơn 1.3 ô vô ích) => chỉ tính khi con kế cách mục tiêu chính <= KHOANGCACHMUCTIEUKEDELAY0 ô, ngưỡng 1 -> 1.5
# Hook bỏ hoạt ảnh chiêu delay 0 ở client (2026-11-09) đã GỠ 2026-11-12: người dùng thấy lâu lâu toạ độ đứng ở client lệch so với
# máy chủ. Bot chỉ còn trả byte gốc nếu client mang bản vá cũ (MoiTruong.action_gohookhoatanhtancong)
# Giữ chân sau chiêu delay 0 chờ số bay (thêm 2026-11-09, tối đa 0.25s) đã GỠ 2026-11-17 theo người dùng: chiêu delay 0 không cần
# giữ chân. Log 347: 660/800 lần "thấy số bay" ngay 0s (nhiều khả năng số bay đòn trước), 134 lần hết giờ không thấy => vô tác dụng
# THỬ LẠI 2026-11-15 (người dùng yêu cầu: đánh xong boss hoạt ảnh kéo dài mãi): đang tư thế xuất chiêu 6/9 mà mục tiêu hiện số bay mới
# (máy chủ đã tính đòn) hoặc mục tiêu chết / mất thì cắt về đứng im (MoiTruong.action_cathoatanhkhicosobay), ghi tư thế khựng 11 (LoopBoKhungSauTanCong tự về 1). Khác bản cũ đã gỡ
# 2026-11-09: không tua hàng đợi hoạt ảnh (bỏ cả bước đi => hình lệch chỗ thật). Bản 15/11 có bỏ các ô đòn đánh đầu hàng nhưng log
# 347 (1.936 lần) chưa từng bỏ được ô nào => gỡ 2026-11-17 theo người dùng, giờ chỉ ghi tư thế 11. Chiêu lướt (không khựng sau, vd Khai Thiên)
# không cắt. Chỉ cắt khi đã ở tư thế xuất chiêu ít nhất THOIGIANTOITHIEUCATHOATANH giây (số bay của đòn trước đến trễ không cắt nhầm
# đòn vừa bắt đầu). Lỗi lệch toạ độ / giật thì đặt False
IS_CATHOATANHKHICOSOBAY = True
THOIGIANTOITHIEUCATHOATANH = 0.1
# Đo tạm mã hoạt ảnh (2026-11-11, MoiTruong._dohoatanhchieu): danh sách khác rỗng thì log "[ĐO HOẠT ẢNH]" mọi đòn đánh của mình có
# mã hoạt ảnh ngoài MAHOATANHDABIETs (bắt cả chiêu bấm tay), và mọi đòn trong THOIGIANDOHOATANH giây sau khi bot gửi chiêu trong danh
# sách.
# Đo 24/11 tối với (Nhất Quyền, ): tắt "kill" thì gói Nhất Quyền chỉ có ô mã 90; bật "kill" thì máy chủ thêm ô mã 0 (đánh thường,
# cùng bộ đếm byte 8-11 = cùng gói) xếp trước. Lưu ý: hàm đo đôi lúc quét lại cả vòng hàng đợi cũ (dòng trùng), lọc theo ô + byte
KYNANGDOHOATANHs = ()
THOIGIANDOHOATANH = 1.5
# Thốn Kình 20, Lạc Ảnh 50, Đại Hải 60, Ba Động 70, Nhất Quyền 90, đánh thường / Lạc Kích 0
MAHOATANHDABIETs = (0, 20, 50, 60, 70, 90)
# Từng tắt 2026-11-09 vì client không bước khi còn tư thế 6 (~0.68s); bật lại cùng ngày nhờ hook bỏ hoạt ảnh chiêu delay 0; TẮT LẠI
# 2026-11-12 khi gỡ hook đó (Ba Động / Đại Hải / Lạc Kích lại vào tư thế 6, đi lúc đó dễ lệch toạ độ máy chủ)
IS_DICHOSAUCHIEUDELAY0 = False
# Đào Hoa Lạc Ảnh là chiêu delay 0 (người dùng xác nhận 2026-11-10); từ 2026-11-11 đưa vào đây theo yêu cầu người dùng => cũng giữ chân
# tới số bay / dịch chỗ sau chiêu như 3 chiêu kia (trước đó chỉ nằm trong danh sách nối chiêu)
# Phản Tỏa cũng là chiêu delay 0 (người dùng xác nhận 2026-11-18)
VITRIKYNANGDELAY0DAOHOAs = (VITRIKYNANG_BADONGQUYEN, VITRIKYNANG_LACKICH, VITRIKYNANG_DAIHAIVOLUONG, VITRIKYNANG_DAOHOALACANH,
                            VITRIKYNANG_PHANTOA)
TENCHIEUDELAY0DAOHOA = {VITRIKYNANG_BADONGQUYEN: "Ba Động", VITRIKYNANG_LACKICH: "Lạc Kích", VITRIKYNANG_DAIHAIVOLUONG: "Đại Hải",
                        VITRIKYNANG_DAOHOALACANH: "Lạc Ảnh", VITRIKYNANG_PHANTOA: "Phản Tỏa"}
SOBUOCDICHODELAY0 = 1
# Không dùng 2 chiêu delay 0 liền nhau (người dùng phát hiện 2026-11-10: delay 0 nối delay 0 bị khoá lâu, kẹp với chiêu có delay thì ổn).
# Chiêu Đào Hoa vào hồi chiêu gần nhất (= máy chủ nhận) là delay 0 và chưa quá THOIGIANCHANDELAY0LIENTIEP
# giây (khoá sau delay 0 dài nhất đo được ~1.7s) thì lượt này bỏ qua mọi chiêu delay 0, dùng chiêu có delay (Nhất Quyền, Thốn Kình...)
VITRIKYNANGDELAY0NOICHIEUDAOHOAs = VITRIKYNANGDELAY0DAOHOAs
VITRIKYNANGCODELAYDAOHOAs = (VITRIKYNANG_THONKINH, VITRIKYNANG_NHATQUYENBATSON, VITRIKYNANG_PHONGMAQUYET, VITRIKYNANG_KHONGTHUNHAPBACHNHAN,
                             VITRIKYNANG_METUNGQUYEN, VITRIKYNANG_HACHODAOTAM)
THOIGIANCHANDELAY0LIENTIEP = 2.
# Khoá sau chiêu delay 0 ngắn nhất từng đo ~0.6s (nguyen-ly-giam-delay-dao-hoa): thôi đi trước mốc đó để không bao giờ để lỡ lúc máy
# chủ nhận chiêu kế; đi 1 ô ~0.42s nên vẫn kịp tới. Hết mốc mà chưa tới thì vòng chiêu bình thường ngắt di chuyển rồi spam chiêu kế
THOIGIANDICHODELAY0 = 0.55
# Chỉ bắt đầu dịch khi đã hết tư thế xuất chiêu 6/9 (client không bước khi còn tư thế này) trong chừng này giây sau khi chiêu delay 0
# vào hồi chiêu; quá thì bỏ lượt dịch (còn ít thời gian khoá, đi không kịp)
THOIGIANCHOBATDAUDICHODELAY0 = 0.35
BANKINHDAIHAI = 3
# Log chẩn đoán vì sao không dùng Đại Hải khi quanh mình có >= 2 quái trong BANKINHDAIHAI ô (người dùng 25/11: PYK quái đông mà
# không thấy dùng). Giãn mỗi dòng chừng này giây cho log khỏi dày
THOIGIANLOGCHANDOANDAIHAI = 2.
HESOGOMQUAIDELAY0 = 2.
PHANTRAMMAUDONMUCTIEUKE = 30
KHOANGCACHMUCTIEUKEDELAY0 = 4.
HESODONMUCTIEUKE = 1.
HESODONDAUNGUOICHOI = 1.5
HESOTHOANGDELAY0 = 0.25
NGUONGDICHODELAY0 = 1.5

VIRIKYNANG_NGUYENKHIQUYNGUYEN = 3172
TENKYNANG_NGUYENKHIQUYNGUYEN = "Nguyên Khí Quy Nguyên"
# Server cho hết hạn ~30 phút mà icon client vẫn còn (cả kiểu 1800 lẫn 30000 đều từng sai). Người dùng chốt 2026-11-22: mốc là
# tin "Tập trung vận khí" gần nhất trong khung chat, quá chừng này giây thì dùng lại 1 lần dù còn hiệu ứng (tắt rồi bật lại)
THOIGIANLAMMOINGUYENKHIQUYNGUYEN = 600
# Sau mỗi lần gửi Nguyên Khí Quy Nguyên, chừng này giây mới được làm mới lần nữa (chờ tin; lỡ không bắt được tin thì không bấm qua lại)
THOIGIANCHOTINLAMMOINGUYENKHIQUYNGUYEN = 30.
VIRIKYNANG_HOTHEKIMCANG = 3173
VITRIKYNANG_DATINHCUONGLUC = 3191

# "kill" (bật tự động đánh thường lên mục tiêu, không phải kỹ năng) đã bật với mục tiêu này thì chừng này giây mới gửi lại cho chắc
THOIGIANGUILAITANCONGVATLY = 5.
# Đào Hoa gửi "kill" riêng ngoài danh sách chiêu (_guikilldaohoa) nên không chiếm lượt kỹ năng: gửi lại mỗi chừng này giây, mọi lúc
# (người dùng 27/11: 2s; 28/11: 1s, 0.5s rồi 0.25s luôn luôn - bỏ dò trận Lạc Ảnh vì Lạc Ảnh / Đại Hải / trong trận / choáng đều xoá cờ)
THOIGIANGUILAIKILLDAOHOA = 0.25
# Tự tăng cấp (TacTu._tudongtangcap): mặc định tăng tới cấp này, mỗi lần gửi "gift upgrade" cách nhau chừng này giây
# 60 -> 75 (người dùng dặn 2026-11-23: acc gà 60 dùng Chén Bạc code welcome2d60 lên ~70)
CAPTUDONGTANGCAPTOIDA = 75
THOIGIANGUILAITANGCAP = 3.
# Lên cấp thì tự quay vòng số ở Bảo Điển (TacTu._tudongquayso): lệnh dò bằng log [LỆNH GAME] khi người chơi tự bấm "Khởi động Game".
# Mỗi lượt gửi lần lượt (mở Bảo Điển, mở vòng quay, "Khởi động Game") cách nhau THOIGIANGIUALENHQUAYSO giây: gửi riêng
# "zgdict rock start" thì máy chủ không quay (thử 2026-11-02). Bảo Điển để mở cho người dùng xem phần thưởng, vòng quay thì đóng; chờ máy chủ trả tên
# món tối đa THOIGIANCHODONGVONGQUAY giây rồi mới sang lượt kế; tự tăng cấp chờ quay hết lượt mới tăng tiếp
LENHQUAYSOLENCAPs = ("zgdict open", "zgdict rock open", "zgdict rock start")
THOIGIANGIUALENHQUAYSO = 1.
THOIGIANCHODONGVONGQUAY = 10.
# Có kết quả rồi thì chờ hoạt ảnh quay tới món trúng (client mới cộng đồ vào túi) tối đa chừng này giây tính từ "Khởi động Game"
THOIGIANCHOCONGDOVONGQUAY = 30.
# Chỉ quay được khi cấp nhân vật không quá chừng này (người dùng dặn 2026-11-02): cấp cao hơn thì bỏ các lượt còn chờ
CAPTOIDAQUAYSO = 29
# Đào Hoa Nguyên chỉ "kill" (bật đánh thường) khi nguyên khí không quá chừng này: còn nguyên khí thì spam chiêu, đánh thường làm chiêu ra chậm.
# 3 = chưa đủ 4 cho Nhất Quyền (để 2 thì nguyên khí 3 + mục tiêu đã có Trọng Thương / Lạc Kích không chiêu nào được dùng, đứng im ~1s)
NGUYENKHITANCONGVATLYDAOHOA = 3
# Nguyên khí hồi tới chừng này thì ngắt đánh thường (cách xa ngưỡng bật để không đánh vài chiêu lại phải "kill" lại)
NGUYENKHINGATTANCONGVATLYDAOHOA = 8# Lạc Kích lặp lại (mục tiêu đã có Lạc Kích) là chiêu lót delay 0 duy trì (khôi phục 2026-11-10, kẹp xen chiêu có delay -
# THOIGIANCHANDELAY0LIENTIEP): dùng khi sau nó còn đủ cho Nhất Quyền (2 + 4 trên mô tả), hoặc khi Nhất Quyền còn hồi ít nhất
# THOIGIANHOICHIEUCONLAICHIEULOT giây (bước chờ delay 0 -> Nhất Quyền 0.8-1.7s bị hồi chiêu che mất) và nguyên khí còn
# NGUYENKHITOITHIEUCHIEULOTKHIHOICHIEU. Thời gian còn lại tính từ lúc Nhất Quyền vào hồi chiêu + tái sử dụng trên mô tả
NGUYENKHITOITHIEUCHIEULOT = 6
THOIGIANHOICHIEUCONLAICHIEULOT = 1.
NGUYENKHITOITHIEUCHIEULOTKHIHOICHIEU = 4
THOIGIANHOICHIEUNHATQUYEN = 2.
# Nhất Quyền đã hồi chiêu mà nguyên khí không quá chừng này thì không dùng Đại Hải (tốn 4) để lót, đánh thường để dành cho Nhất Quyền
# (ngoài Phong Yêu Kính)
NGUYENKHIGIUCHONHATQUYEN = 4
# Phong Yêu Kính, đông quái quanh mình (Đại Hải ưu tiên hơn Nhất Quyền, người dùng 28/11): Đại Hải sẵn sàng mà nguyên khí dưới chừng này thì Nhất Quyền
# (tốn 4) chờ, dồn cho Đại Hải (tốn 4); từ chừng này trở lên thì Nhất Quyền dùng xong vẫn còn đủ cho Đại Hải
NGUYENKHINHUONGDAIHAI = 8
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
# Chưa chính xác hẳn: có choáng dài 6s (Thiên Cân của bảo thú giang hồ) sẽ bị coi là Bất Động => với nhân vật mình nay đọc TÊN hiệu
# ứng (MoiTruong._get_loaihieuung9002banthan), cách theo thời gian chỉ dùng cho đối tượng khác và trong lúc chờ máy chủ trả tên
THOIGIANTOIDACHOANG = 3
THOIGIANTOIDABATDONG = 15
# Ô hiệu ứng trên đối tượng (DC.NV_HIEUUNG, mỗi ô DC.NV_KICHTHUOCHIEUUNG = 0x13C): +0 vị trí trong bảng id, +4 có lợi, +8 thời gian tối
# đa (giây), +0xC mốc GetTickCount kết thúc (ms; đo 2026-11-18 acc 418: mốc - tick hiện tại ≈ thời gian còn lại; dính lại thì đổi),
# +0x10 chữ mô tả (tối đa 0x12B byte). Chữ chỉ có sau lệnh "desc loop <ID mình> <mã hiệu ứng>" (client gửi khi rê chuột lên icon):
# máy chủ trả gói loại 0x82 (xq+0x4F3A: mã hiệu ứng short ở +2, chữ từ +4) và client chép chữ vào ô có mã đó trên NHÂN VẬT MÌNH
# ([xq+0x380AF8]) => chỉ đọc được hiệu ứng của chính mình. Chữ dạng " Lạc Tuyết Vô Ngân :\n Tăng thêm 20％ Thân Thủ."
HIEUUNG_MOCKETTHUC = 0xC
HIEUUNG_MOTA = 0x10
HIEUUNG_DODAIMOTA = 0x12B
# Chưa thấy chữ sau từng ấy giây thì gửi lại "desc loop", tối đa SOLANHOIMOTAHIEUUNG lần mỗi lần dính
THOIGIANCHOMOTAHIEUUNG = 1.0
# Bảng hiệu ứng tab Chiến đấu: mã chưa biết tên thì bot tự "desc loop" (MoiTruong.get_hieuungbanthans), mỗi mã 1 lần / chừng này
# giây, mọi mã cách nhau THOIGIANGIUAHAILANHOITENHIEUUNG giây (tên học được lưu tenhieuung.json, lần sau khỏi hỏi)
THOIGIANHOILAITENHIEUUNG = 60.
THOIGIANGIUAHAILANHOITENHIEUUNG = 1.
SOLANHOIMOTAHIEUUNG = 3
# Tên hiệu ứng 9002 (trước dấu ":") -> loại; Choáng / Hôn Mê không làm gì được, Bất Động chỉ không đi được
TENHIEUUNG9002_MAP = {"choáng": "choang", "bất động": "batdong", "hôn mê": "honme"}
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
# Cấm Vệ Quân (mô tả đọc 2026-11-03, cấp 54, thương): Luân Hồi Vạn Chuyển game chỉ cho dùng khi Khí Huyết dưới 70% (trừ hao 2%);
# nguyên khí từ mức này trở lên mới lót thêm Mãng Xà Xuất Động sau Giao Long Nhập Hải
PHANTRAMSINHLUCLUANHOIVANCHUYEN = 68
NGUYENKHIDUCAMVEQUAN = 8

HIEUUNGKYNANG_NGUYENKHIQUYNGUYEN = 3172
HIEUUNGKYNANG_HOTHEKIMCANG = 3173
HIEUUNGKYNANG_LACKICH = 2123

HIEUUNGKYNANG_PHUCHOISINHLUC = 9154

KYNANGBAOTHU_TROICHAN = 74139
# Kỹ năng bảo thú giang hồ máy chủ xử lý chậm: gửi lại cùng chiêu khi máy chủ chưa kịp đặt hồi chiêu thì vẫn trừ nội lực mà chỉ có tác
# dụng 1 lần (người dùng 27/11). Gửi 1 chiêu rồi khoá chiêu đó tới khi thấy nó vào hồi chiêu (+0x504 khác 0) rồi hồi xong; không thấy vào
# hồi chiêu thì khoá tối đa THOIGIANKHOAKYNANGBAOTHU giây (gửi hụt / máy chủ bỏ) mới thử lại. Giữa 2 chiêu bảo thú bất kỳ cách nhau ít nhất
# GIANCACHKYNANGBAOTHU giây. Người dùng 27/11: cách 1s là bình thường, chỉ sợ spam 0.25s; khoá 8s quá lâu, để 2s
THOIGIANKHOAKYNANGBAOTHU = 2.
# Nhiều nhân vật cùng có bảo thú: bảo thú nào gửi chiêu lên 1 mục tiêu thì giữ chỗ theo NHÓM hiệu ứng (giukynang, như chiêu khống chế
# THOIGIANGIUKYNANGMUCTIEU) trong thời gian hiệu ứng của nhóm; bảo thú các cửa sổ khác bỏ nhóm đó, dùng chiêu nhóm khác (người dùng 27/11:
# nhiều con cùng ném 1 loại hiệu ứng lên 1 mục tiêu là dư). Nhóm khống chế chỉ còn Thiên Cân (27/11 bỏ Trói Buộc: người dùng cho là Trì Hoãn, chỉ chậm di chuyển, kém Đóng Băng).
# Khống chế giữ bằng thời gian choáng của Thiên Cân: bot không đọc được hiệu ứng choáng trên boss, trước giữ 3s thì
# hết giữ là bảo thú khác Thiên Cân chồng lên (log 27/11 Hào Quật: Thk 04:13:22, Kng 04:13:26) và Thiêu Đốt bị đẩy ra sau. Bảo thú
# vừa khống chế 1 mục tiêu cũng không tự chồng chiêu khống chế khác lên nó trong khoảng này (trước đây Thk Thiên Cân rồi 1s sau Trói Buộc)
# Người dùng 28/11: Cao Cấp Từ Năng choáng 6s, Từ Năng thường 3s; 1 nhân vật không bị choáng liên tục được (choáng xong có lúc miễn)
# => giữ = thời gian choáng của chiêu vừa ném + THOIGIANMIENCHOANGBAOTHU. Khoảng miễn 2s như get_is_cothegaychoang (người dùng chốt 28/11)
THOIGIANCHOANGCAOCAPTHIENCANBAOTHU = 6.
THOIGIANCHOANGTHIENCANBAOTHU = 3.
THOIGIANMIENCHOANGBAOTHU = 2.
THOIGIANGIUKHONGCHEBAOTHU = THOIGIANCHOANGCAOCAPTHIENCANBAOTHU + THOIGIANMIENCHOANGBAOTHU
# Thiêu Đốt cháy 20s nhưng chỉ ~15% ném trúng (người dùng 27/11) => không khoá 20s mù (trượt là mất 20s): mục tiêu đã dính cháy
# (HIEUUNGTHIEUDOTBAOTHUs) thì không ném; chưa dính thì mọi bảo thú cứ ném, không giữ chỗ nhường nhau (người dùng 28/11; trước đây
# giữ 3s/1 bảo thú). Mỗi bảo thú vẫn khoá chiêu tới khi hồi xong và cách chiêu trước GIANCACHKYNANGBAOTHU
# Hiệu ứng trên mục tiêu dính Thiêu Đốt bảo thú (icon đốm lửa): 9026 (tenhieuung.json ghi "Đốt Cháy"). Đo log chẩn đoán Kng 359 27/11
# Lăng Ly Sơn: 3 lần 9026 hiện 0.6-0.9s sau "Thêu đốt" (Đường Truy 04:23:39, 04:24:32; Thế Công Minh 04:25:21), lần đầu mất sau ~22s
# (khớp cháy 20s), còn lại các lần ném không ra hiệu ứng mới (trượt, khớp ~15%). Bot nhận theo mã này hoặc tên có "thiêu đốt"
HIEUUNGTHIEUDOTBAOTHUs = (HIEUUNGKYNANG_THIEUDOT,)
# Theo dõi hiệu ứng mới trên mục tiêu trong chừng này giây sau khi ném Thiêu Đốt
THOIGIANCHANDOANTHIEUDOTBAOTHU = 3.
# Bật log chẩn đoán "[BẢO THÚ CHẨN ĐOÁN]" (đã đo xong mã 9026, người dùng bảo tắt 27/11)
IS_CHANDOANTHIEUDOTBAOTHU = False
KHOAGIUCHO_BAOTHUKHONGCHE = "baothukhongche"
# Đóng Băng bảo thú (người dùng 27/11): làm chậm di chuyển + công kích 50% (tenhieuung 9013), không phải khống chế cứng => nhóm giữ
# chỗ riêng, dùng song song Thiên Cân / Thiêu Đốt. Chắc chắn dính (người dùng 28/11) => 1 bảo thú ném, bảo thú khác nhường. Mục tiêu đang dính (HIEUUNGDONGBANGBAOTHUs hoặc tên có "đóng băng") thì không ném.
# 9013 là mã Đóng Băng của Thương Long Quyết (Mao Sơn); bảo thú có cùng mã không thì CHƯA đo (bật IS_CHANDOANTHIEUDOTBAOTHU để đo)
HIEUUNGDONGBANGBAOTHUs = (HIEUUNGKYNANG_DONGBANG,)
KHOAGIUCHO_BAOTHUDONGBANG = "baothudongbang"
# Giữ chỗ Đóng Băng chừng này giây (đủ để hiệu ứng hiện lên mục tiêu, sau đó lọc theo hiệu ứng)
THOIGIANGIUDONGBANGBAOTHU = 3.
# Ngoài người chơi, bảo thú giang hồ dùng kỹ năng chủ động (Thiên Cân, Trói Buộc, Thiêu Đốt) lên quái có đúng tên này khi đang chọn làm
# mục tiêu (người dùng 27/11, để test boss tầng 10 / 20). So bằng (tên đã chuẩn hoá). Tầng 10 "Thập Phá Thiên Đầu Lĩnh" thấy trong log
# 354/359 27/11; tầng 20 "Nhị Thập Phá Thiên Đầu Lĩnh" người dùng xác nhận
# Thêm boss phó bản Thành Kiều (Mã Quỷ, Lương Hưng, Yến Thập Tam, Tư Tà, Thủ Lĩnh Thành Kiều) và Lăng Ly Sơn (Tướng Quân Dũng, Đường Truy,
# Thế Công Minh, Thạch Tướng Quân, Hào Quật, Cơ Quan Tướng Quân) theo BUOCLANGLYSON_MAP (tactu_langlyson_xq) để test (người dùng 27/11)
QUAIDUNGKYNANGBAOTHUs = ("Thập Phá Thiên Đầu Lĩnh", "Nhị Thập Phá Thiên Đầu Lĩnh",
                         "Mã Quỷ", "Lương Hưng", "Yến Thập Tam", "Tư Tà", "Thủ Lĩnh Thành Kiều",
                         "Tướng Quân Dũng", "Đường Truy", "Thế Công Minh", "Thạch Tướng Quân", "Hào Quật", "Cơ Quan Tướng Quân",
                         # Người dùng 27/11: Kỵ Binh Tướng Lĩnh (tên như TENKHONGPHAITINHANHs), Đoạt Bảo Mã Tặc (TENMATAC, tactu_matac_xq)
                         "Kỵ Binh Tướng Lĩnh", "Đoạt Bảo Mã Tặc")
GIANCACHKYNANGBAOTHU = 1.
# Đọc ô kỹ năng bảo thú giang hồ 27/11: 74139 "Trói Buộc" (acc 364), 74236 "Cao Cấp Trói Buộc" (acc 354)
KYNANGBAOTHU_CAOCAPTROICHAN = 74236
# Đọc ô kỹ năng bảo thú giang hồ của Kng (359) 27/11: 74137 "Từ Năng Dao Động" (Thiên Cân thường), 74136 "Thêu đốt" (game ghi sai
# chính tả, Thiêu Đốt thường), 74140 Khiêu Chiến; 74124 Nhược Ngoại, 74220 Khí Huyết Phù Trợ là bị động
KYNANGBAOTHU_THIENCAN = 74137
KYNANGBAOTHU_THIEUDOT = 74136
KYNANGBAOTHU_KHIEUCHIEN = 74140
KYNANGBAOTHU_CAOCAPTHIENCAN = 74234
KYNANGBAOTHU_XUNHPHONG = 74241
# Đọc ô kỹ năng bảo thú giang hồ acc 364 28/11: ô 5 = 74233 "Cao Cấp Thêu Đ…" (game ghi "Thêu", tên bị cắt) — khớp mã sẵn có
KYNANGBAOTHU_CAOCAPTHIEUDOT = 74233
# Đọc ô kỹ năng bảo thú giang hồ của Lầy (1451) 27/11: ô 4 = 74235 "Cao Cấp Đóng B…" (tên bị cắt). Bản thường chưa đo, nhận theo tên "Đóng"
KYNANGBAOTHU_CAOCAPDONGBANG = 74235
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
# Dung lượng túi đọc ra 1/2/3 = túi Càn Khôn đã hết hạn (client xq+0x12B8D6 vẽ cả túi là ô cấm), không phải số ô mở
DUNGLUONGTUIHETHANs = (1, 2, 3)

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
# Tự về sửa đồ (tab Hành trang): mặc định về khi có món sửa được còn dưới chừng này % độ bền
PHANTRAMVESUADO = 20
# Bản đồ quay lại sau khi về bán rác / sửa đồ (tab Hành trang, _idbandoquaylaibanrac): > 0 là id bản đồ chọn sẵn (phù tới đó, không
# có lộ trình thì bot tự dò bản đồ); THEOLOTRINH = bản đồ của điểm đánh đầu tiên (không có lộ trình thì về bản đồ lúc về);
# LUCVE = luôn về bản đồ đang đứng lúc bắt đầu về bán
BANDOQUAYLAI_THEOLOTRINH = 0
BANDOQUAYLAI_LUCVE = -1
# Mao Sơn bật "đổi đồ khi triệu hồi": trong lúc vận khí gọi bảo thú triệu hồi thì đeo "bộ đồ triệu hồi" đã ghi (thường là đồ tấn công),
# vận khí xong mặc lại bộ cũ. Bộ đồ ghi từ đồ đang mặc ở các ô trang bị này (nón, hạng liên, vũ khí, áo, yêu đới, giày, pháp bảo;
# không ngọc / cánh / ngoại trang). Loại theo ô nên không cần mô tả để biết món nào được ghi
VITRITRANGBIDOITRIEUHOIs = tuple(range(VITRITRANGBIDAUTIEN, VITRITRANGBI_PHAPBAO + 1))
# Pháp bảo đổi sang khi máu thấp (không hư hỏng), xong đeo lại pháp bảo cũ
PHAPBAOKHONGHUHONGs = ("Thượng Phương Bảo Kiếm", )
# Chiến Quốc Trân Bảo Khố (cửa hàng Kim Nguyên Bảo). Dò log [LỆNH GAME] 2026-11-13 (Aegis, acc 342/347/359/364 mua Rương Dự Trữ):
#   "buyitem"                -> máy chủ mở menu hội thoại (cửa sổ tuỳ chọn) "Bạn muốn sử dụng loại tiền tệ nào để thanh toán? ...
#                               Kim Nguyên Bảo: <ESC>R324 ... Điểm Point Auto: <ESC>B0.0", lựa chọn "buyitem paytype 1" / CLOSE
#   "buyitem paytype 1"      -> trả bằng Kim Nguyên Bảo, mở cửa sổ Trân Bảo Khố
#   "buyitem <tab>"          -> chuyển tab (1 Gói Vip, 2 Chiến Đấu, 3 Thú Nuôi, 4 Tạp Hóa, 5 VP Hỗ Trợ, 6 Hàng Hot)
#   "buyitem desc <tab> <ô>" -> xem mô tả; "buyitem <tab> <ô> <số lượng>" -> mua (ô đếm từ 0 qua các trang, 7 ô / trang)
#   Client gửi ngay sau lệnh mua "\nzip 123\n" (cùng chuỗi ở mọi acc, không có trong xq.exe: DLL ngoài thêm vào) -> bot gửi giống.
#   Đã thấy mua 50, 57, 59 cái 1 lần. Niết Bàn (9302) có thêm "buyitem ! <tab> <ô> <số lượng>" (xác nhận) ngay sau lệnh mua.
#   Aegis "buyitem ! <tab> <ô> <số lượng>" chỉ hiện hộp "Bạn quyết định mua..." (gõ thử 18/11), phải gửi tiếp "zip 123" (nút Xác Nhận)
#   mới mua; gộp 2 dòng trong 1 lệnh thì máy chủ bỏ dòng zip (thử 418, 18/11). Bot gửi "buyitem <tab> <ô> <n>", chờ gói hỏi mua rồi
#   "zip 123". Bot không mở menu "buyitem" nữa: "buyitem paytype 1" một mình đã cho số dư ở cửa sổ (thử 342, 18/11); các cửa sổ bị hook
#   đầu vòng vẽ ẩn trước khi vẽ (MoiTruong.LECHCOMUANGAM) nên mua không hiện popup
# Số KNB không lưu thành số nguyên ở TG/KDK (quét 3 acc không có ô chung), chỉ có trong lời thoại menu trên => đọc bằng "buyitem"
# Hàng KHÔNG ghi cứng ô: bot gửi "buyitem <tab>" rồi đọc gói tin hàng trong heap (MoiTruong.get_hangtranbaokho), tra ô theo tên.
# Đọc 1 lần cho mỗi phiên bản game (DatVersion trong patch.ini cạnh xq.exe, vd 2.01.10), lưu _internal/hangtranbaokho_cache.json dùng
# chung mọi nhân vật / tiến trình (quét heap mất vài giây mỗi tab). Đệm giữ nguyên suốt phiên bản (hàng mới chỉ thêm khi lên phiên
# bản, người dùng 18/11); chỉ đọc lại tab nào chưa đọc được. Trước khi "zip 123" đọc tên món trong gói hộp hỏi mua: khác món thì không
# mua và xoá đệm phiên bản (cách kiểm đệm duy nhất)
TABTRANBAOKHOs = (1, 2, 3, 4, 5, 6)
# Lệnh bot gửi mà máy chủ trả menu hội thoại (cửa sổ tuỳ chọn): sau lệnh này THOIGIANMENUNGAM giây hook đầu vòng vẽ ẩn menu trước khi
# vẽ (người dùng 2026-11-18 không muốn popup che màn hình lúc đang thao tác; menu người dùng tự bấm NPC ngoài khoảng này vẫn hiện).
# Lời thoại / lệnh / nhãn vẫn đọc được trong bộ nhớ. Dấu "menu đang mở ngầm" quá THOIGIANDAUMENUNGAM giây mà bot chưa đóng thì bỏ
CAULENHMOMENUs = ("look ", "tallk ", "talk ", "pf2 908", "pf 4181", "pf2 61", "dGludmF0 ", "desc revive")
THOIGIANMENUNGAM = 4.
THOIGIANDAUMENUNGAM = 30.
CAULENHXACNHANTRANBAOKHO = "zip 123"
# Trân Bảo Khố là cửa hàng KNB mở bằng lệnh, KHÁC NPC kho "Bảo Khố" (mở rương kho đồ, lệnh pawn) - đừng nhầm.
# Ô "NPC bán" của bảng Mua bù (tab Hành trang) ghi tên này = mua ở Trân Bảo Khố bằng KNB, ở đâu cũng mua, không chạy về Tân Thủ Thôn
TRANBAOKHO = "Trân Bảo Khố (Kim Nguyên Bảo)"
# Xét lại hàng Trân Bảo Khố mỗi chừng này giây (mỗi lần mua phải gửi "buyitem" đọc KNB, bật menu); KNB không đủ thì chờ lâu mới đọc lại
GIANCACHKIEMTRAMUATRANBAOKHO = 30.
THOIGIANCHOKHONGDUKNB = 1800.
# Mỗi lệnh mua tối đa (đã thấy 59 cái 1 lần, giữ 50 cho chắc)
SOLUONGMUATRANBAOKHOTOIDA = 50
# Kỵ thú quý (Thỏ 342 đeo Kỵ Thú Tiểu Quai, 2026-11-13): luôn GIỮ dù luật túi đồ nói bán / vứt / cất kho, Sắp xếp hành trang đặt ở ô mở
# áp chót (ô cuối dành cho bảo thú vật phẩm), chưa đeo thì tự "use <id>#". Không có ô trang bị riêng: món vẫn nằm trong túi (đã
# Phong Ấn), đang đeo hay không đọc ở nhân vật +0x1198 (MoiTruong._get_idthucuoi: Thỏ đang đeo = 1, acc không có kỵ thú = 0)
KYTHUGIUs = ("Kỵ Thú Tiểu Quai", )
# Đã "use" kỵ thú mà sau chừng này giây +0x1198 vẫn 0 là lần đó không ăn; hỏng liên tiếp SOLANDEOKYTHUTOIDA lần thì nghỉ
# THOIGIANNGHIDEOKYTHU giây (phòng trường hợp +0x1198 không phải cờ đeo, use đi use lại thành đeo / tháo liên tục)
THOIGIANCHODEOKYTHU = 5.
SOLANDEOKYTHUTOIDA = 3
THOIGIANNGHIDEOKYTHU = 600.

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
# Người chưa vào phái: "desc user" in "Môn phái: -", bot lưu / hiện tên này
TENVOMONPHAI = "Vô Môn Phái"

# Vân Mộng Cốc buff đồng đội cùng máy theo môn phái: chỉ Ngân Châm Độ Ách hoặc chỉ Kim Châm Độ Ách.
# Môn phái không có trong 2 danh sách (hoặc không biết vì khác máy) thì buff cả hai như cũ
# Môn phái dùng chiêu phép thuật: bị Trầm Mặc thì không dùng được kỹ năng (vẫn đánh thường, di chuyển được)
# Dính Trận Pháp Lạc Ảnh (hiệu ứng HIEUUNGKYNANG_DAOHOALACANH, ~13s) thì không ra khỏi được chừng 3 ô quanh NGƯỜI DÙNG CHIÊU
# (đo 2026-10-26, Thọ nhốt 30: bị giữ ở cách Thọ 2-2.8 ô, có lần cách chỗ bị dính tới 4.5 ô): đích di chuyển ngoài bán kính này
# quanh tâm trận bị kéo về mép trận. Tâm trận = người chơi ngoài nhóm trong KHOANGCACHTIMNGUOIDUNGTRANDO ô lúc vừa bị dính, ưu tiên người đánh tay không (Đào Hoa Nguyên) rồi tới người gần nhất
BANKINHTRANDOLACANH = 2.5
# Trận Lạc Ảnh trên mặt đất (MoiTruong.get_danhsachtranlacanh) là 2 nút hiệu ứng đất cùng tâm, mã 21151 và 21152 (không phải 2115).
# Đo 2026-11-10 00:54 (trận vàng ở (169,175), cả 5 cửa sổ gần đó cùng thấy, cờ +0x18 = 2, +0x1C = 0; tồn tại ~16s rồi xoá hẳn)
MAHIEUUNGDATLACANHs = (21151, 21152)
KHOANGCACHTIMNGUOIDUNGTRANDO = 4.
# Tầm dùng Đào Hoa Lạc Ảnh (người dùng dặn 2026-11-12: không nhất thiết phải cận chiến): trận đặt tâm tại người dùng chiêu, nhốt người
# trong ~BANKINHTRANDOLACANH ô (đo bị giữ ở 2-2.8 ô) => mục tiêu cách mình (đường thẳng, math.dist) tới chừng này là dính. Trừ hao
# 0.5 ô cho lệch toạ độ client - máy chủ và mục tiêu đang chạy ra. Không dùng max(|dx|,|dy|): ô chéo (2,2) đã cách 2.83 > bán kính trận
KHOANGCACHSUDUNGLACANH = BANKINHTRANDOLACANH - 0.5

MONPHAIPHEPTHUATs = ("vanmongcoc", "maoson", "conluan")

MONPHAICHIBUFFNGANCHAMs = ("daohoanguyen", "camvequan", "duongmon")
MONPHAICHIBUFFKIMCHAMs = ("vanmongcoc", "maoson", "conluan")
# Mao Sơn: Ám Ma Nhập Thể chỉ dùng lên người chơi các phái này (biết phái qua "desc user", chưa biết thì hỏi rồi bỏ qua lượt đó)
MONPHAIAMMANHAPTHEs = ("camvequan", "vanmongcoc", "conluan")
# Thục Sơn thì theo vũ khí đang đeo: LOAIVUKHITHUCSONCHIBUFF... (đặt cạnh IDLOAIVUKHI_*)
# Bảo thú triệu hồi (tên bắt đầu bằng): Cương Thi / Thiên Binh / Thiên Tướng / Đậu Binh không cần Kim Châm, Quỷ Tốt không cần Ngân Châm
# (Đậu Binh thêm theo người dùng 2026-11-26). Bảo thú giang hồ không buff cả hai (xử lý ở tactu_muctieu)
BAOTHUCHIBUFFNGANCHAMs = (CUONGTHI, THIENBINH, THIENTUONG, DAUBINH)
BAOTHUCHIBUFFKIMCHAMs = (QUYTOT,)

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
BANDO_KHONMATRAN1 = 291
BANDO_KHONMATRAN2 = 292
BANDO_KHONMATRAN3 = 293
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
# Phó bản mượn ID bản đồ ngoài, nhận ra qua đầu tên bản đồ game (tên chỉ 20 byte nên bị cắt): Phong Yêu Kính "Phó Bản Phong Y" (ID 1 bản đồ ngẫu nhiên, không bao giờ là Tân Thủ Thôn / quốc gia; vd 133
# như Thần Bí Động 1), Tập Kích Môn Phái "Tập Kích Môn Ph" (ID 151 như Kênh Trịnh Quốc 1). Lộ trình nạp trong đó ra ngoài là tự bỏ
# Chỉ "Phó Bản Phong", không để "Phó Bản": vào Lăng Ly Sơn tên đổi thành "Phó Bản Lăng Ly" trước, ID còn Thuý Hoa Sơn vài giây => tưởng
# kẹt trong phó bản mượn bản đồ, Tín Vật bỏ dở việc vào (Kng 2026-11-09 01:16:05)
TIENTOTENPHOBANMUONBANDOs = ("Phó Bản Phong", "Tập Kích Môn", "Chiến Quốc Tr")
# Đầu tên bản đồ Phong Yêu Kính (Aegis "Phó Bản Phong Y", Niết Bàn "Chiến Quốc Tr..."). Cổng của bản đồ thật mượn ID không có tác dụng
# trong đó (người dùng): không né vùng cấm quanh cổng
TIENTOTENBANDOPHONGYEU = ("Phó Bản Phong", "Chiến Quốc Tr")
# Đầu tên bản đồ Tập Kích Môn Phái: gom quái tới khi mọi con thấy được đều đã gom 1 lần mới dừng đánh
TIENTOTENBANDOTAPKICHMONPHAI = "Tập Kích Môn"
# Tên bản đồ thật ID 151: Niết Bàn đặt tên phó bản Tập Kích khác, ở ID 151 mà tên không bắt đầu bằng chữ này thì là Tập Kích
TIENTOTENBANDOKENHTRINHQUOC = "Kênh Trịnh"
# Vừa ra khỏi phó bản mượn ID bản đồ ngoài (Phong Yêu Kính): chờ chừng này giây mới tự chọn lộ trình mẫu (ID bản đồ đổi sau tên)
THOIGIANCHONAPLOTRINHROIPHOBAN = 1.5
# Vừa ra khỏi phó bản mượn ID: ID đọc được còn là ID mượn (Thanh Khê 1...) thì chờ tối đa chừng này giây, không tìm đường / Hồi Thành Phù
# (ra Phong Yêu Kính là về Chu Quốc, tưởng đang ở Thanh Khê nên Tín Vật về phái rồi Xa Phu - QuanSuMuMuu 2026-11-04 07:40)
THOIGIANCHOIDROIPHOBANMUON = 8.
# Đã đổi sang ID bản đồ thật: chờ thêm chừng này giây cho toạ độ / tên ổn định
THOIGIANCHOSAUROIPHOBANMUON = 2.
# Số hành động gần nhất giữ lại (cũng là số dòng bảng Lịch sử hành động cuối tab Khác)
SOLICHSUHANHDONG = 20

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
# Đang ở Chu Quốc thì cất kho ở đây luôn (Quản Khố Chu Quốc), không Hồi Thành Phù về Tân Thủ Thôn. Trước đây cất qua Chủ Tiệm Sửa
# Chữa (234, 185): log 364 2026-11-14 08:51 cất được rương 1 rồi không mở được rương 2, báo "kho đầy (1 rương)" => đổi sang Quản Khố
# (người dùng chỉ 286, 150; vitridoituong ghi 286, 151)
X_KHO_CHU = 286
Y_KHO_CHU = 150
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
BANDO7QUOCGIAs = (BANDO_TEQUOC, BANDO_HANQUOC, BANDO_TRIEUQUOC, BANDO_NGUYQUOC, BANDO_TANQUOC, BANDO_SOQUOC, BANDO_YENQUOC, )

BANDO_CULOC = 131

BAOTHUVATPHAMs = (SONGTUDUNGCAM, SONGTUANHMINH, THANTHUTHO, THANTHUTHIN, THANTHUMAYET, THANTHUDAN, THANTHUSUU, THANTHUDAN2, THANTHUSUU2, THANTHUCHUOT, CONGIAPCHUOT, *THUYBINHs)
# Tên chỉ số trên bảng Nhân Vật -> các ô trong khối điều khiển (KDK + dich; cặp thấp / cao), đối chiếu bảng Nhân Vật của Thọ 2026-11-02.
# Bảo thú vật phẩm ghi trong mô tả chỉ số cộng cho chủ ("tăng 7% Ngoại Công cho chủ nhân", "gia tăng cho chủ nhân 7% Bạo Kích")
CHISONHANVAT_MAP = {
    "Khí Huyết": (0x1530,),
    "Ngoại Công": (0x153C, 0x1550),
    "Ngoại Kháng": (0x1540, 0x1554),
    "Thân Thủ": (0x1544,),
    "Nội Công": (0x1548, 0x1558),
    "Nội Kháng": (0x154C, 0x155C),
    # Bạo Kích x 100 (901 = 9.01%); Thần Thú - Dần cộng đúng 700
    "Bạo Kích": (0x15BC,),
}
# Bảo thú vật phẩm mà mô tả không ghi chỉ số ("Sau khi triệu hồi sẽ tăng thêm năng lực của chủ nhân"): chỉ số cộng cho chủ khai tay.
# 12 con Giáp - Chuột tăng cả Ngoại / Nội Công / Kháng (người dùng báo 2026-11-02); theo dõi Ngoại + Nội Công vì Đào Hoa tự làm Kháng chớp.
# Thần Thú - Chuột cũng tăng cả 4 chỉ số, mô tả không ghi chỉ số nên bot báo "chưa biết chỉ số" (người dùng báo 2026-11-05)
# Song Tử Anh Minh (nhặt ở Phong Ấn, hạn 7 ngày, người dùng gửi mô tả 2026-11-21): "Khi được triệu hồi, sẽ giúp chủ nhân gia tăng
# thêm 5% Ngoại Kháng, 5% Nội Kháng, 5% Khí Huyết, 5% Bạo Kích, 5% Ngoại Công, 5% Nội Công". Tự đọc mô tả sẽ lấy Ngoại Kháng
# (đứng đầu) mà Đào Hoa tự làm Kháng chớp => khai tay theo dõi Ngoại + Nội Công như con Chuột.
# Thần Thú - Ma Yết (nhặt ở Phong Ấn, người dùng gửi mô tả 2026-11-24): "sau khi triệu hồi tăng 10% Ngoại Công và 10% Nội Công cùng
# 2% Bạo Kích cho chủ nhân". Tự đọc mô tả chỉ lấy Ngoại Công (đứng đầu) => khai tay Ngoại + Nội Công cho dấu vân tay chắc hơn;
# không theo dõi Bạo Kích vì chưa đo ô Bạo Kích có đổi theo chiêu (Phản Tỏa Đào Hoa chí mạng 100%) hay không.
CHISOBAOTHUVATPHAM_MAP = {
    THANTHUMAYET: ("Ngoại Công", "Nội Công"),
    SONGTUANHMINH: ("Ngoại Công", "Nội Công"),
    CONGIAPCHUOT: ("Ngoại Công", "Nội Công"),
    THANTHUCHUOT: ("Ngoại Công", "Nội Công"),
}
# Danh sách nhặt (VATPHAMKHONGNHATs / VATPHAMUUTIENNHATs / VATPHAMTUDONGNHATs / VATPHAMTUDONGNHATFARMs) đã chuyển thành luật nhặt
# trong luattuido_xq.NHATMACDINH (sửa ở tab Hành trang)

DUAHAU = "Dưa hấu"
LAOTUU = "Lão Tửu"
THUONGPHUONGBAOKIEM = "Thượng Phương Bảo Kiếm"
CHUONGHAMTHIEN = "Chuông Hám Thiên"
TUIPHAPBAO = "Túi Pháp Bảo"
CHIENQUOCLENH = "Chiến Quốc Lệnh"
CUULONGTHANHOATRAO = "Cửu Long Thần Hỏa Trảo"
# Đổi pháp bảo theo sinh lực (tuỳ chọn "Đổi pháp bảo theo sinh lực", tab Chiến đấu): 3 mức cao / vừa / thấp, mỗi mức là các
# cách viết tên của cùng món (Trảo có bản "Hoả"). Khoá theo NHÓM chứ không theo từng phái (người dùng 2026-11-26: các phái
# dùng chung nhau): Đào Hoa riêng, còn lại chia Nội công / Ngoại công (tactu_vatpham_xq._laynhomphapbaotheomau).
# - Đào Hoa Nguyên (người dùng 2026-11-12): >= 50% Nhiếp Hồn Linh, 25-50% Cửu Long Thần Hỏa Trảo, <= 25% Thượng Phương Bảo Kiếm
# - Nội công (Thục Sơn Kiếm 2026-11-12, Vân Mộng Cốc 2026-11-13): mức cao Chuông Hám Thiên thay Nhiếp Hồn Linh, hai mức dưới như Đào Hoa
# - Ngoại công: như Đào Hoa (Nhiếp Hồn Linh) nhưng không có Dã Tính nên mức thấp luôn tháo
# Mức thấp thực tế là tháo pháp bảo; món mức thấp ở bảng chỉ đeo khi Đào Hoa đang Dã Tính Cuồng Lực (không tháo được)
PHAPBAOTHEOMAU_TRAO = (CUULONGTHANHOATRAO, "Cửu Long Thần Hoả Trảo")
NHOMPHAPBAO_DAOHOA = "daohoanguyen"
NHOMPHAPBAO_NOICONG = "noicong"
NHOMPHAPBAO_NGOAICONG = "ngoaicong"
PHAPBAOTHEOMAU_MAP = {
    NHOMPHAPBAO_DAOHOA: ((NHIEPHONLINH, ), PHAPBAOTHEOMAU_TRAO, (THUONGPHUONGBAOKIEM, )),
    NHOMPHAPBAO_NOICONG: ((CHUONGHAMTHIEN, ), PHAPBAOTHEOMAU_TRAO, (THUONGPHUONGBAOKIEM, )),
    NHOMPHAPBAO_NGOAICONG: ((NHIEPHONLINH, ), PHAPBAOTHEOMAU_TRAO, (THUONGPHUONGBAOKIEM, )),
}
# Bản "Cao Cấp" của pháp bảo trong bảng trên (vd "Chuông Hám Thiên Cao Cấp": chỉ số cao hơn nhưng đeo là mòn độ bền theo thời
# gian). Người dùng 2026-11-26: chỉ đeo khi đang bật PK (ưu tiên hơn bản thường cùng mức); không bật PK thì đổi về bản thường.
# Tên hành trang bị cắt 31 byte nên đuôi có thể cụt ("... Cao C"): khớp theo tên gốc + phần đầu của đuôi này
PHAPBAOCAOCAP = "Cao Cấp"
TENNHOMPHAPBAO_MAP = {NHOMPHAPBAO_DAOHOA: "Đào Hoa Nguyên", NHOMPHAPBAO_NOICONG: "Phái Nội công", NHOMPHAPBAO_NGOAICONG: "Phái Ngoại công"}
# Ngưỡng mặc định (chỉnh ở giao diện, lưu theo nhân vật): máu < VUA% xuống mức vừa, <= THAP% xuống mức thấp.
# Ngưỡng tụt và ngưỡng hồi phải cách nhau, không thì máu dao động quanh 50% / 25% là đổi pháp bảo liên tục
# (người dùng báo 2026-11-12): đang đeo mức thấp hơn thì phải hồi lên ngưỡng + DOTRE% mới đổi lên (mặc định 75% / 50%)
NGUONGPHAPBAOTHEOMAU_VUA = 50
NGUONGPHAPBAOTHEOMAU_THAP = 25
DOTREPHAPBAOTHEOMAU = 25
# Nhánh đổi lên thứ hai (người dùng 2026-11-15): máu ở trên ngưỡng của mức cao hơn liên tục chừng này giây thì đổi lên luôn,
# không cần hồi tới ngưỡng + độ trễ. Đào Hoa Dã Tính giữ máu ~35% (không ai hồi) thì cách cũ (phải lên 50%) gần như không đổi lại Trảo
THOIGIANONDINHDOIPHAPBAO = 5.
# Nhánh trên chỉ tính khi máu cao hơn ngưỡng ít nhất chừng này %: đổi Kiếm <-> Nhiếp Hồn Linh làm khí huyết tối đa đổi, % máu
# nhảy ~2% (log 347 2026-11-20: Kiếm 26% -> Nhiếp Hồn Linh 24% -> Kiếm... liên tục khi máu đứng yên sát 25%)
BIENDOONDINHDOIPHAPBAO = 5
# Vân Mộng Cốc / Tiên Khí hồi máu đồng đội (tab Chiến đấu, lưu theo nhân vật hồi máu): máu <= NGUONGBOMMAUDONGDOI% thì hồi;
# Đào Hoa đang Dã Tính Cuồng Lực (cố ý giữ máu thấp để tăng Ngoại Công) chỉ hồi khi <= NGUONGBOMMAUDATINH%, trừ khi mình đang bật PK
# thì dùng ngưỡng thường (người dùng 2026-11-13, đưa vào cấu hình 2026-11-15)
NGUONGBOMMAUDONGDOI = 75
NGUONGBOMMAUDATINH = 35
# Pháp bảo đang đeo: "desc 7" lại mỗi chừng này giây để biết đã hỏng (độ bền 0/x) chưa, hỏng thì đổi món tương tự trong túi.
# 30s là chậm khi luyện đơn (Lư mòn nhanh, người dùng báo 2026-11-12); mô tả ô trang bị chỉ giữ ~10s rồi bị xoá nên đọc ngay lượt sau
THOIGIANKIEMTRADOBENPHAPBAO = 10.
# Món trong túi desc không ra mô tả: chờ chừng này giây mới thử lại
THOIGIANTHULAIDOBENPHAPBAOTUI = 30.
# Xoay vòng Cửu Long Thần Hỏa Trảo theo khí huyết (người dùng dặn 2026-11-14). Trảo có thanh "Khí Huyết: 100 / 600" riêng
# (hấp thụ 75% sát thương), chỉ hồi khi đang đeo:
# - Đang đánh: Trảo đang đeo hết khí huyết (0/x) thì đeo Trảo khác trong túi còn khí huyết nhiều nhất
# - Nghỉ (bản đồ BANDOKHONGPKs, không có mục tiêu quá THOIGIANNGHIXOAYTRAO giây): đeo Trảo chưa đầy (ít nhất) cho nó tự hồi,
#   Trảo đang đeo đầy thì đổi sang Trảo chưa đầy khác
# Đang đeo Trảo thì "desc 7" dày hơn (THOIGIANKIEMTRAKHIHUYETTRAO) để biết sớm lúc hết khí huyết / đã đầy
THOIGIANNGHIXOAYTRAO = 15.
THOIGIANKIEMTRAKHIHUYETTRAO = 5.
# Ô "hết Trảo đeo mức cao": đang đeo món khác thì Trảo trong túi phải còn ít nhất chừng này khí huyết mới đổi lại Trảo
# (Trảo nằm trong túi KHÔNG BAO GIỜ hồi khí huyết, chỉ hồi khi đeo - người dùng 2026-11-19. Trảo tháo ra lúc còn vài điểm
# mà đeo lại thì hết ngay rồi lại đổi => lật Trảo / Nhiếp Hồn Linh liên tục, log 342 2026-11-19)
KHIHUYETTRAOTOITHIEUDEOLAI = 100
# Thưởng code tân thủ dùng bằng "use2 <id>#" (lệnh nút Xác Nhận của hộp hỏi), không cần "use" trước (người dùng dặn 2026-11-01)
VATPHAMDUNGUSE2s = (CUULONGTHANHOATRAO, "Cửu Long Thần Hoả Trảo", "Hoàng Sa Chi Tâm", *THUYBINHs)
TINHNGUYENDON = "Tinh Nguyên Đơn"
# Tự ép Tinh Nguyên Đơn vào bảo thú giang hồ tới khi bảng "Kỹ năng chiến đấu" có chừng này kỹ năng (bất kỳ, không tính kỹ năng sẵn có ô 0), mỗi lần cách THOIGIANEPTINHNGUYENDON giây
# để đọc lại số kỹ năng; ép EPTINHNGUYENDONTOIDAKHONGTANG lần liền không tăng thì ngưng con đó (người dùng 2026-11-25)
SOKYNANGBAOTHUEPTINHNGUYENDON = 5
THOIGIANEPTINHNGUYENDON = 3.
EPTINHNGUYENDONTOIDAKHONGTANG = 3
# Tinh Nguyên Đơn kỹ năng chuẩn => chừa lại, không tự ép (người dùng 2026-11-25). So không phân biệt hoa thường, gộp khoảng trắng.
# - TINHNGUYENDONGIUs: mô tả chứa chữ này là giữ
# - TINHNGUYENDONGIU_CHISO5s: mô tả có chỉ số này tăng 5%. Mô tả thật (ảnh người dùng 2026-11-25): "Bao gồm kỹ năng:Khí Huyết Phù Trợ
#   Kỹ năng của Bảo thú, Sau khi triệu hồi, Khí Huyết của chủ nhân gia tăng 5%, ..." => không có chuỗi "5% Khí Huyết"; so "<chỉ số>
#   ... 5%" (cách nhau tối đa 40 ký tự, không qua dấu phẩy / chấm) hoặc "5% <chỉ số>"
# Tên đúng trong game là "Từ Năng DAO Động" (ảnh người dùng 2026-11-25); trước ghi "Giao" nên không khớp, đã ép mất 2 viên xanh (347, 354).
# Giữ cả "Giao" phòng bản khác. "Từ Năng Dao Động" đã gồm cả bản Cao Cấp
# Người dùng 27/11: giữ thêm Thiêu Đốt (game ghi "Thêu đốt", ô kỹ năng Kng 359) và Trầm Mộng Thuật
TINHNGUYENDONGIUs = ("Từ Năng Dao Động", "Từ Năng Giao Động", "Thêu Đốt", "Thiêu Đốt", "Trầm Mộng Thuật")
TINHNGUYENDONGIU_CHISO5s = ("Khí Huyết", "Ngoại Công", "Nội Công", "Ngoại Kháng", "Nội Kháng")
# - Tên vàng (mã màu \x1bY, vd Cao Cấp Từ Năng Giao Động) không bao giờ tự ép; TINHNGUYENDONGIU_KYNANGs: tên kỹ năng ngay sau
#   "Bao gồm kỹ năng:" (Phục Sinh tên xanh - ảnh người dùng 2026-11-25)
TINHNGUYENDONGIU_KYNANGs = ("Phục Sinh",)
HOIBANGPHU = "Hồi Bang Phù"
NGUYENLIEULUYENDONs = ("Hoàng Kỳ", "Cúc Dại", "Dã Cúc", "Quả Anh Túc", "Điền Thất", "Táo Đỏ", "Trần Bì", "Dương Kim Hoa", "Linh Chi Thảo", "Sơn Sâm", "Cát Cánh", "Cam Thảo", "Sinh Địa", "Xuyên Tâm Liên", "Hoàng Liên", "Hà Thủ Ô", "La Hán Quả", "Bạch Kỳ", "Đương Quy", "Xuyên Bối", "Đông Trùng Thảo")
CUONGTHIPHU = "Cương Thi Phù"
# Danh sách không bán (VATPHAMKHONGBANs) đã chuyển thành luật Giữ mặc định trong luattuido_xq.LUATMACDINH (sửa ở tab Hành trang)

# Tự động khai khoáng / Hái dược: nhận biết đang làm gì theo tên pháp bảo đang đeo (có "Liềm" = hái dược, có "Cuốc" = khai khoáng).
# Hái dược: tìm đối tượng tên trong NGUYENLIEULUYENDONs; khai khoáng: đối tượng tên chứa "Khoáng" (Thiết / Ngân / Tích Khoáng...).
# Không đeo cả hai (vd đang đổi sang pháp bảo không hư hỏng lúc máu thấp) thì giữ loại nhận biết lần trước; chưa nhận biết lần nào thì tìm cả hai.
PHAPBAOHAIDUOC = "Liềm"
PHAPBAOKHAIKHOANG = "Cuốc"
CHUTENKHOANG = "Khoáng"
# Khai khoáng (hái dược) ở các bản đồ này thì tự vứt các dược không cần (dù có luật Giữ)
BANDOHAIDUOCs = (261, 262, 263)
VATPHAMVUTKHIHAIDUOCs = ("La Hán Quả", "Hoàng Liên", "Hà Thủ Ô", "Xuyên Tâm Liên")
# Khai khoáng: cách khoáng dưới KHOANGCACHDAOKHOANG ô (đường thẳng) thì đứng "look" để đào, xa hơn thì đi tới (đường bot tự tìm theo lưới
# vật cản, dừng cách khoáng KHOANGCACHDUNGDAOKHOANG ô vì ô khoáng có thể là vật cản). Trước khi đi tìm đường 1 lần: không có đường / phải
# vòng quá xa (HESODUONGVONGTOIDA như quái) thì bỏ khoáng đó, không chạy thử 10s rồi mới báo "Khoáng lỗi" như trước.
# Chỉ tính giờ khi bot đang thật sự đi tới khoáng (đánh quái / nhặt đồ chen vào thì dừng đồng hồ): THOIGIANKHONGGANKHOANG giây không gần
# thêm KHOANGCACHGANTHEMKHOANG ô => bỏ. Đứng trong tầm gửi SOLANLOOKKHOANGTOIDA lần "look" mà không vào vận khí (lúc đào không đổi tư thế,
# chỉ có vận khí - người dùng xác nhận 2026-11-10) => bỏ.
# Khoáng bị bỏ thì THOIGIANBOQUAKHOANG giây sau mới xét lại
KHOANGCACHDAOKHOANG = 6.
KHOANGCACHDUNGDAOKHOANG = 4.
THOIGIANKHONGGANKHOANG = 8.
KHOANGCACHGANTHEMKHOANG = 1.
SOLANLOOKKHOANGTOIDA = 6
THOIGIANBOQUAKHOANG = 30.
THOIGIANNHODUONGKHOANG = 20.
# Đứng trong tầm hái: giữ đứng yên + khoá kỹ năng THOIGIANGIUKHAIKHOANG giây (làm mới mỗi lượt) để look kịp vào vận khí, không quay ra
# đánh quái (người dùng báo 2026-11-10: bật đánh quái thì chạy tới khoáng chưa look xong đã chạy ngược lại đánh)
THOIGIANGIUKHAIKHOANG = 1.5

# Xếp chồng tự nhận biết (món có số lượng >= 1 trong hành trang), 1 ô tối đa = số lớn nhất từng thấy (ít nhất 30);
# món có số tối đa khác thì ghi ở đây
# 1 ô hành trang chồng tối đa bao nhiêu món (game nâng từ 30 lên 100); món nào khác mức này thì ghi riêng vào SOLUONGXEPCHONGTOIDA_MAP
SOLUONGXEPCHONGMACDINH = 100
SOLUONGXEPCHONGTOIDA_MAP = {
}

# Làm mới toạ độ trước khi bắn xa (TacTu.action_lammoitrangthai): chọn danh hiệu ("title show <mã>") hoặc ẩn danh hiệu ("title hide")
# làm máy chủ gửi lại trạng thái nhân vật => client cập nhật toạ độ thật. Chọn ở giao diện theo nhân vật, mặc định không dùng
DANHHIEULAMMOI_KHONG = ""
DANHHIEULAMMOI_AN = "hide"
# Hiện thông tin ước lượng mục tiêu đang chọn ngay trong game (danhhieumuctieu_xq): tắt / ghi đè danh hiệu (+0x1134) / nối vào đuôi tên
# (+0x10AC). Bật theo từng cửa sổ ở đầu tab Chiến đấu
CHEDOHIENMUCTIEU_TAT = ""
CHEDOHIENMUCTIEU_DANHHIEU = "danhhieu"
CHEDOHIENMUCTIEU_TEN = "ten"
# Mã màu chữ của game: ESC + 1 chữ cái, bảng ở hàm vẽ chữ xq+0x892BE (dò file xq.exe 2026-11-05, màu 0xRRGGBB): B 0000FF, C 00FFFF,
# G 00FF00, K 7F7F7F, M FF00FF, N màu mặc định, R FF0000, W FFFFFF, Y FFFF00, b 00007F, c 007F7F, g 007F00, m 7F007F, p F076FC,
# r 7F0000, w BFBFBF, y 7F7F00. "Theo % máu" (MAUHIENMUCTIEU_THEOMAU): phần Khí Huyết xanh lá / vàng / đỏ theo NGUONGMAUHIENMUCTIEU, còn lại trắng
MAUHIENMUCTIEU_THEOMAU = "*"
# "Mặc định" (trước là "Theo % máu", giữ mã "*"): dòng bang + phái người chơi tô MAUBANGTRENDAU / MAUPHAITRENDAU; màu khác thì cả dòng 1 màu
MAUHIENMUCTIEU_MAP = {"Mặc định": MAUHIENMUCTIEU_THEOMAU, "Trắng": "W", "Xanh lơ": "C", "Vàng": "Y", "Xanh lá": "G", "Đỏ": "R",
                      "Hồng": "p", "Tím": "M", "Xám nhạt": "w"}
# % máu: > ô đầu xanh lá, > ô sau vàng, còn lại đỏ
NGUONGMAUHIENMUCTIEU = (60, 30)
# Hook vẽ thêm dòng trên danh hiệu (MoiTruong.action_thietlaphookvedanhhieu): số dòng tối đa, byte mỗi dòng, khoảng cách dòng (px,
# game vẽ tên ở y - 0x0E, danh hiệu ở y - 0x1C => 14)
SODONGVEDANHHIEU = 4
KICHTHUOCDONGVEDANHHIEU = 0x80
KHOANGCACHDONGCHU = 14
# Số đối tượng hook vẽ thêm dòng cùng lúc: ô 0 (trước là mục tiêu đang chọn, giờ không dùng), ô 1 nhân vật mình (hành động hiện tại của
# bot, danhhieumuctieu_xq.ODauNhanVat), từ ô OKHOINGUOICHOIDAU: SOKHOINGUOICHOI người chơi xung quanh (bang + môn phái, người dùng yêu
# cầu 2026-11-27 thay cho Kết luận / Khí huyết / Công / Kháng của mục tiêu). Hook so lần lượt từng ô mỗi lần vẽ danh hiệu (rẻ)
SOKHOINGUOICHOI = 40
OKHOIMUCTIEU = 0
OKHOINHANVAT = 1
OKHOINGUOICHOIDAU = 2
SODOITUONGVEDANHHIEU = OKHOINGUOICHOIDAU + SOKHOINGUOICHOI
# Dòng bang + môn phái trên đầu người chơi: màu tên bang, màu môn phái, màu dấu ngăn / "?" chưa biết
MAUBANGTRENDAU = "Y"
MAUPHAITRENDAU = "C"
MAUPHUTRENDAU = "w"
# Màu dòng hành động hiện tại trên đầu nhân vật mình (mã màu game ở trên), tô từng phần như khối 📢 của giao diện: tên việc trước ": ",
# tên đối tượng sau động từ ("Tấn công <tên>", "Đi theo <tên>"), chữ thường, số đếm đủ / còn thiếu ("21/28"), toạ độ "(149, 158)",
# tên bản đồ sau "ở "
MAUHANHDONGTRENDAU = {"dau": "C", "doituong": "Y", "thuong": "W", "du": "G", "thieu": "Y", "toado": "w", "bando": "p"}
# Đang tắt Foxia nhân vật này (TacTu._is_tatbot, nút Tắt trên bảng điều khiển): thay dòng hành động bằng câu này, màu đỏ, hiện cả khi
# tắt ô "Hiện hành động trên đầu" để nhìn trong game biết ngay nhân vật nào đang tắt (người dùng yêu cầu 2026-11-12)
CHUTATFOXIATRENDAU = "Đang tắt Foxia"
MAUTATFOXIATRENDAU = "R"
KICHTHUOCKHOIVEDANHHIEU = 8 + SODONGVEDANHHIEU * KICHTHUOCDONGVEDANHHIEU
# Vùng mã hook; 0x10 byte cuối: dấu hiệu + 5 byte gốc ở chỗ hook (lần chạy bot sau lấy lại, không nối chồng)
KICHTHUOCKICHBANVEDANHHIEU = 0x200
DAUHIEUKICHBANVEDANHHIEU = b"XQDH"
# Hook "bật Alt, ô túi hiện nhãn riêng từng ô thay cho tên" (MoiTruong.action_thietlaphookdaumautui). Vùng mã mỗi chỗ hook:
# +0x00 mã nhánh trắng, +0x40 mã chỗ định dạng, +0x60 địa chỉ bảng nhãn (4 byte), +0x70 dấu hiệu & 5 byte gốc, +0x80 mã dời toạ độ.
# Bảng nhãn: mỗi ô KICHTHUOCNHANOTUI byte chữ UTF-8 kết thúc 0 (bot ghi, MoiTruong.action_capnhatnhanotui); game dùng làm chuỗi
# định dạng ("%" phải ghi "%%") rồi in, tô màu theo phẩm chất, góc trên trái ô, hiểu "\n" (dòng cao 10 px).
# Người dùng 23/11: bỏ hẳn dấu chấm, chữ tô màu phẩm chất là đủ: trang bị "Cấp 85", đá "Cấp 2" (từ tên), pháp bảo độ bền
# còn / tối đa, thuốc lượng hiệu quả ("15%", "1400"); món khác không vẽ gì.
KICHTHUOCKICHBANDAUMAUTUI = 0xA0
DAUHIEUKICHBANDAUMAUTUI = b"XQD3"
# Dấu hiệu các bản cũ (XQDM chuỗi dấu cố định; XQD2 bảng nhãn chưa dời lề): gặp thì đặt đè bằng bản mới
DAUHIEUKICHBANDAUMAUTUICUs = (b"XQDM", b"XQD2")
# Chữ vẽ sát mép trên trái ô (ảnh người dùng 23/11) => dời mọi lần vẽ chữ của ô (chữ + bóng) thêm x / y px
LEXNHANOTUI = 3
LEYNHANOTUI = 2
# Lượng hiệu quả của thuốc trong mô tả ［Có thể sử dụng］ (đọc 23/11): "khôi phục 1400 điểm khí huyết" (Cấp Cứu Đơn), "hồi phục 1850
# điểm Khí Huyết" (Thí Luyện Quả), "gia tăng 15％ Khí Huyết" (Khí Mạch Đơn), "gia tăng lên 8％ Ngoại Công" (Tiêu Dao Tán), "Nâng cao
# 5％ Ngoại Kháng" (Xá Lợi Tử), "gia tăng 600 Khí Huyết" (Nhân Sâm), "khôi phục 2000 điểm lực pháp lực" (Phục Dược). Không khớp
# Thần Thú ("tăng 7%", "gia tăng cho chủ nhân"), Song Tử ("gia tăng thêm"), tiềm năng, sát thương. Nhóm 1 = số, nhóm 2 = có %
MAUHIEUQUATHUOC = (r"(?:khôi phục|hồi phục|gia tăng(?: lên)?|nâng cao)\s*(\d+)\s*([％%])?\s*(?:điểm\s*)?(?:lực\s*)?"
                   r"(?:khí huyết|pháp lực|ngoại công|nội công|ngoại kháng|nội kháng)")
KICHTHUOCNHANOTUI = 0x10
SONHANOTUI = 0x80
# Phẩm chất ô túi (1 byte / ô) và số hiệu hình (4 byte / ô) tính từ TG_HANHTRANG; kho: tính từ TG_KHO (hình = DC.KHO_MA). Dò 2026-11-21/22
HT_PHAMCHAT = 0x1DBC4
HT_HINH = 0x1DA1C
KHO_PHAMCHAT = 0x1B198
# Mô tả ô kho (dò 23/11 từ xq+0xB3821, đoạn rê chuột lên ô kho): ô o (từ 0) ở S + KHO_MOTA + (o + 1) * KHO_KICHTHUOCMOTA (game
# đánh chỉ số từ 1, phần tử 0 trùng đầu cấu trúc), nạp bằng "desc <mã kho># <o + 1>" (chuỗi xq+0x19D8E4; S+0x314 = 1 thì client
# dùng "desc %d %d", chưa gặp). Đổi rương thì mô tả rương trước vẫn nằm đó => kiểm dòng đầu là tên món
KHO_MOTA = 0x4C
KHO_KICHTHUOCMOTA = 0x44C
# Mỗi 0.5s ghi lại bảng nhãn; món không chồng (số lượng 0) chưa có mô tả thì "desc" độ ưu tiên thấp, cách nhau 0.3s, mỗi món 1 lần
THOIGIANCAPNHATNHANOTUI = 0.5
THOIGIANDESCNHANOTUI = 0.3
# Đồ đang mặc (ô VITRITRANGBIDAUTIEN..+SOLUONGOTRANGBI, vẽ ở bảng Nhân Vật TG+0xADFDDC qua hook "cửa sổ 2", 10 ô đọc từ
# bảng [ebp+0x2E2CC - 0x2E0C4] trong xq+0x13BF5D): người dùng 23/11 chỉ muốn độ bền "a/\nb". Độ bền trong mô tả không tự
# cập nhật => "desc <ô - 95>" lại mỗi ô sau chừng này giây
THOIGIANDESCLAIDOBENTRANGBI = 60.
# Danh sách danh hiệu đang có ở KDK_DANHSACHDANHHIEU: mỗi mục KICHTHUOCMUCDANHHIEU byte (mã +0, tên +6), đọc tối đa SODANHHIEUTOIDA mục
KICHTHUOCMUCDANHHIEU = 0x42
SODANHHIEUTOIDA = 16
THOIGIANDOCDANHHIEU = 5.

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
KHUVUCCAM_MAP = {
    BANDO_BACHMATRANG: [
        {"type": "circle", "x": 80, "y": 122, "r": 9.0},
        {"type": "line", "x1": 132, "y1": 159, "x2": 160, "y2": 139, "r": 9.0},
        {"type": "line", "x1": 131, "y1": 111, "x2": 160, "y2": 139, "r": 9.0},
    ],
    # Mã Lăng Đạo: bỏ 2 vùng cấm tầng trên vách đá (vẫn đi bằng đường bot tự tìm, xem BANDOBOTTUTIMDUONGs) (116, 116)-(145, 150), (93, 96)-(124, 118) bán kính 9 (2026-11-06): đã có đi vòng
    # cả bản đồ khi hết quái gần (THOIGIANHETQUAIGANDIVONG). Còn quái gần thì quái tầng trên vẫn bị bỏ vì đường vòng xa như cũ
    BANDO_KENHTRINHQUOC1: [
        {"type": "circle", "x": 108, "y": 57, "r": 6.0},
        # Phó bản Tập Kích Môn Phái dùng chung bản đồ (id vẫn là 151): đi vào 2 chỗ này bị kẹt không đi tiếp được, phải lùi tay
        {"type": "circle", "x": 103, "y": 54, "r": 3.0},
        {"type": "circle", "x": 96, "y": 96, "r": 3.0},
    ],
}
# Bản đồ luôn đi bằng đường bot tự tìm trên lưới vật cản (moitruong.action_dikhongcatgoc) dù không có khu vực cấm: Mã Lăng Đạo vách đá
# dài, tìm đường của client / game tới quái bên kia vách chạy tới chân vách rồi đứng ("Hoàn tất tự động tìm đường" liên tục, 2026-11-06).
# Trước đây có khu vực cấm nên bản đồ này đã đi kiểu này.
# Khốn Ma Trận 1/2/3 là mê cung: tìm đường cục bộ của client (~50-100 bước) tới điểm sư môn phía đông chạy tới ngõ cụt (131, 108) rồi
# quay lại, lắc qua lắc lại quanh (125, 109) (log 342, 2026-11-09); đường bot tự tìm có tìm cả bản đồ khi khung ±25 ô không ra đường
# Cự Lộc: khuôn viên nhà (55-84, 95-112) chỉ có lối ra phía tây rồi vòng lên bắc qua (59, 82), phía đông là tường x 84-88. Tìm đường
# client tới điểm dò phía đông chạy thẳng sang ngõ cụt (80, 101) rồi mới quay lại, giữa chừng gặp quái => kẹt trong khuôn viên ~4 phút
# (log 364, 2026-11-14)
BANDOBOTTUTIMDUONGs = {BANDO_MALANGDAO, BANDO_KHONMATRAN1, BANDO_KHONMATRAN2, BANDO_KHONMATRAN3, BANDO_CULOC}
# True: MỌI bản đồ đi cùng bản đồ bằng A* của bot (astar_xq.dll: cả bản đồ ~1.5 ms), không dùng tìm đường cục bộ của client (~50-100
# bước, chạy vào ngõ cụt rồi mới quay lại) => khỏi thêm tay từng bản đồ vào BANDOBOTTUTIMDUONGs. A* né vòng quanh cổng (VUNGCAM_MAP) để
# không lọt sang bản đồ khác. Sang bản đồ khác vẫn dùng tự động tìm đường của game. False: chỉ bản đồ trong danh sách trên như cũ
IS_BOTTUTIMDUONGMOIBANDO = True
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
# Đây là giá trị mặc định: chỉnh trên giao diện (tab Khác > Nhịp lệnh) thì lưu vào _internal/dieuphoi.json và dùng giá trị trong đó
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
# Ba Động từ xa của Đào Hoa Nguyên (người dùng 26/11): 2 bot cùng tung Ba Động từ xa lên 1 mục tiêu một lúc trông lộ bot. Bot gửi
# trước giữ chỗ (khoá riêng, không theo hiệu ứng) trong khoảng ngẫu nhiên này; bot khác bỏ qua Ba Động từ xa, chạy bộ vào như thường.
# Ngắn hơn hồi chiêu Ba Động (6s) để không chặn quá lâu. Ba Động lót cận chiến không giữ chỗ
KHOAGIUCHO_BADONGTUXA = "badongtuxa"
THOIGIANGIUBADONGTUXA = (2.5, 4.0)

# Nhiều cửa sổ cùng phát nhạc nghe bị vọng: chỉ để tiếng cửa sổ có nhân vật ưu tiên cao nhất trong danh sách tổ đội tự động
# (nhóm đầu, ID đứng trước), tính riêng từng bản Aegis / Niết Bàn, các cửa sổ khác tắt tiếng trong Volume Mixer của Windows. Thoát tool thì bật lại tiếng tất cả
IS_CHIBATAMTHANHCUASOUUTIEN = False
# Như trên nhưng chỉ tắt NHẠC NỀN ở các cửa sổ khác, âm thanh (tiếng chiêu, quái...) vẫn để mọi cửa sổ. Cờ nhạc nền / âm thanh trong
# xq.ini [syssetting] dùng chung mọi client (đọc lúc mở game) nên không chỉnh riêng được bằng cửa sổ Điều chỉnh trò chơi: bot ghi thẳng
# cờ nhạc của từng client trong bộ nhớ ([TG + TG_CAIDATTROCHOI] + 0x1EC) rồi gọi HAMNHACNEN để dừng / phát ngay, không đụng xq.ini.
# Cửa sổ ưu tiên vẫn bật nhạc dù xq.ini đang music=0
IS_CHIBATNHACNENCUASOUUTIEN = True
THOIGIANKIEMTRAAMTHANH = 2.

# Dữ liệu chung giữa các cửa sổ (shared_data) đọc lại sau mỗi khoảng này (các cửa sổ cập nhật 0.25s/lần)
THOIGIANNHOSHAREDDATA = 0.25

# Chết rồi chờ bấy nhiêu giây (có thể được người khác cứu) mới tự phục sinh
THOIGIANCHOTRUOCKHIPHUCSINH = 30.
CAPDOTOITHIEUTETHANTUONG = 60
# Bảo thú triệu hồi còn dưới PHANTRAMSINHLUCTETHANTUONG% sinh lực thì Tế Thần Tướng
PHANTRAMSINHLUCTETHANTUONG = 25
# Mệnh Tế hồi cho cả nhóm trong 21x21 ô quanh bản thân (10 ô mỗi phía)
KHOANGCACHHIEUQUAMENHTE = 10
# Thực tế xa quá thì đồng đội không được hồi: chỉ Mệnh Tế khi đồng đội cần hồi trong KHOANGCACHSUDUNGMENHTE ô,
# đồng đội cần hồi ở xa hơn (trong KHOANGCACHTIMTHANHVIENMENHTE ô) thì tiếp cận tới KHOANGCACHSUDUNGMENHTE ô rồi mới dùng
KHOANGCACHSUDUNGMENHTE = 8
KHOANGCACHTIMTHANHVIENMENHTE = 18
# Ngưỡng % sinh lực để Mệnh Tế / Huyết Tế: (mọi bảo thú, bảo thú không phải Cương Thi / Thần Tướng).
# Lăng Ly Sơn / Thành Kiều quái dồn sát thương nhanh nên tế sớm (35/65); nơi khác (Phong Yêu Kính, farm) 35/65 tế quá vội
# khi mới mất chút máu (người dùng 2026-11-04) nên dùng lại 25/50
PHANTRAMSINHLUCTEBAOTHU = (25, 50)
PHANTRAMSINHLUCTEBAOTHU_LANGLYSON = (35, 65)
BANDOTEBAOTHUSOMs = (BANDO_THANHKIEU, BANDO_LANGLYSON1, BANDO_LANGLYSON2, BANDO_LANGLYSON3)

# Hình thức bảo thú (ô +0x1DC, lệnh "pet <id># mode N"): 1 Tấn công, 2 Phòng thủ, 0 Bị động. Tích ô "Ép bảo thú ... Bị động"
# (mặc định tắt) thì bot ép mọi bảo thú về Bị động
# (người dùng 2026-11-26: Tấn công / Phòng thủ thì bị đánh là nó tự phản kích, chạy đi xa phải quay lại dắt)
HINHTHUCBAOTHU_TANCONG = 1
HINHTHUCBAOTHU_PHONGTHU = 2
HINHTHUCBAOTHU_BIDONG = 0
# Ô hình thức chưa đúng Bị động thì gửi lại lệnh tối đa mỗi chừng này giây cho mỗi con
GIANCACHTHIETLAPHINHTHUCBAOTHU = 5.
# Bảo thú giang hồ dưới % khí huyết này thì thu hồi ("pet <id># hide", chuỗi lệnh trong xq.exe cạnh "show"), cấu hình được ở nhóm
# Bảo thú, 0 = không thu hồi (người dùng 2026-11-26). Đã thu hồi thì không tự triệu hồi lại tới khi máu đủ ngưỡng, hoặc quá
# THOIGIANCHOTRIEUHOILAIBAOTHU giây (phòng máu đọc lúc cất không đổi => không bao giờ gọi lại)
PHANTRAMSINHLUCTHUHOIBAOTHUGIANGHO = 25.
THOIGIANCHOTRIEUHOILAIBAOTHU = 120.
# Bảo thú giang hồ độ trung thành dưới mức này thì không tự triệu hồi, cảnh báo + báo Telegram (người dùng 2026-11-26)
DOTRUNGTHANHTOITHIEUTRIEUHOI = 50
# Cho bảo thú giang hồ ăn: Lão Tửu khi nội lực <= max(NOILUCBAOTHUCHOANLAOTUU, PHANTRAMNOILUCBAOTHUCHOANLAOTUU % tối đa), Dưa hấu khi
# khí huyết thiếu >= SINHLUCTHIEUBAOTHUCHOANDUAHAU; đang có hiệu ứng hồi (mã trong _internal/tenhieuung.json) thì không cho ăn thêm.
# Sau mỗi lần cho ăn chờ CHOHIEUUNGHOIPHUCBAOTHU giây cho hiệu ứng kịp hiện trên bảo thú
NOILUCBAOTHUCHOANLAOTUU = 120
PHANTRAMNOILUCBAOTHUCHOANLAOTUU = 30.
SINHLUCTHIEUBAOTHUCHOANDUAHAU = 1200
HIEUUNG_HOIPHAPLUCBAOTHU = 9156
HIEUUNG_HOIKHIHUYETBAOTHU = 9154
CHOHIEUUNGHOIPHUCBAOTHU = 1.5

# Bảo thú kỹ năng triệu hồi xa nhân vật quá KHOANGCACHGOIBAOTHUVE ô thì gọi theo sau, tới khi về trong KHOANGCACHBAOTHUDAVE ô mới cho đánh tiếp
KHOANGCACHGOIBAOTHUVE = 18.
KHOANGCACHBAOTHUDAVE = 9.
# Đang gọi về thì gửi lệnh Theo sau đều mỗi chừng này giây tới khi về gần: xa đủ thì mỗi lệnh phù bảo thú về cạnh chủ, chưa đủ
# xa thì mỗi lệnh chỉ chạy thêm một đoạn => gọi một lần (hoặc dãn cách dài) nó chạy được một đoạn lại quay về chỗ cũ
THOIGIANGOIBAOTHUVE = 0.5
# Bỏ quay lại đón bảo thú (người dùng 2026-11-20): đi vòng góc vách mà bảo thú đang Theo sau còn cách quá KHOANGCACHBAOTHUDANEO ô thì
# dừng ở ô cuối của đường mà từ chỗ nó còn thấy mình (đường thẳng không vật cản), gọi Theo sau mỗi THOIGIANGOIBAOTHUVE giây, nó về trong
# KHOANGCACHBAOTHUDANEO ô mới rẽ tiếp (moitruong._catduongchobaothu). Chờ một chỗ quá THOIGIANCHOBAOTHUTOIDA giây (nó kẹt chỗ khác) thì
# đi luôn, ra xa quá KHOANGCACHGOIBAOTHUVE thì lệnh Theo sau phù nó về. Không chờ khi đang tiếp cận đánh quái (sobuoctoida / is_dungkedich)
IS_CHOBAOTHUOGOC = True
KHOANGCACHBAOTHUDANEO = 3.
THOIGIANCHOBAOTHUTOIDA = 3.

# Chờ lệnh đánh: đang ra đòn / dùng phép thì không gửi lệnh đánh nào (game đang bận; game cập nhật cờ sẵn sàng chậm, gửi chiêu khác là
# cắt ngang chiêu đang ra), còn lại (đứng im, di chuyển, khựng sau đòn) gửi ngay, riêng vừa gửi xong thì chờ tối đa ngần này giây
# cho game kịp chuyển tư thế (nếu không sẽ gửi tiếp chiêu khác, cắt ngang chiêu vừa gửi). Phải ngắn hơn 1 vòng bot (~0.123s):
# 0.15 làm cứ gửi 1 vòng lại bỏ 1 vòng => spam chiêu thực tế 0.25s/lần (đo log 2026-10-28), lúc server nhận bị làm tròn theo 0.25s
THOIGIANCHOPHANUNGLENH = 0.1

# Côn Luân Đằng Vân Giá Vũ: lướt xong máy chủ không nhận chiêu ~2s (log 273 2026-10-30: <1s sau lướt 64% chiêu không ra, 1-2s 53%,
# >3s 16%) => trong ngần này giây không gửi chiêu (tránh khoá chống spam oan), đi bộ vào gần hơn tầm xa KHOANGCACHGANTHEMSAULUOT ô.
# Khi đánh chỉ lướt lúc mục tiêu xa hơn tầm xa + KHOANGCACHLUOTTHEMKHITANCONG ô (đi bộ ngần đó ô ~ bằng thời gian chờ sau lướt),
# gần hơn thì đi bộ cho nhanh; lùi giữ khoảng cách / đi đường vẫn lướt như cũ
THOIGIANKHOACHIEUSAULUOT = 2.
KHOANGCACHGANTHEMSAULUOT = 3.
KHOANGCACHLUOTTHEMKHITANCONG = 5.
# Chọn mục tiêu khi đang chạy: con nằm sau lưng (ngược hướng đang chạy) bị tính xa thêm ngần này ô, để không quay đầu đổi qua lại
PHATMUCTIEUSAULUNG = 3.
# Mục tiêu đang đánh chỉ bị thay bằng con khác chỉ vì gần hơn khi con đó gần hơn ít nhất ngần này ô (giữa các ứng viên khác chỉ cần 0.5):
# hai con hai bên gần ngang nhau thì cứ chạy về phía con này vài bước là con kia lại "gần hơn" => đổi qua lại liên tục, đứng một chỗ
CHENHLECHKHOANGCACHDOIMUCTIEU = 1.5
# Chọn mục tiêu theo đường đi thật (_is_muctieutheoduongdi): một lần loang BFS 8 hướng từ ô mình trên lưới vật cản ±BANKINHLOANGMUCTIEU ô
# (chéo chỉ khi 2 ô kề đều trống như máy chủ; bước thẳng hay chéo đều 1 nhịp "go", tầm đánh theo ô vuông nên số bước BFS là đúng thời
# gian đi). Con ngoài tầm đánh so bằng max(đường chim bay, số bước tới ô trong tầm nó + tầm) => quái "gần" mà sau vách đá bị tính xa đúng
# quãng phải đi vòng; con không tới được trong khung tính xa thêm PHATMUCTIEUKHONGDUONG ô (vẫn chọn được khi chỉ còn nó). Kết quả loang
# dùng lại tới THOIGIANNHOLOANGMUCTIEU giây nếu mình chưa đi quá SOOLECHLOANGMUCTIEU ô (vòng tìm mục tiêu chạy mỗi 0.15s)
BANKINHLOANGMUCTIEU = 24
THOIGIANNHOLOANGMUCTIEU = 0.6
SOOLECHLOANGMUCTIEU = 2
PHATMUCTIEUKHONGDUONG = 15.
# Ưu tiên cụm quái (_is_uutiencumquai): mỗi con hợp lệ khác đứng trong BANKINHCUMQUAI ô (ô vuông, như chiêu diện rộng quanh mình 3 ô)
# quanh ứng viên làm nó "gần" thêm THUONGMOICONCUM ô khi so, tối đa SOCONCUMTOIDA con => chọn con giữa cụm, đi tới đó là đứng giữa cụm
# (chiêu quanh mình / quanh mục tiêu trúng nhiều con nhất). Chỉ áp cho quái, không cho người chơi / bảo thú
BANKINHCUMQUAI = 3.
THUONGMOICONCUM = 1.
SOCONCUMTOIDA = 4
# Chia mục tiêu giữa các bot (_is_chiamuctieubotkhac): quái bot khác cùng bản đồ (cùng máy / LAN, bật Tự động sử dụng kỹ năng, không
# phải bot theo sau tập hỏa) đang chọn mà nó gần con đó hơn mình (ô vuông; bằng nhau thì ID người chơi nhỏ hơn giữ) thì tính xa thêm
# PHATMUCTIEUBOTKHAC ô: phạt mềm, chỉ còn con đó thì vẫn đánh chung. Mục tiêu mình đã đánh tới (trong tầm đánh) không bị phạt, kẻo hai
# bot cùng nhường nhau chạy qua lại (lỗi nhường theo ID trước 2026-11-08). Boss Lăng Ly Sơn / Thành Kiều không chia
PHATMUCTIEUBOTKHAC = 5.
THOIGIANDOCMUCTIEUBOTKHAC = 1.
# Ô tích nhóm Chọn mục tiêu: thuộc tính TacTu -> lời phát âm khi bật / tắt (lệnh giao diện "battat_chonmuctieu:<thuộc tính>")
CHONMUCTIEUBATTAT_MAP = {
    "_is_muctieutheoduongdi": "chọn mục tiêu theo đường đi",
    "_is_uutiencumquai": "ưu tiên cụm quái",
    "_is_chiamuctieubotkhac": "chia mục tiêu với bot khác",
    "_is_pkbodanhsachten": "bật PK thì đánh cả người chơi ngoài danh sách",
}

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
# Lag mạng làm gói đồng bộ giờ máy chủ tới trễ: giờ client kèm lệnh go bị lùi (đo 21s, 37s, 43s), máy chủ từ chối mọi bước đi tới lần
# đồng bộ sau (~5 phút) => khoá di chuyển oan. MoiTruong.action_suagiomaychu: độ lệch giờ máy chủ tụt >= NGUONGLUIGIOMAYCHULAGMANG
# giây so với lúc mạng tốt thì ghi lại cho đúng
NGUONGLUIGIOMAYCHULAGMANG = 3
# Giờ máy chủ của client tụt mà bấy nhiêu lần đồng bộ liền nhau đều tụt như vậy thì tin là máy chủ đổi giờ thật, không sửa nữa
# (lag chỉ làm 1 lần đồng bộ tới trễ; đồng bộ ~5 phút / lần)
SOLANDONGBOTUTGIOMAYCHU = 2
# Vừa sửa giờ máy chủ chưa quá bấy nhiêu giây thì không học vật cản (MoiTruong.get_is_vuasuagiomaychu): bị kéo về là do lệnh go
# gửi trước lúc sửa mang giờ cũ
THOIGIANKHONGHOCVATCANSAULAG = 10.
# Người chơi giữ chuột trái trên cửa sổ game quá THOIGIANGIUCHUOTTOITHIEU giây (kéo nhân vật đi, click thường không tính):
# bot ngưng tấn công / di chuyển, nhả chuột rồi còn ngưng thêm THOIGIANNGUNGSAUNHACHUOT giây để nhân vật kịp đi tiếp theo
# click cuối (MoiTruong.get_is_dangclickchuottrai)
THOIGIANGIUCHUOTTOITHIEU = 0.3
THOIGIANNGUNGSAUNHACHUOT = 0.4
# Click nhanh xuống đất cũng tính như giữ chuột (cắt cả chiêu đang xuất): đích click chuột của game đổi trong chừng này giây sau
# lúc thấy chuột trái thật đang bấm trên cửa sổ game
THOIGIANNHANCLICKDICHUYEN = 0.5
# Gửi chiêu trong tầm rồi thì chặn client tự bước tối đa chừng này giây chờ vào tư thế xuất chiêu
THOIGIANCHANTUDICHUYENTRUOCXUATCHIEU = 0.25
# Trong lúc xuất chiêu / khựng chỉ gửi chiêu nhắm mục tiêu khi mục tiêu trong chừng này ô (ngoài tầm thì game tự chạy lại gần)
KHOANGCACHCHIEUKHIXUATCHIEU = KHOANGCACHSUDUNGKYNANGCANCHIEN
# Đang chế đồ (vận khí): kiểm tra ô cuối hành trang 1 mỗi chừng này giây, có vật phẩm thì chuyển sang hành trang khác ngay
CHUKYGIUOTRONGHANHTRANG = 0.03
# Kỹ năng cần đứng lại khi ra đòn: chờ tối đa chừng này giây để nhân vật vào tư thế xuất chiêu rồi mới ngắt di chuyển
THOIGIANCHONGATDICHUYENXUATCHIEU = 1.

# Kỹ năng (có hay không mục tiêu) gửi >= SOLANGUITOIDASPAMKYNANG lần trong SOGIAYDEMSPAMKYNANG giây (tức là game báo sẵn sàng mà kỹ năng không ra)
# thì không khoá, chỉ giãn nhịp kỹ năng đó còn 1 lần / KHOANGCACHGUISPAMKYNANG giây; log CHẶN SPAM tối đa 1 lần / THOIGIANLOGSPAMKYNANG giây
SOLANGUITOIDASPAMKYNANG = 3
SOGIAYDEMSPAMKYNANG = 1.5
KHOANGCACHGUISPAMKYNANG = 0.5
THOIGIANLOGSPAMKYNANG = 5.
# Kỹ năng không áp chống spam (gửi dồn bao nhiêu cũng được): Đại Hải Vô Lượng bấm tay liên tục vẫn ra chiêu bình thường,
# chặn spam chỉ làm nó nghỉ 3s vô ích. Các chiêu đánh Đào Hoa Nguyên: server nhận chiêu kế lúc sẵn sàng (lệch ngẫu nhiên
# 0.5-1.7s sau chiêu trước, đo 2026-10-28) nên nối chiêu phải gửi lại tới khi được nhận, khoá 3s làm đứt chuỗi
# Tâm pháp bật / tắt (Nguyên Khí Quy Nguyên, Dã Tính Cuồng Lực): gửi 1 lần rồi chờ chừng này giây cho hiệu ứng hiện mới gửi lại
THOIGIANCHOTAMPHAPBATTAT = 3.
IDKYNANGKHONGCHANSPAMs = (
    VITRIKYNANG_DAIHAIVOLUONG, VITRIKYNANG_THONKINH, VITRIKYNANG_PHONGMAQUYET, VITRIKYNANG_KHONGTHUNHAPBACHNHAN,
    VITRIKYNANG_DAOHOALACANH, VITRIKYNANG_METUNGQUYEN, VITRIKYNANG_BADONGQUYEN, VITRIKYNANG_NHATQUYENBATSON, VITRIKYNANG_LACKICH,
    VITRIKYNANG_PHANTOA,
)

# Nhân vật trong tổ đội tự động (cùng hay khác nhóm, trừ khi đang theo sau trưởng nhóm) có ID nhỏ hơn được giữ vùng: nhân vật ID lớn hơn tránh mọi quái
# và điểm lộ trình trong bán kính này quanh nó
BANKINHVUNGNHUONGQUAIDONGDOI = 15.
# Gom quái: đủ số tối thiểu rồi mà còn quái chưa kéo cách đám đang gom (con neo) không quá bấy nhiêu mét thì kéo nốt rồi mới đánh
BANKINHKEOTHEMGOMQUAI = 8.
# Gom quái: đã gom bấy nhiêu con thì thôi kéo thêm, tụ về neo rồi đánh (cả Tập Kích Môn Phái). Trước 20, người dùng hạ 16 (2026-11-17)
SOQUAIGOMTOIDA = 16

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
# Bí Đạo (Tung Sơn, Trung Nguyên, Lang Gia, Mang Sơn, Hành Sơn, Vũ Lăng, Tuyết Phong Sơn): cổng vào ngoài maplink.dat (bando_xq)
BANDOBIDAOs = frozenset(range(524, 531))


def layphuongandichuyen(idbando):
    # -> (tên NPC, bước: list lệnh welcome (Tân Thủ Tiên Cô) hoặc điểm đến "goto.!" (Chủ Dịch Trạm), id bản đồ phù tới, số cổng chạy bộ tiếp)
    # của cách phù tới idbando ít cổng chạy bộ nhất (phù thẳng tới = 0 cổng), vd. Yên Trường Thành 1: Chủ
    # Dịch Trạm tới Yên Quốc rồi chạy 1 cổng; Tề Quốc: Chủ Dịch Trạm thẳng tới. Không giới hạn số cổng chạy tiếp (Thiên Môn Trận 1: phù Tề
    # Quốc rồi chạy 6 cổng vẫn hơn chạy bộ 15 cổng từ Sở Quốc), nơi gọi tự so với chạy bộ. Không phù tới được thì None
    # Về Tân Thủ Thôn thì dùng Hồi Thành Phù, không phù tới bản đồ khác rồi chạy về
    # Đích là Bí Đạo (BANDOBIDAOs) thì đếm cả cổng ngoài maplink: cổng vào Bí Đạo đều ngoài maplink nhưng bot tự chạy từng cổng
    # (_lapbuocditoibando). Trước chỉ đếm cổng client tự đi => Hành Sơn Bí Đạo "không phù được", Săn Tinh Anh chạy bộ 9 cổng từ Yên
    # Trường Thành 3 thay vì phù Sở Quốc rồi chạy 1 cổng (418, 2026-11-18 20:40). Đích khác giữ như cũ (kẻo chiến trường 5xx, 888 thành
    # đích phù được, sư môn chọn làm bãi train)
    if idbando == BANDO_TANTHUTHON:
        return None
    if idbando not in _phuongandichuyen_cache:
        tot = None
        for tennpc, buoc_map in ((TANTHUTIENCO, DICHUYENTANTHUTIENCO_MAP), (CHUDICHTRAM, DIEMDENCHUDICHTRAM_MAP)):
            for idphutoi, buoc in buoc_map.items():
                solan = 0 if idphutoi == idbando else get_solanchuyenbando(idphutoi, idbando, is_chicongclienttudi = idbando not in BANDOBIDAOs)
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

# Tuỳ chọn "Đi quốc gia bằng Tân Thủ Tiên Cô" (mặc định bật, người dùng dặn 2026-11-06): tới quốc gia thì thay vì Hồi Thành Phù về Tân Thủ
# Thôn, Tín Vật về môn phái, nói chuyện Tân Thủ Tiên Cô trong môn phái phù lên bản đồ gần quốc gia rồi chạy 1 cổng sang.
# Quốc gia -> bản đồ phù tới (đều có trong menu Tân Thủ Tiên Cô, cách quốc gia 1 cổng; kiểm tra bằng timduongbando 2026-11-06)
# Không có Chu Quốc và Tân Thủ Thôn (người dùng dặn 2026-11-07): tới hai nơi này đi như cũ (Hồi Thành Phù, Chủ Dịch Trạm,
# đường ưu tiên Thủ Dương Sơn của DUONGUUTIENs vẫn giữ)
BANDOGANQUOCGIA_TANTHUTIENCO = {
    BANDO_TRIEUQUOC: 131,  # Cự Lộc
    BANDO_TEQUOC: 211,     # Mã Đạp Hồ
    BANDO_NGUYQUOC: 42,    # Vô Định Hà 1
    BANDO_YENQUOC: 271,    # Trác Lộc
    BANDO_SOQUOC: 261,     # Chân Núi Đại Biệt
    BANDO_HANQUOC: 21,     # Tương Lăng
    BANDO_TANQUOC: 151,    # Kênh Trịnh Quốc 1
}
_bandotanthutiencogan_cache = {}
SOCONGTHEMTHAYDICHTRAM = 3


def laybandotanthutiencogan(idbando):
    # Tuỳ chọn "Đi quốc gia bằng Tân Thủ Tiên Cô" cho cả đích SAU quốc gia (người dùng 16/11: Săn Tinh Anh tới Yên Trường Thành 1 vẫn
    # Hồi Thành Phù + Chủ Dịch Trạm qua Yên Quốc): -> (bản đồ Tân Thủ Tiên Cô phù tới, số cổng chạy tiếp) hoặc None.
    # Quốc gia: bản đồ gần trong BANDOGANQUOCGIA_TANTHUTIENCO. Bản đồ khác: khi cách phù tốt nhất (layphuongandichuyen) là Chủ Dịch Trạm
    if idbando not in _bandotanthutiencogan_cache:
        kq = None
        idgan = BANDOGANQUOCGIA_TANTHUTIENCO.get(idbando)
        if idgan is not None:
            solan = get_solanchuyenbando(idgan, idbando, is_chicongclienttudi = idbando not in BANDOBIDAOs)
            kq = (idgan, 1 if solan is None else solan)
        else:
            # Mọi đích mà cách phù tốt nhất là Chủ Dịch Trạm (người dùng 16/11: Dịch Trạm rất tốn), trừ Chu Quốc (đi như cũ): thay bằng
            # bản đồ Tân Thủ Tiên Cô chạy tiếp ít cổng nhất, nếu chạy thêm không quá SOCONGTHEMTHAYDICHTRAM cổng so với Dịch Trạm
            phuongan = layphuongandichuyen(idbando)
            if phuongan and phuongan[0] == CHUDICHTRAM and idbando != BANDO_CHUQUOC:
                for idphutoi in DICHUYENTANTHUTIENCO_MAP:
                    if idphutoi is None:
                        continue
                    solan = 0 if idphutoi == idbando else get_solanchuyenbando(idphutoi, idbando, is_chicongclienttudi = idbando not in BANDOBIDAOs)
                    if solan is not None and (kq is None or solan < kq[1]):
                        kq = (idphutoi, solan)
                if kq and kq[1] > phuongan[3] + SOCONGTHEMTHAYDICHTRAM:
                    kq = None
        _bandotanthutiencogan_cache[idbando] = kq
    return _bandotanthutiencogan_cache[idbando]


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
# Người được theo sau cùng máy đang chạy tới cổng / đích chuyến đi: theo sau bám điểm phía trước họ bấy nhiêu ô theo hướng đó
# (không quá điểm đó), khỏi luôn trễ một nhịp sau lưng. Chưa đo, để nhỏ để không vượt lên trước quá xa
KHOANGCACHPHIATRUOCTHEOSAU = 4.
# Theo sau tự nhiên (ô "Theo sau tự nhiên", tactu_dichuyen._laytinhcachtheosau), để các bot cùng máy trông như người chơi khác nhau.
# Chưa đo, số ước lượng (2026-11-28). Mỗi nhân vật lấy một giá trị cố định theo ID trong các khoảng sau:
#   trễ phản ứng (giây) sau khi ra quá ngưỡng kéo về mới bắt đầu đi
TRETHEOSAUTUNHIEN = (0.2, 1.5)
#   cộng thêm vào ngưỡng kéo về (ô) lúc không đánh, tối đa 40% khoảng cách theo sau
THEMNGUONGTHEOSAUTUNHIEN = (0., 2.)
#   hệ số bán kính chỗ đứng (thích đứng sát / đứng xa) và độ lệch góc riêng (radian)
HESOBANKINHTHEOSAUTUNHIEN = (0.7, 1.15)
LECHGOCTHEOSAUTUNHIEN = 0.35
# Chỗ đứng chia trong hình nón sau lưng người được theo sau theo hướng họ đi (radian, 140°) thay vì vòng tròn đều 360°
GOCNONTHEOSAUTUNHIEN = 140 * 3.141592653589793 / 180
# Độ lệch chỗ đứng (ô) và khoảng thời gian (giây) chọn lại chỗ đứng; họ vừa dừng lại thì chọn lại ngay
LECHDIEMTHEOSAUTUNHIEN = 0.8
THOIGIANDOICHOTHEOSAUTUNHIEN = (30., 90.)
# Tụt quá ngưỡng kéo về hơn bấy nhiêu ô thì bỏ trễ phản ứng, đi ngay
KHOANGCACHBOTRETHEOSAU = 3.
# Đi theo vết (đợt 2): cả hàng nén trong [đầu hàng, khoảng cách theo sau - 0.5] ô tính dọc vết, hai người liền nhau cách tối đa
# KHOANGCACHHANGTHEOSAU ô; mỗi người lệch ngang vết một khoảng riêng (ô, trái hoặc phải) => đi thành dải. Vết giữ tối đa bấy nhiêu điểm (~1 ô/điểm)
DOANLUIDAUHANGTHEOSAU = 1.5
KHOANGCACHHANGTHEOSAU = 1.2
LECHNGANGTHEOSAUTUNHIEN = (0.5, 2.)
SODIEMVETTHEOSAU = 60
# Sang bản đồ bằng nói chuyện NPC (bando_xq.LOIDINPC_MAP): đứng cách NPC tối đa chừng này ô mới nói chuyện, chờ menu hiện tối đa
# THOIGIANCHOMENULOIDINPC giây, chọn rồi quá THOIGIANTHULAILOIDINPC giây vẫn chưa sang (NPC không cho qua, vận khí bị ngắt) thì nói chuyện lại
# Khoảng cách nói chuyện ("look" / talk) với NPC dùng chung mọi việc (sư môn, Danh Vọng, Thiên Xu, kéo cấp, phó bản, Mã Tặc, Tập Kích,
# phân giải, lối đi NPC). Người dùng dặn 2026-11-27: để 6 ô (trước 3-4 ô, phải chen sát NPC vô ích; give NPC 6-9 ô vẫn được)
KHOANGCACHNOICHUYENNPC = 6.
KHOANGCACHNOICHUYENLOIDINPC = KHOANGCACHNOICHUYENNPC
# NPC đứng trên ô vật cản (lưới bot): ô đi được gần nhất có khi xa hơn KHOANGCACHNOICHUYENLOIDINPC, đứng đó mãi không nói chuyện.
# Xa Phu Thục Sơn (187, 148) => kéo đích về (188, 142) cách ~6 ô, Gạ đứng đực 7 phút (2026-11-22 03:22). Đã tới ô đó (lệch <= 2 ô)
# thì nói chuyện luôn nếu cách NPC không quá chừng này ô (give NPC 6-9 ô vẫn được)
KHOANGCACHNOICHUYENLOIDINPCVATCAN = 8.
THOIGIANCHOMENULOIDINPC = 3.
THOIGIANTHULAILOIDINPC = 15.

IDLOAIVUKHI_TAYKHONG = 60
IDLOAIVUKHI_DAO = 61
IDLOAIVUKHI_KIEM = 62
IDLOAIVUKHI_THUONG = 63
IDLOAIVUKHI_CON = 64
IDLOAIVUKHI_AMKHI = 69
# Vũ khí cận chiến (Đào Hoa tay không, Thục Sơn Đao, Cấm Vệ Quân thương, Côn Luân côn): giữ khoảng cách với người chơi thù địch
# cầm loại này cứ đứng gần là lùi, không cần xem có đang đánh mình không (người dùng dặn 2026-11-19)
LOAIVUKHICANCHIENs = (IDLOAIVUKHI_TAYKHONG, IDLOAIVUKHI_DAO, IDLOAIVUKHI_THUONG, IDLOAIVUKHI_CON)
# Vân Mộng Cốc buff Thục Sơn theo vũ khí đang đeo (người dùng dặn 2026-11-09): kiếm chỉ cần Kim Châm, đao chỉ cần Ngân Châm;
# không biết vũ khí thì buff cả hai (MONPHAICHIBUFF... là theo môn phái)
LOAIVUKHITHUCSONCHIBUFFNGANCHAMs = (IDLOAIVUKHI_DAO,)
LOAIVUKHITHUCSONCHIBUFFKIMCHAMs = (IDLOAIVUKHI_KIEM,)

YEUCAUDICHUYEN_NONE = 0
YEUCAUDICHUYENNHATDO = 1
YEUCAUDICHUYENTANCONG = 2
YEUCAUDICHUYENDICHUYENTUDO = 3
YEUCAUDICHUYENTHEOSAU = 4
YEUCAUDICHUYENGOMQUAI = 5
YEUCAUDICHUYENGIUKHOANGCACH = 6
YEUCAUDICHUYENTIMMUCTIEUCHUNG = 7
# Buff toàn bản đồ: chạy tới thành viên cùng máy, cùng bản đồ, ngoài tầm cần buff (tactu_dichuyen._chontoibuffthanhvien)
YEUCAUDICHUYENCHAYTOIBUFF = 8
# Vân Mộng Cốc: bắt đầu chạy khi người cần buff xa hơn chừng này ô (gần hơn là trong tầm nhìn, luật buff tại chỗ tự tiếp cận),
# dừng chạy khi đã vào gần chừng kia ô. Đào Hoa / Thục Sơn dùng tầm đánh xa (luật tại chỗ chỉ xét người trong tầm buff)
KHOANGCACHBATDAUCHAYTOIBUFF = 16.
KHOANGCACHDUNGCHAYTOIBUFF = 12.

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
THOIGIANKHONGTRUNGCHIEUTOIDA = 4.
SOCHIEUKHONGTRUNGTOIDA = 3
THOIGIANBOQUAMUCTIEUKHONGTRUNG = 60.

# Tiếp cận quái mà bị vật cản lớn (cây, đá...) chắn: client tìm đường vòng qua lại nên nhân vật vẫn di chuyển, kiểm tra kẹt đứng im
# không bắt được. Còn phải đi tới mà quá THOIGIANTIEPCANKHONGGANTHEM giây khoảng cách tới quái không giảm thêm được
# KHOANGCACHTIEPCANGANTHEM ô thì bỏ qua quái đó THOIGIANBOQUAMUCTIEUKHONGTIEPCAN giây
THOIGIANTIEPCANKHONGGANTHEM = 6.
KHOANGCACHTIEPCANGANTHEM = 1.
THOIGIANBOQUAMUCTIEUKHONGTIEPCAN = 30.

# Bỏ qua do vật cản (không tới gần được, kẹt tường khi tới, gom bị chặn) chỉ đúng với vị trí lúc đó: quái đi lang thang / mình
# đổi chỗ thì 2-3s sau giữa hai bên có thể không còn vật cản. Nhớ toạ độ quái và mình lúc bỏ qua; sau ít nhất
# THOIGIANBOQUAVATCANTOITHIEU giây mà quái hoặc mình đã đi xa chỗ cũ >= KHOANGCACHHETBOQUAVATCAN ô thì thôi bỏ qua để xét lại
# (lần tiếp cận mới tìm đường lại từ đầu, vẫn bị chắn thì bỏ qua tiếp với vị trí mới). Không ai di chuyển thì hết sau
# THOIGIANBOQUAMUCTIEUKHONGTIEPCAN giây như cũ. Kiểm tra mỗi THOIGIANKIEMTRAHETBOQUAVATCAN giây (đọc toạ độ đối tượng xung quanh)
THOIGIANBOQUAVATCANTOITHIEU = 2.
KHOANGCACHHETBOQUAVATCAN = 3.
# Mình đi xa chỗ cũ thì cần xa hơn: bỏ con bị chắn đi đánh con khác vài ô đã gỡ thì dễ quay lại đúng con bị chắn, chạy qua chạy lại
KHOANGCACHHETBOQUAVATCANBANTHAN = 6.
THOIGIANKIEMTRAHETBOQUAVATCAN = 0.5
# Bắt đầu tiếp cận 1 quái thì tìm đường trên lưới vật cản trước (moitruong.get_sobuocduongtoi): không có đường, hoặc đường dài hơn
# HESODUONGVONGTOIDA lần khoảng cách thẳng + SOBUOCDUONGVONGCONGTHEM bước (phải vòng rất xa qua bên kia vật cản) thì bỏ qua luôn
HESODUONGVONGTOIDA = 2.
SOBUOCDUONGVONGCONGTHEM = 10
# Hết quái gần: vách đá dài (Mã Lăng Đạo, 2026-11-06) quái tầng dưới chết thì mọc lại tầng trên, khung tìm đường ±25 ô không thấy đường
# vòng nên quái tầng trên luôn bị bỏ => đứng chờ. Đã THOIGIANHETQUAIGANDIVONG giây không vào tầm đánh được con quái nào mà quái vừa chọn bị
# bỏ vì vật cản thì tìm đường trên cả bản đồ (moitruong.get_sobuocduongtoi is_cabando), không quá SOBUOCDIVONGXATOIDA bước thì đi vòng
# tới nó. Đi vòng tối đa sobuoc * THOIGIANMOIBUOCDIVONG * 1.5 + 10 giây (client gửi "go" 2 bước / 0.5s), quá thì bỏ như thường
THOIGIANHETQUAIGANDIVONG = 15.
SOBUOCDIVONGXATOIDA = 300
THOIGIANMOIBUOCDIVONG = 0.25
# Quái cách thẳng từ ngần này ô trở lên (mép tầm nhìn client ~17-18 ô) thì không đi vòng cả bản đồ tới nó: đi vòng là ra xa, quái mất
# khỏi bảng đối tượng client, ô địa chỉ bị đối tượng khác dùng lại => yêu cầu tấn công trỏ nhầm sang thú / NPC, rơi về Đi dạo, đi dạo
# lại thấy quái => lặp mãi tại chỗ. Log 364 Gạ 2026-11-22 07:41-07:45 Phong Yêu Kính (131): quanh (70, 80) ~4 phút đổi qua lại
# "Kính Quỷ (78, 95) đường vòng 48-61 bước cho 17.5 ô" ↔ "Thần Thú - Thỏ (66, 62)" ↔ Đi dạo (86, 124). Bỏ qua quái đó để Đi dạo đi tiếp
KHOANGCACHDIVONGXATOIDA = 13.
# Món dưới đất cách thẳng từ ngần này ô trở lên thì tìm đường trước khi chọn đi nhặt: không có đường / đường dài hơn
# HESODUONGVONGTOIDA lần + SOBUOCDUONGVONGCONGTHEM bước (nằm sau vách) thì bỏ qua như món không nhặt được. Log 364 Gạ và 342 Thỏ
# 2026-11-22 07:46-07:48 Phong Yêu Kính: Lam Ma Chi Lệ (81, 100) thẳng ~16 ô mà đường đi 78 bước, đi vòng ra quá 18 ô là món rời
# danh sách, về Đi dạo lại vào trong 18 ô => đổi qua lại Nhặt đồ ↔ Đi dạo mỗi ~1s, đứng một chỗ
KHOANGCACHNHATDOKIEMTRADUONG = 8.
# Lưới cả bản đồ (A* cả bản đồ) nhớ chừng này giây; đi vòng mà đích nhích không quá LECHDICHCABANDO ô thì đi hết chuỗi rồi mới tìm lại
THOIGIANNHOLUOICABANDO = 30.
# action_dikhongcatgoc thấy (từ, tới) không có đường cả trên cả bản đồ thì nhớ chừng này giây (mỗi lần tìm cả bản đồ tốn tới ~1s)
THOIGIANNHOKHONGDUONGCABANDO = 10.
LECHDICHCABANDO = 6.

# Giữ khoảng cách (tùy chọn trên giao diện, hay bật cho Mao Sơn / Vân Mộng Cốc khi giao tranh): chỉ với người chơi thù địch phái cận
# chiến (LOAIVUKHICANCHIENs) đứng gần hơn chừng này ô, không áp dụng cho quái / bảo thú
KHOANGCACHGIUKETANCONG = 6.
# Máu thấp thì chạy trốn khỏi mọi kẻ đang tấn công mình (mọi phái, cả quái, không cần bật giữ khoảng cách): máu dưới NGUONGMAUCHAYTRON%
# thì chạy, hồi trên NGUONGMAUHETCHAYTRON% mới quay lại đánh (mặc định, chỉnh ở giao diện theo nhân vật; ngưỡng chạy 0 = tắt).
# Chạy tới khi cách kẻ gần nhất KHOANGCACHCHAYTRON ô (tầm phép thật ~12 ô). Lúc chạy kẻ tấn công đuổi theo (không ra đòn) nên tính
# cả đối tượng thù địch đang chạy về phía mình, nhớ THOIGIANNHOKETANCONGCHAYTRON giây.
# Mặc định tắt (0) theo người dùng 2026-11-28; bật bằng ô "Máu dưới ...% thì chạy trốn" ở giao diện
NGUONGMAUCHAYTRON = 0
NGUONGMAUHETCHAYTRON = 30
KHOANGCACHCHAYTRON = 14.
THOIGIANNHOKETANCONGCHAYTRON = 6.
# Chạy trốn theo đường tính trên lưới vật cản (moitruong.get_duongchaytron): tính lại đường mỗi chừng này giây; đang chạy mà chừng này
# giây không nhích được 0.5 ô (không bị giữ đứng yên) thì coi đích là kẹt, bỏ đích đó THOIGIANBOQUADICHCHAYTRONKET giây
THOIGIANTINHLAIDUONGCHAYTRON = 0.6
THOIGIANKETDUONGCHAYTRON = 1.2
THOIGIANBOQUADICHCHAYTRONKET = 8.
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
# Hồi máu Vân Mộng Cốc (Cam Lộ Trị / Sơ Trị / Khiết Vân Quyết) chung 1 khoá KHOAGIUCHO_BOMMAU (người dùng 2026-11-28): nhiều acc Vân Mộng
# Cốc không cùng hồi 1 người 1 lúc; lúc chọn người cần hồi (tactu_muctieu) cũng bỏ người bot khác đang giữ để chọn người thấp máu kế tiếp
KHOAGIUCHO_BOMMAU = "bommau"
HIEUUNGGIUCHOKYNANG_MAP = {
    "vanmongcoc": {VITRIKYNANG_PHONGANTHUAT: HIEUUNGKYNANG_TRAMMAC, VITRIKYNANG_HUYENQUANGTHIEMANH: HIEUUNGKYNANG_MULOA, VITRIKYNANG_CAITUHOANSINH: "caituhoansinh",
                   VITRIKYNANG_CAMLOTRI: KHOAGIUCHO_BOMMAU, VITRIKYNANG_SOTRI: KHOAGIUCHO_BOMMAU, VITRIKYNANG_KHIETVANQUYET: KHOAGIUCHO_BOMMAU},
    "maoson": {VITRIKYNANG_THUCCOT: HIEUUNGKYNANG_THUCCOT, VITRIKYNANG_THUCGIAP: HIEUUNGKYNANG_THUCGIAP, VITRIKYNANG_THUCTAM: HIEUUNGKYNANG_THUCTAM},
    "thucsonkiem": {VITRIKYNANG_LANGKHONGCHIHUYET: HIEUUNGKYNANG_CHOANG},
}
# Khoá hiệu lực: bot thấy hiệu ứng dính trên mục tiêu thì đánh dấu, trong chừng này giây (tính từ lúc thấy dính) mọi bot (cùng máy / LAN)
# không buff lại hiệu ứng đó lên mục tiêu đó dù đã hết icon. Thực Cốt / Thực Giáp / Thực Tâm KHÔNG khoá (người dùng 2026-11-15): mục tiêu
# tự giải buff được, Thực Tâm chỉ 20s, nên khoá 120s cũ (2026-11-04) làm mục tiêu trống buff (trận boss 72s chỉ buff Thực Tâm 1 lần).
# Chỉ dựa vào icon: hết icon là buff lại; giữ chỗ giữa các bot (HIEUUNGGIUCHOKYNANG_MAP) vẫn còn nên mỗi lần chỉ 1 bot gửi
THOIGIANHIEULUCBUFFMAOSON_MAP = {}
# Mệnh Tế hồi cả nhóm: 1 bot Mao Sơn vừa Mệnh Tế cho những người thấp máu quanh nó thì bot khác (cùng máy / LAN) không Mệnh Tế cho
# chính những người đó trong chừng này giây (chờ máu hồi hiện ra rồi mới xét lại). Còn người thấp máu chưa ai lo thì vẫn Mệnh Tế
KHOAGIUCHO_MENHTE = "menhte"
THOIGIANGIUMENHTE = 2.5
# Kết quả xét kỹ năng quan trọng (tính trong danh sách kỹ năng của phái) cũ hơn chừng này giây thì coi như rảnh
THOIGIANHIEULUCKYNANGQUANTRONG = 0.5
YEUCAUDICHUYENKHAIKHOANG = 100
YEUCAUDICHUYENDAOTANGBAODO = 200

KIEUDICHUYEN_GIUKHOANGCACHTOIDA = 1
KIEUDICHUYEN_GIUKHOANGCACHTOITHIEU = 2
KIEUDICHUYEN_TOADOCHUAN = 3

# Chỉ là mặc định khi chưa có file _internal/todoi.json; cấu hình thật ở giao diện (tab Tổ đội > Tổ đội tự động)
NHANVATTODOITUDONGs_LIST = [
    [29, 30, 32, 31],
    [132, 133, 134, 135]
]

# Quái Tinh Anh (tên màu vàng trong game). Tên quái trong bộ nhớ không có mã màu, game tô theo loại quái máy chủ gửi => lấy danh sách
# từ map/tips/%03d.txt (từng byte XOR 0xFF), mục "Quái vật": tinh anh ghi "<#ffff66,0,Tên (cấp a ~ b)#>", boss "<#f076fc,...>" (không lấy).
# Gom từ bản Aegis 2026-11-16 (Yên Quốc Tinh Vệ ở 71/72/73/528-530 người dùng đã giết xác nhận tên vàng). Thêm tên mới thì ghi vào đây.
# id bản đồ -> ((tên tinh anh, cấp thấp nhất, cấp cao nhất), ...): chế độ Săn Tinh Anh (tactu_tinhanh_xq) chọn bản đồ từ bảng này
QUAITINHANH_MAP = {
    4: (('Đạo Điền Thủ Vệ', 6, 9),), 5: (('Gà Đế Vương', 6, 9),), 6: (('Thỏ Đế Vương', 6, 9),), 7: (('Đạo Điền Thủ Vệ', 6, 9),),
    8: (('Gà Đế Vương', 6, 9),), 9: (('Thỏ Đế Vương', 6, 9),), 11: (('Quy Thừa Tướng', 46, 49),), 12: (('Quy Thừa Tướng', 46, 49),),
    13: (('Quy Thừa Tướng', 46, 49),), 14: (('Quy Thừa Tướng', 46, 49),), 15: (('Quy Thừa Tướng', 46, 49),),
    21: (('Giang Dương Đại Đạo', 26, 29),), 31: (('Triệu Quốc Tinh Vệ', 67, 70),), 32: (('Triệu Quốc Tinh Vệ', 67, 70),),
    33: (('Triệu Quốc Tinh Vệ', 67, 70),), 42: (('Oan Quỷ', 26, 29),), 51: (('Tần Quốc Tinh Vệ', 71, 74),),
    52: (('Tần Quốc Tinh Vệ', 71, 74),), 53: (('Tần Quốc Tinh Vệ', 71, 74),), 61: (('Sở Quốc Tinh Binh', 16, 19),),
    62: (('Sở Quốc Tinh Binh', 16, 19),), 63: (('Sở Quốc Tinh Binh', 16, 19),), 71: (('Yên Quốc Tinh Vệ', 61, 63),),
    72: (('Yên Quốc Tinh Vệ', 61, 63),), 73: (('Yên Quốc Tinh Vệ', 61, 63),), 81: (('Ác Thiếu Gia', 21, 23),),
    82: (('Ác Thiếu Gia', 21, 23),), 89: (('Tiểu Đội Trưởng', 30, 33),), 111: (('Gấu Xám', 40, 43),), 112: (('Gấu Xám', 40, 43),),
    131: (('Tần Bộ Tiên Phong', 35, 38),), 132: (('Thủ Lĩnh Cường Đạo', 33, 36),), 141: (('Ác Bá', 27, 30),), 142: (('Ác Bá', 27, 30),),
    151: (('Đốc Công Kênh Trịnh Quốc', 51, 54),), 152: (('Đốc Công Kênh Trịnh Quốc', 51, 54),),
    153: (('Đốc Công Kênh Trịnh Quốc', 51, 54),), 155: (('Thủ Lĩnh Thổ Phỉ', 34, 37),), 161: (('Kiến Lính', 6, 9), ('Ếch Tinh', 6, 9)),
    162: (('Kiến Lính', 6, 9), ('Ếch Tinh', 6, 9)), 163: (('Bò Cạp Độc', 35, 38), ('Nhện Độc', 35, 38)),
    164: (('Bò Cạp Độc', 35, 38), ('Nhện Độc', 35, 38)), 171: (('Võng Lượng Quỷ', 56, 59),), 172: (('Võng Lượng Quỷ', 56, 59),),
    173: (('Võng Lượng Quỷ', 56, 59),), 174: (('Võng Lượng Quỷ', 56, 59),), 181: (('Tiểu Đội Trưởng', 30, 33),),
    182: (('Yên Bộ Tiên Phong', 35, 38),), 211: (('Ác Bá', 27, 30),), 231: (('Đăng Hồn', 35, 38),), 241: (('Thủ Lĩnh Cường Đạo', 33, 36),),
    242: (('Thủ Lĩnh Cường Đạo', 33, 36),), 243: (('Thủ Lĩnh Mã Tặc', 34, 37),), 251: (('Ác Thiếu Gia', 21, 23),),
    261: (('Lang Yêu Thủ Lĩnh', 35, 38),), 262: (('Lang Yêu Thủ Lĩnh', 35, 38),), 263: (('Sài Cẩu Vũ Giả', 35, 38),),
    264: (('Sài Cẩu Vũ Giả', 35, 38),), 265: (('Thuỷ Tặc Thủ Lĩnh', 40, 43),), 266: (('Thuỷ Tặc Thủ Lĩnh', 40, 43),),
    271: (('Triệu Cung Tiên Phong', 35, 38),), 272: (('Triệu Cung Tiên Phong', 35, 38),), 281: (('Tinh Tinh Vương', 16, 19),),
    282: (('Giáp Trùng Đại Tướng Quân', 16, 19),), 283: (('Gấu Đen', 16, 19),), 284: (('Sở Quốc Tinh Binh', 16, 19),),
    501: (('Võng Lượng Quỷ', 50, 54),), 502: (('Võng Lượng Quỷ', 55, 59),), 503: (('Quyền Pháp Sư Thủ Lĩnh', 60, 64),),
    504: (('Khô Lâu Thị Vệ', 120, 124),), 505: (('Khô Lâu Thị Vệ', 125, 129),), 506: (('Hư Lăng Đạo Nhân', 130, 134),),
    507: (('Hư Lăng Đạo Nhân', 135, 139),), 508: (('Bệnh Ma', 140, 144),), 509: (('Bệnh Ma', 145, 149),),
    510: (('Tần Quốc Tinh Vệ', 125, 129),), 511: (('Tần Quốc Tinh Vệ', 130, 134),), 512: (('Triệu Quốc Tinh Vệ', 135, 139),),
    513: (('Triệu Quốc Tinh Vệ', 140, 144),), 514: (('Thực Ma', 83, 86),), 515: (('Thực Ma', 83, 86),), 516: (('Đậu Tướng Quân', 82, 85),),
    517: (('Đậu Tướng Quân', 82, 85),), 518: (('Đao Quỷ', 118, 121),), 519: (('Đao Quỷ', 118, 121),),
    520: (('Tử Vân Đạo Nhân', 104, 107),), 521: (('Quán Trung Ma', 109, 112),), 522: (('Tử Vân Đạo Nhân', 104, 107),),
    523: (('Quán Trung Ma', 109, 112),), 524: (('Thủ Lĩnh Thích Khách', 76, 79),), 525: (('Thủ Lĩnh Thích Khách', 76, 79),),
    526: (('Thủ Lĩnh Thích Khách', 76, 79),), 527: (('Thủ Lĩnh Thích Khách', 76, 79),), 528: (('Yên Quốc Tinh Vệ', 61, 64),),
    529: (('Yên Quốc Tinh Vệ', 61, 64),), 530: (('Yên Quốc Tinh Vệ', 61, 64),), 531: (('Thần Binh', 111, 114),),
    532: (('Thần Binh', 111, 114),), 549: (('Tôm Hùm Chúa Đông Hải', 60, 65), ('Cua Đại Tướng', 60, 65)),
}
# 27 bản đồ tips không ghi Tinh Anh (Khốn Ma Trận, Tướng Quân Cổ Mộ, Hư Lăng Động, Cầu Cửu Khúc...; cấp quái thường đã gặp ở
# bando_xq.CAPQUAI_DAGAP_MAP) cũng cho Săn Tinh Anh (người dùng 16/11). Chưa biết tên => tên rỗng TENTINHANHCHUARO, khoảng cấp Tinh Anh
# ĐOÁN = cấp cao nhất quái thường +1 .. +15 (người dùng 16/11): bản đồ có tips chỉ hơn +1~+5 (Yên Trường Thành quái 56~58 / Tinh Anh 61~63, Vu Sơn 32~34 /
# 35~38) nhưng Hầm Vạn Nhân 1 quái 80~83 mà Tinh Binh Oan Linh cấp 93 (+10, người dùng 16/11 ảnh chụp; khoảng +1~+5 cũ bỏ sót).
# Đoán rộng thì tự sửa: con nhận theo cấp chết không rơi Lam Kim bị ghi "khong" ở _internal/tinhanhhoc.json; con cao hơn khoảng thì log
# "Nghi Tinh Anh" để chỉnh lại khoảng ở đây. Bản đồ đã thấy tên thật ghi ở QUAITINHANHDATHAY_MAP (nhận theo tên, giết xong là xong bản đồ)
TENTINHANHCHUARO = ""
SOCAPTINHANHDOAN = (1, 15)
QUAITINHANHDATHAY_MAP = {
    331: (('Tinh Binh Oan Linh', 84, 98),),     # Hầm Vạn Nhân 1: thấy cấp 93 (16/11)
    # Tru Tiên Trận 1: Thương Quỷ (con bò) cấp 119, quái thường 110~113 (người dùng 24/11 ảnh chụp). Khoảng đoán cũ 121~135 (cấp quái đã
    # ghi 110~120 +1~+15) bỏ sót => bot dò hết bản đồ không đánh, sang Tru Tiên Trận 2
    391: (('Thương Quỷ', 118, 125),),
}
for _idbando, _ds in QUAITINHANHDATHAY_MAP.items():
    QUAITINHANH_MAP.setdefault(_idbando, _ds)
for _idbando, (_capthap, _capcao) in CAPQUAI_DAGAP_MAP.items():
    QUAITINHANH_MAP.setdefault(_idbando, ((TENTINHANHCHUARO, _capcao + SOCAPTINHANHDOAN[0], _capcao + SOCAPTINHANHDOAN[1]),))
# Cả bản đồ bot tự ghi cấp quái sau 16/11 (_internal/capquaibando.json, ghicapquaibando đã lọc thành / phó bản): 22/11 Tru Tiên Trận 1
# (391, tips trống, không có trong CAPQUAI_DAGAP_MAP) đã ghi 110~120 nhưng không hiện trong Săn Tinh Anh. Đọc 1 lần lúc khởi động =>
# bản đồ mới ghi thì mở lại bot mới hiện. Khoảng ghi có thể gồm cả chính con Tinh Anh nên đoán từ cấp cao nhất vẫn rộng (+1~+15)
for _idbando, (_capthap, _capcao) in _laycapquaidahoc().items():
    QUAITINHANH_MAP.setdefault(_idbando, ((TENTINHANHCHUARO, _capcao + SOCAPTINHANHDOAN[0], _capcao + SOCAPTINHANHDOAN[1]),))
QUAITINHANHs = frozenset(ten for ds in QUAITINHANH_MAP.values() for ten, _, _ in ds if ten != TENTINHANHCHUARO)


# Tên trong tips khác tên thật trong game (đối chiếu _internal/vitridoituong 16/11): tips "Thủ Lĩnh Lang Yêu" -> game "Lang Yêu Thủ Lĩnh",
# "Thủ Lĩnh Thủy Tặc" -> "Thuỷ Tặc Thủ Lĩnh", "Sài Cẩu Võ Giả" -> "Sài Cẩu Vũ Giả", "Kênh" -> "Kệnh"; tips Bành Thành (503) ghi
# Võng Lượng Quỷ nhưng gặp thật "Quyền Pháp Sư Thủ Lĩnh". Người dùng: mỗi bản đồ 1 con Tinh Anh, tên không cố định, thường là quái thường
# của bản đồ được cường hoá (vd "Lang Yêu Thủ Lĩnh" hoặc "Ngưu ... Thủ Lĩnh") => so tên đã chuẩn hoá (bỏ dấu khác nhau, không kể thứ tự
# chữ "Thủ Lĩnh") + mọi tên có "Thủ Lĩnh"/"Thống Lĩnh"/"Vũ Giả" ở đầu/cuối đều tính là Tinh Anh
_THAYTENTINHANHs = (("Thuỷ", "Thủy"), ("Vũ Giả", "Võ Giả"), ("Kệnh", "Kênh"))
_HAUTOTINHANHs = ("Thủ Lĩnh", "Thống Lĩnh", "Võ Giả")


def _chuanhoatentinhanh(ten):
    ten = " ".join(ten.split("(")[0].replace("\xa0", " ").split())
    for cu, moi in _THAYTENTINHANHs:
        ten = ten.replace(cu, moi)
    for hauto in _HAUTOTINHANHs:
        if ten.startswith(hauto + " "):
            ten = ten[len(hauto) + 1:] + " " + hauto
    return ten


_QUAITINHANHCHUANHOAs = frozenset(_chuanhoatentinhanh(ten) for ten in QUAITINHANHs)
# Tên Tinh Anh của RIÊNG từng bản đồ (đã chuẩn hoá)
_TENTINHANHBANDO_MAP = {idbando: frozenset(_chuanhoatentinhanh(ten) for ten, _, _ in ds if ten) for idbando, ds in QUAITINHANH_MAP.items()}


def is_tentinhanhcuabando(ten, idbando):
    # Tên đúng là Tinh Anh ghi cho chính bản đồ này (không phải tên Tinh Anh của bản đồ khác trùng tên quái thường ở đây)
    return bool(ten) and _chuanhoatentinhanh(ten) in _TENTINHANHBANDO_MAP.get(idbando, ())


# Mỗi loại quái thường của bản đồ đều có thể ra 1 biến thể Tinh Anh (người dùng 16/11), tên đủ kiểu => nhận thêm theo CẤP: Tinh Anh cao
# hơn hẳn quái thường cùng bản đồ (đo: Vu Sơn Sài Cẩu 32~33 / Trư Yêu 34, Sài Cẩu Vũ Giả 38; Chân Núi Đại Biệt Lang Yêu 33 / Ngưu Đầu Quái
# 33~34, Lang Yêu Thủ Lĩnh 37; Yên Trường Thành lính 56~58, Tinh Vệ 61~63). Bản đồ có trong QUAITINHANH_MAP: quái cấp nằm trong khoảng
# cấp Tinh Anh của bản đồ đó (đúng khoảng ghi trong tips, người dùng: cấp Tinh Anh giống mô tả bản đồ, chỉ tên thay theo loại quái) là
# Tinh Anh. Bỏ quái sự kiện đi khắp nơi, bảo bảo, quái Phong Yêu Kính mượn ID bản đồ
CAPTINHANH_MAP = {idbando: (min(a for _, a, _ in ds), max(b for _, _, b in ds)) for idbando, ds in QUAITINHANH_MAP.items()
                  if all(a for _, a, _ in ds)}
# Khoá cấp CHỈ để xếp thứ tự (giao diện chọn bản đồ + thứ tự đi), không dùng nhận Tinh Anh: bản đồ cấp đoán (+1~+15) mà có bản đồ
# cùng cấp quái thường đã thấy Tinh Anh thật thì xếp theo cấp thật đó. Người dùng 27/11: Tru Tiên Trận 2/3 đoán 114~128 xếp trước
# Trận 1 (Thương Quỷ thật 118~125) thành thứ tự 2, 3, 1; nay 3 trận cùng khoá 118~125 => theo id 1, 2, 3
_CAPQUAITHUONG_MAP = dict(_laycapquaidahoc())
_CAPQUAITHUONG_MAP.update(CAPQUAI_DAGAP_MAP)
_CAPTINHANHTHAT_THEOQUAI = {_CAPQUAITHUONG_MAP[i]: CAPTINHANH_MAP[i] for i in QUAITINHANHDATHAY_MAP
                            if i in _CAPQUAITHUONG_MAP and i in CAPTINHANH_MAP}
CAPXEPTINHANH_MAP = {i: (_CAPTINHANHTHAT_THEOQUAI.get(_CAPQUAITHUONG_MAP.get(i), cap)
                         if all(ten == TENTINHANHCHUARO for ten, _, _ in QUAITINHANH_MAP[i]) else cap)
                     for i, cap in CAPTINHANH_MAP.items()}
# Trộm Bảo Phi Tặc (quái sự kiện đi khắp nơi) không phải Tinh Anh (người dùng 18/11)
TENKHONGPHAITINHANHs = frozenset(("Hung Nô Tàn Bạo", "Kỵ Binh Tướng Lĩnh", "Chiến Quốc Tống Bảo Tiểu Yêu", TROMBAOPHITAC))
_MAUCAPTINHANH = re.compile(r"[Cc]ấp\s*(\d+)")
_MAUBAOTHUCOCHU = re.compile(r"\(\s*(?![Cc]ấp)\S")


def laycaptrongten(tenthucte):
    # "Sài Cẩu Vũ Giả (cấp 38)" -> 38; không có cấp -> None
    m = _MAUCAPTINHANH.search(tenthucte or "")
    return int(m.group(1)) if m else None


def is_quaitinhanh(ten, idbando = None, cap = None):
    # ten: tên đã bỏ "(cấp ...)" hoặc còn (chỉ so phần trước "("). idbando + cap (cấp đọc từ tên thực tế) có thì xét thêm theo cấp
    if not ten:
        return False
    tenchuan = _chuanhoatentinhanh(ten)
    if tenchuan in _TENTINHANHBANDO_MAP.get(idbando, ()):
        return True
    # Tên Tinh Anh của bản đồ KHÁC / tên đuôi "Thủ Lĩnh"...: biết bản đồ + cấp thì phải đúng khoảng cấp Tinh Anh bản đồ này. Log 342
    # (Thỏ) 16/11 19:05: Linh Cốc Động 2 có quái THƯỜNG "Võng Lượng Quỷ" (Tinh Anh ở Trường Bạch Sơn 171-174 cấp 56~59) => giết 22 con
    # tưởng Tinh Anh, báo xong bản đồ, sang Linh Cốc Động 3 khi chưa tìm thấy Tinh Anh thật
    if tenchuan in _QUAITINHANHCHUANHOAs or any(tenchuan.endswith(" " + hauto) for hauto in _HAUTOTINHANHs):
        if cap is None or idbando not in CAPTINHANH_MAP:
            return True
    if cap is None or idbando not in CAPTINHANH_MAP:
        return False
    if is_tenkhongthetinhanh(ten):
        return False
    capthap, capcao = CAPTINHANH_MAP[idbando]
    return capthap <= cap <= capcao


def is_tenkhongthetinhanh(ten):
    # Quái sự kiện đi khắp nơi, bảo bảo, quái Phong Yêu Kính mượn ID bản đồ: không bao giờ là Tinh Anh dù cấp cao
    if not ten or _chuanhoatentinhanh(ten) in TENKHONGPHAITINHANHs or "Bảo Bảo" in ten or "Quốc Kính" in ten or "Tàn Phách" in ten:
        return True
    # Bảo thú người chơi "Cương Thi ( Gold-1 )" (ngoặc ghi tên chủ, không phải "(cấp ..)"): không phải Tinh Anh (log 342 / 418 16/11:
    # Cương Thi cấp 100 ở Linh Cốc Động 2, cấp 40-50 ở Ranh Giới Đầm Lầy; khoảng đoán rộng thì kẻo đánh nhầm)
    return bool(_MAUBAOTHUCOCHU.search(ten))


# Bảo thú vật phẩm (cả Thuỷ Bình) không tấn công / không mất máu
TENMUCTIEUKHONGTANCONGs = (*BAOTHUVATPHAMs, "Tần QuốcBinh Sĩ", "Triệu QuốcBinh Sĩ", QUYTOT, THIENBINH, DAUBINH, "CAVE1", "CAVE.2", 'Đỗ Độc', 'Ôn Thần', "Liễu Vọng Tháp")
# "Chiến Quốc Tống Bảo Tiểu Yêu" dài 28 ký tự / 39 byte UTF-8 nhưng tên đối tượng (+0x10AC) không bị cắt 31 byte như tên vật phẩm:
# log [DI CHUYỂN] (đọc qua get_tendoituong) các acc 195/216/286/287 đều ra đủ tên, nên so khớp nguyên tên được
TENBOSSBUFFMAOSONs = ("Mã Quỷ", "Lương Hưng", "Yến Thập Tam", "Tư Tà", "Thủ Lĩnh Thành Kiều", TROMBAOPHITAC, "Bảo Hộp Phi Tặc",
                      "Tướng Quân Dũng", "Lăng Mộ Tà Linh", "Đường Truy", "Thế Công Minh", "Thạch Tướng Quân", "Cơ Quan Tướng Quân",
                      "Hào Quật", "Thủ Lĩnh Thích Khách", "Chiến Quốc Tống Bảo Tiểu Yêu",
                      # Người dùng 27/11: Kỵ Binh Tướng Lĩnh, Đoạt Bảo Mã Tặc (TENMATAC, tactu_matac_xq)
                      "Kỵ Binh Tướng Lĩnh", "Đoạt Bảo Mã Tặc")

# Hàng việc (tab Nhiệm vụ, tactu_hangviec_xq): mã việc -> tên, theo thứ tự mặc định; việc có vòng thì đặt được giới hạn số vòng
VIECHANG_MAP = {"sumon": "Sư môn", "danhvong": "Danh Vọng", "thienxu": "Thiên Xu Viện"}
# Việc đi chung theo đội phó bản (bảng "Phó bản chung", tactu_doiphoban_xq): mã việc -> tên, theo thứ tự mặc định; việc có vòng thì đặt
# được giới hạn số vòng
VIECDOI_MAP = {"sugia": "Sư Gia", "tapkich": "Tập Kích", "langlyson": "Lăng Ly Sơn", "thanhkieu": "Thành Kiều", "phongyeukinh": "Phong Yêu Kính"}
VIECCOVONGs = ("tapkich", "langlyson", "thanhkieu", "phongyeukinh")
# Việc riêng hiện cuối bảng hàng việc (bấm Làm ngay / thiết lập chung một chỗ) nhưng không chạy theo hàng việc
VIECRIENG_MAP = {"matac": "Mã Tặc", "keocap": "Kéo cấp acc gà"}

# Cấp kết thúc mặc định (ô "Kéo tới cấp" trên giao diện, lưu ở s["capketthuc"]; bản lưu cũ không có thì dùng số này).
# Điểm thành thạo kỹ năng bang mỗi lần acc gà lên cấp (người dùng xác nhận 2026-11-14): cấp 1-30 không có, 31-35 1200, cứ 5 cấp thêm 400.
# Đo dàn 1002-1005 (2026-11-14, đăng nhập song song): tới 50 mất 42 phút, 60 mất 83, 64 mất 103 (từ 60 đánh boss nên vòng dài 12-14
# phút) => điểm / phút mỗi acc gần ngang nhau (~745-760), nhưng mỗi vòng Phong Yêu Kính đốt 1 món Lam Kim mà boss không rơi lại:
# dừng 50 ~48 nghìn điểm / món, 60 ~41 nghìn, 64 ~36 nghìn -> người dùng chọn dừng 50
CAPKETTHUCKEOCAP = 50
