# 贡献指南

感谢你愿意为 `modelfig` 出一份力。本文档说明参与开发的基本流程。

## 开发环境

```bash
git clone https://github.com/YOUR_NAME/modelfig.git
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

## 新增一个绘图函数

绘图函数应遵循库内既有约定：

1. 签名中包含可选参数 `ax=None`；
2. 返回 `(fig, ax)`；
3. **不硬编码任何颜色、字号、线宽** —— 这些全部交给风格系统；
4. 在 `modelfig/__init__.py` 的 `__all__` 中导出；
5. 在 `examples/demo.py` 中加一个演示；
6. 在 `tests/test_smoke.py` 中加冒烟测试。

## 新增一套风格

在 `modelfig/styles.py` 里加一个字典并注册进 `STYLES` 即可，
同时在 `docs/style-preview.md` 中补充设计说明。

## 许可证

贡献的代码将按项目的 [MIT License](LICENSE) 发布。
