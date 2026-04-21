#!/usr/bin/env python3
"""
TH2840自动化系统使用示例
"""

import subprocess
import json
import os

def example_single_test():
    """单次测试示例"""
    print("=" * 60)
    print("示例1: 单次测试")
    print("=" * 60)
    
    # 方法1: 使用默认参数
    print("\n方法1: 使用默认参数")
    cmd = ["python", "th2840_automation.py"]
    print(f"命令: {' '.join(cmd)}")
    
    # 方法2: 指定所有参数
    print("\n方法2: 指定所有参数")
    cmd = [
        "python", "th2840_automation.py",
        "--mode", "Cs模式",
        "--frequency", "100",
        "--interval", "0.001",
        "--duration", "10"
    ]
    print(f"命令: {' '.join(cmd)}")
    
    # 方法3: 部分参数（使用默认值填充）
    print("\n方法3: 部分参数")
    cmd = [
        "python", "th2840_automation.py",
        "--mode", "Cp模式",
        "--frequency", "1000"
    ]
    print(f"命令: {' '.join(cmd)}")

def example_batch_tests():
    """批量测试示例"""
    print("\n" + "=" * 60)
    print("示例2: 批量测试")
    print("=" * 60)
    
    # 批量测试4次
    cmd = [
        "python", "th2840_automation.py",
        "--mode", "Cs模式",
        "--frequency", "100",
        "--interval", "0.001",
        "--duration", "5",
        "--batch", "4"
    ]
    print(f"命令: {' '.join(cmd)}")
    print("说明: 将连续执行4次测试，每次5秒")

def example_config_management():
    """配置管理示例"""
    print("\n" + "=" * 60)
    print("示例3: 配置管理")
    print("=" * 60)
    
    # 查看配置
    with open("th2840_config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("配置概览:")
    print(f"- 软件名称: {config['metadata']['name']}")
    print(f"- 版本: {config['metadata']['version']}")
    print(f"- TH2840路径: {config['software_paths']['th2840_exe']}")
    print(f"- 保存路径: {config['file_naming']['save_path']}")
    print(f"- 默认参数:")
    for key, value in config['default_parameters'].items():
        print(f"  - {key}: {value}")

def example_custom_config():
    """自定义配置示例"""
    print("\n" + "=" * 60)
    print("示例4: 自定义配置")
    print("=" * 60)
    
    # 创建自定义配置
    custom_config = {
        "custom_test": {
            "name": "高频测试方案",
            "parameters": {
                "mode": "Cs模式",
                "frequency": 10000,  # 10kHz
                "interval": 0.0001,  # 0.1ms
                "duration": 30       # 30秒
            },
            "description": "高频长时间测试方案"
        },
        "quick_test": {
            "name": "快速测试方案",
            "parameters": {
                "mode": "Cp模式",
                "frequency": 100,
                "interval": 0.01,
                "duration": 3
            },
            "description": "快速验证测试方案"
        }
    }
    
    print("自定义测试方案:")
    for key, scheme in custom_config.items():
        print(f"\n{scheme['name']} ({key}):")
        print(f"  描述: {scheme['description']}")
        params = scheme['parameters']
        print(f"  参数: 模式={params['mode']}, 频率={params['frequency']}Hz, "
              f"间隔={params['interval']}s, 时长={params['duration']}s")
        
        # 生成命令
        cmd = [
            "python", "th2840_automation.py",
            "--mode", params['mode'],
            "--frequency", str(params['frequency']),
            "--interval", str(params['interval']),
            "--duration", str(params['duration'])
        ]
        print(f"  命令: {' '.join(cmd)}")

def example_integration():
    """集成使用示例"""
    print("\n" + "=" * 60)
    print("示例5: 集成到其他脚本")
    print("=" * 60)
    
    code = '''# 在其他Python脚本中集成使用
import subprocess
import time

def run_th2840_test(mode, frequency, interval, duration):
    """运行TH2840测试"""
    cmd = [
        "python", "th2840_automation.py",
        "--mode", mode,
        "--frequency", str(frequency),
        "--interval", str(interval),
        "--duration", str(duration)
    ]
    
    print(f"开始TH2840测试: {mode} {frequency}Hz")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[OK] 测试成功完成")
        return True
    else:
        print(f"[ERROR] 测试失败: {result.stderr}")
        return False

# 示例使用
if __name__ == "__main__":
    # 运行多个测试
    test_cases = [
        ("Cs模式", 100, 0.001, 10),
        ("Cp模式", 1000, 0.0005, 5),
        ("Cs模式", 10000, 0.0001, 30)
    ]
    
    for mode, freq, interval, duration in test_cases:
        success = run_th2840_test(mode, freq, interval, duration)
        if not success:
            break
        time.sleep(2)  # 测试间隔'''
    
    print("集成代码示例:")
    print(code)

def main():
    """主函数"""
    print("TH2840自动化系统使用示例")
    print("=" * 60)
    
    example_single_test()
    example_batch_tests()
    example_config_management()
    example_custom_config()
    example_integration()
    
    print("\n" + "=" * 60)
    print("使用说明总结:")
    print("=" * 60)
    print("1. 基本使用: python th2840_automation.py")
    print("2. 指定参数: python th2840_automation.py --mode Cs模式 --frequency 100")
    print("3. 批量测试: python th2840_automation.py --batch 4")
    print("4. 查看帮助: python th2840_automation.py --help")
    print("\n📝 注意: 确保桌面控制脚本和TH2840软件路径正确配置")

if __name__ == "__main__":
    main()