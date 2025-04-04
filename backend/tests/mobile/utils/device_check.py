#!/usr/bin/env python3
import subprocess
import time

def check_connected_devices():
    """检查连接的Android设备"""
    try:
        # 执行adb devices命令
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        
        # 解析输出
        lines = result.stdout.strip().split('\n')
        if len(lines) <= 1:  # 只有标题行，没有设备
            print("未检测到设备")
            return False
            
        # 打印所有检测到的设备
        print("检测到以下设备：")
        for line in lines[1:]:  # 跳过第一行（标题行）
            if line.strip():
                device_id, status = line.split('\t')
                print(f"设备ID: {device_id}, 状态: {status}")
        return True
        
    except Exception as e:
        print(f"检查设备时出错: {str(e)}")
        return False

def check_device_info():
    """获取已连接设备的详细信息"""
    try:
        # 获取Android版本
        version = subprocess.run(
            ['adb', 'shell', 'getprop', 'ro.build.version.release'],
            capture_output=True, text=True
        ).stdout.strip()
        
        # 获取设备型号
        model = subprocess.run(
            ['adb', 'shell', 'getprop', 'ro.product.model'],
            capture_output=True, text=True
        ).stdout.strip()
        
        # 获取设备制造商
        manufacturer = subprocess.run(
            ['adb', 'shell', 'getprop', 'ro.product.manufacturer'],
            capture_output=True, text=True
        ).stdout.strip()
        
        print(f"\n设备信息:")
        print(f"Android版本: {version}")
        print(f"设备型号: {model}")
        print(f"制造商: {manufacturer}")
        
    except Exception as e:
        print(f"获取设备信息时出错: {str(e)}")

if __name__ == "__main__":
    print("开始检查Android设备...")
    if check_connected_devices():
        check_device_info()
    else:
        print("\n请确保：")
        print("1. Android设备已通过USB连接到计算机")
        print("2. 设备已启用USB调试模式")
        print("3. 已在设备上确认允许USB调试") 