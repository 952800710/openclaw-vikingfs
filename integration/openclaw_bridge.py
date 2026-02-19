#!/usr/bin/env python3
"""
OpenClaw-VikingFS 桥接模块
将VikingFS集成到OpenClaw的上下文管理系统中
"""

import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import sys
sys.path.append('/root/.openclaw/workspace/viking/tools')

try:
    from summarizer import VikingSummarizer
except ImportError:
    print("错误: 无法导入VikingSummarizer")
    sys.exit(1)

class OpenClawVikingBridge:
    """OpenClaw与VikingFS的桥接管理器"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or "~/.openclaw/workspace").expanduser()
        self.viking_root = self.workspace_root / "viking"
        self.summarizer = VikingSummarizer(str(self.viking_root))
        
        # 桥接配置
        self.config_path = self.viking_root / "config" / "bridge_config.json"
        self.load_config()
        
        # 统计数据
        self.stats_path = self.viking_root / "config" / "bridge_stats.json"
        self.stats = self.load_stats()
    
    def load_config(self):
        """加载桥接配置"""
        default_config = {
            "version": "1.0.0",
            "integration_mode": "hybrid",  # hybrid|viking_only|traditional
            "auto_migrate": True,
            "cache_enabled": True,
            "cache_ttl_seconds": 3600,
            "token_optimization": {
                "enabled": True,
                "target_saving_rate": 0.7,  # 70% token节省目标
                "fallback_to_traditional": True
            },
            "query_classification": {
                "enabled": True,
                "min_confidence": 0.6
            },
            "monitoring": {
                "enabled": True,
                "log_interval_queries": 10
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 合并配置
                self.config = {**default_config, **user_config}
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """保存配置"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def load_stats(self):
        """加载统计数据"""
        default_stats = {
            "total_queries": 0,
            "viking_queries": 0,
            "traditional_queries": 0,
            "total_tokens_viking": 0,
            "total_tokens_traditional": 0,
            "total_tokens_saved": 0,
            "average_saving_rate": 0.0,
            "query_type_distribution": {},
            "last_reset": datetime.now().isoformat(),
            "query_history": []
        }
        
        if self.stats_path.exists():
            with open(self.stats_path, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except:
                    return default_stats
        return default_stats
    
    def save_stats(self):
        """保存统计数据"""
        self.stats_path.parent.mkdir(exist_ok=True)
        with open(self.stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def query_context(self, query: str, context_type: str = "memory") -> Dict:
        """
        查询上下文 - 核心桥接方法
        query: 用户查询
        context_type: memory|skills|resources|projects
        """
        start_time = time.time()
        
        # 查询分类
        query_info = self.classify_query(query)
        
        # 根据配置选择策略
        if self.config["integration_mode"] == "viking_only":
            content, tier_info = self.query_viking_only(query_info, context_type)
        elif self.config["integration_mode"] == "traditional":
            content, tier_info = self.query_traditional(query_info, context_type)
        else:  # hybrid模式
            content, tier_info = self.query_hybrid(query_info, context_type)
        
        # 计算token使用
        response_size = len(content)
        response_tokens = response_size * 0.25  # 估算
        
        # 计算传统方式token使用
        traditional_size = self.estimate_traditional_size(context_type)
        traditional_tokens = traditional_size * 0.25
        
        # 计算节省
        if traditional_tokens > 0:
            saving_rate = 1 - (response_tokens / traditional_tokens)
            tokens_saved = traditional_tokens - response_tokens
        else:
            saving_rate = 0
            tokens_saved = 0
        
        # 更新统计数据
        self.update_stats(query_info, response_tokens, traditional_tokens, saving_rate)
        
        # 构建响应
        response = {
            "content": content,
            "metadata": {
                "query": query,
                "query_type": query_info["primary_type"],
                "query_confidence": query_info["confidence"],
                "response_size_bytes": response_size,
                "response_tokens_estimated": response_tokens,
                "traditional_tokens_estimated": traditional_tokens,
                "token_saving_rate": saving_rate,
                "tokens_saved": tokens_saved,
                "loaded_tiers": tier_info["tiers"],
                "response_time_ms": (time.time() - start_time) * 1000,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return response
    
    def classify_query(self, query: str) -> Dict:
        """查询分类器"""
        query_lower = query.lower()
        
        # 定义查询类型和模式
        type_patterns = {
            "factual": ["什么时候", "哪里", "谁", "是什么", "多少", "日期", "时间", "列出", "有哪些"],
            "creative": ["想法", "建议", "创意", "怎么办", "如何", "设计", "改进", "优化"],
            "administrative": ["状态", "进度", "检查", "报告", "总结", "概览", "汇总"],
            "analytical": ["为什么", "分析", "原因", "对比", "优劣", "优缺点", "评估"]
        }
        
        # 计算类型匹配度
        type_scores = {}
        for q_type, patterns in type_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in query_lower:
                    score += 1
            
            # 加分项：问号通常表示事实查询
            if q_type == "factual" and ("?" in query or "？" in query):
                score += 0.5
            
            if score > 0:
                type_scores[q_type] = score
        
        # 确定主要类型
        if type_scores:
            primary_type = max(type_scores, key=type_scores.get)
            confidence = type_scores[primary_type] / (sum(type_scores.values()) or 1)
        else:
            primary_type = "factual"
            confidence = 0.5
        
        return {
            "query": query,
            "primary_type": primary_type,
            "confidence": confidence,
            "type_scores": type_scores,
            "timestamp": datetime.now().isoformat()
        }
    
    def query_viking_only(self, query_info: Dict, context_type: str) -> Tuple[str, Dict]:
        """仅使用VikingFS查询"""
        # 根据查询类型确定层级
        tier_map = {
            "factual": ["L0", "L1"],
            "creative": ["L0", "L1", "L2"],
            "administrative": ["L0"],
            "analytical": ["L1", "L2"]
        }
        
        tiers = tier_map.get(query_info["primary_type"], ["L0", "L1"])
        
        # 加载内容
        content_parts = []
        for tier in tiers:
            tier_content = self.load_tier_content(tier, context_type)
            if tier_content:
                content_parts.append(tier_content)
        
        content = "\n\n".join(content_parts)
        
        return content, {
            "strategy": "viking_only",
            "tiers": tiers,
            "tier_count": len(tiers)
        }
    
    def query_hybrid(self, query_info: Dict, context_type: str) -> Tuple[str, Dict]:
        """混合模式查询"""
        # 根据置信度决定策略
        confidence = query_info["confidence"]
        
        if confidence < self.config["query_classification"]["min_confidence"]:
            # 置信度低，加载更多层级
            tiers = ["L0", "L1", "L2"]
            strategy = "hybrid_low_confidence"
        else:
            # 高置信度，智能选择
            if query_info["primary_type"] == "administrative":
                tiers = ["L0"]
                strategy = "hybrid_admin"
            elif query_info["primary_type"] in ["factual", "analytical"]:
                tiers = ["L0", "L1"]
                strategy = "hybrid_factual"
            else:  # creative
                tiers = ["L0", "L1", "L2"]
                strategy = "hybrid_creative"
        
        # 加载内容
        content_parts = []
        for tier in tiers:
            tier_content = self.load_tier_content(tier, context_type)
            if tier_content:
                content_parts.append(tier_content)
        
        content = "\n\n".join(content_parts)
        
        return content, {
            "strategy": strategy,
            "tiers": tiers,
            "confidence": confidence
        }
    
    def query_traditional(self, query_info: Dict, context_type: str) -> Tuple[str, Dict]:
        """传统方式查询（完整加载）"""
        # 直接加载L2层（完整内容）
        content = self.load_tier_content("L2", context_type)
        
        return content, {
            "strategy": "traditional",
            "tiers": ["L2"]
        }
    
    def load_tier_content(self, tier: str, context_type: str) -> Optional[str]:
        """加载指定层级的内容"""
        tier_dir = self.viking_root / context_type / tier
        
        if not tier_dir.exists():
            return None
        
        # 查找最新或相关的文件
        files = list(tier_dir.glob("*.md"))
        if not files:
            return None
        
        # 暂时只加载第一个文件
        file_path = files[0]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def estimate_traditional_size(self, context_type: str) -> int:
        """估算传统方式的内容大小"""
        # 估算加载完整L2层的大小
        l2_dir = self.viking_root / context_type / "L2"
        if not l2_dir.exists():
            return 0
        
        files = list(l2_dir.glob("*.md"))
        if not files:
            return 0
        
        total_size = 0
        for file in files[:3]:  # 估算前3个文件
            try:
                total_size += file.stat().st_size
            except:
                pass
        
        return total_size
    
    def update_stats(self, query_info: Dict, viking_tokens: float, 
                    traditional_tokens: float, saving_rate: float):
        """更新统计数据"""
        self.stats["total_queries"] += 1
        self.stats["viking_queries"] += 1
        
        self.stats["total_tokens_viking"] += viking_tokens
        self.stats["total_tokens_traditional"] += traditional_tokens
        self.stats["total_tokens_saved"] += (traditional_tokens - viking_tokens)
        
        # 更新平均节省率
        if self.stats["total_queries"] > 0:
            total_saving = self.stats["total_tokens_saved"]
            total_traditional = self.stats["total_tokens_traditional"]
            if total_traditional > 0:
                self.stats["average_saving_rate"] = total_saving / total_traditional
        
        # 更新查询类型分布
        q_type = query_info["primary_type"]
        if q_type not in self.stats["query_type_distribution"]:
            self.stats["query_type_distribution"][q_type] = 0
        self.stats["query_type_distribution"][q_type] += 1
        
        # 记录查询历史（保留最近100条）
        history_entry = {
            "query": query_info["query"],
            "type": q_type,
            "confidence": query_info["confidence"],
            "viking_tokens": viking_tokens,
            "traditional_tokens": traditional_tokens,
            "saving_rate": saving_rate,
            "timestamp": datetime.now().isoformat()
        }
        
        self.stats["query_history"].append(history_entry)
        if len(self.stats["query_history"]) > 100:
            self.stats["query_history"] = self.stats["query_history"][-100:]
        
        # 定期保存
        if self.stats["total_queries"] % self.config["monitoring"]["log_interval_queries"] == 0:
            self.save_stats()
    
    def get_performance_report(self) -> Dict:
        """获取性能报告"""
        return {
            "summary": {
                "total_queries": self.stats["total_queries"],
                "viking_queries": self.stats["viking_queries"],
                "traditional_queries": self.stats["traditional_queries"],
                "average_token_saving_rate": self.stats["average_saving_rate"],
                "total_tokens_saved": self.stats["total_tokens_saved"]
            },
            "query_type_distribution": self.stats["query_type_distribution"],
            "recent_queries": self.stats["query_history"][-10:] if self.stats["query_history"] else [],
            "config": {
                "integration_mode": self.config["integration_mode"],
                "token_optimization_enabled": self.config["token_optimization"]["enabled"]
            }
        }
    
    def migrate_all_to_viking(self):
        """将所有OpenClaw内容迁移到VikingFS"""
        print("开始迁移所有OpenClaw内容到VikingFS...")
        
        # 迁移记忆文件
        memory_dir = self.workspace_root / "memory"
        if memory_dir.exists():
            print(f"迁移记忆文件: {memory_dir}")
            for mem_file in memory_dir.glob("*.md"):
                self.summarizer.migrate_memory_file(str(mem_file))
        
        # 迁移技能元数据
        skills_dir = self.workspace_root
        skill_files = ["AGENTS.md", "SOUL.md", "USER.md", "IDENTITY.md"]
        for skill_file in skill_files:
            file_path = skills_dir / skill_file
            if file_path.exists():
                print(f"迁移技能文件: {skill_file}")
                self.migrate_skill_file(str(file_path))
        
        print("迁移完成!")
    
    def migrate_skill_file(self, file_path: str):
        """迁移技能文件"""
        file = Path(file_path)
        if not file.exists():
            return
        
        # 创建技能目录结构
        skill_name = file.stem
        skill_meta_dir = self.viking_root / "skills" / "meta"
        skill_source_dir = self.viking_root / "skills" / "source"
        
        skill_meta_dir.mkdir(parents=True, exist_ok=True)
        skill_source_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成摘要和概览
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成L0摘要
        l0_summary = self.summarizer.generate_l0_summary(content)
        l0_path = skill_meta_dir / f"{skill_name}-L0.md"
        with open(l0_path, 'w', encoding='utf-8') as f:
            f.write(l0_summary)
        
        # 生成L1概览
        l1_overview = self.summarizer.generate_l1_overview(content)
        l1_path = skill_meta_dir / f"{skill_name}-L1.md"
        with open(l1_path, 'w', encoding='utf-8') as f:
            f.write(l1_overview)
        
        # 创建L2链接
        l2_path = skill_source_dir / f"{skill_name}.md"
        if not l2_path.exists():
            try:
                os.symlink(str(file.absolute()), str(l2_path))
            except:
                # 如果符号链接失败，复制内容
                with open(file, 'r', encoding='utf-8') as src, open(l2_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
        
        print(f"  ✓ 迁移 {skill_name}: {len(content)} → {len(l0_summary)}/{len(l1_overview)} 字符")

def test_bridge():
    """测试桥接功能"""
    print("测试OpenClaw-VikingFS桥接...")
    print("=" * 60)
    
    bridge = OpenClawVikingBridge()
    
    # 测试查询
    test_queries = [
        "今天的日期是什么？",
        "检查系统状态",
        "分析一下我们的改造方案",
        "给我一个完整的项目报告"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = bridge.query_context(query, "memory")
        
        metadata = result["metadata"]
        print(f"  类型: {metadata['query_type']} (置信度: {metadata['query_confidence']:.2f})")
        print(f"  层级: {metadata['loaded_tiers']}")
        print(f"  大小: {metadata['response_size_bytes']} 字节")
        print(f"  Token估算: {metadata['response_tokens_estimated']:.0f}")
        print(f"  传统Token: {metadata['traditional_tokens_estimated']:.0f}")
        print(f"  节省率: {metadata['token_saving_rate']:.1%}")
        print(f"  响应时间: {metadata['response_time_ms']:.1f}ms")
    
    # 显示性能报告
    report = bridge.get_performance_report()
    print(f"\n性能报告:")
    print(f"  总查询数: {report['summary']['total_queries']}")
    print(f"  平均节省率: {report['summary']['average_token_saving_rate']:.1%}")
    print(f"  总节省tokens: {report['summary']['total_tokens_saved']:.0f}")
    
    return bridge

if __name__ == "__main__":
    bridge = test_bridge()