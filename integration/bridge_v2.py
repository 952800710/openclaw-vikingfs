#!/usr/bin/env python3
"""
OpenClaw-VikingFS 桥接模块 v2
独立版本，不依赖外部模块
"""

import os
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

class VikingSummarizerSimple:
    """简化的Viking摘要器"""
    
    def __init__(self, viking_root: str):
        self.viking_root = Path(viking_root)
    
    def generate_l0_summary(self, content: str) -> str:
        """生成L0摘要 (50-100字符)"""
        lines = content.split('\n')
        
        # 提取关键信息
        date_info = ""
        key_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 提取日期信息
            if "202" in line and ("-" in line or "年" in line):
                date_info = line[:50]
            
            # 提取关键点
            if line.startswith("- ") or line.startswith("• "):
                key_points.append(line)
                if len(key_points) >= 3:
                    break
        
        # 构建摘要
        summary = ""
        if date_info:
            summary += date_info[:50]
        
        if key_points:
            for i, point in enumerate(key_points[:2]):
                if len(summary) < 80:  # 控制长度
                    if summary:
                        summary += " | "
                    summary += point.replace("- ", "").replace("• ", "")[:30]
        
        # 确保长度
        if len(summary) < 40:
            summary = content[:100].replace('\n', ' ').strip()
        
        return summary[:100]
    
    def generate_l1_overview(self, content: str) -> str:
        """生成L1概览 (200-500字符)"""
        lines = content.split('\n')
        
        # 提取关键点和章节
        key_points = []
        chapters = []
        current_chapter = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别章节
            if line.startswith("## "):
                current_chapter = line[3:].strip()
                chapters.append(current_chapter)
            
            # 关键点
            elif line.startswith("- ") or line.startswith("• ") or line.startswith("1."):
                if current_chapter:
                    key_points.append(f"{current_chapter}: {line}")
                else:
                    key_points.append(line)
        
        # 构建概览
        overview = "关键点:\n"
        for i, point in enumerate(key_points[:5]):
            overview += f"  {i+1}. {point[:80]}\n"
        
        overview += "章节:\n"
        for chapter in chapters[:3]:
            overview += f"  • {chapter}\n"
        
        return overview[:500]

class OpenClawVikingBridgeV2:
    """OpenClaw-VikingFS桥接v2版"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or "/root/.openclaw/workspace")
        self.viking_root = self.workspace_root / "viking"
        self.summarizer = VikingSummarizerSimple(str(self.viking_root))
        
        # 确保目录存在
        self.viking_root.mkdir(exist_ok=True)
        for dir_name in ["memory/L0", "memory/L1", "memory/L2", "config", "integration"]:
            (self.viking_root / dir_name).mkdir(parents=True, exist_ok=True)
        
        # 配置文件
        self.config_file = self.viking_root / "config" / "bridge_config.json"
        self.stats_file = self.viking_root / "config" / "bridge_stats.json"
        
        # 加载配置
        self.config = self.load_config()
        self.stats = self.load_stats()
        
        print(f"✅ VikingFS Bridge v2 初始化完成")
        print(f"   Workspace: {self.workspace_root}")
        print(f"   VikingFS: {self.viking_root}")
    
    def load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "version": "2.0.0",
            "mode": "hybrid",  # hybrid|viking|traditional
            "auto_summarize": True,
            "cache_enabled": True,
            "token_optimization": True,
            "monitoring": True,
            "query_classifier": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    return {**default_config, **user_config}
            except:
                return default_config
        return default_config
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def load_stats(self) -> Dict:
        """加载统计数据"""
        default_stats = {
            "queries_total": 0,
            "queries_viking": 0,
            "tokens_total": 0,
            "tokens_saved": 0,
            "saving_rate_avg": 0.0,
            "query_types": {},
            "performance_history": []
        }
        
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_stats
        return default_stats
    
    def save_stats(self):
        """保存统计数据"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def classify_query(self, query: str) -> Dict:
        """查询分类"""
        query_lower = query.lower()
        
        # 简单分类规则
        if any(word in query_lower for word in ["什么时候", "日期", "时间", "几号"]):
            q_type = "factual_date"
            confidence = 0.9
        elif any(word in query_lower for word in ["检查", "状态", "报告", "总结"]):
            q_type = "administrative"
            confidence = 0.8
        elif any(word in query_lower for word in ["分析", "为什么", "原因", "对比"]):
            q_type = "analytical"
            confidence = 0.7
        elif any(word in query_lower for word in ["如何", "改进", "创意", "建议"]):
            q_type = "creative"
            confidence = 0.7
        elif any(word in query_lower for word in ["列出", "有哪些", "什么技能"]):
            q_type = "factual_list"
            confidence = 0.8
        elif "?" in query or "？" in query:
            q_type = "factual"
            confidence = 0.6
        else:
            q_type = "general"
            confidence = 0.5
        
        return {
            "type": q_type,
            "confidence": confidence,
            "original": query
        }
    
    def get_tier_strategy(self, query_type: str, confidence: float) -> List[str]:
        """根据查询类型确定层级策略"""
        if not self.config["query_classifier"]:
            return ["L0", "L1"]  # 默认
        
        if query_type == "administrative":
            return ["L0"]
        elif query_type in ["factual_date", "factual_list", "factual"]:
            return ["L0", "L1"]
        elif query_type == "analytical":
            return ["L1", "L2"] if confidence > 0.7 else ["L0", "L1", "L2"]
        elif query_type == "creative":
            return ["L0", "L1", "L2"]
        else:
            return ["L0", "L1"]
    
    def load_tier_content(self, tier: str) -> str:
        """加载指定层级的内容"""
        tier_path = self.viking_root / "memory" / tier
        
        if not tier_path.exists():
            return ""
        
        # 查找最新的记忆文件
        md_files = list(tier_path.glob("*.md"))
        if not md_files:
            return ""
        
        # 取最新的文件
        latest_file = sorted(md_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    def query_memory(self, user_query: str) -> Dict:
        """主查询接口"""
        start_time = time.time()
        
        # 查询分类
        query_info = self.classify_query(user_query)
        
        # 确定层级策略
        if self.config["mode"] == "traditional":
            tiers = ["L2"]
            strategy = "traditional"
        elif self.config["mode"] == "viking":
            tiers = ["L0", "L1"]
            strategy = "viking_only"
        else:  # hybrid
            tiers = self.get_tier_strategy(query_info["type"], query_info["confidence"])
            strategy = "hybrid"
        
        # 加载内容
        content_parts = []
        for tier in tiers:
            tier_content = self.load_tier_content(tier)
            if tier_content:
                content_parts.append(f"--- {tier} ---\n{tier_content}")
        
        content = "\n\n".join(content_parts)
        
        # 计算统计
        response_chars = len(content)
        response_tokens = response_chars * 0.25
        
        # 估算传统方式
        l2_content = self.load_tier_content("L2")
        traditional_chars = len(l2_content)
        traditional_tokens = traditional_chars * 0.25 if traditional_chars > 0 else response_tokens * 3
        
        # 计算节省
        if traditional_tokens > 0:
            saving_rate = 1 - (response_tokens / traditional_tokens)
            tokens_saved = traditional_tokens - response_tokens
        else:
            saving_rate = 0.0
            tokens_saved = 0.0
        
        # 更新统计
        self.update_stats(query_info, response_tokens, traditional_tokens, saving_rate)
        
        # 构建响应
        response_time = (time.time() - start_time) * 1000
        
        return {
            "content": content,
            "metadata": {
                "query": user_query,
                "query_type": query_info["type"],
                "confidence": query_info["confidence"],
                "strategy": strategy,
                "tiers_loaded": tiers,
                "response_chars": response_chars,
                "response_tokens": response_tokens,
                "traditional_tokens": traditional_tokens,
                "token_saving_rate": saving_rate,
                "tokens_saved": tokens_saved,
                "response_time_ms": response_time,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def update_stats(self, query_info: Dict, viking_tokens: float, 
                    traditional_tokens: float, saving_rate: float):
        """更新统计"""
        self.stats["queries_total"] += 1
        self.stats["queries_viking"] += 1
        self.stats["tokens_total"] += viking_tokens
        self.stats["tokens_saved"] += (traditional_tokens - viking_tokens)
        
        # 更新平均节省率
        if self.stats["queries_total"] > 0:
            total_saved = self.stats["tokens_saved"]
            total_traditional = self.stats["queries_total"] * traditional_tokens
            if total_traditional > 0:
                self.stats["saving_rate_avg"] = total_saved / total_traditional
        
        # 更新查询类型分布
        q_type = query_info["type"]
        if q_type not in self.stats["query_types"]:
            self.stats["query_types"][q_type] = 0
        self.stats["query_types"][q_type] += 1
        
        # 记录性能历史
        history_entry = {
            "query": query_info["original"][:50],
            "type": q_type,
            "viking_tokens": viking_tokens,
            "saving_rate": saving_rate,
            "time": datetime.now().isoformat()
        }
        
        self.stats["performance_history"].append(history_entry)
        if len(self.stats["performance_history"]) > 50:
            self.stats["performance_history"] = self.stats["performance_history"][-50:]
        
        # 定期保存
        if self.stats["queries_total"] % 10 == 0:
            self.save_stats()
    
    def get_performance_dashboard(self) -> Dict:
        """获取性能仪表板"""
        return {
            "summary": {
                "total_queries": self.stats["queries_total"],
                "viking_queries": self.stats["queries_viking"],
                "average_saving_rate": f"{self.stats['saving_rate_avg']:.1%}",
                "total_tokens_saved": f"{self.stats['tokens_saved']:,.0f}",
                "estimated_cost_saving_usd": f"${self.stats['tokens_saved'] * 0.000001:.2f}"
            },
            "query_type_distribution": self.stats["query_types"],
            "recent_performance": self.stats["performance_history"][-5:] if self.stats["performance_history"] else [],
            "configuration": {
                "mode": self.config["mode"],
                "token_optimization": self.config["token_optimization"],
                "auto_summarize": self.config["auto_summarize"]
            }
        }
    
    def migrate_openclaw_memory(self):
        """迁移OpenClaw记忆到VikingFS"""
        print("🔄 开始迁移OpenClaw记忆到VikingFS...")
        
        memory_dir = self.workspace_root / "memory"
        if not memory_dir.exists():
            print("❌ 找不到memory目录")
            return False
        
        migrated_count = 0
        
        for mem_file in memory_dir.glob("*.md"):
            try:
                with open(mem_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 生成摘要
                l0_summary = self.summarizer.generate_l0_summary(content)
                l1_overview = self.summarizer.generate_l1_overview(content)
                
                # 保存到VikingFS
                file_name = mem_file.name
                
                # L0
                l0_path = self.viking_root / "memory" / "L0" / file_name
                with open(l0_path, 'w', encoding='utf-8') as f:
                    f.write(l0_summary)
                
                # L1
                l1_path = self.viking_root / "memory" / "L1" / file_name
                with open(l1_path, 'w', encoding='utf-8') as f:
                    f.write(l1_overview)
                
                # L2 (符号链接)
                l2_path = self.viking_root / "memory" / "L2" / file_name
                if not l2_path.exists():
                    try:
                        os.symlink(str(mem_file.absolute()), str(l2_path))
                    except:
                        # 如果符号链接失败，复制内容
                        with open(mem_file, 'r', encoding='utf-8') as src, open(l2_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                
                print(f"  ✓ 迁移 {file_name}: {len(content)} → {len(l0_summary)}/{len(l1_overview)} 字符")
                migrated_count += 1
                
            except Exception as e:
                print(f"  ✗ 迁移失败 {mem_file}: {e}")
        
        print(f"✅ 迁移完成: {migrated_count} 个文件")
        return True

def test_bridge_v2():
    """测试桥接v2"""
    print("🧪 测试VikingFS Bridge v2")
    print("=" * 60)
    
    # 初始化
    bridge = OpenClawVikingBridgeV2()
    
    # 确保有数据
    bridge.migrate_openclaw_memory()
    
    print("\n🔍 测试查询:")
    print("-" * 40)
    
    test_queries = [
        "今天是什么日期？",
        "检查系统状态",
        "我安装了哪些技能？",
        "分析一下我们的改造方案",
        "如何改进这个系统？"
    ]
    
    for query in test_queries:
        print(f"\n📝 查询: {query}")
        result = bridge.query_memory(query)
        meta = result["metadata"]
        
        print(f"  类型: {meta['query_type']} (置信度: {meta['confidence']:.2f})")
        print(f"  策略: {meta['strategy']}")
        print(f"  层级: {meta['tiers_loaded']}")
        print(f"  字符数: {meta['response_chars']:,}")
        print(f"  Token估算: {meta['response_tokens']:.0f}")
        print(f"  传统Token: {meta['traditional_tokens']:.0f}")
        print(f"  节省率: {meta['token_saving_rate']:.1%}")
        print(f"  响应时间: {meta['response_time_ms']:.1f}ms")
    
    # 显示仪表板
    print("\n📊 性能仪表板:")
    print("-" * 40)
    
    dashboard = bridge.get_performance_dashboard()
    summary = dashboard["summary"]
    
    print(f"总查询数: {summary['total_queries']}")
    print(f"平均节省率: {summary['average_saving_rate']}")
    print(f"总节省Token: {summary['total_tokens_saved']}")
    print(f"估算成本节省: {summary['estimated_cost_saving_usd']}")
    
    print("\n查询类型分布:")
    for q_type, count in dashboard["query_type_distribution"].items():
        print(f"  {q_type}: {count}")
    
    return bridge

if __name__ == "__main__":
    bridge = test_bridge_v2()