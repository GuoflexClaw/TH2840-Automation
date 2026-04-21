#!/usr/bin/env python3
"""
TH2840快速调用脚本
在其他对话中直接导入使用
"""

import subprocess
import sys
import os

def run_th2840_test(mode="Cs模式", frequency=100, interval=0.001, duration=10, batch=1):
    """快速运行TH2840测试
    
    Args:
        mode: 测试模式 ("Cs模式" 或 "Cp模式")
        frequency: 测试频率 (Hz)
        interval: 采样间隔 (秒)
        duration: 测试时长 (秒)
        batch: 批量测试次数
        
    Returns:
        bool: 测试是否成功
    """
    # 构建命令
    cmd = [
        sys.executable, "th2840_automation.py",
        "--mode", mode,
        "--frequency", str(frequency),
        "--interval", str(interval),
        "--duration", str(duration)
    ]
    
    if batch > 1:
        cmd.extend(["--batch", str(batch)])
    
    print(f"启动TH2840测试...")
    print(f"参数: 模式={mode}, 频率={frequency}Hz, 间隔={interval}s, 时长={duration}s")
    if batch > 1:
        print(f"批量: {batch}次")
    
    try:
        # 运行测试
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("TH2840测试成功完成")
            # 提取保存的文件名
            for line in result.stdout.split('\n'):
                if "数据保存到:" in line:
                    print(f"数据保存: {line.strip()}")
            return True
        else:
            print(f"[ERROR] TH2840测试失败")
            if result.stderr:
                print(f"错误信息: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] TH2840测试超时")
        return False
    except Exception as e:
        print(f"[WARN]  TH2840测试异常: {e}")
        return False

def run_th2840_quick(mode="Cs模式", frequency=100):
    """快速测试（使用默认参数）
    
    Args:
        mode: 测试模式
        frequency: 测试频率
        
    Returns:
        bool: 测试是否成功
    """
    return run_th2840_test(mode=mode, frequency=frequency)

def run_th2840_batch(mode="Cs模式", frequency=100, count=3):
    """批量快速测试
    
    Args:
        mode: 测试模式
        frequency: 测试频率
        count: 测试次数
        
    Returns:
        bool: 所有测试是否成功
    """
    return run_th2840_test(mode=mode, frequency=frequency, batch=count)

def check_th2840_environment():
    """检查TH2840环境是否就绪
    
    Returns:
        bool: 环境是否就绪
    """
    required_files = [
        "th2840_config.json",
        "th2840_automation.py"
    ]
    
    print("检查TH2840自动化环境...")
    
    # 检查必要文件
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"[ERROR] 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查配置文件
    try:
        import json
        with open("th2840_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查关键路径
        th2840_path = config['software_paths']['th2840_exe']
        if not os.path.exists(th2840_path):
            print(f"TH2840软件不存在: {th2840_path}")
            return False
        
        print("TH2840环境检查通过")
        print(f"软件版本: {config['metadata']['name']} v{config['metadata']['version']}")
        print(f"保存路径: {config['file_naming']['save_path']}")
        return True
        
    except Exception as e:
        print(f"配置文件检查失败: {e}")
        return False

# 命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TH2840快速调用')
    parser.add_argument('--mode', choices=['Cs模式', 'Cp模式'], default='Cs模式', help='测试模式')
    parser.add_argument('--frequency', type=float, default=100, help='测试频率 (Hz)')
    parser.add_argument('--interval', type=float, default=0.001, help='采样间隔 (s)')
    parser.add_argument('--duration', type=float, default=10, help='测试时长 (s)')
    parser.add_argument('--batch', type=int, default=1, help='批量测试次数')
    parser.add_argument('--check', action='store_true', help='只检查环境')
    parser.add_argument('--quick', action='store_true', help='快速测试（使用默认参数）')
    
    args = parser.parse_args()
    
    if args.check:
        sys.exit(0 if check_th2840_environment() else 1)
    elif args.quick:
        success = run_th2840_quick(args.mode, args.frequency)
    else:
        success = run_th2840_test(
            mode=args.mode,
            frequency=args.frequency,
            interval=args.interval,
            duration=args.duration,
            batch=args.batch
        )
    
    sys.exit(0 if success else 1)