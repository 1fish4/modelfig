"""配色方案库。

所有色值均取自科研绘图素材，逐像素采样并核对过印刷 HEX 标注。

两个设计要点
------------
**一、颜色顺序按"可区分性"排，不按色相排。**
画两条线时最怕两色太像。因此每套配色的前几个颜色都被刻意拉开：
第 1、2 色通常是互补对（如蓝配橙），第 3 色引入第三种色相，
浅色系一律往后排——浅色作线条几乎看不见，只适合填充。

**二、区分"类别色"与"渐变色"。**
``kind="categorical"`` 用于分组对比，任意两色都要能分开；
``kind="continuous"`` 用于有序数据（热力图、色阶），色阶必须平滑过渡。
连续配色的 ``colors`` 仍给出类别用顺序，同时用 ``gradient`` 保留真实渐变。
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "PALETTES",
    "categorical",
    "sequential",
    "palette_names",
    "register_palette",
    "list_palettes",
    "describe_palette",
]


# ---------------------------------------------------------------------------
# 一、类别色（categorical）—— 任意两色都能分开
# ---------------------------------------------------------------------------

# 柔和学术：蓝 → 橙 → 粉 → 黄 → 浅蓝 → 冰青
# 最百搭的一套。前两色是蓝橙互补，第三四色引入粉与黄，浅色系压后。
_SOFT_ACADEMIC = {
    "深蓝": "#5B83BC",
    "珊瑚橙": "#FC9262",
    "柔粉": "#E9A4C1",
    "奶黄": "#FEDE8E",
    "浅蓝": "#94BFDC",
    "冰青": "#C4EAF2",
}

# 柔和多彩：深雾蓝 → 樱花粉 → 青碧 → 米杏 → 藕紫 → 雾蓝 → 蜜桃粉 → 薰衣草灰
# 低饱和但色相跨度大，适合 5~8 个类别的分组对比。
_SOFT_MULTI = {
    "深雾蓝": "#56669E",
    "樱花粉": "#F5B5BF",
    "青碧": "#50B9AE",
    "米杏": "#F5DDB5",
    "藕紫": "#CEA2B5",
    "雾蓝": "#728AB9",
    "蜜桃粉": "#F5CCBC",
    "薰衣草灰": "#9A9AB9",
}

# 柔和多组学：柔紫 → 珊瑚橙 → 鼠尾草绿 → 鲑粉 → 苔藓绿 → 蜜桃米 → 淡紫 → 薰衣草灰紫
# 紫绿橙三色打底，适合聚类、UMAP 等"多簇"场景。
_SOFT_OMICS = {
    "柔紫": "#6A4DB3",
    "珊瑚橙": "#E07A5F",
    "鼠尾草绿": "#AFCBA4",
    "鲑粉": "#F4A6A8",
    "苔藓绿": "#4F8F6B",
    "蜜桃米": "#F2D6B2",
    "淡紫": "#B69AD6",
    "薰衣草灰紫": "#9C8AB8",
}

# 烟霞蓝橙：烟霞蓝 → 珊瑚粉 → 奶油黄 → 浅湖蓝 → 杏橙 → 雾绿灰
# 对比度最低的一套，适合大尺寸图与需要"安静"观感的场合。
_MISTY_BLUE = {
    "烟霞蓝": "#92B4C8",
    "珊瑚粉": "#EEA599",
    "奶油黄": "#FFE9BE",
    "浅湖蓝": "#ABD3E1",
    "杏橙": "#FAC795",
    "雾绿灰": "#E3EDE0",
}

# 蓝绿冷色：深青绿 → 焦糖橙 → 雾蓝绿 → 陶土粉 → 浅鼠尾草 → 杏橙 → 灰米白 → 暖砖橙 ...
# 冷色为主、暖色点缀，原素材用于地图、热图、时间序列。
_TEAL_EARTH = {
    "深青绿": "#459688",
    "焦糖橙": "#D98D67",
    "雾蓝绿": "#79AFB1",
    "陶土粉": "#D1A38C",
    "浅鼠尾草": "#D1E2DA",
    "杏橙": "#E5A17E",
    "灰米白": "#E0E3DE",
    "暖砖橙": "#E89E77",
    "雾白": "#EBEFED",
    "沙米色": "#F7EEE3",
}


# ---------------------------------------------------------------------------
# 二、渐变色（continuous）—— 色阶平滑，用于有序数据
# ---------------------------------------------------------------------------

# 暖橙冷蓝：深红 → 珊瑚红 → 暖粉 → 杏 → 浅黄 → 米黄 → 中蓝 → 浅蓝 → 冰蓝
_WARM_COOL_GRADIENT = [
    "#D73221", "#E35235", "#E48070", "#FCB777", "#FDE699",
    "#FEF4AE", "#4573B4", "#6491C1", "#D2EDF2",
]
_WARM_COOL_NAMES = [
    "深砖红", "珊瑚红", "暖粉橙", "浅杏橙", "浅黄",
    "米黄", "中蓝", "浅蓝", "冰蓝",
]
# 类别用顺序：两端取色，保证前几色对比最强
_WARM_COOL_ORDER = [0, 6, 4, 8, 1, 5, 3, 7, 2]

# 地学：珊瑚粉 → 杏橙 → 沙黄 → 淡黄 → 黄绿 → 鼠尾草绿 → 苔绿 → 青绿 → 天空蓝 → 深海蓝
_GEO_GRADIENT = [
    "#F07D7D", "#F4B37A", "#F6D37A", "#FFF186", "#CFE7A4",
    "#9CC88A", "#66A870", "#4CB8B0", "#6FAFE6", "#2F4B88",
]
_GEO_NAMES = [
    "珊瑚粉", "杏橙", "沙黄", "淡黄", "黄绿",
    "鼠尾草绿", "苔绿", "青绿", "天空蓝", "深海蓝",
]
_GEO_ORDER = [0, 9, 4, 7, 2, 8, 1, 6, 3, 5]


def _ordered(names: list[str], colors: list[str],
             order: list[int]) -> dict[str, str]:
    """把渐变配色按给定顺序重排成类别用字典。"""
    return {names[i]: colors[i] for i in order}


# ---------------------------------------------------------------------------
# 注册表
# ---------------------------------------------------------------------------

PALETTES: dict[str, dict[str, Any]] = {
    "soft_academic": {
        "label": "柔和学术",
        "kind": "categorical",
        "usage": "最百搭。分组柱状图、多序列折线、散点分组",
        "colors": _SOFT_ACADEMIC,
    },
    "soft_multi": {
        "label": "柔和多彩",
        "kind": "categorical",
        "usage": "类别多（5~8 组）时的分组对比",
        "colors": _SOFT_MULTI,
    },
    "soft_omics": {
        "label": "柔和多组学",
        "kind": "categorical",
        "usage": "聚类散点、UMAP、多簇分布",
        "colors": _SOFT_OMICS,
    },
    "misty_blue": {
        "label": "烟霞蓝橙",
        "kind": "categorical",
        "usage": "低对比柔和风。大尺寸图、需要安静的观感",
        "colors": _MISTY_BLUE,
    },
    "teal_earth": {
        "label": "蓝绿冷色",
        "kind": "categorical",
        "usage": "冷色为主、暖色点缀。地图、时序、多变量",
        "colors": _TEAL_EARTH,
        "gradient": _TEAL_EARTH,
    },
    "warm_cool": {
        "label": "暖橙冷蓝",
        "kind": "continuous",
        "usage": "热力图、色阶映射（唯一的暖冷渐变）",
        "colors": _ordered(_WARM_COOL_NAMES, _WARM_COOL_GRADIENT,
                           _WARM_COOL_ORDER),
        "gradient": dict(zip(_WARM_COOL_NAMES, _WARM_COOL_GRADIENT)),
    },
    "geo": {
        "label": "地学",
        "kind": "continuous",
        "usage": "分区填色、地图配色、分箱色阶",
        "colors": _ordered(_GEO_NAMES, _GEO_GRADIENT, _GEO_ORDER),
        "gradient": dict(zip(_GEO_NAMES, _GEO_GRADIENT)),
    },
}


# ---------------------------------------------------------------------------
# 对外接口
# ---------------------------------------------------------------------------

def palette_names() -> list[str]:
    """返回所有已注册的配色名。"""
    return list(PALETTES)


def list_palettes() -> list[tuple[str, str, str, int, str]]:
    """返回配色清单，便于打印或生成文档。

    返回
    ----
    list[tuple]
        每项为 ``(名称, 中文标签, 类型, 颜色数, 适用场景)``。
    """
    return [
        (name, spec["label"], spec["kind"], len(spec["colors"]), spec["usage"])
        for name, spec in PALETTES.items()
    ]


def describe_palette(name: str) -> str:
    """返回一套配色的可读说明（含全部色值）。"""
    if name not in PALETTES:
        raise KeyError(f"未知配色 {name!r}。可用配色：{', '.join(PALETTES)}")
    spec = PALETTES[name]
    kind_cn = "类别色" if spec["kind"] == "categorical" else "渐变色"
    lines = [
        f"{spec['label']}（{name}）— {kind_cn}，{len(spec['colors'])} 色",
        f"适用：{spec['usage']}",
        "色值：" + "  ".join(f"{k}={v}" for k, v in spec["colors"].items()),
    ]
    if "gradient" in spec:
        lines.append("渐变：" + " → ".join(spec["gradient"].values()))
    return "\n".join(lines)


def categorical(name: str = "soft_academic") -> list[str]:
    """取出一套配色的颜色列表，供 ``matplotlib`` 的 ``prop_cycle`` 使用。

    参数
    ----
    name : str, 默认 "soft_academic"
        配色名，见 :func:`palette_names`。

    返回
    ----
    list[str]
        HEX 颜色列表，顺序已按"相邻色差异最大"优化。
    """
    if name not in PALETTES:
        raise KeyError(
            f"未知配色 {name!r}。可用配色：{', '.join(PALETTES)}"
        )
    return list(PALETTES[name]["colors"].values())


def sequential(name: str = "warm_cool") -> list[str]:
    """取出一套配色的**渐变**顺序，用于构造自定义 colormap。

    对 ``kind="continuous"`` 的配色返回真实渐变序列（不要打乱顺序）；
    对类别配色则回退为它的类别顺序。
    """
    if name not in PALETTES:
        raise KeyError(
            f"未知配色 {name!r}。可用配色：{', '.join(PALETTES)}"
        )
    spec = PALETTES[name]
    source = spec.get("gradient", spec["colors"])
    return list(source.values())


def register_palette(
    name: str,
    colors: dict[str, str] | list[str],
    *,
    label: str | None = None,
    kind: str = "categorical",
    usage: str = "",
) -> None:
    """注册一套自定义配色。

    参数
    ----
    name : str
        配色名。
    colors : dict 或 list
        ``{"色名": "#RRGGBB"}`` 或直接给 HEX 列表。
    kind : str, 默认 "categorical"
        ``"categorical"`` 类别色 或 ``"continuous"`` 渐变色。

    示例
    ----
    >>> import modelfig as mf
    >>> mf.register_palette("myschool", {"校蓝": "#005BAC", "校红": "#E60012"})
    """
    if isinstance(colors, list):
        colors = {f"c{i+1}": c for i, c in enumerate(colors)}
    PALETTES[name] = {
        "label": label or name,
        "kind": kind,
        "usage": usage,
        "colors": dict(colors),
    }
