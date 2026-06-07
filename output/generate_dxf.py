#!/usr/bin/env python3
"""
33000DWT双燃料成品油轮 — 货仓结构图 DXF 生成脚本
======================================================
生成内容：
  1. 平面图（Tank Top层）— 货舱区俯视布置
  2. 纵剖面图 — 货舱区侧面布置
  3. 横剖面图 — 典型货舱截面（含吸油井）
图层：HULL / BULKHEAD / CENTERLINE / DIMENSION / TEXT
单位：mm（1:1 实船尺寸）
"""

import ezdxf
from ezdxf import units, zoom
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Vec2
import math

# ============================================================
# 船舶设计参数（来源：CLAUDE.md）
# ============================================================
LOA       = 180000   # 总长 [mm]
LBP       = 177000   # 垂线间长 [mm]
B         = 28000    # 型宽 [mm]
D         = 15200    # 型深 [mm]
T_design  = 9500     # 设计吃水 [mm]
DB_H      = 2000     # 双层底高度 [mm]
N_TANKS   = 10       # 货油舱对数
CARGO_LEN = 135000   # 货舱区总长 [mm]
TANK_LEN  = CARGO_LEN // N_TANKS  # 每对舱长度 [mm]
HALF_B    = B // 2   # 半宽 [mm]

# 各区域纵向位置（距AP的距离）
# AP=0, FP=LBP, 船艏方向为+x
ER_START   = 0               # 机舱起始
ER_END     = 21000           # 机舱前端壁 (= 泵舱后壁)
PUMP_LEN   = 6000            # 泵舱长度
PUMP_START = ER_END          # 泵舱起始 = 21000
PUMP_END   = PUMP_START + PUMP_LEN  # 泵舱前端 = 27000
SLOP_LEN   = 6500            # 污油舱长度
SLOP_START = PUMP_END        # 污油舱起始 = 27000
SLOP_END   = SLOP_START + SLOP_LEN  # 污油舱前端 = 33500
COT_START  = SLOP_END        # 货油舱起始 = 33500
COT_END    = COT_START + CARGO_LEN   # 货油舱前端 = 168500
FP         = LBP             # 艏垂线 = 177000

# 各货油舱边界（10对，从艉到艏编号10→1）
COT_BOUNDS = []
for i in range(N_TANKS):
    x0 = COT_START + i * TANK_LEN
    x1 = x0 + TANK_LEN
    tank_no = N_TANKS - i  # 10, 9, 8, ... 1
    COT_BOUNDS.append((x0, x1, tank_no))

# ============================================================
# DXF 文档初始化
# ============================================================
doc = ezdxf.new("R2010", setup=True)
doc.units = units.MM
msp = doc.modelspace()

# ---- 图层定义 ----
LAYERS = {
    "HULL":        {"color": 7,  "lineweight": 50, "linetype": "Continuous"},
    "BULKHEAD":    {"color": 1,  "lineweight": 35, "linetype": "Continuous"},
    "CENTERLINE":  {"color": 2,  "lineweight": 18, "linetype": "CENTER"},
    "DIMENSION":   {"color": 3,  "lineweight": 18, "linetype": "Continuous"},
    "TEXT":        {"color": 7,  "lineweight": 0,  "linetype": "Continuous"},
    "ANNOTATION":  {"color": 4,  "lineweight": 18, "linetype": "Continuous"},
    "HIDDEN":      {"color": 8,  "lineweight": 18, "linetype": "HIDDEN"},
}

for name, props in LAYERS.items():
    layer = doc.layers.add(name)
    layer.color = props["color"]
    layer.lineweight = props["lineweight"]
    # CENTER 和 HIDDEN 线型需要加载
    if props["linetype"] in ("CENTER", "HIDDEN"):
        try:
            doc.linetypes.add(props["linetype"])
        except Exception:
            pass  # 线型可能已存在
    layer.dxf.linetype = props["linetype"]

# ---- 文字样式 ----
doc.styles.add("CJK", font="isocp.shx")
doc.styles.add("CJK_BOLD", font="isocp.shx")

# ============================================================
# 辅助函数
# ============================================================

def polyline_rect(msp, x0, y0, x1, y1, layer="HULL"):
    """绘制矩形"""
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})

def line_seg(msp, x0, y0, x1, y1, layer="HULL"):
    """绘制线段"""
    msp.add_line((x0, y0), (x1, y1), dxfattribs={"layer": layer})

def add_text(msp, x, y, text, height=500, layer="TEXT", rotation=0,
             alignment=TextEntityAlignment.MIDDLE_CENTER):
    """添加文字"""
    t = msp.add_text(text, dxfattribs={"layer": layer, "height": height})
    t.dxf.rotation = rotation
    t.set_placement((x, y), alignment)

def add_text_left(msp, x, y, text, height=500, layer="TEXT"):
    """左对齐文字"""
    t = msp.add_text(text, dxfattribs={"layer": layer, "height": height})
    t.set_placement((x, y), TextEntityAlignment.MIDDLE_LEFT)

def dimension_horiz(msp, x0, x1, y, offset, text_override=None, layer="DIMENSION"):
    """绘制水平尺寸标注"""
    # 尺寸线
    y_dim = y - offset
    line_seg(msp, x0, y_dim, x1, y_dim, layer)
    # 左右起止线
    line_seg(msp, x0, y, x0, y_dim - 300, layer)
    line_seg(msp, x1, y, x1, y_dim - 300, layer)
    # 箭头（简化：短斜线）
    arr = 400
    line_seg(msp, x0, y_dim, x0 + arr, y_dim - arr, layer)
    line_seg(msp, x0, y_dim, x0 + arr, y_dim + arr, layer)
    line_seg(msp, x1, y_dim, x1 - arr, y_dim - arr, layer)
    line_seg(msp, x1, y_dim, x1 - arr, y_dim + arr, layer)
    # 文字
    if text_override:
        txt = text_override
    else:
        txt = f"{(x1 - x0) / 1000:.1f}m"
    add_text(msp, (x0 + x1) / 2, y_dim - 700, txt, height=500, layer="TEXT")

def dimension_vert(msp, x, y0, y1, offset, text_override=None, layer="DIMENSION"):
    """绘制垂直尺寸标注"""
    x_dim = x + offset
    line_seg(msp, x_dim, y0, x_dim, y1, layer)
    line_seg(msp, x, y0, x_dim + 300, y0, layer)
    line_seg(msp, x, y1, x_dim + 300, y1, layer)
    arr = 400
    line_seg(msp, x_dim, y0, x_dim - arr, y0 + arr, layer)
    line_seg(msp, x_dim, y0, x_dim + arr, y0 + arr, layer)
    line_seg(msp, x_dim, y1, x_dim - arr, y1 - arr, layer)
    line_seg(msp, x_dim, y1, x_dim + arr, y1 - arr, layer)
    if text_override:
        txt = text_override
    else:
        txt = f"{(y1 - y0) / 1000:.1f}m"
    add_text(msp, x_dim + 1200, (y0 + y1) / 2, txt, height=500, layer="TEXT", rotation=90,
             alignment=TextEntityAlignment.MIDDLE_CENTER)


def waterline_half_breath(x, ship_half_b=HALF_B):
    """
    计算设计水线处半宽（简化船体线型）
    采用抛物线型艏艉，平行中体

    坐标系统：x = 距AP的距离 [mm]
    LOA 从 -3000 (艉突出) 到 180000 (艏突出)
    """
    loa_aft  = -3000   # LOA 艉端
    loa_fwd  = 180000  # LOA 艏端
    midbody_start = 35000   # 平行中体起始
    midbody_end   = 148000  # 平行中体结束

    if midbody_start <= x <= midbody_end:
        return ship_half_b
    elif x > midbody_end:
        # 艏部：抛物线过渡到 0
        frac = (x - midbody_end) / (loa_fwd - midbody_end)  # 0→1
        frac = max(0, min(1, frac))
        # 使用 1/4 椭圆线型
        return ship_half_b * math.sqrt(1 - frac**2)
    else:
        # 艉部：抛物线过渡
        frac = (midbody_start - x) / (midbody_start - loa_aft)  # 0→1
        frac = max(0, min(1, frac))
        return ship_half_b * math.sqrt(1 - frac**2)

def hull_profile_points(num_points=200):
    """生成船体水线面轮廓点（port半宽）"""
    pts_starboard = []
    pts_port = []
    for i in range(num_points + 1):
        x = -3000 + i * (183000 / num_points)  # LOA 范围
        hb = waterline_half_breath(x)
        pts_starboard.append((x, hb))
        pts_port.append((x, -hb))
    # 合并：沿 starboard 从艉到艏，再沿 port 从艏到艉
    return pts_starboard + pts_port[::-1]

def profile_bottom_height(x):
    """计算船底距基线的高度（简化）"""
    # 底部在大部分区域是平的（基线=0），艏艉升高
    if 30000 <= x <= 160000:
        return 0
    elif x > 160000:
        frac = (x - 160000) / 20000
        return 0 + frac * 3000  # 艏部升高
    else:
        frac = (30000 - x) / 30000
        return 0 + frac * 2000  # 艉部升高

# ============================================================
# 各视图布局偏移量
# ============================================================
PLAN_Y_OFFSET    = 0       # 平面图：y方向偏移
PROFILE_Y_OFFSET = -40000  # 纵剖面图：y方向偏移
SECTION_X_OFFSET = 100000  # 横剖面图：x方向偏移（从AP算）
SECTION_VIEW_X   = 210000  # 横剖面图放置位置的x坐标

# ============================================================
# 1. 平面图 (Tank Top Level)
# ============================================================
print("绘制平面图...")

# 1.1 船体水线轮廓
hull_pts = hull_profile_points(200)
msp.add_lwpolyline(hull_pts, close=True, dxfattribs={"layer": "HULL"})

# 1.2 中纵舱壁（用中心线表示）
line_seg(msp, -3000, 0, 180000, 0, "CENTERLINE")

# 1.3 横向舱壁（货油舱区域）
for x0, x1, tank_no in COT_BOUNDS:
    line_seg(msp, x0, -HALF_B, x0, HALF_B, "BULKHEAD")
    # 后舱壁也画（最后一个舱的前壁 = 下一个舱的后壁）
line_seg(msp, COT_END, -HALF_B, COT_END, HALF_B, "BULKHEAD")  # 最前舱壁
line_seg(msp, COT_START, -HALF_B, COT_START, HALF_B, "BULKHEAD")  # 最后舱壁

# 1.4 泵舱壁
line_seg(msp, PUMP_START, -HALF_B, PUMP_START, HALF_B, "BULKHEAD")
line_seg(msp, PUMP_END, -HALF_B, PUMP_END, HALF_B, "BULKHEAD")

# 1.5 污油舱壁
line_seg(msp, SLOP_START, -HALF_B, SLOP_START, HALF_B, "BULKHEAD")
line_seg(msp, SLOP_END, -HALF_B, SLOP_END, HALF_B, "BULKHEAD")

# 1.6 中纵舱壁全通（货舱区内）
line_seg(msp, COT_START, 0, COT_END, 0, "CENTERLINE")

# 1.7 机舱边界
line_seg(msp, ER_START, -HALF_B, ER_START, HALF_B, "BULKHEAD")

# 1.8 舱室编号文字
for x0, x1, tank_no in COT_BOUNDS:
    cx = (x0 + x1) / 2
    # 右舷（+y）
    add_text(msp, cx, HALF_B / 2, f"COT {tank_no}P", height=600, layer="TEXT")
    # 左舷（-y）
    add_text(msp, cx, -HALF_B / 2, f"COT {tank_no}S", height=600, layer="TEXT")

# 1.9 污油舱标注
cx_slop = (SLOP_START + SLOP_END) / 2
add_text(msp, cx_slop, HALF_B / 2, "SLOP P", height=550, layer="TEXT")
add_text(msp, cx_slop, -HALF_B / 2, "SLOP S", height=550, layer="TEXT")

# 1.10 泵舱标注
cx_pump = (PUMP_START + PUMP_END) / 2
add_text(msp, cx_pump, 0, "PUMP\nROOM", height=600, layer="TEXT")

# 1.11 机舱标注
cx_er = (ER_START + ER_END) / 2
add_text(msp, cx_er, 0, "ENGINE\nROOM", height=600, layer="TEXT")

# 1.12 艏部标注
add_text(msp, (COT_END + FP) / 2, 0, "FORE\nPEAK", height=500, layer="TEXT")

# 1.13 吸油井位置标记（每个货油舱后部舷侧）
for x0, x1, tank_no in COT_BOUNDS:
    # 吸油井位于每舱后部、靠近舷侧
    well_x = x0 + 2500  # 距后舱壁2.5m
    well_y_p = HALF_B - 3000  # 距舷侧3m
    well_y_s = -HALF_B + 3000
    # 小方框标记吸油井
    well_size = 600
    polyline_rect(msp, well_x - well_size, well_y_p - well_size//2,
                  well_x + well_size, well_y_p + well_size//2, "ANNOTATION")
    polyline_rect(msp, well_x - well_size, well_y_s - well_size//2,
                  well_x + well_size, well_y_s + well_size//2, "ANNOTATION")

# 1.14 图名
PLAN_TITLE_Y = HALF_B + 5000
add_text(msp, (COT_START + COT_END) / 2, PLAN_TITLE_Y,
         "PLAN VIEW — TANK TOP LEVEL  (俯视图 — 内底板平面)",
         height=800, layer="TEXT")

# ============================================================
# 1A. 平面图尺寸标注
# ============================================================
DIM_Y = -HALF_B
dim_offsets = [3000, 5000, 7000, 9000]

# 货舱区总长
dimension_horiz(msp, COT_START, COT_END, DIM_Y, dim_offsets[0],
                f"Cargo Area = {CARGO_LEN/1000:.0f}m", "DIMENSION")

# 船宽
dimension_vert(msp, COT_START - 5000, -HALF_B, HALF_B, 5000,
               f"B = {B/1000:.1f}m", "DIMENSION")

# 每舱长度（标注第一舱）
dimension_horiz(msp, COT_BOUNDS[0][0], COT_BOUNDS[0][1], DIM_Y, dim_offsets[1],
                f"({TANK_LEN/1000:.2f}m)", "DIMENSION")

# AP 和 FP 标注
add_text(msp, 0, -HALF_B - dim_offsets[2], "AP", height=500, layer="TEXT")
add_text(msp, FP, -HALF_B - dim_offsets[2], "FP", height=500, layer="TEXT")
# LBP 标注
dimension_horiz(msp, 0, FP, DIM_Y, dim_offsets[3],
                f"LBP = {LBP/1000:.0f}m", "DIMENSION")


# ============================================================
# 2. 纵剖面图 (Profile View)
# ============================================================
print("绘制纵剖面图...")

# 剖面图以基线为基准，y坐标偏移到 PROFILE_Y_OFFSET
def y_prof(z):
    """将高度z转换到剖面图y坐标"""
    return PROFILE_Y_OFFSET + z

# 纵剖面图范围
PROF_X_MIN = -5000
PROF_X_MAX = LOA + 2000
PROF_X_RANGE = (PROF_X_MIN, PROF_X_MAX)

# 2.1 基线
line_seg(msp, PROF_X_MIN, y_prof(0), PROF_X_MAX, y_prof(0), "CENTERLINE")

# 2.2 船底轮廓
bottom_pts = []
for i in range(200):
    x = PROF_X_MIN + i * (PROF_X_MAX - PROF_X_MIN) / 199
    z_bottom = profile_bottom_height(x)
    bottom_pts.append((x, y_prof(z_bottom)))
msp.add_lwpolyline(bottom_pts, dxfattribs={"layer": "HULL"})

# 2.3 内底板
line_seg(msp, PUMP_START, y_prof(DB_H), COT_END, y_prof(DB_H), "HIDDEN")

# 2.4 主甲板
deck_pts = []
for i in range(200):
    x = PROF_X_MIN + i * (PROF_X_MAX - PROF_X_MIN) / 199
    # 简化：主甲板近似在 D 高度，艏部略升高
    z_deck = D
    if x > 150000:
        z_deck = D + (x - 150000) * 0.02  # 艏部甲板升高
    deck_pts.append((x, y_prof(z_deck)))
msp.add_lwpolyline(deck_pts, dxfattribs={"layer": "HULL"})

# 2.5 设计吃水线
line_seg(msp, 0, y_prof(T_design), FP, y_prof(T_design), "ANNOTATION")
add_text_left(msp, FP + 1500, y_prof(T_design), f"T={T_design/1000:.1f}m", height=400, layer="ANNOTATION")

# 2.6 货舱区横舱壁投影（竖线）
for x0, x1, tank_no in COT_BOUNDS:
    line_seg(msp, x0, y_prof(0), x0, y_prof(D), "BULKHEAD")
line_seg(msp, COT_END, y_prof(0), COT_END, y_prof(D), "BULKHEAD")

# 2.7 舱室编号（剖面）
for x0, x1, tank_no in COT_BOUNDS:
    cx = (x0 + x1) / 2
    add_text(msp, cx, y_prof(D / 2), f"COT{tank_no}", height=450, layer="TEXT", rotation=90)

# 2.8 泵舱、污油舱、机舱标记
add_text(msp, (PUMP_START + PUMP_END) / 2, y_prof(D / 2), "PUMP ROOM", height=450,
         layer="TEXT", rotation=90)
add_text(msp, (SLOP_START + SLOP_END) / 2, y_prof(D / 2), "SLOP", height=400,
         layer="TEXT", rotation=90)
add_text(msp, (ER_START + ER_END) / 2, y_prof(D / 2), "ENGINE ROOM", height=450,
         layer="TEXT", rotation=90)

# 2.9 泵舱/污油舱边界
line_seg(msp, PUMP_START, y_prof(0), PUMP_START, y_prof(D), "BULKHEAD")
line_seg(msp, PUMP_END, y_prof(0), PUMP_END, y_prof(D), "BULKHEAD")
line_seg(msp, SLOP_END, y_prof(0), SLOP_END, y_prof(D), "BULKHEAD")

# 2.10 肋位标记（每隔一定距离）
for frame_no in range(0, 181, 10):
    x = frame_no * 1000  # 假设肋距 1000mm（标准值）
    if 0 <= x <= FP:
        line_seg(msp, x, y_prof(0), x, y_prof(-2500), "DIMENSION")
        add_text(msp, x, y_prof(-3500), f"Fr.{frame_no}", height=350, layer="DIMENSION")

# 2.11 图名
PROF_TITLE_Y = y_prof(D) + 6000
add_text(msp, (PROF_X_MIN + PROF_X_MAX) / 2, PROF_TITLE_Y,
         "PROFILE VIEW — CARGO TANK ARRANGEMENT  (纵剖面图)",
         height=800, layer="TEXT")

# 纵剖面图尺寸标注
PROF_DIM_Y = y_prof(-5000)
dimension_horiz(msp, COT_START, COT_END, PROF_DIM_Y, 3000,
                f"Cargo Area = {CARGO_LEN/1000:.0f}m", "DIMENSION")
dimension_vert(msp, COT_START - 8000, y_prof(0), y_prof(D), 5000,
               f"D = {D/1000:.2f}m", "DIMENSION")
dimension_vert(msp, COT_START - 13000, y_prof(0), y_prof(DB_H), 5000,
               f"DB={DB_H/1000:.2f}m", "DIMENSION")


# ============================================================
# 3. 横剖面图 (Midship Section)  — 典型货油舱截面
# ============================================================
print("绘制横剖面图...")

SEC_X = SECTION_VIEW_X            # 截面图中心x
SEC_CY = 0                        # 截面图中心y（船体中心线）
SEC_HALF_B = HALF_B               # 半宽
SEC_D = D                         # 型深
SEC_DB = DB_H                     # 双层底
SEC_BILGE_R = 2000                # 舭部半径
SEC_DECK_CAMBER = 400             # 甲板梁拱（简化）

# 截面轮廓点（右舷，从中心线底部向上，再向外，再向下）
def midship_section_points(half_b=SEC_HALF_B, d=SEC_D, db=SEC_DB, bilge_r=SEC_BILGE_R):
    """生成典型横剖面轮廓（右舷半边）"""
    pts = []
    # 从中心线底部开始
    pts.append((SEC_X, SEC_CY - d))  # 船底中心
    # 平底到舭部起点
    flat_bottom_end = half_b - bilge_r
    pts.append((SEC_X + flat_bottom_end, SEC_CY - d))
    # 舭部圆弧（用多段折线近似）
    n_arc = 8
    for i in range(1, n_arc + 1):
        angle = math.pi / 2 * i / n_arc  # 0 → π/2
        dx = flat_bottom_end + bilge_r * math.sin(angle)
        dz = -d + bilge_r * (1 - math.cos(angle))
        pts.append((SEC_X + dx, SEC_CY + dz))
    # 舷侧直壁向上到主甲板
    pts.append((SEC_X + half_b, SEC_CY - d + db + bilge_r))  # 舭部顶
    pts.append((SEC_X + half_b, SEC_CY + SEC_DECK_CAMBER))  # 甲板边线
    # 甲板（有梁拱）
    pts.append((SEC_X, SEC_CY + SEC_DECK_CAMBER + 200))  # 中心线甲板（略高）
    return pts

# 3.1 右舷截面轮廓
sb_pts = midship_section_points()
msp.add_lwpolyline(sb_pts, close=False, dxfattribs={"layer": "HULL"})

# 3.2 左舷截面轮廓（镜像）
port_pts = [(2 * SEC_X - x, y) for x, y in sb_pts]
msp.add_lwpolyline(port_pts, close=False, dxfattribs={"layer": "HULL"})

# 3.3 内底板
inner_bottom_y = SEC_CY - SEC_D + SEC_DB
line_seg(msp, SEC_X - SEC_HALF_B + 1500, inner_bottom_y,
         SEC_X + SEC_HALF_B - 1500, inner_bottom_y, "HIDDEN")

# 3.4 中纵舱壁（从内底板到主甲板）
deck_center_y = SEC_CY + SEC_DECK_CAMBER + 200
line_seg(msp, SEC_X, inner_bottom_y, SEC_X, deck_center_y, "CENTERLINE")

# 3.5 中心线标记
add_text(msp, SEC_X, SEC_CY - SEC_D - 2000, "C_L", height=500, layer="TEXT")

# 3.6 吸油井标记（左右舷）
# 左舷吸油井（在左货油舱后部舷侧）
well_x_l = SEC_X - SEC_HALF_B + 4000
well_x_r = SEC_X + SEC_HALF_B - 4000
well_width = 1500
well_depth = 800
well_bottom_y = inner_bottom_y - well_depth

# 左舷吸油井
well_pts_l = [
    (well_x_l - well_width / 2, inner_bottom_y),
    (well_x_l - well_width / 2, well_bottom_y),
    (well_x_l + well_width / 2, well_bottom_y),
    (well_x_l + well_width / 2, inner_bottom_y),
]
msp.add_lwpolyline(well_pts_l, close=True, dxfattribs={"layer": "ANNOTATION"})

# 右舷吸油井
well_pts_r = [
    (well_x_r - well_width / 2, inner_bottom_y),
    (well_x_r - well_width / 2, well_bottom_y),
    (well_x_r + well_width / 2, well_bottom_y),
    (well_x_r + well_width / 2, inner_bottom_y),
]
msp.add_lwpolyline(well_pts_r, close=True, dxfattribs={"layer": "ANNOTATION"})

# 吸油井标注
add_text(msp, well_x_l, well_bottom_y - 1200, "SUCTION\nWELL (S)", height=400, layer="TEXT")
add_text(msp, well_x_r, well_bottom_y - 1200, "SUCTION\nWELL (P)", height=400, layer="TEXT")

# 3.7 货油舱区域标注（阴影示意）
tank_label_y = SEC_CY - SEC_D / 2
add_text(msp, SEC_X - SEC_HALF_B / 2, tank_label_y, "COT (S)", height=500, layer="TEXT")
add_text(msp, SEC_X + SEC_HALF_B / 2, tank_label_y, "COT (P)", height=500, layer="TEXT")

# 3.8 双层底区域标注
add_text(msp, SEC_X, SEC_CY - SEC_D + SEC_DB / 2, "DOUBLE BOTTOM", height=400,
         layer="TEXT", rotation=0)

# 3.9 边舱标注
wing_label_y = SEC_CY - SEC_D + SEC_DB + 4000
add_text(msp, SEC_X - SEC_HALF_B + 2000, wing_label_y, "WING\nBALLAST\nTANK", height=350,
         layer="TEXT")
add_text(msp, SEC_X + SEC_HALF_B - 2000, wing_label_y, "WING\nBALLAST\nTANK", height=350,
         layer="TEXT")

# 3.10 图名
SECTION_TITLE_Y = SEC_CY + SEC_DECK_CAMBER + 5000
add_text(msp, SEC_X, SECTION_TITLE_Y,
         "TYPICAL MIDSHIP SECTION  (典型横剖面图)",
         height=800, layer="TEXT")

# 3.11 横剖面尺寸标注
dim_x_base = SEC_X + SEC_HALF_B + 5000
dimension_vert(msp, dim_x_base, SEC_CY - SEC_D, SEC_CY, 2000,
               f"D={SEC_D/1000:.2f}m", "DIMENSION")
dimension_vert(msp, dim_x_base + 5000, SEC_CY - SEC_D, inner_bottom_y, 2000,
               f"DB={SEC_DB/1000:.2f}m", "DIMENSION")
dimension_horiz(msp, SEC_X, SEC_X + SEC_HALF_B, SEC_CY - SEC_D - 4000, 3000,
                f"B/2={SEC_HALF_B/1000:.1f}m", "DIMENSION")

# 吸油井尺寸标注
dimension_horiz(msp, well_x_r - well_width / 2, well_x_r + well_width / 2,
                well_bottom_y, 2000, f"{well_width}mm", "DIMENSION")
dimension_vert(msp, well_x_r + well_width / 2 + 1000,
               well_bottom_y, inner_bottom_y, 1500,
               f"{well_depth}mm", "DIMENSION")


# ============================================================
# 4. 图例 (Legend)
# ============================================================
LEGEND_X = 210000
LEGEND_Y = -35000

add_text(msp, LEGEND_X, LEGEND_Y, "LEGEND  (图例)", height=700, layer="TEXT",
         alignment=TextEntityAlignment.MIDDLE_LEFT)

legend_items = [
    ("HULL", "HULL", "船体轮廓"),
    ("BULKHEAD", "BULKHEAD", "横舱壁/舱壁"),
    ("CENTERLINE", "CENTERLINE", "中心线/中纵舱壁"),
    ("HIDDEN", "HIDDEN", "内底板/隐线"),
    ("DIMENSION", "DIMENSION", "尺寸标注"),
    ("ANNOTATION", "ANNOTATION", "标注/吸油井"),
]

for i, (layer, _, desc) in enumerate(legend_items):
    y = LEGEND_Y - 1000 - i * 900
    # 线示例
    line_seg(msp, LEGEND_X + 2000, y, LEGEND_X + 8000, y, layer)
    # 说明
    add_text(msp, LEGEND_X + 10000, y, f"{desc}", height=450, layer="TEXT",
             alignment=TextEntityAlignment.MIDDLE_LEFT)

# 标题栏区域
TITLE_X = 210000
TITLE_Y = -50000
title_lines = [
    "33000DWT DUAL-FUEL PRODUCT OIL TANKER",
    "CARGO TANK ARRANGEMENT",
    "Drawn: CAD Engineer Agent  |  Date: 2026-06-06",
    "Scale: 1:1 (mm)  |  Unit: mm",
]
for i, line in enumerate(title_lines):
    add_text(msp, TITLE_X, TITLE_Y - i * 1000, line, height=550, layer="TEXT",
             alignment=TextEntityAlignment.MIDDLE_LEFT)

# 规范/参数备注
notes_x = 210000
notes_y = TITLE_Y - 5000
notes = [
    f"Principal Particulars:",
    f"  LOA={LOA/1000:.2f}m  LBP={LBP/1000:.2f}m  B={B/1000:.2f}m  D={D/1000:.2f}m",
    f"  d={T_design/1000:.2f}m  DWT=33,000t",
    f"  Cargo Tanks: {N_TANKS*2} (CO) + 2 (SLOP) = {N_TANKS*2+2} tanks",
    f"  Pump Systems: 22 independent sets",
    f"  Max Loading Rate: 2,400 m3/h (6 pumps x 400 m3/h)",
]
for i, note in enumerate(notes):
    add_text(msp, notes_x, notes_y - i * 700, note, height=400, layer="TEXT",
             alignment=TextEntityAlignment.MIDDLE_LEFT)


# ============================================================
# 保存文件
# ============================================================
output_path = "cargo_tank_arrangement.dxf"
doc.saveas(output_path)
print(f"\n✅ DXF 文件已生成: {output_path}")
print(f"   图层: {list(LAYERS.keys())}")
print(f"   包含: 平面图 + 纵剖面图 + 横剖面图 + 尺寸标注 + 图例")
