# 更新日志

本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

---

## [Unreleased]

### 计划中

- 聚类热图（带树状图）
- 平行坐标图
- 火山图
- 导出内嵌字体的 PDF / SVG

---

## [0.3.0] - 2026-10-09

以「期刊出图规范」为准重构了整套视觉系统，并新增展示画廊。

### 新增

- **风格**：新增 `journal`（严谨期刊，Nature/Science 图幅规范）；
  原 `paper` 更名为 `soft` 并重新调参，成为默认风格
- **配色**：配色由 4 套扩至 7 套，色值全部按素材重新精校
  （新增 `soft_omics`、`teal_earth`、`geo`）
- **底色**：新增 `background` 参数，可选 `white` / `cream`
- **`barplot`**：默认自动计算标准误（SEM）；新增 `show_points` 叠加原始散点；
  `annotate` 改为显著性括号形式，可自动做 t 检验取星号
- **`corr_heatmap`**：默认改用「蓝—白—红」发散色带，色带随当前配色构造
- **`describe_palette()`**：输出单套配色的完整色值说明
- **`style_info()`**：输出风格的中文标签、适用场景与视觉特征
- **`current_background()`**：查询当前底色
- **`examples/gallery.py`**：一键生成 README 展示图
  （四套风格对比、图种总览、色板）
- **`CHANGELOG.md`**：本文件

### 变更

- **视觉约定**：所有风格统一改为 despine（只保留左、下轴线）；
  轴线细化到 0.6 pt 并与数据线拉开反差；字号整体下调；标记统一描白边；
  启用 `constrained_layout`
- **配色排序**：类别色的颜色顺序改为按「相邻色差异最大」排列，
  浅色系后置；渐变色保留真实渐变顺序（`sequential()` 返回）
- **`categorical()`**：对渐变配色返回按对比度重排的版本

### 修复

- 相关性热图的上三角遮罩此前用叠加图层实现，会产生黑块；
  改用 `NaN` 置空，由色带渲染为透明
- `radar()` 的图例此前会压住蛛网外圈，调整锚点位置
- `facet_grid()` / `pairplot_grid()` 中与 `constrained_layout` 冲突的
  `tight_layout()` 调用已移除
- 「蓝绿冷色」配色中「深青绿」的原素材标注 `#4596B8` 与其 RGB 值不符，
  已按 RGB 取 `#459688`

### 迁移指南

自 v0.2.0 升级需注意：

| 旧写法 | 新写法 |
|--------|--------|
| `mf.set_style("paper")` | `mf.set_style("soft")` 或 `"journal"` |
| `mf.set_style("soft_multi")` | `mf.set_style("soft", palette="soft_multi")` |
| `barplot(..., errorbar=None)` | `barplot(..., errorbar=None)`（默认已改为 `"auto"`）|
| `barplot(annotate={"A": [...]})` | `barplot(annotate=[("A", "B")])` |
| `corr_heatmap(..., cmap="warm_cool")` | `corr_heatmap(...)`（默认 `"auto"`）|

---

## [0.2.0] - 2026-10-08

由 5 种图形扩充到 17 种，并引入 DataFrame 接口。

### 新增

- **风格系统**：风格与配色解耦为两个正交维度；
  新增 `poster` 风格（当时共 3 套）
- **配色库** `modelfig/palettes.py`：收录 4 套科研配色，支持注册扩展
- **统计层** `modelfig/stats.py`：13 个 DataFrame 接口函数
  （`lineplot` / `scatterplot` / `regplot` / `barplot` / `boxplot` / `violinplot` /
  `histplot` / `errorbar_line` / `roc_curve` / `corr_heatmap` /
  `pairplot_grid` / `stackplot` / `facet_grid`）
- **通用层**：新增 `scatter` / `box` / `violin` / `stacked_bar` / `errorbar`
- **`roc_curve()`**：梯形积分自实现 AUC，不依赖 scikit-learn
- **`load_csv()`**：带中文编码回退的读取辅助

### 变更

- 依赖由 `matplotlib + numpy` 扩为 `+ pandas + scipy`（效果优先）

---

## [0.1.0] - 2026-10-08

首个可用版本。

### 新增

- 风格系统：`paper`（论文投稿风）、`slide`（演示答辩风）
- 中文字体自动配置：跨平台探测系统中文字体，修复负号显示
- 五种绘图函数：`line` / `bar` / `dual_axis` / `heatmap` / `radar`
- `register_style()` 支持自定义风格扩展
- 冒烟测试与 GitHub Actions 三平台 CI
- MIT 许可证与完整文档

[Unreleased]: https://github.com/1fish4/modelfig/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/1fish4/modelfig/releases/tag/v0.3.0
[0.2.0]: https://github.com/1fish4/modelfig/releases/tag/v0.2.0
[0.1.0]: https://github.com/1fish4/modelfig/releases/tag/v0.1.0
