#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TH2840智能运行脚本
启动测试后定期检查保存文件夹，看到新文件就说明测试完成
"""

import os
import sys
import time
import subprocess
import json
from typing import Optional, List

def fix_windows_encoding():
    """修复Windows控制台编码"""
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_save_folder_files() -> List[str]:
    """获取保存文件夹中的所有文件
    
    Returns:
        文件列表
    """
    save_path = "E:\\A-Openclaw\\"
    if not os.path.exists(save_path):
        return []
    
    return [f for f in os.listdir(save_path) if f.endswith('.csv')]

def wait_for_new_file(initial_files: List[str], timeout: int = 300, check_interval: int = 2) -> Optional[str]:
    """等待新文件出现
    
    Args:
        initial_files: 初始文件列表
        timeout: 超时时间（秒）
        check_interval: 检查间隔（秒）
    
    Returns:
        新文件名，如果超时返回None
    """
    print(f"等待新文件出现（超时: {timeout}秒，检查间隔: {check_interval}秒）...")
    
    start_time = time.time()
    last_check = start_time
    
    while time.time() - start_time < timeout:
        current_time = time.time()
        
        # 定期检查
        if current_time - last_check >= check_interval:
            current_files = get_save_folder_files()
            new_files = [f for f in current_files if f not in initial_files]
            
            if new_files:
                # 按修改时间排序，返回最新的文件
                new_files.sort(key=lambda f: os.path.getmtime(os.path.join("E:\\A-Openclaw\\", f)), reverse=True)
                return new_files[0]
            
            last_check = current_time
            print(f"  {int(current_time - start_time)}秒: 尚未检测到新文件...")
        
        time.sleep(0.5)  # 短暂休眠避免CPU占用过高
    
    print(f"⏰ 超时（{timeout}秒）未检测到新文件")
    return None

def run_th2840_smart(mode: str = "Cs模式", frequency: float = 100, interval: float = 0.001, duration: float = 10) -> bool:
    """智能运行TH2840测试
    
    Args:
        mode: 测试模式 ("Cs模式" 或 "Cp模式")
        frequency: 测试频率 (Hz)
        interval: 采样间隔 (秒)
        duration: 测试时长 (秒)
    
    Returns:
        测试是否成功
    """
    fix_windows_encoding()
    
    # 获取脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取初始文件列表
    initial_files = get_save_folder_files()
    print(f"初始文件数: {len(initial_files)}")
    if initial_files:
        print(f"最新文件: {max(initial_files, key=lambda f: os.path.getmtime(os.path.join('E:\\A-Openclaw\\', f)))}")
    
    # 构建命令
    cmd = [
        sys.executable,
        os.path.join(script_dir, "th2840_automation.py"),
        "--mode", mode,
        "--frequency", str(frequency),
        "--interval", str(interval),
        "--duration", str(duration)
    ]
    
    print(f"=== TH2840智能测试 ===")
    print(f"模式: {mode}")
    print(f"频率: {frequency} Hz")
    print(f"采样间隔: {interval} s")
    print(f"测试时长: {duration} s")
    print(f"启动时间: {time.strftime('%H:%M:%S')}")
    
    try:
        # 启动测试（不等待完成）
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        print("启动测试进程...")
        process = subprocess.Popen(
            cmd,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        # 等待一小段时间确保进程启动
        time.sleep(5)
        
        # 检查进程是否还在运行
        if process.poll() is not None:
            # 进程已结束，读取输出
            stdout, stderr = process.communicate()
            print("测试进程已结束")
            if stdout:
                print(f"输出: {stdout[:200]}")
            if stderr:
                print(f"错误: {stderr[:200]}")
            
            if process.returncode != 0:
                print(f"❌ 测试进程异常结束，返回码: {process.returncode}")
                return False
        
        # 等待新文件出现
        print("\n监控保存文件夹...")
        new_file = wait_for_new_file(initial_files, timeout=duration + 120)  # 测试时长+120秒超时
        
        if new_file:
            print(f"✅ 检测到新文件: {new_file}")
            
            # 获取文件信息
            file_path = os.path.join("E:\\A-Openclaw\\", new_file)
            file_size = os.path.getsize(file_path)
            file_time = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(file_path)))
            
            print(f"   文件大小: {file_size} 字节")
            print(f"   保存时间: {file_time}")
            print(f"   完成时间: {time.strftime('%H:%M:%S')}")
            
            # 如果进程还在运行，等待它结束
            if process.poll() is None:
                print("等待测试进程结束...")
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    print("⚠️  测试进程超时未结束，强制终止")
                    process.terminate()
                    process.wait(timeout=5)
            
            return True
        else:
            print("❌ 未检测到新文件，测试可能失败")
            
            # 如果进程还在运行，终止它
            if process.poll() is None:
                print("终止测试进程...")
                process.terminate()
                process.wait(timeout=5)
            
            return False
            
    except Exception as e:
        print(f"💥 执行异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TH2840智能运行脚本')
    parser.add_argument('--mode', choices=['Cs模式', 'Cp模式'], default='Cs模式', help='测试模式')
    parser.add_argument('--frequency', type=float, default=100, help='测试频率 (Hz)')
    parser.add_argument('--interval', type=float, default=0.001, help='采样间隔 (s)')
    parser.add_argument('--duration', type=float, default=10, help='测试时长 (s)')
    
    args = parser.parse_args()
    
    success = run_th2840_smart(
        mode=args.mode,
        frequency=args.frequency,
        interval=args.interval,
        duration=args.duration
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()