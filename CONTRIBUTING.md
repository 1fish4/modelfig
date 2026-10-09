# 贡献指南

感谢你愿意为 `modelfig` 出一份力。本文档说明参与开发的基本流程。

## 开发环境

```bash
git clone https://github.com/1fish4/modelfig.git
cd modelfig
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

## 运行测试

```bash
pytest
```

提交 PR 前请确保所有测试通过。

## 提 Issue

- **Bug 报告**：请附上操作系统、Python 版本、matplotlib 版本，以及最小复现代码。
- **功能建议**：说明使用场景，而不只是描述想要什么函数。

## 提 PR

1. 从 `main` 切出功能分支：`git checkout -b feat/your-feature`
2. 保持提交粒度适中——一个提交解决一件事，提交信息写清"做了什么"。
3. 新增功能请同时补测试。
4. 代码风格：遵循 PEP 8，公共函数需有 docstring。

## 核心设计约束

改动代码前请先理解这三条，它们是本库的立身之本：

1. **风格、配色、底色三者正交。** 风格只管"线条/字号/网格/边框"，
   配色只管"用什么颜色"。**任何一套风格里都不应该出现颜色定义**，
   任何一套配色里都不应该出现线宽或字号。
2. **绘图函数不硬编码视觉细节。** 颜色、字号、线宽一律从 `rcParams` 读，
   不写死数值。
3. **默认值要贴合科研惯例。** 例如柱状图默认标标准误、热力图默认发散色带——
   用户不改任何参数，出来的图就应该是能直接放进论文的。

## 新增一个绘图函数

绘图函数应遵循库内既有约定：

1. 签名中包含可选参数 `ax=None`；
2. 返回 `(fig, ax)`；
3. **不硬编码任何颜色、字号、线宽** —— 这些全部交给风格系统；
4. 在 `modelfig/__init__.py` 的 `__all__` 中导出；
5. 在 `examples/demo.py` 中加一个演示，在 `examples/gallery.py` 中加一格展示；
6. 在 `tests/test_smoke.py` 中加冒烟测试。

## 新增一套风格

在 `modelfig/styles.py` 中定义 rcParams 字典并注册进 `STYLES`，
同时补 `_STYLE_DESC` 里的中文标签与适用场景，并在 `docs/style-preview.md`
与 README 的风格表中补充说明。

## 新增一套配色

在 `modelfig/palettes.py` 中定义颜色字典并注册进 `PALETTES`。注意两点：

- **类别色的顺序按「相邻色差异最大」排**，不要按色相顺序排。
  浅色系请后置——浅色作线条几乎看不见，只适合填充。
- **渐变色的顺序不能打乱**，它要用于 `sequential()` 构造色带。

新增配色后请运行 `python examples/gallery.py` 重新生成色板图。

## 许可证

贡献的代码将按项目的 [MIT License](LICENSE) 发布。
