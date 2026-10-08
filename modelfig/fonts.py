"""中文字体自动配置。

matplotlib 默认字体不含中文字形，未配置时中文会渲染成方框（俗称"豆腐块"）。
本模块在运行时探测当前系统已安装的中文字体，挑选可用者写入 ``rcParams``，
并顺手修掉负号显示为方块的老问题。

典型用法
--------
>>> from modelfig import setup_chinese_font
>>> setup_chinese_font()          # 之后所有图都能正常显示中文
>>> print(setup_chinese_font.__doc__)  # noqa: D103
"""

from __future__ import annotations

import warnings

import matplotlib as mpl
import matplotlib.font_manager as fm

__all__ = ["available_chinese_fonts", "setup_chinese_font"]


# 按"观感优先级"排列的候选字体。越靠前越优先选用。
# 覆盖 Windows / macOS / Linux 三大平台的常见中文字体。
_PREFERRED: tuple[str, ...] = (
    # Windows
    "Microsoft YaHei",   # 微软雅黑
    "SimHei",            # 黑体
    "SimSun",            # 宋体
    "KaiTi",             # 楷体
    "FangSong",          # 仿宋
    # macOS
    "PingFang SC",
    "Hiragino Sans GB",
    "STHeiti",
    "Songti SC",
    "Heiti TC",
    # Linux / 通用开源字体
    "Noto Sans CJK SC",
    "Noto Sans SC",
    "Source Han Sans SC",
    "Source Han Sans CN",
    "WenQuanYi Micro Hei",
    "WenQuanYi Zen Hei",
    "AR PL UMing CN",
)


def available_chinese_fonts() -> list[str]:
    """返回当前系统中真实可用的中文字体名（按 :data:`_PREFERRED` 优先级排序）。

    该函数同时被 :func:`setup_chinese_font` 与用户诊断场景使用。
    """
    installed = {f.name for f in fm.fontManager.ttflist}
    return [name for name in _PREFERRED if name in installed]


def setup_chinese_font(*, verbose: bool = False) -> str | None:
    """配置 matplotlib 使用系统中可用的中文字体。

    参数
    ----
    verbose : bool, 默认 False
        为 ``True`` 时打印实际选中的字体名，便于排查问题。

    返回
    ----
    str | None
        选中的字体名；若系统中没有找到任何候选中文字体，返回 ``None``
        并发出警告（此时中文仍会显示为方块，需用户自行安装字体）。
    """
    found = available_chinese_fonts()

    if not found:
        warnings.warn(
            "未在系统中找到可用的中文字体，中文可能显示为方块。"
            "请安装任一中文字体（如 Noto Sans CJK SC）后重试。",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    chosen = found[0]
    # 注意：这里用列表而非单个字体名。matplotlib 会按顺序回退，
    # 因此把全部候选中文字体都塞进去，任何一种缺失都不影响出图。
    mpl.rcParams["font.sans-serif"] = found + ["DejaVu Sans"]
    mpl.rcParams["font.family"] = "sans-serif"
    # 使用 Unicode 减号，避免中文环境下负号渲染异常。
    mpl.rcParams["axes.unicode_minus"] = False

    if verbose:
        print(f"[modelfig] 已启用中文字体：{chosen}")
        if len(found) > 1:
            print(f"[modelfig] 回退字体链：{' -> '.join(found)}")

    return chosen
