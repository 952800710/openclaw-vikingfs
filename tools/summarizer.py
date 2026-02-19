#!/usr/bin/env python3
"""
VikingFS 内容摘要器
基于 OpenViking 思想的内容压缩和分层摘要生成
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class VikingSummarizer:
    """VikingFS 内容摘要和分层管理器"""
    
    def __init__(self, viking_root: str = None):
        self.viking_root = Path(viking_root or "~/.openclaw/workspace/viking").expanduser()
        self.config_path = self.viking_root / "config" / "viking-config.json"
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # 默认配置
            self.config = {
                "compression_rules": {
                    "L0_max_chars": 100,
                    "L1_max_chars": 500,
                    "L2_full_content": True
                }
            }
    
    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """提取关键点"""
        lines = text.strip().split('\n')
        key_points = []
        
        # 识别重要行：包含决策、TODO、重要标记
        important_patterns = [
            r'^\s*[-*•]\s*',  # 列表项
            r'^\s*\d+\.\s*',  # 数字列表
            r'\b(?:TODO|FIXME|IMPORTANT|NOTE|决策|重要)\b',
            r'\b(?:完成|进行中|阻塞)\b',
            r'^\s*#+\s+',  # 标题
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
                
            # 检查是否重要行
            is_important = any(re.search(pattern, line, re.IGNORECASE) for pattern in important_patterns)
            if is_important:
                key_points.append(line)
                if len(key_points) >= max_points:
                    break
        
        return key_points
    
    def generate_l0_summary(self, text: str) -> str:
        """生成L0摘要 (50-100字符)"""
        # 提取标题和关键信息
        lines = text.strip().split('\n')
        title = ""
        first_content = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 找标题
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
            elif not title and len(line) < 50:
                title = line[:50]
            
            # 找第一个有意义的内容
            if not first_content and len(line) > 20:
                first_content = line[:100]
                break
        
        # 组合摘要
        if title and first_content:
            summary = f"{title} | {first_content[:50]}..."
        elif title:
            summary = f"{title[:80]}..."
        elif first_content:
            summary = f"{first_content[:80]}..."
        else:
            summary = text[:80] + "..." if len(text) > 80 else text
        
        # 确保不超过L0长度限制
        max_chars = self.config.get("compression_rules", {}).get("L0_max_chars", 100)
        return summary[:max_chars]
    
    def generate_l1_overview(self, text: str) -> str:
        """生成L1概览 (200-500字符)"""
        key_points = self.extract_key_points(text, max_points=5)
        
        # 提取章节结构
        sections = []
        current_section = ""
        
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                if current_section:
                    sections.append(current_section)
                current_section = line.replace('## ', '') + ": "
            elif line.startswith('# '):
                if current_section:
                    sections.append(current_section)
                current_section = ""
            elif current_section and line and len(line) > 10:
                current_section += line[:100] + "... "
        
        if current_section:
            sections.append(current_section)
        
        # 构建概览
        overview_parts = []
        
        # 添加关键点
        if key_points:
            overview_parts.append("关键点:")
            for i, point in enumerate(key_points[:3], 1):
                overview_parts.append(f"  {i}. {point[:80]}")
        
        # 添加章节摘要
        if sections:
            overview_parts.append("章节:")
            for section in sections[:4]:
                overview_parts.append(f"  • {section[:100]}")
        
        # 如果没有提取到结构，使用智能截断
        if not overview_parts:
            # 尝试找最重要的段落
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
            if paragraphs:
                overview_parts.append("主要内容:")
                for para in paragraphs[:2]:
                    overview_parts.append(f"  • {para[:150]}...")
        
        overview = '\n'.join(overview_parts)
        
        # 确保不超过L1长度限制
        max_chars = self.config.get("compression_rules", {}).get("L1_max_chars", 500)
        return overview[:max_chars]
    
    def compress_content(self, content_path: str, target_tier: str = "L1") -> Dict[str, str]:
        """压缩内容到指定层级"""
        if not Path(content_path).exists():
            raise FileNotFoundError(f"文件不存在: {content_path}")
        
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = {
            "original_path": str(content_path),
            "original_size": len(content),
            "compressed_at": datetime.now().isoformat()
        }
        
        if target_tier == "L0":
            result["summary"] = self.generate_l0_summary(content)
            result["compressed_size"] = len(result["summary"])
        elif target_tier == "L1":
            result["overview"] = self.generate_l1_overview(content)
            result["compressed_size"] = len(result["overview"])
        elif target_tier == "L2":
            result["full_content"] = content
            result["compressed_size"] = len(content)
        else:
            raise ValueError(f"不支持的层级: {target_tier}")
        
        result["compression_ratio"] = result["compressed_size"] / result["original_size"] if result["original_size"] > 0 else 0
        
        return result
    
    def migrate_memory_file(self, memory_path: str):
        """迁移单个memory文件到VikingFS结构"""
        memory_file = Path(memory_path)
        if not memory_file.exists():
            print(f"警告: 文件不存在 {memory_path}")
            return
        
        # 确定目标位置
        if "memory" in str(memory_file):
            # 处理记忆文件
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', memory_file.name)
            if date_match:
                date_str = date_match.group(1)
                
                # 生成L0摘要
                l0_result = self.compress_content(str(memory_file), "L0")
                l0_path = self.viking_root / "memory" / "L0" / f"{date_str}-L0.md"
                l0_path.parent.mkdir(parents=True, exist_ok=True)
                with open(l0_path, 'w', encoding='utf-8') as f:
                    f.write(l0_result["summary"])
                
                # 生成L1概览
                l1_result = self.compress_content(str(memory_file), "L1")
                l1_path = self.viking_root / "memory" / "L1" / f"{date_str}-L1.md"
                l1_path.parent.mkdir(parents=True, exist_ok=True)
                with open(l1_path, 'w', encoding='utf-8') as f:
                    f.write(l1_result["overview"])
                
                # 创建L2链接
                l2_path = self.viking_root / "memory" / "L2" / f"{date_str}.md"
                l2_path.parent.mkdir(parents=True, exist_ok=True)
                if not l2_path.exists() or l2_path.is_symlink():
                    # 创建符号链接或复制内容
                    try:
                        os.symlink(str(memory_file.absolute()), str(l2_path))
                    except:
                        # 如果符号链接失败，复制内容
                        with open(memory_file, 'r', encoding='utf-8') as src, open(l2_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                
                print(f"迁移完成: {memory_file.name}")
                print(f"  L0摘要: {l0_path} ({l0_result['compressed_size']} chars)")
                print(f"  L1概览: {l1_path} ({l1_result['compressed_size']} chars)")
                print(f"  L2链接: {l2_path} -> {memory_file}")
                print(f"  压缩率: {l0_result['compression_ratio']:.1%} (L0), {l1_result['compression_ratio']:.1%} (L1)")
        
        return True

if __name__ == "__main__":
    # 测试代码
    summarizer = VikingSummarizer()
    
    # 测试文件
    test_content = """# 测试文档
    
## 项目概述
这是一个测试项目，用于验证VikingFS的内容摘要功能。

## 关键决策
1. 使用分层存储策略
2. 实现智能内容压缩
3. 支持动态上下文加载

## 当前进度
- 已完成：目录结构创建
- 进行中：摘要算法实现
- 待办：集成测试

## 重要信息
这个系统可以显著节省token使用量，提高AI助手的效率。"""
    
    print("L0摘要:")
    print(summarizer.generate_l0_summary(test_content))
    print("\nL1概览:")
    print(summarizer.generate_l1_overview(test_content))