# Copilot 使用说明（仓库定制）

下面的说明面向自动化编码/补全代理，目的是帮助你快速在本仓库中进行安全、正确且高产的改动。

## 项目一览（大局观）
- 这是一个基于 Streamlit 的单文件应用：主入口是 `app.py`，负责 UI、会话状态和所有业务逻辑。
- 项目以本地文件夹形式保存每个手册：根目录下的 `projects/` 目录，每个项目包含 `project.json`（元数据）和 `structure.json`（页面/内容结构），最终输出 `index.html`。
- HTML 的生成逻辑集中在 `HTMLGenerator`（位于 `app.py` 中），并使用内联模板或 `templates/base-template.html` 作为参考样式/占位。

## 关键文件与位置
- 主应用：app.py
- 模板：templates/base-template.html
- 依赖：requirements.txt
- 运行时数据：projects/（自动创建）和 backups/

## 运行与开发流程（开发者/代理可直接使用）
1. 安装依赖：`pip install -r requirements.txt`。
2. 本地调试：`streamlit run app.py`（默认端口 8501）。
3. 在 UI 中：新建项目 → 编辑 → 点击“保存项目”或“导出HTML”会在对应 `projects/<name>/` 下生成 `index.html`。

注意：仓库没有包含额外的 CLI 或测试框架，所有导出/生成逻辑通过 UI 的按钮触发；代理需要模拟用户行为时应修改/调用 `ProjectManager` 与 `HTMLGenerator` 的方法。

## 项目结构与约定（可被代理依赖）
- 项目 JSON 结构（discoverable）: 顶层键 `title`, `description`, `cover_page`, `pages`, `config`。
- 封面页（cover_page）包含 `id`, `title`, `content`（数组，元素含 `type`、`text` 等）。
- 可识别的内容类型（在 `HTMLGenerator.calculate_word_count` 与渲染中出现）：`heading`, `paragraph`, `note`，其他元素以相似字段扩展。
- 备份策略：`backups/<project>/backup_*.json`，保留最近 10 个备份。

## 重要类与调用点（便于自动修改）
- `ProjectManager`：创建/列出/加载/删除项目，直接操作文件系统（projects/、backups/）。修改涉及持久化时请通过该类提供的 API。
- `HTMLGenerator`：负责把 `structure` 转换为最终 HTML，包含 `generate_html`, `generate_css`, `generate_javascript` 等方法。若要更改导出样式，优先在此处修改。
- `SessionStateManager`：封装对 `st.session_state` 的初始化和通知机制；短期内在 UI 交互时使用。

## 代码风格与约定（仓库特定）
- 单文件大型 Streamlit 应用：避免在同一 PR 中大面积拆分文件, 首选小而精确的函数提取与重构。
- 文件 IO 直接使用 `pathlib.Path`；对修改路径或新增持久化字段，确保兼容已有 `project.json` 与 `structure.json`。
- 用户可见文案以中文为主；日志/异常消息也多为中文，保持一致性。

## 安全与边界条件
- 所有对项目名称、JSON 加载的用户输入都有基本校验（见 `ProjectManager.create_project` 与 `load_project`）。若代理要修改这些函数，保留或增强校验逻辑，避免允许任意文件路径（目录穿越）。

## 建议的自动化任务与示例
- 添加单元测试（建议目录 `tests/`）：可先对 `ProjectManager.validate_structure`、`HTMLGenerator.calculate_word_count` 编写小规模测试。
- 若实现 CLI 导出功能：封装 `ProjectManager.create_project`、`ProjectManager.load_project` 与 `HTMLGenerator.generate_html` 为可调用的函数，再提供 `if __name__ == '__main__'` 下的小脚本。

## 例子片段（定位引用）
- 打开主应用并运行：`streamlit run app.py`。
- 编辑样式或模板：参见 `templates/base-template.html`（其占位符：`{{ css }}`、`{{ content }}`、`{{ js }}`）。

---
如果以上某处不清楚或你希望我把某些类拆成独立模块、添加 CLI 或补充测试，我可以先按步骤列一个修改计划并实现。请告诉我你想优先做的改动。
