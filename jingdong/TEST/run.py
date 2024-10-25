import json
import argparse
import subprocess

# 读取 config.json 配置文件
with open('config.json', 'r') as f:
    config = json.load(f)

# 查询设备
def list_devices():
    print("以下是可执行的设备：")
    for index, device_name in enumerate(config.keys(), start=1):
        device_info = config[device_name]
        print(f"{index}. {device_name} - Device Name: {device_info['deviceName']}, UDID: {device_info['udid']}")

# 运行设备
def run_device(device_name):
    device_info = config.get(device_name)

    if not device_info:
        raise ValueError(f"Device '{device_name}' not found in config.json")

    udid = device_info['udid']
    device_name_value = device_info['deviceName']

    # 修改 desired_caps 配置
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '9',
        'deviceName': device_name_value,  # 动态设置 deviceName
        'udid': udid,  # 动态设置 udid
        'automationName': 'UiAutomator2',
        'settings[waitForIdleTimeout]': 10,
        'settings[waitForSelectorTimeout]': 10,
        'newCommandTimeout': 21600,
        'ignoreHiddenApiPolicyError': True,
        'dontStopAppOnReset': True,  # 保持浏览器运行状态
        'noReset': True,  # 不重置应用
    }

    # 将修改后的配置写入一个临时 JSON 文件
    with open('desired_caps.json', 'w') as f:
        json.dump(desired_caps, f, indent=4)

    # 通过子进程调用 main.py
    print(f"Running automation for {device_name}...")
    subprocess.run(['python', 'main.py'])

# 菜单功能
def menu():
    while True:
        print("\n菜单：")
        print("1. 查询设备")
        print("2. 运行设备")
        print("3. 退出")
        choice = input("请选择一个选项（1/2/3）：")

        if choice == '1':
            list_devices()
        elif choice == '2':
            list_devices()  # 显示设备列表，方便用户选择
            device_number = input("请输入设备编号：")
            try:
                device_index = int(device_number) - 1
                device_name = list(config.keys())[device_index]
                run_device(device_name)
            except (ValueError, IndexError):
                print("无效的设备编号，请重试。")
        elif choice == '3':
            print("退出程序。")
            break
        else:
            print("无效的选择，请输入1、2或3。")

# 启动菜单
menu()
