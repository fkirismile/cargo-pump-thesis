#!/usr/bin/env python3
"""
渲染货仓结构图三视图为高清PNG
用于嵌入论文后转PDF
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Arc, Polygon
import numpy as np
import math
import os

# ============================================================
# 中文字体设置
# ============================================================
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti SC', 'STHeiti', 'SimHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 船舶参数 (同 DXF 脚本)
# ============================================================
LOA       = 180.0   # [m]
LBP       = 177.0   # [m]
B         = 28.0    # [m]
D         = 15.2    # [m]
T_design  = 9.5     # [m]
DB_H      = 2.0     # [m]
N_TANKS   = 10
CARGO_LEN = 135.0   # [m]
TANK_LEN  = CARGO_LEN / N_TANKS  # 13.5m
HALF_B    = B / 2   # 14.0m

# 区域定义 (距AP距离 [m])
ER_END     = 21.0
PUMP_END   = 27.0
SLOP_END   = 33.5
COT_START  = 33.5
COT_END    = COT_START + CARGO_LEN  # 168.5
FP         = LBP  # 177.0

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def waterline_half_breadth(x):
    """计算设计水线半宽 (抛物线艏艉+平行中体)"""
    loa_aft = -3.0
    loa_fwd = 180.0
    midbody_start = 35.0
    midbody_end = 148.0

    if midbody_start <= x <= midbody_end:
        return HALF_B
    elif x > midbody_end:
        frac = (x - midbody_end) / (loa_fwd - midbody_end)
        frac = max(0, min(1, frac))
        return HALF_B * math.sqrt(1 - frac**2)
    else:
        frac = (midbody_start - x) / (midbody_start - loa_aft)
        frac = max(0, min(1, frac))
        return HALF_B * math.sqrt(1 - frac**2)


def generate_plan_view():
    """生成平面图 (俯视图)"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 8), dpi=200)
    ax.set_aspect('equal')

    # 船体水线轮廓
    xs = np.linspace(-3, 180, 300)
    y_starboard = [waterline_half_breadth(x) for x in xs]
    y_port = [-y for y in y_starboard]

    ax.fill(np.concatenate([xs, xs[::-1]]),
            np.concatenate([y_starboard, y_port]),
            facecolor='#E8ECF1', edgecolor='#2C3E50', linewidth=1.5, zorder=1)

    # 中纵舱壁
    ax.axhline(y=0, color='#E67E22', linestyle='--', linewidth=1.0, zorder=3)
    ax.plot([COT_START, COT_END], [0, 0], color='#E67E22', linestyle='--', linewidth=1.5, zorder=3)

    # 横舱壁
    bulkhead_xs = [ER_END, PUMP_END, SLOP_END]  # 泵舱和污油舱边界
    for x in bulkhead_xs:
        ax.plot([x, x], [-HALF_B, HALF_B], color='#C0392B', linewidth=1.2, zorder=2)

    # 货油舱横舱壁
    for i in range(N_TANKS + 1):
        x = COT_START + i * TANK_LEN
        ax.plot([x, x], [-HALF_B, HALF_B], color='#C0392B', linewidth=1.2, zorder=2)

    # 机舱边界
    ax.plot([0, 0], [-HALF_B, HALF_B], color='#C0392B', linewidth=1.2, zorder=2)

    # 货油舱编号
    for i in range(N_TANKS):
        x0 = COT_START + i * TANK_LEN
        x1 = x0 + TANK_LEN
        cx = (x0 + x1) / 2
        tank_no = N_TANKS - i
        ax.text(cx, HALF_B * 0.45, f'COT{tank_no}P', ha='center', va='center',
                fontsize=7, fontweight='bold', color='#2C3E50')
        ax.text(cx, -HALF_B * 0.45, f'COT{tank_no}S', ha='center', va='center',
                fontsize=7, fontweight='bold', color='#2C3E50')

    # 污油舱标注
    cx_slop = (SLOP_END + COT_START) / 2
    ax.text(cx_slop, HALF_B * 0.3, 'SLOP P', ha='center', va='center',
            fontsize=6.5, style='italic', color='#7F8C8D')
    ax.text(cx_slop, -HALF_B * 0.3, 'SLOP S', ha='center', va='center',
            fontsize=6.5, style='italic', color='#7F8C8D')

    # 泵舱
    cx_pump = (PUMP_END + SLOP_END) / 2
    ax.text(cx_pump, 0, 'PUMP\nROOM', ha='center', va='center',
            fontsize=7, fontweight='bold', color='#8E44AD')

    # 机舱
    cx_er = ER_END / 2
    ax.text(cx_er, 0, 'ENGINE\nROOM', ha='center', va='center',
            fontsize=7, fontweight='bold', color='#8E44AD')

    # 艏部
    ax.text((COT_END + FP) / 2, 0, 'FORE\nPEAK', ha='center', va='center',
            fontsize=6.5, color='#7F8C8D')

    # 吸油井标记（小方框）
    for i in range(N_TANKS):
        x0 = COT_START + i * TANK_LEN
        well_x = x0 + 2.5
        well_y = HALF_B - 3.0
        rect = patches.Rectangle((well_x - 0.5, well_y - 0.3), 1.0, 0.6,
                                 facecolor='#3498DB', edgecolor='#2980B9', linewidth=0.8, zorder=4)
        ax.add_patch(rect)
        rect2 = patches.Rectangle((well_x - 0.5, -well_y - 0.3), 1.0, 0.6,
                                  facecolor='#3498DB', edgecolor='#2980B9', linewidth=0.8, zorder=4)
        ax.add_patch(rect2)

    # 尺寸标注
    # 货舱区总长
    ax.annotate('', xy=(COT_START, -HALF_B - 2.5), xytext=(COT_END, -HALF_B - 2.5),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.2))
    ax.text((COT_START + COT_END) / 2, -HALF_B - 3.3, f'Cargo Area = {CARGO_LEN:.0f} m',
            ha='center', va='top', fontsize=8, color='#27AE60', fontweight='bold')

    # LBP
    ax.annotate('', xy=(0, -HALF_B - 4.5), xytext=(FP, -HALF_B - 4.5),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.2))
    ax.text(LBP / 2, -HALF_B - 5.3, f'LBP = {LBP:.0f} m',
            ha='center', va='top', fontsize=8, color='#27AE60')

    # AP/FP 标记
    ax.text(0, -HALF_B - 6.0, 'AP', ha='center', fontsize=8, fontweight='bold')
    ax.text(FP, -HALF_B - 6.0, 'FP', ha='center', fontsize=8, fontweight='bold')

    # 船宽标注
    ax.annotate('', xy=(-5, -HALF_B), xytext=(-5, HALF_B),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.2))
    ax.text(-7, 0, f'B = {B:.1f} m', ha='center', va='center',
            fontsize=8, color='#27AE60', rotation=90)

    # 图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#C0392B', linewidth=1.5, label='横舱壁 (Bulkhead)'),
        Line2D([0], [0], color='#E67E22', linestyle='--', linewidth=1.5, label='中纵舱壁 (C.L. Bhd)'),
        patches.Patch(facecolor='#3498DB', edgecolor='#2980B9', label='吸油井 (Suction Well)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=6, framealpha=0.9)

    # 方向
    ax.text(170, -HALF_B + 1.5, '→ 船艏 (Fwd)', fontsize=7, color='#7F8C8D')

    ax.set_xlim(-10, 185)
    ax.set_ylim(-HALF_B - 8, HALF_B + 3)
    ax.set_xlabel('Longitudinal Position from AP [m]', fontsize=9)
    ax.set_ylabel('Breadth [m]', fontsize=9)
    ax.set_title('PLAN VIEW — Tank Top Level   (平面图 — 内底板平面)', fontsize=11, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.2)

    path = os.path.join(OUTPUT_DIR, 'fig_plan_view.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'✅ 平面图已保存: {path}')
    return path


def generate_profile_view():
    """生成纵剖面图"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 6), dpi=200)
    ax.set_aspect('equal')

    # 船底轮廓 (简化)
    bottom_xs = np.linspace(-3, 180, 200)
    bottom_zs = []
    for x in bottom_xs:
        if 30 <= x <= 160:
            bottom_zs.append(0)
        elif x > 160:
            frac = (x - 160) / 20
            bottom_zs.append(frac * 3.0)
        else:
            frac = (30 - x) / 34
            bottom_zs.append(frac * 2.0)

    ax.fill_between(bottom_xs, bottom_zs, alpha=0.15, color='#2C3E50')
    ax.plot(bottom_xs, bottom_zs, color='#2C3E50', linewidth=1.5)

    # 基线
    ax.axhline(y=0, color='#E67E22', linestyle='--', linewidth=0.8)
    ax.text(-5, 0.2, 'BL', fontsize=7, color='#E67E22', va='bottom')

    # 内底板
    ax.plot([PUMP_END, COT_END], [DB_H, DB_H], color='#7F8C8D', linestyle='--', linewidth=1.0)
    ax.text(COT_END + 2, DB_H, f'Inner Bottom (BL+{DB_H:.1f}m)', fontsize=6.5, color='#7F8C8D', va='center')

    # 主甲板
    deck_zs = []
    for x in bottom_xs:
        z = D
        if x > 150:
            z = D + (x - 150) * 0.02
        deck_zs.append(z)
    ax.plot(bottom_xs, deck_zs, color='#2C3E50', linewidth=1.5)
    ax.text(175, D + 0.3, f'Main Deck (D={D:.1f}m)', fontsize=7, color='#2C3E50', va='bottom')

    # 设计吃水
    ax.axhline(y=T_design, color='#3498DB', linestyle='-', linewidth=1.0, alpha=0.7)
    ax.text(175, T_design, f'Design Draft T={T_design:.1f}m', fontsize=6.5, color='#3498DB', va='bottom')

    # 船体填充
    ax.fill_between(bottom_xs, bottom_zs, deck_zs, alpha=0.05, color='#2C3E50')

    # 用蓝色填充水下部分
    water_xs = np.linspace(0, LBP, 100)
    water_bottom = [0 if (30 <= x <= 160) else (0 if x > 160 else 0) for x in water_xs]
    ax.fill_between(water_xs, water_bottom, T_design, alpha=0.08, color='#3498DB')

    # 横舱壁投影
    bulkhead_xs_all = [ER_END, PUMP_END, SLOP_END]
    for x in bulkhead_xs_all:
        ax.plot([x, x], [0, D], color='#C0392B', linewidth=1.0, alpha=0.7)

    for i in range(N_TANKS + 1):
        x = COT_START + i * TANK_LEN
        ax.plot([x, x], [0, D], color='#C0392B', linewidth=1.0, alpha=0.7)

    # 舱室编号
    for i in range(N_TANKS):
        x0 = COT_START + i * TANK_LEN
        cx = (x0 + x0 + TANK_LEN) / 2
        tank_no = N_TANKS - i
        ax.text(cx, D * 0.6, f'COT{tank_no}', ha='center', va='center',
                fontsize=7, fontweight='bold', color='#2C3E50', rotation=90)

    # 机舱/泵舱/污油舱
    ax.text(ER_END / 2, D * 0.5, 'ENGINE ROOM', ha='center', fontsize=7, color='#8E44AD', rotation=90)
    ax.text((PUMP_END + SLOP_END) / 2, D * 0.5, 'PUMP ROOM', ha='center', fontsize=7, color='#8E44AD', rotation=90)
    ax.text((SLOP_END + COT_START) / 2, D * 0.5, 'SLOP', ha='center', fontsize=7, color='#7F8C8D', rotation=90)

    # 肋位标记
    for fn in range(0, 181, 20):
        x = fn
        if 0 <= x <= FP:
            ax.plot([x, x], [-1.0, -2.0], color='#95A5A6', linewidth=0.6)
            ax.text(x, -2.5, f'Fr.{fn}', ha='center', fontsize=5.5, color='#7F8C8D')

    # 货舱区范围
    ax.axvspan(COT_START, COT_END, alpha=0.04, color='#E74C3C')
    ax.annotate('Cargo Tank Area', xy=((COT_START + COT_END) / 2, D + 1.2),
                ha='center', fontsize=8, color='#E74C3C', fontweight='bold')

    # 尺寸
    ax.annotate('', xy=(COT_START, -4), xytext=(COT_END, -4),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.2))
    ax.text((COT_START + COT_END) / 2, -4.8, f'{CARGO_LEN:.0f} m', ha='center',
            fontsize=8, color='#27AE60')

    ax.annotate('', xy=(COT_START - 10, 0), xytext=(COT_START - 10, D),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.2))
    ax.text(COT_START - 13, D / 2, f'D={D:.1f}m', ha='center', va='center',
            fontsize=8, color='#27AE60', rotation=90)

    ax.set_xlim(-10, 185)
    ax.set_ylim(-6, D + 4)
    ax.set_xlabel('Longitudinal Position from AP [m]', fontsize=9)
    ax.set_ylabel('Height from Baseline [m]', fontsize=9)
    ax.set_title('PROFILE VIEW — Cargo Tank Arrangement   (纵剖面图)', fontsize=11, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.2)

    path = os.path.join(OUTPUT_DIR, 'fig_profile_view.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'✅ 纵剖面图已保存: {path}')
    return path


def generate_midship_section():
    """生成典型横剖面图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 9), dpi=200)
    ax.set_aspect('equal')

    HALF_B_SECTION = HALF_B
    DB = DB_H
    BILGE_R = 2.0
    DECK_CAMBER = 0.4

    # 右舷截面轮廓
    sb_pts_x = []
    sb_pts_y = []

    # 中心线底部
    sb_pts_x.append(0); sb_pts_y.append(-D)
    # 平底
    flat_end = HALF_B_SECTION - BILGE_R
    sb_pts_x.append(flat_end); sb_pts_y.append(-D)
    # 舭部圆弧
    n_arc = 12
    for i in range(1, n_arc + 1):
        angle = math.pi / 2 * i / n_arc
        dx = flat_end + BILGE_R * math.sin(angle)
        dy = -D + BILGE_R * (1 - math.cos(angle))
        sb_pts_x.append(dx); sb_pts_y.append(dy)
    # 舷侧向上
    sb_pts_x.append(HALF_B_SECTION); sb_pts_y.append(-D + DB + BILGE_R)
    sb_pts_x.append(HALF_B_SECTION); sb_pts_y.append(DECK_CAMBER)
    # 甲板边线到中心
    sb_pts_x.append(0); sb_pts_y.append(DECK_CAMBER + 0.3)

    # 右舷轮廓
    ax.plot(sb_pts_x, sb_pts_y, color='#2C3E50', linewidth=1.8)
    # 左舷轮廓 (镜像)
    port_pts_x = [-x for x in sb_pts_x]
    ax.plot(port_pts_x, sb_pts_y, color='#2C3E50', linewidth=1.8)

    # 填充截面
    all_x = sb_pts_x + port_pts_x[::-1]
    all_y = sb_pts_y + sb_pts_y[::-1]
    ax.fill(all_x, all_y, alpha=0.08, color='#2C3E50')

    # 内底板
    inner_bottom_y = -D + DB
    ax.plot([-HALF_B_SECTION + 1.5, HALF_B_SECTION - 1.5], [inner_bottom_y, inner_bottom_y],
            color='#7F8C8D', linestyle='--', linewidth=1.2)
    ax.text(HALF_B_SECTION - 2, inner_bottom_y + 0.3, f'Inner Bottom\n(BL+{DB:.1f}m)',
            fontsize=6.5, color='#7F8C8D', va='bottom', ha='center')

    # 中纵舱壁
    ax.plot([0, 0], [inner_bottom_y, DECK_CAMBER + 0.3], color='#E67E22',
            linestyle='--', linewidth=1.5)

    # 中心线标记
    ax.plot([0, 0], [-D - 0.5, -D - 1.8], color='#2C3E50', linewidth=1.0)
    ax.text(0, -D - 2.2, 'C_L', ha='center', fontsize=8, fontweight='bold')

    # 基线
    ax.axhline(y=-D, color='#95A5A6', linewidth=0.5, linestyle=':')
    ax.text(-HALF_B_SECTION + 1, -D + 0.2, 'Baseline', fontsize=6, color='#95A5A6')

    # 设计吃水
    ax.plot([-HALF_B_SECTION, HALF_B_SECTION], [-D + T_design, -D + T_design],
            color='#3498DB', linewidth=0.8, alpha=0.6)
    ax.text(HALF_B_SECTION - 2, -D + T_design + 0.3, f'T={T_design:.1f}m',
            fontsize=6.5, color='#3498DB')

    # 吸油井 (右舷/左舷)
    well_w = 1.0
    well_d = 0.8
    well_bottom_y = inner_bottom_y - well_d

    for side, well_cx in [('P', HALF_B_SECTION - 3.5), ('S', -HALF_B_SECTION + 3.5)]:
        well_rect = patches.Rectangle((well_cx - well_w / 2, well_bottom_y), well_w, well_d,
                                      facecolor='#3498DB', edgecolor='#2980B9', linewidth=1.2, alpha=0.7)
        ax.add_patch(well_rect)
        # 标注
        ax.text(well_cx, well_bottom_y - 1.0, f'Suction Well ({side})',
                ha='center', fontsize=7, fontweight='bold', color='#2980B9')
        # 防击板示意
        ax.plot([well_cx - 0.4, well_cx + 0.4], [well_bottom_y + 0.3, well_bottom_y + 0.3],
                color='#E74C3C', linewidth=2)

    # 货舱标注
    ax.text(HALF_B_SECTION / 2, (inner_bottom_y + DECK_CAMBER) / 2 - 2,
            'CARGO OIL\nTANK (P)', ha='center', fontsize=9, fontweight='bold', color='#2C3E50')
    ax.text(-HALF_B_SECTION / 2, (inner_bottom_y + DECK_CAMBER) / 2 - 2,
            'CARGO OIL\nTANK (S)', ha='center', fontsize=9, fontweight='bold', color='#2C3E50')

    # 双层底
    ax.text(0, -D + DB / 2, 'DOUBLE BOTTOM', ha='center', fontsize=7, color='#7F8C8D')

    # 边压载舱
    ax.text(HALF_B_SECTION - 1.8, -D + DB + 3.5, 'WING\nBALLAST\nTANK',
            ha='center', fontsize=6, color='#95A5A6', style='italic')
    ax.text(-HALF_B_SECTION + 1.8, -D + DB + 3.5, 'WING\nBALLAST\nTANK',
            ha='center', fontsize=6, color='#95A5A6', style='italic')

    # 尺寸标注
    # 型深
    ax.annotate('', xy=(HALF_B_SECTION + 3, -D), xytext=(HALF_B_SECTION + 3, 0),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.2))
    ax.text(HALF_B_SECTION + 4.5, -D / 2, f'D = {D:.2f} m', ha='center', va='center',
            fontsize=9, color='#27AE60', fontweight='bold', rotation=90)

    # 双层底
    ax.annotate('', xy=(HALF_B_SECTION + 5.5, -D), xytext=(HALF_B_SECTION + 5.5, inner_bottom_y),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.0))
    ax.text(HALF_B_SECTION + 7, (-D + inner_bottom_y) / 2, f'DB={DB:.1f}m',
            ha='center', va='center', fontsize=7, color='#27AE60', rotation=90)

    # 半宽
    ax.annotate('', xy=(0, -D - 3.5), xytext=(HALF_B_SECTION, -D - 3.5),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.2))
    ax.text(HALF_B_SECTION / 2, -D - 4.3, f'B/2 = {HALF_B_SECTION:.1f} m',
            ha='center', fontsize=9, color='#27AE60')

    # 吸油井尺寸
    well_cx_r = HALF_B_SECTION - 3.5
    ax.annotate('', xy=(well_cx_r - well_w / 2, well_bottom_y - 1.8),
                xytext=(well_cx_r + well_w / 2, well_bottom_y - 1.8),
                arrowprops=dict(arrowstyle='<->', color='#E74C3C', lw=0.8))
    ax.text(well_cx_r, well_bottom_y - 2.3, f'{well_w*1000:.0f}mm', ha='center',
            fontsize=6, color='#E74C3C')

    ax.annotate('', xy=(well_cx_r + well_w / 2 + 0.5, well_bottom_y),
                xytext=(well_cx_r + well_w / 2 + 0.5, inner_bottom_y),
                arrowprops=dict(arrowstyle='<->', color='#E74C3C', lw=0.8))
    ax.text(well_cx_r + well_w / 2 + 1.2, (well_bottom_y + inner_bottom_y) / 2,
            f'{well_d*1000:.0f}mm', ha='center', va='center', fontsize=6, color='#E74C3C', rotation=90)

    ax.set_xlim(-HALF_B_SECTION - 10, HALF_B_SECTION + 10)
    ax.set_ylim(-D - 6, DECK_CAMBER + 3)
    ax.set_xlabel('Breadth [m]', fontsize=9)
    ax.set_ylabel('Height from Baseline [m]', fontsize=9)
    ax.set_title('TYPICAL MIDSHIP SECTION   (典型横剖面图)', fontsize=11, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.2)

    path = os.path.join(OUTPUT_DIR, 'fig_midship_section.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'✅ 横剖面图已保存: {path}')
    return path


if __name__ == '__main__':
    fig_dir = os.path.join(OUTPUT_DIR, 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    # 将输出路径改到 figures 子目录
    original_join = os.path.join
    def join_with_figures(base, fname):
        if base == OUTPUT_DIR and fname.startswith('fig_'):
            return os.path.join(fig_dir, fname)
        return original_join(base, fname)
    os.path.join = join_with_figures

    p1 = generate_plan_view()
    p2 = generate_profile_view()
    p3 = generate_midship_section()

    print(f'\n✅ 全部三视图已生成:')
    print(f'   图1 (平面图):  {p1}')
    print(f'   图2 (纵剖面图): {p2}')
    print(f'   图3 (横剖面图): {p3}')
    print(f'\n下一步: 将PNG图片嵌入论文，再用 any2pdf 转PDF')
