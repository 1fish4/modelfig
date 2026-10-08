"""配色方案库。

所有色值均取自科研绘图素材，按"用途"而非"好看"来设计：每套配色都
标注了它适合什么场景，避免用户盲目挑选。

配色分两类
----------
* **离散色（categorical）**：用于类别对比（分组柱状图、多条折线）。
  要求任意两色在视觉上都能分开，且灰度打印时仍有明度差。
* **连续色（continuous）**：用于有序数据（热力图、色阶映射）。
  要求色阶过渡平滑，最小值与最大值有足够对比。

命名约定
--------
``c_`` 前缀 = categorical（离散）
``s_`` 前缀 = sequential（连续）
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
]


# ---------------------------------------------------------------------------
# 配色定义
# ---------------------------------------------------------------------------

# 1. 柔和学术 —— 素材"科研绘图配色"第 1 页
#    六色低饱和，蓝绿黄橙红粉，覆盖所有常见类别数，最百搭。
#    适合：分组柱状图、多序列折线、饼图。
_SOFT_ACADEMIC = {
    "深蓝": "#3B84B6",
    "浅蓝": "#6F8FD0",
    "薄荷绿": "#76E4A2",
    "鹅黄": "#F0D08E",
    "橙红": "#F4C1A2",
    "柔粉": "#E93A6C",
}

# 2. 暖橙冷蓝 —— 素材第 5 页
#    九色暖到冷连续过渡，是"有序"配色，也适合类别数多的场景。
#    适合：热力图、色阶映射、多组对比。
_WARM_COOL = {
    "深砖红": "#B04A5A",
    "珊瑚橙": "#E8705A",
    "橙红": "#F49B7E",
    "浅橙": "#F4B98A",
    "浅黄": "#EDE3A3",
    "杏黄": "#FBEDB0",
    "草绿": "#A8CF8D",
    "天青": "#7BC8A4",
    "深蓝": "#3F5F8F",
}

# 3. 烟霞蓝橙 —— 素材第 3 页
#    六色柔和，蓝橙互补对比，冷静中带暖意。
#    适合：折线对比、散点分组、箱线图。
_MISTY_BLUE = {
    "珊瑚粉": "#EEA599",
    "杏橙": "#FAC795",
    "奶油黄": "#FFE9BE",
    "雾绿灰": "#E3EDE0",
    "浅湖蓝": "#ABD3E1",
    "烟霞蓝": "#92B4C8",
}

# 4. 柔和多彩 —— 素材第 7 页
#    八色明快但不刺眼，色相跨度大，适合类别数多的分组。
#    适合：多组柱状图、堆叠图、Facet 分面。
_SOFT_MULTI = {
    "蜜桃": "#F2A57C",
    "珊瑚": "#EE8B8B",
    "玫瑰粉": "#E887B4",
    "薰衣草": "#B79AD9",
    "紫罗兰": "#8E8FD6",
    "天蓝": "#7FB6DE",
    "青绿": "#7FCBBE",
    "草绿": "#A8D08D",
}


#: 配色注册表。``kind`` 字段区分离散/连续，供绘图函数自动选择。
PALETTES: dict[str, dict[str, Any]] = {
    "soft_academic": {
        "label": "柔和学术",
        "kind": "categorical",
        "usage": "分组柱状图、多序列折线、饼图（最百搭）",
        "colors": _SOFT_ACADEMIC,
    },
    "warm_cool": {
        "label": "暖橙冷蓝",
        "kind": "continuous",
        "usage": "热力图、色阶映射、多组对比",
        "colors": _WARM_COOL,
    },
    "misty_blue": {
        "label": "烟霞蓝橙",
        "kind": "categorical",
        "usage": "折线对比、散点分组、箱线图",
        "colors": _MISTY_BLUE,
    },
    "soft_multi": {
        "label": "柔和多彩",
        "kind": "categorical",
        "usage": "多组柱状图、堆叠图、分面网格",
        "colors": _SOFT_MULTI,
    },
}


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


def categorical(name: str = "soft_academic") -> list[str]:
    """取出一套配色的颜色列表，供 :func:`matplotlib.axes.Axes.set_prop_cycle` 使用。

    参数
    ----
    name : str, 默认 "soft_academic"
        配色名，见 :func:`palette_names`。

    返回
    ----
    list[str]
        HEX 颜色列表。
    """
    if name not in PALETTES:
        raise KeyError(
            f"未知配色 {name!r}。可用配色：{', '.join(PALETTES)}"
        )
    return list(PALETTES[name]["colors"].values())


def sequential(name: str = "warm_cool") -> list[str]:
    """取出一套连续配色的色阶列表（用于自定义 colormap）。

    与 :func:`categorical` 的区别仅在语义：连续配色用在有序数据上，
    调用方不应打乱顺序。
    """
    return categorical(name)


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
        ``"categorical"`` 离散 或 ``"continuous"`` 连续。

    示例
    ----
    >>> import modelfig as mf
    >>> mf.register_palette("myschool", ["#005BAC", "#E60012"])
    """
    if isinstance(colors, list):
        colors = {f"c{i+1}": c for i, c in enumerate(colors)}
    PALETTES[name] = {
        "label": label or name,
        "kind": kind,
        "usage": usage,
        "colors": dict(colors),
    }
