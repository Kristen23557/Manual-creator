# 贡献指南

感谢你对本项目的关注！这是一个以单文件 Streamlit 应用为核心的小项目。为保证代码库稳定性，请遵循下列最小准则：

- Fork 并在分支上工作，提交前确保变更聚焦且可回滚。
- 保持向后兼容：不要破坏 `project.json` 或 `structure.json` 的字段结构。
- 提交信息请简洁明了，说明变更目的与影响范围。
- 若修改导出逻辑或数据结构，请在 PR 描述中列出迁移步骤与兼容策略。

运行与测试：

```bash
pip install -r requirements.txt
streamlit run app.py
```

测试框架（骨架）位于 `tests/`，建议在增加逻辑后补充相应单元测试。
