"""
VikingFS 单元测试
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from viking.integration.bridge_v2 import OpenClawVikingBridgeV2
from viking.tools.summarizer import SmartSummarizer


class TestSmartSummarizer(unittest.TestCase):
    """测试智能摘要生成器"""
    
    def setUp(self):
        self.summarizer = SmartSummarizer()
    
    def test_generate_l0_summary(self):
        """测试L0摘要生成"""
        content = """
        今天天气很好，我去公园散步了。
        遇到了老朋友张三，我们一起聊了聊最近的工作。
        他说他的新项目进展很顺利。
        """
        
        result = self.summarizer.generate_l0_summary(content)
        
        # 验证结果不为空且长度合适
        self.assertIsNotNone(result)
        self.assertLess(len(result), 100)  # L0应该小于100字符
        self.assertGreater(len(result), 10)  # 但要有内容
    
    def test_generate_l1_overview(self):
        """测试L1概览生成"""
        content = """
        # 项目周报
        
        ## 本周完成
        1. 完成了用户登录模块的开发
        2. 修复了3个bug
        3. 编写了技术文档
        
        ## 下周计划
        1. 开始开发支付功能
        2. 进行性能优化
        """
        
        result = self.summarizer.generate_l1_overview(content)
        
        self.assertIsNotNone(result)
        self.assertLess(len(result), 500)  # L1应该小于500字符
        self.assertGreater(len(result), 50)  # 但要有足够内容


class TestOpenClawVikingBridgeV2(unittest.TestCase):
    """测试OpenClaw桥接器"""
    
    def setUp(self):
        self.bridge = OpenClawVikingBridgeV2()
    
    def test_classify_query(self):
        """测试查询分类"""
        # 测试管理查询
        result = self.bridge.classify_query("检查系统状态")
        self.assertEqual(result, "administrative")
        
        # 测试事实查询
        result = self.bridge.classify_query("Tony的时区是什么")
        self.assertEqual(result, "factual")
        
        # 测试创意查询
        result = self.bridge.classify_query("设计一个新功能")
        self.assertEqual(result, "creative")
    
    def test_calculate_saving_rate(self):
        """测试节省率计算"""
        original_tokens = 1000
        optimized_tokens = 100
        
        saving_rate = self.bridge.calculate_saving_rate(original_tokens, optimized_tokens)
        
        self.assertEqual(saving_rate, 90.0)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        bridge = OpenClawVikingBridgeV2()
        
        # 模拟查询
        query = "今天有什么安排？"
        result = bridge.query_memory(query)
        
        # 验证返回结构
        self.assertIn("answer", result)
        self.assertIn("metadata", result)
        self.assertIn("saving_rate", result.get("metadata", {}))


if __name__ == "__main__":
    unittest.main()
