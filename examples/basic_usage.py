"""
VikingFS 使用示例
================

本示例展示如何在不同场景下使用 VikingFS
"""

from viking.integration.bridge_v2 import OpenClawVikingBridgeV2


def example_1_basic_query():
    """示例1：基本查询"""
    print("=" * 50)
    print("示例1：基本查询")
    print("=" * 50)
    
    # 初始化桥接器
    bridge = OpenClawVikingBridgeV2()
    
    # 执行查询
    query = "今天是什么日期？"
    result = bridge.query_memory(query)
    
    print(f"查询: {query}")
    print(f"回答: {result['answer']}")
    print(f"Token节省率: {result['metadata']['saving_rate']}%")
    print(f"响应时间: {result['metadata']['response_time_ms']}ms")
    print()


def example_2_administrative_query():
    """示例2：管理类查询（最高节省率）"""
    print("=" * 50)
    print("示例2：管理类查询")
    print("=" * 50)
    
    bridge = OpenClawVikingBridgeV2()
    
    # 管理查询通常只需要 L0 层
    queries = [
        "检查系统状态",
        "今天有什么安排？",
        "最近的任务是什么？"
    ]
    
    for query in queries:
        result = bridge.query_memory(query)
        print(f"查询: {query}")
        print(f"加载层级: {result['metadata']['layers_loaded']}")
        print(f"Token节省: {result['metadata']['saving_rate']}%")
        print()


def example_3_factual_query():
    """示例3：事实类查询（平衡性能和准确性）"""
    print("=" * 50)
    print("示例3：事实类查询")
    print("=" * 50)
    
    bridge = OpenClawVikingBridgeV2()
    
    # 事实查询通常需要 L0 + L1
    queries = [
        "Tony的时区是什么？",
        "项目截止日期是什么时候？",
        "服务器配置是什么？"
    ]
    
    for query in queries:
        result = bridge.query_memory(query)
        print(f"查询: {query}")
        print(f"回答: {result['answer'][:100]}...")  # 截断显示
        print(f"Token节省: {result['metadata']['saving_rate']}%")
        print()


def example_4_creative_query():
    """示例4：创意类查询（完整上下文）"""
    print("=" * 50)
    print("示例4：创意类查询")
    print("=" * 50)
    
    bridge = OpenClawVikingBridgeV2()
    
    # 创意查询需要完整上下文
    query = "帮我设计一个创新的功能方案"
    result = bridge.query_memory(query)
    
    print(f"查询: {query}")
    print(f"加载层级: {result['metadata']['layers_loaded']}")
    print(f"Token节省: {result['metadata']['saving_rate']}% (较低，因为需要完整信息)")
    print()


def example_5_performance_dashboard():
    """示例5：性能监控面板"""
    print("=" * 50)
    print("示例5：性能监控面板")
    print("=" * 50)
    
    bridge = OpenClawVikingBridgeV2()
    
    # 执行一些查询
    queries = [
        "检查系统状态",
        "今天有什么安排？",
        "Tony的时区是什么？",
        "帮我设计一个功能"
    ]
    
    for query in queries:
        bridge.query_memory(query)
    
    # 获取性能统计
    dashboard = bridge.get_performance_dashboard()
    
    print("性能统计:")
    print(f"  总查询数: {dashboard['summary']['total_queries']}")
    print(f"  平均节省率: {dashboard['summary']['average_saving_rate']}%")
    print(f"  总节省Token: {dashboard['summary']['total_tokens_saved']:,}")
    print()
    
    print("查询类型分布:")
    for query_type, stats in dashboard['query_types'].items():
        print(f"  {query_type}: {stats['count']}次, 平均节省{stats['avg_saving']}%")
    print()


def example_6_economic_benefits():
    """示例6：经济效益计算"""
    print("=" * 50)
    print("示例6：经济效益计算")
    print("=" * 50)
    
    bridge = OpenClawVikingBridgeV2()
    
    # 计算经济效益
    savings = bridge.calculate_economic_benefits(
        daily_queries=100,
        avg_token_cost=0.000001  # $0.001 per 1000 tokens
    )
    
    print("成本节省分析:")
    print(f"  每日节省: ${savings['daily_savings']:.2f}")
    print(f"  每月节省: ${savings['monthly_savings']:.2f}")
    print(f"  每年节省: ${savings['yearly_savings']:.2f}")
    print()
    
    print("Token节省:")
    print(f"  每日: {savings['tokens_saved_daily']:,} tokens")
    print(f"  每月: {savings['tokens_saved_monthly']:,} tokens")
    print(f"  每年: {savings['tokens_saved_yearly']:,} tokens")
    print()


if __name__ == "__main__":
    """运行所有示例"""
    print("\nVikingFS 使用示例\n")
    print("=" * 50)
    
    example_1_basic_query()
    example_2_administrative_query()
    example_3_factual_query()
    example_4_creative_query()
    example_5_performance_dashboard()
    example_6_economic_benefits()
    
    print("=" * 50)
    print("所有示例运行完成！")
    print("=" * 50)
