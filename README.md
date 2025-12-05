# 网页手册创建器 (Manual creator)

一个基于 Streamlit 的轻量级网页手册生成器，允许通过可视化界面创建项目、编辑页面内容并导出为可部署的静态 HTML。

核心实现为单文件应用，入口为 [app.py](app.py)。生成 HTML 的模板和样式位于 [templates/base-template.html](templates/base-template.html)。

## 核心特性
- 所见即所得的可视化编辑界面（基于 Streamlit）。
- 将项目保存在本地 `projects/` 目录（每个项目含 `project.json` 与 `structure.json`）。
- 一键导出为静态 `index.html`（生成于对应项目目录）。
- 自动备份：`backups/<project>/backup_*.json`（保留最近 10 个备份）。
- 可通过 `HTMLGenerator` 在代码中自定义导出样式与脚本（实现于 `app.py`）。

## 快速上手
1. 克隆或下载本仓库到本地。
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行应用：

```bash
streamlit run app.py
```

4. 在浏览器中使用 UI 创建项目、编辑内容，并点击“保存项目”或“导出HTML”生成 `projects/<项目名>/index.html`。

## 运行环境
- Python 3.8+ 推荐
- 依赖见 [requirements.txt](requirements.txt)（主要依赖 `streamlit`, `jinja2` 等）。

## 项目数据结构（说明）
- 每个项目保存于 `projects/<name>/`，主要文件：
  - `project.json`：项目元信息（title、description、created_at、last_modified、version、settings）。
  - `structure.json`：页面结构与内容（`title`、`cover_page`、`pages`、`config`）。

示例（摘录）:

`project.json` 示例：

```json
{
  "name": "MyManual",
  "description": "示例项目",
  "created_at": "2025-12-06T12:00:00",
  "last_modified": "2025-12-06T12:00:00",
  "author": "用户",
  "version": "1.0.0",
  "settings": { "theme": "light", "animations": true }
}
```

`structure.json` 示例（简化）：

```json
{
  "title": "MyManual",
  "description": "项目简介",
  "cover_page": {
    "id": "cover",
    "title": "欢迎页面",
    "content": [ { "id": "welcome_text", "type": "paragraph", "text": "欢迎..." } ]
  },
  "pages": [],
  "config": { "theme": "light" }
}
```

注意：应用里有基础校验（见 `ProjectManager.validate_structure`），请勿手动删除必要字段。

## 关键代码位置（便于修改）
- 主入口：[app.py](app.py)
  - `ProjectManager`：负责项目的创建/加载/删除/备份。
  - `HTMLGenerator`：负责把 `structure` 转换为最终 HTML（包含 `generate_css`、`generate_javascript` 等方法）。
  - `SessionStateManager`：封装 `st.session_state` 的默认值和通知。
- 模板：[templates/base-template.html](templates/base-template.html)

如果你想调整导出的 HTML 结构或样式，优先修改 `HTMLGenerator.generate_css` 或 `templates/base-template.html`。

## 开发与调试建议
- 本仓库目前没有自动化测试；建议先在本地运行并手动验证主要路径（创建项目 → 编辑 → 保存 → 导出）。
- 若要编写自动化测试，优先针对 `ProjectManager.validate_structure`、`HTMLGenerator.calculate_word_count` 编写单元测试。

## 常见操作位置
- 生成的 HTML：`projects/<name>/index.html`。
- 备份：`backups/<name>/backup_YYYYmmdd_HHMMSS.json`。

## 贡献指南
- 提交前请保留项目的行为与数据兼容性（不要破坏 `project.json` / `structure.json` 字段）。
- 避免一次性大规模重构：本仓库以单文件 `app.py` 为主，推荐小步重构并配套注释或迁移说明。

## 许可证
本仓库未在代码中包含许可证声明。若需要公开分发，请在仓库根目录添加合适的 `LICENSE` 文件并在此处注明。

---
如果你希望我增加：
- 具体的 JSON 字段完整说明（字段表格），或
- 把 `app.py` 拆成模块并添加测试与 CLI（我可以列计划并实现），
请告诉我你优先的项。
