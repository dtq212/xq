# Kéo cấp acc gà (acc clone) để tăng kỹ năng bang: thành viên bang lên cấp thì kỹ năng bang phái nhận kinh nghiệm. Bật từ giao diện ở acc
# chính (nhân vật đang chọn), giao diện gửi luôn lệnh bật vai acc gà cho các cửa sổ cùng máy được chọn. Acc chính điều phối, báo giai đoạn
# qua shared_data ("_keocap"), acc gà đọc rồi tự làm phần của mình. Quy trình (dò theo log [LỆNH GAME] người dùng làm tay 2026-11-01):
#   tanthu  (acc gà): Tân Thủ Thôn (95, 123) Thần Tiên Gia Gia: "1. Thủ Thuật Nhỏ" (tallk welcome.1) -> "1. Hoàn thành nhiệm vụ"
#           (welcome.2); [tuỳ chọn: look lại -> "Nhập Code Tân Thủ" -> "codett + welcome2d", MENUCODETANTHU]; look lại -> "2. Nhận thời
#           gian x2 kinh nghiệm" (welcome.40) -> "3. 4 giờ". Code tân thủ bỏ 2026-11-07, mở lại 2026-11-12 nên thành ô tuỳ chọn;
#           thưởng code còn trong túi vẫn dùng (VATPHAMTANTHUs; Chiến Quốc Lệnh x3 "use !"). Tập hợp / bãi: acc chính give mỗi acc gà 1
#           Cửu Long Thần Hỏa Trảo (TRAOKEOCAPs), acc gà đeo; thu hồi thì tháo ("remove 7"), trả cùng đồ Lam Kim. Acc gà tự cộng điểm
#           tiềm năng dư vào Nại lực (ô 4)
#   taphop  : mọi người về Tân Thủ Thôn (143, 143); acc chính lập nhóm, mời acc gà ("team + <ID>"), mời vào bang ("org invite <ID>", log
#           acc 192 mời 187); acc gà đồng ý bằng lệnh của hộp Yes/No ("team + <ID chính>", "org join <ID chính>")
#   bai     : acc chính tới bãi (Hồi Thành Phù / phù Tân Thủ Tiên Cô / chạy bộ theo Đi tới bản đồ) đánh theo lộ trình điểm đánh của bản đồ (chưa
#           có mẫu thì tự đề xuất / dò); acc gà bật Theo sau acc chính (tự tìm đường / phù sang bản đồ khác). Cấp thấp nhất của acc gà đủ
#           cấp đích thì sang bãi kế: Ba Khâu -> 10, Thuý Hoa Sơn -> 20, Cự Lộc -> 30, Ranh Giới Đầm Lầy -> 35
#   gomdo   : trước Phong Yêu Kính (người dùng dặn 2026-11-16): acc chính đứng yên, mọi acc gà tới cạnh give hết đồ Lam Kim về acc
#           chính (quá THOIGIANGOMDOKC giây thì thôi), rồi mới sang phongyeu; acc chính chia dần cho acc đốt (SOMONCHIAMOILUOTKC món/lượt)
#   phongyeu: Phong Yêu Kính (tactu_langlyson_xq) tới khi mọi acc gà cấp CAPKETTHUC: người give (lập nhóm, đốt đồ) là 1 ACC GÀ có đồ Lam
#           Kim (quái theo cấp người mở thì acc gà mới có kinh nghiệm), acc chính là thành viên dò bản đồ đánh quái. Trong phó bản acc gà
#           bật "Tự động sử dụng kỹ năng" thì dò đánh như mọi người, tắt thì đứng yên cạnh Truyền Tống Thỏ Yêu; người give ra mở vòng mới
#           theo "Điều kiện thoát" ở cấu hình Phong Yêu Kính (mặc định đủ 2 boss là ra). Bản đồ mượn ID Tây Thành (khó đi) thì ra ngay mở bản đồ khác
#           Đồ Lam Kim để ở acc chính: ngoài phó bản, acc gà nhận đồ (người give, không thì ID nhỏ nhất) hết đồ thì acc chính đứng yên, acc
#           gà đó tới cạnh, acc chính "give <ID acc gà> <đồ>#1 ... $0" (chuyển thẳng, không cần đồng ý, như giao đồ) mọi món đủ cấp acc gà
#   thuhoi  : mọi acc gà tới cấp kết thúc (người dùng dặn): trước khi xong, acc chính đứng yên (đang trong Phong Yêu Kính thì Thỏ Yêu về
#           Chu Quốc), acc gà còn đồ Lam Kim tới cạnh give trả hết về acc chính; mọi acc gà báo đã trả (quá THOIGIANTHUHOIKC giây thì
#           thôi); acc gà trả cả Tạo Hoá Đơn / Bổ Tâm Đơn / Phi Hành - Hồi Thành - Hồi Bang Phù + toàn bộ ngân lượng, acc chính đem
#           bán ở Chủ Tiệm Y Dược (phù bán hết, Lam Kim cấp 25 giữ 8 món), trả cả sách "Nhập Môn" để acc chính cất
#           kho (_catsachthuhoikc) rồi mới sang xong
#   acc phụ (máy khác nối LAN, bật "Làm acc phụ"): tự nhận acc chính đang kéo cấp thấy qua LAN; tập hợp / bãi (cấp 1 -> 35) vào nhóm
#           acc chính (còn chỗ sau acc gà) và theo sau như acc gà (người dùng dặn 2026-11-03), Phong Yêu Kính làm thành viên dò đánh quái
#           như acc chính. Không nhận thưởng tân thủ / vào bang, không tính cấp acc phụ khi chọn bãi / kết thúc
# Acc gà Theo sau tự phù / chạy sang bản đồ của acc chính; không đủ tiền Hồi Thành Phù mà chạy bộ xa thì bộ tìm đường chung
# (_lapbuocditoibando) hồi môn phái về Tân Thủ Thôn (chưa vào môn phái) rồi phù tiếp.
# Mixin của TacTu (tactu_xq.py): chỉ chứa hàm, trạng thái (self._keocap...) khởi tạo trong TacTu.__init__
import json
import math
import os
import time
import unicodedata

from hangso_xq import *
from tienich_xq import phatam, canhbao, taicauhinhphongyeu, taivitrithoyeu, laydieukienrapykeocap, taigiaodienkeocap, _thumucthietlap
from thongbao_xq import baosuco
from giaodo_xq import taolenhgiao
from tactu_catkho_xq import LYDOCATKHO_KEOCAP
from tactu_langlyson_xq import CAPDOLAMKIMTOITHIEU, laytenthoyeu, SOBOSSPHONGYEU, THOIGIANTOITHIEUPY, THOIGIANTOIDAPY, MAMAULAMKIM

BANDO_BAKHAU = 162
BANDO_THUYHOASON_KC = 82
NPCTHANTIENGIAGIA = ("Thần Tiên Gia Gia", 95, 123)
DIEMTAPHOPKEOCAP = (143, 143)
# Thu hồi: acc chính về Tân Thủ Thôn đứng cách điểm tập hợp không quá chừng này ô rồi mới chờ acc gà trả đồ
KHOANGCACHTAPHOPTHUHOIKC = 8.
# Đuôi lệnh của từng menu lần lượt (so với lệnh lựa chọn "tallk <id NPC># <đuôi>", không theo số thứ tự vì menu đổi theo nhiệm vụ)
MENUNHIEMVUTANTHU = ("welcome.1", "welcome.2")
# Code tân thủ đã bỏ (2026-11-07): trả nhiệm vụ xong NPC tự bật lại menu chính, đóng rồi look lại -> "2. Nhận thời gian x2 kinh
# nghiệm" -> "3. 4 giờ". Menu sau khi trả (log acc 526-528): [welcome.20, .40, .90, .80, .84, .11747] khớp 6 dòng trên màn hình
# "1. Truyền Thuyết Sáng Lập Bang, 2. Nhận thời gian x2, 3. Xin đóng băng, 4. VIP là gì, 5. x2 VIP, 6. Gói dùng thử VIP"
# => x2 là welcome.40 (welcome.20 là Truyền Thuyết, chọn nhầm ra hội thoại welcome.21). "3. 4 giờ" chưa dò đuôi: chọn thứ tự 2
MENUX2KINHNGHIEM = ("welcome.40", 2)
# Acc gà cấp >= CAPKIEMTRAX2KC lúc bật kéo cấp (acc cũ kéo tiếp, người dùng dặn 2026-11-23): cửa sổ nhiệm vụ (thẻ Giang Hồ, mục "Viện Trợ
# Trò Chơi") không còn dòng "Thời Gian Nhân Đôi" / "Thời Gian Nhân Ba" thì về Thần Tiên Gia Gia nhận x2 4 giờ (MENUX2KINHNGHIEM). Gửi
# "quest list" rồi chờ THOIGIANCHOX2KC giây mới đọc; quá THOIGIANNHANX2KC giây chưa nhận xong thì thôi
CAPKIEMTRAX2KC = 40
TENTHOIGIANNHANKC = "Thời Gian Nhân"
THOIGIANCHOX2KC = 5.
THOIGIANNHANX2KC = 300.
# Code tân thủ "welcome2d" (tuỳ chọn, ô "Acc gà nhập code welcome2d" trên giao diện, lưu keocap.json "dungcode"): admin mở lại 2026-11-12
# nhưng có thể đóng bất cứ lúc nào. Luồng cũ (log 2026-11-01): look -> "6. Nhập Code Tân Thủ" (welcome.11747) -> welcome.13747 mở hộp
# "Xin nhập mã Code Tân Thủ" -> gửi "codett + welcome2d". Thưởng: lên cấp 8, Cửu Long Thần Hỏa Trảo, Hoàng Sa Chi Tâm, Thủy Bình,
# 3 Chiến Quốc Lệnh x3. Lúc code đóng welcome.11747 thành "Gói dùng thử VIP" nên chọn theo NHÃN chứa "code" (đuôi chỉ dùng khi
# không đọc được nhãn): mỗi menu là (đuôi dự phòng, chữ trong nhãn)
MENUCODETANTHU = (("welcome.11747", "code"), ("welcome.13747", "code"))
LENHCODETANTHU = "codett + welcome2d"
# Gửi code xong chờ thưởng (lên cấp 8 / có món thưởng trong túi) tối đa chừng này giây rồi mới dùng đồ
THOIGIANCHOTHUONGCODE = 15.
# Code cấp 60 "welcome2d60" (bản cập nhật 2026-11-23, người dùng báo; phải cấp >= 60 mới nhập được): thưởng 30 Chén Bạc, mỗi cái
# "[Có thể sử dụng] ... 1.000.000 Kinh Nghiệm" => 60 lên ~70. Ô "Cấp 60: code welcome2d60 + Chén Bạc" (keocap.json "dungcode60").
# Làm ở acc gà lúc THU HỒI, TRƯỚC khi trả đồ / ngân lượng (_buoccode60kc): còn trong bang (xong mới bị trục xuất) nên lên 61-70 vẫn cộng
# điểm kỹ năng bang (3600-4000 mỗi cấp), còn tiền đi đường. Chưa dò menu: giả định cùng lựa chọn "Nhập Code Tân Thủ" ở Thần Tiên Gia Gia
# như welcome2d (chọn theo nhãn chứa "code"), gửi "codett + welcome2d60"
CAPCODE60 = 60
LENHCODE60 = "codett + welcome2d60"
CHENBACs = ("Chén Bạc",)
# Gửi code xong chờ Chén Bạc vào túi tối đa chừng này giây; không có thì coi như code lỗi / đã nhập trước đó, bỏ qua
THOIGIANCHOTHUONGCODE60 = 15.
SOLANNHAPCODE60 = 2
# Dùng Chén Bạc: mỗi cái cách nhau chừng này giây; kinh nghiệm đang đủ lên cấp thì chờ tự tăng cấp ("gift upgrade") trước (tối đa
# THOIGIANCHOTANGCAPCHENBAC giây) cho kinh nghiệm không dồn quá nhiều. Tự tăng cấp được nâng tối thiểu tới CAPTANGCAPCHENBAC.
# Cách dùng chưa dò: thử "use !" như Chiến Quốc Lệnh x3; SOLANDUNGKHONGGIAMCHENBAC lần liền số Chén Bạc không giảm thì đổi sang "use2"
GIANCACHDUNGCHENBAC = 1.5
THOIGIANCHOTANGCAPCHENBAC = 10.
CAPTANGCAPCHENBAC = 75
SOLANDUNGKHONGGIAMCHENBAC = 3
# Cả bước code 60 + Chén Bạc tối đa chừng này giây (gồm đường về Tân Thủ Thôn); acc chính kéo dài chờ thu hồi khi acc gà báo đang làm
THOIGIANCODE60KC = 600.
# Pháp bảo Cửu Long Thần Hỏa Trảo: acc chính có sẵn (người dùng để 4 cái trong túi), give mỗi acc gà 1 cái lúc tập hợp / ở bãi, acc gà
# đeo (use2); thu hồi: acc gà "remove 7" tháo pháp bảo rồi give trả cùng đồ Lam Kim
TRAOKEOCAPs = ("Cửu Long Thần Hỏa Trảo", "Cửu Long Thần Hoả Trảo")
GIANCACHDOCTRAOKC = 3.
# Thu hồi: túi đầy thì "remove 7" không tháo được Trảo; vứt món này trước cho có ô trống (người dùng dặn 2026-11-08). Vứt xong chừng này
# giây mới tháo (chờ máy chủ cập nhật túi)
VATPHAMVUTKHIDAYTUIKC = ("Chiến Quốc Bảo Điển",)
GIANCACHVUTDOTHAOTRAOKC = 2.
# Give Trảo xong chừng này giây mới xét acc gà đã nhận chưa / give lại, tối đa SOLANGIAOTRAOKC lần mỗi acc gà
GIANCACHGIAOTRAOKC = 6.
SOLANGIAOTRAOKC = 3
# Tập hợp: chờ acc gà nhận Trảo tối đa chừng này giây rồi vẫn đi bãi (ở bãi vẫn đưa tiếp)
THOIGIANCHOTRAOKC = 60.
SOLANTHAOTRAOKC = 3
# Cửu Long Thần Hỏa Trảo cần nhân vật cấp 2 mới đeo được (người dùng báo 2026-11-08): acc gà dưới cấp này không use2 Trảo, báo
# trao "chuacap" (acc chính không give, tập hợp không chờ), tới cấp thì báo "" để acc chính give ở bãi
CAPDEOTRAOKC = 2
# Acc gà tự cộng điểm tiềm năng dư vào ô 4 Nại lực (người dùng dặn 2026-11-07): "gift a b c d e" = TỔNG MỚI 5 ô
OTIEMNANGKEOCAP = 3
GIANCACHCONGTIEMNANGKC = 10.
# Thưởng code tân thủ dùng ngay: (các cách viết dấu, cách dùng); tên ô hành trang tối đa 31 byte nên so đầu tên. "use !" không ăn với
# cả 3 món (acc 282-291 2026-11-01), người dùng dặn chỉ gửi "use2 <id>#" (lệnh nút Xác Nhận), không cần "use" trước:
#   "use2"  : pháp bảo / đeo vai, "use2 <id>#"
#   "baothu": bảo thú vật phẩm, dùng không mất khỏi túi: đặt vào ô mở cuối cùng để phần tự triệu hồi bảo thú vật phẩm lo (cũng "use2",
#             VATPHAMDUNGUSE2s; gọi lại khi bảo thú mất)
VATPHAMTANTHUs = ((("Cửu Long Thần Hỏa Trảo", "Cửu Long Thần Hoả Trảo"), "use2"), (("Hoàng Sa Chi Tâm",), "use2"), (THUYBINHs, "baothu"))
# Chỉ dùng đúng món "Chiến Quốc Lệnh x3", không đụng "Chiến Quốc Lệnh" thường (người dùng dặn)
CHIENQUOCLENHX3 = "Chiến Quốc Lệnh x3"
# Tên ô hành trang dài từ chừng này byte (UTF-8) trở lên là có thể đã bị cắt (ô chỉ 31 byte)
SOBYTETENBICAT = 30
SOLANDUNGVATPHAMTANTHU = 4
GIANCACHDOCVATPHAMSOTKC = 10.
SOLANDUNGCHIENQUOCLENH = 5
# Bật giữa chừng ngoài phó bản: mời bang lại tối đa chừng này lần mỗi acc gà chưa ghi nhận đã vào bang (đã ở bang thì lệnh vô hại)
SOLANMOIBANGGIUACHUNG = 3
GIANCACHDUNGVATPHAMKC = 1.5
# (bản đồ, cấp đích): acc gà thấp nhất chưa tới cấp đích thì acc chính đánh ở bản đồ đó
BAIKEOCAPs = ((BANDO_BAKHAU, 10), (BANDO_THUYHOASON_KC, 20), (BANDO_CULOC, 30), (BANDO_RANHGIOIDAMLAY, 35))
# Acc gà đồ đệ quá cấp này (chưa ghi bái sư) thì coi như đã bái sư: bỏ bước bái sư, chỉ nhớ để tới cấp kết thúc xuất sư
CAPTOIDANHANDODE = 30
# Đồ đệ tới cấp này là xuất sư được (người dùng xác nhận lại 14/11: cấp 50, trước ghi 60): xuất sư ngay, không chờ mọi acc gà tới cấp kết thúc, xong kéo tiếp như thường
CAPXUATSU = 50
# Giai đoạn acc chính đã rời Phong Yêu Kính (xuất sư / chờ acc chính 2 xuất sư): acc gà / acc phụ còn trong Phong Yêu Kính thì tự ra theo
# (_theosauchinhkc). "thuhoi" thì _buocthuhoiga tự ra, "xong" thì kết thúc luôn
GIAIDOANSAUPHONGYEUKCs = ("xuatsu", "chosudo", "tapkich")
# Ô "Cấp >= 52 đi Tập Kích" (keocap.json "tapkich50" giữ tên cũ; người dùng dặn 2026-11-23: Phong Yêu Kính quá chậm, mốc 40): acc gà thấp nhất
# đủ CAPTAPKICHKC thì acc chính lập nhóm chỉ với acc gà (acc phụ đứng ngoài, 2026-11-24), bật gom quái rồi bật Tập Kích Môn Phái (tactu_tapkich_xq, môn phái theo ô Tập Kích trên
# giao diện, không chọn thì phái của mình) thay Phong Yêu Kính; acc gà theo sau acc chính, menu vào / Lễ Bao thành viên tự chọn.
# Tập Kích tự dừng (hết lượt / không vào được) thì quay lại Phong Yêu Kính
CAPTAPKICHKC = 52
# Kẹt vùng kín sau Tập Kích (_thoatvungkinkc): xét khi cách acc chính quá chừng này ô, mỗi GIANCACHXETKINKC giây tìm đường 1 lần, không có
# đường liền THOIGIANKINKC giây thì Hồi Môn Phù; 2 lần dùng phù cách nhau ít nhất GIANCACHPHUKINKC giây
KHOANGCACHXETKINKC = 6.
GIANCACHXETKINKC = 3.
THOIGIANKINKC = 5.
GIANCACHPHUKINKC = 60.
# Đã quyết dùng phù thoát vùng kín: đứng yên gọi lại tối đa chừng này giây (chờ acc khác về thành xong, vận khí)
THOIGIANPHUKINTOIDA = 40.
# Người give (acc gà) ra Phong Yêu Kính theo "Điều kiện thoát" ở cấu hình Phong Yêu Kính (tienich_xq.DIEUKIENRAPYKEOCAPs: số boss,
# có chờ hết quái); hết quái = không thành viên nào (cùng bản đồ) còn mục tiêu liền chừng này giây; ở quá THOIGIANTOIDAPY thì thôi chờ
THOIGIANHETMUCTIEUPYKC = 10.
# Acc chính hơn người give (boss Phong Yêu Kính theo cấp người give) QUÁ chừng này cấp thì mọi "Điều kiện thoát" thành kiểu "85quai"
# (đủ 85% quái là ra, không tìm / đánh boss): người dùng dặn 2026-11-14, acc chính 100 đánh boss 55 trở xuống không rơi đồ, đi tìm boss
# phí thời gian. Chênh lệch <= mốc (acc gà kéo lên 60-70) thì đánh boss như cấu hình để có đồ Lam Kim đốt tiếp
CHENHLECHCAPKHONGDANHBOSSKC = 40
KHOANGCACHNOICHUYENKC = 3.
THOIGIANCHOMENUKC = 3.
SOLANTHUMENUKC = 3
GIANCACHMOINHOMKC = 5.
GIANCACHMOIBANGKC = 15.
# Xong kéo cấp: acc chính trục xuất khỏi bang acc gà có tên bắt đầu bằng tiền tố Kéo gà A-Z ("tiento" trong _internal/keogatudong.json,
# đang là "gacon") cho đỡ tốn chỗ bang. Lệnh "org banish <ID>" (log 364 Gạ 2026-11-14 06:20 trục xuất tay: client gửi "org info <ID>"
# rồi "org banish <ID>" kèm "org status"); bấm tay cách nhau ~2-4s nên mỗi người cách chừng này giây
GIANCACHTRUCXUATKC = 3.
# Tập hợp: quá chừng này giây acc gà chưa đồng ý vào bang thì vẫn đi bãi (báo log, vẫn mời tiếp lúc đứng ở Tân Thủ Thôn)
THOIGIANCHOBANGKC = 120.
# Acc gà bị acc chính mời vào nhóm liên tục quá chừng này giây mà chưa vào: tự rời nhóm cũ / tự gửi "team + <ID chính>" (_vaonhomchinhkc)
THOIGIANBIMOIKC = 8.
GIANCACHTUVAONHOMKC = 6.
# Acc gà tự kiểm tra bang ("desc user <ID mình>", _kiemtrabangkc): trước đây "org join" xong là đánh dấu đã vào bang luôn, join lỗi thì
# acc chính không mời lại nữa (người dùng báo 2026-11-08). Hỏi lúc bật, sau mỗi lần join GIANCACHKIEMTRABANGSAUJOIN giây, ngoài ra
# GIANCACHKIEMTRABANG giây 1 lần (sửa dabang lưu cũ sai / bị đá khỏi bang); trả lời hiện ở khung tin hệ thống nên đừng hỏi dày
GIANCACHKIEMTRABANG = 300.
GIANCACHKIEMTRABANGSAUJOIN = 3.
THOIGIANCHOKIEMTRABANG = 5.
SOLANHOIBANGLOI = 3
# Tới bãi chờ acc gà theo sang tối đa chừng này giây rồi mới đánh (có mặt mới được chia kinh nghiệm)
THOIGIANCHOGATOIBAI = 90.
# Phong Yêu Kính: người give tắt Phong Yêu Kính chừng này giây (hết đồ) thì acc chính chọn acc gà khác; ai tắt thì chừng này giây sau bật lại
THOIGIANDOINGUOIGIVE = 10.
THOIGIANBATLAIPYKC = 15.
GIANCACHDOCDOLAMKIMKC = 20.
THOIGIANBAOXONGKC = 20.
# Acc chính đưa đồ Lam Kim: đọc túi mình mỗi chừng này giây; give xong chừng này giây mới xét / gửi lại, tối đa SOLANGIAODOKC lần không giảm
GIANCACHDOCDOCHINHKC = 5.
GIANCACHGIAODOKC = 4.
SOLANGIAODOKC = 3
KHOANGCACHGIAODOKC = 3.
# Đưa đồ Lam Kim: mỗi lượt chỉ một acc di chuyển (acc gà trước), quá chừng này giây chưa đứng cạnh nhau thì đổi lượt
THOIGIANLUOTDIKC = 20.
# Acc gà đang chờ nhận đồ đọc lại túi mỗi chừng này giây
GIANCACHDOCDONHANKC = 3.
# Acc gà tới nhận đồ Lam Kim: không thấy acc chính trên màn hình mà toạ độ chia sẻ của nó vừa nhảy xa hơn chừng này ô (vừa ra Phong Yêu
# Kính / dùng phù: vài giây đầu game còn trả toạ độ cũ) thì chờ toạ độ đứng yên THOIGIANTOADOONDINHKC giây mới đi. Đo 2026-11-08 17:52:
# acc chính ra PYK về Chu (292,185) mà báo (94,137) của PYK, acc gà ở (300,191) tìm đường đi về hướng đó ra tận (263,158) rồi mới quay lại
BUOCNHAYTOADOKC = 15
THOIGIANTOADOONDINHKC = 1.5
# Đưa đồ xong chờ acc gà báo đã có đồ tối đa chừng này giây
THOIGIANCHONHANDOKC = 30.
GIANCACHROINHOMKC = 5.
# Thu hồi đồ Lam Kim về acc chính trước khi xong: chờ acc gà trả tối đa chừng này giây
THOIGIANTHUHOIKC = 300.
# Thu hồi thêm 2 món đáng tiền (người dùng dặn 2026-11-14): acc gà give trả cả chồng cùng đồ Lam Kim / Trảo; acc chính thu hồi xong
# bán hết ở Chủ Tiệm Y Dược (Chu Quốc cạnh Tả Khâu Minh, nơi ra Phong Yêu Kính; đang ở Tân Thủ Thôn thì tiệm ở đó) rồi mới báo xong.
# Quá THOIGIANBANTHUHOIKC giây chưa bán xong thì thôi, báo Telegram
# Tên đúng theo máy chủ (log quay số 845 "Bổ Tâm Đơn", 321/844 "Tạo Hoá Đơn"; người dùng gọi "Tạp Hóa Đơn"). "Bổ Tâm Đan" là món khác
# VATPHAMTHUHOIKCs: acc gà trả cả chồng về acc chính; VATPHAMTHUHOIBANKCs: phần acc chính đem bán. Bổ Tâm Đơn tạm thời giữ lại để
# dùng, không bán (người dùng dặn 2026-11-14): muốn bán lại thì thêm "Bổ Tâm Đơn" vào VATPHAMTHUHOIBANKCs
VATPHAMTHUHOIKCs = ("Tạo Hoá Đơn", "Tạo Hóa Đơn", "Bổ Tâm Đơn")
VATPHAMTHUHOIBANKCs = ("Tạo Hoá Đơn", "Tạo Hóa Đơn")
# Phù acc gà còn trong túi cũng trả về bán (người dùng dặn 2026-11-14). Bán hết mọi chồng, kể cả phù acc chính có sẵn trước đó, không
# giữ lại (người dùng dặn 2026-11-16)
PHUTHUHOIBANKCs = (PHIHANHPHU, HOITHANHPHU, HOIBANGPHU)
# Đồ Lam Kim cấp này (acc gà trả về sau kéo cấp): acc chính luôn chỉ giữ tối đa SOLAMKIMGIULAIKC món (rẻ nhất, để đốt Phong Yêu Kính),
# còn lại bán lúc thu hồi xong (người dùng dặn 2026-11-14). Chỉ xét món đem đốt được (_chondolamkim: không khoá, không ★)
CAPLAMKIMBANKC = 25
# Tăng 4 -> 8 món (người dùng dặn 2026-11-16)
SOLAMKIMGIULAIKC = 8
# Sách "Nhập Môn ..." (tên bắt đầu như vậy, game viết cả "Nhập Môn" lẫn "Nhập môn", vd Nhập Môn Tu Tâm, Nhập môn Khổ Luyện): acc gà trả
# về, acc chính bán đồ xong thì tới Quản Khố cất hết vào rương (người dùng dặn 2026-11-14; dùng bộ cất kho tactu_catkho_xq, rương tự
# động). Đang ở Chu Quốc cất ở Quản Khố Chu Quốc (X_KHO_CHU, Y_KHO_CHU), Tân Thủ Thôn ở Quản Khố, nơi khác thì về Chu Quốc
TIENTOSACHTHUHOIKCs = ("Nhập Môn",)
# Sách "Nhập Môn" acc chính giữ lại trong túi, không cất kho (người dùng dặn 2026-11-18). So theo tên đã cắt 31 byte như trong ô hành
# trang (cattenhanhtrang), vd "Nhập Môn Cơ Bản Thương Pháp" trong túi là "Nhập Môn Cơ Bản Thương"
SACHGIULAIKCs = ("Nhập Môn Thân Thủ Vô Ảnh", "Nhập Môn Kinh Lạc Học Thuyết", "Nhập Môn Cơ Bản Quyền Cước", "Nhập Môn Cơ Bản Đao Pháp",
                 "Nhập Môn Cơ Bản Kiếm Pháp", "Nhập Môn Cơ Bản Thương Pháp", "Nhập Môn Cơ Bản Bổng Pháp", "Nhập Môn Ám Khí Đầu Xạ",
                 "Nhập Môn Chiêu Giá Chi Thuật", "Nhập Môn Tụng Kinh", "Nhập Môn Thiền Định", "Nhập Môn Tu Tâm",
                 "Nhập Môn Đạo Gia Học Thuyết")
NPCBANTHUHOIKCs = {BANDO_CHUQUOC: ("Chủ Tiệm Y Dược", 250, 176), BANDO_TANTHUTHON: ("Chủ Tiệm Y Dược", 135, 170)}
KHOANGCACHBANTHUHOIKC = 3.
THOIGIANBANTHUHOIKC = 300.
# Gom đồ (người dùng dặn 2026-11-16): trước khi bắt đầu Phong Yêu Kính, mọi acc gà give hết đồ Lam Kim đang có về acc chính (acc chính
# đứng yên chờ, mỗi lần bắt đầu có mã "magomdo" riêng, acc gà give xong báo "dagomdo" = mã đó). Quá THOIGIANGOMDOKC giây thì vẫn vào
# Phong Yêu Kính. Sau đó acc chính chia dần cho acc đốt (người give): mỗi lượt tối đa SOMONCHIAMOILUOTKC món, acc đốt nhận (báo có đồ)
# rồi đốt hết thì lượt sau đưa tiếp; đưa từng ít một để chọn món theo cấp acc đốt lúc đó (lên cấp thì món cấp thấp không đốt được nữa)
THOIGIANGOMDOKC = 300.
SOMONCHIAMOILUOTKC = 5
# Acc phụ (cả acc chính 2 Kéo gà A-Z) cũng đưa đồ Lam Kim về acc chính (người dùng báo 2026-11-23: acc chính hết đồ là báo "không acc
# gà nào còn đồ" dừng luôn, trong khi acc chính 2 còn cả chục món nhặt ở Phong Yêu Kính). KHÔNG trả hết ngay ở gom đồ (người dùng dặn:
# acc phụ giữ rất nhiều đồ): chỉ ở Phong Yêu Kính, acc chính hết đồ, acc gà cũng hết mà acc phụ (ngoài phó bản) báo còn đồ ("colamkim")
# thì acc chính đứng yên, mã "magomdophu" + cấp đồ tối thiểu theo acc đốt ("capgomphu"); acc phụ tới cạnh give SOMONGOMPHUKC món rẻ /
# cấp thấp nhất đủ cấp (dùng chung _buocgomdoga). Quá THOIGIANGOMDOPHUKC giây thì thôi; GIANCACHGOMDOPHUKC giây mới gọi lại 1 lần
# Acc gà hết tiền (thu hồi lượt trước lột hết ngân lượng, người dùng báo 2026-11-23: không đi phù được): ngân lượng dưới NGUONGTIENGAKC
# thì acc chính (ngoài phó bản, trước thu hồi) tới cạnh "give <ID> 0#0 ... $TIENCHOGAKC", tối đa SOLANCHOTIENKC lần mỗi acc gà;
# give xong GIANCACHCHOTIENKC giây mới xét lại (chờ acc gà báo tiền mới)
NGUONGTIENGAKC = 1000
TIENCHOGAKC = 2000
SOLANCHOTIENKC = 3
GIANCACHCHOTIENKC = 8.
# Acc gà hết tiền, acc chính ở bản đồ khác: đứng yên chờ acc chính mang tiền tới tối đa chừng này giây rồi mới tự theo sau (_theosauchinhkc)
THOIGIANCHOTIENKC = 240.
THOIGIANGOMDOPHUKC = 180.
GIANCACHGOMDOPHUKC = 60.
SOMONGOMPHUKC = 10
# Acc gà tự thêm (không có trong danh sách bấm tay, tự báo idchinh là mình) mà không thấy online quá chừng này giây thì bỏ khỏi danh
# sách. 2026-11-16: Luyen Don (511) còn lưu "acc gà của 364" từ tối 15/11, cửa sổ nó mở thoáng qua lúc 10:57 tự bật lại -> 364 thêm vào
# rồi chờ "ID 511 chưa online" ở gom đồ (và sẽ kẹt "chờ acc gà out vào lại" lúc xong) dù 4 acc gà thật đủ cả
THOIGIANBOGATUTHEMKC = 180.
TENGIAIDOANKEOCAP = {"tanthu": "nhận thưởng tân thủ", "taphop": "tập hợp Tân Thủ Thôn", "gomdo": "gom đồ Lam Kim về acc chính",
                     "phongyeu": "Phong Yêu Kính", "xuatsu": "xuất sư",
                     "thuhoi": "thu hồi + bán đồ", "xong": "xong", "chosudo": "chờ acc chính 2 xuất sư", "tapkich": "Tập Kích"}
# Nhận đồ đệ (tuỳ chọn): trước khi lập nhóm / mời bang, acc chính lập nhóm riêng với acc gà đồ đệ, Mạnh Tử "2. Ta đem đệ tử đến làm lễ bái
# sư" -> "1. Xác nhận", acc gà "1. Xác nhận" (tallk 17e5# welcome.13); mọi acc gà tới cấp kết thúc thì về Mạnh Tử "3. ... lễ xuất sư" như vậy.
# Nhãn lựa chọn không có trong bộ nhớ (chỉ có lệnh), chưa dò được đuôi lệnh của acc chính nên chọn theo thứ tự (0 = lựa chọn 1)
NPCMANHTU = ("Mạnh Tử", 136, 143)
CHISOBAISU = 1
CHISOXUATSU = 2
KHOANGCACHDODEMANHTU = 5.
# Chọn xong chờ acc gà đồ đệ báo đã xác nhận tối đa chừng này giây rồi làm lại, tối đa SOLANSUPHUKC lần
THOIGIANCHODODEKC = 20.
SOLANSUPHUKC = 3


def _chuanhoa(ten):
    return unicodedata.normalize("NFC", ten or "").strip()


class TacTuKeoCap:
    # --- Bật / tắt, trạng thái cho giao diện ---------------------------------------------------------------------------------------
    def batdau_keocap(self, vaitro, idchinh = 0, idgas = (), dabang = False, xongtanthu = False, tuychoncu = None, muctieutheosaucu = None,
                      iddode = 0, dabaisu = False, daxuatsu = False, capketthuc = CAPKETTHUCKEOCAP, tendode = "", moibang = True,
                      gatuthem = (), chinh2 = False, dacode60 = False, **_):
        # moibang (acc chính, ô "Mời acc gà vào bang" trên giao diện): tắt khi acc chính không có bang / không muốn mời -> bỏ hẳn bước mời bang
        # iddode (acc chính): ID acc gà nhận làm đồ đệ (0 = không); dabaisu / daxuatsu: đã xong (mở lại bot giữa chừng)
        # iddode (acc phụ, Kéo gà A-Z có "Acc chính 2", người dùng dặn 2026-11-21): acc chính 2 cũng nhận 1 đồ đệ riêng (_suphuphukc)
        # tendode (acc chính): đồ đệ là acc gà máy khác (chưa biết ID lúc bấm): thấy acc gà tên này qua LAN thì lấy ID nó
        # capketthuc (acc chính, người dùng chọn trên giao diện): mọi acc gà tới cấp này thì xong; acc gà đọc theo acc chính
        # vaitro "chinh": điều phối, idgas là ID các acc gà (acc gà máy khác báo idchinh là mình thì tự thêm); "ga": idchinh là ID acc
        # chính (0 = tự tìm qua LAN); "phu": acc phụ (idchinh 0 = tự tìm qua LAN)
        if self._keocap or vaitro not in ("chinh", "ga", "phu"):
            return
        self._keocap = {"vaitro": vaitro, "idchinh": int(idchinh or 0), "idgas": [int(i) for i in idgas if int(i)], "batdau": time.time(),
                        "giaidoan": "taphop" if vaitro == "chinh" else ("taphop" if xongtanthu else "tanthu"), "trangthai": "bắt đầu",
                        "tanthu": "nhiemvu", "dabang": bool(dabang), "xongtanthu": bool(xongtanthu), "hoithoai": None, "lucmoi": {},
                        "lucmoibang": {}, "idgive": 0, "luctatgive": 0., "lucbatpy": 0., "codolamkim": None, "lucdocdo": 0., "dadescpy": {},
                        "dathuhoi": False, "trao": None, "giaotrao": {}}
        self._keocap.update(iddode = int(iddode or 0), dabaisu = bool(dabaisu), daxuatsu = bool(daxuatsu),
                            capketthuc = int(capketthuc or CAPKETTHUCKEOCAP), tendode = "" if iddode else _chuanhoa(tendode),
                            moibang = bool(moibang), chinh2 = bool(chinh2) and vaitro == "phu", dacode60 = bool(dacode60))
        # Acc gà tự thêm qua _laygaonline (lưu lại để mở lại bot vẫn biết, THOIGIANBOGATUTHEMKC)
        self._keocap["gatuthem"] = [int(i) for i in gatuthem if int(i) in self._keocap["idgas"]]
        # Mở lại bot giữa chừng: ô gốc của người dùng lưu từ lần trước (get_keocapluu)
        if tuychoncu:
            self._keocap["tuychoncu"] = dict(tuychoncu)
        if muctieutheosaucu:
            self._keocap["muctieutheosaucu"] = tuple(muctieutheosaucu)
        elif vaitro == "ga" and self._keocap["idchinh"] and self._idmuctieutheosau == self._keocap["idchinh"]:
            # Còn Theo sau acc chính sót từ lần kéo cấp trước (bản cũ không lưu ô gốc): coi như gốc là không theo sau ai
            self._keocap.setdefault("tuychoncu", {})["_is_tudongtheosau"] = False
            self._keocap["muctieutheosaucu"] = (0, "")
        if vaitro in ("chinh", "ga") and self._is_trongphongyeu():
            # Mở lại bot khi đang trong Phong Yêu Kính: vào thẳng giai đoạn Phong Yêu Kính. Không thì acc gà thấy acc chính "tập hợp", rời
            # nhóm sang nhóm acc chính -> bị đưa ra khỏi phó bản, lập tổ đội mới
            self._keocap.update(giaidoan = "phongyeu", xongtanthu = True, xonggomdo = True)
            self._logkc("Đang ở trong Phong Yêu Kính: làm tiếp Phong Yêu Kính")
        capdo = self.moitruong.get_capdonhanvat() or 0
        if vaitro == "ga" and not self._keocap["xongtanthu"] and capdo >= 8:
            # Bật giữa chừng: đã có cấp 8 = đã nhập code, bỏ nói chuyện Thần Tiên Gia Gia, chỉ dùng thưởng còn trong túi (nếu có)
            self._keocap["tanthu"] = "vatpham"
            self._logkc(f"Đã cấp {capdo}: bỏ bước trả nhiệm vụ / nhận x2 kinh nghiệm, chỉ dùng thưởng tân thủ còn trong túi")
        mota = {"chinh": "acc chính, acc gà " + (", ".join(map(str, self._keocap["idgas"])) or "chưa có (chờ acc gà máy khác qua LAN)")
                         + (f", đồ đệ tên {self._keocap['tendode']}" if self._keocap["tendode"] else "")
                         + ("" if self._keocap["moibang"] else ", không mời bang"),
                "ga": f"acc gà của {idchinh or 'acc chính tự tìm qua LAN'}",
                "phu": f"acc phụ (theo bãi + Phong Yêu Kính) của {idchinh or 'acc chính tự tìm qua LAN'}"
                       + (f", đồ đệ ID {self._keocap['iddode']}" if self._keocap["iddode"] else "")}[vaitro]
        self._logkc(f"Bắt đầu kéo cấp ({mota})")
        phatam({"chinh": "Bắt đầu kéo cấp acc gà", "ga": "Bắt đầu kéo cấp, vai acc gà", "phu": "Bắt đầu kéo cấp, vai acc phụ"}[vaitro])

    def datdode_keocap(self, iddode):
        # Kéo gà A-Z giao đồ đệ giữa lượt (lệnh "keocapdode:<ID>"): đầu lượt acc chính còn là sư phụ của acc gà ngoài lượt nên không nhận,
        # người dùng xuất sư tay xong thì nhận luôn, không chờ lượt sau (2026-11-21). Chỉ nhận khi đang kéo cấp vai chính / phụ, chưa có đồ đệ
        s = self._keocap
        iddode = int(iddode or 0)
        if not s or s.get("vaitro") not in ("chinh", "phu") or s.get("iddode") or not iddode:
            return
        s.update(iddode = iddode, dabaisu = False, daxuatsu = False)
        s.pop("suphu", None)
        self._logkc(f"Nhận đồ đệ giữa lượt: acc gà ID {iddode} (bái sư ở Mạnh Tử khi xong tân thủ)")

    def huy_keocap(self):
        if self._keocap:
            self._ketthuckeocap("Đã dừng (bấm tay)")

    def _ketthuckeocap(self, thongbao):
        s = self._keocap
        self._keocap = None
        for thuoctinh, giatri in (s.get("tuychoncu") or {}).items():
            setattr(self, thuoctinh, giatri)
        if "muctieutheosaucu" in s:
            self.thietlap_muctieutheosau(*s["muctieutheosaucu"])
        if self._langlyson and self._langlyson["phoban"] == "phongyeukinh":
            self.huy_langlyson()
        if self._tapkich and (s.get("dabattapkich") or s.get("vaitro") == "chinh"):
            # Acc chính: Tập Kích chỉ chạy trong kéo cấp, xong / dừng là tắt (kể cả Tập Kích khôi phục từ thiết lập khi mở lại bot, cờ
            # dabattapkich không lưu: 2026-11-23 19:41 xong kéo cấp mà Gạ vẫn đi Tập Kích một mình, lượt sau giằng nhau chạy loạn)
            self.huy_tapkich()
        self.moitruong._inlog(f"[KÉO CẤP] {thongbao}")
        self._ketquakeocap = f"{time.strftime('%H:%M')} Kéo cấp: {thongbao}"
        phatam("Kết thúc kéo cấp")

    def get_is_dangkeocap(self):
        return bool(self._keocap)

    def get_trangthaikeocap(self):
        s = self._keocap
        if not s:
            return self._ketquakeocap or ""
        vai = {"chinh": "acc chính", "ga": "acc gà", "phu": "acc phụ"}[s["vaitro"]]
        return f"Kéo cấp ({vai}, {self._tengiaidoan(s['giaidoan'])}): {s['trangthai']}"

    def get_keocapshare(self):
        # Báo qua shared_data cho cửa sổ khác cùng máy
        s = self._keocap
        if not s:
            return None
        return {"vaitro": s["vaitro"], "idchinh": s["idchinh"], "idgas": s["idgas"], "giaidoan": s["giaidoan"], "idgive": s["idgive"],
                "capdo": self.moitruong.get_capdonhanvat() or 0, "xongtanthu": s["xongtanthu"], "dabang": s["dabang"],
                "codolamkim": s["codolamkim"], "nhompy": s.get("nhompy") or [], "chuyendo": s.get("chuyendo") or 0,
                "chinhtoi": bool(s.get("chuyendo") and (s.get("luotdi") or {}).get("ai") == "chinh"),
                "iddode": s["iddode"], "dabaisu": s["dabaisu"], "daxuatsu": s["daxuatsu"], "capketthuc": s["capketthuc"],
                "suphudang": s.get("suphudang") or "", "chinh2": bool(s.get("chinh2")), "phuxuatsu": list(s.get("phuxuatsu") or ()), "dathuhoi": s["dathuhoi"], "trao": s.get("trao"), "magomdo": s.get("magomdo") or 0., "dagomdo": s.get("dagomdo") or 0.,
                "code60": s.get("code60") or "", "magomdophu": s.get("magomdophu") or 0., "capgomphu": s.get("capgomphu") or 0,
                "colamkim": s.get("colamkim"), "nganluong": self.moitruong.get_nganluong(),
                "lucmoi": {int(i): float(t) for i, t in (s.get("lucmoi") or {}).items()}}

    def get_keocapluu(self):
        # Lưu thiết lập: dis / mở lại bot thì tự bật tiếp đúng vai
        s = self._keocap
        if not s:
            return None
        # Lưu cả ô gốc của người dùng (tuychoncu / muctieutheosaucu): không lưu thì mở lại bot coi giá trị kéo cấp đang đặt (Theo sau acc
        # chính) là gốc, xong kéo cấp "trả lại" đúng Theo sau đó, acc mới vào cùng cửa sổ tự chạy theo acc chính (gacon7_3 2026-11-01)
        luu = {"vaitro": s["vaitro"], "idchinh": s["idchinh"], "idgas": s["idgas"], "dabang": s["dabang"], "xongtanthu": s["xongtanthu"],
               "tuychoncu": dict(s.get("tuychoncu") or {}), "iddode": s["iddode"], "dabaisu": s["dabaisu"], "daxuatsu": s["daxuatsu"],
               "capketthuc": s["capketthuc"], "tendode": s.get("tendode") or "", "moibang": s.get("moibang", True),
               "gatuthem": list(s.get("gatuthem") or []), "chinh2": bool(s.get("chinh2")), "dacode60": bool(s.get("dacode60"))}
        if "muctieutheosaucu" in s:
            luu["muctieutheosaucu"] = tuple(s["muctieutheosaucu"])
        return luu

    @staticmethod
    def _tengiaidoan(giaidoan):
        if isinstance(giaidoan, str) and giaidoan.startswith("bai:"):
            return f"bãi {laytenbando(int(giaidoan[4:]))}"
        return TENGIAIDOANKEOCAP.get(giaidoan, giaidoan)

    def _logkc(self, noidung):
        self.moitruong._inlog(f"[KÉO CẤP] {noidung}")

    def _sanggiaidoankc(self, s, giaidoan):
        if s["giaidoan"] == giaidoan:
            return
        if s["giaidoan"] == "tapkich" and s.get("dabattapkich"):
            # Rời Tập Kích (xuất sư / thu hồi / quay lại Phong Yêu Kính): tắt Tập Kích mình bật
            s["dabattapkich"] = False
            if self._tapkich:
                self.huy_tapkich()
        self._logkc(f"Sang giai đoạn: {self._tengiaidoan(giaidoan)} (trước: {self._tengiaidoan(s['giaidoan'])})")
        phatam(f"Kéo cấp: {self._tengiaidoan(giaidoan)}")
        s["giaidoan"] = giaidoan
        s["hoithoai"] = None

    def _datkc(self, s, thuoctinh, giatri, ten):
        # Đổi ô của người dùng cho kéo cấp, dừng thì trả lại
        if getattr(self, thuoctinh) != giatri:
            s.setdefault("tuychoncu", {}).setdefault(thuoctinh, getattr(self, thuoctinh))
            setattr(self, thuoctinh, giatri)
            self._logkc(f"{'Bật' if giatri else 'Tắt'} \"{ten}\" (dừng kéo cấp thì trả lại)")

    def _laycuasokeocap(self):
        # {ID người chơi: info} các cửa sổ khác đang kéo cấp, còn cập nhật
        ketqua = {}
        if self.shared_data is None:
            return ketqua
        try:
            danhsach = list(self.shared_data.items())
        except Exception:
            return ketqua
        for idcuaso, info in danhsach:
            if idcuaso == self.idcuaso or not isinstance(info, dict) or not isinstance(info.get("_keocap"), dict):
                continue
            if time.time() - info.get("thoidiemcapnhat", 0.) > 5. or not info.get("idnguoichoi"):
                continue
            ketqua[info["idnguoichoi"]] = info
        return ketqua

    # --- Vòng chính (gọi đầu action_tudongdichuyentudo) --------------------------------------------------------------------------------
    def _xulykeocap(self):
        # -> yêu cầu di chuyển / None (tự lo, đứng yên) hoặc False (để phần sau lo: lộ trình điểm đánh, Theo sau, Phong Yêu Kính)
        s = self._keocap
        if s["trangthai"] != s.get("trangthaidaghi"):
            s["trangthaidaghi"] = s["trangthai"]
            self._logkc(s["trangthai"])
        if s["vaitro"] == "chinh":
            return self._xulykeocapchinh(s)
        if s["vaitro"] == "phu":
            return self._xulykeocapphu(s)
        return self._xulykeocapga(s)

    def _is_dangban(self):
        moitruong = self.moitruong
        return moitruong.get_is_nhanvatdachet() or moitruong.get_is_dangvankhi() or self.get_is_danghoithoainpc() or self._trangthaiveban != 0 \
            or time.time() - moitruong.get_thoidiemthaydoibandogannhat() < 2.

    def _ditoikc(self, s, idbando, toado, nhan):
        # Tới (toado) ở bản đồ idbando: chưa tới bản đồ thì theo bước Đi tới bản đồ (Hồi Thành Phù / phù / chạy bộ). -> yêu cầu / None
        moitruong = self.moitruong
        if self._is_trongphongyeu():
            # Phong Yêu Kính mượn ID bản đồ thường nên Đi tới bản đồ tưởng chạy bộ ra được (12 cổng): ra bằng Thỏ Yêu về Chu Quốc
            return self._raphongyeukc(s)
        if moitruong.get_idbandohientai() != idbando:
            buoc = self._lapbuocditoibando(idbando, is_hoithanhphu = True, toadodich = toado, is_roiphoban = True)
            if buoc["loai"] in ("toinoi", "khongduong"):
                s["trangthai"] = f"{nhan}: {buoc['mota']}"
                return None
            s["trangthai"] = f"{nhan}: {buoc['mota']}"
            return self._thuchienbuocditoibando(buoc, idbando, toado, f"[KÉO CẤP] {nhan}")
        if toado and moitruong.get_khoangcachdiem(*toado) > 3.:
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (toado[0], toado[1], idbando), "khoangcachtoida": 1.}
        return None

    # --- Acc chính ----------------------------------------------------------------------------------------------------------------------
    def _laygaonline(self, s):
        # {ID acc gà: info _keocap} của acc gà trong danh sách đang chạy kéo cấp (cùng máy / máy khác nối LAN). Acc gà bật "Làm acc gà"
        # (máy khác, tự tìm acc chính) báo idchinh là mình thì thêm vào danh sách
        cuasos = self._laycuasokeocap()
        idtoi = self.moitruong.get_idnguoichoi()
        tuthem = s.setdefault("gatuthem", [])
        for i, info in sorted(cuasos.items()):
            if idtoi and i not in s["idgas"] and info["_keocap"].get("vaitro") == "ga" and info["_keocap"].get("idchinh") == idtoi:
                s["idgas"].append(i)
                tuthem.append(i)
                self._logkc(f"Thêm acc gà {info.get('tennhanvat') or ''} (ID {i}" + (f", máy {info['_tenmay']}" if info.get("_tenmay") else "") + ")")
        gas = {i: cuasos[i] for i in s["idgas"] if i in cuasos and cuasos[i]["_keocap"].get("vaitro") == "ga"}
        # Acc gà tự thêm mất tín hiệu quá THOIGIANBOGATUTHEMKC giây: bỏ khỏi danh sách (online lại vẫn tự thêm lại). Acc gà trong danh sách
        # bấm tay thì giữ như cũ (dis vào lại được chờ)
        now = time.time()
        lucthay = s.setdefault("lucthaygatuthem", {})
        for i in list(tuthem):
            if i in gas:
                lucthay[i] = now
            elif now - lucthay.setdefault(i, now) > THOIGIANBOGATUTHEMKC:
                tuthem.remove(i)
                lucthay.pop(i, None)
                if i in s["idgas"]:
                    s["idgas"].remove(i)
                ten = (s.get("tengas") or {}).get(i) or ""
                self._logkc(f"Bỏ acc gà tự thêm {ten} (ID {i}): quá {int(THOIGIANBOGATUTHEMKC)}s không online")
        return gas

    def _layphukc(self, s):
        # {ID acc phụ: info} các acc phụ online nhận mình làm acc chính
        idtoi = self.moitruong.get_idnguoichoi()
        phus = {i: info for i, info in self._laycuasokeocap().items()
                if info["_keocap"].get("vaitro") == "phu" and info["_keocap"].get("idchinh") == idtoi}
        if sorted(phus) != s.get("phus"):
            self._logkc(f"Acc phụ: {', '.join(map(str, sorted(phus))) or 'không có'}")
            s["phus"] = sorted(phus)
        return phus

    def _nhomkeocapkc(self, s, gas):
        # Người acc chính mời vào nhóm ở tập hợp / bãi: acc gà trước, acc phụ lấp chỗ còn lại (nhóm tối đa SOLUONGTHANHVIENNHOMTOIDA)
        phus = self._layphukc(s)
        conlai = max(0, SOLUONGTHANHVIENNHOMTOIDA - 1 - len(gas))
        return {**gas, **{i: phus[i] for i in sorted(phus)[:conlai]}}

    def _phusudokc(self, s, gas, caps, capthap):
        # Acc chính 2 (acc phụ của mình có iddode, Kéo gà A-Z): -> ([(tên acc phụ, ID đồ đệ)] đang cần bái sư, [...] được phép xuất sư).
        # Bái sư: đồ đệ online, chưa quá CAPTOIDANHANDODE (quá thì acc phụ tự coi như đã bái sư). Xuất sư: đồ đệ tới CAPXUATSU hoặc mọi acc
        # gà tới cấp kết thúc (như đồ đệ của mình)
        baisus, xuatsus = [], []
        for idphu, info in sorted(self._layphukc(s).items()):
            kc = info["_keocap"]
            iddd = int(kc.get("iddode") or 0)
            if not iddd or iddd not in gas or iddd == s["iddode"]:
                continue
            ten = info.get("tennhanvat") or str(idphu)
            if not kc.get("dabaisu"):
                # Acc phụ bắt đầu bái sư ngay khi đồ đệ xong tân thủ (_suphuphukc): từ lúc đó mình chờ
                if caps.get(iddd, 0) <= CAPTOIDANHANDODE and (gas[iddd]["_keocap"].get("xongtanthu") or kc.get("suphudang") == "baisu"):
                    baisus.append((ten, iddd))
            elif not kc.get("daxuatsu") and (capthap >= s["capketthuc"] or caps.get(iddd, 0) >= CAPXUATSU):
                xuatsus.append((ten, iddd))
        return baisus, xuatsus

    def _xulykeocapchinh(self, s):
        moitruong = self.moitruong
        now = time.time()
        # Acc chính tự đi bãi / lộ trình điểm đánh: bật "Theo sau" thì bot bỏ lộ trình, đứng im (187 lưu sẵn Theo sau, 2026-11-01)
        if self._is_tudongtheosau:
            self._datkc(s, "_is_tudongtheosau", False, "Theo sau")
        gas = self._laygaonline(s)
        if self._tapkich:
            if s["giaidoan"] == "tapkich" or moitruong.get_is_bandotapkichmonphai():
                s["dabattapkich"] = True
            else:
                self._logkc(f"Tập Kích đang chạy ngoài giai đoạn Tập Kích (đang {self._tengiaidoan(s['giaidoan'])}): tắt")
                self.huy_tapkich()
        # Tên acc gà từng thấy: lúc xong acc gà đã tự dừng / đóng client vẫn biết tên để xét tiền tố trục xuất khỏi bang
        s.setdefault("tengas", {}).update({i: info["tennhanvat"] for i, info in gas.items() if info.get("tennhanvat")})
        if s["giaidoan"] == "xong" and now - s.get("lucxong", now) > THOIGIANBAOXONGKC:
            # Acc gà đọc "xong" là tự dừng ngay (thường trước acc chính): không chờ chúng nữa, kẻo kẹt "chờ cửa sổ acc gà" mãi
            if not self._trucxuatgakc(s):
                return None
            self._kiemtratraothuhoikc(s)
            self._ketthuckeocap(f"✅ Mọi acc gà đã tới cấp {s['capketthuc']}")
            return None
        if s["giaidoan"] == "thuhoi":
            return self._buocthuhoichinh(s, gas)
        if s.get("tendode"):
            # Đồ đệ là acc gà máy khác: thấy acc gà tên đó thì lấy ID; chưa thấy thì chờ (bái sư phải làm trước khi lập nhóm cả đám)
            iddode = next((i for i, info in gas.items() if _chuanhoa(info.get("tennhanvat")) == s["tendode"]), 0)
            if not iddode:
                s["trangthai"] = f"chờ acc gà đồ đệ \"{s['tendode']}\" bật kéo cấp (máy khác: bấm \"Làm acc gà\" ở máy đó)"
                return None
            self._logkc(f"Đồ đệ: {s['tendode']} (ID {iddode})")
            s.update(iddode = iddode, tendode = "")
        if not gas:
            s["trangthai"] = "chờ cửa sổ acc gà bật kéo cấp (cùng máy / máy khác bấm \"Làm acc gà\")"
            return None
        if s["giaidoan"] not in ("thuhoi", "xong"):
            # Acc gà hết ngân lượng (lượt trước thu hồi lột hết): đưa TIENCHOGAKC cho nó đi phù được
            yeucau = self._chotiengakc(s, gas)
            if yeucau is not False:
                return yeucau
        caps ={i: info["_keocap"].get("capdo") or 0 for i, info in gas.items()}
        capthap = min(caps.values())
        # Acc chính 2 (acc phụ có đồ đệ): ai đang chờ bái sư / được phép xuất sư (báo qua get_keocapshare "phuxuatsu", acc phụ đọc)
        phubaisu, phuxuatsu = self._phusudokc(s, gas, caps, capthap)
        s["phuxuatsu"] = [iddd for _, iddd in phuxuatsu]
        # Acc gà từng báo có Cửu Long Thần Hỏa Trảo (đeo / trong túi): lúc thu hồi xong đếm lại xem đủ chưa (_kiemtratraothuhoikc)
        cotrao = s.setdefault("gacotrao", [])
        cotrao.extend(i for i, info in gas.items() if info["_keocap"].get("trao") in ("deo", "tui") and i not in cotrao)
        capketthuc = s["capketthuc"]
        # Cấp đọc được lần cuối của mọi acc gà trong danh sách: acc gà out (dis / mất mạng) không còn trong gas, chỉ xét gas thì acc gà
        # còn lại đã tới cấp kết thúc là tưởng xong (QuanSuMuMuu 26 out, còn DaiTuongQuan 39 -> báo xong, 2026-11-03)
        capcuoi = s.setdefault("capcuoi", {})
        capcuoi.update(caps)
        if moitruong.get_is_bandotapkichmonphai() and s["giaidoan"] != "xong":
            # Đang trong phó bản Tập Kích: đánh hết vòng (giết boss hệ thống tự đưa ra) rồi mới xuất sư / thu hồi / nhập code 60 (người
            # dùng dặn 2026-11-23). Trước đây đủ cấp là tắt Tập Kích ngay, mình kẹt trong phó bản (mượn ID Kênh Trịnh Quốc 1), acc gà ở
            # Kênh Trịnh Quốc thật đi tới toạ độ của mình mãi không gặp để trả đồ
            if s["giaidoan"] != "tapkich":
                self._sanggiaidoankc(s, "tapkich")
                s.pop("lucthuhoi", None)
            if not self._tapkich:
                self.batdau_tapkich()
                s["dabattapkich"] = bool(self._tapkich)
            self._batgomquaitapkichkc()
            s["trangthai"] = (f"mọi acc gà đã tới cấp {capketthuc}: đánh nốt vòng Tập Kích rồi mới ra thu hồi" if capthap >= capketthuc
                              else self.get_trangthaitapkich())
            return False
        offlines = [i for i in s["idgas"] if i not in gas and capcuoi.get(i, 0) < capketthuc]
        if capthap >= capketthuc and offlines and s["giaidoan"] not in ("thuhoi", "xong"):
            s["trangthai"] = "chờ acc gà out vào lại (" + ", ".join(f"ID {i} cấp {capcuoi[i]}" if i in capcuoi else f"ID {i}"
                                                                for i in offlines) + f" chưa tới cấp {capketthuc})"
            # Ngoài phó bản mà Phong Yêu Kính còn dở bước ra / đổi nhóm (vừa bị đưa ra Chu Quốc) thì cho chạy nốt tới "vao": bỏ ngang thì
            # bị mời vào vòng sau là làm tiếp bước ra (rời nhóm ngay) và báo boss vòng cũ cho cả nhóm (2026-11-07)
            pyk = self._langlyson
            if self._is_trongphongyeu() or (pyk and pyk["phoban"] == "phongyeukinh" and pyk["giaidoan"] in ("nhanthuong", "doinhom")):
                return self._buocphongyeuchinh(s, gas)
            return None
        if capthap >= capketthuc and self._is_trongphongyeu():
            # Mọi acc gà đã tới cấp kết thúc mà còn trong Phong Yêu Kính: ra ngay (giải tán nhóm => cả nhóm bị đưa ra Chu Quốc, không được
            # thì nói chuyện Thỏ Yêu), không đánh nốt vòng vô ích (người dùng dặn 2026-11-21). Ra rồi lượt sau mới xuất sư / thu hồi đồ
            if not s.get("dalograpydu"):
                s["dalograpydu"] = True
                self._logkc(f"Mọi acc gà đã tới cấp {capketthuc}: ra khỏi Phong Yêu Kính ngay, không đánh nốt vòng")
            yeucau = self._raphongyeukc(s)
            s["trangthai"] = f"mọi acc gà đã tới cấp {capketthuc}: ra khỏi Phong Yêu Kính"
            return yeucau
        if s["giaidoan"] == "phongyeu" and self._is_trongphongyeu():
            # Đang giữa vòng Phong Yêu Kính: không bỏ ngang đi xuất sư / thu hồi đồ (từng tắt Phong Yêu Kính chạy bộ 12 cổng về Tân Thủ Thôn),
            # đánh hết vòng, ra Chu Quốc rồi mới xét (lúc đó Hồi Thành Phù được)
            return self._buocphongyeuchinh(s, gas)
        self._dodethatkc(s, gas)
        if (capthap >= capketthuc or caps.get(s["iddode"], 0) >= CAPXUATSU or s["giaidoan"] in ("xuatsu", "xong")) \
                and s["iddode"] and s["dabaisu"] and not s["daxuatsu"]:
            # Đồ đệ tới cấp xuất sư (hoặc mọi acc gà tới cấp kết thúc): dắt đồ đệ về Mạnh Tử xuất sư, xong mới kéo tiếp / báo xong
            self._sanggiaidoankc(s, "xuatsu")
            return self._buocsuphuchinh(s, gas, "xuatsu")
        if phuxuatsu:
            # Acc chính 2 (acc phụ có đồ đệ) đi xuất sư: đứng chờ (acc gà khác vẫn theo mình), không mời nhóm / sang thu hồi, kẻo kéo đồ đệ
            # của nó vào nhóm mình hoặc báo xong trước khi nó xuất sư. Giai đoạn riêng "chosudo", không dùng "xuatsu": "xuatsu" làm mình
            # dắt đồ đệ của mình đi xuất sư luôn dù nó chưa cấp 50 (xuất sư không được)
            self._sanggiaidoankc(s, "chosudo")
            if self._langlyson:
                self.huy_langlyson()
            s["trangthai"] = "xuất sư: chờ acc chính 2 xuất sư (" + ", ".join(
                f"{ten} với {gas[iddd].get('tennhanvat') or iddd}" for ten, iddd in phuxuatsu) + ")"
            return None
        if capthap >= capketthuc and s["giaidoan"] != "xong":
            # Trước khi xong: acc gà trả hết đồ Lam Kim về mình (người dùng dặn)
            self._sanggiaidoankc(s, "thuhoi")
            return self._buocthuhoichinh(s, gas)
        if s["giaidoan"] == "xong":
            # Báo "xong" thêm THOIGIANBAOXONGKC giây cho acc gà kịp đọc rồi tự dừng (Phong Yêu Kính của chúng)
            self._sanggiaidoankc(s, "xong")
            if self._langlyson:
                self.huy_langlyson()
            s.setdefault("lucxong", now)
            s["trangthai"] = f"mọi acc gà đã tới cấp {capketthuc}, báo acc gà dừng"
            if now - s["lucxong"] > THOIGIANBAOXONGKC and self._trucxuatgakc(s):
                self._kiemtratraothuhoikc(s)
                self._ketthuckeocap(f"✅ Mọi acc gà đã tới cấp {capketthuc}")
            return None
        if s["iddode"] and not s["dabaisu"] and caps.get(s["iddode"], 0) > CAPTOIDANHANDODE:
            # Acc gà đồ đệ đã quá cấp nhận đồ đệ (người dùng dặn): coi như đã bái sư, bỏ bước bái sư, vẫn nhớ đồ đệ để tới cấp kết thúc xuất sư
            self._logkc(f"Acc gà đồ đệ (ID {s['iddode']}) đã cấp {caps[s['iddode']]} > {CAPTOIDANHANDODE}: bỏ bái sư, cấp "
                        f"{capketthuc} vẫn dắt đi xuất sư")
            s["dabaisu"] = True
        if s["iddode"] and not s["dabaisu"] and all(info["_keocap"].get("xongtanthu") for info in gas.values()):
            # Nhận đồ đệ: bái sư trước khi lập nhóm cả đám / mời bang / đi bãi
            return self._buocsuphuchinh(s, gas, "baisu")
        if phubaisu:
            # Acc chính 2 đang bái sư (nhóm riêng 2 người với đồ đệ của nó): chờ xong mới lập nhóm cả đám, không thì mời đồ đệ nó vào
            # nhóm mình giữa lúc bái sư
            if self._langlyson:
                self.huy_langlyson()
            s["trangthai"] = "chờ acc chính 2 bái sư (" + ", ".join(
                f"{ten} với {gas[iddd].get('tennhanvat') or iddd}" for ten, iddd in phubaisu) + ")"
            return None
        if s["giaidoan"] == "taphop" and capthap >= BAIKEOCAPs[0][1] and all(info["_keocap"].get("xongtanthu") for info in gas.values()):
            # Bật giữa chừng (acc gà đã qua bãi đầu): không về Tân Thủ Thôn tập hợp, đi thẳng bãi theo cấp; mời nhóm / bang ở bãi
            self._logkc(f"Acc gà thấp nhất đã cấp {capthap}: bỏ tập hợp, đi thẳng bãi theo cấp")
            s["giaidoan"] = ""
        if s["giaidoan"] == "taphop":
            return self._buoctaphopchinh(s, gas)
        if capthap >= BAIKEOCAPs[-1][1]:
            if not self._is_trongphongyeu():
                # Acc gà cũ (cấp >= 35, bị trục xuất khỏi bang sau lượt trước) bỏ tập hợp / bãi nên chưa được mời bang: mời lại ở đây,
                # không thì lên cấp không cộng điểm kỹ năng bang (2026-11-23)
                self._moibangkc(s, gas, SOLANMOIBANGGIUACHUNG, "solanmoibangbai")
            if self._buoctapkichchinh(s, gas, capthap) == "tapkich":
                return False
            if not s.get("xonggomdo"):
                # Trước Phong Yêu Kính: mọi acc gà give hết đồ Lam Kim về mình, sau đó mình chia dần cho acc đốt (người dùng dặn)
                self._sanggiaidoankc(s, "gomdo")
                return self._buocgomdochinh(s, gas)
            self._sanggiaidoankc(s, "phongyeu")
            return self._buocphongyeuchinh(s, gas)
        idbai = next(b for b, cap in BAIKEOCAPs if capthap < cap)
        self._sanggiaidoankc(s, f"bai:{idbai}")
        if self._langlyson:
            self.huy_langlyson()
        if self._is_dangban():
            return None
        nhom = self._nhomkeocapkc(s, gas)
        self._moinhomkc(s, nhom)
        self._moibangkc(s, gas, SOLANMOIBANGGIUACHUNG, "solanmoibangbai")
        yeucautrao = self._chuyentraokc(s, gas)
        if yeucautrao is not False:
            return yeucautrao
        tenbai = laytenbando(idbai)
        captoi = dict(BAIKEOCAPs)[idbai]
        if moitruong.get_idbandohientai() != idbai:
            s.pop("lotrinhbando", None)
            s.pop("luctoibai", None)
            return self._ditoikc(s, idbai, None, f"tới {tenbai} (acc gà thấp nhất cấp {capthap}, cần {captoi})")
        s.setdefault("luctoibai", now)
        chuatoi = [info.get("tennhanvat") or str(i) for i, info in nhom.items() if info.get("tenbando") != idbai]
        if chuatoi and now - s["luctoibai"] < THOIGIANCHOGATOIBAI:
            s["trangthai"] = f"{tenbai}: chờ acc gà theo sang ({', '.join(chuatoi)}, còn {int(THOIGIANCHOGATOIBAI - (now - s['luctoibai']))}s)"
            return None
        if s.get("lotrinhbando") != idbai:
            s["lotrinhbando"] = idbai
            # Không nạp lộ trình mẫu: bỏ điểm đánh đang có để lộ trình rỗng, bot tự dò bãi bằng điểm dò riêng (_dobandokhonglotrinh)
            if self._diemdanhxungquanhs:
                self.botoanbo_diemdanhxungquanh()
            self._logkc(f"{tenbai}: dò bãi bằng điểm dò riêng, không dùng lộ trình mẫu")
            self._datkc(s, "_is_tudongdichuyendiemdanhxungquanh", True, "Tự động di chuyển điểm đánh xung quanh")
        s["trangthai"] = f"{tenbai}: đánh quái kéo acc gà tới cấp {captoi} (" + ", ".join(
            f"{gas[i].get('tennhanvat') or i} {c}" for i, c in sorted(caps.items(), key = lambda x: x[1])) + ")"
        return False

    def _buocgomdochinh(self, s, gas):
        # Đứng yên chờ mọi acc gà tới cạnh give hết đồ Lam Kim (acc gà báo dagomdo = magomdo). Xong / quá THOIGIANGOMDOKC giây thì sang
        # Phong Yêu Kính, từ đó đồ Lam Kim chỉ do mình chia cho acc đốt (_chuyendolamkimkc)
        now = time.time()
        if not s.get("magomdo"):
            s["magomdo"] = round(now, 3)
            s.update(idgive = 0, chuyendo = 0)
            s.pop("bogive", None)
            self._logkc("Trước Phong Yêu Kính: chờ mọi acc gà give hết đồ Lam Kim về mình")
        if self._is_tudongtheosau:
            self._datkc(s, "_is_tudongtheosau", False, "Theo sau")
        if self._is_trongphongyeu():
            return self._raphongyeukc(s)
        if self._langlyson:
            self.huy_langlyson()
        chuaxongs = [info.get("tennhanvat") or str(i) for i, info in gas.items() if info["_keocap"].get("dagomdo") != s["magomdo"]]
        chuaxongs += [f"ID {i} chưa online" for i in s["idgas"] if i not in gas]
        if chuaxongs and now - s["magomdo"] <= THOIGIANGOMDOKC:
            s["trangthai"] = f"gom đồ Lam Kim: đứng yên chờ acc gà tới give ({', '.join(chuaxongs)}, còn " \
                             f"{int(THOIGIANGOMDOKC - (now - s['magomdo']))}s)"
            return None
        if chuaxongs:
            noidung = f"Quá {int(THOIGIANGOMDOKC)}s chưa gom xong đồ Lam Kim ({', '.join(chuaxongs)}): vẫn vào Phong Yêu Kính"
            self._logkc("⚠️ " + noidung)
            baosuco(self.moitruong, "vatpham", f"Kéo cấp: {noidung}", khoa = "gomdokc", giancach = 0.)
        else:
            self._logkc("Mọi acc gà đã give hết đồ Lam Kim về mình: vào Phong Yêu Kính, chia dần cho acc đốt")
        s["xonggomdo"] = True
        # Đọc lại túi mình ngay (vừa nhận thêm đồ)
        s["dolamkimchinh"] = "doc"
        self._sanggiaidoankc(s, "phongyeu")
        return self._buocphongyeuchinh(s, gas)

    def _buocthuhoichinh(self, s, gas):
        # Mọi acc gà đã tới cấp kết thúc: ra khỏi Phong Yêu Kính (nếu đang trong) rồi đứng yên chờ acc gà tới cạnh give trả hết đồ Lam Kim.
        # Mọi acc gà báo đã trả (hoặc quá THOIGIANTHUHOIKC giây) thì sang "xong"
        now = time.time()
        if "lucthuhoi" not in s:
            s["lucthuhoi"] = now
            # Số Trảo trong túi mình lúc bắt đầu thu hồi và acc gà đang giữ Trảo: thu hồi xong đếm lại (_kiemtratraothuhoikc)
            s["sotraodauthuhoi"] = self._demtraokc()
            s["gacotraothuhoi"] = list(s.get("gacotrao") or [])
        if self._is_trongphongyeu():
            return self._raphongyeukc(s)
        if self._langlyson:
            self.huy_langlyson()
        if self._is_dangban():
            return None
        if not s.get("daxetthuhoi") and (self.moitruong.get_idbandohientai() != BANDO_TANTHUTHON
                                         or self.moitruong.get_khoangcachdiem(*DIEMTAPHOPKEOCAP) > KHOANGCACHTAPHOPTHUHOIKC):
            # Về Tân Thủ Thôn chờ acc gà trả đồ (người dùng báo 2026-11-23: xong Tập Kích ở Thục Sơn đứng chờ tại đó, acc gà nhập code ở Tân
            # Thủ Thôn phải chạy sang tận bản đồ Tập Kích). Acc gà nhập code / lượt sau cũng ở Tân Thủ Thôn, bán đồ có tiệm ở đó
            return self._ditoikc(s, BANDO_TANTHUTHON, DIEMTAPHOPKEOCAP, "thu hồi: về Tân Thủ Thôn chờ acc gà trả đồ")
        chuaxongs = [info.get("tennhanvat") or str(i) for i, info in gas.items() if not info["_keocap"].get("dathuhoi")]
        chuaxongs += [f"ID {i} chưa online" for i in s["idgas"] if i not in gas]
        # Acc gà đang nhập code cấp 60 / dùng Chén Bạc (_buoccode60kc) trước khi trả: chờ thêm THOIGIANCODE60KC giây
        dangcode60 = [info.get("tennhanvat") or str(i) for i, info in gas.items() if info["_keocap"].get("code60") in ("code", "cho", "dung")]
        if dangcode60 and not s.get("cocode60"):
            s["cocode60"] = True
            self._logkc(f"Acc gà dùng code cấp 60 + Chén Bạc trước khi trả ({', '.join(dangcode60)}): chờ thu hồi thêm {int(THOIGIANCODE60KC)}s")
        hanthuhoi = THOIGIANTHUHOIKC + (THOIGIANCODE60KC if s.get("cocode60") else 0.)
        if chuaxongs and now - s["lucthuhoi"] <= hanthuhoi:
            s["trangthai"] = f"thu hồi đồ Lam Kim + Trảo: đứng yên chờ acc gà tới trả ({', '.join(chuaxongs)}" + \
                             (f"; đang code 60 / Chén Bạc: {', '.join(dangcode60)}" if dangcode60 else "") + \
                             f", còn {int(hanthuhoi - (now - s['lucthuhoi']))}s)"
            return None
        if not s.get("daxetthuhoi"):
            s["daxetthuhoi"] = True
            if chuaxongs:
                noidung = f"Quá {int(hanthuhoi)}s chưa thu hồi xong đồ Lam Kim / Trảo ({', '.join(chuaxongs)}): vẫn kết thúc, lấy tay giúp"
                self._logkc("⚠️ " + noidung)
                baosuco(self.moitruong, "vatpham", f"Kéo cấp: {noidung}", khoa = "thuhoikc", giancach = 0.)
            else:
                self._logkc("Mọi acc gà đã trả hết đồ Lam Kim")
        # Bán Tạo Hoá Đơn / Bổ Tâm Đơn vừa thu về (acc gà vẫn ở "thu hồi", đã báo trả xong nên đứng chờ)
        yeucau = self._banthuhoikc(s)
        if yeucau is not False:
            return yeucau
        yeucau = self._catsachthuhoikc(s)
        if yeucau is not False:
            return yeucau
        self._sanggiaidoankc(s, "xong")
        s["lucxong"] = now
        s["trangthai"] = f"mọi acc gà đã tới cấp {s['capketthuc']}, báo acc gà dừng"
        return None

    def _banthuhoikc(self, s):
        # Thu hồi xong: bán mọi chồng Tạo Hoá Đơn / Bổ Tâm Đơn trong túi ở Chủ Tiệm Y Dược (lệnh "sell" như bán rác Phong Yêu Kính, xếp
        # vào hàng đợi bán rác: 1 lệnh/giây, tự bán lại món máy chủ bỏ sót). -> yêu cầu di chuyển / None khi đang làm, False khi xong
        moitruong = self.moitruong
        now = time.time()
        b = s.setdefault("banthuhoi", {"luc": now, "somon": None, "xong": False})
        if b["xong"]:
            return False

        def xong(thongbao):
            b["xong"] = True
            self._logkc(thongbao)
            return False

        if b["somon"] is not None:
            if self.get_is_dangbanrac() or now < self._thoidiemguibanractieptheo:
                s["trangthai"] = f"bán đồ thu hồi: còn {self.get_somonchobanrac()}/{b['somon']} món"
                return None
            conlai = set(self._idtrongtuikc()) & set(b["ids"])
            return xong(f"Đã bán {b['somon']} món đồ thu hồi" + (f" (⚠️ còn {len(conlai)} món chưa bán được)" if conlai else ""))
        if now - b["luc"] > THOIGIANBANTHUHOIKC:
            noidung = f"Quá {int(THOIGIANBANTHUHOIKC)}s chưa bán được đồ thu hồi (Đơn / phù / Lam Kim cấp {CAPLAMKIMBANKC}): vẫn kết thúc, bán tay giúp"
            baosuco(moitruong, "vatpham", f"Kéo cấp: {noidung}", khoa = "banthuhoikc", giancach = 0.)
            return xong("⚠️ " + noidung)
        mons = self._laydsbanthuhoikc(s)
        if mons == "doc":
            s["trangthai"] = f"bán đồ thu hồi: đọc mô tả túi tìm đồ Lam Kim cấp {CAPLAMKIMBANKC}"
            return None
        if not mons:
            return xong(f"Không có đồ thu hồi để bán (Đơn / phù nhận thêm / Lam Kim cấp {CAPLAMKIMBANKC} quá {SOLAMKIMGIULAIKC} món)")
        idbando = moitruong.get_idbandohientai()
        idbandoban = idbando if idbando in NPCBANTHUHOIKCs else BANDO_CHUQUOC
        tennpc, x, y = NPCBANTHUHOIKCs[idbandoban]
        nhan = f"bán {len(mons)} món đồ thu hồi: tới {tennpc} ({x}, {y})"
        if idbando != idbandoban:
            s["trangthai"] = nhan
            return self._ditoikc(s, idbandoban, (x, y), nhan)
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = tennpc)
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHBANTHUHOIKC:
            s["trangthai"] = nhan
            xdich, ydich = moitruong.get_toado(diachinpc) if diachinpc else (x, y)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(xdich), round(ydich), idbando), "khoangcachtoida": 1.}
        idnpc = moitruong.get_iddoituong(diachinpc)
        if not idnpc or idnpc <= 0:
            return None
        moitruong.action_ngatdichuyen()
        lenhs = [self._lenhbanvatpham(idnpc, idmon, soluong) for idmon, _, soluong in mons]
        b.update(somon = len(lenhs), ids = [idmon for idmon, _, _ in mons])
        self._datnhangdoibanrac(lenhs)
        self._logkc(f"Bán {len(lenhs)} món đồ thu hồi ở {tennpc}: " + ", ".join(mota for _, mota, _ in mons))
        s["trangthai"] = f"bán {len(lenhs)} món đồ thu hồi ở {tennpc}"
        return None

    def _catsachthuhoikc(self, s):
        # Bán xong: cất mọi sách "Nhập Môn" trong túi vào kho (bộ cất kho _buoccatkho, lọc theo tiền tố tên). -> yêu cầu / None khi đang
        # làm, False khi xong
        moitruong = self.moitruong
        if s.get("dacatsach"):
            return False
        viec = s.get("catsach")
        if not viec:
            if not self._laymoncatkho(TIENTOSACHTHUHOIKCs, tenboquas = SACHGIULAIKCs):
                s["dacatsach"] = True
                self._logkc("Không có sách Nhập Môn để cất kho")
                return False
            viec = s["catsach"] = self._taoviec(LYDOCATKHO_KEOCAP)
            viec["tientos"] = TIENTOSACHTHUHOIKCs
            viec["tenboquas"] = SACHGIULAIKCs
            self._logkc("Cất sách Nhập Môn vào kho")
        idbando = moitruong.get_idbandohientai()
        if idbando not in (BANDO_CHUQUOC, BANDO_TANTHUTHON):
            s["trangthai"] = "cất sách Nhập Môn: về Chu Quốc"
            return self._ditoikc(s, BANDO_CHUQUOC, (X_KHO_CHU, Y_KHO_CHU), s["trangthai"])
        ketqua = self._buoccatkho(viec)
        s["trangthai"] = f"cất sách Nhập Môn: {viec['trangthai']}"
        if isinstance(ketqua, tuple):
            _, x, y = ketqua
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}
        if ketqua == "dang":
            return None
        # "xong" / "lỗi": _ketthuccatkho đã ghi log, có món không cất được / lỗi thì đã báo Telegram
        s["dacatsach"] = True
        s.pop("catsach", None)
        self._logkc("Cất sách Nhập Môn xong" if ketqua == "xong" else f"⚠️ Cất sách Nhập Môn lỗi: {self._ketquacatkho}")
        return False

    def _laydsbanthuhoikc(self, s):
        # Đồ thu hồi đem bán: [(id, mô tả, số lượng)], "doc" khi còn ô chưa đọc được mô tả (cần để nhận đồ Lam Kim)
        #   - mọi chồng VATPHAMTHUHOIBANKCs (Tạo Hoá Đơn; Bổ Tâm Đơn tạm giữ lại dùng)
        #   - mọi chồng phù (PHUTHUHOIBANKCs), kể cả phù acc chính có sẵn
        #   - đồ Lam Kim cấp CAPLAMKIMBANKC quá SOLAMKIMGIULAIKC món: giữ món rẻ nhất, bán món giá cao
        moitruong = self.moitruong
        lamkims = self._chondolamkim(s, captoithieu = CAPLAMKIMBANKC, is_tatca = True)
        if lamkims == "doc":
            return "doc"
        ketquas = []
        for vitri, idmon in self._timcacvatphamkc(VATPHAMTHUHOIBANKCs):
            soluong = self._soluongbanvatpham(vitri)
            ketquas.append((idmon, f"{moitruong.get_tenvatphamhanhtrang(vitri) or 'Đơn'} x{soluong}", soluong))
        for ten in PHUTHUHOIBANKCs:
            for vitri, idmon in self._timcacvatphamkc((ten,)):
                soluong = self._soluongbanvatpham(vitri)
                ketquas.append((idmon, f"{ten} x{soluong}", soluong))
        cap25s = [mon for mon in (lamkims or []) if mon[0] == CAPLAMKIMBANKC
                  and (moitruong.get_motathovatphamhanhtrangcosan(mon[2]) or "").startswith(MAMAULAMKIM)]
        # Đã sắp (cấp, giá): giữ SOLAMKIMGIULAIKC món đầu (rẻ nhất), bán phần còn lại
        for capdo, gia, vitri, idmon, ten in cap25s[SOLAMKIMGIULAIKC:]:
            ketquas.append((idmon, f"{ten} (Lam Kim cấp {capdo})", self._soluongbanvatpham(vitri)))
        return ketquas

    def _idtrongtuikc(self):
        # Id mọi món trong 4 túi hành trang
        return [idmon for mons in self.moitruong.get_danhsachvatphamhanhtrang_map().values()
                for vitri, idmon in mons if idmon and vitri < VITRITRANGBIDAUTIEN]

    def _demvatphamkc(self, tens):
        # Tổng số lượng (cộng các chồng) món có tên là 1 trong tens trong túi
        return sum(max(1, self.moitruong.get_soluongvatphamhanhtrang(vitri) or 1) for vitri, _ in self._timcacvatphamkc(tens))

    def _demtraokc(self):
        # Số Cửu Long Thần Hỏa Trảo của mình: mọi ô 4 túi hành trang + pháp bảo đang đeo
        so = 1 if self._is_traokc(self.moitruong.get_tenphapbaohientai()) else 0
        for ten, mons in self.moitruong.get_danhsachvatphamhanhtrang_map().items():
            if self._is_traokc(ten):
                so += sum(1 for vitri, iddoituong in mons if iddoituong and vitri < VITRITRANGBIDAUTIEN)
        return so

    def _kiemtratraothuhoikc(self, s):
        # Thu hồi xong (đã chờ THOIGIANBAOXONGKC giây cho túi cập nhật): số Trảo nhận về ít hơn số acc gà đang giữ lúc bắt đầu thu hồi thì
        # báo log + Telegram (trước đây thiếu 1 Trảo vẫn báo xong im re, người dùng 2026-11-08)
        if s.get("dakiemtratrao") or "sotraodauthuhoi" not in s:
            return
        s["dakiemtratrao"] = True
        try:
            nhan = self._demtraokc() - s["sotraodauthuhoi"]
        except Exception:
            return
        can = len(s.get("gacotraothuhoi") or [])
        if nhan >= can:
            self._logkc(f"{TRAOKEOCAPs[0]}: đã nhận lại {nhan}/{can} cái")
            return
        noidung = (f"Thu hồi thiếu {TRAOKEOCAPs[0]}: nhận lại {nhan}/{can} cái (acc gà giữ Trảo: "
                   f"{', '.join(map(str, s['gacotraothuhoi']))}), còn {self._demtraokc()} cái trong túi. Kiểm tra tay giúp")
        self._logkc("⚠️ " + noidung)
        baosuco(self.moitruong, "vatpham", f"Kéo cấp: {noidung}", khoa = "thieutraokc", giancach = 0.)

    def _raphongyeukc(self, s):
        # Ra khỏi Phong Yêu Kính: tắt Phong Yêu Kính; trưởng nhóm giải tán nhóm (cả nhóm bị đưa ra Chu Quốc), không được (thành viên /
        # quá thời gian) thì nói chuyện Thỏ Yêu "1. Ta muốn về Chu Quốc" (ra cạnh Tả Khâu Minh)
        moitruong = self.moitruong
        py = (self._langlyson or {}).get("py") or {}
        if py.get("vitrithoyeu") and py.get("bandothoyeu") == moitruong.get_idbandohientai():
            s["vitrithoyeu"] = py["vitrithoyeu"]
        if self._langlyson:
            self.huy_langlyson()
        if self._giaitanraphongyeu(s):
            return None
        diachi = moitruong.action_timkiemnhanvat(tennhanvat = laytenthoyeu(moitruong))
        if diachi:
            s["vitrithoyeu"] = moitruong.get_toado(diachi)
        if not s.get("vitrithoyeu"):
            # Tắt bật lại giữa phó bản: toạ độ Thỏ Yêu đã lưu theo bản đồ (_vitrithoyeu)
            s["vitrithoyeu"] = taivitrithoyeu(f"{'nietban' if moitruong.is_nietban else 'aegis'}|{moitruong.get_idbandohientai()}")
        x, y = s.get("vitrithoyeu") or moitruong.get_toado()
        s["trangthai"] = "thu hồi đồ Lam Kim: nói chuyện Thỏ Yêu ra khỏi Phong Yêu Kính"
        return self._noichuyenlls(s, laytenthoyeu(self.moitruong), x, y, is_chovankhi = False, luachon = 0)[1]

    def _moinhomkc(self, s, gas):
        # Acc chính làm trưởng nhóm, mời lần lượt acc gà chưa ở trong nhóm (vào rồi thì mời người kế ngay)
        moitruong = self.moitruong
        now = time.time()
        idtoi = moitruong.get_idnguoichoi()
        if moitruong.get_is_dangnamtrongnhom() and not moitruong.get_is_truongnhom():
            # Đang là thành viên nhóm người khác (vd nhóm Phong Yêu Kính cũ): rời để tự lập nhóm
            if now - s.get("lucroinhom", 0.) > GIANCACHROINHOMKC:
                s["lucroinhom"] = now
                self._logkc("Đang ở nhóm người khác: rời để lập nhóm kéo cấp")
                moitruong.action_thoatkhoinhom()
            return
        is_conhom = moitruong.get_is_dangnamtrongnhom()
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if is_conhom else set()
        chuavaos = [idga for idga in gas if idga not in trongnhoms]
        if not chuavaos:
            s["dangmoinhom"] = [0, 0.]
            return
        if not is_conhom:
            # Chưa có nhóm: lập nhóm 1 người trước (như Phong Yêu Kính), lượt sau mới mời
            if now - s.get("luclapnhom", 0.) >= GIANCACHMOINHOMKC:
                s["luclapnhom"] = now
                moitruong.action_thucthicaulenh(f"team + {idtoi}")
            return
        # Mời lần lượt từng người như Tổ đội (người dùng dặn 2026-11-22: trước mời liền cả đám, ai lỡ lời mời phải chờ 5-8s mời lại):
        # người đang mời vào nhóm rồi thì mời người kế ngay lượt này, quá THOIGIANCHOMOITHANHVIEN giây chưa vào thì chuyển người kế
        # (người lâu chưa được mời nhất trước, vòng sau mời lại người lỡ)
        dangmoi, lucmoi = s.setdefault("dangmoinhom", [0, 0.])
        if dangmoi and (dangmoi not in chuavaos or now - lucmoi > THOIGIANCHOMOITHANHVIEN):
            dangmoi = 0
        if dangmoi:
            return
        idga = min(chuavaos, key = lambda i: s["lucmoi"].get(i, 0.))
        if moitruong.action_moihoacxinvaonhom(idga):
            s["lucmoi"][idga] = now
            s["dangmoinhom"] = [idga, now]
            self._logkc(f"Mời {gas[idga].get('tennhanvat') or idga} vào nhóm")
        else:
            s["dangmoinhom"] = [0, 0.]

    def _cosudokc(self, tendd):
        # Acc chính có danh hiệu "Sư Phụ của <tên đồ đệ>" không (bảng Nhân Vật > Danh Hiệu; đồ đệ thì có "Đệ Tử của <sư phụ>", ảnh người
        # dùng 2026-11-14): True / False; None khi không đọc được (danh sách trống: acc chính luôn có danh hiệu khác như VIP, bang)
        try:
            danhhieus = self.moitruong.get_danhsachdanhhieu()
        except Exception:
            return None
        if not danhhieus:
            return None
        tendd = _chuanhoa(tendd).lower()
        for _, tendh in danhhieus:
            tendh = _chuanhoa(tendh).lower()
            if tendh.startswith("sư phụ") and tendh.endswith(tendd):
                return True
        return False

    def _dodethatkc(self, s, gas):
        # Đồ đệ thật theo danh hiệu "Sư Phụ của <tên>": tên đó là acc gà trong lượt mà khác iddode đang nhớ thì đổi sang nó (đã bái sư,
        # chưa xuất sư). Lượt 2026-11-21 bấm Bắt đầu lại giữa chừng bị ghép lại cặp: Gạ (sư phụ gacon4636) nhớ đồ đệ gacon6555, Kng (sư
        # phụ gacon6098) nhớ gacon4636 -> bái sư 3 lần thất bại bị "bỏ qua" coi như xong, tới cấp 50 xuất sư thấy không có "Sư Phụ của
        # <đồ đệ đang nhớ>" là báo xong, đồ đệ thật không xuất sư. Chỉ xét khi lượt có nhận đồ đệ (iddode khác 0); 10 giây một lần
        if not s["iddode"] or time.time() - s.get("luckiemdodethat", 0.) < 10.:
            return
        s["luckiemdodethat"] = time.time()
        try:
            danhhieus = self.moitruong.get_danhsachdanhhieu() or ()
        except Exception:
            return
        tiento = "sư phụ của"
        tens = {_chuanhoa(ten).lower()[len(tiento):].strip() for _, ten in danhhieus if _chuanhoa(ten).lower().startswith(tiento)}
        idthat = next((i for i, info in gas.items() if _chuanhoa(info.get("tennhanvat")).lower() in tens), 0)
        if not idthat or idthat == s["iddode"]:
            return
        self._logkc(f"⚠️ Danh hiệu: mình là sư phụ của {gas[idthat].get('tennhanvat')} (ID {idthat}), không phải đồ đệ đang nhớ "
                    f"(ID {s['iddode']}): đổi đồ đệ sang nó (đã bái sư), tới cấp thì xuất sư nó")
        s.update(iddode = idthat, dabaisu = True, daxuatsu = False)
        s.pop("suphu", None)

    def _buocsuphuchinh(self, s, gas, loai):
        # loai "baisu" / "xuatsu": về Tân Thủ Thôn, nhóm với acc gà đồ đệ (bái sư: nhóm riêng 2 người), đồ đệ đứng gần Mạnh Tử thì chọn
        # "2. ... bái sư" / "3. ... xuất sư" -> lựa chọn đầu ("1. Xác nhận") rồi chờ đồ đệ báo đã xác nhận (_xacnhansuphuga).
        # Hết SOLANSUPHUKC lần mà đồ đệ chưa báo thì coi như xong (báo log, làm tay giúp) để không kẹt cả kéo cấp
        moitruong = self.moitruong
        now = time.time()
        iddode = s["iddode"]
        co = "dabaisu" if loai == "baisu" else "daxuatsu"
        ten = "bái sư" if loai == "baisu" else "xuất sư"
        info = gas.get(iddode)
        if not info:
            s["trangthai"] = f"{ten}: chờ acc gà đồ đệ (ID {iddode}) online, bật kéo cấp"
            return None
        tendd = info.get("tennhanvat") or str(iddode)
        sp = s.setdefault("suphu", {"loai": loai, "buoc": "menu", "solan": 0, "luc": 0.})
        if sp["loai"] != loai:
            sp.update(loai = loai, buoc = "menu", solan = 0, luc = 0.)
        cosudo = self._cosudokc(tendd)
        if (loai == "baisu" and cosudo is True) or (loai == "xuatsu" and cosudo is False):
            # Danh hiệu là chính xác nhất (người dùng chỉ 2026-11-14): bái sư xong sư phụ có "Sư Phụ của <đồ đệ>", xuất sư thì mất
            s[co] = True
            s.pop("suphu", None)
            self._logkc(f"✅ {ten} {tendd}: danh hiệu \"Sư Phụ của {tendd}\" " + ("đã có" if cosudo else "đã mất"))
            phatam(f"Xong {ten}")
            return None
        if loai == "baisu" and cosudo is False:
            # Đã là sư phụ của người khác: Mạnh Tử không hiện hộp Xác nhận, đi 3 lần vô ích (Kng có đồ đệ gacon6098 bị giao gacon4636,
            # 2026-11-21). Bỏ bái sư, báo log để xuất sư tay
            khac = next((ten for _, ten in self.moitruong.get_danhsachdanhhieu() if _chuanhoa(ten).lower().startswith("sư phụ của")), "")
            if khac:
                s[co] = True
                s.pop("suphu", None)
                self._logkc(f"⚠️ Bỏ bái sư {tendd}: mình đang có danh hiệu \"{khac}\" (đã có đồ đệ khác, xuất sư trước mới nhận được)")
                return None
        if cosudo is None and info["_keocap"].get(co):
            # Không đọc được danh hiệu: tin đồ đệ báo đã chọn Xác nhận như cũ
            s[co] = True
            s.pop("suphu", None)
            self._logkc(f"✅ {tendd} đã xác nhận {ten}")
            phatam(f"Xong {ten}")
            return None
        if self._langlyson:
            self.huy_langlyson()
        if self._is_dangban():
            return None
        _, xnpc, ynpc = NPCMANHTU
        yeucau = self._ditoikc(s, BANDO_TANTHUTHON, (xnpc, ynpc), ten)
        if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            return yeucau
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if moitruong.get_is_dangnamtrongnhom() else set()
        thuas = trongnhoms - {iddode, moitruong.get_idnguoichoi()}
        if thuas:
            # Bái sư / xuất sư phải là nhóm đúng 2 người, sư phụ làm trưởng nhóm (người dùng dặn 2026-11-14: đang nhóm đủ 4 acc gà thì
            # Mạnh Tử không hiện hộp Xác nhận). Rời nhóm đông người; acc gà còn lại thấy trưởng nhóm không phải acc chính thì tự rời
            # (_roinhomkhacchinhkc), acc chính lập nhóm mới chỉ mời đồ đệ; xong sư đồ thì bước bãi / tập hợp mời cả đám lại như thường
            s["trangthai"] = f"{ten}: rời nhóm {len(trongnhoms)} người để lập nhóm riêng với {tendd}"
            if now - s.get("lucroinhom", 0.) > GIANCACHROINHOMKC:
                s["lucroinhom"] = now
                self._logkc(f"{ten}: nhóm còn {len(thuas)} người ngoài đồ đệ, rời nhóm để lập nhóm 2 người với {tendd}")
                moitruong.action_thoatkhoinhom()
            return yeucau
        self._moinhomkc(s, {iddode: info})
        if iddode not in trongnhoms:
            s["trangthai"] = f"{ten}: mời {tendd} vào nhóm"
            return yeucau
        if info.get("tenbando") != BANDO_TANTHUTHON or not info.get("x") \
                or math.dist((info["x"], info["y"]), (xnpc, ynpc)) > KHOANGCACHDODEMANHTU:
            s["trangthai"] = f"{ten}: chờ {tendd} tới Mạnh Tử"
            return yeucau
        if sp["buoc"] == "menu":
            s["trangthai"] = f"{ten}: nói chuyện Mạnh Tử (lần {sp['solan'] + 1})"
            ketqua, yeucau = self._chonmenukc(s, NPCMANHTU[0], xnpc, ynpc, (CHISOBAISU if loai == "baisu" else CHISOXUATSU,))
            if ketqua == "xong":
                sp.update(buoc = "xacnhan", luc = now)
            elif ketqua in ("khongco", "khongmenu"):
                self._logkc(f"Mạnh Tử không có lựa chọn {ten} ({ketqua})")
                sp.update(buoc = "cho", luc = now - THOIGIANCHODODEKC)
            return yeucau
        if sp["buoc"] == "xacnhan":
            # Hộp "Hiện tại bạn có thể nhận <đồ đệ> làm đồ đệ ... 1. Xác nhận" (chưa thấy hộp này lúc xuất sư thì thôi, chờ đồ đệ)
            s["trangthai"] = f"{ten}: xác nhận với Mạnh Tử"
            lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
            noidung = moitruong.get_noidungcuasotuychon()
            if loai == "xuatsu" and "đồ đệ bạn đâu" in noidung:
                # "Bạn sắp sửa xuất sư ? đồ đệ bạn đâu ?" lúc đồ đệ đứng cạnh: không còn đồ đệ nữa = đã xuất sư (mở lại bot giữa chừng)
                moitruong.xoa_noidungcuasotuychon()
                s[co] = True
                s.pop("suphu", None)
                self._logkc(f"✅ Mạnh Tử hỏi đồ đệ đâu: {tendd} đã xuất sư")
                phatam(f"Xong {ten}")
                return None
            # Chỉ chọn hộp của Mạnh Tử: hộp khác hiện lúc đó (Niết Bàn "khai trừ <thành viên> ra khỏi nhóm" lúc lập nhóm riêng) mà chọn
            # lựa chọn đầu là đá người khỏi nhóm
            if noidung.strip().startswith(NPCMANHTU[0]) and lenhs:
                self._logkc(f"Mạnh Tử: {noidung[:80]!r} -> chọn {lenhs[0]!r}")
                moitruong.xoa_noidungcuasotuychon()
                moitruong.action_thucthicaulenh(lenhs[0])
                if loai == "xuatsu" and self._cosudokc(tendd) is None:
                    # Xuất sư không cần đồ đệ xác nhận: sư phụ chọn Xác nhận là xong (từng chờ đồ đệ báo, nói chuyện Mạnh Tử lại 3 lần).
                    # Đọc được danh hiệu thì để bước đầu hàm xét danh hiệu "Sư Phụ của <đồ đệ>" mất hẳn mới coi là xong
                    s[co] = True
                    s.pop("suphu", None)
                    self._logkc(f"✅ {tendd} đã xuất sư")
                    phatam(f"Xong {ten}")
                    return None
                sp.update(buoc = "cho", luc = now)
            elif now - sp["luc"] > THOIGIANCHOMENUKC:
                self._logkc(f"Mạnh Tử không hiện hộp Xác nhận {ten}: chờ {tendd} xác nhận")
                sp.update(buoc = "cho", luc = now)
            return None
        s["trangthai"] = f"{ten}: chờ {tendd} xác nhận"
        if now - sp["luc"] > THOIGIANCHODODEKC:
            sp["solan"] += 1
            if sp["solan"] >= SOLANSUPHUKC:
                s[co] = True
                s.pop("suphu", None)
                self._logkc(f"⚠️ {ten} {tendd}: {SOLANSUPHUKC} lần chưa thấy đồ đệ xác nhận, bỏ qua (làm tay giúp)")
                canhbao(self.moitruong, f"Không {ten} được")
                return None
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            sp["buoc"] = "menu"
        return None

    @staticmethod
    def _tientogakc():
        # Tiền tố tên acc gà của Kéo gà A-Z (_internal/keogatudong.json, ô "Tiền tố" trên giao diện). Không có file (chưa dùng Kéo gà A-Z)
        # thì "" = không trục xuất ai (đừng đoán "ga" mặc định kẻo đá nhầm thành viên thật)
        try:
            with open(os.path.join(os.path.dirname(_thumucthietlap()), "keogatudong.json"), "r", encoding = "utf-8") as f:
                return _chuanhoa(json.load(f).get("tiento") or "")
        except Exception:
            return ""

    def _trucxuatgakc(self, s):
        # Xong kéo cấp: trục xuất khỏi bang acc gà có tên bắt đầu bằng tiền tố Kéo gà A-Z ("org banish <ID>"), mỗi GIANCACHTRUCXUATKC giây
        # 1 người. -> True khi đã gửi hết (hoặc không cần trục xuất ai)
        ds = s.get("cantrucxuat")
        if ds is None:
            ds = []
            tiento = self._tientogakc().casefold()
            if not s.get("moibang", True):
                pass                                    # Không mời bang (acc chính không có bang) thì cũng không trục xuất
            elif any(ten.endswith("Bang Chúng") for _, ten in self.moitruong.get_danhsachdanhhieu()):
                self._logkc("Mình chỉ là Bang Chúng: không trục xuất acc gà khỏi bang")
            elif not tiento:
                self._logkc("Chưa có tiền tố tên acc gà (Kéo gà A-Z): không trục xuất acc gà khỏi bang")
            else:
                tengas = s.get("tengas") or {}
                ds = [i for i in s["idgas"] if _chuanhoa(tengas.get(i)).casefold().startswith(tiento)]
                bo = [f"{tengas.get(i) or '?'} ({i})" for i in s["idgas"] if i not in ds]
                self._logkc(f"Trục xuất khỏi bang acc gà tên bắt đầu \"{tiento}\": "
                            + (", ".join(f"{tengas[i]} ({i})" for i in ds) or "không có")
                            + (f"; giữ lại: {', '.join(bo)}" if bo else ""))
            s["cantrucxuat"] = ds
        if not ds:
            return True
        now = time.time()
        s["trangthai"] = f"trục xuất acc gà khỏi bang (còn {len(ds)})"
        if now - s.get("luctrucxuat", 0.) < GIANCACHTRUCXUATKC:
            return False
        idga = ds.pop(0)
        s["luctrucxuat"] = now
        self._logkc(f"Trục xuất {(s.get('tengas') or {}).get(idga) or idga} khỏi bang (org banish {idga})")
        self.moitruong.action_thucthicaulenh(f"org banish {idga}")
        return False

    def _moibangkc(self, s, gas, solantoida = None, khoa = "solanmoibang"):
        # Mời acc gà chưa đồng ý vào bang ("org invite <ID>"), mỗi GIANCACHMOIBANGKC giây 1 người, mỗi người tối đa solantoida lần (None:
        # không giới hạn). khoa: bộ đếm số lần riêng (ở bãi đếm riêng, không thì số lần mời lúc tập hợp đã vượt giới hạn, ra bãi không
        # mời lại nữa). -> [ID acc gà chưa vào bang]
        # Người dùng tắt ô "Mời acc gà vào bang" (acc chính không có bang): không mời, không ai chờ vào bang
        if not s.get("moibang", True):
            return []
        # Acc chính chỉ là Bang Chúng (danh hiệu "<tên bang> Bang Chúng") thì không mời được: bỏ mời bang, coi như không ai chờ vào bang
        if any(ten.endswith("Bang Chúng") for _, ten in self.moitruong.get_danhsachdanhhieu()):
            if not s.get("bobangchung"):
                s["bobangchung"] = True
                self._logkc("Mình chỉ là Bang Chúng: không mời acc gà vào bang")
            return []
        now = time.time()
        chuabangs = [i for i, info in gas.items() if not info["_keocap"].get("dabang")]
        solans = s.setdefault(khoa, {})
        for idga, info in gas.items():
            if info["_keocap"].get("dabang"):
                # Đã vào bang: xoá bộ đếm, sau này bị ra khỏi bang thì được mời lại đủ lần
                solans.pop(idga, None)
        for idga in chuabangs:
            if solantoida is not None and solans.get(idga, 0) >= solantoida:
                continue
            if now - s["lucmoibang"].get(idga, 0.) >= GIANCACHMOIBANGKC:
                s["lucmoibang"][idga] = now
                solans[idga] = solans.get(idga, 0) + 1
                self._logkc(f"Mời {gas[idga].get('tennhanvat') or idga} vào bang (org invite {idga})")
                self.moitruong.action_thucthicaulenh(f"org invite {idga}")
                break
        return chuabangs

    def _buoctaphopchinh(self, s, gas):
        # Về Tân Thủ Thôn (143, 143), chờ acc gà nhận thưởng tân thủ, mời vào nhóm và vào bang
        moitruong = self.moitruong
        now = time.time()
        if self._is_dangban():
            return None
        yeucau = self._ditoikc(s, BANDO_TANTHUTHON, DIEMTAPHOPKEOCAP, "tập hợp")
        if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            return yeucau
        s.setdefault("luctaphop", now)
        chuaxongs = [info.get("tennhanvat") or str(i) for i, info in gas.items() if not info["_keocap"].get("xongtanthu")]
        if chuaxongs:
            s["trangthai"] = f"tập hợp: chờ {', '.join(chuaxongs)} nhận thưởng tân thủ"
            return yeucau
        # Acc phụ cũng mời nhưng không chờ (chỉ chờ acc gà vào nhóm)
        self._moinhomkc(s, self._nhomkeocapkc(s, gas))
        trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if moitruong.get_is_dangnamtrongnhom() else set()
        chuabangs = self._moibangkc(s, gas)
        chuanhoms = [gas[i].get("tennhanvat") or str(i) for i in gas if i not in trongnhoms]
        if chuanhoms:
            s["trangthai"] = f"tập hợp: mời vào nhóm ({', '.join(chuanhoms)} chưa vào)"
            return yeucau
        # Đưa mỗi acc gà 1 Cửu Long Thần Hỏa Trảo (acc gà tự đeo); chờ tối đa THOIGIANCHOTRAOKC giây, ở bãi vẫn đưa tiếp
        yeucautrao = self._chuyentraokc(s, gas)
        if yeucautrao is not False:
            return yeucautrao
        s.setdefault("lucchotrao", now)
        chuatraos = [info.get("tennhanvat") or str(i) for i, info in gas.items() if info["_keocap"].get("trao") in (None, "")
                     and s["giaotrao"].get(i, 0) < SOLANGIAOTRAOKC]
        if chuatraos and not s.get("luchettrao") and now - s["lucchotrao"] < THOIGIANCHOTRAOKC:
            s["trangthai"] = f"tập hợp: chờ đưa {TRAOKEOCAPs[0]} ({', '.join(chuatraos)} chưa có)"
            return yeucau
        if chuabangs and now - s["luctaphop"] < THOIGIANCHOBANGKC:
            s["trangthai"] = f"tập hợp: mời vào bang ({', '.join(gas[i].get('tennhanvat') or str(i) for i in chuabangs)} chưa đồng ý)"
            return yeucau
        if chuabangs:
            self._logkc(f"⚠️ {', '.join(gas[i].get('tennhanvat') or str(i) for i in chuabangs)} chưa vào bang sau "
                        f"{int(THOIGIANCHOBANGKC)}s, vẫn đi bãi (mời tay giúp)")
        self._sanggiaidoankc(s, f"bai:{BAIKEOCAPs[0][0]}")
        return None

    def _buocphongyeuchinh(self, s, gas):
        # Chọn acc gà give (có đồ Lam Kim), báo qua shared_data; mình làm thành viên Phong Yêu Kính (dò đánh quái)
        now = time.time()
        if self._is_tudongtheosau:
            self._datkc(s, "_is_tudongtheosau", False, "Theo sau")
        idtoi = self.moitruong.get_idnguoichoi()
        s["nhompy"] = [idtoi, *sorted(gas), *sorted(self._layphukc(s))]
        yeucau = self._chuyendolamkimkc(s, gas)
        if yeucau is not False:
            return yeucau
        if s.get("magomdophu") or (s.get("dolamkimchinh") == [] and not any(info["_keocap"].get("codolamkim") for info in gas.values())):
            # Mình hết đồ đưa, acc gà cũng hết: gom đồ Lam Kim của acc phụ về rồi chia tiếp (trước khi kết luận hết đồ dừng kéo cấp)
            yeucau = self._gomdophukc(s, gas)
            if yeucau is not False:
                return yeucau
        give = gas.get(s["idgive"])
        if s["idgive"] and give and give.get("_is_danglanglyson"):
            s["luctatgive"] = 0.
        elif s["idgive"]:
            s["luctatgive"] = s["luctatgive"] or now
            if now - s["luctatgive"] > THOIGIANDOINGUOIGIVE:
                self._logkc(f"{(give or {}).get('tennhanvat') or s['idgive']} không còn đi Phong Yêu Kính (hết đồ / tắt), chọn acc gà khác give")
                s["bogive"] = s["idgive"]
                s["idgive"] = 0
        if not s["idgive"] and self._is_trongphongyeu():
            # Mở lại bot trong Phong Yêu Kính: người give là trưởng nhóm hiện tại (acc gà trong phó bản không đọc túi, codolamkim còn None)
            idtruong = self.moitruong.get_idnguoichoitruongnhom() if self.moitruong.get_is_dangnamtrongnhom() else 0
            if idtruong in gas:
                s["idgive"] = idtruong
                s["luctatgive"] = 0.
                self._logkc(f"Đang trong Phong Yêu Kính: giữ {gas[idtruong].get('tennhanvat') or idtruong} (trưởng nhóm) làm người give")
        if not s["idgive"]:
            # Acc gà đã ở trong Phong Yêu Kính mà mình ở ngoài (mở lại bot, mình bị đưa ra): acc gà trong phó bản không đọc túi (codolamkim
            # None) nên chờ mãi "đọc hành trang" => nhận nó làm người give, mình vào sau qua Tả Khâu Minh (QuanSuMuMuu 9286, 2026-11-03)
            trongs = [i for i in sorted(gas) if gas[i].get("_phobanmuonbando") not in (None, "", TIENTOTENBANDOTAPKICHMONPHAI)]
            if trongs:
                s["idgive"] = trongs[0]
                s["luctatgive"] = 0.
                self._logkc(f"{gas[trongs[0]].get('tennhanvat') or trongs[0]} đang trong Phong Yêu Kính: giữ làm người give")
        if not s["idgive"]:
            cos = [i for i in sorted(gas) if gas[i]["_keocap"].get("codolamkim") and i != s.get("bogive")]
            if not cos:
                cos = [i for i in sorted(gas) if gas[i]["_keocap"].get("codolamkim")]
            if not cos:
                if all(info["_keocap"].get("codolamkim") is False for info in gas.values())                         and not (isinstance(s.get("dolamkimchinh"), list) and s["dolamkimchinh"]):
                    # Mình còn đồ (s["dolamkimchinh"]) mà acc gà nhận ở bản đồ khác (_chuyendolamkimkc trả False chờ gặp) thì chưa dừng
                    # (2026-11-23 19:47: "mình còn 11 món" rồi dừng ngay "không acc gà nào còn đồ")
                    if taigiaodienkeocap().get("tapkich50") and not s.get("botapkich"):
                        # Hết đồ Lam Kim: Tập Kích không cần đồ => đi Tập Kích luôn dù acc gà chưa tới CAPTAPKICHKC (người dùng dặn
                        # 2026-11-23), không dừng kéo cấp
                        if not s.get("hetlamkim"):
                            s["hetlamkim"] = True
                            self._logkc("Hết đồ Lam Kim: chuyển sang đi Tập Kích (không cần đồ)")
                        return None
                    self._ketthuckeocap("❌ Không acc gà nào còn đồ Lam Kim để đốt (ném thêm đồ rồi bật lại)")
                    return None
                s["trangthai"] = "Phong Yêu Kính: chờ acc gà đọc hành trang tìm đồ Lam Kim"
                return None
            s["idgive"] = cos[0]
            s["luctatgive"] = 0.
            self._logkc(f"Chọn {gas[cos[0]].get('tennhanvat') or cos[0]} làm người give Phong Yêu Kính")
        self._roinhomkhacgivekc(s)
        self._batpykc(s)
        s["trangthai"] = f"Phong Yêu Kính: {gas.get(s['idgive'], {}).get('tennhanvat') or s['idgive']} give, mình dò đánh quái (" + ", ".join(
            f"{info.get('tennhanvat') or i} {info['_keocap'].get('capdo')}" for i, info in gas.items()) + ")"
        return False

    def _buoctapkichchinh(self, s, gas, capthap):
        # Ô "Cấp >= 50 đi Tập Kích" bật, acc gà thấp nhất >= CAPTAPKICHKC: đi Tập Kích thay Phong Yêu Kính (mình trưởng nhóm, acc gà / acc
        # phụ theo sau). -> "tapkich" khi đang đi Tập Kích (nơi gọi trả False để tactu_tapkich_xq lo đi lại), False khi không dùng Tập
        # Kích (đi Phong Yêu Kính như cũ)
        moitruong = self.moitruong
        # Hết đồ Lam Kim (hetlamkim) thì đi Tập Kích dù acc gà chưa tới CAPTAPKICHKC
        if not taigiaodienkeocap().get("tapkich50") or (capthap < CAPTAPKICHKC and not s.get("hetlamkim")) or s.get("botapkich")                 or self._is_trongphongyeu():
            if s["giaidoan"] == "tapkich":
                s["giaidoan"] = ""
                if s.get("dabattapkich") and self._tapkich:
                    self.huy_tapkich()
                s["dabattapkich"] = False
            return False
        if self._langlyson:
            self.huy_langlyson()
        s.update(idgive = 0, chuyendo = 0)
        self._sanggiaidoankc(s, "tapkich")
        if s.get("dabattapkich") and not self._tapkich:
            self._logkc("Tập Kích tự dừng (hết lượt / không vào được?): quay lại Phong Yêu Kính")
            s.update(botapkich = True, dabattapkich = False)
            return False
        if not moitruong.get_is_bandotapkichmonphai():
            # Chỉ mời acc gà, không mời acc phụ (người dùng dặn 2026-11-24: acc phụ cấp cao trong nhóm đẩy cấp quái phó bản lên quá cao,
            # acc gà không có kinh nghiệm). Acc phụ đang trong nhóm tự rời (_xulykeocapphu giai đoạn "tapkich")
            self._moinhomkc(s, gas)
        if self._tapkich:
            # Acc gà chưa vào nhóm mình: Tập Kích chờ đủ rồi mới nói chuyện vào phó bản (người dùng 2026-11-23 20:04: chưa mời đủ đã vào)
            trongnhoms = set(moitruong.get_danhsachidnguoichoithanhviennhoms() or ()) if moitruong.get_is_dangnamtrongnhom() else set()
            self._tapkich["thieunhom"] = [info.get("tennhanvat") or str(i) for i, info in gas.items() if i not in trongnhoms]
        if not self._tapkich:
            self.batdau_tapkich()
            if not self._tapkich:
                self._logkc("⚠️ Không bật được Tập Kích (chưa chọn môn phái ở ô Tập Kích, mình chưa vào phái?): đi Phong Yêu Kính")
                s["botapkich"] = True
                return False
            s["dabattapkich"] = True
            self._logkc(f"Acc gà thấp nhất cấp {capthap} >= {CAPTAPKICHKC}: đi Tập Kích thay Phong Yêu Kính")
        self._batgomquaitapkichkc()
        s["trangthai"] = f"{self.get_trangthaitapkich()} (" + ", ".join(
            f"{info.get('tennhanvat') or i} {info['_keocap'].get('capdo')}" for i, info in gas.items()) + ")"
        # Khác False: trước đây trả False nên nơi gọi chạy tiếp xuống Phong Yêu Kính, tắt Tập Kích vừa bật -> bật / tắt mỗi 0,5s, phát âm
        # loạn (log 364 2026-11-23 16:02)
        return "tapkich"

    def _batgomquaitapkichkc(self):
        # Kéo gà đi Tập Kích: acc chính bật "Tự động gom quái" (người dùng dặn 2026-11-24) cho acc gà ăn kinh nghiệm nhanh. Ô cũ nhớ vào
        # tuychoncu của Tập Kích: Tập Kích dừng (_ketthuctapkich) thì trả lại
        if not self._tapkich or self._is_tudonggomquai:
            return
        self._tapkich.setdefault("tuychoncu", {}).setdefault("_is_tudonggomquai", self._is_tudonggomquai)
        self._is_tudonggomquai = True
        self._is_danggomquai = False
        self._danhsachidquaidagom.clear()
        self._logkc("Bật \"Tự động gom quái\" lúc đi Tập Kích (dừng Tập Kích thì trả lại)")

    def _chotiengakc(self, s, gas):
        # Acc gà ngân lượng < NGUONGTIENGAKC: tới cạnh (khác bản đồ thì sang bản đồ nó) give TIENCHOGAKC. -> yêu cầu / None khi đang lo,
        # False khi không cần
        moitruong = self.moitruong
        now = time.time()
        # Trong phó bản Tập Kích cũng không đi đưa tiền (_ditoikc sẽ phù ra khỏi phó bản giữa vòng)
        if self._is_trongphongyeu() or moitruong.get_is_bandotapkichmonphai() or self._is_dangban():
            return False
        dagiao = s.setdefault("chotien", {})
        cans = [i for i, info in sorted(gas.items()) if isinstance(info["_keocap"].get("nganluong"), int)
                and info["_keocap"]["nganluong"] < NGUONGTIENGAKC and dagiao.get(i, (0, 0.))[0] < SOLANCHOTIENKC
                and not self._is_phutrongpykc(info)]
        if not cans:
            return False
        if (moitruong.get_nganluong() or 0) < TIENCHOGAKC:
            if not s.get("dalogthieutien"):
                s["dalogthieutien"] = True
                self._logkc(f"⚠️ Acc gà hết ngân lượng mà mình cũng không đủ {TIENCHOGAKC}: không đưa được")
            return False
        idga = cans[0]
        info = gas[idga]
        ten = info.get("tennhanvat") or str(idga)
        solan, luc = dagiao.get(idga, (0, 0.))
        if now - luc < GIANCACHCHOTIENKC:
            s["trangthai"] = f"đưa ngân lượng: chờ {ten} nhận"
            return None
        nhan = f"đưa {TIENCHOGAKC} ngân lượng cho {ten} (còn {info['_keocap']['nganluong']})"
        s["trangthai"] = nhan
        diachi = moitruong.action_timkiemnhanvat(idnguoichoi = idga)
        if not diachi:
            if not info.get("tenbando"):
                return False
            x, y = info.get("x"), info.get("y")
            return self._ditoikc(s, info["tenbando"], (x, y) if x and y else None, nhan)
        if moitruong.get_khoangcach(diachi) > KHOANGCACHGIAODOKC - 1:
            x, y = moitruong.get_toado(diachi)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
        moitruong.action_ngatdichuyen()
        for lenh in taolenhgiao(str(idga), [], TIENCHOGAKC):
            moitruong.action_thucthicaulenh(lenh)
            self._logkc(f"Đưa {TIENCHOGAKC} ngân lượng cho {ten} (lần {solan + 1}): {lenh}")
        dagiao[idga] = (solan + 1, now)
        return None

    @staticmethod
    def _is_phutrongpykc(info):
        # Acc phụ đang trong phó bản (mượn bản đồ): đừng gọi ra giữa vòng
        return info.get("_phobanmuonbando") not in (None, "", TIENTOTENBANDOTAPKICHMONPHAI)

    def _gomdophukc(self, s, gas):
        # Phong Yêu Kính, ngoài phó bản: acc phụ còn đồ Lam Kim thì đứng yên chờ chúng tới give SOMONGOMPHUKC món về mình (mã magomdophu,
        # acc phụ báo dagomdo = mã). -> None khi đang chờ (đứng yên), False khi không cần
        now = time.time()
        if self._is_trongphongyeu():
            return False
        phus = self._layphukc(s)
        ma = s.get("magomdophu")
        if ma:
            choes = [info.get("tennhanvat") or str(i) for i, info in phus.items()
                     if info["_keocap"].get("dagomdo") != ma and not self._is_phutrongpykc(info)]
            if choes and now - ma <= THOIGIANGOMDOPHUKC:
                if self._langlyson:
                    self.huy_langlyson()
                self.moitruong.action_ngatdichuyen()
                s["trangthai"] = f"Phong Yêu Kính: đứng yên chờ acc phụ give đồ Lam Kim ({', '.join(choes)}, còn " \
                                 f"{int(THOIGIANGOMDOPHUKC - (now - ma))}s)"
                return None
            self._logkc(f"⚠️ Quá {int(THOIGIANGOMDOPHUKC)}s acc phụ chưa give xong đồ Lam Kim ({', '.join(choes)}): chia đồ đã có" if choes
                        else "Acc phụ đã give hết đồ Lam Kim về mình: chia tiếp cho acc đốt")
            s.pop("magomdophu", None)
            # Đọc lại túi mình ngay (vừa nhận thêm đồ), acc gà nhận đồ tới lấy
            s.update(lucgomdophu = now, dolamkimchinh = "doc")
            s.pop("bogive", None)
            return None
        if now - s.get("lucgomdophu", 0.) < GIANCACHGOMDOPHUKC:
            return False
        cos = [i for i, info in phus.items() if info["_keocap"].get("colamkim") and not self._is_phutrongpykc(info)]
        if not cos:
            return False
        # Cấp đồ tối thiểu theo acc đốt (người give, chưa chọn thì ID nhỏ nhất) như lúc mình đưa đồ (_chuyendolamkimkc)
        idnhan = s["idgive"] if s["idgive"] in gas else (min(gas) if gas else 0)
        capnhan = (gas[idnhan]["_keocap"].get("capdo") or 0) if idnhan else 0
        s["capgomphu"] = max(CAPDOLAMKIMTOITHIEU, capnhan - taicauhinhphongyeu(is_keoga = True)["caphonnhanvat"])
        s["magomdophu"] = round(now, 3)
        self._logkc("Mình và acc gà hết đồ Lam Kim, acc phụ còn đồ (" + ", ".join(phus[i].get("tennhanvat") or str(i) for i in cos)
                    + f"): đứng yên chờ give {SOMONGOMPHUKC} món cấp >= {s['capgomphu']} về mình")
        return None

    def _docdolamkimphukc(self, s):
        # Acc phụ ngoài phó bản (gom đồ / Phong Yêu Kính): túi còn đồ Lam Kim (mọi cấp) không, báo "colamkim" để acc chính gọi give về
        if self._is_trongphongyeu() or time.time() - s.get("lucdoclkphu", 0.) < GIANCACHDOCDOLAMKIMKC or self._is_dangban():
            return
        ds = self._chondolamkim(s, captoithieu = 0, is_tatca = True)
        if ds == "doc":
            return
        s["lucdoclkphu"] = time.time()
        co = bool(ds)
        if co != s.get("colamkim"):
            self._logkc(f"Đồ Lam Kim trong túi (give về acc chính): {f'{len(ds)} món' if co else 'không có'}")
        s["colamkim"] = co

    def _chuyendolamkimkc(self, s, gas):
        # Acc chính còn đồ Lam Kim mà acc gà nhận đồ (người give, chưa chọn thì ID nhỏ nhất) đã hết: đứng yên chờ acc gà đó tới cạnh rồi
        # give hết đồ đủ cấp acc gà. Chỉ làm ngoài phó bản. -> yêu cầu di chuyển / None khi đang lo đưa đồ, False khi không cần
        moitruong = self.moitruong
        now = time.time()
        if self._is_trongphongyeu() or s.get("bochuyendo"):
            s["chuyendo"] = 0
            return False
        idnhan = s["idgive"] if s["idgive"] in gas else min(gas)
        nhan = gas[idnhan]
        if nhan["_keocap"].get("codolamkim") is not False:
            s.update(chuyendo = 0, is_tuidaynhan = False)
            return False
        tennhan = nhan.get("tennhanvat") or str(idnhan)
        if s.get("is_tuidaynhan"):
            # Acc gà đầy túi giữa chừng (đã nhận được vài món): chờ nó đọc lại túi báo có đồ, đốt hết thì vòng sau đưa tiếp
            if now - s.get("lucgiaodo", 0.) < THOIGIANCHONHANDOKC:
                s["trangthai"] = f"Phong Yêu Kính: {tennhan} đầy túi, chờ nhận đồ Lam Kim đã đưa"
                return None
            self._logkc(f"⚠️ {tennhan} đầy túi mà quá {int(THOIGIANCHONHANDOKC)}s chưa báo có đồ Lam Kim: thôi đưa đồ, ném tay giúp")
            s.update(bochuyendo = True, chuyendo = 0, is_tuidaynhan = False)
            return False
        # Give xong GIANCACHGIAODOKC giây thì đọc lại túi (xét món vừa give đã đi chưa) rồi mới give món kế
        is_docsaugiao = s.get("lucdocdochinh", 0.) <= s.get("lucgiaodo", 0.) and now - s.get("lucgiaodo", 0.) >= GIANCACHGIAODOKC
        if now - s.get("lucdocdochinh", 0.) > GIANCACHDOCDOCHINHKC or s.get("dolamkimchinh") == "doc" or is_docsaugiao:
            captoithieu = max(CAPDOLAMKIMTOITHIEU, (nhan["_keocap"].get("capdo") or 0) - taicauhinhphongyeu(is_keoga = True)["caphonnhanvat"])
            ds = self._chondolamkim(s, captoithieu = captoithieu, is_tatca = True)
            if ds != "doc":
                s["lucdocdochinh"] = now
                if s.get("dolamkimchinh") not in (None, "doc") and len(ds) < len(s["dolamkimchinh"]):
                    s["sodagiaovong"] = s.get("sodagiaovong", 0) + len(s["dolamkimchinh"]) - len(ds)
                    s["solangiaodo"] = 0
            s["dolamkimchinh"] = ds
        ds = s.get("dolamkimchinh")
        if ds == "doc":
            s["trangthai"] = "Phong Yêu Kính: đọc túi mình tìm đồ Lam Kim đưa acc gà"
            return None
        if not ds:
            if now - s.get("lucgiaodo", 0.) < THOIGIANCHONHANDOKC:
                # Vừa đưa hết đồ: chờ acc gà đọc lại túi (không thì tưởng không ai còn đồ, dừng kéo cấp)
                s["trangthai"] = f"Phong Yêu Kính: chờ {tennhan} nhận đồ Lam Kim"
                return None
            s["chuyendo"] = 0
            return False
        if s.get("chuyendo") != idnhan:
            self._logkc(f"{tennhan} hết đồ Lam Kim, mình còn {len(ds)} món: chờ {tennhan} tới để đưa")
            s.update(chuyendo = idnhan, solangiaodo = 0, sodagiaovong = 0)
            s.pop("luotdi", None)
        if s.get("sodagiaovong", 0) >= SOMONCHIAMOILUOTKC:
            # Chia dần: đủ SOMONCHIAMOILUOTKC món thì chờ acc đốt báo có đồ (đốt hết lượt này thì lượt sau đưa tiếp). Quá
            # THOIGIANCHONHANDOKC giây vẫn báo không có (món vừa đưa không hợp cấp?) thì đưa thêm lượt nữa
            if now - s.get("lucgiaodo", 0.) < THOIGIANCHONHANDOKC:
                s["trangthai"] = f"Phong Yêu Kính: đã đưa {s['sodagiaovong']} món, chờ {tennhan} nhận đồ Lam Kim"
                return None
            self._logkc(f"⚠️ Đã đưa {s['sodagiaovong']} món mà quá {int(THOIGIANCHONHANDOKC)}s {tennhan} chưa báo có đồ Lam Kim: đưa thêm")
            s.update(sodagiaovong = 0, solangiaodo = 0)
        diachi = moitruong.action_timkiemnhanvat(idnguoichoi = idnhan)
        if not diachi:
            if not moitruong.get_is_cungbando(nhan):
                if nhan.get("tenbando") and not nhan.get("_phobanmuonbando") and not self._langlyson:
                    # Chưa bật Phong Yêu Kính (vòng đầu / lượt mới): acc gà đứng chờ ở bản đồ của nó => mình sang đó đưa (trước đây hai bên chờ
                    # nhau mãi, 2026-11-23 19:47 acc gà còn ở Thục Sơn sau Tập Kích)
                    x, y = nhan.get("x"), nhan.get("y")
                    return self._ditoikc(s, nhan["tenbando"], (x, y) if x and y else None,
                                         f"Phong Yêu Kính: sang chỗ {tennhan} đưa {len(ds)} món Lam Kim")
                # Khác bản đồ: để Phong Yêu Kính đưa mình về Chu Quốc (acc gà cũng ở đó chờ)
                s["trangthai"] = f"Phong Yêu Kính: chờ gặp {tennhan} (khác bản đồ) để đưa {len(ds)} món Lam Kim"
                return False
            s["trangthai"] = f"Phong Yêu Kính: chờ {tennhan} tới để đưa {len(ds)} món Lam Kim"
            return None
        if moitruong.get_khoangcach(diachi) > KHOANGCACHGIAODOKC:
            # Chia lượt: mặc định acc gà đi tới, mình đứng yên; quá THOIGIANLUOTDIKC giây chưa tới thì đổi lượt (báo "chinhtoi" để acc gà
            # đứng yên). Hai acc cùng đi tới toạ độ của nhau thì cứ chạy vòng vòng quanh nhau (người dùng báo)
            luot = s.get("luotdi")
            if not luot or luot["id"] != idnhan:
                luot = s["luotdi"] = {"id": idnhan, "ai": "ga", "luc": now}
                moitruong.action_ngatdichuyen()
            elif now - luot["luc"] > THOIGIANLUOTDIKC:
                luot.update(ai = "chinh" if luot["ai"] == "ga" else "ga", luc = now)
                moitruong.action_ngatdichuyen()
                self._logkc(f"Quá {int(THOIGIANLUOTDIKC)}s chưa đứng cạnh {tennhan}: " +
                            ("mình đi tới, " + tennhan + " đứng yên" if luot["ai"] == "chinh" else tennhan + " đi tới, mình đứng yên"))
            if luot["ai"] == "ga":
                s["trangthai"] = f"Phong Yêu Kính: đứng yên chờ {tennhan} tới để đưa đồ Lam Kim"
                return None
            s["trangthai"] = f"Phong Yêu Kính: lại gần {tennhan} (đứng yên) để đưa đồ Lam Kim"
            x, y = moitruong.get_toado(diachi)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
        s.pop("luotdi", None)
        if now - s.get("lucgiaodo", 0.) < GIANCACHGIAODOKC or s.get("lucdocdochinh", 0.) <= s.get("lucgiaodo", 0.):
            return None
        if s.get("solangiaodo", 0) >= SOLANGIAODOKC:
            if s.get("sodagiaovong"):
                # Đã nhận được vài món rồi mới hỏng: acc gà đầy túi, để nó đốt số đã nhận
                self._logkc(f"{tennhan} đầy túi: đã đưa {s['sodagiaovong']} món, mình còn {len(ds)} món, {tennhan} đốt hết thì đưa tiếp")
                s.update(is_tuidaynhan = True, lucgiaodo = now)
                return None
            self._logkc(f"⚠️ Give {SOLANGIAODOKC} lần mà đồ Lam Kim không giảm (đồ khoá / {tennhan} đầy túi?): thôi đưa đồ, ném tay giúp")
            s.update(bochuyendo = True, chuyendo = 0)
            return False
        # Give từng món (cả lệnh nhiều món thì acc gà thiếu chỗ là hỏng hết); hỏng thì lần sau thử món khác (món đó có thể bị khoá)
        mon = ds[s.get("solangiaodo", 0) % len(ds)]
        moitruong.action_ngatdichuyen()
        for lenh in taolenhgiao(str(idnhan), [(mon[3], 1)], 0):
            moitruong.action_thucthicaulenh(lenh)
            self._logkc(f"Đưa {mon[4]} (cấp {mon[0]}) cho {tennhan}: {lenh}")
        s.update(lucgiaodo = now, solangiaodo = s.get("solangiaodo", 0) + 1)
        s["trangthai"] = f"Phong Yêu Kính: đưa đồ Lam Kim cho {tennhan} (còn {len(ds)} món)"
        return None

    def _roinhomkhacgivekc(self, s):
        # Phong Yêu Kính: người give lập nhóm 1 người rồi mời; ai còn ở nhóm khác (nhóm kéo cấp của acc chính) thì không nhận được lời mời
        # => ở ngoài phó bản mà đang ở nhóm không phải của người give thì rời
        moitruong = self.moitruong
        if not s["idgive"] or s["idgive"] == moitruong.get_idnguoichoi() or self._is_trongphongyeu() or not moitruong.get_is_dangnamtrongnhom():
            return
        if moitruong.get_idnguoichoitruongnhom() == s["idgive"] or time.time() - s.get("lucroinhom", 0.) < GIANCACHROINHOMKC:
            return
        s["lucroinhom"] = time.time()
        self._logkc("Rời nhóm cũ để vào nhóm người give Phong Yêu Kính")
        moitruong.action_thoatkhoinhom()

    def _batpykc(self, s):
        # Bật Phong Yêu Kính (ai tắt thì THOIGIANBATLAIPYKC giây sau bật lại)
        if self._langlyson:
            if self._langlyson["phoban"] != "phongyeukinh":
                self.huy_langlyson()
            return
        if time.time() - s["lucbatpy"] < THOIGIANBATLAIPYKC:
            return
        s["lucbatpy"] = time.time()
        self._logkc("Bật Phong Yêu Kính")
        self.batdau_langlyson("phongyeukinh")

    # --- Acc gà -------------------------------------------------------------------------------------------------------------------------
    def _laychinh(self, s):
        info = self._laycuasokeocap().get(s["idchinh"])
        return info if info and info["_keocap"].get("vaitro") == "chinh" else None

    def _xulykeocapga(self, s):
        moitruong = self.moitruong
        # Tăng cấp theo ô "Tự tăng cấp tới cấp" của người dùng, kéo cấp không tự bật/đổi nữa; bản lưu cũ đã đổi thì trả lại ngay
        tuychoncu = s.get("tuychoncu") or {}
        for thuoctinh in ("_is_tudongtangcap", "_captudongtangcaptoida"):
            if thuoctinh in tuychoncu:
                setattr(self, thuoctinh, tuychoncu.pop(thuoctinh))
        if not s["idchinh"]:
            # Bật "Làm acc gà" (máy khác nối LAN): tự nhận acc chính đang kéo cấp; acc chính thấy mình báo idchinh là nó thì thêm vào
            # danh sách acc gà. Chưa thấy thì vẫn làm tân thủ (không cần acc chính), xong thì chờ
            chinhs = sorted(i for i, info in self._laycuasokeocap().items()
                            if info["_keocap"].get("vaitro") == "chinh" and info["_keocap"].get("giaidoan") != "xong")
            if chinhs:
                s["idchinh"] = chinhs[0]
                self._logkc(f"Làm acc gà cho acc chính ID {s['idchinh']}" + (f" (thấy {len(chinhs)} acc chính, lấy ID nhỏ nhất)" if len(chinhs) > 1 else ""))
            elif s["xongtanthu"]:
                s["trangthai"] = "chờ thấy acc chính đang kéo cấp (cùng máy / qua LAN)"
                self._tatsautheokc(s)
                return None
        # Cấp kết thúc theo acc chính (người dùng chọn trên giao diện), chưa thấy acc chính thì giữ lần đọc trước
        chinh = self._laychinh(s)
        if chinh:
            s["capketthuc"] = int(chinh["_keocap"].get("capketthuc") or CAPKETTHUCKEOCAP)
        phu = self._laysuphuphukc() if s["xongtanthu"] else None
        if not (phu and phu["_keocap"].get("suphudang")):
            # Acc chính 2 đang dắt mình đi bái sư / xuất sư: không nhận lời mời nhóm acc chính (_theosuphuga nhận lời mời acc chính 2)
            self._dongykeocapga(s)
        self._kiemtrabangkc(s)
        self._congtiemnangkc(s)
        if not s["xongtanthu"]:
            self._tatsautheokc(s)
            if self._is_dangban():
                return None
            return self._buoctanthuga(s)
        self._doctraokc(s)
        self._dungvatphamconsotkc(s)
        if s.get("giaidoan") not in ("thuhoi", "xong"):
            yeucau = self._kiemtrax2kc(s)
            if yeucau is not False:
                self._tatsautheokc(s)
                return yeucau
        chinh = self._laychinh(s)
        if not chinh:
            s["trangthai"] = f"chờ acc chính (ID {s['idchinh']}) bật kéo cấp"
            self._tatsautheokc(s)
            return None
        giaidoan = chinh["_keocap"].get("giaidoan") or ""
        if giaidoan == "xong":
            self._ketthuckeocap("✅ Acc chính báo xong")
            return None
        s["giaidoan"] = giaidoan if giaidoan != "tanthu" else "taphop"
        s["is_dangnhando"] = False
        # Sư phụ là acc chính 2 (acc phụ có iddode là mình) thì Mạnh Tử hỏi theo nó; nó đang bái sư / xuất sư thì theo nó, không theo acc chính
        phu = self._laysuphuphukc()
        self._xacnhansuphuga(s, phu or chinh)
        if phu and phu["_keocap"].get("suphudang") and giaidoan != "phongyeu" and not self._is_trongphongyeu():
            return self._theosuphuga(s, phu)
        if giaidoan == "thuhoi":
            self._tatsautheokc(s)
            return self._buocthuhoiga(s, chinh)
        if giaidoan == "gomdo":
            self._tatsautheokc(s)
            return self._buocgomdoga(s, chinh)
        if giaidoan == "phongyeu":
            self._tatsautheokc(s)
            s["is_dangnhando"] = chinh["_keocap"].get("chuyendo") == moitruong.get_idnguoichoi() and not self._is_trongphongyeu()
            if s["is_dangnhando"]:
                # Acc chính chờ đưa đồ Lam Kim cho mình: đọc túi thường xuyên, tới cạnh acc chính (khác bản đồ thì để Phong Yêu Kính đưa
                # về Chu Quốc, acc chính cũng về đó)
                s["lucdocdo"] = min(s["lucdocdo"], time.time() - GIANCACHDOCDOLAMKIMKC + GIANCACHDOCDONHANKC)
                self._docdolamkimkc(s)
                s["trangthai"] = f"Phong Yêu Kính: tới nhận đồ Lam Kim từ {chinh.get('tennhanvat') or s['idchinh']}"
                if not moitruong.get_is_cungbando(chinh) or moitruong.get_is_vuaroiphobanmuonbando():
                    return False if self._langlyson else None
                if chinh["_keocap"].get("chinhtoi"):
                    # Lượt acc chính đi tới mình: đứng yên (cả hai cùng đi thì chạy vòng vòng quanh nhau)
                    if not s.get("is_dungchonhando"):
                        s["is_dungchonhando"] = True
                        moitruong.action_ngatdichuyen()
                    s["trangthai"] = f"Phong Yêu Kính: đứng yên chờ {chinh.get('tennhanvat') or s['idchinh']} tới đưa đồ Lam Kim"
                    return None
                s["is_dungchonhando"] = False
                x, y = self._toadochinhnhandokc(s, chinh)
                if x and y and moitruong.get_khoangcachdiem(x, y) > KHOANGCACHGIAODOKC - 1:
                    return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
                return None
            self._docdolamkimkc(s)
            s["idgive"] = chinh["_keocap"].get("idgive") or 0
            if not s["idgive"]:
                s["trangthai"] = "Phong Yêu Kính: chờ acc chính chọn người give"
                return None
            self._roinhomkhacgivekc(s)
            self._batpykc(s)
            s["trangthai"] = "Phong Yêu Kính: " + ("mình give, " if s["idgive"] == moitruong.get_idnguoichoi() else "") + \
                             (self.get_trangthailanglyson() or "chờ bật")
            return False
        return self._theosauchinhkc(s, chinh, giaidoan)

    def _thoatvungkinkc(self, s, chinh):
        # Ra khỏi phó bản Tập Kích hay bị thả vào vùng kín (log 2230 2026-11-23 16:21 Trang Viên (119, 91): "cả bản đồ không có đường"
        # tới acc chính, đứng mãi, người dùng phải bấm Hồi Môn Phù tay). Cùng bản đồ, cách acc chính > KHOANGCACHXETKINKC ô: mỗi
        # GIANCACHXETKINKC giây tìm đường cả bản đồ, không có đường liền THOIGIANKINKC giây thì dùng Hồi Môn Phù (Vô Môn Phái: Hồi Môn
        # Phái về Tân Thủ Thôn) rồi Theo sau tự phù về. -> True khi vừa dùng phù
        moitruong = self.moitruong
        now = time.time()
        if s.get("dangphukin"):
            # Đã quyết dùng phù: đứng yên, gọi lại tới khi sang bản đồ khác (quá THOIGIANPHUKINTOIDA giây thì thôi). Trước đây gọi 1 lần rồi
            # để Theo sau chạy tiếp: gặp lúc acc khác đang về thành thì phù chỉ được xếp chờ, chạy là huỷ, 60s sau mới thử (1033 20:52)
            if moitruong.get_idbandohientai() != s.get("bandokin") or now - s["dangphukin"] > THOIGIANPHUKINTOIDA:
                s.pop("dangphukin", None)
                return False
            moitruong.action_ngatdichuyen()
            self.action_sudunghoithanhphu(nguon = "[KÉO CẤP] kẹt vùng kín, không có đường tới acc chính", is_vemonphai = True)
            s["trangthai"] = f"kẹt vùng kín ở {moitruong.get_toado()}: chờ dùng Hồi Môn Phù"
            return True
        x, y = chinh.get("x"), chinh.get("y")
        if not (x and y) or moitruong.get_is_bandotapkichmonphai() or not moitruong.get_is_cungbando(chinh) \
                or moitruong.get_khoangcachdiem(x, y) <= KHOANGCACHXETKINKC:
            s.pop("luckin", None)
            return False
        if now - s.get("lucxetkin", 0.) < GIANCACHXETKINKC:
            return False
        s["lucxetkin"] = now
        if moitruong.get_sobuocduongtoi(x, y, 2., is_cabando = True) is not None:
            s.pop("luckin", None)
            return False
        s.setdefault("luckin", now)
        if now - s["luckin"] < THOIGIANKINKC or now - s.get("lucphukin", 0.) < GIANCACHPHUKINKC:
            return False
        s.update(lucphukin = now, dangphukin = now, bandokin = moitruong.get_idbandohientai())
        s.pop("luckin", None)
        self._logkc(f"Kẹt vùng kín ở {moitruong.get_toado()}, không có đường tới acc chính ({x}, {y}): đứng yên dùng Hồi Môn Phù")
        moitruong.action_ngatdichuyen()
        self.action_sudunghoithanhphu(nguon = "[KÉO CẤP] kẹt vùng kín, không có đường tới acc chính", is_vemonphai = True)
        return True

    def _theosauchinhkc(self, s, chinh, giaidoan):
        # Acc gà / acc phụ ngoài Phong Yêu Kính: vào nhóm acc chính, theo sau acc chính (tự tìm đường / phù sang bản đồ khác)
        moitruong = self.moitruong
        if self._is_trongphongyeu() and giaidoan in GIAIDOANSAUPHONGYEUKCs:
            # Acc chính đã ra khỏi Phong Yêu Kính đi xuất sư / chờ acc chính 2 (mọi acc gà tới cấp kết thúc): mình cũng ra (trưởng nhóm thì
            # giải tán nhóm cho cả nhóm ra). Trước đây chờ mãi trong đó: acc chính không phải trưởng nhóm nên nói chuyện Thỏ Yêu ra 1 mình,
            # về Tân Thủ Thôn mời đồ đệ mãi không được (2026-11-21)
            yeucau = self._raphongyeukc(s)
            s["trangthai"] = f"acc chính đang {self._tengiaidoan(giaidoan)}: ra khỏi Phong Yêu Kính"
            return yeucau
        if self._is_trongphongyeu():
            # Acc chính vừa mở lại bot (chưa tới giai đoạn Phong Yêu Kính): chờ, không tắt Phong Yêu Kính / rời nhóm (rời là bị đưa ra)
            s["trangthai"] = f"đang trong Phong Yêu Kính, chờ acc chính (đang {self._tengiaidoan(giaidoan)})"
            return False if self._langlyson else None
        if self._langlyson:
            self.huy_langlyson()
        self._roinhomkhacchinhkc(s)
        if "muctieutheosaucu" not in s:
            s["muctieutheosaucu"] = (self._idmuctieutheosau, self._tenmuctieutheosau)
        if self._idmuctieutheosau != s["idchinh"]:
            self.thietlap_muctieutheosau(s["idchinh"], chinh.get("tennhanvat") or "")
        if s["vaitro"] == "phu" and not s.get("chinh2"):
            # Acc phụ: Theo sau / Tự tìm đường theo sau theo ô của người dùng (_xulykeocapphu)
            s["trangthai"] = (f"theo sau {chinh.get('tennhanvat') or s['idchinh']}" if self._is_tudongtheosau else "không theo sau (ô Theo sau đang tắt)") \
                + f" ({self._tengiaidoan(giaidoan)}, cấp {moitruong.get_capdonhanvat()})"
            return False
        self._datkc(s, "_is_tudongtheosau", True, "Theo sau")
        self._datkc(s, "_is_tutimduongtheosau", True, "Tự tìm đường theo sau")
        if self._thoatvungkinkc(s, chinh):
            return None
        tien = moitruong.get_nganluong()
        if s["vaitro"] == "ga" and isinstance(tien, int) and tien < NGUONGTIENGAKC and not moitruong.get_is_cungbando(chinh)                 and time.time() - s.setdefault("lucchotien", time.time()) < THOIGIANCHOTIENKC:
            # Hết tiền mà acc chính ở bản đồ khác: đứng yên chờ acc chính mang tiền tới (_chotiengakc), không theo sau (Hồi Môn Phái
            # miễn phí về Tân Thủ Thôn rồi không đủ tiền phù tiếp, chạy bộ hàng chục cổng, hai bên đuổi nhau). Nhận tiền rồi mới theo
            if not s.get("dalogchotien"):
                s["dalogchotien"] = True
                self._logkc(f"Còn {tien} ngân lượng (< {NGUONGTIENGAKC}), acc chính ở bản đồ khác: đứng yên chờ acc chính mang tiền tới")
            self._tatsautheokc(s)
            moitruong.action_ngatdichuyen()
            s["trangthai"] = f"hết tiền ({tien}): đứng yên chờ {chinh.get('tennhanvat') or s['idchinh']} mang tiền tới"
            return None
        s.pop("dalogchotien", None)
        if not (isinstance(tien, int) and tien < NGUONGTIENGAKC):
            s.pop("lucchotien", None)
        s["trangthai"] = f"theo sau {chinh.get('tennhanvat') or s['idchinh']} ({self._tengiaidoan(giaidoan)}, cấp {moitruong.get_capdonhanvat()})"
        return False

    def _laysuphuphukc(self):
        # Acc phụ (acc chính 2) nhận mình làm đồ đệ: info / None
        idminh = self.moitruong.get_idnguoichoi()
        if not idminh:
            return None
        return next((info for _, info in sorted(self._laycuasokeocap().items())
                     if info["_keocap"].get("vaitro") == "phu" and info["_keocap"].get("iddode") == idminh), None)

    def _theosuphuga(self, s, phu):
        # Acc chính 2 đang dắt mình đi bái sư / xuất sư: vào nhóm riêng của nó (rời nhóm acc chính), theo sau nó tới Mạnh Tử. Xong thì
        # _theosauchinhkc rời nhóm nó, theo sau acc chính lại như cũ
        moitruong = self.moitruong
        now = time.time()
        idphu = int(phu["idnguoichoi"])
        tenphu = phu.get("tennhanvat") or str(idphu)
        moitruong.action_kiemtravadongyloimoinhom([idphu])
        if moitruong.get_is_dangnamtrongnhom() and moitruong.get_idnguoichoitruongnhom() != idphu \
                and now - s.get("lucroinhom", 0.) > GIANCACHROINHOMKC:
            s["lucroinhom"] = now
            self._logkc(f"Sư phụ {tenphu} (acc chính 2) đang {'bái sư' if phu['_keocap'].get('suphudang') == 'baisu' else 'xuất sư'}: "
                        f"rời nhóm để vào nhóm nó")
            moitruong.action_thoatkhoinhom()
        if "muctieutheosaucu" not in s:
            s["muctieutheosaucu"] = (self._idmuctieutheosau, self._tenmuctieutheosau)
        if self._idmuctieutheosau != idphu:
            self.thietlap_muctieutheosau(idphu, tenphu)
        self._datkc(s, "_is_tudongtheosau", True, "Theo sau")
        self._datkc(s, "_is_tutimduongtheosau", True, "Tự tìm đường theo sau")
        s["trangthai"] = f"theo sư phụ {tenphu} (acc chính 2) đi {'bái sư' if phu['_keocap'].get('suphudang') == 'baisu' else 'xuất sư'}"
        return False

    def _toadochinhnhandokc(self, s, chinh):
        # Toạ độ acc chính để acc gà tới nhận đồ: thấy trên màn hình thì lấy đúng toạ độ đó; không thấy thì toạ độ chia sẻ, nhưng vừa nhảy
        # xa (BUOCNHAYTOADOKC) thì chờ đứng yên THOIGIANTOADOONDINHKC giây (toạ độ cũ lúc vừa đổi bản đồ). -> (x, y) / (None, None)
        moitruong = self.moitruong
        now = time.time()
        diachi = moitruong.action_timkiemnhanvat(idnguoichoi = s["idchinh"])
        if diachi:
            x, y = moitruong.get_toado(diachi)
            s["toadochinhkc"] = (x, y, 0.)
            return round(x), round(y)
        x, y = chinh.get("x"), chinh.get("y")
        if not x or not y:
            return None, None
        cu = s.get("toadochinhkc")
        if not cu or max(abs(cu[0] - x), abs(cu[1] - y)) > BUOCNHAYTOADOKC:
            if cu:
                # Đang đi theo đường tới toạ độ cũ: dừng, không thì client cứ đi hết đường cũ (lần đo đi thêm 12s mới quay lại)
                moitruong.action_ngatdichuyen()
            s["toadochinhkc"] = (x, y, now)
        else:
            s["toadochinhkc"] = (x, y, cu[2])
        if now - s["toadochinhkc"][2] < THOIGIANTOADOONDINHKC:
            return None, None
        return x, y

    def get_is_keocapchuyendo(self):
        # Acc chính đang đưa đồ Lam Kim / acc gà đang tới nhận: không chọn quái (trước đây acc chính "đứng yên chờ" mà Tự động sử dụng kỹ
        # năng vẫn đuổi quái chạy đi, give quá xa hỏng 3 lần là bỏ đưa đồ, log 2026-11-08 18:58 ở Ranh Giới Đầm Lầy)
        s = self._keocap
        if s and s.get("giaidoan") == "gomdo" and s.get("vaitro") in ("chinh", "ga"):
            # Gom đồ Lam Kim về acc chính: acc chính đứng yên, acc gà tới cạnh give
            return True
        return bool(s) and s.get("giaidoan") == "phongyeu" and bool(s.get("chuyendo") or s.get("is_dangnhando"))

    def _buocgomdoga(self, s, chinh, ma = None, somon = 0, captoithieu = 0):
        # Trước Phong Yêu Kính: tới cạnh acc chính give hết đồ Lam Kim (lọc như lúc chọn đồ đốt, mọi cấp), hết thì báo dagomdo = mã gom
        # của acc chính. Give SOLANGIAODOKC lần mà số món không giảm (đồ khoá / acc chính đầy túi) thì thôi, vẫn báo xong
        moitruong = self.moitruong
        now = time.time()
        # ma: mã gom (acc phụ ở Phong Yêu Kính truyền magomdophu của acc chính, _gomdophukc); somon > 0: chỉ give chừng ấy món (rẻ / cấp
        # thấp nhất từ captoithieu), give xong 1 lượt mà số món giảm là xong, không trả hết (acc phụ giữ nhiều đồ, người dùng dặn 2026-11-23)
        ma = (chinh["_keocap"].get("magomdo") if ma is None else ma) or 0.
        if not ma:
            s["trangthai"] = "gom đồ Lam Kim: chờ acc chính"
            return None
        if s.get("dagomdo") == ma:
            s["trangthai"] = "gom đồ Lam Kim: đã give hết về acc chính, chờ vào Phong Yêu Kính"
            return None
        if s.get("magomdodang") != ma:
            s.update(magomdodang = ma, sodogom = None, solankhonggiamgom = 0, lucgomdo = 0.)
        if self._is_trongphongyeu():
            return self._raphongyeukc(s)
        if self._langlyson:
            self.huy_langlyson()
        if self._is_dangban() or now - s["lucgomdo"] < GIANCACHGIAODOKC:
            return None
        ds = self._chondolamkim(s, captoithieu = captoithieu, is_tatca = True)
        if ds == "doc":
            s["trangthai"] = "gom đồ Lam Kim: đọc túi tìm đồ Lam Kim give acc chính"
            return None
        tenchinh = chinh.get("tennhanvat") or str(s["idchinh"])

        def xong(is_conthua):
            s["dagomdo"] = ma
            # Hết đồ thì báo luôn không còn đồ (acc chính chia đồ cho mình ngay); còn sót (đồ khoá...) thì đọc lại túi
            s["codolamkim"] = None if is_conthua else False
            s.update(lucdocdo = 0., lucdoclkphu = 0.)
            return None

        if not ds:
            self._logkc(f"Đã give hết đồ Lam Kim cho {tenchinh}" if s["sodogom"] is not None else "Không có đồ Lam Kim phải give acc chính")
            return xong(False)
        truoc = s["sodogom"]
        if somon and truoc is not None and len(ds) < truoc:
            self._logkc(f"Đã give {truoc - len(ds)} món Lam Kim cho {tenchinh}, còn giữ {len(ds)} món (cấp >= {captoithieu})")
            return xong(True)
        # Tổng số món (trước khi cắt lượt somon): so với lần give trước xem đã giảm chưa
        tong = len(ds)
        if somon:
            ds = ds[:somon]
        if truoc is None or tong < truoc:
            s["solankhonggiamgom"] = 0
        elif s["solankhonggiamgom"] >= SOLANGIAODOKC:
            self._logkc(f"⚠️ Give {SOLANGIAODOKC} lần mà đồ Lam Kim không giảm (đồ khoá / {tenchinh} đầy túi?): thôi give, còn {len(ds)} món")
            return xong(True)
        nhan = f"gom đồ Lam Kim: tới {tenchinh} give {len(ds)} món"
        s["trangthai"] = nhan
        diachi = moitruong.action_timkiemnhanvat(idnguoichoi = s["idchinh"])
        if not diachi:
            x, y = chinh.get("x"), chinh.get("y")
            if not chinh.get("tenbando"):
                return None
            if chinh.get("_phobanmuonbando") and not moitruong.get_is_cungbando(chinh):
                # Acc chính đang trong phó bản mượn ID (Tập Kích mượn Kênh Trịnh Quốc 1): đi tới toạ độ đó ở bản đồ thật không bao giờ gặp,
                # đứng chờ acc chính ra (đánh hết vòng)
                s["trangthai"] = f"{nhan}: chờ acc chính ra khỏi phó bản"
                return None
            return self._ditoikc(s, chinh["tenbando"], (x, y) if x and y else None, nhan)
        if moitruong.get_khoangcach(diachi) > KHOANGCACHGIAODOKC - 1:
            x, y = moitruong.get_toado(diachi)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
        moitruong.action_ngatdichuyen()
        for lenh in taolenhgiao(str(s["idchinh"]), [(mon[3], 1) for mon in ds], 0):
            moitruong.action_thucthicaulenh(lenh)
            self._logkc(f"Give đồ Lam Kim cho {tenchinh}: {lenh}")
        self._logkc(f"Đã gửi {len(ds)} món Lam Kim: " + ", ".join(f"{mon[4]} (cấp {mon[0]})" for mon in ds))
        s.update(lucgomdo = now, sodogom = tong, solankhonggiamgom = s["solankhonggiamgom"] + 1)
        s["trangthai"] = f"gom đồ Lam Kim: give {len(ds)} món cho {tenchinh}"
        return None

    def _buocthuhoiga(self, s, chinh):
        # Acc chính sắp xong kéo cấp: tới cạnh acc chính give trả hết đồ Lam Kim (lọc như lúc chọn đồ đốt, mọi cấp), hết đồ thì báo dathuhoi.
        # Give SOLANGIAODOKC lần mà số món không giảm (đồ khoá / acc chính đầy túi) thì thôi, vẫn báo đã trả để acc chính kết thúc
        moitruong = self.moitruong
        now = time.time()
        if s["dathuhoi"]:
            s["trangthai"] = "thu hồi: đã trả hết đồ Lam Kim, chờ acc chính kết thúc"
            return None
        if self._is_trongphongyeu():
            return self._raphongyeukc(s)
        if self._langlyson:
            self.huy_langlyson()
        # Cấp 60: nhập code welcome2d60 + dùng hết Chén Bạc trước khi trả đồ / ngân lượng (còn trong bang, còn tiền đi đường)
        yeucau = self._buoccode60kc(s)
        if yeucau is not False:
            return yeucau
        if self._is_dangban() or now - s.get("luctrado", 0.) < GIANCACHGIAODOKC:
            return None
        is_traocode = self._is_traocodekc(s)
        if not is_traocode and self._is_traokc(moitruong.get_tenphapbaohientai()):
            # Đang đeo Cửu Long Thần Hỏa Trảo của acc chính: tháo ra túi ("remove 7") rồi trả cùng đồ Lam Kim. Trảo từ code welcome2d
            # bị khoá không give được: cứ đeo, không trả (_is_traocodekc)
            if s.get("solanthaotrao", 0) < SOLANTHAOTRAOKC:
                if moitruong.get_is_dayhanhtrang():
                    # Túi đầy: tháo không được, vứt Chiến Quốc Bảo Điển trước
                    mon = self._timvatphamkc(VATPHAMVUTKHIDAYTUIKC)
                    if mon:
                        vitri, idmon = mon
                        soluong = max(1, moitruong.get_soluongvatphamhanhtrang(vitri) or 1)
                        lenh = "drop ! {}#{}".format(hex(idmon), soluong).replace("0x", "")
                        moitruong.action_thucthicaulenh2(lenh)
                        s["luctrado"] = now - GIANCACHGIAODOKC + GIANCACHVUTDOTHAOTRAOKC
                        self._logkc(f"Túi đầy, không tháo được {TRAOKEOCAPs[0]}: vứt {VATPHAMVUTKHIDAYTUIKC[0]} trước ({lenh!r})")
                        s["trangthai"] = f"thu hồi: túi đầy, vứt {VATPHAMVUTKHIDAYTUIKC[0]}"
                        return None
                    if not s.get("dalogdaytui"):
                        s["dalogdaytui"] = True
                        self._logkc(f"⚠️ Túi đầy mà không có {VATPHAMVUTKHIDAYTUIKC[0]} để vứt: vẫn thử tháo {TRAOKEOCAPs[0]}")
                lenh = f"remove {VITRITRANGBI_PHAPBAO - VITRITRANGBIDAUTIEN + 1}"
                s.update(solanthaotrao = s.get("solanthaotrao", 0) + 1, luctrado = now)
                moitruong.action_thucthicaulenh(lenh)
                self._logkc(f"Tháo {TRAOKEOCAPs[0]} để trả acc chính ({lenh!r}, lần {s['solanthaotrao']})")
                s["trangthai"] = f"thu hồi: tháo {TRAOKEOCAPs[0]}"
                return None
            if not s.get("dacanhbaothaotrao"):
                s["dacanhbaothaotrao"] = True
                self._logkc(f"⚠️ Tháo {TRAOKEOCAPs[0]} {SOLANTHAOTRAOKC} lần không được (túi đầy?): lấy tay giúp")
        ds = self._chondolamkim(s, captoithieu = 0, is_tatca = True)
        if ds == "doc":
            s["trangthai"] = "thu hồi: đọc túi tìm đồ Lam Kim trả acc chính"
            return None
        # Trảo trong túi trả cùng đồ Lam Kim: (id, số lượng, tên)
        trao = None if is_traocode else self._timvatphamkc(TRAOKEOCAPs)
        mons =[(mon[3], 1, f"{mon[4]} (cấp {mon[0]})") for mon in ds] + ([(trao[1], 1, TRAOKEOCAPs[0])] if trao else [])
        # Tạo Hoá Đơn / Bổ Tâm Đơn / phù: trả cả chồng, acc chính đem bán (_banthuhoikc; Bổ Tâm Đơn giữ lại dùng)
        for vitri, idmon in self._timcacvatphamkc(VATPHAMTHUHOIKCs + PHUTHUHOIBANKCs):
            soluong = max(1, moitruong.get_soluongvatphamhanhtrang(vitri) or 1)
            mons.append((idmon, soluong, f"{moitruong.get_tenvatphamhanhtrang(vitri) or 'Đơn'} x{soluong}"))
        # Sách "Nhập Môn": acc chính đem cất kho (_catsachthuhoikc)
        for mon in self._laymoncatkho(TIENTOSACHTHUHOIKCs):
            mons.append((mon["id"], max(1, mon["soluong"]), f"{mon['ten']} x{max(1, mon['soluong'])}"))
        # Toàn bộ ngân lượng mang theo cũng trả acc chính (người dùng dặn 2026-11-14), gửi kèm lệnh give đầu ("$<tiền>")
        tien = max(0, moitruong.get_nganluong() or 0)
        tenchinh = chinh.get("tennhanvat") or str(s["idchinh"])
        if not mons and not tien:
            self._logkc(f"Đã trả hết đồ Lam Kim / {TRAOKEOCAPs[0]} / ngân lượng cho {tenchinh}" if s.get("sodotrado")
                        else "Không có đồ Lam Kim / Trảo / ngân lượng phải trả acc chính")
            s["dathuhoi"] = True
            return None
        ds = mons
        truoc = s.get("sodotrado")
        if not truoc or len(ds) < truoc[0] or tien < truoc[1]:
            s["solankhonggiam"] = 0
        elif s.get("solankhonggiam", 0) >= SOLANGIAODOKC:
            self._logkc(f"⚠️ Give {SOLANGIAODOKC} lần mà đồ Lam Kim / Trảo / ngân lượng không giảm (đồ khoá / {tenchinh} đầy túi?): "
                        "thôi trả, lấy tay giúp")
            s["dathuhoi"] = True
            return None
        motatien = f"{tien:,} ngân lượng".replace(",", ".") if tien else ""
        nhan = f"thu hồi: tới {tenchinh} trả {len(ds)} món" + (f" + {motatien}" if tien else "")
        s["trangthai"] = nhan
        diachi = moitruong.action_timkiemnhanvat(idnguoichoi = s["idchinh"])
        if not diachi:
            x, y = chinh.get("x"), chinh.get("y")
            if not chinh.get("tenbando"):
                return None
            if chinh.get("_phobanmuonbando") and not moitruong.get_is_cungbando(chinh):
                # Acc chính đang trong phó bản mượn ID (Tập Kích mượn Kênh Trịnh Quốc 1): đi tới toạ độ đó ở bản đồ thật không bao giờ gặp,
                # đứng chờ acc chính ra (đánh hết vòng)
                s["trangthai"] = f"{nhan}: chờ acc chính ra khỏi phó bản"
                return None
            return self._ditoikc(s, chinh["tenbando"], (x, y) if x and y else None, nhan)
        if moitruong.get_khoangcach(diachi) > KHOANGCACHGIAODOKC - 1:
            x, y = moitruong.get_toado(diachi)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
        moitruong.action_ngatdichuyen()
        for lenh in taolenhgiao(str(s["idchinh"]), [(mon[0], mon[1]) for mon in ds], tien):
            moitruong.action_thucthicaulenh(lenh)
            self._logkc(f"Trả đồ / ngân lượng cho {tenchinh}: {lenh}")
        self._logkc(f"Đã gửi trả {len(ds)} món" + (f" + {motatien}" if tien else "") + (": " + ", ".join(mon[2] for mon in ds) if ds else ""))
        s.update(luctrado = now, sodotrado = (len(ds), tien), solankhonggiam = s.get("solankhonggiam", 0) + 1)
        s["trangthai"] = f"thu hồi: trả {len(ds)} món" + (f" + {motatien}" if tien else "") + f" cho {tenchinh}"
        return None

    def _buoccode60kc(self, s):
        # Acc gà thu hồi, cấp >= CAPCODE60, ô "Cấp 60: code welcome2d60 + Chén Bạc" bật: Thần Tiên Gia Gia nhập code welcome2d60 (đã có Chén
        # Bạc trong túi thì bỏ qua bước này), rồi dùng hết Chén Bạc. s["code60"]: None (chưa xét) / "code" / "cho" (chờ thưởng) / "dung" /
        # "xong". -> False khi không cần / đã xong (làm tiếp trả đồ), còn lại là yêu cầu di chuyển / None
        moitruong = self.moitruong
        now = time.time()
        buoc = s.get("code60")
        if buoc == "xong":
            return False
        if buoc is None:
            capdo = moitruong.get_capdonhanvat()
            if capdo is None or capdo is False:
                return None
            cochen = bool(self._timvatphamkc(CHENBACs))
            if not taigiaodienkeocap().get("dungcode60", True) or capdo < CAPCODE60 or (s.get("dacode60") and not cochen):
                s["code60"] = "xong"
                return False
            s.update(code60 = "dung" if cochen else "code", luccode60 = now, solancode60 = 0, hoithoai = None)
            self._logkc(f"Cấp {capdo}: " + ("dùng Chén Bạc còn trong túi trước khi trả đồ" if cochen
                                            else f"về {NPCTHANTIENGIAGIA[0]} nhập code {LENHCODE60!r} rồi dùng Chén Bạc trước khi trả đồ"))
            buoc = s["code60"]
        if now - s["luccode60"] > THOIGIANCODE60KC:
            self._logkc(f"⚠️ Quá {int(THOIGIANCODE60KC)}s chưa xong code cấp 60 / Chén Bạc (bước {buoc}, còn "
                        f"{self._demvatphamkc(CHENBACs)} Chén Bạc): thôi, trả đồ acc chính")
            s["code60"] = "xong"
            return False
        if self._is_dangban():
            return None
        tennpc, x, y = NPCTHANTIENGIAGIA
        if buoc == "code":
            if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                return self._ditoikc(s, BANDO_TANTHUTHON, (x, y), "cấp 60: tới Thần Tiên Gia Gia nhập code welcome2d60")
            self._donghopcodekc()
            if now < s.get("luccho", 0.):
                return None
            s["trangthai"] = f"cấp 60: {tennpc} nhập code welcome2d60"
            ketqua, yeucau = self._chonmenukc(s, tennpc, x, y, MENUCODETANTHU)
            if ketqua == "xong":
                moitruong.action_thucthicaulenh(LENHCODE60)
                self._logkc(f"Nhập code cấp 60 ({LENHCODE60!r}), chờ Chén Bạc vào túi")
                s.update(code60 = "cho", lucguicode60 = now, dacode60 = True, hoithoai = None)
            elif ketqua in ("khongco", "khongmenu"):
                self._logkc(f"⚠️ {tennpc} không có lựa chọn Nhập Code ({ketqua}): bỏ code cấp 60, trả đồ acc chính")
                s["code60"] = "xong"
            return yeucau
        if buoc == "cho":
            self._donghopcodekc()
            if self._timvatphamkc(CHENBACs):
                self._logkc(f"Đã nhận {self._demvatphamkc(CHENBACs)} Chén Bạc")
                s["code60"] = "dung"
                return None
            if now - s["lucguicode60"] < THOIGIANCHOTHUONGCODE60:
                s["trangthai"] = "cấp 60: chờ nhận Chén Bạc"
                return None
            s["solancode60"] = s.get("solancode60", 0) + 1
            if s["solancode60"] < SOLANNHAPCODE60:
                self._logkc(f"Gửi code cấp 60 {int(THOIGIANCHOTHUONGCODE60)}s chưa thấy Chén Bạc: nhập lại")
                s.update(code60 = "code", luccho = now + 1., hoithoai = None)
            else:
                self._logkc(f"⚠️ Nhập code cấp 60 {s['solancode60']} lần không thấy Chén Bạc (đã nhập trước đó / túi đầy / code sai?): bỏ qua")
                s["code60"] = "xong"
            return None
        # buoc == "dung": dùng hết Chén Bạc, tự tăng cấp theo (nâng mức tự tăng cấp nếu thấp)
        self._donghopcodekc()
        if s.get("hoithoai") is None and moitruong.get_is_danghiencuasotuychon():
            moitruong.set_is_danghiencuasotuychon(False)
            moitruong.xoa_noidungcuasotuychon()
        mon = self._timvatphamkc(CHENBACs)
        capdo = moitruong.get_capdonhanvat() or 0
        if not mon:
            self._logkc(f"Đã dùng hết Chén Bạc (cấp {capdo})")
            phatam("Dùng hết Chén Bạc")
            s["code60"] = "xong"
            return False
        if not self._is_tudongtangcap or self._captudongtangcaptoida < CAPTANGCAPCHENBAC:
            self._logkc(f"Bật tự tăng cấp tới cấp {CAPTANGCAPCHENBAC} để Chén Bạc lên cấp được (trước: "
                        f"{'bật tới ' + str(self._captudongtangcaptoida) if self._is_tudongtangcap else 'tắt'})")
            self._is_tudongtangcap = True
            self._captudongtangcaptoida = max(self._captudongtangcaptoida, CAPTANGCAPCHENBAC)
        lucdung = s.get("lucdungchen", 0.)
        if now - lucdung < GIANCACHDUNGCHENBAC:
            return None
        kinhnghiem, kinhnghiemcan = moitruong.get_kinhnghiem(), moitruong.get_kinhnghiemcanlencap()
        if kinhnghiem is not None and kinhnghiemcan and kinhnghiem >= kinhnghiemcan and capdo < self._captudongtangcaptoida \
                and now - lucdung < THOIGIANCHOTANGCAPCHENBAC:
            s["trangthai"] = f"cấp 60: chờ tăng cấp (cấp {capdo}) rồi dùng tiếp Chén Bạc"
            return None
        so = self._demvatphamkc(CHENBACs)
        truoc = s.get("sochenbactruoc")
        s["solankhonggiamchen"] = s.get("solankhonggiamchen", 0) + 1 if truoc is not None and so >= truoc else 0
        if s["solankhonggiamchen"] >= SOLANDUNGKHONGGIAMCHENBAC:
            if s.get("cachdungchen") != "use2":
                self._logkc(f"Dùng Chén Bạc bằng \"use !\" {SOLANDUNGKHONGGIAMCHENBAC} lần không giảm: đổi sang \"use2\"")
                s.update(cachdungchen = "use2", solankhonggiamchen = 0)
            else:
                self._logkc(f"⚠️ Dùng Chén Bạc cả \"use !\" lẫn \"use2\" không giảm (còn {so}): bỏ, lấy tay giúp")
                s["code60"] = "xong"
                return False
        is_use2 = s.get("cachdungchen") == "use2"
        moitruong.action_sudungvatpham(mon[1], is_boquaxacnhan = not is_use2, delay = 0., is_use2 = is_use2)
        s.update(lucdungchen = now, sochenbactruoc = so)
        s["trangthai"] = f"cấp 60: dùng Chén Bạc (cấp {capdo}, còn {so})"
        return None

    # --- Acc phụ (máy khác nối LAN) -----------------------------------------------------------------------------------------------------
    def _xulykeocapphu(self, s):
        # Tập hợp / bãi: vào nhóm, theo sau acc chính như acc gà (acc chính mời nếu nhóm còn chỗ); Phong Yêu Kính: thành viên dò đánh quái
        if not s["idchinh"]:
            chinhs = sorted(i for i, info in self._laycuasokeocap().items() if info["_keocap"].get("vaitro") == "chinh")
            if not chinhs:
                s["trangthai"] = "chờ thấy acc chính đang kéo cấp (cùng máy / qua LAN)"
                return False
            s["idchinh"] = chinhs[0]
            self._logkc(f"Làm acc phụ cho acc chính ID {s['idchinh']}" + (f" (thấy {len(chinhs)} acc chính, lấy ID nhỏ nhất)" if len(chinhs) > 1 else ""))
        chinh = self._laychinh(s)
        if not chinh:
            # Acc phụ: Theo sau / Tự tìm đường theo sau luôn theo ô của người dùng (kể cả Phong Yêu Kính: bật thì Theo sau lo như cũ, tắt
            # thì tự dò đánh); bản lưu cũ kéo cấp đã đổi thì trả lại một lần
            if not s.get("chinh2"):
                self._traluatheosauphukc(s)
            s["trangthai"] = f"chờ acc chính (ID {s['idchinh']}) online"
            return False
        giaidoan = chinh["_keocap"].get("giaidoan") or ""
        if giaidoan == "xong":
            self._ketthuckeocap("✅ Acc chính báo xong")
            return None
        s["giaidoan"] = giaidoan
        yeucau = self._suphuphukc(s, chinh, giaidoan)
        if yeucau is not False:
            return yeucau
        # Đồ Lam Kim của acc phụ: không trả ngay (acc phụ giữ nhiều đồ), chỉ ở Phong Yêu Kính khi acc chính hết đồ gọi (magomdophu,
        # _gomdophukc) thì give SOMONGOMPHUKC món đủ cấp acc đốt
        if giaidoan == "phongyeu":
            self._docdolamkimphukc(s)
        magomphu = chinh["_keocap"].get("magomdophu") or 0.
        if giaidoan == "phongyeu" and magomphu and s.get("dagomdo") != magomphu and not self._is_trongphongyeu():
            self._tatsautheokc(s)
            return self._buocgomdoga(s, chinh, magomphu, somon = SOMONGOMPHUKC,
                                     captoithieu = int(chinh["_keocap"].get("capgomphu") or 0))
        if giaidoan == "tapkich" and not self.moitruong.get_is_bandotapkichmonphai():
            return self._ngoaitapkichphukc(s, chinh)
        if s.get("chinh2"):
            # Acc chính 2 của Kéo gà A-Z: không theo ô Theo sau của người dùng (thường tắt, acc chính 2 là nhân vật chơi thật: đứng im ở
            # Mạnh Tử sau bái sư, acc chính chờ "theo sang" mãi, 2026-11-21). Ngoài Phong Yêu Kính luôn theo sau acc chính
            # (_theosauchinhkc), trong Phong Yêu Kính tắt để tự dò đánh; dừng kéo cấp thì trả ô gốc
            if giaidoan == "phongyeu":
                self._tatsautheokc(s)
        else:
            self._traluatheosauphukc(s)
        if giaidoan != "phongyeu":
            self._dongykeocapga(s)
            return self._theosauchinhkc(s, chinh, giaidoan)
        s["idgive"] = chinh["_keocap"].get("idgive") or 0
        if not s["idgive"]:
            s["trangthai"] = "Phong Yêu Kính: chờ acc chính chọn người give"
            return None
        self._roinhomkhacgivekc(s)
        self._batpykc(s)
        s["trangthai"] = f"Phong Yêu Kính: phụ đánh ({self.get_trangthailanglyson() or 'chờ bật'})"
        return False

    def _suphuphukc(self, s, chinh, giaidoan):
        # Acc phụ có đồ đệ (acc chính 2 của Kéo gà A-Z, người dùng dặn 2026-11-21: mỗi acc chính nhận 1 đồ đệ): bái sư khi đồ đệ xong tân
        # thủ (acc chính đứng chờ, _phusudokc), xuất sư khi acc chính cho phép (chinh "phuxuatsu"), như acc chính (_buocsuphuchinh: nhóm
        # riêng 2 người, mình trưởng nhóm). Đồ đệ thấy "suphudang" thì theo mình (_theosuphuga). -> yêu cầu / None, False = không có việc
        s["suphudang"] = ""
        if not s["iddode"] or giaidoan == "phongyeu" or self._is_trongphongyeu():
            return False
        if s["dabaisu"] and s["daxuatsu"] and time.time() - s.get("luckiemdodethat", 0.) < 10.:
            # Đã xong sư đồ: chỉ 10 giây xét lại danh hiệu một lần (_dodethatkc), khỏi đọc shared_data mỗi vòng
            return False
        gas = {i: info for i, info in self._laycuasokeocap().items() if info["_keocap"].get("vaitro") == "ga"}
        self._dodethatkc(s, gas)
        if s["dabaisu"] and s["daxuatsu"]:
            return False
        iddode = s["iddode"]
        info = gas.get(iddode)
        if not s["dabaisu"]:
            if not info or not info["_keocap"].get("xongtanthu"):
                return False
            cap = info["_keocap"].get("capdo") or 0
            if cap > CAPTOIDANHANDODE:
                self._logkc(f"Acc gà đồ đệ (ID {iddode}) đã cấp {cap} > {CAPTOIDANHANDODE}: bỏ bái sư, tới cấp xuất sư vẫn dắt đi xuất sư")
                s["dabaisu"] = True
                return False
            loai = "baisu"
        elif iddode in (chinh["_keocap"].get("phuxuatsu") or ()):
            loai = "xuatsu"
        else:
            return False
        s["suphudang"] = loai
        # Tự đi tới Mạnh Tử: tắt Theo sau acc chính (_traluatheosauphukc trả lại khi xong)
        self._tatsautheokc(s)
        if self._langlyson:
            self.huy_langlyson()
        yeucau = self._buocsuphuchinh(s, gas, loai)
        if s["dabaisu" if loai == "baisu" else "daxuatsu"]:
            s["suphudang"] = ""
        return yeucau

    def _ngoaitapkichphukc(self, s, chinh):
        # Acc chính kéo gà đi Tập Kích: acc phụ không vào nhóm / không theo (người dùng dặn 2026-11-24: acc phụ cấp cao trong nhóm đẩy cấp
        # quái phó bản lên quá cao, acc gà không có kinh nghiệm). Đang trong nhóm acc chính thì rời, tắt Theo sau (giai đoạn khác
        # _traluatheosauphukc / _theosauchinhkc bật lại), đứng yên chờ. Đang trong phó bản Tập Kích (vòng dở) thì để đánh nốt
        moitruong = self.moitruong
        now = time.time()
        if self._langlyson:
            self.huy_langlyson()
        if moitruong.get_is_dangnamtrongnhom() and moitruong.get_idnguoichoitruongnhom() == s["idchinh"] \
                and now - s.get("lucroinhom", 0.) > GIANCACHROINHOMKC:
            s["lucroinhom"] = now
            self._logkc("Acc chính đi Tập Kích chỉ với acc gà: rời nhóm acc chính")
            moitruong.action_thoatkhoinhom()
        self._tatsautheokc(s)
        s["trangthai"] = f"acc chính {chinh.get('tennhanvat') or s['idchinh']} đi Tập Kích chỉ với acc gà: mình đứng ngoài chờ"
        return None

    def _traluatheosauphukc(self, s):
        tuychoncu = s.get("tuychoncu") or {}
        for thuoctinh in ("_is_tudongtheosau", "_is_tutimduongtheosau"):
            if thuoctinh in tuychoncu:
                setattr(self, thuoctinh, tuychoncu.pop(thuoctinh))

    def _tatsautheokc(self, s):
        if self._is_tudongtheosau:
            self._datkc(s, "_is_tudongtheosau", False, "Theo sau")

    def _vaonhomchinhkc(self, s):
        # Acc chính mời mình vào nhóm liên tục (share "lucmoi" có ID mình mới đây) mà không vào được: 2026-11-23 20:01 Gạ mời gacon0530 (1714)
        # 33 lần, nó không bao giờ thấy lời mời (không có "team + 364"), cả nhóm kẹt ở Võ Lâm Bại Hoại. Bị mời quá THOIGIANBIMOIKC giây:
        # đang ở nhóm khác thì rời, không thì tự gửi "team + <ID chính>" (cùng lệnh nút Xác Nhận lời mời / xin vào nhóm), mỗi
        # GIANCACHTUVAONHOMKC giây 1 lần
        moitruong = self.moitruong
        now = time.time()
        chinh = self._laychinh(s)
        idtoi = moitruong.get_idnguoichoi()
        lucmoi = ((chinh or {}).get("_keocap") or {}).get("lucmoi") or {}
        luc = lucmoi.get(idtoi) or lucmoi.get(str(idtoi)) or 0.
        if not luc or now - luc > 8. or (moitruong.get_is_dangnamtrongnhom() and moitruong.get_idnguoichoitruongnhom() == s["idchinh"]):
            s.pop("lucbimoi", None)
            return
        s.setdefault("lucbimoi", now)
        if now - s["lucbimoi"] < THOIGIANBIMOIKC or now - s.get("luctuvaonhom", 0.) < GIANCACHTUVAONHOMKC:
            return
        s["luctuvaonhom"] = now
        if moitruong.get_is_dangnamtrongnhom():
            self._logkc(f"Acc chính mời vào nhóm mãi mà mình đang ở nhóm khác (trưởng nhóm {moitruong.get_idnguoichoitruongnhom()}): rời nhóm")
            moitruong.action_thoatkhoinhom()
        else:
            self._logkc(f"Acc chính mời vào nhóm mãi không thấy lời mời: tự gửi \"team + {s['idchinh']}\"")
            moitruong.action_thucthicaulenh(f"team + {s['idchinh']}")

    def _dongykeocapga(self, s):
        # Hộp Yes/No của acc chính: mời nhóm ("team + <ID chính>"), mời bang ("org join <ID chính>"). Phong Yêu Kính thì để
        # tactu_langlyson_xq đồng ý lời mời của người give
        moitruong = self.moitruong
        if not s["idchinh"]:
            return
        if s["giaidoan"] != "phongyeu":
            # Lời mời nhóm được loop phụ ghi vào moitruong._loimoinhom_map (moitruong.action_ghiloimoinhom)
            moitruong.action_kiemtravadongyloimoinhom([s["idchinh"]])
            self._vaonhomchinhkc(s)
        # Lời mời bang thì nhận cả ở Phong Yêu Kính: acc gà cũ (45/50, bị trục xuất sau lượt trước) kéo tiếp vào thẳng gom đồ / Phong Yêu
        # Kính, acc chính mời lại bang ở đó (2026-11-23)
        if not moitruong.get_is_danghiencuasoyesno():
            return
        lenh = moitruong.get_caulenhmoinhomhientai() or ""
        phan = lenh.split()
        if len(phan) == 3 and phan[:2] == ["org", "join"] and phan[2] == str(s["idchinh"]):
            moitruong.action_thucthicaulenh(lenh)
            moitruong.set_is_danghiencuasoyesno(False)
            # Chưa chắc vào được (bang đầy / lỗi): không đánh dấu dabang ở đây, _kiemtrabangkc hỏi lại bang sau GIANCACHKIEMTRABANGSAUJOIN giây
            s["lucjoinbang"] = time.time()
            self._logkc(f"Đồng ý vào bang ({lenh!r}), chờ kiểm tra lại")

    def _kiemtrabangkc(self, s):
        # Acc gà tự kiểm tra đã vào bang chưa bằng "desc user <ID mình>" (dòng Bang phái), báo dabang cho acc chính theo kết quả thật:
        # chưa vào bang thì acc chính mời lại, vừa "org join" thì hỏi sau GIANCACHKIEMTRABANGSAUJOIN giây, ngoài ra GIANCACHKIEMTRABANG giây
        moitruong = self.moitruong
        now = time.time()
        idminh = moitruong.get_idnguoichoi()
        lucgui = s.get("luckiemtrabang", 0.)
        if lucgui and moitruong.get_thoidiembangphai(idminh) >= lucgui:
            tenbang = moitruong.get_bangphai(idminh)
            dabang = bool(tenbang)
            if dabang != s["dabang"] or s.get("tenbangkc") != tenbang:
                self._logkc(f"Kiểm tra bang: {('đã vào bang ' + tenbang) if dabang else 'chưa có bang'}")
            s.update(dabang = dabang, tenbangkc = tenbang, luckiemtrabang = 0., solanhoibangloi = 0)
            return
        if lucgui and now - lucgui < THOIGIANCHOKIEMTRABANG:
            return
        if lucgui:
            # Không thấy trả lời: hỏi lại sớm tối đa SOLANHOIBANGLOI lần, quá thì đợi lượt định kỳ (giữ dabang cũ)
            s["luckiemtrabang"] = 0.
            s["solanhoibangloi"] = s.get("solanhoibangloi", 0) + 1
            if s["solanhoibangloi"] <= SOLANHOIBANGLOI:
                s["lucjoinbang"] = now
            else:
                self._logkc("⚠️ Hỏi bang (desc user) không thấy trả lời, giữ trạng thái bang cũ")
                s["solanhoibangloi"] = 0
        lucjoin = s.get("lucjoinbang", 0.)
        if lucjoin and now - lucjoin >= GIANCACHKIEMTRABANGSAUJOIN:
            can = True
        else:
            can = now - s.get("luckiemtrabangxong", -999.) >= GIANCACHKIEMTRABANG
        if can and moitruong.action_hoibangphaicuaminh():
            s.update(luckiemtrabang = now, luckiemtrabangxong = now, lucjoinbang = 0.)

    def _roinhomkhacchinhkc(self, s):
        # Tập hợp / bãi: đang ở nhóm không phải của acc chính (nhóm Phong Yêu Kính cũ...) thì rời để nhận lời mời acc chính
        moitruong = self.moitruong
        if not moitruong.get_is_dangnamtrongnhom() or moitruong.get_idnguoichoitruongnhom() == s["idchinh"]:
            return
        if time.time() - s.get("lucroinhom", 0.) > GIANCACHROINHOMKC:
            s["lucroinhom"] = time.time()
            self._logkc("Đang ở nhóm khác: rời để vào nhóm acc chính")
            moitruong.action_thoatkhoinhom()

    def _docdolamkimkc(self, s):
        # Có đồ Lam Kim đốt được không (báo acc chính chọn người give): True / False, None khi chưa đọc xong mô tả
        if self._is_trongphongyeu() or time.time() - s["lucdocdo"] < GIANCACHDOCDOLAMKIMKC:
            return
        chon = self._chondolamkim(s)
        if chon == "doc":
            return
        s["lucdocdo"] = time.time()
        co = bool(chon)
        if co != s["codolamkim"]:
            self._logkc(f"Đồ Lam Kim đốt được: {f'có ({chon[4]}, cấp {chon[0]})' if co else 'không còn'}")
        s["codolamkim"] = co

    @staticmethod
    def _is_traokc(ten):
        # Tên (ô hành trang / pháp bảo đang đeo, tối đa 31 byte nên tên bị cắt thì so đầu tên) là Cửu Long Thần Hỏa Trảo
        ten = _chuanhoa(ten)
        is_bicat = len(ten.encode("utf-8")) >= SOBYTETENBICAT
        return bool(ten) and any(t == ten or (is_bicat and t.startswith(ten)) for t in map(_chuanhoa, TRAOKEOCAPs))

    def _doctraokc(self, s):
        # Acc gà báo acc chính có Cửu Long Thần Hỏa Trảo chưa: "deo" / "tui" / "" (không có), None khi chưa đọc
        now = time.time()
        if now - s.get("lucdoctrao", 0.) < GIANCACHDOCTRAOKC:
            return
        s["lucdoctrao"] = now
        trao = "deo" if self._is_traokc(self.moitruong.get_tenphapbaohientai()) else ("tui" if self._timvatphamkc(TRAOKEOCAPs) else "")
        if trao == "" and not self._is_dudeotraokc():
            trao = "chuacap"
        if trao in ("deo", "tui") and self._is_traocodekc(s):
            # Trảo của code welcome2d: acc chính không đưa thêm, không tính vào số Trảo phải thu hồi (_kiemtratraothuhoikc)
            trao = "code"
        if trao != s.get("trao"):
            self._logkc(f"{TRAOKEOCAPs[0]}: " + {"deo": "đang đeo", "tui": "có trong túi", "": "không có",
                                                  "code": "có từ code tân thủ (bị khoá, không trả acc chính)",
                                                  "chuacap": f"không có, chưa cấp {CAPDEOTRAOKC} nên chưa nhận"}[trao])
        s["trao"] = trao

    @staticmethod
    def _is_traocodekc(s):
        # Acc gà tích ô "Acc gà nhập code welcome2d": Cửu Long Thần Hỏa Trảo nhận từ code bị khoá, không give được (người dùng dặn
        # 2026-11-14) => lúc thu hồi không tháo / không trả Trảo, acc chính không chờ Trảo về. Code không mở (admin đóng, "codeloi")
        # thì Trảo là acc chính đưa, vẫn thu hồi như cũ
        return bool(taigiaodienkeocap().get("dungcode")) and not s.get("codeloi")

    def _is_dudeotraokc(self):
        # Đủ cấp đeo Cửu Long Thần Hỏa Trảo chưa (đọc cấp lỗi / ra 0 thì coi như đủ, giữ cách cũ)
        try:
            capdo = int(self.moitruong.get_capdonhanvat() or 0)
        except Exception:
            return True
        return capdo <= 0 or capdo >= CAPDEOTRAOKC

    def _congtiemnangkc(self, s):
        # Acc gà còn điểm tiềm năng chưa cộng thì dồn hết vào Nại lực (ô OTIEMNANGKEOCAP, người dùng dặn): "gift a b c d e" = tổng mới 5 ô
        now = time.time()
        if now - s.get("luctiemnang", 0.) < GIANCACHCONGTIEMNANGKC or self.moitruong.get_is_nhanvatdachet():
            return
        s["luctiemnang"] = now
        moitruong = self.moitruong
        try:
            diem = moitruong.get_diemtiemnangconlai()
            thuoctinhs = moitruong.get_thuoctinhtiemnang()
        except Exception:
            return
        # Chặn số đọc rác (acc gà cấp 100 cũng chỉ ~400 điểm)
        if not diem or diem < 0 or diem > 2000 or not thuoctinhs:
            return
        moi = list(thuoctinhs)
        moi[OTIEMNANGKEOCAP] += diem
        lenh = "gift " + " ".join(map(str, moi))
        if moitruong.action_thucthicaulenh(lenh):
            self._logkc(f"Cộng {diem} điểm tiềm năng vào Nại lực: {thuoctinhs} -> {lenh!r}")

    def _chuyentraokc(self, s, gas):
        # Acc chính: acc gà báo chưa có Cửu Long Thần Hỏa Trảo (trao "") thì tới cạnh give 1 cái trong túi mình, mỗi acc gà tối đa
        # SOLANGIAOTRAOKC lần. -> yêu cầu di chuyển / None khi đang lo đưa, False khi không cần (hết Trảo / acc gà khác bản đồ)
        moitruong = self.moitruong
        now = time.time()
        giao = s["giaotrao"]
        for i, info in gas.items():
            if info["_keocap"].get("trao") == "" and giao.get(i, 0) >= SOLANGIAOTRAOKC and i not in s.setdefault("bogiaotrao", []):
                s["bogiaotrao"].append(i)
                self._logkc(f"⚠️ Give {TRAOKEOCAPs[0]} {SOLANGIAOTRAOKC} lần mà {info.get('tennhanvat') or i} chưa có: thôi, đưa tay giúp")
        cans = [i for i in sorted(gas) if gas[i]["_keocap"].get("trao") == "" and giao.get(i, 0) < SOLANGIAOTRAOKC]
        if not cans or now - s.get("luchettrao", -999.) < 30.:
            return False
        if now - s.get("lucgiaotrao", 0.) < GIANCACHGIAOTRAOKC:
            return None
        trao = self._timvatphamkc(TRAOKEOCAPs)
        if not trao:
            # Không còn trong túi: 30 giây xét lại (người dùng có thể bỏ thêm)
            if not s.get("luchettrao"):
                noidung = f"Hết {TRAOKEOCAPs[0]} trong túi, chưa đưa được cho " + ", ".join(gas[i].get("tennhanvat") or str(i) for i in cans)
                self._logkc("⚠️ " + noidung)
                # Báo cả Telegram (trước chỉ ghi log: 18:35 2026-11-08 thiếu 1 Trảo, gacon4621 kéo cả lượt không có mà không ai biết)
                baosuco(self.moitruong, "vatpham", f"Kéo cấp: {noidung}", khoa = "hettraokc", giancach = 1800.)
            s["luchettrao"] = now
            return False
        idnhan = cans[0]
        tennhan = gas[idnhan].get("tennhanvat") or str(idnhan)
        diachi = moitruong.action_timkiemnhanvat(idnguoichoi = idnhan)
        if not diachi:
            return False
        if moitruong.get_khoangcach(diachi) > KHOANGCACHGIAODOKC:
            s["trangthai"] = f"lại gần {tennhan} để đưa {TRAOKEOCAPs[0]}"
            x, y = moitruong.get_toado(diachi)
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (round(x), round(y), moitruong.get_idbandohientai()), "khoangcachtoida": 1.}
        moitruong.action_ngatdichuyen()
        for lenh in taolenhgiao(str(idnhan), [(trao[1], 1)], 0):
            moitruong.action_thucthicaulenh(lenh)
            self._logkc(f"Đưa {TRAOKEOCAPs[0]} cho {tennhan} (lần {giao.get(idnhan, 0) + 1}): {lenh}")
        giao[idnhan] = giao.get(idnhan, 0) + 1
        s["lucgiaotrao"] = now
        s["trangthai"] = f"đưa {TRAOKEOCAPs[0]} cho {tennhan}"
        return None

    def _buoctanthuga(self, s):
        # Thần Tiên Gia Gia: trả nhiệm vụ, nhận x2 kinh nghiệm 4 giờ, dùng thưởng còn trong túi
        moitruong = self.moitruong
        now = time.time()
        tennpc, x, y = NPCTHANTIENGIAGIA
        buoc = s["tanthu"]
        if buoc in ("nhiemvu", "code", "x2"):
            if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
                return self._ditoikc(s, BANDO_TANTHUTHON, (x, y), "tới Thần Tiên Gia Gia")
            if buoc == "nhiemvu":
                s["trangthai"] = f"tân thủ: {tennpc} trả nhiệm vụ Sứ Mệnh Đưa Thư"
                ketqua, yeucau = self._chonmenukc(s, tennpc, x, y, MENUNHIEMVUTANTHU)
                if ketqua in ("xong", "khongco", "khongmenu"):
                    self._logkc({"xong": "Đã trả nhiệm vụ Sứ Mệnh Đưa Thư", "khongco": "Không có nhiệm vụ Sứ Mệnh Đưa Thư để trả (đã trả?), bỏ qua",
                                 "khongmenu": f"{tennpc} không mở menu, bỏ qua trả nhiệm vụ"}[ketqua])
                    # Ô "nhập code" đọc lúc này (đổi giữa chừng vẫn ăn); acc gà máy khác theo ô trên giao diện máy đó
                    dungcode = bool(taigiaodienkeocap().get("dungcode"))
                    s.update(tanthu = "code" if dungcode else "x2", hoithoai = None, luccho = now + 1.5)
                return yeucau
            self._donghopcodekc()
            if s.get("hoithoai") is None and moitruong.get_is_danghiencuasotuychon():
                # Trả nhiệm vụ / nhập code xong NPC tự bật lại menu: đóng đi rồi look lại cho chắc là menu mới
                moitruong.set_is_danghiencuasotuychon(False)
                moitruong.xoa_noidungcuasotuychon()
            if now < s.get("luccho", 0.):
                return None
            if buoc == "code":
                s["trangthai"] = f"tân thủ: {tennpc} nhập code tân thủ"
                ketqua, yeucau = self._chonmenukc(s, tennpc, x, y, MENUCODETANTHU)
                if ketqua == "xong":
                    moitruong.action_thucthicaulenh(LENHCODETANTHU)
                    # Thưởng code có sẵn 3 Chiến Quốc Lệnh x3 kinh nghiệm (người dùng dặn 2026-11-12): bỏ bước nhận x2 4 giờ
                    self._logkc(f"Nhập code tân thủ ({LENHCODETANTHU!r}), bỏ nhận x2 kinh nghiệm 4 giờ (đã có Chiến Quốc Lệnh x3)")
                    s.update(tanthu = "vatpham", hoithoai = None, luccho = now + 2., lucguicode = now)
                elif ketqua in ("khongco", "khongmenu"):
                    self._logkc(f"{tennpc} không có lựa chọn Nhập Code Tân Thủ ({ketqua}, admin đóng code?), bỏ qua")
                    s.update(tanthu = "x2", hoithoai = None, luccho = now + 1., codeloi = True)
                return yeucau
            s["trangthai"] = f"tân thủ: {tennpc} nhận x2 kinh nghiệm 4 giờ"
            ketqua, yeucau = self._chonmenukc(s, tennpc, x, y, MENUX2KINHNGHIEM)
            if ketqua == "xong":
                self._logkc("Đã nhận x2 kinh nghiệm 4 giờ")
                s.update(tanthu = "vatpham", hoithoai = None, luccho = now + 2.)
            elif ketqua in ("khongco", "khongmenu"):
                self._logkc(f"{tennpc} không có lựa chọn Nhận thời gian x2 kinh nghiệm / 4 giờ ({ketqua}), bỏ qua")
                s.update(tanthu = "vatpham", hoithoai = None)
            return yeucau
        if now < s.get("luccho", 0.):
            return None
        if buoc == "vatpham":
            self._donghopcodekc()
            dalam = s.setdefault("dungvatpham", {})
            if not dalam and now - s.get("lucguicode", -999.) < THOIGIANCHOTHUONGCODE and (moitruong.get_capdonhanvat() or 0) < 8 \
                    and not any(self._timvatphamkc(tens) for tens in (*(t for t, _ in VATPHAMTANTHUs), (CHIENQUOCLENHX3,))):
                s["trangthai"] = "tân thủ: chờ nhận thưởng code"
                return None
            for tens, cach in VATPHAMTANTHUs:
                if tens[0] == TRAOKEOCAPs[0] and not self._is_dudeotraokc():
                    # Chưa đủ cấp đeo: để trong túi, qua tân thủ _dungvatphamconsotkc đeo khi lên cấp
                    continue
                mon = self._timvatphamkc(tens)
                if not mon or dalam.get(tens[0], 0) >= SOLANDUNGVATPHAMTANTHU:
                    continue
                if now - s.get("lucdung", 0.) < GIANCACHDUNGVATPHAMKC:
                    return None
                if not self._dungvatphamtanthukc(s, tens[0], cach, mon, dalam.get(tens[0], 0) + 1):
                    continue
                dalam[tens[0]] = dalam.get(tens[0], 0) + 1
                s["lucdung"] = now
                s["trangthai"] = f"tân thủ: dùng {tens[0]}"
                return None
            s["tanthu"] = "chienquoclenh"
            return None
        if buoc == "chienquoclenh":
            mon = self._timvatphamkc((CHIENQUOCLENHX3,))
            solan = s.get("solancql", 0)
            if mon and solan < SOLANDUNGCHIENQUOCLENH:
                if now - s.get("lucdung", 0.) < GIANCACHDUNGVATPHAMKC:
                    return None
                # "use" chỉ mở hộp hỏi đồng ý, "use !" mới thật sự dùng (người dùng xác nhận)
                s.update(solancql = solan + 1, lucdung = now)
                s["trangthai"] = f"tân thủ: dùng {CHIENQUOCLENHX3}"
                self._logkc(f"Dùng {CHIENQUOCLENHX3} (use !, lần {solan + 1})")
                moitruong.action_sudungvatpham(mon[1], is_boquaxacnhan = True, delay = 0.)
                return None
            s.update(tanthu = "xong", xongtanthu = True, giaidoan = "taphop")
            self._logkc(f"Xong thưởng tân thủ (cấp {moitruong.get_capdonhanvat()}), về tập hợp")
            phatam("Acc gà xong tân thủ")
        return None

    def _kiemtrax2kc(self, s):
        # Acc gà cấp >= CAPKIEMTRAX2KC: hết "Thời Gian Nhân Đôi / Ba" thì về Thần Tiên Gia Gia nhận x2 4 giờ (làm 1 lần lúc bật).
        # s["x2"]: None / "kiemtra" / "nhan" / "xong". -> False khi không cần / đã xong, còn lại là yêu cầu di chuyển / None
        moitruong = self.moitruong
        now = time.time()
        buoc = s.get("x2")
        if buoc == "xong" or self._is_trongphongyeu():
            return False
        if buoc is None:
            capdo = moitruong.get_capdonhanvat()
            if capdo is None or capdo is False:
                return False
            if capdo < CAPKIEMTRAX2KC:
                s["x2"] = "xong"
                return False
            s.update(x2 = "kiemtra", lucx2 = now, solanx2 = 0)
            moitruong.action_thucthicaulenh("quest list")
            s["trangthai"] = "kiểm tra còn thời gian x2 / x3 kinh nghiệm"
            return None
        if buoc == "kiemtra":
            mucs = moitruong.get_danhsachmucnhiemvu()
            con = [ten.strip() for ten, _ in (mucs or ()) if TENTHOIGIANNHANKC in ten]
            if con:
                self._logkc(f"Còn {', '.join(con)}: không cần nhận x2 kinh nghiệm")
                s["x2"] = "xong"
                return False
            if now - s["lucx2"] < THOIGIANCHOX2KC:
                return None
            if mucs is None and s["solanx2"] < 2:
                s.update(lucx2 = now, solanx2 = s["solanx2"] + 1)
                moitruong.action_thucthicaulenh("quest list")
                return None
            self._logkc(f"Không còn Thời Gian Nhân Đôi / Ba{' (không đọc được cửa sổ nhiệm vụ)' if mucs is None else ''}: "
                        f"về {NPCTHANTIENGIAGIA[0]} nhận x2 kinh nghiệm 4 giờ")
            s.update(x2 = "nhan", lucnhanx2 = now, hoithoai = None)
            return None
        if now - s["lucnhanx2"] > THOIGIANNHANX2KC:
            self._logkc(f"⚠️ Quá {int(THOIGIANNHANX2KC)}s chưa nhận được x2 kinh nghiệm: bỏ qua")
            s["x2"] = "xong"
            return False
        if self._is_dangban():
            return None
        tennpc, x, y = NPCTHANTIENGIAGIA
        if moitruong.get_idbandohientai() != BANDO_TANTHUTHON:
            return self._ditoikc(s, BANDO_TANTHUTHON, (x, y), "tới Thần Tiên Gia Gia nhận x2 kinh nghiệm 4 giờ")
        s["trangthai"] = f"{tennpc}: nhận x2 kinh nghiệm 4 giờ"
        ketqua, yeucau = self._chonmenukc(s, tennpc, x, y, MENUX2KINHNGHIEM)
        if ketqua == "xong":
            self._logkc("Đã nhận x2 kinh nghiệm 4 giờ")
            s["x2"] = "xong"
        elif ketqua in ("khongco", "khongmenu"):
            self._logkc(f"⚠️ {tennpc} không có lựa chọn Nhận thời gian x2 kinh nghiệm ({ketqua}): bỏ qua")
            s["x2"] = "xong"
        return yeucau

    def _donghopcodekc(self):
        # welcome.13747 mở hộp "Xin nhập mã Code Tân Thủ" (cửa sổ mã xác nhận), lệnh codett không tự đóng: tắt cờ mở như bấm Hủy Bỏ
        moitruong = self.moitruong
        if moitruong.get_is_dangmocuasoxacnhan() and "Code Tân Thủ" in moitruong.get_noidungcuasomaxacnhan():
            moitruong.set_is_dangmocuasoxacnhan(False)
            self._logkc("Đóng hộp nhập mã Code Tân Thủ")

    def _xacnhansuphuga(self, s, chinh):
        # Mình là đồ đệ acc chính chọn: Mạnh Tử hỏi "Bạn bằng lòng làm đồ đệ của <acc chính> không ?" (hoặc hỏi xuất sư) thì chọn lựa chọn
        # đầu "1. Xác nhận" (tallk 17e5# welcome.13), báo dabaisu / daxuatsu cho acc chính
        moitruong = self.moitruong
        if chinh["_keocap"].get("iddode") != moitruong.get_idnguoichoi() or time.time() - s.get("lucxacnhansp", 0.) < 2.:
            return
        # Aegis "Mạnh Tử:\n Bạn bằng lòng làm đồ đệ của <acc chính> không ?" -> "1. Xác nhận"; Niết Bàn có dấu cách đầu
        # " Mạnh Tử :\n Ngươi chấp nhận làm đồ đệ của <acc chính> ?" -> "1.Chấp nhận" / "2.Rời khỏi" (vẫn lựa chọn đầu)
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung.strip().startswith(NPCMANHTU[0]):
            return
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        if not lenhs:
            return
        # chinh có thể là acc chính 2 (acc phụ): nó báo việc đang làm ở "suphudang"
        suphudang = chinh["_keocap"].get("suphudang")
        co = "daxuatsu" if (suphudang or chinh["_keocap"].get("giaidoan")) == "xuatsu" else "dabaisu"
        s["lucxacnhansp"] = time.time()
        self._logkc(f"Mạnh Tử: {noidung[:80]!r} -> chọn {lenhs[0]!r} ({'xuất sư' if co == 'daxuatsu' else 'bái sư'})")
        moitruong.xoa_noidungcuasotuychon()
        moitruong.action_thucthicaulenh(lenhs[0])
        s[co] = True

    def _dungvatphamconsotkc(self, s):
        # Đã qua tân thủ mà thưởng code (Hoàng Sa Chi Tâm, Cửu Long Thần Hỏa Trảo) còn trong túi (bản cũ dùng "use !", không ăn) / Thủy
        # Bình chưa ở ô mở cuối: dùng lại đúng cách, mỗi món tối đa SOLANDUNGVATPHAMTANTHU lần, GIANCACHDOCVATPHAMSOTKC giây đọc túi 1 lần
        now = time.time()
        if now - s.get("lucdocsot", 0.) < GIANCACHDOCVATPHAMSOTKC or self._is_dangban() or self.get_is_danghoithoainpc():
            return
        s["lucdocsot"] = now
        dalam = s.setdefault("dungvatphamsot", {})
        for tens, cach in VATPHAMTANTHUs:
            if tens[0] == TRAOKEOCAPs[0] and (s.get("giaidoan") in ("thuhoi", "xong") or not self._is_dudeotraokc()):
                # Thu hồi: Trảo vừa tháo ra để trả acc chính, đừng đeo lại; chưa đủ cấp đeo thì chờ lên cấp
                continue
            mon = self._timvatphamkc(tens)
            if mon and dalam.get(tens[0], 0) < SOLANDUNGVATPHAMTANTHU \
                    and self._dungvatphamtanthukc(s, tens[0], cach, mon, dalam.get(tens[0], 0) + 1, "còn trong túi: "):
                dalam[tens[0]] = dalam.get(tens[0], 0) + 1
                return

    def _dungvatphamtanthukc(self, s, ten, cach, mon, solan, tiento = ""):
        # Dùng món thưởng code tân thủ mon (ô, id) theo cách trong VATPHAMTANTHUs, solan: lần thứ mấy (từ 1).
        # -> True nếu đã gửi lệnh, False nếu không cần (bảo thú đã ở ô mở cuối)
        moitruong = self.moitruong
        vitri, idvatpham = mon
        if cach == "baothu":
            # Phần tự triệu hồi (action_tudongsudungvatpham) chỉ gọi bảo thú vật phẩm ở ô mở cuối cùng, cần bật Tự động sử dụng vật phẩm
            self._datkc(s, "_is_tudongsudungvatpham", True, "Tự động sử dụng vật phẩm")
            ocuoi = moitruong.get_vitriomocuoihanhtrang()
            tencuoi = moitruong.get_tenvatphamhanhtrang(ocuoi)
            if vitri == ocuoi or (tencuoi in BAOTHUVATPHAMs and tencuoi not in THUYBINHs):
                return False
            if ocuoi // SOLUONGOMOITUI == vitri // SOLUONGOMOITUI:
                moitruong.action_dichuyenvatphamhanhtrang(idvatpham, ocuoi + 1, delay = 0.)
            else:
                # Khác túi: "to túi" vào ô trống đầu túi đó, lượt sau chuyển trong túi
                moitruong.action_dichuyenvatphamsanghanhtrangkhac(idvatpham, ocuoi // SOLUONGOMOITUI + 1, delay = 0.)
            self._logkc(f"{ten} {tiento}chuyển vào ô mở cuối ({ocuoi + 1}) cho tự triệu hồi bảo thú (lần {solan})")
            return True
        moitruong.action_sudungvatpham(idvatpham, delay = 0., is_use2 = True)
        self._logkc(f"{ten} {tiento}dùng (use2, lần {solan})")
        return True

    def _timcacvatphamkc(self, tens):
        # Mọi (ô, id) món trong túi có tên đúng là 1 trong tens. Tên ô tối đa 31 byte: chỉ tên đã bị cắt (đủ SOBYTETENBICAT byte) mới
        # so đầu tên, còn lại phải trùng hẳn (không thì "Chiến Quốc Lệnh" khớp nhầm "Chiến Quốc Lệnh x3")
        tens = [_chuanhoa(t) for t in tens]
        ketquas = []
        for ten, mons in self.moitruong.get_danhsachvatphamhanhtrang_map().items():
            ten = _chuanhoa(ten)
            is_bicat = len(ten.encode("utf-8")) >= SOBYTETENBICAT
            if not ten or not any(t == ten or (is_bicat and t.startswith(ten)) for t in tens):
                continue
            ketquas.extend((vitri, iddoituong) for vitri, iddoituong in mons if iddoituong and vitri < VITRITRANGBIDAUTIEN)
        return ketquas

    def _timvatphamkc(self, tens):
        # (ô, id) món đầu tiên trong túi có tên là 1 trong tens, không có thì None
        mons = self._timcacvatphamkc(tens)
        return mons[0] if mons else None

    def _chonmenukc(self, s, tennpc, x, y, duois):
        # Tới cạnh NPC, "look", chọn lần lượt lựa chọn có lệnh kết thúc bằng từng đuôi trong duois (mỗi đuôi 1 menu).
        # -> ("xong" | "khongco" (menu không có lựa chọn đó) | "khongmenu" | None, yêu cầu di chuyển)
        moitruong = self.moitruong
        now = time.time()
        idbando = moitruong.get_idbandohientai()
        diachinpc = moitruong.action_timkiemnhanvat(tennhanvat = tennpc)
        h = s["hoithoai"]
        if not h or h["npc"] != tennpc:
            h = s["hoithoai"] = {"npc": tennpc, "buoc": "look", "luc": 0., "cap": 0, "solan": 0}
        if not diachinpc or moitruong.get_khoangcach(diachinpc) > KHOANGCACHNOICHUYENKC:
            h.update(buoc = "look", cap = 0)
            xdich, ydich = moitruong.get_toado(diachinpc) if diachinpc else (x, y)
            return None, {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (xdich, ydich, idbando), "khoangcachtoida": 1.}
        if h["buoc"] == "look":
            if now - h["luc"] < 1.:
                return None, None
            idnpc = moitruong.get_iddoituong(diachinpc)
            if not idnpc:
                return None, None
            moitruong.action_ngatdichuyen()
            moitruong.xoa_noidungcuasotuychon()
            moitruong.action_thucthicaulenh(f"look {idnpc:x}#")
            h.update(buoc = "menu", luc = now, cap = 0)
            return None, None
        noidung = moitruong.get_noidungcuasotuychon()
        if not noidung:
            if now - h["luc"] > THOIGIANCHOMENUKC:
                h.update(buoc = "look", solan = h["solan"] + 1, luc = now)
                if h["solan"] >= SOLANTHUMENUKC:
                    s["hoithoai"] = None
                    return "khongmenu", None
            return None, None
        lenhs = [l for l in moitruong.get_lenhcuasotuychons() if l.strip() and l.upper() != "CLOSE"]
        self._logkc(f"Menu {tennpc}: {noidung[:80]!r} {lenhs}")
        duoi = duois[h["cap"]]
        if isinstance(duoi, int):
            # Số: chọn theo thứ tự lựa chọn (0 = lựa chọn 1), dùng khi chưa biết đuôi lệnh
            lenh = lenhs[duoi] if duoi < len(lenhs) else None
        elif isinstance(duoi, tuple):
            # (đuôi dự phòng, chữ trong nhãn): chọn lựa chọn có nhãn chứa chữ đó; không đọc được nhãn nào thì theo đuôi lệnh
            duoiduphong, chu = duoi
            capdu = [(l, n) for l, n in zip(moitruong.get_lenhcuasotuychons(), moitruong.get_nhanluachoncuasotuychons())
                     if l.strip() and l.upper() != "CLOSE"]
            self._logkc(f"Nhãn menu {tennpc}: {[n for _, n in capdu]}")
            if any(n.strip() for _, n in capdu):
                lenh = next((l for l, n in capdu if _chuanhoa(chu).lower() in _chuanhoa(n).lower()), None)
            else:
                lenh = next((l for l in lenhs if l.split()[-1] == duoiduphong), None)
        else:
            lenh = next((l for l in lenhs if l.split()[-1] == duoi), None)
        if not lenh:
            if moitruong.get_is_danghiencuasotuychon():
                moitruong.set_is_danghiencuasotuychon(False)
            s["hoithoai"] = None
            return "khongco", None
        moitruong.action_ngatdichuyen()
        moitruong.xoa_noidungcuasotuychon()
        moitruong.action_thucthicaulenh(lenh)
        self._logkc(f"{tennpc}: chọn {lenh!r}")
        if h["cap"] + 1 < len(duois):
            h.update(cap = h["cap"] + 1, luc = now)
            return None, None
        s["hoithoai"] = None
        return "xong", None

    # --- Phong Yêu Kính (gọi từ tactu_langlyson_xq) -----------------------------------------------------------------------------------
    def _is_donguocphongyeukeocap(self):
        # Acc phụ dò Phong Yêu Kính ngược chiều acc chính (_dophongyeu)
        return bool(self._keocap) and self._keocap["vaitro"] == "phu"

    def _is_khongdanhbosspykc(self):
        # Đang kéo cấp trong Phong Yêu Kính mà acc chính hơn người give quá CHENHLECHCAPKHONGDANHBOSSKC cấp: không đánh boss (như "85quai").
        # Cấp lấy từ shared_data (_keocap "capdo"); chưa đọc được cấp ai thì coi như không chênh (đánh boss như cấu hình)
        s = self._keocap
        if not s or s["giaidoan"] != "phongyeu" or not s["idgive"]:
            return False
        idtoi = self.moitruong.get_idnguoichoi()
        cuasos = self._laycuasokeocap()

        def capcua(idnguoichoi):
            if idnguoichoi == idtoi:
                return self.moitruong.get_capdonhanvat() or 0
            info = cuasos.get(idnguoichoi)
            return (info["_keocap"].get("capdo") or 0) if info else 0

        capchinh = capcua(idtoi if s["vaitro"] == "chinh" else s["idchinh"])
        capgive = capcua(s["idgive"])
        if not capchinh or not capgive:
            return False
        is_khongdanh = capchinh - capgive > CHENHLECHCAPKHONGDANHBOSSKC
        if is_khongdanh != s.get("khongdanhbosspy"):
            s["khongdanhbosspy"] = is_khongdanh
            self._logkc(f"Phong Yêu Kính: acc chính cấp {capchinh}, người give cấp {capgive} (chênh {capchinh - capgive}): "
                        + ("không đánh boss, đủ 85% quái là ra" if is_khongdanh else "đánh boss theo Điều kiện thoát"))
        return is_khongdanh

    def _laynhompykeocap(self):
        # Đang kéo cấp: (ID người give = acc gà acc chính chọn, [ID người khác: acc chính + acc gà online]) thay cho nhóm todoi, không thì None
        s = self._keocap
        if not s or s["giaidoan"] != "phongyeu" or not s["idgive"]:
            return None
        idtoi = self.moitruong.get_idnguoichoi()
        cuasos = self._laycuasokeocap()
        if s["vaitro"] == "chinh":
            nhom = s.get("nhompy") or []
        else:
            chinh = cuasos.get(s["idchinh"])
            if not chinh:
                return None
            nhom = chinh["_keocap"].get("nhompy") or []
        # Acc chính đứng đầu, rồi acc gà, acc phụ; chỉ tính người online (cửa sổ cùng máy / máy khác nối LAN còn cập nhật)
        ids = [i for i in nhom if i in cuasos or i == idtoi]
        if s["idgive"] not in ids:
            return None
        return s["idgive"], [i for i in ids if i != s["idgive"]]

    def _buoctrongphongyeukeocap(self, s, py, idbando, is_thanhvien):
        # Trong Phong Yêu Kính khi kéo cấp, acc gà tắt "Tự động sử dụng kỹ năng" không đi đâu: đứng cạnh Thỏ Yêu (đứng đâu cũng có kinh
        # nghiệm), không đánh; bật thì dò đánh như thường. Người give ra (vòng mới) khi đã diệt boss và hết quái; bản đồ Tây Thành thì
        # _buoctrongphongyeu ra ngay. -> yêu cầu di chuyển / None, False khi để Phong Yêu Kính làm như cũ (không phải acc gà, acc gà đánh quái)
        kc = self._keocap
        if not kc or kc["vaitro"] != "ga":
            return False
        now = time.time()
        tenpb = self._tenpb(s)
        # Bật "Tự động sử dụng kỹ năng" (người dùng dặn 2026-11-04): không đứng ở Thỏ Yêu, dò lộ trình đánh quái như thành viên thường
        # (người give thì như trưởng nhóm), chỉ thêm điều kiện ra sớm của kéo cấp
        # Bật "Chỉ đánh người chơi" cũng như tắt kỹ năng: đứng Thỏ Yêu (_lydodungthoyeupy, người dùng dặn 2026-11-23)
        is_danhquai = not self._lydodungthoyeupy()
        if is_thanhvien:
            if is_danhquai:
                return False
            py["hoisoquai"] = None
            s["chedo"] = "cho"
            s["trangthai"] = f"{tenpb}: acc gà đứng ở Thỏ Yêu hưởng kinh nghiệm"
            return self._dungthoyeukc(s, py, idbando)
        # Người give: ra theo "Điều kiện thoát" trong cấu hình Phong Yêu Kính (tienich_xq.DIEUKIENRAPYKEOCAPs, mặc định đủ 2 boss là ra
        # ngay): đã diệt đủ số boss (mình hay người cùng nhóm giết, _congbossnguoikhac) hoặc game báo hoàn thành, không xét số
        # quái Thỏ Yêu; kiểu chờ hết quái thì chờ tới khi không thành viên nào còn mục tiêu mới ra. Boss đếm chỉ tin sau
        # THOIGIANTOITHIEUPY giây (vừa vào thì có thể là số boss vòng cũ)
        sobossra, is_chohetquai = laydieukienrapykeocap(taicauhinhphongyeu(is_keoga = True))
        comuctieus = self._thanhviencomuctieupykc(py)
        if is_danhquai and self.moitruong.get_iddoituongmuctieudangchon():
            comuctieus.insert(0, "mình")
            py["luccomuctieu"] = now
        is_quagio = now - py["lucvao"] >= THOIGIANTOIDAPY
        is_hetmuctieu = not is_chohetquai or (not comuctieus and now - py.get("luccomuctieu", 0.) >= THOIGIANHETMUCTIEUPYKC)
        if not is_hetmuctieu and is_quagio:
            is_hetmuctieu = True
            if not py.get("dalogquagiomuctieu"):
                py["dalogquagiomuctieu"] = True
                self._logpb(s, f"Ở quá {THOIGIANTOIDAPY / 60:.0f} phút: không chờ thành viên hết mục tiêu nữa")
        is_duboss = s["daxongphoban"] or (len(py["bossdagiet"]) >= sobossra and now - py["lucvao"] >= THOIGIANTOITHIEUPY)
        is_raquagio = not is_danhquai and not is_duboss and is_quagio and not self._nguoikhacdanhbosspy() and not comuctieus
        if (is_duboss and is_hetmuctieu) or is_raquagio:
            # Đủ điều kiện ra: chờ nhặt xong đồ rơi đã (đứng tại chỗ, không kéo về Thỏ Yêu cho việc nhặt đồ khỏi bị giành)
            if self._chonhatdoroipy(s):
                s["trangthai"] = f"{tenpb}: đủ điều kiện ra ({len(py['bossdagiet'])}/{sobossra} boss), chờ nhặt đồ"
                return None
        else:
            s.pop("lucxongboss", None)
        if is_duboss and is_hetmuctieu:
            self._logpb(s, f"Đã diệt {len(py['bossdagiet'])}/{sobossra} boss" + (", hết quái" if is_chohetquai else "") + ": ra mở vòng mới")
            s.update(giaidoan = "nhanthuong", hoithoai = None)
            return None
        if is_raquagio:
            # Acc gà đứng ở Thỏ Yêu không tự dò: ở quá THOIGIANTOIDAPY mà chưa đủ boss, không ai đánh boss / còn mục tiêu (boss sau không
            # ra) thì thôi, ra mở vòng mới cho khỏi kẹt (người đánh quái thì _buoctrongphongyeu tự ra theo lượt dò)
            self._logpb(s, f"Ở quá {THOIGIANTOIDAPY / 60:.0f} phút mới diệt {len(py['bossdagiet'])}/{sobossra} boss, "
                           "không ai còn đánh: ra mở vòng mới")
            s.update(giaidoan = "nhanthuong", hoithoai = None)
            return None
        if is_danhquai:
            # Để _buoctrongphongyeu dò đánh như trưởng nhóm (đủ boss / hết lượt dò thì nó cũng tự ra)
            return False
        # Điều kiện thoát "85quai": đứng cạnh Thỏ Yêu thì hỏi số quái định kỳ (đủ thì _buoctrongphongyeu ra)
        dangdung, yeucau = self._hoi85quaipy(s, py)
        if dangdung:
            return yeucau
        py["hoisoquai"] = None
        s["chedo"] = "cho"
        if is_duboss:
            s["trangthai"] = f"{tenpb}: đã diệt {len(py['bossdagiet'])} boss, chờ hết quái " \
                             f"({', '.join(comuctieus) if comuctieus else 'vừa hết mục tiêu'} đang đánh)"
        else:
            s["trangthai"] = f"{tenpb}: acc gà đứng ở Thỏ Yêu chờ diệt boss (boss {len(py['bossdagiet'])}/{sobossra})"
        return self._dungthoyeukc(s, py, idbando)

    def _dungthoyeukc(self, s, py, idbando):
        x, y = self._vitrithoyeu(s, py, idbando)
        if self.moitruong.get_khoangcachdiem(x, y) > KHOANGCACHNOICHUYENKC:
            return {"yeucau": YEUCAUDICHUYENDICHUYENTUDO, "toadodich": (x, y, idbando), "khoangcachtoida": 1.}
        return None

    def _thanhviencomuctieupykc(self, py):
        # Tên thành viên nhóm Phong Yêu Kính (cùng máy / LAN, cùng bản đồ) đang có mục tiêu trong game; có người thì nhớ lúc đó vào
        # py["luccomuctieu"] (giữa 2 con quái mục tiêu về 0 một lúc, chờ THOIGIANHETMUCTIEUPYKC giây mới coi là hết quái)
        tens = []
        for idtv in self._laynhompy()[1]:
            info = self._laythongtinnguoichoi(idtv)
            if info and info.get("iddoituongmuctieu") and self.moitruong.get_is_cungbando(info):
                tens.append(info.get("tennhanvat") or f"ID {idtv}")
        if tens:
            py["luccomuctieu"] = time.time()
        return tens
