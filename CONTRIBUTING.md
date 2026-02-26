# Contributing to Multi-Agent Interaction

感谢你考虑为这个项目做出贡献！

## 🤔 如何贡献

### 报告 Bug

如果你发现了 bug，请创建一个 Issue，包含：

1. 清晰的标题和描述
2. 复现步骤
3. 期望行为
4. 实际行为
5. 环境（Python 版本、操作系统等）

### 提出新功能

如果你有新功能的想法，请创建一个 Issue 来讨论。

### 提交代码

1. **Fork 仓库**
   
2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **编写代码**
   - 遵循 PEP 8 代码风格
   - 添加必要的测试
   - 更新文档

4. **提交更改**
   ```bash
   git commit -m "feat: 简短描述你的更改"
   ```
   
   提交信息格式：
   - `feat:` 新功能
   - `fix:` 修复 bug
   - `docs:` 文档更新
   - `test:` 测试相关
   - `refactor:` 重构
   - `chore:` 其他杂项

5. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 清晰描述你的更改
   - 关联相关 Issue
   - 等待审核

## 📝 代码风格

- 遵循 [PEP 8](https://peps.python.org/pep-0008/)
- 使用 4 空格缩进
- 函数和类添加 docstring
- 变量名使用 snake_case
- 类名使用 PascalCase

## ✅ 测试

- 为新功能添加测试
- 确保所有测试通过
- ```bash
  pytest tests/ -v
  ```

## 📄 License

提交代码即表示你同意你的贡献将按照 MIT License 授权。