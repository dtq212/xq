# Tự đề xuất lộ trình điểm đánh từ vị trí quái đã thấy:
#   1. Khi bot chạy, mỗi THOIGIANGHIVITRIQUAI giây cộng 1 vào ô lưới (cạnh OVITRIQUAI) chứa mỗi quái đang thấy (quái đứng lâu / ra nhiều
#      chỗ nào thì ô đó nhiều điểm). Lưu theo ID người chơi: _internal/viquai/<id>.json = {"<id bản đồ>": {"gx,gy": số lần}}
#   2. Gom cụm: lấy ô có mật độ quanh nó cao nhất, điểm đánh = tâm có trọng số của các ô quanh đó, bỏ các ô trong bán kính điểm đánh rồi lặp
#   3. Nối thành vòng ngắn (láng giềng gần nhất + 2-opt), kiểm tra từng đoạn đi được bằng hàm tìm đường cục bộ của client và đường đi
#      không lọt vào vùng cấm; đoạn nào hỏng thì bỏ điểm ít quái hơn của đoạn đó rồi nối lại
# Hàm tìm đường của client chỉ dùng được cho bản đồ đang đứng nên chỉ đề xuất cho bản đồ hiện tại
import itertools
import json
import math
import os
import sys

OVITRIQUAI = 2
THOIGIANGHIVITRIQUAI = 2.
THOIGIANLUUVITRIQUAI = 60.
# Ít hơn số lần thấy quái này trên bản đồ thì chưa đủ dữ liệu để đề xuất
SOLANTHAYQUAITOITHIEU = 50
SODIEMDEXUATTOIDA = 8
# Các điểm đề xuất cách nhau ít nhất chừng này ô (một tầm màn hình). Không dùng bán kính điểm đánh của nhân vật: đó là bộ lọc mục tiêu,
# có thể đặt 999 (không giới hạn) làm cả bản đồ gộp thành 1 điểm
KHOANGCACHDIEMDEXUAT = 18.
# Cụm có mật độ dưới tỷ lệ này so với cụm đông nhất thì bỏ (vài con lẻ tẻ)
TYLECUMTOITHIEU = 0.15
TENMAUDEXUAT = "Tự đề xuất"
# Hàm tìm đường cục bộ của client trả mỗi lần chừng 50 bước (đo ở Khốn Ma Trận 1): đoạn xa hơn thì đi tiếp từ chỗ dừng / chia đôi,
# tối đa chừng này lần
SOLANCHIADOANTOIDA = 10
# Đích rơi vào ô vật cản (tâm cụm quái là trung bình vị trí quái, hay trúng đá / cây) thì game tìm đường tới ô đi được gần nhất:
# dừng cách đích không quá chừng này ô vẫn coi là tới (nhân vật đánh trong bán kính điểm đánh)
SAISODIEMDEN = 3.

# Chuỗi hướng của hàm tìm đường cục bộ: ký tự -> (dx, dy) (xem MoiTruong._get_chuoihuongtimduongcucbo)
HUONGTIMDUONG_MAP = {"1": (1, 0), "2": (1, -1), "3": (0, -1), "4": (-1, -1), "5": (-1, 0), "6": (-1, 1), "7": (0, 1), "8": (1, 1)}


def _thumucviquai():
    thumucgoc = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thumucgoc, "_internal", "viquai")


def taiviquai(idnguoichoi):
    try:
        with open(os.path.join(_thumucviquai(), f"{idnguoichoi}.json"), "r", encoding = "utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as err:
        print(err)
        return {}


def luuviquai(idnguoichoi, bangviquai):
    from tienich_xq import thaythefile
    filepath = os.path.join(_thumucviquai(), f"{idnguoichoi}.json")
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok = True)
        filetam = filepath + ".tmp"
        with open(filetam, "w", encoding = "utf-8") as file:
            json.dump(bangviquai, file, separators = (",", ":"))
        thaythefile(filetam, filepath)
    except Exception as err:
        print(err)


def taiviquaibando(idbando):
    # Gộp vị trí quái của mọi nhân vật đã ghi trên bản đồ: {(gx, gy): số lần}
    tong = {}
    try:
        tenfiles = os.listdir(_thumucviquai())
    except FileNotFoundError:
        return tong
    for tenfile in tenfiles:
        if not tenfile.endswith(".json"):
            continue
        for khoa, solan in taiviquai(tenfile[:-5]).get(str(idbando), {}).items():
            gx, gy = map(int, khoa.split(","))
            tong[(gx, gy)] = tong.get((gx, gy), 0) + solan
    return tong


def ghinhanvitriquai(bangviquai, idbando, toadoquais):
    bang = bangviquai.setdefault(str(idbando), {})
    for x, y in toadoquais:
        khoa = f"{int(x) // OVITRIQUAI},{int(y) // OVITRIQUAI}"
        bang[khoa] = bang.get(khoa, 0) + 1


def _tamo(gx, gy):
    return gx * OVITRIQUAI + OVITRIQUAI // 2, gy * OVITRIQUAI + OVITRIQUAI // 2


def gomcum(demo, bankinh, is_vungcam = None, sodiemtoida = SODIEMDEXUATTOIDA):
    # demo: {(gx, gy): số lần} -> [(x, y, trọng số), ...] đông nhất trước, các điểm cách nhau ít nhất bankinh
    r = max(1, round(bankinh * 0.6 / OVITRIQUAI))
    lechs = [(dx, dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy <= r * r]
    conlai = {o: n for o, n in demo.items() if not (is_vungcam and is_vungcam(*_tamo(*o)))}
    cums = []
    while conlai and len(cums) < sodiemtoida:
        def matdo(o):
            return sum(conlai.get((o[0] + dx, o[1] + dy), 0) for dx, dy in lechs)
        tot = max(conlai, key = matdo)
        trongso = matdo(tot)
        if cums and trongso < cums[0][2] * TYLECUMTOITHIEU:
            break
        quanh = [((tot[0] + dx, tot[1] + dy), conlai[(tot[0] + dx, tot[1] + dy)]) for dx, dy in lechs if (tot[0] + dx, tot[1] + dy) in conlai]
        xtam = sum(_tamo(*o)[0] * n for o, n in quanh) / trongso
        ytam = sum(_tamo(*o)[1] * n for o, n in quanh) / trongso
        # Điểm đánh đặt vào ô đã thấy quái đứng gần tâm cụm nhất (quái đứng được thì nhân vật đứng được), không lấy thẳng tâm trung bình:
        # tâm hay rơi trúng đá / cây / tường. Ô trong vùng cấm đã bị loại khỏi conlai
        x, y = _tamo(*min(quanh, key = lambda q: math.dist(_tamo(*q[0]), (xtam, ytam)))[0])
        cums.append((x, y, trongso))
        conlai = {o: n for o, n in conlai.items() if math.dist(_tamo(*o), (x, y)) >= bankinh}
    return cums


def noivong(diems, is_noiduoc = None):
    # Vòng ngắn nhất đi qua mọi điểm (bắt đầu ở điểm đông quái nhất), chỉ dùng đoạn is_noiduoc(i, j) = True; không có vòng nào thì None.
    # Tối đa SODIEMDEXUATTOIDA điểm nên duyệt hết các thứ tự (8 điểm: 5040 thứ tự)
    if len(diems) <= 1:
        return list(diems)
    tot = None
    for thutu in itertools.permutations(range(1, len(diems))):
        # Vòng và vòng đi ngược là một: chỉ xét chiều có điểm thứ 2 nhỏ hơn điểm cuối
        if len(thutu) > 1 and thutu[0] > thutu[-1]:
            continue
        vong = (0,) + thutu
        canhs = [(vong[i], vong[(i + 1) % len(vong)]) for i in range(len(vong) if len(vong) > 2 else 1)]
        if is_noiduoc and not all(is_noiduoc(i, j) for i, j in canhs):
            continue
        dodai = sum(math.dist(diems[i][:2], diems[j][:2]) for i, j in canhs)
        if not tot or dodai < tot[0]:
            tot = (dodai, vong)
    return [diems[i] for i in tot[1]] if tot else None


def kiemtradoan(x1, y1, x2, y2, timduong, is_vungcam = None, solan = SOLANCHIADOANTOIDA):
    # Đoạn (x1, y1) -> (x2, y2) đi được không: timduong(x1, y1, x2, y2) -> chuỗi hướng (bytes) hoặc None.
    # Mọi ô trên đường đi không được lọt vào vùng cấm (client không biết vùng cấm)
    if (x1, y1) == (x2, y2):
        return True
    chuoihuong = timduong(x1, y1, x2, y2)
    if chuoihuong:
        x, y = x1, y1
        for kytu in chuoihuong.decode("latin1"):
            dx, dy = HUONGTIMDUONG_MAP.get(kytu, (0, 0))
            x, y = x + dx, y + dy
            if is_vungcam and is_vungcam(x, y):
                return False
        if math.dist((x, y), (x2, y2)) <= SAISODIEMDEN:
            return True
        # Chuỗi hướng bị cắt (xa quá): đi tiếp từ chỗ dừng nếu đã lại gần đích
        if solan > 0 and math.dist((x, y), (x2, y2)) < math.dist((x1, y1), (x2, y2)) - 1:
            return kiemtradoan(x, y, x2, y2, timduong, is_vungcam, solan - 1)
        return False
    # Không ra đường: có thể do xa quá => chia đôi theo đường thẳng (điểm giữa vướng vật cản thì coi như không đi được)
    if solan > 0 and math.dist((x1, y1), (x2, y2)) > 20:
        xg, yg = round((x1 + x2) / 2), round((y1 + y2) / 2)
        return kiemtradoan(x1, y1, xg, yg, timduong, is_vungcam, solan - 1) and kiemtradoan(xg, yg, x2, y2, timduong, is_vungcam, solan - 1)
    return False


def dexuatlotrinh(demo, bankinh = KHOANGCACHDIEMDEXUAT, timduong = None, is_vungcam = None, sodiemtoida = SODIEMDEXUATTOIDA):
    # -> (danh sách điểm [(x, y), ...] theo thứ tự đi, số điểm bị bỏ vì không đi được); timduong None thì không kiểm tra đường đi
    diems = gomcum(demo, bankinh, is_vungcam, sodiemtoida)
    # Kiểm tra trước mọi cặp điểm (8 điểm: 28 cặp), coi như đi 2 chiều như nhau
    noiduoc = {}
    if timduong:
        for i, j in itertools.combinations(range(len(diems)), 2):
            (x1, y1, _), (x2, y2, _) = diems[i], diems[j]
            noiduoc[diems[i][:2], diems[j][:2]] = noiduoc[diems[j][:2], diems[i][:2]] = kiemtradoan(x1, y1, x2, y2, timduong, is_vungcam)
    sobo = 0
    while len(diems) >= 2:
        vong = noivong(diems, (lambda i, j: noiduoc[diems[i][:2], diems[j][:2]]) if timduong else None)
        if vong:
            return [(d[0], d[1]) for d in vong], sobo
        # Không có vòng nào: bỏ điểm nối được với ít điểm nhất (ngang nhau thì bỏ điểm ít quái hơn) rồi thử lại
        diems.remove(min(diems, key = lambda d: (sum(noiduoc[d[:2], k[:2]] for k in diems if k is not d), d[2])))
        sobo += 1
    return [(d[0], d[1]) for d in diems], sobo
