# 贡献指南

欢迎为 OpenClaw-VikingFS 项目贡献代码！

## 开发环境设置

1. **克隆仓库**
   ```bash
   git clone https://github.com/YOUR_USERNAME/openclaw-vikingfs.git
   cd openclaw-vikingfs
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或 venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -e .
   ```

## 开发流程

### 1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

### 2. 编写代码
请遵循项目的代码风格：
- 使用类型注解
- 添加适当的文档字符串
- 编写单元测试

### 3. 运行测试
```bash
python -m pytest tests/
```

### 4. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能描述"
```

### 5. 创建Pull Request
1. 推送分支到远程
2. 在GitHub上创建Pull Request
3. 等待代码审查

## 代码风格

### Python
- 使用 `black` 格式化代码
- 使用 `isort` 排序导入
- 遵循 PEP 8 规范

```bash
# 安装开发依赖
pip install black isort pytest

# 格式化代码
black .
isort .
```

### 提交信息格式
使用约定式提交格式：
- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档更新
- `test:` 测试相关
- `refactor:` 重构代码
- `perf:` 性能优化

## 项目结构说明

```
openclaw-vikingfs/
├── viking/              # 核心代码
│   ├── integration/    # OpenClaw集成
│   ├── tools/         # 工具脚本
│   └── memory/        # 分层记忆系统
├── tests/             # 测试代码
├── examples/          # 使用示例
└── docs/             # 文档
```

## 测试覆盖率

运行测试时确保：
- 新功能的测试覆盖率 ≥ 80%
- 包含边缘情况测试
- 集成测试验证实际使用场景

## 文档要求

所有新功能必须包含：
1. API文档（docstrings）
2. 使用示例
3. 更新README.md相关部分

## 问题反馈

发现Bug或有功能建议：
1. 搜索已有的Issue
2. 如果没有相关问题，创建新Issue
3. 提供详细的重现步骤和预期行为

## 核心开发者

- **二狗** (项目创建者) - OpenClaw AI助理
- 欢迎更多贡献者加入！

## 许可证

本项目采用 MIT 许可证。提交代码即表示你同意你的贡献将以相同许可证发布。