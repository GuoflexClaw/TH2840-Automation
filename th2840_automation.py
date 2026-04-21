#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TH2840全自动测试系统
基于JSON配置的模块化自动化脚本
"""

import json
import os
import sys
import time
import subprocess
import datetime
from typing import Dict, List, Any, Optional
import argparse

# Windows控制台编码修复
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')

class TH2840Automation:
    """TH2840全自动测试系统主类"""
    
    def __init__(self, config_path: str = None):
        """初始化自动化系统
        
        Args:
            config_path: JSON配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            # 获取脚本所在目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "th2840_config.json")
        
        self.config = self.load_config(config_path)
        self.current_test_number = self.get_current_test_number()
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载JSON配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"配置文件加载成功: {config['metadata']['name']} v{config['metadata']['version']}")
            return config
        except FileNotFoundError:
            print(f"配置文件不存在: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            sys.exit(1)
    
    def get_current_test_number(self) -> int:
        """获取当前测试编号
        
        Returns:
            下一个测试编号
        """
        save_path = self.config['file_naming']['save_path']
        if not os.path.exists(save_path):
            return self.config['file_naming']['start_number']
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        max_number = 0
        
        for filename in os.listdir(save_path):
            if filename.startswith(today):
                try:
                    # 提取编号部分: YYYY-MM-DD-N
                    parts = filename.split('-')
                    if len(parts) >= 4:
                        number = int(parts[3].split('.')[0])  # 去掉扩展名
                        max_number = max(max_number, number)
                except (ValueError, IndexError):
                    continue
        
        return max_number + 1
    
    def run_desktop_controller(self, command: str, x: int = 0, y: int = 0, text: str = "") -> bool:
        """运行桌面控制脚本
        
        Args:
            command: 命令类型 (click, double_click, type, etc.)
            x: X坐标
            y: Y坐标
            text: 要输入的文本
            
        Returns:
            执行是否成功
        """
        python_path = self.config['software_paths']['python_env']
        controller_path = self.config['software_paths']['desktop_controller']
        
        cmd = [python_path, controller_path, command]
        
        if command in ['click', 'double_click']:
            cmd.extend([str(x), str(y)])
        elif command == 'type':
            cmd.extend([text])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
            else:
                print(f"[WARN]  桌面控制脚本执行失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("[WARN]  桌面控制脚本执行超时")
            return False
        except Exception as e:
            print(f"[ERROR] 桌面控制脚本执行异常: {e}")
            return False
    
    def execute_phase(self, phase_name: str, coordinates: List[Dict[str, Any]], delays: Dict[str, float]) -> bool:
        """执行一个阶段的操作
        
        Args:
            phase_name: 阶段名称
            coordinates: 坐标列表
            delays: 延迟配置
            
        Returns:
            阶段执行是否成功
        """
        print(f"[TOOL] 开始执行 {phase_name} 阶段...")
        
        for i, coord in enumerate(coordinates):
            print(f"  [{i+1}/{len(coordinates)}] {coord['name']} ({coord['x']}, {coord['y']})")
            
            # 执行操作
            if coord['action'] == 'click':
                success = self.run_desktop_controller('click', coord['x'], coord['y'])
            elif coord['action'] == 'double_click':
                success = self.run_desktop_controller('double_click', coord['x'], coord['y'])
            else:
                print(f"[WARN]  未知操作类型: {coord['action']}")
                success = False
            
            if not success:
                print(f"[ERROR] {phase_name} 阶段执行失败: {coord['name']}")
                return False
            
            # 根据操作类型应用延迟
            delay_key = f"{phase_name.lower()}_delay"
            if delay_key in delays:
                time.sleep(delays[delay_key])
            else:
                # 默认延迟
                time.sleep(0.5)
        
        print(f"[OK] {phase_name} 阶段完成")
        return True
    
    def input_parameter(self, coord: Dict[str, Any], value: Any) -> bool:
        """输入参数值
        
        Args:
            coord: 坐标配置
            value: 参数值
            
        Returns:
            输入是否成功
        """
        print(f"  📝 输入参数: {value}")
        
        # 双击选中文本框
        if not self.run_desktop_controller('double_click', coord['x'], coord['y']):
            return False
        
        time.sleep(0.2)
        
        # 输入值
        if not self.run_desktop_controller('type', text=str(value)):
            return False
        
        time.sleep(0.2)
        return True
    
    def start_th2840(self) -> bool:
        """启动TH2840软件
        
        Returns:
            启动是否成功
        """
        th2840_path = self.config['software_paths']['th2840_exe']
        
        print(f"[START] 启动TH2840软件: {th2840_path}")
        
        try:
            subprocess.Popen([th2840_path], shell=True)
            time.sleep(self.config['timing_config']['software_startup_delay'])
            print("[OK] TH2840软件启动成功")
            return True
        except Exception as e:
            print(f"[ERROR] TH2840软件启动失败: {e}")
            return False
    
    def generate_filename(self) -> str:
        """生成文件名
        
        Returns:
            生成的文件名
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}-{self.current_test_number}"
        self.current_test_number += 1
        return filename
    
    def run_full_test(self, 
                     test_mode: str = None,
                     test_frequency: float = None,
                     sampling_interval: float = None,
                     test_duration: float = None) -> bool:
        """运行完整测试流程
        
        Args:
            test_mode: 测试模式 (Cs模式/Cp模式)
            test_frequency: 测试频率 (Hz)
            sampling_interval: 采样间隔 (s)
            test_duration: 测试时长 (s)
            
        Returns:
            测试是否成功
        """
        # 使用默认参数或传入参数
        params = {
            'test_mode': test_mode or self.config['default_parameters']['test_mode'],
            'test_frequency': test_frequency or self.config['default_parameters']['test_frequency'],
            'sampling_interval': sampling_interval or self.config['default_parameters']['sampling_interval'],
            'test_duration': test_duration or self.config['default_parameters']['test_duration']
        }
        
        print("=" * 60)
        print("[TEST] TH2840全自动测试系统启动")
        print("=" * 60)
        print(f"[PARAMS] 测试参数:")
        print(f"  - 测试模式: {params['test_mode']}")
        print(f"  - 测试频率: {params['test_frequency']} Hz")
        print(f"  - 采样间隔: {params['sampling_interval']} s")
        print(f"  - 测试时长: {params['test_duration']} s")
        print("=" * 60)
        
        # 阶段1: 启动软件
        if not self.start_th2840():
            return False
        
        # 阶段2: 配置阶段
        config_coords = self.config['ui_coordinates']['config_phase']
        
        # 执行标准配置步骤（包括再次点击测试项框）
        # 需要执行前7个步骤：1.任务栏 2.连接 3.完成(连接) 4.设置 5.测试项框 6.上拉位置 7.测试项框(再次)
        for i in range(7):  # 前7个标准步骤，包括再次点击测试项框
            coord = config_coords[i]
            if not self.run_desktop_controller(coord['action'], coord['x'], coord['y']):
                return False
            
            # 特殊处理：点击任务栏后需要更长时间等待窗口激活
            if i == 0:  # 第一个步骤是点击任务栏
                time.sleep(self.config['timing_config'].get('taskbar_to_connection_delay', 2))
            else:
                time.sleep(0.5)
        
        # 选择测试模式
        mode_coord = None
        if params['test_mode'] == 'Cs模式':
            mode_coord = next(c for c in config_coords if c['name'] == 'Cs模式位置')
        else:  # Cp模式
            mode_coord = next(c for c in config_coords if c['name'] == 'Cp模式位置')
        
        if mode_coord and not self.run_desktop_controller('click', mode_coord['x'], mode_coord['y']):
            return False
        time.sleep(0.3)
        
        # 输入频率参数
        freq_coord = next(c for c in config_coords if c['name'] == '频率设置框')
        if not self.input_parameter(freq_coord, params['test_frequency']):
            return False
        
        # 输入采样间隔参数
        interval_coord = next(c for c in config_coords if c['name'] == '采样间隔框')
        if not self.input_parameter(interval_coord, params['sampling_interval']):
            return False
        
        # 完成配置
        finish_coord = next(c for c in config_coords if c['name'] == '完成按钮(配置)')
        if not self.run_desktop_controller('click', finish_coord['x'], finish_coord['y']):
            return False
        time.sleep(1)
        
        print("[OK] 软件配置完成")
        
        # 阶段3: 测试阶段
        print("[TIME]  开始测试...")
        start_coord = next(c for c in self.config['ui_coordinates']['test_phase'] if c['name'] == '开始测试按钮')
        if not self.run_desktop_controller('click', start_coord['x'], start_coord['y']):
            return False
        
        # 等待测试完成
        print(f"[WAIT] 测试进行中，等待 {params['test_duration']} 秒...")
        time.sleep(params['test_duration'])
        
        # 停止测试
        stop_coord = next(c for c in self.config['ui_coordinates']['test_phase'] if c['name'] == '停止测试按钮')
        if not self.run_desktop_controller('click', stop_coord['x'], stop_coord['y']):
            return False
        time.sleep(1)
        
        print("[OK] 测试完成")
        
        # 阶段4: 保存阶段
        print("[SAVE] 保存测试数据...")
        
        # 打开保存对话框
        save_coord = next(c for c in self.config['ui_coordinates']['save_phase'] if c['name'] == '保存按钮')
        if not self.run_desktop_controller('click', save_coord['x'], save_coord['y']):
            return False
        time.sleep(1)
        
        # 导航到保存路径
        for coord in self.config['ui_coordinates']['save_phase'][1:5]:  # 跳过保存按钮
            if not self.run_desktop_controller(coord['action'], coord['x'], coord['y']):
                return False
            time.sleep(0.5)
        
        # 输入文件名
        filename = self.generate_filename()
        filename_coord = next(c for c in self.config['ui_coordinates']['save_phase'] if c['name'] == '文件名框')
        
        # 点击文件名框
        if not self.run_desktop_controller('click', filename_coord['x'], filename_coord['y']):
            return False
        time.sleep(0.3)
        
        # 输入文件名
        if not self.run_desktop_controller('type', text=filename):
            return False
        time.sleep(0.3)
        
        # 按回车保存
        if not self.run_desktop_controller('type', text="\n"):
            return False
        time.sleep(1)
        
        print(f"[OK] 数据保存完成: {filename}")
        
        # 阶段5: 清理阶段
        print("[CLEAN] 清理测试环境...")
        cleanup_coord = next(c for c in self.config['ui_coordinates']['cleanup_phase'] if c['name'] == '清除按钮')
        if not self.run_desktop_controller('click', cleanup_coord['x'], cleanup_coord['y']):
            return False
        time.sleep(0.5)
        
        print("[OK] 环境清理完成")
        
        # 总结
        print("=" * 60)
        print("[DONE] TH2840全自动测试完成!")
        print(f"[FILE] 数据保存到: {self.config['file_naming']['save_path']}{filename}")
        print(f"[TIME]  总耗时: 约{self.config['validation']['average_time']}秒")
        print(f"[CHART] 效率提升: {self.config['validation']['efficiency_gain']*100:.0f}%")
        print("=" * 60)
        
        return True
    
    def run_batch_tests(self, count: int, **kwargs) -> bool:
        """运行批量测试
        
        Args:
            count: 测试次数
            **kwargs: 测试参数
            
        Returns:
            批量测试是否成功
        """
        print(f"[BATCH] 开始批量测试，共 {count} 次")
        
        success_count = 0
        for i in range(count):
            print(f"\n[STATS] 第 {i+1}/{count} 次测试")
            if self.run_full_test(**kwargs):
                success_count += 1
            else:
                print(f"[ERROR] 第 {i+1} 次测试失败")
                # 可以在这里添加重试逻辑
        
        print(f"\n[CHART] 批量测试完成: {success_count}/{count} 成功")
        return success_count == count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TH2840全自动测试系统')
    parser.add_argument('--config', default='th2840_config.json', help='配置文件路径')
    parser.add_argument('--mode', choices=['Cs模式', 'Cp模式'], help='测试模式')
    parser.add_argument('--frequency', type=float, help='测试频率 (Hz)')
    parser.add_argument('--interval', type=float, help='采样间隔 (s)')
    parser.add_argument('--duration', type=float, help='测试时长 (s)')
    parser.add_argument('--batch', type=int, default=1, help='批量测试次数')
    
    args = parser.parse_args()
    
    # 创建自动化实例
    automation = TH2840Automation(args.config)
    
    # 准备参数
    params = {}
    if args.mode:
        params['test_mode'] = args.mode
    if args.frequency:
        params['test_frequency'] = args.frequency
    if args.interval:
        params['sampling_interval'] = args.interval
    if args.duration:
        params['test_duration'] = args.duration
    
    # 运行测试
    if args.batch > 1:
        success = automation.run_batch_tests(args.batch, **params)
    else:
        success = automation.run_full_test(**params)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()