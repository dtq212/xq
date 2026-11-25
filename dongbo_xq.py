# Đồng bộ tài khoản (taikhoan_chung.json) và tổ đội (todoi.json) giữa các máy qua GitHub: bot tự đẩy lên / kéo về, không cần commit /
# push tay, không bao giờ conflict (2026-11-15). Máy ở xa (LAPTOP-HAOPCFT6 qua UltraViewer) không chung LAN nên không dùng lan_xq.
#
# Cách làm:
#   - Dữ liệu nằm ở nhánh riêng "dulieu" trên origin, mỗi máy MỘT file dongbo/<tên máy>.json và chỉ máy đó ghi => không thể conflict.
#     Bot đọc / ghi nhánh bằng lệnh nền của git (fetch, cat-file, hash-object, index tạm, commit-tree, push): không checkout, không đụng
#     thư mục làm việc, index hay nhánh main của người dùng.
#   - File của máy là các "ô" {khoá: [mốc giờ, có/không, giá trị]}. Khoá là từng tài khoản (theo "user"), từng trường của tài khoản
#     (kể cả "maydangnhap"), thứ tự tài khoản, đường dẫn game từng máy, từng nhóm tổ đội, thứ tự nhóm. Gộp các máy: mỗi khoá lấy bản có
#     mốc giờ mới nhất => máy A thêm nhóm, máy B sửa mật khẩu một tài khoản thì giữ cả hai.
#   - Mốc giờ ghi = max(giờ máy, mốc lớn nhất đã thấy + 1ms): sửa sau khi đã thấy bản máy khác thì luôn thắng, kể cả giờ máy lệch.
#   - "maydangnhap" là một ô như mọi trường: tích ở máy B sau khi A đang giữ thì B thắng, A kéo về (tối đa CHUKYKEOVE giây) thấy tài
#     khoản không còn của mình nên thôi đăng nhập lại. Hai máy cùng tích trong cùng lúc thì bản sau thắng; trong lúc chờ, cơ chế tạm
#     hoãn khi bị đá liên tục (dangnhap_xq) chặn hai máy đá nhau mãi.
#   - taikhoan_chung.json / todoi.json vẫn là file các phần khác của bot đọc / ghi như cũ (giao diện, tự đăng nhập, tự điền ID...).
#     Luồng này so file với bản đã ghi lần trước để biết người dùng / bot vừa sửa gì, ghi thành ô của máy mình, gộp rồi ghi lại file.
#     File đang sai JSON (đang sửa tay) hoặc mất thì không coi là xoá hết, chỉ bỏ qua lượt đó.
# Trạng thái cục bộ (không đưa lên git): _internal/dongbo/
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time

from tienich_xq import _thumucthietlap, duongdantaikhoan, duongdantodoitudong, tenmaynay, thaythefile

NHANHDULIEU = "dulieu"
REFTUXA = "refs/remotes/origin/" + NHANHDULIEU
THUMUCNHANH = "dongbo"
# Kéo về mỗi chừng này giây: một lần fetch nhánh nhỏ, nhẹ. Đây cũng là độ trễ chuyển quyền đăng nhập sang máy khác
CHUKYKEOVE = 30.
# Kiểm tra file cục bộ có bị sửa không (chỉ stat) mỗi chừng này giây; sửa xong thì đẩy lên ngay lượt sau
CHUKYKIEMTRAFILE = 2.
# Lúc mở bot chờ lượt đồng bộ đầu tối đa chừng này giây trước khi chạy tự đăng nhập (mất mạng thì chạy với bản đã lưu)
THOIGIANCHOLUOTDAU = 25.
THOIGIANCHOLENHGIT = 60
# Thứ tự trường khi ghi lại file tài khoản (cho dễ đọc khi mở tay), trường khác xếp sau theo tên
THUTUTRUONGTAIKHOANs = ("tennhanvat", "idnguoichoi", "group", "server", "char_index", "maydangnhap", "vitricuaso", "duongdangame", "user", "pass")
TAIKHOAN, TODOI = "taikhoan", "todoi"


def _k(*phan):
    return json.dumps(list(phan), ensure_ascii = False)


def _cj(giatri):
    # So giá trị theo JSON: Python coi True == 1, ở đây phải khác
    return json.dumps(giatri, sort_keys = True, ensure_ascii = False)


def _thumuctrangthai():
    return os.path.join(os.path.dirname(_thumucthietlap()), "dongbo")


def _docjson(duongdan):
    with open(duongdan, encoding = "utf-8-sig") as file:
        return json.load(file)


def _ghijson(duongdan, dulieu, thutle = 2):
    os.makedirs(os.path.dirname(duongdan), exist_ok = True)
    filetam = duongdan + ".tmp"
    with open(filetam, "w", encoding = "utf-8") as file:
        json.dump(dulieu, file, ensure_ascii = False, indent = thutle)
    thaythefile(filetam, duongdan)


# ---------- File <-> ô ----------

def _otaikhoan(cauhinh):
    # taikhoan_chung.json -> {khoá: giá trị}
    o = {}
    thutu = []
    for taikhoan in cauhinh.get("taikhoans") or []:
        user = taikhoan.get("user") if isinstance(taikhoan, dict) else None
        if user == "taikhoan" and taikhoan.get("pass") == "matkhau":
            continue  # dòng mẫu dangnhap_xq.CAUHINHMAU
        if not isinstance(user, str) or not user:
            print(f"[ĐỒNG BỘ] Bỏ qua dòng tài khoản không có \"user\": {taikhoan}")
            continue
        if user in thutu:
            print(f"[ĐỒNG BỘ] Tài khoản \"{user}\" bị trùng, chỉ giữ dòng đầu")
            continue
        thutu.append(user)
        o[_k("tk", user)] = True
        for truong, giatri in taikhoan.items():
            if truong != "user":
                o[_k("tk", user, truong)] = giatri
    o[_k("tkthutu")] = thutu
    for may, duongdan in (cauhinh.get("duongdangames") or {}).items():
        o[_k("dg", may)] = duongdan
    for khoa, giatri in cauhinh.items():
        if khoa not in ("taikhoans", "duongdangames", "loi"):
            o[_k("chung", khoa)] = giatri
    return o


def _filetaikhoan(o):
    # {khoá: giá trị} -> nội dung taikhoan_chung.json
    users, truongs, chung, duongdangames, thutu = [], {}, {}, {}, []
    for khoa, giatri in o.items():
        phan = json.loads(khoa)
        if phan[0] == "tk" and len(phan) == 2 and giatri is True:
            users.append(phan[1])
        elif phan[0] == "tk" and len(phan) == 3:
            truongs.setdefault(phan[1], {})[phan[2]] = giatri
        elif phan[0] == "tkthutu" and isinstance(giatri, list):
            thutu = giatri
        elif phan[0] == "dg":
            duongdangames[phan[1]] = giatri
        elif phan[0] == "chung":
            chung[phan[1]] = giatri
    con = set(users)
    thutu = [u for u in dict.fromkeys(thutu) if u in con] + sorted(u for u in con if u not in thutu)
    taikhoans = []
    for user in thutu:
        dl = truongs.get(user, {})
        taikhoan = {truong: dl[truong] for truong in THUTUTRUONGTAIKHOANs if truong in dl}
        taikhoan["user"] = user
        if "pass" in dl:
            taikhoan["pass"] = dl["pass"]
        for truong in sorted(dl):
            taikhoan.setdefault(truong, dl[truong])
        taikhoans.append(taikhoan)
    return {**chung, "duongdangames": dict(sorted(duongdangames.items())), "taikhoans": taikhoans}


def _chuanhoanhoms(nhoms):
    from tienich_xq import _chuanhoanhomtodoitudongs
    return _chuanhoanhomtodoitudongs(nhoms)


def _otodoi(dulieu):
    # Nhóm nhận diện theo nội dung (danh sách ID theo thứ tự ưu tiên): sửa nhóm = xoá nhóm cũ + thêm nhóm mới
    o = {}
    thutu = []
    for nhom in _chuanhoanhoms(dulieu.get("nhoms") if isinstance(dulieu, dict) else None):
        ma = ",".join(map(str, nhom))
        if ma not in thutu:
            thutu.append(ma)
            o[_k("nhom", ma)] = True
    o[_k("nhomthutu")] = thutu
    # Thành viên vãng lai (tienich_xq.layvanglaitodois): mỗi ID 1 ô để máy này bỏ / máy kia thêm gộp được
    vanglais = _chuanhoanhoms([dulieu.get("vanglais")]) if isinstance(dulieu, dict) else []
    for id_ in (vanglais[0] if vanglais else []):
        o[_k("vanglai", id_)] = True
    # Nhóm đang tắt Tổ đội tự động (tienich_xq.tainhomtattodois), theo mã nhóm
    for ma in (dulieu.get("nhomtats") or []) if isinstance(dulieu, dict) else []:
        if isinstance(ma, str) and ma:
            o[_k("nhomtat", ma)] = True
    return o


def _filetodoi(o):
    mas, thutu, vanglais, nhomtats = [], [], [], []
    for khoa, giatri in o.items():
        phan = json.loads(khoa)
        if phan[0] == "vanglai" and giatri is True:
            vanglais.append(int(phan[1]))
        elif phan[0] == "nhomtat" and giatri is True:
            nhomtats.append(phan[1])
        elif phan[0] == "nhom" and giatri is True:
            mas.append(phan[1])
        elif phan[0] == "nhomthutu" and isinstance(giatri, list):
            thutu = giatri
    con = set(mas)
    thutu = [m for m in dict.fromkeys(thutu) if m in con] + sorted(m for m in con if m not in thutu)
    return {"nhoms": [[int(x) for x in ma.split(",")] for ma in thutu], "vanglais": sorted(set(vanglais)),
            "nhomtats": sorted(m for m in set(nhomtats) if m in con)}


def _phanfile(khoa):
    return TODOI if json.loads(khoa)[0] in ("nhom", "nhomthutu", "vanglai", "nhomtat") else TAIKHOAN


LOAIFILEs = {
    TAIKHOAN: (duongdantaikhoan, _otaikhoan, _filetaikhoan, 4),
    TODOI: (duongdantodoitudong, _otodoi, _filetodoi, 2),
}


# ---------- Gộp ô các máy ----------

def hopnhat(cacmay):
    # cacmay: {tên máy: {khoá: [mốc giờ, có/không, giá trị]}} -> ({khoá: giá trị đang có}, mốc lớn nhất)
    thang = {}
    mocmax = 0.
    for may, oss in cacmay.items():
        for khoa, (moc, is_co, giatri) in oss.items():
            mocmax = max(mocmax, moc)
            if khoa not in thang or (moc, may) > (thang[khoa][0], thang[khoa][1]):
                thang[khoa] = (moc, may, is_co, giatri)
    return {khoa: giatri for khoa, (_, _, is_co, giatri) in thang.items() if is_co}, mocmax


def khacnhau(cu, moi):
    # Các khoá đổi giữa hai bộ ô: {khoá: (có/không, giá trị mới)}
    doi = {}
    for khoa in set(cu) | set(moi):
        if khoa not in moi:
            doi[khoa] = (False, None)
        elif khoa not in cu or _cj(cu[khoa]) != _cj(moi[khoa]):
            doi[khoa] = (True, moi[khoa])
    return doi


# ---------- Git ----------

def _timgit():
    duongdan = shutil.which("git")
    if duongdan:
        return duongdan
    for duongdan in (r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files (x86)\Git\cmd\git.exe",
                     os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\cmd\git.exe")):
        if os.path.exists(duongdan):
            return duongdan
    return None


class LoiGit(Exception):
    pass


class GitNhanhDuLieu:
    # Đọc / ghi nhánh dulieu trên origin mà không đụng thư mục làm việc
    def __init__(self, thumuc, tenmay):
        self.exe = _timgit()
        self.thumuc = thumuc
        self.tenmay = tenmay
        self.duongdanfile = f"{THUMUCNHANH}/{tenmay}.json"

    def chay(self, *thamso, dauvao = None, env = None):
        moitruong = dict(os.environ, GIT_TERMINAL_PROMPT = "0")
        if env:
            moitruong.update(env)
        try:
            kq = subprocess.run([self.exe, "-c", "safe.directory=*", *thamso], cwd = self.thumuc, input = dauvao, capture_output = True,
                                timeout = THOIGIANCHOLENHGIT, env = moitruong, creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except subprocess.TimeoutExpired:
            raise LoiGit(f"git {thamso[0]} quá {THOIGIANCHOLENHGIT}s")
        if kq.returncode != 0:
            raise LoiGit(kq.stderr.decode("utf-8", "replace").strip() or f"git {thamso[0]} lỗi {kq.returncode}")
        return kq.stdout

    def is_dung(self):
        if not self.exe:
            return "không tìm thấy git.exe"
        try:
            self.chay("rev-parse", "--git-dir")
            self.chay("remote", "get-url", "origin")
        except LoiGit as err:
            return f"không phải repo git có origin ({err})"
        return None

    def _commit(self):
        try:
            return self.chay("rev-parse", "--verify", "--quiet", REFTUXA + "^{commit}").decode().strip() or None
        except LoiGit:
            return None

    def keove(self):
        # -> commit của nhánh trên origin, None nếu origin chưa có nhánh. Lỗi mạng thì ném LoiGit
        try:
            self.chay("fetch", "--quiet", "--no-tags", "origin", f"+refs/heads/{NHANHDULIEU}:{REFTUXA}")
        except LoiGit as err:
            if "couldn't find remote ref" in str(err).lower():
                return None
            raise
        return self._commit()

    def docfiles(self, commit):
        # -> {tên máy: nội dung file của máy đó trên nhánh}
        if not commit:
            return {}
        ketqua = {}
        for dong in self.chay("ls-tree", "--name-only", commit, THUMUCNHANH + "/").decode("utf-8").splitlines():
            ten = os.path.basename(dong.strip().strip('"'))
            if not ten.endswith(".json"):
                continue
            try:
                ketqua[ten[:-5]] = json.loads(self.chay("cat-file", "blob", f"{commit}:{THUMUCNHANH}/{ten}").decode("utf-8"))
            except (LoiGit, ValueError) as err:
                print(f"[ĐỒNG BỘ] Bỏ qua {THUMUCNHANH}/{ten} trên nhánh {NHANHDULIEU}: {err}")
        return ketqua

    def dayfile(self, noidung):
        # Đẩy file của máy này lên nhánh (ghép lên commit mới nhất của origin). Bị từ chối vì máy khác vừa đẩy thì kéo về rồi ghép lại
        tacgia = {f"GIT_{vai}_{truong}": giatri for vai in ("AUTHOR", "COMMITTER")
                  for truong, giatri in (("NAME", f"bot {self.tenmay}"), ("EMAIL", f"bot@{self.tenmay}.local"))}
        blob = self.chay("hash-object", "-w", "--stdin", dauvao = noidung).decode().strip()
        loicuoi = None
        for _ in range(4):
            cha = self._commit()
            thumuctam = tempfile.mkdtemp(prefix = "xq_dongbo_")
            try:
                index = {"GIT_INDEX_FILE": os.path.join(thumuctam, "index")}
                if cha:
                    self.chay("read-tree", cha, env = index)
                else:
                    self.chay("read-tree", "--empty", env = index)
                self.chay("update-index", "--add", "--cacheinfo", f"100644,{blob},{self.duongdanfile}", env = index)
                cay = self.chay("write-tree", env = index).decode().strip()
            finally:
                shutil.rmtree(thumuctam, ignore_errors = True)
            if cha and self.chay("rev-parse", cha + "^{tree}").decode().strip() == cay:
                return
            thamsocha = ["-p", cha] if cha else []
            commit = self.chay("commit-tree", cay, *thamsocha, "-m", f"dong bo {self.tenmay}", env = tacgia).decode().strip()
            try:
                self.chay("push", "--quiet", "--no-verify", "origin", f"{commit}:refs/heads/{NHANHDULIEU}")
                self.chay("update-ref", REFTUXA, commit)
                return
            except LoiGit as err:
                loicuoi = err
                self.keove()
        raise LoiGit(f"đẩy lên không được: {loicuoi}")

    def khoiphuctulichsu(self, duongdan):
        # File chung trước đây nằm trên main, đã bỏ khỏi git: lấy bản cuối cùng trong lịch sử (khi máy kéo main về bị git xoá mất file)
        tuongdoi = os.path.relpath(duongdan, self.thumuc).replace("\\", "/")
        try:
            commit = self.chay("rev-list", "-1", "HEAD", "--", tuongdoi).decode().strip()
            if not commit:
                return None
            for ban in (commit, commit + "^"):
                try:
                    return json.loads(self.chay("show", f"{ban}:{tuongdoi}").decode("utf-8-sig"))
                except (LoiGit, ValueError):
                    continue
        except LoiGit:
            pass
        return None


# ---------- Luồng đồng bộ ----------

class DongBoDuLieu:
    def __init__(self):
        self.tenmay = tenmaynay()
        self.thumuc = _thumuctrangthai()
        self.duongdancuaminh = os.path.join(self.thumuc, f"{self.tenmay}.json")
        self.duongdanmaykhac = os.path.join(self.thumuc, "_maykhac.json")
        self.duongdandaxem = os.path.join(self.thumuc, "_daxem.json")
        thumucrepo = os.path.dirname(os.path.dirname(_thumucthietlap()))
        self.git = GitNhanhDuLieu(thumucrepo, self.tenmay)
        self.trangthai = "Chưa chạy"
        self._luotdau = threading.Event()
        self._loicuoi = None
        # Ô của máy này {khoá: [mốc, có, giá trị]}, ô các máy khác {máy: {...}}, bản ô đã ghi ra file lần trước {loại file: {...}}
        self.cuaminh = self._doc(self.duongdancuaminh, {}).get("o", {})
        self.maykhacs = self._doc(self.duongdanmaykhac, {})
        daxem = self._doc(self.duongdandaxem, None)
        # Chưa có bản đã xem = máy mới chạy lần đầu: chờ kéo về được một lần rồi mới nhận dữ liệu cục bộ (_khoitao)
        self.is_khoitao = daxem is None
        daxem = daxem or {}
        self.daxem = {loai: daxem.get(loai) for loai in LOAIFILEs}
        self.daday = daxem.get("daday")
        self._statfile = {}

    @staticmethod
    def _doc(duongdan, macdinh):
        try:
            return _docjson(duongdan)
        except FileNotFoundError:
            return macdinh
        except Exception as err:
            print(f"[ĐỒNG BỘ] Lỗi đọc {duongdan}: {err}")
            return macdinh

    def _luutrangthai(self):
        _ghijson(self.duongdancuaminh, self._noidungcuaminh())
        _ghijson(self.duongdanmaykhac, self.maykhacs)
        _ghijson(self.duongdandaxem, {**self.daxem, "daday": self.daday})

    def _noidungcuaminh(self):
        return {"may": self.tenmay, "o": dict(sorted(self.cuaminh.items()))}

    def _baoloi(self, thongbao):
        self.trangthai = f"Lỗi: {thongbao}"
        if thongbao != self._loicuoi:
            self._loicuoi = thongbao
            print(f"[ĐỒNG BỘ] {thongbao}")

    def batdau(self):
        loi = self.git.is_dung()
        if loi:
            self.trangthai = f"Tắt: {loi}"
            print(f"[ĐỒNG BỘ] Tắt đồng bộ tài khoản / tổ đội: {loi}")
            return
        threading.Thread(target = self._loop, daemon = True).start()
        if not self._luotdau.wait(THOIGIANCHOLUOTDAU):
            print(f"[ĐỒNG BỘ] Chưa kéo về được sau {THOIGIANCHOLUOTDAU:.0f}s, chạy tiếp với bản đã lưu trên máy")

    def _loop(self):
        lankeove = 0.
        while True:
            try:
                is_keove = time.time() - lankeove >= CHUKYKEOVE
                if is_keove:
                    lankeove = time.time()
                self._motluot(is_keove)
                if self._loicuoi:
                    self._loicuoi = None
                    print("[ĐỒNG BỘ] Đồng bộ lại bình thường")
            except LoiGit as err:
                self._baoloi(str(err))
            except Exception as err:
                self._baoloi(f"{type(err).__name__}: {err}")
            finally:
                if is_keove:
                    self._luotdau.set()
            time.sleep(CHUKYKIEMTRAFILE)

    def _stat(self, loai):
        try:
            st = os.stat(LOAIFILEs[loai][0]())
            return st.st_mtime_ns, st.st_size
        except OSError:
            return None

    def _docfile(self, loai):
        # -> (ô trong file, stat lúc đọc) ; ô None nếu file mất / sai JSON
        stat = self._stat(loai)
        duongdan, taoo = LOAIFILEs[loai][0](), LOAIFILEs[loai][1]
        if stat is None:
            return None, None
        try:
            dulieu = _docjson(duongdan)
            if not isinstance(dulieu, dict):
                raise ValueError("không phải đối tượng JSON")
        except Exception as err:
            self._baoloi(f"{os.path.basename(duongdan)} đang lỗi, chưa đồng bộ file này: {err}")
            return None, stat
        return taoo(dulieu), stat

    def _keove(self):
        commit = self.git.keove()
        files = self.git.docfiles(commit)
        maykhacs = {may: (nd.get("o") or {}) for may, nd in files.items() if may != self.tenmay and isinstance(nd, dict)}
        if maykhacs != self.maykhacs:
            self.maykhacs = maykhacs
            _ghijson(self.duongdanmaykhac, self.maykhacs)
        return files.get(self.tenmay)

    def _ghio(self, doi, mocmax):
        moc = max(time.time(), mocmax + 0.001)
        for khoa, (is_co, giatri) in doi.items():
            self.cuaminh[khoa] = [moc, is_co, giatri]

    def _khoitao(self, banminhtrennhanh):
        # Máy chạy lần đầu (hoặc mất thư mục dongbo/): lấy dữ liệu trên nhánh làm gốc. Máy đầu tiên (nhánh trống) thì ghi toàn bộ file
        # cục bộ lên. Máy sau chỉ thêm tài khoản / nhóm / đường dẫn game mà nhánh chưa có, không ghi đè các trường đã có trên nhánh
        # (file cục bộ có thể là bản cũ kéo từ main về)
        if isinstance(banminhtrennhanh, dict):
            self.cuaminh = banminhtrennhanh.get("o") or {}
        hientai, mocmax = hopnhat({**self.maykhacs, self.tenmay: self.cuaminh})
        is_nhanhtrong = not hientai
        for loai, (layduongdan, taoo, _, _) in LOAIFILEs.items():
            o, _ = self._docfile(loai)
            if o is None and not os.path.exists(layduongdan()):
                dulieu = self.git.khoiphuctulichsu(layduongdan())
                if dulieu is not None:
                    print(f"[ĐỒNG BỘ] Khôi phục {os.path.basename(layduongdan())} từ lịch sử git để gộp")
                    o = taoo(dulieu)
            # Bản đã xem = file cục bộ: lượt sau không coi nội dung cũ của file là sửa mới, chỉ ghi lại file theo bản gộp
            self.daxem[loai] = o if o is not None else {}
            if o is None:
                continue
            if is_nhanhtrong:
                doi = {khoa: (True, giatri) for khoa, giatri in o.items()}
            else:
                cotk = {json.loads(k)[1] for k in hientai if json.loads(k)[0] == "tk"}
                doi = {}
                for khoa, giatri in o.items():
                    phan = json.loads(khoa)
                    if (phan[0] == "tk" and phan[1] not in cotk) or (phan[0] in ("nhom", "dg") and khoa not in hientai):
                        doi[khoa] = (True, giatri)
            if doi:
                print(f"[ĐỒNG BỘ] Lần đầu: đưa {len(doi)} mục của {os.path.basename(layduongdan())} lên nhánh {NHANHDULIEU}")
                self._ghio(doi, mocmax)
        self.is_khoitao = False

    def _motluot(self, is_keove):
        stats = {loai: self._stat(loai) for loai in LOAIFILEs}
        if not is_keove and not self.is_khoitao and stats == self._statfile:
            return
        if is_keove or self.is_khoitao:
            banminh = self._keove()
            if self.is_khoitao:
                self._khoitao(banminh)
        # Người dùng / bot sửa file từ lần ghi trước -> ô của máy này
        dadoc = {}
        _, mocmax = hopnhat({**self.maykhacs, self.tenmay: self.cuaminh})
        for loai in LOAIFILEs:
            o, stat = self._docfile(loai)
            dadoc[loai] = (o, stat)
            if o is not None and self.daxem[loai] is not None:
                doi = khacnhau(self.daxem[loai], o)
                if doi:
                    print(f"[ĐỒNG BỘ] Ghi nhận {len(doi)} thay đổi trong {os.path.basename(LOAIFILEs[loai][0]())}")
                    self._ghio(doi, mocmax)
        # Gộp mọi máy rồi ghi lại file nếu khác
        hientai, _ = hopnhat({**self.maykhacs, self.tenmay: self.cuaminh})
        for loai, (layduongdan, taoo, taofile, thutle) in LOAIFILEs.items():
            o = {khoa: giatri for khoa, giatri in hientai.items() if _phanfile(khoa) == loai}
            # Chuẩn hoá qua file (thứ tự đã ghép nhóm / tài khoản thiếu trong danh sách thứ tự): bản đã xem đúng như nội dung file
            o = taoo(taofile(o)) if o else o
            ofile, statdoc = dadoc[loai]
            if ofile is None and statdoc is not None:
                continue  # file sai JSON: đợi người dùng sửa xong, không ghi đè
            if not o and ofile is None:
                continue
            if ofile is None or khacnhau(ofile, o):
                if self._stat(loai) != statdoc:
                    continue  # vừa có ai ghi file: lượt sau so lại
                _ghijson(layduongdan(), taofile(o), thutle)
                if ofile is not None:
                    print(f"[ĐỒNG BỘ] Cập nhật {os.path.basename(layduongdan())} theo máy khác")
            self.daxem[loai] = o
        self._statfile = {loai: self._stat(loai) for loai in LOAIFILEs}
        # Đẩy file của máy này lên nếu đổi
        noidung = json.dumps(self._noidungcuaminh(), ensure_ascii = False, indent = 1).encode("utf-8")
        bam = hashlib.sha1(noidung).hexdigest()
        self._luutrangthai()
        if bam != self.daday and self.cuaminh:
            self.git.dayfile(noidung)
            self.daday = bam
            self._luutrangthai()
        self.trangthai = f"Đã đồng bộ {time.strftime('%H:%M:%S')} ({len(self.maykhacs)} máy khác)"
