"""风格系统：为科研绘图提供开箱即用的成套视觉风格。

三个正交维度
------------
**风格（style）** × **配色（palette）** × **底色（background）**

    mf.set_style("soft", palette="soft_academic")             # 柔和风 + 蓝橙配色
    mf.set_style("journal", palette="soft_multi")             # 期刊风 + 多彩配色
    mf.set_style("soft", palette="misty_blue", background="cream")

三者自由组合，只需维护 4 套风格 + 7 套配色，即可覆盖大部分科研出图场景。

设计语言
--------
所有风格都遵循同一套「科研出图」视觉约定，这是让图显得专业的关键：

1. **去边框**：只保留左、下两条轴线（despine），不用四边封闭的方框
2. **轴细线粗**：坐标轴 0.6pt，数据线 1.5~1.8pt —— 约 1:3 的反差让数据"跳出来"
3. **字号偏小**：8~9pt，让图显密实而非松散
4. **网格若有若无**：柔和的浅灰点线，透明度约 0.7
5. **标记描白边**：重叠的数据点更清爽
6. **紧凑布局**：``constrained_layout`` 自动对齐元素

内置风格
--------
``journal`` 严谨期刊 —— 89 mm 单栏、无网格、600 dpi，投稿用
``soft``    柔和学术 —— 浅点线网格、低饱和，报告与论文插图的默认选择
``slide``   演示汇报 —— 大字粗线、浅网格，答辩 PPT 用
``poster``  海报展示 —— 超大字号，学术海报用
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
    "style_info",
    "current_style",
    "current_palette",
    "current_background",
    "BACKGROUNDS",
    "MM_PER_INCH",
]


MM_PER_INCH = 25.4

#: 可选底色。``white`` 通用；``cream`` 为素材里那种米色底，观感更温和。
BACKGROUNDS: dict[str, str] = {
    "white": "#FFFFFF",
    "cream": "#FAF7F1",
}


def _mm(value: float) -> float:
    """毫米转英寸。期刊图幅按毫米规格，这里统一换算。"""
    return value / MM_PER_INCH


# ---------------------------------------------------------------------------
# 所有风格共享的视觉约定
# ---------------------------------------------------------------------------

_SHARED: dict[str, Any] = {
    # --- 布局 ---
    "figure.autolayout": False,
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.h_pad": 0.04,
    "figure.constrained_layout.w_pad": 0.04,
    # --- 去边框：只留左、下 ---
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    # --- 文字颜色：深灰而非纯黑，观感更柔和 ---
    "text.color": "#1A1A1A",
    "axes.labelcolor": "#1A1A1A",
    "axes.edgecolor": "#3A3A3A",
    "xtick.color": "#3A3A3A",
    "ytick.color": "#3A3A3A",
    # --- 刻度朝外 ---
    "xtick.direction": "out",
    "ytick.direction": "out",
    # --- 网格压在数据之下 ---
    "axes.axisbelow": True,
    # --- 标记描白边：重叠点更清爽 ---
    "lines.markeredgecolor": "white",
    "lines.markeredgewidth": 0.6,
    # --- 图例去框 ---
    "legend.frameon": False,
    "legend.handlelength": 1.6,
    "legend.handletextpad": 0.5,
    "legend.borderaxespad": 0.3,
    # --- 导出 ---
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
    "savefig.transparent": False,
    # --- 图像 ---
    "image.aspect": "auto",
}

#: 极浅点线网格，柔和的观感全靠它
_GRID_SOFT: dict[str, Any] = {
    "axes.grid": True,
    "grid.color": "#CFCFCF",
    "grid.linewidth": 0.6,
    "grid.linestyle": ":",
    "grid.alpha": 0.75,
}


# ---------------------------------------------------------------------------
# 内置风格
# ---------------------------------------------------------------------------

# journal —— 严谨期刊：Nature/Science 规格，无网格，投稿专用
_JOURNAL: dict[str, Any] = {
    **_SHARED,
    "figure.figsize": (_mm(89), _mm(89) * 0.75),   # 89 mm 单栏，4:3
    "figure.dpi": 120,
    "savefig.dpi": 600,
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.minor.width": 0.5,
    "ytick.minor.width": 0.5,
    "lines.linewidth": 1.5,
    "lines.markersize": 3.5,
    "patch.linewidth": 0.6,
    "axes.grid": False,
}

# soft —— 柔和学术：浅点线网格、低饱和，本库的默认风格
_SOFT: dict[str, Any] = {
    **_SHARED,
    **_GRID_SOFT,
    "figure.figsize": (_mm(140), _mm(140) * 0.72),
    "figure.dpi": 110,
    "savefig.dpi": 400,
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "lines.linewidth": 1.8,
    "lines.markersize": 5,
    "patch.linewidth": 0.7,
}

# slide —— 演示汇报：大字粗线，浅实线网格
_SLIDE: dict[str, Any] = {
    **_SHARED,
    "axes.grid": True,
    "grid.color": "#DCDCDC",
    "grid.linewidth": 1.0,
    "grid.linestyle": "-",
    "grid.alpha": 0.8,
    "figure.figsize": (_mm(230), _mm(230) * 0.60),
    "figure.dpi": 100,
    "savefig.dpi": 200,
    "font.size": 15,
    "axes.titlesize": 19,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 13,
    "axes.linewidth": 1.2,
    "xtick.major.width": 1.2,
    "ytick.major.width": 1.2,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "lines.linewidth": 2.8,
    "lines.markersize": 8,
    "lines.markeredgewidth": 1.0,
    "patch.linewidth": 1.2,
}

# poster —— 海报展示：超大字号，无网格
_POSTER: dict[str, Any] = {
    **_SHARED,
    "axes.grid": False,
    "figure.figsize": (_mm(280), _mm(280) * 0.64),
    "figure.dpi": 90,
    "savefig.dpi": 300,
    "font.size": 19,
    "axes.titlesize": 25,
    "axes.labelsize": 21,
    "xtick.labelsize": 17,
    "ytick.labelsize": 17,
    "legend.fontsize": 17,
    "axes.linewidth": 1.6,
    "xtick.major.width": 1.6,
    "ytick.major.width": 1.6,
    "xtick.major.size": 7,
    "ytick.major.size": 7,
    "lines.linewidth": 3.6,
    "lines.markersize": 11,
    "lines.markeredgewidth": 1.4,
    "patch.linewidth": 1.6,
}

#: 风格注册表
STYLES: dict[str, dict[str, Any]] = {
    "journal": _JOURNAL,
    "soft": _SOFT,
    "slide": _SLIDE,
    "poster": _POSTER,
}

#: 各风格的定位说明（供文档与 CLI 展示）
_STYLE_DESC: dict[str, dict[str, str]] = {
    "journal": {
        "label": "严谨期刊",
        "usage": "论文投稿、学位论文",
        "character": "89 mm 单栏 · 无网格 · 0.6pt 细轴 · 600 dpi",
    },
    "soft": {
        "label": "柔和学术",
        "usage": "组会汇报、论文插图（默认）",
        "character": "浅灰点线网格 · 低饱和 · 0.6pt 细轴配 1.8pt 粗线",
    },
    "slide": {
        "label": "演示汇报",
        "usage": "答辩 PPT、课堂展示",
        "character": "大字粗线 · 浅色实线网格 · 投影可辨",
    },
    "poster": {
        "label": "海报展示",
        "usage": "学术海报、远距离展示",
        "character": "超大字号 · 无网格 · 极简装饰",
    },
}

_current: str | None = None
_current_palette: str = "soft_academic"
_current_background: str = "white"


def style_names() -> list[str]:
    """返回所有已注册的风格名（按注册顺序）。"""
    return list(STYLES)


def style_info() -> list[tuple[str, str, str, str]]:
    """返回风格清单，便于打印或生成文档。

    返回
    ----
    list[tuple]
        每项为 ``(名称, 中文标签, 适用场景, 视觉特征)``。
    """
    return [
        (name, _STYLE_DESC.get(name, {}).get("label", name),
         _STYLE_DESC.get(name, {}).get("usage", ""),
         _STYLE_DESC.get(name, {}).get("character", ""))
        for name in STYLES
    ]


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
    name: str = "soft",
    *,
    palette: str | None = "soft_academic",
    background: str = "white",
    font: bool = True,
) -> str:
    """激活指定风格、配色与底色，返回风格名以便链式调用。

    参数
    ----
    name : str, 默认 "soft"
        风格名，见 :func:`style_names`。
    palette : str | None, 默认 "soft_academic"
        配色名，见 :func:`modelfig.palettes.palette_names`。
        置为 ``None`` 表示不接管颜色（保留 matplotlib 默认色）。
    background : str, 默认 "white"
        ``"white"`` 纯白 或 ``"cream"`` 米色（更温和，见 :data:`BACKGROUNDS`）。
    font : bool, 默认 True
        是否同时配置中文字体。

    返回
    ----
    str
        实际激活的风格名。
    """
    global _current, _current_palette, _current_background

    params = get_style(name)
    mpl.rcdefaults()          # 先回到干净状态，避免风格之间互相污染
    mpl.rcParams.update(params)

    if palette is not None:
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=categorical(palette))
        _current_palette = palette

    if background not in BACKGROUNDS:
        raise KeyError(
            f"未知底色 {background!r}。可用底色：{', '.join(BACKGROUNDS)}"
        )
    bg = BACKGROUNDS[background]
    mpl.rcParams["figure.facecolor"] = bg
    mpl.rcParams["savefig.facecolor"] = bg
    mpl.rcParams["axes.facecolor"] = bg
    _current_background = background

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


def current_background() -> str:
    """返回当前激活的底色名。"""
    return _current_background
