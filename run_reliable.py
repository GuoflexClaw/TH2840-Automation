#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TH2840可靠运行脚本
修复Windows编码问题，确保稳定运行
"""

import os
import sys
import subprocess
import json

def fix_windows_encoding():
    """修复Windows控制台编码"""
    if sys.platform == "win32":
        # 设置控制台编码为UTF-8
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_th2840_reliable(mode="Cs模式", frequency=100, interval=0.001, duration=10):
    """可靠运行TH2840测试
    
    Args:
        mode: 测试模式 ("Cs模式" 或 "Cp模式")
        frequency: 测试频率 (Hz)
        interval: 采样间隔 (秒)
        duration: 测试时长 (秒)
    
    Returns:
        bool: 测试是否成功
    """
    fix_windows_encoding()
    
    # 获取脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建命令
    cmd = [
        sys.executable,
        os.path.join(script_dir, "th2840_automation.py"),
        "--mode", mode,
        "--frequency", str(frequency),
        "--interval", str(interval),
        "--duration", str(duration)
    ]
    
    print(f"=== TH2840可靠测试 ===")
    print(f"模式: {mode}")
    print(f"频率: {frequency} Hz")
    print(f"采样间隔: {interval} s")
    print(f"测试时长: {duration} s")
    print(f"工作目录: {script_dir}")
    
    try:
        # 运行测试，使用UTF-8编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            cmd,
            cwd=script_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300,  # 5分钟超时
            env=env
        )
        
        # 输出关键信息
        print("\n=== 执行结果 ===")
        print(f"返回码: {result.returncode}")
        
        # 提取和显示关键输出
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in [
                    "配置文件", "参数", "启动", "输入参数", 
                    "测试", "保存", "数据保存", "完成", "耗时"
                ]):
                    print(line)
        
        if result.returncode == 0:
            print("\n✅ 测试成功完成!")
            
            # 检查保存的文件
            save_path = "E:\\A-Openclaw\\"
            if os.path.exists(save_path):
                files = [f for f in os.listdir(save_path) if f.endswith('.csv')]
                if files:
                    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(save_path, f)))
                    print(f"📁 最新数据文件: {latest}")
            
            return True
        else:
            print(f"\n❌ 测试失败")
            if result.stderr:
                print(f"错误信息: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⏰ 测试超时（300秒）")
        return False
    except Exception as e:
        print(f"\n💥 执行异常: {e}")
        return False

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TH2840可靠运行脚本')
    parser.add_argument('--mode', choices=['Cs模式', 'Cp模式'], default='Cs模式', help='测试模式')
    parser.add_argument('--frequency', type=float, default=100, help='测试频率 (Hz)')
    parser.add_argument('--interval', type=float, default=0.001, help='采样间隔 (s)')
    parser.add_argument('--duration', type=float, default=10, help='测试时长 (s)')
    
    args = parser.parse_args()
    
    success = run_th2840_reliable(
        mode=args.mode,
        frequency=args.frequency,
        interval=args.interval,
        duration=args.duration
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()