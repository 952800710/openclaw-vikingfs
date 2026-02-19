#!/usr/bin/env python3
"""
VikingFS 桥接服务
长期运行，提供API接口和监控
"""

import time
import json
import threading
from datetime import datetime
from pathlib import Path
from bridge_v2 import OpenClawVikingBridgeV2

class VikingFSService:
    """VikingFS服务"""
    
    def __init__(self):
        self.bridge = OpenClawVikingBridgeV2()
        self.running = True
        self.query_count = 0
        self.service_start = datetime.now()
        
        print(f"🚀 VikingFS服务启动于 {self.service_start}")
        print(f"   工作目录: {self.bridge.workspace_root}")
        print(f"   运行模式: {self.bridge.config.get('mode', 'hybrid')}")
    
    def run(self):
        """主服务循环"""
        print("📡 VikingFS服务运行中...")
        print("   按 Ctrl+C 停止")
        print()
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        
        try:
            # 简单HTTP服务或等待信号
            while self.running:
                time.sleep(1)
                
                # 每10秒打印状态
                if int(time.time()) % 10 == 0:
                    self.print_status()
        
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号")
        finally:
            self.running = False
            self.shutdown()
    
    def monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查配置文件更新
                self.check_config_update()
                
                # 自动保存统计
                if self.query_count % 20 == 0:
                    self.bridge.save_stats()
                
                time.sleep(5)
                
            except Exception as e:
                print(f"监控错误: {e}")
    
    def check_config_update(self):
        """检查配置更新"""
        config_file = self.bridge.viking_root / "config" / "bridge_config.json"
        if config_file.exists():
            stat = config_file.stat()
            if hasattr(self, 'last_config_mtime') and stat.st_mtime > self.last_config_mtime:
                print("🔄 检测到配置更新，重新加载...")
                self.bridge.config = self.bridge.load_config()
            
            self.last_config_mtime = stat.st_mtime
    
    def print_status(self):
        """打印服务状态"""
        dashboard = self.bridge.get_performance_dashboard()
        
        print(f"🕐 {datetime.now().strftime('%H:%M:%S')} VikingFS状态:")
        print(f"   运行时间: {self.get_uptime()}")
        print(f"   总查询: {dashboard['summary']['total_queries']}")
        print(f"   平均节省: {dashboard['summary']['average_saving_rate']}")
        print(f"   累计节省: {dashboard['summary']['total_tokens_saved']} tokens")
        print()
    
    def get_uptime(self) -> str:
        """获取运行时间"""
        uptime = datetime.now() - self.service_start
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        seconds = uptime.seconds % 60
        
        if uptime.days > 0:
            return f"{uptime.days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def shutdown(self):
        """关闭服务"""
        print("🛑 正在关闭VikingFS服务...")
        
        # 保存最后状态
        self.bridge.save_stats()
        
        print("💾 统计已保存")
        print(f"📊 最终统计:")
        dashboard = self.bridge.get_performance_dashboard()
        
        for key, value in dashboard['summary'].items():
            if isinstance(value, (int, float)) and key != 'total_queries':
                continue
            print(f"   {key}: {value}")
        
        print("👋 VikingFS服务已停止")

if __name__ == "__main__":
    service = VikingFSService()
    service.run()
