/*
 * A* trên lưới vật cản cho bot xq (bản C của MoiTruong._timduongkhongcatgoc, gọi qua ctypes từ astar_c_xq.py).
 *
 * Vì sao viết bằng C: đo 2026-11-12 trên _internal/luoi_*.json, bản Python cả bản đồ có đường mất 4-106 ms (bản đồ 80 có lúc 400 ms),
 * mỗi ô mở tốn vài µs cho dict / tuple / heapq. Bản C dùng mảng phẳng, mỗi ô vài chục ns.
 *
 * Cho ra ĐÚNG Y đường như bản Python để so sánh được từng ký tự:
 *  - chi phí bước: thẳng 1.0, chéo 1.4142 (hằng số như Python, không phải sqrt(2)), cộng phạt của ô bước vào;
 *  - heuristic: khoảng cách Euclid tới đích (Python: math.dist);
 *  - hàng đợi ưu tiên so theo bộ (f, g, x, y) như tuple Python (f, g, (x, y)) trong heapq;
 *  - "lazy deletion": lấy ra mà g > gs[ô] thì bỏ, như Python;
 *  - chéo chỉ khi 2 ô kề đều trống (trừ khi cho cắt góc);
 *  - tới ô cách đích không quá nguong (nguong = 0: đúng ô đích) là xong.
 *
 * Lưới truyền vào là mảng phẳng trong[x * cao + y] (1 đi được, 0 vật cản), cùng thứ tự với luoi[x][y] bên Python.
 *
 * Build: build_astar.bat (MSVC x64, Python 3.8 64-bit). Ra astar_xq.dll cạnh file này.
 */
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#define XUAT __declspec(dllexport)
#else
#define XUAT
#endif

/* Phiên bản giao diện hàm: astar_c_xq.py kiểm tra, lệch thì không dùng DLL (DLL cũ còn sót sau khi sửa C) */
XUAT int astar_phienban(void) { return 1; }

/* Một phần tử hàng đợi: so theo (f, g, x, y) */
typedef struct {
    double f, g;
    int x, y;
} PhanTu;

static int nho_hon(const PhanTu *a, const PhanTu *b) {
    if (a->f != b->f) return a->f < b->f;
    if (a->g != b->g) return a->g < b->g;
    if (a->x != b->x) return a->x < b->x;
    return a->y < b->y;
}

/* Đống nhị phân (min-heap) tự giãn, cùng cách heapq của Python (đẩy lên khi thêm, đẩy xuống khi lấy) */
typedef struct {
    PhanTu *a;
    int n, sucChua;
} Dong;

static int dong_them(Dong *d, PhanTu p) {
    if (d->n == d->sucChua) {
        int moi = d->sucChua ? d->sucChua * 2 : 1024;
        PhanTu *a = (PhanTu *)realloc(d->a, sizeof(PhanTu) * (size_t)moi);
        if (!a) return 0;
        d->a = a;
        d->sucChua = moi;
    }
    int i = d->n++;
    while (i > 0) {
        int cha = (i - 1) >> 1;
        if (!nho_hon(&p, &d->a[cha])) break;
        d->a[i] = d->a[cha];
        i = cha;
    }
    d->a[i] = p;
    return 1;
}

static PhanTu dong_lay(Dong *d) {
    PhanTu dau = d->a[0];
    PhanTu cuoi = d->a[--d->n];
    int i = 0;
    for (;;) {
        int con = 2 * i + 1;
        if (con >= d->n) break;
        if (con + 1 < d->n && nho_hon(&d->a[con + 1], &d->a[con])) con++;
        if (!nho_hon(&d->a[con], &cuoi)) break;
        d->a[i] = d->a[con];
        i = con;
    }
    if (d->n) d->a[i] = cuoi;
    return dau;
}

/*
 * trong:      rong * cao byte, trong[x * cao + y] != 0 là đi được (đã trừ ô vật cản ghi tay)
 * phat:       NULL hoặc rong * cao double, chi phí cộng thêm khi bước VÀO ô (khu vực cấm, NPC, chặn tạm)
 * x1, y1:     ô xuất phát (không cần đi được, như Python)
 * x2, y2:     ô đích; nguong: tới ô cách đích (Euclid) không quá nguong là xong, 0 = đúng ô đích
 * chocatgoc:  1 = cho đi chéo qua khe 2 vật cản chạm góc
 * dxs, dys, kytus: 8 hướng theo đúng thứ tự HUONGTIMDUONG_MAP bên Python, kytus là ký tự ghi vào chuỗi đường đi
 * ra, tranhtoida: bộ đệm nhận chuỗi hướng
 * somo:       NULL hoặc nhận số ô đã mở (để log)
 * Trả về: > 0 độ dài chuỗi; 0 không có đường (hoặc đích = xuất phát); -1 thiếu bộ nhớ; -2 bộ đệm ra quá nhỏ
 */
XUAT int astar_timduong(const unsigned char *trong, const double *phat, int rong, int cao,
                        int x1, int y1, int x2, int y2, double nguong, int chocatgoc,
                        const int *dxs, const int *dys, const char *kytus,
                        char *ra, int tranhtoida, int *somo) {
    const double VOCUC = 1e300;
    size_t soo = (size_t)rong * (size_t)cao;
    double *gs = (double *)malloc(sizeof(double) * soo);
    signed char *huongtoi = (signed char *)malloc(soo);  /* hướng (0..7) đã đi để tới ô, -1 chưa tới */
    Dong dong = {0};
    int ketqua = 0, dem = 0;
    if (!gs || !huongtoi) {
        ketqua = -1;
        goto xong;
    }
    if (x1 < 0 || x1 >= rong || y1 < 0 || y1 >= cao) goto xong;
    for (size_t i = 0; i < soo; i++) gs[i] = VOCUC;
    memset(huongtoi, -1, soo);

#define TRONG(x, y) ((x) >= 0 && (x) < rong && (y) >= 0 && (y) < cao && trong[(size_t)(x) * cao + (y)])

    gs[(size_t)x1 * cao + y1] = 0.;
    {
        PhanTu p = {hypot((double)(x1 - x2), (double)(y1 - y2)), 0., x1, y1};
        if (!dong_them(&dong, p)) { ketqua = -1; goto xong; }
    }
    int dichx = -1, dichy = -1;
    while (dong.n) {
        PhanTu p = dong_lay(&dong);
        size_t k = (size_t)p.x * cao + p.y;
        if (p.g > gs[k]) continue;
        dem++;
        if (nguong > 0. ? hypot((double)(p.x - x2), (double)(p.y - y2)) <= nguong : (p.x == x2 && p.y == y2)) {
            dichx = p.x;
            dichy = p.y;
            break;
        }
        for (int h = 0; h < 8; h++) {
            int dx = dxs[h], dy = dys[h];
            int nx = p.x + dx, ny = p.y + dy;
            if (!TRONG(nx, ny)) continue;
            if (dx && dy && !chocatgoc && !(TRONG(p.x + dx, p.y) && TRONG(p.x, p.y + dy))) continue;
            size_t kn = (size_t)nx * cao + ny;
            double ng = p.g + ((dx && dy) ? 1.4142 : 1.) + (phat ? phat[kn] : 0.);
            if (ng < gs[kn]) {
                gs[kn] = ng;
                huongtoi[kn] = (signed char)h;
                PhanTu q = {ng + hypot((double)(nx - x2), (double)(ny - y2)), ng, nx, ny};
                if (!dong_them(&dong, q)) { ketqua = -1; goto xong; }
            }
        }
    }
    if (dichx < 0 || (dichx == x1 && dichy == y1)) goto xong;

    /* Đi ngược từ đích về xuất phát theo hướng đã tới, rồi đảo chuỗi */
    {
        int n = 0, x = dichx, y = dichy;
        while (!(x == x1 && y == y1)) {
            int h = huongtoi[(size_t)x * cao + y];
            if (n >= tranhtoida) { ketqua = -2; goto xong; }
            ra[n++] = kytus[h];
            x -= dxs[h];
            y -= dys[h];
        }
        for (int i = 0, j = n - 1; i < j; i++, j--) {
            char t = ra[i];
            ra[i] = ra[j];
            ra[j] = t;
        }
        ketqua = n;
    }
#undef TRONG

xong:
    if (somo) *somo = dem;
    free(gs);
    free(huongtoi);
    free(dong.a);
    return ketqua;
}
