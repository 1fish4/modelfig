"""生成展示画廊：把风格与图种排成画册，供 README 与文档引用。

运行方式
--------
    python examples/gallery.py

产物
----
``docs/images/styles.png``   —— 四套风格对同一份数据的观感差异
``docs/images/gallery.png``  —— 全部图种一览
``docs/images/palettes.png`` —— 七套配色色板

实现思路
--------
matplotlib 本身不擅长排版"画册"。因此这里分两步：
1. 用 modelfig 各自渲染每个小图（此时风格是真实的）；
2. 用 Pillow 把这些小图拼成一张带标题与说明的版面。

这样「图是真的用本库画的」，而版面又能做到素材里那种整齐的观感。
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

import modelfig as mf

BUILD = os.path.join(_REPO_ROOT, "docs", "_build")
OUT = os.path.join(_REPO_ROOT, "docs", "images")
os.makedirs(BUILD, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# 版面配色（与素材同源的米色系）
CANVAS_BG = "#FBF8F2"
PANEL_BG = "#FFFFFF"
INK = "#1F2937"
MUTED = "#6B7280"
ACCENT = "#5B83BC"

FONT_REGULAR = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


# ---------------------------------------------------------------------------
# 示例数据
# ---------------------------------------------------------------------------

def _group_df() -> pd.DataFrame:
    """四组、每组 8 个观测 —— 用于柱状图与箱线图。"""
    rng = np.random.default_rng(7)
    rows = []
    for name, mu in (("对照组", 5.0), ("处理组1", 6.6),
                     ("处理组2", 7.4), ("处理组3", 5.6)):
        for _ in range(8):
            rows.append({"组别": name, "表达量": rng.normal(mu, 0.85)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 单元图渲染
# ---------------------------------------------------------------------------

def _render(fname: str, draw_fn, style: str, palette: str,
            background: str = "cream", **kwargs) -> str:
    """按指定风格渲染一张图并保存，返回文件路径。"""
    mf.set_style(style, palette=palette, background=background)
    draw_fn(**kwargs)
    path = os.path.join(BUILD, fname)
    mf.save(path)
    plt.close("all")
    return path


# --- 各图种的画法 ---

def draw_bars_sig():
    """带误差棒、散点与显著性括号的柱状图 —— 最能体现风格差异。"""
    df = _group_df()
    mf.barplot(
        df, x="组别", y="表达量",
        show_points=True,
        annotate=[("对照组", "处理组1"), ("处理组1", "处理组2")],
        xlabel="实验分组", ylabel="相对表达量",
    )


def draw_soft_bars():
    df = _group_df()
    mf.barplot(df, x="组别", y="表达量", hue="组别",
               show_points=True, xlabel="实验分组", ylabel="相对表达量")


def draw_line():
    x = np.arange(1, 9)
    y = np.vstack([
        [2.0, 3.1, 4.2, 5.0, 6.3, 7.1, 8.4, 9.2],
        [1.0, 1.8, 3.0, 3.6, 5.0, 5.4, 6.8, 7.0],
        [0.5, 1.2, 1.6, 2.8, 3.1, 4.4, 4.9, 6.0],
    ])
    mf.line(x, y, labels=["方案 A", "方案 B", "方案 C"],
            xlabel="迭代轮次", ylabel="目标值")


def draw_box():
    df = _group_df()
    mf.boxplot(df, x="组别", y="表达量",
               xlabel="实验分组", ylabel="相对表达量")


def draw_reg():
    rng = np.random.default_rng(11)
    xx = rng.normal(0, 1, 60)
    df = pd.DataFrame({"蛋白表达量": xx * 2 + 6})
    df["基因表达量"] = 1.4 * df["蛋白表达量"] + rng.normal(0, 1.6, 60)
    mf.regplot(df, x="蛋白表达量", y="基因表达量")


def draw_heatmap():
    rng = np.random.default_rng(3)
    base = rng.normal(size=(50, 6))
    mix = base @ np.array([
        [1.0, .7, .4, .1, 0, 0], [0, .6, .8, .3, 0, 0],
        [0, 0, .5, .7, .2, 0], [0, 0, 0, .6, .5, .1],
        [0, 0, 0, 0, .5, .6], [0, 0, 0, 0, 0, .4],
    ])
    df = pd.DataFrame(mix, columns=[f"指标{i}" for i in "ABCDEF"])
    mf.corr_heatmap(df, mask_upper=True)


def draw_radar():
    mf.radar(["成本", "效率", "稳定性", "可扩展性", "易用性"],
             [[8, 6, 7, 5, 9], [6, 9, 8, 7, 6], [7, 7, 9, 8, 7]],
             labels=["方案甲", "方案乙", "方案丙"])


def draw_roc():
    rng = np.random.default_rng(5)
    yt = np.concatenate([np.zeros(70), np.ones(70)])
    ys = np.concatenate([rng.normal(0.32, 0.18, 70),
                         rng.normal(0.74, 0.18, 70)])
    mf.roc_curve(yt, ys, label="诊断模型")


def draw_errorband():
    t = np.arange(0, 21)
    df = pd.DataFrame({
        "时间": np.tile(t, 2),
        "均值": np.concatenate([10 + t * 0.7, 8 + t * 0.45]),
        "标准差": np.concatenate([np.linspace(0.4, 1.1, 21),
                                np.linspace(0.7, 1.5, 21)]),
        "组别": ["治疗组"] * 21 + ["对照组"] * 21,
    })
    mf.errorbar_line(df, x="时间", y="均值", err="标准差", hue="组别",
                     band=True, xlabel="随访时间（周）", ylabel="测量值")


def draw_stack():
    df = pd.DataFrame({
        "季度": ["Q1", "Q2", "Q3", "Q4"],
        "产品甲": [30, 40, 45, 52], "产品乙": [20, 25, 30, 28],
        "产品丙": [10, 15, 18, 25],
    })
    mf.stackplot(df, x="季度", y=["产品甲", "产品乙", "产品丙"],
                 kind="bar", ylabel="销售额（万元）")


def draw_facet():
    df = pd.DataFrame({
        "时间": np.tile(np.arange(1, 9), 3),
        "数值": np.concatenate([
            np.linspace(2, 9, 8), 9 - np.linspace(0, 7, 8),
            np.sin(np.arange(8)) * 3 + 5]),
        "区域": np.repeat(["华东", "华北", "华南"], 8),
    })
    mf.facet_grid(df, x="时间", y="数值", col="区域", kind="line")


def draw_hist():
    rng = np.random.default_rng(2)
    df = pd.DataFrame({
        "测量值": np.concatenate([rng.normal(5, 1, 90), rng.normal(7, 1.1, 90)]),
        "组别": ["对照组"] * 90 + ["处理组"] * 90,
    })
    mf.histplot(df, x="测量值", bins=16, hue="组别", density=True,
                xlabel="测量值", ylabel="概率密度")


def draw_violin():
    df = _group_df()
    mf.violinplot(df, x="组别", y="表达量",
                  xlabel="实验分组", ylabel="相对表达量")


# ---------------------------------------------------------------------------
# 版面拼装
# ---------------------------------------------------------------------------

def _font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _fit(im: Image.Image, max_w: int, max_h: int) -> Image.Image:
    """等比缩放到不超过给定尺寸。"""
    ratio = min(max_w / im.width, max_h / im.height)
    return im.resize((max(1, int(im.width * ratio)),
                      max(1, int(im.height * ratio))), Image.LANCZOS)


def compose(panels, out_path: str, title: str, subtitle: str = "",
            cols: int = 2, width: int = 1680,
            cell_img_h: int = 340, panel_pad: int = 18) -> str:
    """把小图拼成一张画册版面。

    参数
    ----
    panels : list[tuple[str, str, str, str]]
        每项为 ``(序号, 小标题, 副标题, 图片路径)``；副标题可为空串。
    """
    margin, gap = 56, 36
    header_h = 132 if subtitle else 96
    cell_w = (width - 2 * margin - (cols - 1) * gap) // cols

    f_title = _font(FONT_BOLD, 40)
    f_sub = _font(FONT_REGULAR, 20)
    f_cap = _font(FONT_BOLD, 22)
    f_note = _font(FONT_REGULAR, 17)
    f_num = _font(FONT_BOLD, 20)

    # --- 先测量：每格高度 = 标题条 + 图 + 内边距 ---
    loaded = []
    for num, cap, note, path in panels:
        im = Image.open(path).convert("RGB")
        im = _fit(im, cell_w - 2 * panel_pad, cell_img_h)
        loaded.append((num, cap, note, im))

    rows = [loaded[i:i + cols] for i in range(0, len(loaded), cols)]
    cap_bar_h = 46
    row_heights = [
        max(cap_bar_h + im.height + 2 * panel_pad for _, _, _, im in row)
        for row in rows
    ]

    total_h = header_h + sum(row_heights) + gap * (len(rows) - 1) + margin
    canvas = Image.new("RGB", (width, total_h), CANVAS_BG)
    d = ImageDraw.Draw(canvas)

    # --- 页眉 ---
    d.text((margin, 40), title, font=f_title, fill=INK)
    d.rectangle([margin, 92, margin + 96, 97], fill=ACCENT)
    if subtitle:
        d.text((margin, 108), subtitle, font=f_sub, fill=MUTED)

    # --- 逐格绘制 ---
    y = header_h
    for row, row_h in zip(rows, row_heights):
        x = margin
        for num, cap, note, im in row:
            # 卡片
            d.rounded_rectangle(
                [x, y, x + cell_w, y + row_h], radius=14,
                fill=PANEL_BG, outline="#E7E2D8", width=2,
            )
            # 序号徽标
            d.rounded_rectangle(
                [x + panel_pad, y + 12, x + panel_pad + 34, y + 34],
                radius=6, fill=ACCENT,
            )
            d.text((x + panel_pad + 8, y + 14), num, font=f_num, fill="#FFFFFF")
            # 小标题
            d.text((x + panel_pad + 46, y + 13), cap, font=f_cap, fill=INK)
            # 副标题（贴在标题行下方，图表上方）
            cap_h = cap_bar_h
            if note:
                d.text((x + panel_pad + 46, y + 39), note, font=f_note,
                       fill=MUTED)
                cap_h += 22
            # 图
            ix = x + (cell_w - im.width) // 2
            iy = y + cap_h + panel_pad
            canvas.paste(im, (ix, iy))
            x += cell_w + gap
        y += row_h + gap

    canvas.save(out_path, quality=95)
    print(f"  版面已生成：{out_path}  ({canvas.width}x{canvas.height})")
    return out_path


# ---------------------------------------------------------------------------
# 三张展示图
# ---------------------------------------------------------------------------

def build_style_showcase() -> str:
    """四套风格对同一份数据的观感差异。"""
    print("[styles] 渲染四套风格 …")
    meta = {
        "journal": ("严谨期刊", "89 mm 单栏 · 无网格 · 细轴粗线 · 600 dpi"),
        "soft": ("柔和学术", "浅灰点线网格 · 低饱和 · 本库默认风格"),
        "slide": ("演示汇报", "大字粗线 · 浅色实线网格 · 投影可辨"),
        "poster": ("海报展示", "超大字号 · 无网格 · 远距离可读"),
    }
    panels = []
    for i, (style, (label, note)) in enumerate(meta.items(), 1):
        p = _render(f"style_{style}.png", draw_bars_sig, style,
                    "soft_academic")
        panels.append((f"0{i}", label, note, p))

    return compose(
        panels, os.path.join(OUT, "styles.png"),
        "四套绘图风格",
        "同一份数据 · 同一段调用代码 · 只切换风格名",
        cols=2, cell_img_h=420,
    )


def build_gallery() -> str:
    """全部图种一览。"""
    print("[gallery] 渲染各图种 …")
    items = [
        ("01", "折线对比图", "多条序列趋势对比", draw_line),
        ("02", "分组柱状图", "误差棒 + 散点 + 显著性括号", draw_bars_sig),
        ("03", "箱线图", "分位数 + 原始散点", draw_box),
        ("04", "散点回归图", "拟合线 + R² / P 值", draw_reg),
        ("05", "相关性热图", "发散色带 + 上三角遮罩", draw_heatmap),
        ("06", "雷达图", "多方案多指标对比", draw_radar),
        ("07", "ROC 曲线", "自实现 AUC，不依赖 sklearn", draw_roc),
        ("08", "误差带折线图", "均值 ± 标准差置信带", draw_errorband),
        ("09", "堆叠柱状图", "构成随时间变化", draw_stack),
        ("10", "分面网格图", "按分类拆分并共享坐标轴", draw_facet),
        ("11", "分层直方图", "分组密度分布", draw_hist),
        ("12", "小提琴图", "密度形态 + 中位数", draw_violin),
    ]
    panels = []
    for num, cap, note, fn in items:
        p = _render(f"g_{num}.png", fn, "soft", "soft_academic")
        panels.append((num, cap, note, p))

    return compose(
        panels, os.path.join(OUT, "gallery.png"),
        "图种总览",
        "全部图形均由本库渲染：柔和学术风格 + 柔和学术配色",
        cols=3, cell_img_h=300, width=1800,
    )


def build_palettes() -> str:
    """七套配色的色板对照。"""
    print("[palettes] 绘制色板 …")
    mf.set_style("soft", palette=None, background="cream")
    rows = mf.list_palettes()
    n = len(rows)

    fig, axes = plt.subplots(n, 1, figsize=(9.0, 1.0 * n))
    for ax, (name, label, kind, count, usage) in zip(axes, rows):
        colors = mf.sequential(name) if kind == "continuous" else mf.categorical(name)
        k = len(colors)
        for i, c in enumerate(colors):
            ax.add_patch(plt.Rectangle((i, 0), 0.94, 1.0,
                                       facecolor=c, edgecolor="#00000022",
                                       linewidth=0.6))
        ax.set_xlim(0, k)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xticks([])
        kind_cn = "类别色" if kind == "categorical" else "渐变色"
        ax.set_ylabel(f"{label}\n({name} · {kind_cn})",
                      rotation=0, ha="right", va="center",
                      fontsize=9, labelpad=68)
        for s in ax.spines.values():
            s.set_visible(False)

    fig.suptitle("七套科研配色", fontsize=15)
    fig.text(0.5, -0.01,
             "色值取自科研绘图素材，逐像素采样核对",
             ha="center", fontsize=9, color="#6B7280")
    path = os.path.join(OUT, "palettes.png")
    mf.save(path)
    plt.close("all")
    print(f"  色板已生成：{path}")
    return path


def main():
    print(f"[gallery] 输出目录：{OUT}")
    build_style_showcase()
    build_gallery()
    build_palettes()
    print("[gallery] 完成")


if __name__ == "__main__":
    main()
