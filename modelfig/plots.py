"""绘图函数集合。

每个函数都遵循同一套约定，以降低记忆负担：

1. 接收 ``data`` 与可选的 ``ax``；若不给 ``ax`` 就自动创建画布。
2. 返回 ``(fig, ax)``，方便调用方继续微调（如加注释、改坐标范围）。
3. 所有视觉细节交给 :mod:`modelfig.styles`，函数本身不硬编码样式。

这样设计的好处是：同一个函数配合不同风格，就能产出投稿图或答辩图。
"""

from __future__ import annotations

from typing import Any, Sequence

import matplotlib.pyplot as plt
import numpy as np

__all__ = [
    "line",
    "bar",
    "dual_axis",
    "heatmap",
    "radar",
    "scatter",
    "box",
    "violin",
    "stacked_bar",
    "errorbar",
]


def _get_ax(ax):
    """未传入 ``ax`` 时创建一个新的 ``(fig, ax)``，否则复用已有的。"""
    if ax is None:
        return plt.subplots()
    return ax.figure, ax


def line(
    x: Sequence[float],
    y: Sequence[float] | Sequence[Sequence[float]],
    *,
    labels: Sequence[str] | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    markers: bool = True,
    ax: Any = None,
):
    """绘制折线图，支持多条序列对比。

    参数
    ----
    x : 序列
        横坐标，长度记为 ``n``。
    y : 序列 或 二维序列
        单个序列长度为 ``n``；多个序列为 ``(m, n)``，每条画一条线。
    labels : 序列, 可选
        每条线的图例名，长度需与线数一致；给出时才显示图例。
    markers : bool, 默认 True
        是否在数据点画标记，便于区分重叠曲线。

    返回
    ----
    (fig, ax)
    """
    fig, ax = _get_ax(ax)

    y_arr = np.asarray(y, dtype=float)
    x_arr = np.asarray(x, dtype=float)
    is_multi = y_arr.ndim == 2
    y_2d = y_arr if is_multi else y_arr.reshape(1, -1)

    marker = "o" if markers else None
    for i, series in enumerate(y_2d):
        label = labels[i] if labels is not None and i < len(labels) else None
        ax.plot(x_arr, series, marker=marker, label=label)

    if labels is not None:
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax


def bar(
    categories: Sequence[str],
    values: Sequence[float] | Sequence[Sequence[float]],
    *,
    labels: Sequence[str] | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """绘制柱状图，支持分组对比。

    参数
    ----
    categories : 序列
        类别名，长度记为 ``n``。
    values : 序列 或 二维序列
        单个序列长度为 ``n``；多个序列为 ``(m, n)``，按组并排显示。
    labels : 序列, 可选
        每组柱子对应的图例名。

    返回
    ----
    (fig, ax)
    """
    fig, ax = _get_ax(ax)

    values_arr = np.asarray(values, dtype=float)
    is_multi = values_arr.ndim == 2
    vals_2d = values_arr if is_multi else values_arr.reshape(1, -1)

    n_groups, n_cats = vals_2d.shape
    x = np.arange(n_cats)
    # 分组柱宽：整体占 0.8 的带宽，组内均分并留出间隙。
    total_width = 0.8
    width = total_width / n_groups

    for i, series in enumerate(vals_2d):
        offset = (i - (n_groups - 1) / 2) * width
        label = labels[i] if labels is not None and i < len(labels) else None
        ax.bar(x + offset, series, width=width, label=label)

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    if labels is not None:
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax


def dual_axis(
    x: Sequence[float],
    y_left: Sequence[float],
    y_right: Sequence[float],
    *,
    label_left: str = "左轴",
    label_right: str = "右轴",
    xlabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """绘制双 Y 轴图：左右两条量纲不同的曲线共用一个横坐标。

    典型场景：趋势图里同时呈现"绝对量"与"增长率"。

    返回
    ----
    (fig, ax_left)  右轴可通过 ``ax_left.right_ax`` 访问
    """
    fig, ax_l = _get_ax(ax)
    ax_r = ax_l.twinx()

    x_arr = np.asarray(x, dtype=float)

    color_l = plt.rcParams["axes.prop_cycle"].by_key()["color"][0]
    color_r = plt.rcParams["axes.prop_cycle"].by_key()["color"][1]

    ax_l.plot(x_arr, y_left, color=color_l, marker="o", label=label_left)
    ax_r.plot(x_arr, y_right, color=color_r, marker="s", label=label_right)

    ax_l.set_xlabel(xlabel)
    ax_l.set_ylabel(label_left, color=color_l)
    ax_r.set_ylabel(label_right, color=color_r)
    # 刻度颜色跟随曲线颜色，读者一眼对应得上。
    ax_l.tick_params(axis="y", colors=color_l)
    ax_r.tick_params(axis="y", colors=color_r)
    if title:
        ax_l.set_title(title)

    # 把右轴挂到左轴上，便于调用方继续操作。
    ax_l.right_ax = ax_r
    return fig, ax_l


def heatmap(
    matrix: Sequence[Sequence[float]],
    *,
    xlabels: Sequence[str] | None = None,
    ylabels: Sequence[str] | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    cmap: str = "YlOrRd",
    annot: bool = True,
    fmt: str = ".2f",
    ax: Any = None,
):
    """绘制热力图，常用于相关系数矩阵、指标随双变量变化的分布。

    参数
    ----
    matrix : 二维序列
        形状 ``(rows, cols)`` 的数值矩阵。
    cmap : str, 默认 "YlOrRd"
        色带名，默认黄→橙→红，符合"越大越醒目"的直觉。
    annot : bool, 默认 True
        是否在每个格子里标注数值。

    返回
    ----
    (fig, ax)
    """
    fig, ax = _get_ax(ax)

    data = np.asarray(matrix, dtype=float)
    im = ax.imshow(data, cmap=cmap, aspect="auto")

    n_rows, n_cols = data.shape
    ax.set_xticks(np.arange(n_cols))
    ax.set_yticks(np.arange(n_rows))
    if xlabels is not None:
        ax.set_xticklabels(xlabels)
    if ylabels is not None:
        ax.set_yticklabels(ylabels)

    if annot:
        # 用矩阵中位数决定文字颜色，保证任何底色下都清晰可读。
        threshold = float(np.median(data))
        for r in range(n_rows):
            for c in range(n_cols):
                val = data[r, c]
                color = "white" if val > threshold else "black"
                ax.text(
                    c, r, format(val, fmt),
                    ha="center", va="center", color=color,
                )

    fig.colorbar(im, ax=ax, shrink=0.85)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax


def radar(
    categories: Sequence[str],
    values: Sequence[float] | Sequence[Sequence[float]],
    *,
    labels: Sequence[str] | None = None,
    title: str = "",
    fill_alpha: float = 0.15,
    ax: Any = None,
):
    """绘制雷达图（蛛网图），适合多指标方案的综合对比。

    参数
    ----
    categories : 序列
        维度名，长度记为 ``n``，需 ``n >= 3``。
    values : 序列 或 二维序列
        单个方案的各维取值长度为 ``n``；多个方案为 ``(m, n)``。

    返回
    ----
    (fig, ax)  其中 ``ax`` 为极坐标轴
    """
    n = len(categories)
    if n < 3:
        raise ValueError(f"雷达图至少需要 3 个维度，当前只有 {n} 个。")

    values_arr = np.asarray(values, dtype=float)
    is_multi = values_arr.ndim == 2
    vals_2d = values_arr if is_multi else values_arr.reshape(1, -1)

    if ax is None:
        fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    else:
        fig = ax.figure

    # 角度：均分圆周，并闭合首尾。
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    angles_closed = np.concatenate([angles, angles[:1]])

    for i, series in enumerate(vals_2d):
        closed = np.concatenate([series, series[:1]])
        label = labels[i] if labels is not None and i < len(labels) else None
        ax.plot(angles_closed, closed, marker="o", label=label)
        ax.fill(angles_closed, closed, alpha=fill_alpha)

    ax.set_xticks(angles)
    ax.set_xticklabels(categories)
    # 让 0 度从正上方开始、顺时针排列，符合阅读习惯。
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    if labels is not None:
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
    if title:
        ax.set_title(title, pad=20)
    return fig, ax


def scatter(
    x: Sequence[float],
    y: Sequence[float],
    *,
    sizes: Sequence[float] | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """基础散点图（数组接口）。需要按类别着色时请用 ``stats.scatterplot``。

    参数
    ----
    sizes : 序列, 可选
        每个点的大小，用于绘制气泡图。

    返回
    ----
    (fig, ax)
    """
    fig, ax = _get_ax(ax)

    xs = np.asarray(x, dtype=float)
    ys = np.asarray(y, dtype=float)

    s = np.asarray(sizes, dtype=float) if sizes is not None else None
    ax.scatter(xs, ys, s=s, alpha=0.75)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax


def box(
    groups: Sequence[Sequence[float]],
    *,
    labels: Sequence[str] | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    show_points: bool = True,
    ax: Any = None,
):
    """箱线图（数组接口）。

    参数
    ----
    groups : 二维序列
        每个子序列是一个分组的原始数据。

    返回
    ----
    (fig, ax)
    """
    fig, ax = _get_ax(ax)

    data = [np.asarray(g, dtype=float) for g in groups]
    bp = ax.boxplot(
        data, tick_labels=list(labels) if labels else None,
        patch_artist=True, widths=0.55,
        medianprops={"linewidth": 1.6, "color": "0.2"},
    )

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, b in enumerate(bp["boxes"]):
        b.set_facecolor(colors[i % len(colors)])
        b.set_alpha(0.65)
        b.set_edgecolor("0.3")

    if show_points:
        rng = np.random.default_rng(0)
        for i, values in enumerate(data):
            jitter = rng.normal(0, 0.06, size=len(values))
            ax.scatter(np.full(len(values), i + 1) + jitter, values,
                       s=14, color="0.25", alpha=0.6, zorder=3)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax


def violin(
    groups: Sequence[Sequence[float]],
    *,
    labels: Sequence[str] | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """小提琴图（数组接口）。

    返回
    ----
    (fig, ax)
    """
    fig, ax = _get_ax(ax)

    data = [np.asarray(g, dtype=float) for g in groups]
    parts = ax.violinplot(data, showmedians=True, widths=0.75)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, body in enumerate(parts["bodies"]):
        body.set_facecolor(colors[i % len(colors)])
        body.set_alpha(0.6)
        body.set_edgecolor("0.3")
    for key in ("cmedians", "cbars", "cmins", "cmaxes"):
        if key in parts:
            parts[key].set_edgecolor("0.2")
            parts[key].set_linewidth(1.2)

    if labels:
        ax.set_xticks(np.arange(1, len(labels) + 1))
        ax.set_xticklabels(labels)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax


def stacked_bar(
    categories: Sequence[str],
    values: Sequence[Sequence[float]],
    *,
    labels: Sequence[str] | None = None,
    xlabel: str = "",
    ylabel: str = "数值",
    title: str = "",
    ax: Any = None,
):
    """堆叠柱状图（数组接口）。

    参数
    ----
    values : 二维序列
        形状 ``(m, n)`` —— ``m`` 个堆叠层，``n`` 个类别。

    返回
    ----
    (fig, ax)
    """
    fig, ax = _get_ax(ax)

    vals = np.asarray(values, dtype=float)
    x = np.arange(len(categories))
    bottom = np.zeros(len(categories))

    for i, series in enumerate(vals):
        label = labels[i] if labels is not None and i < len(labels) else None
        ax.bar(x, series, bottom=bottom, label=label, width=0.7)
        bottom = bottom + series

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    if labels is not None:
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax


def errorbar(
    x: Sequence[float],
    y: Sequence[float],
    err: Sequence[float],
    *,
    label: str = "",
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    band: bool = False,
    ax: Any = None,
):
    """折线 + 误差棒（数组接口）。``band=True`` 时绘制半透明误差带。

    返回
    ----
    (fig, ax)
    """
    fig, ax = _get_ax(ax)

    xs = np.asarray(x, dtype=float)
    ys = np.asarray(y, dtype=float)
    es = np.asarray(err, dtype=float)

    line, = ax.plot(xs, ys, marker="o", label=label)
    if band:
        ax.fill_between(xs, ys - es, ys + es, alpha=0.2, color=line.get_color())
    else:
        ax.errorbar(xs, ys, yerr=es, fmt="none", capsize=4,
                    color=line.get_color())

    if label:
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax
