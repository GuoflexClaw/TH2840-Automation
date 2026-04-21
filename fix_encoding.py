#!/usr/bin/env python3
"""
修复文件编码问题
"""

import os
import re

def fix_file_encoding(filepath):
    """修复文件中的特殊字符"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换常见特殊字符
    replacements = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARN]',
        '🔧': '[TOOL]',
        '⏱️': '[TIME]',
        '💾': '[SAVE]',
        '🧹': '[CLEAN]',
        '🎉': '[DONE]',
        '🚀': '[START]',
        '📋': '[PARAMS]',
        '🔄': '[BATCH]',
        '📊': '[STATS]',
        '📁': '[FILE]',
        '📈': '[CHART]',
        '🔍': '[CHECK]',
        '🧪': '[TEST]',
        '⏳': '[WAIT]',
        '⏰': '[TIMEOUT]',
        '•': '-',
        '→': '->',
        '≈': '~'
    }
    
    fixed_content = content
    for old, new in replacements.items():
        fixed_content = fixed_content.replace(old, new)
    
    # 写入修复后的内容
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"已修复: {filepath}")

def main():
    """主函数"""
    files_to_fix = [
        'th2840_automation.py',
        'th2840_quick_call.py',
        'th2840_example_usage.py'
    ]
    
    for file in files_to_fix:
        if os.path.exists(file):
            fix_file_encoding(file)
        else:
            print(f"文件不存在: {file}")

if __name__ == "__main__":
    main()