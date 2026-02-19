#!/usr/bin/env python3
"""
VikingFS 分层检索测试
模拟不同查询场景，测试 L0/L1/L2 分层效果
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

class VikingFSTester:
    """VikingFS 测试器"""
    
    def __init__(self):
        self.viking_root = Path("~/.openclaw/workspace/viking").expanduser()
        self.test_results = []
    
    def query_classifier(self, query: str) -> dict:
        """查询分类器"""
        query_lower = query.lower()
        
        # 定义查询类型
        query_types = {
            "factual": ["什么时候", "哪里", "谁", "是什么", "多少", "日期", "时间"],
            "creative": ["想法", "建议", "创意", "怎么办", "如何", "设计"],
            "administrative": ["状态", "进度", "检查", "报告", "总结"],
            "analytical": ["为什么", "分析", "原因", "对比", "优劣"]
        }
        
        # 匹配查询类型
        matched_types = []
        for q_type, patterns in query_types.items():
            for pattern in patterns:
                if pattern in query_lower:
                    matched_types.append(q_type)
                    break
        
        # 默认分类
        if not matched_types:
            if "?" in query or "？" in query:
                matched_types.append("factual")
            else:
                matched_types.append("administrative")
        
        return {
            "query": query,
            "types": matched_types[:2],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_relevant_tier(self, query_type: str) -> list:
        """根据查询类型获取相关层级"""
        tier_map = {
            "factual": ["L0", "L1"],  # 事实查询：只需要摘要和概览
            "creative": ["L0", "L1", "L2"],  # 创意查询：需要完整上下文
            "administrative": ["L0"],  # 管理查询：只需要摘要
            "analytical": ["L1", "L2"]  # 分析查询：需要概览和详细
        }
        return tier_map.get(query_type, ["L0", "L1", "L2"])
    
    def search_vikingfs(self, query: str, use_l0_only: bool = False) -> dict:
        """在VikingFS中搜索"""
        # 分析查询
        query_info = self.query_classifier(query)
        query_types = query_info["types"]
        
        print(f"查询: '{query}'")
        print(f"分类: {query_types}")
        
        # 确定需要加载的层级
        relevant_tiers = []
        for q_type in query_types:
            tiers = self.get_relevant_tier(q_type)
            relevant_tiers.extend(tiers)
        relevant_tiers = list(set(relevant_tiers))  # 去重
        
        if use_l0_only:
            relevant_tiers = ["L0"]
        
        print(f"加载层级: {relevant_tiers}")
        
        # 加载内容
        loaded_content = {}
        total_size = 0
        
        for tier in relevant_tiers:
            tier_dir = self.viking_root / "memory" / tier
            if tier_dir.exists():
                # 查找相关文件
                for file in tier_dir.glob("*.md"):
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        loaded_content[f"{tier}:{file.name}"] = {
                            "content": content,
                            "size": len(content),
                            "tier": tier
                        }
                        total_size += len(content)
                        break  # 先只加载一个文件测试
        
        # 生成响应
        response = {
            "query": query,
            "query_info": query_info,
            "loaded_tiers": relevant_tiers,
            "content_count": len(loaded_content),
            "total_size_bytes": total_size,
            "loaded_content": loaded_content,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def simulate_token_usage(self, response: dict) -> dict:
        """模拟token使用情况"""
        # 假设每个字符消耗 0.25 token（中英文混合）
        total_chars = response["total_size_bytes"]
        total_tokens = total_chars * 0.25
        
        # 模拟传统方式（总是加载L2）
        l2_dir = self.viking_root / "memory" / "L2"
        l2_size = 0
        for file in l2_dir.glob("*.md"):
            l2_size += file.stat().st_size
            break
        
        traditional_tokens = l2_size * 0.25
        
        # 计算节省
        if traditional_tokens > 0:
            saving_percentage = 1 - (total_tokens / traditional_tokens)
        else:
            saving_percentage = 0
        
        return {
            "vikingfs_tokens": total_tokens,
            "traditional_tokens": traditional_tokens,
            "token_saving_percentage": saving_percentage,
            "token_saving_absolute": traditional_tokens - total_tokens,
            "estimated_cost_saving_usd": (traditional_tokens - total_tokens) * 0.000001  # 假设 $0.001/1000 tokens
        }
    
    def run_test_suite(self):
        """运行测试套件"""
        test_queries = [
            "今天是什么日期？",
            "我安装了哪些技能？",
            "Tony的工作风格是什么？",
            "OpenViking的核心思想有哪些？",
            "给我一个关于当前工作的完整报告",
            "我们应该如何改进这个系统？",
            "检查系统状态"
        ]
        
        print("VikingFS 分层检索测试")
        print("=" * 60)
        
        for query in test_queries:
            print(f"\n{'='*40}")
            
            # 测试正常模式
            start_time = time.time()
            response = self.search_vikingfs(query)
            elapsed = time.time() - start_time
            
            # 计算token节省
            token_info = self.simulate_token_usage(response)
            
            # 收集结果
            result = {
                "query": query,
                "query_types": response["query_info"]["types"],
                "loaded_tiers": response["loaded_tiers"],
                "content_size_bytes": response["total_size_bytes"],
                "response_time_ms": round(elapsed * 1000, 2),
                "token_info": token_info
            }
            
            self.test_results.append(result)
            
            # 打印结果
            print(f"查询: {query}")
            print(f"类型: {response['query_info']['types']}")
            print(f"加载层级: {response['loaded_tiers']}")
            print(f"内容大小: {response['total_size_bytes']:,} 字节")
            print(f"响应时间: {elapsed*1000:.1f}ms")
            print(f"Token使用: {token_info['vikingfs_tokens']:.0f} tokens")
            print(f"传统方式: {token_info['traditional_tokens']:.0f} tokens")
            print(f"节省比例: {token_info['token_saving_percentage']:.1%}")
            
            # 显示实际内容
            for key, content_info in response["loaded_content"].items():
                print(f"\n{content_info['tier']}层内容:")
                print("-" * 30)
                print(content_info["content"][:200] + "..." if len(content_info["content"]) > 200 else content_info["content"])
        
        return self.test_results
    
    def generate_report(self):
        """生成测试报告"""
        if not self.test_results:
            print("没有测试结果")
            return
        
        print("\n" + "="*60)
        print("VikingFS 测试报告")
        print("="*60)
        
        total_queries = len(self.test_results)
        avg_token_saving = sum(r["token_info"]["token_saving_percentage"] for r in self.test_results) / total_queries
        avg_response_time = sum(r["response_time_ms"] for r in self.test_results) / total_queries
        
        print(f"总测试查询数: {total_queries}")
        print(f"平均token节省率: {avg_token_saving:.1%}")
        print(f"平均响应时间: {avg_response_time:.1f}ms")
        
        # 按查询类型统计
        type_stats = {}
        for result in self.test_results:
            for q_type in result["query_types"]:
                if q_type not in type_stats:
                    type_stats[q_type] = {"count": 0, "total_saving": 0}
                type_stats[q_type]["count"] += 1
                type_stats[q_type]["total_saving"] += result["token_info"]["token_saving_percentage"]
        
        print("\n按查询类型统计:")
        for q_type, stats in type_stats.items():
            avg_saving = stats["total_saving"] / stats["count"] if stats["count"] > 0 else 0
            print(f"  {q_type}: {stats['count']}次查询, 平均节省 {avg_saving:.1%}")
        
        # 保存报告
        report = {
            "test_date": datetime.now().isoformat(),
            "total_queries": total_queries,
            "average_token_saving": avg_token_saving,
            "average_response_time_ms": avg_response_time,
            "query_type_stats": type_stats,
            "detailed_results": self.test_results
        }
        
        report_path = self.viking_root / "config" / "test_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细报告已保存: {report_path}")
        return report

def main():
    """主测试函数"""
    tester = VikingFSTester()
    
    print("开始VikingFS分层检索测试...")
    tester.run_test_suite()
    tester.generate_report()
    
    print("\n" + "="*60)
    print("测试完成！")

if __name__ == "__main__":
    main()