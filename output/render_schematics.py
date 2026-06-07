#!/usr/bin/env python3
"""渲染图2和图3为PNG，替换ASCII示意图"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti SC', 'STHeiti', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_fig2_pump_schematic():
    """图2: 舱内管路原理示意图"""
    fig, ax = plt.subplots(1, 1, figsize=(7, 10), dpi=200)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-1, 17)
    ax.set_aspect('equal')
    ax.axis('off')

    # 颜色
    steel_color = '#7F8C8D'
    pipe_color = '#2980B9'
    pump_color = '#C0392B'
    oil_color = '#E67E22'
    text_color = '#2C3E50'

    def draw_box(ax, x0, y0, w, h, color, label, lw=1.5):
        rect = patches.FancyBboxPatch((x0-w/2, y0-h/2), w, h,
            boxstyle="round,pad=0.1", facecolor=color, edgecolor='black',
            linewidth=lw, alpha=0.85)
        ax.add_patch(rect)
        if label:
            ax.text(x0, y0, label, ha='center', va='center', fontsize=9,
                    fontweight='bold', color='white')

    # 基线
    ax.axhline(y=0, color='black', linewidth=1.5)
    ax.text(-2.8, 0.3, 'Baseline (BL)', fontsize=7, color=text_color)

    # 船底板
    ax.fill_between([-3, 3], 0, 0.5, color=steel_color, alpha=0.3)
    ax.text(2.8, 0.7, 'Bottom Shell', fontsize=6, color=steel_color, ha='right')

    # 内底板
    ax.plot([-3, 3], [2, 2], color=steel_color, linewidth=2, linestyle='-')
    ax.text(-2.8, 2.3, f'Inner Bottom (BL+2.0m)', fontsize=7, color=steel_color)

    # 双层底标记
    ax.annotate('', xy=(2.5, 0.5), xytext=(2.5, 2),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.0))
    ax.text(2.8, 1.25, 'DB\n2.0m', ha='center', va='center', fontsize=7, color='#27AE60')

    # 货油舱区域
    ax.fill_between([-2.8, 2.8], 2, 15.2, color=oil_color, alpha=0.06)
    ax.text(0, 9, 'CARGO OIL TANK', ha='center', fontsize=11, fontweight='bold',
            color=oil_color, alpha=0.4)

    # 主甲板
    ax.plot([-3, 3], [15.2, 15.2], color=steel_color, linewidth=2.5)
    ax.text(-2.8, 15.5, f'Main Deck (D=15.2m)', fontsize=7, color=steel_color)

    # 吸油井
    well_x = 0
    well_top = 2.0
    well_bottom = 1.1
    well_w = 1.2
    well_rect = patches.FancyBboxPatch((-well_w/2, well_bottom), well_w, well_top-well_bottom,
        boxstyle="round,pad=0.05", facecolor='#3498DB', edgecolor='#2980B9',
        linewidth=1.5, alpha=0.4)
    ax.add_patch(well_rect)
    ax.text(well_x, well_bottom + 0.4, 'Suction\nWell', ha='center', va='center',
            fontsize=7, fontweight='bold', color='#2980B9')

    # 钟形吸口
    bell_x = [-0.3, 0.3, 0.35, -0.35]
    bell_y = [well_top, well_top, well_top+0.3, well_top+0.3]
    ax.fill(bell_x, bell_y, facecolor=pipe_color, edgecolor='black', linewidth=1)

    # 吸入管 DN300
    ax.plot([0, 0], [well_top+0.3, 5.5], color=pipe_color, linewidth=6)
    ax.text(0.6, 4, 'Suction\nPipe\nDN300', ha='left', va='center', fontsize=7, color=pipe_color)

    # 深井泵
    pump_center_y = 6.8
    pump_h = 1.5
    pump_w = 1.0
    draw_box(ax, 0, pump_center_y, pump_w, pump_h, pump_color, 'Deepwell\nPump\n2-3 Stage')

    # 排出立管 DN250
    ax.plot([0, 0], [pump_center_y + pump_h/2, 14.0], color='#E74C3C', linewidth=5)
    ax.text(0.6, 11, 'Discharge\nRiser\nDN250', ha='left', va='center', fontsize=7, color='#E74C3C')

    # 检查标记
    ax.plot([0.2, 0.8], [pump_center_y+pump_h/2+0.5, pump_center_y+pump_h/2+0.5], color=pipe_color, linewidth=4)

    # 齿轮箱
    draw_box(ax, 0, 15.0, 0.9, 0.6, '#8E44AD', 'Gearbox', lw=1.2)

    # 防爆电机
    draw_box(ax, 0, 16.2, 1.2, 1.0, '#2C3E50', 'Motor\n185kW\nEx-d', lw=1.5)

    # 电机和齿轮箱连接
    ax.plot([0, 0], [15.0+0.3, 16.2-0.5], color='black', linewidth=2)

    # 甲板面穿舱
    ax.plot([-1.5, 1.5], [15.2, 15.2], color=steel_color, linewidth=2.5)
    ax.fill_between([-1.5, 1.5], 15.0, 15.2, color='white', alpha=0.8)

    # 止回阀标记
    ax.plot([0.3, 0.3], [13.5, 14.2], color='#E67E22', linewidth=6)
    ax.text(0.9, 13.8, 'Check\nValve', ha='left', va='center', fontsize=6, color='#E67E22')

    # 吸油井距船底标注
    ax.annotate('', xy=(-1.8, -0.1), xytext=(-1.8, well_bottom),
                arrowprops=dict(arrowstyle='<->', color='#E74C3C', lw=1.0))
    ax.text(-2.2, (0.5 + well_bottom)/2, '≥1.0m\n(≥0.5h)', ha='center', va='center',
            fontsize=6, color='#E74C3C')

    # 液面指示
    ax.plot([-2, 2], [5, 5], '--', color='#3498DB', linewidth=0.8, alpha=0.6)
    ax.text(-2, 5.3, 'Min. Liquid Level', fontsize=6, color='#3498DB')

    # 方向标注
    ax.annotate('Discharge to\nDeck Manifold', xy=(0, 16.8), fontsize=6,
                ha='center', color=text_color,
                arrowprops=dict(arrowstyle='->', color=text_color, lw=0.8))

    ax.set_title('Cabin Piping Schematic   (舱内管路原理示意图)', fontsize=11, fontweight='bold', pad=8)

    path = os.path.join(OUTPUT_DIR, 'figures', 'fig_cabin_piping.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'✅ 图2已保存: {path}')
    return path


def render_fig3_deck_piping():
    """图3: 甲板管路布置示意图"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 5), dpi=200)
    ax.set_xlim(-5, 145)
    ax.set_ylim(-6, 6)
    ax.set_aspect('equal')
    ax.axis('off')

    text_color = '#2C3E50'
    pipe_p = '#2980B9'
    pipe_s = '#E74C3C'
    manifold_c = '#8E44AD'

    # 甲板步桥
    ax.fill_between([0, 140], -0.5, 0.5, color='#BDC3C7', alpha=0.5)
    ax.text(70, 0, 'Centerline Walkway (甲板步桥)', ha='center', va='center',
            fontsize=8, color=text_color, fontweight='bold')
    ax.plot([0, 140], [-0.5, -0.5], color=text_color, linewidth=1.5)
    ax.plot([0, 140], [0.5, 0.5], color=text_color, linewidth=1.5)

    # 左舷总管 DN400
    ax.plot([5, 135], [2.5, 2.5], color=pipe_p, linewidth=5)
    ax.text(-3, 2.5, 'Port Main\nDN400', ha='right', va='center', fontsize=7, color=pipe_p, fontweight='bold')

    # 右舷总管 DN400
    ax.plot([5, 135], [-2.5, -2.5], color=pipe_s, linewidth=5)
    ax.text(-3, -2.5, 'Stbd Main\nDN400', ha='right', va='center', fontsize=7, color=pipe_s, fontweight='bold')

    # 各舱泵排出支管
    for i in range(10):
        x = 12 + i * 12
        tank_no = 10 - i
        # 左舷
        ax.plot([x, x], [0.6, 2.5], color=pipe_p, linewidth=2.5)
        ax.text(x, 1.5, f'P{tank_no}', ha='center', fontsize=6, color=pipe_p, fontweight='bold')
        # 右舷
        ax.plot([x, x], [-0.6, -2.5], color=pipe_s, linewidth=2.5)
        ax.text(x, -1.5, f'S{tank_no}', ha='center', fontsize=6, color=pipe_s, fontweight='bold')
        # 泵标记
        ax.plot(x, 0, 's', color='#2C3E50', markersize=6)

    # 支管标注
    ax.text(70, 3.3, '← Discharge Branch Pipes (DN250) from each tank pump →',
            ha='center', fontsize=7, color=pipe_p)

    # 集管区
    manifold_cx = 72
    manifold_w = 18
    manifold_h = 3.5
    manifold_rect = patches.FancyBboxPatch((manifold_cx-manifold_w/2, -manifold_h/2),
        manifold_w, manifold_h, boxstyle="round,pad=0.15",
        facecolor=manifold_c, edgecolor='#7D3C98', linewidth=2, alpha=0.2)
    ax.add_patch(manifold_rect)
    ax.text(manifold_cx, 0, 'MANIFOLD\nAREA', ha='center', va='center',
            fontsize=9, fontweight='bold', color=manifold_c)

    # 6组通岸接头
    for i in range(6):
        mx = manifold_cx - 12 + i * 4.8
        ax.plot([mx, mx], [-3.2, 3.2], color=manifold_c, linewidth=2.5, linestyle='--', alpha=0.6)
        ax.text(mx, 3.8, f'M{i+1}', ha='center', fontsize=6, color=manifold_c, fontweight='bold')
        ax.text(mx, -4.0, f'M{i+1}', ha='center', fontsize=6, color=manifold_c, fontweight='bold')

    # 法兰
    ax.plot(manifold_cx - 10, 3.5, 's', color='#E67E22', markersize=5)
    ax.plot(manifold_cx + 10, 3.5, 's', color='#E67E22', markersize=5)
    ax.text(manifold_cx + 11, 3.5, 'Flange\nANSI 150#', fontsize=6, color='#E67E22', va='center')

    # 距船壳标注
    ax.annotate('', xy=(manifold_cx+manifold_w/2, 5), xytext=(manifold_cx+manifold_w/2+5, 5),
                arrowprops=dict(arrowstyle='<-', color='#27AE60', lw=1.0))
    ax.text(manifold_cx+manifold_w/2+5.5, 5, '4.6m from\nship side', fontsize=6, color='#27AE60', va='center')

    # 集管间距标注
    ax.annotate('', xy=(manifold_cx-12, -4.8), xytext=(manifold_cx+12, -4.8),
                arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=1.0))
    ax.text(manifold_cx, -5.3, 'Spacing ≥ 2.0m (B-class per OCIMF)', ha='center',
            fontsize=7, color='#27AE60')

    # 船艏方向
    ax.annotate('→ FWD (船艏)', xy=(142, 0), fontsize=8, color=text_color,
                ha='center', fontweight='bold')

    ax.set_title('Deck Piping Layout   (甲板管路布置示意图)', fontsize=11, fontweight='bold', pad=8)

    path = os.path.join(OUTPUT_DIR, 'figures', 'fig_deck_piping.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'✅ 图3已保存: {path}')
    return path


if __name__ == '__main__':
    os.makedirs(os.path.join(OUTPUT_DIR, 'figures'), exist_ok=True)
    render_fig2_pump_schematic()
    render_fig3_deck_piping()
    print('\n✅ 图2和图3渲染完成')
