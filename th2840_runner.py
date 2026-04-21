#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TH2840运行器 - 从任何位置运行TH2840自动化系统
"""

import os
import sys
import subprocess

# Windows控制台编码修复
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')

def get_script_dir():
    """获取脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))

def run_th2840_from_anywhere(**kwargs):
    """从任何位置运行TH2840测试
    
    Args:
        **kwargs: 测试参数
            mode: 测试模式 ("Cs模式" 或 "Cp模式")
            frequency: 测试频率 (Hz)
            interval: 采样间隔 (秒)
            duration: 测试时长 (秒)
            batch: 批量测试次数
            
    Returns:
        bool: 测试是否成功
    """
    script_dir = get_script_dir()
    
    # 构建命令
    cmd = [
        sys.executable,
        os.path.join(script_dir, "th2840_automation.py")
    ]
    
    # 添加参数
    if 'mode' in kwargs:
        cmd.extend(["--mode", kwargs['mode']])
    if 'frequency' in kwargs:
        cmd.extend(["--frequency", str(kwargs['frequency'])])
    if 'interval' in kwargs:
        cmd.extend(["--interval", str(kwargs['interval'])])
    if 'duration' in kwargs:
        cmd.extend(["--duration", str(kwargs['duration'])])
    if 'batch' in kwargs and kwargs['batch'] > 1:
        cmd.extend(["--batch", str(kwargs['batch'])])
    
    print(f"启动TH2840测试...")
    print(f"脚本目录: {script_dir}")
    
    try:
        # 运行测试
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=script_dir)
        
        if result.returncode == 0:
            print("TH2840测试成功完成")
            # 提取保存的文件名
            for line in result.stdout.split('\n'):
                if "数据保存到:" in line:
                    print(f"数据保存: {line.strip()}")
            return True
        else:
            print(f"TH2840测试失败")
            if result.stderr:
                print(f"错误信息: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("TH2840测试超时")
        return False
    except Exception as e:
        print(f"TH2840测试异常: {e}")
        return False

def check_environment():
    """检查环境"""
    script_dir = get_script_dir()
    
    required_files = [
        "th2840_config.json",
        "th2840_automation.py"
    ]
    
    print("检查TH2840自动化环境...")
    print(f"检查目录: {script_dir}")
    
    # 检查必要文件
    missing_files = []
    for file in required_files:
        filepath = os.path.join(script_dir, file)
        if not os.path.exists(filepath):
            missing_files.append(file)
    
    if missing_files:
        print(f"[ERROR] 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查配置文件
    try:
        import json
        config_path = os.path.join(script_dir, "th2840_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查关键路径
        th2840_path = config['software_paths']['th2840_exe']
        if not os.path.exists(th2840_path):
            print(f"[ERROR] TH2840软件不存在: {th2840_path}")
            return False
        
        print("TH2840环境检查通过")
        print(f"软件版本: {config['metadata']['name']} v{config['metadata']['version']}")
        print(f"保存路径: {config['file_naming']['save_path']}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 配置文件检查失败: {e}")
        return False

# 命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TH2840运行器 - 从任何位置运行')
    parser.add_argument('--mode', choices=['Cs模式', 'Cp模式'], default='Cs模式', help='测试模式')
    parser.add_argument('--frequency', type=float, default=100, help='测试频率 (Hz)')
    parser.add_argument('--interval', type=float, default=0.001, help='采样间隔 (s)')
    parser.add_argument('--duration', type=float, default=10, help='测试时长 (s)')
    parser.add_argument('--batch', type=int, default=1, help='批量测试次数')
    parser.add_argument('--check', action='store_true', help='只检查环境')
    parser.add_argument('--quick', action='store_true', help='快速测试（使用默认参数）')
    
    args = parser.parse_args()
    
    if args.check:
        sys.exit(0 if check_environment() else 1)
    elif args.quick:
        success = run_th2840_from_anywhere(mode=args.mode, frequency=args.frequency)
    else:
        success = run_th2840_from_anywhere(
            mode=args.mode,
            frequency=args.frequency,
            interval=args.interval,
            duration=args.duration,
            batch=args.batch
        )
    
    sys.exit(0 if success else 1)