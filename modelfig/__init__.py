"""modelfig —— 面向科研与数学建模的标准化绘图模板库。

核心理念
--------
**风格与配色正交，一份数据多套观感。**

    >>> import modelfig as mf
    >>> mf.set_style("paper", palette="soft_academic")   # 论文风 + 柔和学术配色
    >>> mf.line([1, 2, 3], [2, 4, 9], xlabel="时间", ylabel="数值")
    >>> mf.save("trend.png")

两层接口
--------
**通用层**（数组接口，简单直白）
    :func:`line` :func:`bar` :func:`dual_axis` :func:`heatmap` :func:`radar`
    :func:`scatter` :func:`box` :func:`violin` :func:`stacked_bar` :func:`errorbar`

**统计层**（DataFrame 接口，支持分组与统计标注）
    :func:`scatterplot` :func:`regplot` :func:`boxplot` :func:`violinplot`
    :func:`barplot` :func:`histplot` :func:`roc_curve` :func:`errorbar_line`
    :func:`corr_heatmap` :func:`pairplot_grid` :func:`stackplot` :func:`facet_grid`

风格与配色
----------
风格：``paper`` 论文投稿 / ``slide`` 演示答辩 / ``poster`` 海报展示
配色：``soft_academic`` 柔和学术 / ``warm_cool`` 暖橙冷蓝 /
      ``misty_blue`` 烟霞蓝橙 / ``soft_multi`` 柔和多彩
"""

from __future__ import annotations

from .fonts import available_chinese_fonts, setup_chinese_font
from .palettes import (
    PALETTES,
    categorical,
    list_palettes,
    palette_names,
    register_palette,
    sequential,
)
from .plots import (
    bar,
    box,
    dual_axis,
    errorbar,
    heatmap,
    line,
    radar,
    scatter,
    stacked_bar,
    violin,
)
from .stats import (
    barplot,
    boxplot,
    corr_heatmap,
    errorbar_line,
    facet_grid,
    histplot,
    lineplot,
    pairplot_grid,
    regplot,
    roc_curve,
    scatterplot,
    stackplot,
    violinplot,
)
from .styles import (
    STYLES,
    current_palette,
    current_style,
    get_style,
    register_style,
    set_style,
    style_names,
)

__version__ = "0.2.0"

__all__ = [
    # 风格
    "set_style", "style_names", "get_style", "register_style",
    "current_style", "current_palette", "STYLES",
    # 配色
    "palette_names", "list_palettes", "categorical", "sequential",
    "register_palette", "PALETTES",
    # 字体
    "setup_chinese_font", "available_chinese_fonts",
    # 通用层绘图
    "line", "bar", "dual_axis", "heatmap", "radar",
    "scatter", "box", "violin", "stacked_bar", "errorbar",
    # 统计层绘图
    "scatterplot", "regplot", "boxplot", "violinplot", "barplot",
    "histplot", "lineplot", "roc_curve", "errorbar_line",
    "corr_heatmap", "pairplot_grid", "stackplot", "facet_grid",
    # 工具
    "save", "load_csv", "__version__",
]


def save(path: str, *, dpi: int | None = None, **kwargs) -> str:
    """保存当前图形到文件，返回实际写入的路径。

    建议按用途选扩展名：``.png`` 通用位图、``.pdf`` / ``.svg`` 矢量图适合投稿。

    参数
    ----
    path : str
        输出路径。
    dpi : int, 可选
        覆盖风格中的 ``savefig.dpi``。

    返回
    ----
    str
        实际写入的文件路径。
    """
    import matplotlib.pyplot as plt

    if dpi is not None:
        kwargs["dpi"] = dpi
    plt.savefig(path, **kwargs)
    return path


def load_csv(path: str, **kwargs):
    """读取 CSV 为 DataFrame 的便捷函数（带常见中文编码回退）。

    参数
    ----
    path : str
        CSV 文件路径。
    **kwargs
        透传给 :func:`pandas.read_csv`。

    返回
    ----
    pandas.DataFrame
    """
    import pandas as pd

    try:
        return pd.read_csv(path, **kwargs)
    except UnicodeDecodeError:
        # 中文 CSV 常见编码：GBK / GB18030。
        return pd.read_csv(path, encoding="gb18030", **kwargs)
