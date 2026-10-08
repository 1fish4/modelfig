"""风格系统：为科研绘图提供开箱即用的成套视觉风格。

设计要点
--------
**风格与配色是正交的两个维度。** 风格决定"线条多粗、字多大、有没有网格"，
配色决定"用什么颜色"。两者可以自由组合：

    mf.set_style("paper", palette="soft_academic")   # 论文风 + 柔和学术配色
    mf.set_style("slide", palette="soft_multi")      # 答辩风 + 柔和多彩配色

这样只需维护 ``2 × 4 = 8`` 种组合，而不是把 8 种组合各写一遍。

内置风格
--------
``paper``  论文投稿风：细线、小字号、低饱和、黑白打印仍可区分。
``slide``  演示答辩风：粗线、大字号、高饱和、远距离投影清晰可辨。
``poster`` 海报展示风：超大字号、超粗线条、极简装饰。
"""

from __future__ import annotations

from typing import Any

import matplotlib as mpl

from .palettes import categorical, palette_names

__all__ = [
    "STYLES",
    "set_style",
    "register_style",
    "get_style",
    "style_names",
    "current_style",
    "current_palette",
]


# ---------------------------------------------------------------------------
# 内置风格定义
# ---------------------------------------------------------------------------
# 每个风格是一个 rcParams 覆盖字典，刻意不含任何颜色 —— 颜色由配色层注入。
# 这样"换配色不换风格"和"换风格不换配色"都能成立。

_PAPER: dict[str, Any] = {
    # --- 画布与字体 ---
    "figure.figsize": (6.0, 4.0),
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    # --- 线条：细而克制 ---
    "lines.linewidth": 1.2,
    "lines.markersize": 4,
    "patch.linewidth": 0.8,
    # --- 坐标轴：四边保留，内向刻度，期刊惯例 ---
    "axes.linewidth": 0.8,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "axes.grid": False,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
    "legend.frameon": False,
}

_SLIDE: dict[str, Any] = {
    # --- 画布与字体：大一号，保证投影可读 ---
    "figure.figsize": (9.0, 5.5),
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "font.size": 16,
    "axes.titlesize": 20,
    "axes.labelsize": 17,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    # --- 线条：更粗更醒目 ---
    "lines.linewidth": 2.6,
    "lines.markersize": 8,
    "patch.linewidth": 1.4,
    # --- 坐标轴：去顶右边框，浅网格，现代风 ---
    "axes.linewidth": 1.2,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.8,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.frameon": True,
    "legend.framealpha": 0.9,
}

_POSTER: dict[str, Any] = {
    # --- 画布与字体：海报远观，字号再放大 ---
    "figure.figsize": (11.0, 7.0),
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.size": 20,
    "axes.titlesize": 26,
    "axes.labelsize": 22,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 18,
    # --- 线条：最粗 ---
    "lines.linewidth": 3.4,
    "lines.markersize": 11,
    "patch.linewidth": 1.8,
    # --- 坐标轴：极简，无边框 ---
    "axes.linewidth": 1.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 7,
    "ytick.major.size": 7,
    "legend.frameon": False,
}

#: 风格注册表：风格名 -> rcParams 覆盖字典
STYLES: dict[str, dict[str, Any]] = {
    "paper": _PAPER,
    "slide": _SLIDE,
    "poster": _POSTER,
}

#: 当前激活的风格名与配色名
_current: str | None = None
_current_palette: str = "soft_academic"


def style_names() -> list[str]:
    """返回所有已注册的风格名（按注册顺序）。"""
    return list(STYLES)


def get_style(name: str) -> dict[str, Any]:
    """按名字取出风格字典的副本，避免调用方误改全局配置。"""
    if name not in STYLES:
        raise KeyError(
            f"未知风格 {name!r}。可用风格：{', '.join(STYLES)}"
        )
    return dict(STYLES[name])


def register_style(name: str, params: dict[str, Any]) -> None:
    """注册一套自定义风格。

    参数
    ----
    name : str
        风格名，重复注册会覆盖同名风格。
    params : dict
        ``matplotlib.rcParams`` 风格的键值对，只写需要覆盖的项即可。
        建议**不要**在此写颜色，颜色交给 ``palette`` 参数管理。

    示例
    ----
    >>> import modelfig as mf
    >>> mf.register_style("myschool", {"font.size": 12})
    >>> mf.set_style("myschool")
    """
    STYLES[name] = dict(params)


def set_style(
    name: str = "paper",
    *,
    palette: str | None = "soft_academic",
    font: bool = True,
) -> str:
    """激活指定风格与配色，返回风格名以便链式调用。

    参数
    ----
    name : str
        风格名，见 :func:`style_names`。
    palette : str | None, 默认 "soft_academic"
        配色名，见 :func:`modelfig.palettes.palette_names`。
        置为 ``None`` 表示不使用内置配色（保留 matplotlib 默认色）。
    font : bool, 默认 True
        是否同时配置中文字体。

    返回
    ----
    str
        实际激活的风格名。
    """
    global _current, _current_palette

    params = get_style(name)
    mpl.rcdefaults()          # 先回到干净状态，避免风格之间互相污染
    mpl.rcParams.update(params)

    # 配色层：覆盖 axes.prop_cycle，与风格正交。
    if palette is not None:
        colors = categorical(palette)
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors)
        _current_palette = palette

    if font:
        from .fonts import setup_chinese_font

        setup_chinese_font()

    _current = name
    return name


def current_style() -> str | None:
    """返回当前激活的风格名；若未激活任何风格则返回 ``None``。"""
    return _current


def current_palette() -> str:
    """返回当前激活的配色名。"""
    return _current_palette
