"""冒烟测试：确认每个绘图函数在每套风格/配色下都能正常出图且不抛异常。

测试策略：不比对像素、不做视觉回归，只验证
1. 函数能被调用；
2. 返回的图形对象类型正确；
3. 边界情况能给出明确报错。

CI 上跑得动、跑得快，是这套测试的首要目标。
"""

from __future__ import annotations

import matplotlib

# 必须在导入 pyplot 之前切到无界面后端，否则 CI 环境会因缺少显示器而失败。
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import modelfig as mf


@pytest.fixture(autouse=True)
def _clean():
    """每个用例前后清空画布，避免图形对象在用例之间串扰。"""
    yield
    plt.close("all")


@pytest.fixture
def df():
    """构造一份测试用 DataFrame：两组、各 5 个样本。"""
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "组别": ["A"] * 5 + ["B"] * 5,
        "取值": np.concatenate([rng.normal(5, 1, 5), rng.normal(7, 1, 5)]),
        "批次": ["甲", "乙", "甲", "乙", "甲", "乙", "甲", "乙", "甲", "乙"],
        "误差": np.full(10, 0.5),
        "时间": list(range(5)) * 2,
    })


@pytest.fixture
def wide_df():
    """宽表：用于堆叠图与相关性热图。"""
    return pd.DataFrame({
        "时间": [1, 2, 3, 4],
        "甲": [1, 2, 3, 4],
        "乙": [2, 3, 4, 5],
        "丙": [3, 4, 5, 6],
    })


# ---------------------------------------------------------------------------
# 风格与配色系统
# ---------------------------------------------------------------------------

def test_style_names_contains_builtins():
    names = mf.style_names()
    assert {"paper", "slide", "poster"} <= set(names)


def test_palette_names_contains_builtins():
    names = mf.palette_names()
    assert {"soft_academic", "warm_cool", "misty_blue", "soft_multi"} <= set(names)


@pytest.mark.parametrize("style", ["paper", "slide", "poster"])
def test_set_style_activates(style):
    assert mf.set_style(style) == style
    assert mf.current_style() == style


@pytest.mark.parametrize("palette", ["soft_academic", "warm_cool", "misty_blue", "soft_multi"])
def test_set_style_with_palette(palette):
    mf.set_style("paper", palette=palette)
    assert mf.current_palette() == palette
    # 配色应真的写进了 prop_cycle
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    assert len(colors) >= 6


def test_set_style_rejects_unknown():
    with pytest.raises(KeyError):
        mf.set_style("不存在的风格")


def test_set_style_rejects_unknown_palette():
    with pytest.raises(KeyError):
        mf.set_style("paper", palette="不存在的配色")


def test_register_style_roundtrip():
    mf.register_style("_test_style", {"font.size": 13})
    assert "_test_style" in mf.style_names()
    mf.set_style("_test_style", palette=None)
    assert plt.rcParams["font.size"] == 13


def test_register_palette_roundtrip():
    mf.register_palette("_test_pal", ["#005BAC", "#E60012"])
    assert "_test_pal" in mf.palette_names()
    assert mf.categorical("_test_pal") == ["#005BAC", "#E60012"]


def test_list_palettes_shape():
    rows = mf.list_palettes()
    assert all(len(r) == 5 for r in rows)


# ---------------------------------------------------------------------------
# 字体
# ---------------------------------------------------------------------------

def test_available_fonts_returns_list():
    assert isinstance(mf.available_chinese_fonts(), list)


def test_setup_chinese_font_sets_rcparams():
    result = mf.setup_chinese_font()
    if result is not None:
        assert plt.rcParams["axes.unicode_minus"] is False


# ---------------------------------------------------------------------------
# 通用层绘图（数组接口）
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("style", ["paper", "slide", "poster"])
def test_line_single_and_multi(style):
    mf.set_style(style)
    fig, ax = mf.line([1, 2, 3], [1, 4, 9])
    assert fig is not None and ax is not None

    fig, ax = mf.line([1, 2, 3], [[1, 2, 3], [3, 2, 1]], labels=["a", "b"])
    assert len(ax.get_lines()) == 2


def test_bar_grouped():
    mf.set_style("paper")
    fig, ax = mf.bar(["x", "y"], [[1, 2], [3, 4]], labels=["g1", "g2"])
    assert len(ax.patches) == 4


def test_dual_axis_has_twin():
    mf.set_style("paper")
    fig, ax = mf.dual_axis([1, 2, 3], [1, 2, 3], [3, 2, 1])
    assert hasattr(ax, "right_ax")


def test_heatmap_annotations():
    mf.set_style("paper")
    fig, ax = mf.heatmap(np.eye(3), annot=True)
    assert len(ax.texts) == 9


def test_radar_requires_three_dims():
    mf.set_style("paper")
    with pytest.raises(ValueError):
        mf.radar(["a", "b"], [1, 2])


def test_radar_multi_series():
    mf.set_style("paper")
    fig, ax = mf.radar(["a", "b", "c"], [[1, 2, 3], [3, 2, 1]], labels=["s1", "s2"])
    assert len(ax.get_lines()) == 2


def test_scatter_with_sizes():
    mf.set_style("paper")
    fig, ax = mf.scatter([1, 2, 3], [2, 3, 4], sizes=[10, 50, 200])
    assert ax.collections


def test_box_and_violin():
    mf.set_style("paper")
    fig, ax = mf.box([[1, 2, 3, 4], [2, 3, 4, 5]], labels=["g1", "g2"])
    assert len(ax.patches) >= 2
    fig, ax = mf.violin([[1, 2, 3, 4], [2, 3, 4, 5]], labels=["g1", "g2"])
    assert ax.collections


def test_stacked_bar():
    mf.set_style("paper")
    fig, ax = mf.stacked_bar(["x", "y"], [[1, 2], [3, 4]], labels=["s1", "s2"])
    assert len(ax.patches) == 4


def test_errorbar_band_and_bars():
    mf.set_style("paper")
    fig, ax = mf.errorbar([1, 2, 3], [1, 2, 3], [0.1, 0.2, 0.1])
    assert ax.get_lines()
    fig, ax = mf.errorbar([1, 2, 3], [1, 2, 3], [0.1, 0.2, 0.1], band=True)
    assert ax.collections


# ---------------------------------------------------------------------------
# 统计层绘图（DataFrame 接口）
# ---------------------------------------------------------------------------

def test_scatterplot_with_hue(df):
    mf.set_style("paper")
    fig, ax = mf.scatterplot(df, x="时间", y="取值", hue="组别")
    assert ax.get_legend() is not None


def test_scatterplot_accepts_dict():
    mf.set_style("paper")
    fig, ax = mf.scatterplot(data={"a": [1, 2, 3], "b": [3, 2, 1]}, x="a", y="b")
    assert ax.collections


def test_regplot_adds_stat_text(df):
    mf.set_style("paper")
    fig, ax = mf.regplot(df, x="时间", y="取值")
    assert ax.texts  # R² / P 值标注


def test_boxplot_with_points(df):
    mf.set_style("paper")
    fig, ax = mf.boxplot(df, x="组别", y="取值", show_points=True)
    assert ax.collections


def test_violinplot_runs(df):
    mf.set_style("paper")
    fig, ax = mf.violinplot(df, x="组别", y="取值")
    assert ax.collections


def test_barplot_plain_and_grouped(df):
    mf.set_style("paper")
    fig, ax = mf.barplot(df, x="组别", y="取值")
    assert len(ax.patches) == 2

    plt.close("all")
    fig, ax = mf.barplot(df, x="组别", y="取值", hue="批次")
    assert ax.get_legend() is not None


def test_histplot_plain_and_hue(df):
    mf.set_style("paper")
    fig, ax = mf.histplot(df, x="取值", bins=5)
    assert len(ax.patches) == 5

    plt.close("all")
    fig, ax = mf.histplot(df, x="取值", bins=5, hue="组别")
    assert ax.get_legend() is not None


def test_lineplot_with_hue(df):
    mf.set_style("paper")
    fig, ax = mf.lineplot(df, x="时间", y="取值", hue="组别")
    assert len(ax.get_lines()) == 2


def test_roc_curve_auc():
    mf.set_style("paper")
    y_true = [0, 0, 0, 1, 1, 1]
    y_score = [0.1, 0.4, 0.35, 0.8, 0.65, 0.9]
    fig, ax = mf.roc_curve(y_true, y_score)
    assert ax.get_legend() is not None


def test_errorbar_line_band(df):
    mf.set_style("paper")
    fig, ax = mf.errorbar_line(df, x="时间", y="取值", err="误差", hue="组别", band=True)
    assert ax.collections


def test_corr_heatmap(wide_df):
    mf.set_style("paper")
    fig, ax = mf.corr_heatmap(wide_df, mask_upper=True)
    assert ax.images


def test_pairplot_grid():
    mf.set_style("paper")
    frame = pd.DataFrame({"a": [1, 2, 3, 4], "b": [4, 3, 2, 1], "c": [1, 3, 2, 4]})
    fig, axes = mf.pairplot_grid(frame)
    assert axes.shape == (3, 3)


def test_stackplot_bar_and_area(wide_df):
    mf.set_style("paper")
    fig, ax = mf.stackplot(wide_df, x="时间", y=["甲", "乙", "丙"], kind="bar")
    assert ax.patches
    plt.close("all")
    fig, ax = mf.stackplot(wide_df, x="时间", y=["甲", "乙", "丙"], kind="area")
    assert ax.collections


def test_facet_grid(df):
    mf.set_style("paper")
    fig, axes = mf.facet_grid(df, x="时间", y="取值", col="组别", kind="line")
    assert axes.shape[0] >= 1


def test_facet_grid_requires_col(df):
    mf.set_style("paper")
    with pytest.raises(ValueError):
        mf.facet_grid(df, x="时间", y="取值")


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def test_save_writes_file(tmp_path):
    mf.set_style("paper")
    mf.line([1, 2, 3], [1, 4, 9])
    out = tmp_path / "fig.png"
    assert mf.save(str(out)) == str(out)
    assert out.exists() and out.stat().st_size > 0


def test_load_csv(tmp_path):
    mf.set_style("paper")
    p = tmp_path / "d.csv"
    p.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    frame = mf.load_csv(str(p))
    assert list(frame.columns) == ["a", "b"]
    assert len(frame) == 2
