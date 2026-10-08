# 风格与配色

本库的视觉由**风格（style）**和**配色（palette）**两个正交维度决定：

```
最终视觉 = 风格（线条粗细/字号/网格/边框） × 配色（用什么颜色）
```

因此只需维护 `3 套风格 + 4 套配色`，就能组合出 **12 种观感**，
而不是把 12 种组合各写一遍。

---

## 一、风格（决定"长什么样"）

| 风格 | 线宽 | 字号 | 边框 | 网格 | 适用场景 |
|------|------|------|------|------|----------|
| `paper` | 1.2 pt | 10 pt | 四边保留 | 无 | 学位论文、期刊投稿 |
| `slide` | 2.6 pt | 16 pt | 仅左、下 | 浅色 | 答辩 PPT、组会汇报 |
| `poster` | 3.4 pt | 20 pt | 仅左、下 | 无 | 海报、远距离展示 |

**paper —— 论文投稿风**
采用期刊惯例：四边保留边框、刻度内向、无网格，避免视觉噪声。
默认输出 300 dpi，满足多数期刊的分辨率要求。

**slide —— 演示答辩风**
去顶右边框、外向刻度、浅色网格，现代简洁。字号放大到 16 pt 保证后排可读，
线宽加粗到 2.6 pt 让投影后仍清晰。

**poster —— 海报展示风**
字号 20 pt、线宽 3.4 pt，为两三米外观看设计。

---

## 二、配色（决定"用什么颜色"）

全部取自科研绘图素材，按用途而非好看来分类。

### soft_academic —— 柔和学术（离散，6 色）

| 色名 | HEX |
|------|-----|
| 深蓝 | `#3B84B6` |
| 浅蓝 | `#6F8FD0` |
| 薄荷绿 | `#76E4A2` |
| 鹅黄 | `#F0D08E` |
| 橙红 | `#F4C1A2` |
| 柔粉 | `#E93A6C` |

**最百搭的一套**，低饱和、色相跨度均匀，适合分组柱状图、多序列折线、饼图。

### warm_cool —— 暖橙冷蓝（连续，9 色）

| 色名 | HEX | | 色名 | HEX |
|------|-----|---|------|-----|
| 深砖红 | `#B04A5A` | | 浅黄 | `#EDE3A3` |
| 珊瑚橙 | `#E8705A` | | 杏黄 | `#FBEDB0` |
| 橙红 | `#F49B7E` | | 草绿 | `#A8CF8D` |
| 浅橙 | `#F4B98A` | | 天青 | `#7BC8A4` |
| | | | 深蓝 | `#3F5F8F` |

**唯一的连续配色**，暖冷过渡平滑，专为热力图与色阶映射设计。

### misty_blue —— 烟霞蓝橙（离散，6 色）

| 色名 | HEX |
|------|-----|
| 珊瑚粉 | `#EEA599` |
| 杏橙 | `#FAC795` |
| 奶油黄 | `#FFE9BE` |
| 雾绿灰 | `#E3EDE0` |
| 浅湖蓝 | `#ABD3E1` |
| 烟霞蓝 | `#92B4C8` |

蓝橙互补对比，冷静中带暖意，适合折线对比与散点分组。

### soft_multi —— 柔和多彩（离散，8 色）

| 色名 | HEX | | 色名 | HEX |
|------|-----|---|------|-----|
| 蜜桃 | `#F2A57C` | | 紫罗兰 | `#8E8FD6` |
| 珊瑚 | `#EE8B8B` | | 天蓝 | `#7FB6DE` |
| 玫瑰粉 | `#E887B4` | | 青绿 | `#7FCBBE` |
| 薰衣草 | `#B79AD9` | | 草绿 | `#A8D08D` |

八色明快但不刺眼，适合类别数多的分组、堆叠图与分面网格。

---

## 三、组合使用

```python
import modelfig as mf

# 论文风 + 柔和学术配色
mf.set_style("paper", palette="soft_academic")

# 答辩风 + 柔和多彩配色
mf.set_style("slide", palette="soft_multi")

# 海报风 + 暖橙冷蓝配色
mf.set_style("poster", palette="warm_cool")
```

查看全部可用项：

```python
mf.style_names()      # ['paper', 'slide', 'poster']
mf.palette_names()    # ['soft_academic', 'warm_cool', 'misty_blue', 'soft_multi']
mf.list_palettes()    # 带中文标签、类型、色数、适用场景
```

---

## 四、自定义

### 自定义风格

```python
mf.register_style("myschool", {
    "font.size": 12,
    "lines.linewidth": 1.8,
    "axes.grid": True,
})
mf.set_style("myschool", palette="soft_academic")
```

### 自定义配色

```python
mf.register_palette("myschool", ["#005BAC", "#E60012", "#009944"])
mf.set_style("paper", palette="myschool")
```

带中文标签的写法：

```python
mf.register_palette(
    "myschool",
    {"校蓝": "#005BAC", "校红": "#E60012"},
    label="校色",
    usage="学校报告",
)
```

完整可用参数见 [matplotlib rcParams 文档](https://matplotlib.org/stable/users/explain/customizing.html)。

