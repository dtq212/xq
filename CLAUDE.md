# Bot game xq (Python 3.8, Windows)

Bot tự động cho client game `xq.exe` (bản Aegis và Niết Bàn, cùng mã exe). Đọc/ghi bộ nhớ tiến trình
bằng Pymem, gửi lệnh game qua hook, giao diện Tkinter.
**Luôn trả lời bằng tiếng Việt** (cả recap, ghi chú, và sau khi ngữ cảnh bị tóm tắt).

## Chạy
- `chaybot.bat` → `python -X utf8 trochoi_xq.py` (Python 3.8: không dùng `match`, `list[int]`, `X | None`).
- Không có test tự động; người dùng test trong game rồi báo lại kết quả và log.

## Kiến trúc
- `trochoi_xq.py`: `TroChoiManager` dò các cửa sổ game, mỗi cửa sổ chạy một tiến trình bot (`cuaso_xq.CuaSo`);
  dữ liệu chung qua `multiprocessing.Manager` (`shared_data`, `command_dict`).
- `cuaso_xq.py`: dựng `MoiTruong` + `TacTu` cho một cửa sổ, chạy các vòng lặp trong `loop_xq.py`
  (`LoopChinh`, `LoopPhu`, `LoopTimKiemMucTieu`, `LoopDieuPhoiDiChuyen`, `LoopXuLyLenh`...).
- `moitruong_xq.py` (`MoiTruong`, ~4.800 dòng): tầng đọc/ghi game. `get_*` đọc trạng thái,
  `action_*` gửi lệnh/thao tác, `auto_assemble_*` chèn mã. Offset bộ nhớ ghi chú ngay trên hằng số.
- `tactu_xq.py` (`TacTu`): bộ não ra quyết định, ghép từ các mixin `tactu_*_xq.py`.
  **Mixin chỉ chứa hàm; mọi trạng thái `self._...` khởi tạo trong `TacTu.__init__`.**
- `giaodienhienthi_xq.py` (`GiaoDienHienThi`, ~4.600 dòng): bảng điều khiển Tk; `chude_xq.py` là theme.
- `diachi_xq.py`: địa chỉ trong xq.exe tìm bằng chữ ký (cache `_internal/diachi_cache.json`);
  thêm địa chỉ mới thì sinh chữ ký bằng `taochuky_xq.py`. Không ghi cứng địa chỉ tuyệt đối.
- `hangso_xq.py`: hằng số game (NPC, toạ độ, bản đồ, kỹ năng theo môn phái, bảng hàng).
- `tienich_xq.py`: hàm dùng chung (`read_*`/`write_*` bộ nhớ, `phatam`, `canhbao`, lộ trình, vật cản học).

## Bản đồ file `tactu_*` (mixin)
| File | Việc |
|---|---|
| dichuyen | giữ khoảng cách, theo sau, đi tới bản đồ/phù, tìm đường, vật cản |
| muctieu | lọc/chọn mục tiêu, tầm nhìn chia sẻ, ép đá |
| kynang | ưu tiên chiêu, từng môn phái, tâm pháp, Đào Hoa |
| tuhockynang | chế độ kỹ năng Tự học (học từ số bay, lập chuỗi chiêu) |
| vatpham | thuốc, nhặt, vứt, mua, sửa, sắp xếp hành trang |
| hoatdong | hội thoại NPC, tạm ngưng khi thấy người lạ, tổ đội |
| baothu | bảo thú |
| catkho / giaodo | cất kho, giao tiền/đồ ở Tân Thủ Thôn |
| sumon / danhvong / sugia | nhiệm vụ sư môn / Danh Vọng / Sư Gia |
| langlyson / tapkich / matac | phó bản Lăng Ly Sơn + Thành Kiều / Tập Kích / Mã Tặc |
| doiphoban / hangviec / keocap | đội phó bản, hàng việc cá nhân, kéo cấp acc gà |

## File phụ trợ khác
`bando_xq` cổng bản đồ (jmp.dat) · `nhiemvu_xq` đọc/phân loại nhiệm vụ · `luattuido_xq` luật túi đồ ·
`dangnhap_xq` tự đăng nhập lại · `giamsat_xq` watchdog kẹt · `dieuphoi_xq` chia lượt giữa các cửa sổ ·
`lan_xq` chia sẻ dữ liệu qua LAN · `thongbao_xq` Telegram · `thongke_xq` thống kê farm ·
`dexuatlotrinh_xq` đề xuất điểm đánh · `amthanh_xq` tắt tiếng theo tiến trình · `bannganluong_xq` bán ngân lượng ·
`dosatthuong_xq`/`phantichsatthuong_xq` công cụ đo sát thương (chạy tay) · `congthucsatthuong_xq` công thức sát thương đo được ·
`sosanhbuild_xq` (so build, mặc thử đồ) / `domuctieu_xq` (dự đoán máu tối đa, Kháng mục tiêu): chạy từ tab Khác ·
`uocluongmuctieu_xq` luồng trong bot ước Khí Huyết tối đa / Kháng mục tiêu đang chọn, hiện ở tab Chiến đấu, dưới nhóm Tầm đánh.

## Dữ liệu `_internal/`
Cấu hình JSON (`giaodien.json`, `luattuido.json`, `lotrinh.json`, `todoi.json`, `taikhoan_*.json`...),
log theo ID người chơi ở `_internal/log/<id>.log`. Mọi thứ theo nhân vật khoá bằng **ID**, không theo tên.

## Quy ước
- Tên biến/hàm tiếng Việt không dấu viết liền (`get_sinhlucconlai`, `action_sudungkynang`); bool bắt đầu `is_`.
- Chú thích tiếng Việt có dấu, đặt trên hằng số/hàm, ghi cả lý do và số đo thực tế.
- Trước khi viết heuristic mới, grep hàm hạ tầng có sẵn (`get_`/`_tim`/`_doc` trong `moitruong_xq.py`):
  A* `_timduongkhongcatgoc` / `get_sobuocduongtoi`, `_get_luoivatcan`, `vatcanhoc.json`, `action_dikhongcatgoc`...
- File mới tạo phải `git add` ngay, không commit/push trừ khi được bảo. Repo lỗi "dubious ownership":
  `git -c safe.directory=* add -- <file>`. Không add file chứa mật khẩu mới khi chưa hỏi, không add file trạng thái
  bot ghi liên tục (vd `_internal/tiendophoban.json`, đã .gitignore); gặp loại này thì hỏi.

## Mẹo đọc code (tiết kiệm token)
- `moitruong_xq.py`, `giaodienhienthi_xq.py`, `tactu_kynang_xq.py`, `tactu_langlyson_xq.py`, `tactu_dichuyen_xq.py`
  rất lớn: **grep tên hàm/hằng số rồi đọc theo `offset`/`limit`**, không đọc cả file.
- Log: grep theo từ khoá/thời điểm, không đọc cả file log.
