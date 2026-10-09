"""统计图形层：接收 DataFrame 或数组，产出带统计标注的科研图。

这一层对应"B 方案"——seaborn 风格的接口：
    >>> mf.scatterplot(data=df, x="温度", y="产率", hue="催化剂")

与 :mod:`modelfig.plots` 的关系
--------------------------------
``plots.py``  通用图层：接收纯数组，参数少，上手快。
``stats.py``  统计图层：接收 DataFrame，支持分组、着色、统计标注。

两层共用同一套风格与配色系统，视觉完全统一。

依赖说明
--------
本模块使用 ``pandas``（数据）、``scipy``（回归与统计检验）、
``seaborn``（分面网格与聚类热图）。这些是库的**必需依赖**，
因为"效果优先"是本项目的既定目标。
"""

from __future__ import annotations

from typing import Any, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

__all__ = [
    "scatterplot",
    "boxplot",
    "violinplot",
    "barplot",
    "lineplot",
    "histplot",
    "regplot",
    "roc_curve",
    "corr_heatmap",
    "pairplot_grid",
    "stackplot",
    "errorbar_line",
    "facet_grid",
]


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------

def _to_frame(
    data: Any, x: str | None, y: str | None, hue: str | None = None
) -> pd.DataFrame:
    """把各种输入统一成 DataFrame。

    支持三种调用方式：
    1. ``data=df, x="col", y="col"``      —— 标准 DataFrame 接口
    2. ``data={"x": [...], "y": [...]}``  —— 字典，自动转 DataFrame
    3. ``x=[...], y=[...]``               —— 直接给数组（等价于方式 2）
    """
    if data is not None:
        if isinstance(data, pd.DataFrame):
            return data
        return pd.DataFrame(data)

    # 方式 3：x / y 直接是数组
    if x is not None and not isinstance(x, str):
        xs = np.asarray(x)
        if isinstance(y, np.ndarray) or (isinstance(y, (list, tuple)) and y is not None):
            ys = np.asarray(y)
            frame = pd.DataFrame({"__x__": xs, "__y__": ys})
            frame.attrs["_xkey"] = "__x__"
            frame.attrs["_ykey"] = "__y__"
            return frame

    raise ValueError(
        "需要提供 data=DataFrame，或直接传入 x=数组, y=数组。"
    )


def _column(frame: pd.DataFrame, key: str | None, default: str) -> str:
    """解析列名：若调用方直接传了数组，则回退到内部占位列名。"""
    if isinstance(key, str):
        return key
    return frame.attrs.get(f"_{default}key", default)


def _sig_text(p: float) -> str:
    """把 P 值转成星号标注，这是生物学论文的通用惯例。"""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


# ---------------------------------------------------------------------------
# 散点图与回归
# ---------------------------------------------------------------------------

def scatterplot(
    data: Any = None,
    x: str | None = None,
    y: str | None = None,
    *,
    hue: str | None = None,
    size: str | None = None,
    alpha: float = 0.75,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """散点图，支持按类别着色（``hue``）与按数值定尺寸（``size``）。

    参数
    ----
    data : DataFrame 或 dict
        数据源。
    x, y : str
        横纵坐标对应的列名。
    hue : str, 可选
        按该列分类着色，自动生成图例。
    size : str, 可选
        按该列数值决定点大小（气泡图）。

    返回
    ----
    (fig, ax)
    """
    frame = _to_frame(data, x, y, hue)
    xk = _column(frame, x, "x")
    yk = _column(frame, y, "y")

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    if hue is not None:
        for label, group in frame.groupby(hue):
            sizes = None
            if size is not None:
                vals = group[size].astype(float)
                span = vals.max() - vals.min()
                # 归一化到 30~300 平方点，避免全图一个尺寸。
                sizes = 30 + (vals - vals.min()) / span * 270 if span else None
            ax.scatter(group[xk], group[yk], s=sizes, alpha=alpha, label=str(label))
        ax.legend(title=hue)
    else:
        sizes = None
        if size is not None:
            vals = frame[size].astype(float)
            span = vals.max() - vals.min()
            sizes = 30 + (vals - vals.min()) / span * 270 if span else None
        ax.scatter(frame[xk], frame[yk], s=sizes, alpha=alpha)

    ax.set_xlabel(xlabel or xk)
    ax.set_ylabel(ylabel or yk)
    if title:
        ax.set_title(title)
    return fig, ax


def regplot(
    data: Any = None,
    x: str | None = None,
    y: str | None = None,
    *,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    show_stat: bool = True,
    ax: Any = None,
):
    """散点图 + 线性回归线 + 统计标注（R² 与 P 值）。

    这是论文里最常见的"相关性"图。P 值超过 0.05 时不加星号，
    避免对弱相关做过度解读。

    返回
    ----
    (fig, ax)
    """
    from scipy import stats

    frame = _to_frame(data, x, y)
    xk = _column(frame, x, "x")
    yk = _column(frame, y, "y")

    xs = frame[xk].astype(float).to_numpy()
    ys = frame[yk].astype(float).to_numpy()

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    ax.scatter(xs, ys, alpha=0.7)

    # 线性拟合
    slope, intercept, r_value, p_value, _ = stats.linregress(xs, ys)
    xs_line = np.linspace(xs.min(), xs.max(), 100)
    ax.plot(xs_line, slope * xs_line + intercept, linewidth=1.8)

    if show_stat:
        r2 = r_value ** 2
        text = f"$R^2$ = {r2:.3f}\n$P$ = {p_value:.3g}"
        if p_value < 0.05:
            text += f"  {_sig_text(p_value)}"
        # 放在左上角，避开数据密集区。
        ax.text(
            0.05, 0.95, text,
            transform=ax.transAxes, va="top", ha="left",
            bbox={"boxstyle": "round,pad=0.4", "facecolor": "white",
                  "edgecolor": "0.7", "alpha": 0.9},
        )

    ax.set_xlabel(xlabel or xk)
    ax.set_ylabel(ylabel or yk)
    if title:
        ax.set_title(title)
    return fig, ax


# ---------------------------------------------------------------------------
# 分布类图
# ---------------------------------------------------------------------------

def boxplot(
    data: Any = None,
    x: str | None = None,
    y: str | None = None,
    *,
    hue: str | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    show_points: bool = True,
    ax: Any = None,
):
    """箱线图，可选叠加原始散点（``show_points``）。

    叠加散点是论文投稿的推荐做法——箱线图只呈现分位数，
    点出来才能看出样本量与分布形态。

    返回
    ----
    (fig, ax)
    """
    frame = _to_frame(data, x, y)
    xk = _column(frame, x, "x")
    yk = _column(frame, y, "y")

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    groups = [g[yk].astype(float).to_numpy() for _, g in frame.groupby(xk)]
    labels = [str(k) for k, _ in frame.groupby(xk)]

    bp = ax.boxplot(
        groups, tick_labels=labels, patch_artist=True, widths=0.55,
        medianprops={"linewidth": 1.6, "color": "0.2"},
        flierprops={"marker": "", "linestyle": "none"},
    )

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, box in enumerate(bp["boxes"]):
        box.set_facecolor(colors[i % len(colors)])
        box.set_alpha(0.65)
        box.set_edgecolor("0.3")

    if show_points:
        rng = np.random.default_rng(0)
        for i, values in enumerate(groups):
            # 横向抖动，避免点重叠成一条线。
            jitter = rng.normal(0, 0.06, size=len(values))
            ax.scatter(
                np.full(len(values), i + 1) + jitter, values,
                s=14, color="0.25", alpha=0.6, zorder=3,
            )

    ax.set_xlabel(xlabel or xk)
    ax.set_ylabel(ylabel or yk)
    if title:
        ax.set_title(title)
    return fig, ax


def violinplot(
    data: Any = None,
    x: str | None = None,
    y: str | None = None,
    *,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    inner: str = "box",
    ax: Any = None,
):
    """小提琴图：展示分布密度 + 内部箱线。

    相比箱线图，小提琴图能看出"双峰"这类箱线图掩盖的形态。

    返回
    ----
    (fig, ax)
    """
    frame = _to_frame(data, x, y)
    xk = _column(frame, x, "x")
    yk = _column(frame, y, "y")

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    groups = [g[yk].astype(float).to_numpy() for _, g in frame.groupby(xk)]
    labels = [str(k) for k, _ in frame.groupby(xk)]

    parts = ax.violinplot(groups, showmedians=True, widths=0.75)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, body in enumerate(parts["bodies"]):
        body.set_facecolor(colors[i % len(colors)])
        body.set_alpha(0.6)
        body.set_edgecolor("0.3")
    for key in ("cmedians", "cbars", "cmins", "cmaxes"):
        if key in parts:
            parts[key].set_edgecolor("0.2")
            parts[key].set_linewidth(1.2)

    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    ax.set_xlabel(xlabel or xk)
    ax.set_ylabel(ylabel or yk)
    if title:
        ax.set_title(title)
    return fig, ax


# ---------------------------------------------------------------------------
# 分组比较类图
# ---------------------------------------------------------------------------

def _sem(values: np.ndarray) -> float | None:
    """标准误（SEM）。样本量不足 2 时无法估计，返回 ``None``。"""
    n = len(values)
    if n < 2:
        return None
    return float(values.std(ddof=1) / np.sqrt(n))


def _draw_bracket(ax, x1: float, x2: float, y: float, h: float,
                  text: str, *, pad: float) -> None:
    """在两个位置之间画显著性括号并标注。"""
    ax.plot(
        [x1, x1, x2, x2], [y, y + h, y + h, y],
        linewidth=0.9, color="#3A3A3A", clip_on=False, zorder=5,
    )
    ax.text(
        (x1 + x2) / 2, y + h, text,
        ha="center", va="bottom", color="#1A1A1A",
        fontsize=pad, zorder=5,
    )


def barplot(
    data: Any = None,
    x: str | None = None,
    y: str | None = None,
    *,
    hue: str | None = None,
    errorbar: str | None = "auto",
    show_points: bool = False,
    annotate: Sequence[tuple] | dict | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """分组柱状图，默认带误差棒，可选叠加散点与显著性标注。

    默认行为刻意贴近科研惯例：**只要每组有重复观测，就自动标出标准误**。
    不标误差的柱状图在正式场合是不完整的。

    参数
    ----
    errorbar : str 或 None, 默认 "auto"
        ``"auto"`` 按标准误（SEM）自动计算；给列名则读取该列的均值作为误差；
        置为 ``None`` 则不画误差棒。
    show_points : bool, 默认 False
        是否叠加原始观测散点（横向抖动）。样本量可见，是投稿推荐做法。
    annotate : 序列, 可选
        显著性标注。每项为 ``(组A, 组B)`` 时自动做 t 检验取星号，
        或 ``(组A, 组B, "文本")`` 直接指定标注内容。
        例：``annotate=[("对照组", "处理组1"), ("处理组1", "处理组2", "***")]``

    返回
    ----
    (fig, ax)
    """
    from scipy import stats as _stats

    frame = _to_frame(data, x, y)
    xk = _column(frame, x, "x")
    yk = _column(frame, y, "y")

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    cats = list(dict.fromkeys(frame[xk]))
    xpos = np.arange(len(cats))
    #: 记录每个 (类别, 分组层级) 的原始观测，供显著性检验与散点叠加使用
    raw: dict[tuple, np.ndarray] = {}
    #: 记录每个 (类别, 分组层级) 对应的横向位置
    pos: dict[tuple, float] = {}

    def _err(sub: pd.DataFrame) -> float | None:
        if errorbar is None:
            return None
        if errorbar == "auto":
            return _sem(sub[yk].astype(float).to_numpy())
        return float(sub[errorbar].astype(float).mean())

    if hue is None:
        means, errs = [], []
        for c in cats:
            sub = frame.loc[frame[xk] == c]
            means.append(float(sub[yk].astype(float).mean()))
            errs.append(_err(sub))
            raw[(c, None)] = sub[yk].astype(float).to_numpy()
        yerr = None if all(e is None for e in errs) else errs
        ax.bar(xpos, means, width=0.62, yerr=yerr,
               capsize=3, error_kw={"linewidth": 0.9, "ecolor": "#3A3A3A"})
        for i, c in enumerate(cats):
            pos[(c, None)] = float(xpos[i])
    else:
        levels = list(dict.fromkeys(frame[hue]))
        width = 0.78 / len(levels)
        for i, lv in enumerate(levels):
            sub_all = frame[frame[hue] == lv]
            means, errs = [], []
            for c in cats:
                sub = sub_all.loc[sub_all[xk] == c]
                means.append(float(sub[yk].astype(float).mean()))
                errs.append(_err(sub))
                raw[(c, str(lv))] = sub[yk].astype(float).to_numpy()
            yerr = None if all(e is None for e in errs) else errs
            offset = (i - (len(levels) - 1) / 2) * width
            ax.bar(xpos + offset, means, width=width, label=str(lv),
                   yerr=yerr, capsize=2.5,
                   error_kw={"linewidth": 0.9, "ecolor": "#3A3A3A"})
            for j, c in enumerate(cats):
                pos[(c, str(lv))] = float(xpos[j] + offset)
        ax.legend(title=hue)

    # --- 叠加原始散点：让样本量与分布形态可见 ---
    if show_points:
        rng = np.random.default_rng(0)
        for key, values in raw.items():
            if len(values) == 0:
                continue
            jitter = rng.normal(0, 0.035, size=len(values))
            ax.scatter(
                np.full(len(values), pos[key]) + jitter, values,
                s=9, color="#2B2B2B", alpha=0.55, linewidths=0,
                zorder=4,
            )

    # --- 显著性标注：柱顶之上逐层堆叠括号 ---
    if annotate:
        pairs = (
            [(k, v) for k, v in annotate.items()] if isinstance(annotate, dict)
            else list(annotate)
        )
        ax.relim()
        ax.autoscale_view()
        ylo, yhi = ax.get_ylim()
        span = yhi - ylo
        ax.set_ylim(top=yhi + span * (0.10 + 0.11 * len(pairs)))

        base = yhi + span * 0.03
        for level, item in enumerate(pairs):
            a, b = item[0], item[1]
            if len(item) >= 3:
                text = str(item[2])
            else:
                va = raw.get((a, None), np.array([]))
                vb = raw.get((b, None), np.array([]))
                if len(va) >= 2 and len(vb) >= 2:
                    _, p = _stats.ttest_ind(va, vb, equal_var=False)
                    text = _sig_text(float(p))
                else:
                    text = "n/a"
            y = base + level * span * 0.10
            _draw_bracket(
                ax, pos.get((a, None), 0), pos.get((b, None), 1),
                y, span * 0.022, text, pad=plt.rcParams["font.size"] * 0.85,
            )

    ax.set_xticks(xpos)
    ax.set_xticklabels([str(c) for c in cats])
    ax.set_xlabel(xlabel or xk)
    ax.set_ylabel(ylabel or yk)
    if title:
        ax.set_title(title)
    return fig, ax


def histplot(
    data: Any = None,
    x: str | None = None,
    *,
    bins: int = 20,
    hue: str | None = None,
    density: bool = False,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """直方图，可选按类别分层（``hue``）。

    返回
    ----
    (fig, ax)
    """
    frame = _to_frame(data, x, None)
    xk = _column(frame, x, "x")

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    if hue is not None:
        for label, group in frame.groupby(hue):
            ax.hist(group[xk].astype(float), bins=bins, density=density,
                    alpha=0.55, label=str(label))
        ax.legend(title=hue)
    else:
        ax.hist(frame[xk].astype(float), bins=bins, density=density, alpha=0.8)

    ax.set_xlabel(xlabel or xk)
    ax.set_ylabel(ylabel or ("频率密度" if density else "频数"))
    if title:
        ax.set_title(title)
    return fig, ax


# ---------------------------------------------------------------------------
# 曲线类图
# ---------------------------------------------------------------------------

def roc_curve(
    y_true: Any,
    y_score: Any,
    *,
    label: str = "",
    auc: float | None = None,
    xlabel: str = "假阳性率 (1 - 特异度)",
    ylabel: str = "真阳性率 (灵敏度)",
    title: str = "ROC 曲线",
    ax: Any = None,
):
    """ROC 曲线，并标注 AUC。

    AUC 用梯形法数值积分计算，**不依赖 scikit-learn**，保持依赖精简。

    参数
    ----
    y_true : 序列
        真实标签（0/1 或 False/True）。
    y_score : 序列
        预测得分（概率或决策值）。

    返回
    ----
    (fig, ax)
    """
    yt = np.asarray(y_true).astype(int)
    ys = np.asarray(y_score, dtype=float)

    # 按得分降序排列，逐个作为阈值计算 TPR/FPR。
    order = np.argsort(-ys)
    yt = yt[order]
    ys = ys[order]

    positives = yt.sum()
    negatives = len(yt) - positives

    tprs, fprs = [0.0], [0.0]
    tp = fp = 0
    for i in range(len(ys)):
        if yt[i] == 1:
            tp += 1
        else:
            fp += 1
        tprs.append(tp / positives if positives else 0.0)
        fprs.append(fp / negatives if negatives else 0.0)
    tprs.append(1.0)
    fprs.append(1.0)

    tprs = np.asarray(tprs)
    fprs = np.asarray(fprs)

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    auc_val = auc if auc is not None else float(np.trapezoid(tprs, fprs))
    ax.plot(fprs, tprs, linewidth=2.0, label=f"{label} AUC = {auc_val:.3f}".strip())
    ax.plot([0, 1], [0, 1], "--", linewidth=1.0, color="0.6", label="随机猜测")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.legend(loc="lower right")
    if title:
        ax.set_title(title)
    return fig, ax


def errorbar_line(
    data: Any = None,
    x: str | None = None,
    y: str | None = None,
    *,
    err: str | None = None,
    hue: str | None = None,
    band: bool = False,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """折线图 + 误差棒 / 置信带。

    这是时序趋势与实验结果的标准呈现方式。``band=True`` 时用半透明
    误差带代替误差棒，视觉效果更柔和，适合连续曲线。

    返回
    ----
    (fig, ax)
    """
    frame = _to_frame(data, x, y)
    xk = _column(frame, x, "x")
    yk = _column(frame, y, "y")

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    def _draw(sub, label=None):
        sub = sub.sort_values(xk)
        xs = sub[xk].astype(float).to_numpy()
        ys = sub[yk].astype(float).to_numpy()
        es = sub[err].astype(float).to_numpy() if err else None
        line, = ax.plot(xs, ys, marker="o", label=label)
        if es is not None:
            if band:
                ax.fill_between(xs, ys - es, ys + es, alpha=0.2,
                                color=line.get_color())
            else:
                ax.errorbar(xs, ys, yerr=es, fmt="none", capsize=4,
                            color=line.get_color())

    if hue is not None:
        for label, group in frame.groupby(hue):
            _draw(group, str(label))
        ax.legend(title=hue)
    else:
        _draw(frame)

    ax.set_xlabel(xlabel or xk)
    ax.set_ylabel(ylabel or yk)
    if title:
        ax.set_title(title)
    return fig, ax


# ---------------------------------------------------------------------------
# 矩阵类图
# ---------------------------------------------------------------------------

def corr_heatmap(
    data: Any,
    *,
    method: str = "pearson",
    annot: bool = True,
    mask_upper: bool = False,
    labels: Sequence[str] | None = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "相关性热图",
    cmap: str = "auto",
    ax: Any = None,
):
    """相关性矩阵热图。

    参数
    ----
    data : DataFrame
        数值型数据，每列一个变量。
    method : str, 默认 "pearson"
        ``"pearson"`` / ``"spearman"`` / ``"kendall"``。
    mask_upper : bool, 默认 False
        是否遮住上三角。相关矩阵是对称的，遮一半更简洁。
    cmap : str, 默认 "auto"
        ``"auto"`` 自动构造「蓝—白—红」发散色带；
        也可传配色名（见 :func:`modelfig.palette_names`）或任意 matplotlib 色带名。

    返回
    ----
    (fig, ax)
    """
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    numeric = frame.select_dtypes(include=[np.number])
    corr = numeric.corr(method=method)

    if ax is None:
        fig, ax = plt.subplots(figsize=(6.5, 5.5))
    else:
        fig = ax.figure

    # 相关矩阵需要「发散型」色带：负相关偏蓝、0 为白、正相关偏红。
    # 直接取渐变配色的两端再加白色构造，色带随当前配色走。
    from matplotlib.colors import LinearSegmentedColormap

    from .palettes import PALETTES, sequential

    if cmap == "auto" or cmap in PALETTES:
        stops = sequential("warm_cool" if cmap == "auto" else cmap)
        cm = LinearSegmentedColormap.from_list(
            "modelfig_div",
            [stops[-3], stops[-1], "#FFFFFF", stops[3], stops[0]],
        )
    else:
        cm = cmap

    matrix = corr.to_numpy()

    if mask_upper:
        # 遮住上三角（不含对角线）。用 NaN 而非另叠一层图：
        # NaN 会被 colormap 渲染为透明，露出白色底，且不会影响色阶范围。
        matrix = np.where(
            np.triu(np.ones_like(matrix, dtype=bool), k=1),
            np.nan,
            matrix,
        )

    im = ax.imshow(matrix, cmap=cm, vmin=-1, vmax=1, aspect="auto")

    names = list(labels) if labels is not None else list(corr.columns)
    ax.set_xticks(np.arange(len(names)))
    ax.set_yticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_yticklabels(names)

    if annot:
        for i in range(len(names)):
            for j in range(len(names)):
                if mask_upper and j > i:
                    continue
                val = matrix[i, j]
                ax.text(
                    j, i, f"{val:.2f}",
                    ha="center", va="center", fontsize=8,
                    color="white" if abs(val) > 0.6 else "black",
                )

    fig.colorbar(im, ax=ax, shrink=0.8, label="相关系数")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return fig, ax


def pairplot_grid(
    data: Any,
    *,
    hue: str | None = None,
    diag: str = "hist",
    title: str = "",
):
    """成对关系矩阵图（散点矩阵 + 对角线分布）。

    用于快速发现多变量之间的相关性与分组可分性。

    返回
    ----
    (fig, axes)
    """
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    numeric = frame.select_dtypes(include=[np.number])

    cols = list(numeric.columns)
    n = len(cols)
    fig, axes = plt.subplots(n, n, figsize=(2.4 * n, 2.4 * n), squeeze=False)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    groups = None
    if hue is not None:
        groups = [(str(k), g) for k, g in frame.groupby(hue)]

    for i in range(n):
        for j in range(n):
            ax = axes[i][j]
            if i == j:
                if diag == "hist":
                    if groups is None:
                        ax.hist(numeric[cols[i]], bins=15, alpha=0.8)
                    else:
                        for gi, (label, g) in enumerate(groups):
                            ax.hist(g[cols[i]].astype(float), bins=15,
                                    alpha=0.5, label=label,
                                    color=colors[gi % len(colors)])
                else:
                    from scipy import stats as _stats
                    vals = numeric[cols[i]].astype(float).to_numpy()
                    kde = _stats.gaussian_kde(vals)
                    xs = np.linspace(vals.min(), vals.max(), 100)
                    ax.plot(xs, kde(xs))
                    ax.fill_between(xs, kde(xs), alpha=0.3)
            else:
                if groups is None:
                    ax.scatter(numeric[cols[j]], numeric[cols[i]], s=12, alpha=0.6)
                else:
                    for gi, (label, g) in enumerate(groups):
                        ax.scatter(g[cols[j]], g[cols[i]], s=12, alpha=0.6,
                                   label=label, color=colors[gi % len(colors)])

            if i == n - 1:
                ax.set_xlabel(cols[j])
            if j == 0:
                ax.set_ylabel(cols[i])

    if hue is not None:
        axes[0][-1].legend(fontsize=8)
    if title:
        fig.suptitle(title, y=0.995)
    return fig, axes


# ---------------------------------------------------------------------------
# 堆叠与分面
# ---------------------------------------------------------------------------

def stackplot(
    data: Any = None,
    x: str | None = None,
    *,
    y: Sequence[str] | None = None,
    kind: str = "bar",
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """堆叠图：``kind="bar"`` 堆叠柱状图，``kind="area"`` 堆积面积图。

    用于展示"总量随时间的构成变化"。

    返回
    ----
    (fig, ax)
    """
    frame = _to_frame(data, x, None)
    xk = _column(frame, x, "x")

    if y is None:
        y = [c for c in frame.columns if c != xk and
             pd.api.types.is_numeric_dtype(frame[c])]

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    if kind == "bar":
        frame.plot(kind="bar", x=xk, y=list(y), stacked=True, ax=ax, width=0.7)
        ax.set_xlabel(xlabel or xk)
    else:
        frame.plot(kind="area", x=xk, y=list(y), stacked=True, ax=ax, alpha=0.85)
        ax.set_xlabel(xlabel or xk)

    ax.set_ylabel(ylabel or "数值")
    ax.legend(title="", ncol=min(len(y), 4))
    if title:
        ax.set_title(title)
    return fig, ax


def facet_grid(
    data: Any = None,
    x: str | None = None,
    y: str | None = None,
    *,
    col: str | None = None,
    kind: str = "line",
    cols: int | None = None,
    xlabel: str = "",
    ylabel: str = "",
):
    """分面网格：按某个分类列拆成多个子图，共享坐标轴。

    参数
    ----
    col : str
        分面依据的列名，每个取值一个子图。
    kind : str, 默认 "line"
        ``"line"`` 折线 / ``"scatter"`` 散点 / ``"bar"`` 柱状。

    返回
    ----
    (fig, axes)
    """
    frame = _to_frame(data, x, y)
    xk = _column(frame, x, "x")
    yk = _column(frame, y, "y")

    if col is None:
        raise ValueError("facet_grid 需要指定 col=分面列名。")

    levels = list(dict.fromkeys(frame[col]))
    n = len(levels)
    ncols = cols or min(n, 3)
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(
        nrows, ncols, figsize=(4 * ncols, 3 * nrows),
        sharex=True, sharey=True, squeeze=False,
    )

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for idx, lv in enumerate(levels):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        sub = frame[frame[col] == lv].sort_values(xk)
        color = colors[idx % len(colors)]

        if kind == "line":
            ax.plot(sub[xk], sub[yk], marker="o", color=color)
        elif kind == "scatter":
            ax.scatter(sub[xk], sub[yk], color=color)
        else:
            ax.bar(sub[xk].astype(str), sub[yk], color=color)

        ax.set_title(f"{col}={lv}")
        if r == nrows - 1:
            ax.set_xlabel(xlabel or xk)
        if c == 0:
            ax.set_ylabel(ylabel or yk)

    # 关掉多余的空白子图
    for idx in range(n, nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r][c].set_visible(False)

    return fig, axes


def lineplot(
    data: Any = None,
    x: str | None = None,
    y: str | None = None,
    *,
    hue: str | None = None,
    markers: bool = True,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    ax: Any = None,
):
    """折线图（DataFrame 接口），支持按分类列分多条线。

    与通用层 :func:`modelfig.line` 的区别：这里直接吃 DataFrame，
    用 ``hue`` 指定分类列即可自动分组，无需手工拆分数组。

    返回
    ----
    (fig, ax)
    """
    frame = _to_frame(data, x, y)
    xk = _column(frame, x, "x")
    yk = _column(frame, y, "y")

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    marker = "o" if markers else None

    if hue is not None:
        for label, group in frame.groupby(hue):
            g = group.sort_values(xk)
            ax.plot(g[xk], g[yk], marker=marker, label=str(label))
        ax.legend(title=hue)
    else:
        g = frame.sort_values(xk)
        ax.plot(g[xk], g[yk], marker=marker)

    ax.set_xlabel(xlabel or xk)
    ax.set_ylabel(ylabel or yk)
    if title:
        ax.set_title(title)
    return fig, ax
