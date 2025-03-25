#!/usr/bin/env python3
"""
LiteLLM 代理服务器启动脚本
为不支持 function calling 的模型提供这一功能
"""

import os
import sys
import subprocess
from pathlib import Path

def start_litellm_proxy():
    """启动 LiteLLM 代理服务器"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    
    # 配置文件路径
    config_path = current_dir / "litellm_config.yaml"
    
    # 确保配置文件存在
    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        sys.exit(1)
    
    # 构建启动命令
    cmd = [
        "litellm",
        "--config",
        str(config_path),
        "--port",
        "8080",  # 端口应与配置文件中的一致
        "--debug",  # 添加调试输出
        "--model",
        "gpt-3.5-turbo",  # 指定模型名称
        "--drop_params",  # 删除不支持的参数
        "--add_function_to_prompt"  # 将函数调用信息添加到提示中
    ]
    
    print(f"启动 LiteLLM 代理服务器...")
    print(f"配置文件: {config_path}")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        # 启动代理服务器
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # 实时输出日志
        for line in process.stdout:
            print(line, end='')
            
        # 等待进程结束
        process.wait()
        
        if process.returncode != 0:
            print(f"LiteLLM 代理服务器异常退出，返回码: {process.returncode}")
            sys.exit(process.returncode)
            
    except KeyboardInterrupt:
        print("\n用户中断，正在关闭 LiteLLM 代理服务器...")
        process.terminate()
        process.wait()
        print("LiteLLM 代理服务器已关闭")
    except Exception as e:
        print(f"启动 LiteLLM 代理服务器时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_litellm_proxy()
