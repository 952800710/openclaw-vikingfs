#!/usr/bin/env python3
"""
VikingFS 记忆文件迁移脚本
将现有的 memory/*.md 文件迁移到 VikingFS 分层结构中
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from summarizer import VikingSummarizer

def migrate_all_memory_files():
    """迁移所有记忆文件"""
    workspace_root = Path("~/.openclaw/workspace").expanduser()
    memory_dir = workspace_root / "memory"
    viking_root = workspace_root / "viking"
    
    if not memory_dir.exists():
        print(f"错误: 记忆目录不存在 {memory_dir}")
        return False
    
    # 创建VikingFS结构
    viking_root.mkdir(exist_ok=True)
    for subdir in ["memory/L0", "memory/L1", "memory/L2"]:
        (viking_root / subdir).mkdir(parents=True, exist_ok=True)
    
    summarizer = VikingSummarizer(str(viking_root))
    
    # 迁移统计
    stats = {
        "total_files": 0,
        "migrated_files": 0,
        "failed_files": 0,
        "total_original_size": 0,
        "total_compressed_size_L0": 0,
        "total_compressed_size_L1": 0,
        "start_time": datetime.now().isoformat()
    }
    
    # 查找所有记忆文件
    memory_files = list(memory_dir.glob("*.md"))
    memory_files.sort()  # 按日期排序
    
    print(f"找到 {len(memory_files)} 个记忆文件")
    print("=" * 60)
    
    for memory_file in memory_files:
        try:
            print(f"处理: {memory_file.name}")
            
            # 读取文件大小
            file_size = memory_file.stat().st_size
            stats["total_original_size"] += file_size
            
            # 迁移文件
            result = summarizer.migrate_memory_file(str(memory_file))
            
            if result:
                stats["migrated_files"] += 1
                
                # 计算压缩大小
                l0_file = viking_root / "memory" / "L0" / f"{memory_file.stem}-L0.md"
                l1_file = viking_root / "memory" / "L1" / f"{memory_file.stem}-L1.md"
                
                if l0_file.exists():
                    stats["total_compressed_size_L0"] += l0_file.stat().st_size
                if l1_file.exists():
                    stats["total_compressed_size_L1"] += l1_file.stat().st_size
                    
                print(f"  ✓ 迁移成功")
            else:
                stats["failed_files"] += 1
                print(f"  ✗ 迁移失败")
                
        except Exception as e:
            stats["failed_files"] += 1
            print(f"  ✗ 错误: {e}")
        
        print()
    
    stats["total_files"] = len(memory_files)
    stats["end_time"] = datetime.now().isoformat()
    
    # 计算节省比例
    if stats["total_original_size"] > 0:
        stats["compression_ratio_L0"] = stats["total_compressed_size_L0"] / stats["total_original_size"]
        stats["compression_ratio_L1"] = stats["total_compressed_size_L1"] / stats["total_original_size"]
    else:
        stats["compression_ratio_L0"] = 0
        stats["compression_ratio_L1"] = 0
    
    # 保存迁移报告
    report_path = viking_root / "config" / "migration_report.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # 打印摘要报告
    print("=" * 60)
    print("迁移完成!")
    print(f"总文件数: {stats['total_files']}")
    print(f"成功迁移: {stats['migrated_files']}")
    print(f"失败文件: {stats['failed_files']}")
    print()
    print("压缩效果:")
    print(f"  L0摘要层: {stats['total_compressed_size_L0']:,} 字节")
    print(f"  L1概览层: {stats['total_compressed_size_L1']:,} 字节")
    print(f"  原始大小: {stats['total_original_size']:,} 字节")
    print()
    print(f"  L0压缩率: {stats['compression_ratio_L0']:.1%}")
    print(f"  L1压缩率: {stats['compression_ratio_L1']:.1%}")
    print()
    
    # 计算预期token节省
    # 假设平均每个字符消耗 0.25 token（中英文混合）
    original_tokens = stats["total_original_size"] * 0.25
    l1_tokens = stats["total_compressed_size_L1"] * 0.25
    
    if original_tokens > 0:
        token_saving = 1 - (l1_tokens / original_tokens)
        print(f"预期token节省:")
        print(f"  原始token数: ~{original_tokens:,.0f}")
        print(f"  L1层token数: ~{l1_tokens:,.0f}")
        print(f"  节省比例: {token_saving:.1%}")
    
    return True

def create_viking_index():
    """创建VikingFS索引文件"""
    viking_root = Path("~/.openclaw/workspace/viking").expanduser()
    
    index = {
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "description": "VikingFS统一上下文索引",
        "memory_files": [],
        "skill_files": [],
        "resource_files": []
    }
    
    # 扫描memory目录
    memory_dir = viking_root / "memory"
    if memory_dir.exists():
        for tier in ["L0", "L1", "L2"]:
            tier_dir = memory_dir / tier
            if tier_dir.exists():
                for file in tier_dir.glob("*.md"):
                    index["memory_files"].append({
                        "path": str(file.relative_to(viking_root)),
                        "tier": tier,
                        "size": file.stat().st_size,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
    
    # 保存索引
    index_path = viking_root / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"索引已创建: {index_path}")
    print(f"索引包含 {len(index['memory_files'])} 个记忆文件")
    
    return index

if __name__ == "__main__":
    print("VikingFS 记忆文件迁移工具")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--index":
        create_viking_index()
    else:
        migrate_all_memory_files()