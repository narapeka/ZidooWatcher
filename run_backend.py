#!/usr/bin/env python3
"""
ZidooWatcher 后端启动脚本
直接启动 FastAPI 服务
"""

import os
import sys
import subprocess

def main():
    print("🚀 启动 ZidooWatcher 后端服务...")
    
    # 切换到backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    
    try:
        # 启动后端服务
        cmd = [sys.executable, "main.py"]
        subprocess.run(cmd, cwd=backend_dir, check=True)
    except KeyboardInterrupt:
        print("\n⏹️ 后端服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 后端启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 