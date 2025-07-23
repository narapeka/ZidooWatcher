#!/usr/bin/env python3
"""
ZidooWatcher 前端启动脚本
直接启动 Vue 开发服务器
"""

import os
import sys
import subprocess
import platform

def main():
    print("🚀 启动 ZidooWatcher 前端服务...")
    
    # 切换到frontend目录
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    
    # 确定npm命令
    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    
    try:
        # 启动前端开发服务器
        cmd = [npm_cmd, "run", "dev"]
        subprocess.run(cmd, cwd=frontend_dir, check=True)
    except KeyboardInterrupt:
        print("\n⏹️ 前端服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 前端启动失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 未找到 npm 命令，请确保 Node.js 已安装")
        sys.exit(1)

if __name__ == "__main__":
    main() 