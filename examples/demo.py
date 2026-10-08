"""一键生成全部示例图，展示风格 × 配色 × 图种的各种组合。

运行方式
--------
    python examples/demo.py

产物写入 ``examples/output/``，命名规则 ``{风格}_{配色}_{图名}.png``。

分两部分：
* 第一部分：同一份数据在「多套风格 × 多套配色」下的对比（体现风格系统）
* 第二部分：全部统计图种各出一张（体现图库广度）
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

# 允许在"未 pip install"的情况下直接运行本脚本。
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import matplotlib.pyplot as plt

import modelfig as mf

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def _out(name: str) -> str:
    return os.path.join(OUT_DIR, f"{name}.png")


# ---------------------------------------------------------------------------
# 示例数据
# ---------------------------------------------------------------------------

def sample_trend():
    """趋势数据：3 条曲线 × 8 个时间点。"""
    x = np.arange(1, 9)
    y = np.vstack([
        [2.0, 3.1, 4.2, 5.0, 6.3, 7.1, 8.4, 9.2],
        [1.0, 1.8, 3.0, 3.6, 5.0, 5.4, 6.8, 7.0],
        [0.5, 1.2, 1.6, 2.8, 3.1, 4.4, 4.9, 6.0],
    ])
    return x, y


def sample_group_df():
    """分组数据：2 组 × 3 批次 × 若干样本。"""
    rng = np.random.default_rng(7)
    rows = []
    for grp, mu in (("对照组", 5.0), ("实验组", 6.6)):
        for batch in ("批次一", "批次二", "批次三"):
            for _ in range(6):
                rows.append({
                    "组别": grp,
                    "批次": batch,
                    "指标值": rng.normal(mu, 0.9),
                })
    return pd.DataFrame(rows)


def sample_corr_df():
    """相关性数据：5 个相关变量。"""
    rng = np.random.default_rng(3)
    base = rng.normal(size=(40, 5))
    mix = base @ np.array([
        [1.0, 0.7, 0.4, 0.1, 0.0],
        [0.0, 0.6, 0.8, 0.3, 0.0],
        [0.0, 0.0, 0.5, 0.7, 0.2],
        [0.0, 0.0, 0.0, 0.6, 0.5],
        [0.0, 0.0, 0.0, 0.0, 0.4],
    ])
    return pd.DataFrame(
        mix, columns=["指标A", "指标B", "指标C", "指标D", "指标E"]
    )


# ---------------------------------------------------------------------------
# 第一部分：风格 × 配色 对比
# ---------------------------------------------------------------------------

def demo_style_palette_matrix():
    """同一份折线数据，在 3 套风格 × 2 套配色下各出一张。"""
    x, y = sample_trend()
    combos = [
        ("paper", "soft_academic"),
        ("paper", "misty_blue"),
        ("slide", "soft_academic"),
        ("slide", "soft_multi"),
        ("poster", "warm_cool"),
        ("poster", "misty_blue"),
    ]
    for style, palette in combos:
        mf.set_style(style, palette=palette)
        mf.line(
            x, y, labels=["方案 A", "方案 B", "方案 C"],
            xlabel="迭代轮次", ylabel="目标值", title="算法收敛曲线对比",
        )
        mf.save(_out(f"对比_{style}_{palette}_折线"))
        plt.close("all")


# ---------------------------------------------------------------------------
# 第二部分：图种展示
# ---------------------------------------------------------------------------

def demo_basic():
    """通用层：折线、柱状、双轴、热力图、雷达、散点、箱线、小提琴。"""
    x, y = sample_trend()

    mf.line(x, y, labels=["方案 A", "方案 B", "方案 C"],
            xlabel="迭代轮次", ylabel="目标值", title="折线对比图")
    mf.save(_out("图种_折线对比图"))
    plt.close("all")

    mf.bar(["准确率", "召回率", "F1", "AUC"],
           [[0.82, 0.78, 0.80, 0.85], [0.88, 0.84, 0.86, 0.90],
            [0.91, 0.89, 0.90, 0.93]],
           labels=["方法一", "方法二", "方法三"],
           xlabel="评价指标", ylabel="得分", title="分组柱状图")
    mf.save(_out("图种_分组柱状图"))
    plt.close("all")

    years = np.arange(2015, 2025)
    output = np.array([120, 135, 148, 160, 155, 172, 190, 205, 228, 246], dtype=float)
    growth = np.array([0.0, 0.125, 0.096, 0.081, -0.031, 0.110, 0.105, 0.079, 0.112, 0.079])
    mf.dual_axis(years, output, growth, label_left="产量（万吨）",
                 label_right="同比增长率", xlabel="年份", title="双 Y 轴图")
    mf.save(_out("图种_双轴图"))
    plt.close("all")

    labels = [f"指标{i}" for i in range(1, 7)]
    corr = np.corrcoef(np.random.default_rng(42).normal(size=(6, 6)))
    mf.heatmap(corr, xlabels=labels, ylabels=labels,
               xlabel="指标", ylabel="指标", title="相关性热力图")
    mf.save(_out("图种_热力图"))
    plt.close("all")

    mf.radar(["成本", "效率", "稳定性", "可扩展性", "易用性"],
             [[8, 6, 7, 5, 9], [6, 9, 8, 7, 6], [7, 7, 9, 8, 7]],
             labels=["方案甲", "方案乙", "方案丙"], title="雷达图")
    mf.save(_out("图种_雷达图"))
    plt.close("all")

    rng = np.random.default_rng(1)
    mf.scatter(rng.normal(5, 1, 60), rng.normal(5, 1, 60),
               xlabel="变量 X", ylabel="变量 Y", title="散点图")
    mf.save(_out("图种_散点图"))
    plt.close("all")

    rng = np.random.default_rng(2)
    mf.box([rng.normal(5, 1, 30), rng.normal(6.5, 1.2, 30), rng.normal(5.8, 0.8, 30)],
           labels=["对照组", "低剂量", "高剂量"],
           xlabel="处理", ylabel="响应值", title="箱线图（叠加散点）")
    mf.save(_out("图种_箱线图"))
    plt.close("all")

    rng = np.random.default_rng(3)
    mf.violin([rng.normal(5, 1, 40), rng.normal(6.5, 1.6, 40), rng.normal(5.8, 0.7, 40)],
              labels=["对照组", "低剂量", "高剂量"],
              xlabel="处理", ylabel="响应值", title="小提琴图")
    mf.save(_out("图种_小提琴图"))
    plt.close("all")


def demo_stats():
    """统计层：散点回归、显著性柱状、误差带、堆叠图、分面、ROC、相关热图、配对矩阵。"""
    df = sample_group_df()

    # 回归图改用两列真有相关性的变量（用指标值与加噪版本构造散点）。
    rng = np.random.default_rng(11)
    reg_df = pd.DataFrame({
        "X 变量": rng.normal(0, 1, 50),
    })
    reg_df["Y 变量"] = 1.6 * reg_df["X 变量"] + rng.normal(0, 0.7, 50)
    mf.regplot(reg_df, x="X 变量", y="Y 变量",
               xlabel="X 变量", ylabel="Y 变量", title="散点 + 线性回归")
    mf.save(_out("统计_散点回归图"))
    plt.close("all")

    mf.barplot(df, x="组别", y="指标值", hue="批次",
               ylabel="指标值", title="分组柱状图（含误差棒）")
    mf.save(_out("统计_分组柱状图"))
    plt.close("all")

    mf.boxplot(df, x="组别", y="指标值", ylabel="指标值", title="箱线图（DataFrame 接口）")
    mf.save(_out("统计_箱线图"))
    plt.close("all")

    mf.violinplot(df, x="组别", y="指标值", ylabel="指标值", title="小提琴图（DataFrame 接口）")
    mf.save(_out("统计_小提琴图"))
    plt.close("all")

    mf.histplot(df, x="指标值", bins=12, hue="组别",
                xlabel="指标值", title="分层直方图")
    mf.save(_out("统计_直方图"))
    plt.close("all")

    # 误差带折线
    t = np.arange(0, 20)
    trend = pd.DataFrame({
        "时间": np.tile(t, 2),
        "均值": np.concatenate([10 + t * 0.8, 8 + t * 0.5]),
        "标准差": np.concatenate([np.linspace(0.5, 1.2, 20),
                                np.linspace(0.8, 1.6, 20)]),
        "方案": ["甲"] * 20 + ["乙"] * 20,
    })
    mf.errorbar_line(trend, x="时间", y="均值", err="标准差", hue="方案", band=True,
                     xlabel="时间", ylabel="测量值", title="误差带折线图")
    mf.save(_out("统计_误差带折线图"))
    plt.close("all")

    # 堆叠图
    stack_df = pd.DataFrame({
        "季度": ["Q1", "Q2", "Q3", "Q4"],
        "产品甲": [30, 40, 45, 52],
        "产品乙": [20, 25, 30, 28],
        "产品丙": [10, 15, 18, 25],
    })
    mf.stackplot(stack_df, x="季度", y=["产品甲", "产品乙", "产品丙"],
                 kind="bar", ylabel="销售额（万元）", title="堆叠柱状图")
    mf.save(_out("统计_堆叠柱状图"))
    plt.close("all")

    mf.stackplot(stack_df, x="季度", y=["产品甲", "产品乙", "产品丙"],
                 kind="area", ylabel="销售额（万元）", title="堆积面积图")
    mf.save(_out("统计_堆积面积图"))
    plt.close("all")

    # 分面网格
    facet_df = pd.DataFrame({
        "时间": np.tile(np.arange(1, 9), 4),
        "数值": np.concatenate([
            2 ** np.arange(0, 8) * 0.5,
            np.linspace(2, 9, 8),
            9 - np.linspace(0, 7, 8),
            np.sin(np.arange(8)) * 3 + 5,
        ]),
        "区域": np.repeat(["华东", "华北", "华南", "西部"], 8),
    })
    mf.facet_grid(facet_df, x="时间", y="数值", col="区域", kind="line",
                  xlabel="时间", ylabel="数值")
    plt.gcf().suptitle("分面网格图", y=1.02)
    mf.save(_out("统计_分面网格图"))
    plt.close("all")

    # ROC 曲线
    rng = np.random.default_rng(5)
    y_true = np.concatenate([np.zeros(60), np.ones(60)])
    y_score = np.concatenate([rng.normal(0.35, 0.2, 60), rng.normal(0.72, 0.2, 60)])
    mf.roc_curve(y_true, y_score, label="模型 A", title="ROC 曲线")
    mf.save(_out("统计_ROC曲线"))
    plt.close("all")

    # 相关性热图
    mf.corr_heatmap(sample_corr_df(), title="相关性热图（下三角）",
                    mask_upper=True)
    mf.save(_out("统计_相关性热图"))
    plt.close("all")

    # 配对关系矩阵
    mf.pairplot_grid(sample_corr_df(), title="配对关系矩阵")
    mf.save(_out("统计_配对关系矩阵"))
    plt.close("all")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    fonts = mf.available_chinese_fonts()
    print(f"[modelfig] 可用中文字体 {len(fonts)} 个：{', '.join(fonts) or '（无）'}")
    print(f"[modelfig] 可用风格：{', '.join(mf.style_names())}")
    print(f"[modelfig] 可用配色：{', '.join(mf.palette_names())}")

    print("[modelfig] 第一部分：风格 × 配色 对比 …")
    demo_style_palette_matrix()

    mf.set_style("paper", palette="soft_academic")
    print("[modelfig] 第二部分：基础图种 …")
    demo_basic()

    print("[modelfig] 第三部分：统计图种 …")
    demo_stats()

    n = len([f for f in os.listdir(OUT_DIR) if f.endswith(".png")])
    print(f"[modelfig] 完成，共输出 {n} 张图到：{OUT_DIR}")


if __name__ == "__main__":
    main()
