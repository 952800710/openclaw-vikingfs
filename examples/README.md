# OpenClaw-VikingFS 示例文档

## 快速开始示例

### 1. 安装和初始化

```bash
# 克隆仓库
git clone https://github.com/952800710/openclaw-vikingfs.git
cd openclaw-vikingfs

# 安装依赖
pip install -r requirements.txt

# 运行演示
python examples/basic_usage.py
```

### 2. 基本使用

```python
from viking.integration.bridge_v2 import OpenClawVikingBridgeV2

# 初始化
bridge = OpenClawVikingBridgeV2()

# 查询
result = bridge.query_memory("今天有什么安排？")
print(result['answer'])
```

### 3. 查看性能统计

```python
# 获取监控面板
dashboard = bridge.get_performance_dashboard()
print(f"平均节省率: {dashboard['summary']['average_saving_rate']}%")
```

## 更多示例

- `basic_usage.py` - 基础用法示例
- `migration_example.py` - 数据迁移示例（待添加）
- `custom_config_example.py` - 自定义配置示例（待添加）

## 运行测试

```bash
# 运行所有测试
python -m unittest discover tests/

# 运行特定测试
python -m unittest tests.test_vikingfs.TestSmartSummarizer
```
